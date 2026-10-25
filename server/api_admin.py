"""The students board for the admin: who is on the platform and how each one is doing.

Behind SATF_ADMIN_TOKEN (sent as X-Admin, like the reports inbox):
  GET /api/admin/students        one row per student
  GET /api/admin/students/{id}   everything about one student, grouped
  GET /api/admin/access          the approved list for email sign-in
  POST /api/admin/access         add pasted addresses to it
Only the approved list is written here; the rest reads what the app already records.
"""

from __future__ import annotations

import datetime as dt
import hmac
import json
import os
import re

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from . import account, api_me, api_tests, db, progress, scoring

router = APIRouter()

COUNTED = progress.COUNTED
TESTS = ("mock", "section", "module", "paper", "twin", "custom", "diagnostic", "shared")
SKIP = ("gone:", "sample:")


def _admin(x_admin: str | None) -> None:
    want = os.environ.get("SATF_ADMIN_TOKEN")
    if not want:
        raise HTTPException(404, "Not Found")
    if not x_admin or not hmac.compare_digest(x_admin.encode(), want.encode()):
        raise HTTPException(403, "wrong admin token")


def _minutes(ms) -> int:
    return round((ms or 0) / 60000)


@router.get("/api/admin/students")
def students(x_admin: str | None = Header(default=None)) -> dict:
    _admin(x_admin)
    att = {r["learner"]: r for r in db.rows(
        f"SELECT learner, COUNT(*) n, SUM(correct) rt, MAX(at) last, MIN(at) first, SUM(MIN(COALESCE(ms,0),600000)) ms,"
        f" COUNT(DISTINCT substr(at,1,10)) days FROM attempts WHERE {COUNTED} GROUP BY learner")}
    tests = {r["learner"]: r["n"] for r in db.rows(
        f"SELECT learner, COUNT(*) n FROM sessions WHERE finished IS NOT NULL AND abandoned IS NULL"
        f" AND kind IN ({','.join('?' * len(TESTS))}) GROUP BY learner", *TESTS)}
    mistakes = {r["learner"]: r["n"] for r in db.rows(
        "SELECT learner, COUNT(*) n FROM traps WHERE closed IS NULL GROUP BY learner")}
    emails = {}
    for r in db.rows("SELECT learner, email, verified FROM users WHERE learner IS NOT NULL ORDER BY verified, created"):
        emails[r["learner"]] = r["email"]
    out = []
    guardians = {r["parent"] for r in db.rows("SELECT DISTINCT parent FROM guardians")}
    for l in db.rows("SELECT id, name, handle, country, created, target, exam_date, rating, rated FROM learners"):
        if l["id"].startswith(SKIP):
            continue
        a = att.get(l["id"])
        if l["id"] in guardians and not a:
            continue                       # a parent's own account, not a student
        t = tests.get(l["id"], 0)
        if not a and not t and not emails.get(l["id"]) and not l["name"]:
            continue                       # opened the site and did nothing: not a student yet
        n = a["n"] if a else 0
        out.append({"id": l["id"], "name": l["name"] or l["handle"] or "", "handle": l["handle"], "email": emails.get(l["id"]),
                    "country": l["country"], "joined": l["created"], "last": a["last"] if a else None,
                    "answers": n, "accuracy": round((a["rt"] or 0) / n, 3) if n else None,
                    "minutes": _minutes(a["ms"]) if a else 0, "days": a["days"] if a else 0, "tests": t,
                    "open_mistakes": mistakes.get(l["id"], 0), "target": l["target"], "exam_date": l["exam_date"],
                    "rating": round(l["rating"]) if l["rated"] else None})
    out.sort(key=lambda x: x["last"] or x["joined"] or "", reverse=True)
    week = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)).isoformat()
    return {"students": out, "total": len(out), "active_7d": sum(1 for x in out if (x["last"] or "") >= week),
            "answers": sum(x["answers"] for x in out)}


@router.get("/api/admin/students/{learner}")
def student(learner: str, x_admin: str | None = Header(default=None)) -> dict:
    _admin(x_admin)
    l = db.one("SELECT * FROM learners WHERE id=?", learner)
    if l is None:
        raise HTTPException(404, "no such student")
    return detail(l)


def detail(l) -> dict:
    """Everything about one learner row, grouped. The admin page shows it whole, the parent view a part."""
    learner = l["id"]
    users = [dict(r) for r in db.rows(
        "SELECT email, verified, created, last_login FROM users WHERE learner=? ORDER BY verified DESC, created", learner)]
    plan = db.one("SELECT 1 FROM plans WHERE learner=? LIMIT 1", learner) if _has_table("plans") else None
    profile = {"id": l["id"], "name": l["name"], "handle": l["handle"], "country": l["country"], "joined": l["created"],
               "email": users[0]["email"] if users else None, "email_verified": bool(users and users[0]["verified"]),
               "last_login": users[0]["last_login"] if users else None, "exam_date": l["exam_date"], "target": l["target"],
               "current": l["current"], "rw_target": l["rw_target"], "rw_now": l["rw_now"],
               "daily_minutes": l["minutes"], "has_plan": bool(plan or l["plan"]), "board": l["board"]}

    tot = db.one(f"SELECT COUNT(*) n, SUM(correct) rt, MIN(at) first, MAX(at) last, SUM(MIN(COALESCE(ms,0),600000)) ms,"
                 f" COUNT(DISTINCT substr(at,1,10)) days,"
                 f" SUM(difficulty='hard') hard, SUM(difficulty='hard' AND correct=1) hard_rt,"
                 f" SUM(guess) guesses, SUM(hints) hints FROM attempts WHERE learner=? AND {COUNTED}", learner)
    n = tot["n"] or 0
    activity = {"answers": n, "accuracy": round((tot["rt"] or 0) / n, 3) if n else None, "first": tot["first"], "last": tot["last"],
                "minutes": _minutes(tot["ms"]), "active_days": tot["days"] or 0,
                "hard_answers": tot["hard"] or 0, "hard_accuracy": round((tot["hard_rt"] or 0) / tot["hard"], 3) if tot["hard"] else None,
                "hints_used": tot["hints"] or 0}
    since = (dt.date.today() - dt.timedelta(days=29)).isoformat()
    by_day = {r["d"]: r for r in db.rows(
        f"SELECT substr(at,1,10) d, COUNT(*) n, SUM(correct) rt FROM attempts WHERE learner=? AND {COUNTED} AND at>=? GROUP BY d", learner, since)}
    last30 = []
    for i in range(30):
        d = (dt.date.today() - dt.timedelta(days=29 - i)).isoformat()
        r = by_day.get(d)
        last30.append({"day": d, "answers": r["n"] if r else 0, "right": (r["rt"] or 0) if r else 0})
    try:
        streak = progress.days(learner, 0, 8).get("streak")
    except Exception:
        streak = None
    activity["streak"] = streak

    # both subjects' skills, by their own names and domains (an R&W row never shows its slug)
    names = {slug: (t.name, t.domain, s) for s in ("rw", "math") for slug, t in progress.topics(s).items()}
    skills = []
    for r in db.rows(
            f"SELECT topic, COUNT(*) n, SUM(correct) rt, MAX(at) last, SUM(difficulty='hard') hard, SUM(difficulty='hard' AND correct=1) hrt,"
            f" AVG(NULLIF(ms,0)) ms FROM attempts WHERE learner=? AND {COUNTED} GROUP BY topic", learner):
        nm, dom, subject = names.get(r["topic"], (r["topic"], "", "rw" if r["topic"].startswith("rw") else "math"))
        skills.append({"topic": r["topic"], "name": nm, "domain": dom, "subject": subject, "answers": r["n"], "right": r["rt"] or 0,
                       "accuracy": round((r["rt"] or 0) / r["n"], 3),
                       "hard_accuracy": round((r["hrt"] or 0) / r["hard"], 3) if r["hard"] else None, "last": r["last"],
                       "seconds": round((r["ms"] or 0) / 1000) or None})
    skills.sort(key=lambda s: (s["subject"] != "rw", s["domain"], s["accuracy"]))     # R&W first, as on the test
    activity["subjects"] = {}
    for s in ("rw", "math"):
        mine = [x for x in skills if x["subject"] == s]
        n_s = sum(x["answers"] for x in mine)
        activity["subjects"][s] = {"answers": n_s, "accuracy": round(sum(x["right"] for x in mine) / n_s, 3) if n_s else None}

    sittings = []
    for r in db.rows(
            f"SELECT id, kind, subject, cfg, started, finished, result, route, number, qstate FROM sessions WHERE learner=? AND finished IS NOT NULL"
            f" AND abandoned IS NULL AND kind IN ({','.join('?' * len(TESTS))}) ORDER BY finished DESC LIMIT 25", learner, *TESTS):
        res = json.loads(r["result"] or "{}")
        est = res.get("estimate") if isinstance(res.get("estimate"), dict) else {}
        full = (json.loads(r["cfg"] or "{}") or {}).get("full") or {}
        mins = None
        try:
            mins = round((dt.datetime.fromisoformat(r["finished"]) - dt.datetime.fromisoformat(r["started"])).total_seconds() / 60)
        except Exception:
            pass
        sittings.append({"id": r["id"], "kind": r["kind"], "subject": r["subject"] or "math", "full": full.get("id") if isinstance(full, dict) else None,
                         "number": r["number"], "finished": r["finished"], "route": r["route"],
                         "right": res.get("right"), "asked": res.get("asked"), "low": est.get("low"), "high": est.get("high"),
                         "mid": est.get("mid"), "minutes": mins, "integrity": res.get("integrity") or api_tests.integrity_of(r)})
    sittings = _full_rows(sittings)
    practice = db.one("SELECT COUNT(*) n FROM sessions WHERE learner=? AND kind='drill' AND finished IS NOT NULL", learner)["n"]

    traps = db.rows("SELECT label, topic, hits, relapses, opened, closed FROM traps WHERE learner=? ORDER BY closed IS NOT NULL, hits DESC LIMIT 40", learner)
    open_ = [dict(t) for t in traps if t["closed"] is None]
    mistakes = {"open": len(open_), "fixed": sum(1 for t in traps if t["closed"] is not None),
                "top": [{"label": t["label"], "skill": names.get(t["topic"], (t["topic"],))[0], "hits": t["hits"]} for t in open_[:8]]}

    cont = db.rows("SELECT s.contest, s.points, s.finished, c.title, c.kind FROM sessions s LEFT JOIN contests c ON c.id=s.contest"
                   " WHERE s.learner=? AND s.contest IS NOT NULL AND s.finished IS NOT NULL ORDER BY s.finished DESC LIMIT 10", learner)
    compete = {"rating": round(l["rating"]) if l["rated"] else None, "rated_sittings": l["rated"] or 0,
               "contests_played": db.one("SELECT COUNT(*) n FROM sessions WHERE learner=? AND contest IS NOT NULL AND finished IS NOT NULL", learner)["n"],
               "daily_challenges": db.one("SELECT COUNT(*) n FROM sessions WHERE learner=? AND kind='challenge' AND finished IS NOT NULL", learner)["n"],
               "recent": [{"title": c["title"] or c["contest"], "kind": c["kind"], "points": c["points"], "at": c["finished"]} for c in cont]}

    today = dt.date.today().isoformat()
    w = db.one("SELECT COUNT(*) n, SUM(reps) reps, SUM(lapses) lapses, SUM(saved) saved, SUM(due<=?) due FROM word_state WHERE learner=?", today, learner)
    words = {"touched": w["n"] or 0, "reviews": w["reps"] or 0, "lapses": w["lapses"] or 0, "saved": w["saved"] or 0, "due_now": w["due"] or 0}

    badges = [dict(r) for r in db.rows("SELECT id, MAX(tier) tier FROM earned WHERE learner=? GROUP BY id", learner)]
    reports = [dict(r) for r in db.rows("SELECT title, kind, at FROM reports WHERE learner=? ORDER BY at DESC LIMIT 5", learner)]
    parents = [{"name": r["name"], "email": r["email"], "since": r["created"]} for r in db.rows(
        "SELECT g.created, l.name, (SELECT email FROM users WHERE learner=g.parent LIMIT 1) email"
        " FROM guardians g LEFT JOIN learners l ON l.id=g.parent WHERE g.student=? ORDER BY g.created", learner)]
    return {"profile": profile, "parents": parents, "scores": api_me.scores(learner), "activity": activity, "last30": last30,
            "skills": skills, "tests": {"practice_sets": practice, "sittings": sittings},
            "mistakes": mistakes, "compete": compete, "words": words, "badges": len(badges), "reports": reports}


def _full_rows(sittings: list[dict]) -> list[dict]:
    """A full SAT is two linked sittings (cfg.full.id, R&W then Math): one row with its total and both parts.
    A full SAT stopped after R&W stays an R&W section row."""
    parts: dict[str, list[dict]] = {}
    for s in sittings:
        if s["full"]:
            parts.setdefault(s["full"], []).append(s)
    out, done = [], set()
    for s in sittings:
        both = parts.get(s["full"]) if s["full"] else None
        if not both or len(both) < 2 or {x["subject"] for x in both} != {"rw", "math"}:
            out.append(s)
            continue
        if s["full"] in done:
            continue
        done.add(s["full"])
        rw, math = (next(x for x in both if x["subject"] == k) for k in ("rw", "math"))
        mids = [x["mid"] if x["mid"] is not None else (x["low"] + x["high"]) / 2 if x["low"] is not None else None for x in (rw, math)]
        total = scoring.total_band(*mids) if None not in mids else {}
        out.append({**s, "id": rw["id"], "kind": "full", "subject": "both",
                    "finished": max(rw["finished"], math["finished"]), "right": (rw["right"] or 0) + (math["right"] or 0),
                    "asked": (rw["asked"] or 0) + (math["asked"] or 0), "low": total.get("low"), "high": total.get("high"),
                    "mid": total.get("mid"), "minutes": (rw["minutes"] or 0) + (math["minutes"] or 0) or None,
                    "parts": [{k: x[k] for k in ("id", "subject", "low", "high", "right", "asked")} for x in (rw, math)],
                    "integrity": _ig_sum(rw.get("integrity"), math.get("integrity"))})
    return out


IG_COUNTS = ("away_n", "away_ms", "blur_n", "blur_ms", "copy_n", "paste_n", "fs_n", "left_n", "left_ms")


def _ig_sum(*parts) -> dict:
    """Both sections of a full SAT as one integrity record: counts and times added, reasons kept in order."""
    parts = [p for p in parts if p]
    out = {k: sum(p.get(k) or 0 for p in parts) for k in IG_COUNTS}
    out["why"] = list(dict.fromkeys(w for p in parts for w in p.get("why") or []))
    out["flagged"] = any(p.get("flagged") for p in parts)
    out["events"] = [e for p in parts for e in p.get("events") or []]
    return out


def _has_table(name: str) -> bool:
    return bool(db.one("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", name))


# ------------------------------------------------------------------ access (the approved list)

@router.get("/api/admin/access")
def access(x_admin: str | None = Header(default=None)) -> dict:
    """Every approved address, newest first, and whether it has signed in yet."""
    _admin(x_admin)
    joined = {r["e"] for r in db.rows("SELECT lower(email) e FROM users WHERE email IS NOT NULL AND learner IS NOT NULL")}
    rows = [{"email": r["email"], "name": r["name"] or "", "group": r["grp"] or "", "added": r["added"],
             "joined": r["email"] in joined}
            for r in db.rows("SELECT email, name, grp, added FROM email_allow ORDER BY added DESC, email")]
    return {"total": len(rows), "joined": sum(r["joined"] for r in rows), "rows": rows}


class AccessIn(BaseModel):
    text: str = Field(min_length=1, max_length=200_000)


_LETTER = re.compile(r"[^\W\d_]")


@router.post("/api/admin/access")
def give_access(body: AccessIn, x_admin: str | None = Header(default=None)) -> dict:
    """A pasted roster, one person a line: an address, optionally with a name and a group, split by
    commas, semicolons or tabs (a spreadsheet or document table pastes tabs, often with a row number
    and a phone too: the address is the part with an @, the name and group the first parts with
    letters). New addresses are added; listed ones are left exactly as they were."""
    _admin(x_admin)
    out: dict[str, list[str]] = {"added": [], "already": [], "invalid": []}
    for line in body.text.splitlines():
        parts = [p.strip() for p in re.split(r"[\t,;]", line) if p.strip()]
        if not parts:
            continue
        email = next((p for p in parts if "@" in p), parts[0])
        words = [p for p in parts if p is not email and _LETTER.search(p)]
        got = account.allow(email, *(words + ["", ""])[:2], update=False)
        out[got].append(email.strip().lower().rstrip(".") if got != "invalid" else line.strip()[:80])
    return {**out, "total": db.one("SELECT COUNT(*) n FROM email_allow")["n"]}


# ------------------------------------------------------------------ tests and integrity (proctoring)

@router.get("/api/admin/tests")
def tests(hours: int = 24, x_admin: str | None = Header(default=None)) -> dict:
    """Every test sitting started in the last `hours` (live ones too), with who sat it, where it stands and
    its integrity: flagged first, then the most time outside the test. A teacher's view during a mock."""
    _admin(x_admin)
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=max(1, min(hours, 24 * 30)))).isoformat(timespec="seconds")
    names = {r["id"]: r["name"] for r in db.rows("SELECT id, name FROM learners")}
    emails = {r["learner"]: r["email"] for r in db.rows("SELECT learner, email FROM users WHERE learner IS NOT NULL ORDER BY verified, created")}
    rows = []
    for r in db.rows(f"SELECT * FROM sessions WHERE started>=? AND kind IN ({','.join('?' * len(TESTS))})"
                     " AND learner IS NOT NULL ORDER BY started DESC LIMIT 1000", since, *TESTS):
        if (r["learner"] or "").startswith(SKIP):
            continue
        res = json.loads(r["result"] or "{}") if r["finished"] else {}
        cfg = json.loads(r["cfg"] or "{}") or {}
        est = res.get("estimate") if isinstance(res.get("estimate"), dict) else {}
        status = ("discarded" if r["abandoned"] else "finished" if r["finished"]
                  else f"module {r['module'] or 1}" if r["module_started"] else "not begun")
        full = cfg.get("full") if isinstance(cfg.get("full"), dict) else {}
        rows.append({"id": r["id"], "learner": r["learner"], "name": names.get(r["learner"]) or "",
                     "email": emails.get(r["learner"]) or "", "kind": api_tests.kind_label(r), "subject": r["subject"] or "math",
                     "full": full.get("number") if full else None, "started": r["started"], "finished": r["finished"],
                     "status": status, "right": res.get("right"), "asked": res.get("asked"),
                     "low": est.get("low"), "high": est.get("high"),
                     "integrity": res.get("integrity") or api_tests.integrity_of(r)})
    rows.sort(key=lambda x: (not x["integrity"]["flagged"], -x["integrity"]["left_ms"], -(dt.datetime.fromisoformat(x["started"]).timestamp())))
    return {"hours": hours, "rows": rows, "flagged": sum(x["integrity"]["flagged"] for x in rows),
            "live": sum(x["status"].startswith("module") for x in rows)}
