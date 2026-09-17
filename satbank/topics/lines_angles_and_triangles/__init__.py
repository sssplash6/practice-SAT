"""Geometry and Trigonometry -> Lines, Angles, and Triangles.

Forty-eight official items in three families. The first is the triangle
itself: the angle sum, the base angles of an isosceles triangle, and the
exterior angle, reached directly in the easy tier and through two or three
crossings in the hard one. The second is parallel lines cut by a transversal,
where the whole question is which of the eight angles is marked. The third is
similarity -- what a scale factor changes, what it leaves alone, and the
proportions that fall out of a line drawn parallel to one side.

The figure carries the question in most of these, so every figure is generated
from the same parameters as the stem and, wherever the geometry allows it,
drawn to scale. `option_check.py` reads the SVG back and measures the drawn
angles, which is the only check in the engine that can see a triangle with the
right answer attached to the wrong vertex.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import parallels as L
from .families import similar as M
from .families import triangles as T
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "lat.triangle_sum": T.triangle_sum,
    "lat.isosceles": T.isosceles,
    "lat.isosceles_possible": T.isosceles_possible,
    "lat.angle_algebra": T.angle_algebra,
    "lat.exterior_angle": T.exterior_angle,
    "lat.isosceles_cross": T.isosceles_cross,
    "lat.vertical_isosceles": T.vertical_isosceles,
    "lat.crossing_triangles": T.crossing_triangles,
    "lat.transversal": L.transversal,
    "lat.transversal_proof": L.transversal_proof,
    "lat.transversal_inequality": L.transversal_inequality,
    "lat.eight_angles": L.eight_angles,
    "lat.parallel_triangle": L.parallel_triangle,
    "lat.midsegment_angle": L.midsegment_angle,
    "lat.perp_transversal": L.perp_transversal,
    "lat.two_transversals": L.two_transversals,
    "lat.three_lines_point": L.three_lines_point,
    "lat.three_lines_triangle": L.three_lines_triangle,
    "lat.big_chain": L.big_chain,
    "lat.similar_angle": M.similar_angle,
    "lat.similar_side": M.similar_side,
    "lat.shadow": M.shadow,
    "lat.parallel_segments": M.parallel_segments,
    "lat.ratio_match": M.ratio_match,
    "lat.similar_needed": M.similar_needed,
    "lat.similar_sufficient": M.similar_sufficient,
    "lat.vertical_similar": M.vertical_similar,
    "lat.altitude_legs": M.altitude_legs,
    "lat.geometric_mean": M.geometric_mean,
    "lat.parallel_cut_area": M.parallel_cut_area,
    "lat.area_range": M.area_range,
}

TOPIC = Topic(
    slug="lines_angles_and_triangles",
    name="Lines, Angles, and Triangles",
    domain="Geometry and Trigonometry",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
