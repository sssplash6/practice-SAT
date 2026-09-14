"""Generated circle figures.

`satbank/figures.py` draws grids, prisms and similar rectangles but nothing
round, so the two primitives a circles topic needs are written here: a circle
with labelled points on it, and an xy-plane with a circle drawn on it. Same
contract as the shared module -- an SVG string in `currentColor`, every
coordinate derived from the same parameters as the stem, so a redrawn item
cannot keep a stale picture.
"""

from __future__ import annotations

import math

__all__ = ["circle_with_points", "circle_on_grid"]

_CSS = (".ax{stroke:currentColor;stroke-width:1.4;fill:none}"
        ".gr{stroke:currentColor;stroke-width:.5;opacity:.28}"
        ".pt{fill:currentColor}"
        ".sg{stroke:currentColor;stroke-width:1.4;fill:none}"
        ".lb{fill:currentColor;font:11px ui-sans-serif,system-ui,sans-serif}"
        ".it{fill:currentColor;font:italic 13px ui-serif,Georgia,serif}")


def _xy(cx, cy, r, deg):
    a = math.radians(deg)
    return round(cx + r * math.cos(a), 2), round(cy - r * math.sin(a), 2)


def _anchor(deg) -> tuple[str, float]:
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    anchor = "start" if c > 0.3 else ("end" if c < -0.3 else "middle")
    dy = -3.0 if s > 0.5 else (12.0 if s < -0.5 else 4.0)
    return anchor, dy


def circle_with_points(points, *, center="O", radii=(), chords=(), diameters=(),
                       angle=None, angle_label=None, R=76, pad=32) -> str:
    """A circle with named points on it, drawn from their angular positions.

    `points` maps a label to its position in degrees, measured the way the
    xy-plane measures it. `radii` and `chords` name the segments to draw,
    `diameters` the labels whose radius continues through the center, and
    `angle` a pair of labels whose central angle is marked -- with a square
    when it is a right angle and with `angle_label` otherwise.
    """
    longest = max((len(str(lab)) for lab in points), default=1)
    padx = max(pad, 12 + 7 * longest)          # room for a label like "T (-1, 0)"
    w, h = 2 * (R + padx), 2 * (R + pad)
    cx, cy = padx + R, pad + R
    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
           f'xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>',
           f'<circle class="ax" cx="{cx}" cy="{cy}" r="{R}"/>']
    for a, b in chords:
        x1, y1 = _xy(cx, cy, R, points[a])
        x2, y2 = _xy(cx, cy, R, points[b])
        out.append(f'<line class="sg" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    for lab in radii:
        x, y = _xy(cx, cy, R, points[lab])
        out.append(f'<line class="sg" x1="{cx}" y1="{cy}" x2="{x}" y2="{y}"/>')
    for lab in diameters:
        x1, y1 = _xy(cx, cy, R, points[lab])
        x2, y2 = _xy(cx, cy, R, points[lab] + 180)
        out.append(f'<line class="sg" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    if angle:
        a1, a2 = points[angle[0]], points[angle[1]]
        span = (a2 - a1) % 360
        if abs(span - 90) < 1e-9:
            # a right angle is marked with a square, never with a number
            u1, u2 = math.radians(a1), math.radians(a2)
            s = 13
            p0 = (cx + s * math.cos(u1), cy - s * math.sin(u1))
            p2 = (cx + s * math.cos(u2), cy - s * math.sin(u2))
            p1 = (p0[0] + p2[0] - cx, p0[1] + p2[1] - cy)
            out.append(f'<path class="sg" d="M{p0[0]:.1f},{p0[1]:.1f} L{p1[0]:.1f},{p1[1]:.1f} '
                       f'L{p2[0]:.1f},{p2[1]:.1f}"/>')
        else:
            rr = 23
            x1, y1 = _xy(cx, cy, rr, a1)
            x2, y2 = _xy(cx, cy, rr, a2)
            big = 1 if span > 180 else 0
            out.append(f'<path class="sg" d="M{x1},{y1} A{rr},{rr} 0 {big} 0 {x2},{y2}"/>')
        if angle_label:
            lx, ly = _xy(cx, cy, 38, a1 + span / 2)
            out.append(f'<text class="it" x="{lx}" y="{ly + 4}" text-anchor="middle">'
                       f'{angle_label}</text>')
    if center:
        out.append(f'<circle class="pt" cx="{cx}" cy="{cy}" r="2.6"/>')
        if angle:
            # keep the label clear of the arc or square marking the angle
            a1, a2 = points[angle[0]], points[angle[1]]
            lx, ly = _xy(cx, cy, 17, a1 + ((a2 - a1) % 360) / 2 + 180)
            out.append(f'<text class="it" x="{lx}" y="{ly + 4}" '
                       f'text-anchor="middle">{center}</text>')
        else:
            out.append(f'<text class="it" x="{cx - 6}" y="{cy + 15}" '
                       f'text-anchor="end">{center}</text>')
    for lab, deg in points.items():
        x, y = _xy(cx, cy, R, deg)
        out.append(f'<circle class="pt" cx="{x}" cy="{y}" r="3.4"/>')
        anchor, dy = _anchor(deg)
        lx, ly = _xy(cx, cy, R + 9, deg)
        out.append(f'<text class="it" x="{lx}" y="{ly + dy}" text-anchor="{anchor}">{lab}</text>')
    out.append("</svg>")
    return "".join(out)


def circle_on_grid(xmin, xmax, ymin, ymax, cx, cy, r, *, step=2, pad=26,
                   label=None) -> str:
    """An xy-plane with one circle on it, in the style of the shared grid."""
    span = max(xmax - xmin, ymax - ymin, 1)
    px = max(11, min(24, 380 // span))
    w, h = (xmax - xmin) * px + 2 * pad, (ymax - ymin) * px + 2 * pad

    def X(x): return round(pad + (x - xmin) * px, 2)
    def Y(y): return round(h - pad - (y - ymin) * px, 2)

    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
           f'xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>']
    for x in range(xmin, xmax + 1):
        out.append(f'<line class="gr" x1="{X(x)}" y1="{Y(ymin)}" x2="{X(x)}" y2="{Y(ymax)}"/>')
    for y in range(ymin, ymax + 1):
        out.append(f'<line class="gr" x1="{X(xmin)}" y1="{Y(y)}" x2="{X(xmax)}" y2="{Y(y)}"/>')
    out.append(f'<line class="ax" x1="{X(xmin)}" y1="{Y(0)}" x2="{X(xmax) + 12}" y2="{Y(0)}"/>')
    out.append(f'<line class="ax" x1="{X(0)}" y1="{Y(ymin)}" x2="{X(0)}" y2="{Y(ymax) - 12}"/>')
    out.append(f'<text class="it" x="{X(xmax) + 8}" y="{Y(0) + 18}">x</text>')
    out.append(f'<text class="it" x="{X(0) - 14}" y="{Y(ymax) - 10}">y</text>')
    for x in range(xmin, xmax + 1):
        if x and x % step == 0:
            out.append(f'<text class="lb" x="{X(x)}" y="{Y(0) + 15}" text-anchor="middle">{x}</text>')
    for y in range(ymin, ymax + 1):
        if y and y % step == 0:
            out.append(f'<text class="lb" x="{X(0) - 7}" y="{Y(y) + 4}" text-anchor="end">{y}</text>')
    out.append(f'<text class="it" x="{X(0) - 11}" y="{Y(0) + 15}">O</text>')
    out.append(f'<circle class="ax" cx="{X(cx)}" cy="{Y(cy)}" r="{round(r * px, 2)}" '
               f'stroke-width="2"/>')
    if label:
        out.append(f'<text class="it" x="{X(cx)}" y="{Y(cy) + 4}" text-anchor="middle">{label}</text>')
    out.append("</svg>")
    return "".join(out)
