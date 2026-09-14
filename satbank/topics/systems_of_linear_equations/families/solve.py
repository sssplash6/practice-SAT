"""Solving a system and reporting something about the solution.

The source asks for x, for y, for the pair, and for an expression the pair
satisfies -- x + y, x − y, xy, 5x, 3x + 3y -- and it varies the surface the two
equations are written on: both in standard form, one solved for a variable, one
of them a bare value, or a bracket that is itself one of the unknowns' sum.

Everything here solves by substitution: isolate a variable in one equation and
put it into the other. `audit.py` solves the same systems by Cramer's rule, off
determinants it forms itself, so neither route can cover for the other.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text
from ..kit import (MINUS, ask_label, ask_value, choices, coef, dec, displayed,
                   griddable, num, opt_dec, pick, point, q, sent, solved, std)

__all__ = ["solve_standard", "solve_substitution", "solve_pair", "chunk"]


# ------------------------------------------------------ the generator's route

def _reduce(eq) -> tuple:
    """A printed equation as (A, B, C) with A·x + B·y = C."""
    if eq[0] == "std":
        return q(eq[1]), q(eq[2]), q(eq[3])
    _, p, v, m, b = eq
    p, m, b = q(p), q(m), q(b)
    return (-m, p, b) if v == "y" else (p, -m, b)


def _by_substitution(e1, e2) -> tuple:
    """Isolate one unknown in the first equation and put it into the other.

    This is the route the stems describe, and it is the only solving this file
    does. Nothing here forms a determinant.
    """
    a1, b1, c1 = _reduce(e1)
    a2, b2, c2 = _reduce(e2)
    if b1 != 0:                       # y = (c1 − a1·x)/b1, substituted below
        lead = a2 - b2 * a1 / b1
        if lead == 0:
            raise ItemError("the two equations describe parallel lines")
        x = (c2 - b2 * c1 / b1) / lead
        return x, (c1 - a1 * x) / b1
    if a1 == 0:
        raise ItemError("the first equation says nothing about either unknown")
    x = c1 / a1                       # the first equation fixes x outright
    if b2 == 0:
        raise ItemError("neither equation pins the second unknown")
    return x, (c2 - a2 * x) / b2


def _y_on(eq, x):
    """The y that the given equation pairs with this x."""
    a, b, c = _reduce(eq)
    if b == 0:
        return None
    return (c - a * q(x)) / b


# --------------------------------------------------------------- the frames

FRAMES = {
    "solution_value": "The solution to the given system of equations is (x, y). "
                      "What is the value of {ask}?",
    "if_solution": "If (x, y) is the solution to the given system of equations, "
                   "what is the value of {ask} ?",
    "above_has": "The system of equations above has solution (x, y). What is the "
                 "value of {ask} ?",
    "in_above": "In the solution (x, y) to the system of equations above, what is "
                "the value of {ask} ?",
    "in_above_plain": "In the solution to the system of equations above, what is the "
                      "value of {ask} ?",
    "if_above": "If (x, y) is the solution to the system of equations above, what is "
                "the value of {ask} ?",
    "if_satisfies": "If (x, y) satisfies the system of equations above, what is the "
                    "value of {ask} ?",
    "if_has_above": "If the system of equations above has solution (x, y), what is "
                    "the value of {ask} ?",
}
FRAME_NAMES = list(FRAMES)

PAIR_FRAMES = {
    "what_solution": "What is the solution (x, y) to the given system of equations?",
    "what_solution_above": "What is the solution (x, y) to the system of equations "
                           "above?",
}


def _frame(frame: str, label: str) -> str:
    return sent(FRAMES[frame].format(ask=label))


# ------------------------------------------------- both sides standard form

def solve_standard(rng: random.Random, seed: int, *, a1=None, b1=None, c1=None,
                   a2=None, b2=None, c2=None, ask=None, k=None, frame=None,
                   fmt=None, style="frac", value_style=None, wrongs=None,
                   difficulty="medium") -> Item:
    """a₁x + b₁y = c₁ and a₂x + b₂y = c₂; report x, y, or an expression in both."""
    ask = ask or rng.choice(["x", "x", "y", "y", "sum", "diff", "prod", "k_sum"])
    frame = frame or rng.choice(FRAME_NAMES)
    fmt = fmt or ("spr" if rng.random() < 0.35 else "mcq")

    if ask == "k_sum":
        # the item works because subtracting the two equations leaves k(x + y)
        k = Q(int(k) if k is not None else rng.randint(2, 6))
        a1 = Q(int(a1) if a1 is not None else rng.randint(4, 12))
        b1 = Q(int(b1) if b1 is not None else rng.choice([i for i in range(-12, 13) if i]))
        a2 = Q(int(a2) if a2 is not None else a1 - k)
        b2 = Q(int(b2) if b2 is not None else b1 - k)
        if a1 - a2 != k or b1 - b2 != k:
            raise ItemError("subtracting the equations does not leave the expression asked for")
    else:
        k = Q(int(k) if k is not None else rng.choice([2, 3, 4, 5]))
        a1 = q(a1) if a1 is not None else Q(rng.choice([i for i in range(-9, 13)]))
        b1 = q(b1) if b1 is not None else Q(rng.choice([i for i in range(-9, 13) if i]))
        a2 = q(a2) if a2 is not None else Q(rng.choice([i for i in range(-9, 13)]))
        b2 = q(b2) if b2 is not None else Q(rng.choice([i for i in range(-9, 13)]))
    if c1 is None and c2 is None:
        # build the constants from a whole-number solution, so a free draw reads
        # like the source set rather than like a fraction mill
        xw = Q(rng.choice([i for i in range(-9, 13) if i]))
        yw = Q(rng.choice([i for i in range(-9, 13) if i]))
        c1, c2 = a1 * xw + b1 * yw, a2 * xw + b2 * yw
    c1 = q(c1) if c1 is not None else Q(rng.randint(-30, 80))
    c2 = q(c2) if c2 is not None else Q(rng.randint(-30, 80))

    if a1 * b2 - a2 * b1 == 0:
        raise ItemError("the two equations do not cross at a single point")
    if (a1 == 0 and b1 == 0) or (a2 == 0 and b2 == 0):
        raise ItemError("an equation with no unknown in it")
    e1, e2 = ("std", a1, b1, c1), ("std", a2, b2, c2)
    x0, y0 = _by_substitution(e1, e2)
    key = ask_value(ask, x0, y0, k)
    if ask == "prod" and (x0 == 0 or y0 == 0):
        raise ItemError("a product of zero gives the item away")
    if ask != "k_sum" and max(q(x0).denominator, q(y0).denominator) > 20:
        raise ItemError("the solution would not print cleanly")
    if q(key).denominator > 100:
        raise ItemError("the answer would not print cleanly")

    label = ask_label(ask, k)
    stem = displayed(std(a1, b1, c1, style=style), std(a2, b2, c2, style=style),
                     _frame(frame, label))

    # the whole misconception library for this shape, each entry a mistake a
    # teacher would recognise on a page of working
    def val(cc1, cc2, flip_x=False):
        xx, yy = _by_substitution(("std", a1, b1, cc1), ("std", a2, b2, cc2))
        if flip_x:
            xx = -xx
            yy = _y_on(("std", a2, b2, cc2), xx)
            if yy is None:
                return None
        return ask_value(ask, xx, yy, k)

    pool = {
        "other": Mis("found the other unknown and reported that instead",
                     y0 if ask == "x" else x0),
        "pre_divide": Mis("left the coefficient the elimination step produced in "
                          "place instead of dividing it out", key * 2),
        "over_divide": Mis("divided by the elimination coefficient a second time",
                           key / 2),
        "rhs1": Mis("took the value on the right of the first equation as the answer",
                    c1),
        "rhs2": Mis("took the value on the right of the second equation as the answer",
                    c2),
        "rhs1_half": Mis("halved the first equation instead of the second when "
                         "matching the coefficients", c1 / 2),
        "rhs_diff": Mis("subtracted the two right-hand values instead of eliminating "
                        "an unknown", c1 - c2),
        "rhs_sum": Mis("added the two right-hand values instead of eliminating an "
                       "unknown", c1 + c2),
        "flip1": Mis("used the wrong sign for the value on the right of the first "
                     "equation", val(-c1, c2)),
        "flip2": Mis("used the wrong sign for the value on the right of the second "
                     "equation", val(c1, -c2)),
        "flipx": Mis("lost the minus sign when dividing, so x came out with the "
                     "wrong sign", val(c1, c2, flip_x=True)),
        "flip_both": Mis("lost the sign of x and the sign of the second equation's "
                         "constant", val(c1, -c2, flip_x=True)),
        "negate": Mis("moved the answer across the equals sign without changing its "
                      "sign", -key),
        "swap": Mis("subtracted the two unknowns instead of adding them",
                    x0 - y0 if ask == "sum" else x0 + y0),
        "add_eqs": Mis("added the two equations instead of subtracting them", c1 + c2),
        "neg_add_eqs": Mis("added the two equations instead of subtracting them, and "
                           "then took the wrong order", -(c1 + c2)),
        "wrong_order": Mis("subtracted the two equations in the wrong order", -key),
    }

    P = {"kind": "sys_standard", "e1": _pack(e1), "e2": _pack(e2), "ask": ask,
         "k": _p(k)}
    keyx = E(key)
    # a grid-in prints its answer one way; the rationale must not print it another
    final = keyx.gridin().replace("-", MINUS) if fmt == "spr" else None
    rationale = _story(a1, b1, c1, a2, b2, c2, x0, y0, ask, k, label, style, final)
    if fmt == "spr":
        if not griddable(key):
            raise ItemError("this answer could not be entered in the grid")
        return Item("sys.solve_standard", "solving a system", difficulty, seed, stem,
                    "spr", keyx, keyx.gridin(), rationale, params=P)
    fmt_value = opt_dec if value_style == "dec" else None
    ch, tex, why, letter = choices(keyx, pick(pool, wrongs), rng, fmt_value=fmt_value)
    return Item("sys.solve_standard", "solving a system", difficulty, seed, stem,
                "mcq", keyx, letter, rationale, ch, why, tex, params=P)


def _story(a1, b1, c1, a2, b2, c2, x0, y0, ask, k, label, style="frac",
           final=None) -> str:
    """How the elimination goes, in the words a teacher would use at the board."""
    E = lambda a, b, c: std(a, b, c, style=style)                        # noqa: E731
    show = dec if style == "dec" else num
    left = None                     # the unknown the first step leaves on its own
    if b1 == b2 and b1 != 0:
        head = (f"Subtracting {E(a2, b2, c2)} from {E(a1, b1, c1)} removes the "
                f"y-terms and leaves {E(a1 - a2, 0, c1 - c2)}")
        left = "x" if a1 - a2 in (1, -1) else None
    elif b1 == -b2 and b1 != 0:
        head = (f"Adding the two equations removes the y-terms and leaves "
                f"{E(a1 + a2, 0, c1 + c2)}")
        left = "x" if a1 + a2 in (1, -1) else None
    elif a1 == a2 and a1 != 0:
        head = (f"Subtracting {E(a2, b2, c2)} from {E(a1, b1, c1)} removes the "
                f"x-terms and leaves {E(0, b1 - b2, c1 - c2)}")
        left = "y" if b1 - b2 in (1, -1) else None
    elif b1 == 0:
        head = f"The first equation gives {E(a1, 0, c1)} on its own"
        left = "x" if a1 in (1, -1) else None
    elif b2 == 0:
        head = f"The second equation gives {E(a2, 0, c2)} on its own"
        left = "x" if a2 in (1, -1) else None
    else:
        head = (f"Multiplying {E(a1, b1, c1)} by {num(abs(b2))} and "
                f"{E(a2, b2, c2)} by {num(abs(b1))} makes the y-terms match, and "
                f"taking one from the other leaves "
                f"{E(a1 * b2 - a2 * b1, 0, c1 * b2 - c2 * b1)}")
    # when that step already reads "x = 6", saying "so x = 6" again is noise
    if left == "x":
        tail = f"the other equation then gives y = {show(y0)}"
    elif left == "y":
        tail = f"the other equation then gives x = {show(x0)}"
    else:
        tail = f"x = {show(x0)} and y = {show(y0)}"
    joiner = ", and " if left else ", so "
    if ask in ("x", "y"):
        return sent(f"{head}{joiner}{tail}.")
    got = final or show(ask_value(ask, x0, y0, k))
    return sent(f"{head}{joiner}{tail}, which makes {label} = {got}.")


# ----------------------------------------------- one equation solved already

def solve_substitution(rng: random.Random, seed: int, *, e1=None, e2=None, ask=None,
                       k=None, frame=None, fmt=None, style="frac", value_style=None,
                       wrongs=None, difficulty="medium") -> Item:
    """One equation gives a variable outright; substitute it into the other."""
    ask = ask or rng.choice(["x", "x", "y", "y", "sum", "diff", "kx"])
    k = Q(int(k) if k is not None else rng.choice([2, 3, 4, 5]))
    drawn = e1 is None or e2 is None
    if drawn:
        e1, e2 = _draw_pair(rng)
    if e1[0] != "solved" and e2[0] != "solved":
        raise ItemError("this template needs an equation already solved for a variable")

    x0, y0 = _by_substitution(e1, e2)
    key = ask_value(ask, x0, y0, k)
    if max(q(x0).denominator, q(y0).denominator) > 20:
        raise ItemError("the solution would not print cleanly")
    if drawn and (q(x0).denominator != 1 or q(y0).denominator != 1):
        # the official items that answer with a fraction say so in their own
        # numbers; a free draw should read like the many that do not
        raise ItemError("a free draw should land on a whole-number solution")
    label = ask_label(ask, k)
    frame = frame or rng.choice(FRAME_NAMES + ["intersects"])

    if frame == "intersects":
        if e1[0] != "solved" or e2[0] != "solved" or e1[2] != "y" or e2[2] != "y":
            raise ItemError("the intersection wording needs two equations in y")
        lab = {"x": "a", "y": "b"}.get(ask)
        if lab is None:
            raise ItemError("the intersection wording only names the two coordinates")
        stem = sent(f"In the xy-plane, the graph of {_print(e1, style)} intersects the "
                    f"graph of {_print(e2, style)} at the point (a, b). What is the "
                    f"value of {lab} ?")
    else:
        stem = displayed(_print(e1, style), _print(e2, style), _frame(frame, label))

    pool = _sub_pool(e1, e2, x0, y0, ask, k, key)
    P = {"kind": "sys_substitution", "e1": _pack(e1), "e2": _pack(e2), "ask": ask,
         "k": _p(k)}
    keyx = E(key)
    fmt = fmt or ("spr" if rng.random() < 0.3 else "mcq")
    final = keyx.gridin().replace("-", MINUS) if fmt == "spr" else None
    rationale = _sub_story(e1, e2, x0, y0, ask, k, label, final)
    if fmt == "spr":
        if not griddable(key):
            raise ItemError("this answer could not be entered in the grid")
        return Item("sys.solve_substitution", "solving a system by substitution",
                    difficulty, seed, stem, "spr", keyx, keyx.gridin(), rationale,
                    params=P)
    fmt_value = opt_dec if value_style == "dec" else None
    ch, tex, why, letter = choices(keyx, pick(pool, wrongs), rng, fmt_value=fmt_value)
    return Item("sys.solve_substitution", "solving a system by substitution",
                difficulty, seed, stem, "mcq", keyx, letter, rationale, ch, why, tex,
                params=P)


def _draw_pair(rng: random.Random):
    """A random pair of equations, at least one of them already solved."""
    shape = rng.choice(["two_solved", "solved_std", "value_then"])
    if shape == "two_solved":
        m1 = Q(rng.choice([i for i in range(-9, 10) if i]))
        m2 = Q(rng.choice([i for i in range(-9, 10) if i and i != m1]))
        return (("solved", 1, "y", m1, rng.randint(-20, 20)),
                ("solved", rng.choice([1, 1, 2, 3]), "y", m2, rng.randint(-20, 20)))
    if shape == "solved_std":
        return (("std", rng.choice([i for i in range(-9, 10) if i]),
                 rng.choice([i for i in range(-5, 6) if i]), rng.randint(-20, 40)),
                ("solved", 1, "y", rng.choice([i for i in range(-9, 10) if i]),
                 rng.randint(-20, 20)))
    v = rng.choice(["x", "y"])
    other = "y" if v == "x" else "x"
    return (("solved", 1, v, 0, rng.randint(-15, 25)),
            ("solved", 1, other, rng.choice([1, 1, 2, -1, 3]), rng.randint(-20, 25)))


def _print(eq, style="frac") -> str:
    if eq[0] == "std":
        return std(eq[1], eq[2], eq[3], style=style)
    _, p, v, m, b = eq
    w = "x" if v == "y" else "y"
    return solved(p, v, m, w, b, style=style)


def _sub_pool(e1, e2, x0, y0, ask, k, key) -> dict:
    """The misconceptions substitution invites, named as a teacher would name them."""
    asked = "x" if ask in ("x", "kx") else "y"
    other = y0 if asked == "x" else x0
    sol = [e for e in (e1, e2) if e[0] == "solved"]
    stds = [e for e in (e1, e2) if e[0] == "std"]
    # the equation that states the asked variable outright, if there is one
    own = next((e for e in sol if e[2] == asked), None)
    first = e1 if e1[0] == "solved" else e2
    p1, m1, b1 = q(first[1]), q(first[3]), q(first[4])

    pool = {
        "other": Mis("found the other unknown and reported that instead", other),
        "negate": Mis("moved the answer across the equals sign without changing its "
                      "sign", -key),
        "neg_other": Mis("found the other unknown and lost its sign as well", -other),
        "other_sum": Mis("added the two unknowns instead of subtracting them",
                         x0 + y0),
        "x_only": Mis("reported x on its own instead of the expression asked for", x0),
        "slope1": Mis("reported the coefficient of x from the first equation", m1),
        "const1": Mis("read the constant term of the first equation as the answer",
                      b1),
        "neg_const2": Mis("read the constant term of the second equation and dropped "
                          "its minus sign", -q(e2[4]) if e2[0] == "solved" else None),
        "recip1": Mis("turned the first equation's coefficient upside down instead of "
                      "solving", p1 / m1 if m1 else None),
        "recip2": Mis("turned the second equation's coefficient upside down instead "
                      "of solving",
                      (q(e2[1]) / q(e2[3])) if (e2[0] == "solved" and q(e2[3])) else None),
        "recip_sum": Mis("added the two coefficients turned upside down instead of "
                         "setting the two sides equal",
                         (p1 / m1 + q(e2[1]) / q(e2[3]))
                         if (m1 and e2[0] == "solved" and q(e2[3])) else None),
        "double_k": Mis("doubled the multiplier the question asks for", key * 2),
        "k_only": Mis("reported the multiplier from the question rather than the "
                      "value of the expression", k),
        "slope_times_k": Mis("multiplied the question's multiplier by the coefficient "
                             "in the first equation", k * m1),
    }
    if own is not None:
        b_own, m_own, p_own = q(own[4]), q(own[3]), q(own[1])
        pool["const_ask"] = Mis("read the constant term of that equation as the "
                                "answer", b_own / p_own)
        pool["const_over"] = Mis("divided the constant term by the other unknown "
                                 "instead of adding it",
                                 (b_own / p_own) / other if other else None)
        pool["const_minus"] = Mis("subtracted the other unknown from the constant "
                                  "term instead of adding it", b_own / p_own - other)
        pool["drop_const"] = Mis("left the constant term out of the substitution",
                                 m_own * other / p_own)
    if stds and sol:
        a, b, c = q(stds[0][1]), q(stds[0][2]), q(stds[0][3])
        p, m, b0 = q(sol[0][1]), q(sol[0][3]), q(sol[0][4])
        if sol[0][2] == "x":
            a, b = b, a
        lead, back = a + b * m / p, a - b * m / p
        pool["sign_const"] = Mis("used the wrong sign for the constant term when "
                                 "substituting",
                                 (c + b * b0 / p) / lead if lead else None)
        pool["subtract_sub"] = Mis("subtracted the substituted expression instead of "
                                   "adding it", (c + b * b0 / p) / back if back else None)
        pool["numerator"] = Mis("stopped at the numerator and never divided by the "
                                "coefficient substitution left", c - b * b0 / p)
    return pool


def _sub_story(e1, e2, x0, y0, ask, k, label, final=None) -> str:
    sol = e1 if e1[0] == "solved" else e2
    into = e2 if sol is e1 else e1
    w = "x" if sol[2] == "y" else "y"
    rhs = _print(sol).split(" = ", 1)[1]
    head = (f"Putting {rhs} in place of {coef(sol[1], sol[2])} in "
            f"{_print(into)} leaves an equation in {w} alone")
    tail = f"x = {num(x0)} and y = {num(y0)}"
    if ask in ("x", "y"):
        return sent(f"{head}, which gives {tail}.")
    got = final or num(ask_value(ask, x0, y0, k))
    return sent(f"{head}, which gives {tail}, so {label} = {got}.")


# --------------------------------------------------- the pair as the answer

def solve_pair(rng: random.Random, seed: int, *, e1=None, e2=None, frame=None,
               wrongs=None, offsets=None, difficulty="easy") -> Item:
    """The answer is the ordered pair itself, so every option is a point."""
    if e1 is None or e2 is None:
        e1, e2 = _draw_pair(rng)
    x0, y0 = _by_substitution(e1, e2)
    if q(x0).denominator != 1 or q(y0).denominator != 1:
        raise ItemError("the drawn solution is not a lattice point")
    frame = frame or rng.choice(list(PAIR_FRAMES))
    stem = displayed(_print(e1), _print(e2), sent(PAIR_FRAMES[frame]))

    A1, B1, C1 = _reduce(e1)
    sol = next((e for e in (e1, e2) if e[0] == "solved" and e[2] == "y"), None)
    m1 = q(sol[3]) / q(sol[1]) if sol else None
    b1 = q(sol[4]) / q(sol[1]) if sol else None
    offsets = offsets or [1, 2, 3]

    pool = {
        "swap": Mis("wrote the two coordinates in the wrong order", point(y0, x0)),
        "flip_y": Mis("lost the sign when dividing to find y", point(x0, -y0)),
        "flip_x": Mis("lost the sign when dividing to find x", point(-x0, y0)),
        "coef_times_x": Mis("multiplied the coefficient of y by x instead of solving "
                            "for y", point(x0, abs(B1) * x0) if B1 else None),
        "neg_coef_times_x": Mis("multiplied the coefficient of y by x and kept the "
                                "minus sign from the equation",
                                point(x0, -abs(B1) * x0) if B1 else None),
    }
    if m1 is not None:
        pool["drop_const"] = Mis("left the constant term out when substituting",
                                 point(x0, m1 * x0))
        pool["coef_pair"] = Mis("read the coefficient and the constant term as the "
                                "pair", point(m1, b1))
        pool["coef_as_x"] = Mis("used the coefficient of x as the value of x",
                                point(m1, m1 * m1 + b1))
        pool["slope_and_y"] = Mis("used the coefficient of x as the value of x and "
                                  "kept the stated y", point(m1, y0))
        pool["y_and_slope"] = Mis("wrote the pair in the wrong order and used the "
                                  "coefficient of x as y", point(y0, m1))
        pool["lost_sign"] = Mis("lost the minus sign when dividing, so x came out "
                                "positive", point(-x0, m1 * -x0 + b1))
    for i, t in enumerate(offsets, start=1):
        pool[f"along1_{i}"] = Mis("picked a point that satisfies the first equation "
                                  "but not the second",
                                  point(x0 + t * B1, y0 - t * A1))
    flat = next((e for e in (e1, e2) if e[0] == "std"), None)
    if flat is not None and sol is not None:
        A, B, C = _reduce(flat)
        p, m, b0 = q(sol[1]), q(sol[3]), q(sol[4])
        back = A - B * m / p
        if back:
            xx = abs((C + B * b0 / p) / back)
            pool["subtract_sub_abs"] = Mis("subtracted the substituted expression and "
                                           "then dropped the minus sign",
                                           point(xx, m * xx / p + b0 / p))

    P = {"kind": "sys_pair", "e1": _pack(e1), "e2": _pack(e2)}
    rationale = sent(f"{_pair_story(e1, e2)} so the pair is {point(x0, y0)}.")
    ch, why, letter = assemble_text(point(x0, y0), pick(pool, wrongs), rng)
    return Item("sys.solve_pair", "the solution as an ordered pair", difficulty, seed,
                stem, "mcq", E(1), letter, rationale, ch, why, ch, params=P)


def _pair_story(e1, e2) -> str:
    sol = e1 if e1[0] == "solved" else e2
    into = e2 if sol is e1 else e1
    rhs = _print(sol).split(" = ", 1)[1]
    return (f"Putting {rhs} in place of {coef(sol[1], sol[2])} in {_print(into)} "
            f"leaves one unknown,")


# ------------------------------------------- the first equation as a bracket

def chunk(rng: random.Random, seed: int, *, total=None, mult=None, coefy=None,
          grand=None, ask="y", frame=None, wrongs=None) -> Item:
    """x + y = S and k(x + y) + m·y = T: the bracket is the first total."""
    total = Q(int(total) if total is not None else rng.randint(8, 60))
    mult = Q(int(mult) if mult is not None else rng.choice([2, 3, 4, 5, -2, -3]))
    coefy = Q(int(coefy) if coefy is not None else rng.choice([2, 3, 4, 5, 6, 7]))
    grand = Q(int(grand) if grand is not None else rng.randint(20, 140))
    frame = frame or rng.choice(["if_solution", "solution_value", "if_above"])
    y0 = (grand - mult * total) / coefy
    x0 = total - y0
    if q(y0).denominator != 1 or y0 == 0 or x0 == 0 or y0 == x0:
        raise ItemError("the draw does not give a clean pair")
    key = y0 if ask == "y" else x0

    eq1 = std(1, 1, total)
    eq2 = f"{coef(mult, '(x + y)')} + {coef(coefy, 'y')} = {num(grand)}"
    stem = displayed(eq1, eq2, _frame(frame, ask_label(ask)))
    pool = {
        "half_total": Mis("split the first total evenly between the two unknowns",
                          total / 2),
        "coefy_total": Mis("multiplied the first total by the coefficient of y "
                           "instead of substituting it into the bracket",
                           coefy * total),
        "total_minus": Mis("subtracted the first total once instead of the number of "
                           "times the bracket calls for", grand - total),
        "pre_divide": Mis("stopped before dividing by the coefficient of y",
                          grand - mult * total),
        "other": Mis("found the other unknown and reported that instead",
                     x0 if ask == "y" else y0),
        "negate": Mis("moved the bracket across the equals sign without changing its "
                      "sign", -key),
    }
    P = {"kind": "sys_chunk", "total": _p(total), "mult": _p(mult),
         "coefy": _p(coefy), "grand": _p(grand), "ask": ask}
    rationale = sent(f"The bracket is the first total, so {eq2} becomes "
                     f"{num(mult * total)} + {coef(coefy, 'y')} = {num(grand)}, "
                     f"giving y = {num(y0)} and x = {num(x0)}.")
    keyx = E(key)
    ch, tex, why, letter = choices(keyx, pick(pool, wrongs), rng)
    return Item("sys.chunk", "a substituted bracket", "easy", seed, stem, "mcq",
                keyx, letter, rationale, ch, why, tex, params=P)


# ------------------------------------------------------------ params packing

def _p(v) -> list:
    v = q(v)
    return [v.numerator, v.denominator]


def _pack(eq) -> list:
    if eq[0] == "std":
        return ["std", _p(eq[1]), _p(eq[2]), _p(eq[3])]
    return ["solved", _p(eq[1]), eq[2], _p(eq[3]), _p(eq[4])]
