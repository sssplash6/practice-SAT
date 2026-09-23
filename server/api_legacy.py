"""The mixed sticker sheet, POST /api/practice: frozen for archive/site-v1."""

from __future__ import annotations

import json
import logging
import secrets

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from . import db, practice
from .api_tests import payload
from .deps import now, session_or_404

log = logging.getLogger("satf")
router = APIRouter()

MAX_PRACTICE = 120          # the sticker sheet stops here too


class Practice(BaseModel):
    """The sticker sheet, as the mixed page keeps it: topic slug -> how many."""
    basket: dict[str, int]
    learner: str = Field(default="", max_length=120)


@router.post("/api/practice")
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
