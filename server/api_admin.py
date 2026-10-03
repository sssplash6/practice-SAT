"""The students board for the admin: who is on the platform and how each one is doing.

Two read-only endpoints behind SATF_ADMIN_TOKEN (sent as X-Admin, like the reports inbox):
  GET /api/admin/students        one row per student
  GET /api/admin/students/{id}   everything about one student, grouped
Nothing here writes. It only reads what the app already records.
"""

from __future__ import annotations

import datetime as dt
import hmac
import json
import os

from fastapi import APIRouter, Header, HTTPException

from . import db, progress

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
               "current": l["current"], "daily_minutes": l["minutes"], "has_plan": bool(plan or l["plan"]),
               "board": l["board"]}

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

    names = {slug: (t.name, t.domain) for slug, t in progress.topics().items()}
    skills = []
    for r in db.rows(
            f"SELECT topic, COUNT(*) n, SUM(correct) rt, MAX(at) last, SUM(difficulty='hard') hard, SUM(difficulty='hard' AND correct=1) hrt,"
            f" AVG(NULLIF(ms,0)) ms FROM attempts WHERE learner=? AND {COUNTED} GROUP BY topic", learner):
        nm, dom = names.get(r["topic"], (r["topic"], ""))
        skills.append({"topic": r["topic"], "name": nm, "domain": dom, "answers": r["n"], "accuracy": round((r["rt"] or 0) / r["n"], 3),
                       "hard_accuracy": round((r["hrt"] or 0) / r["hard"], 3) if r["hard"] else None, "last": r["last"],
                       "seconds": round((r["ms"] or 0) / 1000) or None})
    skills.sort(key=lambda s: (s["domain"], s["accuracy"]))

    sittings = []
    for r in db.rows(
            f"SELECT id, kind, started, finished, result, route, number FROM sessions WHERE learner=? AND finished IS NOT NULL AND abandoned IS NULL"
            f" AND kind IN ({','.join('?' * len(TESTS))}) ORDER BY finished DESC LIMIT 25", learner, *TESTS):
        res = json.loads(r["result"] or "{}")
        est = res.get("estimate") if isinstance(res.get("estimate"), dict) else {}
        mins = None
        try:
            mins = round((dt.datetime.fromisoformat(r["finished"]) - dt.datetime.fromisoformat(r["started"])).total_seconds() / 60)
        except Exception:
            pass
        sittings.append({"id": r["id"], "kind": r["kind"], "number": r["number"], "finished": r["finished"], "route": r["route"],
                         "right": res.get("right"), "asked": res.get("asked"), "low": est.get("low"), "high": est.get("high"), "minutes": mins})
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
    return {"profile": profile, "parents": parents, "activity": activity, "last30": last30, "skills": skills, "tests": {"practice_sets": practice, "sittings": sittings},
            "mistakes": mistakes, "compete": compete, "words": words, "badges": len(badges), "reports": reports}


def _has_table(name: str) -> bool:
    return bool(db.one("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", name))
