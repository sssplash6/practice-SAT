"""F4 data-layer acceptance. Run with PYTHONPATH=. python3 server/checks/f4.py."""

from __future__ import annotations

import datetime as dt
import json
import math
import pathlib
import sqlite3
import tempfile
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from server import db, deps, estimate, prefs, progress, ratings, satdates, scoring
from server.app import app

TODAY = dt.datetime.now(dt.timezone.utc).date()


def add(table: str, **values):
    cols = ",".join(f'"{c}"' for c in values)
    return db.run(f"INSERT INTO {table} ({cols}) VALUES ({','.join('?' for _ in values)})", *values.values())


def at(day: dt.date | str, hour: int = 12) -> str:
    return f"{day}T{hour:02d}:00:00+00:00"


def q(seed: int, reasons=None, key="lin.evaluate", topic="linear_functions", answer="A") -> dict:
    return {"id": f"q{seed}", "key": key, "seed": seed, "topic": topic,
            "difficulty": "easy", "type": "mcq", "answer": answer,
            "reasons": reasons or ["", "used 10 instead of 20", "used 30 instead of 40", "near-miss arithmetic slip"],
            "stem": f"Find x in question {seed}"}


def spr(seed: int, spr_reasons=(), key="lin.grid", topic="linear_functions", answer="12") -> dict:
    return {"id": f"s{seed}", "key": key, "seed": seed, "topic": topic, "difficulty": "medium",
            "type": "spr", "answer": answer, "spr_reasons": [list(r) for r in spr_reasons], "stem": f"Grid {seed}"}


def real(template: str, seed: int, qid: str | None = None) -> dict:
    from satbank.registry import generate, topic_of
    it = generate(template, seed)
    return {"id": qid or f"{template}:{seed}", "key": template, "seed": seed, "topic": topic_of(template),
            "difficulty": it.difficulty, "type": it.fmt, "answer": it.answer, "reasons": list(it.reasons),
            "spr_reasons": [[m.reason, str(m.value)] for m in getattr(it, "spr_mistakes", ())],
            "stem": it.stem, "domain": "Algebra"}


def ans(item: dict, right: bool = True):
    """What a student would send: the key's index (MC) or its value (grid-in)."""
    if item["type"] == "mcq":
        k = "ABCD".index(item["answer"])
        return k if right else (k + 1) % 4
    return item["answer"] if right else "-999"


def trap(learner: str, **where):
    sql = " AND ".join(f"{k}=?" for k in where)
    return db.one(f"SELECT * FROM traps WHERE learner=?{' AND ' + sql if sql else ''}", learner, *where.values())


def checks():
    for table in ("classes", "members", "assignments", "attachments"):
        assert not db.one("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", table)
    assert "assignment" not in {r["name"] for r in db.rows("PRAGMA table_info(sessions)")}
    try:
        with db.transaction():
            db.run("INSERT INTO learners(id,created) VALUES (?,?)", "a:f4rollback", progress.now())
            raise RuntimeError("simulate a failed multi-field write")
    except RuntimeError:
        pass
    assert not db.one("SELECT 1 FROM learners WHERE id=?", "a:f4rollback")
    assert progress.norm("Used 10 instead of 20") == progress.norm("Used 30 instead of 40")
    progress._self_check()          # norm on the bank's own items, trap kinds, T3 intervals
    p = "a:f4progress"
    start = "2026-01-01T12:00:00+00:00"
    progress.record(p, None, q(1), 1, when=start)
    progress.record(p, None, q(2), 2, when="2026-01-02T12:00:00+00:00")
    traps = db.rows("SELECT * FROM traps WHERE learner=?", p)
    assert len(traps) == 1 and isinstance(traps[0]["id"], int) and traps[0]["hits"] == 2
    assert traps[0]["reason"] == "used 30 instead of 40"
    before = progress.topic_mastery(p, "linear_functions")
    progress.record(p, None, q(2), 0, when="2026-01-03T12:00:00+00:00")
    assert progress.topic_mastery(p, "linear_functions") == before
    assert db.one("SELECT repeat FROM attempts WHERE learner=? ORDER BY id DESC LIMIT 1", p)["repeat"] == 1
    for seed, day in ((3, "2026-01-03"), (4, "2026-01-04")):
        progress.record(p, None, q(seed), 0, when=day + "T12:00:00+00:00")
    t = trap(p)
    assert t["closed_how"] == "fixed" and t["due"] == "2026-01-07" and t["checks"] == 0
    events = [r["event"] for r in db.rows("SELECT event FROM trap_log WHERE learner=? ORDER BY id", p)]
    assert events == ["open", "miss", "miss", "pip", "pip", "fixed"], events
    progress.record(p, None, q(40), 0, when="2026-01-05T12:00:00+00:00")
    early = db.one("SELECT due,checks FROM traps WHERE learner=?", p)
    assert (early["due"], early["checks"]) == ("2026-01-07", 0)
    for seed, day, due, stage in ((5, "2026-01-07", "2026-01-14", 1),
                                  (6, "2026-01-14", "2026-02-03", 2),
                                  (7, "2026-02-03", None, 3)):
        progress.record(p, None, q(seed), 0, when=day + "T12:00:00+00:00")
        t = trap(p)
        assert (t["due"], t["checks"]) == (due, stage)
    progress.record(p, None, q(8), 1, when="2026-02-17T12:00:00+00:00")
    assert db.one("SELECT relapses,closed FROM traps WHERE learner=?", p)["relapses"] == 1
    progress.record(p, None, q(9), 0, flagged=True)
    unsure = db.one("SELECT * FROM traps WHERE learner=? AND norm='~unsure'", p)
    assert unsure and unsure["owed"] == 1

    # G3 check 2 / R45: a named trap closes only on items that offered it again
    g = "a:f4g3"
    named = ["", "left out the constant term", "added the coefficient", "near-miss arithmetic slip"]
    other = ["", "multiplied by the input", "added the coefficient", "near-miss arithmetic slip"]
    progress.record(g, None, q(1, named), 1)
    assert trap(g)["owed"] == 2
    for seed in (2, 3):
        got = progress.record(g, None, q(seed, other), 0)
        assert got["not_offered"] and trap(g)["owed"] == 2
    assert json.loads(db.one("SELECT offered FROM attempts WHERE learner=? ORDER BY id DESC", g)["offered"]) == \
        ["multiplied by the input", "added the coefficient"]
    progress.record(g, None, q(4, named), 0)
    assert trap(g)["owed"] == 1
    # G3 check 7: every kind reaches Fixed
    k = "a:f4kinds"
    progress.record(k, None, q(1), 0, flagged=True)                       # an unsure right owes 1
    progress.record(k, None, q(2, other), 0)
    assert trap(k, norm="~unsure")["closed_how"] == "fixed"
    progress.log_mistake(k, "lin.slope", "linear_functions", note="I don't know", source="outside", unsure=True)
    t = trap(k, template="lin.slope")
    assert (t["norm"], t["owed"], t["label"]) == ("~unsure", 1, "Unsure"), dict(t)
    progress.record(k, None, q(3, other, key="lin.slope"), 0)
    assert trap(k, template="lin.slope")["closed_how"] == "fixed"
    progress.record(k, None, spr(1), "7")                                 # a grid-in naming nothing: norm ''
    assert trap(k, template="lin.grid")["norm"] == ""
    for seed in (2, 3):
        progress.record(k, None, spr(seed), "12")
    assert trap(k, template="lin.grid")["closed_how"] == "fixed"
    progress.record(k, None, q(5, key="lin.filler"), 3)                    # the filler: a slip
    for seed in (6, 7):
        progress.record(k, None, q(seed, other, key="lin.filler"), 0)
    assert trap(k, template="lin.filler")["closed_how"] == "fixed"
    progress.record(k, None, spr(4, [("forgot to halve", "24")], key="lin.named"), "24")   # a named grid-in
    for seed in (5, 6):
        progress.record(k, None, spr(seed, [("added the sides", "30")], key="lin.named"), "12")
    assert trap(k, template="lin.named")["owed"] == 2
    progress.record(k, None, spr(7, [("forgot to halve", "24")], key="lin.named"), "12")
    assert trap(k, template="lin.named")["owed"] == 1
    # R8 amended: hints and unsure answers are not clean; a guess counts half
    h = "a:f4hints"
    progress.record(h, None, q(1, named), 1)
    progress.record(h, None, q(2, named), 0, hints=1)
    assert trap(h)["owed"] == 2
    a = db.one("SELECT hints, guess, conf FROM attempts WHERE learner=? ORDER BY id DESC", h)
    assert (a["hints"], a["guess"], a["conf"]) == (1, 0, None)
    progress.record(h, None, q(3, named), 0, conf="guess")
    assert db.one("SELECT guess, conf FROM attempts WHERE learner=? ORDER BY id DESC", h)["guess"] == 1
    assert trap(h)["owed"] == 2
    progress.record(h, None, q(4, named, key="lin.u"), 0, conf="unsure")
    assert trap(h, template="lin.u", norm="~unsure")["owed"] == 1
    progress.record(h, None, q(5, named), 0, conf="auto")
    assert db.one("SELECT conf FROM attempts WHERE learner=? ORDER BY id DESC", h)["conf"] is None
    assert progress.mastery_of([("easy", 0.5)]) == round(progress.mastery_of([("easy", 1.0)]) / 2, 3)

    # R9: a miss on a due check-in, for another reason, reopens it as Relapsed
    r = "a:f4relapse"
    progress.record(r, None, q(1), 1, when=at("2026-01-01"))
    for seed in (2, 3):
        progress.record(r, None, q(seed), 0, when=at("2026-01-02"))
    assert trap(r)["due"] == "2026-01-05"
    progress.record(r, None, q(4, other), 2, when=at("2026-01-06"))       # another reason, on the due day
    t = trap(r, norm=progress.norm("used 10 instead of 20"))
    assert t["closed"] is None and t["relapses"] == 1 and t["due"] is None
    assert db.one("SELECT COUNT(*) AS n FROM traps WHERE learner=?", r)["n"] == 2
    # X16: a trap-test answer is a check-in whatever the date; taking the trap relapses it
    x = "a:f4traptest"
    progress.record(x, None, q(1), 1, when=at("2026-01-01"))
    for seed in (2, 3):
        progress.record(x, None, q(seed), 0, when=at("2026-01-01", 13))
    progress.record(x, None, q(4), 0, when=at("2026-01-02"), check=True)
    assert trap(x)["checks"] == 1
    progress.record(x, None, q(5), 1, when=at("2026-01-03"), check=True)
    assert trap(x)["relapses"] == 1 and trap(x)["closed"] is None

    # G3 check 4 / R9: the 10-day check-in on another type, closed as 'transfer'
    tr = "a:f4transfer"
    norm = progress.norm("used 10 instead of 20")
    with patch.object(progress, "_related_index", lambda: {norm: ("lin.evaluate", "lin.other")}):
        assert progress.related(norm) == ("lin.evaluate", "lin.other") and progress.related("nothing") == ()
        assert progress.related() == {norm: ("lin.evaluate", "lin.other")}
        progress.record(tr, None, q(1), 1, when=at("2026-01-01"))
        for seed in (2, 3):
            progress.record(tr, None, q(seed), 0, when=at("2026-01-01", 14))
        first = progress.due_rechecks(tr, "2026-01-04")[0]
        assert first["serve"] == "lin.evaluate"                           # the 3-day check, same type
        progress.record(tr, None, q(4, key=first["serve"]), 0, when=at(first["due"]))
        for seed, stage in ((5, 2), (6, 3)):                              # the 10- and 30-day ones, as served
            t = trap(tr)
            c = progress.due_rechecks(tr, t["due"])[0]
            assert c["serve"] == "lin.other" == progress.checkin_template(t), c
            progress.record(tr, None, q(seed, key=c["serve"]), 0, when=at(c["due"]))
            assert trap(tr)["checks"] == stage
        t = trap(tr, template="lin.evaluate")
        assert t["checks"] == 3 and t["closed_how"] == "transfer", dict(t)
        assert progress.rechecks_passed(tr, "2026-01-01")["n"] == 3
    # G3 rule 5: a different wrong pick on that check-in, served elsewhere, relapses it too
    rl = "a:f4transfermiss"
    elsewhere = ["", "used 10 instead of 20", "flipped the sign", progress.FILLER]
    with patch.object(progress, "_related_index", lambda: {norm: ("lin.evaluate", "lin.other")}):
        progress.record(rl, None, q(1), 1, when=at("2026-01-01"))
        for seed, day in ((2, "2026-01-01"), (3, "2026-01-01"), (4, "2026-01-04")):
            progress.record(rl, None, q(seed), 0, when=at(day, 14))
        t = trap(rl)
        assert t["checks"] == 1 and progress.checkin_template(t) == "lin.other"
        got = progress.record(rl, None, q(5, elsewhere, key="lin.other"), 2, when=at(t["due"]))
        t = trap(rl, template="lin.evaluate")
        assert (t["closed"], t["closed_how"], t["relapses"], t["checks"]) == (None, None, 1, 0), dict(t)
        assert got["relapsed"] and got["relapsed"][0]["on"] == "lin.other", got["relapsed"]
    # the same trap answered on its own type at 10 days holds, but as 'fixed'
    own = "a:f4owntype"
    with patch.object(progress, "_related_index", lambda: {norm: ("lin.evaluate", "lin.other")}):
        progress.record(own, None, q(1), 1, when=at("2026-01-01"))
        for seed, day in ((2, "2026-01-01"), (3, "2026-01-01"), (4, "2026-01-04"), (5, "2026-01-11")):
            progress.record(own, None, q(seed), 0, when=at(day, 14))
        progress.record(own, None, q(6, key="lin.other"), 0, when=at("2026-01-31"))
        assert (trap(own)["checks"], trap(own)["closed_how"]) == (3, "fixed")

    # §2.5: the first write makes the learners row (rating DEFAULT 1000, rated 0)
    progress.record("a:f4firstwrite", None, q(1), 0)
    row = db.one("SELECT rating, rated FROM learners WHERE id=?", "a:f4firstwrite")
    assert row and (row["rating"], row["rated"]) == (1000, 0)
    progress.log_mistake("a:f4firstlog", "lin.evaluate", "linear_functions", note="outside")
    assert db.one("SELECT 1 FROM learners WHERE id=?", "a:f4firstlog")

    # R8 / V2: access() already 'reveal' makes a repeat; a printed key does too
    v = "a:f4repeat"
    blank = real("lin.evaluate", 7001, "m1q01")
    add("sessions", id="f4-blank", kind="module", learner=v, started=at(TODAY), finished=at(TODAY, 13),
        questions=json.dumps({"module1": [blank]}))
    assert deps.access(v, "lin.evaluate", 7001) == "reveal"
    got = progress.record(v, "f4-drill", {**blank, "id": "p001"}, ans(blank))
    assert got["repeat"] and not got["clean"]
    add("sessions", id="f4-sheet", kind="drill", learner=v, started=at(TODAY),
        cfg=json.dumps({"feedback": "end", "key_printed": at(TODAY, 1)}))
    assert progress.record(v, "f4-sheet", q(71), 0, when=at(TODAY, 2))["repeat"]
    add("sessions", id="f4-instant", kind="drill", learner=v, started=at(TODAY), cfg="{}")
    progress.record(v, "f4-instant", q(72), 1)
    assert db.one("SELECT revealed_at FROM attempts WHERE learner=? AND seed=72", v)["revealed_at"]

    # P11: ratings move on clean first tries only
    rt = "a:f4ratings"
    before = ratings.item("lin.evaluate", "easy")[1]
    progress.record(rt, None, q(1), 0)
    assert ratings.item("lin.evaluate", "easy")[1] == before + 1
    assert ratings.skill(rt, "linear_functions")["n"] == 1
    progress.record(rt, None, q(2), 0, conf="guess")
    progress.record(rt, None, q(3), 0, hints=1)
    assert ratings.skill(rt, "linear_functions")["n"] == 1
    assert ratings.level_of(ratings.TIER_PRIOR["hard"]) == 6
    db.run("UPDATE learners SET current=700 WHERE id=?", rt) if db.one("SELECT 1 FROM learners WHERE id=?", rt) else None
    db.ensure_learner("a:f4seeded")
    db.run("UPDATE learners SET current=700 WHERE id=?", "a:f4seeded")
    s = ratings.skill("a:f4seeded", "circles")
    assert (round(s["rating"]), s["seed"]) == (1304, "score")
    for i in range(4):
        add("attempts", learner=f"a:f4prior{i}", template="circles.prior", seed=i, topic="circles",
            difficulty="medium", fmt="mcq", correct=1, at=at(TODAY))
    assert ratings.measured_prior("circles.prior", "medium") is None
    add("attempts", learner="a:f4prior4", template="circles.prior", seed=4, topic="circles",
        difficulty="medium", fmt="mcq", correct=1, at=at(TODAY))
    raw = 1000 - 400 * math.log10(0.95 / 0.05)                                     # 5 of 5 right, clamped
    assert abs(ratings.measured_prior("circles.prior", "medium", 1200.0) - (0.2 * raw + 0.8 * 1200)) < 1e-6

    # §2.10: a ranked contest answer calls compete.rate; a voided one does not
    calls = []
    add("sessions", id="f4-contest", kind="drill", learner="a:f4contest", started=at(TODAY), contest="daily", ranked=1)
    real_part = deps.part
    with patch.object(deps, "part", lambda m, n: (lambda *a: calls.append(a)) if (m, n) == ("compete", "rate")
                      else real_part(m, n)):
        progress.record("a:f4contest", "f4-contest", q(1), 0)
        progress.record("a:f4contest", "f4-contest", q(2), 0, void="left")
    assert len(calls) == 1 and calls[0][1] == "f4-contest"

    # R57: an R&W item files as an ordinary attempt; its trap id is the norm
    w = "a:f4rw"
    rw = {"id": "w1", "key": "rw.wic.frame1", "seed": 3, "topic": "words-in-context", "difficulty": "medium",
          "type": "mcq", "answer": "A", "reasons": ["", "too_strong", "wrong_sense", "opposite"],
          "reason_names": [None, "Too strong for the clue", "Wrong sense", "The opposite"]}
    progress.record(w, None, rw, 1, word="abate")
    t = trap(w)
    assert t["norm"] == "too_strong" and t["label"] == "Too strong for the clue"
    assert db.one("SELECT word FROM attempts WHERE learner=?", w)["word"] == "abate"
    progress.record(w, None, {**rw, "seed": 4, "reasons": ["", "wrong_sense", "opposite", "off_topic"]}, 0)
    assert trap(w)["owed"] == 2
    assert deps.subject_of("words-in-context") == "rw" and deps.subject_of("rw.tr.contrast") == "rw"
    assert deps.subject_of("circles") == "math" and deps.subject_of("lin.evaluate") == "math"
    try:
        deps.subject_param("xx")
        raise AssertionError("an unknown subject passed")
    except HTTPException as e:
        assert e.status_code == 422
    assert "linear_functions" in progress.topics("math") and not progress.topics("rw")

    # Shell §3.1.5: an outside mistake's label is the reason, the note, or the skill
    lm = "a:f4logged"
    progress.log_mistake(lm, "lin.evaluate", "linear_functions", note="Bluebook Q7")
    assert trap(lm)["label"] == "Bluebook Q7"
    progress.log_mistake(lm, "lin.slope_from_points", "linear_functions")
    assert trap(lm, template="lin.slope_from_points")["label"] != "linear_functions"

    # V13: a discarded sitting's answers and trap changes roll back, and come back
    d = "a:f4discard"
    add("sessions", id="f4-d0", kind="drill", learner=d, started=at(TODAY), cfg="{}")
    add("sessions", id="f4-d1", kind="drill", learner=d, started=at(TODAY), cfg="{}")
    progress.record(d, "f4-d0", q(1, key="lin.keep"), 1)              # opened earlier, refreshed below
    progress.record(d, "f4-d0", q(4, key="lin.right"), 0)
    m_d0 = progress.topic_mastery(d, "linear_functions")
    progress.record(d, "f4-d1", q(2, key="lin.keep"), 1)
    progress.record(d, "f4-d1", q(3, key="lin.only"), 1)              # opened only here
    m_d1 = progress.topic_mastery(d, "linear_functions")
    assert m_d1 != m_d0
    out = progress.discard(d, "f4-d1")
    assert out["answers"] == 2 and out["traps_closed"] == 1
    assert trap(d, template="lin.only")["closed_how"] == "discarded"
    assert trap(d, template="lin.keep")["hits"] == 1
    assert progress.topic_mastery(d, "linear_functions") == m_d0
    progress.restore(d, "f4-d1")
    assert trap(d, template="lin.only")["closed"] is None and trap(d, template="lin.keep")["hits"] == 2
    assert progress.topic_mastery(d, "linear_functions") == m_d1
    undo = db.rows("SELECT pts, undoes FROM trap_log WHERE learner=? AND event IN ('discarded','restored')", d)
    assert undo and all(r["pts"] is None and r["undoes"] for r in undo)

    # V4: a fix logs what it was worth, gain(t) x share
    pv = "a:f4points"
    old = at(TODAY - dt.timedelta(days=3))
    for i in range(30):
        add("attempts", learner=pv, template="prob.x" if i % 5 else "prob.t", seed=100 + i, topic="probability",
            difficulty="medium", fmt="mcq", correct=int(i % 4 == 0), at=old,
            norm=None if i % 4 == 0 else progress.norm("used 10 instead of 20"))
    progress.record(pv, None, q(1, key="prob.t", topic="probability"), 1)
    for seed in (2, 3):
        progress.record(pv, None, q(seed, key="prob.t", topic="probability"), 0)
    assert trap(pv)["closed_how"] == "fixed"
    gain = next(x["gain"] for x in estimate.gains(pv)["skills"] if x["topic"] == "probability")
    wrong = db.rows("SELECT template, norm FROM attempts WHERE learner=? AND topic='probability' AND correct=0", pv)
    mine = sum(1 for r in wrong if r["template"] == "prob.t" and r["norm"] == trap(pv)["norm"])
    want = round(gain * mine / len(wrong))
    assert want >= 1 and db.one("SELECT pts FROM trap_log WHERE learner=? AND event='fixed' ORDER BY id DESC",
                                pv)["pts"] == want
    assert estimate.trap_pts("a:f4progress", "lin.evaluate", "x", "linear_functions") is None   # under 30 answers

    # U3: remarking an answer right closes the trap it alone opened
    rm = "a:f4remark"
    progress.record(rm, None, q(1, key="lin.rm"), 1)
    aid = db.one("SELECT id FROM attempts WHERE learner=?", rm)["id"]
    assert progress.remark(rm, aid)["closed"] and trap(rm)["closed_how"] == "remarked"

    # scoring: forms that fit the grid, T7's entry rule and SR10's diagnoses
    assert scoring.accepted_forms("2/3") == ["2/3", ".6666", ".6667", "0.666", "0.667"]
    assert scoring.accepted_forms("7/3") == ["7/3", "2.333"] and scoring.accepted_forms("-7/3") == ["-7/3", "-2.333"]
    assert all(len(f) <= (6 if f.startswith("-") else 5) for k in ("100/3", "7/3", "1/8", "-7/3")
               for f in scoring.accepted_forms(k))
    for g_, k_ in ((".66", "2/3"), ("0.66", "2/3"), (".67", "2/3"), ("1.2", "1.25")):
        assert scoring.entry_error(g_, k_) == "early", (g_, k_)
    assert scoring.entry_error("1 1/2", "3/2") == "form"
    for g_, k_ in (("455", "460"), ("154", "150"), (".7", "2/3"), ("3", "3.5"), (".6667", "2/3")):
        assert scoring.entry_error(g_, k_) is None, (g_, k_)
    assert scoring.grid_equal(".6667", "2/3")
    assert scoring.grid_diagnose("0.66", "2/3")["kind"] == "short"
    assert scoring.grid_diagnose("1 1/2", "3/2")["kind"] == "form"
    assert scoring.grid_diagnose("-7", "7")["kind"] == "sign"
    assert scoring.grid_diagnose("45", "0.45")["kind"] == "percent"
    assert scoring.grid_diagnose("12", "8") is None

    legacy = sqlite3.connect(":memory:")
    legacy.row_factory = sqlite3.Row
    legacy.executescript("""
      CREATE TABLE traps(learner TEXT,template TEXT,reason TEXT,label TEXT,topic TEXT,
        hits INTEGER,owed INTEGER,opened TEXT,last TEXT,closed TEXT,
        PRIMARY KEY(learner,template,reason));
      CREATE TABLE attempts(id INTEGER PRIMARY KEY,learner TEXT,template TEXT,reason TEXT,
        correct INTEGER,seed INTEGER,session TEXT,at TEXT);
      INSERT INTO traps VALUES('old','lin.evaluate','used 10 instead of 20','First',
        'linear_functions',2,2,'2026-01-01','2026-01-02',NULL);
      INSERT INTO traps VALUES('old','lin.evaluate','used 30 instead of 40','Second',
        'linear_functions',3,1,'2026-01-02','2026-01-03','2026-01-04');
      INSERT INTO attempts VALUES(1,'old','lin.evaluate','used 30 instead of 40',0,77,'legacy','2026-01-03');
    """)
    db._rebuild_traps(legacy)
    merged = legacy.execute("SELECT * FROM traps").fetchall()
    assert len(merged) == 1 and merged[0]["hits"] == 5 and merged[0]["closed"] is None
    assert merged[0]["seed"] == 77 and merged[0]["reason"] == "used 30 instead of 40"
    legacy.close()
    legacy = sqlite3.connect(":memory:")
    legacy.row_factory = sqlite3.Row
    legacy.executescript("""
      CREATE TABLE sessions(id TEXT PRIMARY KEY,kind TEXT,form_id INTEGER NOT NULL,
        started TEXT NOT NULL,finished TEXT,answers TEXT,result TEXT,user_id TEXT,
        qstate TEXT,mock_id TEXT);
      INSERT INTO sessions(id,kind,form_id,started,qstate,mock_id)
        VALUES('old-session','mock',2,'2026-01-01','{"q1":{"ms":3000}}','1.3');
    """)
    db._relax_form_id(legacy)
    kept = legacy.execute("SELECT qstate,mock_id FROM sessions WHERE id='old-session'").fetchone()
    assert kept["mock_id"] == "1.3" and json.loads(kept["qstate"])["q1"]["ms"] == 3000
    assert not next(c for c in legacy.execute("PRAGMA table_info(sessions)") if c["name"] == "form_id")["notnull"]
    legacy.close()

    gone = add("attempts", learner="a:f4gone", template="gone.template", seed=1, topic="linear_functions",
               difficulty="easy", fmt="mcq", correct=1, at=at(TODAY)).lastrowid
    db._backfill_attempts(db.conn())
    row = db.one("SELECT stem, offered FROM attempts WHERE id=?", gone)
    assert (row["stem"], row["offered"]) == ("", "[]")
    assert not db.one("SELECT 1 FROM attempts WHERE id=? AND (stem IS NULL OR offered IS NULL"
                      " OR (norm IS NULL AND (correct=0 OR flagged=1)))", gone)
    assert "rank_snapshots" in db.LEARNER_TABLES and "undoes" in {r["name"] for r in db.rows("PRAGMA table_info(trap_log)")}

    # the upgrades' schema: every column and table F4 adds
    cols = lambda t: {r["name"] for r in db.rows(f"PRAGMA table_info({t})")}  # noqa: E731
    assert {"conf", "hints", "miss_kind", "offered", "struck", "cover", "calc", "diag", "revealed_at",
            "word"} <= cols("attempts")
    assert {"dir", "token", "approver", "session_only"} <= cols("pairs")
    assert {"feed_seen", "handle", "swap_until"} <= cols("learners") and "google_sub" in cols("users")
    assert "subject" in cols("sessions") and {"subject", "series", "round"} <= cols("contests")
    assert {"hook", "proven", "placed"} <= cols("word_state") and "attempt" in cols("word_reviews")
    for table in ("skill_ratings", "trap_log", "due_days", "passkeys", "webauthn_challenges", "devices",
                  "transfers", "quarantine", "week_goals", "push_subs", "cb_unknown", "follows",
                  "rank_snapshots", "nudges", "champions", "plan_snapshots", "plan_events", "rw_log",
                  "word_lists", "word_suppress", "official_done"):
        assert db.one("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", table), table
    assert db.is_sample("sample:x") and "sample:%" in db.NOT_SAMPLE
    try:
        progress.record("sample:f4", None, q(1), 0)
        raise AssertionError("a sample learner wrote")
    except HTTPException as e:
        assert e.status_code == 403
    assert db.one("SELECT 1 FROM kv WHERE k='backfill:item_priors'") and db.one("SELECT 1 FROM kv WHERE k='backfill:ratings'")


def days_checks():
    # Six study weekdays across a weekend; planned rest days preserve the run.
    learner = "a:f4streak"
    db.ensure_learner(learner)
    db.run("UPDATE learners SET plan='p1',days='1111100' WHERE id=?", learner)
    active = []
    d = TODAY
    while len(active) < 6:
        if d.weekday() < 5:
            active.append(d)
        d -= dt.timedelta(days=1)
    for i, day in enumerate(active):
        add("attempts", learner=learner, template="lin.evaluate", seed=100 + i, topic="linear_functions",
            difficulty="easy", fmt="mcq", correct=1, at=at(day))
    ledger = progress.days(learner, 0, 26)
    assert ledger["best_streak"] == ledger["best"] == 6 and len(ledger["days"]) == 182
    assert ledger["streak"] == 6, ledger["streak"]

    learner = "a:f4minutes"
    finish = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    began = finish - dt.timedelta(minutes=10)
    add("sessions", id="module-time", kind="module", learner=learner, started=began.isoformat(), finished=finish.isoformat())
    add("attempts", learner=learner, session="module-time", template="lin.evaluate", seed=1,
        topic="linear_functions", difficulty="easy", fmt="mcq", correct=1, at=finish.isoformat())
    assert progress.days(learner)["minutes_total"] == 10
    db.run("UPDATE attempts SET ms=180000 WHERE learner=?", learner)
    assert progress.days(learner)["minutes_total"] == 3
    paper = "a:f4paper"
    add("sessions", id="paper-time", kind="paper", learner=paper,
        started=(finish - dt.timedelta(minutes=100)).isoformat(), finished=finish.isoformat(),
        cfg=json.dumps({"timing": "x2"}))
    assert progress.days(paper)["minutes_total"] == 100
    # R13: each module capped at its own clock + 60 s; untimed modules at 90 min each
    split = "a:f4split"
    add("sessions", id="split-time", kind="mock", learner=split, started=(finish - dt.timedelta(minutes=130)).isoformat(),
        module_started=(finish - dt.timedelta(minutes=10)).isoformat(), finished=finish.isoformat())
    assert progress.days(split)["minutes_total"] == 46
    untimed = "a:f4untimed"
    add("sessions", id="untimed-time", kind="mock", learner=untimed, cfg=json.dumps({"timing": "untimed"}),
        started=(finish - dt.timedelta(minutes=170)).isoformat(),
        module_started=(finish - dt.timedelta(minutes=85)).isoformat(), finished=finish.isoformat())
    assert progress.days(untimed)["minutes_total"] == 170
    # L10 / R13: a done own task counts its minutes; a done question task the
    # minutes it says it took elsewhere; a done question task with none, nothing
    pm = "a:f4marks"
    db.ensure_learner(pm)
    db.run("UPDATE learners SET plan='f4-pm' WHERE id=?", pm)
    add("plan_tasks", id="f4-own", plan="f4-pm", day=str(TODAY), title="Read a chapter", minutes=15)
    add("plan_marks", plan="f4-pm", day=str(TODAY), task="f4-own", status="done")
    add("plan_marks", plan="f4-pm", day=str(TODAY), task=f"{TODAY}:practice", status="done", minutes=20)
    add("plan_marks", plan="f4-pm", day=str(TODAY), task=f"{TODAY}:words", status="done")
    assert progress.days(pm)["minutes_total"] == 35
    # Today's day rows: practice, tests and the day's questions
    row = progress.days(split)["recent"][-1]
    assert row["tests"] == 1 and row["practice"] == 0
    qd = "a:f4qotd"
    add("attempts", learner=qd, session=f"qotd:{TODAY}", template="lin.evaluate", seed=5, topic="linear_functions",
        difficulty="easy", fmt="mcq", correct=1, at=at(TODAY, 1))
    add("attempts", learner=qd, session=f"qotd-spr:{TODAY}", template="lin.evaluate", seed=6, topic="linear_functions",
        difficulty="easy", fmt="spr", correct=0, at=at(TODAY, 1))
    row = next(r for r in progress.days(qd)["recent"] if r["day"] == str(TODAY))
    assert row["qotd"] == {"mcq": True, "spr": True} and row["practice"] == 2
    # G16: official questions count toward study time and the day
    off = "a:f4official"
    add("official_done", learner=off, cb_id="84664a7c", pick="C", right=0, ms=120000, at=at(TODAY, 1))
    got = progress.days(off)
    assert got["minutes_total"] == 2 and got["active_days"] == 1
    # U16: 7 study days bank a spare, which a missed study day spends
    sp = "a:f4spare"
    for i in range(9):
        day = TODAY - dt.timedelta(days=9 - i)
        if i != 7:
            add("attempts", learner=sp, template="lin.evaluate", seed=200 + i, topic="linear_functions",
                difficulty="easy", fmt="mcq", correct=1, at=at(day))
    got = progress.days(sp)
    assert got["streak"] == 8 and got["spares"] == 0, got["streak"]
    assert next(r for r in got["recent"] if r["day"] == str(TODAY - dt.timedelta(days=2)))["spare_used"]
    nosp = "a:f4nospare"
    for i in (0, 1, 3):
        add("attempts", learner=nosp, template="lin.evaluate", seed=300 + i, topic="linear_functions",
            difficulty="easy", fmt="mcq", correct=1, at=at(TODAY - dt.timedelta(days=4 - i)))
    assert progress.days(nosp)["streak"] == 1

    # words.md §3.2: lookups, sorts and placements are not reviews, so no study day
    wl = "a:f4lookups"
    for i, mode in enumerate(("lookup", "sort", "placement") * 4):
        add("word_reviews", learner=wl, word=f"w{i}", mode=mode, kind="card", correct=1, ms=50000, at=at(TODAY, 1))
    got = progress.days(wl)
    assert (got["recent"][-1]["words"], got["minutes_total"], got["streak"]) == (0, 0, 0), got["recent"][-1]
    add("word_reviews", learner=wl, word="w99", mode="cards", kind="card", correct=1, ms=60000, at=at(TODAY, 1))
    assert progress.days(wl)["recent"][-1]["words"] == 1

    # T3: counted rights, intervals, candidates and the forecast
    wu = "a:f4warmup"
    old = TODAY - dt.timedelta(days=3)
    for hour in (1, 11):                                  # 10 hours apart: one counted right
        add("attempts", learner=wu, template="lin.evaluate", seed=400 + hour, topic="linear_functions",
            difficulty="easy", fmt="mcq", correct=1, at=at(old, hour))
    assert len(progress._clean_rights(wu)["lin.evaluate"]) == 1
    add("traps", learner=wu, template="circles.arc", norm="n", reason="n", label="Arc", topic="circles", owed=0,
        opened=at(old), last=at(old), closed=at(old), closed_how="fixed", due=str(TODAY), checks=0)
    cand = progress.warmup_candidates(wu)
    assert cand["checks"][0]["template"] == "circles.arc" and cand["fading"][0]["template"] == "lin.evaluate"
    add("traps", learner=wu, template="circles.arc_angle", norm="m", reason="m", label="Angle", topic="circles",
        owed=0, opened=at(old), last=at(old), closed=at(old), closed_how="fixed",
        due=str(TODAY + dt.timedelta(days=4)), checks=1)
    forecast = progress.due_forecast(wu, 0, 14)
    assert next(f for f in forecast if f["day"] == str(TODAY + dt.timedelta(days=4)))["checks"] == 1
    mk = "a:f4marked"
    add("sessions", id="f4-mk", kind="drill", learner=mk, started=at(TODAY - dt.timedelta(days=5)), cfg="{}")
    for template, seed, back in (("circles.arc", 1, 3), ("lin.evaluate", 2, 3), ("lin.slope", 3, 1)):
        add("flags", learner=mk, session="f4-mk", qid=f"q{seed}", template=template, seed=seed,
            topic=progress._topic_of(template), at=at(TODAY - dt.timedelta(days=back)))
    add("attempts", learner=mk, template="lin.evaluate", seed=9, topic="linear_functions", difficulty="easy",
        fmt="mcq", correct=1, at=at(TODAY - dt.timedelta(days=1)))            # a right first try since that flag
    cand = progress.warmup_candidates(mk)
    assert [m["template"] for m in cand["marked"]] == ["circles.arc"] and cand["marked"][0]["kind"] == "marked"
    assert cand["size"] == len(cand["checks"]) + len(cand["fading"]) + len(cand["keep_warm"]) + 1
    fl = "a:f4fluency"
    for i, (template, ms, ok) in enumerate((("circles.fl", 50000, 1), ("circles.fl", 60000, 1),
                                            ("circles.slow", 200000, 1), ("circles.slow", 210000, 1),
                                            ("circles.slow", 190000, 1))):
        add("attempts", learner=fl, template=template, seed=i, topic="circles", difficulty="medium", fmt="mcq",
            correct=ok, ms=ms, at=at(TODAY, 1 + i))
    f = progress.fluency(fl)
    assert f["circles.fl"]["fluent"] and f["circles.fl"]["best_ms"] == 50000 and not f["circles.fl"]["slow_right"]
    assert f["circles.slow"]["slow_right"] and not f["circles.slow"]["fluent"]
    loose = progress.fluency(fl, lambda _t, _tier: 300000)
    assert loose["circles.slow"]["fluent"] and not loose["circles.slow"]["slow_right"]


def causes_checks():
    # T7: one cause per miss, first match wins
    c = "a:f4causes"
    grid = real("le2.slope_of_line", 0, "g1")                  # 4/15 = .2666...
    add("sessions", id="f4-causes", kind="drill", learner=c, started=at(TODAY), cfg="{}")
    progress.record(c, "f4-causes", grid, "0.26", ms=40000)
    got = progress.causes(c)
    assert got["by"]["entry"] == 1, got["by"]
    progress.record(c, "f4-causes", real("le2.slope_of_line", 1, "g2"), "455", ms=180000)
    named = real("lin.evaluate", 1)
    trap_pick = next(i for i, r in enumerate(named["reasons"]) if r and r != progress.FILLER)
    for s in range(20, 25):                                     # 4 of the last 5 right on this type
        progress.record(c, None, real("lin.evaluate", s), ans(real("lin.evaluate", s), s != 24), ms=60000)
    progress.record(c, "f4-causes", named, trap_pick, ms=60000)
    got = progress.causes(c)
    assert sum(got["by"].values()) == got["total"]
    last = db.one("SELECT id FROM attempts WHERE learner=? AND seed=1 AND template='lin.evaluate'", c)["id"]
    assert last in got["items"]["trap"], got["items"]
    assert all(db.one("SELECT learner FROM attempts WHERE id=?", i)["learner"] == c
               for ids in got["items"].values() for i in ids if isinstance(i, int))
    # a timed module finished with 3 blanks: 3 clock
    t = "a:f4clock"
    paper = [real("lin.evaluate", 900 + i, f"m1q{i:02d}") for i in range(1, 5)]
    add("sessions", id="f4-timed", kind="module", learner=t, started=at(TODAY), finished=at(TODAY, 13),
        questions=json.dumps({"module1": paper}), answers=json.dumps({"m1q01": 0}))
    assert progress.causes(t)["by"]["clock"] == 3
    per = progress.causes(t, session="f4-timed")["per_q"]
    assert all(per[f"m1q{i:02d}"]["cause"] == "clock" for i in (2, 3, 4))
    # P8: a student-set cause wins
    aid = db.one("SELECT id FROM attempts WHERE learner=? AND seed=1 AND template='lin.evaluate'", c)["id"]
    db.run("UPDATE attempts SET miss_kind='misread' WHERE id=?", aid)
    assert aid in progress.causes(c)["items"]["misread"]
    # U7: the pace quadrants and the module forecast
    pc = "a:f4pace"
    for i in range(6):
        add("attempts", learner=pc, template="circles.arc", seed=500 + i, topic="circles", difficulty="medium",
            fmt="mcq", correct=int(i < 5), ms=150000, at=at(TODAY, 1))
    pace = progress.pace(pc)
    assert pace["skills"]["circles"]["quadrant"] == "slow_right"
    assert pace["forecast"]["seconds"] * 1000 == sum(s["ms"] for s in pace["forecast"]["strip"])
    total, runs = 0, None
    for s in pace["forecast"]["strip"]:
        total += s["ms"]
        if runs is None and total > 2_100_000:
            runs = s["slot"]
    assert pace["forecast"]["runs_out_at"] == runs
    for i in range(25):
        add("attempts", learner=pc, template="circles.arc", seed=600 + i, topic="circles", difficulty="medium",
            fmt="mcq", correct=int(i < 7), guess=1, conf="guess", ms=30000, at=at(TODAY, 2))
    assert progress.pace(pc)["guess"] == {"n": 25, "right": 7}
    # P7 / P9: the tagger rule and questions to Strong
    assert progress.conf_active(pc) and not progress.conf_active(t)
    assert progress.steps_to("a:f4nobody", "circles") > 0
    strong = "a:f4strong"
    for i in range(40):
        add("attempts", learner=strong, template="circles.arc", seed=700 + i, topic="circles", difficulty="hard",
            fmt="mcq", correct=1, at=at(TODAY, 1))
    assert progress.steps_to(strong, "circles") == 0
    b = progress.board(strong)["circles"]
    assert b["evidence"] == 40 and b["last5"] == [1, 1, 1, 1, 1] and b["accuracy"] == 1.0
    assert progress.types_met(strong)["practice"] == 1
    # U5: a rough skill gets a probe first
    rough = "a:f4rough"
    for i in range(6):
        add("attempts", learner=rough, template="circles.arc", seed=800 + i, topic="circles", difficulty="medium",
            fmt="mcq", correct=1, at=at(TODAY - dt.timedelta(days=1)))
    coach = progress.coach(rough, k=19)
    assert coach["reasons"]["circles"]["kind"] == "probe" and "circles" in coach["probe"]
    # P7: a sure miss ranks first, reason confident
    sure = "a:f4sure"
    progress.record(sure, None, q(1, key="circles.arc", topic="circles"), 1, conf="sure")
    assert progress.coach(sure)["reasons"]["circles"]["kind"] == "confident"
    cal = progress.calibration(sure)
    assert cal["conf"]["sure"]["wrong"] == 1 and cal["sure_wrong"]
    # T9 / X11: blind spots are sure misses, told or inferred
    bl = "a:f4blind"
    for i in range(5):
        for tier in ("easy", "medium"):
            add("attempts", learner=bl, template="circles.base", seed=900 + i + (10 if tier == "easy" else 0),
                topic="circles", difficulty=tier, fmt="mcq", correct=1, ms=100000, at=at(TODAY, 1))
    med = lambda n, key: {**q(n, key=key, topic="circles"), "difficulty": "medium"}  # noqa: E731
    progress.record(bl, None, med(1, "circles.fast"), 1, ms=20000)             # medium, under 0.6 x median
    progress.record(bl, None, q(2, key="circles.easyfast", topic="circles"), 1, ms=1000)   # easy: a slip, never blind
    progress.record(bl, None, med(3, "circles.guess"), 1, ms=20000, conf="guess")
    progress.record(bl, None, med(4, "circles.slow"), 1, ms=150000)
    progress.record(bl, None, med(5, "circles.filler"), 3, ms=20000)          # fast, but T7 says slip, not trap
    add("sessions", id="f4-bl-test", kind="module", learner=bl, started=at(TODAY), finished=at(TODAY, 2),
        qstate=json.dumps({"t1": {"conf": "sure"}, "t2": {"predict": "miss"}, "t3": {}}))
    progress.record(bl, "f4-bl-test", {**q(6, key="circles.testsure", topic="circles"), "id": "t1"}, 1,
                    ms=150000, conf="sure")
    progress.record(bl, "f4-bl-test", {**med(7, "circles.spotted"), "id": "t2"}, 1, ms=150000)
    progress.record(bl, "f4-bl-test", {**med(8, "circles.silent"), "id": "t3"}, 1, ms=150000)
    got = progress.blind(bl)
    whys = {t["template"]: t["why"] for t in got.values()}
    assert whys == {"circles.fast": "fast", "circles.testsure": "sure", "circles.silent": "silent"}, whys
    cache, medians = {}, progress._tier_medians(bl)
    for t in got.values():
        a = dict(db.one("SELECT * FROM attempts WHERE id=?", t["attempt"]))
        assert progress._cause(bl, a, progress._sitting(a["session"], cache), medians)[0] == "trap"
    # QBank §3.3.5: the plan's Focus is a coach reason of its own
    fo = "a:f4focus"
    db.ensure_learner(fo)
    db.run("UPDATE learners SET focus=? WHERE id=?", json.dumps({"Geometry and Trigonometry": "focus"}), fo)
    co = progress.coach(fo)
    kinds = [co["reasons"][p]["kind"] for p in co["topics"]]              # at most two from one domain
    assert co["why"] == "focus" and kinds == ["focus", "focus", "new"], co["reasons"]


def estimate_checks():
    learner = "a:f4estimate"
    for i, (low, high, kind) in enumerate(((500, 640, "mock"), (600, 700, "mock"), (400, 600, "module")), start=1):
        stamp = at(TODAY - dt.timedelta(days=i))
        add("sessions", id=f"score-f4-{i}", kind=kind, learner=learner, started=stamp, finished=stamp,
            route="upper" if kind == "mock" else None, result=json.dumps({"estimate": {"low": low, "high": high}}))
    add("outside_scores", id="outside-f4", learner=learner, day=str(TODAY), math=650, at=progress.now())
    e = estimate.estimate(learner)
    assert e["latest"]["kind"] == "outside" and e["mean3"] == 620
    assert e["combined"] and e["confidence"]["level"] == "high"
    assert estimate.percentile("score-f4-2")["why"] == "too few sittings"
    assert estimate.percentile("score-f4-1")["why"] == "repeat sitting"
    # R16 / Tests §3.4.5: repeats are by kind (not sessions.number); papers by mock_id; modules rank
    for i in range(25):
        stamp = at(TODAY - dt.timedelta(days=40), 1)
        add("sessions", id=f"f4-peer-{i}", kind="module", learner=f"a:f4peer{i}", started=stamp, finished=stamp,
            number=1, result=json.dumps({"estimate": {"low": 300 + 10 * i, "high": 500 + 10 * i}}))
    add("sessions", id="f4-peer-retake", kind="module", learner="a:f4peer3", started=at(TODAY), finished=at(TODAY),
        number=2, result=json.dumps({"estimate": {"low": 700, "high": 800}}))
    assert estimate.percentile("f4-peer-retake")["why"] == "repeat sitting"
    ranked = estimate.percentile("f4-peer-10")
    assert ranked["ranked"] and ranked["n"] >= 25
    db.run("UPDATE sessions SET ranked=0, unranked_why='paused once' WHERE id='f4-peer-11'")
    assert estimate.percentile("f4-peer-11") == {"ranked": False, "pct": None, "n": 0, "why": "paused once"}
    mocks_before = estimate.percentile("score-f4-2")["n"]
    add("sessions", id="f4-paper-7", kind="mock", mock_id="P7", learner="a:f4paper7", started=at(TODAY),
        finished=at(TODAY), result=json.dumps({"estimate": {"low": 500, "high": 640}}))
    add("sessions", id="f4-section", kind="mock", mock_id="new", learner="a:f4paper7", started=at(TODAY),
        finished=at(TODAY, 13), result=json.dumps({"estimate": {"low": 500, "high": 640}}))
    assert estimate.percentile("f4-paper-7")["n"] == 1                   # a paper: only that paper's sittings
    assert estimate.percentile("score-f4-2")["n"] == mocks_before + 1     # the section counts, the paper does not

    # SR5: College Board's table, as printed
    data = json.loads(estimate.PERCENTILES.read_text())
    assert len(data["tables"]["math"]) == 61 and len(data["tables"]["rw"]) == 61 and len(data["tables"]["total"]) == 121
    rank = lambda v: 99.5 if v == "99+" else (0.5 if v == "1-" else v)  # noqa: E731
    for table in data["tables"].values():
        vals = [rank(table[k]) for k in sorted(table, key=int)]
        assert vals == sorted(vals)
    assert data["source"] and isinstance(data["year"], int) and 2024 <= data["year"] <= TODAY.year
    nat = estimate.national(520, 660)
    assert nat["low_pct"] == data["tables"]["math"]["520"] and nat["high_pct"] == data["tables"]["math"]["660"]

    # SR1 / SR2 / SR19: exact re-marking of one section
    sec = "a:f4ledger"
    from satbank.registry import templates
    pool = [t for t in templates() if t.startswith("lin.")][:6]
    paper, answers = [], {}
    for i in range(44):
        item = real(pool[i % len(pool)], 1000 + i, f"m{'1' if i < 22 else '2l'}q{i % 22 + 1:02d}")
        paper.append(item)
        if i < 40:
            answers[item["id"]] = ans(item, i % 4 != 0)
    add("sessions", id="f4-ledger", kind="mock", mock_id="new", learner=sec, route="lower",
        started=at(TODAY), finished=at(TODAY, 13), answers=json.dumps(answers),
        questions=json.dumps({"module1": paper[:22], "module2": paper[22:]}),
        result=json.dumps({"estimate": {"low": 400, "high": 540}}))
    lg = estimate.ledger("f4-ledger")
    for key in ("by_cause", "by_tier", "by_domain"):
        assert abs(sum(b["pts"] for b in lg[key]) - lg["total"]) < 1, key
    assert abs(lg["incorrect_pts"] + lg["blank_pts"] - lg["total"]) < 1
    assert all(v["pts"] >= 0 for v in lg["per_q"].values()) and lg["route"]["short_by"] >= 0
    wrong = [qid for qid in lg["per_q"]][:3]
    assert estimate.rescore("f4-ledger", right=wrong)["mid"] > lg["mid"]
    everything = estimate.rescore("f4-ledger", right=list(lg["per_q"]))
    assert abs(everything["mid"] - lg["all_right"]["mid"]) < 1e-6
    add("attempts", learner=sec, session="f4-ledger", qid=wrong[0], template=pool[0], seed=1000, topic="linear_functions",
        difficulty="easy", fmt="mcq", correct=0, disputed=1, at=at(TODAY, 13))
    res = estimate.rescore_sitting("f4-ledger", qid=wrong[0], how="removed")
    stored = json.loads(db.one("SELECT result FROM sessions WHERE id='f4-ledger'")["result"])
    assert stored["rescored"][0]["how"] == "removed" and wrong[0] in stored["removed"] and res["after"]
    db.run("UPDATE learners SET rw_now=610 WHERE id=?", sec) if db.one("SELECT 1 FROM learners WHERE id=?", sec) \
        else add("learners", id=sec, created=progress.now(), rw_now=610)
    tot = estimate.total(sec, "f4-ledger")
    band = stored["estimate"]
    assert tot["low"] == band["low"] + 610 and tot["parts"][1]["source"] == "self"
    assert tot["pct"]["low_pct"] == data["tables"]["total"][str(tot["low"])]

    # U4 / T6: points on the table
    g = "a:f4gains"
    rows = [("circles", 10, 3), ("linear_functions", 20, 18)] + [
        (t, 3, 2) for t in ("percentages", "probability", "area_and_volume", "equivalent_expressions",
                            "nonlinear_functions", "linear_inequalities", "one_variable_data", "ratios_rates_proportions_and_units",
                            "systems_of_linear_equations", "two_variable_data")]
    n = 0
    for topic, total, right in rows:
        for i in range(total):
            n += 1
            add("attempts", learner=g, template=f"{topic}.x", seed=n, topic=topic, difficulty="medium", fmt="mcq",
                correct=int(i < right), ms=90000, at=at(TODAY - dt.timedelta(days=2)))
    gains = estimate.gains(g)
    by = {s["topic"]: s for s in gains["skills"]}
    assert by["circles"]["raw"] > by["linear_functions"]["raw"]
    assert estimate.gains("a:f4progress") is None
    assert estimate.need(700, g)["path"]["skills"] and estimate.need(700)["m1_min"] == 14
    assert estimate.route(g)["route"] in ("upper", "lower") and estimate.route("a:f4progress") is None
    # T10: practice since a date moves U4's S
    for i in range(30):
        add("attempts", learner=g, template="circles.x", seed=5000 + i, topic="circles", difficulty="medium", fmt="mcq",
            correct=1, ms=90000, at=at(TODAY))
    assert estimate.practice_delta(g, at(TODAY - dt.timedelta(days=1)))["pts"] > 0
    # T8: the time cost, and the same figure in gains' extras
    pace = {"forecast": {"blanks": 2, "runs_out_at": 20,
                         "strip": [{"slot": i, "tier": "medium", "ms": 100000} for i in range(22)],
                         "m2_blank_tiers": ["medium", "medium"]}}
    ace = "a:f4ace"
    for i in range(40):
        add("attempts", learner=ace, template="lin.x", seed=i, topic="linear_functions",
            difficulty=("easy", "medium", "hard")[i % 3], fmt="mcq", correct=1, at=at(TODAY))
    m = estimate.model(estimate._rows(ace))
    want = estimate._round5(m["S"] - scoring._interpolate(m["F"] - 8 / 96))
    assert estimate.time_cost(ace, pace) == want
    assert estimate.time_cost(ace, {"forecast": {"blanks": 0, "strip": [], "runs_out_at": None}}) == 0
    # U9: the projection
    three = estimate.project([(dt.date(2026, 9, 1), 500), (dt.date(2026, 9, 15), 560), (dt.date(2026, 9, 22), 600)],
                             dt.date(2026, 11, 7), 70)
    assert three["mid"] < 700
    assert estimate.project([(dt.date(2026, 9, 1), 500), (dt.date(2026, 9, 15), 560)], dt.date(2026, 11, 7), 70) is None
    # X15: growth needs 20 peers; calibration pairs an outside score with a nearby section
    assert estimate.growth(learner) is None
    grow = "a:f4grow"
    for sid, who, back, low in [("f4-grow-1", grow, 60, 440), ("f4-grow-2", grow, 20, 520), ("f4-grow-3", grow, 10, 560)] + \
            [(f"f4-gpeer-{i}-{n}", f"a:f4gpeer{i}", back, low) for i in range(20) for n, back, low in ((1, 60, 440), (2, 5, 460))]:
        stamp = at(TODAY - dt.timedelta(days=back))
        add("sessions", id=sid, kind="mock", learner=who, started=stamp, finished=stamp,
            result=json.dumps({"estimate": {"low": low, "high": low + 80}}))
    add("outside_scores", id="f4-grow-bb", learner=grow, day=str(TODAY), math=620, source="bluebook", at=progress.now())
    # mean3 = (620 + 600 + 560) / 3 -> 590, so +110 from 480; each peer 500 - 480 = +20
    assert estimate.growth(grow) == {"since_first": 110, "first": 480, "n": 20, "pct": 100}, estimate.growth(grow)
    add("outside_scores", id="bb-f4", learner=learner, day=str(TODAY - dt.timedelta(days=1)), math=610,
        source="bluebook", at=progress.now())
    assert estimate.calibration(learner)["pairs"][0]["inside"] is True

    assert satdates.SAT_DATES == tuple(sorted(satdates.SAT_DATES))
    assert satdates.registration("2026-11-07", None, dt.date(2026, 10, 18))["days_left"] == 5
    assert all("register_by" in d for d in satdates.dates(dt.date(2026, 9, 24)))


def routes(client):
    h = {"X-Learner": "a:f4prefs"}
    fresh = client.get("/api/me", headers={"X-Learner": "a:f4fresh"}).json()
    assert fresh["prefs"]["words_from"] == ["sat", "transitions"]
    assert fresh["profile"]["account"] == {"linked": False, "email": None, "since": None}
    assert fresh["review"]["due_left"] == 0
    assert client.put("/api/me", headers=h, json={"prefs": {"bogus": True}}).status_code == 422
    assert client.put("/api/me", headers=h, json={"prefs": {"theme": "nope"}}).status_code == 422
    a = client.put("/api/me", headers=h, json={"prefs": {"theme": "dark", "words_from": ["sat"]}})
    assert a.status_code == 200, a.text
    b = client.put("/api/me", headers=h, json={"prefs": {"set_length": 20}})
    assert b.status_code == 200 and b.json()["profile"]["prefs"]["theme"] == "dark"
    stored = json.loads(db.one("SELECT prefs FROM learners WHERE id=?", "a:f4prefs")["prefs"])
    assert stored == {"theme": "dark", "words_from": ["sat"], "set_length": 20}
    for bad in ({"words_from": ["math"]}, {"words_goal": 41}, {"mode": "x"}, {"test_timing": "x3"},
                {"practice": {"math": {"presets": [{"name": f"p{i}", "body": {}} for i in range(9)]}}},
                {"practice": {"xx": {}}}, {"quiet": {"from": "25:00", "to": "07:00"}}):
        r = client.put("/api/me", headers=h, json={"prefs": bad})
        assert r.status_code == 422 and next(iter(bad)) in r.text, (bad, r.text)
    for good in ({"words_goal": 40}, {"words_goal": "auto"}, {"test_timing": "x0.85"}, {"repairs": "later"},
                 {"review_minutes": 0}, {"registered": "2026-11-07"}, {"practice": {"math": {"zone": "warm"}}}):
        assert client.put("/api/me", headers=h, json={"prefs": good}).status_code == 200, good
    assert client.put("/api/me", headers=h, json={"prefs": {"theme": None}}).json()["profile"]["prefs"]["theme"] == "light"
    listing = client.get("/api/prefs").json()
    assert {k["key"] for k in listing} == set(prefs.KEYS) and all(k["label"] for k in listing)
    assert any("calculator" in k["synonyms"] for k in listing if k["key"] == "calc_button")
    # U15: the stage follows the exam date; yours wins; null goes back to the stage
    st = {"X-Learner": "a:f4stage"}
    client.put("/api/me", headers=st, json={"exam_date": str(TODAY + dt.timedelta(days=30))})
    me = client.get("/api/me", headers=st).json()
    assert me["prefs"]["clock"] == "pace" and me["pref_source"]["clock"] == "stage" and me["stage"]["name"] == "build"
    me = client.put("/api/me", headers=st, json={"prefs": {"clock": "off"}}).json()["profile"]
    assert me["pref_source"]["clock"] == "yours" and me["prefs"]["clock"] == "off"
    me = client.put("/api/me", headers=st, json={"prefs": {"clock": None}}).json()["profile"]
    assert me["pref_source"]["clock"] == "stage"
    client.put("/api/me", headers=st, json={"exam_date": str(TODAY + dt.timedelta(days=10))})
    assert client.get("/api/me", headers=st).json()["prefs"]["feedback"] == "end"
    assert prefs.for_source("a:f4stage", "redo")["feedback"] == "instant"
    assert prefs.for_source("a:f4stage", "builder")["feedback"] == "end"
    # U29: your name is private and any script; the board name is unique
    assert client.put("/api/me", headers=h, json={"name": "José"}).status_code == 200
    assert client.put("/api/me", headers=h, json={"name": "李明"}).status_code == 200
    r = client.put("/api/me", headers=h, json={"name": "Dana2"})
    assert r.status_code == 422 and "name" in r.text
    assert client.put("/api/me", headers={"X-Learner": "a:f4emma1"}, json={"name": "Emma"}).status_code == 200
    assert client.put("/api/me", headers={"X-Learner": "a:f4emma2"}, json={"name": "Emma"}).status_code == 200
    assert client.put("/api/me", headers={"X-Learner": "a:f4emma1"}, json={"handle": "Emma_R"}).status_code == 200
    r = client.put("/api/me", headers={"X-Learner": "a:f4emma2"}, json={"handle": "emma_r"})
    assert r.status_code == 409 and "handle" in r.text
    assert client.put("/api/me", headers=h, json={"handle": "Student 4f2a"}).status_code == 422
    assert client.put("/api/me", headers=h, json={"country": "XX"}).status_code == 422
    for field in ("exam_date", "days"):                                    # "" is neither a value nor a clear
        r = client.put("/api/me", headers=h, json={field: ""})
        assert r.status_code == 422 and field in r.text, (field, r.text)
        assert client.put("/api/me", headers=h, json={field: None}).json()["profile"][field] is None

    def failed_mirror(_learner, _fields):
        raise RuntimeError("plan mirror failed")
    with patch("server.api_me.part", return_value=failed_mirror):
        try:
            client.put("/api/me", headers=h, json={"target": 700, "prefs": {"theme": "light"}})
            raise AssertionError("the injected mirror failure was not reached")
        except RuntimeError:
            pass
    rolled_back = client.get("/api/me", headers=h).json()["profile"]
    assert rolled_back["target"] is None and rolled_back["prefs"]["theme"] == "light"
    me = client.get("/api/me", headers=h).json()
    assert me["review"]["open"] == 0 and "due_left" in me["review"]
    activity = client.get("/api/me/activity?weeks=26", headers=h)
    assert activity.status_code == 200 and len(activity.json()["days"]) == 182
    # R6 / P21 / V19: notes, type rules, and empty values deleting the row
    add("sessions", id="notes-f4", kind="drill", learner="a:f4prefs", started=progress.now(),
        questions=json.dumps([q(96)]))
    note = client.post("/api/notes", headers=h, json={"session": "notes-f4", "question_id": "q96",
                                                       "note": "Remember the sign", "marks": [{"style": "underline", "note": "This phrase"}]})
    assert note.status_code == 200, note.text
    assert "template" not in note.json()
    assert db.one("SELECT note FROM notes WHERE learner=? AND template=? AND seed=?",
                  "a:f4prefs", "lin.evaluate", 96)["note"] == "Remember the sign"
    assert client.post("/api/notes", headers={"X-Learner": "a:f4other"}, json={"session": "notes-f4", "question_id": "q96"}).status_code == 403
    gone = client.post("/api/notes", headers=h, json={"session": "notes-f4", "question_id": "q96", "note": "", "marks": []})
    assert gone.json()["deleted"] and "template" not in gone.json() and not db.one("SELECT 1 FROM notes WHERE learner=? AND seed=96", "a:f4prefs")
    # R6: a note from any sitting kind that carries its questions; a paper with none is 404, not 500
    for kind, paper, qid in (("spot", [q(90)], "q90"), ("custom", [q(91)], "q91"), ("words", [q(92)], "q92"),
                             ("section", {"module1": [q(93)], "module2": [q(94)]}, "q94")):
        add("sessions", id=f"notes-{kind}", kind=kind, learner="a:f4prefs", started=progress.now(), questions=json.dumps(paper))
        r = client.post("/api/notes", headers=h, json={"session": f"notes-{kind}", "question_id": qid, "note": "x"})
        assert r.status_code == 200 and "template" not in r.json(), (kind, r.text)
    add("sessions", id="notes-empty", kind="spot", learner="a:f4prefs", started=progress.now())
    assert client.post("/api/notes", headers=h, json={"session": "notes-empty", "question_id": "q1", "note": "x"}).status_code == 404
    assert client.post("/api/notes", headers=h, json={"session": "notes-spot", "question_id": "q404", "note": "x"}).status_code == 404
    progress.record("a:f4prefs", None, q(97), 1)
    aid = db.one("SELECT id FROM attempts WHERE learner=? AND seed=97", "a:f4prefs")["id"]
    rule = client.post("/api/notes", headers=h, json={"attempt_id": aid, "scope": "type", "note": "check the sign"})
    assert rule.status_code == 200 and rule.json()["template"] == "lin.evaluate" and db.one("SELECT note FROM notes WHERE learner=? AND template='lin.evaluate' AND seed=-1",
                                              "a:f4prefs")["note"] == "check the sign"
    assert client.post("/api/notes", headers={"X-Learner": "a:f4other"},
                       json={"attempt_id": aid, "scope": "type", "note": "x"}).status_code == 404
    assert client.put("/api/me", headers={"X-Learner": "sample:f4"}, json={"name": "Sam"}).status_code == 403
    assert client.get("/api/me", headers={"X-Learner": "sample:f4"}).status_code == 200
    # SR24: the live sample report can't be claimed by carrying it
    add("sessions", id="f4-sample-sitting", kind="section", learner="sample:report", started=progress.now())
    r = client.post("/api/me/carry", headers={"X-Learner": "a:f4thief"}, json={"learner": "sample:report"})
    assert r.status_code == 403, r.text
    assert db.one("SELECT learner FROM sessions WHERE id='f4-sample-sitting'")["learner"] == "sample:report"
    # U21: device tokens, revocation, idle shared computers and the swap window
    token = deps.mint_device("a:f4device", "passkey", "Chrome on Mac")
    assert client.get("/api/me", headers={"X-Learner": token}).json()["profile"]["id"] == "a:f4device"
    shared = deps.mint_device("a:f4device", "passkey", session_only=True)
    db.run("UPDATE devices SET last_seen=? WHERE token=?",
           (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=16)).isoformat(), shared)
    r = client.get("/api/me", headers={"X-Learner": shared})
    assert r.status_code == 401 and r.json()["detail"]["retired"] is True
    db.run("UPDATE devices SET revoked=? WHERE token=?", progress.now(), token)
    assert client.put("/api/me", headers={"X-Learner": token}, json={"minutes": 30}).status_code == 401
    db.ensure_learner("a:f4saved")
    db.run("UPDATE learners SET swap_until=? WHERE id=?",
           (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=14)).isoformat(), "a:f4saved")
    box = {"label": "Firefox on Linux"}
    reset = deps.SWAP.set(box)
    try:
        assert deps.learner_of("a:f4saved") == "a:f4saved" and box["token"].startswith("d:")
    finally:
        deps.SWAP.reset(reset)
    assert deps.learner_of(box["token"]) == "a:f4saved"
    # over HTTP: the header reaches the browser and its token works (shell-me U21 acceptance 4)
    from fastapi import FastAPI
    from server import api_me
    mini = FastAPI()
    mini.middleware("http")(deps.swap_middleware)
    mini.include_router(api_me.router)
    installed = any(getattr(m, "kwargs", {}).get("dispatch") is deps.swap_middleware for m in app.user_middleware)
    for c in (TestClient(mini),) + ((client,) if installed else ()):
        r = c.get("/api/me", headers={"X-Learner": "a:f4saved", "User-Agent": "Mozilla/5.0 (Macintosh; Mac OS X) Chrome/120"})
        swapped = r.headers.get("X-Learner-Swap", "")
        assert r.status_code == 200 and swapped.startswith("d:"), r.headers
        assert c.get("/api/me", headers={"X-Learner": swapped}).json()["profile"]["id"] == "a:f4saved"
        assert db.one("SELECT label, method FROM devices WHERE token=?", swapped)["method"] == "swap"
    if not installed:
        print("PENDING  app.py does not install deps.swap_middleware (its owner adds"
              " app.middleware('http')(deps.swap_middleware)); checked on a mini app instead")
    db.run("UPDATE learners SET swap_until=? WHERE id=?", progress.now(), "a:f4saved")
    assert client.get("/api/me", headers={"X-Learner": "a:f4saved"}).status_code == 401
    # Shell §3.1.5: a rotated-away code is 401 on writes, reads get its own
    # empty data, and /api/shell can tell (is_retired)
    add("retired", code="a:f4rotated", into="a:f4device", at=progress.now())
    got = client.get("/api/me", headers={"X-Learner": "a:f4rotated"})
    assert got.status_code == 200 and got.json()["profile"]["id"] == "a:f4rotated", got.text
    r = client.put("/api/me", headers={"X-Learner": "a:f4rotated"}, json={"minutes": 30})
    assert r.status_code == 401 and r.json()["detail"] == {"retired": True, "into": None}, r.text
    assert client.post("/api/notes", headers={"X-Learner": "a:f4rotated"}, json={"attempt_id": 1}).status_code == 401
    assert deps.is_retired("a:f4rotated") and not deps.is_retired("a:f4device")
    for method, refused in (("GET", False), ("POST", True), ("DELETE", True)):
        reset = deps.SWAP.set({"label": "Browser", "method": method})
        try:
            deps.learner_of("a:f4rotated")
            assert not refused, method
        except HTTPException as e:
            assert refused and e.status_code == 401, method
        finally:
            deps.SWAP.reset(reset)
    # U21's transfer code: 8 characters of A-HJ-NP-Z2-9, unique across contests and transfers
    code = db.new_code(8)
    assert len(code) == 8 and set(code) <= set(db.CODE_ALPHABET) and not set(code) & set("IO01")
    assert len(db.new_code()) == 6
    add("transfers", code="AAAAAAAA", learner="a:f4saved", expires=progress.now())
    picks = iter("A" * 8 + "B" * 8)
    with patch.object(db.secrets, "choice", lambda _alphabet: next(picks)):
        assert db.new_code(8) == "BBBBBBBB"


def integrity():
    learner = "a:f4access"
    live = q(91)
    add("sessions", id="live-f4", kind="module", learner=learner, started=progress.now(),
        questions=json.dumps({"module1": [live]}))
    assert deps.access(learner, live["key"], live["seed"]) is None
    for day in deps.live_days():               # a challenge is protected wherever its day is still today
        db.run("INSERT INTO challenges(day,questions,built) VALUES (?,?,?)"
               " ON CONFLICT(day) DO UPDATE SET questions=excluded.questions", day, json.dumps([q(92)]), progress.now())
    assert deps.access(learner, "lin.evaluate", 92) is None
    ahead = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=14)).date().isoformat()
    assert ahead in deps.live_days()
    add("sessions", id="f4-twin", kind="challenge", learner="a:f4twin", started=progress.now(), day=ahead,
        finished=progress.now(), questions=json.dumps([q(95)]))
    progress.record("a:f4twin", "f4-twin", q(95), 0)
    assert deps.access("a:f4twin", "lin.evaluate", 95) is None
    add("contests", id="f4-live", kind="private", opens=at(TODAY - dt.timedelta(days=1)),
        closes=at(TODAY + dt.timedelta(days=1)))
    add("contest_items", contest="f4-live", template="lin.evaluate", seed=98)
    progress.record(learner, None, q(98), 0)
    assert deps.access(learner, "lin.evaluate", 98) is None
    add("saved", learner=learner, template="lin.evaluate", seed=93, topic="linear_functions", at=progress.now())
    assert deps.access(learner, "lin.evaluate", 93) == "kept"
    progress.record(learner, None, q(94), 0)
    assert deps.access(learner, "lin.evaluate", 94) == "reveal"
    db.run("UPDATE sessions SET finished=? WHERE id='live-f4'", progress.now())
    assert deps.access(learner, "lin.evaluate", 91) == "reveal"            # on a finished paper
    assert deps.access(learner, "lin.evaluate", 91, exclude="live-f4") is None
    add("flags", learner=learner, session="live-f4", qid="q91", template="lin.evaluate", seed=91,
        topic="linear_functions", at=progress.now())
    assert deps.access(learner, "lin.evaluate", 91) == "reveal"
    # R19 at scale: every answer's access() reads only indexed slices of the site's sittings
    seen, real_rows, real_one = [], db.rows, db.one
    with patch.object(db, "rows", lambda sql, *a: seen.append((sql, a)) or real_rows(sql, *a)), \
            patch.object(db, "one", lambda sql, *a: seen.append((sql, a)) or real_one(sql, *a)):
        deps.access(learner, "lin.evaluate", 4242)
    for sql, a in seen:
        if "learner=?" not in sql:
            plan = " ".join(r["detail"] for r in real_rows("EXPLAIN QUERY PLAN " + sql, *a))
            assert "SCAN" not in plan, (sql, plan)


def carry():
    src, dst = "a:f4source", "a:f4target"
    db.ensure_learner(src)
    db.ensure_learner(dst)
    stamp = progress.now()
    db.run("UPDATE learners SET rating=1400, rated=200 WHERE id=?", src)
    db.run("UPDATE learners SET rating=1000, rated=3 WHERE id=?", dst)
    add("users", id="carry-user", first="", last="", email="carry@example.test", created=stamp, learner=src)
    add("attempts", learner=src, template="lin.evaluate", seed=801, topic="linear_functions", difficulty="easy", fmt="mcq", correct=1, at=stamp)
    add("sessions", id="carry-session", learner=src, started=stamp)
    add("sessions", id="carry-contest-a", learner=src, started=at(TODAY, 1), contest="c1", ranked=1)
    add("sessions", id="carry-contest-b", learner=dst, started=at(TODAY, 2), contest="c1", ranked=1)
    add("practice_seen", learner=src, template="lin.evaluate", seed=801, stem="stem", at=stamp)
    add("traps", learner=src, template="lin.evaluate", norm="error", reason="error", label="Error", topic="linear_functions", owed=2, opened=stamp, last=stamp)
    add("saved", learner=src, template="lin.evaluate", seed=801, topic="linear_functions", at=stamp)
    add("flags", learner=src, session="carry-session", qid="q1", template="lin.evaluate", seed=801, topic="linear_functions", at=stamp)
    add("notes", learner=src, template="lin.evaluate", seed=801, note="note", marks="[]", at=stamp)
    add("links", token="carry-link", learner=src, kind="progress", created=stamp)
    add("pairs", code="carry-pair", learner=src, created=stamp)
    add("reports", learner=src, kind="question", at=stamp)
    add("earned", learner=src, id="streak", tier=1, at=stamp)
    add("tries", learner=src, session="carry-session", qid="q1", n=1, at=stamp)
    add("outside_scores", id="carry-score", learner=src, day=str(TODAY), math=500, at=stamp)
    add("plans", id="carry-plan", learner=src, created=stamp)
    add("plans", id="carry-plan-dst", learner=dst, created=stamp)
    for table in ("plan_days", "plan_overrides", "plan_marks", "plan_snapshots"):
        add(table, plan="carry-plan", **({"made_on": str(TODAY)} if table == "plan_snapshots" else {"day": str(TODAY)}),
            **({"task": "t1"} if table == "plan_marks" else {}))
    add("plan_tasks", id="carry-task", plan="carry-plan", day=str(TODAY))
    add("plan_events", plan="carry-plan", at=stamp, kind="edit")
    add("posts", id=991, learner=src, at=stamp)
    add("post_votes", post=991, learner=src, kind="helpful")
    add("contest_members", contest="carry-contest", learner=src, joined=stamp)
    add("name_reports", target=src, reporter=src, at=stamp)
    add("word_state", learner=src, word="abate", box=2, reps=2, right=1, wrong=1)
    add("word_reviews", id=991, learner=src, word="abate", kind="review", at=stamp)
    add("my_words", id="carry-word", learner=src, word="abate")
    add("skill_ratings", learner=src, topic="circles", rating=1300, n=40, seed="none")
    add("skill_ratings", learner=dst, topic="circles", rating=900, n=2, seed="none")
    add("skill_ratings", learner=src, topic="probability", rating=800, n=1, seed="none")
    add("skill_ratings", learner=dst, topic="probability", rating=1200, n=9, seed="none")
    add("trap_log", learner=src, template="lin.evaluate", norm="error", at=stamp, event="open")
    add("due_days", learner=src, subject="math", day=str(TODAY), keys="[]")
    add("passkeys", cred_id="carry-cred", learner=src, created=stamp)
    add("webauthn_challenges", challenge="carry-ch", learner=src, purpose="login", expires=stamp)
    add("devices", token="d:carry", learner=src, created=stamp)
    add("transfers", code="CARRY123", learner=src, expires=stamp)
    add("week_goals", learner=src, week="2026-W39", id="g1", kind="minutes", target=60, created=stamp)
    add("push_subs", id="carry-push", learner=src, endpoint="https://push.example/1", created=stamp)
    add("champions", kind="week", period="2026-W38", board="points", place=1, learner=src, value=90)
    add("rw_log", learner=src, at=stamp, source="task", domain="Craft and Structure", missed=2, of=10)
    add("word_lists", learner=src, name="mine", words='["abate"]', created=stamp)
    add("word_lists", learner=dst, name="mine", words='["candid"]', created=stamp)
    add("traps", learner=dst, template="lin.evaluate", norm="error", reason="error", label="Error", topic="linear_functions",
        owed=0, opened=stamp, last=stamp, closed=stamp, closed_how="fixed", due="2026-09-13", checks=1)
    add("official_done", learner=src, cb_id="84664a7c", pick="C", right=0, ms=1000, at=stamp)
    add("rank_snapshots", day=str(TODAY), board="points", learner=src, rank=3, value=40)
    add("follows", learner=src, target="a:f4friend", at=stamp)
    add("nudges", sender=src, target="a:f4friend", contest="c1", round=1, at=stamp)
    add("sets", code="CARRYSET", owner=src, kind="set", created=stamp)
    add("contests", id="carry-own", owner=src, kind="private", created=stamp)
    add("retired", code="a:f4carryold", into=src, at=stamp)
    for sid, who, day, hour in (("carry-ch-a", src, TODAY, 1), ("carry-ch-b", dst, TODAY, 2),
                                ("carry-ch-c", src, TODAY - dt.timedelta(days=1), 3)):
        add("sessions", id=sid, kind="challenge", learner=who, day=str(day), started=at(TODAY, hour), ranked=1)
    assert progress.carry(src, dst) == 3
    for table, where in db.LEARNER_TABLES.items():
        found = lambda who: db.conn().execute(f"SELECT 1 FROM {table} WHERE {where}", {"l": who}).fetchone()  # noqa: E731
        assert found(dst) or table == "pairs", table
        assert not found(src), table
    lr = db.one("SELECT rating, rated FROM learners WHERE id=?", dst)
    assert (lr["rating"], lr["rated"]) == (1400, 200)
    assert db.one("SELECT rating FROM skill_ratings WHERE learner=? AND topic='circles'", dst)["rating"] == 1300
    assert db.one("SELECT rating FROM skill_ratings WHERE learner=? AND topic='probability'", dst)["rating"] == 1200
    assert db.one("SELECT archived FROM plans WHERE id='carry-plan'")["archived"]
    assert db.one("SELECT archived FROM plans WHERE id='carry-plan-dst'")["archived"] is None
    ranked = {r["id"]: (r["ranked"], r["unranked_why"]) for r in db.rows("SELECT * FROM sessions WHERE contest='c1'")}
    assert ranked == {"carry-contest-a": (1, None), "carry-contest-b": (0, "repeat")}, ranked
    ranked = {r["id"]: (r["ranked"], r["unranked_why"]) for r in db.rows("SELECT * FROM sessions WHERE id LIKE 'carry-ch-%'")}
    assert ranked == {"carry-ch-a": (1, None), "carry-ch-b": (0, "repeat"), "carry-ch-c": (1, None)}, ranked
    assert db.one('SELECT "into" FROM retired WHERE code=?', "a:f4carryold")["into"] == dst
    assert json.loads(db.one("SELECT words FROM word_lists WHERE learner=? AND name='mine'", dst)["words"]) == ["candid", "abate"]
    t = trap(dst, template="lin.evaluate", norm="error")                    # open under the source: open, no fix shown
    assert (t["closed"], t["closed_how"], t["due"], t["checks"], t["owed"]) == (None, None, None, 0, 2), dict(t)
    for a, b in (("sample:report", dst), (dst, "sample:report")):
        try:
            progress.carry(a, b)
            raise AssertionError(f"carried {a} into {b}")
        except HTTPException as e:
            assert e.status_code == 403


def check(client):
    checks()
    days_checks()
    causes_checks()
    estimate_checks()
    routes(client)
    integrity()
    carry()
    print("ok  F4 schema, traps and check-ins, days, causes, pace, estimate, prefs, access and carry")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="satf-f4-") as path:
        db.DB_PATH = pathlib.Path(path) / "f4-check.db"
        db.init()
        with TestClient(app) as client:
            check(client)
