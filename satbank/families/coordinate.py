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
                    "spr", key, key.gridin(), rationale, figure=fig)
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("GEO.coord.circle_3pt", "circles in the plane", "medium", seed, stem, "mcq",
                key, letter, rationale, choices, reasons, latex, figure=fig)


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
                    key, key.gridin(), rationale, figure=fig)
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("GEO.coord.triangle_area", "area in the plane", "hard", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex, figure=fig)


# --------------------------------------------------- square with axis diagonals

def square_on_axes(rng: random.Random, seed: int, *, fmt="mcq", a=None) -> Item:
    """Vertices at (+-a, 0) and (0, +-a): the diagonals are 2a, so the area is 2a^2."""
    a = a or rng.randint(2, 9)
    key = E(2 * a * a)
    pts = [(a, 0), (-a, 0), (0, a), (0, -a)]
    segs = [((a, 0), (0, a)), ((0, a), (-a, 0)), ((-a, 0), (0, -a)), ((0, -a), (a, 0))]
    fig = coordinate_grid(-a - 2, a + 2, -a - 2, a + 2, segments=segs, step=1)
    stem = rng.choice([
        "In the xy-plane shown, square ABCD has its diagonals on the x- and y-axes. What is "
        "the area, in square units, of the square?",
        "The square shown in the xy-plane has its two diagonals lying along the coordinate "
        "axes. What is the area, in square units, of the square?",
        "In the xy-plane shown, the vertices of a square lie on the x- and y-axes. What is the "
        "area, in square units, of the square?",
    ])
    rationale = (f"Each diagonal has length {2*a}, and a square with diagonal d has area "
                 f"d²/2 = {2*a}²/2 = {key.plain()}.")
    mistakes = [Mis("used the half-diagonal as the side length", E(a * a)),
                Mis("squared the full diagonal", E(4 * a * a)),
                Mis("found the perimeter of the bounding square", E(4 * a)),
                Mis("used the diagonal as the side length", E(2 * a))]
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("GEO.coord.square_diagonals", "area in the plane", "medium", seed, stem, "mcq",
                key, letter, rationale, choices, reasons, latex, figure=fig)


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
                "mcq", key, letter, rationale, choices, reasons, latex, figure=fig)
