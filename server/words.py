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
SELF_KINDS = frozenset({"cards", "self", "sort", "placement", "sheet-grade"})
ACHIEVEMENTS = [{"id": f"words-{n}", "kind": "words_known", "target": n}
                for n in (50, 250, 1000)]
RW_TO_ATTEMPTS = """INSERT INTO attempts(learner,session,qid,template,seed,topic,difficulty,fmt,correct,reason,given,ms,at)
SELECT learner, session, 'rw:' || id, template, seed,
CASE skill WHEN 'Transitions' THEN 'rw.transitions' ELSE 'rw.words_in_context' END,
difficulty, 'mcq', correct, trap, given, ms, at FROM word_reviews
WHERE subject='rw' AND template IS NOT NULL AND attempt=1"""


def _load(name: str):
    value = json.loads((HERE / f"{name}.json").read_text(encoding="utf-8"))
    return value if isinstance(value, list) else value.get("entries", value)


@lru_cache(maxsize=1)
def content() -> dict:
    sat, transitions = _load("sat"), _load("transitions")
    frames, pairs = _load("frames"), _load("pairs")
    entries = {w["slug"]: w for w in sat + transitions}
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    return {"entries": entries, "sat": sat, "transitions": transitions,
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
                       "pending_know": "TEXT", "thought_at": "TEXT", "looked_at": "TEXT"},
        "word_reviews": {"template": "TEXT", "seed": "INTEGER", "trap": "TEXT", "conf": "TEXT",
                         "gap": "TEXT", "subject": "TEXT", "skill": "TEXT", "domain": "TEXT",
                         "difficulty": "TEXT", "attempt": "INTEGER DEFAULT 1"},
    }
    for table, columns in additions.items():
        have = {r["name"] for r in c.execute(f"PRAGMA table_info({table})")}
        for column, declaration in columns.items():
            if column not in have:
                c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {declaration}")
    c.execute("CREATE INDEX IF NOT EXISTS word_reviews_template ON word_reviews(template)")
    c.execute("CREATE INDEX IF NOT EXISTS word_reviews_learner_word ON word_reviews(learner,word,id)")
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
                                  "looked_at": None}


def _upsert_state(c, s: dict) -> None:
    fields = ("learner", "word", "box", "due", "reps", "lapses", "right", "wrong", "saved",
              "first", "last", "lastday", "lastwrong", "proven", "placed", "hook",
              "pending_know", "thought_at", "looked_at")
    c.execute(f"INSERT INTO word_state({','.join(fields)}) VALUES ({','.join('?' for _ in fields)}) "
              f"ON CONFLICT(learner,word) DO UPDATE SET "
              + ",".join(f"{f}=excluded.{f}" for f in fields if f not in ("learner", "word")),
              tuple(s.get(f) for f in fields))


def _exam(learner: str) -> dt.date | None:
    row = db.one("SELECT exam_date FROM learners WHERE id=?", learner)
    return dt.date.fromisoformat(row["exam_date"]) if row and row["exam_date"] else None


def _due(day: dt.date, box: int, learner: str, *, stubborn: bool = False) -> str:
    interval = INTERVALS[box]
    if stubborn:
        interval = {1: 1, 2: 2, 3: 5}.get(box, interval)
    from .deps import part
    scale = part("prefs", "get")
    pref = scale(learner) if scale else {}
    factor = float(pref.get("words_scale", 1) or 1)
    interval = max(1, round(interval * max(.5, min(2, factor))))
    if interval >= 3:
        # Stable fuzz: the same learner, word and review day always get the same interval.
        interval = max(1, interval + round(interval * ((int.from_bytes(
            hashlib.sha256(f"{learner}:{day}:{box}".encode()).digest()[:2], "big") / 65535) * .2 - .1)))
    due = day + dt.timedelta(days=interval)
    exam = _exam(learner)
    if exam and due >= exam:
        due = max(day + dt.timedelta(days=1), exam - dt.timedelta(days=1))
    return due.isoformat()


def _review_row(c, learner: str, slug: str, session: str | None, mode: str, kind: str,
                correct: bool | None, given: str | None, box_before: int, due_before: str | None,
                ms: int | None, at: str, *, template: str | None = None, seed: int | None = None,
                trap: str | None = None, conf: str | None = None, gap: str | None = None,
                attempt: int = 1) -> int:
    word = entry(slug, learner) or {}
    skill = "Transitions" if word.get("collection") == "transitions" else "Words in Context"
    subject = "rw" if template else None
    return c.execute("INSERT INTO word_reviews(learner,word,session,mode,kind,correct,given,confusion,"
                     "box_before,due_before,ms,at,template,seed,trap,conf,gap,subject,skill,domain,difficulty,attempt)"
                     " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     (learner, slug, session, mode, kind, None if correct is None else int(correct),
                      given, trap, box_before, due_before, ms, at, template, seed, trap, conf,
                      gap, subject, skill if subject else None,
                      word.get("subjects", [None])[0] if subject else None,
                      word.get("level") if subject else None, attempt)).lastrowid


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
        before, due_before = int(s["box"] or 0), s["due"]
        early = bool(due_before and due_before > day.isoformat())
        lastday = s["lastday"] == day.isoformat()
        self_grade = kind in SELF_KINDS or kind == "cards"
        proof = kind in PROOF_KINDS or (word.startswith("u:") and kind in {"meaning2word", "typed"})
        passive = mode in {"sprint", "order", "lookup", "outside"} or kind == "order"
        after = before
        promoted = False
        if passive:
            if not ok:
                s["lastwrong"] = stamp
        elif not ok:
            after = 1
            s["proven"] = None
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
            s["due"] = _due(day, after, learner)
        elif self_grade and before >= 3:
            s["due"] = (day + dt.timedelta(days=2)).isoformat() if before == 3 else _due(day, before, learner)
            s["pending_know"] = stamp
        elif before >= 3 and not proof:
            # Recognition quizzes cannot certify a high-box word.
            s["due"] = (day + dt.timedelta(days=2)).isoformat() if before == 3 else due_before
        else:
            after = min(5, 2 if before == 0 else before + 1)
            promoted = after > before
            s["due"] = _due(day, after, learner)
            if after >= 4 and proof:
                s["proven"] = day.isoformat()
        if after >= 4 and not s.get("proven"):
            after = 3
            s["due"] = (day + dt.timedelta(days=2)).isoformat()
        if ok and not self_grade and not passive:
            s["thought_at"] = None
            s["pending_know"] = None
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
                                trap=confusion, conf=conf, gap=gap, attempt=attempt)
    status = ("Prove it in context to make it Known" if after == 3 and not s.get("proven")
              else "Known" if after >= 4 else "Again today" if not ok
              else "Early review" if early else "Back " + (s["due"] or "soon"))
    return {"correct": bool(ok), "word": word, "box": {"before": before, "after": after},
            "due": s["due"], "early": early, "proven": s.get("proven"), "claimed": after == 3 and not s.get("proven"),
            "status": status, "review_id": review_id, "requeued": not ok and not passive}


def place(learner: str, slug: str, choice: str, tz: int = 0, *, at: str | None = None) -> dict:
    """Placement/triage: Yes is a claim, never proof; likely-known waits for one proof."""
    if not entry(slug, learner):
        raise HTTPException(404, "unknown word")
    stamp = _stamp(at)
    day = local_day(tz, stamp)
    with db.atomic() as c:
        s = state(learner, slug)
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
        _review_row(c, learner, slug, None, "placement", "sort", None, choice,
                    before, due_before, None, stamp, attempt=0)
    return {"word": slug, "box": {"before": before, "after": s["box"]}, "due": s["due"],
            "claimed": s["box"] == 3, "placed": s["placed"]}


def word_reviews(learner: str, slug: str | None = None) -> list[dict]:
    sql = "SELECT * FROM word_reviews WHERE learner=?"
    args = [learner]
    if slug:
        sql += " AND word=?"
        args.append(slug)
    return [dict(r) for r in db.rows(sql + " ORDER BY id", *args)]


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
        if review["correct"] is None:
            continue
        if review["mode"] in {"cards", "sort", "placement", "sheet-grade"} and review["correct"]:
            pending[review["word"]] = True
        elif review["kind"] in PROOF_KINDS | {"meaning2word", "word2meaning", "typed"}:
            if pending.pop(review["word"], False):
                n += 1
                held += bool(review["correct"])
    return {"pct": round(100 * held / n) if n else None, "n": n}


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
                    " AND at>=?", learner, slug, (day - dt.timedelta(days=14)).isoformat())["n"]
    return {"is_due": bool(s["due"] and s["due"] <= day.isoformat()),
            "missed": missed, "thought": thought,
            "stubborn": int(s["lapses"] or 0) >= 4 or misses >= 3,
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
    counts["goal"] = 10 if goal == "auto" else goal
    forecast = [{"day": (day + dt.timedelta(days=i)).isoformat(),
                 "n": sum(1 for s in states.values() if s["due"] == (day + dt.timedelta(days=i)).isoformat())}
                for i in range(max(1, min(days, 120)))]
    groups = copy.deepcopy(data["collections"])
    for group in groups:
        for coll in group["collections"]:
            members = [w for w in words if w["collection"] == coll["id"] or coll["id"] in w["lists"]]
            coll["known"] = sum(int((w["state"] or {}).get("box") or 0) >= 4 and bool(w["proven"]) for w in members)
            coll["due"] = sum(w["is_due"] for w in members)
    return {"today": day.isoformat(), "groups": groups, "words": words,
            "counts": dict(counts), "forecast": forecast}


def deck(learner: str, source: str, value=None, n: int = 20, tz: int = 0,
         words: list[str] | None = None) -> list[str]:
    lib = library(learner, tz)
    rows = lib["words"]
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
        rows = [w for w in rows if not w["state"] and not w["placed"]]
    elif source == "saved":
        rows = [w for w in rows if w["saved"]]
    elif source in {"missed", "thought", "stubborn", "looked_up"}:
        rows = [w for w in rows if w[source]]
    elif source == "mine":
        rows = [w for w in rows if w["own"]]
    elif source == "today":
        due = [w for w in rows if w["is_due"]]
        fresh = [w for w in rows if not w["state"]]
        rows = due + fresh[:max(0, lib["counts"]["goal"] - lib["counts"]["new_today"])]
    else:
        raise HTTPException(422, "unknown word deck")
    rows.sort(key=lambda w: (not w["is_due"], -int(w["saved"]),
                             0 if w["collection"] == "sat-core" else 1,
                             -int((entry(w["slug"], learner) or {}).get("value", 1)), w["word"].casefold()))
    return [w["slug"] for w in rows[:max(0, min(n, 200))]]


def today_summary(learner: str, tz: int = 0) -> dict:
    lib = library(learner, tz)
    c = lib["counts"]
    proofs = sum(w["claimed"] and w["is_due"] for w in lib["words"])
    goal = c["goal"]
    new_left = max(0, goal - c["new_today"])
    minutes = round((c["due"] * 10 + new_left * 25) / 60, 1)
    return {"due": c["due"], "proofs": proofs, "new_goal": goal,
            "new_today": c["new_today"], "minutes": minutes,
            "done": c["due"] == 0 and new_left == 0, "goal": goal}


def minutes_today(learner: str, tz: int = 0) -> float:
    return today_summary(learner, tz)["minutes"]


def me_stats(learner: str, tz: int = 0) -> dict:
    c = library(learner, tz)["counts"]
    week = (local_day(tz) - dt.timedelta(days=7)).isoformat()
    reviews_week = db.one("SELECT COUNT(*) n FROM word_reviews WHERE learner=? AND at>=?"
                          " AND correct IS NOT NULL AND mode NOT IN ('sprint','outside','order')", learner, week)["n"]
    return {"known": c["known"], "claimed": c["claimed"],
            "studied": c["learning"] + c["known"], "saved": c["saved"],
            "reviews_week": reviews_week, "due": c["due"]}


def of_reason(template: str, reason: str) -> dict | None:
    """R&W only: math trap links were removed by v2-decisions."""
    return None


def gloss_index() -> dict:
    return {"v": 1, "words": [{"slug": w["slug"], "word": w["word"], "short": w["short"],
                               "also": w.get("also", [])} for w in content()["entries"].values()]}
