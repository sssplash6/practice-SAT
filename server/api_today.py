"""Today: the learner's day, the day's questions, the calendar and added scores.

GET /api/today feeds the core cards (hero, Up next and Due today, mistakes,
score band, exam, plan, study figures); GET /api/today/insights the cards
that look forward (points on the table, pace, the score's projection, where
the points and the minutes went). Both read the one-source functions of F4
(progress, estimate) and, through deps.part, the sections that are not merged
yet (next, plan, words, compete, habits, review), each dropping out quietly
until its module exists. brief, receipt and workload (T12, T17, T19) live here.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import inspect
import json
import math
import re
import secrets
import statistics
import time
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

from . import challenge, daily, db, drill, estimate, progress, satdates
from .api_me import per_session, profile
from .deps import DATE_OK, LEARNER_OK, TARGETS, TEST_KINDS, learner_of, part, subject_param, tz_of, writer_of

router = APIRouter()

BOX_OPTIONS = (5, 15, 30, 45, 60)
GOAL_CHIPS = (15, 30, 45, 60, 90, 120, 180, 240)
OPEN_DRILL_HOURS = 36
MODULE_S = 35 * 60
SECTION_S = 70 * 60
CHALLENGE_S = 16 * 60
SOURCES = ("bluebook", "official", "other")
SCORES_A_DAY = 20                   # added scores are durable writes: a bound, as SEC-06 asks of every write
FIRST_SCORE_DAY = dt.date(2020, 1, 1)


# ------------------------------------------------------------------ small helpers

def _local_today(tz: int) -> dt.date:
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date()


def _start(day: dt.date, tz: int) -> str:
    """The UTC instant a local day begins, as stored timestamps are written."""
    at = dt.datetime.combine(day, dt.time(), dt.timezone.utc) + dt.timedelta(minutes=tz)
    return at.isoformat(timespec="seconds")


def _monday(day: dt.date) -> dt.date:
    return day - dt.timedelta(days=day.weekday())


def _json(text, default=None):
    try:
        return json.loads(text) if text else default
    except (TypeError, ValueError):
        return default


def _gated(row) -> bool:
    """R38: a diagnostic nobody signed up for keeps its results behind the gate."""
    return row["kind"] == "diagnostic" and not row["user_id"]


def _word(m: float, answered: int) -> str:
    """UI.masteryWord's rule, for server text (R37)."""
    if not answered:
        return "Not started"
    return "Learning" if m < 0.4 else "Getting there" if m < progress.STRONG else "Strong"


def _median_s(learner: str) -> float:
    """Median Math seconds over 60 days, after 20 timed first answers.

    One very fast answer is not evidence that a learner can sustain that pace
    across a section. Untimed practice and daily questions are excluded.
    """
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=60)).isoformat()
    rows = db.rows(f"SELECT a.topic, COALESCE(a.ms, a.sms) AS t FROM attempts AS a"
                   f" JOIN sessions AS s ON s.id=a.session WHERE a.learner=? AND a.at>=?"
                   f" AND a.repeat=0 AND a.disputed=0 AND a.void IS NULL"
                   f" AND COALESCE(a.ms, a.sms) BETWEEN 1000 AND ?"
                   f" AND (s.kind IN ({','.join('?' for _ in TEST_KINDS)}, 'challenge')"
                   " OR json_extract(s.cfg,'$.timed')=1)", learner, since, progress.MS_CAP, *TEST_KINDS)
    spent = [r["t"] for r in rows if drill.deps.subject_of(r["topic"]) == "math"]
    return statistics.median(spent) / 1000 if len(spent) >= 20 else 95.0


def _call(module: str, name: str, *args, **kwargs):
    """A section's function through deps.part, or None while it is missing.
    ponytail: a present module that raises is caught so one card cannot take
    /api/today down; its error goes to the log, not to the student."""
    fn = part(module, name)
    if fn is None:
        return None
    try:
        return fn(*args, **kwargs)
    except HTTPException:
        raise
    except Exception:                               # pragma: no cover - logged, card degrades
        import logging
        logging.getLogger("satf").exception("%s.%s failed", module, name)
        return None


def _mastery_at(learner: str, until: str) -> dict[str, float]:
    """Each topic's mastery over the answers before `until` (R8 counting)."""
    per: dict[str, list] = {}
    for r in db.rows(f"SELECT topic, difficulty, correct, guess, hints FROM attempts WHERE learner=?"
                     f" AND at<? AND {progress.COUNTED} ORDER BY id DESC", learner, until):
        got = per.setdefault(r["topic"], [])
        if len(got) < progress.WINDOW:
            got.append((r["difficulty"], progress._counts(r)))
    return {t: progress.mastery_of(v) for t, v in per.items()}


# ------------------------------------------------------------------ scores (R16, R38)

def scores(learner: str, limit: int = 8) -> list[dict]:
    """The newest scored sittings, newest first; an un-signed-up diagnostic is left out."""
    out = []
    for r in db.rows(f"SELECT id, kind, result, finished, route, user_id FROM sessions WHERE learner=?"
                     f" AND finished IS NOT NULL AND abandoned IS NULL AND result IS NOT NULL"
                     f" AND kind IN ({','.join('?' for _ in TEST_KINDS)}) ORDER BY finished DESC",
                     learner, *TEST_KINDS):
        if _gated(r):
            continue
        est = (_json(r["result"], {}) or {}).get("estimate")
        if not isinstance(est, dict) or est.get("low") is None:
            continue
        out.append({"low": est["low"], "high": est["high"], "mid": (est["low"] + est["high"]) / 2,
                    "kind": r["kind"], "session": r["id"], "at": r["finished"],
                    "capped": bool(est.get("capped")), "route": est.get("route") or r["route"]})
        if len(out) == limit:
            break
    return out


def latest_score(learner: str) -> dict | None:
    got = scores(learner, 1)
    return got[0] if got else None


def outside(learner: str) -> list[dict]:
    return [dict(r) for r in db.rows("SELECT id, day, math, rw, source, at FROM outside_scores WHERE learner=?"
                                     " ORDER BY day DESC, at DESC", learner)]


def add_outside_score(learner: str, day: str, math_score: int, rw: int | None = None,
                      source: str = "official", tz: int = 0) -> dict:
    """File a Bluebook, official or other score; S7 records the exam result
    through this. 422 names the field."""
    if source not in SOURCES:
        raise HTTPException(422, f"source is one of {', '.join(SOURCES)}")
    if math_score not in TARGETS:
        raise HTTPException(422, "math is a score from 200 to 800 in tens")
    if rw is not None and rw not in TARGETS:
        raise HTTPException(422, "rw is a score from 200 to 800 in tens")
    try:
        if not isinstance(day, str) or not DATE_OK.match(day):
            raise ValueError
        d = dt.date.fromisoformat(day)
    except ValueError:
        raise HTTPException(422, "day is YYYY-MM-DD")
    if d > _local_today(tz) or d < FIRST_SCORE_DAY:
        raise HTTPException(422, "day is on or before today")
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).isoformat()
    if db.one("SELECT COUNT(*) n FROM outside_scores WHERE learner=? AND at>=?", learner, since)["n"] >= SCORES_A_DAY:
        raise HTTPException(429, f"at most {SCORES_A_DAY} added scores a day")
    row = {"id": secrets.token_hex(8), "learner": learner, "day": day, "math": math_score, "rw": rw,
           "source": source, "at": drill.deps.now()}
    with db.transaction():
        db.ensure_learner(learner)
        db.run("INSERT INTO outside_scores (id, learner, day, math, rw, source, at) VALUES (?,?,?,?,?,?,?)",
               *row.values())
    return {k: v for k, v in row.items() if k != "learner"}


# ------------------------------------------------------------------ the core cards

def study(p: dict, d: dict, t: dt.date) -> dict:
    """Today, this week (Monday to Sunday), this month, from progress.days (R13)."""
    rows = {r["day"]: r for r in d["days"]}
    mon = _monday(t)
    week = [rows[x] for x in ((mon + dt.timedelta(days=i)).isoformat() for i in range((t - mon).days + 1)) if x in rows]
    month = [r for k, r in rows.items() if k[:7] == t.isoformat()[:7]]
    today_row = rows.get(t.isoformat()) or {"minutes": 0, "questions": 0, "right": 0, "fixed": 0,
                                           "words": 0, "rest": False}
    goal = p.get("minutes")
    pattern = p.get("days") if p.get("days") and len(p["days"]) == 7 else "1111111"
    left = sum(pattern[(t + dt.timedelta(days=i)).weekday()] == "1" for i in range(7 - t.weekday()))

    def active(r):
        return bool(r["questions"] or r["words"] >= 10 or r["tests"] or r.get("official"))

    return {"today": today_row["minutes"], "week": sum(r["minutes"] for r in week),
            "month": sum(r["minutes"] for r in month), "active_days_month": sum(active(r) for r in month),
            "questions_today": today_row["questions"], "right_today": today_row["right"],
            "fixed_today": today_row["fixed"], "words_today": today_row["words"], "rest_today": today_row["rest"],
            "goal": goal, "week_goal": goal * pattern.count("1") if goal else None, "week_days_left": left,
            "goal_met": {"n": sum(r["minutes"] >= goal for r in d["recent"]), "of": len(d["recent"])} if goal else None}


def domains(learner: str) -> list[dict]:
    """Each domain with its topics; domain mastery is the mean over answered topics."""
    b = progress.board(learner)
    out = []
    for name in progress.DOMAINS:
        ts = [v for v in b.values() if v["domain"] == name]
        seen = [v for v in ts if v["answered"]]
        out.append({"domain": name,
                    "mastery": round(statistics.mean(v["mastery"] for v in seen), 3) if seen else 0.0,
                    "answered": sum(v["answered"] for v in ts),
                    "right": sum(round((v["accuracy"] or 0) * v["answered"]) for v in ts),
                    "traps": sum(len(v["traps"]) for v in ts),
                    "topics": [{"topic": v["topic"], "name": v["name"], "mastery": v["mastery"],
                                "answered": v["answered"], "accuracy": v["accuracy"], "traps": len(v["traps"])}
                               for v in ts]})
    return out


def _group_gain(learner: str, topics) -> int | None:
    """U4's one change for a set of skills raised to 80% (never a sum of gains)."""
    rows = estimate._rows(learner)
    if len(rows) < estimate.MIN_ANSWERS or not topics:
        return None
    m = estimate.model(rows)
    return estimate._round5(estimate._lift(m, [x for x in topics if x in m["skills"]]))


def _trap_row(x: dict, blind: dict) -> dict:
    return {"id": x["id"], "label": x["label"], "topic": x["topic"], "template": x["template"],
            "hits": x["hits"], "owed": x["owed"], "last": x["last"], "relapses": x["relapses"] or 0,
            "blind": blind[x["id"]]["why"] if x["id"] in blind else None,
            "learn": bool((x["relapses"] or 0) >= 1 or x["hits"] >= 3)}


def _trap_group(learner: str, group: list[dict], blind: dict, **extra) -> dict:
    ids = [x["id"] for x in group]
    return {"n": len(group), "rows": [_trap_row(x, blind) for x in group],
            "fix": {"n": 2 * len({x["template"] for x in group}), "body": {"pool": "redo", "ids": ids}} if ids else None,
            **extra}


def traps(learner: str, tz: int, t: dt.date, open_list: list[dict], stage: dict | None,
          gains: dict | None = None, exam_date: str | None = None) -> dict:
    """Review's card on Today (R30): counts, blind spots first, the top 5;
    in the final stretch (T13) every open trap in two visible groups: worth
    fixing now (skills with 2+ a test, by gain) and rare skills."""
    blind = progress.blind(learner)
    order = sorted(open_list, key=lambda x: (x["hits"], x["last"]), reverse=True)
    order = [x for x in order if x["id"] in blind] + [x for x in order if x["id"] not in blind]
    today0, week0 = _start(t, tz), _start(_monday(t), tz)
    fixed = db.rows("SELECT closed FROM traps WHERE learner=? AND closed>=? AND closed_how IN ('fixed','transfer')",
                    learner, week0)
    out = {"open": len(open_list), "templates": len({x["template"] for x in open_list}),
           "fixed_today": sum(r["closed"] >= today0 for r in fixed), "fixed_week": len(fixed),
           "opened_today": db.one("SELECT COUNT(*) n FROM traps WHERE learner=? AND opened>=?", learner, today0)["n"],
           "blind": [x["id"] for x in order if x["id"] in blind],
           "top": [_trap_row(x, blind) for x in order[:5]],
           "habits": _call("habits", "of_learner", learner) or [], "now": None, "rare": None}
    if stage and stage.get("mode") in ("stretch", "taper", "eve"):
        shares = estimate.shares()
        gain = {x["topic"]: x["raw"] for x in (gains or {}).get("skills", [])}
        now = sorted((x for x in order if 44 * shares.get(x["topic"], 0) >= 2), key=lambda x: -gain.get(x["topic"], 0))
        now_ids = {x["id"] for x in now}
        out["now"] = _trap_group(learner, now, blind, gain=_group_gain(learner, {x["topic"] for x in now}))
        out["rare"] = _trap_group(learner, [x for x in order if x["id"] not in now_ids], blind, until=exam_date)
    return out


def open_sittings(learner: str) -> dict:
    """The newest unfinished drill worth continuing, how many others, and the
    newest unfinished test with its server clock (the clock keeps running)."""
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=OPEN_DRILL_HOURS)).isoformat()
    drills = []
    for r in db.rows("SELECT * FROM sessions WHERE learner=? AND kind='drill' AND finished IS NULL"
                     " AND abandoned IS NULL AND started>=? ORDER BY started DESC", learner, since):
        cfg = _json(r["cfg"], {})
        answered = len(db.load_answers(r))
        if cfg.get("inline") or cfg.get("source") in ("try", "quick") or not answered or drill.overtime(r, cfg):
            continue
        secs = drill.seconds_of(cfg)
        elapsed = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(r["started"])).total_seconds()
        drills.append({"id": r["id"], "topics": cfg.get("topics", []), "answered": answered,
                       "total": cfg.get("total"), "timed": bool(secs), "source": cfg.get("source"),
                       "seconds_left": max(0, int(secs - elapsed)) if secs else None, "started": r["started"]})
    test = None
    from .api_tests import mock_module, questions_of, remaining
    for r in db.rows(f"SELECT * FROM sessions WHERE learner=? AND finished IS NULL AND abandoned IS NULL"
                     f" AND kind IN ({','.join('?' for _ in TEST_KINDS)}) ORDER BY started DESC LIMIT 5",
                     learner, *TEST_KINDS):
        cfg = _json(r["cfg"], {})
        try:
            qs = mock_module(r) if r["kind"] == "mock" else questions_of(r)
            left = None if cfg.get("timed") is False or cfg.get("timing") == "untimed" else remaining(r)
        except (KeyError, TypeError, ValueError):
            continue
        ids = {q["id"] for q in qs}
        test = {"id": r["id"], "kind": r["kind"], "module": r["module"] or 1, "section": r["kind"] == "mock",
                "answered": sum(1 for k in db.load_answers(r) if k in ids), "asked": len(qs),
                "timed": left is not None, "seconds_left": left, "started": r["started"],
                "paused": bool(r["paused_at"])}
        break
    return {"drill": drills[0] if drills else None, "drills": max(0, len(drills) - 1), "test": test}


def week(learner: str, tz: int, d: dict, t: dt.date) -> dict:
    """This week against last, and the skills that moved since Monday."""
    rows = {r["day"]: r for r in d["days"]}
    mon = _monday(t)

    def span(first: dt.date, days: int, until: str) -> dict:
        got = [rows.get((first + dt.timedelta(days=i)).isoformat()) for i in range(days)]
        got = [r for r in got if r]
        opened = db.one("SELECT COUNT(*) n FROM traps WHERE learner=? AND opened>=? AND opened<?",
                        learner, _start(first, tz), until)["n"]
        return {"questions": sum(r["questions"] for r in got), "right": sum(r["right"] for r in got),
                "minutes": sum(r["minutes"] for r in got), "fixed": sum(r["fixed"] for r in got), "opened": opened}

    this = span(mon, (t - mon).days + 1, "9999")
    last = span(mon - dt.timedelta(days=7), 7, _start(mon, tz))
    before = _mastery_at(learner, _start(mon, tz))
    now_m = {k: v["mastery"] for k, v in progress.board(learner).items() if v["answered"]}
    delta = [(k, before.get(k, 0.0), m) for k, m in now_m.items() if abs(m - before.get(k, 0.0)) >= 0.05]
    up = sorted((x for x in delta if x[2] > x[1]), key=lambda x: x[1] - x[2])[:3]
    down = sorted((x for x in delta if x[2] < x[1]), key=lambda x: x[2] - x[1])[:2]
    return {"this": this, "last": last,
            "moved": [{"topic": k, "before": round(b, 3), "now": round(m, 3)} for k, b, m in up + down]}


def warmup(learner: str, tz: int, t: dt.date, stage: dict | None) -> dict:
    """T3: what is due for a spaced return, and how today's and this month's held."""
    c = progress.warmup_candidates(learner, tz)
    size = 8 if stage and stage.get("mode") in ("stretch", "taper") else 5
    rows = db.rows("SELECT a.correct, a.repeat, a.flagged, a.guess, a.topic, a.at FROM attempts AS a"
                   " JOIN sessions AS s ON s.id=a.session WHERE a.learner=? AND a.repair=0 AND s.kind='drill'"
                   " AND json_extract(s.cfg,'$.source') IN ('due','warmup') AND a.at>=?",
                   learner, _start(t.replace(day=1), tz))

    def held(r):
        return r["correct"] and not (r["repeat"] or r["flagged"] or r["guess"])

    today0 = _start(t, tz)
    mine = [r for r in rows if r["at"] >= today0]
    return {"checks": len(c["checks"]), "fading": len(c["fading"]), "keep_warm": len(c["keep_warm"]),
            "marked": len(c["marked"]), "due": c["size"], "size": min(size, c["size"]), "nominal": size,
            "today": {"held": sum(bool(held(r)) for r in mine), "of": len(mine),
                      "slipped": sorted({r["topic"] for r in mine if not r["correct"]})} if mine else None,
            "month": {"held": sum(bool(held(r)) for r in rows), "of": len(rows)}}


def _day_marks(learner: str, tz: int, first: dt.date, last: dt.date) -> dict[str, dict]:
    """Per local day: mistakes fixed and check-ins held (T18's week strip,
    T17's calendar), from the trap log."""
    out: dict[str, dict] = {}
    for r in db.rows("SELECT at, event FROM trap_log WHERE learner=? AND at>=? AND at<? AND event IN ('fixed','check_ok')",
                     learner, _start(first, tz), _start(last + dt.timedelta(days=1), tz)):
        got = out.setdefault(progress._local_day(r["at"], tz).isoformat(), {"fixed": 0, "held": 0})
        got["fixed" if r["event"] == "fixed" else "held"] += 1
    return out


PLAN_MEMO_S = 120
_plan_memo: dict[tuple, tuple] = {}
_PLAN_READS = (   # what plan.payload reads, as one cheap fingerprint
    "SELECT (SELECT MAX(id) FROM attempts WHERE learner=?), (SELECT MAX(id) FROM word_reviews WHERE learner=?),"
    " (SELECT COUNT(*) || ':' || COALESCE(MAX(started), '') || ':' || COALESCE(MAX(finished), '')"
    "  FROM sessions WHERE learner=?),"
    " (SELECT COALESCE(updated, '') || cfg FROM plans WHERE id=?),"
    " (SELECT group_concat(day || task || COALESCE(status, '') || COALESCE(to_day, '') || COALESCE(at, ''))"
    "  FROM plan_marks WHERE plan=?),"
    " (SELECT group_concat(id || COALESCE(removed, '') || COALESCE(minutes, '') || COALESCE(title, ''))"
    "  FROM plan_tasks WHERE plan=?),"
    " (SELECT group_concat(day || COALESCE(minutes, '') || COALESCE(off, '') || COALESCE(test, '')"
    "  || COALESCE(topics, '')) FROM plan_overrides WHERE plan=?),"
    " (SELECT COUNT(*) || ':' || COALESCE(MAX(last), '') || ':' || COALESCE(MAX(closed), '') FROM traps WHERE learner=?),"
    " (SELECT COALESCE(prefs, '') || COALESCE(exam_date, '') || COALESCE(target, '') || COALESCE(minutes, '')"
    "  FROM learners WHERE id=?)")


def plan_payload(learner: str, tz: int, pid: str, t: dt.date) -> dict:
    """S7's whole plan (about a second on a 60-day plan), memoised on a
    fingerprint of the rows it reads, so /api/today stays quick between writes.
    ponytail: the fingerprint misses a test's unsaved answers; bounded by
    PLAN_MEMO_S. Upgrade: a cheap plan.card(learner, tz) from S7."""
    fp = tuple(db.one(_PLAN_READS, learner, learner, learner, pid, pid, pid, pid, learner, learner))
    key = (learner, tz, t.isoformat())
    now = time.monotonic()
    hit = _plan_memo.get(key)
    if hit and hit[0] == fp and now - hit[1] < PLAN_MEMO_S:
        return hit[2]
    got = _call("plan", "payload", learner, tz) or {}
    if len(_plan_memo) > 512:
        _plan_memo.clear()
    _plan_memo[key] = (fp, now, got)
    return got


def plan_part(learner: str, tz: int, t: dt.date | None = None) -> dict | None:
    """S7's day (R14), with the plan's own start (plans.start, R15), its weeks
    and days, and the Plan card's figures (T18): Day N of M, % done, on time,
    the pace verdict, what being behind cost, and what moved since the start."""
    s = _call("plan", "today_summary", learner, tz)
    if not s:
        return None
    t = t or _local_today(tz)
    out = dict(s)
    out["next_start"] = s.get("start")
    row = db.one("SELECT start, cfg FROM plans WHERE id=?", s.get("id"))
    out["start"] = row["start"] if row else None
    cfg = _json(row["cfg"], {}) if row else {}
    out["exam_date"] = cfg.get("exam_date")
    whole = plan_payload(learner, tz, s.get("id"), t)
    out["weeks"] = whole.get("weeks")
    out["stats"] = whole.get("stats")
    iso = t.isoformat()
    marks = _day_marks(learner, tz, dt.date.fromisoformat(out["start"]), t) if out["start"] else {}
    days = []
    for d in whole.get("days") or []:
        counted = [x for x in d.get("tasks") or [] if x.get("counted")]
        days.append({"date": d.get("date"), "kind": d.get("kind"), "test": d.get("test"), "phase": d.get("phase"),
                     "minutes": d.get("minutes"), "minutes_done": d.get("minutes_done"), "status": d.get("status"),
                     "tasks_done": d.get("tasks_done"), "tasks_counted": len(counted),
                     "questions": sum(x.get("count") or 0 for x in counted),
                     "topics": list(dict.fromkeys(tp for x in counted for tp in x.get("topics") or [])),
                     **(marks.get(d.get("date"), {"fixed": 0, "held": 0}) if (d.get("date") or "") <= iso else {})})
    out["days"] = days
    study = [d for d in days if d["kind"] in ("practice", "test")]
    past = [d for d in study if d["date"] < iso]
    if out["start"] and out["exam_date"]:
        first, exam = dt.date.fromisoformat(out["start"]), dt.date.fromisoformat(out["exam_date"])
        done = sum(d["status"] in ("done", "made_up") for d in study)
        out["card"] = {"day": (t - first).days + 1, "of": (exam - first).days + 1,
                       "pct": round(100 * done / len(study)) if study else 0,
                       "study_days_done": done, "study_days": len(study),
                       "on_time": {"n": sum(d["status"] == "done" for d in past), "of": len(past)}}
    out["pace"] = (whole.get("verdict") or {}).get("math")
    out["suggest"] = whole.get("suggest")
    behind = whole.get("behind")
    if behind:
        ten = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=10)).isoformat()
        behind = {**behind, "cost": {
            "missed": behind.get("planned", 0) - behind.get("done", 0),
            "overdue_checks": db.one("SELECT COUNT(*) n FROM traps WHERE learner=? AND closed IS NOT NULL"
                                     " AND due IS NOT NULL AND due<?", learner, iso)["n"],
            "old_mistakes": db.one("SELECT COUNT(*) n FROM traps WHERE learner=? AND closed IS NULL AND opened<?",
                                   learner, ten)["n"]},
            "catch_up": {"box": 15}}
    out["behind"] = behind
    # what moved since the start: each skill's mastery now against its mastery before the plan began
    before = _mastery_at(learner, _start(dt.date.fromisoformat(out["start"]), tz)) if out["start"] else {}
    now_m = {k: v["mastery"] for k, v in progress.board(learner).items() if v["answered"]}
    moved = sorted(((k, m - before.get(k, 0.0)) for k, m in now_m.items()), key=lambda kv: -abs(kv[1]))
    out["moved"] = [{"topic": k, "delta": round(x, 2)} for k, x in moved if abs(x) >= 0.05][:3]
    return out


def plan_draft(learner: str, tz: int, p: dict, t: dt.date, d: dict, score_list: list[dict]) -> dict:
    """T18's Build with these: Plan step 1's source (the mean of 2+ sittings
    in 45 days, the latest one, practice only, or a new student), the SAT
    date, the daily minutes, the days studied, and a target that is never silent."""
    cut = t - dt.timedelta(days=45)
    gated = {r["id"] for r in db.rows("SELECT id FROM sessions WHERE learner=? AND kind='diagnostic'"
                                      " AND user_id IS NULL", learner)}           # R38
    items = [x for x in estimate._sittings(learner)
             if dt.date.fromisoformat(x["at"][:10]) >= cut and x["id"] not in gated]
    answers = db.one("SELECT COUNT(*) n FROM attempts WHERE learner=?", learner)["n"]
    if len(items) >= 2:
        mean = estimate._mean3(items)
        source = {"kind": "mean3", "value": estimate._round10(mean), "n": min(3, len(items))}
    elif items:
        x = items[0]
        source = {"kind": "latest", "value": estimate._round10(x["mid"]), "low": x["low"], "high": x["high"],
                  "at": x["at"], "sitting_kind": x.get("kind"), "session": x.get("id")}
    else:
        source = {"kind": "practice" if answers else "new", "value": None}
    recent = [r for r in d["days"] if r["day"] > (t - dt.timedelta(days=28)).isoformat()]
    avg = sum(r["minutes"] for r in d["days"] if r["day"] > (t - dt.timedelta(days=7)).isoformat()) / 7
    studied = {dt.date.fromisoformat(r["day"]).weekday() for r in recent if r["questions"] or r["tests"]}
    days = "".join("1" if i in studied else "0" for i in range(7)) if studied else "1111100"
    start = source["value"]
    band_high = score_list[0]["high"] if score_list else None
    target = p.get("target") or (min(800, estimate._round10(band_high + 50)) if band_high else
                                 min(800, start + 100) if start else None)
    upcoming = satdates.upcoming(t + dt.timedelta(days=1))
    return {"source": source, "current": start, "target": target,
            "target_from": "profile" if p.get("target") else "band" if band_high else "start" if start else None,
            "exam_date": p.get("exam_date") or (upcoming[0] if upcoming else None),
            "minutes": p.get("minutes") or max(20, 15 * round(avg / 15)), "days": p.get("days") or days,
            "ready": start is not None}


def usual_start(learner: str, tz: int) -> str | None:
    """T17: the median local start of sittings over 30 days, to five minutes."""
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)).isoformat()
    starts = sorted(x.hour * 60 + x.minute for x in (
        dt.datetime.fromisoformat(r["started"]) - dt.timedelta(minutes=tz)
        for r in db.rows("SELECT started FROM sessions WHERE learner=? AND started>=? AND abandoned IS NULL",
                         learner, since)))
    if not starts:
        return None
    m = 5 * round(statistics.median_low(starts) / 5) % 1440
    return f"{m // 60:02d}:{m % 60:02d}"


def review_counts(learner: str, tz: int, t: dt.date) -> dict:
    """Review's counts (S10) for the card, or the same four from the tables."""
    got = _call("api_review", "counts", learner, tz)
    if isinstance(got, dict):
        return got
    row = db.one("SELECT COUNT(*) AS open, SUM(owed=1) AS half FROM traps WHERE learner=? AND closed IS NULL", learner)
    return {"open": row["open"], "half": row["half"] or 0,
            "due": len(progress.due_rechecks(learner, t.isoformat())),
            "marked": db.one("SELECT COUNT(*) n FROM flags WHERE learner=?", learner)["n"]}


def challenge_today(learner: str, tz: int, t: dt.date) -> dict:
    """The day's challenge sitting for the Due row: the contest (S8) or v2's."""
    day = t.isoformat()
    r = db.one("SELECT * FROM sessions WHERE learner=? AND ((kind='challenge' AND day=?) OR contest=?)"
               " ORDER BY started DESC LIMIT 1", learner, day, f"daily-{day}")
    if not r:
        return {"started": False, "done": False, "answered": 0, "total": challenge.CHALLENGE_SIZE, "id": None}
    cfg = _json(r["cfg"], {})
    secs = drill.seconds_of(cfg)
    elapsed = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(r["started"])).total_seconds()
    res = _json(r["result"], {}) or {}
    return {"started": True, "done": bool(r["finished"]), "answered": len(db.load_answers(r)),
            "total": cfg.get("total") or challenge.CHALLENGE_SIZE, "id": r["id"],
            "seconds_left": max(0, int(secs - elapsed)) if secs and not r["finished"] else None,
            "right": res.get("right")}


def qotd_today(learner: str, tz: int) -> dict:
    t = daily.today(tz)
    shown = daily.shown(t)
    m = daily.marks(learner, t, shown)
    streak = daily.qotd_streak(learner, tz)
    return {"day": t, "slots": len(shown), "answered": sum(v is not None for v in m.values()), "marks": m,
            "streak": streak["current"], "best": streak["best"]}


def _local_hour(tz: int) -> int:
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).hour


def stage(learner: str, tz: int, p: dict, t: dt.date, plan: dict | None = None) -> dict | None:
    """T13's mode from the exam date: next.stage (F2) when it exists. With a
    plan, its Final phase's test days are the rehearsals (no second schedule).
    ponytail: the fallback goes once server/next.py lands."""
    got = _call("next", "stage", learner, tz)
    if got is not None or part("next", "stage"):
        return got
    if not p.get("exam_date"):
        return None
    exam = dt.date.fromisoformat(p["exam_date"])
    days = (exam - t).days
    mode = ("after" if days < 0 or (days == 0 and _local_hour(tz) >= 13) else "exam" if days == 0 else
            "eve" if days == 1 else "taper" if days <= 7 else "stretch" if days <= 14 else None)
    if mode is None:
        return {"mode": None, "days": days, "rehearsals": [], "sweep": None, "rare": None, "scores_by": None}
    sats = [exam - dt.timedelta(days=n) for n in range(6, 15) if (exam - dt.timedelta(days=n)).weekday() == 5]
    row = db.one("SELECT start, cfg FROM plans WHERE id=?", plan.get("id")) if plan else None
    if row:
        dates = _call("plan", "_rehearsal_dates", _json(row["cfg"], {}), dt.date.fromisoformat(row["start"]))
        if dates is not None:
            sats = [x for x in dates if exam - dt.timedelta(days=14) <= x < exam]
    rehearsals = []
    for s in sorted(sats)[-2:]:
        done = db.one("SELECT 1 FROM sessions WHERE learner=? AND kind IN ('mock','section','paper')"
                      " AND finished>=? AND finished<?", learner, _start(s, tz), _start(s + dt.timedelta(days=1), tz))
        rehearsals.append({"day": s.isoformat(), "done": bool(done)})
    began = exam - dt.timedelta(days=14)
    cut = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=90)).isoformat()
    closed = db.rows("SELECT id, template FROM traps WHERE learner=? AND closed>=? AND closed_how IN ('fixed','transfer')",
                     learner, cut)
    # a trap is swept once any attempt on its template comes after the stretch began
    last = {r["template"]: r["at"] for r in db.rows(
        "SELECT template, MAX(at) at FROM attempts WHERE learner=? AND at>=? GROUP BY template",
        learner, _start(began, tz))}
    swept = [c for c in closed if c["template"] in last]
    today0 = _start(t, tz)
    study_left = max(1, (exam - t).days - 1)
    return {"mode": mode, "days": days, "rehearsals": rehearsals,
            "sweep": {"total": len(closed), "done": len(swept),
                      "done_today": sum(last[c["template"]] >= today0 for c in swept),
                      "today": math.ceil(max(0, len(closed) - len(swept)) / study_left)},
            "rare": None, "scores_by": satdates.entry(p["exam_date"])["scores_by"] if mode == "after" else None}


def strongest(learner: str, n: int = 3) -> list[str]:
    b = progress.board(learner)
    return [k for k, v in sorted(b.items(), key=lambda kv: -kv[1]["mastery"]) if v["answered"]][:n]


def queue_fallback(learner: str, t: dt.date, open_: dict, plan: dict | None, st: dict | None) -> list[dict]:
    """Up next's first items while next.queue (F2) is not there (§3a 1-3 and
    T13): a running test, an unfinished set, the plan's test, then the
    stage's rehearsal, the eve's light warm-up, exam morning, after the exam.
    ponytail: replaced by next.queue as soon as server/next.py lands."""
    items = []
    x = open_["test"]
    if x:
        out = x["timed"] and x["seconds_left"] == 0
        title = (f"Time's up on module {x['module']}" if out else f"Section · module {x['module']} in progress"
                 if x["section"] else f"{progress_kind(x['kind'])} in progress")
        items.append({"kind": "test", "title": title, "href": f"/test/?s={x['id']}",
                      "action": ("Continue to module 2" if x["section"] and x["module"] == 1 else "See results")
                      if out else "Resume", **{k: x[k] for k in ("id", "answered", "asked", "timed", "seconds_left")}})
    d = open_["drill"]
    if d:
        items.append({"kind": "resume", "title": "Continue", "action": "Continue", "href": f"/practice/session/?id={d['id']}",
                      "more": open_["drills"], **{k: d[k] for k in ("id", "answered", "total", "timed", "seconds_left", "topics")}})
    test = next((x for x in (plan or {}).get("tasks") or [] if x.get("kind") == "test" and x.get("status") not in FINISHED), None)
    if test:
        items.append({"kind": "plan", "test": True, "title": test.get("title"), "action": "Start test",
                      "start": test.get("start"), "task_id": test.get("id"), "minutes": test.get("minutes")})
    mode = (st or {}).get("mode")
    if mode in ("stretch", "taper") and not test and any(r["day"] == t.isoformat() and not r["done"] for r in st["rehearsals"]):
        items.append({"kind": "rehearsal", "action": "Start section", "time": None,
                      "title": "Dress rehearsal · full Math section · 44 q · 70 min · at the time your Math section"
                               " will start (after R&W and the break)",
                      "helper": "On test day Math starts after Reading and Writing (64 min) and a 10-minute break.",
                      "start": {"path": "/api/mock/new", "body": {"kind": "section", "timing": "official"}}})
    if mode in ("eve", "exam"):
        eve = mode == "eve"
        body = {"count": 5, "tiers": ["easy", "medium"] if eve else ["easy"], "timed": False, "source": "today"}
        top = strongest(learner)
        items.append({"kind": mode, "action": "Start",
                      "title": "Light warm-up · 5 from your strongest skills · ~8 min" if eve else
                               "Warm-up · 5 easy · untimed · ~7 min",
                      "then": "Done for today. Sleep does more than cramming now." if eve else None,
                      "start": {"path": "/api/drill", "body": {**body, **({"topics": top} if top else {})}}})
    if mode == "after":
        by = st.get("scores_by")
        items.append({"kind": "after", "action": "Add your official score", "scores_by": by,
                      "title": f"How did it go? Scores come out around {_short(by)}" if by else "How did it go?"})
    return items


def stretch_coach(coach: dict, st: dict | None) -> dict:
    """T13: no new rare skills in the final stretch, and never "New skills"
    as the reason; the rare ones are named with what they are worth."""
    if not st or st.get("mode") not in ("stretch", "taper", "eve") or coach.get("why") != "new":
        return coach
    shares, names = estimate.shares(), progress.topics()

    def rare(topic):
        return 44 * shares.get(topic, 0) < 2

    groups = [coach.get("topics") or []] + list(coach.get("ahead") or [])
    keep = next(([x for x in g if not rare(x)] for g in groups if any(not rare(x) for x in g)), [])
    dropped = [x for x in coach.get("topics") or [] if rare(x)]
    return {**coach, "topics": keep, "why": "stretch_new",
            "suppressed": [{"topic": x, "per_test": round(44 * shares.get(x, 0), 1),
                            "text": f"Not starting {names[x].name if x in names else x}: about"
                                    f" {44 * shares.get(x, 0):.1f} of 44 a test, {st['days']} days left."}
                           for x in dropped]}


def next_part(learner: str, tz: int, p: dict, coach: dict, st: dict | None, plan: dict | None,
              study_: dict, due_: dict, open_: dict, t: dt.date) -> dict:
    """Up next (T1): next.queue's items, the Size row's defaults, and the
    preview of the default box once next.resolve_drill makes one."""
    goal = p.get("minutes")
    if (goal and study_["today"] >= goal) or (due_["total"] and due_["done"] == due_["total"]):
        default = 15
    elif plan and plan.get("minutes_left"):
        default = plan["minutes_left"]
    elif goal:
        default = goal - study_["today"]
    else:
        default = 15
    default = min(BOX_OPTIONS, key=lambda o: (abs(o - default), o))
    if st and st.get("mode") == "taper":
        default = min(default, 30)
    count = coach.get("count") or 10
    preview = None
    if part("next", "resolve_drill"):
        try:
            preview = drill.preview(learner, {"source": "next", "box": default})
        except HTTPException:
            preview = None
    items = _call("next", "queue", learner, tz, limit=6) if part("next", "queue") else \
        queue_fallback(learner, t, open_, plan, st)
    return {"items": items or [],
            "box": {"default": default, "options": list(BOX_OPTIONS)},
            "count": {"default": count, "options": list(dict.fromkeys([5, 10, 22, count])) + [None]},
            "preview": preview, "stage": st}


FINISHED = ("done", "marked", "made_up", "skipped", "moved")
PLAN_OWN_ROWS = ("recheck", "sweep", "words", "qotd", "challenge")     # plan tasks that are rows 4 to 8


def _row(key: str, kind: str, title: str | None, tag: str, minutes, status: str, **extra) -> dict:
    """One Due row in T2's full shape, so no key is ever missing on the client."""
    out = {"key": key, "kind": kind, "title": title, "tag": tag, "meta": None,
           "minutes": math.ceil(minutes) if minutes else 0, "progress": None, "due_at": None,
           "status": status, "why": [], "evidence_href": None, "start": None, "href": None,
           "result": None, "fix": None, "alternatives": None, "task_id": None, "own": False,
           "marked": False, "group": "also"}
    out.update(extra)
    return out


def session_result(learner: str, sid: str | None) -> dict | None:
    """A sitting's result for its done row: answered, right, and the mistakes
    it fixed and opened (a relapse counts as opened)."""
    if not sid:
        return None
    a = db.one("SELECT COUNT(*) n, SUM(correct) r FROM attempts WHERE session=? AND repair=0", sid)
    if not a["n"]:
        return None
    ev = {r["event"]: r["n"] for r in db.rows(
        "SELECT event, COUNT(*) n FROM trap_log WHERE learner=? AND event IN ('open','relapse','fixed')"
        " AND attempt IN (SELECT id FROM attempts WHERE session=?) GROUP BY event", learner, sid)}
    return {"answered": a["n"], "right": a["r"] or 0, "fixed": ev.get("fixed", 0),
            "opened": ev.get("open", 0) + ev.get("relapse", 0), "session": sid}


def _fix(res: dict | None) -> dict | None:
    """`Fix the N it opened`: the sitting's still-open misses as fresh questions."""
    if not res or not res["opened"]:
        return None
    return {"n": res["opened"], "path": "/api/drill",
            "body": {"from_session": res["session"], "still_open": True, "scope": "misses"}}


def _plan_row(learner: str, task: dict, kind: str = "plan", **over) -> dict:
    status = task.get("status") or "todo"
    why = task.get("why") or []
    topic = (task.get("topics") or [None])[0]
    href = next((w.get("href") for w in why if isinstance(w, dict) and w.get("href")), None)
    res = session_result(learner, task.get("session"))
    row = _row(f"plan:{task.get('id')}", kind, task.get("title"), task.get("kind"), task.get("minutes"), status,
               progress={"have": task.get("answered") or 0, "of": task.get("total")},
               why=[w.get("text") if isinstance(w, dict) else str(w) for w in why],
               evidence_href=href or (f"/review/?tab=redo&topic={topic}" if topic else None),
               start=task.get("start"), result=res, fix=_fix(res),
               alternatives=task.get("alternatives") or None, task_id=task.get("id"),
               own=task.get("kind") == "custom",
               marked=status == "marked" or (task.get("kind") == "custom" and status == "done"),   # a tick is a mark
               group="plan" if task.get("counted") else "also", detail=task.get("detail"))
    row.update(over)
    return row


def review_done(learner: str, tz: int, t: dt.date) -> bool:
    """T2: today's review run is finished, or every check-in due today has
    been answered (none is left due and one was answered today)."""
    today0 = _start(t, tz)
    if db.one("SELECT 1 FROM sessions WHERE learner=? AND kind='drill' AND finished>=?"
              " AND json_extract(cfg,'$.source') IN ('due','warmup')", learner, today0):
        return True
    return not progress.due_rechecks(learner, t.isoformat()) and bool(db.one(
        "SELECT 1 FROM trap_log WHERE learner=? AND at>=? AND event IN ('check_ok','relapse')", learner, today0))


def due_fallback(learner: str, tz: int, p: dict, open_: dict, plan: dict | None, warm: dict,
                 words: dict | None, qotd: dict, chal: dict, secs: float, st: dict | None = None,
                 t: dt.date | None = None) -> dict:
    """T2's rows while next.due (F2) is not there, in its order: a running
    test, the plan's tasks, Review (R56: check-ins, fading and keep-warm; the
    plan's recheck is this row), the sweep, Words (the plan's words task is
    this row), the day's questions, the challenge, contests closing today.
    ponytail: replaced by next.due as soon as server/next.py lands."""
    t = t or _local_today(tz)
    rows = []
    if open_["test"]:
        x = open_["test"]
        rows.append(_row(f"test:{x['id']}", "test", "Section" if x["section"] else progress_kind(x["kind"]), "Test",
                         (x["seconds_left"] or 0) / 60, "progress", progress={"have": x["answered"], "of": x["asked"]},
                         href=f"/test/?s={x['id']}"))
    own: dict[str, dict] = {}
    for task in (plan or {}).get("tasks") or []:
        if task.get("kind") in PLAN_OWN_ROWS:
            own.setdefault(task["kind"], task)
        else:
            rows.append(_plan_row(learner, task))
    # 4. Review (R56)
    box = (p.get("prefs") or {}).get("review_minutes", 10)
    done_review = review_done(learner, tz, t)
    task = own.get("recheck")
    if warm["due"] or task or done_review:
        mins = warm["due"] * secs / 60
        mins = min(mins, box) if box else mins
        meta = f"{warm['due']} due · ~{math.ceil(mins)} min · {warm['checks']} check-ins · {warm['fading']} fading"
        today_ = warm["today"] or {"held": 0, "of": 0, "slipped": []}
        extra = dict(meta=meta, progress={"have": today_["of"], "of": max(warm["due"] + today_["of"], today_["of"])},
                     why=["Questions you got right before, back just as you start to forget them."],
                     evidence_href="/review/?tab=checks",
                     start={"path": "/api/drill", "body": {"source": "due", "box": box}},
                     result=warm["today"])
        if task:
            extra["start"] = {"path": "/api/drill", "body": {"source": "due", "box": box, "task": task.get("id")}}
            rows.append(_plan_row(learner, task, "review", title="Review", tag="Review", minutes=math.ceil(mins),
                                  **{k: v for k, v in extra.items() if k != "result"}))
        else:
            rows.append(_row("review", "review", "Review", "Review", mins, "done" if done_review else "todo", **extra))
    # 5. Sweep (T13, final stretch only)
    mode = (st or {}).get("mode")
    sweep = (st or {}).get("sweep") or {}
    if own.get("sweep"):
        rows.append(_plan_row(learner, own["sweep"], "sweep"))
    elif mode in ("stretch", "taper") and (sweep.get("today") or sweep.get("done_today")):
        n = sweep.get("today") or 0
        rows.append(_row("sweep", "sweep", f"Sweep · {n} of {sweep['total']} fixed mistakes today", "Sweep",
                         n * secs / 60, "done" if sweep.get("done_today", 0) >= n else "todo",
                         progress={"have": sweep.get("done_today", 0), "of": n},
                         why=["Every mistake you fixed in the last 90 days gets one fresh twin before the SAT."],
                         start={"path": "/api/drill", "body": {"pool": "checks", "sweep": True, "count": max(1, n)}}))
    # 6. Words (R56)
    task = own.get("words")
    if words and (words.get("due") or task or (_call("words", "minutes_today", learner, tz) or 0) > 0):
        new = (words.get("preview") or {}).get("new", 0)
        meta = f"{words.get('due', 0)} due · {new} new · ~{math.ceil(words.get('minutes') or 0)} min"
        base = dict(title="Words", tag="Words", meta=meta, minutes=math.ceil(words.get("minutes") or 0),
                    why=[words.get("reason")] if words.get("reason") else [], start=words.get("start"),
                    evidence_href="/words/")
        if task:
            base.pop("start")                       # the plan's own start carries its task tag
            rows.append(_plan_row(learner, task, "words", **base))
        else:
            rows.append(_row("words", "words", base.pop("title"), base.pop("tag"), base.pop("minutes"),
                             "done" if words.get("done") else "todo", **base))
    elif task:
        rows.append(_plan_row(learner, task, "words"))
    # 7. The day's questions, 8. the challenge, 9. contests closing today
    task = own.get("qotd")
    rows.append(_row("qotd", "qotd", "The day's questions", "Day's questions", qotd["slots"] * secs / 60,
                     "done" if qotd["answered"] == qotd["slots"] else "progress" if qotd["answered"] else "todo",
                     meta=f"{qotd['answered']} of {qotd['slots']}",
                     progress={"have": qotd["answered"], "of": qotd["slots"]},
                     why=[f"The same {qotd['slots']} for everyone, one try each"], href="/#qotd",
                     result={"marks": qotd["marks"]} if qotd["answered"] else None,
                     task_id=task.get("id") if task else None))
    task = own.get("challenge")
    rows.append(_row("challenge", "challenge", "Daily challenge", "Challenge", CHALLENGE_S / 60,
                     "done" if chal["done"] else "progress" if chal["started"] else "todo",
                     progress={"have": chal["answered"], "of": chal["total"]},
                     why=["10 question types · the same for everyone, your own numbers · ranked by right answers,"
                          " then time"],
                     start={"path": "/api/challenge/start", "body": {}}, href="/compete/contest/?id=daily",
                     result={"right": chal.get("right"), "asked": chal["total"], "session": chal["id"]}
                     if chal["done"] else None, task_id=task.get("id") if task else None))
    for c in _call("compete", "due_today", learner, tz) or []:
        rows.append(_row(f"contest:{c['id']}", "contest", c.get("title"), "Contest", CHALLENGE_S / 60, "todo",
                         due_at=c.get("closes"), href=f"/compete/contest/?id={c['id']}"))
    rows.sort(key=lambda r: r["status"] in FINISHED)
    undone = [r for r in rows if r["status"] not in FINISHED]
    return {"rows": rows, "minutes_left": sum(r["minutes"] for r in undone),
            "goal_minutes": p.get("minutes"), "done": len(rows) - len(undone), "total": len(rows), "source": "today"}


# ------------------------------------------------------------------ T19: brief, at risk, receipt

def _local_time(at: str, tz: int) -> str:
    local = dt.datetime.fromisoformat(at) - dt.timedelta(minutes=tz)
    return local.strftime("%I:%M %p").lstrip("0")


def _short(day: str) -> str:
    return dt.date.fromisoformat(day[:10]).strftime("%b %d").replace(" 0", " ")


def brief(learner: str, tz: int, d: dict, t: dt.date, score_list: list[dict]) -> list[dict]:
    """Up to 3 facts, most urgent first, each a link to its place."""
    facts = []
    for c in _call("compete", "closing_soon", learner, tz) or []:
        facts.append({"kind": "contest", "text": f"{c.get('title')} closes at {_local_time(c['closes'], tz)}",
                      "href": f"/compete/contest/?id={c['id']}"})
    due = progress.due_rechecks(learner, t.isoformat())
    if due:
        ages = sorted({(t - progress._local_day(x["due"] + "T12:00:00+00:00", 0)).days + CHECK_AGE.get(x["checks"], 3)
                       for x in due})
        when = f"{ages[0]} days ago" if len(ages) == 1 else f"{ages[0]} to {ages[-1]} days ago"
        n = len(due)
        facts.append({"kind": "checks", "text": f"{n} mistake{'s' if n > 1 else ''} you fixed {when}"
                      f" {'are' if n > 1 else 'is'} due a check-in", "href": "#mist"})
    active = [r for r in d["days"] if r["day"] < t.isoformat() and (r["questions"] or r["words"] >= 10 or r["tests"])]
    last = active[-1] if active else None
    since = _start(dt.date.fromisoformat(last["day"]), tz) if last else None
    if score_list and since and score_list[0]["at"] >= since:
        s = score_list[0]
        prev = score_list[1] if len(score_list) > 1 else None
        delta = f" · {round(s['mid'] - prev['mid']):+d}" if prev else ""
        facts.append({"kind": "score", "text": f"{progress_kind(s['kind'])} on {_short(s['at'])}: {s['low']}–{s['high']}{delta}",
                      "href": f"/results/report/?id={s['session']}"})
    elif last:                              # an added Bluebook or official score counts as news too
        o = db.one("SELECT day, math, source FROM outside_scores WHERE learner=? AND day>=? ORDER BY day DESC, at DESC"
                   " LIMIT 1", learner, last["day"])
        if o:
            label = {"official": "Official SAT", "bluebook": "Bluebook test"}.get(o["source"], "Added score")
            facts.append({"kind": "score", "text": f"{label} on {_short(o['day'])}: {o['math']}", "href": "#score"})
    if last:
        label = "Yesterday" if last["day"] == (t - dt.timedelta(days=1)).isoformat() else \
            f"Since {dt.date.fromisoformat(last['day']).strftime('%a')}"
        goal = profile_minutes(learner)
        parts = [f"{last['minutes']} of {goal} min" if goal else f"{last['minutes']} min"]
        if last["fixed"]:
            parts.append(f"{last['fixed']} mistake{'s' if last['fixed'] > 1 else ''} fixed")
        you = challenge.board(last["day"], learner, limit=0)["you"]
        if you:
            parts.append(f"challenge #{you['rank']} of {challenge.board(last['day'], None, limit=0)['players']}")
        facts.append({"kind": "yesterday", "text": f"{label}: {' · '.join(parts)}", "href": "#study"})
        lo, hi = _start(dt.date.fromisoformat(last["day"]), tz), _start(dt.date.fromisoformat(last["day"]) + dt.timedelta(days=1), tz)
        before, after = _mastery_at(learner, lo), _mastery_at(learner, hi)
        names = progress.topics()
        counted = {r["topic"]: r["n"] for r in db.rows("SELECT topic, COUNT(*) n FROM attempts WHERE learner=?"
                                                       " AND at<? GROUP BY topic", learner, hi)}
        for topic, m in sorted(after.items(), key=lambda kv: -kv[1]):
            was = _word(before.get(topic, 0.0), 1 if topic in before else 0)
            now_w = _word(m, counted.get(topic, 0))
            if now_w != was and topic in names and m > before.get(topic, 0.0):
                facts.append({"kind": "moved", "text": f"{names[topic].name} is now {now_w}",
                              "href": f"/practice/?topics={topic}"})
                break
    return facts[:3]


CHECK_AGE = {0: 3, 1: 10, 2: 30}     # R9: a check-in comes this many days after the fix


def progress_kind(kind: str) -> str:
    return {"mock": "Section", "module": "Module", "diagnostic": "Diagnostic", "section": "Section",
            "paper": "Weekly paper", "custom": "Custom test"}.get(kind, kind.title())


def profile_minutes(learner: str) -> int | None:
    row = db.one("SELECT minutes FROM learners WHERE id=?", learner)
    return row["minutes"] if row else None


def at_risk(learner: str, tz: int, d: dict, t: dt.date, coach: dict) -> dict | None:
    """After 18:00 with nothing done today, a streak of 2+, not a rest day."""
    now = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)
    row = next((r for r in d["days"] if r["day"] == t.isoformat()), None)
    if now.hour < 18 or not row or row["rest"] or d["streak"] < 2 or \
            row["questions"] or row["words"] >= 10 or row["tests"] or row.get("official"):
        return None
    due = progress.due_rechecks(learner, t.isoformat())
    body = ({"pool": "checks", "ids": [due[0]["trap_id"]], "count": 1, "source": "try"} if due else
            {"topics": coach.get("topics", [])[:1], "count": 1, "source": "try"})
    midnight = dt.datetime.combine(t + dt.timedelta(days=1), dt.time())
    return {"streak": d["streak"], "left_ms": int((midnight - now.replace(tzinfo=None)).total_seconds() * 1000),
            "start": {"path": "/api/drill", "body": body}, "spare": d.get("spares", 0) > 0}


def receipt(learner: str, tz: int, d: dict, t: dt.date, p: dict, due_: dict) -> dict | None:
    """The day's receipt, once the Due list is all done or the goal is met."""
    row = next((r for r in d["days"] if r["day"] == t.isoformat()), None)
    goal = p.get("minutes")
    if not row or not ((due_["total"] and due_["done"] == due_["total"]) or (goal and row["minutes"] >= goal)):
        return None
    midnight = _start(t, tz)
    before, after = _mastery_at(learner, midnight), _mastery_at(learner, "9999")
    counted = {r["topic"]: r["n"] for r in db.rows("SELECT topic, COUNT(*) n FROM attempts WHERE learner=?"
                                                   " GROUP BY topic", learner)}
    today_topics = {r["topic"] for r in db.rows("SELECT DISTINCT topic FROM attempts WHERE learner=? AND at>=?",
                                                learner, midnight)}
    moved = []
    for topic in sorted(today_topics):
        was, now_w = _word(before.get(topic, 0.0), 1 if topic in before else 0), _word(after.get(topic, 0.0), counted.get(topic, 0))
        if was != now_w:
            moved.append({"topic": topic, "from": was, "to": now_w})
    fixed = [r["label"] for r in db.rows("SELECT label FROM traps WHERE learner=? AND closed>=?"
                                         " AND closed_how IN ('fixed','transfer') ORDER BY closed", learner, midnight)]
    log = {r["event"]: r["n"] for r in db.rows("SELECT event, COUNT(*) n FROM trap_log WHERE learner=? AND at>=?"
                                               " AND event IN ('check_ok','relapse') GROUP BY event", learner, midnight)}
    claimed = estimate.practice_delta(learner, midnight)
    return {"minutes": row["minutes"], "questions": row["questions"], "right": row["right"], "moved": moved,
            "fixed": fixed, "checks": {"held": log.get("check_ok", 0), "of": log.get("check_ok", 0) + log.get("relapse", 0)},
            "relapses": log.get("relapse", 0), "claimed": claimed["pts"], "claimed_raw": claimed.get("raw"),
            "streak": d["streak"], "best": d["best"]}


# ------------------------------------------------------------------ T12 / T17: the workload

def _chip(minutes: float) -> int:
    """Rounded up to a goal chip, never under the smallest (15)."""
    return next((c for c in GOAL_CHIPS if c >= minutes), GOAL_CHIPS[-1])


def workload(learner: str, tz: int, p: dict, t: dt.date, d: dict, open_count: int, warm: dict,
             gains: dict | None, secs: float, plan_days: list[dict] | None = None) -> dict | None:
    """Capacity against need to the exam's eve, including the target's skill
    work (estimate.need(target).path). Sized only with 30 answers and a target.
    Capacity is the plan's own days when there is a plan, else the daily goal
    on the study days, else the last 7 days' average."""
    if not p.get("exam_date"):
        return None
    exam = dt.date.fromisoformat(p["exam_date"])
    pattern = p.get("days") if p.get("days") and len(p["days"]) == 7 else None
    days = [t + dt.timedelta(days=i) for i in range(max(0, (exam - t).days - 1))]   # today to the eve's eve
    study_days = [x for x in days if not pattern or pattern[x.weekday()] == "1"]
    lo, hi = t.isoformat(), (exam - dt.timedelta(days=1)).isoformat()
    planned = [x for x in plan_days or [] if lo <= (x.get("date") or "") < hi and x.get("kind") in ("practice", "test")]
    if planned:
        study_days = planned
        capacity = int(sum(x.get("minutes") or 0 for x in planned) * 60)
        per_day = capacity / len(planned)
    else:
        if p.get("minutes"):
            per_day = p["minutes"] * 60
        else:
            week_rows = d["recent"][-7:]
            per_day = sum(r["minutes"] for r in week_rows) * 60 / 7
        capacity = int(per_day * len(study_days))
    answers = db.one(f"SELECT COUNT(*) n FROM attempts WHERE learner=? AND {progress.COUNTED}", learner)["n"]
    unsized = "answers" if gains is None else "target" if not p.get("target") else None
    checks = db.one("SELECT COUNT(*) n FROM traps WHERE learner=? AND closed IS NOT NULL AND due IS NOT NULL"
                    " AND due<?", learner, exam.isoformat())["n"]
    tests_per_week = {"daily": 7, "twice": 2, "weekly": 1, "none": 0}.get(p.get("tests") or "", None)
    if planned:                                     # the plan's test days, each at its own clock
        clocks = [SECTION_S if x.get("test") in ("section", "mock", "rehearsal") else MODULE_S
                  for x in planned if x.get("test") or x.get("kind") == "test"]
        tests, test_s = len(clocks), sum(clocks)
    elif tests_per_week is not None:
        tests = math.ceil(len(study_days) / 7 * tests_per_week) if tests_per_week < 7 else len(study_days)
        test_s = tests * MODULE_S
    else:                                           # T13's rehearsals: the Saturdays 6 to 14 days out
        tests = min(2, sum(1 for n in range(6, 15) if (exam - dt.timedelta(days=n)).weekday() == 5
                           and exam - dt.timedelta(days=n) >= t))
        test_s = tests * SECTION_S
    need = {"traps": int(open_count * 2 * secs), "checks": int(checks * secs), "tests": test_s,
            "tests_n": tests, "warmups": int(warm.get("nominal", 5) * secs * len(study_days)), "target": None,
            "traps_n": open_count, "checks_n": checks, "secs": round(secs)}
    if p.get("target") and gains is not None:
        n = estimate.need(p["target"], learner)
        path = n.get("path") or {}
        need["target"] = {"target": p["target"], "skills": path.get("skills", []),
                          "minutes": path.get("minutes", 0), "reachable": bool(path.get("reachable", n["reachable"])),
                          "right_of_44": n.get("right_of_44"), "now_of_44": n.get("now_of_44")}
    total = need["traps"] + need["checks"] + need["tests"] + need["warmups"] + \
        (need["target"]["minutes"] * 60 if need["target"] else 0)
    out = {"study_days": len(study_days), "capacity": capacity, "per_day": int(per_day), "sized": unsized is None,
           "unsized": unsized, "answers": {"have": answers, "of": estimate.MIN_ANSWERS}, "need": need,
           "total": total, "fits": None, "short_by": None, "add_per_day": None, "suggest_minutes": None}
    if unsized is None and study_days:
        reachable = not need["target"] or need["target"]["reachable"]
        out["fits"] = reachable and capacity >= total
        out["short_by"] = max(0, total - capacity)
        out["add_per_day"] = math.ceil(out["short_by"] / 60 / len(study_days)) if out["short_by"] else 0
        out["suggest_minutes"] = _chip(total / 60 / len(study_days))
    return out


def _dur(minutes: float) -> str:
    """42h 10m, 45m, 6h (the design rules' durations)."""
    m = int(round(minutes))
    h, m = divmod(m, 60)
    return f"{h}h {m}m" if h and m else f"{h}h" if h else f"{m}m"


def goal_suggest(w: dict | None) -> dict | None:
    """T17: the suggested daily goal and its arithmetic, in words; null
    exactly when unsized."""
    if not w or not w["sized"] or w["suggest_minutes"] is None:
        return None
    n = w["need"]
    parts = {"traps": n["traps"], "checks": n["checks"], "tests": n["tests"], "warmups": n["warmups"],
             "target": n["target"]["minutes"] * 60 if n["target"] else 0}
    secs = n.get("secs") or 95
    terms = []
    if n.get("traps_n") or n.get("checks_n"):
        inner = " + ".join(x for x in (f"{n['traps_n']} mistakes × 2" if n.get("traps_n") else "",
                                       f"{n['checks_n']} check-ins" if n.get("checks_n") else "") if x)
        terms.append(f"({inner}) at {secs // 60}:{secs % 60:02d} each ({_dur((n['traps'] + n['checks']) / 60)})")
    if n["tests_n"]:
        terms.append(f"{n['tests_n']} test{'s' if n['tests_n'] > 1 else ''} ({_dur(n['tests'] / 60)})")
    if n["warmups"]:
        terms.append(f"warm-ups ({_dur(n['warmups'] / 60)})")
    if n["target"]:
        terms.append(f"reach {n['target']['target']} (at least {_dur(n['target']['minutes'])})")
    per_day = w["total"] / 60 / max(1, w["study_days"])
    arithmetic = (f"{' + '.join(terms) or 'nothing left'} = {_dur(w['total'] / 60)} ÷ {w['study_days']} study days"
                  f" ≈ {round(per_day)} min → {w['suggest_minutes']} min")
    return {"minutes": w["suggest_minutes"], "study_days": w["study_days"], "total": w["total"],
            "per_day": round(per_day), "parts": parts, "arithmetic": arithmetic,
            "target": n["target"]["target"] if n["target"] else None}


# ------------------------------------------------------------------ GET /api/today

def exam_part(p: dict, t: dt.date) -> dict | None:
    """The exam date with its official deadlines (U17): register by, late by,
    scores by, and the registration line while it applies."""
    if not p.get("exam_date"):
        return None
    e = satdates.entry(p["exam_date"])
    return {"date": p["exam_date"], "days": (dt.date.fromisoformat(p["exam_date"]) - t).days,
            "official": p["exam_date"] in satdates.SAT_DATES,
            "register_by": e["register_by"], "late_by": e["late_by"], "scores_by": e["scores_by"],
            "registration": satdates.registration(p["exam_date"], (p.get("prefs") or {}).get("registered"), t)}


def readiness(learner: str, tz: int, t: dt.date, doms: list[dict]) -> list[dict]:
    """T13's readiness per domain: Ready (Strong, no open mistake on a skill
    with 2+ a test, answered in the last 7 days), Shaky (such mistakes, or
    mastery under 0.6), Untested for 14 days; else close. Each with a 10-minute box."""
    shares = estimate.shares()
    last = {r["topic"]: r["at"] for r in db.rows("SELECT topic, MAX(at) at FROM attempts WHERE learner=? GROUP BY topic",
                                                learner)}
    out = []
    for d in doms:
        topics = [x["topic"] for x in d["topics"]]
        seen = max((last[x] for x in topics if x in last), default=None)
        ago = (t - progress._local_day(seen, tz)).days if seen else None
        big = sum(x["traps"] for x in d["topics"] if 44 * shares.get(x["topic"], 0) >= 2)
        state = ("untested" if ago is None or ago >= 14 else "shaky" if big or d["mastery"] < 0.6 else
                 "ready" if d["mastery"] >= progress.STRONG and ago <= 7 else "close")
        out.append({"domain": d["domain"], "state": state, "open": d["traps"], "open_big": big,
                    "mastery": d["mastery"], "days_since": ago,
                    "start": {"path": "/api/drill", "body": {"topics": topics, "box": 10, "source": "today"}}})
    return out


def today_payload(learner: str, tz: int) -> dict:
    p = profile(learner, tz)
    d = progress.days(learner, tz, 6)
    t = dt.date.fromisoformat(d["today"])
    today0 = _start(t, tz)
    tested = bool(db.one("SELECT 1 FROM sessions WHERE learner=? AND kind IN ('mock','module') AND finished>=?",
                         learner, today0)) or bool(db.one("SELECT 1 FROM outside_scores WHERE learner=? AND day=?",
                                                          learner, t.isoformat()))
    plan = plan_part(learner, tz, t)
    st = stage(learner, tz, p, t, plan)
    coach = stretch_coach(progress.coach(learner, count=per_session(p)), st)
    open_list = progress.open_traps(learner)
    score_list = scores(learner)
    gains = estimate.gains(learner)
    tr = traps(learner, tz, t, open_list, st, gains, p.get("exam_date"))
    if st and tr["rare"] is not None and not st.get("rare"):
        st["rare"] = {"n": tr["rare"]["n"], "ids": tr["rare"]["fix"]["body"]["ids"] if tr["rare"]["fix"] else [],
                      "until": p.get("exam_date")}
    words = _call("words", "today_summary", learner, tz)
    open_ = open_sittings(learner)
    warm = warmup(learner, tz, t, st)
    study_ = study(p, d, t)
    qotd = qotd_today(learner, tz)
    chal = challenge_today(learner, tz, t)
    secs = _median_s(learner)
    due_ = _call("next", "due", learner, tz) or due_fallback(learner, tz, p, open_, plan, warm, words, qotd, chal,
                                                            secs, st, t)
    work = workload(learner, tz, p, t, d, len(open_list), warm, gains, secs, (plan or {}).get("days"))
    review = review_counts(learner, tz, t)
    box = (p.get("prefs") or {}).get("review_minutes", 10)
    review["start"] = {"path": "/api/drill", "body": {"source": "due", "box": box}, "minutes": box}
    doms = domains(learner)
    exam = exam_part(p, t)
    if exam and st and st.get("mode") in ("stretch", "taper", "eve", "exam"):
        exam["readiness"] = readiness(learner, tz, t, doms)
    return {
        "profile": p, "days": d, "exam": exam, "tested": tested,
        "score": score_list[0] if score_list else None,
        "coach": coach, "mistakes": len(open_list),
        "study": study_, "scores": score_list, "outside": outside(learner), "domains": doms,
        "traps": tr, "open": open_, "week": week(learner, tz, d, t),
        "warmup": warm, "plan": plan, "draft": None if plan else plan_draft(learner, tz, p, t, d, score_list),
        "review": review, "words": words,
        "qotd": qotd, "challenge": chal, "seconds_per_question": round(secs),
        "next": next_part(learner, tz, p, coach, st, plan, study_, due_, open_, t), "due": due_,
        "brief": brief(learner, tz, d, t, score_list), "at_risk": at_risk(learner, tz, d, t, coach),
        "receipt": receipt(learner, tz, d, t, p, due_), "workload": work, "goal_suggest": goal_suggest(work),
        "usual_start": None if (p.get("prefs") or {}).get("study_time") else usual_start(learner, tz),
        "assets": helper_assets(),
    }


HELPERS = ("plan-ui", "results-ui", "compete-ui", "words-ui")
ASSETS = Path(__file__).resolve().parent.parent / "web" / "assets"


def helper_assets() -> list[str]:
    """The section helper files that exist (S6, S7, S8, S9's *-ui.js), so the page
    loads only those and a missing one is no 404 in the console (§2.9: consumers
    degrade until the provider lands)."""
    return [n for n in HELPERS if (ASSETS / f"{n}.js").exists()]


@router.get("/api/today")
def get_today(x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    return today_payload(learner_of(x_learner), x_tz)


@router.get("/api/today/need")
def get_target_need(target: int = Query(..., ge=200, le=800),
                    x_learner: str | None = Header(default=None)) -> dict:
    """The target slider's right answers out of 44, at any valid Math target."""
    if target not in TARGETS:
        raise HTTPException(422, "target is a Math score from 200 to 800 in tens")
    return estimate.need(target, learner_of(x_learner))


# ------------------------------------------------------------------ GET /api/today/insights

def _pace_extras(learner: str, pace: dict, tz: int) -> dict:
    """T8's additions to progress.pace: the cost, slow-but-right skills,
    rushing, tests that ran out, and the accuracy guard."""
    fc = pace["forecast"]
    slow = sorted(({"topic": k, "median_ms": s["median_ms_right"] or s["median_ms"], "accuracy": s["accuracy"],
                    "n": s["n"]} for k, s in pace["skills"].items() if k in pace["quadrants"]["slow_right"]),
                  key=lambda x: -x["median_ms"])[:3]
    week0 = _start(_monday(_local_today(tz)), tz)
    fast = db.rows("SELECT topic FROM attempts WHERE learner=? AND at>=? AND correct=0 AND repeat=0"
                   " AND COALESCE(ms, sms) < 20000", learner, week0)
    top = statistics.mode([r["topic"] for r in fast]) if fast else None
    tests = {"modules": 0, "ran_out": 0, "blanks": 0}
    for r in db.rows(f"SELECT * FROM sessions WHERE learner=? AND finished IS NOT NULL AND abandoned IS NULL"
                     f" AND kind IN ({','.join('?' for _ in TEST_KINDS)}) ORDER BY finished DESC LIMIT 4",
                     learner, *TEST_KINDS):
        cfg = _json(r["cfg"], {})
        if cfg.get("timed") is False or cfg.get("timing") == "untimed":
            continue
        answers = _json(r["answers"], {})
        blanks = sum(1 for q in progress._paper(r) if answers.get(q["id"]) in (None, ""))
        tests["modules"] += 2 if r["kind"] in ("mock", "section", "paper") else 1
        tests["ran_out"] += int(blanks > 0)
        tests["blanks"] += blanks
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=60)).isoformat()
    timed = db.one(f"SELECT COUNT(*) n FROM attempts AS a JOIN sessions AS s ON s.id=a.session WHERE a.learner=?"
                   f" AND a.at>=? AND (s.kind IN ({','.join('?' for _ in TEST_KINDS)},'challenge')"
                   " OR json_extract(s.cfg,'$.timed')=1)", learner, since, *TEST_KINDS)["n"]
    guard = []
    three = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=3)).isoformat()
    for s in db.rows("SELECT id FROM sessions WHERE learner=? AND kind='drill' AND finished>=?"
                     " AND json_extract(cfg,'$.source')='pace'", learner, three):
        for r in db.rows("SELECT topic, AVG(correct) acc FROM attempts WHERE session=? AND repair=0 GROUP BY topic", s["id"]):
            usual = db.one(f"SELECT AVG(correct) acc FROM attempts WHERE learner=? AND topic=? AND session!=?"
                           f" AND repair=0 AND {progress.COUNTED}", learner, r["topic"], s["id"])["acc"]
            if usual is not None and usual - r["acc"] >= 0.15 and r["topic"] not in guard:
                guard.append(r["topic"])
    return {"strip": fc["strip"], "runs_out_at": fc["runs_out_at"], "blanks": fc["blanks"],
            "seconds": fc["seconds"], "limit": fc["limit"], "pts_lost": estimate.time_cost(learner, pace),
            "slow_right": slow, "rushing": {"n": len(fast), "topic": top,
                                            "n_topic": sum(r["topic"] == top for r in fast)},
            "tests": tests, "timed_answers": timed,
            "week_before_ms": None,     # needs progress.pace(until=): F4 follow-up
            "guard": guard}


def early_projection(points: list[tuple[dt.date, float]], to_day: dt.date, half_latest: float) -> dict | None:
    """T10's verdict from 2 scored sittings in 60 days a week apart, while
    U9's cone waits for 3 over 21 days: estimate.project's own shrunk slope
    and taper, with the latest band's half-width.
    ponytail: goes once estimate.projection starts at 2 sittings (F4)."""
    got = estimate.project(points, to_day, half_latest)
    if got:
        return got
    points = sorted(points)
    n = len(points)
    if n < 2 or (points[-1][0] - points[0][0]).days < 7:
        return None
    x = [(d - points[0][0]).days / 7 for d, _ in points]
    y = [v for _, v in points]
    xb, yb = sum(x) / n, sum(y) / n
    b = sum((xi - xb) * (yi - yb) for xi, yi in zip(x, y)) / sum((xi - xb) ** 2 for xi in x)
    b2 = b * n / (n + 3)
    w = max(0.0, (to_day - points[-1][0]).days / 7)
    mid_ = max(200.0, min(800.0, yb + b2 * (x[-1] - xb) + b2 * min(w, 4) + max(-20.0, min(20.0, b2)) * max(w - 4, 0)))
    half = max(60, min(150, estimate._round10(half_latest)))
    return {"mid": round(mid_), "low": max(200, round(mid_ - half)), "high": min(800, round(mid_ + half)),
            "half": half, "slope": round(b, 1), "slope_used": round(b2, 1), "n": n, "to": to_day.isoformat(),
            "label": "If this pace held", "early": True}


def _points(learner: str, since: dt.date, before: dt.date | None = None) -> tuple[list, float]:
    """Scored standard sittings (our tests) from `since`, and the newest one's half-width."""
    items = [x for x in estimate._sittings(learner) if x["standard"] and not x["outside"]
             and since <= dt.date.fromisoformat(x["at"][:10]) and (before is None or x["at"][:10] < before.isoformat())]
    half = (items[0]["high"] - items[0]["low"]) / 2 if items else 0
    return [(dt.date.fromisoformat(x["at"][:10]), x["mid"]) for x in items], half


def _estimate_block(learner: str, tz: int, p: dict) -> dict:
    """T10: practice since the last test, evidence per domain, the projection
    and its verdict (in words), calibration against an official score."""
    t = _local_today(tz)
    score_list = scores(learner)
    latest = score_list[0] if score_list else None
    delta = estimate.practice_delta(learner, latest["at"]) if latest else None
    if delta:
        delta["show"] = abs(delta["pts"]) >= 5 and delta["answers"] >= 20
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=60)).isoformat()
    names = progress.topics()
    evidence = {name: 0 for name in progress.DOMAINS}
    for r in db.rows(f"SELECT topic, COUNT(*) n FROM attempts WHERE learner=? AND at>=? AND repair=0"
                     f" AND {progress.COUNTED} GROUP BY topic", learner, since):
        if r["topic"] in names:
            evidence[names[r["topic"]].domain] = evidence.get(names[r["topic"]].domain, 0) + r["n"]
    exam = dt.date.fromisoformat(p["exam_date"]) if p.get("exam_date") else None
    proj = estimate.projection(learner)
    if proj is None and exam:
        pts, half = _points(learner, t - dt.timedelta(days=60))
        proj = early_projection(pts, exam, half)
    target = p.get("target")
    made = proj.get("slope_used") if proj else None
    needs = None
    if latest and target and latest["low"] >= target:
        kind, text = "at_target", "At your target ✓"
    elif proj is None:
        kind, text = "not_enough", "Not enough to project yet · 2 scored sittings in 60 days start it"
    elif target and exam:
        weeks = max(1 / 7, (exam - t).days / 7)
        needs = round((target - (latest["mid"] if latest else proj["mid"])) / weeks, 1)
        if proj["mid"] >= target:
            kind, text = "on_pace", f"On pace: about {proj['low']}–{proj['high']} on {_short(proj['to'])} · target {target}"
        else:
            kind, text = "behind", (f"Behind: on pace for {proj['low']}–{proj['high']} · {target} needs"
                                    f" {needs:+.0f} a week, you're making {made:+.0f}")
    else:
        kind, text = "projected", f"If this pace held: about {proj['low']}–{proj['high']} on {_short(proj['to'])}"
    calibration = None
    o = db.one("SELECT * FROM outside_scores WHERE learner=? AND source='official' AND day>=? ORDER BY day DESC LIMIT 1",
               learner, exam.isoformat()) if exam and exam <= t else None
    if o:                                   # recomputed from the sittings before the exam date: nothing stored
        pts, half = _points(learner, exam - dt.timedelta(days=90), exam)
        pr = early_projection(pts, exam, half)
        if pr:
            calibration = {"projected": {"low": pr["low"], "high": pr["high"]}, "score": o["math"], "day": o["day"],
                           "exam_date": exam.isoformat(), "inside": pr["low"] <= o["math"] <= pr["high"],
                           "text": f"We projected {pr['low']}–{pr['high']} for {_short(exam.isoformat())}"
                                   f" · you scored {o['math']}"}
    standard = sum(1 for x in estimate._sittings(learner) if x["standard"] and not x["outside"]
                   and (t - dt.date.fromisoformat(x["at"][:10])).days <= 90)
    return {"latest": latest, "practice_delta": delta, "evidence": evidence,
            "thin": [k for k, n in evidence.items() if n < 15], "projection": proj, "verdict": text,
            "verdict_kind": kind, "made_per_week": made, "needs_per_week": needs, "calibration": calibration,
            "standard_sittings": standard, "confidence": estimate.estimate(learner)["confidence"]}


def time_split(learner: str, tz: int, gains: dict | None) -> dict:
    """T17: this week's minutes by domain and by kind of work, against the
    test's share and the share of points on the table."""
    names = progress.topics()
    week0 = _start(_monday(_local_today(tz)), tz)
    by_domain = {name: 0.0 for name in progress.DOMAINS}
    kinds = {"new": 0.0, "fix": 0.0, "review": 0.0, "test": 0.0}
    for r in db.rows("SELECT a.topic, COALESCE(a.ms, a.sms) AS t, a.repair, s.kind, s.cfg FROM attempts AS a"
                     " LEFT JOIN sessions AS s ON s.id=a.session WHERE a.learner=? AND a.at>=?", learner, week0):
        m = min(max(r["t"] or 0, 0), progress.MS_CAP) / 60_000
        if r["topic"] in names:
            by_domain[names[r["topic"]].domain] += m
        cfg = _json(r["cfg"], {})
        if r["kind"] in TEST_KINDS:
            kinds["test"] += m
        elif r["repair"] or cfg.get("pool") in ("redo", "checks") or cfg.get("source") in ("mistakes", "try", "twin"):
            kinds["fix"] += m
        elif cfg.get("pool") in ("review", "seen", "history", "saved", "marked") or cfg.get("source") in ("due", "review"):
            kinds["review"] += m
        else:
            kinds["new"] += m
    pts = {x["domain"]: max(0, x["gain"]) for x in (gains or {}).get("by_domain", [])}
    total_pts = sum(pts.values())
    return {"domains": {k: round(v, 1) for k, v in by_domain.items()}, "kinds": {k: round(v, 1) for k, v in kinds.items()},
            "minutes": round(sum(by_domain.values()), 1), "test_share": dict(progress.BLUEPRINT),
            "points_share": {k: round(v / total_pts, 3) for k, v in pts.items()} if total_pts else None}


@router.get("/api/today/insights")
def get_insights(subject: str | None = Query(default=None), x_learner: str | None = Header(default=None),
                 x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    subject = subject_param(subject)
    pace = progress.pace(learner, subject=subject)
    gains = estimate.gains(learner, subject)
    out = {"subject": subject, "gains": gains, "causes": progress.causes(learner, x_tz, subject=subject),
           "pace": {**pace, **_pace_extras(learner, pace, x_tz)} if subject == "math" else pace,
           "estimate": None, "time_split": None,
           "answers": db.one(f"SELECT COUNT(*) n FROM attempts WHERE learner=? AND {progress.COUNTED}", learner)["n"]}
    if subject == "math":
        out["estimate"] = _estimate_block(learner, x_tz, profile(learner, x_tz))
        out["time_split"] = time_split(learner, x_tz, gains)
    return out


# ------------------------------------------------------------------ GET /api/calendar

MONTH_OK = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


@router.get("/api/calendar")
def get_calendar(month: str = Query(...), x_learner: str | None = Header(default=None),
                 x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    tz = x_tz
    t = _local_today(tz)
    if not MONTH_OK.match(month):
        raise HTTPException(422, "month is YYYY-MM")
    first = dt.date(int(month[:4]), int(month[5:]), 1)
    ahead = (first.year - t.year) * 12 + first.month - t.month
    if first < FIRST_SCORE_DAY or ahead > 12:
        raise HTTPException(422, "month is between 2020-01 and 12 months from now")
    nxt = dt.date(first.year + first.month // 12, first.month % 12 + 1, 1)
    last = nxt - dt.timedelta(days=1)
    # ponytail: progress.days reaches back 53 weeks; older months read zeros until it takes a start date
    weeks = min(53, max(1, math.ceil(((t - first).days + 1) / 7)))
    d = progress.days(learner, tz, weeks)
    rows = {r["day"]: r for r in d["days"]}
    lo, hi = _start(first, tz), _start(nxt, tz)
    per: dict[str, dict] = {}

    def bucket(at: str) -> dict:
        return per.setdefault(progress._local_day(at, tz).isoformat(),
                              {"topics": {}, "first_at": None, "last_at": None, "missed": [],
                               "opened": [], "closed": [], "sittings": []})

    for a in db.rows("SELECT id, topic, correct, repeat, repair, disputed, void, at FROM attempts WHERE learner=?"
                     " AND at>=? AND at<? ORDER BY at", learner, lo, hi):
        b = bucket(a["at"])
        tp = b["topics"].setdefault(a["topic"], {"topic": a["topic"], "right": 0, "asked": 0})
        tp["asked"] += 1
        tp["right"] += a["correct"]
        b["first_at"] = b["first_at"] or a["at"]
        b["last_at"] = a["at"]
        if not a["correct"] and not (a["repeat"] or a["repair"] or a["disputed"] or a["void"]):
            b["missed"].append(a["id"])
    for tr in db.rows("SELECT id, label, opened, closed, closed_how FROM traps WHERE learner=?"
                      " AND ((opened>=? AND opened<?) OR (closed>=? AND closed<?))", learner, lo, hi, lo, hi):
        if lo <= tr["opened"] < hi:
            bucket(tr["opened"])["opened"].append({"id": tr["id"], "label": tr["label"]})
        if tr["closed"] and lo <= tr["closed"] < hi and tr["closed_how"] in ("fixed", "transfer"):
            bucket(tr["closed"])["closed"].append({"id": tr["id"], "label": tr["label"]})
    for s in db.rows("SELECT * FROM sessions WHERE learner=? AND finished>=? AND finished<? AND abandoned IS NULL"
                     " AND kind!='words' ORDER BY finished", learner, lo, hi):
        cfg, res = _json(s["cfg"], {}), _json(s["result"], {}) or {}
        if cfg.get("inline") or not res.get("asked") and s["kind"] not in TEST_KINDS:
            continue
        gated = _gated(s)
        est = None if gated else res.get("estimate")
        rank = None
        if s["kind"] == "challenge" and s["day"]:
            you = challenge.board(s["day"], learner, limit=0)["you"]
            rank = you["rank"] if you else None
        bucket(s["finished"])["sittings"].append(
            {"id": s["id"], "kind": s["kind"], "source": cfg.get("source"), "right": None if gated else res.get("right"),
             "asked": res.get("asked"), "estimate": {"low": est["low"], "high": est["high"]} if isinstance(est, dict)
             and est.get("low") is not None else None, "rank": rank, "gated": gated})
    qotd = daily.by_day(learner)
    held = _day_marks(learner, tz, first, min(last, t))
    forecast ={f["day"]: f for f in progress.due_forecast(learner, tz, (last - t).days)} if last > t else {}
    days, totals = [], {"minutes": 0, "questions": 0, "right": 0, "active_days": 0}
    for i in range((last - first).days + 1):
        day = first + dt.timedelta(days=i)
        key = day.isoformat()
        r = rows.get(key) or {"questions": 0, "right": 0, "minutes": 0, "practice": 0, "tests": 0, "words": 0,
                              "fixed": 0, "rest": False, "spare_used": False, "official": 0}
        extra = per.get(key, {})
        row = {"day": key, "questions": r["questions"], "right": r["right"], "minutes": r["minutes"],
               "practice": r["practice"], "tests": r["tests"], "words": r["words"], "fixed": r["fixed"],
               "held": held.get(key, {}).get("held", 0), "rest": r["rest"], "spare_used": r.get("spare_used", False),
               "qotd": daily.marks(learner, key, None, qotd),
               "sittings": extra.get("sittings", []), "opened": extra.get("opened", []),
               "closed": extra.get("closed", []), "topics": list(extra.get("topics", {}).values()),
               "first_at": extra.get("first_at"), "last_at": extra.get("last_at"),
               "missed": extra.get("missed", []), "due": None}
        if day > t:
            f = forecast.get(key)
            row["due"] = {"checks": f["checks"], "fading": f["fading"]} if f else {"checks": 0, "fading": 0}
        else:
            totals["minutes"] += r["minutes"]
            totals["questions"] += r["questions"]
            totals["right"] += r["right"]
            totals["active_days"] += int(bool(r["questions"] or r["words"] >= 10 or r["tests"] or r.get("official")))
        days.append(row)
    firsts = [x for x in (db.one("SELECT MIN(at) m FROM attempts WHERE learner=?", learner)["m"],
                          db.one("SELECT MIN(at) m FROM word_reviews WHERE learner=?", learner)["m"]) if x]
    return {"month": month, "today": t.isoformat(),
            "first_active": progress._local_day(min(firsts), tz).isoformat() if firsts else None,
            "exam_date": profile(learner, tz)["exam_date"], "days": days, "totals": totals}


# ------------------------------------------------------------------ the day's questions

def _maybe_learner(x_learner: str | None) -> str | None:
    """The day's questions are public; a learner only adds their own answers."""
    if x_learner and LEARNER_OK.match(x_learner.strip()):
        return learner_of(x_learner)
    return None


def _slot_rows(learner: str | None, day: str) -> list[dict]:
    out = []
    for slot in daily.shown(day):
        got = daily.answered(learner, slot, day) if learner else None
        if slot in daily.MATH:
            q = (daily.rebuild(got["template"], got["seed"], "qotd" if slot == "math:mcq" else "qotd-spr")
                 if got else daily.item(slot, day))
            mine = daily.feedback(slot, day, q, got["given"], got["late"], got["ms"], learner) if got else None
        else:
            q = daily.item(slot, day)
            if q is None:
                continue
            mine = daily.rw_feedback(slot, day, q, got["given"], got["late"], got["ms"],
                                     {"correct": bool(got["correct"])}, learner) if got else None
        saved = bool(got and slot in daily.MATH and db.one(
            "SELECT 1 FROM saved WHERE learner=? AND template=? AND seed=?", learner, got["template"], got["seed"]))
        out.append({"slot": slot, **daily.SLOTS[slot], "question": daily.public(slot, q), "mine": mine,
                    "saved": saved})
    return out


@router.get("/api/qotd")
def get_qotd(day: str | None = Query(default=None), x_learner: str | None = Header(default=None),
             x_tz: int = Depends(tz_of)) -> dict:
    learner = _maybe_learner(x_learner)
    shown = daily.valid_day(day, x_tz)
    t = daily.today(x_tz)
    slots = _slot_rows(learner, shown)
    streak = daily.qotd_streak(learner, x_tz) if learner else {"current": 0, "best": 0}
    return {"day": shown, "today": t, "late": shown != t, "streak": streak["current"], "best": streak["best"],
            "month": daily.month(learner, x_tz) if learner else None, "slots": slots,
            "past": daily.past(learner, x_tz),
            # v2's one-question shape, kept for older clients: the multiple-choice slot
            "question": slots[0]["question"], "mine": slots[0]["mine"]}


class Reply(BaseModel):
    model_config = ConfigDict(extra="forbid")
    answer: StrictInt | StrictStr
    day: str | None = None          # the day it was shown; past midnight that is not today
    slot: str = "math:mcq"
    ms: int | None = Field(default=None, ge=0, le=86_400_000)


def _answer_for(slot: str, answer):
    fmt = daily.SLOTS[slot]["fmt"]
    if fmt == "spr":
        text = str(answer).strip()
        if not 1 <= len(text) <= 12:
            raise HTTPException(422, "answer is a grid-in entry of 1 to 12 characters")
        return text
    if isinstance(answer, str) and answer.strip().upper() in ("A", "B", "C", "D"):
        return "ABCD".index(answer.strip().upper())
    if not isinstance(answer, int) or not 0 <= answer <= 3:
        raise HTTPException(422, "answer is an option, 0 to 3")
    return answer


@router.post("/api/qotd")
def answer_qotd(body: Reply, x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    """One answer a slot a day. A second one is a double tap, and gets the
    first back. Yesterday's is on time for an hour after midnight; older
    days back to today − 30 are filed late (mastery, not crowd or streak)."""
    learner = writer_of(x_learner)
    slot = daily.slot_id(body.slot)
    if slot is None or slot not in daily.slots():
        raise HTTPException(422, f"slot is one of {', '.join(daily.slots())}")
    day, late = daily.route(body.day, x_tz)
    given = _answer_for(slot, body.answer)
    if slot not in daily.MATH:
        gen = daily.item(slot, day)
        record = part("words", "record_daily")
        if gen is None or record is None:
            raise HTTPException(409, {"reason": "no_item_today"})
        params = inspect.signature(record).parameters
        first = daily.answered(learner, slot, day)
        if first is None and late and "session" not in params:
            raise HTTPException(409, {"reason": "late_rw_unavailable"})     # Words files the day's own only, so far
        kw = {}
        if "session" in params:                 # W21's signature once Words takes S3's routing
            kw["session"] = daily.session(slot, day, late)
        if "tz" in params:
            # ponytail: the grace hour, until Words takes the session: an hour-behind zone makes
            # yesterday "today" for record_daily's own day check
            kw["tz"] = x_tz + daily.GRACE_MIN if day != daily.today(x_tz) and not late else x_tz
        reply = record(learner, day, daily.SLOTS[slot]["fmt"], given, body.ms, **kw) or {}
        return daily.rw_feedback(slot, day, gen, reply.get("given", given), first["late"] if first else late,
                                 body.ms, reply, learner)
    first = daily.answered(learner, slot, day)
    if first is None:
        q = daily.item(slot, day)
        filed = progress.record(learner, daily.session(slot, day, late), q, given, ms=body.ms, once=True)
        if filed is not None:
            daily.remember(learner, q)
            return {**daily.feedback(slot, day, q, given, late, body.ms, learner),
                    "opened": filed["opened"], "closed": filed["closed"]}
        first = daily.answered(learner, slot, day)
    q = daily.rebuild(first["template"], first["seed"], "qotd" if slot == "math:mcq" else "qotd-spr")
    return {**daily.feedback(slot, day, q, first["given"], first["late"], first["ms"], learner), "already": True}


class Another(BaseModel):
    model_config = ConfigDict(extra="forbid")
    day: str | None = None
    slot: str
    like: Literal["word", "trap"] = "word"


@router.post("/api/qotd/another")
def another_qotd(body: Another, x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    """An R&W slot's twin (T14): the same key word in another frame ('word')
    or the trap fallen for with another key ('trap'), answered through Words'
    sample token. A Math twin is POST /api/drill {like}."""
    learner = writer_of(x_learner)
    slot = daily.slot_id(body.slot)
    if slot in daily.MATH:
        raise HTTPException(422, "a Math twin is POST /api/drill {like:{day, slot}, count:1, source:'twin'}")
    if slot is None:
        raise HTTPException(422, "slot is rw:wic or rw:transition")
    try:
        day = daily.valid_day(body.day, x_tz)
    except HTTPException:
        raise HTTPException(404, {"reason": "day_out_of_range"})
    another, sign = part("words", "another"), part("api_words", "_sign")
    gen = daily.item(slot, day)
    if not (another and sign and gen):
        raise HTTPException(501, {"reason": "words_unavailable"})
    got = daily.answered(learner, slot, day)
    if not got:
        raise HTTPException(409, {"reason": "answer it first"})
    prev = dict(gen)
    if isinstance(got["given"], int) and gen.get("traps") and 0 <= got["given"] < len(gen["traps"]):
        prev["picked_trap"] = gen["traps"][got["given"]]
    try:
        twin = another(prev, body.like, learner)
    except ValueError:
        raise HTTPException(409, {"reason": "no_twin"})
    payload = {"learner": learner, "day": daily.today(x_tz), "template": twin["template"], "seed": twin["seed"],
               "word": twin["word"]}
    token = sign(payload)
    item = {**daily.public(slot, twin), "item_id": "sample:" + hashlib.sha256(token.encode()).hexdigest()[:12]}
    return {"item": item, "token": token, "slot": slot, "like": body.like}


class Keep(BaseModel):
    model_config = ConfigDict(extra="forbid")
    day: str | None = None
    slot: str = "math:mcq"
    on: bool = True


@router.post("/api/qotd/save")
def save_qotd(body: Keep, x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    """Save a Math day's question (§3.2.5 "POST /api/saved {qotd, slot, on}", which is
    S10's route): kept as the (template, seed) that regenerates it, and only once
    this learner has answered it, so a save never reads a key early."""
    learner = writer_of(x_learner)
    slot = daily.slot_id(body.slot)
    if slot not in daily.MATH:
        raise HTTPException(422, "slot is math:mcq or math:spr (R&W words are kept with Add to my words)")
    day = daily.valid_day(body.day, x_tz)
    got = daily.answered(learner, slot, day)
    if not got:
        raise HTTPException(409, "answer it first")
    if body.on:
        q = daily.rebuild(got["template"], got["seed"], "qotd" if slot == "math:mcq" else "qotd-spr")
        db.run("INSERT OR IGNORE INTO saved (learner, template, seed, topic, at) VALUES (?,?,?,?,?)",
               learner, got["template"], got["seed"], q["topic"], progress.now())
    else:
        db.run("DELETE FROM saved WHERE learner=? AND template=? AND seed=?", learner, got["template"], got["seed"])
    return {"saved": body.on}


# ------------------------------------------------------------------ /api/scores

class Score(BaseModel):
    model_config = ConfigDict(extra="forbid")
    day: str
    math: StrictInt
    rw: StrictInt | None = None
    source: str = "bluebook"


@router.get("/api/scores")
def list_scores(x_learner: str | None = Header(default=None)) -> dict:
    return {"scores": outside(learner_of(x_learner))}


@router.post("/api/scores", status_code=201)
def post_score(body: Score, x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    return add_outside_score(writer_of(x_learner), body.day, body.math, body.rw, body.source, x_tz)


@router.delete("/api/scores/{sid}")
def delete_score(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = writer_of(x_learner)
    if not db.run("DELETE FROM outside_scores WHERE id=? AND learner=?", sid, learner).rowcount:
        raise HTTPException(404, "no such score")
    return {"deleted": sid}
