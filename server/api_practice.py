"""The map of the skills, and practice sets answered one question at a time."""

from __future__ import annotations

import logging
import secrets

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from . import db, drill, practice, progress, scoring
from .api_me import per_session, profile
from .api_tests import DRILLS, marked_questions
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


class Drill(BaseModel):
    topics: list[str] = Field(default_factory=list)
    count: int | None = 10       # None is a set with no end
    difficulty: list[str] | None = None
    timed: bool = False
    minutes: int | None = Field(default=None, ge=1, le=180)   # a timed set's own clock
    source: str = Field(default="map", max_length=20)
    from_session: str | None = None    # "fix these": the misses of a sitting
    mistakes: bool = False             # every open mistake, twice each
    saved: bool = False                # the saved questions, exactly


def drill_row(sid: str, learner: str):
    """This learner's practice set or challenge sitting. A test is not one."""
    row = session_or_404(sid)
    if row["kind"] not in DRILLS:
        raise HTTPException(404, "no such set")
    return mine(row, learner)


@router.post("/api/drill")
def new_drill(body: Drill, x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    cat = practice.catalogue()
    topics, queue, items, count = list(dict.fromkeys(body.topics)), [], [], body.count

    if body.from_session:
        src = mine(session_or_404(body.from_session), learner)
        if not src["finished"]:
            raise HTTPException(409, "finish that sitting first")
        answers = db.load_answers(src)
        missed = [q for q in marked_questions(src)
                  if "key" in q and not scoring.is_correct(q, answers.get(q["id"]))]
        if not missed:
            raise HTTPException(409, "nothing was missed")
        queue = [q["key"] for q in missed]
        topics = list(dict.fromkeys(q["topic"] for q in missed))
        count = len(queue)
    elif body.mistakes:
        traps = [t for t in progress.open_traps(learner) if not topics or t["topic"] in topics]
        if not traps:
            raise HTTPException(409, "no open mistakes")
        once = list(dict.fromkeys(t["template"] for t in traps))
        queue = once + once              # two clean answers close a mistake
        topics = list(dict.fromkeys(t["topic"] for t in traps))
        count = len(queue)
    elif body.saved:
        items = [[r["template"], r["seed"]]
                 for r in db.rows("SELECT template, seed FROM saved WHERE learner=? ORDER BY at",
                                  learner)]
        if not items:
            raise HTTPException(409, "nothing saved")
        topics = list(dict.fromkeys(practice.topic_of(t) for t, _ in items))
        count = len(items)
    else:
        unknown = [t for t in topics if t not in cat["by_topic"]]
        if unknown:
            raise HTTPException(400, f"no such topic: {', '.join(sorted(unknown)[:3])}")
        if not topics:
            raise HTTPException(400, "pick at least one topic")
        if count is not None and not 1 <= count <= drill.MAX_FIXED:
            raise HTTPException(400, f"a set is 1 to {drill.MAX_FIXED} questions, or endless")

    sid = secrets.token_urlsafe(16)
    drill.create(learner, sid, topics, count, body.difficulty, body.timed, body.source,
                 queue=queue, items=items, minutes=body.minutes)
    row = session_or_404(sid)
    first = drill.next_question(row)
    log.info("drill %s: %s questions over %d topics for %s", sid[:8],
             count if count is not None else "endless", len(topics), learner[:12])
    return {**drill.state(session_or_404(sid)), **first}


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
