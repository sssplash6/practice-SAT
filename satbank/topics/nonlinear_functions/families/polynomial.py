"""Polynomials beyond the parabola: what a table of values forces, and what the
zeros say about the constant term.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import ItemError, Mis
from ..common import MINUS, num, pair, pick, q, sig, text_item, value_item

__all__ = ["factor_from_table", "zeros_constant"]

FACTOR = ("The table above gives selected values of a polynomial function {n}. Based "
          "on the values in the table, which of the following must be a factor of "
          "{n}?")
ZEROS = ("{rule} The function {n} is defined above, where a, b, and c are integer "
         "constants. If the zeros of the function are {z1}, {z2}, and {z3}, what is "
         "the value of c?")


def factor_from_table(rng: random.Random, seed: int, *, z1=None, z2=None, lo=None,
                      vals=None, name=None, wrongs=None) -> object:
    """Two rows of the table are zeros; only their factors must divide p."""
    name = name or rng.choice(["p", "f", "g", "h"])
    lo = int(lo if lo is not None else rng.randint(-4, -1))
    xs = [lo + i for i in range(5)]
    z1 = int(z1 if z1 is not None else rng.choice(xs[:3]))
    z2 = int(z2 if z2 is not None else rng.choice(xs[2:]))
    if z1 == z2 or z1 == -z2:
        # a mirror pair would make the sign-flipped option the same polynomial
        # as the key, which is a second correct answer, not a distractor
        raise ItemError("the two zeros must differ and must not be a mirror pair")
    if vals is None:
        vals = {}
        for x in xs:
            if x in (z1, z2):
                continue
            vals[x] = rng.choice([v for v in range(-9, 10) if v != 0])
    else:
        vals = {int(k): int(v) for k, v in vals.items()}
    marker = vals.get(0, next(iter(vals.values())))
    if abs(marker) in (abs(z1), abs(z2)):
        raise ItemError("the printed output must not look like one of the zeros")
    table = [["x", f"{name}(x)"]]
    for x in xs:
        table.append([num(x), "0" if x in (z1, z2) else num(vals[x])])

    def factor(r) -> str:
        return f"(x {MINUS} {num(r)})" if r > 0 else f"(x + {num(-r)})"

    key = factor(z1) + factor(z2)
    pool = {
        "single_minus": ("read an output in the table as a zero",
                         pair(factor(abs(marker)), abs(marker), 0)),
        "single_plus": ("read an output in the table as a zero and changed its sign",
                        pair(factor(-abs(marker)), -abs(marker), 0)),
        "flipped": ("used the zeros with the signs of their factors the wrong way "
                    "round", pair(factor(-z1) + factor(-z2), -z1, -z2)),
        "repeated": ("assumed the table's first zero is a repeated one, which the "
                     "values do not show", pair(factor(z1) + factor(z1), z1, z1)),
    }
    order = ["single_minus", "single_plus", "flipped", "repeated"]
    why = (f"{name}({num(z1)}) = 0 and {name}({num(z2)}) = 0, so {factor(z1)} and "
           f"{factor(z2)} both divide {name}.")
    P = {"kind": "nlf_factor_table", "z1": z1, "z2": z2,
         "vals": {str(k): v for k, v in vals.items()}, "lo": lo}
    return text_item("nlfunc.factor_from_table", "a factor forced by a table", "hard",
                     seed, FACTOR.format(n=name), key, sig(z1, z2),
                     pick(pool, order, wrongs), rng, P, why, table=table)


def zeros_constant(rng: random.Random, seed: int, *, r1=None, r2=None, r3=None,
                   name=None, deg=None) -> object:
    """x³ + ax² + bx + c with three named zeros: what is c?"""
    name = name or rng.choice(["h", "f", "g", "p"])
    r1 = int(r1 if r1 is not None else rng.randint(-9, -1))
    r2 = int(r2 if r2 is not None else rng.randint(1, 9))
    r3 = int(r3 if r3 is not None else rng.randint(1, 9))
    if len({r1, r2, r3}) < 3 or 0 in (r1, r2, r3):
        raise ItemError("the three zeros must differ and none may be zero")
    key = q(-r1 * r2 * r3)
    rule = f"{name}(x) = x³ + ax² + bx + c"
    why = (f"{name}(x) = (x {MINUS} {num(r1)})(x {MINUS} {num(r2)})(x {MINUS} "
           f"{num(r3)}), and the constant term is the product of the three zeros with "
           f"its sign changed: {num(key)}.")
    P = {"kind": "nlf_zeros_constant", "roots": [r1, r2, r3]}
    return value_item("nlfunc.zeros_constant", "the constant term from three zeros",
                      "hard", seed, ZEROS.format(rule=rule, n=name, z1=num(r1),
                                                 z2=num(r2), z3=num(r3)),
                      key, [], rng, P, why, fmt="spr")
