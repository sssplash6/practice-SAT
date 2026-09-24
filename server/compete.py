"""Contest scheduling, twin forms, scoring, ratings, and ranked views.

The runner owners call clock, twin_questions, finish_contest and state_extra.
All public identities are derived from a server secret, never a learner code.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import json
import math
import secrets
import statistics
from collections import Counter, defaultdict

from fastapi import HTTPException

from . import blueprint, challenge, db, deps, practice, progress, ratings, satdates, scoring

SAT_DATES = satdates.SAT_DATES
ACHIEVEMENTS = [
    {"id": "pace-setter", "name": "Pace setter", "rule": "10 contest answers at SAT pace"},
    {"id": "top-ten", "name": "Top ten", "rule": "Place in a contest's top ten"},
    {"id": "weekly-4", "name": "Four weekly modules", "rule": "Finish four Weekly Modules"},
    {"id": "sprinter", "name": "Sprinter", "rule": "Finish a Sprint"},
    {"id": "dress-rehearsal", "name": "Dress rehearsal", "rule": "Finish a Season Final"},
    {"id": "season-top-10", "name": "Season top ten", "rule": "Place in a season's top ten"},
    {"id": "level-5", "name": "Level five", "rule": "Reach contest level five"},
    {"id": "level-8", "name": "Level eight", "rule": "Reach contest level eight"},
    {"id": "all-rounder", "name": "All rounder", "rule": "Play a Daily, Sprint, and Weekly"},
]


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _iso(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat(timespec="seconds")


def _json(value, default=None):
    try:
        return json.loads(value) if value else default
    except (TypeError, ValueError):
        return default


def init() -> None:
    c = db.conn()
    if not c.execute("SELECT 1 FROM kv WHERE k='compete:pid_secret'").fetchone():
        c.execute("INSERT OR IGNORE INTO kv(k,v) VALUES ('compete:pid_secret',?)", (secrets.token_hex(32),))
    # Older identical daily sittings remain readable and keep their original keys.
    for old in c.execute("SELECT day,questions,built FROM challenges"):
        day = old["day"]
        c.execute("INSERT OR IGNORE INTO contests(id,kind,title,opens,closes,count,seconds,spec,questions,created)"
                  " VALUES (?,?,?,?,?,?,?,?,?,?)",
                  ("daily-" + day, "daily", "Daily Challenge", day + "T00:00:00+00:00",
                   (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat() + "T12:00:00+00:00",
                   10, 950, json.dumps({"twin": False, "rated": True, "reveal": "each"}),
                   old["questions"], old["built"]))
    c.execute("UPDATE sessions SET contest='daily-'||day WHERE kind='challenge' AND day IS NOT NULL"
              " AND contest IS NULL")
    c.commit()


def local_day(tz: int = 0, at: dt.datetime | None = None) -> dt.date:
    return ((at or _now()) - dt.timedelta(minutes=tz)).date()


def _insert(cid: str, kind: str, title: str, opens: dt.datetime, closes: dt.datetime,
            slots: list[list], seconds: int, *, subject: str = "math", extra: dict | None = None) -> None:
    spec = {"slots": slots, "twin": True, "reveal": "each" if kind in ("daily", "sprint") else "end",
            "strict": True, "rated": kind != "private", **(extra or {})}
    db.run("INSERT OR IGNORE INTO contests(id,kind,title,opens,closes,count,seconds,spec,created,subject)"
           " VALUES (?,?,?,?,?,?,?,?,?,?)", cid, kind, title, _iso(opens), _iso(closes),
           len(slots), seconds, json.dumps(spec), _iso(_now()), subject)


def _daily_slots(day: dt.date) -> list[list]:
    # The existing builder fixes a fair domain and tier mix. Its keys are the
    # canonical types; new entrants get their own whole-question variants.
    return [[q["key"], q["difficulty"], q["type"]] for q in challenge.challenge(day.isoformat())]


def _sprint_slots(week: str) -> list[list]:
    domains = tuple(challenge.MIX)
    domain = domains[int(week[-2:]) % len(domains)]
    names = sorted(n for n, data in blueprint.kinds().items() if data["domain"] == domain)
    if not names:
        return []
    ordered = sorted(names, key=lambda n: hashlib.sha256(f"{week}:{n}".encode()).digest())
    slots = []
    for i in range(60):
        tier = "easy" if i < 4 else "medium" if i < 12 or i % 2 == 0 else "hard"
        available = [n for n in ordered if (tier, "mcq") in blueprint.kinds()[n]["kinds"]]
        if not available:
            available = [n for n in ordered if any(t == tier for t, _ in blueprint.kinds()[n]["kinds"])]
        name = available[i % len(available)] if available else ordered[i % len(ordered)]
        fmt = "mcq" if (tier, "mcq") in blueprint.kinds()[name]["kinds"] else "spr"
        slots.append([name, tier, fmt])
    return slots


def _module_slots(form: str, module: int, salt: str) -> list[list]:
    b = practice.Builder("contest:" + salt, set(), set(), dedupe="question")
    cards = blueprint.fill(blueprint.slots(form, module), blueprint.by_domain(), b,
                           blueprint.abilities(), log=lambda *_: None)
    return [[c.key, c.item.difficulty, c.item.fmt] for c in cards]


def ensure(at: dt.datetime | None = None, tz: int = 0) -> list[dict]:
    """Create live and next scheduled contests once, with no background job."""
    at = at or _now()
    local = local_day(tz, at)
    for day in (local, local + dt.timedelta(days=1)):
        if db.one("SELECT 1 FROM contests WHERE id=?", "daily-" + day.isoformat()):
            continue
        end = dt.datetime.combine(day + dt.timedelta(days=1), dt.time(12), dt.timezone.utc)
        _insert("daily-" + day.isoformat(), "daily", "Daily Challenge",
                dt.datetime.combine(day, dt.time(), dt.timezone.utc), end,
                _daily_slots(day), 950)
    monday = at.date() - dt.timedelta(days=at.weekday())
    for offset in (0, 7):
        first = monday + dt.timedelta(days=offset)
        week = f"{first.isocalendar().year}-W{first.isocalendar().week:02d}"
        start = dt.datetime.combine(first, dt.time(), dt.timezone.utc)
        if not db.one("SELECT 1 FROM contests WHERE id=?", "sprint-" + week):
            _insert("sprint-" + week, "sprint", "Sprint · " + week, start,
                    start + dt.timedelta(days=7), _sprint_slots(week), 300,
                    extra={"theme": tuple(challenge.MIX)[int(week[-2:]) % 4]})
        weekend = first + dt.timedelta(days=5)
        sat = weekend.isoformat()
        final_date = next((d for d in SAT_DATES if (dt.date.fromisoformat(d) - weekend).days == 7), None)
        kind = "final" if final_date else "weekly"
        cid = "final-" + final_date if final_date else "weekly-" + week
        if db.one("SELECT 1 FROM contests WHERE id=?", cid):
            continue
        extra = {"sat_date": final_date} if final_date else {}
        if final_date:
            extra["slots_m2"] = {route: _module_slots("module2_" + route, 2, cid + route)
                                 for route in ("lower", "upper")}
        slots = _module_slots("module1", 1, cid)
        _insert(cid, kind, "Season Final" if final_date else "Weekly Module",
                dt.datetime.combine(weekend, dt.time(), dt.timezone.utc),
                dt.datetime.combine(weekend + dt.timedelta(days=2), dt.time(12), dt.timezone.utc),
                slots, 4200 if final_date else 2100, extra=extra)
    return [dict(r) for r in db.rows("SELECT * FROM contests WHERE closes>? ORDER BY opens", _iso(at))]


def contest(cid: str, tz: int = 0):
    if cid == "daily":
        cid = "daily-" + local_day(tz).isoformat()
    ensure(tz=tz)
    row = db.one("SELECT * FROM contests WHERE id=?", cid)
    if not row:
        raise HTTPException(404, "contest not found")
    return row


def twin_questions(learner: str, cid: str, slots: list[list]) -> list[dict]:
    """Same types and order for everyone, with a unique rendered item per slot."""
    seen, _ = db.seen_for(learner)
    b = practice.Builder(learner, seen, set(), dedupe="question")
    out = []
    for i, (key, tier, fmt) in enumerate(slots, 1):
        used = {r["qhash"] for r in db.rows("SELECT qhash FROM contest_items WHERE contest=? AND slot=?",
                                             cid, i)}
        card = None
        for _ in range(120):
            candidate = blueprint.draw_matching(b, key, tier, fmt, tries=20)
            if candidate is None:
                if key in b.spent:
                    break
                continue
            qhash = practice.question_hash(candidate.item)
            if qhash in used:
                b.keep(candidate)
                continue
            written = db.run("INSERT OR IGNORE INTO contest_items(contest,template,seed,slot,qhash)"
                             " VALUES (?,?,?,?,?)", cid, key, candidate.seed, i, qhash)
            if written.rowcount:
                card = candidate
                b.keep(card)
                break
            used.add(qhash)
            b.keep(candidate)
        if card is None:
            raise HTTPException(409, {"reason": "twin_supply", "slot": i, "template": key})
        question = practice.to_question(card, i)
        question["id"] = f"c{i:02d}"
        out.append(question)
    db.remember(learner, [{"key": q["key"], "seed": q["seed"],
                           "stem_hash": practice.stem_hash(q["stem"])} for q in out], _iso(_now()))
    return out


def clock(row) -> dict:
    cfg = _json(row["cfg"], {}) or {}
    seconds = cfg.get("seconds") or (db.one("SELECT seconds FROM contests WHERE id=?", row["contest"])["seconds"]
                                      if row["contest"] else None)
    used = db.one("SELECT COALESCE(SUM(COALESCE(sms,ms)),0) AS n FROM attempts WHERE session=?", row["id"])["n"]
    questions = _json(row["questions"], []) or []
    if isinstance(questions, dict):
        questions = questions.get("module1", []) + questions.get("module2", [])
    answers = _json(row["answers"], {}) or {}
    open_question = next((q for q in reversed(questions) if q["id"] not in answers), None)
    running = bool(open_question and not row["finished"] and open_question.get("served"))
    if running:
        used += max(0, round((_now() - dt.datetime.fromisoformat(open_question["served"])).total_seconds() * 1000))
    return {"used": round(used / 1000), "left": max(0, (seconds or 0) - math.ceil(used / 1000)),
            "running": running}


def rate(learner: str, sid: str, question: dict, right: bool, when: str | None = None) -> None:
    row = db.one("SELECT s.*,c.spec FROM sessions s JOIN contests c ON c.id=s.contest WHERE s.id=?", sid)
    if not row or not (_json(row["spec"], {}) or {}).get("rated") or not row["ranked"]:
        return
    db.run("INSERT INTO learners(id,created) VALUES (?,?) ON CONFLICT(id) DO NOTHING", learner, when or _iso(_now()))
    profile = db.one("SELECT rating,rated FROM learners WHERE id=?", learner)
    before, n = profile["rating"] or 1000.0, profile["rated"] or 0
    item_rating, _ = ratings.item(question["key"], question["difficulty"])
    expected = 1 / (1 + 10 ** ((item_rating - before) / 400))
    after = before + (32 if n < 30 else 12) * ((1 if right else 0) - expected)
    db.run("UPDATE learners SET rating=?,rated=? WHERE id=?", after, n + 1, learner)
    result = _json(row["result"], {}) or {}
    result.setdefault("rating_before", before)
    result["rating_after"] = after
    db.run("UPDATE sessions SET result=? WHERE id=?", json.dumps(result), sid)


def _questions(row) -> list[dict]:
    questions = _json(row["questions"], []) or []
    if isinstance(questions, dict):
        return questions.get("module1", []) + questions.get("module2", [])
    return questions


def finish_contest(row) -> dict:
    """Freeze a contest result after the ordinary drill or test has marked it."""
    row = db.one("SELECT * FROM sessions WHERE id=?", row["id"])
    if not row or not row["contest"]:
        return {}
    if row["points"] is not None:
        return _json(row["result"], {}) or {}
    contest_row = db.one("SELECT * FROM contests WHERE id=?", row["contest"])
    if not contest_row:
        return {}
    spec = _json(contest_row["spec"], {}) or {}
    answers = _json(row["answers"], {}) or {}
    attempts = {r["qid"]: r for r in db.rows("SELECT * FROM attempts WHERE session=? ORDER BY id", row["id"])}
    qs = _questions(row)
    base = pace = right = wrong = skipped = voided = fast = 0
    for q in qs:
        given = answers.get(q["id"])
        attempt = attempts.get(q["id"])
        if given == "_skip" or given is None:
            skipped += 1
            continue
        if not attempt:
            skipped += 1
            continue
        if attempt["void"]:
            voided += 1
            continue
        if attempt["correct"]:
            right += 1
            base += {"easy": 10, "medium": 20, "hard": 30}.get(q["difficulty"], 20)
            budget = q.get("budget_ms") or 95_000
            if contest_row["kind"] != "sprint" and attempt["sms"] is not None and attempt["sms"] <= budget:
                pace += 5
            if attempt["sms"] is not None and attempt["sms"] < 4000:
                fast += 1
        else:
            wrong += 1
    finish_bonus = 10 if contest_row["kind"] != "sprint" and not skipped and not voided and len(qs) == contest_row["count"] else 0
    points = base + pace + finish_bonus
    used = clock(row)["used"]
    if contest_row["kind"] in ("weekly", "final"):
        used = min(contest_row["seconds"], max(0, round((dt.datetime.fromisoformat(row["finished"] or _iso(_now())) -
                                                         dt.datetime.fromisoformat(row["started"])).total_seconds())))
    ranked, why = True, None
    if not contest_row["opens"] <= row["started"] <= contest_row["closes"]:
        ranked, why = False, "ghost"
    elif contest_row["kind"] not in ("sprint", "rush", "words") and db.one(
            "SELECT 1 FROM sessions WHERE contest=? AND learner=? AND id!=? AND ranked=1 AND finished IS NOT NULL",
            row["contest"], row["learner"], row["id"]):
        ranked, why = False, "repeat"
    elif fast > 5:
        ranked, why = False, "fast"
    result = _json(row["result"], {}) or {}
    result.update({"right": right, "wrong": wrong, "skipped": skipped, "voided": voided,
                   "asked": len(qs), "points": points,
                   "points_parts": {"base": base, "pace": pace, "finish": finish_bonus}})
    db.run("UPDATE sessions SET points=?,secs=?,ranked=?,unranked_why=?,result=? WHERE id=?",
           points, used, int(ranked), why, json.dumps(result), row["id"])
    return result


def state_extra(row) -> dict:
    if not row["contest"]:
        return {}
    c = db.one("SELECT id,kind,title FROM contests WHERE id=?", row["contest"])
    return {"contest": dict(c) if c else None, "ranked": bool(row["ranked"]),
            "why": row["unranked_why"], "clock": clock(row)}


def _pid(learner: str) -> str:
    secret = db.one("SELECT v FROM kv WHERE k='compete:pid_secret'")
    if not secret:
        init()
        secret = db.one("SELECT v FROM kv WHERE k='compete:pid_secret'")
    return hmac.new(bytes.fromhex(secret["v"]), learner.encode(), hashlib.sha256).hexdigest()[:10]


def _identity(learner: str, viewer: str | None = None) -> dict:
    profile = db.one("SELECT name,handle,board,rating,rated,country FROM learners WHERE id=?", learner)
    board_mode = profile["board"] if profile else "name"
    hidden = board_mode == "hidden"
    anon = board_mode == "anon"
    name = profile["handle"] or profile["name"] if profile else None
    name = challenge.handle(learner, None if anon else name)
    return {"pid": _pid(learner), "name": name if not hidden or learner == viewer else "Anonymous",
            "anon": hidden, "level": ratings.level_of(profile["rating"] or 1000) if profile else 1,
            "country": profile["country"] if profile else None}


def _rank(entries: list[dict], value: str = "points") -> None:
    entries.sort(key=lambda e: (-e[value], e.get("finished") or "", e["pid"]))
    prior = None
    for i, entry in enumerate(entries, 1):
        score = entry[value]
        entry["rank"] = i if score != prior else entries[i - 2]["rank"]
        prior = score
    counts = Counter(e["rank"] for e in entries)
    for entry in entries:
        entry["tie"] = counts[entry["rank"]] > 1


def board(cid: str, me: str | None = None, scope: str = "all", offset: int = 0,
          limit: int = 50, *, view: str | None = None) -> dict:
    contest_row = contest(cid)
    rows = db.rows("SELECT s.*,l.country,l.rating,l.board,l.handle,l.name FROM sessions s"
                   " LEFT JOIN learners l ON l.id=s.learner WHERE s.contest=? AND s.finished IS NOT NULL"
                   " AND s.ranked=1 ORDER BY s.finished", contest_row["id"])
    best = {}
    for row in rows:
        previous = best.get(row["learner"])
        if previous is None or (row["points"] or 0) > (previous["points"] or 0):
            best[row["learner"]] = row
    entries = []
    for learner, row in best.items():
        ident = _identity(learner, me)
        result = _json(row["result"], {}) or {}
        entries.append({**ident, "learner": learner, "points": row["points"] or 0,
                        "right": result.get("right", 0), "asked": result.get("asked", contest_row["count"]),
                        "secs": row["secs"], "finished": row["finished"], "you": learner == me,
                        "session": row["id"]})
    _rank(entries)
    mine = next((e for e in entries if e["you"]), None)
    if scope == "country" and me:
        own_country = (_identity(me).get("country"))
        entries = [e for e in entries if e["country"] == own_country] if own_country else []
    elif scope == "following" and me:
        followed = {r["target"] for r in db.rows("SELECT target FROM follows WHERE learner=?", me)}
        entries = [e for e in entries if e["learner"] in followed or e["you"]]
    elif scope == "level" and me:
        level = _identity(me)["level"]
        entries = [e for e in entries if e["level"] == level]
    elif scope == "extended":
        entries = [e for e in entries if db.one("SELECT 1 FROM sessions WHERE id=? AND cfg LIKE '%x1.%'",
                                                 e["session"] or "")]
    elif scope == "near" and mine:
        center = next(i for i, e in enumerate(entries) if e["you"])
        start = max(0, min(center - 5, len(entries) - 11))
        entries = entries[start:start + 11]
        offset = 0
        limit = 11
    elif scope != "all":
        raise HTTPException(422, "unknown board scope")
    players = len(entries)
    page = entries[offset:offset + min(max(1, limit), 100)]
    next_offset = offset + len(page) if offset + len(page) < players else None
    for entry in page:
        entry.pop("learner", None)
        entry.pop("finished", None)
        if not entry["you"]:
            entry.pop("session", None)
    if mine:
        mine = {k: v for k, v in mine.items() if k not in ("learner", "finished")}
    return {"id": contest_row["id"], "players": players, "entries": page, "you": mine,
            "mine": mine, "next_offset": next_offset, "pars": []}


def _period_bounds(period: str, at: dt.date | None = None) -> tuple[str | None, str | None]:
    d = at or _now().date()
    if period == "all":
        return None, None
    if period == "week":
        start = d - dt.timedelta(days=d.weekday())
        end = start + dt.timedelta(days=7)
    elif period == "month":
        start = d.replace(day=1)
        end = (start + dt.timedelta(days=32)).replace(day=1)
    elif period == "year":
        start, end = d.replace(month=1, day=1), d.replace(year=d.year + 1, month=1, day=1)
    elif period == "season":
        dates = [dt.date.fromisoformat(x) for x in SAT_DATES]
        next_date = next((x for x in dates if x >= d), None)
        if next_date is None:
            return None, None
        previous = max((x for x in dates if x < next_date), default=next_date - dt.timedelta(days=90))
        start, end = previous + dt.timedelta(days=1), next_date + dt.timedelta(days=1)
    else:
        raise HTTPException(422, "period must be week, month, season, year or all")
    return start.isoformat(), end.isoformat()


def leaderboard(metric: str = "points", period: str = "week", scope: str = "all",
                *, learner: str | None = None, subject: str = "math", domain: str | None = None,
                offset: int = 0, limit: int = 50, sort: str = "value", find: str | None = None,
                at: str | None = None) -> dict:
    """One learner per row, with competition ranks shared by equal values."""
    if metric not in ("points", "net", "rating", "skill", "right", "test", "climb"):
        raise HTTPException(422, "unknown leaderboard metric")
    if subject not in ("math", "rw") or sort not in ("value", "change"):
        raise HTTPException(422, "subject or sort is invalid")
    date = dt.date.fromisoformat(at) if at and len(at) == 10 else None
    start, end = _period_bounds(period, date)
    rows = db.rows("SELECT s.*,c.kind AS contest_kind,c.subject AS contest_subject FROM sessions s"
                   " LEFT JOIN contests c ON c.id=s.contest WHERE s.finished IS NOT NULL AND s.ranked=1")
    values: dict[str, float] = defaultdict(float)
    finished: dict[str, str] = {}
    sprint_best: dict[tuple[str, str], int] = {}
    for row in rows:
        day = row["finished"][:10]
        if (start and day < start) or (end and day >= end):
            continue
        if row["contest"] and row["contest_subject"] != subject:
            continue
        if metric in ("points", "net", "climb"):
            if not row["contest"] or row["contest_kind"] == "private":
                continue
            amount = row["points"] or 0
            if metric == "net":
                amount -= (_json(row["result"], {}) or {}).get("par", {}).get("base", 0)
            if row["contest_kind"] == "sprint":
                key = (row["learner"], row["contest"])
                old = sprint_best.get(key, 0)
                sprint_best[key] = max(old, amount)
                values[row["learner"]] += max(0, amount - old)
            else:
                values[row["learner"]] += amount
            finished[row["learner"]] = max(finished.get(row["learner"], ""), row["finished"])
        elif metric == "test" and row["kind"] == "mock" and (_json(row["cfg"], {}) or {}).get("timed", True):
            band = (_json(row["result"], {}) or {}).get("estimate") or {}
            if band.get("low") is not None and band.get("high") is not None:
                values[row["learner"]] = max(values[row["learner"]], (band["low"] + band["high"]) / 2)
                finished[row["learner"]] = max(finished.get(row["learner"], ""), row["finished"])
    if metric in ("right", "skill"):
        if metric == "skill" and not domain:
            raise HTTPException(422, "skill rating needs a domain")
        if metric == "skill":
            grouped: dict[str, list[float]] = defaultdict(list)
            for r in db.rows("SELECT learner,topic,rating FROM skill_ratings"):
                if ratings and progress.topics().get(r["topic"]) and progress.topics()[r["topic"]].domain == domain:
                    grouped[r["learner"]].append(r["rating"])
            values = {person: round(sum(v) / len(v)) for person, v in grouped.items()}
        else:
            values.clear()
            for a in db.rows("SELECT learner,topic,correct,at FROM attempts WHERE repeat=0 AND disputed=0"
                             " AND void IS NULL"):
                if not a["correct"] or (start and a["at"][:10] < start) or (end and a["at"][:10] >= end):
                    continue
                topic = progress.topics().get(a["topic"])
                if deps.subject_of(a["topic"]) != subject or (domain and (not topic or topic.domain != domain)):
                    continue
                values[a["learner"]] += 1
    if metric == "rating":
        values = {r["id"]: round(r["rating"] or 1000) for r in db.rows("SELECT id,rating,rated FROM learners")
                  if r["rated"]}
    entries = []
    own_country = _identity(learner).get("country") if learner else None
    own_level = _identity(learner)["level"] if learner else None
    followed = {r["target"] for r in db.rows("SELECT target FROM follows WHERE learner=?", learner)} if learner else set()
    for person, value in values.items():
        ident = _identity(person, learner)
        if scope == "country" and (not own_country or ident["country"] != own_country):
            continue
        if scope == "following" and person not in followed and person != learner:
            continue
        if scope == "level" and ident["level"] != own_level:
            continue
        if find and find.casefold() not in ident["name"].casefold():
            continue
        entries.append({**ident, "learner": person, "value": round(value, 1),
                        "finished": finished.get(person), "you": person == learner})
    if metric == "net":
        entries = [e for e in entries if (db.one("SELECT rated FROM learners WHERE id=?", e["learner"]) or
                                          {"rated": 0})["rated"] >= 30]
    _rank(entries, "value")
    mine = next((e for e in entries if e["you"]), None)
    if scope == "near" and mine:
        i = next(i for i, e in enumerate(entries) if e["you"])
        entries = entries[max(0, min(i - 5, len(entries) - 11)):][:11]
        offset = 0
    elif scope not in ("all", "country", "following", "level", "near", "extended"):
        raise HTTPException(422, "unknown leaderboard scope")
    players = len(entries)
    page = entries[offset:offset + min(max(1, limit), 100)]
    for e in page:
        e.pop("learner", None)
        e.pop("finished", None)
    if mine:
        mine = {k: v for k, v in mine.items() if k not in ("learner", "finished")}
    return {"metric": metric, "period": period, "scope": scope, "subject": subject,
            "players": players, "entries": page, "podium": page[:3] if offset == 0 else [],
            "you": mine, "next_offset": offset + len(page) if offset + len(page) < players else None,
            "resets_at": end, "nearest_nonempty": None}


def evaluate(learner: str) -> list[dict]:
    """Record earned Compete badges once; overlapping Shell rules stay shared."""
    played = db.rows("SELECT c.kind,s.id FROM sessions s JOIN contests c ON c.id=s.contest"
                     " WHERE s.learner=? AND s.finished IS NOT NULL AND s.ranked=1", learner)
    kinds = Counter(r["kind"] for r in played)
    paced = db.one("SELECT COUNT(*) AS n FROM attempts a JOIN sessions s ON s.id=a.session"
                   " WHERE s.learner=? AND s.contest IS NOT NULL AND a.correct=1"
                   " AND COALESCE(a.sms,999999)<=95000", learner)["n"]
    rank = rank_snapshot(learner)
    have = {"first-contest": len(played), "pace-setter": paced, "weekly-4": kinds["weekly"],
            "sprinter": kinds["sprint"], "dress-rehearsal": kinds["final"],
            "level-5": rank["level"], "level-8": rank["level"],
            "all-rounder": sum(kinds[k] > 0 for k in ("daily", "sprint", "weekly"))}
    rules = [{"id": "first-contest", "name": "First contest", "rule": "Finish a ranked contest", "need": 1},
             *[{**badge, "need": {"pace-setter": 10, "weekly-4": 4, "level-5": 5,
                                  "level-8": 8, "all-rounder": 3}.get(badge["id"], 1)}
               for badge in ACHIEVEMENTS]]
    out = []
    for rule in rules:
        got = have.get(rule["id"], 0)
        if got >= rule["need"]:
            db.run("INSERT OR IGNORE INTO earned(learner,id,tier,at) VALUES (?,?,1,?)",
                   learner, rule["id"], _iso(_now()))
        earned = db.one("SELECT at FROM earned WHERE learner=? AND id=? AND tier=1", learner, rule["id"])
        out.append({**rule, "have": got, "earned": earned["at"] if earned else None})
    return out


def challenge_streak(learner: str, tz: int = 0) -> dict:
    today = local_day(tz)
    days = {r["day"] for r in db.rows("SELECT DISTINCT day FROM sessions WHERE learner=?"
                                       " AND contest LIKE 'daily-%' AND finished IS NOT NULL", learner)}
    count = 0
    at = today
    if at.isoformat() not in days:
        at -= dt.timedelta(days=1)
    while at.isoformat() in days:
        count += 1
        at -= dt.timedelta(days=1)
    return {"current": count, "days": sorted(days, reverse=True)[:30]}


def rank_snapshot(learner: str, tz: int = 0) -> dict:
    week = leaderboard("points", "week", "all", learner=learner, limit=1)
    all_time = leaderboard("points", "all", "all", learner=learner, limit=1)
    country = leaderboard("points", "all", "country", learner=learner, limit=1)
    profile = db.one("SELECT rating,rated FROM learners WHERE id=?", learner)
    rating = profile["rating"] if profile else 1000
    return {"week": (week["you"] or {}).get("rank"), "all": (all_time["you"] or {}).get("rank"),
            "country": (country["you"] or {}).get("rank"), "rating": round(rating or 1000),
            "level": ratings.level_of(rating or 1000), "provisional": (profile["rated"] or 0) < 30 if profile else True}


def due_today(learner: str, tz: int = 0) -> list[dict]:
    ensure(tz=tz)
    now = _iso(_now())
    out = []
    for row in db.rows("SELECT c.* FROM contests c JOIN contest_members m ON m.contest=c.id"
                       " WHERE m.learner=? AND c.opens<=? AND c.closes>? ORDER BY c.closes", learner, now, now):
        if not db.one("SELECT 1 FROM sessions WHERE contest=? AND learner=? AND finished IS NOT NULL",
                      row["id"], learner):
            out.append({"id": row["id"], "title": row["title"], "closes": row["closes"]})
    return out


def shell_part(learner: str, tz: int = 0) -> dict:
    today_id = "daily-" + local_day(tz).isoformat()
    ensure(tz=tz)
    done = db.one("SELECT 1 FROM sessions WHERE learner=? AND contest=? AND finished IS NOT NULL",
                  learner, today_id)
    return {"daily": {"id": today_id, "done": bool(done)}, "streak": challenge_streak(learner, tz)["current"],
            "due": due_today(learner, tz), "ranks": rank_snapshot(learner, tz)}


def go_for(rule_id: str, learner: str) -> dict | None:
    badge = next((a for a in ACHIEVEMENTS if a["id"] == rule_id), None)
    if not badge:
        return None
    return {**badge, "href": "/compete/", "action": "Open Compete"}
