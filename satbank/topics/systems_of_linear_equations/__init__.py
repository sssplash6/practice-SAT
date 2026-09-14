"""Algebra -> Systems of Linear Equations in Two Variables.

Sixty-two official items across three tiers, and twenty templates in four
families. The axes the source varies are the surface the two equations are
written on (both in standard form, one already solved for a variable, a bracket
that is itself a total, two drawn lines, or a story), what is asked for (x, y,
the pair, an expression in both, a constant that changes the solution set, or
the system itself), and -- the one that carries the hard tier -- whether the
question is about the point the lines share or about whether they share one at
all.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import context as C
from .families import graph as G
from .families import model as M
from .families import solve as S
from .families import structure as T
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "sys.solve_standard": S.solve_standard,
    "sys.solve_substitution": S.solve_substitution,
    "sys.solve_pair": S.solve_pair,
    "sys.chunk": S.chunk,
    "sys.graph_solution": G.graph_solution,
    "sys.model_purchase": M.model_purchase,
    "sys.model_total_value": M.model_total_value,
    "sys.model_relation": M.model_relation,
    "sys.infinite_constant": T.infinite_constant,
    "sys.infinite_normalized": T.infinite_normalized,
    "sys.no_solution_slope": T.no_solution_slope,
    "sys.no_solution_gathered": T.no_solution_gathered,
    "sys.pick_no_solution": T.pick_no_solution,
    "sys.other_equation": T.other_equation,
    "sys.count_intersections": T.count_intersections,
    "sys.unknown_coefficient": T.unknown_coefficient,
    "sys.all_solutions": T.all_solutions,
    "sys.purchase_solve": C.purchase_solve,
    "sys.relation_pair": C.relation_pair,
    "sys.two_rates": C.two_rates,
}

TOPIC = Topic(
    slug="systems_of_linear_equations",
    name="Systems of Linear Equations",
    domain="Algebra",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
