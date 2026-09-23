"""What every router needs: who is asking, their timezone, the shared
validators, and part() for the modules that are not written yet."""

from __future__ import annotations

import datetime as dt
import importlib
import re

from fastapi import Header, HTTPException

from . import db

# The real test gives 35 minutes to 22 math questions, so about 95 seconds each.
# Deriving the duration from the form means changing the blueprint cannot leave
# a stale clock behind.
SECONDS_PER_QUESTION = 95

# A learner is the token in their browser, sent as X-Learner. It is minted on
# the client, so it is checked for shape and nothing else.
LEARNER_OK = re.compile(r"^[A-Za-z0-9:_\-]{4,120}$")
NAME_OK = re.compile(r"^[^\d<>@]{1,60}$")
TARGETS = range(200, 810, 10)
DATE_OK = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DAYS_OK = re.compile(r"^[01]{7}$")


def learner_of(x_learner: str | None) -> str:
    v = (x_learner or "").strip()
    if not LEARNER_OK.match(v):
        raise HTTPException(400, "send your learner token in the X-Learner header")
    return v


def tz_of(x_tz: int = Header(default=0, ge=-840, le=720)) -> int:
    """X-Tz, JavaScript's getTimezoneOffset(): minutes behind UTC."""
    return x_tz


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def session_or_404(sid: str):
    row = db.one("SELECT * FROM sessions WHERE id=?", sid)
    if row is None:
        raise HTTPException(404, "no such session")
    return row


def mine(row, learner: str):
    if row["learner"] and row["learner"] != learner:
        raise HTTPException(403, "that session belongs to someone else")
    return row


def part(module: str, name: str):
    """server.<module>.<name>, or None while that module does not exist yet.
    A module that exists and fails to import is a bug, and raises."""
    try:
        mod = importlib.import_module(f"{__package__}.{module}")
    except ModuleNotFoundError as e:
        if e.name != f"{__package__}.{module}":
            raise
        return None
    return getattr(mod, name, None)
