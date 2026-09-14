"""Slope, intercept and the equation of a line.

The parallel and perpendicular items are the largest group in the topic and
they share one distractor family: the four candidates m, -m, 1/m and -1/m,
three of which are wrong whichever of the two relations is asked for. What
varies is the form the line is handed over in -- slope-intercept, standard
form, a standard form pushed to zero, a bare x = c -- because each form offers
its own extra wrong number to grab, and those are the options the source uses.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q
from math import gcd

from ....figures import coordinate_grid
from ....item import Item, ItemError, Mis
from ..common import (choose, coef_text, ex, lin_text, numtext, point_text, q, sig,
                      std_text, text_item)

__all__ = ["slope_of_line", "parallel_perpendicular", "slope_two_points",
           "point_on_line", "line_equation", "intercepts", "equivalent_system"]

NAMES = ["j", "k", "m", "n", "p", "r", "s", "t"]


def _int_std(m, b):
    """y = mx + b as Ax + By = C with whole, coprime coefficients, A > 0."""
    m, b = q(m), q(b)
    d = m.denominator * b.denominator // gcd(m.denominator, b.denominator)
    A, B, C = (m.numerator * (d // m.denominator), -d,
               -b.numerator * (d // b.denominator))
    g = gcd(gcd(abs(A), abs(B)), abs(C)) or 1
    A, B, C = A // g, B // g, C // g
    if A < 0 or (A == 0 and B < 0):
        A, B, C = -A, -B, -C
    return q(A), q(B), q(C)


# --------------------------------------------- the slope, once simplified

def slope_of_line(rng: random.Random, seed: int, *, form=None, p=None, d=None, r=None,
                  s=None, c=None) -> Item:
    """The equation needs tidying before the coefficient of x can be read off."""
    form = form or rng.choice(["grouped", "fraction"])
    D = int(d if d is not None else rng.randint(2, 20))
    P = int(p if p is not None else rng.randint(2, 40))
    if D < 2 or P == 0:
        raise ItemError("the coefficient of x must survive the division")
    if gcd(P, D) != 1:
        raise ItemError("the printed fraction must already be in lowest terms")
    C = int(c if c is not None else rng.choice([rng.randint(-60, -2), rng.randint(2, 60)]))
    if form == "grouped":
        R = int(r if r is not None else rng.randint(2, 40))
        S = int(s if s is not None else rng.randint(1, 12))
        key = Q(P, D) + S
        body = (f"({numtext(Q(1, D))})({numtext(P)}x + {numtext(R)}) + "
                f"{coef_text(S, 'x')}")
        why = (f"Multiplying through, the bracket contributes {coef_text(Q(P, D), 'x')}, and "
               f"adding the {numtext(S)}x already outside it collects every term in x; "
               f"the constant shifts the line without tilting it.")
        P_ = {"kind": "le2_slope_form", "form": form, "p": P, "d": D, "r": R, "s": S}
    else:
        key = Q(P, D)
        body = f"{numtext(P)}x/{numtext(D)} - {numtext(abs(C))}" if C < 0 else \
               f"{numtext(P)}x/{numtext(D)} + {numtext(C)}"
        why = (f"Only the term in x tilts the line: {numtext(P)}x/{numtext(D)} moves "
               f"y by {numtext(Q(P, D))} for every 1 that x moves, and the constant "
               f"term shifts the whole line without changing that.")
        P_ = {"kind": "le2_slope_form", "form": form, "p": P, "d": D, "c": C}
    keyx = ex(key)
    if not keyx.is_rational or len(keyx.gridin()) > 6:
        raise ItemError("the slope does not fit a grid-in")
    stem = f"What is the slope of the graph of y = {body} in the xy-plane?"
    return Item("le2.slope_of_line", "the slope of a line", "medium", seed, stem, "spr",
                keyx, keyx.gridin(), why, params=P_)


# --------------------------------------------- parallel and perpendicular

def parallel_perpendicular(rng: random.Random, seed: int, *, form=None, relation=None,
                           ask=None, m=None, b=None, A=None, B=None, C=None, c=None,
                           fmt=None, first=None, given=None, other=None, wrongs=None,
                           layout=None) -> Item:
    """The slope, or the equation, of a line parallel or perpendicular to a given one."""
    form = form or rng.choice(["slope_intercept", "standard", "standard_zero", "axis"])
    relation = relation or rng.choice(["parallel", "perpendicular"])
    ask = ask or "slope"
    given = given or rng.choice(NAMES)
    other = other or rng.choice([n for n in NAMES if n != given])

    if form == "axis":
        K = int(c if c is not None else rng.randint(2, 40))
        vertical = (first if first is not None else rng.random() < 0.5)
        line = f"x = {numtext(K)}" if vertical else f"y = {numtext(K)}"
        flat = (vertical and relation == "perpendicular") or \
               (not vertical and relation == "parallel")
        if not flat:
            raise ItemError("a line with no slope at all is not a value to ask for")
        if K < 2:
            raise ItemError("the constant must be large enough to tell from its own "
                            "reciprocal")
        stem = (f"Line ℓ in the xy-plane is {relation} to the line with equation "
                f"{line}. What is the slope of line ℓ?")
        why = (f"{line} is a {'vertical' if vertical else 'horizontal'} line, so a line "
               f"{relation} to it runs flat across the plane, and a flat line does not "
               f"rise at all as it goes along.")
        P = {"kind": "le2_par_perp", "form": form, "relation": relation, "c": K,
             "vertical": bool(vertical), "ask": "slope"}
        wrong = [Mis("gave the slope of the line in the equation rather than the slope "
                     "of the line perpendicular to it, which is the one asked for",
                     ("The slope of line ℓ is undefined.", sig("undef"))),
                 Mis("treated the constant in the equation as a slope and changed its "
                     "sign", (numtext(-K), sig("plain", -K))),
                 Mis("treated the constant in the equation as the slope",
                     (numtext(K), sig("plain", K))),
                 Mis("treated the constant in the equation as a slope and inverted it",
                     (numtext(Q(1, K)), sig("plain", Q(1, K))))]
        return text_item("le2.parallel_perpendicular", "a line parallel or perpendicular "
                         "to another", "hard", seed, stem, "0", sig("zero"), wrong, rng,
                         P, why)

    extra = []
    if form == "slope_intercept":
        M = q(m) if m is not None else q(rng.choice(
            [rng.randint(2, 12), rng.randint(-12, -2), Q(rng.randint(2, 19),
                                                         rng.randint(2, 9))]))
        Bv = q(b) if b is not None else q(rng.randint(-30, 30))
        if M == 0 or Bv == 0:
            raise ItemError("the line must slope and must miss the origin")
        line = f"y = {lin_text(M, Bv)}"
        extra = [("sum", "added the y-intercept to the slope and inverted that",
                  Q(-1, 1) / (M + Bv) if M + Bv != 0 else None),
                 ("diff", "subtracted the slope from the y-intercept and inverted that",
                  Q(-1, 1) / (Bv - M) if Bv != M else None),
                 ("product", "multiplied the slope by the y-intercept and inverted "
                             "that", Q(-1, 1) / (M * Bv))]
        P = {"kind": "le2_par_perp", "form": form, "relation": relation,
             "m": [M.numerator, M.denominator], "b": [Bv.numerator, Bv.denominator]}
    else:
        Ac = q(A) if A is not None else q(rng.choice([rng.randint(2, 12),
                                                      rng.randint(-12, -2)]))
        Bc = q(B) if B is not None else q(rng.choice([rng.randint(2, 12),
                                                      rng.randint(-12, -2)]))
        Cc = q(C) if C is not None else q(rng.randint(-40, 40))
        if Ac == 0 or Bc == 0:
            raise ItemError("both variables must appear")
        M = -Ac / Bc
        if form == "standard":
            flip = layout == "yx" if layout else (A is None and rng.random() < 0.5)
            line = (std_text(Bc, Ac, Cc, "y", "x") if flip
                    else std_text(Ac, Bc, Cc, "x", "y"))
        else:
            line = f"{coef_text(Ac, 'x')} + {coef_text(Bc, 'y')} - {numtext(abs(Cc))} = 0" \
                if Cc > 0 else \
                f"{coef_text(Ac, 'x')} + {coef_text(Bc, 'y')} + {numtext(-Cc)} = 0"
            if Bc < 0:
                line = line.replace(f"+ {coef_text(Bc, 'y')}",
                                    f"- {coef_text(-Bc, 'y')}")
        extra = [("coefx", "read the coefficient of x as the slope", Ac),
                 ("coefy", "read the coefficient of y as the slope", Bc),
                 ("negcoefx", "read the coefficient of x as the slope and changed its "
                              "sign", -Ac)]
        P = {"kind": "le2_par_perp", "form": form, "relation": relation,
             "A": [Ac.numerator, Ac.denominator], "B": [Bc.numerator, Bc.denominator],
             "C": [Cc.numerator, Cc.denominator]}
        if form == "standard":
            P["swapped"] = line.startswith(coef_text(Bc, "y"))

    if M == 0:
        raise ItemError("a horizontal line has no perpendicular with a slope")
    key = M if relation == "parallel" else -1 / M
    P["ask"] = ask

    if ask == "equation":
        Bi = q(b if b is not None else rng.randint(-12, 12))
        if Bi == 0:
            raise ItemError("the new line must miss the origin")
        Ak, Bk, Ck = _int_std(key, Bi)
        stem = (f"In the xy-plane, line {given} is defined by {line}. Line {other} is "
                f"{relation} to line {given}, and the y-intercept of line {other} is "
                f"(0, {numtext(Bi)}). Which of the following is an equation of line "
                f"{other}?")
        keytext = std_text(Ak, Bk, Ck, "x", "y")
        swapped = ("used the given line's own slope instead of the perpendicular one"
                   if relation == "perpendicular" else
                   "turned the slope perpendicular when the two lines are parallel")
        cands = [(swapped, _int_std(-1 / key, Bi)),
                 ("changed the sign of the y-intercept", _int_std(key, -Bi)),
                 ("used the wrong slope and changed the sign of the y-intercept",
                  _int_std(-1 / key, -Bi))]
        wrong = [Mis(r, (std_text(u, v, w, "x", "y"), sig("std", u, v, w)))
                 for r, (u, v, w) in cands if (u, v, w) != (Ak, Bk, Ck)]
        P["bi"] = [Bi.numerator, Bi.denominator]
        why = (f"Line {given} has slope {numtext(M)}, so line {other} has slope "
               f"{numtext(key)}; a line through (0, {numtext(Bi)}) with that slope "
               f"rearranges to the equation above.")
        return text_item("le2.parallel_perpendicular", "a line parallel or perpendicular "
                         "to another", "hard", seed, stem, keytext,
                         sig("std", Ak, Bk, Ck), wrong, rng, P, why)

    stem = (f"Line {given} is defined by {line}. Line {other} is {relation} to line "
            f"{given} in the xy-plane. What is the slope of line {other}?")
    keyx = ex(key)
    moves = (f"rises {numtext(M)}" if M > 0 else f"falls {numtext(-M)}")
    why = (f"Line {given} {moves} for every 1 along, and a perpendicular line has to "
           f"turn a quarter circle, which swaps the rise and the run and reverses the "
           f"direction."
           if relation == "perpendicular" else
           f"Rearranged, line {given} {moves} for every 1 along, and parallel lines "
           f"move at exactly the same rate.")
    pool = [("same", "gave the given line's own slope", M),
            ("negm", "changed the sign of the slope without inverting it", -M),
            ("invm", "inverted the slope without changing its sign", 1 / M),
            ("neginv", "inverted the slope and changed its sign, though parallel lines "
                       "share a slope" if relation == "parallel" else
                       "gave the given line's own slope with its sign changed", -1 / M)]
    pool += list(extra)
    if wrongs:
        # a filter, not just an order: `assemble` prefers options of the key's own
        # surface form, so leaving the others in the pool would crowd out the ones
        # the source item actually printed
        pool = sorted((t for t in pool if t[0] in wrongs),
                      key=lambda t: wrongs.index(t[0]))
    seen, mistakes = {q(key)}, []
    for _, r, v in pool:
        if v is None:
            continue
        v = q(v)
        if v in seen:
            continue
        seen.add(v)
        mistakes.append(Mis(r, ex(v)))
    fmt = fmt or "mcq"
    if fmt == "spr":
        if not keyx.is_rational or len(keyx.gridin()) > 6:
            raise ItemError("the slope does not fit a grid-in")
        return Item("le2.parallel_perpendicular", "a line parallel or perpendicular to "
                    "another", "medium", seed, stem, "spr", keyx, keyx.gridin(), why,
                    params=P)
    choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True,
                                             fillers="shift")
    return Item("le2.parallel_perpendicular", "a line parallel or perpendicular to "
                "another", "medium", seed, stem, "mcq", keyx, letter, why, choices,
                reasons, latex, params=P)


# --------------------------------------------- a slope from what is drawn

def slope_two_points(rng: random.Random, seed: int, *, given=None, ask=None, x1=None,
                     y1=None, x2=None, y2=None, name=None, fmt=None) -> Item:
    """Two points, two intercepts or a drawn line, and the slope they fix."""
    given = given or rng.choice(["points", "intercepts", "graph"])
    ask = ask or ("perpendicular" if given == "graph" else "slope")
    name = name or rng.choice(NAMES)
    if given == "intercepts":
        X1 = q(x1) if x1 is not None else q(rng.choice([rng.randint(-12, -1),
                                                        rng.randint(1, 12)]))
        Y2 = q(y2) if y2 is not None else q(rng.choice(
            [rng.randint(2, 40), Q(rng.randint(5, 99), rng.randint(2, 6))]))
        X2, Y1 = q(0), q(0)
        pts = ((X1, Y1), (X2, Y2))
    else:
        X1 = q(x1) if x1 is not None else q(rng.randint(-12, 12))
        Y1 = q(y1) if y1 is not None else q(rng.randint(-12, 12))
        X2 = q(x2) if x2 is not None else q(rng.randint(-12, 16))
        Y2 = q(y2) if y2 is not None else q(rng.randint(-12, 24))
        pts = ((X1, Y1), (X2, Y2))
    if X1 == X2 or Y1 == Y2:
        raise ItemError("the two points must fix a slope that is neither flat nor "
                        "vertical")
    M = (Y2 - Y1) / (X2 - X1)
    key = M if ask == "slope" else -1 / M
    keyx = ex(key)
    fig = None
    if given == "points":
        stem = (f"A line passes through the points {point_text(X1, Y1)} and "
                f"{point_text(X2, Y2)} in the xy-plane. What is the slope of the line?")
        why = (f"Between the two points the line climbs {numtext(Y2 - Y1)} while it "
               f"runs {numtext(X2 - X1)}, and the slope is the first divided by the "
               f"second.")
    elif given == "intercepts":
        stem = (f"When line {name} is graphed in the xy-plane, it has an x-intercept of "
                f"{point_text(X1, 0)} and a y-intercept of {point_text(0, Y2)}. What is "
                f"the slope of line {name}?")
        why = (f"Both intercepts are points on the line: going from "
               f"{point_text(X1, 0)} to {point_text(0, Y2)} the run is "
               f"{numtext(-X1)} and the climb is {numtext(Y2)}, and the slope is the "
               f"climb divided by the run.")
    else:
        if any(v.denominator != 1 for v in (X1, Y1, X2, Y2)):
            raise ItemError("a drawn line has to pass through lattice points")
        lo = min(int(X1), int(X2), 0) - 2
        hi = max(int(X1), int(X2), 0) + 2
        ylo = min(int(Y1), int(Y2), 0) - 2
        yhi = max(int(Y1), int(Y2), 0) + 2
        if hi - lo > 22 or yhi - ylo > 22:
            raise ItemError("the drawn line would not fit a readable grid")
        fig = coordinate_grid(lo, hi, ylo, yhi,
                              segments=[((int(X1), int(Y1)), (int(X2), int(Y2)))])
        stem = (f"Line {name} is shown in the xy-plane. Line {rng.choice([n for n in NAMES if n != name])} "
                f"(not shown) is perpendicular to line {name}. What is the slope of "
                f"line {rng.choice([n for n in NAMES if n != name])}?")
        other = "j" if name != "j" else "k"
        stem = (f"Line {name} is shown in the xy-plane. Line {other} (not shown) is "
                f"perpendicular to line {name}. What is the slope of line {other}?")
        why = (f"The two marked points give line {name} a slope of {numtext(M)}; a "
               f"perpendicular line flips the rise and the run and reverses the "
               f"direction.")
    P = {"kind": "le2_two_points", "given": given, "ask": ask,
         "x1": [X1.numerator, X1.denominator], "y1": [Y1.numerator, Y1.denominator],
         "x2": [X2.numerator, X2.denominator], "y2": [Y2.numerator, Y2.denominator]}
    fmt = fmt or ("mcq" if given == "intercepts" else "spr")
    if fmt == "spr":
        if not keyx.is_rational or len(keyx.gridin()) > 6:
            raise ItemError("the slope does not fit a grid-in")
        return Item("le2.slope_two_points", "a slope from two points", "medium", seed,
                    stem, "spr", keyx, keyx.gridin(), why, figure=fig, params=P)
    rise, run = Y2 - Y1, X2 - X1
    mistakes = [Mis("inverted the slope, dividing the run by the rise", ex(1 / key)),
                Mis("multiplied the two intercept values instead of dividing one by "
                    "the other", ex(rise * run) if rise * run != 0 else None),
                Mis("inverted the product of the two intercept values",
                    ex(1 / (rise * run)) if rise * run != 0 else None),
                Mis("changed the sign of the slope", ex(-key)),
                Mis("divided the run by the rise and changed the sign", ex(-1 / key))]
    mistakes = [m for m in mistakes if m.value is not None]
    choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True,
                                             fillers="shift")
    return Item("le2.slope_two_points", "a slope from two points", "medium", seed, stem,
                "mcq", keyx, letter, why, choices, reasons, latex, figure=fig, params=P)


# ------------------------------------------- a third point, or a constant

def point_on_line(rng: random.Random, seed: int, *, ask=None, mode=None, x1=None, y1=None,
                  x2=None, y2=None, x3=None, m=None, b=None, c=None, name=None) -> Item:
    """What a line already fixed forces at one more place."""
    ask = ask or rng.choice(["coordinate", "coordinate", "constant"])
    name = name or rng.choice(NAMES)
    if ask == "constant":
        C = q(c) if c is not None else q(rng.choice([rng.randint(2, 30),
                                                     rng.randint(-30, -2)]))
        X1 = q(x1) if x1 is not None else q(rng.choice([rng.randint(-9, -1),
                                                        rng.randint(1, 9)]))
        Y2 = q(y2) if y2 is not None else q(rng.choice([rng.randint(-9, -1),
                                                        rng.randint(1, 9)]))
        Y1 = q(y1) if y1 is not None else q(rng.choice([rng.randint(-9, -1),
                                                        rng.randint(1, 9)]))
        if Y1 == Y2 or X1 == 0 or Y2 == 0 or Y1 == 0:
            raise ItemError("the two points must differ and must not sit on an axis")
        K = C / Y2
        Acon = (C - K * Y1) / X1
        if Acon == 0 or K == 0 or K == Acon:
            raise ItemError("the two constants must both be there and must differ")
        stem = (f"The graph of the equation ax + ky = {numtext(C)} is a line in the "
                f"xy-plane, where a and k are constants. If the line contains the "
                f"points {point_text(X1, Y1)} and {point_text(0, Y2)}, what is the "
                f"value of k ?")
        why = (f"At {point_text(0, Y2)} the x term vanishes whatever a is, so the "
               f"{numtext(Y2)} in the y term has to account for the whole of "
               f"{numtext(C)} by itself.")
        keyx = ex(K)
        seen, mistakes = {K}, []
        for reason, v in [("gave the value of a rather than of k", Acon),
                          ("changed the sign of k", -K),
                          ("used the other point's y-coordinate, which does not stand "
                           "alone", C / Y1),
                          ("divided by the x-coordinate instead of the y-coordinate",
                           C / X1),
                          ("multiplied by the y-coordinate instead of dividing by it",
                           C * Y2),
                          ("divided the y-coordinate by the constant term instead of "
                           "the other way round", Y2 / C)]:
            if v in seen:
                continue
            seen.add(v)
            mistakes.append(Mis(reason, ex(v)))
        if len(mistakes) < 3:
            raise ItemError("too few of the named mistakes survive these numbers")
        P = {"kind": "le2_point_on_line", "ask": ask, "c": [C.numerator, C.denominator],
             "x1": [X1.numerator, X1.denominator], "y1": [Y1.numerator, Y1.denominator],
             "y2": [Y2.numerator, Y2.denominator]}
        choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True,
                                                 fillers="shift")
        return Item("le2.point_on_line", "a constant fixed by a point", "hard", seed,
                    stem, "mcq", keyx, letter, why, choices, reasons, latex, params=P)

    mode = mode or rng.choice(["two_points", "parallel"])
    if mode == "two_points":
        Bv = q(b) if b is not None else q(rng.randint(-20, 20))
        X1 = q(x1) if x1 is not None else q(rng.choice([rng.randint(-9, -1),
                                                        rng.randint(1, 9)]))
        Y1 = q(y1) if y1 is not None else q(rng.randint(-20, 20))
        M = (Y1 - Bv) / X1
        X3 = q(x3) if x3 is not None else q(rng.randrange(10, 40, 2))
        if M == 0:
            raise ItemError("a flat line makes the third point no work")
        key = M * X3 + Bv
        stem = (f"In the xy-plane, line {name} intersects the y-axis at the point "
                f"{point_text(0, Bv)} and passes through the point "
                f"{point_text(X1, Y1)}. If the point ({numtext(X3)}, w) lies on line "
                f"{name}, what is the value of w ?")
        why = (f"Between {point_text(0, Bv)} and {point_text(X1, Y1)} the line climbs "
               f"{numtext(Y1 - Bv)} over a run of {numtext(X1)}, a slope of "
               f"{numtext(M)}; from the y-intercept out to x = {numtext(X3)} is a run "
               f"of {numtext(X3)}, so the line climbs {numtext(X3)}·{numtext(M)} more.")
        P = {"kind": "le2_point_on_line", "ask": ask, "mode": mode,
             "b": [Bv.numerator, Bv.denominator], "x1": [X1.numerator, X1.denominator],
             "y1": [Y1.numerator, Y1.denominator], "x3": [X3.numerator, X3.denominator]}
    else:
        M = q(m) if m is not None else q(rng.choice([rng.randint(2, 12),
                                                     rng.randint(-12, -2)]))
        Cv = q(c) if c is not None else q(rng.randint(-20, 20))
        X3 = q(x3) if x3 is not None else q(rng.randint(2, 12))
        if M == 0 or Cv == 0:
            raise ItemError("the given line must slope and must miss the origin")
        key = M * X3
        stem = (f"In the xy-plane, line ℓ passes through the point (0, 0) and is "
                f"parallel to the line represented by the equation y = "
                f"{lin_text(M, Cv)}. If line ℓ also passes through the point "
                f"({numtext(X3)}, d), what is the value of d?")
        moves = f"climbs {numtext(M)}" if M > 0 else f"drops {numtext(-M)}"
        why = (f"Parallel lines share a slope, so line ℓ {moves} for every 1 along; "
               f"what it does not share is the {numtext(Cv)}, because it starts from "
               f"the origin instead.")
        P = {"kind": "le2_point_on_line", "ask": ask, "mode": mode,
             "m": [M.numerator, M.denominator], "c": [Cv.numerator, Cv.denominator],
             "x3": [X3.numerator, X3.denominator]}
    keyx = ex(key)
    if not keyx.is_rational or len(keyx.gridin()) > 6:
        raise ItemError("the answer does not fit a grid-in")
    return Item("le2.point_on_line", "a further point on a line", "hard", seed, stem,
                "spr", keyx, keyx.gridin(), why, params=P)


# ------------------------------------------- writing the equation of a line

LINE_STEMS = [
    ("In the xy-plane, a line has a slope of {m} and passes through the point (0, {b}). "
     "Which of the following is an equation of this line?", "slope_point"),
    ("A line in the xy-plane has a slope of {m} and passes through the point (0, {b}). "
     "Which equation represents this line?", "slope_point"),
    ("In the xy-plane, line {n} passes through the points (0, {b}) and ({x2}, {y2}). "
     "Which equation defines line {n}?", "two_points"),
]


def line_equation(rng: random.Random, seed: int, *, frame=None, m=None, b=None, x2=None,
                  y2=None, name=None, wrongs=None) -> Item:
    """Slope and y-intercept, or two points, written as y = mx + b."""
    frame = rng.randrange(len(LINE_STEMS)) if frame is None else frame
    text, given = LINE_STEMS[frame]
    name = name or rng.choice(NAMES)
    M = q(m) if m is not None else q(rng.choice(
        [rng.randint(2, 9), rng.randint(-9, -2), Q(1, rng.randint(2, 6)),
         Q(-1, rng.randint(2, 6))]))
    Bv = q(b) if b is not None else q(rng.randint(-12, 12))
    if M == 0 or Bv == 0 or M == Bv:
        raise ItemError("the slope and the intercept must differ and neither may vanish")
    if given == "two_points":
        X2 = q(x2) if x2 is not None else q(rng.randint(1, 8))
        if X2 == 0:
            raise ItemError("the second point must be off the y-axis")
        Y2 = q(y2) if y2 is not None else M * X2 + Bv
        M = (Y2 - Bv) / X2
        if M == 0:
            raise ItemError("a flat line hides the slope")
        stem = text.format(n=name, b=numtext(Bv), x2=numtext(X2), y2=numtext(Y2))
        why = (f"From (0, {numtext(Bv)}) to ({numtext(X2)}, {numtext(Y2)}) the line "
               f"climbs {numtext(Y2 - Bv)} over a run of {numtext(X2)}, and the first "
               f"point is already on the y-axis.")
    else:
        stem = text.format(m=numtext(M), b=numtext(Bv))
        why = (f"The point given is on the y-axis, so {numtext(Bv)} is the constant "
               f"term, and the stated slope is the coefficient of x.")
    key = f"y = {lin_text(M, Bv)}"
    ks = sig("line", M, Bv)

    def opt(u, v):
        return (f"y = {lin_text(u, v)}", sig("line", u, v))

    pool = {
        "swap": Mis("swapped the slope and the y-intercept", opt(Bv, M)),
        "product": Mis("multiplied the slope by the y-intercept and used that as the "
                       "constant term", opt(M, M * Bv)),
        "swapproduct": Mis("swapped the slope and the y-intercept and multiplied them "
                           "for the constant term", opt(Bv, M * Bv)),
        "negb": Mis("changed the sign of the y-intercept", opt(M, -Bv)),
        "negm": Mis("changed the sign of the slope", opt(-M, Bv)),
        "negboth": Mis("changed the sign of both the slope and the y-intercept",
                       opt(-M, -Bv)),
        "invm": Mis("inverted the slope", opt(1 / M, Bv)),
        "inv_neg": Mis("inverted the slope and changed its sign", opt(-1 / M, Bv)),
    }
    if given == "two_points":
        pool["runrise"] = Mis("divided the run by the climb instead of the climb by the "
                              "run", opt(X2 / (Y2 - Bv), Bv))
        pool["negrun"] = Mis("subtracted the coordinates in opposite orders, reversing "
                             "the slope", opt(-M, Bv))
        pool["climb"] = Mis("used the climb itself as the slope, forgetting to divide "
                            "by the run", opt(Y2 - Bv, Bv))
    order = wrongs or (["runrise", "negrun", "climb", "invm"] if given == "two_points"
                       else (["product", "swap", "swapproduct", "negb"]
                             if M.denominator == 1 else
                             ["negb", "negm", "negboth", "invm"]))
    wrong = [pool[k] for k in order if k in pool] + \
            [v for k, v in pool.items() if k not in order]
    P = {"kind": "le2_line_equation", "given": given,
         "m": [M.numerator, M.denominator], "b": [Bv.numerator, Bv.denominator]}
    if given == "two_points":
        P["x2"] = [X2.numerator, X2.denominator]
        P["y2"] = [Y2.numerator, Y2.denominator]
    return text_item("le2.line_equation", "the equation of a line", "easy", seed, stem,
                     key, ks, wrong, rng, P, why)


# ------------------------------------------------------------- intercepts

def intercepts(rng: random.Random, seed: int, *, mode=None, m=None, b=None, A=None,
               B=None, C=None, name=None, fmt=None) -> Item:
    """Where a line crosses an axis, read off an equation or off a picture."""
    mode = mode or rng.choice(["graph_point", "equation_y", "standard_x", "ratio"])

    if mode == "equation_y":
        M = q(m) if m is not None else q(rng.choice([rng.randint(2, 12),
                                                     rng.randint(-12, -2)]))
        Bv = q(b) if b is not None else q(rng.choice([rng.randint(2, 60),
                                                      rng.randint(-60, -2)]))
        if M == 0 or Bv == 0:
            raise ItemError("the line must slope and must miss the origin")
        stem = (f"The y-intercept of the graph of y = {lin_text(M, Bv)} in the xy-plane "
                f"is (0, y). What is the value of y?")
        why = ("Putting x = 0 wipes out the term in x, and what is left is the constant "
               "term.")
        keyx = ex(Bv)
        P = {"kind": "le2_intercepts", "mode": mode, "m": [M.numerator, M.denominator],
             "b": [Bv.numerator, Bv.denominator]}
        return Item("le2.intercepts", "the intercepts of a line", "easy", seed, stem,
                    "spr", keyx, keyx.gridin(), why, params=P)

    if mode == "standard_x":
        Ac = q(A) if A is not None else Q(rng.randint(1, 9), rng.randint(2, 9))
        Bc = q(B) if B is not None else Q(rng.randint(1, 9), rng.randint(2, 9))
        Cc = q(C) if C is not None else q(rng.choice([1, 2, 3, rng.randint(4, 20)]))
        if Ac == 0 or Bc == 0 or Cc == 0:
            raise ItemError("the line must cross both axes away from the origin")
        if Ac.denominator == 1 or Bc.denominator == 1 or Ac == Bc:
            raise ItemError("both coefficients must be fractions, or the item is a "
                            "one-step division")
        key = Cc / Ac
        keyx = ex(key)
        if len(keyx.gridin()) > 6:
            raise ItemError("the intercept does not fit a grid-in")
        eq = std_text(Ac, Bc, Cc, "x", "y")
        stem = (f"The line with the equation {eq} is graphed in the xy-plane. What is "
                f"the x-coordinate of the x-intercept of the line?")
        why = ("On the x-axis y is zero, so the term in y drops out and the term in x "
               "has to account for the whole right-hand side by itself.")
        P = {"kind": "le2_intercepts", "mode": mode, "A": [Ac.numerator, Ac.denominator],
             "B": [Bc.numerator, Bc.denominator], "C": [Cc.numerator, Cc.denominator]}
        return Item("le2.intercepts", "the intercepts of a line", "hard", seed, stem,
                    "spr", keyx, keyx.gridin(), why, params=P)

    if mode == "ratio":
        Ac = q(A) if A is not None else q(rng.randint(2, 12))
        Bc = q(B) if B is not None else q(rng.choice([rng.randint(2, 12),
                                                      rng.randint(-12, -2)]))
        Cc = q(C) if C is not None else q(rng.choice([rng.randint(5, 60),
                                                      rng.randint(-60, -5)]))
        if Ac <= 0 or Bc == 0 or Cc == 0 or abs(Ac) == abs(Bc):
            raise ItemError("the two intercepts must differ and neither may be at the "
                            "origin")
        eq = std_text(Ac, Bc, Cc, "x", "y")
        key = Ac / Bc
        keyx = ex(key)
        stem = (f"The graph of {eq} in the xy-plane has an x-intercept at (a, 0) and a "
                f"y-intercept at (0, b), where a and b are constants. What is the value "
                f"of b/a?")
        why = (f"a is {numtext(Cc)} divided by {numtext(Ac)} and b is {numtext(Cc)} "
               f"divided by {numtext(Bc)}, so dividing b by a cancels the "
               f"{numtext(Cc)} and leaves the two coefficients.")
        mistakes = [Mis("divided a by b instead of b by a", ex(1 / key)),
                    Mis("changed the sign of the ratio", ex(-key)),
                    Mis("divided a by b and changed the sign", ex(-1 / key)),
                    Mis("divided the constant term by the coefficient of y and stopped",
                        ex(Cc / Bc))]
        P = {"kind": "le2_intercepts", "mode": mode, "A": [Ac.numerator, Ac.denominator],
             "B": [Bc.numerator, Bc.denominator], "C": [Cc.numerator, Cc.denominator]}
        choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True,
                                                 fillers="shift")
        return Item("le2.intercepts", "the intercepts of a line", "hard", seed, stem,
                    "mcq", keyx, letter, why, choices, reasons, latex, params=P)

    # mode == "graph_point": read the y-intercept off a drawn line
    M = q(m) if m is not None else Q(rng.randint(1, 6), rng.choice([1, 2, 4, 5]))
    Bv = q(b) if b is not None else q(rng.choice([rng.randint(2, 12),
                                                  rng.randint(-12, -2)]))
    if M == 0 or Bv == 0:
        raise ItemError("the drawn line must slope and must miss the origin")
    den = M.denominator
    lo, hi = 0, den * rng.randint(2, 4)
    ys = [M * lo + Bv, M * hi + Bv]
    if any(v.denominator != 1 for v in ys):
        raise ItemError("the drawn line must pass through lattice points")
    ylo, yhi = min(int(ys[0]), int(ys[1]), 0), max(int(ys[0]), int(ys[1]), 0)
    if hi - lo > 20 or yhi - ylo > 20:
        raise ItemError("the drawn line would not fit a readable grid")
    fig = coordinate_grid(lo, hi + 1, ylo - 1, yhi + 1,
                          segments=[((lo, int(ys[0])), (hi, int(ys[1])))])
    stem = "What is the y-intercept of the line graphed?"
    why = ("The y-intercept is the point where the drawn line crosses the vertical "
           "axis, and the first coordinate of any such point is zero.")
    key = point_text(0, Bv)
    ks = sig("pt", 0, Bv)
    wrong = [Mis("changed the sign of the value read off the axis",
                 (point_text(0, -Bv), sig("pt", 0, -Bv))),
             Mis("inverted the value read off the axis",
                 (point_text(0, -1 / Bv), sig("pt", 0, -1 / Bv))),
             Mis("gave the origin rather than the point where the line meets the "
                 "vertical axis", (point_text(0, 0), sig("pt", 0, 0))),
             Mis("wrote the value read off the vertical axis as an x-coordinate",
                 (point_text(Bv, 0), sig("pt", Bv, 0)))]
    P = {"kind": "le2_intercepts", "mode": mode, "m": [M.numerator, M.denominator],
         "b": [Bv.numerator, Bv.denominator],
         "seg": [[lo, int(ys[0])], [hi, int(ys[1])]]}
    return text_item("le2.intercepts", "the intercepts of a line", "easy", seed, stem,
                     key, ks, wrong, rng, P, why, figure=fig)


# -------------------------------------------- two equations, one same line

def _rterm(coef, var: str = "r") -> str:
    """The source's layout for a multiple of r: 'r/5', '-(3r)/2', '2r', '-r'."""
    coef = q(coef)
    n, d = abs(coef.numerator), coef.denominator
    sign = "-" if coef < 0 else ""
    body = var if n == 1 else f"{n}{var}"
    if d == 1:
        return f"{sign}{body}"
    return f"{sign}{body}/{d}" if n == 1 else f"{sign}({body})/{d}"


def equivalent_system(rng: random.Random, seed: int, *, a=None, b=None, c=None,
                      k=None) -> Item:
    """Two equations of one line, and the point that solves both for every r."""
    A = q(a) if a is not None else q(rng.randint(2, 9))
    B = q(b) if b is not None else q(rng.randint(2, 9))
    C = q(c) if c is not None else q(rng.randint(2, 40))
    K = q(k) if k is not None else q(rng.randint(2, 9))
    if A == 0 or B == 0 or A == B or K < 2:
        raise ItemError("the second equation must be a genuine multiple of the first")
    if gcd(gcd(int(A), int(B)), int(C)) != 1:
        raise ItemError("the first equation must already be in lowest terms, or the "
                        "multiplier between the two is ambiguous")
    eq1 = std_text(A, B, C, "x", "y")
    eq2 = std_text(K * A, K * B, K * C, "x", "y")
    stem = (eq1 + "\n" + eq2 + "\nFor each real number r, which of the following points "
            "lies on the graph of each equation in the xy-plane for the given system?")
    xr, xc = -B / A, C / A
    yr, yc = -A / B, C / B
    key = f"({_rterm(xr)} + {numtext(xc)}, r)"
    ks = sig("x_first", xr, xc)
    wrong = [Mis("solved for y but kept the sign of the x term, which changes the line",
                 (f"(r, {_rterm(-yr)} + {numtext(yc)})", sig("y_first", -yr, yc))),
             Mis("solved the equation for x but wrote that expression as the "
                 "y-coordinate", (f"(r, {_rterm(xr)} + {numtext(xc)})",
                                  sig("y_first", xr, xc))),
             Mis("divided r by the multiplier between the two equations and used the "
                 "two right-hand sides as the shifts",
                 (f"({_rterm(1 / K)} + {numtext(C)}, {_rterm(-1 / K)} + "
                  f"{numtext(K * C)})", sig("scaled", 1 / K, C, K * C))),
             Mis("solved for y correctly but for the second equation's right-hand side",
                 (f"(r, {_rterm(yr)} + {numtext(K * C / B)})",
                  sig("y_first", yr, K * C / B)))]
    P = {"kind": "le2_equivalent", "a": [A.numerator, A.denominator],
         "b": [B.numerator, B.denominator], "c": [C.numerator, C.denominator],
         "k": [K.numerator, K.denominator]}
    why = (f"The second equation is the first multiplied by {numtext(K)}, so the two "
           f"draw the same line and any point on it will do. Letting y be r and solving "
           f"{eq1} for x gives every such point at once.")
    return text_item("le2.equivalent_system", "a system of one line written twice",
                     "hard", seed, stem, key, ks, wrong, rng, P, why)
