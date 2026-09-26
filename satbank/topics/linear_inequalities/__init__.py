"""Algebra -> Linear Inequalities in One or Two Variables.

Forty-six official items across three tiers, and eighteen templates. The axes
the source varies are what the answer looks like -- a relation, a system, a
count, a point, a band -- and, underneath all of them, one rule: which way the
relation points. Every template here can print the mistake that leaves the
boundary right and the direction wrong, because that is the mistake this topic
is written to catch.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import bands as B
from .families import counting as C
from .families import interpret as N
from .families import model as M
from .families import points as P
from .families import solve as S
from .families import supply as U
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "ineq.budget_max_grid": U.budget_max,
    "ineq.interval_count_grid": U.interval_count,
    "ineq.two_sided_bound_grid": U.two_sided_bound,
    "ineq.perimeter_limit_grid": U.perimeter_limit,
    "ineq.solve_linear": S.solve_linear,
    "ineq.greatest_value": S.greatest_value,
    "ineq.y_range_from_system": S.y_range_from_system,
    "ineq.range_solve": S.range_solve,
    "ineq.triangle_third_side": S.triangle_third_side,
    "ineq.allowable_dimension": S.allowable_dimension,
    "ineq.model_two_var": M.model_two_var,
    "ineq.model_one_var": M.model_one_var,
    "ineq.model_system": M.model_system,
    "ineq.whole_number_bound": C.whole_number_bound,
    "ineq.pair_max": C.pair_max,
    "ineq.value_in_range": C.value_in_range,
    "ineq.which_interval": C.which_interval,
    "ineq.point_solution": P.point_solution,
    "ineq.band_from_extremes": B.band_from_extremes,
    "ineq.band_scale": B.band_scale,
    "ineq.band_formula": B.band_formula,
    "ineq.interpret": N.interpret,
}

TOPIC = Topic(
    slug="linear_inequalities",
    name="Linear Inequalities",
    domain="Algebra",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
