"""The daily challenge: today's ten, one sitting each, and the board."""

from __future__ import annotations

import datetime as dt
import json
import logging
import secrets
import statistics
import threading
from collections import Counter

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import RedirectResponse

from . import blueprint, challenge, compete, daily, db, deps, drill, prefs, practice, progress
from .deps import DATE_OK, LEARNER_OK, SECONDS_PER_QUESTION, learner_of, tz_of

log = logging.getLogger("satf")
router = APIRouter()
_START_LOCKS = tuple(threading.Lock() for _ in range(64))


def challenge_row(learner: str, day: str):
    return db.one("SELECT * FROM sessions WHERE kind='challenge' AND learner=? AND day=?", learner, day)


@router.get("/api/challenge")
def get_challenge(x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    day = daily.today(x_tz)
    row = challenge_row(learner, day)
    b = challenge.board(day, learner, limit=5)
    return {"day": day, "count": challenge.CHALLENGE_SIZE,
            "seconds": challenge.CHALLENGE_SIZE * SECONDS_PER_QUESTION,
            "session": row["id"] if row else None,
            "finished": bool(row and row["finished"]),
            "board": b}


@router.post("/api/challenge/start")
def start_challenge(x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    """Today's ten, one sitting each. Coming back resumes it; it never restarts."""
    learner = learner_of(x_learner)
    day = daily.today(x_tz)
    row = challenge_row(learner, day)
    if row is None:
        qs = challenge.challenge(day)
        sid = secrets.token_urlsafe(16)
        drill.create(learner, sid, list(dict.fromkeys(q["topic"] for q in qs)), len(qs), None, True,
                     "challenge", items=[[q["key"], q["seed"]] for q in qs],
                     kind="challenge", fixed=True, day=day)
        row = challenge_row(learner, day)           # this start's, or one made at the same moment
        log.info("challenge %s started by %s", day, learner[:12])
    if row["finished"]:
        return {**drill.state(row), "done": True}
    return {**drill.state(row), **drill.next_question(row)}


@router.get("/api/challenge/board")
def challenge_board(day: str | None = None, x_learner: str | None = Header(default=None),
                    x_tz: int = Depends(tz_of)) -> dict:
    if day and not DATE_OK.match(day):
        raise HTTPException(422, "day is YYYY-MM-DD")
    if day:
        try:
            requested = dt.date.fromisoformat(day)
        except ValueError:
            raise HTTPException(422, "day is YYYY-MM-DD") from None
        today = dt.datetime.now(dt.timezone.utc).date()
        if requested < today - dt.timedelta(days=3 * 366) or requested > today + dt.timedelta(days=1):
            raise HTTPException(422, "day is outside the challenge board range")
    me = x_learner.strip() if x_learner and LEARNER_OK.match(x_learner.strip()) else None
    return challenge.board(day or daily.today(x_tz), me)


def _viewer(x_learner: str | None) -> str | None:
    return learner_of(x_learner) if x_learner else None


def _sitting(cid: str, learner: str):
    return db.one("SELECT * FROM sessions WHERE contest=? AND learner=? ORDER BY started DESC LIMIT 1", cid, learner)


def _meta(row, learner: str | None, tz: int = 0, race: str | None = None) -> dict:
    compete.private_access(row, learner)
    now = compete._iso(compete._now())
    own = _sitting(row["id"], learner) if learner else None
    if own and own["finished"]:
        compete.finish_contest(own)
        own = db.one("SELECT * FROM sessions WHERE id=?", own["id"])
    entries = compete.board(row["id"], learner, limit=1)
    all_scores = [r["points"] for r in db.rows("SELECT points FROM sessions WHERE contest=?"
                                                  " AND ranked=1 AND finished IS NOT NULL AND points IS NOT NULL",
                                                  row["id"])]
    slots = (compete._json(row["spec"], {}) or {}).get("slots", [])
    own_result = compete._json(own["result"], {}) if own else {}
    expected = (own_result or {}).get("par") or compete.par(learner, slots)
    ladder = [{"slot": n, "topic": practice.topic_of(key),
               "skill": blueprint.kinds()[key]["skill"],
               "tier": tier, "format": fmt, "chance": expected["cells"][n - 1]["chance"],
               **({"template": key} if own else {})}
              for n, (key, tier, fmt) in enumerate(slots, 1)]
    me = {"session": own["id"] if own else None,
          "status": "finished" if own and own["finished"] else "progress" if own else "new",
          "answered": len(compete._json(own["answers"], {}) or {}) if own else 0,
          "clock": ({"used": round((compete._now() - dt.datetime.fromisoformat(own["started"])).total_seconds()),
                     "left": max(0, (compete._json(own["cfg"], {}) or {}).get("seconds", 240) -
                                 round((compete._now() - dt.datetime.fromisoformat(own["started"])).total_seconds())),
                     "running": not bool(own["finished"])} if row["kind"] == "words" else
                    compete.clock(own)) if own else None,
          "result": compete._json(own["result"], {}) if own else None,
          "ranked": bool(own["ranked"]) if own else None,
          "why": own["unranked_why"] if own else None,
          "par": {k: v for k, v in expected.items() if k not in ("cells", "sd")}}
    if own:
        flags = (compete._json(own["cfg"], {}) or {}).get("flags", {})
        me["confirm"] = {"due": sum(f.get("status") == "pending" for f in flags.values()),
                         "next": (compete._json(own["cfg"], {}) or {}).get("confirm_active")}
        me["followup"] = compete.rematch_status(own)
    if len(all_scores) >= 10:
        lower = expected["base"] - expected["sd"]
        upper = expected["base"] + expected["sd"]
        me["forecast"] = {"lo": 1 + sum(score > upper for score in all_scores),
                          "hi": 1 + sum(score > lower for score in all_scores), "of": len(all_scores)}
    else:
        me["forecast"] = None
    entrants = None
    if row["kind"] == "private" and learner in compete.private_members(row["id"]):
        entrants = [{**compete._identity(person, learner, private=True, subject=row["subject"]),
                     "status": "finished" if (s := _sitting(row["id"], person)) and s["finished"]
                     else "progress" if s else "new"} for person in compete.private_members(row["id"])]
    status = "upcoming" if row["opens"] > now else "closed" if row["closes"] <= now else "live"
    if row["kind"] == "daily":                  # daily-YYYY-MM-DD, R&W's with -rw after the date
        status = "live" if row["id"][6:16] == compete.local_day(tz).isoformat() else "closed"
    race_data = compete.race_choice(row["id"], learner, race) if race and learner else None
    if race and not learner:
        raise HTTPException(400, "send a learner code to race")
    return {"id": row["id"], "kind": row["kind"], "title": row["title"],
            "subject": row["subject"], "opens": row["opens"], "closes": row["closes"],
            "count": row["count"], "seconds": row["seconds"],
            "spec": compete._json(row["spec"], {}), "ladder": ladder,
            "status": status,
            "field": {"players": entries["players"],
                      "sitting_now": db.one("SELECT COUNT(*) AS n FROM sessions WHERE contest=?"
                                            " AND finished IS NULL", row["id"])["n"],
                      "median_points": statistics.median(all_scores) if all_scores else None,
                      "best": max(all_scores) if all_scores else None},
            "me": me, "entrants": entrants,
            "race": {k: v for k, v in race_data.items() if k not in ("target", "sid")} if race_data else None,
            "series": row["series"], "round": row["round"],
            # a private contest's invite code goes to its members, so any of them can pass it on
            **({"code": row["code"] or (db.one("SELECT code FROM contests WHERE id=?", row["series"]) or {}).get("code"),
                "owner": bool(learner) and row["owner"] == learner}
               if row["kind"] == "private" and learner in compete.private_members(row["id"]) else {})}


@router.get("/api/compete")
def compete_home(subject: str | None = None, x_learner: str | None = Header(default=None),
                 x_tz: int = Depends(tz_of)) -> dict:
    """The hub for one subject: its Daily, your rating and ranks in it, its board (the streak is shared)."""
    learner = learner_of(x_learner)
    subject = deps.subject_param(subject)
    contests = compete.ensure(tz=x_tz)
    daily_row = compete.contest("daily" if subject == "math" else "daily-rw", x_tz)
    now = compete._iso(compete._now())
    ranked = compete.rank_snapshot(learner, x_tz, subject)
    next_sat = next((d for d in compete.SAT_DATES if d >= compete.local_day(x_tz).isoformat()), None)
    return {"daily": _meta(daily_row, learner, x_tz),
            "live": sum(c["opens"] <= now < c["closes"] for c in contests),
            "upcoming": sum(c["opens"] > now for c in contests),
            "me": {**ranked, "challenge_streak": compete.challenge_streak(learner, x_tz)["current"],
                   "played": db.one("SELECT COUNT(*) AS n FROM sessions WHERE learner=? AND contest IS NOT NULL"
                                    " AND finished IS NOT NULL AND subject=?", learner, subject)["n"]},
            "season": {"closes": next_sat,
                       "name": "Road to " + dt.date.fromisoformat(next_sat).strftime("%b %-d") if next_sat else None},
            "board_preview": compete.leaderboard(learner=learner, limit=5, subject=subject),
            "records": compete.records(learner, subject), "week_line": compete.week_line(learner),
            "champions": compete.champions(limit=1, viewer=learner),
            "traps": compete.traps_index(learner)[:3],
            "next_badges": [b for b in compete.evaluate(learner) if not b["earned"]][:3],
            "private": compete.due_today(learner, x_tz), "sat_dates": compete.SAT_DATES}


@router.get("/api/contests")
def list_contests(status: str = "live", offset: int = 0, limit: int = 20, subject: str | None = None,
                  x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    """Contests by status; ?subject= keeps one subject's (every subject when absent)."""
    learner = learner_of(x_learner)
    if status not in ("live", "upcoming", "finished", "private"):
        raise HTTPException(422, "invalid contest status")
    compete.ensure(tz=x_tz)
    now = compete._iso(compete._now())
    rows = db.rows("SELECT * FROM contests ORDER BY opens DESC")
    rows = [r for r in rows if (not subject or r["subject"] == deps.subject_param(subject))
            and (r["kind"] != "private" or learner in compete.private_members(r["id"]))
               and (r["opens"] <= now < r["closes"] if status == "live" else
                               r["opens"] > now if status == "upcoming" else
                               bool(_sitting(r["id"], learner)) if status == "finished" else
                               r["kind"] == "private" and learner in compete.private_members(r["id"]))]
    return {"contests": [_meta(r, learner, x_tz) for r in rows[max(0, offset):max(0, offset) + min(limit, 50)]],
            "total": len(rows)}


@router.post("/api/contests")
def create_contest(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    return compete.create_private(learner_of(x_learner), body)


@router.post("/api/join")
def join_contest(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    code = str(body.get("code", ""))
    return {"kind": "contest", **compete.join_private(learner_of(x_learner), code)}


@router.get("/api/contest/daily")
def daily_contest(race: str | None = None, x_learner: str | None = Header(default=None),
                  x_tz: int = Depends(tz_of)) -> dict:
    return _meta(compete.contest("daily", x_tz), _viewer(x_learner), x_tz, race)


def _start(cid: str, learner: str, tz: int, race: str | None = None) -> dict:
    # Same-process duplicate starts share one build. Render twins before the
    # short claim transaction so question generation never holds a DB writer.
    with _START_LOCKS[hash((cid, learner)) % len(_START_LOCKS)]:
        contest = compete.contest(cid, tz)
        old = _sitting(contest["id"], learner)
        prepared = None
        if not old or old["finished"] and contest["kind"] in ("sprint", "rush"):
            spec = compete._json(contest["spec"], {}) or {}
            if contest["kind"] in ("weekly", "final") or spec.get("twin"):
                prepared = compete.twin_questions(learner, contest["id"], spec["slots"],
                                                   family=spec.get("family"))
            elif not compete._json(contest["questions"], []):
                prepared = compete.twin_questions("contest:" + contest["id"], contest["id"], spec["slots"])
        with db.atomic():
            result = _start_locked(cid, learner, tz, race, prepared)
        if result.pop("_resume_challenge", False):
            row = db.one("SELECT * FROM sessions WHERE id=?", result["session"])
            return {**result, **drill.state(row), **drill.next_question(row)}
        if result.pop("_first_challenge", False):
            sid = result["session"]
            first = drill.next_question(db.one("SELECT * FROM sessions WHERE id=?", sid))
            return {**result, "clock": compete.clock(db.one("SELECT * FROM sessions WHERE id=?", sid)), **first}
        return result


def _start_locked(cid: str, learner: str, tz: int, race: str | None = None,
                  prepared: list[dict] | None = None) -> dict:
    contest = compete.contest(cid, tz)
    if contest["opens"] > compete._iso(compete._now()) and contest["kind"] != "daily":
        raise HTTPException(409, "contest has not opened")
    if contest["kind"] == "private" and learner not in compete.private_members(contest["id"]):
        raise HTTPException(403, "join this contest first")
    old = _sitting(contest["id"], learner)
    if old and (not old["finished"] or contest["kind"] not in ("sprint", "rush")):
        return {"session": old["id"], "runner": "test" if old["kind"] == "module" else "session",
                "clock": compete.clock(db.one("SELECT * FROM sessions WHERE id=?", old["id"])),
                "_resume_challenge": old["kind"] == "challenge" and not old["finished"]}
    spec = compete._json(contest["spec"], {}) or {}
    race_data = compete.race_choice(contest["id"], learner, race)
    if contest["kind"] in ("weekly", "final"):
        questions = prepared
        if questions is None:
            raise RuntimeError("contest twins were not prepared")
        sid = secrets.token_urlsafe(16)
        expected = compete.par(learner, spec["slots"])
        db.run("INSERT INTO sessions(id,kind,learner,started,questions,answers,contest,subject,cfg,module,result)"
               " VALUES (?,?,?,?,?,'{}',?,?,?,1,?)", sid, "module", learner, compete._iso(compete._now()),
               json.dumps({"module1": questions}), contest["id"], contest["subject"],
               json.dumps({"timed": True, "contest": contest["id"], "par": expected, "race": race_data}), json.dumps({"par": expected}))
        return {"session": sid, "runner": "test", "clock": {"left": contest["seconds"]}}
    if spec.get("twin"):
        qs = prepared
        if qs is None:
            raise RuntimeError("contest twins were not prepared")
    else:
        qs = compete._json(contest["questions"], []) or []
        if not qs:
            qs = prepared
            if qs is None:
                raise RuntimeError("contest twins were not prepared")
            db.run("UPDATE contests SET questions=? WHERE id=? AND questions IS NULL", json.dumps(qs), contest["id"])
    sid = secrets.token_urlsafe(16)
    topics = list(dict.fromkeys(q["topic"] for q in qs))
    drill.create(learner, sid, topics, len(qs), None, False, "challenge",
                 items=[[q["key"], q["seed"]] for q in qs], kind="challenge", fixed=True)
    timing = prefs.get(learner).get("contest_timing", "follow")
    if timing == "follow":
        timing = prefs.get(learner).get("test_timing", "official")
    multiplier = {"official": 1, "x1.5": 1.5, "x2": 2}.get(timing, 1)
    cfg = json.loads(db.one("SELECT cfg FROM sessions WHERE id=?", sid)["cfg"])
    expected = compete.par(learner, spec["slots"])
    cfg.update({"contest": contest["id"], "seconds": round(contest["seconds"] * multiplier),
                "timing": timing, "tz": tz, "timed": False, "fixed": True,
                "feedback": spec.get("reveal", "each"), "par": expected, "race": race_data})
    db.run("UPDATE sessions SET contest=?,cfg=?,subject=? WHERE id=?", contest["id"],
           json.dumps(cfg), contest["subject"], sid)
    db.run("UPDATE sessions SET result=? WHERE id=?", json.dumps({"par": expected}), sid)
    return {"session": sid, "runner": "session", "_first_challenge": True}


@router.post("/api/contest/daily/start")
def daily_start(race: str | None = None, x_learner: str | None = Header(default=None),
                x_tz: int = Depends(tz_of)) -> dict:
    return _start("daily", learner_of(x_learner), x_tz, race)


@router.get("/api/leaderboard")
def public_leaderboard(metric: str = "points", period: str = "week", scope: str = "all",
                       subject: str = "math", domain: str | None = None, offset: int = 0,
                       limit: int = 50, find: str | None = None, at: str | None = None,
                       sort: str = "value",
                       x_learner: str | None = Header(default=None)) -> dict:
    return compete.leaderboard(metric, period, scope, learner=_viewer(x_learner), subject=subject,
                               domain=domain, offset=offset, limit=limit, find=find, at=at, sort=sort)


@router.get("/api/compete/champions")
def compete_champions(kind: str | None = None, mine: bool = False, before: str | None = None,
                      x_learner: str | None = Header(default=None)) -> list[dict]:
    learner = _viewer(x_learner)
    return compete.champions(kind, learner if mine else None, before, viewer=learner)


@router.get("/api/compete/me")
def compete_me(subject: str | None = None, x_learner: str | None = Header(default=None),
               x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    subject = deps.subject_param(subject)
    return {**compete.rank_snapshot(learner, x_tz, subject), "badges": compete.evaluate(learner),
            "streak": compete.challenge_streak(learner, x_tz),
            "records": compete.records(learner, subject), "week_line": compete.week_line(learner),
            "boards": {p: compete.leaderboard(period=p, learner=learner, subject=subject)["you"]
                       for p in ("week", "month", "season", "all")}}


@router.get("/api/compete/recap")
def compete_recap(season: str | None = None, x_learner: str | None = Header(default=None)) -> dict:
    return compete.season_recap(learner_of(x_learner), season)


@router.get("/api/compete/final-focus")
def compete_final_focus(x_learner: str | None = Header(default=None)) -> dict:
    return {"focus": compete.final_focus(learner_of(x_learner))}


@router.get("/api/contest/{cid}/card")
def contest_test_day_card(cid: str, x_learner: str | None = Header(default=None),
                          x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    row = compete.contest(cid, x_tz)
    if row["kind"] != "final":
        raise HTTPException(404, "test-day card is for a Season Final")
    focus = compete.final_focus(learner)
    if not focus or focus["sid"] != (_sitting(row["id"], learner) or {"id": None})["id"]:
        raise HTTPException(403, "finish your Final first")
    # move on at twice a question's budget (the Final is the Math section)
    pace = {t: 2 * compete._budget(row["subject"], t) // 1000 for t in ("easy", "medium", "hard")}
    return {"date": focus["exam_date"] or focus["sat_date"], "doors": compete.DOORS_LINE,
            "pace": {t: f"{s // 60}:{s % 60:02d}" for t, s in pace.items()},
            "skip_first": focus["skip_first"], "traps": focus["trap_norms"],
            "band": focus["band"], "route": focus["route"]}


@router.get("/api/compete/traps-index")
def compete_traps_index(x_learner: str | None = Header(default=None)) -> list[dict]:
    return compete.traps_index(learner_of(x_learner))


@router.get("/api/compete/history")
def compete_history(kind: str | None = None, followup: str | None = None,
                    offset: int = 0, limit: int = 20, subject: str | None = None,
                    x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    rows = db.rows("SELECT s.*,c.kind AS contest_kind,c.title,c.subject AS contest_subject FROM sessions s"
                   " JOIN contests c ON c.id=s.contest"
                   " WHERE s.learner=? AND s.finished IS NOT NULL ORDER BY s.finished DESC", learner)
    if followup not in (None, "open"):
        raise HTTPException(422, "followup must be open")
    items = []
    for r in rows:
        if kind and r["contest_kind"] != kind or subject and r["contest_subject"] != deps.subject_param(subject):
            continue
        follow = compete.rematch_status(r)
        open_traps = db.one("SELECT COUNT(DISTINCT t.template||':'||t.reason) AS n FROM attempts a"
                            " JOIN traps t ON t.learner=a.learner AND t.template=a.template"
                            " AND t.closed IS NULL WHERE a.session=? AND a.correct=0", r["id"])["n"]
        due = follow["due"]
        if followup == "open" and not (due or open_traps):
            continue
        result = compete._json(r["result"], {}) or {}
        items.append({"id": r["contest"], "session": r["id"], "kind": r["contest_kind"],
                      "subject": r["contest_subject"],
                      "title": r["title"], "finished": r["finished"], "points": r["points"],
                      "net": result.get("net"), "ranked": bool(r["ranked"]),
                      "why": r["unranked_why"], "result": result,
                      "followup": {**follow, "open_traps": open_traps},
                      "record": bool(result.get("records_new"))})
    return {"history": items[offset:offset + min(limit, 50)], "total": len(items),
            "open_followups": sum(bool(item["followup"]["due"] or item["followup"]["open_traps"])
                                  for item in items)}


@router.post("/api/compete/nudge")
def compete_nudge(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    return compete.nudge(learner_of(x_learner), str(body.get("member", "")), str(body.get("contest", "")))


@router.post("/api/follows")
def follow_student(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    return compete.follow(learner_of(x_learner), str(body.get("pid", "")))


@router.delete("/api/follows/{pid}")
def unfollow_student(pid: str, x_learner: str | None = Header(default=None)) -> dict:
    return compete.unfollow(learner_of(x_learner), pid)


@router.get("/api/compete/rivals")
def compete_rivals(subject: str | None = None, x_learner: str | None = Header(default=None)) -> dict:
    return compete.rivals(learner_of(x_learner), deps.subject_param(subject))


def _secs(body: dict) -> float:
    try:
        return float(body.get("secs", 0))
    except (TypeError, ValueError):
        raise HTTPException(422, "secs is a number") from None


# Strict mode's flag (the runner's integrity events, compete.flag): /spot, its own path, because
# /api/session/{sid}/void is Review's discard (api_review registers it first); /api/drill/{sid}/void stays for
# older pages
@router.post("/api/drill/{sid}/spot")
@router.post("/api/drill/{sid}/void")
def flag_drill(sid: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    return compete.flag(sid, learner_of(x_learner), str(body.get("question_id", "")), str(body.get("why", "")),
                        _secs(body))


@router.post("/api/drill/{sid}/confirm")
def confirm_drill(sid: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    return compete.confirm_next(sid, learner_of(x_learner), body.get("answer"))


@router.post("/api/session/{sid}/spot")
def flag_test(sid: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    return compete.flag(sid, learner_of(x_learner), str(body.get("question_id", "")), str(body.get("why", "")),
                        _secs(body))


@router.post("/api/session/{sid}/confirm")
def confirm_test(sid: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    return compete.confirm_next(sid, learner_of(x_learner), body.get("answer"))


@router.post("/api/report-name")
def report_name(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    reporter = learner_of(x_learner)
    pid = str(body.get("pid", ""))
    target = next((r["id"] for r in db.rows("SELECT id FROM learners") if compete._pid(r["id"]) == pid), None)
    if not target or target == reporter:
        raise HTTPException(404, "student not found")
    qualified = db.one("SELECT 1 FROM sessions WHERE learner=? AND contest IS NOT NULL"
                       " AND ranked=1 AND finished IS NOT NULL", reporter)
    if not qualified:
        return {"filed": False, "reason": "finish a ranked contest first"}
    db.run("INSERT OR IGNORE INTO name_reports(target,reporter,at) VALUES (?,?,?)",
           target, reporter, compete._iso(compete._now()))
    count = db.one("SELECT COUNT(*) AS n FROM name_reports WHERE target=?", target)["n"]
    if count >= 3:
        db.run("UPDATE learners SET name=NULL,handle=NULL WHERE id=?", target)
    return {"filed": True, "count": count}


@router.patch("/api/contest/{cid}")
def edit_private(cid: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    row = compete.contest(cid)
    if row["kind"] != "private" or row["owner"] != learner:
        raise HTTPException(403, "only the creator can change settings")
    if set(body) != {"title"} and set(body) != {"extend"} and set(body) != {"close"}:
        raise HTTPException(422, "change title, extend or close")
    if "title" in body:
        title = str(body["title"]).strip()
        if not 3 <= len(title) <= 60:
            raise HTTPException(422, "title must be 3–60 characters")
        db.run("UPDATE contests SET title=? WHERE id=? OR series=?", title, row["series"] or cid,
               row["series"] or cid)
    elif body.get("extend"):
        root = row["series"] or cid
        for r in db.rows("SELECT id,closes FROM contests WHERE id=? OR series=?", root, root):
            until = dt.datetime.fromisoformat(r["closes"]) + dt.timedelta(hours=24)
            db.run("UPDATE contests SET closes=? WHERE id=?", compete._iso(until), r["id"])
    elif body.get("close"):
        db.run("UPDATE contests SET closes=? WHERE id=?", compete._iso(compete._now()), cid)
    return {"id": cid, "updated": True}


@router.delete("/api/contest/{cid}")
def delete_private(cid: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    row = compete.contest(cid)
    if row["kind"] != "private" or row["owner"] != learner:
        raise HTTPException(403, "only the creator can delete this contest")
    if db.one("SELECT 1 FROM sessions WHERE contest=?", cid):
        raise HTTPException(409, "a started contest cannot be deleted")
    root = row["series"] or cid
    if db.one("SELECT 1 FROM sessions WHERE contest IN (SELECT id FROM contests WHERE id=? OR series=?)",
              root, root):
        raise HTTPException(409, "a started series cannot be deleted")
    db.run("DELETE FROM contest_members WHERE contest=?", root)
    db.run("DELETE FROM contests WHERE id=? OR series=?", root, root)
    return {"deleted": True}


@router.delete("/api/contest/{cid}/members/{pid}")
def remove_private_member(cid: str, pid: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    row = compete.contest(cid)
    if row["kind"] != "private" or row["owner"] != learner:
        raise HTTPException(403, "only the creator can remove entrants")
    target = next((m for m in compete.private_members(cid) if compete._pid(m) == pid), None)
    if not target or target == learner:
        raise HTTPException(404, "entrant not found")
    db.run("DELETE FROM contest_members WHERE contest=? AND learner=?", row["series"] or cid, target)
    return {"removed": True}


@router.get("/api/contest/{cid}/board")
def contest_board(cid: str, scope: str = "all", offset: int = 0, limit: int = 50,
                  view: str | None = None, sort: str = "points", domain: str = "all",
                  x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    row = compete.contest(cid, x_tz)
    compete.private_access(row, _viewer(x_learner))
    if view == "series":
        return compete.series_board(row["series"] or row["id"], sort, _viewer(x_learner))
    if row["kind"] == "rush":
        return compete.rush_board(row["id"], _viewer(x_learner), domain)
    if row["kind"] == "words":
        return compete.word_board(row["id"], _viewer(x_learner))
    return compete.board(row["id"], _viewer(x_learner), scope, offset, limit)


@router.get("/api/contest/{cid}/review")
def contest_review(cid: str, x_learner: str | None = Header(default=None),
                   x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    row = compete.contest(cid, x_tz)
    compete.private_access(row, learner)
    sitting = _sitting(row["id"], learner)
    if row["kind"] == "words":
        if not sitting or not sitting["finished"]:
            raise HTTPException(403, "finish your Word Sprint first")
        answers = compete._json(sitting["answers"], {}) or {}
        return {"items": [{"question": {k: q[k] for k in ("id", "kind", "stem", "text", "choices")
                                        if k in q}, "key": q["answer_index"],
                           "word": q.get("word"), "given": answers.get(q["id"], {}).get("choice"),
                           "correct": answers.get(q["id"], {}).get("correct"),
                           "trap": answers.get(q["id"], {}).get("trap")}
                          for q in compete._questions(sitting)]}
    if (not sitting or not sitting["finished"]) and row["closes"] > compete._iso(compete._now()):
        raise HTTPException(403, "answers open after you finish or the contest closes")
    if not sitting:
        return {"items": []}
    answers = compete._json(sitting["answers"], {}) or {}
    items = []
    for slot, q in enumerate(compete._questions(sitting), 1):
        access = deps.access(learner, q["key"], q["seed"])
        # F4 protects every live contest item globally. A finished twin is
        # safe to show to the learner who just answered that exact form.
        own_finished_twin = bool(sitting["finished"] and
                                 (compete._json(row["spec"], {}) or {}).get("twin"))
        if access != "reveal" and not own_finished_twin:
            continue
        attempts = db.one("SELECT * FROM attempts WHERE session=? AND qid=?", sitting["id"], q["id"])
        field = _slot_field(row["id"], slot)
        items.append({"question": q, "given": answers.get(q["id"]),
                      "correct": bool(attempts["correct"]) if attempts else False,
                      "field": field})
    return {"items": items}


def _slot_field(cid: str, slot: int) -> dict:
    sittings = db.rows("SELECT id,questions,answers FROM sessions WHERE contest=?"
                       " AND finished IS NOT NULL AND ranked=1", cid)
    # R&W entrants each had their own item in a slot, and an R&W miss's reason is that item's own wording:
    # pooled, it would quote other students' questions (live ones too), so R&W counts wrong answers unnamed
    named = (db.one("SELECT subject FROM contests WHERE id=?", cid) or {"subject": "math"})["subject"] != "rw"
    counts: Counter = Counter()
    times = []
    for sitting in sittings:
        qs = compete._questions(sitting)
        if len(qs) < slot:
            continue
        q = qs[slot - 1]
        attempt = db.one("SELECT correct,reason,void,sms FROM attempts WHERE session=? AND qid=?"
                         " ORDER BY id LIMIT 1", sitting["id"], q["id"])
        if attempt is None:
            counts["skip"] += 1
        elif attempt["void"]:
            counts["void"] += 1
        elif attempt["correct"]:
            counts["right"] += 1
        else:
            counts["wrong:" + progress.norm(attempt["reason"] or "Other mistake") if named else "wrong"] += 1
        if attempt and attempt["sms"] is not None:
            times.append(attempt["sms"])
    n = sum(counts.values())
    if not n:
        return {"players": 0, "right": 0, "skipped": 0, "voided": 0, "mistakes": [],
                "shares": {"right": 0, "skipped": 0, "voided": 0}, "median_ms": None}
    mistakes = [{"norm": key[6:], "label": key[6:], "share": value / n, "count": value}
                for key, value in counts.items() if key.startswith("wrong:")]
    mistakes.sort(key=lambda x: -x["count"])
    return {"players": n, "right": counts["right"] / n, "skipped": counts["skip"] / n,
            "voided": counts["void"] / n, "mistakes": mistakes,
            "shares": {"right": counts["right"] / n, "skipped": counts["skip"] / n,
                       "voided": counts["void"] / n,
                       **{m["norm"]: m["share"] for m in mistakes}},
            "median_ms": statistics.median(times) if times else None}


@router.get("/api/contest/{cid}/grid")
def contest_grid(cid: str, offset: int = 0, limit: int = 50,
                 x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    row = compete.contest(cid, x_tz)
    compete.private_access(row, learner)
    own = _sitting(row["id"], learner)
    if (not own or not own["finished"]) and row["closes"] > compete._iso(compete._now()):
        raise HTTPException(403, "grid opens after you finish or the contest closes")
    board = compete.board(row["id"], learner, offset=offset, limit=limit)
    sessions = {compete._pid(s["learner"]): s for s in db.rows(
        "SELECT * FROM sessions WHERE contest=? AND finished IS NOT NULL AND ranked=1"
        " ORDER BY points ASC, finished DESC", row["id"])}
    marks = []
    for entry in board["entries"]:
        session = sessions.get(entry["pid"])
        slots = []
        if session:
            for q in compete._questions(session):
                a = db.one("SELECT correct,void FROM attempts WHERE session=? AND qid=? ORDER BY id LIMIT 1",
                           session["id"], q["id"])
                slots.append("void" if a and a["void"] else "right" if a and a["correct"] else
                             "wrong" if a else "skip")
            slots.extend(["skip"] * max(0, row["count"] - len(slots)))
        marks.append({"pid": entry["pid"], "name": entry["name"], "rank": entry["rank"],
                      "you": entry["you"], "marks": slots})
    footer = []
    for slot in range(1, row["count"] + 1):
        field = _slot_field(row["id"], slot)
        footer.append({"slot": slot, "right_share": field["right"], "median_ms": field["median_ms"],
                       "top": field["mistakes"][0] if field["mistakes"] else None})
    by_norm: Counter = Counter()
    for field in footer:
        if field["top"]:
            by_norm[field["top"]["norm"]] += field["top"]["count"]
    return {"id": row["id"], "rows": marks, "footer": footer,
            "where": [{"norm": norm, "label": norm, "fell": n, "of": board["players"]}
                      for norm, n in by_norm.most_common(3)], "next_offset": board["next_offset"]}


@router.get("/api/contest/{cid}/traps")
def contest_traps(cid: str, x_learner: str | None = Header(default=None),
                  x_tz: int = Depends(tz_of)) -> dict:
    row = compete.contest(cid, x_tz)
    compete.private_access(row, _viewer(x_learner))
    gathered: Counter = Counter()
    for slot in range(1, row["count"] + 1):
        for item in _slot_field(row["id"], slot)["mistakes"]:
            gathered[item["norm"]] += item["count"]
    return {"traps": [{"norm": n, "label": n, "fell": v} for n, v in gathered.most_common(5)]}


@router.get("/api/contest/{cid}/compare/{pid}")
def contest_compare(cid: str, pid: str, x_learner: str | None = Header(default=None),
                    x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    row = compete.contest(cid, x_tz)
    compete.private_access(row, learner)
    own = _sitting(row["id"], learner)
    if not own or not own["finished"]:
        raise HTTPException(403, "finish your sitting first")
    peer = next((s for s in db.rows("SELECT * FROM sessions WHERE contest=? AND finished IS NOT NULL"
                                      " AND ranked=1", row["id"]) if compete._pid(s["learner"]) == pid), None)
    if not peer or compete._identity(peer["learner"], learner,
                                    private=row["kind"] == "private")["name"] == "Anonymous":
        raise HTTPException(404, "student not found")
    def marks(session):
        return [bool(a["correct"]) if (a := db.one("SELECT correct FROM attempts WHERE session=? AND qid=?",
                                                   session["id"], q["id"])) else None
                for q in compete._questions(session)]
    yours, theirs = marks(own), marks(peer)
    return {"you": yours, "them": theirs, "both": sum(a and b for a, b in zip(yours, theirs)),
            "only_you": sum(a and not b for a, b in zip(yours, theirs)),
            "only_them": sum(b and not a for a, b in zip(yours, theirs)),
            "neither": sum(not a and not b for a, b in zip(yours, theirs))}


@router.get("/api/contest/{cid}/debrief")
def contest_debrief(cid: str, x_learner: str | None = Header(default=None),
                     x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    row = compete.contest(cid, x_tz)
    sitting = _sitting(row["id"], learner)
    if not sitting or not sitting["finished"]:
        raise HTTPException(403, "finish your sitting first")
    if row["kind"] == "words":
        result = compete._json(sitting["result"], {}) or {}
        answers = compete._json(sitting["answers"], {}) or {}
        return {"subject": "rw", "score": result.get("score"), "traps": result.get("traps", []),
                "missed": [{"id": q["id"], "word": q.get("word"),
                            "trap": answers[q["id"]].get("trap")}
                           for q in compete._questions(sitting) if q["id"] in answers and
                           not answers[q["id"]].get("correct") and not answers[q["id"]].get("skip")]}
    return compete.debrief(sitting["id"], x_tz)


@router.post("/api/contest/{cid}/rematch")
def contest_rematch(cid: str, body: dict, x_learner: str | None = Header(default=None),
                     x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    row = compete.contest(cid, x_tz)
    sitting = _sitting(row["id"], learner)
    if not sitting or not sitting["finished"]:
        raise HTTPException(409, "finish your contest first")
    when = body.get("when", "later")
    if when not in ("now", "later"):
        raise HTTPException(422, "when must be now or later")
    if when == "later":
        due = (compete.local_day(x_tz) + dt.timedelta(days=2)).isoformat()
        cfg = json.loads(sitting["cfg"] or "{}")
        cfg["rematch_due"] = due
        db.run("UPDATE sessions SET cfg=? WHERE id=?", json.dumps(cfg), sitting["id"])
        return {"due": due}
    prior_cfg = json.loads(sitting["cfg"] or "{}")
    old = prior_cfg.get("rematch_session")
    if old and db.one("SELECT 1 FROM sessions WHERE id=? AND learner=?", old, learner):
        return {"session": old}
    items, mapping = compete.rematch_items(sitting)
    if not items:
        raise HTTPException(409, "no missed questions to rematch")
    sid = secrets.token_urlsafe(16)
    topics = list(dict.fromkeys(practice.topic_of(key) for key, _ in items))
    drill.create(learner, sid, topics, len(items), None, False, "rematch",
                 items=items, kind="drill", fixed=True)
    child_cfg = json.loads(db.one("SELECT cfg FROM sessions WHERE id=?", sid)["cfg"])
    child_cfg.update({"parent": sitting["id"], "rematch_map": mapping,
                      "feedback": "instant", "repairs": "off"})
    db.run("UPDATE sessions SET cfg=? WHERE id=?", json.dumps(child_cfg), sid)
    prior_cfg["rematch_session"] = sid
    db.run("UPDATE sessions SET cfg=? WHERE id=?", json.dumps(prior_cfg), sitting["id"])
    return {"session": sid}


@router.post("/api/contest/{cid}/warmup")
def contest_warmup(cid: str, x_learner: str | None = Header(default=None),
                   x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    row = compete.contest(cid, x_tz)
    compete.private_access(row, learner)
    if _sitting(row["id"], learner):
        raise HTTPException(409, "warm up before you start the contest")
    slots = (compete._json(row["spec"], {}) or {}).get("slots", [])
    expected = compete.par(learner, slots)
    weakest = sorted(zip(expected["cells"], slots), key=lambda pair: pair[0]["chance"])[:3]
    excluded = {slot[0] for slot in slots}
    topics = list(dict.fromkeys(practice.topic_of(slot[0]) for _, slot in weakest))
    tiers = list(dict.fromkeys(slot[1] for _, slot in weakest))
    names = [name for topic in topics for name in practice.catalogue()["by_topic"].get(topic, ())
             if name not in excluded]
    if not names:
        raise HTTPException(409, "no separate warm-up questions in these skills")
    sid = drill.create(learner, {"templates": names, "tiers": tiers, "count": 6,
                                 "source": "warmup", "feedback": "each"})
    sitting = db.one("SELECT cfg FROM sessions WHERE id=?", sid)
    cfg = json.loads(sitting["cfg"])
    cfg["warmup_for"] = row["id"]
    db.run("UPDATE sessions SET cfg=? WHERE id=?", json.dumps(cfg), sid)
    return {"session": sid, "topics": topics}


@router.get("/api/contest/{cid}")
def get_contest(cid: str, code: str | None = None, race: str | None = None,
                x_learner: str | None = Header(default=None),
                x_tz: int = Depends(tz_of)) -> dict:
    if code:
        matched = db.one("SELECT id FROM contests WHERE code=? AND kind='private'", code.strip().upper())
        if not matched:
            raise HTTPException(404, "contest not found")
        cid = matched["id"]
    row = compete.contest(cid, x_tz)
    viewer = _viewer(x_learner)
    if row["kind"] == "private" and viewer not in compete.private_members(row["id"]):
        if not code:
            raise HTTPException(403, "join this contest first")
        return {"id": row["id"], "kind": "private", "title": row["title"],
                "count": row["count"], "opens": row["opens"], "closes": row["closes"], "subject": row["subject"],
                "join": True}
    return _meta(row, viewer, x_tz, race)


@router.post("/api/contest/{cid}/start")
def start_contest(cid: str, race: str | None = None, domain: str = "all",
                  x_learner: str | None = Header(default=None),
                  x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    row = compete.contest(cid, x_tz)
    if row["kind"] == "rush":
        with _START_LOCKS[hash((row["id"], learner)) % len(_START_LOCKS)]:
            return compete.rush_start(learner, row["id"], domain)
    if row["kind"] == "words":
        with _START_LOCKS[hash((row["id"], learner)) % len(_START_LOCKS)]:
            return compete.word_start(learner, row["id"])
    return _start(cid, learner, x_tz, race)


@router.post("/api/contest/{cid}/next")
def contest_next(cid: str, sid: str, x_learner: str | None = Header(default=None),
                 x_tz: int = Depends(tz_of)) -> dict:
    row = compete.contest(cid, x_tz)
    if row["kind"] == "words":
        return compete.word_next(sid, learner_of(x_learner))
    if row["kind"] != "rush":
        raise HTTPException(404, "use this contest's runner")
    return compete.rush_next(sid, learner_of(x_learner))


@router.post("/api/contest/{cid}/answer")
def contest_answer(cid: str, body: dict, x_learner: str | None = Header(default=None),
                   x_tz: int = Depends(tz_of)) -> dict:
    row = compete.contest(cid, x_tz)
    if row["kind"] == "words":
        if not isinstance(body.get("sid"), str) or not isinstance(body.get("question_id"), str):
            raise HTTPException(422, "sid and question_id are required")
        return compete.word_answer(body["sid"], learner_of(x_learner), body["question_id"],
                                   body.get("answer"), body.get("ms"))
    if row["kind"] != "rush":
        raise HTTPException(404, "use this contest's runner")
    if not isinstance(body.get("sid"), str) or not isinstance(body.get("question_id"), str):
        raise HTTPException(422, "sid and question_id are required")
    return compete.rush_answer(body["sid"], learner_of(x_learner), body["question_id"],
                               body.get("answer"), body.get("ms"))


@router.post("/api/contest/{cid}/finish")
def contest_finish(cid: str, sid: str, x_learner: str | None = Header(default=None),
                   x_tz: int = Depends(tz_of)) -> dict:
    row = compete.contest(cid, x_tz)
    if row["kind"] == "words":
        return compete.word_finish(sid, learner_of(x_learner))
    if row["kind"] != "rush":
        raise HTTPException(404, "use this contest's runner")
    return compete.rush_finish(sid, learner_of(x_learner))


@router.get("/api/contest/{cid}/pacer")
def contest_pacer(cid: str, x_learner: str | None = Header(default=None),
                  x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    row = compete.contest(cid, x_tz)
    compete.private_access(row, learner)
    sitting = _sitting(row["id"], learner)
    if not sitting:
        raise HTTPException(404, "start the contest first")
    return {"pacer": compete.pacer(sitting)}


@router.get("/challenge/")
@router.get("/challenge")
def challenge_redirect() -> RedirectResponse:
    return RedirectResponse("/compete/contest/?id=daily", status_code=307)
