"""Figures for Reading and Writing's Command of Evidence items: a `figure`
dict (kind, title, x_axis, y_axis, data) to an SVG string, drawn in
currentColor the way every other chart in the bank is drawn (`plot.py`).

Draws exactly the data it is given and nothing else: no tick, no legend
entry, no series the figure dict did not state. A second series (a grouped
bar, a second line) is told apart from the first without color -- a hatch
fill for a bar, a dash pattern and marker shape for a line -- since
currentColor charts carry no hue of their own.

Self-check: python3 -m satbank.rw_figures
"""

from __future__ import annotations

from .plot import _Frame, _nice, _ticks

__all__ = ["render"]

_DASH = ["", "6,4", "1.6,3.2", "7,3,1.5,3"]          # solid, dashed, dotted, dash-dot
_MARK = ["circle", "square", "triangle", "diamond"]  # CB's own per-series shapes, in order
_HATCH = ('<defs><pattern id="rwhatch" width="6" height="6" patternUnits="userSpaceOnUse" '
          'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" '
          'stroke="currentColor" stroke-width="2"/></pattern></defs>')


def _marker(shape: str, x: float, y: float, r: float = 3.2) -> str:
    if shape == "square":
        s = r * 1.7
        return (f'<rect class="pt" x="{x - s / 2:.2f}" y="{y - s / 2:.2f}" '
                f'width="{s:.2f}" height="{s:.2f}"/>')
    if shape == "triangle":
        s = r * 1.9
        return (f'<polygon class="pt" points="{x:.2f},{y - s:.2f} '
                f'{x - s:.2f},{y + s * 0.75:.2f} {x + s:.2f},{y + s * 0.75:.2f}"/>')
    if shape == "diamond":
        s = r * 1.5
        return (f'<polygon class="pt" points="{x:.2f},{y - s:.2f} {x + s:.2f},{y:.2f} '
                f'{x:.2f},{y + s:.2f} {x - s:.2f},{y:.2f}"/>')
    return f'<circle class="pt" cx="{x:.2f}" cy="{y:.2f}" r="{r}"/>'


_CH = 6.6   # px per character of the 12px semibold title font (a safe average for wrapping)


def _wrap(text: str, width: int) -> list[str]:
    """Greedy word wrap to at most `width` characters a line."""
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur] if cur else lines


def _layout(fig: dict, n: int, yticks=(), w: int = 440, h: int = 260, pad_b: int = 40) -> dict:
    """Room for the title and the y-axis label: a long title wraps under itself and a long
    y label wraps into a second rotated line, the chart growing taller rather than letting
    the label run up into the title (19 of the bank's 46 y labels are longer than the plot)."""
    title = _wrap(fig.get("title", ""), int((w - 16) / _CH))
    extra = 14 * max(0, len(title) - 1)
    pad_t = (42 if n > 1 else (30 if title else 16)) + extra
    ylabel = fig.get("y_axis", "")
    ylines = []
    if ylabel:
        while True:
            ylines = _wrap(ylabel, max(8, int((h - pad_t - pad_b - 8) / _CH)))
            if len(ylines) <= 2:
                break
            h += 20
    # the y label's lines (14px apart from x=12), then the widest tick number (11px font), clear of each other
    tick_w = max((len(_nice(t)) for t in yticks), default=2) * 6.4
    pad_l = max(46, round(14 * len(ylines) + 6 + tick_w + 7))
    return {"title": title, "legend_y": 30 + extra, "pad_t": pad_t, "h": h, "pad_l": pad_l, "ylines": ylines}


def _labels(f, lay: dict, xlabel: str) -> None:
    """The x label under the axis, the wrapped y label beside it, the wrapped title on top."""
    f.axes(xlabel, "")
    cy = (f.t + f.h - f.b) / 2
    for i, line in enumerate(lay["ylines"]):
        x = 12 + 14 * i
        f.out.append(f'<text class="ti" x="{x}" y="{cy}" text-anchor="middle" '
                     f'transform="rotate(-90 {x} {cy})">{line}</text>')
    for i, line in enumerate(lay["title"]):
        f.out.append(f'<text class="ti" x="{f.w / 2}" y="{14 + 14 * i}" text-anchor="middle">{line}</text>')


def _legend(names: list[str], width: float, y: float, kind: str) -> list[str]:
    """A centered row of swatch-plus-label pairs, one per series."""
    widths = [36 + 6.4 * len(n) for n in names]
    x = (width - sum(widths)) / 2
    out = []
    for i, (name, w) in enumerate(zip(names, widths)):
        if kind == "bar":
            fill = "url(#rwhatch)" if i else "currentColor"
            out.append(f'<rect x="{x:.2f}" y="{y - 9:.2f}" width="12" height="12" '
                        f'fill="{fill}" opacity="{0.45 if i else 0.85}"/>')
            tx = x + 18
        else:
            dash = _DASH[i % 4]
            attrs = f' stroke-dasharray="{dash}"' if dash else ""
            out.append(f'<line x1="{x:.2f}" y1="{y - 3:.2f}" x2="{x + 16:.2f}" y2="{y - 3:.2f}" '
                        f'stroke="currentColor" stroke-width="1.8"{attrs}/>')
            out.append(_marker(_MARK[i % 4], x + 8, y - 3))
            tx = x + 22
        out.append(f'<text class="lb" x="{tx:.2f}" y="{y + 2:.2f}">{name}</text>')
        x += w
    return out


def _bar(fig: dict) -> str:
    data = fig["data"]
    n = len(data)
    categories = [str(p[0]) for p in data[0]["points"]]
    top = max(float(v) for s in data for _, v in s["points"]) * 1.15 or 1
    lay = _layout(fig, n, _ticks(0, top))
    f = _Frame(0, len(categories), 0, top, w=440, h=lay["h"], pad_t=lay["pad_t"], pad_l=lay["pad_l"])
    f.grid((), _ticks(0, top))
    _labels(f, lay, fig.get("x_axis", ""))
    if n > 1:
        f.out.append(_HATCH)
    group_w = (f.w - f.l - f.r) / len(categories)
    bar_w = group_w * 0.64 / n
    gap = group_w * 0.18
    for gi, cat in enumerate(categories):
        for si, series in enumerate(data):
            v = float(series["points"][gi][1])
            x = f.l + gi * group_w + gap + si * bar_w
            y = f.Y(v)
            fill = "url(#rwhatch)" if si else "currentColor"
            op = 0.45 if si else 0.85
            f.out.append(f'<rect x="{x:.2f}" y="{y}" width="{round(bar_w * 0.9, 2)}" '
                         f'height="{round(f.Y(0) - y, 2)}" fill="{fill}" opacity="{op}"/>')
        label_x = f.l + gi * group_w + group_w / 2
        f.out.append(f'<text class="lb" x="{round(label_x, 2)}" y="{f.h - f.b + 15}" '
                     f'text-anchor="middle">{cat}</text>')
    if n > 1:
        f.out.extend(_legend([s["series"] for s in data], f.w, lay["legend_y"], "bar"))
    return f.done()


def _line(fig: dict) -> str:
    data = fig["data"]
    n = len(data)
    all_x = [p[0] for p in data[0]["points"]]
    numeric = isinstance(all_x[0], (int, float))
    all_y = [float(v) for s in data for _, v in s["points"]]
    x0, x1 = (min(all_x), max(all_x)) if numeric else (0, len(all_x) - 1)
    y0, y1 = min(min(all_y), 0), max(all_y) * 1.1 or 1
    lay = _layout(fig, n, _ticks(y0, y1))
    f = _Frame(x0, x1, y0, y1, w=440, h=lay["h"], pad_t=lay["pad_t"], pad_l=lay["pad_l"])
    xticks = list(all_x) if numeric else list(range(len(all_x)))
    xlabels = None if numeric else [str(v) for v in all_x]
    f.grid(xticks, _ticks(y0, y1), xlabels=xlabels)
    _labels(f, lay, fig.get("x_axis", ""))
    for si, series in enumerate(data):
        xs = [float(p[0]) if numeric else i for i, p in enumerate(series["points"])]
        ys = [float(p[1]) for p in series["points"]]
        dash = _DASH[si % 4]
        attrs = f' stroke-dasharray="{dash}"' if dash else ""
        pts = " ".join(f"{f.X(x)},{f.Y(y)}" for x, y in zip(xs, ys))
        f.out.append(f'<polyline class="ln" points="{pts}"{attrs}/>')
        for x, y in zip(xs, ys):
            f.out.append(_marker(_MARK[si % 4], f.X(x), f.Y(y)))
    if n > 1:
        f.out.extend(_legend([s["series"] for s in data], f.w, lay["legend_y"], "line"))
    return f.done()


def render(figure: dict) -> str:
    kind = figure.get("kind")
    if kind == "bar graph":
        return _bar(figure)
    if kind == "line graph":
        return _line(figure)
    raise ValueError(f"unknown figure kind: {kind!r}")


if __name__ == "__main__":
    import glob
    import json
    import os

    from .topics.rw import BANK

    seen = 0
    for path in sorted(glob.glob(os.path.join(BANK, "*.json"))):
        for it in json.load(open(path))["items"]:
            fig = it.get("figure")
            if not fig:
                continue
            svg = render(fig)
            assert svg.startswith("<svg") and svg.endswith("</svg>"), it["id"]
            for series in fig["data"]:
                if len(fig["data"]) > 1:
                    assert series["series"] in svg, (it["id"], "missing series", series["series"])
                for cat, _ in series["points"]:
                    assert str(cat) in svg, (it["id"], "missing category/x label", cat)
            lay = _layout(fig, len(fig["data"]))   # tick widths only move the left edge
            for word in (fig.get("title", "") + " " + fig.get("y_axis", "")).split():
                assert word in svg, (it["id"], "missing title or y-label word", word)
            plot_h = lay["h"] - lay["pad_t"] - 40
            assert all(len(x) * _CH <= plot_h for x in lay["ylines"]), (it["id"], "y label longer than the plot")
            seen += 1
    print(f"ok  {seen} figures rendered, every series, category, title and y-label word present and fitting")
