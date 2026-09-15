"""Read the four printed options back, and check only one of them is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct, because nothing in the engine reads the wrong
options as mathematics -- they are strings that `assemble` sorted and
`assemble_text` shuffled. An item with two right answers therefore passes every
gate the engine has, and so does an item whose key answers a different question
from the one the stem prints.

This script closes that hole for the sixteen Circles templates. It parses the
printed stem, the printed options and -- where a figure carries part of the
question -- the SVG's own pixel geometry back into circle geometry, decides
each option's status from that geometry alone, and asserts that exactly one
option has the property the stem asks for and that it is the keyed one. It
imports no template, no renderer and no solver: `generate` is used only to
obtain the finished item, exactly as a student would receive it.

    PYTHONPATH=. python3 satbank/topics/circles/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 2000 --template circles.arc
    PYTHONPATH=. python3 .../option_check.py --selftest

Exits non-zero on the first kind of defect it finds, and prints the item.
"""

from __future__ import annotations

import argparse
import math
import random
import re
import sys
from dataclasses import dataclass, replace
from fractions import Fraction as Q

from satbank.item import ItemError
from satbank.registry import generate
from satbank.topic import load_topics

MINUS = "\N{MINUS SIGN}"
PI = "\N{GREEK SMALL LETTER PI}"
ROOT = "\N{SQUARE ROOT}"
DEG = "\N{DEGREE SIGN}"
SUP2 = "\N{SUPERSCRIPT TWO}"


class Unreadable(Exception):
    """The printed text or the drawn figure is not something this reads."""


# ===================================================== printed text -> numbers

def _squarefree(n: int) -> tuple[int, int]:
    """n = m**2 * k with k squarefree, so sqrt(40) and 2*sqrt(10) are one value."""
    m, k, d = 1, n, 2
    while d * d <= k:
        while k % (d * d) == 0:
            k //= d * d
            m *= d
        d += 1
    return m, k


@dataclass(frozen=True)
class Val:
    """coef * pi**pi_exp * sqrt(rad), the shape every Circles answer has.

    Written here rather than imported so that a printed value and the `Exact`
    that produced it are compared through two separate pieces of code.
    """
    coef: Q = Q(0)
    pi_exp: Q = Q(0)
    rad: int = 1

    @staticmethod
    def of(coef=1, pi_exp=0, rad=1) -> "Val":
        coef, pi_exp, rad = Q(coef), Q(pi_exp), Q(rad)
        if rad < 0:
            raise Unreadable("a negative radicand")
        if coef == 0 or rad == 0:
            return Val(Q(0), Q(0), 1)
        m, k = _squarefree(rad.numerator * rad.denominator)
        return Val(coef * Q(m, rad.denominator), pi_exp, k)

    def __mul__(self, o) -> "Val":
        o = o if isinstance(o, Val) else Val.of(o)
        return Val.of(self.coef * o.coef, self.pi_exp + o.pi_exp, Q(self.rad * o.rad))

    __rmul__ = __mul__

    def __truediv__(self, o) -> "Val":
        o = o if isinstance(o, Val) else Val.of(o)
        if o.coef == 0:
            raise Unreadable("division by zero")
        return Val.of(self.coef / o.coef, self.pi_exp - o.pi_exp, Q(self.rad, o.rad))

    def __add__(self, o) -> "Val":
        o = o if isinstance(o, Val) else Val.of(o)
        if self.coef == 0:
            return o
        if o.coef == 0:
            return self
        if (self.pi_exp, self.rad) != (o.pi_exp, o.rad):
            raise Unreadable(f"cannot add {self} and {o}")
        return Val.of(self.coef + o.coef, self.pi_exp, Q(self.rad))

    __radd__ = __add__

    def __neg__(self) -> "Val":
        return Val(-self.coef, self.pi_exp, self.rad)

    def __sub__(self, o) -> "Val":
        return self + (-(o if isinstance(o, Val) else Val.of(o)))

    def __rsub__(self, o) -> "Val":
        return (o if isinstance(o, Val) else Val.of(o)) + (-self)

    def __pow__(self, n: int) -> "Val":
        return Val.of(self.coef ** n, self.pi_exp * n, Q(self.rad) ** n)

    @property
    def rational(self) -> bool:
        return self.pi_exp == 0 and self.rad == 1

    def __float__(self) -> float:
        return float(self.coef) * math.pi ** float(self.pi_exp) * math.sqrt(self.rad)

    def __str__(self) -> str:
        head = "" if (abs(self.coef) == 1 and (self.pi_exp or self.rad != 1)) else \
            str(abs(self.coef.numerator))
        body = head + (PI if self.pi_exp == 1 else
                       f"{PI}^{self.pi_exp}" if self.pi_exp else "")
        body += f"{ROOT}{self.rad}" if self.rad != 1 else ""
        sign = "-" if self.coef < 0 else ""
        d = self.coef.denominator
        return f"{sign}{body}" + (f"/{d}" if d != 1 else "")


V0 = Val.of(0)
VPI = Val.of(1, 1)


def frac(text: str) -> Q:
    """A printed rational: 8, -11, 2,300, 9/7, 3.5, 0.25."""
    t = str(text).replace(MINUS, "-").replace(",", "").strip()
    if not re.fullmatch(r"-?\d+(?:\.\d+)?(?:/\d+)?", t):
        raise Unreadable(f"{text!r} is not a number")
    if "/" in t:
        a, b = t.split("/", 1)
        return Q(a) / Q(b)
    return Q(t)


# an option's numerator: an optional integer, an optional pi, an optional root
FACTOR = re.compile(
    rf"^(?P<sign>-?)(?P<n>\d[\d,]*(?:\.\d+)?)?"
    rf"(?:(?P<pi>{PI})(?:\^\{{?(?P<exp>-?\d+(?:/\d+)?)\}}?)?)?"
    rf"(?:{ROOT}(?P<rad>\d[\d,]*|{PI}))?$")


def value(text: str) -> Val:
    """One printed option as an exact value.

    Handles every surface the topic prints: 36, 2,592pi/5, pi/3, 13/2 pi (the
    stacked-fraction spelling), -13pi/2, sqrt(40) written as a radical sign,
    sqrt2/2 and 0. Nothing here goes back through `Exact`, so a rendering bug
    that drops a minus sign or a denominator shows up as a value that no
    option carries.
    """
    t = (str(text).strip().replace(MINUS, "-")
         .replace("pi", PI).replace("sqrt", ROOT))
    # "13/2 pi": the whole coefficient printed in front of the symbol
    m = re.fullmatch(rf"(-?[\d,]+(?:/\d+)?)\s+{PI}", t)
    if m:
        return Val.of(frac(m.group(1)), 1)
    t = t.replace(" ", "")
    if t in ("0", "-0"):
        return V0
    den = Q(1)
    if "/" in t:
        head, tail = t.rsplit("/", 1)
        if not re.fullmatch(r"\d+", tail):
            raise Unreadable(f"{text!r} has a denominator this cannot read")
        den, t = Q(int(tail)), head
    m = FACTOR.fullmatch(t)
    if m is None or not (m.group("n") or m.group("pi") or m.group("rad")):
        raise Unreadable(f"{text!r} is not a value this reads")
    coef = frac(m.group("n")) if m.group("n") else Q(1)
    if m.group("sign"):
        coef = -coef
    pi_exp = Q(0)
    if m.group("pi"):
        pi_exp = Q(m.group("exp")) if m.group("exp") else Q(1)
    rad = 1
    if m.group("rad"):
        if m.group("rad") == PI:
            pi_exp += Q(1, 2)
        else:
            rad = int(m.group("rad").replace(",", ""))
    return Val.of(coef / den, pi_exp, rad)


def point(text: str) -> tuple[Q, Q]:
    """`(3, -15)` or `(3/2, -1/2)` as an exact ordered pair."""
    m = re.fullmatch(r"\(([^,()]+),([^,()]+)\)", str(text).strip())
    if m is None:
        raise Unreadable(f"{text!r} is not a point")
    return frac(m.group(1)), frac(m.group(2))


# =================================================== printed text -> a circle

RHS_PAT = (rf"(?:-?\d(?:[\d,]*\d)?(?:/\d+)?(?:[A-Za-z]{SUP2}?)?"
           rf"|-?[A-Za-z]{SUP2}?)")
EQ_RE = re.compile(rf"(?:\(x\s*[+-][^)]*\)|\d*x){SUP2}[^\n?]*?=\s*{RHS_PAT}")
STD_RE = re.compile(
    rf"^\(?x\)?(?:\s*([+-])\s*([^)]+)\))?{SUP2}\s*\+\s*"
    rf"\(?y\)?(?:\s*([+-])\s*([^)]+)\))?{SUP2}\s*=\s*(.+)$")
TERM_RE = re.compile(rf"\s*([+-])?\s*(\d[\d,]*(?:/\d+)?)?\s*([A-Za-z]*)({SUP2})?")


def find_equation(stem: str) -> str:
    """The circle equation the item prints, wherever it prints it.

    A stem may carry two -- the circle it gives and the shape of the answer it
    wants -- and the first is always the one with numbers in it.
    """
    m = EQ_RE.search(stem)
    if m is None:
        raise Unreadable(f"no circle equation in {stem!r}")
    return m.group(0).strip()


def standard(eq: str) -> tuple[Q, Q, str]:
    """`(x - 3)² + (y + 15)² = 1` as (3, -15, "1"), the right side left as text.

    `x²` for a zero coordinate is the same thing written shorter, and reads
    alike, which is how a distractor that moves a circle nowhere is caught.
    """
    t = eq.replace(MINUS, "-").strip()
    m = STD_RE.fullmatch(t)
    if m is None:
        raise Unreadable(f"{eq!r} is not a circle in standard form")
    sx, hx, sy, ky, rhs = m.groups()
    h = -frac(hx) if sx == "-" else frac(hx) if hx else Q(0)
    k = -frac(ky) if sy == "-" else frac(ky) if ky else Q(0)
    # (x - 3)^2 has centre +3: the printed sign is the opposite of the centre
    return -h, -k, rhs.strip()


def terms(side: str) -> tuple[dict, str]:
    """One side of a general-form equation as {monomial: coefficient}.

    A symbol riding on the coefficients -- `112px`, `-448p²` -- is folded to 1
    and its name returned, which is exactly the substitution that makes the
    radius a plain multiple of it.
    """
    t = side.replace(MINUS, "-").replace(" ", "")
    out, sym, i = {}, "", 0
    while i < len(t):
        m = TERM_RE.match(t, i)
        if m is None or m.end() == i:
            raise Unreadable(f"{side!r} at {t[i:]!r}")
        sign, num, body, sq = m.groups()
        v = frac(num) if num else Q(1)
        if sign == "-":
            v = -v
        if body in ("x", "y"):
            name = body + ("2" if sq else "")
        elif len(body) == 2 and body[1] in "xy":
            name, got = body[1] + ("2" if sq else ""), body[0]
            if sym and sym != got:
                raise Unreadable(f"two symbols, {sym!r} and {got!r}")
            sym = got
            if sq:
                raise Unreadable("a squared variable carrying a symbol")
        elif len(body) == 1:
            name, got = "1", body
            if sym and sym != got:
                raise Unreadable(f"two symbols, {sym!r} and {got!r}")
            sym = got
            if not sq:
                raise Unreadable(f"a bare symbol {got!r} in a circle equation")
        elif not body:
            name = "1"
        else:
            raise Unreadable(f"{body!r} is not a term this reads")
        out[name] = out.get(name, Q(0)) + v
        i = m.end()
    return out, sym


def general(eq: str) -> tuple[Q, Q, Q, str]:
    """`5x² - 30x + 5y² + 150y = -1,165` as the centre and squared radius.

    a(x² + y²) + dx + ey = c  ->  centre (-d/2a, -e/2a), r² = c/a + h² + k².
    """
    if eq.count("=") != 1:
        raise Unreadable(eq)
    lhs, rhs = eq.split("=")
    left, s1 = terms(lhs)
    right, s2 = terms(rhs)
    sym = s1 or s2
    if s1 and s2 and s1 != s2:
        raise Unreadable(f"two symbols, {s1!r} and {s2!r}")
    a, b = left.get("x2", Q(0)), left.get("y2", Q(0))
    if a == 0 or a != b:
        raise Unreadable(f"{eq!r} has x² and y² coefficients {a} and {b}")
    d = left.get("x", Q(0)) - right.get("x", Q(0))
    e = left.get("y", Q(0)) - right.get("y", Q(0))
    c = right.get("1", Q(0)) - left.get("1", Q(0))
    h, k = -d / (2 * a), -e / (2 * a)
    return h, k, c / a + h * h + k * k, sym


def circle(eq: str) -> tuple[Q, Q, Q, str]:
    """Centre and squared radius of any printed circle, in units of its symbol."""
    try:
        h, k, rhs = standard(eq)
    except Unreadable:
        return general(eq)
    m = re.fullmatch(rf"(-?[\d,]+(?:/\d+)?)?([A-Za-z])?{SUP2}?", rhs.replace(MINUS, "-"))
    if m is None:
        raise Unreadable(f"{rhs!r} is not a right-hand side this reads")
    n, sym = m.groups()
    if n is None:
        raise Unreadable(f"{rhs!r} carries no number")
    return h, k, frac(n), sym or ""


def circle_of(stem: str) -> tuple[Q, Q, Q, str]:
    return circle(find_equation(stem))


# ================================================ a drawn figure -> geometry

NUMBER = r"([-\d.]+)"
BIG_CIRCLE = re.compile(rf'<circle class="ax" cx="{NUMBER}" cy="{NUMBER}" r="{NUMBER}"')
DOT = re.compile(rf'<circle class="pt" cx="{NUMBER}" cy="{NUMBER}" r="3\.4"/>'
                 rf'<text class="it"[^>]*>([^<]*)</text>')
SEG = re.compile(rf'<line class="sg" x1="{NUMBER}" y1="{NUMBER}" '
                 rf'x2="{NUMBER}" y2="{NUMBER}"/>')
ARCMARK = re.compile(rf'<path class="sg" d="M{NUMBER},{NUMBER} A(\d+),\d+ 0 ([01]) 0 '
                     rf'{NUMBER},{NUMBER}"/>')
SQUAREMARK = re.compile(rf'<path class="sg" d="M{NUMBER},{NUMBER} L{NUMBER},{NUMBER} '
                        rf'L{NUMBER},{NUMBER}"/>')
ANGLE_LABEL = re.compile(rf'<text class="it"[^>]*>([^<]*{DEG})</text>')


@dataclass
class Dial:
    """What a reader with a protractor gets out of a `circle_with_points` SVG.

    Every position is recovered from the pixels -- the drawn dots, the drawn
    radii, the drawn angle arc -- and nothing is taken from the item's
    parameters, so a figure that disagrees with its stem is visible here and
    nowhere else in the engine.
    """
    cx: float
    cy: float
    r: float
    points: dict            # label -> degrees, measured the way the plane does
    radii: list             # degrees of each segment drawn out from the centre
    chords: list            # (degrees, degrees) of each segment between two points
    marked: tuple | None    # (from, to, span) of the marked central angle
    label: str | None       # the text written inside the marked angle

    def at(self, name: str) -> float:
        """The drawn position of the point whose label starts with `name`."""
        hit = [d for lab, d in self.points.items()
               if lab == name or lab.split(" ")[0] == name]
        if len(hit) != 1:
            raise Unreadable(f"{len(hit)} points drawn for {name!r}")
        return hit[0]

    def span(self, a: str, b: str) -> float:
        """The turn from a to b, anticlockwise, in degrees."""
        return (self.at(b) - self.at(a)) % 360.0

    def apart(self, a: str, b: str) -> float:
        """The size of the angle aOb, never more than a straight angle."""
        s = self.span(a, b)
        return min(s, 360.0 - s)


def dial(svg: str) -> Dial:
    if not svg:
        raise Unreadable("this item carries no figure")
    m = BIG_CIRCLE.search(svg)
    if m is None:
        raise Unreadable("no circle is drawn")
    cx, cy, r = (float(v) for v in m.groups())

    def ang(x, y) -> float:
        d = math.hypot(x - cx, cy - y)
        if d < 1e-9:
            raise Unreadable("a point drawn on top of the centre")
        return math.degrees(math.atan2(cy - y, x - cx)) % 360.0

    points = {}
    for x, y, lab in DOT.findall(svg):
        x, y = float(x), float(y)
        if abs(math.hypot(x - cx, cy - y) - r) > 0.5:
            raise Unreadable(f"the point {lab!r} is not drawn on the circle")
        points[lab] = ang(x, y)
    radii, chords = [], []
    for x1, y1, x2, y2 in SEG.findall(svg):
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
        ends = [(x1, y1), (x2, y2)]
        out = [p for p in ends if math.hypot(p[0] - cx, cy - p[1]) > 1.0]
        if len(out) == 1:
            radii.append(ang(*out[0]))
        elif len(out) == 2:
            chords.append((ang(*out[0]), ang(*out[1])))
    marked = None
    a = ARCMARK.search(svg)
    if a:
        x1, y1, _rr, big, x2, y2 = a.groups()
        a1, a2 = ang(float(x1), float(y1)), ang(float(x2), float(y2))
        sp = (a2 - a1) % 360.0
        if (sp > 180.0) != (big == "1"):
            raise Unreadable(f"a {sp:.1f} degree angle drawn with large-arc {big}")
        marked = (a1, a2, sp)
    else:
        s = SQUAREMARK.search(svg)
        if s:
            x1, y1, _x, _y, x2, y2 = (float(v) for v in s.groups())
            a1, a2 = ang(x1, y1), ang(x2, y2)
            sp = (a2 - a1) % 360.0
            if abs(sp - 90.0) > 0.5:
                raise Unreadable(f"a right-angle square marking {sp:.1f} degrees")
            marked = (a1, a2, sp)
    lab = ANGLE_LABEL.search(svg)
    return Dial(cx, cy, r, points, radii, chords, marked,
                lab.group(1) if lab else None)


GRID = re.compile(rf'<line class="gr" x1="{NUMBER}" y1="{NUMBER}" '
                  rf'x2="{NUMBER}" y2="{NUMBER}"/>')
AXIS = re.compile(rf'<line class="ax" x1="{NUMBER}" y1="{NUMBER}" '
                  rf'x2="{NUMBER}" y2="{NUMBER}"/>')
PLOTTED = re.compile(rf'<circle class="ax" cx="{NUMBER}" cy="{NUMBER}" r="{NUMBER}" '
                     rf'stroke-width="2"/>')


def grid_circle(svg: str) -> tuple[float, float, float]:
    """The circle drawn on an xy-plane, in data units, straight off the pixels.

    The axes locate the origin and the gridline spacing gives the pixels per
    unit, so this is what a reader with a ruler would measure -- no parameter
    of the item is consulted.
    """
    if not svg:
        raise Unreadable("this item carries no figure")
    ax = [tuple(float(v) for v in g) for g in AXIS.findall(svg)]
    horiz = [a for a in ax if abs(a[1] - a[3]) < 1e-9]
    vert = [a for a in ax if abs(a[0] - a[2]) < 1e-9]
    if len(horiz) != 1 or len(vert) != 1:
        raise Unreadable("the axes are not one horizontal and one vertical")
    y0, x0 = horiz[0][1], vert[0][0]
    xs = sorted({float(g[0]) for g in GRID.findall(svg) if g[0] == g[2]})
    gaps = {round(b - a, 6) for a, b in zip(xs, xs[1:])}
    if len(gaps) != 1:
        raise Unreadable("the gridlines are not evenly spaced")
    px = gaps.pop()
    m = PLOTTED.search(svg)
    if m is None:
        raise Unreadable("no circle is plotted on the grid")
    cx, cy, r = (float(v) for v in m.groups())
    return (cx - x0) / px, (y0 - cy) / px, r / px


# ================================================== reading the printed stem

TOKEN = rf"[-\d,./{PI}{ROOT}]+"


def amount(stem: str, before: str) -> Val:
    """The value printed after a phrase: `a radius of 18 feet` -> 18."""
    m = re.search(before + rf"\s*({TOKEN})", stem)
    if m is None:
        raise Unreadable(f"no amount after {before!r}")
    return value(m.group(1).rstrip(".,"))


def degree(stem: str) -> int:
    """The one angle the stem states, in degrees."""
    found = re.findall(rf"(\d+){DEG}", stem) or re.findall(r"(\d+) degrees", stem)
    if len(set(found)) != 1:
        raise Unreadable(f"{len(set(found))} different angles printed")
    return int(found[0])


def near(a: float, b: float, tol: float = 0.5) -> bool:
    """Two bearings, compared the way a protractor would."""
    d = (a - b) % 360.0
    return min(d, 360.0 - d) <= tol


def question(stem: str) -> str:
    """The sentence that actually asks something."""
    i = max(stem.lower().rfind("what is"), stem.lower().rfind("which "))
    return stem[i:] if i >= 0 else stem


def options(item) -> list[str]:
    """What the student is offered: four strings, or the one they must enter."""
    return item.choices if item.fmt == "mcq" else [item.answer]


def settle(item, hits: list[bool], what: str) -> str:
    """Exactly one option is right, and it is the keyed one. Both halves."""
    n = sum(1 for h in hits if h)
    if item.fmt == "spr":
        if n != 1:
            raise AssertionError(f"the entered answer {item.answer!r} is not {what}")
        return what
    if n != 1:
        raise AssertionError(f"{n} of the four options are {what}: {item.choices}")
    i = "ABCD".index(item.answer)
    if not hits[i]:
        raise AssertionError(f"the keyed option {item.choices[i]!r} is not {what}; "
                             f"{item.choices[hits.index(True)]!r} is")
    return what


def same_value(target: Val):
    def test(opt: str) -> bool:
        try:
            return value(opt) == target
        except Unreadable:
            return False
    return test


def value_hits(item, target: Val) -> list[bool]:
    return [same_value(target)(o) for o in options(item)]


def point_hits(item, target: tuple) -> list[bool]:
    out = []
    for o in options(item):
        try:
            out.append(point(o) == target)
        except Unreadable:
            out.append(False)
    return out


# ============================================================ the arc family

def arc_wanted(tail: str, theta: float) -> float:
    """How much of the turn the named arc covers.

    `minor arc AB` is the shorter of the two arcs whatever the central angle
    is, and `major arc AB` the longer; an arc named by its endpoints alone is
    the one the stated central angle cuts off.
    """
    if re.search(r"\bminor arc\b", tail):
        return min(theta, 360.0 - theta)
    if re.search(r"\bmajor arc\b", tail):
        return max(theta, 360.0 - theta)
    return theta


def check_arc(item) -> str:
    """The proportion, against the size the stem prints and the angle it marks."""
    tail = question(item.stem)
    if "circumference" in tail:
        theta = degree(item.stem)
        length = amount(item.stem, r"(?:a length of|the length of arc \w+ is)")
        return settle(item, value_hits(item, length * Val.of(360, 0) / Val.of(theta)),
                      f"the circumference of a circle whose {theta}-degree arc is "
                      f"{length}")
    m = re.search(rf"a (circumference|radius|diameter) of\s*({TOKEN})", item.stem)
    if m is None:
        raise Unreadable(f"no size printed in {item.stem!r}")
    size = value(m.group(2).rstrip(".,"))
    whole = {"circumference": size, "radius": Val.of(2) * VPI * size,
             "diameter": VPI * size}[m.group(1)]
    if item.figure:
        a, b = re.search(r"arc (\w)(\w)", tail).groups()
        d = dial(item.figure)
        if d.marked is None:
            raise Unreadable("the figure marks no central angle")
        a1, a2, span = d.marked
        if not (near(a1, d.at(a)) and near(a2, d.at(b))):
            raise AssertionError(f"the figure marks the angle from {a1:.1f} to {a2:.1f} "
                                 f"degrees, but {a} and {b} are drawn at "
                                 f"{d.at(a):.1f} and {d.at(b):.1f}")
        if d.label and not near(float(d.label.rstrip(DEG)), span):
            raise AssertionError(f"the figure is labelled {d.label} but draws "
                                 f"{span:.1f} degrees")
        theta = span
    else:
        theta = float(degree(item.stem))
    want = arc_wanted(tail, theta)
    share = Q(round(want * 2), 720)
    return settle(item, value_hits(item, whole * Val.of(share)),
                  f"the length of the {want:g}-degree arc of a circle measuring {whole}")


def check_arc_pair(item) -> str:
    """Two arcs that make one circle, against the figure that splits it."""
    tail = question(item.stem)
    if "circumference" in tail:
        small = amount(item.stem, r"[Mm]inor arc \w+ has a length of")
        big = amount(item.stem, r"[Mm]ajor arc \w+ has a length of")
        if item.figure:
            names = re.search(r"[Mm]inor arc (\w)(\w)", item.stem).groups()
            d = dial(item.figure)
            drawn = d.span(names[1], names[0])
            share = 360.0 * float(small) / float(small + big)
            if not near(drawn, share, 1.0):
                raise AssertionError(f"the figure splits the circle {drawn:.1f}/"
                                     f"{360 - drawn:.1f}, the stem {share:.1f}/"
                                     f"{360 - share:.1f}")
        return settle(item, value_hits(item, small + big),
                      f"the whole circle, {small} + {big}")
    given = amount(item.stem, r"(?:the length of arc \w+ is|a length of)")
    x = int(re.search(r"x = (\d+)", item.stem).group(1))
    got = re.search(r"of arc (\w)(\w)(\w)\s*\?", item.stem).groups()
    named = re.search(r"(?:length of arc|arc) (\w)(\w)(\w)", item.stem).groups()
    if item.figure:
        d = dial(item.figure)
        if d.marked is None:
            raise Unreadable("the figure marks no central angle")
        a1, a2, span = d.marked
        if not near(span, x):
            raise AssertionError(f"the stem says x = {x} but the figure draws "
                                 f"{span:.1f} degrees")
        if not (near(a1, d.at(named[0])) and near(a2, d.at(named[2]))):
            raise AssertionError("the marked angle is not the one the given arc spans")
        inside = (d.at(named[1]) - a1) % 360.0
        if inside > span:
            raise AssertionError(f"{named[1]} is drawn outside the arc it names")
        outside = (d.at(got[1]) - a1) % 360.0
        if outside < span:
            raise AssertionError(f"{got[1]} is drawn inside the arc that was given")
    whole = given * Val.of(360) / Val.of(x)
    return settle(item, value_hits(item, whole - given),
                  f"the rest of a circle measuring {whole}")


def check_arc_fraction(item) -> str:
    r = amount(item.stem, r"radius")
    length = amount(item.stem, r"(?:has length|length)")
    share = length / (Val.of(2) * VPI * r)
    if not share.rational:
        raise AssertionError(f"the printed arc is {share} of a circle, not a fraction")
    return settle(item, value_hits(item, share),
                  f"the share {length} is of a circle of radius {r}")


def check_arc_angle(item) -> str:
    """Arc measure and central angle, with `minor` and `major` taken at their word."""
    stem = item.stem
    tail = question(stem)
    given = degree(stem)
    said = re.search(rf"(minor arc|major arc|arc|angle)\s+\w+\s+(?:on this circle\s+)?"
                     rf"(?:is|measures)\s+{given}{DEG}", stem)
    if said is None:
        raise Unreadable(f"cannot tell what {given} degrees measures in {stem!r}")
    kind = said.group(1)
    if kind == "minor arc" and given > 180:
        raise AssertionError(f"a minor arc cannot measure {given} degrees")
    if kind == "major arc" and given < 180:
        raise AssertionError(f"a major arc cannot measure {given} degrees")
    # an arc and the central angle that cuts it have the same measure, reflex
    # angles included, so whichever of the two the stem states, the turn is it
    turn = float(given)
    want = turn if "angle" in tail else arc_wanted(tail, turn)
    return settle(item, value_hits(item, Val.of(round(want))),
                  f"{want:g} degrees, for a central angle of {turn:g}")


def check_chord_angle(item) -> str:
    """Two radii and a chord: the base angle has to become a central angle."""
    stem = item.stem
    base = int(re.search(rf"angle O(\w)(\w) is (\d+){DEG}", stem).group(3))
    a, b = re.search(r"angle O(\w)(\w) is", stem).groups()
    central = 180 - 2 * base
    m = re.search(rf"the radius of the circle is\s*({TOKEN})", stem)
    if m:
        r = value(m.group(1).rstrip(".,"))
        third = None
    else:
        m = re.search(rf"the length of O(\w) is\s*({TOKEN})", stem)
        if m is None:
            raise Unreadable(f"no radius printed in {stem!r}")
        third, r = m.group(1), value(m.group(2).rstrip(".,"))
    d = dial(item.figure)
    drawn = d.apart(a, b)
    if not near(drawn, central, 0.5):
        raise AssertionError(f"the base angle {base} leaves {central} degrees at the "
                             f"centre, but the figure draws {drawn:.1f}")
    if third is not None and not any(near(x, d.at(third)) for x in d.radii):
        raise AssertionError(f"O{third} is not drawn as a radius, so its length says "
                             f"nothing about the circle")
    if not any(near(u, d.at(a)) and near(v, d.at(b)) or
               near(u, d.at(b)) and near(v, d.at(a)) for u, v in d.chords):
        raise AssertionError(f"the chord {a}{b} is not drawn")
    if "angle" in question(stem):
        return settle(item, value_hits(item, Val.of(central)),
                      f"the central angle 180 - 2({base})")
    arc = Val.of(2) * VPI * r * Val.of(Q(central, 360))
    return settle(item, value_hits(item, arc),
                  f"the {central}-degree arc of a circle of radius {r}")


def check_sector(item) -> str:
    r = amount(item.stem, r"a radius of")
    whole = VPI * r * r
    if "an area of" in item.stem:
        area = amount(item.stem, r"an area of")
        share = area / whole
        if not share.rational:
            raise AssertionError(f"the printed sector is {share} of the circle")
        return settle(item, value_hits(item, Val.of(360) * share),
                      f"the angle of a sector that is {share} of the circle")
    theta = degree(item.stem)
    return settle(item, value_hits(item, whole * Val.of(Q(theta, 360))),
                  f"the area of a {theta}-degree sector of radius {r}")


# ========================================================= the angle family

def check_degree_radian(item) -> str:
    """180 degrees is pi radians, run whichever way the stem runs it."""
    stem = item.stem
    m = re.search(rf"({TOKEN})\s+radians", stem)
    if m:
        c = value(m.group(1).rstrip(".,"))
        if c.pi_exp != 1:
            raise Unreadable(f"{m.group(1)!r} is not a radian measure")
        return settle(item, value_hits(item, Val.of(180) * c / VPI),
                      f"{c} radians in degrees")
    deg = degree(stem) if re.search(rf"\d+{DEG}", stem) else \
        int(re.search(r"(\d+)[- ]degrees?", stem).group(1))
    if re.search(rf"written as a{PI}", stem):
        return settle(item, value_hits(item, Val.of(Q(deg, 180))),
                      f"the multiple of pi that {deg} degrees is")
    return settle(item, value_hits(item, Val.of(Q(deg, 180), 1)),
                  f"{deg} degrees in radians")


def check_unit_circle_angle(item) -> str:
    """Three angles on a straight line, measured off the drawing."""
    stem = item.stem
    m = re.search(rf"angles (\w)O(\w) and (\w)O(\w) are (?:each )?(\d+){DEG}"
                  rf"(?: and (\d+){DEG})?", stem)
    if m is None:
        raise Unreadable(f"cannot read the marked angles in {stem!r}")
    p, q, r, t, a, b = m.groups()
    a, b = int(a), int(b or a)
    u, v = re.search(r"measure of angle (\w)O(\w)", question(stem)).groups()
    d = dial(item.figure)
    if not near(d.apart(p, t), 180.0):
        raise AssertionError(f"{p}, O and {t} are {d.apart(p, t):.1f} degrees apart, "
                             f"so they are not the ends of one diameter")
    if not near(d.apart(p, q), a):
        raise AssertionError(f"the stem marks angle {p}O{q} as {a} degrees, the figure "
                             f"draws {d.apart(p, q):.1f}")
    if not near(d.apart(r, t), b):
        raise AssertionError(f"the stem marks angle {r}O{t} as {b} degrees, the figure "
                             f"draws {d.apart(r, t):.1f}")
    drawn = d.apart(u, v)
    left = int(round(drawn))
    if not near(drawn, left, 0.01):
        raise AssertionError(f"the figure leaves {drawn:.3f} degrees, not a whole number")
    want = (Val.of(Q(left, 180), 1) if "radian" in question(stem) else Val.of(left))
    return settle(item, value_hits(item, want),
                  f"the {left} degrees the figure leaves between {u} and {v}")


COORD = re.compile(r"[Pp]oint (\w)\b((?:(?![Pp]oint)[^.])*?)coordinates \(([^)]*)\)")


def check_coterminal(item) -> str:
    """Every positive measure that reaches the second point, not just one of them."""
    stem = item.stem
    f, g, h = re.search(r"angle (\w)(\w)(\w)", question(stem)).groups()
    seen = {name: body for name, _gap, body in COORD.findall(stem)}
    if f not in seen or h not in seen:
        raise Unreadable(f"{stem!r} does not give both points' coordinates")
    radius = 1.0 if "unit circle" in stem else \
        float(re.search(r"circle of radius (\d+)", stem).group(1))

    def spot(body: str) -> float:
        parts = [s.strip() for s in body.split(",")]
        known = [(i, frac(s)) for i, s in enumerate(parts) if re.fullmatch(r"-?\d+", s)]
        if len(known) == 2:
            x, y = float(known[0][1]), float(known[1][1])
        elif len(known) == 1:
            i, v = known[0]
            rest = radius * radius - float(v) ** 2
            if rest > 1e-9:
                raise AssertionError(f"({body}) is two points on the circle, not one")
            if rest < -1e-9:
                raise AssertionError(f"({body}) is not on the circle at all")
            x, y = (float(v), 0.0) if i == 0 else (0.0, float(v))
        else:
            raise Unreadable(f"({body}) pins nothing down")
        if abs(math.hypot(x, y) - radius) > 1e-9:
            raise AssertionError(f"({body}) is not on the circle of radius {radius:g}")
        return math.degrees(math.atan2(y, x)) % 360.0

    turn = (spot(seen[h]) - spot(seen[f])) % 360.0
    hits = []
    for o in options(item):
        try:
            v = value(o)
        except Unreadable:
            hits.append(False)
            continue
        if v.pi_exp != 1 or v.rad != 1 or v.coef <= 0:
            hits.append(False)
            continue
        landed = (180.0 * float(v.coef)) % 360.0
        hits.append(near(landed, turn, 1e-6))
    return settle(item, hits, f"a positive measure that turns {turn:g} degrees")


def check_exact_trig(item) -> str:
    """The value on the circle, from the angle the stem prints."""
    m = re.search(rf"value of (cos|sin) ({TOKEN})", item.stem)
    if m is None:
        raise Unreadable(f"no trigonometric value asked in {item.stem!r}")
    fn, ang = m.group(1), value(m.group(2).rstrip(" ?,."))
    if ang.pi_exp != 1 or ang.rad != 1:
        raise Unreadable(f"{m.group(2)!r} is not a multiple of pi")
    turns = ang.coef % 2                       # whole turns come off exactly
    deg = math.radians(180.0 * float(turns))
    want = math.cos(deg) if fn == "cos" else math.sin(deg)
    hits = []
    for o in options(item):
        try:
            hits.append(abs(float(value(o)) - want) < 1e-9)
        except Unreadable:
            hits.append(False)
    return settle(item, hits, f"{fn} of {turns} turns, which is {want:.6f}")


# ====================================================== the equation family

def rhs_form(text: str) -> tuple[Val, str, int]:
    """A right-hand side as (number, symbol, the symbol's exponent).

    `289` is 289; `144p²` is 144 of p squared; `144p` is 144 of p, a different
    circle; `2√13` is a number again. Keeping the exponent is the whole point:
    r² = 144p² is a radius of 12p, and r² = 144p is not.
    """
    t = str(text).strip().replace(MINUS, "-")
    m = re.fullmatch(rf"(.*?)([A-Za-z]){SUP2}", t)
    if m:
        return value(m.group(1) or "1"), m.group(2), 2
    m = re.fullmatch(r"(.*?)([A-Za-z])", t)
    if m:
        return value(m.group(1) or "1"), m.group(2), 1
    return value(t), "", 0


def circle_hits(item, h: Q, k: Q, rhs: tuple) -> list[bool]:
    """Which printed equations describe the circle wanted, however spelled."""
    out = []
    for o in options(item):
        try:
            oh, ok, orhs = standard(o)
            out.append((oh, ok) == (h, k) and rhs_form(orhs) == rhs)
        except Unreadable:
            out.append(False)
    return out


def check_equation_read(item) -> str:
    """Centre, radius or radius coefficient, completed out of what is printed."""
    ask = question(item.stem)
    h, k, r2, sym = circle_of(item.stem)
    if r2 <= 0:
        raise AssertionError(f"the printed equation has r² = {r2}, so it is no circle")
    if "center" in ask:
        return settle(item, point_hits(item, (h, k)), f"the centre ({h}, {k})")
    if re.search(r"value of (\w)\b", ask):
        name = re.search(r"value of (\w)\b", ask).group(1)
        m = re.search(r"radius of the circle is (\w)(\w), where (\w) and (\w) are "
                      r"positive constants", item.stem)
        if m is None:
            raise Unreadable(f"cannot read what {name} stands for")
        n_name, s_name = m.group(1), m.group(2)
        if {n_name, s_name} != {m.group(3), m.group(4)} or name != n_name:
            raise AssertionError(f"the stem calls the radius {n_name}{s_name} but names "
                                 f"{m.group(3)} and {m.group(4)} as the constants")
        if s_name != sym:
            raise AssertionError(f"the stem says the constant is {s_name!r}, the printed "
                                 f"equation carries {sym!r}")
        root = Val.of(1, 0, r2)
        if not root.rational:
            raise AssertionError(f"the radius is {root}{sym}, so {name} is not a constant")
        return settle(item, value_hits(item, root),
                      f"the radius coefficient, {root}")
    want = Val.of(1, 0, r2)
    if "diameter" in ask:
        want = Val.of(2) * want
    return settle(item, value_hits(item, want),
                  f"the {'diameter' if 'diameter' in ask else 'radius'}, {want}")


CENTRE = re.compile(r"cent(?:er|re) (?:at |is )?(\([^)]*\))")


def check_equation_write(item) -> str:
    """From a centre and a size to the equation, or to one of its coefficients."""
    stem = item.stem
    m = CENTRE.search(stem)
    if m is None:
        raise Unreadable(f"no centre printed in {stem!r}")
    h, k = point(m.group(1))
    on = re.search(r"the point (\([^)]*\)) lies on the circle", stem)
    # a radius may be a multiple of a constant -- 7k -- so that spelling is
    # tried before the plain number, which would otherwise match just the 7
    rad = re.search(rf"a radius of (\d+[A-Za-z]|{TOKEN})", stem)
    if on:
        px, py = point(on.group(1))
        r2, sym, exp = Val.of((px - h) ** 2 + (py - k) ** 2), "", 0
    elif rad and re.fullmatch(r"\d+[A-Za-z]", rad.group(1).rstrip(".,")):
        text = rad.group(1).rstrip(".,")
        r2, sym, exp = value(text[:-1]) ** 2, text[-1], 2
    elif rad:
        r2, sym, exp = value(rad.group(1).rstrip(".,")) ** 2, "", 0
    else:
        raise Unreadable(f"no size printed in {stem!r}")
    ask = question(stem)
    if "equation" in ask:
        return settle(item, circle_hits(item, h, k, (r2, sym, exp)),
                      f"the circle centred ({h}, {k}) with r² = {r2}"
                      + (f" {sym}^{exp}" if sym else ""))
    name = re.search(r"value of (\w)\b", ask).group(1)
    if sym:
        raise Unreadable("a symbolic radius with a coefficient asked for")
    want = {"a": Val.of(-2 * h), "b": Val.of(-2 * k),
            "c": Val.of(h * h + k * k) - r2}[name]
    return settle(item, value_hits(item, want),
                  f"{name} = {want} in x² + y² + ax + by + c = 0")


PAIR = re.compile(r"\(\s*(-?[\d,/]+|[a-z])\s*,\s*(-?[\d,/]+|[a-z])\s*\)")


def check_point_on(item) -> str:
    """A point the circle passes through, tested against the printed equation."""
    stem = item.stem
    h, k, r2, _sym = circle_of(stem)
    if "diameter" in stem:
        ends = [point(f"({x}, {y})") for x, y in PAIR.findall(stem)
                if not (x.isalpha() or y.isalpha())]
        on = [p for p in ends if (p[0] - h) ** 2 + (p[1] - k) ** 2 == r2]
        if len(on) != 1:
            raise AssertionError(f"{len(on)} of the printed points lie on the circle")
        px, py = on[0]
        return settle(item, point_hits(item, (2 * h - px, 2 * k - py)),
                      f"the far end of the diameter from ({px}, {py})")
    named = [(x, y) for x, y in PAIR.findall(stem) if x.isalpha() != y.isalpha()]
    if len(named) != 1:
        raise Unreadable(f"{len(named)} points with an unknown coordinate")
    x, y = named[0]
    if x.isalpha():
        rest = r2 - (frac(y) - k) ** 2
        base = h
    else:
        rest = r2 - (frac(x) - h) ** 2
        base = k
    if rest < 0:
        raise AssertionError("the printed point is nowhere near the circle")
    if rest != 0:
        raise AssertionError(f"two values fit: the stem does not pin the coordinate down")
    return settle(item, value_hits(item, Val.of(base)),
                  f"the only coordinate that puts the point on the circle, {base}")


def check_interior(item) -> str:
    """Which point is outside -- decided for all four, not just the keyed one."""
    h, k, r2, _sym = circle_of(item.stem)
    hits = []
    for o in options(item):
        try:
            x, y = point(o)
        except Unreadable:
            hits.append(False)
            continue
        hits.append((x - h) ** 2 + (y - k) ** 2 >= r2)
    return settle(item, hits, f"outside the circle of radius² {r2} at ({h}, {k})")


def check_tangent_slope(item) -> str:
    stem = item.stem
    m = CENTRE.search(stem)
    t = re.search(r"tangent (?:to this circle )?at (?:the point )?(\([^)]*\))", stem)
    if m is None or t is None:
        raise Unreadable(f"cannot read the circle and the tangency point in {stem!r}")
    h, k = point(m.group(1))
    px, py = point(t.group(1))
    if (px, py) == (h, k):
        raise AssertionError("the tangency point is the centre")
    if py == k:
        raise AssertionError("the tangent there is vertical, so it has no slope")
    return settle(item, value_hits(item, Val.of(-(px - h) / (py - k))),
                  f"the perpendicular to the radius through ({px}, {py})")


STEPS = {"right": (1, 0), "left": (-1, 0), "up": (0, 1), "down": (0, -1)}
TIMES = {"two": 2, "three": 3, "four": 4, "five": 5}


def check_transform(item) -> str:
    """Circle B out of circle A, against circle A as printed and as drawn."""
    stem = item.stem
    h, k, r2, _sym = circle_of(stem)
    if item.figure:
        gx, gy, gr = grid_circle(item.figure)
        if abs(gx - h) > 0.02 or abs(gy - k) > 0.02 or abs(gr * gr - r2) > 0.05:
            raise AssertionError(f"the figure draws a circle of radius {gr:.3f} at "
                                 f"({gx:.3f}, {gy:.3f}); the equation says radius "
                                 f"{math.sqrt(float(r2)):.3f} at ({h}, {k})")
    ask = question(stem)
    if "translat" in stem:
        m = (re.search(r"translat\w+ (?:circle \w+ )?(?:to the )?(\w+) (\d+) units", stem)
             or re.search(r"translated (\d+) units (?:to the )?(\w+)", stem))
        one, two = m.groups()
        direction, shift = (one, int(two)) if one in STEPS else (two, int(one))
        ux, uy = STEPS[direction]
        if "equation" in ask:
            return settle(item, circle_hits(item, h + ux * shift, k + uy * shift,
                                            (Val.of(r2), "", 0)),
                          f"circle A slid {shift} units {direction}")
        name = re.search(r"value of (\d*)(\w)\b", ask)
        times = int(name.group(1) or 1)
        return settle(item, value_hits(item, Val.of(times * r2)),
                      f"{times} times the constant a translation leaves alone")
    word = re.search(r"radius of circle \w+ is (\w+) times", stem).group(1)
    scale = TIMES[word]
    return settle(item, value_hits(item, Val.of(scale * scale * r2)),
                  f"the squared radius after scaling by {scale}")


CHECKS = {
    "circles.arc": check_arc,
    "circles.arc_pair": check_arc_pair,
    "circles.arc_fraction": check_arc_fraction,
    "circles.arc_angle": check_arc_angle,
    "circles.chord_angle": check_chord_angle,
    "circles.sector": check_sector,
    "circles.degree_radian": check_degree_radian,
    "circles.unit_circle_angle": check_unit_circle_angle,
    "circles.coterminal": check_coterminal,
    "circles.exact_trig": check_exact_trig,
    "circles.equation_read": check_equation_read,
    "circles.equation_write": check_equation_write,
    "circles.point_on": check_point_on,
    "circles.interior": check_interior,
    "circles.tangent_slope": check_tangent_slope,
    "circles.transform": check_transform,
}


# ================================================================= selftest

def _swap(item, i: int, text: str):
    """The same item with one printed option replaced."""
    ch = list(item.choices)
    ch[i] = text
    return replace(item, choices=ch)


def _not_key(item) -> int:
    return next(i for i in range(4) if "ABCD"[i] != item.answer)


def _second_answer_arc():
    """The key printed twice, in the topic's two spellings for a pi multiple.

    `5pi/2` and `5/2 pi` are one number written the way `exact.py` writes it
    and the way a stacked fraction prints it. A check that compared strings
    would call the second one a distractor.
    """
    item = generate("circles.arc", 0, mode="arc", given="radius", theta=50, size=9,
                    unit=None, fmt="mcq", frame="text", style="back")
    v = value(item.choices["ABCD".index(item.answer)])      # 5pi/2
    if v.pi_exp != 1 or v.coef.denominator == 1:
        raise Unreadable(f"the key {v} has only one spelling")
    twin = f"{v.coef.numerator}/{v.coef.denominator} {PI}"
    return _swap(item, _not_key(item), twin)


def _minor_arc_of_a_reflex_angle():
    """The defect this check was written to find, put back by hand.

    The figure marks a reflex central angle; the stem calls the arc it cuts
    the minor one. The key is then the major arc, and the minor arc is sitting
    in the option set as a distractor.
    """
    item = generate("circles.arc", 0, mode="arc", given="circumference", theta=240,
                    size=36, unit=None, fmt="mcq", frame="figure", labels=("A", "B"))
    return replace(item, stem=item.stem.replace("of arc", "of minor arc"))


def _second_answer_equation():
    """The keyed circle a second time, with its zero coordinate written out."""
    item = generate("circles.equation_write", 0, h=0, k=5, r=3, ask="equation")
    key = item.choices["ABCD".index(item.answer)]          # "x² + (y - 5)² = 9"
    return _swap(item, _not_key(item), key.replace("x²", "(x - 0)²", 1))


def _second_answer_interior():
    """A second point outside the circle among the three meant to be inside."""
    item = generate("circles.interior", 0, h=0, k=0, r=5, out=(6, 1), far=(-4, 2),
                    sq=(3, -1))
    return _swap(item, _not_key(item), "(9, 9)")


def _second_answer_trig():
    """The reference value printed with the sign the key carries."""
    item = generate("circles.exact_trig", 0, fn="cos", num=565, den=6)
    key = item.choices["ABCD".index(item.answer)]
    return _swap(item, _not_key(item), key.replace(ROOT, "sqrt"))


def _moved_key():
    item = generate("circles.tangent_slope", 0, h=-4, k=-6, dx=-3, dy=-1, label="k")
    return replace(item, answer="ABCD"[_not_key(item)])


def _dropped_minus():
    """A renderer that loses a sign: no option is the answer any more."""
    item = generate("circles.tangent_slope", 0, h=-4, k=-6, dx=-3, dy=-1, label="k")
    i = "ABCD".index(item.answer)
    return _swap(item, i, item.choices[i].lstrip("-"))


def _spliced_dial():
    """The right question with another draw's picture."""
    item = generate("circles.arc", 0, mode="arc", given="circumference", theta=60,
                    size=36, unit=None, fmt="mcq", frame="figure", labels=("A", "B"))
    other = generate("circles.arc", 0, mode="arc", given="circumference", theta=120,
                     size=36, unit=None, fmt="mcq", frame="figure", labels=("A", "B"))
    return replace(item, figure=other.figure)


def _spliced_grid():
    item = generate("circles.transform", 0, mode="translate", h=0, k=6, r2=7,
                    direction="right", shift=96, ask="rhs", times=4, fmt="mcq")
    other = generate("circles.transform", 0, mode="translate", h=3, k=6, r2=16,
                     direction="right", shift=96, ask="rhs", times=4, fmt="mcq")
    return replace(item, figure=other.figure)


def _spliced_unit_circle():
    item = generate("circles.unit_circle_angle", 0, a=30, b=30, ask="degrees")
    other = generate("circles.unit_circle_angle", 0, a=55, b=30, ask="degrees")
    return replace(item, figure=other.figure)


INJECTIONS = [
    ("a second correct option: the key's value in the other pi spelling",
     _second_answer_arc),
    ("a second correct option: the keyed circle with (x - 0)² for x²",
     _second_answer_equation),
    ("a second correct option: another point outside the circle",
     _second_answer_interior),
    ("a second correct option: the key with an ASCII radical",
     _second_answer_trig),
    ("a reflex marked angle whose arc the stem calls minor",
     _minor_arc_of_a_reflex_angle),
    ("the key moved to another letter", _moved_key),
    ("a renderer that dropped the key's minus sign", _dropped_minus),
    ("a spliced figure: the arc is drawn at the wrong angle", _spliced_dial),
    ("a spliced figure: the plotted circle is not the printed one", _spliced_grid),
    ("a spliced figure: the marked angles are not the stated ones",
     _spliced_unit_circle),
]


def selftest() -> int:
    """Prove the check can fail. One nobody has seen fail is worth nothing."""
    bad = 0
    for why, build in INJECTIONS:
        try:
            item = build()
        except Exception as exc:                                    # noqa: BLE001
            print(f" ERROR  {why}: could not build ({exc})")
            bad += 1
            continue
        try:
            CHECKS[item.template](item)
        except AssertionError as exc:
            print(f"  ok   {why}\n         caught: {exc}")
            continue
        except Unreadable as exc:
            print(f" WEAK   {why}\n         only unreadable: {exc}")
            bad += 1
            continue
        print(f" MISS   {why}\n{item.pretty()}")
        bad += 1
    return 1 if bad else 0


# ================================================= the official items too

def check_sources(verbose: bool) -> tuple[int, int]:
    """Run the same checks over the 32 encoded College Board items.

    Draws are the point -- the defect this found lived in a stem variant no
    source item uses -- but two option shapes go the other way: a radius given
    as a multiple of a constant, and a radius given by a point on the circle,
    are reachable only from the source parameters. Those option sets would
    never be read at all without this pass.
    """
    topic = load_topics()["circles"]
    made = bad = 0
    for src in topic.sources:
        try:
            item = src.build(random.Random(0))
        except Exception as exc:                                    # noqa: BLE001
            print(f"\n{src.id}: template raised {type(exc).__name__}: {exc}")
            bad += 1
            continue
        made += 1
        try:
            CHECKS[item.template](item)
        except (AssertionError, Unreadable) as exc:
            bad += 1
            print(f"\n{src.id} ({item.template}): {exc}")
            if verbose:
                print(item.pretty())
    mark = "  ok  " if not bad else " FAIL "
    print(f"{mark} {'the 32 official items':<26} {made:>5,} items, {bad} defects")
    return made, bad


# =================================================================== driver

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--draws", type=int, default=600,
                    help="seeds to try per template (default 600)")
    ap.add_argument("--template", action="append",
                    help="check only this template; repeatable")
    ap.add_argument("--selftest", action="store_true",
                    help="inject known-bad option sets and confirm each is caught")
    ap.add_argument("--all", action="store_true",
                    help="report every defect, not only the first of each kind")
    ap.add_argument("--sources", action="store_true",
                    help="check only the 32 official items")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.sources:
        return 1 if check_sources(True)[1] else 0

    names = args.template or list(CHECKS)
    worst = 0
    for name in names:
        checker = CHECKS[name]
        made = mcq = bad = 0
        what = ""
        for seed in range(args.draws):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            made += 1
            mcq += item.fmt == "mcq"
            try:
                what = checker(item)
            except (AssertionError, Unreadable) as exc:
                bad += 1
                if bad == 1 or args.all:
                    print(f"\n{name} seed {seed}: {exc}")
                    print(item.pretty())
        mark = "  ok  " if not bad else " FAIL "
        print(f"{mark} {name:<26} {made:>5,} items ({mcq:,} with options), "
              f"{bad} defects   ({what})")
        worst |= 1 if bad else 0
    if not args.template:
        worst |= 1 if check_sources(args.all)[1] else 0
    return worst


if __name__ == "__main__":
    sys.exit(main())
