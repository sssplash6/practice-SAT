"""Private notes and text marks on an exact question, and a student's own rule
for a whole question type (seed -1, practice.md P21)."""

from __future__ import annotations

import json

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from . import db
from .api_tests import marked_questions, questions_of
from .deps import now, session_or_404, writer_of

router = APIRouter()
STYLES = {"highlight", "strong", "underline", "dashed", "dotted", "box", "strike"}
TYPE_RULE = -1              # notes.seed for a type rule
RULE_MAX = 140


class Note(BaseModel):
    session: str | None = None
    question_id: str | None = None
    attempt_id: int | None = None      # V19: the server resolves the template from the learner's own attempt
    scope: str = Field(default="item", pattern="^(item|type)$")
    note: str | None = Field(default=None, max_length=1000)
    marks: list[dict] | None = None


def _pair(learner: str, body: Note) -> tuple[str, int]:
    """(template, seed) from the learner's own attempt or sitting, never from the client."""
    if body.attempt_id is not None:
        a = db.one("SELECT template, seed FROM attempts WHERE id=? AND learner=?", body.attempt_id, learner)
        if not a:
            raise HTTPException(404, "no such attempt of yours")
        return a["template"], a["seed"]
    if not body.session or not body.question_id:
        raise HTTPException(422, "send attempt_id, or session and question_id")
    row = session_or_404(body.session)
    if row["learner"] != learner:
        raise HTTPException(403, "that session belongs to someone else")
    questions = marked_questions(row) if row["finished"] else questions_of(row)
    q = next((item for item in questions if item.get("id") == body.question_id), None)
    if not q or "key" not in q:
        raise HTTPException(404, "no such question in that session")
    return q["key"], q["seed"]


@router.post("/api/notes")
def put_note(body: Note, x_learner: str | None = Header(default=None)) -> dict:
    learner = writer_of(x_learner)
    template, seed = _pair(learner, body)
    rule = body.scope == "type"
    if rule:
        seed = TYPE_RULE
        if body.marks:
            raise HTTPException(422, "a type rule is a note, with no marks")
        if body.note is not None and len(body.note) > RULE_MAX:
            raise HTTPException(422, f"a type rule is at most {RULE_MAX} characters")
    if body.marks is not None:
        if len(body.marks) > 50:
            raise HTTPException(422, "marks holds at most 50 marks")
        for mark in body.marks:
            if mark.get("style") not in STYLES or not isinstance(mark.get("note", ""), str) or len(mark.get("note", "")) > 500:
                raise HTTPException(422, "marks has an invalid style or note")
    # R6: the template goes back only to a write made from the learner's own
    # attempt (Review); the session page never learns it, live tests and
    # today's challenge included
    shown = {"template": template} if body.attempt_id is not None else {}
    old = db.one("SELECT note,marks FROM notes WHERE learner=? AND template=? AND seed=?", learner, template, seed)
    note = body.note if "note" in body.model_fields_set else (old["note"] if old else "")
    marks = body.marks if "marks" in body.model_fields_set else (json.loads(old["marks"] or "[]") if old else [])
    note, marks = (note or "").strip() and note, marks or []
    if not note and not marks:
        # empty values delete the row (QBank §3.3.5)
        db.run("DELETE FROM notes WHERE learner=? AND template=? AND seed=?", learner, template, seed)
        return {"note": None, "marks": [], "deleted": True, "type_rule": rule, **shown}
    db.run("INSERT INTO notes(learner,template,seed,note,marks,at) VALUES (?,?,?,?,?,?)"
           " ON CONFLICT(learner,template,seed) DO UPDATE SET note=excluded.note,marks=excluded.marks,at=excluded.at",
           learner, template, seed, note or "", json.dumps(marks), now())
    return {"note": note or "", "marks": marks, "type_rule": rule, **shown}
