"""Questions about a condition rather than about a root.

"How many distinct real solutions", "for what value of c is there exactly one",
"which value of t leaves none", "the line meets the parabola at exactly one
point": none of these is answered by solving anything. They turn on the sign of
b² − 4ac, and the wrong options are the places that sign goes wrong -- a dropped
factor of four, a discriminant read the wrong way round, a boundary value taken
as though it were inside the range it bounds.

`audit.py` decides every one of them by counting sign changes in a numeric
sweep of the printed quadratic, which never forms a discriminant at all.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis
from ..kit import (MINUS, choices, dec, displayed, eq, gridin, griddable,
                   gridin_pool, join, mono, num, paren, pick, poly, q, sent,
                   signed_terms, sup, text_choices)

__all__ = ["count_real_solutions", "count_system_solutions",
           "symbolic_intersections", "discriminant_constant", "tangent_constant",
           "tangent_point", "integer_roots_constant"]

COUNT_WORDS = {0: "Zero", 1: "Exactly one", 2: "Exactly two",
               "many": "Infinitely many"}
COUNT_SENTENCES = {0: "There are no solutions.", 1: "There is exactly 1 solution.",
                   2: "There are exactly 2 solutions.",
                   4: "There are exactly 4 solutions."}
PLAIN = {0: "Zero", 1: "One", 2: "Two", "more": "More than two"}

WHY = {
    0: "read the sign of the discriminant the wrong way round, and concluded "
       "that the curve never meets the axis",
    1: "counted the two square roots of a positive number as a single solution",
    2: "took the square root of a negative number as though it were positive",
    "many": "read the equation as an identity, true for every value of x",
    "more": "counted the two branches of the curve as separate solutions and then "
            "counted them again",
    4: "multiplied the number of solutions of the quadratic by the two branches "
       "of the curve",
}


def _statement_item(template: str, skill: str, difficulty: str, seed: int,
                    stem: str, key_label: str, others: list, rng, rationale: str,
                    params: dict, wrongs=None) -> Item:
    pool = {k: Mis(WHY[k], label) for k, label in others}
    ch, why, letter = text_choices(key_label, pick(pool, wrongs), rng, check=False)
    return Item(template, skill, difficulty, seed, sent(stem), "mcq", E(1), letter,
                sent(rationale), ch, why, list(ch),
                params=dict(params, options=list(ch)))


# --------------------------------------------- how many solutions an equation has

def count_real_solutions(rng: random.Random, seed: int, *, shape="standard", a=None,
                         b=None, c=None, h=0, k=None, wrongs=None,
                         difficulty="easy") -> Item:
    """ax² + bx + c = 0 or (x − h)² = k -- how many distinct real solutions?"""
    if shape == "square":
        h = q(h)
        k = Q(rng.choice([-9, -4, -1, 0, 1, 4, 9, 16])) if k is None else q(k)
        left = paren(join(["x", mono(-h, "")])) + sup(2) if h else "x" + sup(2)
        equation = eq(left, num(k))
        count = 0 if k < 0 else (1 if k == 0 else 2)
        disc_text = f"a square equal to {num(k)}"
    else:
        a = Q(rng.choice([1, 2, 3, 4, 5, -1, -2, -3])) if a is None else q(a)
        b = Q(rng.randint(-20, 20)) if b is None else q(b)
        c = Q(rng.randint(-40, 40)) if c is None else q(c)
        if a == 0:
            raise ItemError("not a quadratic")
        equation = eq(poly((c, b, a)), "0")
        d = b * b - 4 * a * c
        count = 0 if d < 0 else (1 if d == 0 else 2)
        disc_text = f"a discriminant of {num(d)}"
    stem = displayed(equation,
                     "How many distinct real solutions "
                     + ("are there to the given equation?" if shape == "standard"
                        else "does the given equation have?"))
    labels = dict(COUNT_WORDS)
    key_label = labels[count]
    others = [(kk, v) for kk, v in labels.items() if kk != count]
    P = {"kind": "nleq_count_equation", "shape": shape,
         "a": _p(a if shape == "standard" else 1),
         "b": _p(b if shape == "standard" else -2 * q(h)),
         "c": _p(c if shape == "standard" else q(h) * q(h) - q(k)),
         "count": count}
    rationale = sent(f"The equation has {disc_text}, so it has "
                     f"{['no', 'exactly one', 'exactly two'][count]} real "
                     f"{'solution' if count == 1 else 'solutions'}.")
    return _statement_item("nleq.count_real_solutions", "counting real solutions",
                           difficulty, seed, stem, key_label, others, rng,
                           rationale, P, wrongs)


# ------------------------------------------ how many solutions a system has

def count_system_solutions(rng: random.Random, seed: int, *, a=None, b=None, c=None,
                           m=None, d=None, labels="sentences", wrongs=None,
                           difficulty="hard") -> Item:
    """y = ax² + bx + c and a line -- how many points do the two graphs share?"""
    a = Q(rng.choice([1, 1, 2, 3, -1, -2])) if a is None else q(a)
    b = Q(rng.randint(-10, 10)) if b is None else q(b)
    c = Q(rng.randint(-20, 20)) if c is None else q(c)
    m = Q(rng.randint(-10, 10)) if m is None else q(m)
    d = Q(rng.randint(-20, 20)) if d is None else q(d)
    if a == 0:
        raise ItemError("not a quadratic")
    disc = (b - m) ** 2 - 4 * a * (c - d)
    count = 0 if disc < 0 else (1 if disc == 0 else 2)
    curve = eq("y", poly((c, b, a)))
    line = eq(join(["y", mono(-m, "x"), mono(-d, "")]), "0")
    stem = displayed(curve, line,
                     "How many solutions are there to the system of equations above?")
    table = COUNT_SENTENCES if labels == "sentences" else PLAIN
    key_label = table[count]
    others = [(kk, v) for kk, v in table.items() if kk != count]
    P = {"kind": "nleq_count_system", "a": _p(a), "b": _p(b), "c": _p(c),
         "m": _p(m), "d": _p(d), "count": count}
    rationale = sent(f"Setting the two right-hand sides equal gives "
                     f"{poly((c - d, b - m, a))} = 0, whose discriminant is "
                     f"{num(disc)}, so the graphs share "
                     f"{['no points', 'exactly one point', 'exactly two points'][count]}.")
    return _statement_item("nleq.count_system_solutions", "counting a system's "
                           "solutions", difficulty, seed, stem, key_label, others,
                           rng, rationale, P, wrongs)


# --------------------------------- a system written entirely in constants

_CONSTANTS = ["a", "b", "c", "d", "h", "j", "k", "m", "n", "p", "q", "r", "t",
              "u", "v", "w"]
LETTER_PAIRS = [(x, y) for x in _CONSTANTS for y in _CONSTANTS if x != y]


def symbolic_intersections(rng: random.Random, seed: int, *, pair=None, sign=None,
                           line=None, wrongs=None, difficulty="medium") -> Item:
    """y = ax² ± c against a horizontal line built from the same two constants.

    Nothing is a number, so nothing can be solved: what decides the count is
    whether the constant the square has to equal comes out positive, and that is
    read off the signs alone.
    """
    a, c = pair or rng.choice(LETTER_PAIRS)
    sign = int(rng.choice([-1, 1]) if sign is None else sign)
    line = line or rng.choice(["sum", "difference", "reverse", "negative"])
    rhs = {"sum": f"{a} + {c}", "difference": f"{a} {MINUS} {c}",
           "reverse": f"{c} {MINUS} {a}", "negative": f"{MINUS}{a} {MINUS} {c}"}[line]
    curve = eq("y", join([f"{a}x{sup(2)}", (MINUS if sign < 0 else "+") + f" {c}"])
               .replace("+ +", "+"))
    curve = eq("y", f"{a}x{sup(2)} " + ("+ " if sign > 0 else MINUS + " ") + c)
    # a·x² + sign·c = <line>  ->  x² = (<line> − sign·c)/a, with a and c positive
    coefficients = {"sum": (1, 1), "difference": (1, -1), "reverse": (-1, 1),
                    "negative": (-1, -1)}[line]
    need_a, need_c = coefficients[0], coefficients[1] - sign
    # x² = (need_a·a + need_c·c)/a, both letters positive
    if need_a >= 0 and need_c >= 0 and (need_a or need_c):
        count = 2
    elif need_a <= 0 and need_c <= 0 and (need_a or need_c):
        count = 0
    elif need_a == 0 and need_c == 0:
        count = 1
    else:
        raise ItemError("the sign of the square cannot be decided from the letters")
    stem = displayed(curve,
                     sent(f"In the equation above, {a} and {c} are positive "
                          f"constants. How many times does the graph of the equation "
                          f"above intersect the graph of the equation y = {rhs} in "
                          f"the xy-plane?"))
    table = dict(PLAIN)
    key_label = table[count]
    others = [(kk, v) for kk, v in table.items() if kk != count]
    P = {"kind": "nleq_symbolic_intersections", "sign": sign, "line": line,
         "count": count, "a": a, "c": c}
    rationale = sent(f"Setting the two sides equal gives {a}x{sup(2)} = "
                     f"{_need_text(need_a, a, need_c, c)}, and since {a} and {c} are "
                     f"positive the right-hand side is "
                     f"{'positive' if count == 2 else 'negative'}, so the graphs "
                     f"meet {'twice' if count == 2 else 'nowhere'}.")
    return _statement_item("nleq.symbolic_intersections", "counting intersections "
                           "from the signs", difficulty, seed, stem, key_label,
                           others, rng, rationale, P, wrongs)


def _need_text(na, a, nc, c) -> str:
    parts = []
    for n, letter in ((na, a), (nc, c)):
        if n:
            parts.append((MINUS if n < 0 else "") + (str(abs(n)) if abs(n) != 1 else "")
                         + letter)
    return join(parts) if parts else "0"


# ---------------------------------------- the constant a condition pins down

CONDITIONS = {
    "one": "The equation has exactly one solution. What is the value of {t}?",
    "none": "If the equation has no real solutions, which of the following could be "
            "the value of {t} ?",
    "more": "For which of the following values of {t} will the equation have more "
            "than one real solution?",
}


def discriminant_constant(rng: random.Random, seed: int, *, a=None, b=None, c=None,
                          unknown="c", slot="constant", condition="one",
                          side="left", value=None,
                          gap=None, offsets=(1, 2, 3), fmt=None, wrongs=None,
                          difficulty="hard") -> Item:
    """ax² + bx + c = 0 with one letter unknown, fixed or bounded by a condition.

    "Exactly one solution" fixes the discriminant at zero and so fixes the letter;
    "no real solutions" and "more than one" bound it, and the four options are then
    one value inside the range and three outside it -- the boundary itself among
    them, because taking a strict inequality as a weak one is the mistake.
    """
    a = Q(rng.choice([1, 2, 3, 4, -1, -2, -4, -16])) if a is None else q(a)
    b = Q(rng.choice([i for i in range(-24, 25) if i])) if b is None else q(b)
    if a == 0:
        raise ItemError("not a quadratic")
    letter = unknown

    if condition == "one":
        if slot != "constant":
            raise ItemError("this condition is stated for the constant term")
        key = b * b / (4 * a)
        if not griddable(key):
            raise ItemError("the constant would not print cleanly")
        equation = _printed(a, b, letter, side, "0")
        stem = displayed(equation,
                         sent(f"In the given equation, {letter} is a constant. "
                              + CONDITIONS["one"].format(t=letter)))
        d = q(gap) if gap is not None else (abs(b) or Q(1))
        pool = {
            "zero": Mis("took the constant term to be zero", Q(0)),
            "sign": Mis("solved b² = 4ac without the minus sign the leading "
                        "coefficient carries", -key),
            "no_four": Mis("left the factor of four out of the discriminant",
                           b * b / a),
            "quarter": Mis("divided by four twice over", key / 4),
            "two_solutions": Mis("chose a constant that leaves the curve crossing "
                                 "the axis twice", key + d),
            "no_solutions": Mis("chose a constant that leaves the curve clear of "
                                "the axis altogether", key - d),
        }
        P = {"kind": "nleq_discriminant_constant", "a": _p(a), "b": _p(b),
             "unknown": letter, "condition": condition,
             "side": side}
        rationale = sent(f"One solution means the discriminant is zero, so "
                         f"{signed_terms([(b * b, ''), (-4 * a, letter)])} = 0 and "
                         f"{letter} = {gridin(key).replace('-', MINUS)}.")
        keyx = E(key)
        fmt = fmt or "spr"
        if fmt == "spr":
            # key ± d is an offset no working produces, so a grid-in names
            # neither; and with a > 0 there is no minus sign to lose
            named = dict(pool)
            del named["two_solutions"], named["no_solutions"]
            if a > 0:
                named["sign"] = Mis("set b² + 4ac = 0 instead of b² − 4ac = 0",
                                    -key)
            return Item("nleq.discriminant_constant", "a condition on the "
                        "discriminant", difficulty, seed, sent(stem), "spr", keyx,
                        gridin(key), rationale, params=P,
                        spr_mistakes=gridin_pool(keyx, named.values()))
        ch, tex, why, letter_ = choices(keyx, pick(pool, wrongs), rng, guard=wrongs is None)
        return Item("nleq.discriminant_constant", "a condition on the discriminant",
                    difficulty, seed, sent(stem), "mcq", keyx, letter_, rationale,
                    ch, why, tex, params=P)

    # a bounded condition: the options straddle the boundary
    c = Q(rng.randint(-30, 30)) if c is None else q(c)
    want = (lambda d: d < 0) if condition == "none" else (lambda d: d > 0)
    if slot == "constant":
        # the unknown is the constant term, printed on whichever side the source
        # printed it -- `ax² + bx + t = 0` and `ax² + bx = t` bound it opposite ways
        sgn = 1 if side == "left" else -1
        bound = sgn * b * b / (4 * a)
        good = (lambda v: want(b * b - 4 * a * sgn * v))
        equation = _printed(a, b, letter, side, "0")
    else:                                     # the middle coefficient is unknown
        bound = _sqrt_bound(4 * a * c)
        if bound is None or bound == 0:
            raise ItemError("the boundary is not a number the page can print")
        good = (lambda v: want(v * v - 4 * a * c))
        equation = eq(join([mono(a, "x", 2), f"{letter}x", mono(c, "")]), "0")

    key = q(value) if value is not None else _first_good(good, bound, offsets)
    if key is None or not good(key) or not griddable(key):
        raise ItemError("no printable value satisfies the condition")
    stem = displayed(equation,
                     sent(f"In the given equation, {letter} is a constant. "
                          + CONDITIONS[condition].format(t=letter)))
    pool = {
        "boundary": Mis("took the boundary value itself, where the curve only "
                        "touches the axis", bound if not good(bound) else None),
        "boundary_mirror": Mis("used the boundary with its sign reversed",
                               -bound if not good(-bound) else None),
        "half_boundary": Mis("halved the boundary instead of passing it",
                             bound / 2 if not good(bound / 2) else None),
        "root_c": Mis("took the square root of the constant term rather than "
                      "comparing it with the discriminant",
                      _sqrt_bound(c) if c and not good(_sqrt_bound(c) or 0) else None),
        "wrong_side_1": Mis("chose a value on the wrong side of the boundary",
                            bound + 1 if not good(bound + 1) else
                            (bound - 1 if not good(bound - 1) else None)),
        "mirror_1": Mis("reversed the boundary's sign and stopped short of it",
                        -bound - 1 if not good(-bound - 1) else None),
        "mirror_2": Mis("reversed the boundary's sign and stepped past it",
                        -bound + 1 if not good(-bound + 1) else None),
    }
    P = {"kind": "nleq_discriminant_constant", "a": _p(a),
         "b": _p(b if slot == "constant" else 0),
         "c": _p(c if slot != "constant" else 0), "slot": slot,
         "unknown": letter, "condition": condition, "side": side,
         "key": _p(key)}
    rationale = sent(f"The discriminant is zero at {letter} = {num(bound)}, and the "
                     f"condition holds "
                     f"{'inside' if condition == 'none' else 'outside'} that "
                     f"boundary, which {num(key)} satisfies.")
    keyx = E(key)
    ch, tex, why, letter_ = choices(keyx, pick(pool, wrongs), rng, guard=wrongs is None)
    return Item("nleq.discriminant_constant", "a condition on the discriminant",
                difficulty, seed, sent(stem), "mcq", keyx, letter_, rationale, ch,
                why, tex, params=P)


def _bracketed(text: str) -> str:
    """A height printed against a coefficient keeps its brackets when it needs
    them: `12(c/4)` is a product, `4c` is not."""
    return text if text.isalpha() else f"({text})"


def _signed(v) -> str:
    """A number inside a formula: bracketed only when its sign needs it."""
    return f"({num(v)})" if q(v) < 0 else num(v)


def _printed(a, b, letter, side, rhs) -> str:
    """`ax² + bx + t = 0`, or `ax² + bx = t` when the source puts it on the right."""
    if side == "left":
        return eq(join([mono(a, "x", 2), mono(b, "x"), letter]), rhs)
    return eq(join([mono(a, "x", 2), mono(b, "x")]), letter)


def _sqrt_bound(v):
    v = q(v)
    if v < 0:
        return None
    from math import isqrt
    rn, rd = isqrt(v.numerator), isqrt(v.denominator)
    return Q(rn, rd) if rn * rn == v.numerator and rd * rd == v.denominator else None


def _first_good(good, bound, offsets):
    for step in list(offsets) + [4, 5, 6, 8, 11]:
        for cand in (bound - step, bound + step):
            if good(cand):
                return cand
    return None


# ------------------------------------ a line that touches a parabola once

def tangent_constant(rng: random.Random, seed: int, *, p=None, height=None, a=None,
                     b=None, ask="height", named="c", wrongs=None,
                     difficulty="hard") -> Item:
    """p·y = <constant> meets y = ax² + bx at exactly one point.

    Substituting the line's height leaves a·x² + b·x − height = 0, so the
    condition is b² = −4a·height: either the height or the curve's middle
    coefficient is the unknown, and the source asks for both.
    """
    p = Q(rng.choice([1, 2, 3, 4])) if p is None else q(p)
    a = Q(rng.choice([-1, -2, -3, -4, 1, 2, 3])) if a is None else q(a)
    if a == 0 or p == 0:
        raise ItemError("that is not a parabola")
    if ask == "height":
        b = Q(rng.choice([i for i in range(-12, 13) if i])) if b is None else q(b)
        h = -b * b / (4 * a)                 # the y-value the line has to carry
        key = p * h
        if not griddable(key):
            raise ItemError("the constant would not print cleanly")
        line = eq(mono(p, "y"), named)
        stem = sent(f"In the xy-plane, a line with equation {line} for some constant "
                    f"{named} intersects a parabola at exactly one point. If the "
                    f"parabola has equation y = {poly((0, b, a))}, what is the value "
                    f"of {named}?")
        height = named if p == 1 else f"{named}/{num(p)}"
        rationale = sent(f"The line is y = {height}, and one intersection means "
                         f"{join([num(b * b), mono(4 * a, _bracketed(height))])}"
                         f" = 0, so {named} = {gridin(key).replace('-', MINUS)}.")
        P = {"kind": "nleq_tangent_constant", "p": _p(p), "a": _p(a), "b": _p(b),
             "ask": ask, "height": _p(h)}
    else:
        height = Q(rng.choice([1, 2, 3, 4, 5, 6, 8, 9])) if height is None else q(height)
        h = height / p
        inside = -4 * a * h
        key = _sqrt_bound(inside)
        if key is None or key <= 0:
            raise ItemError("the constant would not come out a printable number")
        line = eq(mono(p, "y"), dec(height))
        stem = sent(f"In the xy-plane, a line with equation {line} intersects a "
                    f"parabola at exactly one point. If the parabola has equation "
                    f"y = {poly((0, 0, a))} + {named}x, where {named} is a positive "
                    f"constant, what is the value of {named}?")
        rationale = sent(f"The line is y = {num(h)}, and one intersection means "
                         f"{join([named + sup(2), mono(4 * a * h, '')])} = 0, so "
                         f"{named} = {gridin(key).replace('-', MINUS)}.")
        P = {"kind": "nleq_tangent_constant", "p": _p(p), "a": _p(a),
             "b": _p(0), "ask": ask, "height": _p(h)}
    return Item("nleq.tangent_constant", "a line touching a parabola", difficulty,
                seed, sent(stem), "spr", E(key), gridin(key), rationale, params=P)


def tangent_point(rng: random.Random, seed: int, *, a=None, b=None, c=None, m=None,
                  named="a", fmt="mcq", wrongs=None, difficulty="hard") -> Item:
    """y = ax² + bx + c and y = mx + k meet once; where do they meet?

    The unknown constant slides the line up and down without turning it, so the
    single point is fixed by the slopes alone: x = (m − b)/(2a).
    """
    a = Q(rng.choice([1, 2, 3, -1, -2])) if a is None else q(a)
    b = Q(rng.choice([i for i in range(-24, 25) if i])) if b is None else q(b)
    c = Q(rng.randint(-80, 80)) if c is None else q(c)
    m = Q(rng.randint(-12, 12)) if m is None else q(m)
    if a == 0:
        raise ItemError("not a parabola")
    key = (m - b) / (2 * a)
    if key.denominator != 1 or key == 0:
        raise ItemError("the meeting point would not print cleanly")
    stem = displayed(eq("y", poly((c, b, a))),
                     eq("y", join([mono(m, "x"), named])),
                     sent(f"In the given system of equations, {named} is a constant. "
                          f"The graphs of the equations in the given system intersect "
                          f"at exactly one point, (x, y), in the xy-plane. What is "
                          f"the value of x?"))
    root_c = _sqrt_bound(c)
    pool = {
        "negate": Mis("subtracted the two slopes in the wrong order", -key),
        "root_const": Mis("took the square root of the curve's constant term",
                          root_c),
        "neg_root_const": Mis("took the square root of the curve's constant term "
                              "and then changed its sign",
                              -root_c if root_c else None),
        "no_double": Mis("divided by the leading coefficient instead of twice it",
                         (m - b) / a),
        "slope_only": Mis("used the line's slope on its own", m),
    }
    P = {"kind": "nleq_tangent_point", "a": _p(a), "b": _p(b), "c": _p(c),
         "m": _p(m)}
    rationale = sent(f"Setting the two sides equal gives "
                     f"{poly((0, b - m, a))} + ({c} {MINUS} {named}) = 0, which has "
                     f"one solution only at the vertex, x = ({num(m)} {MINUS} "
                     f"({num(b)}))/(2·{num(a)}) = {num(key)}.")
    rationale = sent(f"Whatever {named} is, the line has slope {num(m)}, so the one "
                     f"point it can touch the curve at is where the curve's own "
                     f"slope matches: x = ({num(m)} {MINUS} {_signed(b)})/"
                     f"{_signed(2 * a)} = {num(key)}.")
    keyx = E(key)
    if fmt == "spr":
        return Item("nleq.tangent_point", "a line touching a parabola", difficulty,
                    seed, sent(stem), "spr", keyx, gridin(key), rationale, params=P,
                    spr_mistakes=gridin_pool(keyx, pool.values()))
    ch, tex, why, letter = choices(keyx, pick(pool, wrongs), rng, guard=wrongs is None)
    return Item("nleq.tangent_point", "a line touching a parabola", difficulty, seed,
                sent(stem), "mcq", keyx, letter, rationale, ch, why, tex, params=P)


# ------------------------------------ a constant that leaves integer solutions

NAMES = ["a", "b", "c", "d", "g", "h", "j", "k", "n", "p", "r", "t", "w"]


def integer_roots_constant(rng: random.Random, seed: int, *, k=None, named=None,
                           sign=-1, wrongs=None, difficulty="medium") -> Item:
    """x² − ax + k = 0 has two integer solutions -- what can a be?

    Every factor pair of k gives one value, so the answer is a set and the key
    file carries all of them.
    """
    k = Q(rng.randint(6, 400)) if k is None else q(k)
    named = named or rng.choice(NAMES)
    if k.denominator != 1 or k <= 1:
        raise ItemError("the constant has to be a whole number bigger than one")
    n = int(k)
    sums = sorted({d + n // d for d in range(1, n + 1) if n % d == 0 and d * d <= n})
    if len(sums) < 2:
        raise ItemError("only one factor pair, so the item has a single answer")
    key = sums[0]
    left = join([f"x{sup(2)}", mono(sign, named + "x"), mono(k, "")])
    stem = displayed(eq(left, "0"),
                     sent(f"In the equation above, {named} is a constant and "
                          f"{named} > 0. If the equation has two integer solutions, "
                          f"what is a possible value of {named} ?"))
    P = {"kind": "nleq_integer_roots", "k": _p(k), "sign": int(sign)}
    pairs = [f"{d} and {n // d}" for d in range(1, n + 1)
             if n % d == 0 and d * d <= n]
    shown = ", ".join(pairs[:4]) + (", and so on" if len(pairs) > 4 else "")
    rationale = sent(f"Two integer solutions multiply to {num(k)}, so they are "
                     f"{shown}; {named} is their sum, which can be "
                     f"{', '.join(str(v) for v in sums[:4])}"
                     f"{' and so on' if len(sums) > 4 else ''}.")
    return Item("nleq.integer_roots_constant", "a constant with integer roots",
                difficulty, seed, sent(stem), "spr", E(key), gridin(Q(key)),
                rationale, params=P)


# ------------------------------------------------------------ params packing

def _p(v) -> list:
    v = q(v)
    return [v.numerator, v.denominator]
