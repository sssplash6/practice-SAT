"""Algebra -> Linear Equations in One Variable.

Sixty-five official items across three tiers, and eighteen templates. The axes
the source actually varies are which side the unknown sits on, whether a
bracket has to be expanded, whether the numbers are integers, fractions or
decimals, whether the question wants the unknown or some other expression in
it, and whether the answer is a value, an equation, or a count of solutions.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import algebra as A
from .families import context as C
from .families import structure as S
from .families import supply as U
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "lin1.nested_distribution_grid": U.nested_distribution,
    "lin1.fraction_sum_grid": U.fraction_sum,
    "lin1.solve": A.solve,
    "lin1.distribute": A.distribute,
    "lin1.then_value": A.then_value,
    "lin1.chunk": A.chunk,
    "lin1.reciprocal": A.reciprocal,
    "lin1.count_solutions": S.count_solutions,
    "lin1.identity_constant": S.identity_constant,
    "lin1.no_solution_constant": S.no_solution_constant,
    "lin1.identity_pair": S.identity_pair,
    "lin1.no_solution_conditions": S.no_solution_conditions,
    "lin1.zero_chunk": S.zero_chunk,
    "lin1.equivalent_equation": S.equivalent_equation,
    "lin1.context_solve": C.context_solve,
    "lin1.model_count_mix": C.model_count_mix,
    "lin1.model_context": C.model_context,
    "lin1.expression_in_terms": C.expression_in_terms,
    "lin1.interpret_coefficient": C.interpret_coefficient,
    "lin1.percent_original": C.percent_original,
}

TOPIC = Topic(
    slug="linear_equations_in_one_variable",
    name="Linear Equations in One Variable",
    domain="Algebra",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
