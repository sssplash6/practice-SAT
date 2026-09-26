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
template it came from (R9). A named one -- an option's misconception, a named
grid-in value, an R&W trap id -- closes only on clean answers to questions that
offered it again (R45, G3): a right answer on an item without that trap on
offer counts for mastery and nothing else. An unnamed one (an unsure right, a
filler slip, a grid-in miss naming nothing) closes on any clean answer to its
template. After the fix come check-ins at 3, 10 and 30 days; the 10-day and
30-day ones are served on another template with the same trap when there is
one, and passing both there closes it as 'transfer'. A miss on a due check-in
reopens it as Relapsed. Every change is written to `trap_log` in the same
transaction, a fix with the points it was worth (V4).
"""

from __future__ import annotations

import datetime as dt
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from functools import lru_cache

from fastapi import HTTPException

from . import db, deps, practice, scoring

DIFF_W = {"easy": 1.0, "medium": 2.0, "hard": 3.0}
DECAY = 0.93        # each answer further back counts this much less
WINDOW = 40         # answers per topic that still count
EVIDENCE = 10.0     # answers for the bar to trust about two thirds of what it sees
FOCUS_LIFT = 40.0   # what the plan's Focus adds to a domain's topics, and Strong takes off
OWED = 2            # clean answers on the template that close a mistake
STRONG = 0.8        # past this a topic is kept warm rather than worked on
MS_CAP = 10 * 60 * 1000     # an answer left open over lunch is not ten hours of study
CHECK_DAYS = (3, 10, 30)    # R9: check-ins after a fix
FILLER = "near-miss arithmetic slip"
UNNAMED = ("", "~unsure", FILLER)
COUNTED = "repeat=0 AND disputed=0 AND void IS NULL"    # R8: what mastery and accuracy read

# The published section weights, so a new student meets the big domains first.
BLUEPRINT = {"Algebra": 0.35, "Advanced Math": 0.35,
             "Problem-Solving and Data Analysis": 0.15, "Geometry and Trigonometry": 0.15}
DOMAINS = tuple(BLUEPRINT)

# R47: a student-set cause wins; each maps to one of the causes below, and each
# cause to an R9 kind.
MISS_KINDS = {"trap": "trap", "fell": "trap", "slip": "slip", "rushed": "slip", "misread": "misread",
              "clock": "clock", "ran_long": "clock", "entry": "entry", "gap": "gap",
              "changed": "changed"}
CAUSES = ("changed", "clock", "entry", "trap", "slip", "misread", "gap")
KIND_OF_CAUSE = {"trap": "misconception", "slip": "slip", "misread": "slip", "clock": "slip",
                 "entry": "slip", "changed": "slip", "gap": "unsure"}

_NUMBER = re.compile(r"[-−]?\d[\d.,/]*")


def norm(reason: str) -> str:
    """Fold numeric variants of a misconception into one trap.

    Some distractors in one item already share a norm (for example degree vs
    radian and the two reversed percentages); latest concrete wording wins.
    """
    return " ".join(_NUMBER.sub("#", (reason or "").lower()).split())


def trap_kind(normalized: str, miss_kind: str | None = None, spr: bool = False) -> str:
    """R9's kinds (misconception, gridin, slip, unsure), with R47's student-set
    causes mapped on top."""
    cause = MISS_KINDS.get(miss_kind or "")
    if cause:
        return KIND_OF_CAUSE[cause]
    if normalized == "~unsure":
        return "unsure"
    if normalized == FILLER:
        return "slip"
    if normalized == "" or spr:
        return "gridin"
    return "misconception"


def named(normalized: str, miss_kind: str | None = None) -> bool:
    """A trap that can be on offer again: it closes only on items offering it."""
    return normalized not in UNNAMED and trap_kind(normalized, miss_kind) in ("misconception", "gridin")


def offered_of(q: dict) -> list[str]:
    """The norms of the named traps an item shows (P6): its MC options' reasons
    or its grid-in's named values, fillers and the key left out."""
    if (q.get("type") or q.get("fmt")) == "spr":
        reasons = [r[0] for r in q.get("spr_reasons") or () if isinstance(r, (list, tuple)) and r]
    else:
        reasons = q.get("reasons") or ()
    out: list[str] = []
    for r in reasons:
        n = norm(str(r))
        if n not in UNNAMED and n not in out:
            out.append(n)
    return out


def _self_check() -> None:
    """The folds norm() is trusted with, on the bank's own items (Review §3.9.5)."""
    from satbank.registry import generate
    ten = next(r for r in generate("context.container_percent", 3).reasons if "10%" in r and "twice" in r)
    fifty = next(r for r in generate("context.container_percent", 8).reasons if "50%" in r and "twice" in r)
    assert norm(ten) == norm(fifty), (ten, fifty)
    quarter = [r for r in generate("circles.coterminal", 0).reasons if "quarter turn" in r]
    assert len(quarter) == 2 and norm(quarter[0]) == norm(quarter[1]), quarter
    assert trap_kind(norm(FILLER)) == "slip" and not named(norm(FILLER))
    assert trap_kind("~unsure") == "unsure" and trap_kind("") == "gridin" and not named("")
    assert trap_kind(norm(ten)) == "misconception" and named(norm(ten))
    assert trap_kind(norm(ten), "misread") == "slip" and trap_kind(norm(ten), "gap") == "unsure"
    assert [interval_for(k) for k in (1, 2, 3, 4, 5)] == [2, 5, 12, 30, 30]


assert norm("divided by 360/90 instead of 180") == norm("divided by 90/360 instead of 180")


def init() -> None:
    _self_check()
    if "tz" not in {r["name"] for r in db.rows("PRAGMA table_info(traps)")}:
        db.run("ALTER TABLE traps ADD COLUMN tz INTEGER NOT NULL DEFAULT 0")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _learner_tz(learner: str, tz: int | None = None) -> int:
    """X-Tz is minutes behind UTC; remember it for answer paths without a tz argument."""
    box = deps.SWAP.get()
    raw = box.get("tz_header") if box else None
    if raw is not None:
        try:
            parsed = int(raw)
            if -840 <= parsed <= 720:
                tz = parsed
        except ValueError:
            pass
    if tz is None:
        saved = db.one("SELECT v FROM kv WHERE k=?", "learner-tz:" + learner)
        if saved:
            tz = int(saved["v"])
    if tz is None:
        plan = db.one("SELECT tz FROM plans WHERE learner=? AND archived IS NULL ORDER BY created DESC LIMIT 1", learner)
        tz = int(plan["tz"]) if plan and plan["tz"] is not None else 0
    if not -840 <= tz <= 720:
        tz = 0
    saved = db.one("SELECT v FROM kv WHERE k=?", "learner-tz:" + learner)
    if not saved or saved["v"] != str(tz):
        db.run("INSERT INTO kv(k,v) VALUES (?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v",
               "learner-tz:" + learner, str(tz))
    return tz


def _local_today(learner: str, tz: int | None = None) -> dt.date:
    return (_utc_now() - dt.timedelta(minutes=_learner_tz(learner, tz))).date()


def topics(subject: str = "math") -> dict:
    return {s: t for s, t in practice.catalogue()["topics"].items() if deps.subject_of(s) == subject}


@lru_cache(maxsize=8192)
def _item(template: str, seed: int):
    from satbank.registry import generate
    return generate(template, seed)


def _topic_of(template: str) -> str | None:
    from satbank.registry import topic_of
    try:
        return topic_of(template)
    except KeyError:
        return None


def _key_of(template: str, seed: int) -> str | None:
    try:
        return str(_item(template, seed).answer)
    except Exception:
        return None


# ------------------------------------------------------------------ mastery

def _counts(row) -> float:
    """R8: a right answer that was a guess or took a hint counts half."""
    return row["correct"] * (0.5 if row["guess"] or row["hints"] else 1)


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
            num += w * ok
    if not den:
        return 0.0
    return round(num / den * (1 - math.exp(-len(recent) / EVIDENCE)), 3)


def topic_mastery(learner: str, topic: str) -> float:
    got = db.rows(f"SELECT difficulty, correct, guess, hints FROM attempts WHERE learner=? AND topic=?"
                  f" AND {COUNTED} ORDER BY id DESC LIMIT ?", learner, topic, WINDOW)
    return mastery_of([(r["difficulty"], _counts(r)) for r in got])


def open_traps(learner: str, topic: str | None = None) -> list[dict]:
    sql = ("SELECT id, template, norm, reason, label, topic, hits, owed, opened, last,"
           " relapses, seed, session, due, checks, source, note, origin FROM traps"
           " WHERE learner=? AND closed IS NULL")
    args: list = [learner]
    if topic:
        sql += " AND topic=?"
        args.append(topic)
    return [dict(r) for r in db.rows(sql + " ORDER BY last DESC", *args)]


def board(learner: str, subject: str = "math") -> dict[str, dict]:
    """Every topic: its mastery, how much there is to go on (U5's evidence),
    the change over 14 days, the last five, whether it is fading, and the
    mistakes still open in it."""
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=14)).isoformat()
    today = _local_today(learner)
    recent: dict[str, list] = defaultdict(list)
    before: dict[str, list] = defaultdict(list)
    last: dict[str, str] = {}
    count: Counter = Counter()
    right: Counter = Counter()
    for r in db.rows(f"SELECT topic, difficulty, correct, guess, hints, at FROM attempts"
                     f" WHERE learner=? AND {COUNTED} ORDER BY id DESC", learner):
        count[r["topic"]] += 1
        right[r["topic"]] += r["correct"]
        last.setdefault(r["topic"], r["at"])
        if len(recent[r["topic"]]) < WINDOW:
            recent[r["topic"]].append((r["difficulty"], _counts(r)))
        if r["at"] < cutoff and len(before[r["topic"]]) < WINDOW:
            before[r["topic"]].append((r["difficulty"], _counts(r)))
    traps: dict[str, list] = defaultdict(list)
    for t in open_traps(learner):
        traps[t["topic"]].append({"id": t["id"], "template": t["template"], "label": t["label"],
                                  "hits": t["hits"], "owed": t["owed"]})
    out = {}
    for slug, tp in topics(subject).items():
        m = mastery_of(recent.get(slug, []))
        since = _days_since(last.get(slug), today)
        out[slug] = {
            "topic": slug, "name": tp.name, "domain": tp.domain, "subject": subject,
            "mastery": m, "answered": count[slug], "last": last.get(slug),
            "accuracy": round(right[slug] / count[slug], 3) if count[slug] else None,
            "evidence": len(recent.get(slug, [])),
            "trend14": round(m - mastery_of(before.get(slug, [])), 3) if slug in before else None,
            "last5": [1 if ok else 0 for _, ok in reversed(recent.get(slug, [])[:5])],
            "fading": m >= STRONG and since >= 10,
            "traps": traps.get(slug, [])}
    return out


# ------------------------------------------------------------------ filing

def _check_due(closed: str, checks: int, tz: int = 0) -> str | None:
    """R9: the next check-in after `checks` of 3 have passed."""
    if checks >= len(CHECK_DAYS):
        return None
    return (_local_day(closed, tz) + dt.timedelta(days=CHECK_DAYS[checks])).isoformat()


def log(learner: str, template: str, normalized: str, event: str, when: str,
        attempt: int | None = None, pts: int | None = None, undoes: int | None = None) -> None:
    """V8's trap log, written beside every traps change. pts: what a fix was
    worth when it closed (V4); undoes: the row a discard or restore undoes."""
    db.run("INSERT INTO trap_log(learner,template,norm,at,event,attempt,pts,undoes) VALUES (?,?,?,?,?,?,?,?)",
           learner, template, normalized, when, event, attempt, pts, undoes)


def _reason_of(q: dict, given) -> tuple[str, str | None]:
    """(the concrete misconception the answer names, its display name)."""
    if q["type"] == "mcq" and isinstance(given, int) and 0 <= given < 4:
        reasons = q.get("reasons") or []
        names = q.get("reason_names") or []
        reason = reasons[given] if given < len(reasons) else ""
        return reason or "", (names[given] if given < len(names) and names[given] else None)
    if q["type"] == "spr":
        for item in q.get("spr_reasons") or []:
            if isinstance(item, (list, tuple)) and len(item) >= 2 and scoring.grid_equal(str(given), str(item[1])):
                return str(item[0]), None
    return "", None


def _shows_key(session: str | None) -> bool:
    """Does the sitting show the key as soon as this answer is in? (V2)"""
    if not session:
        return False
    if session.startswith("qotd"):
        return True
    row = db.one("SELECT kind,cfg FROM sessions WHERE id=?", session)
    if not row or row["kind"] not in ("drill", "practice"):
        return False
    return json.loads(row["cfg"] or "{}").get("feedback", "instant") == "instant"


def _latest_miss_kind(learner: str, template: str, normalized: str) -> str | None:
    r = db.one("SELECT miss_kind FROM attempts WHERE learner=? AND template=? AND norm=? AND correct=0"
               " ORDER BY id DESC LIMIT 1", learner, template, normalized)
    return r["miss_kind"] if r else None


def _is_named(learner: str, t) -> bool:
    return named(t["norm"]) and named(t["norm"], _latest_miss_kind(learner, t["template"], t["norm"]))


def _transfers(t) -> int:
    """Check-ins this trap has passed on another template since its fix."""
    return db.one("SELECT COUNT(*) AS n FROM trap_log AS l JOIN attempts AS a ON a.id=l.attempt"
                  " WHERE l.learner=? AND l.template=? AND l.norm=? AND l.event='check_ok'"
                  " AND l.at>=? AND a.template!=?", t["learner"], t["template"], t["norm"],
                  t["closed"], t["template"])["n"]


def _pass_check(t, when: str, attempt: int | None, elsewhere: bool) -> dict:
    checks = min(3, t["checks"] + 1)
    how = t["closed_how"]
    log(t["learner"], t["template"], t["norm"], "check_ok", when, attempt)
    if checks == 3 and _transfers(t) >= 2:
        how = "transfer"
    db.run("UPDATE traps SET checks=?, due=?, last=?, closed_how=? WHERE id=?",
           checks, _check_due(t["closed"], checks, t["tz"]), when, how, t["id"])
    return {"id": t["id"], "label": t["label"], "checks": checks, "how": how, "elsewhere": elsewhere}


def _relapse(t, when: str, attempt: int | None) -> dict:
    db.run("UPDATE traps SET closed=NULL, closed_how=NULL, owed=?, relapses=relapses+1, due=NULL,"
           " checks=0, last=? WHERE id=?", 1 if t["norm"] == "~unsure" else OWED, when, t["id"])
    log(t["learner"], t["template"], t["norm"], "relapse", when, attempt)
    return {"id": t["id"], "label": t["label"]}


def record_trap(learner: str, q: dict, reason: str, when: str, session: str | None = None,
                attempt: int | None = None, unsure: bool = False, label: str | None = None) -> dict:
    """Open or refresh the trap a miss (or an unsure right) files under. Retry
    mode files a later try's trap hit through this too."""
    if db.is_sample(learner):
        raise ValueError("the sample report is read-only")
    key = "~unsure" if unsure else norm(reason)
    if not (unsure or label or reason):
        try:
            label = practice.skill_of(q)
        except Exception:               # a template the bank no longer makes
            label = None
    label = "Unsure" if unsure else (label or reason or q.get("topic_name") or q["topic"])
    label = label[:1].upper() + label[1:]
    stored_reason = "~unsure" if unsure else reason
    owed = 1 if unsure else OWED
    with db.atomic():
        t = db.one("SELECT id,closed,closed_how,relapses FROM traps WHERE learner=? AND template=? AND norm=?",
                   learner, q["key"], key)
        if t:
            relapse = t["closed"] is not None and t["closed_how"] in ("fixed", "transfer")
            db.run("UPDATE traps SET hits=hits+1,owed=?,last=?,closed=NULL,closed_how=NULL,"
                   " label=?,reason=?,seed=?,session=?,due=NULL,checks=0,relapses=? WHERE id=?",
                   owed, when, label, stored_reason, q["seed"], session,
                   t["relapses"] + int(relapse), t["id"])
            event = "relapse" if relapse else ("reopened" if t["closed"] else "miss")
            tid = t["id"]
        else:
            tid = db.run("INSERT INTO traps (learner,template,norm,reason,label,topic,hits,owed,opened,last,seed,session)"
                         " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", learner, q["key"], key, stored_reason, label,
                         q["topic"], 1, owed, when, when, q["seed"], session).lastrowid
            event = "open"
            log(learner, q["key"], key, "open", when, attempt)
        log(learner, q["key"], key, "miss" if event == "open" else event, when, attempt)
    return {"id": tid, "label": label, "event": event, "norm": key}


def record(learner: str, session: str | None, q: dict, given, ms: int | None = None,
           when: str | None = None, once: bool = False, flagged: bool = False,
           guess: bool = False, sms: int | None = None, void: str | None = None, *,
           conf: str | None = None, hints: int = 0, struck=None, cover: bool = False,
           calc: bool = False, word: str | None = None, revealed: bool | None = None,
           source: str | None = None, check: bool = False, miss_kind: str | None = None,
           placement: bool = False, tz: int | None = None) -> dict | None:
    """File one answer, and say what it did to the learner's open mistakes.

    once: the learner may have one answer in this session at all (the question
    of the day). The check is inside the insert, so two at once file one, and
    None means this one was not filed.

    R8: repeat is set here for every caller -- whenever access() already said
    'reveal' (an earlier attempt, the pair on a finished paper, a flag or save
    from one) or a worksheet's key was printed first. A clean answer is right,
    not a repeat, flagged, a guess, voided, hinted or unsure. conf 'guess' is a
    guess; 'auto' is unrated. check: a trap-test answer, a check-in whatever
    the date (X16). revealed: whether the key shows now (V2; inferred from the
    sitting when None).
    """
    if db.is_sample(learner):
        raise HTTPException(403, "the sample report is read-only")
    when = when or now()
    tz = _learner_tz(learner, tz)
    conf = conf if conf in ("sure", "unsure", "guess") else None
    guess = bool(guess) or conf == "guess"
    conf = "guess" if guess else conf
    hints = max(0, int(hints or 0))
    ok = scoring.is_correct(q, given)
    reason, reason_name = _reason_of(q, given) if not ok else ("", None)
    offered = offered_of(q)
    repeat = bool(db.one("SELECT 1 FROM attempts WHERE learner=? AND template=? AND seed=?",
                         learner, q["key"], q["seed"])) \
        or deps.access(learner, q["key"], q["seed"], exclude=session) == "reveal" \
        or deps.key_printed(session, when)
    unsure = ok and (flagged or conf == "unsure")
    normalized = "~unsure" if unsure else (norm(reason) if not ok else None)
    if revealed is None:
        revealed = _shows_key(session)
    struck_json = json.dumps(struck) if struck is not None else None
    values = (learner, session, q["id"], q["key"], q["seed"], q["topic"], q["difficulty"],
              q["type"], int(ok), reason or None, normalized,
              None if given is None else str(given), None if ms is None else max(0, int(ms)),
              when, int(repeat), int(bool(q.get("repair"))), int(flagged), int(guess),
              sms, void, str(q.get("stem") or "")[:200], conf, hints, miss_kind,
              json.dumps(offered), struck_json, int(bool(cover)), int(bool(calc)),
              when if revealed else None, word, source)
    insert = ("INSERT INTO attempts (learner, session, qid, template, seed, topic, difficulty,"
              " fmt, correct, reason, norm, given, ms, at, repeat, repair, flagged, guess, sms, void, stem,"
              " conf, hints, miss_kind, offered, struck, cover, calc, revealed_at, word, source) ")
    marks = ",".join("?" for _ in values)
    opened: list[str] = []
    closed: list[str] = []
    checked: list[dict] = []
    relapsed: list[dict] = []
    not_offered: list[dict] = []
    opened_ids: list[int] = []
    closed_ids: list[int] = []
    clean = ok and not (repeat or flagged or guess or void or hints or conf == "unsure")
    miss_key = None if ok else norm(reason)
    day = _local_day(when, tz).isoformat()
    with db.atomic():
        db.ensure_learner(learner)
        if once:
            cur = db.run(insert + f"SELECT {marks} WHERE NOT EXISTS"
                         " (SELECT 1 FROM attempts WHERE learner=? AND session=?)", *values, learner, session)
            if not cur.rowcount:
                return None
        else:
            cur = db.run(insert + f"VALUES ({marks})", *values)
        attempt = cur.lastrowid

        for t in db.rows("SELECT * FROM traps WHERE learner=? AND template=? AND (closed IS NULL"
                         " OR (due IS NOT NULL AND closed_how IN ('fixed','transfer')))", learner, q["key"]):
            on_offer = t["norm"] in offered
            if t["closed"] is None:
                if not clean:
                    continue
                if not on_offer and _is_named(learner, t):
                    not_offered.append({"id": t["id"], "label": t["label"], "owed": t["owed"]})
                    continue
                left = t["owed"] - 1
                if left <= 0:
                    db.run("UPDATE traps SET owed=0,closed=?,closed_how='fixed',last=?,due=?,checks=0,tz=? WHERE id=?",
                           when, when, _check_due(when, 0, tz), tz, t["id"])
                    log(learner, t["template"], t["norm"], "pip", when, attempt)
                    from . import estimate
                    log(learner, t["template"], t["norm"], "fixed", when, attempt,
                        estimate.trap_pts(learner, t["template"], t["norm"], t["topic"]))
                    closed.append(t["label"])
                    closed_ids.append(t["id"])
                else:
                    db.run("UPDATE traps SET owed=?,last=? WHERE id=?", left, when, t["id"])
                    log(learner, t["template"], t["norm"], "pip", when, attempt)
                continue
            if not (check or t["due"] <= day):
                continue
            if clean and (on_offer or not _is_named(learner, t)):
                checked.append(_pass_check(t, when, attempt, elsewhere=False))
            elif not ok and miss_key != t["norm"] and not check:
                relapsed.append(_relapse(t, when, attempt))

        # R9's transfer check-in: another template offering a fixed trap's norm.
        # A miss there reopens it as on its own template: its own pick always,
        # any other wrong pick unless this is a trap test (G3 rule 5)
        if offered and (clean or not ok):
            marks_n = ",".join("?" for _ in offered)
            for t in db.rows("SELECT * FROM traps WHERE learner=? AND template!=? AND closed IS NOT NULL"
                             " AND closed_how IN ('fixed','transfer') AND due IS NOT NULL AND checks>=1"
                             f" AND norm IN ({marks_n})", learner, q["key"], *offered):
                if not (check or t["due"] <= day):
                    continue
                if clean:
                    checked.append(_pass_check(t, when, attempt, elsewhere=True))
                elif not ok and (miss_key == t["norm"] or not check):
                    relapsed.append({**_relapse(t, when, attempt), "on": q["key"]})

        if not ok or unsure:
            filed = record_trap(learner, q, "~unsure" if unsure else reason, when, session, attempt,
                                unsure=unsure, label=reason_name)
            opened.append(filed["label"])
            opened_ids.append(filed["id"])

        if not (repeat or void or guess or hints or flagged or conf == "unsure") and q.get("difficulty") in ("easy", "medium", "hard"):
            from . import ratings
            ratings.update(learner, q["key"], q["difficulty"], q["topic"], ok, placement=placement)

    if session and not void:
        row = db.one("SELECT contest, ranked FROM sessions WHERE id=?", session)
        rate = deps.part("compete", "rate") if row and row["contest"] and row["ranked"] else None
        if rate:
            rate(learner, session, q, ok, when)
    return {"correct": ok, "reason": reason, "opened": opened, "closed": closed,
            "opened_ids": opened_ids, "closed_ids": closed_ids, "checked": checked,
            "relapsed": relapsed, "not_offered": not_offered, "offered": offered,
            "repeat": repeat, "repair": bool(q.get("repair")), "flagged": flagged,
            "clean": clean, "attempt": attempt}


def record_paper(learner: str, session: str, questions: list[dict], answers: dict,
                 qstate: dict | None = None, flagged: set[str] | None = None) -> int:
    """File a whole test at once, answered questions only: a blank on a timed
    paper says more about the clock than about the topic.

    Each answer carries its time, confidence, strikes, calculator use and
    cover from `qstate` (R7, P3, P6, X19). A trap test's answers are check-ins
    (X16). The odds each item was sat at go into `result.odds` first, before
    these answers move the ratings (P11)."""
    when = now()
    row = db.one("SELECT qstate, cfg, result FROM sessions WHERE id=?", session)
    if qstate is None:
        qstate = json.loads(row["qstate"] or "{}") if row else {}
    cfg = json.loads(row["cfg"] or "{}") if row and row["cfg"] else {}
    trap_test = (cfg.get("custom") or {}).get("source") == "traps"
    if flagged is None:
        flagged = {r["qid"] for r in db.rows("SELECT f.qid FROM flags AS f JOIN sessions AS s ON s.id=f.session"
                                              " WHERE f.learner=? AND f.session=? AND (s.finished IS NULL OR f.at<=s.finished)",
                                              learner, session)}
    if row and row["result"]:
        result = json.loads(row["result"])
        if isinstance(result, dict) and "odds" not in result:
            from . import ratings
            result["odds"] = ratings.snapshot(learner, questions)
            db.run("UPDATE sessions SET result=? WHERE id=?", json.dumps(result), session)
    n = 0
    for q in questions:
        given = answers.get(q["id"])
        if given is None or given == "" or "key" not in q:
            continue
        st = qstate.get(q["id"]) or {}
        record(learner, session, q, given, st.get("ms"), when, flagged=q["id"] in flagged,
               conf=st.get("conf"), struck=st.get("struck"), calc=bool(st.get("calc")),
               cover=bool(st.get("covered")), revealed=False, check=trap_test)
        n += 1
    return n


def log_mistake(learner: str, template: str, topic: str, reason: str = "",
                source: str = "outside", note: str | None = None,
                origin: str | None = None, when: str | None = None, unsure: bool = False) -> int:
    """Put an outside mistake in the same repair queue as answered questions.
    Its label is the reason, else the note, else the template's skill.
    unsure: U2's "I don't know", an Unsure trap that one clean answer closes."""
    if db.is_sample(learner):
        raise HTTPException(403, "the sample report is read-only")
    when = when or now()
    reason = "~unsure" if unsure else (reason or "")[:80]
    skill = None
    if not reason and not note:
        try:
            skill = practice._skill(template, 0)
        except Exception:
            skill = None
    label = "Unsure" if unsure else reason or (note or "")[:80] or skill or topic
    label = label[:1].upper() + label[1:]
    normalized = "~unsure" if unsure else norm(reason)
    with db.atomic():
        db.ensure_learner(learner)
        t = db.one("SELECT id,closed,closed_how,relapses FROM traps WHERE learner=? AND template=? AND norm=?",
                   learner, template, normalized)
        if t:
            relapse = t["closed"] is not None and t["closed_how"] in ("fixed", "transfer")
            db.run("UPDATE traps SET hits=hits+1,owed=?,last=?,closed=NULL,closed_how=NULL,"
                   " relapses=?,reason=?,label=?,source=?,note=?,origin=?,due=NULL,checks=0 WHERE id=?",
                   1 if normalized == "~unsure" else OWED, when, t["relapses"] + int(relapse),
                   reason, label, source, note, origin, t["id"])
            log(learner, template, normalized, "relapse" if relapse else "miss", when)
            return t["id"]
        tid = db.run("INSERT INTO traps(learner,template,norm,reason,label,topic,hits,owed,opened,last,source,note,origin)"
                     " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", learner, template, normalized, reason, label, topic, 1,
                     1 if normalized == "~unsure" else OWED, when, when, source, note, origin).lastrowid
        log(learner, template, normalized, "open", when)
        return tid


def related(normalized: str | None = None):
    """The templates whose items offer this norm, when more than one does
    (R45, G3); with no norm, the whole {norm: templates} index."""
    index = _related_index()
    return index if normalized is None else index.get(normalized, ())


@lru_cache(maxsize=1)
def _related_index() -> dict[str, tuple[str, ...]]:
    """Templates sharing a concrete named misconception across sampled seeds."""
    index: dict[str, set[str]] = defaultdict(set)
    for template in practice.catalogue()["by_topic"].values():
        for key in template:
            for seed in range(12):
                try:
                    it = _item(key, seed)
                except Exception:
                    continue
                for reason in list(it.reasons) + [m.reason for m in getattr(it, "spr_mistakes", ())]:
                    n = norm(reason)
                    if n not in UNNAMED:
                        index[n].add(key)
    return {n: tuple(sorted(keys)) for n, keys in index.items() if len(keys) > 1}


def checkin_template(t) -> str:
    """Where a trap's next check-in is served: the 3-day one on its own
    template, the 10- and 30-day ones on another template offering the same
    norm when one exists (R9, G3 rule 5), else its own."""
    if t["checks"] >= 1:
        others = [k for k in related(t["norm"]) if k != t["template"]]
        if others:
            same_topic = [k for k in others if _topic_of(k) == t["topic"]]
            return (same_topic or others)[0]
    return t["template"]


# ------------------------------------------------------------------ carry

def carry(frm: str, to: str) -> int:
    """Move everything one code has done onto another, as one change.

    A student who opens a second device and types in the first one's code
    must not strand what the second device had already done. A mistake open
    under both codes stays one mistake: its hits add up and it stays open
    until both would have closed it. The target's profile keeps what it has
    set and takes the rest from the other code; the contest rating and each
    skill rating come from whichever side has more rated answers; the target's
    active plan stays active and the other is archived; and a contest sat under
    both codes keeps only its first ranked sitting, as does a challenge day.
    """
    if db.is_sample(frm) or db.is_sample(to):
        raise HTTPException(403, "the sample report can't be added to or claimed")
    if frm == to:
        return 0
    stamp = now()
    with db.transaction() as c:
        n = sum(c.execute(f"SELECT COUNT(*) FROM {table} WHERE learner=?", (frm,)).fetchone()[0]
                for table in ("attempts", "word_reviews", "my_words"))
        if c.execute("SELECT 1 FROM plans WHERE learner=? AND archived IS NULL", (to,)).fetchone():
            c.execute("UPDATE plans SET archived=? WHERE learner=? AND archived IS NULL", (stamp, frm))
        for table in ("attempts", "sessions", "tries", "outside_scores", "plans", "posts", "word_reviews",
                      "my_words", "reports", "links", "trap_log", "official_done", "rw_log", "devices",
                      "passkeys", "webauthn_challenges", "transfers", "push_subs", "users"):
            c.execute(f"UPDATE {table} SET learner=? WHERE learner=?", (to, frm))
        c.execute("UPDATE sets SET owner=? WHERE owner=?", (to, frm))
        c.execute("UPDATE contests SET owner=? WHERE owner=?", (to, frm))
        for table, cols in (("name_reports", ("target", "reporter")), ("follows", ("learner", "target")),
                            ("nudges", ("sender", "target"))):
            for col in cols:
                c.execute(f"UPDATE OR IGNORE {table} SET {col}=? WHERE {col}=?", (to, frm))
            c.execute(f"DELETE FROM {table} WHERE {' OR '.join(f'{col}=?' for col in cols)}", (frm,) * len(cols))
        c.execute("DELETE FROM follows WHERE learner=target")
        # a list named on both sides keeps both sides' words (words.md W19)
        for s in c.execute("SELECT name, words FROM word_lists WHERE learner=?", (frm,)).fetchall():
            t = c.execute("SELECT words FROM word_lists WHERE learner=? AND name=?", (to, s["name"])).fetchone()
            if t:
                both = list(dict.fromkeys(json.loads(t["words"] or "[]") + json.loads(s["words"] or "[]")))
                c.execute("UPDATE word_lists SET words=? WHERE learner=? AND name=?", (json.dumps(both), to, s["name"]))
        for table in ("practice_seen", "saved", "flags", "notes", "earned", "post_votes", "contest_members",
                      "due_days", "week_goals", "word_lists", "champions", "rank_snapshots"):
            c.execute(f"UPDATE OR IGNORE {table} SET learner=? WHERE learner=?", (to, frm))
            c.execute(f"DELETE FROM {table} WHERE learner=?", (frm,))
        for s in c.execute("SELECT * FROM skill_ratings WHERE learner=?", (frm,)).fetchall():
            t = c.execute("SELECT n FROM skill_ratings WHERE learner=? AND topic=?", (to, s["topic"])).fetchone()
            if t is None or s["n"] > t["n"]:
                c.execute("INSERT OR REPLACE INTO skill_ratings(learner,topic,rating,n,seed) VALUES (?,?,?,?,?)",
                          (to, s["topic"], s["rating"], s["n"], s["seed"]))
        c.execute("DELETE FROM skill_ratings WHERE learner=?", (frm,))
        for s in c.execute("SELECT * FROM word_state WHERE learner=?", (frm,)).fetchall():
            t = c.execute("SELECT * FROM word_state WHERE learner=? AND word=?", (to, s["word"])).fetchone()
            if t:
                pick = lambda k, f: f(x for x in (t[k], s[k]) if x) if t[k] or s[k] else None  # noqa: E731
                c.execute("UPDATE word_state SET box=?,reps=?,right=?,wrong=?,lapses=?,saved=?,due=?,first=?,last=?,"
                          "hook=COALESCE(hook,?),proven=?,placed=? WHERE learner=? AND word=?",
                          (max(t["box"], s["box"]), *(t[k] + s[k] for k in ("reps", "right", "wrong", "lapses")),
                           max(t["saved"], s["saved"]), pick("due", min), pick("first", min), pick("last", max),
                           s["hook"], pick("proven", max), pick("placed", max), to, s["word"]))
            else:
                c.execute("UPDATE word_state SET learner=? WHERE learner=? AND word=?", (to, frm, s["word"]))
        c.execute("DELETE FROM word_state WHERE learner=?", (frm,))
        for s in c.execute("SELECT * FROM traps WHERE learner=?", (frm,)).fetchall():
            t = c.execute("SELECT * FROM traps WHERE learner=? AND template=? AND norm=?", (to, s["template"], s["norm"])).fetchone()
            if t:
                recent = s if s["last"] >= t["last"] else t
                shut = t["closed"] is not None and s["closed"] is not None
                # open on either side stays open, with no fix or check-ins to show
                c.execute("UPDATE traps SET hits=?,owed=?,opened=?,last=?,closed=?,closed_how=?,reason=?,label=?,topic=?,"
                          "seed=?,session=?,relapses=?,checks=?,due=?,tz=? WHERE id=?",
                          (t["hits"] + s["hits"], max(t["owed"], s["owed"]), min(t["opened"], s["opened"]),
                           max(t["last"], s["last"]), max(t["closed"], s["closed"]) if shut else None,
                           t["closed_how"] if shut else None,
                           *(recent[k] for k in ("reason", "label", "topic", "seed", "session")), t["relapses"] + s["relapses"],
                           max(t["checks"], s["checks"]) if shut else 0, recent["due"] if shut else None,
                           recent["tz"] if shut else 0, t["id"]))
                c.execute("DELETE FROM traps WHERE id=?", (s["id"],))
            else:
                c.execute("UPDATE traps SET learner=? WHERE id=?", (to, s["id"]))
        c.execute("DELETE FROM pairs WHERE learner=? OR req_learner=?", (frm, frm))
        c.execute('UPDATE retired SET "into"=? WHERE "into"=?', (to, frm))
        # one ranked sitting per contest (per day for a daily one) and per
        # challenge day (decision 1's twins): the first stays, later ones are repeats
        seen: set = set()
        for x in c.execute("SELECT id, COALESCE(contest,'~challenge') AS k, COALESCE(day,'') AS d FROM sessions"
                           " WHERE learner=? AND ranked=1 AND (contest IS NOT NULL OR (kind='challenge' AND day IS NOT NULL))"
                           " ORDER BY started,id", (to,)).fetchall():
            if (x["k"], x["d"]) in seen:
                c.execute("UPDATE sessions SET ranked=0, unranked_why='repeat' WHERE id=?", (x["id"],))
            seen.add((x["k"], x["d"]))
        s = c.execute("SELECT * FROM learners WHERE id=?", (frm,)).fetchone()
        t = c.execute("SELECT * FROM learners WHERE id=?", (to,)).fetchone()
        if s and t:
            cols = ("name", "exam_date", "target", "minutes", "days", "current", "tests", "focus", "avatar",
                    "board", "country", "rw_now", "rw_target", "plan", "plan_draft", "handle")
            for key in cols:
                if t[key] is None and s[key] is not None:
                    c.execute(f"UPDATE learners SET {key}=? WHERE id=?", (s[key], to))
            if (s["rated"] or 0) > (t["rated"] or 0):
                c.execute("UPDATE learners SET rating=?, rated=? WHERE id=?", (s["rating"], s["rated"], to))
            sp, tp = json.loads(s["prefs"] or "{}"), json.loads(t["prefs"] or "{}")
            c.execute("UPDATE learners SET prefs=?,ach_seen=MAX(COALESCE(ach_seen,''),?),"
                      "feed_seen=MAX(COALESCE(feed_seen,''),?),updated=? WHERE id=?",
                      (json.dumps({**sp, **tp}), s["ach_seen"] or "", s["feed_seen"] or "", stamp, to))
            c.execute("DELETE FROM learners WHERE id=?", (frm,))
        elif s:
            c.execute("UPDATE learners SET id=? WHERE id=?", (to, frm))
    return n


# ------------------------------------------------------------------ the coach

def _days_since(at: str | None, today: dt.date) -> int:
    return (today - dt.date.fromisoformat(at[:10])).days if at else 10_000


def _confident_traps(learner: str) -> dict[int, dict]:
    """Open traps whose latest miss the student marked Sure (P7). The coach
    reads only the explicit tag (practice.md's R9 row: null is an ordinary
    miss, P7 acceptance 6); T9's inferred blind spots are blind()."""
    out = {}
    for t in open_traps(learner):
        r = db.one("SELECT conf, at FROM attempts WHERE learner=? AND template=? AND norm=? AND correct=0"
                   " ORDER BY id DESC LIMIT 1", learner, t["template"], t["norm"])
        if r and r["conf"] == "sure":
            out[t["id"]] = {**t, "at": r["at"]}
    return out


def coach(learner: str, k: int = 3, count: int = 10, subject: str = "math") -> dict:
    """The next session: which topics, and why, in the order worth doing them.

    Mistakes the student was sure of first (P7), then other open mistakes,
    because a named misconception is the cheapest point there is. Then the
    weakest topics that have been worked on. A rough skill (under 10 answers)
    gets a probe first (U5). A student with no history meets the big domains
    first. A strong topic left alone for ten days comes back once, so it
    stays strong.
    """
    b = board(learner, subject)
    today = _local_today(learner)
    due = {r["topic"] for r in db.rows("SELECT topic FROM traps WHERE learner=? AND closed_how IN ('fixed','transfer')"
                                      " AND closed IS NOT NULL AND due<=?", learner, today.isoformat())}
    sure = {t["topic"] for t in _confident_traps(learner).values()}
    from . import prefs
    keep_warm = prefs.get(learner)["keep_warm"]
    # the plan's own say: a domain on focus comes up more, a strong one less
    row = db.one("SELECT focus FROM learners WHERE id=?", learner)
    focus = json.loads(row["focus"]) if row and row["focus"] else {}
    first_try = {r["topic"]: (r["rights"], r["n"]) for r in db.rows(
        f"SELECT topic, SUM(correct) AS rights, COUNT(*) AS n FROM attempts WHERE learner=? AND {COUNTED}"
        " AND repair=0 GROUP BY topic", learner)}
    scored = []
    reasons: dict[str, dict] = {}
    for slug, t in b.items():
        s = 100.0 * min(len(t["traps"]), 3)
        if slug in sure:
            s += 50.0
        if slug in due:
            s += 70.0
        s += {"focus": FOCUS_LIFT, "strong": -FOCUS_LIFT}.get(focus.get(t["domain"]), 0.0)
        since = _days_since(t["last"], today)
        if not t["answered"]:
            s += 60.0 * BLUEPRINT.get(t["domain"], 0.15) / 0.35
        else:
            s += (1.0 - t["mastery"]) * 50.0
            if keep_warm and t["mastery"] >= STRONG and since >= 10:
                s += 30.0
            if since == 0 and not t["traps"]:
                s -= 15.0          # already worked on today
        if slug in sure:
            kind = "confident"
        elif t["traps"]:
            kind = "mistakes"
        elif slug in due:
            kind = "check"
        elif t["answered"] and t["evidence"] < 10:
            kind = "probe"
        elif focus.get(t["domain"]) == "focus":
            kind = "focus"              # the plan's Focus lifted it (FOCUS_LIFT)
        elif not t["answered"]:
            kind = "new"
        elif t["mastery"] >= STRONG:
            kind = "review"
        else:
            kind = "weak"
        right, n = first_try.get(slug, (0, 0))
        reasons[slug] = {"kind": kind, "traps": len(t["traps"]), "mastery": t["mastery"],
                         "first_try_rate": round(right / n, 3) if n else None,
                         "since_days": None if not t["answered"] else since}
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

    if any(p in sure for p in picks):
        why = "confident"
    elif any(b[p]["traps"] for p in picks):
        why = "mistakes"
    elif any(p in due for p in picks):
        why = "check"
    elif any(reasons[p]["kind"] == "probe" for p in picks):
        why = "probe"
    elif any(reasons[p]["kind"] == "focus" for p in picks):
        why = "focus"
    elif not any(b[p]["answered"] for p in picks):
        why = "new"
    elif all(b[p]["mastery"] >= STRONG for p in picks):
        why = "review"
    else:
        why = "weak"
    return {"topics": picks, "ahead": ahead, "count": count, "why": why,
            "mistakes": sum(len(b[p]["traps"]) for p in picks),
            "traps": {p: len(b[p]["traps"]) for p in picks},
            "reasons": {p: reasons[p] for p in picks},
            "probe": [p for p in picks if reasons[p]["kind"] == "probe"]}


# ------------------------------------------------------------------ the days

def _local_day(at: str, tz: int) -> dt.date:
    """tz is JavaScript's getTimezoneOffset(): minutes behind UTC."""
    return (dt.datetime.fromisoformat(at) - dt.timedelta(minutes=tz)).date()


def _qotd_slot(sid: str) -> str | None:
    """'mcq' / 'spr' for the Math day's questions, else the slot id (T14)."""
    if sid.startswith("qotd-spr:"):
        return "spr"
    if sid.startswith("qotd-late:"):
        slot = sid.split(":")[1] if sid.count(":") >= 2 else "math:mcq"
        return {"math:mcq": "mcq", "math:spr": "spr", "mcq": "mcq", "spr": "spr"}.get(slot, slot)
    if sid.startswith("qotd:"):
        parts = sid.split(":")
        if len(parts) >= 4:
            slot = f"{parts[1]}:{parts[2]}"
            return {"math:mcq": "mcq", "math:spr": "spr"}.get(slot, slot)
        return "mcq"
    return None


def sitting_seconds(row) -> int:
    """R13: a finished sitting's own time, capped per module at its clock plus
    a minute (90 minutes each when untimed); used when its answers carry no ms."""
    cfg = json.loads(row["cfg"] or "{}")
    timing = cfg.get("timing") or ("untimed" if cfg.get("timed") is False else "official")
    factor = {"x1.5": 1.5, "x2": 2.0, "x0.85": 0.85}.get(timing, 1.0)

    def cap(clock: float) -> float:
        return 5400 if timing == "untimed" else round(clock * factor) + 60

    start, end = dt.datetime.fromisoformat(row["started"]), dt.datetime.fromisoformat(row["finished"])
    total = max(0.0, (end - start).total_seconds())
    kind = row["kind"]
    if kind in ("mock", "paper", "section"):
        split = dt.datetime.fromisoformat(row["module_started"]) if row["module_started"] else None
        if split and start <= split <= end:
            return int(min((split - start).total_seconds(), cap(2100)) + min((end - split).total_seconds(), cap(2100)))
        return int(min(total, 2 * cap(2100)))
    if kind == "module":
        return int(min(total, cap(2100)))
    questions = json.loads(row["questions"] or "[]")
    size = len(questions) if isinstance(questions, list) and questions else (20 if kind == "diagnostic" else 22)
    return int(min(total, cap((cfg.get("minutes") or size * deps.SECONDS_PER_QUESTION / 60) * 60)))


def days(learner: str, tz: int = 0, weeks: int = 2) -> dict:
    """One local-day ledger for questions, words, finished sittings, official
    questions and plan work (R13), with spare days (U16)."""
    tz = _learner_tz(learner, tz)
    weeks = max(1, min(53, int(weeks)))
    per: dict[dt.date, dict] = defaultdict(lambda: {"questions": 0, "right": 0, "words": 0, "ms": 0,
                                                    "practice": 0, "tests": 0, "official": 0, "fixed": 0,
                                                    "qotd": {"mcq": False, "spr": False}})
    kinds = {r["id"]: r["kind"] for r in db.rows("SELECT id,kind FROM sessions WHERE learner=?", learner)}
    timed_sessions = set()
    for r in db.rows("SELECT session,at,ms,sms,correct,disputed FROM attempts WHERE learner=?", learner):
        d = per[_local_day(r["at"], tz)]
        d["questions"] += 1
        d["right"] += int(bool(r["correct"]) and not r["disputed"])
        spent = r["ms"] if r["ms"] is not None else r["sms"]
        d["ms"] += min(max(spent or 0, 0), MS_CAP)
        sid = r["session"] or ""
        slot = _qotd_slot(sid)
        if slot:
            d["qotd"][slot] = True
        if kinds.get(sid) not in deps.TEST_KINDS:
            d["practice"] += 1
        if sid and r["ms"] is not None:
            timed_sessions.add(sid)
    # words.md §3.2: a lookup, a sort or a placement answer is not a review
    for r in db.rows("SELECT at,ms,attempt FROM word_reviews WHERE learner=?"
                     " AND COALESCE(mode,'') NOT IN ('lookup','sort','placement')", learner):
        d = per[_local_day(r["at"], tz)]
        d["words"] += 1
        if r["attempt"] is None:                    # a generated item's minutes count through its attempt
            d["ms"] += min(max(r["ms"] or 0, 0), 60_000)
    for r in db.rows("SELECT at,ms FROM official_done WHERE learner=?", learner):
        d = per[_local_day(r["at"], tz)]
        d["official"] += 1
        d["ms"] += min(max(r["ms"] or 0, 0), MS_CAP)
    for r in db.rows("SELECT * FROM sessions WHERE learner=? AND finished IS NOT NULL AND abandoned IS NULL"
                     f" AND kind IN ({','.join('?' for _ in deps.TEST_KINDS)})", learner, *deps.TEST_KINDS):
        d = per[_local_day(r["finished"], tz)]
        d["tests"] += 1
        d["finished"] = True
        if r["id"] not in timed_sessions:
            d["ms"] += sitting_seconds(r) * 1000
    for r in db.rows("SELECT closed FROM traps WHERE learner=? AND closed IS NOT NULL"
                     " AND closed_how IN ('fixed','transfer')", learner):
        per[_local_day(r["closed"], tz)]["fixed"] += 1
    plan = db.one("SELECT plan,days,exam_date FROM learners WHERE id=?", learner)
    plan_id = plan["plan"] if plan else None
    overrides = {r["day"]: r["off"] for r in db.rows("SELECT day,off FROM plan_overrides WHERE plan=?", plan_id)} if plan_id else {}
    frozen = {r["day"]: r["kind"] for r in db.rows("SELECT day,kind FROM plan_days WHERE plan=?", plan_id)} if plan_id else {}
    if plan_id:
        # R13's own-task rule: an own task's minutes, or the minutes a done
        # question task says it took elsewhere (L10's "Did it elsewhere?")
        for r in db.rows("SELECT m.day, COALESCE(m.minutes, t.minutes) AS minutes FROM plan_marks AS m"
                         " LEFT JOIN plan_tasks AS t ON t.id=m.task WHERE m.plan=? AND m.status='done'", plan_id):
            try:
                per[dt.date.fromisoformat(r["day"])]["ms"] += max(0, r["minutes"] or 0) * 60_000
            except ValueError:
                pass
    today = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date()

    def rest(d: dt.date) -> bool:
        if not plan_id:
            return False
        if plan["exam_date"] and d == dt.date.fromisoformat(plan["exam_date"]) - dt.timedelta(days=1):
            return True
        if overrides.get(d.isoformat()):
            return True
        if d.isoformat() in frozen:
            return frozen[d.isoformat()] in ("rest", "off", "eve")
        return bool(plan["days"] and len(plan["days"]) == 7 and plan["days"][d.weekday()] == "0")

    def active(d: dt.date) -> bool:
        v = per.get(d, {})
        return bool(v.get("questions") or v.get("words", 0) >= 10 or v.get("finished") or v.get("official"))

    # U16: every 7 study days in a row bank a spare (at most 2); a missed study
    # day spends one and, like a rest day, neither breaks nor extends the run.
    # ponytail: plan.md's "spent only once the next study day ends" and L17's
    # made-up days are not modelled; today, still open, never spends or breaks.
    spare_used: set[dt.date] = set()
    run = best = in_row = bank = 0
    start = min((d for d in per if active(d)), default=today)
    for i in range((today - start).days + 1):
        d = start + dt.timedelta(days=i)
        if active(d):
            run += 1
            in_row += 1
            if in_row % 7 == 0:
                bank = min(2, bank + 1)
            best = max(best, run)
        elif rest(d) or d == today:
            continue
        elif bank:
            bank -= 1
            spare_used.add(d)
        else:
            run = in_row = 0

    def line(d: dt.date) -> dict:
        v = per.get(d, {})
        return {"day": d.isoformat(), "questions": v.get("questions", 0), "right": v.get("right", 0),
                "words": v.get("words", 0), "minutes": round(v.get("ms", 0) / 60_000), "rest": rest(d),
                "practice": v.get("practice", 0), "tests": v.get("tests", 0),
                "official": v.get("official", 0), "fixed": v.get("fixed", 0),
                "qotd": dict(v.get("qotd") or {"mcq": False, "spr": False}),
                "spare_used": d in spare_used}

    recent = [line(today - dt.timedelta(days=back)) for back in range(13, -1, -1)]
    calendar = [line(today - dt.timedelta(days=back)) for back in range(weeks * 7 - 1, -1, -1)]
    own_words = db.one("SELECT COUNT(*) AS n FROM my_words WHERE learner=?", learner)["n"]
    return {"today": today.isoformat(), "streak": run, "best": best, "best_streak": best, "spares": bank,
            "active_days": sum(active(d) for d in per),
            "minutes_total": round(sum(v["ms"] for v in per.values()) / 60_000),
            "recent": recent, "days": calendar,
            "total": sum(v["questions"] + v["words"] for v in per.values()) + own_words}


# ------------------------------------------------------------------ spaced returns (T3, R9)

def interval_for(k: int) -> int:
    """T3: days before a type with k counted clean rights fades."""
    return {1: 2, 2: 5, 3: 12}.get(k, 30 if k >= 4 else 0)


def _clean_rights(learner: str, subject: str = "math") -> dict[str, list[str]]:
    """Per template, the clean rights that count toward its interval: each at
    least 20 hours after the previous counted one."""
    out: dict[str, list[str]] = defaultdict(list)
    for r in db.rows(f"SELECT template, topic, at FROM attempts WHERE learner=? AND correct=1 AND {COUNTED}"
                     " AND flagged=0 AND guess=0 AND hints=0 AND COALESCE(conf,'')!='unsure' ORDER BY at", learner):
        if deps.subject_of(r["topic"]) != subject:
            continue
        got = out[r["template"]]
        if not got or dt.datetime.fromisoformat(r["at"]) - dt.datetime.fromisoformat(got[-1]) >= dt.timedelta(hours=20):
            got.append(r["at"])
    return out


def due_rechecks(learner: str, day: str | None = None) -> list[dict]:
    """Fixed traps whose check-in is due by `day`, most overdue first, each with
    the template its check-in is served on."""
    day = day or _local_today(learner).isoformat()
    out = []
    for t in db.rows("SELECT * FROM traps WHERE learner=? AND closed IS NOT NULL AND closed_how IN ('fixed','transfer')"
                     " AND due IS NOT NULL AND due<=? ORDER BY due, id", learner, day):
        out.append({"kind": "check", "trap_id": t["id"], "template": t["template"], "topic": t["topic"],
                    "label": t["label"], "norm": t["norm"], "due": t["due"], "checks": t["checks"],
                    "serve": checkin_template(t),
                    "overdue": (dt.date.fromisoformat(day) - dt.date.fromisoformat(t["due"])).days})
    return out


def rechecks_passed(learner: str, since: str) -> dict:
    """Check-ins passed since `since` (Plan's recheck receipts)."""
    rows = db.rows("SELECT template, norm, at FROM trap_log WHERE learner=? AND event='check_ok' AND at>=?"
                   " ORDER BY at", learner, since)
    return {"n": len(rows), "items": [dict(r) for r in rows]}


def warmup_candidates(learner: str, tz: int | None = None, subject: str = "math") -> dict:
    """T3: what is due for a spaced return, in priority order: check-ins due
    (most overdue first), fading types (by age over interval), one Strong
    topic to keep warm; and P12's marked: a question flagged 2 or more days
    ago whose template has had no right first try since the flag."""
    tz = _learner_tz(learner, tz)
    today = _local_today(learner, tz)
    checks = [c for c in due_rechecks(learner, today.isoformat()) if deps.subject_of(c["topic"]) == subject]
    open_templates = {t["template"] for t in open_traps(learner)}
    fading = []
    for template, stamps in _clean_rights(learner, subject).items():
        if template in open_templates:
            continue
        k = len(stamps)
        age = (today - _local_day(stamps[-1], tz)).days
        if age >= interval_for(k):
            fading.append({"kind": "fading", "template": template, "topic": _topic_of(template),
                           "k": k, "interval": interval_for(k), "age": age,
                           "ratio": round(age / interval_for(k), 2), "last": stamps[-1]})
    fading.sort(key=lambda f: (-f["ratio"], f["template"]))
    keep = []
    from . import prefs
    if prefs.get(learner)["keep_warm"]:
        strong = [t for t in board(learner, subject).values()
                  if t["mastery"] >= STRONG and t["last"] and _days_since(t["last"], today) >= 10]
        if strong:
            t = min(strong, key=lambda t: t["last"])
            keep = [{"kind": "keep_warm", "topic": t["topic"], "last": t["last"]}]
    marked: dict[str, dict] = {}
    for f in db.rows("SELECT f.* FROM flags AS f JOIN sessions AS x ON x.id=f.session WHERE f.learner=?"
                     " AND (x.kind='drill' OR x.finished IS NOT NULL) ORDER BY f.at", learner):
        if deps.subject_of(f["template"]) != subject or (today - _local_day(f["at"], tz)).days < 2:
            continue
        if db.one(f"SELECT 1 FROM attempts WHERE learner=? AND template=? AND at>? AND correct=1 AND flagged=0"
                  f" AND {COUNTED}", learner, f["template"], f["at"]):
            continue
        marked.setdefault(f["template"], {"kind": "marked", "template": f["template"], "topic": f["topic"],
                                          "seed": f["seed"], "session": f["session"], "qid": f["qid"],
                                          "flagged": f["at"]})
    return {"subject": subject, "checks": checks, "fading": fading, "keep_warm": keep,
            "marked": list(marked.values()),
            "size": len(checks) + len(fading) + len(keep) + len(marked)}


def due_forecast(learner: str, tz: int | None = None, days: int = 14) -> list[dict]:
    """T3: check-ins and fading types coming due over the next days, assuming
    no practice in between."""
    tz = _learner_tz(learner, tz)
    today = _local_today(learner, tz)
    checks = Counter(r["due"] for r in db.rows("SELECT due FROM traps WHERE learner=? AND closed IS NOT NULL"
                                                " AND closed_how IN ('fixed','transfer') AND due IS NOT NULL", learner))
    fading: Counter = Counter()
    for template, stamps in _clean_rights(learner).items():
        fading[(_local_day(stamps[-1], tz) + dt.timedelta(days=interval_for(len(stamps)))).isoformat()] += 1
    out = []
    for i in range(1, max(1, int(days)) + 1):
        d = (today + dt.timedelta(days=i)).isoformat()
        out.append({"day": d, "checks": checks.get(d, 0), "fading": fading.get(d, 0)})
    return out


# ------------------------------------------------------------------ causes (T7, R47)

def _paper(row) -> list[dict]:
    """A sitting's questions as one list, both modules of a section included."""
    p = deps.paper_of(row)
    if isinstance(p, dict):
        p = [x for v in p.values() if isinstance(v, list) for x in v]
    return [q for q in p if isinstance(q, dict) and "id" in q]


def cause_of(attempt: dict, ctx: dict | None = None) -> tuple[str, dict]:
    """T7's per-attempt rule, first match: a student-set miss_kind; `changed`
    on tests (the first answer was the key); clock; entry; trap; slip; gap.
    ctx: {qstate, timed, history: [earlier first tries on the template, newest
    first, as 0/1], median_easy_ms, key, spr_reasons}."""
    ctx = ctx or {}
    st = (ctx.get("qstate") or {}).get(attempt.get("qid") or "", {}) or {}
    ms = attempt.get("ms") if attempt.get("ms") is not None else attempt.get("sms")
    evidence: dict = {"ms": ms}
    if attempt.get("miss_kind") in MISS_KINDS:
        return MISS_KINDS[attempt["miss_kind"]], {**evidence, "set_by": "you"}
    given = attempt.get("given")
    key = ctx.get("key")
    if given is None or given == "":
        return ("clock" if ctx.get("timed") else "gap"), {**evidence, "blank": True}
    first = st.get("first")
    if ctx.get("test") and first is not None and key is not None and str(first) != str(given):
        q = {"type": attempt.get("fmt") or "mcq", "answer": key}
        try:
            first_ok = scoring.is_correct(q, int(first) if q["type"] == "mcq" else str(first))
        except (TypeError, ValueError):
            first_ok = False
        if first_ok:
            return "changed", {**evidence, "first": first}
    made_left = st.get("made_left")
    if ctx.get("timed") and made_left is not None and made_left <= 90_000 and ms is not None and ms < 25_000:
        return "clock", {**evidence, "made_left": made_left}
    if attempt.get("fmt") == "spr" and key is not None:
        diag = scoring.grid_diagnose(str(given), str(key), ctx.get("spr_reasons"))
        if scoring.entry_error(str(given), str(key)) or (diag and diag["kind"] in ("form", "short")):
            return "entry", {**evidence, "diagnosis": diag}
    n = attempt.get("norm")
    if n is None:
        n = norm(attempt.get("reason") or "")
    if n not in UNNAMED:
        return "trap", {**evidence, "norm": n}
    second = st.get("second") or {}
    if second.get("correct") and second.get("conf") != "guess":
        return "slip", {**evidence, "second_look": True}
    history = ctx.get("history") or []
    if len(history) >= 5 and sum(history[:5]) >= 4:
        return "slip", {**evidence, "usually_right": f"{sum(history[:5])} of your last 5"}
    median_easy = ctx.get("median_easy_ms")
    if attempt.get("difficulty") == "easy" and median_easy and ms is not None and ms < median_easy / 2:
        return "slip", {**evidence, "fast": True}
    return "gap", evidence


def _tier_medians(learner: str) -> dict[str, float]:
    """The learner's median answer time per tier, over the answers R8 counts."""
    per: dict[str, list] = defaultdict(list)
    for r in db.rows("SELECT difficulty, COALESCE(ms, sms) AS spent FROM attempts WHERE learner=?"
                     f" AND COALESCE(ms, sms) IS NOT NULL AND {COUNTED}", learner):
        per[r["difficulty"]].append(r["spent"])
    return {tier: statistics.median(v) for tier, v in per.items()}


def _sitting(sid: str | None, cache: dict) -> dict:
    """What T7 needs to know about the sitting an answer came from."""
    if sid not in cache:
        row = db.one("SELECT * FROM sessions WHERE id=?", sid) if sid else None
        cfg = json.loads(row["cfg"] or "{}") if row and row["cfg"] else {}
        test = bool(row) and row["kind"] in deps.TEST_KINDS
        timed = bool(row) and (test and cfg.get("timing", "official") != "untimed" and cfg.get("timed", True)
                               or cfg.get("timed") or cfg.get("clock") in ("pace", "custom"))
        cache[sid] = {"row": row, "qstate": json.loads(row["qstate"] or "{}") if row and row["qstate"] else {},
                      "timed": timed, "test": test}
    return cache[sid]


def _cause(learner: str, a: dict, sitting: dict, medians: dict) -> tuple[str, dict]:
    """cause_of for one filed attempt, with its context built the one way
    causes() and blind() share, so the causes bar and T9's card agree."""
    history = [r["correct"] for r in db.rows(f"SELECT correct FROM attempts WHERE learner=? AND template=? AND id<?"
                                             f" AND {COUNTED} ORDER BY id DESC LIMIT 5", learner, a["template"], a["id"])]
    try:
        spr = [[m.reason, str(m.value)] for m in getattr(_item(a["template"], a["seed"]), "spr_mistakes", ())]
    except Exception:
        spr = []
    return cause_of(a, {"qstate": sitting["qstate"], "timed": sitting["timed"], "test": sitting["test"],
                        "history": history, "median_easy_ms": medians.get("easy"),
                        "key": _key_of(a["template"], a["seed"]), "spr_reasons": spr})


def _sure_why(a: dict, sitting: dict, medians: dict) -> str | None:
    """T9's 'sure' for a miss already known to be no guess and a trap:
    'sure' (tagged, P7 or the test's qstate), 'fast' (a medium or hard
    question in under 0.6x the learner's median for its tier; never an easy
    one, which is T7's slip) or 'silent' (a test miss left out of the
    predictions made in that sitting, X11)."""
    qstate = sitting["qstate"] if isinstance(sitting["qstate"], dict) else {}
    st = qstate.get(a.get("qid") or "") or {}
    if a.get("conf") == "sure" or st.get("conf") == "sure":
        return "sure"
    spent = a["ms"] if a.get("ms") is not None else a.get("sms")
    median = medians.get(a["difficulty"])
    if a["difficulty"] in ("medium", "hard") and spent is not None and median and spent < 0.6 * median:
        return "fast"
    predicted = any(isinstance(v, dict) and v.get("predict") == "miss" for v in qstate.values())
    if sitting["test"] and predicted and st.get("predict") != "miss" \
            and "unsure" not in (a.get("conf"), st.get("conf")) and st.get("conf") != "guess":
        return "silent"
    return None


def blind(learner: str, subject: str = "math") -> dict[int, dict]:
    """T9's blind spots: open traps whose latest miss was sure -- not a guess
    (R8), T7's cause `trap`, and `_sure_why`. Newest trap first, the order of
    open_traps; each carries why, the attempt and its time."""
    medians = _tier_medians(learner)
    cache: dict = {}
    out = {}
    for t in open_traps(learner):
        if deps.subject_of(t["topic"]) != subject:
            continue
        a = db.one("SELECT * FROM attempts WHERE learner=? AND template=? AND norm=? AND correct=0"
                   " ORDER BY id DESC LIMIT 1", learner, t["template"], t["norm"])
        if not a or a["guess"] or a["conf"] == "guess":
            continue
        a = dict(a)
        sitting = _sitting(a["session"], cache)
        if _cause(learner, a, sitting, medians)[0] != "trap":
            continue
        why = _sure_why(a, sitting, medians)
        if why:
            out[t["id"]] = {**t, "at": a["at"], "attempt": a["id"], "why": why}
    return out


def causes(learner: str, tz: int = 0, days: int = 14, session: str | None = None,
           subject: str = "math") -> dict:
    """Every wrong or blank first try R8 counts, sorted into one cause each."""
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).isoformat()
    where, args = ("session=?", [session]) if session else ("at>=?", [since])
    rows = [dict(r) for r in db.rows(f"SELECT * FROM attempts WHERE learner=? AND {where} AND {COUNTED}"
                                     " AND correct=0 ORDER BY id", learner, *args)
            if deps.subject_of(r["topic"]) == subject]
    medians = _tier_medians(learner)
    sittings: dict = {}

    def sitting(sid):
        return _sitting(sid, sittings)

    by = {c: 0 for c in CAUSES}
    items: dict[str, list] = {c: [] for c in CAUSES}
    per_q: dict[str, dict] = {}
    top_gap: Counter = Counter()
    for a in rows:
        cause, ev = _cause(learner, a, sitting(a["session"]), medians)
        by[cause] += 1
        if len(items[cause]) < 40:
            items[cause].append(a["id"])
        if cause == "gap":
            top_gap[a["topic"]] += 1
        if session:
            per_q[a["qid"]] = {"cause": cause, "auto": a.get("miss_kind") is None, "evidence": ev, "attempt": a["id"]}
    # blanks on timed test papers have no attempts row
    paper_rows = [db.one("SELECT * FROM sessions WHERE id=?", session)] if session else db.rows(
        f"SELECT * FROM sessions WHERE learner=? AND finished>=? AND abandoned IS NULL"
        f" AND kind IN ({','.join('?' for _ in deps.TEST_KINDS)})", learner, since, *deps.TEST_KINDS)
    for row in paper_rows:
        if not row or not row["finished"] or row["kind"] not in deps.TEST_KINDS:
            continue
        answers = json.loads(row["answers"] or "{}")
        s = sitting(row["id"])
        for q in _paper(row):
            if "key" not in q or deps.subject_of(q.get("topic")) != subject:
                continue
            if answers.get(q["id"]) in (None, ""):
                cause = "clock" if s["timed"] else "gap"
                by[cause] += 1
                if len(items[cause]) < 40:
                    items[cause].append(f"{row['id']}:{q['id']}")
                if session:
                    per_q[q["id"]] = {"cause": cause, "auto": True, "evidence": {"blank": True}}
    changes = {"right_to_wrong": 0, "wrong_to_right": 0, "sittings": 0}
    month = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)).isoformat()
    for row in db.rows(f"SELECT * FROM sessions WHERE learner=? AND finished>=? AND kind IN"
                       f" ({','.join('?' for _ in deps.TEST_KINDS)})", learner, month, *deps.TEST_KINDS):
        qstate = json.loads(row["qstate"] or "{}")
        answers = json.loads(row["answers"] or "{}")
        changed = False
        paper = {q["id"]: q for q in _paper(row)}
        for qid, st in qstate.items():
            q = paper.get(qid)
            if not q or not isinstance(st, dict) or st.get("first") in (None, "") or qid not in answers:
                continue
            if str(st["first"]) == str(answers[qid]):
                continue
            changed = True
            was, now_ok = scoring.is_correct(q, st["first"]), scoring.is_correct(q, answers[qid])
            changes["right_to_wrong"] += int(was and not now_ok)
            changes["wrong_to_right"] += int(now_ok and not was)
        changes["sittings"] += int(changed)
    total = sum(by.values())
    lever = max(by, key=lambda c: (by[c], -CAUSES.index(c))) if total else None
    out = {"subject": subject, "days": days, "total": total, "by": by, "items": items,
           "lever": lever, "top_gap_topic": top_gap.most_common(1)[0][0] if top_gap else None,
           "changes": changes}
    if session:
        out["per_q"] = per_q
    return out


# ------------------------------------------------------------------ pace (U7, T8, C3)

def pace(learner: str, days: int = 60, subject: str = "math", only: str | None = None) -> dict:
    """Per skill with 5 or more timed first tries: the median time on right
    answers, accuracy and n; a module forecast at those medians; the four
    quadrants; guesses; and answers after striking two options."""
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).isoformat()
    sql = (f"SELECT a.* FROM attempts AS a LEFT JOIN sessions AS s ON s.id=a.session WHERE a.learner=?"
           f" AND a.at>=? AND a.repeat=0 AND a.disputed=0 AND a.void IS NULL"
           " AND COALESCE(a.ms, a.sms) IS NOT NULL")
    if only == "contest":
        sql += " AND s.contest IS NOT NULL"
    rows = [r for r in db.rows(sql, learner, since) if deps.subject_of(r["topic"]) == subject]
    per: dict[str, list] = defaultdict(list)
    for r in rows:
        per[r["topic"]].append(r)
    skills = {}
    for topic, rs in per.items():
        if len(rs) < 5:
            continue
        rights = [(r["ms"] if r["ms"] is not None else r["sms"]) for r in rs if r["correct"]]
        skills[topic] = {"n": len(rs), "accuracy": round(sum(r["correct"] for r in rs) / len(rs), 3),
                         "median_ms_right": int(statistics.median(rights)) if rights else None,
                         "median_ms": int(statistics.median([(r["ms"] if r["ms"] is not None else r["sms"]) for r in rs]))}
    mean = statistics.mean([s["accuracy"] for s in skills.values()]) if skills else None
    quadrants = {"slow_right": [], "fast_wrong": [], "slow_wrong": [], "fast_right": []}
    for topic, s in skills.items():
        speed = s["median_ms_right"] if s["median_ms_right"] is not None else s["median_ms"]
        slow = speed > deps.SECONDS_PER_QUESTION * 1000
        right = s["accuracy"] >= mean
        s["quadrant"] = f"{'slow' if slow else 'fast'}_{'right' if right else 'wrong'}"
        quadrants[s["quadrant"]].append(topic)
    from . import blueprint
    names = topics(subject)
    domain_ms: dict[str, list] = defaultdict(list)
    for topic, s in skills.items():
        if topic in names:
            domain_ms[names[topic].domain].append(s["median_ms_right"] or s["median_ms"])
    strip, total, runs_out = [], 0, None
    for i, (domain, tier, _fmt) in enumerate(blueprint.slots("module1", 1)):
        ms = int(statistics.median(domain_ms[domain])) if domain_ms.get(domain) else deps.SECONDS_PER_QUESTION * 1000
        total += ms
        strip.append({"slot": i, "domain": domain, "tier": tier, "ms": ms})
        if runs_out is None and total > blueprint.MODULE_SECONDS * 1000:
            runs_out = i
    blanks = 0 if runs_out is None else len(strip) - runs_out
    guesses = [r for r in rows if r["guess"] or r["conf"] == "guess"]
    struck2 = [r for r in rows if r["struck"] and len(json.loads(r["struck"])) >= 2]
    return {"subject": subject, "days": days, "only": only, "skills": skills, "mean_accuracy": mean,
            "quadrants": quadrants,
            "forecast": {"seconds": round(total / 1000), "limit": blueprint.MODULE_SECONDS,
                         "blanks": blanks, "runs_out_at": runs_out, "strip": strip},
            "guess": {"n": len(guesses), "right": sum(r["correct"] for r in guesses)},
            "struck2": {"n": len(struck2), "right": sum(r["correct"] for r in struck2)}}


TIER_BUDGET_MS = {"easy": 65_000, "medium": 95_000, "hard": 126_000}   # P16's Math tier defaults


def fluency(learner: str, budget_ms=None, subject: str = "math") -> dict[str, dict]:
    """P16, per template with timed first tries: Fluent (its last 2 clean
    first-try rights each under budget), Right but slow (3+ first tries, 80%+
    right, median right time over budget), best_ms (its fastest clean right)
    and the medians. budget_ms(template, tier) is F5's; the tier default
    otherwise."""
    budget = budget_ms or (lambda _t, tier: TIER_BUDGET_MS.get(tier, 95_000))
    per: dict[str, list] = defaultdict(list)
    for r in db.rows(f"SELECT template, topic, difficulty, correct, flagged, guess, hints, conf,"
                     f" COALESCE(ms, sms) AS spent FROM attempts WHERE learner=? AND {COUNTED}"
                     " AND COALESCE(ms, sms) IS NOT NULL ORDER BY id", learner):
        if deps.subject_of(r["topic"]) == subject:
            per[r["template"]].append(r)
    out = {}
    for template, rs in per.items():
        clean = [r for r in rs if r["correct"] and not (r["flagged"] or r["guess"] or r["hints"] or r["conf"] == "unsure")]
        rights = [r["spent"] for r in rs if r["correct"]]
        median_right = statistics.median(rights) if rights else None
        tier = rs[-1]["difficulty"]
        out[template] = {
            "n": len(rs), "right": len(rights), "budget_ms": budget(template, tier),
            "median_ms": int(statistics.median(r["spent"] for r in rs)),
            "median_right_ms": None if median_right is None else int(median_right),
            "best_ms": min((r["spent"] for r in clean), default=None),
            "fluent": len(clean) >= 2 and all(r["spent"] < budget(template, r["difficulty"]) for r in clean[-2:]),
            "slow_right": len(rs) >= 3 and len(rights) >= 0.8 * len(rs) and median_right is not None
            and median_right > budget(template, tier)}
    return out


# ------------------------------------------------------------------ the report's readers

def recovery(learner: str, sid: str) -> dict | None:
    """SR6: which of a sitting's misses have been won back since, re-scored."""
    from . import estimate
    row = db.one("SELECT * FROM sessions WHERE id=?", sid)
    if not row or not row["finished"]:
        return None
    misses = db.rows("SELECT * FROM attempts WHERE session=? AND correct=0 AND learner=?", sid, learner)
    recovered, slipping, still = [], [], []
    timeline: Counter = Counter()
    for m in misses:
        later = db.rows(f"SELECT correct, at FROM attempts WHERE learner=? AND template=? AND at>? AND"
                        f" COALESCE(session,'')!=? AND {COUNTED} AND flagged=0 AND guess=0 AND hints=0"
                        " ORDER BY at", learner, m["template"], row["finished"], sid)
        trap = db.one("SELECT closed FROM traps WHERE learner=? AND template=? AND norm=?",
                      learner, m["template"], m["norm"] or "")
        if later and later[-1]["correct"] and ((trap and trap["closed"]) or sum(r["correct"] for r in later) >= 2):
            recovered.append(m["qid"])
            timeline[("proved", later[-1]["at"][:10])] += 1
        elif later and not later[-1]["correct"]:
            slipping.append(m["qid"])
            timeline[("slipped", later[-1]["at"][:10])] += 1
        else:
            still.append(m["qid"])
    ledger = estimate.ledger(sid)
    now_band = estimate.rescore(sid, right=recovered) if ledger else None
    return {"subject": row["subject"] or "math",
            "recovered": recovered, "slipping": slipping, "open": still, "now": now_band,
            "points_recovered": round(now_band["mid"] - ledger["mid"], 1) if ledger else None,
            "points_open": round(ledger["all_right"]["mid"] - now_band["mid"], 1) if ledger else None,
            "timeline": [{"day": d, "kind": k, "n": n} for (k, d), n in sorted(timeline.items(), key=lambda x: x[0][1])]}


def calibration(learner: str, session: str | None = None, days: int | None = None) -> dict:
    """P7 / SR9 / V5: how right each confidence has been, and what flags and
    answer changes were worth."""
    where, args = ("session=?", [session]) if session else ("1=1", [])
    if days and not session:
        where, args = "at>=?", [(dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).isoformat()]
    rows = db.rows(f"SELECT * FROM attempts WHERE learner=? AND {where} AND {COUNTED}", learner, *args)
    conf = {k: {"right": 0, "wrong": 0} for k in ("sure", "unsure", "guess", "untagged")}
    for r in rows:
        bucket = r["conf"] if r["conf"] in conf else ("guess" if r["guess"] else "untagged")
        conf[bucket]["right" if r["correct"] else "wrong"] += 1
    out = {"conf": conf, "tagged": sum(v["right"] + v["wrong"] for k, v in conf.items() if k != "untagged"),
           "sure_wrong": [r["id"] for r in rows if r["conf"] == "sure" and not r["correct"]],
           "guessed_right": [r["id"] for r in rows if (r["conf"] == "guess" or r["guess"]) and r["correct"]]}
    changes = right_after = 0
    for s in db.rows(f"SELECT * FROM sessions WHERE learner=? AND qstate IS NOT NULL AND qstate!='{{}}'"
                     + (" AND id=?" if session else ""), learner, *([session] if session else [])):
        qstate = json.loads(s["qstate"] or "{}")
        answers = json.loads(s["answers"] or "{}")
        paper = {q["id"]: q for q in _paper(s)}
        for qid, st in qstate.items():
            if isinstance(st, dict) and st.get("first") not in (None, "") and qid in answers \
                    and str(st["first"]) != str(answers[qid]) and qid in paper:
                changes += 1
                right_after += int(scoring.is_correct(paper[qid], answers[qid]))
    out["instinct"] = {"changes": changes, "right": right_after}
    if session:
        flagged = {r["qid"] for r in db.rows("SELECT qid FROM flags WHERE learner=? AND session=?", learner, session)}
        row = db.one("SELECT qstate, answers FROM sessions WHERE id=?", session)
        qstate = json.loads(row["qstate"] or "{}") if row else {}
        by_qid = {r["qid"]: r for r in rows}
        out["flags"] = {"flagged": len(flagged),
                        "revisited": sum(1 for q in flagged if (qstate.get(q) or {}).get("visits", 0) > 1),
                        "changed_right": sum(1 for q in flagged if q in by_qid and by_qid[q]["correct"]
                                             and (qstate.get(q) or {}).get("first") not in (None, "")
                                             and str((qstate.get(q) or {}).get("first")) != str(by_qid[q]["given"])),
                        "left_wrong": sum(1 for q in flagged if q in by_qid and not by_qid[q]["correct"])}
    return out


def types_met(learner: str, subject: str = "math") -> dict:
    """X2 / U8: question types met under the clock, met only in practice, and never."""
    catalogue = [t for ts in practice.catalogue()["by_topic"].values() for t in ts if deps.subject_of(t) == subject]
    tests, other = set(), set()
    for r in db.rows("SELECT DISTINCT a.template, s.kind FROM attempts AS a LEFT JOIN sessions AS s ON s.id=a.session"
                     " WHERE a.learner=?", learner):
        (tests if r["kind"] in deps.TEST_KINDS else other).add(r["template"])
    met = tests | other
    return {"subject": subject, "tests": len(tests & set(catalogue)), "practice": len((other - tests) & set(catalogue)),
            "met": len(met & set(catalogue)), "never": len(set(catalogue) - met), "total": len(catalogue)}


def steps_to(learner: str, topic: str, goal: float = STRONG, tier: str = "medium") -> int | None:
    """P9 / U4: the fewest right answers at `tier` that, appended, lift the
    topic's mastery to `goal`. 0 when it is already there; None when no run
    of rights in the window reaches it."""
    got = db.rows(f"SELECT difficulty, correct, guess, hints FROM attempts WHERE learner=? AND topic=?"
                  f" AND {COUNTED} ORDER BY id DESC LIMIT ?", learner, topic, WINDOW)
    answers = [(r["difficulty"], _counts(r)) for r in got]
    for k in range(0, WINDOW + 1):
        if mastery_of([(tier, 1.0)] * k + answers) >= goal:
            return k
    return None


def conf_active(learner: str) -> bool:
    """P7: an active tagger used Unsure or Guess on at least 10% of their last
    50 first tries; for them a plain Check files Sure."""
    rows = db.rows("SELECT conf, guess FROM attempts WHERE learner=? AND repeat=0 ORDER BY id DESC LIMIT 50", learner)
    tagged = sum(1 for r in rows if r["conf"] in ("unsure", "guess"))
    return bool(rows) and tagged >= 0.1 * len(rows) and tagged > 0


def remark(learner: str, attempt_id: int) -> dict:
    """U3's `remarked`: an answer marked wrong is right after all. The attempt
    is re-marked, a trap it alone opened closes (how 'remarked'), and its
    sitting is re-scored."""
    a = db.one("SELECT * FROM attempts WHERE id=? AND learner=?", attempt_id, learner)
    if not a:
        return {"remarked": False}
    closed = []
    with db.atomic():
        db.run("UPDATE attempts SET correct=1, reason=NULL, norm=NULL WHERE id=?", attempt_id)
        if not a["correct"]:
            t = db.one("SELECT * FROM traps WHERE learner=? AND template=? AND norm=?", learner, a["template"], a["norm"] or "")
            others = db.one("SELECT COUNT(*) AS n FROM attempts WHERE learner=? AND template=? AND norm=? AND correct=0",
                            learner, a["template"], a["norm"] or "")["n"] if t else 0
            if t and t["closed"] is None and not others:
                db.run("UPDATE traps SET closed=?, closed_how='remarked', owed=0, due=NULL WHERE id=?", now(), t["id"])
                log(learner, t["template"], t["norm"], "remarked", now(), attempt_id)
                closed.append(t["id"])
    rescored = None
    if a["session"]:
        from . import estimate
        rescored = estimate.rescore_sitting(a["session"], qid=a["qid"], how="remarked")
    return {"remarked": True, "closed": closed, "rescored": rescored}


def discard(learner: str, sid: str) -> dict:
    """V13: take a sitting's answers off the record and roll its trap changes
    back from trap_log, newest first. Undone by restore()."""
    ids = [r["id"] for r in db.rows("SELECT id FROM attempts WHERE learner=? AND session=?", learner, sid)]
    out = {"answers": len(ids), "traps_closed": 0, "pips_back": 0, "reopened": 0}
    if not ids:
        return out
    marks = ",".join("?" for _ in ids)
    stamp = now()
    with db.atomic():
        db.run(f"UPDATE attempts SET void='discarded' WHERE id IN ({marks})", *ids)
        events = db.rows(f"SELECT * FROM trap_log WHERE learner=? AND attempt IN ({marks})"
                         " AND event NOT IN ('discarded','restored') ORDER BY id DESC", learner, *ids)
        for e in events:
            t = db.one("SELECT * FROM traps WHERE learner=? AND template=? AND norm=?", learner, e["template"], e["norm"])
            if not t:
                continue
            if e["event"] == "open":
                others = db.one(f"SELECT COUNT(*) AS n FROM trap_log WHERE learner=? AND template=? AND norm=?"
                                f" AND event IN ('miss','relapse','reopened') AND (attempt IS NULL OR attempt NOT IN ({marks}))",
                                learner, e["template"], e["norm"], *ids)["n"]
                if not others:
                    db.run("UPDATE traps SET closed=?, closed_how='discarded', due=NULL WHERE id=?", stamp, t["id"])
                    out["traps_closed"] += 1
            elif e["event"] in ("miss", "relapse", "reopened"):
                db.run("UPDATE traps SET hits=MAX(1,hits-1) WHERE id=?", t["id"])
            elif e["event"] == "pip":
                db.run("UPDATE traps SET owed=owed+1 WHERE id=?", t["id"])
                out["pips_back"] += 1
            elif e["event"] == "fixed":
                db.run("UPDATE traps SET closed=NULL, closed_how=NULL, owed=0, due=NULL, checks=0 WHERE id=?", t["id"])
                out["reopened"] += 1
            elif e["event"] == "check_ok":
                checks = max(0, t["checks"] - 1)
                db.run("UPDATE traps SET checks=?, due=? WHERE id=?", checks,
                       _check_due(t["closed"], checks, t["tz"]) if t["closed"] else None, t["id"])
            log(learner, e["template"], e["norm"], "discarded", stamp, e["attempt"], undoes=e["id"])
    return out


def restore(learner: str, sid: str) -> dict:
    """V13's Restore: clear the void and re-apply what discard() rolled back,
    oldest first. The discarded rows name the event they undid (undoes)."""
    ids = [r["id"] for r in db.rows("SELECT id FROM attempts WHERE learner=? AND session=? AND void='discarded'", learner, sid)]
    out = {"answers": len(ids), "traps_closed": 0, "pips_back": 0, "reopened": 0}
    if not ids:
        return out
    marks = ",".join("?" for _ in ids)
    stamp = now()
    with db.atomic():
        db.run(f"UPDATE attempts SET void=NULL WHERE id IN ({marks})", *ids)
        for d in db.rows(f"SELECT d.*, e.event AS undid, e.at AS undid_at FROM trap_log AS d"
                         f" JOIN trap_log AS e ON e.id=d.undoes WHERE d.learner=? AND d.event='discarded'"
                         f" AND d.attempt IN ({marks})"
                         " AND NOT EXISTS (SELECT 1 FROM trap_log AS r WHERE r.event='restored' AND r.undoes=d.id)"
                         " ORDER BY e.id", learner, *ids):
            t = db.one("SELECT * FROM traps WHERE learner=? AND template=? AND norm=?", learner, d["template"], d["norm"])
            if not t:
                continue
            if d["undid"] == "open" and t["closed_how"] == "discarded":
                db.run("UPDATE traps SET closed=NULL, closed_how=NULL WHERE id=?", t["id"])
                out["traps_closed"] += 1
            elif d["undid"] in ("miss", "relapse", "reopened"):
                db.run("UPDATE traps SET hits=hits+1 WHERE id=?", t["id"])
            elif d["undid"] == "pip":
                db.run("UPDATE traps SET owed=MAX(0,owed-1) WHERE id=?", t["id"])
                out["pips_back"] += 1
            elif d["undid"] == "fixed":
                db.run("UPDATE traps SET closed=?, closed_how='fixed', owed=0, due=?, checks=0 WHERE id=?",
                       d["undid_at"], _check_due(d["undid_at"], 0, t["tz"]), t["id"])
                out["reopened"] += 1
            elif d["undid"] == "check_ok" and t["closed"]:
                checks = min(3, t["checks"] + 1)
                db.run("UPDATE traps SET checks=?, due=? WHERE id=?", checks,
                       _check_due(t["closed"], checks, t["tz"]), t["id"])
            log(learner, d["template"], d["norm"], "restored", stamp, d["attempt"], undoes=d["id"])
    return out
