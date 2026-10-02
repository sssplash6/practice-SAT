"""Explanations for the numbers shown across the site (U13, G6)."""

from __future__ import annotations

import datetime as dt
import json
import secrets
from collections import Counter
from functools import lru_cache

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from . import achievements, api_me, db, deps, estimate, practice, prefs, progress
from .deps import learner_of, tz_of

router = APIRouter()


def _fact(value, how: str, inputs: list, *, help: str, next: str | None = None,
          start: dict | None = None, excluded: list | None = None,
          same_on: list | None = None) -> dict:
    return {"value": value, "how": how, "help": help, "inputs": inputs,
            "excluded": excluded or [], "next": next, "start": start,
            "same_on": same_on or []}


def levers(learner: str, tz: int, keys: list[str]) -> dict[str, dict]:
    """Compute each fact from the same reader that paints its page. Memoisation
    here is per request, so a 20-key popover read does not redo the ledger."""

    @lru_cache(maxsize=None)
    def days():
        return progress.days(learner, tz, 5)

    @lru_cache(maxsize=None)
    def due():
        fn = deps.part("review", "due")
        if fn:
            return fn(learner, tz)
        today = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date().isoformat()
        checks = progress.due_rechecks(learner, today)
        left = api_me.due_left(learner, tz, prefs.get(learner, tz))
        return {"left": left, "total": len(checks), "done": 0,
                "snoozed": max(0, len(checks) - left), "waiting": 0, "minutes": 10}

    @lru_cache(maxsize=None)
    def counts():
        fn = deps.part("review", "counts")
        if fn:
            return fn(learner, tz)
        open_traps = progress.open_traps(learner)
        return {"open": len(open_traps), "half": sum(t["owed"] == 1 for t in open_traps),
                "relapsed": sum(bool(t["relapses"]) for t in open_traps)}

    @lru_cache(maxsize=None)
    def board():
        return progress.board(learner)

    @lru_cache(maxsize=None)
    def gains():
        return estimate.gains(learner)

    @lru_cache(maxsize=None)
    def band():
        return estimate.estimate(learner)

    @lru_cache(maxsize=None)
    def pace():
        return progress.pace(learner)

    def left_out() -> list[dict]:
        r = db.one("SELECT SUM(repeat=1) AS repeats,SUM(disputed=1) AS disputed,"
                   " SUM(void IS NOT NULL) AS discarded,SUM(guess=1 AND correct=1) AS guesses"
                   " FROM attempts WHERE learner=?", learner)
        return [{"label": label, "n": r[col] or 0} for col, label in
                (("repeats", "exact repeats"), ("disputed", "disputed answers"),
                 ("discarded", "discarded answers"), ("guesses", "right guesses count half"))
                if r[col]]

    result = {}
    for key in dict.fromkeys(keys):
        parts = key.split(":")
        if key == "streak":
            d = days()
            today = d["recent"][-1]
            next_line = ("Today is a rest day in your plan: your streak is safe" if today["rest"] else
                         f"Answer 1 today to make it {d['streak'] + 1}")
            if d["spares"]:
                next_line += f" · {d['spares']} spare banked"
            result[key] = _fact(d["streak"], "Consecutive active study days, with plan rest days and spares protected.",
                                [{"label": "Current run", "value": d["streak"]},
                                 {"label": "Best run", "value": d["best"]},
                                 {"label": "Today answered", "value": today["questions"]},
                                 {"label": "Today words reviewed", "value": today["words"]}],
                                help="streak", next=next_line,
                                start={"label": "Answer one", "body": {"source": "quick", "count": 1}},
                                same_on=["today", "me", "shell"])
        elif key == "open_mistakes":
            c = counts()
            result[key] = _fact(c["open"], "Open named mistakes and unnamed misses that still need clean answers.",
                                [{"label": "Open traps", "value": c["open"]},
                                 {"label": "Half fixed", "value": c["half"]},
                                 {"label": "Relapsed", "value": c["relapsed"]}],
                                help="mistakes", next="A clean answer on a matching question fills a pip.",
                                start={"label": "Open Review", "href": "/review/?tab=redo"},
                                same_on=["review", "me", "today", "shell"])
        elif key == "due_today":
            d = due()
            result[key] = _fact(d["left"], "Undone items in today's frozen Review list; snoozed items wait for tomorrow.",
                                [{"label": "Today's list", "value": d["total"]},
                                 {"label": "Done", "value": d["done"]},
                                 {"label": "Snoozed", "value": d["snoozed"]},
                                 {"label": "Waiting beyond today's cap", "value": d["waiting"]}],
                                help="review", next=f"{d['left']} still on today's list",
                                start={"label": "Start review", "body": {"source": "due", "box": d["minutes"]}},
                                same_on=["today", "review", "me", "shell"])
        elif key in ("minutes:today", "minutes:week", "minutes:month"):
            d = days()
            span = {"today": 1, "week": 7, "month": 30}[parts[1]]
            minutes = sum(x["minutes"] for x in d["days"][-span:])
            result[key] = _fact(minutes, "Minutes from answered questions, Words reviews, tests and completed plan tasks.",
                                [{"label": "Days counted", "value": span},
                                 {"label": "Study minutes", "value": minutes}],
                                help="study-time", next="Another answered question adds its measured time.",
                                same_on=["today", "me"])
        elif key in ("points", "points_on_table"):
            g = gains()
            top = g["skills"][0] if g and g["skills"] else None
            result[key] = _fact(g["total"] if g else None,
                                "Estimated Math points available if each skill reaches Strong.",
                                [{"label": "Counted answers", "value": g["answers"] if g else 0},
                                 {"label": "Top skill", "value": top["topic"] if top else "not measured"},
                                 {"label": "Top skill points", "value": top["gain"] if top else None}],
                                help="points", next="Reach 30 counted answers for a measured estimate" if not g else
                                f"Practise {top['topic']} to recover about {top['gain']} points" if top else None,
                                start={"label": "Practise top skill", "body": {"topics": [top["topic"]], "count": 8}}
                                if top else None, excluded=left_out(), same_on=["me", "results", "plan"])
        elif key in ("band", "estimate"):
            e = band()
            latest = e["latest"]
            value = {"low": latest["low"], "high": latest["high"]} if latest else None
            result[key] = _fact(value, "The latest scored sitting's Math score range; the range tightens with more sections.",
                                [{"label": "Scored sittings", "value": e["counted"]["sittings"]},
                                 {"label": "Full sections", "value": e["counted"]["sections"]},
                                 {"label": "Confidence", "value": e["confidence"]["level"]}],
                                help="score-band", next=e["confidence"]["reason"],
                                same_on=["today", "me", "results"])
        elif key == "active_days":
            d = days()
            result[key] = _fact(d["active_days"], "Days with a question, enough Words reviews, a completed test or official practice.",
                                [{"label": "Active days", "value": d["active_days"]},
                                 {"label": "Total minutes", "value": d["minutes_total"]}],
                                help="study-days", next="Answer one question on a new day to add a day.",
                                same_on=["today", "me"])
        elif key in ("target", "exam_date"):
            p = db.one("SELECT target,exam_date FROM learners WHERE id=?", learner)
            value = p[key] if p else None
            result[key] = _fact(value, "Your saved study target or SAT date, used by Today and Plan.",
                                [{"label": key.replace("_", " ").capitalize(), "value": value}],
                                help="plan", next="Change this in Settings to update your plan.",
                                start={"label": "Settings", "href": "/me/?tab=settings"},
                                same_on=["today", "plan", "me"])
        elif len(parts) == 2 and parts[0] == "skill":
            topic = parts[1]
            b = board().get(topic)
            if b is None:
                raise HTTPException(422, {"field": "keys", "reason": f"unknown skill {topic}"})
            need = progress.steps_to(learner, topic, progress.STRONG, "medium")
            result[key] = _fact(b["mastery"], "Recent first-try answers are weighted by difficulty and certainty.",
                                [{"label": "Counted answers", "value": b["answered"]},
                                 {"label": "Recent evidence", "value": b["evidence"]},
                                 {"label": "Open mistakes", "value": len(b["traps"])}],
                                help="mastery", next=f"{need} more right at Medium reaches Strong" if need is not None else
                                "Practise this skill to build evidence",
                                start={"label": "Practise", "body": {"topics": [topic], "count": 8}},
                                excluded=left_out(), same_on=["me", "results", "plan"])
        elif len(parts) == 3 and parts[0] == "accuracy":
            topic = parts[1]
            try:
                window = int(parts[2])
            except ValueError:
                raise HTTPException(422, "accuracy keys use accuracy:<topic>:<days>")
            if topic not in progress.topics() or not 1 <= window <= 365:
                raise HTTPException(422, "unknown accuracy topic or days")
            since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=window)).isoformat()
            row = db.one("SELECT COUNT(*) AS n, SUM(correct) AS right FROM attempts WHERE learner=? AND topic=?"
                         f" AND at>=? AND {progress.COUNTED}", learner, topic, since)
            n = row["n"] or 0
            result[key] = _fact(round((row["right"] or 0) / n, 3) if n else None,
                                f"Right first tries on {topic} in the last {window} days divided by counted answers.",
                                [{"label": "Right", "value": row["right"] or 0},
                                 {"label": "Counted", "value": n}],
                                help="accuracy", next="One more clean answer lifts this rate.",
                                start={"label": "Practise", "body": {"topics": [topic], "count": 8}},
                                excluded=left_out(), same_on=["me", "results"])
        elif len(parts) == 2 and parts[0] == "pace":
            topic = parts[1]
            if topic not in progress.topics():
                raise HTTPException(422, "unknown pace topic")
            skill = pace()["skills"].get(topic)
            result[key] = _fact(skill["median_ms_right"] if skill else None,
                                "Median time on right answers to this skill over the last 60 days.",
                                [{"label": "Timed answers", "value": skill["n"] if skill else 0},
                                 {"label": "Right-answer median, ms", "value": skill["median_ms_right"] if skill else None},
                                 {"label": "SAT question budget, ms", "value": 95000}],
                                help="pace", next="Aim to answer correctly within the SAT budget.",
                                start={"label": "Speed drill", "body": {"topics": [topic], "count": 8,
                                                                         "timing": "pace"}}, same_on=["me", "review"])
        elif key == "readiness":
            met = progress.types_met(learner)
            result[key] = _fact(met["met"], "Question types you have met at least once, out of the Math catalogue.",
                                [{"label": "Met", "value": met["met"]},
                                 {"label": "Never met", "value": met["never"]},
                                 {"label": "Total types", "value": met["total"]}],
                                help="readiness", next=f"Meet {met['never']} more question types",
                                start={"label": "Practise unmet", "body": {"pool": "untried", "count": 8}},
                                same_on=["today", "me", "plan"])
        elif len(parts) == 2 and parts[0] == "percentile":
            sid = parts[1]
            row = db.one("SELECT learner FROM sessions WHERE id=?", sid)
            if row is None or row["learner"] != learner:
                raise HTTPException(404, "no such sitting of yours")
            p = estimate.percentile(sid)
            result[key] = _fact(p["pct"], "Rank among first standard sittings of the same kind when 20 peers exist.",
                                [{"label": "Peer sittings", "value": p["n"]},
                                 {"label": "Ranked", "value": p["ranked"]}],
                                help="percentile", next=p.get("why") or "Take another standard section to compare.",
                                same_on=["results", "me"])
        elif len(parts) == 3 and parts[0] == "rank":
            from . import compete
            metric, period = parts[1:]
            board_result = compete.leaderboard(metric, period, learner=learner)
            mine = board_result["you"]
            result[key] = _fact(mine["rank"] if mine else None,
                                "Your place among learners on this competition board.",
                                [{"label": "Your value", "value": mine["value"] if mine else None},
                                 {"label": "Learners", "value": board_result["players"]}],
                                help="rank", next="Answer more questions this period to move up.",
                                same_on=["compete", "me"])
        else:
            raise HTTPException(422, {"field": "keys", "reason": f"unknown fact {key[:60]}"})
    return result


@router.get("/api/levers")
def get_levers(keys: str = Query(min_length=1, max_length=1000),
               x_learner: str | None = Header(default=None),
               x_tz: int = Depends(tz_of)) -> dict:
    names = [k.strip() for k in keys.split(",") if k.strip()]
    if not names or len(names) > 20 or len(set(names)) > 20:
        raise HTTPException(422, "request 1 to 20 fact keys")
    return {"levers": levers(learner_of(x_learner), x_tz, names)}


def _practice_rank(learner: str, scope: str = "all") -> dict | None:
    """Visible seven-day board, including a hidden student's own place."""
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)).isoformat()
    mine = db.one("SELECT exam_date,country FROM learners WHERE id=?", learner)
    if scope == "exam" and (not mine or not mine["exam_date"]):
        return None
    if scope == "country" and (not mine or not mine["country"]):
        return None
    rows = db.rows("SELECT a.learner,COUNT(*) AS answered,SUM(a.correct) AS right,"
                   " l.board,l.handle,l.name,l.exam_date,l.country FROM attempts a"
                   " LEFT JOIN learners l ON l.id=a.learner WHERE a.at>=? AND a.repeat=0"
                   " AND a.disputed=0 AND a.learner NOT LIKE 'sample:%'"
                   " GROUP BY a.learner ORDER BY right DESC,answered DESC,a.learner", cutoff)
    filtered = [r for r in rows if (scope == "all" or
                (scope == "exam" and r["exam_date"] == mine["exam_date"]) or
                (scope == "country" and r["country"] == mine["country"]))]
    visible = [r for r in filtered if r["board"] != "hidden" or r["learner"] == learner]
    own = next((r for r in visible if r["learner"] == learner), None)
    rank = visible.index(own) + 1 if own else None
    before = visible[rank - 2] if rank and rank > 1 else None
    top = [{"name": r["handle"] or r["name"] or "Student", "right": r["right"],
            "answered": r["answered"], "you": r["learner"] == learner}
           for r in visible if r["board"] != "hidden" or r["learner"] == learner][:20]
    return {"rank": rank, "of": len(visible), "top": top,
            "gap": max(1, before["right"] - own["right"] + 1) if before and own else None}


def _qotd_stats(learner: str, tz: int, days: list[dict]) -> dict:
    rows = db.rows("SELECT session,correct,at FROM attempts WHERE learner=? AND"
                   " (session LIKE 'qotd:%' OR session LIKE 'qotd-spr:%')", learner)
    dates = set()
    right = 0
    for r in rows:
        dates.add(progress._local_day(r["at"], tz))
        right += bool(r["correct"])
    today = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date()
    run = 0
    day = today if today in dates else today - dt.timedelta(days=1)
    while day in dates:
        run += 1
        day -= dt.timedelta(days=1)
    return {"answered": len(rows), "right": right, "run": run}


def _habits(learner: str) -> list[dict]:
    family_of = deps.part("habits", "family_of")
    families = deps.part("habits", "families")
    if not family_of or not families:
        return []
    now = dt.datetime.now(dt.timezone.utc)
    prior = (now - dt.timedelta(days=28)).isoformat()
    recent = (now - dt.timedelta(days=14)).isoformat()
    counts: dict[str, dict] = {}
    for r in db.rows("SELECT reason,topic,at FROM attempts WHERE learner=? AND correct=0"
                     " AND repeat=0 AND disputed=0 AND at>=?", learner, prior):
        family = family_of(r["reason"] or "")
        if not family:
            continue
        item = counts.setdefault(family["id"], {"id": family["id"], "name": family["name"],
                                                   "tell": family["tell"], "misses": 0,
                                                   "skills": set(), "this": 0, "prior": 0})
        item["misses"] += 1
        item["skills"].add(r["topic"])
        item["this" if r["at"] >= recent else "prior"] += 1
    out = []
    for item in counts.values():
        out.append({"id": item["id"], "name": item["name"], "tell": item["tell"],
                    "misses": item["misses"], "skills": sorted(item["skills"]),
                    "trend": item["this"] - item["prior"]})
    return sorted(out, key=lambda x: (-x["misses"], x["id"]))


def _self_rank(learner: str, board: dict, current: dict) -> dict | None:
    first = db.one("SELECT MIN(at) AS at FROM attempts WHERE learner=?", learner)["at"]
    if not first:
        return None
    today = dt.datetime.now(dt.timezone.utc).date()
    available = (today - dt.date.fromisoformat(first[:10])).days
    if available < 8:
        return None
    days = min(30, available)
    cutoff = (today - dt.timedelta(days=days)).isoformat()
    old = next((x for x in estimate._sittings(learner) if x["at"] < cutoff), None)
    improved = 0
    for topic, skill in board.items():
        if skill["mastery"] < progress.STRONG:
            continue
        rows = db.rows(f"SELECT difficulty,correct FROM attempts WHERE learner=? AND topic=?"
                       f" AND at<? AND {progress.COUNTED} ORDER BY at DESC,id DESC LIMIT ?",
                       learner, topic, cutoff, progress.WINDOW)
        older = progress.mastery_of([(r["difficulty"], r["correct"]) for r in rows])
        improved += older < progress.STRONG
    fixed = db.one("SELECT COUNT(*) AS n FROM traps WHERE learner=? AND closed>=?",
                   learner, cutoff)["n"]
    delta = round(current["mid"] - old["mid"]) if current and old else None
    return {"days": days, "estimate": delta, "skills_to_strong": improved, "fixed": fixed}


def summary(learner: str, tz: int = 0) -> dict:
    p = api_me.profile(learner, tz)
    d = progress.days(learner, tz, 5)
    b = progress.board(learner)
    e = estimate.estimate(learner)
    g = estimate.gains(learner)
    all_a = db.one("SELECT COUNT(*) AS n,SUM(correct) AS right FROM attempts WHERE learner=?", learner)
    counted = db.one(f"SELECT COUNT(*) AS n,SUM(correct) AS right FROM attempts"
                     f" WHERE learner=? AND {progress.COUNTED}", learner)
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)).isoformat()
    a7 = db.one(f"SELECT COUNT(*) AS n,SUM(correct) AS right FROM attempts WHERE learner=?"
                f" AND at>=? AND {progress.COUNTED}", learner, cutoff)
    sessions = db.rows("SELECT id,kind,cfg,contest,finished,result,route FROM sessions WHERE learner=?"
                       " AND finished IS NOT NULL AND abandoned IS NULL ORDER BY finished DESC", learner)
    kinds = {}
    for r in sessions:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    traps = db.one("SELECT SUM(closed IS NULL) AS opened,SUM(closed IS NOT NULL) AS fixed"
                   " FROM traps WHERE learner=?", learner)
    saved = db.one("SELECT COUNT(*) AS n FROM saved WHERE learner=?", learner)["n"]
    hard = db.one(f"SELECT COUNT(*) AS n FROM attempts WHERE learner=? AND difficulty='hard'"
                  f" AND correct=1 AND {progress.COUNTED}", learner)["n"]
    recent = d["recent"]
    series = {"answered": [x["questions"] for x in recent],
              "minutes": [x["minutes"] for x in recent],
              "accuracy": [round(x["right"] / x["questions"] * 100) if x["questions"] else None
                           for x in recent],
              "fixed": [x["fixed"] for x in recent]}
    delta = {k: sum(x or 0 for x in values[7:]) - sum(x or 0 for x in values[:7])
             for k, values in series.items() if k != "accuracy"}
    this_n = sum(recent[i]["questions"] for i in range(7, 14))
    last_n = sum(recent[i]["questions"] for i in range(7))
    delta["accuracy"] = ((round(100 * sum(x["right"] for x in recent[7:]) / this_n) if this_n else 0) -
                         (round(100 * sum(x["right"] for x in recent[:7]) / last_n) if last_n else 0))
    qotd = _qotd_stats(learner, tz, d["days"])
    stats = {"answered": all_a["n"], "right": all_a["right"] or 0,
             "accuracy": round(100 * (counted["right"] or 0) / counted["n"]) if counted["n"] else None,
             "accuracy7": round(100 * (a7["right"] or 0) / a7["n"]) if a7["n"] else None,
             "minutes_total": d["minutes_total"], "minutes_week": sum(x["minutes"] for x in recent[-7:]),
             "active_days": d["active_days"], "streak": d["streak"], "best_streak": d["best"],
             "since": (db.one("SELECT created FROM learners WHERE id=?", learner) or {"created": None})["created"],
             "tests": sum(kinds.get(k, 0) for k in deps.TEST_KINDS),
             "sections": sum(kinds.get(k, 0) for k in ("section", "mock", "paper")),
             "modules": kinds.get("module", 0), "diagnostics": kinds.get("diagnostic", 0),
             "sets": kinds.get("drill", 0), "mistakes_open": traps["opened"] or 0,
             "mistakes_fixed": traps["fixed"] or 0, "saved": saved, "hard_right": hard,
             "qotd": qotd,
             "challenges_played": sum(bool(r["kind"] == "challenge" or r["contest"])
                                      for r in sessions),
             "series": series, "delta": delta,
             "levers": levers(learner, tz, ["streak", "minutes:week", "open_mistakes"])}
    domains = []
    by_topic = practice.catalogue()["by_topic"]
    met = {r["template"] for r in db.rows("SELECT DISTINCT template FROM attempts WHERE learner=?", learner)}
    coverage = []
    types = {}
    by_type = db.rows("SELECT template,COUNT(*) AS met,SUM(correct) AS right,MAX(at) AS last"
                      f" FROM attempts WHERE learner=? AND {progress.COUNTED} GROUP BY template", learner)
    type_counts = {r["template"]: dict(r) for r in by_type}
    open_types = {r["template"] for r in db.rows("SELECT DISTINCT template FROM traps"
                                                  " WHERE learner=? AND closed IS NULL", learner)}
    from . import api_bank, blueprint
    kinds = blueprint.kinds()
    raw_weights = {name: api_bank._weight(entry) for name, entry in kinds.items()
                   if deps.subject_of(entry["topic"]) == "math"}
    weight_sum = sum(raw_weights.values()) or 1
    ready_weight = 0.0
    for name, weight in raw_weights.items():
        counts = type_counts.get(name, {})
        rights = counts.get("right") or 0
        types[name] = {"met": counts.get("met") or 0, "right": rights,
                       "last": counts.get("last"), "open": name in open_types}
        if rights >= 2:
            ready_weight += weight / weight_sum
    for domain in progress.DOMAINS:
        skills = []
        for topic, skill in b.items():
            if skill["domain"] != domain:
                continue
            skills.append({"topic": topic, "name": skill["name"], "mastery": skill["mastery"],
                           "answered": skill["answered"], "right": round((skill["accuracy"] or 0) *
                                                                             skill["answered"]),
                           "traps": len(skill["traps"]), "evidence": skill["evidence"],
                           "trend14": skill["trend14"], "last5": skill["last5"],
                           "fading": skill["fading"]})
            templates = set(by_topic.get(topic, []))
            coverage.append({"topic": topic, "met": len(met & templates), "total": len(templates)})
        domains.append({"domain": domain,
                        "mastery": round(sum(x["mastery"] for x in skills) / len(skills), 3) if skills else 0,
                        "answered": sum(x["answered"] for x in skills),
                        "right": sum(x["right"] for x in skills), "skills": skills})
    catching = [dict(r) for r in db.rows("SELECT template,reason,label,topic,hits,closed,last,source"
                                        " FROM traps WHERE learner=? ORDER BY hits DESC,last DESC LIMIT 5", learner)]
    for x in catching:
        x["open"] = x.pop("closed") is None
    score = {"latest": e["latest"], "best": e["best"],
             "points": [{"at": x["at"], "low": x["low"], "high": x["high"],
                         "kind": x["kind"], "session": x["id"]}
                        for x in reversed(estimate._sittings(learner))]}
    rw = {"target": p["rw_target"], "now": p["rw_now"], "source": "yours"}
    math = {"target": p["target"], "band": e["latest"], "gains": g,
            "coverage": {"readiness": round(ready_weight, 3),
                         "met": sum(x["met"] for x in coverage),
                         "total": sum(x["total"] for x in coverage), "types": types,
                         "skills": coverage},
            "domains": domains, "levers": levers(learner, tz, ["points", "band", "readiness"])}
    total = None
    if p["target"] and p["rw_target"]:
        total = {"target": p["target"] + p["rw_target"],
                 "now_low": (e["latest"]["low"] + p["rw_now"]) if e["latest"] and p["rw_now"] else None,
                 "now_high": (e["latest"]["high"] + p["rw_now"]) if e["latest"] and p["rw_now"] else None}
    goals = {"total": total, "subjects": {"math": {"target": p["target"], "band": e["latest"]},
                                             "rw": rw},
             "exam_date": p["exam_date"], "minutes": p["minutes"], "days": p["days"],
             "focus": p["focus"], "first_day": d["days"][0]["day"] if d["active_days"] else None,
             "need": estimate.need(p["target"], learner) if p["target"] else None}
    ranks = {"all": _practice_rank(learner), "exam": _practice_rank(learner, "exam"),
             "country": _practice_rank(learner, "country"), "climb": None,
             "self": _self_rank(learner, b, e["latest"])}
    climb = deps.part("compete", "climb")
    if climb:
        ranks["climb"] = climb(learner)
    words = deps.part("words", "me_stats")
    rank_snapshot = deps.part("compete", "rank_snapshot")
    competition = rank_snapshot(learner, tz) if rank_snapshot else {}
    leaderboard = deps.part("compete", "leaderboard")
    week_board = leaderboard("points", "week", learner=learner, limit=1) if leaderboard else {}
    from . import challenge, daily
    day = daily.today(tz)
    today_board = challenge.board(day, learner, 0)
    played = db.one("SELECT COUNT(*) AS n FROM sessions WHERE learner=? AND"
                    " (kind='challenge' OR contest IS NOT NULL) AND finished IS NOT NULL", learner)["n"]
    best = None
    for row in db.rows("SELECT DISTINCT day FROM sessions WHERE learner=? AND kind='challenge'"
                       " AND day IS NOT NULL AND finished IS NOT NULL", learner):
        mine = challenge.board(row["day"], learner, 0).get("you")
        if mine and (best is None or mine["rank"] < best["rank"]):
            best = {"rank": mine["rank"], "day": row["day"]}
    today_rank = (today_board["you"] or {}).get("rank")
    challenge_summary = {"week_rank": competition.get("week"),
                         "week_players": week_board.get("players"), "played": played,
                         "ahead_today": today_rank - 1 if today_rank else None,
                         "best_rank": best["rank"] if best else None,
                         "best_day": best["day"] if best else None,
                         "rating": competition.get("rating"), "level": competition.get("level")}
    from . import api_shell
    resume = api_shell._resume(learner)
    habits = _habits(learner)
    math["habits"] = habits
    return {"stats": stats, "score": score, "ranks": ranks, "domains": domains,
            "catching": catching, "coverage": coverage, "challenge": challenge_summary,
            "resume": [resume] if resume else [],
            "goals": goals, "subjects": {"math": math, "rw": rw},
            "gains": g, "words": words(learner, tz) if words else None,
            "achievements": achievements.evaluate(learner, tz), "habits": habits}


@router.get("/api/me/summary")
def get_summary(x_learner: str | None = Header(default=None),
                x_tz: int = Depends(tz_of)) -> dict:
    return summary(learner_of(x_learner), x_tz)


@router.get("/api/me/achievements")
def get_achievements(x_learner: str | None = Header(default=None),
                     x_tz: int = Depends(tz_of)) -> list[dict]:
    return achievements.evaluate(learner_of(x_learner), x_tz)


@router.post("/api/me/achievements/seen")
def seen_achievements(x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    db.ensure_learner(learner)
    db.run("UPDATE learners SET ach_seen=? WHERE id=?", deps.now(), learner)
    return {"ok": True}


def feed(learner: str, before: str | None = None, kind: str = "all",
         limit: int = 20, unread: bool = False) -> dict:
    if kind not in ("all", "practice", "test", "mistakes", "challenge", "achievements", "reports"):
        raise HTTPException(422, "unknown feed kind")
    marker = before or "9999"
    seen_row = db.one("SELECT feed_seen FROM learners WHERE id=?", learner)
    seen = seen_row["feed_seen"] if seen_row else None
    items = []
    if kind in ("all", "practice", "test", "challenge") and not unread:
        for r in db.rows("SELECT id,kind,cfg,started,finished,result FROM sessions WHERE learner=?"
                         " AND finished IS NOT NULL AND finished<? AND abandoned IS NULL"
                         " ORDER BY finished DESC LIMIT ?", learner, marker, limit + 1):
            cfg = json.loads(r["cfg"] or "{}")
            result = json.loads(r["result"] or "{}")
            is_test = r["kind"] in deps.TEST_KINDS
            is_challenge = r["kind"] == "challenge" or bool(cfg.get("contest"))
            category = "challenge" if is_challenge else "test" if is_test else "practice"
            if kind != "all" and kind != category:
                continue
            fixed = db.one("SELECT COUNT(*) AS n FROM traps WHERE learner=? AND closed>=?"
                           " AND closed<=?", learner, r["started"], r["finished"])["n"]
            opened = db.one("SELECT COUNT(*) AS n FROM traps WHERE learner=? AND opened>=?"
                            " AND opened<=?", learner, r["started"], r["finished"])["n"]
            words = []
            topics = {x["topic"] for x in db.rows("SELECT DISTINCT topic FROM attempts WHERE learner=?"
                                                   " AND session=?", learner, r["id"])}
            for topic in topics:
                before_rows = db.rows(f"SELECT difficulty,correct,guess,hints FROM attempts WHERE learner=?"
                                      f" AND topic=? AND at<? AND {progress.COUNTED}"
                                      " ORDER BY at DESC,id DESC LIMIT ?", learner, topic,
                                      r["started"], progress.WINDOW)
                after_rows = db.rows(f"SELECT difficulty,correct,guess,hints FROM attempts WHERE learner=?"
                                     f" AND topic=? AND at<=? AND {progress.COUNTED}"
                                     " ORDER BY at DESC,id DESC LIMIT ?", learner, topic,
                                     r["finished"], progress.WINDOW)
                def word(rows):
                    if not rows:
                        return "Not started"
                    value = progress.mastery_of([(x["difficulty"], progress._counts(x)) for x in rows])
                    return "Strong" if value >= progress.STRONG else "Learning" if value < .4 else "Getting there"
                old, new = word(before_rows), word(after_rows)
                if old != new:
                    words.append({"topic": topic, "from": old, "to": new})
            title = ("Quick questions" if cfg.get("source") == "quick" else
                     "Challenge" if is_challenge else "Test" if is_test else "Practice set")
            items.append({"kind": category, "at": r["finished"], "title": title,
                          "detail": f"{result.get('right', 0)} of {result.get('asked', 0)} right",
                          "href": f"/results/report/?s={r['id']}", "session": r["id"],
                          "effect": {"words": words, "fixed": fixed, "opened": opened, "pts": None},
                          "again": {"again": r["id"]},
                          "follow_up": {"from_session": r["id"], "still_open": True,
                                        "scope": "misses"} if opened else None})
    if kind in ("all", "mistakes") and not unread:
        for r in db.rows("SELECT id,template,label,opened,closed,source FROM traps WHERE learner=?"
                         " AND (opened<? OR closed<?) ORDER BY last DESC LIMIT ?",
                         learner, marker, marker, limit + 1):
            if r["closed"] and r["closed"] < marker:
                items.append({"kind": "mistakes", "at": r["closed"], "title": "Mistake fixed",
                              "detail": r["label"], "href": f"/review/?open=trap:{r['id']}"})
            elif r["source"] == "outside" and r["opened"] < marker:
                items.append({"kind": "mistakes", "at": r["opened"], "title": "Mistake logged",
                              "detail": r["label"], "href": f"/review/?open=trap:{r['id']}"})
    if kind in ("all", "achievements"):
        for r in db.rows("SELECT id,tier,at FROM earned WHERE learner=? AND at<?"
                         " ORDER BY at DESC LIMIT ?", learner, marker, limit + 1):
            if unread and seen and r["at"] <= seen:
                continue
            items.append({"kind": "achievements", "at": r["at"],
                          "title": r["id"].replace("_", " ").replace("-", " ").title(),
                          "detail": f"Tier {r['tier']}", "href": "/me/?tab=achievements"})
    if kind in ("all", "reports"):
        for r in db.rows("SELECT id,title,replied,seen FROM reports WHERE learner=?"
                         " AND replied IS NOT NULL AND replied<? ORDER BY replied DESC LIMIT ?",
                         learner, marker, limit + 1):
            if unread and (r["seen"] or (seen and r["replied"] <= seen)):
                continue
            items.append({"kind": "reports", "at": r["replied"],
                          "title": "Your report has a reply", "detail": r["title"],
                          "href": f"/me/settings/#report-{r['id']}"})
    if kind == "all":
        for r in db.rows("SELECT kind,done_at FROM week_goals WHERE learner=? AND done_at IS NOT NULL"
                         " AND done_at<? ORDER BY done_at DESC LIMIT ?", learner, marker, limit + 1):
            if unread and seen and r["done_at"] <= seen:
                continue
            items.append({"kind": "goal", "at": r["done_at"], "title": "Weekly goal met",
                          "detail": r["kind"].replace("_", " "), "href": "/me/?tab=week"})
    items.sort(key=lambda x: (x["at"], x["kind"]), reverse=True)
    since = seen or "0000"
    total_unread = sum(db.one(sql, learner, since)["n"] for sql in (
        "SELECT COUNT(*) AS n FROM earned WHERE learner=? AND at>?",
        "SELECT COUNT(*) AS n FROM reports WHERE learner=? AND replied>? AND seen IS NULL",
        "SELECT COUNT(*) AS n FROM week_goals WHERE learner=? AND done_at>?"))
    page = items[:limit]
    return {"items": page, "next": page[-1]["at"] if len(items) > limit else None,
            "unread": total_unread}


@router.get("/api/me/feed")
def get_feed(before: str | None = None, kind: str = "all",
             limit: int = Query(default=20, ge=1, le=50), unread: bool = False,
             x_learner: str | None = Header(default=None)) -> dict:
    return feed(learner_of(x_learner), before, kind, limit, unread)


@router.post("/api/me/feed/seen")
def seen_feed(x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    db.ensure_learner(learner)
    db.run("UPDATE learners SET feed_seen=? WHERE id=?", deps.now(), learner)
    return {"ok": True}


@router.post("/api/share")
def create_share(x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    token = secrets.token_urlsafe(16)
    db.run("INSERT INTO links(token,learner,kind,created) VALUES (?,?,?,?)",
           token, learner, "progress", deps.now())
    return {"token": token, "url": f"/share/?t={token}"}


@router.get("/api/share")
def list_shares(x_learner: str | None = Header(default=None)) -> list[dict]:
    learner = learner_of(x_learner)
    return [dict(r) for r in db.rows("SELECT token,created,views,last_view FROM links WHERE learner=?"
                                      " AND kind='progress' AND revoked IS NULL ORDER BY created DESC", learner)]


@router.delete("/api/share/{token}")
def revoke_share(token: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    if not db.run("UPDATE links SET revoked=? WHERE token=? AND learner=? AND kind='progress'"
                  " AND revoked IS NULL", deps.now(), token, learner).rowcount:
        raise HTTPException(404, "no such progress link")
    return {"ok": True}


def _private_text(value, learner: str, email: str | None):
    """Shared views never expose a learner credential or account email."""
    if isinstance(value, dict):
        return {k: _private_text(v, learner, email) for k, v in value.items()
                if k not in ("account", "classes", "resume", "credential", "token")}
    if isinstance(value, list):
        return [_private_text(v, learner, email) for v in value]
    if isinstance(value, str):
        return value.replace(learner, "Student").replace(email, "[email]") if email else value.replace(learner, "Student")
    return value


@router.get("/api/shared/{token}")
def shared_view(token: str) -> dict:
    row = db.one("SELECT * FROM links WHERE token=? AND kind='progress' AND revoked IS NULL", token)
    if row is None:
        raise HTTPException(404, "progress link is off")
    learner = row["learner"]
    email = db.one("SELECT email FROM users WHERE learner=?", learner)
    data = summary(learner)
    data.pop("resume", None)
    data.pop("achievements", None)
    public = _private_text(data, learner, email["email"] if email else None)
    public["feed"] = _private_text([{k: x[k] for k in ("kind", "at", "title", "detail")}
                                    for x in feed(learner, limit=20)["items"]], learner,
                                   email["email"] if email else None)
    plan = deps.part("plan", "payload")
    if plan:
        try:
            public["plan"] = _private_text(plan(learner, shared=True), learner,
                                            email["email"] if email else None)
        except HTTPException:
            public["plan"] = None
    db.run("UPDATE links SET views=views+1,last_view=? WHERE token=?", deps.now(), token)
    return public


@router.get("/api/me/export")
def export_me(x_learner: str | None = Header(default=None)) -> JSONResponse:
    learner = learner_of(x_learner)
    p = api_me.profile(learner)
    user = db.one("SELECT email FROM users WHERE learner=?", learner)
    tables = {name: [dict(r) for r in db.rows(f"SELECT * FROM {name} WHERE learner=?", learner)]
              for name in ("attempts", "traps", "saved", "earned", "reports")}
    tables["reports"] = [{k: v for k, v in row.items() if k != "files"}
                          for row in tables["reports"]]
    tables["shares"] = [dict(r) for r in db.rows("SELECT kind,created,revoked,views,last_view"
                                                 " FROM links WHERE learner=?", learner)]
    tables["sessions"] = [dict(r) for r in db.rows("SELECT id,kind,started,finished,result"
                                                   " FROM sessions WHERE learner=?", learner)]
    data = {"profile": {k: v for k, v in p.items() if k not in ("id", "account")},
            "prefs": p["prefs"], "account": {"email": user["email"] if user else None}, **tables}
    day = dt.datetime.now(dt.timezone.utc).date().isoformat()
    return JSONResponse(data, headers={"Content-Disposition":
                    f'attachment; filename="sat-freshman-{day}.json"'})


class DeleteMe(BaseModel):
    confirm: str = Field(min_length=6, max_length=6)


@router.delete("/api/me")
def delete_me(body: DeleteMe, x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    if body.confirm != "DELETE":
        raise HTTPException(422, "type DELETE to confirm")
    gone = "gone:" + secrets.token_hex(12)
    counts = {}
    from . import reports
    with db.transaction():
        challenge = db.run("UPDATE sessions SET learner=? WHERE learner=?"
                           " AND (kind='challenge' OR contest IS NOT NULL)", gone, learner)
        counts["anonymous_challenge"] = challenge.rowcount
        # Plan children refer to plans by id, so delete them first.
        for name in ("plan_days", "plan_overrides", "plan_tasks", "plan_marks",
                     "plan_snapshots", "plan_events"):
            counts[name] = db.run(f"DELETE FROM {name} WHERE plan IN"
                                  " (SELECT id FROM plans WHERE learner=?)", learner).rowcount
        counts["report_files"] = reports.delete_files(learner)
        db.run("DELETE FROM email_changes WHERE learner=?", learner)
        db.run("DELETE FROM signup_claims WHERE session IN"
               " (SELECT id FROM sessions WHERE learner=?)", learner)
        for name in ("attempts", "traps", "saved", "practice_seen", "flags", "notes", "tries",
                     "outside_scores", "word_reviews", "word_state", "my_words", "word_lists",
                     "skill_ratings", "trap_log", "due_days", "official_done", "rw_log",
                     "earned", "week_goals", "passkeys", "webauthn_challenges", "devices",
                     "transfers", "pairs", "reports", "links", "posts", "post_votes",
                     "follows", "nudges", "name_reports", "push_subs", "champions",
                     "rank_snapshots", "contest_members", "sets", "plans"):
            if name in ("pairs", "follows", "nudges", "name_reports"):
                where = {"pairs": "learner=? OR req_learner=?",
                         "follows": "learner=? OR target=?", "nudges": "sender=? OR target=?",
                         "name_reports": "target=? OR reporter=?"}[name]
                args = (learner, learner)
            elif name == "sets":
                where, args = "owner=?", (learner,)
            else:
                where, args = "learner=?", (learner,)
            counts[name] = db.run(f"DELETE FROM {name} WHERE {where}", *args).rowcount
        counts["sessions"] = db.run("DELETE FROM sessions WHERE learner=?", learner).rowcount
        counts["passkey_users"] = db.run("DELETE FROM passkey_users WHERE learner=?", learner).rowcount
        db.run("UPDATE users SET learner=NULL WHERE learner=?", learner)
        db.run('UPDATE retired SET "into"=NULL WHERE "into"=?', learner)
        db.run("UPDATE contests SET owner=? WHERE owner=?", gone, learner)
        counts["learners"] = db.run("DELETE FROM learners WHERE id=?", learner).rowcount
    return {"deleted": counts}


GOAL_KINDS = {"fix_traps", "pass_checks", "reach_word", "take_module", "habit_cap", "minutes"}


def _week_id(day: dt.date) -> str:
    iso = day.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def _week_start(week: str) -> dt.date:
    try:
        year, number = week.split("-W")
        start = dt.date.fromisocalendar(int(year), int(number), 1)
    except (ValueError, TypeError, AttributeError) as exc:
        raise HTTPException(422, "week must be YYYY-WNN") from exc
    if _week_id(start) != week:
        raise HTTPException(422, "invalid week")
    return start


def _goal_progress(learner: str, week: str, kind: str, params: dict,
                   target: int, tz: int = 0) -> tuple[int, bool]:
    start = _week_start(week).isoformat()
    end = (_week_start(week) + dt.timedelta(days=7)).isoformat()
    if kind == "fix_traps":
        topic = params.get("topic")
        if topic and topic not in progress.topics():
            raise HTTPException(422, "unknown goal topic")
        sql = "SELECT COUNT(*) AS n FROM traps WHERE learner=? AND closed>=? AND closed<?"
        args = [learner, start, end]
        if topic:
            sql += " AND topic=?"
            args.append(topic)
        have = db.one(sql, *args)["n"]
    elif kind == "pass_checks":
        have = db.one("SELECT COUNT(*) AS n FROM trap_log WHERE learner=? AND at>=? AND at<?"
                      " AND event IN ('check-pass','check_pass','passed')", learner, start, end)["n"]
    elif kind == "reach_word":
        topic = params.get("topic")
        if topic not in progress.topics():
            raise HTTPException(422, "unknown goal topic")
        mastery = progress.topic_mastery(learner, topic)
        have = round(mastery * 100)
        target = {"Learning": 25, "Getting there": 50, "Strong": 80}.get(params.get("word"), target)
    elif kind == "take_module":
        have = db.one("SELECT COUNT(*) AS n FROM sessions WHERE learner=? AND kind='module'"
                      " AND finished>=? AND finished<?", learner, start, end)["n"]
    elif kind == "habit_cap":
        habit = str(params.get("habit") or "")
        have = db.one("SELECT COUNT(*) AS n FROM attempts WHERE learner=? AND at>=? AND at<?"
                      " AND correct=0 AND reason LIKE ?", learner, start, end, f"%{habit}%")["n"]
        attempted = db.one("SELECT 1 FROM attempts WHERE learner=? AND at>=? AND at<? LIMIT 1",
                           learner, start, end)
        return have, bool(attempted and have <= target)
    else:
        d = progress.days(learner, tz, 5)
        have = sum(x["minutes"] for x in d["days"] if start <= x["day"] < end)
    return have, have >= target


def week_goals(learner: str, week: str | None = None, tz: int = 0) -> list[dict]:
    today = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date()
    week = week or _week_id(today)
    out = []
    for r in db.rows("SELECT * FROM week_goals WHERE learner=? AND week=? ORDER BY created,id", learner, week):
        params = json.loads(r["params"] or "{}")
        have, done = _goal_progress(learner, week, r["kind"], params, r["target"], tz)
        if done and not r["done_at"]:
            db.run("UPDATE week_goals SET done_at=? WHERE learner=? AND week=? AND id=?",
                   deps.now(), learner, week, r["id"])
        title = {"fix_traps": "Fix mistakes", "pass_checks": "Pass check-ins",
                 "reach_word": "Reach a skill level", "take_module": "Take a module",
                 "habit_cap": "Keep a habit down", "minutes": "Study minutes"}[r["kind"]]
        out.append({"id": r["id"], "kind": r["kind"], "params": params,
                    "title": title, "have": have, "target": r["target"],
                    "done": done, "done_at": r["done_at"] or (deps.now() if done else None)})
    return out


def week_summary(learner: str, week: str | None = None, tz: int = 0) -> dict:
    today = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date()
    week = week or _week_id(today)
    monday = _week_start(week)
    last = monday - dt.timedelta(days=7)
    end = monday.isoformat()
    prior = db.one(f"SELECT COUNT(*) AS n,SUM(correct) AS right FROM attempts WHERE learner=?"
                   f" AND at>=? AND at<? AND {progress.COUNTED}", learner, last.isoformat(), end)
    d = progress.days(learner, tz, 5)
    minutes = sum(x["minutes"] for x in d["days"] if last.isoformat() <= x["day"] < end)
    closed = db.one("SELECT COUNT(*) AS n FROM traps WHERE learner=? AND closed>=? AND closed<?",
                    learner, last.isoformat(), end)["n"]
    newly = [r["label"] for r in db.rows("SELECT label FROM traps WHERE learner=?"
                                          " AND opened>=? AND opened<? ORDER BY opened DESC LIMIT 5",
                                          learner, last.isoformat(), end)]
    open_traps = progress.open_traps(learner)
    top = Counter(x["topic"] for x in open_traps).most_common(1)
    suggestions = []
    if top:
        topic, n = top[0]
        suggestions.append({"kind": "fix_traps", "params": {"topic": topic}, "target": n,
                            "why": f"{n} open mistakes in {topic}", "minutes": n * 3})
    due = progress.due_rechecks(learner, today.isoformat())
    if due:
        suggestions.append({"kind": "pass_checks", "params": {}, "target": len(due),
                            "why": f"{len(due)} check-ins are due", "minutes": len(due) * 2})
    rough = next((v for v in progress.board(learner).values() if v["answered"] and
                  v["mastery"] < progress.STRONG), None)
    if rough:
        suggestions.append({"kind": "reach_word", "params": {"topic": rough["topic"], "word": "Strong"},
                            "target": 80, "why": f"{rough['name']} is still growing", "minutes": 25})
    suggestions += [{"kind": "take_module", "params": {}, "target": 1,
                     "why": "A module measures progress under the clock", "minutes": 35},
                    {"kind": "minutes", "params": {}, "target": 60,
                     "why": "An hour of study this week", "minutes": 60}]
    return {"week": week,
            "receipts": {"answered": prior["n"], "right": prior["right"] or 0,
                         "accuracy": round(100 * (prior["right"] or 0) / prior["n"]) if prior["n"] else None,
                         "minutes": minutes, "fixed": closed, "new_mistakes": newly},
            "suggestions": suggestions[:5], "goals": week_goals(learner, week, tz)}


@router.get("/api/me/week")
def get_week(week: str | None = None, x_learner: str | None = Header(default=None),
             x_tz: int = Depends(tz_of)) -> dict:
    return week_summary(learner_of(x_learner), week, x_tz)


class Goal(BaseModel):
    kind: str
    params: dict = Field(default_factory=dict)
    target: int = Field(ge=1, le=10000)


class WeekGoals(BaseModel):
    week: str
    goals: list[Goal] = Field(max_length=3)


@router.put("/api/me/week/goals")
def put_week_goals(body: WeekGoals, x_learner: str | None = Header(default=None),
                   x_tz: int = Depends(tz_of)) -> dict:
    learner = deps.writer_of(x_learner)
    _week_start(body.week)
    if any(g.kind not in GOAL_KINDS for g in body.goals):
        raise HTTPException(422, "unknown weekly goal kind")
    for g in body.goals:
        _goal_progress(learner, body.week, g.kind, g.params, g.target, x_tz)
    with db.transaction():
        db.run("DELETE FROM week_goals WHERE learner=? AND week=?", learner, body.week)
        for g in body.goals:
            db.run("INSERT INTO week_goals(learner,week,id,kind,params,target,created)"
                   " VALUES (?,?,?,?,?,?,?)", learner, body.week, secrets.token_urlsafe(8),
                   g.kind, json.dumps(g.params), g.target, deps.now())
    return {"week": body.week, "goals": week_goals(learner, body.week, x_tz)}
