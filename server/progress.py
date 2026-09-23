"""What a learner knows, what keeps catching them, and what to do next.

All of it is read off `attempts` and `traps`, so it can be recomputed at any
time, and a change to the rules below changes every student's map at once
instead of leaving a stored number behind.

Mastery is how right the recent answers in a topic are -- a hard question
counting three times an easy one, each answer a little less than the one after
it -- times how much there is to go on, which grows with the number of answers
and never quite reaches one. So one lucky answer is a sliver of the bar, not a
third of it. It is a practice gauge, not a score, which is why the map draws it
as a bar and never prints it as a number.

A mistake is the misconception the picked option names, filed against the
template it came from. It stays open until the student answers that template
cleanly twice -- which is what a repair question, the same template on a fresh
seed, exists to give them the chance to do.
"""

from __future__ import annotations

import datetime as dt
import math
from collections import Counter, defaultdict

from . import db, practice, scoring

DIFF_W = {"easy": 1.0, "medium": 2.0, "hard": 3.0}
DECAY = 0.93        # each answer further back counts this much less
WINDOW = 40         # answers per topic that still count
EVIDENCE = 10.0     # answers for the bar to trust about two thirds of what it sees
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
    """answers: newest first, as (difficulty, correct).

    Weighted accuracy times 1 - e^(-n/10): one answer, however right, is a
    tenth of the way; ten are about two thirds; thirty are nearly all of it.
    (Dividing by the weights plus a small prior made one answer a third of
    the bar, and kept a perfect record from ever passing 0.87.)
    """
    recent = answers[:WINDOW]
    num = den = 0.0
    for k, (diff, ok) in enumerate(recent):
        w = DIFF_W.get(diff, 2.0) * (DECAY ** k)
        den += w
        if ok:
            num += w
    if not den:
        return 0.0
    return round(num / den * (1 - math.exp(-len(recent) / EVIDENCE)), 3)


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
           when: str | None = None, once: bool = False) -> dict | None:
    """File one answer, and say what it did to the learner's open mistakes.

    once: the learner may have one answer in this session at all (the question
    of the day). The check is inside the insert, so two at once file one, and
    None means this one was not filed.
    """
    when = when or now()
    ok = scoring.is_correct(q, given)
    reason = ""
    if not ok and q["type"] == "mcq" and isinstance(given, int) and 0 <= given < 4:
        reasons = q.get("reasons") or []
        reason = reasons[given] if given < len(reasons) else ""
    values = (learner, session, q["id"], q["key"], q["seed"], q["topic"], q["difficulty"],
              q["type"], int(ok), reason or None, None if given is None else str(given),
              None if ms is None else int(ms), when)
    insert = ("INSERT INTO attempts (learner, session, qid, template, seed, topic, difficulty,"
              " fmt, correct, reason, given, ms, at) ")
    if once:
        if not db.run(insert + "SELECT ?,?,?,?,?,?,?,?,?,?,?,?,? WHERE NOT EXISTS"
                      " (SELECT 1 FROM attempts WHERE learner=? AND session=?)",
                      *values, learner, session).rowcount:
            return None
    else:
        db.run(insert + "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", *values)

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
        label = reason or practice.skill_of(q) or q.get("topic_name") or q["topic"]
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


def carry(frm: str, to: str) -> int:
    """Move everything one code has done onto another, as one change.

    A student who opens a second device and types in the first one's code
    must not strand what the second device had already done. A mistake open
    under both codes stays one mistake: its hits add up and it stays open
    until both would have closed it. The target's profile keeps what it has
    set and takes the rest from the other code.
    """
    c = db.conn()
    with c:
        n = c.execute("SELECT COUNT(*) FROM attempts WHERE learner=?", (frm,)).fetchone()[0]
        c.execute("UPDATE attempts SET learner=? WHERE learner=?", (to, frm))
        # ponytail: two sittings of one day's challenge can end up under one code; the board shows both
        c.execute("UPDATE sessions SET learner=? WHERE learner=?", (to, frm))
        c.execute("UPDATE traps AS t SET hits = t.hits + s.hits, owed = MAX(t.owed, s.owed),"
                  " last = MAX(t.last, s.last),"
                  " closed = CASE WHEN t.closed IS NULL OR s.closed IS NULL THEN NULL"
                  "          ELSE MAX(t.closed, s.closed) END"
                  " FROM traps AS s WHERE t.learner=? AND s.learner=?"
                  " AND s.template = t.template AND s.reason = t.reason", (to, frm))
        c.execute("UPDATE learners AS t SET"
                  " name = COALESCE(t.name, s.name), exam_date = COALESCE(t.exam_date, s.exam_date),"
                  " target = COALESCE(t.target, s.target), minutes = COALESCE(t.minutes, s.minutes),"
                  " days = COALESCE(t.days, s.days), updated = ?"
                  " FROM learners AS s WHERE t.id=? AND s.id=?", (now(), to, frm))
        for table in ("practice_seen", "saved", "traps"):
            c.execute(f"UPDATE OR IGNORE {table} SET learner=? WHERE learner=?", (to, frm))
            c.execute(f"DELETE FROM {table} WHERE learner=?", (frm,))
        c.execute("UPDATE OR IGNORE learners SET id=? WHERE id=?", (to, frm))
        c.execute("DELETE FROM learners WHERE id=?", (frm,))
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

    # The whole ranking dealt into sets of k, at most two from any one domain
    # so a session is never one chapter. The first set is today's; a plan
    # gives the rest to its coming practice days, in order.
    ahead: list[list[str]] = []
    left = [slug for _, slug in scored]
    while left:
        cut: list[str] = []
        per_domain: Counter = Counter()
        for slug in left:
            if per_domain[b[slug]["domain"]] < 2:
                cut.append(slug)
                per_domain[b[slug]["domain"]] += 1
                if len(cut) == k:
                    break
        left = [x for x in left if x not in cut]
        ahead.append(cut)
    picks = ahead[0] if ahead else []

    if any(b[p]["traps"] for p in picks):
        why = "mistakes"
    elif not any(b[p]["answered"] for p in picks):
        why = "new"
    elif all(b[p]["mastery"] >= STRONG for p in picks):
        why = "review"
    else:
        why = "weak"
    return {"topics": picks, "ahead": ahead, "count": count, "why": why,
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
