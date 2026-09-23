"""The question of the day: the same for every student.

It is made from the date alone, so nobody has to set it and two students
anywhere get the identical question -- the one thing an infinite bank cannot
give by accident. The day's challenge is in challenge.py.
"""

from __future__ import annotations

import datetime as dt
import hashlib

from . import blueprint, practice
# moved to challenge.py; kept here so older imports still work
from .challenge import CHALLENGE_SIZE, LADDER, MIX, SPR_AT, board, challenge, handle  # noqa: F401


def today(tz: int = 0) -> str:
    """The student's own date. tz is JavaScript's getTimezoneOffset(), minutes
    behind UTC. Everyone on the same calendar day gets the same question, which
    is what "of the day" means to the person reading it."""
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date().isoformat()


def _hash(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest(), 16)


def question(day: str) -> dict:
    """The question of the day, as stored (key included). Multiple choice,
    because it is answered with one tap on the home page."""
    names = sorted(n for v in practice.catalogue()["by_topic"].values() for n in v)
    can = blueprint.abilities()
    pool = [n for n in names if any(f == "mcq" for _, f in can.get(n, ()))]
    h = _hash(f"qotd:{day}")
    for k in range(200):
        template = pool[(h + k * 7919) % len(pool)]
        seed = (h >> 20) % 100_000 + k
        try:
            item = practice.generate(template, seed)
        except Exception:
            continue
        if item.fmt != "mcq":
            continue
        q = practice.to_question(practice.Card.of(template, seed, item, practice.topic_of(template)), 1)
        q["id"] = "qotd"
        return q
    raise RuntimeError(f"no question of the day for {day}")
