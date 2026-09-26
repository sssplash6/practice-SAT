"""Independent re-derivation of every Lines, Angles and Triangles answer.

Written from the geometry, not from the generators: plain floats and plain
Fractions, no `Exact`, and nothing imported from the templates or the figure
module. Where a template reasoned about a marked angle by name -- "this spot
and that spot are corresponding, so they are equal" -- this file puts the two
rays in coordinates and measures the angle between them, which is a different
route to the same number and catches a template that has the relationship
backwards.
"""

from __future__ import annotations

import math
from fractions import Fraction as Q

from ...audit import AuditError

MINUS = "−"


def supply_pair(p: dict) -> float:
    return _pos(180.0 - p["given"])


def supply_base(p: dict) -> float:
    return _pos((180.0 - p["vertex"]) / 2)


def supply_exterior(p: dict) -> float:
    return _pos(p["a"] + p["b"])


def _pos(v, what="angle"):
    if not 0 < v < 360:
        raise AuditError(f"{what} came out as {v}, which is not a measure")
    return float(v)


def _snap(v, step):
    """Round to the nearest multiple of `step`, refusing an exact halfway value."""
    v, step = Q(v), Q(step)
    k = v / step
    n = k.numerator // k.denominator
    frac = k - n
    if 2 * frac == 1:
        raise AuditError("this value sits exactly halfway between two printable "
                         "answers, so the item has no defensible key")
    return (n + 1) * step if 2 * frac > 1 else n * step


# ================================================================= triangles

def triangle_sum(p: dict) -> float:
    return _pos(180 - p["a"] - p["b"])


def isosceles(p: dict) -> float:
    base = p["base"] if p["mode"] == "base" else 180 - p["ext"]
    if p["mode"] == "exterior" and p["base"] != 180 - p["ext"]:
        raise AuditError("the base angle and the exterior angle disagree")
    return _pos(180 - 2 * base)


def isosceles_possible(p: dict) -> float:
    a = p["a"]
    shapes = {Q(a), Q(180 - a, 2), Q(180 - 2 * a)}
    key = Q(2 * a)
    if key in shapes:
        raise AuditError(f"{key} is in fact a possible measure")
    if len(shapes) != 3:
        raise AuditError("the three isosceles shapes are not three distinct angles")
    return _pos(key)


def angle_algebra(p: dict) -> float:
    rest = 180 - p["c"] - p["a"]
    if rest % p["mult"]:
        raise AuditError("the remaining angle is not a whole multiple of the unknown")
    return _pos(rest // p["mult"])


def exterior_angle(p: dict) -> float:
    if p["mode"] == "extended":
        return _pos(p["p"] + p["q"])
    return _pos(p["ext"] - p["inner"])


def isosceles_cross(p: dict) -> float:
    s, t, v = p["s"], p["t"], p["v"]
    if p["ask"] == "v":
        base = Q(180 - t, 2)
        if base <= 0:
            raise AuditError("the isosceles triangle has no base angles")
        return _pos(s + base)
    base = v - s
    return _pos(180 - 2 * base)


def vertical_isosceles(p: dict) -> float:
    # the apex of the lower triangle is the supplement of the marked angle, and
    # its two base angles share what is left of 180
    apex = 180 - p["apex"]
    return _pos(Q(180 - apex, 2))


def crossing_triangles(p: dict) -> float:
    mid = 180 - p["a"] - p["x"]          # the angle at the crossing
    return _pos(180 - mid - p["e"])      # vertical angle, then the angle sum


# ================================================================= parallels

def _spot_angle(spot, theta: float) -> float:
    """The angle at one of the eight spots, measured in coordinates.

    The transversal makes an angle `theta` with the parallel lines. At either
    crossing the four rays run along 0 and 180 degrees (the parallel line) and
    along theta and theta + 180 (the transversal); a spot names the horizontal
    ray by its side and the transversal ray by whether it points up or down.
    """
    h = 0.0 if spot[2] == "right" else 180.0
    t = theta if spot[1] == "above" else theta + 180.0
    d = abs((t - h + 180.0) % 360.0 - 180.0)
    return d


def transversal(p: dict) -> float:
    given, gs, asks = p["given"], tuple(p["given_spot"]), tuple(p["ask_spot"])
    theta = next((c for c in (float(given), 180.0 - given)
                  if abs(_spot_angle(gs, c) - given) < 1e-9), None)
    if theta is None:
        raise AuditError(f"no transversal makes the marked spot measure {given}")
    return _pos(round(_spot_angle(asks, theta), 9))


def transversal_proof(p: dict) -> str:
    return f"{p['names'][0]} = {p['given']}"


def transversal_inequality(p: dict) -> str:
    return f"{p['names'][0]} > {180 - p['bound']}"


def _term(coef: int, const: int, var: str) -> str:
    if coef == 0:
        return ("{}{:,}").format(MINUS if const < 0 else "", abs(const))
    head = "{}{}{}".format(MINUS if coef < 0 else "",
                           "" if abs(coef) == 1 else "{:,}".format(abs(coef)), var)
    if const == 0:
        return head
    return "{} {} {:,}".format(head, "+" if const > 0 else MINUS, abs(const))


def eight_angles(p: dict) -> str:
    m, c, var = p["m"], p["c"], p["var"]
    reachable = {(4 * m, -4 * c), (2 * m, 180 - 2 * c), (0, 360),
                 (-2 * m, 540 + 2 * c), (-4 * m, 720 + 4 * c)}
    key = (-2 * m, 540 + 4 * c)
    if key in reachable:
        raise AuditError("the keyed expression is in fact one of the five sums")
    return _term(key[0], key[1], var)


def parallel_triangle(p: dict) -> float:
    return _pos(180 - p["y"] - p["z"])


def midsegment_angle(p: dict) -> float:
    return _pos(180 - p["d"] - p["c"])


def perp_transversal(p: dict) -> float:
    # the transversal leaves the parallels at 180 - given; the perpendicular is
    # a quarter turn from them, so what is left is 90 - that
    return _pos(90 - (180 - p["given"]))


def two_transversals(p: dict) -> float:
    at_line = 180 - p["b"]                       # s against the parallel lines
    inside = 180 - p["a"] - at_line              # the triangle's lower angle
    return _pos(Q(180 - inside, 2))


def three_lines_point(p: dict) -> float:
    return _pos(180 - p["x"] - p["y"])


def three_lines_triangle(p: dict) -> float:
    at_sr = 180 - p["p"]
    at_st = 180 - at_sr - p["q"]
    if at_st <= 0:
        raise AuditError("these three lines do not close a triangle")
    return _pos(180 - at_st)


def big_chain(p: dict) -> float:
    at_s = 180 - p["at_q"] - p["at_x"]
    slope = p["at_w"] - at_s
    foot = 180 - p["at_t"]
    if min(at_s, slope, foot) <= 0:
        raise AuditError("this chain of angles does not close")
    return _pos(180 - slope - foot)


# =================================================================== similar

def similar_angle(p: dict) -> float:
    return _pos(p["angle"])


def similar_side(p: dict) -> float:
    return float(p["side"] * p["k"])


def shadow(p: dict) -> float:
    h = Q(p["h1"] * p["s2"], p["s1"])
    return float(_snap(h, p["step"])) if p["closest"] else float(h)


def parallel_segments(p: dict) -> float:
    ab, bc, fe = (Q(*p["ab"]), Q(*p["bc"]), Q(*p["fe"]))
    return float(_snap(fe * bc / ab, Q(1, 10 ** p["places"])))


def ratio_match(p: dict) -> str:
    d, e, f = p["partner"]
    return f"{d}{f}/{d}{e}"


def similar_needed(p: dict) -> str:
    if 180 - p["a"] - p["b"] <= 0:
        raise AuditError("those two angles do not leave a third")
    return "No additional information is needed"


def similar_sufficient(p: dict) -> str:
    third = 180 - p["a"] - p["m"]
    if third <= 0:
        raise AuditError("those two angles do not leave a third")
    return (f"The measures of angles {p['names'][1]} and {p['partner'][2]} are "
            f"{p['m']}° and {third}°, respectively.")


def vertical_similar(p: dict) -> float:
    wq, xq, wx, yq = p["wq"], p["xq"], p["wx"], p["yq"]
    if not abs(wq - xq) < wx < wq + xq:
        raise AuditError("the three given lengths are not a triangle")
    return float(Q(wx * yq, wq))


def altitude_legs(p: dict) -> float:
    a, b, c = p["p"], p["q"], p["h"]
    if a * a + b * b != c * c:
        raise AuditError("the legs and hypotenuse given are not a right triangle")
    return float(Q(a * b, c))


def geometric_mean(p: dict) -> float:
    ad = Q(*p["ad"])
    if p["mode"] == "alt":
        bd = Q(*p["bd"])
        return float(bd * bd / ad)
    ab2 = Q(*p["ab2"])
    ac = ab2 / ad
    if ac <= ad:
        raise AuditError("the foot of the altitude does not lie inside the hypotenuse")
    return float(ac - ad)


def parallel_cut_area(p: dict) -> float:
    rt, lk, area = p["rt"], Q(*p["lk"]), Q(*p["area"])
    st = 2 * area / rt
    if not 0 < lk < rt:
        raise AuditError("the parallel segment is not shorter than the side it copies")
    return float(st - st * lk / rt)


def area_range(p: dict) -> float:
    base = p["d1"] + p["d2"]
    ys = [y for y in range(1, 400) if p["lo"] <= Q(base * y, 2) <= p["hi"]]
    if not ys:
        raise AuditError("no whole height gives an area in that range")
    return float(Q(p["d1"] * ys[0], base))


AUDITS = {
    "lat_supply_pair": supply_pair,
    "lat_supply_base": supply_base,
    "lat_supply_exterior": supply_exterior,
    "lat_triangle_sum": triangle_sum,
    "lat_isosceles": isosceles,
    "lat_isosceles_possible": isosceles_possible,
    "lat_angle_algebra": angle_algebra,
    "lat_exterior_angle": exterior_angle,
    "lat_isosceles_cross": isosceles_cross,
    "lat_vertical_isosceles": vertical_isosceles,
    "lat_crossing_triangles": crossing_triangles,
    "lat_transversal": transversal,
    "lat_transversal_proof": transversal_proof,
    "lat_transversal_inequality": transversal_inequality,
    "lat_eight_angles": eight_angles,
    "lat_parallel_triangle": parallel_triangle,
    "lat_midsegment_angle": midsegment_angle,
    "lat_perp_transversal": perp_transversal,
    "lat_two_transversals": two_transversals,
    "lat_three_lines_point": three_lines_point,
    "lat_three_lines_triangle": three_lines_triangle,
    "lat_big_chain": big_chain,
    "lat_similar_angle": similar_angle,
    "lat_similar_side": similar_side,
    "lat_shadow": shadow,
    "lat_parallel_segments": parallel_segments,
    "lat_ratio_match": ratio_match,
    "lat_similar_needed": similar_needed,
    "lat_similar_sufficient": similar_sufficient,
    "lat_vertical_similar": vertical_similar,
    "lat_altitude_legs": altitude_legs,
    "lat_geometric_mean": geometric_mean,
    "lat_parallel_cut_area": parallel_cut_area,
    "lat_area_range": area_range,
}
