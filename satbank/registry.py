"""Every generator, addressable by name, with retry on rejected parameters.

Rejecting a draw is normal: a template refuses parameters that would produce
a nested radical, a non-monomial inverse, a degenerate triangle or an answer
that cannot be entered in a grid-in. The registry just draws again.
"""

from __future__ import annotations

import random
from typing import Callable

from .families import coordinate as C
from .families import measure as M
from .families import scaling as S
from .families import special as X
from .item import Item, ItemError

__all__ = ["TEMPLATES", "generate", "generate_many"]

TEMPLATES: dict[str, Callable] = {
    "measure.forward": M.forward,
    "measure.inverse": M.inverse,
    "similar.linear": S.similar_linear,
    "similar.area": S.similar_area,
    "scaling.solid": S.solid_scaling,
    "scaling.percent": S.percent_change,
    "coord.circle_3pt": C.circle_from_points,
    "coord.triangle_area": C.triangle_from_points,
    "coord.square_diagonals": C.square_on_axes,
    "coord.leg_from_area": C.leg_from_area,
    "expression.measure": X.expression_measure,
    "expression.symbolic_volume": X.symbolic_volume,
    "context.remaining_volume": X.remaining_volume,
    "context.combined_area": X.combined_area,
    "context.missing_side": X.missing_side,
    "context.container_percent": X.container_percent,
    "circle.equal_area_square": X.equal_area_square,
    "circle.convert": X.circle_convert,
    "context.formula_solve": X.formula_solve,
}


def generate(name: str, seed: int, attempts: int = 60, **kw) -> Item:
    """Deterministic in `seed`: the same seed always yields the same item."""
    fn = TEMPLATES[name]
    for i in range(attempts):
        try:
            return fn(random.Random(seed * 1_000_003 + i), seed, **kw)
        except (ItemError, ValueError, ZeroDivisionError, KeyError, StopIteration):
            continue
    raise ItemError(f"{name}: no valid item after {attempts} attempts (seed {seed})")


def generate_many(n: int, seed0: int = 0, names: list[str] | None = None):
    names = names or list(TEMPLATES)
    for i in range(n):
        yield generate(names[i % len(names)], seed0 + i)
