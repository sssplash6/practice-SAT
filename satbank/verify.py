"""Independent numeric re-implementation of every formula in shapes.py.

Written from the geometry, not from shapes.py, on purpose: an item ships only
when the symbolic key and this float computation agree. A typo has to be made
twice, identically, to escape.
"""

from __future__ import annotations

import math

from .exact import Exact

__all__ = ["NUMERIC", "check"]

NUMERIC = {
    ("square", "area"):            lambda s: s * s,
    ("square", "perimeter"):       lambda s: s + s + s + s,
    ("rectangle", "area"):         lambda l, w: l * w,
    ("rectangle", "perimeter"):    lambda l, w: 2 * l + 2 * w,
    ("triangle", "area"):          lambda b, h: 0.5 * b * h,
    ("parallelogram", "area"):     lambda b, h: b * h,
    ("circle", "area"):            lambda r: math.pi * r ** 2,
    ("circle", "circumference"):   lambda r: math.tau * r,
    ("cube", "volume"):            lambda e: e ** 3,
    ("cube", "surface_area"):      lambda e: 6 * e * e,
    ("rect_prism", "volume"):      lambda l, w, h: l * w * h,
    ("rect_prism", "surface_area"): lambda l, w, h: 2 * (l * w) + 2 * (l * h) + 2 * (w * h),
    ("square_prism", "volume"):    lambda s, h: s * s * h,
    ("square_prism", "surface_area"): lambda s, h: 2 * s * s + 4 * s * h,
    ("cylinder", "volume"):        lambda r, h: math.pi * r * r * h,
    ("cylinder", "surface_area"):  lambda r, h: math.tau * r * r + math.tau * r * h,
    ("cone", "volume"):            lambda r, h: math.pi * r * r * h / 3.0,
    ("sphere", "volume"):          lambda r: 4.0 / 3.0 * math.pi * r ** 3,
    ("sphere", "surface_area"):    lambda r: 4.0 * math.pi * r * r,
    ("hemisphere", "volume"):      lambda r: 2.0 / 3.0 * math.pi * r ** 3,
    ("prism_base", "volume"):      lambda B, h: B * h,
}

# The numeric formulas take positional args in this order.
ORDER = {
    "square": ("s",), "rectangle": ("l", "w"), "triangle": ("b", "h"),
    "parallelogram": ("b", "h"), "circle": ("r",), "cube": ("e",),
    "rect_prism": ("l", "w", "h"), "square_prism": ("s", "h"),
    "cylinder": ("r", "h"), "cone": ("r", "h"), "sphere": ("r",),
    "hemisphere": ("r",), "prism_base": ("B", "h"),
}


def check(shape_key: str, measure: str, dims: dict, claimed: Exact, tol: float = 1e-9) -> None:
    """Raise unless the symbolic key agrees with the independent float route."""
    fn = NUMERIC[(shape_key, measure)]
    args = [float(dims[k]) for k in ORDER[shape_key]]
    want, got = fn(*args), float(claimed)
    scale = max(1.0, abs(want))
    if abs(want - got) > tol * scale:
        raise AssertionError(
            f"{shape_key}.{measure}{tuple(args)}: symbolic {claimed.plain()} "
            f"= {got!r} but numeric route gives {want!r}")
