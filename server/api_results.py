"""Results and the score report (spec/rebuild-v2.md §3.5, R26, R35, and
spec/v2-upgrades/reports.md SR1-SR25), server side.

One sitting's report is GET /api/session/{sid}/results: the stored result
plus everything the report page shows, computed on read from rows that
already exist (sessions, attempts, traps, flags, saved, notes, reports,
tries). Nothing here stores a copy of a fact another module owns: the band
and the points come from estimate.py, mastery, causes and recovery from
progress.py, the crowd from drill.levels() and ratings.py.

Every review item goes out through hold_back() while a second look is
offered (SR3), for every viewer, so no payload names an unseen miss's key.

The writes a report makes: POST /api/session/{sid}/whatif (writes nothing),
/second, /seen, /second/state, /why (and /api/drill/{sid}/why), /note. The
reads: /compare, /briefing, /api/history (R26, R24), /api/stats and
/api/skill/{topic}, the last three also for a progress link (?share=).

init() keeps the live sample report (SR24): a finished section for the
learner `sample:report`, id `sample-section`, readable by anyone, writable
by no one.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import re
import statistics
from collections import Counter, defaultdict

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field

from . import blueprint, db, deps, drill, estimate, practice, progress, scoring
from .api_tests import DRILLS, marked_questions, mock_module, public
from .deps import learner_of, session_or_404, tz_of, writer_of

router = APIRouter()

PACE_MS = round(blueprint.MODULE_SECONDS * 1000 / blueprint.MODULE_SIZE)     # R34: 95,455 ms
MODULE_MS = blueprint.MODULE_SECONDS * 1000
TESTS = tuple(dict.fromkeys(deps.TEST_KINDS + ("twin", "shared")))
SECTIONS = estimate.SECTION_KINDS
PRACTICE = ("drill", "practice")
HIDDEN_KINDS = ("spot",)                    # never a sitting (R36)
KIND_NAME = {"mock": "Section", "section": "Section", "paper": "Paper", "twin": "Twin",
             "shared": "Shared test", "module": "Module", "diagnostic": "Diagnostic",
             "custom": "Custom test", "drill": "Practice", "practice": "Mixed practice",
             "challenge": "Daily challenge", "words": "Words run", "spot": "Spot the trap"}
SOURCE_NAME = {"map": "Map", "coach": "Coach", "mistakes": "Mistakes", "saved": "Saved",
               "fix": "Fix these", "plan": "Plan", "today": "Today", "review": "Review",
               "quick": "Quick questions", "learn": "Learn it", "habit": "Habit drill",
               "shared": "Shared set", "worksheet": "Worksheet", "rematch": "Rematch"}
CORRECT, INCORRECT, UNANSWERED = ("correct",), ("incorrect", "mixed"), ("blank", "skipped")
COUNTED = CORRECT + INCORRECT + UNANSWERED
MISSES = INCORRECT + UNANSWERED
# SR3: every field derived from an unseen miss's key
HELD = ("answer", "reasons", "rationale", "mistake", "accepted", "steps", "step_of", "diverge",
        "wrong_step", "option_steps", "diagnosis", "spr_reasons", "struck", "marks")
SECOND_DAYS = 3
RUSHED_MS, LONG_MS = 30_000, 190_000        # §1.9: under 0:30 and wrong; over 3:10
TIER_ORDER = ("easy", "medium", "hard")
FORMAT_NAME = {"mcq": "Multiple choice", "spr": "Grid-in"}
MAX_IDS = 120


# ------------------------------------------------------------------ small readers

def _json(text, default):
    try:
        v = json.loads(text) if text else default
    except (TypeError, ValueError):
        return default
    return default if v is None else v


def _col(row, name: str, default=None):
    return row[name] if name in row.keys() else default


def _cfg(row) -> dict:
    v = _json(_col(row, "cfg"), {})
    return v if isinstance(v, dict) else {}


def _qstate(row) -> dict:
    v = _json(_col(row, "qstate"), {})
    return v if isinstance(v, dict) else {}


def _result(row) -> dict:
    v = _json(_col(row, "result"), {})
    return v if isinstance(v, dict) else {}


def _subject(row) -> str:
    return _col(row, "subject") or _cfg(row).get("subject") or "math"


def _inline(kind: str, cfg: dict) -> bool:
    """R24: sets that are never a sitting (twins, try-one, word examples,
    the review pane, spot)."""
    return kind in HIDDEN_KINDS or bool(cfg.get("inline")) or cfg.get("source") in drill.INLINE


def _age_days(at: str | None) -> float:
    if not at:
        return 0.0
    return (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(at)).total_seconds() / 86400


def _band(result: dict) -> dict | None:
    e = result.get("estimate")
    return e if isinstance(e, dict) and e.get("low") is not None and e.get("high") is not None else None


def _mid(band: dict | None) -> float | None:
    return (band["low"] + band["high"]) / 2 if band else None


def _round5(x: float) -> int:
    return int(math.floor(x / 5 + 0.5) * 5)


def worth(pts: float | None) -> dict | None:
    """SR1: a miss's points, printed to the nearest 5 or 'under 5'."""
    if pts is None:
        return None
    return {"pts": round(pts, 2), "printed": _round5(pts) if pts >= 2.5 else None,
            "under5": 0 < pts < 2.5}


def viewer(x_learner: str | None) -> str | None:
    """Who is reading: None without a header (a shared link opened anywhere)."""
    return learner_of(x_learner) if x_learner and x_learner.strip() else None


def share_learner(token: str) -> str:
    """R18(a): a progress link (links kind 'progress', S1) resolves to its
    learner, read-only; a bad or revoked token is 404."""
    r = db.one("SELECT learner FROM links WHERE token=? AND kind='progress' AND revoked IS NULL",
               (token or "").strip())
    if not r or not r["learner"]:
        raise HTTPException(404, "that progress link does not work any more")
    return r["learner"]


def _reader(x_learner: str | None, share: str | None) -> tuple[str, bool]:
    if share:
        return share_learner(share), True
    return learner_of(x_learner), False


def _owned(sid: str, x_learner: str | None):
    """A finished sitting of this learner's, for the report's writes: 403 for
    anyone else (and for the sample), 409 until it is finished."""
    learner = writer_of(x_learner)
    row = session_or_404(sid)
    if row["learner"] != learner:
        raise HTTPException(403, "that sitting belongs to someone else")
    if not row["finished"]:
        raise HTTPException(409, {"need": "finish", "kind": row["kind"]})
    return row, learner


# ------------------------------------------------------------------ numbering

def seqs(learner: str | None) -> dict[str, int]:
    """Each finished sitting's number among the learner's sittings of its kind,
    by finished then rowid ("Section #7"). Inline sets and empty sets have none."""
    if not learner:
        return {}
    out, count = {}, Counter()
    for r in db.rows("SELECT id, kind, cfg, result FROM sessions WHERE learner=? AND finished IS NOT NULL"
                     " AND abandoned IS NULL ORDER BY finished, rowid", learner):
        cfg = _json(r["cfg"], {})
        if not isinstance(cfg, dict) or _inline(r["kind"], cfg):
            continue
        if r["kind"] in PRACTICE and (_json(r["result"], {}) or {}).get("asked") == 0:
            continue
        count[r["kind"]] += 1
        out[r["id"]] = count[r["kind"]]
    return out


def kind_name(row, cfg: dict | None = None) -> str:
    cfg = _cfg(row) if cfg is None else cfg
    if row["kind"] == "drill" and cfg.get("source") == "quick":
        return "Quick questions"
    if cfg.get("kind") == "twin" or cfg.get("twin_of"):
        return "Twin"
    if (cfg.get("custom") or {}).get("source") == "misses":
        return "Prove it"
    return KIND_NAME.get(row["kind"], (row["kind"] or "").title())


# ------------------------------------------------------------------ the paper

def groups(row) -> list[tuple[int | None, list[dict]]]:
    """A sitting's questions as (module, questions): two modules for a section,
    one for a module sitting, one unnumbered group for everything else."""
    raw = _json(_col(row, "questions"), None)
    if isinstance(raw, dict):
        mods = [(n, raw[f"module{n}"]) for n in (1, 2)
                if isinstance(raw.get(f"module{n}"), list) and raw[f"module{n}"]]
        if mods:
            return mods
        return [(None, [q for v in raw.values() if isinstance(v, list) for q in v])]
    if isinstance(raw, list):
        return [(None, raw)]
    if row["kind"] == "mock":
        try:
            return [(1, mock_module(row, 1)), (2, mock_module(row, 2) if row["module"] == 2 or row["finished"] else [])]
        except KeyError:
            return [(None, [])]
    try:
        return [(None, marked_questions(row))]
    except (KeyError, TypeError):
        return [(None, [])]


def _is_right(q: dict, given) -> bool:
    try:
        return scoring.is_correct(q, given)
    except (KeyError, TypeError, ValueError):
        return False


def core(row) -> dict:
    """What every reader of one sitting needs, in a handful of queries: each
    question with its number, address, status and time."""
    cfg, result, qstate = _cfg(row), _result(row), _qstate(row)
    answers = db.load_answers(row)
    parts = [(m, [q for q in qs if isinstance(q, dict) and "id" in q]) for m, qs in groups(row)]
    parts = [(m, qs) for m, qs in parts if qs]
    sectioned = len(parts) > 1
    subject = _subject(row)
    atts = db.rows("SELECT * FROM attempts WHERE session=? ORDER BY id", row["id"])
    first: dict[str, object] = {}
    seconds: dict[str, object] = {}
    for a in atts:
        if (a["source"] or "") == "second":
            seconds.setdefault(a["qid"], a)
        elif a["qid"] not in first:
            first[a["qid"]] = a
    removed = set(result.get("removed") or ()) | {a["qid"] for a in atts if a["disputed"]}
    remarked = set(result.get("remarked") or ())
    tries: dict[str, list] = defaultdict(list)
    drilled = row["kind"] in DRILLS
    if drilled:
        for t in db.rows("SELECT * FROM tries WHERE session=? ORDER BY n, rowid", row["id"]):
            tries[t["qid"]].append(dict(t))
    items = []
    for module, qs in parts:
        for n, q in enumerate(qs, 1):
            qid = q["id"]
            given = answers.get(qid)
            st = qstate.get(qid) if isinstance(qstate.get(qid), dict) else {}
            a = first.get(qid)
            tr = tries.get(qid, [])
            if qid in removed:
                status = "removed"
            elif a is not None and a["void"]:
                status = "voided"
            elif given in (None, ""):
                status = "skipped" if st.get("skipped") else ("not_reached" if drilled and a is None else "blank")
            elif qid in remarked or (_is_right(q, given) and not (tr and not tr[0]["correct"])):
                status = "correct"
            elif tr and not tr[0]["correct"] and any(t["correct"] for t in tr[1:]):
                status = "mixed"
            else:
                status = "incorrect"
            ms = st.get("ms")
            if ms is None and a is not None:
                ms = a["ms"] if a["ms"] is not None else a["sms"]
            items.append({
                "q": q, "qid": qid, "n": n, "module": module if (sectioned or row["kind"] == "module") else None,
                "given": given, "status": status, "st": st, "attempt": a, "second_attempt": seconds.get(qid),
                "tries": tr, "ms": ms,
                "address": f"{subject}-m{module}-{n}" if sectioned else f"{subject}-{n}",
                "label": f"M{module} Q{n}" if sectioned else f"Q{n}"})
    return {"row": row, "cfg": cfg, "result": result, "qstate": qstate, "answers": answers,
            "items": items, "sectioned": sectioned, "subject": subject, "removed": removed,
            "first": first}


def sitting_ms(c: dict) -> int | None:
    """§3.5.5: the sum of per-question times, else the wall clock, else a
    set's own ms."""
    times = [i["st"].get("ms") for i in c["items"] if isinstance(i["st"].get("ms"), (int, float))]
    if times and sum(times):
        return int(sum(times))
    row = c["row"]
    if row["kind"] in PRACTICE + ("challenge",):
        ms = c["result"].get("ms") or sum((i["ms"] or 0) for i in c["items"])
        if ms:
            return int(ms)
    if row["finished"] and row["started"]:
        try:
            return progress.sitting_seconds(row) * 1000
        except (TypeError, ValueError, KeyError):
            return None
    return None


def _timing(cfg: dict) -> str:
    return cfg.get("timing") or ("untimed" if cfg.get("timed") is False else "official")


def timed(row, cfg: dict) -> bool:
    if row["kind"] in DRILLS:
        return bool(cfg.get("timed"))
    if row["kind"] == "practice":
        return False
    return _timing(cfg) not in ("untimed", "off")


def _factor(cfg: dict) -> float:
    return {"x1.5": 1.5, "x2": 2.0, "x0.85": 0.85}.get(_timing(cfg), 1.0)


def clock_ms(row, cfg: dict, questions: int) -> int | None:
    """The sitting's whole clock, for "64:12 of 70:00"."""
    if not timed(row, cfg):
        return None
    if row["kind"] in DRILLS:
        secs = drill.seconds_of(cfg)
        return secs * 1000 if secs else None
    if row["kind"] in SECTIONS:
        return int(2 * MODULE_MS * _factor(cfg))
    if row["kind"] == "module":
        return int(MODULE_MS * _factor(cfg))
    return int(questions * deps.SECONDS_PER_QUESTION * 1000 * _factor(cfg))


# ------------------------------------------------------------------ SR3: the second look

def second_block(c: dict) -> dict:
    """Is a second look offered, and which misses are still unseen? The offer
    stands for tests and end-mode sets, until skipped, done, 3 days old, or
    every miss has been seen; prefs.second_look turns it off."""
    row, cfg, qstate = c["row"], c["cfg"], c["qstate"]
    session = qstate.get("_session") if isinstance(qstate.get("_session"), dict) else {}
    st = session.get("second") if isinstance(session.get("second"), dict) else {}
    state = st.get("state")
    eligible = (row["kind"] in TESTS or (row["kind"] == "drill" and cfg.get("feedback") == "end")) \
        and not _inline(row["kind"], cfg)
    if eligible and state is None and _age_days(row["finished"]) >= SECOND_DAYS:
        state = "lapsed"
    misses = [i for i in c["items"] if i["status"] in MISSES]
    unseen = [i["qid"] for i in misses if not i["st"].get("seen_key") and not i["st"].get("second")]
    on = True
    if row["learner"]:
        try:
            from . import prefs
            on = bool(prefs.get(row["learner"]).get("second_look", True))
        except Exception:                           # a prefs row the registry rejects
            on = True
    offered = bool(eligible and state is None and unseen and on)
    looked = [i for i in misses if i["st"].get("second")]
    right = [i for i in looked if i["st"]["second"].get("correct")]
    slips = [i["qid"] for i in right if i["st"]["second"].get("conf") != "guess"]
    wrong = [i for i in looked if not i["st"]["second"].get("correct")]
    same = [i for i in wrong if i["attempt"] is not None and i["attempt"]["norm"]
            and i["st"]["second"].get("norm") == i["attempt"]["norm"]]
    out = {"eligible": eligible, "state": state, "offered": offered, "on": on,
           "unseen": unseen, "looked": len(looked), "right": len(right), "slips": slips,
           "same": len(same), "other": len(wrong) - len(same),
           "still_blank": sum(1 for i in misses if i["status"] in UNANSWERED and not i["st"].get("second")),
           "minutes": round(sum(drill.budget_ms(i["q"]["key"], i["q"]["difficulty"])
                                for i in misses if i["qid"] in unseen and "key" in i["q"]) / 60000),
           "with": None}
    if slips and _band(c["result"]):
        out["with"] = estimate.rescore(row["id"], right=slips)
    return out


def hold_back(sitting: dict, item: dict) -> dict:
    """SR3: while a second look is offered, an unseen miss goes out with
    nothing derived from its key, whoever asks. `sitting` is the payload's
    `second` block ({offered, unseen}); every serializer of a review item
    (results, compare, prints, the worksheet, history peeks) calls this."""
    if not sitting or not sitting.get("offered") or item.get("id") not in set(sitting.get("unseen") or ()):
        return item
    out = {k: v for k, v in item.items() if k not in HELD}
    if isinstance(out.get("crowd"), dict):
        out["crowd"] = {k: v for k, v in out["crowd"].items() if k != "option_share"}
    if isinstance(out.get("cause"), dict):
        ev = out["cause"].get("evidence") or {}
        out["cause"] = {**out["cause"], "evidence": {k: v for k, v in ev.items()
                                                     if k not in ("diagnosis", "struck_key", "first")}}
    if isinstance(out.get("trap"), dict):
        out["trap"] = {**out["trap"], "label": None}
    if out.get("tries"):
        out["tries"] = [{k: v for k, v in t.items() if k != "reason"} for t in out["tries"]]
    out["hidden"] = True
    return out
