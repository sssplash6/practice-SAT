"""S8 Compete backend acceptance checks.

Run from the repository root with SATF_DB=$PWD/server/s8.db PYTHONPATH=.
Only the dedicated S8 database may be used: these checks create sittings.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import secrets
import subprocess
import sys

from fastapi.testclient import TestClient

from server import compete, db, practice
from server.app import app


def assert_ok(condition: bool, message: str) -> None:
    assert condition, message
    print("ok ", message)


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
        assert_ok(c.get("/api/contest/daily/review", headers=head(a)).status_code == 403,
              "review is gated before finishing")
        sid, originals = play(c, a)
        result = c.get("/api/contest/daily", headers=head(a)).json()["me"]["result"]
        assert_ok(result["points"] == 260 and result["points_parts"] ==
              {"base": 200, "pace": 50, "finish": 10}, "perfect Daily scores 260 points")
        assert_ok(result["par"]["base"] == json.loads(db.one("SELECT cfg FROM sessions WHERE id=?", sid)["cfg"])
              ["par"]["base"], "par is frozen at contest start")
        assert_ok(c.get("/api/contest/daily/review", headers=head(a)).status_code == 200 and
              len(c.get("/api/contest/daily/review", headers=head(a)).json()["items"]) == 10,
              "finished learner can review ten twin questions")
        grid = c.get("/api/contest/daily/grid", headers=head(a)).json()
        assert_ok(grid["rows"] and all(len(r["marks"]) == 10 for r in grid["rows"]),
              "contest grid has one mark per slot")
        board = c.get("/api/contest/daily/board", headers=head(a)).json()
        assert_ok(board["you"]["points"] == 260 and len(board["pars"]) in (4, 5),
              "real ranks and four or five par rows share the board")
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
        print("S8 checks passed")


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
    run()
