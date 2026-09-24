"""The word problems: a starting amount, a constant rate, and a question.

Five generators, and the axis that matters in all of them is which family of
wrong answers the item writer reached for. The source set uses four, and they
are not interchangeable: an item whose numbers invite a swap gets swapped
options, one whose numbers invite a dropped term gets dropped ones. `wrong`
names the family, so a source item is rebuilt with its own distractors as well
as its own numbers.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import Item, ItemError, Mis, assemble, gridin_mistakes
from ...linear_functions.common import (MINUS, choose, coef_text, dec, ex, lin_text, money,
                                        numtext, q, year_text,
                                        recip_text, terminating)
from .define import _text_item, pair, sig

__all__ = ["model_equation", "per_unit_model", "tiered_cost", "model_value",
           "context_two_points"]

WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight",
         9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}


SUFFIX = {1: "st", 2: "nd", 3: "rd"}


def _ordinal(n: int) -> str:
    tail = "th" if 10 <= n % 100 <= 20 else SUFFIX.get(n % 10, "th")
    return f"{n}{tail}"


# ------------------------------------------------------------ model equation

# Each context is a stem with an initial amount and a rate to be filled in, the
# left-hand side the options are written with, and the style the source prints
# its numbers in.
MODEL_CTX = [
    dict(text="The front of a roller-coaster car is at the bottom of a hill and is {b} "
              "feet above the ground. If the front of the roller-coaster car rises at a "
              "constant rate of {m} feet per second, which of the following equations "
              "gives the height h, in feet, of the front of the roller-coaster car s "
              "seconds after it starts up the hill?",
         lhs="h", var="s", order="var_first", style="frac", places=None,
         brange=(5, 40), mrange=(2, 15), wrong="swap"),
    dict(text="On January 1, 2015, a city's minimum hourly wage was ${b}. It will increase "
              "by ${m} on the first day of the year for the next 5 years. Which of the "
              "following functions best models the minimum hourly wage, in dollars, x "
              "years after January 1, 2015, where x = 1, 2, 3, 4, 5 ?",
         lhs="f(x)", var="x", order="var_second", style="dec", places=2,
         brange=(700, 1400), mrange=(25, 125), scale=100, wrong="swap"),
    dict(text="The length, y, of a white whale was {b} centimeters (cm) when it was born "
              "and increased an average of {m} cm per month for the first 12 months after "
              "it was born. Which equation best represents this situation, where x is the "
              "number of months after the whale was born and y is the length, in cm, of "
              "the whale?",
         lhs="y", var="x", order="var_first", style="dec", places=None,
         brange=(90, 220), mrange=(15, 90), scale=10, wrong="reuse"),
    dict(text="To repair a refrigerator, a technician charges ${m} per hour for labor plus "
              "${b} for parts. Which function f represents the total amount, in dollars, "
              "the technician will charge for this job if it takes x hours?",
         lhs="f(x)", var="x", order="var_first", style="frac", places=None,
         brange=(40, 300), mrange=(25, 120), wrong="drop"),
    dict(text="A gym charges a one-time enrollment fee of ${b} plus ${m} for each month of "
              "membership. Which function f gives the total amount, in dollars, a member "
              "pays for x months of membership?",
         lhs="f(x)", var="x", order="var_first", style="frac", places=None,
         brange=(20, 250), mrange=(12, 90), wrong="drop"),
    dict(text="A seedling was {b} centimeters (cm) tall when it was planted and grew an "
              "average of {m} cm each week. Which equation best represents this situation, "
              "where x is the number of weeks after the seedling was planted and y is the "
              "height, in cm, of the seedling?",
         lhs="y", var="x", order="var_first", style="dec", places=None,
         brange=(30, 140), mrange=(8, 45), scale=10, wrong="reuse"),
    dict(text="A storage tank held {b} gallons of water and was filled at a constant rate "
              "of {m} gallons per minute. Which equation gives the number of gallons y in "
              "the tank x minutes after the filling began?",
         lhs="y", var="x", order="var_first", style="frac", places=None,
         brange=(40, 400), mrange=(3, 25), wrong="swap"),
    dict(text="A printing shop charges a setup fee of ${b} and then ${m} for each poster "
              "printed. Which equation gives the total cost y, in dollars, of printing x "
              "posters?",
         lhs="y", var="x", order="var_second", style="dec", places=2,
         brange=(500, 4000), mrange=(50, 400), scale=100, wrong="swap"),
]

VERBAL_CTX = [
    dict(text="The number y is {b} less than the number x. Which equation represents the "
              "relationship between x and y?",
         lhs="y", var="x", m=1, sign=-1, brange=(12, 140), style="frac", places=None),
    dict(text="The number y is {b} more than the number x. Which equation represents the "
              "relationship between x and y?",
         lhs="y", var="x", m=1, sign=1, brange=(12, 140), style="frac", places=None),
]

RATE_CTX = [
    dict(text="For a training program, Juan rides his bike at an average rate of {m} "
              "minutes per mile. Which function m models the number of minutes it will "
              "take Juan to ride x miles at this rate?",
         lhs="m(x)", var="x", style="dec", places=None, mrange=(25, 140), scale=10),
    dict(text="A machine fills {m} bottles each minute. Which function b models the number "
              "of bottles the machine fills in x minutes?",
         lhs="b(x)", var="x", style="frac", places=None, mrange=(4, 90)),
    dict(text="A conversion uses {m} centimeters for every inch. Which function c models "
              "the number of centimeters in x inches?",
         lhs="c(x)", var="x", style="dec", places=None, mrange=(20, 60), scale=10),
]


def _model_wrong(m, b, lhs, var, style, places, order, wrong):
    def T(mm, bb, ordr=None):
        return pair(f"{lhs} = {lin_text(mm, bb, var, style, places, ordr or order)}",
                    mm, bb)
    if wrong == "swap":
        return [Mis("swapped the rate and the starting amount",
                    T(b, m, "var_first")),
                Mis("subtracted the rate where the situation adds it", T(-m, b)),
                Mis("swapped the two numbers and subtracted", T(b, -m, "var_first"))]
    if wrong == "reuse":
        return [Mis("used the starting amount as the rate and left out the constant term",
                    T(b, 0, "var_first")),
                Mis("used the starting amount as both the rate and the constant term",
                    T(b, b, "var_first")),
                Mis("used the rate as both the rate and the constant term", T(m, m)),
                Mis("swapped the rate and the starting amount", T(b, m, "var_first"))]
    if wrong == "drop":
        return [Mis("left the rate off the variable term", T(1, b)),
                Mis("left out the fixed amount", T(m, 0)),
                Mis("subtracted the fixed amount instead of adding it", T(m, -b))]
    mag = abs(b) if b != 0 else abs(m)
    if b != 0:
        return [Mis("added where the situation subtracts", T(1, -b)),
                Mis("divided by the number instead of subtracting it",
                    pair(f"{lhs} = {recip_text(mag, var)}", Q(1) / mag, 0)),
                Mis("multiplied by the number instead of subtracting it", T(mag, 0)),
                Mis("used the number as a constant on its own", T(0, mag))]
    return [Mis("divided by the rate instead of multiplying by it",
                pair(f"{lhs} = {recip_text(mag, var)}", Q(1) / mag, 0)),
            Mis("added the rate instead of multiplying by it", T(1, mag)),
            Mis("subtracted the rate instead of multiplying by it", T(1, -mag)),
            Mis("squared nothing and simply doubled the rate", T(2 * m, 0))]


def model_equation(rng: random.Random, seed: int, *, ctx=None, kind=None, m=None, b=None,
                   wrong=None) -> Item:
    """A starting amount and a constant rate, written as an equation."""
    kind = kind or rng.choices(["model", "verbal", "rate"], weights=[6, 2, 2])[0]
    if kind == "verbal":
        c = VERBAL_CTX[rng.randrange(len(VERBAL_CTX))] if ctx is None else VERBAL_CTX[ctx]
        b = q(b if b is not None else rng.randint(*c["brange"])) * c["sign"]
        m = Q(1)
        wrong = "operation"
    elif kind == "rate":
        c = RATE_CTX[rng.randrange(len(RATE_CTX))] if ctx is None else RATE_CTX[ctx]
        m = q(m) if m is not None else Q(rng.randint(*c["mrange"]), c.get("scale", 1))
        b = Q(0)
        wrong = "operation"
    else:
        c = MODEL_CTX[rng.randrange(len(MODEL_CTX))] if ctx is None else MODEL_CTX[ctx]
        m = q(m) if m is not None else Q(rng.randint(*c["mrange"]), c.get("scale", 1))
        b = q(b) if b is not None else Q(rng.randint(*c["brange"]), c.get("scale", 1))
        wrong = wrong or c["wrong"]
    if m == 0 or m == b:
        raise ItemError("the rate and the starting amount must be distinct and non-zero")
    style, places = c["style"], c["places"]
    lhs, var = c["lhs"], c["var"]
    order = c.get("order", "var_first")
    stem = c["text"].format(b=numtext(abs(b), style, places),
                            m=numtext(abs(m), style, places))
    key = f"{lhs} = {lin_text(m, b, var, style, places, order)}"
    wrongs = _model_wrong(m, b, lhs, var, style, places, order, wrong)
    P = {"kind": "lf_model_eq", "m": [m.numerator, m.denominator],
         "b": [b.numerator, b.denominator]}
    rationale = (f"The constant rate is the coefficient of {var} and the starting amount "
                 f"is the constant term, so {key}.")
    return _text_item("lin.model_equation", "modelling with a linear equation", "easy",
                      seed, stem, key, sig(m, b), wrongs, rng, P, rationale)


# ----------------------------------------------------------- per-unit models

OFFSET_CTX = [
    dict(text="The boiling point of water at sea level is {c} degrees Fahrenheit (°F). For "
              "every {n} feet above sea level, the boiling point of water is lowered by "
              "about 1 °F. Which of the following equations can be used to find the "
              "boiling point B of water, in °F, x feet above sea level?",
         lhs="B", var="x", down=True, crange=(180, 240), nrange=(400, 700)),
    dict(text="A reservoir holds {c} acre-feet of water. For every {n} days without rain "
              "the reservoir loses about 1 acre-foot. Which of the following equations can "
              "be used to find the amount W, in acre-feet, of water in the reservoir after "
              "x days without rain?",
         lhs="W", var="x", down=True, crange=(120, 900), nrange=(10, 60)),
    dict(text="A hot-air balloon is {c} meters above the ground. For every {n} seconds of "
              "flight the balloon rises about 1 meter. Which of the following equations "
              "can be used to find the height H, in meters, of the balloon after x seconds "
              "of flight?",
         lhs="H", var="x", down=False, crange=(50, 400), nrange=(4, 45)),
]

SCALED_CTX = [
    dict(text="One gallon of paint will cover {n} square feet of a surface. A room has a "
              "total wall area of w square feet. Which equation represents the total "
              "amount of paint P, in gallons, needed to paint the walls of the room "
              "{ktext}?",
         lhs="P", var="w", nrange=(120, 400), ktext={2: "twice", 3: "three times"}),
    dict(text="One bag of fertilizer treats {n} square feet of lawn. A lawn has an area of "
              "w square feet. Which equation represents the total number of bags F needed "
              "to treat the lawn {ktext}?",
         lhs="F", var="w", nrange=(200, 800), ktext={2: "twice", 3: "three times"}),
]


def per_unit_model(rng: random.Random, seed: int, *, shape=None, ctx=None, c=None, n=None,
                   k=None) -> Item:
    """A rate stated as 'one unit per N', which prints as a division."""
    shape = shape or rng.choice(["offset", "scaled"])
    if shape == "offset":
        d = OFFSET_CTX[rng.randrange(len(OFFSET_CTX))] if ctx is None else OFFSET_CTX[ctx]
        c = int(c if c is not None else rng.randint(*d["crange"]))
        n = int(n if n is not None else rng.randint(*d["nrange"]))
        if c == n:
            raise ItemError("the two numbers must be distinguishable")
        down = d["down"]
        lhs, var = d["lhs"], d["var"]
        stem = d["text"].format(c=numtext(c), n=numtext(n))

        def T(first, second, minus):
            return pair(f"{lhs} = {numtext(first)} {MINUS if minus else '+'} "
                        f"{var}/{numtext(second)}",
                        Q(-1 if minus else 1, second), first)
        key_text, key_sig = T(c, n, down)
        wrongs = [Mis("swapped the two numbers", T(n, c, down)),
                  Mis("swapped the two numbers and changed the sign", T(n, c, not down)),
                  Mis("changed the sign of the per-unit term", T(c, n, not down))]
        rationale = (f"Each foot changes the amount by 1/{numtext(n)}, so the model is "
                     f"{key_text}.")
        P = {"kind": "lf_per_unit", "shape": shape, "c": c, "n": n, "down": bool(down)}
    else:
        d = SCALED_CTX[rng.randrange(len(SCALED_CTX))] if ctx is None else SCALED_CTX[ctx]
        n = int(n if n is not None else rng.randint(*d["nrange"]))
        k = int(k if k is not None else rng.choice([2, 3]))
        if n % k:
            raise ItemError("the coverage must divide evenly by the number of coats")
        lhs, var = d["lhs"], d["var"]
        stem = d["text"].format(n=numtext(n), ktext=d["ktext"][k])

        def D(den):
            return pair(f"{lhs} = {var}/{numtext(den)}", Q(1, den), 0)

        def Mu(mul):
            return pair(f"{lhs} = {coef_text(mul, var)}", mul, 0)
        key_text, key_sig = D(n // k)
        wrongs = [Mis("multiplied by the coverage instead of dividing by it", Mu(k * n)),
                  Mis("used one coat instead of the number the question asks for", D(n)),
                  Mis("multiplied by the coverage for a single coat", Mu(n)),
                  Mis("divided by the number of coats as well", D(n * k))]
        rationale = (f"{numtext(k)} coats over {numtext(n)} square feet per gallon needs "
                     f"{numtext(k)}w/{numtext(n)} = w/{numtext(n // k)} gallons.")
        P = {"kind": "lf_per_unit", "shape": shape, "n": n, "k": k}
    return _text_item("lin.per_unit_model", "a rate written as a quotient", "medium", seed,
                      stem, key_text, key_sig, wrongs, rng, P, rationale)


# --------------------------------------------------------------- tiered cost

TIER_CTX = [
    dict(text="The cost of renting a backhoe for up to {cap} days is ${a} for the first "
              "day and ${b} for each additional day. Which of the following equations "
              "gives the cost y, in dollars, of renting the backhoe for x days, where x is "
              "a positive integer and x ≤ {cap}?",
         lhs="y", var="x", block=1, arange=(120, 500), cap=10),
    dict(text="The cost of renting a large canopy tent for up to {cap} days is ${a} for "
              "the first day and ${b} for each additional day. Which of the following "
              "equations gives the cost y, in dollars, of renting the tent for x days, "
              "where x is a positive integer and x ≤ {cap}?",
         lhs="y", var="x", block=1, arange=(200, 700), cap=10),
    dict(text="For groups of {k} or more people, a museum charges ${a} per person for the "
              "first {k} people and ${b} for each additional person. Which function f "
              "gives the total charge, in dollars, for a tour group with n people, where "
              "n ≥ {k}?",
         lhs="f(n)", var="n", block=None, arange=(12, 40), krange=(10, 40)),
    dict(text="For groups of {k} or more visitors, a botanical garden charges ${a} per "
              "visitor for the first {k} visitors and ${b} for each additional visitor. "
              "Which function f gives the total charge, in dollars, for a group with n "
              "visitors, where n ≥ {k}?",
         lhs="f(n)", var="n", block=None, arange=(8, 30), krange=(8, 30)),
]


def tiered_cost(rng: random.Random, seed: int, *, ctx=None, a=None, b=None, k=None) -> Item:
    """The first unit costs one price, every later unit costs another."""
    d = TIER_CTX[rng.randrange(len(TIER_CTX))] if ctx is None else TIER_CTX[ctx]
    a = int(a if a is not None else rng.randint(*d["arange"]))
    if d["block"] == 1:
        k = 1
        b = int(b if b is not None else a // 2)
    else:
        k = int(k if k is not None else rng.randint(*d["krange"]))
        b = int(b if b is not None else rng.randint(max(2, a // 3), a - 1))
    if b >= a or b <= 0:
        raise ItemError("the additional-unit price must be lower and positive")
    lhs, var = d["lhs"], d["var"]
    const = k * (a - b)
    stem = d["text"].format(a=numtext(a), b=numtext(b), k=numtext(k),
                            cap=numtext(d.get("cap", 10)))
    key = f"{lhs} = {lin_text(b, const, var)}"
    if k == 1:
        wrongs = [Mis("used the first day's price as the rate and subtracted the rest",
                      pair(f"{lhs} = {lin_text(a, -b, var)}", a, -b)),
                  Mis("used the first day's price as the rate and added the rest",
                      pair(f"{lhs} = {lin_text(a, b, var)}", a, b)),
                  Mis("used the first day's price as the constant term",
                      pair(f"{lhs} = {lin_text(b, a, var)}", b, a)),
                  Mis("charged every day at the additional-day price",
                      pair(f"{lhs} = {coef_text(b, var)}", b, 0))]
    else:
        wrongs = [Mis("charged the whole first block again on top of every person",
                      pair(f"{lhs} = {lin_text(b, k * a, var)}", b, k * a)),
                  Mis("added the two prices into the rate and subtracted the block",
                      pair(f"{lhs} = {lin_text(a + b, -k * b, var)}", a + b, -k * b)),
                  Mis("used the per-person price of the first block as the constant term",
                      pair(f"{lhs} = {lin_text(b, a, var)}", b, a)),
                  Mis("charged every person at the additional-person price",
                      pair(f"{lhs} = {coef_text(b, var)}", b, 0))]
    P = {"kind": "lf_tiered", "a": a, "b": b, "k": k}
    rationale = (f"The first {numtext(k)} cost {numtext(k * a)} and each of the remaining "
                 f"{var} {MINUS} {numtext(k)} costs {numtext(b)}, so the total is "
                 f"{key}.")
    return _text_item("lin.tiered_cost", "a two-rate cost model", "hard", seed, stem, key,
                      sig(b, const), wrongs, rng, P, rationale)


# ---------------------------------------------------- evaluating a model

VALUE_CTX = [
    dict(text="Robert rented a truck to transport materials he purchased from a hardware "
              "store. He was charged an initial fee of ${b} plus an additional ${m} per "
              "mile driven. If the truck was driven {x} miles, what was the total amount "
              "Robert was charged?",
         money=True, places=2, bscale=100, mscale=100, brange=(500, 4000),
         mrange=(35, 250), xrange=(12, 80), wrong="steps"),
    dict(text="Gabriella deposits ${m} in a savings account at the end of each week. At "
              "the beginning of the 1st week of a year there was ${b} in that savings "
              "account. How much money, in dollars, will be in the account at the end of "
              "the {xo} week of that year?",
         money=False, places=None, brange=(200, 1200), mrange=(10, 80), xrange=(3, 9),
         ordinal=True, wrong="steps"),
    dict(text="According to a model, the head width, in millimeters, of a worker bumblebee "
              "can be estimated by adding {b} to {mw} times the body weight of the bee, in "
              "grams. According to the model, what would be the head width, in "
              "millimeters, of a worker bumblebee that has a body weight of {x} grams?",
         money=False, places=None, bscale=10, brange=(3, 9), mrange=(2, 9),
         xscale=10, xrange=(3, 9), spelled=True, wrong="given"),
    dict(text="Scientists collected fallen acorns that each housed a colony of the ant "
              "species P. ohioensis and analyzed each colony's structure. For any of these "
              "colonies, if the colony has x worker ants, the equation y = {m}x + {b}, "
              "where 20 ≤ x ≤ 110, gives the predicted number of larvae, y, in the colony. "
              "If one of these colonies has {x} worker ants, which of the following is "
              "closest to the predicted number of larvae in the colony?",
         money=False, places=None, bscale=10, brange=(15, 40), mscale=100,
         mrange=(40, 95), xrange=(25, 105), approx=True, wrong="scale"),
    dict(text="The pressure exerted on a scuba diver at sea level is {b} pounds per square "
              "inch (psi). For each foot the scuba diver descends below sea level, the "
              "pressure exerted on the scuba diver increases by {m} psi. What is the total "
              "pressure, in psi, exerted on the scuba diver at {x} feet below sea level?",
         money=False, places=2, bscale=100, brange=(1200, 1800), mscale=100,
         mrange=(30, 70), xrange=(40, 140), wrong="given"),
    dict(text="The function f(x) = {b} − {mneg}x gives the estimated surface water "
              "temperature f(x), in degrees Celsius, of a body of water on the xth day of "
              "the year, where 220 ≤ x ≤ 360. Based on the model, what is the estimated "
              "surface water temperature, in degrees Celsius, of this body of water on the "
              "{xo} day of the year?",
         money=False, places=2, bscale=100, brange=(4500, 6000), mscale=100,
         mrange=(10, 24), xrange=(230, 350), negative=True, ordinal=True, wrong="given"),
]

INVERSE_CTX = [
    dict(text="T = {b} + {m}h In the equation above, T represents Brittany's total "
              "take-home pay, in dollars, for her first week of work, where h represents "
              "the number of hours she worked that week and {b} represents a sign-on "
              "bonus. If Brittany's total take-home pay was ${total}, for how many hours "
              "was Brittany paid for her first week of work?",
         brange=(500, 2500), mrange=(12, 30), xrange=(12, 45)),
    dict(text="C = {b} + {m}n In the equation above, C represents the total cost, in "
              "dollars, of a catered dinner, where n represents the number of guests and "
              "{b} represents a fixed hall fee. If the total cost was ${total}, how many "
              "guests were at the dinner?",
         brange=(200, 1500), mrange=(15, 60), xrange=(10, 60)),
]


def model_value(rng: random.Random, seed: int, *, ctx=None, direction=None, b=None, m=None,
                x=None, fmt=None, wrong=None) -> Item:
    """A model in words, evaluated forward or run backwards for the input."""
    direction = direction or ("inverse" if rng.random() < 0.2 else "forward")
    if direction == "inverse":
        d = INVERSE_CTX[rng.randrange(len(INVERSE_CTX))] if ctx is None else INVERSE_CTX[ctx]
        b = q(b if b is not None else rng.randint(*d["brange"]))
        m = q(m if m is not None else rng.randint(*d["mrange"]))
        x = q(x if x is not None else rng.randint(*d["xrange"]))
        total = b + m * x
        stem = d["text"].format(b=numtext(b), m=numtext(m), total=numtext(total))
        key = x
        mistakes = [Mis("divided the whole total by the rate without first removing the "
                        "fixed amount", q(round(total / m))),
                    Mis("halved the remaining amount before dividing", (total - b) / (2 * m)),
                    Mis("subtracted the rate instead of dividing by it", total - b - m),
                    Mis("divided the fixed amount by the rate instead", q(round(b / m)))]
        spr = [Mis(mistakes[0].reason, total / m)] + mistakes[1:3] + [
            Mis(mistakes[3].reason, b / m)]
        rationale = (f"{numtext(total)} = {numtext(b)} + {numtext(m)}x gives "
                     f"x = {numtext(key)}.")
        P = {"kind": "lf_model_value", "direction": direction,
             "m": [m.numerator, m.denominator], "b": [b.numerator, b.denominator],
             "x": [x.numerator, x.denominator], "approx": False, "money": False}
        fmt = fmt or "mcq"
    else:
        d = VALUE_CTX[rng.randrange(len(VALUE_CTX))] if ctx is None else VALUE_CTX[ctx]
        b = q(b) if b is not None else Q(rng.randint(*d["brange"]), d.get("bscale", 1))
        m = q(m) if m is not None else Q(rng.randint(*d["mrange"]), d.get("mscale", 1))
        x = q(x) if x is not None else Q(rng.randint(*d["xrange"]), d.get("xscale", 1))
        if d.get("negative"):
            m = -abs(m)
        places = d["places"]
        xi = int(x) if x.denominator == 1 else None
        stem = d["text"].format(
            b=numtext(b, "dec", places),
            m=numtext(abs(m), "dec", places),
            mneg=numtext(abs(m), "dec", places),
            mw=WORDS.get(int(abs(m)), numtext(abs(m))) if d.get("spelled") else
               numtext(abs(m)),
            x=numtext(x, "dec"),
            xo=(_ordinal(xi) if xi is not None else numtext(x)))
        raw = b + m * x
        key = q(round(raw)) if d.get("approx") else raw
        if d.get("approx") and abs(raw - round(raw)) == Q(1, 2):
            raise ItemError("a half-way value would round ambiguously")
        wrong = wrong or d["wrong"]
        if wrong == "given":
            cands = [("gave the starting amount instead of the total", b),
                     ("gave the rate instead of the total", m),
                     ("subtracted the starting amount instead of adding it",
                      m * x - b),
                     ("left out the starting amount", m * x),
                     ("subtracted the change instead of adding it", b - m * x)]
        elif wrong == "scale":
            cands = [("multiplied the input by the constant term as well as by the rate",
                      x * (m + b)),
                     ("solved for the input instead of evaluating the model",
                      (x - b) / m if m != 0 else None),
                     ("added the constant term to the input without scaling it", x + b),
                     ("left out the constant term", m * x)]
        else:
            cands = [("added a single unit's worth instead of all of them", b + m),
                     ("added the number of units instead of multiplying by the rate",
                      b + m + x),
                     ("subtracted the total change instead of adding it", b - m * x),
                     ("left out the starting amount", m * x)]
        mistakes = [Mis(r, q(round(v)) if d.get("approx") else v)
                    for r, v in cands if v is not None]
        # a grid-in slip is rounded as a student rounds, half up, and in
        # b - 0.21x the sign slip adds the change, so it is named as added. The
        # third "given" slip is m*x - b when m >= 0, the start subtracted, not
        # left out, so a typed value is never filed under it (m*x is the fourth)
        spr = []
        for i, (r, v) in enumerate(cands):
            if v is None or (wrong == "given" and i == 2):
                continue
            if m < 0:
                r = r.replace("subtracted", "added").replace("instead of adding",
                                                             "instead of subtracting")
            spr.append(Mis(r, (v + Q(1, 2)) // 1 if d.get("approx") else v))
        rationale = (f"{numtext(b, 'dec')} + {numtext(m, 'dec')}({numtext(x, 'dec')}) = "
                     f"{numtext(raw, 'dec')}"
                     + (f", which is closest to {numtext(key)}." if d.get("approx")
                        else "."))
        P = {"kind": "lf_model_value", "direction": direction,
             "m": [m.numerator, m.denominator], "b": [b.numerator, b.denominator],
             "x": [x.numerator, x.denominator], "approx": bool(d.get("approx")),
             "money": bool(d.get("money"))}
        fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
        # a grid-in is entered as digits, so the dollar sign belongs only to the
        # multiple-choice form and the audit is told which it is looking at
        P["money"] = bool(d.get("money")) and fmt == "mcq"
        if P["money"]:
            P["places"] = 2
    keyx = ex(key)
    mistakes = [Mis(r.reason, ex(r.value)) for r in mistakes if r.value is not None]
    if fmt == "spr":
        return Item("lin.model_value", "evaluating a linear model", "medium", seed, stem,
                    "spr", keyx, keyx.gridin(), rationale, params=P)
    if P.get("money"):
        fmt_value = money
    elif direction == "forward" and d.get("places") and not d.get("approx"):
        fmt_value = lambda v: dec(v, d["places"])
        P["places"] = d["places"]
    else:
        fmt_value = None
    choices, latex, reasons, letter = choose(keyx, mistakes, rng, fmt_value=fmt_value,
                                               signed=not P.get("money"),
                                               fillers="shift")
    return Item("lin.model_value", "evaluating a linear model", "medium", seed, stem,
                "mcq", keyx, letter, rationale, choices, reasons, latex, params=P)


# ----------------------------------------------------- two points in context

PREDICT_CTX = [
    dict(text="A linear model estimates the population of a city from {y1} to {y3}. The "
              "model estimates the population was {v1} thousand in {y1}, {v2} thousand in "
              "{y2}, and x thousand in {y3}. To the nearest whole number, what is the "
              "value of x?",
         years=True, v1range=(30, 90), v2range=(150, 300), approx=True),
    dict(text="An economist modeled the demand Q for a certain product as a linear "
              "function of the selling price P. The demand was {v1} units when the selling "
              "price was ${y1} per unit, and the demand was {v2} units when the selling "
              "price was ${y2} per unit. Based on the model, what is the demand, in units, "
              "when the selling price is ${y3} per unit?",
         years=False, v1range=(12000, 30000), v2range=(8000, 20000), approx=False),
]


def context_two_points(rng: random.Random, seed: int, *, ask=None, ctx=None, x1=None,
                       y1=None, x2=None, y2=None, x3=None, fmt=None, wrong=None,
                       model_ctx=None, style=None) -> Item:
    """Two readings in a real context: predict a third, or write the model."""
    ask = ask or rng.choice(["predict", "model"])
    if ask == "predict":
        d = PREDICT_CTX[rng.randrange(len(PREDICT_CTX))] if ctx is None else PREDICT_CTX[ctx]
        if d["years"]:
            x1 = int(x1 if x1 is not None else rng.randint(1960, 1999))
            x2 = int(x2 if x2 is not None else x1 + rng.randint(10, 25))
            x3 = int(x3 if x3 is not None else x2 + rng.randint(2, 10))
        else:
            x1 = int(x1 if x1 is not None else rng.randint(10, 60))
            x2 = int(x2 if x2 is not None else x1 + rng.randint(10, 40))
            x3 = int(x3 if x3 is not None else x1 + rng.randint(2, x2 - x1 - 1))
        y1 = q(y1 if y1 is not None else rng.randint(*d["v1range"]))
        y2 = q(y2 if y2 is not None else rng.randint(*d["v2range"]))
        if x2 == x1 or y1 == y2:
            raise ItemError("two readings must differ in both coordinates")
        m = (y2 - y1) / (x2 - x1)
        raw = y1 + m * (x3 - x1)
        key = q(round(raw)) if d["approx"] else raw
        if d["approx"] and abs(raw - round(raw)) == Q(1, 2):
            raise ItemError("a half-way value would round ambiguously")
        if not d["approx"] and key.denominator != 1:
            raise ItemError("this context reports whole units")
        mid = y1 + m * (Q(x1 + x2, 2) - x1)
        stem = d["text"].format(y1=year_text(x1), y2=year_text(x2), y3=year_text(x3),
                                v1=numtext(y1), v2=numtext(y2))
        def slips(v):
            """The slips around v, the value at x3."""
            return [Mis("stepped one unit too far from the nearer known point", v - m),
                    Mis("stepped two units too far from the nearer known point",
                        v - 2 * m),
                    Mis("evaluated the model halfway between the two given inputs", mid),
                    Mis("used the nearer reading unchanged", y1)]
        mistakes = slips(key)
        at = year_text(x3) if d["years"] else f"${numtext(x3)}"
        per = "year" if d["years"] else "dollar"
        asked = "the value of x to the nearest whole number" if d["approx"] else \
                "the demand"
        rationale = (f"The rate of change is {numtext(m)} per {per}, so the model's "
                     f"value at {at} is {numtext(raw)}, and {asked} is "
                     f"{numtext(key)}.")
        P = {"kind": "lf_two_points_ctx", "ask": ask, "x1": x1, "x2": x2, "x3": x3,
             "y1": [y1.numerator, y1.denominator], "y2": [y2.numerator, y2.denominator],
             "approx": bool(d["approx"])}
        keyx = ex(key)
        fmt = fmt or ("spr" if rng.random() < 0.4 else "mcq")
        mistakes = [Mis(r.reason, ex(r.value)) for r in mistakes if r.value is not None]
        if fmt == "spr":
            # a slip is worked from the unrounded value and typed as the stem asks,
            # a whole number rounded half up; y1 is the nearer reading only when
            # x3 is nearer x1 than x2. A step too far goes on past x3, away from
            # the nearer point, and with neither point nearer there is no step
            near1, near2 = abs(x3 - x1) < abs(x3 - x2), abs(x3 - x2) < abs(x3 - x1)
            away = (1 if x3 > (x1 if near1 else x2) else -1) * m
            named = slips(raw)[2:4 if near1 else 3]
            if near1 or near2:
                named = [Mis(r.reason, raw + k * away) for k, r in
                         ((1, slips(raw)[0]), (2, slips(raw)[1]))] + named
            if d["approx"]:
                named = [Mis(r.reason, (r.value + Q(1, 2)) // 1) for r in named]
            return Item("lin.context_two_points", "a linear model from two readings",
                        "hard", seed, stem, "spr", keyx, keyx.gridin(), rationale,
                        params=P, spr_mistakes=gridin_mistakes(
                            keyx, [Mis(r.reason, ex(r.value)) for r in named]))
        choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True,
                                                   fillers="shift")
        return Item("lin.context_two_points", "a linear model from two readings", "hard",
                    seed, stem, "mcq", keyx, letter, rationale, choices, reasons, latex,
                    params=P)

    d = MODEL2_CTX[rng.randrange(len(MODEL2_CTX))] if model_ctx is None \
        else MODEL2_CTX[model_ctx]
    x1 = int(x1 if x1 is not None else d["year0"])
    x2 = int(x2 if x2 is not None else x1 + rng.randint(8, 20))
    y1 = q(y1) if y1 is not None else Q(rng.randint(*d["v1range"]), d.get("scale", 1))
    y2 = q(y2) if y2 is not None else Q(rng.randint(*d["v2range"]), d.get("scale", 1))
    if x2 == x1 or y1 == y2:
        raise ItemError("two readings must differ in both coordinates")
    gap = x2 - x1
    m = (y2 - y1) / gap
    style = style or d["style"]
    # a context that prints its rate as a decimal can only print a rate that
    # has one. 862 to 846 over ten years is -1.6; 1,172 to 557 over seventeen
    # is -36.17..., which `dec` would silently round to -36 -- an option that
    # no longer fits the table printed above it.
    if style == "dec" and d.get("places") is None and not terminating(m):
        raise ItemError("a decimal context must print an exact rate of change")
    lhs, var = d["lhs"], d["var"]
    order = d["order"]
    key = f"{lhs} = {lin_text(m, y1, var, style, d.get('places'), order)}"
    wrong = wrong or d["wrong"]
    table = None
    if d.get("table"):
        table = [list(d["table"]), [numtext(x1), numtext(y1, d.get("vstyle", "dec"))],
                 [numtext(x2), numtext(y2, d.get("vstyle", "dec"))]]
    vstyle = d.get("vstyle", "dec")
    stem = d["text"].format(y1=year_text(x1), y2=year_text(x2), v1=numtext(y1, vstyle),
                            v2=numtext(y2, vstyle))
    drop = y1 - y2

    def T(mm, bb, ordr=None):
        return pair(f"{lhs} = {lin_text(mm, bb, var, style, d.get('places'), ordr or order)}",
                    mm, bb)

    def shifted(cval):
        c = q(cval)
        body = (f"{numtext(y1, style)} {'+' if c > 0 else MINUS} "
                f"{numtext(abs(c), style)}({var} {MINUS} {numtext(x1)})")
        return pair(f"{lhs} = {body}", c, y1 - c * x1)
    if wrong == "offset":
        wrongs = [Mis("did not divide the change by the number of years",
                      T(m * gap, y1)),
                  Mis("used the year itself as the input and did not divide the change",
                      shifted(-m * gap)),
                  Mis("used the year itself as the input", shifted(m)),
                  Mis("changed the sign of the rate of change", T(-m, y1))]
    else:
        alt = -y2 / gap if d.get("alt") == "final" else -drop / gap
        if style == "dec" and d.get("places") is None and not terminating(alt):
            raise ItemError("a decimal context must print exact distractor rates")
        wrongs = [Mis("changed the sign of the rate of change", T(-m, y1)),
                  Mis("used the final amount instead of the change in amount", T(alt, y1)),
                  Mis("used the final amount and changed the sign", T(-alt, y1)),
                  Mis("did not divide the change by the number of years", T(m * gap, y1))]
    P = {"kind": "lf_two_points_ctx", "ask": ask, "x1": x1, "x2": x2,
         "y1": [y1.numerator, y1.denominator], "y2": [y2.numerator, y2.denominator]}
    rationale = (f"The amount changes by {numtext(y2 - y1, style)} over {numtext(gap)} "
                 f"units, a rate of {numtext(m, style)}, starting from "
                 f"{numtext(y1, style)}.")
    return _text_item("lin.context_two_points", "a linear model from two readings",
                      "hard", seed, stem, key, sig(m, y1), wrongs, rng, P, rationale,
                      table=table)


MODEL2_CTX = [
    dict(text="The table above shows the population of Greenleaf, Idaho, for the years "
              "{y1} and {y2}. If the relationship between population and year is linear, "
              "which of the following functions P models the population of Greenleaf t "
              "years after {y1}?",
         lhs="P(t)", var="t", order="var_second", style="dec", places=None,
         year0=2000, v1range=(600, 1200), v2range=(500, 1100), wrong="offset",
         table=("Year", "Population")),
    dict(text="Oil and gas production in a certain area dropped from {v1} million barrels "
              "in {y1} to {v2} million barrels in {y2}. Assuming that the oil and gas "
              "production decreased at a constant rate, which of the following linear "
              "functions f best models the production, in millions of barrels, t years "
              "after the year {y1}?",
         lhs="f(t)", var="t", order="var_first", style="frac", places=None,
         year0=2000, v1range=(25, 60), v2range=(8, 24), scale=10, wrong="sign",
         alt="final"),
    dict(text="A town's recycling tonnage rose from {v1} tons in {y1} to {v2} tons in "
              "{y2}. Assuming the tonnage changed at a constant rate, which of the "
              "following linear functions f models the tonnage t years after {y1}?",
         lhs="f(t)", var="t", order="var_first", style="frac", places=None,
         year0=2005, v1range=(40, 120), v2range=(140, 300), wrong="sign", alt="final"),
]
