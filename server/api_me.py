"""The learner's profile, and carrying another code's progress into this one."""

from __future__ import annotations

import datetime as dt
import json

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from . import db, drill, progress
from .deps import (DATE_OK, DAYS_OK, LEARNER_OK, NAME_OK, SECONDS_PER_QUESTION, TARGETS,
                   learner_of, now, tz_of)

router = APIRouter()

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


@router.get("/api/me")
def get_me(x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
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


@router.put("/api/me")
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


@router.post("/api/me/carry")
def carry(body: Carry, x_learner: str | None = Header(default=None)) -> dict:
    """Bring another code's progress into this one, so switching a device to
    another device's code keeps what both have done."""
    to = learner_of(x_learner)
    frm = body.learner.strip()
    if not LEARNER_OK.match(frm):
        raise HTTPException(400, "that is not a learner code")
    return {"moved": 0 if frm == to else progress.carry(frm, to)}
