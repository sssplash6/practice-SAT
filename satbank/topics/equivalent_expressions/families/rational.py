"""Rational expressions: added, cancelled, and divided out.

Three questions the source asks about a quotient of polynomials -- combine two
of them over one denominator, cancel what the numerator and the denominator
share, and divide until what is left is smaller than the divisor. The wrong
answers are the ones a student who cancels too much, or too little, or who
subtracts only the first term of the numerator, actually writes down.
"""

from __future__ import annotations

import random

import math

from ....exact import E
from ....item import Item, ItemError, Mis, assemble, gridin_mistakes
from ..render import MINUS, Q, join, mono, num, pc, poly, sent
from .kit import FRAME_NAMES, Slip, frame_stem, text_item

__all__ = ["rational_combine", "rational_simplify", "divide_remainder"]

VARS = ["x", "n", "t", "w", "z", "j"]
CONSTS = ["r", "t", "a", "b", "k", "p"]


def _lin(m, b, var: str) -> str:
    return join([mono(m, [(var, 1)]), mono(b, [])])


# ---------------------------------------------------------- RATIONAL_COMBINE

def rational_combine(rng: random.Random, seed: int, *, shape=None, var=None,
                     frame=None, a=None, b=None, c=None, p=None, q=None, m=None,
                     n1=None, n2=None) -> Item:
    """Two fractions put over one denominator."""
    shape = shape or rng.choice(["identity", "difference"])
    var = var or rng.choice(VARS)

    if shape == "identity":
        a = Q(rng.choice([2, 3, 4, 5, 6, 7]) if a is None else a)
        b = Q(rng.choice([2, 3, 4, 5, 6, 7, 8]) if b is None else b)
        p = Q(rng.choice([i for i in range(-9, 10) if i]) if p is None else p)
        q = Q(rng.choice([i for i in range(-9, 10) if i]) if q is None else q)
        if p == q or a == b:
            raise ItemError("the two fractions must be genuinely different")
        r, t = a + b, a * q + b * p
        if r <= 0 or t <= 0:
            raise ItemError("the stem promises two positive constants")
        # the two constants are named in the stem, so neither may be the
        # variable: "where t and p are positive constants" about 5/(t − 3) is
        # not a question
        n1 = n1 or rng.choice([l for l in CONSTS if l != var])
        n2 = n2 or rng.choice([l for l in CONSTS if l not in (n1, var)])
        dens = f"({_lin(1, p, var)})({_lin(1, q, var)})"
        lhs = f"{num(a)}/({_lin(1, p, var)}) + {num(b)}/({_lin(1, q, var)})"
        stem = sent(f"{lhs} = ({n1}{var} + {n2})/({dens})\nThe equation above is true "
                    f"for all {var} > {num(max(-p, -q))}, where {n1} and {n2} are "
                    f"positive constants. What is the value of {n1}{n2} ?")
        key = r * t
        mistakes = [
            Mis(f"gave {n2} the sign of the constant in the first denominator",
                E(-r * t)),
            Mis("multiplied the second numerator by the constant in its own "
                "denominator instead of the other one", E(b * q)),
            Mis("multiplied the two numerators together and the two constants in "
                "the denominators together, ignoring their signs",
                E(abs(a * b * p * q))),
            Mis(f"added {n1} and {n2} rather than multiplying them", E(r + t)),
        ]
        why = (f"Over the common denominator the numerator is "
               f"{num(a)}({_lin(1, q, var)}) + {num(b)}({_lin(1, p, var)}), which "
               f"is {_lin(r, t, var)}.")
        params = {"kind": "eqx_rational_combine", "shape": "identity", "expr": lhs,
                  "denominator": dens, "var": var, "vars": [var], "ask": "product"}
        ex = E(key)
        ch, tex, reasons, ltr = assemble(ex, [mm for mm in mistakes if mm.value is not None],
                                         rng, signed=True, fillers="shift")
        return Item("eqx.rational_combine", "rational expressions", "hard", seed,
                    stem, "mcq", ex, ltr, why, ch, reasons, tex, params=params)

    # difference: the variable terms cancel and a bare number is left on top
    m = Q(rng.choice([2, 3, 4, 5, 6]) if m is None else m)
    c = Q(rng.choice([1, 2, 3]) if c is None else c)
    a = c * m
    p = Q(rng.choice([i for i in range(-9, 10) if i]) if p is None else p)
    q = Q(rng.choice([i for i in range(-9, 10) if i]) if q is None else q)
    top = a * q - c * p
    if top == 0 or m * q == p:
        raise ItemError("the two denominators would share a factor")
    if math.gcd(math.gcd(int(a), int(m)), int(abs(p))) != 1:
        raise ItemError("the first fraction would not be in lowest terms")
    frame = frame or rng.choice(["which", "which_of_short", "which_expressions"])
    d1, d2 = _lin(m, p, var), _lin(1, q, var)
    expr = f"{num(a)}/({d1}) {MINUS} {num(c)}/({d2})"
    key = f"{num(top)}/(({d2})({d1}))"
    chosen = [
        Slip("did not change the sign of the second numerator's constant when "
             "subtracting", f"{num(a * q + c * p)}/(({d2})({d1}))"),
        Slip("did not change the sign of the constant and then dropped the minus "
             "sign from the answer", f"{num(-(a * q + c * p))}/(({d2})({d1}))"),
        Slip("subtracted the numerators and the denominators term by term instead "
             "of using a common denominator",
             f"{num(a - c)}/({_lin(m - 1, p - q, var)})"),
        Slip("multiplied the two denominators but left the numerators alone",
             f"{num(a - c)}/(({d2})({d1}))"),
    ]
    why = (f"Over the common denominator the numerator is "
           f"{num(a)}({d2}) {MINUS} {num(c)}({d1}), and the {var}-terms cancel.")
    stem = frame_stem(frame, expr)
    params = {"kind": "eqx_rational_combine", "shape": "equiv", "expr": expr,
              "vars": [var]}
    return text_item("eqx.rational_combine", "rational expressions", "hard", seed,
                     stem, why, key, (lambda t: t), chosen, rng, params)


# --------------------------------------------------------- RATIONAL_SIMPLIFY

def rational_simplify(rng: random.Random, seed: int, *, var=None, k=None, j=None,
                      fname=None, gname=None) -> Item:
    """A quotient of two polynomials with a bracket in common."""
    var = var or rng.choice(["x", "t", "w", "z", "n", "p"])
    k = int(rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]) if k is None else k)
    j = int(rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) if j is None else j)
    fname = fname or "f"
    gname = gname or "g"
    if j == k or j == -k:
        raise ItemError("the second bracket must not cancel as well")
    f = poly(pc([0, -k * k, 0, 1]), var)                       # v³ − k²v
    g = poly(pc([-k * j, j - k, 1]), var)                      # (v − k)(v + j)
    expr = f"({f})/({g})"
    key = f"{var}({_lin(1, k, var)})/({_lin(1, j, var)})"
    chosen = [
        Slip("cancelled the wrong bracket and kept the one the denominator shares",
             f"{var}({_lin(1, -k, var)})/({_lin(1, j, var)})"),
        Slip(f"cancelled the {var} in front as well as the shared bracket",
             f"({_lin(1, k, var)})/({_lin(1, j, var)})"),
        Slip("cancelled everything in the numerator against the denominator",
             f"1/({_lin(1, j, var)})"),
        Slip("cancelled the bracket the two do not share",
             f"{var}({_lin(1, k, var)})/({_lin(1, -k, var)})"),
    ]
    why = (f"{f} is {var}({_lin(1, -k, var)})({_lin(1, k, var)}) and {g} is "
           f"({_lin(1, -k, var)})({_lin(1, j, var)}), so only "
           f"{_lin(1, -k, var)} cancels.")
    stem = sent(f"{fname}({var}) = {f}\n{gname}({var}) = {g}\nWhich of the following "
                f"expressions is equivalent to {fname}({var})/{gname}({var}), for "
                f"{var} > {k} ?")
    params = {"kind": "eqx_rational_simplify", "expr": expr, "vars": [var]}
    return text_item("eqx.rational_simplify", "rational expressions", "hard", seed,
                     stem, why, key, (lambda t: t), chosen, rng, params)


# ---------------------------------------------------------- DIVIDE_REMAINDER

def divide_remainder(rng: random.Random, seed: int, *, ask=None, var=None, frame=None,
                     b=None, c=None, r=None, s=None, n1=None, n2=None,
                     fmt=None) -> Item:
    """One polynomial divided by another, until what is left is smaller."""
    ask = ask or rng.choice(["expression", "expression", "coef_sum"])
    var = var or rng.choice(VARS)

    if ask == "expression":
        b = Q(rng.choice([i for i in range(-9, 10) if i]) if b is None else b)
        c = Q(rng.choice([i for i in range(-12, 13) if i]) if c is None else c)
        r = Q(rng.choice([i for i in range(-9, 10) if abs(i) >= 2]) if r is None else r)
        q0 = b + r
        rem = c + r * q0
        if rem == 0 or q0 == 0 or q0 == b - r:
            raise ItemError("the division comes out exactly, or the routes coincide")
        den = _lin(1, -r, var)
        expr = f"({poly(pc([c, b, 1]), var)})/({den})"

        def show(t):
            quo, rm = t
            sign = "+" if rm > 0 else MINUS
            return f"{_lin(1, quo, var)} {sign} {num(abs(rm))}/({den})"

        key = (q0, rem)
        first = [c + r * (b - r), c + (b - r), c - r]
        if all((v > 0) != (rem > 0) for v in first):
            raise ItemError("every wrong option would carry the opposite sign")
        chosen = [
            Slip("used the divisor's constant with the wrong sign when finding the "
                 "quotient", (b - r, c + r * (b - r))),
            Slip("used the divisor's constant with the wrong sign, and then added "
                 "the quotient's constant to the remainder instead of multiplying "
                 "it by the divisor's root", (b - r, c + (b - r))),
            Slip("subtracted the divisor's constant from the remainder instead of "
                 "multiplying by it", (q0, c - r)),
            Slip("left the divisor's constant out of the remainder altogether",
                 (q0, c)),
        ]
        rem_sign = "+" if rem > 0 else MINUS
        why = (f"{poly(pc([c, b, 1]), var)} is ({den})({_lin(1, q0, var)}) "
               f"{rem_sign} {num(abs(rem))}, and only {num(rem)} is left over.")
        frame = frame or rng.choice(["which_of_expressions", "which_expressions",
                                     "which_of", "which"])
        stem = frame_stem(frame, expr)
        params = {"kind": "eqx_divide_remainder", "shape": "equiv", "expr": expr,
                  "vars": [var]}
        return text_item("eqx.divide_remainder", "rational expressions", "hard",
                         seed, stem, why, key, show, chosen, rng, params)

    # coef_sum: the division is exact and a combination of the quotient is asked
    r = Q(rng.choice([2, 3, 4, 5, 6, 7, 8, 9]) if r is None else r)
    s = Q(rng.choice([i for i in range(-9, 10) if abs(i) >= 1]) if s is None else s)
    if s == r or s == 0:
        raise ItemError("the two brackets must differ")
    n1 = n1 or rng.choice([l for l in ("a", "p", "j") if l != var])
    n2 = n2 or rng.choice([l for l in ("d", "b", "k") if l not in (n1, var)])
    top = poly(pc([r * s, r + s, 1]), var)
    den = _lin(1, r, var)
    stem = sent(f"The equation ({top})/({den}) = {n1}{var} + {n2} is true for all "
                f"{var} ≠ {num(-r)}, where {n1} and {n2} are integers. What is the "
                f"value of {n1} + {n2} ?")
    key = 1 + s
    ex = E(key)
    why = (f"{top} is ({den})({_lin(1, s, var)}), so dividing by {den} leaves "
           f"{_lin(1, s, var)}: {n1} = 1 and {n2} = {num(s)}, so "
           f"{n1} + {n2} = {num(key)}.")
    mistakes = [
        Mis(f"reported {n2} on its own", E(s)),
        Mis(f"reported {n1} on its own", E(1)),
        Mis(f"took {n2} from the divisor rather than from the quotient", E(1 - r)),
        Mis(f"added the divisor's constant instead of the quotient's", E(1 + r)),
        Mis(f"multiplied {n1} and {n2} instead of adding them", E(s)),
    ]
    params = {"kind": "eqx_divide_remainder", "shape": "coef_sum",
              "expr": f"({top})/({den})", "var": var, "vars": [var],
              "degree": 1, "weights": [[1, 1], [0, 1]]}
    fmt = fmt or ("spr" if rng.random() < 0.2 else "mcq")
    if fmt == "spr":
        if key < 0:
            raise ItemError("a negative answer would not go into a grid-in")
        return Item("eqx.divide_remainder", "rational expressions", "hard", seed,
                    stem, "spr", ex, ex.gridin(), why, params=params,
                    # 1 - r fits taking the divisor's root, not its constant
                    spr_mistakes=gridin_mistakes(ex, mistakes[:2] + mistakes[3:]))
    ch, tex, reasons, ltr = assemble(ex, mistakes, rng, signed=True, fillers="shift")
    return Item("eqx.divide_remainder", "rational expressions", "hard", seed, stem,
                "mcq", ex, ltr, why, ch, reasons, tex, params=params)
