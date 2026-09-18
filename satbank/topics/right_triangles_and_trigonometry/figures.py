"""Generated right-triangle figures.

The figure carries the question in this topic, so every coordinate here comes
from the same numbers as the stem: the triangle is drawn *to scale* from its
two legs, the right-angle square sits on the vertex that actually has the
right angle, and each label is placed against the side or vertex it belongs
to. A reader with a ruler and a protractor can recover all of that from the
pixels, and `option_check.py` does exactly that -- which is the only way a
picture that has drifted from its answer can be caught.

`satbank/figures.py` draws grids, prisms and one fixed scalene triangle, none
of which can be driven by a pair of leg lengths, so the primitives are written
here. Same contract as the shared module: an SVG string in `currentColor`.

Three vertex roles run through every function:

    rt   the right angle
    p    the far end of the first leg
    q    the far end of the second leg

so `sides={"p": "3"}` labels the leg from `rt` to `p`, `angles={"p": "x°"}`
labels the angle at `p`, and `names={"rt": "C"}` writes C beside that vertex.
"""

from __future__ import annotations

import math

__all__ = ["right_triangle", "cut_right_triangle", "altitude_triangle",
           "trapezoid_logo"]

CSS = (".ax{stroke:currentColor;stroke-width:1.7;fill:none}"
       ".sg{stroke:currentColor;stroke-width:1.2;fill:none}"
       ".sh{fill:currentColor;opacity:.22;stroke:none}"
       ".lb{fill:currentColor;font:13px ui-serif,Georgia,serif}"
       ".an{fill:currentColor;font:11px ui-sans-serif,system-ui,sans-serif}"
       ".vx{fill:currentColor;font:italic 12px ui-serif,Georgia,serif}"
       ".nt{fill:currentColor;font:12px ui-serif,Georgia,serif}")

NOTE = "Note: Figure not drawn to scale."
PAD = 38
SQ = 11.0          # the side of the right-angle square, in pixels


def _r(v: float) -> float:
    return round(float(v), 2)


def _len(a, b) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _mid(a, b) -> tuple[float, float]:
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def _unit(a, b) -> tuple[float, float]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy)
    if d < 1e-9:
        raise ValueError("a degenerate side")
    return dx / d, dy / d


def _text(cls: str, x: float, y: float, s: str, dx: float, dy: float,
          clear: bool = True, centre: bool = False) -> str:
    """One label, anchored so that it sits clear of the line it names.

    `clear=False` only centres the text on its baseline. An angle label is
    already inside the corner it names, and pushing it a further ten pixels
    would carry it past the corner on a small triangle -- which is how a
    reader ends up attributing the angle to the wrong vertex.
    """
    anchor = "middle" if (centre or abs(dx) < 4) else ("start" if dx > 0 else "end")
    if not clear:
        ty = y + dy + 4.0
    else:
        ty = y + dy + (4.0 if abs(dy) < 4 else (10.0 if dy > 0 else -2.0))
    return (f'<text class="{cls}" x="{_r(x + dx)}" y="{_r(ty)}" '
            f'text-anchor="{anchor}">{s}</text>')


def _right_angle_mark(rt, a, b) -> str:
    """The square on the vertex `rt`, opening toward `a` and `b`.

    Drawn as M p1 L p2 L p3, so the vertex it marks is p1 + p3 - p2 and can be
    recovered from the path alone.
    """
    u, w = _unit(rt, a), _unit(rt, b)
    p1 = (rt[0] + SQ * u[0], rt[1] + SQ * u[1])
    p3 = (rt[0] + SQ * w[0], rt[1] + SQ * w[1])
    p2 = (p1[0] + SQ * w[0], p1[1] + SQ * w[1])
    return (f'<path class="sg" d="M{_r(p1[0])},{_r(p1[1])} L{_r(p2[0])},{_r(p2[1])} '
            f'L{_r(p3[0])},{_r(p3[1])}"/>')


def _side_anchor(a, b, away, gap: float = 13.0) -> tuple[float, float]:
    """Where a label for the side a–b is written: its middle, pushed outward."""
    mx, my = _mid(a, b)
    ox, oy = mx - away[0], my - away[1]
    d = math.hypot(ox, oy) or 1.0
    return (mx + gap * ox / d, my + gap * oy / d)


def _side_label(cls, a, b, away, text: str, gap: float = 13.0) -> str:
    """A label at the midpoint of a–b, pushed away from the third vertex."""
    mx, my = _mid(a, b)
    ox, oy = mx - away[0], my - away[1]
    d = math.hypot(ox, oy) or 1.0
    return _text(cls, mx, my, text, gap * ox / d, gap * oy / d)


def _name_anchor(vertex, centre, gap: float = 14.0) -> tuple[float, float]:
    """Where the letter naming a vertex is written."""
    ox, oy = vertex[0] - centre[0], vertex[1] - centre[1]
    d = math.hypot(ox, oy) or 1.0
    return (vertex[0] + gap * ox / d, vertex[1] + gap * oy / d)


def _readable(spans: dict, written: dict, names: dict = None, spots: dict = None,
              margin: float = 1.35, apart: float = 17.0) -> None:
    """Every written label has to be attributable, and clear of every other.

    A number printed beside a line names that line, so two segments whose
    middles are almost on top of each other make a figure nobody -- reader or
    checker -- can attribute; and a letter naming a vertex must not land on top
    of a length. The registry simply redraws.
    """
    mids = {k: _mid(v[0], v[1]) for k, v in spans.items()}
    placed = {}
    for key, text in (written or {}).items():
        if not text or key not in spans:
            continue
        spot = _side_anchor(*spans[key])
        own = _len(spot, mids[key])
        for other, m in mids.items():
            if other != key and _len(spot, m) < margin * own:
                raise ValueError(f"the label on {key} would sit as close to {other}")
        placed[key] = spot
    for key, text in (names or {}).items():
        if text and key in (spots or {}):
            placed[f"the name {text}"] = spots[key]
    keys = list(placed)
    for i, one in enumerate(keys):
        for other in keys[i + 1:]:
            if _len(placed[one], placed[other]) < apart:
                raise ValueError(f"{one} and {other} would be printed on top of "
                                 f"each other")


def _angle_label(vertex, a, b, text: str, gap: float = 34.0) -> str:
    """A label inside the angle at `vertex`, on the bisector of the two sides.

    The offset shrinks with the shorter of the two sides meeting there, so on a
    long thin triangle the label still sits nearer its own corner than any
    other -- which is what lets a reader tell whose angle it is.
    """
    u, w = _unit(vertex, a), _unit(vertex, b)
    gap = min(gap, 0.30 * min(_len(vertex, a), _len(vertex, b)))
    bx, by = u[0] + w[0], u[1] + w[1]
    d = math.hypot(bx, by) or 1.0
    return _text("an", vertex[0], vertex[1], text, gap * bx / d, gap * by / d,
                 clear=False, centre=True)


def _vertex_name(vertex, centre, text: str, gap: float = 14.0) -> str:
    ox, oy = vertex[0] - centre[0], vertex[1] - centre[1]
    d = math.hypot(ox, oy) or 1.0
    return _text("vx", vertex[0], vertex[1], text, gap * ox / d, gap * oy / d)


NOTE_WIDTH = 210.0        # room for "Note: Figure not drawn to scale." at 12px


def _frame(pts, note: bool, extra_pad: float = 0.0):
    """Shift a set of points into a padded viewBox and return (w, h, move).

    A figure narrower than its own caption would print the caption clipped, so
    a noted figure is widened and the drawing centred in it.
    """
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    pad = PAD + extra_pad
    w = max(xs) - min(xs) + 2 * pad
    h = max(ys) - min(ys) + 2 * pad + (22 if note else 0)
    ox, oy = pad - min(xs), pad - min(ys)
    if note and w < NOTE_WIDTH:
        ox += (NOTE_WIDTH - w) / 2
        w = NOTE_WIDTH
    return w, h, (lambda p: (p[0] + ox, p[1] + oy))


def _open(w, h) -> str:
    return (f'<svg viewBox="0 0 {_r(w)} {_r(h)}" width="{_r(w)}" height="{_r(h)}" '
            f'role="img" xmlns="http://www.w3.org/2000/svg"><style>{CSS}</style>')


def _note(w, h) -> str:
    return f'<text class="nt" x="{_r(w / 2)}" y="{_r(h - 7)}" text-anchor="middle">{NOTE}</text>'


# ------------------------------------------------------------ the right triangle

def _places(leg_p: float, leg_q: float, layout: str, size: float,
            marked: bool = False):
    """Pixel positions of rt, p and q, drawn to scale from the two legs."""
    a, b = float(leg_p), float(leg_q)
    if a <= 0 or b <= 0:
        raise ValueError("a leg of a triangle is positive")
    if marked and not 1 / 6 <= a / b <= 6:
        raise ValueError("an angle marked in so thin a corner cannot be read")
    k = size / max(a, b)
    a, b = a * k, b * k
    if layout == "left":                       # right angle at the lower left
        return (0.0, a), (0.0, 0.0), (b, a)
    if layout == "right":                      # right angle at the lower right
        return (b, a), (b, 0.0), (0.0, a)
    if layout == "apex":                       # right angle at the top vertex
        c = math.hypot(a, b)
        return (a * a / c, 0.0), (0.0, a * b / c), (c, a * b / c)
    raise ValueError(f"unknown layout {layout!r}")


def right_triangle(leg_p, leg_q, *, layout="left", names=None, sides=None,
                   angles=None, note=False, size=190.0) -> str:
    """A right triangle drawn to scale from its two legs.

    `leg_p` runs from the right angle to the vertex `p`, `leg_q` from the right
    angle to `q`, and the hypotenuse joins `p` to `q`. Nothing is fixed: change
    a leg and the picture changes with it.
    """
    rt, p, q = _places(leg_p, leg_q, layout, size, marked=bool(angles))
    w, h, mv = _frame([rt, p, q], note)
    rt, p, q = mv(rt), mv(p), mv(q)
    centre = ((rt[0] + p[0] + q[0]) / 3, (rt[1] + p[1] + q[1]) / 3)
    out = [_open(w, h),
           f'<path class="ax" d="M{_r(rt[0])},{_r(rt[1])} L{_r(p[0])},{_r(p[1])} '
           f'L{_r(q[0])},{_r(q[1])} Z"/>',
           _right_angle_mark(rt, p, q)]
    spans = {"p": (rt, p, q), "q": (rt, q, p), "hyp": (p, q, rt)}
    _readable(spans, sides, names,
              {"rt": _name_anchor(rt, centre), "p": _name_anchor(p, centre),
               "q": _name_anchor(q, centre)})
    for key, (a, b, away) in spans.items():
        text = (sides or {}).get(key)
        if text:
            out.append(_side_label("lb", a, b, away, text))
    for key, (vertex, a, b) in {"p": (p, rt, q), "q": (q, rt, p)}.items():
        text = (angles or {}).get(key)
        if text:
            out.append(_angle_label(vertex, a, b, text))
    for key, vertex in {"rt": rt, "p": p, "q": q}.items():
        text = (names or {}).get(key)
        if text:
            out.append(_vertex_name(vertex, centre, text))
    if note:
        out.append(_note(w, h))
    return "".join(out) + "</svg>"


# ------------------------------------- a right triangle cut by a parallel line

def cut_right_triangle(leg_p, leg_q, cut_at, *, parallel="q", layout="left",
                       names=None, sides=None, angles=None, note=False,
                       size=190.0) -> str:
    """A right triangle with a segment parallel to one leg cutting across it.

    The cut is drawn at `cut_at` along the leg it is perpendicular to, measured
    from the right angle, and runs to the hypotenuse -- so it makes a second
    right triangle similar to the first. `parallel="q"` draws it parallel to
    the leg rt-q (and so perpendicular to rt-p); `parallel="p"` the other way.

    The two new points are `foot` (on the leg) and `edge` (on the hypotenuse).
    """
    a, b = float(leg_p), float(leg_q)
    t = float(cut_at)
    along = a if parallel == "q" else b
    if not 0 < t < along:
        raise ValueError("the cut misses the triangle")
    rt, p, q = _places(a, b, layout, size)

    def lerp(u, v, s):
        return (u[0] + (v[0] - u[0]) * s, u[1] + (v[1] - u[1]) * s)

    if parallel == "q":
        s = t / a                                  # fraction of rt->p
        foot, edge = lerp(rt, p, s), lerp(p, q, 1.0 - s)
    else:
        s = t / b
        foot, edge = lerp(rt, q, s), lerp(q, p, 1.0 - s)
    w, h, mv = _frame([rt, p, q], note)
    rt, p, q, foot, edge = (mv(rt), mv(p), mv(q), mv(foot), mv(edge))
    centre = ((rt[0] + p[0] + q[0]) / 3, (rt[1] + p[1] + q[1]) / 3)
    out = [_open(w, h),
           f'<path class="ax" d="M{_r(rt[0])},{_r(rt[1])} L{_r(p[0])},{_r(p[1])} '
           f'L{_r(q[0])},{_r(q[1])} Z"/>',
           f'<line class="ax" x1="{_r(foot[0])}" y1="{_r(foot[1])}" '
           f'x2="{_r(edge[0])}" y2="{_r(edge[1])}"/>',
           _right_angle_mark(rt, p, q),
           _right_angle_mark(foot, p if parallel == "q" else q, edge)]
    near = p if parallel == "q" else q          # the leg the cut crosses
    far = q if parallel == "q" else p
    spans = {"p": (rt, p, q), "q": (rt, q, p), "hyp": (p, q, rt),
             "cut": (foot, edge, near), "stub": (rt, foot, edge),
             "upper": (foot, near, edge),
             "lower": (near, edge, rt), "top": (edge, far, rt)}
    _readable(spans, sides, names,
              {"rt": _name_anchor(rt, centre), "p": _name_anchor(p, centre),
               "q": _name_anchor(q, centre),
               "foot": _name_anchor(foot, centre), "edge": _name_anchor(edge, centre)})
    for key, (u, v, away) in spans.items():
        text = (sides or {}).get(key)
        if text:
            out.append(_side_label("lb", u, v, away, text))
    for key, (vertex, u, v) in {"p": (p, rt, q), "q": (q, rt, p)}.items():
        text = (angles or {}).get(key)
        if text:
            out.append(_angle_label(vertex, u, v, text))
    spots = {"rt": rt, "p": p, "q": q, "foot": foot, "edge": edge}
    for key, vertex in spots.items():
        text = (names or {}).get(key)
        if text:
            out.append(_vertex_name(vertex, centre, text))
    if note:
        out.append(_note(w, h))
    return "".join(out) + "</svg>"


# ------------------------------------------ a triangle split by its altitude

def altitude_triangle(left, right, height, *, names=None, sides=None,
                      angles=None, note=False, size=200.0) -> str:
    """A triangle with the altitude to its base drawn in.

    `left` and `right` are the two pieces the foot cuts the base into and
    `height` is the altitude, so the apex sits over the foot and the right
    angle is marked there. The vertex roles are `a` (left end of the base),
    `c` (right end), `b` (the apex) and `d` (the foot).
    """
    l, r, ht = float(left), float(right), float(height)
    if l <= 0 or r <= 0 or ht <= 0:
        raise ValueError("a degenerate altitude")
    k = size / max(l + r, ht)
    a = (0.0, ht * k)
    c = ((l + r) * k, ht * k)
    d = (l * k, ht * k)
    b = (l * k, 0.0)
    w, h, mv = _frame([a, b, c], note)
    a, b, c, d = mv(a), mv(b), mv(c), mv(d)
    centre = ((a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3)
    out = [_open(w, h),
           f'<path class="ax" d="M{_r(a[0])},{_r(a[1])} L{_r(b[0])},{_r(b[1])} '
           f'L{_r(c[0])},{_r(c[1])} Z"/>',
           f'<line class="ax" x1="{_r(b[0])}" y1="{_r(b[1])}" '
           f'x2="{_r(d[0])}" y2="{_r(d[1])}"/>',
           _right_angle_mark(d, b, c)]
    spans = {"ab": (a, b, c), "bc": (b, c, a), "ad": (a, d, b),
             "dc": (d, c, b), "bd": (b, d, a), "ac": (a, c, b)}
    _readable(spans, sides, names,
              {"a": _name_anchor(a, centre), "b": _name_anchor(b, centre),
               "c": _name_anchor(c, centre), "d": _name_anchor(d, centre)})
    for key, (u, v, away) in spans.items():
        text = (sides or {}).get(key)
        if text:
            out.append(_side_label("lb", u, v, away, text))
    corners = {"a": (a, b, c), "c": (c, b, a), "abd": (b, a, d), "dbc": (b, d, c)}
    for key, (vertex, u, v) in corners.items():
        text = (angles or {}).get(key)
        if text:
            out.append(_angle_label(vertex, u, v, text, gap=28.0))
    for key, vertex in {"a": a, "b": b, "c": c, "d": d}.items():
        text = (names or {}).get(key)
        if text:
            out.append(_vertex_name(vertex, centre, text))
    if note:
        out.append(_note(w, h))
    return "".join(out) + "</svg>"


# ------------------------------------------------- equilateral triangles in a row

def trapezoid_logo(count: int, *, side=86.0, shade="up") -> str:
    """`count` congruent equilateral triangles alternating up and down.

    An odd count makes a trapezoid: the ones pointing up shade one region, the
    ones pointing down the other, and the outline is the trapezoid itself.
    """
    if count < 3 or count % 2 == 0:
        raise ValueError("the row makes a trapezoid only for an odd count of 3 or more")
    s = float(side)
    ht = s * math.sqrt(3) / 2
    ups, downs = [], []
    for i in range(count):
        x = i * s / 2
        if i % 2 == 0:
            ups.append([(x, ht), (x + s, ht), (x + s / 2, 0.0)])
        else:
            downs.append([(x, ht), (x + s, ht), (x + s / 2, 0.0)])
    # a downward triangle sits with its point on the base line, so flip those
    downs = [[(px, ht - py) for px, py in tri] for tri in downs]
    pts = [pt for tri in ups + downs for pt in tri]
    w, h, mv = _frame(pts, False, extra_pad=-14)
    out = [_open(w, h)]
    for tri in (ups if shade == "up" else downs):
        d = " ".join(f"{'M' if i == 0 else 'L'}{_r(mv(pt)[0])},{_r(mv(pt)[1])}"
                     for i, pt in enumerate(tri))
        out.append(f'<path class="sh" d="{d} Z"/>')
    for tri in ups + downs:
        d = " ".join(f"{'M' if i == 0 else 'L'}{_r(mv(pt)[0])},{_r(mv(pt)[1])}"
                     for i, pt in enumerate(tri))
        out.append(f'<path class="ax" d="{d} Z"/>')
    return "".join(out) + "</svg>"
