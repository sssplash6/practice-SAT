"""Items whose options are sentences.

Nothing here is decided by arithmetic on the key alone: four sentences are
printed and the student picks the true one, so an item with two true sentences
reaches a student with no defensible answer and passes every check the engine
makes. Each template therefore records, in `params`, everything an outside
reader needs to decide all four for itself -- the sign of the slope, the two
numbers in the equation, the vertices of the graph -- and `option_check.py`
decides them from the printed text.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text
from ....plot import chart_scatter, chart_series
from ..common import (bow, cap_first, count_word, fit_scatter, num_str, pick, q,
                      regression, separated, wiggle)

__all__ = ["association", "interpret_slope", "model_type", "graph_statement"]


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


# ------------------------------------------------------------- the direction

ASSOC_CTX = [
    dict(intro="The scatterplot shows the high temperature on a certain day and the "
               "elevation of {n} different locations in the Lake Tahoe Basin. A line of "
               "best fit for the data is also shown.",
         x="elevation", y="temperature",
         tail="locations in the Lake Tahoe Basin",
         title="Temperature and Elevation", xlabel="Elevation (feet)",
         ylabel="Temperature (°F)",
         x0=6_000, x1=9_000, xa=6_200, xb=8_900, xstep=500, xlabel_every=1,
         ystep=1, ylabel_every=1, res=Q(1, 4), mnum=(-13, -7), mden=5_000,
         ymid=(40, 42)),
    dict(intro="The scatterplot shows the number of hours {n} students spent revising "
               "for a test and the score each student earned. A line of best fit for the "
               "data is also shown.",
         x="number of hours spent revising", y="score",
         tail="students in this group",
         title="Revision Time and Test Score", xlabel="Time spent revising (hours)",
         ylabel="Score",
         x0=0, x1=12, xa=1, xb=11, xstep=1, xlabel_every=2, ystep=5, ylabel_every=2,
         res=2, mnum=(25, 55), mden=10, ymid=(62, 76)),
    dict(intro="The scatterplot shows the age, in years, and the resale value, in "
               "hundreds of dollars, of {n} used cars of the same model. A line of best "
               "fit for the data is also shown.",
         x="age", y="resale value",
         tail="used cars of this model",
         title="Age and Resale Value", xlabel="Age (years)",
         ylabel="Resale value (hundreds of dollars)",
         x0=0, x1=12, xa=1, xb=11, xstep=1, xlabel_every=2, ystep=10, ylabel_every=1,
         res=3, mnum=(-90, -40), mden=10, ymid=(70, 90)),
]


def association(rng: random.Random, seed: int, *, ctx=None, m=None, b=None, xs=None,
                resid=None, n=None) -> Item:
    """Which sentence describes the direction of the relationship."""
    d = ASSOC_CTX[rng.randrange(len(ASSOC_CTX))] if ctx is None else ASSOC_CTX[ctx]
    m = q(m) if m is not None else Q(rng.randint(*d["mnum"]), d["mden"])
    if m == 0:
        raise ItemError("a flat line describes no association")
    xa, xb = q(d["xa"]), q(d["xb"])
    if xs is None:
        n = n or rng.randint(7, 11)
        xs = [xa + (xb - xa) * Q(i, n - 1) for i in range(n)]
    xs = [q(v) for v in xs]
    n = len(xs)
    if b is None:
        b = q(rng.randint(*d["ymid"])) - m * (xa + xb) / 2
    b = q(b)
    pts = fit_scatter(m, b, xs, resid if resid is not None else wiggle(rng, n, d["res"]))
    if regression(pts) != (m, b):
        raise ItemError("the drawn points do not have the drawn line as their best fit")

    X, Y = d["x"], d["y"]
    up_up = f"As the {X} increases, the {Y} tends to increase."
    up_down = f"As the {X} increases, the {Y} tends to decrease."
    down_down = f"As the {X} decreases, the {Y} tends to decrease."
    down_up = f"As the {X} decreases, the {Y} tends to increase."
    none = f"There is no association between the {X} and the {Y}."
    if m < 0:
        key, wrong = up_down, [
            Mis("read the line as rising when it falls", up_up),
            Mis("described what happens as the x-value falls but kept the same "
                "direction for the y-value", down_down),
            Mis("read the scatter as having no direction at all", none)]
    else:
        key, wrong = up_up, [
            Mis("read the line as falling when it rises", up_down),
            Mis("described what happens as the x-value falls but reversed the "
                "direction of the y-value", down_up),
            Mis("read the scatter as having no direction at all", none)]
    choices, reasons, letter = assemble_text(key, wrong, rng)

    ys = [p[1] for p in pts]
    y0, y1 = _window(ys, d["ystep"], every=d["ylabel_every"])
    fig = chart_scatter(pts, x0=d["x0"], x1=d["x1"], y0=y0, y1=y1, xstep=d["xstep"],
                         ystep=d["ystep"], xlabel_every=d["xlabel_every"],
                         ylabel_every=d["ylabel_every"], xlabel=d["xlabel"],
                         ylabel=d["ylabel"], title=d["title"], line=(m, b))
    P = dict(kind="tvdata.association", m=str(m), b=str(b), x=X, y=Y,
             xs=[str(v) for v in xs], ys=[str(v) for v in ys], texts=list(choices))
    stem = (f"{d['intro'].format(n=count_word(n))} Which of the following statements "
            f"best describes the association between the {X} and the {Y} of "
            f"{d['tail']}?")
    return Item("tvdata.association", "describing an association", "easy", seed, stem,
                "mcq", E(0), letter,
                f"The line of best fit {'falls' if m < 0 else 'rises'} from left to "
                f"right.", choices, reasons, list(choices), figure=fig, params=P)


# -------------------------------------------------- what the slope stands for

INTERP_CTX = [
    dict(intro="The scatterplot shows the federal-mandated minimum wage every 10 years "
               "between {y0} and {y1}. A line of best fit is shown, and its equation is "
               "{eq}.",
         ask="What does the line of best fit predict about the increase in the minimum "
             "wage over the {span}-year period?",
         quantity="minimum wage", unit="dollars", title="Minimum Wage",
         xlabel="Years since {y0}", ylabel="Minimum wage (dollars)",
         xstep=10, xlabel_every=1, ystep=1, ylabel_every=1, res=Q(1, 4),
         mnum=(80, 120), mden=1_000, bnum=(-600, -300), bden=1_000, places=3),
    dict(intro="The scatterplot shows the mean cost, in dollars, of a cinema ticket "
               "every 10 years between {y0} and {y1}. A line of best fit is shown, and "
               "its equation is {eq}.",
         ask="What does the line of best fit predict about the increase in the mean "
             "ticket cost over the {span}-year period?",
         quantity="mean ticket cost", unit="dollars", title="Mean Cinema Ticket Cost",
         xlabel="Years since {y0}", ylabel="Mean ticket cost (dollars)",
         xstep=10, xlabel_every=1, ystep=2, ylabel_every=1, res=Q(1, 3),
         mnum=(120, 190), mden=1_000, bnum=(-900, -400), bden=1_000, places=3),
]


def interpret_slope(rng: random.Random, seed: int, *, ctx=None, m=None, b=None,
                    span=None, y0=None, n=None, wrongs=None) -> Item:
    """The equation is printed; which sentence says what its slope means."""
    d = INTERP_CTX[rng.randrange(len(INTERP_CTX))] if ctx is None else INTERP_CTX[ctx]
    m = q(m) if m is not None else Q(rng.randint(*d["mnum"]), d["mden"])
    b = q(b) if b is not None else Q(rng.randint(*d["bnum"]), d["bden"])
    if m <= 0 or b >= 0:
        raise ItemError("this stem describes a rising line that starts below the axis")
    span = int(span if span is not None else rng.choice((40, 50, 60, 70, 80)))
    y0 = int(y0 if y0 is not None else rng.randrange(1_930, 1_970, 10))
    y1 = y0 + span
    step = int(d["xstep"])
    xs = [Q(k) for k in range(0, span + 1, step)]
    n = len(xs)
    if n < 5:
        raise ItemError("too few readings to draw")
    pts = fit_scatter(m, b, xs, bow(xs, -b * Q(3, 2)))
    if regression(pts) != (m, b):
        raise ItemError("the drawn points do not have the drawn line as their best fit")

    p = d["places"]
    per_year = num_str(m, p).rstrip("0").rstrip(".")
    per_ten = num_str(10 * m, p).rstrip("0").rstrip(".")
    intercept = num_str(-b, 2)
    intercept_full = num_str(-b, p).rstrip("0").rstrip(".")
    Qy, U = d["quantity"], d["unit"]

    def each(v):
        return f"Each year between {y0} and {y1}, the average increase in {Qy} was {v} {U}."

    def decade(v):
        return (f"Every 10 years between {y0} and {y1}, the average increase in {Qy} "
                f"was {v} {U}.")

    key = each(per_year)
    pool = {
        "intercept_as_rate": ("read the y-intercept as the yearly rate",
                              each(intercept)),
        "per_decade_slope": ("read the slope as a change per 10 years rather than per "
                             "year", decade(per_year)),
        "per_decade_intercept": ("read the y-intercept as a change per 10 years",
                                 decade(intercept_full)),
        "slope_times_ten": ("multiplied the slope by 10 but kept the yearly wording",
                            each(per_ten)),
        "intercept_decade_rounded": ("read the y-intercept as a change per 10 years, "
                                     "rounded", decade(intercept)),
    }
    order = ["intercept_as_rate", "per_decade_slope", "per_decade_intercept",
             "slope_times_ten", "intercept_decade_rounded"]
    mistakes = pick(pool, order, wrongs)
    choices, reasons, letter = assemble_text(key, mistakes, rng)
    if len(set(choices)) != 4:
        raise ItemError("two of the four sentences read the same")

    ys = [pt[1] for pt in pts]
    if min(ys) <= 0:
        raise ItemError("a reading below the axis is not one of these charts")
    ylo, yhi = _window(ys, d["ystep"], every=d["ylabel_every"])
    fig = chart_scatter(pts, x0=0, x1=span + 10, y0=ylo, y1=yhi, xstep=d["xstep"],
                         ystep=d["ystep"], xlabel_every=d["xlabel_every"],
                         ylabel_every=d["ylabel_every"],
                         xlabel=d["xlabel"].format(y0=y0), ylabel=d["ylabel"],
                         title=d["title"], line=(m, b))
    eq = f"y = {num_str(m, p).rstrip('0').rstrip('.')}x − {intercept_full}"
    P = dict(kind="tvdata.interpret_slope", m=str(m), b=str(b), y0=y0, y1=y1,
             quantity=Qy, unit=U, texts=list(choices))
    stem = (f"{d['intro'].format(y0=y0, y1=y1, eq=eq)} "
            f"{d['ask'].format(span=span)}")
    return Item("tvdata.interpret_slope", "interpreting a model", "hard", seed, stem,
                "mcq", E(0), letter,
                f"The slope is the change in {Qy} for each one-year increase in x.",
                choices, reasons, list(choices), figure=fig, params=P)


# ---------------------------------------------------- which shape of model

MODEL_SCENES = [
    dict(text="An inspector begins a day of work with a large sample of shirts that need "
              "to be checked for defects. The inspector works at a constant rate "
              "throughout the morning. What type of model is best to model the number of "
              "shirts remaining to be checked for defects at any given time throughout "
              "the morning?", shape="linear_down"),
    dict(text="A tank holds {a} litres of water. Water is pumped into the tank at a "
              "constant rate of {r} litres per minute. What type of model is best to "
              "model the volume of water in the tank at any given time while the pump "
              "runs?", shape="linear_up"),
    dict(text="A bacterial culture doubles in population every {r} hours. What type of "
              "model is best to model the population of the culture at any given time?",
         shape="exp_growth"),
    dict(text="A sample of a radioactive substance loses {r}% of its mass every hour. "
              "What type of model is best to model the mass of the sample at any given "
              "time?", shape="exp_decay"),
    dict(text="A savings account earns {r}% interest, compounded once per year, and no "
              "money is added to or taken from the account. What type of model is best "
              "to model the balance of the account at any given time?",
         shape="exp_growth"),
    dict(text="A candle {a} centimetres tall burns down at a constant rate of {r} "
              "centimetres per hour. What type of model is best to model the height of "
              "the candle at any given time while it burns?", shape="linear_down"),
    dict(text="A car depreciates in value by {r}% each year. What type of model is best "
              "to model the value of the car at any given time?", shape="exp_decay"),
    dict(text="A cyclist rides away from home at a constant speed of {r} kilometres per "
              "hour. What type of model is best to model the cyclist's distance from "
              "home at any given time during the ride?", shape="linear_up"),
]

SHAPE_TEXT = {"linear_up": "A linear model with a positive slope",
              "linear_down": "A linear model with a negative slope",
              "exp_growth": "An exponential growth model",
              "exp_decay": "An exponential decay model"}

SHAPE_WHY = {
    "linear_up": "reads a quantity that grows by a fixed amount as one that grows by a "
                 "fixed amount, but in the wrong direction",
    "linear_down": "reads a quantity that falls by a fixed amount as one that falls by a "
                   "fixed amount, but in the wrong direction",
    "exp_growth": "reads a fixed amount per unit of time as a fixed percentage",
    "exp_decay": "reads a fixed amount per unit of time as a fixed percentage, falling",
}


def model_type(rng: random.Random, seed: int, *, scene=None, a=None, r=None) -> Item:
    """Constant amount or constant percentage, growing or falling."""
    d = MODEL_SCENES[rng.randrange(len(MODEL_SCENES))] if scene is None \
        else MODEL_SCENES[scene]
    a = int(a if a is not None else rng.randrange(20, 240, 5))
    r = int(r if r is not None else rng.randrange(2, 30))
    key = SHAPE_TEXT[d["shape"]]
    wrong = [Mis(SHAPE_WHY[s], SHAPE_TEXT[s]) for s in SHAPE_TEXT if s != d["shape"]]
    choices, reasons, letter = assemble_text(key, wrong, rng)
    P = dict(kind="tvdata.model_type", shape=d["shape"], texts=list(choices))
    fixed = d["shape"].startswith("linear")
    return Item("tvdata.model_type", "choosing a model", "medium", seed,
                d["text"].format(a=num_str(a), r=num_str(r)), "mcq", E(0), letter,
                f"The quantity changes by a fixed "
                f"{'amount' if fixed else 'percentage'} in equal intervals of time, and "
                f"it {'rises' if d['shape'].endswith(('up', 'growth')) else 'falls'}.",
                choices, reasons, list(choices), params=P)


# ------------------------------------------------- reading a piecewise graph

RUN_CTX = [
    dict(name="Theresa", verb="ran on a treadmill", past="ran", noun="run",
         intro="{name} {verb} for {total} minutes, and her time and speed are shown on "
               "the graph.",
         title="{name}'s Running Speed and Time", xlabel="Time (minutes)",
         ylabel="Speed (miles per hour)", ystep=1, ylabel_every=1, xstep=5,
         xlabel_every=1),
    dict(name="Danielle", verb="cycled on an exercise bike", past="cycled", noun="ride",
         intro="{name} {verb} for {total} minutes, and her time and speed are shown on "
               "the graph.",
         title="{name}'s Cycling Speed and Time", xlabel="Time (minutes)",
         ylabel="Speed (miles per hour)", ystep=1, ylabel_every=1, xstep=5,
         xlabel_every=1),
]


def _segments(vs):
    return [(vs[i], vs[i + 1]) for i in range(len(vs) - 1)]


def graph_statement(rng: random.Random, seed: int, *, ctx=None, pts=None) -> Item:
    """A speed-versus-time graph, and the one sentence about it that is false."""
    d = RUN_CTX[rng.randrange(len(RUN_CTX))] if ctx is None else RUN_CTX[ctx]
    if pts is None:
        total = rng.choice((30, 30, 40))
        cuts = sorted(rng.sample(range(5, total, 5), 4))
        speeds = [0] + [rng.randint(2, 9) for _ in range(4)] + [0]
        pts = list(zip([0] + cuts + [total], speeds))
    pts = [(q(t), q(v)) for t, v in pts]
    ts = [p[0] for p in pts]
    vs = [p[1] for p in pts]
    total = ts[-1]
    if len(pts) < 4 or any(ts[i] >= ts[i + 1] for i in range(len(ts) - 1)):
        raise ItemError("the times must increase")

    segs = [(ts[i], ts[i + 1], vs[i], vs[i + 1]) for i in range(len(ts) - 1)]
    flat = [(a, b) for a, b, u, v in segs if u == v]
    up = sum((b - a for a, b, u, v in segs if v > u), Q(0))
    down = sum((b - a for a, b, u, v in segs if v < u), Q(0))
    if not flat or up == down:
        raise ItemError("this graph does not support the four statements")
    if len({b - a for a, b in flat}) != len(flat):
        raise ItemError("two flat stretches of the same length would read alike")
    flat_len = max(b - a for a, b in flat)
    last = segs[-1]
    top = max(vs)
    if sum(1 for v in vs if v == top) != 1:
        raise ItemError("two points tie for the greatest speed")
    t_top = ts[vs.index(top)]
    tail = total - segs[-1][0]
    if len(segs) < 3:
        raise ItemError("this graph has too few stretches to describe")
    late = total - ts[-3]
    name = d["name"]

    facts = [
        (f"{name} {d['past']} at a constant speed for "
         f"{count_word(int(flat_len))} minutes.", True),
        (f"{name}'s speed was increasing for a longer period of time than it was "
         f"decreasing.", up > down),
        (f"{name}'s speed decreased at a constant rate during the last "
         f"{count_word(int(tail))} minutes.", last[3] < last[2]),
        (f"{name}'s speed reached its maximum during the last "
         f"{count_word(int(late))} minutes.", t_top >= ts[-3]),
    ]
    false = [i for i, (_, ok) in enumerate(facts) if not ok]
    if len(false) != 1:
        raise ItemError("exactly one of the four statements has to be false")
    k = false[0]
    key = facts[k][0]
    wrong = [Mis("the graph does show this, so it is not the statement that is untrue",
                 t) for i, (t, _) in enumerate(facts) if i != k]
    choices, reasons, letter = assemble_text(key, wrong, rng)
    ylo, yhi = _window(vs + [0], d["ystep"], every=d["ylabel_every"])
    fig = chart_series(pts, x0=0, x1=total, y0=ylo, y1=yhi, xstep=d["xstep"],
                        ystep=d["ystep"], xlabel_every=d["xlabel_every"],
                        ylabel_every=d["ylabel_every"], xlabel=d["xlabel"],
                        ylabel=d["ylabel"], title=d["title"].format(name=name))
    P = dict(kind="tvdata.graph_statement", pts=[[str(t), str(v)] for t, v in pts],
             name=name, texts=list(choices))
    stem = (f"{d['intro'].format(name=name, verb=d['verb'], total=count_word(int(total)))} "
            f"According to the graph, which of the following statements is NOT true "
            f"concerning {name}'s {d['noun']}?")
    return Item("tvdata.graph_statement", "reading a graph", "easy", seed, stem, "mcq",
                E(0), letter,
                f"The speed rises for {num_str(up)} minutes and falls for "
                f"{num_str(down)} minutes.",
                choices, reasons, list(choices), figure=fig, params=P)
