"""S7 Plan server acceptance. Run with the S7 database, never the dev database.

    SATF_DB=$PWD/server/s7.db PYTHONPATH=. python3 server/checks/s7.py
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import math
import secrets
import time
from collections import Counter

from fastapi.testclient import TestClient

from server import db, estimate, plan, practice, prefs, progress
from server.app import app

logging.getLogger("httpx").setLevel(logging.WARNING)


def token() -> str:
    return "a:s7" + secrets.token_hex(8)


def call(client: TestClient, method: str, path: str, body=None, learner: str | None = None,
         status: int = 200):
    headers = {"X-Tz": "0"}
    if learner:
        headers["X-Learner"] = learner
    response = client.request(method, path, headers=headers, json=body)
    assert response.status_code == status, (method, path, response.status_code, response.text[:500])
    if response.headers.get("content-type", "").startswith("application/json"):
        return response.json()
    return response.text


def base(exam: dt.date, **changes) -> dict:
    return {"current": 520, "target": 700, "exam_date": exam.isoformat(), "minutes": 45,
            "days": "1111100", "tests": "weekly", "test_size": "module", **changes}


def next_saturday(day: dt.date, weeks: int = 7) -> dt.date:
    return day + dt.timedelta(days=weeks * 7 + (5 - day.weekday()) % 7)


def study_after(days: list[dict], day: str) -> dict:
    return next(d for d in days if d["date"] > day and d["kind"] in ("practice", "test"))


def check_empty_preview_and_validation(client: TestClient, exam: dt.date) -> tuple[str, dict]:
    learner = token()
    empty = call(client, "GET", "/api/plan", learner=learner)
    assert empty["active"] is None and empty["bank"]["topics"] == 19
    assert empty["bank"]["templates"] == sum(map(len, practice.catalogue()["by_topic"].values())) and empty["bank"]["example"]["label"]
    assert empty["proposal"]["cfg"]["measure"] is True
    assert [t["kind"] for t in empty["proposal"]["preview"]["sample_day"]["tasks"][:2]] == ["test", "map"]
    cfg = base(exam, focus={"Geometry and Trigonometry": "focus", "Algebra": "strong"})
    t = time.perf_counter()
    p = call(client, "POST", "/api/plan/preview", cfg, learner)
    assert time.perf_counter() - t < .6
    assert p["split"]["Geometry and Trigonometry"] > .15
    assert p["split"]["Algebra"] < .35
    assert abs(sum(p["split"].values()) - 1) < .01
    assert p["target_note"]["points_pct"] == 88 and p["target_note"]["route_right"] == 14
    capped = call(client, "POST", "/api/plan/preview", {**cfg, "target": 800}, learner)
    assert capped["target_note"]["capped"] is True
    assert len(p["week"]) == 7 and p["sample_day"]["tasks"]
    call(client, "PUT", "/api/plan/draft", {"step": 3, "fields": {"minutes": 90}}, learner)
    bad = [
        {"target": 190}, {"target": 500}, {"exam_date": (plan.today() - dt.timedelta(days=1)).isoformat()},
        {"exam_date": "2026-02-30"}, {"days": "0000000"}, {"tests": "hourly"},
        {"focus": {d: "focus" for d in progress.DOMAINS[:3]}},
        {"off": [[exam.isoformat(), (exam - dt.timedelta(days=1)).isoformat()]]},
        {"name": "x" * 41}, {"custom": [{"title": "x" * 61, "minutes": 20, "day": plan.today().isoformat()}]},
    ]
    for change in bad:
        call(client, "POST", "/api/plan", {**cfg, **change}, learner, 422)
    assert call(client, "GET", "/api/plan", learner=learner)["draft"]["step"] == 3
    print("ok  proposal, preview arithmetic, validation and durable draft")
    return learner, cfg


def check_create_schedule(client: TestClient, learner: str, cfg: dict, exam: dt.date) -> dict:
    t = time.perf_counter()
    payload = call(client, "POST", "/api/plan", cfg, learner)
    assert time.perf_counter() - t < 1, "warm create must finish within one second"
    assert payload["active"]["id"] and payload["draft"] is None
    assert payload["active"]["cfg"]["target"] == 700
    days = payload["days"]
    assert days[-1]["kind"] == "exam" and days[-2]["kind"] == "eve"
    assert days[-2]["tasks"] and days[-2]["tasks"][0]["title"] == "Read your trap sheet"
    taper = [d for d in days if dt.date.fromisoformat(d["date"]) in plan._taper_dates(cfg)]
    assert len(taper) == 5 and all(d["kind"] == "practice" and d["minutes"] == 27 for d in taper)
    assert all(not any(t["kind"] in ("test", "learn", "map") for t in d["tasks"]) for d in taper)
    rehearsals = [d for d in days if any(t.get("rehearsal") for t in d["tasks"])]
    assert rehearsals and len(rehearsals) <= 2
    assert all((exam - dt.date.fromisoformat(d["date"])).days >= 6 for d in rehearsals)
    for d in rehearsals:
        test = next(t for t in d["tasks"] if t["kind"] == "test")
        assert test["start"]["body"]["pause"] is False and test["count"] == 44
    assert all(t["subject"] in ("math", "rw") for d in days for t in d["tasks"])
    for d in days:
        if d["budget"]:
            assert d["budget"]["q"] >= 0
            assert sum(t["minutes"] for t in d["tasks"] if t.get("counted")) <= d["minutes"] + .2, d["date"]
    for d in days[:20]:
        assert call(client, "GET", f"/api/plan/day/{d['date']}", learner=learner)["date"] == d["date"]
    call(client, "GET", f"/api/plan/day/{(exam + dt.timedelta(days=1)).isoformat()}", learner=learner, status=404)
    assert call(client, "GET", "/api/plan/progress", learner=learner)["coverage"]["math"]["counts"]
    assert plan.today_summary(learner, 0)["id"] == payload["active"]["id"]
    assert plan.shell_part(learner, 0)["plan"]["id"] == payload["active"]["id"]
    shell = call(client, "GET", "/api/shell", learner=learner)
    assert shell["plan"]["id"] == payload["active"]["id"] and isinstance(shell.get("next", []), list)
    print("ok  create, final rehearsals and taper, budgets, days and Today helpers")
    return payload


def check_allocation_and_time(learner: str, cfg: dict, payload: dict) -> None:
    cfg = payload["active"]["cfg"]
    start = dt.date.fromisoformat(payload["active"]["start"])
    exam = dt.date.fromisoformat(cfg["exam_date"])
    allocated = plan.allocate(learner, cfg, start, exam, payload["active"]["id"])
    practice_days = [d for d in payload["days"] if d["kind"] == "practice"][:20]
    recent = []
    for d in practice_days:
        topics = allocated.get(d["date"], [])
        assert not any(t in recent[-1] and t in recent[-2] for t in topics) if len(recent) >= 2 else True
        recent.append(set(topics))
    pins = plan.pin_schedule(learner, cfg, start, exam, payload["active"]["id"])
    assert all(len(v) <= 1 and v[0]["count"] == 2 for v in pins.values())
    assert all(p["tier"] in ("easy", "medium", "hard") for v in pins.values() for p in v)
    pre_final_slots = sum(plan._slots(math.floor(d["minutes"] * 60 / 95)) for d in payload["days"]
                          if d["kind"] == "practice" and d["phase"] != "Final")
    assert len(pins) <= .3 * pre_final_slots + 1
    coverage = payload["coverage"]["math"]
    assert len(coverage["cells"]) == 57
    assert coverage["counts"]["unplanned"] == sum(c["needed"] and c["state"] != "proven" and not c["planned"]
                                                  for c in coverage["cells"])
    row = plan.active_row(learner)
    for minutes in (10, 15, 30, 45, 60, 90):
        day = plan.day_view(learner, row, start, preview_minutes=minutes)
        assert day["budget"]["q"] == math.floor((day["budget"]["g"] - day["budget"]["w"]) * 60 /
                                                day["budget"]["s"])
        assert sum(t["minutes"] for t in day["tasks"] if t["counted"]) <= minutes + .2
    print("ok  deterministic allocation, coverage pins, and 10–90 minute budget")


def check_tasks_days(client: TestClient, learner: str, payload: dict) -> None:
    pid = payload["active"]["id"]
    practice_day = next(d for d in payload["days"] if d["date"] >= payload["today"]["date"]
                        and any(t["kind"] in ("focus", "map") for t in d["tasks"]))
    day = practice_day["date"]
    focus = next(t for t in practice_day["tasks"] if t["kind"] in ("focus", "map"))
    call(client, "PATCH", f"/api/plan/{pid}/tasks/{focus['id']}",
         {"day": day, "status": "done", "minutes": 15, "where": "khan"}, learner)
    marked = call(client, "GET", f"/api/plan/day/{day}", learner=learner)
    assert next(t for t in marked["tasks"] if t["id"] == focus["id"])["status"] == "marked"
    if day == payload["today"]["date"]:
        assert marked["minutes_done"] >= 15
    call(client, "PATCH", f"/api/plan/{pid}/tasks/{focus['id']}", {"day": day, "status": "todo"}, learner)
    restored = call(client, "GET", f"/api/plan/day/{day}", learner=learner)
    assert next(t for t in restored["tasks"] if t["id"] == focus["id"])["status"] == "todo"
    own = call(client, "POST", f"/api/plan/{pid}/tasks",
               {"day": day, "title": "Reading & Writing", "minutes": 30, "type": "rw"}, learner)
    tid = own["id"]
    assert next(t for t in own["days"][0]["tasks"] if t["id"] == tid)["subject"] == "rw"
    call(client, "PATCH", f"/api/plan/{pid}/tasks/{tid}", {"day": day, "status": "done"}, learner)
    done = call(client, "GET", f"/api/plan/day/{day}", learner=learner)
    assert next(t for t in done["tasks"] if t["id"] == tid)["status"] == "done"
    if day == payload["today"]["date"]:
        assert done["minutes_done"] >= 30
    call(client, "PATCH", f"/api/plan/{pid}/tasks/{tid}", {"day": day, "status": "todo"}, learner)
    call(client, "DELETE", f"/api/plan/{pid}/tasks/{tid}", learner=learner)
    assert all(t["id"] != tid for t in call(client, "GET", f"/api/plan/day/{day}", learner=learner)["tasks"])
    repeat = call(client, "POST", f"/api/plan/{pid}/tasks",
                  {"repeat": "study_days", "title": "Read", "minutes": 10}, learner)
    upcoming = call(client, "GET", "/api/plan", learner=learner)["days"][:14]
    for d in upcoming:
        present = any(t["id"] == repeat["id"] for t in d["tasks"])
        assert present == (d["kind"] in ("practice", "test")), d["date"]
    call(client, "DELETE", f"/api/plan/{pid}/tasks/{repeat['id']}", learner=learner)
    skipped = call(client, "PATCH", f"/api/plan/{pid}/tasks/{focus['id']}",
                   {"day": day, "status": "skipped"}, learner)
    assert next(t for t in skipped["days"][0]["tasks"] if t["id"] == focus["id"])["status"] == "skipped"
    call(client, "PATCH", f"/api/plan/{pid}/tasks/{focus['id']}", {"day": day, "status": "todo"}, learner)
    next_day = study_after(payload["days"], day)["date"]
    moved = call(client, "PATCH", f"/api/plan/{pid}/tasks/{focus['id']}",
                 {"day": day, "to": next_day}, learner)["days"]
    assert next(t for t in moved[0]["tasks"] if t["id"] == focus["id"])["status"] == "moved"
    assert any(t["id"] == focus["id"] for t in moved[1]["tasks"])
    assert moved[1]["minutes"] > 45
    call(client, "PATCH", f"/api/plan/{pid}/tasks/{focus['id']}", {"day": day, "status": "todo"}, learner)
    no_time = call(client, "PATCH", f"/api/plan/{pid}/tasks/{focus['id']}",
                   {"day": day, "status": "skipped", "reason": "no_time"}, learner)["days"]
    assert next(t for t in no_time[0]["tasks"] if t["id"] == focus["id"])["status"] == "moved"
    assert next(t for t in no_time[0]["tasks"] if t["id"] == focus["id"])["moved_to"] == next_day
    call(client, "PATCH", f"/api/plan/{pid}/tasks/{focus['id']}", {"day": day, "status": "todo"}, learner)
    test_out = call(client, "PATCH", f"/api/plan/{pid}/tasks/{focus['id']}",
                    {"day": day, "status": "skipped", "reason": "know"}, learner)["test_out"]
    assert test_out["count"] == 8 and test_out["tiers"] == ["medium", "hard"]
    off = call(client, "PUT", f"/api/plan/{pid}/day/{day}", {"off": True}, learner)["days"][0]
    assert off["kind"] == "off"
    reset = call(client, "DELETE", f"/api/plan/{pid}/day/{day}", learner=learner)["days"][0]
    assert reset["kind"] in ("practice", "test")
    before = call(client, "GET", f"/api/plan/day/{day}", learner=learner)
    used = {topic for task in before["tasks"] for topic in task.get("topics", [])}
    alternate = next(topic for topic in plan.TOPICS if topic not in used)
    swapped = call(client, "PATCH", f"/api/plan/{pid}/tasks/{focus['id']}",
                   {"day": day, "swap": [alternate]}, learner)["days"][0]
    assert any(alternate in task.get("topics", []) for task in swapped["tasks"])
    print("ok  marks and Undo, own tasks, repeats, moves and day overrides")


def check_freeze_and_links(client: TestClient, learner: str, payload: dict) -> None:
    pid = payload["active"]["id"]
    today = plan.today()
    db.run("UPDATE plans SET start=? WHERE id=?", (today - dt.timedelta(days=3)).isoformat(), pid)
    plan_before = call(client, "GET", "/api/plan", learner=learner)
    frozen = db.rows("SELECT day,minutes FROM plan_days WHERE plan=? ORDER BY day", pid)
    assert len(frozen) >= 3
    before = {r["day"]: r["minutes"] for r in frozen}
    practice_day = next(d for d in plan_before["days"]
                        if d["date"] >= today.isoformat() and d["kind"] == "practice")
    current = practice_day["minutes"]
    patched = call(client, "PATCH", f"/api/plan/{pid}", {"minutes": 90}, learner)
    updated_day = next(d for d in patched["days"] if d["date"] == practice_day["date"])
    assert updated_day["minutes"] != current
    changed = db.one("SELECT kind,field,from_v,to_v FROM plan_events WHERE plan=? ORDER BY id DESC LIMIT 1", pid)
    assert changed["kind"] == "edit" and changed["field"] == "minutes"
    assert json.loads(changed["from_v"]) == 45 and json.loads(changed["to_v"]) == 90
    after = {r["day"]: r["minutes"] for r in db.rows("SELECT day,minutes FROM plan_days WHERE plan=?", pid)}
    assert all(after[d] == m for d, m in before.items())
    assert any(d["status"] == "missed" for d in patched["days"] if d["date"] < today.isoformat()
               and d["kind"] in ("practice", "test"))
    feed = call(client, "GET", f"/api/plan/{pid}/ics", learner=learner)
    active_feed = call(client, "GET", "/api/plan/ics", learner=learner)
    def stable_ics(value):
        return "\n".join(line for line in value.splitlines() if not line.startswith("DTSTAMP:"))
    assert stable_ics(active_feed) == stable_ics(feed)
    assert "BEGIN:VCALENDAR" in feed and "BEGIN:VALARM" in feed
    assert "SUMMARY:SAT" in feed and "DTSTART;VALUE=DATE:" in feed
    links = call(client, "POST", f"/api/plan/{pid}/links", {"cal": True, "view": True}, learner)
    assert links["cal"].startswith("/api/cal/")
    assert db.one("SELECT kind FROM links WHERE token=?", links["cal_token"])["kind"] == "cal"
    assert db.one("SELECT kind FROM links WHERE token=?", links["view_token"])["kind"] == "progress"
    assert stable_ics(call(client, "GET", links["cal"])) == stable_ics(feed)
    shared = call(client, "GET", links["view"])
    assert shared["days"] and shared["stats"] and learner not in json.dumps(shared)
    assert all("start" not in t for d in shared["days"] for t in d["tasks"])
    outside_view, outside_cal = secrets.token_urlsafe(16), secrets.token_urlsafe(16)
    for issued, kind in ((outside_view, "progress"), (outside_cal, "cal")):
        db.run("INSERT INTO links(token,learner,kind,created) VALUES (?,?,?,?)",
               issued, learner, kind, dt.datetime.now(dt.timezone.utc).isoformat())
    assert stable_ics(call(client, "GET", f"/api/cal/{outside_cal}.ics")) == stable_ics(feed)
    assert call(client, "GET", f"/api/plan/shared/{outside_view}")["active"]["id"] == pid
    db.run("UPDATE links SET revoked=? WHERE token IN (?,?)",
           dt.datetime.now(dt.timezone.utc).isoformat(), outside_view, outside_cal)
    call(client, "GET", f"/api/cal/{outside_cal}.ics", status=404)
    call(client, "GET", f"/api/plan/shared/{outside_view}", status=404)
    call(client, "POST", f"/api/plan/{pid}/links", {"cal": False, "view": False}, learner)
    call(client, "GET", links["cal"], status=404)
    call(client, "GET", links["view"], status=404)
    print("ok  frozen history, replan, calendar and revocable read-only link")


def check_rw_measure_lifecycle(client: TestClient, exam: dt.date) -> None:
    learner = token()
    cfg = {"sections": {"math": {"current": 560, "target": 700},
                        "rw": {"current": 500, "target": 650, "minutes": 30,
                               "focus": {"Standard English Conventions": "focus"}}},
           "exam_date": exam.isoformat(), "minutes": 45, "days": "1111100", "tests": "weekly"}
    item = call(client, "POST", "/api/plan", cfg, learner)
    pid = item["active"]["id"]
    assert item["score"]["total"]["start"] == 1060 and item["score"]["total"]["target"] == 1350
    first_study = next(d for d in item["days"] if d["kind"] == "practice")
    rw = [t for t in first_study["tasks"] if t.get("type") == "rw"]
    assert len(rw) == 2 and sum(t["minutes"] for t in rw) == 30
    assert all(t["subject"] == "rw" for t in rw)
    assert "Standard English Conventions" in rw[0]["title"]
    bad = {**cfg, "sections": {**cfg["sections"], "rw": {**cfg["sections"]["rw"],
                                                    "focus": {d: "focus" for d in plan.RW_DOMAINS[:3]}}}}
    call(client, "POST", "/api/plan", bad, learner, 422)
    call(client, "POST", f"/api/plan/{pid}/rwlog", {"day": plan.today().isoformat(),
         "rows": [{"domain": "Craft and Structure", "missed": 3, "of": 13}]}, learner)
    domains = call(client, "GET", "/api/plan/progress", learner=learner)["rw_domains"]
    assert next(d for d in domains if d["domain"] == "Craft and Structure")["missed"] == 3
    call(client, "PATCH", f"/api/plan/{pid}", {"rw_focus": {"Craft and Structure": "focus"}}, learner)
    assert prefs.get(learner)["words_goal"] == 15
    call(client, "POST", f"/api/plan/{pid}/archive", {}, learner)
    assert call(client, "GET", "/api/plan", learner=learner)["active"] is None
    call(client, "POST", f"/api/plan/{pid}/activate", {}, learner)
    assert call(client, "GET", "/api/me", learner=learner)["profile"]["exam_date"] == exam.isoformat()
    duplicated = call(client, "POST", f"/api/plan/{pid}/duplicate", {}, learner)
    assert duplicated["draft"]["fields"]["exam_date"] == exam.isoformat()
    call(client, "DELETE", f"/api/plan/{pid}", learner=learner, status=409)
    call(client, "POST", f"/api/plan/{pid}/archive", {}, learner)
    call(client, "DELETE", f"/api/plan/{pid}", learner=learner)
    measure = token()
    measured = call(client, "POST", "/api/plan", base(exam, current=None, target=600, measure=True,
                                                        tests="none"), measure)
    diagnostic = next(d for d in measured["days"] if d["test"] == "diagnostic")
    first = [t["kind"] for t in diagnostic["tasks"][:2]]
    assert first == ["test", "map"] and diagnostic["tasks"][0]["start"]["path"] == "/api/session"
    print("ok  R&W score/time/evidence, Words focus, lifecycle and diagnostic measure path")


def check_focus_proof(client: TestClient, exam: dt.date) -> None:
    learner = token()
    cfg = base(exam, minutes=90, tests="none", skills={"circles": "focus"})
    made = call(client, "POST", "/api/plan", cfg, learner)
    deal = next(d for d in made["days"] if d["kind"] == "practice" and
                any("circles" in t["topics"] for t in d["tasks"] if t["kind"] in ("focus", "map")))
    week = dt.date.fromisoformat(deal["date"]) - dt.timedelta(days=dt.date.fromisoformat(deal["date"]).weekday())
    first = next(d for d in made["days"] if week.isoformat() <= d["date"] <=
                 (week + dt.timedelta(days=6)).isoformat() and
                 any("circles" in t["topics"] for t in d["tasks"] if t["kind"] in ("focus", "map")))
    assert any(t["kind"] == "check" and t["topics"] == ["circles"] and
               t["start"]["body"]["count"] == 4 for t in first["tasks"]), first["tasks"]
    focus_task = next(t for t in first["tasks"] if t["kind"] in ("focus", "map") and
                      "circles" in t["topics"])
    follow = next(d for d in made["days"] if d["date"] > first["date"] and d["kind"] == "practice" and
                  any(t["kind"] in ("focus", "map") and "circles" in t["topics"] for t in d["tasks"]))
    call(client, "PATCH", f"/api/plan/{made['active']['id']}/tasks/{focus_task['id']}",
         {"day": first["date"], "status": "skipped", "reason": "too_hard"}, learner)
    reordered = call(client, "GET", f"/api/plan/day/{follow['date']}", learner=learner)["tasks"]
    learn_index = next((i for i, t in enumerate(reordered) if t["kind"] == "learn" and "circles" in t["topics"]), None)
    focus_index = next((i for i, t in enumerate(reordered) if t["kind"] in ("focus", "map") and "circles" in t["topics"]), None)
    assert learn_index is not None and focus_index is not None and learn_index < focus_index, (first["date"], follow["date"], reordered)
    for n in range(12):
        db.run("INSERT INTO attempts(learner,template,seed,topic,difficulty,fmt,correct,at)"
               " VALUES (?,?,?,?,?,?,?,?)", learner, "geo.circle_area", n, "circles", "medium", "mcq",
               1, f"{plan.today()}T12:00:00+00:00")
    updated = call(client, "GET", "/api/plan", learner=learner)
    assert updated["active"]["cfg"]["skills"]["circles"]["state"] == "strong"
    assert updated["active"]["cfg"]["skills"]["circles"]["by"] == "auto"
    assert any("passed" in e["text"] for e in updated["changes"]["today"])
    assert any(isinstance(s, dict) and s.get("state") == "focus" and s.get("by") == "auto"
               for s in updated["active"]["cfg"]["skills"].values())
    keep = plan.pin_schedule(learner, updated["active"]["cfg"], plan.today(), exam,
                             updated["active"]["id"])
    assert any(p.get("why") == "keep" and p["topic"] == "circles" and p["count"] == 2
               for pins in keep.values() for p in pins)
    db.run("UPDATE attempts SET correct=0 WHERE learner=? AND topic='circles' AND seed<5", learner)
    slipped = call(client, "GET", "/api/plan", learner=learner)
    assert slipped["active"]["cfg"]["skills"]["circles"]["state"] == "normal"
    assert slipped["active"]["cfg"]["skills"]["circles"]["slipping"] is True
    assert any(b["kind"] == "slipping" for b in slipped["banners"])
    pinned = token()
    prefs.put(pinned, {"plan_auto_focus": False})
    call(client, "POST", "/api/plan", cfg, pinned)
    for n in range(12):
        db.run("INSERT INTO attempts(learner,template,seed,topic,difficulty,fmt,correct,at)"
               " VALUES (?,?,?,?,?,?,?,?)", pinned, "geo.circle_area", n, "circles", "medium", "mcq",
               1, f"{plan.today()}T12:00:00+00:00")
    waiting = call(client, "GET", "/api/plan", learner=pinned)
    assert waiting["active"]["cfg"]["skills"]["circles"] == "focus"
    assert any(b["kind"] == "graduated" for b in waiting["banners"])
    print("ok  before check, 12-answer proof, auto focus and ask-first preference")


def check_checkpoints_and_verdicts(client: TestClient, exam: dt.date) -> None:
    learner = token()
    made = call(client, "POST", "/api/plan", base(exam, current=560, target=700), learner)
    tests = [d for d in made["days"] if d["kind"] == "test" and
             not any(t.get("rehearsal") for t in d["tasks"])]
    assert len(tests) >= 3
    questions = [{"id": f"base-{n}", "key": f"synthetic.{n}", "type": "mcq", "answer": "A",
                  "difficulty": "medium", "topic_name": "Circles"} for n in range(22)]
    copy = [{**q, "id": f"twin-{n}"} for n, q in enumerate(questions)]
    stamp = plan.today().isoformat()
    base_answers = {q["id"]: 0 for q in questions[:11]}
    twin_answers = {q["id"]: 0 for q in copy[:16]}
    db.run("INSERT INTO sessions(id,kind,learner,started,finished,questions,answers,result,cfg)"
           " VALUES (?,?,?,?,?,?,?,?,?)", "s7-base-" + learner, "module", learner,
           stamp + "T09:00:00+00:00", stamp + "T10:00:00+00:00",
           json.dumps({"module1": questions}), json.dumps(base_answers),
           json.dumps({"estimate": {"low": 470, "high": 610}}), "{}")
    baseline = "s7-base-" + learner
    updated = call(client, "GET", "/api/plan", learner=learner)
    first = next(t for t in next(d for d in updated["days"] if d["date"] == tests[0]["date"])["tasks"]
                 if t["kind"] == "test")
    second = next(t for t in next(d for d in updated["days"] if d["date"] == tests[1]["date"])["tasks"]
                  if t["kind"] == "test")
    third = next(t for t in next(d for d in updated["days"] if d["date"] == tests[2]["date"])["tasks"]
                 if t["kind"] == "test")
    assert "twin_of" not in first["start"]["body"] and "twin_of" not in third["start"]["body"]
    assert second["start"]["body"]["kind"] == "twin"
    assert second["start"]["body"]["twin_of"] == baseline
    db.run("INSERT INTO sessions(id,kind,learner,started,finished,questions,answers,result,cfg)"
           " VALUES (?,?,?,?,?,?,?,?,?)", "s7-twin-" + learner, "module", learner,
           stamp + "T12:00:00+00:00", stamp + "T13:00:00+00:00",
           json.dumps({"module1": copy}), json.dumps(twin_answers),
           json.dumps({"estimate": {"low": 560, "high": 700}}), json.dumps({"twin_of": baseline}))
    db.run("INSERT INTO attempts(learner,session,template,seed,topic,difficulty,fmt,correct,at)"
           " VALUES (?,?,?,?,?,?,?,?,?)", learner, "other", "synthetic.0", 5, "circles",
           "medium", "mcq", 1, stamp + "T11:00:00+00:00")
    cp = call(client, "GET", "/api/plan/progress", learner=learner)["checkpoints"][0]
    assert cp["subject"] == "math" and len(cp["slots"]) == 22
    assert sum(cp["counts"].values()) == 22 and cp["slots"][0]["practised"] is True
    assert {s["change"] for s in cp["slots"]} <= {"fixed", "held", "slipped", "still_missed"}
    assert cp["fix"]["only"] == [s["qid"] for s in cp["slots"]
                                  if s["change"] in ("slipped", "still_missed")]
    assert cp["fix"]["sibling"] is True
    assert [plan._test_band({"aim": 620}, {"result": json.dumps({"estimate": b})})["verdict"]
            for b in ({"low": 630, "high": 770}, {"low": 580, "high": 720},
                      {"low": 470, "high": 610})] == ["beat", "within", "under"]
    print("ok  twin rhythm, 22-slot comparison, practice marks, fix body and score-band verdict")


def check_progress_and_records(client: TestClient, exam: dt.date) -> None:
    learner = token()
    made = call(client, "POST", "/api/plan", base(exam, tests="none"), learner)
    pid = made["active"]["id"]
    stamp = plan.today().isoformat()
    yesterday = (plan.today() - dt.timedelta(days=1)).isoformat()
    for index in range(40):
        before = index < 20
        db.run("INSERT INTO attempts(learner,template,seed,topic,difficulty,fmt,correct,ms,conf,at)"
               " VALUES (?,?,?,?,?,?,?,?,?,?)", learner, "synthetic.circles", index, "circles", "medium",
               "mcq", int(index % 20 < (10 if before else 11)), 210000, "sure" if index % 2 else "guess",
               (yesterday if before else stamp) + "T12:00:00+00:00")
    progress_data = call(client, "GET", "/api/plan/progress", learner=learner)
    bought = next(x for x in progress_data["bought"] if x["topic"] == "circles")
    assert bought["before"] == {"right": 10, "of": 20}
    assert bought["after"] == {"right": 11, "of": 20} and bought["not_moving"]
    assert bought["minutes_14d"] >= 70 and len(progress_data["split_domain"]) == 4
    assert progress_data["calibration"]["sure"]["of"] == 10
    assert progress_data["causes"]["total"] == sum(progress_data["causes"]["by"].values())
    db.run("UPDATE attempts SET correct=1 WHERE learner=? AND seed IN (31,32)", learner)
    changed = call(client, "GET", "/api/plan/progress", learner=learner)
    assert not next(x for x in changed["bought"] if x["topic"] == "circles")["not_moving"]
    assert len(changed["skills"]) == 19 and len(changed["domains"]) == 4
    call(client, "PUT", "/api/me", {"prefs": {"registered": exam.isoformat()}}, learner)
    registered = call(client, "GET", "/api/plan", learner=learner)
    assert registered["active"]["cfg"]["booked"] is True
    assert not any(b["kind"] == "registration" for b in registered["banners"])
    future_monday = plan.today() + dt.timedelta(days=(7 - plan.today().weekday()) % 7 or 7)
    week = call(client, "PUT", f"/api/plan/{pid}/week/{future_monday}",
                {"days": [{"date": future_monday.isoformat(), "minutes": 15}]}, learner)
    assert week["days"][0]["minutes"] == 15
    assert db.one("SELECT COUNT(*) AS n FROM plan_snapshots WHERE plan=?", pid)["n"] >= 1
    existing = db.one("SELECT days FROM plan_snapshots WHERE plan=? AND made_on=?", pid, stamp)
    db.run("DELETE FROM plan_snapshots WHERE plan=? AND made_on=?", pid, stamp)
    db.run("INSERT INTO plan_snapshots(plan,made_on,days) VALUES (?,?,?)", pid, yesterday, existing["days"])
    db.run("INSERT INTO traps(learner,template,norm,reason,label,topic,owed,opened,last)"
           " VALUES (?,?,?,?,?,?,?,?,?)", learner, "synthetic.trap", "wrong method", "wrong method", "Wrong method",
           "circles", 2, stamp + "T11:00:00+00:00", stamp + "T11:00:00+00:00")
    changed_plan = call(client, "GET", "/api/plan", learner=learner)
    assert any(e["cause"] == "mistake" and "Wrong method" in e["text"]
               for e in changed_plan["changes"]["today"])
    assert db.one("SELECT COUNT(*) AS n FROM plan_snapshots WHERE plan=? AND made_on=?", pid, stamp)["n"] == 1
    call(client, "GET", "/api/plan", learner=learner)
    assert db.one("SELECT COUNT(*) AS n FROM plan_snapshots WHERE plan=? AND made_on=?", pid, stamp)["n"] == 1
    call(client, "POST", f"/api/plan/{pid}/archive", {}, learner)
    record = call(client, "GET", "/api/plan", learner=learner)["plans"][0]["record"]
    assert len(record["by_dow"]) == 7 and all(0 <= v <= 100 for v in record["by_dow"])
    duplicated = call(client, "POST", f"/api/plan/{pid}/duplicate", {}, learner)["draft"]["fields"]
    assert duplicated["day_minutes"][1] == 15
    print("ok  progress evidence, registration, week shaping, snapshots and plan record")


def check_me_mirror(client: TestClient) -> None:
    learner = token()
    exam = next_saturday(plan.today(), 7)
    made = call(client, "POST", "/api/plan", base(exam, tests="none"), learner)
    later = (exam + dt.timedelta(days=7)).isoformat()
    call(client, "PUT", "/api/me", {"target": 720, "minutes": 60, "exam_date": later}, learner)
    cfg = call(client, "GET", "/api/plan", learner=learner)["active"]["cfg"]
    assert cfg["target"] == 720 and cfg["minutes"] == 60 and cfg["exam_date"] == later
    assert made["active"]["id"] == plan.active_row(learner)["id"]
    print("ok  Me goal edits mirror into the active plan")


def check(client: TestClient) -> None:
    plan._selfcheck()
    exam = next_saturday(plan.today())
    learner, cfg = check_empty_preview_and_validation(client, exam)
    payload = check_create_schedule(client, learner, cfg, exam)
    check_allocation_and_time(learner, cfg, payload)
    check_tasks_days(client, learner, payload)
    check_freeze_and_links(client, learner, payload)
    check_rw_measure_lifecycle(client, exam)
    check_focus_proof(client, exam)
    check_checkpoints_and_verdicts(client, exam)
    check_progress_and_records(client, exam)
    check_me_mirror(client)
    print("S7 plan checks passed")


def main() -> None:
    with TestClient(app) as client:
        check(client)


if __name__ == "__main__":
    main()
