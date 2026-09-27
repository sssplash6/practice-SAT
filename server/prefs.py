"""One registry of learner preferences (R11, §2.7 and every upgrade file's
§2.7 row): each key's values, default, label, group and synonyms.

Stored in `learners.prefs` as JSON. A key is stored when it differs from its
default, or when the student set it and a mode or stage would otherwise set it
(U15); `{key: null}` deletes it ("Back to stage"). Reading resolves each key:
yours, else the stage's bundle (when `stage_auto` and an exam date), else the
chosen mode's bundle, else the default. `GET /api/prefs` serves the registry.
Builder keys live per subject under `practice` (practice.md §2.7).
"""

from __future__ import annotations

import datetime as dt
import json
import re

from fastapi import HTTPException

from . import db

BOOL = "bool"
TIME = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _key(key, label, group, default, values=None, *, kind=None, lo=None, hi=None,
          helper="", synonyms=(), nullable=False, extra=None):
    return {"key": key, "label": label, "group": group, "default": default, "values": values,
            "kind": kind or ("choice" if values is not None else BOOL), "lo": lo, "hi": hi,
            "helper": helper, "synonyms": list(synonyms), "nullable": nullable, "extra": extra}


def _v(*pairs):
    return [{"v": v, "label": label} for v, label in pairs]


REGISTRY = [
    # practice sets
    _key("set_length", "Questions per set", "practice", 10, kind="int", lo=0, hi=120,
         helper="0 means endless.", synonyms=("set", "length", "count", "questions")),
    _key("clock", "Clock", "practice", "off", _v(("off", "Off"), ("pace", "SAT pace"), ("custom", "Custom")),
         synonyms=("timer", "timed", "clock")),
    _key("clock_minutes", "Custom clock minutes", "practice", 16, kind="int", lo=1, hi=180),
    _key("tiers", "Difficulty", "practice", ["easy", "medium", "hard"],
         _v(("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")), kind="subset", synonyms=("hard", "easy")),
    _key("adaptive", "Adaptive difficulty", "practice", False, synonyms=("adaptive",)),
    _key("levels", "Levels", "practice", [1, 2, 3, 4, 5, 6, 7], _v(*[(n, f"L{n}") for n in range(1, 8)]), kind="subset"),
    _key("unmeasured", "Include rough levels", "practice", True),
    _key("formats", "Formats", "practice", ["mcq", "spr"], _v(("mcq", "Multiple choice"), ("spr", "Grid-in")),
         kind="subset", synonyms=("grid", "grid-in", "multiple choice")),
    _key("feedback", "Feedback", "practice", "instant",
         _v(("instant", "After each question"), ("retry", "Retry first"), ("end", "At the end"))),
    _key("repairs", "Repair questions", "practice", "next",
         _v(("next", "Right after a miss"), ("later", "Later in the set"), ("end", "At the end"), ("off", "Off"))),
    _key("rationale", "Explanations", "practice", "miss",
         _v(("miss", "When I miss"), ("always", "Always"), ("tap", "On tap")), synonyms=("explanations",)),
    _key("open_explanations", "Always open explanations", "practice", False),
    _key("option_reasons", "Show why each option is wrong", "practice", True),
    _key("first_tap", "Answer on first tap", "practice", False),
    _key("order", "Order", "practice", "mixed", _v(("mixed", "Mixed"), ("grouped", "Grouped"), ("ramp", "Easy to hard"))),
    _key("mix", "Mix", "practice", "even", _v(("even", "Even"), ("blueprint", "Like the test"))),
    _key("pool", "Questions from", "practice", "new",
         _v(("new", "New"), ("redo", "My mistakes"), ("checks", "Check-ins"), ("review", "Review"),
            ("untried", "Untried"), ("seen", "Seen before"), ("saved", "Saved"), ("marked", "Marked"))),
    _key("keep_warm", "Keep strong skills warm", "practice", True,
         helper="The coach revisits a strong skill after 10 days."),
    _key("confidence", "Confidence on Check", "practice", "ask", _v(("ask", "Sure · Unsure · Guess"), ("off", "Off")),
         synonyms=("sure", "unsure", "confidence")),
    _key("type_rules", "Your rule on every question of its type", "practice", True),
    _key("second_look", "Second look before the key", "practice", True),
    _key("mode", "Mode", "practice", "learn",
         _v(("learn", "Learn"), ("build", "Build"), ("test", "Test-like"), ("custom", "Custom")),
         synonyms=("mode", "test mode")),
    _key("stage_auto", "Follow my exam date", "practice", True),
    _key("practice", "Builder settings per subject", "practice", None, kind="practice"),
    # the session
    _key("confirm_end", "Confirm before ending a set", "session", True),
    _key("keys", "Keyboard shortcuts", "session", True, synonyms=("keys", "shortcuts")),
    _key("show_timer", "Show the timer", "session", True, synonyms=("timer",)),
    _key("hide_timer", "Hide the timer", "session", False),
    _key("show_stopwatch", "Show the stopwatch", "session", True, synonyms=("stopwatch",)),
    _key("pace_alert", "Pace alert", "session", True),
    _key("calc_button", "Calculator button", "session", True, synonyms=("calculator", "desmos")),
    _key("calc_mode", "Calculator", "session", "closed", _v(("closed", "Closed"), ("dock", "Docked"), ("float", "Floating"))),
    _key("ref_button", "Reference sheet button", "session", True, synonyms=("reference", "formulas")),
    # look
    _key("theme", "Theme", "look", "light", _v(("light", "Light"), ("dark", "Dark"), ("system", "System")),
         synonyms=("dark", "light", "theme")),
    _key("text", "Question text size", "look", "normal", _v(("small", "Small"), ("normal", "Normal"), ("large", "Large")),
         synonyms=("font size", "text size")),
    _key("motion", "Motion", "look", "system", _v(("system", "System"), ("reduce", "Reduce"))),
    _key("week_start", "Week starts on", "look", "mon", _v(("mon", "Monday"), ("sun", "Sunday")), synonyms=("week",)),
    # words
    _key("gloss", "Underline library words in Words texts", "words", True),
    _key("words_goal", "Words a day", "words", 10, kind="words_goal", lo=0, hi=40,
         helper="0 keeps Words out of the plan; Auto works it out from your exam date."),
    _key("words_from", "Words from", "words", ["sat", "transitions"],
         _v(("sat", "SAT words"), ("transitions", "Transitions")), kind="subset"),
    _key("words_autonext", "Move on by itself", "words", False),
    _key("words_commit", "Commit before choosing", "words", "auto", _v(("auto", "Auto"), ("on", "On"), ("off", "Off"))),
    _key("words_method", "Method trainer", "words", "auto", _v(("auto", "Auto"), ("on", "On"), ("off", "Off"))),
    _key("words_relation", "Relationship first", "words", "auto", _v(("auto", "Auto"), ("on", "On"), ("off", "Off"))),
    _key("words_spread", "Finish the core list by", "words", None, kind="date", nullable=True),
    # reminders and dates
    _key("study_time", "Study time", "reminders", None, kind="time", nullable=True, synonyms=("reminder",)),
    _key("remind", "Remind me before", "reminders", 10, _v((0, "Off"), (10, "10 minutes"), (30, "30 minutes"))),
    _key("quiet", "Quiet hours", "reminders", {"from": "21:30", "to": "07:00"}, kind="quiet", nullable=True),
    _key("registered", "I've registered for", "reminders", None, kind="date", nullable=True,
         synonyms=("registered", "registration")),
    # tests
    _key("test_timing", "Test timing", "tests", "official",
         _v(("official", "Official"), ("x1.5", "Time and a half"), ("x2", "Double time"), ("untimed", "Untimed"),
            ("x0.85", "Tight (Training)")), synonyms=("accommodations", "extended time")),
    _key("test_calculator", "Calculator in tests", "tests", True),
    _key("test_pace", "Pace guide (Training)", "tests", True),
    _key("test_confidence", "Confidence chips in tests", "tests", False),
    _key("test_reveal_route", "Show my module 2 route", "tests", False),
    _key("test_fullscreen", "Fullscreen tests", "tests", True),
    _key("test_conditions", "Test conditions", "tests", "test_day", _v(("test_day", "Test-day"), ("training", "Training"))),
    _key("test_nudges", "Coaching nudges (Training)", "tests", True),
    _key("test_cover", "Cover the choices (Training)", "tests", False),
    _key("test_predict", "Predict my misses between modules", "tests", True),
    _key("test_type_notes", "My type notes in tests (Training)", "tests", True),
    # review
    _key("review_minutes", "Review time box", "review", 10,
         _v((5, "5 min"), (10, "10 min"), (15, "15 min"), (20, "20 min"), (30, "30 min"), (45, "45 min"),
            (60, "60 min"), (0, "All"))),
    _key("snooze", "Not today", "review", {}, kind="snooze"),
    _key("saved_spaced", "Bring saved questions back spaced", "review", True),
    # compete
    _key("race_rail", "Race rail", "compete", True),
    _key("contest_timing", "Contest timing", "compete", "follow",
         _v(("follow", "Follow my test timing"), ("official", "Official"), ("x1.5", "Time and a half"), ("x2", "Double time"))),
    _key("contest_timing_seen", "Contest timing explained", "compete", False),
    # plan
    _key("plan_auto_focus", "Let the plan move my focus", "plan", True),
    _key("plan_auto_drift", "Let the plan follow my scores", "plan", False),
]
KEYS = {k["key"]: k for k in REGISTRY}
DEFAULTS = {k["key"]: k["default"] for k in REGISTRY if k["key"] != "practice"}

# practice.md §2.7: the builder keys, per subject under prefs.practice[subject]
PRACTICE = {
    "zone": ("stretch", ("off", "warm", "stretch", "challenge")),
    "review_mix": (20, ("off", 2, 20)),
    "review_from": ("picked", ("picked", "all")),
    "final_round": (True, None), "hints": (True, None), "worked_first": (True, None),
    "two_passes": (True, None),
    "cover": ("off", ("off", "hard", "all")),
    "words_mix": ("off", ("off", 2, "all")),
    "presets": ([], "presets"),
}
SUBJECTS = ("math", "rw")
PRACTICE_DEFAULTS = {k: v[0] for k, v in PRACTICE.items()}

# U15 and practice.md: what each mode sets. Flat keys, plus practice.math keys.
BUNDLES = {
    "learn": {"clock": "off", "feedback": "instant", "repairs": "next", "rationale": "miss", "adaptive": True,
              "practice": {"zone": "stretch", "final_round": True}},
    "build": {"clock": "pace", "feedback": "instant", "repairs": "later", "rationale": "miss", "adaptive": True,
              "practice": {"zone": "stretch", "final_round": True}},
    "test": {"clock": "pace", "feedback": "end", "repairs": "end", "rationale": "tap", "adaptive": False,
             "tiers": ["easy", "medium", "hard"], "confidence": "ask",
             "practice": {"zone": "off", "hints": False, "two_passes": True}},
}
BUNDLE_KEYS = {k for b in BUNDLES.values() for k in b if k != "practice"}
BUNDLE_PRACTICE = {k for b in BUNDLES.values() for k in b.get("practice", {})}

# U15: the drill sources the resolved mode or stage governs (F5's resolver).
# Everything else -- redo, checks, habit, gauntlet, quick, inline sources,
# pace and speed drills, week goals -- keeps instant feedback and next repairs.
MODE_SOURCES = frozenset({"builder", "map", "coach", "palette", "gain", "probe", "next", "skill", "plan"})
ALWAYS_INSTANT = {"feedback": "instant", "repairs": "next", "rationale": "miss"}


def _bad(key: str) -> HTTPException:
    return HTTPException(422, f"prefs.{key} has an invalid value")


def _same_type(value, allowed) -> bool:
    return type(value) is type(allowed) or (isinstance(value, int) and isinstance(allowed, int)
                                             and not isinstance(value, bool) and not isinstance(allowed, bool))


def _check(spec: dict, value):
    """The value, normalised, or raise 422 naming the key."""
    key, kind = spec["key"], spec["kind"]
    if value is None and spec["nullable"]:
        return None
    if kind == BOOL:
        if type(value) is not bool:
            raise _bad(key)
        return value
    if kind == "choice":
        allowed = [v["v"] for v in spec["values"]]
        if not any(_same_type(value, a) and value == a for a in allowed):
            raise _bad(key)
        return value
    if kind == "subset":
        allowed = [v["v"] for v in spec["values"]]
        if not (isinstance(value, list) and value and len(value) == len({json.dumps(v) for v in value})
                and all(any(_same_type(v, a) and v == a for a in allowed) for v in value)):
            raise _bad(key)
        return [a for a in allowed if a in value]
    if kind == "int":
        if type(value) is not int or not spec["lo"] <= value <= spec["hi"]:
            raise _bad(key)
        return value
    if kind == "words_goal":
        if value == "auto" or (type(value) is int and 0 <= value <= 40):
            return value
        raise _bad(key)
    if kind == "time":
        if isinstance(value, str) and TIME.match(value):
            return value
        raise _bad(key)
    if kind == "date":
        try:
            if isinstance(value, str) and DATE.match(value):
                dt.date.fromisoformat(value)
                return value
        except ValueError:
            pass
        raise _bad(key)
    if kind == "quiet":
        if isinstance(value, dict) and set(value) == {"from", "to"} and all(
                isinstance(value[k], str) and TIME.match(value[k]) for k in ("from", "to")):
            return {"from": value["from"], "to": value["to"]}
        raise _bad(key)
    if kind == "snooze":
        if not isinstance(value, dict) or len(value) > 200:
            raise _bad(key)
        today = dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=1)   # every zone's today survives
        out = {}
        for k, day in value.items():
            if not isinstance(k, str) or len(k) > 160 or not isinstance(day, str) or not DATE.match(day):
                raise _bad(key)
            if day >= today.isoformat():
                out[k] = day
        return out
    if kind == "practice":
        return _check_practice(value)
    raise _bad(key)


def _check_practice(value) -> dict:
    if not isinstance(value, dict) or any(s not in SUBJECTS for s in value):
        raise HTTPException(422, "prefs.practice maps a subject (math, rw) to builder settings")
    out = {}
    for subject, keys in value.items():
        if not isinstance(keys, dict):
            raise HTTPException(422, f"prefs.practice.{subject} must be an object")
        clean = {}
        for k, v in keys.items():
            if k not in PRACTICE:
                raise HTTPException(422, f"prefs.practice.{subject}.{k} is unknown")
            if v is None:
                clean[k] = None
                continue
            default, allowed = PRACTICE[k]
            if allowed is None:
                ok = type(v) is bool
            elif allowed == "presets":
                ok = (isinstance(v, list) and len(v) <= 8 and all(
                    isinstance(p, dict) and isinstance(p.get("name"), str) and 0 < len(p["name"]) <= 24
                    and isinstance(p.get("body"), dict) and len(json.dumps(p["body"])) <= 4000 for p in v))
            else:
                ok = any(_same_type(v, a) and v == a for a in allowed)
            if not ok:
                raise HTTPException(422, f"prefs.practice.{subject}.{k} has an invalid value"
                                    + (" (at most 8 presets)" if k == "presets" else ""))
            clean[k] = v
        out[subject] = clean
    return out


def validate(changes: dict) -> dict:
    """Each key checked; None (delete) kept as None. 422 names the key."""
    if not isinstance(changes, dict):
        raise HTTPException(422, "prefs must be an object")
    out = {}
    for key, value in changes.items():
        spec = KEYS.get(key)
        if spec is None:
            raise HTTPException(422, f"prefs.{key} is unknown")
        out[key] = None if value is None and not spec["nullable"] else _check(spec, value)
    return out


def _stored(learner: str) -> dict:
    row = db.one("SELECT prefs FROM learners WHERE id=?", learner)
    raw = json.loads(row["prefs"] or "{}") if row and row["prefs"] else {}
    out = {}
    for key, value in raw.items():          # a value an older registry allowed is dropped, not served
        if key not in KEYS:
            continue
        try:
            out[key] = _check(KEYS[key], value)
        except HTTPException:
            continue
    return out


def stage(learner: str, tz: int = 0) -> dict | None:
    """U15: where the exam date puts the student. The active plan's phase for
    today wins when it names one; else by days to the exam: more than 42
    learn, 22-42 build, 8-21 test, 7 or fewer the final week (test rules)."""
    row = db.one("SELECT exam_date, plan FROM learners WHERE id=?", learner)
    if not row or not row["exam_date"]:
        return None
    today = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date()
    exam = dt.date.fromisoformat(row["exam_date"])
    left = (exam - today).days
    cuts = (("learn", None, 42), ("build", 42, 21), ("test", 21, 7), ("final", 7, -1))
    name = next(n for n, _hi, lo in cuts if left > lo) if left >= 0 else "after"
    if row["plan"]:
        p = db.one("SELECT phase FROM plan_days WHERE plan=? AND day=?", row["plan"], today.isoformat())
        if p and p["phase"] in ("learn", "build", "test", "final"):
            name = p["phase"]
    order = [c[0] for c in cuts]
    starts = {"learn": None, "build": exam - dt.timedelta(days=42), "test": exam - dt.timedelta(days=21),
              "final": exam - dt.timedelta(days=7)}
    nxt = order[order.index(name) + 1] if name in order[:-1] else None
    since = starts.get(name)
    return {"name": name, "rules": "test" if name in ("test", "final") else name,
            "since": since.isoformat() if since else None, "days_to_exam": left,
            "next": {"name": nxt, "on": starts[nxt].isoformat()} if nxt else None}


def resolve(learner: str, tz: int = 0) -> tuple[dict, dict, dict | None]:
    """(prefs, pref_source, stage): every key resolved, and where each came from."""
    mine = _stored(learner)
    st = stage(learner, tz)
    mode = mine.get("mode", DEFAULTS["mode"])
    stage_on = mine.get("stage_auto", DEFAULTS["stage_auto"])
    layers = []
    if st and stage_on and st["rules"] in BUNDLES:
        layers.append(("stage", BUNDLES[st["rules"]]))
    if mode in BUNDLES:
        layers.append(("mode", BUNDLES[mode]))
    out, source = {}, {}
    for key, default in DEFAULTS.items():
        if key in mine:
            out[key], source[key] = mine[key], "yours"
            continue
        for name, bundle in layers:
            if key in bundle:
                out[key], source[key] = bundle[key], name
                break
        else:
            out[key], source[key] = default, "default"
    stored_practice = mine.get("practice") or {}
    practice = {}
    for subject in SUBJECTS:
        yours = {k: v for k, v in (stored_practice.get(subject) or {}).items() if v is not None}
        resolved = {}
        for key, default in PRACTICE_DEFAULTS.items():
            if key in yours:
                resolved[key], source[f"practice.{subject}.{key}"] = yours[key], "yours"
                continue
            for name, bundle in layers if subject == "math" else ():
                if key in bundle.get("practice", {}):
                    resolved[key], source[f"practice.{subject}.{key}"] = bundle["practice"][key], name
                    break
            else:
                resolved[key], source[f"practice.{subject}.{key}"] = default, "default"
        practice[subject] = resolved
    out["practice"] = practice
    return out, source, st


def get(learner: str, tz: int = 0) -> dict:
    return resolve(learner, tz)[0]


def for_source(learner: str, source: str | None, tz: int = 0) -> dict:
    """The prefs a drill of this source runs with: fixing drills stay instant."""
    p = get(learner, tz)
    return p if source in MODE_SOURCES or source is None else {**p, **ALWAYS_INSTANT}


def put(learner: str, changes: dict) -> dict:
    changes = validate(changes)
    db.ensure_learner(learner)
    stored = _stored(learner)
    for key, value in changes.items():
        if key == "practice":
            merged = dict(stored.get("practice") or {})
            for subject, keys in value.items():
                sub = dict(merged.get(subject) or {})
                for k, v in keys.items():
                    if v is None or (v == PRACTICE_DEFAULTS[k] and k not in BUNDLE_PRACTICE):
                        sub.pop(k, None)
                    else:
                        sub[k] = v
                if sub:
                    merged[subject] = sub
                else:
                    merged.pop(subject, None)
            if merged:
                stored["practice"] = merged
            else:
                stored.pop("practice", None)
        elif value is None and not KEYS[key]["nullable"]:
            stored.pop(key, None)
        elif value == DEFAULTS[key] and key not in BUNDLE_KEYS:
            stored.pop(key, None)
        else:
            stored[key] = value
    db.run("UPDATE learners SET prefs=? WHERE id=?", json.dumps(stored), learner)
    return get(learner)


def listing() -> list[dict]:
    """GET /api/prefs: the registry, for Settings, Me and the palette."""
    out = []
    for k in REGISTRY:
        item = {"key": k["key"], "label": k["label"], "group": k["group"], "default": k["default"],
                "kind": k["kind"], "helper": k["helper"], "synonyms": k["synonyms"],
                "values": k["values"] if k["values"] is not None else
                ([{"v": True, "label": "On"}, {"v": False, "label": "Off"}] if k["kind"] == BOOL else None)}
        if k["kind"] in ("int", "words_goal"):
            item["range"] = [k["lo"], k["hi"]]
        if k["key"] == "practice":
            item["keys"] = {key: {"default": d, "values": None if a is None else a}
                            for key, (d, a) in PRACTICE.items()}
        out.append(item)
    return out


def _self_check() -> None:
    assert set(DEFAULTS) | {"practice"} == set(KEYS)
    for spec in REGISTRY:
        if spec["key"] != "practice":
            assert _check(spec, spec["default"]) == spec["default"] or spec["kind"] == "snooze", spec["key"]
    assert BUNDLE_KEYS <= set(DEFAULTS) and BUNDLE_PRACTICE <= set(PRACTICE)


_self_check()
