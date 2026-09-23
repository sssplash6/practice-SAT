"""One sitting's results, and every sitting a learner has finished."""

from __future__ import annotations

import json

from fastapi import APIRouter, Header, HTTPException

from . import db, practice, scoring
from .api_tests import marked_questions, public
from .deps import learner_of, session_or_404

router = APIRouter()


@router.get("/api/session/{sid}/results")
def results(sid: str) -> dict:
    row = session_or_404(sid)
    if not row["finished"]:
        raise HTTPException(409, {"need": "finish"})
    # The diagnostic holds its results back until there is somewhere to send
    # them. Practice does not: the student asked for these questions and
    # already knows who they are.
    if row["kind"] == "diagnostic" and not row["user_id"]:
        raise HTTPException(403, {"need": "signup"})

    out = json.loads(row["result"])
    out["mode"] = row["kind"]
    if row["kind"] == "mock":
        out["mock"] = row["mock_id"]
    user = db.one("SELECT * FROM users WHERE id=?", row["user_id"]) if row["user_id"] else None
    out["first"] = user["first"] if user else None
    out["verified"] = bool(user["verified"]) if user else False

    # the review: every question with what they put, what was right, and --
    # for a wrong option -- the mistake that option is built from
    answers = db.load_answers(row)
    review = []
    for q in marked_questions(row):
        given = answers.get(q["id"])
        ok = scoring.is_correct(q, given)
        mistake = None
        if not ok and q["type"] == "mcq" and isinstance(given, int) and 0 <= given < 4:
            reason = (q.get("reasons") or [""] * 4)[given]
            mistake = reason[:1].upper() + reason[1:] if reason else None
        review.append({**public(q), "topic": q.get("topic"), "skill": practice.skill_of(q),
                       "given": given, "answer": q["answer"], "rationale": q["rationale"],
                       "correct": ok, "mistake": mistake})
    out["review"] = review
    out["started"], out["finished"] = row["started"], row["finished"]
    return out


@router.get("/api/history")
def history(x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    out = []
    for r in db.rows("SELECT id, kind, mock_id, started, finished, result, cfg FROM sessions"
                     " WHERE learner=? AND finished IS NOT NULL ORDER BY finished DESC LIMIT 200",
                     learner):
        res = json.loads(r["result"] or "{}")
        cfg = json.loads(r["cfg"] or "{}")
        out.append({"id": r["id"], "kind": r["kind"], "started": r["started"],
                    "finished": r["finished"], "right": res.get("right"), "asked": res.get("asked"),
                    "estimate": res.get("estimate"),
                    "topics": [t["topic"] for t in res.get("topics", [])] or cfg.get("topics", [])})
    return {"sessions": out}
