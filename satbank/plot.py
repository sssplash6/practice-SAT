"""Generated charts: the figures the data and function topics need.

Same contract as `figures.py` -- an SVG string drawn in `currentColor`, so a
chart reads on light and dark backgrounds, and generated from the same
parameters as the stem, so a regenerated item cannot keep a stale picture.

Every chart takes exact data and draws exactly that data: no smoothing, no
auto-fitted trend line unless one is passed in, nothing a student could read
off the picture that the numbers do not say.
"""

from __future__ import annotations

from .exact import MINUS

from fractions import Fraction

__all__ = ["scatter", "bar", "histogram", "dotplot", "boxplot", "line_graph", "curve",
           "boxplots", "histograms"]

_CSS = (".ax{stroke:currentColor;stroke-width:1.3;fill:none}"
        ".bx{stroke:currentColor;stroke-width:1.3;fill:none}"
        ".gr{stroke:currentColor;stroke-width:.5;opacity:.22}"
        ".pt{fill:currentColor}"
        ".bar{fill:currentColor;opacity:.75}"
        ".ln{stroke:currentColor;stroke-width:1.8;fill:none}"
        ".lb{fill:currentColor;font:11px ui-sans-serif,system-ui,sans-serif}"
        ".ti{fill:currentColor;font:600 12px ui-sans-serif,system-ui,sans-serif}")


def _nice(v: float) -> str:
    """An axis label as the page prints it, with a typeset minus.

    Python spells a number's sign with the ASCII hyphen, so a chart whose axis
    runs below zero would label itself in the other spelling from the options
    beside it.
    """
    f = float(v)
    out = str(int(round(f))) if abs(f - round(f)) < 1e-9 else f"{f:g}"
    return out.replace("-", MINUS)


class _Frame:
    """An axis box with a data-to-pixel map. Every chart is drawn inside one."""

    def __init__(self, x0, x1, y0, y1, w=360, h=230, pad_l=46, pad_b=40, pad_t=16, pad_r=14):
        self.x0, self.x1, self.y0, self.y1 = float(x0), float(x1), float(y0), float(y1)
        if self.x1 == self.x0:
            self.x1 += 1
        if self.y1 == self.y0:
            self.y1 += 1
        self.w, self.h = w, h
        self.l, self.b, self.t, self.r = pad_l, pad_b, pad_t, pad_r
        self.out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
                    f'xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>']

    def X(self, x) -> float:
        span = self.x1 - self.x0
        return round(self.l + (float(x) - self.x0) / span * (self.w - self.l - self.r), 2)

    def Y(self, y) -> float:
        span = self.y1 - self.y0
        return round(self.h - self.b - (float(y) - self.y0) / span * (self.h - self.b - self.t), 2)

    def grid(self, xticks=(), yticks=(), xlabels=None, ylabels=None):
        for i, x in enumerate(xticks):
            px = self.X(x)
            self.out.append(f'<line class="gr" x1="{px}" y1="{self.Y(self.y0)}" '
                            f'x2="{px}" y2="{self.t}"/>')
            lab = (xlabels[i] if xlabels else _nice(x))
            self.out.append(f'<text class="lb" x="{px}" y="{self.h - self.b + 15}" '
                            f'text-anchor="middle">{lab}</text>')
        for i, y in enumerate(yticks):
            py = self.Y(y)
            self.out.append(f'<line class="gr" x1="{self.l}" y1="{py}" '
                            f'x2="{self.w - self.r}" y2="{py}"/>')
            lab = (ylabels[i] if ylabels else _nice(y))
            self.out.append(f'<text class="lb" x="{self.l - 7}" y="{py + 4}" '
                            f'text-anchor="end">{lab}</text>')
        return self

    def axes(self, xlabel="", ylabel=""):
        self.out.append(f'<line class="ax" x1="{self.l}" y1="{self.h - self.b}" '
                        f'x2="{self.w - self.r}" y2="{self.h - self.b}"/>')
        self.out.append(f'<line class="ax" x1="{self.l}" y1="{self.h - self.b}" '
                        f'x2="{self.l}" y2="{self.t}"/>')
        if xlabel:
            self.out.append(f'<text class="ti" x="{(self.l + self.w - self.r) / 2}" '
                            f'y="{self.h - 6}" text-anchor="middle">{xlabel}</text>')
        if ylabel:
            cy = (self.t + self.h - self.b) / 2
            self.out.append(f'<text class="ti" x="12" y="{cy}" text-anchor="middle" '
                            f'transform="rotate(-90 12 {cy})">{ylabel}</text>')
        return self

    def done(self) -> str:
        self.out.append("</svg>")
        return "".join(self.out)


def _ticks(lo: float, hi: float, want: int = 6) -> list[float]:
    span = hi - lo
    if span <= 0:
        return [lo]
    raw = span / want
    # whole-number data never gets half-unit gridlines: an axis reading
    # 0, 0.5, 1 under a count of cars is a tell that nobody drew this by hand
    if abs(lo - round(lo)) < 1e-9 and abs(hi - round(hi)) < 1e-9 and raw < 1:
        step = 1.0
        return [float(v) for v in range(int(round(lo)), int(round(hi)) + 1)
                if lo - 1e-9 <= v <= hi + 1e-9] or [lo, hi]
    mag = 10 ** (len(str(int(abs(raw)))) - 1) if abs(raw) >= 1 else 0.1
    step = next((s * mag for s in (1, 2, 2.5, 5, 10) if s * mag >= raw), raw)
    start = step * (int(lo / step) - (1 if lo < 0 else 0))
    out, v = [], start
    while v <= hi + 1e-9:
        if v >= lo - 1e-9:
            out.append(round(v, 10))
        v += step
    return out or [lo, hi]


def scatter(points, xlabel="", ylabel="", line=None, pad=0.12, **kw) -> str:
    """Points, optionally with a line of best fit passed in as (slope, intercept).

    The line is never fitted here: an item that asks about a line of best fit
    must have computed it, so the picture and the answer cannot disagree.
    """
    xs = [float(p[0]) for p in points]
    ys = [float(p[1]) for p in points]
    dx, dy = (max(xs) - min(xs)) or 1, (max(ys) - min(ys)) or 1
    f = _Frame(min(xs) - pad * dx, max(xs) + pad * dx,
               min(min(ys) - pad * dy, 0), max(ys) + pad * dy, **kw)
    f.grid(_ticks(f.x0, f.x1), _ticks(f.y0, f.y1)).axes(xlabel, ylabel)
    if line is not None:
        m, b = float(line[0]), float(line[1])
        f.out.append(f'<line class="ln" x1="{f.X(f.x0)}" y1="{f.Y(m * f.x0 + b)}" '
                     f'x2="{f.X(f.x1)}" y2="{f.Y(m * f.x1 + b)}"/>')
    for x, y in zip(xs, ys):
        f.out.append(f'<circle class="pt" cx="{f.X(x)}" cy="{f.Y(y)}" r="3.2"/>')
    return f.done()


def bar(labels, values, xlabel="", ylabel="", **kw) -> str:
    vals = [float(v) for v in values]
    f = _Frame(0, len(vals), 0, max(vals) * 1.15 or 1, **kw)
    f.grid((), _ticks(0, max(vals) * 1.15 or 1)).axes(xlabel, ylabel)
    width = (f.w - f.l - f.r) / len(vals)
    for i, (lab, v) in enumerate(zip(labels, vals)):
        x = f.l + i * width + width * 0.18
        bw = width * 0.64
        y = f.Y(v)
        f.out.append(f'<rect class="bar" x="{round(x, 2)}" y="{y}" width="{round(bw, 2)}" '
                     f'height="{round(f.Y(0) - y, 2)}"/>')
        f.out.append(f'<text class="lb" x="{round(x + bw / 2, 2)}" y="{f.h - f.b + 15}" '
                     f'text-anchor="middle">{lab}</text>')
    return f.done()


def histogram(edges, counts, xlabel="", ylabel="Frequency", **kw) -> str:
    """`edges` has one more entry than `counts`: the bin boundaries."""
    if len(edges) != len(counts) + 1:
        raise ValueError("a histogram needs one more edge than it has bars")
    top = max(float(c) for c in counts) * 1.15 or 1
    f = _Frame(float(edges[0]), float(edges[-1]), 0, top, **kw)
    f.grid([float(e) for e in edges], _ticks(0, top)).axes(xlabel, ylabel)
    for i, c in enumerate(counts):
        x, x2 = f.X(edges[i]), f.X(edges[i + 1])
        y = f.Y(float(c))
        f.out.append(f'<rect class="bar" x="{x}" y="{y}" width="{round(x2 - x, 2)}" '
                     f'height="{round(f.Y(0) - y, 2)}" stroke="currentColor"/>')
    return f.done()


def dotplot(values, xlabel="", **kw) -> str:
    """One dot per observation, stacked over its value -- the SAT's own form."""
    vals = sorted(float(v) for v in values)
    lo, hi = min(vals), max(vals)
    counts: dict[float, int] = {}
    tallest = 0
    for v in vals:
        counts[v] = counts.get(v, 0) + 1
        tallest = max(tallest, counts[v])
    f = _Frame(lo - 0.7, hi + 0.7, 0, tallest + 1, h=90 + 16 * tallest, pad_l=24, **kw)
    step = 1 if hi - lo <= 12 else max(1, round((hi - lo) / 10))
    marks = [lo + i * step for i in range(int((hi - lo) / step) + 1)]
    # a dot plot has a number line, not a pair of axes: the vertical position
    # of a dot is only its place in the stack, so an axis there would lie
    f.out.append(f'<line class="ax" x1="{f.l}" y1="{f.Y(0)}" '
                 f'x2="{f.w - f.r}" y2="{f.Y(0)}"/>')
    if xlabel:
        f.out.append(f'<text class="ti" x="{(f.l + f.w - f.r) / 2}" y="{f.h - 6}" '
                     f'text-anchor="middle">{xlabel}</text>')
    for x in marks:
        px = f.X(x)
        f.out.append(f'<line class="ax" x1="{px}" y1="{f.Y(0)}" x2="{px}" y2="{f.Y(0) + 4}"/>')
        f.out.append(f'<text class="lb" x="{px}" y="{f.Y(0) + 17}" '
                     f'text-anchor="middle">{_nice(x)}</text>')
    seen: dict[float, int] = {}
    for v in vals:
        seen[v] = seen.get(v, 0) + 1
        f.out.append(f'<circle class="pt" cx="{f.X(v)}" cy="{f.Y(seen[v] - 0.5)}" r="3.4"/>')
    return f.done()


def boxplot(lo, q1, med, q3, hi, xlabel="", **kw) -> str:
    lo, q1, med, q3, hi = (float(v) for v in (lo, q1, med, q3, hi))
    span = (hi - lo) or 1
    f = _Frame(lo - 0.12 * span, hi + 0.12 * span, 0, 1, h=120, pad_b=34, **kw)
    f.grid(_ticks(f.x0, f.x1), ()).axes(xlabel, "")
    ymid, half = f.Y(0.55), 22
    for v in (lo, hi):
        f.out.append(f'<line class="ax" x1="{f.X(v)}" y1="{ymid - 10}" '
                     f'x2="{f.X(v)}" y2="{ymid + 10}"/>')
    f.out.append(f'<line class="ax" x1="{f.X(lo)}" y1="{ymid}" x2="{f.X(q1)}" y2="{ymid}"/>')
    f.out.append(f'<line class="ax" x1="{f.X(q3)}" y1="{ymid}" x2="{f.X(hi)}" y2="{ymid}"/>')
    f.out.append(f'<rect class="ax" x="{f.X(q1)}" y="{ymid - half}" '
                 f'width="{round(f.X(q3) - f.X(q1), 2)}" height="{2 * half}"/>')
    f.out.append(f'<line class="ax" x1="{f.X(med)}" y1="{ymid - half}" '
                 f'x2="{f.X(med)}" y2="{ymid + half}"/>')
    return f.done()


def line_graph(points, xlabel="", ylabel="", marks=True, labels=None, **kw) -> str:
    """`labels` names the points that carry a printed value, by index:
    `{0: "(2003, 40)", 4: "10"}`. Source items often label two points on an
    otherwise unlabelled line and then ask a question only those two can
    answer, so a generated figure has to be able to say the same thing.
    """
    xs = [float(p[0]) for p in points]
    ys = [float(p[1]) for p in points]
    f = _Frame(min(xs), max(xs), min(min(ys), 0), max(ys) * 1.1 or 1, **kw)
    f.grid(_ticks(f.x0, f.x1), _ticks(f.y0, f.y1)).axes(xlabel, ylabel)
    d = " ".join(f"{f.X(x)},{f.Y(y)}" for x, y in zip(xs, ys))
    f.out.append(f'<polyline class="ln" points="{d}"/>')
    if marks:
        for x, y in zip(xs, ys):
            f.out.append(f'<circle class="pt" cx="{f.X(x)}" cy="{f.Y(y)}" r="2.8"/>')
    for i, text in (labels or {}).items():
        x, y = xs[i], ys[i]
        f.out.append(f'<circle class="pt" cx="{f.X(x)}" cy="{f.Y(y)}" r="3.6"/>')
        # above the point, or below it when the point sits near the top edge
        dy = 17 if f.Y(y) - f.t < 20 else -10
        f.out.append(f'<text class="lb" x="{f.X(x)}" y="{f.Y(y) + dy}" '
                     f'text-anchor="middle">{text}</text>')
    return f.done()


def curve(fn, x0, x1, xlabel="x", ylabel="y", points=(), steps=120, **kw) -> str:
    """y = fn(x) over [x0, x1], with the axes crossing at the origin when it
    is in view -- the shape a function item is asked to read."""
    xs = [x0 + (x1 - x0) * i / steps for i in range(steps + 1)]
    ys = [float(fn(x)) for x in xs]
    lo, hi = min(ys), max(ys)
    pad = (hi - lo) * 0.12 or 1
    f = _Frame(x0, x1, lo - pad, hi + pad, **kw)
    f.grid(_ticks(x0, x1), _ticks(lo - pad, hi + pad)).axes(xlabel, ylabel)
    if f.y0 <= 0 <= f.y1:
        f.out.append(f'<line class="ax" x1="{f.l}" y1="{f.Y(0)}" '
                     f'x2="{f.w - f.r}" y2="{f.Y(0)}"/>')
    if f.x0 <= 0 <= f.x1:
        f.out.append(f'<line class="ax" x1="{f.X(0)}" y1="{f.t}" '
                     f'x2="{f.X(0)}" y2="{f.h - f.b}"/>')
    d = " ".join(f"{f.X(x)},{f.Y(y)}" for x, y in zip(xs, ys))
    f.out.append(f'<polyline class="ln" points="{d}"/>')
    for x, y in points:
        f.out.append(f'<circle class="pt" cx="{f.X(x)}" cy="{f.Y(y)}" r="3.4"/>')
    return f.done()


# --------------------------------------------------------- several at a scale
#
# `boxplot` and `histogram` each fit their own axis to their own data. That is
# right for one chart and wrong for two: an item asking which of two
# distributions is more spread out is unanswerable -- worse, answerable
# backwards -- if the pictures are drawn to different scales. These take every
# series at once and draw one scale across all of them.


def _round_steps(lo: float, hi: float, want: int = 7) -> list[float]:
    """Tick positions on a round step, so the reader can count to a value."""
    span = float(hi) - float(lo)
    if span <= 0:
        return [float(lo)]
    raw = span / want
    mag = 1.0
    while mag * 10 <= raw:
        mag *= 10
    while mag > raw:
        mag /= 10
    step = next((s * mag for s in (1, 2, 2.5, 5, 10) if s * mag >= raw), raw)
    start = step * int(float(lo) / step)
    if start < float(lo) - 1e-9:
        start += step
    out, v = [], start
    while v <= float(hi) + 1e-9:
        out.append(round(v, 10))
        v += step
    return out or [float(lo), float(hi)]



def boxplots(summaries, labels, xlabel="", width=430) -> str:
    """One number line, one box plot per group, drawn to the same scale.

    `summaries` is a list of (least, Q1, median, Q3, greatest).
    """
    if len(summaries) != len(labels):
        raise ValueError("every box plot needs a label")
    vals = [float(v) for s in summaries for v in s]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    x0, x1 = lo - 0.22 * span, hi + 0.12 * span
    left, right = 74, 16
    row, top = 40, 16
    axis_y = top + row * len(summaries) + 10
    height = axis_y + 52

    def X(v):
        return round(left + (float(v) - x0) / (x1 - x0) * (width - left - right), 2)

    out = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
           f'role="img" xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>']
    for i, (s, lab) in enumerate(zip(summaries, labels)):
        lo_i, q1, med, q3, hi_i = (float(v) for v in s)
        cy = top + row * i + row / 2
        half = 13
        out.append(f'<text class="ti" x="{left - 10}" y="{cy + 4}" '
                   f'text-anchor="end">{lab}</text>')
        for v in (lo_i, hi_i):
            out.append(f'<line class="bx" x1="{X(v)}" y1="{cy - 7}" '
                       f'x2="{X(v)}" y2="{cy + 7}"/>')
        out.append(f'<line class="bx" x1="{X(lo_i)}" y1="{cy}" x2="{X(q1)}" y2="{cy}"/>')
        out.append(f'<line class="bx" x1="{X(q3)}" y1="{cy}" x2="{X(hi_i)}" y2="{cy}"/>')
        out.append(f'<rect class="bx" x="{X(q1)}" y="{round(cy - half, 2)}" '
                   f'width="{round(X(q3) - X(q1), 2)}" height="{2 * half}"/>')
        out.append(f'<line class="bx" x1="{X(med)}" y1="{round(cy - half, 2)}" '
                   f'x2="{X(med)}" y2="{round(cy + half, 2)}"/>')
    out.append(f'<line class="ax" x1="{X(x0)}" y1="{axis_y}" '
               f'x2="{X(x1)}" y2="{axis_y}"/>')
    for t in _round_steps(lo, hi):
        px = X(t)
        out.append(f'<line class="ax" x1="{px}" y1="{axis_y - 4}" '
                   f'x2="{px}" y2="{axis_y + 4}"/>')
        out.append(f'<text class="lb" x="{px}" y="{axis_y + 19}" '
                   f'text-anchor="middle">{_nice(t)}</text>')
    if xlabel:
        out.append(f'<text class="ti" x="{(left + width - right) / 2}" '
                   f'y="{height - 8}" text-anchor="middle">{xlabel}</text>')
    out.append("</svg>")
    return "".join(out)


def histograms(edges, series, labels, xlabel="", ylabel="Frequency",
                     width=400) -> str:
    """One panel per series, all on the same bins and the same frequency scale.

    `edges` has one more entry than each series: the bin boundaries.
    """
    for counts in series:
        if len(edges) != len(counts) + 1:
            raise ValueError("a histogram needs one more edge than it has bars")
    top_val = max(max(float(c) for c in counts) for counts in series)
    top_val = top_val * 1.12 or 1
    left, right = 46, 14
    panel, gap, head = 130, 56, 20
    height = (panel + gap) * len(series) + 26
    ticks = _round_steps(0, top_val, want=5)
    x0, x1 = float(edges[0]), float(edges[-1])

    def X(v):
        return round(left + (float(v) - x0) / (x1 - x0) * (width - left - right), 2)

    out = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
           f'role="img" xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>']
    for k, (counts, lab) in enumerate(zip(series, labels)):
        base = (panel + gap) * k + head
        floor = base + panel

        def Y(v, floor=floor):
            return round(floor - float(v) / top_val * panel, 2)

        out.append(f'<text class="ti" x="{(left + width - right) / 2}" '
                   f'y="{base - 6}" text-anchor="middle">{lab}</text>')
        for t in ticks:
            py = Y(t)
            out.append(f'<line class="gr" x1="{left}" y1="{py}" '
                       f'x2="{width - right}" y2="{py}"/>')
            out.append(f'<text class="lb" x="{left - 7}" y="{py + 4}" '
                       f'text-anchor="end">{_nice(t)}</text>')
        for i, c in enumerate(counts):
            if float(c) <= 0:
                continue
            xa, xb = X(edges[i]), X(edges[i + 1])
            out.append(f'<rect class="bar" x="{xa}" y="{Y(c)}" '
                       f'width="{round(xb - xa, 2)}" height="{round(Y(0) - Y(c), 2)}"/>')
        out.append(f'<line class="ax" x1="{left}" y1="{floor}" '
                   f'x2="{width - right}" y2="{floor}"/>')
        out.append(f'<line class="ax" x1="{left}" y1="{floor}" '
                   f'x2="{left}" y2="{base}"/>')
        for e in edges:
            px = X(e)
            out.append(f'<line class="ax" x1="{px}" y1="{floor}" '
                       f'x2="{px}" y2="{floor + 4}"/>')
            out.append(f'<text class="lb" x="{px}" y="{floor + 17}" '
                       f'text-anchor="middle">{_nice(e)}</text>')
        cy = base + panel / 2
        out.append(f'<text class="ti" x="12" y="{cy}" text-anchor="middle" '
                   f'transform="rotate(-90 12 {cy})">{ylabel}</text>')
        out.append(f'<text class="ti" x="{(left + width - right) / 2}" '
                   f'y="{floor + 36}" text-anchor="middle">{xlabel}</text>')
    out.append("</svg>")
    return "".join(out)
