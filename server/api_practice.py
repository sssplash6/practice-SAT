"""The map of the skills, and practice sets answered one question at a time."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from . import db, drill, progress
from .api_me import per_session, profile
from .api_tests import DRILLS
from .deps import learner_of, mine, session_or_404

log = logging.getLogger("satf")
router = APIRouter()


@router.get("/api/map")
def get_map(x_learner: str | None = Header(default=None)) -> dict:
    """The 19 topics with mastery and open mistakes, and the coach's pick."""
    learner = learner_of(x_learner)
    board = progress.board(learner)
    return {"topics": list(board.values()),
            "coach": progress.coach(learner, count=per_session(profile(learner)))}


def drill_row(sid: str, learner: str):
    """This learner's practice set or challenge sitting. A test is not one."""
    row = session_or_404(sid)
    if row["kind"] not in DRILLS:
        raise HTTPException(404, "no such set")
    return mine(row, learner)


@router.post("/api/drill")
def new_drill(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    sid = drill.create(learner, body)
    row = session_or_404(sid)
    first = drill.next_question(row)
    log.info("drill %s started for %s", sid[:8], learner[:12])
    return {**drill.state(session_or_404(sid)), **first}


@router.post("/api/drill/preview")
def drill_preview(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    return drill.preview(learner_of(x_learner), body)


@router.get("/api/drill/{sid}")
def get_drill(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    return drill.state(drill_row(sid, learner_of(x_learner)))


@router.post("/api/drill/{sid}/next")
def drill_next(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    row = drill_row(sid, learner_of(x_learner))
    if row["finished"]:
        raise HTTPException(409, "this set is finished")
    return drill.next_question(row)


class DrillAnswer(BaseModel):
    question_id: str
    answer: int | str | None = None
    ms: int | None = Field(default=None, ge=0)


@router.post("/api/drill/{sid}/answer")
def drill_answer(sid: str, body: DrillAnswer, x_learner: str | None = Header(default=None)) -> dict:
    row = drill_row(sid, learner_of(x_learner))
    if row["finished"]:
        raise HTTPException(409, "this set is finished")
    if body.answer is None or body.answer == "":
        raise HTTPException(400, "no answer")
    try:
        return drill.answer(row, body.question_id, body.answer, body.ms)
    except KeyError:
        raise HTTPException(400, "that question is not in this set")
    except drill.Closed as e:
        raise HTTPException(409, str(e))


@router.post("/api/drill/{sid}/finish")
def drill_finish(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    row = drill_row(sid, learner)
    out = drill.finish(row)
    out["next"] = progress.coach(learner, count=per_session(profile(learner)))
    return out
