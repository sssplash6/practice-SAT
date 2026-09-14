"""The eight shapes a linear equation takes on the page.

Every source item in this topic is one of these, differing only in where the
unknown sits, whether a bracket has to be expanded first, and whether the
numbers are integers, fractions or decimals. A shape knows two things: how it
prints, and what `A*v = C` it collapses to. Templates ask for both; `audit.py`
recovers the same collapse by evaluating each side numerically instead.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q
from math import gcd

from ....expr import sign_join
from ....item import ItemError
from .kit import eq_of, num, over, paren, side, term

__all__ = ["SHAPES", "render", "collapse", "draw_shape", "nice"]

SHAPES = ["standard", "over", "split", "sum_left", "paren_right",
          "two_paren", "paren_sum", "paren_both"]

# which keys each shape reads, and which of them may not be zero
REQUIRED = {
    "standard": ("a", "b", "c", "d"),
    "over": ("a", "den", "d"),
    "split": ("f1", "f2", "d"),
    "sum_left": ("a", "b", "c", "d"),
    "paren_right": ("a", "b", "c", "d", "e"),
    "two_paren": ("a", "b", "c", "d", "e"),
    "paren_sum": ("a", "b", "c", "d", "e", "f"),
    "paren_both": ("a", "b", "c", "d", "e", "f", "g"),
}
NONZERO = {
    "standard": ("a",),
    "over": ("a", "den"),
    "split": ("f1", "f2"),
    "sum_left": ("a", "b", "c"),
    "paren_right": ("a", "c", "d"),
    "two_paren": ("a", "b", "c", "d", "e"),
    "paren_sum": ("a", "b", "d", "f"),
    "paren_both": ("a", "b", "e"),
}


def _get(p: dict):
    return lambda k, d=0: Q(p.get(k, d))


def collapse(shape: str, p: dict) -> tuple[Q, Q]:
    """(A, C) with A*v = C -- the equation with everything gathered."""
    g = _get(p)
    if shape == "standard":
        return g("a") - g("c"), g("d") - g("b")
    if shape == "over":
        if g("a") == g("den", 1):
            raise ItemError("a fraction that cancels is not worth printing")
        return g("a") / g("den", 1), g("d")
    if shape == "split":
        return g("f1") - g("f2"), g("d")
    if shape == "sum_left":
        return g("a") + g("b"), g("d") - g("b") * g("c")
    if shape == "paren_right":
        return g("a") - g("c"), g("c") * g("d") + g("e") - g("b")
    if shape == "two_paren":
        return g("a") + g("c") - g("e"), -(g("a") * g("b") + g("c") * g("d"))
    if shape == "paren_sum":
        return g("a") * g("b") + g("d") - g("f"), g("e") - g("a") * g("c")
    if shape == "paren_both":
        return (g("a") * g("b") - g("e"),
                g("e") * g("f") + g("g") - g("d") - g("a") * g("c"))
    raise KeyError(shape)


def render(shape: str, p: dict, v: str, decimal: bool = False) -> str:
    """The equation as the source prints it."""
    g, D = _get(p), decimal
    if shape == "standard":
        return eq_of(side(g("a"), g("b"), v, p.get("cf_l", False), D),
                     side(g("c"), g("d"), v, p.get("cf_r", False), D))
    if shape == "over":
        return eq_of(over(g("a"), g("den", 1), v), num(g("d"), D))
    if shape == "split":
        return eq_of(sign_join([term(g("f1"), v), term(-g("f2"), v)]), num(g("d"), D))
    if shape == "sum_left":
        return eq_of(sign_join([term(g("a"), v, D),
                                paren(g("b"), side(1, g("c"), v, decimal=D), D)]),
                     num(g("d"), D))
    if shape == "paren_right":
        return eq_of(side(g("a"), g("b"), v, decimal=D),
                     sign_join([paren(g("c"), side(1, g("d"), v, decimal=D), D)]
                               + ([num(g("e"), D)] if g("e") else [])))
    if shape == "two_paren":
        return eq_of(sign_join([paren(g("a"), side(1, g("b"), v, decimal=D), D),
                                paren(g("c"), side(1, g("d"), v, decimal=D), D)]),
                     term(g("e"), v, D))
    if shape == "paren_sum":
        return eq_of(sign_join([paren(g("a"), side(g("b"), g("c"), v, decimal=D), D),
                                term(g("d"), v, D)]),
                     side(g("f"), g("e"), v, const_first=True, decimal=D))
    if shape == "paren_both":
        return eq_of(sign_join([paren(g("a"), side(g("b"), g("c"), v, decimal=D), D)]
                               + ([num(g("d"), D)] if g("d") else [])),
                     sign_join([paren(g("e"), side(1, g("f"), v, decimal=D), D)]
                               + ([num(g("g"), D)] if g("g") else [])))
    raise KeyError(shape)


def nice(shape: str, p: dict) -> None:
    """Refuse a draw that would not print as the shape intends."""
    g = _get(p)
    for k in NONZERO[shape]:
        if g(k) == 0:
            raise ItemError(f"a zero {k} collapses the {shape} shape")
    if collapse(shape, p)[0] == 0:
        raise ItemError("the unknown cancels; this template solves for it")
    if shape == "standard" and g("a") == g("c"):
        raise ItemError("identical x-terms on both sides")


def params_of(shape: str, p: dict) -> dict:
    """The coefficients the audit needs, as plain floats."""
    g = _get(p)
    out = {k: float(g(k, 1 if k == "den" else 0)) for k in REQUIRED[shape]}
    out["cf_l"] = bool(p.get("cf_l", False))
    out["cf_r"] = bool(p.get("cf_r", False))
    return out


# --------------------------------------------------------------- sampling

def _nz(rng: random.Random, lo: int, hi: int) -> int:
    for _ in range(40):
        v = rng.randint(lo, hi)
        if v:
            return v
    raise ItemError("no usable coefficient in range")


def draw_shape(rng: random.Random, shape: str) -> dict:
    """Coefficients in the magnitudes the source items actually use."""
    if shape == "standard":
        p = {"a": _nz(rng, -20, 24), "b": rng.randint(-40, 60),
             "c": rng.choice([0, 0, 0, _nz(rng, -20, 24)]), "d": rng.randint(-40, 120),
             "cf_l": rng.random() < 0.15, "cf_r": rng.random() < 0.2}
        if p["a"] == p["c"]:
            p["c"] = 0
        return p
    if shape == "over":
        a = _nz(rng, 1, 9)
        den = rng.choice([d for d in range(2, 13) if d != a and gcd(d, a) == 1])
        return {"a": a, "den": den, "d": _nz(rng, -30, 60)}
    if shape == "split":
        d1, d2 = rng.sample([2, 3, 4, 5, 6, 8, 10, 12], 2)
        return {"f1": Q(1, d1), "f2": Q(1, d2), "d": _nz(rng, -12, 20)}
    if shape == "sum_left":
        return {"a": _nz(rng, -9, 12), "b": _nz(rng, 2, 9),
                "c": _nz(rng, -12, 12), "d": rng.randint(-30, 90)}
    if shape == "paren_right":
        return {"a": _nz(rng, -6, 8), "b": _nz(rng, -30, 30), "c": _nz(rng, 2, 9),
                "d": _nz(rng, -12, 12), "e": rng.choice([0, 0, rng.randint(-20, 20)])}
    if shape == "two_paren":
        return {"a": _nz(rng, 2, 9), "b": _nz(rng, -9, 9), "c": _nz(rng, -9, 9),
                "d": _nz(rng, -9, 9), "e": _nz(rng, -9, 9)}
    if shape == "paren_sum":
        return {"a": _nz(rng, 2, 7), "b": _nz(rng, 2, 6), "c": _nz(rng, -14, 14),
                "d": _nz(rng, -6, 6), "e": rng.randint(-30, 60), "f": _nz(rng, -8, 8)}
    if shape == "paren_both":
        return {"a": _nz(rng, 2, 6), "b": _nz(rng, 2, 5), "c": _nz(rng, -12, 12),
                "d": rng.randint(-20, 20), "e": _nz(rng, 2, 8), "f": _nz(rng, -10, 10),
                "g": rng.randint(-20, 20)}
    raise KeyError(shape)
