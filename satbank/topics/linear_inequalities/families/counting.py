"""Inequalities whose answer is a count, and the two "which of these could it
be" shapes.

A budget item is an inequality wearing a disguise: the arithmetic is one
division, and the whole question is which way the quotient is rounded. A
student who rounds the wrong way lands one off the key every time, which is why
both neighbours of the answer appear among the options the source prints.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis, gridin_mistakes
from .kit import (dec, griddable, money, num, plural, rel, sent,
                  value_choices)

__all__ = ["whole_number_bound", "pair_max", "value_in_range", "which_interval"]


def _floor(v) -> int:
    return math.floor(Q(v))


def _ceil(v) -> int:
    return math.ceil(Q(v))


# ------------------------------------------------- a whole number of units

BOUND_SCENES = {
    "rental": dict(want="greatest", op="<=", tier="easy", spr=True,
                   money=True, noun="cost", fee_range=(5, 40, 5),
                   rate_choices=(15, 20, 25, 30, 40, 50, 60),
                   limit_range=(150, 600, 10),
                   stem="{who} plans to rent a {thing}. The {thing} rental costs "
                        "${rate} per hour, and {who} will also have to pay for a "
                        "{extra} that costs ${fee}. {who} wants to spend no more "
                        "than ${limit} for the rental and the {extra}. If the "
                        "{thing} rental is available only for a whole number of "
                        "hours, what is the maximum number of hours for which "
                        "{who} can rent the {thing}?"),
    "packages": dict(want="least", op=">=", tier="easy", spr=True, nofee=True,
                     noun="number", rate_choices=(6, 8, 10, 12, 15, 20, 24),
                     limit_range=(30, 260, 5),
                     stem="For a party, {limit} {thing} are needed. {Thing} are "
                          "sold in packages of {rate}. What is the minimum number "
                          "of packages that should be bought for the party?"),
    "shortfall": dict(want="least", op=">=", tier="easy", spr=False,
                      unit_rate=True, noun="flight time",
                      fee_range=(20, 140, 2), limit_range=(150, 300, 10),
                      stem="{who} needs at least {limit} hours of flight time to "
                           "get a private pilot certification. If {who} already "
                           "has {fee} hours of flight time, what is the minimum "
                           "number of additional hours of flight time {who} needs "
                           "to get a private pilot certification?"),
    "trailer": dict(want="greatest", op="<=", tier="medium", spr=False,
                    noun="combined weight", fee_range=(200, 900, 50),
                    rate_choices=(40, 60, 80, 100, 120, 150),
                    limit_range=(2000, 6000, 100),
                    stem="A moving truck can tow a trailer if the combined weight "
                         "of the trailer and the boxes it contains is no more than "
                         "{limit} pounds. What is the maximum number of boxes this "
                         "truck can tow in a trailer with a weight of {fee} pounds "
                         "if each box weighs {rate} pounds?"),
    "venue": dict(want="greatest", op="<=", tier="medium", spr=True, money=True,
                  fee_range=(20, 120, 5), limit_range=(200, 900, 10),
                  noun="cost",
                  stem="An event planner is planning a party. It costs the event "
                       "planner a onetime fee of ${fee} to rent the venue and "
                       "${rate} per attendee. The event planner has a budget of "
                       "${limit}. What is the greatest number of attendees "
                       "possible without exceeding the budget?"),
    "transit": dict(want="least", op=">", tier="hard", spr=True, nofee=True,
                    money=True, tickets=True, limit_range=(60, 200, 5),
                    noun="ticket cost",
                    stem="A local transit company sells a monthly pass for "
                         "${limit} that allows an unlimited number of trips of any "
                         "length. Tickets for individual trips cost {prices}, "
                         "depending on the length of the trip. What is the minimum "
                         "number of trips per month for which a monthly pass could "
                         "cost less than purchasing individual tickets for trips?"),
    "ohm": dict(want="greatest", op="<=", tier="hard", spr=True, nofee=True,
                noun="current", circuit=True, limit_range=(5, 60, 5),
                limit_scale=100,
                stem="I = V/R\nThe given formula is Ohm's law for an electric "
                     "circuit with current I, in amperes, potential difference V, "
                     "in volts, and resistance R, in ohms. A circuit has a "
                     "resistance of {ohms} ohms, and its potential difference will "
                     "be generated by n {volts}-volt batteries that produce a "
                     "total potential difference of {volts}n volts. If the circuit "
                     "is to have a current of no more than {limit} "
                     "{amp}, what is the greatest number, n, of {volts}-volt "
                     "batteries that can be used?"),
    "farm": dict(want="least", op=">=", tier="hard", spr=False, tiered=True,
                 noun="savings", money=True, rate_choices=(9, 10, 12, 14, 15),
                 limit_range=(200, 700, 10),
                 stem="{who} is working this summer as part of a crew on a farm, "
                      "and earned ${first_rate} per hour for the first "
                      "{first_hours} hours worked this week. Because of that "
                      "performance, the crew leader raised the salary to ${rate} "
                      "per hour for the rest of the week. {who} saves {pct}% of "
                      "the earnings from each week. What is the least number of "
                      "hours {who} must work the rest of the week to save at "
                      "least ${limit} for the week?"),
}
BOUND_NAMES = list(BOUND_SCENES)

WHO = ["Maria", "Julissa", "Ken", "Devon", "Anika", "Rafael", "Noor", "Stefan"]
RENTALS = [("boat", "water safety course"), ("kayak", "life jacket"),
           ("bicycle", "helmet rental"), ("canoe", "paddling lesson")]
PARTY = ["dinner rolls", "cupcakes", "party favors", "juice boxes", "napkins"]


def whole_number_bound(rng: random.Random, seed: int, *, scene=None, fee=None,
                       rate=None, limit=None, scale=1, fmt=None, **kw) -> Item:
    """fee + rate·n against a limit, answered by a whole number of units."""
    scene = scene or rng.choice(BOUND_NAMES)
    d = BOUND_SCENES[scene]
    op, want = d["op"], d["want"]
    fee = Q(0) if d.get("nofee") else Q(
        fee if fee is not None else rng.randrange(*d.get("fee_range",
                                                         (10, 600, 5))))
    if d.get("unit_rate"):
        rate = Q(1)
    elif d.get("circuit"):
        # the rate is the circuit's own volts per ohm, not a free number
        ohms = kw.get("ohms") or rng.choice([200, 250, 400, 500, 600, 800])
        volts = kw.get("volts") or rng.choice([3, 6, 9, 12])
        kw = dict(kw, ohms=ohms, volts=volts)
        rate = Q(rate) if rate is not None else Q(volts, ohms)
    elif rate is not None:
        rate = Q(rate)
    elif d.get("tickets"):
        # the dearest ticket is what the pass has to beat, so the rate the item
        # is solved with has to be a price the stem actually prints
        rate = Q(rng.randrange(30, 60, 5), 10)
    else:
        rate = Q(rng.choice(d.get("rate_choices",
                                  (3, 4, 6, 8, 10, 12, 15, 20, 25, 40, 60))))
    limit = Q(limit) if limit is not None else Q(
        rng.randrange(*d.get("limit_range", (120, 900, 5))),
        d.get("limit_scale", 1))
    if d.get("tiered"):
        # the money already earned is the first block's pay, not a free number
        first_rate = Q(kw.get("first_rate") or rng.choice([7, 8, 9, 10]))
        first_hours = Q(kw.get("first_hours") or rng.choice([8, 10, 12, 15]))
        kw = dict(kw, first_rate=first_rate, first_hours=first_hours)
        fee = first_rate * first_hours
        if rate <= first_rate:
            raise ItemError("the raise has to leave the crew better paid")
        if scale == 1:
            scale = Q(rng.choice([50, 60, 75, 80, 90]), 100)
    scale = Q(scale)
    if rate <= 0 or scale <= 0:
        raise ItemError("the rate and the savings fraction must be positive")
    edge = (limit / scale - fee) / rate
    if edge < 3 or edge > 400:
        raise ItemError("the count has to be a sensible whole number")
    # an exact fit is only a problem where the rounding is the question: with a
    # unit rate nothing is divided, and a tiered item's distractors come from
    # the two pay rates rather than from which way the quotient was rounded
    rounds = rate != 1 and not d.get("tiered")
    if want == "greatest":
        key = _floor(edge)
        if key == edge and op == "<=" and rounds:
            raise ItemError("an exact fit hides the rounding the item is about")
    else:
        key = _ceil(edge)
        if key == edge and op == ">":
            key = key + 1
        if key == edge and op == ">=" and rounds:
            raise ItemError("an exact fit hides the rounding the item is about")
    if key <= 0:
        raise ItemError("the answer has to be a positive count")

    ex = E(key)
    bare = limit / scale / rate
    pool = []
    if d.get("tiered"):
        pool += [
            Mis("used the first block's hourly rate for the whole week and left "
                "out the money already earned",
                E(_ceil(limit / scale / kw.get("first_rate", 1)))),
            Mis("applied the savings fraction twice, once to the target and "
                "once to the hourly pay", E(_floor(limit / scale / (scale * rate)))),
            Mis("multiplied the target by the savings fraction instead of "
                "dividing by it", E(_floor((limit * scale - fee) / rate)))]
    if want == "greatest":
        pool += [Mis("rounded the quotient up instead of down", E(_ceil(edge))),
                 Mis("left the fixed charge out of the total", E(_floor(bare))),
                 Mis("left the fixed charge out and rounded up", E(_ceil(bare)))]
    else:
        pool += [Mis("rounded the quotient down instead of up", E(_floor(edge))),
                 Mis("reported the amount already accounted for rather than what "
                     "is still needed", E(fee) if fee else None),
                 Mis("added the two given amounts instead of subtracting them",
                     E(fee + limit) if fee else None),
                 Mis("left the amount already accounted for out of the "
                     "subtraction", E(_ceil(bare)))]

    who = kw.get("who") or rng.choice(WHO)
    thing, extra = kw.get("rental") or rng.choice(RENTALS)
    party = kw.get("party") or rng.choice(PARTY)
    prices = kw.get("prices") or (
        f"{money(rate - 2)}, {money(rate - 1)}, or {money(rate)}"
        if rate > 2 else money(rate))
    text = d["stem"].format(
        who=who, thing=thing if scene == "rental" else party,
        Thing=(party[0].upper() + party[1:]), extra=extra,
        rate=dec(rate) if d.get("money") else num(rate),
        fee=dec(fee) if d.get("money") else num(fee),
        limit=dec(limit) if d.get("money") else num(limit),
        prices=prices, ohms=num(kw.get("ohms", 500)),
        volts=num(kw.get("volts", 6)),
        amp=kw.get("amp") or plural(limit, "ampere"),
        first_rate=num(kw.get("first_rate", 8)),
        first_hours=num(kw.get("first_hours", 10)),
        pct=num(scale * 100))
    stem = sent(text)
    P = {"kind": "ineq_whole_bound", "fee": [fee.numerator, fee.denominator],
         "rate": [rate.numerator, rate.denominator],
         "limit": [limit.numerator, limit.denominator],
         "scale": [scale.numerator, scale.denominator], "op": op, "want": want}
    show = (lambda v: money(v)) if d.get("money") else dec
    noun = d.get("noun", "total")
    at = lambda k: show(scale * (fee + rate * k))                   # noqa: E731
    near = key + 1 if want == "greatest" else key - 1
    rationale = (
        f"The condition is {rel(_scaled(scale, fee, rate), op, dec(limit))}. "
        f"With n = {num(key)} the {noun} is {at(key)}, which meets it, and "
        f"with n = {num(near)} it is {at(near)}, which does not, so the {want} "
        f"whole number that works is {num(key)}.")
    fmt = fmt or ("spr" if d.get("spr") else "mcq")
    if fmt == "spr":
        if not griddable(key):
            raise ItemError("this answer would not be enterable in a grid-in")
        # a typed value is named only for what produced it: the tiered pool's
        # savings-fraction values also drop the money earned or round the
        # wrong way, the shortfall reasons would type dollars as hours, the
        # trailer's fixed amount is a weight rather than a charge, and an
        # exact quotient under ">" is the break-even count
        if d.get("tiered"):
            named = [pool[0], pool[3],
                     Mis("left out the money already earned", pool[6].value)]
        elif scene == "trailer":
            named = [pool[0],
                     Mis("left the trailer's weight out of the total",
                         pool[1].value),
                     Mis("left the trailer's weight out and rounded up",
                         pool[2].value)]
        else:
            named = list(pool)
        if op == ">" and key == edge + 1:
            named[0] = Mis("counted the break-even number, where the two "
                           "costs are equal", named[0].value)
        return Item("ineq.whole_number_bound", "a whole-number bound",
                    d["tier"], seed, stem, "spr", ex, ex.gridin(), rationale,
                    params=P, spr_mistakes=gridin_mistakes(ex, named))
    ch, tex, wh, letter = value_choices(ex, [m for m in pool if m.value], rng)
    return Item("ineq.whole_number_bound", "a whole-number bound", d["tier"],
                seed, stem, "mcq", ex, letter, rationale, ch, wh, tex, params=P)


def _scaled(scale, fee, rate) -> str:
    head = "n" if rate == 1 else f"{dec(rate)}n"
    body = head if fee == 0 else f"{dec(fee)} + {head}"
    return body if scale == 1 else f"{dec(scale)}({body})"


# ------------------------------------------- the most of the heavier item

def pair_max(rng: random.Random, seed: int, *, w1=None, w2=None, least=None,
             cap=None, thing="packages", vehicle="cargo helicopter",
             unit="pound") -> Item:
    """Two package weights, a floor on the count and a ceiling on the weight."""
    w1 = Q(w1 if w1 is not None else rng.randrange(20, 200, 10))
    w2 = Q(w2 if w2 is not None else rng.randrange(30, 260, 10))
    least = int(least if least is not None else rng.randint(4, 20))
    cap = Q(cap if cap is not None else rng.randrange(400, 3000, 50))
    if w2 <= w1:
        raise ItemError("the second package has to be the heavier one")
    if cap <= w1 * least:
        raise ItemError("the lightest possible load already breaks the cap")
    key = min(_floor((cap - w1 * least) / (w2 - w1)), least)
    if key < 2 or key >= least:
        raise ItemError("the weight cap has to bite before the count does")
    ex = E(key)
    pool = [Mis("rounded the number of swaps up instead of down", E(key + 1)),
            Mis("stopped one swap short of the weight the load allows",
                E(key - 1)),
            Mis("divided the whole weight allowance by the heavier package and "
                "ignored the smallest number of packages", E(_floor(cap / w2))),
            Mis("divided the weight left over by the heavier package rather "
                "than by the difference between the two",
                E(_floor((cap - w1 * least) / w2)))]
    stem = sent(f"A {vehicle} delivers only {num(w1)}-{unit} {thing} and "
                f"{num(w2)}-{unit} {thing}. For each delivery trip, the "
                f"{vehicle} must carry at least {num(least)} {thing}, and the "
                f"total weight of the {thing} can be at most {num(cap)} "
                f"{unit}s. What is the maximum number of {num(w2)}-{unit} "
                f"{thing} that the {vehicle} can carry per trip?")
    P = {"kind": "ineq_pair_max", "w1": [w1.numerator, w1.denominator],
         "w2": [w2.numerator, w2.denominator], "least": least,
         "cap": [cap.numerator, cap.denominator]}
    rationale = (f"Carrying {num(least)} of the lighter {thing} weighs "
                 f"{num(w1 * least)} {unit}s, and each swap to a heavier one "
                 f"adds {num(w2 - w1)} {unit}s. The cap leaves "
                 f"{num(cap - w1 * least)} {unit}s to spend on swaps, so at "
                 f"most {num(key)} of the {thing} can be the heavier kind.")
    ch, tex, wh, letter = value_choices(ex, pool, rng)
    return Item("ineq.pair_max", "the most of one kind under two constraints",
                "medium", seed, stem, "mcq", ex, letter, rationale, ch, wh,
                tex, params=P)


# ------------------------------------------ which value the range allows

RANGE_SCENES = {
    "trays": dict(style="count",
                  lead="The total on {n} trays lies between {lo} and {hi}",
                  stem="A bakery sells trays of {thing}. Each tray contains at "
                       "least {lo} {thing} but no more than {hi}. Which of the "
                       "following could be the total number of {thing} on {n} "
                       "trays of {thing}?",
                  things=["cookies", "muffins", "rolls", "scones"]),
    "body": dict(style="single", unit="°F",
                 lead="A normal body temperature is anywhere from {lo} to "
                      "{hi}",
                 stem="Normal body temperature for an adult is between {lo}{unit} "
                      "and {hi}{unit}, inclusive. If {who}, an adult, has a body "
                      "temperature that is considered to be normal, which of the "
                      "following could be that body temperature?"),
}


def value_in_range(rng: random.Random, seed: int, *, scene=None, lo=None, hi=None,
                   n=1, inside=None, offsets=None, thing=None, who=None) -> Item:
    """A quantity lies in a band; which of four printed values could it be?"""
    scene = scene or rng.choice(list(RANGE_SCENES))
    d = RANGE_SCENES[scene]
    unit = d.get("unit", "")
    if d["style"] == "count":
        lo = int(lo if lo is not None else rng.randrange(10, 90, 5))
        hi = int(hi if hi is not None else lo + rng.randrange(5, 40, 5))
        n = int(n if n != 1 else rng.randint(2, 8))
        lo_q, hi_q = Q(lo), Q(hi)
    else:
        lo_q = Q(lo) if lo is not None else Q(rng.randrange(960, 990), 10)
        hi_q = Q(hi) if hi is not None else lo_q + Q(rng.randrange(8, 30), 10)
        lo, hi = lo_q, hi_q
        n = 1
    if hi_q <= lo_q:
        raise ItemError("the band has to have some width")
    band_lo, band_hi = n * lo_q, n * hi_q
    width = band_hi - band_lo

    if d["style"] == "count":
        inside = Q(inside if inside is not None else rng.randint(1, int(width) - 1))
        key = band_lo + inside
        opts = [(key, ""),
                (key - width, f"counted one tray fewer than the {num(n)} given"),
                (key + width, "added the leftover onto the largest possible "
                              "total instead of onto the smallest"),
                (key + 2 * width, f"counted one tray more than the {num(n)} given")]
    else:
        o = offsets or [Q(rng.randrange(1, 9), 10) for _ in range(3)]
        inside = Q(inside if inside is not None else Q(rng.randrange(1, 5), 10))
        key = lo_q + inside
        near, far = lo_q - o[0], lo_q - o[0] - o[2]
        opts = [(key, ""),
                (near, f"just below the lower end of the range, {dec(lo_q)}"
                       f"{unit}, which a normal reading has to reach"),
                (hi_q + o[1], f"above the upper end of the range, {dec(hi_q)}"
                              f"{unit}, which a normal reading cannot pass"),
                (far, f"below the lower end of the range, {dec(lo_q)}{unit}, "
                      f"by more than a degree")]
    if key > band_hi:
        raise ItemError("the keyed value is outside the band it must sit in")
    vals = [v for v, _ in opts]
    if len(set(vals)) != 4:
        raise ItemError("two options carry the same value")
    for v, _ in opts[1:]:
        if band_lo <= v <= band_hi:
            raise ItemError("a distractor also satisfies the condition")

    fmt_v = (lambda x: dec(x.coef) + unit) if unit else (lambda x: num(x.coef))
    pool = [Mis(why, E(v)) for v, why in opts[1:]]
    ch, tex, wh, letter = value_choices(E(key), pool, rng, fmt_value=fmt_v)
    shown = {fmt_v(E(v)): Q(v) for v, _ in opts}
    thing = thing or (rng.choice(d["things"]) if "things" in d else "")
    who = who or rng.choice(WHO)
    stem = sent(d["stem"].format(lo=dec(lo_q), hi=dec(hi_q), n=num(n),
                                 thing=thing, unit=unit, who=who))
    P = {"kind": "ineq_value_in_range",
         "lo": [lo_q.numerator, lo_q.denominator],
         "hi": [hi_q.numerator, hi_q.denominator], "n": n,
         "opts": [[c, [shown[c].numerator, shown[c].denominator]] for c in ch]}
    lead = d["lead"].format(n=num(n), lo=fmt_v(E(band_lo)), hi=fmt_v(E(band_hi)))
    rationale = (f"{lead}, and {ch['ABCD'.index(letter)]} is the only one of "
                 f"the four printed values in that range.")
    return Item("ineq.value_in_range", "a value a range allows",
                "easy", seed, stem, "mcq", E(key), letter, rationale, ch, wh,
                tex, params=P)


# -------------------------------------------- which interval clears a line

INTERVAL_SCENES = {
    "plant": dict(who="botanist", thing="plant species", word="tall", var="h",
                  unit="centimeters",
                  measure="typical height when fully grown", lo=20, hi=200),
    "fish": dict(who="ichthyologist", thing="fish species", word="long",
                 var="x", unit="centimeters",
                 measure="typical length when fully grown", lo=15, hi=120),
    "beetle": dict(who="entomologist", thing="beetle species", word="heavy",
                   var="m", unit="milligrams",
                   measure="typical mass when fully grown", lo=40, hi=400),
    "tortoise": dict(who="zoologist", thing="tortoise species",
                     word="long-lived", var="t", unit="years",
                     measure="typical life span", lo=25, hi=150),
}


def which_interval(rng: random.Random, seed: int, *, scene=None, thr=None,
                   key=None, wrong=None, var=None, unit=None, word=None,
                   thing=None, who=None, measure=None) -> Item:
    """Four intervals; only one lies entirely on the far side of a threshold."""
    d = INTERVAL_SCENES[scene or rng.choice(list(INTERVAL_SCENES))]
    var, unit, word = var or d["var"], unit or d["unit"], word or d["word"]
    thing, who = thing or d["thing"], who or d["who"]
    measure = measure or d["measure"]
    thr = int(thr if thr is not None else rng.randrange(d["lo"], d["hi"], 5))
    if key is None:
        a = thr + rng.randint(2, 30)
        key = (a, a + rng.randint(10, 80))
    if wrong is None:
        b = thr - rng.randint(5, 30)
        wrong = [(max(1, b - rng.randint(10, 40)), thr),
                 (max(1, thr - rng.randint(40, 80)), thr - rng.randint(5, 20)),
                 (max(1, thr - rng.randint(60, 100)), thr - rng.randint(10, 30))]
    spans = [(tuple(key), "")] + [
        (tuple(w), "the interval stops at the threshold, so no value in it is "
                   "more than the threshold" if w[1] == thr else
                   f"the whole interval, from {num(w[0])} to {num(w[1])}, "
                   f"lies below the threshold")
        for w in wrong]
    seen = set()
    for (lo, hi), _ in spans:
        if lo >= hi or lo < 0:
            raise ItemError("an interval has no width")
        if (lo, hi) in seen:
            raise ItemError("two options print the same interval")
        seen.add((lo, hi))
    if spans[0][0][0] <= thr:
        raise ItemError("the keyed interval has to clear the threshold")
    for (lo, _hi), _ in spans[1:]:
        if lo > thr:
            raise ItemError("a distractor also clears the threshold")
    texts = [f"{num(lo)} < {var} < {num(hi)}" for (lo, hi), _ in spans]
    pool = [Mis(why, t) for t, (_, why) in zip(texts[1:], spans[1:])]
    from .kit import text_choices
    ch, wh, letter = text_choices(texts[0], pool, rng)
    stem = sent(f"A particular {who} classifies a {thing} as {word} if its "
                f"{measure} is more than {num(thr)} {unit}. Each of the "
                f"following inequalities represents the possible values of "
                f"{var}, in {unit}, for a specific {thing}. Which inequality "
                f"represents the possible values of {var}, in {unit}, for a "
                f"{word} {thing}?")
    P = {"kind": "ineq_which_interval", "thr": float(thr),
         "spans": [[t, float(lo), float(hi)] for t, ((lo, hi), _) in
                   zip(texts, spans)]}
    P["order"] = list(ch)
    rationale = (f"Only {texts[0]} keeps every value above {num(thr)} "
                 f"{unit}; each of the others allows values at or below it.")
    return Item("ineq.which_interval", "choosing the interval that clears a "
                "threshold", "medium", seed, stem, "mcq", E(0), letter,
                rationale, ch, wh, list(ch), params=P)
