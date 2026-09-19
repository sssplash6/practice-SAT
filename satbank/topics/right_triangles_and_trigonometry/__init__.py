"""Geometry and Trigonometry -> Right Triangles and Trigonometry.

Thirty-three official items, nineteen of them hard, collapsed into nineteen
templates in four families: the sides of a right triangle and the two special
triangles; the three ratios and the named mistakes students make with them;
similar right triangles, where the correspondence the stem prints is part of
the mathematics; and the composite figures in which one right triangle sits
inside another.

Two things run through all of it. Nothing floats -- a 5√3 leg, a √2/2 sine and
a 58 + 58√2 perimeter all stay exact to the printed page, the last of them in
`exact.Surd`, written here and since promoted, because `Exact` holds
`coef · π^e · √rad` and not a rational added to a radical. And every figure
is drawn to scale from the item's own parameters, right-angle mark included,
so `option_check.py` can read the picture back off the pixels and ask whether
it still agrees with the answer.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import composite as C
from .families import ratios as R
from .families import sides as S
from .families import similar as M
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "rtt.pythagoras": S.pythagoras,
    "rtt.leg_expression": S.leg_expression,
    "rtt.rectangle_diagonal": S.rectangle_diagonal,
    "rtt.special_triangle": S.special_triangle,
    "rtt.special_perimeter": S.special_perimeter,
    "rtt.equilateral_logo": S.equilateral_logo,
    "rtt.trig_ratio": R.trig_ratio,
    "rtt.ratio_to_side": R.ratio_to_side,
    "rtt.cofunction_match": R.cofunction_match,
    "rtt.cofunction_angles": R.cofunction_angles,
    "rtt.complement_tangent": R.complement_tangent,
    "rtt.complement_ratio": R.complement_ratio,
    "rtt.split_right_angle": R.split_right_angle,
    "rtt.similar_ratio": M.similar_ratio,
    "rtt.similar_side": M.similar_side,
    "rtt.similar_sides_ratio": M.similar_sides_ratio,
    "rtt.altitude_special": C.altitude_special,
    "rtt.nested_similar": C.nested_similar,
    "rtt.parallel_similar": C.parallel_similar,
}

TOPIC = Topic(
    slug="right_triangles_and_trigonometry",
    name="Right Triangles and Trigonometry",
    domain="Geometry and Trigonometry",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
