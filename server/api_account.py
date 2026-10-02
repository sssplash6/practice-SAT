"""The diagnostic's sign-up and the email confirmation."""

from __future__ import annotations

import logging
import json
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field

from . import account, api_results, db, mail, practice, scoring
from .api_tests import marked_questions, public
from .deps import NAME_OK, learner_of, now, session_or_404

log = logging.getLogger("satf")
router = APIRouter()
router.include_router(account.router)


def init() -> None:
    """Pending diagnostic claims must not confer account access before email proof."""
    db.run("""CREATE TABLE IF NOT EXISTS signup_claims (
        token TEXT PRIMARY KEY, user_id TEXT NOT NULL, session TEXT NOT NULL,
        created TEXT NOT NULL, expires TEXT NOT NULL
    )""")
    db.run("CREATE INDEX IF NOT EXISTS signup_claims_session ON signup_claims(session)")


class Signup(BaseModel):
    first: str = Field(min_length=1, max_length=60)
    last: str = Field(min_length=1, max_length=60)
    email: EmailStr


@router.post("/api/session/{sid}/signup")
def signup(sid: str, body: Signup) -> dict:
    row = session_or_404(sid)
    if not row["finished"]:
        raise HTTPException(409, "finish the test first")

    first, last = body.first.strip(), body.last.strip()
    if not (NAME_OK.match(first) and NAME_OK.match(last)):
        raise HTTPException(422, "that does not look like a name")
    email = body.email.strip().lower()

    existing = db.one("SELECT * FROM users WHERE email=?", email)
    token = secrets.token_urlsafe(24)
    created = now()
    expires = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
    with db.transaction():
        if existing:
            uid = existing["id"]
            # Never change an existing account's profile from an unproved request.
            if not existing["verified"]:
                db.run("UPDATE users SET token=?, token_sent=? WHERE id=?", token, created, uid)
        else:
            uid = secrets.token_urlsafe(12)
            db.run("INSERT INTO users (id, first, last, email, token, token_sent, created)"
                   " VALUES (?,?,?,?,?,?,?)", uid, first, last, email, token, created, created)
        db.run("DELETE FROM signup_claims WHERE session=?", sid)
        db.run("INSERT INTO signup_claims (token,user_id,session,created,expires) VALUES (?,?,?,?,?)",
               token, uid, sid, created, expires)

    # The response says nothing about whether the mailbox already has an account.
    delivery = mail.send(email, existing["first"] if existing and existing["first"] else first, token)
    return {"ok": True, "first": first, "verified": False, "email": delivery}


@router.get("/api/verify")
def verify(token: str):
    claim = db.one("SELECT * FROM signup_claims WHERE token=?", token)
    if claim is None or claim["expires"] < now():
        return RedirectResponse("/diagnostic/verified.html?state=bad", status_code=303)
    with db.transaction():
        claimed = db.run("DELETE FROM signup_claims WHERE token=? AND expires>=?",
                         token, now()).rowcount
        if not claimed:
            return RedirectResponse("/diagnostic/verified.html?state=bad", status_code=303)
        db.run("UPDATE users SET verified=1, token=NULL WHERE id=?", claim["user_id"])
        db.run("UPDATE sessions SET user_id=? WHERE id=?",
               claim["user_id"], claim["session"])
        session = db.one("SELECT learner FROM sessions WHERE id=?", claim["session"])
        user = db.one("SELECT learner FROM users WHERE id=?", claim["user_id"])
        if session and session["learner"] and user and user["learner"] is None:
            db.run("UPDATE users SET learner=? WHERE id=?", session["learner"], claim["user_id"])
    log.info("verified diagnostic signup %s", claim["user_id"])
    if session and session["learner"] and user and user["learner"] is None:
        account.start_swap(session["learner"])
    return RedirectResponse("/diagnostic/verified.html?state=ok", status_code=303)


@router.get("/api/session/{sid}/results")
def saved_diagnostic_results(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    """Passkey-only and Google-saved learners can see their diagnostic result."""
    row = session_or_404(sid)
    if row["kind"] != "diagnostic" or row["user_id"]:
        # this route is registered before Results' own: every other sitting goes to Results' handler (the integration walk
        # found `api_results.results` does not exist, so every report request was a 500)
        return api_results.get_results(sid, x_learner)
    if not row["finished"]:
        raise HTTPException(409, {"need": "finish"})
    if not x_learner or learner_of(x_learner) != row["learner"] or not account.saved(row["learner"]):
        raise HTTPException(403, {"need": "signup"})
    out = json.loads(row["result"] or "{}")
    out["mode"] = "diagnostic"
    out["first"] = (db.one("SELECT name FROM learners WHERE id=?", row["learner"]) or
                    {"name": None})["name"]
    out["verified"] = True
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
