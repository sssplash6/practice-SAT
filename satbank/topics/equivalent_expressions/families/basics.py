"""Rewriting an expression without factoring it: collect, expand, substitute.

  COMBINE_LIKE   like terms in one line, and the exponent that must not move
  ADD_POLYS      the sum or the difference of two polynomials in brackets
  DISTRIBUTE     a coefficient, or a monomial, against a bracket
  PRODUCT        two brackets multiplied out
  EXPAND_SQUARE  a square, and the middle term everybody forgets
  SUBSTITUTE     expressions named by letters, put back before expanding

The wrong answers are the ones the source prints: the minus sign that reached
only the first term of the bracket, the coefficients added where they should
have been multiplied, the exponents added along with them, and the middle
term of (a + b)² left out.
"""

from __future__ import annotations

import random

from ..render import (MINUS, Q, join, mono, pc, paren, poly, show_terms, terms)
from .kit import (FRAMES, FRAME_NAMES, SUM_FRAMES, Item, ItemError, Slip,
                  frame_stem, sent, text_item)

__all__ = ["combine_like", "add_polys", "distribute", "product",
           "expand_square", "substitute"]

VARS = ["x", "n", "p", "t", "w", "y", "z", "d", "a", "r", "k", "j"]
PAIRS = [("x", "y"), ("a", "b"), ("y", "z"), ("p", "q"), ("c", "d"),
         ("s", "t"), ("u", "v")]
NICE = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20]


def _p(rng, lo=2, hi=20):
    return Q(rng.randint(lo, hi))


# ------------------------------------------------------------ COMBINE_LIKE

def combine_like(rng: random.Random, seed: int, *, shape=None, var=None, var2=None,
                 frame="which", slips=None, a=None, b=None, c=None, d=None,
                 k=None, m=None) -> Item:
    """Like terms gathered in a single line -- and the exponent that stays put."""
    shape = shape or rng.choice(["same_power", "same_power", "two_powers",
                                 "two_vars", "const_mid", "minus_group"])
    var = var or rng.choice(VARS)
    k = Q(rng.choice([1, 2, 2, 3, 3, 4, 5]) if k is None else k)
    a = _p(rng, 3, 20) if a is None else Q(a)

    if shape == "same_power":
        slips = slips or rng.choice(["arithmetic", "exponent"])
        b = Q(rng.choice([i for i in range(-20, 21) if abs(i) >= 2])
              if b is None else b)
        if a + b == 0 or a == b:
            raise ItemError("the two terms cancel, or the two routes coincide")
        expr = join([mono(a, [(var, k)]), mono(b, [(var, k)])])
        key = terms((((var, k),), a + b))
        sets = {
            "arithmetic": [
                Slip("added the coefficients where the expression subtracts them"
                     if b < 0 else
                     "subtracted the coefficients where the expression adds them",
                     terms((((var, k),), a - b))),
                Slip("multiplied the coefficients instead of combining them",
                     terms((((var, k),), a * b))),
                Slip("used the exponent as a factor on the combined coefficient",
                     terms((((var, k),), k * (a - b)))),
            ],
            "exponent": [
                Slip("added the coefficients where the expression subtracts them"
                     if b < 0 else
                     "subtracted the coefficients where the expression adds them",
                     terms((((var, k),), a - b))),
                Slip("combined the coefficients but added the exponents as well",
                     terms((((var, 2 * k),), a + b))),
                Slip("added both the coefficients and the exponents",
                     terms((((var, 2 * k),), a - b))),
            ],
        }
        chosen = sets[slips] + sets["arithmetic"] + sets["exponent"]
        why = (f"{mono(a, [(var, k)])} and {mono(abs(b), [(var, k)])} are like terms, "
               f"so only their coefficients combine and the exponent is unchanged.")
    elif shape == "two_powers":
        b = _p(rng, 2, 15) if b is None else Q(b)
        c = _p(rng, 2, 15) if c is None else Q(c)
        m = Q(rng.randint(1, int(k) - 1) if m is None else m)
        if m >= k or a + b == 0:
            raise ItemError("the unlike term must sit at a lower power")
        expr = join([mono(a, [(var, k)]), mono(b, [(var, k)]), mono(c, [(var, m)])])
        key = terms((((var, k),), a + b), (((var, m),), c))
        chosen = [
            Slip("multiplied the like terms instead of adding them, and added "
                 "their exponents", terms((((var, 2 * k),), a * b), (((var, m),), c))),
            Slip("combined the term that is not like the others with one of them",
                 terms((((var, k),), a), (((var, m),), b + c))),
            Slip("treated all three terms as alike and added every coefficient and "
                 "every exponent", terms((((var, 2 * k + m),), a + b + c))),
            Slip("added the exponents of the like terms as well as their coefficients",
                 terms((((var, 2 * k),), a + b), (((var, m),), c))),
        ]
        why = (f"{mono(a, [(var, k)])} and {mono(b, [(var, k)])} are the only like "
               f"terms, so they combine and {mono(c, [(var, m)])} stands alone.")
    elif shape == "two_vars":
        var, var2 = rng.choice(PAIRS) if var2 is None else (var, var2)
        b = _p(rng, 2, 15) if b is None else Q(b)
        c = _p(rng, 2, 15) if c is None else Q(c)
        d = _p(rng, 2, 15) if d is None else Q(d)
        if a == b or c == d or a - b == a + b:
            raise ItemError("two of the wrong routes would coincide")
        expr = join([mono(a, [(var, 1)]), mono(b, [(var, 1)]),
                     mono(c, [(var2, 1)]), mono(d, [(var2, 1)])])
        key = terms((((var, 1),), a + b), (((var2, 1),), c + d))
        chosen = [
            Slip(f"subtracted the two {var}-terms instead of adding them",
                 terms((((var, 1),), a - b), (((var2, 1),), c + d))),
            Slip("grouped the first term with the last and the second with the third",
                 terms((((var, 1),), a + d), (((var2, 1),), b + c))),
            Slip("grouped the outer and the inner terms, and subtracted in the "
                 "outer pair", terms((((var, 1),), a - d), (((var2, 1),), b + c))),
            Slip("added every coefficient and attached both variables",
                 terms((((var, 1), (var2, 1)), a + b + c + d))),
        ]
        why = (f"Only the two {var}-terms are alike, and only the two {var2}-terms "
               f"are alike, so each pair combines on its own.")
    elif shape == "const_mid":
        b = _p(rng, 2, 20) if b is None else Q(b)
        if a == b or k < 2:
            raise ItemError("the two constants must differ under a real power")
        expr = join([mono(a, []), mono(1, [(var, k)]), mono(b, [])])
        key = terms((((var, k),), 1), ((), a + b))
        chosen = [
            Slip("multiplied the two constants instead of adding them",
                 terms((((var, k),), 1), ((), a * b))),
            Slip("subtracted the constants instead of adding them",
                 terms((((var, k),), 1), ((), a - b))),
            Slip("changed the sign of the combined constant",
                 terms((((var, k),), 1), ((), -(a + b)))),
            Slip("added the constants into the coefficient of the power",
                 terms((((var, k),), 1 + a + b))),
        ]
        why = (f"{mono(1, [(var, k)])} is not a constant, so only {mono(a, [])} and "
               f"{mono(b, [])} combine.")
    else:                                            # minus_group
        a = _p(rng, 10, 40) if a is None else Q(a)
        b = _p(rng, 2, 12) if b is None else Q(b)
        c = _p(rng, 2, 12) if c is None else Q(c)
        if b == c or a - b - c <= 0:
            raise ItemError("the bracket must leave something positive behind")
        inner = join([mono(b, [(var, 1)]), mono(c, [(var, 1)])])
        expr = f"{mono(a, [(var, 1)])} {MINUS} ({inner})"
        key = terms((((var, 1),), a - b - c))
        chosen = [
            Slip("subtracted only the first term inside the parentheses",
                 terms((((var, 1),), a - b + c))),
            Slip("added the first term inside the parentheses and subtracted the "
                 "second", terms((((var, 1),), a + b - c))),
            Slip("subtracted the second term inside the parentheses twice",
                 terms((((var, 1),), a - b - 2 * c))),
            Slip("added everything inside the parentheses instead of subtracting it",
                 terms((((var, 1),), a + b + c))),
        ]
        why = (f"The minus sign applies to both terms inside the parentheses, so "
               f"{mono(b, [(var, 1)])} and {mono(c, [(var, 1)])} are both taken away.")

    stem = frame_stem(frame, expr)
    P = {"kind": "eqx_combine_like", "expr": expr,
         "vars": sorted({var} | ({var2} if shape == "two_vars" else set()))}
    return text_item("eqx.combine_like", "equivalent expressions", "easy", seed,
                     stem, why, key, show_terms, chosen, rng, P)


# -------------------------------------------------------------- ADD_POLYS

def _at(t: tuple, i: int) -> Q:
    return t[i] if 0 <= i < len(t) else Q(0)


def _pos(p: tuple) -> list[int]:
    """The degrees that actually print, highest first."""
    return [i for i in range(len(p) - 1, -1, -1) if p[i] != 0]


def _align(p: tuple, q: tuple, mult: bool, powers: bool) -> tuple:
    """Pairing the two polynomials term by term as they are written."""
    dp, dq = _pos(p), _pos(q)
    if len(dp) != len(dq):
        return None
    out = []
    for i, j in zip(dp, dq):
        coef = p[i] * q[j] if mult else p[i] + q[j]
        out.append(((i + j if powers else i), coef))
    hi = max(d for d, _ in out)
    acc = [Q(0)] * (hi + 1)
    for d, c in out:
        acc[d] += c
    return pc(acc)


def add_polys(rng: random.Random, seed: int, *, op=None, P=None, R=None, var=None,
              frame=None, slips=None, decimal=False, brackets=True, deg=None) -> Item:
    """Two polynomials in brackets, added or subtracted."""
    op = op or rng.choice(["sum", "difference"])
    var = var or rng.choice(VARS)
    if P is None or R is None:
        n = rng.choice([2, 2, 3, 4])
        P = [rng.choice([i for i in range(-9, 10)]) for _ in range(n)]
        R = [rng.choice([i for i in range(-9, 10)]) for _ in range(n)]
        P[-1] = rng.choice([i for i in (1, 2, 3, 4, 5, -2, -3, 6)])
        R[-1] = rng.choice([i for i in (1, 2, 3, 4, 5, -2, -3, 6)])
    p, q = pc([Q(x) for x in P]), pc([Q(x) for x in R])
    if len(p) < 2 or len(q) < 2:
        raise ItemError("each polynomial needs at least two terms")
    sign = Q(1) if op == "sum" else Q(-1)
    n = max(len(p), len(q))
    key = pc([_at(p, i) + sign * _at(q, i) for i in range(n)])
    if len(key) < 2:
        raise ItemError("the two polynomials collapse into a single term")

    show = (lambda t: poly(t, var, decimal))
    left, right = poly(p, var, decimal), poly(q, var, decimal)
    if frame in SUM_FRAMES:
        a, b = (paren(left), paren(right)) if brackets else (left, right)
        stem = sent(SUM_FRAMES[frame](a, b))
    else:
        frame = frame or rng.choice(FRAME_NAMES)
        joiner = "+" if op == "sum" else MINUS
        stem = frame_stem(frame, f"({left}) {joiner} ({right})")
    expr = f"({left}) {'+' if op == 'sum' else MINUS} ({right})"

    added = pc([_at(p, i) + _at(q, i) for i in range(n)])

    def one_off(base_sign, flip_deg):
        """The result with a single term combined the other way round."""
        out = [_at(p, i) + base_sign * _at(q, i) for i in range(n)]
        if flip_deg >= len(out):
            return None
        out[flip_deg] = _at(p, flip_deg) - base_sign * _at(q, flip_deg)
        return pc(out)

    mid = _pos(key)[len(_pos(key)) // 2] if len(_pos(key)) > 1 else 0
    deg = mid if deg is None else int(deg)
    lower = pc([key[i] if i == len(key) - 1 else -key[i] for i in range(len(key))])

    if op == "sum":
        pool = {
            "signs": [
                Slip("subtracted the constant terms instead of adding them",
                     one_off(Q(1), 0)),
                Slip("subtracted the constant terms the wrong way round",
                     pc([(_at(q, 0) - _at(p, 0) if i == 0 else _at(p, i) + _at(q, i))
                         for i in range(n)])),
                Slip("changed the sign of the combined constant term",
                     pc([(-(_at(p, 0) + _at(q, 0)) if i == 0 else _at(p, i) + _at(q, i))
                         for i in range(n)])),
            ],
            "powers": [
                Slip("added the exponents as well as the coefficients",
                     _align(p, q, False, True)),
                Slip("multiplied the coefficients of the like terms instead of "
                     "adding them", _align(p, q, True, False)),
                Slip("added every coefficient and every exponent as if all the "
                     "terms were alike",
                     pc([Q(0)] * (sum(_pos(p)) + sum(_pos(q)))
                        + [sum(p) + sum(q)])),
            ],
            "align": [
                Slip("lined the two polynomials up term by term as they are "
                     "written instead of matching like terms", _align(p, q, False, False)),
                Slip("lined the terms up as written and added the exponents too",
                     _align(p, q, False, True)),
                Slip("multiplied the coefficients of the like terms instead of "
                     "adding them", _align(p, q, True, False)),
            ],
        }
    else:
        def times(u: tuple, v: tuple) -> tuple:
            return pc([sum((u[i] * v[d - i] for i in range(len(u))
                            if 0 <= d - i < len(v)), Q(0))
                       for d in range(len(u) + len(v) - 1)])

        negq = pc([-c for c in q])
        prod_neg = times(p, negq)
        part = list(q)
        part[len(part) - 1] = -part[len(part) - 1]
        prod_part = times(p, pc(part))
        pool = {
            "signs": [
                Slip("added the second polynomial instead of subtracting it", added),
                Slip("let the minus sign reach only the middle term of the second "
                     "polynomial", one_off(Q(1), mid)),
                Slip("applied the minus sign to its own answer's lower terms "
                     "instead of to the second polynomial", lower),
            ],
            "partial": [
                Slip("added the second polynomial instead of subtracting it", added),
                Slip("did not carry the minus sign as far as the constant term",
                     one_off(Q(-1), 0)),
                Slip("did not carry the minus sign as far as the leading term",
                     one_off(Q(-1), len(key) - 1)),
            ],
            "grouped": [
                Slip("did not carry the minus sign as far as the constant term",
                     one_off(Q(-1), 0)),
                Slip("multiplied the first expression by the negative of the second "
                     "instead of subtracting", prod_neg),
                Slip("changed the sign of only the first term of the second "
                     "expression and then multiplied", prod_part),
            ],
            "onepower": [
                Slip(f"did not carry the minus sign as far as the {var}"
                     f"-term of degree {deg}", one_off(Q(-1), deg)),
                Slip("added the two polynomials and subtracted a single term",
                     one_off(Q(1), deg)),
                Slip("added the second polynomial instead of subtracting it", added),
            ],
        }
    slips = slips or rng.choice(list(pool))
    chosen = pool[slips] + [s for k in pool if k != slips for s in pool[k]]
    # an option that has lost the variable altogether is crossed out on sight
    chosen = [s for s in chosen if s.value is None or len(s.value) > 1]
    why = (f"Like terms are collected power by power"
           + ("." if op == "sum" else
              f", and the minus sign in front of ({right}) applies to every term "
              f"inside it."))
    P_ = {"kind": "eqx_add_polys", "expr": expr, "vars": [var]}
    return text_item("eqx.add_polys", "equivalent expressions",
                     "easy" if len(key) < 3 else "medium", seed, stem, why,
                     key, show, chosen, rng, P_)


# -------------------------------------------------------------- DISTRIBUTE

def distribute(rng: random.Random, seed: int, *, shape=None, var=None, var2=None,
               frame=None, slips=None, k=None, b=None, c=None, e=None, f=None,
               m=None, n=None) -> Item:
    """A coefficient or a monomial multiplied across a bracket."""
    shape = shape or rng.choice(["paren_const", "paren_const", "repeat", "monomial"])
    var = var or rng.choice(VARS)
    frame = frame or rng.choice(FRAME_NAMES)
    k = Q(rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10]) if k is None else k)

    if shape == "paren_const":
        slips = slips or rng.choice(["bracket", "outside", "constant"])
        e = Q(rng.choice([1, 1, 2, 3]) if e is None else e)
        b = Q(rng.choice([i for i in range(-12, 13) if abs(i) >= 2]) if b is None else b)
        c = Q(rng.randint(-10, 10) if c is None else c)
        pair = [(var, e)] if var2 is None else [(var, 1), (var2, 1)]
        inner = join([mono(1, pair), mono(b, [])])
        head = f"{k if k != 1 else ''}"
        expr = f"{head}({inner})" + ("" if c == 0 else
                                     (f" + {c}" if c > 0 else f" {MINUS} {-c}"))
        key = terms((tuple(pair), k), ((), k * b + c))
        if k * b + c == 0:
            raise ItemError("the constant disappears and the options collapse")
        pool = {
            "bracket": [
                Slip("did not multiply the constant inside the parentheses",
                     terms((tuple(pair), k), ((), b + c))),
                Slip("combined the constant outside with the one inside before "
                     "distributing", terms((tuple(pair), k), ((), k * (b + c)))),
                Slip("multiplied the coefficient of the variable by the constant "
                     "inside instead of distributing",
                     terms((tuple(pair), k * b), ((), c))),
            ],
            "outside": [
                Slip("did not multiply the constant inside the parentheses",
                     terms((tuple(pair), k), ((), b + c))),
                Slip("subtracted the constant outside the parentheses instead of "
                     "adding it", terms((tuple(pair), k), ((), k * b - c))),
                Slip("neither distributed to the constant inside nor kept the sign "
                     "of the constant outside", terms((tuple(pair), k), ((), b - c))),
            ],
            "constant": [
                Slip("did not multiply the constant inside the parentheses",
                     terms((tuple(pair), k), ((), b + c))),
                Slip("added the coefficient to the constant inside instead of "
                     "multiplying", terms((tuple(pair), k), ((), k + b + c))),
                Slip("subtracted the constant inside from the coefficient instead "
                     "of multiplying", terms((tuple(pair), k), ((), k - b + c))),
            ],
        }
        chosen = pool[slips] + [s for key_ in pool if key_ != slips for s in pool[key_]]
        why = (f"The {k} multiplies both {mono(1, pair)} and {mono(b, [])}, and only "
               f"then is the constant outside collected.")
    elif shape == "repeat":
        m = Q(rng.choice([2, 3, 4, 5, 6]) if m is None else m)
        n = Q(rng.choice([2, 3, 4, 5, 7]) if n is None else n)
        e = Q(rng.choice([2, 3]) if e is None else e)
        f = Q(rng.choice([1, 1, 2]) if f is None else f)
        if e <= f or m == n:
            raise ItemError("the bracket needs two different powers")
        inner = join([mono(1, [(var, e)]), mono(-1, [(var, f)])])
        expr = f"{m}({inner}) + {n}({inner})"
        key = terms((((var, e),), m + n), (((var, f),), -(m + n)))
        chosen = [
            Slip("changed the sign of the second term inside the parentheses",
                 terms((((var, e),), m + n), (((var, f),), m + n))),
            Slip(f"treated {inner} as a single {mono(1, [(var, f)])}-term",
                 terms((((var, f),), m + n))),
            Slip(f"treated {inner} as a single {mono(1, [(var, e)])}-term",
                 terms((((var, e),), m + n))),
            Slip("multiplied the two coefficients outside instead of adding them",
                 terms((((var, e),), m * n), (((var, f),), -(m * n)))),
        ]
        why = (f"Both brackets hold the same {inner}, so there are {m} of it and "
               f"{n} more of it.")
    else:                                            # monomial
        e = Q(rng.choice([1, 2, 3]) if e is None else e)
        f = Q(rng.choice([1, 1, 2]) if f is None else f)
        b = Q(rng.choice([2, 3, 4, 5, 6, 7, 8, 9]) if b is None else b)
        inner = join([mono(1, [(var, f)]), mono(b, [])])
        expr = f"{mono(k, [(var, e)])}({inner})"
        key = terms((((var, e + f),), k), (((var, e),), k * b))
        chosen = [
            Slip("multiplied only the first term inside the parentheses",
                 terms((((var, e + f),), k), ((), b))),
            Slip("added the coefficients and the exponents instead of distributing",
                 terms((((var, e + f),), k + b))),
            Slip("added what is inside the parentheses into one term and added the "
                 "number inside to the exponent as well",
                 terms((((var, e + b),), k * (1 + b)))),
            Slip("multiplied the second term by the coefficient but not by the "
                 "variable", terms((((var, e + f),), k), ((), k * b))),
        ]
        why = (f"{mono(k, [(var, e)])} multiplies both {mono(1, [(var, f)])} and "
               f"{mono(b, [])}, and the exponents add when the powers multiply.")

    stem = frame_stem(frame, expr)
    P = {"kind": "eqx_distribute", "expr": expr,
         "vars": sorted({var} | ({var2} if var2 else set()))}
    return text_item("eqx.distribute", "equivalent expressions", "easy", seed,
                     stem, why, key, show_terms, chosen, rng, P)


# ----------------------------------------------------------------- PRODUCT

def _mul_terms(t1, t2):
    out = []
    for p1, c1 in t1:
        for p2, c2 in t2:
            d = dict(p1)
            for v, e in p2:
                d[v] = d.get(v, Q(0)) + e
            out.append((tuple(sorted(d.items())), c1 * c2))
    return terms(*out)


def product(rng: random.Random, seed: int, *, shape=None, var=None, var2=None,
            frame=None, slips=None, a=None, b=None, c=None, d=None,
            m=None, n=None, p=None, q=None, e=None, f=None, g=None) -> Item:
    """Two brackets multiplied out, term against term."""
    shape = shape or rng.choice(["binomials", "binomials", "two_var_mixed"])
    var = var or rng.choice(VARS)
    frame = frame or rng.choice(FRAME_NAMES)

    if shape == "binomials":
        slips = slips or rng.choice(["expressions", "crossterms"])
        a = Q(rng.choice([1, 1, 2, 3, 4, 5]) if a is None else a)
        b = Q(rng.choice([i for i in range(-9, 10) if abs(i) >= 2]) if b is None else b)
        c = Q(rng.choice([1, 1, 2, 3, 4, 8]) if c is None else c)
        d = Q(rng.choice([i for i in range(-9, 10) if abs(i) >= 2]) if d is None else d)
        m = Q(rng.choice([1, 2, 3]) if m is None else m)
        n = Q(rng.choice([0, 1]) if n is None else n)
        p = Q(rng.choice([1, 2, 3]) if p is None else p)
        q = Q(rng.choice([0, 1]) if q is None else q)
        if m <= n or p <= q:
            raise ItemError("each bracket must print its higher power first")
        left = terms((((var, m),), a), (((var, n),), b))
        right = terms((((var, p),), c), (((var, q),), d))
        lt, rt = show_terms(left), show_terms(right)
        expr = f"({lt})({rt})"
        key = _mul_terms(left, right)
        if len(key) < 3:
            raise ItemError("the product collapses to two terms")
        diff = terms(*(list(left) + [(pw, -co) for pw, co in right]))
        summ = terms(*(list(left) + list(right)))
        # the four partial products, so a wrong route can spoil exactly one
        ac, ad = (((var, m + p),), a * c), (((var, m + q),), a * d)
        bc, bd = (((var, n + p),), b * c), (((var, n + q),), b * d)
        sgn = -1 if b * c < 0 else 1
        lead_add = terms((ac[0], a + c), ad, bc, bd)
        outer = terms(ac, ad, (bc[0], sgn * (abs(b) + abs(c))), bd)
        firstlast = terms(ac, bd)
        pool = {
            "expressions": [
                Slip("subtracted the second expression instead of multiplying by it",
                     diff),
                Slip("added the two expressions instead of multiplying them", summ),
                Slip("added the leading coefficients instead of multiplying them",
                     lead_add),
            ],
            "crossterms": [
                Slip("added the coefficients of the outer pair instead of "
                     "multiplying them", outer),
                Slip("multiplied the first terms and the last terms and left the "
                     "two middle products out", firstlast),
                Slip("added the two expressions instead of multiplying them", summ),
            ],
        }
        chosen = pool[slips] + [s for kk in pool if kk != slips for s in pool[kk]]
        why = (f"Every term of ({lt}) multiplies every term of ({rt}), and the two "
               f"middle products are then collected.")
        names = [var]
    else:                                            # two_var_mixed
        var, var2 = rng.choice(PAIRS) if var2 is None else (var, var2)
        b = Q(rng.choice([3, 5, 7, 9, 11, 13]) if b is None else b)
        c = Q(rng.choice([2, 3, 4, 5]) if c is None else c)
        d = Q(rng.choice([2, 3, 4, 5, 6]) if d is None else d)
        e = Q(rng.choice([4, 6, 8, 10, 12, 14]) if e is None else e)
        f = Q(rng.choice([2, 3, 4]) if f is None else f)
        g = Q(rng.choice([2, 3, 4, 5]) if g is None else g)
        X, Y = (var, 1), (var2, 1)
        left = terms(((X,), 1), ((Y,), -b))
        right = terms(((X,), c), ((Y,), -d))
        tail = terms(((X,), -f), ((Y,), g))
        prod1 = _mul_terms(left, right)
        prod2 = _mul_terms(terms(((Y,), -e)), tail)
        key = terms(*(list(prod1) + list(prod2)))
        expr = (f"({show_terms(left)})({show_terms(right)}) {MINUS} "
                f"{mono(e, [Y])}({show_terms(tail)})")
        chosen = [
            Slip("added the terms instead of multiplying the brackets out",
                 terms(*(list(left) + [((Y,), -e)]))),
            Slip("used the minus sign in front of the second product twice -- once "
                 "inside it and once again when combining",
                 terms(*(list(prod1) + [(pw, -co) for pw, co in prod2]))),
            Slip("multiplied the first brackets out but kept the sign of the last "
                 "term of the second product",
                 terms(*(list(prod1) + [(pw, (-co if len(pw) == 1 and pw[0][0] == var2
                                              else co)) for pw, co in prod2]))),
            Slip("left the second product out altogether", prod1),
        ]
        why = (f"The two brackets multiply term by term, and "
               f"{mono(-e, [Y])} then multiplies both terms of "
               f"({show_terms(tail)}).")
        names = sorted([var, var2])

    stem = frame_stem(frame, expr)
    P = {"kind": "eqx_product", "expr": expr, "vars": names}
    return text_item("eqx.product", "equivalent expressions", "medium", seed,
                     stem, why, key, show_terms, chosen, rng, P)


# ----------------------------------------------------------- EXPAND_SQUARE

def _terminates(v) -> bool:
    """Does this fraction print as a finite decimal?"""
    d = Q(v).denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    return d == 1


def _half(mid_n, mid_d, sq_d, va, vb) -> str:
    """'a² + ab + b²/4' -- a square whose fraction stays a fraction."""
    parts = [mono(1, [(va, 2)])]
    if mid_n:
        head = f"{va}{vb}" if abs(mid_n) == 1 else f"{abs(mid_n)}{va}{vb}"
        body = head if mid_d == 1 else f"{head}/{mid_d}"
        parts.append((MINUS if mid_n < 0 else "") + body)
    tail = mono(1, [(vb, 2)])
    parts.append(tail if sq_d == 1 else f"{tail}/{sq_d}")
    return join(parts)


def expand_square(rng: random.Random, seed: int, *, shape=None, var=None, var2=None,
                  frame=None, a=None, b=None, c=None, d=None, e=None, k=None,
                  decimal=False) -> Item:
    """A binomial squared -- and the middle term everybody leaves out."""
    shape = shape or rng.choice(["square_plus", "square_minus_poly", "two_var_half"])
    var = var or rng.choice(VARS)
    frame = frame or rng.choice(FRAME_NAMES)

    if shape == "square_plus":                       # (av + b)² − (v + c) + d(v + e)
        a = Q(rng.choice([1, 2, 3, 4]) if a is None else a)
        b = Q(rng.choice([i for i in range(-9, 10) if abs(i) >= 2]) if b is None else b)
        c = Q(rng.choice([i for i in range(-9, 10) if i]) if c is None else c)
        d = Q(rng.choice([2, 3, 4, 5]) if d is None else d)
        e = Q(rng.choice([2, 3, 4, 5, 6]) if e is None else e)
        sq = f"({join([mono(a, [(var, 1)]), mono(b, [])])})²"
        expr = (f"{sq} {MINUS} ({join([mono(1, [(var, 1)]), mono(c, [])])}) + "
                f"{d}({join([mono(1, [(var, 1)]), mono(e, [])])})")
        mid, const = 2 * a * b - 1 + d, b * b - c + d * e
        key = pc([const, mid, a * a])
        if mid == -1 + d or const == b * b + c + d * e:
            raise ItemError("a wrong route would land on the answer")
        chosen = [
            Slip("left out the middle term of the square",
                 pc([const, -1 + d, a * a])),
            Slip("did not change the sign of the constant in the bracket that is "
                 "subtracted", pc([b * b + c + d * e, mid, a * a])),
            Slip("left out the middle term of the square and did not change the "
                 "sign of the subtracted constant",
                 pc([b * b + c + d * e, -1 + d, a * a])),
            Slip("squared each term of the bracket separately",
                 pc([b * b - c + d * e, -1 + d, a * a])),
        ]
        why = (f"{sq} is {poly(pc([b * b, 2 * a * b, a * a]), var)}, and the minus "
               f"sign in front of the second bracket reaches its constant too.")
        show, names = (lambda t: poly(t, var)), [var]
    elif shape == "square_minus_poly":               # (av + b)² − (cv² + d)
        a = Q(rng.choice([Q(3, 2), 2, 3, Q(1, 2), 4]) if a is None else a)
        b = Q(rng.choice([Q(-12, 5), -2, -3, 2, 3, Q(7, 2)]) if b is None else b)
        c = Q(rng.choice([Q(26, 5), 2, 3, 5, 6]) if c is None else c)
        d = Q(rng.choice([Q(-32, 5), -4, -6, 4, 6]) if d is None else d)
        if a * a == c or b == 0:
            raise ItemError("the squared term cancels")
        if not decimal:
            decimal = all(_terminates(v) for v in (a, b, c, d, b * b - d, 2 * a * b,
                                                   a * a - c))
        sq = f"({join([mono(a, [(var, 1)], decimal), mono(b, [], decimal)])})²"
        expr = f"{sq} {MINUS} ({poly(pc([d, 0, c]), var, decimal)})"
        key = pc([b * b - d, 2 * a * b, a * a - c])
        chosen = [
            Slip("doubled each term instead of squaring the binomial, so the middle "
                 "term never appeared", pc([2 * b - d, 0, 2 * a - c])),
            Slip("doubled each term instead of squaring and then added the two "
                 "constants rather than subtracting", pc([-2 * b - d, 0, 2 * a - c])),
            Slip("subtracted the two constant terms the wrong way round",
                 pc([d - b * b, 2 * a * b, a * a - c])),
            Slip("left out the middle term of the square", pc([b * b - d, 0, a * a - c])),
        ]
        why = (f"{sq} is {poly(pc([b * b, 2 * a * b, a * a]), var, decimal)}, and "
               f"every term of the second bracket is then subtracted.")
        show, names = (lambda t: poly(t, var, decimal)), [var]
    else:                                            # (a + b/k)²
        var, var2 = rng.choice(PAIRS) if var2 is None else (var, var2)
        k = int(rng.choice([2, 3, 4, 5]) if k is None else k)
        expr = f"({var} + {var2}/{k})²"
        key = (2, k, k * k)                          # (mid numerator, mid den, sq den)
        chosen = [
            Slip("left out the middle term of the square", (0, 1, k * k)),
            Slip("left out the middle term and squared only the numerator of the "
                 "fraction", (0, 1, k)),
            Slip("forgot to double the middle term and squared only the numerator "
                 "of the fraction", (1, k, k)),
            Slip("squared only the numerator of the fraction", (2, k, k)),
        ]
        why = (f"({var} + {var2}/{k})² is {var}² plus twice {var}·{var2}/{k} plus "
               f"({var2}/{k})², and squaring a fraction squares its denominator too.")

        def show(t):
            n, dd, sq_d = t
            g = 1
            for i in range(1, max(abs(n), 1) + 1):
                if n % i == 0 and dd % i == 0:
                    g = i
            return _half(n // g, dd // g, sq_d, var, var2)

        names = sorted([var, var2])

    stem = frame_stem(frame, expr)
    P = {"kind": "eqx_expand_square", "expr": expr, "vars": names}
    return text_item("eqx.expand_square", "equivalent expressions", "medium", seed,
                     stem, why, key, show, chosen, rng, P)


# -------------------------------------------------------------- SUBSTITUTE

def substitute(rng: random.Random, seed: int, *, shape=None, var=None, var2=None,
               frame=None, n1=None, n2=None, a=None, b=None, c=None, d=None,
               e=None, k=None) -> Item:
    """Letters that stand for expressions, put back before anything is expanded."""
    shape = shape or rng.choice(["two_defs", "square_diff", "complete_sub"])
    var = var or "x"

    if shape == "two_defs":
        n1 = n1 or rng.choice(["p", "u", "h", "s"])
        n2 = n2 or rng.choice([v for v in ("v", "w", "g", "q") if v != n1])
        a = Q(rng.choice([2, 3, 4, 5]) if a is None else a)
        b = Q(rng.choice([2, 3, 4, 5, 6, 7]) if b is None else b)
        c = Q(rng.choice([1, 1, 2]) if c is None else c)
        d = Q(rng.choice([3, 4, 5, 6, 7, 8]) if d is None else d)
        k = Q(rng.choice([2, 3, 4]) if k is None else k)
        first = pc([b, a])                           # n1 = a·x + b
        second = pc([d, c])                          # n2 = c·x + d
        prod = pc([first[0] * second[0], first[0] * second[1] + first[1] * second[0],
                   first[1] * second[1]])
        key = pc([prod[0] - k * first[0] + second[0],
                  prod[1] - k * first[1] + second[1], prod[2]])
        expr = f"{n1}{n2} {MINUS} {k}{n1} + {n2}"
        stem = sent(f"If {n1} = {poly(first, var)} and {n2} = {poly(second, var)}, "
                    f"which of the following is equivalent to "
                    f"{n1}{n2} {MINUS} {k}{n1} + {n2} ?")
        chosen = [
            Slip(f"multiplied {n1} by {n2} and stopped there", prod),
            Slip(f"subtracted {n2} instead of adding it",
                 pc([prod[0] - k * first[0] - second[0],
                     prod[1] - k * first[1] - second[1], prod[2]])),
            Slip(f"added {k}{n1} instead of subtracting it",
                 pc([prod[0] + k * first[0] + second[0],
                     prod[1] + k * first[1] + second[1], prod[2]])),
            Slip(f"left {n2} out of the sum",
                 pc([prod[0] - k * first[0], prod[1] - k * first[1], prod[2]])),
        ]
        why = (f"Putting {poly(first, var)} for {n1} and {poly(second, var)} for "
               f"{n2} turns the expression into one in {var} alone, and the like "
               f"terms are then collected.")
        show, names = (lambda t: poly(t, var)), [var]
        P = {"kind": "eqx_substitute", "expr": expr, "vars": [var],
             "defs": {n1: poly(first, var), n2: poly(second, var)}}
    elif shape == "square_diff":
        A, Bv, C = "a", "b", "c"
        y = var2 or (rng.choice(["y", "z", "w"]) if var == "x" else "y")
        expr = f"(({A} + {Bv}) − ({A} + {C}))²"
        key = terms((((Bv, 2),), 1), (((Bv, 1), (C, 1)), -2), (((C, 2),), 1))
        chosen = [
            Slip(f"subtracted the wrong pair and used {A} − {C}, where the {A}-terms "
                 f"do not cancel",
                 terms((((A, 2),), 1), (((A, 1), (C, 1)), -2), (((C, 2),), 1))),
            Slip(f"added the two expressions instead of subtracting, so the "
                 f"{A}-terms doubled, and multiplied {Bv} by {C} in the middle term",
                 terms((((A, 2),), 4), (((A, 1), (Bv, 1), (C, 1)), -4), (((C, 2),), 1))),
            Slip(f"added the two expressions instead of subtracting and forgot to "
                 f"double the middle term",
                 terms((((A, 2),), 4), (((A, 1), (Bv, 1), (C, 1)), -2),
                       (((Bv, 2), (C, 2)), 1))),
            Slip("squared each term separately",
                 terms((((Bv, 2),), 1), (((C, 2),), 1))),
        ]
        stem = sent(f"If {var}² = {A} + {Bv} and {y}² = {A} + {C}, which of the "
                    f"following is equal to ({var}² {MINUS} {y}²)² ?")
        why = (f"{var}² {MINUS} {y}² is ({A} + {Bv}) {MINUS} ({A} + {C}), and the "
               f"{A}-terms cancel before the difference is squared.")
        show, names = show_terms, [A, Bv, C]
        P = {"kind": "eqx_substitute", "expr": expr, "vars": names}
    else:                                            # complete_sub
        A, C, D = "a", "c", "d"
        expr = f"{var}² − {C}² − 2{C}{D} − {D}²"
        key = f"({var} + {A})({var} − {A})"
        chosen = [
            Slip(f"read {C}² + 2{C}{D} + {D}² as a square but added it instead of "
                 f"subtracting it", f"({var} + {A})²"),
            Slip(f"wrote the difference of two squares as a square",
                 f"({var} − {A})²"),
            Slip(f"replaced 2{C}{D} with {A}{var} instead of completing the square",
                 f"{var}² − {A}{var} − {A}²"),
            Slip(f"replaced only the first of the three subtracted terms",
                 f"{var}² − {A}² − 2{C}{D} − {D}²"),
        ]
        stem = sent(f"If {A} = {C} + {D}, which of the following is equivalent to "
                    f"the expression {expr}?")
        why = (f"{C}² + 2{C}{D} + {D}² is ({C} + {D})², which is {A}², so the "
               f"expression is a difference of two squares.")
        show, names = (lambda t: t), [var, C, D]
        P = {"kind": "eqx_substitute", "expr": expr, "vars": names,
             "defs": {A: f"{C} + {D}"}}

    return text_item("eqx.substitute", "equivalent expressions", "medium", seed,
                     stem, why, key, show, chosen, rng, P)
