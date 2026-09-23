"""A constant hidden inside an identity, and the coefficients an expansion
leaves behind.

These are the items whose answer is a number rather than an expression: the
two sides are equivalent *for all x*, and the question is what the letter has
to be for that to be true, or what the coefficients of the expanded form add
up to.
"""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, ItemError, Mis, assemble, gridin_mistakes
from ..render import MINUS, Q, dec, join, mono, num, pc, poly, sent
from .kit import Slip

__all__ = ["match_constant", "coef_combination"]

VARS = ["x", "n", "p", "t", "w", "y", "z", "j"]
LETTERS = ["a", "b", "c", "k", "p", "r", "t"]


def _griddable(v: Q) -> bool:
    return v.denominator in (1, 2, 4, 5, 10, 20, 25, 50, 100)


# ------------------------------------------------------------ MATCH_CONSTANT

def match_constant(rng: random.Random, seed: int, *, shape=None, var=None, letter=None,
                   other=None, fmt=None, a=None, b=None, c=None, d=None, e=None,
                   k=None, m=None, scale=None) -> Item:
    """Two expressions agree for every x; what does the constant have to be?"""
    shape = shape or rng.choice(["factor_out", "factor_pair", "rational", "scale",
                                 "expand_sub", "cubic_pair"])
    var = var or rng.choice(VARS)
    letter = letter or rng.choice([l for l in LETTERS if l != var])
    # mistakes whose reason does not produce the value: a grid-in, which names
    # the reason for a typed value, leaves them out
    off = ()

    if shape == "factor_out":                        # c·v² + @v ≡ v(c·v + k)
        c = Q(rng.choice([2, 3, 4, 5, 6, 7]) if c is None else c)
        k = Q(rng.choice([3, 5, 7, 9, 11, 13, 15]) if k is None else k)
        if k == c or k - 2 * c in (Q(0), c, 2 * c, k):
            raise ItemError("two of the wrong routes would coincide")
        lhs = join([mono(c, [(var, 2)]), f"{letter}{var}"])
        rhs = f"{var}({join([mono(c, [(var, 1)]), mono(k, [])])})"
        stem = sent(f"The expression {lhs} is equivalent to {rhs} for some constant "
                    f"{letter}. What is the value of {letter} ?")
        key = k
        mistakes = [
            Mis(f"reported the coefficient of {mono(1, [(var, 2)])} instead", E(c)),
            Mis(f"doubled the coefficient of {mono(1, [(var, 2)])}", E(2 * c)),
            Mis(f"took twice the coefficient of {mono(1, [(var, 2)])} away from the "
                f"number inside the parentheses", E(k - 2 * c)),
            Mis("multiplied the two numbers in the factored form", E(c * k)),
        ]
        off = (1, 2)                 # 2c and k − 2c are labels, not routes to the letter
        why = (f"{rhs} multiplies out to "
               f"{join([mono(c, [(var, 2)]), mono(k, [(var, 1)])])}, so "
               f"{letter}{var} has to be {mono(k, [(var, 1)])}.")
        params = {"kind": "eqx_match_constant", "shape": "affine", "vars": [var],
                  "lhs": lhs, "rhs": rhs, "letter": letter}
    elif shape == "factor_pair":                     # a·v² + b·v + c ≡ (a·v − d)(v + @)
        a = Q(rng.choice([2, 3, 4, 5]) if a is None else a)
        d = Q(rng.choice([1, 2, 3, 4, 5, 6, 7]) if d is None else d)
        k = Q(rng.choice([2, 3, 4, 5, 6, 7, 8, 9]) if k is None else k)
        quad = pc([-d * k, a * k - d, a])
        lhs, rhs = poly(quad, var), (f"({join([mono(a, [(var, 1)]), mono(-d, [])])})"
                                     f"({var} + {letter})")
        stem = sent(f"{lhs}\nIf the given expression is rewritten in the form "
                    f"{rhs}, where {letter} is a constant, what is the value of "
                    f"{letter} ?")
        key = k
        mistakes = [
            Mis("reported the constant term of the expression instead", E(-d * k)),
            Mis("divided the constant term by the leading coefficient", E(-d * k / a)),
            Mis("reported the constant already inside the first bracket", E(d)),
            Mis("reported the coefficient of the middle term", E(a * k - d)),
        ]
        # that constant is −d; a zero middle coefficient prints no middle term to report
        off = (2,) if a * k != d else (2, 3)
        why = (f"The two brackets multiply to "
               f"{poly(pc([-d * k, a * k - d, a]), var)} only when {letter} makes "
               f"the constant term {num(-d * k)}.")
        params = {"kind": "eqx_match_constant", "shape": "affine", "vars": [var],
                  "lhs": lhs, "rhs": rhs, "letter": letter}
    elif shape == "rational":                        # a/(m·v + m·k) ≡ (a/m)/(v + @)
        m = Q(rng.choice([2, 3, 4, 5, 6, 7, 8]) if m is None else m)
        k = Q(rng.choice([2, 3, 5, 6, 7, 8, 9, 10, 11, 12]) if k is None else k)
        a = Q(m * rng.choice([2, 3, 4, 5, 6]) if a is None else a)
        if a % m != 0 or a / m == k:
            raise ItemError("the numerator must reduce to a whole number")
        lhs = f"{num(a)}/({join([mono(m, [(var, 1)]), mono(m * k, [])])})"
        rhs = f"{num(a / m)}/({var} + {letter})"
        stem = sent(f"The expression {lhs} is equivalent to {rhs}, where {letter} is "
                    f"a constant and {var} > 0. What is the value of {letter}?")
        key = k
        mistakes = [
            Mis("multiplied the two numbers in the denominator instead of dividing "
                "the constant by the coefficient", E(m * m * k)),
            Mis("reported the numerator instead of the constant", E(a)),
            Mis("added the coefficient of the variable to the new numerator instead "
                "of dividing", E(a / m + m)),
            Mis("divided the constant by the new numerator instead of by the "
                "coefficient", E(m * k / (a / m))),
        ]
        off = (2,)                   # the new numerator plays no part in finding the letter
        why = (f"Dividing the numerator and the denominator by {num(m)} turns "
               f"{lhs} into {num(a / m)} over {join([mono(1, [(var, 1)]), mono(k, [])])}.")
        params = {"kind": "eqx_match_constant", "shape": "affine", "vars": [var],
                  "lhs": lhs, "rhs": rhs, "letter": letter}
    elif shape == "scale":                           # s(A v² + B v + C), find s
        a = Q(rng.choice([2, 3, 4, 5, 6, 7, 8, 9]) if a is None else a)
        b = Q(rng.choice([3, 5, 7, 9, 11, 13]) if b is None else b)
        c = Q(rng.choice([6, 11, 13, 17, 19, 23]) if c is None else c)
        scale = Q(rng.choice([Q(9, 100), Q(3, 100), Q(1, 4), Q(1, 2), Q(6, 100),
                              Q(12, 100), Q(15, 100)]) if scale is None else Q(scale))
        lhs = poly(pc([scale * c, scale * b, scale * a]), var, decimal=True)
        rhs = f"{letter}({poly(pc([c, b, a]), var)})"
        stem = sent(f"{lhs}\nThe given expression can be rewritten as {rhs}, where "
                    f"{letter} is a constant. What is the value of {letter}?")
        key = scale
        mistakes = [
            Mis("matched only the leading coefficients and divided the wrong way",
                E(scale * a)),
            Mis("inverted the ratio", E(1 / scale) if scale else None),
            Mis("used the middle coefficients rather than matching every term",
                E(scale * b)),
        ]
        off = (0, 2)       # scale·a is the given coefficient; the middle ratio is the key
        why = (f"Every coefficient of {lhs} is the matching coefficient of "
               f"{poly(pc([c, b, a]), var)} multiplied by the same number.")
        params = {"kind": "eqx_match_constant", "shape": "affine", "vars": [var],
                  "lhs": lhs, "rhs": rhs, "letter": letter}
    elif shape == "expand_sub":                      # m(a v² + @v + c) − e·v(@ + d)
        m = Q(rng.choice([2, 3, 4, 5]) if m is None else m)
        a = Q(rng.choice([2, 3, 4, 5]) if a is None else a)
        c = Q(rng.choice([4, 6, 8, 9, 12]) if c is None else c)
        e = Q(rng.choice([8, 12, 16, 20, 24]) if e is None else e)
        d = Q(rng.choice([2, 3, 4, 5, 6]) if d is None else d)
        k = Q(rng.choice([3, 5, 7, 9, 11, 13]) if k is None else k)
        gathered = m * k - e * k - e * d               # the coefficient of v
        lhs = (f"{num(m)}({join([mono(a, [(var, 2)]), f'{letter}{var}', mono(c, [])])}) "
               f"{MINUS} {num(e)}{var}({letter} + {num(d)})")
        rhs = poly(pc([m * c, gathered, m * a]), var)
        stem = sent(f"In the expression {lhs}, {letter} is a constant. This "
                    f"expression is equivalent to the expression {rhs}. What is the "
                    f"value of {letter} ?")
        key = k
        mistakes = [
            Mis(f"reported the coefficient of {var} in the second expression",
                E(abs(gathered))),
            Mis(f"reported the number that multiplies {letter} after gathering",
                E(e - m)),
            Mis("used the constant term instead of the coefficient of the variable",
                E(m * c)),
            Mis(f"changed the sign of {letter}", E(-k)),
        ]
        # the coefficient and the multiplier are negative; matching the constant
        # terms holds no letter, so it yields no value
        off = (0, 1, 2)
        why = (f"Expanding gathers the {var}-terms into "
               f"({num(m)} {MINUS} {num(e)}){letter} {MINUS} {num(e * d)}, and that "
               f"has to equal {num(gathered)}.")
        params = {"kind": "eqx_match_constant", "shape": "affine", "vars": [var],
                  "lhs": lhs, "rhs": rhs, "letter": letter}
    else:                                            # cubic_pair
        other = other or rng.choice([l for l in LETTERS if l not in (var, letter)])
        a = Q(rng.choice([2, 3, 4, 5, 6]) if a is None else a)
        b = Q(rng.choice([2, 3, 4, 5, 6, 7, 8]) if b is None else b)
        c = Q(rng.choice([2, 3, 4, 5]) if c is None else c)
        d = Q(rng.choice([2, 3, 4, 5, 6]) if d is None else d)
        e = Q(rng.choice([2, 3, 4, 5, 6]) if e is None else e)
        cube = pc([c * e, a * e - c * b, c * d - a * b, a * d])
        lhs = (f"({join([f'{letter}{var}', mono(c, [])])})"
               f"({join([mono(d, [(var, 2)]), f'{MINUS}{other}{var}', mono(e, [])])})")
        rhs = poly(cube, var)
        stem = sent(f"{lhs} = {rhs}\nThe equation above is true for all {var}, where "
                    f"{letter} and {other} are constants. What is the value of "
                    f"{letter}{other} ?")
        key = a * b
        mistakes = [
            Mis(f"multiplied the constant in the first bracket by {other} instead "
                f"of {letter}", E(c * b)),
            Mis("reported the leading coefficient of the cubic", E(a * d)),
            Mis(f"reported {letter} + {other} rather than their product", E(a + b)),
            Mis(f"multiplied {letter} by the leading coefficient of the second "
                f"bracket", E(a * d * 2)),
        ]
        off = (3,)                                   # that product is a·d, not 2ad
        why = (f"The leading term forces {letter} = {num(a)}, and the "
               f"{mono(1, [(var, 2)])}-term then forces {other} = {num(b)}.")
        params = {"kind": "eqx_match_constant", "shape": "cubic_pair", "var": var,
                  "c": float(c), "d": float(d), "e": float(e), "rhs": rhs,
                  "ask": "product"}
        fmt = fmt or "mcq"

    fmt = fmt or ("spr" if rng.random() < 0.35 else "mcq")
    ex = E(key)
    if fmt == "spr":
        if not _griddable(Q(key)) or key < 0:
            raise ItemError("that constant would not go into a grid-in")
        return Item("eqx.match_constant", "equivalent expressions", "medium", seed,
                    stem, "spr", ex, ex.gridin(), why, params=params,
                    spr_mistakes=gridin_mistakes(
                        ex, [m for i, m in enumerate(mistakes) if i not in off]))
    good = [m for m in mistakes if m.value is not None]
    ch, tex, reasons, ltr = assemble(ex, good, rng, signed=True, fillers="shift")
    return Item("eqx.match_constant", "equivalent expressions", "hard", seed, stem,
                "mcq", ex, ltr, why, ch, reasons, tex, params=params)


# --------------------------------------------------------- COEF_COMBINATION

def coef_combination(rng: random.Random, seed: int, *, shape=None, var=None,
                     P=None, R=None, ask=None, a=None, a2=None, b=None, c=None,
                     d=None, e=None, f=None, g=None) -> Item:
    """Expand or collect, then report a combination of the coefficients."""
    shape = shape or rng.choice(["sum_two", "product_frac", "product_int",
                                 "sum_scaled"])
    var = var or rng.choice(VARS)
    letters = ("a", "b", "c")

    if shape == "sum_two":
        P = P or [rng.randint(-40, 40), rng.randint(-9, 9),
                  rng.choice([i for i in range(-5, 6) if i])]
        R = R or [rng.randint(-40, 40), rng.randint(-9, 9),
                  rng.choice([i for i in range(-5, 6) if i])]
        p, q = pc([Q(x) for x in P]), pc([Q(x) for x in R])
        if len(p) != 3 or len(q) != 3 or p[2] + q[2] == 0:
            raise ItemError("both polynomials must stay quadratic")
        expr = f"({poly(p, var)}) + ({poly(q, var)})"
        key = sum(p[i] + q[i] for i in range(3))
        stem = sent(f"The sum of {poly(p, var)} and {poly(q, var)} can be written in "
                    f"the form a{var}² + b{var} + c, where a, b, and c are "
                    f"constants. What is the value of a + b + c ?")
        weights = [[2, 1], [1, 1], [0, 1]]
        degree = 2
        why = (f"Adding like terms gives {poly(pc([p[i] + q[i] for i in range(3)]), var)}, "
               f"and a, b and c are its three coefficients.")
    elif shape in ("product_frac", "product_int"):
        if shape == "product_frac":
            a = Q(a if a is not None else Q(rng.randint(1, 5), rng.choice([2, 3, 4])))
            b = Q(b if b is not None else Q(rng.randint(1, 7), rng.choice([2, 3, 4])))
            c = Q(c if c is not None else Q(rng.randint(1, 5), rng.choice([2, 3, 4])))
            d = Q(d if d is not None else Q(rng.randint(1, 7), rng.choice([2, 3, 4])))
        else:
            a = Q(rng.choice([2, 3, 4, 5, 7]) if a is None else a)
            b = Q(rng.choice([i for i in range(-30, 31) if abs(i) > 10])
                  if b is None else b)
            c = Q(rng.choice([11, 13, 17, 19, 23]) if c is None else c)
            d = Q(rng.choice([i for i in range(-9, 10) if i]) if d is None else d)
        left = join([mono(a, [(var, 1)]), mono(b, [])])
        right = join([mono(c, [(var, 1)]), mono(d, [])])
        expr = f"({left})({right})"
        key = a * d + b * c
        if shape == "product_frac":
            stem = sent(f"{expr}\nThe expression above is equivalent to "
                        f"a{var}² + b{var} + c, where a, b, and c are constants. "
                        f"What is the value of b?")
        else:
            stem = sent(f"The expression {expr} is equivalent to the expression "
                        f"a{var}² + b{var} + c, where a, b, and c are constants. "
                        f"What is the value of b?")
        weights = [[1, 1]]
        degree = 2
        why = (f"The middle coefficient is the sum of the two cross products, "
               f"{num(a)} × {num(d)} and {num(b)} × {num(c)}.")
    else:                                            # sum_scaled
        a = Q(rng.choice([100, 50, 20, 25, 200]) if a is None else a)
        b = Q(rng.randint(1000, 9000) if b is None else b)
        c = Q(rng.choice([2, 5, 10, 4]) if c is None else c)
        d = Q(rng.choice([10, 20, 50, 100, 110, 120]) if d is None else d)
        a2 = Q(rng.choice([2, 5, 10, 20, 25]) if a2 is None else a2)
        expr = (f"({join([mono(b, []), mono(a, [(var, 2)])])}) + "
                f"{num(c)}({join([mono(a2, [(var, 2)]), mono(-d, [])])})")
        key = (a + c * a2) + (b - c * d)
        stem = sent(f"{expr}\nThe expression above can be written in the form "
                    f"a{var}² + b, where a and b are constants. What is the value "
                    f"of a + b ?")
        weights = [[2, 1], [0, 1]]
        degree = 2
        why = (f"The two {mono(1, [(var, 2)])}-terms collect into "
               f"{mono(a + c * a2, [(var, 2)])} and the constants into "
               f"{num(b - c * d)}.")

    ex = E(key)
    if not _griddable(Q(key)):
        raise ItemError("that value would not go into a grid-in")
    params = {"kind": "eqx_coef_combination", "expr": expr, "var": var,
              "degree": degree, "weights": weights, "vars": [var]}
    return Item("eqx.coef_combination", "equivalent expressions",
                "medium" if shape != "product_int" else "hard", seed, stem, "spr",
                ex, ex.gridin(), why, params=params)
