"""Parabolas: where the turning point is, what it is worth, and how a few
printed facts pin the whole curve down.

Three surfaces appear in the source -- vertex form, standard form and factored
form -- and each has its own mistake. From a(x − h)² + k a student reads the
coefficient; from a factored form the average of the numbers printed inside
the brackets rather than of the zeros; from ax² + bx + c the ratio b/a with
the 2 left out. The pools below are those mistakes, named.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import ItemError, Mis
from ..common import (MINUS, dec, factored, fn, linear_factor, num, pair, pick,
                      point, poly_text, q, sig, signed, sup, text_item,
                      value_item)

__all__ = ["vertex_value", "vertex_symmetry", "shift_max", "quad_must_be_true",
           "quad_fit"]

NAMES = ["f", "g", "h", "p"]


OFFSETS = [(-2, -1, 3, 5, 6), (-3, -1, 2, 4, 7), (-4, -2, 1, 3, 5),
           (-6, -1, 4, 6, 9), (-2, -1, 1, 3, 4), (-5, -3, 2, 5, 8)]


def _decimal(v) -> str:
    """A decimal where the option set is decimals: 27, −0.28, 880."""
    return num(v) if q(v).denominator == 1 else dec(v)

VERTEX_MIN = "{rule} What is the minimum value of the given function?"
VERTEX_MIN2 = "What is the minimum value of the function {n} defined by {rule}?"
VERTEX_LOC = ("{rule} The function {n} is defined by the given equation. For what "
              "value of x does {n}(x) reach its minimum?")
VERTEX_LOC2 = ("{rule} The given equation defines the function {n}. For what value "
               "of x does {n}(x) reach its minimum?")
VERTEX_INT = ("The function {n} is defined by {rule}. The graph of {n} in the "
              "xy-plane is a parabola. Which of the following intervals contains the "
              "x-coordinate of the vertex of the graph of {n}?")
FAN = ("{rule} An engineer wanted to identify the best angle for a cooling fan in an "
       "engine in order to get the greatest airflow. The engineer discovered that "
       "the function above models the airflow {n}(θ), in cubic feet per minute, as a "
       "function of the angle of the fan θ, in degrees. According to the model, what "
       "angle, in degrees, gives the greatest airflow?")
TICKETS = ("An auditorium has seats for {seats} people. Tickets to attend a show at "
           "the auditorium currently cost {price}. For each $1.00 increase to the "
           "ticket price, {drop} fewer tickets will be sold. This situation can be "
           "modeled by the equation y = {rule}, where x represents the increase in "
           "ticket price, in dollars, and y represents the revenue, in dollars, from "
           "ticket sales. If this equation is graphed in the xy-plane, at what value "
           "of x is the maximum of the graph?")


def vertex_value(rng: random.Random, seed: int, *, form=None, ask=None, name=None,
                 a=None, h=None, k=None, b=None, c=None, r1=None, r2=None, seats=None,
                 price=None, fmt="mcq", wrongs=None) -> object:
    """The turning point of a parabola: where it is, or what it is worth."""
    form = form or rng.choice(["vertex", "standard", "factored", "fan", "tickets"])
    ask = ask or rng.choice(["value", "location"])
    name = name or rng.choice(NAMES)

    if form == "fan":
        a = q(a if a is not None else -Q(rng.randrange(8, 60), 100))
        h = q(h if h is not None else rng.randint(10, 80))
        k = q(k if k is not None else rng.randrange(20, 200) * 10)
        if a >= 0 or h <= 0 or k <= 0:
            raise ItemError("the airflow model must peak at a positive angle")
        rule = fn(name, "θ", f"{dec(a)}(θ {MINUS} {num(h)})² + {num(k)}")
        key = h
        pool = {
            "coef": ("gave the coefficient outside the square", a),
            "abs_coef": ("gave the coefficient with its sign dropped", -a),
            "value": ("gave the greatest airflow rather than the angle at which it "
                      "happens", k),
        }
        order = ["coef", "abs_coef", "value"]
        why = (f"The square is never negative and its coefficient is negative, so the "
               f"airflow is greatest when θ {MINUS} {num(h)} = 0, that is at "
               f"θ = {num(h)}.")
        P = {"kind": "nlf_vertex", "form": form, "ask": "location",
             "a": [a.numerator, a.denominator], "h": [h.numerator, h.denominator],
             "k": [k.numerator, k.denominator]}
        return value_item("nlfunc.vertex_value", "the angle that maximises a model",
                          "medium", seed, FAN.format(rule=rule, n=name), key,
                          pick(pool, order, wrongs), rng, P, why, fmt=fmt,
                          fmt_value=_decimal)

    if form == "tickets":
        drop = int(a if a is not None else rng.choice([50, 100, 200]))
        seats = int(seats if seats is not None else drop * rng.randint(9, 20))
        price = q(price if price is not None else rng.randint(2, 9))
        aa = q(-drop)
        bb = q(seats) - drop * price
        cc = q(seats) * price
        if bb <= 0:
            raise ItemError("the revenue model must still rise at x = 0")
        key = -bb / (2 * aa)
        if key.denominator != 1:
            raise ItemError("the printed maximum must fall on a whole dollar")
        rule = poly_text([cc, bb, aa])
        pool = {
            "no_two": ("divided by the coefficient without the factor of 2",
                       -bb / aa),
            "price": ("gave the current ticket price", price),
            "seats_over_drop": ("divided the number of seats by the drop per dollar",
                                q(seats) / drop),
            "half_price": ("halved the current ticket price", price / 2),
        }
        order = ["price", "no_two", "seats_over_drop", "half_price"]
        why = (f"The maximum of a parabola is at x = {MINUS}b/(2a) = "
               f"{num(bb)}/{num(2 * drop)} = {num(key)}.")
        P = {"kind": "nlf_vertex", "form": form, "ask": "location",
             "a": [aa.numerator, aa.denominator], "b": [bb.numerator, bb.denominator],
             "c": [cc.numerator, cc.denominator]}
        return value_item("nlfunc.vertex_value", "the price that maximises revenue",
                          "hard", seed,
                          TICKETS.format(seats=num(seats), price="$" + dec(price, 2),
                                         drop=num(drop), rule=rule),
                          key, pick(pool, order, wrongs), rng, P, why, fmt=fmt,
                          signed=False)

    if form == "vertex":
        a = q(a if a is not None else rng.choice([1, 1, 2, 3, -1, -2]))
        h = q(h if h is not None else rng.randint(-9, 9))
        k = q(k if k is not None else rng.randint(-40, 60))
        if a == 0 or h == 0 or k == 0:
            raise ItemError("every number in the vertex form must be visible")
        if a < 0:
            raise ItemError("a minimum needs an upward-opening parabola")
        body = (f"(x {MINUS} {num(h)})²" if h > 0 else f"(x + {num(-h)})²")
        body = (body if a == 1 else f"{num(a)}{body}")
        rule = fn(name, "x", f"{body} {'+' if k > 0 else MINUS} {num(abs(k))}")
        key = k if ask == "value" else h
        pool = {
            "other": ("gave the other coordinate of the vertex", h if ask == "value" else k),
            "flip": ("changed the sign of the answer", -key),
            "flip_other": ("changed the sign of the other coordinate",
                           -h if ask == "value" else -k),
            "half": ("halved the answer", key / 2),
            "coef": ("gave the coefficient outside the square", a if a != 1 else None),
        }
        order = ["other", "flip", "flip_other", "half", "coef"]
        why = (f"The square is never negative, so {name} is least when x = {num(h)}, "
               f"where {name}(x) = {num(k)}.")
        P = {"kind": "nlf_vertex", "form": form, "ask": ask,
             "a": [a.numerator, a.denominator], "h": [h.numerator, h.denominator],
             "k": [k.numerator, k.denominator]}
        stem = (VERTEX_MIN2.format(n=name, rule=rule) if ask == "value"
                else VERTEX_LOC.format(rule=rule, n=name))
        return value_item("nlfunc.vertex_value", "the vertex of a parabola", "hard",
                          seed, stem, key, pick(pool, order, wrongs), rng, P, why,
                          fmt=fmt)

    if form == "standard":
        a = q(a if a is not None else rng.choice([1, 2, 3, 4]))
        b = q(b if b is not None else rng.choice([0, rng.randint(-60, 60)]))
        c = q(c if c is not None else rng.randint(-40, 140))
        if a <= 0 or c == 0:
            raise ItemError("the printed quadratic must open upward and show a constant")
        if ask == "location" and b == 0:
            raise ItemError("a missing middle term makes the vertex trivially zero")
        key = (-b / (2 * a)) if ask == "location" else (c - b ** 2 / (4 * a))
        rule = fn(name, "x", poly_text([c, b, a]))
        pool = {
            "constant": ("gave the constant term", c if c != key else None),
            "no_two": ("divided by the coefficient without the factor of 2",
                       -b / a if b != 0 else None),
            "double": ("doubled the answer", 2 * key),
            "swap_coefs": (f"swapped the two coefficients in {MINUS}b/(2a)",
                           -a / (2 * b) if (b != 0 and ask == "location") else None),
            "square": ("squared the constant term", c ** 2 if ask == "value" else None),
            "zero": ("assumed the least value of a square is the whole function",
                     q(0) if ask == "value" else None),
            "flip": ("changed the sign of the answer", -key),
        }
        # the swapped coefficients always carry the key's own sign, so a
        # fractional vertex is never the only fraction of its sign
        order = (["swap_coefs", "no_two", "double", "constant", "flip"]
                 if ask == "location"
                 else ["double", "zero", "square", "constant", "flip"])
        why = (f"The vertex of {rule} is at x = {num(-b / (2 * a))}, where "
               f"{name}(x) = {num(c - b ** 2 / (4 * a))}.")
        P = {"kind": "nlf_vertex", "form": form, "ask": ask,
             "a": [a.numerator, a.denominator], "b": [b.numerator, b.denominator],
             "c": [c.numerator, c.denominator]}
        stem = (VERTEX_MIN.format(rule=rule) if ask == "value"
                else VERTEX_LOC2.format(rule=rule, n=name))
        return value_item("nlfunc.vertex_value", "the vertex of a parabola", "hard",
                          seed, stem, key, pick(pool, order, wrongs), rng, P, why,
                          fmt=fmt)

    # factored: (x − r1)(x − r2)
    r1 = q(r1 if r1 is not None else rng.randint(-20, 20))
    r2 = q(r2 if r2 is not None else rng.randint(-20, 20))
    if r1 == r2 or r1 == 0 or r2 == 0:
        raise ItemError("the two zeros must differ and neither may be the origin")
    rule = fn(name, "x", factored([(1, -r1, 1), (1, -r2, 1)]))
    mid = (r1 + r2) / 2
    if ask == "interval":
        if mid.denominator != 1:
            raise ItemError("the drawn boundaries must be whole numbers")
        offsets = OFFSETS[rng.randrange(len(OFFSETS))] if seats is None \
            else OFFSETS[seats % len(OFFSETS)]
        cuts = [mid + o for o in offsets]
        key = f"{num(cuts[1])} < x < {num(cuts[2])}"
        pool = {
            "left": ("chose the interval to the left of the one holding the vertex",
                     pair(f"{num(cuts[0])} < x < {num(cuts[1])}", cuts[0], cuts[1])),
            "right": ("chose the interval to the right of the one holding the vertex",
                      pair(f"{num(cuts[2])} < x < {num(cuts[3])}", cuts[2], cuts[3])),
            "far": ("chose the interval furthest from the vertex",
                    pair(f"{num(cuts[3])} < x < {num(cuts[4])}", cuts[3], cuts[4])),
        }
        order = ["left", "right", "far"]
        why = (f"The vertex sits halfway between the zeros {num(r1)} and {num(r2)}, "
               f"at x = {num(mid)}.")
        P = {"kind": "nlf_vertex", "form": form, "ask": ask,
             "r1": [r1.numerator, r1.denominator], "r2": [r2.numerator, r2.denominator],
             "cuts": [[c.numerator, c.denominator] for c in cuts]}
        return text_item("nlfunc.vertex_value", "which interval holds the vertex",
                         "hard", seed, VERTEX_INT.format(n=name, rule=rule), key,
                         sig(cuts[1], cuts[2]), pick(pool, order, wrongs), rng, P, why)

    key = mid if ask == "location" else (mid - r1) * (mid - r2)
    pool = {
        "product": ("multiplied the zeros instead of averaging them", r1 * r2),
        "one_zero": ("gave one of the zeros", r2),
        "flip_first": ("changed the sign of one of the zeros before averaging them",
                       (-r1 + r2) / 2),
        "printed_average": ("averaged the numbers printed inside the brackets rather "
                            "than the zeros", (-r1 - r2) / 2),
        "sum": ("added the zeros without halving", r1 + r2),
    }
    order = ["product", "one_zero", "flip_first", "printed_average", "sum"]
    why = (f"The zeros are {num(r1)} and {num(r2)}, so the vertex is halfway between "
           f"them at x = {num(mid)}.")
    P = {"kind": "nlf_vertex", "form": form, "ask": ask,
         "r1": [r1.numerator, r1.denominator], "r2": [r2.numerator, r2.denominator]}
    stem = (VERTEX_MIN2.format(n=name, rule=rule) if ask == "value"
            else VERTEX_LOC.format(rule=rule, n=name))
    return value_item("nlfunc.vertex_value", "the vertex of a factored quadratic",
                      "hard", seed, stem, key, pick(pool, order, wrongs), rng, P, why,
                      fmt=fmt)


# ------------------------------------------------------------- symmetry

OTHER_INT = ("When the quadratic function {n} is graphed in the xy-plane, where "
             "y = {n}(x), its vertex is {vertex}. One of the x-intercepts of this "
             "graph is {given}. What is the other x-intercept of the graph?")
MIDPOINT = ("Function {n} is a quadratic function where {n}({r1}) = 0 and "
            "{n}({r2}) = 0. The graph of y = {n}(x) in the xy-plane has a vertex at "
            "(r, {k}). What is the value of r?")


def vertex_symmetry(rng: random.Random, seed: int, *, mode=None, h=None, k=None,
                    p=None, r1=None, r2=None, name=None, wrongs=None) -> object:
    """Two facts about a parabola, joined by its line of symmetry."""
    mode = mode or rng.choice(["other_intercept", "midpoint"])
    name = name or rng.choice(NAMES)

    if mode == "other_intercept":
        h = q(h if h is not None else rng.randint(-9, 9))
        k = q(k if k is not None else rng.choice([rng.randint(-9, -1), rng.randint(1, 9)]))
        d = q(p if p is not None else Q(rng.choice([1, 3, 5, 7, 9, 11]),
                                        rng.choice([2, 4])))
        if d <= 0:
            raise ItemError("the distance from the vertex must be positive")
        given = h - d
        other = h + d
        key = point(other, 0)
        pool = {
            "sum": ("added the vertex's x-coordinate to the given intercept instead "
                    "of reflecting", pair(point(given + h, 0), given + h, 0)),
            "flip_sum": ("changed the sign of the given intercept before adding the "
                         "vertex", pair(point(-given + h, 0), -given + h, 0)),
            "negate": ("changed the sign of the given intercept",
                       pair(point(-given, 0), -given, 0)),
            "double": ("doubled the given intercept", pair(point(2 * given, 0),
                                                           2 * given, 0)),
        }
        order = ["sum", "flip_sum", "negate", "double"]
        why = (f"The vertex is {num(d)} to the right of {num(given)}, so the other "
               f"intercept is {num(d)} to the right of the vertex, at {key}.")
        P = {"kind": "nlf_symmetry", "mode": mode, "h": [h.numerator, h.denominator],
             "given": [given.numerator, given.denominator]}
        return text_item("nlfunc.vertex_symmetry", "the other x-intercept", "hard",
                         seed, OTHER_INT.format(n=name, vertex=point(h, k),
                                                given=point(given, 0)),
                         key, sig(other, 0), pick(pool, order, wrongs), rng, P, why)

    r1 = q(r1 if r1 is not None else rng.randint(-30, 10))
    r2 = q(r2 if r2 is not None else r1 + 2 * rng.randint(2, 12))
    k = q(k if k is not None else -rng.randrange(4, 200))
    if r1 == r2:
        raise ItemError("the two zeros must differ")
    key = (r1 + r2) / 2
    why = (f"A parabola is symmetric about its vertex, so r is halfway between "
           f"{num(r1)} and {num(r2)}: r = {num(key)}.")
    P = {"kind": "nlf_symmetry", "mode": "midpoint",
         "r1": [r1.numerator, r1.denominator], "r2": [r2.numerator, r2.denominator]}
    return value_item("nlfunc.vertex_symmetry", "the axis of symmetry from two zeros",
                      "hard", seed, MIDPOINT.format(n=name, r1=num(r1), r2=num(r2),
                                                    k=num(k)),
                      key, [], rng, P, why, fmt="spr")


# ------------------------------------------------ a shifted maximum, in symbols

SHIFT = ("{rule} The function f is defined by the given equation. The function g is "
         "defined by g(t) = f(t) + {k}. Which expression represents the maximum "
         "value of g(t)?")


def shift_max(rng: random.Random, seed: int, *, a=None, b=None, k=None,
              wrongs=None) -> object:
    """f(t) = bt − at², lifted by k; the answer stays in symbols."""
    a = q(a if a is not None else rng.randint(2, 9))
    b = q(b if b is not None else rng.randrange(11, 99))
    k = q(k if k is not None else rng.randint(2, 15))
    if a <= 0 or b <= 0 or (b / (2 * a)).denominator == 1:
        raise ItemError("the half-way point must print as a fraction")
    t = b / (2 * a)
    rule = f"f(t) = {num(b)}t {MINUS} {num(a)}t²"
    body = f"({num(t)})²"
    key = f"{num(k)} + {num(a)}{body}"
    pool = {
        "no_coef": ("left the coefficient out when squaring the half-way point",
                    pair(f"{num(k)} + {body}", k, 1)),
        "minus_coef": ("subtracted the squared term instead of adding it",
                       pair(f"{num(k)} {MINUS} {num(a)}{body}", k, -a)),
        "minus_plain": ("subtracted the squared term and left the coefficient out",
                        pair(f"{num(k)} {MINUS} {body}", k, -1)),
        "double": ("doubled the coefficient", pair(f"{num(k)} + {num(2 * a)}{body}",
                                                    k, 2 * a)),
    }
    order = ["no_coef", "minus_coef", "minus_plain", "double"]
    raw = f"{num(b)}/{num(2 * a)}"
    at = raw if raw == num(t) else f"{raw} = {num(t)}"
    why = (f"f is greatest at t = {at}, where it equals {num(a)}({num(t)})², so g is "
           f"greatest at {num(k)} + {num(a)}({num(t)})².")
    P = {"kind": "nlf_shift_max", "a": [a.numerator, a.denominator],
         "b": [b.numerator, b.denominator], "k": [k.numerator, k.denominator]}
    return text_item("nlfunc.shift_max", "a maximum written as an expression", "hard",
                     seed, SHIFT.format(rule=rule, k=num(k)), key, sig(k, a),
                     pick(pool, order, wrongs), rng, P, why)


# ------------------------------------------------------- what must be true

MUST = ("{rule} In the given quadratic function, a and c are constants. The graph of "
        "y = f(x) in the xy-plane is a parabola that opens upward and has a vertex at "
        "the point (h, k), where h and k are constants. I. {one} II. {two} If k < 0 "
        "and f({p}) = f({qv}), which of the following must be true?")
MUST_ANSWERS = {(True, False): "I only", (False, True): "II only",
                (True, True): "I and II", (False, False): "Neither I nor II"}


def quad_must_be_true(rng: random.Random, seed: int, *, b=None, p=None, qv=None,
                      t=None, first=None, wrongs=None) -> object:
    """Two claims about a parabola pinned by a vertex, an axis and a sign."""
    b = q(b if b is not None else rng.choice([2, 3, 4, 5, 6, 8]))
    p = q(p if p is not None else rng.randint(-12, 0))
    qv = q(qv if qv is not None else rng.randint(1, 12))
    if p == qv:
        raise ItemError("the two inputs must differ")
    h = (p + qv) / 2
    if h == 0:
        raise ItemError("a vertex on the y-axis leaves the coefficient undetermined")
    a = -b / (2 * h)
    if a <= 0:
        raise ItemError("the parabola must open upward")
    t = q(t if t is not None else rng.choice([1, 2, 3]))
    first = first or rng.choice(["c_neg", "a_pos", "h_neg"])
    claims = {"c_neg": ("c < 0", False),
              "a_pos": ("a > 0", True),
              "h_neg": (f"h < 0", h < 0)}
    one_text, one_true = claims[first]
    two_text, two_true = f"a ≥ {num(t)}", a >= t
    key = MUST_ANSWERS[(bool(one_true), bool(two_true))]
    pool = {}
    for combo, text in MUST_ANSWERS.items():
        if text == key:
            continue
        pool[text] = (f"claims {text}, which the printed facts do not force",
                      pair(text, 1 if combo[0] else 0, 1 if combo[1] else 0))
    order = [t_ for t_ in ("I only", "II only", "I and II", "Neither I nor II")
             if t_ != key]
    rule = f"f(x) = ax² + {num(b)}x + c"
    why = (f"f({num(p)}) = f({num(qv)}) puts the vertex at h = {num(h)}, so "
           f"a = {MINUS}{num(b)}/(2 · {num(h)}) = {num(a)}; k < 0 only bounds c from "
           f"above.")
    P = {"kind": "nlf_must_be_true", "b": [b.numerator, b.denominator],
         "p": [p.numerator, p.denominator], "q": [qv.numerator, qv.denominator],
         "t": [t.numerator, t.denominator], "first": first}
    return text_item("nlfunc.quad_must_be_true", "what a parabola's facts force",
                     "hard", seed,
                     MUST.format(rule=rule, p=num(p), qv=num(qv), one=one_text,
                                 two=two_text),
                     key, sig(1 if one_true else 0, 1 if two_true else 0),
                     pick(pool, order, wrongs), rng, P, why)


# ------------------------------------------------ fitting a parabola to facts

FIT_VALUE = ("A quadratic function models the height, in feet, of an object above "
             "the ground in terms of the time, in seconds, after the object is "
             "launched off an elevated surface. The model indicates the object has "
             "an initial height of {y0} feet above the ground and reaches its maximum "
             "height of {k} feet above the ground {h} seconds after being launched. "
             "Based on the model, what is the height, in feet, of the object above "
             "the ground {t} seconds after being launched?")
FIT_EQUATION = ("A machine launches a softball from ground level. The softball "
                "reaches a maximum height of {k} meters above the ground at {h} "
                "seconds and hits the ground at {g} seconds. Which equation "
                "represents the height above ground h, in meters, of the softball t "
                "seconds after it is launched?")
FIT_POINTS = ("The total distance d, in meters, traveled by an object moving in a "
              "straight line can be modeled by a quadratic function that is defined "
              "in terms of t, where t is the time in seconds. At a time of {t1} "
              "seconds, the total distance traveled by the object is {d1} meters, and "
              "at a time of {t2} seconds, the total distance traveled by the object "
              "is {d2} meters. If the object was at a distance of 0 meters when "
              "t = 0, then what is the total distance traveled, in meters, by the "
              "object after {t3} seconds?")
FIT_TABLE = ("The table shows three values of x and their corresponding values of y, "
             "where y = {n}(x) + {s} and {n} is a quadratic function. What is the "
             "y-coordinate of the y-intercept of the graph of y = {n}(x) in the "
             "xy-plane?")


def quad_fit(rng: random.Random, seed: int, *, mode=None, y0=None, k=None, h=None,
             t=None, t1=None, d1=None, t2=None, t3=None, x0=None, step=None, s=None,
             aa=None, name=None, fmt="mcq", wrongs=None) -> object:
    """A parabola recovered from an initial value, a vertex, or three points."""
    mode = mode or rng.choice(["vertex_value", "vertex_equation", "three_points",
                               "table"])

    if mode == "vertex_value":
        h = q(h if h is not None else rng.randint(3, 12))
        y0 = q(y0 if y0 is not None else rng.choice([5, 8, 10, 12, 20]))
        a = q(aa if aa is not None else -rng.choice([4, 8, 16]))
        k = y0 - a * h ** 2
        t = q(t if t is not None else h + rng.randint(1, 5))
        key = k + a * (t - h) ** 2
        if key <= 0:
            raise ItemError("the object must still be above the ground")
        pool = {
            "coef_sq": ("subtracted the square of the coefficient rather than the "
                        "square of the time past the vertex", k - a ** 2),
            "vertex_as_coef": ("used the vertex's time as the coefficient and the time "
                               "itself as the distance", k - h * t ** 2),
            "linear": ("multiplied the time past the vertex by the initial height "
                       "instead of squaring and scaling", k - (t - h) * y0),
            "at_vertex": ("gave the greatest height rather than the height at the "
                          "stated time", k),
        }
        order = ["vertex_as_coef", "coef_sq", "linear", "at_vertex"]
        stem = FIT_VALUE.format(y0=num(y0), k=num(k), h=num(h), t=num(t))
        why = (f"The model is {num(k)} {MINUS} {num(-a)}(t {MINUS} {num(h)})², so at "
               f"t = {num(t)} the height is {num(k)} {MINUS} "
               f"{num(-a * (t - h) ** 2)} = {num(key)}.")
        P = {"kind": "nlf_quad_fit", "mode": mode, "y0": [y0.numerator, y0.denominator],
             "h": [h.numerator, h.denominator], "a": [a.numerator, a.denominator],
             "t": [t.numerator, t.denominator]}
        return value_item("nlfunc.quad_fit", "a height from a fitted parabola", "hard",
                          seed, stem, key, pick(pool, order, wrongs), rng, P, why,
                          fmt=fmt, signed=False)

    if mode == "vertex_equation":
        a = q(aa if aa is not None else -16)
        h = q(h if h is not None else Q(rng.randrange(10, 40), 10))
        k = -a * h ** 2
        g = 2 * h
        key = f"h = {MINUS}{num(-a)}(t {MINUS} {dec(h)})² + {dec(k)}"
        pool = {
            "plain_ground": ("kept only the time the softball lands",
                             pair(f"h = {MINUS}t² + {dec(g)}", 1, 0, g)),
            "plain_max": ("kept only the greatest height",
                          pair(f"h = {MINUS}t² + {dec(k)}", 1, 0, k)),
            "swapped": ("put the greatest height inside the bracket and the landing "
                        "time outside",
                        pair(f"h = {MINUS}{num(-a)}(t + {dec(k)})² {MINUS} {dec(g)}",
                             -a, -k, -g)),
            "no_shift": ("left the time of the maximum out of the bracket",
                         pair(f"h = {MINUS}{num(-a)}t² + {dec(k)}", -a, 0, k)),
        }
        order = ["plain_ground", "plain_max", "swapped", "no_shift"]
        stem = FIT_EQUATION.format(k=dec(k), h=dec(h), g=dec(g))
        why = (f"The vertex is ({dec(h)}, {dec(k)}) and the curve returns to the "
               f"ground at t = {dec(g)}, which needs a coefficient of {num(a)}.")
        P = {"kind": "nlf_quad_fit", "mode": mode, "a": [a.numerator, a.denominator],
             "h": [h.numerator, h.denominator]}
        return text_item("nlfunc.quad_fit", "an equation from a vertex and a zero",
                         "hard", seed, stem, key, sig(-a, h, k),
                         pick(pool, order, wrongs), rng, P, why)

    if mode == "three_points":
        a = q(aa if aa is not None else Q(rng.randrange(1, 20), 10))
        b = q(k if k is not None else Q(rng.randrange(0, 40), 10))
        t1 = q(t1 if t1 is not None else rng.randrange(5, 20) * 1)
        t2 = q(t2 if t2 is not None else 2 * t1)
        t3 = q(t3 if t3 is not None else 3 * t1)
        d1, d2 = a * t1 ** 2 + b * t1, a * t2 ** 2 + b * t2
        key = a * t3 ** 2 + b * t3
        for v in (d1, d2, key):
            if (v * 10).denominator != 1:
                raise ItemError("every printed distance must land on a tenth")
        stem = FIT_POINTS.format(t1=dec(t1, 1), d1=dec(d1, 1), t2=dec(t2, 1),
                                 d2=dec(d2, 1), t3=dec(t3, 1))
        why = (f"Fitting d = at² + bt to the two readings gives a = {dec(a)} and "
               f"b = {dec(b)}, so d({dec(t3, 1)}) = {dec(key, 1)}.")
        P = {"kind": "nlf_quad_fit", "mode": mode,
             "t1": [t1.numerator, t1.denominator], "d1": [d1.numerator, d1.denominator],
             "t2": [t2.numerator, t2.denominator], "d2": [d2.numerator, d2.denominator],
             "t3": [t3.numerator, t3.denominator]}
        return value_item("nlfunc.quad_fit", "a quadratic through three points",
                          "hard", seed, stem, key, [], rng, P, why, fmt="spr")

    name = name or rng.choice(NAMES)
    x0 = q(x0 if x0 is not None else rng.randint(8, 40))
    step = q(step if step is not None else rng.randint(1, 4))
    a = q(aa if aa is not None else rng.choice([-4, -2, -1, 1, 2, 4]))
    s = q(s if s is not None else rng.randint(1, 9))
    peak = q(t if t is not None else rng.randint(-12, 12))
    table = [["x", "y"]]
    for dx in (-step, q(0), step):
        table.append([num(x0 + dx), num(a * dx ** 2 + peak + s)])
    key = a * x0 ** 2 + peak
    if abs(key) >= 100000:
        raise ItemError("the answer would be too long to grid in")
    head = f"{num(a)}" if abs(a) != 1 else ("" if a == 1 else MINUS)
    shape = signed(f"{head}(x {MINUS} {num(x0)})²", peak)
    why = (f"The table is symmetric about x = {num(x0)}, so {name}(x) = {shape} and "
           f"{name}(0) = {num(key)}.")
    P = {"kind": "nlf_quad_fit", "mode": "table", "x0": [x0.numerator, x0.denominator],
         "step": [step.numerator, step.denominator], "a": [a.numerator, a.denominator],
         "peak": [peak.numerator, peak.denominator], "s": [s.numerator, s.denominator]}
    return value_item("nlfunc.quad_fit", "a y-intercept from a shifted table", "hard",
                      seed, FIT_TABLE.format(n=name, s=num(s)), key, [], rng, P, why,
                      fmt="spr", table=table)
