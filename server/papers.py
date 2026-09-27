"""Papers: the shared forms on /tests/ (X20), their question boards (X21) and
their discussion.

A paper is a slot list, never stems: `{sections:[{subject, module1,
module2_lower, module2_upper}]}` of [template, tier, fmt]. Everyone who sits
paper #3 gets the same question type, tier and format in every slot, each with
their own numbers (blueprint.twin_slots), so Sat by, the rating and the
percentile compare while answers can't be passed around.

* #1-#7 are the launch set, from server/mocks.json's seven shelf sections.
* One paper a week, built the first time anyone asks on or after Monday 00:00
  UTC, from blueprint.fill(order='shuffle') on a Builder seeded paper:{week}.
* A Compete Season Final joins the shelf when it closes, as a Road-to paper
  whose crowd starts with the Final's ranked sittings.

The routes are mounted by api_tests (app.py lists no router for this module).
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import statistics
import time
from collections import Counter, defaultdict

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from . import blueprint, db, deps, practice, scoring
from .deps import learner_of, now, writer_of

router = APIRouter()

MOCKS_PATH = pathlib.Path(__file__).resolve().parent / "mocks.json"
FORMS = ("module1", "module2_lower", "module2_upper")
SLOT_PREFIX = {"module1": "m1", "module2_lower": "m2l", "module2_upper": "m2u"}
CROWD_N = 20            # R16's one threshold: a paper's own crowd, percentiles, measured ratings
AVERAGE_N = 5           # an average shows from 5 first sittings (ranked-only from 20)
SHARE_N = 5             # no crowd share below this, so one other sitter's pick can't be read off
TYPICAL = 0.05          # measured rating: within +-0.05 of the shelf's mean share is Typical
POSTS_A_DAY = 20
EDIT_SECONDS = 15 * 60
HIDE_AT = 3             # reports from different codes that hide a post
TEXT_MAX = 500
ABOUT_OK = re.compile(r"^m(1|2u|2l):([1-9]|1\d|2[0-2])$")
CROWD_TTL = 600         # the board's crowd part, per paper, in seconds
FIRSTS_TTL = 300        # each paper's first sittings; a paper sitting's hand-in forgets its paper
_CROWD: dict[int, tuple[float, dict]] = {}
_FIRSTS: dict[int, tuple[float, tuple[dict, dict]]] = {}


def _json(text, default=None):
    try:
        return json.loads(text) if text else default
    except (TypeError, ValueError):
        return default


def week_of(day: dt.date) -> str:
    y, w, _ = day.isocalendar()
    return f"{y}-W{w:02d}"


def _utc_today() -> dt.date:
    return dt.datetime.now(dt.timezone.utc).date()


# ------------------------------------------------------------------ building

def init() -> None:
    launch()
    ensure()


def _slots(questions: list[dict]) -> list[list]:
    return [[q["key"], q["difficulty"], q.get("type") or "mcq"] for q in questions]


def launch() -> None:
    """Papers #1-#7 from the seven shelf sections, once."""
    if not MOCKS_PATH.exists():
        return
    mocks = sorted(json.loads(MOCKS_PATH.read_text())["mocks"], key=lambda m: m["id"])
    for n, m in enumerate(mocks, 1):
        section = {"subject": "math", **{f: _slots(m[f]) for f in FORMS}}
        db.run("INSERT OR IGNORE INTO papers(n,week,label,built,questions,source) VALUES (?,?,?,?,?,?)",
               n, None, "Launch set", now(), json.dumps({"sections": [section]}), "launch")


def _build(salt: str) -> dict:
    b = practice.Builder(salt, set(), set(), dedupe="question")
    section = {"subject": "math"}
    for form in FORMS:
        cards = blueprint.fill(blueprint.slots(form, blueprint.module_of(form)), blueprint.by_domain(), b,
                               blueprint.abilities(), log=lambda *_: None, order="shuffle")
        section[form] = [[c.key, c.item.difficulty, c.item.fmt] for c in cards]
    return {"sections": [section]}


def ensure(day: dt.date | None = None) -> int:
    """This ISO week's paper, built the first time anyone asks (as the daily
    challenge is), and every Season Final that has closed since. Returns n."""
    day = day or _utc_today()
    week = week_of(day)
    row = db.one("SELECT n FROM papers WHERE week=?", week)
    if row is None:
        monday = day - dt.timedelta(days=day.weekday())
        questions = json.dumps(_build(f"paper:{week}"))
        # n is taken inside the insert and week is UNIQUE, so two first
        # requests of the week make one paper
        db.run("INSERT OR IGNORE INTO papers(n,week,label,built,questions,source)"
               " SELECT COALESCE(MAX(n),0)+1, ?, ?, ?, ?, 'weekly' FROM papers",
               week, f"Week of {monday:%b} {monday.day}", now(), questions)
        row = db.one("SELECT n FROM papers WHERE week=?", week)
    _road_to()
    return row["n"]


def _road_to() -> None:
    """X20: a closed Season Final becomes a paper of its own slots."""
    stamp = now()
    for c in db.rows("SELECT * FROM contests WHERE kind='final' AND closes<=?", stamp):
        if db.one("SELECT 1 FROM papers WHERE source=?", c["id"]):
            continue
        spec = _json(c["spec"], {}) or {}
        m2 = spec.get("slots_m2") or {}
        if not spec.get("slots") or not m2.get("lower") or not m2.get("upper"):
            continue
        date = spec.get("sat_date") or c["id"].removeprefix("final-")
        try:
            label = f"Road to {dt.date.fromisoformat(date):%b} {dt.date.fromisoformat(date).day}"
        except ValueError:
            label = "Road to the SAT"
        section = {"subject": c["subject"] if "subject" in c.keys() and c["subject"] else "math",
                   "module1": spec["slots"], "module2_lower": m2["lower"], "module2_upper": m2["upper"]}
        db.run("INSERT OR IGNORE INTO papers(n,week,label,built,questions,source)"
               " SELECT COALESCE(MAX(n),0)+1, NULL, ?, ?, ?, ? FROM papers WHERE NOT EXISTS"
               " (SELECT 1 FROM papers WHERE source=?)", label, stamp,
               json.dumps({"sections": [section]}), c["id"], c["id"])


def paper(n: int) -> dict | None:
    row = db.one("SELECT * FROM papers WHERE n=?", n)
    if row is None:
        return None
    q = _json(row["questions"], {}) or {}
    return {"n": row["n"], "week": row["week"], "label": row["label"], "built": row["built"],
            "source": row["source"] or ("weekly" if row["week"] else "launch"),
            "sections": q.get("sections") or []}


def slots(n: int, form: str) -> list[list]:
    p = paper(n)
    if p is None or not p["sections"]:
        raise HTTPException(404, f"no paper {n}")
    return p["sections"][0][form]


def all_papers() -> list[dict]:
    return [paper(r["n"]) for r in db.rows("SELECT n FROM papers ORDER BY n")]


# ------------------------------------------------------------------ sittings

def sittings(n: int) -> list:
    """Every finished, non-abandoned sitting of paper n, oldest first."""
    return db.rows(f"SELECT * FROM sessions WHERE mock_id=? AND finished IS NOT NULL AND abandoned IS NULL"
                   f" AND learner IS NOT NULL AND {db.NOT_SAMPLE} ORDER BY finished,id", f"P{n}")


def _final_sittings(p: dict) -> list:
    if not p["source"].startswith("final-"):
        return []
    return db.rows(f"SELECT * FROM sessions WHERE contest=? AND finished IS NOT NULL AND ranked=1"
                   f" AND {db.NOT_SAMPLE} ORDER BY finished,id", p["source"])


def _ranked(row) -> bool:
    from . import estimate
    return estimate._standard(row)


def _mid(row) -> float | None:
    e = (_json(row["result"], {}) or {}).get("estimate") or {}
    return (e["low"] + e["high"]) / 2 if e.get("low") is not None and e.get("high") is not None else None


def _share(row) -> float | None:
    """Share of the possible weight a sitting earned (the measured rating)."""
    res = _json(row["result"], {}) or {}
    doms = res.get("domains") or []
    possible = sum(d.get("possible", 0) for d in doms)
    return sum(d.get("earned", 0) for d in doms) / possible if possible else None


def forget(n: int) -> None:
    """A sitting of paper n was handed in: its Sat by and averages move now."""
    _FIRSTS.pop(n, None)


def firsts(p: dict) -> tuple[dict, dict]:
    """(each learner's first finished sitting, each learner's first ranked
    sitting), a Road-to paper's Final sittings counting as first sittings.
    Cached per paper, so the shelf doesn't read every sitting on each view."""
    hit = _FIRSTS.get(p["n"])
    if hit and time.monotonic() - hit[0] < FIRSTS_TTL:
        return hit[1]
    first: dict[str, object] = {}
    ranked: dict[str, object] = {}
    for row in list(_final_sittings(p)) + list(sittings(p["n"])):
        first.setdefault(row["learner"], row)
        if row["learner"] not in ranked and (row["contest"] or _ranked(row)):
            ranked[row["learner"]] = row
    _FIRSTS[p["n"]] = (time.monotonic(), (first, ranked))
    return first, ranked


def sat_by(learner: str, n: int) -> list:
    return db.rows("SELECT * FROM sessions WHERE learner=? AND mock_id=? AND abandoned IS NULL"
                   " ORDER BY started", learner, f"P{n}")


def has_sat(learner: str, p: dict) -> bool:
    if db.one("SELECT 1 FROM sessions WHERE learner=? AND mock_id=? AND finished IS NOT NULL"
              " AND abandoned IS NULL", learner, f"P{p['n']}"):
        return True
    return bool(p["source"].startswith("final-") and db.one(
        "SELECT 1 FROM sessions WHERE learner=? AND contest=? AND finished IS NOT NULL", learner, p["source"]))


# ------------------------------------------------------------------ rating (P11's odds, one model)

class Odds:
    """ratings.expected over a viewer's skill ratings, read once per request
    and never written (ratings.skill inserts on first use; a GET must not)."""

    def __init__(self, learner: str | None):
        from . import ratings
        self.r = ratings
        self.items: dict[tuple[str, str], float] = {}
        self.skills: dict[str, float] = {}
        self.source = "types"
        if learner:
            base, _ = ratings._seed_rating(learner)
            self.base = base
            for s in db.rows("SELECT topic, rating, n FROM skill_ratings WHERE learner=?", learner):
                self.skills[s["topic"]] = s["rating"]
                if s["n"] and s["n"] >= 1:
                    self.source = "you"
        else:
            self.base = 1000.0
            by: dict[str, list[float]] = defaultdict(list)
            for s in db.rows(f"SELECT topic, rating FROM skill_ratings WHERE n>=1 AND {db.NOT_SAMPLE}"):
                by[s["topic"]].append(s["rating"])
            # the crowd median per topic, 1000 where fewer than 10 learners have one
            self.skills = {t: statistics.median(v) for t, v in by.items() if len(v) >= 10}
            self.source = "predicted"

    def item(self, template: str, tier: str) -> float:
        k = (template, tier)
        if k not in self.items:
            self.items[k] = self.r.item(template, tier)[0]
        return self.items[k]

    def p(self, template: str, tier: str) -> float:
        return self.r.expected(self.item(template, tier), self.skills.get(practice.topic_of(template), self.base))

    def expect(self, slot_list: list[list]) -> float:
        return sum(self.p(t, tier) for t, tier, *_ in slot_list)


def _chip(value: float, typical: float) -> str:
    if value <= typical - 1:
        return "harder"
    if value >= typical + 1:
        return "easier"
    return "about"


def ratings_for(learner: str, papers: list[dict]) -> dict[int, dict]:
    """{n: {you, everyone}} over the shelf, so 'most papers' is this shelf."""
    you, crowd = Odds(learner), Odds(None)
    rows = {}
    for p in papers:
        s = p["sections"][0]
        m1 = you.expect(s["module1"])
        m2 = you.expect(s["module2_upper"] if m1 >= 14 else s["module2_lower"])
        rows[p["n"]] = {"m1": m1, "m2": m2, "everyone": crowd.expect(s["module1"])}
    typical = statistics.median(r["m1"] for r in rows.values()) if rows else 0.0
    shelf = statistics.median(r["everyone"] for r in rows.values()) if rows else 0.0
    measured: dict[int, tuple[float, int]] = {}
    for p in papers:
        _, ranked = firsts(p)
        shares = [x for x in (_share(r) for r in ranked.values()) if x is not None]
        if len(shares) >= CROWD_N:
            measured[p["n"]] = (statistics.mean(shares), len(shares))
    shelf_share = statistics.mean(v for v, _ in measured.values()) if measured else None
    out = {}
    for p in papers:
        r = rows[p["n"]]
        if p["n"] in measured:
            share, n = measured[p["n"]]
            label = ("typical" if abs(share - shelf_share) <= TYPICAL else
                     "harder" if share < shelf_share else "easier")
            everyone = {"source": "measured", "label": label, "n": n, "share": round(share, 3)}
        else:
            label = {"harder": "harder", "easier": "easier", "about": "typical"}[_chip(r["everyone"], shelf)]
            everyone = {"source": "predicted", "label": label, "n": 0, "expect_m1": round(r["everyone"], 1)}
        out[p["n"]] = {"you": {"expect_m1": round(r["m1"], 1), "expect_m2": round(r["m2"], 1),
                               "typical_m1": round(typical, 1), "chip": _chip(r["m1"], typical),
                               "source": you.source},
                       "everyone": everyone}
    return out


# ------------------------------------------------------------------ the shelf's cards

def _met_under_clock(learner: str) -> set[str]:
    return {r["template"] for r in db.rows(
        "SELECT DISTINCT a.template FROM attempts AS a JOIN sessions AS s ON s.id=a.session"
        " WHERE a.learner=? AND s.kind IN ('mock','module','custom','diagnostic')", learner)}


def card(p: dict, learner: str, rating: dict, met: set[str], seen: set[str], open_t: set[str]) -> dict:
    first, ranked = firsts(p)
    mids = [m for m in (_mid(r) for r in ranked.values()) if m is not None]
    any_mids = [m for m in (_mid(r) for r in first.values()) if m is not None]
    if len(mids) >= CROWD_N:
        average = {"value": int(round(statistics.mean(mids) / 10) * 10), "n": len(mids), "basis": "ranked"}
    elif len(any_mids) >= AVERAGE_N:
        average = {"value": int(round(statistics.mean(any_mids) / 10) * 10), "n": len(any_mids),
                   "basis": "sittings"}
    else:
        average = None
    mine = sat_by(learner, p["n"])
    done = [r for r in mine if r["finished"]]
    live = [r for r in mine if not r["finished"]]
    my_first = ranked.get(learner)
    pct = None
    if my_first is not None and len(mids) >= CROWD_N and _mid(my_first) is not None:
        me = _mid(my_first)
        pct = round(100 * sum(m <= me for m in mids) / len(mids))
    s = p["sections"][0]
    templates = [t for form in FORMS for t, *_ in s[form]]
    status = "completed" if done else "in_progress" if live else "not_sat"
    misses_to_fix, hardest = 0, None
    if done:
        mine_q, ans = _slot_questions(done[0]), _json(done[0]["answers"], {}) or {}
        misses_to_fix = sum(q.get("key") in open_t and not scoring.is_correct(q, ans.get(q["id"]))
                            for q in mine_q.values())
        hardest = _hardest(p, mine_q, ans)
    posts = db.one("SELECT COUNT(*) AS n FROM posts WHERE paper=? AND hidden=0", p["n"])["n"]
    return {"n": p["n"], "label": p["label"], "week": p["week"], "source": p["source"],
            "kind": ("road_to" if p["source"].startswith("final-") else p["source"]),
            "subject": s.get("subject", "math"), "built": p["built"],
            "sat_by": len(first), "ranked_n": len(ranked), "average": average,
            "hist": sorted(round(m) for m in mids) if len(mids) >= CROWD_N else None,
            "rating": rating,
            "yours": {"status": status, "sittings": len(done),
                      "last": _mid(done[-1]) if done else None, "last_session": done[-1]["id"] if done else None,
                      "live_session": live[-1]["id"] if live else None, "first_percentile": pct,
                      "misses_to_fix": misses_to_fix},
            "hardest": hardest,
            "types_new": len({t for t in templates if t not in met}),
            "new_to_you": len({t for t in templates if t not in seen}),
            "open_traps": sum(t in open_t for t in templates),
            "posts": posts, "questions": sum(len(s[f]) for f in ("module1", "module2_upper")),
            "gated": not done}


def _hardest(p: dict, mine_q: dict[str, dict], ans: dict) -> dict | None:
    """X20's "Hardest: M2 harder Q19 · 18% right · you got it", over the slots
    you sat, from this paper's first ranked sittings or site-wide (n >= 5)."""
    c = _crowd(p)
    s = p["sections"][0]
    best = None
    for form in FORMS:
        tag = SLOT_PREFIX[form]
        for i, (t, tier, *_) in enumerate(s[form], 1):
            slot = f"{tag}:{i}"
            q = mine_q.get(slot)
            d = (c["per"].get(slot) if c["own"] else None) or c["site"].get((t, tier))
            if q is None or not d or d["n"] < SHARE_N:
                continue
            share = d["right"] / d["n"]
            if best is None or share < best["right"]:
                given = ans.get(q["id"])
                best = {"slot": slot, "module": tag, "position": i, "right": round(share, 3), "n": d["n"],
                        "source": "paper" if c["own"] else "site",
                        "you": "blank" if given in (None, "") else "right" if scoring.is_correct(q, given) else "wrong"}
    return best


def listing(learner: str) -> list[dict]:
    """Every paper, newest first, with its stats for this viewer."""
    ensure()
    papers = all_papers()
    rating = ratings_for(learner, papers)
    met = _met_under_clock(learner)
    seen = {r["template"] for r in db.rows("SELECT DISTINCT template FROM practice_seen WHERE learner=?", learner)}
    open_t = {r["template"] for r in db.rows("SELECT template FROM traps WHERE learner=? AND closed IS NULL", learner)}
    newest = max((p["n"] for p in papers if p["week"]), default=None)
    out = []
    for p in sorted(papers, key=lambda p: -p["n"]):
        c = card(p, learner, rating[p["n"]], met, seen, open_t)
        c["newest"] = p["n"] == newest
        out.append(c)
    return out


# ------------------------------------------------------------------ the question board (X21)

def _slot_questions(row) -> dict[str, dict]:
    """{'m1:17': question} for one sitting, key included."""
    built = _json(row["questions"], {}) or {}
    if not isinstance(built, dict):
        return {}
    out = {}
    for i, q in enumerate(built.get("module1") or [], 1):
        out[f"m1:{i}"] = q
    tag = "m2u" if row["route"] == "upper" else "m2l"
    for i, q in enumerate(built.get("module2") or [], 1):
        out[f"{tag}:{i}"] = q
    return out


def _norm_of(q: dict, given) -> str | None:
    from . import progress
    if given in (None, "") or scoring.is_correct(q, given):
        return None
    if q.get("type") == "mcq" and isinstance(given, int) and 0 <= given < len(q.get("reasons") or []):
        return progress.norm(q["reasons"][given] or "") or None
    for reason, value in q.get("spr_reasons") or []:
        if scoring.normalise(str(value)) == scoring.normalise(str(given)):
            return progress.norm(reason) or None
    return None


def _labels() -> dict[str, str]:
    """The latest reason text for each norm (SQLite takes the bare column
    from the MAX(id) row)."""
    return {r["norm"]: r["reason"] for r in db.rows(
        "SELECT norm, reason, MAX(id) FROM attempts WHERE norm IS NOT NULL AND norm!=''"
        " AND reason IS NOT NULL GROUP BY norm")}


def _crowd(p: dict) -> dict:
    """The part of the board that doesn't depend on the viewer, cached."""
    hit = _CROWD.get(p["n"])
    if hit and time.monotonic() - hit[0] < CROWD_TTL:
        return hit[1]
    _, ranked = firsts(p)
    own = len(ranked) >= CROWD_N
    s = p["sections"][0]
    per: dict[str, dict] = {}
    if own:
        for row in ranked.values():
            answers = _json(row["answers"], {}) or {}
            qstate = _json(row["qstate"], {}) or {}
            for slot, q in _slot_questions(row).items():
                d = per.setdefault(slot, {"n": 0, "right": 0, "norms": Counter(), "ms": [], "given": Counter()})
                given = answers.get(q["id"])
                d["n"] += 1
                if scoring.is_correct(q, given):
                    d["right"] += 1
                    ms = (qstate.get(q["id"]) or {}).get("ms")
                    if ms:
                        d["ms"].append(ms)
                else:
                    norm = _norm_of(q, given)
                    if norm:
                        d["norms"][norm] += 1
                    if q.get("type") == "spr" and given not in (None, ""):
                        d["given"][str(given)] += 1
    site: dict[tuple[str, str], dict] = {}
    pairs = {(t, tier) for form in FORMS for t, tier, *_ in s[form]}
    for t, tier in pairs:
        rows = db.rows(f"SELECT a.correct, a.norm, a.given, a.fmt, COALESCE(a.ms, a.sms) AS ms, s.kind, s.cfg"
                       f" FROM attempts AS a"
                       f" LEFT JOIN sessions AS s ON s.id=a.session WHERE a.template=? AND a.difficulty=?"
                       f" AND a.repeat=0 AND a.disputed=0 AND a.void IS NULL AND a.{db.NOT_SAMPLE}", t, tier)
        timed = [r["ms"] for r in rows if r["correct"] and r["ms"] and (
            r["kind"] in ("mock", "module", "custom", "diagnostic") or '"timed": true' in (r["cfg"] or ""))]
        site[(t, tier)] = {"n": len(rows), "right": sum(r["correct"] for r in rows),
                           "norms": Counter(r["norm"] for r in rows if not r["correct"] and r["norm"]),
                           "ms": timed,
                           "given": Counter(str(r["given"]) for r in rows if not r["correct"] and r["fmt"] == "spr"
                                            and r["given"] not in (None, ""))}
    out = {"own": own, "n_first": len(ranked), "per": per, "site": site, "labels": _labels()}
    _CROWD[p["n"]] = (time.monotonic(), out)
    return out


def _designed(template: str, tier: str, fmt: str, q: dict | None) -> list[str]:
    """The misconceptions a slot's options are built to catch (labels only)."""
    if q is None:
        for seed in range(12):
            try:
                it = practice.generate(template, seed)
            except Exception:
                continue
            if it.difficulty == tier and it.fmt == fmt:
                q = {"reasons": list(it.reasons), "spr_reasons": practice.spr_reasons(template, seed, it)}
                break
    if q is None:
        return []
    labels = [r for r in (q.get("reasons") or []) if r]
    labels += [r for r, _ in (q.get("spr_reasons") or []) if r]
    return list(dict.fromkeys(labels))[:3]


def crowd(n: int, learner: str) -> dict:
    p = paper(n)
    if p is None:
        raise HTTPException(404, f"no paper {n}")
    posts = db.one("SELECT COUNT(*) AS n FROM posts WHERE paper=? AND hidden=0", n)["n"]
    if not has_sat(learner, p):
        return {"gated": True, "count": posts}
    from . import progress
    c = _crowd(p)
    labels = c["labels"]
    s = p["sections"][0]
    mine = [r for r in sat_by(learner, n) if r["finished"]]
    my = mine[0] if mine else None
    my_q = _slot_questions(my) if my else {}
    my_ans = _json(my["answers"], {}) if my else {}
    my_state = _json(my["qstate"], {}) if my else {}
    my_route = my["route"] if my else None
    about = Counter(r["about"] for r in db.rows("SELECT about FROM posts WHERE paper=? AND hidden=0"
                                                 " AND about IS NOT NULL", n))
    rows, trap_pool = [], Counter()
    for form in FORMS:
        tag = SLOT_PREFIX[form]
        for i, (t, tier, fmt, *_) in enumerate(s[form], 1):
            slot = f"{tag}:{i}"
            data = c["per"].get(slot) if c["own"] else None
            src = "paper" if data else "site"
            d = data or c["site"].get((t, tier)) or {"n": 0, "right": 0, "norms": Counter(), "ms": [],
                                                     "given": Counter()}
            wrong = d["n"] - d["right"]
            spread = ([{"norm": k, "label": labels.get(k, k), "share": round(v / d["n"], 3)}
                       for k, v in d["norms"].most_common(4)] if d["n"] >= SHARE_N else [])
            q = my_q.get(slot)
            you = None
            if q is not None:
                given = my_ans.get(q["id"])
                you = {"state": "blank" if given in (None, "") else
                       "right" if scoring.is_correct(q, given) else "wrong",
                       "ms": (my_state.get(q["id"]) or {}).get("ms"), "q": f"{tag.upper()}-{i}"}
            top = db.one("SELECT text FROM posts WHERE paper=? AND about=? AND hidden=0 AND parent IS NULL"
                         " ORDER BY helpful DESC, at LIMIT 1", n, slot)
            topic = practice.topic_of(t)
            names = progress.topics()
            row = {"slot": slot, "module": tag, "position": i, "topic": topic,
                   "topic_name": names[topic].name if topic in names else topic, "tier": tier, "fmt": fmt,
                   "source": src, "n": d["n"], "right": round(d["right"] / d["n"], 3) if d["n"] else None,
                   "median_right_ms": int(statistics.median(d["ms"])) if d["ms"] else None,
                   "spread": spread, "designed": [] if spread else _designed(t, tier, fmt, q),
                   "spr_top": ([{"value": v, "share": round(k / d["n"], 3)} for v, k in d["given"].most_common(3)]
                               if fmt == "spr" and d["n"] >= SHARE_N else []),
                   "wrong": wrong if d["n"] >= SHARE_N else None,
                   "you": you, "on_route": tag == "m1" or my_route is None or tag == ("m2u" if my_route == "upper" else "m2l"),
                   "posts": about.get(slot, 0), "top_post": (top["text"][:120] if top else None)}
            rows.append(row)
            for x in spread:
                trap_pool[(x["norm"], x["label"])] += x["share"]
    traps = [{"norm": k[0], "label": k[1], "share": round(v, 3)} for k, v in trap_pool.most_common(3)]
    cheapest = [{"slot": r["slot"], "right": r["right"], "source": r["source"], "you": r["you"]["state"]}
                for r in rows if r["you"] and r["you"]["state"] != "right" and r["right"] is not None
                and r["right"] >= 0.8 and r["n"] >= SHARE_N]
    return {"gated": False, "subject": s.get("subject", "math"), "n": n, "label": p["label"],
            "n_first": c["n_first"], "source": "paper" if c["own"] else "site", "traps": traps,
            "cheapest": cheapest, "slots": rows, "count": posts}


# ------------------------------------------------------------------ discussion

def _post_view(r, viewer: str) -> dict:
    return {"id": r["id"], "name": r["name"], "at": r["at"], "edited": r["edited"], "parent": r["parent"],
            "about": r["about"], "text": r["text"], "helpful": r["helpful"], "hidden": bool(r["hidden"]),
            "mine": r["learner"] == viewer,
            "editable": r["learner"] == viewer and _age(r["at"]) <= EDIT_SECONDS,
            "voted": bool(db.one("SELECT 1 FROM post_votes WHERE post=? AND learner=? AND kind='helpful'",
                                 r["id"], viewer))}


def _age(at: str) -> float:
    return (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(at)).total_seconds()


def _paper_or_404(n: int) -> dict:
    p = paper(n)
    if p is None:
        raise HTTPException(404, f"no paper {n}")
    return p


@router.get("/api/papers/{n}/posts")
def get_posts(n: int, sort: str = "top", about: str | None = None,
              x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    p = _paper_or_404(n)
    count = db.one("SELECT COUNT(*) AS n FROM posts WHERE paper=? AND hidden=0", n)["n"]
    if not has_sat(learner, p):
        return {"gated": True, "count": count}
    if sort not in ("top", "new"):
        raise HTTPException(422, {"field": "sort", "reason": "top or new"})
    if about is not None and not ABOUT_OK.match(about):
        raise HTTPException(422, {"field": "about", "reason": "like m1:17 or m2u:5"})
    order = "helpful DESC, at DESC" if sort == "top" else "at DESC"
    sql = "SELECT * FROM posts WHERE paper=? AND parent IS NULL AND (hidden=0 OR learner=?)"
    args: list = [n, learner]
    if about:
        sql += " AND about=?"
        args.append(about)
    threads = []
    for r in db.rows(sql + f" ORDER BY {order} LIMIT 200", *args):
        replies = [_post_view(x, learner) for x in db.rows(
            "SELECT * FROM posts WHERE parent=? AND (hidden=0 OR learner=?) ORDER BY at", r["id"], learner)]
        threads.append({**_post_view(r, learner), "replies": replies})
    return {"gated": False, "count": count, "sort": sort, "about": about, "threads": threads}


class PostIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=TEXT_MAX)
    about: str | None = Field(default=None, max_length=8)
    parent: int | None = None


def _muted(learner: str) -> bool:
    return bool(db.one("SELECT 1 FROM kv WHERE k=?", f"mute:{learner}"))


@router.post("/api/papers/{n}/posts")
def post_post(n: int, body: PostIn, x_learner: str | None = Header(default=None)) -> dict:
    learner = writer_of(x_learner)
    p = _paper_or_404(n)
    if not has_sat(learner, p):
        raise HTTPException(403, "sit this paper first")
    text = body.text.strip()
    if not text:
        raise HTTPException(422, {"field": "text", "reason": "empty"})
    if body.about is not None and not ABOUT_OK.match(body.about):
        raise HTTPException(422, {"field": "about", "reason": "like m1:17 or m2u:5"})
    name = db.one("SELECT name FROM learners WHERE id=?", learner)
    if not name or not (name["name"] or "").strip():
        raise HTTPException(422, "set a name first")
    if body.parent is not None:
        parent = db.one("SELECT * FROM posts WHERE id=? AND paper=?", body.parent, n)
        if parent is None:
            raise HTTPException(404, "no such post")
        if parent["parent"] is not None:
            raise HTTPException(422, {"field": "parent", "reason": "reply to a top-level post"})
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).isoformat(timespec="seconds")
    with db.transaction() as c:
        if c.execute("SELECT COUNT(*) FROM posts WHERE learner=? AND at>=?", (learner, since)).fetchone()[0] >= POSTS_A_DAY:
            raise HTTPException(429, "that's 20 posts today; more tomorrow")
        cur = c.execute("INSERT INTO posts(paper,learner,name,at,parent,about,text,hidden) VALUES (?,?,?,?,?,?,?,?)",
                        (n, learner, name["name"].strip(), now(), body.parent, body.about, text,
                         int(_muted(learner))))
    return _post_view(db.one("SELECT * FROM posts WHERE id=?", cur.lastrowid), learner)


class EditIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=TEXT_MAX)


def _own_post(pid: int, learner: str):
    r = db.one("SELECT * FROM posts WHERE id=?", pid)
    if r is None:
        raise HTTPException(404, "no such post")
    if r["learner"] != learner:
        raise HTTPException(403, "only its author can change a post")
    if _age(r["at"]) > EDIT_SECONDS:
        raise HTTPException(409, "posts can be changed for 15 minutes")
    return r


@router.put("/api/posts/{pid}")
def put_post(pid: int, body: EditIn, x_learner: str | None = Header(default=None)) -> dict:
    learner = writer_of(x_learner)
    _own_post(pid, learner)
    db.run("UPDATE posts SET text=?, edited=? WHERE id=?", body.text.strip(), now(), pid)
    return _post_view(db.one("SELECT * FROM posts WHERE id=?", pid), learner)


@router.delete("/api/posts/{pid}")
def delete_post(pid: int, x_learner: str | None = Header(default=None)) -> dict:
    learner = writer_of(x_learner)
    _own_post(pid, learner)
    with db.transaction() as c:
        c.execute("DELETE FROM post_votes WHERE post IN (SELECT id FROM posts WHERE id=? OR parent=?)", (pid, pid))
        c.execute("DELETE FROM posts WHERE id=? OR parent=?", (pid, pid))
    return {"deleted": pid}


def _vote(pid: int, x_learner: str | None, kind: str) -> dict:
    learner = writer_of(x_learner)
    r = db.one("SELECT * FROM posts WHERE id=?", pid)
    if r is None:
        raise HTTPException(404, "no such post")
    p = _paper_or_404(r["paper"])
    if not has_sat(learner, p):
        raise HTTPException(403, "sit this paper first")
    if r["learner"] == learner:
        raise HTTPException(409, "that's your own post")
    col = "helpful" if kind == "helpful" else "reports"
    with db.transaction() as c:
        new = c.execute("INSERT OR IGNORE INTO post_votes(post,learner,kind) VALUES (?,?,?)",
                        (pid, learner, kind)).rowcount
        if new:
            c.execute(f"UPDATE posts SET {col}={col}+1 WHERE id=?", (pid,))
            if kind == "report":
                c.execute("UPDATE posts SET hidden=1 WHERE id=? AND reports>=?", (pid, HIDE_AT))
    r = db.one("SELECT * FROM posts WHERE id=?", pid)
    return {"id": pid, "helpful": r["helpful"], "reported": kind == "report", "hidden": bool(r["hidden"])}


@router.post("/api/posts/{pid}/helpful")
def helpful(pid: int, x_learner: str | None = Header(default=None)) -> dict:
    return _vote(pid, x_learner, "helpful")


@router.post("/api/posts/{pid}/report")
def report(pid: int, x_learner: str | None = Header(default=None)) -> dict:
    return _vote(pid, x_learner, "report")


@router.get("/api/papers/{n}/crowd")
def get_crowd(n: int, x_learner: str | None = Header(default=None)) -> dict:
    return crowd(n, learner_of(x_learner))


@router.get("/api/papers/{n}")
def get_paper(n: int, x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    p = _paper_or_404(n)
    rating = ratings_for(learner, all_papers())
    met = _met_under_clock(learner)
    seen = {r["template"] for r in db.rows("SELECT DISTINCT template FROM practice_seen WHERE learner=?", learner)}
    open_t = {r["template"] for r in db.rows("SELECT template FROM traps WHERE learner=? AND closed IS NULL", learner)}
    return card(p, learner, rating[n], met, seen, open_t)


# ------------------------------------------------------------------ moderation (tools/moderate.py)

def reported(pending_only: bool = True) -> list[dict]:
    """Posts with reports; pending = not yet hidden, restored or confirmed by
    a moderator (hidden by 3 reports or not)."""
    sql = "SELECT * FROM posts WHERE reports>0"
    if pending_only:
        sql += " AND NOT EXISTS (SELECT 1 FROM kv WHERE k='reviewed:'||posts.id)"
    return [dict(r) for r in db.rows(sql + " ORDER BY reports DESC, at")]


def hide(pid: int) -> bool:
    ok = db.run("UPDATE posts SET hidden=1 WHERE id=?", pid).rowcount > 0
    db.run("INSERT OR REPLACE INTO kv(k,v) VALUES (?,?)", f"reviewed:{pid}", now())
    return ok


def restore(pid: int) -> bool:
    ok = db.run("UPDATE posts SET hidden=0 WHERE id=?", pid).rowcount > 0
    db.run("INSERT OR REPLACE INTO kv(k,v) VALUES (?,?)", f"reviewed:{pid}", now())
    return ok


def mute(code: str, on: bool = True) -> None:
    if on:
        db.run("INSERT OR REPLACE INTO kv(k,v) VALUES (?,?)", f"mute:{code}", now())
    else:
        db.run("DELETE FROM kv WHERE k=?", f"mute:{code}")
