"""The daily challenge: today's ten, one sitting each, and the board."""

from __future__ import annotations

import logging
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException

from . import challenge, daily, db, drill
from .deps import DATE_OK, LEARNER_OK, SECONDS_PER_QUESTION, learner_of, tz_of

log = logging.getLogger("satf")
router = APIRouter()


def challenge_row(learner: str, day: str):
    return db.one("SELECT * FROM sessions WHERE kind='challenge' AND learner=? AND day=?", learner, day)


@router.get("/api/challenge")
def get_challenge(x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    day = daily.today(x_tz)
    row = challenge_row(learner, day)
    b = challenge.board(day, learner, limit=5)
    return {"day": day, "count": challenge.CHALLENGE_SIZE,
            "seconds": challenge.CHALLENGE_SIZE * SECONDS_PER_QUESTION,
            "session": row["id"] if row else None,
            "finished": bool(row and row["finished"]),
            "board": b}


@router.post("/api/challenge/start")
def start_challenge(x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    """Today's ten, one sitting each. Coming back resumes it; it never restarts."""
    learner = learner_of(x_learner)
    day = daily.today(x_tz)
    row = challenge_row(learner, day)
    if row is None:
        qs = challenge.challenge(day)
        sid = secrets.token_urlsafe(16)
        drill.create(learner, sid, list(dict.fromkeys(q["topic"] for q in qs)), len(qs), None, True,
                     "challenge", items=[[q["key"], q["seed"]] for q in qs],
                     kind="challenge", fixed=True, day=day)
        row = challenge_row(learner, day)           # this start's, or one made at the same moment
        log.info("challenge %s started by %s", day, learner[:12])
    if row["finished"]:
        return {**drill.state(row), "done": True}
    return {**drill.state(row), **drill.next_question(row)}


@router.get("/api/challenge/board")
def challenge_board(day: str | None = None, x_learner: str | None = Header(default=None),
                    x_tz: int = Depends(tz_of)) -> dict:
    if day and not DATE_OK.match(day):
        raise HTTPException(422, "day is YYYY-MM-DD")
    me = x_learner.strip() if x_learner and LEARNER_OK.match(x_learner.strip()) else None
    return challenge.board(day or daily.today(x_tz), me)
