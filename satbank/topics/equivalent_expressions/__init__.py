"""Advanced Math -> Equivalent Expressions.

Seventy official items and twenty-one templates. What the source actually
varies is the *direction* of the rewrite -- expand a product or factor one,
turn a radical into an exponent or an exponent into a radical, divide out a
quotient or put two fractions back over one denominator -- and whether the
answer is the expression itself, a constant hidden inside an identity, or a
combination of the coefficients the rewrite produces.

The audit for this topic never compares strings. Two expressions are
equivalent when they take the same value everywhere they are defined, so
`audit.py` parses what the item prints -- the stem's expression and all four
options -- and puts rational sample points through both.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import basics as B
from .families import constants as C
from .families import factoring as F
from .families import powers as W
from .families import rational as R
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "eqx.combine_like": B.combine_like,
    "eqx.add_polys": B.add_polys,
    "eqx.distribute": B.distribute,
    "eqx.product": B.product,
    "eqx.expand_square": B.expand_square,
    "eqx.substitute": B.substitute,
    "eqx.factor_gcf": F.factor_gcf,
    "eqx.factor_quadratic": F.factor_quadratic,
    "eqx.difference_squares": F.difference_squares,
    "eqx.which_factor": F.which_factor,
    "eqx.complete_square": F.complete_square,
    "eqx.factor_constant": F.factor_constant,
    "eqx.match_constant": C.match_constant,
    "eqx.coef_combination": C.coef_combination,
    "eqx.monomial_power": W.monomial_power,
    "eqx.radical_form": W.radical_form,
    "eqx.exponent_value": W.exponent_value,
    "eqx.telescope": W.telescope,
    "eqx.rational_combine": R.rational_combine,
    "eqx.rational_simplify": R.rational_simplify,
    "eqx.divide_remainder": R.divide_remainder,
}

TOPIC = Topic(
    slug="equivalent_expressions",
    name="Equivalent Expressions",
    domain="Advanced Math",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
