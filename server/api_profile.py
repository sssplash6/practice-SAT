"""Explanations for the numbers shown across the site (U13, G6)."""

from __future__ import annotations

import datetime as dt
from functools import lru_cache

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from . import api_me, db, deps, estimate, prefs, progress
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
