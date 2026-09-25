"""S8 Compete backend acceptance checks.

Run from the repository root with SATF_DB=$PWD/server/s8.db PYTHONPATH=.
Only the dedicated S8 database may be used: these checks create sittings.
"""

from __future__ import annotations

import datetime as dt
import inspect
import json
import os
import pathlib
import secrets
import subprocess
import sys

from fastapi.testclient import TestClient

from server import blueprint, compete, db, deps, practice, prefs, progress
from server.app import app


def assert_ok(condition: bool, message: str) -> None:
    assert condition, message
    print("ok ", message)


def pending(condition: bool, message: str) -> None:
    print(("ok  " if condition else "PENDING  ") + message)


def learner(tag: str) -> str:
    return "a:s8check" + tag + secrets.token_hex(3)


def head(person: str) -> dict:
    return {"X-Learner": person, "X-Tz": "0"}


def question_for(sid: str, qid: str) -> dict:
    row = db.one("SELECT questions FROM sessions WHERE id=?", sid)
    questions = json.loads(row["questions"])
    return next(q for q in questions if q["id"] == qid)


def answer_of(q: dict):
    return "ABCD".index(q["answer"]) if q["type"] == "mcq" else q["answer"]


def play(c: TestClient, person: str, cid: str = "daily", *, flag_first: bool = False) -> tuple[str, list[dict]]:
    h = head(person)
    start = c.post(f"/api/contest/{cid}/start", headers=h)
    assert_ok(start.status_code == 200, "contest sitting starts")
    sid = start.json()["session"]
    q = start.json()["question"]
    originals = []
    total = c.get(f"/api/contest/{cid}", headers=h).json()["count"]
    for slot in range(total):
        original = question_for(sid, q["id"])
        originals.append(original)
        if flag_first and slot == 0:
            flagged = c.post(f"/api/drill/{sid}/void", headers=h,
                             json={"question_id": q["id"], "why": "left", "secs": 12})
            assert_ok(flagged.status_code == 200 and flagged.json()["flagged"], "strict flag is recorded")
        marked = c.post(f"/api/drill/{sid}/answer", headers=h,
                        json={"question_id": q["id"], "answer": answer_of(original), "ms": 60_000})
        assert_ok(marked.status_code == 200, "answer is accepted")
        if slot < total - 1:
            nxt = c.post(f"/api/drill/{sid}/next", headers=h)
            assert_ok(nxt.status_code == 200 and nxt.json().get("question"), "next question is served")
            q = nxt.json()["question"]
    if flag_first:
        confirm = c.post(f"/api/drill/{sid}/confirm", headers=h, json={})
        assert_ok(confirm.status_code == 200 and confirm.json().get("question"), "strict twin confirm is served")
        cfg = json.loads(db.one("SELECT cfg FROM sessions WHERE id=?", sid)["cfg"])
        twin = cfg["confirm_active"]["question"]
        done = c.post(f"/api/drill/{sid}/confirm", headers=h, json={"answer": answer_of(twin)})
        assert_ok(done.status_code == 200 and not done.json()["due"], "clean confirm keeps the slot")
    finished = c.post(f"/api/drill/{sid}/finish", headers=h)
    assert_ok(finished.status_code == 200, "contest drill finishes")
    return sid, originals


def run() -> None:
    path = pathlib.Path(os.environ.get("SATF_DB", "")).resolve()
    assert_ok(path.name == "s8.db" and path.parent.name == "server", "only the dedicated S8 database is used")
    with TestClient(app) as c:
        a, b = learner("a"), learner("b")
        today = dt.datetime.now(dt.timezone.utc).date().isoformat()
        lobby = c.get("/api/contest/daily", headers=head(a))
        assert_ok(lobby.status_code == 200 and lobby.json()["id"] == "daily-" + today,
              "daily resolves to the UTC local day")
        assert_ok(lobby.json()["count"] == 10 and lobby.json()["seconds"] == 950 and
              lobby.json()["spec"]["twin"], "daily has ten twin slots and a 950-second clock")
        assert_ok(all("template" not in cell and "chance" in cell for cell in lobby.json()["ladder"]),
              "lobby gives odds without exposing the template")
        redirect = c.get("/challenge/", follow_redirects=False)
        assert_ok(redirect.status_code == 307 and "id=daily" in redirect.headers["location"],
              "old challenge page redirects to Compete")
        start_a = c.post("/api/contest/daily/start", headers=head(a)).json()
        start_a_again = c.post("/api/contest/daily/start", headers=head(a)).json()
        assert_ok(start_a["session"] == start_a_again["session"], "daily start is idempotent")
        assert_ok(start_a["clock"]["running"] and start_a["clock"]["left"] <= 950,
              "daily answer clock runs while the question is open")
        start_b = c.post("/api/contest/daily/start", headers=head(b)).json()
        first_a = question_for(start_a["session"], start_a["question"]["id"])
        first_b = question_for(start_b["session"], start_b["question"]["id"])
        assert_ok(first_a["key"] == first_b["key"] and first_a["difficulty"] == first_b["difficulty"]
              and first_a["type"] == first_b["type"], "twin starts share a canonical slot")
        assert_ok(practice.question_hash(practice.generate(first_a["key"], first_a["seed"])) !=
              practice.question_hash(practice.generate(first_b["key"], first_b["seed"])),
              "two entrants receive different whole questions")
        wrong_index = next(i for i, reason in enumerate(first_b["reasons"]) if reason)
        missed_norm = progress.norm(first_b["reasons"][wrong_index])
        c.post(f"/api/drill/{start_b['session']}/answer", headers=head(b),
               json={"question_id": first_b["id"], "answer": wrong_index, "ms": 60_000})
        c.post(f"/api/drill/{start_b['session']}/finish", headers=head(b))
        c.get("/api/contest/daily", headers=head(b))
        named_rematch = c.post("/api/contest/daily/rematch", headers=head(b), json={"when": "now"})
        assert_ok(named_rematch.status_code == 200, "named miss starts a fresh rematch")
        fresh_sid = named_rematch.json()["session"]
        fresh = c.post(f"/api/drill/{fresh_sid}/next", headers=head(b)).json()["question"]
        fresh_original = question_for(fresh_sid, fresh["id"])
        assert_ok(fresh_original["seed"] != first_b["seed"] and
                  missed_norm in progress.offered_of(fresh_original),
                  "named rematch preserves the original misconception on fresh numbers")
        assert_ok(c.get("/api/contest/daily/review", headers=head(a)).status_code == 403,
              "review is gated before finishing")
        sid, originals = play(c, a)
        result = c.get("/api/contest/daily", headers=head(a)).json()["me"]["result"]
        assert_ok(result["points"] == 260 and result["points_parts"] ==
              {"base": 200, "pace": 50, "finish": 10}, "perfect Daily scores 260 points")
        assert_ok(result["par"]["base"] == json.loads(db.one("SELECT cfg FROM sessions WHERE id=?", sid)["cfg"])
              ["par"]["base"], "par is frozen at contest start")
        assert_ok(result["records_new"] == [{"kind": "daily", "value": 260, "was": None}] and
                  c.get("/api/compete/me", headers=head(a)).json()["records"]["bests"]["daily"]["value"] == 260,
                  "first Daily stores and exposes its personal record")
        assert_ok(c.get("/api/compete/me", headers=head(a)).json()["streak"]["current"] == 1,
                  "daily twin sitting advances the challenge streak")
        makeup = learner("makeup")
        db.ensure_learner(makeup)
        for back in range(6, -1, -1):
            day = dt.date.fromisoformat(today) - dt.timedelta(days=back)
            finished = dt.datetime.combine(day, dt.time(10), dt.timezone.utc)
            if back == 1:
                finished = dt.datetime.combine(day + dt.timedelta(days=1), dt.time(0, 30), dt.timezone.utc)
            if back == 0:
                finished = dt.datetime.combine(day, dt.time(0, 40), dt.timezone.utc)
            db.run("INSERT INTO sessions(id,kind,learner,started,finished,answers,contest,day,ranked)"
                   " VALUES (?,?,?,?,?,'{}',?,?,?)", secrets.token_urlsafe(12), "challenge", makeup,
                   finished.isoformat(), finished.isoformat(), "daily-" + day.isoformat(),
                   day.isoformat(), int(back != 1))
        streak = compete.challenge_streak(makeup)
        assert_ok(streak["current"] == 7 and streak["strip"][-2]["state"] == "made_up",
                  "a Daily made up within 48 hours preserves the challenge streak")
        assert_ok(c.get("/api/contest/daily/review", headers=head(a)).status_code == 200 and
              len(c.get("/api/contest/daily/review", headers=head(a)).json()["items"]) == 10,
              "finished learner can review ten twin questions")
        racer = learner("race")
        target_pid = compete._pid(a)
        race_lobby = c.get(f"/api/contest/daily?race={target_pid}", headers=head(racer))
        assert_ok(race_lobby.status_code == 200 and race_lobby.json()["race"]["points"] == 260,
                  "a public finished run can be selected as a race")
        race_start = c.post(f"/api/contest/daily/start?race={target_pid}", headers=head(racer)).json()
        race_sid = race_start["session"]
        for index in range(3):
            question = race_start["question"] if index == 0 else c.post(
                f"/api/drill/{race_sid}/next", headers=head(racer)).json()["question"]
            original = question_for(race_sid, question["id"])
            c.post(f"/api/drill/{race_sid}/answer", headers=head(racer),
                   json={"question_id": question["id"], "answer": answer_of(original), "ms": 60_000})
        first_pacer = c.get("/api/contest/daily/pacer", headers=head(racer)).json()["pacer"]
        second_pacer = c.get("/api/contest/daily/pacer", headers=head(racer)).json()["pacer"]
        assert_ok(len(first_pacer["marks"]) == 3 and first_pacer["at"] == second_pacer["at"],
                  "race pacer reveals only answered slots and freezes at the verdict")
        c.post(f"/api/drill/{race_sid}/finish", headers=head(racer))
        race_result = c.get("/api/contest/daily", headers=head(racer)).json()["me"]
        assert_ok(race_result["ranked"] and race_result["result"]["race"]["them"] == 260,
                  "a first live race is ranked and reports the opponent's score")
        priced = c.get("/api/contest/daily/debrief", headers=head(racer)).json()
        assert_ok(len(priced["lost"]) == 15 and sum(row["pts"] for row in priced["lost"]) ==
                  priced["max"] - priced["points"],
                  "debrief prices early hand-in skips, pace and finish exactly")
        rematch = c.post("/api/contest/daily/rematch", headers=head(racer), json={"when": "now"})
        assert_ok(rematch.status_code == 200, "missed contest slots start a rematch")
        rematch_sid = rematch.json()["session"]
        rematch_cfg = json.loads(db.one("SELECT cfg FROM sessions WHERE id=?", rematch_sid)["cfg"])
        assert_ok(len(rematch_cfg["rematch_map"]) == 7 and
                  all(q["original"].startswith("c") for q in rematch_cfg["rematch_map"]),
                  "rematch keeps every skipped slot's type and tier")
        recovered = 0
        for index, cell in enumerate(rematch_cfg["rematch_map"]):
            asked = c.post(f"/api/drill/{rematch_sid}/next", headers=head(racer)).json()["question"]
            original = question_for(rematch_sid, asked["id"])
            assert_ok((original["key"], original["difficulty"], original["type"]) ==
                      (cell["template"], cell["tier"], cell["format"]),
                      "rematch serves the original slot's type, tier and format")
            if index < 2:
                given = answer_of(original)
                recovered += cell["pts"]
            else:
                given = (answer_of(original) + 1) % 4 if original["type"] == "mcq" else "999999999"
            marked = c.post(f"/api/drill/{rematch_sid}/answer", headers=head(racer),
                            json={"question_id": asked["id"], "answer": given, "ms": 60_000})
            assert_ok(marked.status_code == 200, "rematch answer is filed")
        c.post(f"/api/drill/{rematch_sid}/finish", headers=head(racer))
        followup = c.get("/api/contest/daily", headers=head(racer)).json()["me"]["followup"]
        assert_ok(followup["won_back"] == recovered and followup["of"] == sum(
                  cell["pts"] for cell in rematch_cfg["rematch_map"]),
                  "won-back totals only recovered original slot points")
        db.run("UPDATE learners SET board='hidden' WHERE id=?", a)
        assert_ok(c.get(f"/api/contest/daily?race={target_pid}", headers=head(racer)).status_code == 403,
                  "hiding a learner revokes their race link")
        db.run("UPDATE learners SET board='name' WHERE id=?", a)
        grid = c.get("/api/contest/daily/grid", headers=head(a)).json()
        assert_ok(grid["rows"] and all(len(r["marks"]) == 10 for r in grid["rows"]),
              "contest grid has one mark per slot")
        board = c.get("/api/contest/daily/board", headers=head(a)).json()
        assert_ok(board["you"]["points"] == 260 and len(board["pars"]) in (4, 5),
              "real ranks and four or five par rows share the board")
        yesterday = (dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=1)).isoformat()
        db.run("INSERT OR REPLACE INTO rank_snapshots(day,board,learner,rank,value) VALUES (?,?,?,?,?)",
               yesterday, "points:week:all:math::value", a, 4, 200)
        moving = c.get("/api/leaderboard?metric=points&period=week", headers=head(a)).json()
        assert_ok(moving["you"]["move"] == 3 and moving["you"]["gap"] == 0 and
                  all("gap" in entry for entry in moving["entries"]),
                  "leaderboard shows movement and the gap from one rank source")
        assert_ok(c.get("/api/compete/me", headers=head(a)).json()["rating"] != 1000,
              "ranked answers move contest rating")
        assert_ok(c.get("/api/leaderboard", headers=head(a)).status_code == 200,
              "practice rank leaderboard responds")
        assert_ok(c.get("/api/contest/daily/debrief", headers=head(a)).json()["points"] == 260,
              "debrief keeps the contest points")
        assert_ok(c.get("/api/contests?status=upcoming", headers=head(a)).json()["total"] >= 1,
              "future contests are scheduled")
        private = c.post("/api/contests", headers=head(a), json={
            "title": "Friday Five", "templates": ["eqx.add_polys"], "count": 5,
            "repeat": {"every": "day", "rounds": 3}, "strict": True, "twin": True}).json()
        code, root = private["code"], private["id"]
        assert_ok(len(code) == 6 and all(ch in "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" for ch in code),
              "private invite code uses six unambiguous characters")
        rounds = db.rows("SELECT id,opens FROM contests WHERE id=? OR series=? ORDER BY round", root, root)
        assert_ok(len(rounds) == 3 and all((dt.datetime.fromisoformat(rounds[i]["opens"]) -
              dt.datetime.fromisoformat(rounds[i - 1]["opens"])).days == 1 for i in (1, 2)),
              "private series opens on consecutive days")
        joined = c.post("/api/join", headers=head(b), json={"code": code})
        assert_ok(joined.status_code == 200 and joined.json()["kind"] == "contest" and
              b in compete.private_members(rounds[1]["id"]), "one join enters every series round")
        first_nudge = c.post("/api/compete/nudge", headers=head(a), json={"contest": root, "member": b})
        second_nudge = c.post("/api/compete/nudge", headers=head(a), json={"contest": root, "member": b})
        assert_ok(first_nudge.status_code == 200 and second_nudge.status_code == 429,
              "only one nudge per entrant per round")
        assert_ok(c.get(f"/api/contest/{root}/grid", headers=head(b)).status_code == 403,
              "private grid is gated before finishing")
        private_sid, _ = play(c, a, root, flag_first=True)
        private_result = c.get(f"/api/contest/{root}", headers=head(a)).json()["me"]["result"]
        assert_ok(private_result["confirmed"] == 1 and private_result["voided"] == 0,
              "held confirm preserves the original right answer")
        private_cfg = json.loads(db.one("SELECT cfg FROM sessions WHERE id=?", private_sid)["cfg"])
        private_cfg["rematch_due"] = today
        db.run("UPDATE sessions SET cfg=? WHERE id=?", json.dumps(private_cfg), private_sid)
        open_history = c.get("/api/compete/history?followup=open", headers=head(a)).json()
        assert_ok(any(row["session"] == private_sid and row["followup"]["due"] == today
                      for row in open_history["history"]),
                  "history open filter includes a due rematch")
        assert_ok(c.get(f"/api/contest/{root}/grid", headers=head(a)).status_code == 200,
              "finished entrant sees private grid")
        assert_ok(c.get("/api/groups").status_code == 404 and c.get("/api/classes").status_code == 404,
              "class and group APIs are absent")
        assert_ok(compete.series_streak(root)["current"] == 0 and
              len(compete.series_board(root)["entries"]) == 2,
              "series board includes members and honest unfinished rounds")
        assert_ok(compete.due_today(b), "joined private contest appears in due today")
        assert_ok(c.get("/api/contest/daily/board", headers=head(a)).json()["you"]["pid"] != a,
              "public board uses an opaque participant id")
        ids = db.rows("SELECT slot,qhash FROM contest_items WHERE contest=?", "daily-" + today)
        by_slot = {}
        for item in ids:
            slot = item["slot"]
            by_slot.setdefault(slot, set())
            assert item["qhash"] not in by_slot[slot]
            by_slot[slot].add(item["qhash"])
        assert_ok(bool(ids), "whole-question twin hashes are unique within every slot")
        # A closed week is permanent even while fresh Dailies arrive.
        old_week = "2025-W02"
        db.run("DELETE FROM champions WHERE kind='week' AND period=?", old_week)
        db.run("DELETE FROM sessions WHERE contest='s8-historic'")
        old_people = [learner("champ") for _ in range(3)]
        db.run("INSERT OR IGNORE INTO contests(id,kind,title,opens,closes,count,seconds,spec,created,subject)"
               " VALUES ('s8-historic','daily','Old Daily','2025-01-06T00:00:00+00:00',"
               " '2025-01-13T12:00:00+00:00',10,950,'{}','2025-01-06T00:00:00+00:00','math')")
        for index, person in enumerate(old_people):
            db.ensure_learner(person)
            db.run("UPDATE learners SET board=? WHERE id=?", "hidden" if index == 0 else "name", person)
            db.run("INSERT INTO sessions(id,kind,learner,started,finished,answers,result,contest,ranked,points)"
                   " VALUES (?,?,?,?,?,'{}',?,?,1,?)", secrets.token_urlsafe(12), "challenge", person,
                   "2025-01-08T10:00:00+00:00", "2025-01-08T10:10:00+00:00",
                   json.dumps({"net": 30 - index * 10, "rating_before": 1000,
                               "rating_after": 1030 - index * 10}), "s8-historic", 230 - index * 10)
        past = c.get(f"/api/leaderboard?period=week&at={old_week}", headers=head(b))
        assert_ok(past.status_code == 200 and past.json()["closed"] and
                  [e["value"] for e in past.json()["entries"][:3]] == [230, 220, 210],
                  "closed week keeps its ranked values")
        hall = c.get("/api/compete/champions?kind=week&before=2025-W03", headers=head(b)).json()
        old = next(p for p in hall if p["period"] == old_week)
        assert_ok(len(old["boards"]["points"]) == 3 and len(old["boards"]["net"]) == 3 and
                  len(old["boards"]["change"]) == 3,
                  "closed week writes points, over-par and change podiums")
        assert_ok(old["boards"]["points"][0]["name"] == "Anonymous" and
                  c.get("/api/compete/champions?kind=week&before=2025-W03", headers=head(old_people[0]))
                  .json()[0]["boards"]["points"][0]["name"] != "Anonymous",
                  "hidden champion stays anonymous to others")
        assert_ok(c.get(f"/api/leaderboard?period=week&at={old_week}", headers=head(b)).json()
                  ["entries"] == past.json()["entries"], "closed board is stable on repeated reads")
        rush_cid = next(row["id"] for row in compete.ensure() if row["kind"] == "rush" and
                        row["opens"] <= compete._iso(compete._now()))
        rush_person = learner("rush")
        def rush_pick(q, right):
            original = question_for(rush_sid, q["id"])
            answer = answer_of(original)
            return answer if right else ((answer + 1) % 4 if original["type"] == "mcq" else "999999999")
        rush = c.post(f"/api/contest/{rush_cid}/start", headers=head(rush_person)).json()
        rush_sid = rush["session"]
        for strike in range(3):
            rush = c.post(f"/api/contest/{rush_cid}/answer", headers=head(rush_person),
                          json={"sid": rush_sid, "question_id": rush["question"]["id"],
                                "answer": rush_pick(rush["question"], False), "ms": 60_000}).json()
        assert_ok(rush["done"] and rush["result"]["right"] == 0 and len(rush["result"]["strikes"]) == 3,
                  "Rush ends on its third strike")
        again = c.post(f"/api/contest/{rush_cid}/start", headers=head(rush_person)).json()
        rush_sid = again["session"]
        ratings_seen, keys = [], []
        for _ in range(5):
            ratings_seen.append(again["item_rating"])
            keys.append(question_for(rush_sid, again["question"]["id"])["key"])
            again = c.post(f"/api/contest/{rush_cid}/answer", headers=head(rush_person),
                           json={"sid": rush_sid, "question_id": again["question"]["id"],
                                 "answer": rush_pick(again["question"], True), "ms": 60_000}).json()
        assert_ok(len(set(keys)) == 5 and all(b > a for a, b in zip(ratings_seen, ratings_seen[1:])),
                  "five clean Rush answers climb through fresh item ratings")
        for strike in range(3):
            again = c.post(f"/api/contest/{rush_cid}/answer", headers=head(rush_person),
                           json={"sid": rush_sid, "question_id": again["question"]["id"],
                                 "answer": rush_pick(again["question"], False), "ms": 60_000}).json()
        rush_board = c.get(f"/api/contest/{rush_cid}/board", headers=head(rush_person)).json()
        assert_ok(again["done"] and len({row["pid"] for row in rush_board["entries"]}) ==
                  rush_board["players"] and
                  rush_board["you"]["right"] == 5 and rush_board["you"]["runs"] == 2,
                  "Rush weekly board keeps one best run per learner")
        timed_person = learner("rush-timing")
        prefs.put(timed_person, {"contest_timing": "x1.5"})
        timed = c.post(f"/api/contest/{rush_cid}/start", headers=head(timed_person)).json()
        timed_sid = timed["session"]
        first = question_for(timed_sid, timed["question"]["id"])
        paced = c.post(f"/api/contest/{rush_cid}/answer", headers=head(timed_person),
                       json={"sid": timed_sid, "question_id": first["id"],
                             "answer": answer_of(first), "ms": first["budget_ms"] * 2}).json()
        assert_ok(paced["strikes"] == 0, "Rush slow strike respects extended contest time")
        # The S9 provider is owned by the Words branch. Exercise the S8
        # contract with fixed SAT-form items until those functions land.
        real_part = deps.part
        reviewed, missed = [], []
        def sprint_items(person, seed, n, level):
            return [{"template": "rw.mock", "seed": seed + i, "word": "mock",
                     "kind": "incontext" if i % 2 == 0 else "transition",
                     "stem": "Which choice completes the text?", "text": "A short passage.",
                     "choices": ["right", "lure", "weak", "opposite"], "answer_index": 0,
                     "traps": [None, "topical lure", "weak", "opposite"],
                     "reasons": ["Right fit", "Topical lure", "Too weak", "Opposite"]}
                    for i in range(12)]
        def fake_part(module, name):
            if module == "words":
                return {"sprint_items": sprint_items,
                        "grade": lambda *args, **kwargs: reviewed.append((args, kwargs)),
                        "record_contest_miss": lambda *args: missed.append(args)}.get(name)
            return real_part(module, name)
        deps.part = fake_part
        try:
            word_cid = next(row["id"] for row in compete.ensure() if row["kind"] == "words" and
                            row["opens"] <= compete._iso(compete._now()))
            word_person = learner("word-sprint")
            live = c.get("/api/contests?status=live&limit=50", headers=head(word_person)).json()
            entries = live["contests"]
            for offset in range(50, live["total"], 50):
                if any(row["kind"] == "words" for row in entries):
                    break
                entries.extend(c.get(f"/api/contests?status=live&limit=50&offset={offset}",
                                     headers=head(word_person)).json()["contests"])
            assert_ok(any(row["kind"] == "words" and row["subject"] == "rw" for row in entries),
                      "Word Sprint schedules as R&W when S9 provides items")
            word_run = c.post(f"/api/contest/{word_cid}/start", headers=head(word_person)).json()
            word_sid = word_run["session"]
            for index in range(12):
                word_run = c.post(f"/api/contest/{word_cid}/answer", headers=head(word_person),
                                  json={"sid": word_sid, "question_id": word_run["question"]["id"],
                                        "answer": 0 if index < 9 else 1, "ms": 4000}).json()
            result = word_run["result"]
            assert_ok(word_run["done"] and result["score"] == 8.0 and result["right"] == 9 and
                      result["wrong"] == 3 and result["traps"][0]["n"] == 3,
                      "Word Sprint scores 9 right and 3 wrong as 8.0 with named traps")
            review = c.get(f"/api/contest/{word_cid}/review", headers=head(word_person)).json()
            debrief = c.get(f"/api/contest/{word_cid}/debrief", headers=head(word_person)).json()
            assert_ok(all(item["question"]["kind"] in ("incontext", "transition")
                          for item in review["items"]) and len(debrief["missed"]) == 3,
                      "Word Sprint review contains SAT forms and missed words")
            assert_ok(len(reviewed) == 12 and len(missed) == 3 and
                      not db.one("SELECT 1 FROM attempts WHERE session=?", word_sid),
                      "Word Sprint writes only Words reviews, never Math attempts")
            assert_ok(c.get(f"/api/contest/{word_cid}/board", headers=head(word_person)).json()
                      ["you"]["score"] == 8.0 and
                      c.get("/api/leaderboard?metric=points&subject=math", headers=head(word_person))
                      .json()["you"] is None and
                      c.get("/api/leaderboard?metric=points&subject=rw", headers=head(word_person))
                      .json()["you"]["value"] == 8.0,
                      "Word Sprint board and subject standings stay separate from Math")
        finally:
            deps.part = real_part
            db.run("DELETE FROM sessions WHERE contest LIKE 'words-%' AND learner LIKE 'a:s8checkword-sprint%'")
            db.run("DELETE FROM contests WHERE kind='words'")
        final_person = learner("final")
        db.ensure_learner(final_person)
        sat_day = next(day for day in compete.SAT_DATES if day >= today)
        final_cid = "final-" + sat_day
        compete.contest(final_cid)
        db.run("UPDATE learners SET exam_date=? WHERE id=?", sat_day, final_person)
        circle_name = practice.catalogue()["by_topic"]["circles"][0]
        cards = []
        for seed in range(100):
            item = practice.generate(circle_name, seed, fmt="mcq")
            if item.fmt == "mcq" and any(item.reasons):
                q = practice.to_question(practice.Card.of(circle_name, seed, item, "circles"), len(cards) + 1)
                q["id"] = f"f{len(cards) + 1:02d}"
                q["budget_ms"] = 95_000
                cards.append(q)
            if len(cards) == 2:
                break
        assert len(cards) == 2
        final_sid = secrets.token_urlsafe(12)
        db.run("INSERT INTO sessions(id,kind,learner,started,finished,questions,answers,result,contest,ranked)"
               " VALUES (?,?,?,?,?,?,?, ?,?,1)", final_sid, "module", final_person,
               today + "T00:00:00+00:00", today + "T01:00:00+00:00",
               json.dumps({"module1": cards}), "{}", json.dumps({"estimate": {"low": 610, "high": 750},
                                                        "route": "upper"}), final_cid)
        for q in cards:
            reason = next(text for text in q["reasons"] if text)
            db.run("INSERT INTO attempts(learner,session,qid,template,seed,topic,difficulty,fmt,correct,reason,ms,at)"
                   " VALUES (?,?,?,?,?,?,?,?,0,?,?,?)", final_person, final_sid, q["id"], q["key"], q["seed"],
                   q["topic"], q["difficulty"], q["type"], reason, 210_000, today + "T01:00:00+00:00")
        focus = compete.final_focus(final_person)
        card = c.get(f"/api/contest/{final_cid}/card", headers=head(final_person))
        assert_ok(focus["mode"] == "last_week" and "circles" in focus["skip_first"] and
                  card.status_code == 200 and "7:45 AM" in card.json()["doors"],
                  "Final focus names slow wrong skills and the test-day doors")
        db.run("UPDATE learners SET exam_date=? WHERE id=?",
               (dt.date.fromisoformat(sat_day) + dt.timedelta(days=42)).isoformat(), final_person)
        assert_ok(compete.final_focus(final_person)["mode"] == "focus",
                  "a later exam date keeps Final advice without entering the taper")
        drill_state = deps.part("drill", "state")
        pending(bool(drill_state and "state_extra" in inspect.getsource(drill_state)),
                "S4 practice runner calls compete.state_extra")
        test_path = pathlib.Path(__file__).resolve().parents[1] / "api_test.py"
        test_source = test_path.read_text() if test_path.exists() else ""
        pending("confirm_next" in test_source and "finish_contest" in test_source,
                "S5 test runner calls Compete confirm and finish hooks")
        pending(deps.part("achievements", "FOLDED") is not None,
                "S1 achievement rules expose FOLDED")
        pending(deps.part("words", "sprint_items") is not None and
                deps.part("words", "record_contest_miss") is not None,
                "S9 Words exposes sprint_items and record_contest_miss")
        pending(deps.part("habits", "families") is not None and
                deps.part("habits", "family_of") is not None,
                "U6 habits catalogue and reason-family matcher are available")
        supply = compete._read_supply()
        passing = set(compete.pool("daily", "easy", need=1000)) if supply else set()
        supplied = sum(name in passing and ("easy", "spr") in blueprint.abilities()[name]
                       for name in blueprint.by_domain()["Advanced Math"])
        pending(supplied >= 3, "C26 Advanced Math easy grid-in supply has at least 3 templates")
        print("S8 checks passed (external contracts may be PENDING)")


def supply() -> None:
    with TestClient(app):
        if not compete._read_supply():
            print("Surveying up to 3,000 seeds per template and tier; this may take several minutes.")
            compete.survey_supply()
        required = set()
        for form, module in (("module1", 1), ("module2_lower", 2), ("module2_upper", 2)):
            required.update(blueprint.slots(form, module))
        for back in range(2):
            day = compete.local_day() + dt.timedelta(days=back)
            for name, tier, fmt in compete._daily_slots(day):
                required.add((blueprint.kinds()[name]["domain"], tier, fmt))
        shortages = []
        for domain, names in blueprint.by_domain().items():
            for tier in ("easy", "medium", "hard"):
                for fmt in (None, "mcq", "spr"):
                    passing = set(compete.pool("daily", tier, need=1000))
                    count = sum(name in passing and (any(t == tier for t, _ in blueprint.abilities()[name])
                                 if fmt is None else (tier, fmt) in blueprint.abilities()[name])
                                for name in names)
                    needed = (domain, tier, fmt) in required
                    print(f"{domain}\t{tier}\t{fmt or 'either'}\t{count}\t{'required' if needed else 'optional'}")
                    if needed and count < 3:
                        shortages.append((domain, tier, fmt, count))
        pending(not shortages, f"C26 required supply cells each have at least three templates; gaps={shortages}")


def simulate(n: int) -> None:
    with TestClient(app):
        row = compete.contest("daily", 0)
        slots = compete._json(row["spec"], {})["slots"]
        for i in range(n):
            questions = compete.twin_questions(learner(f"sim{i}"), row["id"], slots)
            assert [q["key"] for q in questions] == [cell[0] for cell in slots]
        rows = db.rows("SELECT slot,qhash,COUNT(*) AS n FROM contest_items WHERE contest=?"
                       " GROUP BY slot,qhash HAVING COUNT(*)>1", row["id"])
        assert not rows, rows
        print(f"simulated {n} entrants without whole-question collisions")


def traps() -> None:
    with TestClient(app):
        survey = compete.trap_families()
        if not survey["families"]:
            print("PENDING  Trap of the week:", survey["reason"],
                  "(server/habits.py has not landed on master)")
            return
        print("topic floor", survey["topic_floor"], "no-repeat window", survey["window"])
        qualified = {row["family"]["id"] for row in survey["families"]}
        for fid, entry in survey["survey"].items():
            print(fid, *(f"{tier}={len(entry['tiers'][tier])}" for tier in ("easy", "medium", "hard")),
                  "topics=" + str(len(entry["topics"])), "qualified=" + str(fid in qualified))
        monday = dt.datetime.now(dt.timezone.utc).date()
        monday -= dt.timedelta(days=monday.weekday())
        themes = []
        for offset in range(12):
            day = monday + dt.timedelta(days=7 * offset)
            week = f"{day.isocalendar().year}-W{day.isocalendar().week:02d}"
            theme = compete.trap_theme(week, survey)
            slots = compete._trap_slots(week, theme, survey["topic_floor"])
            assert len(slots) == 10 and [s[1] for s in slots].count("easy") == 3
            assert [s[1] for s in slots].count("medium") == 4 and [s[1] for s in slots].count("hard") == 3
            assert theme["family"]["id"] != "slip"
            assert theme["family"]["id"] not in themes[-survey["window"]:]
            themes.append(theme["family"]["id"])
        print("12 trap weeks:", ", ".join(themes))


def check(client: TestClient) -> None:
    # test_flow has its own scratch DB and intentionally rewrites a Daily.
    # Exercise S8 on the dedicated database in a fresh process instead.
    root = pathlib.Path(__file__).resolve().parents[2]
    env = {**os.environ, "SATF_DB": str(root / "server" / "s8.db"), "PYTHONPATH": str(root)}
    result = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve())],
                            cwd=root, env=env, text=True, capture_output=True, check=False)
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)
    print("ok  S8 Compete server checks")


if __name__ == "__main__":
    if "--supply" in sys.argv:
        supply()
    elif "--traps" in sys.argv:
        traps()
    elif "--simulate" in sys.argv:
        at = sys.argv.index("--simulate")
        simulate(int(sys.argv[at + 1]))
    else:
        run()
