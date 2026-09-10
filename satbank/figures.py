"""Generated SVG figures.

Figures are part of the item, so they have to be generated from the same
parameters as the stem -- a fixed picture with swapped numbers is how a
generated set gets caught. Everything is drawn with `currentColor` so a figure
reads correctly on light and dark backgrounds.
"""

from __future__ import annotations

__all__ = ["coordinate_grid", "cylinder_rh", "prism_lwh", "triangle_xyz"]

_CSS = (".ax{stroke:currentColor;stroke-width:1.4;fill:none}"
        ".gr{stroke:currentColor;stroke-width:.5;opacity:.28}"
        ".pt{fill:currentColor}"
        ".sg{stroke:currentColor;stroke-width:2.2;fill:none}"
        ".lb{fill:currentColor;font:11px ui-sans-serif,system-ui,sans-serif}"
        ".it{fill:currentColor;font:italic 13px ui-serif,Georgia,serif}")


def coordinate_grid(xmin, xmax, ymin, ymax, points=(), segments=(),
                    step=2, px=26, pad=26) -> str:
    """An xy-plane with a unit grid, labelled axes and plotted points."""
    w, h = (xmax - xmin) * px + 2 * pad, (ymax - ymin) * px + 2 * pad

    def X(x): return pad + (x - xmin) * px
    def Y(y): return h - pad - (y - ymin) * px

    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
           f'xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>']
    for x in range(xmin, xmax + 1):
        out.append(f'<line class="gr" x1="{X(x)}" y1="{Y(ymin)}" x2="{X(x)}" y2="{Y(ymax)}"/>')
    for y in range(ymin, ymax + 1):
        out.append(f'<line class="gr" x1="{X(xmin)}" y1="{Y(y)}" x2="{X(xmax)}" y2="{Y(y)}"/>')
    out.append(f'<line class="ax" x1="{X(xmin)}" y1="{Y(0)}" x2="{X(xmax) + 12}" y2="{Y(0)}"/>')
    out.append(f'<line class="ax" x1="{X(0)}" y1="{Y(ymin)}" x2="{X(0)}" y2="{Y(ymax) - 12}"/>')
    out.append(f'<path class="pt" d="M{X(xmax)+12},{Y(0)} l-6,-3.5 v7 z"/>')
    out.append(f'<path class="pt" d="M{X(0)},{Y(ymax)-12} l-3.5,6 h7 z"/>')
    out.append(f'<text class="it" x="{X(xmax)+8}" y="{Y(0)+18}">x</text>')
    out.append(f'<text class="it" x="{X(0)-14}" y="{Y(ymax)-10}">y</text>')
    for x in range(xmin, xmax + 1):
        if x and x % step == 0:
            out.append(f'<text class="lb" x="{X(x)}" y="{Y(0)+15}" text-anchor="middle">{x}</text>')
    for y in range(ymin, ymax + 1):
        if y and y % step == 0:
            out.append(f'<text class="lb" x="{X(0)-7}" y="{Y(y)+4}" text-anchor="end">{y}</text>')
    out.append(f'<text class="it" x="{X(0)-11}" y="{Y(0)+15}">O</text>')
    for (x1, y1), (x2, y2) in segments:
        out.append(f'<line class="sg" x1="{X(x1)}" y1="{Y(y1)}" x2="{X(x2)}" y2="{Y(y2)}"/>')
        for px_, py_ in ((x1, y1), (x2, y2)):
            out.append(f'<circle class="pt" cx="{X(px_)}" cy="{Y(py_)}" r="4"/>')
    for x, y in points:
        out.append(f'<circle class="pt" cx="{X(x)}" cy="{Y(y)}" r="4.5"/>')
    out.append("</svg>")
    return "".join(out)


def cylinder_rh(r_label="r", h_label="h") -> str:
    """A right circular cylinder with its radius and height marked."""
    return (
        '<svg viewBox="0 0 190 170" width="190" height="170" role="img" '
        f'xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>'
        '<ellipse class="ax" cx="80" cy="38" rx="58" ry="19"/>'
        '<path class="ax" d="M22,38 V118 A58,19 0 0 0 138,118 V38"/>'
        '<line class="ax" x1="80" y1="38" x2="132" y2="30" stroke-dasharray="0"/>'
        '<circle class="pt" cx="80" cy="38" r="3"/>'
        f'<text class="it" x="108" y="26">{r_label}</text>'
        '<line class="ax" x1="152" y1="38" x2="152" y2="118"/>'
        '<path class="pt" d="M152,38 l-3.5,7 h7 z"/><path class="pt" d="M152,118 l-3.5,-7 h7 z"/>'
        f'<text class="it" x="160" y="82">{h_label}</text></svg>')


def prism_lwh(l_label, w_label, h_label) -> str:
    """A right rectangular prism in the source's flat isometric style."""
    return (
        '<svg viewBox="0 0 210 150" width="210" height="150" role="img" '
        f'xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>'
        '<path class="ax" d="M20,50 H130 V115 H20 Z"/>'
        '<path class="ax" d="M20,50 L58,22 H168 L130,50"/>'
        '<path class="ax" d="M130,115 L168,87 V22"/>'
        f'<text class="lb" x="75" y="130" text-anchor="middle">{l_label}</text>'
        f'<text class="lb" x="152" y="112">{w_label}</text>'
        f'<text class="lb" x="174" y="58">{h_label}</text></svg>')


def triangle_xyz(a="x", b="y", c="z") -> str:
    """A scalene triangle with its three sides labelled, as in the source set."""
    return (
        '<svg viewBox="0 0 170 150" width="170" height="150" role="img" '
        f'xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>'
        '<path class="ax" d="M108,18 L128,132 L38,74 Z"/>'
        f'<text class="it" x="66" y="40">{a}</text>'
        f'<text class="it" x="126" y="76">{b}</text>'
        f'<text class="it" x="62" y="116">{c}</text></svg>')


def two_rectangles(big_side, small_side, small_base,
                   big_names=("B", "C", "A", "D"), small_names=("R", "S", "Q", "T")) -> str:
    """Two similar rectangles side by side, as the source draws them."""
    bn, sn = big_names, small_names
    return (
        '<svg viewBox="0 0 330 130" width="330" height="130" role="img" '
        f'xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>'
        '<rect class="ax" x="42" y="24" width="112" height="72"/>'
        f'<text class="it" x="36" y="20" text-anchor="end">{bn[0]}</text>'
        f'<text class="it" x="160" y="20">{bn[1]}</text>'
        f'<text class="it" x="36" y="112">{bn[2]}</text>'
        f'<text class="it" x="160" y="112">{bn[3]}</text>'
        f'<text class="lb" x="38" y="64" text-anchor="end">{big_side}</text>'
        '<rect class="ax" x="216" y="52" width="80" height="44"/>'
        f'<text class="it" x="210" y="48" text-anchor="end">{sn[0]}</text>'
        f'<text class="it" x="302" y="48">{sn[1]}</text>'
        f'<text class="it" x="210" y="112">{sn[2]}</text>'
        f'<text class="it" x="302" y="112">{sn[3]}</text>'
        f'<text class="lb" x="212" y="78" text-anchor="end">{small_side}</text>'
        f'<text class="lb" x="256" y="112" text-anchor="middle">{small_base}</text></svg>')
