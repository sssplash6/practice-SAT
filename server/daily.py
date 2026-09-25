"""The day's questions: the same for every student on the same local date.

They are made from the date alone, so nobody has to set them and two students
anywhere get the identical questions -- the one thing an infinite bank cannot
give by accident. A slot is {subject, fmt}, its id `{subject}:{fmt}` (T14):
two Math slots here, and the two R&W slots Words generates (S9), which join
as soon as `words.daily_item` exists. The day's challenge is in challenge.py.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import statistics
from collections import Counter

from fastapi import HTTPException

from . import blueprint, db, deps, practice, scoring
# moved to challenge.py; kept here so older imports still work
from .challenge import CHALLENGE_SIZE, LADDER, MIX, SPR_AT, board, challenge, handle  # noqa: F401

BACK = 30               # days of past questions that can still be opened and answered (late)
GRACE_MIN = 60          # minutes after local midnight that yesterday's answer still counts on time
CROWD_MIN = 5           # on-time answers before a median time is shown
SAT_PACE_MS = {"math": deps.SECONDS_PER_QUESTION * 1000, "rw": 64 * 60 * 1000 // 54}

SLOTS = {
    "math:mcq": {"subject": "math", "fmt": "mcq", "label": "MATH · MULTIPLE CHOICE"},
    "math:spr": {"subject": "math", "fmt": "spr", "label": "MATH · GRID-IN"},
    "rw:wic": {"subject": "rw", "fmt": "wic", "label": "R&W · WORDS IN CONTEXT"},
    "rw:transition": {"subject": "rw", "fmt": "transition", "label": "R&W · TRANSITIONS"},
}
ALIASES = {"mcq": "math:mcq", "spr": "math:spr"}      # v2 clients and stored rows
MATH = ("math:mcq", "math:spr")


def today(tz: int = 0) -> str:
    """The student's own date. tz is JavaScript's getTimezoneOffset(), minutes
    behind UTC. Everyone on the same calendar day gets the same questions,
    which is what "of the day" means to the person reading it."""
    return local_now(tz).date().isoformat()


def local_now(tz: int = 0) -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)


def _hash(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest(), 16)


def rebuild(template: str, seed: int, qid: str) -> dict:
    """A stored question (key included) from its (template, seed)."""
    item = practice.generate(template, seed)
    q = practice.to_question(practice.Card.of(template, seed, item, practice.topic_of(template)), 1)
    q["id"] = qid
    return q


def question(day: str, fmt: str = "mcq") -> dict:
    """The Math question of the day, as stored (key included). 'mcq' keeps
    v2's pick, so history stays valid; 'spr' draws from the grid-in
    templates, never from the multiple-choice question's domain."""
    if fmt not in ("mcq", "spr"):
        raise ValueError(fmt)
    names = sorted(n for v in practice.catalogue()["by_topic"].values() for n in v)
    can = blueprint.abilities()
    pool = [n for n in names if any(f == fmt for _, f in can.get(n, ()))]
    skip = None
    if fmt == "spr":
        skip = question(day, "mcq")["domain"]
        topics = practice.catalogue()["topics"]
        pool = [n for n in pool if topics[practice.topic_of(n)].domain != skip]
    h = _hash(f"qotd:{day}" if fmt == "mcq" else f"qotd-spr:{day}")
    for k in range(200):
        template = pool[(h + k * 7919) % len(pool)]
        # the grid-in walks seeds on one template as draw_matching does
        for step in range(1 if fmt == "mcq" else 12):
            seed = (h >> 20) % 100_000 + k + step * 1_000
            try:
                item = practice.generate(template, seed)
            except Exception:
                continue
            if item.fmt != fmt:
                continue
            q = practice.to_question(practice.Card.of(template, seed, item, practice.topic_of(template)), 1)
            q["id"] = "qotd" if fmt == "mcq" else "qotd-spr"
            return q
    raise RuntimeError(f"no {fmt} question of the day for {day}")


# ------------------------------------------------------------------ slots

def slot_id(value) -> str | None:
    v = ALIASES.get(value, value) if isinstance(value, str) else None
    return v if v in SLOTS else None


def slots() -> list[str]:
    """The slots shown today: the R&W two only once Words can make them."""
    return list(MATH) + (["rw:wic", "rw:transition"] if deps.part("words", "daily_item") else [])


def session(slot: str, day: str, late: bool = False) -> str:
    if late:
        return f"qotd-late:{slot}:{day}"
    if slot == "math:mcq":
        return f"qotd:{day}"
    if slot == "math:spr":
        return f"qotd-spr:{day}"
    return f"qotd:{slot}:{day}"


def day_of(sid: str) -> tuple[str, str, bool] | None:
    """(slot, day, late) of a day's-question session, else None."""
    if not sid or not sid.startswith(("qotd:", "qotd-spr:", "qotd-late:")):
        return None
    day = sid[-10:]
    if sid.startswith("qotd-spr:"):
        return "math:spr", day, False
    if sid.startswith("qotd-late:"):
        return slot_id(sid[len("qotd-late:"):-11]) or "math:mcq", day, True
    middle = sid[len("qotd:"):-11]
    return (slot_id(middle) if middle else "math:mcq") or "math:mcq", day, False


def item(slot: str, day: str):
    """The slot's item: a stored Math question, or Words' generated R&W item."""
    if slot in MATH:
        return question(day, SLOTS[slot]["fmt"])
    make = deps.part("words", "daily_item")
    return make(day, SLOTS[slot]["fmt"]) if make else None


def public(slot: str, q: dict) -> dict:
    """What the page may see before the answer: no key, reasons, traps or seed."""
    if slot in MATH:
        from .drill import public as drill_public
        return drill_public(q)
    shown = deps.part("words", "public_item")
    out = shown(q) if shown else {k: q[k] for k in ("kind", "head", "text", "stem", "choices") if k in q}
    for k in ("answer", "answer_index", "reasons", "traps", "key", "seed", "word", "template", "spans"):
        out.pop(k, None)
    return out


def valid_day(day: str | None, tz: int, closed: int = 422) -> str:
    """A day's-question date the student may open: today back to today − 30.
    Before that the day is `closed` (422 to open; an answer gets 409)."""
    t = today(tz)
    if day is None:
        return t
    try:
        if not deps.DATE_OK.match(day):
            raise ValueError
        d = dt.date.fromisoformat(day)
    except ValueError:
        raise HTTPException(422, "day is YYYY-MM-DD")
    first = dt.date.fromisoformat(t) - dt.timedelta(days=BACK)
    if d > dt.date.fromisoformat(t):
        raise HTTPException(422, "that day's questions are not out yet")
    if d < first:
        raise HTTPException(closed, f"the day's questions go back {BACK} days")
    return day


def route(day: str | None, tz: int) -> tuple[str, bool]:
    """(day, late) for an answer: today is on time; yesterday is on time
    within an hour of local midnight; any other day back to today − 30 is
    late (it moves mastery, never the crowd or the streak)."""
    day = valid_day(day, tz, closed=409)
    t = today(tz)
    if day == t:
        return day, False
    now = local_now(tz)
    yesterday = (now.date() - dt.timedelta(days=1)).isoformat()
    if day == yesterday and now.hour * 60 + now.minute < GRACE_MIN:
        return day, False
    return day, True


# ------------------------------------------------------------------ answers

def _given(text):
    return int(text) if text is not None and str(text).isdigit() else text


def _rows(cols: str, where: str, *args) -> list:
    """Day's-question answers: every slot's `attempts` rows (R57 files the R&W
    ones there too), then Words' own rows that carry no attempt yet, so one
    answer is never counted twice and nothing is missed before R57 lands."""
    return (db.rows(f"SELECT {cols} FROM attempts WHERE {where} ORDER BY id", *args)
            + db.rows(f"SELECT {cols} FROM word_reviews WHERE attempt IS NULL AND {where} ORDER BY id", *args))


def answered(learner: str, slot: str, day: str) -> dict | None:
    """This learner's one answer in that slot on that day, on time or late."""
    for late in (False, True):
        sid = session(slot, day, late)
        got = _rows("template, seed, given, correct, ms, at, id", "learner=? AND session=?", learner, sid)
        r = got[0] if got else None
        if r:
            given = r["given"] if SLOTS[slot]["fmt"] == "spr" else _given(r["given"])
            return {**dict(r), "given": given, "late": late, "session": sid}
    return None


def _group(value: str):
    """Grid-in answers grouped by exact value (0.5 is 1/2), else by text."""
    exact = scoring._exact(value)
    return exact if exact is not None else scoring.normalise(value)


def crowd(slot: str, day: str) -> dict:
    """On-time answers only, everyone but sample learners."""
    rows = _rows("given, correct, ms", f"session=? AND {db.NOT_SAMPLE}", session(slot, day))
    out = {"answered": len(rows), "right": sum(bool(r["correct"]) for r in rows),
           "median_ms": None}
    times = [r["ms"] for r in rows if r["ms"] is not None]
    if len(rows) >= CROWD_MIN and times:
        out["median_ms"] = int(statistics.median(times))
    if SLOTS[slot]["fmt"] == "spr":
        wrong = [str(r["given"]) for r in rows if not r["correct"] and r["given"] not in (None, "")]
        groups: dict = {}
        for g in wrong:
            groups.setdefault(_group(g), Counter())[g] += 1
        top = sorted(groups.values(), key=lambda c: -sum(c.values()))[:3]
        out["top_wrong"] = [{"value": c.most_common(1)[0][0], "n": sum(c.values())} for c in top]
    else:
        picks = [0, 0, 0, 0]
        for r in rows:
            g = _given(r["given"])
            if isinstance(g, int) and 0 <= g < 4:
                picks[g] += 1
        out["picks"] = picks
    return out


def _cap(text: str | None) -> str | None:
    return text[:1].upper() + text[1:] if text else None


def spread(picks: list[int] | None, mistakes: list) -> list[dict] | None:
    """R27 / Compete's panel: each option's share of the on-time picks and
    the mistake it names (None for the key)."""
    if not picks:
        return None
    n = sum(picks)
    return [{"index": i, "n": p, "share": round(p / n, 3) if n else None,
             "mistake": mistakes[i] if i < len(mistakes) else None} for i, p in enumerate(picks)]


def entry_line(given, key) -> dict | None:
    """T14: a grid-in entry error, named as entry (the answer is still wrong)."""
    kind = scoring.entry_error(str(given or ""), str(key))
    if not kind:
        return None
    forms = scoring.accepted_forms(str(key))
    if kind == "form":
        shown = " or ".join(forms[:2]) or str(key)
        return {"kind": kind, "text": f"Right value, rejected form: you entered {given}. The grid takes {shown}."}
    fills = [f for f in forms if "/" not in f]
    return {"kind": kind, "text": f"Stopped too early: {given} for {key}. Fill the grid: {', '.join(fills[:-1])}"
                                  f"{' or ' if len(fills) > 1 else ''}{fills[-1] if fills else key}."}


def feedback(slot: str, day: str, q: dict, given, late: bool, ms: int | None = None) -> dict:
    """What an answered Math slot shows: the key, the named mistake, the
    rationale, every option explained, the on-time crowd and the entry line."""
    from .progress import _reason_of          # the one rule record() files the mistake by
    ok = scoring.is_correct(q, given)
    reasons = list(q.get("reasons") or [""] * 4)
    reason = "" if ok else _reason_of(q, given)[0]
    out = {"slot": slot, "subject": "math", "fmt": q["type"], "day": day, "late": late,
           "correct": ok, "given": given, "answer": q["answer"], "ms": ms,
           "mistake": _cap(reason), "rationale": q["rationale"],
           "crowd": crowd(slot, day), "sat_pace_ms": SAT_PACE_MS["math"],
           "choices_explained": None, "entry": None, "options": None,
           "template": q["key"], "topic": q["topic"], "difficulty": q["difficulty"]}
    if q["type"] == "mcq":
        key = "ABCD".index(q["answer"])
        out["answer_index"] = key
        out["choices_explained"] = [None if i == key else _cap(reasons[i] if i < len(reasons) else "")
                                    for i in range(4)]
        out["options"] = spread(out["crowd"].get("picks"), out["choices_explained"])
    elif not ok:
        out["entry"] = entry_line(given, q["answer"])
        out["accepted"] = scoring.accepted_forms(str(q["answer"]))
    return out


def rw_feedback(slot: str, day: str, gen: dict, given, late: bool, ms: int | None = None,
                reply: dict | None = None) -> dict:
    """An answered R&W slot: Words' reply fields plus the key word, its
    meaning and the on-time crowd."""
    word = gen.get("word")
    entry = deps.part("words", "entry")
    meaning = ((entry(word) or {}).get("meaning") if entry and word else None)
    base = {k: gen.get(k) for k in ("reasons", "traps", "spans", "needs", "logic_needed", "relation")
            if k in gen}
    out = {**base, **(reply or {}), "slot": slot, "subject": "rw", "fmt": SLOTS[slot]["fmt"], "day": day,
           "late": late, "given": given, "answer_index": gen.get("answer_index"), "ms": ms,
           "key_word": word, "meaning": meaning, "crowd": crowd(slot, day),
           "sat_pace_ms": SAT_PACE_MS["rw"]}
    out["correct"] = bool(out.get("correct", isinstance(given, int) and given == gen.get("answer_index")))
    if isinstance(given, int) and gen.get("traps") and 0 <= given < len(gen["traps"]):
        out.setdefault("trap", gen["traps"][given])
    out["options"] = spread(out["crowd"].get("picks"), list(gen.get("traps") or []))
    return out


def mine(learner: str, slot: str, day: str) -> dict | None:
    """This learner's feedback for the slot, rebuilt from the attempt's own
    (template, seed) so a bank change cannot swap what they saw."""
    got = answered(learner, slot, day)
    if not got:
        return None
    if slot in MATH:
        q = rebuild(got["template"], got["seed"], "qotd" if slot == "math:mcq" else "qotd-spr")
        return feedback(slot, day, q, got["given"], got["late"], got["ms"])
    gen = item(slot, day)
    return rw_feedback(slot, day, gen, got["given"], got["late"], got["ms"],
                       {"correct": bool(got["correct"])}) if gen else None


# ------------------------------------------------------------------ the learner's record

def _on_time_days(learner: str) -> dict[str, list[int]]:
    """Per local day, the correct flags of this learner's on-time answers
    (graced ones included, since they are filed in that day's session)."""
    out: dict[str, list[int]] = {}
    for r in _rows("session, correct", "learner=? AND (session LIKE 'qotd:%' OR session LIKE 'qotd-spr:%')", learner):
        got = day_of(r["session"])
        if got and not got[2]:
            out.setdefault(got[1], []).append(int(bool(r["correct"])))
    return out


def qotd_streak(learner: str, tz: int = 0) -> dict:
    """R13's day's-questions streak: consecutive days ending today or
    yesterday with at least one on-time answer; best is the longest run."""
    days = sorted(_on_time_days(learner))
    best = run = 0
    prev = None
    for d in days:
        day = dt.date.fromisoformat(d)
        run = run + 1 if prev and day - prev == dt.timedelta(days=1) else 1
        best = max(best, run)
        prev = day
    have = set(days)
    at = dt.date.fromisoformat(today(tz))
    if at.isoformat() not in have:
        at -= dt.timedelta(days=1)
    current = 0
    while at.isoformat() in have:
        current += 1
        at -= dt.timedelta(days=1)
    return {"current": current, "best": best}


def month(learner: str, tz: int = 0) -> dict:
    """This local month: right of answered on time, and the crowd's % right."""
    prefix = today(tz)[:7]
    mine_ = [c for d, flags in _on_time_days(learner).items() if d.startswith(prefix) for c in flags]
    n = right = 0
    for r in _rows("session, correct", f"(session LIKE ? OR session LIKE ? OR session LIKE ?) AND {db.NOT_SAMPLE}",
                   f"qotd:{prefix}-%", f"qotd-spr:{prefix}-%", f"qotd:%:%:{prefix}-%"):
        got = day_of(r["session"])
        if got and not got[2]:
            n += 1
            right += int(bool(r["correct"]))
    return {"right": sum(mine_), "of": len(mine_), "crowd_pct": round(100 * right / n) if n else None}


def by_day(learner: str | None) -> dict[str, dict[str, str]]:
    """{day: {slot: 'right' | 'wrong'}} for every day this learner answered,
    on time or late (the first answer in a slot wins), from one read."""
    out: dict[str, dict[str, str]] = {}
    if not learner:
        return out
    for r in _rows("session, correct", "learner=? AND (session LIKE 'qotd:%' OR session LIKE 'qotd-spr:%'"
                   " OR session LIKE 'qotd-late:%')", learner):
        got = day_of(r["session"])
        if got:
            out.setdefault(got[1], {}).setdefault(got[0], "right" if r["correct"] else "wrong")
    return out


def marks(learner: str | None, day: str, shown: list[str] | None = None, known: dict | None = None) -> dict:
    """{slot: 'right' | 'wrong' | None} for one day, on time or late."""
    got = (known if known is not None else by_day(learner)).get(day, {})
    return {slot: got.get(slot) for slot in shown or slots()}


def past(learner: str | None, tz: int = 0, n: int = 7) -> list[dict]:
    """The n days before today, with a mark per slot (v2's mcq / spr kept)."""
    t = dt.date.fromisoformat(today(tz))
    shown, known = slots(), by_day(learner)
    out = []
    for back in range(n, 0, -1):
        d = (t - dt.timedelta(days=back)).isoformat()
        m = marks(learner, d, shown, known)
        out.append({"day": d, "marks": m, "mcq": m["math:mcq"], "spr": m["math:spr"]})
    return out


# ------------------------------------------------------------------ the drill registry (R10)

def _range_ok(day) -> bool:
    """today − 30 to today in some zone on Earth (drill.resolve has no X-Tz)."""
    try:
        if not isinstance(day, str) or not deps.DATE_OK.match(day):
            return False
        d = dt.date.fromisoformat(day)
    except ValueError:
        return False
    live = [dt.date.fromisoformat(x) for x in deps.live_days()]
    return min(live) - dt.timedelta(days=BACK) <= d <= max(live)


def resolve_drill(learner: str, body: dict) -> dict:
    """`like: {day, slot}` -> the day's own template on fresh seeds, the
    day's seed excluded; 409 until this learner has answered that slot."""
    like = body.pop("like")
    if not isinstance(like, dict) or set(like) - {"day", "slot"}:
        raise HTTPException(422, {"field": "like", "reason": "expected {day, slot}"})
    slot = slot_id(like.get("slot") or "math:mcq")
    if slot not in MATH:
        raise HTTPException(422, {"field": "like", "reason": "a Math slot: an R&W twin is POST /api/qotd/another"})
    if not _range_ok(like.get("day")):
        raise HTTPException(404, {"reason": "day_out_of_range"})
    got = answered(learner, slot, like["day"])
    if not got:
        raise HTTPException(409, {"reason": "answer it first"})
    count = body.get("count", 5)
    if type(count) is not int or not 1 <= count <= 20:
        raise HTTPException(422, {"field": "count", "reason": "use 1–20"})
    exclude = body.get("exclude") if isinstance(body.get("exclude"), list) else []
    body.update(templates=[got["template"]], topics=[practice.topic_of(got["template"])],
                exclude=exclude + [[got["template"], got["seed"]]], count=count,
                formats=[SLOTS[slot]["fmt"]], source=body.get("source", "qotd"))
    return body


def saved_item(learner: str, day: str, slot: str) -> dict:
    """For POST /api/saved {qotd: day, slot, on} (S10): the (template, seed)
    that regenerates the slot's question; 409 until it is answered."""
    s = slot_id(slot)
    if s not in MATH:
        raise HTTPException(422, "slot is math:mcq or math:spr")
    got = answered(learner, s, day) if _range_ok(day) else None
    if not got:
        raise HTTPException(409, "answer it first")
    return {"template": got["template"], "seed": got["seed"], "topic": practice.topic_of(got["template"]),
            "session": got["session"], "qid": "qotd" if s == "math:mcq" else "qotd-spr"}


def remember(learner: str, q: dict) -> None:
    """The day's seed is never served to this learner again."""
    db.remember(learner, [{"key": q["key"], "seed": q["seed"], "stem_hash": practice.stem_hash(q["stem"])}],
                deps.now())


if __name__ == "__main__":
    assert day_of("qotd:2026-09-23") == ("math:mcq", "2026-09-23", False)
    assert day_of("qotd-spr:2026-09-23") == ("math:spr", "2026-09-23", False)
    assert day_of("qotd:rw:wic:2026-09-23") == ("rw:wic", "2026-09-23", False)
    assert day_of("qotd-late:math:spr:2026-09-20") == ("math:spr", "2026-09-20", True)
    assert day_of("qotd-late:mcq:2026-09-20") == ("math:mcq", "2026-09-20", True)
    assert all(day_of(session(s, "2026-09-23", late)) == (s, "2026-09-23", late) for s in SLOTS for late in (0, 1))
    spr = question("2026-09-23", "spr")
    assert spr["type"] == "spr" and spr["domain"] != question("2026-09-23", "mcq")["domain"]
    assert entry_line("1 1/2", "3/2")["kind"] == "form" and entry_line(".66", "2/3")["kind"] == "early"
    assert entry_line("455", "460") is None
    print("daily ok", json.dumps({"spr": spr["key"]}))
