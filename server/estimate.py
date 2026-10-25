"""The score model's readers (R16 and the upgrades' R48): one band summary for
Tests, Today, Plan and Results, and the two ways points are priced.

* A sitting's points come only from exact re-marking: `rescore`, `ledger`,
  `rescore_sitting`, `total`. Shown without "about".
* Practice points come only from U4's `gains` model over the answer rows:
  `gains`, `need`, `route`, `time_cost`, `practice_delta`. Its S is never shown
  as a score, only its differences.
* `projection` looks forward from the sittings; `percentile`, `national`,
  `growth` and `calibration` place a band among others.
"""

from __future__ import annotations

if __package__ in (None, ""):                     # python3 server/estimate.py
    import pathlib
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    __package__ = "server"

import datetime as dt
import itertools
import json
import math
import pathlib
import statistics
from collections import Counter, defaultdict

from . import db, deps, scoring

SECTION_KINDS = ("mock", "section", "paper")
RANK_KINDS = SECTION_KINDS + ("module", "diagnostic")
EVIDENCE = 10.0                 # U4: answers before a skill's own accuracy outweighs the learner's
MIN_ANSWERS = 30
STRONG_AT = 0.8
PERCENTILES = pathlib.Path(__file__).resolve().parent / "data" / "cb_percentiles.json"

# U4: College Board Question Bank counts per skill, the weights within a domain
SKILL_WEIGHT = {
    "linear_equations_in_one_variable": 112, "linear_functions": 170,
    "linear_equations_in_two_variables": 130, "systems_of_linear_equations": 126,
    "linear_inequalities": 77,
    "equivalent_expressions": 116, "nonlinear_equations_and_systems": 164, "nonlinear_functions": 258,
    "evaluating_statistical_claims": 12, "sample_statistics_and_margin_of_error": 28,
    "one_variable_data": 84, "percentages": 83, "probability": 49,
    "ratios_rates_proportions_and_units": 93, "two_variable_data": 71,
    "area_and_volume": 110, "circles": 67, "lines_angles_and_triangles": 102,
    "right_triangles_and_trigonometry": 69,
}
DOMAIN_OF = {
    **{t: "Algebra" for t in ("linear_equations_in_one_variable", "linear_functions",
                              "linear_equations_in_two_variables", "systems_of_linear_equations",
                              "linear_inequalities")},
    **{t: "Advanced Math" for t in ("equivalent_expressions", "nonlinear_equations_and_systems",
                                    "nonlinear_functions")},
    **{t: "Problem-Solving and Data Analysis" for t in (
        "evaluating_statistical_claims", "sample_statistics_and_margin_of_error", "one_variable_data",
        "percentages", "probability", "ratios_rates_proportions_and_units", "two_variable_data")},
    **{t: "Geometry and Trigonometry" for t in ("area_and_volume", "circles", "lines_angles_and_triangles",
                                                "right_triangles_and_trigonometry")},
}
SPR_SHARE = 12 / 44             # grid-ins in a section (blueprint.SPR_AT, both modules)


def _spec(subject: str) -> dict:
    from .blueprint import SPEC
    return SPEC[subject]


def weights(subject: str = "math") -> dict[str, int]:
    """Question Bank counts per skill: SKILL_WEIGHT for Math, blueprint.RW_SKILL_WEIGHT for R&W."""
    return _spec(subject)["skill_weight"] or SKILL_WEIGHT


def domain_of(subject: str = "math") -> dict[str, str]:
    """skill -> domain; R&W's from the bank's own topics."""
    if subject == "math":
        return DOMAIN_OF
    from satbank.topic import load_topics
    return {t: load_topics()[t].domain for t in weights(subject)}


def section_size(subject: str = "math") -> int:
    return 2 * _spec(subject)["module_size"]


def _domain_split(subject: str = "math") -> dict[str, int]:
    out: Counter = Counter()
    for module in _spec(subject)["domain_split"].values():
        out.update(module)
    return dict(out)


def shares(subject: str = "math") -> dict[str, float]:
    """s_t: each skill's share of a section (44 Math, 54 R&W)."""
    split, of = _domain_split(subject), domain_of(subject)
    total = sum(split.values())
    per_domain: Counter = Counter()
    for t, w in weights(subject).items():
        per_domain[of[t]] += w
    return {t: split[of[t]] / total * w / per_domain[of[t]] for t, w in weights(subject).items()}


def _round10(value: float) -> int:
    return round(value / 10) * 10


def _round5(value: float) -> int:
    return int(math.floor(value / 5 + 0.5) * 5)


def _cfg(row) -> dict:
    return json.loads(row["cfg"] or "{}") if row["cfg"] else {}


def _standard(row) -> bool:
    """R16 via tests.md: a sitting ranks when S5 marked it ranked (Test-day,
    official timing, adaptive route, standard module 1, no pause or long
    break) and it is a test kind. The cfg rules are kept as a floor for
    sittings finished before S5 sets `ranked`."""
    if row["kind"] not in RANK_KINDS or row["ranked"] == 0:
        return False
    cfg = _cfg(row)
    return (cfg.get("timing", "official") == "official" and cfg.get("timed", True) is not False and
            cfg.get("route", "adaptive") == "adaptive" and
            cfg.get("m1", "standard") == "standard" and
            row["route"] not in ("fixed-upper", "fixed-lower") and
            cfg.get("variant") is None and cfg.get("conditions", "test_day") != "training")


def _subject(row) -> str:
    return (row["subject"] if "subject" in row.keys() else None) or _cfg(row).get("subject") or "math"


def _sittings(learner: str, subject: str = "math") -> list[dict]:
    out = []
    for row in db.rows("SELECT * FROM sessions WHERE learner=? AND finished IS NOT NULL"
                       " AND result IS NOT NULL ORDER BY finished DESC,id DESC", learner):
        if _subject(row) != subject:
            continue
        res = json.loads(row["result"] or "{}")
        band = res.get("estimate") or {}
        if not isinstance(band, dict) or band.get("low") is None or band.get("high") is None:
            continue
        out.append({"id": row["id"], "kind": row["kind"], "low": band["low"], "high": band["high"],
                    "mid": _mid(band), "at": row["finished"], "capped": bool(band.get("capped")),
                    "route": row["route"], "standard": _standard(row), "outside": False,
                    "why": None if _standard(row) else (row["unranked_why"] or "not standard")})
    col = "math" if subject == "math" else "rw"
    for row in db.rows(f"SELECT * FROM outside_scores WHERE learner=? AND {col} IS NOT NULL", learner):
        out.append({"id": row["id"], "kind": "outside", "low": row[col], "high": row[col],
                    "mid": row[col], "at": row["day"] + "T12:00:00+00:00", "capped": False,
                    "route": None, "standard": False, "outside": True, "source": row["source"]})
    return sorted(out, key=lambda x: (x["at"], str(x["id"])), reverse=True)


def current(learner: str, subject: str = "math", items: list[dict] | None = None) -> dict | None:
    """"Your current score" in a subject, the one rule every page shows: the
    latest up to 3 scored sittings and logged scores, as the band of their mean
    mid. One alone keeps its own band (a logged point gets scoring.band's); when
    every one was capped on a lower route the band stays under that ceiling.
    None of them: the score the student typed (source "self"), else None.
    `items` = _sittings(learner, subject) when the caller has them already."""
    recent = (_sittings(learner, subject) if items is None else items)[:3]
    if not recent:
        lr = db.one("SELECT current, rw_now, updated FROM learners WHERE id=?", learner)
        typed = lr["rw_now" if subject == "rw" else "current"] if lr else None
        return {**scoring.band(typed), "capped": False, "n": 0, "source": "self", "at": lr["updated"],
                "id": None} if typed else None
    # items built elsewhere (fixtures, older callers) may lack capped / mid / outside
    if len(recent) == 1 and not recent[0].get("outside"):
        x = recent[0]
        band = {"low": x["low"], "high": x["high"], "mid": _mid(x), "capped": bool(x.get("capped"))}
    else:
        band = scoring.section_band(statistics.mean(_mid(x) for x in recent),
                                    "lower" if all(x.get("capped") for x in recent) else None, subject)
    sat = next((x for x in recent if not x.get("outside")), None)
    return {**band, "n": len(recent), "source": "measured" if sat else (recent[0].get("source") or "other"),
            "at": recent[0]["at"], "id": sat["id"] if sat else None}


def _mid(band: dict) -> float:
    """A stored band's centre: its own `mid` (held at a route's ceiling), else the middle of the ends."""
    return band["mid"] if band.get("mid") is not None else (band["low"] + band["high"]) / 2


def _mean3(items: list[dict]) -> int | None:
    """R16: the last up to 3 scored sittings within 45 days, outside scores included."""
    recent = [x for x in items if (dt.date.today() - dt.date.fromisoformat(x["at"][:10])).days <= 45][:3]
    return _round10(sum(x["mid"] for x in recent) / len(recent)) if recent else None


def estimate(learner: str, subject: str = "math") -> dict:
    items = _sittings(learner, subject)
    latest = items[0] if items else None
    previous = items[1] if len(items) > 1 else None
    best = max(items, key=lambda x: x["mid"]) if items else None
    mean3 = _mean3(items)
    standard = [x for x in items if x["standard"] and x["kind"] in SECTION_KINDS]
    last3 = standard[:3]
    combined = {**scoring.band(statistics.mean(x["mid"] for x in last3)), "n": len(last3)} if len(last3) >= 2 else None
    last30 =[x for x in standard if (dt.date.today() - dt.date.fromisoformat(x["at"][:10])).days <= 30]
    # the 100 below is how far apart sittings landed, not a band width
    if not standard:
        confidence = {"level": "low", "reason": "Rough estimate: based on a module or the diagnostic only. A full section makes it firmer."}
    elif len(last30) >= 2 and max(x["mid"] for x in last30[:3]) - min(x["mid"] for x in last30[:3]) <= 100:
        confidence = {"level": "high", "reason": f"Consistent estimate: your last {len(last30[:3])} sections (past 30 days) landed within 100 points of each other."}
    elif len(standard) == 1:
        confidence = {"level": "medium", "reason": "Mixed estimate: one full section so far. A second within 100 points would firm it up."}
    else:
        gap = round(abs(standard[0]["mid"] - standard[1]["mid"]) / 10) * 10
        confidence = {"level": "medium", "reason": f"Mixed estimate: your last two sections are {gap} points apart."}
    delta = round(latest["mid"] - previous["mid"]) if latest and previous else None
    trend = {"direction": "steady" if delta is None or abs(delta) <= 20 else ("up" if delta > 0 else "down"),
             "delta": delta, "since": previous["at"] if previous else None}
    sections = [x for x in items if x["kind"] in SECTION_KINDS]
    counted = {"sittings": len(items), "sections": len(sections),
               "modules": sum(x["kind"] == "module" for x in items),
               "diagnostics": sum(x["kind"] == "diagnostic" for x in items)}
    return {"subject": subject, "latest": latest, "previous": previous, "best": best,
            "range": current(learner, subject, items),
            "mean3": mean3, "combined": combined, "confidence": confidence, "trend": trend,
            "routed_up": {"up": sum(x["route"] == "upper" for x in sections), "sections": len(sections)},
            "counted": counted}


def _peer_key(row) -> tuple:
    """Who a sitting is compared with: the same kind and subject, a full SAT's
    section only with full SAT sections, and for a paper (kind mock, mock_id
    'P{n}') the same paper."""
    paper = row["kind"] == "mock" and (row["mock_id"] or "").startswith("P")
    full = bool(_cfg(row).get("full"))
    return (row["kind"], _subject(row), row["mock_id"] if paper else ("paper" if row["kind"] == "paper" else None),
            paper, full)


def percentile(sid: str) -> dict:
    """R16: a ranked sitting among each learner's first ranked sitting of the
    same kind (a paper: of that paper), shown only when n >= 20."""
    row = db.one("SELECT * FROM sessions WHERE id=?", sid)
    if not row or not row["finished"] or not _standard(row):
        return {"ranked": False, "pct": None, "n": 0,
                "why": (row["unranked_why"] if row and row["unranked_why"] else "not standard")}
    band = (json.loads(row["result"] or "{}").get("estimate") or {})
    if band.get("low") is None:
        return {"ranked": False, "pct": None, "n": 0, "why": "unscored"}
    key = _peer_key(row)
    first: dict[str, tuple[str, float]] = {}
    for x in db.rows(f"SELECT * FROM sessions WHERE kind=? AND finished IS NOT NULL AND learner IS NOT NULL"
                     f" AND {db.NOT_SAMPLE} ORDER BY finished,id", row["kind"]):
        if _peer_key(x) != key or x["learner"] in first or not _standard(x):
            continue
        e = (json.loads(x["result"] or "{}").get("estimate") or {})
        if e.get("low") is not None and e.get("high") is not None:
            first[x["learner"]] = (x["id"], _mid(e))
    mine = first.get(row["learner"])
    if mine and mine[0] != sid:
        return {"ranked": False, "pct": None, "n": 0, "why": "repeat sitting"}
    peers = [m for _, m in first.values()]
    if len(peers) < 20:
        return {"ranked": False, "pct": None, "n": len(peers), "why": "too few sittings"}
    me = _mid(band)
    return {"ranked": True, "pct": round(100 * sum(score <= me for score in peers) / len(peers)), "n": len(peers)}


# ------------------------------------------------------------------ national placement (SR5)

def _table() -> dict | None:
    try:
        return json.loads(PERCENTILES.read_text())
    except (OSError, ValueError):
        return None


def national(low: int, high: int, subject: str = "math") -> dict | None:
    """Where a band's two ends sit on College Board's SAT User percentiles, as
    printed ('99+' and '1-' stay as they are)."""
    data = _table()
    if not data or subject not in data["tables"]:
        return None
    table = data["tables"][subject]
    step = lambda v: str(max(int(min(table, key=int)), min(int(max(table, key=int)), _round10(v))))  # noqa: E731
    return {"low_pct": table[step(low)], "high_pct": table[step(high)], "source": data["source"],
            "year": data["year"]}


# ------------------------------------------------------------------ exact re-marking

def mid(earned: float, possible: float, route: str | None, subject: str = "math") -> dict:
    """SR1's measure: scoring's band for this marking, its mid the unrounded
    centre held at the lower route's ceiling (so a point under the cap still
    counts and one over it does not)."""
    c = scoring._interpolate(earned / possible if possible else 0.0)
    return {**scoring.section_band(c, route, subject), "centre": c}


def _paper(row) -> list[dict]:
    p = deps.paper_of(row)
    if isinstance(p, dict):
        p = [x for v in p.values() if isinstance(v, list) for x in v]
    return [q for q in p if isinstance(q, dict) and "key" in q and "id" in q]


def _marking(sid: str):
    """(row, questions, right {qid: bool}, removed {qid}) for a finished sitting."""
    row = db.one("SELECT * FROM sessions WHERE id=?", sid)
    if not row:
        return None
    questions = _paper(row)
    answers = json.loads(row["answers"] or "{}")
    result = json.loads(row["result"] or "{}") if row["result"] else {}
    removed = set(result.get("removed") or ())
    removed |= {r["qid"] for r in db.rows("SELECT qid FROM attempts WHERE session=? AND disputed=1", sid)}
    remarked = set(result.get("remarked") or ())
    right = {q["id"]: q["id"] in remarked or scoring.is_correct(q, answers.get(q["id"])) for q in questions}
    return row, questions, right, removed


def _route(row) -> str | None:
    """Only a two-module sitting (a section, the Season Final) has a route; it is what marking capped by."""
    return row["route"]


def _score(row, questions, right, removed) -> dict:
    earned = sum(scoring.WEIGHT[q["difficulty"]] for q in questions if q["id"] not in removed and right[q["id"]])
    possible = sum(scoring.WEIGHT[q["difficulty"]] for q in questions if q["id"] not in removed)
    return mid(earned, possible, _route(row), _subject(row))


def _printed(m: dict) -> dict:
    """The band in scoring's tens, the midpoint unrounded."""
    return {k: m[k] for k in ("low", "high", "mid", "capped", "centre")}


def rescore(sid: str, right=(), wrong=(), drop=()) -> dict | None:
    """SR2 / T16: the sitting re-marked with those qids right, those wrong and
    those left out, the route held as taken."""
    got = _marking(sid)
    if not got:
        return None
    row, questions, marks, removed = got
    marks = {**marks, **{q: True for q in right}, **{q: False for q in wrong}}
    m = _score(row, questions, marks, removed | set(drop))
    return {**_printed(m), "route": _route(row)}


def _shapley(value, names: list[str]) -> dict[str, float]:
    """Each bucket's gain averaged over every order of flipping the buckets."""
    k = len(names)
    cache: dict[frozenset, float] = {}

    def v(s: frozenset) -> float:
        if s not in cache:
            cache[s] = value(s)
        return cache[s]

    out = {}
    for i in names:
        rest = [n for n in names if n != i]
        total = 0.0
        for size in range(len(rest) + 1):
            w = math.factorial(size) * math.factorial(k - size - 1) / math.factorial(k)
            for s in itertools.combinations(rest, size):
                fs = frozenset(s)
                total += w * (v(fs | {i}) - v(fs))
        out[i] = total
    return out


def _largest_remainder(values: dict[str, float], step: int = 5) -> dict[str, int]:
    """Round to `step` so the printed parts add up to the printed whole."""
    whole = _round5(sum(values.values())) if step == 5 else round(sum(values.values()) / step) * step
    floors = {k: math.floor(v / step) * step for k, v in values.items()}
    left = int(round((whole - sum(floors.values())) / step))
    for k in sorted(values, key=lambda k: values[k] - floors[k], reverse=True)[:max(0, left)]:
        floors[k] += step
    return floors


def ledger(sid: str) -> dict | None:
    """SR1: where a scored sitting's points went, exactly and order-free."""
    got = _marking(sid)
    if not got:
        return None
    row, questions, marks, removed = got
    result = json.loads(row["result"] or "{}") if row["result"] else {}
    if not row["finished"] or (result.get("estimate") or {}).get("low") is None:
        return None
    answers = json.loads(row["answers"] or "{}")
    base = _score(row, questions, marks, removed)
    misses = [q for q in questions if not marks[q["id"]] and q["id"] not in removed]
    everything = _score(row, questions, {**marks, **{q["id"]: True for q in misses}}, removed)
    per_q = {}
    for q in misses:
        m = _score(row, questions, {**marks, q["id"]: True}, removed)
        per_q[q["id"]] = {"pts": round(m["mid"] - base["mid"], 2), "capped": m["capped"]}
    from . import progress
    cause = {qid: c["cause"] for qid, c in progress.causes(row["learner"], session=sid, subject=_subject(row))
             .get("per_q", {}).items()} if row["learner"] else {}

    def buckets(of) -> list[dict]:
        groups: dict[str, list[str]] = defaultdict(list)
        for q in misses:
            groups[of(q)].append(q["id"])
        names = sorted(groups)
        if not names:
            return []

        def value(s: frozenset) -> float:
            flipped = {qid: True for n in s for qid in groups[n]}
            return _score(row, questions, {**marks, **flipped}, removed)["mid"] - base["mid"]

        pts = _shapley(value, names)
        printed = _largest_remainder(pts)
        return [{"key": n, "n": len(groups[n]), "pts": round(pts[n], 2), "printed": printed[n]} for n in names]

    by_cause = [{"cause": b.pop("key"), **b} for b in buckets(lambda q: cause.get(q["id"], "gap"))]
    by_tier = [{"tier": b.pop("key"), **b} for b in buckets(lambda q: q["difficulty"])]
    by_domain = [{"domain": b.pop("key"), **b} for b in buckets(lambda q: q.get("domain") or "Math")]
    blank = {b["key"]: b for b in buckets(lambda q: "blank" if answers.get(q["id"]) in (None, "") else "incorrect")}
    route = None
    if row["route"] == "lower":
        m1 = questions[:_spec(_subject(row))["module_size"]]
        m1_right = sum(marks[q["id"]] for q in m1 if q["id"] not in removed)
        needed = math.ceil(scoring.ROUTE_UP_AT * len(m1))
        short = max(0, needed - m1_right)
        savers = sorted((q for q in m1 if q in misses), key=lambda q: (scoring.WEIGHT[q["difficulty"]],
                                                                       -per_q[q["id"]]["pts"]))[:short]
        # all right off the cap: the centre the ceiling took away, not a band end
        route = {"m1_right": m1_right, "m1_asked": len(m1), "needed": needed, "short_by": short,
                 "savers": [q["id"] for q in savers],
                 "cap_cost": max(0, round(everything["centre"] - everything["mid"]))}
    return {"subject": _subject(row), "mid": base["mid"],
            "all_right": {"low": everything["low"], "high": everything["high"], "mid": everything["mid"]},
            "total": round(everything["mid"] - base["mid"], 2), "per_q": per_q,
            "by_cause": by_cause, "by_tier": by_tier, "by_domain": by_domain,
            "incorrect_pts": blank.get("incorrect", {}).get("pts", 0.0),
            "blank_pts": blank.get("blank", {}).get("pts", 0.0), "route": route}


def rescore_sitting(sid: str, qid: str | None = None, how: str | None = None,
                    report: int | None = None) -> dict | None:
    """SR19: after a key correction, re-score the sitting. A broken or
    wrong-key question leaves scoring ('removed'); a remarked one counts right
    ('remarked'). Disputed attempts are always removed. The route is held."""
    row = db.one("SELECT * FROM sessions WHERE id=?", sid)
    if not row or not row["finished"] or not row["result"]:
        return None
    result = json.loads(row["result"])
    before = result.get("estimate")
    if not isinstance(before, dict) or before.get("low") is None:
        return None
    removed, remarked = set(result.get("removed") or ()), set(result.get("remarked") or ())
    if qid and how == "removed":
        removed.add(qid)
    if qid and how == "remarked":
        remarked.add(qid)
    result["removed"], result["remarked"] = sorted(removed), sorted(remarked)
    db.run("UPDATE sessions SET result=? WHERE id=?", json.dumps(result), sid)
    _, questions, marks, gone = _marking(sid)
    m = _score(row, questions, marks, gone)
    after = {**before, **_printed(m)}
    result["estimate"] = after
    result.setdefault("rescored", []).append({"at": deps.now(), "qid": qid, "how": how, "report": report,
                                              "before": {"low": before["low"], "high": before["high"]},
                                              "after": {"low": after["low"], "high": after["high"]}})
    db.run("UPDATE sessions SET result=? WHERE id=?", json.dumps(result), sid)
    return {"before": before, "after": after}


# ------------------------------------------------------------------ U4: the practice model

def _rows(learner: str, subject: str = "math", until: str | None = None, days: int | None = None) -> list:
    sql = ("SELECT topic, template, difficulty, fmt, correct, guess, hints, ms, sms, at FROM attempts"
           " WHERE learner=? AND repeat=0 AND disputed=0 AND void IS NULL")
    args: list = [learner]
    if until:
        sql += " AND at<=?"
        args.append(until)
    rows = [dict(r) for r in db.rows(sql + " ORDER BY id DESC", *args)]
    return [r for r in rows if deps.subject_of(r["topic"]) == subject]


def _acc(rows) -> tuple[float, int]:
    """Difficulty-weighted accuracy; a guessed or hinted right counts half."""
    num = den = 0.0
    for r in rows:
        w = scoring.WEIGHT.get(r["difficulty"], 2)
        den += w
        num += w * r["correct"] * (0.5 if r.get("guess") or r.get("hints") else 1)
    return (num / den if den else 0.5), len(rows)


def model(rows: list[dict], subject: str = "math") -> dict:
    """U4 steps 1-3, pure: per skill (s_t, a, n, a'), F and S."""
    s = shares(subject)
    overall, _ = _acc(rows)
    per: dict[str, list] = defaultdict(list)
    for r in rows:
        if r["topic"] in s and len(per[r["topic"]]) < 60:
            per[r["topic"]].append(r)
    skills = {}
    for t, share in s.items():
        a, n = _acc(per.get(t, []))
        pulled = (n * a + EVIDENCE * overall) / (n + EVIDENCE)
        skills[t] = {"share": share, "accuracy": a if n else None, "n": n, "pulled": pulled}
    F = sum(v["share"] * v["pulled"] for v in skills.values())
    return {"skills": skills, "F": F, "S": scoring._interpolate(F), "overall": overall, "answers": len(rows)}


def _lift(m: dict, topics, to: float = STRONG_AT) -> float:
    """S after raising these skills to `to`, as one change."""
    F = m["F"] + sum(m["skills"][t]["share"] * (max(m["skills"][t]["pulled"], to) - m["skills"][t]["pulled"])
                     for t in topics)
    return scoring._interpolate(F) - m["S"]


def _tiers(rows) -> dict[str, dict]:
    out: dict[str, dict] = defaultdict(lambda: {"easy": [0, 0], "medium": [0, 0], "hard": [0, 0]})
    for r in rows:
        if r["difficulty"] in ("easy", "medium", "hard"):
            out[r["topic"]][r["difficulty"]][0] += r["correct"]
            out[r["topic"]][r["difficulty"]][1] += 1
    return {k: dict(v) for k, v in out.items()}


def gains(learner: str, subject: str = "math") -> dict | None:
    """U4 (+ T6): each skill priced in points, the top 3 together, and the
    extras (grid-ins, pace), tiers and domains. None under 30 answers."""
    rows = _rows(learner, subject)
    if len(rows) < MIN_ANSWERS:
        return None
    m, of, size = model(rows, subject), domain_of(subject), section_size(subject)
    from . import progress
    skills = []
    tier_now = {}
    for r in rows:
        tier_now.setdefault(r["topic"], r["difficulty"])
    medians = defaultdict(list)
    for r in rows:
        spent = r["ms"] if r["ms"] is not None else r["sms"]
        if spent:
            medians[r["topic"]].append(spent)
    for t, v in m["skills"].items():
        gain = _lift(m, [t])
        k = progress.steps_to(learner, t, progress.STRONG, tier_now.get(t, "medium")) or 0
        secs = statistics.median(medians[t]) / 1000 if medians[t] else deps.PACE[subject]
        skills.append({"topic": t, "domain": of[t], "gain": _round5(gain), "raw": round(gain, 2),
                       "per_test": round(size * v["share"], 1),
                       "accuracy": None if v["accuracy"] is None else round(v["accuracy"], 3),
                       "evidence": v["n"], "rough": v["n"] < 10, "to_strong": k,
                       "minutes": round(k * secs / 60, 1)})
    skills.sort(key=lambda x: (-x["raw"], x["topic"]))
    top3 = [x["topic"] for x in skills[:3]]
    tiers = _tiers(rows)
    extras = []
    spr = [r for r in rows if r["fmt"] == "spr"][:60]
    mcq = [r for r in rows if r["fmt"] == "mcq"][:60]
    if len(spr) >= 10 and len(mcq) >= 10:
        a_s = sum(r["correct"] for r in spr) / len(spr)
        a_m = sum(r["correct"] for r in mcq) / len(mcq)
        if a_m - a_s >= 0.15:
            g = scoring._interpolate(m["F"] - SPR_SHARE * a_s + SPR_SHARE * a_m) - m["S"]
            extras.append({"kind": "spr", "gain": _round5(g),
                           "detail": {"spr": round(a_s, 3), "mcq": round(a_m, 3), "per_test": 12}})
    cost = time_cost(learner, subject=subject)
    if cost:
        extras.append({"kind": "pace", "gain": cost, "detail": {}})
    board = progress.board(learner, subject)
    by_domain = []
    for d in (scoring.RW_DOMAINS if subject == "rw" else progress.DOMAINS):
        ts = [t for t in m["skills"] if of[t] == d]
        answered = sum(board[t]["answered"] for t in ts if t in board)
        by_domain.append({"domain": d, "gain": _round5(_lift(m, ts)),
                          "mastery": round(statistics.mean([board[t]["mastery"] for t in ts if t in board] or [0]), 3),
                          "answered": answered,
                          "right": sum(round((board[t]["accuracy"] or 0) * board[t]["answered"]) for t in ts if t in board),
                          "traps": sum(len(board[t]["traps"]) for t in ts if t in board)})
    return {"subject": subject, "answers": len(rows), "total": _round5(_lift(m, list(m["skills"]))),
            "top3": {"topics": top3, "gain": _round5(_lift(m, top3))},
            "others": {"gain": _round5(_lift(m, [x["topic"] for x in skills[3:]]))},
            "skills": skills, "tiers": tiers, "extras": extras, "by_domain": by_domain}


def trap_pts(learner: str, template: str, normalized: str, topic: str) -> int | None:
    """V4: a trap's points, gain(t) x share, where share is this trap's wrong
    first tries over all wrong first tries in skill t in 60 days (U1). Whole
    points; None below 1, and while gains is None (under 30 answers)."""
    g = gains(learner, deps.subject_of(topic))
    gain = next((x["gain"] for x in g["skills"] if x["topic"] == topic), None) if g else None
    if not gain:
        return None
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=60)).isoformat()
    wrong = db.rows("SELECT template, norm FROM attempts WHERE learner=? AND topic=? AND correct=0"
                    " AND repeat=0 AND disputed=0 AND void IS NULL AND at>=?", learner, topic, since)
    mine = sum(1 for r in wrong if r["template"] == template and r["norm"] == normalized)
    pts = round(gain * mine / len(wrong)) if wrong else 0
    return pts if pts >= 1 else None


def need(target: int, learner: str | None = None, subject: str = "math") -> dict:
    """U4 step 7 (+ T12's path): what a section target takes, in right answers
    of the section (`right_of_44` keeps its name: out of `of`, 54 for R&W), the
    module-1 route and the skill work."""
    ceiling = scoring.ANCHORS[-1][1]
    n, m1_of = section_size(subject), _spec(subject)["module_size"]
    m1_min = math.ceil(scoring.ROUTE_UP_AT * m1_of - 1e-9) if target > scoring.CEILING[subject] else None
    m = model(_rows(learner, subject), subject) if learner else None
    now_of_44 = round(n * m["F"]) if m and m["answers"] else None
    if target > ceiling:
        return {"target": target, "reachable": False, "ceiling": int(ceiling), "right_of_44": n, "of": n,
                "now_of_44": now_of_44, "m1_min": m1_min, "m1_of": m1_of, "where": [], "path": None}
    f_star = scoring.fraction_for(target)["fraction"]
    right = min(n, max(0, math.ceil(n * f_star - 1e-9)))
    out = {"target": target, "reachable": True, "ceiling": int(ceiling), "right_of_44": right, "of": n,
           "now_of_44": now_of_44, "m1_min": m1_min, "m1_of": m1_of, "where": [], "path": None}
    if m and m["answers"] >= MIN_ANSWERS:
        g = gains(learner, subject) or {"skills": []}
        order = [x["topic"] for x in g["skills"]]
        out["where"] = order[:3]
        chosen, F = [], m["F"]
        for t in order:
            if F >= f_star:
                break
            chosen.append(t)
            F = m["F"] + sum(m["skills"][c]["share"] * (max(m["skills"][c]["pulled"], STRONG_AT)
                                                        - m["skills"][c]["pulled"]) for c in chosen)
        minutes = sum(x["minutes"] for x in g["skills"] if x["topic"] in chosen)
        out["path"] = {"skills": chosen, "minutes": round(minutes), "reachable": F >= f_star, "at_least": True}
    return out


def route(learner: str, subject: str = "math") -> dict | None:
    """P10's route check: module 1's tier mix at the learner's first-try
    accuracy per tier. None under 30 answers."""
    rows = _rows(learner, subject)
    if len(rows) < MIN_ANSWERS:
        return None
    return route_of(rows, subject)


def route_of(rows, subject: str = "math") -> dict:
    mix = _spec(subject)["tiers"]["module1"]
    p = {}
    for tier in mix:
        rs = [r for r in rows if r["difficulty"] == tier]
        n = len(rs)
        a = sum(r["correct"] for r in rs) / n if n else 0.5
        p[tier] = (n * a + EVIDENCE * 0.5) / (n + EVIDENCE)
    m1 = sum(mix[t] * p[t] for t in mix) / sum(mix.values())
    return {"m1": round(m1, 3), "route": "upper" if m1 >= scoring.ROUTE_UP_AT else "lower",
            "margin": round(m1 - scoring.ROUTE_UP_AT, 3), "tiers": {t: round(v, 3) for t, v in p.items()}}


def time_cost(learner: str, pace: dict | None = None, subject: str = "math") -> int:
    """T8: points lost to the clock alone at the learner's pace. Blanks are the
    module-1 strip's cells after it runs out, and as many at the end of module
    2; each costs only what the learner would have scored on it."""
    from . import progress
    pace = pace or progress.pace(learner, subject=subject)
    fc = pace["forecast"]
    if not fc.get("blanks"):
        return 0
    rows = _rows(learner, subject)
    m = model(rows, subject) if rows else None
    if not m:
        return 0
    tiers = _spec(subject)["tiers"]
    overall = m["overall"]
    a_tier = {}
    for tier in ("easy", "medium", "hard"):
        rs = [r for r in rows if r["difficulty"] == tier]
        a = sum(r["correct"] for r in rs) / len(rs) if rs else overall
        a_tier[tier] = (len(rs) * a + EVIDENCE * overall) / (len(rs) + EVIDENCE)
    latest = db.one("SELECT route FROM sessions WHERE learner=? AND kind IN ('mock','section','paper')"
                    " AND finished IS NOT NULL AND route IS NOT NULL AND COALESCE(subject,'math')=?"
                    " ORDER BY finished DESC", learner, subject)
    up = (latest["route"] == "upper") if latest else m["F"] >= scoring.ROUTE_UP_AT
    form = "module2_upper" if up else "module2_lower"
    W = sum(scoring.WEIGHT[t] * n for t, n in tiers["module1"].items()) + \
        sum(scoring.WEIGHT[t] * n for t, n in tiers[form].items())
    m1_tiers = [c["tier"] for c in fc["strip"][fc["runs_out_at"]:]] if fc.get("runs_out_at") is not None else []
    ladder = [t for t in ("easy", "medium", "hard") for _ in range(tiers[form][t])]     # a module runs easiest first
    m2_tiers = fc.get("m2_blank_tiers") or ladder[-len(m1_tiers):]
    lost = sum(scoring.WEIGHT[t] * a_tier[t] for t in m1_tiers + m2_tiers) / W
    return max(0, _round5(m["S"] - scoring._interpolate(m["F"] - lost)))


def practice_delta(learner: str, since: str, subject: str = "math") -> dict:
    """T10 / T19: how far U4's S moved between `since` and now (only its
    difference is ever shown)."""
    before = _rows(learner, subject, until=since)
    after = _rows(learner, subject)
    if not after:
        return {"pts": 0, "answers": 0, "since": since}
    delta = model(after, subject)["S"] - (model(before, subject)["S"] if before
                                          else scoring._interpolate(model([], subject)["F"]))
    return {"pts": _round5(delta), "raw": round(delta, 2), "answers": len(after) - len(before), "since": since}


# ------------------------------------------------------------------ U9: projection

def project(points: list[tuple[dt.date, float]], to_day: dt.date, half_latest: float | None = None) -> dict | None:
    """U9, pure: a shrunk, tapered least-squares line, shown as scoring's band
    around where it lands (`half_latest` is ignored; every band is +- 10).
    `ponytail:` replace with a fitted growth model once enough learners have sat
    both a module and the real SAT to calibrate against."""
    points = sorted(points)
    n = len(points)
    if n < 3 or (points[-1][0] - points[0][0]).days < 21:
        return None
    x = [(d - points[0][0]).days / 7 for d, _ in points]
    y = [v for _, v in points]
    xb, yb = sum(x) / n, sum(y) / n
    sxx = sum((xi - xb) ** 2 for xi in x)
    b = sum((xi - xb) * (yi - yb) for xi, yi in zip(x, y)) / sxx
    b2 = b * n / (n + 3)
    anchor = yb + b2 * (x[-1] - xb)
    w = max(0.0, (to_day - points[-1][0]).days / 7)
    gain = b2 * min(w, 4) + max(-20.0, min(20.0, b2)) * max(w - 4, 0)
    mid_ = max(200.0, min(800.0, anchor + gain))
    band = scoring.band(mid_)
    return {"mid": round(mid_), "low": band["low"], "high": band["high"], "half": scoring.HALF,
            "slope": round(b, 1), "slope_used": round(b2, 1), "n": n, "to": to_day.isoformat(),
            "label": "If this pace held"}


def projection(learner: str, to_day: str | dt.date | None = None, subject: str = "math") -> dict | None:
    """U9: the band on a date, from 3+ scored standard sittings of the subject
    over 21+ days in the last 90."""
    if to_day is None:
        row = db.one("SELECT exam_date FROM learners WHERE id=?", learner)
        to_day = row["exam_date"] if row and row["exam_date"] else None
    if to_day is None:
        return None
    day = dt.date.fromisoformat(to_day) if isinstance(to_day, str) else to_day
    cutoff = dt.date.today() - dt.timedelta(days=90)
    items = [x for x in _sittings(learner, subject) if x["standard"] and dt.date.fromisoformat(x["at"][:10]) >= cutoff]
    return project([(dt.date.fromisoformat(x["at"][:10]), x["mid"]) for x in items], day) if items else None


# ------------------------------------------------------------------ totals and placement

def total(learner: str, sid: str | None = None) -> dict | None:
    """SR4: an R&W centre plus a Math centre, +- 10 (scoring.total_band), placed
    on College Board's total table. Each side is `sid` (and a full SAT part's
    partner) for its own subject, else that subject's current() score. Never two
    ranges added."""
    parts: dict[str, dict] = {}
    row = db.one("SELECT * FROM sessions WHERE id=?", sid) if sid else None
    full = (_cfg(row).get("full") or {}).get("id") if row else None
    mine = [row] if row else []
    if full:
        mine += db.rows("SELECT * FROM sessions WHERE learner=? AND id<>? AND json_extract(cfg,'$.full.id')=?",
                        row["learner"], sid, full)
    for r in mine:
        band = json.loads(r["result"] or "{}").get("estimate") if r["result"] else None
        if isinstance(band, dict) and band.get("low") is not None:
            parts[_subject(r)] = {"low": band["low"], "high": band["high"], "mid": _mid(band),
                                  "capped": bool(band.get("capped")), "n": 1, "source": "measured",
                                  "at": r["finished"], "id": r["id"]}
    for subject in ("rw", "math"):
        if subject not in parts and (now := current(learner, subject)):
            parts[subject] = now
    if set(parts) != {"rw", "math"}:
        return None
    parts = {s: {"subject": s, **p, "value": _round10(p["mid"])} for s, p in parts.items()}
    lr = db.one("SELECT rw_target, target FROM learners WHERE id=?", learner)
    t = scoring.total_band(parts["rw"]["mid"], parts["math"]["mid"])
    gap = None
    if lr and lr["target"] and lr["rw_target"]:
        path = _path(sid, lr["target"]) if sid and parts["math"]["id"] == sid else None
        gap = {"target": lr["target"] + lr["rw_target"], "above_high": lr["target"] + lr["rw_target"] - t["high"],
               "math_path": path, "rw_to_target": lr["rw_target"] - parts["rw"]["value"]}
    history = [{"day": r["day"], "value": r["rw"], "source": r["source"]}
               for r in db.rows("SELECT day, rw, source FROM outside_scores WHERE learner=? AND rw IS NOT NULL"
                                " ORDER BY day", learner)]
    return {**t, "pct": national(t["low"], t["high"], "total"), "parts": [parts["rw"], parts["math"]],
            "gap": gap, "rw_history": history}


def _path(sid: str, target: int) -> list[str] | None:
    """SR2: misses flipped greedily by points (ties: easier first) until the
    midpoint reaches the target; None when all right on this route falls short."""
    lg = ledger(sid)
    if not lg:
        return None
    got = _marking(sid)
    row, questions, marks, removed = got
    diff = {q["id"]: scoring.WEIGHT[q["difficulty"]] for q in questions}
    order = sorted(lg["per_q"], key=lambda q: (-lg["per_q"][q]["pts"], diff[q]))
    chosen = []
    for q in order:
        if rescore(sid, right=chosen)["mid"] >= target:
            return chosen
        chosen.append(q)
    return chosen if rescore(sid, right=chosen)["mid"] >= target else None


def growth(learner: str, subject: str = "math") -> dict | None:
    """X15: mean3 against the first ranked section's midpoint, among learners
    whose first ranked section of the subject was within 40 points and who have
    sat two or more ranked sections of it (n >= 20)."""
    def firsts() -> dict[str, list[float]]:
        out: dict[str, list[float]] = defaultdict(list)
        for x in db.rows(f"SELECT * FROM sessions WHERE finished IS NOT NULL AND kind IN ('mock','section','paper')"
                         f" AND {db.NOT_SAMPLE} ORDER BY finished,id"):
            e = (json.loads(x["result"] or "{}").get("estimate") or {}) if x["result"] else {}
            if _standard(x) and _subject(x) == subject and e.get("low") is not None:
                out[x["learner"]].append(_mid(e))
        return out
    seq = firsts()
    mine = seq.get(learner)
    now3 = _mean3(_sittings(learner, subject)) if mine and len(mine) >= 2 else None
    if now3 is None:
        return None
    my_gain = now3 - mine[0]
    peers = []
    for k, s in seq.items():
        if k != learner and len(s) >= 2 and abs(s[0] - mine[0]) <= 40:
            # ponytail: one read per nearby peer; keep mean3 on learners if peers grow into thousands
            m3 = _mean3(_sittings(k, subject))
            if m3 is not None:
                peers.append(m3 - s[0])
    if len(peers) < 20:
        return None
    return {"since_first": round(my_gain), "first": mine[0], "n": len(peers),
            "pct": round(100 * sum(g < my_gain for g in peers) / len(peers))}


def calibration(learner: str, subject: str = "math") -> dict:
    """X15: official or Bluebook scores of the subject dated within 10 days of
    a ranked section of it, against that section's band."""
    col = "rw" if subject == "rw" else "math"     # outside_scores has one column per subject
    sections = [x for x in _sittings(learner, subject) if x["standard"] and x["kind"] in SECTION_KINDS]
    pairs = []
    for o in db.rows(f"SELECT * FROM outside_scores WHERE learner=? AND {col} IS NOT NULL"
                     " AND source IN ('bluebook','official') ORDER BY day", learner):
        day = dt.date.fromisoformat(o["day"])
        near = [s for s in sections if abs((dt.date.fromisoformat(s["at"][:10]) - day).days) <= 10]
        if near:
            s = min(near, key=lambda s: abs((dt.date.fromisoformat(s["at"][:10]) - day).days))
            pairs.append({"score": o[col], "day": o["day"], "source": o["source"], "section": s["id"],
                          "band": {"low": s["low"], "high": s["high"]},
                          "inside": s["low"] <= o[col] <= s["high"]})
    checked = 0             # pairs across every real learner, for "Checked against n scores"
    for o in db.rows(f"SELECT learner, day FROM outside_scores WHERE {col} IS NOT NULL"
                     f" AND source IN ('bluebook','official') AND {db.NOT_SAMPLE}"):
        lo = (dt.date.fromisoformat(o["day"]) - dt.timedelta(days=10)).isoformat()
        hi = (dt.date.fromisoformat(o["day"]) + dt.timedelta(days=11)).isoformat()
        checked += any(_standard(x) for x in db.rows(
            "SELECT * FROM sessions WHERE learner=? AND kind IN ('mock','section','paper')"
            " AND COALESCE(subject,'math')=? AND finished>=? AND finished<?", o["learner"], subject, lo, hi))
    return {"pairs": pairs, "latest": pairs[-1] if pairs else None, "inside": sum(p["inside"] for p in pairs),
            "checked": checked}


if __name__ == "__main__":
    # U4: the model's arithmetic, on synthetic answer rows
    def rows_at(acc: dict[str, float], n: int = 20) -> list[dict]:
        out = []
        for t, a in acc.items():
            right = round(a * n)
            out += [{"topic": t, "difficulty": "medium", "correct": int(i < right), "guess": 0, "hints": 0}
                    for i in range(n)]
        return out
    base = {t: 0.5 for t in SKILL_WEIGHT}
    m0 = model(rows_at(base))
    for t in SKILL_WEIGHT:
        assert model(rows_at({**base, t: 0.9}))["S"] >= m0["S"] - 1e-9, t
    perfect = model(rows_at({t: 1.0 for t in SKILL_WEIGHT}))
    assert all(abs(_lift(perfect, [t])) < 1e-9 for t in SKILL_WEIGHT)
    assert abs(sum(shares().values()) - 1) < 1e-9
    assert abs(shares()["circles"] - 7 / 44 * 67 / 348) < 1e-9
    assert need(700)["m1_min"] == 14 and need(560)["m1_min"] is None
    assert need(800)["reachable"] is False and need(800)["ceiling"] == 780
    for target in range(200, 790, 10):
        r = need(target)["right_of_44"]
        assert scoring._interpolate(r / 44) >= target - 1e-9, target
        assert r == 0 or scoring._interpolate((r - 1) / 44) < target, target
    assert scoring.route_after(need(700)["m1_min"], 22) == "upper"
    assert scoring.route_after(need(700)["m1_min"] - 1, 22) == "lower"
    # R&W: its own skills, a 54-question section, 27-question modules
    rw = weights("rw")
    assert abs(sum(shares("rw").values()) - 1) < 1e-9 and set(domain_of("rw").values()) == set(scoring.RW_DOMAINS)
    assert abs(shares("rw")["rw_cross_text_connections"] - 15 / 54 * 181 / 1400) < 1e-9
    assert model(rows_at({t: 0.9 for t in rw}), "rw")["S"] > model(rows_at({t: 0.5 for t in rw}), "rw")["S"]
    assert (need(700, subject="rw")["of"], need(700, subject="rw")["m1_min"]) == (54, 17)
    assert scoring.route_after(17, 27) == "upper" and scoring.route_after(16, 27) == "lower"
    # the 20-point rule: a lower route holds the centre at its ceiling, so only points under it count
    for c in (300, 522, 575, 606, 780):
        for r in (None, "upper", "lower"):
            b = mid(scoring.fraction_for(c)["fraction"], 1, r)
            assert b["high"] - b["low"] == 20 and (r != "lower" or b["high"] <= 580), (c, r, b)
    assert mid(scoring.fraction_for(606)["fraction"], 1, "lower")["mid"] == 580
    assert mid(scoring.fraction_for(522)["fraction"], 1, "lower")["mid"] == 522
    # P10: the route check
    all_right = [{"difficulty": t, "correct": 1} for t in ("easy", "medium", "hard") for _ in range(20)]
    assert route_of(all_right)["route"] == "upper" and route_of(all_right, "rw")["route"] == "upper"
    assert route_of([{**r, "correct": 0} for r in all_right])["route"] == "lower"
    # U9: a flat series projects its own mean; no more than 20 a week after week 4; a 20-point band
    d0 = dt.date(2026, 9, 1)
    flat = project([(d0, 500), (d0 + dt.timedelta(days=14), 500), (d0 + dt.timedelta(days=28), 500)],
                   d0 + dt.timedelta(days=120))
    assert flat["mid"] == 500 and (flat["low"], flat["high"]) == (490, 510)
    steep = [(d0, 400), (d0 + dt.timedelta(days=14), 500), (d0 + dt.timedelta(days=28), 600)]
    a = project(steep, d0 + dt.timedelta(days=28 + 7 * 10))["mid"]
    b = project(steep, d0 + dt.timedelta(days=28 + 7 * 11))["mid"]
    assert b - a <= 20 + 1
    assert project(steep[:2], d0 + dt.timedelta(days=60)) is None
    three = project([(dt.date(2026, 9, 1), 500), (dt.date(2026, 9, 15), 560), (dt.date(2026, 9, 22), 600)],
                    dt.date(2026, 11, 7), 70)        # api_today still passes a half; it no longer widens anything
    assert three["mid"] < 700 and abs(three["mid"] - 683) <= 3 and three["high"] - three["low"] == 20, three
    top = project([(d0, 760), (d0 + dt.timedelta(days=14), 790), (d0 + dt.timedelta(days=28), 800)], d0 + dt.timedelta(days=90))
    assert (top["low"], top["high"]) == (780, 800), top
    assert scoring.total_band(745, 752) == {"low": 1490, "high": 1510, "mid": 1497}
    # current(): one sitting keeps its own band; three are the band of their mean; all capped stays under 580
    def sat(mid_, capped=False, outside=False, at="2026-10-0"):
        b = scoring.section_band(mid_, "lower" if capped else None)
        return {**b, "id": f"s{mid_}", "outside": outside, "at": at, "source": "bluebook" if outside else None}
    one = current("x", "math", [sat(612.4)])
    assert (one["low"], one["high"], one["mid"], one["n"], one["source"]) == (600, 620, 612.4, 1, "measured")
    three = current("x", "math", [sat(640), sat(600), sat(560), sat(400)])
    assert (three["low"], three["high"], three["mid"], three["n"]) == (590, 610, 600, 3), three
    capped = current("x", "math", [sat(640, True), sat(620, True), sat(600, True)])
    assert capped["high"] <= 580 and capped["capped"] and capped["mid"] == 580, capped
    assert not current("x", "math", [sat(640, True), sat(600)])["capped"]
    old = [{"id": "o1", "low": 500, "high": 640, "at": "2026-09-01"}, {"id": "o2", "low": 560, "high": 580, "at": "2026-08-01"}]
    assert (current("x", "math", old[:1])["mid"], current("x", "math", old)["low"]) == (570, 560)   # pre-migration shape
    logged = current("x", "rw", [sat(650, outside=True)])
    assert (logged["low"], logged["high"], logged["source"], logged["id"]) == (640, 660, "bluebook", None)
    t = scoring.total_band(three["mid"], logged["mid"])
    assert (t["low"], t["high"]) == (1240, 1260)
    # SR1: Shapley shares sum to the whole and ignore labels
    v = lambda s: {frozenset(): 0, frozenset("a"): 10, frozenset("b"): 20, frozenset("ab"): 40}[s]  # noqa: E731
    sh = _shapley(v, ["a", "b"])
    assert abs(sum(sh.values()) - 40) < 1e-9 and abs(sh["a"] - 15) < 1e-9 and abs(sh["b"] - 25) < 1e-9
    assert sum(_largest_remainder({"a": 12.4, "b": 7.9, "c": 0.0}).values()) == _round5(20.3)
    print("estimate ok")
