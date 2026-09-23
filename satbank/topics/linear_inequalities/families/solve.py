"""Solving, rather than writing, an inequality -- and the sign rule that makes
this topic different from the linear-equation topics.

Dividing both sides by a negative number reverses the relation. A student who
solves the equation correctly and forgets that gets the boundary right and the
direction wrong, so the wrong option here is the key's mirror image and no
amount of arithmetic checking finds it. That mistake is modelled explicitly in
every template in this file, and the rationale says why the sign turned over
whenever it did.
"""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, ItemError, Mis, gridin_mistakes
from .kit import (FLIP, MINUS, Q, STRICT, band, dec, griddable, mixed, num,
                  rel, sent, side, term, text_choices)

__all__ = ["solve_linear", "greatest_value", "y_range_from_system",
           "range_solve", "triangle_third_side", "allowable_dimension"]

SOLVE_SHAPES = ["gathered", "both_sides", "bracket"]
SOLVE_FRAMES = [
    "{q}\nWhich of the following describes all the possible values of {v} ?",
    "{q}\nWhich inequality represents all the values of {v} that satisfy the "
    "given inequality?",
    "{q}\nWhich of the following is equivalent to the given inequality?",
]
SOLVE_VARS = ["x", "n", "t", "w", "p", "m", "k", "c"]


def solve_linear(rng: random.Random, seed: int, *, shape=None, var=None, op=None,
                 a=None, b=None, c=None, d=None, x0=None, frame=None) -> Item:
    """A displayed linear inequality in one variable, solved for that variable.

    The coefficient the student ends up dividing by is negative about half the
    time, which is the only way the sign rule gets exercised.
    """
    shape = shape or rng.choice(SOLVE_SHAPES)
    var = var or rng.choice(SOLVE_VARS)
    op = op or rng.choice(["<", "<=", ">", ">="])
    frame = rng.randrange(len(SOLVE_FRAMES)) if frame is None else frame
    x0 = Q(rng.choice([i for i in range(-12, 13) if i]) if x0 is None else x0)
    if x0 == 0:
        raise ItemError("a boundary of zero makes two distractors the same option")

    if shape == "gathered":                       # a*v + b ⋈ c
        a = Q(rng.choice([i for i in range(-9, 10) if abs(i) > 1]) if a is None else a)
        b = Q(rng.randint(-20, 20) if b is None else b)
        c = a * x0 + b
        lhs, rhs = side([(a, var)], b), num(c)
        A = a
    elif shape == "both_sides":                   # a*v + b ⋈ c*v + d
        a = Q(rng.randint(-9, 9) if a is None else a)
        c = Q(rng.randint(-9, 9) if c is None else c)
        b = Q(rng.randint(-20, 20) if b is None else b)
        if a == c:
            raise ItemError("the variable cancels, so there is nothing to solve")
        d = (a - c) * x0 + b
        lhs, rhs = side([(a, var)], b), side([(c, var)], d)
        A = a - c
    else:                                         # a(v + b) ⋈ c*v + d
        a = Q(rng.choice([i for i in range(-8, 9) if abs(i) > 1]) if a is None else a)
        b = Q(rng.randint(-12, 12) if b is None else b)
        c = Q(rng.randint(-6, 6) if c is None else c)
        if a == c:
            raise ItemError("the variable cancels, so there is nothing to solve")
        d = (a - c) * x0 + a * b
        inner = side([(1, var)], b)
        lhs = f"({inner})" if a == 1 else (f"{MINUS}({inner})" if a == -1
                                          else f"{num(a)}({inner})")
        rhs = side([(c, var)], d)
        A = a - c

    if abs(A) == 1 and shape == "gathered":
        raise ItemError("dividing by 1 asks nothing about the sign rule")
    flipped = A < 0
    key_op = FLIP[op] if flipped else op
    question = rel(lhs, op, rhs)
    stem = sent(SOLVE_FRAMES[frame].format(q=question, v=var))
    key = rel(var, key_op, num(x0))

    wrong = [
        Mis("did not reverse the inequality when dividing both sides by a "
            "negative number" if flipped else
            "reversed the inequality although both sides were divided by a "
            "positive number",
            rel(var, op if flipped else FLIP[op], num(x0))),
        Mis("changed the sign of the boundary value when moving the constant "
            "across", rel(var, key_op, num(-x0))),
        Mis("changed the sign of the boundary value and did not reverse the "
            "inequality" if flipped else
            "changed the sign of the boundary value and reversed the "
            "inequality", rel(var, op if flipped else FLIP[op], num(-x0))),
        Mis("included the boundary value, which a strict inequality leaves out"
            if key_op in STRICT else
            "left the boundary value out, although the inequality includes it",
            rel(var, _loosen(key_op), num(x0))),
        Mis("divided the constant by the coefficient the wrong way round",
            rel(var, key_op, num(Q(1) / x0)) if x0 != 0 else None),
    ]
    P = {"kind": "ineq_solve_linear", "shape": shape, "op": op, "var": var,
         "a": float(a), "b": float(b), "c": float(c),
         "d": float(d) if shape != "gathered" else 0.0}
    why_flip = (f"dividing both sides by {num(A)}, a negative number, reverses "
                f"the relation, so it turns over and " if flipped else
                f"dividing both sides by {num(A)}, a positive number, leaves "
                f"the relation pointing the same way, so ")
    rationale = (f"Gathering {question} leaves {term(A, var)} on one side and "
                 f"{num(A * x0)} on the other; {why_flip}{key}.")
    ch, wh, letter = text_choices(key, [m for m in wrong if m.value], rng)
    return Item("ineq.solve_linear", "solving a linear inequality", "medium",
                seed, stem, "mcq", E(0), letter, rationale, ch, wh, list(ch),
                params=P)


def _loosen(op: str) -> str:
    return {"<": "<=", ">": ">=", "<=": "<", ">=": ">"}[op]


# ------------------------------------------------- the extreme allowed value

PHRASES = {"less": ("less than", -1), "more": ("more than", 1)}


def greatest_value(rng: random.Random, seed: int, *, m=None, k=None, y=None,
                   op=None, phrase=None, u="x", v="y", fmt="spr") -> Item:
    """'x is at most k less than m times y' -- the largest x the bound allows."""
    m = Q(rng.randint(2, 9) if m is None else m)
    k = Q(rng.randint(1, 15) if k is None else k)
    y = Q(rng.choice([i for i in range(-12, 13) if i]) if y is None else y)
    op = op or rng.choice(["<=", ">="])
    phrase = phrase or rng.choice(list(PHRASES))
    word, sgn = PHRASES[phrase]
    key = m * y + sgn * k
    if key == 0:
        raise ItemError("a zero answer makes the sign of the bound invisible")
    if m == k:
        raise ItemError("the same number twice reads as a typo in the stem")
    if not griddable(key):
        raise ItemError("this answer would not be enterable in a grid-in")
    want = "greatest" if op == "<=" else "least"
    stem = sent(f"A number {u} is at most {num(k)} {word} {num(m)} times the "
                f"value of {v}. If the value of {v} is {num(y)}, what is the "
                f"{want} possible value of {u}?"
                if op == "<=" else
                f"A number {u} is at least {num(k)} {word} {num(m)} times the "
                f"value of {v}. If the value of {v} is {num(y)}, what is the "
                f"{want} possible value of {u}?")
    P = {"kind": "ineq_greatest_value", "m": float(m), "k": float(k),
         "y": float(y), "op": op, "sign": sgn}
    rationale = (f"The condition is {rel(u, op, side([(m, v)], sgn * k))}, and "
                 f"with {v} = {num(y)} the right side is {num(key)}, so the "
                 f"{want} value {u} can take is {num(key)}.")
    ex = E(key)
    wrong = [Mis("used the other sign for the number of units subtracted",
                 E(m * y - sgn * k)),
             Mis("multiplied the two given numbers and stopped", E(m * y)),
             Mis(f"added {num(k)} to {v} before multiplying", E(m * (y + sgn * k))),
             Mis("used the value given for the other variable", E(y))]
    if fmt == "spr":
        # the option reasons above fit only one phrase each; a typed value is
        # named for the phrase this stem used
        did, to = ("added", "to") if sgn > 0 else ("subtracted", "from")
        named = [Mis(f"used the other sign for the number of units {did}",
                     wrong[0].value), wrong[1],
                 Mis(f"{did} {num(k)} {to} {v} before multiplying",
                     wrong[2].value), wrong[3]]
        return Item("ineq.greatest_value", "the extreme value an inequality "
                    "allows", "hard", seed, stem, "spr", ex, ex.gridin(),
                    rationale, params=P, spr_mistakes=gridin_mistakes(ex, named))
    from .kit import value_choices
    ch, tex, wh, letter = value_choices(ex, wrong, rng)
    return Item("ineq.greatest_value", "the extreme value an inequality allows",
                "hard", seed, stem, "mcq", ex, letter, rationale, ch, wh, tex,
                params=P)


# ------------------------------------------- what the system leaves for y

def y_range_from_system(rng: random.Random, seed: int, *, m=None, c=None, n=None,
                        t=None, u="x", v="y") -> Item:
    """Two inequalities bound x from below; the question wants the bound on y."""
    m = Q(rng.randint(2, 8) if m is None else m)
    c = Q(rng.choice([i for i in range(-10, 11) if i]) if c is None else c)
    n = Q(rng.randint(2, 6) if n is None else n)
    t = Q(rng.randint(-15, 25) if t is None else t)
    if m <= 0 or n <= 0:
        raise ItemError("both coefficients must be positive for one clean bound")
    xb = t / n
    key_val = m * xb + c
    if key_val == 0 or xb == 0 or key_val == xb:
        raise ItemError("a zero bound collapses the distractors")
    first = rel(v, ">", side([(m, u)], c))
    second = rel(term(n, u), ">", num(t))
    stem = sent(f"{first}\n{second}\nWhich of the following consists of the "
                f"{v}-coordinates of all the points that satisfy the given "
                f"system of inequalities?")
    key = rel(v, ">", num(key_val))
    wrong = [
        Mis(f"reported the bound on {u} rather than the bound on {v}",
            rel(v, ">", num(xb))),
        Mis(f"added the constant to the bound on {u} without multiplying by the "
            f"coefficient of {u}", rel(v, ">", num(xb + c))),
        Mis(f"used the number the second inequality prints instead of the bound "
            f"it gives for {u}", rel(v, ">", num(t - c))),
        Mis(f"multiplied the bound on {u} but left the constant out",
            rel(v, ">", num(m * xb))),
    ]
    P = {"kind": "ineq_y_range", "m": float(m), "c": float(c), "n": float(n),
         "t": float(t), "u": u, "v": v}
    rationale = (f"{second} gives {rel(u, '>', num(xb))}, so "
                 f"{side([(m, u)], c)} is greater than {num(key_val)}, and {v} "
                 f"is greater than that again, so {key}.")
    ch, wh, letter = text_choices(key, wrong, rng)
    return Item("ineq.y_range_from_system", "reading a bound out of a system",
                "hard", seed, stem, "mcq", E(0), letter, rationale, ch, wh,
                list(ch), params=P)


# --------------------------------------------- solving a compound inequality

def range_solve(rng: random.Random, seed: int, *, rate=None, k1=None, k2=None,
                base="x", var="s", pct=None) -> Item:
    """Total = base + rate·s is held between k1 and k2 times the base; find s."""
    pct = pct or rng.choice([4, 5, 6, 8, 10, 11, 12, 15, 20, 25])
    rate = Q(pct, 100) if rate is None else Q(rate)
    k1 = Q(rng.randint(2, 5) if k1 is None else k1)
    k2 = Q(rng.randint(3, 7) if k2 is None else k2)
    if k2 <= k1 or k1 < 2:
        raise ItemError("the goal has to be a band above the base salary")
    lo, hi = k1 - 1, k2 - 1
    r = dec(rate)

    def over(n) -> str:
        return f"({num(n)}/{r}){base}"

    key = band(over(lo), "<=", var, "<=", over(hi))
    wrong = [
        Mis("forgot to divide by the commission rate",
            band(term(lo, base), "<=", var, "<=", term(hi, base))),
        Mis("used the two multiples of the base salary as the bounds on sales",
            band(term(k1, base), "<=", var, "<=", term(k2, base))),
        Mis("did not subtract the base salary before dividing by the commission "
            "rate", band(over(k1), "<=", var, "<=", over(k2))),
        Mis("subtracted the base salary from only the upper bound",
            band(over(k1), "<=", var, "<=", over(hi))),
    ]
    stem = sent(f"A salesperson's total earnings consist of a base salary of "
                f"{base} dollars per year, plus commission earnings of "
                f"{num(pct)}% of the total sales the salesperson makes during "
                f"the year. This year, the salesperson has a goal for the total "
                f"earnings to be at least {num(k1)} times and at most "
                f"{num(k2)} times the base salary. Which of the following "
                f"inequalities represents all possible values of total sales "
                f"{var}, in dollars, the salesperson can make this year in order "
                f"to meet that goal?")
    P = {"kind": "ineq_range_solve", "rate": [rate.numerator, rate.denominator],
         "k1": float(k1), "k2": float(k2), "base": base, "var": var}
    rationale = (f"Total earnings are {base} + {r}{var}, and holding that "
                 f"between {num(k1)}{base} and {num(k2)}{base} leaves "
                 f"{num(lo)}{base} ≤ {r}{var} ≤ {num(hi)}{base}; "
                 f"dividing by {r}, which is positive, keeps the directions, so "
                 f"{key}.")
    ch, wh, letter = text_choices(key, wrong, rng)
    return Item("ineq.range_solve", "solving a compound inequality", "hard",
                seed, stem, "mcq", E(0), letter, rationale, ch, wh, list(ch),
                params=P)


# --------------------------------------------------------- triangle sides

def triangle_third_side(rng: random.Random, seed: int, *, a=None, b=None,
                        var="x") -> Item:
    """The third side of a triangle lies strictly between the two given ones."""
    a = int(rng.randint(2, 30) if a is None else a)
    b = int(rng.randint(2, 30) if b is None else b)
    if a == b:
        raise ItemError("equal sides give a lower bound of zero")
    lo, hi = abs(a - b), a + b
    key = band(num(lo), "<", var, "<", num(hi))
    wrong = [
        Mis("used only the sum of the two sides and left out the lower bound",
            rel(var, "<", num(hi))),
        Mis("reversed the one bound that was found",
            rel(var, ">", num(hi))),
        Mis("took the values outside the two bounds instead of between them",
            f"{rel(var, '<', num(lo))} or {rel(var, '>', num(hi))}"),
        Mis("used the difference of the two sides as the only bound",
            rel(var, ">", num(lo))),
    ]
    stem = sent(f"The triangle inequality theorem states that the sum of any "
                f"two sides of a triangle must be greater than the length of "
                f"the third side. If a triangle has side lengths of {num(a)} "
                f"and {num(b)}, which inequality represents the possible "
                f"lengths, {var}, of the third side of the triangle?")
    P = {"kind": "ineq_triangle", "a": float(a), "b": float(b), "var": var}
    rationale = (f"The third side has to be shorter than {num(a)} + {num(b)} "
                 f"and longer than the difference {num(hi - 2 * min(a, b))}, "
                 f"since the two shorter sides together must still beat the "
                 f"longest, so {key}.")
    ch, wh, letter = text_choices(key, wrong, rng)
    return Item("ineq.triangle_third_side", "a bound from the triangle "
                "inequality", "hard", seed, stem, "mcq", E(0), letter,
                rationale, ch, wh, list(ch), params=P)


# ------------------------------------------------- a dimension under a cap

def allowable_dimension(rng: random.Random, seed: int, *, cap=None, height=None,
                        factor=None, var="x") -> Item:
    """Perimeter of the base plus the height is capped; how wide can the box be?"""
    cap = int(rng.randrange(80, 260, 5) if cap is None else cap)
    height = int(rng.randrange(20, 120, 5) if height is None else height)
    factor = Q(factor if factor is not None else
               rng.choice([Q(3, 2), Q(2), Q(5, 2), Q(3), Q(7, 2), Q(4)]))
    if height >= cap or factor <= 1:
        raise ItemError("no positive width is left under that cap")
    left = Q(cap - height)
    key_v = left / (2 * (1 + factor))
    alts = [(left / (1 + factor),
             "added the width and the length once each instead of finding the "
             "whole perimeter"),
            (left / 4,
             "used four widths, as though the base were a square"),
            (left / (1 + 2 * factor),
             "doubled the length but counted the width only once")]
    key = band("0", "<", var, "<=", mixed(key_v))
    wrong = [Mis(why, band("0", "<", var, "<=", mixed(v))) for v, why in alts]
    wrong.append(Mis("left the height out of the cap altogether",
                     band("0", "<", var, "<=",
                          mixed(Q(cap) / (2 * (1 + factor))))))
    stem = sent(f"A shipping service restricts the dimensions of the boxes it "
                f"will ship for a certain type of service. The restriction "
                f"states that for boxes shaped like rectangular prisms, the sum "
                f"of the perimeter of the base of the box and the height of the "
                f"box cannot exceed {num(cap)} inches. The perimeter of the "
                f"base is determined using the width and length of the box. If "
                f"a box has a height of {num(height)} inches and its length is "
                f"{dec(factor)} times the width, which inequality shows the "
                f"allowable width {var}, in inches, of the box?")
    P = {"kind": "ineq_dimension", "cap": float(cap), "height": float(height),
         "factor": [factor.numerator, factor.denominator], "var": var}
    rationale = (f"The base has perimeter 2({var} + {dec(factor)}{var}) = "
                 f"{dec(2 * (1 + factor))}{var}, so "
                 f"{dec(2 * (1 + factor))}{var} + {num(height)} ≤ "
                 f"{num(cap)}, leaving {var} ≤ {mixed(key_v)}; a width is "
                 f"positive, so {key}.")
    ch, wh, letter = text_choices(key, wrong, rng)
    return Item("ineq.allowable_dimension", "a dimension under a cap", "hard",
                seed, stem, "mcq", E(0), letter, rationale, ch, wh, list(ch),
                params=P)
