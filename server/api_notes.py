"""Private notes and text marks on an exact question."""

from __future__ import annotations

import json

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from . import db
from .api_tests import marked_questions, questions_of
from .deps import learner_of, now, session_or_404

router = APIRouter()
STYLES = {"highlight", "strong", "underline", "dashed", "dotted", "box", "strike"}


class Note(BaseModel):
    session: str
    question_id: str
    note: str | None = Field(default=None, max_length=1000)
    marks: list[dict] | None = None


@router.post("/api/notes")
def put_note(body: Note, x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    row = session_or_404(body.session)
    if row["learner"] != learner:
        raise HTTPException(403, "that session belongs to someone else")
    questions = marked_questions(row) if row["finished"] else questions_of(row)
    q = next((item for item in questions if item.get("id") == body.question_id), None)
    if not q or "key" not in q:
        raise HTTPException(404, "no such question in that session")
    if body.marks is not None:
        if len(body.marks) > 50:
            raise HTTPException(422, "marks holds at most 50 marks")
        for mark in body.marks:
            if mark.get("style") not in STYLES or not isinstance(mark.get("note", ""), str) or len(mark.get("note", "")) > 500:
                raise HTTPException(422, "marks has an invalid style or note")
    old = db.one("SELECT note,marks FROM notes WHERE learner=? AND template=? AND seed=?",
                 learner,q["key"],q["seed"])
    note = body.note if "note" in body.model_fields_set else (old["note"] if old else "")
    marks = body.marks if "marks" in body.model_fields_set else (json.loads(old["marks"] or "[]") if old else [])
    db.run("INSERT INTO notes(learner,template,seed,note,marks,at) VALUES (?,?,?,?,?,?)"
           " ON CONFLICT(learner,template,seed) DO UPDATE SET note=excluded.note,marks=excluded.marks,at=excluded.at",
           learner,q["key"],q["seed"],note,json.dumps(marks),now())
    return {"note":note,"marks":marks}
