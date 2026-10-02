"""The study plan's server-owned calendar, allocation, status and summaries.

All dates are learner-local (X-Tz is minutes west of UTC).  Past days are
frozen before an edit; future days are dealt from the same inputs each time.
Other sections are optional and are reached through deps.part.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import re
import secrets
import statistics
from collections import Counter, defaultdict
from functools import lru_cache

from fastapi import HTTPException

from . import db, deps, estimate, progress, satdates, scoring

DOMAINS = tuple(progress.DOMAINS)
TOPICS = tuple(estimate.DOMAIN_OF)
PHASES = ("Build", "Sharpen", "Final")
STATES = ("focus", "normal", "strong")
TESTS = ("none", "weekly", "twice", "daily")
TASK_KINDS = ("test", "recheck", "fix", "learn", "check", "habit", "pace",
              "map", "focus", "sweep", "words", "custom", "qotd", "challenge")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
TASK_TYPES = ("other", "bluebook", "rw", "tutor", "book", "khan")
RW_DOMAINS = ("Information and Ideas", "Craft and Structure",
              "Expression of Ideas", "Standard English Conventions")
RW_SHARES = (.26, .28, .20, .26)


def init() -> None:
    """S7-owned additions to F4's base tables; app.py calls this at startup."""
    c = db.conn()
    for table, cols in {
        "plans": {"cal_token": "TEXT", "view_token": "TEXT", "start_points": "TEXT"},
        "plan_days": {"gate": "INTEGER DEFAULT 0"},
        "plan_overrides": {"trim": "INTEGER DEFAULT 0"},
        "plan_marks": {"minutes": "INTEGER", "note": "TEXT"},
        "plan_tasks": {"type": "TEXT DEFAULT 'other'", "subject": "TEXT DEFAULT 'math'"},
    }.items():
        have = {r["name"] for r in c.execute(f"PRAGMA table_info({table})")}
        for name, decl in cols.items():
            if name not in have:
                c.execute(f"ALTER TABLE {table} ADD COLUMN {name} {decl}")
    c.execute("CREATE INDEX IF NOT EXISTS plan_events_plan_at ON plan_events(plan,at)")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS plans_cal_token ON plans(cal_token)")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS plans_view_token ON plans(view_token)")
    c.commit()


def today(tz: int = 0) -> dt.date:
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date()


def _date(value: str, field: str) -> dt.date:
    if not isinstance(value, str) or not DATE.fullmatch(value):
        raise HTTPException(422, f"{field}: use YYYY-MM-DD")
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(422, f"{field}: not a real date") from exc


def _json(value, default=None):
    try:
        return json.loads(value) if value else default
    except (TypeError, ValueError):
        return default


def cfg_of(row) -> dict:
    return _json(row["cfg"], {}) or {}


def active_row(learner: str):
    link = db.one("SELECT plan FROM learners WHERE id=?", learner)
    if link and link["plan"]:
        row = db.one("SELECT * FROM plans WHERE id=? AND learner=?", link["plan"], learner)
        if row and not row["archived"]:
            return row
    return db.one("SELECT * FROM plans WHERE learner=? AND archived IS NULL ORDER BY created DESC LIMIT 1", learner)


def owned_row(learner: str, pid: str, active: bool = False):
    row = db.one("SELECT * FROM plans WHERE id=? AND learner=?", pid, learner)
    if not row:
        raise HTTPException(404, "plan not found")
    if active and (row["archived"] or not active_row(learner) or active_row(learner)["id"] != pid):
        raise HTTPException(409, "that plan is archived; make it active first")
    return row


def _score(value, field: str, optional: bool = False):
    if value is None and optional:
        return None
    if type(value) is not int or value < 200 or value > 800 or value % 10:
        raise HTTPException(422, f"{field}: use a score from 200 to 800 in tens")
    return value


def validate(body: dict, learner: str, tz: int = 0, base: dict | None = None) -> dict:
    """One strict PlanIn validator for create, edit and preview."""
    if not isinstance(body, dict):
        raise HTTPException(422, "plan body must be an object")
    profile = db.one("SELECT * FROM learners WHERE id=?", learner)
    default = {"current": 520, "target": 650, "exam_date": None, "minutes": 45,
               "days": "1111100", "day_minutes": None, "off": [], "tests": "weekly",
               "test_size": "module", "test_day": None, "clock": "auto", "time": "18:00",
               "focus": {}, "skills": {}, "extras": {"recheck": True, "qotd": False, "challenge": False},
               "booked": False, "rw_current": None, "rw_target": None, "rw_minutes": 0,
               "measure": False, "ramp": None, "place": None, "checkpoints": "every_2nd",
               "rehearsal_at": "08:30"}
    if profile and not base:
        default.update({k: profile[k] for k in ("current", "target", "exam_date", "minutes", "days", "tests")
                        if profile[k] is not None})
        default["focus"] = _json(profile["focus"], {}) or {}
        default["rw_current"] = profile["rw_now"]
        default["rw_target"] = profile["rw_target"]
    cfg = {**default, **(base or {}), **body}
    sections = cfg.get("sections") or {}
    if not isinstance(sections, dict):
        raise HTTPException(422, "sections must be an object")
    math_section = sections.get("math") or {}
    rw_section = sections.get("rw") or {}
    if not isinstance(math_section, dict) or not isinstance(rw_section, dict):
        raise HTTPException(422, "sections.math and sections.rw must be objects")
    for field in ("current", "target", "focus", "skills"):
        if field not in body and field in math_section:
            cfg[field] = math_section[field]
    for field, alias in (("current", "rw_current"), ("target", "rw_target"),
                         ("focus", "rw_focus"), ("minutes", "rw_minutes")):
        if alias not in body and field in rw_section:
            cfg[alias] = rw_section[field]
    cfg["current"] = _score(cfg["current"], "current", optional=bool(cfg.get("measure")))
    cfg["target"] = _score(cfg["target"], "target")
    if cfg["current"] is not None and cfg["target"] < cfg["current"]:
        raise HTTPException(422, "target must be at least current")
    exam = _date(cfg.get("exam_date"), "exam_date")
    if not today(tz) < exam <= today(tz) + dt.timedelta(days=730):
        raise HTTPException(422, "exam_date must be after today and within 730 days")
    if type(cfg["minutes"]) is not int or not 5 <= cfg["minutes"] <= 240:
        raise HTTPException(422, "minutes must be 5 to 240")
    if not isinstance(cfg["days"], str) or not re.fullmatch(r"[01]{7}", cfg["days"]) or "1" not in cfg["days"]:
        raise HTTPException(422, "days must be seven 0s and 1s with a study day")
    dm = cfg["day_minutes"]
    if dm is not None and (not isinstance(dm, list) or len(dm) != 7 or
                            any(v is not None and (type(v) is not int or v not in (0, *range(5, 241))) for v in dm)):
        raise HTTPException(422, "day_minutes must have seven values of null, 0 or 5–240")
    if cfg["tests"] not in TESTS or cfg["test_size"] not in ("module", "section") or cfg["clock"] not in ("off", "auto", "always"):
        raise HTTPException(422, "tests, test_size or clock is invalid")
    if cfg["test_day"] is not None and (type(cfg["test_day"]) is not int or not 0 <= cfg["test_day"] <= 6):
        raise HTTPException(422, "test_day must be Monday=0 through Sunday=6")
    if cfg["time"] is not None and (not isinstance(cfg["time"], str) or not TIME.fullmatch(cfg["time"])):
        raise HTTPException(422, "time must be HH:MM")
    if not isinstance(cfg["rehearsal_at"], str) or not TIME.fullmatch(cfg["rehearsal_at"]):
        raise HTTPException(422, "rehearsal_at must be HH:MM")
    if cfg["place"] is not None and (not isinstance(cfg["place"], str) or len(cfg["place"]) > 30):
        raise HTTPException(422, "place is at most 30 characters")
    for field, allowed, cap in (("focus", DOMAINS, 2), ("skills", TOPICS, 6)):
        data = cfg[field]
        if not isinstance(data, dict):
            raise HTTPException(422, f"{field} must map names to states")
        for key, raw in data.items():
            state = raw.get("state") if isinstance(raw, dict) else raw
            if key not in allowed or state not in STATES:
                raise HTTPException(422, f"{field}: unknown name or state")
        if sum((v.get("state") if isinstance(v, dict) else v) == "focus" for v in data.values()) > cap:
            raise HTTPException(422, f"{field}: at most {cap} on Focus")
    off = cfg["off"]
    if not isinstance(off, list) or len(off) > 20:
        raise HTTPException(422, "off: at most 20 date ranges")
    for pair in off:
        if not isinstance(pair, list) or len(pair) != 2 or not today(tz) <= _date(pair[0], "off") <= _date(pair[1], "off") <= exam:
            raise HTTPException(422, "off: ranges must be ordered inside the plan")
    for key in ("rw_current", "rw_target"):
        cfg[key] = _score(cfg.get(key), key, optional=True)
    if cfg["rw_target"] is not None and cfg["rw_current"] is not None and cfg["rw_target"] < cfg["rw_current"]:
        raise HTTPException(422, "rw_target must be at least rw_current")
    rw_focus = cfg.get("rw_focus") or {}
    if not isinstance(rw_focus, dict) or any(k not in RW_DOMAINS or v not in STATES for k, v in rw_focus.items()):
        raise HTTPException(422, "rw.focus: unknown domain or state")
    if sum(v == "focus" for v in rw_focus.values()) > 2:
        raise HTTPException(422, "rw: 2 focus areas at most")
    if type(cfg["rw_minutes"]) is not int or cfg["rw_minutes"] not in (0, 15, 30, 45, 60):
        raise HTTPException(422, "rw_minutes must be 0, 15, 30, 45 or 60")
    if cfg["checkpoints"] not in ("every", "every_2nd", "off"):
        raise HTTPException(422, "checkpoints must be every, every_2nd or off")
    if type(cfg["booked"]) is not bool:
        raise HTTPException(422, "booked must be boolean")
    if cfg["ramp"] is not None:
        start_m = cfg["ramp"].get("from") if isinstance(cfg["ramp"], dict) else cfg["ramp"]
        if type(start_m) is not int or not 5 <= start_m <= cfg["minutes"]:
            raise HTTPException(422, "ramp.from must be between 5 and minutes")
        cfg["ramp"] = {"from": start_m}
    cfg["sections"] = {"math": {k: cfg[k] for k in ("current", "target", "focus", "skills")}}
    if cfg["rw_current"] is not None or cfg["rw_target"] is not None or rw_focus or cfg["rw_minutes"]:
        cfg["sections"]["rw"] = {"current": cfg["rw_current"], "target": cfg["rw_target"],
                                  "focus": rw_focus, "minutes": cfg["rw_minutes"]}
    return cfg


def _override(pid: str, day: dt.date) -> dict:
    r = db.one("SELECT * FROM plan_overrides WHERE plan=? AND day=?", pid, day.isoformat())
    return dict(r) if r else {}


def _base_minutes(cfg: dict, day: dt.date, start: dt.date | None = None) -> int:
    m = cfg.get("day_minutes")
    value = m[day.weekday()] if isinstance(m, list) and m[day.weekday()] is not None else cfg["minutes"]
    if cfg.get("ramp") and start:
        week = max(0, (day - start).days // 7)
        value = min(value, cfg["ramp"]["from"] + 5 * week)
    if cfg.get("exam_date"):
        exam = dt.date.fromisoformat(cfg["exam_date"])
        if day in _taper(cfg["exam_date"], cfg["days"]):
            value = round(value * .6)
    return value


@lru_cache(maxsize=256)
def _taper(exam_iso: str, days: str) -> frozenset[dt.date]:
    exam = dt.date.fromisoformat(exam_iso)
    out = []
    for n in range(2, 30):
        day = exam - dt.timedelta(days=n)
        if days[day.weekday()] == "1":
            out.append(day)
        if len(out) == 5:
            break
    return frozenset(out)


def _taper_dates(cfg: dict) -> frozenset[dt.date]:
    return _taper(cfg["exam_date"], cfg["days"])


@lru_cache(maxsize=256)
def _rehearsals(exam_iso: str, days: str, start: dt.date) -> frozenset[dt.date]:
    exam = dt.date.fromisoformat(exam_iso)
    final_start = next((start + dt.timedelta(days=i) for i in range((exam - start).days)
                        if phase(start, exam, start + dt.timedelta(days=i)) == "Final"), exam)
    result = []
    day = final_start
    while day <= exam - dt.timedelta(days=6):
        if day.weekday() == exam.weekday() and day not in _taper(exam_iso, days):
            result.append(day)
        day += dt.timedelta(days=1)
    return frozenset(result[-2:])


def _rehearsal_dates(cfg: dict, start: dt.date) -> frozenset[dt.date]:
    return _rehearsals(cfg["exam_date"], cfg["days"], start)


def phase(start: dt.date, exam: dt.date, day: dt.date) -> str:
    total = (exam - start).days
    left = (exam - day).days
    if total < 14 or left <= max(10, math.ceil(total * .15)):
        return "Final"
    if total < 35 or (day - start).days >= math.floor(total * .55):
        return "Sharpen"
    return "Build"


def _off(cfg: dict, day: dt.date, override: dict | None = None) -> bool:
    return bool((override or {}).get("off") or any(_date(a, "off") <= day <= _date(b, "off")
                                                    for a, b in cfg.get("off", [])))


def kind_of(cfg: dict, start: dt.date, day: dt.date, override: dict | None = None,
            override_of=None) -> tuple[str, str | None, int]:
    """The date's kind, test size and minutes, with the exam week test on Thursday."""
    exam = dt.date.fromisoformat(cfg["exam_date"])
    override = override or {}
    if day < start:
        return "before", None, 0
    if day > exam:
        return "after", None, 0
    if day == exam:
        return "exam", None, 0
    if day == exam - dt.timedelta(days=1):
        return "eve", None, 0
    if _off(cfg, day, override):
        return "off", None, 0
    if day in _rehearsal_dates(cfg, start):
        return "test", "section", max(70, override.get("minutes") or _base_minutes(cfg, day, start))
    if cfg["days"][day.weekday()] == "0":
        return "rest", None, 0
    minutes = override.get("minutes") if override.get("minutes") is not None else _base_minutes(cfg, day, start)
    if minutes < 5:
        return "off", None, 0
    if day in _taper_dates(cfg):
        return "practice", None, minutes
    test = override.get("test")
    if test == "none":
        test = None
        forced = True
    else:
        forced = bool(test)
    if not forced and cfg["tests"] != "none":
        monday = day - dt.timedelta(days=day.weekday())
        end = min(monday + dt.timedelta(days=6), exam - dt.timedelta(days=2))
        study = []
        for n in range((end - monday).days + 1):
            d = monday + dt.timedelta(days=n)
            ov = override_of(d) if override_of else (override if d == day else {})
            if d >= start and cfg["days"][d.weekday()] == "1" and not _off(cfg, d, ov):
                study.append(d)
        if study:
            preferred = next((d for d in study if d.weekday() == cfg["test_day"]), None) if cfg["test_day"] is not None else None
            weekly = preferred or study[-1]
            if (exam - day).days <= 7:
                thurs = next((d for d in study if d.weekday() == 3), None)
                weekly = thurs or study[-1]
            tests = {weekly}
            if cfg["tests"] == "twice" and len(study) > 1:
                tests.add(min((d for d in study if d != weekly), key=lambda d: (abs(d.weekday() - 2), d)))
            if cfg["tests"] == "daily":
                tests = set(study)
            if day in tests:
                test = cfg["test_size"]
    if test and minutes < 35:
        test = None
    if test == "section" and minutes < 70:
        test = "module"
    if test == "module" and phase(start, exam, day) == "Final" and minutes >= 70:
        test = "section"
    return ("test" if test else "practice"), test, minutes


def _state(cfg: dict, topic: str) -> str:
    raw = cfg.get("skills", {}).get(topic, cfg.get("focus", {}).get(estimate.DOMAIN_OF[topic], "normal"))
    return raw.get("state", "normal") if isinstance(raw, dict) else raw


def _values(learner: str, cfg: dict) -> tuple[dict[str, float], dict | None]:
    gains = estimate.gains(learner)
    board = progress.board(learner)
    values: dict[str, float] = {}
    if gains and any(x["gain"] >= 5 for x in gains["skills"]):
        high = {x["topic"]: x["gain"] / max(x["minutes"], 10) for x in gains["skills"] if x["gain"] >= 5}
        floor = statistics.median(high.values()) * .1
        values = {t: high.get(t, floor) for t in TOPICS}
    else:
        for t in TOPICS:
            b = board.get(t, {})
            m = b.get("mastery", .5) if b.get("answered") else .5
            values[t] = progress.BLUEPRINT[estimate.DOMAIN_OF[t]] / sum(
                x == estimate.DOMAIN_OF[t] for x in estimate.DOMAIN_OF.values()) * (1.5 - m)
    return {t: max(.0001, v) * {"focus": 2, "normal": 1, "strong": .4}[_state(cfg, t)]
            for t, v in values.items()}, gains


def shares(learner: str, cfg: dict) -> dict[str, float]:
    vals, _ = _values(learner, cfg)
    weight = {d: sum(vals[t] for t in TOPICS if estimate.DOMAIN_OF[t] == d) for d in DOMAINS}
    total = sum(weight.values())
    return {d: round(weight[d] / total, 5) for d in DOMAINS}


def _gate(learner: str, cfg: dict, pid: str | None = None) -> bool:
    if cfg["target"] <= 580:
        return False
    route = estimate.route(learner)
    m1 = route.get("m1") if route else None
    if m1 is None:
        return False
    if m1 < .60:
        return True
    if m1 >= .65:
        return False
    last = db.one("SELECT gate FROM plan_days WHERE plan=? ORDER BY day DESC LIMIT 1", pid) if pid else None
    return bool(last["gate"]) if last else False


def _slots(q: int) -> int:
    return 3 if q >= 15 else 2 if q >= 8 else 1


def allocate(learner: str, cfg: dict, start: dt.date, through: dt.date, pid: str | None = None) -> dict[str, list[str]]:
    """Deficit walk with recent-day avoidance and the Advanced Math fallback."""
    weights, _ = _values(learner, cfg)
    domain_w = {d: sum(weights[t] for t in TOPICS if estimate.DOMAIN_OF[t] == d) for d in DOMAINS}
    scale = sum(domain_w.values())
    shares_ = {d: domain_w[d] / scale for d in DOMAINS}
    used_d: Counter = Counter()
    used_t: Counter = Counter()
    recent: list[set[str]] = []
    out = {}
    all_slots = 0
    week_slots = 0
    for n in range(7):
        sample = start + dt.timedelta(days=n)
        kind, test, minutes = kind_of(cfg, start, sample)
        if kind in ("practice", "test"):
            q = math.floor(max(0, minutes - (70 if test == "section" else 35 if test else 0)) * 60 / 95)
            week_slots += _slots(q)
    window = max(14, math.ceil(len(TOPICS) / max(1, week_slots)) * 7)
    last_used = {t: start - dt.timedelta(days=window) for t in TOPICS}
    d = start
    exam = dt.date.fromisoformat(cfg["exam_date"])
    while d <= min(through, exam - dt.timedelta(days=2)):
        ov = _override(pid, d) if pid else {}
        kind, test, minutes = kind_of(cfg, start, d, ov, (lambda x: _override(pid, x)) if pid else None)
        if kind not in ("practice", "test"):
            d += dt.timedelta(days=1)
            continue
        q = max(0, math.floor(max(0, minutes - (35 if test == "module" else 70 if test else 0)) * 60 / 95))
        n = _slots(q)
        today_set: set[str] = set()
        picked = []
        swapped = _json(ov.get("topics"), []) if ov.get("topics") else []
        for topic in swapped[:n]:
            if topic in TOPICS:
                picked.append(topic)
                today_set.add(topic)
                used_d[estimate.DOMAIN_OF[topic]] += 1
                used_t[topic] += 1
                all_slots += 1
                last_used[topic] = d
        while len(picked) < n:
            overdue = [t for t in TOPICS if d >= start + dt.timedelta(days=max(0, window - 4)) and
                       t not in today_set and
                       (d - last_used[t]).days >= window and
                       sum(estimate.DOMAIN_OF[x] == estimate.DOMAIN_OF[t] for x in picked) < 2]
            if overdue:
                chosen = max(overdue, key=lambda t: ((d - last_used[t]).days, weights[t], t))
                picked.append(chosen)
                today_set.add(chosen)
                used_d[estimate.DOMAIN_OF[chosen]] += 1
                used_t[chosen] += 1
                all_slots += 1
                last_used[chosen] = d
                continue
            domains = sorted(DOMAINS, key=lambda domain: (-(shares_[domain] * (all_slots + 1) - used_d[domain]), domain))
            chosen = None
            for domain in domains:
                if sum(estimate.DOMAIN_OF[t] == domain for t in picked) >= 2:
                    continue
                candidates = [t for t in TOPICS if estimate.DOMAIN_OF[t] == domain and t not in today_set]
                for lookback in (2, 1, 0):
                    allowed = [t for t in candidates if not any(t in old for old in recent[-lookback:])] if lookback else candidates
                    if allowed:
                        chosen = max(allowed, key=lambda t: (weights[t] * (all_slots + 1) - used_t[t], weights[t], t))
                        break
                if chosen:
                    break
            if chosen is None:
                break
            picked.append(chosen)
            today_set.add(chosen)
            used_d[estimate.DOMAIN_OF[chosen]] += 1
            used_t[chosen] += 1
            all_slots += 1
            last_used[chosen] = d
        out[d.isoformat()] = picked
        recent.append(today_set)
        d += dt.timedelta(days=1)
    return out


def pin_schedule(learner: str, cfg: dict, start: dt.date, through: dt.date,
                 pid: str | None = None) -> dict[str, list[dict]]:
    """Two small samples of each unproven needed skill/tier, within a 30% cap."""
    from . import blueprint
    available: set[tuple[str, str]] = set()
    for info in blueprint.kinds().values():
        available.update((info["topic"], tier) for tier, _ in info["kinds"])
    recent: dict[tuple[str, str], list[int]] = defaultdict(list)
    for r in db.rows("SELECT topic,difficulty,correct FROM attempts WHERE learner=? AND repeat=0"
                     " AND disputed=0 AND void IS NULL ORDER BY id DESC", learner):
        key = (r["topic"], r["difficulty"])
        if len(recent[key]) < 4:
            recent[key].append(r["correct"])
    gate = _gate(learner, cfg, pid)
    weights, _ = _values(learner, cfg)
    cells = [key for key in available if key[0] in TOPICS and
             (key[1] != "hard" or (cfg["target"] > 580 and not gate)) and
             (len(recent[key]) < 4 or sum(recent[key]) < 3)]
    cells.sort(key=lambda key: (0 if not recent[key] else 1, -weights[key[0]], key[0], key[1]))
    exam = dt.date.fromisoformat(cfg["exam_date"])
    days = []
    slots = 0
    rough = sum(b["answered"] < 6 for b in progress.board(learner).values())
    study_index = 0
    d = start
    while d <= min(through, exam - dt.timedelta(days=2)):
        kind, _, minutes = kind_of(cfg, start, d, _override(pid, d) if pid else None,
                                   (lambda x: _override(pid, x)) if pid else None)
        if kind == "practice" and phase(start, exam, d) != "Final":
            study_index += 1
            q = math.floor(minutes * 60 / 95)
            mapping = rough > 5 and (d - start).days < 14 and study_index <= 5
            if q >= 7 and not mapping:
                days.append(d)
                slots += _slots(q)
        d += dt.timedelta(days=1)
    limit = min(len(days), math.floor(.3 * slots))
    out: dict[str, list[dict]] = {}
    if days and limit:
        # Two dated samples prove the plan covered a cell; the card reports any
        # shortfall rather than claiming coverage from one accidental item.
        ordered = [key for cell in cells for key in (cell, cell)]
        for day, (topic, tier) in zip(days[:limit], ordered[:limit]):
            out[day.isoformat()] = [{"topic": topic, "tier": tier, "count": 2}]
    # Keep-warm samples occupy focus-set slots, but do not consume the coverage
    # pin cap. One per week after the automatic promotion keeps the proof fresh.
    promoted = [(topic, raw) for topic, raw in (cfg.get("skills") or {}).items()
                if isinstance(raw, dict) and raw.get("state") == "strong" and raw.get("by") == "auto"]
    for topic, raw in promoted:
        weeks_seen: set[str] = set()
        d = start
        while d <= min(through, exam - dt.timedelta(days=2)):
            monday = (d - dt.timedelta(days=d.weekday())).isoformat()
            kind, _, minutes = kind_of(cfg, start, d, _override(pid, d) if pid else None,
                                       (lambda x: _override(pid, x)) if pid else None)
            if (d.isoformat() > raw.get("since", "") and monday not in weeks_seen and
                    kind == "practice" and minutes >= 15):
                out.setdefault(d.isoformat(), []).append({"topic": topic, "tier": "medium",
                                                         "count": 2, "why": "keep"})
                weeks_seen.add(monday)
            d += dt.timedelta(days=1)
    return out


def _own_tasks(pid: str | None, day: dt.date, study: bool) -> list[dict]:
    if not pid:
        return []
    out = []
    for row in db.rows("SELECT * FROM plan_tasks WHERE plan=? AND removed IS NULL ORDER BY created,id", pid):
        if (row["day"] == day.isoformat() or row["repeat"] == f"weekly:{day.weekday()}" or
                (study and row["repeat"] == "study_days")):
            out.append(dict(row))
    return out


def _seconds(learner: str) -> int:
    values = [r["spent"] for r in db.rows("SELECT COALESCE(ms,sms) AS spent FROM attempts WHERE learner=?"
                                          " AND COALESCE(ms,sms) IS NOT NULL AND repeat=0"
                                          " ORDER BY id DESC LIMIT 60", learner)]
    return max(60, min(150, round(statistics.median(values) / 1000))) if values else 95


def _words(learner: str, tz: int, cfg: dict) -> tuple[dict, int]:
    summary = deps.part("words", "today_summary")
    minutes = deps.part("words", "minutes_today")
    if not summary or not minutes:
        return {}, 0
    from . import prefs
    goal = prefs.get(learner, tz).get("words_goal", 0)
    info = summary(learner, tz)
    estimate_m = minutes(learner, tz)
    if not (goal or info.get("due")) or info.get("done"):
        return info, 0
    return info, max(0, math.ceil(estimate_m))


def _task(day: dt.date, kind: str, title: str, count: int, minutes: float,
          body: dict | None = None, *, suffix: str = "", subject: str = "math",
          topics: list[str] | None = None, why: list[dict] | None = None,
          detail: str = "", counted: bool = True, **other) -> dict:
    ident = f"{day.isoformat()}:{kind}{':' + suffix if suffix else ''}"
    path = "/api/words/run" if kind == "words" else "/api/mock/new" if kind == "test" else "/api/drill"
    body = {**(body or {}), "task": ident}
    return {"id": ident, "kind": kind, "title": title, "detail": detail,
            "topics": topics or [], "labels": [], "count": count,
            "minutes": round(minutes, 1), "subject": subject, "counted": counted,
            "status": "todo", "why": why or [], "alternatives": [],
            "start": {"path": path, "body": body}, "open": None,
            "session": None, "answered": 0, "total": count, "result": None, **other}


def _why(learner: str, topics: list[str], cfg: dict, gains: dict | None, gate: bool) -> list[dict]:
    board = progress.board(learner)
    gain_of = {x["topic"]: x for x in gains["skills"]} if gains else {}
    out = []
    for topic in topics:
        b = board.get(topic, {})
        g = gain_of.get(topic)
        if g:
            out.append({"text": f"{b.get('name', topic)} ≈ +{g['gain']} on the table · about {g['per_test']} of 44 a section",
                        "href": f"/me/#points-{topic}"})
        if b.get("answered"):
            out.append({"text": f"{b.get('name', topic)}: {round(100 * (b['accuracy'] or 0))}% right on {b['answered']}",
                        "href": f"/results/?skill={topic}"})
        if b.get("traps"):
            trap = b["traps"][0]
            out.append({"text": f"{b.get('name', topic)}: {len(b['traps'])} open mistakes, {trap['label']}",
                        "href": f"/review/?open=trap:{trap['id']}"})
        if _state(cfg, topic) == "focus":
            out.append({"text": f"{b.get('name', topic)} is on Focus", "href": "/plan/?tab=progress"})
        raw = (cfg.get("skills") or {}).get(topic)
        if isinstance(raw, dict) and raw.get("slipping"):
            out.append({"text": f"{b.get('name', topic)} is slipping · back to Normal until {raw.get('since')}",
                        "href": f"/results/?skill={topic}"})
    if gate:
        out.append({"text": "Below the route: Math tops out at 580 until module 1 reaches 14 of 22",
                    "href": "/me/#route"})
    return out or [{"text": "This gives an unmeasured skill a first look", "href": "/plan/?tab=progress"}]


def _tiers(cfg: dict, ph: str, gate: bool) -> list[str]:
    if gate and ph != "Final":
        return ["easy", "medium"]
    if ph == "Build":
        return ["easy", "medium"] if cfg["target"] < 550 else ["medium", "hard"] if cfg["target"] >= 690 else ["easy", "medium", "hard"]
    if ph == "Sharpen":
        return ["easy", "medium", "hard"] if cfg["target"] <= 580 else ["medium", "hard"]
    return ["easy", "medium", "hard"] if cfg["target"] <= 680 else ["medium", "hard"]


def _question_body(cfg: dict, ph: str, gate: bool, topics: list[str], count: int,
                   learner: str, *, pins: list[dict] | None = None) -> dict:
    body = {"topics": topics, "count": count, "source": "plan", "tiers": _tiers(cfg, ph, gate)}
    body["difficulty"] = body["tiers"]
    if ph == "Final":
        body["adaptive"] = False
    else:
        body["zone"] = "stretch"
    if pins:
        body["pins"] = [p for p in pins if p["tier"] in body["tiers"]]
    slow = False
    if cfg["clock"] == "auto" and ph == "Build" and topics:
        for topic in topics:
            times = [r["spent"] for r in db.rows(
                "SELECT COALESCE(ms,sms) AS spent FROM attempts WHERE learner=? AND topic=?"
                " AND COALESCE(ms,sms) IS NOT NULL ORDER BY id DESC LIMIT 20", learner, topic)]
            if len(times) >= 5 and statistics.median(times) > 1.3 * 95_000:
                slow = True
                break
    if cfg["clock"] == "always" or (cfg["clock"] == "auto" and (ph != "Build" or slow)):
        body["timing"] = "pace"
        body["timed"] = True
        body["minutes"] = round(count * 95 / 60)
    if cfg["clock"] == "off":
        body["timing"] = "off"
    # Only enough grid-ins to measure a gap may tilt a set.
    recent = db.rows("SELECT fmt,correct FROM attempts WHERE learner=? AND repeat=0"
                     " ORDER BY id DESC LIMIT 60", learner)
    spr = [r for r in recent if r["fmt"] == "spr"]
    mcq = [r for r in recent if r["fmt"] == "mcq"]
    if len(spr) >= 15 and mcq and sum(r["correct"] for r in mcq) / len(mcq) - sum(r["correct"] for r in spr) / len(spr) >= .15:
        body["fmt"] = "mix"
        body["spr_share"] = .5
    return body


def _custom_task(day: dt.date, row: dict) -> dict:
    typ = row.get("type") or "other"
    out = _task(day, "custom", row["title"], 0, row["minutes"], {}, suffix=row["id"],
                subject=row.get("subject") or ("rw" if typ == "rw" else "math"),
                detail="Your own task", why=[{"text": "Do this on your own, then mark it done.", "href": "/plan/"}])
    out["id"] = row["id"]
    out["type"] = typ
    out["repeat"] = row["repeat"]
    out["start"] = None
    return out


def _rw_tasks(day: dt.date, cfg: dict) -> list[dict]:
    """R&W minutes sit alongside Math, with focused domains on their own rows."""
    total = cfg.get("rw_minutes") or 0
    if not total:
        return []
    focus = cfg.get("rw_focus") or {}
    weights = [share * {"focus": 2, "normal": 1, "strong": .4}[focus.get(domain, "normal")]
               for domain, share in zip(RW_DOMAINS, RW_SHARES)]
    n = total // 5
    quotas = [n * w / sum(weights) for w in weights]
    blocks = [math.floor(q) for q in quotas]
    for i in sorted(range(4), key=lambda j: (-(quotas[j] - blocks[j]), j))[:n - sum(blocks)]:
        blocks[i] += 1
    rows = []
    shared = []
    shared_minutes = 0
    for domain, block in zip(RW_DOMAINS, blocks):
        if block and focus.get(domain) == "focus":
            rows.append((domain, block * 5, domain))
        elif block:
            shared.append(domain)
            shared_minutes += block * 5
    if shared:
        rows.append((", ".join(shared), shared_minutes, "shared"))
    out = []
    for label, minutes, suffix in rows:
        task = _task(day, "custom", f"R&W · {label} · {minutes} min", 0, minutes,
                     suffix=f"rw:{suffix}", subject="rw",
                     detail="On your own · Bluebook or official SAT practice",
                     why=[{"text": "This is your Reading & Writing time", "href": "/plan/?tab=progress"}])
        task["type"] = "rw"
        task["start"] = None
        task["domains"] = [label] if suffix != "shared" else shared
        out.append(task)
    return out


def _check_for(learner: str, row, day: dt.date, topics: list[str], budget: int) -> dict | None:
    if budget < 4:
        return None
    cfg = cfg_of(row)
    focused = [t for t in topics if _state(cfg, t) == "focus"][:2]
    if not focused:
        return None
    monday = day - dt.timedelta(days=day.weekday())
    week = [monday + dt.timedelta(days=n) for n in range(7)]
    topic = focused[0]
    allocated = allocate(learner, cfg, dt.date.fromisoformat(row["start"]), week[-1], row["id"])
    study = [d for d in week if d >= dt.date.fromisoformat(row["start"]) and
             topic in allocated.get(d.isoformat(), []) and plan_kind(cfg, row, d) in ("practice", "test")]
    if not study or day not in (study[0], study[-1]):
        return None
    before = next((db.one("SELECT * FROM sessions WHERE learner=? AND cfg LIKE ? ORDER BY started LIMIT 1",
                          learner, f'%{d.isoformat()}:check:{topic}%')
                   for d in study[:-1] if d < day), None)
    if day == study[-1] and before and before["finished"]:
        body = {"rematch": before["id"], "timing": "pace"}
        title = f"After · {progress.topics()[topic].name}"
    elif day == study[0]:
        body = {"topics": [topic], "count": 4, "order": "mixed", "feedback": "end", "repairs": "end"}
        title = f"Before · {progress.topics()[topic].name}"
    else:
        return None
    task = _task(day, "check", title, 4, 4 * _seconds(learner) / 60, body,
                 suffix=topic, topics=[topic],
                 why=[{"text": "A fresh check on the same question types will show what changed",
                       "href": "/plan/?tab=progress"}])
    return task


def plan_kind(cfg: dict, row, day: dt.date) -> str:
    return kind_of(cfg, dt.date.fromisoformat(row["start"]), day,
                   _override(row["id"], day))[0]


def _sweep_count(learner: str, cfg: dict, start: dt.date, day: dt.date) -> int:
    if phase(start, dt.date.fromisoformat(cfg["exam_date"]), day) != "Final":
        return 0
    closed = db.one("SELECT COUNT(*) AS n FROM traps WHERE learner=? AND closed IS NOT NULL", learner)["n"]
    if closed < 5:
        return 0
    exam = dt.date.fromisoformat(cfg["exam_date"])
    final_days = [start + dt.timedelta(days=i) for i in range((exam - start).days)
                  if phase(start, exam, start + dt.timedelta(days=i)) == "Final" and
                  kind_of(cfg, start, start + dt.timedelta(days=i))[0] == "practice"]
    if not final_days:
        return 0
    slots = min(len(final_days), max(1, math.ceil(closed / 3)))
    picks = [final_days[min(len(final_days) - 1, math.floor(i * len(final_days) / slots))]
             for i in range(slots)]
    if day not in picks:
        return 0
    index = picks.index(day)
    return closed // slots + int(index < closed % slots)


def _checkpoint(learner: str, cfg: dict, start: dt.date, day: dt.date) -> dict | None:
    rule = cfg.get("checkpoints", "every_2nd")
    if rule == "off":
        return None
    exams = [start + dt.timedelta(days=i) for i in range((day - start).days + 1)
             if kind_of(cfg, start, start + dt.timedelta(days=i))[0] == "test" and
             start + dt.timedelta(days=i) not in _rehearsal_dates(cfg, start)]
    n = len(exams)
    if not n or (rule == "every_2nd" and n % 2):
        return None
    scored = [s for s in reversed(estimate._sittings(learner))
              if s["kind"] in ("module", "section") and s["at"][:10] <= day.isoformat()]
    a = next((s for s in scored if s["at"][:10] >= start.isoformat()), None)
    if not a:
        a = next((s for s in reversed(scored) if s["at"][:10] >= (start - dt.timedelta(days=14)).isoformat()), None)
    if not a:
        return None
    b = next((s for s in reversed(scored) if s["at"][:10] >= (start + dt.timedelta(days=14)).isoformat()
              and s["id"] != a["id"] and s["kind"] == "module"), None)
    index = n if rule == "every" else n // 2
    base = b if b and index % 2 == 0 else a
    return {"kind": "twin", "twin_of": base["id"], "checkpoint": index}


def build_day(learner: str, row, day: dt.date, topics: list[str] | None = None,
              preview_minutes: int | None = None, pins: list[dict] | None = None,
              words_plan: tuple[dict, int] | None = None) -> dict:
    """One budget for ordinary days and Today-I-have previews alike."""
    cfg = cfg_of(row)
    pid = row["id"]
    start = dt.date.fromisoformat(row["start"])
    exam = dt.date.fromisoformat(cfg["exam_date"])
    ov = _override(pid, day)
    if preview_minutes is not None:
        if type(preview_minutes) is not int or preview_minutes not in (0, *range(5, 241)):
            raise HTTPException(422, "minutes must be 0 or 5–240")
        ov["minutes"] = preview_minutes
    kind, test, m = kind_of(cfg, start, day, ov, lambda d: _override(pid, d))
    ph = phase(start, exam, day)
    tasks: list[dict] = []
    cut: list[dict] = []
    if kind not in ("practice", "test"):
        if kind == "eve":
            tasks.append(_task(day, "custom", "Read your trap sheet", 0, 5,
                               counted=False, detail="Check your personal traps once, then rest"))
            tasks[-1]["start"] = None
        return {"date": day.isoformat(), "day": day.isoformat(), "kind": kind, "test": None,
                "phase": ph, "minutes": 0, "tasks": tasks, "budget": {"m": 0, "g": 0, "w": 0, "q": 0, "s": 95, "cut": []},
                "custom": False, "overridden": bool(ov)}
    moved_rows = db.rows("SELECT task,day,note FROM plan_marks WHERE plan=? AND status='moved' AND to_day=?",
                         pid, day.isoformat())
    moved_in = []
    for mark in moved_rows:
        moved = _json(mark["note"], {}) or {}
        if moved.get("id") == mark["task"]:
            moved_in.append({**moved, "moved_from": mark["day"]})
    moved_out = [(_json(r["note"], {}) or {}) for r in
                 db.rows("SELECT note FROM plan_marks WHERE plan=? AND status='moved' AND day=?",
                         pid, day.isoformat())]
    outgoing = sum(t.get("minutes", 0) for t in moved_out)
    m += sum(t["minutes"] for t in moved_in) - outgoing
    custom = [_custom_task(day, t) for t in _own_tasks(pid, day, True)]
    rw_tasks = _rw_tasks(day, cfg)
    kept = list(custom)
    while kept and m - sum(t["minutes"] for t in kept) < 10:
        drop = max(kept, key=lambda t: t["minutes"])
        kept.remove(drop)
        cut.append({"kind": "custom", "count": 1, "to": "skip today" if drop.get("repeat") else "next study day"})
    own_minutes = sum(t["minutes"] for t in kept) + sum(t["minutes"] for t in moved_in)
    g = m - own_minutes
    s = _seconds(learner)
    first_study = next((start + dt.timedelta(days=n) for n in range(7)
                        if cfg["days"][(start + dt.timedelta(days=n)).weekday()] == "1"), start)
    measuring = bool(cfg.get("measure") and cfg.get("current") is None and day == first_study)
    if measuring:
        test = "diagnostic"
        kind = "test"
    if test and g < 35 and not measuring:
        cut.append({"kind": "test", "count": 1, "to": "next study day with 35 min"})
        test = None
        kind = "practice"
    if test == "section" and g < 70:
        test = "module"
    test_minutes = 30 if measuring else 70 if test == "section" else 35 if test else 0
    if test:
        rehearsal = day in _rehearsal_dates(cfg, start)
        body = {"full": test == "section", "timed": True, "pause": not rehearsal}
        checkpoint = None if rehearsal or measuring else _checkpoint(learner, cfg, start, day)
        if checkpoint:
            body.update({"kind": checkpoint["kind"], "twin_of": checkpoint["twin_of"]})
        aim = round((cfg["current"] or 520) + (cfg["target"] - (cfg["current"] or 520)) *
                    (day - start).days / max(1, (exam - start).days), -1)
        tasks.append(_task(day, "test", "Diagnostic · find your starting score" if measuring else
                           "Dress rehearsal" if rehearsal else f"{test.title()} test",
                           20 if measuring else 44 if test == "section" else 22,
                           test_minutes, body, detail="Fresh adaptive test"))
        if measuring:
            tasks[-1]["start"] = {"path": "/api/session", "body": {"task": tasks[-1]["id"]}}
        tasks[-1].update(rehearsal=rehearsal, aim=aim,
                         checkpoint=checkpoint["checkpoint"] if checkpoint else None)
        g -= test_minutes
    word_info, word_need = words_plan if words_plan is not None else _words(learner, row["tz"] or 0, cfg)
    w = min(word_need, max(3, round(.2 * g))) if word_need and g >= 3 else 0
    q = min(120, math.floor(max(0, g - w) * 60 / s))
    left = q
    reserve = math.ceil((.3 if ph == "Final" else .4) * q) if q >= 20 else 0
    gate = _gate(learner, cfg, pid)
    b = progress.board(learner)
    gains = estimate.gains(learner)
    focus_topics = topics if topics is not None else allocate(learner, cfg, start, day, pid).get(day.isoformat(), [])
    warm = progress.warmup_candidates(learner, row["tz"] or 0)
    warm_n = min(8 if ph == "Final" else 5, max(2, math.ceil((.3 if ph == "Final" else .4) * q))) if warm["size"] else 0
    if warm_n and left >= 2:
        take = min(warm_n, left)
        tasks.append(_task(day, "recheck", "Warm-up", take, take * s / 60,
                           {"source": "warmup", "count": take},
                           detail=" · ".join(x for x in (warm['checks'] and f"{len(warm['checks'])} check-ins due",
                                                          warm['fading'] and f"{len(warm['fading'])} fading") if x),
                           why=[{"text": "Review questions just as they start to fade", "href": "/review/"}]))
        left -= take
    elif warm_n:
        cut.append({"kind": "recheck", "count": warm_n, "to": "next study day"})
    traps = progress.open_traps(learner)
    if traps:
        sure = {r["template"] for r in db.rows("SELECT template FROM attempts WHERE learner=? AND correct=0"
                                                    " AND conf='sure' ORDER BY id DESC LIMIT 80", learner)}
        traps.sort(key=lambda t: (-int(t["template"] in sure), -t["hits"], t["last"]))
        if gate:
            traps.sort(key=lambda t: (db.one("SELECT difficulty FROM attempts WHERE learner=? AND template=?"
                                             " ORDER BY id DESC LIMIT 1", learner, t["template"]) or
                                      {"difficulty": "medium"})["difficulty"] == "hard")
        target = min(2 * len({t["template"] for t in traps}), max(4, round(.3 * q)))
        target += target % 2
        if left >= 4:
            take = min(left, target)
            tasks.append(_task(day, "fix", "Fix mistakes", take, take * s / 60,
                               {"mistakes": True, "ids": [t["id"] for t in traps], "count": take},
                               detail=", ".join(t["label"] for t in traps[:3]),
                               why=[{"text": f"{t['label']} · {t['hits']} times", "href": f"/review/?open=trap:{t['id']}"}
                                    for t in traps[:3]]))
            left -= take
        else:
            cut.append({"kind": "fix", "count": target, "to": "next study day"})
    hard_skips = {parts[1] for mark in db.rows("SELECT note FROM plan_marks WHERE plan=? AND status='skipped'"
                                                " AND note LIKE 'too_hard:%'", pid)
                  if (parts := (mark["note"] or "").split(":")) and len(parts) == 3
                  and parts[2] == day.isoformat()}
    learn_topic = next((t for t in focus_topics if t in hard_skips), None) or next(
        (t for t in focus_topics if b[t]["answered"] < 5 or
         (ph == "Build" and b[t]["mastery"] < .35)), None)
    if learn_topic and not measuring and day not in _taper_dates(cfg) and left - reserve >= 4:
        tasks.append(_task(day, "learn", f"Learn it · {b[learn_topic]['name']}", 3, 4 * s / 60,
                           {"source": "learn", "topics": [learn_topic], "example": True, "count": 3},
                           topics=[learn_topic], detail="A worked example + 3",
                           why=_why(learner, [learn_topic], cfg, gains, gate)))
        left -= 4
    elif learn_topic and not measuring:
        cut.append({"kind": "learn", "count": 4, "to": "next study day"})
    check = _check_for(learner, row, day, focus_topics, left - reserve)
    if check:
        tasks.append(check)
        left -= 4
    sweep_task = None
    sweep_target = _sweep_count(learner, cfg, start, day)
    if sweep_target >= 3 and left - reserve >= 3:
        sweep_n = min(sweep_target, math.floor(.4 * q), left - reserve)
        if sweep_n >= 3:
            sweep_task = _task(day, "sweep", "Sweep · still fixed?", sweep_n, sweep_n * s / 60,
                               {"pool": "checks", "sweep": True, "count": sweep_n},
                               why=[{"text": "Revisit old mistakes with fresh numbers before test day",
                                     "href": "/review/"}])
            left -= sweep_n
    rough = sum(b[t]["answered"] < 6 for t in TOPICS)
    map_on = rough > 5 and (day - start).days < 14 and day not in _taper_dates(cfg)
    # The first five practice days are the only Map days.
    map_n = sum(x <= day.isoformat() for x in allocate(learner, cfg, start, day, pid))
    map_on = map_on and map_n <= 5
    focus_n = left if left >= 3 else 0
    if focus_n:
        task_kind = "map" if map_on else "focus"
        if pins is None and not map_on:
            pins = pin_schedule(learner, cfg, start, exam, pid).get(day.isoformat(), [])
        body = ({"source": "probe", "count": focus_n} if map_on else
                _question_body(cfg, ph, gate, focus_topics, focus_n, learner, pins=pins))
        why = ([{"text": f"Map {rough} skills with fewer than six first tries", "href": "/plan/?tab=progress"}]
               if map_on else _why(learner, focus_topics, cfg, gains, gate))
        tasks.append(_task(day, task_kind, "Map" if map_on else "Focus set", focus_n,
                           focus_n * s / 60, body, topics=focus_topics,
                           detail=" · ".join(b[t]["name"] for t in focus_topics), why=why,
                           difficulty=_tiers(cfg, ph, gate), timed=body.get("timing") == "pace",
                           fmt=body.get("fmt", "mix")))
        left -= focus_n
    if sweep_task:
        tasks.append(sweep_task)
    if left:
        cut.append({"kind": "focus", "count": left, "to": "next study day"})
    if w:
        word_body = {"mode": "mix", "deck": {"source": "today"}, "box": w,
                     "run": day.isoformat()}
        if (cfg.get("rw_focus") or {}).get("Craft and Structure") == "focus":
            word_body["in_context"] = 2
            word_body["goal"] = 15
        if (cfg.get("rw_focus") or {}).get("Expression of Ideas") == "focus":
            word_body["transitions"] = 6
        tasks.append(_task(day, "words", "Words", 0, w,
                           word_body, subject="rw",
                           detail=f"{word_info.get('due', 0)} due · due first",
                           why=[{"text": "SAT words and transitions due today", "href": "/words/"}]))
    tasks += kept + moved_in + rw_tasks
    seen_ids = {t["id"] for t in tasks}
    tasks += [t for t in moved_out if t.get("id") and t["id"] not in seen_ids]
    extras = cfg.get("extras") or {}
    if extras.get("qotd"):
        tasks.append(_task(day, "qotd", "Question of the day", 1, 0, {}, counted=False))
    if extras.get("challenge"):
        tasks.append(_task(day, "challenge", "Daily challenge", 10, 0, {}, counted=False))
    budget = {"m": m, "g": g, "w": w, "q": q, "s": s, "cut": cut, "rw": sum(t["minutes"] for t in rw_tasks)}
    return {"date": day.isoformat(), "day": day.isoformat(), "kind": kind,
            "test": test, "phase": ph, "minutes": round(m + sum(t["minutes"] for t in rw_tasks), 1), "tasks": tasks, "budget": budget,
            "custom": bool(custom), "overridden": bool(ov)}


def _local_of(stamp: str | None, tz: int) -> str | None:
    if not stamp:
        return None
    moment = dt.datetime.fromisoformat(stamp)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=dt.timezone.utc)
    return (moment.astimezone(dt.timezone.utc) - dt.timedelta(minutes=tz)).date().isoformat()


def _sessions(learner: str) -> list[dict]:
    out = []
    for row in db.rows("SELECT * FROM sessions WHERE learner=? ORDER BY started", learner):
        cfg = _json(row["cfg"], {}) or {}
        out.append({**dict(row), "config": cfg})
    return out


def _test_band(task: dict, session: dict) -> dict | None:
    result = _json(session.get("result"), {}) or {}
    band = result.get("estimate") or {}
    if not isinstance(band, dict) or band.get("low") is None or band.get("high") is None:
        return None
    low, high = band["low"], band["high"]
    aim = task.get("aim")
    verdict = "beat" if aim is not None and low >= aim else "under" if aim is not None and high < aim else "within"
    return {"mid": round((low + high) / 2), "low": low, "high": high, "verdict": verdict}


def _module_questions(session: dict) -> list[dict]:
    questions = _json(session.get("questions"), {}) or {}
    if isinstance(questions, dict):
        questions = questions.get("module1", [])
    return questions if isinstance(questions, list) else []


def checkpoints_of(learner: str, row) -> list[dict]:
    """Compare finished twin module-1 slots with their stored baseline form."""
    sittings = _sessions(learner)
    by_id = {s["id"]: s for s in sittings}
    out = []
    for current in sittings:
        base = by_id.get(current["config"].get("twin_of"))
        if not base or not current["finished"] or not base["finished"]:
            continue
        if not row["start"] <= current["finished"][:10] <= cfg_of(row)["exam_date"]:
            continue
        current_qs, base_qs = _module_questions(current), _module_questions(base)
        if len(current_qs) != 22 or len(base_qs) != 22:
            continue
        answers = _json(current["answers"], {}) or {}
        base_answers = _json(base["answers"], {}) or {}
        counts = Counter()
        slots = []
        for index, (was, now) in enumerate(zip(base_qs, current_qs), 1):
            before = scoring.is_correct(was, base_answers.get(was["id"]))
            after = scoring.is_correct(now, answers.get(now["id"]))
            change = ("held" if after else "slipped") if before else ("fixed" if after else "still_missed")
            template = now.get("key") or now.get("template")
            practised = db.one("SELECT COUNT(*) AS n FROM attempts WHERE learner=? AND template=?"
                               " AND at>? AND at<? AND session!=?",
                               learner, template, base["finished"], current["started"], current["id"])["n"] if template else 0
            counts[change] += 1
            if practised:
                counts[change + "_practised"] += 1
            slots.append({"n": index, "qid": now["id"], "baseline_qid": was["id"],
                          "topic": now.get("topic") or now.get("topic_name"),
                          "tier": now.get("difficulty"), "template": template,
                          "change": change, "practised": bool(practised), "practice_count": practised})
        old_band = (_json(base["result"], {}) or {}).get("estimate") or {}
        new_band = (_json(current["result"], {}) or {}).get("estimate") or {}
        fix = [s["qid"] for s in slots if s["change"] in ("slipped", "still_missed")]
        out.append({"subject": "math", "session": current["id"], "baseline": base["id"],
                    "baseline_band": old_band, "band": new_band, "slots": slots,
                    "counts": {key: counts[key] for key in ("fixed", "held", "slipped", "still_missed")},
                    "fix": {"from_session": current["id"], "only": fix, "each": 2,
                            "sibling": True, "source": "twin", "task": f"{today(row['tz'] or 0)}:extra"}})
    return out


def _task_status(learner: str, pid: str, day: dt.date, task: dict,
                 sessions: list[dict], tz: int, words_summary: dict | None = None) -> dict:
    out = dict(task)
    mark = db.one("SELECT * FROM plan_marks WHERE plan=? AND day=? AND task=?",
                  pid, day.isoformat(), task["id"])
    if mark:
        if mark["status"] == "moved":
            out.update(status="moved", moved_to=mark["to_day"])
            return out
        if mark["status"] == "skipped":
            out.update(status="skipped", reason=mark["note"])
            return out
        if mark["status"] == "done":
            out.update(status="marked" if task["kind"] != "custom" else "done",
                       minutes_done=mark["minutes"] or task["minutes"], where=mark["note"])
            return out
    matches = [s for s in sessions if s["config"].get("task") == task["id"]]
    if task["kind"] == "words":
        summary = words_summary
        if summary is None:
            read = deps.part("words", "today_summary")
            summary = read(learner, tz) if read else {}
        if summary.get("done") and day == today(tz):
            out["status"] = "done"
    if matches:
        s = matches[-1]
        answers = _json(s["answers"], {}) or {}
        out["session"] = s["id"]
        out["answered"] = len(answers)
        out["total"] = max(out.get("count") or 0, len(_json(s["questions"], []) or []))
        if s["finished"] or (out["count"] and out["answered"] >= out["count"]):
            out["status"] = "made_up" if _local_of(s["finished"] or s["started"], tz) > day.isoformat() else "done"
        else:
            out["status"] = "active"
        if s["result"]:
            result = _json(s["result"], {}) or {}
            out["result"] = {"right": result.get("right", result.get("correct", 0)),
                             "asked": result.get("asked", len(answers)), "ms": result.get("ms")}
            if task["kind"] == "test":
                out["result"].update(_test_band(task, s) or {})
    if task["kind"] == "focus" and out["status"] == "todo" and task.get("topics"):
        marks = ",".join("?" for _ in task["topics"])
        count = db.one(f"SELECT COUNT(*) AS n FROM attempts WHERE learner=? AND topic IN ({marks})"
                       " AND substr(at,1,10)=? AND repeat=0", learner, *task["topics"], day.isoformat())["n"]
        if count >= task["count"]:
            out["status"] = "done"
            out["answered"] = count
    if task["kind"] == "test" and out["status"] == "todo":
        same_day = next((s for s in reversed(sessions) if s["kind"] in deps.TEST_KINDS and s["finished"] and
                         _local_of(s["finished"], tz) == day.isoformat()), None)
        if same_day:
            out["status"] = "done"
            out["session"] = same_day["id"]
            band = _test_band(task, same_day)
            if band:
                out["result"] = band
    return out


def day_view(learner: str, row, date: dt.date, *, allocated: dict | None = None,
             pins: dict | None = None,
             sessions: list[dict] | None = None, ledger: dict | None = None,
             preview_minutes: int | None = None,
             words_plan: tuple[dict, int] | None = None) -> dict:
    cfg = cfg_of(row)
    start, exam = dt.date.fromisoformat(row["start"]), dt.date.fromisoformat(cfg["exam_date"])
    if date < start or date > exam:
        raise HTTPException(404, "date is outside this plan")
    frozen = db.one("SELECT * FROM plan_days WHERE plan=? AND day=?", row["id"], date.isoformat())
    if frozen and preview_minutes is None:
        base = {"date": date.isoformat(), "day": date.isoformat(), "kind": frozen["kind"],
                "minutes": frozen["minutes"], "test": frozen["test"], "phase": frozen["phase"],
                "tasks": _json(frozen["tasks"], []) or [], "budget": None,
                "custom": False, "overridden": False, "frozen": True}
    else:
        topics = allocated.get(date.isoformat(), []) if allocated is not None else None
        base = build_day(learner, row, date, topics, preview_minutes,
                         pins.get(date.isoformat(), []) if pins is not None else None,
                         words_plan=words_plan)
        base["frozen"] = False
    tz = row["tz"] or 0
    sessions = sessions if sessions is not None else _sessions(learner)
    base["tasks"] = [_task_status(learner, row["id"], date, t, sessions, tz,
                                  words_plan[0] if words_plan is not None else None)
                     for t in base["tasks"]]
    if ledger is None:
        ledger = {d["day"]: d for d in progress.days(learner, tz, 53)["days"]}
    fact = ledger.get(date.isoformat(), {})
    counted = [t for t in base["tasks"] if t.get("counted") and t["status"] != "moved"]
    done = [t for t in counted if t["status"] in ("done", "made_up", "marked")]
    base["minutes_done"] = fact.get("minutes", 0)
    base["questions"] = fact.get("questions", 0)
    base["right"] = fact.get("right", 0)
    base["tasks_planned"] = len(counted)
    base["tasks_done"] = len(done)
    if base["kind"] in ("exam", "eve", "rest", "off"):
        base["status"] = "rest" if base["kind"] in ("rest", "eve") else base["kind"]
    elif counted and (len(done) == len(counted) or base["minutes_done"] >= .8 * base["minutes"]):
        base["status"] = "done"
    elif counted and all(t["status"] == "skipped" for t in counted):
        base["status"] = "skipped"
    elif done or base["minutes_done"] or base["questions"]:
        base["status"] = "partial"
    elif date < today(tz):
        base["status"] = "missed"
    else:
        base["status"] = "planned"
    if any(t["status"] == "made_up" for t in counted):
        base["status"] = "made_up"
    if base.get("budget") and base["budget"]["m"] < .6 * _base_minutes(cfg, date, start) and _override(row["id"], date).get("trim"):
        if base["status"] == "done":
            base["status"] = "partial"
        base["short_day"] = True
    return base


def freeze(learner: str, row, tz: int | None = None) -> None:
    """Write each elapsed day once. Edits never redraw these rows."""
    cfg = cfg_of(row)
    start = dt.date.fromisoformat(row["start"])
    end = min(dt.date.fromisoformat(cfg["exam_date"]), today(row["tz"] if tz is None else tz) - dt.timedelta(days=1))
    if end < start:
        return
    existing = {r["day"] for r in db.rows("SELECT day FROM plan_days WHERE plan=?", row["id"])}
    allocation = allocate(learner, cfg, start, end, row["id"])
    pins = pin_schedule(learner, cfg, start, dt.date.fromisoformat(cfg["exam_date"]), row["id"])
    with db.atomic() as c:
        d = start
        while d <= end:
            if d.isoformat() not in existing:
                built = build_day(learner, row, d, allocation.get(d.isoformat(), []),
                                  pins=pins.get(d.isoformat(), []))
                c.execute("INSERT INTO plan_days(plan,day,kind,minutes,test,phase,tasks,gate) VALUES (?,?,?,?,?,?,?,?)",
                          (row["id"], d.isoformat(), built["kind"], built["minutes"], built["test"],
                           built["phase"], json.dumps(built["tasks"]), int(_gate(learner, cfg, row["id"]))))
            d += dt.timedelta(days=1)


def _week_days(days: list[dict]) -> list[dict]:
    weeks: dict[str, list[dict]] = defaultdict(list)
    for day in days:
        date = dt.date.fromisoformat(day["date"])
        monday = date - dt.timedelta(days=date.weekday())
        weeks[monday.isoformat()].append(day)
    out = []
    for index, (week, group) in enumerate(sorted(weeks.items()), 1):
        topics = Counter(t for d in group for task in d["tasks"] for t in task.get("topics", []))
        phase_ = group[0]["phase"]
        tests = next((d["date"] for d in group if d["kind"] == "test"), None)
        title = f"{phase_} · {', '.join(t for t, _ in topics.most_common(3)) or 'Math practice'}"
        if tests:
            title += f" · Test {tests}"
        out.append({"n": index, "from": group[0]["date"], "to": group[-1]["date"],
                    "theme": title, "tasks_planned": sum(d["tasks_planned"] for d in group),
                    "tasks_done": sum(d["tasks_done"] for d in group)})
    return out


def streak_of(days: list[dict], local: str) -> tuple[int, int]:
    """Count completed study days, letting rest days pass without a reset."""
    run = best = 0
    current = 0
    for d in days:
        if d["date"] > local:
            break
        if d["kind"] in ("rest", "off", "eve"):
            if d["questions"] or d["minutes_done"]:
                run += 1
                best = max(best, run)
            continue
        if d["kind"] not in ("practice", "test"):
            continue
        if d["status"] in ("done", "partial", "made_up"):
            run += 1
            best = max(best, run)
        elif d["date"] != local:
            run = 0
        current = run
    return current, best


def _stats(learner: str, row, days: list[dict], ledger: dict) -> dict:
    start = row["start"]
    study = [d for d in days if d["kind"] in ("practice", "test")]
    elapsed = [d for d in study if d["date"] <= today(row["tz"] or 0).isoformat()]
    marks = db.rows("SELECT status FROM plan_marks WHERE plan=?", row["id"])
    traps = db.one("SELECT COUNT(*) AS opened,SUM(closed IS NOT NULL) AS closed,"
                   " SUM(closed IS NULL) AS open FROM traps WHERE learner=? AND opened>=?", learner, start)
    recheck = progress.rechecks_passed(learner, start)
    streak, longest = streak_of(days, today(row["tz"] or 0).isoformat())
    planned_split: Counter = Counter()
    done_split: Counter = Counter()
    for d in days:
        for task in d["tasks"]:
            if task.get("counted"):
                planned_split[task["kind"]] += task["minutes"]
                if task["status"] in ("done", "made_up", "marked"):
                    done_split[task["kind"]] += task["minutes"]
    week_start = today(row["tz"] or 0) - dt.timedelta(days=today(row["tz"] or 0).weekday())
    week = [d for d in days if week_start.isoformat() <= d["date"] <= (week_start + dt.timedelta(days=6)).isoformat()]
    return {"days_planned": len(study), "days_done": sum(d["status"] in ("done", "made_up") for d in elapsed),
            "study_days_total": len(study), "tasks_done": sum(d["tasks_done"] for d in days),
            "tasks_skipped": sum(r["status"] == "skipped" for r in marks),
            "made_up": sum(d["status"] == "made_up" for d in days),
            "minutes_planned": round(sum(d["minutes"] for d in study)),
            "minutes_done": sum(ledger.get(d["date"], {}).get("minutes", 0) for d in days),
            "questions": sum(ledger.get(d["date"], {}).get("questions", 0) for d in days),
            "right": sum(ledger.get(d["date"], {}).get("right", 0) for d in days),
            "mistakes_opened": traps["opened"] or 0, "mistakes_closed": traps["closed"] or 0,
            "mistakes_open": traps["open"] or 0, "rechecks_passed": recheck["n"],
            "rechecks_due": len(progress.due_rechecks(learner)),
            "tests": sum(ledger.get(d["date"], {}).get("tests", 0) for d in days),
            "streak": streak, "longest": longest,
            "week": {"minutes_planned": sum(d["minutes"] for d in week),
                     "minutes_done": sum(d["minutes_done"] for d in week),
                     "days": [{"date": d["date"], "status": d["status"]} for d in week]},
            "split_planned": dict(planned_split), "split_done": dict(done_split)}


def _sittings(learner: str) -> list[dict]:
    return [{"session": s["id"], "kind": s["kind"], "at": s["at"],
             "low": s["low"], "high": s["high"]} for s in estimate._sittings(learner)[:60]]


def _pace_suggest(learner: str, row) -> tuple[dict | None, dict | None]:
    cfg = cfg_of(row)
    sit = [x for x in estimate._sittings(learner) if x["at"] >= row["start"] and x["kind"] in deps.TEST_KINDS][:3]
    if not sit or cfg.get("current") is None:
        return None, None
    mean = round(sum(x["mid"] for x in sit) / len(sit) / 10) * 10
    elapsed = max(0, (dt.date.fromisoformat(sit[0]["at"][:10]) - dt.date.fromisoformat(row["start"])).days)
    span = max(1, (dt.date.fromisoformat(cfg["exam_date"]) - dt.date.fromisoformat(row["start"])).days)
    expected = cfg["current"] + (min(cfg["target"], 780) - cfg["current"]) * min(1, elapsed / span)
    delta = round(mean - expected)
    pace = {"status": "Target reached" if mean >= min(cfg["target"], 780) else
            "On pace" if abs(delta) <= 35 else "Ahead" if delta > 0 else "Behind",
            "delta": delta, "mean": mean, "expected": round(expected), "sessions": [x["id"] for x in sit]}
    changed_after = max(row["updated"] or row["created"], row["drift_seen"] or "")
    fresh = any(s["at"] > changed_after for s in sit)
    kind = "target" if mean >= min(cfg["target"], 780) else "up" if mean - cfg["current"] >= 40 else "down" if cfg["current"] - mean >= 40 else None
    suggest = {"kind": kind, "current": mean, "sessions": [x["id"] for x in sit]} if fresh and kind else None
    return pace, suggest


def _points(learner: str, row=None) -> dict | None:
    gains = estimate.gains(learner)
    if not gains:
        return None
    high = {x["topic"]: x["gain"] / max(x["minutes"], 10) for x in gains["skills"] if x["gain"] >= 5}
    floor = statistics.median(high.values()) * .1 if high else 0
    items = sorted([{**x, "v": round(high.get(x["topic"], floor), 5), "floor": x["topic"] not in high}
                    for x in gains["skills"]], key=lambda x: (-x["v"], x["topic"]))
    start = _json(row["start_points"], {}) if row else {}
    cfg = cfg_of(row) if row else {}
    route = estimate.route(learner)
    return {"total": gains["total"], "top3": gains["top3"],
            "claimed": start.get("total", gains["total"]) - gains["total"], "skills": items,
            "route": {**(route or {}), "gate": _gate(learner, cfg, row["id"]) if row else False}}


def _coverage(learner: str, cfg: dict, days: list[dict], gate: bool) -> dict:
    from . import blueprint
    kinds = blueprint.kinds()
    rows = db.rows("SELECT topic,difficulty,correct FROM attempts WHERE learner=? AND repeat=0"
                   " AND disputed=0 AND void IS NULL ORDER BY id DESC", learner)
    by: dict[tuple[str, str], list[int]] = defaultdict(list)
    for r in rows:
        key = (r["topic"], r["difficulty"])
        if len(by[key]) < 4:
            by[key].append(r["correct"])
    planned: dict[tuple[str, str], list[str]] = defaultdict(list)
    for day in days:
        for task in day["tasks"]:
            for pin in ((task.get("start") or {}).get("body") or {}).get("pins", []):
                planned[(pin["topic"], pin["tier"])].append(day["date"])
    cells = []
    counts: Counter = Counter()
    for topic in TOPICS:
        for tier in ("easy", "medium", "hard"):
            available = any(tier == shape[0] for info in kinds.values()
                            if info.get("topic") == topic for shape in info.get("kinds", []))
            last = by.get((topic, tier), [])
            state = "n/a" if not available else "proven" if len(last) == 4 and sum(last) >= 3 else "shaky" if last else "untested"
            needed = available and (tier != "hard" or (cfg["target"] > 580 and not gate))
            places = planned[(topic, tier)]
            planned_ok = len(places) >= 2
            cell = {"topic": topic, "tier": tier, "state": state, "right": sum(last), "n": len(last),
                    "needed": needed, "next": places[0] if places else None, "planned": planned_ok}
            cells.append(cell)
            if needed:
                counts[state] += 1
                if state != "proven" and not planned_ok:
                    counts["unplanned"] += 1
    week_slots = sum(_slots(max(0, math.floor(d["minutes"] * 60 / 95))) for d in days[:7]
                     if d["kind"] == "practice")
    window = max(14, math.ceil(19 / max(1, week_slots)) * 7)
    return {"math": {"cells": cells, "counts": {k: counts[k] for k in ("proven", "shaky", "untested", "unplanned")},
                     "window_days": window}}


def _domains_skills(learner: str, cfg: dict, row, days: list[dict]) -> tuple[list[dict], list[dict]]:
    board = progress.board(learner)
    domain_shares = shares(learner, cfg)
    planned: Counter = Counter()
    done: Counter = Counter()
    for day in days:
        for task in day["tasks"]:
            if task["kind"] in ("focus", "map"):
                for topic in task["topics"]:
                    domain = estimate.DOMAIN_OF[topic]
                    planned[domain] += task["minutes"] / max(1, len(task["topics"]))
                    if task["status"] in ("done", "marked", "made_up"):
                        done[domain] += task["minutes"] / max(1, len(task["topics"]))
    start_mastery = _json(row["start_mastery"], {}) or {}
    domains = []
    for domain in DOMAINS:
        topics = [board[t] for t in TOPICS if estimate.DOMAIN_OF[t] == domain]
        answered = sum(t["answered"] for t in topics)
        right = sum(round((t["accuracy"] or 0) * t["answered"]) for t in topics)
        domains.append({"domain": domain, "state": cfg.get("focus", {}).get(domain, "normal"),
                        "mastery": round(statistics.mean(t["mastery"] for t in topics), 3),
                        "start_mastery": start_mastery.get(domain, 0),
                        "right": right, "answered": answered, "share_planned": domain_shares[domain],
                        "share_done": round(done[domain] / max(1, sum(done.values())), 3)})
    skills = [{"topic": t, "answered": board[t]["answered"],
               "right": round((board[t]["accuracy"] or 0) * board[t]["answered"]),
               "traps": len(board[t]["traps"]), "last": board[t]["last"], "gap": None,
               "state": _state(cfg, t)} for t in TOPICS]
    skills.sort(key=lambda x: (x["right"] / x["answered"] if x["answered"] else -1, x["topic"]))
    return domains, skills


def rw_domains(learner: str, cfg: dict, days: list[dict]) -> list[dict]:
    logged = db.rows('SELECT domain,source,missed,"of" AS total FROM rw_log WHERE learner=?', learner)
    out = []
    for domain in RW_DOMAINS:
        evidence = [r for r in logged if r["domain"] == domain]
        planned = sum(t["minutes"] for d in days for t in d["tasks"]
                      if t.get("subject") == "rw" and t.get("type") == "rw" and domain in t.get("domains", []))
        done = sum(t["minutes"] for d in days for t in d["tasks"]
                   if t.get("subject") == "rw" and t.get("type") == "rw" and
                   domain in t.get("domains", []) and t["status"] in ("done", "made_up", "marked"))
        out.append({"domain": domain, "state": (cfg.get("rw_focus") or {}).get(domain, "normal"),
                    "missed": sum(r["missed"] for r in evidence), "of": sum(r["total"] for r in evidence),
                    "sources": dict(Counter(r["source"] for r in evidence)),
                    "minutes_planned": planned, "minutes_done": done})
    return out


def log_rw(learner: str, rows: list[dict], *, source: str = "bluebook",
           ref: str | None = None, day: str | None = None) -> int:
    """U2 and Plan share one validated R&W evidence write path."""
    if source not in ("bluebook", "task") or not isinstance(rows, list) or not 1 <= len(rows) <= 4:
        raise HTTPException(422, "rwlog: source or rows are invalid")
    at = _date(day, "day").isoformat() if day else today().isoformat()
    for item in rows:
        if (not isinstance(item, dict) or item.get("domain") not in RW_DOMAINS or
                type(item.get("missed")) is not int or type(item.get("of")) is not int or
                not 0 <= item["missed"] <= item["of"] <= 54):
            raise HTTPException(422, "rwlog: invalid domain or counts")
    with db.atomic() as c:
        for item in rows:
            c.execute('INSERT INTO rw_log(learner,at,source,ref,domain,missed,"of") VALUES (?,?,?,?,?,?,?)',
                      (learner, at, source, ref, item["domain"], item["missed"], item["of"]))
    return len(rows)


def words_focus_goal(learner: str, cfg: dict, before: dict | None = None) -> int | str | None:
    """Return a Words goal change when Craft and Structure enters or leaves Focus."""
    from . import prefs
    old = (before or {}).get("rw_focus") or {}
    new = cfg.get("rw_focus") or {}
    was, now = old.get("Craft and Structure") == "focus", new.get("Craft and Structure") == "focus"
    if now and not was:
        value = prefs.get(learner).get("words_goal", 10)
        cfg["words_previous"] = value
        return min(20, (value if isinstance(value, int) else 10) + 5)
    if was and not now:
        previous = (before or {}).get("words_previous")
        cfg.pop("words_previous", None)
        return previous
    if was and now and before and "words_previous" in before:
        cfg["words_previous"] = before["words_previous"]
    return None


def _check_receipt(session: dict | None) -> dict | None:
    if not session:
        return None
    result = _json(session.get("result"), {}) or {}
    attempts = db.rows("SELECT correct,COALESCE(ms,sms) AS spent FROM attempts WHERE session=?"
                       " AND repeat=0 AND disputed=0 AND void IS NULL", session["id"])
    return {"sid": session["id"], "right": result.get("right", sum(a["correct"] for a in attempts)),
            "of": result.get("asked", len(attempts)),
            "ms": sum(a["spent"] or 0 for a in attempts)}


def checks_of(learner: str, row) -> list[dict]:
    """Before/After evidence and the 12-answer proof ladder, by focus skill."""
    sessions = []
    for s in db.rows("SELECT * FROM sessions WHERE learner=? AND cfg LIKE '%:check:%' ORDER BY started", learner):
        cfg = _json(s["cfg"], {}) or {}
        match = re.fullmatch(r"(\d{4}-\d{2}-\d{2}):check:([a-z_]+)", cfg.get("task") or "")
        if match and row["start"] <= match.group(1) <= cfg_of(row)["exam_date"]:
            sessions.append((dict(s), cfg, match.group(1), match.group(2)))
    groups: dict[tuple[str, str], dict] = {}
    for session, cfg, day, topic in sessions:
        d = dt.date.fromisoformat(day)
        week = (d - dt.timedelta(days=d.weekday())).isoformat()
        group = groups.setdefault((week, topic), {"subject": "math", "topic": topic, "week": week,
                                                  "before": None, "after": None})
        group["after" if cfg.get("rematch") else "before"] = _check_receipt(session)
    out = []
    focused = [t for t in TOPICS if _state(cfg_of(row), t) == "focus"]
    for topic in focused:
        if not any(t == topic for _, t in groups):
            groups[(row["start"], topic)] = {"subject": "math", "topic": topic, "week": row["start"],
                                             "before": None, "after": None}
    for (week, topic), entry in sorted(groups.items()):
        answers = db.rows("SELECT correct FROM attempts WHERE learner=? AND topic=? AND repeat=0"
                          " AND disputed=0 AND void IS NULL AND difficulty IN ('medium','hard')"
                          " ORDER BY id DESC LIMIT 12", learner, topic)
        right = sum(a["correct"] for a in answers)
        recent = {"right": right, "of": len(answers)}
        before, after = entry["before"], entry["after"]
        passed = bool(len(answers) >= 12 and
                      ((after and before and after["right"] >= 3 and after["ms"] <= before["ms"]
                        and right >= 9) or
                       (right >= 11 and not progress.open_traps(learner, topic))))
        result = ("passed" if passed else "learn" if after and after["right"] <= 1 else
                  "again" if after else None)
        out.append({**entry, "recent": recent, "result": result})
    return out


def auto_focus(learner: str, row, checks: list[dict]) -> tuple[dict | None, list[dict]]:
    """Move a proved skill to Strong, then give its focus place to real points."""
    from . import prefs
    cfg = cfg_of(row)
    settings = prefs.get(learner, row["tz"] or 0)
    banners = []
    changed = False
    for topic, raw in list((cfg.get("skills") or {}).items()):
        if (not isinstance(raw, dict) or raw.get("state") != "strong" or raw.get("pin")):
            continue
        answers = db.rows("SELECT correct FROM attempts WHERE learner=? AND topic=? AND repeat=0"
                          " AND disputed=0 AND void IS NULL AND difficulty IN ('medium','hard')"
                          " ORDER BY id DESC LIMIT 12", learner, topic)
        if len(answers) < 12 or sum(a["correct"] for a in answers) > 7:
            continue
        until = (today(row["tz"] or 0) + dt.timedelta(days=7)).isoformat()
        cfg["skills"][topic] = {"state": "normal", "by": "auto", "since": until, "slipping": True}
        banners.append({"kind": "slipping", "topic": topic,
                        "text": f"{topic} is slipping · back to Normal until {until}"})
        event(row["id"], "auto", f"{topic} is slipping · 7 of 12 or fewer · Normal until {until}",
              field="skills", before=raw, after=cfg["skills"][topic])
        changed = True
    for check in checks:
        topic = check["topic"]
        raw = cfg.get("skills", {}).get(topic)
        state = raw.get("state") if isinstance(raw, dict) else raw
        if check["result"] != "passed" or state != "focus" or (isinstance(raw, dict) and raw.get("pin")):
            continue
        if not settings.get("plan_auto_focus", True):
            banners.append({"kind": "graduated", "topic": topic,
                            "text": f"{topic} passed its check; move it to Strong?"})
            continue
        skills = cfg.setdefault("skills", {})
        skills[topic] = {"state": "strong", "by": "auto", "since": today(row["tz"] or 0).isoformat()}
        weights, _ = _values(learner, cfg)
        next_topic = next((t for t in sorted(TOPICS, key=lambda t: (-weights[t], t))
                           if t != topic and _state(cfg, t) == "normal" and
                           not (isinstance(skills.get(t), dict) and
                                skills[t].get("since", "") > today(row["tz"] or 0).isoformat())), None)
        if next_topic:
            skills[next_topic] = {"state": "focus", "by": "auto", "since": today(row["tz"] or 0).isoformat()}
        event(row["id"], "auto", f"{topic} passed its check; next focus: {next_topic or 'none'}",
              field="skills", before=topic, after=next_topic)
        changed = True
    if changed:
        db.run("UPDATE plans SET cfg=?,updated=? WHERE id=?", json.dumps(cfg), deps.now(), row["id"])
        row = db.one("SELECT * FROM plans WHERE id=?", row["id"])
    return row if changed else None, banners


def _changes(row, local_day: str) -> dict:
    rs = [dict(r) for r in db.rows("SELECT id,at,kind,text,day FROM plan_events WHERE plan=? ORDER BY at DESC,id DESC LIMIT 100", row["id"])]
    counts = dict(Counter(r["kind"] for r in rs))
    previous = db.one("SELECT made_on FROM plan_snapshots WHERE plan=? AND made_on<?"
                      " ORDER BY made_on DESC LIMIT 1", row["id"], local_day)
    return {"since": previous["made_on"] if previous else row["start"],
            "today": [{"text": r["text"], "day": r["day"],
                                                   "cause": r["kind"], "event": r["id"]}
                                                  for r in rs if _local_of(r["at"], row["tz"] or 0) == local_day],
            "counts": counts}


def event(pid: str, kind: str, text: str, day: str | None = None,
          field: str | None = None, before=None, after=None) -> None:
    db.run("INSERT INTO plan_events(plan,at,kind,field,from_v,to_v,text,day) VALUES (?,?,?,?,?,?,?,?)",
           pid, deps.now(), kind, field, json.dumps(before), json.dumps(after), text, day)


def snapshot(learner: str, row, days: list[dict]) -> None:
    local = today(row["tz"] or 0).isoformat()
    if db.one("SELECT 1 FROM plan_snapshots WHERE plan=? AND made_on=?", row["id"], local):
        return
    future = [{"day": d["date"], "kind": d["kind"], "minutes": d["minutes"],
               "test": d["test"], "phase": d["phase"], "tasks": [
        {"id": t["id"], "kind": t["kind"], "topics": t["topics"], "count": t["count"]} for t in d["tasks"]]}
        for d in days if local <= d["date"] < (today(row["tz"] or 0) + dt.timedelta(days=14)).isoformat()]
    old = db.one("SELECT made_on,days FROM plan_snapshots WHERE plan=? ORDER BY made_on DESC LIMIT 1", row["id"])
    before = {d["day"]: d for d in _json(old["days"], []) or []} if old else {}
    with db.atomic() as c:
        c.execute("INSERT OR IGNORE INTO plan_snapshots(plan,made_on,days) VALUES (?,?,?)",
                  (row["id"], local, json.dumps(future)))
        if old:
            since = old["made_on"] + "T00:00:00"
            for trap in c.execute("SELECT label,opened,closed FROM traps WHERE learner=?"
                                  " AND (opened>? OR closed>?)", (learner, since, since)):
                action = "opened" if trap["opened"] > since else "fixed"
                c.execute("INSERT INTO plan_events(plan,at,kind,text) VALUES (?,?,?,?)",
                          (row["id"], deps.now(), "mistake", f"{trap['label']} {action}"))
            for sitting in c.execute("SELECT id,finished FROM sessions WHERE learner=? AND finished>?"
                                     " AND kind IN ('diagnostic','module','mock','section','paper')", (learner, since)):
                c.execute("INSERT INTO plan_events(plan,at,kind,text) VALUES (?,?,?,?)",
                          (row["id"], deps.now(), "sitting", f"Scored sitting {sitting['id']}"))
            previous_phase = phase(dt.date.fromisoformat(row["start"]),
                                   dt.date.fromisoformat(cfg_of(row)["exam_date"]),
                                   dt.date.fromisoformat(old["made_on"]))
            current_phase = phase(dt.date.fromisoformat(row["start"]),
                                  dt.date.fromisoformat(cfg_of(row)["exam_date"]), today(row["tz"] or 0))
            if current_phase != previous_phase:
                c.execute("INSERT INTO plan_events(plan,at,kind,text) VALUES (?,?,?,?)",
                          (row["id"], deps.now(), "phase", f"{current_phase} starts"))
            for d in future:
                prior = before.get(d["day"])
                if prior and prior != d:
                    edit = c.execute("SELECT text FROM plan_events WHERE plan=? AND kind='edit'"
                                     " AND (day=? OR day IS NULL) AND at>=? ORDER BY id DESC LIMIT 1",
                                     (row["id"], d["day"], since)).fetchone()
                    if prior["kind"] != d["kind"] and d["kind"] == "off":
                        line = f"{dt.date.fromisoformat(d['day']):%a} off"
                    elif prior.get("test") != d.get("test"):
                        line = f"{d['day']} {prior.get('test') or 'practice'} → {d.get('test') or 'practice'}"
                    else:
                        line = f"{d['day']} re-dealt from your answers"
                    c.execute("INSERT INTO plan_events(plan,at,kind,text,day) VALUES (?,?,?,?,?)",
                              (row["id"], deps.now(), "edit" if edit else "auto", line, d["day"]))
        c.execute("DELETE FROM plan_snapshots WHERE plan=? AND made_on<?",
                  (row["id"], (today(row["tz"] or 0) - dt.timedelta(days=60)).isoformat()))


def _summary(row, days: list[dict] | None = None) -> dict:
    cfg = cfg_of(row)
    exam = dt.date.fromisoformat(cfg["exam_date"])
    if days is None:
        frozen = db.rows("SELECT day,kind,minutes FROM plan_days WHERE plan=? ORDER BY day", row["id"])
        ledger = {d["day"]: d for d in progress.days(row["learner"], row["tz"] or 0, 53)["days"]}
        record_days = [{"date": d["day"], "kind": d["kind"], "minutes": d["minutes"],
                        "minutes_done": ledger.get(d["day"], {}).get("minutes", 0),
                        "status": "done" if ledger.get(d["day"], {}).get("minutes", 0) >= .8 * d["minutes"]
                        else "partial" if ledger.get(d["day"], {}).get("minutes", 0) else "missed"}
                       for d in frozen]
    else:
        record_days = days
    study = [d for d in record_days if d["kind"] in ("practice", "test") and
             d["date"] <= today(row["tz"] or 0).isoformat()]
    by_dow = []
    for weekday in range(7):
        chosen = [d for d in study if dt.date.fromisoformat(d["date"]).weekday() == weekday]
        by_dow.append(round(100 * sum(d["status"] in ("done", "partial", "made_up") for d in chosen) /
                            len(chosen)) if chosen else 0)
    events = [dict(e) for e in db.rows("SELECT at,text FROM plan_events WHERE plan=? ORDER BY id DESC LIMIT 3", row["id"])]
    result = _json(row["result"], None)
    fixed = db.one("SELECT COUNT(*) AS n,SUM(relapses) AS relapsed FROM traps WHERE learner=? AND opened>=?"
                   " AND opened<=? AND closed IS NOT NULL", row["learner"], row["start"], cfg["exam_date"])
    record = {"hours": round(sum(d["minutes_done"] for d in study) / 60, 1),
              "days_pct": round(100 * sum(d["status"] in ("done", "partial", "made_up") for d in study) /
                                len(study)) if study else 0,
              "by_dow": by_dow, "start_mid": cfg.get("current"),
              "end_mid": (result or {}).get("math"), "result": result,
              "fixed": fixed["n"] or 0, "relapsed": fixed["relapsed"] or 0,
              "checks_passed": progress.rechecks_passed(row["learner"], row["start"])["n"],
              "best_weekday": max(range(7), key=lambda n: by_dow[n]),
              "changes": db.one("SELECT COUNT(*) AS n FROM plan_events WHERE plan=?", row["id"])["n"]}
    return {"id": row["id"], "name": row["name"],
            "status": "finished" if row["result"] else "archived" if row["archived"] else "active",
            "built": row["created"], "start": row["start"], "exam": cfg["exam_date"],
            "target": cfg["target"], "days_left": max(0, (exam - today(row["tz"] or 0)).days),
            "tasks_done": sum(d["tasks_done"] for d in days) if days else 0,
            "adherence": round(sum(d["status"] in ("done", "made_up") for d in days) /
                               max(1, sum(d["kind"] in ("practice", "test") for d in days)), 3) if days else 0,
            "result": result, "total_target": cfg["target"] + cfg["rw_target"] if cfg.get("rw_target") else None,
            "total_result": sum(result.get(k, 0) for k in ("math", "rw")) if result else None,
            "record": record, "recent_events": events}


def _bank(learner: str) -> dict:
    cat = deps.part("practice", "catalogue")
    data = cat() if cat else {"by_topic": {}}
    names = data.get("topics", {})
    topic = next(iter(data["by_topic"]), None)
    label = names[topic].name if topic and topic in names else topic
    out = {"topics": len(data["by_topic"]), "templates": sum(map(len, data["by_topic"].values())),
           "domains": len(DOMAINS), "example": {"label": label, "topic": topic}}
    words_stats = deps.part("words", "me_stats")
    if words_stats:
        try:
            out["words"] = words_stats(learner)
        except TypeError:
            pass
    return out


def rhythm_of(learner: str, tz: int = 0) -> dict:
    recent = progress.days(learner, tz, 4)["days"][-28:]
    active = [d for d in recent if d["questions"] or d["words"] or d["tests"] or d["minutes"]]
    by_dow = []
    for weekday in range(7):
        dates = [d for d in recent if dt.date.fromisoformat(d["day"]).weekday() == weekday]
        worked = [d for d in dates if d in active]
        by_dow.append({"studied": len(worked), "of": len(dates),
                       "median_min": round(statistics.median([d["minutes"] for d in worked])) if worked else 0})
    return {"weeks": 4, "days_per_week": round(len(active) / 4, 1),
            "median_min": round(statistics.median([d["minutes"] for d in active])) if active else None,
            "weekly_min": round(sum(d["minutes"] for d in active) / 4),
            "by_dow": by_dow, "active_days": len(active)}


def _progress_extra(learner: str, row, days: list[dict], checks: list[dict]) -> dict:
    """Evidence behind Progress; every minute and answer comes from learner rows."""
    start = row["start"]
    cutoff14 = (today(row["tz"] or 0) - dt.timedelta(days=14)).isoformat()
    attempts = [dict(r) for r in db.rows("SELECT topic,correct,at,COALESCE(ms,sms) AS spent,conf,difficulty"
                                        " FROM attempts WHERE learner=? AND repeat=0 AND disputed=0"
                                        " AND void IS NULL ORDER BY at,id", learner)]
    gained = estimate.gains(learner)
    gain_of = {x["topic"]: x["gain"] for x in gained["skills"]} if gained else {}
    fixed = Counter(r["topic"] for r in db.rows("SELECT topic FROM traps WHERE learner=?"
                                                   " AND closed IS NOT NULL AND closed>=?", learner, start))
    bought = []
    for topic in TOPICS:
        rows = [r for r in attempts if r["topic"] == topic]
        inside = [r for r in rows if r["at"][:10] >= start]
        minutes = round(sum(min(max(r["spent"] or 0, 0), 600_000) for r in inside) / 60_000, 1)
        if minutes < 10:
            continue
        before_rows = [r for r in rows if r["at"][:10] < start][-20:] or inside[:20]
        before_ids = {id(r) for r in before_rows}
        after_rows = [r for r in inside if id(r) not in before_ids][-20:]
        before = {"right": sum(r["correct"] for r in before_rows), "of": len(before_rows)}
        after = {"right": sum(r["correct"] for r in after_rows), "of": len(after_rows)}
        minutes14 = round(sum(min(max(r["spent"] or 0, 0), 600_000) for r in inside
                              if r["at"][:10] >= cutoff14) / 60_000, 1)
        not_moving = bool(minutes14 >= 60 and len(before_rows) == len(after_rows) == 20 and
                          after["right"] - before["right"] < 2)
        bought.append({"topic": topic, "subject": "math", "minutes": minutes, "minutes_14d": minutes14,
                       "before": before, "after": after, "not_moving": not_moving,
                       "fixed": fixed[topic],
                       "check": next((c for c in reversed(checks) if c["topic"] == topic), None),
                       "claimed": gain_of.get(topic)})
    bought.sort(key=lambda r: (-r["minutes"], r["topic"]))
    period = min(60, max(1, (today(row["tz"] or 0) - dt.date.fromisoformat(start)).days + 1))
    causes = progress.causes(learner, row["tz"] or 0, days=period)
    confidence = {}
    for label in ("sure", "unsure", "guess"):
        group = [r for r in attempts if r["at"][:10] >= start and r["conf"] == label]
        confidence[label] = {"right": sum(r["correct"] for r in group), "of": len(group),
                             "accuracy": round(sum(r["correct"] for r in group) / len(group), 3) if group else None}
    split = Counter()
    done = Counter()
    for d in days:
        for task in d["tasks"]:
            if task["kind"] in ("focus", "map", "check", "learn", "pace"):
                for topic in task.get("topics", []):
                    domain = estimate.DOMAIN_OF.get(topic)
                    if domain:
                        share = task["minutes"] / max(1, len(task["topics"]))
                        split[domain] += share
                        if task["status"] in ("done", "marked", "made_up"):
                            done[domain] += share
    points_by_domain = Counter()
    if gained:
        points_by_domain.update({x["domain"]: x["gain"] for x in gained["by_domain"]})
    split_domain = [{"domain": domain, "minutes_planned": round(split[domain], 1),
                     "minutes_done": round(done[domain], 1),
                     "time_share": round(split[domain] / max(1, sum(split.values())), 3),
                     "points_share": round(points_by_domain[domain] / max(1, sum(points_by_domain.values())), 3)}
                    for domain in DOMAINS]
    return {"bought": bought, "causes": causes, "calibration": confidence,
            "skill_pace": progress.pace(learner), "split_domain": split_domain,
            "changes_counts": dict(Counter(r["kind"] for r in db.rows(
                "SELECT kind FROM plan_events WHERE plan=?", row["id"]))) }


def _verdict_levers(learner: str, row, days: list[dict], score_pace: dict | None) -> tuple[dict, list[dict], dict]:
    cfg = cfg_of(row)
    exam = dt.date.fromisoformat(cfg["exam_date"])
    local = today(row["tz"] or 0)
    weeks_left = max(1 / 7, (exam - local).days / 7)
    recent = estimate._mean3(estimate._sittings(learner))
    baseline = recent or cfg.get("current") or 520
    needs = round((min(cfg["target"], 780) - baseline) / weeks_left, 1)
    projected = estimate.projection(learner, exam)
    made = projected["slope_used"] if projected else None
    verdict = {"math": {"kind": "on_pace" if made is not None and made >= needs else
                         "behind" if made is not None else "unmeasured",
                        "made_per_week": made, "needs_per_week": needs,
                        "mean": recent, "projection": projected}}
    future = [d for d in days if d["date"] >= local.isoformat() and d["kind"] in ("practice", "test")]
    available = round(sum(d["minutes"] for d in future))
    path = (estimate.need(cfg["target"], learner).get("path") or {})
    required = path.get("minutes") if path.get("reachable") else None

    def capacity(minutes: int, study_days: int, needed: int | None) -> dict:
        gap = minutes - needed if needed is not None else None
        return {"study_days": study_days, "hours_available": round(minutes / 60, 1),
                "minutes_available": minutes, "hours_needed": round(needed / 60, 1) if needed is not None else None,
                "fits": gap >= 0 if gap is not None else None,
                "spare_h": round(max(0, gap) / 60, 1) if gap is not None else None,
                "short_h": round(max(0, -gap) / 60, 1) if gap is not None else None}

    workload = capacity(available, len(future), required)
    if required is not None and required > available and future:
        workload["suggest_minutes"] = min(240, cfg["minutes"] + math.ceil((required - available) / len(future) / 5) * 5)
    levers = []
    if cfg["minutes"] <= 225:
        effect = capacity(available + len(future) * 15, len(future), required)
        levers.append({"kind": "minutes", "label": f"Add 15 min a day · {len(future)} days",
                       "patch": {"minutes": cfg["minutes"] + 15},
                       "effect": {"needs_per_week": needs, **effect}})
    if "0" in cfg["days"]:
        weekday = cfg["days"].index("0")
        changed = cfg["days"][:weekday] + "1" + cfg["days"][weekday + 1:]
        added = sum((local + dt.timedelta(days=n)).weekday() == weekday
                    for n in range((exam - local).days))
        effect = capacity(available + added * cfg["minutes"], len(future) + added, required)
        levers.append({"kind": "days", "label": f"Add {('Mon','Tue','Wed','Thu','Fri','Sat','Sun')[weekday]}",
                       "patch": {"days": changed}, "effect": {"needs_per_week": needs,
                       **effect}})
    if not cfg.get("booked"):
        later = next((d for d in satdates.upcoming(local) if d > cfg["exam_date"]), None)
        if later:
            later_weeks = max(1 / 7, (dt.date.fromisoformat(later) - local).days / 7)
            later_date = dt.date.fromisoformat(later)
            extra_days = sum(cfg["days"][(exam + dt.timedelta(days=n)).weekday()] == "1"
                             for n in range(1, (later_date - exam).days))
            effect = capacity(available + extra_days * cfg["minutes"], len(future) + extra_days, required)
            levers.append({"kind": "date", "label": f"Move to {later}",
                           "patch": {"exam_date": later},
                           "effect": {"needs_per_week": round((min(cfg["target"], 780) - baseline) / later_weeks, 1),
                                      **effect}})
    return verdict, levers[:3], workload


def propose(learner: str, tz: int = 0) -> dict:
    """A credible one-tap starting point; no stored plan is needed."""
    from . import prefs
    row = db.one("SELECT * FROM learners WHERE id=?", learner)
    sittings = estimate._sittings(learner)
    current = estimate._mean3(sittings) or (round(sittings[0]["mid"] / 10) * 10 if sittings else None)
    if row and row["current"] is not None:
        current = row["current"]
    published = [d for d in satdates.upcoming(today(tz)) if d >= (today(tz) + dt.timedelta(days=28)).isoformat()]
    if not published:
        published = satdates.upcoming(today(tz))
    if not published:
        raise HTTPException(409, "no published SAT date is available")
    ledger = progress.days(learner, tz, 4)["days"]
    recent = ledger[-28:]
    studied = [d for d in recent if d["questions"] or d["minutes"] or d["tests"] or d["words"]]
    weekday_counts = Counter(dt.date.fromisoformat(d["day"]).weekday() for d in studied)
    pattern = "".join("1" if weekday_counts[i] >= 2 else "0" for i in range(7))
    if pattern.count("1") < 3:
        pattern = "1111100"
    chips = (15, 30, 45, 60, 90, 120, 150, 180, 240)
    median_min = statistics.median([d["minutes"] for d in studied]) if studied else 45
    snapped = max(15, max((c for c in chips if c <= median_min), default=15))
    cfg = {"current": current, "measure": current is None,
           "target": row["target"] if row and row["target"] else min(round((current or 500) / 10) * 10 + 100, 780) if current else 600,
           "exam_date": row["exam_date"] if row and row["exam_date"] and row["exam_date"] > today(tz).isoformat() else published[0],
           "minutes": row["minutes"] if row and row["minutes"] else snapped,
           "days": row["days"] if row and row["days"] else pattern,
           "tests": row["tests"] if row and row["tests"] else "weekly",
           "checkpoints": "every_2nd", "focus": _json(row["focus"], {}) if row else {}}
    if cfg["current"] is not None and cfg["target"] < cfg["current"]:
        cfg["target"] = cfg["current"]
    cfg = validate(cfg, learner, tz)
    return {"cfg": cfg, "why": {"current": "results" if sittings else "default",
                                 "target": "profile" if row and row["target"] else "default",
                                 "minutes": "profile" if row and row["minutes"] else "rhythm" if studied else "default",
                                 "days": "profile" if row and row["days"] else "rhythm" if studied else "default",
                                 "tests": "profile" if row and row["tests"] else "default"},
            "preview": preview(learner, cfg, tz)}


def preview(learner: str, cfg: dict, tz: int = 0) -> dict:
    """Fast, read-only wizard arithmetic; no draft or plan is written."""
    start = today(tz)
    exam = dt.date.fromisoformat(cfg["exam_date"])
    weeks = math.ceil((exam - start).days / 7)
    split = shares(learner, cfg)
    gains = estimate.gains(learner)
    points = _points(learner)
    active_days = []
    tests = []
    for n in range((exam - start).days + 1):
        d = start + dt.timedelta(days=n)
        kind, test, minutes = kind_of(cfg, start, d)
        if kind in ("practice", "test"):
            active_days.append((d, kind, minutes))
        if test:
            tests.append((d, test))
    study_days = len(active_days)
    hours = round(sum(m for _, _, m in active_days) / 60, 1)
    pace = (cfg["target"] - (cfg["current"] or 520)) / max(1, weeks)
    point_split = {}
    if gains:
        by = Counter(x["domain"] for x in gains["skills"] for _ in range(max(0, x["gain"])))
        point_split = {d: round(by[d] / max(1, sum(by.values())), 3) for d in DOMAINS}
    note = scoring.fraction_for(cfg["target"])
    sample = {"date": None, "tasks": []}
    if active_days:
        d, _, m = active_days[0]
        topics = allocate(learner, cfg, start, d).get(d.isoformat(), [])
        preview_row = {"id": "preview", "cfg": json.dumps(cfg), "start": start.isoformat(), "tz": tz}
        made = build_day(learner, preview_row, d, topics)
        sample = {"date": d.isoformat(), "tasks": made["tasks"]}
    week = []
    allocation = allocate(learner, cfg, start, start + dt.timedelta(days=6))
    for n in range(min(7, (exam - start).days + 1)):
        d = start + dt.timedelta(days=n)
        kind, _, minutes = kind_of(cfg, start, d)
        week.append({"date": d.isoformat(), "kind": kind, "minutes": minutes,
                     "topics": allocation.get(d.isoformat(), [])})
    return {"study_days": study_days, "tests": {"count": len(tests), "size": cfg["test_size"],
                                                   "weekday": cfg["test_day"]},
            "hours": hours, "questions": sum(math.floor(m * 60 / 95) for _, _, m in active_days),
            "pace_per_week": round(pace, 1),
            "pace_tag": "Steady" if pace <= 15 else "Ambitious" if pace <= 30 else "Very ambitious",
            "per_date": [], "later_date": None, "split": split, "base_split": dict(progress.BLUEPRINT),
            "split_points": {"math": point_split} if gains else None,
            "points": {"math": points}, "phases": [phase(start, exam, d) for d, _, _ in active_days],
            "target_note": {"route_up": cfg["target"] > 580, "route_right": 14, "route_of": 22,
                            "points_pct": round(note["fraction"] * 100), "capped": note["capped"]},
            "sample_day": sample, "week": week, "first": None,
            "calendar": [{"date": d.isoformat(), "kind": k, "minutes": m,
                                                   "phase": phase(start, exam, d), "test": next((t for x, t in tests if x == d), None)}
                                                  for d, k, m in active_days], "warnings": []}


def payload(learner: str, tz: int = 0, pid: str | None = None, *, shared: bool = False) -> dict:
    row = owned_row(learner, pid) if pid else active_row(learner)
    draft = db.one("SELECT plan_draft FROM learners WHERE id=?", learner)
    plans = db.rows("SELECT * FROM plans WHERE learner=? ORDER BY created DESC", learner)
    if row is None:
        out = {"active": None, "plans": [_summary(p) for p in plans],
               "draft": _json(draft["plan_draft"], None) if draft else None,
               "bank": _bank(learner), "proposal": propose(learner, tz)}
        return out
    cfg = cfg_of(row)
    if not shared:
        from . import prefs
        booked = prefs.get(learner, tz).get("registered") == cfg["exam_date"]
        if cfg.get("booked") != booked:
            cfg["booked"] = booked
            db.run("UPDATE plans SET cfg=? WHERE id=?", json.dumps(cfg), row["id"])
            row = db.one("SELECT * FROM plans WHERE id=?", row["id"])
    if cfg.get("measure") and cfg.get("current") is None and not shared:
        measured = next((s for s in reversed(estimate._sittings(learner))
                         if s["at"] >= row["start"] and s["kind"] in deps.TEST_KINDS), None)
        if measured:
            current = round(measured["mid"] / 10) * 10
            cfg["current"] = current
            cfg["measure"] = False
            cfg.setdefault("sections", {}).setdefault("math", {})["current"] = current
            with db.atomic() as c:
                c.execute("UPDATE plans SET cfg=?,updated=? WHERE id=?", (json.dumps(cfg), deps.now(), row["id"]))
                c.execute("UPDATE learners SET current=? WHERE id=?", (current, learner))
                event(row["id"], "auto", f"Starting score set to {current} from your diagnostic",
                      field="current", after=current)
            row = db.one("SELECT * FROM plans WHERE id=?", row["id"])
    checks = checks_of(learner, row)
    banners = []
    if not shared:
        changed, banners = auto_focus(learner, row, checks)
        if changed:
            row = changed
            cfg = cfg_of(row)
    freeze(learner, row, tz)
    start, exam = dt.date.fromisoformat(row["start"]), dt.date.fromisoformat(cfg["exam_date"])
    allocation = allocate(learner, cfg, start, exam, row["id"])
    pins = pin_schedule(learner, cfg, start, exam, row["id"])
    sessions = _sessions(learner)
    ledger = {d["day"]: d for d in progress.days(learner, tz, 53)["days"]}
    # Every generated day uses today's Words due count and minutes. Read it
    # once for this response, rather than rescanning the full library per day.
    words_plan = _words(learner, row["tz"] or 0, cfg)
    days = [day_view(learner, row, start + dt.timedelta(days=i), allocated=allocation, pins=pins,
                     sessions=sessions, ledger=ledger, words_plan=words_plan)
            for i in range((exam - start).days + 1)]
    if not shared:
        snapshot(learner, row, days)
    local = today(tz).isoformat()
    current = next((d for d in days if d["date"] == local), None)
    stats = _stats(learner, row, days, ledger)
    pace, suggest = _pace_suggest(learner, row)
    domains, skills = _domains_skills(learner, cfg, row, days)
    progress_extra = _progress_extra(learner, row, days, checks)
    verdict, levers, workload = _verdict_levers(learner, row, days, pace)
    last7 = [d for d in days if (today(tz) - dt.timedelta(days=7)).isoformat() <= d["date"] < local
             and d["kind"] in ("practice", "test")]
    behind = None
    if len(last7) >= 3:
        done = sum(d["status"] in ("done", "partial", "made_up") for d in last7)
        if done / len(last7) < .6:
            avg = round(sum(d["minutes_done"] for d in last7) / len(last7))
            chips = (15, 30, 45, 60, 90, 120, 150, 180, 240)
            behind = {"planned": len(last7), "done": done, "avg_minutes": avg,
                      "suggest_minutes": next((x for x in chips if x >= max(15, avg)), 240)}
    if behind:
        recent28 = [d for d in days if (today(tz) - dt.timedelta(days=28)).isoformat() <= d["date"] < local
                    and d["kind"] in ("practice", "test")]
        fixes = [{"kind": "shorter", "label": f"Fit to {behind['suggest_minutes']} min",
                  "patch": {"minutes": behind["suggest_minutes"]}}]
        for weekday in range(7):
            sample = [d for d in recent28 if dt.date.fromisoformat(d["date"]).weekday() == weekday]
            missed = sum(d["status"] == "missed" for d in sample)
            if len(sample) >= 2 and missed >= 2 and missed >= len(sample) / 2:
                day_minutes = list(cfg.get("day_minutes") or [None] * 7)
                day_minutes[weekday] = 15
                fixes.append({"kind": "weekday", "weekday": weekday,
                              "label": f"Make {('Mon','Tue','Wed','Thu','Fri','Sat','Sun')[weekday]} 15 min",
                              "patch": {"day_minutes": day_minutes}})
        behind["fixes"] = fixes
        behind["text"] = f"{len(last7) - done} study days missed · catch up in 15 min"
    if local > cfg["exam_date"]:
        state = "after"
    elif local == cfg["exam_date"]:
        state = "exam"
    elif local == (exam - dt.timedelta(days=1)).isoformat():
        state = "eve"
    else:
        state = "active"
    active = {**_summary(row, days), "cfg": cfg}
    registered = satdates.registration(cfg["exam_date"], cfg["exam_date"] if cfg.get("booked") else None,
                                       today(tz))
    if registered and not cfg.get("booked"):
        banners.append({"kind": "registration", "date": cfg["exam_date"], "data": registered})
    if suggest:
        old_needs = verdict["math"]["needs_per_week"]
        new_needs = round((min(cfg["target"], 780) - suggest["current"]) /
                          max(1 / 7, (exam - today(tz)).days / 7), 1)
        suggest["preview"] = f"Start from {suggest['current']} · needs +{new_needs} a week instead of +{old_needs}"
        banners.append({"kind": "drift", "suggest": suggest})
    out = {"active": active, "plans": [_summary(p, days if p["id"] == row["id"] else None) for p in plans],
           "draft": _json(draft["plan_draft"], None) if draft else None, "bank": _bank(learner),
           "score": {"math": {"start": cfg["current"], "target": cfg["target"], "sittings": _sittings(learner)},
                     "rw": {"start": cfg.get("rw_current"), "target": cfg.get("rw_target"),
                            "sittings": [dict(r) for r in db.rows("SELECT day,rw,source FROM outside_scores WHERE learner=? AND rw IS NOT NULL ORDER BY day", learner)]},
                     "total": {"start": (cfg["current"] or 0) + (cfg.get("rw_current") or 0),
                               "target": cfg["target"] + (cfg.get("rw_target") or 0)}},
           "sittings": _sittings(learner), "days": days, "weeks": _week_days(days),
           "today": current, "stats": stats, "domains": domains, "skills": skills,
           "rw_domains": rw_domains(learner, cfg, days),
           "gaps": {}, "phases": PHASES, "pace": {"math": pace}, "suggest": suggest, "behind": behind,
           "state": state, "points": {"math": _points(learner, row)},
           "projection": {"math": estimate.projection(learner, cfg["exam_date"])},
           "coverage": _coverage(learner, cfg, days, _gate(learner, cfg, row["id"])),
           "map": {"on": sum(progress.board(learner)[t]["answered"] < 6 for t in TOPICS) > 5,
                   "measured": sum(progress.board(learner)[t]["answered"] >= 6 for t in TOPICS),
                   "of": 19, "done_at": None},
           "changes": _changes(row, local), "checks": checks_of(learner, row),
           "focus_history": [dict(e) for e in db.rows("SELECT at,text,from_v,to_v FROM plan_events"
                                                      " WHERE plan=? AND kind='auto' AND field='skills' ORDER BY id DESC",
                                                      row["id"])],
           "habits": [], "banners": banners, "rhythm": rhythm_of(learner, tz),
           "verdict": verdict, "levers": levers, "workload": workload,
           "bought": progress_extra["bought"], "causes": progress_extra["causes"],
           "calibration": progress_extra["calibration"], "skill_pace": progress_extra["skill_pace"],
           "split_domain": progress_extra["split_domain"],
           "changes_counts": progress_extra["changes_counts"], "checkpoints": checkpoints_of(learner, row)}
    if shared:
        out.pop("draft", None)
        out.pop("proposal", None)
        out["active"]["name"] = row["name"] if db.one("SELECT name FROM learners WHERE id=?", learner)["name"] else None
        for day in out["days"]:
            for task in day["tasks"]:
                task.pop("start", None)
        if out["today"]:
            for task in out["today"]["tasks"]:
                task.pop("start", None)
    return out


def mirror(learner: str, fields: dict) -> None:
    """PUT /api/me invokes this inside its transaction after writing learners."""
    row = active_row(learner)
    if not row:
        return
    freeze(learner, row)
    cfg = cfg_of(row)
    mapped = {"rw_now": "rw_current", "rw_target": "rw_target"}
    for key, value in fields.items():
        target = mapped.get(key, key)
        if target in cfg:
            cfg[target] = value
    cfg = validate(cfg, learner, row["tz"] or 0, cfg_of(row))
    db.run("UPDATE plans SET cfg=?,updated=? WHERE id=?", json.dumps(cfg), deps.now(), row["id"])
    event(row["id"], "edit", "Goals updated from Me", field="goals", after=fields)


def today_summary(learner: str, tz: int = 0) -> dict | None:
    row = active_row(learner)
    if not row:
        return None
    freeze(learner, row, tz)
    date = today(tz)
    if not row["start"] <= date.isoformat() <= cfg_of(row)["exam_date"]:
        return None
    day = day_view(learner, row, date)
    if not db.one("SELECT 1 FROM plan_snapshots WHERE plan=? AND made_on=?", row["id"], date.isoformat()):
        last = min(date + dt.timedelta(days=13), dt.date.fromisoformat(cfg_of(row)["exam_date"]))
        allocation = allocate(learner, cfg_of(row), dt.date.fromisoformat(row["start"]), last, row["id"])
        pins = pin_schedule(learner, cfg_of(row), dt.date.fromisoformat(row["start"]),
                            dt.date.fromisoformat(cfg_of(row)["exam_date"]), row["id"])
        snapshot(learner, row, [day_view(learner, row, date + dt.timedelta(days=n), allocated=allocation, pins=pins)
                                for n in range((last - date).days + 1)])
    counted = [t for t in day["tasks"] if t.get("counted")]
    next_task = next((t for t in counted if t["status"] not in ("done", "marked", "made_up", "skipped", "moved")), None)
    return {"id": row["id"], "day": date.isoformat(), "tasks": day["tasks"],
            "tasks_done": day["tasks_done"], "tasks_counted": len(counted),
            "minutes_left": max(0, day["minutes"] - day["minutes_done"]),
            "next": next_task, "status": day["status"], "start": next_task["start"] if next_task else None}


def shell_part(learner: str, tz: int = 0) -> dict | None:
    summary = today_summary(learner, tz)
    if not summary:
        return None
    return {"plan": {"id": summary["id"], "day": summary["day"], "done": summary["tasks_done"],
                     "total": summary["tasks_counted"], "minutes_left": summary["minutes_left"],
                     "next": summary["next"]["title"] if summary["next"] else None}}


def _ics_escape(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")


def calendar(learner: str, row, tz: int | None = None) -> str:
    cfg = cfg_of(row)
    start = max(dt.date.fromisoformat(row["start"]), today(row["tz"] if tz is None else tz))
    exam = dt.date.fromisoformat(cfg["exam_date"])
    allocation = allocate(learner, cfg, dt.date.fromisoformat(row["start"]), exam, row["id"])
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//SAT Freshman//Study Plan//EN",
             "CALSCALE:GREGORIAN"]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for n in range(max(0, (exam - start).days + 1)):
        day = start + dt.timedelta(days=n)
        kind, test, minutes = kind_of(cfg, dt.date.fromisoformat(row["start"]), day,
                                      _override(row["id"], day), lambda d: _override(row["id"], d))
        if kind not in ("practice", "test"):
            continue
        rehearsal = day in _rehearsal_dates(cfg, dt.date.fromisoformat(row["start"]))
        hh, mm = map(int, (cfg["rehearsal_at"] if rehearsal else cfg.get("time") or "18:00").split(":"))
        begin = dt.datetime.combine(day, dt.time(hh, mm))
        end = begin + dt.timedelta(minutes=90 if rehearsal else minutes)
        topics = allocation.get(day.isoformat(), [])
        summary = "SAT Math · Dress rehearsal" if rehearsal else f"SAT Math · {test.title()} test" if test else f"SAT Math · {minutes} min · {', '.join(topics)}"
        lines += ["BEGIN:VEVENT", f"UID:plan-{row['id']}-{day.isoformat()}@satfreshman",
                  f"DTSTAMP:{stamp}", f"DTSTART:{begin:%Y%m%dT%H%M%S}",
                  f"DTEND:{end:%Y%m%dT%H%M%S}", f"SUMMARY:{_ics_escape(summary)}"]
        if cfg.get("place"):
            lines.append(f"LOCATION:{_ics_escape(cfg['place'])}")
        lines += ["BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:SAT study time",
                  "TRIGGER:-PT10M", "END:VALARM", "END:VEVENT"]
    for day, label in ((exam - dt.timedelta(days=1), "Rest before the SAT"), (exam, "SAT")):
        if day >= start:
            lines += ["BEGIN:VEVENT", f"UID:plan-{row['id']}-{day.isoformat()}@satfreshman",
                      f"DTSTAMP:{stamp}", f"DTSTART;VALUE=DATE:{day:%Y%m%d}",
                      f"DTEND;VALUE=DATE:{(day + dt.timedelta(days=1)):%Y%m%d}",
                      f"SUMMARY:{label}", "END:VEVENT"]
    return "\r\n".join([*lines, "END:VCALENDAR", ""])


def _selfcheck() -> None:
    cfg = {"exam_date": "2026-11-07", "days": "1111100", "minutes": 45,
           "day_minutes": None, "off": [], "tests": "weekly", "test_size": "module",
           "test_day": None, "clock": "auto", "target": 700}
    start = dt.date(2026, 9, 25)
    assert kind_of(cfg, start, dt.date(2026, 11, 7))[0] == "exam"
    assert kind_of(cfg, start, dt.date(2026, 11, 6))[0] == "eve"
    assert kind_of(cfg, start, dt.date(2026, 11, 5))[0] == "practice"
    assert kind_of(cfg, start, dt.date(2026, 11, 2))[0] == "practice"
    assert kind_of(cfg, start, dt.date(2026, 10, 3))[0] == "rest"
    assert kind_of(cfg, start, dt.date(2026, 10, 31))[:2] == ("test", "section")
    assert len(_rehearsal_dates(cfg, start)) == 1
    assert _base_minutes(cfg, dt.date(2026, 11, 5), start) == 27
    assert all(kind_of(cfg, start, d)[0] != "test" for d in _taper_dates(cfg))
    assert kind_of({**cfg, "minutes": 45, "test_size": "section"}, start, dt.date(2026, 10, 2))[1] == "module"
    assert abs(sum(progress.BLUEPRINT.values()) - 1) < 1e-9
    print("plan core self-check passed")


if __name__ == "__main__":
    _selfcheck()
