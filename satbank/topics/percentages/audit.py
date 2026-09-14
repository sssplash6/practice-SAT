"""Independent re-derivation of every Percentages answer.

Written from the arithmetic, in plain floats, sharing nothing with the
generators: no Fraction, no `Num`, no helper imported from `values.py`. Where
a template runs a percent backwards -- the whole from a part, the original
from what remains -- this file does not rearrange the algebra at all. It
root-finds the unknown with `solve_for`, so the two routes have no step in
common and a wrong rearrangement cannot be made right twice.

The two rounding rules are restated here rather than shared, because a
disagreement about where a half goes is exactly the kind of error the audit
exists to find.
"""

from __future__ import annotations

import math

from ...audit import AuditError, close, solve_for


def _snap(v: float, step: float) -> float:
    """Round to a multiple of `step`, halves upward."""
    return math.floor(v / step + 0.5 + 1e-9) * step


def _round(v, places) -> float:
    """Round to `places` decimals, or leave alone when the item does not round."""
    if places is None:
        return float(v)
    return _snap(float(v), 10.0 ** -int(places))


def _d(x: float) -> str:
    """A coefficient the way an option prints it: 0.89, 8.9, 1.09, 5."""
    s = f"{float(x):.6f}".rstrip("0").rstrip(".")
    return s or "0"


# --------------------------------------------------------- one step

def pct_of(p: dict):
    part = p["n"] * p["p"] / 100.0
    v = part * 60.0 if p["frame"] == "workday" else part
    return _snap(v, p["round_to"]) if p["round_to"] else v


def pct_find(p: dict):
    return _round(100.0 * p["part"] / p["whole"], p["round"])


def pct_shift(p: dict):
    step = 1.0 if p["up"] else -1.0
    v = p["n"] + step * p["n"] * p["p"] / 100.0
    return _snap(v, p["round_to"]) if p["round_to"] else v


def pct_reverse(p: dict):
    """The whole is unknown, so it is searched for rather than solved for."""
    result, pct, frame = p["result"], p["p"], p["frame"]
    if frame == "is_p_of":
        whole = solve_for(lambda x: x * pct / 100.0, result)
    elif frame == "increased_to":
        whole = solve_for(lambda x: x + x * pct / 100.0, result)
    else:
        whole = solve_for(lambda x: x - x * pct / 100.0, result)
    if p["round_to"]:
        whole = _snap(whole, p["round_to"])
    if frame == "removed_remained" and p["ask"] == "removed":
        return whole - result
    return whole


def pct_change(p: dict):
    old, new = p["old"], p["new"]
    return _round(100.0 * abs(new - old) / old, p["round"])


def pct_multiplier(p: dict):
    n, pct = p["n"], p["p"]
    other = n + n * pct / 100.0 if p["up"] else n - n * pct / 100.0
    if p["ask"] == "factor":
        return other / n
    return 100.0 * (other - n) / n


def pct_expression(p: dict):
    pct, var, form = p["p"], p["var"], p["form"]
    if form == "of":
        return f"{_d(pct / 100.0)}{var}"
    if form == "increase":
        return f"{_d(1.0 + pct / 100.0)}{var}"
    return f"{_d(1.0 - pct / 100.0)}{var}"


# ------------------------------------------------------------ chains

def pct_chain(p: dict):
    pcts, ask = p["pcts"], p["ask"]
    if ask == "count":
        v = p["base"]
        for one in pcts:
            v = v * one / 100.0
        return v
    v = 100.0
    for one in pcts:
        v = v * one / 100.0
    return _round(100.0 - v if ask == "complement" else v, p["round"])


def pct_successive(p: dict):
    pcts, ups, ask = p["pcts"], p["ups"], p["ask"]
    if len(pcts) == 1:                       # the same percent, year after year
        v = p["start"]
        for _ in range(p["years"]):
            v = v + v * pcts[0] / 100.0 if ups[0] else v - v * pcts[0] / 100.0
        return _round(v, p["round"])
    v = 1.0
    for one, up in zip(pcts, ups):
        v = v + v * one / 100.0 if up else v - v * one / 100.0
    if ask == "net_percent":
        return _round(abs(100.0 * (v - 1.0)), p["round"])
    return _round(p["start"] * v, p["round"])


def pct_two_step(p: dict):
    v = 1.0
    for one, up in ((p["p1"], p["up1"]), (p["p2"], p["up2"])):
        v = v + v * one / 100.0 if up else v - v * one / 100.0
    return v if p["start"] is None else v * p["start"]


def pct_markup(p: dict):
    consumer = p["cost"] * p["markup"] / 100.0
    return consumer - consumer * p["discount"] / 100.0


def pct_repeated(p: dict):
    return p["units"] * p["p"] / 100.0 * (p["months"] + 1)


def pct_remainder(p: dict):
    pcts, ask = p["pcts"], p["ask"]
    rest = 100.0 - sum(pcts)
    if rest <= 0:
        raise AuditError("the categories given already use up the whole group")
    total = solve_for(lambda x: x * rest / 100.0, p["left"])
    counts = [total * one / 100.0 for one in pcts]
    if ask == "total":
        return total
    if ask == "one_group":
        return counts[1]
    return counts[1] - counts[2]


def pct_per_unit(p: dict):
    return f"p = {_d(p['per'])}x"


# -------------------------------------------------------------- data

def pct_table(p: dict):
    ask = p["ask"]
    if ask == "ratio":
        return _round(100.0 * p["a"] / p["b"], p["round"])
    if ask == "row_share":
        return _round(100.0 * p["cell"] / p["row_total"], p["round"])
    a = 100.0 * p["a_cell"] / p["a_total"]
    b = 100.0 * p["b_cell"] / p["b_total"]
    return _round(abs(a - b), p["round"])


def pct_percent_table(p: dict):
    share = sum(p["pcts"][i] for i in p["picks"])
    if abs(sum(p["pcts"]) - 100.0) > 1e-9:
        raise AuditError("the percentages in the table do not total 100")
    if p["ask"] == "neither":
        share = 100.0 - share
    return p["total"] * share / 100.0


def pct_series(p: dict):
    if p["ask"] == "project":
        v0, v1 = p["v0"], p["v1"]
        rate = (v1 - v0) / v0 / p["multiple"]
        return _round(v1 + v1 * rate, p["round"])
    return _round(100.0 * abs(p["b"] - p["a"]) / p["a"], p["round"])


def pct_conclusion(p: dict):
    who, name = p["who"], p["name"]
    hi, lo = ((p["phr_a"], p["phr_b"]) if p["rate_a"] >= p["rate_b"]
              else (p["phr_b"], p["phr_a"]))
    if p["rate_a"] == p["rate_b"]:
        raise AuditError("neither group prefers the candidate more strongly")
    return (f"{who.capitalize()} {hi} were more likely to prefer {name} than were "
            f"{who} {lo}.")


AUDITS = {
    "pct_of": pct_of,
    "pct_find": pct_find,
    "pct_shift": pct_shift,
    "pct_reverse": pct_reverse,
    "pct_change": pct_change,
    "pct_multiplier": pct_multiplier,
    "pct_expression": pct_expression,
    "pct_chain": pct_chain,
    "pct_successive": pct_successive,
    "pct_two_step": pct_two_step,
    "pct_markup": pct_markup,
    "pct_repeated": pct_repeated,
    "pct_remainder": pct_remainder,
    "pct_per_unit": pct_per_unit,
    "pct_table": pct_table,
    "pct_percent_table": pct_percent_table,
    "pct_series": pct_series,
    "pct_conclusion": pct_conclusion,
}
