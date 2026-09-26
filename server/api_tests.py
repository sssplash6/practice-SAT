"""Sittings: the diagnostic, the shelf mocks and the fresh sections, and the
paper helpers every other router reads a sitting through."""

from __future__ import annotations

import datetime as dt
import json
import logging
import random
import secrets

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from . import blueprint, db, drill, practice, progress, scoring
from .deps import LEARNER_OK, SECONDS_PER_QUESTION, learner_of, now, session_or_404, writer_of

log = logging.getLogger("satf")
router = APIRouter()

# A mock is the real thing: 35 minutes a module, whatever is in it.
MOCK_MODULE_SECONDS = 35 * 60

# what a student is allowed to see about a question
PUBLIC_FIELDS = ("id", "domain", "topic_name", "difficulty", "type",
                 "stem", "choices", "latex", "figure", "table")

# filled by app.py's startup
FORMS: dict[int, list[dict]] = {}
MOCKS: dict[str, dict] = {}


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

@router.post("/api/session")
def new_session(x_learner: str | None = Header(default=None)) -> dict:
    """Start a diagnostic on one of the ten forms, drawn at random."""
    sid = secrets.token_urlsafe(16)
    form_id = random.choice(list(FORMS))
    learner = x_learner.strip() if x_learner and LEARNER_OK.match(x_learner.strip()) else None
    db.run("INSERT INTO sessions (id, kind, form_id, learner, started) VALUES (?,?,?,?,?)",
           sid, "diagnostic", form_id, learner, now())
    log.info("session %s started on form %d", sid[:8], form_id)
    return payload(session_or_404(sid))


@router.get("/api/session/{sid}")
def get_session(sid: str) -> dict:
    return payload(session_or_404(sid))


class Answer(BaseModel):
    question_id: str
    answer: int | str | None = None


@router.post("/api/session/{sid}/answer")
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


@router.post("/api/session/{sid}/finish")
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

@router.get("/api/mocks")
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


@router.post("/api/mock/new")
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


@router.post("/api/mock/{num}")
def start_mock(num: str, body: MockStart | None = None,
               x_learner: str | None = Header(default=None)) -> dict:
    if num not in MOCKS:
        raise HTTPException(404, f"no mock {num}")
    body_learner = writer_of(body.learner) if body and body.learner.strip() else None
    header_learner = writer_of(x_learner) if x_learner else None
    if body_learner and header_learner and body_learner != header_learner:
        raise HTTPException(403, "learner tokens disagree")
    learner = body_learner or header_learner or writer_of("anon:" + secrets.token_urlsafe(9))
    sid = secrets.token_urlsafe(16)
    stamp = now()
    db.run("INSERT INTO sessions (id, kind, mock_id, module, learner, started, module_started)"
           " VALUES (?,?,?,?,?,?,?)", sid, "mock", num, 1, learner, stamp, stamp)
    log.info("mock %s started as %s", num, sid[:8])
    return payload(session_or_404(sid))
