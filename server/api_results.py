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
from .deps import learner_of, now, session_or_404, tz_of, writer_of

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
        "wrong_step", "option_steps", "diagnosis", "spr_reasons", "spr_mistakes",
        "struck", "marks")
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
    if db.is_sample(row["learner"]):
        raise HTTPException(403, "the sample report is read-only")
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
        out["crowd"] = {k: v for k, v in out["crowd"].items()
                        if k not in ("option_share", "n", "rate", "level")}
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


# ------------------------------------------------------------------ report

def _read_sitting(sid: str, x_learner: str | None):
    row = session_or_404(sid)
    if not row["finished"]:
        raise HTTPException(409, {"need": "finish", "kind": row["kind"]})
    # SEC-03: a learner-owned report requires that learner's credential. The
    # old anonymous diagnostic is released only after its signup gate.
    who = viewer(x_learner)
    if row["learner"] and row["learner"] != who and sid != "sample-section":
        raise HTTPException(403, {"need": "owner"})
    if not row["learner"] and not row["user_id"]:
        raise HTTPException(403, {"need": "signup"})
    if row["kind"] == "challenge" and row["day"]:
        from . import daily
        if row["day"] >= daily.today(-840) and row["learner"] != who:
            raise HTTPException(403, {"need": "owner"})
    return row, who


def _profile(learner: str | None) -> dict:
    if not learner:
        return {"target": None, "exam_date": None}
    r = db.one("SELECT target,exam_date FROM learners WHERE id=?", learner)
    return dict(r) if r else {"target": None, "exam_date": None}


def _flagged(learner: str | None, sid: str) -> set[str]:
    if not learner:
        return set()
    return {r["qid"] for r in db.rows("SELECT qid FROM flags WHERE learner=? AND session=?", learner, sid)}


def _review(c: dict, second: dict, ledger: dict | None, causes: dict | None) -> list[dict]:
    row = c["row"]
    learner = row["learner"]
    qids = [i["qid"] for i in c["items"]]
    keys = {(i["q"].get("key"), i["q"].get("seed")) for i in c["items"]}
    flags = _flagged(learner, row["id"])
    saved = {(r["template"], r["seed"]) for r in db.rows(
        "SELECT template,seed FROM saved WHERE learner=?", learner)} if learner else set()
    notes = {(r["template"], r["seed"]): dict(r) for r in db.rows(
        "SELECT template,seed,note,marks FROM notes WHERE learner=?", learner)} if learner else {}
    reported = {r["qid"] for r in db.rows(
        "SELECT qid FROM reports WHERE learner=? AND session=?", learner, row["id"])} if learner else set()
    traps = {(r["template"], r["norm"] or ""): dict(r) for r in db.rows(
        "SELECT * FROM traps WHERE learner=?", learner)} if learner else {}
    history: dict[str, list[dict]] = defaultdict(list)
    if learner and keys:
        names = sorted({k for k, _ in keys if k})
        if names:
            holes = ",".join("?" for _ in names)
            for a in db.rows("SELECT template,at,session,correct,reason,ms FROM attempts"
                             f" WHERE learner=? AND template IN ({holes}) AND COALESCE(session,'')!=?"
                             " ORDER BY id DESC LIMIT 500", learner, *names, row["id"]):
                if len(history[a["template"]]) < 5:
                    history[a["template"]].append(dict(a))
    levels = drill.levels()
    out = []
    for i in c["items"]:
        q, qid, st = i["q"], i["qid"], i["st"]
        key = (q.get("key"), q.get("seed"))
        a = i["attempt"]
        trap = traps.get((q.get("key"), a["norm"] or "")) if a and not a["correct"] else None
        note = notes.get(key) or {}
        status = i["status"]
        crowd = levels.get((q.get("key"), q.get("difficulty")), {})
        odds = c["result"].get("odds") or {}
        item = {**q, "id": qid, "n": i["n"], "module": i["module"], "address": i["address"],
                "label": i["label"], "subject": c["subject"], "status": status,
                "correct": status == "correct", "given": i["given"], "ms": i["ms"],
                "flagged": qid in flags, "saved": key in saved, "reported": qid in reported,
                "repair": bool(q.get("repair") or (a and a["repair"])),
                "ref": f"{q.get('key') or qid} · {q.get('seed', '')}",
                "changes": st.get("trail") or [], "conf": st.get("conf") or (a["conf"] if a else None),
                "struck": st.get("struck"),
                "trap": {"open": not trap["closed"], "owed": trap["owed"], "closed": trap["closed"],
                         "hits": trap["hits"], "label": trap["label"]} if trap else None,
                "mistake": a["reason"] if a and not a["correct"] else None,
                "history": history.get(q.get("key"), []), "note": note.get("note"),
                "marks": _json(note.get("marks"), []), "tries": i["tries"],
                "second": st.get("second"), "seen": bool(st.get("seen_key")),
                "cause": (causes or {}).get("per_q", {}).get(qid),
                "worth": worth((ledger or {}).get("per_q", {}).get(qid, {}).get("pts")),
                "crowd": crowd or None, "odds": odds.get(qid) if isinstance(odds, dict) else None}
        if q.get("type") == "spr":
            item["accepted"] = scoring.accepted_forms(q["answer"]) if "answer" in q else []
            item["diagnosis"] = scoring.grid_diagnose(str(i["given"]), str(q["answer"])) \
                if i["given"] not in (None, "") and status == "incorrect" else None
        if i["tries"]:
            item["tries"] = i["tries"]
        out.append(hold_back(second, item))
    return out


def _report_insight(c: dict, review: list[dict], second: dict, summary: dict) -> dict:
    """Small report readers over the one marked sitting. Key-derived lines only
    use misses whose key is already visible (SR3)."""
    row = c["row"]
    learner = row["learner"]
    visible = [i for i in review if not i.get("hidden")]
    misses = [i for i in visible if i["status"] in MISSES]
    judgement = progress.calibration(learner, session=row["id"]) if learner else {}
    session = c["qstate"].get("_session") or {}
    away = session.get("away_log") or []
    judgement.update({"away": {"n": len(away), "ms": sum(x[1] for x in away if isinstance(x, list)
                              and len(x) > 1 and isinstance(x[1], (int, float))), "log": away},
                      "pauses": row["pauses"],
                      "crossed_key": [i["id"] for i in visible if i.get("struck") and i.get("answer") in
                                      ["ABCD"[k] for k in i["struck"] if isinstance(k, int) and 0 <= k < 4]]})
    from . import habits
    families: dict[str, dict] = {}
    norms: dict[str, dict] = {}
    for i in misses:
        a = next((x["attempt"] for x in c["items"] if x["qid"] == i["id"]), None)
        if not a or not a["reason"]:
            continue
        family = habits.family_of(a["reason"])
        if family:
            h = families.setdefault(family["id"], {"id": family["id"], "name": family["name"],
                           "tell": family["tell"], "qids": [], "topics": set(), "recur": 0})
            h["qids"].append(i["id"])
            h["topics"].add(i.get("topic"))
        norm = a["norm"] or ""
        if norm:
            n = norms.setdefault(norm, {"norm": norm, "label": a["reason"], "qids": [],
                                        "templates": set(), "hits_all_time": 0, "unmet_types": 0})
            n["qids"].append(i["id"])
            n["templates"].add(a["template"])
    for n in norms.values():
        n["hits_all_time"] = sum(r["hits"] for r in db.rows("SELECT hits FROM traps WHERE learner=? AND norm=?",
                                                     learner, n["norm"])) if learner else 0
        n["templates"] = sorted(n["templates"])
    for h in families.values():
        h["topics"] = sorted(t for t in h["topics"] if t)
    rush = []
    long = []
    for i in review:
        if not isinstance(i.get("ms"), (int, float)):
            continue
        if i["ms"] < RUSHED_MS and i["status"] in MISSES:
            rush.append(i["id"])
        if i["ms"] > LONG_MS:
            long.append(i["id"])
    pace = {"pace_ms": PACE_MS, "rushed": rush, "long": long,
            "per_q": [{"qid": i["id"], "ms": i.get("ms"),
                       "budget_ms": drill.budget_ms(i.get("key"), i.get("difficulty"))
                       if i.get("key") and i.get("difficulty") in TIER_ORDER else PACE_MS}
                      for i in review]}
    takeaways = []
    if summary["incorrect"] or summary["unanswered"]:
        takeaways.append({"kind": "misses", "text": f"{summary['incorrect']} incorrect and {summary['unanswered']} unanswered"})
    if rush:
        takeaways.append({"kind": "pace", "text": f"{len(rush)} quick misses; leave time to check them"})
    if summary["changed"]["right_to_wrong"]:
        takeaways.append({"kind": "changes", "text":
                          f"{summary['changed']['right_to_wrong']} answers changed from right to wrong"})
    return {"judgement": judgement, "habits": [h for h in families.values() if len(h["qids"]) >= 2],
            "norms": [n for n in norms.values() if len(n["qids"]) >= 2 or n["hits_all_time"] >= 3],
            "pace": pace, "debrief": {"takeaways": takeaways[:3],
                                      "reviewed": {"n": sum(i.get("seen") for i in review if i["status"] in MISSES),
                                                   "of": sum(i["status"] in MISSES for i in review)}},
            "conditions": {"timing": _timing(c["cfg"]), "pauses": row["pauses"],
                           "calculator": c["cfg"].get("calculator"),
                           "ranked": bool(row["ranked"]), "unranked_why": row["unranked_why"]}}


def report(sid: str, x_learner: str | None = None) -> dict:
    row, who = _read_sitting(sid, x_learner)
    c = core(row)
    result, learner = c["result"], row["learner"]
    counted = [i for i in c["items"] if i["status"] != "not_reached"]
    counts = Counter("unanswered" if i["status"] in UNANSWERED else
                     "correct" if i["status"] in CORRECT else "incorrect" for i in counted)
    right, incorrect, blank = counts["correct"], counts["incorrect"], counts["unanswered"]
    asked = len(counted)
    flags = _flagged(learner, sid)
    flagged_wrong = sum(i["qid"] in flags and i["status"] not in CORRECT for i in counted)
    changed = Counter()
    for i in c["items"]:
        trail = i["st"].get("trail") or []
        if len(trail) < 2:
            continue
        first = next((x for x in trail if x not in (None, "")), None)
        last = next((x for x in reversed(trail) if x not in (None, "")), None)
        if first is None or last is None or str(first) == str(last):
            continue
        was, now = _is_right(i["q"], first), _is_right(i["q"], last)
        changed["total"] += 1
        changed["wrong_to_right" if now and not was else "right_to_wrong" if was and not now
                else "wrong_to_wrong"] += 1
    ms = sitting_ms(c)
    summary = {"correct": right, "incorrect": incorrect, "unanswered": blank,
               "answered": right + incorrect, "accuracy": round(right / asked, 3) if asked else 0,
               "accuracy_answered": round(right / (right + incorrect), 3) if right + incorrect else 0,
               "ms": ms, "avg_ms": round(ms / asked) if ms and asked else None,
               "pace_ms": PACE_MS, "flagged": len(flags), "flagged_wrong": flagged_wrong,
               "changed": {k: changed[k] for k in ("total", "wrong_to_right", "right_to_wrong", "wrong_to_wrong")}}
    modules = []
    for mod, items in groups(row):
        if not items:
            continue
        ids = {q["id"] for q in items if isinstance(q, dict) and "id" in q}
        xs = [i for i in counted if i["qid"] in ids]
        modules.append({"n": mod, "route": row["route"] if mod == 2 else "mixed",
                        "right": sum(i["status"] == "correct" for i in xs), "asked": len(xs),
                        "ms": sum(i["ms"] or 0 for i in xs), "flagged": len(ids & flags),
                        "wrong": [i["n"] for i in xs if i["status"] in INCORRECT],
                        "blank": [i["n"] for i in xs if i["status"] in UNANSWERED]})
    led = estimate.ledger(sid) if _band(result) and learner else None
    causes = progress.causes(learner, session=sid, subject=c["subject"]) if learner else None
    second = second_block(c)
    review = _review(c, second, led, causes)
    domains = scoring.score([i["q"] for i in counted], c["answers"])["domains"] if counted else []
    for d in domains:
        d.update({"pct": round(d["right"] / d["asked"], 3) if d["asked"] else 0,
                  "share": round(d["asked"] / asked, 3) if asked else 0,
                  "level": round(d["mastery"] * 7), "previous": None})
    by_topic: dict[str, dict] = {}
    for i in counted:
        q = i["q"]
        t = by_topic.setdefault(q.get("topic", i["qid"]), {"topic": q.get("topic"),
            "name": q.get("topic_name"), "domain": q.get("domain"), "right": 0, "asked": 0,
            "before": 0.0, "after": 0.0, "open": 0})
        t["asked"] += 1
        t["right"] += int(i["status"] == "correct")
    if learner:
        first_id = db.one("SELECT MIN(id) AS n FROM attempts WHERE session=?", sid)
        before_id = first_id["n"] if first_id else None
        for t in by_topic.values():
            if not t["topic"]:
                continue
            past = db.rows("SELECT difficulty,correct FROM attempts WHERE learner=? AND topic=? AND id<?"
                           " ORDER BY id DESC LIMIT 30", learner, t["topic"], before_id or 0)
            t["before"] = progress.mastery_of([(p["difficulty"], p["correct"]) for p in past])
            t["after"] = progress.topic_mastery(learner, t["topic"])
            t["open"] = db.one("SELECT COUNT(*) n FROM traps WHERE learner=? AND topic=? AND closed IS NULL",
                               learner, t["topic"])["n"]
    by_difficulty, by_format = [], []
    for field, dest, order in (("difficulty", by_difficulty, TIER_ORDER), ("type", by_format, ("mcq", "spr"))):
        for value in order:
            xs = [i for i in counted if i["q"].get(field) == value]
            if xs:
                times = [i["ms"] for i in xs if i["ms"] is not None]
                dest.append({"key": value, "right": sum(i["status"] == "correct" for i in xs),
                             "asked": len(xs), "avg_ms": round(statistics.mean(times)) if times else None})
    grouped = defaultdict(list)
    for i in counted:
        if i["status"] in MISSES and i["attempt"]:
            a = i["attempt"]
            grouped[(a["template"], a["norm"] or "")].append(i["qid"])
    mistakes = []
    for (template, norm), ids in grouped.items():
        t = db.one("SELECT * FROM traps WHERE learner=? AND template=? AND norm=?", learner, template, norm)
        mistakes.append({"template": template, "reason": norm, "label": t["label"] if t else "Incorrect",
                         "kind": "misconception" if norm else "gridin", "topic": t["topic"] if t else None,
                         "qids": ids, "open": bool(t and not t["closed"]), "owed": t["owed"] if t else 0,
                         "closed": t["closed"] if t else None, "hits_all_time": t["hits"] if t else len(ids)})
    sequence = seqs(learner)
    same = [r for r in db.rows("SELECT id,finished,result FROM sessions WHERE learner=? AND kind=?"
                              " AND finished<? AND abandoned IS NULL ORDER BY finished DESC,rowid DESC LIMIT 1",
                              learner, row["kind"], row["finished"])] if learner else []
    previous = None
    if same:
        p = same[0]
        previous = {"id": p["id"], "seq": sequence.get(p["id"]), "finished": p["finished"],
                    "estimate": _result(p).get("estimate"), "right": _result(p).get("right"),
                    "asked": _result(p).get("asked")}
    rank = estimate.percentile(sid) if _band(result) else {"ranked": False, "pct": None, "n": 0}
    rank["attempt"] = sequence.get(sid)
    if rank.get("why") == "too few sittings" and row["ranked"] and sequence.get(sid) == 1:
        rank["ranked"] = True
    if _band(result):
        rank["national"] = estimate.national(result["estimate"]["low"], result["estimate"]["high"], c["subject"])
    twins = db.rows("SELECT id FROM sessions WHERE learner=? AND finished IS NOT NULL"
                    " AND json_extract(cfg,'$.parent')=?", learner, sid) if learner else []
    insight = _report_insight(c, review, second, summary)
    challenge = None
    if row["kind"] == "challenge" and row["day"]:
        from . import challenge as challenge_module
        board = challenge_module.board(row["day"], learner)
        avg = db.one("SELECT AVG(CAST(json_extract(result,'$.right') AS REAL)) AS n FROM sessions"
                     " WHERE kind='challenge' AND day=? AND finished IS NOT NULL", row["day"])
        challenge = {"day": row["day"], "rank": (board.get("you") or {}).get("rank"),
                     "players": board.get("players"), "average": round(avg["n"], 2) if avg and avg["n"] else 0}
    return {**result, "id": sid, "mode": row["kind"], "kind": row["kind"],
            "subject": c["subject"], "started": row["started"], "finished": row["finished"],
            "mine": bool(learner and who == learner), "verified": bool(row["user_id"] and
            (db.one("SELECT verified FROM users WHERE id=?", row["user_id"]) or {"verified": 0})["verified"]),
            "seq": sequence.get(sid), "label": kind_name(row), "source": c["cfg"].get("source"),
            "ms": ms, "timed": timed(row, c["cfg"]), "clock_ms": clock_ms(row, c["cfg"], asked),
            "right": right, "asked": asked, "summary": summary, "modules": modules,
            "domains": domains, "topics": list(by_topic.values()), "by_difficulty": by_difficulty,
            "by_format": by_format, "mistakes": mistakes, "review": review,
            "previous": previous, "rank": rank, "ledger": led, "second": second,
            "causes": causes, "recovery": progress.recovery(learner, sid) if learner else None,
            "profile": _profile(learner), "twins": {"n": len(twins), "right": 0},
            "total": estimate.total(learner, sid) if learner and _band(result) else None,
            "challenge": challenge, "contest": {"points": result.get("points"),
                                                  "points_parts": result.get("points_parts"),
                                                  "skipped": result.get("skipped"),
                                                  "voided": result.get("voided")}
            if row["contest"] else None,
            **insight,
            "route_rule": {"cut": scoring.ROUTE_UP_AT, "lower_ceiling": scoring.LOWER_ROUTE_CEILING,
                           "half_band": 70 if row["kind"] in SECTIONS else 100},
            "note": row["note"]}


@router.get("/api/session/{sid}/results")
def get_results(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    return report(sid, x_learner)


# ------------------------------------------------------------------ one sittings list (R26)

def _listed(row, include_words: bool) -> bool:
    cfg, result = _cfg(row), _result(row)
    if row["abandoned"] or _inline(row["kind"], cfg) or row["kind"] == "spot":
        return False
    if row["kind"] == "words" and not include_words:
        return False
    if row["kind"] in PRACTICE + ("challenge", "words") and result.get("asked", 0) == 0:
        return False
    return True


def _kind_filter(row, kinds: set[str]) -> bool:
    if not kinds or "all" in kinds:
        return True
    k = row["kind"]
    return k in kinds or ("tests" in kinds and k in TESTS + ("custom",)) or \
        ("practice" in kinds and k in PRACTICE) or ("challenge" in kinds and k == "challenge")


def history(learner: str, kind: str | None = None, open_only: bool = False,
            limit: int = 20, offset: int = 0, all_: bool = False,
            reviewed: bool | None = None, topic: str | None = None,
            sort: str = "newest", shared: bool = False) -> dict:
    kinds = {s.strip() for s in (kind or "").split(",") if s.strip()}
    include_words = "words" in kinds or all_
    rows = [r for r in db.rows("SELECT rowid,* FROM sessions WHERE learner=? AND finished IS NOT NULL"
                               " ORDER BY finished DESC,rowid DESC", learner)
            if _listed(r, include_words) and _kind_filter(r, kinds)]
    seq = seqs(learner)
    all_rows = rows[:]
    if topic:
        ids = {r["session"] for r in db.rows("SELECT DISTINCT session FROM attempts"
                                               " WHERE learner=? AND topic=?", learner, topic)}
        rows = [r for r in rows if r["id"] in ids]
    previous_mid: dict[str, float] = {}
    deltas: dict[str, float | None] = {}
    for r in reversed(all_rows):
        mid = _mid(_band(_result(r)))
        deltas[r["id"]] = mid - previous_mid[r["kind"]] if mid is not None and r["kind"] in previous_mid else None
        if mid is not None:
            previous_mid[r["kind"]] = mid
    entries = []
    for r in rows:
        cfg, result = _cfg(r), _result(r)
        c = core(r)
        counted = [i for i in c["items"] if i["status"] != "not_reached"]
        modules = []
        for n, qs in groups(r):
            ids = {q["id"] for q in qs if isinstance(q, dict) and "id" in q}
            xs = [i for i in counted if i["qid"] in ids]
            if not xs:
                continue
            modules.append({"n": n, "right": sum(i["status"] == "correct" for i in xs),
                            "asked": len(xs), "wrong": [i["n"] for i in xs if i["status"] in INCORRECT],
                            "blank": [i["n"] for i in xs if i["status"] in UNANSWERED]})
        traps = db.one("SELECT COUNT(*) n FROM traps WHERE learner=? AND session=? AND closed IS NULL",
                       learner, r["id"])
        open_n = traps["n"] if traps else 0
        if open_only and open_n == 0:
            continue
        misses = [i for i in counted if i["status"] in MISSES]
        seen = sum(bool(i["st"].get("seen_key")) for i in misses)
        if reviewed is False and (not misses or seen == len(misses)):
            continue
        twins = db.one("SELECT COUNT(*) n FROM sessions WHERE learner=? AND finished IS NOT NULL"
                       " AND json_extract(cfg,'$.parent')=?", learner, r["id"])["n"]
        rec = progress.recovery(learner, r["id"]) if _band(result) else None
        entry = {"id": r["id"], "kind": r["kind"], "subject": _subject(r),
                 "started": r["started"], "finished": r["finished"],
                 "seq": seq.get(r["id"]), "label": kind_name(r, cfg),
                 "right": result.get("right", sum(i["status"] == "correct" for i in counted)),
                 "asked": result.get("asked", len(counted)), "estimate": result.get("estimate"),
                 "ms": sitting_ms(c), "pct": round(result.get("right", 0) / result["asked"], 3)
                 if result.get("asked") else None, "route": r["route"], "delta": deltas.get(r["id"]),
                 "modules": modules, "open": open_n, "twins": twins,
                 "reviewed": {"n": seen, "of": len(misses)}, "recovery": rec,
                 "topics": [t.get("topic") for t in result.get("topics", ()) if isinstance(t, dict)]
                 or cfg.get("topics", []), "note": r["note"]}
        entries.append(entry)
    if sort == "points_open":
        entries.sort(key=lambda x: ((x["recovery"] or {}).get("points_open") or 0, x["finished"]), reverse=True)
    elif sort == "oldest":
        entries.reverse()
    elif sort in ("highest", "lowest"):
        entries.sort(key=lambda x: _mid(_band(x)) if _band(x) else -1, reverse=sort == "highest")
    counts = {"all": len(all_rows), "tests": sum(r["kind"] in TESTS + ("custom",) for r in all_rows),
              "practice": sum(r["kind"] in PRACTICE for r in all_rows),
              "challenge": sum(r["kind"] == "challenge" for r in all_rows)}
    in_progress = []
    if not shared:
        from .api_tests import remaining
        for r in db.rows("SELECT * FROM sessions WHERE learner=? AND finished IS NULL"
                         " AND abandoned IS NULL ORDER BY started DESC", learner):
            cfg = _cfg(r)
            if _inline(r["kind"], cfg) or r["kind"] == "spot" or cfg.get("source") == "quick":
                continue
            if r["kind"] not in TESTS + PRACTICE + ("custom",):
                continue
            answers = db.load_answers(r)
            if r["kind"] in PRACTICE and not answers:
                continue
            try:
                total = sum(len(qs) for _, qs in groups(r))
                left = None if not timed(r, cfg) else remaining(r)
            except (KeyError, TypeError, ValueError):
                total, left = 0, None
            in_progress.append({"id": r["id"], "kind": r["kind"], "started": r["started"],
                                "module": r["module"], "answered": len(answers), "total": total,
                                "seconds_left": left, "expired": left == 0 if left is not None else False})
    weeks: dict[str, dict] = {}
    for x in entries:
        day = dt.date.fromisoformat(x["finished"][:10])
        week = (day - dt.timedelta(days=day.weekday())).isoformat()
        w = weeks.setdefault(week, {"week": week, "sittings": 0, "questions": 0, "ms": 0})
        w["sittings"] += 1
        w["questions"] += x["asked"] or 0
        w["ms"] += x["ms"] or 0
    return {"sessions": entries[offset:offset + limit], "total": len(entries),
            "counts": counts, "in_progress": in_progress, "weeks": list(weeks.values())}


@router.get("/api/history")
def get_history(kind: str | None = None, open: bool = False, limit: int = Query(default=20, ge=1, le=200),
                offset: int = Query(default=0, ge=0), all: bool = False,
                reviewed: bool | None = None, topic: str | None = None, sort: str = "newest",
                share: str | None = None, x_learner: str | None = Header(default=None)) -> dict:
    learner, shared = _reader(x_learner, share)
    return history(learner, kind, open, limit, offset, all, reviewed, topic, sort, shared)


# ------------------------------------------------------------------ overview and skill panel

def _split_attempts(rows: list, field: str, order: tuple[str, ...]) -> list[dict]:
    return [{"difficulty" if field == "difficulty" else "format": key,
             "key": key, "right": sum(bool(r["correct"]) for r in rows if r[field] == key),
             "answered": sum(r[field] == key for r in rows),
             "avg_ms": round(statistics.mean([r["ms"] for r in rows
                                               if r[field] == key and r["ms"] is not None]))
             if any(r[field] == key and r["ms"] is not None for r in rows) else None}
            for key in order]


def stats(learner: str, tz: int = 0) -> dict:
    rows = db.rows("SELECT * FROM attempts WHERE learner=? AND repeat=0 AND disputed=0", learner)
    last14 = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=14)).isoformat()
    recent = [a for a in rows if a["at"] >= last14]
    ledger = progress.days(learner, tz)
    est = estimate.estimate(learner)
    traps = db.rows("SELECT * FROM traps WHERE learner=? ORDER BY hits DESC,last DESC", learner)
    sittings = db.rows("SELECT id,kind,finished,result FROM sessions WHERE learner=?"
                       " AND finished IS NOT NULL AND abandoned IS NULL ORDER BY finished DESC,rowid DESC", learner)
    tests = {k: sum(r["kind"] == k for r in sittings) for k in ("mock", "module", "diagnostic")}
    over = []
    numbers = seqs(learner)
    for r in sittings:
        result = _result(r)
        if _band(result) and len(over) < 5:
            over.append({"id": r["id"], "seq": numbers.get(r["id"]), "finished": r["finished"],
                         "domains": [{"domain": d["domain"], "right": d["right"], "asked": d["asked"]}
                                     for d in result.get("domains", ())]})
    minutes_week = sum(day["minutes"] for day in ledger["recent"][-7:])
    causes = progress.causes(learner)
    profile = _profile(learner)
    return {"answered": len(rows), "right": sum(bool(a["correct"]) for a in rows),
            "accuracy": round(sum(bool(a["correct"]) for a in rows) / len(rows), 3) if rows else 0,
            "recent_accuracy": round(sum(bool(a["correct"]) for a in recent) / len(recent), 3)
            if recent else None, "minutes_total": ledger["minutes_total"], "minutes_week": minutes_week,
            "tests": tests, "streak": ledger["streak"], "best_streak": ledger["best_streak"],
            "days14": ledger["recent"], "by_difficulty": _split_attempts(rows, "difficulty", TIER_ORDER),
            "by_format": _split_attempts(rows, "fmt", ("mcq", "spr")),
            "traps": {"open": sum(not t["closed"] for t in traps),
                      "closed": sum(bool(t["closed"]) for t in traps)},
            "top_traps": [{"label": t["label"], "topic": t["topic"], "template": t["template"],
                           "hits": t["hits"], "open": not bool(t["closed"]), "owed": t["owed"],
                           "last": t["last"], "closed": t["closed"]} for t in traps[:10]],
            "latest": est["latest"], "previous": est["previous"], "best": est["best"],
            "estimate": est, "domains_over_time": over, "profile": profile,
            "gap": estimate.gains(learner), "why": causes,
            "calibration_trend": progress.calibration(learner),
            "types_met": progress.types_met(learner),
            "week": {"minutes": minutes_week, "questions": sum(d["questions"] for d in ledger["recent"][-7:])}}


@router.get("/api/stats")
def get_stats(share: str | None = None, x_learner: str | None = Header(default=None),
              x_tz: int = Depends(tz_of)) -> dict:
    learner, _ = _reader(x_learner, share)
    return stats(learner, x_tz)


def skill(learner: str, topic: str) -> dict:
    catalogue = practice.catalogue()["topics"]
    if topic not in catalogue:
        raise HTTPException(404, "no such skill")
    t = catalogue[topic]
    rows = db.rows("SELECT * FROM attempts WHERE learner=? AND topic=? AND repeat=0 AND disputed=0"
                   " ORDER BY id", learner, topic)
    traps = db.rows("SELECT * FROM traps WHERE learner=? AND topic=? ORDER BY last DESC", learner, topic)
    numbers = seqs(learner)
    sittings = []
    by_session: dict[str, list] = defaultdict(list)
    for a in rows:
        if a["session"]:
            by_session[a["session"]].append(a)
    if by_session:
        holes = ",".join("?" for _ in by_session)
        for s in db.rows(f"SELECT id,kind,finished FROM sessions WHERE id IN ({holes})"
                         " AND finished IS NOT NULL ORDER BY finished DESC,rowid DESC", *by_session):
            a = by_session[s["id"]]
            sittings.append({"id": s["id"], "kind": s["kind"], "seq": numbers.get(s["id"]),
                             "finished": s["finished"], "right": sum(bool(x["correct"]) for x in a),
                             "asked": len(a)})
            if len(sittings) >= 5:
                break
    return {"topic": topic, "name": t.name, "domain": t.domain,
            "mastery": progress.topic_mastery(learner, topic), "answered": len(rows),
            "right": sum(bool(a["correct"]) for a in rows),
            "by_difficulty": _split_attempts(rows, "difficulty", TIER_ORDER),
            "recent": [bool(a["correct"]) for a in rows[-20:]],
            "last": rows[-1]["at"] if rows else None,
            "traps_open": [{"template": x["template"], "label": x["label"],
                            "hits": x["hits"], "owed": x["owed"]} for x in traps if not x["closed"]],
            "traps_closed": sum(bool(x["closed"]) for x in traps), "sittings": sittings,
            "practice": {"topics": [topic]}}


@router.get("/api/skill/{topic}")
def get_skill(topic: str, share: str | None = None,
              x_learner: str | None = Header(default=None)) -> dict:
    learner, _ = _reader(x_learner, share)
    return skill(learner, topic)


# ------------------------------------------------------------------ actions on a finished sitting

def _qid(c: dict, question_id: str) -> dict:
    item = next((i for i in c["items"] if i["qid"] == question_id), None)
    if item is None:
        raise HTTPException(422, "that question is not in this sitting")
    return item


class WhatIf(BaseModel):
    right: list[str] = Field(default_factory=list, max_length=MAX_IDS)
    wrong: list[str] = Field(default_factory=list, max_length=MAX_IDS)
    drop: list[str] = Field(default_factory=list, max_length=MAX_IDS)


@router.post("/api/session/{sid}/whatif")
def whatif(sid: str, body: WhatIf, x_learner: str | None = Header(default=None)) -> dict:
    row, _ = _owned(sid, x_learner)
    ids = {i["qid"] for i in core(row)["items"]}
    if (set(body.right) | set(body.wrong) | set(body.drop)) - ids \
            or set(body.right) & set(body.wrong):
        raise HTTPException(422, "select questions from this sitting")
    out = estimate.rescore(sid, right=body.right, wrong=body.wrong, drop=body.drop)
    if out is None:
        raise HTTPException(409, "this sitting has no score band")
    return out


class SecondIn(BaseModel):
    question_id: str
    answer: int | str
    conf: str | None = Field(default=None, pattern="^(sure|unsure|guess)$")
    ms: int | None = Field(default=None, ge=0, le=600_000)


@router.post("/api/session/{sid}/second")
def second_answer(sid: str, body: SecondIn, x_learner: str | None = Header(default=None)) -> dict:
    row, learner = _owned(sid, x_learner)
    c = core(row)
    item = _qid(c, body.question_id)
    if item["status"] not in MISSES:
        raise HTTPException(409, "second look is for missed questions")
    q = item["q"]
    st = item["st"]
    session = c["qstate"].get("_session") or {}
    second = session.get("second") or {}
    if second.get("state") in ("skipped", "lapsed", "done") or _age_days(row["finished"]) >= SECOND_DAYS:
        raise HTTPException(409, "second look has ended")
    if st.get("seen_key") or st.get("second"):
        raise HTTPException(409, "answers already shown")
    if not q.get("key"):
        raise HTTPException(409, "this question has no repeatable type")
    correct = scoring.is_correct(q, body.answer)
    at = now()
    with db.atomic():
        fresh = session_or_404(sid)
        state = _qstate(fresh)
        prior = state.get(body.question_id) or {}
        if prior.get("seen_key") or prior.get("second"):
            raise HTTPException(409, "answers already shown")
        prior["second"] = {"answer": body.answer, "correct": bool(correct),
                           "conf": body.conf, "ms": body.ms, "at": at}
        prior["seen_key"] = True
        state[body.question_id] = prior
        db.run("UPDATE sessions SET qstate=? WHERE id=?", json.dumps(state), sid)
        progress.record(learner, sid, q, body.answer, body.ms, at, conf=body.conf,
                        source="second", revealed=True)
    return {"correct": bool(correct), "answer": q["answer"], "reasons": q.get("reasons"),
            "rationale": q.get("rationale"), "accepted": scoring.accepted_forms(str(q["answer"]))
            if q.get("type") == "spr" else [], "cause": progress.causes(learner, session=sid)
            .get("per_q", {}).get(body.question_id),
            "verdict": "slip" if correct and body.conf != "guess" else "same trap" if not correct else "guess"}


class SeenIn(BaseModel):
    qids: list[str] = Field(max_length=MAX_IDS)


@router.post("/api/session/{sid}/seen")
def seen(sid: str, body: SeenIn, x_learner: str | None = Header(default=None)) -> dict:
    row, _ = _owned(sid, x_learner)
    c = core(row)
    ids = {i["qid"] for i in c["items"]}
    if set(body.qids) - ids:
        raise HTTPException(422, "select questions from this sitting")
    state = c["qstate"]
    for qid in body.qids:
        st = state.get(qid) or {}
        st["seen_key"] = True
        state[qid] = st
    db.run("UPDATE sessions SET qstate=? WHERE id=?", json.dumps(state), sid)
    return {"seen": sorted(set(body.qids))}


class SecondStateIn(BaseModel):
    state: str = Field(pattern="^(skipped|done)$")


@router.post("/api/session/{sid}/second/state")
def second_state(sid: str, body: SecondStateIn, x_learner: str | None = Header(default=None)) -> dict:
    row, _ = _owned(sid, x_learner)
    state = _qstate(row)
    session = state.get("_session") or {}
    if (session.get("second") or {}).get("state") in ("skipped", "done"):
        raise HTTPException(409, "second look has already ended")
    session["second"] = {"state": body.state, "at": now()}
    state["_session"] = session
    db.run("UPDATE sessions SET qstate=? WHERE id=?", json.dumps(state), sid)
    return {"state": body.state}


class WhyIn(BaseModel):
    question_id: str
    kind: str = Field(pattern="^(auto|trap|slip|misread|rushed|clock|entry|gap)$")


@router.post("/api/session/{sid}/why")
@router.post("/api/drill/{sid}/why")
def why(sid: str, body: WhyIn, x_learner: str | None = Header(default=None)) -> dict:
    row, learner = _owned(sid, x_learner)
    item = _qid(core(row), body.question_id)
    if item["status"] not in MISSES:
        raise HTTPException(409, "only a miss can have a cause")
    a = item["attempt"]
    if not a:
        raise HTTPException(409, "this miss has no answer to annotate")
    db.run("UPDATE attempts SET miss_kind=? WHERE id=? AND learner=?", None if body.kind == "auto" else body.kind,
           a["id"], learner)
    return {"cause": progress.causes(learner, session=sid).get("per_q", {}).get(body.question_id)}


class NoteIn(BaseModel):
    note: str | None = Field(default=None, max_length=140)


@router.post("/api/session/{sid}/note")
def note(sid: str, body: NoteIn, x_learner: str | None = Header(default=None)) -> dict:
    _owned(sid, x_learner)
    value = (body.note or "").strip()
    db.run("UPDATE sessions SET note=? WHERE id=?", value or None, sid)
    return {"note": value or None}


def init() -> None:
    """A live, read-only example for an empty Results page (SR24). It uses a
    shelf mock but never contributes to learner or crowd statistics."""
    if db.one("SELECT 1 FROM sessions WHERE id='sample-section'"):
        return
    from .api_tests import MOCKS
    if not MOCKS:
        return
    mid, form = next(iter(MOCKS.items()))
    m1, m2 = form["module1"], form["module2_upper"]
    questions = m1 + m2
    answers = {}
    for n, q in enumerate(questions):
        if n % 4:
            answers[q["id"]] = "ABCD".index(q["answer"]) if q["type"] == "mcq" else q["answer"]
        elif q["type"] == "mcq":
            answers[q["id"]] = ("ABCD".index(q["answer"]) + 1) % 4
    result = scoring.score(questions, answers)
    result.update({"mock": mid, "route": "upper", "module1": {"right": 16, "asked": len(m1)}})
    result["estimate"] = scoring.section_score(result, "upper")
    stamp = "2026-09-01T12:00:00+00:00"
    db.run("INSERT OR IGNORE INTO sessions(id,kind,mock_id,module,learner,started,finished,answers,result,route,module1)"
           " VALUES (?,?,?,?,?,?,?,?,?,?,?)", "sample-section", "mock", mid, 2, "sample:report", stamp,
           "2026-09-01T13:10:00+00:00", json.dumps(answers), json.dumps(result), "upper",
           json.dumps({"right": 16, "asked": len(m1)}))


# ------------------------------------------------------------------ compare and briefing

def compare(sid: str, other: str | None, x_learner: str | None) -> dict:
    row, learner = _read_sitting(sid, x_learner)
    if not learner or row["learner"] != learner:
        raise HTTPException(403, "compare is private to the learner")
    cfg = _cfg(row)
    other = other or cfg.get("twin_of") or cfg.get("rematch_of") or \
        (cfg.get("custom") or {}).get("from_session")
    if not other:
        raise HTTPException(404, "no sitting to compare")
    before, owner = _read_sitting(other, x_learner)
    if owner != learner or before["learner"] != learner:
        raise HTTPException(403, "compare is private to the learner")
    old, new = core(before), core(row)
    first = {i["qid"]: i for i in old["items"]}
    buckets: dict[str, list[dict]] = defaultdict(list)
    for i in old["items"]:
        buckets[i["q"].get("key")].append(i)
    used = set()
    slots = []
    counts = Counter()
    led_old, led_new = estimate.ledger(other), estimate.ledger(sid)
    fixed_pts = slipped_pts = 0.0
    for i in new["items"]:
        q = i["q"]
        prior = first.get(q.get("slot_of"))
        if prior is None:
            prior = next((x for x in buckets.get(q.get("key"), []) if x["qid"] not in used), None)
        if prior is None or prior["qid"] in used:
            continue
        used.add(prior["qid"])
        was, now_right = prior["status"] == "correct", i["status"] == "correct"
        change = "held" if was and now_right else "fixed" if now_right else \
            "slipped" if was else "still_missing"
        counts[change] += 1
        same_trap = bool(not was and not now_right and prior["attempt"] and i["attempt"]
                         and prior["attempt"]["norm"] and
                         prior["attempt"]["norm"] == i["attempt"]["norm"])
        counts["same_trap"] += int(same_trap)
        fixed_pts += (led_old or {}).get("per_q", {}).get(prior["qid"], {}).get("pts", 0) if change == "fixed" else 0
        slipped_pts += (led_new or {}).get("per_q", {}).get(i["qid"], {}).get("pts", 0) if change == "slipped" else 0
        old_second, new_second = second_block(old), second_block(new)
        left = hold_back(old_second, {"id": prior["qid"], "status": prior["status"], "ms": prior["ms"],
                                      "mistake": prior["attempt"]["reason"] if prior["attempt"] else None})
        right = hold_back(new_second, {"id": i["qid"], "status": i["status"], "ms": i["ms"],
                                       "mistake": i["attempt"]["reason"] if i["attempt"] else None})
        slots.append({"n": i["n"], "module": i["module"], "template": q.get("key"),
                      "type_name": q.get("topic_name"), "tier": q.get("difficulty"),
                      "then": {"qid": prior["qid"], **left}, "now": {"qid": i["qid"], **right},
                      "change": change, "same_trap": same_trap})
    seq = seqs(learner)
    old_band, new_band = _band(old["result"]), _band(new["result"])
    old_ms, new_ms = sitting_ms(old), sitting_ms(new)
    return {"subject": _subject(row), "with": {"id": other, "seq": seq.get(other),
            "label": kind_name(before), "finished": before["finished"], "estimate": old_band},
            "paired": len(slots), "unpaired": len(new["items"]) - len(slots), "slots": slots,
            "counts": {k: counts[k] for k in ("fixed", "slipped", "still_missing", "same_trap", "held")},
            "band": {"then": old_band, "now": new_band,
                     "delta": _mid(new_band) - _mid(old_band) if old_band and new_band else None},
            "ms_per_q": {"then": round(old_ms / len(old["items"])) if old_ms and old["items"] else None,
                         "now": round(new_ms / len(new["items"])) if new_ms and new["items"] else None},
            "explained": {"fixed_pts": round(fixed_pts, 2), "slipped_pts": round(slipped_pts, 2)},
            "skills": [], "module2": "different_route" if before["route"] != row["route"] else
            "paired" if len(slots) > 22 else "none"}


@router.get("/api/session/{sid}/compare")
def get_compare(sid: str, with_sid: str | None = Query(default=None, alias="with"),
                x_learner: str | None = Header(default=None)) -> dict:
    return compare(sid, with_sid, x_learner)


@router.get("/api/session/{sid}/briefing")
def briefing(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    row, learner = _read_sitting(sid, x_learner)
    if learner != row["learner"]:
        raise HTTPException(403, "briefing is private to the learner")
    c = core(row)
    rules = []
    names = [i["q"].get("key") for i in c["items"] if i["q"].get("key")]
    if names:
        holes = ",".join("?" for _ in set(names))
        rules = [dict(r) for r in db.rows("SELECT template,note,at FROM notes WHERE learner=? AND seed=-1"
                                         f" AND template IN ({holes}) ORDER BY at DESC LIMIT 5",
                                         learner, *sorted(set(names)))]
    ms = [i for i in c["items"] if i["ms"] and i["status"] in MISSES]
    slow = sorted(ms, key=lambda i: i["ms"], reverse=True)[:2]
    pace = [f"{i['label']} took {round(i['ms'] / 1000)} seconds. Aim for about 95 seconds a question."
            for i in slow]
    changes = sum(len(i["st"].get("trail") or []) > 1 for i in c["items"])
    return {"id": sid, "label": kind_name(row), "seq": seqs(learner).get(sid),
            "rules": rules, "pace": pace,
            "changes": f"You changed {changes} answers; change only with a reason." if changes else None,
            "route": f"Module 1 decides the route: {math.ceil(scoring.ROUTE_UP_AT * 22)} of 22 sends you to the harder Module 2."
            if row["kind"] in SECTIONS else None}
