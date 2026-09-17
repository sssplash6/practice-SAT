"""Advanced Math -> Nonlinear Equations in One Variable and Systems of Equations
in Two Variables.

Eighty-five official items across three tiers, and thirty-two templates in five
families. The axes the source varies are the surface the nonlinearity is written
on -- a square, an absolute value, a radical, a denominator, a product already
factored -- what is asked for (one solution, the positive one, their sum, the
set, a pair, a constant) and, for the hard tier, whether the question is about a
root at all or about a condition: how many solutions there are, and which value
of a constant leaves exactly one.

Two things run through the whole topic and are the reason it is built the way it
is. Squaring a radical and clearing a denominator both invent roots the printed
equation does not have, so every template that does either tests its candidates
against the printed equation rather than against the equation squaring produced.
And nearly a third of the items are grid-ins, several of which admit more than
one answer -- the key file carries all of them and the engine only has to land on
one.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import condition as C
from .families import graph as G
from .families import literal as L
from .families import solve as S
from .families import system as Y
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "nleq.isolate_sum": L.isolate_sum,
    "nleq.isolate_bracket": L.isolate_bracket,
    "nleq.isolate_factor": L.isolate_factor,
    "nleq.isolate_denominator": L.isolate_denominator,
    "nleq.scale_relation": L.scale_relation,
    "nleq.square_equation": S.square_equation,
    "nleq.absolute_equation": S.absolute_equation,
    "nleq.quadratic_solve": S.quadratic_solve,
    "nleq.quadratic_formula": S.quadratic_formula,
    "nleq.factored_equation": S.factored_equation,
    "nleq.shared_factor": S.shared_factor,
    "nleq.cancel_squares": S.cancel_squares,
    "nleq.scaled_quadratic": S.scaled_quadratic,
    "nleq.radical_equation": S.radical_equation,
    "nleq.rational_linear": S.rational_linear,
    "nleq.rational_quadratic": S.rational_quadratic,
    "nleq.rational_combine": S.rational_combine,
    "nleq.product_roots_constant": S.product_roots_constant,
    "nleq.paired_quadratics": S.paired_quadratics,
    "nleq.curve_line_system": Y.curve_line_system,
    "nleq.sum_product": Y.sum_product,
    "nleq.secant_slope": Y.secant_slope,
    "nleq.count_real_solutions": C.count_real_solutions,
    "nleq.count_system_solutions": C.count_system_solutions,
    "nleq.symbolic_intersections": C.symbolic_intersections,
    "nleq.discriminant_constant": C.discriminant_constant,
    "nleq.tangent_constant": C.tangent_constant,
    "nleq.tangent_point": C.tangent_point,
    "nleq.integer_roots_constant": C.integer_roots_constant,
    "nleq.graph_solution": G.graph_solution,
    "nleq.graph_count": G.graph_count,
    "nleq.function_meets": G.function_meets,
}

TOPIC = Topic(
    slug="nonlinear_equations_and_systems",
    name="Nonlinear Equations and Systems",
    domain="Advanced Math",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
