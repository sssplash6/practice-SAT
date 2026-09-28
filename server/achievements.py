"""The single earned-badge ladder shared by Me, Shell, Compete and Words."""

from __future__ import annotations

import datetime as dt
import json
from collections import Counter

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
                            "tiers": [extra.get("target", 1)]})
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
    values = {"streak": days["best"], "on_target": on_target, "consistency": consistency,
              "qotd": qotd, "answered": attempted["answered"] or 0,
              "hard_right": attempted["hard_right"] or 0, "hours": days["minutes_total"] // 60,
              "fixed": traps["fixed"] or 0, "clean_set": clean, "never_twice": traps["held"] or 0,
              "explorer": progress.types_met(learner)["met"], "first_module": int(tests["module"] > 0),
              "first_section": int(sections > 0), "sections": sections,
              "upper_route": sum(s["route"] == "upper" for s in sittings),
              "climbing": climb, "challenge": len(challenge),
              "podium": 0, "first_place": 0, "perfect": perfect}
    for topic, item in board.items():
        values[f"skill:{topic}"] = int(item["mastery"] >= progress.STRONG)
    for domain in progress.DOMAINS:
        members = [v for v in board.values() if v["domain"] == domain]
        values[f"domain:{domain}"] = int(bool(members) and all(v["mastery"] >= progress.STRONG for v in members))
    known = db.one("SELECT COUNT(*) AS n FROM word_state WHERE learner=? AND box>=4", learner)["n"]
    for n in (50, 250, 1000):
        values[f"words-{n}"] = known
    compete_evaluate = deps.part("compete", "evaluate")
    if compete_evaluate:
        for item in compete_evaluate(learner):
            values[item["id"]] = item["have"]
    return values, {"days": days, "board": board}


def _go(rule_id: str) -> dict:
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
    out = []
    for rule in rules():
        key, have = rule["id"], values.get(rule["id"], 0)
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
        out.append({**rule, "icon": key.split(":")[0], "have": have,
                    "tier": got[-1]["tier"] if got else None, "next": next_tier,
                    "earned": got, "go": _go(key) if next_tier is not None else None})
    return out


def shell_part(learner: str, tz: int = 0) -> dict:
    badges = evaluate(learner, tz)
    row = db.one("SELECT ach_seen FROM learners WHERE id=?", learner)
    seen = row["ach_seen"] if row else None
    fresh = [{"id": b["id"], "tier": e["tier"], "name": b["name"]}
             for b in badges for e in b["earned"] if not seen or e["at"] > seen]
    return {"new": {"achievements": fresh}}
