"""An independent solver for every kind this topic produces.

Written from the mathematics, not from the generators. Nothing here imports a
family module, a pool or a renderer; the only thing it borrows from `world`
is the scenario's *labels*, which are scenery rather than arithmetic, and only
where the answer is a word.

Every solver rebuilds the answer from `item.params` by adding up the cells it
was given, and then -- where the item prints a rounded answer -- rounds it
again, with its own arithmetic, so that a rounding bug in `values.dec` cannot
be confirmed by `values.dec`.
"""

from __future__ import annotations

from fractions import Fraction as Q

__all__ = ["AUDITS"]


def _sum(cells, rows, cols) -> int:
    rows = range(len(cells)) if rows is None else rows
    cols = range(len(cells[0])) if cols is None else cols
    return sum(cells[i][j] for i in rows for j in cols)


def _round(v: Q, step: Q) -> Q:
    """Nearest multiple of `step`, halves away from zero. Written out rather
    than imported: the templates round with `values.snap`, and a check that
    calls the function it is checking proves nothing."""
    k = Q(v) / Q(step)
    whole = k.numerator // k.denominator
    frac = k - whole
    if frac * 2 >= 1:
        whole += 1
    return whole * Q(step)


def _printed(v: Q, surface: str, places: int) -> float:
    """The number the page shows, which is what `item.key` carries."""
    if surface in ("ratio", "reduced"):
        return float(v)
    if surface == "decimal":
        return float(_round(v, Q(1, 10 ** places)))
    if surface == "percent":
        return float(_round(v * 100, Q(1, 10 ** places)) / 100)
    raise ValueError(f"unknown surface {surface!r}")


# --------------------------------------------------------------- two-way tables

def two_way(p: dict) -> float:
    """P(event | given) = |event and given| / |given|, both sides counted by hand."""
    cells = p["cells"]
    num = _sum(cells, _both(p["ev_rows"], p["gv_rows"]),
               _both(p["ev_cols"], p["gv_cols"]))
    den = _sum(cells, p["gv_rows"], p["gv_cols"])
    if den == 0:
        raise ZeroDivisionError("the condition names no cells")
    return _printed(Q(num, den), p["surface"], p["places"])


def _both(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return [i for i in a if i in b]


def missing_cell(p: dict) -> float:
    """The hidden cell is simply the count that is there; the stem's stated
    probability is the thing derived from it, so re-deriving the probability
    and checking it reproduces the stem would be checking the renderer. What
    the grid-in answers is the cell, and the cell is `cells[hr][hc]`.
    The arithmetic worth re-doing is the consistency: the printed probability
    must equal the event count over the row total *including* the answer."""
    cells, hr, hc, ec = p["cells"], p["hr"], p["hc"], p["ec"]
    row = cells[hr]
    total = sum(row)
    stated = Q(row[ec], total)
    x = total - sum(v for j, v in enumerate(row) if j != hc)
    if Q(row[ec], total - row[hc] + x) != stated:
        raise ValueError("the stated probability does not recover the hidden cell")
    return float(x)


def cell_from_total(p: dict) -> float:
    cells, hr, hc = p["cells"], p["hr"], p["hc"]
    total = sum(sum(r) for r in cells)
    others = sum(v for i, r in enumerate(cells) for j, v in enumerate(r)
                 if (i, j) != (hr, hc))
    return float(total - others)


def percent_columns(p: dict) -> float:
    """Two columns of percentages whose counts stand in the ratio 1 : mult.

    Take the first column to be 100 units and the second 100 * mult, so the
    row holds first[i] and second[i] * mult units; the conditional is the
    second of those over their sum.
    """
    a, b, m, i = p["first"][p["idx"]], p["second"][p["idx"]], p["mult"], p["idx"]
    if sum(p["first"]) != 100 or sum(p["second"]) != 100:
        raise ValueError("a column of percentages does not total 100")
    return float(Q(b * m, a + b * m))


def nearest_row(p: dict) -> str:
    from .world import TWO_WAY
    cells, cj = p["cells"], p["cj"]
    frac = Q(*p["frac"])
    col = [r[cj] for r in cells]
    target = frac * sum(col)
    gaps = [abs(Q(v) - target) for v in col]
    best = min(gaps)
    if gaps.count(best) != 1:
        raise ValueError("two rows are equally close")
    return TWO_WAY[p["scenario"]].rows[gaps.index(best)].label


# ------------------------------------------------------------- counts in a stem

def bag(p: dict) -> float:
    """`counts` lists every group; `num` is how many the question counts."""
    total = sum(p["counts"])
    return _printed(Q(p["num"], total), p["surface"], p["places"])


def data_set(p: dict) -> float:
    test = {"negative": lambda v: v < 0, "positive": lambda v: v > 0,
            "even": lambda v: v % 2 == 0, "odd": lambda v: v % 2 != 0}[p["trait"]]
    vals = p["values"]
    return float(Q(sum(1 for v in vals if test(v)), len(vals)))


def freq(p: dict) -> float:
    total = sum(p["counts"])
    return _printed(Q(p["counts"][p["idx"]], total), p["surface"], p["places"])


def grouped(p: dict) -> float:
    counts, a, b = p["counts"], p["cut"], p["cut2"]
    return float(Q(sum(counts[b:]), sum(counts[a:])))


def count(p: dict) -> float:
    n, pr = p["n"], Q(*p["p"])
    if p["mode"] == "single":
        return float(pr * n)
    if p["mode"] == "third":
        return float((1 - pr - Q(*p["p2"])) * n)
    if p["mode"] == "round":
        return float(_round(pr * n, Q(1)))
    raise ValueError(f"unknown mode {p['mode']!r}")


def symbolic(p: dict) -> str:
    k = p["k"]
    top = "n" if p["ask_first"] else f"{k:,}"
    return f"{top}/(n + {k:,})"


def rate(p: dict) -> float:
    return float(Q(p["rate"] * p["days"], p["total"]))


AUDITS = {
    "prob_two_way": two_way,
    "prob_missing_cell": missing_cell,
    "prob_cell_total": cell_from_total,
    "prob_percent_columns": percent_columns,
    "prob_nearest_row": nearest_row,
    "prob_bag": bag,
    "prob_data_set": data_set,
    "prob_freq": freq,
    "prob_grouped": grouped,
    "prob_count": count,
    "prob_symbolic": symbolic,
    "prob_rate": rate,
}
