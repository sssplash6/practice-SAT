"""Geometry and Trigonometry -> Area and Volume.

The first topic, and the pattern the rest follow: 19 templates in six
families, an independently written solver for every one of them, and the 59
official items encoded as the parameters that reproduce them.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import coordinate as C
from .families import measure as M
from .families import scaling as S
from .families import special as X
from .sources import ALL, EXCLUDED

TEMPLATES = {
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

TOPIC = Topic(
    slug="area_and_volume",
    name="Area and Volume",
    domain="Geometry and Trigonometry",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
