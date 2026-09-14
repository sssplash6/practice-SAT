"""Algebra -> Linear Equations in Two Variables.

Eighty-one official items across three tiers, collapsed to twenty-two
templates in six families. Where Linear Functions varies the surface form of a
rule and asks what it does to a number, this topic varies what the two
variables are *for*: the same equation ax + by = c is a shopping bill, a
perimeter, a mixture and a pair of intercepts, and the question is as often
what one of its pieces means as what number solves it.

The axes the source actually varies are the form the equation arrives in
(standard, slope-intercept, a graph, a table, four tables to choose between),
what is asked of it (a value, a coefficient, an interpretation, an equation, a
slope, an intercept), and which family of wrong answers the item writer reached
for -- which for an interpretation item is the whole of the item.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import graphs as G
from .families import interpret as I
from .families import lines as L
from .families import model as M
from .families import solve as V
from .families import tables as T
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "le2.model_standard": M.model_standard,
    "le2.model_percent": M.model_percent,
    "le2.material_table": M.material_table,
    "le2.interpret_coefficient": I.interpret_coefficient,
    "le2.interpret_constant": I.interpret_constant,
    "le2.interpret_point": I.interpret_point,
    "le2.substitute": V.substitute,
    "le2.context_substitute": V.context_substitute,
    "le2.mixture_solve": V.mixture_solve,
    "le2.slope_of_line": L.slope_of_line,
    "le2.parallel_perpendicular": L.parallel_perpendicular,
    "le2.slope_two_points": L.slope_two_points,
    "le2.point_on_line": L.point_on_line,
    "le2.line_equation": L.line_equation,
    "le2.intercepts": L.intercepts,
    "le2.equivalent_system": L.equivalent_system,
    "le2.line_from_graph": G.line_from_graph,
    "le2.graph_combinations": G.graph_combinations,
    "le2.table_equation": T.table_equation,
    "le2.which_table": T.which_table,
    "le2.table_symbolic": T.table_symbolic,
    "le2.table_line": T.table_line,
}

TOPIC = Topic(
    slug="linear_equations_in_two_variables",
    name="Linear Equations in Two Variables",
    domain="Algebra",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
