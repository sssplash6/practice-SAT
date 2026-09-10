"""Independent re-derivation of a generated item's answer.

This module is deliberately written from the geometry rather than from the
generators: plain floats, no Exact, no shapes.py formulas except the ones in
verify.py, which were themselves written independently. Inverse items are
checked by numerically root-finding the unknown rather than by any algebra the
generator performs, so the two routes share no reasoning.

An item passes only when this file, knowing nothing but the item's parameters,
lands on the answer the item ships with.
"""

from __future__ import annotations

import math

from .item import Item
from .verify import NUMERIC, ORDER

__all__ = ["audit", "AuditError"]

TOL = 1e-7


class AuditError(Exception):
    pass


def _close(a: float, b: float, tol: float = TOL) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def _sig3(v: float) -> float:
    if v == 0:
        return 0.0
    return round(v, -int(math.floor(math.log10(abs(v)))) + 2)


def _bisect(f, target: float, lo: float = 1e-9, hi: float = 1e7) -> float:
    """Find x > 0 with f(x) = target, for the monotone-increasing formulas here."""
    if f(lo) > target:
        raise AuditError("target below the formula's range")
    while f(hi) < target:
        hi *= 2
        if hi > 1e12:
            raise AuditError("target above the formula's range")
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _measure(shape: str, measure: str, dims: dict) -> float:
    return NUMERIC[(shape, measure)](*[dims[k] for k in ORDER[shape]])


# --------------------------------------------------------------- the answer

def expected(p: dict, item: Item):
    """Return the answer this item should carry: a float, or a string for
    expression items. Raises AuditError if the parameters are unusable."""
    k = p.get("kind")

    if k == "measure_forward":
        v = _measure(p["shape"], p["measure"], p["dims"])
        if p.get("ask_coefficient"):
            v /= math.pi
        if p.get("approximate"):
            v = _sig3(v)
        return v

    if k == "measure_inverse":
        shape, measure, unknown, dims = p["shape"], p["measure"], p["unknown"], p["dims"]
        total = _measure(shape, measure, dims)
        # recover the unknown from the stated total without using any algebra
        # the generator performed
        found = _bisect(lambda x: _measure(shape, measure, {**dims, unknown: x}), total)
        if not _close(found, dims[unknown], 1e-6):
            raise AuditError(f"inverse does not invert: solved {found}, built {dims[unknown]}")
        if p.get("then_measure"):
            return _measure(shape, p["then_measure"], dims)
        return dims[unknown]

    if k == "similar_linear":
        return p["scaled"] * p["k"]

    if k == "similar_area":
        m = p["mode"]
        if m == "area_from_ratio":
            return p["base"] * p["k"] ** 2
        if m == "ratio_from_sides":
            return p["k"] ** 2
        return p["big_side"] / p["k"]

    if k == "solid_scaling":
        if p["mode"] == "volume_multiple":
            return p["v"] * p["rf"] ** 2 * p["hf"]
        if p["a"] ** 2 * p["b"] != p["mult"]:
            raise AuditError(f"{p['a']}^2 x {p['b']} != {p['mult']}")
        return f"R = {p['a']}r and H = {p['b']}h"

    if k == "percent_change":
        return p["area"] * p["ratio"] ** 2

    if k == "circle_3pt":
        r = p["r"]
        return 2.0 * r if p["ask"] == "circumference" else r * r

    if k == "triangle_area":
        (x1, y1), (x2, y2), (x3, y3) = p["pts"]
        return abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0

    if k == "square_diagonals":
        d = 2.0 * p["a"]                       # a square of diagonal d has area d^2/2
        return d * d / 2.0

    if k == "leg_from_area":
        drawn = math.hypot(p["dx"], p["dy"])
        if not _close(0.5 * drawn * p["other"], p["area"], 1e-9):
            raise AuditError("stated area disagrees with the two legs")
        return 2.0 * p["area"] / drawn

    if k == "expression_measure":
        if p["shape"] == "square":
            s = p["s"]
            return f"{s} * {s}" if p["measure"] == "area" else f"4 * {s}"
        l, w = p["l"], p["w"]
        return f"{l} * {w}" if p["measure"] == "area" else f"2({l} + {w})"

    if k == "symbolic_volume":
        c = p["c"]
        return (f"V = pi*r^3 + {c}pi*r^2" if p["relation"] == "longer"
                else f"V = {c}pi*r^3")

    if k == "remaining_volume":
        return p["base"] * p["h"] - p["filled"]

    if k == "combined_area":
        return p["tri"] + p["s"] ** 2

    if k == "missing_side":
        x, y, z = p["x"], p["y"], p["z"]
        if x + y + z != p["perimeter"]:
            raise AuditError("sides do not sum to the stated perimeter")
        if not (x + y > z and x + z > y and y + z > x):
            raise AuditError(f"({x}, {y}, {z}) violates the triangle inequality")
        return float(p["perimeter"] - x - y)

    if k == "container_percent":
        rb = p["rA"] * (100.0 + p["pct"]) / 100.0
        return math.pi * rb * rb * p["h"]

    if k == "equal_area_square":
        return math.sqrt(math.pi * p["r"] ** 2)

    if k == "circle_convert":
        r = p["r"]
        return {"radius": r, "diameter": 2 * r, "circumference": math.tau * r,
                "area": math.pi * r * r}[p["ask"]]

    if k == "formula_solve":
        return round((p["b"] * p["volume"] / (p["a"] * math.pi)) ** (1 / 3), 2)

    raise AuditError(f"no independent solver for kind {k!r}")


def audit(item: Item) -> None:
    """Raise AuditError unless the item's own answer survives re-derivation."""
    if not item.params:
        raise AuditError("item carries no parameters to audit")
    want = expected(item.params, item)

    if isinstance(want, str):
        got = item.choices["ABCD".index(item.answer)]
        if got.replace(" ", "") != want.replace(" ", ""):
            raise AuditError(f"keyed option {got!r}, independently derived {want!r}")
        return

    got = float(item.key)
    if not _close(got, want):
        raise AuditError(f"item answers {item.key.plain()} ({got!r}), "
                         f"independently derived {want!r}")

    # the keyed option must be the key -- by value, since a template may render
    # its options in its own form (decimals rather than a canonical fraction)
    if item.fmt == "mcq":
        keyed = item.choices["ABCD".index(item.answer)]
        if keyed != item.key.plain():
            try:
                shown = float(keyed.replace(",", ""))
            except ValueError:
                raise AuditError(
                    f"answer letter points at {keyed!r}, key is {item.key.plain()!r}") from None
            if not _close(shown, want, 1e-6):
                raise AuditError(f"keyed option reads {keyed!r} but the answer is {want!r}")
        if len(set(item.choices)) != len(item.choices):
            raise AuditError(f"an option is repeated: {item.choices}")
    elif item.fmt == "spr":
        txt = item.answer
        val = (float(txt.split("/")[0]) / float(txt.split("/")[1])) if "/" in txt else float(txt)
        if not _close(val, want, 1e-6):
            raise AuditError(f"grid-in reads {txt!r}, independently derived {want!r}")
