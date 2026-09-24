"""Items that ask a student to read a picture.

A point, an interval, an extreme, a value off a curve, a rate between two
plotted points. Everything the student needs is in the figure, and everything
in the figure is generated from the same numbers as the stem, so a variation
moves the dots as well as the words.

The rule that governs this whole family is the gridline rule: a chart can be
read only to the spacing of its own gridlines, so `separated` is called on every
draw before the item is built, and the draw is thrown away when two options are
closer together than the picture can distinguish.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text, gridin_mistakes
from ....plot import chart_curve, chart_scatter, chart_series
from ..common import (ascending, assemble_num, cap_first, closest_guard, count_word,
                      listing, num_str, ordinal, pick, plural, q, separated, snap,
                      year_text)

__all__ = ["point_read", "interval_change", "series_extreme", "curve_read",
           "rate_of_change"]


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


# ------------------------------------------------------------- a single point

POINT_CTX = [
    dict(intro="The scatterplot shows the relationship between the weight, in pounds, of "
               "each of {n} female gray wolves on April 30 and the number of offspring "
               "each gray wolf produced.",
         ask="How many offspring did the {x}-pound gray wolf produce?",
         xlabel="Weight (pounds)", ylabel="Number of offspring",
         xstep=5, xlabel_every=2, ystep=1, ylabel_every=1,
         x_lo=35, x_hi=70, y_lo=4, y_hi=9, spread=1),
    dict(intro="An orchard owner recorded the weight, in pounds, of all nectarines that "
               "grew on a dwarf nectarine tree during each growing season after the "
               "tree's transplantation. The scatterplot shows this weight, in pounds, "
               "for each growing season after the tree's transplantation.",
         ask="What was the weight, to the nearest pound, of all nectarines that grew on "
             "the tree during the {o} growing season after the tree's transplantation?",
         xlabel="Growing season after transplantation", ylabel="Weight of nectarines "
                                                               "(pounds)",
         xstep=1, xlabel_every=1, ystep=10, ylabel_every=1,
         x_lo=1, x_hi=8, y_lo=1, y_hi=90, spread=10, consecutive=True),
    dict(intro="The scatterplot shows the number of books borrowed from a library on "
               "each of {n} days, along with the number of visitors to the library that "
               "day.",
         ask="How many books were borrowed on the day with {x} visitors?",
         xlabel="Number of visitors", ylabel="Number of books borrowed",
         xstep=10, xlabel_every=2, ystep=5, ylabel_every=2,
         x_lo=40, x_hi=140, y_lo=20, y_hi=95, spread=5),
    dict(intro="A cyclist recorded the distance travelled, in kilometres, on each of {n} "
               "training rides, along with the time spent riding. The scatterplot shows "
               "the results.",
         ask="How far did the cyclist travel on the ride that lasted {x} minutes?",
         xlabel="Time (minutes)", ylabel="Distance (kilometres)",
         xstep=10, xlabel_every=2, ystep=2, ylabel_every=2,
         x_lo=20, x_hi=110, y_lo=6, y_hi=38, spread=2),
]


def point_read(rng: random.Random, seed: int, *, ctx=None, xs=None, ys=None,
               target=None, fmt="mcq", wrongs=None) -> Item:
    """Read the y-value of one plotted point straight off the scatterplot."""
    d = POINT_CTX[rng.randrange(len(POINT_CTX))] if ctx is None else POINT_CTX[ctx]
    step = q(d["spread"])
    if xs is None:
        n = rng.randint(7, 10)
        if d.get("consecutive"):
            xs = list(range(d["x_lo"], d["x_lo"] + n))
        else:
            pool = list(range(d["x_lo"], d["x_hi"] + 1, d["xstep"] // 5 or 1))
            if len(pool) < n:
                raise ItemError("not enough distinct x-values for this context")
            xs = sorted(rng.sample(pool, n))
    n = len(xs)
    if len(set(xs)) != n:
        raise ItemError("two readings at the same x-value")
    if ys is None:
        lo, hi = q(d["y_lo"]), q(d["y_hi"])
        rise = (hi - lo) / (n - 1)
        ys = []
        for i in range(n):
            v = lo + rise * i + step * rng.choice((-1, 0, 0, 1))
            snapped = q(int(round(float(v) / float(step)))) * step
            ys.append(max(snapped, lo))
        if len(set(ys)) < 4:
            raise ItemError("the plotted points take too few distinct values")
    if len(ys) != n:
        raise ItemError("one reading per plotted point")
    j = rng.randrange(n) if target is None else target
    key = q(ys[j])
    # A reader locates the point by its x-value, so the dot the question names
    # has to stand clear of its neighbours: half a gridline is the gap at which
    # one dot is visibly on a gridline and the next visibly is not. College
    # Board's own gray-wolf item is drawn exactly that finely.
    separated(xs[j], [v for i, v in enumerate(xs) if i != j], q(d["xstep"]) / 2)

    others = sorted({q(v) for v in ys} - {key})
    if len(others) < 3:
        raise ItemError("too few other plotted values to offer as distractors")
    below = [v for v in others if v < key][-2:]
    above = [v for v in others if v > key][:2]
    pool = {
        "below": ("gave the reading of a point lower on the chart",
                  E(below[-1]) if below else None),
        "below2": ("gave the reading of a point further down the chart",
                   E(below[-2]) if len(below) > 1 else None),
        "above": ("gave the reading of a point higher on the chart",
                  E(above[0]) if above else None),
        "above2": ("gave the reading of a point further up the chart",
                   E(above[1]) if len(above) > 1 else None),
        "largest": ("gave the greatest value on the chart", E(max(others))),
        "smallest": ("gave the least value on the chart", E(min(others))),
        "x_value": ("gave the x-value the question supplies, not the reading",
                    E(q(xs[j])) if q(xs[j]) != key else None),
    }
    order = ["below", "above", "above2", "below2", "largest", "smallest", "x_value"]

    ask = d["ask"].format(x=num_str(xs[j]), o=ordinal(int(xs[j])), n=count_word(n))
    intro = d["intro"].format(n=count_word(n))
    y0, y1 = _window(ys, d["ystep"], every=d["ylabel_every"])
    x0, x1 = q(min(xs)) - q(d["xstep"]), q(max(xs)) + q(d["xstep"])
    fig = chart_scatter([(x, y) for x, y in zip(xs, ys)],
                         x0=x0, x1=x1, y0=y0, y1=y1,
                         xstep=d["xstep"], ystep=d["ystep"],
                         xlabel_every=d["xlabel_every"], ylabel_every=d["ylabel_every"],
                         xlabel=d["xlabel"], ylabel=d["ylabel"])
    P = dict(kind="tvdata.point_read", xs=[str(q(v)) for v in xs],
             ys=[str(q(v)) for v in ys], j=j)
    stem = f"{intro} {ask}"
    mistakes = pick(pool, order, wrongs)
    if fmt == "spr":
        return Item("tvdata.point_read", "reading a scatterplot", "easy", seed, stem,
                    "spr", E(key), E(key).gridin(), "Read the plotted point across to "
                    "the vertical axis.", figure=fig, params=P,
                    spr_mistakes=gridin_mistakes(E(key), mistakes))
    choices, latex, reasons, letter = assemble_num(key, mistakes, rng)
    separated(key, [q(c.replace("−", "-").replace(",", "")) for c in choices
                    if q(c.replace("−", "-").replace(",", "")) != key], d["ystep"])
    return Item("tvdata.point_read", "reading a scatterplot", "easy", seed, stem, "mcq",
                E(key), letter,
                f"The point at {num_str(xs[j])} on the horizontal axis lies at "
                f"{num_str(key)} on the vertical axis.",
                choices, reasons, latex, figure=fig, params=P)


# ------------------------------------------------ the biggest change, interval

CHANGE_CTX = [
    dict(intro="In an experiment, a heated cup of coffee is removed from a heat source, "
               "and the cup of coffee is then left in a room that is kept at a constant "
               "temperature. The graph shows the temperature, in degrees Fahrenheit "
               "(°F), of the coffee immediately after being removed from the heat source "
               "and at {gap}-minute intervals thereafter.",
         ask="During which of the following {gap}-minute intervals does the temperature "
             "of the coffee decrease at the greatest average rate?",
         label="Between {a} and {b} minutes", direction="down", cooling=True,
         xlabel="Time since cup was removed from heat source (minutes)",
         ylabel="Temperature (°F)", kindly="scatter", gap=10, lo=70, hi=200,
         xstep=2, xlabel_every=1, ystep=20, ylabel_every=1),
    dict(intro="The line graph shows the number of 3-D movies released each year from "
               "{first} to {last}.",
         ask="According to the line graph, between which two consecutive years was there "
             "the greatest change in the number of 3-D movies released?",
         label="{a}–{b}", direction="either", year=True,
         xlabel="Year", ylabel="Number of 3-D movies released", kindly="series",
         gap=1, lo=0, hi=60, xstep=1, xlabel_every=1, ystep=5, ylabel_every=2),
    dict(intro="The scatterplot shows the temperature y, in °F, recorded by a "
               "meteorologist at various times x, in days since June 1.",
         ask="During which of the following time periods did the greatest increase in "
             "recorded temperature take place?",
         label="From x = {a} to x = {b}", direction="up",
         xlabel="Time (days since June 1)", ylabel="Temperature (°F)",
         kindly="scatter", gap=1, lo=55, hi=95, xstep=1, xlabel_every=1, ystep=5,
         ylabel_every=2),
    dict(intro="The line graph shows the number of members of a hiking club on January 1 "
               "of each year from {first} to {last}.",
         ask="According to the graph, between which two consecutive years was there the "
             "greatest increase in the number of members?",
         label="{a}–{b}", direction="up", year=True,
         xlabel="Year", ylabel="Number of members", kindly="series",
         gap=1, lo=40, hi=260, xstep=1, xlabel_every=1, ystep=10, ylabel_every=2),
]


def interval_change(rng: random.Random, seed: int, *, ctx=None, values=None,
                    x0=None, gap=None, offer=None) -> Item:
    """Four intervals are offered; one carries the biggest move on the chart."""
    d = CHANGE_CTX[rng.randrange(len(CHANGE_CTX))] if ctx is None else CHANGE_CTX[ctx]
    step = q(d["ystep"])
    gap = q(d["gap"] if gap is None else gap)
    show = year_text if d.get("year") else num_str
    if values is None:
        # the readings stay inside a band the context could really produce: a
        # June temperature of 250 °F is arithmetically fine and nonsense on a page
        lo, hi = d["lo"], d["hi"]
        n = rng.randint(7, 11)
        v = rng.randrange(lo, hi + 1, max(1, int(step)))
        values, drift = [v], rng.choice((1, -1))
        for _ in range(n - 1):
            v += drift * rng.randrange(0, 4) * int(step) + rng.choice((-1, 0, 1)) * int(step)
            v = min(max(v, lo), hi)
            values.append(v)
        if len(set(values)) < 4:
            raise ItemError("the readings barely move")
    n = len(values)
    if n < 5:
        raise ItemError("too few readings to offer four intervals")
    x0 = (1_990 + rng.randrange(0, 20) if d.get("year") else 0) if x0 is None else x0
    xs = [q(x0) + q(gap) * i for i in range(n)]
    moves = [q(values[i + 1]) - q(values[i]) for i in range(n - 1)]
    if d.get("cooling") and any(move > 0 for move in moves):
        raise ItemError("coffee left to cool cannot warm between readings")

    if d["direction"] == "down":
        score = [-m for m in moves]
    elif d["direction"] == "up":
        score = list(moves)
    else:
        score = [abs(m) for m in moves]
    best = max(range(n - 1), key=lambda i: score[i])
    if d["direction"] != "either" and score[best] <= 0:
        raise ItemError("nothing on the chart moves in the asked direction")
    if offer is None:
        rest = [i for i in range(n - 1) if i != best]
        rng.shuffle(rest)
        offer = sorted([best] + rest[:3])
    if best not in offer or len(offer) != 4 or len(set(offer)) != 4:
        raise ItemError("the four intervals offered must include the answer, once")
    separated(score[best], [score[i] for i in offer if i != best], step)

    def label(i):
        return d["label"].format(a=show(xs[i]), b=show(xs[i + 1]))

    key = label(best)
    worst = min((i for i in offer if i != best), key=lambda i: score[i])
    wrong = [Mis("read the interval that moves furthest the other way"
                 if i == worst and score[i] < 0 else
                 "read an interval that moves the other way" if score[i] < 0 else
                 "read an interval whose reading moves less than the answer's",
                 label(i)) for i in offer if i != best]
    choices, reasons, letter = assemble_text(key, wrong, rng)
    intro = d["intro"].format(gap=num_str(gap), first=show(xs[0]), last=show(xs[-1]))
    y0, y1 = _window(values, d["ystep"], every=d["ylabel_every"])
    pts = list(zip(xs, [q(v) for v in values]))
    draw = chart_series if d["kindly"] == "series" else chart_scatter
    fig = draw(pts, x0=xs[0] - q(gap) / 2, x1=xs[-1] + q(gap) / 2, y0=y0, y1=y1,
               xstep=d["xstep"] * q(gap), ystep=d["ystep"],
               xlabel_every=d["xlabel_every"], ylabel_every=d["ylabel_every"],
               xlabel=d["xlabel"], ylabel=d["ylabel"], xgroup=not d.get("year"))
    P = dict(kind="tvdata.interval_change", values=[str(q(v)) for v in values],
             xs=[str(x) for x in xs], offer=list(offer), direction=d["direction"],
             labels=[label(i) for i in range(n - 1)])
    change = abs(moves[best])
    # An opposite-direction move can be larger in absolute size while still
    # being irrelevant to a question about the greatest rise or fall.
    misleading_distance = (d["direction"] != "either" and
                            any(abs(moves[i]) >= change for i in offer if i != best))
    if misleading_distance:
        verb = "rises" if d["direction"] == "up" else "falls"
        rationale = (f"Over that interval the reading {verb} by {num_str(change)}, "
                     f"more than over any other interval offered.")
    else:
        rationale = (f"Over that interval the reading moves by {num_str(change)}, "
                     f"further than over any other interval offered.")
    return Item("tvdata.interval_change", "reading a scatterplot", "easy", seed,
                f"{intro} {d['ask'].format(gap=num_str(gap))}", "mcq", E(0), letter,
                rationale,
                choices, reasons, list(choices), figure=fig, params=P)


# ---------------------------------------------------- the biggest of the four

EXTREME_CTX = [
    dict(intro="The line graph shows the number of graduates from the classes of {first} "
               "through {last} at a certain school who enrolled in college within 24 "
               "months of graduation.",
         ask="Of the following, which class had the {word} graduates who enrolled in "
             "college within 24 months of graduation?",
         xlabel="Graduating class year", ylabel="Graduates enrolling in college",
         most="most", least="fewest", kindly="series", year=True,
         xstep=1, xlabel_every=2, ystep=25, ylabel_every=2, lo=180, hi=300),
    dict(intro="The line graph shows the estimated number of chipmunks in a state park "
               "on April 1 of each year from {first} to {last}.",
         ask="Based on the line graph, in which year was the estimated number of "
             "chipmunks in the state park the {word}?",
         xlabel="Year", ylabel="Estimated number of chipmunks",
         most="greatest", least="least", kindly="series", year=True,
         xstep=1, xlabel_every=2, ystep=25, ylabel_every=2, lo=30, hi=190),
    dict(intro="The scatterplot shows the amount of rainfall, in millimetres, recorded at "
               "a weather station in each month of {first}.",
         ask="Based on the scatterplot, in which month was the recorded rainfall the "
             "{word}?", year=True,
         xlabel="Month", ylabel="Rainfall (millimetres)",
         most="greatest", least="least", kindly="scatter", month=True,
         xstep=1, xlabel_every=1, ystep=10, ylabel_every=2, lo=10, hi=120),
]

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]


def series_extreme(rng: random.Random, seed: int, *, ctx=None, values=None, x0=None,
                   ask="least", offer=None) -> Item:
    """Four labels are offered; one names the highest or lowest reading."""
    d = EXTREME_CTX[rng.randrange(len(EXTREME_CTX))] if ctx is None else EXTREME_CTX[ctx]
    step = q(d["ystep"])
    if values is None:
        n = rng.randint(7, 11)
        values = [rng.randrange(d["lo"], d["hi"] + 1, int(step)) for _ in range(n)]
    n = len(values)
    if n < 5:
        raise ItemError("too few readings")
    if d.get("month"):
        if n > 12:
            raise ItemError("a year has twelve months")
        x0, labels = 1, {Q(i + 1): MONTHS[i][:3] for i in range(n)}
    else:
        x0 = (1_985 + rng.randrange(0, 24)) if x0 is None else x0
        labels = None
    xs = [q(x0) + i for i in range(n)]
    vals = [q(v) for v in values]
    best = (min if ask == "least" else max)(range(n), key=lambda i: vals[i])
    if offer is None:
        rest = [i for i in range(n) if i != best]
        rng.shuffle(rest)
        offer = sorted([best] + rest[:3])
    if best not in offer or len(offer) != 4 or len(set(offer)) != 4:
        raise ItemError("the four labels offered must include the answer, once")
    separated(vals[best], [vals[i] for i in offer if i != best], step)

    def name(i):
        return MONTHS[int(xs[i]) - 1] if d.get("month") else year_text(xs[i])


    key = name(best)
    wrong = [Mis(f"gave a reading that is {'lower' if vals[i] < vals[best] else 'higher'} "
                 f"on the chart than the one the question asks for", name(i))
             for i in offer if i != best]
    choices, reasons, letter = ascending(*assemble_text(key, wrong, rng))
    y0, y1 = _window(vals, step, every=d["ylabel_every"])
    pts = list(zip(xs, vals))
    draw = chart_series if d["kindly"] == "series" else chart_scatter
    fig = draw(pts, x0=xs[0] - 1, x1=xs[-1] + 1, y0=y0, y1=y1,
               xstep=d["xstep"], ystep=step, xlabel_every=d["xlabel_every"],
               ylabel_every=d["ylabel_every"], xlabel=d["xlabel"], ylabel=d["ylabel"],
               xlabels=labels, xgroup=False)
    P = dict(kind="tvdata.series_extreme", values=[str(v) for v in vals],
             offer=list(offer), ask=ask,
             labels=[name(i) for i in range(n)])
    word = d["least"] if ask == "least" else d["most"]
    year = 1_985 + rng.randrange(0, 34) if d.get("month") else None
    intro = d["intro"].format(first=year_text(year) if year else name(0),
                              last=name(n - 1))
    return Item("tvdata.series_extreme", "reading a scatterplot", "easy", seed,
                f"{intro} {d['ask'].format(word=word)}", "mcq", E(0), letter,
                f"Of the four offered, {key} has the {word} reading, "
                f"{num_str(vals[best])}.",
                choices, reasons, list(choices), figure=fig, params=P)


# ------------------------------------------------------ a value off a curve

CURVE_CTX = [
    dict(intro="The graph shows the relationship between the speed of a particular car, "
               "in miles per hour, and its corresponding braking distance, in feet.",
         ask_one="Approximately how many feet is the car's braking distance when the car "
                 "is travelling at {x} miles per hour?",
         ask_two="Approximately how many feet greater will the car's braking distance be "
                 "when the car is travelling at {x} miles per hour than when the car is "
                 "travelling at {x2} miles per hour?",
         xlabel="Speed (miles per hour)", ylabel="Braking distance (feet)",
         title="Braking Distance versus Speed", dots=False,
         x_lo=0, x_hi=80, xstep=10, xlabel_every=2, ystep=50, ylabel_every=2,
         prec=25, a=(4, 100), c=(1, 2)),
    dict(intro="A study was done to determine a new car's stopping distance when it was "
               "travelling at different speeds. The study was done on a dry road with "
               "good surface conditions. The results are shown, along with the graph of "
               "a quadratic function that models the data.",
         ask_one="According to the model, which of the following is the best estimate "
                 "for the stopping distance, in feet, if the vehicle was travelling {x} "
                 "miles per hour?",
         ask_two="According to the model, approximately how many feet greater is the "
                 "stopping distance at {x} miles per hour than at {x2} miles per hour?",
         xlabel="Speed (miles per hour)", ylabel="Stopping distance (feet)",
         title="Vehicle Stopping Distance", dots=True,
         x_lo=0, x_hi=80, xstep=20, xlabel_every=1, ystep=25, ylabel_every=2,
         prec=10, a=(5, 100), c=(1, 2)),
    dict(intro="The graph shows the area, in square centimetres, of a square sheet of "
               "metal with a side length of x centimetres.",
         ask_one="Approximately how many square centimetres is the area of a sheet whose "
                 "side length is {x} centimetres?",
         ask_two="Approximately how many square centimetres greater is the area of a "
                 "sheet of side length {x} centimetres than one of side length {x2} "
                 "centimetres?",
         xlabel="Side length (centimetres)", ylabel="Area (square centimetres)",
         title="Area of a Square Sheet", dots=False,
         x_lo=0, x_hi=24, xstep=4, xlabel_every=1, ystep=50, ylabel_every=2,
         prec=25, a=(1, 1), c=(0, 1)),
]


def curve_read(rng: random.Random, seed: int, *, ctx=None, a=None, c=None, x=None,
               x2=None, gap=None, wrongs=None) -> Item:
    """y = ax² + cx is drawn; read one value off it, or the gap between two."""
    d = CURVE_CTX[rng.randrange(len(CURVE_CTX))] if ctx is None else CURVE_CTX[ctx]
    a = q(a) if a is not None else Q(d["a"][0] * rng.randint(1, 3), d["a"][1])
    c = q(c) if c is not None else Q(d["c"][0] * rng.randint(1, 3), d["c"][1])
    if a <= 0:
        raise ItemError("the curve must rise")
    step = q(d["ystep"])
    gap = q(gap) if gap is not None else step
    lo, hi = d["x_lo"], d["x_hi"]
    x = q(x) if x is not None else Q(rng.randrange(lo + 20, hi - 5, 5))
    f = lambda t: a * t * t + c * t
    if x2 is None and rng.random() < 0.5 and x - 20 > lo:
        x2 = x - 20
    prec = q(d["prec"])
    exact = f(x) - f(q(x2)) if x2 is not None else f(x)
    key = snap(exact, prec, strict=True)
    if key <= 0:
        raise ItemError("the reading must be positive")

    pool = {
        "one_low": ("read the curve one gridline below where it passes", E(key - gap)),
        "one_high": ("read the curve one gridline above where it passes", E(key + gap)),
        "two_high": ("read the curve two gridlines above where it passes", E(key + 2 * gap)),
        "double": ("doubled the reading", E(2 * key)),
        "half": ("halved the reading", E(key / 2)),
        "x_value": ("gave the speed the question supplies, not the reading off the "
                    "vertical axis", E(x) if q(x) != key else None),
        "sum": ("added the two readings instead of subtracting them",
                E(snap(f(x) + f(q(x2)), gap)) if x2 is not None else None),
        "one_only": ("read the curve at only one of the two speeds",
                     E(snap(f(x), gap)) if x2 is not None else None),
    }
    order = ["one_low", "one_high", "two_high", "double", "half", "sum", "one_only",
             "x_value"]
    mistakes = pick(pool, order, wrongs)
    choices, latex, reasons, letter = assemble_num(key, mistakes, rng)
    vals = [q(v.replace("−", "-").replace(",", "")) for v in choices]
    separated(key, [v for v in vals if v != key], step)
    closest_guard(exact, key, [v for v in vals if v != key])

    # The chart is drawn around the part of the curve the question is about:
    # like the source, the curve runs off the top rather than the window being
    # stretched to hold a value nobody is asked to read.
    reach = max([key, f(q(x))] + ([f(q(x2))] if x2 is not None else []))
    y0, y1 = _window([0, reach * Q(3, 2)], step, every=d["ylabel_every"])
    y1 = min(y1, _window([0, f(q(hi))], step, every=d["ylabel_every"])[1])
    right = q(hi)
    while right > q(lo) + q(d["xstep"]) and f(right - q(d["xstep"])) > y1:
        right -= q(d["xstep"])
    if right <= max(q(x), q(x2) if x2 is not None else q(lo)):
        raise ItemError("the reading sits outside the part of the curve drawn")
    dots = []
    if d["dots"]:
        dots = [(t, f(t)) for t in range(lo + 10, int(right), 10) if f(t) <= y1]
    fig = chart_curve(f, x0=lo, x1=right, y0=y0, y1=y1, xstep=d["xstep"], ystep=step,
                       xlabel_every=d["xlabel_every"], ylabel_every=d["ylabel_every"],
                       xlabel=d["xlabel"], ylabel=d["ylabel"], title=d["title"],
                       points=dots)
    ask = (d["ask_two"].format(x=num_str(x), x2=num_str(q(x2))) if x2 is not None
           else d["ask_one"].format(x=num_str(x)))
    P = dict(kind="tvdata.curve_read", a=str(a), c=str(c), x=str(q(x)),
             x2=None if x2 is None else str(q(x2)), gap=str(prec))
    why = (f"The curve is at about {num_str(f(x), 0)} at {num_str(x)} and about "
           f"{num_str(f(q(x2)), 0)} at {num_str(q(x2))}." if x2 is not None
           else f"The curve passes {num_str(x)} on the horizontal axis at about "
                f"{num_str(key)}.")
    return Item("tvdata.curve_read", "reading a model", "easy", seed,
                f"{d['intro']} {ask}", "mcq", E(key), letter, why,
                choices, reasons, latex, figure=fig, params=P)


# ---------------------------------------------- average rate between two dots

RATE_CTX = [
    dict(intro="The scatterplot shows the relationship between the length of time y, in "
               "hours, a certain bird spent in flight and the number of days after "
               "January 11, x.",
         ask="What is the average rate of change, in hours per day, of the length of "
             "time the bird spent in flight on January {d1} to the length of time the "
             "bird spent in flight on January {d2}?",
         xlabel="Days after January 11", ylabel="Length of time (hours)",
         xstep=1, xlabel_every=2, ystep=2, ylabel_every=1, base=11,
         y_lo=5, y_hi=16),
    dict(intro="The scatterplot shows the height, in centimetres, of a seedling measured "
               "on each of the first several days after it was planted.",
         ask="What is the average rate of change, in centimetres per day, of the height "
             "of the seedling from day {a} to day {b}?",
         xlabel="Days after planting", ylabel="Height (centimetres)",
         xstep=1, xlabel_every=2, ystep=2, ylabel_every=1, base=None,
         y_lo=4, y_hi=26),
]


def rate_of_change(rng: random.Random, seed: int, *, ctx=None, ys=None, i=None,
                   j=None) -> Item:
    """The average rate of change between two plotted points, entered as a value."""
    d = RATE_CTX[rng.randrange(len(RATE_CTX))] if ctx is None else RATE_CTX[ctx]
    n = 10 if ys is None else len(ys)
    if ys is None:
        ys = [Q(rng.randrange(d["y_lo"] * 2, d["y_hi"] * 2 + 1), 2) for _ in range(n)]
    ys = [q(v) for v in ys]
    xs = [Q(k + 1) for k in range(n)]
    if i is None or j is None:
        i = rng.randrange(0, n - 2)
        j = rng.randrange(i + 1, min(i + 5, n))
    if not 0 <= i < j < n:
        raise ItemError("the two points must be distinct and in order")
    rate = (ys[j] - ys[i]) / (xs[j] - xs[i])
    if rate == 0:
        raise ItemError("a rate of change of zero is not a grid-in answer")
    if rate.denominator > 4 or abs(rate) > 40:
        raise ItemError("that rate is not a value this test would ask a student to enter")
    y0, y1 = _window(ys, d["ystep"], every=d["ylabel_every"])
    fig = chart_scatter(list(zip(xs, ys)), x0=0, x1=xs[-1] + 1, y0=y0, y1=y1,
                         xstep=d["xstep"], ystep=d["ystep"],
                         xlabel_every=d["xlabel_every"], ylabel_every=d["ylabel_every"],
                         xlabel=d["xlabel"], ylabel=d["ylabel"])
    if d["base"] is not None:
        ask = d["ask"].format(d1=d["base"] + int(xs[i]), d2=d["base"] + int(xs[j]))
    else:
        ask = d["ask"].format(a=num_str(xs[i]), b=num_str(xs[j]))
    P = dict(kind="tvdata.rate_of_change", ys=[str(v) for v in ys], i=i, j=j)
    return Item("tvdata.rate_of_change", "reading a scatterplot", "hard", seed,
                f"{d['intro']} {ask}", "spr", E(rate), E(rate).gridin(),
                f"The two points are {num_str(abs(ys[j] - ys[i]))} apart on the "
                f"vertical axis over {plural(int(xs[j] - xs[i]), 'day')}.",
                figure=fig, params=P)
