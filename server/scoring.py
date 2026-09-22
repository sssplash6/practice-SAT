"""Marking a diagnostic, and saying only what sixteen questions can support.

What the College Board actually does, and what this cannot copy: the digital
SAT is scored by item response theory, not by counting. A student's section
score comes from a maximum-likelihood ability estimate over items whose
difficulty, discrimination and guessing parameters were calibrated on real
test-takers beforehand. There is no published raw-to-scaled conversion table,
and there cannot be one, because two students with the same number correct can
score differently depending on which questions they got right.

None of those parameters are public. So the weights below are an ORDINAL
HEURISTIC over the College Board's own easy/medium/hard labels, which are
published on their question bank. Calling this IRT would be the one claim here
that is actually false.

The size of the band is not modesty either. The real test reports a standard
error near 20 points per section off ninety calibrated, adaptively targeted
items. This has sixteen, none calibrated, with no adaptivity. Scaling that
error by the square root of the question count puts one standard error near 50
points, so a band narrower than 200 points would be pretending.

Per domain it is worse, and the College Board says so itself: a domain scored
off four items has low precision, and a strong student can look weak in a hard
domain by chance. That is why a domain gets a bar and a word, never a number,
and why the copy says where to practise next rather than what you are bad at.
"""

from __future__ import annotations

# The published labels, turned into an ordinal weight. A hard question answered
# correctly says more than an easy one; how much more is a judgement call.
WEIGHT = {"easy": 1, "medium": 2, "hard": 3}

# one easy, two medium, one hard per domain
DOMAIN_MAX = WEIGHT["easy"] + 2 * WEIGHT["medium"] + WEIGHT["hard"]   # 8

BANDS = (
    (0.00, "Start here",  "Worth building the basics of this domain first."),
    (0.35, "Building",    "The ideas are landing. Repetition is what is missing."),
    (0.65, "Steady",      "Solid on the routine questions. The hard ones are next."),
    (0.90, "Strong",      "Little to fix here. Spend the time elsewhere."),
)

# Anchors on the 200-800 section scale, linearly interpolated between. Invented,
# and stated as invented. Four options mean blind guessing earns about a
# quarter of the weight, so a quarter is where the scale should start to mean
# anything; half the weight sits near the national mean; and everything right
# including the hard items sits high but short of the ceiling, because sixteen
# questions cannot evidence an 800.
ANCHORS = ((0.0, 200.0), (0.25, 300.0), (0.5, 480.0), (0.75, 620.0), (1.0, 780.0))

HALF_BAND = 100             # a 200-point band, per the note above


def normalise(text: str) -> str:
    """Grid-in answers are compared without the decoration a student may add."""
    return (text or "").strip().replace(",", "").replace(" ", "").lstrip("$").rstrip(".")


def is_correct(question: dict, given) -> bool:
    if given is None or given == "":
        return False
    if question["type"] == "mcq":
        # the client sends the index it highlighted; the bank keys a letter
        if not isinstance(given, int) or not 0 <= given < 4:
            return False
        return "ABCD"[given] == question["answer"]
    return normalise(str(given)) == normalise(question["answer"])


def band_for(fraction: float) -> tuple[str, str]:
    name, note = BANDS[0][1], BANDS[0][2]
    for edge, n, t in BANDS:
        if fraction >= edge:
            name, note = n, t
    return name, note


def _interpolate(x: float) -> float:
    for (x0, y0), (x1, y1) in zip(ANCHORS, ANCHORS[1:]):
        if x <= x1:
            span = x1 - x0
            return y0 + (y1 - y0) * ((x - x0) / span if span else 0)
    return ANCHORS[-1][1]


def score(questions: list[dict], answers: dict) -> dict:
    """Mark the sixteen, and report per domain plus one wide band."""
    domains: dict[str, dict] = {}
    earned = possible = 0

    for q in questions:
        d = domains.setdefault(
            q["domain"],
            {"domain": q["domain"], "right": 0, "asked": 0, "earned": 0,
             "possible": 0, "missed": []},
        )
        w = WEIGHT[q["difficulty"]]
        ok = is_correct(q, answers.get(q["id"]))
        d["asked"] += 1
        d["possible"] += w
        possible += w
        if ok:
            d["right"] += 1
            d["earned"] += w
            earned += w
        else:
            d["missed"].append({"topic": q["topic_name"], "difficulty": q["difficulty"]})

    for d in domains.values():
        frac = d["earned"] / d["possible"] if d["possible"] else 0.0
        d["mastery"] = round(frac, 3)
        d["band"], d["note"] = band_for(frac)
        # the topics to look at first, worst-hit first, named once each
        seen, focus = set(), []
        for m in sorted(d["missed"], key=lambda m: -WEIGHT[m["difficulty"]]):
            if m["topic"] not in seen:
                seen.add(m["topic"])
                focus.append(m["topic"])
        d["focus"] = focus[:2]
        d.pop("missed")

    raw = earned / possible if possible else 0.0
    centre = _interpolate(raw)
    low = max(200, int(round((centre - HALF_BAND) / 10) * 10))
    high = min(800, int(round((centre + HALF_BAND) / 10) * 10))

    order = ["Algebra", "Advanced Math",
             "Problem-Solving and Data Analysis", "Geometry and Trigonometry"]
    return {
        "right": sum(d["right"] for d in domains.values()),
        "asked": sum(d["asked"] for d in domains.values()),
        "estimate": {"low": low, "high": high, "section": "Math", "scale": [200, 800]},
        "domains": [domains[k] for k in order if k in domains],
    }
