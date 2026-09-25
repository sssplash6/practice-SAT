"""Exponents and radicals: the rules that say what may be added, what must be
multiplied, and what a fractional exponent means.

The wrong answers here are almost all one rule applied in place of another --
exponents added where they should have been multiplied, divided where they
should have been subtracted, a root's index used as a coefficient, a
denominator of an exponent written as a factor.
"""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, ItemError, Mis, gridin_mistakes
from ..render import (MINUS, Q, join, mono, num, power, pow_of, root, sent, sup)
from .kit import FRAME_NAMES, Slip, frame_stem, text_item

__all__ = ["monomial_power", "radical_form", "exponent_value", "telescope"]

VARS = ["x", "n", "p", "t", "w", "y", "z", "j"]
TRIPLES = [("x", "y", "z"), ("a", "b", "c"), ("p", "q", "r"), ("u", "v", "w")]


def _rad_pow(var: str, e) -> str:
    """A positive rational power written the way the source writes it:
    x^(7/3) as x²·³√x, x^(2/3) as ³√(x²), y^(3/2) as y√y."""
    e = Q(e)
    whole, frac = divmod(e.numerator, e.denominator)
    parts = []
    if whole:
        parts.append(power(var, whole))
    if frac:
        inner = var if frac == 1 else f"({power(var, frac)})"
        parts.append(root(e.denominator, inner))
    if not parts:
        return "1", False
    # a superscript sitting against a root index needs separating, but a plain
    # square root does not: y√y is unambiguous, x²³√x is not
    glue = "·" if (whole and frac and (whole > 1 or e.denominator > 2)) else ""
    return glue.join(parts), bool(whole and frac)


# ----------------------------------------------------------- MONOMIAL_POWER

def monomial_power(rng: random.Random, seed: int, *, shape=None, frame=None,
                   names=None, cond=None, a=None, b=None, c=None, m=None, n=None,
                   k=None, p=None, q=None, r=None, s=None, t=None, u=None,
                   v=None) -> Item:
    """Monomials multiplied, divided, and rooted -- exponents only."""
    shape = shape or rng.choice(["product", "distribute_powers", "root_quotient"])
    X, Y, Z = names or rng.choice(TRIPLES)
    frame = frame or rng.choice(FRAME_NAMES)

    if shape == "product":                           # (a·YZ)(Y)(b·Z)
        a = int(rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 11, 12]) if a is None else a)
        b = int(rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 11, 13]) if b is None else b)
        if a == b:
            raise ItemError("two equal coefficients make the slips coincide")
        expr = f"({mono(a, [(Y, 1), (Z, 1)])})({Y})({mono(b, [(Z, 1)])})"
        show = (lambda t: mono(t[0], [(Y, t[1]), (Z, t[2])]))
        key = (a * b, 2, 2)
        chosen = [
            Slip(f"added the exponents of {Y} but left {Z} alone", (a * b, 2, 1)),
            Slip("multiplied the coefficients but added none of the exponents",
                 (a * b, 1, 1)),
            Slip("added the three coefficients instead of multiplying them",
                 (a + b + 1, 1, 1)),
            Slip("added every exponent into one variable", (a * b, 4, 0)),
        ]
        why = (f"The coefficients multiply and the exponents of {Y} and of {Z} each "
               f"add, giving {mono(a * b, [(Y, 2), (Z, 2)])}.")
        vs = sorted([Y, Z])
    elif shape == "distribute_powers":               # (Xᵖ Yᵠ Zʳ)(Xˢ Zᵗ + Yᵘ Zᵛ)
        p = int(rng.choice([-6, -5, -4, -3, -2, 2, 3]) if p is None else p)
        q = int(rng.choice([2, 3, 4, 5]) if q is None else q)
        r = int(rng.choice([3, 4, 5, 6]) if r is None else r)
        s = int(rng.choice([2, 3, 4, 5]) if s is None else s)
        t = int(rng.choice([4, 5, 6, 7]) if t is None else t)
        u = int(rng.choice([6, 7, 8, 9]) if u is None else u)
        v = int(rng.choice([-8, -7, -6, -5]) if v is None else v)
        if p + s == p or q + u == q or r + t == r + v:
            raise ItemError("a term would vanish or two routes would coincide")
        left = mono(1, [(X, p), (Y, q), (Z, r)])
        right = join([mono(1, [(X, s), (Z, t)]), mono(1, [(Y, u), (Z, v)])])
        expr = f"({left})({right})"

        def show(tt):
            (p1, q1, r1), (p2, q2, r2) = tt
            return join([mono(1, [(X, p1), (Y, q1), (Z, r1)]),
                         mono(1, [(X, p2), (Y, q2), (Z, r2)])])

        key = ((p + s, q, r + t), (p, q + u, r + v))
        chosen = [
            Slip("multiplied only the first term inside the parentheses by the "
                 "monomial", ((p + s, q, r + t), (0, u, v))),
            Slip(f"left {Y} out of both products because it is missing from one "
                 f"factor of each", ((p + s, 0, r + t), (p, 0, r + v))),
            Slip(f"kept only the variables that both factors carry, dropping {Y} "
                 f"from the first product and {X} from the second",
                 ((p + s, 0, r + t), (0, q + u, r + v))),
            Slip("multiplied the exponents instead of adding them",
                 ((p * s, q, r * t), (p, q * u, r * v))),
        ]
        why = (f"{left} multiplies each term inside the parentheses, and the "
               f"exponents of each variable add.")
        vs = sorted([X, Y, Z])
    else:                                            # √(c²X^2m Y^2n) / X^k
        c = int(rng.choice([2, 3, 4, 5, 6, 7, 9, 10]) if c is None else c)
        m = int(rng.choice([1, 2, 3]) if m is None else m)
        n = int(rng.choice([2, 3, 4]) if n is None else n)
        k = int(rng.choice([2, 3, 4, 5]) if k is None else k)
        if m - k == 0 or 2 * m % c or 2 * n % c:
            raise ItemError("this draw would not separate the wrong routes")
        inside = mono(c * c, [(X, 2 * m), (Y, 2 * n)])
        expr = f"√({inside})/{power(X, k)}"
        show = (lambda tt: mono(tt[0], [(X, tt[1]), (Y, tt[2])]))
        key = (c, m - k, n)
        chosen = [
            Slip("halved the coefficient instead of taking its square root, and "
                 f"never divided by {power(X, k)}", (c * c // 2, m, n)),
            Slip("subtracted the exponents the wrong way round and dropped the "
                 "minus sign", (c, k - m, n)),
            Slip("used the square root of the coefficient as the root's index and "
                 "divided each exponent by it",
                 (c, 2 * m // c - k, 2 * n // c)),
            Slip("took the square root of the coefficient but halved none of the "
                 "exponents", (c, 2 * m - k, 2 * n)),
        ]
        why = (f"√({inside}) is {mono(c, [(X, m), (Y, n)])}, and dividing by "
               f"{power(X, k)} subtracts {k} from the exponent of {X}.")
        vs = sorted([X, Y])

    if frame == "product_of" and shape == "distribute_powers":
        stem = sent(f"Which expression represents the product of ({left}) and "
                    f"({right})?")
    else:
        stem = frame_stem(frame if frame != "product_of" else "which", expr)
    if cond:
        stem = sent(f"If {cond}, {stem[0].lower()}{stem[1:]}")
    P = {"kind": "eqx_monomial_power", "expr": expr, "vars": vs}
    return text_item("eqx.monomial_power", "exponent rules", "medium", seed, stem,
                     why, key, show, chosen, rng, P)


# -------------------------------------------------------------- RADICAL_FORM

def radical_form(rng: random.Random, seed: int, *, shape=None, var=None, var2=None,
                 frame=None, n=None, a=None, b=None, c=None, e=None, f=None) -> Item:
    """A radical written as a power, or a power written as a radical."""
    shape = shape or rng.choice(["frac_exp", "root_of_powers", "root_of_square",
                                 "quotient", "product_root"])
    var = var or rng.choice(VARS)

    if shape == "frac_exp":
        n = int(rng.choice([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
                if n is None else n)
        expr = f"({var})^(1/{n})"
        key = root(n, var)
        chosen = [
            Slip("read the exponent as a coefficient", f"(1/{n}) · {var}"),
            Slip("read the denominator of the exponent as a multiplier",
                 f"{n} · {var}"),
            Slip("put the denominator of the exponent under the radical as a power "
                 "instead of using it as the index", f"√({power(var, n)})"),
            Slip("used the denominator as the power of the variable",
                 power(var, n)),
        ]
        why = (f"An exponent of 1/{n} is the {_ordinal(n)} root, so "
               f"{expr} is {key}.")
        stem = sent(f"Which expression is equivalent to {expr}, where {var} > 0?")
        vs = [var]
    elif shape == "root_of_powers":
        var, var2 = (var, var2) if var2 else rng.choice([("x", "y"), ("a", "b"),
                                                         ("u", "v"), ("p", "q")])
        n = int(rng.choice([2, 3, 4, 5]) if n is None else n)
        b = int(rng.choice([2, 3, 4]) if b is None else b)
        inside = mono(1, [(var, n), (var2, n * b)])
        expr = root(n, f"({inside})")
        key = mono(1, [(var, 1), (var2, b)])
        chosen = [
            Slip(f"treated {power(var, n)} under a root of index {n} as 1",
                 mono(1, [(var2, b)])),
            Slip("subtracted the index from the exponents instead of dividing by it, "
                 f"and dropped {var}", mono(1, [(var2, n * b - n)])),
            Slip("subtracted the index from the exponents instead of dividing by it",
                 mono(1, [(var, 1), (var2, n * b - n)])),
            Slip("divided only the first exponent by the index",
                 mono(1, [(var, 1), (var2, n * b)])),
        ]
        why = (f"A root of index {n} divides each exponent by {n}, so "
               f"{power(var, n)} becomes {var} and {power(var2, n * b)} becomes "
               f"{power(var2, b)}.")
        stem = sent(f"{expr}\nWhich of the following expressions is equivalent to "
                    f"the expression above?")
        vs = sorted([var, var2])
    elif shape == "root_of_square":
        n = int(rng.choice([4, 6, 8, 10]) if n is None else n)
        a = int(rng.choice([2, 3, 4, 5, 6, 7, 8, 9]) if a is None else a)
        inside = join([mono(1, [(var, 2)]), mono(2 * a, [(var, 1)]), mono(a * a, [])])
        expr = root(n, f"({inside})")
        base = f"({var} + {a})"
        key = pow_of(base, Q(2, n))
        chosen = [
            Slip("used the root's index as the exponent instead of dividing by it",
                 pow_of(base, n)),
            Slip("factored the trinomial but never took the root",
                 pow_of(base, 2)),
            Slip("wrote the exponent as 1 over the index and forgot the 2 the "
                 "square contributes", pow_of(base, Q(1, n))),
            Slip(f"took a square root rather than the root of index {n}", base),
            Slip("divided the index by the exponent instead of the other way round",
                 pow_of(base, Q(n, 2))),
        ]
        why = (f"{inside} is {base}², and a root of index {n} divides that "
               f"exponent by {n}.")
        stem = sent(f"Which of the following is equivalent to {expr}, where "
                    f"{var} > 0?")
        vs = [var]
    elif shape == "quotient":
        var, var2 = (var, var2) if var2 else rng.choice([("x", "y"), ("a", "b"),
                                                         ("u", "v"), ("p", "q")])
        a = int(rng.choice([2, 3, 4]) if a is None else a)           # x⁻ᵃ
        b = int(rng.choice([2, 3, 4, 5]) if b is None else b)        # 1/b in x^(1/b)
        c = int(rng.choice([2, 3]) if c is None else c)              # y^(1/c)
        ex, ey = Q(-a) - Q(1, b), Q(1, c) + 1
        if ex >= 0 or ey <= 0 or b == c:
            raise ItemError("this draw does not print as a quotient of radicals")
        expr = (f"({mono(1, [(var, -a)])}{power(var2, Q(1, c))})/"
                f"({power(var, Q(1, b))}{power(var2, -1)})")
        def show(t):
            top, _ = _rad_pow(var2, t[0])
            bot, wrap = _rad_pow(var, t[1])
            return f"{top}/({bot})" if wrap else f"{top}/{bot}"

        key = (ey, -ex)
        chosen = [
            Slip(f"multiplied the exponents of {var} instead of subtracting them",
                 (ey, Q(a, b))),
            Slip(f"multiplied the exponents of {var} and did not subtract the "
                 f"negative exponent of {var2}", (Q(1, c), Q(a, b))),
            Slip(f"subtracted one from the exponent of {var} instead of {a}, and "
                 f"read the root as a square root", (ey, Q(1) + Q(1, 2))),
            Slip(f"added the two exponents of {var2} the wrong way round",
                 (1 - Q(1, c), -ex)),
        ]
        why = (f"Dividing subtracts the exponents, so {var} carries "
               f"{num(ex)} and {var2} carries {num(ey)}.")
        stem = sent(f"The expression {expr}, where {var} > 1 and {var2} > 1, is "
                    f"equivalent to which of the following?")
        vs = sorted([var, var2])
        P = {"kind": "eqx_radical_form", "expr": expr, "vars": vs}
        return text_item("eqx.radical_form", "exponent rules", "hard", seed, stem,
                         why, key, show, chosen, rng, P)
    else:                                            # product_root
        var, var2 = (var, var2) if var2 else rng.choice([("a", "c"), ("x", "y"),
                                                         ("u", "v"), ("p", "q")])
        n = int(rng.choice([3]) if n is None else n)
        base = f"({var} + {var2})"
        expr = f"√({pow_of(base, n)})·√{base}"
        half = (n + 1) // 2
        key = join([mono(1, [(var, 2)]), mono(2, [(var, 1), (var2, 1)]),
                    mono(1, [(var2, 2)])])
        chosen = [
            Slip("added the two indices instead of the two exponents",
                 f"{var} + {var2}"),
            Slip("squared each term separately",
                 join([mono(1, [(var, 2)]), mono(1, [(var2, 2)])])),
            Slip("multiplied the two terms instead of squaring their sum",
                 mono(1, [(var, 2), (var2, 2)])),
            Slip("took the two roots separately and multiplied the results",
                 pow_of(base, half)),
        ]
        why = (f"The two square roots give exponents {n}/2 and 1/2, which add to "
               f"{(n + 1) // 2 if (n + 1) % 2 == 0 else str(n + 1) + '/2'}, so the "
               f"product is {base} squared.")
        stem = sent(f"If {var} and {var2} are positive numbers, which of the "
                    f"following is equivalent to {expr}?")
        vs = sorted([var, var2])
        if (n + 1) % 4:
            raise ItemError("the two roots must multiply to a whole power")

    P = {"kind": "eqx_radical_form", "expr": expr, "vars": vs}
    return text_item("eqx.radical_form", "exponent rules", "medium", seed, stem,
                     why, key, (lambda t: t), chosen, rng, P)


def _ordinal(n: int) -> str:
    names = {2: "square", 3: "cube", 4: "fourth", 5: "fifth", 6: "sixth",
             7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth", 11: "eleventh",
             12: "twelfth", 13: "thirteenth", 14: "fourteenth", 15: "fifteenth"}
    return names.get(n, f"{n}th")


# ------------------------------------------------------------ EXPONENT_VALUE

def exponent_value(rng: random.Random, seed: int, *, shape=None, var=None, m=None,
                   n=None, p=None, k=None, base=None) -> Item:
    """An expression that is one power of something; find the exponent."""
    shape = shape or rng.choice(["ratio", "product"])
    # the unknown in the "product" shape is called x, so the base cannot be
    var = var or rng.choice(["x", "t", "w", "z"] if shape == "ratio"
                            else ["n", "t", "w", "z"])

    if shape == "ratio":
        m = int(rng.choice([3, 5, 7, 9, 11]) if m is None else m)
        n = int(rng.choice([3, 4, 5, 6]) if n is None else n)
        p = int(rng.choice([2, 4, 5, 7, 8]) if p is None else p)
        e = Q(m, 2) - Q(p, n)
        if e <= 0 or e.denominator == 1:
            raise ItemError("the source's answer here is a fraction")
        expr = f"√({power(var, m)})/{root(n, f'({power(var, p)})')}"
        stem = sent(f"If {expr} = {var}^(a/b) for all positive values of {var}, "
                    f"what is the value of a/b ?")
        why = (f"The two radicals are {var}^({num(Q(m, 2))}) and "
               f"{var}^({num(Q(p, n))}), and dividing subtracts the exponents.")
        ex = E(e)
        routes = [
            Mis("added the exponents across a quotient instead of subtracting them",
                E(Q(m, 2) + Q(p, n))),
            Mis("used only the exponent from the numerator", E(Q(m, 2))),
            Mis("used only the exponent from the denominator", E(Q(p, n))),
            Mis("did not halve the exponent inside the square root", E(Q(m) - Q(p, n))),
        ]
        params = {"kind": "eqx_exponent_value", "expr": expr, "base": var,
                  "vars": [var], "mult": 1}
    else:
        base = base or f"{rng.choice([30, 40, 50, 60, 70, 80, 90])}{var}"
        m = int(rng.choice([3, 4, 5, 6, 7]) if m is None else m)
        n = int(rng.choice([4, 5, 6, 8, 9]) if n is None else n)
        k = int(rng.choice([10, 12, 15, 20, 24, 30]) if k is None else k)
        if m == n:
            raise ItemError("the two roots must differ")
        e = (Q(1, m) + Q(2, n)) / k
        expr = f"{root(m, f'({base})')}({root(n, f'({base})')})²"
        stem = sent(f"{expr}\nFor what value of x is the given expression "
                    f"equivalent to ({base})^({k}x), where {var} > 1?")
        why = (f"The two roots give exponents 1/{m} and 2/{n}, which add to "
               f"{num(Q(1, m) + Q(2, n))}, and that has to equal {k}x.")
        ex = E(e)
        routes = [
            Mis("stopped at the combined radical exponent without dividing by the stated multiplier",
                E(Q(1, m) + Q(2, n))),
            Mis("treated the squared second root as a single root",
                E((Q(1, m) + Q(1, n)) / k)),
            Mis("multiplied by the exponent multiplier instead of dividing by it",
                E((Q(1, m) + Q(2, n)) * k)),
        ]
        params = {"kind": "eqx_exponent_value", "expr": expr, "base": base,
                  "vars": [var], "mult": k}
    if ex.coef.denominator > 1000:
        raise ItemError("that exponent would not go into a grid-in")
    return Item("eqx.exponent_value", "exponent rules", "hard", seed, stem, "spr",
                ex, ex.gridin(), why, params=params,
                spr_mistakes=gridin_mistakes(ex, routes))


# ---------------------------------------------------------------- TELESCOPE

def telescope(rng: random.Random, seed: int, *, var=None, n=None, step=None,
              frame=None, flip=None) -> Item:
    """(1 − p)(1 + p + p² + ... + pⁿ), where everything in the middle cancels."""
    var = var or rng.choice(["p", "x", "t", "q", "r", "w"])
    n = int(rng.choice([3, 4, 5, 6, 7, 8, 9, 10]) if n is None else n)
    step = int(rng.choice([1, 1, 1, 2, 3]) if step is None else step)
    flip = rng.choice([False, False, True]) if flip is None else flip
    frame = frame or rng.choice(FRAME_NAMES)
    u = power(var, step) if step > 1 else var
    first = f"({u} {MINUS} 1)" if flip else f"(1 {MINUS} {u})"
    series = "(" + " + ".join(["1"] + [power(var, step * i) for i in range(1, n + 1)]) + ")"
    expr = first + series
    top = step * (n + 1)
    key = f"{power(var, top)} {MINUS} 1" if flip else f"1 {MINUS} {power(var, top)}"

    def other(e):
        return f"{power(var, e)} {MINUS} 1" if flip else f"1 {MINUS} {power(var, e)}"

    chosen = [
        Slip("counted the terms in the long bracket and used one power too many",
             other(top + step)),
        Slip("used the highest power that appears in the long bracket",
             other(step * n)),
        Slip("used one power less than the highest power in the long bracket",
             other(step * (n - 1))),
        Slip("added the two highest powers instead of cancelling the middle terms",
             other(step * (2 * n))),
    ]
    why = (f"Multiplying out gives every power from 1 to {power(var, top)} twice "
           f"with opposite signs, so only the first and the last terms survive.")
    stem = frame_stem(frame, expr)
    P = {"kind": "eqx_telescope", "expr": expr, "vars": [var]}
    return text_item("eqx.telescope", "equivalent expressions", "medium", seed,
                     stem, why, key, (lambda t: t), chosen, rng, P)
