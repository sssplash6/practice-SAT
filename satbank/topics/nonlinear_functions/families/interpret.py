"""What a number in a model means, in words.

These are the items where a distractor can be a *true* statement -- the
starting amount really is 9,000, the maximum really is 1,034 -- and still be
the wrong answer, because it answers a different question. So each option here
is a claim of a named shape attached to a named number, and the signature
records both: which quantity the sentence talks about, and which of the item's
own printed numbers it attaches to it.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import ItemError, Mis, unit_word
from ..common import (MINUS, dec, num, pair, pick, poly_text, q, sig,
                      text_item, value_item, year)
from ..figures import context_curve

__all__ = ["interpret_value", "interpret_initial", "interpret_rate", "quad_feature"]


def _pct(r) -> str:
    r = q(r) * 100
    return (num(r) if r.denominator == 1 else dec(r)) + "%"


# ------------------------------------------------ what f(a) = v is saying

VALUE_CTX = [
    dict(name="revenue",
         stem="The function f(x) = {a}({b})^x gives a company's predicted annual "
              "revenue, in dollars, x years after the company started selling {thing} "
              "online, where 0 < x ≤ {cap}. What is the best interpretation of the "
              "statement “f({t}) is approximately equal to {v}” in this "
              "context?",
         key="{t} years after the company started selling {thing} online, its "
             "predicted annual revenue is approximately {v} dollars.",
         wrong={
             "total": "{t} years after the company started selling {thing} online, "
                      "its predicted annual revenue will have increased by a total of "
                      "approximately {v} dollars.",
             "times": "When the company's predicted annual revenue is approximately "
                      "{v} dollars, it is {t} times the predicted annual revenue for "
                      "the previous year.",
             "percent": "When the company's predicted annual revenue is approximately "
                        "{v} dollars, it is {t}% greater than the predicted annual "
                        "revenue for the previous year."},
         things=["light bulbs", "jewelry", "sneakers", "bicycles"]),
    dict(name="coin",
         stem="{who} purchased a certain rare coin on January 1. The function "
              "f(x) = {a}({b})^x, where 0 ≤ x ≤ {cap}, gives the predicted value, in "
              "dollars, of the rare coin x years after {who} purchased it. What is "
              "the best interpretation of the statement “f({t}) is approximately "
              "equal to {v}” in this context?",
         key="{t} years after {who} purchased the rare coin, its predicted value is "
             "approximately {v} dollars.",
         wrong={
             "percent": "When the rare coin's predicted value is approximately {v} "
                        "dollars, it is {t}% greater than the predicted value, in "
                        "dollars, on January 1 of the previous year.",
             "times": "When the rare coin's predicted value is approximately {v} "
                      "dollars, it is {t} times the predicted value, in dollars, on "
                      "January 1 of the previous year.",
             "total": "From the day {who} purchased the rare coin to {t} years after "
                      "{who} purchased the coin, its predicted value increased by a "
                      "total of approximately {v} dollars."},
         things=["a rare coin"]),
    dict(name="isotope",
         stem="A sample of a certain isotope takes {half} years to decay to half its "
              "original mass. The function s(t) = {a}(0.5)^(t/{half}) gives the "
              "approximate mass of this isotope, in grams, that remains t years after "
              "a {a}-gram sample starts to decay. Which statement is the best "
              "interpretation of s({t}) = {v} in this context?",
         key="Approximately {v} grams of the sample remains {t} years after the "
             "sample starts to decay.",
         wrong={
             "decrease": "The mass of the sample has decreased by approximately {v} "
                         "grams {t} years after the sample starts to decay.",
             "swap_decrease": "The mass of the sample has decreased by approximately "
                              "{t} grams {v} years after the sample starts to decay.",
             "swap": "Approximately {t} grams of the sample remains {v} years after "
                     "the sample starts to decay."},
         things=["an isotope"]),
    dict(name="height",
         stem="The height, in feet, of an object x seconds after it is thrown "
              "straight up in the air can be modeled by the function h(x) = "
              "{MINUS}16x² + {b}x + {a}. Based on the model, which of the following "
              "statements best interprets the equation h({t}) = {v}?",
         key="The height of the object {t} {sec_t} after being thrown straight up in "
             "the air is {v} {ft_v}.",
         wrong={
             "swap": "The height of the object {v} {sec_v} after being thrown "
                     "straight up in the air is {t} {ft_t}.",
             "times": "The height of the object {v} {sec_v} after being thrown "
                      "straight up in the air is approximately {t} {times_t} as great as "
                      "its initial height.",
             "speed": "The speed of the object {t} {sec_t} after being thrown straight "
                      "up in the air is approximately {v} {ft_v} per second."},
         things=["an object"]),
]


def interpret_value(rng: random.Random, seed: int, *, ctx=None, a=None, b=None, t=None,
                    thing=None, who=None, cap=None, half=None, steps=None,
                    wrongs=None) -> object:
    """A statement f(a) = v, and the four sentences it might be saying."""
    d = VALUE_CTX[rng.randrange(len(VALUE_CTX))] if ctx is None else VALUE_CTX[ctx]
    thing = thing or rng.choice(d["things"])
    who = who or rng.choice(["Immanuel", "Priya", "Dara", "Nadia", "Elias"])
    cap = int(cap if cap is not None else rng.choice([8, 10, 12]))
    if d["name"] not in ("height", "isotope"):
        t = int(t if t is not None else rng.randint(2, cap - 2))

    if d["name"] == "height":
        a = q(a if a is not None else rng.randint(2, 9))
        b = q(b if b is not None else rng.randint(12, 40))
        tt = q(t) / 10 if t is not None else q(rng.randrange(8, 20)) / 10
        v = -16 * tt ** 2 + b * tt + a
        if v <= 0 or (v * 100).denominator != 1:
            raise ItemError("the printed height must be positive and land on a cent")
        f = dict(t=dec(tt), v=dec(v), a=num(a), b=num(b), MINUS=MINUS, thing=thing,
                 who=who, cap=num(cap), half="")
        f.update(sec_t=unit_word(tt, "second", "seconds"),
                 sec_v=unit_word(v, "second", "seconds"),
                 ft_t=unit_word(tt, "foot", "feet"),
                 ft_v=unit_word(v, "foot", "feet"),
                 times_t=unit_word(tt, "time", "times"))
        vnum, tnum = v, tt
        inputs = {"a": [q(a).numerator, q(a).denominator],
                  "b": [q(b).numerator, q(b).denominator]}
    elif d["name"] == "isotope":
        half = int(half if half is not None else rng.choice([11, 19, 29, 41]))
        a = int(a if a is not None else rng.randrange(4, 60) * 8)
        steps = int(steps) if steps is not None else rng.choice([2, 3])
        tt = q(half * steps)
        v = q(a) / 2 ** steps
        if v.denominator != 1:
            raise ItemError("the printed mass must be a whole number of grams")
        f = dict(t=num(tt), v=num(v), a=num(a), b="", half=num(half), thing=thing,
                 who=who, cap=num(cap), MINUS=MINUS)
        vnum, tnum = v, tt
        inputs = {"a": [int(a), 1], "half": half, "steps": steps}
    else:
        a = int(a if a is not None else rng.randrange(5, 60) * 5000)
        b = q(b if b is not None else Q(rng.randrange(102, 140), 100))
        v = q(a) * b ** t
        vv = (v + Q(1, 2)).__floor__()          # the source rounds, it does not cut
        if vv == a or vv <= 0:
            raise ItemError("the printed value must have moved")
        f = dict(t=num(t), v=num(vv), a=num(a), b=dec(b, 2), thing=thing, who=who,
                 cap=num(cap), half="", MINUS=MINUS)
        vnum, tnum = q(vv), q(t)
        inputs = {"a": [int(a), 1], "b": [b.numerator, b.denominator]}

    key = d["key"].format(**f)
    pool = {k_: (_reason(k_, d["name"]),
                 pair(text.format(**f), _shape(k_), vnum if k_ in
                      ("total", "times", "percent", "decrease") else tnum))
            for k_, text in d["wrong"].items()}
    order = list(d["wrong"])
    fname = {"isotope": "s", "height": "h"}.get(d["name"], "f")
    why = (f"{fname}({f['t']}) is the output when the input is {f['t']}, so the "
           f"model's value at that input is {f['v']}.")
    P = {"kind": "nlf_interpret_value", "ctx": d["name"],
         "t": [tnum.numerator, tnum.denominator], **inputs}
    return text_item("nlfunc.interpret_value", "what a function value says", "easy",
                     seed, d["stem"].format(**f), key, sig("value", vnum),
                     pick(pool, order, wrongs), rng, P, why)


def _shape(name: str) -> str:
    return {"total": "total", "times": "times", "percent": "percent",
            "decrease": "decrease", "swap": "swap", "swap_decrease": "swap_decrease",
            "speed": "speed"}[name]


def _reason(name: str, ctx: str = "") -> str:
    times = ("read the input as a multiple of the object's starting height"
             if ctx == "height" else
             "read the input as a multiplier of the previous year's value")
    return {
        "total": "read the output as the total increase rather than the value itself",
        "times": times,
        "percent": "read the input as a percent increase over the previous year",
        "decrease": "read the output as the amount lost rather than the amount left",
        "swap_decrease": "swapped the input and the output and read the output as the "
                         "amount lost",
        "swap": "swapped the input and the output",
        "speed": "read the output as a speed rather than a height",
    }[name]


# --------------------------------------- what the coefficient in front means

INITIAL_CTX = [
    dict(name="traffic",
         stem="D = {a}({b})^t The equation above estimates the global data traffic D, "
              "in terabytes, for the year that is t years after {y0}. What is the "
              "best interpretation of the number {a} in this context?",
         key="The estimated data traffic, in terabytes, in {y0}",
         wrong={"increase": "The estimated amount of increase of data traffic, in "
                            "terabytes, each year",
                "percent": "The estimated percent increase in the data traffic, in "
                           "terabytes, each year",
                "any_year": "The estimated data traffic, in terabytes, for the year "
                            "that is t years after {y0}"}),
    dict(name="employees",
         stem="The equation E(t) = {a}({b})^t gives the estimated number of employees "
              "at a restaurant, where t is the number of years since the restaurant "
              "opened. Which of the following is the best interpretation of the "
              "number {a} in this context?",
         key="The estimated number of employees when the restaurant opened",
         wrong={"increase": "The increase in the estimated number of employees each "
                            "year",
                "years": "The number of years the restaurant has been open",
                "percent": "The percent increase in the estimated number of employees "
                           "each year"}),
    dict(name="beetles",
         stem="f(x) = {a}({b})^x An entomologist recommended a program to reduce a "
              "certain invasive beetle population in an area. The given function "
              "estimates this beetle species' population x years after {y0}, where "
              "x ≤ {cap}. Which of the following is the best interpretation of {a} in "
              "this context?",
         key="The estimated initial beetle population for this species and area in "
             "{y0}",
         wrong={"later": "The estimated beetle population for this species and area "
                         "{cap} years after {y0}",
                "percent": "The estimated percent decrease in the beetle population "
                           "for this species and area each year after {y0}",
                "percent_span": "The estimated percent decrease in the beetle "
                                "population for this species and area every {cap} "
                                "years after {y0}"}),
    dict(name="adverts",
         stem="f(x) = {a}({b})^x The given function f models the number of "
              "advertisements a company sent to its clients each year, where x "
              "represents the number of years since {y0}, and 0 ≤ x ≤ {cap}. If "
              "y = f(x) is graphed in the xy-plane, which of the following is the "
              "best interpretation of the y-intercept of the graph in this context?",
         key="The estimated number of advertisements the company sent to its clients "
             "in {y0} was {a}.",
         wrong={"min_last": "The minimum estimated number of advertisements the "
                            "company sent to its clients during the {cap} years was "
                            "{last}.",
                "min_first": "The minimum estimated number of advertisements the "
                             "company sent to its clients during the {cap} years was "
                             "{a}.",
                "last": "The estimated number of advertisements the company sent to "
                        "its clients in {y0} was {last}."}),
]
INITIAL_REASON = {
    "increase": "read the coefficient as the amount added each year",
    "percent": "read the coefficient as the percent change each year",
    "percent_span": "read the coefficient as a percent change over the whole period",
    "any_year": "read the coefficient as the value in any year rather than the first",
    "years": "read the coefficient as a count of years",
    "later": "read the coefficient as the value at the end of the period",
    "min_last": "gave the least value over the period rather than the value at the "
                "start",
    "min_first": "described the starting value as a minimum, which the y-intercept "
                 "does not claim",
    "last": "attached the value at the end of the period to the first year",
}


def interpret_initial(rng: random.Random, seed: int, *, ctx=None, a=None, b=None,
                      y0=None, cap=None, wrongs=None) -> object:
    """The number in front of the base: what it stands for in the situation."""
    d = INITIAL_CTX[rng.randrange(len(INITIAL_CTX))] if ctx is None else INITIAL_CTX[ctx]
    a = int(a if a is not None else rng.randrange(4, 99) * 100)
    b = q(b if b is not None else Q(rng.randrange(55, 195), 100))
    y0 = int(y0 if y0 is not None else rng.randrange(1990, 2016))
    cap = int(cap if cap is not None else rng.choice([5, 6, 7, 8]))
    if b == 1:
        raise ItemError("a model that never changes has nothing to interpret")
    # "the minimum during the N years" is the value at the last of those years
    last = (q(a) * b ** (cap - 1) + Q(1, 2)).__floor__()
    f = dict(a=num(a), b=dec(b), y0=year(y0), cap=num(cap), last=num(last))
    key = d["key"].format(**f)
    pool = {k_: (INITIAL_REASON[k_], pair(text.format(**f), k_))
            for k_, text in d["wrong"].items()}
    order = list(d["wrong"])
    v = "t" if d["name"] in ("traffic", "employees") else "x"
    why = (f"At {v} = 0 the power is 1, so {num(a)} is the model's value at the "
           f"start, in {year(y0)}.")
    P = {"kind": "nlf_interpret_initial", "ctx": d["name"], "a": a,
         "base": [b.numerator, b.denominator], "y0": y0, "cap": cap}
    return text_item("nlfunc.interpret_initial", "what the coefficient stands for",
                     "medium", seed, d["stem"].format(**f), key, sig("start"),
                     pick(pool, order, wrongs), rng, P, why)


# --------------------------------------- a rate whose unit is not the axis

RATE = ("N(d) = {a}({b})^d The function N defined above can be used to model the "
        "number of species of {thing} at various ocean depths d, where d is in "
        "{scale} of meters. Which of the following does the model predict?")
SCALES = {"hundreds": 100, "thousands": 1000}


def interpret_rate(rng: random.Random, seed: int, *, a=None, r=None, scale=None,
                   thing=None, wrongs=None) -> object:
    """The base says what happens per unit of d -- and d is not one metre."""
    thing = thing or rng.choice(["brachiopod", "coral", "sponge", "crinoid"])
    scale = scale or rng.choice(list(SCALES))
    step = SCALES[scale]
    a = int(a if a is not None else rng.randrange(40, 200))
    r = q(r if r is not None else Q(rng.randrange(5, 40), 100))
    base = 1 - r
    if base <= 0:
        raise ItemError("the model must still be positive")
    key = (f"For every increase in depth by {num(step)} meters, the number of "
           f"{thing} species decreases by {_pct(r)}.")
    pool = {
        "one_metre_pct": (f"attached the per-step percent to a single metre",
                          pair(f"For every increase in depth by 1 meter, the number "
                               f"of {thing} species decreases by {_pct(r)}.",
                               1, "percent")),
        "one_metre_count": ("read the coefficient as the number lost, and lost each "
                            "metre",
                            pair(f"For every increase in depth by 1 meter, the number "
                                 f"of {thing} species decreases by {num(a)}.",
                                 1, "count")),
        "step_count": ("read the coefficient as the number lost per step",
                       pair(f"For every increase in depth by {num(step)} meters, the "
                            f"number of {thing} species decreases by {num(a)}.",
                            step, "count")),
    }
    order = ["one_metre_pct", "one_metre_count", "step_count"]
    why = (f"Each increase of 1 in d multiplies the count by {dec(base, 2)}, a loss "
           f"of {_pct(r)}, and 1 in d is {num(step)} meters.")
    P = {"kind": "nlf_interpret_rate", "a": a, "r": [r.numerator, r.denominator],
         "step": step}
    return text_item("nlfunc.interpret_rate", "a rate whose unit is scaled", "medium",
                     seed, RATE.format(a=num(a), b=dec(base, 2), thing=thing + "s",
                                       scale=scale),
                     key, sig(step, "percent"), pick(pool, order, wrongs), rng, P, why)


# ----------------------------------- what a feature of a quadratic model means

FEATURE_NUMBER = ("{rule} The function above models the height h, in feet, of an "
                  "object above ground t seconds after being launched straight up in "
                  "the air. What does the number {c} represent in the function?")
FEATURE_KICK = ("An object is kicked from a platform. The equation h = {rule} "
                "represents this situation, where h is the height of the object above "
                "the ground, in meters, t seconds after it is kicked. Which number "
                "represents the height, in meters, from which the object was kicked?")
FEATURE_MONTH = ("y = {rule} The given equation models a company's scheduled "
                 "deliveries over {span} months, where y is the estimated number of "
                 "scheduled deliveries x months after the end of {month} {yr}, where "
                 "0 ≤ x ≤ {span}. Which statement is the best interpretation of the "
                 "y-intercept of the graph of this equation in the xy-plane?")
FEATURE_GRAPH = ("The graph shows a marble's height above the ground y, in inches, x "
                 "seconds after it started moving on an elevated track of a marble "
                 "run. Which of the following is the best interpretation of the "
                 "y-intercept of the graph?")
FEATURE_VERTEX = ("The function f(x) = ({frac})(x {MINUS} {h})² + {k} gives a metal "
                  "ball's height above the ground f(x), in inches, x seconds after it "
                  "started moving on a track, where 0 ≤ x ≤ {cap}. Which of the "
                  "following is the best interpretation of the vertex of the graph of "
                  "y = f(x) in the xy-plane?")
FEATURE_TIME = ("{rule} The quadratic function above models the height above the "
                "ground h, in feet, of a projectile x seconds after it had been "
                "launched vertically. If y = h(x) is graphed in the xy-plane, which "
                "of the following represents the real-life meaning of the positive "
                "x-intercept of the graph?")
FEATURE_PRICE = ("{rule} The revenue f(x), in dollars, that a company receives from "
                 "sales of a product is given by the function f above, where x is the "
                 "unit price, in dollars, of the product. The graph of y = f(x) in "
                 "the xy-plane intersects the x-axis at 0 and a. What does a "
                 "represent?")
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]


def quad_feature(rng: random.Random, seed: int, *, mode=None, a=None, b=None, c=None,
                 h=None, k=None, den=None, month=None, yr=None, span=None, cap=None,
                 wrongs=None) -> object:
    """The constant term, the vertex or the x-intercept, said in words."""
    mode = mode or rng.choice(["number", "kick", "month", "graph", "vertex", "time",
                               "price"])

    if mode in ("number", "kick"):
        a = q(a if a is not None else (-16 if mode == "number" else Q(-49, 10)))
        b = q(b if b is not None else rng.randrange(5, 140))
        c = q(c if c is not None else rng.randint(2, 99))
        if c <= 0 or b <= 0:
            raise ItemError("the model must start above the ground and rise")
        body = (poly_text([c, b, a], "t") if mode == "number"
                else f"{dec(a)}t² + {num(b)}t + {num(c)}")
        rule = f"h(t) = {body}" if mode == "number" else body
        unit = "feet" if mode == "number" else "meters"
        speed_unit = "feet per second" if mode == "number" else "meters per second"
        if mode == "number":
            key = f"The initial height, in {unit}, of the object"
            pool = {
                "max_height": ("named the greatest height rather than the starting "
                               "height", pair(f"The maximum height, in {unit}, of the "
                                              f"object", "max_height")),
                "initial_speed": ("named a speed, which the constant term is not",
                                  pair(f"The initial speed, in {speed_unit}, of the "
                                       f"object", "initial_speed")),
                "max_speed": ("named the greatest speed, which the model does not give",
                              pair(f"The maximum speed, in {speed_unit}, of the "
                                   f"object", "max_speed")),
            }
            order = ["max_height", "initial_speed", "max_speed"]
            stem = FEATURE_NUMBER.format(rule=rule, c=num(c))
            key_sig = sig("initial_height")
            why = (f"At t = 0 both terms with a t vanish, so {num(c)} is the height "
                   f"the object starts from.")
            P = {"kind": "nlf_quad_feature", "mode": mode,
                 "a": [a.numerator, a.denominator], "b": [b.numerator, b.denominator],
                 "c": [c.numerator, c.denominator]}
            return text_item("nlfunc.quad_feature",
                             "what a quadratic model's number means", "medium", seed,
                             stem, key, key_sig, pick(pool, order, wrongs), rng, P, why)

        pool = {
            "zero": ("gave 0, the height of the ground rather than of the platform",
                     q(0)),
            "coef": ("gave the size of the coefficient of t², which sets how fast the "
                     "object falls rather than where it starts", -a),
            "linear": ("gave the coefficient of t, which is the launch speed", b),
        }
        order = ["zero", "coef", "linear"]
        why = (f"At t = 0 both terms with a t vanish, so {num(c)} is the height the "
               f"object starts from.")
        P = {"kind": "nlf_quad_feature", "mode": mode,
             "a": [a.numerator, a.denominator], "b": [b.numerator, b.denominator],
             "c": [c.numerator, c.denominator]}
        return value_item("nlfunc.quad_feature", "which number is the initial height",
                          "medium", seed, FEATURE_KICK.format(rule=rule), c,
                          pick(pool, order, wrongs), rng, P, why, signed=True,
                          fmt_value=lambda v: dec(v) if q(v).denominator != 1 else num(v))

    if mode == "month":
        den = int(den if den is not None else rng.choice([2, 3, 4, 5]))
        b = q(b if b is not None else rng.randint(1, 6))
        c = q(c if c is not None else rng.randrange(12, 90))
        span = int(span if span is not None else rng.choice([6, 8, 10, 12]))
        month = MONTHS[rng.randrange(12)] if month is None else MONTHS[month]
        yr = int(yr if yr is not None else rng.randrange(2005, 2020))
        nxt = MONTHS[(MONTHS.index(month) + 1) % 12]
        rule = f"{MINUS}(1/{den})x² + {num(b)}x + {num(c)}"
        key = (f"At the end of {month} {year(yr)}, the estimated number of scheduled "
               f"deliveries was {num(c)}.")
        pool = {
            "zero_same": ("read the y-intercept as a zero of the model",
                          pair(f"At the end of {month} {year(yr)}, the estimated "
                               f"number of scheduled deliveries was 0.",
                               month, 0)),
            "zero_next": ("shifted the starting month on and read the value as zero",
                          pair(f"At the end of {nxt} {year(yr)}, the estimated number "
                               f"of scheduled deliveries was 0.", nxt, 0)),
            "next": ("shifted the starting month on by one",
                     pair(f"At the end of {nxt} {year(yr)}, the estimated number of "
                          f"scheduled deliveries was {num(c)}.", nxt, c)),
        }
        order = ["zero_same", "zero_next", "next"]
        stem = FEATURE_MONTH.format(rule=rule, span=num(span), month=month,
                                    yr=year(yr))
        why = (f"x counts months after the end of {month} {year(yr)}, so x = 0 is that "
               f"moment and the model gives {num(c)} there.")
        P = {"kind": "nlf_quad_feature", "mode": mode, "c": [c.numerator, c.denominator],
             "month": month, "yr": yr}
        return text_item("nlfunc.quad_feature", "what a y-intercept means in months",
                         "easy", seed, stem, key, sig(month, c),
                         pick(pool, order, wrongs), rng, P, why)

    if mode == "graph":
        h = int(h if h is not None else rng.randint(3, 7))
        k = int(k if k is not None else rng.randint(1, 4))
        start = int(c if c is not None else k + rng.randint(3, 7))
        aa = Q(start - k, h ** 2)
        if aa <= 0 or (aa * h ** 2).denominator != 1:
            raise ItemError("the drawn parabola must sit on whole-number gridlines")
        top = start + 2
        if top > 12:
            # eleven-odd labels on a 190-pixel axis touch each other; the
            # source's own marble chart runs to 10
            raise ItemError("the drawn height axis would need too many labels")

        def fnc(x, aa=float(aa), h=h, k=k):
            return aa * (x - h) ** 2 + k

        fig = context_curve(fnc, 0, 10, 0, top, xstep=1, ystep=1,
                            dots=[(0, start)])
        key = (f"The marble's height was {num(start)} inches above the ground when it "
               f"started moving.")
        pool = {
            "zero_at_h": ("read the y-intercept as a height of zero at the lowest "
                          "point", pair(f"The marble's height was 0 inches above the "
                                        f"ground {num(start)} seconds after it started "
                                        f"moving.", "zero", start)),
            "min_zero": ("described a minimum of zero, which the graph does not show",
                         pair("The marble's minimum height was 0 inches above the "
                              "ground.", "min", 0)),
            "min_start": ("called the starting height the minimum",
                          pair(f"The marble's minimum height was {num(start)} inches "
                               f"above the ground.", "min", start)),
        }
        order = ["zero_at_h", "min_zero", "min_start"]
        why = (f"The graph meets the vertical axis at {num(start)}, and x = 0 is the "
               f"moment the marble started moving.")
        P = {"kind": "nlf_quad_feature", "mode": mode, "start": start, "h": h, "k": k}
        return text_item("nlfunc.quad_feature", "what a y-intercept means on a graph",
                         "easy", seed, FEATURE_GRAPH, key, sig("start", start),
                         pick(pool, order, wrongs), rng, P, why, figure=fig)

    if mode == "vertex":
        den = int(den if den is not None else rng.choice([4, 9, 16, 25]))
        h = int(h if h is not None else rng.randint(2, 9))
        k = int(k if k is not None else rng.randint(1, 9))
        cap = int(cap if cap is not None else rng.choice([8, 10, 12]))
        if h >= cap:
            raise ItemError("the vertex must lie inside the stated interval")
        inch_k = unit_word(k, "inch", "inches")
        key = f"The metal ball's minimum height was {num(k)} {inch_k} above the ground."
        pool = {
            "min_h": ("read the vertex's x-coordinate as the height",
                      pair(f"The metal ball's minimum height was {num(h)} inches above "
                           f"the ground.", "min", h)),
            "start_k": ("read the vertex as the starting height",
                        pair(f"The metal ball's height was {num(k)} {inch_k} above the "
                             f"ground when it started moving.", "start", k)),
            "start_h": ("read the vertex's x-coordinate as a starting height",
                        pair(f"The metal ball's height was {num(h)} inches above the "
                             f"ground when it started moving.", "start", h)),
        }
        order = ["min_h", "start_k", "start_h"]
        stem = FEATURE_VERTEX.format(frac=f"1/{den}", MINUS=MINUS, h=num(h), k=num(k),
                                     cap=num(cap))
        why = (f"The square is never negative, so the least height is {num(k)} {inch_k}, "
               f"reached {num(h)} seconds in.")
        P = {"kind": "nlf_quad_feature", "mode": mode, "h": h, "k": k, "den": den}
        return text_item("nlfunc.quad_feature", "what a vertex means in context",
                         "hard", seed, stem, key, sig("min", k),
                         pick(pool, order, wrongs), rng, P, why)

    if mode == "time":
        a = q(a if a is not None else -16)
        b = q(b if b is not None else rng.randrange(40, 160))
        c = q(c if c is not None else rng.randint(2, 40))
        rule = f"h(x) = {poly_text([c, b, a])}"
        key = "The time at which the projectile hits the ground"
        pool = {
            "initial": ("named the starting height, which is the y-intercept",
                        pair("The initial height of the projectile", "initial")),
            "max": ("named the greatest height, which is the vertex's y-coordinate",
                    pair("The maximum height of the projectile", "max")),
            "time_max": ("named the time of the greatest height, which is the vertex's "
                         "x-coordinate",
                         pair("The time at which the projectile reaches its maximum "
                              "height", "time_max")),
        }
        order = ["initial", "max", "time_max"]
        why = ("An x-intercept is where the height is zero, and the positive one is "
               "when the projectile comes back down to the ground.")
        P = {"kind": "nlf_quad_feature", "mode": mode,
             "a": [a.numerator, a.denominator], "b": [b.numerator, b.denominator],
             "c": [c.numerator, c.denominator]}
        return text_item("nlfunc.quad_feature", "what an x-intercept means in context",
                         "hard", seed, FEATURE_TIME.format(rule=rule), key,
                         sig("ground_time"), pick(pool, order, wrongs), rng, P, why)

    a = q(a if a is not None else -rng.randrange(1, 20) * 100)
    b = q(b if b is not None else rng.randrange(5, 60) * 1000)
    rule = f"f(x) = {poly_text([0, b, a])}"
    key = "The unit price, in dollars, of the product that will result in a revenue of $0"
    pool = {
        "revenue_zero": ("named the revenue at a price of nothing, which is the other "
                         "intercept", pair("The revenue, in dollars, when the unit "
                                           "price of the product is $0", "revenue0")),
        "best_price": ("named the price at the vertex rather than at an x-intercept",
                       pair("The unit price, in dollars, of the product that will "
                            "result in maximum revenue", "best_price")),
        "max_revenue": ("named the greatest revenue, which is a y-value not an x-value",
                        pair("The maximum revenue, in dollars, that the company can "
                             "make", "max_revenue")),
    }
    order = ["revenue_zero", "best_price", "max_revenue"]
    why = ("An x-intercept of a revenue model is a price at which the revenue is zero.")
    P = {"kind": "nlf_quad_feature", "mode": "price",
         "a": [a.numerator, a.denominator], "b": [b.numerator, b.denominator]}
    return text_item("nlfunc.quad_feature", "what an x-intercept means for revenue",
                     "hard", seed, FEATURE_PRICE.format(rule=rule), key,
                     sig("zero_price"), pick(pool, order, wrongs), rng, P, why)
