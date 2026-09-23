"""What the constants do to the solution set.

Two lines meet once, never, or everywhere, and the source asks about that six
ways: supply the constant that makes the two equations the same line, supply the
one that makes them parallel, pick the system that is empty, pick the equation
that would empty it, count the crossings, and -- when the two equations are one
line -- describe every point on it.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text
from ..kit import (MINUS, choices, coef, displayed, griddable, gridin_pool, num,
                   opt_dec, opt_pair, pick, q, sent, side, solved, std)

__all__ = ["infinite_constant", "infinite_normalized", "no_solution_slope",
           "no_solution_gathered", "pick_no_solution", "other_equation",
           "count_intersections", "unknown_coefficient", "all_solutions"]

CONSTS = ["a", "b", "c", "k", "p", "r", "t", "w"]


# ------------------------------- the constant that makes it one line twice

def infinite_constant(rng: random.Random, seed: int, *, a=None, b=None, c=None,
                      k=None, letter=None, fmt=None, wrongs=None) -> Item:
    """a·x + b·y = c and k·a·x + k·b·y = L; L is pinned by the scaling."""
    letter = letter or rng.choice(CONSTS)
    a = Q(int(a) if a is not None else rng.choice([i for i in range(-9, 13) if i]))
    b = Q(int(b) if b is not None else rng.choice([i for i in range(-9, 13) if i]))
    c = Q(int(c) if c is not None else rng.choice([i for i in range(-20, 40) if i]))
    k = Q(int(k) if k is not None else rng.choice([2, 3, 4, 5, 6, -2, -3]))
    if abs(k) == 1:
        raise ItemError("a scaling of one prints the same equation twice")
    key = k * c
    eq1 = std(a, b, c)
    eq2 = f"{side(k * a, k * b)} = {letter}"
    stem = displayed(eq1, eq2,
                     sent(f"In the given system of equations, {letter} is a constant. "
                          f"If the system has infinitely many solutions, what is the "
                          f"value of {letter} ?"))
    pool = {
        "constant": Mis("read the constant from the first equation and never scaled "
                        "it", c),
        "multiplier": Mis("reported the multiplier rather than multiplying the "
                          "constant by it", k),
        "diff_mult": Mis("found the multiplier by subtracting the two coefficients of "
                         "x instead of dividing them", (k * a - a) * c),
        "sum_coef": Mis("added the second equation's two coefficients instead of "
                        "scaling the constant", k * a + k * b),
        "over": Mis("divided the constant by the multiplier instead of multiplying",
                    c / k),
        "negate": Mis("moved the constant across the equals sign without changing its "
                      "sign", -key),
        "neg_constant": Mis("never scaled the constant and changed its sign on the "
                            "way across the equals sign", -c),
    }
    P = {"kind": "sys_infinite_constant", "a": _p(a), "b": _p(b), "c": _p(c),
         "k": _p(k)}
    rationale = sent(f"Every term of the second equation is {num(k)} times the "
                     f"matching term of the first, so the right-hand side has to be "
                     f"{num(k)} times {num(c)} as well.")
    keyx = E(key)
    fmt = fmt or ("spr" if rng.random() < 0.3 else "mcq")
    if fmt == "spr":
        if not griddable(key):
            raise ItemError("this answer could not be entered in the grid")
        return Item("sys.infinite_constant", "infinitely many solutions", "easy", seed,
                    stem, "spr", keyx, keyx.gridin(), rationale, params=P,
                    spr_mistakes=gridin_pool(keyx, pool))
    ch, tex, why, letter_ = choices(keyx, pick(pool, wrongs), rng)
    return Item("sys.infinite_constant", "infinitely many solutions", "easy", seed,
                stem, "mcq", keyx, letter_, rationale, ch, why, tex, params=P)


# ---------------------- the constant after the equation has been normalized

def infinite_normalized(rng: random.Random, seed: int, *, shape=None, p=None, r=None,
                        s=None, m=None, b=None, letter=None, other=None, ask=None,
                        fmt=None, value_style=None, wrongs=None) -> Item:
    """The second equation is written in a fixed shape; scaling pins one constant."""
    shape = shape or rng.choice(["scaled_standard", "slope_intercept"])
    if shape == "scaled_standard":
        letter = letter or rng.choice(CONSTS)
        other = other or rng.choice([l for l in CONSTS if l != letter])
        p = q(p) if p is not None else Q(rng.choice([i for i in range(-9, 10) if i]),
                                         rng.choice([1, 2, 3, 4]))
        r = q(r) if r is not None else Q(rng.choice([i for i in range(-9, 10) if i]),
                                         rng.choice([1, 2, 3]))
        s = q(s) if s is not None else Q(rng.choice([i for i in range(-9, 10) if i]),
                                         rng.choice([1, 2, 3, 6]))
        if r == 0 or p == 0:
            raise ItemError("a missing term leaves nothing to scale")
        key = p / r
        eq1 = std(p, r, s)
        eq2 = f"{letter}x + y = {other}"
        stem = displayed(sent(f"In the system of equations below, {letter} and "
                              f"{other} are constants."),
                         eq1, eq2,
                         sent(f"If the system of equations has an infinite number of "
                              f"solutions (x, y), what is the value of {letter} ?"))
        pool = {
            "raw": Mis("read the coefficient of x straight off the first equation "
                       "without scaling it to match", p),
            "neg_raw": Mis("read the coefficient of x off the first equation and "
                           "changed its sign on the way across", -p),
            "ratio_flip": Mis("divided the coefficient of x by the coefficient of y "
                              "the wrong way round", r / p),
            "scaled_const": Mis("scaled the constant instead of the coefficient of x",
                                s / r),
            "negate": Mis("scaled correctly but changed the sign", -key),
            "doubled": Mis("scaled the first equation by twice the factor that turns "
                           "its y-term into y, and read the coefficient of x off "
                           "that", 2 * key),
            "const_over_x": Mis("divided the constant by the coefficient of x instead "
                                "of dividing the coefficient of x by the coefficient "
                                "of y", s / p),
            "neg_scaled_const": Mis("scaled the constant instead of the coefficient of "
                                    "x, and changed its sign on the way across",
                                    -s / r),
        }
        rationale = sent(f"Multiplying {eq1} by {num(1 / r)} makes its y-term y, and "
                         f"the x-term becomes {coef(key, 'x')}, so {letter} = "
                         f"{num(key)}.")
        P = {"kind": "sys_infinite_normalized", "shape": shape, "p": _p(p),
             "r": _p(r), "s": _p(s), "m": _p(0), "b": _p(0), "ask": "a"}
    else:
        ask = ask or rng.choice(["b", "m"])
        m = q(m) if m is not None else Q(rng.choice([i for i in range(-9, 10) if i]),
                                         rng.choice([1, 2, 3, 5, 7]))
        b = q(b) if b is not None else Q(rng.choice([i for i in range(-9, 10) if i]))
        if b == 0 or m == 0:
            raise ItemError("a zero constant makes the reciprocal options collapse")
        key = b if ask == "b" else m
        eq1 = solved(1, "y", m, "x", b)
        stem = displayed(eq1,
                         sent("One of the two equations in a system of linear "
                              "equations is given. The system has infinitely many "
                              "solutions. If the second equation in the system is "
                              "y = mx + b, where m and b are constants, what is the "
                              f"value of {ask}?"))
        named = "constant term" if ask == "b" else "coefficient of x"
        pool = {
            "neg": Mis(f"changed the sign of the {named} when matching the two "
                       "equations", -key),
            "recip": Mis(f"turned the {named} upside down instead of copying it",
                         1 / key),
            "neg_recip": Mis(f"turned the {named} upside down and changed its sign",
                             -1 / key),
            "other": Mis("copied the other number from the given equation",
                         m if ask == "b" else b),
            "clear_denominator": Mis("cleared the fraction by multiplying through and "
                                     "then read the constant off the cleared equation",
                                     key * (m.denominator if ask == "b"
                                            else m.numerator)),
            "doubled": Mis(f"doubled the given equation to build the second one and "
                           f"read the {named} off it, without dividing by the "
                           f"doubled coefficient of y", 2 * key),
        }
        rationale = sent(f"Two equations have every solution in common only when they "
                         f"are the same line, so y = mx + b has to be {eq1}, giving "
                         f"{ask} = {num(key)}.")
        P = {"kind": "sys_infinite_normalized", "shape": shape, "p": _p(0),
             "r": _p(1), "s": _p(0), "m": _p(m), "b": _p(b), "ask": ask}

    keyx = E(key)
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    if fmt == "spr":
        if not griddable(key):
            raise ItemError("this answer could not be entered in the grid")
        return Item("sys.infinite_normalized", "infinitely many solutions", "medium",
                    seed, stem, "spr", keyx, keyx.gridin(), rationale, params=P,
                    spr_mistakes=gridin_pool(keyx, pool))
    fmt_value = opt_dec if value_style == "dec" else None
    ch, tex, why, ltr = choices(keyx, pick(pool, wrongs), rng, fmt_value=fmt_value)
    return Item("sys.infinite_normalized", "infinitely many solutions", "medium", seed,
                stem, "mcq", keyx, ltr, rationale, ch, why, tex, params=P)


# ------------------------------ the constant that makes the two lines parallel

def no_solution_slope(rng: random.Random, seed: int, *, m=None, b1=None, b2=None,
                      letter=None, fmt=None, value_style=None, wrongs=None) -> Item:
    """y = m·x + b₁ and y = L·x + b₂ with b₁ ≠ b₂: the system is empty when L = m."""
    letter = letter or rng.choice(CONSTS)
    m = q(m) if m is not None else Q(rng.choice([i for i in range(-9, 10) if i]),
                                     rng.choice([1, 1, 2, 3, 4]))
    b1 = q(b1) if b1 is not None else Q(rng.randint(-15, 15))
    b2 = q(b2) if b2 is not None else Q(rng.randint(-15, 15))
    if b1 == b2:
        raise ItemError("equal constants make the two equations one line")
    if m == 0:
        raise ItemError("a horizontal line leaves nothing for the constant to match")
    key = m
    eq1 = solved(1, "y", m, "x", b1)
    if b2 == 0:
        eq2 = f"y = {letter}x"
    else:
        eq2 = f"y = {letter}x + {num(b2)}" if b2 > 0 else \
              f"y = {letter}x {MINUS} {num(-b2)}"
    stem = displayed(eq1, eq2,
                     sent(f"In the system of equations above, {letter} is a constant. "
                          f"If the system has no solution, what is the value of "
                          f"{letter} ?"))
    pool = {
        "neg_recip": Mis("used the perpendicular slope instead of the equal one",
                         -1 / m),
        "zero": Mis("took the constant to be 0, as if a horizontal line could never "
                    "meet the given line", 0),
        "half": Mis("halved the coefficient of x instead of matching it", m / 2),
        "recip": Mis("turned the coefficient of x upside down instead of copying it",
                     1 / m),
        "neg": Mis("copied the coefficient of x but changed its sign", -m),
        "const": Mis("matched the constant terms instead of the coefficients of x",
                     b2),
        "doubled": Mis("doubled the coefficient of x instead of matching it", 2 * m),
    }
    P = {"kind": "sys_no_solution_slope", "m": _p(m), "b1": _p(b1), "b2": _p(b2)}
    rationale = sent(f"Two lines miss each other only when they rise at the same rate "
                     f"but start apart, and {num(b1)} is not {num(b2)}, so {letter} "
                     f"must equal {num(m)}.")
    keyx = E(key)
    fmt = fmt or ("spr" if rng.random() < 0.35 else "mcq")
    if fmt == "spr":
        if not griddable(key):
            raise ItemError("this answer could not be entered in the grid")
        return Item("sys.no_solution_slope", "no solution", "hard", seed, stem, "spr",
                    keyx, keyx.gridin(), rationale, params=P,
                    spr_mistakes=gridin_pool(keyx, pool))
    fmt_value = opt_dec if value_style == "dec" else None
    ch, tex, why, ltr = choices(keyx, pick(pool, wrongs), rng, fmt_value=fmt_value)
    return Item("sys.no_solution_slope", "no solution", "hard", seed, stem, "mcq",
                keyx, ltr, rationale, ch, why, tex, params=P)


# ----------------------- the same question with the terms scattered about

def no_solution_gathered(rng: random.Random, seed: int, *, shape=None, alpha=None,
                         beta=None, delta=None, phi=None, eta=None, split=None,
                         glue=None, letter=None) -> Item:
    """Both equations have terms on both sides; gather first, then match."""
    shape = shape or rng.choice(["x_first", "y_first"])
    letter = letter or rng.choice(CONSTS)
    den = [1, 2, 3, 4]
    alpha = q(alpha) if alpha is not None else Q(rng.choice([i for i in range(-9, 10)
                                                             if i]), rng.choice(den))
    beta = q(beta) if beta is not None else Q(rng.choice([i for i in range(-9, 10)
                                                          if i]), rng.choice([1, 2]))
    delta = q(delta) if delta is not None else Q(rng.choice([i for i in range(-9, 10)
                                                             if i]), rng.choice(den))
    phi = q(phi) if phi is not None else Q(rng.choice([i for i in range(-9, 10) if i]),
                                           rng.choice([1, 2]))
    eta = q(eta) if eta is not None else Q(rng.choice([i for i in range(-9, 10)]),
                                           rng.choice(den))
    if alpha == 0 or beta == 0 or phi == 0:
        raise ItemError("a missing term leaves nothing to match")
    if eta == delta * phi / alpha:
        raise ItemError("with these numbers the system has infinitely many solutions")

    ratio = beta * phi / alpha
    if shape == "x_first":
        # α·x + Bl·y = C·y + δ  and  L·y = H + F·x
        split = q(split) if split is not None else Q(rng.choice([i for i in range(-9, 10)
                                                                 if i]))
        Bl, C = split, split - beta
        F, H = -phi, eta
        if C == 0 or Bl == 0:
            raise ItemError("the y-terms must appear on both sides")
        eq1 = f"{side(alpha, Bl)} = {_join_const(coef(C, 'y'), delta)}"
        eq2 = f"{letter}y = {_join_rev(H, coef(F, 'x'))}"
        key = ratio
    else:
        # (β/2)y + α·x = δ − (β/2)y  and  F·x + G = L·y + H
        half = beta / 2
        glue = q(glue) if glue is not None else Q(rng.choice([i for i in range(-9, 10)
                                                              if i]), rng.choice(den))
        F, G, H = phi, glue, eta + glue
        eq1 = f"{_join_const(coef(half, 'y'), 0, tail=coef(alpha, 'x'))} = " \
              f"{_join_const(num(delta), 0, tail=coef(-half, 'y'))}"
        eq2 = f"{_join_const(coef(F, 'x'), G)} = {_join_const(f'{letter}y', H)}"
        key = -ratio
    if key == 0:
        raise ItemError("a constant of zero deletes the unknown from the equation")
    stem = displayed(eq1, eq2,
                     sent(f"In the given system of equations, {letter} is a constant. "
                          f"If the system has no solution, what is the value of "
                          f"{letter}?"))
    if not griddable(key):
        raise ItemError("this answer could not be entered in the grid")
    P = {"kind": "sys_no_solution_gathered", "shape": shape, "alpha": _p(alpha),
         "beta": _p(beta), "delta": _p(delta), "phi": _p(phi), "eta": _p(eta)}
    keyx = E(key)
    rationale = sent(f"Collecting the y-terms turns the first equation into "
                     f"{std(alpha, beta, delta)}; the second has an x-term of "
                     f"{coef(phi, 'x')}, and the two are parallel only when the "
                     f"y-terms are in the same ratio, which needs {letter} = "
                     f"{_shown(keyx)}.")
    return Item("sys.no_solution_gathered", "no solution after gathering", "hard",
                seed, stem, "spr", keyx, keyx.gridin(), rationale, params=P)


def _join_const(head: str, c, first: bool = False, tail: str = "") -> str:
    parts = [head]
    if tail:
        parts.append(tail)
    if q(c) != 0 or (not tail and len(parts) == 1 and first):
        parts.append(num(c))
    out = parts[0]
    for p in parts[1:]:
        out += f" {MINUS} {p[1:]}" if p.startswith(MINUS) else f" + {p}"
    return out


def _join_rev(c, term: str) -> str:
    """The constant printed first, as 'ty = 1/2 + 2x' does."""
    head = num(c)
    return head + (f" {MINUS} {term[1:]}" if term.startswith(MINUS) else f" + {term}")


# --------------------------------------- which of four systems is the odd one

PAIRS = [("x", "y"), ("s", "t"), ("a", "b"), ("m", "n"), ("p", "q"), ("u", "v"),
         ("w", "z"), ("c", "d"), ("f", "g"), ("h", "k"), ("r", "s"), ("j", "k"),
         ("x", "z"), ("y", "z"), ("b", "c"), ("n", "p"), ("t", "w"), ("d", "f"),
         ("g", "h"), ("m", "p"), ("q", "r"), ("u", "w"), ("v", "y"), ("c", "k")]

SET_WORDS = {"none": "no solution", "many": "infinitely many solutions"}

# a distractor that is itself one line written twice cannot be offered against a
# stem asking for infinitely many solutions -- it would be a second key
ONE_LINE = {"same_line", "same_line_neg", "same_multiple"}


def pick_no_solution(rng: random.Random, seed: int, *, style=None, outcome=None,
                     pair=None, phrasing=None, a=None, b=None, c=None, k=None,
                     d=None, given=None, wrongs=None) -> Item:
    """Four systems; only one has the solution set the sentence names."""
    style = style or rng.choice(["slope_intercept", "standard"])
    outcome = outcome or rng.choice(["none", "none", "many"])
    phrasing = phrasing or rng.choice(["of_the_following", "which_system"])
    vx, vy = pair or PAIRS[rng.randrange(len(PAIRS))]
    if vx == vy:
        raise ItemError("a system needs two different unknowns")
    given = given or {}
    rnd = lambda lo, hi: rng.choice([i for i in range(lo, hi) if i])     # noqa: E731

    if style == "slope_intercept":
        m = Q(int(a) if a is not None else rnd(-9, 10))
        b = Q(int(b) if b is not None else rng.randint(-12, 12))
        d = Q(int(d) if d is not None else rng.randint(-12, 12))
        if b == d:
            raise ItemError("equal constants make the two lines one line")
        empty = opt_pair(solved(1, vy, m, vx, b), solved(1, vy, m, vx, d))
        same = opt_pair(solved(1, vy, m, vx, b), solved(2, vy, 2 * m, vx, 2 * b))
        pool = _pick_pool_lines(rng, given, m, b, d, vx, vy)
        nums = {"m": _p(m), "b": _p(b), "c": _p(0), "k": _p(2), "d": _p(d)}
    else:
        a = Q(int(a) if a is not None else rnd(-9, 10))
        b = Q(int(b) if b is not None else rnd(-9, 10))
        c = Q(int(c) if c is not None else rng.randint(-20, 20))
        k = Q(int(k) if k is not None else rng.choice([2, 3, -2, -3]))
        d = Q(int(d) if d is not None else k * c + rng.choice([-9, -6, 6, 9, 18]))
        if d == k * c:
            raise ItemError("the second equation is the first one again")
        empty = opt_pair(std(a, b, c, vx, vy), std(k * a, k * b, d, vx, vy))
        same = opt_pair(std(a, b, c, vx, vy), std(k * a, k * b, k * c, vx, vy))
        pool = _pick_pool_std(rng, given, a, b, c, k, d, vx, vy)
        nums = {"m": _p(a), "b": _p(b), "c": _p(c), "k": _p(k), "d": _p(d)}

    if outcome == "none":
        key = empty
        pool["same_multiple"] = Mis("the second equation is the first one multiplied "
                                    "through, so the two are one line and every point "
                                    "on it solves both", same)
    else:
        key = same
        pool = {"empty": Mis("the two equations describe parallel lines, so no pair "
                             f"of values for {vx} and {vy} satisfies both", empty),
                **{kk: vv for kk, vv in pool.items() if kk not in ONE_LINE}}
    named = "" if (vx, vy) == ("x", "y") else f" in {vx} and {vy}"
    head = ("Which of the following systems of linear equations"
            if phrasing == "of_the_following" else "Which system of linear equations")
    stem = sent(f"{head}{named} has {SET_WORDS[outcome]}?")
    P = {"kind": "sys_pick_none", "style": style, "outcome": outcome, "vx": vx,
         "vy": vy, **nums}
    rationale = sent(
        "Two lines with the same rate of change but different starting values run "
        "alongside each other forever, so that is the empty system."
        if outcome == "none" else
        "Multiplying every term of one equation by the same number gives the same "
        "line again, so every point on it satisfies both equations.")
    ch, why, letter = assemble_text(key, pick(pool, wrongs), rng)
    return Item("sys.pick_no_solution", "spotting an empty system", "medium", seed,
                stem, "mcq", E(1), letter, rationale, ch, why, ch, params=P)


def _pick_pool_lines(rng, given, m, b, d, vx, vy) -> dict:
    g = lambda name, n: given.get(name) or [rng.randint(2, 15) for _ in range(n)]  # noqa: E731
    h1, h2, h3 = g("horizontal_slanted", 3)
    s1, s2, s3 = g("different_slopes", 3)
    v1, v2 = g("vertical_horizontal", 2)
    return {
        "horizontal_slanted": Mis("a horizontal line always meets a slanted line, so "
                                  "that system has exactly one solution",
                                  opt_pair(std(0, 1, h1, vx, vy),
                                           solved(1, vy, h2, vx, h3))),
        "different_slopes": Mis(f"the two coefficients of {vx} differ, so those lines "
                                "cross exactly once",
                                opt_pair(solved(1, vy, s1, vx, s3),
                                         solved(1, vy, s2, vx, s3))
                                if s1 != s2 else None),
        "vertical_horizontal": Mis("a vertical line and a horizontal line always "
                                   "cross, so that system has exactly one solution",
                                   opt_pair(std(1, 0, v1, vx, vy),
                                            std(0, 1, v2, vx, vy))),
        "same_line": Mis("the second equation is the first one multiplied through, so "
                         "every point on the line solves both",
                         opt_pair(solved(1, vy, m, vx, b),
                                  solved(2, vy, 2 * m, vx, 2 * b))),
    }


def _pick_pool_std(rng, given, a, b, c, k, d, vx, vy) -> dict:
    same = given.get("same_line_neg") or [int(a), int(b), int(c)]
    cross = given.get("crossing_standard") or [int(-a), int(-b), int(-c),
                                               int(b) or 1, int(a) or 1,
                                               rng.randint(-15, 15)]
    mult = given.get("same_line") or [int(a), int(b), int(c), -3]
    return {
        "swapped_coefs": Mis(f"the second equation has the {vx}- and {vy}-coefficients "
                             "swapped, which changes the slope, so those lines cross "
                             "exactly once",
                             opt_pair(std(a, b, c, vx, vy), std(b, a, c, vx, vy))
                             if a * a != b * b else None),
        "scaled_left_only": Mis(f"only the {vx}-term and the right-hand side were "
                                "scaled, which changes the slope, so those lines "
                                "cross exactly once",
                                opt_pair(std(a, b, c, vx, vy),
                                         std(k * a, b, k * c, vx, vy))
                                if k * b != b else None),
        "same_line_neg": Mis("the second equation is the first one multiplied by "
                             "\u22121, so the two are the same line and every point on it "
                             "solves both",
                             opt_pair(std(same[0], same[1], same[2], vx, vy),
                                      std(-same[0], -same[1], -same[2], vx, vy))),
        "crossing_standard": Mis("the coefficients of those two equations are not "
                                 "proportional, so the lines cross exactly once",
                                 opt_pair(std(cross[0], cross[1], cross[2], vx, vy),
                                          std(cross[3], cross[4], cross[5], vx, vy))
                                 if cross[0] * cross[4] != cross[1] * cross[3]
                                 else None),
        "same_line": Mis("the second equation is a multiple of the first, so the two "
                         "are the same line and every point on it solves both",
                         opt_pair(std(mult[0], mult[1], mult[2], vx, vy),
                                  std(mult[3] * mult[0], mult[3] * mult[1],
                                      mult[3] * mult[2], vx, vy))),
    }


# ------------------------------------- which equation would empty the system

def other_equation(rng: random.Random, seed: int, *, a=None, b=None, c=None, g=None,
                   d=None, wrongs=None) -> Item:
    """One equation is given; choose a second that leaves the system with nothing."""
    g = int(g) if g is not None else rng.choice([2, 2, 3, 4, 5])
    a = Q(int(a) if a is not None else g * rng.choice([i for i in range(1, 7) if i]))
    b = Q(int(b) if b is not None else g * rng.choice([i for i in range(1, 7) if i]))
    c = Q(int(c) if c is not None else g * rng.randint(1, 12))
    if a % g or b % g or c % g:
        raise ItemError("the stated factor does not divide every term")
    if a == b:
        raise ItemError("equal coefficients make the swapped option identical")
    d = Q(int(d) if d is not None else c / g + rng.choice([-25, -20, -15, 15, 20, 25]))
    if d == c / g:
        raise ItemError("that second equation is the given line itself")
    given = std(a, b, c)
    key = std(a / g, b / g, d)
    stem = sent(f"One of the two equations in a linear system is {given}. The system "
                f"has no solution. Which of the following could be the other equation "
                f"in the system?")
    pool = {
        "same_line": Mis("this is the given equation divided through by "
                         f"{g}, so the two are the same line and every point on it "
                         "solves both", std(a / g, b / g, c / g)),
        "swapped_signs": Mis("swapping the coefficients and changing a sign changes "
                             "the rate of change, so these lines still cross once",
                             std(b, -a, 0)),
        "swapped_coefs": Mis("swapping the two coefficients changes the rate of "
                             "change, so these lines still cross once", std(b, a, c)),
        "scaled_both": Mis("multiplying every term, the right-hand side included, "
                           "leaves the same line rather than a parallel one",
                           std(2 * a, 2 * b, 2 * c)),
    }
    P = {"kind": "sys_other_equation", "a": _p(a), "b": _p(b), "c": _p(c), "g": g,
         "d": _p(d)}
    rationale = sent(f"Dividing {given} by {g} gives {std(a / g, b / g, c / g)}, so an "
                     f"equation with the same left side and a different right side "
                     f"describes a parallel line and the system is empty.")
    ch, why, letter = assemble_text(key, pick(pool, wrongs), rng)
    return Item("sys.other_equation", "an equation that empties the system", "hard",
                seed, stem, "mcq", E(1), letter, rationale, ch, why, ch, params=P)


# ----------------------------------------------- how many points do they share

def count_intersections(rng: random.Random, seed: int, *, m1=None, b1=None, m2=None,
                        b2=None, wrongs=None) -> Item:
    """Two lines named in the sentence; how many points do their graphs share?"""
    m1 = Q(int(m1) if m1 is not None else rng.choice([i for i in range(-9, 10) if i]))
    b1 = Q(int(b1) if b1 is not None else rng.randint(-25, 25))
    m2 = Q(int(m2) if m2 is not None else rng.choice([i for i in range(-9, 10) if i]))
    b2 = Q(int(b2) if b2 is not None else rng.randint(-25, 25))
    if m1 == m2 and b1 == b2:
        raise ItemError("one line written twice has no countable answer")
    key = Q(1) if m1 != m2 else Q(0)
    e1, e2 = solved(1, "y", m1, "x", b1), solved(1, "y", m2, "x", b2)
    stem = sent(f"At how many points do the graphs of the equations {e1} and {e2} "
                f"intersect in the xy-plane?")
    pool = {
        "zero": Mis("read the different constant terms as a sign that the lines are "
                    "parallel", 0),
        "two": Mis("counted one crossing for each equation", 2),
        "slope": Mis("read a coefficient of x as the number of crossings",
                     abs(m2) if abs(m2) not in (0, 1, 2) else abs(m1)),
        "one": Mis("saw the equal coefficients of x and still expected one crossing",
                   1),
        "sum": Mis("added the two coefficients of x instead of comparing them",
                   abs(m1) + abs(m2)),
    }
    P = {"kind": "sys_count_points", "m1": _p(m1), "b1": _p(b1), "m2": _p(m2),
         "b2": _p(b2)}
    rationale = sent(f"The two lines rise at {num(m1)} and {num(m2)} per unit, so they "
                     + ("are parallel and never meet." if m1 == m2 else
                        "are not parallel and cross at exactly one point."))
    keyx = E(key)
    ch, tex, why, letter = choices(keyx, pick(pool, wrongs), rng)
    return Item("sys.count_intersections", "counting the solutions", "medium", seed,
                stem, "mcq", keyx, letter, rationale, ch, why, tex, params=P)


# ------------------------------- a constant inside a coefficient, one coordinate given

def unknown_coefficient(rng: random.Random, seed: int, *, shape=None, p1=None,
                        p2=None, c1=None, c2=None, k=None, x0=None, y0=None,
                        letter=None, other=None, fmt=None, wrongs=None) -> Item:
    """The unknown sits in a coefficient; one coordinate of the crossing is given."""
    shape = shape or rng.choice(["pair_ab", "shared_y"])
    letter = letter or rng.choice(CONSTS)
    other = other or rng.choice([l for l in CONSTS if l != letter])
    if shape == "pair_ab":
        p2 = Q(int(p2) if p2 is not None else rng.choice([i for i in range(2, 15)]))
        k = Q(int(k) if k is not None else rng.choice([2, 3, 4, -2]))
        c1 = Q(int(c1) if c1 is not None else rng.randint(20, 120))
        c2 = Q(int(c2) if c2 is not None else rng.randint(20, 120))
        x0 = Q(int(x0) if x0 is not None else rng.choice([i for i in range(2, 12)]))
        if abs(k) == 1:
            raise ItemError("without a scaling the second equation says nothing new")
        by = (c2 - p2 * x0) / k               # what b·y has to be
        key = (c1 - by) / x0
        if by.denominator != 1 or key.denominator != 1 or key == 0:
            raise ItemError("the constant would not come out a whole number")
        eq1 = f"{letter}x + {other}y = {num(c1)}"
        eq2 = f"{_join([side(p2, 0), coef(k, other) + 'y'])} = {num(c2)}"
        stem = displayed(eq1, eq2,
                         sent(f"In the given system of equations, {letter} and "
                              f"{other} are constants. The graphs of these equations "
                              f"in the xy-plane intersect at the point "
                              f"({num(x0)}, y). What is the value of {letter}?"))
        pool = {
            "coef2": Mis("read the coefficient of x from the second equation", p2),
            "given_x": Mis("reported the x-coordinate of the intersection point", x0),
            "half_coef2": Mis("scaled the second equation's coefficient of x the way "
                              f"{other} is scaled instead of solving", p2 / k),
            "const_over": Mis("divided the first equation's right-hand value by the "
                              "given x-coordinate and stopped", c1 / x0),
            "diff": Mis("subtracted the two right-hand values instead of eliminating "
                        f"{other}y", c1 - c2),
        }
        P = {"kind": "sys_unknown_coef", "shape": shape, "p1": _p(1), "p2": _p(p2),
             "c1": _p(c1), "c2": _p(c2), "k": _p(k), "x0": _p(x0), "y0": _p(0)}
        rationale = sent(f"The second equation at x = {num(x0)} gives "
                         f"{coef(k, other)}y = {num(c2 - p2 * x0)}, so {other}y = "
                         f"{num(by)}; putting that into the first gives "
                         f"{coef(x0, letter)} = {num(c1 - by)}, and so {letter} = "
                         f"{num(key)}.")
    else:
        p1 = Q(int(p1) if p1 is not None else rng.choice([i for i in range(-6, 7) if i]))
        p2 = Q(int(p2) if p2 is not None else rng.choice([i for i in range(-6, 7) if i]))
        if p1 == p2:
            raise ItemError("the x-terms must differ for subtraction to find x")
        k = Q(int(k) if k is not None else rng.choice([1, -1]))
        y0 = Q(int(y0) if y0 is not None else rng.choice([i for i in range(2, 30) if i]))
        c1 = Q(int(c1) if c1 is not None else rng.randint(-400, 400))
        c2 = Q(int(c2) if c2 is not None else rng.randint(-400, 400))
        x0 = (c2 - c1) / (p2 - p1)
        key = (c1 - p1 * x0) / (k * y0)
        if key == 0 or q(x0).denominator != 1 or q(key).denominator != 1:
            raise ItemError("the crossing point is not a whole number of units along")
        eq1 = f"{_join([side(p1, 0), coef(k, letter) + 'y'])} = {num(c1)}"
        eq2 = f"{_join([side(p2, 0), coef(k, letter) + 'y'])} = {num(c2)}"
        stem = displayed(eq1, eq2,
                         sent(f"In the given system of equations, {letter} is a "
                              f"constant. In the xy-plane, the graphs of these "
                              f"equations intersect at the point (q, {num(y0)}), "
                              f"where q is a constant. What is the value of "
                              f"{letter}?"))
        pool = {
            "given_y": Mis("reported the y-coordinate of the intersection point", y0),
            "x_value": Mis("reported the x-coordinate the subtraction produces", x0),
            "diff": Mis("subtracted the two right-hand values and stopped",
                        c1 - c2),
            "no_divide": Mis("stopped before dividing by the given y-coordinate",
                             key * y0),
        }
        P = {"kind": "sys_unknown_coef", "shape": shape, "p1": _p(p1), "p2": _p(p2),
             "c1": _p(c1), "c2": _p(c2), "k": _p(k), "x0": _p(0), "y0": _p(y0)}
        step = std(p2 - p1, 0, c2 - c1)
        rationale = sent(f"Subtracting the two equations removes the y-term and gives "
                         + (f"{step}; putting that " if p2 - p1 in (1, -1)
                            else f"{step}, so x = {num(x0)}; putting that ")
                         + f"and y = {num(y0)} back gives {letter} = {num(key)}.")

    keyx = E(key)
    fmt = fmt or ("spr" if rng.random() < 0.35 else "mcq")
    if fmt == "spr":
        if not griddable(key):
            raise ItemError("this answer could not be entered in the grid")
        return Item("sys.unknown_coefficient", "a constant inside a coefficient",
                    "hard", seed, stem, "spr", keyx, keyx.gridin(), rationale,
                    params=P, spr_mistakes=gridin_pool(keyx, pool))
    ch, tex, why, ltr = choices(keyx, pick(pool, wrongs), rng)
    return Item("sys.unknown_coefficient", "a constant inside a coefficient", "hard",
                seed, stem, "mcq", keyx, ltr, rationale, ch, why, tex, params=P)


# --------------------------------- the two equations are one line: every point

def all_solutions(rng: random.Random, seed: int, *, a=None, b=None, c=None, k=None,
                  var="r", wrongs=None) -> Item:
    """a·x + b·y = c printed twice over; describe every point the two share."""
    a = Q(int(a) if a is not None else rng.choice([i for i in range(2, 13)]))
    b = Q(int(b) if b is not None else rng.choice([i for i in range(2, 13)]))
    c = Q(int(c) if c is not None else rng.choice([i for i in range(2, 30)]))
    k = Q(int(k) if k is not None else rng.choice([2, 3, 4, 5]))
    if a == b or b == 1:
        raise ItemError("the printed fractions would collapse into whole numbers")
    if a % b == 0 or c % b == 0:
        raise ItemError("the coordinate would not print as a fraction")
    eq1, eq2 = std(a, b, c), std(k * a, k * b, k * c)
    stem = displayed(eq1, eq2,
                     sent(f"For each real number {var}, which of the following points "
                          f"lies on the graph of each equation in the xy-plane for "
                          f"the given system?"))
    key = f"({var}, {_ratio(-a, b, var)} + {num(c / b)})"
    pool = {
        "swapped": Mis("wrote the two coordinates in the wrong order",
                       f"({_ratio(-a, b, var)} + {num(c / b)}, {var})"),
        "raw_constants": Mis("divided only the x-term by the coefficient of y and "
                             "took the two right-hand values as printed",
                             f"({_ratio(-a, b, var)} + {num(c)}, "
                             f"{_ratio(a, b, var)} + {num(k * c)})"),
        "by_factor": Mis("divided by the factor relating the two equations instead of "
                         "by the coefficient of y",
                         f"({_ratio(1, k, var)} + {num(c)}, "
                         f"{_ratio(-1, k, var)} + {num(k * c)})"),
        "no_divide": Mis("never divided by the coefficient of y at all",
                         f"({var}, {_ratio(-a, 1, var)} + {num(c)})"),
    }
    P = {"kind": "sys_all_points", "a": _p(a), "b": _p(b), "c": _p(c), "k": _p(k),
         "var": var}
    rationale = sent(f"The second equation is {num(k)} times the first, so the two "
                     f"describe one line; solving {eq1} for y gives y = "
                     f"{_ratio(-a, b, 'x')} + {num(c / b)}.")
    ch, why, letter = assemble_text(key, pick(pool, wrongs), rng)
    return Item("sys.all_solutions", "every point of a repeated line", "hard", seed,
                stem, "mcq", E(1), letter, rationale, ch, why, ch, params=P)


def _ratio(n, d, var: str) -> str:
    """The source prints this coefficient as one fraction: −8r/7, r/3, −r/3."""
    f = Q(int(n), int(d)) if not isinstance(n, Q) else q(n) / q(d)
    sign = MINUS if f < 0 else ""
    top = abs(f.numerator)
    head = var if top == 1 else f"{top}{var}"
    return f"{sign}{head}" if f.denominator == 1 else f"{sign}{head}/{f.denominator}"


def _shown(keyx) -> str:
    """The answer spelled the way the grid-in takes it: 5.25, not 21/4."""
    return keyx.gridin().replace("-", MINUS)


def _join(parts: list) -> str:
    out = parts[0]
    for p in parts[1:]:
        out += f" {MINUS} {p[1:]}" if p.startswith(MINUS) else f" + {p}"
    return out


def _p(v) -> list:
    v = q(v)
    return [v.numerator, v.denominator]
