"""Read the four printed options back, and check only one of them is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct, because nothing in the engine reads a wrong option
as mathematics: `assemble_text` takes four strings, shuffles them and records
which one is the key; `audit` re-derives the key; `structure` counts surface
forms and `prose` looks for placeholders. An item with two right answers passes
every one of them.

This topic has the sharpest exposure of any, because most of its options are
*sentences about a distribution*. A distractor that happens to be a true
statement is the defect, and nothing in the engine reads a sentence at all.

So this script decides every option from its printed text and from the item's
own table or picture, and asserts both halves: exactly one option is right, and
it is the keyed one. Three rules it follows throughout:

  * read the printed string, never the parameters. The readers below
    re-implement the printing rules they need; `generate` is the only thing
    imported from the engine, and only to obtain the finished item in the state
    a student receives it.
  * where a chart carries the question -- a dot plot, a pair of histograms, a
    box plot, a bar graph -- the chart is recovered from the SVG's own pixel
    geometry, so the picture is checked against the options rather than the
    options against each other.
  * where the question is "must be true" or "could be", an option is decided by
    searching for a data set consistent with the printed stem that breaks it. A
    statement called true has to survive that search; a statement called false
    has to produce a witness. Neither half is taken on trust.

    PYTHONPATH=. python3 satbank/topics/one_variable_data/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 2000 --template ovd.box_compare
    PYTHONPATH=. python3 .../option_check.py --selftest
    PYTHONPATH=. python3 .../option_check.py --sources

Exits non-zero on the first kind of defect it finds, and prints the item.
"""

from __future__ import annotations

import argparse
import random
import re
import sys
from fractions import Fraction as Q

from satbank.item import ItemError
from satbank.registry import generate

MINUS = "−"
LETTERS = "ABCD"


class Unreadable(Exception):
    """The printed text is not something this reader understands.

    Raised rather than swallowed: an option shape nobody taught this reader
    about is an unchecked option, which is the thing the script exists to stop.
    """


# ------------------------------------------------- printed text -> numbers

UNIT = re.compile(r"\s*(?:°F|°C|°|%|degrees?|ounces?|pounds?|inches|inch|feet|foot|"
                  r"grams?|kilograms?|centimeters?|millimeters?|meters?|miles?|"
                  r"kilometers?|minutes?|seconds?|years?|points?|hours?|days?)$", re.I)


def num(text: str) -> Q:
    """A printed number: 8, −11, 2,300, 9/7, 3.5, 0.95%, 81°F, $1.29."""
    t = UNIT.sub("", str(text).strip())
    t = t.replace(MINUS, "-").replace(",", "").replace("$", "").strip()
    if not t:
        raise Unreadable(f"{text!r} carries no number")
    try:
        if "/" in t:
            a, b = t.split("/", 1)
            return Q(int(a), int(b))
        return Q(t)
    except (ValueError, ZeroDivisionError):
        raise Unreadable(f"{text!r} is not a number") from None


def numbers(text: str) -> list[Q]:
    """A printed list of values: `2, 2, 3, 4.5, 11` or `1,126, 4,399`.

    Values are split on the comma *and space* that separates them, never on the
    comma inside a thousands group -- which is the whole difference between
    `1,126` and `163, 179`.
    """
    return [num(p) for p in re.split(r",\s+", str(text).strip()) if p.strip()]


def numeric(cell: str) -> bool:
    try:
        num(cell)
        return True
    except Unreadable:
        return False


VALUE_LINE = re.compile(r"^\s*[\d.,\s" + MINUS + r"-]+\s*$")


def listed_in(stem: str) -> list[Q]:
    """The one line of the stem that is a list of data values."""
    found = [line for line in stem.split("\n")
             if VALUE_LINE.match(line) and line.count(",") >= 2]
    if len(found) != 1:
        raise Unreadable(f"{len(found)} lines of the stem are a list of values")
    return numbers(found[0])


# ---------------------------------------------- statistics, written afresh

def mean_(xs) -> Q:
    if not xs:
        raise Unreadable("the mean of no values")
    return sum(xs, Q(0)) / len(xs)


def median_(xs) -> Q:
    s = sorted(xs)
    n = len(s)
    if n == 0:
        raise Unreadable("the median of no values")
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def mode_(xs) -> Q:
    """The single most common value. A tie is not a mode a question may have."""
    counts: dict[Q, int] = {}
    for v in xs:
        counts[v] = counts.get(v, 0) + 1
    top = max(counts.values())
    winners = [v for v, c in counts.items() if c == top]
    if len(winners) != 1 or top == 1:
        raise AssertionError(f"{len(winners)} values tie for most common "
                             f"({sorted(winners)}), so 'the mode' names no one number")
    return winners[0]


def range_(xs) -> Q:
    return max(xs) - min(xs)


def var_(xs) -> Q:
    mu = mean_(xs)
    return sum((v - mu) ** 2 for v in xs) / len(xs)


STAT_FN = {"mean": mean_, "average": mean_, "median": median_, "mode": mode_,
           "range": range_}


def round_half_up(v: Q, places: int) -> Q:
    scale = Q(10) ** places
    x = v * scale
    n, d = x.numerator, x.denominator
    whole = (2 * n + d) // (2 * d) if n >= 0 else -((-2 * n + d) // (2 * d))
    return Q(whole) / scale


# ------------------------------------------------- a drawn chart -> numbers
#
# Every chart in this topic is generated by `satbank/plot.py`, which prints the
# data straight into pixel coordinates. These readers go the other way: they
# take the axis labels the chart draws for a student, fit the pixels-per-unit
# from them, and map every dot, bar, box edge and bin back to a value. They
# consult none of the item's parameters -- this is what a reader with a ruler
# would get, so the picture is checked against the options.

TEXT = re.compile(r'<text class="(lb|ti)" x="([-\d.]+)" y="([-\d.]+)"'
                  r'[^>]*?text-anchor="(\w+)"[^>]*>([^<]*)</text>')
LINE = re.compile(r'<line class="(ax|bx|gr)" x1="([-\d.]+)" y1="([-\d.]+)" '
                  r'x2="([-\d.]+)" y2="([-\d.]+)"')
RECT = re.compile(r'<rect class="(ax|bx|bar)" x="([-\d.]+)" y="([-\d.]+)" '
                  r'width="([-\d.]+)" height="([-\d.]+)"')


def texts(svg: str) -> list[tuple]:
    """(class, x, y, anchor, text) for every label drawn on the chart."""
    return [(m.group(1), float(m.group(2)), float(m.group(3)), m.group(4), m.group(5))
            for m in TEXT.finditer(svg)]


def lines(svg: str) -> list[tuple]:
    return [(m.group(1), float(m.group(2)), float(m.group(3)),
             float(m.group(4)), float(m.group(5))) for m in LINE.finditer(svg)]


def rects(svg: str) -> list[tuple]:
    return [(m.group(1), float(m.group(2)), float(m.group(3)),
             float(m.group(4)), float(m.group(5))) for m in RECT.finditer(svg)]


def scale(marks: list[tuple[float, float]]):
    """A pixel-to-value map fitted to the axis labels, and checked against them.

    `marks` is [(pixel, value)]. Two labels fix the line; every other label has
    to fall on it, or the axis is not linear and nothing may be read off it.
    """
    pts = sorted(set(marks))
    if len(pts) < 2:
        raise Unreadable(f"{len(pts)} labels on this axis, too few to fix a scale")
    (p0, v0), (p1, v1) = pts[0], pts[-1]
    if p1 == p0:
        raise Unreadable("two axis labels at the same pixel")
    per = (v1 - v0) / (p1 - p0)
    # pixel coordinates are printed to two decimals, so a label may sit up to a
    # few hundredths of a pixel from where an exact scale would put it
    for p, v in pts:
        if abs((v0 + (p - p0) * per) - v) > 0.05 * abs(per):
            raise Unreadable(f"the axis label {v} is not where a linear scale puts it")
    return lambda px: v0 + (px - p0) * per, abs(per)


def _tidy(v: float, per: float, what: str) -> Q:
    """A value read off pixels, snapped to the exact number it must be.

    Pixel coordinates are printed to two decimals, so a reading is good to a
    hundredth of a pixel. Anything that does not land on a value the axis could
    carry is a picture that disagrees with itself.
    """
    best = round(v)
    if abs(v - best) > min(0.25, max(0.05 * per, 1e-9)):
        raise AssertionError(f"the {what} is drawn at {v:.4f}, which is not a value "
                             f"this axis can carry")
    return Q(int(best))


def dots(svg: str) -> list[Q]:
    """A dot plot as the data set it draws."""
    marks = [(x, num(t)) for cls, x, y, anchor, t in texts(svg)
             if cls == "lb" and anchor == "middle"]
    at = [float(m.group(1)) for m in
          re.finditer(r'<circle class="pt" cx="([-\d.]+)"', svg)]
    if not at:
        raise Unreadable("a dot plot with no dots")
    if len(marks) == 1:
        # every value is the same, so the number line carries one mark. A dot
        # over it can still be read; a dot anywhere else cannot
        px, value = marks[0]
        for cx in at:
            if abs(cx - px) > 0.5:
                raise AssertionError(f"a dot at {cx} is away from the only mark on the "
                                     f"number line, so its value cannot be read")
        return [value] * len(at)
    to_value, per = scale([(x, float(v)) for x, v in marks])
    return sorted(_tidy(to_value(cx), per, "dot") for cx in at)


def one_box(svg: str) -> tuple:
    """A single box plot as the five numbers it draws, in data units."""
    marks = [(x, float(num(t))) for cls, x, y, anchor, t in texts(svg)
             if cls == "lb" and anchor == "middle"]
    to_value, per = scale(marks)
    box = [r for r in rects(svg) if r[0] == "ax"]
    if len(box) != 1:
        raise Unreadable(f"{len(box)} boxes drawn, not one")
    _, bx, by, bw, bh = box[0]
    verticals = [(x1, abs(y2 - y1)) for cls, x1, y1, x2, y2 in lines(svg)
                 if cls == "ax" and x1 == x2]
    mid = [x for x, h in verticals if abs(h - bh) < 0.5]
    caps = sorted(x for x, h in verticals if abs(h - bh / 2 + 2) < 2.5)
    if len(mid) != 1 or len(caps) != 2:
        raise Unreadable(f"{len(mid)} median lines and {len(caps)} whisker caps drawn")
    return tuple(to_value(px) for px in (caps[0], bx, mid[0], bx + bw, caps[1]))


def many_boxes(svg: str) -> list[tuple]:
    """Box plots drawn to one scale, as [(label, (lo, q1, median, q3, hi))]."""
    marks = [(x, float(num(t))) for cls, x, y, anchor, t in texts(svg)
             if cls == "lb" and anchor == "middle"]
    to_value, per = scale(marks)
    boxes = [r for r in rects(svg) if r[0] == "bx"]
    names = [(y, t) for cls, x, y, anchor, t in texts(svg)
             if cls == "ti" and anchor == "end"]
    if len(boxes) != len(names):
        raise Unreadable(f"{len(boxes)} boxes and {len(names)} labels")
    out = []
    for _, bx, by, bw, bh in boxes:
        cy = by + bh / 2
        verticals = [(x1, abs(y2 - y1)) for cls, x1, y1, x2, y2 in lines(svg)
                     if cls == "bx" and x1 == x2 and abs((y1 + y2) / 2 - cy) < 1]
        mid = [x for x, h in verticals if abs(h - bh) < 0.5]
        caps = sorted(x for x, h in verticals if abs(h - bh) >= 0.5)
        label = min(names, key=lambda n: abs(n[0] - 4 - cy))[1]
        if len(mid) != 1 or len(caps) != 2:
            raise Unreadable(f"{label}: {len(mid)} median lines, {len(caps)} caps")
        out.append((label, tuple(_tidy(to_value(px), per, f"{label} box plot")
                                 for px in (caps[0], bx, mid[0], bx + bw, caps[1]))))
    if len(out) < 2:
        raise Unreadable(f"{len(out)} box plots drawn, not a pair")
    return out


def bars(svg: str) -> list[tuple]:
    """A bar graph as [(label, height)], heights read off the frequency axis."""
    left = [(y, float(num(t))) for cls, x, y, anchor, t in texts(svg)
            if cls == "lb" and anchor == "end"]
    to_value, per = scale(left)
    under = [(x, t) for cls, x, y, anchor, t in texts(svg)
             if cls == "lb" and anchor == "middle"]
    out = []
    for _, bx, by, bw, bh in [r for r in rects(svg) if r[0] == "bar"]:
        centre = bx + bw / 2
        near = [t for x, t in under if abs(x - centre) < 1]
        if len(near) != 1:
            raise Unreadable(f"{len(near)} labels under the bar at x={centre}")
        out.append((near[0], _tidy(to_value(by) - to_value(by + bh), per, "bar")))
    if not out:
        raise Unreadable("a bar graph with no bars")
    return out


def panels(svg: str) -> list[tuple]:
    """Histograms drawn to one scale, as [(label, edges, counts)].

    Each panel is found by the line its bars stand on; a label belongs to the
    panel whose floor is the first one at or below it, which needs nothing
    known about how tall a panel is.
    """
    boxes = [r for r in rects(svg) if r[0] == "bar"]
    floors = sorted({round(by + bh, 1) for _, bx, by, bw, bh in boxes})
    if len(floors) < 2:
        raise Unreadable(f"{len(floors)} histogram panels, not a pair")

    def floor_of(y: float) -> float:
        return min((f for f in floors if f >= y - 0.5), default=floors[-1])

    out = []
    for floor in floors:
        left = [(y - 4, float(num(t))) for cls, x, y, anchor, t in texts(svg)
                if cls == "lb" and anchor == "end" and floor_of(y - 4) == floor]
        to_count, per = scale(left)
        under = [(x, float(num(t))) for cls, x, y, anchor, t in texts(svg)
                 if cls == "lb" and anchor == "middle" and abs(y - (floor + 17)) < 1]
        to_value, _ = scale(under)
        edges = sorted(v for _, v in under)
        top = min(y for y, _ in left)
        titles = [(y, t) for cls, x, y, anchor, t in texts(svg)
                  if cls == "ti" and anchor == "middle" and y < top]
        counts = [0] * (len(edges) - 1)
        for _, bx, by, bw, bh in boxes:
            if abs(by + bh - floor) > 1:
                continue
            lo, hi = to_value(bx), to_value(bx + bw)
            where = [i for i in range(len(edges) - 1)
                     if abs(edges[i] - lo) < 0.05 and abs(edges[i + 1] - hi) < 0.05]
            if len(where) != 1:
                raise Unreadable(f"a bar spanning {lo} to {hi} is not one bin")
            counts[where[0]] = int(_tidy(to_count(by), per, "bar"))
        out.append((max(titles)[1] if titles else f"panel {len(out) + 1}",
                    [Q(str(e)) for e in edges], counts))
    return out


# ------------------------------------------------------ printed tables

def table_of(item):
    if not item.table:
        raise Unreadable("this item prints no table")
    return [list(r) for r in item.table]


def series(item) -> list[tuple[str, list[Q]]]:
    """The table's data series as [(name, values)], read off the printed cells.

    Which way a table runs is settled first -- data across the page when there
    are more columns than rows, or when the corner cell is blank; data down it
    otherwise -- and then by whether the first cell of a data row is a number
    or the name of the row. Nothing here guesses which of two numeric rows is
    the data.
    """
    rows = table_of(item)
    body = [r for r in rows[1:] if r[0].lower() != "total"]
    if not body:
        raise Unreadable("a table with no rows under its heading")
    if rows[0][0] == "" or len(rows[0]) > len(rows):          # data across
        if all(numeric(c) for c in body[0]):
            return [("", [num(c) for c in r]) for r in body]
        return [(r[0], [num(c) for c in r[1:]]) for r in body]
    return [(rows[0][k], [num(r[k]) for r in body])           # data down
            for k in range(1, len(rows[0]))]


def labels_of(item) -> list[str]:
    """The label against each value: the row of headings or the first column."""
    rows = table_of(item)
    body = [r for r in rows[1:] if r[0].lower() != "total"]
    if rows[0][0] == "" or len(rows[0]) > len(rows):
        return rows[0] if all(numeric(c) for c in body[0]) else rows[0][1:]
    return [r[0] for r in body]


def named_series(item, question: str) -> tuple[str, list[Q]]:
    """The one series the question names, when the table prints more than one."""
    got = series(item)
    if len(got) == 1:
        return got[0]
    q = question.lower()
    hits = [s for s in got if s[0] and s[0].lower() in q]
    if len(hits) != 1:
        raise Unreadable(f"the question names {len(hits)} of the table's series "
                         f"{[s[0] for s in got]}")
    return hits[0]


def freq_table(item) -> tuple[list[Q], list[Q]]:
    """A value-and-frequency table as (values, frequencies).

    A frequency printed symbolically -- `a`, `3a` -- reads as its coefficient,
    and every stat is then checked to be the same whatever `a` is.
    """
    rows = table_of(item)
    vals, freqs = [], []
    for r in rows[1:]:
        if r[0].lower() == "total":
            continue
        vals.append(num(r[0]))
        m = re.fullmatch(r"(\d*)a", r[1].strip())
        freqs.append(Q(int(m.group(1) or 1)) if m else num(r[1]))
    if not vals or len(set(vals)) != len(vals):
        raise Unreadable("a frequency table wants one row per distinct value")
    return vals, freqs


def symbolic(item) -> bool:
    return any(re.fullmatch(r"\d*a", r[1].strip()) for r in table_of(item)[1:])


def expand(vals: list[Q], freqs: list[Q]) -> list[Q]:
    out: list[Q] = []
    for v, f in zip(vals, freqs):
        if f.denominator != 1 or f < 0:
            raise Unreadable(f"a frequency of {f}")
        out += [v] * int(f)
    if not out:
        raise Unreadable("an empty frequency table")
    return out


# ------------------------------------------------------------- the verdict

def keyed(item) -> int:
    return LETTERS.index(item.answer)


def verdict(item, hits: list[bool], what: str) -> str:
    """Both halves of the assertion: exactly one hit, and the keyed one.

    `hits.count(True) == 1` is the half no gate in the engine performs, and the
    half this script exists for; `hits[keyed]` is the half `audit` already does,
    kept because a check that drops it can be satisfied by a shuffled answer.
    """
    if len(hits) != len(item.choices):
        raise Unreadable("an option was not decided")
    if hits.count(True) != 1:
        right = [c for c, h in zip(item.choices, hits) if h]
        raise AssertionError(f"{hits.count(True)} of the four options are right: "
                             + ("; ".join(repr(c) for c in right) or "none is"))
    if not hits[keyed(item)]:
        raise AssertionError(f"the right option is {item.choices[hits.index(True)]!r}, "
                             f"but the key is {item.choices[keyed(item)]!r}")
    return what


def closest(item, exact: Q, what: str, tol: Q | None = None) -> str:
    """Exactly one printed option is nearest the value the item determines."""
    gaps = [abs(num(c) - exact) for c in item.choices]
    best = min(gaps)
    if tol is not None and best > tol:
        raise AssertionError(f"the nearest option is {float(best)} away from {float(exact)}, "
                             f"which the item itself determines")
    return verdict(item, [g == best for g in gaps], what)


# ================================================================== CHECKS
#
# One per template. Each returns a short description of what it decided, or
# None when that draw is not asked in a way this check applies to (a grid-in
# has no options to read back).


# ---------------------------------------------------------- a printed list

ASK_STAT = re.compile(r"\bWhat (?:is|was) the (mean|median|mode|range)\b", re.I)


def check_list_stat(item) -> str | None:
    """A centre or a spread read off a printed list or a drawn dot plot."""
    if item.fmt != "mcq":
        return None
    m = ASK_STAT.search(item.stem)
    if m is None:
        raise Unreadable(item.stem)
    stat = m.group(1).lower()
    data = dots(item.figure) if item.figure else listed_in(item.stem)
    n = re.search(r"each of (\d+) |of (\d+) data values|A list of (\d+) data", item.stem)
    if n is not None and len(data) != int(next(g for g in n.groups() if g)):
        raise AssertionError(f"the stem says {n.group(0)!r} but {len(data)} are shown")
    want = STAT_FN[stat](data)
    return verdict(item, [num(c) == want for c in item.choices],
                   f"the {stat} of the {'drawn' if item.figure else 'printed'} values")


# --------------------------------------------------------- a printed table

PAIR_ASK = re.compile(r"(?:answered|responded with|responded) either “(.+?)” "
                      r"or “(.+?)”|are either an? (.+?) or an? (.+?)\?")
REFERENCE = re.compile(r"(?:was|is) ([\d.,]+%?)\.")
# "to the nearest hundredth", "to the nearest tenth of a million", and -- when
# the answer carries a unit -- "to the nearest square kilometer", which is a
# whole number of them
NEAREST = re.compile(r"to the nearest ([a-z ]+)")


def check_table_stat(item) -> str | None:
    """A statistic read out of a printed table."""
    if item.fmt != "mcq":
        return None
    if "either" in item.stem:
        return _pair_sum(item)
    m = ASK_STAT.search(item.stem) or re.search(
        r"how much greater.*?was the (mean|median|mode|range)", item.stem, re.I | re.S)
    if m is None:
        m = re.search(r"the difference between the (mean|median|mode|range)", item.stem, re.I)
    if m is None:
        raise Unreadable(item.stem)
    stat = m.group(1).lower()
    name, values = named_series(item, item.stem)
    exact = STAT_FN[stat](values)
    what = f"the {stat} of {name or 'the values'}"
    if "difference between" in item.stem or "how much greater" in item.stem:
        r = REFERENCE.search(item.stem)
        if r is None:
            raise Unreadable(f"no stated value to take the difference from: {item.stem!r}")
        exact = abs(exact - num(r.group(1)))
        what = f"{what} against the stated {r.group(1)}"
    near = NEAREST.search(item.stem)
    if near:
        word = near.group(1)
        places = 2 if "hundredth" in word else (1 if "tenth" in word else 0)
        half = exact * Q(10) ** places
        if half.denominator == 2:
            raise AssertionError(f"the exact value is {float(exact)}, halfway between two "
                                 f"options at this precision: which one is 'nearest' is a "
                                 f"convention the stem does not state")
        exact = round_half_up(exact, places)
    return verdict(item, [num(c) == exact for c in item.choices], what)


def _pair_sum(item) -> str:
    """Two rows of a printed frequency table, added."""
    m = PAIR_ASK.search(item.stem)
    if m is None:
        raise Unreadable(item.stem)
    wanted = [g.lower() for g in m.groups() if g]
    labels, (_, values) = labels_of(item), series(item)[0]
    rows = table_of(item)
    total = [r for r in rows if r[0].lower() == "total"]
    if total and num(total[0][1]) != sum(values, Q(0)):
        raise AssertionError(f"the printed total {total[0][1]} is not the sum of the rows")
    picked = []
    for phrase in wanted:
        hit = [i for i, lab in enumerate(labels) if lab.lower() == phrase]
        if len(hit) != 1:
            raise Unreadable(f"{phrase!r} names {len(hit)} rows of {labels}")
        picked.append(hit[0])
    if len(set(picked)) != 2:
        raise Unreadable("the question names one row twice")
    exact = sum(values[i] for i in picked)
    return verdict(item, [num(c) == exact for c in item.choices], "two rows added")


# ------------------------------------------------------------ a bar graph

def check_bar_read(item) -> str | None:
    """A value, a difference or a mean read off the bars that are drawn."""
    if item.fmt != "mcq":
        return None
    drawn = bars(item.figure)
    question = item.stem.split(". ")[-1]
    named = _bars_named(drawn, question)
    if "mean" in question:
        if named:
            raise Unreadable(f"a mean question naming {named}")
        exact = mean_([v for _, v in drawn])
        what = "the mean of the drawn bars"
    elif "more" in question:
        if len(named) != 2:
            raise AssertionError(f"a difference between {len(named)} named bars")
        exact = named[0][1] - named[1][1]
        what = f"the drawn {named[0][0]} bar less the {named[1][0]} bar"
    else:
        if len(named) != 1:
            raise AssertionError(f"{len(named)} bars are named by {question!r}")
        exact = named[0][1]
        what = f"the height of the drawn {named[0][0]} bar"
    return verdict(item, [num(c) == exact for c in item.choices], what)


def _bars_named(drawn, question: str) -> list[tuple]:
    """The bars the question names, in the order it names them."""
    found = []
    for label, value in drawn:
        pat = (rf"\b{re.escape(label)}\b" if len(label) == 1
               else re.escape(label.lower()))
        where = ([m.start() for m in re.finditer(pat, question)] if len(label) == 1
                 else [m.start() for m in re.finditer(pat, question.lower())])
        if where:
            found.append((where[0], label, value))
    return [(lab, v) for _, lab, v in sorted(found)]


# ------------------------------------------------------ a frequency table

FREQ_ASK = re.compile(r"What is the (mean|median|mode|range) of the ", re.I)


def check_freq_stat(item) -> str | None:
    """A statistic of the data set a frequency table stands for."""
    if item.fmt != "mcq":
        return None
    vals, freqs = freq_table(item)
    if "How much greater is the mean" in item.stem:
        def measure(scaled):
            return mean_(scaled) - median_(scaled)
        what = "the mean less the median"
    else:
        m = FREQ_ASK.search(item.stem)
        if m is None:
            raise Unreadable(item.stem)
        stat = m.group(1).lower()
        measure = STAT_FN[stat]
        what = f"the {stat} of the tabulated data"
    exact = measure(expand(vals, freqs))
    if symbolic(item):
        # the table says `a`, `2a`, `3a` for a positive integer a: an answer
        # that moves with a is no answer at all
        for a in (2, 3, 5):
            if measure(expand(vals, [f * a for f in freqs])) != exact:
                raise AssertionError(f"the answer changes when a = {a}, so the table "
                                     f"does not determine it")
        what += " (the same for every a)"
    return verdict(item, [num(c) == exact for c in item.choices], what)


ORDER = re.compile(r"^(mean|median|mode) < (mean|median|mode) < (mean|median|mode)$")


def check_freq_order(item) -> str | None:
    """Which printed ordering of the mean, median and mode is the true one."""
    data = expand(*freq_table(item))
    value = {"mean": mean_(data), "median": median_(data), "mode": mode_(data)}
    hits = []
    for c in item.choices:
        m = ORDER.match(c.strip())
        if m is None:
            raise Unreadable(f"{c!r} is not an ordering this reader knows")
        a, b, d = (value[g] for g in m.groups())
        if len(set(m.groups())) != 3:
            raise Unreadable(f"{c!r} names a measure twice")
        hits.append(a < b < d)
    return verdict(item, hits, "the true order of the three measures")


TWO_MEDIANS = re.compile(r"median of the .*? for (.+?) is how much greater than the "
                         r"median of the .*? for (.+?)\?", re.I)


def check_freq_two_groups(item) -> str | None:
    """Two frequency columns: their medians compared, or their means."""
    if item.fmt != "mcq":
        return None
    rows = table_of(item)
    vals = [num(r[0]) for r in rows[1:]]
    # `Data set A frequency` heads a column of counts; the sentences call the
    # data set itself `data set A`, so the word `frequency` comes off the name
    cols = {re.sub(r"\s*frequency$", "", rows[0][k], flags=re.I):
            expand(vals, [num(r[k]) for r in rows[1:]]) for k in (1, 2)}
    if len(cols) != 2:
        raise Unreadable(f"the table's two columns are headed {rows[0][1:]!r}")
    m = TWO_MEDIANS.search(item.stem)
    if m:
        a, b = (_column_named(cols, g) for g in (m.group(1), m.group(2)))
        exact = median_(cols[a]) - median_(cols[b])
        return verdict(item, [num(c) == exact for c in item.choices],
                       f"the median of {a} less the median of {b}")
    hits = [_compares(c, cols) for c in item.choices]
    return verdict(item, hits, "the true comparison of the two means")


def _column_named(cols: dict, phrase: str) -> str:
    hits = [c for c in cols if c.lower() in phrase.lower()]
    if len(hits) != 1:
        raise Unreadable(f"{phrase!r} names {len(hits)} of {list(cols)}")
    return hits[0]


# --------------------------------------------------- four data sets as options

TABLE_OPTION = re.compile(r"^(.+?) \(frequency (\d+)\)$")


def as_table(option: str) -> tuple[list[Q], list[Q]]:
    """`4 (frequency 4), 8 (frequency 3)` as (values, frequencies)."""
    vals, freqs = [], []
    for part in option.split("), "):
        m = TABLE_OPTION.match(part if part.endswith(")") else part + ")")
        if m is None:
            raise Unreadable(f"{part!r} is not a row of a printed frequency table")
        vals.append(num(m.group(1)))
        freqs.append(Q(int(m.group(2))))
    return vals, freqs


def check_freq_choose(item) -> str | None:
    """Four data sets as options, and one property that must pick out one."""
    if "correctly represents the data" in item.stem:
        data = sorted(listed_in(item.stem))
        hits = [sorted(expand(*as_table(c))) == data for c in item.choices]
        return verdict(item, hits, "the table that is the printed data")
    if "greatest mean" in item.stem:
        means = []
        for c in item.choices:
            vals, freqs = as_table(c)
            if len(set(vals)) != len(vals):
                raise Unreadable(f"{c!r} lists a value twice, so it is not a data set")
            means.append(mean_(expand(vals, freqs)))
        top = max(means)
        return verdict(item, [m == top for m in means], "the one greatest mean")
    if "mean greater than the median" in item.stem:
        sets = [numbers(c) for c in item.choices]
        return verdict(item, [mean_(s) > median_(s) for s in sets],
                       "the one right-skewed data set")
    raise Unreadable(item.stem)


# -------------------------------------------------- two data sets compared

REL = {"greater than": ">", "less than": "<", "larger than": ">",
       "smaller than": "<", "equal to": "=", "the same as": "="}
STAT_WORD = re.compile(r"\b(standard deviation|mean|median|average|range|mode)\b")


def comparison(sentence: str) -> tuple:
    """`The mean of data set A is greater than the mean of data set B.`

    Returns (stat, subject, relation, stat, subject) with the two subjects as
    printed, so the caller decides which distribution each one names.
    """
    s = sentence.strip().rstrip(".")
    m = re.match(r"^(.*?) is (greater than|less than|larger than|smaller than|"
                 r"equal to|the same as) (.*)$", s)
    if m is None:
        raise Unreadable(f"{sentence!r} is not a comparison this reader knows")
    left, rel, right = m.group(1), REL[m.group(2)], m.group(3)
    out = []
    for side in (left, right):
        found = STAT_WORD.findall(side)
        if len(found) != 1:
            raise Unreadable(f"{side!r} names {len(found)} measures")
        stat = found[0].replace("average", "mean")
        out.append((stat, side[side.index(found[0]) + len(found[0]):].strip()))
    return out[0][0], out[0][1], rel, out[1][0], out[1][1]


def holds(rel: str, a: Q, b: Q) -> bool:
    return {">": a > b, "<": a < b, "=": a == b}[rel]


def which_set(subject: str, sets: dict) -> list[Q]:
    """The distribution a printed subject phrase names."""
    hits = [k for k in sets if k.lower() in subject.lower()]
    if len(hits) != 1:
        raise Unreadable(f"{subject!r} names {len(hits)} of {list(sets)}")
    return sets[hits[0]]


def _compares(option: str, sets: dict) -> bool:
    """One printed comparison, decided against the data the item shows."""
    if "not enough information" in option.lower():
        # every distribution in this topic is printed in full, as a list, a
        # table or a picture drawn to scale: a stat it asks about is determined
        return False
    stat_a, who_a, rel, stat_b, who_b = comparison(option)
    if stat_a != stat_b:
        raise Unreadable(f"{option!r} compares a {stat_a} with a {stat_b}")
    fn = STAT_FN[stat_a]
    return holds(rel, fn(which_set(who_a, sets)), fn(which_set(who_b, sets)))


def listed_sets(item) -> dict:
    """The two data sets an item shows, by the name it prints them under."""
    out = {}
    for line in item.stem.split("\n"):
        m = re.match(r"^(Data set \w+|[A-Z][\w ]*?): ([\d.,\s" + MINUS + r"-]+)$", line)
        if m and m.group(2).count(",") >= 2:
            out[m.group(1)] = numbers(m.group(2))
    if not out and item.table:
        for name, values in series(item):
            if name:
                out[name] = values
    if len(out) != 2:
        raise Unreadable(f"{len(out)} data sets shown, not two")
    return out


ROMAN = {"I": 1, "II": 2, "III": 3}


def roman_options(item, truth: dict) -> list[bool]:
    """Options of the form `I only`, `II and III only`, `Neither I nor II`."""
    hits = []
    true_set = {n for n, t in truth.items() if t}
    for c in item.choices:
        text = c.strip().rstrip(".")
        if text.lower().startswith("neither"):
            named = set()
        else:
            named = {ROMAN[w] for w in re.findall(r"\b(III|II|I)\b", text)}
            if not named:
                raise Unreadable(f"{c!r} names no statement")
        hits.append(named == true_set)
    if len({c for c in item.choices}) != len(item.choices):
        raise AssertionError("two options print the same")
    return hits


def numbered_statements(stem: str) -> dict:
    """The `I. ...` lines of a stem, by number."""
    out = {}
    for line in stem.split("\n"):
        m = re.match(r"^(III|II|I)\. (.+)$", line.strip())
        if m:
            out[ROMAN[m.group(1)]] = m.group(2)
    if not out:
        raise Unreadable("no numbered statements in the stem")
    return out


def check_compare_sets(item) -> str | None:
    """Two data sets side by side, and which sentence about them is true."""
    sets = listed_sets(item)
    a, b = sets.values()
    if "\nI. " in item.stem:
        truth = {n: _compares(s, sets) for n, s in numbered_statements(item.stem).items()}
        return verdict(item, roman_options(item, truth),
                       "the statements that are true of the printed values")
    if "means and medians" in item.stem:
        same = {"mean": mean_(a) == mean_(b), "median": median_(a) == median_(b)}
        hits = [_differ(c, same) for c in item.choices]
        return verdict(item, hits, "what actually differs between the two sets")
    hits = []
    for c in item.choices:
        m = re.match(r"^The mean of each data set is (.+)\.$", c.strip())
        if m:
            hits.append(mean_(a) == mean_(b) == num(m.group(1)))
        else:
            hits.append(_compares(c, sets))
    return verdict(item, hits, "the true comparison of the two means")


DIFFER = {"Only the means are different.": ("mean",),
          "Only the medians are different.": ("median",),
          "Both the means and the medians are different.": ("mean", "median"),
          "Neither the means nor the medians are different.": ()}


def _differ(option: str, same: dict) -> bool:
    claim = DIFFER.get(option.strip())
    if claim is None:
        raise Unreadable(f"{option!r} is not a claim this reader knows")
    return all((not same[k]) == (k in claim) for k in same)


# --------------------------------------------------------------- spread

def check_sd_compare(item) -> str | None:
    """Standard deviation compared -- from a summary table, or from the drawn
    histograms."""
    if item.figure:
        return _sd_from_histograms(item)
    return _sd_from_table(item)


def _sd_from_table(item) -> str:
    rows = table_of(item)
    head = [h.lower() for h in rows[0]]
    if not head[0].startswith("group"):
        raise Unreadable(f"{rows[0]!r} is not the summary table this reader knows")
    col = {}
    for want in ("sample size", "mean", "standard deviation"):
        k = [i for i, h in enumerate(head) if h.startswith(want)]
        if len(k) != 1:
            raise Unreadable(f"{len(k)} columns for {want!r}")
        col[want] = k[0]
    groups = {r[0]: {w: num(r[col[w]]) for w in col} for r in rows[1:]}
    if len(groups) != 2:
        raise Unreadable(f"{len(groups)} groups in the table, not two")
    (ga, fa), (gb, fb) = groups.items()
    if fa["standard deviation"] == fb["standard deviation"]:
        raise AssertionError("the two standard deviations are equal, so no statement "
                             "about spread is true")
    hits = [_summary_true(c, ga, fa, gb, fb) for c in item.choices]
    return verdict(item, hits, "the one claim the summary table forces")


def _summary_true(option: str, ga, fa, gb, fb) -> bool:
    """A sentence about two groups a table gives only n, mean and sd for.

    Three things follow from such a table and nothing else does: the sample
    sizes, the means and the spreads. Every other sentence here names something
    two different data sets with these same three summaries can disagree about,
    so it is not true *based on the table* -- which is what the stem asks.
    """
    s = option.strip().rstrip(".")
    if "larger spread than" in s:
        first, second = s.split("larger spread than", 1)
        wide = [g for g in (ga, gb) if f"group {g}".lower() in first.lower()]
        narrow = [g for g in (ga, gb) if f"group {g}".lower() in second.lower()]
        if len(wide) != 1 or len(narrow) != 1 or wide == narrow:
            raise Unreadable(f"{option!r} does not name the two groups")
        sd = {ga: fa["standard deviation"], gb: fb["standard deviation"]}
        return sd[wide[0]] > sd[narrow[0]]
    if "identical to" in s:
        # equal n, equal mean and unequal sd already make them different; even
        # all three equal would not make two data sets the same
        return False
    if re.search(r"contained the \w+ ", s):
        # the extreme value: a spread says how far from the mean the values sit
        # on average, never which group holds the single furthest one
        return False
    if "median" in s:
        # a table of means says nothing about medians
        return False
    raise Unreadable(f"{option!r} is a claim this reader cannot decide")


SPREAD_MARGIN = Q(6, 5)         # one variance must beat the other by this much


def _sd_from_histograms(item) -> str:
    got = panels(item.figure)
    if len(got) != 2:
        raise Unreadable(f"{len(got)} histograms drawn, not two")
    spread = {}
    for label, edges, counts in got:
        if sum(counts) <= 0:
            raise AssertionError(f"{label} is an empty histogram")
        mids = [(edges[i] + edges[i + 1]) / 2 for i in range(len(counts))]
        data = expand(mids, [Q(c) for c in counts])
        spread[label.lower()] = var_(data)
    (na, va), (nb, vb) = spread.items()
    close = max(va, vb) < min(va, vb) * SPREAD_MARGIN
    hits = []
    for c in item.choices:
        if "not enough information" in c.lower():
            hits.append(close)
            continue
        stat_a, who_a, rel, stat_b, who_b = comparison(c)
        if stat_a != "standard deviation" or stat_b != "standard deviation":
            raise Unreadable(f"{c!r} does not compare two standard deviations")
        x, y = which_panel(who_a, spread), which_panel(who_b, spread)
        hits.append(False if close else holds(rel, x, y))
    return verdict(item, hits, "the wider of the two drawn distributions")


def which_panel(subject: str, spread: dict) -> Q:
    hits = [k for k in spread if k in subject.lower()]
    if len(hits) != 1:
        raise Unreadable(f"{subject!r} names {len(hits)} of the drawn panels "
                         f"{list(spread)}")
    return spread[hits[0]]


# ------------------------------------------------------ an edit to a data set

MEASURE = {"mean": mean_, "median": median_, "range": range_,
           "standard deviation": var_, "sum of the numbers": lambda xs: sum(xs, Q(0))}

EDIT_N = re.compile(r"for (\d+) [a-z]|data set of (\d+) different numbers")
EDIT_K = re.compile(r"(\d+) \w+ (?:less|more) than its reported|adding (\d+) to each")


def check_measure_effect(item) -> str | None:
    """An edit to a data set, and which summary measure survives it.

    Decided by making data sets the stem describes, applying the edit it prints
    and looking: an option counts as an answer only when it behaves the same way
    for every such data set, which is what "the same value in both" claims.
    """
    n = EDIT_N.search(item.stem)
    k = EDIT_K.search(item.stem)
    if n is None or k is None:
        raise Unreadable(item.stem)
    n = int(next(g for g in n.groups() if g))
    k = Q(int(next(g for g in k.groups() if g)))
    edit, make = _edit_from(item.stem, n, k)
    want_same = "unchanged" in item.stem or "does NOT" not in item.stem
    names = [c.strip().lower() for c in item.choices]
    for name in names:
        if name not in MEASURE:
            raise Unreadable(f"{name!r} is not a measure this reader knows")
    same = {name: True for name in names}
    moved = {name: True for name in names}
    rng = random.Random(11)
    for _ in range(40):
        before = make(rng)
        after = edit(before)
        if len(after) != len(before):
            raise AssertionError("the edit changed how many values there are")
        for name in names:
            fn = MEASURE[name]
            if fn(before) == fn(after):
                moved[name] = False
            else:
                same[name] = False
    hits = [(same if want_same else moved)[name] for name in names]
    return verdict(item, hits,
                   f"the one measure the edit always {'leaves' if want_same else 'moves'}")


def _edit_from(stem: str, n: int, k: Q):
    """The printed edit as a function, and a source of data sets it can act on."""
    def spread_out(xs):
        med = median_(xs)
        return [v + k if v > med else (v - k if v < med else v) for v in xs]

    if "lowest reported" in stem:
        return (lambda xs: sorted(xs)[:1] and [v - k if v == min(xs) else v for v in xs],
                lambda rng: _distinct(rng, n))
    if "greatest reported" in stem:
        return ((lambda xs: [v + k if v == max(xs) else v for v in xs]),
                lambda rng: _distinct(rng, n))
    if "greater than the median" in stem:
        centre = re.search(r"mean of (\d+) and a median of (\d+)", stem)
        if centre is None:
            raise Unreadable(stem)
        c = Q(int(centre.group(1)))
        if centre.group(1) != centre.group(2):
            raise Unreadable("this reader only knows the mean = median frame")
        return spread_out, lambda rng: _centred(rng, n, c)
    if "adding" in stem:
        return (lambda xs: [v + k for v in xs]), lambda rng: _distinct(rng, n)
    raise Unreadable(f"no edit this reader knows in {stem!r}")


def _distinct(rng, n: int) -> list[Q]:
    return [Q(v) for v in rng.sample(range(1, 400), n)]


def _centred(rng, n: int, c: Q) -> list[Q]:
    """n different numbers whose mean and median are both c, lopsided on purpose.

    Half sit below the centre and half above, so the middle one is c; the
    largest offset above is then whatever makes the two sides balance, so the
    mean is c as well without the data set being a mirror image.
    """
    if n % 2 == 0:
        raise Unreadable("an even count has no middle value to pivot on")
    half = (n - 1) // 2
    for _ in range(200):
        below = sorted(rng.sample(range(1, 300), half))
        above = sorted(rng.sample(range(1, 200), half - 1)) if half > 1 else []
        last = sum(below) - sum(above)
        if half and (last <= (above[-1] if above else 0) or last in above):
            continue
        offsets = above + [last]
        return ([c - Q(d) for d in reversed(below)] + [c]
                + [c + Q(d) for d in offsets])
    raise Unreadable("could not build the data set the stem describes")


# ------------------------------------------------- four measures of one set

ODD_TARGET = re.compile(r"NOT equal to ([\d.,]+ ?\w*°?[FC]?)\?")
ODD_OPTION = re.compile(r"^(Mean|Median|Mode|Range) of the ", re.I)


def check_odd_measure(item) -> str | None:
    """Four measures of one printed data set; exactly one must miss the value."""
    m = ODD_TARGET.search(item.stem)
    if m is None:
        raise Unreadable(item.stem)
    target = num(m.group(1))
    _, values = series(item)[0]
    n = re.search(r"(?:over|for) (?:this|these) (\d+)", item.stem)
    if n and len(values) != int(n.group(1)):
        raise AssertionError(f"the stem counts {n.group(1)} values, the table shows "
                             f"{len(values)}")
    hits = []
    for c in item.choices:
        w = ODD_OPTION.match(c.strip())
        if w is None:
            raise Unreadable(f"{c!r} is not a measure this reader knows")
        hits.append(STAT_FN[w.group(1).lower()](values) != target)
    return verdict(item, hits, f"the one measure that is not {m.group(1)}")


# ------------------------------------------------------- a new data set

SHIFT = re.compile(r"(adding|subtracting) ([\d.,]+) (?:to|from) each")
APPEND = re.compile(r"additional \w+ with ([\d.,]+) ")


def check_new_data_set(item) -> str | None:
    """Data set B is made from the drawn data set A. What moved?"""
    a = dots(item.figure)
    m = SHIFT.search(item.stem)
    if m:
        c = num(m.group(2)) * (1 if m.group(1) == "adding" else -1)
        if c == 0:
            raise AssertionError("data set B is data set A")
        b = [v + c for v in a]
        n = re.search(r"has (\d+) values", item.stem)
        if n and len(a) != int(n.group(1)):
            raise AssertionError(f"the stem says {n.group(1)} values, {len(a)} are drawn")
        sets = {"data set A": a, "data set B": b}
        hits = [_pair_claim(c_, sets) for c_ in item.choices]
        return verdict(item, hits, "the true comparison of the medians and the ranges")
    m = APPEND.search(item.stem)
    if m is None:
        raise Unreadable(item.stem)
    b = a + [num(m.group(1))]
    truth = {}
    for i, s in numbered_statements(item.stem).items():
        found = STAT_WORD.findall(s)
        if len(found) != 1:
            raise Unreadable(f"{s!r} names {len(found)} measures")
        fn = STAT_FN[found[0].replace("average", "mean")]
        truth[i] = fn(b) > fn(a)
    return verdict(item, roman_options(item, truth),
                   "the measures the extra value actually lifts")


def _pair_claim(option: str, sets: dict) -> bool:
    """`The median of B is greater than the median of A, and the range of B is
    equal to the range of A.` -- two comparisons in one sentence."""
    parts = [p.strip() for p in option.rstrip(".").split(", and ")]
    if len(parts) != 2:
        raise Unreadable(f"{option!r} is not two comparisons")
    return all(_compares(p, sets) for p in parts)


# -------------------------------------------------------------- box plots

BOX_PART = {"median": 2, "first quartile": 1, "third quartile": 3,
            "least value": 0, "greatest value": 4}


def check_box_read(item) -> str | None:
    """A value read off the box plot that is drawn."""
    if item.fmt != "mcq":
        return None
    summary = one_box(item.figure)
    if not all(summary[i] <= summary[i + 1] for i in range(4)):
        raise AssertionError(f"the drawn box plot is out of order: {summary}")
    named = [p for p in BOX_PART if p in item.stem]
    if len(named) != 1:
        raise Unreadable(f"the question names {named}")
    drawn = summary[BOX_PART[named[0]]]
    span = summary[4] - summary[0]
    return closest(item, Q(str(round(drawn, 6))), f"the drawn {named[0]}",
                   tol=Q(str(round(span / 100, 6))))


def check_box_compare(item) -> str | None:
    """Two box plots on one scale: only the medians they draw are comparable."""
    drawn = many_boxes(item.figure)
    summaries = {label.lower(): five for label, five in drawn}
    if len(summaries) != 2:
        raise Unreadable(f"{len(summaries)} box plots drawn")
    hits = [_box_claim(c, summaries) for c in item.choices]
    return verdict(item, hits, "the one comparison the drawn boxes force")


def _box_claim(option: str, summaries: dict) -> bool:
    stat, who_a, rel, stat_b, who_b = comparison(option)
    if stat != stat_b:
        raise Unreadable(f"{option!r} compares a {stat} with a {stat_b}")
    a, b = which_panel(who_a, summaries), which_panel(who_b, summaries)
    if stat == "median":
        if a[2] == b[2]:
            raise AssertionError("the two drawn medians are equal, so no comparison "
                                 "of them is true")
        return holds(rel, a[2], b[2])
    if stat == "range":
        return holds(rel, a[4] - a[0], b[4] - b[0])
    if stat == "mean":
        # a box plot draws five numbers and leaves every value between them
        # free, so a claim about a mean is true only where it holds for every
        # data set the picture allows. A quarter of the values lie in each of
        # the four spans, which bounds the mean between the two ends below.
        (loa, hia), (lob, hib) = _mean_band(a), _mean_band(b)
        return {"<": hia < lob, ">": loa > hib, "=": loa == hia == lob == hib}[rel]
    raise Unreadable(f"{option!r} is a claim this reader cannot decide from a box plot")


def _mean_band(five) -> tuple[Q, Q]:
    """How low and how high the mean of a data set drawn like this can go."""
    lo, q1, med, q3, hi = five
    return (lo + q1 + med + q3) / 4, (q1 + med + q3 + hi) / 4


# ------------------------------------------------------ solving for a value

def check_unknown_value(item) -> str | None:
    """A data set solved for the one value it does not show."""
    if item.fmt != "mcq":
        return None
    if "NOT a possible value" in item.stem:
        listed = _listed_beside_x(item.stem)
        hits = []
        for c in item.choices:
            x = num(c)
            full = listed + [x]
            hits.append(mean_(full) != median_(full))
        return verdict(item, hits, "the one value that cannot make them agree")
    if "largest integer" in item.stem:
        return _integer_mean(item)
    return _equal_means(item)


def _listed_beside_x(stem: str) -> list[Q]:
    """`34, 38, 40, 41, x` -- the values printed next to the unknown."""
    for line in stem.split("\n"):
        parts = [p.strip() for p in re.split(r",\s+", line.strip())]
        if len(parts) >= 3 and parts.count("x") == 1 and all(
                numeric(p) for p in parts if p != "x"):
            return [num(p) for p in parts if p != "x"]
    raise Unreadable("no list with an unknown in it")


EQUAL_MEANS = re.compile(r"the mean of (.+?) is (equal to|[\d.,]+ (?:\w+ )?(?:greater|less) "
                         r"than) the mean of (.+?)(?:,| what| \?)", re.I | re.S)


def _equal_means(item) -> str:
    """One data set shows an x; the relation between the two means fixes it."""
    m = EQUAL_MEANS.search(item.stem)
    if m is None:
        raise Unreadable(item.stem)
    sets = _sets_with_x(item)
    first, second = _side(m.group(1), sets), _side(m.group(3), sets)
    rel = m.group(2)
    gap = Q(0) if rel.startswith("equal") else num(rel.split()[0]) * (
        1 if "greater" in rel else -1)
    # the printed sentence says mean(first) = mean(second) + gap, and exactly
    # one of the two data sets is the one showing an x
    if first.endswith("*") == second.endswith("*"):
        raise Unreadable("exactly one of the two data sets must carry the x")
    known, other = sets[first][0], sets[second][0]
    hits = []
    for c in item.choices:
        x = num(c)
        a = mean_(known + [x]) if first.endswith("*") else mean_(known)
        b = mean_(other + [x]) if second.endswith("*") else mean_(other)
        hits.append(a == b + gap)
    return verdict(item, hits, "the value the two means force")


def _sets_with_x(item) -> dict:
    """The two data sets, with the one carrying the unknown marked by a `*`."""
    out = {}
    if item.table:
        rows = table_of(item)
        for r in rows[1:]:
            cells = r[1:]
            name = r[0] + ("*" if "x" in cells else "")
            out[name] = ([num(c) for c in cells if c.strip() != "x"], len(cells))
    for line in item.stem.split("\n"):
        m = re.match(r"^(Data set \w+): (.+)$", line)
        if m and ("," in m.group(2)):
            cells = [c.strip() for c in m.group(2).split(",")]
            name = m.group(1) + ("*" if "x" in cells else "")
            out[name] = ([num(c) for c in cells if c != "x"], len(cells))
    if len(out) != 2:
        raise Unreadable(f"{len(out)} data sets shown, not two")
    return out


def _side(phrase: str, sets: dict) -> str:
    hits = [k for k in sets if k.rstrip("*").lower() in phrase.lower()]
    if len(hits) != 1:
        raise Unreadable(f"{phrase!r} names {len(hits)} of {list(sets)}")
    return hits[0]


def _integer_mean(item) -> str:
    """The list, plus the one integer that makes the whole mean an integer."""
    listed = listed_in(item.stem)
    bound = re.search(r"less than (\d+)", item.stem)
    m = re.search(r"mean of these \d+ integers is ([\d.,]+)", item.stem)
    if bound is None or m is None:
        raise Unreadable(item.stem)
    n = len(listed) + 1
    total = sum(listed, Q(0))
    if mean_(listed) != num(m.group(1)):
        raise AssertionError(f"the stem says the listed mean is {m.group(1)}, it is "
                             f"{float(mean_(listed))}")
    fits = [x for x in range(1, int(bound.group(1)))
            if (total + x) % n == 0 and (total + x) / n > num(m.group(1))]
    if len(fits) != 1:
        raise AssertionError(f"{len(fits)} integers fit the stem, so the largest value "
                             f"is not determined")
    largest = max(max(listed), Q(fits[0]))
    return verdict(item, [num(c) == largest for c in item.choices],
                   "the largest integer the stem allows")


# ------------------------------------------------------- totals and means

REMOVED = [
    re.compile(r"mean score of (\d+) players.*? was ([\d.,]+) points.*?remaining \d+ "
               r"players becomes ([\d.,]+) points", re.S),
    re.compile(r"the (\d+) employees.*? is ([\d.,]+) years.*?reduced to ([\d.,]+) years",
               re.S),
    re.compile(r"mean height of the (\d+) trees.*? is ([\d.,]+) feet.*?remaining \d+ "
               r"trees is ([\d.,]+) feet", re.S),
]
COMBINED = re.compile(r"of (\d+) \w+ and has a mean of ([\d.,]+) \w+\. Data set \w+ "
                      r"consists of the \w+ of (\d+) \w+ and has a mean of ([\d.,]+)",
                      re.S)


def check_mean_totals(item) -> str | None:
    """total = mean x count, run backwards."""
    if item.fmt != "mcq":
        return None
    for pat in REMOVED:
        m = pat.search(item.stem)
        if m:
            n, m1, m2 = int(m.group(1)), num(m.group(2)), num(m.group(3))
            exact = n * m1 - (n - 1) * m2
            return verdict(item, [num(c) == exact for c in item.choices],
                           "the value that was taken away")
    m = COMBINED.search(item.stem)
    if m is None:
        raise Unreadable(item.stem)
    n1, m1, n2, m2 = (num(m.group(i)) for i in (1, 2, 3, 4))
    exact = (n1 * m1 + n2 * m2) / (n1 + n2)
    return verdict(item, [num(c) == exact for c in item.choices],
                   "the mean of the two sets together")


def check_mean_identity(item) -> str | None:
    """Two facts about the mean that hold whatever the numbers are."""
    if item.fmt != "mcq":
        return None
    m = re.search(r"mean and b is the median of (\w+) consecutive integers", item.stem)
    if m:
        seen = set()
        for start in (-7, 0, 3, 41):
            n = _word_number(m.group(1))
            run = [Q(start + i) for i in range(n)]
            seen.add(mean_(run) - median_(run))
        if seen != {Q(0)}:
            raise AssertionError(f"the mean and the median of a run differ by {seen}")
        return verdict(item, [num(c) == 0 for c in item.choices],
                       "the gap between a run's mean and its median")
    if "what fraction of the sum" in item.stem:
        vals = listed_in(item.stem)
        if sum(vals, Q(0)) == 0:
            raise AssertionError("the sum is zero, so no fraction of it is the mean")
        exact = mean_(vals) / sum(vals, Q(0))
        if exact != Q(1, len(vals)):
            raise AssertionError("the mean is not one nth of the sum")
        return verdict(item, [num(c) == exact for c in item.choices],
                       "the mean as a share of the total")
    raise Unreadable(item.stem)


WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
         "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
         "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
         "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20}


def _word_number(w: str) -> int:
    return WORDS[w] if w in WORDS else int(w)


# --------------------------------------------------------- what a total settles

CALC = re.compile(r"(\d+) (\w+) (?:sold|answered|produced|collected) a total of "
                  r"([\d,]+) (\w+)")
CALC_OPTION = re.compile(r"^The (average|median|greatest|least) number of ")


def check_reason_center(item) -> str | None:
    """What a total settles, and where a median must lie."""
    if "could be the median" in item.stem:
        return _median_interval(item)
    m = CALC.search(item.stem)
    if m is None:
        raise Unreadable(item.stem)
    n, total = int(m.group(1)), num(m.group(3))
    # every way the total could have been split between them: what all of them
    # agree on is calculable, what any two of them disagree about is not
    ways = _splits(int(total), n)
    hits = []
    for c in item.choices:
        w = CALC_OPTION.match(c.strip())
        if w is None:
            raise Unreadable(f"{c!r} is not a quantity this reader knows")
        fn = {"average": mean_, "median": median_,
              "greatest": max, "least": min}[w.group(1)]
        hits.append(len({fn(way) for way in ways}) == 1)
    return verdict(item, hits, "the one quantity the total pins down")


def _splits(total: int, n: int) -> list[list[Q]]:
    """Several ways n whole numbers could total this much."""
    if n < 1 or total < 0:
        raise Unreadable(f"{n} of them sharing {total}")
    flat = [Q(total // n + (1 if i < total % n else 0)) for i in range(n)]
    spike = [Q(0)] * (n - 1) + [Q(total)]
    lean = [Q(0)] * (n // 2) + [Q(0)] * (n - n // 2)
    left = total
    for i in range(n - 1, -1, -1):
        take = min(left, 2 * (total // n) + 1)
        lean[i] = Q(take)
        left -= take
    lean[0] += Q(left)
    return [flat, spike, sorted(lean)]


BANDS = re.compile(r"(\w+) \w+ \w+ less than ([\d.,]+) \w+ are placed in (\w+ \w+)\.\s*"
                   r"(\w+) \w+ \w+ at least ([\d.,]+) \w+ but no more than ([\d.,]+) \w+ "
                   r"are placed in (\w+ \w+)\.\s*"
                   r"(\w+) \w+ \w+ more than ([\d.,]+) \w+ are placed in (\w+ \w+)\.")


def _median_interval(item) -> str:
    m = BANDS.search(item.stem)
    if m is None:
        raise Unreadable(item.stem)
    counts = [_word_number(m.group(i).lower()) for i in (1, 4, 8)]
    b1, b2 = num(m.group(2)), num(m.group(6))
    if num(m.group(5)) != b1 or num(m.group(9)) != b2:
        raise AssertionError("the three bands do not meet at the same two bounds")
    n = sum(counts)
    total = re.search(r"these (\d+) ", item.stem)
    if total and int(total.group(1)) != n:
        raise AssertionError(f"the stem counts {total.group(1)}, the bands hold {n}")
    if n % 2 == 0:
        raise Unreadable("an even count puts the median between two values")
    pos = (n + 1) // 2
    band = 0 if pos <= counts[0] else (1 if pos <= counts[0] + counts[1] else 2)

    def possible(v: Q) -> bool:
        return [v < b1, b1 <= v <= b2, v > b2][band]
    hits = [possible(num(c)) for c in item.choices]
    return verdict(item, hits, f"the values {m.group([3, 7, 10][band])} allows")


# ------------------------------------------------------------ must be true

MEANS_SHOWN = re.compile(r"^(\w+ \w+): ([\d.,]+) \w+$", re.M)


def check_must_be_true(item) -> str | None:
    """What two means force, and what an extra value forces.

    Every statement is decided by search: one called false has to produce a
    data set the stem allows where it fails, and one called true has to survive
    the same search. A statement neither way is a statement this script will not
    guess at.
    """
    statements = numbered_statements(item.stem)
    shown = MEANS_SHOWN.findall(item.stem)
    if shown:
        worlds = _two_mean_worlds(item, shown)
        judge = _two_mean_claim
    else:
        worlds = _append_worlds(item)
        judge = _append_claim
    truth = {}
    for i, s in statements.items():
        outcomes = {judge(s, w) for w in worlds}
        if outcomes == {True}:
            truth[i] = True
        elif False in outcomes:
            truth[i] = False
        else:
            raise Unreadable(f"statement {i} could not be decided: {s!r}")
    return verdict(item, roman_options(item, truth),
                   "the statements the stem actually forces")


def _two_mean_worlds(item, shown) -> list[dict]:
    """Every pairing of data sets that the two printed means allow.

    Each group gets the same handful of shapes -- flat, one runaway value, one
    value far below the rest, and random ones -- and the worlds are every pair
    of them, so a statement that happens to hold for matching shapes is still
    tested against mismatched ones.
    """
    m = re.search(r"consisting of (\d+) \w+ each", item.stem)
    if m is None or len(shown) != 2:
        raise Unreadable(item.stem)
    n = int(m.group(1))
    if n < 3:
        raise Unreadable("too few members to build witnesses from")
    names = [s[0] for s in shown]
    shapes = [_shapes(num(s[1]), n) for s in shown]
    out = [{names[0]: a, names[1]: b} for a in shapes[0] for b in shapes[1]]
    for w in out:
        for name, xs in w.items():
            want = num(dict(shown)[name])
            if mean_(xs) != want or min(xs) <= 0 or len(xs) != n:
                raise Unreadable(f"a witness for {name} the stem does not allow")
    return out


def _shapes(mu: Q, n: int) -> list[list[Q]]:
    """Data sets of n positive values with this mean, of several shapes."""
    rng = random.Random(5)
    out = [[mu] * n]
    for share in (Q(1, 2), Q(1, 10)):                  # one value carries a lot
        rest = mu * n * (1 - share) / (n - 1)
        out.append([mu * n * share] + [rest] * (n - 1))
    low = mu / 10                                       # most of them low, one high
    out.append([low] * (n - 1) + [mu * n - low * (n - 1)])
    for _ in range(8):
        xs = [mu * Q(rng.randint(20, 180), 100) for _ in range(n - 1)]
        last = mu * n - sum(xs, Q(0))
        if last > 0:
            out.append(xs + [last])
    return out


def _two_mean_claim(statement: str, world: dict) -> bool:
    """One of the three printed claims, checked against one possible world."""
    s = statement.rstrip(".")
    who = sorted((k for k in world if k.lower() in s.lower()),
                 key=lambda k: s.lower().index(k.lower()))
    if len(who) != 2:
        raise Unreadable(f"{statement!r} names {len(who)} of {list(world)}")
    first, second = who[0], who[1]
    if s.lower().startswith("every"):
        # every member of the first named group beats every member of the second
        return max(world[first]) < min(world[second])
    if "median" in s:
        stat, a, rel, stat2, b = comparison(statement)
        if stat != "median" or stat2 != "median":
            raise Unreadable(statement)
        x = [k for k in world if k.lower() in a.lower()]
        y = [k for k in world if k.lower() in b.lower()]
        if len(x) != 1 or len(y) != 1:
            raise Unreadable(statement)
        return holds(rel, median_(world[x[0]]), median_(world[y[0]]))
    if "at least one" in s:
        # somebody in the first named group is beaten by somebody in the second
        return max(world[first]) > min(world[second])
    raise Unreadable(f"{statement!r} is a claim this reader cannot decide")


APPEND_STEM = re.compile(r"consists of (\d+) integers between ([\d.,]+) and ([\d.,]+)\. "
                         r"Data set (\w+) consists of all the integers in data set (\w+) "
                         r"as well as the integer ([\d.,−-]+)")


def _append_worlds(item) -> list[dict]:
    m = APPEND_STEM.search(item.stem)
    if m is None:
        raise Unreadable(item.stem)
    size, lo, hi = int(m.group(1)), num(m.group(2)), num(m.group(3))
    bn, an, extra = m.group(4), m.group(5), num(m.group(6))
    if hi <= lo or size < 1:
        raise Unreadable(item.stem)
    rng = random.Random(7)
    pools = [[lo] * size, [hi] * size,
             [lo + (hi - lo) * Q(i % 2) for i in range(size)],
             sorted(Q(rng.randint(int(lo), int(hi))) for _ in range(size))]
    for _ in range(30):
        pools.append(sorted(Q(rng.randint(int(lo), int(hi))) for _ in range(size)))
    return [{f"data set {an}": p, f"data set {bn}": sorted(p + [extra])} for p in pools]


def _append_claim(statement: str, world: dict) -> bool:
    """`The mean.` / `The median.` under `which must be less for A than for B`."""
    s = statement.strip().rstrip(".").lower()
    fn = {"the mean": mean_, "the median": median_}.get(s)
    if fn is None:
        raise Unreadable(f"{statement!r} is not a measure this reader knows")
    a, b = sorted(world)                    # A before B, as the question asks
    return fn(world[a]) < fn(world[b])


CHECKS = {
    "ovd.list_stat": check_list_stat,
    "ovd.table_stat": check_table_stat,
    "ovd.bar_read": check_bar_read,
    "ovd.freq_stat": check_freq_stat,
    "ovd.freq_order": check_freq_order,
    "ovd.freq_two_groups": check_freq_two_groups,
    "ovd.freq_choose": check_freq_choose,
    "ovd.compare_sets": check_compare_sets,
    "ovd.sd_compare": check_sd_compare,
    "ovd.measure_effect": check_measure_effect,
    "ovd.odd_measure": check_odd_measure,
    "ovd.new_data_set": check_new_data_set,
    "ovd.box_read": check_box_read,
    "ovd.box_compare": check_box_compare,
    "ovd.unknown_value": check_unknown_value,
    "ovd.mean_totals": check_mean_totals,
    "ovd.mean_identity": check_mean_identity,
    "ovd.reason_center": check_reason_center,
    "ovd.must_be_true": check_must_be_true,
}


# ------------------------------------------- proving the check can fail

def _draw(name: str, want=lambda it: True, seeds: int = 400):
    for seed in range(seeds):
        try:
            item = generate(name, seed)
        except ItemError:
            continue
        if item.fmt == "mcq" and want(item):
            return item
    raise RuntimeError(f"no {name} draw to injure")


def _swap(item, i: int, text: str):
    """Put a different string in one option slot, keeping the key where it is."""
    item.choices = list(item.choices)
    item.choices[i] = text
    return item


def selftest() -> int:
    """Six faults, injected on purpose.

    A check nobody has seen fail is worth nothing, so each of these has to be
    reported, and by the right half of the assertion: three of them are second
    correct answers, one is a tie, one is the key moved to another letter, and
    one is a picture that no longer draws the item its options answer.
    """
    cases = []

    # 1. a second true statement: the key's comparison, said the other way
    #    round, so the strings differ and the mathematics does not
    item = _draw("ovd.compare_sets", lambda it: "is greater than" in it.choices[keyed(it)]
                 or "is less than" in it.choices[keyed(it)])
    key = item.choices[keyed(item)]
    stat, who_a, rel, _, who_b = comparison(key)
    flip = {">": "less than", "<": "greater than"}[rel]
    twin = f"The {stat} {who_b} is {flip} the {stat} {who_a}."
    cases.append(("the key said backwards, which says the same thing",
                  _swap(item, (keyed(item) + 1) % 4, twin), CHECKS["ovd.compare_sets"]))

    # 2. a second statement that is true of the drawn pair -- the shape the
    #    live defect took, and only the pixels can tell
    item = _draw("ovd.box_compare")
    (_, a), (_, b) = many_boxes(item.figure)
    first, second = re.findall(r"of (group \w+)", item.choices[keyed(item)])
    wider = "greater" if (a[4] - a[0]) > (b[4] - b[0]) else "less"
    what = "distances" if "distance" in item.choices[keyed(item)] else "values"
    cases.append(("a range comparison the drawn boxes do force",
                  _swap(item, (keyed(item) + 2) % 4,
                        f"The range of the {what} of {first} is {wider} than the range "
                        f"of the {what} of {second}."),
                  CHECKS["ovd.box_compare"]))

    # 3. a tie: a second data set with exactly the key's mean, built by doubling
    #    every frequency, so no two options print the same and no value repeats
    item = _draw("ovd.freq_choose", lambda it: "greatest mean" in it.stem)
    vals, freqs = as_table(item.choices[keyed(item)])
    twin = ", ".join(f"{v} (frequency {int(f) * 2})" for v, f in zip(vals, freqs))
    cases.append(("a second data set with the key's mean",
                  _swap(item, (keyed(item) + 1) % 4, twin), CHECKS["ovd.freq_choose"]))

    # 4. the right answer attached to the wrong letter
    item = _draw("ovd.odd_measure")
    item.answer = LETTERS[(keyed(item) + 1) % 4]
    cases.append(("the key moved a letter", item, CHECKS["ovd.odd_measure"]))

    # 5. a picture that drifted from the options it is supposed to answer
    item = _draw("ovd.bar_read")
    other = _draw("ovd.bar_read", lambda it: it.figure != item.figure)
    item.figure = other.figure
    cases.append(("a bar graph that drew somebody else's data", item,
                  CHECKS["ovd.bar_read"]))

    # 6. the second defect this script found, put back: another value inside
    #    the band that holds the median
    def band_zero(it):
        m = BANDS.search(it.stem)
        return m is not None and num(it.choices[keyed(it)]) < num(m.group(2))

    item = _draw("ovd.reason_center", band_zero)
    half = num(item.choices[keyed(item)]) / 2
    cases.append(("half the key, which is inside the band too",
                  _swap(item, (keyed(item) + 3) % 4,
                        f"{float(half):g}"), CHECKS["ovd.reason_center"]))

    bad = 0
    for what, item, checker in cases:
        try:
            checker(item)
            print(f" FAIL  {what}: not caught")
            bad = 1
        except (AssertionError, Unreadable) as exc:
            print(f"  ok   {what}: {exc}")
    return bad


# a finished item is stamped with the name of the frame it was drawn in, not
# with the template it came from: this is the way back, first match winning
OWNER = [("ovd.list.", "ovd.list_stat"), ("ovd.table.", "ovd.table_stat"),
         ("ovd.bar.", "ovd.bar_read"), ("ovd.freq.order", "ovd.freq_order"),
         ("ovd.freq.choose.", "ovd.freq_choose"),
         ("ovd.freq.median_gap", "ovd.freq_two_groups"),
         ("ovd.freq.compare_means", "ovd.freq_two_groups"),
         ("ovd.freq.", "ovd.freq_stat"), ("ovd.compare.", "ovd.compare_sets"),
         ("ovd.spread.", "ovd.sd_compare"), ("ovd.change.shift", "ovd.new_data_set"),
         ("ovd.change.append", "ovd.new_data_set"),
         ("ovd.change.", "ovd.measure_effect"), ("ovd.odd_measure", "ovd.odd_measure"),
         ("ovd.box.compare", "ovd.box_compare"), ("ovd.box.", "ovd.box_read"),
         ("ovd.unknown.", "ovd.unknown_value"),
         ("ovd.mean.removed", "ovd.mean_totals"),
         ("ovd.mean.combined", "ovd.mean_totals"), ("ovd.mean.", "ovd.mean_identity"),
         ("ovd.reason.calculable", "ovd.reason_center"),
         ("ovd.reason.median_interval", "ovd.reason_center"),
         ("ovd.reason.", "ovd.must_be_true")]


def check_sources() -> int:
    """The same assertions over the official option sets, as transcribed."""
    from satbank.topic import load_topics

    bad = checked = 0
    for src in load_topics()["one_variable_data"].sources:
        item = src.build(random.Random(0))
        if item.fmt != "mcq":
            continue
        checker = next((CHECKS[name] for start, name in OWNER
                        if item.template.startswith(start)), None)
        if checker is None:
            print(f" ????  {src.id}: no check for {item.template}")
            bad += 1
            continue
        try:
            if checker(item) is not None:
                checked += 1
        except (AssertionError, Unreadable) as exc:
            bad += 1
            print(f" FAIL  {src.id} ({item.template}): {exc}")
            print(item.pretty())
    print(f"\n{checked} official option sets read back"
          + ("" if not bad else f", {bad} of them a defect"))
    return 1 if bad else 0


# ------------------------------------------------------------------ driver

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--draws", type=int, default=600,
                    help="seeds to try per template (default 600)")
    ap.add_argument("--template", action="append",
                    help="check only this template; repeatable")
    ap.add_argument("--selftest", action="store_true",
                    help="inject known-bad option sets and show each one caught")
    ap.add_argument("--sources", action="store_true",
                    help="check the official option sets instead of draws")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.sources:
        return check_sources()

    worst = read = 0
    for name in args.template or list(CHECKS):
        checker = CHECKS[name]
        made = skipped = bad = 0
        what = ""
        for seed in range(args.draws):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            try:
                got = checker(item)
            except (AssertionError, Unreadable) as exc:
                bad += 1
                if bad == 1:
                    print(f"\n{name} seed {seed}: {exc}")
                    print(item.pretty())
                continue
            if got is None:
                skipped += 1
            else:
                made += 1
                what = got
        read += made
        mark = "  ok  " if not bad else " FAIL "
        tail = f", {skipped:,} grid-ins" if skipped else ""
        if not made and skipped:
            what = "every draw is a grid-in: no options to read"
        print(f"{mark} {name:<24} {made:>5,} items, {bad} defects{tail}   ({what})")
        worst |= 1 if bad else 0
    print(f"\n{read:,} option sets read back")
    return worst


if __name__ == "__main__":
    sys.exit(main())
