"""The line of best fit: predicting from it, measuring it, naming it.

Every scatterplot in this file is built from its line rather than fitted to it.
`fit_scatter` adds a residual vector that is orthogonal to both 1 and x, which
is precisely the condition for ordinary least squares to return the line it
started from, so the drawn points really do have the drawn line as their line
of best fit -- exactly, not approximately. `option_check.py` recovers both from
the picture's own pixels and refits, which is the only way to be sure the figure
and the answer have not drifted apart.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text
from ...two_variable_data import charts
from ..common import (assemble_num, closest_guard, count_word, fit_scatter, num_str,
                      pick, q, regression, separated, snap, wiggle)

__all__ = ["predict_from_line", "fit_slope", "fit_equation", "residual", "slope_scaled"]


_snap = snap


def _window(values, step, pad=1, every=1):
    """A y-window on whole gridlines, starting and ending on a *labelled* one.

    An axis whose printed labels read 0.5, 2.5, 4.5 is a tell that nobody chose
    them, so the window is aligned to the spacing of the labels rather than to
    the spacing of the gridlines.
    """
    lo = min(q(v) for v in values)
    hi = max(q(v) for v in values)
    step, big = q(step), q(step) * every
    y0 = (lo // big) * big
    y1 = (hi // big + 1) * big
    while lo - y0 < step:
        y0 -= big
    while y1 - hi < step:
        y1 += big
    if lo >= 0 and y0 < 0:
        y0 = Q(0)
    return y0, y1


def lin_text(m, b, var="x", *, lhs="y", order="slope_first", places=None) -> str:
    """A line as the source prints one: y = −x + 6, n = 16,090 + 4,680t, y = 100x."""
    m, b = q(m), q(b)
    if m == 0:
        raise ItemError("a line of best fit with no slope is not one of these items")
    body = var if m == 1 else (f"−{var}" if m == -1 else f"{num_str(m, places)}{var}")
    if order == "intercept_first":
        head = num_str(b, places)
        join = " − " if m < 0 else " + "
        tail = var if abs(m) == 1 else f"{num_str(abs(m), places)}{var}"
        return f"{lhs} = {head}{join}{tail}" if b != 0 else f"{lhs} = {body}"
    if b == 0:
        return f"{lhs} = {body}"
    join = " − " if b < 0 else " + "
    return f"{lhs} = {body}{join}{num_str(abs(b), places)}"


_EQ = __import__("re").compile(r"^\s*\w+\s*=\s*(.+)$")
_TERM = __import__("re").compile(r"([+−-]?)\s*([\d.,]*)\s*([a-z]?)")


def _read_back(text: str, var: str) -> tuple:
    """A printed equation as (slope, intercept) -- read from the string itself."""
    body = _EQ.match(text).group(1).replace(" ", "").replace(",", "")
    slope, const, i = Q(0), Q(0), 0
    while i < len(body):
        mt = _TERM.match(body, i)
        if mt is None or mt.end() == i:
            raise ItemError(f"cannot read back {text!r}")
        sign, digits, name = mt.groups()
        v = q(digits) if digits else Q(1)
        if sign in ("-", "−"):
            v = -v
        if name:
            slope += v
        else:
            const += v
        i = mt.end()
    return slope, const


def _points(rng, m, b, xs, resid, res):
    xs = [q(v) for v in xs]
    if resid is None:
        resid = wiggle(rng, len(xs), res)
    return fit_scatter(m, b, xs, resid)


# ------------------------------------------------------------ predicting a y

PREDICT_CTX = [
    dict(intro="The scatterplot shows the high temperature on a certain day and the "
               "elevation of {n} different locations in the Lake Tahoe Basin. A line of "
               "best fit for the data is also shown.",
         ask="What temperature is predicted by the line of best fit for a location in "
             "the Lake Tahoe Basin with an elevation of {x} feet?",
         title="Temperature and Elevation", xlabel="Elevation (feet)",
         ylabel="Temperature (°F)", suffix="°F",
         x0=6_000, x1=9_000, xa=6_200, xb=8_900, xstep=500, xlabel_every=1,
         ystep=1, ylabel_every=1, gap=2, prec=1, res=Q(1, 4),
         mnum=(-13, -7), mden=5_000, ymid=(40, 42)),
    dict(intro="The scatterplot shows the densities of {n} planetoids, in grams per cubic "
               "centimetre, with respect to their average distances from the Sun in "
               "astronomical units (AU). The line of best fit is also shown.",
         ask="An astronomer has discovered a new planetoid about {x} AU from the Sun. "
             "According to the line of best fit, which of the following best "
             "approximates the density of the planetoid, in grams per cubic centimetre?",
         title="Distance and Density of Planetoids in the Inner Solar System",
         xlabel="Distance from the Sun (AU)", ylabel="Density (g/cm³)", suffix="",
         x0=0, x1=Q(16, 5), xa=Q(2, 5), xb=3, xstep=Q(2, 5), xlabel_every=1,
         ystep=Q(1, 2), ylabel_every=1, gap=Q(1, 2), prec=Q(1, 10), res=Q(1, 5),
         mnum=(-45, -35), mden=50, ymid=(4, 5)),
    dict(intro="{n} data points are shown in the scatterplot. A line of best fit for the "
               "data is also shown.",
         ask="At x = {x}, which of the following is closest to the y-value predicted by "
             "the line of best fit?",
         title="", xlabel="x", ylabel="y", suffix="",
         x0=0, x1=2_000, xa=100, xb=1_700, xstep=300, xlabel_every=2,
         ystep=1, ylabel_every=2, gap=1, prec=1, res=Q(1, 2),
         mnum=(7, 13), mden=1_200, ymid=(9, 12)),
    dict(intro="The scatterplot shows the relationship between two variables, x and y. A "
               "line of best fit for the data is also shown.",
         ask="At x = {x}, which of the following is closest to the y-value predicted by "
             "the line of best fit?",
         title="", xlabel="x", ylabel="y", suffix="",
         x0=24, x1=36, xa=24, xb=34, xstep=1, xlabel_every=2,
         ystep=Q(1, 2), ylabel_every=4, gap=Q(9, 10), prec=Q(1, 10), res=Q(1, 2),
         mnum=(-11, -7), mden=10, ymid=(4, 6)),
    dict(intro="Each dot in the scatterplot represents the temperature and the number of "
               "people who visited a beach in Lagos, Nigeria, on one of {n} different "
               "days. The line of best fit for the data is also shown.",
         ask="According to the line of best fit, what is the number of people, rounded "
             "to the nearest {r}, predicted to visit this beach on a day with an average "
             "temperature of {x}°C?",
         title="Number of Beach Visitors versus Temperature",
         xlabel="Average temperature (°C)", ylabel="Number of people", suffix="",
         x0=25, x1=35, xa=25, xb=35, xstep=1, xlabel_every=2,
         ystep=40, ylabel_every=2, gap=40, prec=40, res=25,
         mnum=(50, 64), mden=1, ymid=(360, 420), spr=True),
    dict(intro="The densities of different concentrations of grape juice are shown in "
               "the scatterplot.",
         ask="According to the trend shown by the data, which of the following is "
             "closest to the predicted density, in kilograms per cubic metre (kg/m³), "
             "for grape juice with a concentration of {x}%?",
         title="Density of Grape Juice", xlabel="Concentration", ylabel="Density (kg/m³)",
         suffix="", no_line=True, percent_x=True,
         x0=20, x1=80, xa=20, xb=70, xstep=10, xlabel_every=1,
         ystep=50, ylabel_every=1, gap=50, prec=50, res=8,
         mnum=(48, 56), mden=10, ymid=(1_200, 1_260)),
]


def predict_from_line(rng: random.Random, seed: int, *, ctx=None, m=None, b=None,
                      xq=None, gap=None, xs=None, resid=None, n=None, fmt="mcq",
                      round_to=None, wrongs=None) -> Item:
    """A line of best fit is drawn; read the value it predicts at a given x."""
    d = PREDICT_CTX[rng.randrange(len(PREDICT_CTX))] if ctx is None else PREDICT_CTX[ctx]
    m = q(m) if m is not None else Q(rng.randint(*d["mnum"]), d["mden"])
    if m == 0:
        raise ItemError("a flat line of best fit predicts nothing")
    xa, xb = q(d["xa"]), q(d["xb"])
    if xs is None:
        n = n or rng.randint(8, 12)
        xs = [xa + (xb - xa) * Q(i, n - 1) for i in range(n)]
    xs = [q(v) for v in xs]
    n = len(xs)
    if b is None:
        mid = (xa + xb) / 2
        b = q(rng.randint(*d["ymid"])) - m * mid
    b = q(b)
    pts = _points(rng, m, b, xs, resid, d["res"])
    if regression(pts) != (m, b):
        raise ItemError("the drawn points do not have the drawn line as their best fit")

    step, gap = q(d["ystep"]), q(gap if gap is not None else d["gap"])
    prec = q(d["prec"])
    if gap < step:
        raise ItemError("the options are spaced more finely than the chart's gridlines")
    if xq is None:
        inside = [v for v in charts.ticks_between(xa, xb, d["xstep"]) if xa < v < xb]
        if not inside:
            raise ItemError("no gridline inside the data to ask about")
        xq = inside[rng.randrange(len(inside))]
    xq = q(xq)
    if not q(d["x0"]) <= xq <= q(d["x1"]):
        raise ItemError("the question asks about an x outside the chart")
    if d.get("spr") and round_to is None:
        # this stem prints "rounded to the nearest ...", which only makes sense
        # when the question says what to round to
        round_to, fmt = 10, "spr"
    true = m * xq + b
    key = snap(true, q(round_to) if round_to is not None else prec, strict=True)
    if key <= 0:
        raise ItemError("the prediction must be positive on these charts")

    ys = [p[1] for p in pts]
    xstep = q(d["xstep"])
    pool = {
        "one_low": ("read the line one gridline below where it crosses",
                    E(key - gap)),
        "one_high": ("read the line one gridline above where it crosses",
                     E(key + gap)),
        "two_low": ("read the line two gridlines below where it crosses",
                    E(key - 2 * gap)),
        "two_high": ("read the line two gridlines above where it crosses",
                     E(key + 2 * gap)),
        "x_left": ("read the line one gridline to the left of the given x-value",
                   E(_snap(m * (xq - xstep) + b, prec))),
        "x_right": ("read the line one gridline to the right of the given x-value",
                    E(_snap(m * (xq + xstep) + b, prec))),
        "x_left2": ("read the line two gridlines to the left of the given x-value",
                    E(_snap(m * (xq - 2 * xstep) + b, prec))),
        "x_right2": ("read the line two gridlines to the right of the given x-value",
                     E(_snap(m * (xq + 2 * xstep) + b, prec))),
        "half_x": ("halved the given x-value before reading the line",
                   E(_snap(m * xq / 2 + b, gap))),
        "at_end": ("read the line where the data ends instead of at the given x-value",
                   E(_snap(m * xb + b, gap))),
        "at_start": ("read the line where the data starts instead of at the given "
                     "x-value", E(_snap(m * xa + b, gap))),
        "point_high": ("read the highest plotted point instead of the line",
                       E(_snap(max(ys), gap))),
        "point_low": ("read the lowest plotted point instead of the line",
                      E(_snap(min(ys), gap))),
        "near_point": ("read the plotted point nearest the given x-value instead of "
                       "the line",
                       E(_snap(min(pts, key=lambda p: abs(p[0] - xq))[1], gap))),
    }
    order = ["one_low", "one_high", "two_high", "two_low", "x_left", "x_right",
             "point_high", "at_end", "half_x", "near_point", "point_low", "at_start"]

    y0, y1 = _window(list(ys) + [key], step, every=d["ylabel_every"])
    xlabels = None
    if d.get("percent_x"):
        xlabels = {v: f"{charts.fmt_tick(v)}%"
                   for v in charts.ticks_between(d["x0"], d["x1"], d["xstep"])}
    fig = charts.scatter(pts, x0=d["x0"], x1=d["x1"], y0=y0, y1=y1,
                         xstep=d["xstep"], ystep=step, xlabel_every=d["xlabel_every"],
                         ylabel_every=d["ylabel_every"], xlabel=d["xlabel"],
                         ylabel=d["ylabel"], title=d["title"], xlabels=xlabels,
                         line=None if d.get("no_line") else (m, b))
    ask = d["ask"].format(x=num_str(xq), n=count_word(n),
                          r=num_str(round_to) if round_to is not None else "")
    stem = f"{d['intro'].format(n=count_word(n))} {ask}"
    P = dict(kind="tvdata.predict_from_line", m=str(m), b=str(b), xq=str(xq),
             gap=str(q(round_to) if round_to is not None else prec),
             xs=[str(v) for v in xs], ys=[str(v) for v in ys])
    why = (f"The line of best fit passes {num_str(xq)} at about {num_str(key)}.")
    if fmt == "spr":
        return Item("tvdata.predict_from_line", "line of best fit", "easy", seed, stem,
                    "spr", E(key), E(key).gridin(), why, figure=fig, params=P)
    mistakes = pick(pool, order, wrongs)
    choices, latex, reasons, letter = assemble_num(key, mistakes, rng,
                                                   suffix=d["suffix"])
    vals = [q(c.replace("−", "-").replace(",", "").rstrip("°FC")) for c in choices]
    others = [v for v in vals if v != key]
    separated(key, others, step)
    closest_guard(true, key, others)
    return Item("tvdata.predict_from_line", "line of best fit", "easy", seed, stem,
                "mcq", E(key), letter, why, choices, reasons, latex, figure=fig,
                params=P)


# ---------------------------------------------------------------- the slope

SLOPE_CTX = [
    dict(intro="In the given scatterplot, a line of best fit for the data is shown.",
         ask="Which of the following is closest to the slope of this line of best fit?",
         title="", xlabel="x", ylabel="y",
         x0=0, x1=10, xa=0, xb=10, xstep=1, xlabel_every=1, ystep=1, ylabel_every=1,
         gap=Q(1, 2), prec=Q(1, 10), res=Q(1, 2), mnum=(-9, 9), mden=10,
         ymid=(4, 6)),
    dict(intro="The scatterplot shows the relationship between two variables, x and y. A "
               "line of best fit is also shown.",
         ask="Which of the following is closest to the slope of the line of best fit "
             "shown?",
         title="", xlabel="x", ylabel="y",
         x0=0, x1=14, xa=1, xb=13, xstep=1, xlabel_every=2, ystep=1, ylabel_every=2,
         gap=Q(4, 5), prec=Q(1, 10), res=Q(3, 2), mnum=(-12, 12), mden=10,
         ymid=(6, 8)),
    dict(intro="The scatterplot shows the numbers of grams of both total protein and "
               "total fat for {n} sandwiches on a restaurant menu. The line of best fit "
               "for the data is also shown.",
         ask="According to the line of best fit, which of the following is closest to "
             "the predicted increase in total fat, in grams, for every increase of 1 "
             "gram in total protein?",
         title="Total Protein and Total Fat for Eight Sandwiches",
         xlabel="Total protein (grams)", ylabel="Total fat (grams)",
         x0=0, x1=50, xa=10, xb=45, xstep=10, xlabel_every=1, ystep=10, ylabel_every=1,
         gap=Q(1, 2), prec=Q(1, 2), res=2, mnum=(10, 22), mden=10, ymid=(40, 50)),
    dict(intro="In the given scatterplot, a line of best fit for the data is shown.",
         ask="Which of the following is closest to the slope of the line of best fit "
             "shown?",
         title="", xlabel="x", ylabel="y",
         x0=0, x1=10, xa=1, xb=8, xstep=1, xlabel_every=5, ystep=1, ylabel_every=5,
         gap=Q(4, 5), prec=Q(1, 10), res=1, mnum=(12, 24), mden=10, ymid=(7, 10)),
]


def fit_slope(rng: random.Random, seed: int, *, ctx=None, m=None, b=None, gap=None,
              xs=None, resid=None, n=None, places=None, wrongs=None) -> Item:
    """Measure the slope of the drawn line of best fit."""
    d = SLOPE_CTX[rng.randrange(len(SLOPE_CTX))] if ctx is None else SLOPE_CTX[ctx]
    m = q(m) if m is not None else Q(rng.randint(*d["mnum"]), d["mden"])
    if m == 0:
        raise ItemError("a flat line of best fit has nothing to measure")
    xa, xb = q(d["xa"]), q(d["xb"])
    if xs is None:
        n = n or rng.randint(8, 11)
        xs = [xa + (xb - xa) * Q(i, n - 1) for i in range(n)]
    xs = [q(v) for v in xs]
    n = len(xs)
    if b is None:
        b = q(rng.randint(*d["ymid"])) - m * (xa + xb) / 2
    b = q(b)
    pts = _points(rng, m, b, xs, resid, d["res"])
    if regression(pts) != (m, b):
        raise ItemError("the drawn points do not have the drawn line as their best fit")
    gap = q(gap if gap is not None else d["gap"])
    key = snap(m, q(d["prec"]), strict=True)
    if key == 0:
        raise ItemError("a slope that rounds to zero is not an answer")
    pool = {
        "sign": ("read the line as rising when it falls, or the reverse", E(-key)),
        "times_ten": ("moved the decimal point one place", E(key * 10)),
        "sign_times_ten": ("moved the decimal point one place and lost the sign",
                           E(-key * 10)),
        "reciprocal": ("divided the run by the rise instead of the rise by the run",
                       E(_snap(1 / key, gap)) if key != 0 else None),
        "one_up": ("counted one gridline too many in the rise", E(key + gap)),
        "one_down": ("counted one gridline too few in the rise", E(key - gap)),
        "two_up": ("counted two gridlines too many in the rise", E(key + 2 * gap)),
        "two_down": ("counted two gridlines too few in the rise", E(key - 2 * gap)),
        "sign_two_up": ("counted two gridlines too many in the rise and read the line "
                        "as rising when it falls", E(-(key + 2 * gap))),
        "sign_two_down": ("counted two gridlines too few in the rise and read the line "
                          "as rising when it falls", E(-(key - 2 * gap))),
        "intercept": ("gave the value where the line meets the vertical axis",
                      E(_snap(b, gap))),
    }
    order = ["sign", "times_ten", "sign_times_ten", "one_up", "one_down", "two_up",
             "two_down", "sign_two_up", "sign_two_down", "reciprocal", "intercept"]
    mistakes = pick(pool, order, wrongs)
    choices, latex, reasons, letter = assemble_num(key, mistakes, rng, signed=True,
                                                   places=places)
    vals = [q(c.replace("−", "-").replace(",", "")) for c in choices]
    others = [v for v in vals if v != key]
    # one gridline over the whole width of the chart is the finest change of
    # slope a reader could possibly see in the drawn line
    separated(key, others, q(d["ystep"]) / (q(d["x1"]) - q(d["x0"])))
    closest_guard(m, key, others)

    ys = [p[1] for p in pts]
    y0, y1 = _window(ys, q(d["ystep"]), every=d["ylabel_every"])
    fig = charts.scatter(pts, x0=d["x0"], x1=d["x1"], y0=y0, y1=y1, xstep=d["xstep"],
                         ystep=d["ystep"], xlabel_every=d["xlabel_every"],
                         ylabel_every=d["ylabel_every"], xlabel=d["xlabel"],
                         ylabel=d["ylabel"], title=d["title"], line=(m, b))
    P = dict(kind="tvdata.fit_slope", m=str(m), b=str(b), gap=str(q(d["prec"])),
             xs=[str(v) for v in xs], ys=[str(v) for v in ys])
    return Item("tvdata.fit_slope", "line of best fit", "medium", seed,
                f"{d['intro'].format(n=count_word(n))} {d['ask']}", "mcq", E(key),
                letter,
                f"The drawn line {'rises' if m > 0 else 'falls'} "
                f"{num_str(abs(m) * 10)} for every 10 it runs, a slope of about "
                f"{num_str(key)}.",
                choices, reasons, latex, figure=fig, params=P)


# ------------------------------------------------------- naming the equation

EQ_CTX = [
    dict(intro="", ask="Which of the following could be an equation for a line of best "
                       "fit for the data in the scatterplot?",
         title="", xlabel="x", ylabel="y", lhs="y", var="x", order="slope_first",
         places=None, x0=0, x1=6, xa=0, xb=5, xstep=1, xlabel_every=1,
         ystep=1, ylabel_every=1, res=Q(1, 4), mnum=(-15, 15), mden=10, ymid=(3, 5)),
    dict(intro="Each dot in the scatterplot represents the height x, in feet, in the "
               "high jump, and the distance y, in feet, in the long jump, made by each "
               "student in a group of {n} students.",
         ask="The graph of which of the following equations is a line that most closely "
             "fits the data?",
         title="", xlabel="High jump height (feet)", ylabel="Long jump distance (feet)",
         lhs="y", var="x", order="slope_first", places=2,
         x0=0, x1=6, xa=1, xb=5, xstep=1, xlabel_every=1, ystep=2, ylabel_every=1,
         res=Q(3, 2), mnum=(250, 380), mden=100, ymid=(9, 12)),
    dict(intro="The scatterplot shows the number of visitors to a railroad museum in "
               "Pennsylvania each year from {y0} to {y1}, where t is the number of years "
               "since {y0} and n is the number of visitors. A line of best fit is also "
               "shown.",
         ask="Which of the following could be an equation of the line of best fit shown?",
         title="Railroad Museum Visitors", xlabel="Years since {y0}",
         ylabel="Annual visitors", lhs="n", var="t", order="intercept_first",
         places=0, x0=0, x1=15, xa=0, xb=12, xstep=5, xlabel_every=1,
         ystep=20_000, ylabel_every=1, res=4_000, mnum=(4_000, 5_200), mden=1,
         ymid=(40_000, 48_000), year0=(1_960, 1_975)),
    dict(intro="The scatterplot shows a company's ice cream sales d, in dollars, and the "
               "high temperature t, in degrees Celsius (°C), on {n} different days. A "
               "line of best fit for the data is also shown.",
         ask="Which of the following could be an equation of the line of best fit?",
         title="Ice Cream Sales", xlabel="Temperature (°C)", ylabel="Sales (dollars)",
         lhs="d", var="t", order="slope_first", places=None,
         x0=10, x1=26, xa=12, xb=25, xstep=2, xlabel_every=1, ystep=100,
         ylabel_every=1, res=40, mnum=(28, 38), mden=1, ymid=(650, 720)),
    dict(intro="The scatterplot shows the size x and the sale price y of {n} houses for "
               "sale in Town H.",
         ask="Which of the following could be an equation for a line of best fit for the "
             "data?",
         title="Size and Sale Price of Houses in Town H",
         xlabel="Size (thousands of square feet)",
         ylabel="Sale price (thousands of dollars)", lhs="y", var="x",
         order="slope_first", places=None,
         x0=0, x1=3, xa=Q(4, 5), xb=Q(13, 5), xstep=Q(1, 2), xlabel_every=2,
         ystep=50, ylabel_every=1, res=30, mnum=(80, 130), mden=1, ymid=(250, 290)),
    dict(intro="", ask="Which of the following could be the equation for a line of best "
                       "fit for the data shown in the scatterplot?",
         title="", xlabel="x", ylabel="y", lhs="y", var="x", order="slope_first",
         places=None, x0=0, x1=10, xa=1, xb=8, xstep=2, xlabel_every=1,
         ystep=5, ylabel_every=1, res=1, mnum=(20, 35), mden=10, ymid=(12, 18)),
]


def fit_equation(rng: random.Random, seed: int, *, ctx=None, m=None, b=None, xs=None,
                 resid=None, n=None, alt_m=None, year0=None, wrongs=None) -> Item:
    """Four equations are printed; one could be the drawn line of best fit."""
    d = EQ_CTX[rng.randrange(len(EQ_CTX))] if ctx is None else EQ_CTX[ctx]
    m = q(m) if m is not None else Q(rng.randint(*d["mnum"]), d["mden"])
    if m == 0:
        raise ItemError("a flat line is not one of these items")
    xa, xb = q(d["xa"]), q(d["xb"])
    if xs is None:
        n = n or rng.randint(8, 12)
        xs = [xa + (xb - xa) * Q(i, n - 1) for i in range(n)]
    xs = [q(v) for v in xs]
    n = len(xs)
    if b is None:
        b = q(rng.randint(*d["ymid"])) - m * (xa + xb) / 2
    b = q(b)
    if b == 0:
        raise ItemError("a line of best fit through the origin hides its intercept")
    pts = _points(rng, m, b, xs, resid, d["res"])
    if regression(pts) != (m, b):
        raise ItemError("the drawn points do not have the drawn line as their best fit")
    ys = [p[1] for p in pts]
    y0, y1 = _window(ys, q(d["ystep"]), every=d["ylabel_every"])

    P = dict(order=d["order"], places=d["places"], lhs=d["lhs"], var=d["var"])
    show = lambda mm, bb: lin_text(mm, bb, d["var"], lhs=d["lhs"], order=d["order"],
                                   places=d["places"])
    key = show(m, b)
    alt = q(alt_m) if alt_m is not None else None
    pool = {
        "swap": ("exchanged the slope and the y-intercept",
                 show(b, m) if b != m else None),
        "swap_intercept_sign": ("exchanged the slope and the y-intercept and lost the "
                                "sign of the y-intercept",
                                show(b, -m) if b != -m else None),
        "swap_sign": ("exchanged the slope and the y-intercept and lost the sign of "
                      "the slope", show(-b, m)),
        "slope_sign": ("read the line as rising when it falls, or the reverse",
                       show(-m, b)),
        "intercept_sign": ("gave the y-intercept the wrong sign", show(m, -b)),
        "slope_half": ("halved the rise when measuring the slope", show(m / 2, b)),
        "slope_double": ("doubled the rise when measuring the slope", show(2 * m, b)),
        "no_intercept": ("assumed the line passes through the origin", show(m, 0)),
        "b_twice": ("used the y-intercept for the slope as well", show(b, -b)),
        "m_twice": ("used the slope for the y-intercept as well", show(m, -m)),
        "slope_reciprocal": ("divided the run by the rise instead of the rise by the "
                             "run", show(_snap(1 / m, Q(1, 100)), b)
                             if m != 0 and _snap(1 / m, Q(1, 100)) != 0 else None),
        "axis_min": ("read the y-intercept off the bottom of an axis that does not "
                     "start at zero", show(m, y0) if y0 not in (0, b) else None),
        "alt_slope": ("measured the rise over half the run", show(alt, b)
                      if alt not in (None, m) else None),
        "alt_swap": ("measured the rise over half the run and then exchanged the slope "
                     "and the y-intercept", show(b, alt) if alt not in (None, m) else None),
    }
    order = ["swap", "slope_sign", "swap_sign", "swap_intercept_sign",
             "intercept_sign", "slope_double",
             "slope_half", "no_intercept", "b_twice", "m_twice", "slope_reciprocal",
             "axis_min", "alt_slope", "alt_swap"]
    mistakes = pick(pool, order, wrongs)
    span = max(ys) - min(ys)
    for miss in mistakes:
        mm, bb = _read_back(miss.value, d["var"])
        if max(abs((mm - m) * x + (bb - b)) for x in xs) < span / 4:
            raise ItemError(f"the option {miss.value!r} is too close to the line of "
                            f"best fit to be wrong")
    choices, reasons, letter = assemble_text(key, mistakes, rng)

    year = year0 if year0 is not None else (
        rng.randint(*d["year0"]) if "year0" in d else None)
    fmt = dict(n=count_word(n), y0=year, y1=None if year is None else year + int(xb))
    fig = charts.scatter(pts, x0=d["x0"], x1=d["x1"], y0=y0, y1=y1, xstep=d["xstep"],
                         ystep=d["ystep"], xlabel_every=d["xlabel_every"],
                         ylabel_every=d["ylabel_every"],
                         xlabel=d["xlabel"].format(**fmt), ylabel=d["ylabel"],
                         title=d["title"], line=(m, b))
    P.update(kind="tvdata.fit_equation", m=str(m), b=str(b), texts=list(choices),
             xs=[str(v) for v in xs], ys=[str(v) for v in ys])
    intro = d["intro"].format(**fmt)
    stem = f"{intro} {d['ask']}".strip()
    return Item("tvdata.fit_equation", "line of best fit", "medium", seed, stem, "mcq",
                E(0), letter,
                f"The drawn line meets the vertical axis near {num_str(b)} and "
                f"{'rises' if m > 0 else 'falls'} {num_str(abs(m))} for each 1 it "
                f"runs.",
                choices, reasons, list(choices), figure=fig, params=P)


# -------------------------------------------------------------- the residual

RESID_CTX = [
    dict(intro="The scatterplot shows the relationship between two variables, x and y. A "
               "line of best fit for the data is also shown.",
         ask="Which of the following is closest to the difference between the "
             "y-coordinate of the data point with x = {x} and the y-value predicted by "
             "the line of best fit at x = {x}?",
         pickby="x", title="", xlabel="x", ylabel="y",
         x0=0, x1=6, xa=0, xb=5, xstep=1, xlabel_every=1, ystep=1, ylabel_every=1,
         gap=1, prec=1, n=6, mnum=(-14, -8), mden=10, ymid=(9, 10)),
    dict(intro="The scatterplot shows data for {n} charities along with the line of best "
               "fit.",
         ask="For the charity with the greatest percent of total expenses spent on "
             "programs, which of the following is closest to the difference of the "
             "actual percent and the percent predicted by the line of best fit?",
         pickby="highest", title="Income and Percent of Total Expenses Spent on Programs",
         xlabel="Total income (millions of dollars)",
         ylabel="Percent spent on programs", suffix="%",
         x0=0, x1=7_000, xa=500, xb=6_350, xstep=1_000, xlabel_every=1,
         ystep=Q(5, 2), ylabel_every=2, gap=3, prec=1, n=10, mnum=(10, 18),
         mden=10_000, ymid=(84, 87)),
]


def residual(rng: random.Random, seed: int, *, ctx=None, m=None, b=None, xs=None,
             resid=None, n=None, j=None, gap=None, wrongs=None) -> Item:
    """How far one plotted point sits from the line of best fit."""
    d = RESID_CTX[rng.randrange(len(RESID_CTX))] if ctx is None else RESID_CTX[ctx]
    m = q(m) if m is not None else Q(rng.randint(*d["mnum"]), d["mden"])
    xa, xb = q(d["xa"]), q(d["xb"])
    if xs is None:
        # the stem prints the x it names, so those x-values have to be numbers a
        # page would print: they sit on the gridlines rather than wherever an
        # arbitrary count of points would put them
        n = n or d["n"]
        xs = [xa + (xb - xa) * Q(i, n - 1) for i in range(n)]
    xs = [q(v) for v in xs]
    n = len(xs)
    if b is None:
        b = q(rng.randint(*d["ymid"])) - m * (xa + xb) / 2
    b = q(b)
    gap = q(gap if gap is not None else d["gap"])
    if resid is None:
        resid = wiggle(rng, n, gap)
    pts = fit_scatter(m, b, xs, resid)
    if regression(pts) != (m, b):
        raise ItemError("the drawn points do not have the drawn line as their best fit")
    ys = [p[1] for p in pts]
    rs = [q(v) for v in resid]
    if j is None:
        j = max(range(n), key=lambda i: ys[i]) if d["pickby"] == "highest" \
            else rng.randrange(n)
    if d["pickby"] == "x" and q(xs[j]).denominator != 1:
        raise ItemError("the stem would print an x-value as a fraction")
    if d["pickby"] == "highest" and ys.index(max(ys)) != j:
        raise ItemError("the point the question names is not the highest one plotted")
    if d["pickby"] == "highest":
        rest = sorted(ys)[:-1]
        if not rest or max(ys) - rest[-1] < q(d["ystep"]):
            raise ItemError("the highest plotted point is within a gridline of the "
                            "next highest, so no reader could tell which is meant")
    if rs[j] <= 0:
        raise ItemError("the stem asks for a difference, so the point named must lie "
                        "above the line")
    key = snap(rs[j], q(d["prec"]), strict=True)
    if key <= 0:
        raise ItemError("that point lies on the line, so there is no gap to measure")

    pool = {
        "one_low": ("counted one gridline too few", E(key - gap)),
        "one_high": ("counted one gridline too many", E(key + gap)),
        "two_high": ("counted two gridlines too many", E(key + 2 * gap)),
        "two_low": ("counted two gridlines too few", E(key - 2 * gap)),
        "point_y": ("gave the y-coordinate of the point itself",
                    E(_snap(ys[j], gap))),
        "line_y": ("gave the value the line predicts, not the gap",
                   E(_snap(m * xs[j] + b, gap))),
        "double": ("doubled the gap", E(2 * key)),
        "biggest": ("measured at the point furthest from the line, not the one named",
                    E(_snap(max(abs(v) for v in rs), gap))),
    }
    order = ["one_low", "one_high", "two_high", "two_low", "point_y", "double",
             "line_y", "biggest"]
    mistakes = pick(pool, order, wrongs)
    choices, latex, reasons, letter = assemble_num(key, mistakes, rng,
                                                   suffix=d.get("suffix", ""))
    vals = [q(c.replace("−", "-").replace(",", "").rstrip("%")) for c in choices]
    others = [v for v in vals if v != key]
    separated(key, others, q(d["ystep"]))
    closest_guard(rs[j], key, others)

    y0, y1 = _window(ys, q(d["ystep"]), every=d["ylabel_every"])
    fig = charts.scatter(pts, x0=d["x0"], x1=d["x1"], y0=y0, y1=y1, xstep=d["xstep"],
                         ystep=d["ystep"], xlabel_every=d["xlabel_every"],
                         ylabel_every=d["ylabel_every"], xlabel=d["xlabel"],
                         ylabel=d["ylabel"], title=d["title"], line=(m, b))
    P = dict(kind="tvdata.residual", m=str(m), b=str(b), j=j, gap=str(gap),
             xs=[str(v) for v in xs], ys=[str(v) for v in ys])
    stem = (f"{d['intro'].format(n=count_word(n))} "
            f"{d['ask'].format(x=num_str(xs[j]))}").strip()
    return Item("tvdata.residual", "line of best fit", "medium", seed, stem, "mcq",
                E(key), letter,
                f"The point is at about {num_str(ys[j], 1)} and the line predicts "
                f"about {num_str(m * xs[j] + b, 1)} there.",
                choices, reasons, latex, figure=fig, params=P)


# ------------------------------------------------- the slope over k units of x

SCALE_CTX = [
    dict(intro="Each dot in the scatterplot represents the temperature and the number of "
               "people who visited a beach in Lagos, Nigeria, on one of {n} different "
               "days. The line of best fit for the data is also shown. The line of best "
               "fit for the data has a slope of approximately {m}.",
         ask="According to this estimate, how many additional people per day are "
             "predicted to visit the beach for each {k}°C increase in average "
             "temperature?",
         title="Number of Beach Visitors versus Temperature",
         xlabel="Average temperature (°C)", ylabel="Number of people",
         x0=25, x1=35, xa=25, xb=35, xstep=1, xlabel_every=2, ystep=40, ylabel_every=2,
         res=25, mnum=(50, 64), mden=1, ymid=(360, 420)),
    dict(intro="The scatterplot shows the monthly electricity use, in kilowatt-hours, of "
               "a household against the mean outdoor temperature, in degrees Fahrenheit, "
               "for {n} months. The line of best fit for the data has a slope of "
               "approximately {m}.",
         ask="According to this estimate, how many fewer kilowatt-hours are predicted "
             "to be used for each {k}°F increase in mean outdoor temperature?",
         title="Electricity Use and Temperature",
         xlabel="Mean outdoor temperature (°F)", ylabel="Electricity use (kilowatt-hours)",
         x0=30, x1=80, xa=32, xb=78, xstep=10, xlabel_every=1, ystep=100, ylabel_every=1,
         res=40, mnum=(-16, -8), mden=1, ymid=(700, 900), negated=True),
]


def slope_scaled(rng: random.Random, seed: int, *, ctx=None, m=None, b=None, k=None,
                 xs=None, resid=None, n=None) -> Item:
    """The slope is stated; report the change it predicts over k units of x."""
    d = SCALE_CTX[rng.randrange(len(SCALE_CTX))] if ctx is None else SCALE_CTX[ctx]
    m = q(m) if m is not None else Q(rng.randint(*d["mnum"]), d["mden"])
    k = q(k) if k is not None else Q(rng.randrange(2, 11))
    if m == 0 or k <= 1:
        raise ItemError("the stated slope and step must both be real")
    xa, xb = q(d["xa"]), q(d["xb"])
    if xs is None:
        n = n or rng.randint(8, 12)
        xs = [xa + (xb - xa) * Q(i, n - 1) for i in range(n)]
    xs = [q(v) for v in xs]
    n = len(xs)
    if b is None:
        b = q(rng.randint(*d["ymid"])) - m * (xa + xb) / 2
    b = q(b)
    pts = _points(rng, m, b, xs, resid, d["res"])
    if regression(pts) != (m, b):
        raise ItemError("the drawn points do not have the drawn line as their best fit")
    key = abs(m) * k
    if key.denominator != 1:
        raise ItemError("that step gives an answer that is not a whole number of people")
    ys = [p[1] for p in pts]
    y0, y1 = _window(ys, q(d["ystep"]), every=d["ylabel_every"])
    fig = charts.scatter(pts, x0=d["x0"], x1=d["x1"], y0=y0, y1=y1, xstep=d["xstep"],
                         ystep=d["ystep"], xlabel_every=d["xlabel_every"],
                         ylabel_every=d["ylabel_every"], xlabel=d["xlabel"],
                         ylabel=d["ylabel"], title=d["title"], line=(m, b))
    P = dict(kind="tvdata.slope_scaled", m=str(m), k=str(k))
    stem = (f"{d['intro'].format(n=count_word(n), m=num_str(m))} "
            f"{d['ask'].format(k=num_str(k))}")
    return Item("tvdata.slope_scaled", "line of best fit", "hard", seed, stem, "spr",
                E(key), E(key).gridin(),
                f"A slope of {num_str(m)} means a change of {num_str(abs(m))} for "
                f"each 1, so {num_str(abs(m))} × {num_str(k)} = {num_str(key)} for "
                f"each {num_str(k)}.", figure=fig, params=P)
