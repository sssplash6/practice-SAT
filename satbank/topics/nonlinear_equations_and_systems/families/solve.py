"""Solving one nonlinear equation in one variable.

A square, an absolute value, a quadratic, a radical, a rational equation: the
source asks for one solution, for the positive one, for the sum of them, or for
the set. Two of these shapes -- the radical and the rational -- produce
candidate roots that do not satisfy the printed equation, so every template here
that clears a denominator or squares a side filters its candidates against the
**printed** equation before it keeps one. A template that reported an extraneous
root as the key would still pass the audit, because the audit re-derives from
the same parameters; only substituting back can see it.

`audit.py` re-derives every answer from the parameters by a different route --
the quadratic formula rather than factoring, a numeric sweep rather than
algebra -- and `option_check.py` decides each printed option by substituting it
into the printed equation.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis
from ..kit import (MINUS, PM, ROOT, cap, choices, displayed, eq, gridin,
                   griddable, join, mono, num, paren, pick, poly, q, sent, setof,
                   sup, text_choices)

__all__ = ["square_equation", "absolute_equation", "quadratic_solve",
           "quadratic_formula", "factored_equation", "shared_factor",
           "cancel_squares", "scaled_quadratic", "radical_equation",
           "rational_linear", "rational_quadratic", "rational_combine",
           "product_roots_constant", "paired_quadratics"]


# ------------------------------------------------------------------ helpers

def _isqrt(n: int) -> int:
    return math.isqrt(int(n))


def _exact_root(v) -> Q | None:
    """√v as a Fraction, or None when it is irrational."""
    v = q(v)
    if v < 0:
        return None
    rn, rd = _isqrt(v.numerator), _isqrt(v.denominator)
    return Q(rn, rd) if rn * rn == v.numerator and rd * rd == v.denominator else None


def _roots(a, b, c):
    """The rational roots of ax² + bx + c, ascending; None when irrational."""
    a, b, c = q(a), q(b), q(c)
    if a == 0:
        return None if b == 0 else [-c / b]
    d = b * b - 4 * a * c
    if d < 0:
        return []
    r = _exact_root(d)
    if r is None:
        return None
    return sorted({(-b - r) / (2 * a), (-b + r) / (2 * a)})


ASKS = {
    "one_possible": "What is one possible solution to the given equation?",
    "one_possible_above": "What is one possible solution to the equation above?",
    "positive": "What is the positive solution to the given equation?",
    "negative": "What is the negative solution to the given equation?",
    "sum": "What is the sum of the solutions to the given equation?",
    "product": "What is the product of the solutions to the given equation?",
    "which": "Which of the following is a solution to the given equation?",
    "which_above": "Which of the following is a solution to the equation above?",
    "which_value": "Which of the following values of x satisfies the given equation?",
    "what_value": "What value of x satisfies the equation above?",
    "solutions": "What are the solutions to the given equation?",
    "values": "What values satisfy the equation above?",
    "solution_set": "What is the solution set of the equation above?",
    "solution": "What is the solution to the equation above?",
}


# The asks that any solution answers. "Which of the following is a solution"
# is true of every root, so no root may be offered as a distractor; "the
# positive solution" singles one out, and there the other root is a fair wrong
# answer -- it is what a student who ignored the word `positive` would pick.
ANY_SOLUTION = {"which", "which_above", "which_value", "one_possible",
                "one_possible_above", "what_value", "solution"}


def _strike(pool: dict, values, ask: str, key) -> dict:
    """Remove the other solutions from the pool when they answer the question."""
    if ask not in ANY_SOLUTION:
        return pool
    live = [q(v) for v in values if q(v) != q(key)]
    out = {}
    for name, m in pool.items():
        clash = m.value is not None and any(q(m.value) == v for v in live)
        out[name] = Mis(m.reason, None) if clash else m
    return out


def _value_item(template: str, skill: str, difficulty: str, seed: int, stem: str,
                key, pool: dict, wrongs, rng, rationale: str, params: dict,
                fmt: str, signed: bool = True, sign_rule: bool = True) -> Item:
    """A numeric answer, gridded or offered among four."""
    keyx = E(q(key))
    if fmt == "spr":
        if not griddable(key):
            raise ItemError("that answer could not be entered in the grid")
        return Item(template, skill, difficulty, seed, sent(stem), "spr", keyx,
                    gridin(key), sent(rationale), params=params)
    ch, tex, why, letter = choices(keyx, pick(pool, wrongs), rng, signed=signed,
                                   sign_rule=sign_rule)
    return Item(template, skill, difficulty, seed, sent(stem), "mcq", keyx, letter,
                sent(rationale), ch, why, tex, params=params)


# ------------------------------------------------------------ a bare square

def square_equation(rng: random.Random, seed: int, *, shape=None, a=None, h=None,
                    k=None, spare=None, rhs_style="number", ask=None, fmt=None,
                    wrongs=None, signed=True, sign_rule=True,
                    difficulty="easy") -> Item:
    """a(x + h)² + spare = k -- a square, undone by a square root.

    Both signs come out, which is the whole point: the source asks for the
    positive one, the negative one, their sum, or simply which of four numbers
    works.
    """
    shape = shape or rng.choice(["plain", "plain", "shifted", "shifted",
                                 "gathered"])
    if k is None:
        # a free draw builds the right-hand side from a square root it has
        # chosen, so the page always carries a root the grid can take
        a = Q(rng.choice([1, 1, 1, 2, 3, 4, 5, 9])) if a is None else q(a)
        h = (Q(rng.randint(-9, 9)) if shape == "shifted" else Q(0)) \
            if h is None else q(h)
        root = Q(rng.randint(1, 15))
        if shape == "gathered":
            # (a+1)x² + spare = x² gathers to a·x² = −spare, so the right-hand
            # side is the printed x² and nothing else: k has to be zero here
            spare = -a * root * root if spare is None else q(spare)
            k = Q(0)
        else:
            spare = (Q(rng.randint(-40, 40)) if shape == "plain" else Q(0)) \
                if spare is None else q(spare)
            k = a * root * root + spare
    else:
        # a source item pins the numbers it prints; everything it leaves out
        # takes its neutral value rather than a fresh draw, or the page stops
        # matching the item being reproduced
        a = Q(1) if a is None else q(a)
        h = Q(0) if h is None else q(h)
        spare = Q(0) if spare is None else q(spare)
        k = q(k)
    if a == 0:
        raise ItemError("no square left in the equation")
    if shape == "gathered" and k != 0:
        raise ItemError("a gathered square is printed against x², not a number")
    inner = (k - spare) / a
    if inner <= 0:
        raise ItemError("this square has no real solutions to report")
    root = _exact_root(inner)
    if root is None or root == 0:
        raise ItemError("the square root is not a number the page can print")
    lo, hi = -h - root, -h + root

    var = "x"
    if shape == "plain":
        left = mono(a, var, 2)
        if spare:
            left = join([left, mono(spare, "")])
    elif shape == "shifted":
        left = paren(join([var, mono(h, "")])) + sup(2) if h else var + sup(2)
        if a != 1:
            left = mono(a, "") + left
        if spare:
            left = join([left, mono(spare, "")])
    elif shape == "gathered":
        # 2x² − 4 = x²: the square has to be gathered before it is undone
        left = join([mono(a + 1, var, 2), mono(spare, "")])
    else:
        raise ItemError(f"unknown shape {shape!r}")

    if rhs_style == "product":
        r = _exact_root(k)
        if r is None or r.denominator != 1:
            raise ItemError("that right-hand side cannot be printed as a product")
        right = f"({num(r)})({num(r)})"
    elif rhs_style == "scaled":
        if a == 1 or (k / a).denominator != 1:
            raise ItemError("that right-hand side cannot be printed as a multiple")
        right = f"{num(a)}({num(k / a)})"
    else:
        right = num(k)
    if shape == "gathered":
        right = mono(1, var, 2)
        equation = eq(left, right)
    else:
        equation = eq(left, right)

    ask = ask or rng.choice(["positive", "negative", "one_possible", "sum",
                             "which_value", "which"])
    fmt = fmt or ("mcq" if ask.startswith("which") else "spr")
    stem = displayed(equation, ASKS[ask])
    key = {"positive": max(lo, hi), "negative": min(lo, hi), "sum": lo + hi,
           "one_possible": hi, "which_value": lo, "which": hi}[ask]
    if ask == "positive" and key <= 0:
        raise ItemError("this draw has no positive solution")
    if ask == "negative" and key >= 0:
        raise ItemError("this draw has no negative solution")
    if ask in ("positive", "negative") and lo * hi > 0:
        raise ItemError("both solutions share a sign, so the stem does not pick one")

    pool = {
        "constant": Mis("reported the number the square equals instead of its "
                        "square root", k - spare - h),
        "half_constant": Mis("halved the number the square equals instead of taking "
                             "its square root", (k - spare) / 2 - h),
        "double_constant": Mis("doubled the number the square equals instead of "
                               "taking its square root", 2 * (k - spare) - h),
        "quarter": Mis("divided by the coefficient of the squared term twice over "
                       "instead of taking a square root", inner / 4 - h),
        "half_root": Mis("halved the square root as well as taking it",
                         root / 2 - h),
        "no_root": Mis("never took the square root at all", inner - h),
        "swap_shift": Mis("subtracted the square from the shift instead of the "
                          "other way round", h - inner),
        "other": Mis("reported the other solution", lo if key == hi else hi),
        "abs_other": Mis("lost the sign of the other solution", abs(lo)),
        "sum_shift": Mis("added the two solutions instead of choosing one",
                         lo + hi if ask != "sum" else None),
        "root_only": Mis("took the square root but never undid the shift", root),
    }
    P = {"kind": "nleq_square", "shape": shape, "a": _p(a), "h": _p(h), "k": _p(k),
         "spare": _p(spare), "ask": ask}
    pool = _strike(pool, [lo, hi], ask, key)
    shifted = join(["x", mono(h, "")]) if h else "x"
    rationale = sent(f"The square is {num(inner)}, so {shifted} is {num(root)} or "
                     f"{num(-root)}, giving x = {num(hi)} and x = {num(lo)}.")
    return _value_item("nleq.square_equation", "undoing a square", difficulty, seed,
                       stem, key, pool, wrongs, rng, rationale, P, fmt, signed,
                       sign_rule)


# -------------------------------------------------------- an absolute value

def absolute_equation(rng: random.Random, seed: int, *, a=1, b=0, h=None,
                      reversed_inner=False, bare=False, k=None, ask=None,
                      fmt=None, wrongs=None, difficulty="easy") -> Item:
    """a|x − h| + b|x − h| = k -- two solutions, symmetric about h."""
    a, b = q(a), q(b)
    h = Q(rng.randint(-9, 12)) if h is None else q(h)
    if bare:
        h = Q(0)
    k = Q(rng.choice([5, 8, 9, 10, 12, 15, 20, 24, 25, 30, 45])) if k is None else q(k)
    if a + b == 0:
        raise ItemError("the two absolute-value terms cancel")
    m = k / (a + b)
    if m <= 0:
        raise ItemError("an absolute value cannot be negative")
    lo, hi = h - m, h + m

    inner = ("x" if bare else
             (join([num(h), MINUS + "x"]) if reversed_inner
              else join(["x", mono(-h, "")])))
    bars = f"|{inner}|"
    left = mono(a, "") + bars if a != 1 else bars
    if b:
        left = join([left, (mono(b, "") + bars) if b != 1 else bars])
    equation = eq(left, num(k))

    ask = ask or rng.choice(["one_possible", "positive", "negative", "sum"])
    fmt = fmt or ("mcq" if ask.startswith("which") else "spr")
    stem = displayed(equation, ASKS[ask])
    key = {"one_possible": hi, "positive": max(lo, hi), "negative": min(lo, hi),
           "sum": lo + hi, "which": hi}[ask]
    if ask == "positive" and (key <= 0 or lo * hi > 0):
        raise ItemError("this draw does not have exactly one positive solution")
    if ask == "negative" and (key >= 0 or lo * hi > 0):
        raise ItemError("this draw does not have exactly one negative solution")

    pool = {
        "other": Mis("reported the other solution", lo if key == hi else hi),
        "no_bars": Mis("dropped the bars and solved only the positive case",
                       h + k),
        "no_bars_neg": Mis("dropped the bars and solved only the negative case",
                           h - k),
        "no_divide": Mis("never divided by the total of the two coefficients",
                         h + k if a + b != 1 else None),
        "k_itself": Mis("reported the number on the right of the equation", k),
        "shift_only": Mis("reported the number inside the bars", h),
        "sum_shift": Mis("added the two solutions instead of choosing one",
                         lo + hi if ask != "sum" else None),
        "abs_other": Mis("lost the sign of the other solution", abs(lo)),
    }
    pool = _strike(pool, [lo, hi], ask, key)
    P = {"kind": "nleq_absolute", "a": _p(a), "b": _p(b), "h": _p(h), "k": _p(k),
         "bare": bool(bare), "ask": ask}
    head = (f"Gathering the two terms gives {num(a + b)} times the absolute value, so "
            if b else "")
    rationale = sent(cap(f"{head}the quantity inside the bars is {num(m)} or "
                         f"{num(-m)}, so x = {num(hi)} or x = {num(lo)}."))
    return _value_item("nleq.absolute_equation", "an absolute-value equation",
                       difficulty, seed, stem, key, pool, wrongs, rng, rationale,
                       P, fmt)


# ------------------------------------------------------------- a quadratic

def quadratic_solve(rng: random.Random, seed: int, *, a=None, b=None, c=None,
                    ra=0, rb=0, rc=0, ask=None, fmt=None, frame=None, wrongs=None,
                    difficulty="medium") -> Item:
    """ax² + bx + c = rax² + rbx + rc -- solved by factoring the difference."""
    if a is None:
        a, b, c = _draw_quadratic(rng)
    a, b, c = q(a), q(b), q(c)
    ra, rb, rc = q(ra), q(rb), q(rc)
    na, nb, nc = a - ra, b - rb, c - rc
    if na == 0:
        raise ItemError("the squares cancel, so this is not a quadratic")
    ask = ask or rng.choice(["positive", "negative", "sum", "which", "a_positive"])
    if ask in ("sum",):
        roots = None
        key = -nb / na
    else:
        roots = _roots(na, nb, nc)
        if not roots or len(roots) != 2:
            raise ItemError("this draw does not have two printable solutions")
        lo, hi = roots
        key = {"positive": hi, "negative": lo, "which": hi, "a_positive": hi,
               "product": nc / na, "one_possible": hi}[ask]
        if ask in ("positive", "a_positive") and (key <= 0 or lo * hi > 0):
            raise ItemError("this draw does not have exactly one positive solution")
        if ask == "negative" and (key >= 0 or lo * hi > 0):
            raise ItemError("this draw does not have exactly one negative solution")
    if roots is None and _roots(na, nb, nc) == []:
        raise ItemError("the equation has no real solutions to add up")

    left = poly((c, b, a))
    right = poly((rc, rb, ra))
    equation = eq(left, right)
    frame = frame or ("a_positive" if ask == "a_positive" else ask)
    if frame == "a_positive":
        question = ("If a is a solution of the equation above and a > 0, what is "
                    "the value of a ?")
    else:
        question = ASKS[frame]
    fmt = fmt or ("mcq" if ask == "which" else "spr")
    stem = displayed(equation, question)

    pool = _strike(_quadratic_pool(na, nb, nc, roots, key, ask), roots or [], ask,
                   key)
    P = {"kind": "nleq_quadratic", "a": _p(na), "b": _p(nb), "c": _p(nc),
         "ask": ask}
    if roots:
        rationale = sent(f"The equation gathers to {poly((nc, nb, na))} = 0, whose "
                         f"solutions are x = {num(roots[0])} and x = {num(roots[1])}.")
    else:
        rationale = sent(f"The equation gathers to {poly((nc, nb, na))} = 0, and the "
                         f"two solutions of a quadratic add to minus its middle "
                         f"coefficient over its leading one, which is {num(key)}.")
    return _value_item("nleq.quadratic_solve", "solving a quadratic", difficulty,
                       seed, stem, key, pool, wrongs, rng, rationale, P, fmt)


def _draw_quadratic(rng: random.Random):
    a = Q(rng.choice([1, 1, 1, 2, 3, 4, 5, 6, 7, -1, -2, -4]))
    r1 = Q(rng.choice([i for i in range(-12, 13) if i]))
    r2 = Q(rng.choice([i for i in range(-12, 13) if i and i != r1]),
           rng.choice([1, 1, 1, 2, 3, 4]))
    return a, -a * (r1 + r2), a * r1 * r2


def _quadratic_pool(a, b, c, roots, key, ask) -> dict:
    other = None
    if roots:
        other = roots[0] if key == roots[1] else roots[1]
    pool = {
        "other": Mis("reported the other solution", other),
        "other_abs": Mis("reported the other solution without its sign",
                         abs(other) if other is not None else None),
        "b_over_a": Mis("read the ratio of the first two coefficients as the "
                        "solution", abs(b / a) if a else None),
        "b_itself": Mis("read the coefficient of x as the solution", abs(b)),
        "c_abs": Mis("read the constant term as the answer", abs(c)),
        "c_half": Mis("halved the constant term instead of solving", abs(c) / 2),
        "c_over_a": Mis("read the product of the solutions as the answer", c / a),
        "zero_sum": Mis("assumed the two solutions are opposites, so they cancel",
                        Q(0) if ask == "sum" else None),
        "sum_sign": Mis("kept the sign of the middle coefficient when adding the "
                        "solutions", b / a),
        "sum_instead": Mis("added the two solutions instead of choosing one",
                           roots[0] + roots[1] if roots and ask != "sum" else None),
        "product_instead": Mis("multiplied the two solutions instead of choosing "
                               "one", c / a if ask != "product" else None),
        "negate": Mis("moved the solution across the equals sign without changing "
                      "its sign", -key),
    }
    return pool


# ------------------------------------------- the quadratic formula, surfaced

def quadratic_formula(rng: random.Random, seed: int, *, a=None, b=None, c=None,
                      ra=0, rb=0, rc=0, style="formula", frame="solutions",
                      wrongs=None, difficulty="medium") -> Item:
    """ax² + bx + c = 0, with the quadratic formula itself as the four options.

    `formula` leaves the arithmetic half done, the way the source prints it;
    `pair` writes both solutions out with the radical simplified; `single` offers
    one solution among four look-alikes.
    """
    if a is None:
        a = Q(rng.choice([1, 2, 3, 4, 5, 6, 7, 8]))
        b = Q(rng.choice([i for i in range(-12, 13) if i]))
        c = Q(rng.choice([i for i in range(-12, 13) if i]))
    a, b, c = q(a), q(b), q(c)
    ra, rb, rc = q(ra), q(rb), q(rc)
    na, nb, nc = a - ra, b - rb, c - rc
    if na == 0:
        raise ItemError("not a quadratic")
    disc = nb * nb - 4 * na * nc
    if disc <= 0 or _exact_root(disc) is not None:
        raise ItemError("this draw's solutions are rational, so no radical is printed")
    for v in (na, nb, nc):
        if v.denominator != 1:
            raise ItemError("the formula is printed with whole-number coefficients")

    equation = eq(poly((c, b, a)), poly((rc, rb, ra)))
    stem = displayed(equation, ASKS[frame])
    a, b, c = na, nb, nc

    if style == "formula":
        key = _formula(-b, b * b, -4 * a * c, 2 * a)
        pool = {
            "b_as_a": Mis("used the coefficient of x² where the formula wants the "
                          "coefficient of x", _formula(-a, b * b, -4 * a * c, 2 * a)),
            "disc_sign": Mis("subtracted four times the product of the outer "
                             "coefficients when the formula adds it",
                             _formula(-b, a * a, 4 * a * c, 2 * a)),
            "both": Mis("used the wrong coefficient in front and got the sign of "
                        "the discriminant wrong as well",
                        _formula(-a, a * a, 4 * a * c, 2 * a)),
            "denominator": Mis("divided by the coefficient of x² instead of twice it",
                               _formula(-b, b * b, -4 * a * c, a)),
            "square_lead": Mis("squared the coefficient of x² instead of the "
                               "coefficient of x", _formula(-b, a * a, -4 * a * c,
                                                            2 * a)),
        }
        variables = ()
        check = False
    elif style == "pair":                   # both solutions written out in full
        r = _isqrt(int(disc))
        key = _pair_text(-b, 1, disc, 2 * a)
        upper = (-b + math.sqrt(float(disc))) / float(2 * a)
        bracket = (math.floor(upper), math.floor(upper) + 1)
        pool = {
            "sign_b": Mis("used the coefficient of x with its own sign instead of "
                          "the opposite one", _pair_text(b, 1, disc, 2 * a)),
            "disc_rounded": Mis("rounded the discriminant down to the nearest "
                                "perfect square",
                                _pair_text(-b, 0, Q(r * r), 2 * a) if r * r != disc
                                else None),
            "bracketing_pair": Mis("gave the two whole numbers the larger solution "
                                   "lies between",
                                   f"x = {num(bracket[0])} and x = {num(bracket[1])}"),
            "denominator": Mis("divided by the coefficient of x² instead of twice it",
                               _pair_text(-b, 1, disc, a) if a != 1 else None),
        }
        variables = ()
        check = False
    else:                                   # one solution among four look-alikes
        top, g, m, den = _reduced(-b, disc, 2 * a)
        key = _surd(top, g, m, den)
        pool = {
            "minus_b": Mis("read minus the coefficient of x as a solution by "
                           "itself", num(-b)),
            "no_denominator": Mis("never divided by twice the leading coefficient",
                                  _surd(top, -g, m, 1)),
            "first_over_only": Mis("divided only the first term by twice the "
                                   "leading coefficient",
                                   _surd_split(top, g, m, den) if den != 1 else None),
            "sign_b": Mis("used the coefficient of x with its own sign instead of "
                          "the opposite one", _surd(-top, g, m, den)),
            "whole_root": Mis("treated the discriminant as though its square root "
                              "were a whole number",
                              num(Q(-b + _isqrt(int(disc)), 1) / (2 * a))
                              if (Q(-b + _isqrt(int(disc))) / (2 * a)).denominator == 1
                              else None),
        }
        variables = ()
        check = False
    P = {"kind": "nleq_formula", "a": _p(a), "b": _p(b), "c": _p(c), "style": style}
    rationale = sent(f"With a = {num(a)}, b = {num(b)} and c = {num(c)}, the quadratic "
                     f"formula gives {key}.")
    ch, why, letter = text_choices(key, pick(pool, wrongs), rng, variables=variables,
                                   check=check)
    return Item("nleq.quadratic_formula", "the quadratic formula", difficulty, seed,
                sent(stem), "mcq", E(1), letter, rationale, ch, why, list(ch),
                params=dict(P, options=list(ch)))


def _formula(head, first, second, den) -> str:
    """'(−5 ± √(25 + 168))/12' -- the formula with its arithmetic half done."""
    inside = join([num(first), mono(second, "")])
    return f"({num(head)} {PM} {ROOT}{paren(inside)})/{num(den)}"


def _pair_text(head, keep_radical: int, disc, den) -> str:
    """'x = (1 + √5)/2 and x = (1 − √5)/2', or the same with a whole root.

    A radical pair is printed plus-branch first, the way the source prints it; a
    pair that comes out rational is printed in ascending order, as it also does.
    """
    head, disc, den = q(head), q(disc), q(den)
    if keep_radical:
        body = [f"{num(head)} + {ROOT}{num(disc)}",
                f"{num(head)} {MINUS} {ROOT}{num(disc)}"]
        return " and ".join(f"x = ({b})/{num(den)}" for b in body)
    r = _exact_root(disc)
    if r is None:
        return None
    return " and ".join(f"x = {num(v)}"
                        for v in sorted([(head + r) / den, (head - r) / den]))


def _reduced(head, disc, den):
    """(−b ± √D)/(2a) with the radical pulled out and the fraction cancelled."""
    head, disc, den = q(head), q(disc), q(den)
    g, m = 1, int(disc)
    d = 2
    while d * d <= m:
        while m % (d * d) == 0:
            m //= d * d
            g *= d
        d += 1
    f = math.gcd(math.gcd(abs(int(head)), g), abs(int(den)))
    sign = -1 if den < 0 else 1
    return head / f * sign, Q(g, f) * sign, Q(m), abs(den) / f


def _surd(head, g, m, den) -> str:
    """'(1 + √11)/2', '1 − √11', '√11/2'."""
    head, g, den = q(head), q(g), q(den)
    root = (num(abs(g)) if abs(g) != 1 else "") + ROOT + num(m)
    body = join([num(head), (MINUS if g < 0 else "") + root]) if head else \
        ((MINUS if g < 0 else "") + root)
    return f"({body})/{num(den)}" if den != 1 else body


def _surd_split(head, g, m, den) -> str:
    """'1/2 + √11' -- the denominator applied to the first term only."""
    head, g, den = q(head), q(g), q(den)
    root = (num(abs(g)) if abs(g) != 1 else "") + ROOT + num(m)
    return join([num(head / den), (MINUS if g < 0 else "") + root])


# ------------------------------------------------ a product already factored

def factored_equation(rng: random.Random, seed: int, *, roots=None, ask="product",
                      fmt="mcq", wrongs=None, difficulty="medium") -> Item:
    """(x − r)(x − s)(x − t) = 0 -- the solutions are on the page already."""
    if roots is None:
        n = rng.choice([2, 3, 3])
        roots = rng.sample([i for i in range(-9, 10) if i], n)
    roots = [q(r) for r in roots]
    if len(set(roots)) != len(roots):
        raise ItemError("a repeated factor hides one of the solutions")
    body = "".join(paren(join(["x", mono(-r, "")])) for r in roots)
    equation = eq(body, "0")
    stem = displayed(equation, ASKS[ask])

    total, product = sum(roots), Q(1)
    for r in roots:
        product *= r
    key = {"product": product, "sum": total}[ask]
    pool = {
        "abs_key": Mis("lost the sign that the negative factor contributes",
                       abs(key)),
        "sum_instead": Mis("added the solutions instead of multiplying them",
                           total if ask == "product" else product),
        "neg_sum": Mis("added the solutions and kept the signs printed in the "
                       "brackets", -total if ask == "product" else -product),
        "signs_as_printed": Mis("used the numbers as they appear inside the "
                                "brackets rather than the solutions",
                                _from_printed(roots, ask)),
        "drop_one": Mis("left one of the three factors out",
                        _without_last(roots, ask)),
    }
    P = {"kind": "nleq_factored", "roots": [_p(r) for r in roots], "ask": ask}
    rationale = sent(f"Each bracket gives a solution, so they are "
                     f"{_listed([num(r) for r in roots])}, and their "
                     f"{'product' if ask == 'product' else 'sum'} is {num(key)}.")
    return _value_item("nleq.factored_equation", "a factored equation", difficulty,
                       seed, stem, key, pool, wrongs, rng, rationale, P, fmt)


def _listed(parts) -> str:
    parts = list(parts)
    if len(parts) < 2:
        return "".join(parts)
    return ", ".join(parts[:-1]) + f" and {parts[-1]}"


def _from_printed(roots, ask):
    vals = [-r for r in roots]
    if ask == "sum":
        return sum(vals)
    out = Q(1)
    for v in vals:
        out *= v
    return out


def _without_last(roots, ask):
    if len(roots) < 3:
        return None
    if ask == "sum":
        return sum(roots[:-1])
    out = Q(1)
    for v in roots[:-1]:
        out *= v
    return out


# -------------------------------------------------- a factor on both sides

def shared_factor(rng: random.Random, seed: int, *, a=None, k=None, b=None, m=None,
                  ask="sum", fmt="spr", wrongs=None, difficulty="hard") -> Item:
    """a(x + k) = b(x − m)(x + k) -- the shared bracket is one of the solutions.

    Dividing by the bracket is the mistake the item is built around: it throws
    away the solution x = −k, and the sum then comes out wrong by exactly that.
    """
    a = Q(rng.choice([2, 3, 5, 6, 7, 10, 15])) if a is None else q(a)
    b = Q(rng.choice([3, 5, 6, 9, 12, 15, 20])) if b is None else q(b)
    k = Q(rng.randint(-20, 20)) if k is None else q(k)
    m = Q(rng.randint(-20, 20)) if m is None else q(m)
    if b == 0 or a == 0:
        raise ItemError("a coefficient of zero collapses the equation")
    r1, r2 = -k, m + a / b
    if r1 == r2:
        raise ItemError("the two solutions coincide")
    key = {"sum": r1 + r2, "positive": max(r1, r2), "product": r1 * r2}[ask]
    if ask == "positive" and (key <= 0 or r1 * r2 > 0):
        raise ItemError("this draw does not have exactly one positive solution")

    lhs = f"{num(a)}{paren(join(['x', mono(k, '')]))}"
    rhs = f"{num(b)}{paren(join(['x', mono(-m, '')]))}{paren(join(['x', mono(k, '')]))}"
    stem = displayed(eq(lhs, rhs), ASKS[ask])
    pool = {
        "divided_out": Mis("divided both sides by the shared bracket and lost the "
                           "solution it carries", r2),
        "bracket_only": Mis("kept only the solution the shared bracket gives", r1),
        "printed_signs": Mis("read the numbers inside the brackets as the solutions",
                             k + (-m) if ask == "sum" else k * -m),
        "no_ratio": Mis("forgot to divide the two outer coefficients", r1 + m),
        "negate": Mis("moved the answer across the equals sign without changing its "
                      "sign", -key),
    }
    P = {"kind": "nleq_shared_factor", "a": _p(a), "b": _p(b), "k": _p(k),
         "m": _p(m), "ask": ask}
    rationale = sent(f"Taking everything to one side gives "
                     f"{paren(join(['x', mono(k, '')]))}"
                     f"[{num(a)} {MINUS} {num(b)}"
                     f"{paren(join(['x', mono(-m, '')]))}] = 0, so "
                     f"x = {gridin(r1).replace('-', MINUS)} or "
                     f"x = {gridin(r2).replace('-', MINUS)}.")
    return _value_item("nleq.shared_factor", "a factor on both sides", difficulty,
                       seed, stem, key, pool, wrongs, rng, rationale, P, fmt)


# ------------------------------------------------- the squares cancel out

def cancel_squares(rng: random.Random, seed: int, *, p=None, r=None, k=None,
                   ask="which", fmt="mcq", wrongs=None, difficulty="medium") -> Item:
    """(x + p)(x + r) = (x − p)(x − r) + k -- the x² terms go, leaving a line."""
    p = Q(rng.randint(1, 9)) if p is None else q(p)
    r = Q(rng.randint(1, 9)) if r is None else q(r)
    k = Q(rng.choice([i for i in range(-40, 41) if i])) if k is None else q(k)
    if p + r == 0:
        raise ItemError("the x terms cancel as well, leaving no equation")
    if p == r:
        raise ItemError("the two brackets would print identically")
    key = k / (2 * (p + r))
    if key.denominator > 4:
        raise ItemError("the solution would not print cleanly")

    lhs = paren(join(["x", mono(p, "")])) + paren(join(["x", mono(r, "")]))
    rhs = (paren(join(["x", mono(-p, "")])) + paren(join(["x", mono(-r, "")]))
           + f" + {num(k)}" if k > 0 else
           paren(join(["x", mono(-p, "")])) + paren(join(["x", mono(-r, "")]))
           + f" {MINUS} {num(-k)}")
    stem = displayed(eq(lhs, rhs), ASKS[ask])
    pool = {
        "zero": Mis("cancelled both sides entirely and concluded that x is zero",
                    Q(0)),
        "minus_p": Mis("read the first bracket's number as the solution", -p),
        "minus_r": Mis("read the second bracket's number as the solution", -r),
        "minus_sum": Mis("added the two bracket numbers and changed the sign",
                         -(p + r)),
        "no_double": Mis("forgot that the x terms appear twice over",
                         k / (p + r)),
        "negate": Mis("solved for the wrong sign of x", -key),
    }
    pool = _strike(pool, [key], ask, key)
    P = {"kind": "nleq_cancel_squares", "p": _p(p), "r": _p(r), "k": _p(k)}
    rationale = sent(f"Both sides carry x², and what is left is "
                     f"{num(2 * (p + r))}x = {num(k)}, so x = {num(key)}.")
    return _value_item("nleq.cancel_squares", "an equation whose squares cancel",
                       difficulty, seed, stem, key, pool, wrongs, rng, rationale,
                       P, fmt)


# ------------------------------------- reading a whole expression off at once

def scaled_quadratic(rng: random.Random, seed: int, *, shape="divide", k=None,
                     b=None, c=None, n=None, ask=None, fmt=None, wrongs=None,
                     difficulty="hard") -> Item:
    """The question asks for a combination the equation already contains.

    `divide`: k·x² + k·b·x + c = 0, so x² + bx is −c/k without solving at all.
    `cross`:  n/x = m·x, so m·x² is n -- again without finding x.
    """
    if shape == "divide":
        k = Q(rng.choice([2, 3, 4, 5, 6, 7, 8])) if k is None else q(k)
        b = Q(rng.choice([i for i in range(-9, 10) if i])) if b is None else q(b)
        c = Q(rng.choice([i for i in range(-60, 61) if i])) if c is None else q(c)
        if k == 0:
            raise ItemError("nothing to divide by")
        if (k * b) ** 2 - 4 * k * c < 0:
            raise ItemError("the printed equation has no real solutions, so the "
                            "stem's premise is false")
        key = -c / k
        if key.denominator != 1:
            raise ItemError("the value asked for would not print cleanly")
        equation = eq(poly((c, k * b, k)), "0")
        want = poly((0, b, 1))
        stem = sent(f"If {equation}, what is the value of {want}?")
        pool = {
            "no_divide": Mis("never divided the equation by the common factor", -c),
            "sign": Mis("moved the constant term across without changing its sign",
                        c / k),
            "constant": Mis("read the constant term as the answer", c),
            "coef": Mis("read the common factor as the answer", k),
        }
        P = {"kind": "nleq_scaled", "shape": shape, "k": _p(k), "b": _p(b),
             "c": _p(c)}
        rationale = sent(f"Dividing {equation} by {num(k)} gives "
                         f"{poly((c / k, b, 1))} = 0, so {want} = {num(key)}.")
        ask = ask or "value"
        fmt = fmt or "spr"
    else:
        n = Q(rng.randint(6, 400)) if n is None else q(n)
        k = Q(rng.choice([2, 3, 5, 6, 7, 8, 9, 11])) if k is None else q(k)
        if n <= 0 or k <= 0 or (n / k) <= 0:
            raise ItemError("this draw has no printable solution")
        key = n
        equation = eq(f"{num(n)}/x", mono(k, "x"))
        want = mono(k, "x", 2)
        stem = sent(f"If {equation}, what is the value of {want}?")
        pool = {
            "x_squared": Mis("stopped at the value of x² instead of the multiple of "
                             "it the question asks for", n / k),
            "coef_itself": Mis("reported the coefficient rather than the value of "
                               "the expression", k),
            "product": Mis("multiplied by the coefficient a second time", n * k),
            "half": Mis("halved instead of multiplying", n / 2),
        }
        P = {"kind": "nleq_scaled", "shape": shape, "n": _p(n), "k": _p(k)}
        rationale = sent(f"Multiplying both sides of {equation} by x gives "
                         f"{num(n)} = {want}, so {want} = {num(key)}.")
        ask = ask or "value"
        fmt = fmt or "mcq"
    return _value_item("nleq.scaled_quadratic", "reading a combination off an "
                       "equation", difficulty, seed, stem, key, pool, wrongs, rng,
                       rationale, P, fmt)


# ------------------------------------------------------------- a radical

def radical_equation(rng: random.Random, seed: int, *, shape=None, a=None, b=None,
                     c=None, d=None, e=None, ask=None, fmt=None, wrongs=None,
                     difficulty="medium") -> Item:
    """√(ax + b) = c, or √(ax + b) + d = x + e -- where extraneous roots live.

    Squaring both sides adds roots the printed equation does not have. Every
    candidate is put back into the printed equation here before it is kept; the
    audit cannot see that, because it re-derives from the same parameters.
    """
    # the extraneous-root shape is the whole point of this template, so a free
    # draw reaches it as often as the plain one
    shape = shape or rng.choice(["simple", "linear"])
    a = Q(rng.choice([1, 1, 2, 3, 4])) if a is None else q(a)
    b = Q(rng.randint(-30, 30)) if b is None else q(b)
    d = (Q(rng.randint(0, 6)) if shape == "linear" else Q(0)) if d is None else q(d)
    e = (Q(rng.randint(-6, 6)) if shape == "linear" else Q(0)) if e is None else q(e)
    if a == 0:
        raise ItemError("no unknown under the radical")
    inside = poly((b, a))

    if shape == "simple":
        c = Q(rng.randint(2, 15)) if c is None else q(c)
        if c <= 0:
            raise ItemError("a printed square root is never negative")
        x0 = (c * c - b) / a
        if a * x0 + b < 0:
            raise ItemError("the radicand would be negative")
        equation = eq(f"{ROOT}{paren(inside)}", num(c))
        key = x0
        pool = {
            "no_square": Mis("subtracted the right-hand number instead of squaring "
                             "it", (c - b) / a),
            "halved": Mis("halved the right-hand number instead of squaring it",
                          (c / 2 - b) / a),
            "sign": Mis("added the number inside the radical instead of subtracting "
                        "it", (c * c + b) / a),
            "no_coef": Mis("never divided by the coefficient of x inside the "
                           "radical", c * c - b if a != 1 else None),
            "root_of_c": Mis("took a square root of the right-hand number instead "
                             "of squaring it",
                             (_exact_root(c) - b) / a if _exact_root(c) else None),
        }
        ask = ask or "what_value"
        fmt = fmt or "spr"
        stem = displayed(equation, ASKS[ask])
        P = {"kind": "nleq_radical", "shape": shape, "a": _p(a), "b": _p(b),
             "c": _p(c), "d": _p(0), "e": _p(0), "ask": ask}
        rationale = sent(f"Squaring both sides gives {inside} = {num(c * c)}, so "
                         f"x = {gridin(key).replace('-', MINUS)}.")
        return _value_item("nleq.radical_equation", "a radical equation", difficulty,
                           seed, stem, key, pool, wrongs, rng, rationale, P, fmt)

    # √(ax + b) + d = x + e
    shift = e - d
    # (x + shift)² = ax + b
    cand = _roots(1, 2 * shift - a, shift * shift - b)
    if cand is None or len(cand) != 2:
        raise ItemError("this draw does not square down to two printable candidates")
    good = [x for x in cand if _radical_holds(a, b, d, e, x)]
    bad = [x for x in cand if x not in good]
    if len(good) != 1 or not bad:
        raise ItemError("this draw is not an extraneous-root item")
    key = good[0]
    # A solution set is printed the way the source prints one, in braces -- and
    # `check._prose` reads a brace as an unrendered placeholder, which it has to,
    # since that is what a half-rendered template looks like. So the braced
    # surface is offered only where a source item asks for it by name; a free
    # draw takes the same mathematics as a grid-in, and the extraneous root is
    # tested either way.
    ask = ask or "what_value"
    equation = eq(join([f"{ROOT}{paren(inside)}", mono(d, "")]),
                  join(["x", mono(e, "")]))
    stem = displayed(equation, ASKS[ask])
    P = {"kind": "nleq_radical", "shape": shape, "a": _p(a), "b": _p(b),
         "c": [0, 1], "d": _p(d), "e": _p(e), "ask": ask}
    rationale = sent(f"Squaring gives {poly((shift * shift - b, 2 * shift - a, 1))}"
                     f" = 0, whose roots are "
                     f"{num(cand[0])} and {num(cand[1])}; only x = {num(key)} "
                     f"satisfies the printed equation, because a square root is "
                     f"never negative.")
    if ask == "what_value":
        pool = {
            "extraneous": Mis("kept the root that squaring introduced", bad[0]),
            "sum": Mis("added the two candidates instead of testing them",
                       cand[0] + cand[1]),
            "product": Mis("multiplied the two candidates instead of testing them",
                           cand[0] * cand[1]),
        }
        return _value_item("nleq.radical_equation", "a radical equation", difficulty,
                           seed, stem, key, pool, wrongs, rng, rationale, P, "spr")
    key_text = setof([num(key)])
    pool = {
        "extraneous_only": Mis("kept only the root that squaring introduced and "
                               "discarded the one that works", setof([num(bad[0])])),
        "both": Mis("never put the two roots back into the printed equation, so the "
                    "extraneous one stayed", setof([num(v) for v in cand])),
        "both_and_zero": Mis("kept both roots and added x = 0 as well",
                             setof(["0"] + [num(v) for v in cand]) if 0 not in cand
                             else None),
        "empty": Mis("rejected both roots as extraneous", setof([])),
    }
    ch, why, letter = text_choices(key_text, pick(pool, wrongs), rng, check=False)
    return Item("nleq.radical_equation", "a radical equation", difficulty, seed,
                sent(stem), "mcq", E(1), letter, sent(rationale), ch, why, list(ch),
                params=dict(P, options=list(ch)))


def _radical_holds(a, b, d, e, x) -> bool:
    """Does x satisfy the equation as printed, radical sign and all?"""
    inside = q(a) * q(x) + q(b)
    if inside < 0:
        return False
    r = _exact_root(inside)
    if r is None:
        r = Q(str(math.sqrt(float(inside))))
    return abs(float(r + q(d)) - float(q(x) + q(e))) < 1e-9


# ------------------------------------------------------ rational equations

def rational_linear(rng: random.Random, seed: int, *, p=None, a=None, b=None,
                    r=1, m=None, ask="solution", fmt="mcq", wrongs=None,
                    difficulty="medium") -> Item:
    """p(x + a)/(x + b) = r − m/(x + b) -- one denominator, cleared once."""
    p = Q(rng.choice([2, 3, 4, 5])) if p is None else q(p)
    a = Q(rng.randint(-9, 9)) if a is None else q(a)
    b = Q(rng.choice([i for i in range(-9, 10) if i])) if b is None else q(b)
    r, m = q(r), Q(rng.randint(1, 9)) if m is None else q(m)
    if p == r:
        raise ItemError("the x terms cancel, so there is nothing to solve")
    key = (r * b - m - p * a) / (p - r)
    if key + b == 0:
        raise ItemError("the only candidate makes a denominator zero")
    if key.denominator > 4:
        raise ItemError("the solution would not print cleanly")

    den = join(["x", mono(b, "")])
    lhs = f"{num(p)}{paren(join(['x', mono(a, '')]))}/{paren(den)}"
    rhs = join([num(r), mono(-m, "")]) if m > 0 else join([num(r), mono(-m, "")])
    rhs = f"{num(r)} {MINUS} {num(m)}/{paren(den)}" if m > 0 else \
          f"{num(r)} + {num(-m)}/{paren(den)}"
    stem = displayed(eq(lhs, rhs), ASKS[ask])
    pool = {
        "drop_bracket": Mis("multiplied only the first term by the denominator",
                            (r * b - m - a) / (p - r) if p != r else None),
        "sign_m": Mis("added the second fraction instead of subtracting it",
                      (r * b + m - p * a) / (p - r)),
        "excluded": Mis("gave the value that makes the denominator zero", -b),
        "denominator_number": Mis("read the number in the denominator as the "
                                  "solution", abs(b)),
        "zero": Mis("cancelled the two fractions against each other and concluded "
                    "that x is zero", Q(0)),
        "drop_r": Mis("left the whole number on the right out of the working",
                      (-m - p * a) / p if p else None),
        "negate": Mis("solved for the wrong sign of x", -key),
    }
    P = {"kind": "nleq_rational_linear", "p": _p(p), "a": _p(a), "b": _p(b),
         "r": _p(r), "m": _p(m)}
    rationale = sent(f"Multiplying through by {den} gives "
                     f"{poly((p * a, p))} = {poly((r * b - m, r))}, so x = {num(key)}.")
    return _value_item("nleq.rational_linear", "a rational equation", difficulty,
                       seed, stem, key, pool, wrongs, rng, rationale, P, fmt)


def rational_quadratic(rng: random.Random, seed: int, *, shape="cross", n=None,
                       b=None, h=None, k=None, ask=None, fmt=None, wrongs=None,
                       difficulty="medium") -> Item:
    """n/(x + b) = x, or 1/(x + h)² = k -- clearing leaves a quadratic.

    Both shapes can produce a candidate the printed equation rejects, so the
    candidates are tested against the printed equation, not against the
    quadratic that squaring or cross-multiplying produced.
    """
    if shape == "cross":
        b = Q(rng.randint(-12, 12)) if b is None else q(b)
        n = Q(rng.randint(2, 300)) if n is None else q(n)
        roots = _roots(1, b, -n)
        if roots is None or len(roots) != 2:
            raise ItemError("this draw does not cross-multiply to printable roots")
        live = [x for x in roots if x + b != 0]
        if len(live) != 2:
            raise ItemError("one candidate makes the denominator zero")
        lo, hi = live
        ask = ask or rng.choice(["positive", "negative"])
        key = hi if ask == "positive" else lo
        if ask == "positive" and (key <= 0 or lo * hi > 0):
            raise ItemError("this draw does not have exactly one positive solution")
        if ask == "negative" and (key >= 0 or lo * hi > 0):
            raise ItemError("this draw does not have exactly one negative solution")
        equation = eq(f"{num(n)}/{paren(join(['x', mono(b, '')]))}", "x")
        stem = displayed(equation, ASKS[ask])
        pool = {
            "other": Mis("reported the other solution", lo if key == hi else hi),
            "numerator": Mis("read the numerator as the solution", n),
            "excluded": Mis("gave the value that makes the denominator zero", -b),
            "no_shift": Mis("ignored the shift in the denominator and took a square "
                            "root", _exact_root(n)),
            "sum": Mis("added the two solutions instead of choosing one", lo + hi),
        }
        P = {"kind": "nleq_rational_quadratic", "shape": shape, "n": _p(n),
             "b": _p(b), "ask": ask}
        rationale = sent(f"Multiplying by {join(['x', mono(b, '')])} gives "
                         f"{poly((-n, b, 1))} = 0, so x = {num(lo)} or x = {num(hi)}.")
        return _value_item("nleq.rational_quadratic", "a rational equation",
                           difficulty, seed, stem, key, pool, wrongs, rng,
                           rationale, P, fmt or "spr")

    # 1/(x + h)² = k, and the question asks for x + h
    h = Q(rng.randint(1, 12)) if h is None else q(h)
    k = Q(rng.choice([4, 9, 16, 25, 36, 49, 100])) if k is None else q(k)
    if k <= 0:
        raise ItemError("a square cannot be negative")
    r = _exact_root(1 / k)
    if r is None or r == 0:
        raise ItemError("the value asked for would not print cleanly")
    equation = eq(f"1/{paren(poly((h * h, 2 * h, 1)))}", num(k))
    ask = "possible_shift"
    stem = displayed(equation, sent(f"If x is a solution to the given equation, which "
                                    f"of the following is a possible value of "
                                    f"{join(['x', mono(h, '')])} ?"))
    key = r
    pool = {
        "no_root": Mis("never took the square root of the reciprocal", 1 / k),
        "k_itself": Mis("read the right-hand number as the answer", k),
        "root_k": Mis("took the square root of the right-hand number instead of its "
                      "reciprocal", _exact_root(k)),
        "shift_added": Mis("added the shift to the answer a second time", r + h),
        "shift_minus": Mis("subtracted the answer from the shift instead of "
                           "reporting it", h - r),
        "half_shift": Mis("halved the shift instead of taking the square root of "
                          "the reciprocal", h / 2),
        "double": Mis("doubled the square root instead of halving the reciprocal",
                      2 * r),
        "half": Mis("halved the answer once more", r / 2),
    }
    P = {"kind": "nleq_rational_quadratic", "shape": shape, "h": _p(h), "k": _p(k),
         "ask": ask}
    rationale = sent(f"Taking reciprocals gives {paren(join(['x', mono(h, '')]))}"
                     f"{sup(2)} = {num(1 / k)}, so {join(['x', mono(h, '')])} is "
                     f"{num(r)} or {num(-r)}.")
    return _value_item("nleq.rational_quadratic", "a rational equation", difficulty,
                       seed, stem, key, pool, wrongs, rng, rationale, P,
                       fmt or "mcq")


def rational_combine(rng: random.Random, seed: int, *, A=None, B=None, C=None,
                     h=None, ask="what_value", fmt="mcq", wrongs=None,
                     difficulty="hard") -> Item:
    """Ax²/(x² − h²) − Bx/(x + h) = C/(x − h) -- three denominators, one common.

    Multiplying by (x + h)(x − h) leaves a quadratic whose roots include x = −h,
    which the printed equation forbids. That root is the item.
    """
    h = Q(rng.randint(2, 14)) if h is None else q(h)
    A = Q(rng.randint(2, 14)) if A is None else q(A)
    B = Q(rng.randint(1, 12)) if B is None else q(B)
    C = Q(rng.randint(1, 14)) if C is None else q(C)
    if h <= 0:
        raise ItemError("the two denominators would coincide")
    # A x² − B x (x − h) = C (x + h)
    a2, a1, a0 = A - B, B * h - C, -C * h
    if a2 == 0:
        raise ItemError("the squares cancel, so this is not the intended item")
    roots = _roots(a2, a1, a0)
    if roots is None or len(roots) != 2:
        raise ItemError("this draw does not clear to two printable roots")
    live = [x for x in roots if x != h and x != -h]
    if len(live) != 1:
        raise ItemError("this draw is not an excluded-value item")
    key = live[0]
    dead = [x for x in roots if x not in live]
    equation = (f"{mono(A, 'x', 2)}/{paren(poly((-h * h, 0, 1)))} {MINUS} "
                f"{mono(B, 'x')}/{paren(join(['x', mono(h, '')]))} = "
                f"{num(C)}/{paren(join(['x', mono(-h, '')]))}")
    stem = displayed(equation, ASKS[ask])
    pool = {
        "excluded": Mis("kept the root that makes a denominator zero", dead[0]),
        "other_excluded": Mis("gave the other value the denominators forbid",
                              h if dead[0] == -h else -h),
        "sign": Mis("added the second fraction instead of subtracting it",
                    _other_root(A + B, -B * h - C, -C * h, h)),
        "no_common": Mis("cleared only one of the two denominators", C / (A - B)),
        "negate": Mis("solved for the wrong sign of x", -key),
    }
    P = {"kind": "nleq_rational_combine", "A": _p(A), "B": _p(B), "C": _p(C),
         "h": _p(h)}
    rationale = sent(f"The first denominator is {poly((-h * h, 0, 1))}, so "
                     f"multiplying through by it leaves {poly((a0, a1, a2))} = 0, "
                     f"whose roots are {num(roots[0])} and {num(roots[1])}; "
                     f"x = {num(dead[0])} makes a denominator zero, so the solution "
                     f"is x = {num(key)}.")
    return _value_item("nleq.rational_combine", "a rational equation", difficulty,
                       seed, stem, key, pool, wrongs, rng, rationale, P, fmt)


def _other_root(a, b, c, h):
    rs = _roots(a, b, c)
    if not rs:
        return None
    live = [x for x in rs if abs(x) != abs(h)]
    return live[0] if live else None


# -------------------------------------- a product of factors with a constant

def product_roots_constant(rng: random.Random, seed: int, *, p=None, u=None, v=None,
                           g=None, w=None, s=None, t=6, ask="p", fmt="spr",
                           wrongs=None, difficulty="hard") -> Item:
    """(ux + p)(vx² − g)(wx² − sx + tp) = 0, with the sum of the roots given.

    Every factor but the first contributes a sum that does not depend on p -- the
    middle one contributes a pair that cancels, the last one s/w -- so the stated
    total fixes p outright, provided the five roots stay distinct.
    """
    p = Q(rng.randint(1, 24)) if p is None else q(p)
    u = Q(rng.choice([2, 3, 4, 5, 6, 7])) if u is None else q(u)
    v = Q(rng.choice([2, 3, 5, 6, 7, 10, 11])) if v is None else q(v)
    w = Q(rng.choice([1, 2, 3, 4, 5])) if w is None else q(w)
    if g is None:
        # the middle factor has to come apart, so build it from its own root
        g = v * Q(rng.randint(2, 12)) ** 2
    g = q(g)
    s = Q(rng.choice([6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 24])) \
        if s is None else q(s)
    t = q(t)
    if p <= 0 or u == 0 or v == 0 or w == 0 or t == 0:
        raise ItemError("a coefficient of zero collapses a factor")
    sq = _exact_root(g / v)
    if sq is None or sq == 0:
        raise ItemError("the middle factor has no printable roots")
    last = _roots(w, -s, t * p)
    if last is None or len(last) != 2:
        raise ItemError("the last factor has no two printable roots")
    roots = sorted({-p / u, sq, -sq, last[0], last[1]})
    if len(roots) != 5:
        raise ItemError("two factors share a root, so the sum would double-count")
    total = sum(roots)

    f1 = paren(join([mono(u, "x"), "p"]))
    f2 = paren(join([mono(v, "x", 2), mono(-g, "")]))
    f3 = paren(join([mono(w, "x", 2), mono(-s, "x"), mono(t, "p")]))
    stem = displayed(eq(f1 + f2 + f3, "0"),
                     sent(f"In the given equation, p is a positive constant. The sum "
                          f"of the solutions to the equation is {num(total)}. What "
                          f"is the value of p?"))
    key = p
    pool = {
        "sum_itself": Mis("reported the stated total instead of the constant", total),
        "no_lead": Mis("forgot that the first factor's root carries a coefficient",
                       s / w - total),
        "sign": Mis("kept the sign of the first factor's root", -p),
        "times_lead": Mis("multiplied by the first coefficient instead of dividing",
                          p * u * u),
        "last_sum": Mis("reported what the last factor contributes to the total",
                        s / w),
    }
    P = {"kind": "nleq_product_constant", "p": _p(p), "u": _p(u), "v": _p(v),
         "w": _p(w), "g": _p(g), "s": _p(s), "t": _p(t)}
    rationale = sent(f"The middle factor contributes {num(sq)} and {num(-sq)}, which "
                     f"cancel, and the last contributes {num(s / w)}; the first "
                     f"contributes {MINUS}p/{num(u)}, so {num(s / w)} {MINUS} "
                     f"p/{num(u)} = {num(total)} and p = {num(p)}.")
    return _value_item("nleq.product_roots_constant", "a product of factors",
                       difficulty, seed, stem, key, pool, wrongs, rng, rationale,
                       P, fmt)


# ------------------------------------------ two quadratics feeding a third

def paired_quadratics(rng: random.Random, seed: int, *, b1=None, c1=None, b2=None,
                      c2=None, fmt="spr", wrongs=None, difficulty="hard") -> Item:
    """x² + b₁x + c₁ and x² + b₂x + c₂; the sums of their roots make a third.

    The smaller root of one plus the smaller of the other, and likewise the
    larger pair, are the roots of x² + (b₁ + b₂)x + c. The middle coefficient
    comes out for free; the constant is the item.
    """
    if b1 is None:
        t = rng.choice([2, 3, 5, 6, 7, 8, 10])
        m, n = rng.randint(1, 4), rng.randint(1, 4)
        b1, c1 = 2 * rng.randint(2, 9), None
        d1, d2 = t * m * m, t * n * n
        b1 = rng.randint(2, 12) * 2
        if b1 * b1 <= d1:
            raise ItemError("that discriminant is too big for the draw")
        c1 = Q(b1 * b1 - d1, 4)
        b2 = rng.randint(2, 12) * 2
        if b2 * b2 <= d2:
            raise ItemError("that discriminant is too big for the draw")
        c2 = Q(b2 * b2 - d2, 4)
    b1, c1, b2, c2 = q(b1), q(c1), q(b2), q(c2)
    d1, d2 = b1 * b1 - 4 * c1, b2 * b2 - 4 * c2
    if d1 <= 0 or d2 <= 0:
        raise ItemError("one of the two quadratics has no real solutions")
    if _exact_root(d1) is not None or _exact_root(d2) is not None:
        raise ItemError("the source's item turns on the roots being irrational")
    cross = _exact_root(d1 * d2)
    if cross is None:
        raise ItemError("the two discriminants do not multiply to a square")
    if c1.denominator != 1 or c2.denominator != 1:
        raise ItemError("the coefficients are printed as whole numbers")
    # (r + t)(s + u) with r,s from the first and t,u from the second
    key = ((b1 + b2) ** 2 - (d1 + d2 + 2 * cross)) / 4
    if key.denominator != 1:
        raise ItemError("the constant would not print cleanly")

    q1, q2 = poly((c1, b1, 1)), poly((c2, b2, 1))
    q3 = join([poly((0, b1 + b2, 1)), "c"])
    stem = sent(f"The solutions to {q1} = 0 are r and s, where r < s. The solutions "
                f"to {q2} = 0 are t and u, where t < u. The solutions to {q3} = 0, "
                f"where c is a constant, are r + t and s + u. What is the value of c?")
    pool = {
        "sum_instead": Mis("added the two constants instead of multiplying the two "
                           "sums", c1 + c2),
        "product": Mis("multiplied the two constant terms", c1 * c2),
        "no_cross": Mis("left the product of the two discriminants out of the "
                        "working", ((b1 + b2) ** 2 - (d1 + d2)) / 4),
        "middle": Mis("reported the middle coefficient instead of the constant",
                      b1 + b2),
    }
    P = {"kind": "nleq_paired", "b1": _p(b1), "c1": _p(c1), "b2": _p(b2),
         "c2": _p(c2)}
    rationale = sent(f"The two sums add to {num(-(b1 + b2))}, which matches the "
                     f"middle coefficient, and their product is "
                     f"[{num(b1 + b2)}² {MINUS} ({num(d1)} + {num(d2)} + "
                     f"2·{num(cross)})]/4 = {num(key)}.")
    return _value_item("nleq.paired_quadratics", "two quadratics feeding a third",
                       difficulty, seed, stem, key, pool, wrongs, rng, rationale,
                       P, fmt)


# ------------------------------------------------------------ params packing

def _p(v) -> list:
    v = q(v)
    return [v.numerator, v.denominator]
