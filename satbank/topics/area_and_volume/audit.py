"""Independent re-derivation of every Area and Volume answer.

Written from the geometry rather than from the generators: plain floats, no
Exact, and no formula taken from `shapes.py`. The only formulas shared are the
ones in `verify.py`, which were themselves written a second time from the
geometry. Inverse items are checked by root-finding the unknown, so the two
routes share no algebra.

A wrong answer has to be produced twice, identically, by two separately
written pieces of code, to escape.
"""

from __future__ import annotations

import math

from ...audit import AuditError, close, sig3, solve_for
from ...verify import NUMERIC, ORDER


def _measure(shape: str, measure: str, dims: dict) -> float:
    return NUMERIC[(shape, measure)](*[dims[k] for k in ORDER[shape]])


def measure_forward(p: dict):
    v = _measure(p["shape"], p["measure"], p["dims"])
    if p.get("ask_coefficient"):
        v /= math.pi
    if p.get("approximate"):
        v = sig3(v)
    return v


def measure_inverse(p: dict):
    shape, measure, unknown, dims = p["shape"], p["measure"], p["unknown"], p["dims"]
    total = _measure(shape, measure, dims)
    found = solve_for(lambda x: _measure(shape, measure, {**dims, unknown: x}), total)
    if not close(found, dims[unknown], 1e-6):
        raise AuditError(f"inverse does not invert: solved {found}, built {dims[unknown]}")
    if p.get("then_measure"):
        return _measure(shape, p["then_measure"], dims)
    return dims[unknown]


def similar_linear(p: dict):
    return p["scaled"] * p["k"]


def similar_area(p: dict):
    m = p["mode"]
    if m == "area_from_ratio":
        return p["base"] * p["k"] ** 2
    if m == "ratio_from_sides":
        return p["k"] ** 2
    return p["big_side"] / p["k"]


def solid_scaling(p: dict):
    if p["mode"] == "volume_multiple":
        return p["v"] * p["rf"] ** 2 * p["hf"]
    if p["a"] ** 2 * p["b"] != p["mult"]:
        raise AuditError(f"{p['a']}^2 x {p['b']} != {p['mult']}")
    return f"R = {p['a']}r and H = {p['b']}h"


def percent_change(p: dict):
    return p["area"] * p["ratio"] ** 2


def circle_3pt(p: dict):
    r = p["r"]
    return 2.0 * r if p["ask"] == "circumference" else r * r


def triangle_area(p: dict):
    (x1, y1), (x2, y2), (x3, y3) = p["pts"]
    return abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0


def square_diagonals(p: dict):
    da, db = 2.0 * p["a"], 2.0 * p.get("b", p["a"])
    ask = p.get("ask", "area")
    if ask == "area":
        return da * db / 2.0
    side = math.hypot(p["a"], p.get("b", p["a"]))
    return side if ask == "side" else 4.0 * side


def leg_from_area(p: dict):
    drawn = math.hypot(p["dx"], p["dy"])
    if not close(0.5 * drawn * p["other"], p["area"], 1e-9):
        raise AuditError("stated area disagrees with the two legs")
    return 2.0 * p["area"] / drawn


def expression_measure(p: dict):
    if p["shape"] == "square":
        s = p["s"]
        return f"{s} * {s}" if p["measure"] == "area" else f"4 * {s}"
    l, w = p["l"], p["w"]
    return f"{l} * {w}" if p["measure"] == "area" else f"2({l} + {w})"


def symbolic_volume(p: dict):
    c, rel, solid = p["c"], p["relation"], p.get("solid", "cylinder")
    if solid == "cylinder":
        return {"longer": f"V = pi*r^3 + {c}pi*r^2",
                "times": f"V = {c}pi*r^3",
                "shorter": f"V = 2pi*r^3 - {c}pi*r^2",
                "twice_plus": f"V = 2pi*r^3 + {c}pi*r^2"}[rel]
    return {"longer": f"V = s^3 + {c}s^2",
            "times": f"V = {c}s^3",
            "shorter": f"V = 2s^3 - {c}s^2",
            "twice_plus": f"V = 2s^3 + {c}s^2"}[rel]


def remaining_volume(p: dict):
    return p["base"] * p["h"] - p["filled"]


def combined_area(p: dict):
    return p["tri"] + p["s"] ** 2


def missing_side(p: dict):
    x, y, z = p["x"], p["y"], p["z"]
    if x + y + z != p["perimeter"]:
        raise AuditError("sides do not sum to the stated perimeter")
    if not (x + y > z and x + z > y and y + z > x):
        raise AuditError(f"({x}, {y}, {z}) violates the triangle inequality")
    return float(p["perimeter"] - x - y)


def container_percent(p: dict):
    f = (100.0 + p["pct"] if p.get("up", True) else 100.0 - p["pct"]) / 100.0
    dim = p.get("dim", "radius")
    rb = p["rA"] * (f if dim in ("radius", "both") else 1.0)
    hb = p["h"] * (f if dim in ("height", "both") else 1.0)
    vb = math.pi * rb * rb * hb
    if p.get("ask", "volume") == "volume":
        return vb
    return vb / (math.pi * p["rA"] ** 2 * p["h"])


def equal_area_square(p: dict):
    side = math.sqrt(math.pi * p["r"] ** 2)
    return side if p.get("ask", "side") == "side" else 4.0 * side


def circle_convert(p: dict):
    r = p["r"]
    return {"radius": r, "diameter": 2 * r, "circumference": math.tau * r,
            "area": math.pi * r * r}[p["ask"]]


def formula_solve(p: dict):
    return round((p["b"] * p["volume"] / (p["a"] * math.pi)) ** (1 / 3), 2)


AUDITS = {
    "measure_forward": measure_forward,
    "measure_inverse": measure_inverse,
    "similar_linear": similar_linear,
    "similar_area": similar_area,
    "solid_scaling": solid_scaling,
    "percent_change": percent_change,
    "circle_3pt": circle_3pt,
    "triangle_area": triangle_area,
    "square_diagonals": square_diagonals,
    "leg_from_area": leg_from_area,
    "expression_measure": expression_measure,
    "symbolic_volume": symbolic_volume,
    "remaining_volume": remaining_volume,
    "combined_area": combined_area,
    "missing_side": missing_side,
    "container_percent": container_percent,
    "equal_area_square": equal_area_square,
    "circle_convert": circle_convert,
    "formula_solve": formula_solve,
}
