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
import os
import pathlib
import secrets
import statistics
import sys
import threading
import time
from collections import Counter, defaultdict

from fastapi import HTTPException

if __name__ == "__main__" and not __package__:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from server import blueprint, challenge, db, deps, practice, progress, ratings, satdates, scoring
else:
    from . import blueprint, challenge, db, deps, practice, progress, ratings, satdates, scoring

SAT_DATES = satdates.SAT_DATES
SUPPLY_PATH = pathlib.Path(__file__).resolve().parent / "cache" / "twin_supply.json"
_SUPPLY: dict | None = None
_SUPPLY_THREAD: threading.Thread | None = None
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
    global _SUPPLY_THREAD
    if _SUPPLY_THREAD is None and not _read_supply():
        _SUPPLY_THREAD = threading.Thread(target=_survey_background, daemon=True, name="twin-supply")
        _SUPPLY_THREAD.start()


def _bank_hash() -> str:
    root = pathlib.Path(__file__).resolve().parent.parent / "satbank"
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*.py")):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()[:16]


def _read_supply() -> dict | None:
    global _SUPPLY
    if _SUPPLY is not None:
        return _SUPPLY
    if not SUPPLY_PATH.exists():
        return None
    try:
        found = json.loads(SUPPLY_PATH.read_text())
    except (ValueError, OSError):
        return None
    if found.get("bank") != _bank_hash():
        return None
    _SUPPLY = found
    return found


def survey_supply() -> dict:
    """Build the long-range twin variety cache, stopping each pair at 1,000."""
    pairs = {}
    names = blueprint.kinds()
    for name, info in names.items():
        for tier in sorted({t for t, _ in info["kinds"]}):
            seen = set()
            for seed in range(3000):
                try:
                    item = practice.generate(name, seed)
                except Exception:
                    continue
                if item.difficulty == tier:
                    seen.add(practice.question_hash(item))
                    if len(seen) == 1000:
                        break
            pairs[f"{name}|{tier}"] = len(seen)
    found = {"bank": _bank_hash(), "pairs": pairs}
    SUPPLY_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = SUPPLY_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(found, sort_keys=True))
    tmp.replace(SUPPLY_PATH)
    global _SUPPLY
    _SUPPLY = found
    return found


def _survey_background() -> None:
    try:
        # Let startup and the first request finish before the CPU-heavy survey.
        time.sleep(30)
        survey_supply()
    except Exception:
        import logging
        logging.getLogger("satf").exception("twin supply survey failed")


def supply_need(kind: str) -> int:
    cutoff = _iso(_now() - dt.timedelta(days=30))
    fields = db.rows("SELECT c.id,COUNT(DISTINCT s.learner) AS n FROM contests c"
                     " JOIN sessions s ON s.contest=c.id WHERE c.kind=? AND s.ranked=1"
                     " AND s.finished>=? GROUP BY c.id", kind, cutoff)
    largest = max((r["n"] for r in fields), default=0)
    return min(1000, max(100, 2 * largest))


def pool(kind: str, tier: str, *, need: int | None = None) -> list[str]:
    threshold = need or supply_need(kind)
    known = _read_supply()
    names = blueprint.kinds()
    return sorted(name for name, info in names.items() if any(t == tier for t, _ in info["kinds"])
                  and ((known["pairs"].get(f"{name}|{tier}", 0) >= threshold) if known
                       else info["variety"] >= 15))


def local_day(tz: int = 0, at: dt.datetime | None = None) -> dt.date:
    return ((at or _now()) - dt.timedelta(minutes=tz)).date()


def _insert(cid: str, kind: str, title: str, opens: dt.datetime, closes: dt.datetime,
            slots: list[list], seconds: int, *, subject: str = "math", extra: dict | None = None) -> None:
    spec = {"slots": slots, "twin": True, "reveal": "each" if kind in ("daily", "sprint") else "end",
            "strict": True, "rated": kind != "private", **(extra or {})}
    db.run("INSERT OR IGNORE INTO contests(id,kind,title,opens,closes,count,seconds,spec,created,subject)"
           " VALUES (?,?,?,?,?,?,?,?,?,?)", cid, kind, title, _iso(opens), _iso(closes),
           len(slots), seconds, json.dumps(spec), _iso(_now()), subject)


def _supply_shapes(kind: str) -> dict[str, set[tuple[str, str]]]:
    allowed = {tier: set(pool(kind, tier)) for tier in ("easy", "medium", "hard")}
    return {name: {(tier, fmt) for tier, fmt in shapes if name in allowed[tier]}
            for name, shapes in blueprint.abilities().items()}


def _daily_slots(day: dt.date) -> list[list]:
    # A separate canonical form keeps the legacy identical /api/challenge
    # sitting readable while the new Daily deals each entrant a fresh twin.
    domains = blueprint.spread(dict(challenge.MIX))
    slots = [(domain, tier, "spr" if i + 1 in challenge.SPR_AT else None)
             for i, (domain, tier) in enumerate(zip(domains, challenge.LADDER))]
    shapes = _supply_shapes("daily")
    b = practice.Builder("contest:daily:" + day.isoformat(), set(), set(), dedupe="question")
    cards = blueprint.fill(slots, blueprint.by_domain(), b, shapes, log=lambda *_: None)
    if len(cards) != 10 or any(card.key not in pool("daily", card.item.difficulty) for card in cards):
        raise HTTPException(409, "daily twin supply is too small")
    return [[card.key, card.item.difficulty, card.item.fmt] for card in cards]


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
        supplied = set(pool("sprint", tier))
        available = [n for n in ordered if n in supplied and (tier, "mcq") in blueprint.kinds()[n]["kinds"]]
        if not available:
            available = [n for n in ordered if n in supplied and any(t == tier for t, _ in blueprint.kinds()[n]["kinds"])]
        if not available:
            raise HTTPException(409, "sprint twin supply is too small")
        name = available[i % len(available)]
        fmt = "mcq" if (tier, "mcq") in blueprint.kinds()[name]["kinds"] else "spr"
        slots.append([name, tier, fmt])
    return slots


def _module_slots(form: str, module: int, salt: str) -> list[list]:
    b = practice.Builder("contest:" + salt, set(), set(), dedupe="question")
    kind = "final" if salt.startswith("final-") else "weekly"
    cards = blueprint.fill(blueprint.slots(form, module), blueprint.by_domain(), b,
                           _supply_shapes(kind), log=lambda *_: None)
    if len(cards) != blueprint.MODULE_SIZE or any(card.key not in pool(kind, card.item.difficulty)
                                                  for card in cards):
        raise HTTPException(409, "module twin supply is too small")
    return [[c.key, c.item.difficulty, c.item.fmt] for c in cards]


def ensure(at: dt.datetime | None = None, tz: int = 0) -> list[dict]:
    """Create live and next scheduled contests once, with no background job."""
    at = at or _now()
    local = local_day(tz, at)
    for day in (local, local + dt.timedelta(days=1)):
        cid = "daily-" + day.isoformat()
        previous = db.one("SELECT spec FROM contests WHERE id=?", cid)
        if previous:
            old_spec = _json(previous["spec"], {}) or {}
            if not old_spec.get("twin"):
                old_spec.update({"slots": _daily_slots(day), "twin": True,
                                 "strict": True, "rated": True})
                db.run("UPDATE contests SET spec=? WHERE id=?", json.dumps(old_spec), cid)
            continue
        end = dt.datetime.combine(day + dt.timedelta(days=1), dt.time(12), dt.timezone.utc)
        _insert(cid, "daily", "Daily Challenge",
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


def twin_questions(learner: str, cid: str, slots: list[list], start_slot: int = 1) -> list[dict]:
    """Same types and order for everyone, with a unique rendered item per slot."""
    seen, _ = db.seen_for(learner)
    b = practice.Builder(learner, seen, set(), dedupe="question")
    out = []
    for i, (key, tier, fmt) in enumerate(slots, start_slot):
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
    open_question = questions[-1] if questions and questions[-1]["id"] not in answers else None
    started = None
    if open_question:
        seen = db.one("SELECT at FROM practice_seen WHERE learner=? AND template=? AND seed=?",
                      row["learner"], open_question["key"], open_question["seed"])
        started = open_question.get("served") or (seen["at"] if seen else None)
    running = bool(open_question and not row["finished"] and started)
    if running:
        used += max(0, round((_now() - dt.datetime.fromisoformat(started)).total_seconds() * 1000))
    return {"used": round(used / 1000), "left": max(0, (seconds or 0) - math.ceil(used / 1000)),
            "running": running}


def par(learner: str | None, slots: list[list], at: str | None = None,
        *, rating: float | None = None) -> dict:
    """Expected points from calibrated item odds, frozen when a sitting starts."""
    profile = db.one("SELECT rating,rated FROM learners WHERE id=?", learner) if learner else None
    current = rating if rating is not None else (profile["rating"] if profile and profile["rating"] else 1000)
    if learner and rating is None:
        cutoff = (_now() - dt.timedelta(days=30)).isoformat()
        recent = [(_json(r["result"], {}) or {}).get("rating_after") for r in db.rows(
            "SELECT result FROM sessions WHERE learner=? AND started>=? AND result IS NOT NULL", learner, cutoff)]
        peak = max((x for x in recent if x is not None), default=current)
        current = max(current, peak - 100)
    expected = base = speed = variance = 0.0
    rough = bool(learner and (not profile or (profile["rated"] or 0) < 30))
    cells = []
    for key, tier, _fmt in slots:
        item_rating, n = ratings.item(key, tier)
        odds = 1 / (1 + 10 ** ((item_rating - current) / 400))
        worth = {"easy": 10, "medium": 20, "hard": 30}[tier]
        budget = {"easy": 65000, "medium": 95000, "hard": 126000}[tier]
        times = db.one("SELECT COUNT(*) AS n,SUM(CASE WHEN sms<=? THEN 1 ELSE 0 END) AS fast"
                       " FROM attempts WHERE template=? AND difficulty=? AND correct=1"
                       " AND repeat=0 AND disputed=0 AND void IS NULL AND sms IS NOT NULL",
                       budget, key, tier)
        paced = (times["fast"] or 0) / times["n"] if times["n"] else .75
        expected += odds
        base += odds * worth
        speed += odds * paced
        variance += odds * (1 - odds) * worth * worth
        rough |= n < 30
        cells.append({"template": key, "tier": tier, "chance": round(odds, 2)})
    return {"base": round(base / 5) * 5, "right": round(expected, 1),
            "points": round(base + 5 * speed + 10), "rating": round(current),
            "rough": bool(rough), "sd": round(math.sqrt(variance), 1), "cells": cells}


def field_line(template: str, tier: str, cid: str, slot: int, rating: float = 1000) -> dict:
    people = db.rows("SELECT s.id,s.questions FROM sessions s WHERE s.contest=?"
                     " AND s.ranked=1 AND s.finished IS NOT NULL", cid)
    seen = []
    for row in people:
        qs = _json(row["questions"], []) or []
        if isinstance(qs, dict):
            qs = qs.get("module1", []) + qs.get("module2", [])
        if len(qs) >= slot:
            a = db.one("SELECT correct FROM attempts WHERE session=? AND qid=?", row["id"], qs[slot - 1]["id"])
            if a:
                seen.append(a["correct"])
    if len(seen) >= 5:
        return {"source": "contest", "share": round(sum(seen) / len(seen), 3), "n": len(seen)}
    type_rows = db.one("SELECT COUNT(*) AS n,SUM(correct) AS right FROM attempts"
                       " WHERE template=? AND difficulty=? AND repeat=0 AND disputed=0 AND void IS NULL",
                       template, tier)
    if type_rows["n"] >= 20:
        return {"source": "type", "share": round(type_rows["right"] / type_rows["n"], 3),
                "n": type_rows["n"]}
    item_rating, _ = ratings.item(template, tier)
    chance = 1 / (1 + 10 ** ((item_rating - rating) / 400))
    return {"source": "expected", "share": round(chance, 3), "n": None,
            "level": ratings.level_of(rating)}


def rate(learner: str, sid: str, question: dict, right: bool, when: str | None = None) -> None:
    row = db.one("SELECT s.*,c.spec,c.opens,c.closes,c.kind AS contest_kind"
                 " FROM sessions s JOIN contests c ON c.id=s.contest WHERE s.id=?", sid)
    if not row or not (_json(row["spec"], {}) or {}).get("rated") or not row["ranked"]:
        return
    cfg = _json(row["cfg"], {}) or {}
    if question.get("id") in cfg.get("flags", {}):
        return
    in_window = (local_day(cfg.get("tz", 0), dt.datetime.fromisoformat(row["started"])).isoformat()
                 == row["contest"][6:]) if row["contest_kind"] == "daily" else (
                     row["opens"] <= row["started"] <= row["closes"])
    if not in_window:
        return
    if row["contest_kind"] not in ("sprint", "rush") and db.one(
            "SELECT 1 FROM sessions WHERE contest=? AND learner=? AND id!=? AND finished IS NOT NULL"
            " AND ranked=1", row["contest"], learner, sid):
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
    cfg.setdefault("rating_before", before)
    cfg["rating_after"] = after
    db.run("UPDATE sessions SET cfg=? WHERE id=?", json.dumps(cfg), sid)


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
    timing = (_json(row["cfg"], {}) or {}).get("timing", "official")
    multiplier = {"official": 1, "x1.5": 1.5, "x2": 2}.get(timing, 1)
    for q in qs:
        given = answers.get(q["id"])
        attempt = attempts.get(q["id"])
        if given == "_skip" or given is None:
            skipped += 1
            continue
        if not attempt:
            skipped += 1
            continue
        flag = (_json(row["cfg"], {}) or {}).get("flags", {}).get(q["id"], {})
        if attempt["void"] or (flag and flag.get("status") != "confirmed"):
            voided += 1
            continue
        if attempt["correct"]:
            right += 1
            base += {"easy": 10, "medium": 20, "hard": 30}.get(q["difficulty"], 20)
            budget = (q.get("budget_ms") or {"easy": 65_000, "medium": 95_000,
                                              "hard": 126_000}.get(q["difficulty"], 95_000)) * multiplier
            elapsed = attempt["sms"] if attempt["sms"] is not None else attempt["ms"]
            if contest_row["kind"] not in ("sprint", "rush") and elapsed is not None and elapsed <= budget:
                pace += 5
            if elapsed is not None and elapsed < 4000:
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
    cfg = _json(row["cfg"], {}) or {}
    in_window = (local_day(cfg.get("tz", 0), dt.datetime.fromisoformat(row["started"])).isoformat()
                 == row["contest"][6:]) if contest_row["kind"] == "daily" else (
                     contest_row["opens"] <= row["started"] <= contest_row["closes"])
    if not in_window:
        ranked, why = False, "ghost"
    elif contest_row["kind"] not in ("sprint", "rush", "words") and db.one(
            "SELECT 1 FROM sessions WHERE contest=? AND learner=? AND id!=? AND ranked=1 AND finished IS NOT NULL",
            row["contest"], row["learner"], row["id"]):
        ranked, why = False, "repeat"
    elif fast > 5:
        ranked, why = False, "fast"
    result = _json(row["result"], {}) or {}
    saved_cfg = _json(row["cfg"], {}) or {}
    for field in ("rating_before", "rating_after"):
        if field in saved_cfg:
            result[field] = saved_cfg[field]
    result.update({"right": right, "wrong": wrong, "skipped": skipped, "voided": voided,
                   "asked": len(qs), "points": points,
                   "points_parts": {"base": base, "pace": pace, "finish": finish_bonus}})
    par_data = result.get("par") or (_json(row["cfg"], {}) or {}).get("par")
    if par_data:
        result["par"] = par_data
        result["net"] = base - par_data["base"]
    result["confirmed"] = sum(f.get("status") == "confirmed" for f in
                              (_json(row["cfg"], {}) or {}).get("flags", {}).values())
    db.run("UPDATE sessions SET points=?,secs=?,ranked=?,unranked_why=?,result=? WHERE id=?",
           points, used, int(ranked), why, json.dumps(result), row["id"])
    return result


def flag(sid: str, learner: str, qid: str, why: str, secs: float = 0) -> dict:
    if why not in ("left", "blur", "copyleave", "paste", "pagehide", "fast") or not 0 <= secs <= 3600:
        raise HTTPException(422, "invalid flag")
    row = db.one("SELECT * FROM sessions WHERE id=? AND learner=?", sid, learner)
    if not row or not row["contest"] or row["finished"]:
        raise HTTPException(404, "contest sitting not found")
    q = next((q for q in _questions(row) if q["id"] == qid), None)
    if not q:
        raise HTTPException(404, "question not found")
    spec = _json(db.one("SELECT spec FROM contests WHERE id=?", row["contest"])["spec"], {}) or {}
    if not spec.get("strict"):
        return {"flagged": False}
    cfg = _json(row["cfg"], {}) or {}
    flags = cfg.setdefault("flags", {})
    flags.setdefault(qid, {"why": why, "secs": secs, "status": "pending"})
    db.run("UPDATE sessions SET cfg=? WHERE id=?", json.dumps(cfg), sid)
    return {"flagged": True, "question_id": qid, "why": why}


def confirm_next(sid: str, learner: str, answer=None) -> dict:
    row = db.one("SELECT * FROM sessions WHERE id=? AND learner=?", sid, learner)
    if not row or not row["contest"]:
        raise HTTPException(404, "contest sitting not found")
    cfg = _json(row["cfg"], {}) or {}
    flags = cfg.get("flags", {})
    original = _questions(row)
    if not all(q["id"] in (_json(row["answers"], {}) or {}) for q in original):
        raise HTTPException(409, "finish the original questions first")
    active = cfg.get("confirm_active")
    if active and answer is not None:
        q = active["question"]
        from . import scoring as scorer
        clean = scorer.is_correct(q, answer)
        progress.record(learner, sid, q, answer, None)
        flags[active["of"]]["status"] = "confirmed" if clean else "failed"
        if not clean:
            db.run("UPDATE attempts SET void=? WHERE session=? AND qid=?", flags[active["of"]]["why"],
                   sid, active["of"])
        cfg.pop("confirm_active", None)
    elif active:
        from .drill import public
        return {"question": public(active["question"]), "of": active["of"], "due": True}
    pending = [q for q in original if q["id"] in flags and flags[q["id"]]["status"] == "pending"
               and (a := db.one("SELECT correct FROM attempts WHERE session=? AND qid=?", sid, q["id"]))
               and a["correct"]]
    if len(pending) > 5:
        for q in pending[5:]:
            flags[q["id"]]["status"] = "failed"
        pending = pending[:5]
    if not pending:
        cfg["flags"] = flags
        db.run("UPDATE sessions SET cfg=? WHERE id=?", json.dumps(cfg), sid)
        return {"due": False, "confirmed": sum(f["status"] == "confirmed" for f in flags.values())}
    target = pending[0]
    slot = next(i for i, q in enumerate(original, 1) if q["id"] == target["id"])
    question = twin_questions(learner, row["contest"], [[target["key"], target["difficulty"], target["type"]]],
                              start_slot=len(original) + slot)[0]
    question["id"] = f"confirm:{target['id']}"
    cfg["flags"] = flags
    cfg["confirm_active"] = {"of": target["id"], "question": question}
    db.run("UPDATE sessions SET cfg=? WHERE id=?", json.dumps(cfg), sid)
    from .drill import public
    return {"question": public(question), "of": target["id"], "due": True}


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
    anon = board_mode in ("anon", "hidden")
    name = profile["handle"] if profile else None
    name = challenge.handle(learner, name)
    return {"pid": _pid(learner), "name": name if not anon or learner == viewer else "Anonymous",
            "anon": anon, "level": ratings.level_of(profile["rating"] or 1000) if profile else 1,
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
    extended_entries = []
    marks = Counter()
    for learner, row in best.items():
        ident = _identity(learner, me)
        result = _json(row["result"], {}) or {}
        flags = (_json(row["cfg"], {}) or {}).get("flags", {})
        mark = ("clean" if not flags else "confirmed" if all(f.get("status") == "confirmed"
                                                           for f in flags.values()) else None)
        if mark:
            marks[mark] += 1
        entry = {**ident, "learner": learner, "points": row["points"] or 0,
                        "net": result.get("net"),
                        "right": result.get("right", 0), "asked": result.get("asked", contest_row["count"]),
                        "secs": row["secs"], "finished": row["finished"], "you": learner == me,
                        "session": row["id"], "mark": mark,
                        "n": len(flags) if mark == "confirmed" else 0}
        if contest_row["kind"] != "private" and (_json(row["cfg"], {}) or {}).get("timing") in ("x1.5", "x2"):
            extended_entries.append(entry)
        else:
            entries.append(entry)
    _rank(entries)
    _rank(extended_entries)
    mine = next((e for e in entries if e["you"]), None)
    extended_mine = next((e for e in extended_entries if e["you"]), None)
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
        return {"id": contest_row["id"], "players": len(extended_entries), "entries": [],
                "you": {"extended": {"rank": extended_mine["rank"], "of": len(extended_entries)}}
                if extended_mine else None, "mine": None, "next_offset": None, "pars": [], "marks": {}}
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
    elif extended_mine:
        mine = {"extended": {"rank": extended_mine["rank"], "of": len(extended_entries)}}
    slots = (_json(contest_row["spec"], {}) or {}).get("slots", [])
    par_rows = []
    if slots and contest_row["kind"] not in ("sprint", "rush", "words"):
        for level, midpoint in ((3, 1025), (5, 1325), (7, 1625), (9, 1925)):
            expected = par(None, slots, rating=midpoint)
            par_rows.append({"level": level, "right": expected["right"],
                             "points": expected["points"], "rough": expected["rough"]})
        if me:
            own_level = _identity(me)["level"]
            if own_level not in (3, 5, 7, 9):
                expected = par(me, slots)
                par_rows.append({"level": own_level, "right": expected["right"],
                                 "points": expected["points"], "rough": expected["rough"]})
    return {"id": contest_row["id"], "players": players, "entries": page, "you": mine,
            "mine": mine, "next_offset": next_offset, "pars": par_rows, "marks": dict(marks)}


def _period_bounds(period: str, at: dt.date | None = None) -> tuple[str | None, str | None]:
    d = at or _now().date()
    if period == "all":
        return None, None
    if period == "7d":
        start, end = d - dt.timedelta(days=6), d + dt.timedelta(days=1)
    elif period == "week":
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
        raise HTTPException(422, "period must be 7d, week, month, season, year or all")
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
    if domain and metric == "rating":
        raise HTTPException(400, {"error": "domain applies to metric=skill"})
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
                if row["contest_kind"] in ("sprint", "rush", "words"):
                    continue
                amount = (_json(row["result"], {}) or {}).get("net", 0)
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
        if metric == "skill":
            grouped: dict[str, list[tuple[float, int]]] = defaultdict(list)
            for r in db.rows("SELECT learner,topic,rating,n FROM skill_ratings"):
                topic = progress.topics().get(r["topic"])
                if topic and (not domain or topic.domain == domain):
                    grouped[r["learner"]].append((r["rating"], r["n"]))
            values = {person: round(sum(r * n for r, n in cells) / sum(n for _, n in cells))
                      for person, cells in grouped.items() if sum(n for _, n in cells) >= 15}
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
    climb_window = None
    if metric == "climb":
        values, climb_window = _climb_cohort(learner)
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
                                          {"rated": 0})["rated"] >= 30 and db.one(
            "SELECT COUNT(*) AS n FROM sessions WHERE learner=? AND contest IS NOT NULL"
            " AND finished IS NOT NULL AND ranked=1", e["learner"])["n"] >= 3]
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
            "resets_at": end, "nearest_nonempty": None, "window": climb_window}


def _midpoint(result: dict) -> float | None:
    band = result.get("estimate") or result.get("band") or {}
    if isinstance(band, dict) and band.get("low") is not None and band.get("high") is not None:
        return (band["low"] + band["high"]) / 2
    return None


def _climb_cohort(learner: str | None) -> tuple[dict[str, float], int | None]:
    sittings: dict[str, list[float]] = defaultdict(list)
    for row in db.rows("SELECT learner,result FROM sessions WHERE finished IS NOT NULL"
                       " AND kind IN ('module','mock','diagnostic') ORDER BY finished"):
        midpoint = _midpoint(_json(row["result"], {}) or {})
        if midpoint is not None:
            sittings[row["learner"]].append(midpoint)
    if len(sittings) < 20:
        return {}, None
    first = sittings.get(learner, [None])[0] if learner else None
    window = None
    if first is not None:
        for width in (40, 80, 160):
            if sum(abs(v[0] - first) <= width for v in sittings.values()) >= 20:
                window = width
                break
    chosen = {person: v for person, v in sittings.items()
              if window is None or first is None or abs(v[0] - first) <= window}
    return {person: round(statistics.mean(v[-3:]) - v[0], 1) for person, v in chosen.items()}, window


def climb(learner: str) -> dict | None:
    values, window = _climb_cohort(learner)
    if learner not in values:
        return None
    ranked = sorted(values.items(), key=lambda pair: (-pair[1], pair[0]))
    rank = 1 + sum(value > values[learner] for value in values.values())
    first = db.rows("SELECT result FROM sessions WHERE learner=? AND finished IS NOT NULL"
                    " AND kind IN ('module','mock','diagnostic') ORDER BY finished LIMIT 1", learner)
    start = _midpoint(_json(first[0]["result"], {}) or {}) if first else None
    return {"rank": rank, "of": len(ranked), "window": window,
            "lo": start - window if start is not None and window else None,
            "hi": start + window if start is not None and window else None,
            "gain": values[learner]}


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
            "level": ratings.level_of(rating or 1000), "provisional": (profile["rated"] or 0) < 30 if profile else True,
            "climb": climb(learner)}


def ranks(learner: str) -> dict:
    snapshot = rank_snapshot(learner)
    practice_board = leaderboard("right", "7d", learner=learner)
    country_board = leaderboard("right", "7d", "country", learner=learner)
    snapshot["practice"] = practice_board["you"]
    snapshot["practice_country"] = country_board["you"]
    return snapshot


def test_rank(sid: str) -> dict | None:
    row = db.one("SELECT learner,result,finished FROM sessions WHERE id=?", sid)
    if not row or not row["finished"]:
        return None
    board = leaderboard("test", "month", learner=row["learner"])
    return {"rank": (board["you"] or {}).get("rank"), "of": board["players"],
            "climb": climb(row["learner"])}


def due_today(learner: str, tz: int = 0) -> list[dict]:
    ensure(tz=tz)
    now = _iso(_now())
    out = []
    for row in db.rows("SELECT c.* FROM contests c JOIN contest_members m"
                       " ON m.contest=COALESCE(c.series,c.id)"
                       " WHERE m.learner=? AND c.opens<=? AND c.closes>? ORDER BY c.closes", learner, now, now):
        if not db.one("SELECT 1 FROM sessions WHERE contest=? AND learner=? AND finished IS NOT NULL",
                      row["id"], learner):
            out.append({"id": row["id"], "title": row["title"], "closes": row["closes"]})
    return out


def closing_soon(learner: str) -> list[dict]:
    end = _iso(_now() + dt.timedelta(hours=24))
    return [item for item in due_today(learner) if item["closes"] <= end]


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


def _private_slots(cid: str, names: list[str], count: int, tiers: list[str], fmt: str) -> list[list]:
    catalogue = blueprint.kinds()
    choices = [(name, tier, shape) for name in names for tier, shape in catalogue[name]["kinds"]
               if tier in tiers and (fmt == "both" or fmt == shape)]
    if not choices:
        raise HTTPException(409, "no questions match these skills and settings")
    choices.sort(key=lambda cell: hashlib.sha256(f"{cid}:{cell}".encode()).digest())
    return [list(choices[i % len(choices)]) for i in range(count)]


def create_private(learner: str, body: dict) -> dict:
    title = str(body.get("title", "")).strip()
    if not 3 <= len(title) <= 60:
        raise HTTPException(422, "title must be 3–60 characters")
    count = body.get("count", 10)
    if count not in (5, 10, 15, 22):
        raise HTTPException(422, "count must be 5, 10, 15 or 22")
    minutes = body.get("minutes")
    if minutes is not None and (not isinstance(minutes, int) or not 5 <= minutes <= 70):
        raise HTTPException(422, "minutes must be 5–70")
    duration = body.get("duration", {1: "hour", 24: "day", 72: "3days", 168: "week"}.get(
        body.get("open_for"), "day"))
    lengths = {"hour": 3600, "day": 86400, "3days": 3 * 86400, "week": 7 * 86400}
    if duration not in lengths:
        raise HTTPException(422, "duration must be hour, day, 3days or week")
    repeat = body.get("repeat") or {}
    every = repeat.get("every") if isinstance(repeat, dict) else None
    rounds = repeat.get("rounds", 1) if every else 1
    if every not in (None, "day", "week") or not isinstance(rounds, int) or not 1 <= rounds <= 30:
        raise HTTPException(422, "repeat must specify day or week and 2–30 rounds")
    if every and rounds < 2:
        raise HTTPException(422, "a series needs at least two rounds")
    source = body.get("source", "skills")
    if source not in ("skills", "my_traps", "our_traps"):
        raise HTTPException(422, "unknown question source")
    if source == "our_traps" and not every:
        raise HTTPException(400, "Our open mistakes starts from round 2.")
    kinds = blueprint.kinds()
    names = body.get("templates") or []
    topics = body.get("topics") or []
    if source == "my_traps":
        names = [t["template"] for t in progress.open_traps(learner)]
    elif not names:
        names = [n for n, data in kinds.items() if data["topic"] in topics]
    names = sorted({n for n in names if n in kinds})
    if not names:
        raise HTTPException(409, "choose a skill with available questions")
    tiers = body.get("difficulty") or ["easy", "medium", "hard"]
    if not isinstance(tiers, list) or not tiers or set(tiers) - {"easy", "medium", "hard"}:
        raise HTTPException(422, "invalid difficulty")
    fmt = body.get("format", "both")
    if fmt not in ("both", "mcq", "spr"):
        raise HTTPException(422, "invalid format")
    twin = bool(body.get("twins", body.get("twin", False)))
    reveal = body.get("reveal", "each")
    if reveal not in ("each", "end"):
        raise HTTPException(422, "invalid reveal")
    now = _now()
    base = "p-" + secrets.token_hex(5)
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    code = "".join(secrets.choice(alphabet) for _ in range(6))
    while db.one("SELECT 1 FROM contests WHERE code=?", code):
        code = "".join(secrets.choice(alphabet) for _ in range(6))
    for number in range(1, rounds + 1):
        cid = base if number == 1 else f"{base}-r{number}"
        round_seconds = 86400 if every == "day" else 7 * 86400 if every == "week" else lengths[duration]
        delta = dt.timedelta(seconds=(number - 1) * round_seconds)
        opens = now + delta
        closes = opens + dt.timedelta(seconds=round_seconds)
        slots = _private_slots(cid, names, count, tiers, fmt)
        spec = {"slots": slots, "twin": twin, "rated": False, "strict": bool(body.get("strict")),
                "reveal": reveal, "source": source if number > 1 else ("skills" if source == "our_traps" else source),
                "repeat": {"every": every, "rounds": rounds} if every else None}
        db.run("INSERT INTO contests(id,kind,title,owner,code,opens,closes,count,seconds,spec,created,subject,series,round)"
               " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", cid, "private", title, learner,
               code if number == 1 else None, _iso(opens), _iso(closes), count,
               (minutes * 60 if minutes else count * 95), json.dumps(spec), _iso(now), "math",
               base if every else None, number)
    db.run("INSERT OR IGNORE INTO contest_members(contest,learner,joined) VALUES (?,?,?)", base, learner, _iso(now))
    return {"id": base, "code": code, "link": f"/compete/contest/?code={code}",
            "rounds": rounds, "opens": _iso(now)}


def join_private(learner: str, code: str) -> dict:
    row = db.one("SELECT * FROM contests WHERE code=? AND kind='private'", code.strip().upper())
    if not row:
        raise HTTPException(404, "no private contest has that code")
    rounds = db.rows("SELECT * FROM contests WHERE id=? OR series=? ORDER BY round", row["id"], row["id"])
    if all(r["closes"] <= _iso(_now()) for r in rounds):
        raise HTTPException(409, "that contest has ended")
    db.run("INSERT OR IGNORE INTO contest_members(contest,learner,joined) VALUES (?,?,?)",
           row["id"], learner, _iso(_now()))
    return {"id": row["id"], "title": row["title"], "rounds": len(rounds)}


def private_members(cid: str) -> list[str]:
    row = db.one("SELECT id,series FROM contests WHERE id=?", cid)
    if not row:
        return []
    root = row["series"] or row["id"]
    return [r["learner"] for r in db.rows("SELECT learner FROM contest_members WHERE contest=?", root)]


def series_board(series: str, sort: str = "points", viewer: str | None = None) -> dict:
    root = db.one("SELECT * FROM contests WHERE id=? AND kind='private'", series)
    if not root:
        raise HTTPException(404, "series not found")
    rounds = db.rows("SELECT id,round FROM contests WHERE id=? OR series=? ORDER BY round", series, series)
    entries = []
    for member in private_members(series):
        scores = []
        for rnd in rounds:
            run = db.one("SELECT points,result FROM sessions WHERE contest=? AND learner=?"
                         " AND finished IS NOT NULL ORDER BY points DESC LIMIT 1", rnd["id"], member)
            scores.append({"round": rnd["round"], "points": run["points"] if run else None,
                           "net": ((_json(run["result"], {}) or {}).get("net") if run else None)})
        entries.append({**_identity(member, viewer), "you": member == viewer,
                        "rounds": scores, "sat": sum(x["points"] is not None for x in scores),
                        "points": sum(x["points"] or 0 for x in scores),
                        "net": sum(x["net"] or 0 for x in scores)})
    if sort not in ("points", "net"):
        raise HTTPException(422, "sort must be points or net")
    _rank(entries, sort)
    return {"id": series, "entries": entries, "streak": series_streak(series)}


def series_streak(series: str) -> dict:
    rounds = db.rows("SELECT id,round,closes FROM contests WHERE id=? OR series=? ORDER BY round",
                    series, series)
    members = private_members(series)
    threshold = len(members) if len(members) <= 10 else math.ceil(len(members) * .75)
    run = best = 0
    for rnd in rounds:
        done = db.one("SELECT COUNT(DISTINCT learner) AS n FROM sessions WHERE contest=? AND finished IS NOT NULL",
                      rnd["id"])["n"]
        if done >= threshold and threshold:
            run += 1
            best = max(best, run)
        elif rnd["closes"] > _iso(_now()):
            break
        else:
            run = 0
    return {"current": run, "best": best}


def nudge(sender: str, target: str, cid: str) -> dict:
    row = contest(cid)
    target = person_of(target) or target
    if row["kind"] != "private" or sender == target or sender not in private_members(cid) or target not in private_members(cid):
        raise HTTPException(403, "both learners must be entrants")
    if db.one("SELECT 1 FROM nudges WHERE sender=? AND target=? AND contest=? AND round=?",
              sender, target, row["series"] or cid, row["round"] or 1):
        raise HTTPException(429, "already nudged this entrant this round")
    db.run("INSERT INTO nudges(sender,target,contest,round,at) VALUES (?,?,?,?,?)",
           sender, target, row["series"] or cid, row["round"] or 1, _iso(_now()))
    return {"sent": True}


def person_of(pid: str) -> str | None:
    return next((r["id"] for r in db.rows("SELECT id FROM learners") if _pid(r["id"]) == pid), None)


def follow(learner: str, pid: str) -> dict:
    target = person_of(pid)
    if not target or target == learner:
        raise HTTPException(404, "student not found")
    profile = db.one("SELECT board FROM learners WHERE id=?", target)
    if profile and profile["board"] in ("anon", "hidden"):
        raise HTTPException(403, "this student is not public")
    n = db.one("SELECT COUNT(*) AS n FROM follows WHERE learner=?", learner)["n"]
    if n >= 50 and not db.one("SELECT 1 FROM follows WHERE learner=? AND target=?", learner, target):
        raise HTTPException(409, "follow limit is 50")
    db.run("INSERT OR IGNORE INTO follows(learner,target,at) VALUES (?,?,?)", learner, target, _iso(_now()))
    return {"pid": pid, "following": True}


def unfollow(learner: str, pid: str) -> dict:
    target = person_of(pid)
    if target:
        db.run("DELETE FROM follows WHERE learner=? AND target=?", learner, target)
    return {"pid": pid, "following": False}


def h2h(learner: str, target: str, season: str | None = None) -> dict:
    start, end = _period_bounds("season", dt.date.fromisoformat(season) if season else None)
    a = b = ties = 0
    common = db.rows("SELECT x.contest,x.points AS ap,y.points AS bp FROM sessions x"
                     " JOIN sessions y ON y.contest=x.contest AND y.learner=? AND y.finished IS NOT NULL"
                     " AND y.ranked=1 WHERE x.learner=? AND x.finished IS NOT NULL AND x.ranked=1",
                     target, learner)
    for row in common:
        c = db.one("SELECT closes FROM contests WHERE id=?", row["contest"])
        if not c or (start and c["closes"][:10] < start) or (end and c["closes"][:10] >= end):
            continue
        a += row["ap"] > row["bp"]
        b += row["bp"] > row["ap"]
        ties += row["ap"] == row["bp"]
    return {"you": a, "them": b, "ties": ties}


def rivals(learner: str) -> dict:
    own = db.one("SELECT rating FROM learners WHERE id=?", learner)
    rating = own["rating"] if own and own["rating"] else 1000
    followed = {r["target"] for r in db.rows("SELECT target FROM follows WHERE learner=?", learner)}
    candidates = []
    for row in db.rows("SELECT id,rating,board FROM learners WHERE id!=? AND rated>0", learner):
        if row["board"] in ("anon", "hidden") or abs((row["rating"] or 1000) - rating) > 200:
            continue
        ident = _identity(row["id"], learner)
        if row["id"] in followed:
            ident["following"] = True
        common = db.one("SELECT MAX(a.finished) AS at FROM sessions a JOIN sessions b"
                        " ON b.contest=a.contest WHERE a.learner=? AND b.learner=?"
                        " AND a.finished IS NOT NULL AND b.finished IS NOT NULL", learner, row["id"])
        ident["last_shared"] = common["at"]
        ident["h2h"] = h2h(learner, row["id"])
        candidates.append(ident)
    candidates.sort(key=lambda x: x["pid"])
    candidates.sort(key=lambda x: x["last_shared"] or "", reverse=True)
    candidates.sort(key=lambda x: not x.get("following"))
    return {"rivals": candidates[:10]}
