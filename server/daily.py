"""The day's question and the day's challenge: the same for every student.

Both are made from the date alone, so nobody has to set them and two students
anywhere get the identical question -- the one thing an infinite bank cannot
give by accident, and the thing a leaderboard needs to be fair.

The challenge is built once and stored. The builder's choices depend on its
survey of the bank, and a set that could change under a student mid-morning
would make the board meaningless.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json

from . import blueprint, db, practice

CHALLENGE_SIZE = 10
# the section's weights, rounded to ten questions
MIX = {"Algebra": 3, "Advanced Math": 3,
       "Problem-Solving and Data Analysis": 2, "Geometry and Trigonometry": 2}
LADDER = ["easy"] * 3 + ["medium"] * 4 + ["hard"] * 3
SPR_AT = (4, 8)             # two grid-ins, as a module carries about a quarter


def today(tz: int = 0) -> str:
    """The student's own date. tz is JavaScript's getTimezoneOffset(), minutes
    behind UTC. Everyone on the same calendar day gets the same question, which
    is what "of the day" means to the person reading it."""
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date().isoformat()


def _hash(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest(), 16)


def question(day: str) -> dict:
    """The question of the day, as stored (key included). Multiple choice,
    because it is answered with one tap on the home page."""
    names = sorted(n for v in practice.catalogue()["by_topic"].values() for n in v)
    can = blueprint.abilities()
    pool = [n for n in names if any(f == "mcq" for _, f in can.get(n, ()))]
    h = _hash(f"qotd:{day}")
    for k in range(200):
        template = pool[(h + k * 7919) % len(pool)]
        seed = (h >> 20) % 100_000 + k
        try:
            item = practice.generate(template, seed)
        except Exception:
            continue
        if item.fmt != "mcq":
            continue
        q = practice.to_question(practice.Card.of(template, seed, item, practice.topic_of(template)), 1)
        q["id"] = "qotd"
        return q
    raise RuntimeError(f"no question of the day for {day}")


def challenge(day: str) -> list[dict]:
    """The day's ten, built the first time anyone asks and kept."""
    row = db.one("SELECT questions FROM challenges WHERE day=?", day)
    if row:
        return json.loads(row["questions"])
    spread = blueprint.spread(dict(MIX))
    slots = [(dom, tier, "spr" if i + 1 in SPR_AT else None)
             for i, (dom, tier) in enumerate(zip(spread, LADDER))]
    b = practice.Builder(f"challenge:{day}", set(), set())
    cards = blueprint.fill(slots, blueprint.by_domain(), b, blueprint.abilities(),
                           log=lambda *_: None)
    qs = []
    for i, c in enumerate(cards, 1):
        q = practice.to_question(c, i)
        q["id"] = f"c{i:02d}"
        qs.append(q)
    db.run("INSERT OR IGNORE INTO challenges (day, questions, built) VALUES (?,?,?)",
           day, json.dumps(qs, ensure_ascii=False),
           dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
    return json.loads(db.one("SELECT questions FROM challenges WHERE day=?", day)["questions"])


def handle(learner: str | None, name: str | None) -> str:
    """What the board calls someone who has not chosen a name."""
    if name:
        return name
    return "Student " + hashlib.sha1((learner or "").encode()).hexdigest()[:4].upper()


def board(day: str, me: str | None = None, limit: int = 100) -> dict:
    """Right answers first, then time, then who finished first."""
    got = db.rows(
        "SELECT s.learner, s.started, s.finished, s.result, l.name FROM sessions s"
        " LEFT JOIN learners l ON l.id = s.learner"
        " WHERE s.kind='challenge' AND s.day=? AND s.finished IS NOT NULL", day)
    entries = []
    for r in got:
        res = json.loads(r["result"] or "{}")
        secs = (dt.datetime.fromisoformat(r["finished"]) - dt.datetime.fromisoformat(r["started"])).total_seconds()
        entries.append({"name": handle(r["learner"], r["name"]), "right": res.get("right", 0),
                        "asked": res.get("asked", CHALLENGE_SIZE), "seconds": int(secs),
                        "you": r["learner"] == me, "finished": r["finished"]})
    entries.sort(key=lambda e: (-e["right"], e["seconds"], e["finished"]))
    for i, e in enumerate(entries, 1):
        e["rank"] = i
    mine = next((e for e in entries if e["you"]), None)
    top = entries[:limit]
    if mine and mine not in top:
        top.append(mine)
    for e in top:
        e.pop("finished", None)
    return {"day": day, "players": len(entries), "entries": top, "you": mine}
