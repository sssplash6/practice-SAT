"""Read the four printed options back, and check only one of them is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct, because nothing in the engine reads the wrong
options as mathematics -- they are strings that `assemble_text` shuffled. An
item with two right answers therefore passes every gate the engine has.

This script closes that hole for the templates whose options are text. It parses
the option strings themselves -- and, for the graph items, the drawn SVG -- back
into linear algebra, decides each option's status from that algebra alone, and
asserts that exactly one option has the property the stem asks for and that it is
the keyed one. It imports no template, no renderer and no solver: `generate` is
used only to obtain the finished item, exactly as a student would receive it.

    PYTHONPATH=. python3 satbank/topics/systems_of_linear_equations/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 2000 --template sys.solve_pair

Exits non-zero on the first kind of defect it finds, and prints the item.
"""

from __future__ import annotations

import argparse
import re
import sys
from fractions import Fraction as Q

from satbank.item import ItemError
from satbank.registry import generate

MINUS = "−"


class Unreadable(Exception):
    """The printed text is not something this reader understands."""


# --------------------------------------------------- printed text -> numbers

def _num(text: str) -> Q:
    """A printed number: 8, −11, 2,300, 9/7, 3.5."""
    t = text.replace(MINUS, "-").replace(",", "").strip()
    if "/" in t:
        a, b = t.split("/", 1)
        return Q(int(a), int(b))
    return Q(t)


# one term of a printed side: an optional sign, then a number (bare, a bracketed
# fraction, a loose fraction or a decimal), then an optional variable letter
TERM = re.compile(r"([+-]?)(?:\((\d+)/(\d+)\)|(\d+)/(\d+)|(\d+\.\d+)|(\d+))?([a-z])?")


def side(text: str) -> tuple[dict, Q]:
    """One side of an equation as ({variable: coefficient}, constant)."""
    t = text.replace(MINUS, "-").replace(",", "").replace(" ", "")
    coef, const, i = {}, Q(0), 0
    while i < len(t):
        m = TERM.match(t, i)
        if m is None or m.end() == i:
            raise Unreadable(f"{text!r} at {t[i:]!r}")
        sign, pn, pd, fn, fd, dec, whole, var = m.groups()
        if pn:
            v = Q(int(pn), int(pd))
        elif fn:
            v = Q(int(fn), int(fd))
        elif dec:
            v = Q(dec)
        elif whole:
            v = Q(int(whole))
        elif var:
            v = Q(1)
        else:
            raise Unreadable(f"{text!r} at {t[i:]!r}")
        if sign == "-":
            v = -v
        if var:
            coef[var] = coef.get(var, Q(0)) + v
        else:
            const += v
        i = m.end()
    return coef, const


def row(eq: str) -> tuple[dict, Q]:
    """A printed equation as the row (coefficients, constant), everything moved
    to the left of the equals sign. `3y = 5x` and `−5x + 3y = 0` read alike."""
    if eq.count("=") != 1:
        raise Unreadable(eq)
    lhs, rhs = eq.split("=")
    lc, lk = side(lhs)
    rc, rk = side(rhs)
    for v, c in rc.items():
        lc[v] = lc.get(v, Q(0)) - c
    return {v: c for v, c in lc.items() if c != 0}, rk - lk


def system(option: str) -> list:
    """A system printed as one option: `eq1, eq2`."""
    parts = [p for p in option.split(", ") if "=" in p]
    if len(parts) != 2:
        raise Unreadable(option)
    return [row(p) for p in parts]


def unknowns(rows: list) -> list:
    names = sorted(set().union(*(set(r[0]) for r in rows)))
    if len(names) != 2:
        raise Unreadable(f"a system in {len(names)} unknowns: {names}")
    return names


def matrix(rows: list) -> tuple:
    u, v = unknowns(rows)
    (c1, k1), (c2, k2) = rows
    return (c1.get(u, Q(0)), c1.get(v, Q(0)), k1,
            c2.get(u, Q(0)), c2.get(v, Q(0)), k2)


def solution_set(rows: list) -> str:
    """'one', 'none' or 'many' -- straight off the two determinants."""
    a1, b1, k1, a2, b2, k2 = matrix(rows)
    if a1 * b2 - a2 * b1 != 0:
        return "one"
    if a1 * k2 - a2 * k1 == 0 and b1 * k2 - b2 * k1 == 0:
        return "many"
    return "none"


def crossing(rows: list) -> tuple:
    a1, b1, k1, a2, b2, k2 = matrix(rows)
    det = a1 * b2 - a2 * b1
    if det == 0:
        raise Unreadable("those two lines do not cross at one point")
    return (k1 * b2 - k2 * b1) / det, (a1 * k2 - a2 * k1) / det


def satisfies(r: tuple, values: dict) -> bool:
    coef, const = r
    return sum(c * values.get(v, Q(0)) for v, c in coef.items()) == const


def point(text: str) -> tuple:
    """`(2, 3)` or `(−4, −8)`."""
    m = re.fullmatch(r"\(([^,]+),([^,]+)\)", text.strip())
    if m is None:
        raise Unreadable(text)
    return _num(m.group(1)), _num(m.group(2))


AFFINE = re.compile(r"([+-]?)(\d*)([a-z]?)(?:/(\d+))?")


def affine(text: str, var: str) -> tuple:
    """`−8r/7 + 9/7` as (coefficient of r, constant)."""
    t = text.replace(MINUS, "-").replace(" ", "")
    slope, const, i = Q(0), Q(0), 0
    while i < len(t):
        m = AFFINE.match(t, i)
        if m is None or m.end() == i:
            raise Unreadable(f"{text!r} at {t[i:]!r}")
        sign, whole, name, den = m.groups()
        if name and name != var:
            raise Unreadable(f"{text!r} mentions {name!r}, not {var!r}")
        v = Q(int(whole) if whole else 1, int(den) if den else 1)
        if sign == "-":
            v = -v
        if name:
            slope += v
        else:
            const += v
        i = m.end()
    return slope, const


def parametric(text: str, var: str) -> tuple:
    """`(r, −8r/7 + 9/7)` as the two affine functions of r."""
    m = re.fullmatch(r"\((.+),(.+)\)", text.strip())
    if m is None:
        raise Unreadable(text)
    return affine(m.group(1), var), affine(m.group(2), var)


# ------------------------------------------------ a drawn grid -> two lines

def _svg_num(text: str) -> Q:
    return Q(text) if "/" in text else Q(text)


def lines_from_svg(svg: str) -> list:
    """The two drawn lines as (slope, intercept), read back out of the picture.

    The grid gives the scale: the axes locate the origin in pixels and the
    spacing of the gridlines gives the pixels per unit. Nothing about the item's
    parameters is consulted -- this is what a reader with a ruler would get.
    """
    ax = re.findall(r'<line class="ax" x1="([^"]+)" y1="([^"]+)" '
                    r'x2="([^"]+)" y2="([^"]+)"', svg)
    if len(ax) != 2:
        raise Unreadable("a grid with something other than two axes")
    horizontal = [a for a in ax if a[1] == a[3]]
    vertical = [a for a in ax if a[0] == a[2]]
    if len(horizontal) != 1 or len(vertical) != 1:
        raise Unreadable("the axes are not one horizontal and one vertical")
    y0 = _svg_num(horizontal[0][1])
    x0 = _svg_num(vertical[0][0])

    gr = re.findall(r'<line class="gr" x1="([^"]+)" y1="[^"]+" '
                    r'x2="([^"]+)" y2="[^"]+"', svg)
    xs = sorted({_svg_num(a) for a, b in gr if a == b})
    gaps = {b - a for a, b in zip(xs, xs[1:])}
    if len(gaps) != 1:
        raise Unreadable("the gridlines are not evenly spaced")
    px = gaps.pop()

    out = []
    for x1, ya, x2, yb in re.findall(
            r'<line class="sg" x1="([^"]+)" y1="([^"]+)" '
            r'x2="([^"]+)" y2="([^"]+)"', svg):
        ax1, ay1 = (_svg_num(x1) - x0) / px, (y0 - _svg_num(ya)) / px
        ax2, ay2 = (_svg_num(x2) - x0) / px, (y0 - _svg_num(yb)) / px
        if ax1 == ax2:
            raise Unreadable("a vertical drawn line has no slope")
        m = (ay2 - ay1) / (ax2 - ax1)
        out.append((m, ay1 - m * ax1))
    if len(out) != 2:
        raise Unreadable(f"{len(out)} lines drawn, not two")
    return out


# ------------------------------------------------------------- the checks

def _keyed(item) -> int:
    return "ABCD".index(item.answer)


def check_pick(item) -> str:
    """Exactly one of the four systems has the solution set the stem names."""
    want = "many" if "infinitely" in item.stem else "none"
    got = [solution_set(system(c)) for c in item.choices]
    if got.count(want) != 1:
        raise AssertionError(f"{got.count(want)} options have {want!r}: {got}")
    if got[_keyed(item)] != want:
        raise AssertionError(f"the key is {got[_keyed(item)]!r}, not {want!r}")
    return want


def check_pair(item) -> str:
    """Exactly one of the four points satisfies both printed equations."""
    rows = [row(line) for line in item.stem.split("\n")[:2]]
    u, v = unknowns(rows)
    hits = []
    for c in item.choices:
        x, y = point(c)
        hits.append(all(satisfies(r, {u: x, v: y}) for r in rows))
    if hits.count(True) != 1:
        raise AssertionError(f"{hits.count(True)} options satisfy both equations")
    if not hits[_keyed(item)]:
        raise AssertionError("the keyed point does not satisfy both equations")
    return "one point"


def check_graph(item) -> str:
    """The options must agree with the picture, not merely with each other."""
    (m1, b1), (m2, b2) = lines_from_svg(item.figure)
    if m1 == m2:
        raise AssertionError("the two drawn lines are parallel")
    x = (b2 - b1) / (m1 - m2)
    y = m1 * x + b1
    if item.choices[0].count("=") == 2:              # options are systems
        hits = []
        for c in item.choices:
            rows = system(c)
            hits.append(solution_set(rows) == "one" and crossing(rows) == (x, y))
        what = "system"
    else:                                            # options are points
        hits = [point(c) == (x, y) for c in item.choices]
        what = "point"
    if hits.count(True) != 1:
        raise AssertionError(f"{hits.count(True)} options name the drawn crossing "
                             f"point ({x}, {y})")
    if not hits[_keyed(item)]:
        raise AssertionError(f"the drawn lines cross at ({x}, {y}), which is not "
                             f"the keyed option")
    return f"drawn crossing as a {what}"


def check_other(item) -> str:
    """Exactly one of the four equations leaves the printed system empty."""
    m = re.search(r"linear system is (.+?)\. The system", item.stem)
    if m is None:
        raise Unreadable(item.stem)
    given = row(m.group(1))
    hits = [solution_set([given, row(c)]) == "none" for c in item.choices]
    if hits.count(True) != 1:
        raise AssertionError(f"{hits.count(True)} options empty the system")
    if not hits[_keyed(item)]:
        raise AssertionError("the keyed equation does not empty the system")
    return "empty system"


def check_all_points(item) -> str:
    """Exactly one parameterized point lies on both lines for every r."""
    rows = [row(line) for line in item.stem.split("\n")[:2]]
    u, v = unknowns(rows)
    var = re.search(r"For each real number (\w)", item.stem).group(1)
    hits = []
    for c in item.choices:
        (mx, cx), (my, cy) = parametric(c, var)
        hits.append(all(
            all(satisfies(r, {u: mx * t + cx, v: my * t + cy}) for r in rows)
            for t in (Q(0), Q(1), Q(-3), Q(7, 2))))
    if hits.count(True) != 1:
        raise AssertionError(f"{hits.count(True)} options lie on both lines")
    if not hits[_keyed(item)]:
        raise AssertionError("the keyed point does not lie on both lines")
    return "every point of the line"


CHECKS = {
    "sys.pick_no_solution": check_pick,
    "sys.solve_pair": check_pair,
    "sys.graph_solution": check_graph,
    "sys.other_equation": check_other,
    "sys.all_solutions": check_all_points,
}


# ------------------------------------------------------------------ driver

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--draws", type=int, default=600,
                    help="seeds to try per template (default 600)")
    ap.add_argument("--template", action="append",
                    help="check only this template; repeatable")
    args = ap.parse_args()
    names = args.template or list(CHECKS)

    worst = 0
    for name in names:
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
        print(f"{mark} {name:<26} {made:>5,} items, {bad} defects   ({what})")
        worst |= 1 if bad else 0
    return worst


if __name__ == "__main__":
    sys.exit(main())
