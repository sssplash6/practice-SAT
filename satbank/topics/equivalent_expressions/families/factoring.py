"""Writing an expression as a product: the common factor, the quadratic, the
difference of two squares, and the square completed.

Factoring is the one place where the wrong answers are almost all *nearly*
right -- a factor pair whose product is correct but whose sum is not, the two
signs on the wrong brackets, half of the common factor taken out, the square
root of the variable taken but not of its coefficient -- so each is built as
the exact near-miss it is.
"""

from __future__ import annotations

import math
import random

from ....exact import E
from ....item import Item, ItemError, Mis, assemble, gridin_mistakes
from ..render import (MINUS, Q, join, mono, num, pc, poly, sent, show_terms,
                      sup, terms)
from .kit import FRAME_NAMES, Slip, frame_stem, text_item

__all__ = ["factor_gcf", "factor_quadratic", "difference_squares", "which_factor",
           "complete_square", "factor_constant"]

VARS = ["x", "n", "p", "t", "w", "y", "z", "d", "a", "r", "k", "j"]
PAIRS = [("x", "y"), ("a", "b"), ("y", "z"), ("p", "q"), ("c", "d"),
         ("s", "t"), ("u", "v")]


def _out(coef, powers, inner: str) -> str:
    """A factored form: '8w(15w + 1)', '3(4x + 9)', '6x²y²(x⁶ + 2)'."""
    head = mono(coef, powers)
    return f"({inner})" if head == "1" else f"{head}({inner})"


# --------------------------------------------------------------- FACTOR_GCF

def factor_gcf(rng: random.Random, seed: int, *, shape=None, var=None, var2=None,
               frame=None, slips=None, a=None, b=None, c=None, e=None, f=None,
               g=None) -> Item:
    """The greatest common factor taken outside a bracket."""
    shape = shape or rng.choice(["numeric", "numeric", "two_var", "monomial",
                                 "power", "exponent"])
    var = var or rng.choice(VARS)
    frame = frame or rng.choice(FRAME_NAMES)

    if shape == "numeric":
        slips = slips or rng.choice(["double", "arith", "factor"])
        e = int(rng.choice([1, 1, 2, 3]) if e is None else e)
        g = int(rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 11, 12]) if g is None else g)
        a = int(g * rng.randint(1, 9) if a is None else a)        # coefficient of vᵉ
        b = int(g * rng.randint(2, 9) if b is None else b)        # the constant
        if math.gcd(a, b) != g or a == b:
            raise ItemError("that is not the greatest common factor")
        expr = join([mono(a, [(var, e)]), mono(b, [])])
        show = (lambda t: _out(t[0], [], join([mono(t[1], [(var, e)]), mono(t[2], [])])))
        key = (g, a // g, b // g)
        pool = {
            "double": [
                Slip("took the common factor out but left the constant term "
                     "undivided", (g, a // g, b)),
                Slip("used the constant term as the common factor instead of the "
                     "greatest common factor", (b, a // g, b // g)),
                Slip("used the constant term as the common factor and left it "
                     "undivided", (b, a // g, b)),
            ],
            "arith": [
                Slip("took the common factor out but left the constant term "
                     "undivided", (g, a // g, b)),
                Slip("subtracted the common factor from the constant instead of "
                     "dividing by it", (g, a // g, b - g)),
                Slip("added the common factor to the constant instead of dividing "
                     "by it", (g, a // g, b + g)),
            ],
            "factor": [
                Slip("used the constant term as the common factor and left the "
                     "coefficient of the variable inside unchanged", (b, a, 1)),
                Slip("subtracted the common factor from each coefficient instead of "
                     "dividing by it", (g, a - g, b - g)),
                Slip("took the common factor out but left the constant term "
                     "undivided", (g, a // g, b)),
            ],
        }
        chosen = pool[slips] + [s for kk in pool if kk != slips for s in pool[kk]]
        why = (f"{g} is the largest number that divides both {a} and {b}, and each "
               f"term inside the parentheses is what is left after dividing by it.")
        names = [var]
    elif shape == "two_var":
        var, var2 = rng.choice(PAIRS) if var2 is None else (var, var2)
        a = int(rng.choice([6, 7, 8, 11, 12, 13, 14, 17, 19, 23, 26, 29, 34, 41])
                if a is None else a)
        expr = join([mono(a, [(var, 1)]), mono(a, [(var2, 1)])])
        key = f"{a}({var} + {var2})"
        chosen = [
            Slip("multiplied the two terms instead of adding them",
                 mono(a, [(var, 1), (var2, 1)])),
            Slip(f"combined the two unlike terms as if they were both {var}-terms",
                 mono(2 * a, [(var, 1)])),
            Slip(f"combined the two unlike terms as if they were both {var2}-terms",
                 mono(2 * a, [(var2, 1)])),
            Slip("halved the common factor instead of taking all of it out",
                 f"{2 * a}({var}/2 + {var2}/2)"),
        ]
        show = (lambda t: t)
        why = (f"{a} multiplies both terms, so it comes outside and {var} + {var2} "
               f"is what is left.")
        names = sorted([var, var2])
    elif shape == "monomial":
        a = int(rng.choice([3, 5, 7, 9, 11, 13, 15, 17, 19, 21]) if a is None else a)
        b = int(rng.choice([2, 4, 8, 10, 14, 16, 22, 26]) if b is None else b)
        e = int(rng.choice([2, 2, 3]) if e is None else e)
        f = int(rng.choice([1, 1, 2]) if f is None else f)
        if math.gcd(a, b) != 1 or e <= f:
            raise ItemError("this shape wants coprime coefficients and a real gap")
        expr = join([mono(a, [(var, e)]), mono(b, [(var, f)])])
        key = _out(1, [(var, f)], join([mono(a, [(var, e - f)]), mono(b, [])]))
        chosen = [
            Slip("took the whole second term out as the common factor",
                 _out(b, [(var, f)], join([mono(a, [(var, e - f)]), mono(1, [])]))),
            Slip("took the whole first term out as the common factor",
                 _out(a, [(var, e)], join([mono(b, [(var, f)]), mono(1, [])]))),
            Slip("added the two coefficients and took that outside",
                 _out(a + b, [], join([mono(1, [(var, e)]), mono(1, [(var, f)])]))),
            Slip("took the variable out but not at the lower of the two powers",
                 _out(1, [(var, e)], join([mono(a, [(var, f)]), mono(b, [])]))),
        ]
        show = (lambda t: t)
        why = (f"{mono(1, [(var, f)])} is the highest power of {var} in both terms "
               f"and the coefficients share no factor, so only {mono(1, [(var, f)])} "
               f"comes out.")
        names = [var]
    elif shape == "power":
        g = int(rng.choice([2, 3, 4, 5, 6, 8, 9, 10]) if g is None else g)
        e = int(rng.choice([5, 6, 7, 8, 9, 10]) if e is None else e)
        c = int(rng.choice([2, 3, 5, 7, 11, 13]) if c is None else c)
        a, b = g, g * c                              # a·vᵉ − a·vᵉ⁻¹ + b·v
        if e < 4:
            raise ItemError("the powers are too low for this shape")
        expr = join([mono(a, [(var, e)]), mono(-a, [(var, e - 1)]),
                     mono(b, [(var, 1)])])
        inner = (lambda d: join([mono(1, [(var, e - 1 - d)]),
                                 mono(-1, [(var, e - 2 - d)]), mono(c, [])]))
        key = _out(g, [(var, 1)], inner(0))
        chosen = [
            Slip("took the common factor out but reduced none of the exponents",
                 _out(g, [(var, 1)], join([mono(1, [(var, e)]), mono(-1, [(var, e - 1)]),
                                           mono(c, [(var, 1)])]))),
            Slip("attached the powers of the variable to the coefficient instead of "
                 "to the variable",
                 _out(1, [(var, 1)], join([f"{g}{sup(e)}", f"-{g}{sup(e - 1)}",
                                           f"{b}"]))),
            Slip("took only the variable out and subtracted one from every "
                 "coefficient instead of dividing by the common factor",
                 _out(1, [(var, 1)], join([mono(a - 1, [(var, e)]),
                                           mono(-(a - 1), [(var, e - 1)]),
                                           mono(b - 1, [(var, 1)])]))),
        ]
        show = (lambda t: t)
        why = (f"Every term holds at least one {var} and a factor of {g}, so "
               f"{mono(g, [(var, 1)])} comes out and each exponent drops by one.")
        names = [var]
    else:                                            # exponent
        var, var2 = rng.choice(PAIRS) if var2 is None else (var, var2)
        g = int(rng.choice([2, 3, 4, 5, 6]) if g is None else g)
        c = int(rng.choice([2, 3, 4, 5]) if c is None else c)
        e = int(rng.choice([6, 7, 8, 9, 10]) if e is None else e)
        f = int(rng.choice([2, 3]) if f is None else f)
        b = int(rng.choice([2, 2, 3]) if b is None else b)
        if e - b < 2 or e % b == 0 and (e - b) == e // b:
            raise ItemError("the two wrong exponent routes would coincide")
        base = [(var, b), (var2, f)]
        expr = join([mono(g, [(var, e), (var2, f)]), mono(g * c, base)])
        key = _out(g, base, join([mono(1, [(var, e - b)]), mono(c, [])]))
        chosen = [
            Slip("divided the exponents instead of subtracting them",
                 _out(g, base, join([mono(1, [(var, e // b)]), mono(c, [])]))
                 if e % b == 0 else None),
            Slip("multiplied the two terms left inside instead of adding them",
                 _out(g, base, mono(c, [(var, e - b)]))),
            Slip("divided the exponents and dropped the second term",
                 _out(g, base, mono(1, [(var, e // b)])) if e % b == 0 else None),
            Slip("subtracted the exponents the wrong way round",
                 _out(g, base, join([mono(1, [(var, b - e)]), mono(c, [])]))),
        ]
        show = (lambda t: t)
        why = (f"{mono(g, base)} divides both terms, and dividing {mono(1, [(var, e)])} "
               f"by {mono(1, [(var, b)])} subtracts the exponents.")
        names = sorted([var, var2])

    stem = frame_stem(frame, expr)
    P = {"kind": "eqx_factor_gcf", "expr": expr, "vars": names}
    return text_item("eqx.factor_gcf", "factoring", "easy", seed, stem, why,
                     key, show, chosen, rng, P)


# ---------------------------------------------------------- FACTOR_QUADRATIC

def _pairs_of(n: int) -> list[tuple]:
    out = []
    for d in range(1, int(math.isqrt(n)) + 1):
        if n % d == 0:
            out.append((d, n // d))
    return out


def factor_quadratic(rng: random.Random, seed: int, *, shape=None, var=None,
                     frame=None, r1=None, r2=None) -> Item:
    """A quadratic written as two brackets -- the sum matters as much as the
    product."""
    shape = shape or rng.choice(["monic", "monic", "in_square"])
    var = var or rng.choice(VARS)
    frame = frame or rng.choice(FRAME_NAMES)
    power = 1 if shape == "monic" else 2
    body = mono(1, [(var, power)])

    r1 = int(rng.choice([-12, -10, -9, -8, -7, -6, -5, -4, -3, -2])
             if r1 is None else r1)                  # the negative constant
    r2 = int(rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 12]) if r2 is None else r2)
    if r1 >= 0 or r2 <= 0 or -r1 == r2:
        raise ItemError("this shape wants one positive and one negative constant")
    prod, summ = -r1 * r2, r1 + r2
    expr = join([mono(1, [(var, 2 * power)]), mono(summ, [(var, power)]),
                 mono(-prod, [])])

    def show(t):
        p, q = t
        first, second = (p, q) if shape == "monic" else ((q, p) if q > 0 else (p, q))
        return (f"({join([body, mono(first, [])])})"
                f"({join([body, mono(second, [])])})")

    key = (r1, r2)
    others = [(-d, prod // d) for d, _ in _pairs_of(prod)] + \
             [(-(prod // d), d) for d, _ in _pairs_of(prod)]
    others = [t for t in others if t != key and t[0] + t[1] != summ]
    others.sort(key=lambda t: (abs(abs(t[0]) - abs(t[1])), -abs(t[0])))
    chosen = [Slip("put the two signs on the wrong brackets", (-r2, -r1))]
    for p, q in others[:5]:
        chosen.append(Slip(f"found a pair whose product is {num(-prod)} but whose "
                           f"sum is {num(p + q)}, not {num(summ)}", (p, q)))
    why = (f"The constants in the two brackets have to multiply to {num(-prod)} "
           f"and add to {num(summ)}; that second condition is what rules out the "
           f"other factor pairs.")
    stem = frame_stem(frame, expr)
    P = {"kind": "eqx_factor_quadratic", "expr": expr, "vars": [var]}
    return text_item("eqx.factor_quadratic", "factoring", "easy" if shape == "monic"
                     else "medium", seed, stem, why, key, show, chosen, rng, P)


# -------------------------------------------------------- DIFFERENCE_SQUARES

def difference_squares(rng: random.Random, seed: int, *, shape=None, var=None,
                       frame=None, a=None, b=None, c=None) -> Item:
    """A² − B², and the two brackets that only differ in a sign."""
    shape = shape or rng.choice(["numeric", "radical"])
    var = var or rng.choice(VARS)
    frame = frame or rng.choice(FRAME_NAMES)

    if shape == "numeric":
        a = int(rng.choice([4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26])
                if a is None else a)
        b = int(rng.choice([6, 10, 14, 18, 22, 26, 30, 34, 38, 42]) if b is None else b)
        if a % 2 or b % 2 or a == b:
            raise ItemError("this shape halves both square roots")
        expr = join([mono(a * a, [(var, 2)]), mono(-b * b, [])])
        show = (lambda t: f"({join([mono(t[0], [(var, 1)]), mono(-t[1], [])])})"
                          f"({join([mono(t[0], [(var, 1)]), mono(t[2], [])])})")
        key = (a, b, b)
        chosen = [
            Slip("used the same sign in both brackets, which squares the first "
                 "bracket instead", (a, b, -b)),
            Slip("halved the two square roots instead of taking them",
                 (a // 2, b // 2, b // 2)),
            Slip("halved the two square roots and used the same sign in both "
                 "brackets", (a // 2, b // 2, -b // 2)),
            Slip("took the square root of the coefficient but not of the constant",
                 (a, b * b, b * b)),
        ]
        why = (f"{a * a} is {a}² and {b * b} is {b}², so the expression is "
               f"{mono(1, [(var, 1)])} times {a} all squared minus {b} squared.")
        P = {"kind": "eqx_difference_squares", "expr": expr, "vars": [var]}
    else:
        c = int(rng.choice([2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21, 22])
                if c is None else c)
        if any(c % (d * d) == 0 for d in range(2, int(math.isqrt(c)) + 1)) or c < 2:
            raise ItemError("the radical here has to be in its simplest form")
        expr = join([mono(1, [(var, 2)]), mono(-c, [])])
        rad = f"√{c}"
        show = (lambda t: t)
        key = f"({var} + {rad})({var} {MINUS} {rad})"
        chosen = [
            Slip("used the same sign in both brackets, which gives a square rather "
                 "than a difference of squares", f"({var} + {rad})²"),
            Slip("used the same negative sign in both brackets",
                 f"({var} {MINUS} {rad})²"),
            Slip(f"looked for two whole numbers multiplying to {MINUS}{c} instead of "
                 f"taking a square root", f"({var} + {c})({var} {MINUS} 1)"),
            Slip("took the square root of the whole expression instead of the "
                 "constant", f"({var} + {c})({var} {MINUS} {c})"),
        ]
        why = (f"{c} is not a perfect square, but it is still {rad} squared, so the "
               f"expression is a difference of two squares.")
        P = {"kind": "eqx_difference_squares", "expr": expr, "vars": [var]}

    stem = frame_stem(frame, expr)
    return text_item("eqx.difference_squares", "factoring", "easy" if shape == "numeric"
                     else "medium", seed, stem, why, key, show, chosen, rng, P)


# --------------------------------------------------------------- WHICH_FACTOR

def which_factor(rng: random.Random, seed: int, *, shape=None, var=None, var2=None,
                 a=None, b=None, p=None, q=None, lead=None) -> Item:
    """Not "factor this" but "is this one of the factors?"."""
    shape = shape or rng.choice(["perfect_square", "roman"])

    if shape == "perfect_square":
        var, var2 = rng.choice(PAIRS) if var2 is None else (var or "a", var2)
        a = int(rng.choice([2, 3, 4, 5, 6, 7]) if a is None else a)
        b = int(rng.choice([2, 3, 4, 5, 6, 7, 8, 9]) if b is None else b)
        if a == b or a == 1 or b == 1 or math.gcd(a, b) != 1:
            raise ItemError("the factor must be primitive and both roots real")
        expr = join([mono(a * a, [(var, 2)]), mono(2 * a * b, [(var, 1), (var2, 1)]),
                     mono(b * b, [(var2, 2)])])
        show = (lambda t: join([mono(t[0], [(var, 1)]), mono(t[1], [(var2, 1)])]))
        key = (a, b)
        chosen = [
            Slip("took the square roots of the variables but not of their "
                 "coefficients", (1, 1)),
            Slip(f"did not take the square root of the coefficient of "
                 f"{mono(1, [(var, 2)])}", (a * a, b)),
            Slip("took the square root of neither coefficient", (a * a, b * b)),
            Slip(f"did not take the square root of the coefficient of "
                 f"{mono(1, [(var2, 2)])}", (a, b * b)),
        ]
        why = (f"{mono(a * a, [(var, 2)])} is {mono(a, [(var, 1)])} squared, "
               f"{mono(b * b, [(var2, 2)])} is {mono(b, [(var2, 1)])} squared, and "
               f"the middle term is twice their product, so the polynomial is a "
               f"perfect square.")
        stem = sent(f"{expr}\nWhich of the following is a factor of the polynomial "
                    f"above?")
        P = {"kind": "eqx_which_factor", "shape": "pick", "poly": expr,
             "vars": sorted([var, var2])}
        return text_item("eqx.which_factor", "factoring", "medium", seed, stem, why,
                         key, show, chosen, rng, P)

    # roman: two candidate factors, and the answer is which of them work
    var = var or rng.choice(VARS)
    lead = int(rng.choice([2, 3, 4, 5]) if lead is None else lead)
    p = int(rng.choice([2, 3, 4, 5, 6, 7, 8, 11, 13]) if p is None else p)
    q = int(rng.choice([4, 5, 6, 7, 8, 9, 10, 11, 12]) if q is None else q)
    if math.gcd(lead, p) != 1 or p == q:
        raise ItemError("the non-monic factor must not share the leading factor")
    # (lead·v − p)(v + q)
    quad = pc([-p * q, lead * q - p, lead])
    expr = poly(quad, var)
    good = f"{join([mono(lead, [(var, 1)]), mono(-p, [])])}"
    bad = f"{join([mono(1, [(var, 1)]), mono(-q, [])])}"
    stem = sent(f"{expr}\nI. {bad}\nII. {good}\nWhich of the expressions above "
                f"is(are) a factor of the given polynomial?")
    key = "II only"
    chosen = [
        Slip(f"read the {num(q)} in the factorisation as {bad} instead of "
             f"{join([mono(1, [(var, 1)]), mono(q, [])])}", "I only"),
        Slip("checked only that the two numbers appear in the factorisation, not "
             "their signs", "I and II"),
        Slip("divided the constant term by the leading coefficient before testing "
             "the factors", "Neither I nor II"),
    ]
    why = (f"{expr} factors as ({good})"
           f"({join([mono(1, [(var, 1)]), mono(q, [])])}), so only the second "
           f"expression divides it.")
    P = {"kind": "eqx_which_factor", "shape": "roman", "poly": expr, "vars": [var],
         "candidates": [bad, good],
         "verdicts": {"00": "Neither I nor II", "10": "I only", "01": "II only",
                      "11": "I and II"}}
    return text_item("eqx.which_factor", "factoring", "hard", seed, stem, why,
                     key, (lambda t: t), chosen, rng, P)


# ------------------------------------------------------------ COMPLETE_SQUARE

def complete_square(rng: random.Random, seed: int, *, var=None, frame=None,
                    h=None, c=None) -> Item:
    """x² + bx + c rewritten as (x + h)² + k."""
    var = var or rng.choice(VARS)
    frame = frame or rng.choice(FRAME_NAMES)
    h = int(rng.choice([i for i in range(-9, 10) if abs(i) >= 2]) if h is None else h)
    c = int(rng.choice([i for i in range(-20, 21) if i]) if c is None else c)
    k = c - h * h
    if k == 0 or abs(k) == abs(c):
        raise ItemError("the completed square would collapse")
    expr = poly(pc([c, 2 * h, 1]), var)
    show = (lambda t: f"({join([mono(1, [(var, 1)]), mono(t[0], [])])})² "
                      f"{'+' if t[1] > 0 else MINUS} {abs(t[1])}")
    key = (h, k)
    chosen = [
        Slip("added the correction instead of subtracting it" if k < 0 else
             "subtracted the correction instead of adding it", (h, -k)),
        Slip("halved the middle coefficient but changed its sign", (-h, k)),
        Slip("halved the middle coefficient with the wrong sign and corrected the "
             "wrong way too", (-h, -k)),
        Slip("subtracted the middle coefficient rather than half of it squared",
             (h, c - 2 * h)),
    ]
    why = (f"Half of {num(2 * h)} is {num(h)}, and "
           f"({join([mono(1, [(var, 1)]), mono(h, [])])})² already carries "
           f"{num(h * h)}, so {num(k)} is what is left to reach {num(c)}.")
    stem = frame_stem(frame, expr)
    P = {"kind": "eqx_complete_square", "expr": expr, "vars": [var]}
    return text_item("eqx.complete_square", "factoring", "medium", seed, stem, why,
                     key, show, chosen, rng, P)


# ------------------------------------------------------------ FACTOR_CONSTANT

def factor_constant(rng: random.Random, seed: int, *, shape=None, var=None,
                    letter=None, b=None, c=None, d=None, p=None, q=None,
                    lead=None, fmt=None) -> Item:
    """A factorisation with a constant missing, and the constant is the answer."""
    shape = shape or rng.choice(["sq_over", "sq_diff", "cubic_root"])
    var = var or rng.choice(["x", "n", "t", "w"])

    if shape == "sq_over":
        letter = letter or "c"
        other = "b" if letter != "b" else "k"
        b = int(rng.randint(2, 9) if b is None else b)
        key = Q(b * b)
        expr = f"({var}² {MINUS} {letter})/({var} {MINUS} {other})"
        stem = sent(f"{expr}\nIn the expression above, {other} and {letter} are "
                    f"positive integers. If the expression is equivalent to "
                    f"{var} + {other} and {var} ≠ {other}, which of the following "
                    f"could be the value of {letter} ?")
        mistakes = [
            Mis("kept the middle terms of the expansion instead of letting them "
                "cancel", E(b * b + 2 * b)),
            Mis(f"used {other}({other} + 1) in place of {other}²", E(b * b + b)),
            Mis(f"left three copies of {other} behind when expanding",
                E(b * b + 3 * b)),
            Mis(f"doubled {other} instead of squaring it", E(2 * b)),
        ]
        why = (f"({var} {MINUS} {other})({var} + {other}) is {var}² {MINUS} {other}², "
               f"so {letter} has to be a perfect square.")
        params = {"kind": "eqx_factor_constant", "shape": "sq_over", "var": var,
                  "numerator": f"{var}² − @c", "denominator": f"{var} − @b",
                  "target": f"{var} + @b", "max_b": 60}
        ex = E(key)
    elif shape == "sq_diff":
        letter = letter or "k"
        d = int(rng.choice([2, 3, 4, 5, 6, 7, 8, 10, 11, 12]) if d is None else d)
        c = int(rng.choice([2, 3, 4, 5]) if c is None else c)
        if int(math.isqrt(c * d)) ** 2 == c * d:
            raise ItemError("a whole-number constant makes three options collapse")
        lead_txt = f"(1/{c})"
        expr = f"{lead_txt}{var}² {MINUS} {d}"
        stem = sent(f"The expression {expr} can be rewritten as "
                    f"{lead_txt}({var} {MINUS} {letter})({var} + {letter}), where "
                    f"{letter} is a positive constant. What is the value of "
                    f"{letter} ?")
        ex = E(1, 0, c * d)
        mistakes = [
            Mis(f"gave {letter}² instead of {letter}", E(c * d)),
            Mis("left the denominator out before taking the square root", E(1, 0, d)),
            Mis("reported the constant term of the expression", E(d)),
            Mis("multiplied the denominator by the constant instead of taking a "
                "square root", E(c)),
        ]
        why = (f"{lead_txt}({var} {MINUS} {letter})({var} + {letter}) is "
               f"{lead_txt}{var}² {MINUS} {letter}²/{c}, so {letter}² is "
               f"{c} × {d}.")
        params = {"kind": "eqx_factor_constant", "shape": "sq_diff", "var": var,
                  "expr": expr, "lead": float(Q(1, c))}
        key = None
    else:                                            # cubic_root, a grid-in
        letter = letter or "b"
        lead = int(rng.choice([1, 2, 3, 4, 5]) if lead is None else lead)
        p = int(rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]) if p is None else p)
        q = int(rng.choice([5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]) if q is None else q)
        if p >= q:
            raise ItemError("the two factors must differ, smaller one first")
        expr = poly(pc([0, lead * p * q, lead * (p + q), lead]), var)
        stem = sent(f"One of the factors of {expr} is {var} + {letter}, where "
                    f"{letter} is a positive constant. What is the smallest "
                    f"possible value of {letter}?")
        ex = E(p)
        why = (f"{expr} is {mono(lead, [(var, 1)])}"
               f"({var} + {p})({var} + {q}), so {letter} is {p} or {q}.")
        params = {"kind": "eqx_factor_constant", "shape": "cubic_root", "var": var,
                  "expr": expr, "ask": "smallest"}
        return Item("eqx.factor_constant", "factoring", "hard", seed, stem, "spr",
                    ex, ex.gridin(), why, params=params,
                    spr_mistakes=gridin_mistakes(ex, [
                        Mis("chose the larger positive factor instead of the smallest", E(q)),
                        Mis("reported the sum of the two positive factor constants", E(p + q)),
                        Mis("reported the product of the two positive factor constants", E(p * q)),
                    ]))

    fmt = "mcq" if shape == "sq_over" else (fmt or ("spr" if rng.random() < 0.25
                                                    else "mcq"))
    if fmt == "spr":
        if not ex.is_rational:
            raise ItemError("that constant cannot be entered in a grid-in")
        return Item("eqx.factor_constant", "factoring", "hard", seed, stem, "spr",
                    ex, ex.gridin(), why, params=params)
    if shape == "sq_over":
        params["candidates"] = None                  # filled in below
    ch, tex, reasons, letter_ = assemble(ex, mistakes, rng, signed=False)
    if shape == "sq_over":
        params["candidates"] = [float(x) for x in
                                (float(c_) for c_ in
                                 (_numeric(o) for o in ch))]
    return Item("eqx.factor_constant", "factoring", "hard", seed, stem, "mcq",
                ex, letter_, why, ch, reasons, tex, params=params)


def _numeric(text: str) -> float:
    return float(str(text).replace(",", "").replace(MINUS, "-"))
