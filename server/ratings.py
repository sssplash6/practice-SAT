"""Item and skill ratings (practice.md P11, compete.md C13): one Elo-style rule
for every mode.

An item is a (template, tier); a learner has one rating per topic in
`skill_ratings`, separate from Compete's single `learners.rating`. The odds of
a right answer are E = 1 / (1 + 10^((Ri - Rs) / 400)), and every clean first
try moves both sides by the same surprise, S - E.

Priors, so levels 1-7 mean something before anyone has answered. Three
specs set them and disagree (compete.md C13, review.md V15, practice.md P11);
this is the reconciliation, and the one rule seed_ratings and startup share:
* structural (C13's signal): each pair's score over 18 seeds is +50 for a
  grid-in (V15's "SPR one step harder"), +25 with a figure or table, and +25
  per rationale sentence above the tier's median (-25 below). Taken raw, as
  C13 writes it, the bank's rationales are mostly one sentence and the scores
  bunch: L1 and L3 get 0% and L5 3.5%, failing V15's 5%-per-level assert. So
  the score only ranks a tier's pairs, and the rank places each in the tier's
  SPREAD, which keeps C13's "within 150 of the tier" and ">= 8 distinct per
  tier" and V15's ">= 5% of types at every level". V15's P1 step count is not
  a field any Item has, so it is not used.
* measured (V15's n >= 5 first tries, C13's formula and shrinkage): the
  answerers' mean skill rating less 400 log10(p / (1 - p)), p clamped to
  0.05-0.95, shrunk toward the structural prior by n / (n + 20), so 5 answers
  move it a fifth of the way and 20 half.
`ponytail:` College Board's own score bands (P11: material/cb_index.json,
T-bank's cb-index task) replace the structural prior once that file and U2's
map exist.
"""

from __future__ import annotations

if __package__ in (None, ""):                     # python3 server/ratings.py
    import pathlib
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    __package__ = "server"

import datetime as dt
import math
import re
import statistics
from collections import defaultdict

from . import db

TIER_PRIOR = {"easy": 900.0, "medium": 1100.0, "hard": 1300.0}
EDGES = (850, 1000, 1075, 1150, 1225, 1350)      # L1 < 850 <= L2 < 1000 ... <= L7
MEASURED = 20                                     # answers before a level is "measured"
PRIOR_FROM = 5                                    # first tries before they move a prior (V15)
PLACED = 8                                        # clean first tries before a skill is aimed at
SURVEY_SEEDS = 18


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def expected(item_rating: float, skill_rating: float) -> float:
    return 1 / (1 + 10 ** ((item_rating - skill_rating) / 400))


def level_of(rating: float) -> int:
    return 1 + sum(rating >= e for e in EDGES)


def item(template: str, tier: str) -> tuple[float, int]:
    r = db.one("SELECT rating,n FROM item_ratings WHERE template=? AND tier=?", template, tier)
    return (r["rating"], r["n"]) if r else (TIER_PRIOR.get(tier, 1100.0), 0)


def level(template: str, tier: str) -> dict:
    rating, n = item(template, tier)
    return {"level": level_of(rating), "rating": round(rating), "n": n, "rough": n < MEASURED}


def _seed_rating(learner: str) -> tuple[float, str]:
    row = db.one("SELECT current FROM learners WHERE id=?", learner)
    if row and row["current"]:
        return max(700.0, min(1500.0, 1100 + 1.2 * (row["current"] - 530))), "score"
    return 1000.0, "none"


def skill(learner: str, topic: str, seed: str | None = None) -> dict:
    """This learner's rating in a topic, made on first use from the best
    evidence there is: a probe (seed 'probe'), the starting score, or 1000."""
    r = db.one("SELECT rating,n,seed FROM skill_ratings WHERE learner=? AND topic=?", learner, topic)
    if r:
        return dict(r)
    rating, how = _seed_rating(learner)
    if db.is_sample(learner):
        return {"rating": rating, "n": 0, "seed": seed or how}
    db.run("INSERT OR IGNORE INTO skill_ratings(learner,topic,rating,n,seed) VALUES (?,?,?,0,?)",
           learner, topic, rating, seed or how)
    return {"rating": rating, "n": 0, "seed": seed or how}


def placed(learner: str, topic: str) -> bool:
    s = skill(learner, topic)
    return s["n"] >= PLACED or s["seed"] == "probe"


def odds(learner: str, template: str, tier: str, topic: str | None = None) -> float:
    from satbank.registry import topic_of
    return expected(item(template, tier)[0], skill(learner, topic or topic_of(template))["rating"])


def snapshot(learner: str, questions: list[dict]) -> dict:
    """{qid: E} for a sitting, read before its answers move the ratings."""
    return {q["id"]: round(odds(learner, q["key"], q["difficulty"], q.get("topic")), 3)
            for q in questions if "key" in q}


def update(learner: str, template: str, tier: str, topic: str, right: bool,
           placement: bool = False) -> None:
    """One clean first try. The caller decides clean (progress.record does)."""
    if db.is_sample(learner):
        return
    s = skill(learner, topic)
    ri, ni = item(template, tier)
    e = expected(ri, s["rating"])
    surprise = (1.0 if right else 0.0) - e
    ks = 32 if placement or s["n"] < 30 else 16
    ki = max(4.0, 32 / math.sqrt(ni + 1))
    db.run("UPDATE skill_ratings SET rating=?, n=n+1 WHERE learner=? AND topic=?",
           s["rating"] + ks * surprise, learner, topic)
    db.run("INSERT INTO item_ratings(template,tier,rating,n) VALUES (?,?,?,1)"
           " ON CONFLICT(template,tier) DO UPDATE SET rating=excluded.rating, n=item_ratings.n+1",
           template, tier, ri - ki * surprise)


# ------------------------------------------------------------------ priors

_SENTENCE = re.compile(r"[.!?](?:\s|$)")


# Each tier's pairs are spread over this range by their structural rank, so
# the seven levels are all populated on day one (V15) while every prior stays
# within 150 of its tier (C13).
SPREAD = {"easy": (760.0, 1045.0), "medium": (960.0, 1240.0), "hard": (1160.0, 1440.0)}


def structural_priors(seeds: int = SURVEY_SEEDS) -> dict[tuple[str, str], float]:
    """C13's prior for every (template, tier) the bank can make: the structural
    score (+50 a grid-in, +25 a figure or table, +25 per rationale sentence
    above the tier's median) ranks the pairs of a tier, and the rank places
    each in the tier's SPREAD."""
    from satbank.registry import generate, templates
    seen: dict[tuple[str, str], list[tuple[int, int, int]]] = defaultdict(list)
    for t in templates():
        for seed in range(seeds):
            try:
                it = generate(t, seed)
            except Exception:
                continue
            sentences = max(1, len(_SENTENCE.findall(it.rationale or "")))
            seen[(t, it.difficulty)].append((it.fmt == "spr", bool(it.figure or it.table), sentences))
    median = {tier: statistics.median([s for (t, ti), rows in seen.items() if ti == tier for *_, s in rows] or [1])
              for tier in TIER_PRIOR}
    out = {}
    for tier, (lo, hi) in SPREAD.items():
        scored = sorted((statistics.mean(50 * spr + 25 * pic + 25 * (s - median[tier]) for spr, pic, s in rows), t)
                        for (t, ti), rows in seen.items() if ti == tier)
        for i, (_, t) in enumerate(scored):
            out[(t, tier)] = lo + (hi - lo) * (i + 0.5) / len(scored)
    return out


def histogram() -> dict[int, float]:
    """The share of (template, tier) types at each level, from item_ratings."""
    rows = db.rows("SELECT rating FROM item_ratings")
    counts = {lv: 0 for lv in range(1, 8)}
    for r in rows:
        counts[level_of(r["rating"])] += 1
    return {lv: round(n / len(rows), 3) if rows else 0.0 for lv, n in counts.items()}


def measured_prior(template: str, tier: str, toward: float | None = None) -> float | None:
    """From the clean first tries on the pair, once there are 5 of them,
    shrunk toward `toward` (the structural prior; the tier's by default)."""
    rows = db.rows("SELECT a.correct, COALESCE(s.rating, 1000) AS rs FROM attempts AS a"
                   " LEFT JOIN skill_ratings AS s ON s.learner=a.learner AND s.topic=a.topic"
                   " WHERE a.template=? AND a.difficulty=? AND a.repeat=0 AND a.guess=0 AND a.hints=0"
                   " AND a.void IS NULL AND a.disputed=0 AND COALESCE(a.conf,'')!='unsure'"
                   f" AND a.{db.NOT_SAMPLE}", template, tier)
    n = len(rows)
    if n < PRIOR_FROM:
        return None
    p = min(0.95, max(0.05, sum(r["correct"] for r in rows) / n))
    raw = statistics.mean(r["rs"] for r in rows) - 400 * math.log10(p / (1 - p))
    w = n / (n + MEASURED)
    return w * raw + (1 - w) * (TIER_PRIOR.get(tier, 1100.0) if toward is None else toward)


def write_priors() -> int:
    """Priors for every pair that has no answers yet. Idempotent."""
    n = 0
    priors = structural_priors()
    with db.atomic():
        for (t, tier), prior in priors.items():
            measured = measured_prior(t, tier, prior)
            prior = prior if measured is None else measured
            n += db.run("INSERT INTO item_ratings(template,tier,rating,n) VALUES (?,?,?,0)"
                        " ON CONFLICT(template,tier) DO UPDATE SET rating=excluded.rating"
                        " WHERE item_ratings.n=0", t, tier, prior).rowcount
    return n


def replay() -> int:
    """Every clean first try on file, in order, as if filed today."""
    n = 0
    with db.atomic():
        for a in db.rows("SELECT learner,template,difficulty,topic,correct FROM attempts"
                         " WHERE repeat=0 AND guess=0 AND hints=0 AND void IS NULL AND disputed=0"
                         " AND flagged=0 AND COALESCE(conf,'')!='unsure'"
                         f" AND {db.NOT_SAMPLE} ORDER BY id"):
            update(a["learner"], a["template"], a["difficulty"], a["topic"], bool(a["correct"]))
            n += 1
    return n


def backfill() -> None:
    """Startup: priors once, then the replay once (kv flags)."""
    for flag, fn in (("backfill:item_priors", write_priors), ("backfill:ratings", replay)):
        if db.one("SELECT 1 FROM kv WHERE k=?", flag):
            continue
        fn()
        db.run("INSERT OR REPLACE INTO kv(k,v) VALUES (?,?)", flag, now())


if __name__ == "__main__":
    # a right answer never lowers Rs; the two updates are symmetric in E
    for ri, rs in ((900, 1000), (1300, 1000), (1100, 1500)):
        e = expected(ri, rs)
        assert 0 < e < 1 and abs(expected(rs, ri) - (1 - e)) < 1e-12
        assert rs + 32 * (1 - e) >= rs and rs + 32 * (0 - e) <= rs
    assert [level_of(r) for r in (800, 900, 1037, 1112, 1187, 1287, 1400)] == [1, 2, 3, 4, 5, 6, 7]
    assert level_of(TIER_PRIOR["easy"]) == 2 and level_of(TIER_PRIOR["medium"]) == 4
    assert level_of(TIER_PRIOR["hard"]) == 6
    assert round(max(700, min(1500, 1100 + 1.2 * (700 - 530)))) == 1304
    priors = structural_priors()
    for tier in TIER_PRIOR:
        values = sorted({round(v) for (t, ti), v in priors.items() if ti == tier})
        print(f"{tier}: {len(values)} distinct priors, {values[0]}..{values[-1]}")
        assert len(values) >= 8, tier
        assert all(abs(v - TIER_PRIOR[tier]) <= 150 for v in values)
    levels = [level_of(v) for v in priors.values()]
    shares = {lv: levels.count(lv) / len(levels) for lv in range(1, 8)}
    print("levels:", {lv: f"{100 * sh:.0f}%" for lv, sh in shares.items()})
    assert all(sh >= 0.05 for sh in shares.values()), shares
    print("ratings ok")
