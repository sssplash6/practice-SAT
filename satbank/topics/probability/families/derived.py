"""Four questions that read a two-way table backwards or sideways.

* an unknown cell recovered from a stated conditional probability (`missing_cell`);
* an unknown cell recovered from a grand total the stem states (`cell_from_total`);
* a table of column percentages plus a stated ratio between the two column
  sizes, which is the only way to reach a count from percentages alone
  (`percent_columns`);
* which row of a column comes closest to a stated fraction of that column's
  total (`nearest_row`), whose four options are the row labels themselves.

The last one is the one to watch. Its options are words, so `assemble`'s
ascending order and its lone-surface rule protect nothing, and every one of
the three wrong rows *has* to print -- they are the other rows. So a draw is
refused unless each wrong row is the row some named mistake actually lands on.
An option nobody can explain is not a distractor, it is padding.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import ItemError
from ..values import Q as _Q
from ..values import count as C
from ..values import grid, griddable, mcq, pick, reduced, spr, text_mcq
from ..world import Event, Table, TWO_WAY, ctx, meet
from .simple import order_of
from .twoway import intro_of, setup


# ------------------------------------------------- prob.two_way.missing_cell

def missing_cell(rng: random.Random, seed: int, *, scenario=None, cells=None,
                 hr=None, hc=None, ec=None, tier="hard"):
    """One cell is printed as x; a stated conditional probability recovers it.

    The probability is *derived* from the cells the same way every other
    template derives one -- count of the event within the condition over the
    count of the condition -- and then printed. The unknown is the answer, so
    the stem and the key move together: change a cell and the printed
    probability changes with it.
    """
    c, T = setup(rng, scenario, cells)
    if T.nc < 2:
        raise ItemError("this scenario has only one column to hide a cell in")
    hr = rng.randrange(T.nr) if hr is None else hr
    hc = rng.randrange(T.nc) if hc is None else hc
    ec = rng.choice([j for j in range(T.nc) if j != hc]) if ec is None else ec
    if ec == hc:
        raise ItemError("the stated probability must not be about the hidden cell")
    row, col = c.rows[hr], c.cols[ec]

    given = Event(rows=row.idx)
    num, den = T.count(meet(Event(cols=col.idx), given)), T.count(given)
    p = Q(num, den)
    x = T.cells[hr][hc]
    if x < 1 or not 0 < p < 1:
        raise ItemError("the hidden cell must hold at least one unit and the stated "
                        "probability must be strictly between 0 and 1")
    if p.denominator > 24 or p.numerator > 12:
        raise ItemError("the stated probability is not one a stem would print")
    if not griddable(x):
        raise ItemError("this cell count is not enterable in five characters")

    shown = f"{p.numerator}/{p.denominator}"
    stem = (f"{intro_of(c, T)} If one of the {row.g} is chosen at random, the "
            f"probability that {c.subject} {col.p} is {shown}. What is the value "
            f"of x ?")
    P = {"kind": "prob_missing_cell", "scenario": c.key,
         "cells": [list(r) for r in T.cells], "hr": hr, "hc": hc, "ec": ec}
    rationale = (f"Once x is counted there are {den:,} {row.g}, and {num:,} of them "
                 f"{col.plural()}, so {num}/({den - x} + x) = {shown} and "
                 f"x = {x:,}.")
    table = T.printed(c, margins=False, hide=(hr, hc), mark="x")
    return spr("prob.two_way.missing_cell", "two-way table", tier, seed, stem, x,
               rationale, params=P, table=table)


# --------------------------------------------- prob.two_way.cell_from_total

def cell_from_total(rng: random.Random, seed: int, *, scenario=None, cells=None,
                    hr=None, hc=None, wrongs=None, tier="easy"):
    """The grand total is in the stem and one cell is printed as a question mark."""
    c, T = setup(rng, scenario, cells)
    if "{n}" not in c.intro:
        raise ItemError("this scenario's prose never states the grand total, and "
                        "without it the missing cell cannot be recovered from the "
                        "page")
    hr = rng.randrange(T.nr) if hr is None else hr
    hc = rng.randrange(T.nc) if hc is None else hc
    x, N = T.cells[hr][hc], T.total
    if x < 1:
        raise ItemError("the hidden cell must hold at least one unit")
    row, col = c.rows[hr], c.cols[hc]

    others = N - x
    pool = {
        "sum_others": (f"gave the total of the three cells that are printed",
                       others),
        "minus_row": (f"subtracted only the {T.row_total(1 - hr) if T.nr == 2 else 0:,} "
                      f"in the other row from {N:,}",
                      N - T.row_total(1 - hr) if T.nr == 2 else None),
        "minus_col": (f"subtracted only the {T.col_total(1 - hc) if T.nc == 2 else 0:,} "
                      f"in the other column from {N:,}",
                      N - T.col_total(1 - hc) if T.nc == 2 else None),
        "minus_cell": (f"subtracted only the cell for {c.rows[1 - hr].label if T.nr == 2 else ''} "
                       f"and {col.label} from {N:,}",
                       N - T.cells[1 - hr][hc] if T.nr == 2 else None),
        "minus_same_row": (f"subtracted only the rest of the same row from {N:,}",
                           N - (T.row_total(hr) - x)),
        "half": (f"split the total evenly between the two columns",
                 N // T.nc if N % T.nc == 0 else None),
    }
    for k, v in list(pool.items()):
        if v[1] is not None and not 0 < v[1] or v[1] == x:
            pool[k] = (v[0], None)

    stem = (f"{intro_of(c, T)} How many of the {col.g} {row.plural()}?")
    P = {"kind": "prob_cell_total", "scenario": c.key,
         "cells": [list(r) for r in T.cells], "hr": hr, "hc": hc}
    rationale = (f"The other cells account for {others:,} of the {N:,} {c.units}, so "
                 f"the missing cell is {N:,} − {others:,} = {x:,}.")
    table = T.printed(c, margins=False, hide=(hr, hc), mark="?")
    mistakes = [(why, C(v)) for why, v in
                pick(pool, wrongs or order_of(pool, ["minus_row", "minus_cell",
                                                     "sum_others", "minus_col"]),
                     wrongs) if v]
    return mcq("prob.two_way.cell_from_total", "two-way table", tier, seed, stem,
               C(x), mistakes, rng, rationale, params=P, table=table)


# -------------------------------------------- prob.two_way.percent_columns

PCT = {
    "alumni": ("An alumni association survey asked each high school graduate to "
               "select the one activity he or she preferred for the association's "
               "next event. Some of the people responded by phone, and the others "
               "responded by email. The table shows the distribution of preferred "
               "activity, in percent, for each response type used.",
               [("Dinner dance", "a dinner dance"),
                ("Football game", "a football game"), ("Picnic", "a picnic"),
                ("Pool party", "a pool party")],
               ["Phone", "Email"], "person", "people",
               "responded by phone", "responded by email",
               "For the survey, the number of email responses was {mult} the "
               "number of phone responses.",
               "If a person who preferred {row} is selected at random, what is the "
               "probability that the person responded by email?"),
    "club": ("A club asked each member to choose one meeting time. Some of the "
             "members answered in person and the others answered online. The table "
             "shows the distribution of preferred meeting time, in percent, for each "
             "way of answering.",
             [("Monday morning", "Monday morning"),
              ("Tuesday evening", "Tuesday evening"),
              ("Thursday evening", "Thursday evening"),
              ("Saturday morning", "Saturday morning")],
             ["In person", "Online"], "member", "members",
             "answered in person", "answered online",
             "Overall, the number of online answers was {mult} the number of "
             "in-person answers.",
             "If a member who preferred {row} is selected at random, what is the "
             "probability that the member answered online?"),
}
MULT = {2: "twice", 3: "three times", 4: "four times"}


def percent_columns(rng: random.Random, seed: int, *, scenario=None, first=None,
                    second=None, mult=None, idx=None, tier="hard"):
    """Column percentages plus a stated ratio between the two column sizes."""
    key_s = scenario or rng.choice(sorted(PCT))
    intro, pairs, cols, unit, units, _, _, ratio_txt, ask = PCT[key_s]
    rows = [lab for lab, _ in pairs]
    mult = mult or rng.choice(sorted(MULT))
    first = list(first) if first else _split(rng, len(rows))
    second = list(second) if second else _split(rng, len(rows))
    if sum(first) != 100 or sum(second) != 100:
        raise ItemError("each column of percentages must total 100")
    idx = rng.randrange(len(rows)) if idx is None else idx
    a, b = first[idx], second[idx]
    num, den = b * mult, a + b * mult
    if a == 0 and b == 0:
        raise ItemError("nobody preferred this activity, so the condition is empty")
    if not 0 < Q(num, den) < 1 or not griddable(Q(num, den)):
        raise ItemError("this probability is 0, 1, or not enterable in five "
                        "characters")

    table = [[""] + cols]
    for lab, x, y in zip(rows, first, second):
        table.append([lab, f"{x}%", f"{y}%"])
    table.append(["Total", "100%", "100%"])
    stem = (f"{intro} {ratio_txt.format(mult=MULT[mult])} "
            f"{ask.format(row=pairs[idx][1])} (Express your answer as a decimal "
            f"or fraction, not as a percent.)")
    P = {"kind": "prob_percent_columns", "first": first, "second": second,
         "mult": mult, "idx": idx}
    key = Q(num, den)
    rationale = (f"For every 100 {units} in the first column there are {mult} "
                 f"× 100 in the second, so the counts are in the ratio "
                 f"{a} to {b} × {mult} = {b * mult}, and the probability is "
                 f"{grid(key)}.")
    return spr("prob.two_way.percent_columns", "two-way table", tier, seed, stem,
               key, rationale, params=P, table=table)


def _split(rng: random.Random, k: int) -> list[int]:
    """k percentages, each a multiple of 5, totalling 100."""
    parts = [1] * k
    for _ in range(20 - k):
        parts[rng.randrange(k)] += 1
    return [p * 5 for p in parts]


# ------------------------------------------------ prob.two_way.nearest_row

FRACS = {Q(1, 2): "one half", Q(1, 3): "one third", Q(1, 4): "one fourth",
         Q(2, 3): "two thirds", Q(1, 5): "one fifth", Q(3, 4): "three fourths"}


def nearest_row(rng: random.Random, seed: int, *, scenario=None, cells=None, cj=None,
                frac=None, tier="medium"):
    """Which row's count in one column comes closest to a fraction of that column?

    Every option is a row label, so all three wrong rows print whether or not
    a mistake explains them. The draw is refused unless each of them is the
    row that some named mistake lands on -- see the module docstring.
    """
    c, T = setup(rng, scenario, cells)
    if T.nr < 4:
        raise ItemError("this question needs four rows to make four options")
    if any("pi" in r.label for r in c.rows):
        raise ItemError("an option containing the letters 'pi' reads as a "
                        "mathematical option to the gate's surface check")
    cj = rng.randrange(T.nc) if cj is None else cj
    frac = Q(frac) if frac else rng.choice(sorted(FRACS))
    col = c.cols[cj]
    colv = [T.cells[i][cj] for i in range(T.nr)]
    target = frac * T.col_total(cj)

    def nearest(vals, t):
        d = [abs(Q(v) - t) for v in vals]
        best = min(d)
        if d.count(best) != 1:
            raise ItemError("two rows are equally close, so there is no single "
                            "nearest row")
        return d.index(best)

    key_i = nearest(colv, target)
    gaps = sorted(abs(Q(v) - target) for v in colv)
    # "closest to" needs a clear winner. 59 against a target of 60, with the
    # runner-up 6 away, is an item; 17 against 23 with the runner-up 10 away
    # is a judgement call printed as a fact.
    if gaps[1] < 2 * gaps[0]:
        raise ItemError("the two nearest rows are too close together for one of "
                        "them to be the answer")
    other = 1 - cj if T.nc == 2 else (cj + 1) % T.nc
    rules = [
        (nearest([T.row_total(i) for i in range(T.nr)], target),
         f"compared the total for each row with {FRACS[frac]} of the {col.label} "
         f"column instead of comparing only the {col.label} counts"),
        (nearest([T.cells[i][other] for i in range(T.nr)], target),
         f"read the {c.cols[other].label} column instead of the {col.label} column"),
        (nearest(colv, frac * T.total),
         f"took {FRACS[frac]} of all {T.total:,} {c.units} instead of "
         f"{FRACS[frac]} of the {T.col_total(cj):,} {col.g}"),
        (nearest(colv, frac * target),
         f"divided by {frac.denominator} a second time"),
        (max(range(T.nr), key=lambda i: colv[i]),
         f"chose the largest group rather than the one nearest {FRACS[frac]} of "
         f"the column"),
        (nearest([Q(T.cells[i][cj]) - frac * T.row_total(i) for i in range(T.nr)], 0),
         f"compared each {col.label} count with {FRACS[frac]} of its own row total "
         f"instead of {FRACS[frac]} of the {col.label} column"),
    ]
    reasons: dict[int, str] = {}
    for i, why in rules:
        if i != key_i and i not in reasons:
            reasons[i] = why
    missing = [i for i in range(T.nr) if i != key_i and i not in reasons]
    if missing:
        raise ItemError("no named mistake lands on the row labelled "
                        f"{c.rows[missing[0]].label}, so it would print as padding")

    stem = (f"{intro_of(c, T)} Which {c.row_head.lower() or 'row'} has a "
            f"{col.label.lower()} count that is closest to being {FRACS[frac]} of "
            f"the total {col.label.lower()} count in the table?")
    P = {"kind": "prob_nearest_row", "scenario": c.key,
         "cells": [list(r) for r in T.cells], "cj": cj,
         "frac": [frac.numerator, frac.denominator]}
    rationale = (f"{FRACS[frac].capitalize()} of {T.col_total(cj):,} is "
                 f"{_num(target)}. {c.rows[key_i].label}'s {col.label.lower()} count "
                 f"of {colv[key_i]:,} is {_num(gaps[0])} away from that, and every "
                 f"other row is further.")
    wrong = [(reasons[i], c.rows[i].label) for i in range(T.nr) if i != key_i]
    return text_mcq("prob.two_way.nearest_row", "two-way table", tier, seed, stem,
                    c.rows[key_i].label, wrong, rng, rationale, params=P, table=
                    T.printed(c, margins=True))


def _num(v: Q) -> str:
    if v.denominator == 1:
        return f"{v.numerator:,}"
    return f"{float(v):.2f}".rstrip("0").rstrip(".")
