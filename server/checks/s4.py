"""S4 acceptance, server half: /api/bank, the drill body and every session
endpoint, as spec §3.3.8 (amended by §2.13) and practice.md P1-P25 ask.

test_flow.py runs check(c) on its scratch database. Standalone:
    PYTHONPATH=. python3 server/checks/s4.py
Learner codes start a:v2revpr. Browser items (25-35, and the browser halves
of the upgrades) belong to the page checks, not here.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import zlib
from unittest.mock import patch

from satbank.registry import generate
from server import blueprint, db, drill, practice, progress, ratings

PREFIX = "a:v2revpr"
BAD = {"answer", "answer_index", "rationale", "reasons", "steps", "mistake"}


def who(name: str) -> str:
    return PREFIX + name


def hdr(learner: str) -> dict:
    return {"X-Learner": learner}


def call(c, learner, method, path, body=None, expect=200):
    r = getattr(c, method)(path, headers=hdr(learner), **({"json": body} if body is not None else {}))
    assert r.status_code == expect, (method, path, body, r.status_code, r.text[:600])
    return r.json()


def post(c, learner, path, body=None, expect=200):
    return call(c, learner, "post", path, body if body is not None else {}, expect)


def get(c, learner, path, expect=200):
    return call(c, learner, "get", path, None, expect)


def start(c, learner, body, expect=200):
    return post(c, learner, "/api/drill", body, expect)


def served(sid: str) -> list[dict]:
    return json.loads(db.one("SELECT questions FROM sessions WHERE id=?", sid)["questions"])


def asked(sid: str) -> list[dict]:
    return [q for q in served(sid) if q.get("kind", "question") == "question"]


def cfg_of(sid: str) -> dict:
    return json.loads(db.one("SELECT cfg FROM sessions WHERE id=?", sid)["cfg"])


def full(sid: str, qid: str) -> dict:
    return next(q for q in served(sid) if q["id"] == qid)


def right(q: dict):
    return "ABCD".index(q["answer"]) if q["type"] == "mcq" else str(q["answer"])


def named(q: dict) -> int | None:
    """A named (non-filler) distractor of an MC question."""
    if q["type"] != "mcq":
        return None
    key = "ABCD".index(q["answer"])
    return next((i for i, r in enumerate(q.get("reasons") or ()) if r and i != key
                 and not (q.get("filler") or [False] * 4)[i]), None)


def wrong(q: dict):
    i = named(q)
    if i is not None:
        return i
    if q["type"] == "mcq":
        return next(i for i in range(len(q["choices"])) if i != "ABCD".index(q["answer"]))
    return "-98765"


def answer(c, learner, sid, qid, given, expect=200, **extra):
    return post(c, learner, f"/api/drill/{sid}/answer", {"question_id": qid, "answer": given, **extra}, expect)


def nxt(c, learner, sid, body=None, expect=200):
    return post(c, learner, f"/api/drill/{sid}/next", body or {}, expect)


def state(c, learner, sid):
    return get(c, learner, f"/api/drill/{sid}")


def play(c, learner, sid, choose=right, limit=60, extra=None) -> list[tuple[dict, dict]]:
    """Answer every question the set serves (cards are passed), in order."""
    out = []
    q = state(c, learner, sid)["question"]
    for _ in range(limit):
        if q is None:
            break
        if q.get("kind") in ("example", "word"):
            r = nxt(c, learner, sid)
        else:
            f = full(sid, q["id"])
            out.append((f, answer(c, learner, sid, q["id"], choose(f), **(extra or {}))))
            r = nxt(c, learner, sid)
        if r.get("done"):
            break
        q = r.get("question")
    return out


def first_attempt(sid: str, qid: str):
    return db.one("SELECT * FROM attempts WHERE session=? AND qid=? ORDER BY id LIMIT 1", sid, qid)


def math_templates() -> list[str]:
    cat = practice.catalogue()["by_topic"]
    return [t for topic, names in cat.items() if progress.deps.subject_of(topic) == "math" for t in names]


# ------------------------------------------------------------------ /api/bank

def bank_checks(c) -> dict:
    """Item 1 (as the catalogue now stands), amended item 5's levels, P6 3,
    P10 3, P11 1 and P15's subject switch."""
    learner = who("bank1")
    d = get(c, learner, "/api/bank?subject=math")
    names = math_templates()
    t = d["totals"]
    assert (t["domains"], t["skills"], t["types"]) == (4, 19, len(names)) and len(names) >= 386, t
    sk = {s["slug"]: s for x in d["domains"] for s in x["skills"]}
    assert len(sk) == 19 and sum(len(s["types"]) for s in sk.values()) == len(names)
    assert len(sk["evaluating_statistical_claims"]["types"]) == \
        len(practice.catalogue()["by_topic"]["evaluating_statistical_claims"]) >= 6
    ty = [y for s in sk.values() for y in s["types"]]
    assert all(y["name"] for y in ty) and sum(1 for y in ty if y["about"]) >= .97 * len(ty)
    assert all(set(y["tiers"]) <= {"easy", "medium", "hard"} and set(y["formats"]) <= {"mcq", "spr"} for y in ty)
    # P11 1: levels from ratings on day one, rough until 20 answers, every level used
    assert all(1 <= y["level"] <= 7 for y in ty)
    assert all(v["rough"] == (v["n"] < ratings.MEASURED) for y in ty for v in y["levels"].values())
    assert {v["level"] for y in ty for v in y["levels"].values()} == set(range(1, 8))
    for field in ("gain", "per_test", "to_strong", "fluent_n", "due_n", "ready_n", "sure_rate", "calc_split",
                  "cb_count", "labels", "by_tier", "traps", "marked", "seen", "missed"):
        assert field in sk["circles"], field
    for field in ("level", "rough", "rating", "odds", "budget_ms", "median_ms", "best_ms", "fluent", "slow_right",
                  "due", "k", "next_return", "state", "official", "desmos", "steps", "type_note", "lookalikes"):
        assert field in ty[0], field
    assert all(y["state"] == "unmet" and 0 < y["odds"] < 1 for y in ty)
    assert sum(s["cb_count"] for s in sk.values()) > 1500, "College Board's counts per skill (P13)"
    for key in ("coach", "counts", "forecast", "route", "habits", "subject"):
        assert key in d, key
    assert d["subject"] == "math" and d["route"] is None and d["gains"] is None      # P10 3: under 30 answers
    assert len(d["forecast"]) == 14
    rw = get(c, learner, "/api/bank?subject=rw")
    skills = [s for x in rw["domains"] for s in x["skills"]]
    assert rw["subject"] == "rw" and rw["bank"] is False and len(rw["domains"]) == 4 and len(skills) == 10, rw
    assert {s["name"] for s in skills if s["available"]} == {"Words in Context", "Transitions"}
    assert all(s["cb_count"] > 0 for s in skills)
    call(c, learner, "get", "/api/bank?subject=physics", expect=422)
    return d


# ------------------------------------------------------------------ the body

def body_checks(c, bank: dict) -> None:
    """Items 2-5, and P15 3 (time boxes)."""
    learner = who("body1")
    body = {"topics": ["evaluating_statistical_claims"], "formats": ["spr"]}
    pv = post(c, learner, "/api/drill/preview", body)
    assert pv["servable"] is False and "grid-in" in pv["reason"], pv
    start(c, learner, body, expect=409)
    # 3: templates only, five distinct seeds
    s = start(c, learner, {"templates": ["lin.evaluate"], "count": 5, "zone": "off"})
    play(c, learner, s["id"])
    qs = asked(s["id"])
    assert len(qs) == 5 and {q["key"] for q in qs} == {"lin.evaluate"} and len({q["seed"] for q in qs}) == 5
    # 4: tiers
    s = start(c, learner, {"topics": ["linear_functions"], "tiers": ["hard"], "count": 6})
    play(c, learner, s["id"])
    assert {x["difficulty"] for x in state(c, learner, s["id"])["served"]} == {"hard"}
    # 5 (amended): levels from ratings; unmeasured means rough
    sk = {s["slug"]: s for x in bank["domains"] for s in x["skills"]}
    topic = next(slug for slug, s in sk.items() if any(v["level"] == 1 for y in s["types"] for v in y["levels"].values()))
    measured_1 = any(v["level"] == 1 and not v["rough"] for y in sk[topic]["types"] for v in y["levels"].values())
    got = c.post("/api/drill", headers=hdr(learner), json={"topics": [topic], "levels": [1], "unmeasured": False})
    if measured_1:
        assert got.status_code == 200, got.text
    else:
        assert got.status_code == 409 and "level 1" in got.json()["detail"]["reason"], got.text
    s = start(c, learner, {"topics": [topic], "levels": [1], "unmeasured": True, "count": 3})
    for q in asked(s["id"]):
        assert ratings.level(q["key"], q["difficulty"])["level"] == 1
    call(c, learner, "post", "/api/drill", {"templates": ["no.such_type"]}, expect=422)
    call(c, learner, "post", "/api/drill", {"levels": [9], "topics": [topic]}, expect=422)
    call(c, learner, "post", "/api/drill", {"topics": ["circles"], "shoe_size": 9}, expect=422)
    # P15 3: a 15-minute box
    s = start(c, learner, {"topics": ["circles"], "box": 15})
    assert cfg_of(s["id"])["box"] == 15 and s["total"] is None and s["seconds"] == 900
    print("ok  S4 bank and body: totals, filters, levels from ratings, time boxes")


# ------------------------------------------------------------------ feedback modes

def mode_checks(c) -> None:
    """Items 7, 8 and 9: end mode, the lazy finish, retry mode."""
    learner = who("mode1")
    s = start(c, learner, {"topics": ["linear_functions"], "feedback": "end", "count": 2})
    q = s["question"]
    said = answer(c, learner, s["id"], q["id"], wrong(full(s["id"], q["id"])))
    assert not (BAD | {"correct"}) & set(said), said
    answer(c, learner, s["id"], q["id"], right(full(s["id"], q["id"])))         # re-answering is allowed
    assert db.one("SELECT COUNT(*) n FROM attempts WHERE session=?", s["id"])["n"] == 0
    q2 = nxt(c, learner, s["id"])["question"]
    answer(c, learner, s["id"], q2["id"], right(full(s["id"], q2["id"])))
    post(c, learner, f"/api/drill/{s['id']}/hint", {"question_id": q2["id"]}, expect=409)   # P2 3
    done = post(c, learner, f"/api/drill/{s['id']}/finish")
    assert db.one("SELECT COUNT(*) n FROM attempts WHERE session=?", s["id"])["n"] == 2
    assert {x["status"] for x in done["questions"]} <= {"correct", "incorrect"} and len(done["questions"]) == 2
    assert done["final"] is None                                                     # P12 2: no final round
    # 8: a timed end-mode set past its clock is finished when read
    s = start(c, learner, {"topics": ["circles"], "feedback": "end", "count": 2, "timing": "pace"})
    q = s["question"]
    answer(c, learner, s["id"], q["id"], right(full(s["id"], q["id"])))
    old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=3)).isoformat()
    db.run("UPDATE sessions SET started=? WHERE id=?", old, s["id"])
    assert state(c, learner, s["id"])["finished"]
    assert db.one("SELECT COUNT(*) n FROM attempts WHERE session=?", s["id"])["n"] == 1
    # 9: retry mode hides the key until the question is final
    s = start(c, learner, {"topics": ["linear_functions"], "formats": ["mcq"], "feedback": "retry", "count": 1})
    q = full(s["id"], s["question"]["id"])
    miss = answer(c, learner, s["id"], q["id"], named(q) if named(q) is not None else wrong(q))
    assert miss["final"] is False and miss["tries_left"] == 2 and miss["mistake"], miss
    assert not {"answer", "answer_index"} & set(miss)
    hit = answer(c, learner, s["id"], q["id"], right(q))
    assert hit["final"] is True and hit["status"] == "mixed", hit
    assert db.one("SELECT COUNT(*) n FROM tries WHERE session=? AND qid=?", s["id"], q["id"])["n"] == 1
    done = post(c, learner, f"/api/drill/{s['id']}/finish")
    assert done["mixed"] == 1 and done["right"] == 0
    print("ok  S4 end mode files at finish, lazy finish, retry keeps the key until final")


# ------------------------------------------------------------------ the session's actions

def action_checks(c) -> None:
    """Items 10-14 and 19; P23 3 and 4; the strict bodies and ownership."""
    learner = who("act1")
    s = start(c, learner, {"topics": ["linear_functions"], "count": 4, "formats": ["mcq"], "zone": "off"})
    sid, q1 = s["id"], s["question"]
    assert not BAD & set(q1)                                                       # P23 3
    # 10: skip with its time, answered later
    q2 = nxt(c, learner, sid, {"skip": True, "ms": 4000})["question"]
    assert q2["id"] != q1["id"]
    row = next(x for x in state(c, learner, sid)["served"] if x["id"] == q1["id"])
    assert row["status"] == "skipped" and row["ms"] >= 4000
    answer(c, learner, sid, q1["id"], right(full(sid, q1["id"])))
    assert next(x for x in state(c, learner, sid)["served"] if x["id"] == q1["id"])["status"] == "correct"
    # 11: time and the resume position
    before = next(x for x in state(c, learner, sid)["served"] if x["id"] == q2["id"])["ms"]
    post(c, learner, f"/api/drill/{sid}/time", {"question_id": q2["id"], "ms": 3000})
    st = state(c, learner, sid)
    assert next(x for x in st["served"] if x["id"] == q2["id"])["ms"] == before + 3000 and st["at"] == q2["id"]
    # 12: strikes persist
    post(c, learner, f"/api/drill/{sid}/strike", {"question_id": q2["id"], "choice": 2, "on": True})
    assert next(x for x in state(c, learner, sid)["served"] if x["id"] == q2["id"])["strikes"] == [2]
    # P23 4: the verdict carries the next question, held outside served until shown
    said = answer(c, learner, sid, q2["id"], right(full(sid, q2["id"])))
    held = cfg_of(sid)["pending"]["q"]
    assert said["next"] and said["next"]["id"] == held["id"] and not BAD & set(said["next"])
    assert held["id"] not in {x["id"] for x in served(sid)}
    # 13 (amended): /more same grows the set by one, same type, new seed; it drops the preview
    total = state(c, learner, sid)["total"]
    post(c, learner, f"/api/drill/{sid}/more", {"question_id": q2["id"], "axis": "same"})
    st = state(c, learner, sid)
    assert st["total"] == total + 1 and "pending" not in cfg_of(sid)
    assert not db.one("SELECT 1 FROM practice_seen WHERE learner=? AND template=? AND seed=?",
                      learner, held["key"], held["seed"]) or held["key"] == full(sid, q2["id"])["key"]
    twin = full(sid, nxt(c, learner, sid)["question"]["id"])
    first = full(sid, q2["id"])
    assert twin["key"] == first["key"] and twin["seed"] != first["seed"]
    assert all(x["id"] in {q["id"] for q in served(sid)} for x in st["served"])
    # the strict boundary: unknown fields and bad values are 422, others' sets are not yours
    post(c, learner, f"/api/drill/{sid}/answer", {"question_id": twin["id"], "answer": 0, "colour": 1}, expect=422)
    post(c, learner, f"/api/drill/{sid}/strike", {"question_id": twin["id"], "choice": 7}, expect=422)
    post(c, learner, f"/api/drill/{sid}/answer", {"question_id": "d999", "answer": 0}, expect=400)
    assert c.get(f"/api/drill/{sid}", headers=hdr(who("act2"))).status_code in (403, 404)
    assert c.post(f"/api/drill/{sid}/answer", headers=hdr(who("act2")),
                  json={"question_id": twin["id"], "answer": 0}).status_code in (403, 404)
    assert c.post("/api/drill", headers=hdr("sample:v2revprsample"), json={"topics": ["circles"]}).status_code == 403
    # 14: pause freezes the clock; answers wait; resume runs it again
    t = start(c, learner, {"topics": ["circles"], "count": 3, "timing": "pace"})
    post(c, learner, f"/api/drill/{t['id']}/pause")
    left = state(c, learner, t["id"])["seconds_left"]
    shifted = lambda text, s: (dt.datetime.fromisoformat(text) - dt.timedelta(seconds=s)).isoformat()
    row = db.one("SELECT started, cfg FROM sessions WHERE id=?", t["id"])
    cfg = json.loads(row["cfg"])
    cfg["paused_at"] = shifted(cfg["paused_at"], 3)
    db.run("UPDATE sessions SET started=?, cfg=? WHERE id=?", shifted(row["started"], 3), json.dumps(cfg), t["id"])
    assert abs(state(c, learner, t["id"])["seconds_left"] - left) <= 1
    answer(c, learner, t["id"], t["question"]["id"], 0, expect=409)
    post(c, learner, f"/api/drill/{t['id']}/resume")
    db.run("UPDATE sessions SET started=? WHERE id=?",
           shifted(db.one("SELECT started FROM sessions WHERE id=?", t["id"])["started"], 5), t["id"])
    assert state(c, learner, t["id"])["seconds_left"] <= left - 4
    # 19: Your sets
    lister = who("list1")
    a = start(c, lister, {"topics": ["circles"], "count": 3})
    answer(c, lister, a["id"], a["question"]["id"], right(full(a["id"], a["question"]["id"])))
    mine = get(c, lister, "/api/drill")
    assert [x["id"] for x in mine["active"]] == [a["id"]] and mine["active"][0]["answered"] == 1
    post(c, lister, f"/api/drill/{a['id']}/finish")
    empty = start(c, lister, {"topics": ["circles"], "count": 3})
    post(c, lister, f"/api/drill/{empty['id']}/finish")
    mine = get(c, lister, "/api/drill")
    assert not mine["active"] and [x["id"] for x in mine["recent"]] == [a["id"]]
    assert mine["recent"][0]["answered"] == 1 and mine["recent"][0]["right"] == 1
    print("ok  S4 skip, time, strikes, more, pause, previews held outside served, Your sets")


def challenge_checks(c) -> None:
    """Item 22, P2 3 (no hints) and the study-aid gate on a challenge item."""
    learner = who("chal1")
    ch = post(c, learner, "/api/challenge/start")
    sid, q = ch["id"], ch["question"]
    post(c, learner, f"/api/drill/{sid}/pause", expect=409)
    post(c, learner, f"/api/drill/{sid}/more", {"question_id": q["id"]}, expect=409)
    nxt(c, learner, sid, {"skip": True}, expect=409)
    post(c, learner, f"/api/drill/{sid}/hint", {"question_id": q["id"]}, expect=409)
    st = state(c, learner, sid)
    assert st["can"]["permalink"] is False and st["can"]["pause"] is False
    # a type rule never reaches a challenge payload (the shared study-aid rule)
    post(c, learner, "/api/notes", {"session": sid, "question_id": q["id"], "note": "check the sign", "scope": "type"})
    detail = get(c, learner, f"/api/drill/{sid}/q/{q['id']}")
    assert detail["id_note"] == "Shown after today's challenge closes" and "template" not in detail
    assert "type_note" not in detail["question"] and "type_note" not in state(c, learner, sid)["question"]
    template = full(sid, q["id"])["key"]
    s = start(c, learner, {"templates": [template], "count": 1, "zone": "off"})
    assert s["question"].get("type_note") == "check the sign"
    s = start(c, learner, {"templates": [template], "count": 1, "zone": "off", "feedback": "end"})
    assert "type_note" not in s["question"]
    call(c, learner, "post", "/api/drill", {"rematch": sid}, expect=409)       # P19 3
    print("ok  S4 challenge refuses pause, more, skip and hints, withholds ids, never shows study aids")


# ------------------------------------------------------------------ retakes, sets, notes

def share_checks(c) -> None:
    """Items 15 (amended to F6's sets) and 17, P19's Start clean, and P19 1-2."""
    owner, taker = who("own1"), who("take1")
    s = start(c, owner, {"topics": ["percentages"], "count": 3, "zone": "off", "review_mix": "off"})
    sid = s["id"]
    q1 = s["question"]
    play(c, owner, sid)
    post(c, owner, "/api/notes", {"session": sid, "question_id": q1["id"], "note": "check sign"})
    post(c, owner, f"/api/drill/{sid}/finish")
    stems = [q["stem"] for q in asked(sid)]
    again = start(c, owner, {"retake": sid})
    play(c, owner, again["id"])
    assert [q["stem"] for q in asked(again["id"])] == stems
    assert get(c, owner, f"/api/drill/{again['id']}/q/{q1['id']}")["note"] == "check sign"
    clean = start(c, owner, {"retake": sid, "clean": True})
    assert get(c, owner, f"/api/drill/{clean['id']}/q/{q1['id']}")["note"] is None
    post(c, owner, f"/api/drill/{clean['id']}/finish")
    assert get(c, owner, f"/api/drill/{clean['id']}/q/{q1['id']}")["note"] == "check sign"
    shared = post(c, owner, "/api/sets", {"kind": "set", "session": sid})
    code = shared["code"]
    got = start(c, taker, {"pool": "set", "ids": code, "show_name": True})
    play(c, taker, got["id"])
    post(c, taker, f"/api/drill/{got['id']}/finish")
    assert [q["stem"] for q in asked(got["id"])] == stems
    assert db.one("SELECT shared_from FROM sessions WHERE id=?", got["id"])["shared_from"] == code
    assert get(c, taker, f"/api/sets/{code}")["taken"] == 1
    get(c, owner, f"/api/sets/{code}/results")
    get(c, taker, f"/api/sets/{code}/results", expect=403)
    call(c, owner, "delete", f"/api/sets/{code}")
    start(c, taker, {"pool": "set", "ids": code}, expect=410)
    # P22: a twin set gives each taker the same types in order, their own seeds
    twin = post(c, owner, "/api/sets", {"kind": "set", "cfg": {
        "slots": [[q["key"], q["difficulty"], q["type"]] for q in asked(sid)], "fresh": True}})
    a = start(c, who("take2"), {"pool": "set", "ids": twin["code"]})
    b = start(c, who("take3"), {"pool": "set", "ids": twin["code"]})
    play(c, who("take2"), a["id"])
    play(c, who("take3"), b["id"])
    assert [q["key"] for q in asked(a["id"])] == [q["key"] for q in asked(b["id"])] == [q["key"] for q in asked(sid)]
    assert [q["seed"] for q in asked(a["id"])] != [q["seed"] for q in asked(b["id"])]
    # P19 1-2: a rematch serves the same types, tiers and formats in order on new seeds
    rem = start(c, owner, {"rematch": sid})
    play(c, owner, rem["id"])
    old, new = asked(sid), asked(rem["id"])
    assert [(q["key"], q["difficulty"], q["type"]) for q in new] == [(q["key"], q["difficulty"], q["type"]) for q in old]
    assert all(a["seed"] != b["seed"] for a, b in zip(old, new))
    done = post(c, owner, f"/api/drill/{rem['id']}/finish")
    assert len(done["slots"]) == len(old)
    assert {x["change"] for x in done["slots"]} <= {"fixed", "still_missing", "slipped", "held", "same_trap"}
    due = post(c, owner, f"/api/drill/{rem['id']}/rematch-due", {"days": 3})
    assert cfg_of(rem["id"])["rematch_due"] == due["rematch_due"]
    print("ok  S4 retake, notes across a retake, Start clean, sets exact and twin, rematch")


def report_check(c) -> None:
    """Item 16 (amended to R17): a report with a file is stored with the
    question's template and seed; an 11 MB file is 413."""
    import struct
    import zlib as z
    learner = who("rep1")
    s = start(c, learner, {"topics": ["circles"], "count": 1})
    q = full(s["id"], s["question"]["id"])

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", z.crc32(kind + data) & 0xffffffff)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", z.compress(b"\x00\xff\x85\x08")) + chunk(b"IEND", b""))
    data = {"data": json.dumps({"kind": "question", "source": "practice", "category": "wording",
                                "session": s["id"], "question_id": q["id"], "details": "the key looks off"})}
    r = c.post("/api/report", headers=hdr(learner), data=data, files={"files": ("shot.png", png, "image/png")})
    assert r.status_code == 200, r.text[:400]
    row = db.one("SELECT template, seed, files FROM reports WHERE learner=? ORDER BY id DESC LIMIT 1", learner)
    assert (row["template"], row["seed"]) == (q["key"], q["seed"]) and len(json.loads(row["files"] or "[]")) == 1
    big = png + b"\x00" * (11 * 1024 * 1024)
    r = c.post("/api/report", headers=hdr(learner), data=data, files={"files": ("big.png", big, "image/png")})
    assert r.status_code == 413, r.status_code
    print("ok  S4 a report from the session stores its question and file; an 11 MB file is 413")


def prefs_check(c) -> None:
    """Item 18 (amended): the builder's prefs round-trip and a builder set runs by them."""
    learner = who("pref1")
    call(c, learner, "put", "/api/me", {"prefs": {"clock": "pace", "feedback": "retry"}})
    p = get(c, learner, "/api/me")["prefs"]
    assert p["clock"] == "pace" and p["feedback"] == "retry"
    s = start(c, learner, {"topics": ["circles"], "count": 2, "source": "builder"})
    assert s["feedback"] == "retry"
    presets = [{"name": f"p{i}", "body": {"topics": ["circles"]}} for i in range(9)]
    r = c.put("/api/me", headers=hdr(learner), json={"prefs": {"practice": {"math": {"presets": presets}}}})
    assert r.status_code == 422 and "presets" in r.text, r.text[:300]                  # P15 4
    print("ok  S4 prefs round-trip into a builder set; a ninth preset is 422")


# ------------------------------------------------------------------ mistakes, guesses, grid-ins

def mistake_checks(c) -> None:
    """Items 20 and 21; P2 1, 2, 5, 7; P7 1, 2, 6, 7; P9 1, 2; P1 4; P6 1, 2."""
    learner = who("miss1")
    s = start(c, learner, {"templates": ["lin.evaluate"], "formats": ["mcq"], "count": 2, "repairs": "off",
                           "zone": "off"})
    q = full(s["id"], s["question"]["id"])
    first = answer(c, learner, s["id"], q["id"], named(q), conf="sure", ms=20000)
    a = first_attempt(s["id"], q["id"])
    assert a["conf"] == "sure" and first["confident_miss"]                               # P7 1
    assert len(json.loads(a["offered"])) <= 3 and all(isinstance(x, str) for x in json.loads(a["offered"]))  # P6 1
    trap = db.one("SELECT * FROM traps WHERE learner=? AND template='lin.evaluate' AND closed IS NULL", learner)
    assert trap
    coach = json.dumps(get(c, learner, "/api/bank")["coach"])
    assert "confident" in coach, coach[:400]
    # P2 5: a second first-try miss on the type offers Learn it step by step
    q2 = full(s["id"], nxt(c, learner, s["id"])["question"]["id"])
    second = answer(c, learner, s["id"], q2["id"], wrong(q2))
    assert "Missed this type twice" in (second.get("learn_offer") or ""), second.get("learn_offer")
    total = state(c, learner, s["id"])["total"]
    assert post(c, learner, f"/api/drill/{s['id']}/more", {"question_id": q2["id"], "ladder": True})["total"] == total + 3
    # 20 / P7 2: a guessed right keeps the trap's owed
    owed = db.one("SELECT owed FROM traps WHERE id=?", trap["id"])["owed"]
    g = start(c, learner, {"templates": ["lin.evaluate"], "formats": ["mcq"], "count": 2, "zone": "off"})
    gq = full(g["id"], g["question"]["id"])
    answer(c, learner, g["id"], gq["id"], right(gq), conf="guess")
    assert first_attempt(g["id"], gq["id"])["guess"] == 1
    assert db.one("SELECT owed FROM traps WHERE id=?", trap["id"])["owed"] == owed
    # P2 1, 2, 7: the hint ladder counts this item's own rungs and never shows the key
    hq = full(g["id"], nxt(c, learner, g["id"])["question"]["id"])
    if named(hq) is not None:
        assert hq["rungs"][0] == "strike" and hq["rungs"][-1] == "example"
        if not hq.get("steps"):
            assert hq["rungs"] == ["strike", "example"]
        h = post(c, learner, f"/api/drill/{g['id']}/hint", {"question_id": hq["id"]})
        assert h["kind"] == "strike" and h["reason"] and h["choice"] != "ABCD".index(hq["answer"])
        assert not {"answer", "answer_index"} & set(h)
        assert h["choice"] in next(x for x in state(c, learner, g["id"])["served"] if x["id"] == hq["id"])["strikes"]
        answer(c, learner, g["id"], hq["id"], right(hq))
        assert first_attempt(g["id"], hq["id"])["hints"] == 1
        assert db.one("SELECT owed FROM traps WHERE id=?", trap["id"])["owed"] == owed
    # P9 1: a clean right that pays the last owed closes it, and next_step says so
    db.run("UPDATE traps SET owed=1 WHERE id=?", trap["id"])
    f = start(c, learner, {"templates": ["lin.evaluate"], "formats": ["mcq"], "count": 1, "zone": "off"})
    fq = full(f["id"], f["question"]["id"])
    said = answer(c, learner, f["id"], fq["id"], right(fq), ms=15000)
    assert "closes" in (said.get("next_step") or ""), said.get("next_step")
    assert db.one("SELECT closed FROM traps WHERE id=?", trap["id"])["closed"], progress.offered_of(fq)
    # P9 2: then vs now, after a miss two days ago
    then_l = who("then1")
    old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=2)).isoformat()
    q0 = practice.to_question(practice.Card.of("lin.evaluate", 4242, generate("lin.evaluate", 4242, fmt="mcq"),
                                               "linear_functions"), 1)
    db.run("INSERT INTO attempts(learner,session,qid,template,seed,topic,difficulty,fmt,correct,given,reason,ms,at)"
           " VALUES (?,?,?,?,?,?,?,?,0,'1',?,160000,?)", then_l, "then-fixture", "q1", "lin.evaluate", 4242,
           "linear_functions", q0["difficulty"], "mcq", "used the slope as the intercept", old)
    t = start(c, then_l, {"templates": ["lin.evaluate"], "formats": ["mcq"], "count": 1, "zone": "off"})
    tq = full(t["id"], t["question"]["id"])
    said = answer(c, then_l, t["id"], tq["id"], right(tq), ms=30000)
    assert "B" in (said.get("then") or "") and "today: right" in said["then"], said.get("then")
    # 21: a grid-in value matched to a named mistake files that mistake
    grid_l = who("grid1")
    found = None
    for tpl in math_templates():
        if ("easy", "spr") not in blueprint.abilities().get(tpl, ()) and ("medium", "spr") not in blueprint.abilities().get(tpl, ()):
            continue
        for seed in range(40):
            try:
                it = generate(tpl, 7000 + seed)
            except Exception:
                continue
            if it.fmt != "spr":
                continue
            qq = practice.to_question(practice.Card.of(tpl, 7000 + seed, it, practice.topic_of(tpl)), 1)
            if qq.get("spr_reasons"):
                found = (tpl, 7000 + seed, qq["spr_reasons"][0])
                break
        if found:
            break
    assert found, "some grid-in names its mistakes"
    tpl, seed, (reason, value) = found
    gs = start(c, grid_l, {"item": f"{tpl}:{seed}"})
    said = answer(c, grid_l, gs["id"], gs["question"]["id"], value)
    assert said["correct"] is False and (said["mistake"] or "").lower() == reason.lower(), (said["mistake"], reason)
    label = db.one("SELECT label, reason FROM traps WHERE learner=? AND template=?", grid_l, tpl)
    assert label and reason.lower() in ((label["label"] or "") + " " + (label["reason"] or "")).lower()
    # P6 2: striking the key is graded, and the strike is filed
    st_l = who("strike1")
    k = start(c, st_l, {"topics": ["percentages"], "formats": ["mcq"], "count": 1, "zone": "off"})
    kq = full(k["id"], k["question"]["id"])
    key = "ABCD".index(kq["answer"])
    post(c, st_l, f"/api/drill/{k['id']}/strike", {"question_id": kq["id"], "choice": key, "on": True})
    said = answer(c, st_l, k["id"], kq["id"], (key + 1) % 4)
    assert said["struck_key"] is True and key in json.loads(first_attempt(k["id"], kq["id"])["struck"])
    # P1 4: Practise this trap serves the same type on a new seed offering that trap
    p = start(c, who("trap1"), {"templates": ["lin.evaluate"], "formats": ["mcq"], "count": 1, "zone": "off"})
    pq = full(p["id"], p["question"]["id"])
    answer(c, who("trap1"), p["id"], pq["id"], right(pq))
    c_norm = progress.norm(pq["reasons"][named(pq)])
    post(c, who("trap1"), f"/api/drill/{p['id']}/more", {"question_id": pq["id"], "want": pq["reasons"][named(pq)]})
    tw = full(p["id"], nxt(c, who("trap1"), p["id"])["question"]["id"])
    assert tw["key"] == pq["key"] and tw["seed"] != pq["seed"] and c_norm in progress.offered_of(tw)
    # P7 6, 7: Check alone files unrated, until the learner tags
    auto = who("auto1")
    a = start(c, auto, {"topics": ["circles"], "formats": ["mcq"], "count": 8, "zone": "off", "repairs": "off"})
    aq = full(a["id"], a["question"]["id"])
    said = answer(c, auto, a["id"], aq["id"], wrong(aq), conf="auto")
    assert first_attempt(a["id"], aq["id"])["conf"] is None and not said.get("confident_miss")
    for _ in range(6):
        aq = full(a["id"], nxt(c, auto, a["id"])["question"]["id"])
        answer(c, auto, a["id"], aq["id"], right(aq), conf="unsure")
    assert state(c, auto, a["id"])["conf_active"] is True
    aq = full(a["id"], nxt(c, auto, a["id"])["question"]["id"])
    answer(c, auto, a["id"], aq["id"], wrong(aq), conf="auto")
    assert first_attempt(a["id"], aq["id"])["conf"] == "sure"
    done = post(c, auto, f"/api/drill/{a['id']}/finish")
    cal = done["calibration"]["conf"]
    assert cal["unsure"] == {"right": 6, "wrong": 0} and cal["sure"]["wrong"] == 1, cal      # P7 5's counts
    print("ok  S4 mistakes: confident misses, guesses, hints, Learn offer, closes, then vs now, grid-in, strikes")


# ------------------------------------------------------------------ why, calculator, cover

def cause_checks(c) -> None:
    """P8 1-4, P3 4-6 (Desmos flag off), P5 1-3."""
    learner = who("why1")
    s = start(c, learner, {"templates": ["pct.change"], "formats": ["mcq"], "count": 8, "zone": "off",
                           "repairs": "off"})
    sid = s["id"]
    q = full(sid, s["question"]["id"])
    for i in range(5):
        answer(c, learner, sid, q["id"], right(q), ms=20000)
        q = full(sid, nxt(c, learner, sid)["question"]["id"])
    said = answer(c, learner, sid, q["id"], wrong(q), ms=15000)
    assert said["cause"]["kind"] == "slip" and said["cause"]["why"], said["cause"]
    assert not said.get("desmos")                                                      # P3 6: flag off
    post(c, learner, f"/api/drill/{sid}/why", {"question_id": q["id"], "kind": "misread"})
    assert first_attempt(sid, q["id"])["miss_kind"] == "misread"
    assert progress.causes(learner).get("misread", 0) >= 1 or \
        "misread" in json.dumps(progress.causes(learner)), progress.causes(learner)
    post(c, learner, f"/api/drill/{sid}/why", {"question_id": q["id"], "kind": "sneeze"}, expect=422)
    # P3 4: what was typed in Desmos while the question was open is filed with it
    q = full(sid, nxt(c, learner, sid)["question"]["id"])
    post(c, learner, f"/api/drill/{sid}/calc", {"question_id": q["id"], "exprs": ["y=2x+1", "y=3"]})
    answer(c, learner, sid, q["id"], right(q))
    assert first_attempt(sid, q["id"])["calc"] == 1
    assert get(c, learner, f"/api/drill/{sid}/q/{q['id']}")["calc"] == ["y=2x+1", "y=3"]
    done = post(c, learner, f"/api/drill/{sid}/finish")
    misses = sum(1 for x in done["questions"] if x["status"] == "incorrect")
    assert sum(done["causes"].values()) == misses                                      # P8 3
    pv = post(c, learner, "/api/drill/preview", {"topics": ["systems_of_linear_equations"], "has": ["desmos"]})
    assert pv["servable"] is False                                                     # P3 5 with the flag off
    # P8 2: two misreads in a skill underline the question sentence there
    read = who("read1")
    r = start(c, read, {"topics": ["circles"], "formats": ["mcq"], "count": 4, "zone": "off", "repairs": "off"})
    for _ in range(2):
        rq = full(r["id"], state(c, read, r["id"])["question"]["id"])
        answer(c, read, r["id"], rq["id"], wrong(rq))
        post(c, read, f"/api/drill/{r['id']}/why", {"question_id": rq["id"], "kind": "misread"})
        nxt(c, read, r["id"])
    span = state(c, read, r["id"])["question"].get("ask_span")
    assert isinstance(span, list) and len(span) == 2 and all(isinstance(x, int) for x in span), span
    # P8 4: a slip is not the crowd's top mistake
    tpl, tier = "lin.from_points", next(iter(sorted(drill._tiers_of("lin.from_points"))))
    now = progress.now()
    for i in range(25):
        db.run("INSERT INTO attempts(learner,session,qid,template,seed,topic,difficulty,fmt,correct,given,reason,"
               "norm,miss_kind,at) VALUES (?,?,?,?,?,?,?,?,0,'1',?,?,'slip',?)", who(f"crowd{i}"), "crowd", "q1",
               tpl, 50000 + i, "linear_functions", tier, "mcq", "zz s4 slip probe", "zz s4 slip probe", now)
    assert (drill.levels()[(tpl, tier)]["crowd"] or {}).get("top_mistake") != "zz s4 slip probe"
    # P5 1-3: Solve first -- a typed answer matched to the choices
    cov = who("cover1")
    v = start(c, cov, {"topics": ["percentages"], "formats": ["mcq"], "count": 8, "zone": "off", "repairs": "off",
                       "cover": "all"})
    from satbank.item import numeral
    done_kinds = set()
    q = full(v["id"], v["question"]["id"])
    for _ in range(8):
        values = [numeral(x) for x in q["choices"]]
        d = named(q)
        if all(x is not None for x in values) and d is not None and len(set(values)) == 4:
            if "distractor" not in done_kinds:
                said = answer(c, cov, v["id"], q["id"], None, own=str(q["choices"][d]).replace("−", "-"))
                assert said["cover"] == "distractor" and said["correct"] is False
                assert (said["mistake"] or "").lower() == q["reasons"][d].lower()
                assert first_attempt(v["id"], q["id"])["cover"] == 1
                done_kinds.add("distractor")
            elif "key" not in done_kinds:
                key = "ABCD".index(q["answer"])
                said = answer(c, cov, v["id"], q["id"], None, own=str(q["choices"][key]).replace("−", "-"))
                assert said["cover"] == "key" and said["correct"] is True
                done_kinds.add("key")
            elif "none" not in done_kinds:
                n_before = db.one("SELECT COUNT(*) n FROM attempts WHERE learner=?", cov)["n"]
                said = answer(c, cov, v["id"], q["id"], None, own="987654")
                assert said["cover"] == "none" and db.one("SELECT COUNT(*) n FROM attempts WHERE learner=?",
                                                           cov)["n"] == n_before
                assert db.one("SELECT n FROM tries WHERE session=? AND qid=? AND reason='cover_miss'",
                              v["id"], q["id"])["n"] == 0
                answer(c, cov, v["id"], q["id"], right(q))
                assert first_attempt(v["id"], q["id"])
                done_kinds.add("none")
            else:
                answer(c, cov, v["id"], q["id"], right(q))
        else:
            answer(c, cov, v["id"], q["id"], right(q))
        r = nxt(c, cov, v["id"])
        if r.get("done") or len(done_kinds) == 3:
            break
        q = full(v["id"], r["question"]["id"])
    assert done_kinds == {"distractor", "key", "none"}, done_kinds
    print("ok  S4 causes and the student's own, Desmos typed and flag, Solve first")


# ------------------------------------------------------------------ choosing: For me, tier mix, probe

def choosing_checks(c) -> None:
    """P11 2-5, 7, 8; P16 1-3, 5-6."""
    learner = who("zone1")
    # P11 2: a clean first try moves the item and skill ratings; a guess or a hint does not
    s = start(c, learner, {"templates": ["pct.change"], "formats": ["mcq"], "count": 3, "zone": "off"})
    sid = s["id"]
    q = full(sid, s["question"]["id"])

    def item_n(x):
        r = db.one("SELECT n FROM item_ratings WHERE template=? AND tier=?", x["key"], x["difficulty"])
        return r["n"] if r else 0

    def skill_n():
        r = db.one("SELECT n FROM skill_ratings WHERE learner=? AND topic='percentages'", learner)
        return r["n"] if r else 0
    n0, s0 = item_n(q), skill_n()
    answer(c, learner, sid, q["id"], right(q))
    assert item_n(q) == n0 + 1 and skill_n() == s0 + 1
    for extra in ({"conf": "guess"}, {"hints": 1}):
        q = full(sid, nxt(c, learner, sid)["question"]["id"])
        n0, s0 = item_n(q), skill_n()
        answer(c, learner, sid, q["id"], right(q), **extra)
        assert item_n(q) == n0 and skill_n() == s0, extra
    # P11 3: a placed skill aims each question at the zone's odds
    placed = who("zone2")
    db.run("INSERT OR REPLACE INTO skill_ratings(learner,topic,rating,n,seed) VALUES (?,?,?,?,?)",
           placed, "circles", 1100.0, 8, "none")
    z = start(c, placed, {"topics": ["circles"], "zone": "stretch", "count": 5})
    play(c, placed, z["id"])
    rated = {(r["template"], r["tier"]): r["rating"] for r in db.rows("SELECT template,tier,rating FROM item_ratings")}
    pairs = [(t, tier) for t in practice.catalogue()["by_topic"]["circles"] for tier in drill._tiers_of(t)]
    for q in asked(z["id"])[:5]:
        skill = db.one("SELECT rating FROM skill_ratings WHERE learner=? AND topic='circles'", placed)["rating"]
        best = min(abs(ratings.expected(rated.get(p, ratings.TIER_PRIOR[p[1]]), skill) - .70) for p in pairs)
        assert abs(q["odds"] - .70) <= max(.15, best + .25), (q["odds"], best)
    # P11 4: the harder module's mix
    mix = who("zone3")
    m = start(c, mix, {"topics": ["linear_functions", "circles"], "tier_mix": "module2_upper", "count": 22})
    assert sorted(cfg_of(m["id"])["plan"]) == sorted(["easy"] * 3 + ["medium"] * 8 + ["hard"] * 11)
    play(c, mix, m["id"])
    tiers = [q["difficulty"] for q in asked(m["id"])]
    assert (tiers.count("easy"), tiers.count("medium"), tiers.count("hard")) == (3, 8, 11), tiers
    # P11 5: Check my level is end mode and steps up after a right
    probe = who("zone4")
    p = start(c, probe, {"source": "probe", "topics": ["circles"], "count": 8})
    assert cfg_of(p["id"])["feedback"] == "end"
    q = full(p["id"], p["question"]["id"])
    answer(c, probe, p["id"], q["id"], right(q))
    q2 = full(p["id"], nxt(c, probe, p["id"])["question"]["id"])
    assert drill.TIERS.index(q2["difficulty"]) > drill.TIERS.index(q["difficulty"]), (q["difficulty"], q2["difficulty"])
    # P11 7: a new learner's default set is the test's mix until placed
    fresh = who("zone5")
    f = start(c, fresh, {"topics": ["linear_functions", "circles", "percentages"], "count": 10})
    assert f["zone"] == "stretch"
    play(c, fresh, f["id"])
    qs = asked(f["id"])
    assert sum(q["difficulty"] in ("medium", "hard") for q in qs) >= 3
    assert any((q.get("zone") or "").startswith("For me starts after 8 answers here") for q in qs)
    # P11 8: a 700 starter's skill ratings are seeded from the score
    high = who("zone6")
    call(c, high, "put", "/api/me", {"current": 700})
    h = start(c, high, {"topics": ["circles"], "count": 1})
    row = db.one("SELECT rating, seed FROM skill_ratings WHERE learner=? AND topic='circles'", high)
    assert row["seed"] == "score" and round(row["rating"]) == 1304, dict(row)
    for topic in ("linear_functions", "percentages"):
        db.run("INSERT OR REPLACE INTO skill_ratings(learner,topic,rating,n,seed) VALUES (?,?,1304,8,'score')",
               high, topic)
    h = start(c, high, {"topics": ["linear_functions", "percentages"], "count": 10})
    play(c, high, h["id"])
    assert sum(q["difficulty"] == "hard" for q in asked(h["id"])) >= 2
    # P16 1: tier budgets where the crowd is thin
    thin = next(t for t in math_templates() if {"medium", "hard"} <= drill._tiers_of(t)
                and all(drill.levels().get((t, x), {}).get("n", 0) < 20 for x in ("medium", "hard")))
    assert drill.budget_ms(thin, "medium") == 95_000 and drill.budget_ms(thin, "hard") == 126_000
    # P16 2: the pace clock is the plan's budgets, and a repair adds its own
    pace = who("pace1")
    t = start(c, pace, {"topics": ["linear_functions"], "count": 10, "timing": "pace", "zone": "off"})
    cfg = cfg_of(t["id"])
    planned = sum(drill.TIER_BUDGET["math"][x] for x in cfg["plan"])
    moved = sum(e["delta_ms"] for e in cfg["clock_log"] if e["why"] != "plan") // 1000
    assert cfg["seconds"] == math.ceil(planned / 60_000) * 60 + moved, (cfg["seconds"], planned, cfg["clock_log"])
    assert abs(t["seconds_left"] - cfg["seconds"]) <= 1
    q = full(t["id"], t["question"]["id"])
    answer(c, pace, t["id"], q["id"], wrong(q))
    before = cfg_of(t["id"])["seconds"]
    rep = full(t["id"], nxt(c, pace, t["id"])["question"]["id"])
    assert rep["repair"] and cfg_of(t["id"])["seconds"] == before + math.ceil(rep["budget_ms"] / 1000)
    assert cfg_of(t["id"])["clock_log"][-1]["why"] == "repair"
    # P16 3, 5, 6: fluent, a new best, a time sink
    fl = who("flu1")
    tpl = "lin.evaluate"
    s = start(c, fl, {"templates": [tpl], "formats": ["mcq"], "count": 3, "zone": "off", "repairs": "off"})
    q = full(s["id"], s["question"]["id"])
    answer(c, fl, s["id"], q["id"], right(q), ms=30000)
    q = full(s["id"], nxt(c, fl, s["id"])["question"]["id"])
    said = answer(c, fl, s["id"], q["id"], right(q), ms=10000)
    assert "New best on this type" in (said.get("best") or {}).get("text", ""), said.get("best")
    q = full(s["id"], nxt(c, fl, s["id"])["question"]["id"])
    answer(c, fl, s["id"], q["id"], wrong(q), ms=5 * q["budget_ms"])
    done = post(c, fl, f"/api/drill/{s['id']}/finish")
    assert len(done["time_sinks"]) == 1 and done["next_set"]["count"] >= 1
    # the summary's blocks: what this set moved (P10), its head line (P9), habits (P6), the Time card (P16)
    assert done["moved"] and done["moved"][0]["rate_after"] is not None and isinstance(done["habits"], list)
    assert done["head"]["closed"] == 0 and done["time"]["over"] >= 1
    assert next(y for x in get(c, fl, "/api/bank")["domains"] for sk in x["skills"] for y in sk["types"]
                if y["template"] == tpl)["fluent"] is True
    nxt_set = start(c, fl, done["next_set"]["body"])                                  # the summary's next set
    assert asked(nxt_set["id"])[0]["key"] == tpl and nxt_set["total"] == done["next_set"]["count"]
    print("ok  S4 ratings move on clean first tries, For me zones, tier mix, probe, budgets, pace clock, fluency")


# ------------------------------------------------------------------ retrieval, final round, pools

def retrieval_checks(c) -> None:
    """P12 1, 3, 4, 5; P16 7; P21 1, 3, 5, 6; P14 3."""
    learner = who("fin1")
    s = start(c, learner, {"topics": ["linear_functions", "percentages"], "count": 10, "repairs": "off",
                           "zone": "off", "review_mix": "off", "timing": "pace"})
    sid = s["id"]
    missed = []
    q = full(sid, s["question"]["id"])
    for i in range(10):
        if len(missed) < 2 and q["key"] not in {m["key"] for m in missed}:
            answer(c, learner, sid, q["id"], wrong(q))
            missed.append(q)
        else:
            answer(c, learner, sid, q["id"], right(q))
        r = nxt(c, learner, sid)
        if r.get("done"):
            break
        q = full(sid, r["question"]["id"])
    st = state(c, learner, sid)
    assert st["final"]["offer"] and st["final"]["n"] == 2, st["final"]
    seconds = cfg_of(sid)["seconds"]
    fin = post(c, learner, f"/api/drill/{sid}/final")
    assert fin["total"] == 12
    fq = full(sid, fin["question"]["id"])
    assert fq["final"] and fq["why"]["kind"] == "final" and fq["key"] == missed[0]["key"] and fq["seed"] != missed[0]["seed"]
    assert cfg_of(sid)["seconds"] == seconds + math.ceil(fq["budget_ms"] / 1000)       # P16 7
    answer(c, learner, sid, fq["id"], right(fq))
    fq2 = full(sid, nxt(c, learner, sid)["question"]["id"])
    assert fq2["key"] == missed[1]["key"] and fq2["why"]["kind"] == "final"
    # P12 3: review slots come from T3's fading types, never first or second
    rev = who("rev1")
    old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=3)).isoformat()
    circles = practice.catalogue()["by_topic"]["circles"][:3]
    for i, tpl in enumerate(circles):
        tier = sorted(drill._tiers_of(tpl), key=drill.TIERS.index)[0]
        db.run("INSERT INTO attempts(learner,session,qid,template,seed,topic,difficulty,fmt,correct,given,at)"
               " VALUES (?,?,?,?,?,?,?,?,1,'0',?)", rev, "rev-fixture", f"q{i}", tpl, 60000 + i, "circles", tier,
               "mcq", old)
    fading = progress.warmup_candidates(rev)["fading"]
    assert {f["template"] for f in fading} >= set(circles)
    pv = post(c, rev, "/api/drill/preview", {"pool": "review"})
    assert pv["pools"]["review"] == len(fading) and pv["types"] == len(fading)        # P12 5
    r = start(c, rev, {"topics": ["circles"], "count": 10})
    play(c, rev, r["id"])
    due = [i for i, q in enumerate(asked(r["id"]), 1) if (q.get("why") or {}).get("kind") == "due"]
    assert len(due) >= 2 and min(due) >= 3, due
    # P12 4: a flag 3 days old with no right since comes back as 'marked'
    flag = who("flag1")
    q0 = practice.to_question(practice.Card.of("pct.change", 81, generate("pct.change", 81), "percentages"), 1)
    db.run("INSERT INTO sessions(id,kind,learner,started,finished,questions) VALUES (?,?,?,?,?,?)",
           "flag-fixture", "drill", flag, old, old, json.dumps([{**q0, "id": "d001"}]))
    db.run("INSERT INTO flags(learner,session,qid,template,seed,topic,at) VALUES (?,?,?,?,?,?,?)",
           flag, "flag-fixture", "d001", "pct.change", 81, "percentages", old)
    assert any(m["template"] == "pct.change" for m in progress.warmup_candidates(flag)["marked"])
    # P21 3, 1, 5: Marked is exact by default, Saved gives twins
    m = start(c, flag, {"pool": "marked"})
    assert [[q["key"], q["seed"]] for q in asked(m["id"])] == [["pct.change", 81]]
    db.run("INSERT INTO saved(learner,template,seed,topic,at) VALUES (?,?,?,?,?)", flag, "lin.evaluate", 91,
           "linear_functions", old)
    sv = start(c, flag, {"pool": "saved", "count": 2})
    assert all(q["key"] == "lin.evaluate" and q["seed"] != 91 for q in asked(sv["id"]))
    pools = post(c, flag, "/api/drill/preview", {"topics": ["circles"]})["pools"]
    whole = post(c, flag, "/api/drill/preview", {})["pools"]
    assert whole["marked"] == 1 and whole["saved"] == 1 and pools["marked"] == 0
    # P21 2, 6: your rule for a type shows on fresh questions of it, costs no help, and the pref hides it
    post(c, flag, "/api/notes", {"session": m["id"], "question_id": asked(m["id"])[0]["id"],
                                 "note": "check the sign", "scope": "type"})
    ty = start(c, flag, {"templates": ["pct.change"], "count": 1, "zone": "off"})
    q = ty["question"]
    assert get(c, flag, f"/api/drill/{ty['id']}/q/{q['id']}")["question"]["type_note"] == "check the sign"
    answer(c, flag, ty["id"], q["id"], right(full(ty["id"], q["id"])))
    assert first_attempt(ty["id"], q["id"])["hints"] == 0
    call(c, flag, "put", "/api/me", {"prefs": {"type_rules": False}})
    off = start(c, flag, {"templates": ["pct.change"], "count": 1, "zone": "off"})
    assert "type_note" not in get(c, flag, f"/api/drill/{off['id']}/q/{off['question']['id']}")["question"]
    # P14 3: Finish this skill starts with the open mistake, at most 30, as the preview counts
    fin_l = who("finish1")
    tpl = practice.catalogue()["by_topic"]["circles"][2]
    q0 = practice.to_question(practice.Card.of(tpl, 33, generate(tpl, 33), "circles"), 1)
    progress.record_trap(fin_l, q0, next(r for r in q0["reasons"] if r) if q0["type"] == "mcq" else "x", progress.now())
    body = {"source": "finish", "topics": ["circles"]}
    pv = post(c, fin_l, "/api/drill/preview", body)
    f = start(c, fin_l, body)
    assert asked(f["id"])[0]["key"] == tpl and f["total"] <= 30 and pv["count"] == f["total"]
    done = post(c, fin_l, f"/api/drill/{f['id']}/finish")
    circles_n = len(practice.catalogue()["by_topic"]["circles"])
    assert done["finish"] == {"topic": "circles", "ready": 0, "was": 0, "types": circles_n, "to_go": circles_n}
    print("ok  S4 final round and its clock, review slots, marked and saved pools, type rules, Finish this skill")


# ------------------------------------------------------------------ official twins, mix-up, axes, voids

def twin_checks(c) -> None:
    """P13 1, 2, 4, 5, 6; P17 1-3; P18 1-4; P20 2; P25."""
    learner = who("cb1")
    known = drill._official_map()["23c5fcce"]
    s = start(c, learner, {"pool": "official", "ids": ["23c5fcce"], "each": 3})
    texts = [json.dumps(s)]
    for f, said in play(c, learner, s["id"]):
        texts.append(json.dumps(said))
    qs = asked(s["id"])
    # 23c5fcce's key-file tier (easy) is not one circles.arc serves: the nearest one it does
    near = min(drill._tiers_of(known["template"]),
               key=lambda d: (abs(drill.TIERS.index(d) - drill.TIERS.index(known["tier"])), d))
    assert len(qs) == 3 and all(q["key"] == known["template"] and q["difficulty"] == near
                                and q["why"]["kind"] == "official" for q in qs), [(q["key"], q["difficulty"]) for q in qs]
    fits = next(k for k, e in sorted(drill._official_map().items()) if e["tier"] in drill._tiers_of(e["template"]))
    e = drill._official_map()[fits]
    exact = start(c, learner, {"pool": "official", "ids": [fits], "each": 3})
    play(c, learner, exact["id"])
    assert all(q["key"] == e["template"] and q["difficulty"] == e["tier"] for q in asked(exact["id"]))
    params, stems = drill._pinned()
    assert all((q["key"], drill._frozen(generate(q["key"], q["seed"]).params)) not in params for q in qs)
    repro = known["stem"]
    blob = " ".join(texts).lower()
    shared = [repro[i:i + 40] for i in range(0, max(1, len(repro) - 40), 7) if repro[i:i + 40] in blob]
    assert not shared, shared[:2]
    post(c, learner, f"/api/drill/{s['id']}/finish")
    brought = get(c, learner, "/api/drill")["official"]
    assert brought[0]["cb_id"] == "23c5fcce" and brought[0]["twins"] == 3
    names = practice.catalogue()["by_topic"]
    every = [t for ts in names.values() for t in ts]
    pv = post(c, learner, "/api/drill/preview", {"has": ["official"], "topics": list(names)})
    official = {e["template"] for e in drill._official_map().values()}
    assert pv["types"] == len(official & set(every)) > 0
    index = {k: v for k, v in drill.cb_index().items() if v["subject"] == "math" and k not in drill._official_map()}
    sample = sorted(index, key=lambda k: zlib.crc32(k.encode()))[:20]
    for cbid in sample:
        got = start(c, who("cb2"), {"pool": "official", "ids": [cbid], "each": 3})
        qs = asked(got["id"])[:1] + [full(got["id"], nxt(c, who("cb2"), got["id"], {"skip": True})["question"]["id"])]
        x = index[cbid]
        assert all(q["topic"] == x["topic"] and q["difficulty"] == x["tier"] for q in qs), (cbid, x, [(q["key"], q["difficulty"], q.get("why"), q.get("repair")) for q in qs], [drill._tiers_of(t) for t in drill._index_twins(cbid, 3)])
        assert "Close twin" in qs[0]["why"]["detail"] and "Not in our map" not in json.dumps(got)
        assert got["total"] == 3
    rw = next(k for k, v in drill.cb_index().items() if v["subject"] == "rw")
    assert start(c, learner, {"pool": "official", "ids": [rw]}, expect=409)["detail"]["reason"] == "rw_bank_pending"
    # P17: Mix-up interleaves look-alikes, never one type twice in a row, and hides the skill until Check
    assert "pct.change" not in blueprint.lookalikes("pct.change")
    mx = who("mix1")
    m = start(c, mx, {"templates": ["pct.change"], "order": "mixup", "count": 8})
    assert state(c, mx, m["id"])["hide_skill"] is True and "type_name" not in m["question"]
    play(c, mx, m["id"])
    keys = [q["key"] for q in asked(m["id"])]
    allowed = set(blueprint.lookalikes("pct.change")) | {"pct.change"}
    assert len(set(keys)) >= 3 and set(keys) <= allowed and all(a != b for a, b in zip(keys, keys[1:])), keys
    # P18: the axes
    ax = who("axis1")
    grid_t = next(t for t in math_templates() if "grid" in blueprint.kinds()[t].get("axes", ())
                  and any(f == "mcq" for _, f in blueprint.abilities()[t]))
    g = start(c, ax, {"templates": [grid_t], "formats": ["mcq"], "count": 1, "zone": "off"})
    gq = full(g["id"], g["question"]["id"])
    answer(c, ax, g["id"], gq["id"], right(gq))
    post(c, ax, f"/api/drill/{g['id']}/more", {"question_id": gq["id"], "axis": "grid"})
    gt = full(g["id"], nxt(c, ax, g["id"])["question"]["id"])
    assert gt["key"] == gq["key"] and gt["type"] == "spr" and gt["seed"] != gq["seed"]
    ask_t = next((t for t in math_templates() if "ask" in blueprint.kinds()[t].get("axes", ())), None)
    if ask_t:
        a = start(c, ax, {"templates": [ask_t], "count": 1, "zone": "off"})
        aq = full(a["id"], a["question"]["id"])
        answer(c, ax, a["id"], aq["id"], right(aq))
        post(c, ax, f"/api/drill/{a['id']}/more", {"question_id": aq["id"], "axis": "ask"})
        at = full(a["id"], nxt(c, ax, a["id"])["question"]["id"])
        # the same setup (template and seed, so the same params), another question
        assert at["key"] == aq["key"] and at["seed"] == aq["seed"] and at["stem"] != aq["stem"]
    no_ask = next(t for t in math_templates() if "ask" not in blueprint.kinds()[t].get("axes", ()))
    n = start(c, ax, {"templates": [no_ask], "count": 1, "zone": "off"})
    nq = full(n["id"], n["question"]["id"])
    answer(c, ax, n["id"], nq["id"], right(nq))
    post(c, ax, f"/api/drill/{n['id']}/more", {"question_id": nq["id"], "axis": "ask"}, expect=409)
    one_tier = next((t for t in math_templates() if drill._tiers_of(t) == {"medium"}
                     and blueprint.siblings(t, 1) and blueprint.siblings(t, 1)[0] != t), None)
    if one_tier:
        h = start(c, ax, {"templates": [one_tier], "count": 1, "zone": "off"})
        hq = full(h["id"], h["question"]["id"])
        answer(c, ax, h["id"], hq["id"], right(hq))
        post(c, ax, f"/api/drill/{h['id']}/more", {"question_id": hq["id"], "axis": "harder"})
        up = full(h["id"], nxt(c, ax, h["id"])["question"]["id"])
        assert up["key"] == blueprint.siblings(one_tier, 1)[0] and up["difficulty"] == "hard", (up["key"], up["difficulty"])
    assert sum(1 for t in math_templates() if blueprint.siblings(t, 1) or blueprint.siblings(t, -1)) >= 150
    # P20 2: Twins of these (2)
    tw = who("twins1")
    t = start(c, tw, {"topics": ["circles"], "count": 2, "zone": "off"})
    play(c, tw, t["id"])
    cells = asked(t["id"])
    total = state(c, tw, t["id"])["total"]
    for q in cells:
        post(c, tw, f"/api/drill/{t['id']}/more", {"question_id": q["id"], "axis": "same"})
    assert state(c, tw, t["id"])["total"] == total + 2
    new = [full(t["id"], nxt(c, tw, t["id"])["question"]["id"])]
    answer(c, tw, t["id"], new[0]["id"], right(new[0]))
    new.append(full(t["id"], nxt(c, tw, t["id"])["question"]["id"]))
    assert [q["key"] for q in new] == [q["key"] for q in cells]
    # P25: a broken question is voided and replaced; the set keeps its length
    vd = who("void1")
    v = start(c, vd, {"topics": ["circles"], "count": 3, "zone": "off"})
    vq = full(v["id"], v["question"]["id"])
    total = state(c, vd, v["id"])["total"]
    real = drill._removed
    with patch.object(drill, "_removed", lambda t, s: (t, s) == (vq["key"], vq["seed"]) or real(t, s)):
        post(c, vd, f"/api/drill/{v['id']}/more", {"question_id": vq["id"], "axis": "same"})
        rep = full(v["id"], nxt(c, vd, v["id"], {"skip": True})["question"]["id"])
        st = state(c, vd, v["id"])
        assert rep["key"] == vq["key"] and rep["seed"] != vq["seed"] and st["total"] == total
        assert next(x for x in st["served"] if x["id"] == vq["id"])["status"] == "voided"
    print("ok  S4 official twins (exact and index), no official copies, Mix-up, axes, Twins of these, voids")


# ------------------------------------------------------------------ Learn this type, worked first, words

def learn_checks(c) -> None:
    """P2 4, 6; P6 3, 4; P12's word cards when Words (S9) serves them."""
    learner = who("learn1")
    t = "lin.from_points"
    s = start(c, learner, {"source": "learn", "templates": [t], "example": True, "count": 3})
    ex = full(s["id"], s["question"]["id"])
    assert ex["kind"] == "example" and ex["seed"] >= 900_000, {k: ex.get(k) for k in ("kind", "seed", "key", "id")}
    q1 = full(s["id"], nxt(c, learner, s["id"])["question"]["id"])
    assert q1["kind"] == "question" and "with help" in q1["why"]["detail"]
    answer(c, learner, s["id"], q1["id"], right(q1), hints=1)
    a = first_attempt(s["id"], q1["id"])
    assert a["hints"] == 1 and a["guess"] == 0
    assert not db.one("SELECT 1 FROM attempts WHERE session=? AND seed>=900000", s["id"])
    q2 = full(s["id"], nxt(c, learner, s["id"])["question"]["id"])
    answer(c, learner, s["id"], q2["id"], right(q2))
    q3 = full(s["id"], nxt(c, learner, s["id"])["question"]["id"])
    if len(drill._tiers_of(t)) > 1 or blueprint.siblings(t, 1):
        assert drill.TIERS.index(q3["difficulty"]) > drill.TIERS.index(q1["difficulty"]), (q1["difficulty"], q3["difficulty"])
    # P2 6: worked_first shows at most one example a skill
    wf = who("learn2")
    w = start(c, wf, {"topics": ["circles", "percentages"], "count": 5, "worked_first": True})
    play(c, wf, w["id"])
    examples = [q for q in served(w["id"]) if q.get("kind") == "example"]
    assert 1 <= len(examples) <= 2
    t_ = start(c, who("learn3"), {"topics": ["circles"], "count": 3, "worked_first": True, "timing": "pace"})
    assert all(q.get("kind") != "example" for q in served(t_["id"]))
    # P6 3, 4: habits in the bank, and a habit drill offers them
    h = who("habit1")
    hs = start(c, h, {"topics": ["percentages", "linear_functions"], "count": 5, "formats": ["mcq"], "zone": "off"})
    play(c, h, hs["id"], choose=wrong)
    rows = get(c, h, "/api/bank")["habits"]
    assert rows and all({"id", "caught", "dodged", "offered", "open", "skills"} <= set(x) for x in rows)
    from server import habits
    hd = start(c, h, {"source": "habit", "habits": ["whole_part", "sign"], "count": 6, "formats": ["mcq"]})
    got = play(c, h, hd["id"])
    assert len(asked(hd["id"])) == 6
    for q in asked(hd["id"]):
        fams = {(habits.family(r) or {}).get("id") for r in q["reasons"] if r}
        assert fams & {"whole_part", "sign"}, (q["key"], fams)
    # P12: word cards at the breaks, when Words serves due items (S9)
    if drill.deps.part("words", "due_items") and drill.deps.part("words", "grade_item"):
        wl = who("words1")
        ws = start(c, wl, {"topics": ["circles"], "count": 10, "words_mix": 2, "zone": "off"})
        play(c, wl, ws["id"])
        kinds = [q.get("kind", "question") for q in served(ws["id"])]
        if "word" in kinds:
            assert kinds.count("word") <= 2 and kinds.index("word") == 5
            assert state(c, wl, ws["id"])["total"] == 10
    else:
        print("..  S4 word cards wait for S9's words.due_items / grade_item")
    print("ok  S4 Learn this type, worked first, habits, word cards")


def check(c) -> None:
    b = bank_checks(c)
    body_checks(c, b)
    mode_checks(c)
    action_checks(c)
    challenge_checks(c)
    share_checks(c)
    report_check(c)
    prefs_check(c)
    mistake_checks(c)
    cause_checks(c)
    choosing_checks(c)
    retrieval_checks(c)
    twin_checks(c)
    learn_checks(c)
    print("ok  S4 Practice server checks")


if __name__ == "__main__":
    import os
    import pathlib
    import tempfile
    os.environ.pop("SATF_SMTP_HOST", None)
    with tempfile.TemporaryDirectory(prefix="satf-s4-") as path:
        db.DB_PATH = pathlib.Path(path) / "s4-check.db"      # never the developer's database
        from server import reports
        reports.FILES = pathlib.Path(path) / "reports"
        from fastapi.testclient import TestClient
        from server.app import app
        with TestClient(app) as client:
            check(client)
