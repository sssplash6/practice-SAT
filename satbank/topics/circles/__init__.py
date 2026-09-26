"""Geometry and Trigonometry -> Circles.

Thirty-two official items across three tiers, collapsed into sixteen
templates in three families: the arc-to-circumference proportion and the
places the source hides it, angle measure in degrees and radians, and the
circle in the xy-plane -- its equation, the points around it, and what
happens to the equation when the circle moves.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import angles as G
from .families import arc as A
from .families import equation as Q
from .families import supply as U
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "circles.radius_from_circumference": U.radius_from_circumference,
    "circles.diameter_from_area": U.diameter_from_area,
    "circles.arc": A.arc,
    "circles.arc_pair": A.arc_pair,
    "circles.arc_fraction": A.arc_fraction,
    "circles.arc_angle": A.arc_angle,
    "circles.chord_angle": A.chord_angle,
    "circles.sector": A.sector,
    "circles.degree_radian": G.degree_radian,
    "circles.unit_circle_angle": G.unit_circle_angle,
    "circles.coterminal": G.coterminal,
    "circles.exact_trig": G.exact_trig,
    "circles.equation_read": Q.equation_read,
    "circles.equation_write": Q.equation_write,
    "circles.point_on": Q.point_on,
    "circles.interior": Q.interior,
    "circles.tangent_slope": Q.tangent_slope,
    "circles.transform": Q.transform,
}

TOPIC = Topic(
    slug="circles",
    name="Circles",
    domain="Geometry and Trigonometry",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
