"""Where a curve meets an axis, read off the rule rather than off a picture.

The options here are points and expressions, not values, so every item is
assembled with `text_item` and every option carries the signature the
independent solver in `audit.py` recomputes: a point's two coordinates, or the
name of the identity a statement asserts. The printed string is never compared
with the key's string.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import ItemError, Mis
from ..common import (MINUS, dec, factored, fn, num, pair, pick, point, poly_text,
                      power, q, sig, text_item, value_item)

__all__ = ["y_intercept", "x_intercept"]

NAMES = ["f", "g", "h", "p"]

Y_SPR = [
    "The y-intercept of the graph of y = {body} in the xy-plane is (0, y). What is "
    "the value of y?",
    "{rule} For the given function {n}, the graph of y = {n}(x) in the xy-plane "
    "passes through the point (0, b), where b is a constant. What is the value of b?",
]
Y_MCQ = ("{rule} If the given function {n} is graphed in the xy-plane, where "
         "y = {n}(x), what is the y-intercept of the graph?")
Y_ID = [
    "In the xy-plane, the y-coordinate of the y-intercept of the graph of the "
    "function {n} is c. Which of the following must be equal to c?",
    "In the xy-plane, the graph of the function {n} passes through the point (0, c), "
    "where c is a constant. Which of the following must be equal to c?",
    "The graph of y = {n}(x) in the xy-plane has a y-intercept of (0, c). Which of "
    "the following must be equal to c?",
]


def y_intercept(rng: random.Random, seed: int, *, mode=None, name=None, frame=None,
                n=None, k=None, mid=None, a=None, base=None, others=None,
                wrongs=None) -> object:
    """The y-intercept of a printed rule: a value, a point, or f(0) itself."""
    mode = mode or rng.choice(["poly", "expo", "identity"])
    name = name or rng.choice(NAMES)

    if mode == "poly":
        frame = rng.randrange(len(Y_SPR)) if frame is None else frame
        n = int(n if n is not None else rng.choice([2, 3, 4, 5]))
        k = q(k if k is not None else rng.randint(-60, 60))
        mid = q(mid if mid is not None else rng.choice([0, 0, rng.randint(-9, 9)]))
        if k == 0:
            raise ItemError("the y-intercept must not be the origin")
        coeffs = [k] + [mid] + [0] * (n - 2) + [1]
        body = poly_text(coeffs)
        rule = fn(name, "x", body)
        why = (f"At x = 0 every term with an x vanishes, so the y-intercept is "
               f"(0, {num(k)}).")
        P = {"kind": "nlf_y_intercept", "mode": mode, "n": n,
             "k": [k.numerator, k.denominator], "mid": [mid.numerator, mid.denominator]}
        stem = Y_SPR[frame].format(body=body, rule=rule, n=name)
        return value_item("nlfunc.y_intercept", "the y-intercept of a curve", "easy",
                          seed, stem, k, [], rng, P, why, fmt="spr")

    if mode == "expo":
        a = q(a if a is not None else rng.randint(2, 60))
        base = q(base if base is not None else rng.choice(
            [Q(1, rng.randint(2, 12)), Q(rng.randint(2, 9)), Q(rng.randint(11, 49), 10)]))
        if a <= 0 or base <= 0 or base == 1:
            raise ItemError("an exponential needs a positive base other than 1")
        body = f"{num(a)}({num(base)})^x"
        rule = fn(name, "x", body)
        key = point(0, a)
        pool = {
            "times_recip": ("multiplied the coefficient by the reciprocal of the base",
                            pair(point(0, a / base), 0, a / base)),
            "one": ("gave the power alone, which is 1 at x = 0", pair(point(0, 1), 0, 1)),
            "recip": ("gave the reciprocal of the base rather than the coefficient",
                      pair(point(0, 1 / base), 0, 1 / base)),
            "times_base": ("multiplied the coefficient by the base",
                           pair(point(0, a * base), 0, a * base)),
            "swapped": ("wrote the coefficient as the x-coordinate",
                        pair(point(a, 0), a, 0)),
        }
        order = ["times_recip", "one", "recip", "times_base", "swapped"]
        why = (f"Any nonzero base raised to the power 0 is 1, so {name}(0) = "
               f"{num(a)} and the y-intercept is {key}.")
        P = {"kind": "nlf_y_intercept", "mode": mode, "a": [a.numerator, a.denominator],
             "base": [base.numerator, base.denominator]}
        return text_item("nlfunc.y_intercept", "the y-intercept of an exponential",
                         "medium", seed, Y_MCQ.format(rule=rule, n=name), key,
                         sig(0, a), pick(pool, order, wrongs), rng, P, why)

    frame = rng.randrange(len(Y_ID)) if frame is None else frame
    others = list(others) if others else rng.sample([1, 2, 3, 4, 5, 6], 3)
    key = f"{name}(0)"
    pool = {}
    for v in others:
        pool[f"at{v}"] = (f"read the y-intercept as the value of {name} at x = {v}",
                          pair(f"{name}({v})", v))
    order = [f"at{v}" for v in others]
    why = (f"A point on the y-axis has x = 0, so its y-coordinate is {name}(0).")
    P = {"kind": "nlf_y_intercept", "mode": "identity", "name": name}
    return text_item("nlfunc.y_intercept", "what a y-intercept is", "medium", seed,
                     Y_ID[frame].format(n=name), key, sig(0),
                     pick(pool, order, wrongs), rng, P, why)


# ------------------------------------------------------------ x-intercepts

X_SPR = ("{rule} If the given function {n} is graphed in the xy-plane, where "
         "y = {n}(x), what is the x-coordinate of an x-intercept of the graph?")
X_MCQ = ("{rule} If the given function {n} is graphed in the xy-plane, where "
         "y = {n}(x), what is an x-intercept of the graph?")
X_NOT = ("{rule} The function {n} is defined above. Which of the following is NOT an "
         "x-intercept of the graph of the function in the xy-plane?")
X_VERTEX = ("{rule} The quadratic function {n} is defined as shown. In the xy-plane, "
            "the graph of y = {n}(x) intersects the x-axis at the points (0, 0) and "
            "(t, 0), where t is a constant. What is the value of t?")


def x_intercept(rng: random.Random, seed: int, *, mode=None, name=None, r1=None,
                r2=None, r3=None, m=None, a=None, h=None, fmt=None,
                wrongs=None) -> object:
    """Where the curve meets the x-axis, from a factored or an expanded rule."""
    mode = mode or rng.choice(["factored", "standard", "not", "vertex"])
    name = name or rng.choice(NAMES)

    if mode == "factored":
        r1 = q(r1 if r1 is not None else rng.randint(-12, -1))
        r2 = q(r2 if r2 is not None else rng.randint(1, 12))
        if r1 == r2:
            raise ItemError("the two zeros must differ")
        rule = fn(name, "x", factored([(1, -r1, 1), (1, -r2, 1)]))
        why = (f"The product is zero when either factor is zero, so the graph crosses "
               f"the x-axis at x = {num(r1)} and x = {num(r2)}.")
        P = {"kind": "nlf_x_intercept", "mode": mode,
             "roots": [[r1.numerator, r1.denominator], [r2.numerator, r2.denominator]]}
        return value_item("nlfunc.x_intercept", "the zeros of a factored quadratic",
                          "medium", seed, X_SPR.format(rule=rule, n=name), r1, [],
                          rng, P, why, fmt="spr")

    if mode == "standard":
        r1 = q(r1 if r1 is not None else rng.randint(-30, -2))
        r2 = q(r2 if r2 is not None else rng.randint(2, 30))
        if r1 == r2 or r1 == -r2:
            raise ItemError("the two zeros must differ and must not be a mirror pair")
        b, c = -(r1 + r2), r1 * r2
        rule = fn(name, "x", poly_text([c, b, 1]))
        key = point(r1, 0)
        pool = {
            "other_negated": ("changed the sign of the other zero",
                              pair(point(-r2, 0), -r2, 0)),
            "constant": ("read the constant term as a zero", pair(point(c, 0), c, 0)),
            "flip": ("changed the sign of the zero", pair(point(-r1, 0), -r1, 0)),
            "middle": ("read the coefficient of x as a zero", pair(point(b, 0), b, 0)),
            "y_axis": ("gave the point where the graph meets the y-axis instead",
                       pair(point(0, c), 0, c)),
        }
        order = ["other_negated", "constant", "flip", "middle", "y_axis"]
        why = (f"{poly_text([c, b, 1])} factors as "
               f"{factored([(1, -r1, 1), (1, -r2, 1)])}, so the graph crosses the "
               f"x-axis at {point(r1, 0)} and {point(r2, 0)}.")
        P = {"kind": "nlf_x_intercept", "mode": mode,
             "b": [b.numerator, b.denominator], "c": [c.numerator, c.denominator]}
        return text_item("nlfunc.x_intercept", "an x-intercept of a quadratic",
                         "medium", seed, X_MCQ.format(rule=rule, n=name), key,
                         sig(r1, 0), pick(pool, order, wrongs), rng, P, why)

    if mode == "not":
        r1 = q(r1 if r1 is not None else rng.randint(-8, -2))
        r2 = q(r2 if r2 is not None else rng.randint(1, 8))
        m = q(m if m is not None else rng.randint(2, 5))
        r3 = q(r3 if r3 is not None else rng.randint(1, 9))
        third = r3 / m
        if len({r1, r2, third}) < 3 or third.denominator == 1:
            raise ItemError("the three zeros must differ and the third must be a fraction")
        trap = -m / r3
        if trap in (r1, r2, third):
            raise ItemError("the trap must not itself be a zero")
        rule = fn(name, "x", factored([(1, -r1, 1), (1, -r2, 1), (m, -r3, 1)]))
        key = point(trap, 0)
        pool = {
            "first": (f"({num(r1)}, 0) is an x-intercept: the first factor is zero there",
                      pair(point(r1, 0), r1, 0)),
            "second": (f"({num(r2)}, 0) is an x-intercept: the second factor is zero "
                       f"there", pair(point(r2, 0), r2, 0)),
            "third": (f"({num(third)}, 0) is an x-intercept: the third factor is zero "
                      f"there", pair(point(third, 0), third, 0)),
        }
        order = ["first", "second", "third"]
        why = (f"The zeros are {num(r1)}, {num(r2)} and {num(third)}; "
               f"{num(trap)} is the third factor's coefficients read the wrong way "
               f"round, so {key} is not an x-intercept.")
        P = {"kind": "nlf_x_intercept", "mode": mode,
             "r1": [r1.numerator, r1.denominator], "r2": [r2.numerator, r2.denominator],
             "m": [m.numerator, m.denominator], "r3": [r3.numerator, r3.denominator]}
        return text_item("nlfunc.x_intercept", "which point is not a zero", "medium",
                         seed, X_NOT.format(rule=rule, n=name), key, sig(trap, 0),
                         pick(pool, order, wrongs), rng, P, why)

    a = q(a if a is not None else rng.randint(2, 6))
    h = q(h if h is not None else rng.randint(2, 12))
    k = -a * h ** 2
    rule = fn(name, "x", f"{num(a)}(x {MINUS} {num(h)})² {MINUS} {num(-k)}")
    key = 2 * h
    pool = {
        "vertex": ("gave the vertex's x-coordinate", h),
        "coef": ("gave the coefficient outside the square", a),
        "half": ("halved the distance from the vertex to the origin", h / 2 + h),
        "shift": ("added the coefficient to the vertex instead of doubling it", h + a),
    }
    order = ["vertex", "coef", "half", "shift"]
    why = (f"{num(a)}(x {MINUS} {num(h)})² = {num(-k)} gives x {MINUS} {num(h)} = "
           f"±{num(h)}, so the zeros are 0 and {num(key)}.")
    P = {"kind": "nlf_x_intercept", "mode": "vertex", "a": [a.numerator, a.denominator],
         "h": [h.numerator, h.denominator]}
    return value_item("nlfunc.x_intercept", "the second zero of a vertex form",
                      "hard", seed, X_VERTEX.format(rule=rule, n=name), key,
                      pick(pool, order, wrongs), rng, P, why, fmt=fmt or "mcq",
                      signed=False)
