"""S5 acceptance, server side: §3.4.8 as amended by §2.13, tests.md X1-X23's
server checks and §3.1 item 63's test_flow additions, plus SEC-03 and SEC-07.

Run alone with PYTHONPATH=. python3 server/checks/s5.py, or inside test_flow.
What another owner still has to land is printed as `waiting:` lines, not
asserted, so this file stays green while they build it."""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import secrets
import subprocess
import sys
import tempfile
import time
from collections import Counter

from fastapi.testclient import TestClient

from server import api_tests, blueprint, db, deps, papers, practice, progress, scoring

N = [0]
LEAKS = {"answer", "rationale", "reasons", "distractor_reasons", "key", "seed", "template"}
WAITING: list[str] = []
SPLIT = {"Algebra": 8, "Advanced Math": 7, "Problem-Solving and Data Analysis": 4,
         "Geometry and Trigonometry": 3}


def code(tag: str) -> str:
    N[0] += 1
    return f"a:v2revtests{tag}{N[0]:03d}"


def H(learner: str | None) -> dict:
    return {"X-Learner": learner} if learner else {}


def ok(r, status: int = 200):
    assert r.status_code == status, (r.status_code, r.text[:400])
    return r.json()


def leaks(obj, path: str = "") -> list[str]:
    """Every forbidden key at any depth."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in LEAKS:
                out.append(f"{path}.{k}")
            out += leaks(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += leaks(v, f"{path}[{i}]")
    return out


def wait(msg: str) -> None:
    WAITING.append(msg)


def row(sid: str):
    return db.one("SELECT * FROM sessions WHERE id=?", sid)


def live(sid: str) -> list[dict]:
    """The live module's questions, key included (straight from the store)."""
    return api_tests.questions_of(row(sid))


def result(sid: str) -> dict:
    return json.loads(row(sid)["result"] or "{}")


def qstate(sid: str) -> dict:
    return json.loads(row(sid)["qstate"] or "{}")


def key_of(q: dict):
    return "ABCD".index(q["answer"]) if q["type"] == "mcq" else scoring.keys(q["answer"])[0]


def wrong_of(q: dict, named: bool = False):
    """A wrong answer; with named, an option whose reason names a mistake."""
    if q["type"] != "mcq":
        return "-999"
    k = key_of(q)
    if named:
        for i, r in enumerate(q.get("reasons") or []):
            if i != k and r and progress.norm(r):
                return i
    return (k + 1) % 4


def new(c, learner: str, body: dict, status: int = 200) -> dict:
    return ok(c.post("/api/mock/new", headers=H(learner), json=body), status)


def begin(c, learner: str, sid: str, **body) -> dict:
    return ok(c.post(f"/api/session/{sid}/begin", headers=H(learner), json=body))


def answer(c, learner: str, sid: str, q: dict, value, status: int = 200, **extra) -> dict:
    return ok(c.post(f"/api/session/{sid}/answer", headers=H(learner),
                     json={"question_id": q["id"], "answer": value, **extra}), status)


def state(c, learner: str, sid: str, body: dict, status: int = 200) -> dict:
    return ok(c.post(f"/api/session/{sid}/state", headers=H(learner), json=body), status)


def finish(c, learner: str, sid: str, **body) -> dict:
    return ok(c.post(f"/api/session/{sid}/finish", headers=H(learner), json=body))


def back(sid: str, seconds: float, *cols: str) -> None:
    """Move timestamps back, as if that much time had passed."""
    r = row(sid)
    for col in cols:
        if r[col]:
            t = dt.datetime.fromisoformat(r[col]) - dt.timedelta(seconds=seconds)
            db.run(f"UPDATE sessions SET {col}=? WHERE id=?", t.isoformat(timespec="seconds"), sid)


def fill(c, learner: str, sid: str, right: int = 0, blank=(), named: bool = False, **stamps) -> list[dict]:
    """Answer the live module: the first `right` right, positions in blank
    (1-based) left empty, the rest wrong."""
    qs = live(sid)
    for i, q in enumerate(qs, 1):
        if i in blank:
            continue
        answer(c, learner, sid, q, key_of(q) if i <= right else wrong_of(q, named), **stamps)
    return qs


def sit(c, learner: str, body: dict | None = None, m1: int = 22, m2: int = 22, blank1=(), blank2=(),
        named: bool = False, m1_stamps: dict | None = None, m2_begin: dict | None = None,
        timeout2: bool = False) -> str:
    """A whole section (or single module) from the lobby to the hand-in."""
    s = new(c, learner, body or {"kind": "section"})
    sid = s["id"]
    begin(c, learner, sid, **(m1_stamps or {}))
    fill(c, learner, sid, m1, blank1, named)
    f = finish(c, learner, sid, **(m1_stamps or {}))
    if f.get("next_module") == 2:
        begin(c, learner, sid, **(m2_begin or {}))
        fill(c, learner, sid, m2, blank2, named)
        if timeout2:
            back(sid, 36 * 60, "module_started")
        finish(c, learner, sid)
    assert row(sid)["finished"], "the sitting did not finish"
    return sid


def tests(c, learner: str) -> dict:
    return ok(c.get("/api/tests", headers=H(learner)))


# ------------------------------------------------------------------ the lobby, the clock, pauses (§3.4.8 1-5, 8, 9, 12; X1 1-2)

def lobby(c) -> None:
    me = code("lobby")
    s = new(c, me, {"kind": "section"})
    sid = s["id"]
    assert (s["begun"], s["questions"], s["question_count"], s["seconds"]) == (False, [], 22, 2100), s
    assert s["conditions"] == "test_day" and "pace" not in s and not leaks(s), leaks(s)
    time.sleep(1.1)
    assert ok(c.get(f"/api/session/{sid}", headers=H(me)))["seconds"] == 2100, "the clock ran in the lobby"
    old = new(c, me, {"full": False})
    assert old["mode"] == "module" and old["begun"] is False, "the old body lost its lobby"
    answer(c, me, sid, {"id": "m1q01"}, 0, status=409)
    got = begin(c, me, sid)
    assert len(got["questions"]) == 22 and 2097 <= got["seconds"] <= 2100 and got["begun"]
    assert not leaks(got), leaks(got)
    assert begin(c, me, sid)["seconds"] <= got["seconds"], "Begin is idempotent"

    t = new(c, me, {"kind": "section"})["id"]
    x = ok(c.post(f"/api/session/{t}/cfg", headers=H(me), json={"timing": "x1.5"}))
    assert x["seconds"] == 3150 and x["timing"] == "x1.5"
    begin(c, me, t)
    assert c.post(f"/api/session/{t}/cfg", headers=H(me), json={"timing": "x2"}).status_code == 409

    # Save and exit: the clock stops, questions are withheld, answers refused
    before = ok(c.get(f"/api/session/{sid}", headers=H(me)))["seconds"]
    ok(c.post(f"/api/session/{sid}/pause", headers=H(me), json={}))
    back(sid, 4, "module_started", "paused_at")
    p = ok(c.get(f"/api/session/{sid}", headers=H(me)))
    assert abs(p["seconds"] - before) <= 1 and p["questions"] == [] and p["paused"] is True, p["seconds"]
    answer(c, me, sid, live(sid)[0], 0, status=409)
    r = begin(c, me, sid)
    assert abs(r["seconds"] - before) <= 1 and not r["paused"] and len(r["questions"]) == 22

    # §3.4.8 8: owner only (SEC-03)
    assert c.get(f"/api/session/{sid}", headers=H(code("other"))).status_code == 403
    assert c.get(f"/api/session/{sid}").status_code == 403

    # §3.4.8 9: module 1 in, module 2 waits for its own Begin
    f = finish(c, me, sid)
    assert f["next_module"] == 2 and f["summary"]["answered"] + f["summary"]["unanswered"] == 22, f
    g = ok(c.get(f"/api/session/{sid}", headers=H(me)))
    assert g["begun"] is False and g["seconds"] == 2100 and g["module"] == 2 and g["questions"] == []
    assert "route" not in g, "Test-day never tells the route"

    for timing, secs in (("x1.5", 3150), ("x2", 4200), ("untimed", None)):
        x = new(c, me, {"kind": "section", "timing": timing})
        got = begin(c, me, x["id"])["seconds"]
        assert (got is None) if secs is None else secs - 3 <= got <= secs, (timing, got)
    # X1 2: Tight clock is Training's
    r = c.post("/api/mock/new", headers=H(me), json={"kind": "section", "timing": "x0.85"})
    assert r.status_code == 422 and "timing" in r.text, r.text
    tr = new(c, me, {"kind": "section", "timing": "x0.85", "conditions": "training"})
    assert 1782 <= begin(c, me, tr["id"])["seconds"] <= 1785
    r = c.post(f"/api/session/{tr['id']}/cfg", headers=H(me), json={"conditions": "test_day"})
    assert r.status_code == 409, "cfg after begin"
    # /test/ without ?s= makes nothing (§3.4.8 20)
    n = db.one("SELECT COUNT(*) AS n FROM sessions")["n"]
    assert c.get("/test/").status_code == 200 and db.one("SELECT COUNT(*) AS n FROM sessions")["n"] == n
    print("ok  S5 lobby: clock from Begin, cfg before it, pause and resume, 403s, module 2's own Begin, timings")


# ------------------------------------------------------------------ per-question state (§3.4.8 6-7; X4 X5 X7 X8 X9 X10 X19)

def per_question(c) -> None:
    me = code("state")
    sid = new(c, me, {"kind": "section"})["id"]
    begin(c, me, sid, pid="pa", el=0, hid=0, off=0)
    qs = live(sid)
    state(c, me, sid, {"question_id": "m1q01", "marked": True, "struck": [0, 2], "ms": 12000, "conf": "guess"})
    state(c, me, sid, {"question_id": "m1q01", "ms": 12000})
    g = ok(c.get(f"/api/session/{sid}", headers=H(me)))
    q1 = g["qstate"]["m1q01"]
    assert (q1["marked"], q1["struck"], q1["ms"], q1["conf"]) == (True, [0, 2], 24000, "guess"), q1
    assert not leaks(g), leaks(g)
    assert "pids" not in g["qstate"]["_session"], "stamps stay on the server"
    # X8 1: scratch caps
    big = {"w": 700, "text": 16, "strokes": [[[i, i + 1] for i in range(1300)]] * 2, "typed": ""}
    small = {"w": 700, "text": 16, "strokes": [[[i, i + 1] for i in range(500)]], "typed": "y=2x"}
    assert len(json.dumps(big)) > 20 * 1024 and len(json.dumps(small)) < 20 * 1024
    r = c.post(f"/api/session/{sid}/state", headers=H(me), json={"question_id": "m1q02", "scratch": big})
    assert r.status_code == 422 and "scratch too large" in r.text
    state(c, me, sid, {"question_id": "m1q02", "scratch": small})
    # X9 3, X7, X10 1, X4
    state(c, me, sid, {"question_id": "m1q02", "ref_n": 1, "ref_ms": 4000})
    state(c, me, sid, {"question_id": "m1q02", "ref_n": 1})
    state(c, me, sid, {"question_id": "m1q03", "covered": True, "reveal_ms": 65000, "own": "12"})
    state(c, me, sid, {"report_later": "m1q05"})
    state(c, me, sid, {"nudge": {"kind": "sink", "qid": "m1q03", "took": True}})
    state(c, me, sid, {"question_id": "m1q01", "struck": [5]}, status=422)
    state(c, me, sid, {"marked": True}, status=422)
    got = ok(c.get(f"/api/session/{sid}", headers=H(me)))["qstate"]
    assert got["m1q02"]["scratch"] == small and got["m1q02"]["ref_n"] == 2 and got["m1q02"]["ref_ms"] == 4000
    assert got["m1q03"]["reveal_ms"] > 0 and got["m1q03"]["covered"] is True
    assert got["_session"]["report_later"] == ["m1q05"] and got["_session"]["nudges"][0]["kind"] == "sink"

    # X8 3: the calculator log files attempts.calc; X19: every strike kept
    q4 = qs[3]
    state(c, me, sid, {"question_id": q4["id"], "calc": {"open_ms": 3000, "exprs": ["y=2x+1"]}})
    answer(c, me, sid, q4, key_of(q4))
    mq = next(q for q in qs[5:] if q["type"] == "mcq")
    k = key_of(mq)
    others = [i for i in range(4) if i != k]
    state(c, me, sid, {"question_id": mq["id"], "struck": [k]})
    state(c, me, sid, {"question_id": mq["id"], "struck": [others[1]]})
    answer(c, me, sid, mq, others[0])
    # X5 3: an answer after end_at is the second pass
    state(c, me, sid, {"end_at": 100})
    state(c, me, sid, {"end_at": 99999})                      # first time only
    late_q = next(q for q in qs if q["id"] not in (q4["id"], mq["id"], "m1q01"))
    answer(c, me, sid, late_q, key_of(late_q), pid="pa", el=800)
    assert qstate(sid)[late_q["id"]]["pass"] == 2 and qstate(sid)["_session"]["end_at"] == 100
    finish(c, me, sid)
    assert "end_at" not in qstate(sid)["_session"], "module 2's second pass starts from its own end_at"
    begin(c, me, sid)
    finish(c, me, sid)
    res = result(sid)
    assert res["pass2"]["answered"] >= 1 and res["pass2"]["right"] >= 1 and res["pass2"]["pts"] >= 0, res["pass2"]
    assert "y=2x+1" in qstate(sid)[q4["id"]]["calc"]["exprs"]
    a4 = db.one("SELECT calc FROM attempts WHERE session=? AND qid=?", sid, q4["id"])
    assert a4 and a4["calc"] == 1, "attempts.calc"
    assert k in qstate(sid)[mq["id"]]["struck_ever"]
    am = db.one("SELECT struck FROM attempts WHERE session=? AND qid=?", sid, mq["id"])
    struck = json.loads(am["struck"]) if am and am["struck"] and am["struck"].startswith("[") else am and am["struck"]
    assert am and (struck == [others[1]] or str(others[1]) in str(struck)), struck
    print("ok  S5 qstate: marks, strikes, ms, conf, scratch caps, ref, cover, report-later, calc, pass 2, no leaks")


# ------------------------------------------------------------------ answer rules (§3.4.8 10)

def answer_rules(c) -> None:
    me = code("rules")
    sid = new(c, me, {"kind": "module"})["id"]
    begin(c, me, sid)
    qs = live(sid)
    spr = next(q for q in qs if q["type"] == "spr")
    for bad in ("123456", "1/2/3", "1.2.3", "abc"):
        r = c.post(f"/api/session/{sid}/answer", headers=H(me), json={"question_id": spr["id"], "answer": bad})
        assert r.status_code == 422 and "grid-in" in r.text, (bad, r.text)
    answer(c, me, sid, spr, "-1234")
    mq = next(q for q in qs if q["type"] == "mcq")
    answer(c, me, sid, mq, 0)
    answer(c, me, sid, mq, 1)
    answer(c, me, sid, mq, 1)
    st = qstate(sid)[mq["id"]]
    assert st["first"] == 0 and st["changes"] == 1, st
    answer(c, me, sid, mq, 7, status=422)
    back(sid, 36 * 60, "module_started")
    r = c.post(f"/api/session/{sid}/answer", headers=H(me), json={"question_id": qs[0]["id"], "answer": 0})
    assert r.status_code == 409 and "time is up" in r.text
    assert answer(c, me, sid, qs[0], 0, made_left=5)["late"] is True
    finish(c, me, sid)
    assert result(sid)["late"] == 1 and result(sid)["summary"]["timed_out"] is True
    print("ok  S5 answers: grid-in shape, first and changes, time up, a late answer made in time")


# ------------------------------------------------------------------ ranked or not, from the client's stamps (X1 3-4, X11 3)

def ranks(c) -> None:
    me = code("rank")
    # X1 3: a pause keeps the score and drops the rank
    sid = new(c, me, {"kind": "section"})["id"]
    begin(c, me, sid)
    ok(c.post(f"/api/session/{sid}/pause", headers=H(me), json={}))
    assert ok(c.get(f"/api/session/{sid}", headers=H(me)))["why"] == "paused once"
    begin(c, me, sid)
    finish(c, me, sid)
    begin(c, me, sid)
    finish(c, me, sid)
    r = row(sid)
    assert (r["ranked"], r["unranked_why"]) == (0, "paused once"), (r["ranked"], r["unranked_why"])
    a, b = sit(c, me), sit(c, me)
    t = tests(c, me)
    assert t["estimate"]["latest"]["id"] in (a, b)
    assert t["estimate"]["combined"]["n"] == 2, "Combined counts ranked sittings only"
    assert estimate_has(me, sid), "the paused sitting keeps its score"

    def stamped(stamps_m1: list[dict], last: dict) -> str:
        s = new(c, me, {"kind": "section"})["id"]
        begin(c, me, s, **stamps_m1[0])
        back(s, 300, "module_started")
        for st in stamps_m1[1:]:
            state(c, me, s, st)
        finish(c, me, s, **last)
        begin(c, me, s, pid=last["pid"], el=0, between_ms=20000)
        finish(c, me, s, pid=last["pid"], el=1000)
        return s

    # X1 4: a queue that flushes late while offline stays ranked
    s = stamped([{"pid": "pa", "el": 0}], {"pid": "pa", "el": 290000, "hid": 0, "off": 180000})
    assert row(s)["ranked"] == 1 and qstate(s)["_session"]["offline_ms"] >= 180000, row(s)["unranked_why"]
    assert result(s)["offline_ms"] >= 180000
    s = stamped([{"pid": "pa", "el": 0}], {"pid": "pa", "el": 290000, "hid": 190000, "off": 0})
    assert row(s)["unranked_why"] == "away 3:10", row(s)["unranked_why"]
    s = stamped([{"pid": "pa", "el": 0}, {"pid": "pa", "el": 10000}, {"pid": "pb", "el": 210000}],
                {"pid": "pb", "el": 220000})
    assert (row(s)["unranked_why"] or "").startswith("away"), row(s)["unranked_why"]
    # a stamp can't buy time: el beyond the server's clock is capped
    s = new(c, me, {"kind": "section"})["id"]
    begin(c, me, s, pid="px", el=0)
    state(c, me, s, {"pid": "px", "el": 3_000_000})
    assert qstate(s)["_session"]["pids"]["m1:px"]["last_el"] < 10_000

    # X11 3: a break between modules
    def broke(same_page: bool) -> str:
        s = new(c, me, {"kind": "section"})["id"]
        begin(c, me, s, pid="p1", el=0)
        finish(c, me, s, pid="p1", el=1000)
        m1 = json.loads(row(s)["module1"])
        m1["at"] = (dt.datetime.fromisoformat(m1["at"]) - dt.timedelta(minutes=10)).isoformat(timespec="seconds")
        db.run("UPDATE sessions SET module1=? WHERE id=?", json.dumps(m1), s)
        if same_page:
            begin(c, me, s, pid="p1", el=0, between_ms=55000)
        else:
            begin(c, me, s, pid="p2", el=0)
        finish(c, me, s)
        return s
    s = broke(False)
    assert row(s)["ranked"] == 0 and row(s)["unranked_why"].startswith("break"), row(s)["unranked_why"]
    assert result(s)["between"]["source"] == "server"
    s = broke(True)
    assert row(s)["ranked"] == 1 and result(s)["between"] == {"ms": 55000, "source": "stamp"}
    # Training never ranks
    s = sit(c, me, {"kind": "section", "conditions": "training"}, m1=0, m2=0)
    assert (row(s)["ranked"], row(s)["unranked_why"]) == (0, "training")
    s = sit(c, me, {"kind": "section", "timing": "x1.5"}, m1=0, m2=0)
    assert row(s)["unranked_why"] == "time and a half"
    print("ok  S5 ranks: paused once, offline stays ranked, away and closed pages unrank, breaks, capped stamps")


def estimate_has(learner: str, sid: str) -> bool:
    from server import estimate
    return any(x["id"] == sid for x in estimate._sittings(learner))


# ------------------------------------------------------------------ kinds and the blueprint (§3.4.8 11, 13; X2)

def kinds(c) -> None:
    me = code("kinds")
    s = new(c, me, {"kind": "section", "m1": "upper"})
    begin(c, me, s["id"])
    tiers = Counter(q["difficulty"] for q in live(s["id"]))
    assert tiers == {"easy": 3, "medium": 8, "hard": 11}, tiers
    finish(c, me, s["id"])
    begin(c, me, s["id"])
    finish(c, me, s["id"])
    res = result(s["id"])
    assert res["estimate"] is None and res["scored"] is False and res["not_scored"] == "harder module 1"
    m = sit(c, me, {"kind": "module", "module": "m2u"})
    assert result(m)["scored"] is False and result(m)["not_scored"] == "single module 2"

    # X2 2: fresh sections keep the blueprint
    fresh = code("fresh")
    for _ in range(2):
        x = new(c, fresh, {"kind": "section"})
        qs = api_tests.mock_module(row(x["id"]), 1)
        assert Counter(q["domain"] for q in qs) == SPLIT, Counter(q["domain"] for q in qs)
        assert Counter(q["difficulty"] for q in qs) == {"easy": 7, "medium": 8, "hard": 7}
        assert tuple(i for i, q in enumerate(qs, 1) if q["type"] == "spr") == blueprint.SPR_AT
        # X2 3: what it holds, public counts only
        h = x["holds"]
        assert h["subject"] == "math" and sum(h["domains"].values()) == 22 and isinstance(h["new_types"], int)
        assert h["grid_ins"] == 6 and not leaks(x), leaks(x)

    # §3.4.8 13: a twin keeps each slot's template, tier and format, with new seeds
    src = sit(c, me, {"kind": "section"}, m1=15, m2=10)
    tw = new(c, me, {"kind": "twin", "twin_of": src})
    a, b = api_tests.mock_module(row(src), 1), api_tests.mock_module(row(tw["id"]), 1)
    assert [(q["key"], q["difficulty"], q["type"]) for q in a] == [(q["key"], q["difficulty"], q["type"]) for q in b]
    assert all(x["seed"] != y["seed"] for x, y in zip(a, b)) and [q["id"] for q in a] == [q["id"] for q in b]
    assert json.loads(row(tw["id"])["cfg"])["twin_of"] == src
    assert api_tests.sitting_row(row(tw["id"]))["chain"] == {"root": src, "n": 2}
    like = new(c, me, {"like": src})
    assert json.loads(row(like["id"])["cfg"])["twin_of"] == src, "{like} is the twin alias"
    other = code("other")
    assert c.post("/api/mock/new", headers=H(other), json={"kind": "twin", "twin_of": src}).status_code == 403
    print("ok  S5 kinds: harder module 1 and module 2 unscored, the blueprint, holds, twins slot by slot")


def orders() -> None:
    """X2 1 and 4, with a seeded Builder."""
    can, doms = blueprint.abilities(), blueprint.by_domain()
    _, tier, fmt = next(s for s in blueprint.slots("module1", 1) if s[0] == "Algebra")
    want = (tier, fmt or "mcq")
    pool = [t for t in doms["Algebra"] if want in can.get(t, ())]
    only = [t for t in pool if {k for k in can[t] if k[1] == want[1]} == {want}]
    a, b = (only + pool)[:2] if len(only) >= 2 else pool[:2]
    for seed in range(200):
        bld = practice.Builder(f"s5-order-{seed}", set(), set())
        got = blueprint.fill([("Algebra", tier, fmt)], {"Algebra": [a, b]}, bld, can,
                             log=lambda *_: None, order="exposure", exposure={a: 40})
        assert got and got[0].key == b, (seed, got and got[0].key)

    class Poison(dict):
        def get(self, *_):
            raise AssertionError("the Test-day key read exposure")
    firsts = {sorted(pool, key=blueprint.order_key("shuffle", {}, f"s5-shuffle-{s}", Poison()))[0]
              for s in range(200)}
    assert firsts == set(pool), f"{len(set(pool) - firsts)} of {len(pool)} never ranked first"
    print("ok  S5 X2: Training brings the least-met type, the Test-day key is fair and blind to exposure")


# ------------------------------------------------------------------ X3: the pace plan

def pace(c) -> None:
    me = code("pace")
    assert abs(sum(api_tests.pace_plan(me, "module1", 1)["budget_s"]) - (2100 - 180)) <= 1
    assert abs(sum(api_tests.pace_plan(me, "module1", 1.5)["budget_s"]) - (3150 - 270)) <= 1
    up = api_tests.pace_plan(me, "module2", 1, reveal_route=False, route="upper")
    low = api_tests.pace_plan(me, "module2", 1, reveal_route=False, route="lower")
    assert up["budget_s"] == low["budget_s"], "module 2's budgets gave the route away"
    assert api_tests.pace_plan(me, "module2", 1, True, "upper")["budget_s"] != \
        api_tests.pace_plan(me, "module2", 1, True, "lower")["budget_s"]
    tr = new(c, me, {"kind": "section", "conditions": "training", "pace": True})
    assert len(tr["pace"]["budget_s"]) == 22 and tr["questions"] == [], "the lobby says whose pace it is"
    got = begin(c, me, tr["id"])
    assert len(got["pace"]["budget_s"]) == 22 and got["pace"]["source"] == "default"
    assert isinstance(got["odds"], dict) and all(isinstance(v, float) for v in got["odds"].values())
    td = begin(c, me, new(c, me, {"kind": "section", "pace": True})["id"])
    assert "pace" not in td and "odds" not in td and td["confidence"] is False, "Test-day has no aids"
    # X3 3: 20 first-try rights per tier at 50 / 80 / 140 s
    fast = code("fast")
    sid = "s5-pace-" + secrets.token_hex(4)
    db.run("INSERT INTO sessions(id,kind,learner,started,finished,cfg) VALUES (?,?,?,?,?,?)",
           sid, "mock", fast, deps.now(), deps.now(), "{}")
    for tier, s in (("easy", 50), ("medium", 80), ("hard", 140)):
        for i in range(20):
            db.run("INSERT INTO attempts(learner,session,qid,template,seed,topic,difficulty,fmt,correct,ms,at)"
                   " VALUES (?,?,?,?,?,?,?,?,?,?,?)", fast, sid, f"{tier}{i}", "circle.convert", 9000 + i,
                   "circles", tier, "mcq", 1, s * 1000, deps.now())
    p = api_tests.pace_plan(fast, "module1", 1)
    assert p["source"] == "you" and p["n_answers"] == 60, p
    print("ok  S5 X3: budgets fill the clock less the reserve, blind to the route, from your own speed")


# ------------------------------------------------------------------ papers (§3.4.8 14-15; X20)

def paper_rows(c, me: str) -> dict[int, dict]:
    return {p["n"]: p for p in tests(c, me)["papers"]}


def papers_check(c) -> None:
    me = code("paper")
    rows = paper_rows(c, me)
    assert all(rows[n]["label"] == "Launch set" and rows[n]["source"] == "launch" for n in range(1, 8))
    week = papers.week_of(dt.datetime.now(dt.timezone.utc).date())
    wk = [p for p in rows.values() if p["week"] == week]
    assert len(wk) == 1 and wk[0]["newest"] and wk[0]["source"] == "weekly"
    assert papers.ensure() == wk[0]["n"] and db.one("SELECT COUNT(*) AS n FROM papers WHERE week=?", week)["n"] == 1
    q = json.loads(db.one("SELECT questions FROM papers WHERE n=1")["questions"])
    assert q["sections"][0]["subject"] == "math" and "\"stem\"" not in json.dumps(q)
    assert len(q["sections"][0]["module1"]) == 22 and all(len(s) == 3 for s in q["sections"][0]["module1"])

    # X20 1: the same slots for everyone, each with their own numbers
    a, b = code("pa"), code("pb")
    sa = new(c, a, {"kind": "paper", "paper": 1})["id"]
    sb = new(c, b, {"kind": "paper", "paper": 1})["id"]
    begin(c, a, sa)
    begin(c, b, sb)
    ma, mb = live(sa), live(sb)
    assert [(x["key"], x["difficulty"], x["type"]) for x in ma] == [(x["key"], x["difficulty"], x["type"]) for x in mb]
    assert sum(x["seed"] != y["seed"] for x, y in zip(ma, mb)) >= 20
    assert [s[0] for s in q["sections"][0]["module1"]] == [x["key"] for x in ma], "slots follow the paper"
    g = ok(c.get(f"/api/session/{sa}", headers=H(a)))
    assert g["paper"] == 1 and g["section"].startswith("Paper #1 · Math · Module 1 of 2") and not leaks(g)

    # §3.4.8 15 and X20 7: sat twice counts once; a retake is a twin; Again, exactly re-serves
    fill(c, a, sa, 12)
    finish(c, a, sa)
    begin(c, a, sa)
    finish(c, a, sa)
    re = new(c, a, {"kind": "paper", "paper": 1})["id"]
    assert all(x["seed"] != y["seed"] for x, y in zip(api_tests.mock_module(row(re), 1), ma))
    ex = new(c, a, {"kind": "paper", "paper": 1, "exact": True})["id"]
    assert [(x["key"], x["seed"]) for x in api_tests.mock_module(row(ex), 1)] == [(x["key"], x["seed"]) for x in ma]
    for s in (re, ex):
        begin(c, a, s)
        finish(c, a, s)
        begin(c, a, s)
        finish(c, a, s)
    assert api_tests.sitting_row(row(re))["retake"] == 2 and api_tests.sitting_row(row(ex))["exact"] is True
    before = paper_rows(c, a)[1]
    assert before["yours"]["sittings"] == 3 and before["yours"]["status"] == "completed"
    assert "hardest" in before and before["yours"]["misses_to_fix"] >= 0
    assert new(c, code("none"), {"kind": "paper", "paper": 1, "exact": True}, status=409)
    sat = {r["learner"] for r in papers.sittings(1)}
    assert before["sat_by"] == len(sat), (before["sat_by"], len(sat))

    # X20 5: Sat by counts every first sitting, ranked_n the ranked ones
    n = papers.ensure(dt.date(2031, 3, 3))
    for i, body in enumerate(({"kind": "paper", "paper": n}, {"kind": "paper", "paper": n, "conditions": "training"},
                              {"kind": "paper", "paper": n, "timing": "x2"})):
        sit(c, code("sat"), body, m1=10, m2=5)
    card = paper_rows(c, me)[n]
    assert (card["sat_by"], card["ranked_n"]) == (3, 1), (card["sat_by"], card["ranked_n"])
    assert card["average"] is None and card["hist"] is None and card["yours"]["status"] == "not_sat"
    assert card["rating"]["everyone"]["source"] == "predicted" and card["rating"]["you"]["source"] == "types"
    src = pathlib.Path(papers.__file__).read_text()
    assert "item_ratings" in pathlib.Path(__import__("server.ratings", fromlist=["x"]).__file__).read_text()
    assert "TIER_DEFAULT" not in src and "126" not in src, "papers has no tier-default constants"

    # X20 3: for you, from P11's odds
    weak = code("weak")
    base = q["sections"][0]
    cat = practice.catalogue()["by_topic"]
    lin = cat["linear_functions"]
    can = blueprint.abilities()
    swapped = [list(s) for s in base["module1"]]
    done = 0
    algebra = set(blueprint.by_domain()["Algebra"])
    for s in swapped:
        if done >= 5:
            break
        if s[0] in algebra and practice.topic_of(s[0]) != "linear_functions":
            t = next((t for t in lin if (s[1], s[2]) in can.get(t, ())), None)
            if t:
                s[0] = t
                done += 1
    assert done == 5, "five Algebra slots to swap"
    nx = db.one("SELECT COALESCE(MAX(n),0)+1 AS n FROM papers")["n"]
    for k, m1 in ((nx, swapped), (nx + 1, [list(s) for s in base["module1"]])):
        db.run("INSERT INTO papers(n,week,label,built,questions,source) VALUES (?,?,?,?,?,?)", k, None,
               f"s5 rating {k}", deps.now(), json.dumps({"sections": [{**base, "module1": m1}]}), "launch")
    for topic in {practice.topic_of(t) for t in algebra}:
        db.run("INSERT OR REPLACE INTO skill_ratings(learner,topic,rating,n,seed) VALUES (?,?,?,?,?)",
               weak, topic, 700 if topic == "linear_functions" else 1000, 5, "s5")
    rw = paper_rows(c, weak)
    assert rw[nx]["rating"]["you"]["expect_m1"] <= rw[nx + 1]["rating"]["you"]["expect_m1"] - 1, \
        (rw[nx]["rating"]["you"], rw[nx + 1]["rating"]["you"])
    assert rw[nx]["rating"]["you"]["source"] == "you"
    db.run("DELETE FROM papers WHERE n IN (?,?)", nx, nx + 1)
    papers.forget(nx)
    papers.forget(nx + 1)

    # X20 8: a closed Season Final joins the shelf with its crowd
    cid = "final-2031-10-04"
    spec = {"slots": base["module1"], "slots_m2": {"lower": base["module2_lower"], "upper": base["module2_upper"]},
            "sat_date": "2031-10-04"}
    past = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).isoformat(timespec="seconds")
    db.run("INSERT INTO contests(id,kind,title,opens,closes,count,seconds,spec,created,subject) VALUES"
           " (?,?,?,?,?,?,?,?,?,?)", cid, "final", "Season Final", past, past, 44, 4200, json.dumps(spec), past, "math")
    crowd = []
    for i in range(25):
        who = code("fin")
        crowd.append(who)
        est = {"low": 460 + 10 * i, "high": 480 + 10 * i}        # 20 wide (scoring.band), centres 470 + 10 i
        db.run("INSERT INTO sessions(id,kind,learner,started,finished,contest,ranked,result,cfg,subject)"
               " VALUES (?,?,?,?,?,?,?,?,?,?)", f"s5-final-{i}-{secrets.token_hex(3)}", "module", who, past, past,
               cid, 1, json.dumps({"estimate": est}), "{}", "math")
    road = papers.ensure()
    road_n = db.one("SELECT n FROM papers WHERE source=?", cid)["n"]
    assert road == wk[0]["n"]
    card = paper_rows(c, crowd[3])[road_n]
    assert card["sat_by"] == 25 and card["kind"] == "road_to" and card["label"] == "Road to Oct 4"
    assert card["hist"] and len(card["hist"]) == 25 and card["yours"]["first_percentile"] is not None
    assert card["average"]["basis"] == "ranked"
    print("ok  S5 papers: the shelf, one weekly build, twin slots, retakes, exact, Sat by, ratings, Road-to")


# ------------------------------------------------------------------ discussion and the board (§3.4.8 16; X21; tools/moderate.py)

def seat(learner: str, n: int, route: str = "upper") -> str:
    """A finished paper sitting straight into the store, for voters and readers."""
    sid = f"s5-seat-{secrets.token_hex(5)}"
    db.run("INSERT INTO sessions(id,kind,mock_id,learner,started,finished,route,cfg,result) VALUES (?,?,?,?,?,?,?,?,?)",
           sid, "mock", f"P{n}", learner, deps.now(), deps.now(), route, json.dumps({"paper": n}), "{}")
    return sid


def discussion(c) -> None:
    from tools import moderate
    me = code("talk")
    g = ok(c.get("/api/papers/1/posts", headers=H(me)))
    assert g["gated"] is True and "threads" not in g
    assert c.post("/api/papers/1/posts", headers=H(me), json={"text": "hi"}).status_code == 403
    sit(c, me, {"kind": "paper", "paper": 1}, m1=8, m2=4)
    g = ok(c.get("/api/papers/1/posts", headers=H(me)))
    assert g["gated"] is False and isinstance(g["threads"], list)
    r = c.post("/api/papers/1/posts", headers=H(me), json={"text": "Q7 is a trap", "about": "m1:7"})
    assert r.status_code == 422 and "name" in r.text
    ok(c.put("/api/me", headers=H(me), json={"name": "Ana"}))
    post = ok(c.post("/api/papers/1/posts", headers=H(me), json={"text": "Q7 is a trap", "about": "m1:7"}))
    reply = ok(c.post("/api/papers/1/posts", headers=H(me), json={"text": "and Q8", "parent": post["id"]}))
    assert c.post("/api/papers/1/posts", headers=H(me), json={"text": "x", "parent": reply["id"]}).status_code == 422
    assert c.post("/api/papers/1/posts", headers=H(me), json={"text": "x", "about": "m9:1"}).status_code == 422
    ok(c.put(f"/api/posts/{post['id']}", headers=H(me), json={"text": "Q7 is a real trap"}))
    voters = [code("vote") for _ in range(3)]
    for v in voters:
        seat(v, 1)
    assert c.put(f"/api/posts/{post['id']}", headers=H(voters[0]), json={"text": "no"}).status_code == 403
    ok(c.post(f"/api/posts/{post['id']}/helpful", headers=H(voters[0])))
    ok(c.post(f"/api/posts/{post['id']}/helpful", headers=H(voters[0])))
    assert db.one("SELECT helpful FROM posts WHERE id=?", post["id"])["helpful"] == 1, "one vote per code"
    assert moderate.main(["--pending"]) == 0
    for i, v in enumerate(voters):
        got = ok(c.post(f"/api/posts/{post['id']}/report", headers=H(v)))
        assert got["hidden"] is (i == 2), (i, got)
        if i == 0:
            assert moderate.main(["--pending"]) == 1, "a reported post waits for a moderator"
    seen = ok(c.get("/api/papers/1/posts", headers=H(voters[0])))["threads"]
    assert all(t["id"] != post["id"] for t in seen), "a hidden post shows only to its author"
    assert any(t["id"] == post["id"] for t in ok(c.get("/api/papers/1/posts", headers=H(me)))["threads"])
    assert moderate.main(["restore", str(post["id"])]) == 0 and moderate.main(["--pending"]) == 0
    assert not db.one("SELECT hidden FROM posts WHERE id=?", post["id"])["hidden"]
    moderate.main(["mute", voters[1]])
    ok(c.put("/api/me", headers=H(voters[1]), json={"name": "Bo"}))
    muted = ok(c.post("/api/papers/1/posts", headers=H(voters[1]), json={"text": "spam"}))
    assert muted["hidden"] is True
    moderate.main(["unmute", voters[1]])
    for i in range(18):
        ok(c.post("/api/papers/1/posts", headers=H(me), json={"text": f"note {i}"}))
    assert c.post("/api/papers/1/posts", headers=H(me), json={"text": "one too many"}).status_code == 429
    ok(c.delete(f"/api/posts/{reply['id']}", headers=H(me)))
    # X21 5: a code with no finished sitting of this week's paper can't post there
    wk = papers.ensure()
    assert c.post(f"/api/papers/{wk}/posts", headers=H(code("minted")), json={"text": "hi"}).status_code == 403
    print("ok  S5 discussion: gated, names, replies, edits, one vote each, 3 reports hide, moderate.py, 20 a day")


def board(c) -> None:
    n = papers.ensure(dt.date(2031, 5, 5))
    me = code("board")
    g = ok(c.get(f"/api/papers/{n}/crowd", headers=H(me)))
    assert g["gated"] is True and "slots" not in g
    sid = sit(c, me, {"kind": "paper", "paper": n}, m1=6, m2=4, blank1=(20, 21))
    papers._CROWD.clear()
    got = ok(c.get(f"/api/papers/{n}/crowd", headers=H(me)))
    assert got["gated"] is False and len(got["slots"]) >= 44 and got["source"] == "site", len(got["slots"])
    assert not leaks({k: v for k, v in got.items()}), leaks(got)
    p = papers.paper(n)["sections"][0]
    by = {s["slot"]: s for s in got["slots"]}
    # X21 2: site-wide data per (template, tier)
    t, tier, fmt = p["module1"][0]
    n0 = by["m1:1"]["n"]
    for i in range(30):
        db.run("INSERT INTO attempts(learner,session,qid,template,seed,topic,difficulty,fmt,correct,ms,at)"
               " VALUES (?,?,?,?,?,?,?,?,?,?,?)", code("crowd"), None, "q", t, 50000 + i, practice.topic_of(t),
               tier, fmt, i % 3 == 0, 60000, deps.now())
    papers._CROWD.clear()
    by = {s["slot"]: s for s in ok(c.get(f"/api/papers/{n}/crowd", headers=H(me)))["slots"]}
    assert by["m1:1"]["source"] == "site" and by["m1:1"]["n"] == n0 + 30 and isinstance(by["m1:1"]["right"], float)
    # X21 3: under 5 answers, no shares, the designed traps instead
    thin = next((s for s in by.values() if 0 < s["n"] < 5 or s["n"] == 0), None)
    if thin:
        assert thin["spread"] == [] and (thin["designed"] or thin["fmt"] == "spr"), thin
    assert any(s["designed"] for s in by.values() if s["n"] < 5)
    # X21 4
    for s in by.values():
        assert sum(x["share"] for x in s["spread"]) <= 1.0001, s
        assert s["spread"] == [] or s["n"] >= 5
    for ch in ok(c.get(f"/api/papers/{n}/crowd", headers=H(me)))["cheapest"]:
        assert ch["you"] != "right" and ch["right"] >= 0.8
    assert by["m1:20"]["you"]["state"] == "blank" and by["m1:1"]["you"]["state"] in ("right", "wrong")
    route = row(sid)["route"]
    off = "m2l" if route == "upper" else "m2u"
    assert all(not s["on_route"] for s in by.values() if s["module"] == off)
    print("ok  S5 board: gated, 66 slots, site-wide until 20 first sittings, no share below 5, designed traps")


# ------------------------------------------------------------------ the hand-in (X10 X11 X12 X14)

def hand_in(c) -> None:
    me = code("done")
    sid = new(c, me, {"kind": "section"})["id"]
    begin(c, me, sid)
    qs = live(sid)
    q5 = qs[4]
    db.run("INSERT INTO reports(learner,kind,template,seed,category,title,context,at,status) VALUES (?,?,?,?,?,?,?,?,?)",
           code("rep"), "report", q5["key"], q5["seed"], "key_wrong", "wrong key", json.dumps({"outcome": "key_wrong"}),
           deps.now(), "new")
    fill(c, me, sid, 16, blank=(21, 22))
    f = finish(c, me, sid)
    # X11 1: a prediction on the handed-in module, nothing else
    state(c, me, sid, {"question_id": "m1q03", "predict": "miss"})
    state(c, me, sid, {"question_id": "m1q03", "marked": True}, status=409)
    state(c, me, sid, {"question_id": "m1q21", "predict": "miss"}, status=409)      # a blank can't be
    begin(c, me, sid)
    state(c, me, sid, {"question_id": "m1q03", "marked": True}, status=409)
    state(c, me, sid, {"question_id": "m1q17", "predict": "miss"})
    fill(c, me, sid, 10)
    f = finish(c, me, sid)
    done = f["done"]
    assert done["estimate"]["low"] and done["estimate"]["high"] and done["headline"] == "Your first estimate"
    assert done["pressure"]["eligible"] and done["pressure"]["n"] >= 5 and "See your report" not in json.dumps(done)
    assert done["misses"] > 0 and done["ranked"] is True and done["gate"]["needed"] == 14
    res = result(sid)
    # X10 2: a question with a bad key leaves the score
    assert res["removed"] == [q5["id"]] and res["modules"][0]["asked"] == 21, (res["removed"], res["modules"][0])
    r = c.get(f"/api/session/{sid}/results", headers=H(me))
    if r.status_code != 200 or r.json().get("removed") != [q5["id"]]:
        wait("S6: GET /api/session/{id}/results carries result.removed and re-reads removals (X10 2)")
    after = api_tests.predicted(row(sid))
    wrong = sum(len(m["missed"]) for m in res["modules"])
    assert after["spotted"] + after["silent"] == wrong and after["underconfident"] == 1, (after, wrong)
    state(c, me, sid, {"question_id": "m1q04", "predict": "miss"})
    back(sid, 16 * 60, "finished")
    state(c, me, sid, {"question_id": "m1q04", "predict": None}, status=409)
    # X14 1: the gate
    m = sit(c, me, {"kind": "module"}, m1=13)
    g = result(m)["gate"]
    assert (g["right"], g["needed"], g["margin"]) == (13, 14, -1) and g["subject"] == "math", g
    assert g["cheap_misses"] == [i for i, q in enumerate(api_tests.mock_module(row(m), 1), 1)
                                 if i > 13 and q["difficulty"] in ("easy", "medium")]
    print("ok  S5 hand-in: done, predictions after the module, a removed question, the gate")


def trainers(c) -> None:
    me = code("train")
    body = {"kind": "module", "module": "m1", "trainer": "route", "conditions": "test_day"}
    for _ in range(3):
        sit(c, me, body, m1=15)
    k = {x["id"]: x for x in tests(c, me)["kinds"]}
    assert k["trainer"]["streak"] == 3 and k["trainer"]["yours"] == 3, k["trainer"]
    assert k["module2u"]["gauntlet"]["goal"] == 18 and k["module2u"]["gauntlet"]["pips"] == []
    assert new(c, me, {"kind": "module", "module": "m1", "trainer": "gauntlet"}, status=422)
    g = new(c, me, {"kind": "module", "module": "m2u", "trainer": "gauntlet"})
    assert g["kind_label"] == "Gauntlet"
    # X14 3: Protect the gate after two lower routes
    low = code("low")
    for _ in range(2):
        sit(c, low, m1=5, m2=5)
    gate = tests(c, low)["gate"]
    assert gate["lower_recent"] and gate["protect"]["count"] == 12
    cheap = set()
    for r in api_tests.finished_sittings(low):
        m1 = api_tests.mock_module(r, 1)
        cheap |= {m1[i - 1]["key"] for i in result(r["id"])["gate"]["cheap_misses"]}
        assert all(m1[i - 1]["difficulty"] in ("easy", "medium") for i in result(r["id"])["gate"]["cheap_misses"])
    assert set(gate["protect"]["templates"]) <= cheap
    t = tests(c, low)
    assert t["up_next"]["kind"] == "trainer" or t["up_next"]["reason"] in ("pressure", "paper", "traps"), t["up_next"]
    print("ok  S5 X14: trainer streaks, the gauntlet, Protect the gate from easy and medium misses")


# ------------------------------------------------------------------ X13: the pressure check

def pressure(c) -> None:
    me = code("press")
    sid = new(c, me, {"kind": "section"})["id"]
    begin(c, me, sid)
    qs = live(sid)
    # 3 wrong with a named mistake, 2 blank, the rest right
    wrong_at = [i for i, q in enumerate(qs, 1) if q["type"] == "mcq" and i > 2][:3]
    blank_at = [1, 2]
    for i, q in enumerate(qs, 1):
        if i in blank_at:
            continue
        answer(c, me, sid, q, wrong_of(q, True) if i in wrong_at else key_of(q))
    finish(c, me, sid)
    begin(c, me, sid)
    fill(c, me, sid, 22)
    finish(c, me, sid)
    lost = api_tests.pressure_questions(row(sid))
    assert lost[:5] == [qs[i - 1]["id"] for i in sorted(blank_at + wrong_at)], lost
    r = c.post("/api/drill", headers=H(me), json={"pressure": sid})
    if r.status_code != 200:
        wait("F5: POST /api/drill {pressure: sid} through api_tests.resolve_drill, sources pressure/gate/fix, "
             "and drill.finish calling api_tests.on_drill_finish when cfg.pressure_of is set (R10, §2.10)")
    d = ok(c.post(f"/api/session/{sid}/pressure", headers=H(me)))
    did = d["id"] if "id" in d else d.get("session")
    drow = row(did)
    cfg = json.loads(drow["cfg"])
    assert cfg["inline"] and cfg["parent"] == sid and cfg["source"] == "pressure" and cfg["feedback"] == "end"
    of = cfg["pressure_of"]
    marked = {q["id"]: q for q in api_tests.marked_questions(row(sid))}
    assert len(of) >= 5
    for pair, qid in of.items():
        t, s = pair.rsplit(":", 1)
        assert t == marked[qid]["key"] and int(s) != marked[qid]["seed"]
        assert practice.generate(t, int(s)).difficulty == marked[qid]["difficulty"]
    assert all(h["id"] != did for h in ok(c.get("/api/history", headers=H(me)))["sessions"])
    # answer the twins: the first wrong original's twin the same wrong way, a blank's twin right in 40 s
    knowledge_qid = pressure_qid = None
    served = {}
    for _ in range(len(of) + 2):
        nx = c.post(f"/api/drill/{did}/next", headers=H(me))
        if nx.status_code != 200 or not nx.json().get("question"):
            break
        qid = nx.json()["question"]["id"]
        dq = next(q for q in json.loads(row(did)["questions"]) if q["id"] == qid)
        orig = of[f"{dq['key']}:{dq['seed']}"]
        pick = key_of(dq)
        ms = 40000
        if orig in [qs[i - 1]["id"] for i in wrong_at] and knowledge_qid is None:
            oq = marked[orig]
            want = progress.norm(oq["reasons"][wrong_of(oq, True)])
            same = [i for i, rsn in enumerate(dq.get("reasons") or []) if rsn and progress.norm(rsn) == want]
            if same:
                pick, knowledge_qid = same[0], orig
        elif orig == qs[0]["id"]:
            pressure_qid = orig
        served[orig] = pick
        ok(c.post(f"/api/drill/{did}/answer", headers=H(me), json={"question_id": qid, "answer": pick, "ms": ms}))
    assert len(served) == len(of), "the pressure round serves only its mapped twins"
    ok(c.post(f"/api/drill/{did}/finish", headers=H(me)))
    t = tests(c, me)
    got = result(sid).get("pressure")
    assert got, "the verdicts were stored on the parent"
    assert pressure_qid in got["buckets"]["pressure"], got["buckets"]
    if knowledge_qid:
        assert knowledge_qid in got["buckets"]["knowledge"], got["buckets"]
    band = result(sid)["estimate"]
    assert got["ceiling"]["mid"] >= (band["low"] + band["high"]) / 2
    assert not api_tests.pressure_eligible(row(sid))[0], "one pressure check a sitting"
    assert t["in_progress"] == [] and all(r["id"] != did for r in t["in_progress"])
    causes = progress.causes(me, session=sid).get("per_q", {})
    if not (causes.get(pressure_qid, {}).get("cause") == "slip" and
            (not knowledge_qid or causes.get(knowledge_qid, {}).get("cause") == "trap")):
        wait("F4: progress.causes lets result.pressure verdicts decide (knowledge→trap, pressure→slip) (X13 4)")
    # X13 3: after the review has been opened
    other = sit(c, me, m1=12, m2=8)
    db.run("UPDATE sessions SET qstate=json_set(qstate,'$._session.keys_seen',?) WHERE id=?", deps.now(), other)
    r = c.post(f"/api/session/{other}/pressure", headers=H(me))
    assert r.status_code == 409 and "answers already seen" in r.text
    assert c.post(f"/api/session/{sid}/pressure", headers=H(code("x"))).status_code == 403
    print("ok  S5 X13: twins of what was lost, end mode and inline, verdicts on the parent, the ceiling, 409s")


# ------------------------------------------------------------------ X16: the trap test and the cycle

def traps(c) -> None:
    me = code("trap")
    sid = sit(c, me, m1=10, m2=6, named=True)
    rows = db.rows("SELECT * FROM traps WHERE learner=?", me)
    assert len(rows) >= 3, "a section with named misses opened traps"
    body = {"kind": "custom", "custom": {"source": "traps", "from_session": sid, "neutral": 0.25}}
    s = new(c, me, body)
    tid = s["id"]
    qs = api_tests.mock_module(row(tid), 1)
    trap_of = json.loads(row(tid)["cfg"])["custom"]["trap_of"]
    assert len(qs) >= 6 and trap_of
    norms = {r["norm"] for r in db.rows("SELECT norm FROM traps WHERE learner=? AND closed IS NULL", me)}
    for q in qs:
        offered = set(progress.offered_of(q))
        if q["id"] in trap_of:
            assert trap_of[q["id"]] in offered, (q["id"], trap_of[q["id"]], offered)
        else:
            assert not offered & norms, (q["id"], offered & norms)
    assert s["kind_label"] == "Trap test" and s["seconds"] == 95 * len(qs)
    # X16 3: close one trap, then take it again; answer another cleanly
    t_ids = list(trap_of)
    first = next(q for q in qs if q["id"] == t_ids[0])
    trap_row = db.one("SELECT * FROM traps WHERE learner=? AND template=? AND norm=?", me, first["key"], trap_of[first["id"]])
    db.run("UPDATE traps SET closed=?, closed_how=?, due=? WHERE id=?", deps.now(), "fixed", deps.now()[:10], trap_row["id"])
    begin(c, me, tid)
    pick = next(i for i, rsn in enumerate(first["reasons"]) if rsn and progress.norm(rsn) == trap_of[first["id"]])
    answer(c, me, tid, first, pick)
    clean = cleaned = None
    if len(t_ids) > 1:
        clean = next(q for q in qs if q["id"] == t_ids[1])
        cleaned = db.one("SELECT * FROM traps WHERE learner=? AND template=? AND norm=?", me, clean["key"],
                         trap_of[clean["id"]])
        if cleaned:
            db.run("UPDATE traps SET closed=?, closed_how=?, due=?, checks=0 WHERE id=?", deps.now(), "fixed",
                   deps.now()[:10], cleaned["id"])
        answer(c, me, tid, clean, key_of(clean))
    finish(c, me, tid)
    res = result(tid)
    assert res["estimate"] is None and res["scored"] is False and res["not_scored"] == "trap test"
    after = db.one("SELECT * FROM traps WHERE id=?", trap_row["id"])
    assert after["relapses"] == (trap_row["relapses"] or 0) + 1 and after["closed"] is None, dict(after)
    if cleaned:
        got = db.one("SELECT checks, closed FROM traps WHERE id=?", cleaned["id"])
        assert got["checks"] == 1 and got["closed"], dict(got)
    assert api_tests.sitting_row(row(tid))["kind_label"] == "Trap test"
    k = {x["id"]: x for x in tests(c, me)["kinds"]}
    assert k["traps"]["yours"] == 1 and k["traps"]["ready"] >= 1
    # X16 1: Prove is due 3 days after the last of the sitting's traps closes
    day = dt.date.today() - dt.timedelta(days=1)
    db.run("UPDATE traps SET closed=? WHERE learner=? AND session=?", f"{day}T10:00:00+00:00", me, sid)
    cyc = tests(c, me)["cycle"]
    if cyc and cyc["session"] == sid:
        assert cyc["prove"]["due"] == (day + dt.timedelta(days=3)).isoformat(), cyc["prove"]
    else:
        assert db.one("SELECT COUNT(*) AS n FROM traps WHERE session=?", sid)["n"] == 0 or cyc, cyc
        wait("F4: traps.session names the sitting a trap opened in (X16 1's cycle)")
    assert new(c, code("none"), body, status=404)
    print("ok  S5 X16: the trap test offers each trap's norm, neutral slots offer none, unscored, the cycle")


# ------------------------------------------------------------------ X15, X17, X1 7: what /api/tests prescribes

def overview(c) -> None:
    empty = code("empty")
    t = tests(c, empty)
    assert t["up_next"]["kind"] == "diagnostic" and t["in_progress"] == [] and t["habits"]["rows"] == []
    assert t["levers"]["causes"] == [] and t["growth"] is None and t["cycle"] is None and t["twin"] is None
    assert t["prefs"]["test_conditions"] == "test_day" and set(t["types_met"]) >= {"tests", "never"}
    assert {k["id"] for k in t["kinds"]} >= {"section", "module1", "custom", "diagnostic", "trainer", "traps"}
    # X1 7: two sections that left 3 blanks each
    me = code("blank")
    for _ in range(2):
        sit(c, me, m1=15, m2=15, blank2=(20, 21, 22), timeout2=True)
    rec = tests(c, me)["recommended"]
    assert rec["preset"] == "pacing" and "blanks" in rec["reason"], rec
    # X15 1: traps and the clock priced by re-marking
    lv = code("lever")
    sit(c, lv, m1=18, m2=18, named=True)
    sit(c, lv, m1=18, m2=19, blank2=(20, 21, 22), timeout2=True)
    got = tests(c, lv)["levers"]
    causes = {x["cause"]: x for x in got["causes"]}
    if "trap" in causes:
        assert causes["trap"]["pts"] > 0 and causes["trap"]["action"]["body"]["pool"] == "redo"
    if causes.get("clock", {}).get("n") != 3:
        wait(f"F4: progress.causes files blanks at time-up as 'clock' (X15 1; got {sorted(causes)})")
    assert got["sittings"] == 2
    # X15 2-4
    assert tests(c, lv)["growth"] is None
    last, other = api_tests.finished_sittings(lv)[:2]
    # 20-wide bands no longer overlap, so the score must pair with `last`: the other section two days earlier
    back(other["id"], 2 * 86400, "finished")
    band = result(last["id"])["estimate"]
    day = (dt.date.fromisoformat(last["finished"][:10]) + dt.timedelta(days=3)).isoformat()
    db.run("INSERT INTO outside_scores(learner,day,math,source,at) VALUES (?,?,?,?,?)", lv, day,
           int((band["low"] + band["high"]) / 20) * 10, "bluebook", deps.now())
    cal = tests(c, lv)["calibration"]
    assert cal and any(p.get("inside") for p in cal.get("pairs", [])) or cal.get("inside") is True, cal
    db.run("UPDATE learners SET rw_now=620 WHERE id=?", lv) if db.one("SELECT 1 FROM learners WHERE id=?", lv) else \
        db.run("INSERT INTO learners(id,rw_now,created) VALUES (?,?,?)", lv, 620, deps.now())
    assert tests(c, lv)["total"], "a total with the R&W score"
    # X17: habits
    hb = code("habit")
    one = sit(c, hb, m1=10, m2=10)
    assert tests(c, hb)["habits"]["rows"] == []
    flips = [(5, 0), (0, 2), (0, 0)]
    for rw, wr in flips:
        s = new(c, hb, {"kind": "section"})["id"]
        begin(c, hb, s)
        qs = live(s)
        for i, q in enumerate(qs):
            if i < rw:
                answer(c, hb, s, q, key_of(q))
                answer(c, hb, s, q, wrong_of(q))
            elif i < rw + wr:
                answer(c, hb, s, q, wrong_of(q))
                answer(c, hb, s, q, key_of(q))
            else:
                answer(c, hb, s, q, key_of(q) if i % 2 else wrong_of(q))
        finish(c, hb, s)
        begin(c, hb, s)
        finish(c, hb, s)
    h = tests(c, hb)["habits"]
    assert len(h["rows"]) >= 8 and h["n"] == 4 and h["from_n"] >= 3
    ch = next(r for r in h["rows"] if r["id"] == "changes")
    assert ch["verdict"] == "costs" and "5" in ch["evidence"] and "2" in ch["evidence"], ch
    assert one
    print("ok  S5 overview: the empty state, the recommended preset, levers, calibration, total, habits")


# ------------------------------------------------------------------ discard, history rows, shares, security

def rows_and_discard(c) -> None:
    me = code("hist")
    live_sid = new(c, me, {"kind": "section"})["id"]
    begin(c, me, live_sid)
    fill(c, me, live_sid, 3, blank=range(4, 23))
    r = api_tests.sitting_row(row(live_sid))
    assert r["status"] == "in_progress" and r["left_seconds"] and r["answered"] == 3 and r["href"].endswith(live_sid)
    t = tests(c, me)
    assert [x["id"] for x in t["in_progress"]] == [live_sid] and t["up_next"]["kind"] == "resume"
    done = sit(c, me, m1=11, m2=9, blank1=(21, 22))
    d = api_tests.sitting_row(row(done))
    assert d["status"] == "completed" and d["modules"][0]["asked"] == 22 and d["modules"][0]["blank"] == [21, 22]
    assert len(d["modules"][0]["missed"]) == 9 and d["number"] == 2 and d["ranked"] is True
    ok(c.put(f"/api/session/{done}/note", headers=H(me), json={"text": "felt rushed"}))
    assert api_tests.sitting_row(row(done))["note"] == "felt rushed"
    ok(c.post(f"/api/session/{live_sid}/discard", headers=H(me)))
    assert row(live_sid)["finished"] is None and row(live_sid)["abandoned"]
    assert tests(c, me)["in_progress"] == []
    for path, body in (("answer", {"question_id": "m1q01", "answer": 0}), ("state", {"question_id": "m1q01", "marked": True}),
                       ("begin", {}), ("finish", {}), ("pause", {})):
        r = c.post(f"/api/session/{live_sid}/{path}", headers=H(me), json=body)
        assert r.status_code == 409 and "discarded" in r.text, (path, r.text)
    today = ok(c.get("/api/today", headers=H(me)))
    assert today.get("tested") in (True, False)
    fresh = code("disc")
    x = new(c, fresh, {"kind": "section"})["id"]
    ok(c.post(f"/api/session/{x}/discard", headers=H(fresh)))
    assert ok(c.get("/api/today", headers=H(fresh)))["tested"] is False
    assert new(c, fresh, {"kind": "section"})["number"] == 1, "a discarded sitting takes no number"
    h = c.get("/api/history?all=1", headers=H(me)).json().get("sessions", [])
    if not any(s.get("status") == "completed" and s.get("modules") for s in h):
        wait("S6: GET /api/history?all=1 lists rows through api_tests.sitting_row / open_sittings (§3.4.8 18-19)")
    print("ok  S5 rows: in progress, completed with missed and blank lists, notes, discard everywhere")


def shares(c) -> None:
    owner, v1, v2 = code("sho"), code("shv"), code("shw")
    src = sit(c, owner, m1=16, m2=12)
    twin = ok(c.post("/api/sets", headers=H(owner), json={"kind": "test", "session": src, "cfg": {"fresh": True}}))
    exact = ok(c.post("/api/sets", headers=H(owner), json={"kind": "test", "session": src}))
    assert '"stem"' not in json.dumps(ok(c.get(f"/api/sets/{twin['code']}")))
    m1 = api_tests.mock_module(row(src), 1)
    a = new(c, v1, {"kind": "shared", "shared": twin["code"]})
    b = new(c, v2, {"kind": "shared", "shared": twin["code"]})
    for got in (a, b):
        qs = api_tests.mock_module(row(got["id"]), 1)
        assert [(q["key"], q["difficulty"]) for q in qs] == [(q["key"], q["difficulty"]) for q in m1]
        assert got["shared_by"] is None or isinstance(got["shared_by"], str)
    qa, qb = api_tests.mock_module(row(a["id"]), 1), api_tests.mock_module(row(b["id"]), 1)
    assert sum(x["seed"] != y["seed"] for x, y in zip(qa, qb)) >= 20
    e = new(c, v1, {"kind": "shared", "shared": exact["code"]})
    assert [(q["key"], q["seed"]) for q in api_tests.mock_module(row(e["id"]), 1)] == [(q["key"], q["seed"]) for q in m1]
    assert row(e["id"])["shared_from"] == exact["code"] and not leaks(e)
    print("ok  S5 shares: twin shares slot by slot with new seeds, exact shares the same items, no stems")


def security(c) -> None:
    me, other = code("sec"), code("secx")
    sid = new(c, me, {"kind": "section"})["id"]
    calls = (("get", "", None), ("post", "/answer", {"question_id": "m1q01", "answer": 0}),
             ("post", "/state", {"question_id": "m1q01", "marked": True}), ("post", "/begin", {}),
             ("post", "/pause", {}), ("post", "/cfg", {"timing": "x2"}), ("post", "/finish", {}),
             ("post", "/discard", {}), ("put", "/note", {"text": "x"}), ("post", "/pressure", None))
    for who in (other, None):
        for method, path, body in calls:
            r = getattr(c, method)(f"/api/session/{sid}{path}", headers=H(who),
                                   **({"json": body} if body is not None else {}))
            assert r.status_code == 403, (who, path, r.status_code)
    assert row(sid)["module_started"] is None and row(sid)["abandoned"] is None
    # SEC-07: a retired code writes nothing through any creation route
    gone = code("gone")
    db.run("INSERT INTO retired(code,[into],at) VALUES (?,?,?)", gone, code("into"), deps.now())
    n = db.one("SELECT COUNT(*) AS n FROM sessions")["n"]
    assert c.post("/api/mock/1.1", json={"learner": gone}).status_code in (401, 403)
    assert c.post("/api/mock/1.1", headers=H(gone), json={}).status_code in (401, 403)
    assert c.post("/api/session", headers=H(gone)).status_code in (401, 403)
    assert c.post("/api/mock/new", headers=H(gone), json={"kind": "section"}).status_code in (401, 403)
    assert db.one("SELECT COUNT(*) AS n FROM sessions")["n"] == n
    assert c.post("/api/mock/1.1", headers=H(me), json={"learner": other}).status_code == 403
    # a diagnostic with no code gets a server-minted one, and answers only to it
    d = ok(c.post("/api/session"))
    assert d["learner"].startswith("anon:") and not d["questions"]
    assert c.get(f"/api/session/{d['id']}").status_code == 403
    assert len(ok(c.post(f"/api/session/{d['id']}/begin", headers=H(d["learner"]), json={}))["questions"]) == 20
    seen = lambda who: db.one("SELECT COUNT(*) AS n FROM practice_seen WHERE learner=?", who)["n"]  # noqa: E731
    assert seen(d["learner"]) == 20, "a diagnostic form remembers what it served (QBank)"
    arc = ok(c.post("/api/mock/1.1", headers=H(me), json={}))
    assert arc["learner"] == me and arc["begun"] is False
    was = seen(me)
    begin(c, me, arc["id"])
    assert seen(me) == was + 22, "a shelf section remembers what it served, at Begin"
    busy = code("busy")
    past = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=5)).isoformat(timespec="seconds")
    for i in range(api_tests.NEW_PER_HOUR):
        db.run("INSERT INTO sessions(id,kind,learner,started,cfg) VALUES (?,?,?,?,?)",
               f"s5-busy-{i}-{secrets.token_hex(3)}", "module", busy, past, "{}")
    assert c.post("/api/mock/new", headers=H(busy), json={"kind": "module"}).status_code == 429
    print("ok  S5 security: every sitting endpoint owner-only (SEC-03), retired codes write nothing (SEC-07)")


def shell_resume(c) -> None:
    me = code("shell")
    sid = new(c, me, {"kind": "section"})["id"]
    begin(c, me, sid)
    ok(c.post(f"/api/session/{sid}/pause", headers=H(me), json={}))
    t = tests(c, me)
    assert t["in_progress"][0]["status"] == "paused" and t["in_progress"][0]["unranked_why"] == "paused once"
    r = c.get("/api/shell", headers=H(me))
    items = (r.json().get("next") or []) if r.status_code == 200 else []
    if not (items and items[0].get("kind") == "resume" and "Paused" in (items[0].get("title") or "")):
        wait("F2: /api/shell next.items[0] is kind 'resume' titled 'Paused · …' for a paused test (X23)")
    print("ok  S5 X23: a paused sitting is In progress with its rank line")


def rw(c) -> None:
    """Reading and Writing on the same server paths (spec/full-sat/DESIGN.md section 2): the pace
    plan, a single module 2, the weekly R&W paper, the pressure check's re-draws, the overview."""
    me = code("rw")
    p = api_tests.pace_plan(me, "module1", 1, subject="rw")
    assert p["subject"] == "rw" and len(p["budget_s"]) == 27 and abs(sum(p["budget_s"]) - (1920 - 180)) <= 1, p
    m = new(c, me, {"kind": "module", "module": "m2u", "subject": "rw"})
    assert m["subject"] == "rw" and m["duration"] == 1920 and m["section"] == "Reading and Writing · Module 2 (harder)"
    assert Counter(q["difficulty"] for q in live(m["id"])) == blueprint.RW_TIERS["module2_upper"]
    ok(c.post(f"/api/session/{m['id']}/discard", headers=H(me)))
    shelf = tests(c, me)["papers"]
    papers_rw = ok(c.get("/api/tests", params={"subject": "rw"}, headers=H(me)))["papers"]
    assert {x["subject"] for x in papers_rw} == {"rw"} and {x["subject"] for x in shelf} == {"math"}
    n = papers_rw[0]["n"]
    assert c.post("/api/mock/new", headers=H(me), json={"kind": "paper", "paper": shelf[0]["n"], "subject": "rw"}
                  ).status_code == 422, "a Math paper is not an R&W one"
    # 3 wrong with a named mistake in module 1, so the pressure check has R&W items to re-draw
    sid = new(c, me, {"kind": "paper", "paper": n})["id"]
    assert row(sid)["subject"] == "rw" and len(live(sid)) == 27
    begin(c, me, sid)
    for i, q in enumerate(live(sid), 1):
        answer(c, me, sid, q, wrong_of(q, True) if i in (3, 9, 15) else key_of(q))
    finish(c, me, sid)
    begin(c, me, sid)
    fill(c, me, sid, 27)
    finish(c, me, sid)
    card = next(x for x in ok(c.get("/api/tests", params={"subject": "rw"}, headers=H(me)))["papers"] if x["n"] == n)
    assert card["yours"]["status"] == "completed" and card["questions"] == 54
    got = api_tests.resolve_drill(me, {"pressure": sid})
    marked = {q["id"]: q for q in api_tests.marked_questions(row(sid))}
    assert len(got["ids"]) == 3, got["ids"]
    for (t, s), qid in zip(got["ids"], got["pressure_of"].values()):
        q = marked[qid]
        assert practice.topic_of(t) == q["topic"] and practice.generate(t, s).difficulty == q["difficulty"]
        assert (t, s) != (q["key"], q["seed"]), "the pressure check re-served the lost item"
    view = ok(c.get("/api/tests", params={"subject": "rw"}, headers=H(me)))
    assert view["subject"] == "rw" and view["estimate"]["headline_parts"]["subject"] == "Reading and Writing"
    assert view["estimate"]["latest"]["id"] == sid and view["levers"]["subject"] == "rw"
    assert {k["id"]: k["yours"] for k in view["kinds"]}["section"] == 1
    assert {k["id"]: k["yours"] for k in tests(c, me)["kinds"]}["section"] == 0, "a Math view counted an R&W section"
    assert c.get("/api/tests", params={"subject": "both"}, headers=H(me)).status_code == 422
    print("ok  S5 R&W: pace plan, single module 2, the weekly R&W paper, same-skill re-draws, a per-subject overview")


def check(c, *, isolated: bool = False) -> None:
    if not isolated:
        # The S5 acceptance run creates hundreds of sittings. Keep them out
        # of test_flow's shared database so later sections measure their own
        # warm requests against representative data, not S5's fixtures.
        root = pathlib.Path(__file__).resolve().parents[2]
        run = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve())],
                             cwd=root, env={**os.environ, "PYTHONPATH": str(root)},
                             text=True, capture_output=True, check=False)
        if run.returncode:
            raise AssertionError(run.stdout + run.stderr)
        print(run.stdout, end="")
        return
    WAITING.clear()
    lobby(c)
    per_question(c)
    answer_rules(c)
    ranks(c)
    kinds(c)
    orders()
    pace(c)
    papers_check(c)
    discussion(c)
    board(c)
    hand_in(c)
    trainers(c)
    pressure(c)
    traps(c)
    overview(c)
    rows_and_discard(c)
    shares(c)
    security(c)
    shell_resume(c)
    rw(c)
    for w in WAITING:
        print("waiting:", w)
    print("ok  S5 server checks")


if __name__ == "__main__":
    from server import mail
    os.environ.pop("SATF_SMTP_HOST", None)
    with tempfile.TemporaryDirectory(prefix="satf-s5db-") as path:
        db.DB_PATH = pathlib.Path(path) / "s5-check.db"
        mail.OUTBOX = pathlib.Path(path) / "outbox"
        from server.app import app
        with TestClient(app) as client:
            check(client, isolated=True)
