"""Advanced Math -> Nonlinear Functions.

A hundred and ten official items, the largest topic in the set, collapsed to
thirty-five templates in seven families. Three axes run through all of it: the
*surface* the rule is written on (vertex form, factored form, a table, a drawn
curve, an exponent with a period folded into it), what is asked for (a value,
an intercept, a model, a sentence, an equivalent form), and -- the axis that
matters most here -- whether the question is about the mathematics or about
the writing, because "which of the following is equivalent" items have three
equivalent options and only one that *displays* the thing the stem names.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import evaluate as E
from .families import exp_forms as X
from .families import exponential as P
from .families import graphs as G
from .families import intercepts as I
from .families import interpret as N
from .families import polynomial as Y
from .families import quadratic as Q
from .families import word as W
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "nlfunc.evaluate": E.evaluate,
    "nlfunc.exp_evaluate": E.exp_evaluate,
    "nlfunc.solve_value": E.solve_value,
    "nlfunc.param_value": E.param_value,
    "nlfunc.abs_value": E.abs_value,
    "nlfunc.y_intercept": I.y_intercept,
    "nlfunc.x_intercept": I.x_intercept,
    "nlfunc.graph_intercept": G.graph_intercept,
    "nlfunc.graph_context": G.graph_context,
    "nlfunc.graph_zeros": G.graph_zeros,
    "nlfunc.graph_equation": G.graph_equation,
    "nlfunc.exp_model": P.exp_model,
    "nlfunc.exp_period": P.exp_period,
    "nlfunc.exp_from_table": P.exp_from_table,
    "nlfunc.exp_offset": P.exp_offset,
    "nlfunc.exp_anchor": P.exp_anchor,
    "nlfunc.exp_reach": P.exp_reach,
    "nlfunc.exp_rate": X.exp_rate,
    "nlfunc.exp_two_points": X.exp_two_points,
    "nlfunc.exp_display": X.exp_display,
    "nlfunc.exp_rewrite": X.exp_rewrite,
    "nlfunc.exp_steps": X.exp_steps,
    "nlfunc.exp_power_table": X.exp_power_table,
    "nlfunc.vertex_value": Q.vertex_value,
    "nlfunc.vertex_symmetry": Q.vertex_symmetry,
    "nlfunc.shift_max": Q.shift_max,
    "nlfunc.quad_must_be_true": Q.quad_must_be_true,
    "nlfunc.quad_fit": Q.quad_fit,
    "nlfunc.interpret_value": N.interpret_value,
    "nlfunc.interpret_initial": N.interpret_initial,
    "nlfunc.interpret_rate": N.interpret_rate,
    "nlfunc.quad_feature": N.quad_feature,
    "nlfunc.quad_word": W.quad_word,
    "nlfunc.build_expression": W.build_expression,
    "nlfunc.factor_from_table": Y.factor_from_table,
    "nlfunc.zeros_constant": Y.zeros_constant,
}

TOPIC = Topic(
    slug="nonlinear_functions",
    name="Nonlinear Functions",
    domain="Advanced Math",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
