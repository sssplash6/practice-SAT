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

Nor is the range a confidence interval. The real test reports a standard error
near 20 points per section off calibrated, adaptively targeted items; none of
these items are calibrated, so the true uncertainty here is wider than what is
shown. The owner's choice (2026-10-22) is to show every score as its centre
+- 10 all the same: an estimate from this site's questions, never a College
Board score.

Per domain it is worse, and the College Board says so itself: a domain scored
off a handful of items has low precision, and a strong student can look weak in
a hard domain by chance. That is why a domain gets a bar and a word, never a number,
and why the copy says where to practise next rather than what you are bad at.
"""

from __future__ import annotations

import math
import re
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from fractions import Fraction

from satbank.item import fold_entry, norm_text, numeral

# The published labels, turned into an ordinal weight. A hard question answered
# correctly says more than an easy one; how much more is a judgement call.
WEIGHT = {"easy": 1, "medium": 2, "hard": 3}
RW_DOMAINS = ("Information and Ideas", "Craft and Structure", "Expression of Ideas", "Standard English Conventions")

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

# The owner's rule (2026-10-22): every range shown is at most 20 points wide, centre +- 10. It is a
# display precision, not a confidence interval; band() and total_band() are the only places a width is made.
HALF = 10
HALF_BAND = HALF


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
# R&W has no published figure; 580 mirrors Math as a stated choice until there is one.
CEILING = {"math": LOWER_ROUTE_CEILING, "rw": LOWER_ROUTE_CEILING}
SECTION_NAME = {"math": "Math", "rw": "Reading and Writing"}

# A name older callers still read; a section's band is as wide as any other now.
MOCK_HALF_BAND = HALF


def route_after(right: int, asked: int) -> str:
    """Which second module this performance earns. See ROUTE_UP_AT."""
    return "upper" if asked and (right / asked) >= ROUTE_UP_AT else "lower"


def band(centre: float, scale: tuple[int, int] = (200, 800)) -> dict:
    """The one range: centre +- HALF, each end on a multiple of 10, inside the scale. Always 20 wide;
    at the scale's edge it slides inside (800 gives 780-800)."""
    lo_s, hi_s = scale
    mid = int(round(min(max(centre, lo_s), hi_s) / 10) * 10)
    low, high = max(lo_s, mid - HALF), min(hi_s, mid + HALF)
    if high - low < 2 * HALF:                   # pushed against an edge: keep the width inside the scale
        low, high = (lo_s, lo_s + 2 * HALF) if low == lo_s else (hi_s - 2 * HALF, hi_s)
    return {"low": low, "high": high, "mid": round(centre, 1)}


def total_band(rw_mid: float, math_mid: float) -> dict:
    """A 400-1600 total: the sum of the two section centres +- HALF, never the sum of two ranges."""
    return band(rw_mid + math_mid, (400, 1600))


def section_band(centre: float, route: str | None, subject: str = "math") -> dict:
    """band(centre) with the lower route's ceiling: a capped band is the 20 points under the ceiling and
    its mid is the centre held at the ceiling, so points below the cap still move it."""
    b = band(centre)
    ceiling = CEILING.get(subject, LOWER_ROUTE_CEILING)
    if route == "lower" and b["high"] > ceiling:
        return {"low": ceiling - 2 * HALF, "high": ceiling, "mid": min(b["mid"], ceiling), "capped": True}
    return {**b, "capped": False}


def section_score(result: dict, route: str | None, subject: str | None = None) -> dict:
    """A section score from both modules, with the route's ceiling applied."""
    subject = subject or result.get("subject") or "math"
    earned = sum(d["earned"] for d in result["domains"])
    possible = sum(d["possible"] for d in result["domains"])
    b = section_band(_interpolate(earned / possible if possible else 0.0), route, subject)
    return {**b, "section": SECTION_NAME.get(subject, "Math"), "scale": [200, 800], "route": route}


def normalise(text: str) -> str:
    """Grid-in answers are compared without the decoration a student may add."""
    return (text or "").strip().replace(",", "").replace(" ", "").lstrip("$").rstrip(".")


def _value(text: str) -> float | None:
    return numeral(fold_entry(str(text).strip()).replace(" ", "").lstrip("+"))


def keys(key: str) -> list[str]:
    """A key that lists every right answer, the way CB's keys do: "12, 18, 33"."""
    parts = re.split(r",\s+", str(key))
    return parts if len(parts) > 1 and all(_value(k) is not None for k in parts) else [str(key)]


def grid_equal(given: str, key: str) -> bool:
    """Whether a typed grid-in answer is the keyed one, the way the SAT marks it.

    The same number written another way counts: 0.125 is 1/8, 2/4 is 1/2, a
    typeset minus is a keyboard one. And a decimal too long for the grid counts
    when it is truncated or rounded at the fourth digit, so 2/3 accepts .6666,
    .6667, 0.666 and 0.667 -- but not 0.66, which stops short of filling it.
    That is College Board's own rule, printed in the grid-in directions.
    """
    if len(ks := keys(key)) > 1:
        return any(grid_equal(given, k) for k in ks)
    g, key = fold_entry((given or "").strip()), fold_entry(key)
    if not g:
        return False
    if normalise(g) == normalise(key) or norm_text(g) == norm_text(key):
        return True
    gv, kv = _value(g), _value(key)
    if gv is None or kv is None:
        return False
    if math.isclose(gv, kv, rel_tol=0, abs_tol=1e-9):
        return True
    body = fold_entry(g).lstrip("-")
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


def fraction_for(score: float) -> dict:
    """Invert the published heuristic anchors for the score explanation."""
    if score >= ANCHORS[-1][1]:
        return {"fraction": 1.0, "capped": score > ANCHORS[-1][1]}
    if score <= ANCHORS[0][1]:
        return {"fraction": 0.0, "capped": False}
    for (x0,y0),(x1,y1) in zip(ANCHORS,ANCHORS[1:]):
        if y0 <= score <= y1:
            return {"fraction": x0+(score-y0)*(x1-x0)/(y1-y0), "capped": False}
    raise AssertionError("unreachable score anchor")


def _exact(text) -> Fraction | None:
    """A typed or keyed number as an exact rational: 2/3, 0.125, -7, 1.5e0 no."""
    if len(keys(str(text or ""))) > 1:
        return None
    t = fold_entry(str(text or "").strip()).replace(",", "").replace(" ", "").lstrip("+")
    if not t:
        return None
    try:
        return Fraction(t)
    except (ValueError, ZeroDivisionError):
        return None


def _grid_cap(text: str) -> int:
    """The grid holds 5 characters, 6 with a leading minus."""
    return 6 if text.startswith("-") else 5


def _fill(value: Fraction, places: int, rounding: str) -> str:
    """value (>= 0) cut or rounded at `places` decimal places."""
    d = Decimal(value.numerator) / Decimal(value.denominator)
    return str(d.quantize(Decimal(1).scaleb(-places), rounding=rounding))


def accepted_forms(key: str) -> list[str]:
    """Up to 5 ways to grid the key that grid_equal accepts: the fraction, then
    the decimal -- exact when it ends in time, else truncated and rounded to
    fill the grid (5 characters, 6 with a minus) -- without and with the
    leading 0. 2/3 -> 2/3, .6666, .6667, 0.666, 0.667; 7/3 -> 7/3, 2.333.
    A key listing several answers gives each one's forms."""
    if len(ks := keys(key)) > 1:
        return [f for k in ks for f in accepted_forms(k)]
    value = _exact(key)
    if value is None:
        return []
    forms: list[str] = []

    def add(s: str) -> None:
        if s not in forms and len(s) <= _grid_cap(s) and grid_equal(s, str(key)):
            forms.append(s)

    sign = "-" if value < 0 else ""
    a = abs(value)
    whole = a.numerator // a.denominator
    if a.denominator == 1:
        add(f"{sign}{whole}")
        return forms
    add(f"{value.numerator}/{value.denominator}")
    exact = Decimal(a.numerator) / Decimal(a.denominator)
    ends = Fraction(exact) == a
    for head in (("", "0") if whole == 0 else (str(whole),)):
        places = _grid_cap(sign) - len(sign) - len(head) - 1
        if places < 1:
            continue
        digits = str(exact).split(".", 1)[1] if "." in str(exact) else ""
        if ends and len(digits) <= places:
            add(f"{sign}{head}.{digits}")
            continue
        for rounding in (ROUND_DOWN, ROUND_HALF_UP):
            q = str(exact.quantize(Decimal(1).scaleb(-places), rounding=rounding))
            add(f"{sign}{head}.{q.split('.', 1)[1]}" if q.split(".")[0] == str(whole) else sign + q)
    return forms[:5]


def entry_error(given: str, key: str) -> str | None:
    """T7's entry cause, exact equivalence only.

    'form': the value is the key's, written the way the grid refuses: a mixed
    number (1 1/2 for 3/2) or more than 5 characters (6 with a minus).
    'early': a decimal that stops short -- a point, no slash, at least two
    significant digits, fewer characters than the grid holds -- equal to the
    key truncated or rounded at its own number of places (.66 or .67 for 2/3,
    1.2 for 1.25). A nearby number is never entry.
    """
    g = fold_entry((given or "").strip())
    kv = _exact(key)
    if not g or kv is None or grid_equal(g, str(key)):
        return None
    mixed = re.fullmatch(r"(-?)(\d+)\s+(\d+)/(\d+)", g)
    if mixed and int(mixed[4]):
        whole = int(mixed[2]) + Fraction(int(mixed[3]), int(mixed[4]))
        return "form" if (-whole if mixed[1] else whole) == kv else None
    gv = _exact(g)
    if gv is None:
        return None
    if gv == kv and len(g.replace(" ", "")) > _grid_cap(g):
        return "form"
    body = g.lstrip("-")
    if "." in body and "/" not in body and len(g) < _grid_cap(g):
        digits = body.replace(".", "").lstrip("0")
        places = len(body.split(".", 1)[1])
        if len(digits) >= 2 and places and gv != kv:
            cut = Fraction(_fill(abs(kv), places, ROUND_DOWN))
            near = Fraction(_fill(abs(kv), places, ROUND_HALF_UP))
            if (gv < 0) == (kv < 0) and abs(gv) in (cut, near):
                return "early"
    return None


def grid_diagnose(given: str, key: str, spr_reasons=None) -> dict | None:
    """SR10: why a typed grid-in failed, first match; None when it is simply a
    different value, not a named mistake."""
    g = fold_entry((given or "").strip())
    kv, gv = _exact(key), _exact(g)
    if not g or kv is None or grid_equal(g, str(key)):
        return None
    shown = " or ".join(accepted_forms(key)[:2]) or str(key)
    err = entry_error(g, key)
    if err == "form":
        return {"kind": "form", "text": f"Right value, in a form the grid refuses: enter {shown}."}
    if gv is not None and kv and (err == "early" or (abs(gv - kv) <= abs(kv) / 100
                                                     and "." in g and "/" not in g and len(g) < _grid_cap(g))):
        decimals = [f for f in accepted_forms(key) if "/" not in f][:2]
        return {"kind": "short", "text": f"Right value, too few digits: {key} needs {' or '.join(decimals) or shown}."}
    if gv is not None:
        if kv and gv == -kv:
            return {"kind": "sign", "text": "Right size, wrong sign."}
        if kv and gv in (kv * 100, kv / 100):
            return {"kind": "percent", "text": "Off by a factor of 100: percent and decimal mixed up."}
        if kv and gv in (kv * 10, kv / 10):
            return {"kind": "ten", "text": "Off by a factor of 10: check the place value."}
    for item in spr_reasons or ():
        if isinstance(item, (list, tuple)) and len(item) >= 2 and grid_equal(g, str(item[1])):
            return {"kind": "named", "text": str(item[0])}
    return None


assert accepted_forms("2/3") == ["2/3", ".6666", ".6667", "0.666", "0.667"]
assert accepted_forms("7/3") == ["7/3", "2.333"] and accepted_forms("-7/3") == ["-7/3", "-2.333"]
assert accepted_forms("100/3") == ["100/3", "33.33"] and accepted_forms("1/8") == ["1/8", ".125", "0.125"]
assert accepted_forms("12, 18, 33") == ["12", "18", "33"] and grid_equal("18", "12, 18, 33")
assert not grid_equal("121833", "12, 18, 33") and grid_equal("1,000", "1000") and grid_diagnose("32", "12, 18, 33") is None
assert accepted_forms("12") == ["12"] and all(grid_equal(f, "2/3") for f in accepted_forms("2/3"))
for g in (".66", "0.66", ".67"):
    assert entry_error(g, "2/3") == "early", g
assert entry_error("1.2", "1.25") == "early" and entry_error("1 1/2", "3/2") == "form"
assert [entry_error(g, k) for g, k in (("455", "460"), ("154", "150"), (".7", "2/3"), ("3", "3.5"),
                                       (".6667", "2/3"))] == [None] * 5
assert grid_diagnose("0.66", "2/3")["kind"] == "short" and grid_diagnose("1 1/2", "3/2")["kind"] == "form"
assert grid_diagnose("-7", "7")["kind"] == "sign" and grid_diagnose("45", "0.45")["kind"] == "percent"
assert grid_diagnose("12", "8") is None


def score(questions: list[dict], answers: dict) -> dict:
    """Mark the paper, and report per domain plus one band."""
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
    est = band(_interpolate(raw))

    order = ["Algebra", "Advanced Math",
             "Problem-Solving and Data Analysis", "Geometry and Trigonometry",
             *RW_DOMAINS]
    return {
        "right": sum(d["right"] for d in domains.values()),
        "asked": sum(d["asked"] for d in domains.values()),
        "estimate": {"low": est["low"], "high": est["high"], "mid": est["mid"], "scale": [200, 800],
                     "section": SECTION_NAME["rw" if any(q["domain"] in RW_DOMAINS for q in questions) else "math"]},
        "domains": [domains[k] for k in order if k in domains],
    }
