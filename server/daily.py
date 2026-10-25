"""The day's questions: the same for every student on the same local date.

They are made from the date alone, so nobody has to set them and two students
anywhere get the identical questions -- the one thing an infinite bank cannot
give by accident. A slot is {subject, fmt}, its id `{subject}:{fmt}` (T14):
two Math slots and the R&W bank's passage question (`rw:bank`) here, and the
R&W vocabulary slots Words generates (S9), which join as soon as
`words.daily_item` exists. The day's challenge is in challenge.py.
"""

from __future__ import annotations

import datetime as dt
import functools
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
    "math:mcq": {"subject": "math", "fmt": "mcq", "label": "MATH · MULTIPLE CHOICE", "bank": True},
    "math:spr": {"subject": "math", "fmt": "spr", "label": "MATH · GRID-IN", "bank": True},
    "rw:bank": {"subject": "rw", "fmt": "mcq", "label": "R&W · PASSAGE", "bank": True},
    "rw:wic": {"subject": "rw", "fmt": "wic", "label": "R&W · WORDS IN CONTEXT", "bank": False},
    "rw:transition": {"subject": "rw", "fmt": "transition", "label": "R&W · TRANSITIONS", "bank": False},
}
ALIASES = {"mcq": "math:mcq", "spr": "math:spr"}      # v2 clients and stored rows
MATH = ("math:mcq", "math:spr")
# the slots made from the question bank: stored as (template, seed), answered through progress.record and
# feedback(), twinned by POST /api/drill {like}; the other R&W slots are Words' generated vocabulary items
BANK = MATH + ("rw:bank",)
QID = {"math:mcq": "qotd", "math:spr": "qotd-spr", "rw:bank": "qotd-rw"}
# From this day the R&W bank's passage question takes the Transitions slot's place (Transitions is a bank skill
# now), so four slots stay; days before it keep the slots they were answered in. Set to the deploy day.
BANK_FROM = "2026-10-24"


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
    names = sorted(n for k, v in practice.catalogue()["by_topic"].items() if deps.subject_of(k) == "math" for n in v)
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


def rw_question(day: str) -> dict:
    """The R&W bank's question of the day, as stored (key included): one written item picked by
    the date from every R&W type, the same for everyone."""
    names = sorted(n for k, v in practice.catalogue()["by_topic"].items() if deps.subject_of(k) == "rw" for n in v)
    h = _hash(f"qotd-rw:{day}")
    for k in range(200):
        template = names[(h + k * 7919) % len(names)]
        seed = (h >> 20) % 100_000 + k
        try:
            item = practice.generate(template, seed)
        except Exception:
            continue
        q = practice.to_question(practice.Card.of(template, seed, item, practice.topic_of(template)), 1)
        q["id"] = QID["rw:bank"]
        return q
    raise RuntimeError(f"no R&W question of the day for {day}")


def rw_for(day: str, learner: str | None) -> dict:
    """The R&W slot as this learner meets it. A type holds a few written items, so the day's pick
    can be one they already met in practice: then an unseen item of the same type, else of another
    type of its skill (what a twin of a written item is, DESIGN §2).
    ponytail: a swapped learner answers another item under the same session; the crowd reads the
    day's own item only (crowd()), so their answer counts for them but not in its picks."""
    q = rw_question(day)
    if not learner:
        return q
    from .drill import _builder
    b = _builder(learner, dedupe="question")
    if (q["key"], q["seed"]) not in b.seen and b.signature(practice.generate(q["key"], q["seed"])) not in b.seen_stems:
        return q
    topic = practice.topic_of(q["key"])
    others = sorted((t for t in practice.catalogue()["by_topic"].get(topic, ()) if t != q["key"]),
                    key=lambda t: _hash(f"{learner}:{day}:{t}"))
    for name in [q["key"], *others]:
        card = b.draw(name, topic)
        if card is not None:
            got = practice.to_question(card, 1)
            got["id"] = QID["rw:bank"]
            return got
    return q


# ------------------------------------------------------------------ slots

def slot_id(value) -> str | None:
    v = ALIASES.get(value, value) if isinstance(value, str) else None
    return v if v in SLOTS else None


def slots() -> list[str]:
    """Every slot an answer may name: both Math ones and the R&W bank's, and Words' two once Words
    can make them (Transitions stays for the days before BANK_FROM)."""
    return list(BANK) + (["rw:wic", "rw:transition"] if deps.part("words", "daily_item") else [])


@functools.lru_cache(maxsize=128)
def shown(day: str) -> tuple[str, ...]:
    """The slots on the page that day: both Math ones, then R&W's: from BANK_FROM the bank's
    passage question and Words in Context, before it Words' two, each only when Words can make
    an item for it (N in `1 of N`, the past marks, the calendar).
    ponytail: cached per process; a Words content reload shows after a restart."""
    rw = ("rw:bank", "rw:wic") if day >= BANK_FROM else ("rw:wic", "rw:transition")
    return tuple(s for s in (*MATH, *rw) if s in slots() and (s in BANK or item(s, day) is not None))


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


def item(slot: str, day: str, learner: str | None = None):
    """The slot's item: a stored bank question (the R&W one as this learner meets it), or Words'
    generated R&W item."""
    if slot in MATH:
        return question(day, SLOTS[slot]["fmt"])
    if slot == "rw:bank":
        return rw_for(day, learner)
    make = deps.part("words", "daily_item")
    return make(day, SLOTS[slot]["fmt"]) if make else None


def rebuild_slot(slot: str, got: dict) -> dict:
    """A bank slot's question from the attempt's own (template, seed)."""
    return rebuild(got["template"], got["seed"], QID[slot])


def public(slot: str, q: dict) -> dict:
    """What the page may see before the answer: no key, reasons, traps or seed."""
    if slot in BANK:
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
    ones there too), then Words' own rows for sessions with no attempts row
    (word_reviews.attempt is the try number, not a link), so one answer is
    never counted twice and nothing is missed before R57 lands."""
    return (db.rows(f"SELECT {cols} FROM attempts WHERE {where} ORDER BY id", *args)
            + db.rows(f"SELECT {cols} FROM word_reviews AS w WHERE {where} AND NOT EXISTS (SELECT 1 FROM attempts AS a"
                      f" WHERE a.session=w.session AND a.learner=w.learner) ORDER BY id", *args))


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


# SEC-02: the questions are public and the same for everyone, so a code minted
# on the day can read the key and a second code answer it right. Nothing here
# is ranked, so that only fools its author; what it must not do is move the
# crowd everyone else reads. The crowd counts learners who were here before
# the day began (created before its UTC midnight; a session id ends in its
# day), plus the one asking.
# ponytail: pre-aged throwaway codes still count; a verified identity would
# close that, once ranked daily scores exist.
ESTABLISHED = "learner IN (SELECT id FROM learners WHERE created < substr(session, -10))"


def crowd(slot: str, day: str, you: str | None = None) -> dict:
    """On-time answers of established learners (SEC-02) and the asker's own;
    never sample learners."""
    where, args = f"session=? AND {db.NOT_SAMPLE} AND ({ESTABLISHED} OR learner=?)", [session(slot, day), you or ""]
    if slot == "rw:bank":                   # only the day's own item: a learner who met it got another (rw_for)
        q = rw_question(day)
        where, args = where + " AND template=? AND seed=?", args + [q["key"], q["seed"]]
    rows = _rows("given, correct, ms", where, *args)
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


def feedback(slot: str, day: str, q: dict, given, late: bool, ms: int | None = None,
             you: str | None = None) -> dict:
    """What an answered bank slot (Math, or R&W's passage question) shows: the key, the named
    mistake, the rationale, every option explained, the on-time crowd and the entry line."""
    from .progress import _reason_of          # the one rule record() files the mistake by
    subject = SLOTS[slot]["subject"]
    ok = scoring.is_correct(q, given)
    reasons = list(q.get("reasons") or [""] * 4)
    reason = "" if ok else _reason_of(q, given)[0]
    out = {"slot": slot, "subject": subject, "fmt": q["type"], "day": day, "late": late,
           "correct": ok, "given": given, "answer": q["answer"], "ms": ms,
           "mistake": _cap(reason), "rationale": q["rationale"],
           "crowd": crowd(slot, day, you), "sat_pace_ms": SAT_PACE_MS[subject],
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
                reply: dict | None = None, you: str | None = None) -> dict:
    """An answered R&W slot: Words' reply fields plus the key word, its
    meaning and the on-time crowd."""
    given = _given(given)                   # Words stores the pick as text
    word = gen.get("word")
    entry = deps.part("words", "entry")
    meaning = ((entry(word) or {}).get("meaning") if entry and word else None)
    base = {k: gen.get(k) for k in ("reasons", "traps", "spans", "needs", "logic_needed", "relation")
            if k in gen}
    out = {**base, **(reply or {}), "slot": slot, "subject": "rw", "fmt": SLOTS[slot]["fmt"], "day": day,
           "late": late, "given": given, "answer_index": gen.get("answer_index"), "ms": ms,
           "key_word": word, "meaning": meaning, "crowd": crowd(slot, day, you),
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
    if slot in BANK:
        return feedback(slot, day, rebuild_slot(slot, got), got["given"], got["late"], got["ms"], learner)
    gen = item(slot, day)
    return rw_feedback(slot, day, gen, got["given"], got["late"], got["ms"],
                       {"correct": bool(got["correct"])}, learner) if gen else None


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
    for r in _rows("session, correct", f"(session LIKE ? OR session LIKE ? OR session LIKE ?) AND {db.NOT_SAMPLE}"
                   f" AND {ESTABLISHED}", f"qotd:{prefix}-%", f"qotd-spr:{prefix}-%", f"qotd:%:%:{prefix}-%"):
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


def marks(learner: str | None, day: str, only=None, known: dict | None = None) -> dict:
    """{slot: 'right' | 'wrong' | None} for one day's shown slots, on time or late."""
    got = (known if known is not None else by_day(learner)).get(day, {})
    return {slot: got.get(slot) for slot in only or shown(day)}


def past(learner: str | None, tz: int = 0, n: int = 7) -> list[dict]:
    """The n days before today, with a mark per slot (v2's mcq / spr kept)."""
    t = dt.date.fromisoformat(today(tz))
    known = by_day(learner)
    out = []
    for back in range(n, 0, -1):
        d = (t - dt.timedelta(days=back)).isoformat()
        m = marks(learner, d, None, known)
        out.append({"day": d, "marks": m, "mcq": m.get("math:mcq"), "spr": m.get("math:spr")})
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
    day's seed excluded; 409 until this learner has answered that slot. For the
    R&W bank slot a fresh seed is an unseen written item of the type, and the set
    goes on with the skill's other types when the type is spent (drill's sibling rule)."""
    like = body.pop("like")
    if not isinstance(like, dict) or set(like) - {"day", "slot"}:
        raise HTTPException(422, {"field": "like", "reason": "expected {day, slot}"})
    slot = slot_id(like.get("slot") or "math:mcq")
    if slot not in BANK:
        raise HTTPException(422, {"field": "like", "reason": "a bank slot: a Words twin is POST /api/qotd/another"})
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
                formats=[SLOTS[slot]["fmt"]], source=body.get("source", "qotd"), subject=SLOTS[slot]["subject"])
    return body


def saved_item(learner: str, day: str, slot: str) -> dict:
    """For POST /api/saved {qotd: day, slot, on} (S10): the (template, seed)
    that regenerates the slot's question; 409 until it is answered."""
    s = slot_id(slot)
    if s not in BANK:
        raise HTTPException(422, "slot is math:mcq, math:spr or rw:bank")
    got = answered(learner, s, day) if _range_ok(day) else None
    if not got:
        raise HTTPException(409, "answer it first")
    return {"template": got["template"], "seed": got["seed"], "topic": practice.topic_of(got["template"]),
            "session": got["session"], "qid": QID[s]}


def remember(learner: str, q: dict) -> None:
    """The day's item is never served to this learner again (a written R&W item by its whole
    question: its stem repeats across passages)."""
    from .drill import _hash_of
    mark = _hash_of(q) if q.get("text") else practice.stem_hash(q["stem"])
    db.remember(learner, [{"key": q["key"], "seed": q["seed"], "stem_hash": mark}], deps.now())


if __name__ == "__main__":
    assert day_of("qotd:2026-09-23") == ("math:mcq", "2026-09-23", False)
    assert day_of("qotd-spr:2026-09-23") == ("math:spr", "2026-09-23", False)
    assert day_of("qotd:rw:wic:2026-09-23") == ("rw:wic", "2026-09-23", False)
    assert day_of("qotd:rw:bank:2026-10-23") == ("rw:bank", "2026-10-23", False)
    rq = rw_question("2026-10-23")
    assert deps.subject_of(rq["key"]) == "rw" and rq["text"] and rw_question("2026-10-23")["stem"] == rq["stem"]
    assert "rw:bank" in shown("2026-10-23") and "rw:transition" not in shown("2026-10-23")
    assert "rw:bank" not in shown("2026-09-23")
    assert day_of("qotd-late:math:spr:2026-09-20") == ("math:spr", "2026-09-20", True)
    assert day_of("qotd-late:mcq:2026-09-20") == ("math:mcq", "2026-09-20", True)
    assert all(day_of(session(s, "2026-09-23", late)) == (s, "2026-09-23", late) for s in SLOTS for late in (0, 1))
    spr = question("2026-09-23", "spr")
    assert spr["type"] == "spr" and spr["domain"] != question("2026-09-23", "mcq")["domain"]
    assert entry_line("1 1/2", "3/2")["kind"] == "form" and entry_line(".66", "2/3")["kind"] == "early"
    assert entry_line("455", "460") is None
    print("daily ok", json.dumps({"spr": spr["key"]}))
