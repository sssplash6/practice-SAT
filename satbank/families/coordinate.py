"""Coordinate-plane geometry: the figure carries the parameters.

Each generator draws its own grid from the same numbers that produce the key,
so a variation changes the picture as well as the words.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction

from ..exact import E, PI, Exact
from ..figures import coordinate_grid
from ..item import Item, ItemError, Mis, assemble
from ..shapes import UNITS

__all__ = ["circle_from_points", "triangle_from_points", "square_on_axes", "leg_from_area"]


def _window(pts, pad=2):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(0, min(xs)) - pad, max(xs) + pad, min(0, min(ys)) - pad, max(ys) + pad)


# ---------------------------------------------------- circle through 3 points

CIRCLE_STEMS = [
    "The three points shown define a circle. The {measure} of this circle is k*pi, where k "
    "is a constant. What is the value of k?",
    "A circle in the xy-plane passes through the three points shown. The {measure} of the "
    "circle is k*pi, where k is a constant. What is the value of k?",
    "The three points shown lie on a circle. If the {measure} of the circle is k*pi, what is "
    "the value of k?",
]


def circle_from_points(rng: random.Random, seed: int, *, fmt=None, r=None,
                       center=None, ask=None) -> Item:
    """Three points fix a circle; the answer is its circumference as k*pi.

    The source builds these the same way every time: two points are the ends of
    a vertical diameter and the third is the horizontal extreme, so k = 2r.
    """
    fmt = fmt or rng.choice(["mcq", "spr"])
    r = r or rng.randint(2, 7)
    ask = ask or ("circumference" if rng.random() < 0.7 else "area")
    cx, cy = center or (rng.randint(r, 11), rng.randint(r + 1, 13))
    pts = [(cx, cy + r), (cx, cy - r), (cx - r, cy)]
    rng.shuffle(pts)
    key = E(2 * r) if ask == "circumference" else E(r * r)
    xmin, xmax, ymin, ymax = _window(pts)
    stem = rng.choice(CIRCLE_STEMS).format(measure=ask)
    fig = coordinate_grid(max(0, xmin), xmax, max(0, ymin), ymax, points=pts)
    P = {"kind": "circle_3pt", "r": r, "ask": ask, "center": (cx, cy)}
    formula = "C = 2*pi*r" if ask == "circumference" else "A = pi*r^2"
    rationale = (f"The points lie on a circle centered at ({cx}, {cy}) with radius {r}, so "
                 f"{formula} gives k = {key.plain()}.")
    other = E(r * r) if ask == "circumference" else E(2 * r)
    mistakes = [Mis("gave the radius instead", E(r)),
                Mis(f"used the {'area' if ask == 'circumference' else 'circumference'} "
                    f"coefficient instead", other),
                Mis("doubled the correct value", key * E(2)),
                Mis("miscounted the radius by one grid square",
                    E(2 * (r + 1)) if ask == "circumference" else E((r + 1) ** 2))]
    if fmt == "spr":
        return Item("GEO.coord.circle_3pt", "circles in the plane", "medium", seed, stem,
                    "spr", key, key.gridin(), rationale, figure=fig, params=P)
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("GEO.coord.circle_3pt", "circles in the plane", "medium", seed, stem, "mcq",
                key, letter, rationale, choices, reasons, latex, figure=fig, params=P)


# ------------------------------------------------------- triangle from points

def triangle_from_points(rng: random.Random, seed: int, *, fmt=None, pts=None) -> Item:
    fmt = fmt or rng.choice(["spr", "mcq"])
    given = pts
    for _ in range(200):
        pts = given or [(rng.randint(-5, 7), rng.randint(-4, 10)) for _ in range(3)]
        (x1, y1), (x2, y2), (x3, y3) = pts
        cross = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
        if given:
            if cross == 0:
                raise ItemError("given points are collinear")
            break
        if cross == 0 or len(set(pts)) < 3:
            continue
        if min(abs(x2 - x1), abs(x3 - x1)) < 2 or abs(cross) < 8:
            continue
        break
    else:
        raise ItemError("no non-degenerate triangle found")

    P = {"kind": "triangle_area", "pts": [(x1, y1), (x2, y2), (x3, y3)]}
    key = E(Fraction(abs(cross), 2))
    box = E((max(x1, x2, x3) - min(x1, x2, x3)) * (max(y1, y2, y3) - min(y1, y2, y3)))
    xmin, xmax, ymin, ymax = _window(pts, pad=1)
    stem = rng.choice([
        "What is the area, in square units, of the triangle formed by connecting the three "
        "points shown?",
        "The three points shown are the vertices of a triangle. What is the area, in square "
        "units, of that triangle?",
        "In the xy-plane shown, a triangle has vertices at the three points shown. What is the "
        "area, in square units, of the triangle?",
    ])
    fig = coordinate_grid(xmin, xmax, ymin, ymax, points=pts, step=1 if xmax - xmin < 9 else 2)
    rationale = (f"With vertices ({x1}, {y1}), ({x2}, {y2}) and ({x3}, {y3}), the area is "
                 f"|{cross}|/2 = {key.plain()}.")
    mistakes = [Mis("omitted the one half", key * E(2)),
                Mis("found the area of the bounding rectangle", box),
                Mis("halved twice", key / E(2)),
                Mis("subtracted the bounding rectangle from the triangle", box - key)]
    if fmt == "spr":
        return Item("GEO.coord.triangle_area", "area in the plane", "hard", seed, stem, "spr",
                    key, key.gridin(), rationale, figure=fig, params=P)
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("GEO.coord.triangle_area", "area in the plane", "hard", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex, figure=fig, params=P)


# --------------------------------------------------- square with axis diagonals

def square_on_axes(rng: random.Random, seed: int, *, fmt="mcq", a=None, b=None,
                   ask=None, center=None) -> Item:
    """A quadrilateral whose diagonals lie along (or parallel to) the axes.

    Half-diagonals a and b give area 2ab and side sqrt(a^2 + b^2). Equal
    half-diagonals make it a square, unequal ones a rhombus -- the same
    construction, and the same mistakes, across both.
    """
    a = a or rng.randint(2, 9)
    if b is None:
        b = a if rng.random() < 0.45 else rng.choice([v for v in range(2, 10) if v != a])
    cx, cy = center if center is not None else (
        (0, 0) if rng.random() < 0.5 else (rng.randint(-3, 4), rng.randint(-3, 4)))
    ask = ask or rng.choices(["area", "side", "perimeter"], weights=[6, 2, 2])[0]
    square = (a == b)
    noun = "square" if square else "rhombus"

    side = E(1, 0, a * a + b * b)                     # sqrt(a^2 + b^2)
    key = {"area": E(2 * a * b), "side": side, "perimeter": E(4) * side}[ask]
    if fmt == "spr" and not key.is_rational:
        raise ItemError("a radical answer cannot be entered in a grid-in")

    verts = [(cx + a, cy), (cx, cy + b), (cx - a, cy), (cx, cy - b)]
    segs = [(verts[i], verts[(i + 1) % 4]) for i in range(4)]
    pad = 2
    fig = coordinate_grid(min(0, cx - a) - pad, max(0, cx + a) + pad,
                          min(0, cy - b) - pad, max(0, cy + b) + pad,
                          segments=segs, step=1 if max(a, b) + abs(cx) + abs(cy) < 9 else 2)

    where = ("has its diagonals on the x- and y-axes" if (cx, cy) == (0, 0)
             else "has its diagonals parallel to the x- and y-axes")
    asked = {"area": "the area, in square units,", "side": "the length, in units, of one side of",
             "perimeter": "the perimeter, in units, of"}[ask]
    stem = rng.choice([
        f"In the xy-plane shown, {noun} ABCD {where}. What is {asked} the {noun}?",
        f"The {noun} shown in the xy-plane {where}. What is {asked} the {noun}?",
        f"In the xy-plane shown, the vertices of a {noun} are the four points shown. "
        f"What is {asked} the {noun}?",
    ])

    if ask == "area":
        mistakes = [Mis("used the half-diagonals as the side lengths", E(a * b)),
                    Mis("multiplied the full diagonals without halving", E(4 * a * b)),
                    Mis("added the diagonals instead of multiplying", E(2 * (a + b))),
                    Mis("used one diagonal only", E(2 * max(a, b)))]
        rationale = (f"The diagonals have lengths {2*a} and {2*b}, and a {noun} with diagonals "
                     f"p and q has area pq/2 = {2*a}({2*b})/2 = {key.plain()}.")
    elif ask == "side":
        mistakes = [Mis("added the half-diagonals instead of using the Pythagorean theorem",
                        E(a + b)),
                    Mis("used a full diagonal as the side", E(2) * side),
                    Mis("gave the area instead of a side", E(2 * a * b)),
                    Mis("halved the side", side / E(2))]
        rationale = (f"Half of each diagonal is {a} and {b}, so a side is "
                     f"sqrt({a}^2 + {b}^2) = {side.plain()}.")
    else:
        mistakes = [Mis("gave one side instead of the perimeter", side),
                    Mis("used two sides only", E(2) * side),
                    Mis("added the four half-diagonals", E(2 * (a + b))),
                    Mis("gave the area instead of the perimeter", E(2 * a * b))]
        rationale = (f"Each side is sqrt({a}^2 + {b}^2) = {side.plain()}, so the perimeter is "
                     f"4({side.plain()}) = {key.plain()}.")

    P = {"kind": "square_diagonals", "a": a, "b": b, "ask": ask}
    if fmt == "spr":
        return Item("GEO.coord.quad_diagonals", "area in the plane", "medium", seed, stem,
                    "spr", key, key.gridin(), rationale, figure=fig, params=P)
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("GEO.coord.quad_diagonals", "area in the plane", "medium", seed, stem, "mcq",
                key, letter, rationale, choices, reasons, latex, figure=fig, params=P)


# ------------------------------------------------- right triangle leg from area

def leg_from_area(rng: random.Random, seed: int, *, fmt="mcq", dx=None, dy=None,
                  other=None) -> Item:
    """A drawn segment is one leg; the area is given; find the other leg.

    The drawn leg is usually irrational, which is what makes the item hard --
    the radical has to survive the division rather than be approximated.
    """
    gdx, gdy, gother = dx, dy, other
    for _ in range(200):
        dx, dy = (gdx, gdy) if gdx else (rng.randint(2, 9), rng.randint(2, 9))
        leg1 = E(1, 0, dx * dx + dy * dy)            # sqrt(dx^2 + dy^2), simplified
        other = E(gother) if gother else E(rng.choice([6, 8, 10, 12, 14, 16, 18, 20, 24]))
        area = leg1 * other / E(2)
        if gdx:
            break
        if leg1.rad == 1 or area.coef.denominator != 1:
            continue                                  # keep the radical, keep it tidy
        break
    else:
        raise ItemError("no tidy leg/area pair found")

    P = {"kind": "leg_from_area", "dx": dx, "dy": dy, "other": float(other),
         "area": float(area)}
    x1, y1 = rng.randint(-7, 0), rng.randint(2, 5)
    x2, y2 = x1 + dx, y1 + dy
    key = other
    fig = coordinate_grid(min(x1, -8), max(x2 + 1, 8), 0, max(y2 + 2, 10),
                          segments=[((x1, y1), (x2, y2))])
    stem = (f"The line segment shown in the xy-plane represents one of the legs of a right "
            f"triangle. The area of this triangle is {area.plain()} square units. What is the "
            f"length, in units, of the other leg of this triangle?")
    rationale = (f"The drawn leg has length √({dx}² + {dy}²) = {leg1.plain()}. "
                 f"From A = ½(leg₁)(leg₂): leg₂ = 2({area.plain()})/{leg1.plain()} "
                 f"= {key.plain()}.")
    mistakes = [Mis("divided the area by the leg without doubling", key / E(2)),
                Mis("gave the length of the drawn leg", leg1),
                Mis("halved the area instead of doubling it", area / E(2)),
                Mis("used the horizontal run as the drawn leg", E(2) * area / E(dx)),
                Mis("used the vertical rise as the drawn leg", E(2) * area / E(dy))]
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("GEO.coord.leg_from_area", "right triangles in the plane", "hard", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex, figure=fig, params=P)
