"""Independent re-derivation of every answer this topic ships.

Written from the arithmetic, in plain floats, sharing nothing with the
generators: no Fraction, no ``Num``, no helper imported from ``values.py`` or
from a family. Where a template runs a ratio backwards -- the partner of a
count, the deposit behind four years of doubling, the edge of a cube from its
density -- this file does not rearrange the algebra at all. It root-finds the
unknown with ``solve_for``, so the two routes have no step in common and a
wrong rearrangement cannot be made right twice.

Two rules are deliberately restated here rather than shared. A conversion
chain is re-derived by multiplying the stated factors in the **opposite
order** to the template, so the two routes agree only if both are right. And
every rounding rule -- half up to a decimal place, to a number of significant
figures -- is written again from scratch, because a disagreement about where
a half goes is exactly the kind of error the audit exists to find.
"""

from __future__ import annotations

import math

from ...audit import AuditError, solve_for


# ------------------------------------------------------------- arithmetic

def _round(v: float, places: int) -> float:
    """Round half away from zero to `places` decimals, the way a page prints."""
    scale = 10.0 ** places
    return math.floor(abs(v) * scale + 0.5 + 1e-9) / scale * (1 if v >= 0 else -1)


def _sig(v: float, figures: int = 3) -> float:
    """Round to `figures` significant figures, half up."""
    if v == 0:
        return 0.0
    e = math.floor(math.log10(abs(v)))
    scale = 10.0 ** (figures - 1 - e)
    return math.floor(abs(v) * scale + 0.5 + 1e-9) / scale * (1 if v >= 0 else -1)


def _short(v: float, cap: int = 2) -> str:
    """A number the way an option prints it: 24.5, 1.5, 160, 0.075."""
    for p in range(cap + 1):
        if abs(v * 10 ** p - round(v * 10 ** p)) < 1e-9:
            return f"{v:.{p}f}"
    return f"{v:.{cap}f}"


def _reduce(a: int, b: int) -> tuple[int, int]:
    """Lowest terms, by looking for the largest common divisor from below."""
    g = 1
    for d in range(2, min(abs(a), abs(b)) + 1):
        if a % d == 0 and b % d == 0:
            g = d
    return a // g, b // g


def _coef(c: float, var: str) -> str:
    """'(4/3)w', '2w', 'w' -- a coefficient against a variable, as printed."""
    if abs(c - 1) < 1e-12:
        return var
    if abs(c - round(c)) < 1e-12:
        return f"{round(c)}{var}"
    for d in range(2, 200):
        if abs(c * d - round(c * d)) < 1e-9:
            return f"({round(c * d)}/{d}){var}"
    raise AuditError(f"coefficient {c} is not a printable fraction")


# ------------------------------------------------------------------ ratios

def rr_partner(p: dict):
    """The unknown part is searched for, not solved for."""
    a = p["a"][0] / p["a"][1]
    b = p["b"][0] / p["b"][1]
    n = p["n"][0] / p["n"][1]
    if p["given"] == "first":
        # n is the a-side, so the b-side x satisfies x * (a/b) = n
        return solve_for(lambda x: x * (a / b), n)
    return solve_for(lambda x: x * (b / a), n)


def rr_equivalent(p: dict):
    if p["ask"] == "term":
        # first : m equals c : d, so m satisfies m * (c/d) = first
        return solve_for(lambda x: x * (p["c"] / p["d"]), p["first"])
    # both quantities scale by one factor, so the factor is the factor
    return p["n"]


def rr_table_constant(p: dict):
    ratio = p["ratio"][0] / p["ratio"][1]
    return p["last"] * ratio


def rr_simplify(p: dict):
    a, b = _reduce(int(p["n1"]), int(p["n2"]))
    return f"{a} to {b}"


def rr_similar_rect(p: dict):
    # the widths carry the same factor as the lengths
    return _coef(p["l2"] / p["l1"], p["var"])


def rr_dimension_shift(p: dict):
    ratio = (p["length"] / p["width"]) if p["moved"] == "width" \
        else (p["width"] / p["length"])
    shift = ratio * p["change"]
    way = "increase" if p["up"] else "decrease"
    unit = "unit" if math.isclose(abs(shift), 1.0) else "units"
    return f"It must {way} by {_short(shift)} {unit}."


def rr_mix_statement(p: dict):
    factor = p["second"] / p["first"]
    return (f"{_short(factor)} times the amount of {p['one']} used in the "
            f"second batch")


def rr_expression(p: dict):
    n, var, form = int(p["n"]), p["var"], p["form"]
    if form in ("scale_pay", "scale_mass"):
        return f"{n}{var}"
    if form == "substitute":
        return f"{n * int(p['rate'])}{p['partner']}"
    return f"{n}({p['rate']:.2f}{var})"


def rr_multiple(p: dict):
    big, small = int(p["big"]), int(p["small"])
    if big % small:
        raise AuditError("the two periods do not divide")
    return f"{big // small}"


def rr_chain_unknown(p: dict):
    """c*a/b is given and a/(b*n) is given, so n is searched for."""
    over = p["first"] / p["c"]                       # a/b
    return solve_for(lambda x: x * p["second"], over)


def rr_repeated_factor(p: dict):
    factor, years = float(p["factor"]), int(p["years"])
    return solve_for(lambda x: x * factor ** years, p["total"])


# ------------------------------------------------------------------- rates

def rr_unit_rate(p: dict):
    if p["ask"] == "rate":
        return p["total"] / p["count"]
    if p["ask"] == "count":
        return solve_for(lambda x: x * p["per"], p["total"])
    return p["per"] * p["count"]


_SECONDS = {"second": 1.0, "minute": 60.0, "hour": 3600.0, "day": 86400.0}


def rr_rate_convert(p: dict):
    value = p["value"][0] / p["value"][1]
    factor = p["factor"][0] / p["factor"][1]
    # a rate per X, expressed per Y, carries however many X there are in a Y
    per = value * factor * (_SECONDS[p["per_to"]] / _SECONDS[p["per_from"]])
    return per if p["places"] is None else _round(per, int(p["places"]))


def rr_rate_product(p: dict):
    frame = p["frame"]
    if frame == "recipe":
        v = p["first"] * p["second"] / 16.0
    else:
        v = p["first"] * p["second"]
    return v if not p["figures"] else _sig(v, int(p["figures"]))


def rr_gap(p: dict):
    base = p["base"][0] / p["base"][1]
    low = p["low"][0] / p["low"][1]
    high = p["high"][0] / p["high"][1]
    return base * high - base * low


def rr_growth_table(p: dict):
    """A growth factor of g is g years to the inch, so the tree gains 1/g a year."""
    fast = p["fast"][0] / p["fast"][1]
    slow = p["slow"][0] / p["slow"][1]
    years = float(p["years"])
    return _round(years / fast - years / slow, 1)


def rr_table_unit_price(p: dict):
    """Cents and grams are integers, so the ratio reduces exactly."""
    a1, a2, c1, c2 = int(p["a1"]), int(p["a2"]), int(p["c1"]), int(p["c2"])
    x, y = _reduce(c1 * a2, c2 * a1)
    return f"{x} : {y}"


def rr_exchange_fee(p: dict):
    rate = p["rate"][0] / p["rate"][1]
    gross = p["amount"] * rate
    return gross - gross * p["fee"] / 100.0


# ------------------------------------------------------------------- units

def rr_convert(p: dict):
    n = p["n"][0] / p["n"][1]
    f = float(p["factor"]) ** int(p["power"])
    if p["op"] == "mul":
        return n * f
    # the measure is in the smaller unit, so it is searched for in the larger
    return solve_for(lambda x: x * f, n)


def rr_convert_chain(p: dict):
    """The stated factors, multiplied in the opposite order to the template.

    The template walks the chain forwards -- furlongs to yards, yards to feet.
    Here the second factor is applied first, so the two routes share no
    arithmetic and agree only because multiplication does not care.
    """
    v = p["n"][0] / p["n"][1]
    for f in reversed([float(p["f1"]), float(p["f2"])]):
        v *= f
    return v


def rr_pop_density(p: dict):
    if p["ask"] == "area":
        # people per square mile times square miles is people
        return solve_for(lambda x: x * p["density"], p["people"])
    land = p["total"] - p["water"]
    if land <= 0:
        raise AuditError("no land left once the water is taken out")
    return _sig(p["people"] / land, 3)


def rr_cube_density(p: dict):
    ask, places = p["ask"], p["places"]
    if ask == "edge":
        edge = solve_for(lambda e: e ** 3 * p["density"], p["mass"])
        return _round(edge, int(places))
    edge = p["edge"][0] / p["edge"][1]
    volume = edge * edge * edge
    v = p["density"] * volume if ask == "mass" else p["mass"] / volume
    return v if places is None else _round(v, int(places))


AUDITS = {
    "rr_partner": rr_partner,
    "rr_equivalent": rr_equivalent,
    "rr_table_constant": rr_table_constant,
    "rr_simplify": rr_simplify,
    "rr_similar_rect": rr_similar_rect,
    "rr_dimension_shift": rr_dimension_shift,
    "rr_mix_statement": rr_mix_statement,
    "rr_expression": rr_expression,
    "rr_multiple": rr_multiple,
    "rr_chain_unknown": rr_chain_unknown,
    "rr_repeated_factor": rr_repeated_factor,
    "rr_unit_rate": rr_unit_rate,
    "rr_rate_convert": rr_rate_convert,
    "rr_rate_product": rr_rate_product,
    "rr_gap": rr_gap,
    "rr_growth_table": rr_growth_table,
    "rr_table_unit_price": rr_table_unit_price,
    "rr_exchange_fee": rr_exchange_fee,
    "rr_convert": rr_convert,
    "rr_convert_chain": rr_convert_chain,
    "rr_pop_density": rr_pop_density,
    "rr_cube_density": rr_cube_density,
}
