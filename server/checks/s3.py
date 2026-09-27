"""S3 Today server acceptance: spec/rebuild-v2.md §3.2.8 as amended by §2.13 and
spec/v2-upgrades/today.md (T1-T20), plus SEC-02. test_flow runs check(c); alone:

    PYTHONPATH=. python3 server/checks/s3.py

Items that belong to another owner's endpoint (S6's /api/history modules, F2's
next.preview) are checked when that part has landed and skipped quietly before.
"""

from __future__ import annotations

import datetime as dt
import itertools
import json
import os
import secrets
import tempfile
from unittest.mock import patch

if __name__ == "__main__":
    os.environ["SATF_DB"] = tempfile.mktemp(prefix="satf-s3-check-", suffix=".db")

from fastapi.testclient import TestClient

from server import api_today, daily, db, deps, estimate, practice, progress
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


def answer_drill(c: TestClient, sid: str, learner: str, limit: int = 30) -> list[dict]:
    """Answer a drill right until done; the questions it served."""
    for _ in range(limit):
        q = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", sid)["questions"])[-1]
        given = "ABCD".index(q["answer"]) if q["type"] == "mcq" else q["answer"]
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
    assert t["exam"] == {"date": exam, "days": 40} and t["study"]["goal"] == 60 and t["study"]["week_goal"] == 300
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
    print("S3 today checks passed")


if __name__ == "__main__":
    with TestClient(app) as client:
        check(client)
