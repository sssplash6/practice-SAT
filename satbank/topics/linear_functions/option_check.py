"""Read the four printed options back, and check only one of them is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct, because nothing in the engine reads a wrong
option as mathematics -- the wrong options are strings that `assemble_text`
shuffled and `_text_item` deduplicated by signature. An item with two right
answers therefore passes every gate the engine has.

This topic is exposed to that three ways. Its largest family prints
EQUATIONS, and two equations can be the same line written differently, so an
option set has to be decided by solving each option rather than by comparing
its text with the key's. Three templates print SENTENCES, where a distractor
can be a true statement about the model without being what the coefficient
means -- and where the number a sentence names has to be checked against a
number the item actually prints. And four templates hang the question on a
drawn line, which is only checked if something reads the picture -- both what
it says and how finely it can be read, since two options nearer together than
the gridlines can separate are two answers whichever one is keyed.

So this script parses the printed stem, the printed table, the printed options
and the SVG's own pixel geometry back into linear algebra, decides every option
from that alone, and asserts that exactly one option has the property the stem
asks for and that it is the keyed one. It imports no template, no renderer and
no solver: `generate` is used only to obtain the finished item, exactly as a
student would receive it.

    PYTHONPATH=. python3 satbank/topics/linear_functions/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 2500 --template lin.from_points
    PYTHONPATH=. python3 .../option_check.py --selftest

Exits non-zero on the first kind of defect it finds, and prints the item.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from fractions import Fraction as Q

from satbank.item import ItemError
from satbank.registry import generate

MINUS = "−"


class Unreadable(Exception):
    """The printed text is not something this reader understands.

    Raised, never swallowed: an option this file cannot read is an option it
    cannot clear, and the run reports it rather than passing quietly.
    """


# --------------------------------------------------- printed text -> numbers

def num(text) -> Q:
    """A printed number: 8, -11, 2,300, 9/7, 3.5, (3/4), $46.60, -(1/2)."""
    t = (str(text).replace(MINUS, "-").replace(",", "").replace(" ", "")
         .strip().lstrip("$").rstrip("."))
    if t.startswith("-(") and t.endswith(")"):
        t = "-" + t[2:-1]
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


# the fraction alternative comes first: `-7/6` must not be read as `-7`
N = r"(-?\d+/\d+|-?\d[\d,]*(?:\.\d+)?)"


def stem_num(text: str, pattern: str, group: int = 1) -> Q:
    m = re.search(pattern, text)
    if m is None:
        raise Unreadable(f"{pattern!r} is not in the printed text")
    return num(m.group(group))


# ------------------------------------------ printed text -> a linear side
#
# The reader is deliberately naive: it knows how an SAT page prints a linear
# expression and nothing else. It shares no code with `common.py`, which is
# the point -- a renderer that drops a minus sign has to be invisible to the
# renderer and visible here.

def split_terms(t: str) -> list[str]:
    """A printed side broken at its top-level + and -, signs kept."""
    out, depth, start = [], 0, 0
    for i, ch in enumerate(t):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch in "+-" and depth == 0 and i > start:
            out.append(t[start:i])
            start = i
    out.append(t[start:])
    return [p for p in out if p not in ("", "+", "-")]


# one printed term, in the five layouts this topic uses
SCALED_SUM = re.compile(r"\(?(-?[\d.]+(?:/[\d.]+)?)\)?\(([a-z])([+-])([a-z])\)")
OVER = re.compile(r"([\d.]*)([a-z])/([\d.]+)")                 # x/20, 3x/4, x/5.7
FRACVAR = re.compile(r"\(?(-?[\d.]+)/([\d.]+)\)?([a-z])?")     # (3/4)x, 9/7
NUMVAR = re.compile(r"\(?([\d.]*)\)?([a-z])")                  # 4x, x, (2)p
PLAIN = re.compile(r"\(?([\d.]+)\)?")                          # 41, 0.50


def side(text: str) -> tuple[dict, Q]:
    """One side of an equation as ({variable: coefficient}, constant).

    Handles every layout this topic prints: `-2x + 7`, `9.25 + 0.50x`,
    `(5/6)x - 2`, `82 + x/20`, `w/191`, `x/5.7`, `(1/84)x`, `4.2x`, and the
    scaled sum `35 - (1/2)(p + c)` the unit-relation options are written in.
    """
    t = text.replace(MINUS, "-").replace(",", "").replace(" ", "").strip()
    if not t:
        raise Unreadable(repr(text))
    coef: dict[str, Q] = {}
    const = Q(0)
    for piece in split_terms(t):
        sign = Q(-1) if piece[0] == "-" else Q(1)
        body = piece.lstrip("+-")
        if not body:
            raise Unreadable(f"{text!r} at {piece!r}")

        m = SCALED_SUM.fullmatch(body)
        if m:
            k = sign * num(m.group(1))
            inner = Q(1) if m.group(3) == "+" else Q(-1)
            coef[m.group(2)] = coef.get(m.group(2), Q(0)) + k
            coef[m.group(4)] = coef.get(m.group(4), Q(0)) + k * inner
            continue
        m = OVER.fullmatch(body)
        if m:
            v = sign * num(m.group(1) or "1") / num(m.group(3))
            coef[m.group(2)] = coef.get(m.group(2), Q(0)) + v
            continue
        m = FRACVAR.fullmatch(body)
        if m:
            v = sign * num(m.group(1)) / num(m.group(2))
            if m.group(3):
                coef[m.group(3)] = coef.get(m.group(3), Q(0)) + v
            else:
                const += v
            continue
        m = NUMVAR.fullmatch(body)
        if m:
            v = sign * (num(m.group(1)) if m.group(1) else Q(1))
            coef[m.group(2)] = coef.get(m.group(2), Q(0)) + v
            continue
        m = PLAIN.fullmatch(body)
        if m:
            const += sign * num(m.group(1))
            continue
        raise Unreadable(f"{text!r} at {piece!r}")
    return {v: c for v, c in coef.items() if c != 0}, const


def row(eq: str) -> tuple[dict, Q]:
    """A printed equation as the row (coefficients, constant), everything moved
    to the left of the equals sign. `d = 7m` and `-7m + d = 0` read alike."""
    if eq.count("=") != 1:
        raise Unreadable(eq)
    lhs, rhs = eq.split("=")
    lc, lk = side(lhs)
    rc, rk = side(rhs)
    for v, c in rc.items():
        lc[v] = lc.get(v, Q(0)) - c
    return {v: c for v, c in lc.items() if c != 0}, rk - lk


NAMED = re.compile(r"^\s*([A-Za-z])\s*\(\s*([a-z])\s*\)\s*$")


def as_function(option: str) -> tuple[str, Q, Q]:
    """`j(x) = -2x + 7`, `y = 9.25 + 0.50x`, `P = w/191` as (var, slope, b).

    The left side names the output -- a function call, or a bare letter that
    does not appear on the right. Anything else (`x = 4.2k`, `xk = 4.2`) is not
    a function of one variable and cannot be one of these options.
    """
    if option.count("=") != 1:
        raise Unreadable(option)
    lhs, rhs = option.split("=")
    coef, const = side(rhs)
    if len(coef) > 1:
        raise Unreadable(f"{option!r} has more than one variable on the right")
    m = NAMED.match(lhs)
    if m:
        out, arg = m.group(1), m.group(2)
        if coef and arg not in coef:
            raise Unreadable(f"{option!r} is not written in {arg!r}")
        var = arg
    else:
        out = lhs.strip()
        if not re.fullmatch(r"[A-Za-z]", out):
            raise Unreadable(f"{option!r} does not name a single output")
        if out in coef:
            raise Unreadable(f"{option!r} has {out!r} on both sides")
        var = next(iter(coef), "x")
    return var, coef.get(var, Q(0)), const


def line_of(option: str) -> tuple[Q, Q]:
    """The option's (slope, intercept), whatever it calls its variable."""
    _, m, b = as_function(option)
    return m, b


def point(text: str) -> tuple[Q, Q]:
    """`(2, 3)`, `(-4, 0)`."""
    m = re.fullmatch(r"\(([^,()]+),([^,()]+)\)", text.strip())
    if m is None:
        raise Unreadable(text)
    return num(m.group(1)), num(m.group(2))


def points_in(text: str) -> list[tuple[Q, Q]]:
    """Every ordered pair printed in a stem, in order."""
    return [(num(a), num(b))
            for a, b in re.findall(rf"\(\s*{N}\s*,\s*{N}\s*\)", text)]


# --------------------------------------------- a printed table -> its numbers

def columns(table) -> list[list[Q]]:
    """The table's two numeric series, whichever way round it is printed.

    `from_table` prints one row per point; `x_intercept` prints one row per
    series. Both end up as [xs, ys] -- and a header cell that is not a number
    is what tells them apart.
    """
    if not table or len(table) < 2:
        raise Unreadable("no table")
    if len(table[0]) == 2:                       # a row per point
        xs, ys = [], []
        for r in table[1:]:
            xs.append(num(r[0]))
            ys.append(num(r[1]))
        return [xs, ys]
    return [[num(c) for c in r[1:]] for r in table]   # a row per series


def fit(xs: list[Q], ys: list[Q]) -> tuple[Q, Q]:
    """The line through the first two rows -- which the rest must also lie on."""
    if len(xs) < 2 or xs[1] == xs[0]:
        raise Unreadable("the table does not pin a line down")
    m = (ys[1] - ys[0]) / (xs[1] - xs[0])
    b = ys[0] - m * xs[0]
    for x, y in zip(xs, ys):
        if m * x + b != y:
            raise Unreadable("the printed table is not linear")
    return m, b


# --------------------------------------- a printed expression with a letter

TOKEN = re.compile(r"\d+\.\d+|\d+|[a-z]|[-+*/()]")


def at(expr: str, letter: str, value: Q) -> Q:
    """The printed expression, evaluated with its letter set to a number.

    `(-45d - 12)/(20d)` at d = 2. A four-line recursive-descent parser rather
    than `eval`: it reads only numbers, the one letter, brackets and the four
    operators, every literal is an exact Fraction, and implicit multiplication
    (`45d`, `20d`, `2(x + 1)`) is handled where it is written.
    """
    t = expr.replace(MINUS, "-").replace(",", "").replace(" ", "").strip()
    toks = TOKEN.findall(t)
    if "".join(toks) != t:
        raise Unreadable(f"{expr!r} is not a plain arithmetic expression")
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def atom() -> Q:
        nonlocal pos
        tok = peek()
        if tok is None:
            raise Unreadable(f"{expr!r} ends early")
        if tok == "(":
            pos += 1
            v = add()
            if peek() != ")":
                raise Unreadable(f"{expr!r} has an unclosed bracket")
            pos += 1
            return v
        if tok == "-":
            pos += 1
            return -atom()
        if tok == "+":
            pos += 1
            return atom()
        pos += 1
        if tok == letter:
            return value
        if re.fullmatch(r"[a-z]", tok):
            raise Unreadable(f"{expr!r} mentions {tok!r}, not {letter!r}")
        return Q(tok)

    def mul() -> Q:
        nonlocal pos
        v = atom()
        while True:
            tok = peek()
            if tok in ("*", "/"):
                pos += 1
                rhs = atom()
                if tok == "/":
                    if rhs == 0:
                        raise Unreadable(f"{expr!r} divides by zero")
                    v /= rhs
                else:
                    v *= rhs
            elif tok is not None and (tok == "(" or re.fullmatch(r"[a-z0-9.]+", tok)):
                v *= atom()                      # 45d, 20d, 2(p + c)
            else:
                return v

    def add() -> Q:
        nonlocal pos
        v = mul()
        while peek() in ("+", "-"):
            op = toks[pos]
            pos += 1
            v = v + mul() if op == "+" else v - mul()
        return v

    v = add()
    if pos != len(toks):
        raise Unreadable(f"{expr!r} has trailing text")
    return v


# ------------------------------------------ a drawn figure -> the drawn line

def line_from_grid(svg: str) -> tuple[Q, Q]:
    """The drawn line as (slope, intercept), read out of a coordinate grid.

    The two axes locate the origin in pixels and the spacing of the gridlines
    gives the pixels per unit. Nothing about the item's parameters is
    consulted: this is what a reader with a ruler would get, so it checks the
    picture against the options rather than the options against each other.
    """
    ax = re.findall(r'<line class="ax" x1="([^"]+)" y1="([^"]+)" '
                    r'x2="([^"]+)" y2="([^"]+)"', svg)
    horizontal = [a for a in ax if a[1] == a[3]]
    vertical = [a for a in ax if a[0] == a[2]]
    if len(horizontal) != 1 or len(vertical) != 1:
        raise Unreadable("the axes are not one horizontal and one vertical")
    y0, x0 = Q(horizontal[0][1]), Q(vertical[0][0])
    gr = re.findall(r'<line class="gr" x1="([^"]+)" y1="[^"]+" '
                    r'x2="([^"]+)" y2="[^"]+"', svg)
    xs = sorted({Q(a) for a, b in gr if a == b})
    gaps = {b - a for a, b in zip(xs, xs[1:])}
    if len(gaps) != 1:
        raise Unreadable("the gridlines are not evenly spaced")
    px = gaps.pop()
    seg = re.findall(r'<line class="sg" x1="([^"]+)" y1="([^"]+)" '
                     r'x2="([^"]+)" y2="([^"]+)"', svg)
    if len(seg) != 1:
        raise Unreadable(f"{len(seg)} lines drawn, not one")
    x1, ya, x2, yb = seg[0]
    ax1, ay1 = (Q(x1) - x0) / px, (y0 - Q(ya)) / px
    ax2, ay2 = (Q(x2) - x0) / px, (y0 - Q(yb)) / px
    if ax1 == ax2:
        raise Unreadable("a vertical drawn line has no slope")
    m = (ay2 - ay1) / (ax2 - ax1)
    return m, ay1 - m * ax1


def line_from_chart(svg: str) -> tuple[float, float, float, float]:
    """The plotted line, read out of a labelled chart, with what it can resolve.

    Returns (slope, intercept, gridline gap, run). A chart's axes sit at the
    edge of the frame rather than at the origin, so the scale comes from the
    printed tick labels: two on each axis fix the affine map from pixels back
    to the quantities the axes are named for.

    The gap between the horizontal gridlines is how finely a reader can take a
    value off the picture, and the run is how far apart the two plotted ends
    are, which is what a rate read off the picture is divided by. Both come out
    of the drawing, not out of the item.
    """
    xt = [(float(x), float(lab)) for x, lab in re.findall(
        r'<text class="lb" x="([^"]+)" y="[^"]+" text-anchor="middle">'
        r'(-?[\d.]+)</text>', svg)]
    yt = [(float(y), float(lab)) for y, lab in re.findall(
        r'<text class="lb" x="[^"]+" y="([^"]+)" text-anchor="end">'
        r'(-?[\d.]+)</text>', svg)]
    if len(xt) < 2 or len(yt) < 2:
        raise Unreadable("too few tick labels to fix the scale")

    def mapper(ticks, shift=0.0):
        (p1, v1), (p2, v2) = ticks[0], ticks[-1]
        if p1 == p2:
            raise Unreadable("two tick labels at one pixel")
        k = (v2 - v1) / (p2 - p1)
        return lambda p: v1 + (p - p1 - shift) * k

    fx = mapper(xt)
    fy = mapper([(p - 4, v) for p, v in yt])       # the label sits 4px low
    pts = re.findall(r'<polyline class="ln" points="([^"]+)"', svg)
    if len(pts) != 1:
        raise Unreadable(f"{len(pts)} polylines, not one")
    coords = [tuple(float(c) for c in p.split(",")) for p in pts[0].split()]
    (px1, py1), (px2, py2) = coords[0], coords[-1]
    x1, y1, x2, y2 = fx(px1), fy(py1), fx(px2), fy(py2)
    if x1 == x2:
        raise Unreadable("a vertical plotted line has no slope")
    m = (y2 - y1) / (x2 - x1)
    gaps = sorted({round(b - a, 9) for a, b in
                   zip(sorted(v for _, v in yt), sorted(v for _, v in yt)[1:])})
    if not gaps:
        raise Unreadable("a single gridline gives no scale")
    return m, y1 - m * x1, gaps[0], abs(x2 - x1)


def figure_carries_numbers(svg: str | None) -> bool:
    """True when the picture has a scale a reader could take a number off.

    A pair of bare axes with a line across them says which way the quantity
    goes and nothing else: any sentence that names an amount is unanswerable
    against it.
    """
    if not svg:
        return False
    return bool(re.search(r'<text class="lb"[^>]*>\s*-?[\d.]', svg))


def near(a, b, rel: float = 0.004, floor: float = 1e-7) -> bool:
    a, b = float(a), float(b)
    return abs(a - b) <= max(floor, rel * max(abs(a), abs(b)))


# ------------------------------------------------------------- the verdict

def keyed(item) -> int:
    return "ABCD".index(item.answer)


def one_hit(item, hits: list[bool], what: str, detail: str = "") -> str:
    """Both halves. `hits.count(True) == 1` catches the second right answer;
    `hits[keyed]` catches the right answer under the wrong letter. Checking
    only the second is what the engine already does."""
    if hits.count(True) != 1:
        raise AssertionError(
            f"{hits.count(True)} of the four options are correct{detail}")
    if not hits[keyed(item)]:
        raise AssertionError(f"the keyed option is not the correct one{detail}")
    return what


def lines(item) -> list[tuple[Q, Q] | None]:
    """Every option as a line, with `None` for one that is not a function."""
    out = []
    for c in item.choices:
        try:
            out.append(line_of(c))
        except (Unreadable, ZeroDivisionError):
            out.append(None)
    return out


def numerals(item) -> list[Q | None]:
    out = []
    for c in item.choices:
        try:
            out.append(num(c))
        except Unreadable:
            out.append(None)
    return out


def distinct_numbers(item) -> str:
    """Four bare numbers, and no two of them the same number.

    This is the whole of what an option set of four numbers can get wrong that
    `audit` does not already catch: `audit` re-derives the key, and four
    distinct numbers cannot hold two right answers -- but two options that
    print the same value, or round to it, can and do.
    """
    got = numerals(item)
    if any(v is None for v in got):
        bad = [c for c, v in zip(item.choices, got) if v is None]
        raise Unreadable(f"an option is not a bare number: {bad!r}")
    for i in range(4):
        for j in range(i + 1, 4):
            if got[i] == got[j]:
                raise AssertionError(
                    f"options {'ABCD'[i]} and {'ABCD'[j]} are the same number "
                    f"({item.choices[i]!r} and {item.choices[j]!r})")
    return "four distinct numbers"


def one_number(item, want: Q, what: str) -> str:
    """Exactly one printed option is the value the item's own text gives.

    The distinctness check runs first: two options that print the same number
    are a defect whichever of them is keyed, and a formatter that rounds two
    different values into one string is the way it happens.
    """
    distinct_numbers(item)
    got = numerals(item)
    hits = [v is not None and v == want for v in got]
    return one_hit(item, hits, what, f"; the text gives {want}")


# ============================================================ the checks
#
# Every check has the same shape: read the question out of the printed stem,
# table or figure; decide all four options from their own printed text; demand
# exactly one hit and demand it is the keyed one.


# ------------------------------------------------------ lines written down

def check_from_points(item) -> str:
    """Exactly one printed equation passes through both printed points."""
    pts = points_in(item.stem)
    if len(pts) != 2:
        raise Unreadable(f"{len(pts)} points in the stem, not two")
    hits = [ln is not None and all(ln[0] * x + ln[1] == y for x, y in pts)
            for ln in lines(item)]
    return one_hit(item, hits, "through both printed points")


SLOPE_PHRASE = rf"slope (?:of )?{N}"


def check_define_line(item) -> str:
    """Exactly one printed equation meets the conditions the stem states."""
    stem = item.stem
    values = [(num(a), num(b)) for a, b in
              re.findall(rf"[A-Za-z]\({N}\) = {N}", stem)]
    pts = points_in(stem)
    m = re.search(SLOPE_PHRASE, stem)
    slope = num(m.group(1)) if m else None
    if not values and not pts:
        raise Unreadable("the stem states no conditions on the line")

    def ok(ln):
        if ln is None:
            return False
        if slope is not None and ln[0] != slope:
            return False
        return all(ln[0] * x + ln[1] == y for x, y in values + pts)

    hits = [ok(ln) for ln in lines(item)]
    what = "the stated slope and value" if slope is not None else "both stated values"
    return one_hit(item, hits, what)


def check_from_table(item) -> str:
    """Exactly one printed equation fits every row of the printed table."""
    xs, ys = columns(item.table)
    hits = [ln is not None and all(ln[0] * x + ln[1] == y for x, y in zip(xs, ys))
            for ln in lines(item)]
    return one_hit(item, hits, "fits every row of the table")


def check_x_intercept(item) -> str:
    """Exactly one printed point is where the line meets the x-axis."""
    if item.table:
        m, b = fit(*columns(item.table))
    elif "h(x) = f(x) + g(x)" in item.stem:
        mm = re.search(r"f\(x\) = (.+?) and g\(x\) = (.+?)\. If the function h",
                       item.stem)
        if mm is None:
            raise Unreadable("the two summed rules are not printed")
        c1, k1 = side(mm.group(1))
        c2, k2 = side(mm.group(2))
        m = c1.get("x", Q(0)) + c2.get("x", Q(0))
        b = k1 + k2
    else:
        m = stem_num(item.stem, SLOPE_PHRASE)
        b = point(re.search(rf"y-intercept of (\({N}, {N}\))", item.stem).group(1))[1]
    if m == 0:
        raise Unreadable("a flat line has no single x-intercept")
    hits = []
    for c in item.choices:
        try:
            x, y = point(c)
        except Unreadable:
            hits.append(False)
            continue
        hits.append(y == 0 and m * x + b == 0)
    return one_hit(item, hits, "the zero of the printed line",
                   f"; the line is y = {m}x + {b}")


def check_y_intercept(item) -> str:
    """From a rule, the constant term; from a picture, the drawn crossing."""
    if item.figure:
        m, b = line_from_grid(item.figure)
        hits = []
        for c in item.choices:
            try:
                hits.append(point(c) == (Q(0), b))
            except Unreadable:
                hits.append(False)
        return one_hit(item, hits, "the drawn line's y-intercept",
                       f"; the drawn line is y = {m}x + {b}")
    body = re.search(r"defined by [A-Za-z]\([a-z]\) = (.+?)\. What", item.stem)
    if body is None:
        raise Unreadable("no rule printed in the stem")
    _, b = side(body.group(1))
    return one_number(item, b, "the constant term of the printed rule")


# --------------------------------------------------- lines from a situation

# Each entry is a marker that identifies the printed situation and the pattern
# pair that reads its rate and its starting amount straight out of the words.
SITUATIONS = [
    ("roller-coaster car", rf"constant rate of {N} feet per second",
     rf"is {N} feet above the ground"),
    ("minimum hourly wage", rf"increase by \${N} on the first day",
     rf"minimum hourly wage was \${N}"),
    ("white whale", rf"increased an average of {N} cm per month",
     rf"was {N} centimeters"),
    ("repair a refrigerator", rf"charges \${N} per hour for labor",
     rf"plus \${N} for parts"),
    ("gym charges", rf"plus \${N} for each month",
     rf"enrollment fee of \${N}"),
    ("seedling was", rf"grew an average of {N} cm each week",
     rf"was {N} centimeters"),
    ("storage tank held", rf"constant rate of {N} gallons per minute",
     rf"held {N} gallons"),
    ("printing shop", rf"then \${N} for each poster",
     rf"setup fee of \${N}"),
    ("rides his bike", rf"average rate of {N} minutes per mile", None),
    ("machine fills", rf"fills {N} bottles each minute", None),
    ("conversion uses", rf"uses {N} centimeters for every inch", None),
]


def model_from_stem(stem: str) -> tuple[Q, Q]:
    """The (rate, starting amount) the printed situation itself demands."""
    m = re.search(rf"The number y is {N} (less|more) than the number x", stem)
    if m:
        b = num(m.group(1))
        return Q(1), (-b if m.group(2) == "less" else b)
    for marker, rate, start in SITUATIONS:
        if marker in stem:
            return stem_num(stem, rate), (stem_num(stem, start) if start else Q(0))
    raise Unreadable("an unfamiliar situation")


def check_model_equation(item) -> str:
    """Exactly one printed equation is the line the situation describes."""
    m, b = model_from_stem(item.stem)
    hits = [ln == (m, b) for ln in lines(item)]
    return one_hit(item, hits, "the situation's own rate and starting amount",
                   f"; the situation is y = {m}x + {b}")


def check_per_unit(item) -> str:
    """A rate stated as `one unit per N`, which prints as a division."""
    stem = item.stem
    m = re.search(rf"For every {N} \w+ .*?(lowered by|loses|rises) about 1", stem)
    if m:
        n = num(m.group(1))
        start = stem_num(stem, rf"(?:is|holds) {N} (?:degrees|acre-feet|meters)")
        slope = (Q(1) / n) if m.group(2) == "rises" else -(Q(1) / n)
        want = (slope, start)
    else:
        n = stem_num(stem, rf"(?:cover|treats) {N} square feet")
        k = 2 if " twice?" in stem or "twice" in stem else 3
        want = (Q(k) / n, Q(0))
    hits = [ln == want for ln in lines(item)]
    return one_hit(item, hits, "the per-unit rate the words state",
                   f"; the model is y = {want[0]}x + {want[1]}")


def check_tiered(item) -> str:
    """Exactly one option charges what the two printed prices come to.

    The option is tested as a function at several group sizes rather than
    matched against a form, so an equivalent rewriting would still be caught.
    """
    stem = item.stem
    m = re.search(rf"\${N} for the first day and \${N} for each additional day", stem)
    if m:
        a, b, k = num(m.group(1)), num(m.group(2)), Q(1)
    else:
        m = re.search(rf"charges \${N} per (?:person|visitor) for the first {N} "
                      rf"(?:people|visitors) and \${N} for each additional", stem)
        if m is None:
            raise Unreadable("an unfamiliar tiered-price situation")
        a, k, b = num(m.group(1)), num(m.group(2)), num(m.group(3))

    def total(n):
        return k * a + b * (n - k)

    tries = [k, k + 1, k + 4, k + 10]
    hits = [ln is not None and all(ln[0] * n + ln[1] == total(n) for n in tries)
            for ln in lines(item)]
    return one_hit(item, hits, "the two printed prices at several sizes")


def check_two_points(item) -> str:
    """Predict a third reading, or write the model the two readings give."""
    stem = item.stem
    if item.table:
        (x1, y1), (x2, y2) = [(num(r[0]), num(r[1])) for r in item.table[1:]]
    else:
        m = re.search(rf"(?:from|was) {N} (?:million barrels|tons|units) in {N} to "
                      rf"{N} (?:million barrels|tons|units) in {N}", stem)
        if m:
            y1, x1, y2, x2 = (num(m.group(i)) for i in (1, 2, 3, 4))
        else:
            m = re.search(rf"rose from {N} tons in {N} to {N} tons in {N}", stem)
            if m is None:
                return check_predict(item)
            y1, x1, y2, x2 = (num(m.group(i)) for i in (1, 2, 3, 4))
    if x2 == x1:
        raise Unreadable("the two readings share an input")
    m = (y2 - y1) / (x2 - x1)
    hits = [ln == (m, y1) for ln in lines(item)]
    return one_hit(item, hits, "the rate and start the two readings give",
                   f"; the model is y = {m}t + {y1}")


def check_predict(item) -> str:
    """The third reading the two printed readings predict."""
    stem = item.stem
    m = re.search(rf"was {N} thousand in {N}, {N} thousand in {N}, and x thousand "
                  rf"in {N}", stem)
    if m:
        y1, x1, y2, x2, x3 = (num(m.group(i)) for i in range(1, 6))
    else:
        m = re.search(rf"demand was {N} units when the selling price was \${N} per "
                      rf"unit, and the demand was {N} units when the selling price "
                      rf"was \${N} per unit.*?price is \${N}", stem, re.S)
        if m is None:
            raise Unreadable("an unfamiliar two-reading situation")
        y1, x1, y2, x2, x3 = (num(m.group(i)) for i in range(1, 6))
    if x2 == x1:
        raise Unreadable("the two readings share an input")
    slope = (y2 - y1) / (x2 - x1)
    exact = y1 + slope * (x3 - x1)
    if "nearest whole number" in stem:
        want = Q(round(exact))
        if abs(exact - want) == Q(1, 2):
            raise Unreadable("a half-way value rounds ambiguously")
        return one_number(item, want, "the rounded prediction")
    return one_number(item, exact, "the predicted reading")


# ------------------------------------------------------ a table of units

def check_unit_relation(item) -> str:
    """The energy table: a conversion factor, or one variable in terms of two.

    Both modes test the printed option as a *relation*, at several values, so
    `xk = 4.2` -- true at x = 1 and nowhere else -- is not mistaken for a
    conversion, and a rewriting of the key would still be caught.
    """
    rows_ = item.table[1:]
    per = {r[0].lower(): (num(r[1]), num(r[2])) for r in rows_}
    if "which best represents the relationship" in item.stem:
        cal, kj = per["protein"]
        ratio = kj / cal
        hits = []
        for c in item.choices:
            try:
                coef, const = row(c)
            except (Unreadable, ZeroDivisionError):
                hits.append(False)
                continue
            if set(coef) != {"x", "k"} or const != 0:
                hits.append(False)
                continue
            # k as a function of x, tested away from the origin as well
            if coef.get("k", Q(0)) == 0:
                hits.append(False)
                continue
            got = [-coef["x"] / coef["k"] * t for t in (Q(1), Q(2), Q(7))]
            hits.append(all(near(g, ratio * t, rel=0.02)
                            for g, t in zip(got, (Q(1), Q(2), Q(7)))))
        return one_hit(item, hits, "k as the table's own multiple of x",
                       f"; the table gives {float(ratio):.3f} kilojoules per calorie")

    total = stem_num(item.stem, rf"If the {N} food calories")
    ap, _ = per["protein"]
    af, _ = per["fat"]
    ac, _ = per["carbohydrate"]
    hits = []
    for c in item.choices:
        try:
            coef, const = row(c)
        except (Unreadable, ZeroDivisionError):
            hits.append(False)
            continue
        if set(coef) != {"p", "f", "c"}:
            hits.append(False)
            continue
        # the option and the table's own energy sum must be the same plane
        lead = coef["f"]
        ratio = af / lead
        hits.append(coef["p"] * ratio == ap and coef["c"] * ratio == ac
                    and const * ratio == total)
    return one_hit(item, hits, "the same plane as the table's energy sum",
                   f"; the sum is {ap}p + {af}f + {ac}c = {total}")


def check_parameter_intercept(item) -> str:
    """An x-intercept with a letter in it, decided by evaluating the letter."""
    m = re.search(rf"f\(x\) = {N}([a-z])\({N}x \+ {N}\) \+ {N}", item.stem)
    if m is None:
        raise Unreadable("the stem is not the parameterised rule")
    c, letter, a, b, e = (num(m.group(1)), m.group(2), num(m.group(3)),
                          num(m.group(4)), num(m.group(5)))
    k = stem_num(item.stem, rf"y = f\(x\) \+ {N}")
    tries = [Q(1), Q(2), Q(3), Q(-1), Q(5), Q(1, 2)]
    hits = []
    for choice in item.choices:
        mm = re.fullmatch(r"\((.+),\s*0\)", choice.strip())
        if mm is None:
            hits.append(False)
            continue
        ok = True
        for v in tries:
            want = -(c * b * v + e + k) / (c * a * v)
            try:
                got = at(mm.group(1), letter, v)
            except Unreadable:
                ok = False
                break
            if got != want:
                ok = False
                break
        hits.append(ok)
    return one_hit(item, hits, f"the x-intercept at several values of {letter}")


def check_affine_conversion(item) -> str:
    """The printed conversion formula, run forwards or backwards."""
    m = re.search(rf"\({N}/{N}\)\(x - {N}\) \+ {N}", item.stem)
    if m:
        p, qd, s, t = (num(m.group(i)) for i in range(1, 5))
        delta = stem_num(item.stem, rf"increased by {N} kelvins")
        return one_number(item, p / qd * delta, "the scaled change")
    m = re.search(rf"h = {N}\(v - {N}\)/{N} \+ {N}", item.stem)
    if m is None:
        raise Unreadable("no conversion formula printed")
    p, s, qd, t = (num(m.group(i)) for i in range(1, 5))
    value = stem_num(item.stem, rf"temperature of {N} degrees Fahrenheit")
    return one_number(item, (value - t) * qd / p + s, "the inverted conversion")


# ------------------------------------------------------- lines that are drawn

# what a reader can take off a drawn line: four tenths of the gap between the
# gridlines for a value, and that divided by the run for a rate, since a rate
# read off a picture is a difference of two such readings over the distance
# between them. A distractor inside that is not a wrong answer -- it is the
# same reading, printed twice.
READ = 0.4


def check_graph_read(item) -> str:
    """The options must agree with the picture, not merely with each other.

    And they must be far enough apart on the picture's own scale for a reader
    to choose between them, which is the thing a graph item can get wrong that
    no amount of re-deriving the key would show.
    """
    m, b, gap, run = line_from_chart(item.figure)
    if "equations correctly relates" in item.stem:
        hits = []
        for ln in lines(item):
            hits.append(ln is not None
                        and abs(float(ln[0]) - m) < READ * gap / run
                        and abs(float(ln[1]) - b) < READ * gap)
        return one_hit(item, hits, "the drawn line as an equation",
                       f"; the drawn line is y = {m:.4f}x + {b:.4f}")
    if "per second" in item.stem or "each additional mile" in item.stem:
        want, tol, what = m, READ * gap / run, "the drawn rate"
    else:
        x = stem_num(item.stem, rf"(?:pressure is|temperature is) {N} "
                                rf"(?:atmospheres|kelvins)\?")
        want, tol = m * float(x) + b, READ * gap
        what = "the drawn value at the stated input"
    distinct_numbers(item)
    got = numerals(item)
    hits = [v is not None and abs(float(v) - want) < tol for v in got]
    return one_hit(item, hits, what,
                   f"; the picture gives {want:.4f}, and a reader can tell "
                   f"{tol:.4f} apart on it")


def check_graph_shifted(item) -> str:
    """The drawn line is y = f(x) - k, so f is the drawn line lifted by k."""
    m, c = line_from_grid(item.figure)
    k = stem_num(item.stem, rf"y = [a-z]\(x\) - {N} is shown")
    want = (m, c + k)
    hits = [ln == want for ln in lines(item)]
    return one_hit(item, hits, "the drawn line lifted by the printed shift",
                   f"; the drawn line is y = {m}x + {c} and the shift is {k}")


# ----------------------------------------------------- rules written down

def printed_rule(stem: str) -> tuple[str, Q, Q]:
    """The linear rule the stem prints, as (variable, slope, constant)."""
    for pat in (r"defined by (?:the equation )?[A-Za-z]\([a-z]\) = (.+?)(?:\.|,| For | What)",
                r"^[A-Za-z]\([a-z]\) = (.+?) The function",
                r"^If y = (.+?), what",
                r"If [A-Za-z] is the function defined by [A-Za-z]\([a-z]\) = (.+?), what"):
        m = re.search(pat, stem)
        if m:
            body = m.group(1).strip()
            break
    else:
        raise Unreadable("no rule printed in the stem")
    mm = re.fullmatch(r"\((.+)\)/([\d.,]+)", body)
    if mm:
        coef, const = side(mm.group(1))
        d = num(mm.group(2))
        coef = {v: c / d for v, c in coef.items()}
        const = const / d
    else:
        coef, const = side(body)
    if len(coef) != 1:
        raise Unreadable(f"{body!r} is not linear in one variable")
    var = next(iter(coef))
    return var, coef[var], const


def check_evaluate(item) -> str:
    """Exactly one option is the printed rule evaluated at the printed input."""
    var, m, b = printed_rule(item.stem)
    x = None
    for pat in (rf"when {var} = {N}", rf"value of [A-Za-z]\({N}\)"):
        mm = re.search(pat, item.stem)
        if mm:
            x = num(mm.group(1))
            break
    if x is None:
        raise Unreadable("the stem does not say where to evaluate")
    return one_number(item, m * x + b, "the rule at the printed input")


def check_table_facts(item) -> str:
    """The table pins a line down; the question asks it for one number."""
    xs, ys = columns(item.table)
    m, b = fit(xs, ys)
    stem = item.stem
    if "value of b?" in stem:
        return one_number(item, b, "the constant term of the table's line")
    if "value of m?" in stem:
        return one_number(item, m, "the slope of the table's line")
    if "value of a - b?" in stem:
        return one_number(item, m - b, "a - b for the table's line")
    mm = re.search(rf"value of [A-Za-z]\({N}\)\?", stem) or \
        re.search(rf"passes through the point \({N}, a\)", stem)
    if mm is None:
        raise Unreadable("an unfamiliar question about the table")
    x = num(mm.group(1))
    return one_number(item, m * x + b, "the table's line at the asked input")


VAR_TERM = re.compile(r"(-?[\d.,]+|[a-z])?([a-z])")


def check_coefficient(item) -> str:
    """One coefficient is a letter; the printed function values pin it down.

    The rule is read as two printed terms -- a variable term and a constant
    term -- either of which may be a letter rather than a number. Whichever is
    a letter is solved for from the values the stem states, and the question is
    then answered from the rule that comes out.
    """
    stem = item.stem
    body = re.search(r"defined (?:by|as) [A-Za-z]\([a-z]\) = (.+?),? where", stem) or \
        re.search(r"^[A-Za-z]\([a-z]\) = (.+?) For the linear", stem)
    if body is None:
        raise Unreadable("no rule printed in the stem")
    parts = [p.strip() for p in body.group(1).split(" + ")]
    if len(parts) != 2:
        raise Unreadable(f"{body.group(1)!r} is not a variable term plus a constant")
    vt = VAR_TERM.fullmatch(parts[0])
    if vt is None or vt.group(2) == vt.group(1):
        raise Unreadable(f"{parts[0]!r} is not a variable term")
    written = vt.group(1) or ""
    slope_letter = written if written.isalpha() and written else None
    slope = None if (slope_letter or not written) else num(written)
    const_letter = parts[1] if parts[1].isalpha() else None
    const = None if const_letter else num(parts[1])

    known = [(num(a), num(b)) for a, b in re.findall(rf"[A-Za-z]\({N}\) = {N}", stem)]
    if not known:
        raise Unreadable("no function value printed")
    if const is None:
        if slope is None:
            raise Unreadable("two unknowns and no way to separate them")
        const = known[0][1] - slope * known[0][0]
    if slope is None:
        pinned = next(((x, y) for x, y in known if x != 0), None)
        if pinned is None:
            raise Unreadable("the printed values do not pin the slope down")
        slope = (pinned[1] - const) / pinned[0]
    for x, y in known:
        if slope * x + const != y:
            raise AssertionError(f"the stem's own values disagree: the rule gives "
                                 f"{slope * x + const} at {x}, not {y}")
    ask = re.search(rf"value of [A-Za-z]\({N}\)\?", stem)
    if ask:
        x2 = num(ask.group(1))
        return one_number(item, slope * x2 + const, "the rule at the second input")
    asked = re.search(r"value of ([a-z]) \?", stem)
    if asked is None:
        raise Unreadable("the stem does not say what it is asking for")
    if asked.group(1) == slope_letter:
        return one_number(item, slope, "the slope the printed values pin down")
    if asked.group(1) == const_letter:
        return one_number(item, const, "the constant the printed values pin down")
    raise Unreadable(f"the stem asks for {asked.group(1)!r}, which is not a letter "
                     f"in the printed rule")


def check_combine(item) -> str:
    """Two function values put together, both rules printed in the stem."""
    stem = item.stem
    m = re.search(rf"f\(x\) = \(x \+ {N}\)/{N} .*?value of f\({N}\) - f\({N}\)", stem, re.S)
    if m:
        c, d, p, qv = (num(m.group(i)) for i in range(1, 5))
        return one_number(item, (p + c) / d - (qv + c) / d, "the printed difference")
    m = re.search(rf"f\(x\) = x \+ {N} and g\(x\) = (.+?), what is the value of "
                  rf"{N}f\({N}\) - (?:{N})?g\({N}\)", stem)
    if m is None:
        raise Unreadable("an unfamiliar combination")
    c = num(m.group(1))
    gcoef, gconst = side(m.group(2))
    d = gcoef.get("x", Q(0))
    af, p = num(m.group(3)), num(m.group(4))
    bg = num(m.group(5)) if m.group(5) else Q(1)
    p2 = num(m.group(6))
    return one_number(item, af * (p + c) - bg * (d * p2 + gconst),
                      "the printed combination")


def check_inner_scale(item) -> str:
    """f(cx) = x + d, asked at a point or asked for the scale."""
    stem = item.stem
    m = re.search(rf"if f\((.+?)\) = (.+?) for all values of x, what is the value of "
                  rf"f\({N}\)", stem)
    if m:
        arg, _ = side(m.group(1))
        c = arg.get("x", Q(0))
        icoef, d = side(m.group(2))
        if c == 0 or icoef.get("x", Q(0)) != 1:
            raise Unreadable("the inner rule is not x + d")
        k = num(m.group(3))
        return one_number(item, k / c + d, "the value through the scaled argument")
    m = re.search(rf"f\(cx\) = (.+?) for all values of x, where c is a positive "
                  rf"constant. If f\({N}\) = {N}", stem)
    if m is None:
        raise Unreadable("an unfamiliar scaled-argument item")
    icoef, d = side(m.group(1))
    k, value = num(m.group(2)), num(m.group(3))
    if value == d:
        raise Unreadable("the scale is not pinned down")
    return one_number(item, k / (value - d), "the scale the stated value pins down")


# ---------------------------------------------------- a model in words

VALUE_SITUATIONS = [
    ("rented a truck", rf"initial fee of \${N}", rf"additional \${N} per mile",
     rf"driven {N} miles"),
    ("savings account", rf"there was \${N} in that savings",
     rf"deposits \${N} in a savings", rf"end of the {N}(?:st|nd|rd|th) week"),
    ("worker bumblebee", rf"adding {N} to", r"to (\w+) times the body weight",
     rf"body weight of {N} grams"),
    ("P. ohioensis", rf"y = {N}x \+ {N}", None, rf"has {N} worker ants"),
    ("scuba diver", rf"sea level is {N} pounds", rf"increases by {N} psi",
     rf"at {N} feet below"),
    ("surface water temperature", rf"f\(x\) = {N} - {N}x", None,
     rf"on the {N}(?:st|nd|rd|th) day"),
]

WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
         "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}


def check_model_value(item) -> str:
    """A model stated in words, evaluated forward or run back for the input."""
    stem = item.stem
    m = re.search(rf"([TC]) = {N} \+ {N}[hn].*?(?:total take-home pay was|total cost "
                  rf"was) \${N}", stem, re.S)
    if m:
        b, rate, total = num(m.group(2)), num(m.group(3)), num(m.group(4))
        if rate == 0:
            raise Unreadable("a zero rate cannot be inverted")
        return one_number(item, (total - b) / rate, "the input the total implies")
    for marker, bp, mp, xp in VALUE_SITUATIONS:
        if marker not in stem:
            continue
        if marker == "P. ohioensis":
            rate, b = stem_num(stem, bp), stem_num(stem, bp, 2)
        elif marker == "surface water temperature":
            b, rate = stem_num(stem, bp), -stem_num(stem, bp, 2)
        elif marker == "worker bumblebee":
            b = stem_num(stem, bp)
            word = re.search(mp, stem).group(1)
            rate = Q(WORDS[word]) if word in WORDS else num(word)
        else:
            b, rate = stem_num(stem, bp), stem_num(stem, mp)
        x = stem_num(stem, xp)
        exact = b + rate * x
        if "closest to" in stem:
            want = Q(round(exact))
            if abs(exact - want) == Q(1, 2):
                raise Unreadable("a half-way value rounds ambiguously")
            return one_number(item, want, "the closest whole number to the model")
        return one_number(item, exact, "the model at the printed input")
    raise Unreadable("an unfamiliar modelled situation")


# ============================================================== sentences
#
# A sentence option is decided in two steps: what claim it makes (a rate, a
# level, an elapsed time, a count), and what number it attaches to that claim.
# The claim comes from the option's own English; the number it has to match
# comes from the item's own printed equation, table or figure. A distractor
# that is a true statement about the model is still wrong unless the claim it
# makes is the one the question asks about -- and a sentence whose number the
# item never prints anywhere cannot be checked at all, which is itself the
# defect this catches.

UNIT_ALIASES = {"centimeter": "centimeters", "newton": "newtons", "cm": "centimeters",
                "inch": "inches", "second": "seconds", "minute": "minutes",
                "hour": "hours", "day": "days", "gallon": "gallons", "foot": "feet",
                "ton": "tons", "mile": "miles", "dollar": "dollars"}


def unit(word: str) -> str:
    w = word.strip().lower()
    return UNIT_ALIASES.get(w, w)


def slope_claim(option: str) -> tuple[str, Q | None]:
    """What a slope-interpretation sentence claims, and the number it names.

    The claim is one of `rate` (the modelled quantity per one unit of the
    input), `reverse` (the same rate read the other way round), `level` (an
    amount rather than a rate), `elapsed`, `count` or `extreme`.
    """
    t = option.strip().rstrip(".")
    m = re.match(r"The increase in the (\w+), in (\w+), of the \w+ for each "
                 r"one-(\w+) increase in the (\w+)", t)
    if m:
        return f"rate:{m.group(1)}/{unit(m.group(3))}", None
    m = re.match(rf"The object is moving at a rate of ({N[1:-1]}) inches per second", t)
    if m:
        return "rate:distance/seconds", num(m.group(1))
    m = re.match(rf"\w+ drove at an average speed of about {N} miles per hour", t)
    if m:
        return "rate:distance/hours", num(m.group(1))
    m = re.match(rf"Each (\w+) costs \${N}", t)
    if m:
        return f"rate:cost/{unit(m.group(1))}s", num(m.group(2))
    if re.match(r"The cost for each guest", t):
        return "rate:cost/guests", None
    if re.match(r"The electrician's hourly rate", t):
        return "rate:cost/hours", None
    if re.search(r"\b(maximum|largest)\b", t):
        return "extreme", None
    m = re.match(rf"\w+ took {N} trips", t)
    if m:
        return "count", num(m.group(1))
    m = re.match(rf"It took \w+ {N} hours", t)
    if m:
        return "elapsed", num(m.group(1))
    m = re.match(rf"The object moved a total of {N}t? inches", t)
    if m:
        return "level", num(m.group(1))
    m = re.match(rf"The distance between City A and City B is {N} miles", t)
    if m:
        return "level", num(m.group(1))
    m = re.match(rf"The (?:video game system|\w+) costs \${N}", t)
    if m:
        return "level", num(m.group(1))
    m = re.match(rf"The weight, in newtons, of an object that will stretch the "
                 rf"spring {N} centimeters", t)
    if m:
        return "level", num(m.group(1))
    if re.match(r"The length, in centimeters, of the spring with no weight", t):
        return "level", None
    if re.match(r"The (?:electrician's onetime fee|caterer's fixed setup charge)", t):
        return "level", None
    if re.match(r"The total (?:amount that the electrician charges|cost of the order)", t):
        return "level", None
    raise Unreadable(f"an unfamiliar interpretation: {option!r}")


def slope_of_item(item) -> Q | float | None:
    """The slope the item actually prints, or None when it prints none.

    The stem's own equation first; then the drawn line, but only when the
    picture carries a scale. A picture with bare axes says which way the
    quantity goes and no more.
    """
    m = re.search(rf"^([a-z]) = {N}([a-z])\b", item.stem)
    if m:
        return num(m.group(2))
    m = re.search(rf"formula [a-z] = {N} \+ {N}[a-z]", item.stem)
    if m:
        return num(m.group(2))
    if item.figure and figure_carries_numbers(item.figure):
        if '<polyline class="ln"' in item.figure:
            return line_from_chart(item.figure)[0]  # (slope, ...)
        return line_from_grid(item.figure)[0]
    return None


def check_interpret_slope(item) -> str:
    """Exactly one sentence says what the coefficient of the input means."""
    claims = [slope_claim(c) for c in item.choices]
    want = None
    m = re.search(r"relates the (\w+) \w+, in (\w+), of the \w+ to the (\w+) "
                  r"\w+, in (\w+)", item.stem)
    if m:
        want = f"rate:{m.group(1)}/{unit(m.group(4))}"
    else:
        for shape, _ in claims:
            if shape.startswith("rate:"):
                want = shape if want in (None, shape) else "ambiguous"
        if want == "ambiguous":
            want = None
    slope = slope_of_item(item)
    hits = []
    for shape, value in claims:
        if want is not None:
            ok = shape == want
        else:
            ok = shape.startswith("rate:")
        if ok and value is not None:
            if slope is None:
                # the sentence names a number the item never prints: nothing in
                # the stem, and no scale on the picture, can tell it from the
                # option that names the other one
                ok = True
            else:
                ok = near(value, slope)
        hits.append(ok)
    detail = ("; the item prints no slope for the options' numbers to be checked "
              "against" if slope is None and any(v is not None for _, v in claims)
              else f"; the printed slope is {slope}")
    return one_hit(item, hits, "the rate the coefficient stands for", detail)


MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
          "July": 7, "August": 8, "September": 9, "October": 10, "November": 11,
          "December": 12}


def check_interpret_constant(item) -> str:
    """Exactly one sentence says what the constant, or the stated value, means."""
    stem = item.stem
    m = re.search(rf"([A-Z])\(t\) = {N} \+ {N}t", stem)
    if m:                                             # a stated function value
        b, rate = num(m.group(2)), num(m.group(3))
        y0 = stem_num(stem, rf"t years after {N}")
        stated = re.search(rf"[A-Z]\({N}\) = {N}", stem)
        if stated is None:
            raise Unreadable("the stem states no function value")
        t, v = num(stated.group(1)), num(stated.group(2))
        if b + rate * t != v:
            raise AssertionError(f"the stem's own model gives {b + rate * t}, not the "
                                 f"printed value {v}")
        year = y0 + t
        hits = []
        for c in item.choices:
            mm = re.search(rf"predicted to be {N} in the year {N}", c)
            hits.append(bool(mm) and num(mm.group(1)) == v
                        and num(mm.group(2)) == year)
        return one_hit(item, hits, "the model's value in the right year",
                       f"; the model gives {v} in {year}")

    m = re.search(rf"F\(x\) = {N} - {N}\(x - {N}\)", stem)
    if m:                                             # a shifted constant
        k = int(num(m.group(3)))
        mm = re.search(r"x months after (\w+) (\d+)", stem)
        if mm is None:
            raise Unreadable("the stem does not say what x counts from")
        base = MONTHS[mm.group(1)]
        hits = []
        for c in item.choices:
            cm = re.match(r"The average price per gallon on (\w+) \d+", c)
            hits.append(bool(cm) and cm.group(1) in MONTHS
                        and (MONTHS[cm.group(1)] - base) % 12 == k % 12)
        return one_hit(item, hits, "the month the shift points at",
                       f"; the constant sits at x = {k}")

    body = re.search(rf"function f\(x\) = {N} - {N}x", stem)
    if body is None:
        raise Unreadable("no start-value model printed")
    b = num(body.group(1))
    asked = stem_num(stem, rf"best interpretation of {N} in this context")
    if asked != b:
        raise AssertionError(f"the question asks about {asked}, which is not the "
                             f"constant term {b}")
    hits = []
    for c in item.choices:
        low = c.lower()
        level = ("estimated height" in low or "estimated charge" in low)
        start = ("at the start of" in low or "when the recording began" in low)
        hits.append(level and start)
    return one_hit(item, hits, "the modelled quantity at the start")


def check_interpret_x_intercept(item) -> str:
    """Exactly one sentence says what the moment of running out means."""
    m = re.search(rf"y = {N} - {N}x", item.stem)
    if m is None:
        raise Unreadable("no draining model printed")
    b, rate = num(m.group(1)), num(m.group(2))
    if rate == 0:
        raise Unreadable("a flat model never reaches zero")
    xi = b / rate
    hits = []
    for c in item.choices:
        t = c.strip().rstrip(".")
        mm = re.match(rf"The (?:tank will be empty|team will have moved all the cargo) "
                      rf"in about {N} (?:minutes|hours)", t)
        if mm:
            hits.append(near(num(mm.group(1)), xi, rel=0.06))
            continue
        if re.match(r"The number of seconds it took from the time \w+ began applying "
                    r"the brakes until the bicycle came to a complete stop", t):
            hits.append(True)
            continue
        hits.append(False)
    return one_hit(item, hits, "the time the quantity runs out",
                   f"; the model reaches zero at {float(xi):.4f}")


CHECKS = {
    "lin.evaluate": check_evaluate,
    "lin.coefficient": check_coefficient,
    "lin.combine": check_combine,
    "lin.inner_scale": check_inner_scale,
    "lin.from_points": check_from_points,
    "lin.from_table": check_from_table,
    "lin.define_line": check_define_line,
    "lin.table_facts": check_table_facts,
    "lin.x_intercept": check_x_intercept,
    "lin.y_intercept": check_y_intercept,
    "lin.model_equation": check_model_equation,
    "lin.per_unit_model": check_per_unit,
    "lin.tiered_cost": check_tiered,
    "lin.model_value": check_model_value,
    "lin.context_two_points": check_two_points,
    "lin.interpret_slope": check_interpret_slope,
    "lin.interpret_constant": check_interpret_constant,
    "lin.interpret_x_intercept": check_interpret_x_intercept,
    "lin.graph_read": check_graph_read,
    "lin.graph_shifted": check_graph_shifted,
    "lin.parameter_intercept": check_parameter_intercept,
    "lin.affine_conversion": check_affine_conversion,
    "lin.unit_relation": check_unit_relation,
}


# --------------------------------------------------- proving it can fail

def as_printed(item):
    """The finished item with the page's typeset minus folded to the ASCII sign.

    The number readers in this file already fold U+2212 on the way in (`num`,
    `terms`, `expr_value`), because an option prints it. The patterns that
    search a STEM cannot: they are written as literal algebra -- "y = f(x) - 7
    is shown", "(9/5)(x - 273.15)" -- and a regex spelled with the keyboard
    hyphen simply stops matching the day the renderer starts typesetting. That
    is the reader's version of the bug this file exists to catch, so the fold
    happens once, here, at the only door items come through, and every checker
    below sees one spelling. It normalises inbound; it decides nothing.
    """
    out = copy.copy(item)
    out.stem = item.stem.replace(MINUS, "-")
    out.rationale = item.rationale.replace(MINUS, "-")
    out.choices = [c.replace(MINUS, "-") for c in item.choices]
    if item.table:
        out.table = [[c.replace(MINUS, "-") for c in row] for row in item.table]
    if item.figure:
        out.figure = item.figure.replace(MINUS, "-")
    return out


def broken(item, **changes):
    """A copy of a finished item with something wrong done to it."""
    bad = copy.deepcopy(item)
    for k, v in changes.items():
        setattr(bad, k, v)
    return bad


def first(name, want=lambda it: True):
    for seed in range(400):
        try:
            item = as_printed(generate(name, seed))
        except ItemError:
            continue
        if item.fmt == "mcq" and want(item):
            return item
    raise RuntimeError(f"no usable {name} item to break")


def signed(m: Q, var: str, over: int = 1) -> str:
    """A slope written a way the topic never writes it: `- 2x/1`, `+ 18x/2`."""
    sign = "+" if m > 0 else "-"
    n = abs(m.numerator) * over
    return f"{sign} {n}{var}/{m.denominator * over}"


def strip_scale(svg: str) -> str:
    """The same picture with its tick labels rubbed out."""
    return re.sub(r'<text class="lb"[^>]*>[^<]*</text>', "", svg)


def selftest() -> int:
    """A check nobody has seen fail is worth nothing.

    Five faults, one of each kind the assertions are for: a second correct
    answer written a different way, a scaled rewriting of the key, the right
    answer under the wrong letter, a figure spliced in from another item, and
    a picture whose scale has been rubbed out, which leaves two of the printed
    sentences equally defensible.
    """
    cases = []

    # 1. a second correct answer: the key's own line, restated
    item = first("lin.from_points")
    i = keyed(item)
    m, b = line_of(item.choices[i])
    name = item.choices[i].split("(")[0]
    twin = list(item.choices)
    twin[(i + 1) % 4] = f"{name}(x) = {b} {signed(m, 'x')}"
    cases.append(("a second correct answer, written differently",
                  broken(item, choices=twin), check_from_points))

    # 2. the key as a scaled rewriting -- the same line, every number doubled
    item = first("lin.model_equation", lambda it: "=" in it.choices[0])
    i = keyed(item)
    var, m, b = as_function(item.choices[i])
    lhs = item.choices[i].split("=")[0].strip()
    twin = list(item.choices)
    twin[(i + 2) % 4] = f"{lhs} = {2 * b}/2 {signed(m, var, 2)}"
    cases.append(("the key rewritten as a scaled form",
                  broken(item, choices=twin), check_model_equation))

    # 3. the right answer under the wrong letter
    item = first("lin.from_table")
    other = "ABCD"[(keyed(item) + 2) % 4]
    cases.append(("the key under the wrong letter",
                  broken(item, answer=other), check_from_table))

    # 4. a figure spliced in from another item: the options no longer describe
    #    the line that is drawn
    a = first("lin.graph_shifted")
    other_fig = next(it.figure for it in
                     (generate("lin.graph_shifted", s) for s in range(1, 400))
                     if it.figure != a.figure)
    cases.append(("a figure spliced in from another item",
                  broken(a, figure=other_fig), check_graph_shifted))

    # 5. the scale rubbed off a picture whose options name numbers -- the
    #    defect this file found, kept as a regression
    item = first("lin.interpret_slope", lambda it: "video game system" in it.stem)
    cases.append(("a picture with no scale under numbered sentences",
                  broken(item, figure=strip_scale(item.figure)),
                  check_interpret_slope))

    # 6. two options a reader of the drawn line could not choose between --
    #    the other defect this file found, also kept as a regression
    item = first("lin.graph_read", lambda it: "cab ride" in it.stem)
    i = keyed(item)
    twin = list(item.choices)
    twin[(i + 1) % 4] = f"${float(num(item.choices[i])) + 0.04:.2f}"
    cases.append(("two options a reader of the picture cannot separate",
                  broken(item, choices=twin), check_graph_read))

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
                raw = generate(name, seed)
            except ItemError:
                continue
            if raw.fmt != "mcq":
                continue
            item = as_printed(raw)
            made += 1
            try:
                what = checker(item) or what
            except Unreadable as exc:
                skipped += 1
                if skipped <= args.show:
                    print(f"\n{name} seed {seed}: unreadable -- {exc}")
                    print(raw.pretty())
            except AssertionError as exc:
                bad += 1
                if bad <= args.show:
                    print(f"\n{name} seed {seed}: {exc}")
                    print(raw.pretty())
        total += made
        mark = "  ok  " if not (bad or skipped) else " FAIL "
        tail = f", {skipped} unreadable" if skipped else ""
        print(f"{mark} {name:<26} {made:>5,} items, {bad} defects{tail}   ({what})")
        worst |= 1 if (bad or skipped) else 0
    print(f"\n{total:,} items read back")
    return worst


if __name__ == "__main__":
    sys.exit(main())
