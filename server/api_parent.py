"""Parents: a student invites a parent with a link, the parent follows that student's progress.

A parent is an ordinary learner (usually with an email account) linked to one or more students in `guardians`.
Students manage the links (/api/guardians); parents read a short summary per child (/api/parent/...).
Nothing here lets a parent change anything of the student's. Link ids are random and are never the learner id.
"""

from __future__ import annotations

import datetime as dt
import secrets

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from . import api_admin, db, deps
from .deps import learner_of

router = APIRouter()

INVITE_DAYS = 7
OPEN_INVITES = 5
MIN_ANSWERS = 5          # a skill needs this many answers before it counts as strong or weak


class Join(BaseModel):
    code: str = Field(min_length=6, max_length=64)


def _name(learner: str) -> str:
    r = db.one("SELECT name, handle FROM learners WHERE id=?", learner)
    return (r["name"] or r["handle"] or "") if r else ""


def _in(days: int) -> str:
    return (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=days)).isoformat(timespec="seconds")


# ---- the student's side

@router.post("/api/guardians/invite")
def invite(x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    db.ensure_learner(learner)
    now = deps.now()
    open_ = db.one("SELECT COUNT(*) n FROM guardian_invites WHERE student=? AND used IS NULL AND expires>?", learner, now)["n"]
    if open_ >= OPEN_INVITES:
        raise HTTPException(429, "too many open invites; cancel one first")
    code = secrets.token_urlsafe(9)
    db.run("INSERT INTO guardian_invites(code,student,created,expires) VALUES (?,?,?,?)", code, learner, now, _in(INVITE_DAYS))
    return {"code": code, "url": f"/parent/?invite={code}"}


@router.get("/api/guardians")
def guardians(x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    return {"parents": [{"id": r["id"], "name": _name(r["parent"]), "since": r["created"]} for r in db.rows(
                "SELECT id, parent, created FROM guardians WHERE student=? ORDER BY created", learner)],
            "invites": [{"code": r["code"], "url": f"/parent/?invite={r['code']}", "expires": r["expires"]} for r in db.rows(
                "SELECT code, expires FROM guardian_invites WHERE student=? AND used IS NULL AND expires>? ORDER BY created DESC",
                learner, deps.now())]}


@router.delete("/api/guardians/{link}")
def remove_parent(link: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    if not db.run("DELETE FROM guardians WHERE id=? AND student=?", link, learner).rowcount:
        raise HTTPException(404, "no such parent")
    return {"ok": True}


@router.delete("/api/guardians/invites/{code}")
def cancel_invite(code: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    if not db.run("DELETE FROM guardian_invites WHERE code=? AND student=? AND used IS NULL", code, learner).rowcount:
        raise HTTPException(404, "no such invite")
    return {"ok": True}


# ---- the parent's side

@router.post("/api/parent/join")
def join(body: Join, x_learner: str | None = Header(default=None)) -> dict:
    parent = deps.writer_of(x_learner)
    inv = db.one("SELECT student FROM guardian_invites WHERE code=? AND used IS NULL AND expires>?", body.code, deps.now())
    if inv is None:
        raise HTTPException(410, "this invite has expired or was already used")
    if inv["student"] == parent:
        raise HTTPException(409, "you cannot follow your own progress as a parent")
    db.ensure_learner(parent)
    with db.transaction():
        link = db.one("SELECT id FROM guardians WHERE parent=? AND student=?", parent, inv["student"])
        if link is None:
            link = {"id": secrets.token_urlsafe(9)}
            db.run("INSERT INTO guardians(id,parent,student,created) VALUES (?,?,?,?)", link["id"], parent, inv["student"], deps.now())
        db.run("UPDATE guardian_invites SET used=? WHERE code=?", deps.now(), body.code)
    return {"child": {"id": link["id"], "name": _name(inv["student"])}}


@router.get("/api/parent/children")
def children(x_learner: str | None = Header(default=None)) -> dict:
    parent = learner_of(x_learner)
    return {"name": _name(parent), "children": [{"id": r["id"], "name": _name(r["student"]), "since": r["created"]} for r in db.rows(
        "SELECT id, student, created FROM guardians WHERE parent=? ORDER BY created", parent)]}


def _link(link: str, parent: str):
    r = db.one("SELECT student FROM guardians WHERE id=? AND parent=?", link, parent)
    if r is None:
        raise HTTPException(404, "no such child")
    return r["student"]


@router.delete("/api/parent/children/{link}")
def unlink(link: str, x_learner: str | None = Header(default=None)) -> dict:
    parent = deps.writer_of(x_learner)
    _link(link, parent)
    db.run("DELETE FROM guardians WHERE id=? AND parent=?", link, parent)
    return {"ok": True}


@router.get("/api/parent/children/{link}")
def child(link: str, x_learner: str | None = Header(default=None)) -> dict:
    """The short version of the admin's student page: how much, how well, where it is going, what needs work."""
    student = _link(link, learner_of(x_learner))
    d = api_admin.detail(db.one("SELECT * FROM learners WHERE id=?", student))
    a, p, days = d["activity"], d["profile"], d["last30"]
    this, prev = days[-7:], days[-14:-7]
    tot = lambda xs, k: sum(x[k] for x in xs)
    skills = [s for s in d["skills"] if s["answers"] >= MIN_ANSWERS]
    by = sorted(skills, key=lambda s: s["accuracy"])
    tests = [{k: t[k] for k in ("finished", "kind", "number", "right", "asked", "low", "high")} for t in d["tests"]["sittings"][:5]]
    return {"name": p["name"] or "", "last": a["last"], "joined": p["joined"],
            "goal": {"target": p["target"], "exam_date": p["exam_date"], "has_plan": p["has_plan"]},
            "totals": {"answers": a["answers"], "accuracy": a["accuracy"], "minutes": a["minutes"], "active_days": a["active_days"],
                       "streak": a["streak"], "tests": len(d["tests"]["sittings"])},
            "week": {"answers": tot(this, "answers"), "right": tot(this, "right"), "active_days": sum(1 for x in this if x["answers"]),
                     "prev_answers": tot(prev, "answers")},
            "last14": [{"day": x["day"], "answers": x["answers"]} for x in days[-14:]],
            "focus": [{"name": s["name"], "accuracy": s["accuracy"]} for s in by[:3]],
            "strong": [{"name": s["name"], "accuracy": s["accuracy"]} for s in reversed(by[-3:]) if s["accuracy"] >= 0.7],
            "tests": tests, "open_mistakes": d["mistakes"]["open"]}
