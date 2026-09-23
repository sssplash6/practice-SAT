"""The day: the learner's today, and the question of the day for everyone."""

from __future__ import annotations

import datetime as dt
import json

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from . import daily, db, drill, progress, scoring
from .api_me import per_session, profile
from .deps import LEARNER_OK, learner_of, tz_of

router = APIRouter()


def latest_score(learner: str) -> dict | None:
    """The newest section estimate a sitting has produced, and when."""
    for r in db.rows("SELECT id, kind, result, finished FROM sessions WHERE learner=?"
                     " AND finished IS NOT NULL AND kind IN ('mock','module','diagnostic')"
                     " ORDER BY finished DESC", learner):
        est = (json.loads(r["result"] or "{}") or {}).get("estimate")
        if est:
            return {**est, "kind": r["kind"], "session": r["id"], "at": r["finished"]}
    return None


@router.get("/api/today")
def get_today(x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    p = profile(learner)
    days = progress.days(learner, x_tz)
    exam = None
    if p["exam_date"]:
        left = (dt.date.fromisoformat(p["exam_date"]) - dt.date.fromisoformat(days["today"])).days
        exam = {"date": p["exam_date"], "days": left}
    # a section or module finished today is a plan's test day done
    tested = any(progress._local_day(r["finished"], x_tz).isoformat() == days["today"]
                 for r in db.rows("SELECT finished FROM sessions WHERE learner=?"
                                  " AND kind IN ('mock', 'module') AND finished IS NOT NULL", learner))
    return {"profile": p, "days": days, "exam": exam, "tested": tested, "score": latest_score(learner),
            "coach": progress.coach(learner, count=per_session(p)),
            "mistakes": len(progress.open_traps(learner))}


# ------------------------------------------------------- the day, for everyone

def qotd_feedback(q: dict, given, day: str) -> dict:
    ok = scoring.is_correct(q, given)
    reason = ""
    if not ok and isinstance(given, int) and 0 <= given < 4:
        reason = (q.get("reasons") or [""] * 4)[given]
    crowd = db.one("SELECT COUNT(*) n, COALESCE(SUM(correct), 0) r FROM attempts WHERE session=?",
                   f"qotd:{day}")
    return {"correct": ok, "given": given, "answer": q["answer"],
            "answer_index": "ABCD".index(q["answer"]),
            "mistake": reason[:1].upper() + reason[1:] if reason else None,
            "rationale": q["rationale"],
            "crowd": {"answered": crowd["n"], "right": crowd["r"]}}


@router.get("/api/qotd")
def get_qotd(x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    day = daily.today(x_tz)
    q = daily.question(day)
    out = {"day": day, "question": drill.public(q), "mine": None}
    if x_learner and LEARNER_OK.match(x_learner.strip()):
        had = db.one("SELECT given FROM attempts WHERE learner=? AND session=?",
                     x_learner.strip(), f"qotd:{day}")
        if had:
            given = int(had["given"]) if had["given"] is not None and had["given"].isdigit() else had["given"]
            out["mine"] = qotd_feedback(q, given, day)
    return out


class Reply(BaseModel):
    answer: int | str
    day: str | None = None      # the day it was shown; past midnight that is not today


@router.post("/api/qotd")
def answer_qotd(body: Reply, x_learner: str | None = Header(default=None),
                x_tz: int = Depends(tz_of)) -> dict:
    """One answer a day. A second one is a double tap, and gets the first back."""
    learner = learner_of(x_learner)
    day = daily.today(x_tz)
    if body.day is not None and body.day != day:
        raise HTTPException(409, "that was another day's question")
    q = daily.question(day)
    if progress.record(learner, f"qotd:{day}", q, body.answer, once=True) is None:
        had = db.one("SELECT given FROM attempts WHERE learner=? AND session=?", learner, f"qotd:{day}")
        given = int(had["given"]) if had["given"] is not None and had["given"].isdigit() else had["given"]
        return qotd_feedback(q, given, day)
    return qotd_feedback(q, body.answer, day)
