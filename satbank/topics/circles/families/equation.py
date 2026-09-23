"""The circle in the xy-plane: its equation, and the points around it.

Everything an SAT item asks about a circle's equation is one of four moves --
read the center and radius out of it, write it down from them, test a point
against it, or move the circle and write it down again -- so the templates are
grouped by the move rather than by the surface the answer happens to have.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction as F

from ....exact import E, Exact
from ....item import Item, ItemError, Mis, assemble, assemble_text, gridin_mistakes
from ..figures import circle_on_grid
from ....expr import sign_join
from ..render import (MINUS, coef_term, general_equation, num, point, radical,
                      standard_equation)

__all__ = ["equation_read", "equation_write", "point_on", "interior",
           "tangent_slope", "transform"]


def _sign_safe(key: Exact, mistakes: list[Mis]) -> list[Mis]:
    """Put a same-signed distractor first.

    Options are chosen by their algebraic form, which ignores the sign, so a
    negative key can end up the only negative option on the page -- crossable
    off without doing any algebra. This makes sure it is not.
    """
    neg = float(key) < 0
    same = [m for m in mistakes if m.value is not None and (float(m.value) < 0) == neg]
    if not same:
        return mistakes
    rest = [m for m in mistakes if m is not same[0]]
    return [same[0]] + rest


def _frac(v) -> F:
    """A center coordinate, given either as a number or as a (numerator,
    denominator) pair -- the source puts half-integers at the center whenever
    it prints a common factor in front of the squares."""
    return F(*v) if isinstance(v, (tuple, list)) else F(v)


def _readable(key: Exact) -> Exact:
    """Reject a key the unsimplified-radical rendering would disguise.

    `radical` prints 2*sqrt(10) as sqrt(40), which is what the source does, but
    the shared audit reads an option back either as exactly `key.plain()` or as
    a float. Keys that survive both spellings are the only ones shipped.
    """
    if radical(key) != key.plain():
        raise ItemError("this radius cannot be printed as an unsimplified root")
    return key


def _root(n) -> Exact:
    """The exact square root of a non-negative rational."""
    if n < 0:
        raise ItemError("a circle needs a positive radius")
    return E(1, 0, F(n))


# ------------------------------------------------- reading off an equation

def equation_read(rng: random.Random, seed: int, *, form=None, h=None, k=None,
                  r2=None, lead=None, u=None, v=None, n=None, sym="p", ask=None,
                  fmt=None, display=None) -> Item:
    """Centre or radius, out of an equation in whatever form it is printed.

    The four forms are the four the source uses: already completed, a general
    form with the squares left to complete, the same with a common factor in
    front, and the same again with the coefficients carrying a constant.
    """
    form = form or rng.choice(["standard", "standard", "general", "general", "scaled",
                              "symbolic"])
    ask = ask or rng.choice(["radius", "center", "center", "diameter"])
    if form == "symbolic":
        ask = "radius"
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    display = rng.choice([True, False]) if display is None else display

    if form == "symbolic":
        lead = lead or rng.randint(1, 12)
        u = u if u is not None else rng.choice([i for i in range(-9, 10) if i])
        v = v if v is not None else rng.choice([i for i in range(-9, 10) if i])
        n = n or rng.randint(1, 12)
        d, e = 2 * lead * u, 2 * lead * v
        rhs = lead * (n * n - u * u - v * v)
        eq = general_equation(lead, d, e, rhs, sym=sym)
        key = E(n)
        mistakes = [
            Mis("gave the square of the radius coefficient", E(n * n)),
            Mis("read the coefficient off the x-term of the equation", E(abs(u))),
            Mis("read the coefficient off the y-term of the equation", E(abs(v))),
            Mis("gave the coefficient of the diameter", E(2 * n)),
            Mis("added the two center coefficients", E(abs(u) + abs(v))),
        ]
        stem = (f"{eq}\nIn the xy-plane, the graph of the given equation is a circle. The "
                f"length of the radius of the circle is n{sym}, where n and {sym} are positive "
                f"constants. What is the value of n?")
        rationale = (f"Dividing by {lead} and completing both squares gives a radius of "
                     f"{n}{sym}, so n = {n}.")
        P = {"kind": "circles_equation_read", "form": form, "lead": lead, "d": d, "e": e,
             "rhs": rhs, "ask": "radius", "symbolic": True}
        if fmt == "spr":
            return Item("circles.equation_read", "the equation of a circle", "hard", seed,
                        stem, "spr", key, key.gridin(), rationale, params=P,
                        spr_mistakes=gridin_mistakes(key, mistakes))
        choices, latex, reasons, letter = assemble(key, mistakes, rng, fmt_value=radical)
        return Item("circles.equation_read", "the equation of a circle", "hard", seed, stem,
                    "mcq", key, letter, rationale, choices, reasons, latex, params=P)

    lead = lead or (rng.choice([2, 3, 4, 5]) if form == "scaled" else 1)
    if form == "scaled":
        half = rng.random() < 0.5
        h = _frac(h) if h is not None else F(rng.randint(-24, 24) * 2 + (1 if half else 0), 2)
        k = _frac(k) if k is not None else F(rng.randint(-24, 24) * 2 + (1 if half else 0), 2)
    else:
        h = _frac(h) if h is not None else F(rng.randint(-30, 30))
        k = _frac(k) if k is not None else F(rng.randint(-30, 30))
    if r2 is None:
        r2 = F(rng.choice([1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225]))
    r2 = F(r2)
    d, e = -2 * lead * h, -2 * lead * k
    rhs = lead * (r2 - h * h - k * k)
    if d.denominator != 1 or e.denominator != 1 or rhs.denominator != 1:
        raise ItemError("this center does not give whole-number coefficients")
    eq = (standard_equation(h, k, str(r2)) if form == "standard"
          else general_equation(lead, d, e, rhs))
    radius = _root(r2)

    if ask == "center":
        key_text = point(h, k)
        swap_first = h == 0 or k == 0
        flips = [
            Mis("read the center straight out of the equation without changing either sign",
                point(-h, -k)),
            Mis("changed the sign for y but not for x", point(-h, k)),
            Mis("changed the sign for x but not for y", point(h, -k)),
        ]
        if form == "standard":
            wrong = flips + [Mis("swapped the two coordinates", point(k, h))]
        else:
            raw = [Mis("used the coefficients themselves instead of half of them",
                       point(2 * h, 2 * k)),
                   Mis("used the coefficients and did not change the sign",
                       point(-2 * h, -2 * k))]
            swap = [Mis("swapped the two coordinates", point(k, h)),
                    Mis("swapped the coordinates and did not change the sign",
                        point(-k, -h))]
            wrong = flips[:1] + (swap + raw if swap_first else raw + swap) + flips[1:]
        body = rng.choice([
            "In the xy-plane, the graph of the given equation is a circle. What are the "
            "coordinates (x, y) of the center of the circle?",
            "The equation above defines a circle in the xy-plane. What are the coordinates "
            "of the center of the circle?",
        ]) if display else rng.choice([
            f"What is the center of the circle in the xy-plane defined by the equation {eq}?",
            f"In the xy-plane, the graph of {eq} is a circle. What is the center of the "
            f"circle?",
        ])
        stem = f"{eq}\n{body}" if display else body
        rationale = (f"Completing both squares puts the equation in the form "
                     f"{standard_equation(h, k, str(r2))}, so the center is {key_text}.")
        P = {"kind": "circles_equation_read", "form": form, "lead": lead, "d": int(d),
             "e": int(e), "rhs": int(rhs), "ask": "center", "symbolic": False}
        choices, reasons, letter = assemble_text(key_text, wrong, rng)
        return Item("circles.equation_read", "the equation of a circle", "medium", seed,
                    stem, "mcq", E(0), letter, rationale, choices, reasons, choices,
                    params=P)

    key = _readable(radius if ask == "radius" else E(2) * radius)
    noun = "radius" if ask == "radius" else "diameter"
    mistakes = [
        Mis(f"gave the square of the radius instead of the {noun}", E(r2)),
        Mis(f"read the {noun} off the x-coordinate of the center", E(abs(h))),
        Mis(f"read the {noun} off the y-coordinate of the center", E(abs(k))),
        Mis("gave the diameter instead of the radius" if ask == "radius"
            else "gave the radius instead of the diameter",
            radius * E(2) if ask == "radius" else radius),
    ]
    if form == "scaled":
        # the constant is only the square of the radius after dividing through
        mistakes = [
            Mis(f"gave the square of the radius instead of the {noun}", E(r2)),
            Mis("completed the square without first dividing by the leading coefficient",
                _root(rhs + lead * (h * h + k * k))),
            Mis("moved the completing constants to the wrong side of the equation",
                _root(rhs - lead * (h * h + k * k)) if rhs > lead * (h * h + k * k)
                else None),
        ]
    elif form == "general" and rhs > 0:
        mistakes.insert(1, Mis("took the number on the right as the square of the radius, "
                               "without completing the square", _root(rhs)))
    mistakes = [m for m in mistakes if m.value is not None]
    body = rng.choice([
        f"The graph of the given equation in the xy-plane is a circle. What is the length of "
        f"the {noun} of this circle?",
        f"In the xy-plane, the graph of the given equation is a circle. What is the {noun} of "
        f"the circle?",
    ]) if display else rng.choice([
        f"The equation {eq} defines a circle in the xy-plane. What is the {noun} of the "
        f"circle?",
        f"In the xy-plane, the graph of {eq} is a circle. What is the {noun} of the circle?",
    ])
    stem = f"{eq}\n{body}" if display else body
    rationale = (f"Completing both squares gives {standard_equation(h, k, str(r2))}, so the "
                 f"{noun} is {key.plain()}.")
    P = {"kind": "circles_equation_read", "form": form, "lead": lead, "d": int(d),
         "e": int(e), "rhs": int(rhs), "ask": ask, "symbolic": False}
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("an irrational radius cannot be entered in a grid-in")
        return Item("circles.equation_read", "the equation of a circle", "medium", seed,
                    stem, "spr", key, key.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble(key, mistakes, rng, fmt_value=radical)
    return Item("circles.equation_read", "the equation of a circle", "medium", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex, params=P)


# --------------------------------------------------- writing the equation down

def equation_write(rng: random.Random, seed: int, *, h=None, k=None, r=None,
                   on=None, sym=None, mult=None, ask=None, coef=None, fmt=None) -> Item:
    """From a center and a size to the equation, or to one of its coefficients."""
    h = F(h) if h is not None else F(rng.randint(-20, 20))
    k = F(k) if k is not None else F(rng.randint(-20, 20))
    ask = ask or rng.choice(["equation", "equation", "coefficient"])
    if sym:
        ask = "equation"
    fmt = fmt or ("spr" if rng.random() < 0.4 else "mcq")

    whole_r = None
    if sym:
        mult = mult or rng.randint(2, 12)
        r2, rhs, rhs_plain = None, f"{mult * mult}{sym}²", f"{mult}{sym}"
        size = f"a radius of {mult}{sym}"
    elif on is not None:
        px, py = on
        r2 = F(px - h) ** 2 + F(py - k) ** 2
        if r2 == 0:
            raise ItemError("the given point is the center")
        root = _root(r2)
        rhs, rhs_plain = str(r2), root.plain()
        whole_r = F(root.coef) if root.is_rational else None
        size = f"the point {point(px, py)} lies on the circle"
    else:
        whole_r = F(r) if r is not None else F(rng.randint(1, 20))
        r2 = whole_r * whole_r
        rhs, rhs_plain = str(r2), str(whole_r)
        size = f"a radius of {whole_r}"

    if ask == "equation":
        key_text = standard_equation(h, k, rhs)
        if sym:
            wrong = [
                Mis("squared only the number in the radius, not the whole radius",
                    standard_equation(h, k, f"{mult * mult}{sym}")),
                Mis("used the radius itself instead of its square",
                    standard_equation(h, k, f"{mult}{sym}")),
                Mis("squared only the letter in the radius",
                    standard_equation(h, k, f"{mult}{sym}²")),
            ]
        else:
            wrong = [
                Mis("kept the signs of the center's coordinates instead of changing them",
                    standard_equation(-h, -k, rhs)),
                Mis("used the radius itself instead of its square",
                    standard_equation(h, k, rhs_plain)),
                Mis("kept the signs of the center and used the radius instead of its square",
                    standard_equation(-h, -k, rhs_plain)),
                Mis("doubled the radius instead of squaring it",
                    standard_equation(h, k, str(2 * whole_r)) if whole_r else None),
            ]
        if on is not None:
            stem = (f"A circle in the xy-plane has its center at {point(h, k)} and "
                    f"{size}. Which equation represents this circle?")
            rationale = (f"The radius is the distance from {point(h, k)} to "
                         f"{point(on[0], on[1])}, so r² = {rhs} and the equation is "
                         f"{key_text}.")
        else:
            stem = rng.choice([
                f"In the xy-plane, a circle with {size} has center {point(h, k)}. Which of "
                f"the following is an equation of the circle?",
                f"A circle in the xy-plane has its center at {point(h, k)} and has "
                f"{size}. Which equation represents this circle?",
            ])
            rationale = (f"A circle with center (h, k) and radius r has equation "
                         f"(x {MINUS} h)² + (y {MINUS} k)² = r², which gives {key_text}.")
        P = {"kind": "circles_equation_write", "h": [h.numerator, h.denominator],
             "k": [k.numerator, k.denominator], "ask": "equation", "sym": sym or "",
             "mult": mult, "r2": None if r2 is None else [r2.numerator, r2.denominator]}
        choices, reasons, letter = assemble_text(key_text, wrong, rng)
        return Item("circles.equation_write", "the equation of a circle", "medium", seed,
                    stem, "mcq", E(0), letter, rationale, choices, reasons, choices,
                    params=P)

    coef = coef or rng.choice(["a", "b", "c"])
    a_, b_, c_ = -2 * h, -2 * k, h * h + k * k - r2
    key = E({"a": a_, "b": b_, "c": c_}[coef])
    if coef == "c":
        mistakes = [
            Mis("subtracted the square of the radius twice", E(c_ - r2)),
            Mis("added the square of the radius instead of subtracting it",
                E(h * h + k * k + r2)),
            Mis("took the subtraction the wrong way round", E(r2 - h * h - k * k)),
            Mis("left the radius out of the constant term", E(h * h + k * k)),
            Mis("subtracted the radius instead of its square",
                E(h * h + k * k - whole_r) if whole_r else None),
        ]
    else:
        base = h if coef == "a" else k
        mistakes = [
            Mis("did not change the sign when expanding the square", E(2 * base)),
            Mis("forgot to double the coordinate", E(-base)),
            Mis("squared the coordinate instead of doubling it", E(base * base)),
            Mis("used the other coordinate of the center",
                E(-2 * (k if coef == "a" else h))),
        ]
    stem = (f"A circle in the xy-plane has its center at {point(h, k)} and has {size}. An "
            f"equation of this circle is x² + y² + ax + by + c = 0, where a, b, and "
            f"c are constants. What is the value of {coef}?")
    expanded = sign_join([t for t in ("x²", "y²", coef_term(a_, "x"),
                                      coef_term(b_, "y"), coef_term(c_, "")) if t])
    rationale = (f"Expanding {standard_equation(h, k, rhs)} gives {expanded} = 0, so "
                 f"{coef} = {key.plain()}.")
    P = {"kind": "circles_equation_write", "h": [h.numerator, h.denominator],
         "k": [k.numerator, k.denominator], "r2": [r2.numerator, r2.denominator],
         "ask": "coefficient", "coef": coef}
    if fmt == "spr":
        return Item("circles.equation_write", "the equation of a circle", "hard", seed,
                    stem, "spr", key, key.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble(key, _sign_safe(key, mistakes), rng,
                                               signed=True, fillers="shift")
    return Item("circles.equation_write", "the equation of a circle", "hard", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex, params=P)


# ------------------------------------------------------- a point on the circle

def point_on(rng: random.Random, seed: int, *, mode=None, h=None, k=None, r=None,
             axis=None, side=None, dx=None, dy=None, fmt=None, labels=None) -> Item:
    """A point the circle passes through: the coordinate it forces, or the far
    end of the diameter through it."""
    mode = mode or rng.choice(["coordinate", "diameter"])
    h = int(h) if h is not None else rng.randint(-15, 15)
    k = int(k) if k is not None else rng.randint(-15, 15)
    r = int(r) if r is not None else rng.randint(2, 12)
    r2 = r * r

    if mode == "coordinate":
        axis = axis or rng.choice(["x", "y"])
        side = side or rng.choice([1, -1])
        fmt = fmt or ("spr" if rng.random() < 0.5 else "mcq")
        if axis == "x":
            shown, key, other = f"({num(h + side * r)}, c)", E(k), "y"
        else:
            shown, key, other = f"(c, {num(k + side * r)})", E(h), "x"
        eq = standard_equation(h, k, str(r2))
        mistakes = [
            Mis("added the radius to the center's coordinate", E((k if axis == 'x' else h) + r)),
            Mis("subtracted the radius from the center's coordinate",
                E((k if axis == 'x' else h) - r)),
            Mis("gave the other coordinate of the center", E(h if axis == "x" else k)),
            Mis("used the square of the radius in place of the radius",
                E((k if axis == 'x' else h) + r2)),
        ]
        stem = rng.choice([
            f"In the xy-plane, the graph of the equation {eq} is a circle. The point {shown}, "
            f"where c is a constant, lies on this circle. What is the value of c?",
            f"The graph of {eq} in the xy-plane is a circle, and the point {shown} lies on "
            f"this circle, where c is a constant. What is the value of c?",
        ])
        rationale = (f"The circle has center {point(h, k)} and radius {r}, so {shown} is the "
                     f"point where the circle is furthest in the {other}-direction; "
                     f"c = {key.plain()}.")
        P = {"kind": "circles_point_on", "mode": "coordinate", "h": h, "k": k, "r": r,
             "axis": axis, "side": side}
        if fmt == "spr":
            return Item("circles.point_on", "points on a circle", "medium", seed, stem,
                        "spr", key, key.gridin(), rationale, params=P,
                        spr_mistakes=gridin_mistakes(key, mistakes))
        choices, latex, reasons, letter = assemble(key, _sign_safe(key, mistakes), rng,
                                                   signed=True, fillers="shift")
        return Item("circles.point_on", "points on a circle", "medium", seed, stem, "mcq",
                    key, letter, rationale, choices, reasons, latex, params=P)

    p, q = labels or rng.choice([("P", "Q"), ("A", "B"), ("M", "N"), ("R", "S")])
    if dx is None or dy is None:
        dx, dy = rng.choice([(r, 0), (-r, 0), (0, r), (0, -r)])
    if dx * dx + dy * dy != r2:
        raise ItemError("the named point is not on the circle")
    eq = standard_equation(h, k, str(r2))
    key_text = point(h - dx, k - dy)
    wrong = [
        Mis(f"gave the center of the circle instead of the far end of {p}{q}",
            point(h, k)),
        Mis(f"measured one radius from the center at a right angle to {p}{q}",
            point(h - dy, k + dx)),
        Mis(f"measured one radius from the center the other way, at a right angle to {p}{q}",
            point(h + dy, k - dx)),
        Mis("changed the sign of one coordinate only", point(h - dx, k + dy)),
    ]
    stem = rng.choice([
        f"{eq}\nIn the xy-plane, the graph of the equation above is a circle. Point {p} is on "
        f"the circle and has coordinates {point(h + dx, k + dy)}. If {p}{q} is a diameter of "
        f"the circle, what are the coordinates of point {q} ?",
        f"In the xy-plane, the graph of {eq} is a circle. Point {p} lies on this circle at "
        f"{point(h + dx, k + dy)}, and {p}{q} is a diameter of the circle. What are the "
        f"coordinates of point {q} ?",
    ])
    rationale = (f"The center {point(h, k)} is the midpoint of {p}{q}, so {q} is as far the "
                 f"other side of it as {p}: {key_text}.")
    P = {"kind": "circles_point_on", "mode": "diameter", "h": h, "k": k, "r": r,
         "dx": dx, "dy": dy}
    choices, reasons, letter = assemble_text(key_text, wrong, rng)
    return Item("circles.point_on", "points on a circle", "hard", seed, stem, "mcq", E(0),
                letter, rationale, choices, reasons, choices, params=P)


# ------------------------------------------------------------ inside or outside

def interior(rng: random.Random, seed: int, *, h=None, k=None, r=None, out=None,
             far=None, sq=None) -> Item:
    """Three points inside and one outside, each inside one chosen for the
    particular test a student gets wrong."""
    h = int(h) if h is not None else rng.randint(-8, 8)
    k = int(k) if k is not None else rng.randint(-8, 8)
    r = int(r) if r is not None else rng.randint(4, 10)
    r2 = r * r

    def draw(pred):
        for _ in range(400):
            dx, dy = rng.randint(-r - 4, r + 4), rng.randint(-r - 4, r + 4)
            if pred(dx, dy):
                return dx, dy
        raise ItemError("no point meeting the condition was found")

    out = tuple(out) if out else draw(lambda a, b: a * a + b * b > r2)
    far = tuple(far) if far else draw(
        lambda a, b: 0 < a * a + b * b < r2 and max(abs(h + a), abs(k + b)) > r)
    sq = tuple(sq) if sq else draw(
        lambda a, b: r < a * a + b * b < r2 and (a, b) != far)
    if out[0] ** 2 + out[1] ** 2 <= r2:
        raise ItemError("the keyed point is not outside the circle")
    for off in (far, sq):
        if off[0] ** 2 + off[1] ** 2 >= r2:
            raise ItemError("a point meant to be inside the circle is not")

    eq = standard_equation(h, k, str(r2))
    key_text = point(h + out[0], k + out[1])
    wrong = [
        Mis("inside the circle: a student who compares the point's own coordinates with the "
            "radius, rather than its distance from the center, calls this one outside",
            point(h + far[0], k + far[1])),
        Mis("inside the circle: a student who compares the squared distance with the radius "
            "instead of with the square of the radius calls this one outside",
            point(h + sq[0], k + sq[1])),
        Mis("the center of the circle, which lies inside it", point(h, k)),
    ]
    stem = rng.choice([
        f"A circle in the xy-plane has equation {eq}. Which of the following points does NOT "
        f"lie in the interior of the circle?",
        f"In the xy-plane, a circle is defined by {eq}. Which of the following points does NOT "
        f"lie inside this circle?",
    ])
    away = out[0] ** 2 + out[1] ** 2
    rationale = (f"The circle has center {point(h, k)} and radius {r}. The squared distance "
                 f"from the center to {key_text} is {away}, which is more than "
                 f"{r}² = {r * r}, so that point lies outside the circle; for the other "
                 f"three the squared distance is less than {r * r}.")
    P = {"kind": "circles_interior", "h": h, "k": k, "r": r, "out": list(out),
         "far": list(far), "sq": list(sq)}
    choices, reasons, letter = assemble_text(key_text, wrong, rng)
    return Item("circles.interior", "points and a circle", "hard", seed, stem, "mcq", E(0),
                letter, rationale, choices, reasons, choices, params=P)


# --------------------------------------------------------------- the tangent

def tangent_slope(rng: random.Random, seed: int, *, h=None, k=None, dx=None, dy=None,
                  label=None, fmt="mcq") -> Item:
    """A tangent meets the radius at a right angle, so its slope is the
    negative reciprocal of the radius's."""
    h = int(h) if h is not None else rng.randint(-12, 12)
    k = int(k) if k is not None else rng.randint(-12, 12)
    lab = label or rng.choice(["k", "m", "n", "t", "p"])
    if dx is None or dy is None:
        for _ in range(200):
            dx, dy = rng.randint(-9, 9), rng.randint(-9, 9)
            if abs(dx) > 1 and abs(dy) > 1 and math.gcd(abs(dx), abs(dy)) == 1:
                break
        else:
            raise ItemError("no tidy radius direction found")
    if dy == 0:
        raise ItemError("the tangent there is vertical, so it has no slope")
    if dx == 0:
        raise ItemError("a horizontal tangent makes the item trivial")

    key = E(-F(dx, dy))
    mistakes = [
        Mis("gave the slope of the radius instead of the slope of the tangent", E(F(dy, dx))),
        Mis("changed the sign but did not take the reciprocal", E(-F(dy, dx))),
        Mis("took the reciprocal but did not change the sign", E(F(dx, dy))),
    ]
    stem = rng.choice([
        f"A circle in the xy-plane has its center at {point(h, k)}. Line {lab} is tangent to "
        f"this circle at the point {point(h + dx, k + dy)}. What is the slope of line {lab}?",
        f"In the xy-plane, line {lab} is tangent at {point(h + dx, k + dy)} to the circle with "
        f"center {point(h, k)}. What is the slope of line {lab}?",
    ])
    rationale = (f"The radius to {point(h + dx, k + dy)} has slope {num(F(dy, dx))}, and a "
                 f"tangent is perpendicular to the radius at the point of tangency, so its "
                 f"slope is {key.plain()}.")
    P = {"kind": "circles_tangent", "h": h, "k": k, "dx": dx, "dy": dy}
    choices, latex, reasons, letter = assemble(key, _sign_safe(key, mistakes), rng,
                                               signed=True, fillers="shift")
    return Item("circles.tangent_slope", "tangents to a circle", "hard", seed, stem, "mcq",
                key, letter, rationale, choices, reasons, latex, params=P)


# ---------------------------------------------------------- moving the circle

DIRECTIONS = {"right": (1, 0), "left": (-1, 0), "up": (0, 1), "down": (0, -1)}


def transform(rng: random.Random, seed: int, *, mode=None, h=None, k=None, r2=None,
              direction=None, shift=None, scale=None, ask=None, times=None,
              fmt=None, figure=None, names=None) -> Item:
    """Circle B out of circle A: slid along an axis, or grown from the same center."""
    mode = mode or rng.choice(["translate", "translate", "scale"])
    h = int(h) if h is not None else rng.randint(-12, 12)
    k = int(k) if k is not None else rng.randint(-12, 12)
    r2 = int(r2) if r2 is not None else rng.choice([1, 4, 7, 9, 11, 16, 25, 36, 49, 64])
    a_name, b_name = names or ("A", "B")
    eq_a = standard_equation(h, k, str(r2))

    if mode == "translate":
        direction = direction or rng.choice(list(DIRECTIONS))
        shift = int(shift) if shift is not None else rng.randint(2, 99)
        ux, uy = DIRECTIONS[direction]
        nh, nk = h + ux * shift, k + uy * shift
        ask = ask or rng.choice(["equation", "equation", "rhs"])
        if ask == "equation":
            key_text = standard_equation(nh, nk, str(r2))
            opp = {"right": "left", "left": "right", "up": "down", "down": "up"}[direction]
            other = ("up", "down") if direction in ("right", "left") else ("right", "left")
            wrong = [
                Mis(f"translated to the {opp} instead of to the {direction}",
                    standard_equation(h - ux * shift, k - uy * shift, str(r2))),
                Mis(f"translated {other[0]} instead of {direction}",
                    standard_equation(h + DIRECTIONS[other[0]][0] * shift,
                                      k + DIRECTIONS[other[0]][1] * shift, str(r2))),
                Mis(f"translated {other[1]} instead of {direction}",
                    standard_equation(h + DIRECTIONS[other[1]][0] * shift,
                                      k + DIRECTIONS[other[1]][1] * shift, str(r2))),
                Mis("changed the constant on the right by the distance translated",
                    standard_equation(nh, nk, str(r2 + shift))),
            ]
            stem = rng.choice([
                f"Circle {a_name} has equation {eq_a}. In the xy-plane, circle {b_name} is "
                f"obtained by translating circle {a_name} to the {direction} {shift} units. "
                f"Which equation represents circle {b_name}?",
                f"In the xy-plane, circle {a_name} is defined by {eq_a}. Circle {b_name} is "
                f"circle {a_name} translated {shift} units {direction}. Which equation "
                f"represents circle {b_name}?",
            ])
            rationale = (f"Translating {shift} units {direction} moves the center from "
                         f"{point(h, k)} to {point(nh, nk)} and leaves the radius alone, so "
                         f"circle {b_name} is {key_text}.")
            P = {"kind": "circles_transform", "mode": "translate", "h": h, "k": k,
                 "r2": r2, "dir": direction, "shift": shift, "ask": "equation"}
            choices, reasons, letter = assemble_text(key_text, wrong, rng)
            return Item("circles.transform", "transforming a circle", "hard", seed, stem,
                        "mcq", E(0), letter, rationale, choices, reasons, choices,
                        params=P)

        times = int(times) if times else rng.choice([1, 2, 3, 4])
        key = E(times * r2)
        fmt = fmt or ("spr" if rng.random() < 0.7 else "mcq")
        mistakes = [
            Mis("gave the constant itself rather than the multiple that was asked for",
                E(r2)),
            Mis("added the distance translated to the constant on the right",
                E(times * (r2 + shift))),
            Mis("multiplied the constant by the distance translated",
                E(times * r2 * shift)),
            Mis("used the radius rather than its square", E(times) * _root(r2)),
        ]
        asked = "a" if times == 1 else f"{times}a"
        fig = circle_on_grid(min(h - int(math.isqrt(r2)) - 3, -2),
                             max(h + int(math.isqrt(r2)) + 3, 2),
                             min(k - int(math.isqrt(r2)) - 3, -2),
                             max(k + int(math.isqrt(r2)) + 3, 2),
                             h, k, math.sqrt(r2)) if figure is not False else None
        stem = (f"Circle {a_name} shown is defined by the equation {eq_a}. Circle {b_name} "
                f"(not shown) has the same radius but is translated {shift} units to the "
                f"{direction}. If the equation of circle {b_name} is (x {MINUS} h)² + "
                f"(y {MINUS} k)² = a, where h, k, and a are constants, what is the value "
                f"of {asked}?")
        rationale = (f"A translation moves the center but not the radius, so a is still "
                     f"{r2} and {asked} = {key.plain()}.")
        P = {"kind": "circles_transform", "mode": "translate", "h": h, "k": k, "r2": r2,
             "dir": direction, "shift": shift, "ask": "rhs", "times": times}
        if fmt == "spr":
            return Item("circles.transform", "transforming a circle", "hard", seed, stem,
                        "spr", key, key.gridin(), rationale, figure=fig, params=P,
                        spr_mistakes=gridin_mistakes(key, mistakes))
        choices, latex, reasons, letter = assemble(key, mistakes, rng, fmt_value=radical)
        return Item("circles.transform", "transforming a circle", "hard", seed, stem, "mcq",
                    key, letter, rationale, choices, reasons, latex, figure=fig, params=P)

    scale = int(scale) if scale else rng.choice([2, 3, 4, 5])
    key = E(scale * scale * r2)
    fmt = fmt or ("spr" if rng.random() < 0.6 else "mcq")
    mistakes = [
        Mis("multiplied the constant by the scale factor instead of by its square",
            E(scale * r2)),
        Mis("left the constant unchanged", E(r2)),
        Mis("squared the diameter of the new circle instead of its radius",
            E(4 * scale * scale * r2)),
        Mis("added the scale factor to the constant", E(r2 + scale)),
    ]
    word = {2: "two times", 3: "three times", 4: "four times", 5: "five times"}[scale]
    stem = (f"Circle {a_name} in the xy-plane has the equation {eq_a}. Circle {b_name} has "
            f"the same center as circle {a_name}. The radius of circle {b_name} is {word} the "
            f"radius of circle {a_name}. The equation defining circle {b_name} in the "
            f"xy-plane is {standard_equation(h, k, 'k')}, where k is a constant. What is the "
            f"value of k?")
    rationale = (f"Circle {a_name} has radius {_root(r2).plain()}, so circle {b_name} has "
                 f"radius {(E(scale) * _root(r2)).plain()} and k is its square, "
                 f"{key.plain()}.")
    P = {"kind": "circles_transform", "mode": "scale", "h": h, "k": k, "r2": r2,
         "scale": scale, "ask": "rhs"}
    if fmt == "spr":
        return Item("circles.transform", "transforming a circle", "hard", seed, stem, "spr",
                    key, key.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble(key, mistakes, rng, fmt_value=radical)
    return Item("circles.transform", "transforming a circle", "hard", seed, stem, "mcq",
                key, letter, rationale, choices, reasons, latex, params=P)
