"""Writing the line down: from two points, from a table, from slope and
intercept, and the two intercepts themselves.

The options here are equations and points rather than numbers, so the item is
assembled with `assemble_text`. Each option carries a signature -- the slope
and intercept it encodes -- in `params`, which is what the independent solver
in `audit.py` checks: it recomputes the slope and intercept from the raw data
and asks which option they belong to. The rendering is checked as a side
effect; the mathematics is checked head on.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....figures import coordinate_grid
from ....item import Item, ItemError, Mis, assemble, assemble_text
from ...linear_functions.common import (MINUS, choose, coef_text, ex, lin_text,
                                        numtext, q)

__all__ = ["from_points", "from_table", "define_line", "table_facts",
           "x_intercept", "y_intercept", "sig", "pair"]

NAMES = ["f", "g", "h", "j"]


def _count(n: int) -> str:
    return {2: "two", 3: "three", 4: "four", 5: "five"}.get(n, str(n))


def sig(m, b) -> list:
    m, b = q(m), q(b)
    return [m.numerator, m.denominator, b.numerator, b.denominator]


def pair(text: str, m, b) -> tuple:
    return (text, sig(m, b))


def _text_item(template, skill, difficulty, seed, stem, key_text, key_sig, wrong, rng, P,
               rationale, figure=None, table=None):
    """Four written options, one of them right, with the signatures recorded."""
    picked, seen, sigs = [], {key_text}, {tuple(key_sig)}
    for m in wrong:
        if m.value is None:
            continue
        text, s = m.value
        if text in seen or tuple(s) in sigs:
            continue
        seen.add(text)
        sigs.add(tuple(s))
        picked.append(m)
        if len(picked) == 3:
            break
    if len(picked) < 3:
        raise ItemError("could not build three distinct written distractors")
    choices, reasons, letter = assemble_text(
        key_text, [Mis(m.reason, m.value[0]) for m in picked], rng)
    by_text = {m.value[0]: m.value[1] for m in picked}
    by_text[key_text] = key_sig
    P["texts"] = list(choices)
    P["sigs"] = [by_text[c] for c in choices]
    return Item(template, skill, difficulty, seed, stem, "mcq", E(0), letter, rationale,
                choices, reasons, list(choices), figure=figure, table=table, params=P)


# ---------------------------------------------------------------- two points

POINT_STEMS = [
    "In the xy-plane, the graph of the linear function {n} contains the points {p1} and "
    "{p2}. Which equation defines {n}, where y = {n}(x)?",
    "In the xy-plane, the points {p1} and {p2} lie on the graph of which of the following "
    "linear functions?",
    "The graph of the linear function {n} in the xy-plane passes through the points {p1} "
    "and {p2}. Which equation defines {n}?",
]


def from_points(rng: random.Random, seed: int, *, x1=None, y1=None, x2=None, y2=None,
                name=None, frame=None) -> Item:
    name = name or rng.choice(NAMES)
    frame = rng.randrange(len(POINT_STEMS)) if frame is None else frame
    x1 = q(x1 if x1 is not None else rng.choice([0, 0, 0, rng.randint(-6, 6)]))
    y1 = q(y1 if y1 is not None else rng.randint(-9, 12))
    x2 = q(x2 if x2 is not None else rng.randint(2, 12))
    if x2 == x1:
        raise ItemError("two points on a vertical line define no function")
    y2 = q(y2) if y2 is not None else y1 + q(rng.choice(
        [rng.randint(2, 8), rng.randint(-8, -2)])) * (x2 - x1)
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    if m == 0:
        raise ItemError("a horizontal line makes the slope invisible")
    key = f"{name}(x) = {lin_text(m, b)}"
    rise, run = y2 - y1, x2 - x1

    if x1 == 0:
        wrong = [Mis("used the rise as the slope and the sum of the outputs as the "
                     "y-intercept", pair(f"{name}(x) = {lin_text(rise, y1 + y2)}",
                                         rise, y1 + y2)),
                 Mis("used the first output as the slope and the sum of the second "
                     "point's coordinates as the y-intercept",
                     pair(f"{name}(x) = {lin_text(y1, y2 + x2)}", y1, y2 + x2)),
                 Mis("used the run as the slope",
                     pair(f"{name}(x) = {lin_text(run, b)}", run, b)),
                 Mis("changed the sign of the slope",
                     pair(f"{name}(x) = {lin_text(-m, b)}", -m, b))]
    else:
        inv = (x2 - x1) / (y2 - y1)
        wrong = [Mis("subtracted the coordinates in opposite orders, flipping the slope",
                     pair(f"{name}(x) = {lin_text(-m, b)}", -m, b)),
                 Mis("inverted the slope, dividing the run by the rise",
                     pair(f"{name}(x) = {lin_text(inv, b)}", inv, b)),
                 Mis("used the first point's y-value as the y-intercept",
                     pair(f"{name}(x) = {lin_text(m, y1)}", m, y1)),
                 Mis("used the rise as the slope",
                     pair(f"{name}(x) = {lin_text(rise, b)}", rise, b))]
    stem = POINT_STEMS[frame].format(n=name, p1=f"({numtext(x1)}, {numtext(y1)})",
                                     p2=f"({numtext(x2)}, {numtext(y2)})")
    P = {"kind": "lf_from_points", "x1": [x1.numerator, x1.denominator],
         "y1": [y1.numerator, y1.denominator], "x2": [x2.numerator, x2.denominator],
         "y2": [y2.numerator, y2.denominator]}
    rationale = (f"The slope is ({numtext(y2)} {MINUS} {numtext(y1)})"
                 f"/({numtext(x2)} {MINUS} "
                 f"{numtext(x1)}) = {numtext(m)}, and the y-intercept is {numtext(b)}.")
    return _text_item("lin.from_points", "a line through two points", "medium", seed,
                      stem, key, sig(m, b), wrong, rng, P, rationale)


# --------------------------------------------------------------- from a table

TABLE_STEMS = [
    "Some values of the linear function {n} are shown in the table above. Which of the "
    "following defines {n} ?",
    "For the linear function {n}, the table shows {c} values of {v} and their "
    "corresponding values of {n}({v}). Which equation defines {n}({v})?",
    "The table shows {c} values of {v} and their corresponding values of {n}({v}) for the "
    "linear function {n}. Which equation defines {n}?",
    "The table gives {c} values of {v} and their corresponding values of {n}({v}) for the "
    "linear function {n}. Which equation could define {n}?",
    "For the linear function {n}, the table above shows {c} values of {v} and their "
    "corresponding values of {n}({v}). Which of the following defines {n}?",
]


def from_table(rng: random.Random, seed: int, *, m=None, b=None, xs=None, x0=None,
               step=None, rows=None, name=None, frame=None, mode=None, cell="frac",
               coef="frac", labels=None, var=None, dep=None, context=None,
               wrong_style=None) -> Item:
    """A table of values, and the rule that produced it."""
    mode = mode or rng.choice(["affine", "affine", "proportional"])
    name = name or rng.choice(NAMES)
    var = var or rng.choice(["x", "x", "t", "n"])
    rows = rows or rng.choice([3, 3, 4, 5])
    frame = rng.randrange(len(TABLE_STEMS)) if frame is None else frame
    if xs is None:
        x0 = q(x0 if x0 is not None else rng.choice([0, 1, rng.randint(-4, 6)]))
        step = q(step if step is not None else rng.randint(1, 3))
        xs = [x0 + step * i for i in range(rows)]
    else:
        xs = [q(v) for v in xs]
        step = xs[1] - xs[0]
    rows = len(xs)
    if mode == "proportional":
        m = q(m if m is not None else rng.choice([rng.randint(2, 40), Q(9, 5), Q(3, 2)]))
        b = Q(0)
        if any(v <= 0 for v in xs):
            raise ItemError("a proportional context needs positive inputs")
    else:
        m = q(m if m is not None else rng.choice(
            [rng.randint(2, 9), rng.randint(-9, -2)]))
        b = q(b if b is not None else rng.randint(-40, 60))
    ys = [m * x + b for x in xs]
    head = labels or [var, f"{name}({var})"]
    table = [list(head)] + [[numtext(x, cell), numtext(y, cell)] for x, y in zip(xs, ys)]
    lhs = dep or f"{name}({var})"
    dy = ys[1] - ys[0]

    if mode == "proportional":
        key = f"{lhs} = {coef_text(m, var, coef)}"
        wrong_style = wrong_style or "outputs"
        if wrong_style == "inverted":
            cands = [("inverted the constant of proportionality", 1 / m),
                     ("divided the change in the outputs by an input instead of by the "
                      "change in the inputs", dy / xs[1]),
                     ("used the first output as the constant of proportionality", ys[0]),
                     ("used the change in the outputs as the constant of proportionality",
                      dy)]
        else:
            cands = [("used the first output as the constant of proportionality", ys[0]),
                     ("used the change in the outputs as the constant of proportionality",
                      dy),
                     ("divided the change in the outputs by an input instead of by the "
                      "change in the inputs", dy / xs[1]),
                     ("inverted the constant of proportionality", 1 / m)]
        wrong = [Mis(r, pair(f"{lhs} = {coef_text(v, var, coef)}", v, 0))
                 for r, v in cands if v != 0]
    else:
        key = f"{lhs} = {lin_text(m, b, var, coef)}"
        wrong_style = wrong_style or "outputs"
        outputs = [Mis("read two of the table's outputs as the slope and the y-intercept",
                       pair(f"{lhs} = {lin_text(u, v, var, coef)}", u, v))
                   for u, v in [(ys[0], ys[1]), (ys[-1], ys[0]), (ys[1], ys[-1])]]
        fitted = [Mis("fitted the first row only, using the step in x as the slope",
                      pair(f"{lhs} = {lin_text(s0, ys[0] - s0 * xs[0], var, coef)}",
                           s0, ys[0] - s0 * xs[0]))
                  for s0 in (step, step + 1) if s0 != m and s0 != 0]
        bare = [Mis("used the first output as the slope with no constant term",
                    pair(f"{lhs} = {coef_text(ys[0], var, coef)}", ys[0], 0))]
        wrong = (fitted + bare + outputs) if wrong_style == "fit_first" \
            else (outputs + fitted + bare)
    stem = context or TABLE_STEMS[frame].format(n=name, v=var, c=_count(rows))
    P = {"kind": "lf_from_table", "mode": mode,
         "xs": [[v.numerator, v.denominator] for v in xs],
         "ys": [[v.numerator, v.denominator] for v in ys]}
    rationale = (f"The outputs change by {numtext(dy, cell)} for every "
                 f"{numtext(step, cell)} in {var}, so the slope is {numtext(m, coef)}"
                 + (f" and the constant term is {numtext(b, coef)}."
                    if mode == "affine" else "."))
    return _text_item("lin.from_table", "a line from a table", "easy", seed, stem, key,
                      sig(m, b), wrong, rng, P, rationale, table=table)


# ------------------------------------------------- from slope and y-intercept

def define_line(rng: random.Random, seed: int, *, m=None, b=None, given=None, phrase=None,
                name=None) -> Item:
    """Slope and intercept, or f(0) and f(1), turned into an equation."""
    given = given or rng.choice(["slope_intercept", "two_values"])
    name = name or rng.choice(NAMES)
    if m is None:
        m = q(rng.choice([rng.randint(2, 9), rng.randint(-9, -2), 1, -1, 0,
                          Q(1, rng.randint(2, 6)),
                          Q(rng.randint(2, 5), rng.randint(3, 8))]))
    else:
        m = q(m)
    b = q(b if b is not None else rng.randint(-40, 45))
    if b == 0:
        raise ItemError("a zero intercept hides the distinction being tested")
    key = f"{name}(x) = {lin_text(m, b)}"

    if given == "two_values":
        y1 = b + m
        phrase = phrase or rng.choice(["for_the", "in_the"])
        lead = (f"For the linear function {name}, " if phrase == "for_the"
                else f"In the linear function {name}, ")
        stem = (f"{lead}{name}(0) = {numtext(b)} and {name}(1) = {numtext(y1)}. Which "
                f"equation defines {name}?")
        if m == 0:
            wrong = [Mis("took the reciprocal of the constant output",
                         pair(f"{name}(x) = {numtext(1 / b)}", 0, 1 / b)),
                     Mis("wrote the coefficient as 1 instead of the constant output",
                         pair(f"{name}(x) = 1", 0, 1)),
                     Mis("added the two given outputs",
                         pair(f"{name}(x) = {numtext(2 * b)}", 0, 2 * b))]
        elif abs(m) == 1:
            s = 1 if m > 0 else -1
            wrong = [Mis("left out the constant term",
                         pair(f"{name}(x) = {coef_text(m, 'x')}", m, 0)),
                     Mis("used the value at 0 as the slope",
                         pair(f"{name}(x) = {coef_text(s * b, 'x')}", s * b, 0)),
                     Mis("gave the value at 0 as a constant function",
                         pair(f"{name}(x) = {numtext(s * b)}", 0, s * b))]
        else:
            wrong = [Mis("used the value at 1 as the slope",
                         pair(f"{name}(x) = {lin_text(y1, b)}", y1, b)),
                     Mis("left out the constant term",
                         pair(f"{name}(x) = {coef_text(m, 'x')}", m, 0)),
                     Mis("used the value at 1 as the y-intercept",
                         pair(f"{name}(x) = {lin_text(m, y1)}", m, y1))]
    else:
        if m == 0:
            raise ItemError("a stated slope of zero makes the item trivial")
        phrase = phrase or rng.choice(["slope_f0", "y_intercept_at", "passes_through"])
        if phrase == "slope_f0":
            stem = (f"The graph of the function {name} is a line in the xy-plane. If the "
                    f"line has slope {numtext(m)} and {name}(0) = {numtext(b)}, which of "
                    f"the following defines {name}?")
        elif phrase == "y_intercept_at":
            stem = (f"For the linear function {name}, the graph of y = {name}(x) in the "
                    f"xy-plane has a slope of {numtext(m)} and has a y-intercept at "
                    f"(0, {numtext(b)}). Which equation defines {name}?")
        else:
            stem = (f"For the linear function {name}, the graph of y = {name}(x) in the "
                    f"xy-plane has a slope of {numtext(m)} and passes through the point "
                    f"(0, {numtext(b)}). Which equation defines {name}?")
        if m.denominator == 1:
            wrong = [Mis("inverted the slope", pair(f"{name}(x) = {lin_text(1 / m, b)}",
                                                    1 / m, b)),
                     Mis("changed the sign of the slope",
                         pair(f"{name}(x) = {lin_text(-m, b)}", -m, b)),
                     Mis("inverted the slope and changed its sign",
                         pair(f"{name}(x) = {lin_text(-1 / m, b)}", -1 / m, b))]
        elif abs(m.numerator) == 1:
            wrong = [Mis("changed the sign of the y-intercept",
                         pair(f"{name}(x) = {lin_text(m, -b)}", m, -b)),
                     Mis("took the reciprocal of the y-intercept",
                         pair(f"{name}(x) = {lin_text(m, 1 / b)}", m, 1 / b)),
                     Mis("multiplied the y-intercept by the slope and subtracted it",
                         pair(f"{name}(x) = {lin_text(m, -m * b)}", m, -m * b))]
        else:
            den = q(m.denominator)
            wrong = [Mis("changed the sign of the y-intercept",
                         pair(f"{name}(x) = {lin_text(m, -b)}", m, -b)),
                     Mis("used the denominator of the slope as the slope",
                         pair(f"{name}(x) = {lin_text(den, b)}", den, b)),
                     Mis("used the denominator of the slope and changed the sign of the "
                         "y-intercept", pair(f"{name}(x) = {lin_text(den, -b)}", den, -b))]
    P = {"kind": "lf_define", "given": given, "m": [m.numerator, m.denominator],
         "b": [b.numerator, b.denominator]}
    rationale = (f"Slope-intercept form is y = mx + b with m = {numtext(m)} and "
                 f"b = {numtext(b)}.")
    return _text_item("lin.define_line", "slope-intercept form", "easy", seed, stem, key,
                      sig(m, b), wrong, rng, P, rationale)


# --------------------------------------------------------- facts from a table

def table_facts(rng: random.Random, seed: int, *, m=None, b=None, xs=None, x0=None,
                step=None, rows=3, ask=None, name=None, fmt=None, x_ask=None,
                frame=None, labels=None) -> Item:
    """The table is given; the question is a coefficient or a missing value."""
    ask = ask or rng.choice(["value", "intercept", "slope", "a_minus_b"])
    name = name or rng.choice(NAMES)
    fmt = fmt or ("spr" if rng.random() < 0.3 else "mcq")
    frame = frame or "function"
    m = q(m if m is not None else rng.choice([rng.randint(2, 12), rng.randint(-12, -2)]))
    b = q(b if b is not None else rng.randint(-130, 90))
    if xs is None:
        x0 = q(x0 if x0 is not None else rng.randint(-12, 4))
        step = q(step if step is not None else rng.choice([1, 1, 2, 3]))
        xs = [x0 + step * i for i in range(rows)]
    else:
        xs = [q(v) for v in xs]
        step = xs[1] - xs[0]
    rows = len(xs)
    ys = [m * x + b for x in xs]
    head = labels or ["x", f"{name}(x)"]
    table = [list(head)] + [[numtext(x), numtext(y)] for x, y in zip(xs, ys)]

    if ask == "value":
        if x_ask is None:
            x_ask = xs[0] + step * q(rng.randint(1, 2 * rows - 1)) / 2
        x_ask = q(x_ask)
        if x_ask in xs:
            raise ItemError("the requested input is already in the table")
        key = m * x_ask + b
        near = min(xs, key=lambda v: abs(v - x_ask))
        y_near = m * near + b
        if frame == "point":
            stem = (f"The table shows two values of x and their corresponding values of y. "
                    f"The graph of the linear equation representing this relationship "
                    f"passes through the point ({numtext(x_ask)}, a). What is the value "
                    f"of a?")
        else:
            stem = (f"Some values of the linear function {name} are shown in the table "
                    f"above. What is the value of {name}({numtext(x_ask)})?")
        mistakes = [Mis("left out the constant term", m * x_ask),
                    Mis("used the step in x as the slope and left out the constant term",
                        step * x_ask),
                    Mis("divided the change in the outputs by the requested input instead "
                        "of by the change in x",
                        y_near + (ys[-1] - y_near) / x_ask if x_ask != 0 else None),
                    Mis("gave the value from the nearest row of the table", y_near),
                    Mis("added the slope to the wrong row", ys[-1] + m),
                    # the sign slip lands on the key's own surface -- it moves the
                    # answer by 2mx and nothing else, so it carries the key's
                    # denominator, which the five mistakes above need not
                    Mis("subtracted the outputs in the wrong order, giving the slope "
                        "the wrong sign", -m * x_ask + b)]
    elif ask == "intercept":
        key = b
        stem = (f"For the linear function {name}, the table shows {_count(rows)} values of "
                f"x and their corresponding values of {name}(x). The function can be "
                f"written as {name}(x) = mx + b, where m and b are constants. What is the "
                f"value of b?")
        mistakes = [Mis("gave the size of the slope instead of the constant term", abs(m)),
                    Mis("read the first output as the y-intercept", ys[0]),
                    Mis("halved the first output", ys[0] / 2),
                    Mis("stepped the wrong way from the first row", ys[0] + m * xs[0])]
    elif ask == "slope":
        key = m
        stem = (f"For the linear function {name}, the table shows {_count(rows)} values of "
                f"x and their corresponding values of {name}(x). The function can be "
                f"written as {name}(x) = mx + b, where m and b are constants. What is the "
                f"value of m?")
        mistakes = [Mis("divided the change in x by the change in the outputs",
                        step / (ys[1] - ys[0]) if ys[1] != ys[0] else None),
                    Mis("used the change in the outputs without dividing by the step in x",
                        ys[1] - ys[0]),
                    Mis("changed the sign of the slope", -m),
                    Mis("gave the constant term instead of the slope", b),
                    # when the rows step by one, "used the change in the outputs
                    # without dividing" lands on the slope itself and drops out as a
                    # duplicate, leaving no wrong option that reads like a slope. This
                    # one always does: it is a whole multiple of m, so it carries the
                    # key's sign and its integer surface whatever the table's step
                    Mis("divided the change in the outputs across the whole table by "
                        "the step between two consecutive rows",
                        (ys[-1] - ys[0]) / step if rows > 2 else None)]
    else:
        key = m - b
        stem = (f"For the linear function {name}, the table shows {_count(rows)} values of "
                f"x and their corresponding values of {name}(x). Function {name} is "
                f"defined by {name}(x) = ax + b, where a and b are constants. What is the "
                f"value of a {MINUS} b?")
        mistakes = [Mis("added a and b instead of subtracting them", m + b),
                    Mis("gave b without its sign", abs(b)),
                    Mis("subtracted the second input instead of b", m - xs[1]),
                    Mis("gave a alone", m)]
    P = {"kind": "lf_table_facts", "ask": ask, "m": [m.numerator, m.denominator],
         "b": [b.numerator, b.denominator],
         "xs": [[v.numerator, v.denominator] for v in xs],
         "ys": [[v.numerator, v.denominator] for v in ys],
         "x_ask": ([x_ask.numerator, x_ask.denominator] if ask == "value" else None)}
    rationale = (f"The table gives slope {numtext(m)} and constant term {numtext(b)}, so "
                 f"the answer is {numtext(key)}.")
    keyx = ex(key)
    if fmt == "spr":
        return Item("lin.table_facts", "reading a linear table", "medium", seed, stem,
                    "spr", keyx, keyx.gridin(), rationale, table=table, params=P)
    mistakes = [Mis(r.reason, ex(r.value)) for r in mistakes if r.value is not None]
    choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True,
                                               fillers="shift")
    return Item("lin.table_facts", "reading a linear table", "medium", seed, stem, "mcq",
                keyx, letter, rationale, choices, reasons, latex, table=table, params=P)


# ---------------------------------------------------------------- intercepts

def x_intercept(rng: random.Random, seed: int, *, m=None, b=None, given=None, fmt=None,
                m2=None, b2=None, step=None, x0=None, rows=4, name=None) -> Item:
    """Where the line crosses the x-axis, from a rule, a sum or a table."""
    given = given or rng.choice(["slope_intercept", "sum", "table"])
    name = name or rng.choice(NAMES)
    fmt = fmt or ("mcq" if given == "table" else "spr")
    table = None
    if given == "sum":
        m = q(m if m is not None else Q(1, rng.randint(2, 5)))
        b = q(b if b is not None else rng.randint(-30, -2))
        m2 = q(m2 if m2 is not None else 1 - m)
        b2 = q(b2 if b2 is not None else rng.randint(4, 40))
        M, B = m + m2, b + b2
        parts = [m, b, m2, b2]
        stem = (f"The functions f and g are defined as f(x) = {lin_text(m, b)} and "
                f"g(x) = {lin_text(m2, b2)}. If the function h is defined as "
                f"h(x) = f(x) + g(x), what is the x-coordinate of the x-intercept of the "
                f"graph of y = h(x) in the xy-plane?")
        if M == 0:
            raise ItemError("the sum must still be a line with a slope")
        rationale = (f"h(x) = {lin_text(M, B)}, which is zero at x = {numtext(-B / M)}.")
    elif given == "table":
        m = q(m if m is not None else rng.choice([rng.randint(2, 6), rng.randint(-6, -2)]))
        b = q(b if b is not None else rng.randint(-40, 40))
        x0 = q(x0 if x0 is not None else rng.randint(-12, 6))
        step = q(step if step is not None else 1)
        xs = [x0 + step * i for i in range(rows)]
        ys = [m * x + b for x in xs]
        if any(y == 0 for y in ys):
            raise ItemError("the table must not give the intercept away")
        table = [["x"] + [numtext(v) for v in xs],
                 [f"{name}(x)"] + [numtext(v) for v in ys]]
        M, B = m, b
        parts = None
        stem = (f"The table above shows some values of x and their corresponding values "
                f"{name}(x) for the linear function {name}. What is the x-intercept of the "
                f"graph of y = {name}(x) in the xy-plane?")
        rationale = (f"The table gives {name}(x) = {lin_text(m, b)}, which is zero at "
                     f"x = {numtext(-b / m)}.")
    else:
        m = q(m if m is not None else rng.choice([rng.randint(2, 12),
                                                  rng.randint(-12, -2)]))
        b = q(b if b is not None else rng.randint(-90, 90))
        M, B = m, b
        parts = None
        stem = (f"In the xy-plane, line k has a slope of {numtext(m)} and a y-intercept of "
                f"(0, {numtext(b)}). What is the x-coordinate of the x-intercept of "
                f"line k?")
        rationale = (f"0 = {lin_text(m, b)} gives x = {numtext(-b / m)}.")
    if M == 0 or B == 0:
        raise ItemError("the line must cross both axes away from the origin")
    key = -B / M
    P = {"kind": "lf_x_intercept", "given": given, "m": [M.numerator, M.denominator],
         "b": [B.numerator, B.denominator]}
    if parts is not None:
        P["parts"] = [[v.numerator, v.denominator] for v in parts]
    if given == "table":
        P["xs"] = [[v.numerator, v.denominator] for v in xs]
        P["ys"] = [[v.numerator, v.denominator] for v in ys]
    keyx = ex(key)
    if fmt == "spr":
        return Item("lin.x_intercept", "the x-intercept of a line", "hard", seed, stem,
                    "spr", keyx, keyx.gridin(), rationale, table=table, params=P)

    if key.denominator != 1 or (B / M).denominator != 1:
        raise ItemError("every option must be a lattice point on the x-axis")
    P["as_point"] = True

    def pt(v):
        v = q(v)
        return (f"({numtext(v)}, 0)", [v.numerator, v.denominator, 0, 1])
    wrong = [Mis("gave the y-intercept as the x-intercept", pt(B)),
             Mis("gave the slope as the x-intercept", pt(M)),
             Mis("divided without changing the sign", pt(B / M)),
             Mis("stepped one row too far along the table", pt(key - M))]
    return _text_item("lin.x_intercept", "the x-intercept of a line", "hard", seed, stem,
                      f"({numtext(key)}, 0)", [key.numerator, key.denominator, 0, 1],
                      wrong, rng, P, rationale, table=table)


def y_intercept(rng: random.Random, seed: int, *, m=None, b=None, given=None, fmt=None,
                name=None) -> Item:
    """The y-intercept, from the rule (a number) or from a drawn line (a point)."""
    given = given or rng.choice(["equation", "graph"])
    name = name or rng.choice(NAMES)
    b = q(b if b is not None else rng.randint(-12, 12))
    if b == 0:
        raise ItemError("a line through the origin makes the two intercepts the same")
    if given == "equation":
        m = q(m if m is not None else rng.choice([rng.randint(2, 12),
                                                  rng.randint(-12, -2)]))
        stem = (f"The function {name} is defined by {name}(x) = {lin_text(m, b)}. What is "
                f"the y-coordinate of the y-intercept of the graph of y = {name}(x) in the "
                f"xy-plane?")
        keyx = ex(b)
        P = {"kind": "lf_y_intercept", "given": given, "m": [m.numerator, m.denominator],
             "b": [b.numerator, b.denominator]}
        rationale = f"At x = 0 the value is {numtext(b)}."
        if (fmt or "spr") == "spr":
            return Item("lin.y_intercept", "the y-intercept of a line", "easy", seed, stem,
                        "spr", keyx, keyx.gridin(), rationale, params=P)
        mistakes = [Mis("gave the slope instead of the y-intercept", ex(m)),
                    Mis("changed the sign of the y-intercept", ex(-b)),
                    Mis("gave the x-intercept instead", ex(-b / m))]
        choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True,
                                                   fillers="shift")
        return Item("lin.y_intercept", "the y-intercept of a line", "easy", seed, stem,
                    "mcq", keyx, letter, rationale, choices, reasons, latex, params=P)

    if m is None:
        m = Q(rng.randint(1, 5), rng.choice([1, 2, 3, 4, 5]))
    m = q(m)
    if m == 0:
        raise ItemError("a horizontal line has no x-intercept to confuse it with")
    den = m.denominator
    xi = -b / m
    if xi.denominator != 1 or xi == 0:
        raise ItemError("the drawn line must cross the axes at lattice points")
    lo, hi = int(xi) - den * 2, int(xi) + den * 2
    seg = ((lo, int(m * lo + b)), (hi, int(m * hi + b)))
    ys = [seg[0][1], seg[1][1]]
    fig = coordinate_grid(min(lo, 0) - 1, max(hi, 0) + 1, min(min(ys), 0) - 1,
                          max(max(ys), 0) + 1, segments=[seg])
    stem = (f"The graph of the linear function {name} is shown. What is the y-intercept of "
            f"the graph of y = {name}(x)?")
    P = {"kind": "lf_y_intercept", "given": given, "m": [m.numerator, m.denominator],
         "b": [b.numerator, b.denominator],
         "seg": [list(seg[0]), list(seg[1])]}
    rationale = f"The line meets the y-axis at (0, {numtext(b)})."
    xin = int(xi)

    def pt(x, y):
        x, y = q(x), q(y)
        return (f"({numtext(x)}, {numtext(y)})",
                [x.numerator, x.denominator, y.numerator, y.denominator])
    wrong = [Mis("gave the x-intercept instead of the y-intercept", pt(xin, 0)),
             Mis("wrote the y-intercept's value as an x-coordinate", pt(b, 0)),
             Mis("read the x-intercept's value into the y-coordinate", pt(0, xin)),
             Mis("changed the sign of the y-intercept", pt(0, -b))]
    return _text_item("lin.y_intercept", "the y-intercept of a line", "easy", seed, stem,
                      f"(0, {numtext(b)})", [0, 1, b.numerator, b.denominator],
                      wrong, rng, P, rationale, figure=fig)
