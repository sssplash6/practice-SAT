"""The system drawn rather than written.

A curve and a line are plotted and the question is where they meet, or how many
times. The picture is generated from the same parameters as the answer, so a
variation moves the curve as well as the options, and the wrong answers are the
ones a student reaches by reading the grid: the vertex instead of the crossing,
the y-intercept of one graph, the two coordinates the wrong way round, a point
that sits on one graph only.

`option_check.py` reads this figure back out of its own SVG -- origin and scale
from the axes and gridlines, the marked point from its circle, the line from its
segment and the curve from its polyline -- and checks the options against the
picture rather than against the parameters that drew it.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis
from ..figure import plane
from ..kit import (MINUS, choices, join, mono, num, pick, point, q, sent,
                   text_choices)

__all__ = ["graph_solution", "graph_count", "function_meets"]

FRAMES = {
    "nonlinear": "The graph of a system of a linear equation and a nonlinear "
                 "equation is shown. What is the solution (x, y) to this system?",
    "quadratic": "The graph of a system of a linear and a quadratic equation is "
                 "shown. What is the solution (x, y) to this system?",
    "absolute": "The graph of a system of an absolute value function and a linear "
                "function is shown. What is the solution (x, y) to this system of "
                "two equations?",
}

COUNT_FRAME = ("A system of equations consists of a quadratic equation and a "
               "linear equation. The equations in this system are graphed in the "
               "xy-plane above. How many solutions does this system have?")


# ---------------------------------------------------------------- the curves

def _curve(kind, a, h, k):
    a, h, k = float(a), float(h), float(k)
    if kind == "parabola":
        return lambda x: a * (x - h) ** 2 + k
    if kind == "absolute":
        return lambda x: a * abs(x - h) + k
    if kind == "exponential":
        return lambda x: k + a ** (x - h)
    raise ItemError(f"unknown curve {kind!r}")


def _curve_text(kind, a, h, k) -> str:
    inner = f"x {MINUS} {num(h)}" if q(h) > 0 else (f"x + {num(-h)}" if h else "x")
    body = {"parabola": f"({inner})²", "absolute": f"|{inner}|",
            "exponential": f"{num(a)}^({inner})"}[kind]
    a = q(a)
    head = ("" if a == 1 or kind == "exponential" else
            (num(a) if a.denominator == 1 else f"({num(a)})"))
    tail = "" if q(k) == 0 else (f" + {num(k)}" if q(k) > 0 else f" {MINUS} {num(-k)}")
    return f"y = {head}{body}{tail}"


def _line_ends(m, b, xmin, xmax, ymin, ymax):
    m, b = q(m), q(b)
    seen = []
    for x in (Q(xmin), Q(xmax)):
        y = m * x + b
        if ymin <= y <= ymax:
            seen.append((x, y))
    if m != 0:
        for y in (Q(ymin), Q(ymax)):
            x = (y - b) / m
            if xmin < x < xmax:
                seen.append((x, y))
    out = []
    for p in seen:
        if p not in out:
            out.append(p)
    if len(out) < 2:
        raise ItemError("the line barely crosses the drawn window")
    out.sort(key=lambda p: (float(p[0]), float(p[1])))
    return out[0], out[-1]


# ------------------------------------------------- where the two graphs meet

def graph_solution(rng: random.Random, seed: int, *, kind=None, a=1, h=None, k=None,
                   m=None, x0=None, window=None, step=2, frame=None, offsets=None,
                   wrongs=None, difficulty="easy") -> Item:
    """A drawn curve and a drawn line; name the point they share.

    The line is built through the crossing point, so the picture cannot disagree
    with the key: everything drawn is derived from the same four numbers.
    """
    kind = kind or rng.choice(["parabola", "absolute", "exponential"])
    h = Q(rng.randint(-2, 6)) if h is None else q(h)
    k = Q(rng.randint(-2, 6)) if k is None else q(k)
    a = q(a)
    if kind == "exponential" and a <= 1:
        raise ItemError("an exponential curve needs a base above one")
    if x0 is None:
        x0 = Q(rng.randint(window[0] + 1, window[1] - 1) if window
               else rng.randint(-2, 6))
    x0 = q(x0)
    if kind == "absolute" and x0 == h:
        raise ItemError("the line would meet the V at its corner")
    y0 = _value(kind, a, h, k, x0)
    if y0 is None or y0.denominator != 1:
        raise ItemError("the crossing point is not on the grid")
    m = Q(rng.choice([i for i in range(-3, 4) if i])) if m is None else q(m)
    b = y0 - m * x0

    lo = int(min(0, x0, h)) - 3
    hi = int(max(0, x0, h)) + 5
    ylo = int(min(0, y0, k)) - 2
    yhi = int(max(0, y0, k)) + 5
    xmin, xmax, ymin, ymax = window or (lo, hi, ylo, yhi)
    if not (xmin < x0 < xmax and ymin < y0 < ymax):
        raise ItemError("the crossing point is not inside the drawn window")
    if _crossings(kind, a, h, k, m, b) != 1:
        raise ItemError("the drawn line does not meet the drawn curve exactly once")

    fig = plane(xmin, xmax, ymin, ymax, curves=[_curve(kind, a, h, k)],
                segments=[_line_ends(m, b, xmin, xmax, ymin, ymax)],
                points=[(x0, y0)], step=step)
    frame = frame or {"parabola": "quadratic", "absolute": "absolute",
                      "exponential": "nonlinear"}[kind]
    stem = sent(FRAMES[frame])

    offsets = offsets or [1, -1, 2]
    key = point(x0, y0)
    pool = {
        "swap": Mis("wrote the two coordinates the wrong way round", point(y0, x0)),
        "origin": Mis("named the origin rather than the point the two graphs share",
                      point(0, 0) if (x0, y0) != (0, 0) else None),
        "vertex": Mis("named the lowest point of the curve rather than where the "
                      "line crosses it", point(h, k) if (h, k) != (x0, y0) else None),
        "y_axis_line": Mis("read where the line meets the y-axis instead of where "
                           "it meets the curve", point(0, b) if b.denominator == 1
                           and x0 != 0 else None),
        "y_axis_curve": Mis("read where the curve meets the y-axis instead",
                            _at(kind, a, h, k, Q(0)) if x0 != 0 else None),
        "x_only": Mis("read the x-coordinate off the grid and then wrote it twice",
                      point(x0, x0) if x0 != y0 else None),
        "y_sign": Mis("read the y-coordinate on the wrong side of the axis",
                      point(x0, -y0) if y0 else None),
        "y_then_zero": Mis("wrote the y-coordinate in the x place and paired it "
                           "with zero", point(y0, 0) if y0 != 0 and y0 != x0 else None),
        "x_sign": Mis("read the x-coordinate on the wrong side of the axis",
                      point(-x0, y0) if x0 else None),
    }
    for i, t in enumerate(offsets, start=1):
        xx = x0 + Q(t)
        pool[f"on_line_{i}"] = Mis(f"read the crossing point {_off(t)}, landing on "
                                   "the line but not the curve",
                                   point(xx, m * xx + b))
        pool[f"on_curve_{i}"] = Mis(f"read the crossing point {_off(t)}, landing on "
                                    "the curve but not the line",
                                    _at(kind, a, h, k, xx))
    P = {"kind": "nleq_graph_solution", "curve": kind, "a": _p(a), "h": _p(h),
         "k": _p(k), "m": _p(m), "b": _p(b), "x0": _p(x0), "y0": _p(y0)}
    rationale = sent(f"The drawn curve is {_curve_text(kind, a, h, k)} and the drawn "
                     f"line is y = {join([mono(m, 'x'), mono(b, '')])}; they meet "
                     f"at {key}.")
    ch, why, letter = text_choices(key, pick(pool, wrongs), rng, check=False)
    return Item("nleq.graph_solution", "reading a system off a graph", difficulty,
                seed, stem, "mcq", E(1), letter, rationale, ch, why, list(ch),
                figure=fig, params=dict(P, options=list(ch)))


def _value(kind, a, h, k, x):
    a, h, k, x = q(a), q(h), q(k), q(x)
    if kind == "parabola":
        return a * (x - h) ** 2 + k
    if kind == "absolute":
        return a * abs(x - h) + k
    e = x - h
    if e.denominator != 1:
        return None
    return k + (a ** int(e) if e >= 0 else Q(1) / a ** int(-e))


def _at(kind, a, h, k, x) -> str | None:
    v = _value(kind, a, h, k, x)
    return None if v is None or v.denominator != 1 else point(x, v)


def _crossings(kind, a, h, k, m, b) -> int:
    """How many points the drawn line and the drawn curve actually share.

    Worked out from the shapes rather than sampled, because a tangency read off a
    sample grid is a coin toss: the parabola gives a discriminant, the V gives one
    linear equation per branch inside that branch's own half-line, and a rising
    exponential is only offered against a falling line, where the difference is
    strictly increasing and there can be exactly one.
    """
    a, h, k, m, b = q(a), q(h), q(k), q(m), q(b)
    if kind == "parabola":
        A, B, C = a, -(2 * a * h + m), a * h * h + k - b
        d = B * B - 4 * A * C
        return 0 if d < 0 else (1 if d == 0 else 2)
    if kind == "absolute":
        hits = 0
        if a - m != 0:
            x = (b - k + a * h) / (a - m)
            hits += x >= h
        if -a - m != 0:
            x = (b - k - a * h) / (-a - m)
            hits += x <= h
        return hits
    if (a > 1 and m < 0) or (0 < a < 1 and m > 0):
        return 1
    return 2


WORDS = {1: "one", 2: "two", 3: "three"}


def _off(t: int) -> str:
    n = abs(int(t))
    side = "left" if t < 0 else "right"
    if n > 3:
        return f"well to the {side} of where the graphs meet"
    unit = "gridline" if n == 1 else "gridlines"
    return f"{WORDS[n]} {unit} to the {side}"


# --------------------------------------------- how many times they meet

def graph_count(rng: random.Random, seed: int, *, a=None, h=None, k=None, m=None,
                b=None, window=None, step=5, wrongs=None,
                difficulty="medium") -> Item:
    """A drawn parabola and a drawn line; count the points they share."""
    a = Q(rng.choice([1, 1, 2, -1])) if a is None else q(a)
    h = Q(rng.randint(-4, 4)) if h is None else q(h)
    k = Q(rng.randint(-8, 4)) if k is None else q(k)
    m = Q(rng.choice([i for i in range(-3, 4)])) if m is None else q(m)
    b = Q(rng.randint(-8, 8)) if b is None else q(b)
    if a == 0:
        raise ItemError("that is not a parabola")
    # a(x − h)² + k = mx + b  ->  a x² − (2ah + m) x + (a h² + k − b) = 0
    A, B, C = a, -(2 * a * h + m), a * h * h + k - b
    disc = B * B - 4 * A * C
    count = 0 if disc < 0 else (1 if disc == 0 else 2)
    xmin, xmax, ymin, ymax = window or (-10, 10, -10, 10)
    if count:
        from math import sqrt
        r = sqrt(float(disc))
        roots = [(float(-B) - r) / float(2 * A), (float(-B) + r) / float(2 * A)]
        if any(not (xmin + 1 < x < xmax - 1) for x in roots):
            raise ItemError("a crossing falls outside the drawn window")
        if any(not (ymin + 1 < float(m) * x + float(b) < ymax - 1) for x in roots):
            raise ItemError("a crossing falls outside the drawn window")
    fig = plane(xmin, xmax, ymin, ymax, curves=[_curve("parabola", a, h, k)],
                segments=[_line_ends(m, b, xmin, xmax, ymin, ymax)], step=step)
    stem = sent(COUNT_FRAME)
    pool = {
        "zero": Mis("read the two graphs as missing each other altogether", Q(0)),
        "one": Mis("counted only the crossing on one side of the curve's turning "
                   "point", Q(1)),
        "two": Mis("counted two crossings where the line only touches the curve",
                   Q(2)),
        "three": Mis("counted the curve's turning point as a crossing as well",
                     Q(3)),
    }
    pool = {kk: v for kk, v in pool.items() if float(v.value) != count}
    P = {"kind": "nleq_graph_count", "a": _p(a), "h": _p(h), "k": _p(k), "m": _p(m),
         "b": _p(b), "count": count}
    rationale = sent(f"Setting {_curve_text('parabola', a, h, k)} equal to the drawn "
                     f"line leaves a quadratic with discriminant {num(disc)}, so the "
                     f"two graphs share "
                     f"{['no points', 'exactly one point', 'two points'][count]}.")
    keyx = E(Q(count))
    ch, tex, why, letter = choices(keyx, pick(pool, wrongs), rng, sign_rule=False)
    return Item("nleq.graph_count", "counting crossings on a graph", difficulty,
                seed, stem, "mcq", keyx, letter, rationale, ch, why, tex,
                figure=fig, params=P)


def _p(v) -> list:
    v = q(v)
    return [v.numerator, v.denominator]


# ------------------------------------- one drawn function against another

def function_meets(rng: random.Random, seed: int, *, a=None, h=None, k=None, m=None,
                   b=None, window=None, step=1, fname="f", gname="g",
                   difficulty="hard") -> Item:
    """f is drawn and given by a formula, g is not drawn; where do they agree?

    The picture carries the shape of f and nothing else -- the formula is printed
    beside it -- so the item is answerable from the text alone and the figure is
    what tells a reader which branch the answers sit on.
    """
    a = rng.choice([Q(-1, 2), Q(1, 2), Q(-1), Q(1), Q(-1, 4)]) if a is None else q(a)
    h = Q(rng.randint(0, 8)) if h is None else q(h)
    k = Q(rng.randint(2, 14)) if k is None else q(k)
    m = Q(rng.choice([i for i in range(-3, 4) if i])) if m is None else q(m)
    b = Q(rng.randint(0, 14)) if b is None else q(b)
    if a == 0:
        raise ItemError("that is not a parabola")
    # a(x − h)² + k = mx + b  ->  a x² − (2ah + m)x + (a h² + k − b) = 0
    A, B, C = a, -(2 * a * h + m), a * h * h + k - b
    disc = B * B - 4 * A * C
    if disc <= 0:
        raise ItemError("the two functions never agree")
    from math import isqrt
    dd = disc
    rn, rd = isqrt(dd.numerator), isqrt(dd.denominator)
    if rn * rn != dd.numerator or rd * rd != dd.denominator:
        raise ItemError("the two agree at points the grid cannot show")
    r = Q(rn, rd)
    xs = sorted({(-B - r) / (2 * A), (-B + r) / (2 * A)})
    if any(x.denominator != 1 for x in xs) or xs[0] == xs[1]:
        raise ItemError("the two agree at points the grid cannot show")
    xmin, xmax, ymin, ymax = window or (0, int(max(xs) + 2), 0,
                                        int(k) + 2 if a < 0 else int(k) + 12)
    if not all(xmin <= x <= xmax for x in xs):
        raise ItemError("an agreement falls outside the drawn window")
    fig = plane(xmin, xmax, ymin, ymax, curves=[_curve("parabola", a, h, k)],
                step=step, labels=[(h, k + (1 if a < 0 else -1),
                                    f"y = {fname}(x)")])
    inner = f"x {MINUS} {num(h)}" if h > 0 else (f"x + {num(-h)}" if h else "x")
    head = num(a) if q(a).denominator == 1 else f"({num(a)})"
    ftext = f"{fname}(x) = {head}({inner})² + {num(k)}"
    gtext = f"{gname}(x) = " + join([mono(m, "x"), mono(b, "")])
    stem = sent(f"The graph of the function {fname}, defined by {ftext}, is shown in "
                f"the xy-plane above. If the function {gname} (not shown) is defined "
                f"by {gtext}, what is one possible value of a such that "
                f"{fname}(a) = {gname}(a) ?")
    key = xs[-1]
    P = {"kind": "nleq_function_meets", "a": _p(a), "h": _p(h), "k": _p(k),
         "m": _p(m), "b": _p(b)}
    gathered = join([mono(A, "a", 2), mono(B, "a"), mono(C, "")])
    rationale = sent(f"Setting {head}({inner})² + {num(k)} equal to "
                     f"{join([mono(m, 'x'), mono(b, '')])} and gathering gives "
                     f"{gathered} = 0, so a = {num(xs[0])} or a = {num(xs[1])}.")
    from ..kit import gridin, griddable
    if not griddable(key):
        raise ItemError("that answer could not be entered in the grid")
    return Item("nleq.function_meets", "two functions that agree", difficulty, seed,
                stem, "spr", E(key), gridin(key), rationale, figure=fig, params=P)
