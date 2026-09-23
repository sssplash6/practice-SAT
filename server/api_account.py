"""The diagnostic's sign-up and the email confirmation."""

from __future__ import annotations

import logging
import secrets

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field

from . import db, mail
from .deps import NAME_OK, now, session_or_404

log = logging.getLogger("satf")
router = APIRouter()


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
    if existing:
        uid = existing["id"]
        # a returning student keeps their verified state; the name may have changed
        if existing["verified"]:
            db.run("UPDATE users SET first=?, last=? WHERE id=?", first, last, uid)
        else:
            db.run("UPDATE users SET first=?, last=?, token=?, token_sent=? WHERE id=?",
                   first, last, token, now(), uid)
    else:
        uid = secrets.token_urlsafe(12)
        db.run("INSERT INTO users (id, first, last, email, token, token_sent, created)"
               " VALUES (?,?,?,?,?,?,?)", uid, first, last, email, token, now(), now())

    db.run("UPDATE sessions SET user_id=? WHERE id=?", uid, sid)

    user = db.one("SELECT * FROM users WHERE id=?", uid)
    delivery = "already-verified" if user["verified"] else mail.send(email, first, token)
    return {"ok": True, "first": first, "verified": bool(user["verified"]), "email": delivery}


@router.get("/api/verify")
def verify(token: str):
    user = db.one("SELECT * FROM users WHERE token=?", token)
    if user is None:
        return RedirectResponse("/diagnostic/verified.html?state=bad", status_code=303)
    db.run("UPDATE users SET verified=1, token=NULL WHERE id=?", user["id"])
    log.info("verified %s", user["email"])
    return RedirectResponse("/diagnostic/verified.html?state=ok", status_code=303)
