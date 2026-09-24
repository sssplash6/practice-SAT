"""GET /api/shell: what the chrome shows on every page, in one call.

Shell §2.12 and §3.1.5, with shell-me.md override 16 and the §2.10 parts
registry: every module in PARTS may define shell_part(learner, tz) -> dict,
merged over the defaults here once that module exists. The figures that are
F4's (streak, today, mistakes, saved, resume, prefs) are read here from the
one function each has, so the chrome and the pages can never disagree.

Classes are not built (v2-decisions 5): no role line, no assignments.
"""

from __future__ import annotations

import datetime as dt
import json
import logging

from fastapi import APIRouter, Depends, Header, HTTPException

from . import challenge, daily, db, progress, satdates
from .api_me import due_left, per_session, profile
from .deps import TEST_KINDS, is_retired, learner_of, part, tz_of

log = logging.getLogger("satf")
router = APIRouter()

# §2.10: plan (the plan meta and the Today card's day), compete (the challenge,
# closing_soon), reports (report_replies), achievements (new.achievements),
# account (inbox, goals), words (words due), review (Review's own counts).
PARTS = ("plan", "compete", "reports", "achievements", "account", "words", "review")
RESUME_TESTS = ("mock", "module", "section", "custom", "paper")
RESUME_DRILL_HOURS = 24


def mask(email: str | None) -> str | None:
    """d•••@gmail.com"""
    if not email or "@" not in email:
        return None
    name, _, domain = email.partition("@")
    return f"{name[:1]}•••@{domain}"


def _merge(base: dict, extra: dict) -> dict:
    """A part's keys win; a dict under a key merges one level down, so
    achievements can fill new.achievements without replacing new."""
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = {**base[k], **v}
        else:
            base[k] = v
    return base


def _domains(learner: str) -> tuple[dict, dict]:
    """U22: each domain's mastery, 0 to 1, in progress.DOMAINS order, per subject."""
    board = progress.board(learner)
    out = []
    for d in progress.DOMAINS:
        ms = [t["mastery"] for t in board.values() if t["domain"] == d]
        out.append(round(sum(ms) / len(ms), 3) if ms else 0.0)
    return {"math": out}, board


def _avatar(learner: str, choice: str | None, board: dict) -> dict:
    """U22: a topic glyph (ringed once that skill is Strong or its badge is
    earned) or the living mark, which is the default."""
    if not choice:
        return {"kind": "mark", "glyph": None, "ring": False}
    strong = (board.get(choice) or {}).get("mastery", 0) >= progress.STRONG
    earned = db.one("SELECT 1 FROM earned WHERE learner=? AND id=?", learner, choice)
    return {"kind": "glyph", "glyph": choice, "ring": bool(strong or earned)}


def _resume(learner: str) -> dict | None:
    """The newest unfinished test with time left (paused ones included), or a
    practice set started in the last 24 h with an answer; never a quick or an
    inline sitting, and never the challenge (Compete's meta covers it)."""
    from .api_tests import mock_module, questions_of, remaining
    marks = ",".join("?" for _ in RESUME_TESTS)
    for r in db.rows(f"SELECT * FROM sessions WHERE learner=? AND finished IS NULL AND abandoned IS NULL"
                     f" AND kind IN ({marks}) ORDER BY started DESC LIMIT 5", learner, *RESUME_TESTS):
        cfg = json.loads(r["cfg"] or "{}")
        try:
            qs = mock_module(r) if r["kind"] == "mock" else questions_of(r)
            left = None if cfg.get("timed") is False else remaining(r)
        except (KeyError, TypeError, ValueError):
            continue
        if left == 0 and not r["paused_at"]:
            continue
        ids = {q["id"] for q in qs}
        answered = sum(1 for k in db.load_answers(r) if k in ids)
        return {"id": r["id"], "kind": r["kind"], "answered": answered, "total": len(qs),
                "seconds_left": left, "paused": bool(r["paused_at"]), "href": f"/test/?s={r['id']}"}
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=RESUME_DRILL_HOURS)).isoformat()
    for r in db.rows("SELECT * FROM sessions WHERE learner=? AND kind='drill' AND finished IS NULL"
                     " AND abandoned IS NULL AND started>=? ORDER BY started DESC LIMIT 10", learner, since):
        cfg = json.loads(r["cfg"] or "{}")
        answered = len(db.load_answers(r))
        if cfg.get("inline") or cfg.get("source") == "quick" or not answered:
            continue
        return {"id": r["id"], "kind": "drill", "answered": answered, "total": cfg.get("total"),
                "seconds_left": None, "paused": bool(r["paused_at"]),
                "href": f"/practice/session/?id={r['id']}"}
    return None


def _newest_report(learner: str) -> str | None:
    for r in db.rows("SELECT id, cfg FROM sessions WHERE learner=? AND finished IS NOT NULL"
                     " AND abandoned IS NULL ORDER BY finished DESC LIMIT 10", learner):
        if not json.loads(r["cfg"] or "{}").get("inline"):
            return r["id"]
    return None


def _device(token: str) -> dict:
    if token.startswith("d:"):
        row = db.one("SELECT method, session_only, expires FROM devices WHERE token=?", token)
        if row:
            return {"method": row["method"], "session_only": bool(row["session_only"]), "expires": row["expires"]}
    return {"method": "code", "session_only": False, "expires": None}


def shell(learner: str, tz: int, token: str) -> dict:
    p = profile(learner, tz)
    d = progress.days(learner, tz)
    line = d["recent"][-1]
    today = dt.date.fromisoformat(d["today"])
    acct = p["account"]
    domains, board = _domains(learner)
    answered = db.one("SELECT COUNT(*) AS n FROM attempts WHERE learner=?", learner)["n"]

    exam = None
    if p["exam_date"]:
        exam = {"date": p["exam_date"], "days": (dt.date.fromisoformat(p["exam_date"]) - today).days}
    has_plan = bool(p["plan"] or (p["exam_date"] and p["minutes"] and p["days"]))
    plan = None
    if has_plan:
        kind = "exam" if p["exam_date"] == d["today"] else "rest" if line["rest"] else "practice"
        plan = {"exam_date": p["exam_date"], "minutes": p["minutes"], "days": p["days"], "tests": p["tests"],
                "per_session": per_session(p), "target": p["target"], "kind": kind, "done": None}
    tested = any(progress._local_day(r["finished"], tz) == today
                 for r in db.rows("SELECT finished FROM sessions WHERE learner=? AND finished IS NOT NULL"
                                  f" AND kind IN ({','.join('?' for _ in TEST_KINDS)})", learner, *TEST_KINDS))

    review = db.one("SELECT COUNT(*) AS open, SUM(owed=1) AS half FROM traps WHERE learner=? AND closed IS NULL",
                    learner)
    words_due = db.one("SELECT COUNT(*) AS n FROM word_state WHERE learner=? AND due<=?", learner, d["today"])["n"]
    day = daily.today(tz)
    mine = db.one("SELECT finished FROM sessions WHERE kind='challenge' AND learner=? AND day=?", learner, day)
    b = challenge.board(day, learner, limit=0)
    closing = part("compete", "closing_soon")

    out = {
        "me": {"name": p["name"], "handle": p["handle"], "label": p["name"] or p["handle"] or challenge.handle(learner, None),
               "avatar": _avatar(learner, p["avatar"], board), "domains": domains, "board": p["board"],
               "linked": acct["linked"], "email_masked": mask(acct["email"]), "since": acct["since"]},
        "answered": answered,
        "streak": d["streak"], "best_streak": d["best_streak"], "spares": d["spares"],
        "today": {"day": d["today"], "questions": line["questions"], "right": line["right"],
                  "minutes": line["minutes"], "words": line["words"], "rest": line["rest"],
                  "goal": {"minutes": p["minutes"], "questions": per_session(p)} if p["minutes"] else None,
                  "done": None, "exam": exam, "contest": closing(learner, tz) if closing else []},
        "plan": plan,
        "tested_today": tested,
        "mistakes": review["open"],
        "review": {"open": review["open"], "half": review["half"] or 0,
                   "due_left": due_left(learner, tz, p["prefs"])},
        "saved": db.one("SELECT COUNT(*) AS n FROM saved WHERE learner=?", learner)["n"],
        "words": {"due": words_due},
        "challenge": {"day": day, "started": bool(mine), "done": bool(mine and mine["finished"]),
                      "rank": b["you"]["rank"] if b["you"] else None, "players": b["players"]},
        "resume": _resume(learner),
        "newest_report": _newest_report(learner),
        "report_replies": 0,
        "new": {"achievements": []},
        "next": [],
        "goals": [],
        "inbox": 0,
        "registration": satdates.registration(p["exam_date"], p["prefs"].get("registered"), today),
        "device": _device(token),
        "dates": satdates.dates(today),
        "prefs": p["prefs"], "pref_source": p["pref_source"], "stage": p["stage"],
    }
    queue = part("next", "queue")
    if queue:
        out["next"] = queue(learner, tz, limit=3)[:3]
    for name in PARTS:
        fn = part(name, "shell_part")
        if fn is None:
            continue
        try:
            _merge(out, fn(learner, tz))
        except Exception:                   # one broken part must not take the nav down
            log.exception("shell_part of %s failed", name)
    return out


@router.get("/api/shell")
def get_shell(x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    """{retired: true} in place of the data for a rotated-away code, a
    revoked or expired device token, or an ended shared-computer session."""
    if is_retired(x_learner):
        return {"retired": True}
    try:
        learner = learner_of(x_learner)
    except HTTPException as e:
        if e.status_code == 401 and isinstance(e.detail, dict) and e.detail.get("retired"):
            return {"retired": True}
        raise
    return shell(learner, x_tz, (x_learner or "").strip())
