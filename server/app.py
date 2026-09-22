"""The serving layer.

    pip install fastapi uvicorn
    python3 -m uvicorn server.app:app --reload --port 8000

A student's first move is the diagnostic, so that is what this serves: one of
ten fixed forms, drawn at random, twenty questions, marked here. The answer
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

from . import db, mail, practice, scoring

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("satf")

HERE = pathlib.Path(__file__).resolve().parent
WEB = HERE.parent / "web"
FORMS_PATH = HERE / "forms.json"
MOCKS_PATH = HERE / "mocks.json"

# The real test gives 35 minutes to 22 math questions, so about 95 seconds each.
# Deriving the duration from the form means changing the blueprint cannot leave
# a stale clock behind.
SECONDS_PER_QUESTION = 95

# A mock is the real thing: 35 minutes a module, whatever is in it.
MOCK_MODULE_SECONDS = 35 * 60

# what a student is allowed to see about a question
PUBLIC_FIELDS = ("id", "domain", "topic_name", "difficulty", "type",
                 "stem", "choices", "latex", "figure", "table")

MAX_PRACTICE = 120          # the sticker sheet stops here too

app = FastAPI(title="SAT Freshman")
FORMS: dict[int, list[dict]] = {}
MOCKS: dict[str, dict] = {}


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
    # the bank's lazy globals are not thread safe on first touch, so they are
    # warmed here rather than on whichever request happens to arrive first
    cat = practice.catalogue()
    log.info("practice catalogue: %d topics, %d templates",
             len(cat["by_topic"]), sum(len(v) for v in cat["by_topic"].values()))

    if MOCKS_PATH.exists():
        for m in json.loads(MOCKS_PATH.read_text())["mocks"]:
            MOCKS[m["id"]] = m
        log.info("loaded %d mock sections", len(MOCKS))
    else:
        log.warning("%s is missing; run tools/build_mocks.py", MOCKS_PATH)


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def public(q: dict) -> dict:
    return {k: q[k] for k in PUBLIC_FIELDS if k in q}


def mock_module(row, module: int | None = None, route: str | None = None) -> list[dict]:
    """One module of a mock. Module 2 exists in two forms and the route picks."""
    m = MOCKS[row["mock_id"]]
    module = module or row["module"] or 1
    if module == 1:
        return m["module1"]
    return m["module2_" + (route or row["route"] or "upper")]


def mock_all(row) -> list[dict]:
    """Both modules, for marking the section once it is over."""
    return mock_module(row, 1) + mock_module(row, 2)


def questions_of(row) -> list[dict]:
    """A diagnostic points at a form, a practice set carries its own, and a
    mock serves whichever of its two modules the student is in."""
    if row["kind"] == "practice":
        return json.loads(row["questions"] or "[]")
    if row["kind"] == "mock":
        return mock_module(row)
    return FORMS[row["form_id"]]


def session_or_404(sid: str):
    row = db.one("SELECT * FROM sessions WHERE id=?", sid)
    if row is None:
        raise HTTPException(404, "no such session")
    return row


def duration(row) -> int:
    if row["kind"] == "mock":
        return MOCK_MODULE_SECONDS
    return len(questions_of(row)) * SECONDS_PER_QUESTION


def remaining(row) -> int:
    """Time left, from when the live module started -- not from when the page
    loaded, or a reload is free time, and the clock is the one thing on this
    screen a student has a reason to game. A mock's second module gets its own
    thirty-five minutes, so the clock restarts with it rather than running on.
    """
    began = row["module_started"] or row["started"]
    elapsed = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(began)).total_seconds()
    return max(0, int(duration(row) - elapsed))


def section_label(row) -> str:
    if row["kind"] == "practice":
        return "Mixed practice"
    if row["kind"] == "mock":
        return f"Section 2, Module {row['module'] or 1}: Math"
    return "Section 1, Module 1: Math"


def payload(row) -> dict:
    qs = questions_of(row)
    practice_mode = row["kind"] == "practice"
    out = {
        "id": row["id"],
        "mode": row["kind"],
        "section": section_label(row),
        "subject": "math",
        # practice is not an exam, so it is not on a clock
        "seconds": None if practice_mode else remaining(row),
        "form": row["form_id"],
        "questions": [public(q) for q in qs],
        "answers": db.load_answers(row),
        "finished": row["finished"],
    }
    if row["kind"] == "mock":
        out["mock"] = row["mock_id"]
        out["module"] = row["module"] or 1
    return out


# --------------------------------------------------------------- the session

@app.post("/api/session")
def new_session() -> dict:
    """Start a diagnostic on one of the ten forms, drawn at random."""
    sid = secrets.token_urlsafe(16)
    form_id = random.choice(list(FORMS))
    db.run("INSERT INTO sessions (id, kind, form_id, started) VALUES (?,?,?,?)",
           sid, "diagnostic", form_id, now())
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
    if not any(q["id"] == body.question_id for q in questions_of(row)):
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
    """Mark the paper. The result is stored now and released after signup.

    A mock has two modules, and finishing the first one does not finish the
    test: it routes. Which module 2 a student gets is decided from module 1
    alone, as on the day, and there is no way back into module 1 afterwards.
    """
    row = session_or_404(sid)
    if row["finished"]:
        return {"finished": row["finished"], "already": True}

    if row["kind"] == "mock" and (row["module"] or 1) == 1:
        answers = db.load_answers(row)
        m1 = mock_module(row, 1)
        right = sum(1 for q in m1 if scoring.is_correct(q, answers.get(q["id"])))
        route = scoring.route_after(right, len(m1))
        db.run("UPDATE sessions SET module=2, route=?, module1=?, module_started=? WHERE id=?",
               route, json.dumps({"right": right, "asked": len(m1)}), now(), sid)
        log.info("mock %s (%s): module 1 %d/%d -> %s module 2",
                 row["mock_id"], sid[:8], right, len(m1), route)
        return {"next_module": 2, "finished_module": 1,
                "right": right, "asked": len(m1)}

    marked = mock_all(row) if row["kind"] == "mock" else questions_of(row)
    result = scoring.score(marked, db.load_answers(row))
    if row["kind"] == "mock":
        result["mock"] = row["mock_id"]
        result["route"] = row["route"]
        result["module1"] = json.loads(row["module1"] or "{}")
        result["estimate"] = scoring.section_score(result, row["route"])
    db.run("UPDATE sessions SET finished=?, result=? WHERE id=?",
           now(), json.dumps(result), sid)
    log.info("session %s finished: %d/%d", sid[:8], result["right"], result["asked"])
    return {"finished": now(), "right": result["right"], "asked": result["asked"]}


# ------------------------------------------------------------------ the mock

@app.get("/api/mocks")
def list_mocks(learner: str = "") -> dict:
    """What is on the shelf, and what this learner last scored on each."""
    scores: dict[str, int] = {}
    if learner:
        for r in db.conn().execute(
            "SELECT mock_id, result FROM sessions"
            " WHERE kind='mock' AND learner=? AND finished IS NOT NULL"
            " ORDER BY finished", (learner,)
        ):
            est = (json.loads(r["result"]) or {}).get("estimate") or {}
            if est:
                # the middle of the band, because a cassette spine fits a number
                scores[r["mock_id"]] = int(round((est["low"] + est["high"]) / 20) * 10)
    return {"mocks": [
        {"id": m["id"], "box": m["box"],
         "questions": len(m["module1"]) + len(m["module2_upper"]),
         "score": scores.get(m["id"])}
        for m in MOCKS.values()
    ]}


class MockStart(BaseModel):
    learner: str = Field(default="", max_length=120)


@app.post("/api/mock/{num}")
def start_mock(num: str, body: MockStart | None = None) -> dict:
    if num not in MOCKS:
        raise HTTPException(404, f"no mock {num}")
    sid = secrets.token_urlsafe(16)
    learner = (body.learner.strip() if body else "") or ("anon:" + secrets.token_urlsafe(9))
    stamp = now()
    db.run("INSERT INTO sessions (id, kind, mock_id, module, learner, started, module_started)"
           " VALUES (?,?,?,?,?,?,?)", sid, "mock", num, 1, learner, stamp, stamp)
    log.info("mock %s started as %s", num, sid[:8])
    return payload(session_or_404(sid))


# -------------------------------------------------------------- the practice

class Practice(BaseModel):
    """The sticker sheet, as the mixed page keeps it: topic slug -> how many."""
    basket: dict[str, int]
    learner: str = Field(default="", max_length=120)


@app.post("/api/practice")
def new_practice(body: Practice) -> dict:
    """Build a mixed set. Nothing here is drawn at random; see practice.py."""
    cat = practice.catalogue()
    basket = {k: int(v) for k, v in body.basket.items() if int(v) > 0}
    unknown = [k for k in basket if k not in cat["by_topic"]]
    if unknown:
        raise HTTPException(400, f"no such topic: {', '.join(sorted(unknown)[:3])}")
    if not basket:
        raise HTTPException(400, "pick at least one question")
    total = sum(basket.values())
    if total > MAX_PRACTICE:
        raise HTTPException(400, f"{total} questions is over the limit of {MAX_PRACTICE}")

    # An anonymous learner still gets a history, because repetition is felt by
    # the person and not by the account.
    learner = body.learner.strip() or ("anon:" + secrets.token_urlsafe(9))
    seen, seen_stems = db.seen_for(learner)

    cards = practice.build(basket, learner, seen, seen_stems)
    if not cards:
        raise HTTPException(409, "nothing left to ask on those topics")
    questions = [practice.to_question(c, i + 1) for i, c in enumerate(cards)]

    sid = secrets.token_urlsafe(16)
    db.run("INSERT INTO sessions (id, kind, questions, learner, started) VALUES (?,?,?,?,?)",
           sid, "practice", json.dumps(questions, ensure_ascii=False), learner, now())
    db.remember(learner, [
        {"key": c.key, "seed": c.seed, "stem_hash": practice.stem_hash(c.item.stem)}
        for c in cards
    ], now())

    if len(cards) < total:
        log.warning("asked for %d, built %d -- topics are running thin", total, len(cards))
    log.info("practice %s: %d questions over %d topics for %s",
             sid[:8], len(cards), len(basket), learner[:12])

    out = payload(session_or_404(sid))
    out["learner"] = learner
    out["asked"] = total
    return out


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
        for q in (mock_all(row) if row["kind"] == "mock" else questions_of(row))
    ]
    return out


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "forms": len(FORMS)}


@app.middleware("http")
async def revalidate(request, call_next):
    """Ask the browser to check before reusing a file.

    Without this a page keeps running the stylesheet and script it loaded an
    hour ago, which during development means testing a fix that is not there.
    The etag still means nothing is re-downloaded when it has not changed.
    """
    response = await call_next(request)
    if not request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-cache"
    return response


# The site itself. Mounted last so every /api route above wins the match.
if WEB.is_dir():
    app.mount("/", StaticFiles(directory=WEB, html=True), name="web")
else:                                              # pragma: no cover
    @app.get("/", response_class=HTMLResponse)
    def missing() -> str:
        return f"<p>No web directory at {WEB}</p>"
