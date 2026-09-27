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
from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

from . import challenge, daily, db, drill, estimate, progress, scoring
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
    """The learner's median seconds a question over 60 days (95 by default)."""
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=60)).isoformat()
    spent = [r["t"] for r in db.rows("SELECT COALESCE(ms, sms) AS t FROM attempts WHERE learner=? AND at>=?"
                                     " AND COALESCE(ms, sms) BETWEEN 1000 AND ?", learner, since, progress.MS_CAP)]
    return statistics.median(spent) / 1000 if spent else float(drill.deps.SECONDS_PER_QUESTION)


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


def traps(learner: str, tz: int, t: dt.date, open_list: list[dict], stage: dict | None) -> dict:
    """Review's card on Today (R30): counts, blind spots first, the top 5."""
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
           "top": [{"id": x["id"], "label": x["label"], "topic": x["topic"], "template": x["template"],
                    "hits": x["hits"], "owed": x["owed"], "last": x["last"], "relapses": x["relapses"] or 0,
                    "blind": blind[x["id"]]["why"] if x["id"] in blind else None,
                    "learn": bool((x["relapses"] or 0) >= 1 or x["hits"] >= 3)} for x in order[:5]],
           "habits": _call("habits", "of_learner", learner) or [], "now": None, "rare": None}
    if stage and stage.get("mode") in ("stretch", "taper", "eve"):
        shares = estimate.shares()
        now_ids = [x["id"] for x in order if 44 * shares.get(x["topic"], 0) >= 2]
        out["now"] = now_ids
        out["rare"] = [x["id"] for x in order if x["id"] not in now_ids]
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
            "marked": len(c["marked"]), "due": c["size"], "size": min(size, c["size"]),
            "today": {"held": sum(bool(held(r)) for r in mine), "of": len(mine),
                      "slipped": sorted({r["topic"] for r in mine if not r["correct"]})} if mine else None,
            "month": {"held": sum(bool(held(r)) for r in rows), "of": len(rows)}}


def plan_part(learner: str, tz: int) -> dict | None:
    """S7's day (R14), with the plan's own start (plans.start, R15) and its weeks."""
    s = _call("plan", "today_summary", learner, tz)
    if not s:
        return None
    out = dict(s)
    out["next_start"] = s.get("start")
    row = db.one("SELECT start, cfg FROM plans WHERE id=?", s.get("id"))
    out["start"] = row["start"] if row else None
    cfg = _json(row["cfg"], {}) if row else {}
    out["exam_date"] = cfg.get("exam_date")
    whole = _call("plan", "payload", learner, tz) or {}
    out["weeks"] = whole.get("weeks")
    out["stats"] = whole.get("stats")
    return out


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


def stage(learner: str, tz: int, p: dict, t: dt.date) -> dict | None:
    """T13's mode from the exam date: next.stage (F2) when it exists."""
    got = _call("next", "stage", learner, tz)
    if got is not None or part("next", "stage"):
        return got
    if not p.get("exam_date"):
        return None
    exam = dt.date.fromisoformat(p["exam_date"])
    days = (exam - t).days
    hour = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).hour
    mode = ("after" if days < 0 or (days == 0 and hour >= 13) else "exam" if days == 0 else "eve" if days == 1
            else "taper" if days <= 7 else "stretch" if days <= 14 else None)
    if mode is None:
        return {"mode": None, "days": days, "rehearsals": [], "sweep": None, "rare": None}
    sats = [exam - dt.timedelta(days=n) for n in range(6, 15) if (exam - dt.timedelta(days=n)).weekday() == 5]
    rehearsals = []
    for s in sorted(sats)[-2:]:
        done = db.one("SELECT 1 FROM sessions WHERE learner=? AND kind IN ('mock','section','paper')"
                      " AND finished>=? AND finished<?", learner, _start(s, tz), _start(s + dt.timedelta(days=1), tz))
        rehearsals.append({"day": s.isoformat(), "done": bool(done)})
    began = exam - dt.timedelta(days=14)
    cut = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=90)).isoformat()
    closed = db.rows("SELECT id, template FROM traps WHERE learner=? AND closed>=? AND closed_how IN ('fixed','transfer')",
                     learner, cut)
    swept = sum(bool(db.one("SELECT 1 FROM attempts WHERE learner=? AND template=? AND at>=?",
                            learner, c["template"], _start(began, tz))) for c in closed)
    study_left = max(1, (exam - t).days - 1)
    return {"mode": mode, "days": days, "rehearsals": rehearsals,
            "sweep": {"total": len(closed), "done": swept,
                      "today": math.ceil(max(0, len(closed) - swept) / study_left)},
            "rare": None}


def next_part(learner: str, tz: int, p: dict, coach: dict, st: dict | None, plan: dict | None,
              study_: dict, due_: dict) -> dict:
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
    return {"items": _call("next", "queue", learner, tz, limit=6) or [],
            "box": {"default": default, "options": list(BOX_OPTIONS)},
            "count": {"default": count, "options": list(dict.fromkeys([5, 10, 22, count])) + [None]},
            "preview": preview, "stage": st}


def due_fallback(learner: str, tz: int, p: dict, open_: dict, plan: dict | None, warm: dict,
                 words: dict | None, qotd: dict, chal: dict, secs: float) -> dict:
    """T2's rows while next.due (F2) is not there: the same sources, in its order.
    ponytail: replaced by next.due as soon as server/next.py lands."""
    rows = []
    if open_["test"]:
        x = open_["test"]
        rows.append({"key": f"test:{x['id']}", "kind": "test", "title": "Section" if x["section"] else "Module",
                     "tag": "Test", "minutes": math.ceil((x["seconds_left"] or 0) / 60),
                     "progress": {"have": x["answered"], "of": x["asked"]}, "status": "progress",
                     "href": f"/test/?s={x['id']}"})
    recheck = False
    for task in (plan or {}).get("tasks") or []:
        kind = task.get("kind")
        if kind in ("qotd", "challenge"):
            continue
        recheck = recheck or kind == "recheck"
        rows.append({"key": f"plan:{task.get('id')}", "kind": "warmup" if kind == "recheck" else "plan",
                     "title": task.get("title"), "tag": kind, "minutes": task.get("minutes"),
                     "status": task.get("status"), "task_id": task.get("id"), "own": kind == "custom",
                     "marked": task.get("status") == "marked", "start": task.get("start"),
                     "why": task.get("why") or [], "alternatives": task.get("alternatives"),
                     "progress": task.get("progress"), "result": task.get("result")})
    if warm["size"] and not recheck:
        done = bool(warm["today"] and warm["today"]["of"] >= warm["size"])
        rows.append({"key": "warmup", "kind": "warmup", "title": f"Warm-up · {warm['size']} questions",
                     "tag": "Warm-up", "minutes": math.ceil(warm["size"] * secs / 60),
                     "progress": {"have": (warm["today"] or {}).get("of", 0), "of": warm["size"]},
                     "status": "done" if done else "todo",
                     "start": {"path": "/api/drill", "body": {"source": "warmup", "count": warm["size"]}}})
    if words and words.get("due"):
        rows.append({"key": "words", "kind": "words", "title": words.get("title"), "tag": "Words",
                     "minutes": words.get("minutes"), "status": "done" if words.get("done") else "todo",
                     "start": words.get("start")})
    rows.append({"key": "qotd", "kind": "qotd", "title": "The day's questions", "tag": "Day's questions",
                 "minutes": math.ceil(qotd["slots"] * secs / 60),
                 "progress": {"have": qotd["answered"], "of": qotd["slots"]},
                 "status": "done" if qotd["answered"] == qotd["slots"] else "progress" if qotd["answered"] else "todo",
                 "why": [f"The same {qotd['slots']} for everyone, one try each"], "href": "/#qotd"})
    rows.append({"key": "challenge", "kind": "challenge", "title": "Daily challenge", "tag": "Challenge",
                 "minutes": 0 if chal["done"] else CHALLENGE_S // 60,
                 "progress": {"have": chal["answered"], "of": chal["total"]},
                 "status": "done" if chal["done"] else "progress" if chal["started"] else "todo",
                 "start": {"path": "/api/challenge/start", "body": {}}})
    for c in _call("compete", "due_today", learner, tz) or []:
        rows.append({"key": f"contest:{c['id']}", "kind": "contest", "title": c.get("title"), "tag": "Contest",
                     "minutes": CHALLENGE_S // 60, "due_at": c.get("closes"), "status": "todo",
                     "href": f"/compete/contest/?id={c['id']}"})
    finished = ("done", "marked", "made_up", "skipped", "moved")
    rows.sort(key=lambda r: r.get("status") in finished)
    undone = [r for r in rows if r.get("status") not in finished]
    return {"rows": rows, "minutes_left": sum(r.get("minutes") or 0 for r in undone),
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
             gains: dict | None, secs: float) -> dict | None:
    """Capacity against need to the exam's eve, including the target's skill
    work (estimate.need(target).path). Sized only with 30 answers and a target."""
    if not p.get("exam_date"):
        return None
    exam = dt.date.fromisoformat(p["exam_date"])
    pattern = p.get("days") if p.get("days") and len(p["days"]) == 7 else None
    days = [t + dt.timedelta(days=i) for i in range(max(0, (exam - t).days - 1))]   # today to the eve's eve
    study_days = [x for x in days if not pattern or pattern[x.weekday()] == "1"]
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
    if tests_per_week is not None:
        tests, clock = math.ceil(len(study_days) / 7 * tests_per_week) if tests_per_week < 7 else len(study_days), MODULE_S
    else:
        tests = sum(1 for n in range(6, 15) if (exam - dt.timedelta(days=n)).weekday() == 5
                    and exam - dt.timedelta(days=n) >= t)
        tests, clock = min(2, tests), SECTION_S
    need = {"traps": int(open_count * 2 * secs), "checks": int(checks * secs), "tests": tests * clock,
            "tests_n": tests, "warmups": int(min(5, warm["due"]) * secs * len(study_days)), "target": None}
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


def goal_suggest(w: dict | None) -> dict | None:
    """T17: the suggested daily goal and its arithmetic; null exactly when unsized."""
    if not w or not w["sized"] or w["suggest_minutes"] is None:
        return None
    n = w["need"]
    parts = {"traps": n["traps"], "checks": n["checks"], "tests": n["tests"], "warmups": n["warmups"],
             "target": n["target"]["minutes"] * 60 if n["target"] else 0}
    return {"minutes": w["suggest_minutes"], "study_days": w["study_days"], "total": w["total"],
            "per_day": round(w["total"] / 60 / max(1, w["study_days"])), "parts": parts,
            "target": n["target"]["target"] if n["target"] else None}


# ------------------------------------------------------------------ GET /api/today

def today_payload(learner: str, tz: int) -> dict:
    p = profile(learner, tz)
    d = progress.days(learner, tz, 6)
    t = dt.date.fromisoformat(d["today"])
    exam = None
    if p["exam_date"]:
        exam = {"date": p["exam_date"], "days": (dt.date.fromisoformat(p["exam_date"]) - t).days}
    today0 = _start(t, tz)
    tested = bool(db.one("SELECT 1 FROM sessions WHERE learner=? AND kind IN ('mock','module') AND finished>=?",
                         learner, today0)) or bool(db.one("SELECT 1 FROM outside_scores WHERE learner=? AND day=?",
                                                          learner, t.isoformat()))
    coach = progress.coach(learner, count=per_session(p))
    open_list = progress.open_traps(learner)
    score_list = scores(learner)
    st = stage(learner, tz, p, t)
    plan = plan_part(learner, tz)
    words = _call("words", "today_summary", learner, tz)
    open_ = open_sittings(learner)
    warm = warmup(learner, tz, t, st)
    study_ = study(p, d, t)
    qotd = qotd_today(learner, tz)
    chal = challenge_today(learner, tz, t)
    secs = _median_s(learner)
    due_ = _call("next", "due", learner, tz) or due_fallback(learner, tz, p, open_, plan, warm, words, qotd, chal, secs)
    gains = estimate.gains(learner)
    work = workload(learner, tz, p, t, d, len(open_list), warm, gains, secs)
    return {
        "profile": p, "days": d, "exam": exam, "tested": tested, "score": score_list[0] if score_list else None,
        "coach": coach, "mistakes": len(open_list),
        "study": study_, "scores": score_list, "outside": outside(learner), "domains": domains(learner),
        "traps": traps(learner, tz, t, open_list, st), "open": open_, "week": week(learner, tz, d, t),
        "warmup": warm, "plan": plan, "review": review_counts(learner, tz, t), "words": words,
        "qotd": qotd, "challenge": chal, "seconds_per_question": round(secs),
        "next": next_part(learner, tz, p, coach, st, plan, study_, due_), "due": due_,
        "brief": brief(learner, tz, d, t, score_list), "at_risk": at_risk(learner, tz, d, t, coach),
        "receipt": receipt(learner, tz, d, t, p, due_), "workload": work, "goal_suggest": goal_suggest(work),
    }


@router.get("/api/today")
def get_today(x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    return today_payload(learner_of(x_learner), x_tz)


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


def _estimate_block(learner: str, tz: int, p: dict) -> dict:
    """T10: practice since the last test, evidence per domain, the projection
    and its verdict, calibration against an official score."""
    score_list = scores(learner)
    latest = score_list[0] if score_list else None
    delta = estimate.practice_delta(learner, latest["at"]) if latest else None
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=60)).isoformat()
    names = progress.topics()
    evidence = {name: 0 for name in progress.DOMAINS}
    for r in db.rows(f"SELECT topic, COUNT(*) n FROM attempts WHERE learner=? AND at>=? AND repair=0"
                     f" AND {progress.COUNTED} GROUP BY topic", learner, since):
        if r["topic"] in names:
            evidence[names[r["topic"]].domain] = evidence.get(names[r["topic"]].domain, 0) + r["n"]
    proj = estimate.projection(learner)
    target = p.get("target")
    verdict = made = needs = None
    if latest and target and latest["low"] >= target:
        verdict = "at_target"
    elif proj is None:
        verdict = "not_enough"
    else:
        made = proj.get("slope_used")
        if target and p.get("exam_date"):
            weeks = max(1 / 7, (dt.date.fromisoformat(p["exam_date"]) - _local_today(tz)).days / 7)
            needs = round((target - (latest["mid"] if latest else proj["mid"])) / weeks, 1)
            verdict = "on_pace" if proj["mid"] >= target else "behind"
        else:
            verdict = "projected"
    calibration = None
    o = db.one("SELECT * FROM outside_scores WHERE learner=? AND source='official' AND math IS NOT NULL"
               " ORDER BY day DESC LIMIT 1", learner)
    if o:
        day = dt.date.fromisoformat(o["day"])
        items = [x for x in estimate._sittings(learner) if x["standard"] and not x["outside"]
                 and day - dt.timedelta(days=90) <= dt.date.fromisoformat(x["at"][:10]) < day]
        if items:
            pr = estimate.project([(dt.date.fromisoformat(x["at"][:10]), x["mid"]) for x in items], day,
                                  (items[0]["high"] - items[0]["low"]) / 2)
            if pr:
                calibration = {"projected": {"low": pr["low"], "high": pr["high"]}, "score": o["math"],
                               "day": o["day"], "inside": pr["low"] <= o["math"] <= pr["high"]}
    standard = sum(1 for x in estimate._sittings(learner) if x["standard"] and not x["outside"]
                   and (dt.date.today() - dt.date.fromisoformat(x["at"][:10])).days <= 90)
    return {"latest": latest, "practice_delta": delta, "evidence": evidence,
            "thin": [k for k, n in evidence.items() if n < 15], "projection": proj, "verdict": verdict,
            "made_per_week": made, "needs_per_week": needs, "calibration": calibration,
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
    forecast = {f["day"]: f for f in progress.due_forecast(learner, tz, (last - t).days)} if last > t else {}
    days, totals = [], {"minutes": 0, "questions": 0, "right": 0, "active_days": 0}
    for i in range((last - first).days + 1):
        day = first + dt.timedelta(days=i)
        key = day.isoformat()
        r = rows.get(key) or {"questions": 0, "right": 0, "minutes": 0, "practice": 0, "tests": 0, "words": 0,
                              "fixed": 0, "rest": False, "spare_used": False, "official": 0}
        extra = per.get(key, {})
        row = {"day": key, "questions": r["questions"], "right": r["right"], "minutes": r["minutes"],
               "practice": r["practice"], "tests": r["tests"], "words": r["words"], "fixed": r["fixed"],
               "rest": r["rest"], "spare_used": r.get("spare_used", False),
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
        out.append({"slot": slot, **daily.SLOTS[slot], "question": daily.public(slot, q), "mine": mine})
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
        # W21's signature; the session carries S3's grace and late routing when Words takes it
        kw = {"session": daily.session(slot, day, late)} if "session" in inspect.signature(record).parameters else {}
        reply = record(learner, day, daily.SLOTS[slot]["fmt"], given, body.ms, **kw) or {}
        return daily.rw_feedback(slot, day, gen, reply.get("given", given), late, body.ms, reply, learner)
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
