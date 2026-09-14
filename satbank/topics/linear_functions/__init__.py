"""Algebra -> Linear Functions.

Eighty-six official items across three tiers, collapsed to twenty-three
templates in six families. The axes the source actually varies are the surface
form of the rule (mx + b, b - kx, (ax + c)/d, a table, a drawn line), what is
asked for (a value, a coefficient, an intercept, an equation, a sentence), and
-- the one that matters most here -- which family of wrong answers the item
writer reached for, since an interpretation item's distractors are as much a
part of the item as its numbers.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import basic as B
from .families import context as C
from .families import define as D
from .families import graph as G
from .families import interpret as I
from .families import symbolic as S
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "lin.evaluate": B.evaluate,
    "lin.coefficient": B.coefficient,
    "lin.combine": B.combine,
    "lin.inner_scale": B.inner_scale,
    "lin.from_points": D.from_points,
    "lin.from_table": D.from_table,
    "lin.define_line": D.define_line,
    "lin.table_facts": D.table_facts,
    "lin.x_intercept": D.x_intercept,
    "lin.y_intercept": D.y_intercept,
    "lin.model_equation": C.model_equation,
    "lin.per_unit_model": C.per_unit_model,
    "lin.tiered_cost": C.tiered_cost,
    "lin.model_value": C.model_value,
    "lin.context_two_points": C.context_two_points,
    "lin.interpret_slope": I.interpret_slope,
    "lin.interpret_constant": I.interpret_constant,
    "lin.interpret_x_intercept": I.interpret_x_intercept,
    "lin.graph_read": G.graph_read,
    "lin.graph_shifted": G.graph_shifted,
    "lin.parameter_intercept": S.parameter_intercept,
    "lin.affine_conversion": S.affine_conversion,
    "lin.unit_relation": S.unit_relation,
}

TOPIC = Topic(
    slug="linear_functions",
    name="Linear Functions",
    domain="Algebra",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
