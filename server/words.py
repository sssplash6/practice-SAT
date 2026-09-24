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

# ------------------------------------------------------------------ generated Reading & Writing items

def _servable(row: dict) -> bool:
    return bool(row.get("reviewed")) or os.environ.get("SATF_WORDS_UNREVIEWED") == "1"


def _suppressed(frame: str) -> bool:
    return bool(db.one("SELECT 1 FROM word_suppress WHERE frame=? AND word='*'", frame))


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
            if kind and w["slug"] not in suppressed:
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
        excluded = {logic, *pair.get("compatible", [])}
        candidates: dict[str, list[dict]] = defaultdict(list)
        for transition in data["transitions"]:
            other = transition["logic"]
            if other not in excluded and logic not in transition.get("also_reads", []) and not _appears(transition, passage):
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
                "difficulty": pair.get("difficulty", "medium"), "seed": seed, "word": slug,
                "kind": "transition", "stem": "Which choice completes the text with the most logical transition?",
                "text": passage, "choices": [w["word"] for w, _ in options],
                "answer_index": next(i for i, (_, l) in enumerate(options) if l == logic),
                "reasons": reasons, "traps": [None if l == logic else "wrong_logic" for _, l in options],
                "spans": spans, "rationale": f"The two ideas have a {logic} relationship.",
                "needs": pair["relation"], "logic_needed": logic,
                "option_logics": [l for _, l in options], "relation": pair["relation"],
                "subject": pair["subject"]}
    raise ValueError("unknown Reading & Writing template")


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
    reps = int(state(learner, slug)["reps"] if reps is None else reps)
    previous = [r["template"] for r in rw_answers(learner) if r["word"] == slug]
    seen = set(previous)
    last = previous[-1] if previous else None
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
    out["item_id"] = item_id or generated.get("item_id")
    return out
