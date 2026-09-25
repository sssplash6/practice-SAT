"""Items whose line is drawn rather than written.

Every picture is generated from the same numbers as the stem, so a variation
moves the line as well as the words. Reading a rate off a graph has its own
misconceptions -- the y-intercept taken for the rate, a single plotted point
divided by its own x-coordinate -- and those are the options here.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....figures import coordinate_grid
from ....item import Item, ItemError, Mis, assemble, gridin_mistakes
# `_ticks` places the gridlines `line_graph` draws, and how finely a reader
# can take a value off the picture is exactly the gap between them. The
# guard below has to use the same function that draws them: an
# approximation of the spacing would drift away from the picture.
from ....plot import _ticks, line_graph
from ...linear_functions.common import (MINUS, choose, coef_text, ex, lin_text, money,
                                        numtext, q)
from .define import _text_item, pair, sig

__all__ = ["graph_read", "graph_shifted"]

READ_CTX = [
    dict(ask="value",
         stem="Oxygen gas is placed inside a tank with a constant volume. The graph shows "
              "the estimated temperature y, in kelvins, of the oxygen gas when its "
              "pressure is x atmospheres. What is the estimated temperature, in kelvins, "
              "of the oxygen gas when its pressure is {x} atmospheres?",
         xlabel="Pressure (atmospheres)", ylabel="Temperature (kelvins)",
         mrange=(50, 150), mscale=1, brange=(50, 300), x0=1, x1=9, xrange=(2, 8)),
    dict(ask="value",
         stem="Hydrogen is placed inside a container and kept at a constant pressure. The "
              "graph shows the estimated volume y, in liters, of the hydrogen when its "
              "temperature is x kelvins. What is the estimated volume, in liters, of the "
              "hydrogen when its temperature is {x} kelvins?",
         xlabel="Temperature (kelvins)", ylabel="Volume (liters)",
         mrange=(5, 20), mscale=500, brange=(0, 0), x0=100, x1=800, xrange=(200, 700),
         xstep=100, proportional=True),
    dict(ask="rate", money=True,
         stem="The line graphed in the xy-plane below models the total cost, in dollars, "
              "for a cab ride, y, in a certain city during nonpeak hours based on the "
              "number of miles traveled, x. According to the graph, what is the cost for "
              "each additional mile traveled, in dollars, of a cab ride?",
         xlabel="Distance traveled (miles)", ylabel="Cost (dollars)",
         mrange=(1, 6), mscale=1, brange=(2, 8), x0=0, x1=6),
    dict(ask="rate",
         stem="The graph shown models the number of candy bars a certain machine wraps "
              "with a label in x seconds. According to the graph, what is the estimated "
              "number of candy bars the machine wraps with a label per second?",
         xlabel="Time (seconds)", ylabel="Number of candy bars wrapped",
         mrange=(15, 60), mscale=1, brange=(0, 0), x0=0, x1=6, proportional=True),
    dict(ask="equation",
         stem="The graph above shows the distance traveled d, in feet, by a product on a "
              "conveyor belt m minutes after the product is placed on the belt. Which of "
              "the following equations correctly relates d and m ?",
         xlabel="Time (minutes)", ylabel="Distance traveled (feet)", lhs="d", var="m",
         mrange=(2, 9), mscale=1, brange=(0, 0), x0=0, x1=3, proportional=True),
]


def graph_read(rng: random.Random, seed: int, *, ctx=None, m=None, b=None, x=None,
               fmt=None) -> Item:
    """A line is drawn; read a value, the rate, or the whole equation off it."""
    d = READ_CTX[rng.randrange(len(READ_CTX))] if ctx is None else READ_CTX[ctx]
    m = q(m) if m is not None else Q(rng.randint(*d["mrange"]), d.get("mscale", 1))
    if d.get("proportional"):
        b = Q(0)
    else:
        b = q(b) if b is not None else Q(rng.randint(*d["brange"]))
    if m <= 0:
        raise ItemError("the drawn line must rise")
    x0, x1 = d["x0"], d["x1"]
    pts = [(x0, m * x0 + b), (x1, m * x1 + b)]
    fig = line_graph(pts, d["xlabel"], d["ylabel"])
    ys = [float(p[1]) for p in pts]
    ticks = _ticks(min(min(ys), 0.0), max(ys) * 1.1 or 1.0)
    gridline = float(ticks[1] - ticks[0]) if len(ticks) > 1 else (max(ys) or 1.0)

    if d["ask"] == "equation":
        lhs, var = d["lhs"], d["var"]
        key = f"{lhs} = {coef_text(m, var)}"
        wrongs = [Mis("inverted the rate read off the graph",
                      pair(f"{lhs} = {coef_text(1 / m, var)}", 1 / m, 0)),
                  Mis("read the rate as a constant term",
                      pair(f"{lhs} = {lin_text(1, m, var)}", 1, m)),
                  Mis("added a starting amount the graph does not show",
                      pair(f"{lhs} = {lin_text(m, m, var)}", m, m)),
                  Mis("doubled the rate read off the graph",
                      pair(f"{lhs} = {coef_text(2 * m, var)}", 2 * m, 0))]
        P = {"kind": "lf_graph_read", "ask": "equation",
             "m": [m.numerator, m.denominator], "b": [b.numerator, b.denominator]}
        rationale = (f"The line passes through the origin and rises {numtext(m)} for every "
                     f"1 along, so {key}.")
        return _text_item("lin.graph_read", "reading a line off a graph", "easy", seed,
                          d["stem"], key, sig(m, 0), wrongs, rng, P, rationale, figure=fig)

    if d["ask"] == "value":
        step = d.get("xstep", 1)
        lo, hi = d["xrange"]
        x = q(x) if x is not None else q(rng.randrange(lo, hi + 1, step))
        if not (x0 <= x <= x1):
            raise ItemError("the requested input is off the drawn line")
        key = m * x + b
        stem = d["stem"].format(x=numtext(x))
        mistakes = [Mis("read the value where the line meets the vertical axis", b),
                    Mis("gave the rate rather than the value at that input", m),
                    Mis("divided the input by the value instead of reading the graph",
                        x / key if key != 0 else None),
                    Mis("gave the input rather than the value read off the graph", x),
                    Mis("left out the starting amount", m * x)]
        # the vertical axis is drawn at the frame's left edge, x0, where the line
        # reads m*x0 + b; and x/key needs the key itself, so it is no route to a
        # wrong answer a student types
        spr = [Mis(mistakes[0].reason, m * x0 + b)] + mistakes[1:2] + mistakes[3:]
        # a value taken off the picture is read to within a fraction of a
        # gridline, so an option that sits nearer the key than half a gridline
        # is not a wrong answer -- it is the same reading printed twice
        tol = gridline / 2
        P = {"kind": "lf_graph_read", "ask": "value", "m": [m.numerator, m.denominator],
             "b": [b.numerator, b.denominator], "x": [x.numerator, x.denominator]}
        rationale = (f"The line has slope {numtext(m)} and passes through "
                     f"(0, {numtext(b)}), so at x = {numtext(x)} the value is "
                     f"{numtext(key)}.")
        skill, difficulty = "reading a value off a graph", "easy"
    else:
        key = m
        stem = d["stem"]
        top = m * x1 + b
        if b != 0:
            x_read = q(max(1, x1 - 1))
            mistakes = [Mis("read the y-intercept as the rate", b),
                        Mis("divided a plotted value by its input, ignoring the fixed "
                            "amount", (m * x_read + b) / x_read),
                        Mis("divided the largest plotted value by the y-intercept",
                            top / b),
                        Mis("inverted the rate", 1 / m)]
        else:
            mistakes = [Mis("read the rise over two units without halving it", 2 * m),
                        Mis("gave the input at a labelled gridline instead of the rate",
                            q(2)),
                        Mis("halved the rate", m / 2),
                        Mis("read the rise over five units without dividing", 5 * m)]
        spr = mistakes
        # a rate is two such readings divided by the distance between them, so
        # what the picture can separate shrinks with the run
        tol = gridline / (2 * float(x1 - x0)) if x1 != x0 else gridline
        P = {"kind": "lf_graph_read", "ask": "rate", "m": [m.numerator, m.denominator],
             "b": [b.numerator, b.denominator]}
        rationale = (f"The line rises {numtext(m)} for every 1 along, so the rate is "
                     f"{numtext(m)}.")
        skill, difficulty = "a rate of change from a graph", "easy"

    keyx = ex(key)
    fmt = fmt or "mcq"
    def apart(ms):
        return [Mis(r.reason, ex(r.value)) for r in ms if r.value is not None
                and abs(float(r.value) - float(key)) >= tol]
    if fmt == "spr":
        return Item("lin.graph_read", skill, difficulty, seed, stem, "spr", keyx,
                    keyx.gridin(), rationale, figure=fig, params=P,
                    spr_mistakes=gridin_mistakes(keyx, apart(spr)))
    mistakes = apart(mistakes)
    fmt_value = money if d.get("money") else None
    if d.get("money"):
        P["money"] = True
    choices, latex, reasons, letter = choose(keyx, mistakes, rng, fmt_value=fmt_value,
                                               signed=True)
    return Item("lin.graph_read", skill, difficulty, seed, stem, "mcq", keyx, letter,
                rationale, choices, reasons, latex, figure=fig, params=P)


# ------------------------------------------------------------ shifted graph

def graph_shifted(rng: random.Random, seed: int, *, m=None, c=None, k=None,
                  name=None) -> Item:
    """The graph shown is y = f(x) − k, so the drawn intercept is not f's."""
    name = name or rng.choice(["f", "g", "h"])
    m = q(m if m is not None else rng.choice([rng.randint(-6, -1), rng.randint(1, 6)]))
    c = q(c if c is not None else rng.randint(-8, 8))
    k = q(k if k is not None else rng.randint(2, 20))
    if m == 0 or c == 0 or k == 0:
        raise ItemError("the drawn line must cross both axes away from the origin")
    xi = -c / m
    if xi.denominator != 1:
        raise ItemError("the drawn line must cross the axes at lattice points")
    b = c + k
    lo, hi = int(xi) - 2, int(xi) + 2
    seg = ((lo, int(m * lo + c)), (hi, int(m * hi + c)))
    ys = [seg[0][1], seg[1][1]]
    fig = coordinate_grid(min(lo, 0) - 1, max(hi, 0) + 1, min(min(ys), 0) - 1,
                          max(max(ys), 0) + 1, segments=[seg], step=1)
    stem = (f"The graph of y = {name}(x) {MINUS} {numtext(k)} is shown. Which equation "
            f"defines "
            f"the linear function {name}?")
    key = f"{name}(x) = {lin_text(m, b)}"
    wrongs = [Mis("subtracted the shift from the slope instead of the constant term",
                  pair(f"{name}(x) = {lin_text(m - k, b)}", m - k, b)),
              Mis("used the shift itself as the constant term",
                  pair(f"{name}(x) = {lin_text(m, -k)}", m, -k)),
              Mis("subtracted the shift from the slope and used it as the constant term",
                  pair(f"{name}(x) = {lin_text(m - k, -k)}", m - k, -k)),
              Mis("read the drawn constant term as the function's own",
                  pair(f"{name}(x) = {lin_text(m, c)}", m, c))]
    P = {"kind": "lf_graph_shift", "m": [m.numerator, m.denominator],
         "c": [c.numerator, c.denominator], "k": [k.numerator, k.denominator]}
    rationale = (f"The drawn line is y = {lin_text(m, c)}, and that is {name}(x) "
                 f"{MINUS} "
                 f"{numtext(k)}, so {key}.")
    return _text_item("lin.graph_shifted", "a vertically shifted graph", "medium", seed,
                      stem, key, sig(m, b), wrongs, rng, P, rationale, figure=fig)
