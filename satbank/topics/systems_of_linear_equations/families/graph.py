"""The system drawn rather than written.

Two lines are plotted and the question is where they meet. The picture is
generated from the same two slopes and intercepts as the answer, so a variation
moves the lines as well as the options, and the wrong answers are the ones a
student reaches by reading the grid: a point that sits on one line only, the two
coordinates written the wrong way round, a fraction rounded to the gridline.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....figures import coordinate_grid
from ....item import Item, ItemError, Mis, assemble_text
from ..kit import displayed, num, opt_pair, pick, point, q, sent, std

__all__ = ["graph_solution"]

FRAMES = {
    "shown": "The graph of a system of linear equations is shown. What is the "
             "solution (x, y) to the system?",
    "below": "A system of two linear equations is graphed in the xy-plane below. "
             "Which of the following points is the solution to the system of "
             "equations?",
    "same_solution": "Which of the following systems of equations has the same "
                     "solution as the system of equations graphed above?",
}


def _ends(m, b, xmin, xmax, ymin, ymax):
    """Where the line leaves the drawn window, as the two points to draw between."""
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


def graph_solution(rng: random.Random, seed: int, *, m1=None, b1=None, m2=None,
                   b2=None, ask="pair", frame=None, window=None, step=2,
                   offsets=None, wrongs=None, difficulty="easy") -> Item:
    """Two drawn lines; name the point they share, or the system that shares it."""
    m1 = q(m1) if m1 is not None else Q(rng.choice([i for i in range(-4, 5) if i]))
    m2 = q(m2) if m2 is not None else Q(rng.choice(range(-4, 5)))
    if m1 == m2:
        raise ItemError("two parallel lines never meet")
    b1 = q(b1) if b1 is not None else Q(rng.randint(-8, 8))
    b2 = q(b2) if b2 is not None else Q(rng.randint(-8, 8))
    x0 = (b2 - b1) / (m1 - m2)
    y0 = m1 * x0 + b1
    if ask == "pair" and (x0.denominator != 1 or y0.denominator != 1):
        raise ItemError("the crossing point is not on the grid")
    if abs(x0) > 12 or abs(y0) > 18:
        raise ItemError("the crossing point falls outside a readable window")

    if window is None:
        lo = int(min(0, x0)) - 3
        hi = int(max(0, x0)) + 4
        ylo = int(min(0, y0)) - 3
        yhi = int(max(0, y0)) + 4
        window = (lo, hi, ylo, yhi)
    xmin, xmax, ymin, ymax = window
    if not (xmin < x0 < xmax and ymin < y0 < ymax):
        raise ItemError("the crossing point is not inside the drawn window")
    segs = [_ends(m1, b1, *window), _ends(m2, b2, *window)]
    fig = coordinate_grid(xmin, xmax, ymin, ymax, segments=segs, step=step)

    offsets = offsets or [-1, 1, 2]
    if ask == "pair":
        frame = frame or rng.choice(["shown", "below"])
        key = point(x0, y0)
        pool = {"swap": Mis("wrote the two coordinates in the wrong order",
                            point(y0, x0)),
                "y_axis1": Mis("read where the first line meets the y-axis instead of "
                               "where the two lines meet", point(0, b1)),
                "y_axis2": Mis("read where the second line meets the y-axis instead "
                               "of where the two lines meet", point(0, b2))}
        for i, t in enumerate(offsets, start=1):
            pool[f"on1_{i}"] = Mis(f"read the crossing point {_off(t)}, landing on "
                                   "the first line but not the second",
                                   point(x0 + t, m1 * (x0 + t) + b1))
            pool[f"on2_{i}"] = Mis(f"read the crossing point {_off(t)}, landing on "
                                   "the second line but not the first",
                                   point(x0 + t, m2 * (x0 + t) + b2))
    else:
        frame = frame or "same_solution"
        floor = Q(x0.numerator // x0.denominator)
        key = opt_pair(std(0, 1, y0), std(1, 0, x0))
        pool = {
            "swapped": Mis("read the crossing point's two coordinates the wrong way "
                           "round", opt_pair(std(0, 1, x0), std(1, 0, y0))),
            "rounded": Mis("rounded the x-coordinate down to the gridline below it",
                           opt_pair(std(0, 1, y0), std(1, 0, floor))
                           if floor != x0 else None),
            "swapped_rounded": Mis("read the two coordinates the wrong way round and "
                                   "rounded the fraction to a gridline",
                                   opt_pair(std(0, 1, floor), std(1, 0, y0))
                                   if floor != y0 else None),
            "origin": Mis("read the point where the lines cross the axes rather than "
                          "each other", opt_pair(std(0, 1, 0), std(1, 0, 0))
                          if (x0, y0) != (0, 0) else None),
        }
    stem = sent(FRAMES[frame])
    P = {"kind": "sys_graph", "m1": _p(m1), "b1": _p(b1), "m2": _p(m2),
         "b2": _p(b2), "ask": ask}
    rationale = sent(f"The drawn lines are {_line(m1, b1)} and {_line(m2, b2)}; "
                     f"setting the two right-hand sides equal gives x = {num(x0)}, "
                     f"and putting that back gives y = {num(y0)}.")
    ch, why, letter = assemble_text(key, pick(pool, wrongs), rng)
    return Item("sys.graph_solution", "reading a system off a graph", difficulty,
                seed, stem, "mcq", E(1), letter, rationale, ch, why, ch,
                figure=fig, params=P)


WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
         7: "seven", 8: "eight", 9: "nine"}


def _off(t: int) -> str:
    n = abs(int(t))
    side = "left" if t < 0 else "right"
    if n > 3:
        return f"well to the {side} of where the lines meet"
    unit = "gridline" if n == 1 else "gridlines"
    return f"{WORDS[n]} {unit} to the {side}"


def _line(m, b) -> str:
    from ..kit import solved
    return solved(1, "y", m, "x", b)


def _p(v) -> list:
    v = q(v)
    return [v.numerator, v.denominator]
