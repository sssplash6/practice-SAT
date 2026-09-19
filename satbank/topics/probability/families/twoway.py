"""Probability read off a two-way table: marginal, joint and conditional.

The conditional is the whole topic. P(A|B) and P(B|A) use the same cell as
their numerator and differ only in the denominator, and choosing the wrong
denominator is the commonest mistake a student makes -- which is exactly why
it must not be a mistake the *engine* can make quietly. So no template here
ever names a denominator. A question is an event and a condition, both of
them sets of cells (`world.Event`), and the value is

    table.count(meet(event, given)) / table.count(given)

with `given` the whole table when the question is unconditional. The reversed
conditional is then not a bug that can hide; it is `reverse`, a named member
of the distractor pool, and it prints as a wrong answer with the teacher's
sentence beside it.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import ItemError
from ..values import (decimal, mcq, percent, pick, ratio, reduced, spr,
                      unambiguous, griddable)
from ..world import Event, Table, TWO_WAY, ctx, meet

SURFACES = ("ratio", "reduced", "decimal", "percent")
PLACES = {"decimal": 2, "percent": 1}


# ------------------------------------------------------------- the surface

def render(num, den, surface: str, places: int):
    """One (numerator, denominator) pair as the page prints it."""
    if den == 0:
        raise ItemError("a probability with an empty denominator")
    if surface == "ratio":
        return ratio(num, den)
    if surface == "reduced":
        return reduced(Q(num, den))
    if surface == "decimal":
        return decimal(Q(num, den), places)
    if surface == "percent":
        return percent(Q(num, den), places)
    raise ItemError(f"no surface named {surface!r}")


def guard_surface(num, den, surface, places, approx):
    """Refuse a draw whose key cannot be printed in the surface it asked for.

    A decimal or a percent is a *rounded* answer, and an item may print one
    only when it says so. Three separate topics shipped a "closest to" item
    whose true value sat exactly on the boundary between two printable
    answers, so the halfway case is refused here rather than rounded by a
    convention the stem never states.
    """
    v = Q(num, den)
    if surface == "decimal":
        if approx:
            unambiguous(v, Q(1, 10 ** places))
        elif (v * 10 ** places).denominator != 1:
            raise ItemError("this probability does not print exactly as a decimal, "
                            "and the stem does not say the answer is approximate")
    elif surface == "percent":
        unambiguous(v * 100, Q(1, 10 ** places))


# ------------------------------------------------------------ the scenarios

def setup(rng: random.Random, scenario, cells):
    c = ctx(scenario) if scenario else ctx(rng.choice(sorted(TWO_WAY)))
    if cells is None:
        cells = [[rng.randint(c.lo, c.hi) for _ in range(len(c.cols))]
                 for _ in range(len(c.rows))]
    T = Table(cells)
    if T.nr != len(c.rows) or T.nc != len(c.cols):
        raise ItemError(f"{c.key} has {len(c.rows)}x{len(c.cols)} categories but the "
                        f"cells are {T.nr}x{T.nc}")
    if any(T.row_total(i) == 0 for i in range(T.nr)) or \
       any(T.col_total(j) == 0 for j in range(T.nc)):
        raise ItemError("an empty row or column makes an unanswerable table")
    return c, T


def intro_of(c, T) -> str:
    return c.intro.format(n=f"{T.total:,}", r=f"{T.row_total(0):,}")


def sentence(select: str, question: str) -> str:
    """Attach the question to the clause that sets it up, capitalising if the
    scenario's clause is a whole sentence of its own."""
    if select.rstrip().endswith("."):
        return f"{select} {question[0].upper()}{question[1:]}"
    return f"{select} {question}"


def params_of(kind, c, T, ev, given, surface, places, approx=False):
    return {"kind": kind, "scenario": c.key, "cells": [list(r) for r in T.cells],
            "ev_rows": None if ev.rows is None else list(ev.rows),
            "ev_cols": None if ev.cols is None else list(ev.cols),
            "gv_rows": None if given.rows is None else list(given.rows),
            "gv_cols": None if given.cols is None else list(given.cols),
            "surface": surface, "places": places, "approx": bool(approx)}


# ------------------------------------------------------------ prob.two_way.marginal

def marginal(rng: random.Random, seed: int, *, scenario=None, cells=None, axis=None,
             idx=None, surface=None, places=None, frame=None, margins=True,
             fmt="mcq", wrongs=None, tier="easy"):
    """P(one category), over every unit in the table."""
    c, T = setup(rng, scenario, cells)
    axis = axis or rng.choice(("row", "col"))
    sels = c.rows if axis == "row" else c.cols
    idx = rng.randrange(len(sels)) if idx is None else idx
    sel = sels[idx]
    ev = Event(rows=sel.idx) if axis == "row" else Event(cols=sel.idx)
    surface = surface or rng.choice(SURFACES)
    places = PLACES.get(surface, 0) if places is None else places
    num, N = T.count(ev), T.total
    if not 0 < num < N:
        raise ItemError("a probability of 0 or 1 is not what this question asks")
    guard_surface(num, N, surface, places, False)

    pool = {"not": (f"found the probability of the complement, that the {c.unit} "
                    f"is not among the {sel.g}", (N - num, N)),
            "one": (f"treated the answer as one {c.unit} out of the {N:,}", (1, N))}
    for i, r in enumerate(c.rows):
        pool[f"row{i}"] = (f"used the number of {r.g} instead of the number of "
                           f"{sel.g}", (T.row_total(i), N))
        pool[f"row{i}/"] = (f"divided the number of {sel.g} by the number of {r.g} "
                            f"instead of by the {N:,} {c.units}", (num, T.row_total(i)))
        pool[f"/row{i}"] = (f"divided the number of {r.g} by the number of {sel.g}, "
                            f"turning the question upside down", (T.row_total(i), num))
    for j, col in enumerate(c.cols):
        pool[f"col{j}"] = (f"used the number of {col.g} instead of the number of "
                           f"{sel.g}", (T.col_total(j), N))
        pool[f"col{j}/"] = (f"divided the number of {sel.g} by the number of {col.g} "
                            f"instead of by the {N:,} {c.units}", (num, T.col_total(j)))
        pool[f"/col{j}"] = (f"divided the number of {col.g} by the number of {sel.g}, "
                            f"turning the question upside down", (T.col_total(j), num))
    for i in range(T.nr):
        for j in range(T.nc):
            v = T.cells[i][j]
            pool[f"cell{i}{j}"] = (f"read a single cell of the table, {c.rows[i].label} "
                                   f"and {c.cols[j].label}, instead of a whole total",
                                   (v, N))
            pool[f"cell{i}{j}/row"] = (f"read a single cell and divided by the total "
                                       f"for its own row instead of by the {N:,} "
                                       f"{c.units}", (v, T.row_total(i)))
            pool[f"cell{i}{j}/col"] = (f"read a single cell and divided by the total "
                                       f"for its own column instead of by the {N:,} "
                                       f"{c.units}", (v, T.col_total(j)))
    pool.pop(f"{axis}{idx}", None)
    pool.pop(f"{axis}{idx}/", None)
    pool.pop(f"/{axis}{idx}", None)

    order = wrongs or _order(pool, [f"{'col' if axis == 'row' else 'row'}0",
                                    f"{'col' if axis == 'row' else 'row'}1",
                                    "not", "one", "cell00", "cell01/row", "cell10/col"])
    stem = sentence(c.select.format(n=f"{T.total:,}"),
                    _ask(c, sel, frame or rng.choice(("pred", "noun"))))
    stem = f"{intro_of(c, T)} {stem}"
    key = render(num, N, surface, places)
    P = params_of("prob_two_way", c, T, ev, Event(), surface, places)
    rationale = (f"{num:,} of the {N:,} {c.units} {sel.plural()}, so the probability "
                 f"is {key.plain()}.")
    table = T.printed(c, margins=margins)
    if fmt == "spr":
        if not griddable(Q(num, N)):
            raise ItemError("this probability is not enterable in five characters")
        return spr("prob.two_way.marginal", "two-way table", tier, seed,
                   stem + _GRID_NOTE, Q(num, N), rationale, params=P, table=table)
    mistakes = [(why, render(a, b, surface, places))
                for why, (a, b) in pick(pool, order, wrongs) if b]
    return mcq("prob.two_way.marginal", "two-way table", tier, seed, stem, key,
               mistakes, rng, rationale, params=P, table=table)


_GRID_NOTE = " (Express your answer as a decimal or fraction, not as a percent.)"


def _order(pool, prefer):
    return [k for k in prefer if k in pool] + [k for k in pool if k not in prefer]


def _ask(c, sel, frame: str) -> str:
    if frame == "noun":
        return f"what is the probability of selecting {sel.n}?"
    return f"what is the probability that {c.subject} {sel.p}?"


# --------------------------------------------------------------- prob.two_way.joint

def joint(rng: random.Random, seed: int, *, scenario=None, cells=None, ri=None,
          cj=None, surface=None, places=None, margins=True, fmt="mcq",
          wrongs=None, tier="medium"):
    """P(this row and this column) -- one cell, over every unit in the table."""
    c, T = setup(rng, scenario, cells)
    ri = rng.randrange(T.nr) if ri is None else ri
    cj = rng.randrange(T.nc) if cj is None else cj
    row, col = c.rows[ri], c.cols[cj]
    ev = Event(rows=row.idx, cols=col.idx)
    surface = surface or rng.choice(SURFACES)
    places = PLACES.get(surface, 0) if places is None else places
    num, N = T.count(ev), T.total
    if not 0 < num < N:
        raise ItemError("a probability of 0 or 1 is not what this question asks")
    guard_surface(num, N, surface, places, False)

    rt, ct = T.row_total(ri), T.col_total(cj)
    pool = {
        "over_row": (f"divided by the number of {row.g} instead of by all {N:,} "
                     f"{c.units}", (num, rt)),
        "over_col": (f"divided by the number of {col.g} instead of by all {N:,} "
                     f"{c.units}", (num, ct)),
        "row": (f"used the number of {row.g}, ignoring the second condition", (rt, N)),
        "col": (f"used the number of {col.g}, ignoring the first condition", (ct, N)),
        "union": (f"found the probability of {row.n} or {col.n} rather than both",
                  (rt + ct - num, N)),
        "sum": (f"added the two totals without subtracting the {c.units} counted "
                f"twice", (rt + ct, N)),
        "not": (f"found the probability of the complement", (N - num, N)),
    }
    for i in range(T.nr):
        for j in range(T.nc):
            if (i, j) == (ri, cj):
                continue
            v = T.cells[i][j]
            pool[f"cell{i}{j}"] = (f"read the cell for {c.rows[i].label} and "
                                   f"{c.cols[j].label} instead", (v, N))
            pool[f"cell{i}{j}_over_row"] = (
                f"read the cell for {c.rows[i].label} and {c.cols[j].label} and "
                f"divided it by its own row total", (v, T.row_total(i)))
            pool[f"cell{i}{j}_over_col"] = (
                f"read the cell for {c.rows[i].label} and {c.cols[j].label} and "
                f"divided it by its own column total", (v, T.col_total(j)))

    order = wrongs or _order(pool, ["over_row", "over_col", "row", "col", "union"])
    ask = (f"what is the probability that {c.subject} {row.p} {c.join} {col.p}?")
    stem = f"{intro_of(c, T)} {sentence(c.select.format(n=f'{T.total:,}'), ask)}"
    key = render(num, N, surface, places)
    P = params_of("prob_two_way", c, T, ev, Event(), surface, places)
    rationale = (f"The table shows {num:,} {c.units} that {row.plural()} and "
                 f"{col.plural()}, out of {N:,} in all, so the probability is "
                 f"{key.plain()}.")
    table = T.printed(c, margins=margins)
    if fmt == "spr":
        if not griddable(Q(num, N)):
            raise ItemError("this probability is not enterable in five characters")
        return spr("prob.two_way.joint", "two-way table", tier, seed,
                   stem + _GRID_NOTE, Q(num, N), rationale, params=P, table=table)
    mistakes = [(why, render(a, b, surface, places))
                for why, (a, b) in pick(pool, order, wrongs) if b]
    return mcq("prob.two_way.joint", "two-way table", tier, seed, stem, key,
               mistakes, rng, rationale, params=P, table=table)


# --------------------------------------------- prob.two_way.conditional / .grouped

FRAMES = ("given", "if_cond", "select_cond", "fraction_of", "of_the")


def _conditional(name, rng, seed, *, scenario, cells, ev_axis, ev_idx, cd_idx,
                 surface, places, frame, margins, fmt, wrongs, tier, approx,
                 unions):
    c, T = setup(rng, scenario, cells)
    ev_axis = ev_axis or rng.choice(("row", "col"))
    cd_axis = "col" if ev_axis == "row" else "row"
    ev_pool = (c.row_sels() if ev_axis == "row" else c.col_sels())
    cd_pool = (c.col_sels() if ev_axis == "row" else c.row_sels())
    n_ev = len(c.rows) if ev_axis == "row" else len(c.cols)
    n_cd = len(c.cols) if ev_axis == "row" else len(c.rows)

    def choose(pool, plain_n, want_union, given):
        if given is not None:
            return pool[given]
        span = range(plain_n, len(pool)) if want_union else range(plain_n)
        opts = [i for i in span]
        if not opts:
            raise ItemError("this scenario has no union along that axis")
        return pool[rng.choice(opts)]

    if unions:
        # at least one side is a union of categories the stem names in words
        which = rng.choice(("ev", "cd", "both")) if (ev_idx is None and cd_idx is None) \
            else "cd"
        ev = choose(ev_pool, n_ev, which in ("ev", "both"), ev_idx)
        cd = choose(cd_pool, n_cd, which in ("cd", "both"), cd_idx)
        if len(ev.idx) < 2 and len(cd.idx) < 2:
            raise ItemError("this draw named no union, so it belongs to the plain "
                            "conditional template")
    else:
        ev = choose(ev_pool, n_ev, False, ev_idx)
        cd = choose(cd_pool, n_cd, False, cd_idx)

    E = Event(rows=ev.idx) if ev_axis == "row" else Event(cols=ev.idx)
    G = Event(cols=cd.idx) if ev_axis == "row" else Event(rows=cd.idx)
    num, den = T.count(meet(E, G)), T.count(G)
    N = T.total
    if den == 0 or not 0 < num < den:
        raise ItemError("a conditional probability of 0 or 1 is not what this asks")
    surface = surface or rng.choice(SURFACES)
    places = PLACES.get(surface, 0) if places is None else places
    if approx and surface != "decimal":
        raise ItemError("only a decimal answer is offered as the closest of four")
    guard_surface(num, den, surface, places, approx)

    n_ev_all = T.count(E)
    pool = {
        "joint": (f"divided by all {N:,} {c.units} instead of by the {den:,} {cd.g}",
                  (num, N)),
        "reverse": (f"divided by the number of {ev.g} instead of by the number of "
                    f"{cd.g} — the conditional the other way round", (num, n_ev_all)),
        "event_over_grand": (f"used the number of {ev.g} over all {N:,} {c.units}, "
                             f"ignoring the condition", (n_ev_all, N)),
        "cond_over_grand": (f"found the probability of the condition itself, that "
                            f"{c.subject} {cd.p}", (den, N)),
        "complement_in": (f"found the fraction of the {cd.g} that are not {ev.g}",
                          (den - num, den)),
        "cond_over_event": (f"divided the number of {cd.g} by the number of {ev.g}",
                            (den, n_ev_all)),
        "count_as_percent": (f"reported the count {num:,} itself as the percent",
                             (num, 100)),
    }
    for i, other in enumerate(c.rows if ev_axis == "row" else c.cols):
        if other.idx == ev.idx:
            continue
        o = Event(rows=other.idx) if ev_axis == "row" else Event(cols=other.idx)
        pool[f"other{i}"] = (f"read the row for {other.label} rather than for "
                             f"{_label(ev, c, ev_axis)}" if ev_axis == "row" else
                             f"read the column for {other.label} rather than for "
                             f"{_label(ev, c, ev_axis)}", (T.count(meet(o, G)), den))
        pool[f"over_other{i}"] = (f"divided by the count for {other.label} instead of "
                                  f"by the total for the {cd.g}",
                                  (num, T.count(meet(o, G))))
        pool[f"diff{i}"] = (f"subtracted the two counts in the given group instead of "
                            f"using one of them",
                            (abs(num - T.count(meet(o, G))), den))
    for i, other in enumerate(c.cols if ev_axis == "row" else c.rows):
        if other.idx == cd.idx:
            continue
        o = Event(cols=other.idx) if ev_axis == "row" else Event(rows=other.idx)
        pool[f"in{i}"] = (f"answered the question for the {other.label} group instead",
                          (T.count(meet(E, o)), T.count(o)))
    for j in cd.idx:                    # only a union has more than one
        if len(cd.idx) < 2:
            break
        one = Event(cols=(j,)) if ev_axis == "row" else Event(rows=(j,))
        lab = (c.cols if ev_axis == "row" else c.rows)[j].label
        pool[f"single{j}"] = (f"used only the {lab} part of the group the condition "
                              f"covers", (T.count(meet(E, one)), T.count(one)))

    order = wrongs or _order(pool, ["joint", "reverse", "event_over_grand",
                                    "complement_in", "cond_over_grand"])
    frame = frame or rng.choice(FRAMES)
    stem = f"{intro_of(c, T)} {_ask_cond(c, T, ev, cd, frame, approx, surface, places)}"
    key = render(num, den, surface, places)
    P = params_of("prob_two_way", c, T, E, G, surface, places, approx)
    tail = (f"and {num:,}/{den:,} is closest to {key.plain()}." if approx else
            f"so the {'percent' if surface == 'percent' else 'probability'} is "
            f"{key.plain()}.")
    rationale = f"There are {den:,} {cd.g}, and {num:,} of them {ev.plural()}, {tail}"
    table = T.printed(c, margins=margins)
    if fmt == "spr":
        if not griddable(Q(num, den)):
            raise ItemError("this probability is not enterable in five characters")
        return spr(name, "two-way table", tier, seed, stem + _GRID_NOTE,
                   Q(num, den), rationale, params=P, table=table)
    mistakes = [(why, render(a, b, surface, places))
                for why, (a, b) in pick(pool, order, wrongs) if b]
    item = mcq(name, "two-way table", tier, seed, stem, key, mistakes, rng,
               rationale, params=P, table=table)
    if approx:
        _closest(Q(num, den), item)
    return item


def _label(sel, c, axis) -> str:
    return sel.label or sel.g


def _closest(exact: Q, item) -> None:
    """A "closest to" page must have one option nearer the exact value than
    every other. Rounding the key correctly is not the same thing: the student
    compares against the four numbers that are printed."""
    vals = [Q(ch.replace(",", "")) if "/" not in ch else Q(ch)
            for ch in item.choices]
    keyed = vals["ABCD".index(item.answer)]
    d = abs(keyed - exact)
    if any(abs(v - exact) <= d for i, v in enumerate(vals)
           if i != "ABCD".index(item.answer)):
        raise ItemError("two of the printed options are equally close to the exact "
                        "value, so the page has no single closest answer")


def _ask_cond(c, T, ev, cd, frame, approx, surface, places) -> str:
    the = f"the {c.unit}"
    prob = ("which of the following is closest to the probability" if approx
            else "what is the probability")
    if surface == "percent":
        place = {0: "whole percent", 1: "tenth of a percent",
                 2: "hundredth of a percent"}[places]
        return (f"To the nearest {place}, what percent of {cd.g} {ev.plural()}?")
    if frame == "given":
        return sentence(c.select.format(n=f"{T.total:,}"),
                        f"{prob} of selecting {ev.n}, given that {the} {cd.p}?")
    if frame == "if_cond":
        return f"If {c.subject} {cd.p}, {prob} that {the} {ev.p}?"
    if frame == "select_cond":
        return f"If one of the {cd.g} is selected at random, {prob} that {the} {ev.p}?"
    if frame == "fraction_of":
        return f"What fraction of the {cd.g} {ev.plural()}?"
    if frame == "of_the":
        return f"Of the {cd.g}, what fraction {ev.plural()}?"
    raise ItemError(f"no question frame named {frame!r}")


def conditional(rng, seed, *, scenario=None, cells=None, ev_axis=None, ev_idx=None,
                cd_idx=None, surface=None, places=None, frame=None, margins=True,
                fmt="mcq", wrongs=None, tier="medium", approx=False):
    """P(A|B) where A and B are each one printed category."""
    return _conditional("prob.two_way.conditional", rng, seed, scenario=scenario,
                        cells=cells, ev_axis=ev_axis, ev_idx=ev_idx, cd_idx=cd_idx,
                        surface=surface, places=places, frame=frame, margins=margins,
                        fmt=fmt, wrongs=wrongs, tier=tier, approx=approx, unions=False)


def grouped(rng, seed, *, scenario=None, cells=None, ev_axis=None, ev_idx=None,
            cd_idx=None, surface=None, places=None, frame=None, margins=True,
            fmt="mcq", wrongs=None, tier="hard", approx=False):
    """P(A|B) where at least one of A and B merges several printed categories."""
    return _conditional("prob.two_way.grouped", rng, seed, scenario=scenario,
                        cells=cells, ev_axis=ev_axis, ev_idx=ev_idx, cd_idx=cd_idx,
                        surface=surface, places=places, frame=frame, margins=margins,
                        fmt=fmt, wrongs=wrongs, tier=tier, approx=approx, unions=True)
