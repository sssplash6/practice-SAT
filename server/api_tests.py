"""Sittings: the diagnostic, sections, single modules, custom tests, twins,
papers and shared tests, and the paper helpers every other router reads a
sitting through (spec/rebuild-v2.md §3.4.5 with spec/v2-upgrades/tests.md).

A sitting is made in a lobby: questions are withheld and the clock doesn't run
until POST /begin. Every sitting endpoint is owner-only (SEC-03): a sitting
with a learner answers only to that X-Learner, and a diagnostic started with no
code gets a server-minted `anon:` one, returned as `learner` (SEC-07).
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import math
import random
import re
import secrets
import statistics
from collections import Counter, defaultdict
from typing import Literal

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from . import blueprint, db, deps, drill, papers, practice, progress, scoring
from .deps import SECONDS_PER_QUESTION, learner_of, now, session_or_404, writer_of

log = logging.getLogger("satf")
router = APIRouter()
router.include_router(papers.router)

# A mock is the real thing: 35 minutes a module, whatever is in it.
MOCK_MODULE_SECONDS = 35 * 60

# what a student is allowed to see about a question
PUBLIC_FIELDS = ("id", "domain", "topic_name", "difficulty", "type",
                 "stem", "choices", "latex", "figure", "table")

# filled by app.py's startup
FORMS: dict[int, list[dict]] = {}
MOCKS: dict[str, dict] = {}

FRESH = "new"               # questions built for the sitting and stored in it
DRILLS = ("drill", "challenge")     # answered one at a time through /api/drill, never as a paper
TESTS = ("mock", "module", "custom", "diagnostic")
FACTOR = {"official": 1.0, "x1.5": 1.5, "x2": 2.0, "x0.85": 0.85, "untimed": 1.0}
TIMING_WHY = {"x1.5": "time and a half", "x2": "double time", "untimed": "untimed", "x0.85": "tight clock"}
M1_FORM = {"standard": "module1", "upper": "module1_upper", "lower": "module1_lower"}
MODULE_FORM = {"m1": "module1", "m2u": "module2_upper", "m2l": "module2_lower"}
SUBJECT_LABEL = {"math": "Math", "rw": "Reading and Writing"}
LATE_GRACE = 15             # seconds past time-up an answer is still just on time
LATE_WINDOW = 15 * 60       # an answer made in time may arrive this late (the offline queue)
PREDICT_WINDOW = 15 * 60    # predictions after the final hand-in
QSTATE_MAX = 256 * 1024
SCRATCH_MAX = 20 * 1024
BREAK_MAX_MS = 75_000       # X11: Bluebook's 60 s step plus slack for a slow device
AWAY_MAX_MS = 120_000       # X1
PRESSURE_MAX = 15
PRESSURE_DAYS = 7
GRID_OK = re.compile(r"^[-\u2212]?[0-9./]{1,5}$")
QID_OK = re.compile(r"^[A-Za-z0-9_:-]{1,24}$")
PID_OK = r"^[A-Za-z0-9_-]{1,40}$"
MARK_STYLES = ("highlight", "strong", "underline", "dashed", "dotted", "box", "strike")


def public(q: dict) -> dict:
    return {k: q[k] for k in PUBLIC_FIELDS if k in q}


def _json(text, default=None):
    try:
        return json.loads(text) if text else default
    except (TypeError, ValueError):
        return default


def _cfg(row) -> dict:
    return _json(row["cfg"], {}) or {}


def _utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _at(text: str) -> dt.datetime:
    return dt.datetime.fromisoformat(text)


def mmss(ms: float) -> str:
    s = int(round(ms / 1000))
    return f"{s // 60}:{s % 60:02d}"


# ------------------------------------------------------------------ what a sitting holds

def _contest_kind(row) -> str | None:
    if not row["contest"]:
        return None
    c = db.one("SELECT kind FROM contests WHERE id=?", row["contest"])
    return c["kind"] if c else None


def two_modules(row) -> bool:
    """A section routes; so does the Season Final (kind module, a contest)."""
    return row["kind"] == "mock" or _contest_kind(row) == "final"


def mock_module(row, module: int | None = None, route: str | None = None) -> list[dict]:
    """One module of a sitting. A built sitting carries its own questions
    (module 1 made when it started, module 2 when module 1 routed, so only the
    route taken is ever built); the archive's shelf mocks are read by id."""
    module = module or row["module"] or 1
    built = _json(row["questions"])
    if isinstance(built, dict):
        return built["module1"] if module == 1 else built.get("module2", [])
    m = MOCKS[row["mock_id"]]
    if module == 1:
        return m["module1"]
    return m["module2_" + (route or row["route"] or "upper")]


def mock_all(row) -> list[dict]:
    """Both modules, for marking the section once it is over."""
    return mock_module(row, 1) + mock_module(row, 2)


def questions_of(row) -> list[dict]:
    """The live module: a diagnostic points at a form, a practice set carries
    its own list, and every other test serves the module the student is in."""
    if row["kind"] in ("practice", "drill", "challenge"):
        return _json(row["questions"], []) or []
    if row["kind"] in ("mock", "module", "custom"):
        return mock_module(row)
    return FORMS[row["form_id"]]


def marked_questions(row) -> list[dict]:
    """Everything a sitting asked, for marking and for review."""
    if row["kind"] not in ("mock", "module", "custom"):
        return questions_of(row)
    first = mock_module(row, 1)
    built = _json(row["questions"])
    if isinstance(built, dict):
        return first + (built.get("module2") or [])
    return first + (mock_module(row, 2) if row["route"] or (row["module"] or 1) == 2 else [])


def _modules(row) -> list[list[dict]]:
    """The sitting's modules as marked so far, in order."""
    if row["kind"] not in ("mock", "module", "custom"):
        return [questions_of(row)]
    out = [mock_module(row, 1)]
    if two_modules(row) and ((row["module"] or 1) == 2 or row["route"]):
        out.append(mock_module(row, 2))
    return out


def timing_of(row) -> str:
    cfg = _cfg(row)
    if cfg.get("timing") in FACTOR:
        return cfg["timing"]
    return "untimed" if cfg.get("timed") is False else "official"


def is_timed(row) -> bool:
    return row["kind"] != "practice" and timing_of(row) != "untimed"


def duration(row) -> int:
    """The live module's clock: 35 minutes a module, 95 s a question for a
    diagnostic or custom test (or its own minutes), times the timing factor."""
    cfg = _cfg(row)
    if row["kind"] in ("mock", "module"):
        base = MOCK_MODULE_SECONDS
    elif row["kind"] == "custom" and cfg.get("minutes"):
        base = cfg["minutes"] * 60
    else:
        base = len(questions_of(row)) * SECONDS_PER_QUESTION
    return int(round(base * FACTOR.get(timing_of(row), 1.0)))


def begun(row) -> bool:
    return not _cfg(row).get("lobby") or row["module_started"] is not None


def _left(row) -> float:
    """Seconds left on the live module, unclamped: from when it began, less
    pauses -- not from when the page loaded, or a reload is free time."""
    dur = duration(row)
    if not begun(row):
        return float(dur)
    t = _utc()
    elapsed = (t - _at(row["module_started"] or row["started"])).total_seconds()
    elapsed -= (row["paused_ms"] or 0) / 1000
    if row["paused_at"]:
        elapsed -= (t - _at(row["paused_at"])).total_seconds()
    return dur - elapsed


def remaining(row) -> int:
    return max(0, int(_left(row)))


def elapsed_ms(row) -> int:
    """The live module clock's elapsed time, pauses left out."""
    return max(0, int((duration(row) - _left(row)) * 1000))


def kind_of(row) -> str:
    """The sitting's kind as the start sheet names it."""
    cfg = _cfg(row)
    if row["kind"] == "mock":
        return cfg.get("kind") or ("paper" if (row["mock_id"] or "").startswith("P") else "section")
    return cfg.get("kind") or row["kind"]


def kind_label(row) -> str:
    cfg = _cfg(row)
    k = kind_of(row)
    if row["contest"]:
        return {"final": "Season Final", "weekly": "Weekly Module"}.get(_contest_kind(row) or "", "Contest")
    if k == "paper":
        return f"Paper #{cfg.get('paper') or (row['mock_id'] or 'P')[1:]}"
    if k == "twin":
        return "Twin"
    if k == "shared":
        return "Shared test"
    if row["kind"] == "mock":
        return "Full section"
    if row["kind"] == "module":
        if cfg.get("trainer") == "route":
            return "Route-up trainer"
        if cfg.get("trainer") == "gauntlet":
            return "Gauntlet"
        return {"m2u": "Module 2 · harder", "m2l": "Module 2 · easier"}.get(
            cfg.get("module"), {"upper": "Module 1 · harder", "lower": "Module 1 · easier"}.get(cfg.get("m1"), "Module 1"))
    if row["kind"] == "custom":
        return "Trap test" if (cfg.get("custom") or {}).get("source") == "traps" else "Custom test"
    if row["kind"] == "practice":
        return "Mixed practice"
    return "Diagnostic"


def modules_list(row) -> list[dict]:
    """Decision 3: [{subject, n, questions}], one per module of the sitting."""
    subject = row["subject"] if "subject" in row.keys() and row["subject"] else "math"
    if row["kind"] in ("mock", "module", "custom") and two_modules(row):
        n1 = len(mock_module(row, 1))
        return [{"subject": subject, "n": 1, "questions": n1}, {"subject": subject, "n": 2, "questions": 22}]
    return [{"subject": subject, "n": 1, "questions": len(questions_of(row))}]


def section_label(row) -> str:
    """Derived from the modules list, subject first; nothing hard-codes 'of 2'."""
    cfg = _cfg(row)
    mods = modules_list(row)
    subject = SUBJECT_LABEL.get(mods[0]["subject"], "Math")
    m = row["module"] or 1
    if row["kind"] == "practice":
        return "Mixed practice"
    if row["kind"] == "diagnostic":
        return f"{subject} · Diagnostic"
    if row["kind"] == "custom":
        return f"{subject} · {kind_label(row)}"
    of = sum(x["subject"] == mods[0]["subject"] for x in mods)
    if row["kind"] == "mock" and kind_of(row) == "paper":
        return f"{kind_label(row)} · {subject} · Module {m} of {of}"
    if len(mods) > 1:
        return f"{subject} · Module {m} of {of}"
    return {"m2u": f"{subject} · Module 2 (harder)", "m2l": f"{subject} · Module 2 (easier)"}.get(
        cfg.get("module"), {"upper": f"{subject} · Module 1 (harder)", "lower": f"{subject} · Module 1 (easier)"}.get(
            cfg.get("m1"), f"{subject} · Module 1"))


# ------------------------------------------------------------------ ownership (SEC-03)

def own(row, x_learner: str | None, write: bool = False):
    """A sitting with a learner answers only to that learner's X-Learner; a
    missing header is 403 too. Old diagnostics made with no learner stay
    reachable by their 128-bit id."""
    if row["learner"]:
        if not x_learner or not x_learner.strip():
            raise HTTPException(403, "that test belongs to another code")
        who = writer_of(x_learner) if write else learner_of(x_learner)
        if who != row["learner"]:
            raise HTTPException(403, "that test belongs to another code")
    return row


def _guard(row, what: str = "answer") -> None:
    if row["kind"] in DRILLS:
        raise HTTPException(409, f"a practice set is {what}ed through /api/drill" if what != "finish"
                            else "a practice set is finished through /api/drill")
    if row["abandoned"]:
        raise HTTPException(409, "discarded")
    if row["finished"]:
        raise HTTPException(409, "this test is already finished")
    if not begun(row):
        raise HTTPException(409, "press Begin first")
    if row["paused_at"]:
        raise HTTPException(409, "paused")


# ------------------------------------------------------------------ qstate writes

def _path(qid: str, *keys: str) -> str:
    return "$." + ".".join(f'"{k}"' for k in (qid, *keys))


class Stamps(BaseModel):
    """X1's client stamps: page load, the module clock's elapsed ms when it
    happened, hidden and offline totals for this page load."""
    pid: str | None = Field(default=None, pattern=PID_OK)
    el: int | None = Field(default=None, ge=0, le=36_000_000)
    hid: int | None = Field(default=None, ge=0, le=36_000_000)
    off: int | None = Field(default=None, ge=0, le=36_000_000)


def _stamp_sets(row, s: Stamps | None) -> list[tuple[str, str, list]]:
    """json_set parts for this page load's stamps. el is capped at the
    server's clock, so stamps can't buy time."""
    if s is None or not s.pid:
        return []
    base = f'$."_session"."pids"."m{row["module"] or 1}:{s.pid}"'
    cap = elapsed_ms(row) + 2000
    el = min(s.el if s.el is not None else elapsed_ms(row), cap)
    out = [(base + '."first_el"', f"COALESCE(json_extract(qstate, ?), ?)", [base + '."first_el"', el]),
           (base + '."last_el"', "max(COALESCE(json_extract(qstate, ?), 0), ?)", [base + '."last_el"', el])]
    for k in ("hid", "off"):
        v = getattr(s, k)
        if v is not None:
            out.append((f'{base}."{k}"', "max(COALESCE(json_extract(qstate, ?), 0), ?)", [f'{base}."{k}"', v]))
    return out


def _qstate_sql(parts: list[tuple[str, str, list]]) -> tuple[str, list]:
    """One json_set over qstate, so two calls at once can't clobber each other."""
    if not parts:
        return "COALESCE(qstate,'{}')", []
    sql, args = "json_set(COALESCE(qstate,'{}')", []
    for path, expr, a in parts:
        sql += f", ?, {expr}"
        args += [path, *a]
    return sql + ")", args


def _set(path: str, value) -> tuple[str, str, list]:
    return (path, "json(?)", [json.dumps(value)])


def _add(path: str, delta: int) -> tuple[str, str, list]:
    return (path, "COALESCE(json_extract(qstate, ?), 0) + ?", [path, delta])


def _write_qstate(sid: str, parts: list, where: str = "") -> int:
    if not parts:
        return 1
    sql, args = _qstate_sql(parts)
    return db.run(f"UPDATE sessions SET qstate={sql} WHERE id=?{where}", *args, sid).rowcount


# ------------------------------------------------------------------ the payload

def _live_ids(row) -> list[str]:
    return [q["id"] for q in questions_of(row)]


def _met_templates(learner: str | None, before: str | None = None, exclude: str | None = None) -> set[str]:
    """Templates this learner has answered under the clock (in a test sitting)."""
    if not learner:
        return set()
    sql = ("SELECT DISTINCT a.template FROM attempts AS a JOIN sessions AS s ON s.id=a.session"
           " WHERE a.learner=? AND s.kind IN ('mock','module','custom','diagnostic')")
    args: list = [learner]
    if before:
        sql += " AND a.at<?"
        args.append(before)
    if exclude:
        sql += " AND a.session!=?"
        args.append(exclude)
    return {r["template"] for r in db.rows(sql, *args)}


def holds(row, qs: list[dict]) -> dict:
    """X2: what the live module holds, public counts only."""
    subject = row["subject"] if "subject" in row.keys() and row["subject"] else "math"
    out = blueprint.holds(qs, subject)
    templates = {q["key"] for q in qs if "key" in q}
    met = _met_templates(row["learner"])
    ever = {r["template"] for r in db.rows("SELECT DISTINCT template FROM attempts WHERE learner=?",
                                           row["learner"])} if row["learner"] else set()
    out["new_types"] = len(templates - met)
    out["never"] = len(templates - ever)
    return out


def _training(cfg: dict) -> bool:
    return cfg.get("conditions") == "training"


def live_rank(row) -> dict:
    """The runner chip: whether the sitting still ranks, and why not."""
    ranked, why = rank_of(row, _cfg(row), partial=True)
    return {"ranked": bool(ranked), "why": why}


def payload(row) -> dict:
    cfg = _cfg(row)
    qs = questions_of(row)
    ids = {q["id"] for q in qs}
    practice_mode = row["kind"] == "practice"
    started, paused = begun(row), bool(row["paused_at"])
    show = started and not paused
    training = _training(cfg)
    subject = row["subject"] if "subject" in row.keys() and row["subject"] else "math"
    answers = db.load_answers(row)
    qstate = _json(row["qstate"], {}) or {}
    out = {
        "id": row["id"], "mode": row["kind"], "kind": kind_of(row), "kind_label": kind_label(row),
        "section": section_label(row), "subject": subject,
        # practice is not an exam, so it is not on a clock
        "seconds": None if practice_mode or not is_timed(row) else remaining(row),
        "duration": None if practice_mode or not is_timed(row) else duration(row),
        "form": row["form_id"],
        "questions": [public(q) for q in qs] if show else [],
        "question_count": len(qs),
        "answers": {k: v for k, v in answers.items() if k in ids},
        "finished": row["finished"], "begun": started, "paused": paused,
        "pauses": row["pauses"] or 0, "number": row["number"],
        "modules": modules_list(row), "module": row["module"] or 1,
        "conditions": cfg.get("conditions", "test_day"), "timing": timing_of(row),
        "factor": FACTOR.get(timing_of(row), 1.0),
        "calculator": cfg.get("calculator", True), "fullscreen": cfg.get("fullscreen", True),
        "predict": cfg.get("predict", True),
        "confidence": training and bool(cfg.get("confidence")),
        "reveal_route": training and bool(cfg.get("reveal_route")),
        "nudges": training and bool(cfg.get("nudges")),
        "cover": training and bool(cfg.get("cover")),
        "abandoned": row["abandoned"], "note": row["note"],
        "qstate": {**{k: v for k, v in qstate.items() if k in ids},
                   "_session": {k: v for k, v in (qstate.get("_session") or {}).items() if k != "pids"}},
        "holds": holds(row, qs) if row["kind"] != "practice" else None,
    }
    if row["kind"] in TESTS:
        out.update(live_rank(row))
    if row["learner"]:
        name = db.one("SELECT name FROM learners WHERE id=?", row["learner"])
        out["name"] = name["name"] if name else None
    if cfg.get("paper"):
        out["paper"] = cfg["paper"]
    if cfg.get("share"):
        owner = db.one("SELECT l.name FROM sets AS s LEFT JOIN learners AS l ON l.id=s.owner WHERE s.code=?",
                       cfg["share"])
        out["shared_by"] = owner["name"] if owner else None
    if cfg.get("paper") or cfg.get("share"):
        seen = {(r["template"], r["seed"]) for r in db.rows(
            "SELECT template, seed FROM practice_seen WHERE learner=? AND at<?", row["learner"],
            row["module_started"] or now())} if row["learner"] else set()
        out["new_to_you"] = sum((q.get("key"), q.get("seed")) not in seen for q in qs)
    if row["kind"] == "mock" and not cfg.get("kind"):
        out["mock"] = row["mock_id"]
    if training and cfg.get("reveal_route") and (row["module"] or 1) == 2:
        out["route"] = row["route"]
    if training and cfg.get("pace") and is_timed(row) and row["kind"] in TESTS:
        # numbers from the public ladder only, so the lobby can say whose pace it is
        out["pace"] = pace_plan(row["learner"], _form_of(row), FACTOR.get(timing_of(row), 1.0),
                                reveal_route=bool(cfg.get("reveal_route")), route=row["route"],
                                seconds=duration(row))
    if training and show:
        from . import ratings
        out["odds"] = {q["id"]: round(ratings.odds(row["learner"], q["key"], q["difficulty"], q.get("topic")), 2)
                       for q in qs if "key" in q} if row["learner"] and not db.is_sample(row["learner"]) else {}
        if cfg.get("type_notes", True) and row["learner"]:
            notes = {r["template"]: r["note"] for r in db.rows(
                "SELECT template, note FROM notes WHERE learner=? AND seed=-1 AND note IS NOT NULL AND note!=''",
                row["learner"])}
            # the note's text on its question only, never the template name (X9)
            for pq, q in zip(out["questions"], qs):
                if q.get("key") in notes:
                    pq["type_note"] = notes[q["key"]]
    if row["contest"]:
        extra = deps.part("compete", "state_extra")
        if extra:
            e = extra(row)
            out["contest"] = {**(e.get("contest") or {}), "ranked": e.get("ranked"), "why": e.get("why"),
                              "clock": e.get("clock"), "pacer": e.get("pacer")}
    return out


def _form_of(row):
    """The blueprint form of the live module, for its public tier ladder; a
    custom test or diagnostic uses its own questions' tiers."""
    cfg = _cfg(row)
    if row["kind"] == "mock" or (row["kind"] == "module" and two_modules(row)):
        if (row["module"] or 1) == 2:
            return "module2"
        return M1_FORM.get(cfg.get("m1", "standard"), "module1")
    if row["kind"] == "module":
        if cfg.get("module") in ("m2u", "m2l"):
            return MODULE_FORM[cfg["module"]]
        return M1_FORM.get(cfg.get("m1", "standard"), "module1")
    return [q["difficulty"] for q in questions_of(row)]


# ------------------------------------------------------------------ X3: the pace plan

TIER_DEFAULT_S = {"easy": 65, "medium": 95, "hard": 126}     # P16


def _tier_bases(learner: str | None) -> tuple[dict[str, float], str, int]:
    """Median seconds on first-try right answers per tier over 60 days in
    timed contexts, when every tier has 15; else P16's defaults."""
    if not learner:
        return dict(TIER_DEFAULT_S), "default", 0
    since = (_utc() - dt.timedelta(days=60)).isoformat()
    per: dict[str, list[float]] = defaultdict(list)
    n = 0
    for r in db.rows("SELECT a.difficulty, COALESCE(a.ms, a.sms) AS ms, s.kind, s.cfg FROM attempts AS a"
                     " JOIN sessions AS s ON s.id=a.session WHERE a.learner=? AND a.at>=? AND a.correct=1"
                     " AND a.repeat=0 AND a.void IS NULL AND COALESCE(a.ms, a.sms) IS NOT NULL", learner, since):
        cfg = _json(r["cfg"], {}) or {}
        if r["kind"] in TESTS or cfg.get("timing") == "pace" or cfg.get("clock") == "pace":
            per[r["difficulty"]].append(r["ms"] / 1000)
            n += 1
    if all(len(per[t]) >= 15 for t in TIER_DEFAULT_S):
        return {t: statistics.median(per[t]) for t in TIER_DEFAULT_S}, "you", n
    return dict(TIER_DEFAULT_S), "default", n


def _scale(weights: list[float], total: int) -> list[int]:
    """Whole seconds in proportion, adding up to total exactly."""
    s = sum(weights) or 1
    raw = [w * total / s for w in weights]
    out = [math.floor(x) for x in raw]
    for i in sorted(range(len(raw)), key=lambda i: raw[i] - out[i], reverse=True)[:total - sum(out)]:
        out[i] += 1
    return out


def pace_plan(learner: str | None, form, factor: float = 1.0, reveal_route: bool = False,
              route: str | None = None, seconds: int | None = None) -> dict:
    """X3: {subject, budget_s[n], reserve_s, source, n_answers}. Each
    position's tier is the form's public ladder, never the items served;
    budgets fill duration - reserve (180 s x factor). Module 2 without the
    route revealed averages the two module 2 ladders, so it can't tell."""
    bases, source, n = _tier_bases(learner)
    if isinstance(form, list):
        weights = [bases[t] for t in form]
        dur = seconds or int(round(len(form) * SECONDS_PER_QUESTION * factor))
    else:
        if form == "module2":
            if reveal_route and route in ("upper", "lower"):
                weights = [bases[t] for t in blueprint.ladder("module2_" + route)]
            else:
                weights = [(bases[a] + bases[b]) / 2 for a, b in
                           zip(blueprint.ladder("module2_upper"), blueprint.ladder("module2_lower"))]
        else:
            weights = [bases[t] for t in blueprint.ladder(form)]
        dur = seconds or int(round(blueprint.MODULE_SECONDS * factor))
    reserve = int(round(180 * factor))
    return {"subject": "math", "budget_s": _scale(weights, max(0, dur - reserve)), "reserve_s": reserve,
            "source": source, "n_answers": n}


# ------------------------------------------------------------------ the session

class NewDiagnostic(BaseModel):
    model_config = ConfigDict(extra="forbid")
    conditions: Literal["test_day", "training"] | None = None


@router.post("/api/session")
def new_session(body: NewDiagnostic | None = None, x_learner: str | None = Header(default=None)) -> dict:
    """Start a diagnostic on one of the ten forms, drawn at random, in its
    lobby. With no code, the server mints one and returns it (SEC-07)."""
    minted = not (x_learner and x_learner.strip())
    learner = writer_of("anon:" + secrets.token_urlsafe(9)) if minted else writer_of(x_learner)
    form_id = random.choice(list(FORMS))
    opts = options(learner, NewMock(conditions=body.conditions if body else None))
    cfg = {**opts, "kind": "diagnostic", "lobby": True}
    sid = _insert(learner, "diagnostic", None, None, cfg, form_id=form_id)
    log.info("session %s started on form %d", sid[:8], form_id)
    out = payload(session_or_404(sid))
    if minted:
        out["learner"] = learner
    return out


@router.get("/api/session/{sid}")
def get_session(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    return payload(own(session_or_404(sid), x_learner))


class Answer(Stamps):
    model_config = ConfigDict(extra="forbid")
    question_id: str = Field(max_length=40)
    answer: int | str | None = None
    made_left: int | None = Field(default=None, ge=-86_400_000, le=36_000_000)
    ms: int | None = Field(default=None, ge=0, le=600_000)


def _checked_answer(q: dict, value):
    """An answer the question's format can hold (422 otherwise)."""
    if value is None or value == "":
        return None
    if q.get("type") == "spr":
        text = str(value).strip()
        shaped = GRID_OK.match(text) and (text.count(".") + text.count("/")) <= 1
        # ponytail: 15 of ~600 bank keys overflow the grid (19/900, 787500); the key itself
        # stays enterable until T-bank fixes them
        if isinstance(value, bool) or not (shaped or scoring.is_correct(q, text)):
            raise HTTPException(422, "not a grid-in answer")
        return text
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < max(4, len(q.get("choices") or [])):
        raise HTTPException(422, "not an option")
    return value


@router.post("/api/session/{sid}/answer")
def put_answer(sid: str, body: Answer, x_learner: str | None = Header(default=None)) -> dict:
    row = own(session_or_404(sid), x_learner, write=True)
    if row["kind"] in DRILLS:
        raise HTTPException(409, "a practice set is answered through /api/drill")
    if row["abandoned"]:
        raise HTTPException(409, "discarded")
    if row["finished"]:
        raise HTTPException(409, "this test is already finished")
    if not begun(row):
        raise HTTPException(409, "press Begin first")
    if row["paused_at"]:
        raise HTTPException(409, "paused")
    q = next((q for q in questions_of(row) if q["id"] == body.question_id), None)
    if q is None:
        raise HTTPException(400, "that question is not on this form")
    late = False
    if is_timed(row):
        left = _left(row)
        if left < -LATE_GRACE:
            # made in time but delivered late (the offline queue): accepted
            # within 15 minutes of time-up, and counted
            if body.made_left is None or body.made_left < 0 or left < -LATE_WINDOW:
                raise HTTPException(409, "time is up")
            late = True
    value = _checked_answer(q, body.answer)
    qid = body.question_id
    qstate = _json(row["qstate"], {}) or {}
    parts = _stamp_sets(row, body)
    if body.ms:
        parts.append(_add(_path(qid, "ms"), body.ms))
    if body.made_left is not None:
        parts.append(_set(_path(qid, "made_left"), body.made_left))
    if late:
        parts.append(_add('$."_session"."late"', 1))
    end_at = (qstate.get("_session") or {}).get("end_at")
    el = body.el if body.el is not None else elapsed_ms(row)
    if value is not None and end_at is not None and el > end_at:
        parts.append(_set(_path(qid, "pass"), 2))
    qsql, qargs = _qstate_sql(parts)
    path = f'$."{qid}"'
    if value is None:
        cur = db.run(f"UPDATE sessions SET qstate={qsql}, answers=json_remove(answers, ?)"
                     " WHERE id=? AND finished IS NULL AND abandoned IS NULL", *qargs, path, sid)
    else:
        # the first non-null answer is kept (json_insert never overwrites), and
        # a change to a different value is counted; SET sees the old row
        first = _path(qid, "first")
        changes = _path(qid, "changes")
        qsql = (f"json_insert(json_set({qsql}, ?, COALESCE(json_extract(qstate, ?), 0) +"
                f" (json_type(answers, ?) IS NOT NULL AND json_extract(answers, ?) IS NOT ?)), ?, json(?))")
        qargs = qargs + [changes, changes, path, path, value, first, json.dumps(value)]
        cur = db.run(f"UPDATE sessions SET qstate={qsql}, answers=json_set(answers, ?, json(?))"
                     " WHERE id=? AND finished IS NULL AND abandoned IS NULL",
                     *qargs, path, json.dumps(value), sid)
    if cur.rowcount != 1:
        raise HTTPException(409, "this test is already finished")
    return {"saved": True, "late": late, "answered": len(db.load_answers(session_or_404(sid)))}


class Mark(BaseModel):
    model_config = ConfigDict(extra="forbid")
    start: int = Field(ge=0, le=20_000)
    end: int = Field(ge=0, le=20_000)
    style: Literal["highlight", "strong", "underline", "dashed", "dotted", "box", "strike"]
    note: str | None = Field(default=None, max_length=500)
    at: str | None = Field(default=None, pattern=r"^(stem|t:\d{1,2}:\d{1,2}|o:[0-3])$")


class Calc(BaseModel):
    model_config = ConfigDict(extra="forbid")
    open_ms: int = Field(default=0, ge=0, le=36_000_000)
    exprs: list[str] = Field(default_factory=list, max_length=20)


class Nudge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["sink", "last_minute", "grid"]
    qid: str | None = Field(default=None, max_length=24)
    took: bool | None = None


class State(Stamps):
    model_config = ConfigDict(extra="forbid")
    question_id: str | None = Field(default=None, max_length=40)
    marked: bool | None = None
    struck: list[int] | None = Field(default=None, max_length=4)
    ms: int | None = Field(default=None, ge=0, le=600_000)
    conf: Literal["sure", "unsure", "guess"] | None = None
    note: str | None = Field(default=None, max_length=500)
    marks: list[Mark] | None = Field(default=None, max_length=50)
    away_ms: int | None = Field(default=None, ge=0, le=3_600_000)
    away_n: int | None = Field(default=None, ge=0, le=10)
    predict: Literal["miss"] | None = None
    scratch: dict | None = None
    calc: Calc | None = None
    ref_n: int | None = Field(default=None, ge=0, le=50)
    ref_ms: int | None = Field(default=None, ge=0, le=3_600_000)
    covered: bool | None = None
    reveal_ms: int | None = Field(default=None, ge=0, le=3_600_000)
    own: str | None = Field(default=None, max_length=40)
    report_later: str | None = Field(default=None, max_length=40)
    end_at: int | None = Field(default=None, ge=0, le=36_000_000)
    nudge: Nudge | None = None


def _handed_in_ids(row) -> set[str]:
    """Questions of modules already handed in."""
    if row["finished"]:
        return {q["id"] for q in marked_questions(row)}
    if two_modules(row) and (row["module"] or 1) == 2:
        return {q["id"] for q in mock_module(row, 1)}
    return set()


@router.post("/api/session/{sid}/state")
def put_state(sid: str, body: State, x_learner: str | None = Header(default=None)) -> dict:
    """Per-question state (R7, X1-X11), written in place with json_set."""
    row = own(session_or_404(sid), x_learner, write=True)
    fields = body.model_dump(exclude_unset=True)
    stamps = {k for k in ("pid", "el", "hid", "off") if k in fields}
    given = set(fields) - stamps - {"question_id"}
    qid = body.question_id
    if qid is not None and not QID_OK.match(qid):
        raise HTTPException(400, "that question is not on this form")
    # X11: a prediction on a handed-in module, until 15 minutes after the end
    if given == {"predict"}:
        if row["kind"] in DRILLS or row["abandoned"]:
            raise HTTPException(409, "discarded" if row["abandoned"] else "not a test")
        if qid is None or qid not in _handed_in_ids(row):
            raise HTTPException(409, "predictions are for a handed-in module")
        if row["finished"] and (_utc() - _at(row["finished"])).total_seconds() > PREDICT_WINDOW:
            raise HTTPException(409, "predictions close 15 minutes after the hand-in")
        if db.load_answers(row).get(qid) in (None, ""):
            raise HTTPException(409, "an unanswered question can't be a predicted miss")
        _write_qstate(sid, [_set(_path(qid, "predict"), body.predict)])
        return {"saved": True}
    _guard(row, "answer")
    live = set(_live_ids(row))
    if qid is not None and qid not in live:
        if qid in _handed_in_ids(row):
            raise HTTPException(409, "that module is handed in")
        raise HTTPException(400, "that question is not on this form")
    per_q = {"marked", "struck", "ms", "conf", "note", "marks", "predict", "scratch", "calc", "ref_n",
             "ref_ms", "covered", "reveal_ms", "own"}
    if given & per_q and qid is None:
        raise HTTPException(422, {"field": "question_id", "reason": "required for per-question state"})
    if body.struck is not None and any(i not in range(4) for i in body.struck):
        raise HTTPException(422, {"field": "struck", "reason": "option indices 0-3"})
    if body.report_later is not None and body.report_later not in live:
        raise HTTPException(422, {"field": "report_later", "reason": "a question of this module"})
    if body.calc is not None and any(len(x) > 200 for x in body.calc.exprs):
        raise HTTPException(422, {"field": "calc", "reason": "200 characters an expression"})
    scratch = json.dumps(body.scratch) if body.scratch is not None else ""
    if len(scratch) > SCRATCH_MAX:
        raise HTTPException(422, "scratch too large")
    if len(row["qstate"] or "") + len(body.model_dump_json(exclude_unset=True)) > QSTATE_MAX:
        raise HTTPException(422, "qstate too large")
    qstate = _json(row["qstate"], {}) or {}
    mine = qstate.get(qid) or {} if qid else {}
    sess = qstate.get("_session") or {}
    parts = _stamp_sets(row, body)
    for k in ("marked", "conf", "note", "covered", "own"):
        if k in fields:
            parts.append(_set(_path(qid, k), fields[k]))
    if "struck" in fields:
        parts.append(_set(_path(qid, "struck"), body.struck))
        # ponytail: read-modify-write for the union; a lost race loses a strike's history, not a strike
        parts.append(_set(_path(qid, "struck_ever"), sorted(set(mine.get("struck_ever") or []) | set(body.struck))))
    if "marks" in fields:
        parts.append(_set(_path(qid, "marks"), [m.model_dump(exclude_none=True) for m in body.marks or []]))
    if body.scratch is not None:
        parts.append(_set(_path(qid, "scratch"), body.scratch))
    if body.calc is not None:
        parts.append(_set(_path(qid, "calc"), body.calc.model_dump()))
    for k in ("ms", "ref_n", "ref_ms"):
        if fields.get(k):
            parts.append(_add(_path(qid, k), fields[k]))
    if body.reveal_ms is not None:
        parts.append(_set(_path(qid, "reveal_ms"), body.reveal_ms))
    for k in ("away_ms", "away_n"):
        if fields.get(k):
            parts.append(_add(f'$."_session"."{k}"', fields[k]))
    if body.report_later is not None:
        later = list(dict.fromkeys((sess.get("report_later") or []) + [body.report_later]))
        parts.append(_set('$."_session"."report_later"', later))
    if body.nudge is not None:
        nudges = (sess.get("nudges") or [])[-99:] + [{**body.nudge.model_dump(), "at": elapsed_ms(row)}]
        parts.append(_set('$."_session"."nudges"', nudges))
    sql, args = _qstate_sql(parts)
    if body.end_at is not None:
        sql, args = f"json_insert({sql}, ?, ?)", args + ['$."_session"."end_at"', body.end_at]
    if (parts or body.end_at is not None) and db.run(f"UPDATE sessions SET qstate={sql} WHERE id=? AND finished IS NULL"
                                  " AND abandoned IS NULL", *args, sid).rowcount != 1:
        raise HTTPException(409, "this test is already finished")
    return {"saved": True}


class Begin(Stamps):
    model_config = ConfigDict(extra="forbid")
    between_ms: int | None = Field(default=None, ge=0, le=86_400_000)
    at: str | None = Field(default=None, max_length=40)


def _remember(row) -> None:
    if row["learner"]:
        db.remember(row["learner"], [{"key": q["key"], "seed": q["seed"],
                                      "stem_hash": practice.stem_hash(q["stem"])}
                                     for q in questions_of(row) if "key" in q], now())


@router.post("/api/session/{sid}/begin")
def begin(sid: str, body: Begin | None = None, x_learner: str | None = Header(default=None)) -> dict:
    """Start the live module's clock, or resume a pause. Owner-only, idempotent."""
    body = body or Begin()
    row = own(session_or_404(sid), x_learner, write=True)
    if row["kind"] in DRILLS:
        raise HTTPException(409, "a practice set starts through /api/drill")
    if row["abandoned"]:
        raise HTTPException(409, "discarded")
    if row["finished"]:
        raise HTTPException(409, "this test is already finished")
    stamp = now()
    if row["paused_at"]:
        gone = int((_utc() - _at(row["paused_at"])).total_seconds() * 1000)
        db.run("UPDATE sessions SET paused_ms=COALESCE(paused_ms,0)+?, paused_at=NULL"
               " WHERE id=? AND paused_at IS NOT NULL", gone, sid)
    elif not begun(row):
        start = stamp
        m1 = _json(row["module1"], {}) or {}
        floor = m1.get("at") or row["started"]
        if body.at:
            # a Begin queued offline starts the clock when it was pressed
            try:
                t = _at(body.at).astimezone(dt.timezone.utc)
                if _at(floor) <= t <= _utc():
                    start = t.isoformat(timespec="seconds")
            except ValueError:
                pass
        if db.run("UPDATE sessions SET module_started=? WHERE id=? AND module_started IS NULL",
                  start, sid).rowcount:
            _remember(row)
            if (row["module"] or 1) == 2:
                qstate = _json(row["qstate"], {}) or {}
                pids = (qstate.get("_session") or {}).get("pids") or {}
                same_page = body.pid and f"m1:{body.pid}" in pids
                if same_page and body.between_ms is not None:
                    between = {"ms": body.between_ms, "source": "stamp"}
                else:
                    ms = int((_at(start) - _at(floor)).total_seconds() * 1000)
                    between = {"ms": max(0, ms), "source": "server"}
                _write_qstate(sid, [_set('$."_session"."between"', between)])
    row = session_or_404(sid)
    _write_qstate(sid, _stamp_sets(row, body))
    return payload(session_or_404(sid))


@router.post("/api/session/{sid}/pause")
def pause(sid: str, body: Stamps | None = None, x_learner: str | None = Header(default=None)) -> dict:
    """Save and exit: the clock stops until /begin. A timed, live sitting only;
    anything else is left as it is."""
    row = own(session_or_404(sid), x_learner, write=True)
    if row["kind"] in DRILLS:
        raise HTTPException(409, "a practice set pauses through /api/drill")
    if row["abandoned"]:
        raise HTTPException(409, "discarded")
    if row["finished"]:
        raise HTTPException(409, "this test is already finished")
    _write_qstate(sid, _stamp_sets(row, body))
    if begun(row) and is_timed(row) and not row["paused_at"]:
        db.run("UPDATE sessions SET paused_at=?, pauses=COALESCE(pauses,0)+1"
               " WHERE id=? AND paused_at IS NULL AND finished IS NULL", now(), sid)
    return payload(session_or_404(sid))


class Options(BaseModel):
    """What a sitting runs with (the start sheet's steps 3 and 4)."""
    model_config = ConfigDict(extra="forbid")
    conditions: Literal["test_day", "training"] | None = None
    timing: Literal["official", "x1.5", "x2", "untimed", "x0.85"] | None = None
    minutes: int | None = Field(default=None, ge=1, le=180)
    calculator: bool | None = None
    pace: bool | None = None
    confidence: bool | None = None
    reveal_route: bool | None = None
    nudges: bool | None = None
    cover: bool | None = None
    predict: bool | None = None
    type_notes: bool | None = None
    fullscreen: bool | None = None


def options(learner: str, body: "Options", base: dict | None = None) -> dict:
    """The sitting's cfg options: the body over this sitting's (or the
    learner's test_* prefs). Test-day leaves every Training aid out."""
    from . import prefs
    p = prefs.get(learner) if learner and not db.is_sample(learner) else dict(prefs.DEFAULTS)
    old = base or {}
    pick = lambda k, pref: (getattr(body, k) if getattr(body, k, None) is not None  # noqa: E731
                            else old.get(k, p.get(pref)))
    conditions = pick("conditions", "test_conditions") or "test_day"
    training = conditions == "training"
    timing = body.timing
    if timing is None:
        timing = old.get("timing") or p.get("test_timing") or "official"
        if getattr(body, "timed", None) is False:
            timing = "untimed"
        if timing == "x0.85" and not training:
            timing = "official"
    elif timing == "x0.85" and not training:
        raise HTTPException(422, {"field": "timing", "reason": "tight clock is a training timing"})
    out = {"conditions": conditions, "timing": timing, "timed": timing != "untimed",
           "calculator": bool(pick("calculator", "test_calculator")),
           "fullscreen": bool(pick("fullscreen", "test_fullscreen")),
           "predict": bool(pick("predict", "test_predict"))}
    for k, pref in (("pace", "test_pace"), ("confidence", "test_confidence"),
                    ("reveal_route", "test_reveal_route"), ("nudges", "test_nudges"),
                    ("cover", "test_cover"), ("type_notes", "test_type_notes")):
        out[k] = training and bool(pick(k, pref))
    minutes = body.minutes if body.minutes is not None else old.get("minutes")
    if minutes:
        out["minutes"] = minutes
    return out


@router.post("/api/session/{sid}/cfg")
def put_cfg(sid: str, body: Options, x_learner: str | None = Header(default=None)) -> dict:
    """Change a sitting's settings in the lobby, before module 1 begins."""
    row = own(session_or_404(sid), x_learner, write=True)
    if row["kind"] not in TESTS:
        raise HTTPException(409, "not a test")
    if row["abandoned"]:
        raise HTTPException(409, "discarded")
    if row["finished"] or begun(row) or (row["module"] or 1) != 1 or not _cfg(row).get("lobby"):
        raise HTTPException(409, "already begun")
    cfg = _cfg(row)
    if body.minutes is not None and row["kind"] != "custom":
        raise HTTPException(422, {"field": "minutes", "reason": "own minutes are for a custom test"})
    cfg.update(options(row["learner"], body, base=cfg))
    if db.run("UPDATE sessions SET cfg=? WHERE id=? AND module_started IS NULL AND finished IS NULL",
              json.dumps(cfg), sid).rowcount != 1:
        raise HTTPException(409, "already begun")
    return payload(session_or_404(sid))


@router.post("/api/session/{sid}/discard")
def discard(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    """Throw a sitting away. It is never finished, so nothing that reads
    `finished` counts it, and nothing is filed to attempts."""
    row = own(session_or_404(sid), x_learner, write=True)
    if row["kind"] not in TESTS:
        raise HTTPException(409, "not a test")
    if row["finished"]:
        raise HTTPException(409, "this test is already finished")
    db.run("UPDATE sessions SET abandoned=COALESCE(abandoned, ?) WHERE id=? AND finished IS NULL", now(), sid)
    return {"id": sid, "discarded": session_or_404(sid)["abandoned"]}


class NoteIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(default="", max_length=1000)


@router.put("/api/session/{sid}/note")
def put_note(sid: str, body: NoteIn, x_learner: str | None = Header(default=None)) -> dict:
    row = own(session_or_404(sid), x_learner, write=True)
    if row["kind"] not in TESTS:
        raise HTTPException(409, "not a test")
    text = body.text.strip() or None
    db.run("UPDATE sessions SET note=? WHERE id=?", text, sid)
    return {"id": sid, "note": text}


# ------------------------------------------------------------------ finishing

class Finish(Stamps):
    model_config = ConfigDict(extra="forbid")


def _flagged(row) -> set[str]:
    return {r["qid"] for r in db.rows("SELECT qid FROM flags WHERE session=?", row["id"])}


def summary(row, qs: list[dict]) -> dict:
    """What was handed in: answered, unanswered, marked, guesses, time."""
    answers = db.load_answers(row)
    qstate = _json(row["qstate"], {}) or {}
    flagged = _flagged(row)
    answered = sum(answers.get(q["id"]) not in (None, "") for q in qs)
    sess = qstate.get("_session") or {}
    return {"answered": answered, "unanswered": len(qs) - answered,
            "marked": sum(bool((qstate.get(q["id"]) or {}).get("marked")) or q["id"] in flagged for q in qs),
            "guesses": sum((qstate.get(q["id"]) or {}).get("conf") == "guess" for q in qs),
            "ms": sum((qstate.get(q["id"]) or {}).get("ms") or 0 for q in qs),
            "away_ms": sess.get("away_ms", 0),
            "timed_out": bool(is_timed(row) and _left(row) <= 0),
            "left_s": remaining(row) if is_timed(row) else None}


def _removed(q: dict) -> bool:
    """X10: a question with a confirmed bad key (or quarantined) leaves the score."""
    fn = deps.part("reports", "removed")
    return bool(fn and "key" in q and fn(q["key"], q["seed"]))


def _builder(learner: str) -> practice.Builder:
    return drill._builder(learner)


def _twin_builder(learner: str) -> practice.Builder:
    """For twins: a new (template, seed) whose rendered question is new. A
    graph template keeps its stem's words, so stem dedupe would spend it on
    the very sitting being twinned."""
    return drill._builder(learner, dedupe="question")


def exposure(learner: str) -> dict[str, int]:
    """X2: the learner's attempts plus practice_seen rows per template."""
    out: Counter = Counter()
    for r in db.rows("SELECT template, COUNT(*) AS n FROM attempts WHERE learner=? GROUP BY template", learner):
        out[r["template"]] += r["n"]
    for r in db.rows("SELECT template, COUNT(*) AS n FROM practice_seen WHERE learner=? GROUP BY template", learner):
        out[r["template"]] += r["n"]
    return dict(out)


def fresh_module(learner: str, form: str, training: bool = False) -> list[dict]:
    """A module built to the blueprint now, from questions this learner has
    never been given: a seeded shuffle for Test-day, the least-met types
    first for Training (X2). Remembered at /begin, not here."""
    if training:
        return blueprint.module(form, _builder(learner), order="exposure", exposure=exposure(learner))
    return blueprint.module(form, _builder(learner), order="shuffle")


def _pairs_questions(pairs: list[list], prefix: str, start: int = 1) -> list[dict]:
    """Exact (template, seed) items as stored questions with ids {prefix}q01.."""
    cards = []
    for t, s in pairs:
        cards.append(practice.Card.of(t, s, practice.generate(t, s), practice.topic_of(t)))
    return blueprint.stored(cards, prefix, start)


def _module2(row, cfg: dict, route: str) -> list[dict] | None:
    """Module 2 for the route earned: copied for papers, twins and shares when
    it matches, else built fresh; the Final's from its contest's twin slots."""
    learner = row["learner"]
    prefix = blueprint.PREFIX["module2_" + route]
    if _contest_kind(row) == "final":
        spec = _json(db.one("SELECT spec FROM contests WHERE id=?", row["contest"])["spec"], {}) or {}
        twin = deps.part("compete", "twin_questions")
        return twin(learner, row["contest"], spec["slots_m2"][route], start_slot=len(mock_module(row, 1)) + 1)
    if cfg.get("twin_source"):
        src = db.one("SELECT * FROM sessions WHERE id=?", cfg["twin_source"])
        if src is not None and src["route"] == route:
            return blueprint.twin(mock_module(src, 2), _twin_builder(learner))
    if cfg.get("paper"):
        if cfg.get("exact"):
            first = _first_of_paper(learner, cfg["paper"], exclude=row["id"])
            if first is not None and first["route"] == route:
                return [dict(q) for q in (_json(first["questions"], {}) or {}).get("module2", [])]
        return blueprint.twin_slots(papers.slots(cfg["paper"], "module2_" + route), _twin_builder(learner), prefix)
    if cfg.get("share"):
        m2 = cfg.get("shared_m2") or []
        match = bool(m2) and cfg.get("shared_route") == route
        cfg["shared_route_match"] = match
        if match:
            return _pairs_questions(m2, prefix)
    if row["mock_id"] in MOCKS:
        return None
    return fresh_module(learner, "module2_" + route, _training(cfg))


def _route(row, cfg: dict, body) -> dict:
    """Finishing module 1 routes. Which module 2 is decided from module 1
    alone, as on the day, and there is no way back into module 1."""
    answers = db.load_answers(row)
    m1 = mock_module(row, 1)
    right = sum(1 for q in m1 if scoring.is_correct(q, answers.get(q["id"])))
    verdict = scoring.route_after(right, len(m1))
    fixed = cfg.get("route") in ("upper", "lower")
    route = cfg["route"] if fixed else verdict
    info = {"right": right, "asked": len(m1), "at": now(), "would_route": verdict,
            "summary": summary(row, m1), "fixed": fixed}
    m2 = _module2(row, cfg, route)
    built = _json(row["questions"])
    questions = row["questions"]
    if isinstance(built, dict) and m2 is not None:
        built["module2"] = m2
        questions = json.dumps(built, ensure_ascii=False)
    # module 2's clock waits for its own Begin in the lobby flow
    started = None if cfg.get("lobby") else now()
    # The route and module 2 are set in one statement that only a paper
    # still in module 1 matches, so a second finish sent at the same moment
    # cannot route it again; it is told where the first one went.
    # end_at (X5) is module 1's; module 2's second pass starts from its own
    if not db.run("UPDATE sessions SET module=2, route=?, module1=?, module_started=?, paused_ms=0,"
                  " paused_at=NULL, questions=?, cfg=?,"
                  " qstate=json_remove(COALESCE(qstate,'{}'), '$.\"_session\".\"end_at\"')"
                  " WHERE id=? AND COALESCE(module, 1)=1 AND finished IS NULL",
                  route, json.dumps(info), started, questions, json.dumps(cfg), row["id"]).rowcount:
        m = _json(session_or_404(row["id"])["module1"], {}) or {}
        return {"next_module": 2, "finished_module": 1, "summary": m.get("summary")}
    log.info("sitting %s: module 1 %d/%d -> %s module 2", row["id"][:8], right, len(m1), route)
    out = {"next_module": 2, "finished_module": 1, "summary": info["summary"]}
    if _training(cfg) and cfg.get("reveal_route"):
        out.update({"route": route, "right": right, "asked": len(m1), "gate": gate_of(m1, answers)})
    return out


def _positions(qs: list[dict], ids: set[str]) -> list[int]:
    return [i for i, q in enumerate(qs, 1) if q["id"] in ids]


def gate_of(m1: list[dict], answers: dict, subject: str = "math") -> dict:
    """X14: module 1's margin to the harder module 2."""
    right = sum(scoring.is_correct(q, answers.get(q["id"])) for q in m1)
    needed = math.ceil(scoring.ROUTE_UP_AT * len(m1))
    cheap = [i for i, q in enumerate(m1, 1) if q["difficulty"] in ("easy", "medium")
             and not scoring.is_correct(q, answers.get(q["id"]))]
    return {"subject": subject, "right": right, "needed": needed, "margin": right - needed,
            "cheap_misses": cheap}


def scored_of(row, cfg: dict) -> tuple[bool, str | None]:
    """R16 via §3.4.5: which kinds give a score estimate."""
    m1 = cfg.get("m1", "standard")
    if row["kind"] == "custom":
        return False, "trap test" if (cfg.get("custom") or {}).get("source") == "traps" else "custom test"
    if row["kind"] == "diagnostic":
        return True, None
    if row["kind"] == "module" and cfg.get("module") in ("m2u", "m2l"):
        return False, "single module 2"
    if m1 == "upper":
        return False, "harder module 1"
    if m1 == "lower":
        return False, "easier module 1"
    return True, None


def away_of(qstate: dict) -> tuple[int, int]:
    """(away ms, offline ms) from the client's stamps, per module: each page
    load's hidden time, plus the clock time between one page load's last
    stamp and the next one's first (the page was closed). Offline time never
    counts as away."""
    pids = (qstate.get("_session") or {}).get("pids") or {}
    by: dict[str, list[dict]] = defaultdict(list)
    for key, v in pids.items():
        if isinstance(v, dict):
            by[key.split(":", 1)[0]].append(v)
    away = off = 0
    for loads in by.values():
        loads.sort(key=lambda v: v.get("first_el") or 0)
        for i, v in enumerate(loads):
            away += v.get("hid") or 0
            off += v.get("off") or 0
            if i:
                away += max(0, (v.get("first_el") or 0) - (loads[i - 1].get("last_el") or 0))
    if not by:
        away = (qstate.get("_session") or {}).get("away_ms") or 0
    return int(away), int(off)


def rank_of(row, cfg: dict, partial: bool = False) -> tuple[int, str | None]:
    """X1: a sitting ranks when Test-day, official timing, adaptive, standard
    module 1, a rankable kind, no pause, a break of 75 s or less and 2 minutes
    or less away. The reason is the first rule that fails."""
    if cfg.get("conditions", "test_day") == "training":
        return 0, "training"
    pauses = row["pauses"] or 0
    if pauses:
        return 0, {1: "paused once", 2: "paused twice"}.get(pauses, f"paused {pauses} times")
    timing = timing_of(row)
    if timing != "official":
        return 0, TIMING_WHY.get(timing, timing)
    if cfg.get("route") in ("upper", "lower"):
        return 0, "fixed route"
    scored, why = scored_of(row, cfg)
    if not scored:
        return 0, why
    qstate = _json(row["qstate"], {}) or {}
    between = (qstate.get("_session") or {}).get("between") or {}
    if (between.get("ms") or 0) > BREAK_MAX_MS:
        return 0, f"break {mmss(between['ms'])}"
    away, _ = away_of(qstate)
    if away > AWAY_MAX_MS:
        return 0, f"away {mmss(away)}"
    return 1, None


def _new_types(row, marked: list[dict], answers: dict) -> dict:
    """X2: the types met under the clock for the first time in this sitting."""
    met = _met_templates(row["learner"], exclude=row["id"])
    new = [q for q in marked if "key" in q and q["key"] not in met]
    templates = list(dict.fromkeys(q["key"] for q in new))
    right = len({q["key"] for q in new if scoring.is_correct(q, answers.get(q["id"]))})
    return {"n": len(templates), "right": right, "templates": templates}


def _moments(row, result: dict, est: dict | None, prev: dict | None) -> list[dict]:
    """X12: up to two earned moments from a fixed list; nothing when none."""
    out = []
    learner = row["learner"]
    band = result.get("estimate") or {}
    if row["kind"] == "mock" and row["route"] == "upper" and learner and not db.one(
            "SELECT 1 FROM sessions WHERE learner=? AND kind='mock' AND route='upper' AND finished IS NOT NULL"
            " AND id!=?", learner, row["id"]):
        out.append({"id": "first_upper", "text": "Your first harder module 2"})
    if band.get("low") is not None and est and est.get("best") and est["best"]["id"] == row["id"] and prev:
        out.append({"id": "best", "text": "A new best band"})
    cfg = _cfg(row)
    mid = _mid(result)
    if mid is not None and cfg.get("paper"):
        p = papers.paper(cfg["paper"])
        others = [m for r in papers.firsts(p)[0].values() if r["id"] != row["id"]
                  for m in [papers._mid(r)] if m is not None] if p else []
        if len(others) >= papers.AVERAGE_N and mid > statistics.mean(others):
            out.append({"id": "paper_avg", "text": "Above this paper's average"})
    if mid is not None and cfg.get("twin_source"):
        src = db.one("SELECT result FROM sessions WHERE id=?", cfg["twin_source"])
        was = _mid(_json(src["result"], {}) or {}) if src else None
        if was is not None and mid - was >= 30:
            out.append({"id": "twin_up", "text": f"Up {int(round((mid - was) / 10) * 10)} on the original"})
    if not any(m["blank"] for m in result.get("modules", [])):
        out.append({"id": "no_blanks", "text": "No blanks"})
    left = [(_json(row["module1"], {}) or {}).get("summary", {}).get("left_s"), result.get("left_s")]
    if is_timed(row) and all(x is not None and x >= 180 for x in left if x is not None) and any(x is not None for x in left):
        out.append({"id": "time_left", "text": "Every module finished with 3:00 or more left"})
    return out[:2]


def pressure_questions(row) -> list[str]:
    """X13: wrong, blank, tagged Guess, or over 2 x budget x factor; at most
    15, wrong and blank first, then in position order."""
    answers = db.load_answers(row)
    qstate = _json(row["qstate"], {}) or {}
    factor = FACTOR.get(timing_of(row), 1.0)
    first, then = [], []
    for q in marked_questions(row):
        given = answers.get(q["id"])
        st = qstate.get(q["id"]) or {}
        if given in (None, "") or not scoring.is_correct(q, given):
            first.append(q["id"])
        elif st.get("conf") == "guess" or (st.get("ms") or 0) > 2 * TIER_DEFAULT_S[q["difficulty"]] * 1000 * factor:
            then.append(q["id"])
    return (first + then)[:PRESSURE_MAX]


def pressure_eligible(row) -> tuple[bool, str | None]:
    cfg = _cfg(row)
    if not row["finished"] or row["kind"] not in TESTS:
        return False, "finish the test first"
    if not is_timed(row):
        return False, "untimed"
    if (cfg.get("custom") or {}).get("source") == "traps":
        return False, "a trap test is already a retest"
    if ((_json(row["qstate"], {}) or {}).get("_session") or {}).get("keys_seen"):
        return False, "answers already seen"
    if (_utc() - _at(row["finished"])).days >= PRESSURE_DAYS:
        return False, "the pressure check closes 7 days after the test"
    if (_json(row["result"], {}) or {}).get("pressure"):
        return False, "already done"
    if not pressure_questions(row):
        return False, "nothing to check"
    return True, None


def _done(row, result: dict) -> dict:
    """X12: the hand-in moment."""
    from . import estimate
    learner = row["learner"]
    est = estimate.estimate(learner) if learner and result.get("scored") and row["kind"] != "diagnostic" else None
    band = result.get("estimate") or {}
    prev = est["previous"] if est else None
    target = db.one("SELECT target FROM learners WHERE id=?", learner) if learner else None
    ok, _ = pressure_eligible(row)
    n = len(pressure_questions(row)) if ok else 0
    qstate = _json(row["qstate"], {}) or {}
    misses = sum(len(m["missed"]) for m in result.get("modules", []))
    blanks = sum(len(m["blank"]) for m in result.get("modules", []))
    headline = None
    if band.get("low") is not None and row["kind"] != "diagnostic":
        if prev:
            d = (band["low"] + band["high"]) / 2 - prev["mid"]
            day = prev["at"][:10]
            headline = (f"Up {int(round(d / 10) * 10)} since {day}" if d >= 10 else
                        f"Down {int(round(-d / 10) * 10)} since {day}" if d <= -10 else f"Level with {day}")
        else:
            headline = "Your first estimate"
    return {"subject": row["subject"] if "subject" in row.keys() and row["subject"] else "math",
            "kind_label": kind_label(row), "number": row["number"],
            "estimate": None if band.get("low") is None or row["kind"] == "diagnostic" else {
                "low": band["low"], "high": band["high"],
                "previous": {"low": prev["low"], "high": prev["high"]} if prev else None,
                "best": {"low": est["best"]["low"], "high": est["best"]["high"]} if est and est.get("best") else None,
                "target": target["target"] if target else None},
            "headline": headline, "route": row["route"], "gate": result.get("gate"),
            "moments": _moments(row, result, est, prev), "misses": misses, "blanks": blanks,
            "right": result.get("right"), "asked": result.get("asked"),
            "report_later": (qstate.get("_session") or {}).get("report_later") or [],
            "ranked": result.get("ranked"), "unranked_why": result.get("unranked_why"),
            "pressure": {"eligible": ok and n > 0, "n": n, "minutes": max(1, round(n * 80 / 60)) if n else 0},
            "scored": result.get("scored"), "not_scored": result.get("not_scored")}


def _final(row, cfg: dict) -> dict:
    marked = marked_questions(row)
    answers = db.load_answers(row)
    qstate = _json(row["qstate"], {}) or {}
    removed = [q["id"] for q in marked if _removed(q)]
    kept = [q for q in marked if q["id"] not in removed]
    result = scoring.score(kept, answers)
    mods = []
    for n, qs in enumerate(_modules(row), 1):
        live = [q for q in qs if q["id"] not in removed]
        wrong = {q["id"] for q in live if answers.get(q["id"]) not in (None, "")
                 and not scoring.is_correct(q, answers.get(q["id"]))}
        blank = {q["id"] for q in live if answers.get(q["id"]) in (None, "")}
        mods.append({"subject": row["subject"] or "math", "n": n,
                     "right": sum(scoring.is_correct(q, answers.get(q["id"])) for q in live),
                     "asked": len(live), "missed": _positions(qs, wrong), "blank": _positions(qs, blank)})
    scored, not_scored = scored_of(row, cfg)
    sess = qstate.get("_session") or {}
    away, offline = away_of(qstate)
    m1_info = _json(row["module1"], {}) or {}
    timing = timing_of(row)
    now_summary = summary(row, questions_of(row))
    result.update({
        "subject": row["subject"] or "math", "modules": mods, "removed": removed,
        "timing": timing, "factor": FACTOR.get(timing, 1.0), "extended": timing in ("x1.5", "x2"),
        "pauses": row["pauses"] or 0, "late": sess.get("late", 0),
        "away": {"ms": away, "n": sess.get("away_n", 0)}, "offline_ms": offline,
        "fixed_route": cfg.get("route") in ("upper", "lower"), "scored": scored,
        "conditions": cfg.get("conditions", "test_day"), "left_s": now_summary["left_s"],
        "summary": now_summary,
    })
    if sess.get("between"):
        result["between"] = sess["between"]
    if m1_info:
        result["module1"] = {k: m1_info.get(k) for k in ("right", "asked")}
        result["would_route"] = m1_info.get("would_route")
    passed = [q for q in marked if (qstate.get(q["id"]) or {}).get("pass") == 2]
    result["pass2"] = {"answered": len(passed), "right": sum(scoring.is_correct(q, answers.get(q["id"])) for q in passed)}
    result["new_types"] = _new_types(row, kept, answers)
    if row["kind"] == "mock" or two_modules(row):
        result["mock"] = row["mock_id"]
        result["route"] = row["route"]
        result["estimate"] = scoring.section_score(result, row["route"]) if scored else None
    elif not scored:
        result["estimate"] = None
    if not scored:
        result["not_scored"] = not_scored
    if cfg.get("m1", "standard") == "standard" and row["kind"] in ("mock", "module") and cfg.get("module", "m1") == "m1":
        result["gate"] = gate_of(mock_module(row, 1), answers, result["subject"])
    ranked, why = rank_of(row, cfg)
    result["ranked"], result["unranked_why"] = bool(ranked), why
    stamp = now()
    # marked once: a second finish at the same moment finds it done and files nothing
    if not db.run("UPDATE sessions SET finished=?, result=?, ranked=?, unranked_why=?, qstate=json_set("
                  "COALESCE(qstate,'{}'), '$.\"_session\".\"offline_ms\"', ?) WHERE id=? AND finished IS NULL",
                  stamp, json.dumps(result), ranked, why, offline, row["id"]).rowcount:
        done = session_or_404(row["id"])
        return {"finished": done["finished"], "already": True,
                "done": (_json(done["result"], {}) or {}).get("done")}
    if row["learner"]:
        # every answered question goes on the learner's map, a removed one aside
        progress.record_paper(row["learner"], row["id"], kept, answers, qstate)
    if row["contest"]:
        hook = deps.part("compete", "finish_contest")
        if hook:
            hook(session_or_404(row["id"]))
    fresh = session_or_404(row["id"])
    res = _json(fresh["result"], {}) or {}
    res["done"] = done = _done(fresh, res)
    db.run("UPDATE sessions SET result=? WHERE id=?", json.dumps(res), row["id"])
    log.info("session %s finished: %d/%d", row["id"][:8], result["right"], result["asked"])
    return {"finished": stamp, "right": result["right"], "asked": result["asked"],
            "summary": now_summary, "done": done}


@router.post("/api/session/{sid}/finish")
def finish(sid: str, body: Finish | None = None, x_learner: str | None = Header(default=None)) -> dict:
    """Hand in the live module. Module 1 of a section routes; the last one marks
    the paper, files it, and returns the hand-in moment (X12)."""
    row = own(session_or_404(sid), x_learner, write=True)
    if row["kind"] in DRILLS:
        raise HTTPException(409, "a practice set is finished through /api/drill")
    if row["abandoned"]:
        raise HTTPException(409, "discarded")
    if row["finished"]:
        return {"finished": row["finished"], "already": True,
                "done": (_json(row["result"], {}) or {}).get("done")}
    if not begun(row):
        raise HTTPException(409, "press Begin first")
    if row["paused_at"]:
        raise HTTPException(409, "paused")
    _write_qstate(sid, _stamp_sets(row, body))
    row = session_or_404(sid)
    cfg = _cfg(row)
    if two_modules(row) and (row["module"] or 1) == 1:
        return _route(row, cfg, body)
    return _final(row, cfg)


def predicted(row) -> dict:
    """X11 for the report: Spotted, Silent, Underconfident, from predictions
    and Unsure / Guess tags. S6 renders it."""
    answers = db.load_answers(row)
    qstate = _json(row["qstate"], {}) or {}
    out = {"spotted": 0, "silent": 0, "underconfident": 0, "made": 0, "qids": {}}
    for q in marked_questions(row):
        st = qstate.get(q["id"]) or {}
        given = answers.get(q["id"])
        if given in (None, ""):
            continue
        pred = st.get("predict") == "miss"
        out["made"] += pred
        if scoring.is_correct(q, given):
            if pred:
                out["underconfident"] += 1
                out["qids"][q["id"]] = "underconfident"
        else:
            k = "spotted" if pred or st.get("conf") in ("unsure", "guess") else "silent"
            out[k] += 1
            out["qids"][q["id"]] = k
    return out


# ------------------------------------------------------------------ making a sitting

class Custom(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: Literal["skills", "mistakes", "saved", "misses", "traps"] = "skills"
    from_session: str | None = Field(default=None, max_length=80)
    topics: list[str] = Field(default_factory=list, max_length=19)
    count: int | None = Field(default=None, ge=5, le=60)
    order: Literal["ladder", "mixed"] = "ladder"
    formats: Literal["both", "mcq", "spr"] = "both"
    tiers: list[Literal["easy", "medium", "hard"]] = Field(default_factory=lambda: ["easy", "medium", "hard"],
                                                           min_length=1)
    traps: Literal["all", "open", "due"] | list[int] = "all"
    neutral: Literal[0, 0.25] = 0.25


class NewMock(Options):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["section", "module", "custom", "twin", "paper", "shared"] | None = None
    module: Literal["m1", "m2u", "m2l"] | None = None
    m1: Literal["standard", "upper", "lower"] | None = None
    route: Literal["adaptive", "upper", "lower"] | None = None
    paper: int | None = Field(default=None, ge=1, le=100_000)
    exact: bool = False
    shared: str | None = Field(default=None, max_length=20)
    twin_of: str | None = Field(default=None, max_length=80)
    like: str | None = Field(default=None, max_length=80)
    trainer: Literal["route", "gauntlet"] | None = None
    custom: Custom | None = None
    full: bool | None = None            # the old body: full -> section, else module 1
    timed: bool | None = None           # the old body: false -> untimed


def _insert(learner: str, kind: str, mock_id: str | None, questions: dict | None, cfg: dict,
            form_id: int | None = None, subject: str = "math") -> str:
    """A sitting in its lobby; `number` is counted inside the insert."""
    sid = secrets.token_urlsafe(16)
    db.run("INSERT INTO sessions (id, kind, mock_id, form_id, module, learner, started, questions, cfg,"
           " subject, number) VALUES (?,?,?,?,1,?,?,?,?,?, (SELECT COUNT(*)+1 FROM sessions WHERE learner=?"
           " AND abandoned IS NULL AND kind IN ('mock','module','custom','diagnostic')))",
           sid, kind, mock_id, form_id, learner, now(),
           json.dumps(questions, ensure_ascii=False) if questions is not None else None,
           json.dumps(cfg), subject, learner)
    return sid


def _source_sitting(learner: str, sid: str) -> object:
    src = db.one("SELECT * FROM sessions WHERE id=?", sid)
    if src is None:
        raise HTTPException(404, "no such session")
    if src["learner"] != learner:
        raise HTTPException(403, "that test belongs to another code")
    if src["kind"] not in ("mock", "module") or not src["finished"]:
        raise HTTPException(409, "a twin is of a finished section or module")
    return src


def _first_of_paper(learner: str, n: int, exclude: str | None = None):
    return db.one("SELECT * FROM sessions WHERE learner=? AND mock_id=? AND abandoned IS NULL AND id!=?"
                  " ORDER BY started, rowid LIMIT 1", learner, f"P{n}", exclude or "")


def _trap_queue(learner: str, c: Custom) -> list[tuple[str, str]]:
    """X16: (template, norm) of the traps to put on offer."""
    today = dt.date.today().isoformat()
    since = (_utc() - dt.timedelta(days=60)).isoformat()
    rows = db.rows("SELECT * FROM traps WHERE learner=? AND norm IS NOT NULL AND norm!=''"
                   " AND (closed IS NULL OR closed>=?) ORDER BY last DESC", learner, since)
    if isinstance(c.traps, list):
        rows = [r for r in rows if r["id"] in set(c.traps)]
    elif c.traps == "open":
        rows = [r for r in rows if r["closed"] is None]
    elif c.traps == "due":
        rows = [r for r in rows if r["closed"] is not None and r["due"] and r["due"][:10] <= today]
    if c.from_session:
        src = db.one("SELECT * FROM sessions WHERE id=? AND learner=?", c.from_session, learner)
        if src is None:
            raise HTTPException(404, "no such session")
        mine = {(a["template"], a["norm"]) for a in db.rows(
            "SELECT template, norm FROM attempts WHERE session=? AND correct=0", c.from_session)}
        rows = [r for r in rows if (r["template"], r["norm"]) in mine] or \
               [r for r in db.rows("SELECT * FROM traps WHERE learner=? AND norm IS NOT NULL", learner)
                if (r["template"], r["norm"]) in mine]
    return [(r["template"], r["norm"]) for r in rows]


def _offers(card: practice.Card, norm: str) -> bool:
    return norm in progress.offered_of(practice.to_question(card, 1))


def _neutral(b: practice.Builder, templates: list[str], norms: set[str], n: int) -> list[practice.Card]:
    """Neutral slots: the same skills, none of the learner's trap norms on offer."""
    out = []
    pool = [t for tp in dict.fromkeys(practice.topic_of(t) for t in templates)
            for t in practice.catalogue()["by_topic"].get(tp, [])]
    random.Random(b.learner).shuffle(pool)
    for t in pool:
        if len(out) >= n:
            break
        for _ in range(6):
            card = b.draw(t, practice.topic_of(t))
            if card is None:
                break
            b.keep(card)
            if not (set(progress.offered_of(practice.to_question(card, 1))) & norms):
                out.append(card)
                break
    return out


def _custom(learner: str, c: Custom) -> tuple[list[dict], dict]:
    b = _builder(learner)
    if c.source == "skills":
        cat = practice.catalogue()
        bad = [t for t in c.topics if t not in cat["by_topic"]]
        if not c.topics or bad:
            raise HTTPException(422, {"field": "custom.topics", "reason": "known skill slugs, at least one"})
        return blueprint.custom(c.topics, c.count or 22, list(c.tiers), c.order, c.formats, b,
                                exposure=exposure(learner)), {}
    if c.source == "saved":
        pairs = [[r["template"], r["seed"]] for r in db.rows(
            "SELECT template, seed FROM saved WHERE learner=? ORDER BY at DESC", learner)]
        pairs = [p for p in pairs if deps.access(learner, p[0], p[1]) in ("reveal", "kept")][:c.count or 22]
        if not pairs:
            raise HTTPException(409, {"reason": "nothing saved"})
        return _pairs_questions(pairs, "c", 1), {}
    if c.source == "mistakes":
        queue = [r["template"] for r in db.rows("SELECT template FROM traps WHERE learner=? AND closed IS NULL"
                                                " ORDER BY last DESC", learner)]
        if not queue:
            raise HTTPException(409, {"reason": "no open mistakes"})
        qs = blueprint.custom([], 0, ["easy"], "ladder", "both", b, queue=queue[:c.count or 22])
        return [dict(q, id=f"c{i:02d}") for i, q in enumerate(qs, 1)], {}
    if c.source == "misses":
        if not c.from_session:
            raise HTTPException(422, {"field": "custom.from_session", "reason": "which sitting's misses"})
        src = db.one("SELECT * FROM sessions WHERE id=? AND learner=?", c.from_session, learner)
        if src is None or not src["finished"]:
            raise HTTPException(409, "finish that test first")
        answers = db.load_answers(src)
        queue = [q["key"] for q in marked_questions(src) if "key" in q
                 and not scoring.is_correct(q, answers.get(q["id"]))]
        if not queue:
            raise HTTPException(409, {"reason": "no misses in that sitting"})
        qs = blueprint.custom([], 0, ["easy"], "ladder", "both", b, queue=queue[:c.count or 60])
        return [dict(q, id=f"c{i:02d}") for i, q in enumerate(qs, 1)], {}
    # traps (X16): each slot offers a trap you've fallen for; neutral ones mixed in
    queue = _trap_queue(learner, c)
    if not queue:
        raise HTTPException(409, {"reason": "no traps ready"})
    if c.count:
        queue = queue[:c.count]
    trap_cards: list[practice.Card] = []
    for template, norm in queue:
        card = None
        for _ in range(40):
            got = b.draw(template, practice.topic_of(template))
            if got is None:
                break
            b.keep(got)
            if _offers(got, norm):
                card = got
                break
        if card is None:
            # pool 'related': a sibling template with the same norm
            for sib in progress.related(norm) or ():
                if sib == template:
                    continue
                for _ in range(20):
                    got = b.draw(sib, practice.topic_of(sib))
                    if got is None:
                        break
                    b.keep(got)
                    if _offers(got, norm):
                        card = got
                        break
                if card:
                    break
        if card is not None:
            trap_cards.append((card, norm))
    norms = {n for _, n in queue}
    want = max(0, 6 - len(trap_cards))
    if c.neutral:
        want = max(want, round(len(trap_cards) * c.neutral / (1 - c.neutral)))
    neutral = _neutral(b, [t for t, _ in queue], norms, want)
    rank = {"easy": 0, "medium": 1, "hard": 2}
    cards = sorted([(cd, n) for cd, n in trap_cards] + [(cd, None) for cd in neutral],
                   key=lambda x: rank[x[0].feats["difficulty"]])
    if len(cards) < 6:
        raise HTTPException(409, {"reason": "not enough questions offer your traps yet"})
    qs = blueprint.stored([cd for cd, _ in cards], "c", sep="")
    return qs, {"trap_of": {q["id"]: n for q, (_, n) in zip(qs, cards) if n}}


def _new(learner: str, body: NewMock) -> str:
    """Build the sitting the body asks for and put it in its lobby."""
    if body.like and not body.twin_of:
        body.kind, body.twin_of = "twin", body.like
    kind = body.kind
    if kind is None:
        kind = "section" if body.full is not False else "module"
    opts = options(learner, body)
    training = opts["conditions"] == "training"
    cfg: dict = {**opts, "kind": kind, "lobby": True, "subject": "math"}
    if kind != "custom" and body.minutes is not None:
        raise HTTPException(422, {"field": "minutes", "reason": "own minutes are for a custom test"})
    if kind in ("section", "module") and body.m1:
        cfg["m1"] = body.m1
    if body.route and body.route != "adaptive":
        if kind not in ("section", "paper", "twin", "shared"):
            raise HTTPException(422, {"field": "route", "reason": "a route is for a full section"})
        cfg["route"] = body.route
    if kind == "section":
        form = M1_FORM[body.m1 or "standard"]
        m1 = fresh_module(learner, form, training)
        return _insert(learner, "mock", FRESH, {"module1": m1}, cfg)
    if kind == "module":
        module = body.module or "m1"
        cfg["module"] = module
        if body.trainer:
            if module != ("m1" if body.trainer == "route" else "m2u"):
                raise HTTPException(422, {"field": "trainer", "reason": "route trains module 1, gauntlet module 2 harder"})
            cfg["trainer"] = body.trainer
        if module != "m1" and body.m1:
            raise HTTPException(422, {"field": "m1", "reason": "a module 1 tier is for module 1"})
        form = M1_FORM[body.m1 or "standard"] if module == "m1" else MODULE_FORM[module]
        qs = fresh_module(learner, form, training)
        return _insert(learner, "module", FRESH, {"module1": qs}, cfg)
    if kind == "custom":
        c = body.custom or Custom()
        qs, extra = _custom(learner, c)
        if not qs:
            raise HTTPException(409, {"reason": "nothing to build from those choices"})
        cfg["custom"] = {**c.model_dump(), **extra}
        return _insert(learner, "custom", FRESH, {"module1": qs}, cfg)
    if kind == "twin":
        if not body.twin_of:
            raise HTTPException(422, {"field": "twin_of", "reason": "which sitting to twin"})
        src = _source_sitting(learner, body.twin_of)
        scfg = _cfg(src)
        cfg["twin_of"] = scfg.get("twin_of") or src["id"]
        cfg["twin_source"] = src["id"]
        for k in ("m1", "module", "paper", "trainer"):
            if scfg.get(k) and k not in cfg:
                cfg[k] = scfg[k]
        m1 = blueprint.twin(mock_module(src, 1), _twin_builder(learner))
        return _insert(learner, "mock" if src["kind"] == "mock" else "module",
                       f"P{scfg['paper']}" if scfg.get("paper") else FRESH, {"module1": m1}, cfg)
    if kind == "paper":
        n = body.paper or papers.ensure()
        if papers.paper(n) is None:
            raise HTTPException(404, f"no paper {n}")
        cfg["paper"] = n
        first = _first_of_paper(learner, n) if body.exact else None
        if body.exact:
            if first is None:
                raise HTTPException(409, "sit this paper once before sitting it again exactly")
            cfg["exact"] = True
            m1 = [dict(q) for q in mock_module(first, 1)]
        else:
            m1 = blueprint.twin_slots(papers.slots(n, "module1"), _twin_builder(learner), "m1")
        return _insert(learner, "mock", f"P{n}", {"module1": m1}, cfg)
    # shared (R18c): the set's module 1, exact or twins, and its module 2 for the same route
    if not body.shared:
        raise HTTPException(422, {"field": "shared", "reason": "the set code"})
    from . import sets
    got = sets.serve(body.shared, learner)
    if got.get("kind") != "test":
        raise HTTPException(422, {"field": "shared", "reason": "that code is not a test"})
    mods = got.get("modules") or [1] * len(got["items"])
    m1_pairs = [p for p, m in zip(got["items"], mods) if m == 1]
    m2_pairs = [p for p, m in zip(got["items"], mods) if m == 2]
    cfg.update({"share": got["code"], "exact_share": bool(got.get("exact")), "shared_route": got.get("route"),
                "shared_m2": m2_pairs})
    single = not m2_pairs and not got.get("route")
    sid = _insert(learner, "module" if single else "mock", FRESH,
                  {"module1": _pairs_questions(m1_pairs, "m1")}, cfg)
    sets.link(sid, got["code"])
    return sid


@router.post("/api/mock/new")
def new_mock(body: NewMock | None = None, x_learner: str | None = Header(default=None)) -> dict:
    """A sitting that has never existed before, in its lobby. The body picks
    the kind; the old {full, timed} still works for Today and Plan."""
    learner = writer_of(x_learner)
    sid = _new(learner, body or NewMock())
    row = session_or_404(sid)
    log.info("new %s %s for %s", kind_of(row), sid[:8], learner[:12])
    return payload(row)


# ------------------------------------------------------------------ the archive

@router.get("/api/mocks")
def list_mocks(learner: str = "", x_learner: str | None = Header(default=None)) -> dict:
    """What is on the old shelf, and what this learner last scored on each."""
    who = learner_of(x_learner) if x_learner else (learner if deps.LEARNER_OK.match(learner or "") else "")
    scores: dict[str, int] = {}
    if who:
        for r in db.rows("SELECT mock_id, result FROM sessions WHERE kind='mock' AND learner=?"
                         " AND finished IS NOT NULL ORDER BY finished", who):
            est = (_json(r["result"], {}) or {}).get("estimate") or {}
            if est:
                # the middle of the band, because a cassette spine fits a number
                scores[r["mock_id"]] = int(round((est["low"] + est["high"]) / 20) * 10)
    return {"mocks": [
        {"id": m["id"], "box": m["box"],
         "questions": len(m["module1"]) + len(m["module2_upper"]),
         "score": scores.get(m["id"])}
        for m in MOCKS.values()
    ]}


class MockStart(BaseModel):
    learner: str = Field(default="", max_length=120)


@router.post("/api/mock/{num}")
def start_mock(num: str, body: MockStart | None = None,
               x_learner: str | None = Header(default=None)) -> dict:
    """The archive's shelf section. X-Learner, or the body's learner for the
    archive page; both go through writer_of before anything is written."""
    if num not in MOCKS:
        raise HTTPException(404, f"no mock {num}")
    body_learner = writer_of(body.learner) if body and body.learner.strip() else None
    header_learner = writer_of(x_learner) if x_learner else None
    if body_learner and header_learner and body_learner != header_learner:
        raise HTTPException(403, "learner tokens disagree")
    learner = body_learner or header_learner or writer_of("anon:" + secrets.token_urlsafe(9))
    cfg = {**options(learner, Options()), "kind": "section", "lobby": True, "archive": num}
    sid = _insert(learner, "mock", num, None, cfg)
    log.info("mock %s started as %s", num, sid[:8])
    out = payload(session_or_404(sid))
    out["learner"] = learner
    return out


# ------------------------------------------------------------------ X13: the pressure check

def resolve_drill(learner: str, body: dict) -> dict:
    """R10's registry for POST /api/drill {pressure: sid}: the drill body of an
    untimed, end-mode round of twins of the sitting's lost questions."""
    sid = body.get("pressure")
    row = db.one("SELECT * FROM sessions WHERE id=?", sid) if isinstance(sid, str) else None
    if row is None:
        raise HTTPException(404, "no such session")
    if row["learner"] != learner:
        raise HTTPException(403, "that test belongs to another code")
    ok, why = pressure_eligible(row)
    if not ok:
        raise HTTPException(409, why)
    b = _twin_builder(learner)
    marked = {q["id"]: q for q in marked_questions(row)}
    ids, of = [], {}
    for qid in pressure_questions(row):
        q = marked[qid]
        card = blueprint.draw_matching(b, q["key"], q["difficulty"], "spr" if q["type"] == "spr" else None, tries=40)
        if card is None or card.seed == q["seed"]:
            continue
        b.keep(card)
        ids.append([card.key, card.seed])
        of[f"{card.key}:{card.seed}"] = qid
    if not ids:
        raise HTTPException(409, "no twins could be drawn")
    rest = {k: v for k, v in body.items() if k != "pressure"}
    return {**rest, "pool": "items", "ids": ids, "exact": True, "feedback": "end", "timing": "off",
            "repairs": "off", "source": "pressure", "parent": sid, "pressure_of": of}


@router.post("/api/session/{sid}/pressure")
def start_pressure(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    """The pressure check as a drill: fresh twins, no clock, nothing revealed
    until the end, inline (never listed; counted on the parent)."""
    learner = own(session_or_404(sid), x_learner, write=True)["learner"] or writer_of(x_learner)
    got = resolve_drill(learner, {"pressure": sid})
    new = secrets.token_urlsafe(16)
    drill.create(learner, new, list(dict.fromkeys(practice.topic_of(t) for t, _ in got["ids"])),
                 len(got["ids"]), None, False, "twin", items=got["ids"])
    row = session_or_404(new)
    cfg = {**_cfg(row), "feedback": "end", "timing": "off", "repairs": "off", "source": "pressure", "inline": True,
           "parent": sid, "pressure_of": got["pressure_of"]}
    db.run("UPDATE sessions SET cfg=? WHERE id=?", json.dumps(cfg), new)
    first = drill.next_question(session_or_404(new))
    return {**drill.state(session_or_404(new)), **first}


def on_drill_finish(row) -> dict | None:
    """Classify each original question by its twin (X13) and store the
    verdicts on the parent. Called from drill.finish when cfg.pressure_of is set."""
    cfg = _cfg(row)
    of = cfg.get("pressure_of")
    parent = db.one("SELECT * FROM sessions WHERE id=?", cfg.get("parent")) if of else None
    if parent is None:
        return None
    from . import estimate
    marked = {q["id"]: q for q in marked_questions(parent)}
    answers = db.load_answers(parent)
    qstate = _json(parent["qstate"], {}) or {}
    factor = FACTOR.get(timing_of(parent), 1.0)
    twins = {}
    for a in db.rows("SELECT * FROM attempts WHERE session=? ORDER BY id", row["id"]):
        twins.setdefault(f"{a['template']}:{a['seed']}", a)
    buckets = {k: [] for k in ("knowledge", "shaky", "speed", "pressure", "lucky", "confirmed")}
    for pair, qid in of.items():
        a = twins.get(pair)
        q = marked.get(qid)
        if a is None or q is None:
            continue
        given = answers.get(qid)
        right = given not in (None, "") and scoring.is_correct(q, given)
        budget = TIER_DEFAULT_S[q["difficulty"]] * 1000 * factor
        ms = a["ms"] if a["ms"] is not None else (a["sms"] or 0)
        if not right:
            if not a["correct"]:
                pick = papers._norm_of(q, given)
                buckets["knowledge" if pick and pick == (a["norm"] or progress.norm(a["reason"] or "")) else "shaky"].append(qid)
            else:
                buckets["speed" if ms > 2 * budget else "pressure"].append(qid)
        else:
            buckets["confirmed" if a["correct"] else "lucky"].append(qid)
    flips = buckets["pressure"]
    ceiling = estimate.rescore(parent["id"], right=flips) if flips else None
    m1 = {q["id"] for q in mock_module(parent, 1)} if parent["kind"] in ("mock", "module") else set()
    routes_up = False
    if parent["kind"] == "mock" and parent["route"] == "lower":
        m1q = mock_module(parent, 1)
        right = sum(scoring.is_correct(q, answers.get(q["id"])) for q in m1q) + sum(f in m1 for f in flips)
        routes_up = scoring.route_after(right, len(m1q)) == "upper"
    result = _json(parent["result"], {}) or {}
    result["pressure"] = {"subject": parent["subject"] or "math", "buckets": buckets,
                          "ceiling": ceiling, "routes_up": routes_up, "drill": row["id"]}
    db.run("UPDATE sessions SET result=? WHERE id=?", json.dumps(result), parent["id"])
    return result["pressure"]


def settle_pressure(learner: str) -> None:
    """X13 until drill.finish calls on_drill_finish (F5, §2.10): a finished
    pressure round whose parent has no verdicts yet is classified on read.
    /api/tests calls it; S6's results read can too."""
    for d in db.rows("SELECT d.* FROM sessions AS d JOIN sessions AS p ON p.id=json_extract(d.cfg,'$.parent')"
                     " WHERE d.learner=? AND d.kind='drill' AND d.finished IS NOT NULL"
                     " AND json_extract(d.cfg,'$.source')='pressure'"
                     " AND json_extract(p.result,'$.pressure') IS NULL", learner):
        on_drill_finish(d)


# ------------------------------------------------------------------ the sittings list's Tests fields

def _src(name: str) -> str:
    """A drill body's source label: Tests' own (fix, gate) once F5's
    drill.SOURCES lists them, else one it accepts today."""
    return name if name in drill.SOURCES else "mistakes"


def status_of(row) -> str:
    if row["finished"]:
        res = _json(row["result"], {}) or {}
        return "timed_out" if (res.get("summary") or {}).get("timed_out") else "completed"
    if not begun(row):
        return "not_begun"
    if row["paused_at"]:
        return "paused"
    if is_timed(row) and _left(row) <= 0:
        return "timed_out"
    return "in_progress"


def sitting_row(row) -> dict:
    """One sitting in the history shape (§3.4.5 History), for /api/tests and
    for S6's /api/history (deps.part('api_tests', 'sitting_row'))."""
    cfg = _cfg(row)
    res = _json(row["result"], {}) or {}
    answers = db.load_answers(row)
    qstate = _json(row["qstate"], {}) or {}
    mods = res.get("modules")
    if mods is None and row["finished"]:
        mods = []
        for n, qs in enumerate(_modules(row), 1):
            mods.append({"subject": row["subject"] or "math", "n": n,
                         "right": sum(scoring.is_correct(q, answers.get(q["id"])) for q in qs), "asked": len(qs),
                         "missed": [i for i, q in enumerate(qs, 1) if answers.get(q["id"]) not in (None, "")
                                    and not scoring.is_correct(q, answers.get(q["id"]))],
                         "blank": [i for i, q in enumerate(qs, 1) if answers.get(q["id"]) in (None, "")]})
    marked = marked_questions(row) if row["kind"] in TESTS else []
    retake = None
    if cfg.get("paper"):
        # rowid breaks a tie between sittings started in the same second
        k = db.one("SELECT COUNT(*) AS n FROM sessions WHERE learner=? AND mock_id=? AND abandoned IS NULL"
                   " AND (started<? OR (started=? AND rowid<=(SELECT rowid FROM sessions WHERE id=?)))",
                   row["learner"], f"P{cfg['paper']}", row["started"], row["started"], row["id"])["n"]
        retake = k if k >= 2 else None
    est = res.get("estimate") or None
    out = {"id": row["id"], "kind": kind_of(row), "mode": row["kind"], "kind_label": kind_label(row),
           "section": section_label(row), "subject": row["subject"] or "math",
           "number": row["number"], "status": status_of(row), "started": row["started"],
           "finished": row["finished"], "route": row["route"],
           "fixed_route": cfg.get("route") in ("upper", "lower"),
           "capped": bool(est and est.get("capped")), "timing": timing_of(row),
           "extended": timing_of(row) in ("x1.5", "x2"), "scored": res.get("scored"),
           "pauses": row["pauses"] or 0, "conditions": cfg.get("conditions", "test_day"),
           "ranked": bool(row["ranked"]) if row["finished"] else live_rank(row)["ranked"],
           "unranked_why": row["unranked_why"] if row["finished"] else live_rank(row)["why"],
           "modules": mods, "estimate": est, "right": res.get("right"), "asked": res.get("asked"),
           "ms": sum((qstate.get(q["id"]) or {}).get("ms") or 0 for q in marked),
           "mean_weight": round(statistics.mean(scoring.WEIGHT[q["difficulty"]] for q in marked), 3) if marked else None,
           "twin_of": cfg.get("twin_of"), "paper": cfg.get("paper"), "retake": retake,
           "exact": bool(cfg.get("exact")), "shared_from": row["shared_from"], "note": row["note"],
           "trainer": cfg.get("trainer"), "contest": row["contest"],
           "offline_ms": (qstate.get("_session") or {}).get("offline_ms"),
           "gate": res.get("gate"), "pass2": res.get("pass2"), "pressure": res.get("pressure")}
    if not row["finished"]:
        ids = {q["id"] for q in questions_of(row)}
        out.update({"module": row["module"] or 1, "answered": sum(1 for k in answers if k in ids),
                    "left_seconds": remaining(row) if is_timed(row) else None,
                    "href": f"/test/?s={row['id']}"})
    return out


def open_sittings(learner: str) -> list:
    return db.rows("SELECT * FROM sessions WHERE learner=? AND finished IS NULL AND abandoned IS NULL"
                   " AND kind IN ('mock','module','custom','diagnostic') ORDER BY started DESC", learner)


def finished_sittings(learner: str, limit: int = 200) -> list:
    return db.rows("SELECT * FROM sessions WHERE learner=? AND finished IS NOT NULL AND abandoned IS NULL"
                   " AND kind IN ('mock','module','custom','diagnostic') ORDER BY finished DESC LIMIT ?",
                   learner, limit)


# ------------------------------------------------------------------ /api/tests pieces

def _mid(res: dict) -> float | None:
    e = res.get("estimate") or {}
    return (e["low"] + e["high"]) / 2 if e.get("low") is not None else None


def kinds_rows(learner: str) -> list[dict]:
    """T4: each kind's use by everyone, and yours."""
    def key(row) -> str | None:
        cfg = _cfg(row)
        if row["kind"] == "mock":
            return "section"
        if row["kind"] == "module":
            if cfg.get("trainer") == "route":
                return "trainer"
            return {"m2u": "module2u", "m2l": "module2l"}.get(cfg.get("module"), "module1")
        if row["kind"] == "custom":
            return "traps" if (cfg.get("custom") or {}).get("source") == "traps" else "custom"
        return "diagnostic" if row["kind"] == "diagnostic" else None
    ids = ("section", "module1", "module2u", "module2l", "custom", "diagnostic", "trainer", "traps")
    everyone: Counter = Counter()
    ranked: dict[str, dict[str, float]] = defaultdict(dict)
    for r in db.rows(f"SELECT * FROM sessions WHERE finished IS NOT NULL AND abandoned IS NULL AND contest IS NULL"
                     f" AND kind IN ('mock','module','custom','diagnostic') AND {db.NOT_SAMPLE}"):
        k = key(r)
        if k:
            everyone[k] += 1
            m = _mid(_json(r["result"], {}) or {})
            if m is not None and r["ranked"] and r["learner"] not in ranked[k]:
                ranked[k][r["learner"]] = m
    mine: dict[str, list] = defaultdict(list)
    for r in reversed(finished_sittings(learner)):
        k = key(r)
        if k:
            mine[k].append(r)
    out = []
    for k in ids:
        rs = mine.get(k, [])
        mids = [m for m in (_mid(_json(r["result"], {}) or {}) for r in rs) if m is not None]
        pct = None
        peers = list(ranked[k].values())
        if mids and len(peers) >= papers.CROWD_N:
            pct = round(100 * sum(p <= mids[-1] for p in peers) / len(peers))
        row = {"id": k, "everyone": everyone.get(k, 0), "yours": len(rs),
               "last": mids[-1] if mids else (None if not rs else
                       {"right": (_json(rs[-1]["result"], {}) or {}).get("right"),
                        "asked": (_json(rs[-1]["result"], {}) or {}).get("asked")}),
               "best": max(mids) if mids else None, "percentile": pct}
        if k == "trainer":
            streak = best = 0
            for r in rs:
                up = (_json(r["result"], {}) or {}).get("gate", {}).get("margin", -1) >= 0 and \
                     _cfg(r).get("conditions", "test_day") == "test_day" and timing_of(r) == "official"
                streak = streak + 1 if up else 0
                best = max(best, streak)
            row.update({"streak": streak, "best_streak": best,
                        "pips": [(_json(r["result"], {}) or {}).get("gate", {}).get("margin", -1) >= 0 for r in rs[-5:]]})
        if k == "traps":
            row["ready"] = _traps_ready(learner)
        if k == "module2u":
            # X14's gauntlet: 18 of 22 on the harder module 2, shown from a 620 target or 2 upper routes
            g = [r for r in rs if _cfg(r).get("trainer") == "gauntlet"]
            lr = db.one("SELECT target FROM learners WHERE id=?", learner)
            ups = sum(r["route"] == "upper" for r in finished_sittings(learner, 50) if r["kind"] == "mock")
            row["gauntlet"] = {"shown": bool((lr and (lr["target"] or 0) >= 620) or ups >= 2), "goal": 18,
                               "pips": [((_json(r["result"], {}) or {}).get("right") or 0) >= 18 for r in g[-5:]]}
        out.append(row)
    return out


def _traps_ready(learner: str) -> int:
    since = (_utc() - dt.timedelta(days=60)).isoformat()
    return db.one("SELECT COUNT(*) AS n FROM traps WHERE learner=? AND norm IS NOT NULL AND norm!=''"
                  " AND (closed IS NULL OR closed>=?)", learner, since)["n"]


def gate_summary(learner: str) -> dict:
    """X14's T1 row: routed up k of n, the last 6 margins, and the lower-route warning."""
    sections = [r for r in finished_sittings(learner, 50) if r["kind"] == "mock"]
    margins = [(_json(r["result"], {}) or {}).get("gate", {}).get("margin") for r in sections]
    margins = [m for m in margins if m is not None]
    lower_recent = sum(r["route"] == "lower" for r in sections[:3]) >= 2
    protect = None
    if lower_recent:
        templates = []
        for r in sections[:3]:
            g = (_json(r["result"], {}) or {}).get("gate") or {}
            m1 = mock_module(r, 1)
            templates += [m1[i - 1]["key"] for i in g.get("cheap_misses", []) if i - 1 < len(m1)]
        protect = {"templates": list(dict.fromkeys(templates))[:40], "count": 12, "timing": "pace",
                   "source": _src("gate")} if templates else None
    return {"up": sum(r["route"] == "upper" for r in sections), "sections": len(sections),
            "margins": list(reversed(margins[:6])), "lower_recent": lower_recent, "protect": protect}


def _up_to(row, qids: list[str], got: dict | None, base: dict | None) -> int | None:
    """X15's "up to +N with the harder module 2": only when these flips carry
    a lower-routed module 1 over the line, priced at the uncapped band."""
    if row["route"] != "lower" or not got or not base or not got.get("capped"):
        return None
    g = (_json(row["result"], {}) or {}).get("gate") or {}
    m1 = {q["id"] for q in mock_module(row, 1)}
    if g.get("right", 0) + sum(q in m1 for q in qids) < g.get("needed", 10 ** 6):
        return None
    centre = min(800 - scoring.MOCK_HALF_BAND, got["low"] + scoring.MOCK_HALF_BAND)
    return int(round((centre - base["mid"]) / 10) * 10)


def levers(learner: str) -> dict:
    """X15: where the points went over the last 3 sections, priced by
    re-marking them with that cause's positions right."""
    from . import estimate
    sections = [r for r in finished_sittings(learner, 30)
                if r["kind"] == "mock" and _mid(_json(r["result"], {}) or {}) is not None][:3]
    empty = {"subject": "math", "causes": [], "route": None, "skills": [], "both": None, "sittings": len(sections)}
    if not sections:
        return empty
    per_cause: dict[str, dict] = defaultdict(lambda: {"n": 0, "pts": [], "up": [], "templates": []})
    both_flips: dict[str, list[str]] = {}
    for r in sections:
        c = progress.causes(learner, session=r["id"]).get("per_q", {})
        base = estimate.rescore(r["id"])
        if not base:
            continue
        keys = {q["id"]: q.get("key") for q in marked_questions(r)}
        groups: dict[str, list[str]] = defaultdict(list)
        for qid, v in c.items():
            groups[v["cause"]].append(qid)
        for cause, qids in groups.items():
            got = estimate.rescore(r["id"], right=qids)
            d = per_cause[cause]
            d["n"] += len(qids)
            d["pts"].append(got["mid"] - base["mid"])
            d["up"].append(_up_to(r, qids, got, base))
            d["templates"] += [keys[q] for q in qids if keys.get(q)]
        both_flips[r["id"]] = groups.get("trap", []) + groups.get("slip", [])
    causes = []
    for cause, d in sorted(per_cause.items(), key=lambda kv: -sum(kv[1]["pts"])):
        pts = int(round(sum(d["pts"]) / len(sections) / 10) * 10)
        ups = [u for u in d["up"] if u is not None]
        templates = list(dict.fromkeys(d["templates"]))[:120]
        action = {"trap": {"label": f"Fix {d['n']}", "body": {"pool": "redo", "templates": templates,
                                                               "source": _src("fix")}},
                  "clock": {"label": "Pacing practice", "preset": "pacing"},
                  "slip": {"label": f"See your {d['n']} slips", "also": "Careful set · 8",
                           "body": {"templates": templates, "count": 8, "source": _src("fix")}},
                  "entry": {"label": "Grid-in entry drill · 5", "body": {"formats": ["spr"], "count": 5}},
                  "gap": {"label": "Learn it", "templates": templates[:1]},
                  "changed": {"label": "See the changes", "href": f"/results/report/?id={sections[0]['id']}&filter=changed"},
                  "misread": {"label": "Careful set · 8", "body": {"templates": templates, "count": 8}}}.get(cause, {})
        causes.append({"cause": cause, "n": d["n"], "pts": pts, "route_pts": max(ups) if ups else None,
                       "action": action})
    route = None
    for r in sections:
        g = (_json(r["result"], {}) or {}).get("gate") or {}
        if r["route"] == "lower" and g and -2 <= g.get("margin", -99) < 0:
            m1 = mock_module(r, 1)
            flips = [m1[i - 1]["id"] for i in g.get("cheap_misses", [])][:-g["margin"]]
            base = estimate.rescore(r["id"])
            up = _up_to(r, flips, estimate.rescore(r["id"], right=flips), base) if flips and base else None
            route = {"session": r["id"], "day": r["finished"][:10], "short_by": -g["margin"],
                     "cap": scoring.LOWER_ROUTE_CEILING, "pts": up}
            break
    gains = estimate.gains(learner) or {}
    skills = (gains.get("skills") or gains.get("rows") or [])[:3] if isinstance(gains, dict) else []
    both = None
    if any(both_flips.values()):
        pts = [estimate.rescore(sid, right=q)["mid"] - estimate.rescore(sid)["mid"] for sid, q in both_flips.items()]
        both = {"pts": int(round(statistics.mean(pts) / 10) * 10)}
    return {"subject": "math", "causes": causes, "route": route, "skills": skills, "both": both,
            "sittings": len(sections)}


def habits(learner: str, last: int | None = None) -> dict:
    """X17: how this learner takes tests, from qstate across finished, timed,
    non-abandoned test sittings. Every row shows (decision 4)."""
    rows = [r for r in finished_sittings(learner, 60) if is_timed(r)]
    if last:
        rows = rows[:last]
    with_state = [r for r in rows if len(_json(r["qstate"], {}) or {}) > 1]
    out = {"subject": "math", "n": len(rows), "from_n": len(with_state), "rows": []}
    if len(rows) < 2:
        return out
    end_r = end_n = early_r = early_n = 0
    zero, margins, blanks, mods = 0, [], 0, 0
    marked = back = changed_m = gained = 0
    p2a = p2r = 0
    guess = {"sure": [0, 0], "unsure": [0, 0], "guess": [0, 0]}
    calc_with = [0, 0]
    calc_without = [0, 0]
    ref = ref_ms = 0
    away_n = 0
    struck_right = 0
    took = fired = 0
    series: dict[str, list] = defaultdict(list)
    for r in reversed(rows):
        res = _json(r["result"], {}) or {}
        answers = db.load_answers(r)
        qs = _json(r["qstate"], {}) or {}
        sitting_blanks = 0
        for qs_mod in _modules(r):
            mods += 1
            n = len(qs_mod)
            for i, q in enumerate(qs_mod, 1):
                ok = scoring.is_correct(q, answers.get(q["id"]))
                st = qs.get(q["id"]) or {}
                if i > n - 6:
                    end_n += 1
                    end_r += ok
                else:
                    early_n += 1
                    early_r += ok
                if answers.get(q["id"]) in (None, ""):
                    blanks += 1
                    sitting_blanks += 1
                if st.get("marked"):
                    marked += 1
                    if (st.get("changes") or 0) or st.get("pass") == 2:
                        back += 1
                    if st.get("changes"):
                        changed_m += 1
                        first = st.get("first")
                        if first is not None and ok and not scoring.is_correct(q, first):
                            gained += 1
                if st.get("pass") == 2:
                    p2a += 1
                    p2r += ok
                if st.get("conf") in guess:
                    guess[st["conf"]][0] += 1
                    guess[st["conf"]][1] += ok
                c = calc_with if (st.get("calc") or {}).get("exprs") else calc_without
                c[0] += 1
                c[1] += ok
                ref += st.get("ref_n") or 0
                ref_ms += st.get("ref_ms") or 0
                if q.get("type") == "mcq":
                    try:
                        k = "ABCD".index(q["answer"])
                    except (ValueError, KeyError):
                        k = None
                    if k is not None and k in (st.get("struck_ever") or []):
                        struck_right += 1
        summ = res.get("summary") or {}
        left = summ.get("left_s")
        if left is not None:
            margins.append(left)
            zero += left <= 0
        m1s = (_json(r["module1"], {}) or {}).get("summary") or {}
        if m1s.get("left_s") is not None:
            margins.append(m1s["left_s"])
            zero += m1s["left_s"] <= 0
        away_n += (res.get("away") or {}).get("ms", 0) > 0
        for nd in (qs.get("_session") or {}).get("nudges") or []:
            if nd.get("kind") == "sink":
                fired += 1
                took += bool(nd.get("took"))
        series["blanks"].append(sitting_blanks)
        series["end"].append(res.get("right"))
    ch = progress.causes(learner, days=365).get("changes", {})
    q_worth = 12
    rows_out = []

    def add(id_, verdict, title, evidence, points=0, action=None, why=""):
        rows_out.append({"id": id_, "verdict": verdict, "title": title, "evidence": evidence,
                         "series": series.get(id_, []), "points": points, "action": action, "why": why})
    end_pct = round(100 * end_r / end_n) if end_n else 0
    early_pct = round(100 * early_r / early_n) if early_n else 0
    add("end", "costs" if early_pct - end_pct >= 20 else "good", "End of module",
        f"Q17–22: {end_pct}% right · Q1–16: {early_pct}%", action={"label": "Hard-end practice · 10 hard at 95 s",
        "body": {"tiers": ["hard"], "count": 10, "timing": "pace"}}, why="The last six questions of each module.")
    avg = round(statistics.mean(margins)) if margins else 0
    add("finish", "costs" if zero else "good", "Finish margin",
        f"{zero} of {len(margins)} modules ran to 0:00" if zero else f"You kept {mmss(avg * 1000)} on average to check",
        action={"label": "Pacing practice", "preset": "pacing"}, why="Time left when each module was handed in.")
    add("pace", "info", "Pace by position", f"{len(margins)} modules timed", why="Against X3's budgets.")
    per_mod = blanks / mods if mods else 0
    add("blanks", "costs" if blanks else "good", "Blanks",
        f"{per_mod:.1f} a module · ≈ −{int(round(blanks * 0.25 * q_worth / max(1, len(rows)) / 10) * 10)} against guessing",
        points=-int(round(blanks * 0.25 * q_worth / max(1, len(rows)))), why="A guess can't cost you.")
    rw, wr = ch.get("right_to_wrong", 0), ch.get("wrong_to_right", 0)
    add("changes", "costs" if rw > wr else "good", "Answer changes",
        f"{rw} right→wrong, {wr} wrong→right · ≈ {'−' if rw > wr else '+'}{abs(rw - wr) * q_worth}",
        points=(wr - rw) * q_worth, action={"label": "See the changes"}, why="First answer against the final one.")
    add("marks", "good" if gained else "info", "Mark for review",
        f"Marked {marked} · went back to {back} · changed {changed_m} · gained {gained}")
    add("pass2", "good" if p2r else "info", "Second pass", f"Pass 2: {p2a} answered, {p2r} right")
    pr = [predicted(r) for r in rows]
    spotted = sum(p["spotted"] for p in pr)
    silent = sum(p["silent"] for p in pr)
    add("calibration", "costs" if silent > spotted else "good", "Calibration",
        f"Spotted {spotted} of {spotted + silent} misses")
    if any(v[0] for v in guess.values()):
        add("confidence", "info", "Confidence", " · ".join(
            f"{k.title()} {round(100 * v[1] / v[0]) if v[0] else 0}%" for k, v in guess.items()))
    total_q = calc_with[0] + calc_without[0]
    add("calculator", "info", "Calculator",
        f"Open on {round(100 * calc_with[0] / total_q) if total_q else 0}% of questions · right "
        f"{round(100 * calc_with[1] / calc_with[0]) if calc_with[0] else 0}% with it, "
        f"{round(100 * calc_without[1] / calc_without[0]) if calc_without[0] else 0}% without")
    add("reference", "info", "Reference", f"Opened {round(ref / mods, 1) if mods else 0} times a module ({mmss(ref_ms / max(1, mods))})")
    add("away", "costs" if away_n else "good", "Away", f"Left the window in {away_n} of {len(rows)} tests")
    press = [(_json(r["result"], {}) or {}).get("pressure") for r in rows]
    press = [p for p in press if p]
    if press:
        add("pressure", "costs", "Pressure", f"Pressure losses {statistics.mean(len(p['buckets']['pressure']) for p in press):.0f} a test")
    add("eliminations", "costs" if struck_right else "good", "Eliminations", f"Crossed out the right answer {struck_right} times")
    if fired:
        add("nudges", "info", "Nudges", f"Took {took} of {fired} time-sink nudges")
    rows_out.sort(key=lambda r: (r["verdict"] != "costs", r["points"]))
    out["rows"] = rows_out
    return out


def types_met(learner: str) -> dict:
    """{tests, practice, never, total}: F4's progress.types_met when present."""
    fn = deps.part("progress", "types_met")
    if fn:
        return fn(learner)
    total = sum(len(v) for v in practice.catalogue()["by_topic"].values())
    tests = _met_templates(learner)
    ever = {r["template"] for r in db.rows("SELECT DISTINCT template FROM attempts WHERE learner=?", learner)}
    return {"tests": len(tests), "practice": len(ever - tests), "never": total - len(ever | tests), "total": total}


def cycle(learner: str) -> dict | None:
    """X16: Test -> Fix -> Prove for the latest scored sitting with 3 or more
    misses in the last 21 days."""
    since = (_utc() - dt.timedelta(days=21)).isoformat()
    for r in finished_sittings(learner, 20):
        if r["finished"] < since:
            break
        res = _json(r["result"], {}) or {}
        if res.get("estimate") is None:
            continue
        misses = sum(len(m.get("missed", [])) + len(m.get("blank", [])) for m in res.get("modules", []))
        if misses < 3:
            continue
        traps = db.rows("SELECT * FROM traps WHERE learner=? AND session=?", learner, r["id"])
        closed = [t["closed"] for t in traps if t["closed"]]
        prove_due = None
        if traps and len(closed) == len(traps):
            prove_due = (dt.date.fromisoformat(max(closed)[:10]) + dt.timedelta(days=3)).isoformat()
        twin_from = (dt.date.fromisoformat(r["finished"][:10]) + dt.timedelta(days=7)).isoformat()
        return {"session": r["id"], "label": kind_label(r), "number": r["number"], "misses": misses,
                "fix": {"body": {"from_session": r["id"], "scope": "misses", "source": _src("fix")},
                        "open": len(traps) - len(closed), "done": bool(traps) and len(closed) == len(traps)},
                "prove": {"due": prove_due, "body": {"kind": "custom", "custom": {"source": "traps",
                                                                                "from_session": r["id"]}}},
                "twin": {"from": twin_from, "body": {"kind": "twin", "twin_of": r["id"]}}}
    return None


def up_next(learner: str, live: list, done: list, gate: dict, lever: dict, paper_n: int) -> dict:
    """§3.1 item 11's order: resume, pressure, prove, plan, new learner,
    Season Final / Road-to, trap test, route-up trainer, this week's paper,
    then the biggest cause."""
    if live:
        return {"kind": "resume", "reason": "resume", "session": live[0]["id"]}
    day_ago = (_utc() - dt.timedelta(hours=24)).isoformat()
    for r in done[:5]:
        if r["finished"] >= day_ago and pressure_eligible(r)[0]:
            return {"kind": "pressure", "reason": "pressure", "session": r["id"]}
    cyc = cycle(learner)
    if cyc and cyc["prove"]["due"] and cyc["prove"]["due"] <= dt.date.today().isoformat():
        return {"kind": "traps", "reason": "prove", "session": cyc["session"], "body": cyc["prove"]["body"]}
    plan = db.one("SELECT d.test FROM plan_days AS d JOIN learners AS l ON l.plan=d.plan WHERE l.id=? AND d.day=?"
                  " AND d.test IS NOT NULL", learner, dt.date.today().isoformat())
    if plan and plan["test"]:
        return {"kind": "module" if "module" in str(plan["test"]) else "section", "reason": "plan", "preset": "like_test_day"}
    if not done:
        return {"kind": "diagnostic", "reason": "new"}
    stamp = now()
    final = db.one("SELECT id FROM contests WHERE kind='final' AND opens<=? AND closes>?", stamp, stamp)
    if final:
        return {"kind": "contest", "reason": "final", "contest": final["id"]}
    road = db.one("SELECT n FROM papers WHERE source LIKE 'final-%' ORDER BY n DESC LIMIT 1")
    exam = db.one("SELECT exam_date FROM learners WHERE id=?", learner)
    if road and exam and exam["exam_date"] and exam["exam_date"] >= dt.date.today().isoformat() \
            and not papers.sat_by(learner, road["n"]):
        return {"kind": "paper", "reason": "paper", "paper": road["n"]}
    week_ago = (_utc() - dt.timedelta(days=7)).isoformat()
    due = db.one("SELECT COUNT(*) AS n FROM traps WHERE learner=? AND closed IS NOT NULL AND due<=?",
                 learner, dt.date.today().isoformat())["n"]
    open_ = db.one("SELECT COUNT(*) AS n FROM traps WHERE learner=? AND closed IS NULL", learner)["n"]
    recent_trap = any(_cfg(r).get("custom", {}).get("source") == "traps" and r["finished"] >= week_ago for r in done)
    if (due >= 5 or open_ >= 8) and not recent_trap:
        return {"kind": "traps", "reason": "traps"}
    if gate["lower_recent"]:
        return {"kind": "trainer", "reason": "trainer"}
    if not papers.sat_by(learner, paper_n):
        return {"kind": "paper", "reason": "paper", "paper": paper_n}
    if lever.get("causes") and lever["causes"][0]["cause"] == "clock":
        return {"kind": "module", "reason": "default", "preset": "pacing"}
    return {"kind": "section", "reason": "default"}


def recommended(learner: str, done: list, gate: dict) -> dict:
    """X1's orange preset chip and its reason line."""
    sections = [r for r in done if r["kind"] == "mock"][:2]
    blanks = [sum(len(m.get("blank", [])) for m in (_json(r["result"], {}) or {}).get("modules", [])) for r in sections]
    if len(sections) == 2 and all(b >= 3 for b in blanks):
        return {"preset": "pacing", "reason": f"Your last 2 sections left {min(blanks)} blanks each at time-up"}
    for r in sections:
        g = (_json(r["result"], {}) or {}).get("gate") or {}
        if r["route"] == "lower" and -2 <= g.get("margin", -99) < 0:
            return {"preset": "routing", "reason": f"{r['finished'][:10]} missed the harder module 2 by {-g['margin']}"}
    return {"preset": "like_test_day", "reason": None}


@router.get("/api/tests")
def tests_overview(x_learner: str | None = Header(default=None)) -> dict:
    """Everything /tests/ shows, in one round trip. Builds this week's paper
    if it is missing."""
    from . import estimate, prefs
    learner = learner_of(x_learner)
    paper_n = papers.ensure()
    settle_pressure(learner)
    live = open_sittings(learner)
    done = finished_sittings(learner)
    est = estimate.estimate(learner)
    latest, previous = est.get("latest"), est.get("previous")
    lr = db.one("SELECT target, exam_date FROM learners WHERE id=?", learner)
    exam = None
    if lr and lr["exam_date"]:
        exam = {"date": lr["exam_date"], "days": (dt.date.fromisoformat(lr["exam_date"]) - dt.date.today()).days}
    gate = gate_summary(learner)
    lever = levers(learner)
    twin = None
    for r in done:
        if r["kind"] in ("mock", "module") and (_json(r["result"], {}) or {}).get("scored"):
            twin = {"source": r["id"], "label": f"{kind_label(r)} #{r['number']}" if r["number"] else kind_label(r)}
            break
    p = prefs.get(learner) if not db.is_sample(learner) else dict(prefs.DEFAULTS)
    ranked_n = sum(1 for r in done if r["ranked"])
    return {
        "estimate": {**est, "delta": est.get("trend", {}).get("delta"),
                     "headline_parts": {"subject": "Math", "low": latest["low"] if latest else None,
                                        "high": latest["high"] if latest else None},
                     "counted": {**est.get("counted", {}), "ranked": ranked_n}},
        "target": lr["target"] if lr else None, "exam": exam,
        "up_next": up_next(learner, live, done, gate, lever, paper_n),
        "recommended": recommended(learner, done, gate),
        "in_progress": [sitting_row(r) for r in live],
        "kinds": kinds_rows(learner),
        "papers": papers.listing(learner),
        "twin": twin,
        "prefs": {k: v for k, v in p.items() if k.startswith("test_")},
        "levers": lever, "total": estimate.total(learner), "projection": estimate.projection(learner),
        "growth": estimate.growth(learner), "calibration": estimate.calibration(learner),
        "habits": habits(learner), "cycle": cycle(learner), "gate": gate, "types_met": types_met(learner),
    }
