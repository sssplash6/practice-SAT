"""The day's challenge: the same ten for every student, and the board.

Made from the date alone, like the question of the day (daily.py), so two
students anywhere sit the identical ten -- the thing a leaderboard needs to
be fair. It is built once and stored: the builder's choices depend on its
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
BOARD_RIGHT = "COALESCE(CAST(json_extract(result,'$.right') AS INTEGER),0)"
BOARD_SECONDS = "CAST(strftime('%s',finished) AS INTEGER)-CAST(strftime('%s',started) AS INTEGER)"
BOARD_ORDER = f"{BOARD_RIGHT} DESC,{BOARD_SECONDS},finished,id"
BOARD_ORDER_QUERY = f"{BOARD_RIGHT} DESC,{BOARD_SECONDS},s.finished,s.id"


def init() -> None:
    db.run("CREATE INDEX IF NOT EXISTS sessions_challenge_board ON sessions("
           f"day,{BOARD_RIGHT} DESC,{BOARD_SECONDS},finished,id) "
           "WHERE kind='challenge' AND finished IS NOT NULL")


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
    where = "kind='challenge' AND day=? AND finished IS NOT NULL"
    players = db.one(f"SELECT COUNT(*) n FROM sessions WHERE {where}", day)["n"]
    select = ("SELECT s.id,s.learner,s.result,s.finished,l.name,"
              f"{BOARD_RIGHT} AS right,{BOARD_SECONDS} AS seconds FROM sessions s"
              " LEFT JOIN learners l ON l.id=s.learner"
              " WHERE s.kind='challenge' AND s.day=? AND s.finished IS NOT NULL")

    def entry(row, rank: int) -> dict:
        result = json.loads(row["result"] or "{}")
        return {"name": handle(row["learner"], row["name"]), "right": row["right"],
                "asked": result.get("asked", CHALLENGE_SIZE), "seconds": row["seconds"],
                "you": row["learner"] == me, "rank": rank}

    top = [entry(r, i) for i, r in enumerate(db.rows(
        select + f" ORDER BY {BOARD_ORDER_QUERY} LIMIT ?", day, max(1, min(limit, 100))), 1)]
    mine = next((e for e in top if e["you"]), None)
    if me and mine is None:
        row = db.one(select + f" AND s.learner=? ORDER BY {BOARD_ORDER_QUERY} LIMIT 1", day, me)
        if row:
            right, seconds, finished, sid = row["right"], row["seconds"], row["finished"], row["id"]
            ahead = db.one(f"SELECT COUNT(*) n FROM sessions WHERE {where} AND ("
                           f"{BOARD_RIGHT}>? OR ({BOARD_RIGHT}=? AND {BOARD_SECONDS}<?) OR "
                           f"({BOARD_RIGHT}=? AND {BOARD_SECONDS}=? AND finished<?) OR "
                           f"({BOARD_RIGHT}=? AND {BOARD_SECONDS}=? AND finished=? AND id<?))",
                           day, right, right, seconds, right, seconds, finished,
                           right, seconds, finished, sid)["n"]
            mine = entry(row, ahead + 1)
            top.append(mine)
    return {"day": day, "players": players, "entries": top, "you": mine}
