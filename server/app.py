"""The serving layer.

    pip install fastapi uvicorn
    python3 -m uvicorn server.app:app --reload --port 8000

A student's first move is the diagnostic, so that is what this serves: one of
ten fixed forms, drawn at random, sixteen questions, marked here. The answer
key never leaves this process -- questions go out without it, responses come
back, and grading happens on this side. A student reading the page source finds
their own answers and nothing else.
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import pathlib
import random
import re
import secrets

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

from . import db, mail, scoring

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("satf")

HERE = pathlib.Path(__file__).resolve().parent
WEB = HERE.parent / "web"
FORMS_PATH = HERE / "forms.json"

# 16 questions at the real test's pace -- 35 minutes for 22 -- is a little
# under 26 minutes. Rounded down, because a diagnostic is not an endurance test.
DURATION_SECONDS = 25 * 60

# what a student is allowed to see about a question
PUBLIC_FIELDS = ("id", "domain", "topic_name", "difficulty", "type",
                 "stem", "choices", "latex", "figure", "table")

app = FastAPI(title="SAT Freshman")
FORMS: dict[int, list[dict]] = {}


@app.on_event("startup")
def startup() -> None:
    db.init()
    if not FORMS_PATH.exists():
        raise SystemExit(f"{FORMS_PATH} is missing. Run tools/build_diagnostics.py first.")
    data = json.loads(FORMS_PATH.read_text())
    for form in data["forms"]:
        FORMS[form["id"]] = form["questions"]
    log.info("loaded %d diagnostic forms, %d questions each",
             len(FORMS), len(next(iter(FORMS.values()))))


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def public(q: dict) -> dict:
    return {k: q[k] for k in PUBLIC_FIELDS if k in q}


def session_or_404(sid: str):
    row = db.one("SELECT * FROM sessions WHERE id=?", sid)
    if row is None:
        raise HTTPException(404, "no such session")
    return row


def payload(row) -> dict:
    qs = FORMS[row["form_id"]]
    return {
        "id": row["id"],
        "section": "Section 1, Module 1: Math",
        "subject": "math",
        "seconds": DURATION_SECONDS,
        "form": row["form_id"],
        "questions": [public(q) for q in qs],
        "answers": db.load_answers(row),
        "finished": row["finished"],
    }


# --------------------------------------------------------------- the session

@app.post("/api/session")
def new_session() -> dict:
    """Start a diagnostic on one of the ten forms, drawn at random."""
    sid = secrets.token_urlsafe(16)
    form_id = random.choice(list(FORMS))
    db.run("INSERT INTO sessions (id, form_id, started) VALUES (?,?,?)", sid, form_id, now())
    log.info("session %s started on form %d", sid[:8], form_id)
    return payload(session_or_404(sid))


@app.get("/api/session/{sid}")
def get_session(sid: str) -> dict:
    return payload(session_or_404(sid))


class Answer(BaseModel):
    question_id: str
    answer: int | str | None = None


@app.post("/api/session/{sid}/answer")
def put_answer(sid: str, body: Answer) -> dict:
    row = session_or_404(sid)
    if row["finished"]:
        raise HTTPException(409, "this test is already finished")
    if not any(q["id"] == body.question_id for q in FORMS[row["form_id"]]):
        raise HTTPException(400, "that question is not on this form")

    answers = db.load_answers(row)
    if body.answer is None or body.answer == "":
        answers.pop(body.question_id, None)
    else:
        answers[body.question_id] = body.answer
    db.save_answers(sid, answers)
    return {"saved": True, "answered": len(answers)}


@app.post("/api/session/{sid}/finish")
def finish(sid: str) -> dict:
    """Mark the paper. The result is stored now and released after signup."""
    row = session_or_404(sid)
    if row["finished"]:
        return {"finished": row["finished"], "already": True}

    result = scoring.score(FORMS[row["form_id"]], db.load_answers(row))
    db.run("UPDATE sessions SET finished=?, result=? WHERE id=?",
           now(), json.dumps(result), sid)
    log.info("session %s finished: %d/%d", sid[:8], result["right"], result["asked"])
    return {"finished": now(), "right": result["right"], "asked": result["asked"]}


# ---------------------------------------------------------------- the signup

NAME_OK = re.compile(r"^[^\d<>@]{1,60}$")


class Signup(BaseModel):
    first: str = Field(min_length=1, max_length=60)
    last: str = Field(min_length=1, max_length=60)
    email: EmailStr


@app.post("/api/session/{sid}/signup")
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


@app.get("/api/verify")
def verify(token: str):
    user = db.one("SELECT * FROM users WHERE token=?", token)
    if user is None:
        return RedirectResponse("/diagnostic/verified.html?state=bad", status_code=303)
    db.run("UPDATE users SET verified=1, token=NULL WHERE id=?", user["id"])
    log.info("verified %s", user["email"])
    return RedirectResponse("/diagnostic/verified.html?state=ok", status_code=303)


# --------------------------------------------------------------- the results

@app.get("/api/session/{sid}/results")
def results(sid: str) -> dict:
    row = session_or_404(sid)
    if not row["finished"]:
        raise HTTPException(409, {"need": "finish"})
    if not row["user_id"]:
        raise HTTPException(403, {"need": "signup"})

    user = db.one("SELECT * FROM users WHERE id=?", row["user_id"])
    out = json.loads(row["result"])
    out["first"] = user["first"]
    out["verified"] = bool(user["verified"])

    # the review: every question with what they put and what was right
    answers = db.load_answers(row)
    out["review"] = [
        {
            **public(q),
            "given": answers.get(q["id"]),
            "answer": q["answer"],
            "rationale": q["rationale"],
            "correct": scoring.is_correct(q, answers.get(q["id"])),
        }
        for q in FORMS[row["form_id"]]
    ]
    return out


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "forms": len(FORMS)}


# The site itself. Mounted last so every /api route above wins the match.
if WEB.is_dir():
    app.mount("/", StaticFiles(directory=WEB, html=True), name="web")
else:                                              # pragma: no cover
    @app.get("/", response_class=HTMLResponse)
    def missing() -> str:
        return f"<p>No web directory at {WEB}</p>"
