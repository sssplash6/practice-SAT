"""Items whose curve is drawn rather than written.

Every picture comes from the same numbers as the stem, and every option has to
be separable *on the picture*: an option nearer the key than the gridlines can
resolve is not a wrong answer, it is the same reading printed twice. The
gridline spacing is therefore a parameter of the draw, not an afterthought,
and a misconception that lands inside it is dropped before the options are
assembled.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import ItemError, Mis
from ..common import (MINUS, num, pair, pick, point, q, sig, text_item, value_item,
                      year)
from ..figures import context_curve, plane_curve

__all__ = ["graph_intercept", "graph_context", "graph_zeros", "graph_equation"]

INTERCEPT_MCQ = "What is the y-intercept of the graph shown?"
INTERCEPT_SPR = [
    "The graph of the {what} function {n} is shown, where y = {n}(x). The "
    "y-intercept of the graph is (0, y). What is the value of y?",
    "The graph of y = {n}(x) is shown in the xy-plane. The value of {n}(0) is an "
    "integer. What is the value of {n}(0)?",
]


def _window(values, lo_pad=2, hi_pad=2):
    lo, hi = min(values), max(values)
    return int(lo) - lo_pad, int(hi) + hi_pad


def graph_intercept(rng: random.Random, seed: int, *, shape=None, c=None, d=None,
                    base=None, a=None, name=None, fmt=None, frame=None,
                    wrongs=None) -> object:
    """A curve is drawn; read its y-intercept off the picture."""
    shape = shape or rng.choice(["exp_asymptote", "exp_decay", "exp_growth",
                                 "flat_poly", "rational"])
    name = name or rng.choice(["f", "g", "h"])
    fmt = fmt or rng.choice(["mcq", "spr"])

    if shape == "exp_asymptote":
        c = int(c if c is not None else rng.choice([-6, -5, -4, -3, 3, 4, 5]))
        d = int(d if d is not None else rng.randint(1, 3))
        base = int(base if base is not None else rng.choice([2, 3, 4]))
        y0 = c - d
        xmin, xmax = -4, 5
        ymin, ymax = min(y0 - 7, c - 7), max(c + 2, 2)

        def fnc(x, c=c, d=d, base=base):
            return c - d * base ** (-x)

        branches = [fnc]
        what, asym = "exponential", c

    elif shape == "exp_decay":
        a = int(a if a is not None else rng.randint(2, 12))
        base = int(base if base is not None else rng.choice([2, 3, 4]))
        y0 = a
        if a * base > 16:
            raise ItemError("the drawn height axis would need too many gridlines")
        xmin, xmax = -1, 1
        ymin, ymax = -1, a * base + 1

        def fnc(x, a=a, base=base):
            return a * base ** (-x)

        branches = [fnc]
        what, asym = "exponential", 0

    elif shape == "exp_growth":
        a = int(a if a is not None else rng.randint(2, 9))
        base = int(base if base is not None else rng.choice([2, 3]))
        y0 = a
        if a * base ** 2 > 16:
            raise ItemError("the drawn height axis would need too many gridlines")
        xmin, xmax = -5, 5
        ymin, ymax = -1, a * base ** 2 + 1

        def fnc(x, a=a, base=base):
            return a * base ** x

        branches = [fnc]
        what, asym = "exponential", 0

    elif shape == "flat_poly":
        c = int(c if c is not None else rng.randint(-8, 8))
        d = int(d if d is not None else rng.choice([8, 9, 10, 12]))
        y0 = c
        xmin, xmax = -1, 1
        ymin, ymax = c - d - 1, c + 2

        def fnc(x, c=c, d=d):
            return c - d * x ** 4

        branches = [fnc]
        what, asym = "polynomial", None

    else:                                                          # rational
        a = int(a if a is not None else rng.randint(2, 6))
        d = int(d if d is not None else rng.randint(1, 3))
        if a % d:
            raise ItemError("the value at zero must be an integer")
        y0 = a // d
        xmin, xmax = -8, 8
        ymin, ymax = -8, 8

        def left(x, a=a, d=d):
            return a / (x + d) if x + d < 0 else None

        def right(x, a=a, d=d):
            return a / (x + d) if x + d > 0 else None

        branches = [left, right]
        what, asym = "rational", 0

    tall, wide = ymax - ymin, xmax - xmin
    fig = plane_curve(branches, xmin, xmax, ymin, ymax, dots=[(0, y0)],
                      xlabel_every=1 if wide <= 12 else 2,
                      ylabel_every=1 if tall <= 13 else 2)
    why = (f"The curve crosses the y-axis at (0, {num(y0)}), so the y-intercept is "
           f"(0, {num(y0)}).")
    P = {"kind": "nlf_graph_intercept", "shape": shape,
         "c": None if c is None else int(c), "d": None if d is None else int(d),
         "a": None if a is None else int(a),
         "base": None if base is None else int(base)}

    key = point(0, y0)
    pool = {
        "asymptote": ("read the horizontal line the curve approaches instead of the "
                      "y-intercept", None if asym is None or asym == y0
                      else pair(point(0, asym), 0, asym)),
        "origin": ("assumed the curve passes through the origin",
                   None if y0 == 0 else pair(point(0, 0), 0, 0)),
        "swapped": ("wrote the value read off the graph as the x-coordinate",
                    None if y0 == 0 else pair(point(y0, 0), y0, 0)),
        "both": ("used the value read off the graph for both coordinates",
                 None if y0 == 0 else pair(point(y0, y0), y0, y0)),
        "asym_both": ("used the height the curve approaches for both coordinates",
                      None if asym is None or asym == 0
                      else pair(point(asym, asym), asym, asym)),
        "left": ("read the curve one unit to the left of the y-axis",
                 None if shape not in ("exp_asymptote", "exp_decay")
                 else pair(point(-1, round(fnc(-1))), -1, round(fnc(-1)))),
    }

    if fmt == "spr":
        frame = rng.randrange(len(INTERCEPT_SPR)) if frame is None else frame
        stem = INTERCEPT_SPR[frame].format(what=what, n=name)
        # a grid-in types the height alone: each misread point, by its y
        typed = [Mis(m.reason, Q(*m.value[1][2:]))
                 for m in pick(pool, ["asymptote", "origin", "left"])]
        return value_item("nlfunc.graph_intercept", "a y-intercept read off a graph",
                          "easy", seed, stem, q(y0), typed, rng, P, why, fmt="spr",
                          figure=fig)

    order = ["asymptote", "origin", "swapped", "both", "asym_both", "left"]
    return text_item("nlfunc.graph_intercept", "a y-intercept read off a graph",
                     "easy", seed, INTERCEPT_MCQ, key, sig(0, y0),
                     pick(pool, order, wrongs), rng, P, why, figure=fig)


# --------------------------------------------------- a curve in a context

START = ("The graph shown models the number of {thing} of a certain {place} x years "
         "after {y0}. How many {thing} does this model estimate the {place} had in "
         "{y0}?")
PEAK = ("The quadratic function graphed above models a particular measure of {what} "
        "as a function of the {axis} in {where}. According to the model, which of "
        "the following is closest to the {axis}, in {unit}, at which {what} is "
        "greatest?")

START_CTX = [dict(thing="residents", place="city"),
             dict(thing="members", place="club"),
             dict(thing="employees", place="company")]
PEAK_CTX = [dict(what="plant diversity", axis="elevation", unit="meters",
                 where="a region of Switzerland", ylabel="Measure of plant diversity",
                 xlabel="Elevation (meters)"),
            dict(what="insect diversity", axis="elevation", unit="meters",
                 where="a region of Peru", ylabel="Measure of insect diversity",
                 xlabel="Elevation (meters)")]


def graph_context(rng: random.Random, seed: int, *, mode=None, ctx=None, a=None,
                  base=None, y0=None, span=None, peak=None, top=None, wrongs=None
                  ) -> object:
    """A modelled curve on labelled axes: its starting value, or where it peaks."""
    mode = mode or rng.choice(["start", "peak"])

    if mode == "start":
        d = START_CTX[rng.randrange(len(START_CTX))] if ctx is None else START_CTX[ctx]
        a = int(a if a is not None else rng.choice([12, 16, 20, 24, 28, 32, 36, 40]) * 1000)
        base = q(base if base is not None else Q(rng.randint(103, 107), 100))
        y0 = int(y0 if y0 is not None else rng.randrange(1980, 2015))
        span = int(span if span is not None else 10)
        if a % 4:
            raise ItemError("the starting value must sit on a gridline")
        # the starting value is four gridlines up, so a reader can count to it
        step = a // 4
        grown = a * float(base) ** span
        top = step * int(grown / step + 0.999)
        if top > 8 * step:
            raise ItemError("the curve would run off the top of the drawn window")
        key = q(a)

        def fnc(x, a=a, base=float(base)):
            return a * base ** x

        fig = context_curve(fnc, 0, span, 0, top, xlabel=f"Years after {year(y0)}",
                            ylabel=f"Number of {d['thing']}", xstep=2, ystep=step,
                            dots=[(0, a)])
        gridline = q(step)
        pool = {
            "later": ("read the value a few years along instead of at the start",
                      q(round(a * float(base) ** 4 / step) * step)),
            "scale": ("misread the vertical scale by a factor of ten", q(a) / 10),
            "origin": ("read the value where the axes meet", q(0)),
            "span": ("gave the number of years the graph covers", q(span)),
        }
        order = ["later", "scale", "origin", "span"]
        mistakes = [m for m in pick(pool, order, wrongs)
                    if abs(q(m.value) - key) >= gridline]
        stem = START.format(thing=d["thing"], place=d["place"], y0=year(y0))
        why = (f"The curve starts at {num(a)} when x = 0, which is {year(y0)}, so the "
               f"model estimates {num(a)} {d['thing']} in {year(y0)}.")
        P = {"kind": "nlf_graph_context", "mode": mode, "a": a,
             "base": [base.numerator, base.denominator], "span": span, "step": step}
        return value_item("nlfunc.graph_context", "a starting value read off a graph",
                          "easy", seed, stem, key, mistakes, rng, P, why,
                          figure=fig, signed=False)

    d = PEAK_CTX[rng.randrange(len(PEAK_CTX))] if ctx is None else PEAK_CTX[ctx]
    peak = int(peak if peak is not None else rng.randrange(5, 12) * 250)
    top = int(top if top is not None else rng.randrange(8, 16) * 1000)
    xmax = int(span if span is not None else 3000)
    xstep = 500
    if not (xstep <= peak <= xmax - xstep):
        raise ItemError("the peak must sit inside the drawn window")
    a = Q(top) / Q((xmax - peak) ** 2)                       # the curve reaches 0 at xmax
    ystep = 2000
    if top - float(a) * peak ** 2 <= 0:
        raise ItemError("the curve must still be above the axis at the left edge")

    def fnc(x, a=float(a), peak=peak, top=top):
        return top - a * (x - peak) ** 2

    fig = context_curve(fnc, 0, xmax, 0, top + 500, xlabel=d["xlabel"],
                        ylabel=d["ylabel"], xstep=xstep, ystep=ystep)
    key = q(peak)
    pool = {
        "height": ("gave the greatest value rather than the input at which it happens",
                   q(top)),
        "far_end": ("read the far end of the horizontal axis", q(xmax)),
        "first_mark": ("read the first gridline instead of the peak", q(xstep) / 2),
        "half_top": ("halved the greatest value", q(top) / 2),
    }
    order = ["height", "far_end", "first_mark", "half_top"]
    mistakes = [m for m in pick(pool, order, wrongs) if abs(q(m.value) - key) >= xstep]
    stem = PEAK.format(what=d["what"], axis=d["axis"], unit=d["unit"], where=d["where"])
    why = (f"The curve is highest at {num(peak)} {d['unit']}, so {d['what']} is "
           f"greatest at an {d['axis']} of about {num(peak)} {d['unit']}.")
    P = {"kind": "nlf_graph_context", "mode": mode, "peak": peak, "top": top,
         "xmax": xmax, "xstep": xstep}
    return value_item("nlfunc.graph_context", "where a modelled curve peaks", "easy",
                      seed, stem, key, mistakes, rng, P, why, figure=fig, signed=False)


# ------------------------------------------------------- counting zeros

ZEROS = ("The graph of y = {n}(x) is shown, where {n}(x) = ab^x + c, and a, b, and c "
         "are constants. For how many values of x does {n}(x) = 0?")
WORDS = {0: "Zero", 1: "One", 2: "Two", 3: "Three"}


def graph_zeros(rng: random.Random, seed: int, *, a=None, c=None, base=None,
                name=None, wrongs=None) -> object:
    """An exponential with a horizontal asymptote: how often does it reach zero?"""
    name = name or rng.choice(["f", "g", "h"])
    a = int(a if a is not None else rng.choice([-3, -2, -1, 1, 2, 3]))
    c = int(c if c is not None else rng.choice([-8, -7, -6, -5, 5, 6, 7, 8]))
    base = int(base if base is not None else rng.choice([2, 3, 4]))
    if a == 0 or c == 0:
        raise ItemError("both constants must be visible on the picture")
    crosses = (a > 0) != (c > 0)
    count = 1 if crosses else 0
    lo = min(c - 3, c + a * base ** 3, -2)
    hi = max(c + 3, c + a * base ** 3, 2)
    if hi - lo > 26:
        raise ItemError("the drawn window would be too tall to read")

    def fnc(x, a=a, c=c, base=base):
        return a * base ** x + c

    fig = plane_curve([fnc], -10, 10, int(lo), int(hi), xlabel_every=2,
                      ylabel_every=2)
    key = WORDS[count]
    pool = {}
    for n_ in (0, 1, 2, 3):
        if n_ == count:
            continue
        if n_ == 0:
            why_ = ("counted no crossing, but the curve does cross the x-axis")
        elif n_ == 1:
            why_ = ("counted one crossing, but the curve stays on one side of the "
                    "x-axis")
        elif n_ == 2:
            why_ = "counted a second crossing that an exponential curve cannot have"
        else:
            why_ = "counted the turning points of a polynomial, not of an exponential"
        pool[WORDS[n_]] = (why_, pair(WORDS[n_], n_))
    order = [WORDS[n_] for n_ in (3, 2, 1, 0) if n_ != count]
    why = (f"The curve approaches the horizontal line y = {num(c)} and lies "
           f"{'on both sides of' if crosses else 'entirely on one side of'} the "
           f"x-axis, so {name}(x) = 0 for {key.lower()} "
           f"{'value' if count == 1 else 'values'} of x.")
    P = {"kind": "nlf_graph_zeros", "a": a, "c": c, "base": base}
    return text_item("nlfunc.graph_zeros", "how often a curve meets the x-axis",
                     "hard", seed, ZEROS.format(n=name), key, sig(count),
                     pick(pool, order, wrongs), rng, P, why, figure=fig)


# ------------------------------------------- matching an equation to a curve

EQUATION = "Which of the following could be the equation of the graph shown in the xy-plane?"


def graph_equation(rng: random.Random, seed: int, *, r=None, p=None, lead=None,
                   wrongs=None) -> object:
    """A quartic with one double zero; which factored equation is it?"""
    r = int(r if r is not None else rng.randint(2, 6))
    p = int(p if p is not None else rng.randint(2, 6))
    lead = q(lead if lead is not None else Q(-1, rng.choice([5, 10, 20])))
    if r == p or lead >= 0 or lead.numerator != -1:
        raise ItemError("the drawn quartic opens downward with a unit fraction outside")

    def body(dr, dp, squared):
        first = f"x(x {MINUS} {num(dr)})" + ("²" if squared == "first" else "")
        second = f"(x + {num(dp)})" + ("²" if squared == "second" else "")
        return f"y = {MINUS}(1/{lead.denominator}){first}{second}"

    key_text = body(r, p, "second")

    def fnc(x, lead=float(lead), r=r, p=p):
        return lead * x * (x - r) * (x + p) ** 2

    span = max(r, p) + 3
    # the window is set by the turning points between the outermost zeros, not
    # by the tails: a curve drawn to the height of its tails is a flat line
    # through all three zeros and shows nothing the question asks about
    inner = max(abs(fnc(x / 8)) for x in range(-8 * p, 8 * r + 1))
    if inner <= 0:
        raise ItemError("the drawn curve is flat between its zeros")
    want = 5 * inner
    mag = 10.0 ** (len(str(int(want))) - 1)
    top = int(next(s * mag for s in (1, 2, 5, 10) if s * mag >= want))
    ystep = top // 5
    fig = plane_curve([fnc], -span, span, -top, top, xstep=1, ystep=ystep,
                      xlabel_every=1, ylabel_every=2)
    pool = {
        "no_square": ("left the repeated zero unsquared, so the curve would cross the "
                      "x-axis there instead of touching it",
                      pair(body(r, p, None), r, p, "none")),
        "swap_no_square": ("swapped the two zeros and left the repeated one unsquared",
                           pair(body(p, r, None), p, r, "none")),
        "swap": ("swapped the two zeros and squared the wrong one",
                 pair(body(p, r, "first"), p, r, "first")),
        "square_other": ("squared the zero the curve crosses rather than the one it "
                         "touches", pair(body(r, p, "first"), r, p, "first")),
    }
    order = ["no_square", "swap_no_square", "swap", "square_other"]
    why = (f"The curve touches the x-axis at x = {MINUS}{num(p)} and crosses it at "
           f"x = 0 and x = {num(r)}, so the factor (x + {num(p)}) is repeated.")
    P = {"kind": "nlf_graph_equation", "r": r, "p": p,
         "lead": [lead.numerator, lead.denominator]}
    return text_item("nlfunc.graph_equation", "matching a polynomial to its graph",
                     "medium", seed, EQUATION, key_text, sig(r, p, "second"),
                     pick(pool, order, wrongs), rng, P, why, figure=fig)
