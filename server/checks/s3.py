"""S3 Today server acceptance: spec/rebuild-v2.md §3.2.8 as amended by §2.13 and
spec/v2-upgrades/today.md (T1-T20), plus SEC-02. test_flow runs check(c); alone:

    PYTHONPATH=. python3 server/checks/s3.py

Items that belong to another owner's endpoint (S6's /api/history modules, F2's
next.preview) are checked when that part has landed and skipped quietly before.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import importlib
import itertools
import json
import os
import re
import secrets
import tempfile
from unittest.mock import patch

if __name__ == "__main__":
    os.environ["SATF_DB"] = tempfile.mktemp(prefix="satf-s3-check-", suffix=".db")

from fastapi.testclient import TestClient

from server import api_today, daily, db, deps, drill, estimate, practice, progress, satdates
from server.app import app

LEAKS = ("answer", "answer_index", "rationale", "reasons", "traps", "key", "seed", "word")
OLD = "2020-01-01T00:00:00+00:00"
SEEDS = itertools.count(5000)          # every answer a pair never met before


def code() -> str:
    return "a:v2revtoday" + secrets.token_hex(6)


def call(c: TestClient, method: str, path: str, learner: str | None = None, body=None, tz: int = 0,
         status: int = 200):
    headers = {"X-Tz": str(tz)}
    if learner:
        headers["X-Learner"] = learner
    r = c.request(method, path, headers=headers, json=body)
    assert r.status_code == status, (method, path, status, r.status_code, r.text[:400])
    return r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text


def today(tz: int = 0) -> dt.date:
    return dt.date.fromisoformat(daily.today(tz))


def tz_at(minute_of_day: int) -> int:
    """An X-Tz whose local clock reads minute_of_day now (the range covers 26 h)."""
    utc = dt.datetime.now(dt.timezone.utc)
    tz = (utc.hour * 60 + utc.minute - minute_of_day) % 1440
    return tz if tz <= 720 else tz - 1440


def establish(learner: str) -> None:
    """SEC-02: a code counts in the crowd once it existed before the day."""
    db.run("UPDATE learners SET created=? WHERE id=?", OLD, learner)


def question(template: str, seed: int) -> dict:
    item = practice.generate(template, seed)
    return practice.to_question(practice.Card.of(template, seed, item, practice.topic_of(template)), 1)


def named_miss(learner: str, template: str, when: str | None = None) -> dict | None:
    """File a named multiple-choice miss on this template; the trap it opened."""
    for seed in range(300):
        try:
            q = question(template, seed)
        except Exception:
            continue
        if q["type"] != "mcq" or not progress.offered_of(q):
            continue
        right = "ABCD".index(q["answer"])
        wrong = next((i for i, r in enumerate(q.get("reasons") or []) if r and i != right), None)
        if wrong is None:
            continue
        progress.record(learner, None, q, wrong, 30000, when=when)
        got = [t for t in progress.open_traps(learner) if t["template"] == template]
        if got:
            return got[0]
    return None


def answers(learner: str, n: int, right: bool = True, ms: int = 40000, topic: str | None = None,
            when: str | None = None) -> None:
    """n counted answers on fresh (template, seed) pairs, all right or all wrong."""
    names = sorted(x for t, v in practice.catalogue()["by_topic"].items() if topic in (None, t) for x in v)
    done = 0
    while done < n:
        seed = next(SEEDS)
        template = names[seed * 7 % len(names)]
        try:
            q = question(template, seed)
        except Exception:
            continue
        given = ("ABCD".index(q["answer"]) if right else ("ABCD".index(q["answer"]) + 1) % 4) \
            if q["type"] == "mcq" else (q["answer"] if right else "-99999")
        progress.record(learner, None, q, given, ms, when=when)
        done += 1


def answer_drill(c: TestClient, sid: str, learner: str, limit: int = 30, right: bool = True) -> list[dict]:
    """Answer a drill all right (or all wrong) until done; the questions it served."""
    for _ in range(limit):
        q = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", sid)["questions"])[-1]
        given = "ABCD".index(q["answer"]) if q["type"] == "mcq" else q["answer"]
        if not right:
            given = (given + 1) % 4 if q["type"] == "mcq" else "-99999"
        call(c, "POST", f"/api/drill/{sid}/answer", learner, {"question_id": q["id"], "answer": given})
        if call(c, "POST", f"/api/drill/{sid}/next", learner).get("done"):
            break
    return json.loads(db.one("SELECT questions FROM sessions WHERE id=?", sid)["questions"])


# ------------------------------------------------------------------ §3.2.8 check 1, T12.6, T2

def fresh(c: TestClient) -> None:
    me = code()
    t = call(c, "GET", "/api/today", me)
    assert all(t["study"][k] == 0 for k in ("today", "week", "month", "active_days_month",
                                            "questions_today", "right_today")), t["study"]
    assert t["days"]["best"] == 0 and t["scores"] == [] and t["outside"] == []
    assert t["open"] == {"drill": None, "drills": 0, "test": None}, t["open"]
    assert t["traps"]["open"] == 0 and t["traps"]["top"] == [] and t["mistakes"] == 0
    assert t["week"]["this"] == {"questions": 0, "right": 0, "minutes": 0, "fixed": 0, "opened": 0}
    kinds = [r["kind"] for r in t["due"]["rows"]]
    assert "qotd" in kinds and "challenge" in kinds, kinds
    qrow = next(r for r in t["due"]["rows"] if r["kind"] == "qotd")
    assert qrow["progress"] == {"have": 0, "of": t["qotd"]["slots"]}
    assert qrow["why"] == [f"The same {t['qotd']['slots']} for everyone, one try each"]
    assert t["due"]["minutes_left"] == sum(r["minutes"] or 0 for r in t["due"]["rows"] if r["status"] != "done")
    assert t["brief"] == [] and t["at_risk"] is None and t["receipt"] is None
    assert t["workload"] is None and t["goal_suggest"] is None           # no exam date
    for k in ("today", "week", "month"):
        assert t["study"][k] == 0
    print("ok  S3 a fresh code's Today is all zeros and empty lists, with the day's questions and challenge due")


# ------------------------------------------------------------------ check 2 / T14.1, 2, 4, 5

def qotd_shape(c: TestClient) -> None:
    a, b = code(), code()
    qa, qb = call(c, "GET", "/api/qotd", a), call(c, "GET", "/api/qotd", b)
    slots = [s["slot"] for s in qa["slots"]]
    rw = [s for s in ("rw:wic", "rw:transition") if daily.item(s, qa["day"]) is not None]
    assert slots == ["math:mcq", "math:spr"] + rw, slots
    assert [s["question"]["stem"] for s in qa["slots"]] == [s["question"]["stem"] for s in qb["slots"]]
    assert qa["slots"][0]["question"]["type"] == "mcq" and qa["slots"][1]["question"]["type"] == "spr"
    for s in qa["slots"]:
        assert not any(k in s["question"] for k in LEAKS), (s["slot"], set(s["question"]) & set(LEAKS))
        assert s["mine"] is None and s["label"] == daily.SLOTS[s["slot"]]["label"]
    assert qa["late"] is False and qa["streak"] == 0 and len(qa["past"]) == 7
    assert all(set(p["marks"]) == set(slots) for p in qa["past"])
    assert call(c, "GET", "/api/qotd")["slots"][0]["question"]["stem"] == qa["slots"][0]["question"]["stem"]
    day = qa["day"]
    # the alias files as math:mcq in v2's session
    first = call(c, "POST", "/api/qotd", a, {"answer": 0, "day": day, "slot": "mcq", "ms": 30000})
    assert first["slot"] == "math:mcq" and first["late"] is False and len(first["choices_explained"]) == 4
    assert first["choices_explained"][first["answer_index"]] is None
    assert db.one("SELECT 1 FROM attempts WHERE learner=? AND session=?", a, f"qotd:{day}")
    again = call(c, "POST", "/api/qotd", a, {"answer": 1, "day": day, "slot": "math:mcq"})
    assert again["already"] and again["given"] == first["given"] == 0
    assert db.one("SELECT COUNT(*) n FROM attempts WHERE learner=? AND session=?", a, f"qotd:{day}")["n"] == 1
    mine = call(c, "GET", "/api/qotd", a)["slots"][0]["mine"]
    assert mine and mine["given"] == 0 and mine["answer"] == first["answer"]
    # the day's seed is never served to this learner again
    kq = daily.question(day, "mcq")
    assert db.one("SELECT 1 FROM practice_seen WHERE learner=? AND template=? AND seed=?", a, kq["key"], kq["seed"])
    # grid-in entry errors, exact equivalence only (T14.4)
    spr = dict(daily.question(day, "spr"), answer="3/2")
    assert daily.feedback("math:spr", day, spr, "1 1/2", False)["entry"]["kind"] == "form"
    assert daily.feedback("math:spr", day, dict(spr, answer="2/3"), ".66", False)["entry"]["kind"] == "early"
    assert daily.feedback("math:spr", day, dict(spr, answer="460"), "455", False)["entry"] is None
    # bad slots and answers
    call(c, "POST", "/api/qotd", a, {"answer": 0, "day": day, "slot": "rw:mcq"}, status=422)
    call(c, "POST", "/api/qotd", a, {"answer": 7, "day": day, "slot": "math:mcq"}, status=422)
    call(c, "POST", "/api/qotd", a, {"answer": "x" * 13, "day": day, "slot": "math:spr"}, status=422)
    call(c, "POST", "/api/qotd", a, {"answer": 0, "day": "2026-9-1"}, status=422)
    # R&W twins are R&W only and need the slot answered
    call(c, "POST", "/api/qotd/another", a, {"day": day, "slot": "math:mcq"}, status=422)
    status = 409 if daily.item("rw:wic", day) is not None and deps.part("api_words", "_sign") else 501
    call(c, "POST", "/api/qotd/another", a, {"day": day, "slot": "rw:wic"}, status=status)
    print("ok  S3 the day's questions: same stems for everyone, no key before answering, one answer a slot, entry errors named")


# ------------------------------------------------------------------ check 3, T14.5, SEC-02

def qotd_answer_and_crowd(c: TestClient) -> None:
    me = code()
    day = call(c, "GET", "/api/qotd", me)["day"]
    got = call(c, "POST", "/api/qotd", me, {"answer": "999", "day": day, "slot": "spr", "ms": 40000})
    assert got["correct"] is False and got["answer"] and got["crowd"]["answered"] >= 1, got
    assert got["accepted"] and got["sat_pace_ms"] == 95_000
    again = call(c, "POST", "/api/qotd", me, {"answer": "999", "day": day, "slot": "spr", "ms": 40000})
    assert again["given"] == got["given"] == "999" and again["already"]
    t = call(c, "GET", "/api/today", me)
    assert t["study"]["today"] >= 1 and t["qotd"]["answered"] == 1
    assert call(c, "GET", "/api/me", me)["days"]["streak"] == t["days"]["streak"] == 1
    assert call(c, "GET", "/api/qotd", me)["streak"] == 1

    # SEC-02: a code minted today reads the key; its answer never moves the crowd others read
    viewer = code()
    call(c, "POST", "/api/qotd", viewer, {"answer": "1", "day": day, "slot": "spr", "ms": 20000})
    establish(viewer)
    before = daily.crowd("math:spr", day, viewer)["answered"]
    burner = code()
    leaked = call(c, "POST", "/api/qotd", burner, {"answer": "0", "day": day, "slot": "spr"})
    assert leaked["crowd"]["answered"] == before + 1, "the asker always sees their own answer"
    copier = code()
    call(c, "POST", "/api/qotd", copier, {"answer": leaked["answer"], "day": day, "slot": "spr"})
    assert daily.crowd("math:spr", day, viewer)["answered"] == before
    assert call(c, "GET", "/api/qotd", viewer)["slots"][1]["mine"]["crowd"]["answered"] == before

    # T14.5: five established on-time answers give a median time
    for i in range(5):
        x = code()
        call(c, "POST", "/api/qotd", x, {"answer": str(10 + i), "day": day, "slot": "spr", "ms": 30000 + i})
        establish(x)
    crowd = call(c, "GET", "/api/qotd", viewer)["slots"][1]["mine"]["crowd"]
    assert isinstance(crowd["median_ms"], int) and crowd["answered"] >= 5, crowd
    assert crowd["top_wrong"] and all(set(w) == {"value", "n"} for w in crowd["top_wrong"])
    print("ok  S3 an answer returns the key and crowd once; a code minted today never moves the crowd (SEC-02)")


# ------------------------------------------------------------------ checks 4, 5, grace

def late_and_grace(c: TestClient) -> None:
    me = code()
    t = today()
    back3 = (t - dt.timedelta(days=3)).isoformat()
    crowd_before = daily.crowd("math:mcq", back3)["answered"]
    late = call(c, "POST", "/api/qotd", me, {"answer": 0, "day": back3, "slot": "mcq"})
    assert late["late"] is True
    assert db.one("SELECT 1 FROM attempts WHERE learner=? AND session=?", me, f"qotd-late:math:mcq:{back3}")
    past = call(c, "GET", f"/api/qotd?day={back3}", me)
    assert past["late"] is True and past["slots"][0]["mine"]["late"] is True
    assert daily.crowd("math:mcq", back3)["answered"] == crowd_before
    assert past["streak"] == 0 and daily.qotd_streak(me)["current"] == 0
    assert next(p for p in past["past"] if p["day"] == back3)["marks"]["math:mcq"] in ("right", "wrong")
    call(c, "POST", "/api/qotd", me, {"answer": 0, "day": (t + dt.timedelta(days=1)).isoformat()}, status=422)
    call(c, "GET", f"/api/qotd?day={(t - dt.timedelta(days=40)).isoformat()}", me, status=422)
    call(c, "GET", f"/api/qotd?day={(t + dt.timedelta(days=1)).isoformat()}", me, status=422)
    call(c, "POST", "/api/qotd", me, {"answer": 0, "day": (t - dt.timedelta(days=31)).isoformat()}, status=409)

    # 00:30 local: yesterday's answer is on time, in the crowd and the streak
    tz = tz_at(30)
    local = today(tz)
    yday = (local - dt.timedelta(days=1)).isoformat()
    graced = code()
    n0 = daily.crowd("math:spr", yday)["answered"]
    g = call(c, "POST", "/api/qotd", graced, {"answer": "7", "day": yday, "slot": "spr"}, tz=tz)
    assert g["late"] is False and g["day"] == yday, g
    establish(graced)
    assert daily.crowd("math:spr", yday)["answered"] == n0 + 1
    assert call(c, "GET", "/api/qotd", graced, tz=tz)["streak"] == 1
    # 01:30 local: the same answer is late, and changes neither
    tz = tz_at(90)
    yday = (today(tz) - dt.timedelta(days=1)).isoformat()
    tardy = code()
    n0 = daily.crowd("math:spr", yday)["answered"]
    g = call(c, "POST", "/api/qotd", tardy, {"answer": "7", "day": yday, "slot": "spr"}, tz=tz)
    establish(tardy)
    assert g["late"] is True and daily.crowd("math:spr", yday)["answered"] == n0
    assert call(c, "GET", "/api/qotd", tardy, tz=tz)["streak"] == 0
    print("ok  S3 late answers file late; tomorrow and 40 days back are 422; the hour after midnight is graced")


# ------------------------------------------------------------------ check 6, T5.1

def like_drill(c: TestClient) -> None:
    me = code()
    day = daily.today(0)
    call(c, "POST", "/api/drill", me, {"like": {"day": day, "slot": "mcq"}, "count": 5}, status=409)
    call(c, "POST", "/api/drill", me, {"like": {"day": "2020-01-01", "slot": "mcq"}}, status=404)
    kq = daily.question(day, "mcq")
    call(c, "POST", "/api/qotd", me, {"answer": ("ABCD".index(kq["answer"]) + 1) % 4, "day": day})
    call(c, "POST", "/api/drill", me, {"like": {"day": day, "slot": "mcq"}, "count": 21}, status=422)
    d = call(c, "POST", "/api/drill", me, {"like": {"day": day, "slot": "mcq"}, "count": 5})
    served = answer_drill(c, d["id"], me)
    assert len(served) == 5 and all(q["key"] == kq["key"] for q in served), [q["key"] for q in served]
    assert all(q["seed"] != kq["seed"] for q in served)
    twin = call(c, "POST", "/api/drill", me, {"like": {"day": day, "slot": "mcq"}, "count": 1, "source": "twin"})
    row = db.one("SELECT cfg, questions FROM sessions WHERE id=?", twin["id"])
    assert json.loads(row["cfg"])["inline"] is True
    q1 = json.loads(row["questions"])[0]
    assert q1["key"] == kq["key"] and q1["seed"] != kq["seed"]
    assert twin["id"] not in {s["id"] for s in call(c, "GET", "/api/history", me)["sessions"]}
    # the grid-in slot's twins stay grid-ins
    sq = daily.question(day, "spr")
    call(c, "POST", "/api/qotd", me, {"answer": "-99999", "day": day, "slot": "spr"})
    g = call(c, "POST", "/api/drill", me, {"like": {"day": day, "slot": "spr"}, "count": 1, "source": "twin"})
    gq = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", g["id"])["questions"])[0]
    assert gq["key"] == sq["key"] and gq["type"] == "spr" and gq["seed"] != sq["seed"]
    print("ok  S3 'like' drills wait for the answer, then serve the day's template on new seeds only")


# ------------------------------------------------------------------ check 7

def templates_drill(c: TestClient) -> None:
    me = code()
    for topic, names in sorted(practice.catalogue()["by_topic"].items()):
        traps = [x for x in (named_miss(me, n) for n in names[:6]) if x]
        if len({x["template"] for x in traps}) >= 2:
            break
    t1, t2 = traps[0]["template"], traps[1]["template"]
    d = call(c, "POST", "/api/drill", me, {"mistakes": True, "templates": [t1]})
    assert d["total"] == 2, d["total"]
    served = answer_drill(c, d["id"], me)
    assert [q["key"] for q in served] == [t1, t1] and t2 not in {q["key"] for q in served}
    one = call(c, "POST", "/api/drill", me, {"mistakes": True, "templates": [t2], "count": 1, "source": "try"})
    assert one["total"] == 1
    print("ok  S3 a mistakes drill on one template serves only that template, twice")


# ------------------------------------------------------------------ check 8 (and 9 when S6 lands), open.test

def module_minutes(c: TestClient) -> None:
    me = code()
    m = call(c, "POST", "/api/mock/new", me, {"full": False})
    sid = m["id"]
    began = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=20)).isoformat(timespec="seconds")
    db.run("UPDATE sessions SET started=?, module_started=? WHERE id=?", began, began, sid)
    q = m["questions"][0]
    call(c, "POST", f"/api/session/{sid}/answer", me, {"question_id": q["id"], "answer": 0})
    t = call(c, "GET", "/api/today", me)
    assert t["open"]["test"]["id"] == sid and t["open"]["test"]["answered"] == 1
    assert 13 * 60 <= t["open"]["test"]["seconds_left"] <= 15 * 60 + 5, t["open"]["test"]
    assert t["due"]["rows"][0]["kind"] == "test", "a running test leads the Due list"
    call(c, "POST", f"/api/session/{sid}/finish", me)
    t = call(c, "GET", "/api/today", me)
    assert 20 <= t["study"]["today"] <= 37, t["study"]
    assert t["open"]["test"] is None and t["days"]["streak"] == 1 and t["tested"] is True
    cal = call(c, "GET", f"/api/calendar?month={today().isoformat()[:7]}", me)
    row = next(d for d in cal["days"] if d["day"] == today().isoformat())
    assert sid in {s["id"] for s in row["sittings"]} and row["tests"] == 1
    results = call(c, "GET", f"/api/session/{sid}/results", me)
    hist = call(c, "GET", "/api/history?kind=tests&all=1&limit=6", me).get("sessions", [])
    mine = next((h for h in hist if h["id"] == sid), None)
    if mine and "modules" in mine:                  # S6 (R26): the same misses as the report
        wrong = sorted(i + 1 for i, r in enumerate(results["review"]) if not r.get("correct"))
        got = sorted(mine["modules"][0].get("missed", []) + mine["modules"][0].get("blank", []))
        assert got == wrong, (got, wrong)
    print("ok  S3 a module's clock is on Today while it runs; finished, its minutes and sitting are on the day")


# ------------------------------------------------------------------ check 10 (R38)

def diagnostic_gate(c: TestClient) -> None:
    me = code()
    s = call(c, "POST", "/api/session", me)
    call(c, "POST", f"/api/session/{s['id']}/answer", me, {"question_id": s["questions"][0]["id"], "answer": 0})
    call(c, "POST", f"/api/session/{s['id']}/finish", me)
    t = call(c, "GET", "/api/today", me)
    assert all(x["session"] != s["id"] for x in t["scores"]) and t["score"] is None
    assert api_today.latest_score(me) is None
    call(c, "POST", "/api/drill", me, {"from_session": s["id"]}, status=403)
    cal = call(c, "GET", f"/api/calendar?month={today().isoformat()[:7]}", me)
    sit = next(x for d in cal["days"] for x in d["sittings"] if x["id"] == s["id"])
    assert sit["gated"] is True and sit["estimate"] is None and sit["right"] is None
    print("ok  S3 an un-signed-up diagnostic gives no score, no Fix and a gated calendar row")


# ------------------------------------------------------------------ check 11, T3.4, T17 day rows

def calendar(c: TestClient) -> None:
    me = code()
    call(c, "GET", "/api/calendar?month=2026-13", me, status=422)
    call(c, "GET", "/api/calendar?month=2019-12", me, status=422)
    call(c, "GET", "/api/calendar?month=26-09", me, status=422)
    far = today() + dt.timedelta(days=400)
    call(c, "GET", f"/api/calendar?month={far.isoformat()[:7]}", me, status=422)
    sep = call(c, "GET", "/api/calendar?month=2026-09", me)
    assert len(sep["days"]) == 30 and sep["days"][0]["day"] == "2026-09-01" and sep["days"][-1]["day"] == "2026-09-30"
    year = today().year + (today().month > 2)
    feb = call(c, "GET", f"/api/calendar?month={year}-02", me)
    assert len(feb["days"]) == (29 if year % 4 == 0 and (year % 100 or year % 400 == 0) else 28)
    # a day of practice: minutes, questions, misses and topics
    trap = named_miss(me, "lin.evaluate") or named_miss(me, "pct.change")
    answers(me, 3)
    t = today().isoformat()
    cal = call(c, "GET", f"/api/calendar?month={t[:7]}", me)
    row = next(d for d in cal["days"] if d["day"] == t)
    assert row["questions"] == 4 and row["right"] == 3 and len(row["missed"]) == 1
    assert {o["id"] for o in row["opened"]} == {trap["id"]} and sum(x["asked"] for x in row["topics"]) == 4
    assert row["first_at"] and row["last_at"] and set(row["qotd"]) == set(daily.shown(t))
    assert cal["totals"]["questions"] == 4 and cal["first_active"] == t and cal["today"] == t
    # T3.4: a check-in due in two days is on that future cell
    due = today() + dt.timedelta(days=2)
    db.run("UPDATE traps SET closed=?, closed_how='fixed', due=?, checks=0, owed=0 WHERE id=?",
           progress.now(), due.isoformat(), trap["id"])
    cal = call(c, "GET", f"/api/calendar?month={due.isoformat()[:7]}", me)
    cell = next(d for d in cal["days"] if d["day"] == due.isoformat())
    assert cell["due"]["checks"] == 1, cell["due"]
    assert all(d["due"] is None for d in cal["days"] if d["day"] <= t)
    print("ok  S3 the calendar: every day of the month, day rows with misses and topics, check-ins on future days")


# ------------------------------------------------------------------ check 12 (PUT /api/me, F4's route)

def profile_fields(c: TestClient) -> None:
    me = code()
    call(c, "PUT", "/api/me", me, {"exam_date": "2020-01-01"}, status=422)
    exam = (today() + dt.timedelta(days=40)).isoformat()
    call(c, "PUT", "/api/me", me, {"exam_date": exam, "minutes": 60, "days": "1111100"})
    call(c, "PUT", "/api/me", me, {"rw_now": 610, "rw_target": 700})
    p = call(c, "GET", "/api/me", me)["profile"]
    assert p["exam_date"] == exam and p["minutes"] == 60 and p["rw_now"] == 610 and p["rw_target"] == 700
    assert not p.get("plan_started")
    call(c, "PUT", "/api/me", me, {"rw_now": 615}, status=422)
    t = call(c, "GET", "/api/today", me)
    assert t["exam"]["date"] == exam and t["exam"]["days"] == 40 and t["study"]["goal"] == 60
    assert t["study"]["week_goal"] == 300
    print("ok  S3 exam date today or later, a goal without a plan, and R&W now and target on the profile")


# ------------------------------------------------------------------ check 13 (/api/scores, S3's)

def outside_scores(c: TestClient) -> None:
    me, other = code(), code()
    t = today().isoformat()
    s = call(c, "POST", "/api/scores", me, {"day": t, "math": 610, "rw": 600, "source": "bluebook"}, status=201)
    assert s["id"] and s["math"] == 610 and "learner" not in s
    listed = call(c, "GET", "/api/scores", me)["scores"]
    assert [x["id"] for x in listed] == [s["id"]]
    assert call(c, "GET", "/api/today", me)["outside"][0]["id"] == s["id"]
    for bad in ({"day": t, "math": 615}, {"day": t, "math": 900}, {"day": t, "math": 600, "rw": 190},
                {"day": (today() + dt.timedelta(days=1)).isoformat(), "math": 600},
                {"day": "2019-12-31", "math": 600}, {"day": "yesterday", "math": 600},
                {"day": t, "math": 600, "source": "khan"}, {"day": t, "math": "600"},
                {"day": t, "math": 600, "learner": other}):
        call(c, "POST", "/api/scores", me, bad, status=422)
    call(c, "DELETE", f"/api/scores/{s['id']}", other, status=404)
    call(c, "DELETE", f"/api/scores/{s['id']}", me)
    assert call(c, "GET", "/api/scores", me)["scores"] == []
    call(c, "DELETE", f"/api/scores/{s['id']}", me, status=404)
    # an official score lands on the day and in carry
    kept = call(c, "POST", "/api/scores", other, {"day": t, "math": 700, "source": "official"}, status=201)
    progress.carry(other, me)
    assert [x["id"] for x in call(c, "GET", "/api/scores", me)["scores"]] == [kept["id"]]
    print("ok  S3 added scores: validated, listed newest first, deleted only by their owner, carried with the code")


# ------------------------------------------------------------------ check 14 as amended (R14), T2.1, 2, 7

def plan_edits(c: TestClient) -> None:
    if not deps.part("plan", "today_summary"):
        return
    me = code()
    t = today()
    exam = t + dt.timedelta(days=49 + (5 - t.weekday()) % 7)
    call(c, "POST", "/api/plan", me, {"current": 520, "target": 700, "exam_date": exam.isoformat(),
                                      "minutes": 45, "days": "1111111", "tests": "weekly",
                                      "test_size": "module"})
    today_ = call(c, "GET", "/api/today", me)
    plan = today_["plan"]
    assert plan and plan["start"] == t.isoformat() and plan["exam_date"] == exam.isoformat()
    counted = [x for x in plan["tasks"] if x.get("counted")]
    assert plan["tasks_counted"] == len(counted) and counted
    plan_rows = [r for r in today_["due"]["rows"] if r["key"].startswith("plan:")]
    assert all(r["kind"] not in ("qotd", "challenge") for r in plan_rows)
    assert [r["kind"] for r in today_["due"]["rows"]].count("warmup") <= 1
    task = counted[0]
    path = f"/api/plan/{plan['id']}/tasks/{task['id']}"
    call(c, "PATCH", path, me, {"day": t.isoformat(), "status": "skipped"})
    after = call(c, "GET", "/api/today", me)["plan"]
    assert next(x for x in after["tasks"] if x["id"] == task["id"])["status"] == "skipped"
    call(c, "PATCH", path, me, {"day": t.isoformat(), "status": "todo"})
    after = call(c, "GET", "/api/today", me)["plan"]
    assert next(x for x in after["tasks"] if x["id"] == task["id"])["status"] == task["status"]
    r = c.patch(path, headers={"X-Learner": me, "X-Tz": "0"},
                json={"day": t.isoformat(), "to": (exam + dt.timedelta(days=1)).isoformat()})
    assert r.status_code == 422, r.text
    hero = call(c, "GET", "/api/today", me)
    assert hero["next"]["box"]["default"] in api_today.BOX_OPTIONS
    print("ok  S3 Today's plan edits go through S7's PATCH and read back through /api/today.plan")


# ------------------------------------------------------------------ open.drill (§3.2.5 test_flow list)

def open_drill(c: TestClient) -> None:
    me = code()
    d = call(c, "POST", "/api/drill", me, {"topics": ["linear_functions"], "count": 5})
    assert call(c, "GET", "/api/today", me)["open"]["drill"] is None, "no answer yet"
    q = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", d["id"])["questions"])[-1]
    call(c, "POST", f"/api/drill/{d['id']}/answer", me,
         {"question_id": q["id"], "answer": "ABCD".index(q["answer"]) if q["type"] == "mcq" else q["answer"]})
    o = call(c, "GET", "/api/today", me)["open"]
    assert o["drill"]["id"] == d["id"] and o["drill"]["answered"] == 1 and o["drills"] == 0
    tried = call(c, "POST", "/api/drill", me, {"topics": ["linear_functions"], "count": 1, "source": "try"})
    q = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", tried["id"])["questions"])[-1]
    call(c, "POST", f"/api/drill/{tried['id']}/answer", me, {"question_id": q["id"], "answer": 0})
    assert call(c, "GET", "/api/today", me)["open"]["drill"]["id"] == d["id"], "a 'try' sheet is never Continue"
    call(c, "POST", f"/api/drill/{d['id']}/finish", me)
    assert call(c, "GET", "/api/today", me)["open"]["drill"] is None
    print("ok  S3 an unfinished set is Continue after one answer and gone once finished; a Try sheet never is")


# ------------------------------------------------------------------ T12.1, 2, 6, 7

def workload(c: TestClient) -> None:
    t = today()
    p = {"exam_date": (t + dt.timedelta(days=10)).isoformat(), "days": "1111100", "minutes": 45,
         "target": None, "tests": "none"}
    d = {"recent": []}
    warm = {"due": 0}
    w = api_today.workload("a:v2revtodaynobody", 0, p, t, d, 10, warm, None, 100)
    assert w["need"]["traps"] == 2000 and w["sized"] is False and w["unsized"] == "answers"
    assert w["fits"] is None and w["short_by"] is None and w["suggest_minutes"] is None
    assert api_today.goal_suggest(w) is None
    fake = {"target": 700, "reachable": True, "right_of_44": 37, "now_of_44": 31,
            "path": {"skills": ["circles"], "minutes": 60, "reachable": True}}
    with patch.object(estimate, "need", return_value=fake):
        w = api_today.workload("a:v2revtodaynobody", 0, {**p, "target": 700}, t, d, 10, warm, {}, 100)
        total = sum(w["need"][k] for k in ("traps", "checks", "tests", "warmups")) + 3600
        assert w["sized"] and w["total"] == total and w["fits"] == (w["capacity"] >= total)
        assert w["need"]["target"]["skills"] == ["circles"]
        tight = api_today.workload("a:v2revtodaynobody", 0, {**p, "target": 700, "minutes": 5}, t, d, 40, warm, {}, 100)
        assert tight["short_by"] > 0 and tight["suggest_minutes"] in api_today.GOAL_CHIPS
        assert api_today.goal_suggest(tight)["minutes"] == tight["suggest_minutes"]
    # T12.7: the suggested goal is null or at least 15 for any need and capacity, a 5-minute need too
    for traps_n, secs, minutes, days in ((1, 150, 5, "1111111"), (0, 95, 240, "1000000"), (3, 30, 15, "1111100"),
                                         (60, 200, 30, "0000011"), (0, 1, 60, None), (500, 300, 90, "1111111")):
        for need_min in (0, 5, 600):
            path = {**fake, "path": {"skills": [], "minutes": need_min, "reachable": True}}
            with patch.object(estimate, "need", return_value=path):
                for exam_in in (2, 3, 10, 120):
                    q = {**p, "exam_date": (t + dt.timedelta(days=exam_in)).isoformat(), "minutes": minutes,
                         "days": days, "target": 700}
                    w = api_today.workload("a:v2revtodaynobody", 0, q, t, d, traps_n, warm, {}, secs)
                    assert w["suggest_minutes"] is None or w["suggest_minutes"] >= 15, (q, w)
    # T12.6 through the route: under 30 answers, then no target
    me = code()
    call(c, "PUT", "/api/me", me, {"exam_date": (t + dt.timedelta(days=30)).isoformat()})
    answers(me, 12)
    got = call(c, "GET", "/api/today", me)
    assert got["workload"]["sized"] is False and got["workload"]["unsized"] == "answers"
    assert got["workload"]["answers"] == {"have": 12, "of": 30} and got["goal_suggest"] is None
    ins = call(c, "GET", "/api/today/insights", me)
    assert ins["gains"] is None and ins["answers"] == 12                               # T6.4
    assert "Geometry and Trigonometry" in ins["estimate"]["thin"]                     # T10.4
    answers(me, 28)
    got = call(c, "GET", "/api/today", me)
    assert got["workload"]["unsized"] == "target" and got["goal_suggest"] is None, (got["workload"], got["goal_suggest"])
    call(c, "PUT", "/api/me", me, {"target": 700})
    got = call(c, "GET", "/api/today", me)
    assert got["workload"]["sized"] is True and got["workload"]["need"]["target"]["target"] == 700
    assert got["goal_suggest"] is None or got["goal_suggest"]["minutes"] >= 15
    ins = call(c, "GET", "/api/today/insights", me)
    assert ins["gains"] is not None and ins["subject"] == "math"
    split = ins["time_split"]
    assert abs(sum(split["domains"].values()) - got["study"]["week"]) <= 1 + 0.05 * got["study"]["week"], split
    print("ok  S3 the workload: sized only with 30 answers and a target, need includes the target, goal at least 15")


# ------------------------------------------------------------------ T19.1, 4

def brief_and_receipt(c: TestClient) -> None:
    t = today()
    y = f"{(t - dt.timedelta(days=1)).isoformat()}T12:00:00+00:00"
    me = code()
    ids = []
    for names in practice.catalogue()["by_topic"].values():
        got = named_miss(me, names[0], when=y) if len(ids) < 3 else None
        if got and got["id"] not in ids:
            ids.append(got["id"])
    for i in ids:
        db.run("UPDATE traps SET closed=?, closed_how='fixed' WHERE id=?", y, i)
    facts = call(c, "GET", "/api/today", me)["brief"]
    line = next(f for f in facts if f["kind"] == "yesterday")
    assert line["text"].startswith("Yesterday") and "3 mistakes fixed" in line["text"], facts
    # the receipt, once the goal is met, claims what practice_delta says for today
    me = code()
    call(c, "PUT", "/api/me", me, {"minutes": 15})
    assert call(c, "GET", "/api/today", me)["receipt"] is None
    answers(me, 2, ms=600000)
    got = call(c, "GET", "/api/today", me)
    r = got["receipt"]
    assert r and r["minutes"] >= 15 and r["questions"] == 2
    midnight = api_today._start(t, 0)
    assert r["claimed"] == estimate.practice_delta(me, midnight)["pts"]
    print("ok  S3 the briefing names yesterday's fixes; the receipt claims practice_delta since midnight")


def final_stretch(c: TestClient) -> None:
    """T13.1-2: exam + 12 is the stretch, and traps fixed 20 days ago are swept from Due."""
    me = code()
    t = today()
    for days, mode in ((12, "stretch"), (6, "taper"), (1, "eve"), (30, None)):
        call(c, "PUT", "/api/me", me, {"exam_date": (t + dt.timedelta(days=days)).isoformat()})
        st = call(c, "GET", "/api/today", me)["next"]["stage"]
        assert st and st["mode"] == mode and st["days"] == days, (days, st)
    names = sorted(x for v in practice.catalogue()["by_topic"].values() for x in v)
    missed = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=25)).isoformat()
    opened = [tr for tr in (named_miss(me, n, missed) for n in names[::7][:12]) if tr][:3]
    assert len(opened) == 3
    closed = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=20)).isoformat()
    for tr in opened:
        db.run("UPDATE traps SET closed=?, closed_how='fixed' WHERE id=?", closed, tr["id"])
    call(c, "PUT", "/api/me", me, {"exam_date": (t + dt.timedelta(days=12)).isoformat()})
    got = call(c, "GET", "/api/today", me)
    assert got["next"]["stage"]["sweep"]["total"] == 3, got["next"]["stage"]
    row = next(r for r in got["due"]["rows"] if r["kind"] == "sweep")
    assert row["start"]["body"]["sweep"] is True and row["start"]["body"]["count"] >= 1
    print("ok  S3 exam in 12 days is the final stretch, and fixed mistakes come back as a sweep row")


# ------------------------------------------------------------------ T2 (R56), T1.1, T1.8

ROW_KEYS = {"key", "kind", "title", "tag", "meta", "minutes", "progress", "due_at", "status", "why", "evidence_href",
            "start", "href", "result", "fix", "alternatives", "task_id", "own", "marked", "group"}


def traps_on(learner: str, n: int, topics=None) -> list[dict]:
    """n open traps on different templates (in `topics` when given)."""
    names = sorted(x for t, v in practice.catalogue()["by_topic"].items() if topics is None or t in topics for x in v)
    got: list[dict] = []
    for name in names[::3] + names[1::3] + names[2::3]:
        if len(got) == n:
            break
        tr = named_miss(learner, name)
        if tr and tr["id"] not in {x["id"] for x in got}:
            got.append(tr)
    assert len(got) == n, (n, topics, len(got))
    return got


def check_ins_due(learner: str, traps: list[dict], day: dt.date) -> None:
    for tr in traps:
        db.run("UPDATE traps SET closed=?, closed_how='fixed', due=?, checks=0, owed=0 WHERE id=?",
               progress.now(), day.isoformat(), tr["id"])


def wrong_named_in_drill(c: TestClient, sid: str, learner: str) -> None:
    """Answer the drill right until an item with a named distractor comes, and pick it."""
    for _ in range(12):
        q = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", sid)["questions"])[-1]
        key = "ABCD".index(q["answer"]) if q["type"] == "mcq" else None
        wrong = next((i for i, r in enumerate(q.get("reasons") or []) if r and i != key), None) if key is not None else None
        call(c, "POST", f"/api/drill/{sid}/answer", learner,
             {"question_id": q["id"], "answer": wrong if wrong is not None else (key if key is not None else q["answer"])})
        if wrong is not None:
            return
        if call(c, "POST", f"/api/drill/{sid}/next", learner).get("done"):
            break
    raise AssertionError("no named distractor came up")


def due_rows(c: TestClient) -> None:
    me = code()
    answers(me, 6)
    before = [db.one(f"SELECT COUNT(*) n FROM {tb} WHERE learner=?", me)["n"] for tb in ("practice_seen", "sessions")]
    t = today()
    check_ins_due(me, traps_on(me, 2), t)
    seen = db.one("SELECT COUNT(*) n FROM practice_seen WHERE learner=?", me)["n"]
    got = call(c, "GET", "/api/today", me)
    again = call(c, "GET", "/api/today", me)
    # T1.1: loading Today marks nothing seen and creates no session
    assert db.one("SELECT COUNT(*) n FROM practice_seen WHERE learner=?", me)["n"] == seen
    assert db.one("SELECT COUNT(*) n FROM sessions WHERE learner=?", me)["n"] == before[1]
    rows = got["due"]["rows"]
    assert all(ROW_KEYS <= set(r) for r in rows), [sorted(ROW_KEYS - set(r)) for r in rows]
    kinds = [r["kind"] for r in rows]
    assert kinds.count("review") == 1 and "warmup" not in kinds, kinds
    review = next(r for r in rows if r["kind"] == "review")
    assert got["warmup"]["checks"] >= 2 and f"{got['warmup']['checks']} check-ins" in review["meta"], review["meta"]
    assert review["start"] == {"path": "/api/drill", "body": {"source": "due", "box": 10}}, review["start"]
    assert got["review"]["start"]["body"] == review["start"]["body"]            # R30: #mist starts the same row
    undone = [r for r in rows if r["status"] not in api_today.FINISHED]
    assert got["due"]["minutes_left"] == sum(r["minutes"] for r in undone)
    assert [r["status"] in api_today.FINISHED for r in rows] == sorted(r["status"] in api_today.FINISHED for r in rows)
    assert again["due"]["rows"] == rows
    d = call(c, "POST", "/api/drill", me, review["start"]["body"])
    served = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", d["id"])["questions"])
    assert served, "the Review row starts a set"
    # T2.4: a set that opened a mistake: its result and the Fix body
    s = call(c, "POST", "/api/drill", me, {"topics": ["linear_functions"], "count": 4})
    wrong_named_in_drill(c, s["id"], me)
    res = api_today.session_result(me, s["id"])
    assert res["opened"] == 1 and res["answered"] >= 1, res
    assert api_today._fix(res)["body"] == {"from_session": s["id"], "still_open": True, "scope": "misses"}
    # T2.5: Words absent, then 12 due (R56's row)
    base = (me, 0, got["profile"], got["open"], None, got["warmup"])
    rest = (got["qotd"], got["challenge"], 95)
    none = api_today.due_fallback(*base, None, *rest)
    assert "words" not in [r["kind"] for r in none["rows"]]
    words = {"due": 12, "preview": {"new": 5}, "minutes": 6, "done": False, "reason": "12 come back today",
             "start": {"path": "/api/words/run", "body": {"mode": "mix", "deck": {"source": "today"}}}}
    w = next(r for r in api_today.due_fallback(*base, words, *rest)["rows"] if r["kind"] == "words")
    assert w["title"] == "Words" and w["meta"].startswith("12 due · 5 new · ~6 min") and w["start"] == words["start"]
    print("ok  S3 Due today: one Review row (R56), the full row shape, minutes left, a set's result and Fix;"
          " loading Today writes nothing")


def goal_met_box(c: TestClient) -> None:
    """T1.8's server half: the goal met, the box defaults to 15."""
    me = code()
    call(c, "PUT", "/api/me", me, {"minutes": 30})
    answers(me, 4, ms=600000)
    got = call(c, "GET", "/api/today", me)
    assert got["study"]["today"] >= 30 and got["next"]["box"]["default"] == 15, (got["study"], got["next"]["box"])
    assert got["next"]["box"]["options"] == [5, 15, 30, 45, 60]
    assert got["next"]["count"]["options"][-1] is None and len(set(got["next"]["count"]["options"][:-1])) == \
        len(got["next"]["count"]["options"][:-1])
    print("ok  S3 the Size row: five time chips, deduplicated counts with Endless, 15 once the goal is met")


# ------------------------------------------------------------------ T13

def stages(c: TestClient) -> None:
    t = today()
    me = code()
    answers(me, 3)
    call(c, "PUT", "/api/me", me, {"exam_date": (t + dt.timedelta(days=1)).isoformat()})
    got = call(c, "GET", "/api/today", me)
    first = got["next"]["items"][0]
    assert got["next"]["stage"]["mode"] == "eve" and first["title"].startswith("Light warm-up"), first
    assert first["then"].startswith("Done for today") and first["start"]["body"]["count"] == 5
    call(c, "POST", first["start"]["path"], me, first["start"]["body"])            # the drill body is valid
    # exam morning, 07:00 local
    tz = tz_at(7 * 60)
    morning = code()
    call(c, "PUT", "/api/me", morning, {"exam_date": today(tz).isoformat()}, tz=tz)
    got = call(c, "GET", "/api/today", morning, tz=tz)
    assert got["next"]["stage"]["mode"] == "exam" and got["next"]["items"][0]["title"].startswith("Warm-up · 5 easy")
    # after the exam: scores come out
    past = (t - dt.timedelta(days=3)).isoformat()
    db.run("UPDATE learners SET exam_date=? WHERE id=?", past, me)
    got = call(c, "GET", "/api/today", me)
    last = got["next"]["items"][-1]
    assert got["next"]["stage"]["mode"] == "after" and last["kind"] == "after"
    assert last["scores_by"] == satdates.entry(past)["scores_by"]
    # T13.3, 8: the rehearsal leads on its Saturday, with no clock time
    items = api_today.queue_fallback(me, t, {"test": None, "drill": None, "drills": 0}, None,
                                     {"mode": "stretch", "days": 10, "rehearsals": [{"day": t.isoformat(), "done": False}]})
    title = items[0]["title"]
    assert title.startswith("Dress rehearsal") and "after R&W and the break" in title and items[0]["time"] is None
    assert not re.search(r"\d:\d\d", title) and items[0]["start"]["body"] == {"kind": "section", "timing": "official"}
    call(c, "PUT", "/api/me", me, {"exam_date": (t + dt.timedelta(days=14)).isoformat()})
    st = call(c, "GET", "/api/today", me)["next"]["stage"]
    exam = t + dt.timedelta(days=14)
    assert 1 <= len(st["rehearsals"]) <= 2 and all(
        dt.date.fromisoformat(r["day"]).weekday() == 5 and (exam - dt.date.fromisoformat(r["day"])).days >= 6
        for r in st["rehearsals"]), st["rehearsals"]
    # T13.1: in the stretch the coach never starts New skills, and never a rare one
    shares = estimate.shares()
    new = code()
    call(c, "PUT", "/api/me", new, {"exam_date": (t + dt.timedelta(days=12)).isoformat()})
    coach = call(c, "GET", "/api/today", new)["coach"]
    assert coach["why"] != "new" and all(44 * shares[x] >= 2 for x in coach["topics"]), coach
    # T13.7: both groups, every row, and the rare group's own Fix
    common = [x for x in shares if 44 * shares[x] >= 2]
    rare = [x for x in shares if 44 * shares[x] < 2]
    grp = code()
    now_ids = [x["id"] for x in traps_on(grp, 3, common)]
    rare_ids = [x["id"] for x in traps_on(grp, 2, rare)]
    call(c, "PUT", "/api/me", grp, {"exam_date": (t + dt.timedelta(days=12)).isoformat()})
    got = call(c, "GET", "/api/today", grp)
    tr = got["traps"]
    assert sorted(x["id"] for x in tr["now"]["rows"]) == sorted(now_ids) and tr["now"]["n"] == 3
    assert sorted(tr["rare"]["fix"]["body"]["ids"]) == sorted(rare_ids) and tr["rare"]["fix"]["body"]["pool"] == "redo"
    assert sorted(got["next"]["stage"]["rare"]["ids"]) == sorted(rare_ids)
    print("ok  S3 the final stretch: eve, exam morning and after lead Up next; rehearsals on Saturdays with no"
          " clock time; no new rare skills; both trap groups with their own Fix")


# ------------------------------------------------------------------ T14 with Words' R&W slots

def rw_slots(c: TestClient) -> None:
    if not deps.part("words", "record_daily"):
        return
    with patch.dict(os.environ, {"SATF_WORDS_UNREVIEWED": "1"}), contextlib.ExitStack() as stack:
        daily.shown.cache_clear()
        try:
            # S9's known crash (helper Task 18, v2/words-fix) hits some days' seeds: take a zone whose day files
            for tz in (0, 720, -720):
                day = daily.today(tz)
                gen = daily.item("rw:wic", day)
                if gen is None or daily.item("rw:transition", day) is None:
                    continue
                try:
                    for fmt in ("wic", "transition"):
                        deps.part("words", "record_daily")(code(), day, fmt, 0, 1000, tz=tz)
                    break
                except OverflowError:
                    continue
            else:                           # none does: run S3's paths on seeds SQLite can hold
                words_mod = importlib.import_module("server.words")
                made = words_mod.daily_item

                def held(d, fmt):
                    g = made(d, fmt)
                    return g and {**g, "seed": g["seed"] % 2 ** 62}

                stack.enter_context(patch.object(words_mod, "daily_item", held))
                print("--  S3 R&W seeds clamped for this check: words.daily_item's seeds overflow SQLite (S9, Task 18)")
                tz, day = 0, daily.today(0)
                gen = daily.item("rw:wic", day)
            q = call(c, "GET", "/api/qotd", code(), tz=tz)
            assert [s["slot"] for s in q["slots"]] == ["math:mcq", "math:spr", "rw:wic", "rw:transition"]
            named = re.compile(rf"\b{re.escape(gen['word'])}\b", re.I)
            for s in q["slots"]:
                assert not any(k in s["question"] for k in LEAKS), (s["slot"], set(s["question"]) & set(LEAKS))
                shown = {k: v for k, v in s["question"].items() if not (s["slot"] == "rw:wic" and k == "choices")}
                assert not named.search(json.dumps(shown)), (s["slot"], "names the key word before the answer")
                for ch in s["question"].get("choices") or []:
                    assert not isinstance(ch, dict) or not {"correct", "key", "answer", "is_key"} & set(ch), ch
            me = code()
            wrong = (gen["answer_index"] + 1) % 4
            first = call(c, "POST", "/api/qotd", me, {"slot": "rw:wic", "answer": wrong, "day": day, "ms": 20000}, tz=tz)
            assert first["correct"] is False and first["key_word"] == gen["word"] and len(first["reasons"]) == 4
            assert first["given"] == wrong and first["sat_pace_ms"] == daily.SAT_PACE_MS["rw"]
            session = f"qotd:rw:wic:{day}"
            assert db.one("SELECT COUNT(*) n FROM word_reviews WHERE learner=? AND session=?", me, session)["n"] == 1
            again = call(c, "POST", "/api/qotd", me, {"slot": "rw:wic", "answer": gen["answer_index"], "day": day}, tz=tz)
            assert again["already"] and again["given"] == wrong and again["correct"] is False
            assert db.one("SELECT COUNT(*) n FROM word_reviews WHERE learner=? AND session=?", me, session)["n"] == 1
            # T14.6: the twin waits for the answer, then keeps the word in another frame
            call(c, "POST", "/api/qotd/another", code(), {"day": day, "slot": "rw:wic", "like": "word"}, status=409, tz=tz)
            if deps.part("api_words", "_unsign"):
                tw = call(c, "POST", "/api/qotd/another", me, {"day": day, "slot": "rw:wic", "like": "word"}, tz=tz)
                assert not any(k in tw["item"] for k in LEAKS)
                payload = deps.part("api_words", "_unsign")(tw["token"], me, tz)
                assert payload["word"] == gen["word"] and payload["template"] != gen["template"], payload
            # T14.7 / 8: a right answer shows every reason; the Due row is N of 4 and done at 4
            x = code()
            for s in q["slots"]:
                item = daily.item(s["slot"], day)
                key = item["answer_index"] if "answer_index" in item else item["answer"]
                if s["slot"] == "math:mcq":
                    key = "ABCD".index(item["answer"])
                reply = call(c, "POST", "/api/qotd", x, {"slot": s["slot"], "answer": key, "day": day}, tz=tz)
                assert reply["correct"] is True, (s["slot"], reply)
                assert reply.get("rationale") or len(reply.get("reasons") or []) == 4
                row = next(r for r in call(c, "GET", "/api/today", x, tz=tz)["due"]["rows"] if r["kind"] == "qotd")
                assert row["progress"]["of"] == 4
            assert row["status"] == "done" and row["meta"] == "4 of 4"
            assert all(s["mine"] and s["mine"]["correct"] for s in call(c, "GET", "/api/qotd", x, tz=tz)["slots"])
        finally:
            daily.shown.cache_clear()
    print("ok  S3 the four day's questions: R&W keys hidden, filed once in Words' session, twins after the answer,"
          " every reason open, the Due row done at 4 of 4")


# ------------------------------------------------------------------ T6, T8, T10, T12.5, T17.1, T18, T19.4

def fake_sitting(sid: str, mid: int, day: dt.date, half: int = 40) -> dict:
    return {"id": sid, "kind": "module", "low": mid - half, "high": mid + half, "mid": mid,
            "at": f"{day.isoformat()}T12:00:00+00:00", "route": None, "standard": True, "outside": False, "why": None}


def insights_and_score(c: TestClient) -> None:
    t = today()
    me = code()
    answers(me, 25)
    answers(me, 15, right=False)
    ins, got = call(c, "GET", "/api/today/insights", me), call(c, "GET", "/api/today", me)
    by = {x["domain"]: x["answered"] for x in ins["gains"]["by_domain"]}
    assert by == {x["domain"]: x["answered"] for x in got["domains"]}, (by, got["domains"])          # T6.3
    # T8.1: slow but right
    slow = code()
    answers(slow, 6, topic="circles", ms=150000)
    answers(slow, 24, ms=30000)
    pace = call(c, "GET", "/api/today/insights", slow)["pace"]
    assert pace["slow_right"] and pace["slow_right"][0]["topic"] == "circles", pace["slow_right"]
    # T8.4: a Speed drill 20 points under the usual brings the guard (once F5 takes source 'pace')
    if "pace" in drill.SOURCES:
        d = call(c, "POST", "/api/drill", slow, {"topics": ["circles"], "count": 3, "timing": "pace", "source": "pace"})
        answer_drill(c, d["id"], slow, right=False)
        call(c, "POST", f"/api/drill/{d['id']}/finish", slow)
        assert "circles" in call(c, "GET", "/api/today/insights", slow)["pace"]["guard"]
    # T10.1: practice since the last test
    sit = code()
    two_days = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=2)).isoformat()
    answers(sit, 30, right=False, when=two_days)
    m = call(c, "POST", "/api/mock/new", sit, {"full": False})
    call(c, "POST", f"/api/session/{m['id']}/finish", sit)
    db.run("UPDATE sessions SET finished=? WHERE id=?",
           (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).isoformat(timespec="seconds"), m["id"])
    answers(sit, 40)
    delta = call(c, "GET", "/api/today/insights", sit)["estimate"]["practice_delta"]
    assert delta and delta["pts"] > 0 and delta["show"] is True and delta["answers"] == 40, delta
    # T10.2: two sittings two weeks apart project a verdict and a cone
    fake = [fake_sitting("b", 560, t - dt.timedelta(days=10)), fake_sitting("a", 500, t - dt.timedelta(days=24))]
    with patch.object(estimate, "_sittings", return_value=fake):
        blk = api_today._estimate_block(me, 0, {"exam_date": (t + dt.timedelta(days=45)).isoformat(), "target": 700})
    assert blk["verdict"].startswith(("On pace", "Behind")) and blk["projection"]["low"] < blk["projection"]["high"]
    assert blk["made_per_week"] > 0 and blk["needs_per_week"] > 0
    # T10.3: an official score after the exam date, against what was projected
    exam = t - dt.timedelta(days=5)
    api_today.add_outside_score(me, (t - dt.timedelta(days=1)).isoformat(), 640, None, "official")
    before = [fake_sitting("d", 600, exam - dt.timedelta(days=9)), fake_sitting("c", 560, exam - dt.timedelta(days=30))]
    with patch.object(estimate, "_sittings", return_value=before):
        cal = api_today._estimate_block(me, 0, {"exam_date": exam.isoformat(), "target": 700})["calibration"]
    assert cal and cal["score"] == 640 and cal["text"].startswith("We projected") and "you scored 640" in cal["text"]
    # T12.5: a target 200 points above the model, no traps, no sittings: the target's skill work is sized
    far = code()
    answers(far, 20)
    answers(far, 20, right=False)
    db.run("UPDATE traps SET closed=?, closed_how='fixed', due=NULL WHERE learner=?", progress.now(), far)
    s_now = estimate.model(estimate._rows(far))["S"]
    target = min(800, 10 * round((s_now + 200) / 10))
    call(c, "PUT", "/api/me", far, {"exam_date": (t + dt.timedelta(days=30)).isoformat(), "target": target})
    w = call(c, "GET", "/api/today", far)["workload"]
    order = [x["topic"] for x in estimate.gains(far)["skills"]]
    need = w["need"]["target"]
    assert need and need["minutes"] > 0 and need["skills"] == order[:len(need["skills"])], (need, order[:5])
    assert w["fits"] == (need["reachable"] and w["capacity"] >= w["total"])
    print("ok  S3 insights: domains agree, slow-but-right and the guard, practice since the test,"
          " the verdict from 2 sittings, calibration, and the target's skill work")


def day_redo_and_draft(c: TestClient) -> None:
    t = today()
    me = code()
    answers(me, 5, right=False)
    row = next(d for d in call(c, "GET", f"/api/calendar?month={t.isoformat()[:7]}", me)["days"]
               if d["day"] == t.isoformat())
    assert len(row["missed"]) == 5 and "held" in row
    missed = {r["id"]: (r["template"], r["seed"]) for r in db.rows(
        f"SELECT id, template, seed FROM attempts WHERE id IN ({','.join('?' * 5)})", *row["missed"])}
    d = call(c, "POST", "/api/drill", me, {"pool": "history", "ids": row["missed"], "exact": False, "each": 1,
                                           "source": "today"})
    served = answer_drill(c, d["id"], me)
    assert sorted(q["key"] for q in served) == sorted(x[0] for x in missed.values())            # T17.1
    assert not {(q["key"], q["seed"]) for q in served} & set(missed.values())
    # T17: the usual start
    assert re.fullmatch(r"\d\d:\d\d", call(c, "GET", "/api/today", me)["usual_start"] or "")
    # T18: Build with these, Plan step 1's four sources
    blank = {"target": None, "exam_date": None, "minutes": None, "days": None}
    two = [fake_sitting("y", 680, t - dt.timedelta(days=5)), fake_sitting("x", 620, t - dt.timedelta(days=20))]
    with patch.object(estimate, "_sittings", return_value=two):
        dr = api_today.plan_draft(me, 0, blank, t, {"days": []}, [{"high": 720}])
    assert dr["source"]["kind"] == "mean3" and dr["current"] == 650 and dr["target"] == 770 and dr["ready"]
    assert dr["minutes"] == 20 and dr["days"] == "1111100" and dr["exam_date"] > t.isoformat()
    with patch.object(estimate, "_sittings", return_value=two[:1]):
        dr = api_today.plan_draft(me, 0, blank, t, {"days": []}, [])
    assert dr["source"]["kind"] == "latest" and dr["current"] == 680 and dr["target"] == 780
    dr = call(c, "GET", "/api/today", me)["draft"]
    assert dr["source"] == {"kind": "practice", "value": None} and dr["ready"] is False and dr["target"] is None
    assert call(c, "GET", "/api/today", code())["draft"]["source"]["kind"] == "new"
    print("ok  S3 a day's misses redo as twins; the usual start; Build with these reads Plan step 1's four sources")


def receipt_falls(c: TestClient) -> None:
    """T19.4: a day that lowers S claims a negative figure, the same as practice_delta."""
    me = code()
    call(c, "PUT", "/api/me", me, {"minutes": 15})
    answers(me, 30, when=(dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).isoformat())
    answers(me, 20, right=False, ms=60000)
    r = call(c, "GET", "/api/today", me)["receipt"]
    assert r and r["claimed"] < 0 and r["claimed"] == estimate.practice_delta(me, api_today._start(today(), 0))["pts"]
    # an added official score since the last study day is news in the briefing
    call(c, "POST", "/api/scores", me, {"day": today().isoformat(), "math": 650, "source": "official"}, status=201)
    facts = call(c, "GET", "/api/today", me)["brief"]
    assert any(f["kind"] == "score" and f["text"].startswith("Official SAT on") for f in facts), facts
    print("ok  S3 a bad day's receipt claims a fall, as practice_delta does; an added score is in the briefing")


def plan_rows(c: TestClient) -> None:
    """T2.1, 2, 6, 7 and T18's card with a plan (S7)."""
    if not deps.part("plan", "today_summary"):
        return
    me = code()
    t = today()
    check_ins_due(me, traps_on(me, 2), t)
    exam = t + dt.timedelta(days=49 + (5 - t.weekday()) % 7)
    call(c, "POST", "/api/plan", me, {"current": 520, "target": 700, "exam_date": exam.isoformat(),
                                      "minutes": 60, "days": "1111111", "tests": "weekly", "test_size": "module"})
    got = call(c, "GET", "/api/today", me)
    plan, rows = got["plan"], got["due"]["rows"]
    kinds = [r["kind"] for r in rows]
    assert kinds[0] == "plan" and kinds.count("review") == 1 and "warmup" not in kinds, kinds
    assert all(k == "plan" for k in kinds[:kinds.index("review")]), kinds
    assert not [r for r in rows if r["group"] == "plan" and r["kind"] in ("qotd", "challenge")]        # T2.7
    plan_n = [r for r in rows if r["group"] == "plan"]
    assert all(r["task_id"] for r in plan_n) and len(plan_n) <= plan["tasks_counted"] + 1
    card = plan["card"]
    assert card["day"] == 1 and card["of"] == (exam - t).days + 1 and set(card["on_time"]) == {"n", "of"}
    assert got["draft"] is None and plan["days"] and all("status" in d for d in plan["days"])
    # T2.6: the student's own task is a tick, through S7's PATCH, and its minutes count today
    r = c.post(f"/api/plan/{plan['id']}/tasks", headers={"X-Learner": me, "X-Tz": "0"},
               json={"title": "R&W reading", "minutes": 30, "day": t.isoformat()})
    assert r.status_code == 200, r.text[:300]
    got = call(c, "GET", "/api/today", me)
    own = next(x for x in got["due"]["rows"] if x["own"])
    assert own["title"] == "R&W reading" and own["group"] == "plan" and own["status"] == "todo"
    minutes, done = got["study"]["today"], got["plan"]["tasks_done"]
    path = f"/api/plan/{plan['id']}/tasks/{own['task_id']}"
    call(c, "PATCH", path, me, {"day": t.isoformat(), "status": "done"})
    after = call(c, "GET", "/api/today", me)
    mine = next(x for x in after["due"]["rows"] if x["task_id"] == own["task_id"])
    # T2.6 names Plan's status `marked`; S7 files a ticked own task as `done` (listed for S7)
    assert mine["status"] in ("marked", "done") and mine["marked"] and after["plan"]["tasks_done"] == done + 1
    assert after["study"]["today"] == minutes + 30, (minutes, after["study"]["today"])

    def week_done(payload):                 # the week header's figures follow the tick (the plan memo sees it)
        return next(w["tasks_done"] for w in payload["plan"]["weeks"] if w["from"] <= t.isoformat() <= w["to"])
    assert week_done(after) == week_done(got) + 1
    call(c, "PATCH", path, me, {"day": t.isoformat(), "status": "todo"})
    back = call(c, "GET", "/api/today", me)
    assert back["study"]["today"] == minutes and back["plan"]["tasks_done"] == done
    print("ok  S3 with a plan: PLAN rows, then one Review row; no daily extras in PLAN; Day 1 of N;"
          " your own task ticks through S7's PATCH and its minutes count today")


def streak_at_risk(c: TestClient) -> None:
    """T19.2's server half: after 18:00 local, a 6-day streak and nothing today."""
    for minute, risky in ((19 * 60, True), (17 * 60, False)):
        tz = tz_at(minute)
        me = code()
        local = today(tz)
        for back in range(1, 7):
            noon = dt.datetime.combine(local - dt.timedelta(days=back), dt.time(12), dt.timezone.utc) + \
                dt.timedelta(minutes=tz)
            answers(me, 1, when=noon.isoformat())
        got = call(c, "GET", "/api/today", me, tz=tz)
        assert got["days"]["streak"] == 6, got["days"]["streak"]
        r = got["at_risk"]
        assert (r is not None) == risky, (minute, r)
        if risky:
            assert r["streak"] == 6 and 0 < r["left_ms"] <= 5 * 3600 * 1000 and r["start"]["body"]["source"] == "try"
            assert r["start"]["body"]["count"] == 1
    print("ok  S3 the streak at risk shows after 18:00 with a 6-day streak and nothing today, and not at 17:00")


def gates_and_twins(c: TestClient) -> None:
    """Check 10's history half and check 9 once S6's modules land; T5.2 (R19);
    SEC-06's bound on added scores; readiness in the final stretch."""
    me = code()
    s = call(c, "POST", "/api/session", me)
    call(c, "POST", f"/api/session/{s['id']}/finish", me)
    hist = call(c, "GET", "/api/history?kind=tests&all=1&limit=6", me).get("sessions") or []
    row = next((h for h in hist if h["id"] == s["id"]), None)
    if row and "gated" in row:
        assert row["gated"] is True and not row.get("modules") and not row.get("estimate"), row
    m = call(c, "POST", "/api/mock/new", me, {"full": True})
    call(c, "POST", f"/api/session/{m['id']}/finish", me)
    call(c, "POST", f"/api/session/{m['id']}/finish", me)
    review = call(c, "GET", f"/api/session/{m['id']}/results", me).get("review") or []
    row = next((h for h in call(c, "GET", "/api/history?kind=tests&all=1&limit=6", me).get("sessions") or []
                if h["id"] == m["id"]), None)
    if row and len(row.get("modules") or []) == 2:
        one, two = row["modules"]
        assert one.get("asked") == 22 and min(two.get("missed", []) + two.get("blank", [])) == 1, row["modules"]
        assert len(review) == 44
    # T5.2: a twin of a live test's item is refused
    live = call(c, "POST", "/api/mock/new", me, {"full": False})
    r = c.post("/api/drill", headers={"X-Learner": me, "X-Tz": "0"},
               json={"from_session": live["id"], "only": [live["questions"][2]["id"]], "source": "twin"})
    assert r.status_code == 409, (r.status_code, r.text[:200])
    # added scores are bounded
    x = code()
    for _ in range(api_today.SCORES_A_DAY):
        call(c, "POST", "/api/scores", x, {"day": today().isoformat(), "math": 600}, status=201)
    call(c, "POST", "/api/scores", x, {"day": today().isoformat(), "math": 600}, status=429)
    # T13: readiness per domain from 12 days out, each with a 10-minute box
    call(c, "PUT", "/api/me", me, {"exam_date": (today() + dt.timedelta(days=12)).isoformat()})
    got = call(c, "GET", "/api/today", me)
    rd = got["exam"]["readiness"]
    assert [x["domain"] for x in rd] == [x["domain"] for x in got["domains"]] and len(rd) == 4
    assert all(x["state"] in ("ready", "shaky", "untested", "close") and x["start"]["body"]["topics"] for x in rd)
    assert got["exam"]["days"] == 12 and "register_by" in got["exam"] and "registration" in got["exam"]
    print("ok  S3 gated diagnostics and the module split in history (with S6), no twins of a live test,"
          " added scores bounded, readiness per domain in the stretch")


def check(c: TestClient) -> None:
    fresh(c)
    qotd_shape(c)
    qotd_answer_and_crowd(c)
    late_and_grace(c)
    like_drill(c)
    templates_drill(c)
    module_minutes(c)
    diagnostic_gate(c)
    calendar(c)
    profile_fields(c)
    outside_scores(c)
    plan_edits(c)
    open_drill(c)
    workload(c)
    brief_and_receipt(c)
    final_stretch(c)
    due_rows(c)
    goal_met_box(c)
    stages(c)
    rw_slots(c)
    insights_and_score(c)
    day_redo_and_draft(c)
    receipt_falls(c)
    plan_rows(c)
    streak_at_risk(c)
    gates_and_twins(c)
    print("S3 today checks passed")


if __name__ == "__main__":
    with TestClient(app) as client:
        check(client)
