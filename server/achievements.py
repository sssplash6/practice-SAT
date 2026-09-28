"""The single earned-badge ladder shared by Me, Shell, Compete and Words."""

from __future__ import annotations

import datetime as dt
import json
from collections import Counter
from fastapi import HTTPException

from . import db, deps, estimate, progress


BASE = [
    ("streak", "Study streak", "Habits", (3, 7, 14, 30, 60, 100)),
    ("on_target", "On target", "Habits", (5, 20, 50, 100)),
    ("consistency", "Every planned day", "Habits", (1, 4, 8)),
    ("qotd", "Question of the day", "Habits", (7, 30, 100)),
    ("answered", "Questions answered", "Volume", (50, 100, 250, 500, 1000, 2500, 5000)),
    ("hard_right", "Hard questions right", "Volume", (10, 50, 150, 500)),
    ("hours", "Study hours", "Volume", (5, 20, 50, 100)),
    ("fixed", "Mistakes fixed", "Mistakes", (1, 10, 25, 50, 100, 250)),
    ("clean_set", "Clean sets", "Mistakes", (1, 5, 20)),
    ("never_twice", "Fixes that held", "Mistakes", (5, 25, 100)),
    ("explorer", "Question types met", "Skills", (50, 100, 200, 300, 386)),
    ("first_module", "First module", "Tests", (1,)),
    ("first_section", "First section", "Tests", (1,)),
    ("sections", "Sections completed", "Tests", (1, 5, 10)),
    ("upper_route", "Upper route", "Tests", (1, 5)),
    ("climbing", "Score climb", "Tests", (50, 100, 150, 200)),
    ("challenge", "Challenges played", "Compete", (1, 7, 30, 100)),
    ("podium", "Podium finishes", "Compete", (1, 5, 20)),
    ("first_place", "First place", "Compete", (1, 5)),
    ("perfect", "Perfect challenges", "Compete", (1, 5)),
]

# Old Compete badge ids that R25 presents through the Shell achievement ladder.
# This map is also the bridge used by Compete's Go actions (C23).
FOLDED = {
    "first-contest": ("challenge", 1), "streak-7": ("streak", 7),
    "daily-7": ("challenge", 7), "daily-30": ("challenge", 30),
    "perfect-ten": ("perfect", 1), "podium": ("podium", 1),
    "solved-1000": ("answered", 1000), "consistency": ("consistency", 1),
    "trap-hunter": ("fixed", 25),
}


def rules() -> list[dict]:
    out = [{"id": key, "name": name, "group": group, "rule": name,
            "tiers": list(tiers)} for key, name, group, tiers in BASE]
    for topic, item in progress.topics().items():
        out.append({"id": f"skill:{topic}", "name": item.name, "group": "Skills",
                    "rule": f"Reach Strong in {item.name}", "tiers": [1]})
    for domain in progress.DOMAINS:
        out.append({"id": f"domain:{domain}", "name": domain, "group": "Skills",
                    "rule": f"Reach Strong across {domain}", "tiers": [1]})
    for section in ("compete", "words"):
        module = deps.part(section, "ACHIEVEMENTS")
        for extra in module or []:
            if not any(x["id"] == extra["id"] for x in out):
                out.append({"id": extra["id"], "name": extra.get("name") or extra["id"].replace("-", " ").title(),
                            "group": section.title(), "rule": extra.get("rule") or "Keep learning",
                            "tiers": extra.get("tiers") or [extra.get("target", 1)]})
    out += [{"id": "words-collection", "name": "Collection complete", "group": "Words",
             "rule": "Know every word in a collection", "tiers": [1]},
            {"id": "words-review-streak", "name": "Seven review days", "group": "Words",
             "rule": "Review words on seven consecutive days", "tiers": [7]}]
    return out


def _counts(learner: str, tz: int) -> tuple[dict, dict]:
    days = progress.days(learner, tz, 53)
    board = progress.board(learner)
    attempted = db.one(f"SELECT COUNT(*) AS answered, SUM(correct=1 AND difficulty='hard') AS hard_right"
                       f" FROM attempts WHERE learner=? AND {progress.COUNTED}", learner)
    traps = db.one("SELECT SUM(closed IS NOT NULL) AS fixed, SUM(closed IS NOT NULL AND relapses=0"
                   " AND closed<=?) AS held FROM traps WHERE learner=?",
                   (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=14)).isoformat(), learner)
    sittings = db.rows("SELECT kind,route,result,finished,contest FROM sessions WHERE learner=?"
                       " AND finished IS NOT NULL AND abandoned IS NULL", learner)
    tests = Counter(s["kind"] for s in sittings)
    sections = sum(tests[k] for k in ("section", "mock", "paper"))
    challenge = [s for s in sittings if s["contest"] or s["kind"] == "challenge"]
    clean = sum(1 for s in sittings if (r := json.loads(s["result"] or "{}")) and
                (r.get("asked") or 0) >= 10 and r.get("right") == r.get("asked"))
    perfect = sum(1 for s in challenge if (r := json.loads(s["result"] or "{}")) and
                  (r.get("asked") or 0) >= 10 and r.get("right") == r.get("asked"))
    plan = db.one("SELECT minutes,days FROM learners WHERE id=?", learner)
    goal = plan["minutes"] if plan else None
    on_target = sum(x["minutes"] >= goal for x in days["days"] if goal and not x["rest"])
    consistency = 0
    if plan and plan["days"] and len(plan["days"]) == 7:
        per_week: dict[str, list[dict]] = {}
        for d in days["days"]:
            per_week.setdefault(dt.date.fromisoformat(d["day"]).strftime("%G-W%V"), []).append(d)
        consistency = sum(len(lines) == 7 and all(x["rest"] or x["questions"] or x["words"] or x["tests"]
                                                    for x in lines) for lines in per_week.values())
    qotd = sum(any(x["qotd"].values()) for x in days["days"])
    scored = estimate._sittings(learner)
    latest, earliest = (scored[0], scored[-1]) if scored else (None, None)
    climb = max(0, round(latest["mid"] - earliest["mid"])) if latest and earliest else 0
    podium = first_place = top_ten = 0
    contest_board = deps.part("compete", "board")
    if contest_board:
        seen_contests = {s["contest"] for s in challenge if s["contest"]}
        for cid in seen_contests:
            try:
                mine = contest_board(cid, learner, limit=1).get("you")
            except HTTPException:
                continue
            rank = mine.get("rank") if mine else None
            podium += bool(rank and rank <= 3)
            first_place += rank == 1
            top_ten += bool(rank and rank <= 10)
    legacy_board = deps.part("challenge", "board")
    if legacy_board:
        for day in {s["day"] for s in db.rows("SELECT day FROM sessions WHERE learner=?"
                                                  " AND kind='challenge' AND finished IS NOT NULL", learner)}:
            if not day:
                continue
            mine = legacy_board(day, learner, 0).get("you")
            rank = mine.get("rank") if mine else None
            podium += bool(rank and rank <= 3)
            first_place += rank == 1
            top_ten += bool(rank and rank <= 10)
    values = {"streak": days["best"], "on_target": on_target, "consistency": consistency,
              "qotd": qotd, "answered": attempted["answered"] or 0,
              "hard_right": attempted["hard_right"] or 0, "hours": days["minutes_total"] // 60,
              "fixed": traps["fixed"] or 0, "clean_set": clean, "never_twice": traps["held"] or 0,
              "explorer": progress.types_met(learner)["met"], "first_module": int(tests["module"] > 0),
              "first_section": int(sections > 0), "sections": sections,
              "upper_route": sum(s["route"] == "upper" for s in sittings),
              "climbing": climb, "challenge": len(challenge),
              "podium": podium, "first_place": first_place, "perfect": perfect,
              "top-ten": top_ten}
    for topic, item in board.items():
        values[f"skill:{topic}"] = int(item["mastery"] >= progress.STRONG)
    for domain in progress.DOMAINS:
        members = [v for v in board.values() if v["domain"] == domain]
        values[f"domain:{domain}"] = int(bool(members) and all(v["mastery"] >= progress.STRONG for v in members))
    known = db.one("SELECT COUNT(*) AS n FROM word_state WHERE learner=? AND box>=4"
                   " AND proven IS NOT NULL", learner)["n"]
    for n in (50, 250, 1000):
        values[f"words-{n}"] = known
    word_library = deps.part("words", "library")
    if word_library:
        collections = [coll for group in word_library(learner, tz)["groups"]
                       for coll in group["collections"]]
        values["words-collection"] = sum(c.get("count", 0) > 0 and
                                          c.get("known", 0) >= c["count"] for c in collections)
    reviews = {progress._local_day(r["at"], tz) for r in db.rows(
        "SELECT at FROM word_reviews WHERE learner=? AND correct IS NOT NULL"
        " AND mode NOT IN ('lookup','sort','placement','sprint','outside','order')", learner)}
    day = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date()
    if day not in reviews:
        day -= dt.timedelta(days=1)
    run = 0
    while day in reviews:
        run += 1
        day -= dt.timedelta(days=1)
    values["words-review-streak"] = run
    compete_evaluate = deps.part("compete", "evaluate")
    if compete_evaluate:
        for item in compete_evaluate(learner):
            values[item["id"]] = item["have"]
    return values, {"days": days, "board": board}


def _go(rule_id: str, learner: str) -> dict:
    compete_go = deps.part("compete", "go_for")
    if compete_go and (rule_id in {value[0] for value in FOLDED.values()} or
                       any(x["id"] == rule_id for x in (deps.part("compete", "ACHIEVEMENTS") or []))):
        origin = next((old for old, (new, _) in FOLDED.items() if new == rule_id), rule_id)
        action = compete_go(origin, learner)
        if action:
            return {"label": action.get("label") or action.get("action") or "Open Compete",
                    "href": action.get("href") or "/compete/"}
    if rule_id.startswith("skill:"):
        return {"label": "Practise this skill", "body": {"topics": [rule_id[6:]], "count": 8}}
    if rule_id == "explorer":
        return {"label": "Try new types", "body": {"pool": "untried", "count": 8}}
    if rule_id in ("fixed", "never_twice"):
        return {"label": "Fix mistakes", "body": {"pool": "redo", "count": 8}}
    if rule_id == "clean_set":
        return {"label": "Start a clean set", "body": {"count": 10}}
    if rule_id == "hard_right":
        return {"label": "Try hard questions", "body": {"tiers": ["hard"], "count": 8}}
    if rule_id.startswith("words-"):
        return {"label": "Review words", "href": "/words/"}
    if rule_id in ("challenge", "podium", "first_place", "perfect"):
        return {"label": "Open Compete", "href": "/compete/"}
    return {"label": "Answer a question", "body": {"source": "quick", "count": 1}}


def evaluate(learner: str, tz: int = 0) -> list[dict]:
    values, _ = _counts(learner, tz)
    rows = db.rows("SELECT id,tier,at FROM earned WHERE learner=?", learner)
    earned = {}
    for row in rows:
        earned.setdefault(row["id"], []).append({"tier": row["tier"], "at": row["at"]})
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)).isoformat()
    active_sql = ("SELECT learner FROM attempts WHERE at>=? UNION "
                  "SELECT learner FROM word_reviews WHERE at>=? UNION "
                  "SELECT learner FROM sessions WHERE finished>=?")
    active = db.one(f"SELECT COUNT(*) AS n FROM ({active_sql}) WHERE learner NOT LIKE 'sample:%'"
                    " AND learner NOT LIKE 'gone:%'", cutoff, cutoff, cutoff)["n"]
    rarity = {}
    if active >= 50:
        for row in db.rows(f"WITH active AS ({active_sql}) SELECT e.id,e.tier,COUNT(DISTINCT e.learner) AS n"
                           " FROM earned e JOIN active a ON a.learner=e.learner"
                           " WHERE e.learner NOT LIKE 'sample:%' AND e.learner NOT LIKE 'gone:%'"
                           " GROUP BY e.id,e.tier", cutoff, cutoff, cutoff):
            rarity[(row["id"], row["tier"])] = row["n"]
    out = []
    for rule in rules():
        key = rule["id"]
        have = max(values.get(key, 0), *(x["tier"] for x in earned.get(key, [])), 0)
        if key in ("pace-setter", "weekly-4", "level-5", "level-8", "all-rounder"):
            rule = {**rule, "tiers": [{"pace-setter": 10, "weekly-4": 4, "level-5": 5,
                                       "level-8": 8, "all-rounder": 3}[key]]}
        for tier in rule["tiers"]:
            if have >= tier and not any(x["tier"] == tier for x in earned.get(key, [])):
                at = deps.now()
                if key == "answered":
                    row = db.one(f"SELECT at FROM attempts WHERE learner=? AND {progress.COUNTED}"
                                 " ORDER BY at,id LIMIT 1 OFFSET ?", learner, tier - 1)
                    at = row["at"] if row else at
                db.run("INSERT OR IGNORE INTO earned(learner,id,tier,at) VALUES (?,?,?,?)",
                       learner, key, tier, at)
                earned.setdefault(key, []).append({"tier": tier, "at": at})
        got = sorted(earned.get(key, []), key=lambda x: x["tier"])
        next_tier = next((n for n in rule["tiers"] if n > have), None)
        rare = None
        if got and active >= 50:
            percent = round(100 * rarity.get((key, got[-1]["tier"]), 0) / active)
            rare = {"percent": percent, "label": f"Earned by {percent}%"}
        out.append({**rule, "icon": key.split(":")[0], "have": have,
                    "tier": got[-1]["tier"] if got else None, "next": next_tier,
                    "earned": got, "go": _go(key, learner) if next_tier is not None else None,
                    "rarity": rare})
    return out


def shell_part(learner: str, tz: int = 0) -> dict:
    badges = evaluate(learner, tz)
    row = db.one("SELECT ach_seen FROM learners WHERE id=?", learner)
    seen = row["ach_seen"] if row else None
    fresh = [{"id": b["id"], "tier": e["tier"], "name": b["name"]}
             for b in badges for e in b["earned"] if not seen or e["at"] > seen]
    return {"new": {"achievements": fresh}}
