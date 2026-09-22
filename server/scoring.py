"""Marking a diagnostic, and saying only what twenty questions can support.

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
items. This has twenty, none calibrated, with no adaptivity. Scaling that
error by the square root of the question count puts one standard error near 45
points, so a band narrower than 200 points would be pretending.

Per domain it is worse, and the College Board says so itself: a domain scored
off a handful of items has low precision, and a strong student can look weak in
a hard domain by chance. That is why a domain gets a bar and a word, never a number,
and why the copy says where to practise next rather than what you are bad at.
"""

from __future__ import annotations

import math

from satbank.item import norm_text, numeral

# The published labels, turned into an ordinal weight. A hard question answered
# correctly says more than an easy one; how much more is a judgement call.
WEIGHT = {"easy": 1, "medium": 2, "hard": 3}

# one easy, two medium, two hard per domain. Not used in the marking, which
# accumulates what each domain actually carried, but it is the number the bands
# below are pitched against.
DOMAIN_MAX = WEIGHT["easy"] + 2 * WEIGHT["medium"] + 2 * WEIGHT["hard"]   # 11

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
# including the hard items sits high but short of the ceiling, because twenty
# questions cannot evidence an 800.
ANCHORS = ((0.0, 200.0), (0.25, 300.0), (0.5, 480.0), (0.75, 620.0), (1.0, 780.0))

HALF_BAND = 100             # a 200-point band, per the note above


# ---------------------------------------------------------------- the mock
#
# Routing. The College Board sets the cut between the two second modules at the
# median of archival test scores -- half the population each way -- and says so
# in the Technical Manual, but does not publish the threshold itself, nor how
# it weights the module's items. The "miss two or three and you route down"
# figure that circulates is third-party and has no source behind it.
#
# So this is a stated choice, not a reported fact: above sixty per cent of a
# mixed-difficulty first module routes up. A median SAT Math score sits near
# 520 of 800, and a student there gets a little over half of a module spanning
# the full difficulty range.
ROUTE_UP_AT = 0.60

# What a low route costs. The Technical Manual simulates a student who takes
# the lower second module and answers every question in it correctly, and
# reports they "would, at most, earn a 580" on Math. That is the College
# Board's own number for the ceiling, so it is the one used here.
LOWER_ROUTE_CEILING = 580

# A mock is 44 questions against the diagnostic's 20, so its band is narrower
# by the square root of the ratio. It is not as narrow as the real test's 20
# points, because none of these items are calibrated on real test-takers.
MOCK_HALF_BAND = 70


def route_after(right: int, asked: int) -> str:
    """Which second module this performance earns. See ROUTE_UP_AT."""
    return "upper" if asked and (right / asked) >= ROUTE_UP_AT else "lower"


def section_score(result: dict, route: str | None) -> dict:
    """A Math section score from both modules, with the route's ceiling applied."""
    earned = sum(d["earned"] for d in result["domains"])
    possible = sum(d["possible"] for d in result["domains"])
    centre = _interpolate(earned / possible if possible else 0.0)

    low = max(200, int(round((centre - MOCK_HALF_BAND) / 10) * 10))
    high = min(800, int(round((centre + MOCK_HALF_BAND) / 10) * 10))
    capped = False
    if route == "lower" and high > LOWER_ROUTE_CEILING:
        high = LOWER_ROUTE_CEILING
        low = min(low, high - 10)
        capped = True
    return {"low": low, "high": high, "section": "Math", "scale": [200, 800],
            "route": route, "capped": capped}


def normalise(text: str) -> str:
    """Grid-in answers are compared without the decoration a student may add."""
    return (text or "").strip().replace(",", "").replace(" ", "").lstrip("$").rstrip(".")


def _value(text: str) -> float | None:
    return numeral(str(text).strip().replace("−", "-").replace(" ", "").lstrip("+"))


def grid_equal(given: str, key: str) -> bool:
    """Whether a typed grid-in answer is the keyed one, the way the SAT marks it.

    The same number written another way counts: 0.125 is 1/8, 2/4 is 1/2, a
    typeset minus is a keyboard one. And a decimal too long for the grid counts
    when it is truncated or rounded at the fourth digit, so 2/3 accepts .6666,
    .6667, 0.666 and 0.667 -- but not 0.66, which stops short of filling it.
    That is College Board's own rule, printed in the grid-in directions.
    """
    g = (given or "").strip()
    if not g:
        return False
    if normalise(g) == normalise(key) or norm_text(g) == norm_text(key):
        return True
    gv, kv = _value(g), _value(key)
    if gv is None or kv is None:
        return False
    if math.isclose(gv, kv, rel_tol=0, abs_tol=1e-9):
        return True
    body = g.replace("−", "-").lstrip("-")
    if "." in body and "/" not in body and len(body) >= 5:
        scale = 10 ** len(body.split(".", 1)[1])
        cut = math.trunc(kv * scale) / scale
        near = math.copysign(math.floor(abs(kv) * scale + 0.5) / scale, kv)
        return math.isclose(gv, cut, abs_tol=1e-9) or math.isclose(gv, near, abs_tol=1e-9)
    return False


def is_correct(question: dict, given) -> bool:
    if given is None or given == "":
        return False
    if question["type"] == "mcq":
        # the client sends the index it highlighted; the bank keys a letter
        if not isinstance(given, int) or not 0 <= given < 4:
            return False
        return "ABCD"[given] == question["answer"]
    return grid_equal(str(given), str(question["answer"]))


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
    """Mark the paper, and report per domain plus one wide band."""
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
