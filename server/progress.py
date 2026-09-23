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
import json
import math
import re
from functools import lru_cache
from collections import Counter, defaultdict

from . import db, practice, scoring

DIFF_W = {"easy": 1.0, "medium": 2.0, "hard": 3.0}
DECAY = 0.93        # each answer further back counts this much less
WINDOW = 40         # answers per topic that still count
EVIDENCE = 10.0     # answers for the bar to trust about two thirds of what it sees
FOCUS_LIFT = 40.0   # what the plan's Focus adds to a domain's topics, and Strong takes off
OWED = 2            # clean answers on the template that close a mistake
STRONG = 0.8        # past this a topic is kept warm rather than worked on
MS_CAP = 10 * 60 * 1000     # an answer left open over lunch is not ten hours of study

# The published section weights, so a new student meets the big domains first.
BLUEPRINT = {"Algebra": 0.35, "Advanced Math": 0.35,
             "Problem-Solving and Data Analysis": 0.15, "Geometry and Trigonometry": 0.15}
DOMAINS = tuple(BLUEPRINT)

_NUMBER = re.compile(r"[-−]?\d[\d.,/]*")


def norm(reason: str) -> str:
    """Fold numeric variants of a misconception into one trap.

    Some distractors in one item already share a norm (for example degree vs
    radian and the two reversed percentages); latest concrete wording wins.
    """
    return " ".join(_NUMBER.sub("#", (reason or "").lower()).split())


assert norm("Container 10% of 50") == norm("Container 50% of 10")
assert norm("divided by 360/90 instead of 180") == norm("divided by 90/360 instead of 180")
assert norm("near-miss arithmetic slip") == "near-miss arithmetic slip"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def topics() -> dict:
    return practice.catalogue()["topics"]


# ------------------------------------------------------------------ mastery

def mastery_of(answers: list[tuple[str, float]]) -> float:
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
    got = db.rows("SELECT difficulty, correct, guess FROM attempts WHERE learner=? AND topic=?"
                  " AND repeat=0 AND disputed=0 AND void IS NULL"
                  " ORDER BY id DESC LIMIT ?", learner, topic, WINDOW)
    return mastery_of([(r["difficulty"], r["correct"] * (0.5 if r["guess"] else 1)) for r in got])


def open_traps(learner: str, topic: str | None = None) -> list[dict]:
    sql = ("SELECT id, template, norm, reason, label, topic, hits, owed, opened, last,"
           " relapses, seed, session, due, checks, source, note, origin FROM traps"
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
    for r in db.rows("SELECT topic, difficulty, correct, guess, at FROM attempts"
                     " WHERE learner=? AND repeat=0 AND disputed=0 AND void IS NULL ORDER BY id DESC", learner):
        count[r["topic"]] += 1
        last.setdefault(r["topic"], r["at"])
    for r in db.rows("SELECT topic, difficulty, correct, guess FROM attempts WHERE learner=?"
                     " AND repeat=0 AND disputed=0 AND void IS NULL ORDER BY id DESC", learner):
        if len(recent[r["topic"]]) < WINDOW:
            recent[r["topic"]].append((r["difficulty"], r["correct"] * (0.5 if r["guess"] else 1)))
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
           when: str | None = None, once: bool = False, flagged: bool = False,
           guess: bool = False, sms: int | None = None, void: str | None = None) -> dict | None:
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
    elif not ok and q["type"] == "spr":
        for item in q.get("spr_reasons") or []:
            if isinstance(item, (list, tuple)) and len(item) >= 2 and scoring.grid_equal(str(given), str(item[1])):
                reason = str(item[0])
                break
    repeat = bool(db.one("SELECT 1 FROM attempts WHERE learner=? AND template=? AND seed=?",
                         learner, q["key"], q["seed"]))
    normalized = "~unsure" if ok and flagged else (norm(reason) if not ok else None)
    values = (learner, session, q["id"], q["key"], q["seed"], q["topic"], q["difficulty"],
              q["type"], int(ok), reason or None, normalized,
              None if given is None else str(given), None if ms is None else max(0,int(ms)),
              when, int(repeat), int(bool(q.get("repair"))), int(flagged), int(guess),
              sms, void, str(q.get("stem") or "")[:200])
    insert = ("INSERT INTO attempts (learner, session, qid, template, seed, topic, difficulty,"
              " fmt, correct, reason, norm, given, ms, at, repeat, repair, flagged, guess, sms, void, stem) ")
    if once:
        if not db.run(insert + "SELECT " + ",".join("?" for _ in values) + " WHERE NOT EXISTS"
                      " (SELECT 1 FROM attempts WHERE learner=? AND session=?)",
                      *values, learner, session).rowcount:
            return None
    else:
        db.run(insert + "VALUES (" + ",".join("?" for _ in values) + ")", *values)

    opened: list[str] = []
    closed: list[str] = []
    clean = ok and not (repeat or flagged or guess or void)
    if clean:
        for t in db.rows("SELECT id, label, owed, closed, due, checks FROM traps"
                         " WHERE learner=? AND template=? AND (closed IS NULL OR due IS NOT NULL)", learner, q["key"]):
            if t["closed"] is not None:
                checks = min(3, t["checks"] + 1)
                due = (dt.date.fromisoformat(when[:10]) + dt.timedelta(days=(10,30)[checks-1])).isoformat() if checks < 3 else None
                db.run("UPDATE traps SET checks=?,due=?,last=? WHERE id=?", checks,due,when,t["id"])
                continue
            left = t["owed"] - 1
            if left <= 0:
                due = (dt.date.fromisoformat(when[:10]) + dt.timedelta(days=3)).isoformat()
                db.run("UPDATE traps SET owed=0,closed=?,closed_how='fixed',last=?,due=?,checks=0 WHERE id=?",
                       when,when,due,t["id"])
                closed.append(t["label"])
            else:
                db.run("UPDATE traps SET owed=?,last=? WHERE id=?", left,when,t["id"])
    if not ok or (ok and flagged):
        if ok:
            reason = "~unsure"
        # a grid-in names no mistake, so it is filed under what it was testing
        label = ("Unsure" if ok else reason) or practice.skill_of(q) or q.get("topic_name") or q["topic"]
        label = label[:1].upper() + label[1:]
        key = "~unsure" if ok else norm(reason)
        t = db.one("SELECT id,closed,closed_how,relapses FROM traps WHERE learner=? AND template=? AND norm=?",
                   learner,q["key"],key)
        owed = 1 if ok else OWED
        if t:
            db.run("UPDATE traps SET hits=hits+1,owed=?,last=?,closed=NULL,closed_how=NULL,"
                   " label=?,reason=?,seed=?,session=?,due=NULL,checks=0,relapses=? WHERE id=?",
                   owed,when,label,reason,q["seed"],session,
                   t["relapses"] + int(t["closed"] is not None and t["closed_how"] == "fixed"),t["id"])
        else:
            db.run("INSERT INTO traps (learner,template,norm,reason,label,topic,hits,owed,opened,last,seed,session)"
                   " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                   learner,q["key"],key,reason,label,q["topic"],1,owed,when,when,q["seed"],session)
        opened.append(label)
    return {"correct": ok, "reason": reason, "opened": opened, "closed": closed,
            "repeat": repeat, "repair": bool(q.get("repair")), "flagged": flagged}


def record_paper(learner: str, session: str, questions: list[dict], answers: dict,
                 qstate: dict | None = None, flagged: set[str] | None = None) -> int:
    """File a whole test at once, answered questions only: a blank on a timed
    paper says more about the clock than about the topic."""
    when = now()
    if qstate is None:
        row = db.one("SELECT qstate FROM sessions WHERE id=?", session)
        qstate = json.loads(row["qstate"] or "{}") if row else {}
    if flagged is None:
        flagged = {r["qid"] for r in db.rows("SELECT f.qid FROM flags AS f JOIN sessions AS s ON s.id=f.session"
                                              " WHERE f.learner=? AND f.session=? AND (s.finished IS NULL OR f.at<=s.finished)",
                                              learner,session)}
    n = 0
    for q in questions:
        given = answers.get(q["id"])
        if given is None or given == "" or "key" not in q:
            continue
        record(learner, session, q, given, (qstate.get(q["id"]) or {}).get("ms"), when,
               flagged=q["id"] in flagged)
        n += 1
    return n


def log_mistake(learner: str, template: str, topic: str, reason: str = "",
                source: str = "outside", note: str | None = None,
                origin: str | None = None, when: str | None = None) -> int:
    """Put an outside mistake in the same repair queue as answered questions."""
    when = when or now()
    reason = (reason or "")[:80]
    label = reason or topic
    normalized = norm(reason)
    t = db.one("SELECT id,closed,closed_how,relapses FROM traps WHERE learner=? AND template=? AND norm=?",
               learner,template,normalized)
    if t:
        db.run("UPDATE traps SET hits=hits+1,owed=2,last=?,closed=NULL,closed_how=NULL,"
               " relapses=?,reason=?,label=?,source=?,note=?,origin=?,due=NULL,checks=0 WHERE id=?",
               when,t["relapses"]+int(t["closed"] is not None and t["closed_how"] == "fixed"),
               reason,label,source,note,origin,t["id"])
        return t["id"]
    return db.run("INSERT INTO traps(learner,template,norm,reason,label,topic,hits,owed,opened,last,source,note,origin)"
                  " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", learner,template,normalized,reason,label,topic,1,2,
                  when,when,source,note,origin).lastrowid


@lru_cache(maxsize=1)
def related() -> dict[str, tuple[str, ...]]:
    """Templates sharing a concrete named misconception across sampled seeds."""
    from satbank.registry import generate
    index: dict[str,set[str]] = defaultdict(set)
    for template in practice.catalogue()["by_topic"].values():
        for key in template:
            for seed in range(12):
                try:
                    for reason in generate(key, seed).reasons:
                        n = norm(reason)
                        if n and n != "near-miss arithmetic slip":
                            index[n].add(key)
                except Exception:
                    continue
    return {n: tuple(sorted(keys)) for n,keys in index.items() if len(keys)>1}


def carry(frm: str, to: str) -> int:
    """Move everything one code has done onto another, as one change.

    A student who opens a second device and types in the first one's code
    must not strand what the second device had already done. A mistake open
    under both codes stays one mistake: its hits add up and it stays open
    until both would have closed it. The target's profile keeps what it has
    set and takes the rest from the other code.
    """
    if frm == to:
        return 0
    c = db.conn()
    with c:
        n = sum(c.execute(f"SELECT COUNT(*) FROM {table} WHERE learner=?", (frm,)).fetchone()[0]
                for table in ("attempts","word_reviews","my_words"))
        for table in ("attempts", "sessions", "tries", "outside_scores", "plans", "posts",
                      "word_reviews", "my_words", "reports", "links"):
            c.execute(f"UPDATE {table} SET learner=? WHERE learner=?", (to, frm))
        c.execute("UPDATE users SET learner=? WHERE learner=?", (to, frm))
        c.execute("UPDATE sets SET owner=? WHERE owner=?", (to, frm))
        c.execute("UPDATE contests SET owner=? WHERE owner=?", (to, frm))
        c.execute("UPDATE OR IGNORE name_reports SET target=? WHERE target=?", (to, frm))
        c.execute("UPDATE OR IGNORE name_reports SET reporter=? WHERE reporter=?", (to, frm))
        c.execute("DELETE FROM name_reports WHERE target=? OR reporter=?", (frm, frm))
        for table in ("practice_seen", "saved", "flags", "notes", "earned", "post_votes", "contest_members"):
            c.execute(f"UPDATE OR IGNORE {table} SET learner=? WHERE learner=?", (to, frm))
            c.execute(f"DELETE FROM {table} WHERE learner=?", (frm,))
        for s in c.execute("SELECT * FROM word_state WHERE learner=?", (frm,)).fetchall():
            t = c.execute("SELECT * FROM word_state WHERE learner=? AND word=?", (to, s["word"])).fetchone()
            if t:
                c.execute("UPDATE word_state SET box=?,reps=?,right=?,wrong=?,lapses=?,saved=?,due=?,first=?,last=? WHERE learner=? AND word=?",
                          (max(t["box"], s["box"]), *(t[k]+s[k] for k in ("reps", "right", "wrong", "lapses")),
                           max(t["saved"], s["saved"]), min(x for x in (t["due"],s["due"]) if x) if t["due"] or s["due"] else None,
                           min(x for x in (t["first"],s["first"]) if x) if t["first"] or s["first"] else None,
                           max(x for x in (t["last"],s["last"]) if x) if t["last"] or s["last"] else None,
                           to, s["word"]))
            else:
                c.execute("UPDATE word_state SET learner=? WHERE learner=? AND word=?", (to, frm, s["word"]))
        c.execute("DELETE FROM word_state WHERE learner=?", (frm,))
        for s in c.execute("SELECT * FROM traps WHERE learner=?", (frm,)).fetchall():
            t = c.execute("SELECT * FROM traps WHERE learner=? AND template=? AND norm=?", (to,s["template"],s["norm"])).fetchone()
            if t:
                recent = s if s["last"] >= t["last"] else t
                c.execute("UPDATE traps SET hits=?,owed=?,opened=?,last=?,closed=?,reason=?,label=?,topic=?,seed=?,session=?,relapses=?,checks=?,due=? WHERE id=?",
                          (t["hits"]+s["hits"],max(t["owed"],s["owed"]),min(t["opened"],s["opened"]),
                           max(t["last"],s["last"]),None if t["closed"] is None or s["closed"] is None else max(t["closed"],s["closed"]),
                           *(recent[k] for k in ("reason","label","topic","seed","session")),t["relapses"]+s["relapses"],
                           max(t["checks"],s["checks"]),recent["due"],t["id"]))
                c.execute("DELETE FROM traps WHERE id=?", (s["id"],))
            else:
                c.execute("UPDATE traps SET learner=? WHERE id=?", (to,s["id"]))
        c.execute("DELETE FROM pairs WHERE learner=? OR req_learner=?", (frm,frm))
        s = c.execute("SELECT * FROM learners WHERE id=?", (frm,)).fetchone()
        t = c.execute("SELECT * FROM learners WHERE id=?", (to,)).fetchone()
        if s and t:
            cols = ("name","exam_date","target","minutes","days","current","tests","focus","avatar","board","country","rw_now","rw_target","plan","plan_draft")
            for key in cols:
                if t[key] is None and s[key] is not None:
                    c.execute(f"UPDATE learners SET {key}=? WHERE id=?", (s[key],to))
            sp, tp = json.loads(s["prefs"] or "{}"), json.loads(t["prefs"] or "{}")
            c.execute("UPDATE learners SET prefs=?,ach_seen=MAX(COALESCE(ach_seen,''),?),updated=? WHERE id=?",
                      (json.dumps({**sp,**tp}),s["ach_seen"] or "",now(),to))
        elif s:
            c.execute("UPDATE learners SET id=? WHERE id=?", (to,frm))
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
    due = {r["topic"] for r in db.rows("SELECT topic FROM traps WHERE learner=? AND closed_how='fixed'"
                                      " AND closed IS NOT NULL AND due<=?", learner,today.isoformat())}
    from . import prefs
    keep_warm = prefs.get(learner)["keep_warm"]
    # the plan's own say: a domain on focus comes up more, a strong one less
    row = db.one("SELECT focus FROM learners WHERE id=?", learner)
    focus = json.loads(row["focus"]) if row and row["focus"] else {}
    scored = []
    for slug, t in b.items():
        s = 100.0 * min(len(t["traps"]), 3)
        if slug in due:
            s += 70.0
        s += {"focus": FOCUS_LIFT, "strong": -FOCUS_LIFT}.get(focus.get(t["domain"]), 0.0)
        if not t["answered"]:
            s += 60.0 * BLUEPRINT.get(t["domain"], 0.15) / 0.35
        else:
            s += (1.0 - t["mastery"]) * 50.0
            since = _days_since(t["last"], today)
            if keep_warm and t["mastery"] >= STRONG and since >= 10:
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
    elif any(p in due for p in picks):
        why = "check"
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


def days(learner: str, tz: int = 0, weeks: int = 2) -> dict:
    """One local-day ledger for questions, words, finished sittings and plan work."""
    weeks = max(1, min(53, int(weeks)))
    per: dict[dt.date, dict] = defaultdict(lambda: {"questions": 0, "right": 0, "words": 0, "ms": 0})
    for r in db.rows("SELECT at,ms,correct,disputed FROM attempts WHERE learner=?", learner):
        d = per[_local_day(r["at"], tz)]
        d["questions"] += 1
        d["right"] += int(bool(r["correct"]) and not r["disputed"])
        d["ms"] += min(max(r["ms"] or 0, 0), MS_CAP)
    for r in db.rows("SELECT at,ms FROM word_reviews WHERE learner=? AND COALESCE(kind,'')!='lookup'", learner):
        d = per[_local_day(r["at"], tz)]
        d["words"] += 1
        d["ms"] += min(max(r["ms"] or 0, 0), 60_000)
    for r in db.rows("SELECT id,kind,started,finished,cfg FROM sessions WHERE learner=?"
                     " AND finished IS NOT NULL AND kind IN ('mock','module','diagnostic','custom')", learner):
        timed = db.one("SELECT 1 FROM attempts WHERE learner=? AND session=? AND ms IS NOT NULL LIMIT 1", learner,r["id"])
        if timed:
            continue
        elapsed = max(0, int((dt.datetime.fromisoformat(r["finished"]) - dt.datetime.fromisoformat(r["started"])).total_seconds()))
        cfg = json.loads(r["cfg"] or "{}")
        cap = 5400 if cfg.get("timing") == "untimed" else (4260 if r["kind"] == "mock" else 2160)
        per[_local_day(r["finished"], tz)]["ms"] += min(elapsed, cap) * 1000
        per[_local_day(r["finished"], tz)]["finished"] = True
    plan = db.one("SELECT plan,days,exam_date FROM learners WHERE id=?", learner)
    if plan and plan["plan"]:
        for r in db.rows("SELECT m.day,t.minutes FROM plan_marks AS m JOIN plan_tasks AS t ON t.id=m.task"
                         " WHERE t.plan=? AND m.status='done'", plan["plan"]):
            try:
                per[dt.date.fromisoformat(r["day"])]["ms"] += max(0,r["minutes"] or 0)*60_000
            except ValueError:
                pass
    today = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date()

    def rest(d: dt.date) -> bool:
        if not plan or not plan["plan"]:
            return False
        if plan["exam_date"] and d == dt.date.fromisoformat(plan["exam_date"]) - dt.timedelta(days=1):
            return True
        override = db.one("SELECT off FROM plan_overrides WHERE plan=? AND day=?", plan["plan"],d.isoformat())
        if override and override["off"]:
            return True
        frozen = db.one("SELECT kind FROM plan_days WHERE plan=? AND day=?", plan["plan"],d.isoformat())
        if frozen:
            return frozen["kind"] in ("rest","off","eve")
        return bool(plan["days"] and len(plan["days"]) == 7 and plan["days"][d.weekday()] == "0")

    def active(d: dt.date) -> bool:
        v = per.get(d, {})
        return bool(v.get("questions") or v.get("words",0) >= 10 or v.get("finished"))

    streak = 0
    d = today
    if not active(d) and not rest(d):
        d -= dt.timedelta(days=1)
    floor = min(per, default=today) - dt.timedelta(days=7)
    while d >= floor:
        if active(d):
            streak += 1
        elif not rest(d):
            break
        d -= dt.timedelta(days=1)
    best = run = 0
    for i in range(max(0,(today-floor).days)+1):
        d = floor + dt.timedelta(days=i)
        if active(d):
            run += 1
            best = max(best,run)
        elif not rest(d):
            run = 0

    def line(d: dt.date) -> dict:
        v = per.get(d,{})
        return {"day":d.isoformat(),"questions":v.get("questions",0),"right":v.get("right",0),
                "words":v.get("words",0),"minutes":round(v.get("ms",0)/60_000),"rest":rest(d)}

    recent = [line(today-dt.timedelta(days=back)) for back in range(13,-1,-1)]
    calendar = [line(today-dt.timedelta(days=back)) for back in range(weeks*7-1,-1,-1)]
    own_words = db.one("SELECT COUNT(*) AS n FROM my_words WHERE learner=?", learner)["n"]
    return {"today":today.isoformat(),"streak":streak,"best_streak":best,
            "active_days":sum(active(d) for d in per),"minutes_total":round(sum(v["ms"] for v in per.values())/60_000),
            "recent":recent,"days":calendar,
            "total":sum(v["questions"]+v["words"] for v in per.values())+own_words}
