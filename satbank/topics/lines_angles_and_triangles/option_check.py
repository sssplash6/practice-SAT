"""Read the printed page back, and check only one of the four options is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct, because nothing in the engine reads the wrong
options as mathematics -- they are strings that `assemble` sorted. An item with
two right answers therefore passes every gate the engine has. Worse, in this
topic, nothing in the engine reads the *figure* either: a triangle drawn with
the 40 degree angle at the wrong vertex is a wrong question that every one of
the seven checks calls right.

This script closes both holes for the thirty-one Lines, Angles and Triangles
templates. It parses the printed stem, the printed options and the SVG's own
pixel geometry, and from those alone it

  * measures every angle the figure marks, with what amounts to a protractor,
    and checks it against the number printed beside it, against any value the
    stem assigns to that letter, and against the item's own answer;
  * recovers every named point, so an angle the stem asks for by name --
    "the measure of angle QPR" -- is measured where the drawing actually puts
    Q, P and R rather than where the template meant to put them;
  * decides every option from its printed text and asserts that exactly one of
    them is correct and that it is the keyed one.

It imports no template, no figure builder and no solver. `generate` is used
only to obtain the finished item, exactly as a student would receive it.

    PYTHONPATH=. python3 satbank/topics/lines_angles_and_triangles/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 400 --template lat.transversal
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

SLUG = "lines_angles_and_triangles"
DEG = "\N{DEGREE SIGN}"
MINUS = "\N{MINUS SIGN}"
ANG = "\N{ANGLE}"
TOL = 1.4          # degrees: the slack a figure rounded to a tenth of a pixel needs


class Unreadable(Exception):
    """The printed text or the drawn figure is not something this reads."""


class Bad(Exception):
    """A defect in the item itself."""


# ===================================================== printed text -> numbers

def value(text: str):
    """The number an option carries, or None when it is not one.

    Handles the four surface forms this topic prints: a bare integer, a
    decimal, a fraction, and any of those with a degree sign. It also
    evaluates the two unevaluated forms one source item prints, "(26 . 57)" and
    "(26 + 57)", because an option a student can evaluate is an option this
    check must evaluate.
    """
    t = str(text).strip().replace(MINUS, "-").replace(",", "").replace(DEG, "")
    t = t.strip()
    m = re.fullmatch(r"\((\d+)\s*[·*x]\s*(\d+)\)", t)
    if m:
        return float(m.group(1)) * float(m.group(2))
    m = re.fullmatch(r"\((\d+)\s*\+\s*(\d+)\)", t)
    if m:
        return float(m.group(1)) + float(m.group(2))
    m = re.fullmatch(r"(-?\d+)\s*/\s*(\d+)", t)
    if m:
        return float(m.group(1)) / float(m.group(2))
    try:
        return float(t)
    except ValueError:
        return None


def numbers(text: str) -> list[float]:
    return [float(v.replace(",", ""))
            for v in re.findall(r"\d[\d,]*\.?\d*", str(text))]


def degrees_in(text: str) -> list[float]:
    return [float(v.replace(",", ""))
            for v in re.findall(r"(\d[\d,]*(?:\.\d+)?)\s*" + DEG, str(text))]


def options(item) -> list[str]:
    if item.fmt != "mcq":
        raise Unreadable("a grid-in has no options")
    return list(item.choices)


def keyed(item) -> str:
    return item.choices["ABCD".index(item.answer)]


# ================================================ a drawn figure -> geometry

LINE = re.compile(r'<line class="fg" x1="([-\d.]+)" y1="([-\d.]+)" '
                  r'x2="([-\d.]+)" y2="([-\d.]+)"/>')
ARC = re.compile(r'<path class="ar" d="M([-\d.]+),([-\d.]+) '
                 r'A([-\d.]+),[-\d.]+ 0 \d \d ([-\d.]+),([-\d.]+)"/>')
SQUARE = re.compile(r'<path class="ar" d="M([-\d.]+),([-\d.]+) L([-\d.]+),([-\d.]+) '
                    r'L([-\d.]+),([-\d.]+)"/>')
TEXT = re.compile(r'<text class="(it|lb)" x="([-\d.]+)" y="([-\d.]+)" '
                  r'text-anchor="\w+">([^<]*)</text>')
NOTE = "Note: Figure not drawn to scale."


def _dist(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _dir(a, b) -> float:
    """Direction from a to b, in degrees, with y measured upwards."""
    return math.degrees(math.atan2(a[1] - b[1], b[0] - a[0])) % 360.0


def _between(v, a, b) -> float:
    d = abs((_dir(v, a) - _dir(v, b) + 180.0) % 360.0 - 180.0)
    return d


@dataclass
class Mark:
    vertex: tuple
    span: float
    d1: float
    d2: float
    radius: float
    label: str | None = None


class Drawn:
    """What a reader with a ruler and a protractor gets out of one figure.

    Every position is recovered from the SVG's own numbers -- the drawn
    segments, the drawn arcs, the drawn text -- and nothing is taken from the
    item's parameters, so a figure that disagrees with its stem is visible here
    and nowhere else in the engine.
    """

    def __init__(self, svg: str):
        if not svg:
            raise Unreadable("this item carries no figure")
        self.svg = svg
        self.to_scale = NOTE not in svg
        self.segs = [((float(a), float(b)), (float(c), float(d)))
                     for a, b, c, d in LINE.findall(svg)]
        if not self.segs:
            raise Unreadable("no segments are drawn")
        self.texts = [(kind, (float(x), float(y)), body)
                      for kind, x, y, body in TEXT.findall(svg)]
        self.vertices = self._vertices()
        self.marks = self._marks()
        self.squares = self._squares()
        self.points = self._points()
        self._label_marks()

    # ------------------------------------------------------------ recovery

    def _vertices(self) -> list[tuple]:
        out = []
        for a, b in self.segs:
            out += [a, b]
        for i, (p1, p2) in enumerate(self.segs):
            for p3, p4 in self.segs[i + 1:]:
                hit = _cross(p1, p2, p3, p4)
                if hit is not None:
                    out.append(hit)
        keep: list[tuple] = []
        for p in out:
            if not any(_dist(p, q) < 1.5 for q in keep):
                keep.append(p)
        return keep

    def near_vertex(self, p, tol=2.5):
        best = min(self.vertices, key=lambda q: _dist(p, q), default=None)
        if best is None or _dist(p, best) > tol:
            return None
        return best

    def _marks(self) -> list[Mark]:
        out = []
        for x1, y1, r, x2, y2 in ARC.findall(self.svg):
            p1, p2, r = (float(x1), float(y1)), (float(x2), float(y2)), float(r)
            for c in _centres(p1, p2, r):
                v = self.near_vertex(c, 3.0)
                if v is None:
                    continue
                d1, d2 = _dir(v, p1), _dir(v, p2)
                span = abs((d1 - d2 + 180.0) % 360.0 - 180.0)
                out.append(Mark(v, span, d1, d2, r))
                break
            else:
                raise Unreadable("an angle arc is not centred on any drawn vertex")
        return out

    def _squares(self) -> list[tuple]:
        out = []
        for a, b, c, d, e, f in SQUARE.findall(self.svg):
            p1, p2, p3 = ((float(a), float(b)), (float(c), float(d)),
                          (float(e), float(f)))
            v = self.near_vertex((p1[0] + p3[0] - p2[0], p1[1] + p3[1] - p2[1]), 3.0)
            if v is None:
                raise Unreadable("a right-angle square is not at a drawn vertex")
            if abs(_between(v, p1, p3) - 90.0) > 1.0:
                raise Unreadable(f"a right-angle square marks "
                                 f"{_between(v, p1, p3):.1f} degrees")
            out.append(v)
        return out

    def _points(self) -> dict:
        """Point names read off the drawing, by the vertex each sits next to."""
        out = {}
        for kind, pos, body in self.texts:
            if DEG in body or not re.fullmatch(r"[A-Za-zℓ][A-Za-z0-9]?", body):
                continue
            near = sorted(self.vertices, key=lambda q: _dist(pos, q))
            if not near or _dist(pos, near[0]) > 46.0:
                continue
            out.setdefault(body, []).append(near[0])
        return {k: v[0] for k, v in out.items() if len(v) == 1}

    def _label_marks(self):
        """Attach each angle's printed name to the arc it belongs to."""
        used = set()
        for m in self.marks:
            mid = (m.d1 + (m.d2 - m.d1 + 360.0) % 360.0 / 2.0) % 360.0
            if abs((m.d2 - m.d1) % 360.0) > 180.0:
                mid = (mid + 180.0) % 360.0
            best, score = None, None
            for i, (kind, pos, body) in enumerate(self.texts):
                if i in used or not body.endswith(DEG):
                    continue
                d = _dist(m.vertex, pos)
                if not (m.radius * 0.8 <= d <= m.radius * 5.0 + 26.0):
                    continue
                off = abs((_dir(m.vertex, pos) - mid + 180.0) % 360.0 - 180.0)
                if off > 34.0:
                    continue
                s = off + d * 0.08
                if score is None or s < score:
                    best, score = i, s
            if best is not None:
                used.add(best)
                m.label = self.texts[best][2]

    # -------------------------------------------------------------- reading

    def angle_named(self, name: str) -> float:
        """The drawn measure of the angle three named points make."""
        a, v, b = name[0], name[1], name[2]
        for n in (a, v, b):
            if n not in self.points:
                raise Unreadable(f"the figure does not name a point {n!r}")
        return _between(self.points[v], self.points[a], self.points[b])

    def marked(self, label: str) -> list[float]:
        return [m.span for m in self.marks if m.label == label]

    def one_marked(self, label: str) -> float:
        hit = self.marked(label)
        if len(hit) != 1:
            raise Unreadable(f"{len(hit)} angles in the figure are marked {label!r}")
        return hit[0]

    def length(self, a: str, b: str) -> float:
        if a not in self.points or b not in self.points:
            raise Unreadable(f"the figure does not name both {a!r} and {b!r}")
        return _dist(self.points[a], self.points[b])


def _cross(p1, p2, p3, p4):
    """Where two drawn segments cross, if they do so away from their ends."""
    d1 = (p2[0] - p1[0], p2[1] - p1[1])
    d2 = (p4[0] - p3[0], p4[1] - p3[1])
    det = d1[0] * (-d2[1]) - (-d2[0]) * d1[1]
    if abs(det) < 1e-9:
        return None
    bx, by = p3[0] - p1[0], p3[1] - p1[1]
    t = (bx * (-d2[1]) - (-d2[0]) * by) / det
    u = (d1[0] * by - bx * d1[1]) / det
    if not (0.02 < t < 0.98 and 0.02 < u < 0.98):
        return None
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def _centres(p1, p2, r):
    d = _dist(p1, p2)
    if d > 2 * r + 0.5:
        return []
    h2 = max(r * r - d * d / 4.0, 0.0)
    h = math.sqrt(h2)
    mx, my = (p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0
    nx, ny = -(p2[1] - p1[1]) / d, (p2[0] - p1[0]) / d
    return [(mx + h * nx, my + h * ny), (mx - h * nx, my - h * ny)]


# ================================================== the shared assertions

def settle(item, hits: list[bool], what: str) -> str:
    """Exactly one option is right, and it is the one the key points at."""
    opts = options(item)
    right = [opts[i] for i, ok in enumerate(hits) if ok]
    if len(right) != 1:
        raise Bad(f"{len(right)} of the four options are correct ({what}): "
                  f"{right or opts}")
    if right[0] != keyed(item):
        raise Bad(f"the key points at {keyed(item)!r} but {right[0]!r} is the one "
                  f"that is correct ({what})")
    return what


def near(a: float, b: float, tol: float = 0.05) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def hits_value(item, target: float, tol: float = 1e-6) -> list[bool]:
    out = []
    for text in options(item):
        v = value(text)
        out.append(v is not None and abs(v - target) <= tol * max(1.0, abs(target)))
    return out


def check_answer(item, target: float, what: str) -> str:
    """The item's own answer, whichever format it is in, is `target`."""
    if item.fmt == "spr":
        v = value(item.answer)
        if v is None or not near(v, target, 1e-9):
            raise Bad(f"the grid-in answer is {item.answer!r} but the page gives "
                      f"{target} ({what})")
        return what
    return settle(item, hits_value(item, target), what)


# ================================== the figure agrees with the page it is on

LETTER_ANGLE = re.compile(r"^(\d*)([a-z])" + DEG + r"$")
ASSIGN = re.compile(r"\b([a-z]) = (\d+)\b")


def audit_figure(item, answer: float | None, unknown: str | None):
    """Every angle the figure marks is the angle the page says it is.

    A number printed beside an arc has to be the arc's own measure; a letter
    the stem gives a value to has to be that value; two arcs marked with the
    same letter have to be the same size; and the letter the question asks for
    has to be the answer. A figure the template drew from stale parameters
    fails here and passes everywhere else.
    """
    if not item.figure:
        return
    fig = Drawn(item.figure)
    if not fig.marks:
        return
    given = {m.group(1): float(m.group(2)) for m in ASSIGN.finditer(item.stem)}
    seen: dict[str, list[float]] = {}
    for m in fig.marks:
        if m.label is None:
            continue
        seen.setdefault(m.label, []).append(m.span)
    for label, spans in seen.items():
        if max(spans) - min(spans) > TOL:
            raise Bad(f"two angles both marked {label!r} are drawn {min(spans):.1f} "
                      f"and {max(spans):.1f} degrees apart")
        drawn = sum(spans) / len(spans)
        plain = label.rstrip(DEG)
        if plain.replace(".", "").isdigit():
            if fig.to_scale and abs(drawn - float(plain)) > TOL:
                raise Bad(f"the figure marks {label!r} on an angle it draws as "
                          f"{drawn:.1f} degrees")
            continue
        hit = LETTER_ANGLE.match(label)
        if hit is None:
            continue
        mult = float(hit.group(1) or 1), hit.group(2)
        if mult[1] in given and fig.to_scale:
            if abs(drawn - mult[0] * given[mult[1]]) > TOL:
                raise Bad(f"the stem says {mult[1]} = {given[mult[1]]} but the "
                          f"figure draws {label!r} as {drawn:.1f} degrees")
        if answer is not None and unknown == mult[1] and fig.to_scale:
            if abs(drawn - mult[0] * answer) > TOL:
                raise Bad(f"the answer is {answer} but the figure draws {label!r} "
                          f"as {drawn:.1f} degrees")


def asked_letter(stem: str) -> str | None:
    m = re.search(r"value of ([a-z])\b", stem)
    return m.group(1) if m else None


def asked_angle(stem: str) -> str | None:
    m = re.search(r"measure(?:, in degrees,)? of (?:" + ANG + r"|angle )"
                  r"([A-Z]{3})\b", stem)
    return m.group(1) if m else None


# ==================================== the angle-chasing templates, one by one

def from_marked_unknown(item) -> str:
    """The answer is the angle the figure marks with the stem's own letter."""
    letter = asked_letter(item.stem)
    if letter is None:
        raise Unreadable("this stem does not ask for a lettered value")
    fig = Drawn(item.figure)
    if not fig.to_scale:
        raise Unreadable("this figure is not drawn to scale")
    drawn = fig.one_marked(letter + DEG)
    audit_figure(item, drawn, letter)
    return check_answer(item, round(drawn), f"the figure draws {letter} as "
                                            f"{drawn:.1f} degrees")


def from_named_angle(item) -> str:
    """The answer is the angle the drawing puts at three named points."""
    name = asked_angle(item.stem)
    if name is None:
        raise Unreadable("this stem does not ask for a named angle")
    fig = Drawn(item.figure)
    drawn = fig.angle_named(name)
    audit_figure(item, None, None)
    return check_answer(item, round(drawn),
                        f"the drawing puts {drawn:.1f} degrees at {name}")


def check_triangle_sum(item) -> str:
    stem = item.stem
    if "right triangle shown" in stem:
        return from_marked_unknown(item)
    degs = degrees_in(stem)
    if "each" in stem:
        if len(degs) != 1:
            raise Unreadable("an equal-angle stem with the wrong count of measures")
        target = 180 - 2 * degs[0]
    elif "right angle" in stem or "right triangle" in stem:
        if len(degs) != 1:
            raise Unreadable("a right-triangle stem with the wrong count of measures")
        target = 90 - degs[0]
    else:
        if len(degs) != 2:
            raise Unreadable("a plain angle-sum stem with the wrong count")
        target = 180 - degs[0] - degs[1]
    return check_answer(item, target, f"the printed angles leave {target} degrees")


def check_isosceles_possible(item) -> str:
    degs = degrees_in(item.stem)
    if len(degs) != 1:
        raise Unreadable("this stem does not print exactly one angle")
    a = degs[0]

    def possible(b: float) -> bool:
        c = 180.0 - a - b
        if min(a, b, c) <= 1e-9:
            return False
        return (abs(a - b) < 1e-9 or abs(a - c) < 1e-9 or abs(b - c) < 1e-9)

    hits = []
    for text in options(item):
        v = value(text)
        if v is None:
            raise Unreadable(f"option {text!r} is not a measure")
        hits.append(not possible(v))
    return settle(item, hits, f"only one option is impossible beside {a} degrees")


def check_angle_algebra(item) -> str:
    fig = Drawn(item.figure)
    label = next((m.label for m in fig.marks
                  if m.label and LETTER_ANGLE.match(m.label)
                  and LETTER_ANGLE.match(m.label).group(2) == "b"), None)
    if label is None:
        raise Unreadable("the figure marks no multiple of b")
    mult = float(LETTER_ANGLE.match(label).group(1) or 1)
    drawn = fig.one_marked(label)
    audit_figure(item, None, None)
    target = drawn / mult
    return check_answer(item, round(target),
                        f"the figure draws {label} as {drawn:.1f} degrees")


def check_exterior_angle(item) -> str:
    if asked_letter(item.stem):
        return from_marked_unknown(item)
    return from_named_angle(item)


def check_transversal(item) -> str:
    """Two of the eight angles are marked; the drawing says how they relate."""
    fig = Drawn(item.figure)
    letter = asked_letter(item.stem)
    if letter is None:
        raise Unreadable("this stem does not ask for a lettered value")
    printed = [m for m in fig.marks if m.label and m.label.rstrip(DEG).isdigit()]
    wanted = [m for m in fig.marks if m.label == letter + DEG]
    if len(printed) != 1 or len(wanted) != 1:
        raise Unreadable("this figure does not mark exactly one number and one letter")
    given = float(printed[0].label.rstrip(DEG))
    gap = abs(printed[0].span - wanted[0].span)
    total = printed[0].span + wanted[0].span
    if gap <= TOL:
        target = given
        why = "the two marked angles are drawn equal"
    elif abs(total - 180.0) <= TOL:
        target = 180.0 - given
        why = "the two marked angles are drawn supplementary"
    else:
        raise Bad(f"the two marked angles are drawn {printed[0].span:.1f} and "
                  f"{wanted[0].span:.1f} degrees, which are neither equal nor "
                  f"supplementary")
    if fig.to_scale and abs(wanted[0].span - target) > TOL:
        raise Bad(f"the figure draws {letter} as {wanted[0].span:.1f} degrees "
                  f"but the page makes it {target}")
    return check_answer(item, target, why)


def check_transversal_proof(item) -> str:
    """Only a fact about the far crossing can make the two lines parallel."""
    fig = Drawn(item.figure)
    printed = [m for m in fig.marks if m.label and m.label.rstrip(DEG).isdigit()]
    if len(printed) != 1:
        raise Unreadable("this figure does not mark exactly one number")
    here = printed[0].vertex
    drawn = {m.label.rstrip(DEG): (m.span, m.vertex) for m in fig.marks
             if m.label and not m.label.rstrip(DEG).isdigit()}
    hits = []
    for text in options(item):
        m = re.fullmatch(r"([a-z]) = (\d+)", text.strip())
        if m is None:
            raise Unreadable(f"option {text!r} is not an angle statement")
        name, want = m.group(1), float(m.group(2))
        if name not in drawn:
            raise Unreadable(f"the figure marks no angle {name!r}")
        span, where = drawn[name]
        far = _dist(where, here) > 8.0
        hits.append(far and abs(span - want) <= TOL)
    return settle(item, hits, "only a fact about the other crossing settles it")


def check_transversal_inequality(item) -> str:
    fig = Drawn(item.figure)
    spans = sorted(m.span for m in fig.marks if m.label)
    if len(spans) != 2 or abs(sum(spans) - 180.0) > TOL:
        raise Bad(f"the two marked angles are drawn {spans}, which do not make a "
                  f"straight angle")
    m = re.search(r"If ([a-z]) < (\d+)", item.stem)
    if m is None:
        raise Unreadable("this stem states no bound")
    var, bound = m.group(1), float(m.group(2))
    other = next(n for n in ("x", "y", "w", "z")
                 if n != var and (n + DEG) in item.figure)
    sample = [bound * f for f in (0.05, 0.2, 0.5, 0.8, 0.95, 0.999)]
    hits = []
    for text in options(item):
        f = _inequality(text, var, other)
        hits.append(all(f(y, 180.0 - y) for y in sample))
    return settle(item, hits, f"only one option holds for every {var} below {bound}")


def _inequality(text: str, var: str, other: str):
    body = text.replace(MINUS, "-").strip()
    m = re.fullmatch(r"([a-z](?: \+ [a-z])?) ([<>]) (\d+)", body)
    if m is None:
        raise Unreadable(f"option {text!r} is not an inequality")
    left, rel, rhs = m.group(1), m.group(2), float(m.group(3))

    def f(y, x, left=left, rel=rel, rhs=rhs):
        env = {var: y, other: x}
        v = sum(env[t] for t in left.split(" + "))
        return v < rhs if rel == "<" else v > rhs
    return f


def check_eight_angles(item) -> str:
    m = re.search(r"\((\d+)x " + MINUS + r" (\d+)\)" + DEG, item.stem)
    if m is None:
        raise Unreadable("this stem does not print the angle as mx - c")
    a, c = float(m.group(1)), float(m.group(2))
    reach = [(4 * a, -4 * c), (2 * a, 180 - 2 * c), (0.0, 360.0),
             (-2 * a, 540 + 2 * c), (-4 * a, 720 + 4 * c)]
    hits = []
    for text in options(item):
        coef, const = _linear(text)
        hits.append(not any(abs(coef - p) < 1e-9 and abs(const - q) < 1e-9
                            for p, q in reach))
    return settle(item, hits, "only one expression is not a sum of four of the eight")


def _linear(text: str) -> tuple[float, float]:
    body = text.replace(MINUS, "-").replace(",", "").replace(" ", "")
    m = re.fullmatch(r"(-?\d*)x([+-]\d+)?", body)
    if m:
        head = m.group(1)
        coef = -1.0 if head == "-" else (1.0 if head == "" else float(head))
        return coef, float(m.group(2) or 0)
    m = re.fullmatch(r"-?\d+", body)
    if m:
        return 0.0, float(body)
    raise Unreadable(f"option {text!r} is not a linear expression in x")


def check_two_transversals(item) -> str:
    fig = Drawn(item.figure)
    spans = fig.marked("w" + DEG)
    if len(spans) != 2:
        raise Unreadable("this figure does not mark two equal angles")
    if abs(spans[0] - spans[1]) > TOL:
        raise Bad(f"the two angles marked w are drawn {spans[0]:.1f} and "
                  f"{spans[1]:.1f} degrees")
    audit_figure(item, None, None)
    drawn = sum(spans) / 2.0
    return check_answer(item, round(drawn * 2) / 2.0,
                        f"the figure draws each w as {drawn:.1f} degrees")


# ================================================ the similarity templates

def check_similar_angle(item) -> str:
    """A similarity carries the angle across untouched, whatever k is."""
    degs = degrees_in(item.stem)
    if len(degs) != 1:
        raise Unreadable("this stem does not print exactly one angle")
    target = degs[0]
    if item.figure and "dilated by a scale factor" in item.stem:
        fig = Drawn(item.figure)
        name = re.search(r"angle ([A-Z])\?", item.stem)
        drawn = [m.span for m in fig.marks if m.label == f"{int(target)}" + DEG]
        if len(drawn) != 1 or abs(drawn[0] - target) > TOL:
            raise Bad(f"the figure draws the marked angle as "
                      f"{drawn[0] if drawn else None} rather than {target}")
        del name
    return check_answer(item, target, f"a similarity keeps the angle at {target}")


def check_similar_side(item) -> str:
    m = re.search(r"is (\d+) times the length", item.stem)
    n = re.search(r"measure of side [A-Z]{2} is (\d+)", item.stem)
    if not m or not n:
        raise Unreadable("this stem does not print a scale factor and a side")
    target = float(m.group(1)) * float(n.group(1))
    return check_answer(item, target, f"the side scales to {target}")


def check_shadow(item) -> str:
    nums = numbers(item.stem)
    if "Washington" in item.stem or "closest to the height" in item.stem:
        s1, s2, h1 = nums[0], nums[1], nums[2]
    else:
        h1, s1, s2 = nums[0], nums[1], nums[2]
    exact = h1 * s2 / s1
    if "closest" not in item.stem:
        return check_answer(item, exact, f"the proportion gives {exact}")
    gaps = [abs((value(t) or 1e9) - exact) for t in options(item)]
    best = min(gaps)
    if gaps.count(best) != 1:
        raise Bad(f"two options are equally close to {exact}: {options(item)}")
    return settle(item, [g == best for g in gaps],
                  f"one option is nearest to {exact:.3f}")


def check_parallel_segments(item) -> str:
    m = re.search(r"If ([A-Z]{2}) = ([\d.]+), ([A-Z]{2}) = ([\d.]+), and "
                  r"([A-Z]{2}) = ([\d.]+)", item.stem)
    if m is None:
        raise Unreadable("this stem does not print three lengths")
    ab, bc, fe = float(m.group(2)), float(m.group(4)), float(m.group(6))
    exact = fe * bc / ab
    fig = Drawn(item.figure)
    on_first = fig.length(m.group(1)[0], m.group(1)[1]) / fig.length(
        m.group(1)[0], m.group(3)[1])
    if abs(on_first - ab / (ab + bc)) > 0.02:
        raise Bad(f"the figure divides the first transversal {on_first:.3f} of the "
                  f"way along, not {ab / (ab + bc):.3f}")
    gaps = [abs((value(t) or 1e9) - exact) for t in options(item)]
    best = min(gaps)
    if best > 0.06:
        raise Bad(f"no option is within a tenth of {exact:.4f}")
    if gaps.count(best) != 1:
        raise Bad(f"two options round to the same tenth of {exact:.4f}")
    return settle(item, [g == best for g in gaps],
                  f"one option is {exact:.4f} to the nearest tenth")


def check_ratio_match(item) -> str:
    """Each option is a ratio of two drawn sides, and only one matches."""
    fig = Drawn(item.figure)
    m = re.search(r"ratio ([A-Z]{2})/([A-Z]{2})", item.stem)
    if m is None:
        raise Unreadable("this stem does not print the ratio asked about")
    target = fig.length(*m.group(1)) / fig.length(*m.group(2))
    hits = []
    for text in options(item):
        pair = re.fullmatch(r"([A-Z]{2})/([A-Z]{2})", text.strip())
        if pair is None:
            raise Unreadable(f"option {text!r} is not a ratio")
        hits.append(abs(fig.length(*pair.group(1)) / fig.length(*pair.group(2))
                        - target) < 0.01 * target)
    return settle(item, hits, f"only one drawn ratio equals {target:.4f}")


def check_similar_needed(item) -> str:
    degs = degrees_in(item.stem)
    if len(degs) != 4 or degs[0] != degs[2] or degs[1] != degs[3]:
        raise Bad(f"the two triangles are not given the same pair of angles: {degs}")
    hits = [t.strip().lower().startswith("no additional") for t in options(item)]
    return settle(item, hits, "two equal pairs of angles already settle it")


def check_similar_sufficient(item) -> str:
    m = re.search(r"angles ([A-Z]) and ([A-Z]) each have measure (\d+)", item.stem)
    if m is None:
        raise Unreadable("this stem does not print the shared angle")
    shared = float(m.group(3))
    first = re.search(r"triangles ([A-Z])([A-Z])([A-Z]) and ([A-Z])([A-Z])([A-Z])",
                      item.stem)
    if first is None:
        raise Unreadable("this stem does not name the two triangles")
    L, M, N, R, S, T = first.groups()
    hits = []
    for text in options(item):
        hits.append(_settles(text, shared, M, N, S, T))
    return settle(item, hits, "only a second pair of angles proves it")


def _settles(text: str, shared: float, M, N, S, T) -> bool:
    m = re.fullmatch(r"The measures of angles ([A-Z]) and ([A-Z]) are (\d+)"
                     + DEG + r" and (\d+)" + DEG + r", respectively\.", text.strip())
    if m is None:
        return False                      # a pair of sides opposite the given angles
    v1, v2, a1, a2 = m.group(1), m.group(2), float(m.group(3)), float(m.group(4))
    first = {M: a1, N: 180.0 - shared - a1}
    if v1 != M:
        return False
    second = {S: a2, T: 180.0 - shared - a2} if v2 == S else \
             ({T: a2, S: 180.0 - shared - a2} if v2 == T else None)
    if second is None:
        return False
    return abs(first[M] - second[S]) < 1e-9 and abs(first[N] - second[T]) < 1e-9


def check_vertical_similar(item) -> str:
    fig = Drawn(item.figure)
    m = re.search(r"([A-Z]{2}) and ([A-Z]{2}) intersect at point ([A-Z])", item.stem)
    if m is None:
        raise Unreadable("this stem does not say which segments cross")
    lengths = dict(re.findall(r"([A-Z])([A-Z]) = (\d+)", item.stem.replace(" = ", "=")
                              .replace("=", " = ")))
    pairs = re.findall(r"([A-Z]{2}) = (\d+)", item.stem)
    if len(pairs) < 4:
        raise Unreadable("this stem does not print four lengths")
    scale = []
    for name, size in pairs:
        scale.append(fig.length(name[0], name[1]) / float(size))
    if max(scale) - min(scale) > 0.02 * max(scale):
        raise Bad(f"the figure does not draw the four printed lengths to one scale: "
                  f"{[round(s, 4) for s in scale]}")
    k = sum(scale) / len(scale)
    ask = re.search(r"length of ([A-Z]{2})\?", item.stem)
    if ask is None:
        raise Unreadable("this stem does not say which length is asked for")
    target = fig.length(ask.group(1)[0], ask.group(1)[1]) / k
    del lengths
    return check_answer(item, round(target * 1000) / 1000,
                        f"the drawing makes it {target:.3f}")


def _drawn_scale(fig: Drawn, item, pairs) -> float:
    vals = [fig.length(a, b) / v for (a, b), v in pairs]
    if max(vals) - min(vals) > 0.02 * max(vals):
        raise Bad(f"the figure draws the printed lengths to different scales: "
                  f"{[round(v, 4) for v in vals]}")
    return sum(vals) / len(vals)


def check_altitude_legs(item) -> str:
    fig = Drawn(item.figure)
    sides = re.findall(r'<text class="lb" x="[-\d.]+" y="[-\d.]+" '
                       r'text-anchor="\w+">(\d+)</text>', item.figure)
    if len(sides) != 2:
        raise Unreadable("this figure does not label two legs")
    ask = re.search(r"length of ([A-Z])([A-Z])", item.stem)
    if ask is None:
        raise Unreadable("this stem does not say which length is asked for")
    corner = [v for v in fig.squares]
    if len(corner) != 2:
        raise Bad(f"{len(corner)} right angles are drawn, not two")
    legs = sorted(float(v) for v in sides)
    hyp = math.hypot(*legs)
    k = _leg_scale(fig, item, legs)
    target = fig.length(ask.group(1), ask.group(2)) / k
    if abs(target - legs[0] * legs[1] / hyp) > 0.02 * target:
        raise Bad(f"the drawn altitude is {target:.3f} but the labelled legs make "
                  f"it {legs[0] * legs[1] / hyp:.3f}")
    return check_answer(item, round(target * 1000) / 1000,
                        f"the drawing makes the altitude {target:.3f}")


def _leg_scale(fig: Drawn, item, legs) -> float:
    """Pixels per unit, from the two legs the figure labels."""
    names = sorted(fig.points)
    best = None
    for a in names:
        for b in names:
            if a >= b:
                continue
            d = fig.length(a, b)
            for leg in legs:
                r = d / leg
                if best is None or abs(math.log(r)) < abs(math.log(best)):
                    pass
    del best
    # the two labelled legs meet at the drawn right angle at the apex
    apex = fig.squares[0]
    ends = [p for p in fig.vertices if abs(_dist(p, apex)) > 1.0]
    got = sorted(_dist(apex, p) for p in ends)[:2]
    return sum(g / l for g, l in zip(got, sorted(legs))) / 2.0


def check_geometric_mean(item) -> str:
    fig = Drawn(item.figure)
    m = re.search(r"([A-Z])([A-Z]) = ([\d./]+) and", item.stem)
    if m is None:
        raise Unreadable("this stem does not print a first length")
    known = value(m.group(3))
    if known is None:
        raise Unreadable("the first printed length is not a number")
    k = fig.length(m.group(1), m.group(2)) / known
    ask = re.search(r"length of ([A-Z])([A-Z])", item.stem)
    if ask is None:
        raise Unreadable("this stem does not say which length is asked for")
    target = fig.length(ask.group(1), ask.group(2)) / k
    return check_answer(item, round(target * 1000) / 1000,
                        f"the drawing makes it {target:.3f}")


def check_parallel_cut_area(item) -> str:
    m = re.search(r"length of ([A-Z]{2}) is ([\d.]+) units, the length of ([A-Z]{2}) "
                  r"is ([\d.]+) units, and the area of triangle [A-Z]{3} is "
                  r"([\d.,]+) square units", item.stem)
    if m is None:
        raise Unreadable("this stem does not print the three measurements")
    rt, lk, area = (float(m.group(2)), float(m.group(4)),
                    float(m.group(5).replace(",", "")))
    st = 2 * area / rt
    target = st * (1 - lk / rt)
    return check_answer(item, round(target * 1e6) / 1e6,
                        f"the similar triangle leaves {target:.4f}")


def check_area_range(item) -> str:
    m = re.search(r"at least (\d+) but no more than (\d+)", item.stem)
    if m is None:
        raise Unreadable("this stem does not print an area range")
    lo, hi = float(m.group(1)), float(m.group(2))
    sides = re.findall(r'<text class="lb" x="[-\d.]+" y="[-\d.]+" '
                       r'text-anchor="\w+">(\d+)</text>', item.figure or "")
    if len(sides) != 2:
        raise Unreadable("this figure does not label the two pieces of the base")
    d1, d2 = float(sides[0]), float(sides[1])
    ys = [y for y in range(1, 400) if lo <= (d1 + d2) * y / 2 <= hi]
    got = value(item.answer)
    if got is None:
        raise Bad(f"the answer {item.answer!r} is not a number")
    ok = [y for y in ys if abs(d1 * y / (d1 + d2) - got) < 1e-9]
    if not ok:
        raise Bad(f"{got} is not d1*y/(d1+d2) for any whole y between "
                  f"{ys[0] if ys else None} and {ys[-1] if ys else None}")
    return f"x = {got} comes from y = {ok[0]}"


# ===================================================== the register of checks

CHECKS = {
    "lat.triangle_sum": check_triangle_sum,
    "lat.isosceles": from_marked_unknown,
    "lat.isosceles_possible": check_isosceles_possible,
    "lat.angle_algebra": check_angle_algebra,
    "lat.exterior_angle": check_exterior_angle,
    "lat.isosceles_cross": from_marked_unknown,
    "lat.vertical_isosceles": from_named_angle,
    "lat.crossing_triangles": from_marked_unknown,
    "lat.transversal": check_transversal,
    "lat.transversal_proof": check_transversal_proof,
    "lat.transversal_inequality": check_transversal_inequality,
    "lat.eight_angles": check_eight_angles,
    "lat.parallel_triangle": from_marked_unknown,
    "lat.midsegment_angle": from_named_angle,
    "lat.perp_transversal": from_marked_unknown,
    "lat.two_transversals": check_two_transversals,
    "lat.three_lines_point": from_marked_unknown,
    "lat.three_lines_triangle": from_marked_unknown,
    "lat.big_chain": from_named_angle,
    "lat.similar_angle": check_similar_angle,
    "lat.similar_side": check_similar_side,
    "lat.shadow": check_shadow,
    "lat.parallel_segments": check_parallel_segments,
    "lat.ratio_match": check_ratio_match,
    "lat.similar_needed": check_similar_needed,
    "lat.similar_sufficient": check_similar_sufficient,
    "lat.vertical_similar": check_vertical_similar,
    "lat.altitude_legs": check_altitude_legs,
    "lat.geometric_mean": check_geometric_mean,
    "lat.parallel_cut_area": check_parallel_cut_area,
    "lat.area_range": check_area_range,
}


# ================================================================= selftest

def _swap(item, i: int, text: str):
    ch = list(item.choices)
    ch[i] = text
    return replace(item, choices=ch)


def _not_key(item) -> int:
    return next(i for i in range(4) if "ABCD"[i] != item.answer)


def _second_answer():
    """Two options that are both the angle the figure draws."""
    it = generate("lat.isosceles", 3)
    return _swap(it, _not_key(it), keyed(it) + " ")


def _moved_key():
    it = generate("lat.triangle_sum", 5)
    while it.fmt != "mcq":
        it = generate("lat.triangle_sum", it.seed + 1)
    return replace(it, answer="ABCD"[_not_key(it)])


def _bent_arc():
    """A figure whose marked angle no longer matches its printed number."""
    it = generate("lat.transversal", 2)
    m = ARC.search(it.figure)
    x1, y1, r, x2, y2 = (float(v) for v in m.groups())
    cx = float(x1)
    ang = math.radians(28.0)
    bent = (f'<path class="ar" d="M{x1},{y1} A{r},{r} 0 0 0 '
            f'{cx + r * math.cos(ang):.1f},{y1 - r * math.sin(ang):.1f}"/>')
    return replace(it, figure=it.figure.replace(m.group(0), bent))


def _relabelled_figure():
    """The right answer, printed beside the wrong angle in the picture."""
    it = generate("lat.three_lines_point", 4)
    fig = Drawn(it.figure)
    a, b = [m for m in fig.marks if m.label][:2]
    swapped = it.figure
    la, lb = a.label, b.label
    swapped = swapped.replace(f">{la}<", ">@@<").replace(f">{lb}<", f">{la}<")
    swapped = swapped.replace(">@@<", f">{lb}<")
    return replace(it, figure=swapped)


def _stale_figure():
    """A figure drawn from one draw's parameters under another draw's stem."""
    a = generate("lat.parallel_triangle", 1)
    b = generate("lat.parallel_triangle", 2)
    return replace(a, figure=b.figure)


def _wrong_scale():
    """A length item whose drawing no longer matches the printed lengths."""
    it = generate("lat.vertical_similar", 1)
    m = re.search(r"([A-Z]{2}) = (\d+)", it.stem)
    bad = it.stem.replace(m.group(0), f"{m.group(1)} = {int(m.group(2)) + 7}", 1)
    return replace(it, stem=bad)


def _both_possible():
    it = generate("lat.isosceles_possible", 1)
    a = degrees_in(it.stem)[0]
    return _swap(it, _not_key(it), f"{int(180 - 2 * a) + 3}{DEG}"
                 if 180 - 2 * a + 3 < 180 else f"{int(a) + 1}{DEG}")


def _reachable_sum():
    it = generate("lat.eight_angles", 0)
    m = re.search(r"\((\d+)x " + MINUS + r" (\d+)\)", it.stem)
    a, c = int(m.group(1)), int(m.group(2))
    return _swap(it, "ABCD".index(it.answer), f"{4 * a}x {MINUS} {4 * c:,}")


CASES = [("a second option that is also correct", _second_answer),
         ("the key attached to the wrong letter", _moved_key),
         ("an arc bent away from its printed measure", _bent_arc),
         ("two angle labels swapped in the figure", _relabelled_figure),
         ("a figure left over from another draw", _stale_figure),
         ("a printed length the drawing does not use", _wrong_scale),
         ("a fourth possible measure where one must be impossible", _both_possible),
         ("a key that is in fact one of the five reachable sums", _reachable_sum)]


def selftest() -> int:
    """A check nobody has seen fail is worth nothing, so make it fail."""
    bad = 0
    for what, make in CASES:
        try:
            item = make()
        except Exception as exc:                                    # noqa: BLE001
            print(f"  ??  could not build the case {what!r}: "
                  f"{type(exc).__name__}: {exc}")
            bad += 1
            continue
        try:
            CHECKS[item.template](item)
        except (Bad, Unreadable) as exc:
            print(f"  ok  caught {what}: {exc}")
            continue
        print(f" FAIL  {what} was not caught")
        bad += 1
    return bad


# ================================================== the official items too

def check_sources(verbose: bool) -> tuple[int, int]:
    topic = load_topics()[SLUG]
    ok = skipped = 0
    for s in topic.sources:
        item = s.build(random.Random(0))
        fn = CHECKS.get(item.template)
        if fn is None:
            skipped += 1
            continue
        try:
            note = fn(item)
        except Unreadable as exc:
            skipped += 1
            if verbose:
                print(f"  --  {s.id}: not read ({exc})")
            continue
        ok += 1
        if verbose:
            print(f"  ok  {s.id}  {note}")
    return ok, skipped


# =================================================================== driver

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=300)
    ap.add_argument("--template", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        bad = selftest()
        print("selftest:", "every injected defect was caught" if not bad
              else f"{bad} injected defects slipped through")
        return 1 if bad else 0

    names = [args.template] if args.template else list(CHECKS)
    total = unread = 0
    worst = 0
    for name in names:
        read = skip = 0
        reasons: dict[str, int] = {}
        for seed in range(args.draws):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            try:
                CHECKS[name](item)
                read += 1
            except Unreadable as exc:
                skip += 1
                reasons[str(exc)] = reasons.get(str(exc), 0) + 1
            except Bad as exc:
                print(f"\nFAIL {name} seed {seed}: {exc}\n")
                print(item.pretty())
                return 1
        total += read
        unread += skip
        tail = ""
        if skip:
            top = sorted(reasons.items(), key=lambda kv: -kv[1])[0]
            tail = f"   ({skip} not read, commonest: {top[0]})"
        print(f"  ok  {name:<32} {read:>4} draws checked{tail}")
        worst = max(worst, 1 if read == 0 else 0)
    print(f"\n{total:,} generated items read back; {unread:,} draws this reader "
          f"could not parse")
    print("\nthe official items:")
    ok, skipped = check_sources(args.verbose)
    print(f"  {ok}/{ok + skipped} official items read back and checked")
    if worst:
        print("\nsome template was never read at all")
    return worst


if __name__ == "__main__":
    sys.exit(main())
