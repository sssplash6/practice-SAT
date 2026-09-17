"""Read the printed options and the drawn figure back, and check only one is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct, because nothing in the engine reads the wrong
options as mathematics -- they are strings that `assemble` sorted. An item with
two right answers therefore passes every gate the engine has. Nor does anything
in the engine look at the picture: a figure that has drifted from its own stem
is a wrong item that all seven checks call green.

This script closes both holes for the nineteen Right Triangles templates. It

* parses each printed option back into an exact value through its own reader,
  which shares nothing with `Exact`, `Surd` or `figures.py`;
* parses the printed stem for the numbers the item states;
* reads the **SVG's pixel geometry** -- the three drawn vertices, the drawn
  side lengths, the labelled angles and the vertex the right-angle square sits
  on -- and asserts the picture agrees with the numbers printed on it and with
  the answer the template computed;
* asserts that exactly one option has the property the stem asks for, and that
  it is the keyed one.

    PYTHONPATH=. python3 satbank/topics/right_triangles_and_trigonometry/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 2000 --template rtt.trig_ratio
    PYTHONPATH=. python3 .../option_check.py --selftest
    PYTHONPATH=. python3 .../option_check.py --sources

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
ROOT = "\N{SQUARE ROOT}"
DEG = "\N{DEGREE SIGN}"
SUP2 = "\N{SUPERSCRIPT TWO}"
SLUG = "right_triangles_and_trigonometry"


class Unreadable(Exception):
    """The printed text or the drawn figure is not something this reads."""


# ===================================================== printed text -> numbers

def _squarefree(n: int) -> tuple[int, int]:
    m, k, d = 1, int(n), 2
    while d * d <= k:
        while k % (d * d) == 0:
            k //= d * d
            m *= d
        d += 1
    return m, k


@dataclass(frozen=True)
class Val:
    """a + b√d, exactly: the shape every printed answer in this topic has.

    Written here rather than imported so that a printed value and the `Exact`
    or `Surd` that produced it are compared through two separate pieces of
    code. √8 and 2√2 are one number; 3/√3 and √3 are one number.
    """
    a: Q = Q(0)
    b: Q = Q(0)
    d: int = 1

    @staticmethod
    def of(a=0, b=0, d=1) -> "Val":
        a, b, d = Q(a), Q(b), int(d)
        if d < 1:
            raise Unreadable("a radicand is a positive integer")
        m, k = _squarefree(d)
        b = b * m
        return Val(a + b, Q(0), 1) if k == 1 else (Val(a, Q(0), 1) if b == 0
                                                   else Val(a, b, k))

    def __add__(self, o) -> "Val":
        o = o if isinstance(o, Val) else Val.of(o)
        if self.b and o.b and self.d != o.d:
            raise Unreadable(f"{self} and {o} are unlike radicals")
        return Val.of(self.a + o.a, self.b + o.b, self.d if self.b else o.d)

    def __neg__(self) -> "Val":
        return Val(-self.a, -self.b, self.d)

    def __sub__(self, o) -> "Val":
        return self + (-(o if isinstance(o, Val) else Val.of(o)))

    def __mul__(self, o) -> "Val":
        o = o if isinstance(o, Val) else Val.of(o)
        if not self.b or not o.b:
            return Val.of(self.a * o.a, self.a * o.b + self.b * o.a,
                          self.d if self.b else o.d)
        if self.d != o.d:
            raise Unreadable("unlike radicals multiplied")
        return Val.of(self.a * o.a + self.b * o.b * self.d,
                      self.a * o.b + self.b * o.a, self.d)

    def __truediv__(self, o) -> "Val":
        o = o if isinstance(o, Val) else Val.of(o)
        if o.a == 0 and o.b == 0:
            raise Unreadable("division by zero")
        if o.b == 0:
            return Val.of(self.a / o.a, self.b / o.a, self.d)
        if o.a == 0:                      # x / (b√d) = x·√d / (b·d)
            return self * Val.of(0, Q(1, o.b * o.d), o.d)
        den = o.a * o.a - o.b * o.b * o.d
        if den == 0:
            raise Unreadable("division by zero")
        return self * Val(o.a, -o.b, o.d) / Val.of(den)

    def __float__(self) -> float:
        return float(self.a) + float(self.b) * math.sqrt(self.d)

    def __str__(self) -> str:
        if self.b == 0:
            return str(self.a)
        return f"{self.a} + {self.b}{ROOT}{self.d}"


V0 = Val.of(0)

_NUM = r"\d[\d,]*(?:\.\d+)?"
SIMPLE = re.compile(rf"^(?P<n>{_NUM})?(?:{ROOT}(?P<rad>\d[\d,]*))?$")


def _plain(t: str) -> Q:
    t = t.replace(",", "")
    if not re.fullmatch(r"\d+(?:\.\d+)?", t):
        raise Unreadable(f"{t!r} is not a plain number")
    return Q(t)


def _simple(t: str) -> Val:
    """One factor: 58, 1,184, 3.5, √17, 8√6, 4√74."""
    t = t.strip().replace(" ", "")
    m = SIMPLE.fullmatch(t)
    if m is None or not (m.group("n") or m.group("rad")):
        raise Unreadable(f"{t!r} is not a value this reads")
    coef = _plain(m.group("n")) if m.group("n") else Q(1)
    if m.group("rad"):
        return Val.of(0, coef, int(m.group("rad").replace(",", "")))
    return Val.of(coef)


def _term(t: str) -> Val:
    """One signed term, possibly a quotient: −√3/3, 3/√3, 125√3/2, 63/73."""
    t = t.strip().replace(MINUS, "-")
    sign = 1
    while t.startswith("-"):
        sign, t = -sign, t[1:].strip()
    if "/" in t:
        num, den = t.rsplit("/", 1)
        out = _simple(num) / _simple(den)
    else:
        out = _simple(t)
    return out if sign > 0 else -out


SPLIT = re.compile(rf"\s(\+|{MINUS}|-)\s")


def value(text: str) -> Val:
    """A printed option as an exact value: 7.6, 4√74, 58 + 58√2, 3/√3, 16/23."""
    t = str(text).strip()
    parts = SPLIT.split(t)
    out = _term(parts[0])
    for i in range(1, len(parts), 2):
        piece = _term(parts[i + 1])
        out = out + piece if parts[i] == "+" else out - piece
    return out


def numbers(text: str) -> list[Val]:
    """Every standalone number in a stem, in printed order."""
    found = []
    for m in re.finditer(rf"{MINUS}?\d[\d,]*(?:\.\d+)?(?:/\d+)?|{ROOT}\d+|"
                         rf"\d+{ROOT}\d+", text):
        try:
            found.append(value(m.group(0)))
        except Unreadable:
            pass
    return found


# ================================================ a drawn figure -> geometry

N = r"([-\d.]+)"
TRI = re.compile(rf'<path class="ax" d="M{N},{N} L{N},{N} L{N},{N} Z"/>')
MARK = re.compile(rf'<path class="sg" d="M{N},{N} L{N},{N} L{N},{N}"/>')
SEG = re.compile(rf'<line class="ax" x1="{N}" y1="{N}" x2="{N}" y2="{N}"/>')
TEXT = re.compile(rf'<text class="(lb|an|vx|nt)" x="{N}" y="{N}" '
                  rf'text-anchor="\w+">([^<]*)</text>')
SHADE = re.compile(r'<path class="sh" d="([^"]*)"/>')


def _dist(p, q) -> float:
    return math.hypot(p[0] - q[0], p[1] - q[1])


def _angle_at(v, a, b) -> float:
    u = (a[0] - v[0], a[1] - v[1])
    w = (b[0] - v[0], b[1] - v[1])
    n = math.hypot(*u) * math.hypot(*w)
    if n == 0:
        raise Unreadable("a degenerate corner")
    return math.degrees(math.acos(max(-1.0, min(1.0, (u[0] * w[0] + u[1] * w[1]) / n))))


@dataclass
class Figure:
    """What a reader with a ruler and a protractor gets out of the SVG.

    Every number here comes from the pixels: the three drawn corners, the
    corner the right-angle square sits on, the text nearest each side's
    midpoint and each corner. Not one parameter of the item is consulted, so a
    figure that disagrees with its own stem is visible here and nowhere else.
    """
    verts: list
    marks: list                 # the vertex each right-angle square marks
    segs: list                  # extra drawn segments (a cut, an altitude)
    labels: list                # (class, x, y, text)
    sides: dict = None          # side key -> the length written beside it
    angles: dict = None         # vertex key -> the angle written inside it
    names: dict = None          # vertex key -> the letter written beside it
    extra: dict = None          # named spots that are not corners of the triangle

    # ----------------------------------------------------------- lookups

    def _assign(self, anchors: dict, cls: str) -> dict:
        """Every label of one class goes to the spot it is nearest.

        This is what a reader does -- a number printed beside a segment names
        that segment -- and it is deliberately not told which spots the
        renderer meant to use.
        """
        out = {}
        for c, x, y, t in self.labels:
            if c != cls:
                continue
            key = min(anchors, key=lambda k: _dist((x, y), anchors[k]))
            if key in out:
                raise Unreadable(f"two {cls} labels are nearest the same spot {key}")
            out[key] = t
        return out

    def wire(self, more_sides=None, more_points=None) -> "Figure":
        mids = {(a, b): ((self.verts[a][0] + self.verts[b][0]) / 2,
                         (self.verts[a][1] + self.verts[b][1]) / 2)
                for a, b in ((0, 1), (0, 2), (1, 2))}
        mids.update(more_sides or {})
        pts = {0: self.verts[0], 1: self.verts[1], 2: self.verts[2]}
        self.extra = dict(more_points or {})
        self.sides = self._assign(mids, "lb")
        self.angles = self._assign(pts, "an")
        self.names = self._assign({**pts, **self.extra}, "vx")
        return self

    def side(self, i, j=None) -> str | None:
        key = i if j is None else (min(i, j), max(i, j))
        return self.sides.get(key)

    def angle_text(self, i: int) -> str | None:
        return self.angles.get(i)

    def name(self, i) -> str | None:
        return self.names.get(i)

    def named(self) -> dict:
        """letter -> the point it labels, whether a corner or a marked spot."""
        out = {}
        for key, text in self.names.items():
            out[text] = self.verts[key] if isinstance(key, int) else self.extra[key]
        return out

    def length(self, i: int, j: int) -> float:
        return _dist(self.verts[i], self.verts[j])

    def corner(self, i: int) -> float:
        j, k = [n for n in range(3) if n != i]
        return _angle_at(self.verts[i], self.verts[j], self.verts[k])

    @property
    def right(self) -> int:
        """The index of the vertex the right-angle square is drawn on."""
        if not self.marks:
            raise Unreadable("no right angle is marked")
        hit = [i for i in range(3) if _dist(self.verts[i], self.marks[0]) < 1.0]
        if len(hit) != 1:
            raise Unreadable("the right-angle square is not on a drawn vertex")
        return hit[0]

    @property
    def note(self) -> bool:
        return any(c == "nt" for c, _, _, _ in self.labels)


def figure(svg: str, wire: bool = True) -> Figure:
    if not svg:
        raise Unreadable("this item carries no figure")
    tri = TRI.findall(svg)
    if len(tri) != 1:
        raise Unreadable(f"{len(tri)} triangles are drawn")
    nums = [float(v) for v in tri[0]]
    verts = [(nums[0], nums[1]), (nums[2], nums[3]), (nums[4], nums[5])]
    marks = []
    for g in MARK.findall(svg):
        p1 = (float(g[0]), float(g[1]))
        p2 = (float(g[2]), float(g[3]))
        p3 = (float(g[4]), float(g[5]))
        if abs(_dist(p1, p2) - _dist(p2, p3)) > 0.3:
            raise Unreadable("the right-angle marking is not square")
        marks.append((p1[0] + p3[0] - p2[0], p1[1] + p3[1] - p2[1]))
    segs = [tuple(float(v) for v in g) for g in SEG.findall(svg)]
    labels = [(g[0], float(g[1]), float(g[2]), g[3]) for g in TEXT.findall(svg)]
    fig = Figure(verts, marks, segs, labels)
    return fig.wire() if wire else fig


def check_triangle(fig: Figure) -> dict:
    """The generic figure assertion, run on every item that carries a triangle.

    Returns the pixels-per-unit scale the numeric labels imply, so a template
    can then measure an unlabelled side and read its length off the picture.
    """
    i = fig.right
    assert abs(fig.corner(i) - 90.0) < 0.4, \
        f"the right-angle square is drawn on a {fig.corner(i):.1f}° corner"
    for j in range(3):
        if j != i:
            assert fig.corner(j) < 89.7, \
                f"two corners of the drawn triangle are right angles"
    # every angle label that states a number must be the angle actually drawn
    for j in range(3):
        text = fig.angle_text(j)
        if text and text.endswith(DEG) and text[:-1].isdigit():
            drawn = fig.corner(j)
            assert abs(drawn - float(text[:-1])) < 0.6, \
                f"the corner labelled {text} is drawn at {drawn:.2f}°"
    # every pair of numerically labelled sides must be drawn in that ratio
    known = []
    for a, b in ((0, 1), (0, 2), (1, 2)):
        text = fig.side(a, b)
        if text is None:
            continue
        try:
            val = float(value(text))
        except Unreadable:
            continue
        if val > 0:
            known.append((val, fig.length(a, b)))
    for (v1, px1), (v2, px2) in zip(known, known[1:]):
        assert abs(px1 / px2 - v1 / v2) < 0.01 * max(1.0, v1 / v2), \
            (f"the sides labelled {v1:g} and {v2:g} are drawn "
             f"{px1:.1f} and {px2:.1f} pixels long")
    scale = {px / v for v, px in known}
    return {"scale": (sum(px / v for v, px in known) / len(known)) if known else None,
            "spread": (max(scale) / min(scale)) if known else 1.0}


def measured(fig: Figure, scale: float, i: int, j: int) -> float:
    """The length of a drawn side, in the figure's own units."""
    return fig.length(i, j) / scale


# =============================================== deciding an option set

def _keyed(item) -> int:
    return "ABCD".index(item.answer)


def one_hit(item, hits: list[bool], what: str) -> str:
    """The assertion every check makes: exactly one right, and it is the key."""
    assert sum(hits) == 1, (f"{sum(hits)} of the options are {what}: "
                            + ", ".join(f"{'ABCD'[i]}) {c}" for i, c in
                                        enumerate(item.choices) if hits[i]))
    assert hits[_keyed(item)], (f"the key is {item.answer}) "
                                f"{item.choices[_keyed(item)]!r}, but the option that "
                                f"is {what} is "
                                f"{'ABCD'[hits.index(True)]}) "
                                f"{item.choices[hits.index(True)]!r}")
    return what


def options(item) -> list[Val]:
    return [value(c) for c in item.choices]


def decide(item, target: float, what: str, tol: float = 1e-9) -> str:
    """Exactly one printed option is this number, and it is the keyed one."""
    if item.fmt == "spr":
        got = value(item.answer)
        assert abs(float(got) - target) <= tol * max(1.0, abs(target)), \
            f"the grid-in answer is {item.answer!r}, but {what} is {target!r}"
        return what
    hits = [abs(float(v) - target) <= tol * max(1.0, abs(target)) for v in options(item)]
    return one_hit(item, hits, what)


def decide_closest(item, true_value: float, what: str) -> str:
    """For a *closest to* stem: the nearest printed option, and only one."""
    vals = [float(v) for v in options(item)]
    gaps = sorted((abs(v - true_value), i) for i, v in enumerate(vals))
    assert gaps[1][0] - gaps[0][0] > 1e-9 * max(1.0, abs(true_value)), \
        f"two printed options are equally close to {true_value!r}"
    hits = [i == gaps[0][1] for i in range(4)]
    return one_hit(item, hits, what)


# ====================================================== the sides family

def _sides_of(fig) -> dict:
    """Every side of the drawn triangle that carries a number, by vertex pair."""
    out = {}
    for a, b in ((0, 1), (0, 2), (1, 2)):
        t = fig.side(a, b)
        if t and _numeric(t):
            out[(a, b)] = float(value(t))
    return out


def check_pythagoras(item) -> str:
    approx = "closest" in item.stem
    if item.figure:
        fig = figure(item.figure)
        info = check_triangle(fig)
        i = fig.right
        o1, o2 = [n for n in range(3) if n != i]
        hyp_key = (min(o1, o2), max(o1, o2))
        known = _sides_of(fig)
        assert len(known) == 2, \
            f"the figure labels {len(known)} of its sides with a number"
        if hyp_key in known:
            big = known[hyp_key]
            small = next(v for k, v in known.items() if k != hyp_key)
            assert big > small, "the side drawn opposite the right angle is not the longest"
            true = math.sqrt(big * big - small * small)
        else:
            true = math.hypot(*known.values())
        missing = next(k for k in ((min(i, o1), max(i, o1)), (min(i, o2), max(i, o2)),
                                   hyp_key) if k not in known)
        assert info["scale"], "no side of the drawn triangle carries a length"
        drawn = fig.length(*missing) / info["scale"]
        assert abs(drawn - true) < 0.01 * true, \
            (f"the unlabelled side is drawn {drawn:.3f} long where the two labelled "
             f"sides make it {true:.3f}")
    else:
        nums = [float(v) for v in numbers(item.stem)]
        assert len(nums) >= 2, f"the stem states {len(nums)} lengths"
        if "hypotenuse of length" in item.stem:
            assert nums[0] > nums[1], "the stated leg is not shorter than the hypotenuse"
            true = math.sqrt(nums[0] ** 2 - nums[1] ** 2)
        else:
            true = math.hypot(nums[0], nums[1])
    if approx:
        return decide_closest(item, true, "closest to the third side")
    return decide(item, true, "the third side", tol=1e-9)


def _numeric(text: str) -> bool:
    try:
        return float(value(text)) > 0
    except Unreadable:
        return False


EXPR = re.compile(rf"^(?:{ROOT}\()?(.+?)\)?$")


TERM = re.compile(rf"(\d[\d,]*)({SUP2})?")


def _eval_expression(text: str) -> float:
    """Evaluate a printed expression: √(21² − 6²), 21² − 6², (21² + 6²)/2.

    Hand-parsed rather than handed to `eval`: the whole grammar is a sum or a
    difference of two terms, each a number that may be squared, optionally
    under a radical and optionally halved.
    """
    t = text.strip().replace(MINUS, "-")
    root = t.startswith(ROOT)
    if root:
        t = t[1:]
    half = False
    if t.endswith("/2") and t.startswith("("):
        t, half = t[:-2], True
    if t.startswith("(") and t.endswith(")"):
        t = t[1:-1]
    pieces = re.split(r"\s([+-])\s", t.strip())
    if len(pieces) not in (1, 3):
        raise Unreadable(f"{text!r} is not an expression this evaluates")

    def term(s: str) -> float:
        m = TERM.fullmatch(s.strip())
        if m is None:
            raise Unreadable(f"{s!r} is not a term this evaluates")
        v = float(m.group(1).replace(",", ""))
        return v * v if m.group(2) else v

    out = term(pieces[0])
    if len(pieces) == 3:
        out = out + term(pieces[2]) if pieces[1] == "+" else out - term(pieces[2])
    if half:
        out /= 2.0
    if root:
        return math.sqrt(out) if out >= 0 else float("nan")
    return out


def check_leg_expression(item) -> str:
    fig = figure(item.figure)
    check_triangle(fig)
    i = fig.right
    o1, o2 = [n for n in range(3) if n != i]
    hyp_key = (min(o1, o2), max(o1, o2))
    nums = _sides_of(fig)
    assert len(nums) == 2, f"the figure labels {len(nums)} of its sides with a number"
    if hyp_key in nums:
        big = nums[hyp_key]
        small = next(v for k, v in nums.items() if k != hyp_key)
        assert big > small, "the side drawn opposite the right angle is not the longest"
        true = math.sqrt(big * big - small * small)
    else:
        true = math.hypot(*nums.values())
    hits = []
    for c in item.choices:
        try:
            v = _eval_expression(c)
        except Unreadable:
            v = float("nan")
        hits.append(v == v and abs(v - true) < 1e-9 * max(1.0, true))
    return one_hit(item, hits, "the missing side")


def check_rectangle_diagonal(item) -> str:
    m = re.search(r"diagonal is ([^,]+), and the length of the rectangle's "
                  r"(shorter|longer) side is ([^.]+)\.", item.stem)
    if m is None:
        m = re.search(r"diagonal of length (\S+) and a (shorter|longer) side of "
                      r"length ([^.]+)\.", item.stem)
    assert m, f"the stem does not state a diagonal and a side: {item.stem[:80]!r}"
    d, other = float(value(m.group(1))), float(value(m.group(3)))
    assert d > other, "the printed diagonal is not the longest side"
    true = math.sqrt(d * d - other * other)
    want = "longer" if "longer side?" in item.stem else "shorter"
    if want == m.group(2):
        raise Unreadable("the stem asks for the side it states")
    return decide(item, true, f"the {want} side", tol=1e-9)


SPECIAL_ANGLE = re.compile(rf"^(\d+){DEG}$")


def _solve_right(fig) -> dict:
    """Every side of the drawn triangle, from what is printed on it.

    A right triangle is fixed by two sides, or by one side and one acute
    angle, and both come off the page: the numbers beside the sides and the
    degrees written inside the corners. Working in the printed numbers rather
    than in pixels is what lets the options be decided exactly.
    """
    i = fig.right
    o1, o2 = [n for n in range(3) if n != i]
    hyp = (min(o1, o2), max(o1, o2))
    leg = {j: (min(i, j), max(i, j)) for j in (o1, o2)}
    known = _sides_of(fig)
    angles = {}
    for j in (o1, o2):
        t = fig.angle_text(j)
        if t and t.endswith(DEG) and t[:-1].isdigit():
            angles[j] = float(t[:-1])
    if len(known) >= 2:
        L = dict(known)
        if hyp in L:
            other = next(k for k in L if k != hyp)
            rest = L[hyp] ** 2 - L[other] ** 2
            assert rest > 0, "the side opposite the right angle is not the longest"
            L[next(leg[j] for j in (o1, o2) if leg[j] != other)] = math.sqrt(rest)
        else:
            L[hyp] = math.hypot(L[leg[o1]], L[leg[o2]])
    else:
        assert len(known) == 1 and angles, \
            (f"the figure states {len(known)} lengths and {len(angles)} angles, "
             f"which does not pin the triangle down")
        (key, size), = known.items()
        j, deg = next(iter(angles.items()))
        other = o2 if j == o1 else o1
        r = math.radians(deg)
        if key == hyp:
            h = size
        elif key == leg[j]:
            h = size / math.cos(r)
        else:
            h = size / math.sin(r)
        L = {hyp: h, leg[j]: h * math.cos(r), leg[other]: h * math.sin(r)}
    # and the picture has to be the triangle those numbers describe
    ratios = [fig.length(*k) / v for k, v in L.items()]
    assert max(ratios) / min(ratios) < 1.005, \
        (f"the printed numbers make the sides {['%.2f' % v for v in L.values()]}, "
         f"which is not the shape drawn")
    return L


def check_special_triangle(item) -> str:
    fig = figure(item.figure)
    check_triangle(fig)
    L = _solve_right(fig)
    segment = re.search(r"the length of ([A-Z])([A-Z]) \?", item.stem)
    letter = re.search(r"the value of ([a-z]) \?", item.stem)
    if segment:
        names = {fig.name(j): j for j in range(3) if fig.name(j)}
        a, b = segment.group(1), segment.group(2)
        assert a in names and b in names, f"{a}{b} names a corner that is not drawn"
        key = (min(names[a], names[b]), max(names[a], names[b]))
        return decide(item, L[key], f"the length of {a}{b}", tol=1e-9)
    assert letter, f"the stem asks for nothing this reads: {item.stem[:70]!r}"
    x = letter.group(1)
    i = fig.right
    for j in range(3):
        if fig.angle_text(j) == f"{x}{DEG}":
            assert j != i, "the stem asks for the measure of the right angle"
            other = next(n for n in range(3) if n not in (i, j))
            opp = L[(min(i, other), max(i, other))]
            hyp = L[(min(n for n in range(3) if n != i),
                     max(n for n in range(3) if n != i))]
            deg = math.degrees(math.asin(opp / hyp))
            return decide(item, deg, f"the angle marked {x}{DEG}", tol=1e-9)
    for a, b in ((0, 1), (0, 2), (1, 2)):
        if fig.side(a, b) == x:
            return decide(item, L[(a, b)], f"the side marked {x}", tol=1e-9)
    raise Unreadable(f"nothing in the figure is labelled {x!r}")


R2, R3 = math.sqrt(2.0), math.sqrt(3.0)
SHAPES = {
    "isosceles right triangle": {"leg": 1.0, "short": 1.0, "long": 1.0, "hyp": R2,
                                 "perimeter": 2.0 + R2},
    "triangle with angle measures 30\u00b0, 60\u00b0, and 90\u00b0":
        {"short": 1.0, "long": R3, "hyp": 2.0, "perimeter": 3.0 + R3},
}
GIVEN_PHRASE = {"a perimeter of": "perimeter", "a hypotenuse of length": "hyp",
                "a leg of length": "leg", "a shorter leg of length": "short",
                "a longer leg of length": "long"}
ASK_PHRASE = {"the perimeter": "perimeter", "one leg": "leg", "the other leg": "leg",
              "the hypotenuse": "hyp", "the longest side": "hyp",
              "the shorter leg": "short", "the shortest side": "short",
              "the longer leg": "long"}
UNIT_TAIL = re.compile(r"\s+(inches|centimeters|feet|meters|units)$")


def check_special_perimeter(item) -> str:
    shape = next((k for k in SHAPES if k in item.stem), None)
    assert shape, f"the stem names no special triangle: {item.stem[:70]!r}"
    parts = SHAPES[shape]
    m = re.search(r"has (a perimeter of|a hypotenuse of length|a leg of length|"
                  r"a shorter leg of length|a longer leg of length) ([^.]+)\. What",
                  item.stem)
    if m:
        given, stated = GIVEN_PHRASE[m.group(1)], m.group(2)
    else:
        m = re.search(r"^The perimeter of .+? is ([^.]+)\. What", item.stem)
        assert m, f"the stem states no measure: {item.stem[:90]!r}"
        given, stated = "perimeter", m.group(1)
    stated = UNIT_TAIL.sub("", stated.strip())
    mm = re.search(r"What is the length(?:, in [a-z]+,)? of (.+?) of this triangle\?",
                   item.stem)
    if mm:
        ask_phrase = mm.group(1)
    else:
        assert re.search(r"What is the perimeter(?:, in [a-z]+,)? of this triangle\?",
                         item.stem), f"the stem asks for nothing this reads: " \
                                     f"{item.stem[-70:]!r}"
        ask_phrase = "the perimeter"
    assert ask_phrase in ASK_PHRASE, f"{ask_phrase!r} is not a measure this reads"
    ask = ASK_PHRASE[ask_phrase]
    assert given in parts and ask in parts, \
        f"{shape} has no measure called {given!r} or {ask!r}"
    assert given != ask, "the stem asks for the measure it states"
    base = float(value(stated)) / parts[given]
    return decide(item, base * parts[ask], ask_phrase, tol=1e-9)


def check_equilateral_logo(item) -> str:
    svg = item.figure or ""
    drawn = len(TRI.findall(svg))
    shaded = len(SHADE.findall(svg))
    assert drawn >= 3 and drawn % 2 == 1, f"{drawn} triangles are drawn"
    word = {"three": 3, "five": 5, "seven": 7, "nine": 9}
    named = next((v for k, v in word.items() if f"{k} congruent" in item.stem), None)
    assert named == drawn, f"the stem says {named} triangles and {drawn} are drawn"
    m = re.search(r"perimeter of the logo is (\d[\d,]*)|perimeter of the logo is "
                  r"(\d[\d,]*)", item.stem)
    if m is None:
        m = re.search(r"perimeter of the logo is (\d[\d,]*)", item.stem)
    assert m, f"the stem states no perimeter: {item.stem[:90]!r}"
    perim = float((m.group(1) or m.group(2)).replace(",", ""))
    s = perim / (drawn + 2)
    one = math.sqrt(3.0) / 4.0 * s * s
    if "combined area of the shaded regions" in item.stem:
        n, what = shaded, "the shaded area"
    elif "area of one of the triangles" in item.stem:
        n, what = 1, "one triangle's area"
    else:
        n, what = drawn, "the whole logo's area"
    assert 1 <= shaded < drawn, f"{shaded} of {drawn} triangles are shaded"
    return decide(item, n * one, what, tol=1e-9)


# ===================================================== the ratios family

def _ratio_at(fig: Figure, vertex: int, fn: str) -> float:
    i = fig.right
    assert vertex != i, "a right angle has no ratio"
    other = next(j for j in range(3) if j not in (i, vertex))
    opp = fig.length(i, other)
    adj = fig.length(i, vertex)
    hyp = fig.length(vertex, other)
    return {"sin": opp / hyp, "cos": adj / hyp, "tan": opp / adj}[fn]


ASK_RATIO = re.compile(rf"the value of (sin|cos|tan) ([A-Z]|[a-z]{DEG}) \?")
STEM_SIDE = re.compile(rf"([A-Z])([A-Z]) = (\d*{ROOT}\d+|\d[\d,]*)")


def check_trig_ratio(item) -> str:
    fig = figure(item.figure)
    check_triangle(fig)
    i = fig.right
    known = dict(_sides_of(fig))
    names = {fig.name(j): j for j in range(3) if fig.name(j)}
    for a, b, text in STEM_SIDE.findall(item.stem):
        if a in names and b in names:
            key = (min(names[a], names[b]), max(names[a], names[b]))
            known[key] = float(value(text))
    o = [n for n in range(3) if n != i]
    hyp_key = (min(o[0], o[1]), max(o[0], o[1]))
    legs = [(min(i, j), max(i, j)) for j in o]
    assert len(known) >= 2, f"only {len(known)} sides of the triangle are stated"
    if hyp_key not in known:
        known[hyp_key] = math.hypot(known[legs[0]], known[legs[1]])
    else:
        for a, b in (legs, legs[::-1]):
            if a not in known:
                rest = known[hyp_key] ** 2 - known[b] ** 2
                assert rest > 0, "the stated leg is not shorter than the hypotenuse"
                known[a] = math.sqrt(rest)
    m = ASK_RATIO.search(item.stem)
    assert m, f"the stem asks for no ratio: {item.stem[:80]!r}"
    fn, who = m.group(1), m.group(2)
    if who.endswith(DEG):
        spots = [j for j in range(3) if fig.angle_text(j) == who]
        assert len(spots) == 1, f"{len(spots)} corners are marked {who}"
        vertex = spots[0]
    else:
        assert who in names, f"{who} is not a drawn corner"
        vertex = names[who]
    assert vertex != i, "the stem asks for a ratio at the right angle"
    other = next(j for j in o if j != vertex)
    opp = known[(min(i, other), max(i, other))]
    adj = known[(min(i, vertex), max(i, vertex))]
    hyp = known[hyp_key]
    true = {"sin": opp / hyp, "cos": adj / hyp, "tan": opp / adj}[fn]
    # and the picture has to draw the same triangle the numbers describe
    drawn = _ratio_at(fig, vertex, fn)
    assert abs(drawn - true) < 3e-3 * max(1.0, true), \
        f"the stated sides make {fn} {who} = {true:.5f}; the figure draws {drawn:.5f}"
    return decide(item, true, f"{fn} {who}", tol=1e-7)


def check_ratio_to_side(item) -> str:
    m = re.search(r"(sin|cos|tan) ([A-Z]) = (\d[\d,]*)/(\d[\d,]*)", item.stem)
    assert m, f"the stem states no ratio: {item.stem[:90]!r}"
    fn, at = m.group(1), m.group(2)
    ratio = float(m.group(3).replace(",", "")) / float(m.group(4).replace(",", ""))
    angle = {"sin": math.asin, "cos": math.acos, "tan": math.atan}[fn](ratio)
    right = re.search(r"[Aa]ngle ([A-Z]) is a right angle", item.stem)
    seg = re.search(r"length of ([A-Z]{2}) is ([\d,]+)", item.stem)
    if seg is None:
        fig = figure(item.figure)
        check_triangle(fig)
        rname = fig.name(fig.right)
        stated = [(k, v) for k, v in _sides_of(fig).items()]
        assert len(stated) == 1, f"the figure labels {len(stated)} sides"
        (a, b), given_len = stated[0]
        pair = f"{fig.name(a)}{fig.name(b)}"
    else:
        assert right, f"the stem says which angle is right: {item.stem[:90]!r}"
        rname = right.group(1)
        given_len = float(seg.group(2).replace(",", ""))
        pair = seg.group(1)
    if right:
        rname = right.group(1)
    kind = lambda s: ("hyp" if rname not in s else ("adj" if at in s else "opp"))
    hyp = {"adj": given_len / math.cos(angle), "opp": given_len / math.sin(angle),
           "hyp": given_len}[kind(pair)]
    want = re.search(r"of (?:side )?([A-Z]{2}) \?", item.stem)
    assert want, f"the stem asks for no side: {item.stem[-60:]!r}"
    asked = want.group(1)
    assert asked != pair, "the stem asks for the side it states"
    true = {"adj": hyp * math.cos(angle), "opp": hyp * math.sin(angle),
            "hyp": hyp}[kind(asked)]
    return decide(item, true, f"the length of {asked}", tol=1e-7)


TRIG_OPT = re.compile(r"^(sin|cos|tan) ([A-Z])$")


def check_cofunction_match(item) -> str:
    fig = figure(item.figure)
    check_triangle(fig)
    m = re.search(r"same value as (sin|cos|tan) ([A-Z])|equal to (sin|cos|tan) ([A-Z])",
                  item.stem)
    assert m, f"the stem names no ratio: {item.stem[:80]!r}"
    fn, who = (m.group(1) or m.group(3)), (m.group(2) or m.group(4))
    names = {fig.name(j): j for j in range(3)}
    assert who in names, f"{who} is not a drawn vertex"
    target = _ratio_at(fig, names[who], fn)
    hits = []
    for c in item.choices:
        mo = TRIG_OPT.fullmatch(c.strip())
        assert mo, f"{c!r} is not a ratio this reads"
        g, v = mo.group(1), mo.group(2)
        assert v in names, f"{c!r} names a vertex that is not drawn"
        if (g, v) == (fn, who):
            hits.append(False)          # the ratio the stem already names
            continue
        hits.append(abs(_ratio_at(fig, names[v], g) - target) < 1e-9)
    return one_hit(item, hits, f"equal to {fn} {who}")


def check_cofunction_angles(item) -> str:
    m = re.search(r"(cos|sin) ([A-Z]) = (sin|cos) ([A-Z])", item.stem)
    assert m, f"the stem states no cofunction: {item.stem[:80]!r}"
    exprs = re.findall(rf"((?:\d+)?x (?:\+|{MINUS}) \d+)", item.stem)
    assert len(exprs) == 2, f"the stem prints {len(exprs)} angle measures"

    def evaluate(text, x):
        mm = re.fullmatch(rf"(\d+)?x (\+|{MINUS}) (\d+)", text)
        coef = int(mm.group(1)) if mm.group(1) else 1
        const = int(mm.group(3)) * (1 if mm.group(2) == "+" else -1)
        return coef * x + const

    f1, f2 = {"cos": math.cos, "sin": math.sin}[m.group(1)], \
        {"cos": math.cos, "sin": math.sin}[m.group(3)]
    if item.fmt == "spr":
        cands = [float(value(item.answer))]
    else:
        cands = [float(v) for v in options(item)]
    hits = []
    for x in cands:
        a1, a2 = evaluate(exprs[0], x), evaluate(exprs[1], x)
        ok = (0 < a1 < 90 and 0 < a2 < 90
              and abs(f1(math.radians(a1)) - f2(math.radians(a2))) < 1e-12)
        hits.append(ok)
    if item.fmt == "spr":
        assert hits[0], f"the grid-in answer {item.answer!r} does not satisfy the stem"
        return "the value of x"
    return one_hit(item, hits, "a value of x the stem's equation holds at")


def check_complement_tangent(item) -> str:
    m = re.search(r"tangent of one of the two acute angles is ([^.]+)\.", item.stem)
    if m is None:
        m = re.search(r"has a tangent of ([^.]+)\.", item.stem)
    assert m, f"the stem states no tangent: {item.stem[:80]!r}"
    t = float(value(m.group(1)))
    assert t > 0, "the tangent of an acute angle is positive"
    return decide(item, 1.0 / t, "the other angle's tangent", tol=1e-12)


def check_complement_ratio(item) -> str:
    m = re.search(r"(sin|cos|tan) ([A-Z]) = (\d[\d,]*)/(\d[\d,]*)", item.stem)
    assert m, f"the stem states no ratio: {item.stem[:90]!r}"
    fn, p_, q_ = m.group(1), float(m.group(3).replace(",", "")), \
        float(m.group(4).replace(",", ""))
    angle = {"sin": math.asin, "cos": math.acos, "tan": math.atan}[fn](p_ / q_)
    want = re.search(r"the value of (sin|cos|tan) ([A-Z]) \?", item.stem)
    assert want, f"the stem asks for no ratio: {item.stem[-50:]!r}"
    rm = re.search(r"[Aa]ngle ([A-Z]) is a right angle", item.stem)
    assert rm, f"the stem does not say which angle is right"
    right = rm.group(1)
    assert want.group(2) not in (m.group(2), right), \
        "the stem asks about the vertex it states, or about the right angle"
    other = math.pi / 2.0 - angle
    true = {"sin": math.sin, "cos": math.cos, "tan": math.tan}[want.group(1)](other)
    return decide(item, true, f"{want.group(1)} {want.group(2)}", tol=1e-9)


def check_split_right_angle(item) -> str:
    fig = figure(item.figure)
    check_triangle(fig)
    m = re.search(rf"(cos|sin)\(∠([A-Z])([A-Z])([A-Z])\) {MINUS} "
                  rf"(cos|sin)\(∠([A-Z])([A-Z])([A-Z])\)", item.stem)
    assert m, f"the stem asks for no difference: {item.stem[:90]!r}"
    f1, r, s, w = m.group(1), m.group(2), m.group(3), m.group(4)
    f2, w2, s2, t = m.group(5), m.group(6), m.group(7), m.group(8)
    assert s == s2 and w == w2, "the two angles do not share the vertex and the ray"
    assert {f1, f2} == {"cos", "sin"}, "both pieces use the same function"
    names = {fig.name(j): j for j in range(3)}
    assert names.get(s) == fig.right, \
        f"the shared vertex {s} is not where the right angle is drawn"
    assert r in names and t in names, "the ray's endpoints are not both drawn"
    # solved on the drawn coordinates, at three places for W
    a, b = fig.verts[names[r]], fig.verts[names[t]]
    v = fig.verts[names[s]]
    fn = {"cos": math.cos, "sin": math.sin}
    for u in (0.2, 0.5, 0.8):
        wp = (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
        val = (fn[f1](math.radians(_angle_at(v, a, wp)))
               - fn[f2](math.radians(_angle_at(v, wp, b))))
        assert abs(val) < 1e-3, f"the difference is {val} when W is {u} along RT"
    return decide(item, 0.0, "the difference of the two ratios", tol=1e-9)


# ================================================== the similar family

CORR = re.compile(r"Triangle ([A-Z])([A-Z])([A-Z]) is similar to triangle "
                  r"([A-Z])([A-Z])([A-Z]), where (?:angle )?([A-Z]) corresponds to "
                  r"(?:angle )?([A-Z])")


def _correspondence(stem: str):
    m = CORR.search(stem)
    assert m, f"the stem prints no correspondence: {stem[:100]!r}"
    first = (m.group(1), m.group(2), m.group(3))
    second = (m.group(4), m.group(5), m.group(6))
    pairs = dict(zip(first, second))
    assert pairs.get(m.group(7)) == m.group(8), \
        (f"the stem says {m.group(7)} corresponds to {m.group(8)}, but the order of "
         f"the letters pairs it with {pairs.get(m.group(7))}")
    return first, second, pairs


def check_similar_ratio(item) -> str:
    first, second, pairs = _correspondence(item.stem)
    right = re.search(r"[Aa]ngles? ([A-Z]) and ([A-Z]) are right angles", item.stem)
    assert right, "the stem does not say which angles are right angles"
    m = re.search(r"If (sin|cos|tan) ([A-Z]) = (\d[\d,]*)/(\d[\d,]*)", item.stem)
    assert m, f"the stem states no ratio: {item.stem[:110]!r}"
    fn, at = m.group(1), m.group(2)
    p_, q_ = float(m.group(3).replace(",", "")), float(m.group(4).replace(",", ""))
    angle = {"sin": math.asin, "cos": math.acos, "tan": math.atan}[fn](p_ / q_)
    want = re.search(r"the value of (sin|cos|tan) ([A-Z]) \?", item.stem)
    assert want, f"the stem asks for no ratio: {item.stem[-60:]!r}"
    asked = want.group(2)
    # walk the correspondence both ways to find whether the asked vertex is the
    # partner of the stated one or the other acute vertex
    back = {v: k for k, v in pairs.items()}
    assert asked in back, f"{asked} is not a vertex of the second triangle"
    here = back[asked]
    assert here != right.group(1), "the stem asks about the right angle"
    theta = angle if here == at else math.pi / 2.0 - angle
    true = {"sin": math.sin, "cos": math.cos, "tan": math.tan}[want.group(1)](theta)
    return decide(item, true, f"{want.group(1)} {asked}", tol=1e-9)


def check_similar_side(item) -> str:
    first, second, pairs = _correspondence(item.stem)
    m = re.search(r"tan ([A-Z]) = (\S+) and ([A-Z]{2}) = ([\d,]+)", item.stem)
    assert m, f"the stem states no tangent and side: {item.stem[:120]!r}"
    t = float(value(m.group(2)))
    leg = float(m.group(4).replace(",", ""))
    angle = math.atan(t)
    right = re.search(r"[Aa]ngles ([A-Z]) and ([A-Z]) are right angles", item.stem)
    assert right, "the stem does not say which angles are right angles"
    rname = next(g for g in right.groups() if g in second)
    stated, want = m.group(3), re.search(r"the length of ([A-Z]{2}) \?", item.stem)
    assert want, f"the stem asks for no side: {item.stem[-60:]!r}"
    asked = want.group(1)
    at = pairs[m.group(1)]
    assert rname in stated and at in stated, \
        f"{stated} is not the leg adjacent to {at}"
    true = leg / math.cos(angle) if rname not in asked else leg * math.tan(angle)
    return decide(item, true, f"the length of {asked}", tol=1e-9)


def check_similar_sides_ratio(item) -> str:
    sides = dict(re.findall(r"([A-Z]{2}) = ([\d,]+)", item.stem))
    assert len(sides) == 3, f"{len(sides)} side lengths are printed"
    lengths = {k: float(v.replace(",", "")) for k, v in sides.items()}
    longest = max(lengths, key=lengths.get)
    rest = [k for k in lengths if k != longest]
    a, b = lengths[rest[0]], lengths[rest[1]]
    assert abs(a * a + b * b - lengths[longest] ** 2) < 1e-6 * lengths[longest] ** 2, \
        "the three printed sides are not a right triangle"
    right = (set(rest[0]) & set(rest[1])).pop()         # the shared vertex
    # the correspondence is the order of the two triangle names; the sentence
    # that spells part of it out has to agree with that order
    m = re.search(r"[Tt]riangle ([A-Z])([A-Z])([A-Z]) is similar to triangle "
                  r"([A-Z])([A-Z])([A-Z]), where ([A-Z]) corresponds to ([A-Z]) and "
                  r"([A-Z]) corresponds to ([A-Z])", item.stem)
    assert m, f"the stem prints no correspondence: {item.stem[:160]!r}"
    pairs = dict(zip(m.group(1, 2, 3), m.group(4, 5, 6)))
    for x, y in ((m.group(7), m.group(8)), (m.group(9), m.group(10))):
        assert pairs.get(x) == y, \
            (f"the stem says {x} corresponds to {y}, but the order of the letters "
             f"pairs it with {pairs.get(x)}")
    want = re.search(r"the value of (sin|cos|tan) ([A-Z]) \?", item.stem)
    assert want, f"the stem asks for no ratio: {item.stem[-60:]!r}"
    back = {v: k for k, v in pairs.items()}
    assert want.group(2) in back, f"{want.group(2)} has no partner in the first triangle"
    here = back[want.group(2)]
    assert here != right, "the stem asks about the right angle"
    opp = lengths[next(k for k in rest if here not in k)]
    adj = lengths[next(k for k in rest if here in k)]
    hyp = lengths[longest]
    true = {"sin": opp / hyp, "cos": adj / hyp, "tan": opp / adj}[want.group(1)]
    return decide(item, true, f"{want.group(1)} {want.group(2)}", tol=1e-9)


# ============================================= two triangles in one figure

def check_altitude_special(item) -> str:
    fig = figure(item.figure, wire=False)
    assert len(fig.segs) == 1, f"{len(fig.segs)} extra segments are drawn"
    assert len(fig.marks) == 1, f"{len(fig.marks)} right angles are marked"
    seg = fig.segs[0]
    apex, foot = (seg[0], seg[1]), (seg[2], seg[3])
    hit = [i for i in range(3) if _dist(fig.verts[i], apex) < 1.0]
    assert len(hit) == 1, "the altitude does not start at a drawn vertex"
    b = hit[0]
    base = [i for i in range(3) if i != b]
    assert abs(_angle_at(foot, fig.verts[base[0]], apex) - 90.0) < 0.4, \
        "the altitude is not drawn perpendicular to the base"
    assert _dist(fig.marks[0], foot) < 1.0, \
        "the right-angle square is not drawn at the foot of the altitude"
    assert abs(_dist(fig.verts[base[0]], foot) + _dist(foot, fig.verts[base[1]])
               - fig.length(*base)) < 0.6, \
        "the foot of the altitude is not drawn on the base"
    mid = lambda p, q: ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    fig.wire(more_sides={"ad": mid(fig.verts[base[0]], foot),
                         "dc": mid(foot, fig.verts[base[1]]),
                         "bd": mid(apex, foot)},
             more_points={"d": foot})
    # which base vertex the apex angle is measured to, and which carries its own
    apex_text = fig.angle_text(b)
    assert apex_text and apex_text.endswith(DEG) and apex_text[:-1].isdigit(), \
        "the angle the altitude makes at the apex is not marked"
    alpha = float(apex_text[:-1])
    # the base vertex that carries its own measure is the one the stem uses;
    # the apex angle is then the half of the split that faces the other one
    lettered = [j for j in base
                if (fig.angle_text(j) or "").endswith(DEG)
                and (fig.angle_text(j) or " ")[:-1].isdigit()]
    assert len(lettered) == 1, f"{len(lettered)} base angles carry a measure"
    c_i = lettered[0]
    a_i = next(j for j in base if j != c_i)
    halves = {j: _angle_at(apex, foot, fig.verts[j]) for j in base}
    assert abs(halves[a_i] - alpha) < 0.6, \
        (f"the apex is labelled {apex_text} but the altitude leaves "
         f"{halves[a_i]:.2f}{DEG} on that side")
    gamma = float(fig.angle_text(c_i)[:-1])
    assert abs(fig.corner(c_i) - gamma) < 0.6, \
        f"the corner labelled {c_text} is drawn at {fig.corner(c_i):.2f}{DEG}"
    A, B, C = fig.name(a_i), fig.name(b), fig.name(c_i)
    D = fig.name("d")
    assert None not in (A, B, C, D), "a point of the figure is not named"
    ra, rc = math.radians(alpha), math.radians(gamma)
    unit = {frozenset((B, D)): 1.0, frozenset((A, D)): math.tan(ra),
            frozenset((D, C)): 1.0 / math.tan(rc),
            frozenset((A, B)): 1.0 / math.cos(ra),
            frozenset((B, C)): 1.0 / math.sin(rc),
            frozenset((A, C)): math.tan(ra) + 1.0 / math.tan(rc)}
    pair = {(min(a_i, b), max(a_i, b)): frozenset((A, B)),
            (min(b, c_i), max(b, c_i)): frozenset((B, C)),
            (min(a_i, c_i), max(a_i, c_i)): frozenset((A, C)),
            "ad": frozenset((A, D)), "dc": frozenset((D, C)),
            "bd": frozenset((B, D))}
    scale = None
    for key, text in fig.sides.items():
        if text and _numeric(text) and key in pair:
            scale = float(value(text)) / unit[pair[key]]
    assert scale, "no drawn segment carries a length"
    # the picture has to be the triangle the two marked angles describe
    points = fig.named()
    px = _dist(points[B], points[D])
    for names, size in unit.items():
        x, y = tuple(names)
        assert abs(_dist(points[x], points[y]) / size - px) < 5e-3 * px, \
            f"{x}{y} is not drawn at the length the marked angles give it"
    want = re.search(r"the length of ([A-Z])([A-Z]) \?", item.stem)
    assert want, f"the stem asks for no segment: {item.stem[-60:]!r}"
    key = frozenset((want.group(1), want.group(2)))
    assert key in unit, f"{want.group(0)} is not a segment of this figure"
    return decide(item, unit[key] * scale,
                  f"the length of {want.group(1)}{want.group(2)}", tol=1e-9)


def _cut_figure(item):
    fig = figure(item.figure, wire=False)
    assert len(fig.segs) == 1, f"{len(fig.segs)} cuts are drawn"
    assert len(fig.marks) == 2, f"{len(fig.marks)} right angles are marked"
    seg = fig.segs[0]
    foot, edge = (seg[0], seg[1]), (seg[2], seg[3])
    i = fig.right
    on_leg = [j for j in range(3) if j != i
              and abs(_dist(fig.verts[i], foot) + _dist(foot, fig.verts[j])
                      - fig.length(i, j)) < 0.5]
    assert len(on_leg) == 1, "the cut does not start on a leg of the triangle"
    near = on_leg[0]
    far = next(j for j in range(3) if j not in (i, near))
    assert abs(_dist(fig.verts[near], edge) + _dist(edge, fig.verts[far])
               - fig.length(near, far)) < 0.6, \
        "the cut does not end on the hypotenuse"
    v1 = (edge[0] - foot[0], edge[1] - foot[1])
    v2 = (fig.verts[far][0] - fig.verts[i][0], fig.verts[far][1] - fig.verts[i][1])
    cross = v1[0] * v2[1] - v1[1] * v2[0]
    assert abs(cross) < 1e-3 * math.hypot(*v1) * math.hypot(*v2), \
        "the cut is not drawn parallel to the other leg"
    assert abs(_angle_at(foot, fig.verts[i], edge) - 90.0) < 0.4, \
        "the cut is not drawn square to the leg it crosses"
    mid = lambda p, q: ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    fig.wire(more_sides={"cut": mid(foot, edge), "stub": mid(fig.verts[i], foot),
                         "upper": mid(foot, fig.verts[near]),
                         "lower_hyp": mid(fig.verts[near], edge),
                         "upper_hyp": mid(edge, fig.verts[far])},
             more_points={"foot": foot, "edge": edge})
    check_triangle(fig)
    ends = {(0, 1): (fig.verts[0], fig.verts[1]), (0, 2): (fig.verts[0], fig.verts[2]),
            (1, 2): (fig.verts[1], fig.verts[2]), "cut": (foot, edge),
            "stub": (fig.verts[i], foot), "upper": (foot, fig.verts[near]),
            "lower_hyp": (fig.verts[near], edge), "upper_hyp": (edge, fig.verts[far])}
    return fig, foot, edge, i, near, far, ends


def check_nested_similar(item) -> str:
    fig, foot, edge, i, near, far, ends = _cut_figure(item)
    points = fig.named()
    names = {fig.name(j): j for j in range(3) if fig.name(j)}
    m = re.search(r"tan ([A-Z]) = (\d+)/(\d+)", item.stem)
    assert m, f"the stem states no tangent: {item.stem[:90]!r}"
    at = m.group(1)
    assert at in names and names[at] == near, \
        f"the stem takes its tangent at {at}, which is not the corner the cut meets"
    printed = float(m.group(2)) / float(m.group(3))
    drawn = _ratio_at(fig, names[at], "tan")
    assert abs(drawn - printed) < 3e-3 * printed, \
        f"the stem says tan {at} = {printed:.4f} but the figure draws {drawn:.4f}"
    stated = dict(((a + b), float(v.replace(",", "")))
                  for a, b, v in re.findall(r"([A-Z])([A-Z]) = ([\d,]+)", item.stem))
    # the whole triangle from the stem's own numbers, then the cut-off one
    A, B, C = fig.name(i), fig.name(near), fig.name(far)
    D, Ev = fig.name("foot"), fig.name("edge")
    hyp = next((v for k, v in stated.items() if set(k) == {B, C}), None)
    cut = next((v for k, v in stated.items() if set(k) == {D, A}), None)
    assert hyp and cut, f"the stem states {sorted(stated)} rather than {B}{C} and {D}{A}"
    sin_b = printed / math.hypot(printed, 1.0)
    cos_b = 1.0 / math.hypot(printed, 1.0)
    ac, ab = hyp * sin_b, hyp * cos_b
    assert 0 < cut < ab, "the cut does not lie on the leg"
    share = (ab - cut) / ab
    L = {frozenset((A, C)): ac, frozenset((A, B)): ab, frozenset((B, C)): hyp,
         frozenset((D, A)): cut, frozenset((B, D)): ab - cut,
         frozenset((D, Ev)): ac * share, frozenset((B, Ev)): hyp * share}
    # the picture has to be that same pair of triangles
    for pair, size in L.items():
        a, b = tuple(pair)
        assert abs(_dist(points[a], points[b]) / size - _dist(points[A], points[C]) / ac) \
            < 5e-3 * _dist(points[A], points[C]) / ac, \
            f"{a}{b} is not drawn at the length the stem's numbers give it"
    want = re.search(r"the length of ([A-Z])([A-Z]) \?", item.stem)
    assert want, f"the stem asks for no segment: {item.stem[-60:]!r}"
    key = frozenset((want.group(1), want.group(2)))
    assert key in L, f"{want.group(0)} is not a segment of this figure"
    return decide(item, L[key], f"the length of {want.group(1)}{want.group(2)}",
                  tol=1e-9)


def check_parallel_similar(item) -> str:
    fig, foot, edge, i, near, far, ends = _cut_figure(item)
    points = fig.named()
    A, C, Ev = fig.name(i), fig.name(near), fig.name(far)
    B, D = fig.name("foot"), fig.name("edge")
    m = re.search(r"([A-Z])([A-Z]) is parallel to ([A-Z])([A-Z])", item.stem)
    assert m, f"the stem names no parallel pair: {item.stem[:80]!r}"
    assert {m.group(1), m.group(2)} == {B, D} and {m.group(3), m.group(4)} == {A, Ev}, \
        f"the stem calls {m.group(0)} parallel, which is not the cut and the leg"
    u = (points[m.group(2)][0] - points[m.group(1)][0],
         points[m.group(2)][1] - points[m.group(1)][1])
    w = (points[m.group(4)][0] - points[m.group(3)][0],
         points[m.group(4)][1] - points[m.group(3)][1])
    assert abs(u[0] * w[1] - u[1] * w[0]) < 1e-3 * math.hypot(*u) * math.hypot(*w), \
        f"{m.group(1)}{m.group(2)} is not drawn parallel to {m.group(3)}{m.group(4)}"
    stated = {}
    for key, text in fig.sides.items():
        if text and _numeric(text):
            a, b = ends[key]
            stated[key] = (float(value(text)), a, b)
    ae = next((v for k, (v, _, _) in stated.items() if k == (min(i, far), max(i, far))),
              None)
    bd = next((v for k, (v, _, _) in stated.items() if k == "cut"), None)
    cb = next((v for k, (v, _, _) in stated.items() if k == "upper"), None)
    assert ae and bd and cb, \
        f"the figure does not label the leg, the cut and the stub"
    k = ae / bd
    assert k > 1.0, "the cut is not shorter than the leg it is parallel to"
    ca, cd = k * cb, math.hypot(cb, bd)
    L = {frozenset((A, Ev)): ae, frozenset((B, D)): bd, frozenset((C, B)): cb,
         frozenset((C, A)): ca, frozenset((C, D)): cd, frozenset((C, Ev)): k * cd,
         frozenset((A, B)): ca - cb, frozenset((D, Ev)): k * cd - cd}
    ref = _dist(points[A], points[Ev]) / ae
    for pair, size in L.items():
        a, b = tuple(pair)
        assert abs(_dist(points[a], points[b]) / size - ref) < 5e-3 * ref, \
            f"{a}{b} is not drawn at the length the figure's own labels give it"
    want = re.search(r"the length of ([A-Z])([A-Z]) \?", item.stem)
    assert want, f"the stem asks for no segment: {item.stem[-60:]!r}"
    key = frozenset((want.group(1), want.group(2)))
    assert key in L, f"{want.group(0)} is not a segment of this figure"
    return decide(item, L[key], f"the length of {want.group(1)}{want.group(2)}",
                  tol=1e-9)


CHECKS = {
    "rtt.pythagoras": check_pythagoras,
    "rtt.leg_expression": check_leg_expression,
    "rtt.rectangle_diagonal": check_rectangle_diagonal,
    "rtt.special_triangle": check_special_triangle,
    "rtt.special_perimeter": check_special_perimeter,
    "rtt.equilateral_logo": check_equilateral_logo,
    "rtt.trig_ratio": check_trig_ratio,
    "rtt.ratio_to_side": check_ratio_to_side,
    "rtt.cofunction_match": check_cofunction_match,
    "rtt.cofunction_angles": check_cofunction_angles,
    "rtt.complement_tangent": check_complement_tangent,
    "rtt.complement_ratio": check_complement_ratio,
    "rtt.split_right_angle": check_split_right_angle,
    "rtt.similar_ratio": check_similar_ratio,
    "rtt.similar_side": check_similar_side,
    "rtt.similar_sides_ratio": check_similar_sides_ratio,
    "rtt.altitude_special": check_altitude_special,
    "rtt.nested_similar": check_nested_similar,
    "rtt.parallel_similar": check_parallel_similar,
}


# ================================================================= selftest

def _swap(item, i: int, text: str):
    ch = list(item.choices)
    ch[i] = text
    return replace(item, choices=ch)


def _not_key(item) -> int:
    return next(i for i in range(4) if "ABCD"[i] != item.answer)


def _second_answer_radical():
    """The key printed twice, in the topic's two spellings for a radical.

    4√74 and √1,184 are one number. A check that compared strings would call
    the second one a distractor.
    """
    item = generate("rtt.pythagoras", 0, mode="hypotenuse", a=28, b=20, frame="text",
                    fmt="mcq", wrongs=["difference", "add", "sum_squares"])
    return _swap(item, _not_key(item), f"{ROOT}1,184")


def _key_moved():
    item = generate("rtt.similar_sides_ratio", 0, triple=(55, 48, 73), scale=8,
                    ask_fn="tan", ask_at="W", names=(("S", "R", "T"), ("V", "U", "W")),
                    fmt="mcq", wrongs=["sin", "cos", "reciprocal"])
    return replace(item, answer="ABCD"[_not_key(item)])


def _dropped_denominator():
    """A rendering slip: the key printed without its denominator."""
    item = generate("rtt.trig_ratio", 0, hyp=29, leg=21, mode="triple", fn="tan",
                    at="q", names=("C", "B", "A"), layout="right", fmt="mcq",
                    wrongs=["sin", "cos", "reciprocal"])
    return _swap(item, _keyed(item), "20")


def _figure_from_another_draw():
    """The right triangle of one item over the stem of another."""
    a = generate("rtt.trig_ratio", 0, hyp=73, leg=63, mode="two_sides", fn="sin",
                 at="p", letter="x", names=False, layout="left", fmt="mcq",
                 wrongs=["unit_leg", "diff_over_hyp", "sum_over_hyp"])
    b = generate("rtt.trig_ratio", 0, hyp=53, leg=45, mode="two_sides", fn="sin",
                 at="p", letter="x", names=False, layout="left", fmt="mcq",
                 wrongs=["unit_leg", "diff_over_hyp", "sum_over_hyp"])
    return replace(a, figure=b.figure)


def _right_angle_moved():
    """The right-angle square drawn on the wrong corner of the same triangle."""
    item = generate("rtt.trig_ratio", 0, hyp=73, leg=63, mode="two_sides", fn="sin",
                    at="p", letter="x", names=False, layout="left", fmt="mcq",
                    wrongs=["unit_leg", "diff_over_hyp", "sum_over_hyp"])
    fig = figure(item.figure)
    v = fig.verts
    bad = (f'<path class="sg" d="M{v[1][0]},{v[1][1] + 11} '
           f'L{v[1][0] + 11},{v[1][1] + 11} L{v[1][0] + 11},{v[1][1]}"/>')
    svg = MARK.sub(bad, item.figure, count=1)
    return replace(item, figure=svg)


def _angle_label_lies():
    """A 45-45-90 figure whose marked angle says something else."""
    item = generate("rtt.special_triangle", 0, alpha=45, given="p", value=24, ask="q",
                    layout="right", label="x", mark="both", fmt="mcq", note=True,
                    wrongs=["angle_measure", "double", "sum_with_angle"])
    svg = item.figure.replace(">45°<", ">30°<", 1)
    return replace(item, figure=svg)


def _figure_out_of_scale():
    """The same labels over a triangle drawn in the wrong proportion."""
    a = generate("rtt.pythagoras", 0, mode="hypotenuse", a=3, b=7, approximate=True,
                 places=1, frame="figure", layout="left", fmt="mcq", note=True,
                 wrongs=["sqrt_sum", "average", "double_sum"])
    b = generate("rtt.pythagoras", 0, mode="hypotenuse", a=6, b=7, approximate=True,
                 places=1, frame="figure", layout="left", fmt="mcq", note=True,
                 wrongs=["sqrt_sum", "average", "double_sum"])
    svg = b.figure.replace(">6<", ">3<", 1)
    return replace(a, figure=svg)


def _tie_on_closest():
    """A *closest* stem with two options the same distance from the truth."""
    item = generate("rtt.pythagoras", 0, mode="hypotenuse", a=3, b=7, approximate=True,
                    places=1, frame="figure", layout="left", fmt="mcq", note=True,
                    wrongs=["sqrt_sum", "average", "double_sum"])
    true = math.hypot(3.0, 7.0)
    return _swap(item, _not_key(item), f"{2 * true - 7.6:.12f}")


def _correspondence_scrambled():
    """The similar-triangles stem relabelled so the correspondence contradicts it."""
    item = generate("rtt.similar_ratio", 0, given_fn="tan", given_at="A", p=21, q=20,
                    ask_fn="sin", ask_at="D", names=(("A", "B", "C"), ("D", "E", "F")),
                    fmt="mcq")
    bad = item.stem.replace("angle A corresponds to angle D",
                            "angle A corresponds to angle E")
    return replace(item, stem=bad)


def _cut_not_parallel():
    """The parallel segment tilted, so the two triangles are not similar."""
    item = generate("rtt.parallel_similar", 0, base=8, height=6, factor=3, ask="ce",
                    names=("C", "A", "E"), foot="B", edge="D", fmt="mcq", note=False)
    m = SEG.search(item.figure)
    x1, y1, x2, y2 = (float(v) for v in m.groups())
    bad = (f'<line class="ax" x1="{x1}" y1="{y1}" x2="{x2 + 14}" y2="{y2}"/>')
    return replace(item, figure=item.figure[:m.start()] + bad + item.figure[m.end():])


INJECTED = [
    ("the key a second time as √1,184 beside 4√74", _second_answer_radical,
     "rtt.pythagoras"),
    ("the key moved to another letter", _key_moved, "rtt.similar_sides_ratio"),
    ("the key printed without its denominator", _dropped_denominator,
     "rtt.trig_ratio"),
    ("a figure spliced from a draw at other lengths", _figure_from_another_draw,
     "rtt.trig_ratio"),
    ("the right-angle square drawn on the wrong corner", _right_angle_moved,
     "rtt.trig_ratio"),
    ("a marked angle that is not the angle drawn", _angle_label_lies,
     "rtt.special_triangle"),
    ("a triangle drawn out of proportion to its labels", _figure_out_of_scale,
     "rtt.pythagoras"),
    ("two options equally close on a 'closest' stem", _tie_on_closest,
     "rtt.pythagoras"),
    ("a correspondence the letter order contradicts", _correspondence_scrambled,
     "rtt.similar_ratio"),
    ("a parallel segment drawn out of parallel", _cut_not_parallel,
     "rtt.parallel_similar"),
]


def selftest() -> int:
    bad = 0
    for label, build, template in INJECTED:
        try:
            item = build()
        except Exception as exc:                                    # noqa: BLE001
            print(f" FAIL  {label}: could not be built ({type(exc).__name__}: {exc})")
            bad += 1
            continue
        try:
            CHECKS[template](item)
        except (AssertionError, Unreadable) as exc:
            print(f"  ok   {label}\n         caught: {str(exc)[:110]}")
            continue
        print(f" FAIL  {label}: NOT caught")
        bad += 1
    print(f"\n{len(INJECTED) - bad}/{len(INJECTED)} injected faults caught")
    return 1 if bad else 0


# ================================================= the official items too

def check_sources(verbose: bool) -> tuple[int, int]:
    """The same checks over the 33 encoded College Board items.

    Draws are the point -- a defect can live in a stem variant no official item
    uses -- but the argument runs the other way too: the unsimplified radical
    spelling `3/√3` and the `√3` tangent of item 3.6 are reachable only from
    the encoded source parameters, and those option sets would never be read by
    anything without this pass.
    """
    topic = load_topics()[SLUG]
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
    print(f"{mark} {'the 33 official items':<28} {made:>5,} items, {bad} defects")
    return made, bad


# =================================================================== driver

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--draws", type=int, default=600,
                    help="seeds to try per template (default 600)")
    ap.add_argument("--template", action="append",
                    help="check only this template; repeatable")
    ap.add_argument("--selftest", action="store_true",
                    help="inject known-bad items and confirm each is caught")
    ap.add_argument("--all", action="store_true",
                    help="report every defect, not only the first of each kind")
    ap.add_argument("--sources", action="store_true",
                    help="check only the 33 official items")
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
        print(f"{mark} {name:<28} {made:>5,} items ({mcq:,} with options), "
              f"{bad} defects   ({what})")
        worst |= 1 if bad else 0
    if not args.template:
        worst |= 1 if check_sources(args.all)[1] else 0
    return worst


if __name__ == "__main__":
    sys.exit(main())
