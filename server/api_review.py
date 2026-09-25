"""Review's endpoints (spec/rebuild-v2.md §3.9.5, R2, R5; spec/v2-upgrades/review.md V1-V19).

Every route is owner-only and subject-aware (?subject=, math by default).
The model -- the daily list, counts, blind spots, the ledger, calibration and
the trap sheet -- is server/review.py; this file validates at the boundary,
reads the rows and shapes them for the page:

  /mistakes/                        307 to /review/?tab=redo, keeping the query (R2)
  GET  /api/mistakes                open traps and saved questions (kept for test_flow)
  POST /api/saved, PATCH /api/saved keep a question, its note (R6) and why (V3)
  POST /api/session/{sid}/flag      mark a test question for review (R5)
  POST /api/flags                   the same for practice sets and the challenge, and the hub's Unmark
  POST /api/mistakes/dismiss | restore | reopen | add
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from . import db, deps, practice, progress, review
from .api_tests import DRILLS, questions_of
from .deps import TEST_KINDS, learner_of, mine, now, session_or_404, writer_of

router = APIRouter()
NOTE_MAX = 280              # a saved question's note (§5)
QID = r"^[A-Za-z0-9_.:\-]{1,64}$"
TEMPLATE = r"^[a-z0-9_.]{1,80}$"


def bad(field: str, reason: str = "invalid value"):
    raise HTTPException(422, {"field": field, "reason": reason})


def known(template: str) -> str:
    """A catalogue template, or 404: an address is never guessed at."""
    try:
        return practice.topic_of(template)
    except Exception:
        raise HTTPException(404, "no such question type")


# ------------------------------------------------------------------ the old page (R2)

@router.get("/mistakes", include_in_schema=False)
@router.get("/mistakes/", include_in_schema=False)
@router.get("/mistakes/index.html", include_in_schema=False)
def mistakes_page(request: Request) -> RedirectResponse:
    query = request.url.query
    return RedirectResponse("/review/?tab=redo" + (f"&{query}" if query else ""), status_code=307)


@router.get("/api/mistakes")
def mistakes(x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    names = progress.topics()
    saved = [{"template": r["template"], "topic": r["topic"], "name": names[r["topic"]].name,
              "at": r["at"]}
             for r in db.rows("SELECT template, topic, at FROM saved WHERE learner=? ORDER BY at DESC",
                              learner) if r["topic"] in names]
    traps = [{**t, "name": names[t["topic"]].name, "domain": names[t["topic"]].domain,
              "status": review.status(t), "of": review.of(t)}
             for t in progress.open_traps(learner) if t["topic"] in names]
    return {"traps": traps, "saved": saved}


# ------------------------------------------------------------------ saved (§5, V3, R6)

class Save(BaseModel):
    session: str | None = Field(default=None, max_length=64)
    question_id: str | None = Field(default=None, pattern=QID)
    template: str | None = Field(default=None, pattern=TEMPLATE)
    seed: int | None = Field(default=None, ge=0)
    note: str | None = Field(default=None, max_length=NOTE_MAX)
    why: str | None = Field(default=None, pattern="^(trick|hard)$")
    on: bool = True


def _pair_of_session(learner: str, sid: str, qid: str | None, on: bool) -> tuple[str, int, str]:
    """(template, seed, topic) of a question in the learner's own sitting. A
    practice set's question, an answered challenge question, and any question
    of a finished test (blanks included) can be kept; a live test's never,
    or saving would be a way to read a key before answering."""
    row = mine(session_or_404(sid), learner)
    q = None
    if row["kind"] in DRILLS:
        q = next((x for x in questions_of(row) if x["id"] == qid), None)
    elif row["kind"] in TEST_KINDS and row["finished"]:
        q = next((x for x in progress._paper(row) if x.get("id") == qid), None)
    if q is None or "key" not in q:
        raise HTTPException(404, "no such question in that session")
    if on and row["kind"] == "challenge" and qid not in db.load_answers(row):
        raise HTTPException(409, "answer it first")
    return q["key"], q["seed"], q["topic"]


def _pair(learner: str, body) -> tuple[str, int, str, str | None, str | None]:
    if body.session:
        if not body.question_id:
            bad("question_id", "required with session")
        return (*_pair_of_session(learner, body.session, body.question_id, body.on),
                body.session, body.question_id)
    if body.template is None or body.seed is None:
        bad("template", "send session and question_id, or template and seed")
    topic = known(body.template)
    if body.on and deps.access(learner, body.template, body.seed) is None:
        raise HTTPException(404, "no such question of yours")
    return body.template, body.seed, topic, None, None


def put_note(learner: str, template: str, seed: int, note: str | None) -> str | None:
    """R6's one store: the note on this exact question, its marks kept."""
    note = (note or "").strip()
    old = db.one("SELECT marks FROM notes WHERE learner=? AND template=? AND seed=?", learner, template, seed)
    marks = json.loads(old["marks"] or "[]") if old else []
    if not note and not marks:
        db.run("DELETE FROM notes WHERE learner=? AND template=? AND seed=?", learner, template, seed)
        return None
    db.run("INSERT INTO notes(learner,template,seed,note,marks,at) VALUES (?,?,?,?,?,?)"
           " ON CONFLICT(learner,template,seed) DO UPDATE SET note=excluded.note, at=excluded.at",
           learner, template, seed, note, json.dumps(marks), now())
    return note or None


@router.post("/api/saved")
def save_question(body: Save, x_learner: str | None = Header(default=None)) -> dict:
    """Keep a question for good (R5), by its sitting or, from Review, by its
    address. Unsave keeps the note (R6: it is the question's note, and undo
    re-posts it anyway)."""
    learner = writer_of(x_learner)
    template, seed, topic, session, qid = _pair(learner, body)
    if not body.on:
        db.run("DELETE FROM saved WHERE learner=? AND template=? AND seed=?", learner, template, seed)
        return {"saved": False}
    with db.atomic():
        db.ensure_learner(learner)
        db.run("INSERT INTO saved (learner, template, seed, topic, at, session, qid, why) VALUES (?,?,?,?,?,?,?,?)"
               " ON CONFLICT(learner,template,seed) DO UPDATE SET why=COALESCE(excluded.why, saved.why),"
               " session=COALESCE(saved.session, excluded.session), qid=COALESCE(saved.qid, excluded.qid)",
               learner, template, seed, topic, now(), session, qid, body.why)
        note = put_note(learner, template, seed, body.note) if body.note is not None else None
    return {"saved": True, "note": note, "why": body.why}


class SavedEdit(BaseModel):
    template: str = Field(pattern=TEMPLATE)
    seed: int = Field(ge=0)
    note: str | None = Field(default=None, max_length=NOTE_MAX)
    why: str | None = Field(default=None, pattern="^(trick|hard|)$")


@router.patch("/api/saved")
def edit_saved(body: SavedEdit, x_learner: str | None = Header(default=None)) -> dict:
    """A saved question's note (280 characters, 422 above) and why tag."""
    learner = writer_of(x_learner)
    row = db.one("SELECT why FROM saved WHERE learner=? AND template=? AND seed=?", learner, body.template, body.seed)
    if not row:
        raise HTTPException(404, "that question is not saved")
    sent = body.model_fields_set
    why = row["why"]
    if "why" in sent:
        why = body.why or None
        db.run("UPDATE saved SET why=? WHERE learner=? AND template=? AND seed=?", why, learner, body.template, body.seed)
    if "note" in sent:
        note = put_note(learner, body.template, body.seed, body.note)
    else:
        n = db.one("SELECT note FROM notes WHERE learner=? AND template=? AND seed=?", learner, body.template, body.seed)
        note = n["note"] or None if n else None
    return {"note": note, "why": why}


# ------------------------------------------------------------------ marks for review (R5)

class Flag(BaseModel):
    question_id: str = Field(pattern=QID)
    on: bool = True


class HubFlag(BaseModel):
    session: str = Field(max_length=64)
    question_id: str | None = Field(default=None, pattern=QID)
    template: str | None = Field(default=None, pattern=TEMPLATE)
    seed: int | None = Field(default=None, ge=0)
    on: bool = True


def _own(sid: str, learner: str):
    """The flag endpoints check ownership outright: GET /api/session/{sid} has
    no owner check, so holding an id must not be enough to set a flag, and a
    sitting with no learner belongs to nobody."""
    row = session_or_404(sid)
    if row["learner"] != learner:
        raise HTTPException(403, "that session belongs to someone else")
    return row


def flags_of(learner: str, sid: str) -> list[str]:
    return [r["qid"] for r in db.rows("SELECT qid FROM flags WHERE learner=? AND session=? ORDER BY at",
                                      learner, sid)]


def set_flag(learner: str, row, qid: str, on: bool) -> dict:
    """Upsert or delete one flag. The qid must be on the sitting's paper; the
    row carries the (template, seed) so Review and the builder can find it."""
    q = next((x for x in progress._paper(row) if x.get("id") == qid), None)
    if q is None or "key" not in q:
        raise HTTPException(400, "that question is not on this paper")
    if on:
        db.run("INSERT OR IGNORE INTO flags(learner,session,qid,template,seed,topic,at) VALUES (?,?,?,?,?,?,?)",
               learner, row["id"], qid, q["key"], q["seed"], q["topic"], now())
    else:
        db.run("DELETE FROM flags WHERE learner=? AND session=? AND qid=?", learner, row["id"], qid)
    return {"flags": flags_of(learner, row["id"])}


@router.post("/api/session/{sid}/flag")
def flag_test(sid: str, body: Flag, x_learner: str | None = Header(default=None)) -> dict:
    """Mark for review in a section, module or diagnostic, while it is live
    and after it is finished (a flag set later reads 'flagged later')."""
    learner = writer_of(x_learner)
    row = _own(sid, learner)
    if row["kind"] not in TEST_KINDS:
        raise HTTPException(409, "a practice set or challenge is flagged through /api/flags")
    return set_flag(learner, row, body.question_id, body.on)


@router.post("/api/flags")
def flag_other(body: HubFlag, x_learner: str | None = Header(default=None)) -> dict:
    """Mark for review in a practice set or the challenge (a challenge flag
    stays hidden until that question is answered), and Review's Unmark /
    undo by {session, question_id} or {session, template, seed}."""
    learner = writer_of(x_learner)
    row = _own(body.session, learner)
    if body.question_id:
        return set_flag(learner, row, body.question_id, body.on)
    if body.template is None or body.seed is None:
        bad("question_id", "send question_id, or template and seed")
    if body.on:
        q = next((x for x in progress._paper(row) if x.get("key") == body.template and x.get("seed") == body.seed), None)
        if q is None:
            raise HTTPException(400, "that question is not on this paper")
        return set_flag(learner, row, q["id"], True)
    db.run("DELETE FROM flags WHERE learner=? AND session=? AND template=? AND seed=?",
           learner, body.session, body.template, body.seed)
    return {"flags": flags_of(learner, body.session)}


# ------------------------------------------------------------------ mistake actions (§3.9.5)

class TrapRef(BaseModel):
    id: int = Field(ge=1)


class AddRef(BaseModel):
    template: str = Field(pattern=TEMPLATE)
    seed: int = Field(ge=0)


def _trap(learner: str, tid: int):
    t = db.one("SELECT * FROM traps WHERE id=? AND learner=?", tid, learner)
    if not t:
        raise HTTPException(404, "no such mistake of yours")
    return t


def _brief(tid: int) -> dict:
    t = db.one("SELECT * FROM traps WHERE id=?", tid)
    return {"id": t["id"], "label": review.trap_label(t), "owed": t["owed"], "of": review.of(t),
            "closed": t["closed"], "closed_how": t["closed_how"], "relapses": t["relapses"],
            "status": review.status(t) if t["closed"] is None else t["closed_how"]}


@router.post("/api/mistakes/dismiss")
def dismiss(body: TrapRef, x_learner: str | None = Header(default=None)) -> dict:
    """Remove a mistake without fixing it. It stays in History and the log; a
    later miss reopens it as Open, never as a relapse."""
    learner = writer_of(x_learner)
    t = _trap(learner, body.id)
    if t["closed"] is not None:
        raise HTTPException(409, "that mistake is not open")
    stamp = now()
    with db.atomic():
        db.run("UPDATE traps SET closed=?, closed_how='dismissed', due=NULL WHERE id=?", stamp, t["id"])
        progress.log(learner, t["template"], t["norm"], "dismissed", stamp)
    return _brief(t["id"])


def _undismiss(learner: str, tid: int, event: str) -> dict:
    t = _trap(learner, tid)
    if t["closed_how"] != "dismissed":
        raise HTTPException(409, "that mistake was not dismissed")
    stamp = now()
    with db.atomic():
        if event == "restored":     # the undo: exactly as it was, owed and all
            db.run("UPDATE traps SET closed=NULL, closed_how=NULL WHERE id=?", t["id"])
            last = db.one("SELECT id FROM trap_log WHERE learner=? AND template=? AND norm=? AND event='dismissed'"
                          " ORDER BY id DESC LIMIT 1", learner, t["template"], t["norm"])
            progress.log(learner, t["template"], t["norm"], "restored", stamp, undoes=last["id"] if last else None)
        else:                       # Reopen on a dismissed row: open again, owing its full count
            db.run("UPDATE traps SET closed=NULL, closed_how=NULL, owed=?, last=? WHERE id=?",
                   review.of(t), stamp, t["id"])
            progress.log(learner, t["template"], t["norm"], "reopened", stamp)
    return _brief(t["id"])


@router.post("/api/mistakes/restore")
def restore(body: TrapRef, x_learner: str | None = Header(default=None)) -> dict:
    """Undo a dismiss. Relapses are unchanged."""
    return _undismiss(writer_of(x_learner), body.id, "restored")


@router.post("/api/mistakes/reopen")
def reopen(body: TrapRef, x_learner: str | None = Header(default=None)) -> dict:
    return _undismiss(writer_of(x_learner), body.id, "reopened")


@router.post("/api/mistakes/add")
def add_to_redo(body: AddRef, x_learner: str | None = Header(default=None)) -> dict:
    """Add to Redo (an answer that was right, but not for sure): an Unsure
    that one clean answer closes. The question must be one this learner may
    see revealed."""
    learner = writer_of(x_learner)
    topic = known(body.template)
    if deps.access(learner, body.template, body.seed) != "reveal":
        raise HTTPException(404, "no such question of yours")
    filed = progress.record_trap(learner, {"key": body.template, "seed": body.seed, "topic": topic},
                                 "", now(), unsure=True)
    return {"trap": {**_brief(filed["id"]), "event": filed["event"]}}
