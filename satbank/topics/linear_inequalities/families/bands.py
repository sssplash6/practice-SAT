"""A quantity trapped between two numbers, and what happens to that band when
the quantity is scaled, offset or divided into something else.

Eight of the official items are this shape. The band itself is never the hard
part: what the source tests is whether the two ends travel together. Multiply
by a positive number and the ends keep their order; divide *by* the band and
they change places, because the widest parking space gives the fewest spaces.
Every distractor here is a band whose ends were carried across wrongly, and the
one that matters most is the pair that was left in the original quantity's
units altogether.
"""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, ItemError, Mis
from .kit import MINUS, Q, band, dec, num, rel, sent, text_choices

__all__ = ["band_from_extremes", "band_scale", "band_formula"]


def _places(v) -> int:
    text = dec(v)
    return len(text.split(".")[1]) if "." in text else 0


def _matched(lo, hi) -> tuple[str, str]:
    """Two ends of a band printed alike: 7.5 feet and 9.0 feet, not 9."""
    places = max(_places(lo), _places(hi))
    return f"{float(lo):.{places}f}", f"{float(hi):.{places}f}"


def _denom(text: str) -> str:
    """A divisor keeps its own brackets when it is not a single number."""
    return f"({text})" if "/" in text else text


def _span(lo, hi, var: str, op: str = "<=", decimal: bool = False) -> str:
    """The band as it is printed: '1,510 ≤ d ≤ 4,130'. The ends are ordered."""
    lo, hi = (lo, hi) if Q(lo) <= Q(hi) else (hi, lo)
    show = dec if decimal else num
    return band(show(lo), op, var, op, show(hi))


# --------------------------------------------- a band read off two records

EXTREME_SCENES = {
    "migration": dict(
        tier="easy", var="d",
        stem="During spring migration, {a} {thing} traveled a minimum of {lo} "
             "{unit} and a maximum of {hi} {unit} between stopover locations. "
             "Which inequality represents this situation, where {var} is a "
             "possible distance, in {unit}, this {thing} traveled between "
             "stopover locations during spring migration?",
        things=["dragonfly", "monarch butterfly", "sandhill crane",
                "arctic tern"],
        unit="miles"),
    "temperature": dict(
        tier="easy", var="t",
        stem="For a {weeks}-week period in a town in {place}, the lowest "
             "recorded temperature was {lo} degrees Fahrenheit (°F) and the "
             "highest recorded temperature was {hi}°F. Which inequality is "
             "true for any recorded temperature {var}, in °F, in this town for "
             "this {weeks}-week period?",
        things=["Illinois", "Nebraska", "Vermont", "Oregon"], unit=""),
}


def band_from_extremes(rng: random.Random, seed: int, *, scene=None, lo=None,
                       hi=None, var=None, picks=None, thing=None,
                       weeks=None) -> Item:
    """A smallest and a largest value are recorded; the band is the answer."""
    scene = scene or rng.choice(list(EXTREME_SCENES))
    d = EXTREME_SCENES[scene]
    var = var or d["var"]
    lo = Q(lo if lo is not None else rng.randrange(20, 90, 1))
    hi = Q(hi if hi is not None else lo + rng.randrange(10, 60))
    if hi <= lo or lo <= 0:
        raise ItemError("the largest recorded value has to beat the smallest")
    key = _span(lo, hi, var)
    pool = {
        "hi_floor": Mis("kept only the largest recorded value and read it as a "
                        "floor rather than as the top of the range",
                        rel(var, ">=", num(hi))),
        "lo_cap": Mis("kept only the smallest recorded value and read it as a "
                      "cap rather than as the bottom of the range",
                      rel(var, "<=", num(lo))),
        "sum_floor": Mis("added the two recorded values instead of using them "
                         "as the two ends of the range",
                         rel(var, ">=", num(lo + hi))),
        "sum_band": Mis("used the largest recorded value as the bottom of the "
                        "range and the sum of the two as the top",
                        _span(hi, lo + hi, var)),
        "strict": Mis("left both recorded values out of the range, although "
                      "each of them was recorded and so is possible",
                      _span(lo, hi, var, "<")),
        "hi_cap": Mis("used the largest recorded value as a cap and left the "
                      "smallest out altogether", rel(var, "<=", num(hi))),
    }
    picks = picks or ["lo_cap", "hi_floor", "sum_band", "sum_floor", "strict"]
    wrong = [pool[p] for p in picks]
    thing = thing or rng.choice(d["things"])
    weeks = weeks or rng.choice([2, 3, 4, 5, 6])
    stem = sent(d["stem"].format(lo=num(lo), hi=num(hi), var=var, thing=thing,
                                 place=thing, unit=d["unit"], weeks=num(weeks),
                                 a="an" if thing[0].lower() in "aeiou" else "a"))
    P = {"kind": "ineq_band_extremes", "lo": [lo.numerator, lo.denominator],
         "hi": [hi.numerator, hi.denominator], "var": var}
    rationale = (f"Every recorded value is at least the smallest, {num(lo)}, "
                 f"and at most the largest, {num(hi)}; both were recorded, so "
                 f"both ends belong to the range and {key}.")
    ch, why, letter = text_choices(key, wrong, rng)
    return Item("ineq.band_from_extremes", "a range read off two records",
                d["tier"], seed, stem, "mcq", E(0), letter, rationale, ch, why,
                list(ch), params=P)


# ------------------------------------ a band carried through a multiplication

SCALE_SCENES = {
    "granite": dict(
        tier="easy", shape="product", var="x", order="rate_first",
        decimal=True, op="<",
        why="Each cubic foot weighs {rate} pounds",
        lo_range=(60, 260), gap=(10, 60), rate_range=(80, 300, 5),
        stem="A geologist estimates that the volume of a slab of {thing} is "
             "greater than {lo} cubic feet but less than {hi} cubic feet. The "
             "geologist also estimates that the slab of {thing} weighs {rate} "
             "pounds per cubic foot of volume. Which inequality represents "
             "this situation, where {var} represents the estimated total "
             "weight, in pounds, of the slab of {thing}?",
        things=["granite", "basalt", "limestone", "marble"]),
    "whale": dict(
        tier="medium", shape="product", var="x", order="band_first",
        decimal=False, op="<=",
        why="Each of the {rate} days adds between {lo} and {hi} miles",
        lo_range=(40, 120), gap=(2, 12), rate_range=(8, 40, 1),
        stem="A model estimates that {thing} travel {lo} to {hi} miles in the "
             "ocean each day during their migration. Based on this model, "
             "which inequality represents the estimated total number of miles, "
             "{var}, one of these whales could travel in {rate} days of its "
             "migration?",
        things=["whales from the genus Eschrichtius",
                "whales from the genus Balaenoptera",
                "whales from the genus Megaptera"]),
    "parking": dict(
        tier="medium", shape="divide", var="n", decimal=True, op="<=",
        stem="In North America, the standard width of a parking space is at "
             "least {lo} feet and no more than {hi} feet. A restaurant owner "
             "recently resurfaced the restaurant's parking lot and wants to "
             "determine the number of parking spaces, {var}, in the parking "
             "lot that could be placed perpendicular to a curb that is {rate} "
             "feet long, based on the standard width of a parking space. Which "
             "of the following describes all the possible values of {var} ?",
        things=["restaurant", "clinic", "library"]),
}


def band_scale(rng: random.Random, seed: int, *, scene=None, lo=None, hi=None,
               rate=None, var=None, picks=None, thing=None) -> Item:
    """A per-unit rate multiplies a band, or a total is divided by one."""
    scene = scene or rng.choice(list(SCALE_SCENES))
    d = SCALE_SCENES[scene]
    var = var or d["var"]
    op, decimal = d["op"], d["decimal"]
    if d["shape"] == "divide":
        if lo is None or hi is None:
            # build from the two counts, so both ends come out whole and the
            # widths stay the size a parking space really is
            fewest = rng.randint(8, 26)
            most = fewest + rng.randint(1, 5)
            lo = Q(rng.randrange(120, 240, 5), 20)          # 6 to 12 feet
            rate = lo * most
            hi = rate / fewest
            if rate.denominator != 1 or hi > 14 or hi.denominator not in (1, 2, 4):
                raise ItemError("these counts do not give a sensible width")
        lo, hi, rate = Q(lo), Q(hi), Q(rate)
        if hi <= lo or lo <= 0:
            raise ItemError("the band has to have a positive width")
        small, big = rate / hi, rate / lo
        if small.denominator != 1 or big.denominator != 1 or small < 2:
            raise ItemError("the two ends have to come out as whole counts")
        key = _span(small, big, var, op)
        pool = {
            "total_top": Mis("used the length of the curb itself as the "
                             "greatest possible number of spaces",
                             _span(small, rate, var, op)),
            "widths": Mis("gave the range of widths of one space rather than "
                          "the number of spaces that fit",
                          _span(lo, hi, var, op, decimal=True)),
            "swapped_total": Mis("used the greatest number of spaces as the "
                                 "least, and the length of the curb as the "
                                 "greatest", _span(big, rate, var, op)),
            "one_end": Mis("divided the curb length by the wider space only "
                           "and read that single count as a floor",
                           rel(var, ">=", num(small))),
        }
        picks = picks or ["swapped_total", "widths", "total_top", "one_end"]
        lo_txt, hi_txt = _matched(lo, hi)
        rationale = (f"The narrowest space, {dec(lo)} feet, lets {num(big)} "
                     f"spaces fit along {num(rate)} feet, and the widest, "
                     f"{dec(hi)} feet, lets only {num(small)} fit, so {key}.")
    else:
        step = 10 if decimal else 1
        span = d.get("lo_range", (20, 200))
        gap = d.get("gap", (5, 60))
        lo = Q(lo) if lo is not None else Q(rng.randrange(*span), step)
        hi = Q(hi) if hi is not None else lo + Q(rng.randrange(*gap), step)
        rate = Q(rate if rate is not None else
                 rng.randrange(*d.get("rate_range", (10, 300, 5))))
        if hi <= lo or rate <= 0:
            raise ItemError("the band has to have a positive width")
        show = dec if decimal else num

        def prod(v) -> str:
            return (f"{show(rate)}({show(v)})" if d["order"] == "rate_first"
                    else f"({show(v)})({show(rate)})")

        def plus(v) -> str:
            return (f"{show(rate)} + {show(v)}" if d["order"] == "rate_first"
                    else f"{show(v)} + {show(rate)}")

        key = band(prod(lo), op, var, op, prod(hi))
        pool = {
            "add": Mis("added the two quantities instead of multiplying them",
                       band(plus(lo), op, var, op, plus(hi))),
            "subtract": Mis("subtracted the two quantities instead of "
                            "multiplying them",
                            band(f"{show(rate)} {MINUS} {show(hi)}", op, var,
                                 op, f"{show(rate)} {MINUS} {show(lo)}")),
            "divide": Mis("divided by the quantity that should have been "
                          "multiplied, which also turns the two ends round",
                          band(f"{show(rate)}/{_denom(show(hi))}", op, var, op,
                               f"{show(rate)}/{_denom(show(lo))}")),
            "band_on_total": Mis("left the range on the total rather than on "
                                 "the daily amount it describes",
                                 band(show(lo), op, f"{show(rate)}{var}", op,
                                      show(hi))),
            "total_added": Mis("added the total to the range instead of "
                               "multiplying the range by it",
                               band(show(lo), op,
                                    f"{show(rate)} + {var}", op, show(hi))),
        }
        picks = picks or ["add", "subtract", "divide", "band_on_total"]
        lo_txt, hi_txt = show(lo), show(hi)
        lead = d["why"].format(rate=show(rate), lo=show(lo), hi=show(hi))
        rationale = (f"{lead}, so the smallest total is {prod(lo)} and the "
                     f"largest is {prod(hi)}; multiplying by a positive number "
                     f"keeps the two ends in order, so {key}.")
    wrong = [pool[p] for p in picks]
    thing = thing or rng.choice(d["things"])
    stem = sent(d["stem"].format(lo=lo_txt, hi=hi_txt, rate=num(rate), var=var,
                                 thing=thing))
    P = {"kind": "ineq_band_scale", "shape": d["shape"], "op": op, "var": var,
         "lo": [lo.numerator, lo.denominator],
         "hi": [hi.numerator, hi.denominator],
         "rate": [rate.numerator, rate.denominator],
         "order": d.get("order", ""), "decimal": bool(decimal)}
    ch, why, letter = text_choices(key, wrong, rng)
    return Item("ineq.band_scale", "carrying a range through a rate", d["tier"],
                seed, stem, "mcq", E(0), letter, rationale, ch, why, list(ch),
                params=P)


# ------------------------------- a band carried through a linear formula

FORMULA_SCENES = {
    "elephant": dict(
        tier="medium", var="w", op="<", decimal=False, formula="",
        offword="birth weight", mult_range=(60, 365, 5),
        off_range=(120, 320, 10), lo_range=(1, 7),
        stem="A certain {thing} weighs {off} pounds at birth and gains more "
             "than {lo} but less than {hi} pounds per day during its first "
             "year. Which of the following inequalities represents all "
             "possible weights {var}, in pounds, for the {thing} {mult} days "
             "after birth?",
        things=["elephant", "giraffe", "rhinoceros"]),
    "heart": dict(
        tier="medium", var="H", op="<=", decimal=True,
        offword="resting heart rate", mult_range=(90, 160, 10),
        off_range=(50, 80, 5),
        formula="{var} = {mult}p + {off}",
        stem="{formula}\nThe formula above shows the relationship between "
             "{who}'s target heart rate {var}, in beats per minute (bpm), and "
             "the intensity level p of different activities. When p = 0, {who} "
             "has a resting heart rate. When p = 1, {who} has a maximum heart "
             "rate. It is recommended that p be between {lo} and {hi} for "
             "{who} when training. Which of the following inequalities "
             "describes {who}'s target training heart rate?",
        things=["Alice", "Renata", "Malik", "Joon"]),
}


def band_formula(rng: random.Random, seed: int, *, scene=None, lo=None, hi=None,
                 mult=None, off=None, var=None, picks=None, thing=None) -> Item:
    """value = off + mult·t, with t between two numbers: the band on value."""
    scene = scene or rng.choice(list(FORMULA_SCENES))
    d = FORMULA_SCENES[scene]
    var = var or d["var"]
    op, decimal = d["op"], d["decimal"]
    if decimal:
        lo = Q(lo) if lo is not None else Q(rng.randrange(20, 60, 5), 100)
        hi = Q(hi) if hi is not None else lo + Q(rng.randrange(10, 45, 5), 100)
    else:
        span = d.get("lo_range", (1, 6))
        lo = Q(lo if lo is not None else rng.randint(*span))
        hi = Q(hi if hi is not None else lo + rng.randint(1, 5))
    mult = Q(mult if mult is not None else
             rng.randrange(*d.get("mult_range", (20, 400, 5))))
    off = Q(off if off is not None else
            rng.randrange(*d.get("off_range", (20, 300, 5))))
    if hi <= lo or mult <= 0 or off <= 0:
        raise ItemError("the band has to have a positive width")
    ends = [off + mult * lo, off + mult * hi]
    if any(v.denominator != 1 for v in ends):
        raise ItemError("both ends of the band have to come out whole")
    key = _span(ends[0], ends[1], var, op)
    word = d.get("offword", "starting amount")
    pool = {
        "no_offset": (mult * lo, mult * hi,
                      f"left the {word} out of both ends of the range"),
        "offset_lower": (off + mult * lo, mult * hi,
                         f"added the {word} at the bottom of the range but "
                         f"not at the top"),
        "offset_upper": (mult * lo, off + mult * hi,
                         f"added the {word} at the top of the range but not "
                         f"at the bottom"),
        "offset_times": (off * lo, off * hi,
                         f"multiplied the {word} by each end of the range "
                         f"instead of adding the amount the rate builds up"),
        "shifted": ((off + mult * (lo - 1), off + mult * (hi - 1),
                     "used one unit less at each end of the range")
                    if lo > 1 else None),
    }
    picks = picks or ["no_offset", "offset_times", "offset_upper",
                      "offset_lower"]
    wrong = []
    for name in picks:
        got = pool.get(name)
        # an end that is not a whole number gives the key away by its shape
        if got is None or any(Q(v).denominator != 1 for v in got[:2]):
            continue
        wrong.append(Mis(got[2], _span(got[0], got[1], var, op)))
    if len(wrong) < 3:
        raise ItemError("this band does not admit three distinct distractors")
    thing = thing or rng.choice(d["things"])
    show = dec if decimal else num
    formula = d["formula"].format(var=var, mult=num(mult), off=num(off))
    stem = sent(d["stem"].format(lo=show(lo), hi=show(hi), var=var,
                                 mult=num(mult), off=num(off), thing=thing,
                                 who=thing, formula=formula))
    P = {"kind": "ineq_band_formula", "op": op, "var": var,
         "lo": [lo.numerator, lo.denominator],
         "hi": [hi.numerator, hi.denominator],
         "mult": [mult.numerator, mult.denominator],
         "off": [off.numerator, off.denominator]}
    rationale = (f"The smallest the quantity can be is {num(off)} + "
                 f"{num(mult)}({show(lo)}) = {num(ends[0])}, and the largest "
                 f"is {num(off)} + {num(mult)}({show(hi)}) = {num(ends[1])}; "
                 f"the multiplier is positive, so the ends keep their order "
                 f"and {key}.")
    ch, why, letter = text_choices(key, wrong, rng)
    return Item("ineq.band_formula", "a range carried through a formula",
                d["tier"], seed, stem, "mcq", E(0), letter, rationale, ch, why,
                list(ch), params=P)
