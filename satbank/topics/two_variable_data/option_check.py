"""Read the four printed options back, and the picture, and check only one is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct, and it never looks at the figure at all: the audit
re-derives the answer from `item.params`, which is the same set of numbers the
template drew the chart from. So two whole classes of defect pass every gate the
engine has --

* an item with two true statements, or two equations that both fit, and
* an item whose picture has drifted away from the answer it is supposed to carry.

This script closes both. It imports no template, no renderer and no solver:
`generate` gives it the finished item exactly as a student receives it, and
everything after that comes from the printed stem, the printed options and the
SVG's own pixels.

    PYTHONPATH=. python3 satbank/topics/two_variable_data/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 800 --template tvdata.fit_slope
    PYTHONPATH=. python3 .../option_check.py --prove      # show the checks can fail

Three things it does that a checker built on the parameters could not:

* **The scale comes from the printed gridline labels.** `chart()` pairs every
  labelled gridline with its pixel position and fits the pixels-to-data map from
  those pairs alone, then verifies the remaining labels against it. A renderer
  that mislabelled an axis would be caught here and nowhere else.
* **The line of best fit is refitted from the plotted dots.** A "line of best
  fit" item is answerable only if the drawn scatter really has the drawn line as
  its least-squares line, so the dots are recovered from the SVG and refitted.
* **The gridline rule is enforced against the drawn gridlines.** Two options
  closer together than the chart's own gridline spacing cannot be separated by
  any reader, whatever the parameters said.

Exits non-zero on the first kind of defect it finds, and prints the item.
"""

from __future__ import annotations

import argparse
import re
import sys
from fractions import Fraction as F

from satbank.item import ItemError
from satbank.registry import generate

MINUS = "−"
# Every pixel in the SVG is written to two decimal places, so a value recovered
# from the picture is out by a few parts in ten thousand. A gap the template
# made exactly one gridline wide therefore measures a whisker under one, and
# the comparisons below leave it that whisker.
SLACK = 0.99


class Unreadable(Exception):
    """The printed item is not something this reader understands."""


# ------------------------------------------------------- printed text -> number

def num(text) -> float:
    t = str(text).replace(MINUS, "-").replace(",", "").strip()
    t = t.replace("°F", "").replace("°C", "").replace("%", "").replace("$", "")
    t = t.strip()
    if not t:
        raise Unreadable(f"{text!r} is not a number")
    try:
        if "/" in t:
            a, b = t.split("/", 1)
            return float(a) / float(b)
        return float(t)
    except ValueError as exc:
        raise Unreadable(f"{text!r} is not a number") from exc


def numbers(text: str) -> list:
    return [num(t) for t in re.findall(r"-?−?[\d,]+(?:\.\d+)?", str(text))]


def keyed(item) -> int:
    return "ABCD".index(item.answer)


def option_numbers(item) -> list:
    return [num(c) for c in item.choices]


# ------------------------------------------------------------ SVG -> geometry

GRID = re.compile(r'<line class="gr" x1="([-\d.]+)" y1="([-\d.]+)" '
                  r'x2="([-\d.]+)" y2="([-\d.]+)"/>')
XLAB = re.compile(r'<text class="lb xl" x="([-\d.]+)" y="[-\d.]+" '
                  r'text-anchor="middle">([^<]*)</text>')
YLAB = re.compile(r'<text class="lb yl" x="[-\d.]+" y="([-\d.]+)" '
                  r'text-anchor="end">([^<]*)</text>')
DOT = re.compile(r'<circle class="pt" cx="([-\d.]+)" cy="([-\d.]+)" r="[-\d.]+"/>')
BEST = re.compile(r'<line class="bf" x1="([-\d.]+)" y1="([-\d.]+)" '
                  r'x2="([-\d.]+)" y2="([-\d.]+)"/>')
POLY = re.compile(r'<polyline class="(cv|sr)" points="([^"]*)"/>')

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]


def _affine(pairs, what: str):
    """The pixels-to-data map through the labelled gridlines, as a function."""
    pairs = sorted(pairs)
    if len(pairs) < 2:
        raise Unreadable(f"only {len(pairs)} labelled gridlines on the {what} axis")
    (p0, v0), (p1, v1) = pairs[0], pairs[-1]
    if p1 == p0:
        raise Unreadable(f"two {what} labels at the same place")
    k = (v1 - v0) / (p1 - p0)

    def f(p):
        return v0 + k * (p - p0)

    # every pixel in the SVG is rounded to two decimal places, so a recovered
    # value is out by a thousandth of the axis at worst; anything larger is a
    # mislabelled axis rather than a rounding artefact
    tol = abs(v1 - v0) / 1_000
    for p, v in pairs:
        if abs(f(p) - v) > tol:
            raise Unreadable(f"the {what} axis is not evenly labelled: {p} reads "
                             f"{f(p)} but is printed {v}")
    return f, abs(k)


def chart(svg: str) -> dict:
    """Everything a reader with a ruler could take off the picture.

    Nothing here consults the item's parameters. The gridlines give the scale,
    the printed labels give the values, and the map between them is fitted and
    then checked against every label it was not fitted through.
    """
    if not svg:
        raise Unreadable("the item carries no figure")
    grid = [tuple(float(v) for v in g) for g in GRID.findall(svg)]
    verticals = sorted({g[0] for g in grid if g[0] == g[2]})
    horizontals = sorted({g[1] for g in grid if g[1] == g[3]})
    xlabels = [(float(px), t) for px, t in XLAB.findall(svg)]
    ylabels = [(float(py) - 4, num(t)) for py, t in YLAB.findall(svg)]

    numeric = []
    for px, t in xlabels:
        t = t.strip()
        short = [i for i, m in enumerate(MONTHS) if m == t or m[:3] == t]
        if short:
            numeric.append((px, float(short[0] + 1)))
        else:
            numeric.append((px, num(t)))
    X, xk = _affine(numeric, "horizontal")
    Y, yk = _affine(ylabels, "vertical")

    def gaps(vals):
        # pixels are written to two decimal places, so evenly spaced gridlines
        # can still differ by a hundredth of a pixel
        d = [b - a for a, b in zip(vals, vals[1:])]
        if max(d) - min(d) > 0.02:
            raise Unreadable(f"the gridlines are not evenly spaced: "
                             f"{min(d):.4g} to {max(d):.4g}")
        return sum(d) / len(d)

    out = {"X": X, "Y": Y,
           "xstep": gaps(verticals) * xk if len(verticals) > 1 else None,
           "ystep": gaps(horizontals) * yk if len(horizontals) > 1 else None,
           "points": sorted((X(float(a)), Y(float(b))) for a, b in DOT.findall(svg)),
           "line": None, "curve": None, "series": None}
    drawn = BEST.findall(svg)
    if len(drawn) > 1:
        raise Unreadable(f"{len(drawn)} lines of best fit drawn")
    if drawn:
        x1, y1, x2, y2 = (float(v) for v in drawn[0])
        ax1, ay1, ax2, ay2 = X(x1), Y(y1), X(x2), Y(y2)
        if ax1 == ax2:
            raise Unreadable("the drawn line of best fit is vertical")
        m = (ay2 - ay1) / (ax2 - ax1)
        out["line"] = (m, ay1 - m * ax1)
        out["line_span"] = abs(ax2 - ax1)
    for cls, body in POLY.findall(svg):
        pts = []
        for pair in body.split():
            a, b = pair.split(",")
            pts.append((X(float(a)), Y(float(b))))
        out["curve" if cls == "cv" else "series"] = pts
    return out


def regression(points):
    """Least squares by the normal equations, on the recovered dots."""
    n = len(points)
    if n < 3:
        raise Unreadable("too few plotted points to fit a line")
    sx = sum(p[0] for p in points)
    sy = sum(p[1] for p in points)
    sxy = sum(p[0] * p[1] for p in points)
    sxx = sum(p[0] * p[0] for p in points)
    den = n * sxx - sx * sx
    if den == 0:
        raise Unreadable("every plotted point has the same x-value")
    m = (n * sxy - sx * sy) / den
    return m, (sy - m * sx) / n


def agrees(fit, drawn, xs, span):
    """The refitted line and the drawn line must be the same line, to the pixel."""
    lo, hi = min(xs), max(xs)
    off = max(abs((fit[0] - drawn[0]) * x + (fit[1] - drawn[1])) for x in (lo, hi))
    if off > span / 200:
        raise AssertionError(
            f"the drawn line y = {drawn[0]:.4g}x + {drawn[1]:.4g} is not the line of "
            f"best fit of the drawn points, which is y = {fit[0]:.4g}x + {fit[1]:.4g}")


def unique_nearest(item, value, what: str, step=None):
    """Exactly one printed option is nearest `value`, and it is the keyed one.

    A grid-in has no options, so what it prints has to *be* the value, to
    whatever the stem said to round it to -- never more than half a gridline
    away from what the picture shows.
    """
    if item.fmt == "spr":
        got = num(item.answer)
        room = (step or 0) / 2 + 1e-6
        if abs(got - value) > room:
            raise AssertionError(f"{what} is {value:.6g}, the item answers {got}")
        return what
    vals = option_numbers(item)
    d = [abs(v - value) for v in vals]
    best = min(d)
    if sum(1 for v in d if v <= best + 1e-9) != 1:
        raise AssertionError(f"{what} is {value:.6g}, which is equally close to two of "
                             f"{item.choices}")
    if d[keyed(item)] > best + 1e-9:
        raise AssertionError(f"{what} is {value:.6g}, nearest {item.choices[d.index(best)]!r}, "
                             f"but the key is {item.choices[keyed(item)]!r}")
    if step:
        k = vals[keyed(item)]
        for i, v in enumerate(vals):
            if i != keyed(item) and abs(v - k) < step * SLACK:
                raise AssertionError(
                    f"the options {item.choices[keyed(item)]!r} and {item.choices[i]!r} "
                    f"are {abs(v - k):.6g} apart on a chart gridlined every {step:.6g}")
    return what


def at(points, x):
    """The plotted y at x, when exactly one point sits there.

    How near counts as "there" comes from the picture: half the closest gap
    between two plotted points, so a reading is only claimed when the reader
    could not have taken the neighbouring dot instead.
    """
    xs = sorted({p[0] for p in points})
    if len(xs) < 2:
        raise Unreadable("a chart with a single column of points")
    near = min(b - a for a, b in zip(xs, xs[1:])) / 2
    hits = [p for p in points if abs(p[0] - x) <= near]
    if len(hits) != 1:
        raise AssertionError(f"{len(hits)} plotted points within {near:.4g} of "
                             f"x = {x:.6g}")
    return hits[0][1]


def on_curve(curve, x):
    for (xa, ya), (xb, yb) in zip(curve, curve[1:]):
        if xa - 1e-9 <= x <= xb + 1e-9:
            if xb == xa:
                return ya
            return ya + (yb - ya) * (x - xa) / (xb - xa)
    raise Unreadable(f"the drawn curve does not reach x = {x:.6g}")


# ------------------------------------------------------- pulling x out of a stem

def one(stem: str, patterns) -> float:
    for p in patterns:
        m = re.search(p, stem)
        if m:
            return num(m.group(1))
    raise Unreadable(f"no x-value in {stem[:120]!r}")


PREDICT_X = [r"elevation of ([\d,.]+) feet", r"about ([\d,.]+) AU",
             r"[Aa]t x = ([\d,.]+),", r"temperature of ([\d,.]+)°C",
             r"concentration of ([\d,.]+)%"]
POINT_X = [r"the ([\d,.]+)-pound", r"during the (\d+)(?:st|nd|rd|th) growing season",
           r"with ([\d,]+) visitors", r"lasted ([\d,]+) minutes"]
RESID_X = [r"the data point with x = ([\d,.]+)"]
CURVE_X = r"([\d,.]+) (?:miles per hour|centimetres)"


# --------------------------------------------------------------- the checks

def check_point_read(item) -> str:
    c = chart(item.figure)
    x = one(item.stem, POINT_X)
    y = at(c["points"], x)
    # the reader finds the dot by its x-value, so no other dot may be within
    # half a gridline of it along the horizontal axis
    near = sorted(c["points"], key=lambda p: abs(p[0] - x))
    if len(near) > 1 and abs(near[1][0] - x) < c["xstep"] * SLACK / 2:
        raise AssertionError(f"another plotted point sits within half a gridline of "
                             f"x = {x:.6g}")
    return unique_nearest(item, y, "the plotted reading", c["ystep"])


def check_predict(item) -> str:
    c = chart(item.figure)
    pts = c["points"]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    span = max(ys) - min(ys)
    fit = regression(pts)
    if c["line"] is not None:
        agrees(fit, c["line"], xs, span)
        fit = c["line"]
    x = one(item.stem, PREDICT_X)
    return unique_nearest(item, fit[0] * x + fit[1], "the line's value", c["ystep"])


def check_fit_slope(item) -> str:
    c = chart(item.figure)
    if c["line"] is None:
        raise AssertionError("a slope question with no line drawn")
    pts = c["points"]
    ys = [p[1] for p in pts]
    agrees(regression(pts), c["line"], [p[0] for p in pts], max(ys) - min(ys))
    # the finest change of slope a reader could see is the one that moves the
    # drawn line by a single gridline over the length it is actually drawn
    step = c["ystep"] / c["line_span"]
    return unique_nearest(item, c["line"][0], "the drawn slope", step)


LHS = re.compile(r"^\s*(\w+)\s*=\s*(.+)$")
TERM = re.compile(r"([+−-]?)\s*([\d.,]*)\s*([a-z]?)")


def read_line(text: str) -> tuple:
    """A printed equation as (slope, intercept), read from the string itself."""
    m = LHS.match(text)
    if m is None:
        raise Unreadable(f"cannot read {text!r} as an equation")
    body = m.group(2).replace(" ", "").replace(",", "")
    slope = const = 0.0
    i, names = 0, set()
    while i < len(body):
        t = TERM.match(body, i)
        if t is None or t.end() == i:
            raise Unreadable(f"cannot read {text!r} at {body[i:]!r}")
        sign, digits, name = t.groups()
        v = float(digits) if digits else 1.0
        if sign in ("-", MINUS):
            v = -v
        if name:
            names.add(name)
            slope += v
        else:
            const += v
        i = t.end()
    if len(names) > 1:
        raise Unreadable(f"{text!r} mentions more than one variable")
    return slope, const


def check_fit_equation(item) -> str:
    c = chart(item.figure)
    pts = c["points"]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    span = max(ys) - min(ys)
    fit = regression(pts)
    if c["line"] is not None:
        agrees(fit, c["line"], xs, span)
    good = []
    for text in item.choices:
        m, b = read_line(text)
        off = max(abs((m - fit[0]) * x + (b - fit[1])) for x in (min(xs), max(xs)))
        good.append(off <= span / 5)
    if good.count(True) != 1:
        raise AssertionError(f"{good.count(True)} of the four equations fit the drawn "
                             f"points, whose line of best fit is "
                             f"y = {fit[0]:.4g}x + {fit[1]:.4g}")
    if not good[keyed(item)]:
        raise AssertionError("the keyed equation is not the one that fits")
    return "one equation fits the dots"


def check_residual(item) -> str:
    c = chart(item.figure)
    pts = c["points"]
    if c["line"] is None:
        raise AssertionError("a residual question with no line drawn")
    agrees(regression(pts), c["line"], [p[0] for p in pts],
           max(p[1] for p in pts) - min(p[1] for p in pts))
    m, b = c["line"]
    if "greatest percent" in item.stem:
        top = max(p[1] for p in pts)
        chosen = [p for p in pts if abs(p[1] - top) < c["ystep"] / 4]
        if len(chosen) != 1:
            raise AssertionError("two plotted points tie for the greatest reading")
        p = chosen[0]
    else:
        x = one(item.stem, RESID_X)
        p = (x, at(pts, x))
    return unique_nearest(item, abs(p[1] - (m * p[0] + b)), "the gap to the line",
                          c["ystep"])


def check_curve_read(item) -> str:
    c = chart(item.figure)
    if not c["curve"]:
        raise AssertionError("a curve question with no curve drawn")
    xs = [num(t) for t in re.findall(CURVE_X, item.stem)]
    if not xs:
        raise Unreadable(f"no speed in {item.stem[:120]!r}")
    if "greater" in item.stem:
        if len(xs) != 2:
            raise Unreadable("a difference needs two readings")
        value = on_curve(c["curve"], xs[0]) - on_curve(c["curve"], xs[1])
    else:
        value = on_curve(c["curve"], xs[0])
    return unique_nearest(item, value, "the curve's value", c["ystep"])


def _label_xs(text: str) -> list:
    if text.strip() in MONTHS:
        return [float(MONTHS.index(text.strip()) + 1)]
    return numbers(text)


def check_interval(item) -> str:
    c = chart(item.figure)
    pts = c["points"] if c["points"] else c["series"]
    if not pts:
        raise AssertionError("no readings drawn")
    if "greatest average rate" in item.stem or "decrease" in item.stem:
        score = lambda d: -d
    elif "increase" in item.stem:
        score = lambda d: d
    else:
        score = abs
    got = []
    for text in item.choices:
        xs = _label_xs(text)
        if len(xs) != 2:
            raise Unreadable(f"cannot read an interval out of {text!r}")
        got.append(score(at(pts, xs[1]) - at(pts, xs[0])))
    best = max(got)
    if sum(1 for v in got if best - v < c["ystep"] * SLACK) != 1:
        raise AssertionError(f"two offered intervals are within one gridline of the "
                             f"biggest move: {got}")
    if got[keyed(item)] < best - 1e-9:
        raise AssertionError(f"the keyed interval moves {got[keyed(item)]:.6g}, not the "
                             f"biggest {best:.6g}")
    return "one interval moves furthest"


def check_extreme(item) -> str:
    c = chart(item.figure)
    pts = c["points"] if c["points"] else c["series"]
    want_min = "fewest" in item.stem or "least" in item.stem
    got = []
    for text in item.choices:
        xs = _label_xs(text)
        if len(xs) != 1:
            raise Unreadable(f"cannot read a label out of {text!r}")
        got.append(at(pts, xs[0]))
    best = min(got) if want_min else max(got)
    close = [v for v in got if abs(v - best) < c["ystep"] * SLACK]
    if len(close) != 1:
        raise AssertionError(f"two offered readings are within one gridline of the "
                             f"{'least' if want_min else 'greatest'}: {got}")
    if abs(got[keyed(item)] - best) > 1e-9:
        raise AssertionError(f"the keyed reading is {got[keyed(item)]:.6g}, not {best:.6g}")
    return "one reading is the extreme"


def check_rate(item) -> str:
    c = chart(item.figure)
    pts = c["points"]
    base = re.search(r"days after January (\d+)", item.stem)
    days = re.findall(r"in flight on January (\d+)", item.stem)
    if base and len(days) == 2:
        xs = [float(d) - float(base.group(1)) for d in days]
    else:
        m = re.search(r"from day (\d+) to day (\d+)", item.stem)
        if m is None:
            raise Unreadable(f"no pair of days in {item.stem[:120]!r}")
        xs = [float(m.group(1)), float(m.group(2))]
    y0 = at(pts, xs[0])
    y1 = at(pts, xs[1])
    want = (y1 - y0) / (xs[1] - xs[0])
    got = num(item.answer)
    if abs(got - want) > max(1e-6, c["ystep"] * 0.02):
        raise AssertionError(f"the chart gives a rate of {want:.6g}, the item answers {got}")
    return "the rate matches the dots"


def check_slope_scaled(item) -> str:
    m = re.search(r"slope of approximately (−?-?[\d.,]+)", item.stem)
    k = re.search(r"for each ([\d.,]+)°[FC] increase", item.stem)
    if not m or not k:
        raise Unreadable(f"no slope and step in {item.stem[:140]!r}")
    want = abs(num(m.group(1))) * num(k.group(1))
    got = num(item.answer)
    if abs(got - want) > 1e-9:
        raise AssertionError(f"a slope of {m.group(1)} over {k.group(1)} is {want:.6g}, "
                             f"the item answers {got}")
    c = chart(item.figure)
    drawn = c["line"]
    if drawn is None:
        raise AssertionError("no line of best fit drawn")
    agrees(regression(c["points"]), drawn, [p[0] for p in c["points"]],
           max(p[1] for p in c["points"]) - min(p[1] for p in c["points"]))
    if abs(abs(drawn[0]) - abs(num(m.group(1)))) > abs(num(m.group(1))) * 0.02:
        raise AssertionError(f"the stem says the slope is {m.group(1)} but the drawn "
                             f"line has slope {drawn[0]:.6g}")
    return "the stated slope is the drawn one"


UP = re.compile(r"As the (.+) increases, the (.+) tends to increase\.")
DOWN = re.compile(r"As the (.+) increases, the (.+) tends to decrease\.")
XDOWN_UP = re.compile(r"As the (.+) decreases, the (.+) tends to increase\.")
XDOWN_DOWN = re.compile(r"As the (.+) decreases, the (.+) tends to decrease\.")


def check_association(item) -> str:
    c = chart(item.figure)
    m, _ = regression(c["points"])
    if c["line"] is not None:
        agrees((m, regression(c["points"])[1]), c["line"], [p[0] for p in c["points"]],
               max(p[1] for p in c["points"]) - min(p[1] for p in c["points"]))
    true = []
    for text in item.choices:
        if text.startswith("There is no association"):
            ok = False
        elif UP.match(text) or XDOWN_DOWN.match(text):
            ok = m > 0
        elif DOWN.match(text) or XDOWN_UP.match(text):
            ok = m < 0
        else:
            raise Unreadable(f"cannot read the statement {text!r}")
        true.append(ok)
    if true.count(True) != 1:
        raise AssertionError(f"{true.count(True)} of the four sentences are true of a "
                             f"line of slope {m:.4g}")
    if not true[keyed(item)]:
        raise AssertionError("the keyed sentence is not the true one")
    return "one sentence describes the direction"


EACH = re.compile(r"^Each year between \d+ and \d+, the average increase in .+ was "
                  r"([\d.]+) \w+\.$")
DECADE = re.compile(r"^Every 10 years between \d+ and \d+, the average increase in .+ "
                    r"was ([\d.]+) \w+\.$")


def check_interpret(item) -> str:
    m = re.search(r"its equation is y = ([\d.]+)x − ([\d.]+)", item.stem)
    if m is None:
        raise Unreadable(f"no equation in {item.stem[:160]!r}")
    slope = float(m.group(1))
    true = []
    for text in item.choices:
        e, d = EACH.match(text), DECADE.match(text)
        if e:
            true.append(abs(float(e.group(1)) - slope) < 1e-9)
        elif d:
            true.append(abs(float(d.group(1)) - 10 * slope) < 1e-9)
        else:
            raise Unreadable(f"cannot read the statement {text!r}")
    if true.count(True) != 1:
        raise AssertionError(f"{true.count(True)} of the four sentences are true of a "
                             f"slope of {slope}")
    if not true[keyed(item)]:
        raise AssertionError("the keyed sentence is not the true one")
    # the drawn line has to be the line the stem writes down
    c = chart(item.figure)
    if c["line"] is None or abs(c["line"][0] - slope) > slope * 0.02:
        raise AssertionError(f"the stem writes a slope of {slope} but the drawn line "
                             f"has slope {c['line'] and c['line'][0]}")
    return "one sentence reads the slope right"


SHAPES = {"A linear model with a positive slope": ("linear", "up"),
          "A linear model with a negative slope": ("linear", "down"),
          "An exponential growth model": ("exponential", "up"),
          "An exponential decay model": ("exponential", "down")}

FALLING = ("remaining", "burns down", "loses", "depreciates", "fewer")


def check_model_type(item) -> str:
    stem = item.stem
    kind = "linear" if "constant rate" in stem or "constant speed" in stem \
        else "exponential"
    if "%" in stem or "doubles" in stem or "compounded" in stem:
        kind = "exponential"
    down = any(w in stem for w in FALLING)
    want = (kind, "down" if down else "up")
    got = [SHAPES.get(c) for c in item.choices]
    if None in got:
        raise Unreadable(f"an option this reader does not know: {item.choices}")
    if len(set(got)) != 4:
        raise AssertionError("the four options do not name four different shapes")
    if got[keyed(item)] != want:
        raise AssertionError(f"the scenario is {want}, the key says {got[keyed(item)]}")
    return "one shape matches the scenario"


WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen "
    "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}
WORDS.update({"twenty-one": 21, "twenty-two": 22, "twenty-three": 23,
              "twenty-four": 24, "twenty-five": 25})


def _minutes(text: str, after: str) -> float:
    tail = text.split(after, 1)[1].strip().split(" ")[0]
    return float(WORDS[tail]) if tail in WORDS else num(tail)


def check_graph_statement(item) -> str:
    c = chart(item.figure)
    pts = c["series"]
    if not pts:
        raise AssertionError("no line graph drawn")
    ts = [p[0] for p in pts]
    vs = [p[1] for p in pts]
    eps = c["ystep"] / 4
    dt = c["xstep"] / 1_000
    total = ts[-1]
    up = sum(ts[i + 1] - ts[i] for i in range(len(pts) - 1) if vs[i + 1] > vs[i] + eps)
    down = sum(ts[i + 1] - ts[i] for i in range(len(pts) - 1) if vs[i + 1] < vs[i] - eps)
    top = max(vs)
    t_top = ts[vs.index(top)]
    false = []
    for text in item.choices:
        if "constant speed for" in text:
            want = _minutes(text, "constant speed for")
            ok = any(abs(ts[i + 1] - ts[i] - want) < dt and abs(vs[i + 1] - vs[i]) < eps
                     for i in range(len(pts) - 1))
        elif "longer period of time" in text:
            ok = up > down + 1e-9
        elif "decreased at a constant rate during the last" in text:
            want = _minutes(text, "during the last")
            ok = abs(total - ts[-2] - want) < dt and vs[-1] < vs[-2] - eps
        elif "reached its maximum during the last" in text:
            want = _minutes(text, "during the last")
            ok = total - t_top <= want + dt
        else:
            raise Unreadable(f"cannot read the statement {text!r}")
        if not ok:
            false.append(text)
    if len(false) != 1:
        raise AssertionError(f"{len(false)} of the four statements are untrue")
    if false[0] != item.choices[keyed(item)]:
        raise AssertionError("the keyed statement is not the untrue one")
    return "one statement is untrue"


QUAD = re.compile(r"([+−-]?)([\d.]*)(x²|x|)")


def read_quad(text: str) -> tuple:
    m = LHS.match(text)
    if m is None:
        raise Unreadable(f"cannot read {text!r} as an equation")
    body = m.group(2).replace(" ", "").replace(",", "")
    a = b = k = 0.0
    i, seen = 0, False
    while i < len(body):
        t = QUAD.match(body, i)
        if t is None or t.end() == i:
            raise Unreadable(f"cannot read {text!r} at {body[i:]!r}")
        sign, digits, tail = t.groups()
        v = float(digits) if digits else 1.0
        if sign in ("-", MINUS):
            v = -v
        if tail == "x²":
            a += v
        elif tail == "x":
            b += v
        else:
            k += v
        seen = True
        i = t.end()
    if not seen:
        raise Unreadable(f"cannot read {text!r} as a quadratic")
    return a, b, k


def check_best_model(item) -> str:
    c = chart(item.figure)
    pts = c["points"]
    ys = [p[1] for p in pts]
    span = max(ys) - min(ys)
    good = []
    for text in item.choices:
        a, b, k = read_quad(text)
        good.append(max(abs(a * x * x + b * x + k - y) for x, y in pts) <= span / 6)
    if good.count(True) != 1:
        raise AssertionError(f"{good.count(True)} of the four models fit the drawn dots")
    if not good[keyed(item)]:
        raise AssertionError("the keyed model is not the one that fits")
    return "one model fits the dots"


GROWTH = re.compile(r"the values of (\d+)ˣ and (.+) for (\w) > 0")


def check_growth(item) -> str:
    m = GROWTH.search(item.stem)
    if m is None:
        raise Unreadable(f"cannot read {item.stem[:140]!r}")
    base = float(m.group(1))
    slope, const = read_line("y = " + m.group(2))
    var = m.group(3)
    signs = []
    for i in range(1, 2_001):
        x = i / 40
        d = base ** x - (slope * x + const)
        if d != 0:
            signs.append(d > 0)
    if not any(signs):
        shape = "less"
    elif all(signs):
        shape = "greater"
    else:
        flips = sum(1 for a, b in zip(signs, signs[1:]) if a != b)
        if flips != 1 or signs[0]:
            raise AssertionError("the two graphs cross in a way no option describes")
        shape = "cross"
    got = []
    for text in item.choices:
        if text.startswith(f"For all {var} > 0"):
            got.append("less" if "<" in text else "greater")
        elif text.startswith("There is a constant c"):
            first = text.split(", but if")[0].split("then")[1]
            got.append("cross" if "<" in first else "cross_back")
        else:
            raise Unreadable(f"cannot read the statement {text!r}")
    if len(set(got)) != 4:
        raise AssertionError("the four options do not make four different claims")
    if got.count(shape) != 1 or got[keyed(item)] != shape:
        raise AssertionError(f"the truth is {shape!r} but the key claims "
                             f"{got[keyed(item)]!r}")
    return "one claim about the crossing"


def check_invest(item) -> str:
    if not item.table:
        raise AssertionError("no table of investments")
    rows = {r[0]: r[1:] for r in item.table[1:]}
    if len(rows) != 2:
        raise Unreadable("a table with something other than two accounts")
    (a_name, a_row), (b_name, b_row) = list(rows.items())
    rate = num(a_row[1].split("%")[0]) / 100
    principal = num(a_row[0])
    fee = num(b_row[1].split(" ")[0])
    first = principal * rate
    if first == fee:
        raise AssertionError("the two accounts earn the same in the first year")
    always_more = f"{a_name} always earns more money per year than {b_name}."
    later_more = (f"{a_name} earns less money per year than {b_name} at first but "
                  f"eventually earns more money per year.")
    want = always_more if first > fee else later_more
    if item.choices.count(want) != 1:
        raise AssertionError(f"the true sentence {want!r} is not among the four once")
    if item.choices[keyed(item)] != want:
        raise AssertionError(f"the key is {item.choices[keyed(item)]!r}, the truth is "
                             f"{want!r}")
    return "one sentence about the two accounts"


PAIRS = re.compile(r"x = (.+); y = (.+)")


def check_nonlinear(item) -> str:
    curved = []
    for text in item.choices:
        m = PAIRS.match(text)
        if m is None:
            raise Unreadable(f"cannot read {text!r} as a table")
        xs = numbers(m.group(1))
        ys = numbers(m.group(2))
        if len(xs) != len(ys) or len(xs) < 3:
            raise Unreadable(f"a table with mismatched rows: {text!r}")
        slopes = {round((ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]), 9)
                  for i in range(len(xs) - 1)}
        if len(slopes) != 1:
            curved.append(text)
    if len(curved) != 1:
        raise AssertionError(f"{len(curved)} of the four tables are nonlinear")
    if curved[0] != item.choices[keyed(item)]:
        raise AssertionError("the keyed table is not the nonlinear one")
    return "one table is not linear"


CHECKS = {
    "tvdata.point_read": check_point_read,
    "tvdata.predict_from_line": check_predict,
    "tvdata.fit_slope": check_fit_slope,
    "tvdata.fit_equation": check_fit_equation,
    "tvdata.residual": check_residual,
    "tvdata.curve_read": check_curve_read,
    "tvdata.interval_change": check_interval,
    "tvdata.series_extreme": check_extreme,
    "tvdata.rate_of_change": check_rate,
    "tvdata.slope_scaled": check_slope_scaled,
    "tvdata.association": check_association,
    "tvdata.interpret_slope": check_interpret,
    "tvdata.model_type": check_model_type,
    "tvdata.graph_statement": check_graph_statement,
    "tvdata.best_model": check_best_model,
    "tvdata.growth_compare": check_growth,
    "tvdata.invest_compare": check_invest,
    "tvdata.nonlinear_table": check_nonlinear,
}

SPR = {"tvdata.rate_of_change", "tvdata.slope_scaled"}


# --------------------------------------------------- proving the check can fail

def prove() -> int:
    """A check nobody has seen fail is worth nothing: break four items on purpose."""
    import copy
    bad = 0

    def expect(name, mutate, why):
        """Break one generated item on purpose and insist the check sees it."""
        nonlocal bad
        item = None
        for seed in range(1, 60):
            try:
                made = generate(name, seed)
            except ItemError:
                continue
            if made.fmt == "mcq":          # every injection swaps or rewrites an option
                item = copy.deepcopy(made)
                break
        if item is None:
            bad += 1
            print(f" FAIL  {why}: no multiple-choice draw to break")
            return
        mutate(item)
        try:
            CHECKS[name](item)
        except (AssertionError, Unreadable) as exc:
            print(f"  ok   {why}\n         caught: {str(exc)[:110]}")
            return
        bad += 1
        print(f" FAIL  {why} was NOT caught")

    def point_at_key(item):
        i = "ABCD".index(item.answer)
        item.choices[i], item.choices[(i + 1) % 4] = (item.choices[(i + 1) % 4],
                                                      item.choices[i])

    expect("tvdata.predict_from_line", point_at_key,
           "a prediction keyed to the wrong option")
    def tilt_the_line(it):
        it.figure = _tilt(it.figure)

    expect("tvdata.fit_slope", tilt_the_line,
           "a line of best fit drawn at the wrong slope")

    def second_truth(it):
        """Add the sentence that says the same thing the other way round."""
        text = it.choices[keyed(it)]
        m = DOWN.match(text) or UP.match(text)
        if m is None:
            raise Unreadable(text)
        tail = "decrease" if UP.match(text) else "increase"
        twin = f"As the {m.group(1)} decreases, the {m.group(2)} tends to {tail}."
        slot = next(i for i in range(4)
                    if i != keyed(it) and it.choices[i] != twin)
        it.choices[slot] = twin

    expect("tvdata.association", second_truth,
           "an association item with two true sentences")
    expect("tvdata.nonlinear_table",
           lambda it: it.choices.__setitem__(
               (keyed(it) + 1) % 4, "x = 1, 2, 3, 4; y = 3, 9, 27, 81"),
           "a table item with two nonlinear tables")
    return 1 if bad else 0


def _tilt(svg: str) -> str:
    """Move one end of the drawn line of best fit by twelve pixels."""
    m = BEST.search(svg)
    if m is None:
        raise Unreadable("no line to tilt")
    x1, y1, x2, y2 = (float(v) for v in m.groups())
    return svg.replace(m.group(0),
                       f'<line class="bf" x1="{x1}" y1="{y1}" x2="{x2}" '
                       f'y2="{y2 - 12}"/>')


# ------------------------------------------------------------------- driver

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--draws", type=int, default=400,
                    help="seeds to try per template (default 400)")
    ap.add_argument("--template", action="append",
                    help="check only this template; repeatable")
    ap.add_argument("--prove", action="store_true",
                    help="inject known-bad items and show they are caught")
    args = ap.parse_args()
    if args.prove:
        return prove()

    worst = 0
    for name in (args.template or list(CHECKS)):
        checker = CHECKS[name]
        made = bad = 0
        what = ""
        for seed in range(args.draws):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            if item.fmt == "mcq" and len(item.choices) != 4:
                continue
            made += 1
            try:
                what = checker(item)
            except (AssertionError, Unreadable) as exc:
                bad += 1
                if bad == 1:
                    print(f"\n{name} seed {seed}: {exc}")
                    print(item.pretty()[:1400])
        mark = "  ok  " if not bad else " FAIL "
        print(f"{mark} {name:<28} {made:>5,} items, {bad} defects   ({what})")
        worst |= 1 if bad else 0
    return worst


if __name__ == "__main__":
    sys.exit(main())
