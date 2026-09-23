"""Open mistakes and saved questions."""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from . import db, progress
from .api_tests import DRILLS, questions_of
from .deps import learner_of, mine, now, session_or_404

router = APIRouter()


@router.get("/api/mistakes")
def mistakes(x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    names = progress.topics()
    saved = [{"template": r["template"], "topic": r["topic"], "name": names[r["topic"]].name,
              "at": r["at"]}
             for r in db.rows("SELECT template, topic, at FROM saved WHERE learner=? ORDER BY at DESC",
                              learner)]
    traps = [{**t, "name": names[t["topic"]].name, "domain": names[t["topic"]].domain}
             for t in progress.open_traps(learner)]
    return {"traps": traps, "saved": saved}


class Save(BaseModel):
    session: str
    question_id: str
    on: bool = True


@router.post("/api/saved")
def save_question(body: Save, x_learner: str | None = Header(default=None)) -> dict:
    """Keep a question to see again. It is stored as the triple that makes it,
    and a saved set serves it with its key -- so only a practice set's
    questions can be kept, and a challenge's only once answered, or saving
    would be a way to read a key before answering."""
    learner = learner_of(x_learner)
    row = mine(session_or_404(body.session), learner)
    q = None
    if row["kind"] in DRILLS:
        q = next((x for x in questions_of(row) if x["id"] == body.question_id), None)
    if q is None or "key" not in q:
        raise HTTPException(404, "no such question in that session")
    if body.on and row["kind"] == "challenge" and body.question_id not in db.load_answers(row):
        raise HTTPException(409, "answer it first")
    if body.on:
        db.run("INSERT OR IGNORE INTO saved (learner, template, seed, topic, at) VALUES (?,?,?,?,?)",
               learner, q["key"], q["seed"], q["topic"], now())
    else:
        db.run("DELETE FROM saved WHERE learner=? AND template=? AND seed=?",
               learner, q["key"], q["seed"])
    return {"saved": body.on}
