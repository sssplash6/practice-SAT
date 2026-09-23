"""One registry of learner preferences and their validated defaults."""

from __future__ import annotations

import json
import re

from fastapi import HTTPException

from . import db

DEFAULTS = {
    "set_length": 10, "clock": "off", "clock_minutes": 16,
    "tiers": ["easy", "medium", "hard"], "adaptive": False,
    "levels": [1, 2, 3, 4, 5, 6, 7], "unmeasured": True,
    "formats": ["mcq", "spr"], "feedback": "instant", "repairs": "next",
    "rationale": "miss", "option_reasons": True, "first_tap": False,
    "order": "mixed", "mix": "even", "pool": "new", "keep_warm": True,
    "confirm_end": True, "keys": True, "show_timer": True,
    "show_stopwatch": True, "pace_alert": True, "calc_button": True,
    "calc_mode": "closed", "ref_button": True, "theme": "light",
    "text": "normal", "motion": "system", "week_start": "mon",
    "gloss": True, "study_time": None, "remind": 10,
    "test_timing": "official", "test_calculator": True, "test_pace": True,
    "test_confidence": False, "test_reveal_route": False,
    "test_fullscreen": True, "words_goal": 10,
    "words_from": ["sat"],  # Words ships with EBRW vocabulary only.
}

CHOICES = {
    "clock": ("off", "pace", "custom"),
    "feedback": ("instant", "retry", "end"),
    "repairs": ("next", "end", "off"),
    "rationale": ("miss", "always", "tap"),
    "order": ("mixed", "grouped", "ramp"), "mix": ("even", "blueprint"),
    "pool": ("new", "redo", "checks", "review", "untried", "seen", "saved", "marked"),
    "calc_mode": ("closed", "dock", "float"),
    "theme": ("light", "dark", "system"),
    "text": ("small", "normal", "large"), "motion": ("system", "reduce"),
    "week_start": ("mon", "sun"),
    "test_timing": ("official", "x1.5", "x2", "untimed"),
    "remind": (0, 10, 30), "words_goal": (0, 5, 10, 20),
}
SUBSETS = {
    "tiers": ("easy", "medium", "hard"),
    "levels": (1, 2, 3, 4, 5, 6, 7),
    "formats": ("mcq", "spr"),
    "words_from": ("sat", "transitions"),
}


def validate(changes: dict) -> dict:
    if not isinstance(changes, dict):
        raise HTTPException(422, "prefs must be an object")
    out = {}
    for key, value in changes.items():
        if key not in DEFAULTS:
            raise HTTPException(422, f"prefs.{key} is unknown")
        valid = False
        if key in CHOICES:
            valid = type(value) is type(CHOICES[key][0]) and value in CHOICES[key]
        elif key in SUBSETS:
            valid = isinstance(value, list) and bool(value) and len(value) == len(set(map(str, value))) and all(type(v) is type(SUBSETS[key][0]) and v in SUBSETS[key] for v in value)
            if valid:
                value = [v for v in SUBSETS[key] if v in value]
        elif key == "set_length":
            valid = type(value) is int and 0 <= value <= 120
        elif key == "clock_minutes":
            valid = type(value) is int and 1 <= value <= 180
        elif key == "study_time":
            valid = value is None or (isinstance(value, str) and re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value) is not None)
        else:
            valid = type(value) is bool
        if not valid:
            raise HTTPException(422, f"prefs.{key} has an invalid value")
        out[key] = value
    return out


def get(learner: str) -> dict:
    row = db.one("SELECT prefs FROM learners WHERE id=?", learner)
    stored = json.loads(row["prefs"] or "{}") if row else {}
    return {**DEFAULTS, **{k: v for k, v in stored.items() if k in DEFAULTS}}


def put(learner: str, changes: dict) -> dict:
    changes = validate(changes)
    db.ensure_learner(learner)
    merged = {**get(learner), **changes}
    sparse = {k: v for k, v in merged.items() if v != DEFAULTS[k]}
    db.run("UPDATE learners SET prefs=? WHERE id=?", json.dumps(sparse), learner)
    return merged
