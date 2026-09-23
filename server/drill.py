"""Practice with the answer shown: one question at a time, made when asked for.

A drill does not build its set up front. Each question is generated when the
student asks for the next one, so it can answer to what just happened:

* a wrong answer is followed by the same template on a fresh seed -- the same
  trap with new numbers -- and a set with a length grows by one to fit it;
* a template the student has an open mistake on is asked before the others;
* a set asked for with no length simply never runs out.

Everything the student is given is remembered against them, so nothing is
ever served twice, and every answer is filed through progress.record so the
map, the coach and the mistakes list move as they go.
"""

from __future__ import annotations

import datetime as dt
import json
import zlib
from collections import Counter
from types import SimpleNamespace

from satbank.registry import generate, topic_of

from . import blueprint, db, practice, progress, scoring

MAX_FIXED = 120             # the longest set with a length
GRACE = 15                  # seconds past a timed set's clock an answer may still arrive
TIERS = ("easy", "medium", "hard")
PUBLIC = ("id", "topic", "topic_name", "domain", "difficulty", "skill", "type",
          "stem", "choices", "latex", "figure", "table")


class Closed(Exception):
    """The set is finished, or its clock ran out: nothing more is filed."""


def _cfg(row) -> dict:
    return json.loads(row["cfg"] or "{}")


def _served(row) -> list[dict]:
    return json.loads(row["questions"] or "[]")


def _save(sid: str, cfg: dict, served: list[dict]) -> None:
    db.run("UPDATE sessions SET cfg=?, questions=? WHERE id=?",
           json.dumps(cfg), json.dumps(served, ensure_ascii=False), sid)


def public(q: dict) -> dict:
    out = {k: q[k] for k in PUBLIC if k in q}
    out["repair"] = bool(q.get("repair"))
    return out


# ------------------------------------------------------------------ building

def _builder(learner: str) -> practice.Builder:
    seen, stems = db.seen_for(learner)
    b = practice.Builder(learner, seen, stems)
    # Start each template's walk past the seeds this learner has already used,
    # or one they have drilled sixty times reads as spent.
    for t, n in Counter(t for t, _ in seen).items():
        b.cursor[t] = n
    return b


def _fresh(b: practice.Builder, template: str, allowed: set[str] | None) -> practice.Card | None:
    """The next unseen item from a template, of an allowed difficulty."""
    topic = topic_of(template)
    for _ in range(12):
        card = b.draw(template, topic)
        if card is None:
            return None
        if not allowed or card.feats["difficulty"] in allowed:
            return card
        b.keep(card)              # not this one; move the template past it
    return None


def _tiers_of(template: str) -> set[str]:
    return {d for d, _ in blueprint.abilities().get(template, ())}


def _pick(row, cfg: dict, served: list[dict], b: practice.Builder):
    """The next card, and whether it is a repair."""
    allowed = set(cfg.get("difficulty") or TIERS)
    learner = row["learner"]

    # the same trap with new numbers, before anything else is asked -- even the
    # next saved question -- and a difficulty filter never blocks it
    rep = cfg.pop("repair", None)
    if rep:
        card = _fresh(b, rep, None)
        if card:
            return card, True

    # a saved question, served again exactly
    while cfg.get("items"):
        template, seed = cfg["items"].pop(0)
        try:
            return practice.Card.of(template, seed, generate(template, seed), topic_of(template)), False
        except Exception:
            continue

    # templates queued by a report or the mistakes list
    while cfg.get("queue"):
        card = _fresh(b, cfg["queue"].pop(0), None)
        if card:
            return card, True

    topics = cfg.get("topics") or []
    by_topic = practice.catalogue()["by_topic"]
    used = Counter(q["key"] for q in served)
    recent = [SimpleNamespace(feats=q["feats"]) for q in served[-practice.WINDOW:] if "feats" in q]
    last_keys = {q["key"] for q in served[-3:]}

    for _ in range(len(topics)):
        topic = topics[cfg.get("turn", 0) % len(topics)]
        cfg["turn"] = cfg.get("turn", 0) + 1
        pool = [t for t in by_topic.get(topic, []) if _tiers_of(t) & allowed] or by_topic.get(topic, [])

        # an open mistake in this topic is asked before anything new
        for trap in progress.open_traps(learner, topic):
            if trap["template"] in pool and trap["template"] not in last_keys:
                card = _fresh(b, trap["template"], allowed)
                if card:
                    return card, False

        # otherwise the least used templates, tie-broken per session so two
        # sessions do not open on the same one
        salt = row["id"]
        ranked = sorted(pool, key=lambda t: (used[t], zlib.crc32(f"{salt}:{t}".encode())))
        cards = [c for c in (_fresh(b, t, allowed) for t in ranked[:practice.CANDIDATES]) if c]
        if cards:
            return min(cards, key=lambda c: practice.penalty(c, recent, dict(used))), False
    return None, False


def _serve(row, cfg: dict, served: list[dict]) -> dict | None:
    b = _builder(row["learner"])
    card, repair = _pick(row, cfg, served, b)
    if card is None:
        return None
    q = practice.to_question(card, len(served) + 1)
    q["id"] = f"d{len(served) + 1:03d}"
    q["feats"] = card.feats
    q["repair"] = repair
    served.append(q)
    db.remember(row["learner"], [{"key": card.key, "seed": card.seed,
                                  "stem_hash": practice.stem_hash(card.item.stem)}], progress.now())
    return q


# ------------------------------------------------------------------ the session

def create(learner: str, sid: str, topics: list[str], count: int | None,
           difficulty: list[str] | None, timed: bool, source: str,
           queue: list[str] | None = None, items: list[list] | None = None,
           kind: str = "drill", fixed: bool = False, day: str | None = None) -> None:
    """A fixed set (the challenge) is the same for everyone, so it has no
    repairs and never grows; the answer is still shown after each question."""
    every = set(topics) | {topic_of(t) for t in (queue or [])} | {topic_of(t) for t, _ in (items or [])}
    cfg = {
        "topics": topics, "count": count, "total": count,
        "difficulty": [d for d in (difficulty or TIERS) if d in TIERS] or list(TIERS),
        "timed": bool(timed), "source": source, "turn": 0, "fixed": fixed,
        "queue": list(queue or []), "items": [list(i) for i in (items or [])],
        "before": {t: progress.topic_mastery(learner, t) for t in every},
    }
    row = (sid, kind, learner, progress.now(), json.dumps(cfg), "[]", day)
    if day is None:
        db.run("INSERT INTO sessions (id, kind, learner, started, cfg, questions, day)"
               " VALUES (?,?,?,?,?,?,?)", *row)
    else:
        # A day's sitting exists once per learner. The check is inside the
        # insert, so two starts at the same moment still make one; the caller
        # reads back whichever was made.
        db.run("INSERT INTO sessions (id, kind, learner, started, cfg, questions, day)"
               " SELECT ?,?,?,?,?,?,? WHERE NOT EXISTS"
               " (SELECT 1 FROM sessions WHERE kind=? AND learner=? AND day=?)", *row, kind, learner, day)


def seconds_of(cfg: dict) -> int | None:
    """A timed set's clock, at the real test's pace."""
    if cfg.get("timed") and cfg.get("count"):
        return cfg["count"] * blueprint.MODULE_SECONDS // blueprint.MODULE_SIZE
    return None


def overtime(row, cfg: dict) -> bool:
    secs = seconds_of(cfg)
    if not secs:
        return False
    began = dt.datetime.fromisoformat(row["started"])
    return (dt.datetime.now(dt.timezone.utc) - began).total_seconds() > secs + GRACE


def state(row) -> dict:
    """Where a drill stands, so a reload resumes it rather than starting over."""
    cfg, served, answers = _cfg(row), _served(row), db.load_answers(row)
    current = served[-1] if served and served[-1]["id"] not in answers else None
    return {
        "id": row["id"], "mode": row["kind"], "topics": cfg.get("topics", []),
        "total": cfg.get("total"), "timed": cfg.get("timed", False),
        "seconds": seconds_of(cfg),
        "started": row["started"], "finished": row["finished"],
        "answered": len(answers),
        "marks": [scoring.is_correct(q, answers[q["id"]]) for q in served if q["id"] in answers],
        "question": public(current) if current else None,
    }


def next_question(row) -> dict:
    cfg, served, answers = _cfg(row), _served(row), db.load_answers(row)
    if served and served[-1]["id"] not in answers:
        return {"question": public(served[-1]), "index": len(served), "total": cfg.get("total")}
    if cfg.get("total") is not None and len(answers) >= cfg["total"]:
        return {"done": True, "total": cfg["total"]}
    q = _serve(row, cfg, served)
    _save(row["id"], cfg, served)
    if q is None:
        return {"done": True, "exhausted": True, "total": cfg.get("total")}
    return {"question": public(q), "index": len(served), "total": cfg.get("total")}


def _answers(sid: str) -> dict:
    return json.loads(db.one("SELECT answers FROM sessions WHERE id=?", sid)["answers"] or "{}")


def answer(row, qid: str, given, ms: int | None) -> dict:
    cfg, served = _cfg(row), _served(row)
    q = next((x for x in served if x["id"] == qid), None)
    if q is None:
        raise KeyError(qid)
    if overtime(row, cfg):
        raise Closed("time is up")
    # Claimed in one statement before anything is filed, so the same answer
    # sent twice at once -- a double tap, a retried request -- files once.
    if not db.set_answer(row["id"], qid, given, only_new=True):
        answers = _answers(row["id"])
        if qid not in answers:
            raise Closed("this set is finished")
        given = answers[qid]                          # a double tap, not a second try
        ok = scoring.is_correct(q, given)
        reason = (q.get("reasons") or [""] * 4)[given] if not ok and isinstance(given, int) and 0 <= given < 4 else ""
        return _feedback(q, given, ok, reason, [], [], None, None, cfg, answers, served)

    before = progress.topic_mastery(row["learner"], q["topic"])
    filed = progress.record(row["learner"], row["id"], q, given, ms)
    after = progress.topic_mastery(row["learner"], q["topic"])
    answers = _answers(row["id"])

    # one repair per question: a missed repair stays an open mistake for later,
    # or a student who keeps missing would never reach the end of the set
    if not filed["correct"] and not cfg.get("fixed") and not q.get("repair"):
        cfg["repair"] = q["key"]
        if cfg.get("total") is not None:
            cfg["total"] += 1                        # the set grows to fit the repair
    _save(row["id"], cfg, served)
    return _feedback(q, given, filed["correct"], filed["reason"], filed["opened"],
                     filed["closed"], before, after, cfg, answers, served)


def _feedback(q, given, ok, reason, opened, closed, before, after, cfg, answers, served) -> dict:
    run = 0
    for x in reversed([x for x in served if x["id"] in answers]):
        if not scoring.is_correct(x, answers[x["id"]]):
            break
        run += 1
    mistake = reason[:1].upper() + reason[1:] if reason else None
    return {
        "correct": ok, "given": given,
        "answer": q["answer"],
        "answer_index": "ABCD".index(q["answer"]) if q["type"] == "mcq" else None,
        "mistake": mistake,
        "rationale": q["rationale"],
        "skill": q.get("skill"),
        "opened": opened, "closed": closed,
        "mastery": None if before is None else {"topic": q["topic"], "before": before, "after": after},
        "total": cfg.get("total"), "answered": len(answers), "streak": run,
    }


def finish(row) -> dict:
    cfg = _cfg(row)
    learner = row["learner"]
    # one attempt per question, the first, whatever else reached the table
    got = db.rows("SELECT topic, correct, reason, template, ms FROM attempts WHERE id IN"
                  " (SELECT MIN(id) FROM attempts WHERE session=? GROUP BY qid) ORDER BY id", row["id"])
    names = progress.topics()
    per: dict[str, dict] = {}
    for a in got:
        d = per.setdefault(a["topic"], {"right": 0, "asked": 0})
        d["asked"] += 1
        d["right"] += a["correct"]
    topics_out = [
        {"topic": t, "name": names[t].name, "domain": names[t].domain, **v,
         "before": cfg.get("before", {}).get(t, 0.0),
         "after": progress.topic_mastery(learner, t)}
        for t, v in per.items()
    ]
    still = {(t["template"], t["label"]) for t in progress.open_traps(learner)}
    opened = []
    for t in db.rows("SELECT template, label, topic FROM traps WHERE learner=? AND opened>=?",
                     learner, row["started"]):
        if (t["template"], t["label"]) in still:
            opened.append({"topic": t["topic"], "label": t["label"]})
    closed = [{"topic": t["topic"], "label": t["label"]}
              for t in db.rows("SELECT label, topic FROM traps WHERE learner=? AND closed>=?",
                               learner, row["started"])]
    result = {
        "mode": row["kind"], "asked": len(got), "right": sum(a["correct"] for a in got),
        "topics": topics_out, "opened": opened, "closed": closed,
        "ms": sum(a["ms"] or 0 for a in got),
    }
    if not row["finished"]:
        db.run("UPDATE sessions SET finished=?, result=? WHERE id=? AND finished IS NULL",
               progress.now(), json.dumps(result), row["id"])
    return result
