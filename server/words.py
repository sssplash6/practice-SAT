"""SAT Reading & Writing words: content, review state, and generated study items.

The public API lives in api_words. This module owns all review transitions so a
card, an inline sample, a worksheet, and the daily item use the same rules.
"""

from __future__ import annotations

import datetime as dt
import copy
import hashlib
import json
import os
import random
import re
import unicodedata
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException

from . import db

HERE = Path(__file__).with_name("words")
INDEX = Path(__file__).with_name("words_index.json")
INTERVALS = {1: 1, 2: 3, 3: 7, 4: 16, 5: 35}
PROOF_KINDS = frozenset({"incontext", "nearly", "transition", "precise"})
SELF_KINDS = frozenset({"card", "cards", "self", "sort", "placement", "sheet-grade"})
ACHIEVEMENTS = [{"id": f"words-{n}", "kind": "words_known", "target": n}
                for n in (50, 250, 1000)]
RW_TO_ATTEMPTS = """INSERT INTO attempts(learner,session,qid,template,seed,topic,difficulty,fmt,correct,reason,given,conf,ms,at)
SELECT learner, session, 'w' || id, template, seed,
CASE skill WHEN 'Transitions' THEN 'rw.transitions' ELSE 'rw.words_in_context' END,
difficulty, 'mcq', correct, trap, given, conf, ms, at FROM word_reviews
WHERE subject='rw' AND template IS NOT NULL AND correct IS NOT NULL"""


def _load(name: str):
    value = json.loads((HERE / f"{name}.json").read_text(encoding="utf-8"))
    return value if isinstance(value, list) else value.get("entries", value)


@lru_cache(maxsize=1)
def content() -> dict:
    sat, transitions = _load("sat"), _load("transitions")
    transition_data = json.loads((HERE / "transitions.json").read_text(encoding="utf-8"))
    frames, pairs = _load("frames"), _load("pairs")
    entries = {w["slug"]: w for w in sat + transitions}
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    return {"entries": entries, "sat": sat, "transitions": transitions,
            "transition_data": transition_data,
            "frames": {f["id"]: f for f in frames}, "pairs": {p["id"]: p for p in pairs},
            "confusions": {c["id"]: c for c in _load("confusions")},
            "roots": {r["id"]: r for r in _load("roots")},
            "classes": {c["id"]: c for c in _load("classes")},
            "traps": {t["id"]: t for t in _load("traps")},
            "fills": json.loads((HERE / "fills.json").read_text(encoding="utf-8"))["pools"],
            "collections": json.loads((HERE / "collections.json").read_text(encoding="utf-8"))["groups"],
            "index": idx}


def init() -> None:
    """Add S9 columns here; app.py already calls module init functions."""
    c = db.conn()
    additions = {
        "word_state": {"proven": "TEXT", "placed": "INTEGER DEFAULT 0", "hook": "TEXT",
                       "pending_know": "TEXT", "thought_at": "TEXT", "looked_at": "TEXT",
                       "stubborn_right_day": "TEXT", "stubborn_cleared": "TEXT",
                       "sentence_history": "TEXT"},
        "word_reviews": {"template": "TEXT", "seed": "INTEGER", "trap": "TEXT", "conf": "TEXT",
                         "gap": "TEXT", "subject": "TEXT", "skill": "TEXT", "domain": "TEXT",
                         "difficulty": "TEXT", "attempt": "INTEGER DEFAULT 1",
                         "state_before": "TEXT"},
    }
    for table, columns in additions.items():
        have = {r["name"] for r in c.execute(f"PRAGMA table_info({table})")}
        for column, declaration in columns.items():
            if column not in have:
                c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {declaration}")
    c.execute("CREATE INDEX IF NOT EXISTS word_reviews_template ON word_reviews(template)")
    c.execute("CREATE INDEX IF NOT EXISTS word_reviews_learner_word ON word_reviews(learner,word,id)")
    c.execute("CREATE TABLE IF NOT EXISTS word_fit_reports (frame TEXT NOT NULL, word TEXT NOT NULL,"
              " learner TEXT NOT NULL, at TEXT NOT NULL, PRIMARY KEY(frame,word,learner))")
    c.commit()
    content()


def local_day(tz: int = 0, at: str | dt.datetime | None = None) -> dt.date:
    moment = dt.datetime.fromisoformat(at) if isinstance(at, str) else at
    moment = moment or dt.datetime.now(dt.timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=dt.timezone.utc)
    return (moment.astimezone(dt.timezone.utc) - dt.timedelta(minutes=tz)).date()


def _stamp(at: str | None = None) -> str:
    if at:
        moment = dt.datetime.fromisoformat(at)
        if moment.tzinfo is None:
            raise HTTPException(422, "review time must include a timezone")
        now = dt.datetime.now(dt.timezone.utc)
        if moment > now or moment < now - dt.timedelta(hours=72):
            raise HTTPException(422, "review time must be within the last 72 hours")
        return moment.astimezone(dt.timezone.utc).isoformat(timespec="seconds")
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def entry(slug: str, learner: str | None = None) -> dict | None:
    known = content()["entries"].get(slug)
    if known:
        return known
    if slug.startswith("u:") and learner:
        row = db.one("SELECT * FROM my_words WHERE id=? AND learner=?", slug, learner)
        if row:
            own = dict(row)
            return {"slug": slug, "word": own["word"], "sense": "", "pos": own["pos"],
                    "meaning": own["meaning"], "short": own["meaning"][:60],
                    "examples": [own["example"]] if own["example"] else [],
                    "same": json.loads(own["same"] or "[]"),
                    "opposite": json.loads(own["opposite"] or "[]"),
                    "notes": own["notes"], "collection": own["list"], "own": True,
                    "level": "medium", "freq_band": 3, "lists": []}
    return None


def state(learner: str, slug: str) -> dict:
    row = db.one("SELECT * FROM word_state WHERE learner=? AND word=?", learner, slug)
    return dict(row) if row else {"learner": learner, "word": slug, "box": 0, "due": None,
                                  "reps": 0, "lapses": 0, "right": 0, "wrong": 0,
                                  "saved": 0, "first": None, "last": None, "lastday": None,
                                  "lastwrong": None, "proven": None, "placed": 0,
                                  "hook": None, "pending_know": None, "thought_at": None,
                                  "looked_at": None, "stubborn_right_day": None,
                                  "stubborn_cleared": None, "sentence_history": None}


def _upsert_state(c, s: dict) -> None:
    fields = ("learner", "word", "box", "due", "reps", "lapses", "right", "wrong", "saved",
              "first", "last", "lastday", "lastwrong", "proven", "placed", "hook",
              "pending_know", "thought_at", "looked_at", "stubborn_right_day",
              "stubborn_cleared", "sentence_history")
    c.execute(f"INSERT INTO word_state({','.join(fields)}) VALUES ({','.join('?' for _ in fields)}) "
              f"ON CONFLICT(learner,word) DO UPDATE SET "
              + ",".join(f"{f}=excluded.{f}" for f in fields if f not in ("learner", "word")),
              tuple(s.get(f) for f in fields))


def _exam(learner: str) -> dt.date | None:
    row = db.one("SELECT exam_date FROM learners WHERE id=?", learner)
    return dt.date.fromisoformat(row["exam_date"]) if row and row["exam_date"] else None


def _due(day: dt.date, box: int, learner: str, *, word: str = "", reps: int = 0,
         stubborn: bool = False) -> str:
    interval = INTERVALS[box]
    if stubborn:
        interval = {1: 1, 2: 2, 3: 5}.get(box, interval)
    factor = recall(learner)["scale"]
    interval = max(1, round(interval * max(.5, min(2, factor))))
    if interval >= 3:
        # Stable fuzz spreads words reviewed together across adjacent due days.
        interval = max(1, interval + round(interval * ((int.from_bytes(
            hashlib.sha256(f"{learner}:{word}:{reps}:{box}".encode()).digest()[:2], "big") / 65535) * .2 - .1)))
    due = day + dt.timedelta(days=interval)
    exam = _exam(learner)
    if exam and due >= exam:
        due = max(day + dt.timedelta(days=1), exam - dt.timedelta(days=1))
    return due.isoformat()


def _review_row(c, learner: str, slug: str, session: str | None, mode: str, kind: str,
                correct: bool | None, given: str | None, box_before: int, due_before: str | None,
                ms: int | None, at: str, *, template: str | None = None, seed: int | None = None,
                trap: str | None = None, conf: str | None = None, gap: str | None = None,
                attempt: int = 1, state_before: dict | None = None) -> int:
    word = entry(slug, learner) or {}
    skill = "Transitions" if word.get("collection") == "transitions" else "Words in Context"
    subject = "rw" if template else None
    return c.execute("INSERT INTO word_reviews(learner,word,session,mode,kind,correct,given,confusion,"
                     "box_before,due_before,ms,at,template,seed,trap,conf,gap,subject,skill,domain,difficulty,attempt,state_before)"
                     " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     (learner, slug, session, mode, kind, None if correct is None else int(correct),
                      given, trap, box_before, due_before, ms, at, template, seed, trap, conf,
                      gap, subject, skill if subject else None,
                      ("Expression of Ideas" if skill == "Transitions" else "Craft and Structure")
                      if subject else None,
                      word.get("level") if subject else None, attempt,
                      json.dumps(state_before) if state_before else None)).lastrowid


def grade(learner: str, word: str, ok: bool, mode: str = "cards", kind: str = "cards",
          ms: int | None = None, session: str | None = None, confusion: str | None = None,
          tz: int = 0, *, given: str | None = None, conf: str | None = None,
          template: str | None = None, seed: int | None = None, gap: str | None = None,
          hinted: bool = False, at: str | None = None, attempt: int = 1) -> dict:
    """Apply the proof ladder and return a verdict. One call grades one target only."""
    if not entry(word, learner):
        raise HTTPException(404, "unknown word")
    stamp = _stamp(at)
    day = local_day(tz, stamp)
    with db.atomic() as c:
        s = state(learner, word)
        prior = s.copy()
        was_stubborn = int(s["lapses"] or 0) >= 4
        before, due_before = int(s["box"] or 0), s["due"]
        early = bool(due_before and due_before > day.isoformat())
        lastday = s["lastday"] == day.isoformat()
        self_grade = kind in SELF_KINDS or kind == "cards"
        proof = kind in PROOF_KINDS or (word.startswith("u:") and kind in {"meaning2word", "typed"})
        passive = mode in {"sprint", "order", "lookup", "outside"} or kind in {"order", "rootshare"}
        after = before
        promoted = False
        if passive:
            if not ok:
                s["lastwrong"] = stamp
        elif not ok:
            after = 0 if int(s.get("placed") or 0) == 2 else 1
            s["proven"] = None
            s["placed"] = 0
            s["stubborn_right_day"] = None
            s["lapses"] = int(s["lapses"] or 0) + 1
            s["lastwrong"] = stamp
            s["due"] = day.isoformat()
            if not self_grade and s.get("pending_know"):
                s["thought_at"] = stamp
                s["pending_know"] = None
        elif conf == "guess" or hinted:
            s["due"] = (day + dt.timedelta(days=1)).isoformat()
        elif early or lastday:
            pass
        elif int(s.get("placed") or 0) == 2 and proof:
            after = 4
            promoted = True
            s["placed"] = 0
            s["proven"] = day.isoformat()
            s["due"] = _due(day, after, learner, word=word, reps=int(s["reps"] or 0), stubborn=was_stubborn)
        elif kind == "decode" and before == 0:
            after = 1
            promoted = True
            s["due"] = _due(day, after, learner, word=word, reps=int(s["reps"] or 0), stubborn=was_stubborn)
        elif self_grade and before >= 3:
            s["due"] = (day + dt.timedelta(days=2)).isoformat() if before == 3 else _due(day, before, learner, word=word, reps=int(s["reps"] or 0), stubborn=was_stubborn)
            s["pending_know"] = stamp
        elif before >= 3 and not proof:
            # Recognition quizzes cannot certify a high-box word.
            s["due"] = (day + dt.timedelta(days=2)).isoformat() if before == 3 else due_before
        else:
            after = min(5, 2 if before == 0 else before + 1)
            promoted = after > before
            s["due"] = _due(day, after, learner, word=word, reps=int(s["reps"] or 0), stubborn=was_stubborn)
            if after >= 4 and proof:
                s["proven"] = day.isoformat()
        if after >= 4 and not s.get("proven"):
            after = 3
            s["due"] = (day + dt.timedelta(days=2)).isoformat()
        if ok and not self_grade and not passive:
            s["thought_at"] = None
            s["pending_know"] = None
            if was_stubborn:
                if s.get("stubborn_right_day") and s["stubborn_right_day"] != day.isoformat():
                    after = 2
                    s["proven"] = None
                    s["due"] = _due(day, after, learner, word=word, reps=int(s["reps"] or 0), stubborn=True)
                    s["lapses"] = 0
                    s["stubborn_cleared"] = stamp
                    s["stubborn_right_day"] = None
                else:
                    s["stubborn_right_day"] = day.isoformat()
        if ok and self_grade:
            s["pending_know"] = stamp
        s["box"] = after
        s["reps"] = int(s["reps"] or 0) + 1
        s["right" if ok else "wrong"] = int(s["right" if ok else "wrong"] or 0) + 1
        s["first"] = s["first"] or stamp
        s["last"] = stamp
        if promoted:
            s["lastday"] = day.isoformat()
        _upsert_state(c, s)
        review_id = _review_row(c, learner, word, session, mode, kind, ok, given,
                                before, due_before, ms, stamp, template=template, seed=seed,
                                trap=confusion, conf=conf, gap=gap, attempt=attempt,
                                state_before=prior)
    status = ("Hinted · no box up" if hinted and ok else
              "Guessed · review tomorrow" if conf == "guess" and ok else
              "Prove it in context to make it Known" if after == 3 and not s.get("proven")
              else "Known" if after >= 4 else "Again today" if not ok
              else "Early review" if early else "Back " + (s["due"] or "soon"))
    return {"correct": bool(ok), "word": word, "box": {"before": before, "after": after},
            "due": s["due"], "early": early, "proven": s.get("proven"), "claimed": after == 3 and not s.get("proven"),
            "status": status, "review_id": review_id, "requeued": not ok and not passive,
            "hinted": hinted, "guessed": conf == "guess"}


def place(learner: str, slug: str, choice: str, tz: int = 0, *, at: str | None = None) -> dict:
    """Placement/triage: Yes is a claim, never proof; likely-known waits for one proof."""
    if not entry(slug, learner):
        raise HTTPException(404, "unknown word")
    stamp = _stamp(at)
    day = local_day(tz, stamp)
    with db.atomic() as c:
        s = state(learner, slug)
        prior = s.copy()
        before, due_before = s["box"], s["due"]
        if choice in {"yes", "know"}:
            s["box"] = 3
            s["proven"] = None
            s["placed"] = 1
            n = int.from_bytes(hashlib.sha256(slug.encode()).digest()[:2], "big") % 12 + 3
            s["due"] = (day + dt.timedelta(days=n)).isoformat()
            s["pending_know"] = stamp
        elif choice == "probably":
            s["placed"] = 2
            s["due"] = day.isoformat()
        elif choice in {"no", "unsure"}:
            s["placed"] = -1 if choice == "no" else -2
            s["due"] = day.isoformat()
        else:
            raise HTTPException(422, "choice must be yes, no, unsure or probably")
        s["first"] = s["first"] or stamp
        s["last"] = stamp
        _upsert_state(c, s)
        review_id = _review_row(c, learner, slug, None, "placement", "sort", None, choice,
                                before, due_before, None, stamp, attempt=0, state_before=prior)
    return {"word": slug, "box": {"before": before, "after": s["box"]}, "due": s["due"],
            "claimed": s["box"] == 3, "placed": s["placed"], "review_id": review_id}


def word_reviews(learner: str, slug: str | None = None) -> list[dict]:
    sql = "SELECT * FROM word_reviews WHERE learner=?"
    args = [learner]
    if slug:
        sql += " AND word=?"
        args.append(slug)
    return [dict(r) for r in db.rows(sql + " ORDER BY id", *args)]


def restore_review(learner: str, slug: str, review_id: int) -> None:
    """Undo only a word's latest grade before replacing it in the same request."""
    with db.atomic() as c:
        latest = c.execute("SELECT id,state_before FROM word_reviews WHERE learner=? AND word=?"
                           " ORDER BY id DESC LIMIT 1", (learner, slug)).fetchone()
        if not latest or latest["id"] != review_id or not latest["state_before"]:
            raise HTTPException(409, "this grade has a newer review")
        _upsert_state(c, json.loads(latest["state_before"]))
        c.execute("DELETE FROM word_reviews WHERE id=?", (review_id,))


def rw_answers(learner: str | None = None, since: str | None = None,
               template: str | None = None) -> list[dict]:
    sql = ("SELECT learner,template,seed,word,skill,domain,difficulty,given,correct,"
           "trap,conf,ms,session,at FROM word_reviews WHERE subject='rw' AND template IS NOT NULL")
    args = []
    for clause, value in (("learner=?", learner), ("at>=?", since), ("template=?", template)):
        if value is not None:
            sql += " AND " + clause
            args.append(value)
    return [dict(r) for r in db.rows(sql + " ORDER BY at,id", *args)]


def calibration(learner: str) -> dict:
    pending: dict[str, bool] = {}
    n = held = 0
    for review in word_reviews(learner):
        if review["mode"] == "placement" and review["given"] in {"yes", "know"}:
            pending[review["word"]] = True
            continue
        if review["correct"] is None:
            continue
        if review["mode"] in {"cards", "sort", "placement", "sheet-grade"} and review["correct"]:
            pending[review["word"]] = True
        elif review["kind"] in PROOF_KINDS | {"meaning2word", "word2meaning", "typed"}:
            if pending.pop(review["word"], False):
                n += 1
                held += bool(review["correct"])
    return {"pct": round(100 * held / n) if n else None, "n": n}


def recall(learner: str, tz: int = 0) -> dict:
    """Measure only scheduled reviews; early answers and placement do not tune intervals."""
    rows = db.rows("SELECT correct,box_before,due_before,at,kind,mode FROM word_reviews"
                   " WHERE learner=? AND correct IS NOT NULL ORDER BY id DESC LIMIT 500", learner)
    due = [dict(r) for r in rows if r["box_before"] and r["due_before"] and
           r["due_before"] <= local_day(tz, r["at"]).isoformat() and
           r["mode"] not in {"sprint", "outside", "placement", "sort", "lookup", "order"} and
           r["kind"] not in {"order", "rootshare"}]
    last50 = due[:50]
    pct = round(100 * sum(r["correct"] for r in last50) / len(last50)) if last50 else None
    by_box = {}
    for box in range(1, 6):
        group = [r for r in due if r["box_before"] == box and
                 r["at"] >= (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)).isoformat()]
        by_box[str(box)] = {"n": len(group), "pct": round(100 * sum(r["correct"] for r in group) / len(group))
                            if group else None}
    scale = (1.2 if len(last50) == 50 and pct is not None and pct > 95 else
             .8 if len(last50) == 50 and pct is not None and pct < 80 else 1)
    return {"pct": pct, "n": len(last50), "by_box": by_box, "scale": scale}


def simulate(learner: str, goal: int, days: int = 45, *, lapse_override: float | None = None) -> dict:
    """Expected review load from the five review intervals, independent of storage."""
    if goal < 0 or days < 1:
        raise ValueError("goal and days must be nonnegative")
    if lapse_override is None:
        recent = db.rows("SELECT correct FROM word_reviews WHERE learner=? AND correct IS NOT NULL"
                         " AND mode NOT IN ('sprint','placement','sort','outside','lookup')"
                         " ORDER BY id DESC LIMIT 50", learner)
        lapse = 1 - sum(r["correct"] for r in recent) / len(recent) if recent else .2
    else:
        lapse = lapse_override
    # Each day's new cohort contributes to future visits, with a miss returning tomorrow.
    due = [0.0] * (days + 40)
    for day in range(days):
        due[day + 3] += goal
        for box, offset in ((2, 3), (3, 7), (4, 16), (5, 35)):
            if day + offset < len(due):
                due[day + offset] += goal * ((1 - lapse) ** max(0, box - 2))
    load = round(sum(due[7:21]) / 14) if days >= 21 else round(sum(due[:days]) / days)
    return {"goal": goal, "load_2w": load, "minutes": round(load * 10 / 60, 1),
            "lapse": round(lapse, 3)}


def _simulate_selfcheck() -> None:
    assert simulate("selfcheck", 0, lapse_override=.2)["load_2w"] == 0
    assert simulate("selfcheck", 20, lapse_override=.2)["load_2w"] > simulate("selfcheck", 5, lapse_override=.2)["load_2w"]


def _measured(slug: str) -> dict:
    prior = content()["index"]["words"][slug]["prior"]
    rows = db.rows("SELECT correct FROM word_reviews WHERE word=? AND subject='rw'"
                   " AND kind IN ('incontext','nearly','transition') AND attempt=1"
                   " AND learner NOT LIKE 'sample:%'", slug)
    n = len(rows)
    return {"pct": round(100 * (sum(r["correct"] for r in rows) + 20 * prior) / (n + 20)),
            "n": n, "prior": prior}


def _flags(learner: str, slug: str, s: dict, day: dt.date) -> dict:
    recent_wrong = bool(s["lastwrong"] and (day - local_day(0, s["lastwrong"])).days <= 14)
    last_right = db.one("SELECT at FROM word_reviews WHERE learner=? AND word=? AND correct=1"
                        " ORDER BY id DESC LIMIT 1", learner, slug)
    missed = recent_wrong and (not last_right or last_right["at"] < s["lastwrong"])
    thought = bool(s.get("thought_at") and (day - local_day(0, s["thought_at"])).days <= 30
                   and (not last_right or last_right["at"] < s["thought_at"]))
    misses = db.one("SELECT COUNT(*) n FROM word_reviews WHERE learner=? AND word=? AND correct=0"
                    " AND at>=?", learner, slug,
                    max((day - dt.timedelta(days=14)).isoformat(), s.get("stubborn_cleared") or ""))["n"]
    context = db.rows("SELECT correct FROM word_reviews WHERE learner=? AND word=?"
                      " AND kind IN ('incontext','nearly','transition') ORDER BY id DESC LIMIT 20",
                      learner, slug)
    return {"is_due": bool(s["due"] and s["due"] <= day.isoformat()),
            "missed": missed, "thought": thought,
            "stubborn": int(s["lapses"] or 0) >= 4 or misses >= 3,
            "hard_for_you": int(s["lapses"] or 0) >= 2 or thought or int(s.get("placed") or 0) == -1 or
            (len(context) >= 2 and sum(r["correct"] for r in context) / len(context) < .5),
            "looked_up": bool(s.get("looked_at") and (day - local_day(0, s["looked_at"])).days <= 30
                              and int(s["box"] or 0) < 4)}


def library(learner: str, tz: int = 0, days: int = 14) -> dict:
    data = content()
    day = local_day(tz)
    states = {r["word"]: dict(r) for r in db.rows("SELECT * FROM word_state WHERE learner=?", learner)}
    own = [dict(r) for r in db.rows("SELECT id FROM my_words WHERE learner=?", learner)]
    slugs = list(data["entries"]) + [r["id"] for r in own]
    words = []
    for slug in slugs:
        w = entry(slug, learner)
        s = states.get(slug) or state(learner, slug)
        flags = _flags(learner, slug, s, day)
        box = int(s["box"] or 0)
        measured = _measured(slug) if slug in data["entries"] else None
        words.append({"slug": slug, "word": w["word"], "sense": w.get("sense"), "pos": w.get("pos"),
                      "collection": w.get("collection"), "topics": w.get("subjects", w.get("topics", [])),
                      "difficulty": ("easy" if measured["pct"] >= 75 else "medium" if measured["pct"] >= 45 else "hard")
                      if measured else w.get("level", "medium"), "short": w["short"],
                      "freq_band": w.get("freq_band", 3), "measured": measured,
                      "lists": w.get("lists", []), "bank": 0, "own": slug.startswith("u:"),
                      "second_sense": bool(w.get("second_sense")), "state": s if slug in states else None,
                      "proven": s.get("proven"), "claimed": box == 3 and not s.get("proven"),
                      **flags, "saved": bool(s["saved"]), "placed": s.get("placed", 0)})
    counts = Counter()
    for w in words:
        box = int((w["state"] or {}).get("box") or 0)
        counts["due"] += bool(w["is_due"])
        counts["new"] += box == 0 and not w["own"]
        counts["learning"] += 1 <= box <= 3
        counts["known"] += box >= 4 and bool(w["proven"])
        counts["claimed"] += w["claimed"]
        counts["saved"] += w["saved"]
        counts["mine"] += w["own"]
        for key in ("missed", "looked_up", "stubborn", "thought"):
            counts[key] += bool(w[key])
    counts["total"] = len(words)
    counts["new_today"] = sum(1 for s in states.values() if s["first"] and
                              local_day(tz, s["first"]) == day and s["reps"])
    from .deps import part
    prefs_get = part("prefs", "get")
    prefs = prefs_get(learner, tz) if prefs_get else {}
    goal = prefs.get("words_goal", 10)
    counts["goal"] = (finish_metrics(learner, tz)["chips"][-1]["daily"] if goal == "auto" and _exam(learner)
                      else 10 if goal == "auto" else goal)
    history = Counter(local_day(tz, r["at"]).isoformat() for r in db.rows(
        "SELECT at FROM word_reviews WHERE learner=? AND correct IS NOT NULL"
        " AND mode NOT IN ('placement','sort','lookup','outside','sprint','order')"
        " AND at>=?", learner, (day - dt.timedelta(days=14)).isoformat()))
    daily = sorted(history.get((day - dt.timedelta(days=i)).isoformat(), 0) for i in range(1, 15))
    median = (daily[6] + daily[7]) / 2
    debt = {"due": counts["due"], "spread": (counts["due"] + 3) // 4,
            "median": median} if counts["due"] > max(60, 2 * median) else None
    forecast = [{"day": (day + dt.timedelta(days=i)).isoformat(),
                 "n": sum(1 for s in states.values() if s["due"] == (day + dt.timedelta(days=i)).isoformat())}
                for i in range(max(1, min(days, 120)))]
    groups = copy.deepcopy(data["collections"])
    for group in groups:
        for coll in group["collections"]:
            members = [w for w in words if w["collection"] == coll["id"] or coll["id"] in w["lists"]]
            coll["known"] = sum(int((w["state"] or {}).get("box") or 0) >= 4 and bool(w["proven"]) for w in members)
            coll["due"] = sum(w["is_due"] for w in members)
    counts["mistakes"] = counts["missed"]
    counts["lookedup"] = counts["looked_up"]
    return {"today": day.isoformat(), "groups": groups, "words": words,
            "counts": dict(counts), "forecast": forecast, "debt": debt,
            "estimate": estimate(learner)}


def deck(learner: str, source: str, value=None, n: int = 20, tz: int = 0,
         words: list[str] | None = None) -> list[str]:
    lib = library(learner, tz)
    rows = lib["words"]
    def overdue(row: dict) -> float:
        s = row["state"] or {}
        if not s.get("due"):
            return 0.0
        return (local_day(tz) - dt.date.fromisoformat(s["due"])).days / max(1, INTERVALS.get(int(s.get("box") or 0), 1))
    if source in {"words", "selection"}:
        allowed = set(words or [])
        rows = [w for w in rows if w["slug"] in allowed]
    elif source == "collection":
        rows = [w for w in rows if w["collection"] == value or value in w["lists"]]
    elif source == "list":
        saved = db.one("SELECT words FROM word_lists WHERE learner=? AND name=?", learner, value)
        allowed = set(json.loads(saved["words"]) if saved else [])
        rows = [w for w in rows if w["slug"] in allowed]
    elif source == "topic":
        rows = [w for w in rows if value in w["topics"]]
    elif source == "due":
        rows = [w for w in rows if w["is_due"]]
    elif source == "new":
        rows = [w for w in rows if int((w["state"] or {}).get("box") or 0) == 0
                and w["placed"] != 2]
        from .deps import part
        pref_get = part("prefs", "get")
        allowed_from = (pref_get(learner, tz) if pref_get else {}).get("words_from", ["sat", "transitions"])
        rows = [w for w in rows if w["own"] or
                ("transitions" in allowed_from if w["collection"] == "transitions" else "sat" in allowed_from)]
        exam = _exam(learner)
        if exam and (exam - local_day(tz)).days <= 10:
            rows = [w for w in rows if entry(w["slug"], learner).get("tier") != "advanced"]
    elif source == "saved":
        rows = [w for w in rows if w["saved"]]
    elif source in {"missed", "thought", "stubborn", "looked_up", "hard_for_you"}:
        rows = [w for w in rows if w[source]]
    elif source == "atrisk":
        exam = _exam(learner)
        if not exam:
            return []
        rows = [w for w in rows if (w["state"] or {}).get("box") and
                retention(w["state"], exam) < .8]
    elif source == "root":
        related = {r["slug"] for r in content()["roots"].get(value, {}).get("words", [])}
        rows = [w for w in rows if w["slug"] in related]
    elif source == "mine":
        rows = [w for w in rows if w["own"]]
    elif source == "today":
        due = [w for w in rows if w["is_due"]]
        due.sort(key=overdue, reverse=True)
        missed = [w for w in rows if w["missed"] and w not in due][:3]
        extra_transitions = [w for w in rows if w["collection"] == "transitions" and
                             w not in due and w not in missed][:3]
        assigned = {w["slug"] for w in due + missed + extra_transitions}
        fresh = [w for w in rows if int((w["state"] or {}).get("box") or 0) == 0 and
                 w["placed"] != 2 and w["slug"] not in assigned]
        from .deps import part
        prefs_get = part("prefs", "get")
        pref = prefs_get(learner, tz) if prefs_get else {}
        allowed_from = pref.get("words_from", ["sat", "transitions"])
        fresh = [w for w in fresh if w["own"] or
                 ("transitions" in allowed_from if w["collection"] == "transitions" else "sat" in allowed_from)]
        spread = pref.get("words_spread")
        if lib["debt"] and spread and spread >= local_day(tz).isoformat():
            due = due[:lib["debt"]["spread"]]
            fresh = []
            extra_transitions = []
        exam = _exam(learner)
        probable = [w for w in due if w["placed"] == 2]
        proof_goal = (max(1, min(8, (len(probable) + max(1, (exam - local_day(tz)).days - 10) - 1) //
                              max(1, (exam - local_day(tz)).days - 10))) if exam else 2)
        due = [w for w in due if w["placed"] != 2] + probable[:proof_goal]
        if exam and (exam - local_day(tz)).days <= 10:
            fresh = [w for w in fresh if entry(w["slug"], learner).get("tier") != "advanced"]
        rows = due + missed + extra_transitions + fresh[:max(0, lib["counts"]["goal"] - lib["counts"]["new_today"])]
    else:
        raise HTTPException(422, "unknown word deck")
    if source == "today":
        rows.sort(key=lambda w: (0 if w["stubborn"] and w["is_due"] else
                                 1 if w["is_due"] and not w["claimed"] and w["placed"] != 2 else
                                 2 if w["is_due"] else 3 if w["missed"] else
                                 4 if w["collection"] == "transitions" else 5,
                                 -overdue(w),
                                 w["word"].casefold()))
    else:
        rows.sort(key=lambda w: (not w["is_due"], -int(w["saved"]),
                                 0 if w["collection"] == "sat-core" else 1,
                                 -int((entry(w["slug"], learner) or {}).get("value", 1)), w["word"].casefold()))
    return [w["slug"] for w in rows[:max(0, min(n, 200))]]


def today_summary(learner: str, tz: int = 0) -> dict:
    lib = library(learner, tz)
    c = lib["counts"]
    proofs = sum((w["claimed"] or w["placed"] == 2) and w["is_due"] for w in lib["words"])
    goal = c["goal"]
    new_left = max(0, goal - c["new_today"])
    recent = db.rows("SELECT kind,ms FROM word_reviews WHERE learner=? AND correct IS NOT NULL"
                     " AND ms BETWEEN 1000 AND 60000 ORDER BY id DESC LIMIT 200", learner)
    def pace(card: bool, fallback: int) -> int:
        values = sorted(r["ms"] for r in recent if (r["kind"] in {"card", "fix", "cards"}) == card)
        return values[len(values)//2] if len(values) >= 20 else fallback
    card_ms, quiz_ms = pace(True, 10_000), pace(False, 20_000)
    minutes = round((max(0, c["due"] - proofs) * card_ms + proofs * quiz_ms + new_left * 25_000) / 60_000, 1)
    title = f"Today's words · {c['due']} due · {minutes:g} min"
    reason = f"{c['due']} come back today · {proofs} are proofs"
    finished = db.one("SELECT 1 FROM sessions WHERE learner=? AND kind='words' AND finished IS NOT NULL"
                      " AND json_extract(cfg,'$.mode')='mix' AND substr(finished,1,10)=? LIMIT 1",
                      learner, local_day(tz).isoformat())
    return {"due": c["due"], "proofs": proofs, "new_goal": goal,
            "new_today": c["new_today"], "minutes": minutes,
            "done": bool(finished) or (c["due"] == 0 and new_left == 0), "goal": goal,
            "title": title, "reason": reason,
            "preview": {"fix": sum(w["is_due"] and w["stubborn"] for w in lib["words"]),
                        "due": max(0, c["due"] - proofs), "proofs": proofs,
                        "new": new_left, "transitions": 3},
            "start": {"path": "/api/words/run", "body": {"mode": "mix", "deck": {"source": "today"}}}}


def minutes_today(learner: str, tz: int = 0) -> float:
    # A default preference alone does not enroll an untouched learner in Words;
    # reserve study time once a plan or a Words review actually exists.
    enrolled = db.one("SELECT plan FROM learners WHERE id=?", learner)
    active = db.one("SELECT 1 FROM word_reviews WHERE learner=? LIMIT 1", learner)
    if not active and not (enrolled and enrolled["plan"]):
        return 0.0
    return today_summary(learner, tz)["minutes"]


def me_stats(learner: str, tz: int = 0) -> dict:
    c = library(learner, tz)["counts"]
    week = (local_day(tz) - dt.timedelta(days=7)).isoformat()
    reviews_week = db.one("SELECT COUNT(*) n FROM word_reviews WHERE learner=? AND at>=?"
                          " AND correct IS NOT NULL AND mode NOT IN ('sprint','outside','order')", learner, week)["n"]
    return {"known": c["known"], "claimed": c["claimed"], "estimate": estimate(learner),
            "studied": c["learning"] + c["known"], "saved": c["saved"],
            "reviews_week": reviews_week, "due": c["due"]}


def estimate(learner: str) -> dict:
    latest = db.one("SELECT result,finished FROM sessions WHERE kind='words' AND learner=?"
                    " AND json_extract(cfg,'$.mode')='placement' AND finished IS NOT NULL"
                    " ORDER BY finished DESC LIMIT 1", learner)
    if not latest:
        return {"n": 0, "lo": 0, "hi": 0, "at": None, "delta_30": 0}
    out = (json.loads(latest["result"] or "{}").get("estimate") or {}).copy()
    out.update(at=latest["finished"], delta_30=0)
    return out


def retention(s: dict, exam: dt.date) -> float:
    """Estimated chance this reviewed word is recalled on the exam date."""
    if not s.get("last") or not s.get("box"):
        return 0.0
    t = max(0, (exam - local_day(0, s["last"])).days)
    h = INTERVALS.get(int(s["box"]), 1) * (.8 ** int(s.get("lapses") or 0))
    return 2 ** (-t / max(.1, h))


def finish_metrics(learner: str, tz: int = 0) -> dict:
    """Exam forecast and goal choices for Words, Plan, and Me."""
    exam = _exam(learner)
    today = local_day(tz)
    states = {r["word"]: dict(r) for r in db.rows("SELECT * FROM word_state WHERE learner=?", learner)}
    sat = content()["sat"]
    left = {tier: sum(1 for w in sat if w["tier"] == tier and
                      int(states.get(w["slug"], {}).get("box") or 0) < 4)
            for tier in ("core", "advanced")}
    logic = {w["logic"] for w in content()["transitions"] if
             int(states.get(w["slug"], {}).get("box") or 0) < 4}
    left["logics"] = len(logic)
    if not exam:
        return {"left": left, "chips": [], "at_risk": 0, "likely": 0,
                "forecast_to_exam": [], "exam": None}
    days = max(0, (exam - today).days)
    total = left["core"] + left["logics"]
    auto = min(40, max(5, (total + max(1, days - 10) - 1) // max(1, days - 10)))
    chips = []
    for goal in (0, 5, 10, 15, 20, 30, "auto"):
        g = auto if goal == "auto" else goal
        forecast = simulate(learner, g)
        chips.append({"goal": goal, "daily": g,
                      "core_done": (today + dt.timedelta(days=(left["core"] + g - 1) // g)).isoformat()
                      if g else None,
                      "advanced_done": (today + dt.timedelta(days=(left["core"] + left["advanced"] + g - 1) // g)).isoformat()
                      if g else None,
                      "load_2w": forecast["load_2w"], "minutes": forecast["minutes"]})
    studied = [s for s in states.values() if int(s.get("box") or 0) > 0]
    likely = sum(retention(s, exam) >= .8 for s in studied)
    weeks = [{"week": (today + dt.timedelta(days=7 * i)).isoformat(),
              "n": sum(bool(s.get("due") and today + dt.timedelta(days=7*i) <=
                       dt.date.fromisoformat(s["due"]) < today + dt.timedelta(days=7*(i+1))
                       ) for s in studied)} for i in range((days + 6) // 7)]
    return {"left": left, "chips": chips, "at_risk": len(studied) - likely,
            "likely": likely, "forecast_to_exam": weeks, "exam": exam.isoformat(), "days": days}


def of_reason(template: str, reason: str) -> dict | None:
    """R&W only: math trap links were removed by v2-decisions."""
    return None


def gloss_index() -> dict:
    return {"v": 1, "words": [{"slug": w["slug"], "word": w["word"], "short": w["short"],
                               "also": w.get("also", [])} for w in content()["entries"].values()],
            "common": content()["index"].get("common", [])}

# ------------------------------------------------------------------ generated Reading & Writing items

def _servable(row: dict) -> bool:
    return bool(row.get("reviewed")) or os.environ.get("SATF_WORDS_UNREVIEWED") == "1"


def _suppressed(frame: str) -> bool:
    return bool(db.one("SELECT 1 FROM word_suppress WHERE frame=? AND word='*'", frame))


def suppress(frame: str, word: str, why: str) -> None:
    """Pull the whole frame until an editor reviews the questionable choice."""
    stamp = _stamp()
    with db.atomic() as c:
        c.execute("INSERT OR IGNORE INTO word_suppress(frame,word,why,at) VALUES (?,?,?,?)",
                  (frame, word, why, stamp))
        c.execute("INSERT OR IGNORE INTO word_suppress(frame,word,why,at) VALUES (?,?,?,?)",
                  (frame, "*", why, stamp))


def report_fit(template: str, choice: str, learner: str) -> dict:
    ident = template.removeprefix("rw.wic.").removeprefix("rw.tr.")
    if ident not in content()["frames"] and ident not in content()["pairs"]:
        raise HTTPException(404, "unknown Words item")
    with db.atomic() as c:
        c.execute("INSERT OR IGNORE INTO word_fit_reports(frame,word,learner,at) VALUES (?,?,?,?)",
                  (ident, choice, learner, _stamp()))
        count = c.execute("SELECT COUNT(*) FROM word_fit_reports WHERE frame=? AND word=?",
                          (ident, choice)).fetchone()[0]
        if count >= 2:
            suppress(ident, choice, "two learners reported another fitting choice")
    return {"reports": count, "suppressed": count >= 2}


def crowd_guard(template: str) -> None:
    """Check first tries by strong learners for a misleading distractor."""
    ident = template.removeprefix("rw.wic.").removeprefix("rw.tr.")
    reviews = rw_answers(template=template)
    first = {}
    for row in reviews:
        first.setdefault(row["learner"], row)
    strong = []
    for row in first.values():
        recent = db.rows("SELECT correct FROM word_reviews WHERE learner=? AND subject='rw'"
                         " AND kind IN ('incontext','nearly','transition') ORDER BY id DESC LIMIT 30",
                         row["learner"])
        if len(recent) >= 8 and sum(r["correct"] for r in recent) / len(recent) >= .8:
            strong.append(row)
    if len(strong) < 8:
        return
    counts = Counter(r["given"] for r in strong if r["correct"] == 0 and r["given"])
    for choice, n in counts.items():
        if n >= 4 and n / len(strong) >= .4:
            suppress(ident, choice, "strong learner pick split")


def pick_split(template: str) -> dict | None:
    first = {}
    for row in rw_answers(template=template):
        first.setdefault(row["learner"], row)
    if len(first) < 20:
        return None
    counts = Counter(r["given"] for r in first.values() if r["given"])
    return {"n": len(first), "choices": dict(counts)}


def _rng(template: str, seed: int, word: str | None = None) -> random.Random:
    address = f"{template}\0{seed}\0{word or ''}".encode()
    return random.Random(int.from_bytes(hashlib.sha256(address).digest()[:8], "big"))


def _render(raw: str, rng: random.Random,
            chosen: dict[str, str] | None = None) -> tuple[str, list[dict]]:
    if chosen is None:
        chosen = {}
    pools = content()["fills"]
    def fill(match):
        name = match.group(1)
        if name not in chosen:
            chosen[name] = rng.choice(pools[name])
        return chosen[name]
    raw = re.sub(r"\{([a-z_]+)\}", fill, raw)
    out, spans, pos = [], [], 0
    for match in re.finditer(r"\[\[([^\[\]]+)\]\]", raw):
        piece = raw[pos:match.start()]
        out.append(piece)
        start = sum(map(len, out))
        out.append(match.group(1))
        spans.append({"start": start, "end": start + len(match.group(1)), "kind": "clue"})
        pos = match.end()
    out.append(raw[pos:])
    return "".join(out), spans


def _legal(word: dict, need: dict) -> bool:
    return (word.get("class") == need["class"] and word.get("polarity") == need["polarity"]
            and need["lo"] <= word.get("intensity", -1) <= need["hi"]
            and word.get("pos") == need["pos"] and need["pattern"] in word.get("pattern", []))


def _synonyms(a: dict, b: dict) -> bool:
    an = {a.get("slug", "").casefold(), a.get("word", "").casefold()}
    bn = {b.get("slug", "").casefold(), b.get("word", "").casefold()}
    return bool(an & {s.casefold() for s in b.get("same", [])} or
                bn & {s.casefold() for s in a.get("same", [])})


def _trap(frame: dict, key: dict, choice: dict) -> str | None:
    need = frame["need"]
    if _legal(choice, need):
        return None
    synonym = _synonyms(key, choice)
    pins = need.get("pins") == "intensity"
    traps = set()
    opposite = content()["classes"][need["class"]].get("opposite")
    if opposite and choice.get("class") == opposite:
        traps.add("reversed")
    if choice.get("class") == need["class"]:
        if choice.get("polarity") == need["polarity"] and pins:
            if choice["intensity"] > need["hi"]:
                traps.add("too_strong")
            elif choice["intensity"] < need["lo"]:
                traps.add("too_weak")
        elif choice.get("polarity") == -need["polarity"] != 0:
            traps.add("connotation")
    looks = {x["word"].casefold() for x in key.get("lookalikes", [])}
    if choice["word"].casefold() in looks and choice.get("class") != need["class"]:
        traps.add("lookalike")
    if frame["subject"] in choice.get("subjects", []) and choice.get("class") not in {need["class"], opposite}:
        traps.add("topical")
    if synonym:
        traps &= {"too_strong", "too_weak", "connotation"}
    for kind in ("lookalike", "too_strong", "too_weak", "connotation", "reversed", "topical"):
        if kind in traps:
            return kind
    return None


def _appears(word: dict, passage: str) -> bool:
    forms = [word["word"], *word.get("also", [])]
    return any(re.search(r"(?<!\w)" + re.escape(form) + r"(?!\w)", passage, re.I) for form in forms)


def _trap_reason(kind: str, choice: dict, need: str, clue: str) -> str:
    labels = {"too_strong": "Too strong", "too_weak": "Too weak", "connotation": "Wrong tone",
              "reversed": "Reversed meaning", "lookalike": "Looks like the answer",
              "topical": "On the topic but wrong meaning"}
    return (f"{labels[kind]}: the clue says “{clue}” and needs {need}; "
            f"“{choice['word']}” means {choice['short']}.")


def item(template: str, seed: int, word: str | None = None,
         want_trap: str | None = None) -> dict:
    """Regenerate one exact `(template, seed, word)` address.

    The content review gate is enforced here, so every caller shares it.
    """
    data = content()
    rng = _rng(template, seed, word)
    if template.startswith("rw.wic."):
        ident = template[len("rw.wic."):]
        frame = data["frames"].get(ident)
        if not frame or not _servable(frame) or _suppressed(ident):
            raise ValueError("frame is not reviewed or is suppressed")
        keys = frame["keys"]
        if word is not None and word not in keys:
            raise ValueError("word is not a key of this frame")
        slug = word or rng.choice(keys)
        key = data["entries"][slug]
        passage, spans = _render(frame["text"], rng)
        suppressed = {r["word"] for r in db.rows("SELECT word FROM word_suppress WHERE frame=?", ident)}
        need = frame["need"]
        clue = passage[spans[0]["start"]:spans[0]["end"]] if spans else frame["needs"]
        candidates = []
        for w in data["sat"]:
            if w["pos"] != key["pos"] or w["slug"] == slug or _appears(w, passage):
                continue
            kind = _trap(frame, key, w)
            if kind and w["slug"] not in suppressed and w["word"] not in suppressed:
                candidates.append((w, kind))
        rng.shuffle(candidates)
        candidates.sort(key=lambda pair: (0 if pair[1] == want_trap else 1,
                                          {"lookalike": 0, "too_strong": 1, "too_weak": 2,
                                           "connotation": 3, "reversed": 4, "topical": 5}[pair[1]]))
        picked, seen = [], {(key["class"], key["polarity"], key["intensity"])}
        used_words = {key["word"].casefold()}
        for w, kind in candidates:
            features = (w["class"], w["polarity"], w["intensity"])
            if features not in seen and w["word"].casefold() not in used_words:
                seen.add(features)
                used_words.add(w["word"].casefold())
                picked.append((w, kind))
                if len(picked) == 3:
                    break
        if len(picked) < 3 or _appears(key, passage):
            raise ValueError("frame has fewer than three safe traps")
        options = [(key, None)] + picked
        rng.shuffle(options)
        choices = [w["word"] for w, _ in options]
        answer = next(i for i, (_, kind) in enumerate(options) if kind is None)
        reasons = [(f"“{key['word']}” means {key['short']}; the text needs {frame['needs']}."
                    if kind is None else _trap_reason(kind, w, frame["needs"], clue))
                   for w, kind in options]
        out = {"template": template, "skill": "Words in Context", "domain": "Craft and Structure",
               "difficulty": frame["difficulty"], "seed": seed, "word": slug,
               "kind": "nearly" if frame["stem"] == "nearly" else "incontext",
               "stem": (f"As used in the text, what does the word “{key['word']}” most nearly mean?"
                        if frame["stem"] == "nearly" else
                        "Which choice completes the text with the most logical and precise word or phrase?"),
               "text": passage, "choices": choices, "answer_index": answer,
               "reasons": reasons, "traps": [kind for _, kind in options],
               "spans": spans, "rationale": reasons[answer], "needs": frame["needs"],
               "subject": frame["subject"]}
        if frame.get("source"):
            out["source"] = frame["source"]
        return out
    if template.startswith("rw.tr."):
        ident = template[len("rw.tr."):]
        pair = data["pairs"].get(ident)
        if not pair or not _servable(pair) or _suppressed(ident):
            raise ValueError("transition family is not reviewed or is suppressed")
        keys = pair["fits"]
        if word is not None and word not in keys:
            raise ValueError("word is not a key of this family")
        slug = word or rng.choice(keys)
        key = data["entries"][slug]
        chosen = {}
        s1, first_spans = _render(pair["s1"], rng, chosen)
        s2, second_spans = _render(rng.choice(pair["s2"]), rng, chosen)
        passage = s1 + " " + s2
        spans = [{**s, "kind": "idea"} for s in first_spans]
        spans += [{**s, "start": s["start"] + len(s1) + 1,
                   "end": s["end"] + len(s1) + 1, "kind": "idea"} for s in second_spans]
        logic = pair["logic"]
        suppressed = {r["word"] for r in db.rows("SELECT word FROM word_suppress WHERE frame=?", ident)}
        excluded = {logic, *pair.get("compatible", [])}
        candidates: dict[str, list[dict]] = defaultdict(list)
        for transition in data["transitions"]:
            other = transition["logic"]
            if other not in excluded and logic not in transition.get("also_reads", []) and not _appears(transition, passage) and transition["slug"] not in suppressed and transition["word"] not in suppressed:
                candidates[other].append(transition)
        preferred = [b if a == logic else a for a, b in data["transition_data"]["confusable"]
                     if a == logic or b == logic]
        logics = [l for l in preferred if l in candidates]
        logics += [l for l in sorted(candidates) if l not in logics]
        if want_trap in candidates and want_trap not in logics[:3]:
            logics = [want_trap] + [l for l in logics if l != want_trap]
        picked = []
        for other in logics[:3]:
            picked.append((rng.choice(candidates[other]), other))
        if len(picked) < 3 or _appears(key, passage):
            raise ValueError("transition family has fewer than three distinct wrong logics")
        options = [(key, logic)] + picked
        rng.shuffle(options)
        reasons_map = data["transition_data"]["logic_reasons"]
        reasons = [(f"“{w['word']}” signals {logic}; the second sentence has that relationship."
                    if other == logic else reasons_map[logic][other].replace("{word}", w["word"]))
                   for w, other in options]
        return {"template": template, "skill": "Transitions", "domain": "Expression of Ideas",
                "difficulty": pair.get("difficulty") or key.get("level", "medium"), "seed": seed, "word": slug,
                "kind": "transition", "stem": "Which choice completes the text with the most logical transition?",
                "text": passage, "choices": [w["word"] for w, _ in options],
                "answer_index": next(i for i, (_, l) in enumerate(options) if l == logic),
                "reasons": reasons, "traps": [None if l == logic else "wrong_logic" for _, l in options],
                "spans": spans, "rationale": f"The two ideas have a {logic} relationship.",
                "needs": pair["relation"], "logic_needed": logic,
                "option_logics": [l for _, l in options], "relation": pair["relation"],
                "subject": pair["subject"]}
    raise ValueError("unknown Reading & Writing template")


def _sprint_pool(kind: str, tier: str) -> list[tuple[str, str]]:
    """Reviewed SAT-form addresses at one authored difficulty."""
    data = content()
    if kind == "incontext":
        return [("rw.wic." + frame["id"], slug)
                for frame in data["frames"].values()
                if frame["stem"] == "complete" and frame["difficulty"] == tier
                and _servable(frame) and not _suppressed(frame["id"])
                for slug in frame["keys"]]
    return [("rw.tr." + pair["id"], slug)
            for pair in data["pairs"].values()
            if _servable(pair) and not _suppressed(pair["id"])
            for slug in pair["fits"] if data["entries"][slug].get("level") == tier]


def sprint_available() -> bool:
    """The weekly contest opens only when both reviewed SAT forms can climb."""
    return all(_sprint_pool(kind, tier) for kind in ("incontext", "transition")
               for tier in ("easy", "medium", "hard"))


def sprint_items(learner: str, seed: int, n: int, level: int) -> list[dict]:
    """Alternating W1/W2 twins with a difficulty band every five answers.

    The template walk depends on the shared contest seed. The learner changes
    each passage's draw, so entrants receive the same forms but fresh text.
    """
    if not isinstance(n, int) or not 1 <= n <= 80 or not isinstance(level, int) or not 1 <= level <= 5:
        raise HTTPException(422, "Word Sprint count is 1–80 and level is 1–5")
    if not sprint_available():
        raise HTTPException(409, "reviewed Words in Context and Transitions frames are needed")
    pools = {(kind, tier): _sprint_pool(kind, tier)
             for kind in ("incontext", "transition") for tier in ("easy", "medium", "hard")}
    out, seen = [], set()
    for index in range(n):
        band = min(5, level + index // 5)
        tier = "easy" if band <= 2 else "medium" if band == 3 else "hard"
        kind = "incontext" if index % 2 == 0 else "transition"
        candidates = pools[kind, tier]
        start = (seed + index // 2) % len(candidates)
        selected = None
        for offset in range(len(candidates)):
            template, slug = candidates[(start + offset) % len(candidates)]
            draw = int.from_bytes(hashlib.sha256(
                f"{learner}:{seed}:{index}:{offset}".encode()).digest()[:4], "big")
            for retry in range(4):
                try:
                    generated = item(template, draw + retry, slug)
                except ValueError:
                    continue
                signature = (generated["text"], tuple(generated["choices"]))
                if signature in seen:
                    continue
                selected = generated
                seen.add(signature)
                break
            if selected:
                break
        if not selected:
            raise HTTPException(409, f"reviewed {kind} supply ran out at item {index + 1}")
        if kind == "transition":
            need = selected["logic_needed"]
            selected["traps"] = [None if i == selected["answer_index"] else
                                 f"Read {need} as {logic}"
                                 for i, logic in enumerate(selected["option_logics"])]
        else:
            labels = content()["traps"]
            selected["traps"] = [labels[trap]["name"] if trap in labels else trap
                                 for trap in selected["traps"]]
        selected["sprint_band"] = band
        out.append(selected)
    return out


def record_contest_miss(learner: str, word: str, trap: str | None) -> dict:
    """Mark a Word Sprint miss without another review or any box loss.

    Compete grades the item first in passive sprint mode. This adapter also
    works when a contest imports a miss after its review was filed.
    """
    if not entry(word, learner):
        raise HTTPException(404, "unknown word")
    with db.atomic() as c:
        s = state(learner, word)
        before = s["box"]
        s["lastwrong"] = _stamp()
        _upsert_state(c, s)
        latest = c.execute("SELECT id,trap FROM word_reviews WHERE learner=? AND word=?"
                           " AND mode='sprint' AND correct=0 ORDER BY id DESC LIMIT 1",
                           (learner, word)).fetchone()
        if latest and trap and not latest["trap"]:
            c.execute("UPDATE word_reviews SET trap=?,confusion=? WHERE id=?", (trap, trap, latest["id"]))
    return {"word": word, "trap": trap, "box": before, "missed": True}


def choose_template(slug: str, *, learner: str | None = None,
                    seed: int = 0, seen: set[str] | None = None,
                    avoid_subject: str | None = None) -> str | None:
    data = content()
    known = data["index"]["words"].get(slug)
    if not known:
        return None
    if slug in {w["slug"] for w in data["transitions"]}:
        candidates = ["rw.tr." + p["id"] for p in data["pairs"].values()
                      if slug in p["fits"] and _servable(p) and not _suppressed(p["id"])]
    else:
        candidates = ["rw.wic." + ident for ident in known["frames"]
                      if _servable(data["frames"][ident]) and not _suppressed(ident)]
    if not candidates:
        return None
    seen = set(seen or ())
    if learner and not seen:
        seen = {r["template"] for r in rw_answers(learner) if r["word"] == slug}
    fresh = [t for t in candidates if t not in seen]
    pool = fresh or candidates
    if avoid_subject:
        other = [t for t in pool if (data["pairs"][t[6:]]["subject"] if t.startswith("rw.tr.")
                                    else data["frames"][t[7:]]["subject"]) != avoid_subject]
        if other:
            pool = other
    rng = _rng("pick:" + slug, seed, learner)
    return rng.choice(pool)


def new_sentence(learner: str, slug: str, reps: int | None = None) -> dict | None:
    """W8: unseen frame and fill first, keyed to this learner's review count."""
    w = entry(slug, learner)
    if not w or slug.startswith("u:"):
        return None
    s = state(learner, slug)
    history = json.loads(s.get("sentence_history") or "[]")
    reps = int(s["reps"] if reps is None else reps)
    previous = [r["template"] for r in rw_answers(learner) if r["word"] == slug]
    seen = set(previous) | {r["template"] for r in history}
    last = history[-1]["template"] if history else previous[-1] if previous else None
    avoid = (content()["pairs"][last[6:]]["subject"] if last and last.startswith("rw.tr.")
             else content()["frames"][last[7:]]["subject"] if last and last.startswith("rw.wic.")
             else None)
    template = choose_template(slug, learner=learner, seed=reps, seen=seen, avoid_subject=avoid)
    if not template:
        return None
    seed = int.from_bytes(hashlib.sha256(f"sentence:{learner}:{slug}:{reps}".encode()).digest()[:4], "big")
    try:
        generated = item(template, seed, slug)
    except ValueError:
        return None
    text = generated["text"].replace("____", w["word"], 1)
    history.append({"template": template, "seed": seed})
    s["sentence_history"] = json.dumps(history[-30:])
    with db.atomic() as c:
        _upsert_state(c, s)
    return {"template": template, "seed": seed, "text": text,
            "subject": generated["subject"], "source": generated.get("source")}


def _distractors(slug: str, rng: random.Random, *, meanings: bool = False,
                 learner: str | None = None) -> list[dict]:
    target = entry(slug, learner)
    if not target:
        raise ValueError("unknown word")
    data = content()
    if slug.startswith("u:"):
        others = [entry(r["id"], learner) for r in db.rows("SELECT id FROM my_words WHERE learner=?", learner)]
    elif target["collection"] == "transitions":
        others = [w for w in data["transitions"] if w["logic"] != target["logic"]]
    else:
        others = [w for w in data["sat"] if w["pos"] == target["pos"]]
    same = {s.casefold() for s in target.get("same", [])}
    allowed = [w for w in others if w and w["slug"] != slug and
               w["word"].casefold() not in same and not _synonyms(target, w) and
               (not meanings or .6 <= len(w["short"]) / max(1, len(target["short"])) <= 1.4)]
    confused = {other for c in data["confusions"].values() if slug in c["words"]
                for other in c["words"] if other != slug}
    rng.shuffle(allowed)
    allowed.sort(key=lambda w: (0 if w["slug"] in confused else 1,
                                0 if w.get("collection") == target.get("collection") else 1))
    out, used = [], {target["short"] if meanings else target["word"]}
    for w in allowed:
        value = w["short"] if meanings else w["word"]
        if value not in used:
            out.append(w)
            used.add(value)
        if len(out) == 3:
            break
    if len(out) < 3:
        raise ValueError("this deck needs four distinct words")
    return out


def quiz_item(word: str, kind: str, rng: random.Random,
              learner: str | None = None) -> dict:
    target = entry(word, learner)
    if not target:
        raise ValueError("unknown word")
    if kind not in {"meaning2word", "word2meaning", "typed", "cloze"}:
        raise ValueError("unknown simple quiz kind")
    if kind == "typed":
        return {"kind": kind, "word": word, "stem": "Type the word that fits this meaning.",
                "text": target["short"], "also": target.get("also", []),
                "answer": target["word"], "choices": []}
    meanings = kind == "word2meaning"
    distractors = _distractors(word, rng, meanings=meanings, learner=learner)
    options = [target, *distractors]
    rng.shuffle(options)
    if kind == "cloze":
        examples = target.get("examples", [])
        raw = rng.choice(examples) if examples else ""
        text = re.sub(r"\[\[[^\[\]]+\]\]", "____", raw, count=1)
        if "____" not in text and target.get("own"):
            text = re.sub(r"(?<!\w)" + re.escape(target["word"]) + r"(?!\w)",
                          "____", raw, count=1, flags=re.I)
        if "____" not in text:
            raise ValueError("word has no usable cloze")
    else:
        text = target["word"] if meanings else target["short"]
    values = [w["short"] if meanings else w["word"] for w in options]
    correct = options.index(target)
    return {"kind": kind, "word": word, "stem": ("What does this word mean?" if meanings else
             "Which word best matches the meaning?"), "text": text, "choices": values,
            "answer_index": correct,
            "reasons": [(f"“{w['word']}” means {w['short']}." if w != target else
                         f"“{target['word']}” means {target['short']}.") for w in options],
            "traps": [None if w == target else "meaning" for w in options]}


def another(prev: dict, like: str, learner: str, seen: set[str] | None = None) -> dict:
    if like not in {"word", "trap"}:
        raise ValueError("like must be word or trap")
    seed = int(prev["seed"]) + 1
    old = prev["word"]
    if like == "word":
        slug = old
        want = None
    else:
        want = prev.get("picked_trap") or next((t for t in prev.get("traps", []) if t), None)
        choices = [w["slug"] for w in content()["sat"] if w["slug"] != old]
        rng = _rng("another", seed, old)
        rng.shuffle(choices)
        slug = next((s for s in choices if choose_template(s, learner=learner, seed=seed,
                                                           seen=seen) is not None), old)
    for offset in range(20):
        template = choose_template(slug, learner=learner, seed=seed + offset, seen=seen)
        if template:
            try:
                return item(template, seed + offset, slug, want)
            except ValueError:
                continue
    raise ValueError("no reviewed frame is available")


def public_item(generated: dict, item_id: str | None = None) -> dict:
    """One public shape; never serialize keys or trap reasons before a verdict."""
    allowed = ("kind", "stem", "text", "choices", "head", "step", "predictions", "source")
    out = {k: generated[k] for k in allowed if k in generated}
    if generated.get("step") in {"predict", "logic"} and not generated.get("stage_done"):
        out.pop("choices", None)
    if generated.get("kind") in {"card", "fix", "learn"}:
        out["word"] = generated.get("word")
        out["back"] = generated.get("back")
        if generated.get("picks"):
            out["picks"] = generated["picks"]
    out["item_id"] = item_id or generated.get("item_id")
    return out

# ------------------------------------------------------------------ shared daily Reading & Writing items

def daily_item(day: str, fmt: str) -> dict | None:
    """The sole deterministic chooser for both Words and Today's R&W slots."""
    if fmt not in {"wic", "transition"}:
        raise ValueError("daily format must be wic or transition")
    digest = hashlib.sha256(f"qotd:rw:{fmt}:{day}".encode()).digest()
    data = content()
    if fmt == "wic":
        eligible = sorted(w["slug"] for w in data["sat"] if
                          len([ident for ident in data["index"]["words"][w["slug"]]["frames"]
                               if _servable(data["frames"][ident]) and not _suppressed(ident)]) >= 6)
        if not eligible:
            return None
        for offset in range(min(40, len(eligible))):
            slug = eligible[(int.from_bytes(digest[:8], "big") + offset) % len(eligible)]
            frames = [ident for ident in data["index"]["words"][slug]["frames"]
                      if _servable(data["frames"][ident]) and not _suppressed(ident)]
            ident = frames[int.from_bytes(digest[8:16], "big") % len(frames)]
            seed = int.from_bytes(digest[16:24], "big")
            try:
                generated = item("rw.wic." + ident, seed, slug)
                generated["item_id"] = f"rw:wic:{day}"
                return generated
            except ValueError:
                continue
        return None
    families = sorted(p["id"] for p in data["pairs"].values()
                      if _servable(p) and not _suppressed(p["id"]))
    if not families:
        return None
    for offset in range(min(40, len(families))):
        ident = families[(int.from_bytes(digest[:8], "big") + offset) % len(families)]
        seed = int.from_bytes(digest[8:16], "big")
        try:
            generated = item("rw.tr." + ident, seed)
            generated["item_id"] = f"rw:transition:{day}"
            return generated
        except ValueError:
            continue
    return None


def record_daily(learner: str, day: str, fmt: str, answer: int | str,
                 ms: int | None = None, conf: str | None = None, tz: int = 0) -> dict:
    generated = daily_item(day, fmt)
    if not generated:
        raise HTTPException(409, "no reviewed daily item is available")
    session = f"qotd:rw:{fmt}:{day}"
    with db.atomic():
        previous = db.one("SELECT * FROM word_reviews WHERE learner=? AND session=? ORDER BY id LIMIT 1",
                          learner, session)
        if previous:
            return {"correct": bool(previous["correct"]), "given": previous["given"],
                    "answer_index": generated["answer_index"],
                    "word": generated["word"], "reasons": generated["reasons"],
                    "traps": generated["traps"], "already": True}
        if day != local_day(tz).isoformat():
            raise HTTPException(409, "that daily item is no longer today")
        chosen = ("ABCD".index(answer.upper()) if isinstance(answer, str) and
                  answer.upper() in "ABCD" else answer)
        if not isinstance(chosen, int) or not 0 <= chosen <= 3:
            raise HTTPException(422, "answer must be an option from 0 to 3")
        ok = chosen == generated["answer_index"]
        verdict = grade(learner, generated["word"], ok, "daily", generated["kind"], ms,
                        session, generated["traps"][chosen], tz,
                        given=str(chosen), conf=conf, template=generated["template"],
                        seed=generated["seed"])
    return {**verdict, "given": chosen, "answer_index": generated["answer_index"],
            "word": generated["word"], "reasons": generated["reasons"],
            "traps": generated["traps"], "spans": generated["spans"], "already": False}


def order_item(seed: int, family: str | None = None) -> dict:
    data = content()
    rng = _rng("rw.order." + (family or "any"), seed)
    families = defaultdict(list)
    for w in data["sat"]:
        families[w["class"]].append(w)
    eligible = {name: group for name, group in families.items()
                if len({w["intensity"] for w in group}) >= 4}
    if family and family not in eligible:
        raise ValueError("this family has no four-step ladder")
    name = family or rng.choice(sorted(eligible))
    by_strength = defaultdict(list)
    for w in eligible[name]:
        by_strength[w["intensity"]].append(w)
    levels = rng.sample(sorted(by_strength), 4)
    picked = [rng.choice(by_strength[level]) for level in levels]
    key = [w["slug"] for w in sorted(picked, key=lambda x: x["intensity"])]
    rng.shuffle(picked)
    return {"template": "rw.order." + name, "seed": seed, "kind": "order",
            "word": key[0], "stem": "Put these words in order from weakest to strongest.",
            "text": data["classes"][name]["dimension"],
            "choices": [w["word"] for w in picked],
            "option_slugs": [w["slug"] for w in picked], "answer_order": key,
            "reasons": [f"“{w['word']}” is at strength {w['intensity']}." for w in picked]}


def root_item(seed: int, kind: str = "decode", root_id: str | None = None) -> dict:
    data = content()
    rng = _rng("rw.root." + (root_id or "any"), seed)
    roots = [r for r in data["roots"].values() if len(r["words"]) >= 3]
    root = data["roots"].get(root_id) if root_id else rng.choice(roots)
    if not root or len(root["words"]) < 3:
        raise ValueError("root has too few family words")
    if kind == "rootshare":
        family = rng.sample(root["words"], 3)
        others = rng.sample([r for r in roots if r["id"] != root["id"]], 3)
        choices = [root, *others]
        rng.shuffle(choices)
        return {"kind": "rootshare", "word": family[0]["slug"],
                "stem": "Which root do these words share?",
                "text": ", ".join(data["entries"][w["slug"]]["word"] for w in family),
                "choices": [r["forms"][0] for r in choices],
                "answer_index": choices.index(root),
                "reasons": [f"{r['forms'][0]} means {r['meaning']}." for r in choices],
                "traps": [None if r == root else "wrong_root" for r in choices]}
    related = rng.choice(root["words"])
    key = data["entries"][related["slug"]]
    family_slugs = {x["slug"] for x in root["words"]}
    others = [w for w in data["sat"] if w["slug"] not in family_slugs and
              .6 <= len(w["short"]) / max(1, len(key["short"])) <= 1.4]
    rng.shuffle(others)
    chosen, seen = [], {key["short"]}
    for w in others:
        if w["short"] not in seen:
            chosen.append(w)
            seen.add(w["short"])
        if len(chosen) == 3:
            break
    options = [key, *chosen]
    rng.shuffle(options)
    return {"kind": "decode", "word": key["slug"],
            "stem": "What does this word most likely mean?",
            "text": key["word"], "parts": related["split"],
            "choices": [w["short"] for w in options], "answer_index": options.index(key),
            "reasons": [f"“{w['word']}” means {w['short']}." for w in options],
            "traps": [None if w == key else "wrong_root" for w in options]}


def open_traps(learner: str) -> list[str]:
    misses = [r for r in rw_answers(learner) if r["correct"] == 0 and r["trap"]]
    recent = misses[-20:]
    counts = Counter(r["trap"] for r in recent)
    return [kind for kind, n in counts.most_common()
            if n >= 3 and n / max(1, len(recent)) >= .25]


def logic_pairs(learner: str) -> list[dict]:
    transition_by_word = {w["word"].casefold(): w["logic"] for w in content()["transitions"]}
    counts = Counter()
    for r in rw_answers(learner):
        if r["skill"] != "Transitions" or r["correct"] != 0:
            continue
        ident = r["template"][6:]
        pair = content()["pairs"].get(ident)
        picked = transition_by_word.get((r["given"] or "").casefold())
        if pair and picked and picked != pair["logic"]:
            counts[(pair["logic"], picked)] += 1
    return [{"needed": a, "picked": b, "n": n} for (a, b), n in counts.most_common()]
