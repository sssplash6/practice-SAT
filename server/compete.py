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
DOORS_LINE = "Doors open by 7:45 AM; check your admission ticket. Doors close at 8:00 AM."
SUPPLY_PATH = pathlib.Path(__file__).resolve().parent / "cache" / "twin_supply.json"
_SUPPLY: dict | None = None
_SUPPLY_THREAD: threading.Thread | None = None
_TRAP_CACHE: dict | None = None
_ENSURE_LOCK = threading.RLock()
_ENSURE_READY: set[tuple[str, str, str, int]] = set()
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
    _ENSURE_READY.clear()
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
    # Build the current UTC day's scheduled forms before health goes ready.
    # Shell asks for them several times; the first learner must not pay for it.
    ensure(tz=0)
    challenge.challenge(local_day().isoformat())


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
    global _SUPPLY, _TRAP_CACHE
    _SUPPLY = found
    _TRAP_CACHE = None
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


def _habit_id(norm: str) -> str | None:
    family = deps.part("habits", "family_of") or deps.part("habits", "family")
    if family is None or not norm:
        return None
    found = family(norm)
    return found.get("id") if isinstance(found, dict) else found


def _habit_catalogue() -> list[dict]:
    families = deps.part("habits", "families") or deps.part("habits", "FAMILIES")
    if families is None:
        return []
    if callable(families):
        families = families()
    if isinstance(families, dict):
        return [{"id": key, **value} for key, value in families.items()]
    return [dict(value) for value in families]


def trap_families() -> dict:
    """Families with supplied, trap-bearing slots in all three tiers."""
    global _TRAP_CACHE
    if _TRAP_CACHE is not None:
        return _TRAP_CACHE
    families = [f for f in _habit_catalogue() if f.get("id") != "slip"]
    if not families:
        _TRAP_CACHE = {"families": [], "topic_floor": 5, "window": 0, "reason": "habits_unavailable"}
        return _TRAP_CACHE
    found: dict[str, dict] = {f["id"]: {"family": f, "tiers": {t: set() for t in ("easy", "medium", "hard")},
                                     "topics": set()} for f in families}
    kinds = blueprint.kinds()
    for tier in ("easy", "medium", "hard"):
        for name in pool("trap", tier):
            info = kinds[name]
            if not any(t == tier for t, _ in info["kinds"]):
                continue
            matched = set()
            for seed in range(18):
                try:
                    item = practice.generate(name, seed)
                except Exception:
                    continue
                if item.difficulty != tier:
                    continue
                reasons = list(item.reasons) + [mistake[0] for mistake in
                                                 practice.spr_reasons(name, seed, item)]
                matched.update(_habit_id(progress.norm(reason)) for reason in reasons if reason)
            for fid in matched & found.keys():
                found[fid]["tiers"][tier].add(name)
                found[fid]["topics"].add(info["topic"])
    topic_floor = 5
    qualified = [entry for entry in found.values() if len(entry["topics"]) >= 5 and
                 all(len(entry["tiers"][tier]) >= 10 for tier in ("easy", "medium", "hard"))]
    if len(qualified) < 5:
        topic_floor = 3
        qualified = [entry for entry in found.values() if len(entry["topics"]) >= 3 and
                     all(len(entry["tiers"][tier]) >= 10 for tier in ("easy", "medium", "hard"))]
    if len(qualified) < 2:
        _TRAP_CACHE = {"families": [], "topic_floor": topic_floor, "window": 0,
                       "reason": "too_few_qualified_families", "survey": found}
        return _TRAP_CACHE
    _TRAP_CACHE = {"families": qualified, "topic_floor": topic_floor,
                   "window": min(4, len(qualified) - 1), "survey": found}
    return _TRAP_CACHE


def trap_theme(week: str, catalogue: dict | None = None) -> dict | None:
    catalogue = catalogue or trap_families()
    qualified = catalogue["families"]
    if not qualified:
        return None
    year, number = week.split("-W")
    monday = dt.date.fromisocalendar(int(year), int(number), 1)
    blocked = set()
    for back in range(1, catalogue["window"] + 1):
        previous = monday - dt.timedelta(days=7 * back)
        prev_id = f"{previous.isocalendar().year}-W{previous.isocalendar().week:02d}"
        prior = db.one("SELECT spec FROM contests WHERE id=?", "trap-" + prev_id)
        if prior:
            blocked.add((_json(prior["spec"], {}) or {}).get("family"))
        else:
            # The no-data walk is deterministic even if a past week was not opened.
            blocked.add(qualified[(monday.toordinal() // 7 - back) % len(qualified)]["family"]["id"])
    available = [entry for entry in qualified if entry["family"]["id"] not in blocked]
    if not available:
        available = qualified
    prior_start = (monday - dt.timedelta(days=7)).isoformat()
    prior_end = monday.isoformat()
    chances: Counter = Counter()
    falls: Counter = Counter()
    for attempt in db.rows("SELECT offered,reason,correct FROM attempts WHERE at>=? AND at<?"
                           " AND repeat=0 AND disputed=0", prior_start, prior_end):
        offered = {_habit_id(norm) for norm in (_json(attempt["offered"], []) or [])}
        for fid in offered:
            if fid:
                chances[fid] += 1
        if not attempt["correct"]:
            falls[_habit_id(progress.norm(attempt["reason"] or ""))] += 1
    measured = [entry for entry in available if chances[entry["family"]["id"]] >= 30]
    if measured:
        return max(measured, key=lambda entry: (falls[entry["family"]["id"]] /
                         chances[entry["family"]["id"]], -qualified.index(entry)))
    # Keep the catalogue's order while skipping themes already used by a
    # data-selected week; a plain modulo can repeat one of those themes.
    start = monday.toordinal() // 7 % len(qualified)
    return next(qualified[(start + offset) % len(qualified)]
                for offset in range(len(qualified))
                if qualified[(start + offset) % len(qualified)] in available)


def _trap_slots(week: str, theme: dict, floor: int) -> list[list]:
    chosen = []
    topics: set[str] = set()
    used: set[str] = set()
    for tier, count in (("easy", 3), ("medium", 4), ("hard", 3)):
        names = sorted(theme["tiers"][tier], key=lambda name: hashlib.sha256(
            f"{week}:{name}".encode()).digest())
        for _ in range(count):
            name = next((n for n in names if n not in used and blueprint.kinds()[n]["topic"] not in topics),
                        next((n for n in names if n not in used), None))
            if not name:
                raise HTTPException(409, "trap theme lacks supplied slots")
            used.add(name)
            topics.add(blueprint.kinds()[name]["topic"])
            formats = {fmt for t, fmt in blueprint.abilities()[name] if t == tier}
            chosen.append([name, tier, "mcq" if "mcq" in formats else "spr"])
    if len(topics) < floor:
        raise HTTPException(409, "trap theme has too few topics")
    return chosen


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
    """Serialize first builds; a second request waits for the same saved form."""
    at = at or _now()
    local = local_day(tz, at)
    monday = at.date() - dt.timedelta(days=at.weekday())
    # A swapped dependency resolver (used by optional integrations and checks)
    # may make a previously unavailable Word Sprint schedulable.
    window = (str(db.DB_PATH.resolve()), local.isoformat(), monday.isoformat(), id(deps.part))
    with _ENSURE_LOCK:
        if window not in _ENSURE_READY:
            rows = _ensure_unlocked(at, tz)
            _ENSURE_READY.add(window)
            return rows
    return [dict(r) for r in db.rows("SELECT * FROM contests WHERE closes>? ORDER BY opens", _iso(at))]


def _ensure_unlocked(at: dt.datetime | None = None, tz: int = 0) -> list[dict]:
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
        if not db.one("SELECT 1 FROM contests WHERE id=?", "rush-" + week):
            _insert("rush-" + week, "rush", "Rush · " + week, start,
                    start + dt.timedelta(days=7), [], 0,
                    extra={"mode": "three_strikes", "rated": True})
        available = deps.part("words", "sprint_available")
        if deps.part("words", "sprint_items") and (available is None or available()) and not db.one(
                "SELECT 1 FROM contests WHERE id=?", "words-" + week):
            _insert("words-" + week, "words", "Word Sprint · " + week, start,
                    start + dt.timedelta(days=7), [], 240, subject="rw",
                    extra={"rated": False, "twin": False, "mode": "word_sprint"})
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
    # the trap weeks: trap_families() builds ~16k questions on its first call in a process, so it runs only when a
    # trap-week contest is actually missing (every cold /api/shell paid it, 17.7 s for five calls; Up next, F2B)
    missing = []
    for offset in (0, 7):
        first = monday + dt.timedelta(days=offset)
        week = f"{first.isocalendar().year}-W{first.isocalendar().week:02d}"
        if not db.one("SELECT 1 FROM contests WHERE id=?", "trap-" + week):
            missing.append((first, week, "trap-" + week))
    themes = trap_families() if missing else {"families": []}
    if themes["families"]:
        for first, week, cid in missing:
            theme = trap_theme(week, themes)
            slots = _trap_slots(week, theme, themes["topic_floor"])
            family = theme["family"]
            _insert(cid, "trap", "Trap of the week · " + family["name"],
                    dt.datetime.combine(first, dt.time(), dt.timezone.utc),
                    dt.datetime.combine(first + dt.timedelta(days=7), dt.time(12), dt.timezone.utc),
                    slots, 950, extra={"family": family["id"], "tell": family["tell"],
                                       "topic_floor": themes["topic_floor"]})
    return [dict(r) for r in db.rows("SELECT * FROM contests WHERE closes>? ORDER BY opens", _iso(at))]


def contest(cid: str, tz: int = 0):
    if cid == "daily":
        cid = "daily-" + local_day(tz).isoformat()
    ensure(tz=tz)
    row = db.one("SELECT * FROM contests WHERE id=?", cid)
    if not row:
        raise HTTPException(404, "contest not found")
    return row


def twin_questions(learner: str, cid: str, slots: list[list], start_slot: int = 1,
                   family: str | None = None) -> list[dict]:
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
            if family and not any(_habit_id(norm) == family for norm in
                                  progress.offered_of(practice.to_question(candidate, i))):
                b.keep(candidate)
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


def rush_start(learner: str, cid: str, domain: str = "all") -> dict:
    """A repeatable rated run; each next item is chosen after its verdict."""
    from . import drill
    row = contest(cid)
    if row["kind"] != "rush":
        raise HTTPException(404, "not a Rush contest")
    domains = blueprint.by_domain()
    if domain != "all" and domain not in domains:
        raise HTTPException(422, "unknown Rush domain")
    current = db.one("SELECT * FROM sessions WHERE learner=? AND contest=? AND kind='rush'"
                     " AND finished IS NULL ORDER BY started DESC LIMIT 1", learner, row["id"])
    if current:
        return {"session": current["id"], "runner": "session", **rush_next(current["id"], learner)}
    skills = [r["rating"] for r in db.rows("SELECT rating FROM skill_ratings WHERE learner=?", learner)]
    if domain != "all":
        topics = {practice.topic_of(name) for name in domains[domain]}
        skills = [ratings.skill(learner, topic)["rating"] for topic in topics]
    skill_rating = statistics.mean(skills) if skills else 1000
    placing = db.one("SELECT COUNT(*) AS n FROM attempts WHERE learner=? AND repeat=0", learner)["n"] < 8
    target = 700 if placing else skill_rating - 300
    sid = secrets.token_urlsafe(16)
    preferences = deps.part("prefs", "get")
    timing = preferences(learner).get("contest_timing", "follow") if preferences else "official"
    if timing == "follow":
        timing = preferences(learner).get("test_timing", "official") if preferences else "official"
    factor = {"official": 1, "x1.5": 1.5, "x2": 2}.get(timing, 1)
    cfg = {"contest": row["id"], "domain": domain, "target": target, "strikes": 0,
           "strike_reasons": [], "top_bank": False, "turn": 0, "last_rating": None,
           "last_right": None, "tz": 0, "source": "rush", "timing_factor": factor}
    with db.atomic():
        existing = db.one("SELECT id FROM sessions WHERE learner=? AND contest=? AND kind='rush'"
                          " AND finished IS NULL ORDER BY started DESC LIMIT 1", learner, row["id"])
        if existing:
            sid = existing["id"]
        else:
            db.run("INSERT INTO sessions(id,kind,learner,started,questions,answers,cfg,result,contest,subject,ranked)"
                   " VALUES (?,?,?,?,'[]','{}',?,'{}',?,'math',1)", sid, "rush", learner,
                   _iso(_now()), json.dumps(cfg), row["id"])
    return {"session": sid, "runner": "session", **rush_next(sid, learner)}


def _rush_row(sid: str, learner: str):
    row = db.one("SELECT * FROM sessions WHERE id=? AND learner=? AND kind='rush'", sid, learner)
    if not row:
        raise HTTPException(404, "Rush run not found")
    return row


def rush_next(sid: str, learner: str) -> dict:
    from . import drill
    row = _rush_row(sid, learner)
    cfg = _json(row["cfg"], {}) or {}
    served = _questions(row)
    answers = _json(row["answers"], {}) or {}
    if row["finished"]:
        return {"done": True, "result": _json(row["result"], {})}
    if served and served[-1]["id"] not in answers:
        return {"question": drill.public(served[-1]), "target": round(cfg["target"]),
                "item_rating": served[-1]["item_rating"],
                "strikes": cfg["strikes"], "top_bank": cfg["top_bank"]}
    allowed = set(blueprint.by_domain().get(cfg["domain"], ())) if cfg["domain"] != "all" else None
    used = {q["key"] for q in served}
    pairs = [(name, tier, ratings.item(name, tier)[0]) for name, shapes in blueprint.abilities().items()
             if name not in used and (allowed is None or name in allowed)
             for tier in {t for t, _ in shapes}]
    if not pairs:
        return rush_finish(sid, learner)
    previous = cfg.get("last_rating")
    direction = cfg.get("last_right")
    # The lobby displays integer ratings, so direction must be strict at that
    # same precision. Comparing raw candidates with a rounded previous value
    # can serve 794 immediately after 794.
    directional = [(name, tier, value) for name, tier, value in pairs if previous is None or
                   (round(value) > previous if direction else round(value) < previous)]
    if not directional:
        cfg["top_bank"] = True
        directional = pairs
    preferred = sorted(directional, key=lambda cell: (abs(cell[2] - cfg["target"]), cell[0]))
    # All-domains runs rotate through the four Math domains. If the next one
    # has no eligible fresh pair, the nearest pair in another domain keeps the
    # run moving instead of repeating an item.
    if cfg["domain"] == "all":
        domain_order = tuple(challenge.MIX)
        next_domain = domain_order[cfg["turn"] % len(domain_order)]
        preferred.sort(key=lambda cell: (blueprint.kinds()[cell[0]]["domain"] != next_domain,
                                         abs(cell[2] - cfg["target"]), cell[0]))
    b = drill._builder(learner, dedupe="question")
    chosen = None
    for name, tier, value in preferred:
        card = drill._fresh(b, name, {tier}, {"formats": ["mcq", "spr"]})
        if card:
            chosen = card, value
            break
    if not chosen:
        return rush_finish(sid, learner)
    card, item_rating = chosen
    q = practice.to_question(card, len(served) + 1)
    q["id"] = f"r{len(served) + 1:03d}"
    q["item_rating"] = round(item_rating)
    q["item_code"] = "L" + str(ratings.level_of(item_rating))
    q["level"] = q["item_code"]
    q["budget_ms"] = drill.budget_ms(card.key, q["difficulty"])
    served.append(q)
    cfg["turn"] += 1
    db.run("UPDATE sessions SET questions=?,cfg=? WHERE id=?", json.dumps(served), json.dumps(cfg), sid)
    return {"question": drill.public(q), "target": round(cfg["target"]),
            "item_rating": q["item_rating"], "strikes": cfg["strikes"],
            "top_bank": cfg["top_bank"]}


def rush_answer(sid: str, learner: str, qid: str, answer, ms: int | None = None) -> dict:
    row = _rush_row(sid, learner)
    if row["finished"]:
        raise HTTPException(409, "Rush run is finished")
    questions = _questions(row)
    q = questions[-1] if questions and questions[-1]["id"] == qid else None
    if q is None:
        raise HTTPException(409, "answer the current Rush item")
    if not db.set_answer(sid, qid, answer, only_new=True):
        raise HTTPException(409, "Rush item already answered")
    feedback = progress.record(learner, sid, q, answer, ms)
    cfg = _json(db.one("SELECT cfg FROM sessions WHERE id=?", sid)["cfg"], {}) or {}
    right = bool(feedback["correct"])
    slow = ms is not None and ms > 1.5 * q["budget_ms"] * cfg.get("timing_factor", 1)
    cfg["target"] += 60 if right else -120
    cfg["last_rating"] = q["item_rating"]
    cfg["last_right"] = right
    cfg["strikes"] += int(not right) + int(slow)
    if not right:
        cfg["strike_reasons"].append({"template": q["key"], "reason": feedback["reason"]})
    if slow:
        cfg["strike_reasons"].append({"template": q["key"], "reason": "slow"})
    db.run("UPDATE sessions SET cfg=? WHERE id=?", json.dumps(cfg), sid)
    if cfg["strikes"] >= 3:
        next_item = rush_finish(sid, learner)
    else:
        next_item = rush_next(sid, learner)
    return {"correct": right, "reason": feedback["reason"], "strikes": cfg["strikes"],
            "target": round(cfg["target"]), **next_item}


def rush_finish(sid: str, learner: str) -> dict:
    row = _rush_row(sid, learner)
    if row["finished"]:
        return {"done": True, "result": _json(row["result"], {})}
    cfg = _json(row["cfg"], {}) or {}
    answers = _json(row["answers"], {}) or {}
    questions = _questions(row)
    right = sum(scoring.is_correct(q, answers[q["id"]]) for q in questions if q["id"] in answers)
    top = max((q["item_rating"] for q in questions if q["id"] in answers and
               scoring.is_correct(q, answers[q["id"]])), default=None)
    result = {"right": right, "asked": len(answers), "top_item": top,
              "strikes": cfg["strike_reasons"], "top_bank": cfg["top_bank"],
              "domain": cfg["domain"]}
    db.run("UPDATE sessions SET finished=?,result=?,points=?,secs=?,ranked=1 WHERE id=?",
           _iso(_now()), json.dumps(result), right, clock(row)["used"], sid)
    return {"done": True, "result": result}


def rush_board(cid: str, viewer: str | None = None, domain: str = "all") -> dict:
    best = {}
    for row in db.rows("SELECT * FROM sessions WHERE contest=? AND kind='rush' AND finished IS NOT NULL"
                       " AND ranked=1", cid):
        result = _json(row["result"], {}) or {}
        if domain != "all" and result.get("domain") != domain:
            continue
        prior = best.get(row["learner"])
        if prior is None or (result.get("right", 0), result.get("top_item") or 0) > (
                prior[1].get("right", 0), prior[1].get("top_item") or 0):
            best[row["learner"]] = row, result
    entries = [{**_identity(person, viewer), "right": result.get("right", 0),
                "top_item": result.get("top_item"), "domain": result.get("domain"),
                "you": person == viewer, "runs": db.one("SELECT COUNT(*) AS n FROM sessions"
                " WHERE contest=? AND learner=? AND kind='rush' AND finished IS NOT NULL", cid, person)["n"]}
               for person, (_, result) in best.items()]
    entries.sort(key=lambda e: (-e["right"], -(e["top_item"] or 0), e["pid"]))
    for index, entry in enumerate(entries):
        prior = entries[index - 1] if index else None
        entry["rank"] = prior["rank"] if prior and (prior["right"], prior["top_item"]) == (
            entry["right"], entry["top_item"]) else index + 1
    return {"id": cid, "domain": domain, "players": len(entries), "entries": entries,
            "you": next((entry for entry in entries if entry["you"]), None)}


def word_start(learner: str, cid: str) -> dict:
    """Start one R&W sprint without writing a Math attempt or rating."""
    row = contest(cid)
    if row["kind"] != "words":
        raise HTTPException(404, "not a Word Sprint")
    provider = deps.part("words", "sprint_items")
    if provider is None:
        raise HTTPException(503, "Words Sprint items are pending")
    prior = db.one("SELECT id FROM sessions WHERE learner=? AND contest=? AND kind='words'"
                   " AND finished IS NULL ORDER BY started DESC LIMIT 1", learner, cid)
    if prior:
        return {"session": prior["id"], "runner": "words", **word_next(prior["id"], learner)}
    estimate = deps.part("words", "estimate")
    placement = estimate(learner) if estimate else {}
    # W10 reports an estimated vocabulary count and six band sizes, rather
    # than a single sprint band. Start in one of five bands according to the
    # estimated share known; the provider raises that band every five items.
    total = sum(int(row.get("size") or 0) for row in placement.get("bands", ()))
    known = int(placement.get("n") or 0)
    level = 1 + min(4, max(0, 5 * known // total)) if total else 1
    # Template order is shared across entrants; the Words provider uses the
    # learner code only to vary each rendered passage and its options.
    seed = int.from_bytes(hashlib.sha256(cid.encode()).digest()[:4], "big")
    items = provider(learner, seed, 80, level)
    if not isinstance(items, list) or not items or any(
            item.get("kind") not in ("incontext", "transition") or
            not isinstance(item.get("choices"), list) or len(item["choices"]) != 4 or
            item.get("answer_index") not in range(4) for item in items):
        raise HTTPException(409, "Words Sprint provider returned no SAT-form items")
    preferences = deps.part("prefs", "get")
    settings = preferences(learner) if preferences else {}
    timing = settings.get("contest_timing", "follow")
    if timing == "follow":
        timing = settings.get("test_timing", "official")
    seconds = round(240 * {"official": 1, "x1.5": 1.5, "x2": 2}.get(timing, 1))
    sid = secrets.token_urlsafe(16)
    questions = [{**item, "id": f"w{i:03d}"} for i, item in enumerate(items, 1)]
    with db.atomic():
        existing = db.one("SELECT id FROM sessions WHERE learner=? AND contest=? AND kind='words'"
                          " AND finished IS NULL ORDER BY started DESC LIMIT 1", learner, cid)
        if existing:
            sid = existing["id"]
        else:
            db.ensure_learner(learner)
            db.run("INSERT INTO sessions(id,kind,learner,started,questions,answers,cfg,result,contest,subject,ranked)"
                   " VALUES (?,?,?,? ,?,'{}',?,'{}',?,'rw',1)", sid, "words", learner, _iso(_now()),
                   json.dumps(questions), json.dumps({"mode": "word_sprint", "seed": seed,
                                                       "seconds": seconds, "timing": timing}), cid)
    return {"session": sid, "runner": "words", **word_next(sid, learner)}


def _word_row(sid: str, learner: str):
    row = db.one("SELECT * FROM sessions WHERE id=? AND learner=? AND kind='words'"
                 " AND json_extract(cfg,'$.mode')='word_sprint'", sid, learner)
    if not row:
        raise HTTPException(404, "Word Sprint run not found")
    return row


def word_next(sid: str, learner: str) -> dict:
    row = _word_row(sid, learner)
    if row["finished"]:
        return {"done": True, "result": _json(row["result"], {})}
    cfg = _json(row["cfg"], {}) or {}
    left = max(0, cfg["seconds"] - round((_now() - dt.datetime.fromisoformat(row["started"])).total_seconds()))
    answers = _json(row["answers"], {}) or {}
    questions = _questions(row)
    if not left or len(answers) >= len(questions):
        return word_finish(sid, learner)
    item = questions[len(answers)]
    return {"question": {key: item[key] for key in ("id", "kind", "stem", "text", "choices")
                         if key in item}, "left": left, "answered": len(answers),
            "score": round(sum(1 if value["correct"] else -1 / 3 if not value["skip"] else 0
                               for value in answers.values()), 1)}


def word_answer(sid: str, learner: str, qid: str, choice: int | None,
                ms: int | None = None) -> dict:
    row = _word_row(sid, learner)
    if row["finished"]:
        raise HTTPException(409, "Word Sprint is finished")
    cfg = _json(row["cfg"], {}) or {}
    if (_now() - dt.datetime.fromisoformat(row["started"])).total_seconds() >= cfg["seconds"]:
        word_finish(sid, learner)
        raise HTTPException(409, "Word Sprint time is up")
    questions = _questions(row)
    answers = _json(row["answers"], {}) or {}
    if len(answers) >= len(questions) or questions[len(answers)]["id"] != qid:
        raise HTTPException(409, "answer the current Word Sprint item")
    if choice is not None and (type(choice) is not int or choice not in range(4)):
        raise HTTPException(422, "choice is an index from 0 to 3 or null to skip")
    item = questions[len(answers)]
    right = choice is not None and choice == item["answer_index"]
    trap = ((item.get("traps") or [None] * 4)[choice] if choice is not None and not right else None)
    with db.atomic():
        if not db.set_answer(sid, qid, {"choice": choice, "correct": right,
                                        "skip": choice is None, "trap": trap}, only_new=True):
            raise HTTPException(409, "Word Sprint item already answered")
        if choice is not None:
            grade = deps.part("words", "grade")
            if grade:
                grade(learner, item["word"], right, mode="sprint", kind=item["kind"],
                      ms=ms, session=sid, given=item["choices"][choice],
                      confusion=trap, template=item.get("template"), seed=item.get("seed"))
            if not right:
                record_miss = deps.part("words", "record_contest_miss")
                if record_miss:
                    record_miss(learner, item["word"], trap)
    return {"correct": right, "skip": choice is None,
            "reason": item.get("reasons", [None] * 4)[choice] if choice is not None else None,
            **word_next(sid, learner)}


def word_finish(sid: str, learner: str) -> dict:
    row = _word_row(sid, learner)
    if row["finished"]:
        return {"done": True, "result": _json(row["result"], {})}
    answers = _json(row["answers"], {}) or {}
    right = sum(bool(a["correct"]) for a in answers.values())
    wrong = sum(not a["correct"] and not a["skip"] for a in answers.values())
    skipped = sum(bool(a["skip"]) for a in answers.values())
    traps = Counter(a["trap"] for a in answers.values() if a.get("trap"))
    result = {"score": round(right - wrong / 3, 1), "right": right, "wrong": wrong,
              "skipped": skipped, "traps": [{"trap": key, "label": key, "n": n}
                                            for key, n in traps.most_common()]}
    db.run("UPDATE sessions SET finished=?,result=?,points=?,secs=?,ranked=1 WHERE id=?",
           _iso(_now()), json.dumps(result), result["score"],
           round((_now() - dt.datetime.fromisoformat(row["started"])).total_seconds()), sid)
    return {"done": True, "result": result}


def word_board(cid: str, viewer: str | None = None) -> dict:
    best: dict[str, tuple] = {}
    runs: Counter = Counter()
    for row in db.rows("SELECT * FROM sessions WHERE contest=? AND kind='words'"
                       " AND finished IS NOT NULL AND ranked=1", cid):
        result = _json(row["result"], {}) or {}
        runs[row["learner"]] += 1
        prior = best.get(row["learner"])
        if prior is None or (result.get("score", 0), result.get("right", 0)) > (
                prior[1].get("score", 0), prior[1].get("right", 0)):
            best[row["learner"]] = row, result
    entries = [{**_identity(person, viewer), "score": result["score"],
                "right": result["right"], "wrong": result["wrong"],
                "runs": runs[person], "you": person == viewer}
               for person, (_, result) in best.items()]
    entries.sort(key=lambda e: (-e["score"], -e["right"], e["pid"]))
    for index, entry in enumerate(entries):
        prior = entries[index - 1] if index else None
        entry["rank"] = prior["rank"] if prior and (prior["score"], prior["right"]) == (
            entry["score"], entry["right"]) else index + 1
    return {"id": cid, "subject": "rw", "players": len(entries), "entries": entries,
            "you": next((entry for entry in entries if entry["you"]), None)}


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
    if contest_row["kind"] == "trap":
        family = spec["family"]
        chances = sum(any(_habit_id(norm) == family for norm in progress.offered_of(q)) for q in qs)
        caught = sum(_habit_id(progress.norm(a["reason"] or "")) == family
                     for a in attempts.values() if not a["correct"])
        peers = [(_json(peer["result"], {}) or {}).get("trap", {}).get("resisted") for peer in
                 db.rows("SELECT result FROM sessions WHERE contest=? AND ranked=1"
                         " AND finished IS NOT NULL AND id!=?", row["contest"], row["id"])]
        field = [value for value in peers if value is not None]
        result["trap"] = {"family": family, "resisted": max(0, chances - caught),
                          "chances": chances, "field_mean": round(statistics.mean(field), 1) if field else None}
    previous = [s["points"] for s in db.rows("SELECT s.points FROM sessions s"
                " JOIN contests c ON c.id=s.contest WHERE s.learner=? AND s.id!=?"
                " AND c.kind=? AND s.finished IS NOT NULL AND s.points IS NOT NULL AND s.ranked=1",
                row["learner"], row["id"], contest_row["kind"])]
    best = max(previous, default=None)
    result["records_new"] = ([{"kind": contest_row["kind"], "value": points, "was": best}]
                             if ranked and (best is None or points > best) else [])
    if cfg.get("race"):
        race = cfg["race"]
        opponent = db.one("SELECT points FROM sessions WHERE id=?", race.get("sid")) if race.get("sid") else None
        them = opponent["points"] if opponent else race.get("points")
        if them is not None:
            result["race"] = {"them": them, "you": points, "won": points > them,
                              "label": race["label"]}
    db.run("UPDATE sessions SET points=?,secs=?,ranked=?,unranked_why=?,result=? WHERE id=?",
           points, used, int(ranked), why, json.dumps(result), row["id"])
    return result


def records(learner: str) -> dict:
    """Personal contest bests and the permanent weekly podium ledger."""
    rows = db.rows("SELECT s.*,c.kind AS contest_kind FROM sessions s JOIN contests c ON c.id=s.contest"
                   " WHERE s.learner=? AND s.finished IS NOT NULL AND s.ranked=1 ORDER BY s.finished", learner)
    best: dict[str, dict] = {}
    for row in rows:
        kind = row["contest_kind"]
        value = row["points"] or 0
        if kind not in best or value > best[kind]["value"]:
            best[kind] = {"kind": kind, "value": value, "at": row["finished"], "session": row["id"]}
        if kind == "daily" and (_json(row["result"], {}) or {}).get("right") == 10:
            secs = row["secs"] or 0
            if secs and ("fastest_daily" not in best or secs < best["fastest_daily"]["value"]):
                best["fastest_daily"] = {"kind": "fastest_daily", "value": secs,
                                         "at": row["finished"], "session": row["id"]}
    rating = db.one("SELECT rating FROM learners WHERE id=?", learner)
    best["peak_rating"] = {"kind": "peak_rating", "value": round(rating["rating"] or 1000) if rating else 1000}
    best["challenge_streak"] = {"kind": "challenge_streak", "value": challenge_streak(learner)["best"]}
    podiums = db.rows("SELECT kind,period,board,place FROM champions WHERE learner=? ORDER BY period DESC", learner)
    return {"bests": best, "podiums": [dict(row) for row in podiums]}


def debrief(sid: str, tz: int = 0) -> dict:
    """Price each lost slot, its misconception and the places one fix buys."""
    sitting = db.one("SELECT * FROM sessions WHERE id=?", sid)
    if not sitting or not sitting["contest"] or not sitting["finished"]:
        raise HTTPException(403, "finish your contest first")
    finish_contest(sitting)
    sitting = db.one("SELECT * FROM sessions WHERE id=?", sid)
    contest_row = db.one("SELECT * FROM contests WHERE id=?", sitting["contest"])
    spec = _json(contest_row["spec"], {}) or {}
    questions = _questions(sitting)
    attempts = {r["qid"]: r for r in db.rows("SELECT * FROM attempts WHERE session=?"
                                              " ORDER BY id", sid)}
    causes = progress.causes(sitting["learner"], tz, session=sid).get("per_q", {})
    cfg = _json(sitting["cfg"], {}) or {}
    timing = {"official": 1, "x1.5": 1.5, "x2": 2}.get(cfg.get("timing"), 1)
    slots = spec.get("slots") or [[q["key"], q["difficulty"], q["type"]] for q in questions]
    paced = contest_row["kind"] not in ("sprint", "rush", "words")
    max_points = sum({"easy": 10, "medium": 20, "hard": 30}.get(slot[1], 20) + (5 if paced else 0)
                     for slot in slots) + (10 if paced else 0)
    board_rows = board(sitting["contest"], sitting["learner"], limit=100)["entries"]
    others = [entry["points"] for entry in board_rows if not entry["you"]]
    current_rank = 1 + sum(value > (sitting["points"] or 0) for value in others) if len(others) else None
    def rank_if(gain: int) -> int | None:
        return 1 + sum(value > (sitting["points"] or 0) + gain for value in others) if len(others) else None
    lost = []
    by_norm: Counter = Counter()
    per = []
    for index, slot in enumerate(slots):
        q = questions[index] if index < len(questions) else None
        qid = q["id"] if q else f"c{index + 1:02d}"
        key, tier = slot[0], slot[1]
        a = attempts.get(qid)
        worth = {"easy": 10, "medium": 20, "hard": 30}.get(tier, 20)
        budget = (q.get("budget_ms") if q else None) or {"easy": 65_000, "medium": 95_000,
                                                        "hard": 126_000}.get(tier, 95_000)
        budget *= timing
        elapsed = (a["sms"] if a["sms"] is not None else a["ms"]) if a else None
        on_pace = elapsed is not None and elapsed <= budget
        flag = cfg.get("flags", {}).get(qid, {})
        right = bool(a and a["correct"] and not a["void"] and
                     (not flag or flag.get("status") == "confirmed"))
        norm = progress.norm(a["reason"]) if a and a["reason"] else None
        topic = (q or {}).get("topic") or practice.topic_of(key)
        if right:
            if paced and not on_pace:
                lost.append({"qid": qid, "slot": index + 1, "kind": "pace", "template": key,
                             "tier": tier, "topic": topic, "norm": None, "label": "Over budget",
                             "pts": 5, "rank_if": rank_if(5),
                             "places": current_rank - rank_if(5) if current_rank else None,
                             "rushed": False})
        else:
            kind = "void" if a and (a["void"] or (flag and flag.get("status") != "confirmed")) else \
                (causes.get(qid) or {}).get("cause", "trap") if a else "skip"
            # A missed paced answer loses its possible pace bonus in that row.
            amount = worth + (5 if paced and a and on_pace and kind not in ("skip", "void") else 0)
            lost.append({"qid": qid, "slot": index + 1, "kind": kind, "template": key,
                         "tier": tier, "topic": topic, "norm": norm, "label": norm or kind.title(),
                         "pts": amount, "rank_if": rank_if(amount),
                         "places": current_rank - rank_if(amount) if current_rank else None,
                         "rushed": bool(a and elapsed is not None and elapsed < budget / 4),
                         "fix": {"from_session": sid, "only": [qid], "each": 3, "source": "twin",
                                 "parent": sid, "want": {key: norm}} if norm else None})
            if norm:
                by_norm[norm] += amount
            if paced and not (a and on_pace and kind not in ("skip", "void")):
                lost.append({"qid": qid, "slot": index + 1, "kind": "pace", "template": key,
                             "tier": tier, "topic": topic, "norm": None, "label": "Pace bonus",
                             "pts": 5, "rank_if": rank_if(5),
                             "places": current_rank - rank_if(5) if current_rank else None,
                             "rushed": False})
        per.append({"slot": index + 1, "cause": "right" if right else kind, "lost": 0 if right else worth,
                    "budget_ms": budget, "ms": elapsed})
    result = _json(sitting["result"], {}) or {}
    if paced and not result.get("points_parts", {}).get("finish"):
        lost.append({"qid": None, "slot": len(slots) + 1, "kind": "finish", "template": None,
                     "tier": None, "topic": None, "norm": None, "label": "Finish bonus", "pts": 10,
                     "rank_if": rank_if(10), "places": current_rank - rank_if(10) if current_rank else None,
                     "rushed": False})
    lost.sort(key=lambda item: (-(item["places"] or 0), -item["pts"], item["slot"]))
    if sum(item["pts"] for item in lost) != max_points - (sitting["points"] or 0):
        raise RuntimeError("contest debrief does not reconcile with its points")
    return {"subject": contest_row["subject"], "max": max_points, "points": sitting["points"],
            "rank": current_rank, "players": len(others) + 1, "lost": lost, "slots": per,
            "by_norm": [{"norm": norm, "label": norm, "pts": pts,
                         "slots": sum(item["norm"] == norm for item in lost)}
                        for norm, pts in by_norm.most_common()],
            "all_right_rank": rank_if(max_points - (sitting["points"] or 0))}


def rematch_items(sitting) -> tuple[list[list], list[dict]]:
    """Deal fresh exact twins of missed, skipped and voided slots with their trap."""
    row = db.one("SELECT * FROM contests WHERE id=?", sitting["contest"])
    slots = (_json(row["spec"], {}) or {}).get("slots") or [
        [q["key"], q["difficulty"], q["type"]] for q in _questions(sitting)]
    originals = _questions(sitting)
    attempts = {a["qid"]: a for a in db.rows("SELECT * FROM attempts WHERE session=?", sitting["id"])}
    b = practice.Builder(sitting["learner"], *db.seen_for(sitting["learner"]), dedupe="question")
    items = []
    mapping = []
    for index, (key, tier, fmt) in enumerate(slots):
        original = originals[index] if index < len(originals) else None
        qid = original["id"] if original else f"c{index + 1:02d}"
        attempt = attempts.get(qid)
        if attempt and attempt["correct"] and not attempt["void"]:
            continue
        norm = progress.norm(attempt["reason"]) if attempt and attempt["reason"] else None
        picked = None
        for _ in range(600 if norm else 100):
            card = blueprint.draw_matching(b, key, tier, fmt, tries=20)
            if not card:
                # A twenty-seed batch can miss a valid tier/format even when
                # later seeds supply it; the Builder has advanced its cursor.
                continue
            if original and card.seed == original["seed"]:
                b.keep(card)
                continue
            offered = progress.offered_of(practice.to_question(card, index + 1))
            if norm and norm not in offered:
                b.keep(card)
                continue
            picked = card
            b.keep(card)
            break
        if not picked:
            raise HTTPException(409, {"reason": "rematch_supply", "slot": index + 1,
                                      "template": key, "norm": norm})
        items.append([key, picked.seed])
        mapping.append({"original": qid, "template": key, "tier": tier, "format": fmt,
                        "norm": norm, "pts": {"easy": 10, "medium": 20, "hard": 30}.get(tier, 20)})
    return items, mapping


def rematch_status(sitting) -> dict:
    cfg = _json(sitting["cfg"], {}) or {}
    sid = cfg.get("rematch_session")
    status = {"due": cfg.get("rematch_due"), "session": sid, "won_back": None, "of": None}
    if not sid:
        return status
    other = db.one("SELECT finished,cfg FROM sessions WHERE id=? AND learner=?", sid, sitting["learner"])
    if not other:
        return status
    mapping = (_json(other["cfg"], {}) or {}).get("rematch_map", [])
    status["of"] = sum(item["pts"] for item in mapping)
    if other["finished"]:
        right = {r["qid"] for r in db.rows("SELECT qid FROM attempts WHERE session=?"
                                            " AND correct=1 AND void IS NULL", sid)}
        status["won_back"] = sum(item["pts"] for index, item in enumerate(mapping, 1)
                                 if f"d{index:03d}" in right)
        status["due"] = None
    return status


def traps_index(learner: str) -> list[dict]:
    catalog = _habit_catalogue()
    if not catalog:
        return []
    today = _now().date()
    this_week = today - dt.timedelta(days=today.weekday())
    last_week = this_week - dt.timedelta(days=7)
    cutoff = (today - dt.timedelta(days=30)).isoformat()
    mine_chances: Counter = Counter()
    mine_falls: Counter = Counter()
    templates: dict[str, set[str]] = defaultdict(set)
    field: dict[str, Counter] = defaultdict(Counter)
    for a in db.rows("SELECT learner,template,offered,reason,correct,at FROM attempts"
                     " WHERE at>=? AND repeat=0 AND disputed=0", cutoff):
        offered = {_habit_id(norm) for norm in (_json(a["offered"], []) or [])}
        offered.discard(None)
        period = "this" if a["at"][:10] >= this_week.isoformat() else "last" if a["at"][:10] >= last_week.isoformat() else "older"
        chosen = _habit_id(progress.norm(a["reason"] or "")) if not a["correct"] else None
        for family in offered:
            if a["learner"] == learner:
                mine_chances[family] += 1
                templates[family].add(a["template"])
                mine_falls[family] += chosen == family
            field[family][period + "_chances"] += 1
            field[family][period + "_falls"] += chosen == family
    out = []
    for descriptor in catalog:
        fid = descriptor["id"]
        current = field[fid]["this_falls"] / field[fid]["this_chances"] if field[fid]["this_chances"] else 0
        previous = field[fid]["last_falls"] / field[fid]["last_chances"] if field[fid]["last_chances"] else 0
        own_share = mine_falls[fid] / mine_chances[fid] if mine_chances[fid] else None
        out.append({"family": fid, "name": descriptor["name"], "tell": descriptor["tell"],
                    "field_share": round(current, 3), "field_move": round(current - previous, 3),
                    "you_share": round(own_share, 3) if own_share is not None else None,
                    "chances": mine_chances[fid], "proven": mine_chances[fid] >= 5 and
                    len(templates[fid]) >= 3 and mine_falls[fid] == 0})
    return out


def week_line(learner: str) -> dict:
    today = _now().date()
    end = today - dt.timedelta(days=today.weekday())
    start = end - dt.timedelta(days=7)
    rows = db.rows("SELECT s.points,s.result,c.kind FROM sessions s JOIN contests c ON c.id=s.contest"
                   " WHERE s.learner=? AND s.finished>=? AND s.finished<? AND s.ranked=1",
                   learner, start.isoformat(), end.isoformat())
    kinds = Counter(r["kind"] for r in rows)
    points = sum(r["points"] or 0 for r in rows)
    record_count = sum(len((_json(r["result"], {}) or {}).get("records_new", [])) for r in rows)
    return {"week": f"{start.isocalendar().year}-W{start.isocalendar().week:02d}",
            "daily": kinds["daily"], "weekly": kinds["weekly"], "points": points,
            "records": record_count, "text": f"Last week: {kinds['daily']} Dailies · "
            f"{kinds['weekly']} Weekly · {points} pts · {record_count} records"}


def season_recap(learner: str, season: str | None = None) -> dict:
    if season is None:
        previous = [day for day in SAT_DATES if day < _now().date().isoformat()]
        if not previous:
            raise HTTPException(404, "no finished season")
        season = "road-" + previous[-1]
    if not season.startswith("road-") or season[5:] not in SAT_DATES:
        raise HTTPException(404, "season not found")
    start, end, _, closed = period_window("season", season)
    if not closed:
        raise HTTPException(409, "season is still live")
    rows = db.rows("SELECT s.*,c.kind AS contest_kind FROM sessions s JOIN contests c ON c.id=s.contest"
                   " WHERE s.learner=? AND s.finished>=? AND s.finished<? ORDER BY s.finished", learner, start, end)
    rated = [(_json(row["result"], {}) or {}) for row in rows if row["ranked"]]
    before = next((r["rating_before"] for r in rated if r.get("rating_before") is not None), None)
    after = next((r["rating_after"] for r in reversed(rated) if r.get("rating_after") is not None), None)
    closed_traps = db.one("SELECT COUNT(*) AS n FROM traps WHERE learner=? AND closed>=? AND closed<?",
                          learner, start, end)["n"]
    titles = [dict(r) for r in db.rows("SELECT kind,period,board,place FROM champions WHERE learner=?"
                                        " AND period=?", learner, season)]
    return {"season": season, "contests": len(rows), "points": sum(r["points"] or 0 for r in rows),
            "rating_before": before, "rating_after": after, "mistakes_closed": closed_traps,
            "best_finish": min((board(r["contest"], learner)["you"]["rank"] for r in rows
                                if r["ranked"] and board(r["contest"], learner)["you"]), default=None),
            "titles": titles}


def final_focus(learner: str) -> dict | None:
    """The Final's three costly traps and topics too slow to start with on test day."""
    row = db.one("SELECT s.*,c.spec FROM sessions s JOIN contests c ON c.id=s.contest"
                 " WHERE s.learner=? AND c.kind='final' AND s.finished IS NOT NULL"
                 " ORDER BY s.finished DESC LIMIT 1", learner)
    if not row:
        return None
    questions = _questions(row)
    mistakes: Counter = Counter()
    slow_topics: Counter = Counter()
    for q in questions:
        attempt = db.one("SELECT correct,reason,COALESCE(sms,ms) AS ms FROM attempts"
                         " WHERE session=? AND qid=? ORDER BY id LIMIT 1", row["id"], q["id"])
        if not attempt or attempt["correct"]:
            continue
        if attempt["reason"]:
            mistakes[progress.norm(attempt["reason"])] += {"easy": 10, "medium": 20,
                                                              "hard": 30}.get(q["difficulty"], 20)
        budget = q.get("budget_ms") or {"easy": 65_000, "medium": 95_000,
                                        "hard": 126_000}.get(q["difficulty"], 95_000)
        if attempt["ms"] and attempt["ms"] > 2 * budget:
            slow_topics[q["topic"]] += 1
    trap_ids = []
    for norm, _ in mistakes.most_common(3):
        trap = db.one("SELECT id FROM traps WHERE learner=? AND norm=? ORDER BY last DESC LIMIT 1",
                      learner, norm)
        if trap:
            trap_ids.append(trap["id"])
    sat = (_json(row["spec"], {}) or {}).get("sat_date") or row["contest"].removeprefix("final-")
    profile = db.one("SELECT exam_date FROM learners WHERE id=?", learner)
    result = _json(row["result"], {}) or {}
    return {"sid": row["id"], "traps": trap_ids, "trap_norms": [norm for norm, _ in mistakes.most_common(3)],
            "skip_first": [topic for topic, _ in slow_topics.most_common(3)],
            "band": result.get("estimate") or result.get("band"), "route": result.get("route"),
            "mode": "last_week" if profile and profile["exam_date"] == sat else "focus",
            "sat_date": sat, "exam_date": profile["exam_date"] if profile else None,
            "doors": DOORS_LINE}


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
            "why": row["unranked_why"], "clock": clock(row),
            "pacer": pacer(row)}


def race_choice(cid: str, learner: str, choice: str | None) -> dict | None:
    """Resolve a public race choice before a sitting starts; never expose a pick."""
    if not choice:
        return None
    contest_row = contest(cid)
    if choice == "pace":
        return {"kind": "pace", "label": "SAT pace", "level": None, "points": None,
                "right": None, "secs": contest_row["seconds"]}
    if choice.startswith("par:"):
        try:
            level = int(choice[4:])
        except ValueError as exc:
            raise HTTPException(422, "invalid par level") from exc
        if level < 1 or level > 10:
            raise HTTPException(422, "invalid par level")
        slots = (_json(contest_row["spec"], {}) or {}).get("slots", [])
        expected = par(None, slots, rating=700 + 150 * (level - 1))
        return {"kind": "par", "label": f"Level {level} par", "level": level,
                "points": expected["points"], "right": expected["right"],
                "secs": contest_row["seconds"]}
    if choice == "median":
        points = [r["points"] for r in db.rows("SELECT points FROM sessions WHERE contest=?"
                                              " AND ranked=1 AND finished IS NOT NULL", contest_row["id"])]
        return {"kind": "median", "label": "Field median", "level": None,
                "points": statistics.median(points) if points else None,
                "right": None, "secs": contest_row["seconds"]}
    if choice == "best":
        other = db.one("SELECT s.* FROM sessions s JOIN contests c ON c.id=s.contest"
                       " WHERE s.learner=? AND c.kind=? AND s.finished IS NOT NULL AND s.ranked=1"
                       " ORDER BY s.points DESC,s.finished DESC LIMIT 1", learner, contest_row["kind"])
        if not other:
            raise HTTPException(404, "no previous run to race")
        return {"kind": "best", "label": "Your best", "sid": other["id"], "target": learner,
                "level": _identity(learner, learner)["level"], "points": other["points"],
                "right": (_json(other["result"], {}) or {}).get("right"), "secs": other["secs"]}
    target = person_of(choice)
    if not target:
        raise HTTPException(404, "student not found")
    profile = db.one("SELECT board FROM learners WHERE id=?", target)
    if profile and profile["board"] == "hidden":
        raise HTTPException(403, "this run is private now")
    other = db.one("SELECT * FROM sessions WHERE contest=? AND learner=? AND finished IS NOT NULL"
                   " AND ranked=1 ORDER BY points DESC LIMIT 1", contest_row["id"], target)
    if not other:
        raise HTTPException(404, "that student has not finished this contest")
    return {"kind": "run", "label": _identity(target, learner)["name"], "sid": other["id"],
            "target": target, "level": _identity(target, learner)["level"],
            "points": other["points"], "right": (_json(other["result"], {}) or {}).get("right"),
            "secs": other["secs"]}


def pacer(row) -> dict | None:
    cfg = _json(row["cfg"], {}) or {}
    race = cfg.get("race")
    if not race:
        return None
    target = race.get("target")
    if target and target != row["learner"]:
        profile = db.one("SELECT board FROM learners WHERE id=?", target)
        if profile and profile["board"] == "hidden":
            return None
    own = db.one("SELECT COUNT(DISTINCT qid) AS n FROM attempts WHERE session=?", row["id"])["n"]
    used = clock(row)["used"]
    marks = []
    elapsed = 0
    if race.get("sid"):
        other = db.one("SELECT questions FROM sessions WHERE id=?", race["sid"])
        questions = _json(other["questions"], []) if other else []
        if isinstance(questions, dict):
            questions = questions.get("module1", []) + questions.get("module2", [])
        by_id = {q["id"]: q for q in (questions or [])}
        for attempt in db.rows("SELECT qid,correct,void,COALESCE(sms,ms,95000) AS ms"
                               " FROM attempts WHERE session=? ORDER BY id", race["sid"]):
            q = by_id.get(attempt["qid"])
            if not q:
                continue
            elapsed += (attempt["ms"] or 0) / 1000
            points = ({"easy": 10, "medium": 20, "hard": 30}.get(q["difficulty"], 20)
                      if attempt["correct"] and not attempt["void"] else 0)
            marks.append({"right": bool(attempt["correct"] and not attempt["void"]),
                          "points": points, "at": round(elapsed)})
    elif race["kind"] in ("pace", "par"):
        slots = (_json(contest(row["contest"])["spec"], {}) or {}).get("slots", [])
        for index, slot in enumerate(slots):
            elapsed += {"easy": 65, "medium": 95, "hard": 126}.get(slot[1], 95)
            right = race["kind"] == "pace" or index < (race.get("right") or 0)
            marks.append({"right": right, "points": {"easy": 10, "medium": 20, "hard": 30}.get(slot[1], 20)
                          if right else 0, "at": round(elapsed)})
    visible = marks[:own]
    progressed = [m for m in visible if m["at"] <= used]
    return {"label": race["label"], "level": race.get("level"), "at": len(progressed),
            "points_at": sum(m["points"] for m in progressed),
            "marks": [{"right": m["right"], "points": m["points"], "at": m["at"]} for m in visible]}


def _pid(learner: str) -> str:
    secret = db.one("SELECT v FROM kv WHERE k='compete:pid_secret'")
    if not secret:
        init()
        secret = db.one("SELECT v FROM kv WHERE k='compete:pid_secret'")
    return hmac.new(bytes.fromhex(secret["v"]), learner.encode(), hashlib.sha256).hexdigest()[:10]


def _identity(learner: str, viewer: str | None = None, *, private: bool = False) -> dict:
    profile = db.one("SELECT name,handle,board,rating,rated,country FROM learners WHERE id=?", learner)
    board_mode = profile["board"] if profile else "name"
    anon = board_mode in ("anon", "hidden")
    name = profile["handle"] if profile else None
    name = challenge.handle(learner, name)
    masked = learner != viewer and (board_mode == "hidden" or private and anon)
    if learner != viewer and board_mode == "anon" and not private:
        name = challenge.handle(learner, None)
    title = champion_title(learner)
    return {"pid": _pid(learner), "name": "Anonymous" if masked else name,
            "anon": anon, "level": ratings.level_of(profile["rating"] or 1000) if profile else 1,
            "country": profile["country"] if profile else None,
            "ring": bool(title) and not masked,
            "title": title if not masked else None}


def private_access(row, viewer: str | None) -> None:
    if row["kind"] == "private" and (not viewer or viewer not in private_members(row["id"])):
        raise HTTPException(403, "join this contest first")


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
    private_access(contest_row, me)
    if contest_row["kind"] == "rush":
        return rush_board(contest_row["id"], me)
    if contest_row["kind"] == "words":
        return word_board(contest_row["id"], me)
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
        ident = _identity(learner, me, private=contest_row["kind"] == "private")
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
    near_players = None
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
        near_players = len(entries)
        center = next(i for i, e in enumerate(entries) if e["you"])
        start = max(0, min(center - 5, len(entries) - 11))
        entries = entries[start:start + 11]
        offset = 0
        limit = 11
    elif scope != "all":
        raise HTTPException(422, "unknown board scope")
    yesterday = (_now().date() - dt.timedelta(days=1)).isoformat()
    prior = {r["learner"]: r["rank"] for r in db.rows(
        "SELECT learner,rank FROM rank_snapshots WHERE day=? AND board=?", yesterday,
        "contest:" + contest_row["id"])}
    for index, entry in enumerate(entries):
        gap = max(0, entries[index - 1]["points"] - entry["points"]) if index else 0
        entry["gap"] = gap
        entry["move"] = prior[entry["learner"]] - entry["rank"] if entry["learner"] in prior else None
        entry["cheapest"] = gap + 1 if gap else None
        db.run("INSERT OR IGNORE INTO rank_snapshots(day,board,learner,rank,value) VALUES (?,?,?,?,?)",
               _now().date().isoformat(), "contest:" + contest_row["id"], entry["learner"],
               entry["rank"], entry["points"])
    players = near_players if near_players is not None else len(entries)
    page = entries[offset:offset + min(max(1, limit), 100)]
    next_offset = (offset + len(page) if near_players is None and offset + len(page) < players
                   else None)
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


def period_window(period: str, at: str | None = None) -> tuple[str | None, str | None, str | None, bool]:
    """Decode public period IDs and refuse future or still-open historical boards."""
    if at is None:
        start, end = _period_bounds(period)
        return start, end, None, False
    if period in ("all", "7d", "rating", "skill", "climb"):
        raise HTTPException(400, "this board has no past-period stepper")
    try:
        if period == "week":
            year, week = at.split("-W")
            date = dt.date.fromisocalendar(int(year), int(week), 1)
        elif period == "month":
            date = dt.date.fromisoformat(at + "-01")
        elif period == "year":
            date = dt.date(int(at), 1, 1)
        elif period == "season" and at.startswith("road-"):
            date = dt.date.fromisoformat(at[5:])
            if date.isoformat() not in SAT_DATES:
                raise ValueError("unknown SAT season")
        else:
            raise ValueError("invalid period")
    except (TypeError, ValueError) as exc:
        raise HTTPException(400, "invalid past period") from exc
    start, end = _period_bounds(period, date)
    if start is None or end is None:
        raise HTTPException(400, "period has no dates")
    current_start, _ = _period_bounds(period)
    if start > current_start:
        raise HTTPException(400, "period has not started")
    close = dt.datetime.fromisoformat(end + "T12:00:00+00:00")
    closed = _now() >= close
    if start != current_start and not closed:
        raise HTTPException(400, "period has not closed")
    return start, end, at, closed


def _season_end(period: str) -> dt.date:
    return dt.date.fromisoformat(period.removeprefix("road-"))


def champion_title(learner: str) -> dict | None:
    """A season/final podium ring lasts until the next SAT season closes."""
    now = _now().date()
    rows = db.rows("SELECT kind,period,board,place FROM champions WHERE learner=?"
                   " AND kind IN ('season','final') ORDER BY period DESC,place LIMIT 12", learner)
    for row in rows:
        end = _season_end(row["period"]) if row["kind"] == "season" else dt.date.fromisoformat(row["period"])
        next_sat = next((dt.date.fromisoformat(x) for x in SAT_DATES if dt.date.fromisoformat(x) > end), None)
        if end < now <= (next_sat or end):
            return dict(row)
    return None


def _champion_values(start: str, end: str, metric: str, subject: str = "math") -> list[dict]:
    rows = db.rows("SELECT s.*,c.kind AS contest_kind,c.subject AS contest_subject FROM sessions s"
                   " JOIN contests c ON c.id=s.contest WHERE s.finished>=? AND s.finished<?"
                   " AND s.ranked=1 AND c.kind!='private' AND c.subject=?", start, end, subject)
    totals: dict[str, float] = defaultdict(float)
    first: dict[str, tuple[str, float]] = {}
    last: dict[str, tuple[str, float]] = {}
    sprint_best: dict[tuple[str, str], float] = {}
    for row in rows:
        person = row["learner"]
        result = _json(row["result"], {}) or {}
        if metric == "change":
            before, after = result.get("rating_before"), result.get("rating_after")
            if before is None or after is None:
                continue
            if person not in first or row["finished"] < first[person][0]:
                first[person] = (row["finished"], before)
            if person not in last or row["finished"] > last[person][0]:
                last[person] = (row["finished"], after)
            continue
        if metric == "net":
            if row["contest_kind"] in ("sprint", "rush", "words"):
                continue
            value = result.get("net", 0) or 0
        else:
            if row["contest_kind"] in ("rush", "words"):
                continue
            value = row["points"] or 0
        if row["contest_kind"] == "sprint":
            key = (person, row["contest"])
            previous = sprint_best.get(key, 0)
            sprint_best[key] = max(previous, value)
            totals[person] += max(0, value - previous)
        else:
            totals[person] += value
    if metric == "change":
        totals = {person: after - first[person][1] for person, (_, after) in last.items() if person in first}
    entries = [{"learner": person, "pid": _pid(person), "value": round(value, 1),
                "level": _identity(person)["level"]} for person, value in totals.items()]
    _rank(entries, "value")
    return entries


def _save_podium(kind: str, period: str, board_name: str, entries: list[dict], band: str = "") -> None:
    for entry in entries:
        if entry["rank"] > (1 if band else 3):
            continue
        db.run("INSERT OR IGNORE INTO champions(kind,period,board,place,learner,value,band)"
               " VALUES (?,?,?,?,?,?,?)", kind, period, board_name, entry["rank"],
               entry["learner"], entry["value"], band)


def close_champions() -> None:
    """Lazily freeze every finished, populated week, season and Final."""
    now = _now()
    rows = db.rows("SELECT DISTINCT finished FROM sessions WHERE contest IS NOT NULL"
                   " AND ranked=1 AND finished IS NOT NULL")
    weeks: set[dt.date] = set()
    seasons: set[str] = set()
    for row in rows:
        day = dt.date.fromisoformat(row["finished"][:10])
        weeks.add(day - dt.timedelta(days=day.weekday()))
        season = next((s for s in SAT_DATES if s >= day.isoformat()), None)
        if season:
            seasons.add(season)
    for monday in sorted(weeks):
        end = monday + dt.timedelta(days=7)
        if now < dt.datetime.combine(end, dt.time(12), dt.timezone.utc):
            continue
        period = f"{monday.isocalendar().year}-W{monday.isocalendar().week:02d}"
        if db.one("SELECT 1 FROM champions WHERE kind='week' AND period=?", period):
            continue
        for metric in ("points", "net", "change"):
            entries = _champion_values(monday.isoformat(), end.isoformat(), metric)
            _save_podium("week", period, metric, entries)
            if metric == "points":
                for label, low, high in (("1-3", 1, 3), ("4-6", 4, 6), ("7-10", 7, 10)):
                    band = [e.copy() for e in entries if low <= e["level"] <= high]
                    _rank(band, "value")
                    _save_podium("week", period, "band", band, label)
    for sat in sorted(seasons):
        end = dt.date.fromisoformat(sat) + dt.timedelta(days=1)
        if now < dt.datetime.combine(end, dt.time(12), dt.timezone.utc):
            continue
        period = "road-" + sat
        if db.one("SELECT 1 FROM champions WHERE kind='season' AND period=?", period):
            continue
        start, _ = _period_bounds("season", dt.date.fromisoformat(sat))
        for metric in ("points", "net", "change"):
            entries = _champion_values(start, end.isoformat(), metric)
            _save_podium("season", period, metric, entries)
            if metric == "points":
                for label, low, high in (("1-3", 1, 3), ("4-6", 4, 6), ("7-10", 7, 10)):
                    band = [e.copy() for e in entries if low <= e["level"] <= high]
                    _rank(band, "value")
                    _save_podium("season", period, "band", band, label)
        standings = {metric: _champion_values(start, end.isoformat(), metric)
                     for metric in ("points", "net", "change")}
        db.run("INSERT OR IGNORE INTO seasons(id,opens,closes,standings,closed) VALUES (?,?,?,?,?)",
               period, start, end.isoformat(), json.dumps(standings), _iso(now))
        final = "final-" + sat
        final_rows = db.rows("SELECT learner,points FROM sessions WHERE contest=? AND ranked=1"
                             " AND finished IS NOT NULL", final)
        podium = [{"learner": r["learner"], "pid": _pid(r["learner"]), "value": r["points"] or 0}
                  for r in final_rows]
        _rank(podium, "value")
        _save_podium("final", sat, "points", podium)


def champions(kind: str | None = None, mine: str | None = None,
              before: str | None = None, limit: int = 8,
              viewer: str | None = None) -> list[dict]:
    close_champions()
    rows = db.rows("SELECT * FROM champions ORDER BY period DESC,kind,board,place")
    periods: dict[tuple[str, str], dict] = {}
    for row in rows:
        if (kind and row["kind"] != kind) or (before and row["period"] >= before):
            continue
        key = (row["kind"], row["period"])
        group = periods.setdefault(key, {"kind": row["kind"], "period": row["period"], "boards": {}})
        ident = _identity(row["learner"], viewer)
        group["boards"].setdefault(row["board"], []).append(
            {"place": row["place"], "value": row["value"], "band": row["band"], **ident})
    if mine:
        own_pid = _pid(mine)
        periods = {key: group for key, group in periods.items()
                   if any(entry["pid"] == own_pid for entries in group["boards"].values() for entry in entries)}
    return list(periods.values())[:max(1, min(limit, 50))]


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
    if at and metric in ("rating", "skill", "climb"):
        raise HTTPException(400, "this metric has no past-period board")
    start, end, period_id, closed = period_window(period, at)
    close_champions()
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
            if not row["contest"] or row["contest_kind"] in ("private", "rush"):
                continue
            amount = row["points"] or 0
            if metric == "net":
                if row["contest_kind"] in ("sprint", "rush", "words"):
                    continue
                amount = (_json(row["result"], {}) or {}).get("net", 0)
            if row["contest_kind"] in ("sprint", "words"):
                key = (row["learner"], row["contest"])
                old = sprint_best.get(key)
                best = amount if old is None else max(old, amount)
                sprint_best[key] = best
                values[row["learner"]] += best - (old or 0)
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
        if sort == "change":
            changes: dict[str, tuple[str, float, str, float]] = {}
            for r in rows:
                if not r["contest"] or r["contest_subject"] != subject:
                    continue
                if (start and r["finished"][:10] < start) or (end and r["finished"][:10] >= end):
                    continue
                result = _json(r["result"], {}) or {}
                before, after = result.get("rating_before"), result.get("rating_after")
                if before is None or after is None:
                    continue
                first_time, first_rating, last_time, last_rating = changes.get(
                    r["learner"], (r["finished"], before, r["finished"], after))
                if r["finished"] < first_time:
                    first_time, first_rating = r["finished"], before
                if r["finished"] > last_time:
                    last_time, last_rating = r["finished"], after
                changes[r["learner"]] = first_time, first_rating, last_time, last_rating
            values = {person: round(after - before, 1) for person, (_, before, _, after) in changes.items()}
    climb_window = None
    if metric == "climb":
        values, climb_window = _climb_cohort(learner)
    entries = []
    own_country = _identity(learner).get("country") if learner else None
    own_level = _identity(learner)["level"] if learner else None
    own_exam = (db.one("SELECT exam_date FROM learners WHERE id=?", learner) or {"exam_date": None})["exam_date"] if learner else None
    followed = {r["target"] for r in db.rows("SELECT target FROM follows WHERE learner=?", learner)} if learner else set()
    for person, value in values.items():
        ident = _identity(person, learner)
        if scope == "country" and (not own_country or ident["country"] != own_country):
            continue
        if scope == "following" and person not in followed and person != learner:
            continue
        if scope == "level" and (own_level is None or abs(ident["level"] - own_level) > 1):
            continue
        if scope == "exam" and (not own_exam or not db.one(
                "SELECT 1 FROM learners WHERE id=? AND exam_date=?", person, own_exam)):
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
    snapshot_key = f"{metric}:{period}:{scope}:{subject}:{domain or ''}:{sort}"
    yesterday = (_now().date() - dt.timedelta(days=1)).isoformat()
    previous = {r["learner"]: r["rank"] for r in db.rows(
        "SELECT learner,rank FROM rank_snapshots WHERE day=? AND board=?", yesterday, snapshot_key)}
    for index, entry in enumerate(entries):
        gap = max(0, entries[index - 1]["value"] - entry["value"]) if index else 0
        entry["gap"] = round(gap, 1)
        entry["move"] = previous[entry["learner"]] - entry["rank"] if entry["learner"] in previous else None
        entry["cheapest"] = math.floor(gap) + 1 if gap and metric in ("points", "net") else None
        if not at:
            db.run("INSERT OR IGNORE INTO rank_snapshots(day,board,learner,rank,value) VALUES (?,?,?,?,?)",
                   _now().date().isoformat(), snapshot_key, entry["learner"], entry["rank"], entry["value"])
    mine = next((e for e in entries if e["you"]), None)
    if scope == "near" and mine:
        i = next(i for i, e in enumerate(entries) if e["you"])
        entries = entries[max(0, min(i - 5, len(entries) - 11)):][:11]
        offset = 0
    elif scope not in ("all", "country", "following", "level", "near", "extended", "exam"):
        raise HTTPException(422, "unknown leaderboard scope")
    players = len(entries)
    page = entries[offset:offset + min(max(1, limit), 100)]
    for e in page:
        e.pop("learner", None)
        e.pop("finished", None)
    if mine:
        mine = {k: v for k, v in mine.items() if k not in ("learner", "finished")}
    return {"metric": metric, "period": period, "at": period_id, "closed": closed,
            "scope": scope, "subject": subject,
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
    states: dict[str, str] = {}
    for row in db.rows("SELECT COALESCE(day,SUBSTR(contest,7,10)) AS day,finished,ranked"
                       " FROM sessions WHERE learner=? AND contest LIKE 'daily-%'"
                       " AND finished IS NOT NULL", learner):
        day = row["day"]
        if not day:
            continue
        date = dt.date.fromisoformat(day)
        finished = dt.datetime.fromisoformat(row["finished"])
        local = local_day(tz, finished)
        # A ghost can make up the day for 48 h after that day's end.
        made_up = date < local and finished < dt.datetime.combine(
            date + dt.timedelta(days=3), dt.time(), dt.timezone.utc) + dt.timedelta(minutes=tz)
        status = "sat" if local == date else "made_up" if made_up else "ghost"
        if states.get(day) != "sat" and (states.get(day) != "made_up" or status == "sat"):
            states[day] = status
    days = {day for day, status in states.items() if status in ("sat", "made_up")}
    count = 0
    at = today
    if at.isoformat() not in days:
        at -= dt.timedelta(days=1)
    while at.isoformat() in days:
        count += 1
        at -= dt.timedelta(days=1)
    best = 0
    streak = 0
    prior = None
    for day in sorted(days):
        date = dt.date.fromisoformat(day)
        streak = streak + 1 if prior and date == prior + dt.timedelta(days=1) else 1
        best = max(best, streak)
        prior = date
    strip = [{"day": (today - dt.timedelta(days=back)).isoformat(),
              "state": states.get((today - dt.timedelta(days=back)).isoformat(), "missed")}
             for back in range(29, -1, -1)]
    return {"current": count, "best": best, "days": sorted(days, reverse=True)[:30], "strip": strip}


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


def closing_soon(learner: str, tz: int = 0) -> list[dict]:
    end = _iso(_now() + dt.timedelta(hours=24))
    return [item for item in due_today(learner, tz) if item["closes"] <= end]


def shell_part(learner: str, tz: int = 0) -> dict:
    today_id = "daily-" + local_day(tz).isoformat()
    done = db.one("SELECT 1 FROM sessions WHERE learner=? AND contest=? AND finished IS NOT NULL",
                  learner, today_id)
    return {"challenge": {"streak": challenge_streak(learner, tz)["current"]},
            "daily": {"id": today_id, "done": bool(done)},
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
    profile = db.one("SELECT board,handle FROM learners WHERE id=?", learner)
    public_name = (profile["handle"] if profile and profile["board"] == "name" else None)
    title = str(body.get("title") or f"{challenge.handle(learner, public_name)}'s challenge").strip()
    if not 3 <= len(title) <= 40:
        raise HTTPException(422, "title must be 3–40 characters")
    count = body.get("count", 10)
    if count not in (5, 10, 15, 22):
        raise HTTPException(422, "count must be 5, 10, 15 or 22")
    minutes = body.get("minutes")
    if minutes is not None and (not isinstance(minutes, int) or not 5 <= minutes <= 70):
        raise HTTPException(422, "minutes must be 5–70")
    hours = body.get("open_for", 24)
    if hours not in (1, 24, 72, 168):
        raise HTTPException(422, "open_for must be 1, 24, 72 or 168 hours")
    duration = body.get("duration", {1: "hour", 24: "day", 72: "3days", 168: "week"}[hours])
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
    private_access(root, viewer)
    rounds = db.rows("SELECT id,round FROM contests WHERE id=? OR series=? ORDER BY round", series, series)
    entries = []
    for member in private_members(series):
        scores = []
        for rnd in rounds:
            run = db.one("SELECT points,result FROM sessions WHERE contest=? AND learner=?"
                         " AND finished IS NOT NULL ORDER BY points DESC LIMIT 1", rnd["id"], member)
            scores.append({"round": rnd["round"], "points": run["points"] if run else None,
                           "net": ((_json(run["result"], {}) or {}).get("net") if run else None)})
        entries.append({**_identity(member, viewer, private=True), "you": member == viewer,
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
    if profile and profile["board"] == "hidden":
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
        if row["board"] == "hidden" or abs((row["rating"] or 1000) - rating) > 200:
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
