"""Generated figures for Lines, Angles, and Triangles.

The figure *is* the question here -- a transversal item is unanswerable
without knowing which of the eight angles is marked -- so no picture in this
topic is fixed. Every one is built the same way: the template solves the
geometry in ordinary Cartesian coordinates from its own parameters, hands the
resulting points to `Fig`, and `Fig` scales them into an SVG. Change an angle
in the stem and the drawing changes with it, because the drawing is the only
place those coordinates come from.

Two consequences worth stating, because they are what the checker relies on:

* **Everything is drawn to scale.** The source items print "Note: Figure not
  drawn to scale" and then draw a 60 degree angle as 40; here a 60 degree
  angle is 60 degrees of arc on the page. That removes a whole class of defect
  (a figure that contradicts its own labels) and it lets `option_check.py`
  take a protractor to the SVG and check the drawn angle against the answer.
* **A degenerate draw is refused, not fixed.** A triangle whose angles do not
  sum to 180, a point that would land outside the segment it is supposed to
  lie on, a figure so thin that nothing can be read off it -- the builder
  raises `ItemError` and the registry draws again.

Same contract as the shared `satbank/figures.py`: an SVG string in
`currentColor`, so a figure reads on light and dark backgrounds.
"""

from __future__ import annotations

import math

from ...item import ItemError

__all__ = ["Fig", "P", "ray", "meet", "along", "polar", "turn", "triangle_pts",
           "direction", "between", "dist"]

_CSS = (".fg{stroke:currentColor;stroke-width:1.5;fill:none}"
        ".ar{stroke:currentColor;stroke-width:1.1;fill:none}"
        ".pt{fill:currentColor}"
        ".lb{fill:currentColor;font:12px ui-sans-serif,system-ui,sans-serif}"
        ".it{fill:currentColor;font:italic 13px ui-serif,Georgia,serif}")

# how far a label sits from the thing it names, in pixels
NAME_GAP = 15.0
ARC_R = 21.0
ARC_GAP = 12.0
SQUARE = 11.0


# ----------------------------------------------------------------- geometry
# Plain Cartesian points, y upwards. Nothing here knows about SVG.

def P(x, y) -> tuple[float, float]:
    return (float(x), float(y))


def polar(o, deg, r) -> tuple[float, float]:
    a = math.radians(deg)
    return (o[0] + r * math.cos(a), o[1] + r * math.sin(a))


def ray(o, deg) -> tuple:
    """A line through `o` in direction `deg`, as the pair (point, direction)."""
    return (o, float(deg) % 360.0)


def direction(p, q) -> float:
    return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) % 360.0


def turn(a, b) -> float:
    """The anticlockwise turn from direction a to direction b, in [0, 360)."""
    return (b - a) % 360.0


def between(v, a, b) -> float:
    """The (non-reflex) angle at v between the rays to a and to b."""
    t = turn(direction(v, a), direction(v, b))
    return min(t, 360.0 - t)


def meet(r1, r2) -> tuple[float, float]:
    """Where two lines cross. Refuses a pair that is parallel or nearly so."""
    (p1, d1), (p2, d2) = r1, r2
    u = (math.cos(math.radians(d1)), math.sin(math.radians(d1)))
    v = (math.cos(math.radians(d2)), math.sin(math.radians(d2)))
    det = u[0] * (-v[1]) - (-v[0]) * u[1]
    if abs(det) < 1e-6:
        raise ItemError("two lines in this figure are parallel where they must cross")
    bx, by = p2[0] - p1[0], p2[1] - p1[1]
    t = (bx * (-v[1]) - (-v[0]) * by) / det
    return (p1[0] + t * u[0], p1[1] + t * u[1])


def along(a, b, frac) -> tuple[float, float]:
    return (a[0] + (b[0] - a[0]) * frac, a[1] + (b[1] - a[1]) * frac)


def dist(a, b) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def triangle_pts(ang_a, ang_b, base=1.0):
    """Triangle ABC with A at the origin and B at (base, 0), drawn to scale.

    `ang_a` and `ang_b` are the interior angles at A and B in degrees; C is
    wherever those two rays meet, so the drawn angles are the stated ones.
    """
    if ang_a <= 0 or ang_b <= 0 or ang_a + ang_b >= 180:
        raise ItemError(f"no triangle has angles {ang_a} and {ang_b} at two vertices")
    a, b = P(0, 0), P(base, 0)
    c = meet(ray(a, ang_a), ray(b, 180 - ang_b))
    return a, b, c


# -------------------------------------------------------------------- figure

class Fig:
    """A drawing under construction: points in math space, labels in pixels.

    Nothing is placed in the picture until `render`, which finds the bounding
    box of everything -- segments, arcs and the text as well -- and scales the
    whole drawing into it. That is what keeps a wide figure and a tall one the
    same physical size on the page.
    """

    def __init__(self, size: float = 340.0, thin: float = 0.045):
        self.size = size
        self.thin = thin            # reject a drawing flatter than this
        self.caption: str | None = None
        self.segs: list[tuple] = []
        self.arcs: list[tuple] = []
        self.squares: list[tuple] = []
        self.texts: list[tuple] = []
        self.dots: list[tuple] = []
        self.marks: list[tuple] = []

    # ------------------------------------------------------------ building

    def seg(self, p, q):
        if dist(p, q) < 1e-9:
            raise ItemError("a segment in this figure has zero length")
        self.segs.append((p, q))
        return self

    def path(self, *pts):
        for a, b in zip(pts, pts[1:]):
            self.seg(a, b)
        return self

    def dot(self, *pts):
        self.dots.extend(pts)
        return self

    def name(self, p, text, deg, gap: float = NAME_GAP, italic: bool = True):
        """Label a point, `deg` saying which way to push the text clear of it."""
        self.texts.append((p, text, float(deg), float(gap), italic))
        return self

    def angle(self, v, a, b, text=None, r: float = ARC_R, italic: bool = True):
        """Mark the angle at v between the rays to a and to b, and name it."""
        d1, d2 = direction(v, a), direction(v, b)
        if turn(d1, d2) > 180.0:
            d1, d2 = d2, d1
        span = turn(d1, d2)
        if span < 6.0:
            raise ItemError(f"a {span:.1f} degree angle is too thin to mark in a figure")
        if span < 24.0:
            r = max(r, 26.0)            # a thin wedge needs a longer arc to read
        self.arcs.append((v, d1, d2, float(r)))
        if text is not None:
            # and its label pushed far enough out that the two lines making the
            # angle pass either side of the text rather than through it
            half = max(math.sin(math.radians(span / 2.0)), 0.05)
            room = (3.7 * len(str(text)) + 4.0) / half
            gap = max(r + ARC_GAP, min(4.0 * r, room))
            self.texts.append((v, text, d1 + span / 2.0, gap, italic))
        return self

    def right(self, v, a, b):
        """A right-angle square, which is how a right angle is always shown."""
        d1, d2 = direction(v, a), direction(v, b)
        if turn(d1, d2) > 180.0:
            d1, d2 = d2, d1
        if abs(turn(d1, d2) - 90.0) > 0.5:
            raise ItemError("a right-angle square was asked for on an angle that is "
                            f"{turn(d1, d2):.1f} degrees")
        self.squares.append((v, d1, d2))
        return self

    def side(self, p, q, text, out: float = 13.0, italic: bool = False):
        """Label a segment's length, pushed clear on one side of it."""
        mid = along(p, q, 0.5)
        n = (direction(p, q) + 90.0) % 360.0
        self.texts.append((mid, text, n if out >= 0 else (n + 180) % 360,
                           abs(out), italic))
        return self

    def tick(self, p, q):
        """The single stroke that says two segments have the same length."""
        self.marks.append((along(p, q, 0.5), direction(p, q)))
        return self

    # ------------------------------------------------------------ rendering

    def _scale(self):
        xs = [c[0] for s in self.segs for c in s] + [a[0][0] for a in self.arcs] \
             + [p[0] for p in self.dots] + [t[0][0] for t in self.texts]
        ys = [c[1] for s in self.segs for c in s] + [a[0][1] for a in self.arcs] \
             + [p[1] for p in self.dots] + [t[0][1] for t in self.texts]
        if not xs:
            raise ItemError("an empty figure")
        w, h = max(xs) - min(xs), max(ys) - min(ys)
        if max(w, h) <= 0:
            raise ItemError("a figure with no extent")
        if min(w, h) < self.thin * max(w, h):
            raise ItemError("this draw makes a figure too flat to read")
        # a flat figure is stretched until its short side is legible, never
        # past the width of a column: the angles stay exact either way
        k = self.size / max(w, h)
        if min(w, h) * k < 130.0:
            k = min(130.0 / min(w, h), 700.0 / max(w, h))
        return k, min(xs), max(ys)

    def note(self, text: str = "Note: Figure not drawn to scale."):
        self.caption = text
        return self

    def render(self) -> str:
        k, x0, y1 = self._scale()

        def X(p):
            return (p[0] - x0) * k

        def Y(p):
            return (y1 - p[1]) * k

        prim, boxes = [], []

        def box(x, y, w=0.0, h=0.0):
            boxes.append((x - w / 2, y - h / 2, x + w / 2, y + h / 2))

        for p, q in self.segs:
            prim.append(("line", (X(p), Y(p), X(q), Y(q))))
            box(X(p), Y(p))
            box(X(q), Y(q))
        for v, d1, d2, r in self.arcs:
            x1, y1_ = X(v) + r * math.cos(math.radians(d1)), Y(v) - r * math.sin(math.radians(d1))
            x2, y2_ = X(v) + r * math.cos(math.radians(d2)), Y(v) - r * math.sin(math.radians(d2))
            prim.append(("arc", (x1, y1_, r, x2, y2_)))
            box(x1, y1_)
            box(x2, y2_)
        for v, d1, d2 in self.squares:
            a = (X(v) + SQUARE * math.cos(math.radians(d1)),
                 Y(v) - SQUARE * math.sin(math.radians(d1)))
            c = (X(v) + SQUARE * math.cos(math.radians(d2)),
                 Y(v) - SQUARE * math.sin(math.radians(d2)))
            b = (a[0] + c[0] - X(v), a[1] + c[1] - Y(v))
            prim.append(("sq", (a[0], a[1], b[0], b[1], c[0], c[1])))
            box(*b)
        for p in self.dots:
            prim.append(("dot", (X(p), Y(p))))
        for m, d in self.marks:
            n = math.radians(d + 90.0)
            prim.append(("line", (X(m) + 5 * math.cos(n), Y(m) - 5 * math.sin(n),
                                  X(m) - 5 * math.cos(n), Y(m) + 5 * math.sin(n))))
        for p, text, deg, gap, italic in self.texts:
            tx = X(p) + gap * math.cos(math.radians(deg))
            ty = Y(p) - gap * math.sin(math.radians(deg))
            c = math.cos(math.radians(deg))
            anchor = "start" if c > 0.35 else ("end" if c < -0.35 else "middle")
            s = math.sin(math.radians(deg))
            ty += -3.0 if s > 0.5 else (11.0 if s < -0.5 else 4.5)
            prim.append(("text", (tx, ty, anchor, text, italic)))
            wid = 7.4 * len(text)
            shift = {"start": wid / 2, "end": -wid / 2, "middle": 0.0}[anchor]
            box(tx + shift, ty - 4, wid, 15)

        pad = 4.0
        foot = 20.0 if self.caption else 0.0
        bx0 = min(b[0] for b in boxes) - pad
        by0 = min(b[1] for b in boxes) - pad
        bx1 = max(b[2] for b in boxes) + pad
        by1 = max(b[3] for b in boxes) + pad + foot
        w, h = round(bx1 - bx0, 1), round(by1 - by0, 1)

        def f(v):
            return f"{v:.1f}"

        out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
               f'xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>']
        for kind, a in prim:
            if kind == "line":
                out.append(f'<line class="fg" x1="{f(a[0] - bx0)}" y1="{f(a[1] - by0)}" '
                           f'x2="{f(a[2] - bx0)}" y2="{f(a[3] - by0)}"/>')
            elif kind == "arc":
                out.append(f'<path class="ar" d="M{f(a[0] - bx0)},{f(a[1] - by0)} '
                           f'A{f(a[2])},{f(a[2])} 0 0 0 '
                           f'{f(a[3] - bx0)},{f(a[4] - by0)}"/>')
            elif kind == "sq":
                out.append(f'<path class="ar" d="M{f(a[0] - bx0)},{f(a[1] - by0)} '
                           f'L{f(a[2] - bx0)},{f(a[3] - by0)} '
                           f'L{f(a[4] - bx0)},{f(a[5] - by0)}"/>')
            elif kind == "dot":
                out.append(f'<circle class="pt" cx="{f(a[0] - bx0)}" '
                           f'cy="{f(a[1] - by0)}" r="2.8"/>')
            else:
                tx, ty, anchor, text, italic = a
                cls = "it" if italic else "lb"
                out.append(f'<text class="{cls}" x="{f(tx - bx0)}" y="{f(ty - by0)}" '
                           f'text-anchor="{anchor}">{_esc(text)}</text>')
        if self.caption:
            out.append(f'<text class="lb" x="{f((bx1 - bx0) / 2)}" '
                       f'y="{f(by1 - by0 - 6)}" text-anchor="middle">'
                       f'{_esc(self.caption)}</text>')
        out.append("</svg>")
        return "".join(out)


def _esc(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
