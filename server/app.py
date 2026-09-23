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

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

from . import blueprint, daily, db, drill, mail, practice, progress, scoring

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

# A learner is the token in their browser, sent as X-Learner. It is minted on
# the client, so it is checked for shape and nothing else.
LEARNER_OK = re.compile(r"^[A-Za-z0-9:_\-]{4,120}$")


def learner_of(x_learner: str | None) -> str:
    v = (x_learner or "").strip()
    if not LEARNER_OK.match(v):
        raise HTTPException(400, "send your learner token in the X-Learner header")
    return v

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
    # what every template can make, which fresh sections and difficulty
    # filters both need, surveyed once rather than on a student's first request
    can = blueprint.abilities()
    log.info("surveyed %d templates", len(can))


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def public(q: dict) -> dict:
    return {k: q[k] for k in PUBLIC_FIELDS if k in q}


FRESH = "new"               # a mock built for its sitting, not taken off the shelf
DRILLS = ("drill", "challenge")     # answered one at a time through /api/drill, never as a paper


def mock_module(row, module: int | None = None, route: str | None = None) -> list[dict]:
    """One module of a mock. Module 2 exists in two forms and the route picks.

    A fresh mock carries its own questions: module 1 made when it started,
    module 2 made when module 1 routed, so only the route taken is ever built.
    """
    module = module or row["module"] or 1
    if row["mock_id"] == FRESH:
        built = json.loads(row["questions"] or "{}")
        return built["module1"] if module == 1 else built.get("module2", [])
    m = MOCKS[row["mock_id"]]
    if module == 1:
        return m["module1"]
    return m["module2_" + (route or row["route"] or "upper")]


def mock_all(row) -> list[dict]:
    """Both modules, for marking the section once it is over."""
    return mock_module(row, 1) + mock_module(row, 2)


def questions_of(row) -> list[dict]:
    """A diagnostic points at a form, a practice set carries its own, and a
    mock serves whichever of its two modules the student is in."""
    if row["kind"] in ("practice", "drill", "challenge"):
        return json.loads(row["questions"] or "[]")
    if row["kind"] == "module":
        return json.loads(row["questions"] or "{}")["module1"]
    if row["kind"] == "mock":
        return mock_module(row)
    return FORMS[row["form_id"]]


def marked_questions(row) -> list[dict]:
    """Everything a finished sitting asked, for marking and for review."""
    return mock_all(row) if row["kind"] == "mock" else questions_of(row)


def session_or_404(sid: str):
    row = db.one("SELECT * FROM sessions WHERE id=?", sid)
    if row is None:
        raise HTTPException(404, "no such session")
    return row


def duration(row) -> int:
    if row["kind"] in ("mock", "module"):
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
    if row["kind"] == "module":
        return "Module 1: Math"
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
    if row["kind"] in ("mock", "module") and json.loads(row["cfg"] or "{}").get("timed") is False:
        out["seconds"] = None           # sat untimed, by choice
    return out


# --------------------------------------------------------------- the session

@app.post("/api/session")
def new_session(x_learner: str | None = Header(default=None)) -> dict:
    """Start a diagnostic on one of the ten forms, drawn at random."""
    sid = secrets.token_urlsafe(16)
    form_id = random.choice(list(FORMS))
    learner = x_learner.strip() if x_learner and LEARNER_OK.match(x_learner.strip()) else None
    db.run("INSERT INTO sessions (id, kind, form_id, learner, started) VALUES (?,?,?,?,?)",
           sid, "diagnostic", form_id, learner, now())
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
    if row["kind"] in DRILLS:
        raise HTTPException(409, "a practice set is answered through /api/drill")
    if row["finished"]:
        raise HTTPException(409, "this test is already finished")
    if not any(q["id"] == body.question_id for q in questions_of(row)):
        raise HTTPException(400, "that question is not on this form")

    # one answer changed in place, so two sent together cannot undo each other
    if body.answer is None or body.answer == "":
        ok = db.clear_answer(sid, body.question_id)
    else:
        ok = db.set_answer(sid, body.question_id, body.answer)
    if not ok:
        raise HTTPException(409, "this test is already finished")
    return {"saved": True, "answered": len(db.load_answers(session_or_404(sid)))}


@app.post("/api/session/{sid}/finish")
def finish(sid: str) -> dict:
    """Mark the paper. The result is stored now and released after signup.

    A mock has two modules, and finishing the first one does not finish the
    test: it routes. Which module 2 a student gets is decided from module 1
    alone, as on the day, and there is no way back into module 1 afterwards.
    """
    row = session_or_404(sid)
    if row["kind"] in DRILLS:
        raise HTTPException(409, "a practice set is finished through /api/drill")
    if row["finished"]:
        return {"finished": row["finished"], "already": True}

    if row["kind"] == "mock" and (row["module"] or 1) == 1:
        answers = db.load_answers(row)
        m1 = mock_module(row, 1)
        right = sum(1 for q in m1 if scoring.is_correct(q, answers.get(q["id"])))
        route = scoring.route_after(right, len(m1))
        questions = row["questions"]
        if row["mock_id"] == FRESH:
            # module 2 is made now, for the route module 1 earned and nothing
            # else, from questions this student has never been given
            built = json.loads(row["questions"])
            built["module2"] = fresh_module(row["learner"], "module2_" + route)
            questions = json.dumps(built, ensure_ascii=False)
        # The route and module 2 are set in one statement that only a paper
        # still in module 1 matches, so a second finish sent at the same moment
        # cannot route it again; it is told where the first one went.
        if not db.run("UPDATE sessions SET module=2, route=?, module1=?, module_started=?, questions=?"
                      " WHERE id=? AND COALESCE(module, 1)=1 AND finished IS NULL",
                      route, json.dumps({"right": right, "asked": len(m1)}), now(), questions, sid).rowcount:
            m = json.loads(session_or_404(sid)["module1"] or "{}")
            return {"next_module": 2, "finished_module": 1, "right": m.get("right"), "asked": m.get("asked")}
        log.info("mock %s (%s): module 1 %d/%d -> %s module 2",
                 row["mock_id"], sid[:8], right, len(m1), route)
        return {"next_module": 2, "finished_module": 1,
                "right": right, "asked": len(m1)}

    marked = marked_questions(row)
    answers = db.load_answers(row)
    result = scoring.score(marked, answers)
    if row["kind"] == "mock":
        result["mock"] = row["mock_id"]
        result["route"] = row["route"]
        result["module1"] = json.loads(row["module1"] or "{}")
        result["estimate"] = scoring.section_score(result, row["route"])
    # marked once: a second finish at the same moment finds it done and files nothing
    if not db.run("UPDATE sessions SET finished=?, result=? WHERE id=? AND finished IS NULL",
                  now(), json.dumps(result), sid).rowcount:
        return {"finished": session_or_404(sid)["finished"], "already": True}
    # every answered question goes on the learner's map, whatever the mode
    if row["learner"]:
        progress.record_paper(row["learner"], sid, marked, answers)
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


def fresh_module(learner: str, form: str) -> list[dict]:
    """A module built to the blueprint now, from questions this learner has
    never been given, and remembered so they never are again."""
    qs = blueprint.module(form, drill._builder(learner))
    db.remember(learner, [{"key": q["key"], "seed": q["seed"],
                           "stem_hash": practice.stem_hash(q["stem"])} for q in qs], now())
    return qs


class NewMock(BaseModel):
    full: bool = True           # the whole adaptive section, or one module on its own
    timed: bool = True


@app.post("/api/mock/new")
def new_mock(body: NewMock | None = None, x_learner: str | None = Header(default=None)) -> dict:
    """A section that has never existed before and will never be sat again.

    The shelf above is seven fixed sections. This is the one to use: the bank
    makes a new one for every sitting, to the same blueprint, so a student can
    sit a hundred and never meet a question twice.
    """
    learner = learner_of(x_learner)
    full = True if body is None else body.full
    timed = True if body is None else body.timed
    sid = secrets.token_urlsafe(16)
    stamp = now()
    m1 = fresh_module(learner, "module1")
    db.run("INSERT INTO sessions (id, kind, mock_id, module, learner, started, module_started,"
           " questions, cfg) VALUES (?,?,?,?,?,?,?,?,?)",
           sid, "mock" if full else "module", FRESH, 1, learner, stamp, stamp,
           json.dumps({"module1": m1}, ensure_ascii=False), json.dumps({"timed": timed}))
    log.info("fresh %s %s for %s", "section" if full else "module", sid[:8], learner[:12])
    return payload(session_or_404(sid))


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


# --------------------------------------------------------------- the learner

TARGETS = range(200, 810, 10)
DATE_OK = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DAYS_OK = re.compile(r"^[01]{7}$")


FOCUS_STATES = ("focus", "normal", "strong")
MAX_FOCUS = 2               # of four domains, as theirs allow four of eight


def profile(learner: str) -> dict:
    row = db.one("SELECT * FROM learners WHERE id=?", learner)
    base = {"id": learner, "name": None, "exam_date": None, "target": None,
            "minutes": None, "days": None, "current": None, "tests": None, "focus": None}
    out = {**base, **({k: row[k] for k in base} if row else {})}
    out["focus"] = json.loads(out["focus"]) if out["focus"] else {}
    return out


def per_session(p: dict) -> int:
    """How many questions a study day's minutes hold, at the real test's pace."""
    if not p.get("minutes"):
        return 10
    return max(5, min(drill.MAX_FIXED, round(p["minutes"] * 60 / SECONDS_PER_QUESTION)))


@app.get("/api/me")
def get_me(x_learner: str | None = Header(default=None), x_tz: int = Header(default=0, ge=-840, le=720)) -> dict:
    learner = learner_of(x_learner)
    return {"profile": profile(learner), "days": progress.days(learner, x_tz)}


class Me(BaseModel):
    name: str | None = Field(default=None, max_length=24)
    exam_date: str | None = None
    target: int | None = None
    minutes: int | None = None
    days: str | None = None
    current: int | None = None          # where the plan starts from
    tests: str | None = None            # "weekly" or "daily"
    focus: dict[str, str] | None = None # domain -> focus / normal / strong


@app.put("/api/me")
def put_me(body: Me, x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    got = body.model_dump(exclude_unset=True)
    if "name" in got and got["name"] is not None:
        got["name"] = got["name"].strip() or None
        if got["name"] and not NAME_OK.match(got["name"]):
            raise HTTPException(422, "that name has characters it cannot have")
    if got.get("exam_date"):
        try:
            if not DATE_OK.match(got["exam_date"]):
                raise ValueError
            dt.date.fromisoformat(got["exam_date"])        # 2026-02-30 matches the pattern
        except ValueError:
            raise HTTPException(422, "exam_date is a real date, YYYY-MM-DD")
    if got.get("target") is not None and got["target"] not in TARGETS:
        raise HTTPException(422, "target is a Math score, 200 to 800 in tens")
    if got.get("minutes") is not None and not 5 <= got["minutes"] <= 240:
        raise HTTPException(422, "minutes is between 5 and 240")
    if got.get("days") and not DAYS_OK.match(got["days"]):
        raise HTTPException(422, "days is seven 0s and 1s, Monday first")
    if got.get("current") is not None and got["current"] not in TARGETS:
        raise HTTPException(422, "current is a Math score, 200 to 800 in tens")
    if got.get("tests") is not None and got["tests"] not in ("weekly", "daily"):
        raise HTTPException(422, "tests is weekly or daily")
    if got.get("focus") is not None:
        domains = set(progress.DOMAINS)
        if any(d not in domains or v not in FOCUS_STATES for d, v in got["focus"].items()):
            raise HTTPException(422, "focus maps a domain to focus, normal or strong")
        if sum(v == "focus" for v in got["focus"].values()) > MAX_FOCUS:
            raise HTTPException(422, f"at most {MAX_FOCUS} domains on focus")
        # normal is the default and is not stored
        got["focus"] = json.dumps({d: v for d, v in got["focus"].items() if v != "normal"}) or None
    if not db.one("SELECT 1 FROM learners WHERE id=?", learner):
        db.run("INSERT INTO learners (id, created) VALUES (?,?)", learner, now())
    for k, v in got.items():
        db.run(f"UPDATE learners SET {k}=?, updated=? WHERE id=?", v, now(), learner)
    return {"profile": profile(learner)}


class Carry(BaseModel):
    learner: str = Field(max_length=120)       # the code this device held until now


@app.post("/api/me/carry")
def carry(body: Carry, x_learner: str | None = Header(default=None)) -> dict:
    """Bring another code's progress into this one, so switching a device to
    another device's code keeps what both have done."""
    to = learner_of(x_learner)
    frm = body.learner.strip()
    if not LEARNER_OK.match(frm):
        raise HTTPException(400, "that is not a learner code")
    return {"moved": 0 if frm == to else progress.carry(frm, to)}


def latest_score(learner: str) -> dict | None:
    """The newest section estimate a sitting has produced, and when."""
    for r in db.rows("SELECT id, kind, result, finished FROM sessions WHERE learner=?"
                     " AND finished IS NOT NULL AND kind IN ('mock','module','diagnostic')"
                     " ORDER BY finished DESC", learner):
        est = (json.loads(r["result"] or "{}") or {}).get("estimate")
        if est:
            return {**est, "kind": r["kind"], "session": r["id"], "at": r["finished"]}
    return None


@app.get("/api/map")
def get_map(x_learner: str | None = Header(default=None)) -> dict:
    """The 19 topics with mastery and open mistakes, and the coach's pick."""
    learner = learner_of(x_learner)
    board = progress.board(learner)
    return {"topics": list(board.values()),
            "coach": progress.coach(learner, count=per_session(profile(learner)))}


@app.get("/api/today")
def get_today(x_learner: str | None = Header(default=None), x_tz: int = Header(default=0, ge=-840, le=720)) -> dict:
    learner = learner_of(x_learner)
    p = profile(learner)
    days = progress.days(learner, x_tz)
    exam = None
    if p["exam_date"]:
        left = (dt.date.fromisoformat(p["exam_date"]) - dt.date.fromisoformat(days["today"])).days
        exam = {"date": p["exam_date"], "days": left}
    # a section or module finished today is a plan's test day done
    tested = any(progress._local_day(r["finished"], x_tz).isoformat() == days["today"]
                 for r in db.rows("SELECT finished FROM sessions WHERE learner=?"
                                  " AND kind IN ('mock', 'module') AND finished IS NOT NULL", learner))
    return {"profile": p, "days": days, "exam": exam, "tested": tested, "score": latest_score(learner),
            "coach": progress.coach(learner, count=per_session(p)),
            "mistakes": len(progress.open_traps(learner))}


@app.get("/api/history")
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


@app.get("/api/mistakes")
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


@app.post("/api/saved")
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


# ----------------------------------------------------------------- the drill

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


def mine(row, learner: str):
    if row["learner"] and row["learner"] != learner:
        raise HTTPException(403, "that session belongs to someone else")
    return row


def drill_row(sid: str, learner: str):
    """This learner's practice set or challenge sitting. A test is not one."""
    row = session_or_404(sid)
    if row["kind"] not in DRILLS:
        raise HTTPException(404, "no such set")
    return mine(row, learner)


@app.post("/api/drill")
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


@app.get("/api/drill/{sid}")
def get_drill(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    return drill.state(drill_row(sid, learner_of(x_learner)))


@app.post("/api/drill/{sid}/next")
def drill_next(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    row = drill_row(sid, learner_of(x_learner))
    if row["finished"]:
        raise HTTPException(409, "this set is finished")
    return drill.next_question(row)


class DrillAnswer(BaseModel):
    question_id: str
    answer: int | str | None = None
    ms: int | None = Field(default=None, ge=0)


@app.post("/api/drill/{sid}/answer")
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


@app.post("/api/drill/{sid}/finish")
def drill_finish(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    row = drill_row(sid, learner)
    out = drill.finish(row)
    out["next"] = progress.coach(learner, count=per_session(profile(learner)))
    return out


# ------------------------------------------------------- the day, for everyone

def qotd_feedback(q: dict, given, day: str) -> dict:
    ok = scoring.is_correct(q, given)
    reason = ""
    if not ok and isinstance(given, int) and 0 <= given < 4:
        reason = (q.get("reasons") or [""] * 4)[given]
    crowd = db.one("SELECT COUNT(*) n, COALESCE(SUM(correct), 0) r FROM attempts WHERE session=?",
                   f"qotd:{day}")
    return {"correct": ok, "given": given, "answer": q["answer"],
            "answer_index": "ABCD".index(q["answer"]),
            "mistake": reason[:1].upper() + reason[1:] if reason else None,
            "rationale": q["rationale"],
            "crowd": {"answered": crowd["n"], "right": crowd["r"]}}


@app.get("/api/qotd")
def get_qotd(x_learner: str | None = Header(default=None), x_tz: int = Header(default=0, ge=-840, le=720)) -> dict:
    day = daily.today(x_tz)
    q = daily.question(day)
    out = {"day": day, "question": drill.public(q), "mine": None}
    if x_learner and LEARNER_OK.match(x_learner.strip()):
        had = db.one("SELECT given FROM attempts WHERE learner=? AND session=?",
                     x_learner.strip(), f"qotd:{day}")
        if had:
            given = int(had["given"]) if had["given"] is not None and had["given"].isdigit() else had["given"]
            out["mine"] = qotd_feedback(q, given, day)
    return out


class Reply(BaseModel):
    answer: int | str
    day: str | None = None      # the day it was shown; past midnight that is not today


@app.post("/api/qotd")
def answer_qotd(body: Reply, x_learner: str | None = Header(default=None),
                x_tz: int = Header(default=0, ge=-840, le=720)) -> dict:
    """One answer a day. A second one is a double tap, and gets the first back."""
    learner = learner_of(x_learner)
    day = daily.today(x_tz)
    if body.day is not None and body.day != day:
        raise HTTPException(409, "that was another day's question")
    q = daily.question(day)
    if progress.record(learner, f"qotd:{day}", q, body.answer, once=True) is None:
        had = db.one("SELECT given FROM attempts WHERE learner=? AND session=?", learner, f"qotd:{day}")
        given = int(had["given"]) if had["given"] is not None and had["given"].isdigit() else had["given"]
        return qotd_feedback(q, given, day)
    return qotd_feedback(q, body.answer, day)


def challenge_row(learner: str, day: str):
    return db.one("SELECT * FROM sessions WHERE kind='challenge' AND learner=? AND day=?", learner, day)


@app.get("/api/challenge")
def get_challenge(x_learner: str | None = Header(default=None), x_tz: int = Header(default=0, ge=-840, le=720)) -> dict:
    learner = learner_of(x_learner)
    day = daily.today(x_tz)
    row = challenge_row(learner, day)
    b = daily.board(day, learner, limit=5)
    return {"day": day, "count": daily.CHALLENGE_SIZE,
            "seconds": daily.CHALLENGE_SIZE * SECONDS_PER_QUESTION,
            "session": row["id"] if row else None,
            "finished": bool(row and row["finished"]),
            "board": b}


@app.post("/api/challenge/start")
def start_challenge(x_learner: str | None = Header(default=None), x_tz: int = Header(default=0, ge=-840, le=720)) -> dict:
    """Today's ten, one sitting each. Coming back resumes it; it never restarts."""
    learner = learner_of(x_learner)
    day = daily.today(x_tz)
    row = challenge_row(learner, day)
    if row is None:
        qs = daily.challenge(day)
        sid = secrets.token_urlsafe(16)
        drill.create(learner, sid, list(dict.fromkeys(q["topic"] for q in qs)), len(qs), None, True,
                     "challenge", items=[[q["key"], q["seed"]] for q in qs],
                     kind="challenge", fixed=True, day=day)
        row = challenge_row(learner, day)           # this start's, or one made at the same moment
        log.info("challenge %s started by %s", day, learner[:12])
    if row["finished"]:
        return {**drill.state(row), "done": True}
    return {**drill.state(row), **drill.next_question(row)}


@app.get("/api/challenge/board")
def challenge_board(day: str | None = None, x_learner: str | None = Header(default=None),
                    x_tz: int = Header(default=0, ge=-840, le=720)) -> dict:
    if day and not DATE_OK.match(day):
        raise HTTPException(422, "day is YYYY-MM-DD")
    me = x_learner.strip() if x_learner and LEARNER_OK.match(x_learner.strip()) else None
    return daily.board(day or daily.today(x_tz), me)


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
