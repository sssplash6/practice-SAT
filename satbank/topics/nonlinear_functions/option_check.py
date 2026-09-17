"""Read the four printed options back, and check only one of them is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct, because nothing in the engine reads a wrong
option as mathematics: `assemble_text` shuffles four strings and `text_item`
deduplicates them by the signature it was handed, `audit` re-derives the key
and compares, `structure` counts surface forms and `prose` looks for
placeholders. An item with two right answers satisfies every one of them.

This topic is the worst-exposed in the set, three ways. Most of its options
are EQUATIONS, and two exponentials can be the same model written differently
-- `600(0.85)^t` and `600(17/20)^t`, `1,800(1.02)^(q/4)` and
`1,800(1.02^(1/4))^q` -- so an option set has to be decided by solving each
option rather than by comparing its text with the key's. Several templates
print SENTENCES, where a distractor can be a true statement about the model
and still not answer the question. And eight templates hang the question on a
DRAWN CURVE, which is only checked if something reads the picture -- both what
it says and how finely it can be read, since two options nearer together than
the gridlines can separate are two answers whichever one is keyed.

So this script parses the printed stem, the printed table, the printed options
and the SVG's own pixel geometry, decides every option from that alone, and
asserts that exactly one option has the property the stem asks for and that it
is the keyed one. It imports no template, no renderer and no solver from this
topic: `generate` obtains the finished item and `expr.parse` reads printed
mathematics back, and that is all.

    PYTHONPATH=. python3 satbank/topics/nonlinear_functions/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 800 --template nlfunc.exp_model
    PYTHONPATH=. python3 .../option_check.py --selftest

Exits non-zero on the first kind of defect it finds, and prints the item.
"""

from __future__ import annotations

import argparse
import copy
import math
import re
import sys
from fractions import Fraction as Q

from satbank.expr import ParseError, agree, parse
from satbank.item import ItemError
from satbank.registry import generate

MINUS = "−"


class Unreadable(Exception):
    """The printed text is not something this reader understands.

    Raised, never swallowed: an option this file cannot read is an option it
    cannot clear, and the run reports it rather than passing quietly.
    """


# --------------------------------------------------- printed text -> numbers

# the fraction alternative comes first: `-7/6` must not be read as `-7`
N = r"(?:−|-)?\d[\d,]*(?:\.\d+)?(?:/\d+)?"


def num(text) -> Q:
    """A printed number: 8, −11, 2,300, 9/7, 3.5, (3/4), $46.60, 10%."""
    t = (str(text).replace(MINUS, "-").replace(",", "").replace(" ", "")
         .strip().lstrip("$").rstrip("%").rstrip("."))
    if t.startswith("(") and t.endswith(")"):
        t = t[1:-1]
    if not t:
        raise Unreadable(repr(text))
    try:
        if "/" in t:
            a, b = t.split("/", 1)
            return Q(a) / Q(b)
        return Q(t)
    except (ValueError, ZeroDivisionError, ArithmeticError):
        raise Unreadable(repr(text))


def stem_num(text: str, pattern: str, group: int = 1) -> Q:
    m = re.search(pattern, text)
    if m is None:
        raise Unreadable(f"{pattern!r} is not in the printed text")
    return num(m.group(group))


def numbers_in(text: str) -> list:
    """Every number literal a printed expression shows."""
    return [num(t) for t in re.findall(N, text)]


# ------------------------------------------------ printed text -> a function
#
# `expr.parse` is the engine's reader for printed mathematics and shares
# nothing with this topic's renderers, which is the point: a renderer that
# drops a minus sign has to be invisible to the renderer and visible here.

_SUPER = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6",
          "⁷": "7", "⁸": "8", "⁹": "9"}


def fn_of(text: str, var: str = "x"):
    """A printed expression as a callable of one variable.

    Superscripts are handed to `expr.parse` as it prints them; a trailing
    `^(...)` power and juxtaposed multiplication it already understands. A
    printed equation is split at its single equals sign and the right side is
    taken, which is what an option like `f(x) = 5(2^(−x))` means.
    """
    body = str(text).strip().rstrip(".")
    if body.count("=") == 1:
        body = body.split("=", 1)[1].strip()
    elif "=" in body:
        raise Unreadable(f"{text!r} has more than one equals sign")
    try:
        f = parse(body)
    except (ParseError, ValueError) as exc:
        raise Unreadable(f"{text!r}: {exc}")

    def run(v):
        return f(**{var: v})

    return run


def value_at(text: str, v, var: str = "x") -> float:
    try:
        return fn_of(text, var)(v)
    except (ParseError, ValueError, ZeroDivisionError, OverflowError) as exc:
        raise Unreadable(f"{text!r} at {var} = {v}: {exc}")


def defined_at(text: str, v, var: str = "x"):
    """The value, or None where the printed expression has no value there."""
    try:
        out = fn_of(text, var)(v)
    except Exception:                                           # noqa: BLE001
        return None
    return out if isinstance(out, (int, float)) and math.isfinite(out) else None


def near(a, b, rel: float = 1e-7) -> bool:
    a, b = float(a), float(b)
    return abs(a - b) <= rel * max(1.0, abs(a), abs(b))


def point_of(text: str) -> tuple:
    """A printed ordered pair back into two exact rationals."""
    t = str(text).strip()
    if not (t.startswith("(") and t.endswith(")")):
        raise Unreadable(f"{text!r} is not an ordered pair")
    parts = t[1:-1].split(",")
    if len(parts) != 2:
        raise Unreadable(f"{text!r} does not have two coordinates")
    return num(parts[0]), num(parts[1])


# --------------------------------------------------- printed SVG -> a curve

_GRID = re.compile(r'<line class="gr" x1="([-\d.]+)" y1="([-\d.]+)" '
                   r'x2="([-\d.]+)" y2="([-\d.]+)"/>')
_AXIS = re.compile(r'<line class="ax" x1="([-\d.]+)" y1="([-\d.]+)" '
                   r'x2="([-\d.]+)" y2="([-\d.]+)"/>')
_LABEL = re.compile(r'<text class="lb" x="([-\d.]+)" y="([-\d.]+)" '
                    r'text-anchor="(middle|end)">([^<]+)</text>')
_POLY = re.compile(r'<polyline class="ln" points="([^"]+)"/>')


class Figure:
    """A drawn curve, recovered from the picture's own pixel geometry.

    Nothing here consults a parameter of the item. The two axes fix where the
    zero of each scale sits; the printed tick labels fix how many units a
    pixel is worth; the gridlines fix how finely the picture can be read; and
    the polyline is the curve itself.
    """

    def __init__(self, svg: str):
        if not svg:
            raise Unreadable("the item carries no figure")
        self.svg = svg
        labels = _LABEL.findall(svg)
        grid = [tuple(float(v) for v in g) for g in _GRID.findall(svg)]
        xlines = sorted({g[0] for g in grid if g[0] == g[2]})
        ylines = sorted({g[1] for g in grid if g[1] == g[3]})
        xs = [(_snap(float(x), xlines), num(v))
              for x, y, anc, v in labels if anc == "middle"]
        ys = [(_snap(float(y), ylines), num(v))
              for x, y, anc, v in labels if anc == "end"]
        self.xmap = _affine(xs)
        self.ymap = _affine(ys)
        self.xgrid = _spacing(xlines)
        self.ygrid = _spacing(ylines)
        ax = [tuple(float(v) for v in a) for a in _AXIS.findall(svg)]
        self.axis_x = next((a[0] for a in ax if a[0] == a[2]), None)
        self.axis_y = next((a[1] for a in ax if a[1] == a[3]), None)
        self.runs = []
        for body in _POLY.findall(svg):
            pts = [tuple(float(v) for v in p.split(",")) for p in body.split()]
            self.runs.append(pts)
        if not self.runs:
            raise Unreadable("the figure draws no curve")

    # ---- pixel -> data

    def X(self, px: float) -> float:
        if self.xmap is None:
            raise Unreadable("the horizontal axis carries no readable scale")
        return self.xmap[0] + (px - self.xmap[1]) * self.xmap[2]

    def Y(self, py: float) -> float:
        if self.ymap is None:
            raise Unreadable("the vertical axis carries no readable scale")
        return self.ymap[0] + (py - self.ymap[1]) * self.ymap[2]

    def points(self) -> list:
        return [(self.X(px), self.Y(py)) for run in self.runs for px, py in run]

    def grid_y(self) -> float:
        """How many units apart the horizontal gridlines are drawn."""
        if self.ygrid is None or self.ymap is None:
            raise Unreadable("the picture has no readable horizontal gridlines")
        return abs(self.ygrid * self.ymap[2])

    def grid_x(self) -> float:
        if self.xgrid is None or self.xmap is None:
            raise Unreadable("the picture has no readable vertical gridlines")
        return abs(self.xgrid * self.xmap[2])

    def at_axis(self) -> float:
        """The drawn value where the curve crosses the vertical axis."""
        if self.axis_x is None:
            raise Unreadable("the picture draws no vertical axis")
        best = None
        for run in self.runs:
            for px, py in run:
                d = abs(px - self.axis_x)
                if best is None or d < best[0]:
                    best = (d, py)
        if best is None or best[0] > 4:
            raise Unreadable("the drawn curve does not reach the vertical axis")
        return self.Y(best[1])

    def at(self, x: float) -> float:
        """The drawn value at a data x, taken off the polyline."""
        pts = self.points()
        best = min(pts, key=lambda p: abs(p[0] - x))
        if abs(best[0] - x) > self.grid_x() / 2:
            raise Unreadable(f"the drawn curve does not reach x = {x}")
        return best[1]

    def peak(self) -> tuple:
        return max(self.points(), key=lambda p: p[1])


def _snap(pixel: float, lines) -> float:
    """A printed label sits beside its gridline; this is which one."""
    if not lines:
        return pixel
    return min(lines, key=lambda v: abs(v - pixel))


def _affine(pairs):
    """(value0, pixel0, units per pixel) from two or more printed tick labels."""
    if len(pairs) < 2:
        return None
    pairs = sorted(pairs)
    (p1, v1), (p2, v2) = pairs[0], pairs[-1]
    if p1 == p2:
        return None
    return (float(v1), p1, float(v2 - v1) / (p2 - p1))


def _spacing(values):
    vals = sorted(set(round(v, 2) for v in values))
    if len(vals) < 2:
        return None
    return min(b - a for a, b in zip(vals, vals[1:]))


# ------------------------------------------------------------ the assertion

def keyed(item) -> int:
    return "ABCD".index(item.answer)


def one_hit(item, hits: list, what: str, detail: str = "") -> str:
    """Exactly one option has the property, and it is the keyed one."""
    if len(hits) != 4:
        raise Unreadable(f"decided {len(hits)} of the four options")
    if hits.count(True) != 1:
        raise AssertionError(f"{hits.count(True)} of the four options are correct "
                             f"({what}){detail}")
    if not hits[keyed(item)]:
        raise AssertionError(f"the keyed option is not the correct one ({what})"
                             f"{detail}")
    return what


def all_distinct(item) -> None:
    vals = []
    for c in item.choices:
        try:
            vals.append(num(c))
        except Unreadable:
            return
    if len(set(vals)) != 4:
        raise AssertionError(f"two options print the same number: {item.choices}")


# ========================================================== the checks

def check_evaluate(item) -> str:
    """Exactly one option is the printed rule evaluated at the printed input."""
    m = re.search(r"([A-Za-z])\(x\) = (.+?)(?=\.\s+What|,\s+what|\s+For the function)",
                  item.stem)
    if m is None:
        raise Unreadable("no printed rule of the form f(x) = ...")
    name, body = m.group(1), m.group(2).strip()
    at = re.search(rf"value of {name}\(({N})\)", item.stem) \
        or re.search(rf"what is {name}\(({N})\)", item.stem) \
        or re.search(rf"when x = ({N})", item.stem)
    if at is None:
        raise Unreadable("the stem names no input")
    x0 = at.group(1)
    want = value_at(body, float(num(x0)))
    all_distinct(item)
    hits = [near(num(c), want, 1e-9) for c in item.choices]
    return one_hit(item, hits, "the printed rule at the printed input",
                   f"; {name}({x0}) = {want:g}")


def check_solve_value(item) -> str:
    """Exactly one option satisfies the printed equation."""
    m = re.search(rf"([A-Za-z])\(([a-z])\) = (.+?)\. What is the value of "
                  rf"[a-z] when [A-Za-z]\([a-z]\) is equal to ({N})", item.stem)
    if m:
        body, var, target = m.group(3).strip(), m.group(2), num(m.group(4))
        all_distinct(item)
        hits = [near(value_at(body, float(num(c)), var), target) for c in item.choices]
        return one_hit(item, hits, "the input the printed rule sends to the target",
                       f"; the target is {target}")
    mass = stem_num(item.stem, rf"mass of ({N}) kilograms")
    energy = stem_num(item.stem, rf"kinetic energy of ({N}) joules")
    all_distinct(item)
    hits = [near(Q(1, 2) * mass * num(c) ** 2, energy) for c in item.choices]
    return one_hit(item, hits, "the speed the printed mass and energy give",
                   f"; (1/2)({mass})v² = {energy}")


def check_param_value(item) -> str:
    """The hidden constant comes from the stated value; then exactly one option."""
    K = stem_num(item.stem, rf"\)² \+ ({N})\)/\(2c\)")
    v = stem_num(item.stem, rf"[A-Za-z]\(c\) = ({N})")
    m = stem_num(item.stem, rf"value of [A-Za-z]\(({N})\)\?")
    if v == 0:
        raise Unreadable("the stated value is zero")
    c = K / (2 * v)
    want = ((m - c) ** 2 + K) / (2 * c)
    all_distinct(item)
    hits = [near(num(x), want, 1e-9) for x in item.choices]
    return one_hit(item, hits, "the rule's value once the constant is found",
                   f"; c = {c}, p({m}) = {float(want):.4f}")


def check_y_intercept(item) -> str:
    """Exactly one option is where the printed rule meets the y-axis."""
    if "must be equal to c" in item.stem:
        hits = [bool(re.fullmatch(r"[A-Za-z]\(0\)", c.strip())) for c in item.choices]
        return one_hit(item, hits, "the function value at x = 0")
    m = re.search(r"([A-Za-z])\(x\) = (.+?) If the given function", item.stem)
    if m is None:
        raise Unreadable("no printed rule before the question")
    want = value_at(m.group(2).strip(), 0.0)
    hits = []
    for c in item.choices:
        x, y = point_of(c)
        hits.append(x == 0 and near(y, want))
    return one_hit(item, hits, "the point (0, f(0)) of the printed rule",
                   f"; f(0) = {want:g}")


def check_x_intercept(item) -> str:
    """Zeros of the printed rule -- or, once, the point that is not one."""
    m = re.search(r"([A-Za-z])\(x\) = (.+?)(?: The function| If the given function|"
                  r" The quadratic function)", item.stem)
    if m is None:
        raise Unreadable("no printed rule before the question")
    body = m.group(2).strip()
    if "NOT an x-intercept" in item.stem:
        hits = []
        for c in item.choices:
            x, y = point_of(c)
            hits.append(not (y == 0 and near(value_at(body, float(x)), 0.0, 1e-9)))
        return one_hit(item, hits, "the only printed point that is not a zero")
    if "(t, 0)" in item.stem:
        all_distinct(item)
        hits = [near(value_at(body, float(num(c))), 0.0, 1e-9) and num(c) != 0
                for c in item.choices]
        return one_hit(item, hits, "the nonzero zero of the printed rule")
    hits = []
    for c in item.choices:
        x, y = point_of(c)
        hits.append(y == 0 and near(value_at(body, float(x)), 0.0, 1e-9))
    return one_hit(item, hits, "a point where the printed rule is zero")


def check_graph_intercept(item) -> str:
    """Exactly one printed point is where the DRAWN curve meets the y-axis."""
    fig = Figure(item.figure)
    drawn = fig.at_axis()
    step = fig.grid_y()
    hits = []
    for c in item.choices:
        x, y = point_of(c)
        hits.append(x == 0 and abs(float(y) - drawn) < step * 0.4)
    what = one_hit(item, hits, "the drawn curve's value on the y-axis",
                   f"; the picture reads {drawn:.3f}")
    kx, ky = point_of(item.choices[keyed(item)])
    for i, c in enumerate(item.choices):
        if i == keyed(item):
            continue
        x, y = point_of(c)
        if x == kx and abs(float(y) - float(ky)) < step * 0.9:
            raise AssertionError(f"{c!r} is less than a gridline from the key on a "
                                 f"picture gridlined every {step:g}")
    return what


def check_graph_context(item) -> str:
    """The starting value, or the peak, taken off the DRAWN chart."""
    fig = Figure(item.figure)
    if "closest to the" in item.stem:
        want, step = fig.peak()[0], fig.grid_x()
        what = "the input at which the drawn curve is highest"
    else:
        want, step = fig.at_axis(), fig.grid_y()
        what = "the drawn curve's value at the start"
    all_distinct(item)
    hits = [abs(float(num(c)) - want) < step * 0.4 for c in item.choices]
    out = one_hit(item, hits, what, f"; the picture reads {want:g}")
    key = num(item.choices[keyed(item)])
    for i, c in enumerate(item.choices):
        if i != keyed(item) and abs(float(num(c) - key)) < step * 0.9:
            raise AssertionError(f"{c!r} is less than a gridline from the key on a "
                                 f"chart gridlined every {step:g}")
    return out


WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3}


def check_graph_zeros(item) -> str:
    """How often the DRAWN curve actually crosses the x-axis."""
    fig = Figure(item.figure)
    pts = sorted(fig.points())
    crossings = sum(1 for a, b in zip(pts, pts[1:]) if (a[1] > 0) != (b[1] > 0))
    hits = [WORDS.get(c.strip().lower()) == crossings for c in item.choices]
    return one_hit(item, hits, "the number of times the drawn curve meets the x-axis",
                   f"; the picture crosses {crossings} time(s)")


def check_graph_equation(item) -> str:
    """Exactly one printed equation passes through the DRAWN curve."""
    fig = Figure(item.figure)
    pts = [p for p in fig.points()]
    if len(pts) < 20:
        raise Unreadable("too little of the curve is drawn to test against")
    sample = pts[:: max(1, len(pts) // 25)]
    tol = fig.grid_y() * 0.02
    hits = []
    for c in item.choices:
        f = fn_of(c)
        ok = True
        for x, y in sample:
            v = defined_at(c, x)
            if v is None or abs(v - y) > tol:
                ok = False
                break
        hits.append(ok)
    return one_hit(item, hits, "the equation the drawn curve follows",
                   f"; sampled {len(sample)} drawn points to {tol:g}")


# --------------------------------------------------------- exponentials

def _percent(stem: str) -> Q:
    return stem_num(stem, rf"({N})%") / 100


def _model_hits(item, start, factor, var: str, extra=None) -> list:
    """Which printed options are the model `start · factor^var`?"""
    hits = []
    for c in item.choices:
        f = fn_of(c, var)
        try:
            v0, v1, v2 = f(0.0), f(1.0), f(2.0)
        except Exception:                                       # noqa: BLE001
            hits.append(False)
            continue
        ok = (near(v0, float(start), 1e-9)
              and near(v1, float(start) * float(factor), 1e-9)
              and near(v2, float(start) * float(factor) ** 2, 1e-9))
        hits.append(bool(ok))
    return hits


def check_exp_model(item) -> str:
    """Exactly one printed equation is the model the words describe."""
    stem = item.stem
    var = "d" if "days after the video" in stem else (
        "t" if re.search(r"\bt years after\b|, t years after|number of years", stem)
        else "x")
    var = re.search(r"\b([a-z])\b(?= days after| years after)", stem)
    var = var.group(1) if var else "x"
    if "doubled from the number the previous day" in stem:
        start = stem_num(stem, rf"had ({N}) subscribers")
        factor = Q(2)
    else:
        r = _percent(stem)
        if "declined each year" in stem or "less than the number" in stem:
            factor = 1 - r
        else:
            factor = 1 + r
        start = stem_num(stem, rf"approximately ({N}) million CDs") if "CDs" in stem \
            else (stem_num(stem, rf"had ({N}) students") if "students" in stem
                  else (stem_num(stem, rf"was ({N}) in ") if "population of Bergen" in stem
                        else stem_num(stem, rf"when ({N}) jackrabbits")))
    hits = _model_hits(item, start, factor, var)
    return one_hit(item, hits, "the model the printed words describe",
                   f"; {start} multiplied by {factor} each {var}")


def check_exp_period(item) -> str:
    """The period belongs in the exponent, and only one option puts it there."""
    stem = item.stem
    if "views of an advertisement" in stem:
        start = stem_num(stem, rf"there were ({N}) views")
        k = stem_num(stem, rf"Every ({N}) days after")
        factor = 1 + _percent(stem)
        var = "x"
    else:
        m = re.search(rf"= ({N})\(({N})\)\^t", stem)
        if m is None:
            raise Unreadable("no printed yearly model")
        start, factor = num(m.group(1)), num(m.group(2))
        mv = re.search(r"\b([a-z]) (quarter years|months) after", stem)
        if mv is None:
            raise Unreadable("the stem does not say what the new unit counts")
        var = mv.group(1)
        k = Q(4) if mv.group(2) == "quarter years" else Q(12)
    hits = []
    for c in item.choices:
        f = fn_of(c, var)
        try:
            v0, vk, v2k = f(0.0), f(float(k)), f(2.0 * float(k))
        except Exception:                                       # noqa: BLE001
            hits.append(False)
            continue
        hits.append(bool(near(v0, float(start), 1e-9)
                         and near(vk, float(start) * float(factor), 1e-9)
                         and near(v2k, float(start) * float(factor) ** 2, 1e-9)))
    return one_hit(item, hits, "the model that folds the period into the exponent",
                   f"; {start} multiplied by {factor} every {k} {var}")


def check_exp_from_table(item) -> str:
    """Exactly one printed equation reproduces every row of the printed table."""
    if not item.table:
        raise Unreadable("the item carries no table")
    rows = [(num(a), num(b)) for a, b in item.table[1:]]
    var = "t" if item.table[0][0].lower().startswith("time") else "x"
    hits = []
    for c in item.choices:
        ok = True
        for x, y in rows:
            v = defined_at(c, float(x), var)
            if v is None or not near(v, float(y), 1e-4):
                ok = False
                break
        hits.append(ok)
    return one_hit(item, hits, "the equation that fits every printed row",
                   f"; {len(rows)} rows")


def check_exp_offset(item) -> str:
    """The model must approach the room, and match the three printed readings."""
    stem = item.stem
    amb = stem_num(stem, rf"constant temperature of ({N}) degrees")
    temps = [num(t) for t in re.findall(rf"({N})°F", stem)]
    if len(temps) < 3:
        raise Unreadable("the stem prints fewer than three temperatures")
    t0, t1, t2 = temps[:3]
    mins = [int(m) for m in re.findall(r":(\d\d) p\.m\.", stem)]
    if len(mins) < 3:
        raise Unreadable("the stem prints no reading times")
    k = mins[1]
    hits = []
    for c in item.choices:
        f = fn_of(c, "m")
        try:
            v0, vk, v2k, far = f(0.0), f(float(k)), f(2.0 * k), f(400.0 * k)
        except Exception:                                       # noqa: BLE001
            hits.append(False)
            continue
        hits.append(bool(near(v0, float(t0), 1e-9)
                         and abs(vk - float(t1)) <= 0.5
                         and abs(v2k - float(t2)) <= 0.5
                         and abs(far - float(amb)) <= 0.5))
    return one_hit(item, hits, "the model that starts, cools and settles as printed",
                   f"; {t0} to {t1} to {t2}, settling at {amb}")


def check_exp_anchor(item) -> str:
    """The printed reading is a year in, so the coefficient is not that reading."""
    stem = item.stem
    v = stem_num(stem, rf"there were ({N}) ")
    factor = 1 + _percent(stem)
    hits = []
    for c in item.choices:
        f = fn_of(c, "t")
        try:
            v0, v1, v2 = f(0.0), f(1.0), f(2.0)
        except Exception:                                       # noqa: BLE001
            hits.append(False)
            continue
        hits.append(bool(near(v1, float(v), 1e-9)
                         and v0 != 0 and near(v1 / v0, float(factor), 1e-9)
                         and near(v2 / v1, float(factor), 1e-9)))
    return one_hit(item, hits, "the model that gives the printed count a year in",
                   f"; {v} at t = 1, growing by a factor of {factor}")


def check_exp_reach(item) -> str:
    """The equation to solve: the right side grows from the current population."""
    stem = item.stem
    a = stem_num(stem, rf"currently ({N}),")
    b = stem_num(stem, rf"to reach ({N})")
    factor = 1 + _percent(stem)
    hits = []
    for c in item.choices:
        if c.count("=") != 1:
            hits.append(False)
            continue
        lhs, rhs = c.split("=")
        try:
            left = fn_of(lhs.strip() + " = 0", "t")(0.0) if False else float(num(lhs))
        except Unreadable:
            hits.append(False)
            continue
        f = fn_of(rhs.strip(), "t")
        try:
            v0, v1 = f(0.0), f(1.0)
        except Exception:                                       # noqa: BLE001
            hits.append(False)
            continue
        hits.append(bool(near(left, float(b), 1e-9) and near(v0, float(a), 1e-9)
                         and v0 != 0 and near(v1 / v0, float(factor), 1e-9)))
    return one_hit(item, hits, "the equation whose solution is the number of years",
                   f"; {b} = {a}({factor})^t")


def check_exp_rate(item) -> str:
    """A growth factor, a yearly percent, or the range a falling rate must lie in."""
    stem = item.stem
    if "must be true" in stem:
        rising = "increases by a fixed percent" in stem
        hits = []
        for c in item.choices:
            ok = _interval_holds(c, rising)
            hits.append(ok)
        return one_hit(item, hits,
                       "the range of r that makes the printed model "
                       + ("rise" if rising else "fall"))
    if "value of a?" in stem:
        want = 1 + _percent(stem)
        all_distinct(item)
        hits = [near(num(c), want, 1e-9) for c in item.choices]
        return one_hit(item, hits, "the factor a percent rise multiplies by",
                       f"; 1 + {want - 1} = {want}")
    m = re.search(rf"= ({N})\(({N})\)\^\(x/({N})\)", stem)
    if m is None:
        raise Unreadable("no printed period model")
    base, k = num(m.group(2)), num(m.group(3))
    yearly = base ** int(k // k)          # one year is x = k, where the exponent is 1
    want = 100 * (1 - yearly)
    all_distinct(item)
    hits = [near(num(c), want, 1e-9) for c in item.choices]
    return one_hit(item, hits, "the percent a whole year takes off",
                   f"; a year multiplies by {base}")


def _interval_holds(text: str, rising: bool) -> bool:
    """Does the printed range of r hold exactly the r that behave as stated?"""
    t = text.replace(MINUS, "-").replace(" ", "")
    samples = [Q(-3), Q(-3, 2), Q(-1, 2), Q(1, 2), Q(3, 2), Q(3)]
    inside = []
    for r in samples:
        m = re.fullmatch(r"(-?[\d./]+)<r<(-?[\d./]+)", t)
        if m:
            inside.append(num(m.group(1)) < r < num(m.group(2)))
            continue
        m = re.fullmatch(r"r<(-?[\d./]+)", t)
        if m:
            inside.append(r < num(m.group(1)))
            continue
        m = re.fullmatch(r"r>(-?[\d./]+)", t)
        if m:
            inside.append(r > num(m.group(1)))
            continue
        raise Unreadable(f"{text!r} is not a range of r")
    want = [(1 + r > 1) if rising else (0 < 1 + r < 1) for r in samples]
    return inside == want


def check_exp_two_points(item) -> str:
    """a and b come from the two printed points; exactly one option is their product."""
    stem = item.stem
    p = stem_num(stem, rf"through the points \(0, ({N})\)")
    m = re.search(rf"\(−({N}), ({N})\)", stem) or re.search(rf"\(-({N}), ({N})\)", stem)
    if m is None:
        raise Unreadable("the stem prints no second point")
    e, v = num(m.group(1)), num(m.group(2))
    b = p - 1
    tail = v - b
    if tail <= 0:
        raise Unreadable("the second point lies below the horizontal asymptote")
    a = float(1 / tail) ** (1.0 / float(e))
    all_distinct(item)
    hits = [near(num(c), a * float(b), 1e-6) for c in item.choices]
    return one_hit(item, hits, "the product of the two constants",
                   f"; a = {a:g}, b = {b}")


ROMAN = {"I only": (True, False), "II only": (False, True),
         "I and II": (True, True), "Neither I nor II": (False, False)}


def _shows_extreme(eq: str) -> bool:
    """Does the printed equation show its own value at x = 0 as a literal?"""
    v = value_at(eq, 0.0)
    return any(near(float(n), v, 1e-9) for n in numbers_in(eq.split("=", 1)[1]))


def check_exp_display(item) -> str:
    """Which printed form shows its own extreme value as a constant?"""
    eqs = re.findall(r"(?:I|II)\. ([A-Za-z]\(x\) = [^I]+?)(?= II\.| Which)", item.stem)
    if len(eqs) != 2:
        raise Unreadable(f"found {len(eqs)} printed equations, not two")
    shows = tuple(_shows_extreme(e.strip()) for e in eqs)
    hits = [ROMAN.get(c.strip()) == shows for c in item.choices]
    return one_hit(item, hits, "which printed form shows its extreme value",
                   f"; I {'does' if shows[0] else 'does not'}, "
                   f"II {'does' if shows[1] else 'does not'}")


def check_exp_rewrite(item) -> str:
    """Equivalent forms, and the one that puts the named number on show."""
    stem = item.stem
    m = re.search(rf"y = ({N})\^\(({N})x \+ ({N})\)", stem)
    if m:
        base, k = num(m.group(1)), num(m.group(2))
        s = float(base) ** float(m.group(3))
        hits = [any(near(float(n), s, 1e-9) for n in numbers_in(c.split("=", 1)[1]))
                for c in item.choices]
        return one_hit(item, hits, "the form whose own numbers include the y-intercept",
                       f"; s = {s:g}")
    F = stem_num(stem, rf"factor of ({N})")
    base = [fn_of(c) for c in item.choices]
    v0 = [f(0.0) for f in base]
    if not all(near(v, v0[0]) for v in v0):
        raise AssertionError("the four printed forms do not agree at x = 0")
    for probe in (0.5, 1.0, 2.0):
        vals = [f(probe) for f in base]
        if not all(near(v, vals[0], 1e-7) for v in vals):
            raise AssertionError(f"the four printed forms disagree at x = {probe}; "
                                 f"they are meant to be equivalent")
    ratio = base[0](1.0) / base[0](0.0)
    c = math.log(float(F)) / math.log(ratio)
    hits = []
    for text in item.choices:
        shown = re.search(r"\(\((\d+/\d+)\)x\)", text)
        if shown is None:
            raise Unreadable(f"{text!r} shows no coefficient of x")
        hits.append(near(num(shown.group(1)), 1 / c, 1e-7))
    return one_hit(item, hits, "the form that shows 1/c as the coefficient of x",
                   f"; c = {c:g}")


def check_exp_steps(item) -> str:
    """Doubling: which printed year or day the count reaches the printed total."""
    stem = item.stem
    if "Moore's law" in stem:
        k = stem_num(stem, rf"doubles every ({N}) years")
        y0 = stem_num(stem, rf"In ({N}), a microprocessor")
        a = stem_num(stem, rf"that had ({N}) transistors")
        target = stem_num(stem, rf"to reach ({N})\?")
        n = math.log(float(target / a), 2)
        want = float(y0) + float(k) * n
        all_distinct(item)
        hits = [near(num(c), want, 1e-9) for c in item.choices]
        return one_hit(item, hits, "the year the doubling count is reached",
                       f"; {n:g} doublings of {k} years from {y0}")
    if not item.table:
        raise Unreadable("the item carries no table")
    rows = [(num(d), _sci(v)) for d, v in item.table[1:]]
    ratio = rows[1][1] / rows[0][1]
    target = _sci(re.search(r"reach (.+)\?", stem).group(1))
    n = math.log(float(target / rows[0][1]), float(ratio))
    want = float(rows[0][0]) + n
    hits = [near(num(c.replace("Day", "")), want, 1e-9) for c in item.choices]
    return one_hit(item, hits, "the day the printed count is reached",
                   f"; {n:g} doublings after day {rows[0][0]}")


_SCI = re.compile(r"([\d.]+)\s*×\s*10([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)")


def _sci(text: str) -> Q:
    m = _SCI.search(str(text))
    if m is None:
        return num(text)
    exp = "".join(_SUPER.get(ch, "-" if ch == "⁻" else ch) for ch in m.group(2))
    return num(m.group(1)) * Q(10) ** int(exp)


def check_exp_power_table(item) -> str:
    raise Unreadable("this template answers with a grid-in and prints no options")


# ------------------------------------------------------------- parabolas

def _extreme(body: str, lo: float, hi: float, want_max: bool):
    """Where a printed parabola turns, found by search rather than by algebra."""
    f = fn_of(body)
    best, arg = None, None
    n = 4000
    for i in range(n + 1):
        x = lo + (hi - lo) * i / n
        try:
            v = f(x)
        except Exception:                                       # noqa: BLE001
            continue
        if best is None or (v > best if want_max else v < best):
            best, arg = v, x
    if arg is None:
        raise Unreadable(f"{body!r} has no value on the searched range")
    step = (hi - lo) / n
    for _ in range(80):
        step /= 2
        for cand in (arg - step, arg + step):
            try:
                v = f(cand)
            except Exception:                                   # noqa: BLE001
                continue
            if (v > best) if want_max else (v < best):
                best, arg = v, cand
    return arg, best


def check_vertex_value(item) -> str:
    """The turning point of the printed parabola, found numerically."""
    stem = item.stem
    m = re.search(r"([A-Za-z])\((?:x|θ)\) = (.+?)(?:\. |\?$|\? | An engineer|"
                  r" The function| The given equation| What is| The graph)", stem)
    if m is None:
        m = re.search(r"y = (.+?), where x represents", stem)
        if m is None:
            raise Unreadable("no printed parabola")
        body, var = m.group(1).strip(), "x"
    else:
        body, var = m.group(2).strip(), "θ" if "(θ)" in stem else "x"
    body = body.replace("θ", "x")
    want_max = ("greatest airflow" in stem or "maximum of the graph" in stem)
    arg, val = _extreme(body, -400.0, 400.0, want_max)
    if "intervals contains" in stem:
        hits = []
        for c in item.choices:
            lo, hi = _range_of(c)
            hits.append(lo < arg < hi)
        return one_hit(item, hits, "the interval holding the printed vertex",
                       f"; the vertex is at x = {arg:.4f}")
    asks_value = ("minimum value" in stem or "maximum value" in stem)
    want = val if asks_value else arg
    all_distinct(item)
    hits = [near(num(c), want, 1e-5) for c in item.choices]
    return one_hit(item, hits,
                   "the value at the printed vertex" if asks_value
                   else "where the printed parabola turns",
                   f"; the vertex is ({arg:.4f}, {val:.4f})")


def _range_of(text: str) -> tuple:
    t = text.replace(MINUS, "-").replace(" ", "")
    m = re.fullmatch(r"(-?[\d./]+)<x<(-?[\d./]+)", t)
    if m is None:
        raise Unreadable(f"{text!r} is not an interval")
    return float(num(m.group(1))), float(num(m.group(2)))


def check_vertex_symmetry(item) -> str:
    """The two x-intercepts sit either side of the printed vertex."""
    h = stem_num(item.stem, rf"its vertex is \(({N}), ")
    given = stem_num(item.stem, rf"x-intercepts of this graph is \(({N}), 0\)")
    want = 2 * h - given
    hits = []
    for c in item.choices:
        x, y = point_of(c)
        hits.append(y == 0 and x == want)
    return one_hit(item, hits, "the mirror of the printed intercept in the vertex",
                   f"; {given} reflects to {want}")


def check_shift_max(item) -> str:
    """The maximum of the lifted parabola, as a number the expressions come to."""
    m = re.search(rf"f\(t\) = ({N})t {MINUS} ({N})t²", item.stem)
    if m is None:
        raise Unreadable("no printed quadratic")
    b, a = num(m.group(1)), num(m.group(2))
    k = stem_num(item.stem, rf"g\(t\) = f\(t\) \+ ({N})")
    want = float(k) + float(b) ** 2 / (4 * float(a))
    vals = [value_at(c, 0.0) for c in item.choices]
    if len(set(round(v, 9) for v in vals)) != 4:
        raise AssertionError(f"two printed expressions come to the same number: {vals}")
    hits = [near(v, want, 1e-9) for v in vals]
    return one_hit(item, hits, "the greatest value of the lifted parabola",
                   f"; it is {want:g}")


def check_quad_must_be_true(item) -> str:
    """Two claims about a parabola, each decided from the printed facts."""
    stem = item.stem
    b = stem_num(stem, rf"f\(x\) = ax² \+ ({N})x \+ c")
    m = re.search(rf"f\(({N})\) = f\(({N})\)", stem)
    if m is None:
        raise Unreadable("the stem states no pair of equal values")
    p, qv = num(m.group(1)), num(m.group(2))
    h = (p + qv) / 2
    if h == 0:
        raise Unreadable("the axis of symmetry sits on the y-axis")
    a = -b / (2 * h)
    claims = re.findall(r"I+\. ([^I]+?)(?= II\.| If k)", stem)
    if len(claims) != 2:
        raise Unreadable(f"found {len(claims)} claims, not two")
    truth = tuple(_claim(c.strip(), a=a, h=h) for c in claims)
    hits = [ROMAN.get(c.strip()) == truth for c in item.choices]
    return one_hit(item, hits, "which of the two claims the printed facts force",
                   f"; a = {a}, h = {h}")


def _claim(text: str, a: Q, h: Q) -> bool:
    """A claim about the parabola's constants, decided from a and h.

    `c` is never forced: k < 0 only bounds it from above, and c may be of
    either sign, so a claim about c alone cannot be true of every such
    parabola.
    """
    t = text.replace(MINUS, "-").replace(" ", "")
    if t.startswith("c"):
        return False
    if t == "a>0":
        return a > 0
    if t.startswith("h<"):
        return h < num(t[2:])
    m = re.fullmatch(r"a≥(-?[\d./]+)", t)
    if m:
        return a >= num(m.group(1))
    raise Unreadable(f"{text!r} is not a claim this reader decides")


def check_quad_fit(item) -> str:
    """A parabola pinned by an initial height and a vertex."""
    stem = item.stem
    if "Which equation represents the height" in stem:
        k = stem_num(stem, rf"maximum height of ({N}) meters")
        h = stem_num(stem, rf"above the ground at ({N}) seconds")
        g = stem_num(stem, rf"hits the ground at ({N}) seconds")
        hits = []
        for c in item.choices:
            v0 = defined_at(c, 0.0, "t")
            vh = defined_at(c, float(h), "t")
            vg = defined_at(c, float(g), "t")
            hits.append(bool(v0 is not None and vh is not None and vg is not None
                             and near(v0, 0.0, 1e-6) and near(vh, float(k), 1e-6)
                             and near(vg, 0.0, 1e-6)))
        return one_hit(item, hits, "the equation with the printed vertex and zero",
                       f"; 0 at t = 0 and t = {g}, {k} at t = {h}")
    y0 = stem_num(stem, rf"initial height of ({N}) feet")
    k = stem_num(stem, rf"maximum height of ({N}) feet")
    h = stem_num(stem, rf"({N}) seconds after being launched\.")
    t = stem_num(stem, rf"ground ({N}) seconds after being launched\?")
    a = (y0 - k) / (h ** 2)
    want = k + a * (t - h) ** 2
    all_distinct(item)
    hits = [near(num(c), want, 1e-9) for c in item.choices]
    return one_hit(item, hits, "the fitted parabola's value at the printed time",
                   f"; a = {a}, height = {want}")


# ----------------------------------------------------------- in words

def check_interpret_value(item) -> str:
    """Exactly one sentence says the output is the value at the input.

    Four sentence families appear, and each has one shape that reads the
    statement correctly. Every other shape -- an increase "by a total of", a
    multiple of last year, a percent, a loss rather than a remainder, or the
    input and output swapped -- is decided by the same regexes, so a
    distractor that happens to be a true sentence about the model is still
    not a hit.
    """
    m = re.search(rf"[a-z]\(({N})\) (?:is approximately equal to|=) ({N})", item.stem)
    if m is None:
        raise Unreadable("the stem states no function value")
    t, v = num(m.group(1)), num(m.group(2))
    shapes = [
        rf"^({N}) years after the company started selling .+ online, its predicted "
        rf"annual revenue is approximately ({N}) dollars\.$",
        rf"^({N}) years after \w+ purchased the rare coin, its predicted value is "
        rf"approximately ({N}) dollars\.$",
        rf"^The height of the object ({N}) seconds after being thrown straight up in "
        rf"the air is ({N}) feet\.$",
    ]
    reversed_shape = (rf"^Approximately ({N}) grams of the sample remains ({N}) years "
                      rf"after the sample starts to decay\.$")
    hits = []
    for c in item.choices:
        text = c.strip()
        hit = False
        for shape in shapes:
            mm = re.match(shape, text)
            if mm and num(mm.group(1)) == t and num(mm.group(2)) == v:
                hit = True
        mm = re.match(reversed_shape, text)
        if mm and num(mm.group(1)) == v and num(mm.group(2)) == t:
            hit = True
        hits.append(hit)
    return one_hit(item, hits, "the sentence that reads the value at the input",
                   f"; input {t}, output {v}")


def check_interpret_initial(item) -> str:
    """Exactly one sentence names the model's value at the start."""
    stem = item.stem
    year = re.search(r"(?:after|since|in) (\d{4})", stem)
    if year is None:
        year = None
    else:
        year = year.group(1)
    a = stem_num(stem, rf"= ({N})\(")
    hits = []
    for c in item.choices:
        low = c.strip().rstrip(".")
        if "percent" in low:
            hits.append(False)
            continue
        if low.startswith("The increase") or low.startswith("The estimated amount of "
                                                            "increase"):
            hits.append(False)
            continue
        if "number of years" in low:
            hits.append(False)
            continue
        if "minimum" in low:
            hits.append(False)
            continue
        if "t years after" in low or "years after" in low and "initial" not in low \
                and year and f"in {year}" not in low:
            hits.append(False)
            continue
        names_start = ("initial" in low or "when the restaurant opened" in low
                       or (year is not None and f"in {year}" in low))
        if names_start and re.search(N, low):
            names_start = any(n == a for n in numbers_in(low)) or \
                (year is not None and numbers_in(low) == [num(year)])
        hits.append(bool(names_start))
    return one_hit(item, hits, "the sentence naming the model's value at the start",
                   f"; the coefficient is {a}")


def check_interpret_rate(item) -> str:
    """The base is a percent per unit of d, and d is not one metre."""
    stem = item.stem
    step = 100 if "hundreds of meters" in stem else 1000
    base = stem_num(stem, rf"\)\^d The function|= ({N})\(({N})\)\^d", 2)
    pct = 100 * (1 - base)
    hits = []
    for c in item.choices:
        m = re.match(rf"For every increase in depth by ({N}) meters?, the number of "
                     rf"\w+ species decreases by ({N})(%?)\.", c.strip())
        if m is None:
            raise Unreadable(f"{c!r} is not a sentence this reader decides")
        hits.append(num(m.group(1)) == step and m.group(3) == "%"
                    and near(num(m.group(2)), pct))
    return one_hit(item, hits, "the loss per step of d, with the step in metres",
                   f"; {pct}% every {step} m")


def check_quad_feature(item) -> str:
    """What a feature of a quadratic model means, decided sentence by sentence."""
    stem = item.stem
    if "What does the number" in stem:
        hits = [c.strip().startswith("The initial height") for c in item.choices]
        return one_hit(item, hits, "the constant term is the starting height")
    if "from which the object was kicked" in stem:
        m = re.search(rf"h = ({N})t² \+ ({N})t \+ ({N})", stem.replace(MINUS, "-"))
        if m is None:
            raise Unreadable("no printed height model")
        c0 = num(m.group(3))
        all_distinct(item)
        hits = [num(x) == c0 for x in item.choices]
        return one_hit(item, hits, "the constant term of the printed model",
                       f"; it is {c0}")
    if "scheduled deliveries" in stem:
        rule = re.search(r"y = (.+?) The given equation", stem).group(1)
        start = value_at(rule, 0.0)
        month = re.search(r"end of (\w+) (\d{4})", stem)
        hits = []
        for c in item.choices:
            m = re.match(r"At the end of (\w+) (\d{4}), the estimated number of "
                         rf"scheduled deliveries was ({N})\.", c.strip())
            if m is None:
                raise Unreadable(f"{c!r} is not a dated sentence")
            hits.append(m.group(1) == month.group(1) and m.group(2) == month.group(2)
                        and near(num(m.group(3)), start))
        return one_hit(item, hits, "the model's value at the month x counts from",
                       f"; {start:g} at the end of {month.group(1)}")
    if "marble's height above the ground" in stem:
        drawn = Figure(item.figure).at_axis()
        hits = []
        for c in item.choices:
            t = c.strip()
            if "minimum" in t:
                hits.append(False)
                continue
            m = re.match(rf"The marble's height was ({N}) inches above the ground "
                         r"when it started moving\.", t)
            hits.append(bool(m) and near(num(m.group(1)), drawn, 1e-2))
        return one_hit(item, hits, "the drawn curve's height when x = 0",
                       f"; the picture reads {drawn:.3f}")
    if "metal ball's height" in stem:
        rule = re.search(r"f\(x\) = (.+?) gives a metal", stem).group(1)
        body = rule.replace("(1/", "(1/")
        arg, val = _extreme(body, 0.0, 40.0, False)
        hits = []
        for c in item.choices:
            m = re.match(rf"The metal ball's minimum height was ({N}) inches above "
                         r"the ground\.", c.strip())
            hits.append(bool(m) and near(num(m.group(1)), val, 1e-6))
        return one_hit(item, hits, "the least value the printed rule takes",
                       f"; the vertex is ({arg:.3f}, {val:.3f})")
    if "positive x-intercept" in stem:
        hits = [c.strip() == "The time at which the projectile hits the ground"
                for c in item.choices]
        return one_hit(item, hits, "an x-intercept is where the height is zero")
    hits = [c.strip().startswith("The unit price") and "revenue of $0" in c
            for c in item.choices]
    return one_hit(item, hits, "an x-intercept of a revenue model is a price")


# ---------------------------------------------------------- situations

def check_quad_word(item) -> str:
    """Rebuild the situation's equation from the stem, and solve it once."""
    stem = item.stem
    if "twice the width" in stem:
        area = stem_num(stem, rf"area of ({N}) square")
        test = lambda w: 2 * w * w == area                       # noqa: E731
        what = "the width whose doubled square is the printed area"
    elif "length of x units" in stem:
        off = stem_num(stem, rf"width of \(x {MINUS} ({N})\)")
        area = stem_num(stem, rf"area of ({N}) square units")
        test = lambda x: x * (x - off) == area                   # noqa: E731
        what = "the x whose rectangle has the printed area"
    elif "product of two positive integers" in stem:
        product = stem_num(stem, rf"integers is ({N})")
        off = stem_num(stem, rf"is ({N}) greater than")
        mult = 3 if "three times" in stem else 2
        test = lambda n: n > 0 and (mult * n + off) * n == product  # noqa: E731
        what = "the smaller integer of the printed product"
    elif "area of a triangle is" in stem and "square centimeters" in stem:
        area = stem_num(stem, rf"triangle is ({N}) square")
        off = stem_num(stem, rf"is ({N}) centimeters greater")
        test = lambda h: h > 0 and h * (h + off) == 2 * area      # noqa: E731
        what = "the height whose triangle has the printed area"
    else:
        raise Unreadable("this situation answers with a grid-in")
    all_distinct(item)
    hits = []
    for c in item.choices:
        v = num(c)
        hits.append(bool(test(v)))
    return one_hit(item, hits, what)


def check_build_expression(item) -> str:
    """The expression the situation asks for, checked at several values."""
    stem = item.stem
    if "area A, in square centimeters" in stem:
        d = stem_num(stem, rf"w\(w \+ ({N})\)")
        want = f"w + {d}"
        hits = [agree(c, want, variables=("w",)) for c in item.choices]
        return one_hit(item, hits, "the other factor of the printed area")
    if "product of a number" in stem:
        d = stem_num(stem, rf"is ({N}) more than x")
        want = f"x*(x + {d})"
        hits = [agree(c.split("=", 1)[1], want) for c in item.choices]
        return one_hit(item, hits, "the product the words describe")
    if "right rectangular prism" in stem:
        h = stem_num(stem, rf"height of ({N}) inches")
        d = stem_num(stem, rf"which is ({N}) inch")
        want = f"{h}*x*(x - {d})"
        hits = [agree(c.split("=", 1)[1], want) for c in item.choices]
        return one_hit(item, hits, "height times length times width")
    den = stem_num(item.stem, rf"6\(a/({N})\)²")
    want = f"4*a/{den}"
    hits = [agree(c, want, variables=("a",)) for c in item.choices]
    return one_hit(item, hits, "four times the cube's edge",
                   f"; the edge is a/{den}")


def check_factor_from_table(item) -> str:
    """A factor is forced only by a zero the table actually shows."""
    if not item.table:
        raise Unreadable("the item carries no table")
    rows = {num(x): num(y) for x, y in item.table[1:]}
    zeros = {x for x, y in rows.items() if y == 0}
    hits = []
    for c in item.choices:
        f = fn_of(c)
        roots = {x for x in rows if near(f(float(x)), 0.0, 1e-9)}
        others = [x for x in _linear_roots(c) if x not in rows]
        hits.append(bool(roots) and roots <= zeros and not others
                    and len(roots) == len(_linear_roots(c)))
    return one_hit(item, hits, "the factor whose every zero the table shows",
                   f"; the table's zeros are {sorted(zeros)}")


def _linear_roots(text: str) -> list:
    out = []
    for m in re.finditer(r"\(x\s*([+−-])\s*([\d.]+)\)", text):
        v = num(m.group(2))
        out.append(v if m.group(1) == "+" else -v)
    return [-r for r in out]


CHECKS = {
    "nlfunc.evaluate": check_evaluate,
    "nlfunc.exp_evaluate": check_evaluate,
    "nlfunc.solve_value": check_solve_value,
    "nlfunc.param_value": check_param_value,
    "nlfunc.y_intercept": check_y_intercept,
    "nlfunc.x_intercept": check_x_intercept,
    "nlfunc.graph_intercept": check_graph_intercept,
    "nlfunc.graph_context": check_graph_context,
    "nlfunc.graph_zeros": check_graph_zeros,
    "nlfunc.graph_equation": check_graph_equation,
    "nlfunc.exp_model": check_exp_model,
    "nlfunc.exp_period": check_exp_period,
    "nlfunc.exp_from_table": check_exp_from_table,
    "nlfunc.exp_offset": check_exp_offset,
    "nlfunc.exp_anchor": check_exp_anchor,
    "nlfunc.exp_reach": check_exp_reach,
    "nlfunc.exp_rate": check_exp_rate,
    "nlfunc.exp_two_points": check_exp_two_points,
    "nlfunc.exp_display": check_exp_display,
    "nlfunc.exp_rewrite": check_exp_rewrite,
    "nlfunc.exp_steps": check_exp_steps,
    "nlfunc.vertex_value": check_vertex_value,
    "nlfunc.vertex_symmetry": check_vertex_symmetry,
    "nlfunc.shift_max": check_shift_max,
    "nlfunc.quad_must_be_true": check_quad_must_be_true,
    "nlfunc.quad_fit": check_quad_fit,
    "nlfunc.interpret_value": check_interpret_value,
    "nlfunc.interpret_initial": check_interpret_initial,
    "nlfunc.interpret_rate": check_interpret_rate,
    "nlfunc.quad_feature": check_quad_feature,
    "nlfunc.quad_word": check_quad_word,
    "nlfunc.build_expression": check_build_expression,
    "nlfunc.factor_from_table": check_factor_from_table,
}

# Templates that only ever answer with a grid-in: there is no option set to
# read back, and saying so is better than a silent pass.
GRID_ONLY = ["nlfunc.abs_value", "nlfunc.exp_power_table", "nlfunc.zeros_constant"]


# --------------------------------------------------- proving it can fail

def broken(item, **changes):
    """A copy of a finished item with something wrong done to it."""
    bad = copy.deepcopy(item)
    for k, v in changes.items():
        setattr(bad, k, v)
    return bad


def first(name, want=lambda it: True):
    for seed in range(600):
        try:
            item = generate(name, seed)
        except ItemError:
            continue
        if item.fmt == "mcq" and want(item):
            return item
    raise RuntimeError(f"no usable {name} item to break")


def selftest() -> int:
    """A check nobody has seen fail is worth nothing.

    Six faults, one of each kind the assertions are for: the same model
    written a second way, an equivalent rewriting of an exponential's base, the
    right answer under the wrong letter, a figure spliced in from another item,
    a distractor moved inside what the picture can resolve, and a sentence
    given the other number the item prints.
    """
    cases = []

    # 1. a second correct answer: the key's own model, written as a fraction
    item = first("nlfunc.exp_model")
    i = keyed(item)
    lhs, rhs = item.choices[i].split("=", 1)
    m = re.match(rf"\s*({N})\(({N})\)\^([a-z])\s*$", rhs)
    if m is None:
        raise RuntimeError("could not rewrite the exponential model")
    a, b, var = num(m.group(1)), num(m.group(2)), m.group(3)
    twin = list(item.choices)
    twin[(i + 1) % 4] = f"{lhs}= {a}({b.numerator}/{b.denominator})^{var}"
    cases.append(("a second correct answer, the same model written as a fraction",
                  broken(item, choices=twin), check_exp_model))

    # 2. the key restated with its base and exponent scaled together
    item = first("nlfunc.exp_period", lambda it: "quarter years" in it.stem
                 or "months" in it.stem)
    i = keyed(item)
    lhs, rhs = item.choices[i].split("=", 1)
    m = re.match(rf"\s*({N})\(({N})\)\^\(([a-z])/({N})\)\s*$", rhs)
    if m is None:
        raise RuntimeError("could not rewrite the rescaled model")
    head, base, var, k = m.group(1), m.group(2), m.group(3), m.group(4)
    twin = list(item.choices)
    twin[(i + 2) % 4] = f"{lhs}= {head}(({base})^(1/{k}))^{var}"
    cases.append(("the key rewritten with the root taken into the base",
                  broken(item, choices=twin), check_exp_period))

    # 3. the right answer under the wrong letter
    item = first("nlfunc.evaluate")
    other = "ABCD"[(keyed(item) + 2) % 4]
    cases.append(("the key under the wrong letter",
                  broken(item, answer=other), check_evaluate))

    # 4. a figure spliced in from another item: the options no longer describe
    #    the curve that is drawn
    a = first("nlfunc.graph_intercept", lambda it: it.figure is not None)
    other_fig = next(it.figure for it in
                     (generate("nlfunc.graph_intercept", s) for s in range(1, 600))
                     if it.figure and it.figure != a.figure
                     and it.fmt == "mcq")
    cases.append(("a figure spliced in from another item",
                  broken(a, figure=other_fig), check_graph_intercept))

    # 5. a distractor moved to inside what the chart can resolve: three fifths
    #    of a gridline from the key, which no reader of the picture can separate
    item = first("nlfunc.graph_context", lambda it: "How many" in it.stem)
    i = keyed(item)
    grid = Figure(item.figure).grid_y()
    twin = list(item.choices)
    twin[(i + 1) % 4] = f"{int(num(item.choices[i]) + round(0.6 * grid)):,}"
    cases.append(("a distractor moved inside what the chart can resolve",
                  broken(item, choices=twin), check_graph_context))

    # 6. a sentence given the item's other printed number
    item = first("nlfunc.interpret_rate")
    i = keyed(item)
    twin = list(item.choices)
    other = (i + 1) % 4
    twin[other] = item.choices[i]
    twin[other] = twin[other].replace("brachiopod", "coral")
    cases.append(("the key repeated under another species name",
                  broken(item, choices=twin), check_interpret_rate))

    worst = 0
    for what, bad, checker in cases:
        try:
            checker(bad)
        except AssertionError as exc:
            print(f"  ok   caught {what}: {exc}")
            continue
        except Unreadable as exc:
            print(f" FAIL  {what} was not read at all: {exc}")
            worst = 1
            continue
        print(f" FAIL  {what} was not caught")
        worst = 1
    return worst


# ------------------------------------------------------------------ driver

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--draws", type=int, default=400,
                    help="seeds to try per template (default 400)")
    ap.add_argument("--template", action="append",
                    help="check only this template; repeatable")
    ap.add_argument("--selftest", action="store_true",
                    help="inject faulty option sets and check each is caught")
    ap.add_argument("--show", type=int, default=1,
                    help="how many failing items to print per template")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    names = args.template or list(CHECKS)

    worst, total = 0, 0
    for name in names:
        checker = CHECKS[name]
        made, bad, skipped, what = 0, 0, 0, ""
        for seed in range(args.draws):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            if item.fmt != "mcq":
                continue
            made += 1
            try:
                what = checker(item) or what
            except Unreadable as exc:
                skipped += 1
                if skipped <= args.show:
                    print(f"\n{name} seed {seed}: unreadable -- {exc}")
                    print(item.pretty())
            except AssertionError as exc:
                bad += 1
                if bad <= args.show:
                    print(f"\n{name} seed {seed}: {exc}")
                    print(item.pretty())
        total += made
        mark = "  ok  " if not (bad or skipped) else " FAIL "
        tail = f", {skipped} unreadable" if skipped else ""
        print(f"{mark} {name:<28} {made:>5,} items, {bad} defects{tail}   ({what})")
        worst |= 1 if (bad or skipped) else 0
    for name in GRID_ONLY:
        print(f"  --   {name:<28}     0 items   (grid-in only: no options to read)")
    print(f"\n{total:,} items read back")
    return worst


if __name__ == "__main__":
    sys.exit(main())
