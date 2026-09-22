"""What a learner knows, what keeps catching them, and what to do next.

All of it is read off `attempts` and `traps`, so it can be recomputed at any
time, and a change to the rules below changes every student's map at once
instead of leaving a stored number behind.

Mastery is a weighted share of recent answers in a topic. A hard question
counts three times an easy one, each answer counts a little less than the one
after it, and a prior of a few unanswered questions sits in the denominator so
one lucky answer is not a full bar. It is a practice gauge, not a score, which
is why the map draws it as a bar and never prints it as a number.

A mistake is the misconception the picked option names, filed against the
template it came from. It stays open until the student answers that template
cleanly twice -- which is what a repair question, the same template on a fresh
seed, exists to give them the chance to do.
"""

from __future__ import annotations

import datetime as dt
from collections import Counter, defaultdict

from . import db, practice, scoring

DIFF_W = {"easy": 1.0, "medium": 2.0, "hard": 3.0}
DECAY = 0.93        # each answer further back counts this much less
WINDOW = 40         # answers per topic that still count
PRIOR = 4.0         # two medium questions' worth of nothing, in the denominator
OWED = 2            # clean answers on the template that close a mistake
STRONG = 0.8        # past this a topic is kept warm rather than worked on
MS_CAP = 10 * 60 * 1000     # an answer left open over lunch is not ten hours of study

# The published section weights, so a new student meets the big domains first.
BLUEPRINT = {"Algebra": 0.35, "Advanced Math": 0.35,
             "Problem-Solving and Data Analysis": 0.15, "Geometry and Trigonometry": 0.15}
DOMAINS = tuple(BLUEPRINT)


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def topics() -> dict:
    return practice.catalogue()["topics"]


# ------------------------------------------------------------------ mastery

def mastery_of(answers: list[tuple[str, int]]) -> float:
    """answers: newest first, as (difficulty, correct)."""
    num = den = 0.0
    for k, (diff, ok) in enumerate(answers[:WINDOW]):
        w = DIFF_W.get(diff, 2.0) * (DECAY ** k)
        den += w
        if ok:
            num += w
    return round(num / (den + PRIOR), 3) if den else 0.0


def topic_mastery(learner: str, topic: str) -> float:
    got = db.rows("SELECT difficulty, correct FROM attempts WHERE learner=? AND topic=?"
                  " ORDER BY id DESC LIMIT ?", learner, topic, WINDOW)
    return mastery_of([(r["difficulty"], r["correct"]) for r in got])


def open_traps(learner: str, topic: str | None = None) -> list[dict]:
    sql = ("SELECT template, reason, label, topic, hits, owed, opened, last FROM traps"
           " WHERE learner=? AND closed IS NULL")
    args: list = [learner]
    if topic:
        sql += " AND topic=?"
        args.append(topic)
    return [dict(r) for r in db.rows(sql + " ORDER BY last DESC", *args)]


def board(learner: str) -> dict[str, dict]:
    """Every topic: its mastery, how much it has been answered, when last, and
    the mistakes still open in it."""
    recent: dict[str, list] = defaultdict(list)
    last: dict[str, str] = {}
    count: Counter = Counter()
    for r in db.rows("SELECT topic, difficulty, correct, at FROM attempts"
                     " WHERE learner=? ORDER BY id DESC", learner):
        count[r["topic"]] += 1
        if len(recent[r["topic"]]) < WINDOW:
            recent[r["topic"]].append((r["difficulty"], r["correct"]))
        last.setdefault(r["topic"], r["at"])
    traps: dict[str, list] = defaultdict(list)
    for t in open_traps(learner):
        traps[t["topic"]].append({"template": t["template"], "label": t["label"],
                                  "hits": t["hits"], "owed": t["owed"]})
    return {
        slug: {"topic": slug, "name": tp.name, "domain": tp.domain,
               "mastery": mastery_of(recent.get(slug, [])), "answered": count[slug],
               "last": last.get(slug), "traps": traps.get(slug, [])}
        for slug, tp in topics().items()
    }


# ------------------------------------------------------------------ filing

def record(learner: str, session: str | None, q: dict, given, ms: int | None = None,
           when: str | None = None) -> dict:
    """File one answer, and say what it did to the learner's open mistakes."""
    when = when or now()
    ok = scoring.is_correct(q, given)
    reason = ""
    if not ok and q["type"] == "mcq" and isinstance(given, int) and 0 <= given < 4:
        reasons = q.get("reasons") or []
        reason = reasons[given] if given < len(reasons) else ""
    db.run("INSERT INTO attempts (learner, session, qid, template, seed, topic, difficulty,"
           " fmt, correct, reason, given, ms, at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
           learner, session, q["id"], q["key"], q["seed"], q["topic"], q["difficulty"],
           q["type"], int(ok), reason or None, None if given is None else str(given),
           None if ms is None else int(ms), when)

    opened: list[str] = []
    closed: list[str] = []
    if ok:
        for t in db.rows("SELECT reason, label, owed FROM traps WHERE learner=? AND template=?"
                         " AND closed IS NULL", learner, q["key"]):
            left = t["owed"] - 1
            if left <= 0:
                db.run("UPDATE traps SET owed=0, closed=?, last=? WHERE learner=? AND template=?"
                       " AND reason=?", when, when, learner, q["key"], t["reason"])
                closed.append(t["label"])
            else:
                db.run("UPDATE traps SET owed=?, last=? WHERE learner=? AND template=? AND reason=?",
                       left, when, learner, q["key"], t["reason"])
    else:
        # a grid-in names no mistake, so it is filed under what it was testing
        label = reason or q.get("skill") or q.get("topic_name") or q["topic"]
        label = label[:1].upper() + label[1:]
        if db.one("SELECT 1 FROM traps WHERE learner=? AND template=? AND reason=?",
                  learner, q["key"], reason):
            db.run("UPDATE traps SET hits=hits+1, owed=?, last=?, closed=NULL, label=?"
                   " WHERE learner=? AND template=? AND reason=?",
                   OWED, when, label, learner, q["key"], reason)
        else:
            db.run("INSERT INTO traps (learner, template, reason, label, topic, hits, owed,"
                   " opened, last) VALUES (?,?,?,?,?,?,?,?,?)",
                   learner, q["key"], reason, label, q["topic"], 1, OWED, when, when)
        opened.append(label)
    return {"correct": ok, "reason": reason, "opened": opened, "closed": closed}


def record_paper(learner: str, session: str, questions: list[dict], answers: dict) -> int:
    """File a whole test at once, answered questions only: a blank on a timed
    paper says more about the clock than about the topic."""
    when = now()
    n = 0
    for q in questions:
        given = answers.get(q["id"])
        if given is None or given == "" or "key" not in q:
            continue
        record(learner, session, q, given, None, when)
        n += 1
    return n


# ------------------------------------------------------------------ the coach

def _days_since(at: str | None, today: dt.date) -> int:
    return (today - dt.date.fromisoformat(at[:10])).days if at else 10_000


def coach(learner: str, k: int = 3, count: int = 10) -> dict:
    """The next session: which topics, and why, in the order worth doing them.

    Open mistakes first, because a named misconception is the cheapest point
    there is. Then the weakest topics that have been worked on. A student with
    no history meets the big domains first. A strong topic left alone for ten
    days comes back once, so it stays strong.
    """
    b = board(learner)
    today = dt.datetime.now(dt.timezone.utc).date()
    scored = []
    for slug, t in b.items():
        s = 100.0 * min(len(t["traps"]), 3)
        if not t["answered"]:
            s += 60.0 * BLUEPRINT.get(t["domain"], 0.15) / 0.35
        else:
            s += (1.0 - t["mastery"]) * 50.0
            since = _days_since(t["last"], today)
            if t["mastery"] >= STRONG and since >= 10:
                s += 30.0
            if since == 0 and not t["traps"]:
                s -= 15.0          # already worked on today
        scored.append((s, slug))
    scored.sort(key=lambda p: (-p[0], p[1]))

    # at most two from any one domain, so a session is never one chapter
    picks: list[str] = []
    per_domain: Counter = Counter()
    for _, slug in scored:
        if per_domain[b[slug]["domain"]] >= 2:
            continue
        picks.append(slug)
        per_domain[b[slug]["domain"]] += 1
        if len(picks) == k:
            break

    if any(b[p]["traps"] for p in picks):
        why = "mistakes"
    elif not any(b[p]["answered"] for p in picks):
        why = "new"
    elif all(b[p]["mastery"] >= STRONG for p in picks):
        why = "review"
    else:
        why = "weak"
    return {"topics": picks, "count": count, "why": why,
            "mistakes": sum(len(b[p]["traps"]) for p in picks),
            "traps": {p: len(b[p]["traps"]) for p in picks}}


# ------------------------------------------------------------------ the days

def _local_day(at: str, tz: int) -> dt.date:
    """tz is JavaScript's getTimezoneOffset(): minutes behind UTC."""
    return (dt.datetime.fromisoformat(at) - dt.timedelta(minutes=tz)).date()


def days(learner: str, tz: int = 0) -> dict:
    """The streak, today, and the last fourteen days, in the learner's own time."""
    per: dict[dt.date, dict] = defaultdict(lambda: {"questions": 0, "right": 0, "ms": 0})
    for r in db.rows("SELECT at, ms, correct FROM attempts WHERE learner=?", learner):
        d = per[_local_day(r["at"], tz)]
        d["questions"] += 1
        d["right"] += r["correct"]
        d["ms"] += min(r["ms"] or 0, MS_CAP)
    today = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date()

    streak = 0
    day = today if per.get(today, {}).get("questions") else today - dt.timedelta(days=1)
    while per.get(day, {}).get("questions"):
        streak += 1
        day -= dt.timedelta(days=1)

    recent = []
    for back in range(13, -1, -1):
        d = today - dt.timedelta(days=back)
        v = per.get(d, {"questions": 0, "right": 0, "ms": 0})
        recent.append({"day": d.isoformat(), "questions": v["questions"], "right": v["right"],
                       "minutes": round(v["ms"] / 60000)})
    return {"today": today.isoformat(), "streak": streak, "recent": recent,
            "total": sum(v["questions"] for v in per.values())}
