"""Independent re-derivation of every Circles answer.

Written from the geometry and the algebra, not from the generators: plain
floats and plain Fractions, no Exact, and nothing imported from the templates
except the two functions that decide how a point or an equation is spelled,
which are not mathematics. Where a template ran a formula forwards, this runs
it from the printed numbers instead -- the centre and radius are recovered by
completing the square from the coefficients the item actually prints, not from
the h, k and r the template started with, so a template that prints an
equation it did not mean cannot pass.
"""

from __future__ import annotations

import math
from fractions import Fraction as F

from ...audit import AuditError
from .render import point, standard_equation

TAU = 2.0 * math.pi


def supply_radius(p: dict) -> float:
    return p["pi_coefficient"] / 2.0


def supply_diameter(p: dict) -> float:
    return 2.0 * math.sqrt(p["area_pi_coefficient"])


# ------------------------------------------------------------------- arcs

def arc(p: dict) -> float:
    theta = p["theta"]
    if p["mode"] == "arc":
        return p["circumference"] * theta / 360.0
    return p["length"] * 360.0 / theta


def arc_pair(p: dict) -> float:
    if p["mode"] == "sum":
        return p["minor"] + p["major"]
    whole = p["given"] * 360.0 / p["theta"]
    return whole - p["given"]


def arc_fraction(p: dict) -> float:
    share = p["length"] / (TAU * p["r"])
    if abs(share - p["num"] / p["den"]) > 1e-9:
        raise AuditError(f"the printed arc is {share} of the circle, not "
                         f"{p['num']}/{p['den']}")
    return share


def arc_angle(p: dict) -> float:
    return 360.0 - p["theta"] if p["ask"] == "major" else float(p["theta"])


def chord_angle(p: dict) -> float:
    # two radii and the chord make an isosceles triangle: the angles sum to 180
    central = 180.0 - 2.0 * p["base"]
    if p["ask"] == "central":
        return central
    return TAU * p["r"] * central / 360.0


def sector(p: dict) -> float:
    whole = math.pi * p["r"] ** 2
    if p["ask"] == "area":
        return whole * p["theta"] / 360.0
    return 360.0 * p["area"] / whole


# ----------------------------------------------------------------- angles

def degree_radian(p: dict) -> float:
    if p["mode"] == "to_radians":
        turns = p["deg"] / 180.0
        return turns if p["ask"] == "coefficient" else turns * math.pi
    return 180.0 * p["num"] / p["den"]


def unit_circle_angle(p: dict) -> float:
    left = 180.0 - p["a"] - p["b"]
    return left * math.pi / 180.0 if p["ask"] == "radians" else left


def coterminal(p: dict) -> float:
    # the two named points are opposite ends of a diameter, so the angle is a
    # half turn, and any whole number of full turns may be added to it
    return (1.0 + 2.0 * p["k"]) * math.pi


def exact_trig(p: dict) -> float:
    a = p["num"] * math.pi / p["den"]
    return math.cos(a) if p["fn"] == "cos" else math.sin(a)


# --------------------------------------------------------------- equations

def _complete(p: dict) -> tuple[F, F, F]:
    """Centre and squared radius, from the coefficients the item prints.

    a(x^2 + y^2) + dx + ey = c  ->  (x + d/2a)^2 + (y + e/2a)^2 = c/a + h^2 + k^2
    """
    a, d, e, c = F(p["lead"]), F(p["d"]), F(p["e"]), F(p["rhs"])
    if a == 0:
        raise AuditError("an equation with no squared terms is not a circle")
    h, k = -d / (2 * a), -e / (2 * a)
    r2 = c / a + h * h + k * k
    if r2 <= 0:
        raise AuditError(f"radius squared came out as {r2}, so this is not a circle")
    return h, k, r2


def equation_read(p: dict):
    h, k, r2 = _complete(p)
    if p.get("symbolic"):
        n = math.sqrt(float(r2))
        if abs(n - round(n)) > 1e-9:
            raise AuditError(f"the radius coefficient {n} is not a whole number")
        return float(round(n))
    if p["ask"] == "center":
        return point(h, k)
    root = math.sqrt(float(r2))
    return root if p["ask"] == "radius" else 2.0 * root


def equation_write(p: dict):
    h, k = F(*p["h"]), F(*p["k"])
    if p["ask"] == "equation":
        if p.get("sym"):
            rhs = f"{p['mult'] ** 2}{p['sym']}²"
        else:
            rhs = str(F(*p["r2"]))
        return standard_equation(h, k, rhs)
    r2 = F(*p["r2"])
    value = {"a": -2 * h, "b": -2 * k, "c": h * h + k * k - r2}[p["coef"]]
    return float(value)


def point_on(p: dict):
    h, k, r = p["h"], p["k"], p["r"]
    if p["mode"] == "coordinate":
        # the named point sits at the far edge along one axis, so the other
        # coordinate is forced: solve (x - h)^2 + (y - k)^2 = r^2 with one known
        off = p["side"] * r
        rest = r * r - off * off
        if rest != 0:
            raise AuditError("the stated point does not pin the coordinate down")
        return float(k if p["axis"] == "x" else h)
    dx, dy = p["dx"], p["dy"]
    if dx * dx + dy * dy != r * r:
        raise AuditError("the named point is not on the circle")
    return point(2 * h - (h + dx), 2 * k - (k + dy))


def interior(p: dict):
    r2 = p["r"] ** 2
    ox, oy = p["out"]
    if ox * ox + oy * oy <= r2:
        raise AuditError("the keyed point is not outside the circle")
    for name in ("far", "sq"):
        ax, ay = p[name]
        if ax * ax + ay * ay >= r2:
            raise AuditError(f"the {name} point is not inside the circle")
    return point(p["h"] + ox, p["k"] + oy)


def tangent(p: dict) -> float:
    dx, dy = p["dx"], p["dy"]
    if dy == 0:
        raise AuditError("a tangent at that point is vertical")
    return -dx / dy


def transform(p: dict):
    if p["mode"] == "scale":
        return float(p["scale"] ** 2 * p["r2"])
    step = {"right": (1, 0), "left": (-1, 0), "up": (0, 1), "down": (0, -1)}[p["dir"]]
    if p["ask"] == "rhs":
        return float(p.get("times", 1) * p["r2"])
    h = p["h"] + step[0] * p["shift"]
    k = p["k"] + step[1] * p["shift"]
    return standard_equation(F(h), F(k), str(p["r2"]))


AUDITS = {
    "circles_supply_radius": supply_radius,
    "circles_supply_diameter": supply_diameter,
    "circles_arc": arc,
    "circles_arc_pair": arc_pair,
    "circles_arc_fraction": arc_fraction,
    "circles_arc_angle": arc_angle,
    "circles_chord_angle": chord_angle,
    "circles_sector": sector,
    "circles_degree_radian": degree_radian,
    "circles_unit_circle_angle": unit_circle_angle,
    "circles_coterminal": coterminal,
    "circles_exact_trig": exact_trig,
    "circles_equation_read": equation_read,
    "circles_equation_write": equation_write,
    "circles_point_on": point_on,
    "circles_interior": interior,
    "circles_tangent": tangent,
    "circles_transform": transform,
}
