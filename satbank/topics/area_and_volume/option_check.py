"""Read the wrong options back, and check that only one of them is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct: `assemble_text` shuffles four strings and records
which one is the key, `audit` re-derives the key, `structure` counts surface
forms. An item with two right answers satisfies every one of them.

This script closes that hole for the three templates in this topic whose options
are expressions rather than measured values -- `expression.measure`,
`expression.symbolic_volume` and `scaling.solid`. It parses the printed option
strings, and the printed stem, back into arithmetic, decides each option's
status from that arithmetic alone, and asserts that exactly one option has the
property the stem asks for and that it is the keyed one.

It does the same for the five templates whose figure carries half the question:
there it recovers the plotted points, the drawn segments and the measurements
printed on the figure from the SVG itself, and asks whether the picture agrees
with the options -- the one failure mode `satbank check` has no way to see,
because the audit re-derives the answer from the parameters the picture was
meant to be drawn from.

It imports no template, no renderer and no solver: `generate` is used only to
obtain the finished item, in the state a student would receive it.

    PYTHONPATH=. python3 satbank/topics/area_and_volume/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 5000 --template expression.measure
    PYTHONPATH=. python3 .../option_check.py --self-test

Exits non-zero on the first kind of defect it finds, and prints the item.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import replace

from satbank.item import ItemError
from satbank.registry import generate

MINUS = "−"
PROBE = (2.0, 3.0, 5.0, 7.0)      # where two expressions are compared
TOL = 1e-9


class Unreadable(Exception):
    """The printed text is not something this reader understands."""


# ------------------------------------------- printed expression -> a number

def _split(text: str) -> list[str]:
    """Top-level terms of a sum, each keeping its own sign."""
    out, depth, start = [], 0, 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch in "+-−" and depth == 0 and i > start:
            out.append(text[start:i])
            start = i
    out.append(text[start:])
    return [t for t in out if t.strip()]


def _factors(term: str) -> list[tuple[bool, str]]:
    """A term as a product: 3 * 39, 2 · 94 · 94, 104/3 -- each part with its
    operator, so a printed fraction divides rather than multiplies."""
    out, depth, start, over = [], 0, 0, False
    for i, ch in enumerate(term):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch in "*·×/" and depth == 0:
            out.append((over, term[start:i]))
            over, start = ch == "/", i + 1
    out.append((over, term[start:]))
    return out


ATOM = re.compile(r"(\d+\.\d+|\d*)(π?)(?:\(([^()]*(?:\([^()]*\)[^()]*)*)\)|([a-z]))?([²³]?)$")
RADICAL = re.compile(r"(\d+\.\d+|\d*)√(?:\((.+)\)|(π)|(\d+))$")


def _atom(text: str, x: float) -> float:
    """One factor: 39, π, 4πr², π(2r)³, (s + 4)³, r, 8√2, √(2π)."""
    rad = RADICAL.fullmatch(text)
    if rad:
        digits, group, pi, whole = rad.groups()
        under = (value_of(group, x) if group is not None else
                 math.pi if pi else float(whole))
        return (float(digits) if digits else 1.0) * math.sqrt(under)
    if "√" in text:
        raise Unreadable(text)
    m = ATOM.fullmatch(text)
    if m is None:
        raise Unreadable(text)
    digits, pi, group, var, power = m.groups()
    if not any((digits, pi, group, var)):
        raise Unreadable(text)
    value = float(digits) if digits else 1.0
    if pi:
        value *= math.pi
    exp = {"": 1, "²": 2, "³": 3}[power]
    if group is not None:
        value *= value_of(group, x) ** exp
    elif var is not None:
        value *= x ** exp
    elif exp != 1:
        value **= exp
    return value


def value_of(text: str, x: float = 1.0) -> float:
    """What a printed expression is worth, with every letter standing for x."""
    t = text.replace(" ", "").replace(MINUS, "-").replace(",", "")
    total = 0.0
    for term in _split(t):
        sign = 1.0
        while term[:1] in "+-":
            if term[0] == "-":
                sign = -sign
            term = term[1:]
        product = 1.0
        for over, f in _factors(term):
            product = product / _atom(f, x) if over else product * _atom(f, x)
        total += sign * product
    return total


def same(a: float, b: float) -> bool:
    return abs(a - b) <= TOL * max(1.0, abs(a), abs(b))


# --------------------------------------------- a drawn grid -> data points

def _floats(pairs) -> list[tuple[float, float]]:
    return [(float(a), float(b)) for a, b in pairs]


def grid(svg: str):
    """Where the origin is and how many pixels a unit takes, from the picture.

    The axes locate the origin and the spacing of the gridlines gives the scale.
    Nothing about the item's parameters is consulted: this is what a reader with
    a ruler would get, so it checks the picture against the options rather than
    the options against each other.
    """
    ax = re.findall(r'<line class="ax" x1="([-\d.]+)" y1="([-\d.]+)" '
                    r'x2="([-\d.]+)" y2="([-\d.]+)"', svg)
    horizontal = [a for a in ax if a[1] == a[3]]
    vertical = [a for a in ax if a[0] == a[2]]
    if len(horizontal) != 1 or len(vertical) != 1:
        raise Unreadable("the axes are not one horizontal and one vertical")
    y0, x0 = float(horizontal[0][1]), float(vertical[0][0])
    gr = re.findall(r'<line class="gr" x1="([-\d.]+)" y1="[-\d.]+" '
                    r'x2="([-\d.]+)" y2="[-\d.]+"', svg)
    xs = sorted({float(a) for a, b in gr if a == b})
    gaps = {round(b - a, 6) for a, b in zip(xs, xs[1:])}
    if len(gaps) != 1:
        raise Unreadable("the gridlines are not evenly spaced")
    px = gaps.pop()
    return lambda cx, cy: ((float(cx) - x0) / px, (y0 - float(cy)) / px)


def plotted(svg: str) -> list[tuple[float, float]]:
    """The plotted points, in data coordinates."""
    at = grid(svg)
    return [at(cx, cy) for cx, cy in re.findall(
        r'<circle class="pt" cx="([-\d.]+)" cy="([-\d.]+)" r="4.5"', svg)]


def drawn(svg: str) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """The drawn segments, as pairs of endpoints in data coordinates."""
    at = grid(svg)
    return [(at(a, b), at(c, d)) for a, b, c, d in re.findall(
        r'<line class="sg" x1="([-\d.]+)" y1="([-\d.]+)" '
        r'x2="([-\d.]+)" y2="([-\d.]+)"', svg)]


def circumcircle(pts):
    """The centre and radius of the circle through three plotted points."""
    (x1, y1), (x2, y2), (x3, y3) = pts
    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    if d == 0:
        raise Unreadable("the three drawn points are collinear")
    s1, s2, s3 = x1 * x1 + y1 * y1, x2 * x2 + y2 * y2, x3 * x3 + y3 * y3
    cx = (s1 * (y2 - y3) + s2 * (y3 - y1) + s3 * (y1 - y2)) / d
    cy = (s1 * (x3 - x2) + s2 * (x1 - x3) + s3 * (x2 - x1)) / d
    return (cx, cy), math.hypot(x1 - cx, y1 - cy)


def shoelace(pts) -> float:
    total = 0.0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        total += x1 * y2 - x2 * y1
    return abs(total) / 2


# ------------------------------------------------------ printed stem -> facts

def _int(text: str) -> int:
    return int(text.replace(",", ""))


def _keyed(item) -> int:
    return "ABCD".index(item.answer)


def _verdict(item, hits: list[bool], what: str) -> str:
    if hits.count(True) != 1:
        raise AssertionError(f"{hits.count(True)} of the four options are correct")
    if not hits[_keyed(item)]:
        raise AssertionError("the keyed option is not the correct one")
    return what


def _answers(item, want: float, what: str) -> str:
    """Exactly one option is the value the figure and the stem determine.

    A grid-in has no options to compare, so there the picture is checked
    against the answer the student is expected to enter.
    """
    if item.fmt == "spr":
        if not same(value_of(item.answer), want):
            raise AssertionError(f"the figure gives {want}, the answer is {item.answer!r}")
        return what + ", entered"
    hits = [same(value_of(c), want) for c in item.choices]
    return _verdict(item, hits, what)


# --------------------------------------------------------- expression.measure

def check_expression(item) -> str:
    """Exactly one printed expression is worth the measure the stem asks for."""
    stem = item.stem
    asked = "area" if re.search(r"gives the area", stem) else "perimeter"
    sq = re.search(r"length of each side of a square is ([\d,]+)", stem)
    rect = re.search(r"a length of ([\d,]+).*?a width of ([\d,]+)", stem)
    if sq:
        s = _int(sq.group(1))
        want = s * s if asked == "area" else 4 * s
        what = f"square {asked}"
    elif rect:
        l, w = _int(rect.group(1)), _int(rect.group(2))
        want = l * w if asked == "area" else 2 * (l + w)
        what = f"rectangle {asked}"
    else:
        raise Unreadable(stem)
    hits = [same(value_of(c), want) for c in item.choices]
    return _verdict(item, hits, what)


# ------------------------------------------------- expression.symbolic_volume

def _height(stem: str):
    """The height the sentence states, as a function of the base dimension."""
    m = re.search(r"a height that is (.+?) offer the optimal", stem)
    if m is None:
        raise Unreadable(stem)
    phrase = m.group(1)
    n = re.search(r"(\d+)", phrase)
    if n is None:
        raise Unreadable(phrase)
    c = int(n.group(1))
    if "times" in phrase:
        return lambda x: c * x
    if "shorter than twice" in phrase:
        return lambda x: 2 * x - c
    if "more than twice" in phrase:
        return lambda x: 2 * x + c
    if "longer than" in phrase:
        return lambda x: x + c
    raise Unreadable(phrase)


def check_symbolic(item) -> str:
    """Exactly one printed expression is the volume the sentence describes."""
    stem = item.stem
    height = _height(stem)
    if "right cylindrical" in stem:
        base, what = (lambda x: math.pi * x * x), "cylinder volume"
    elif "right square prism" in stem:
        base, what = (lambda x: x * x), "square prism volume"
    else:
        raise Unreadable(stem)
    var = re.search(r"where (\w) is the", stem)
    if var is None:
        raise Unreadable(stem)
    var = var.group(1)

    hits = []
    for c in item.choices:
        head, _, body = c.partition("=")
        if head.strip() != "V" or not body.strip():
            raise Unreadable(c)
        letters = set(re.findall(r"[a-z]", body))
        if letters - {var}:
            raise AssertionError(f"option {c!r} uses a letter the stem never defines")
        hits.append(all(same(value_of(body, x), base(x) * height(x)) for x in PROBE))
    return _verdict(item, hits, what)


# --------------------------------------------------------------- scaling.solid

WORD_FACTOR = {"half": 0.5, "one third": 1 / 3, "twice": 2.0, "three times": 3.0,
               "four times": 4.0}


def _factor(text: str) -> float:
    for word, value in WORD_FACTOR.items():
        if text.endswith(word):
            return value
    m = re.search(r"(\d+)/(\d+) times$", text)
    if m:
        return int(m.group(1)) / int(m.group(2))
    m = re.search(r"(\d+) times$", text)
    if m:
        return float(m.group(1))
    raise Unreadable(text)


def check_scaling(item) -> str:
    """Either which pair of factors multiplies the volume, or what it becomes."""
    stem = item.stem
    pair = re.search(r"volume that is ([\d,]+) times as large", stem)
    if pair:
        mult = _int(pair.group(1))
        hits = []
        for c in item.choices:
            m = re.fullmatch(r"R = (\d*)r and H = (\d*)h", c.strip())
            if m is None:
                raise Unreadable(c)
            a = int(m.group(1) or 1)
            b = int(m.group(2) or 1)
            hits.append(same(a * a * b, mult))
        return _verdict(item, hits, "which pair of factors")

    m = re.search(r"volume of right circular cylinder A is ([\d,]+) cubic", stem)
    n = re.search(r"cylinder with (.+?) the radius and (.+?) the height", stem)
    if m is None or n is None:
        raise Unreadable(stem)
    want = _int(m.group(1)) * _factor(n.group(1)) ** 2 * _factor(n.group(2))
    hits = [same(value_of(c), want) for c in item.choices]
    return _verdict(item, hits, "the scaled volume")


# ------------------------------------------- the items whose figure is the item

def check_circle(item) -> str:
    """The circle drawn through the three plotted points fixes k."""
    pts = plotted(item.figure)
    if len(pts) != 3:
        raise Unreadable(f"{len(pts)} points plotted, not three")
    _, r = circumcircle(pts)
    want = 2 * r if "circumference" in item.stem else r * r
    return _answers(item, want, "the drawn circle")


def check_triangle(item) -> str:
    """The triangle drawn on the grid fixes its own area."""
    pts = plotted(item.figure)
    if len(pts) != 3:
        raise Unreadable(f"{len(pts)} points plotted, not three")
    return _answers(item, shoelace(pts), "the drawn triangle")


def check_quad(item) -> str:
    """The quadrilateral drawn on the grid fixes its area, side and perimeter."""
    segs = drawn(item.figure)
    if len(segs) != 4:
        raise Unreadable(f"{len(segs)} sides drawn, not four")
    corners = []
    for a, b in segs:
        for p in (a, b):
            if p not in corners:
                corners.append(p)
    if len(corners) != 4:
        raise Unreadable(f"{len(corners)} distinct corners, not four")
    # walk the drawn sides so the corners come round in order
    order, seen = [segs[0][0]], {segs[0][0]}
    while len(order) < 4:
        here = order[-1]
        nxt = next((b if a == here else a) for a, b in segs
                   if here in (a, b) and (b if a == here else a) not in seen)
        order.append(nxt)
        seen.add(nxt)
    side = math.dist(order[0], order[1])
    if "the area" in item.stem:
        want, what = shoelace(order), "the drawn quadrilateral's area"
    elif "the perimeter" in item.stem:
        want, what = sum(math.dist(p, q) for p, q in
                         zip(order, order[1:] + order[:1])), "its perimeter"
    else:
        want, what = side, "one of its sides"
    return _answers(item, want, what)


def check_leg(item) -> str:
    """The drawn leg and the stated area fix the other leg."""
    segs = drawn(item.figure)
    if len(segs) != 1:
        raise Unreadable(f"{len(segs)} segments drawn, not one")
    (a, b), = segs
    m = re.search(r"area of this triangle is (.+?) square units", item.stem)
    if m is None:
        raise Unreadable(item.stem)
    return _answers(item, 2 * value_of(m.group(1)) / math.dist(a, b),
                    "the other leg of the drawn triangle")


def check_similar(item) -> str:
    """Whatever fixes the scale factor -- figure, table or sentence -- fixes
    the answer, and exactly one option is it."""
    stem = item.stem
    if item.figure:
        labels = re.findall(r'<text class="lb"[^>]*>([^<]+)</text>', item.figure)
        if len(labels) != 3:
            raise Unreadable(f"{len(labels)} measurements on the figure, not three")
        big, small, base = (value_of(t.split()[0]) for t in labels)
        if small == 0:
            raise Unreadable("the smaller rectangle is drawn with no side")
        want, what = base * big / small, "the labelled rectangles"
    elif item.table:
        m = re.search(r"The length of (?:side )?\w+ is ([\d,]+(?:\.\d+)?)", stem)
        rows = [r for r in item.table if r[0].lower().startswith("triangle")]
        if m is None or len(rows) != 2:
            raise Unreadable(stem)
        p1, p2 = (value_of(r[1]) for r in rows)
        want, what = value_of(m.group(1)) * p2 / p1, "the tabulated perimeters"
    elif " = " in stem:
        m = re.search(r"If \w\w = (\d*)\w\w and the perimeter of triangle \w+ is "
                      r"([\d,]+)", stem)
        if m is None:
            raise Unreadable(stem)
        want = float(m.group(1) or 1) * value_of(m.group(2))
        what = "the stated ratio"
    else:
        m = re.search(r"length of side \w+ is ([\d,]+), and the perimeter of triangle "
                      r"\w+ is ([\d,]+)\. The length of side \w+ is ([\d,]+)", stem)
        if m is None:
            raise Unreadable(stem)
        s1, p, s2 = (value_of(g) for g in m.groups())
        want, what = p * s2 / s1, "the two corresponding sides"
    return _answers(item, want, what)


CHECKS = {
    "expression.measure": check_expression,
    "expression.symbolic_volume": check_symbolic,
    "scaling.solid": check_scaling,
    "coord.circle_3pt": check_circle,
    "coord.triangle_area": check_triangle,
    "coord.square_diagonals": check_quad,
    "coord.leg_from_area": check_leg,
    "similar.linear": check_similar,
}


# ------------------------------------------------------------------ self-test

def self_test() -> int:
    """A check nobody has seen fail is worth nothing.

    Four faults, one of each kind the check exists to catch: a second correct
    option, a right answer on the wrong letter, the key offered twice, and a
    figure that no longer draws the item its options answer.
    """
    faults = []

    item = generate("expression.measure", 4)
    i = next(j for j in range(4) if j != _keyed(item))
    doubled = replace(item, choices=[c if j != i else item.choices[_keyed(item)] + " * 1"
                                     for j, c in enumerate(item.choices)])
    faults.append(("a second correct expression", "expression.measure", doubled))

    item = generate("expression.symbolic_volume", 3)
    moved = replace(item, answer="ABCD"[(_keyed(item) + 1) % 4])
    faults.append(("the key on the wrong letter", "expression.symbolic_volume", moved))

    item = generate("scaling.solid", 1)
    while "times as large" not in item.stem:
        item = generate("scaling.solid", item.seed + 1)
    i = next(j for j in range(4) if j != _keyed(item))
    twin = replace(item, choices=[c if j != i else item.choices[_keyed(item)]
                                  for j, c in enumerate(item.choices)])
    faults.append(("the key offered twice", "scaling.solid", twin))

    item = generate("coord.triangle_area", 0)
    other = next(generate("coord.triangle_area", seed) for seed in range(1, 40)
                 if generate("coord.triangle_area", seed).figure != item.figure)
    drifted = replace(item, figure=other.figure)
    faults.append(("a figure that drifted from its answer", "coord.triangle_area",
                   drifted))

    bad = 0
    for what, name, broken in faults:
        try:
            CHECKS[name](broken)
        except (AssertionError, Unreadable) as exc:
            print(f"  ok   caught {what}: {exc}")
            continue
        bad += 1
        print(f" FAIL  {what} went unnoticed")
        print(broken.pretty())
    return bad


# ------------------------------------------------------------------- driver

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--draws", type=int, default=4000,
                    help="seeds to try per template (default 4000)")
    ap.add_argument("--template", action="append",
                    help="check only this template; repeatable")
    ap.add_argument("--self-test", action="store_true",
                    help="prove the check can fail, and stop")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    worst = 0
    for name in args.template or list(CHECKS):
        checker = CHECKS[name]
        made, bad, what = 0, 0, ""
        for seed in range(args.draws):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            made += 1
            try:
                what = checker(item)
            except (AssertionError, Unreadable) as exc:
                bad += 1
                if bad == 1:
                    print(f"\n{name} seed {seed}: {exc}")
                    print(item.pretty())
        mark = "  ok  " if not bad else " FAIL "
        print(f"{mark} {name:<28} {made:>6,} items, {bad} defects   ({what})")
        worst |= 1 if bad else 0
    return worst


if __name__ == "__main__":
    sys.exit(main())
