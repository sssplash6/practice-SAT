"""What every router needs: who is asking, their timezone, the shared
validators, and part() for the modules that are not written yet."""

from __future__ import annotations

import datetime as dt
import importlib
import json
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
    if db.one("SELECT 1 FROM retired WHERE code=?", v):
        raise HTTPException(401, {"retired": True, "into": None})
    return v


def _has_pair(value, template: str, seed: int) -> bool:
    if isinstance(value, dict):
        if value.get("key", value.get("template")) == template and value.get("seed") == seed:
            return True
        return any(_has_pair(x, template, seed) for x in value.values())
    if isinstance(value, list):
        return any(_has_pair(x, template, seed) for x in value)
    return False


def access(learner: str, template: str, seed: int) -> str | None:
    """May this exact item be revealed, kept for later, or neither?"""
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    challenge = db.one("SELECT questions FROM challenges WHERE day=?", today)
    if challenge and _has_pair(json.loads(challenge["questions"]), template, seed):
        return None
    for row in db.rows("SELECT * FROM sessions WHERE learner=? AND finished IS NULL"
                       " AND kind IN ('mock','module','diagnostic','custom','paper')", learner):
        if row["questions"]:
            if _has_pair(json.loads(row["questions"]), template, seed):
                return None
        else:
            from .api_tests import marked_questions, questions_of
            try:
                items = marked_questions(row) if row["kind"]=="mock" else questions_of(row)
                if _has_pair(items, template, seed):
                    return None
            except (KeyError,TypeError):
                continue
    if db.one("SELECT 1 FROM attempts WHERE learner=? AND template=? AND seed=?", learner,template,seed):
        return "reveal"
    if db.one("SELECT 1 FROM saved AS s JOIN sessions AS x ON x.id=s.session"
              " WHERE s.learner=? AND s.template=? AND s.seed=? AND x.finished IS NOT NULL"
              " AND x.kind IN ('mock','module','diagnostic')",learner,template,seed):
        return "reveal"
    if db.one("SELECT 1 FROM flags AS f JOIN sessions AS x ON x.id=f.session"
              " WHERE f.learner=? AND f.template=? AND f.seed=? AND x.finished IS NOT NULL"
              " AND x.kind IN ('mock','module','diagnostic')",learner,template,seed):
        return "reveal"
    if db.one("SELECT 1 FROM saved WHERE learner=? AND template=? AND seed=?", learner,template,seed):
        return "kept"
    if db.one("SELECT 1 FROM flags AS f JOIN sessions AS x ON x.id=f.session"
              " WHERE f.learner=? AND f.template=? AND f.seed=?"
              " AND (x.kind='drill' OR x.finished IS NOT NULL)",learner,template,seed):
        return "kept"
    return None


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
