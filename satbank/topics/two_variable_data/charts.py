"""The pictures this topic asks questions about, drawn so they can be read back.

Every item here is a question about a picture, so the picture has to carry the
answer exactly. Three rules follow from that, and they are why this file exists
rather than `plot.scatter` being called directly:

* **The window is stated, never inferred.** `plot.scatter` fits its axes to the
  data it is handed, so two draws of the same item can be gridlined differently
  and a question about a reading becomes a question about a scale nobody chose.
  Here `x0, x1, y0, y1` and the gridline steps are arguments.
* **The gridline spacing is the resolution of the chart.** A reader can separate
  two values only when they are at least one gridline apart, so the step is
  something the template must know and the option check must be able to recover.
* **Everything a reader uses is in the SVG.** The gridlines carry their own
  printed labels, so the picture states its own scale. `option_check.py`
  recovers the pixels-to-data map from those labels alone -- not from the
  parameters that drew them -- and so reads the chart the way a student does.

Nothing is fitted here. A line of best fit is passed in; the template that
passes it is the one that has to prove the points support it.
"""

from __future__ import annotations

from fractions import Fraction as Q

__all__ = ["scatter", "series", "curve", "fmt_tick", "ticks_between"]

_CSS = (".ax{stroke:currentColor;stroke-width:1.4;fill:none}"
        ".gr{stroke:currentColor;stroke-width:.6;opacity:.3}"
        ".pt{fill:currentColor}"
        ".bf{stroke:currentColor;stroke-width:1.9;fill:none}"
        ".cv{stroke:currentColor;stroke-width:1.9;fill:none}"
        ".sr{stroke:currentColor;stroke-width:1.9;fill:none}"
        ".lb{fill:currentColor;font:11px ui-sans-serif,system-ui,sans-serif}"
        ".ti{fill:currentColor;font:600 12px ui-sans-serif,system-ui,sans-serif}")


def fmt_tick(v, group: bool = True) -> str:
    """A gridline label the way a chart prints one: 8,500 and 0.5 and 37.

    `group=False` is for an axis of years, where 1,960 is a misprint of 1960.
    """
    q = Q(v)
    if q.denominator == 1:
        return f"{q.numerator:,}" if group else str(q.numerator)
    neg = q < 0
    a = -q if neg else q
    whole = a.numerator // a.denominator
    rest = a - whole
    digits = ""
    for _ in range(6):
        if rest == 0:
            break
        rest *= 10
        digits += str(rest.numerator // rest.denominator)
        rest -= rest.numerator // rest.denominator
    head = f"{whole:,}" if group else str(whole)
    body = f"{head}.{digits}" if digits else head
    return ("-" if neg else "") + body


def ticks_between(lo, hi, step) -> list:
    """Every multiple of `step` inside [lo, hi], as exact rationals."""
    lo, hi, step = Q(lo), Q(hi), Q(step)
    if step <= 0:
        raise ValueError("a gridline step must be positive")
    k = -((-lo) // step) if lo % step else lo // step
    out = []
    v = k * step
    while v <= hi:
        if v >= lo:
            out.append(v)
        v += step
    return out


class _Frame:
    """An axis box and its data-to-pixel map. Every chart is drawn inside one."""

    def __init__(self, x0, x1, y0, y1, w, h, pad):
        self.x0, self.x1 = Q(x0), Q(x1)
        self.y0, self.y1 = Q(y0), Q(y1)
        if self.x1 <= self.x0 or self.y1 <= self.y0:
            raise ValueError("a chart window must have positive width and height")
        self.w, self.h = w, h
        self.l, self.r, self.t, self.b = pad
        self.out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
                    f'xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>']

    def X(self, x) -> float:
        span = self.x1 - self.x0
        return round(float(self.l + (Q(x) - self.x0) / span * (self.w - self.l - self.r)), 2)

    def Y(self, y) -> float:
        span = self.y1 - self.y0
        return round(float(self.h - self.b - (Q(y) - self.y0) / span
                          * (self.h - self.b - self.t)), 2)

    def grid(self, xstep, ystep, xlabel_every=1, ylabel_every=1, xlabels=None,
             xgroup=True):
        # a tall window can carry more gridlines than an axis can carry labels,
        # so the labels thin out rather than run into each other
        while len(ticks_between(self.y0, self.y1, Q(ystep))) // ylabel_every > 9:
            ylabel_every *= 2
        xs = ticks_between(self.x0, self.x1, xstep)
        wide = max((len(xlabels[x]) if xlabels and x in xlabels
                    else len(fmt_tick(x, xgroup))) for x in xs) if xs else 2
        room = max(1, int((self.w - self.l - self.r) // (6.6 * wide + 10)))
        while len(xs) // xlabel_every > room:
            xlabel_every *= 2
        for i, x in enumerate(xs):
            px = self.X(x)
            self.out.append(f'<line class="gr" x1="{px}" y1="{self.Y(self.y0)}" '
                            f'x2="{px}" y2="{self.Y(self.y1)}"/>')
            if i % xlabel_every == 0:
                text = (xlabels[x] if xlabels and x in xlabels
                        else fmt_tick(x, xgroup))
                self.out.append(f'<text class="lb xl" x="{px}" y="{self.h - self.b + 16}" '
                                f'text-anchor="middle">{text}</text>')
        ys = ticks_between(self.y0, self.y1, ystep)
        for i, y in enumerate(ys):
            py = self.Y(y)
            self.out.append(f'<line class="gr" x1="{self.X(self.x0)}" y1="{py}" '
                            f'x2="{self.X(self.x1)}" y2="{py}"/>')
            if i % ylabel_every == 0:
                self.out.append(f'<text class="lb yl" x="{self.l - 7}" y="{py + 4}" '
                                f'text-anchor="end">{fmt_tick(y)}</text>')
        return self

    def axes(self, xlabel="", ylabel="", title=""):
        self.out.append(f'<line class="ax" x1="{self.X(self.x0)}" y1="{self.Y(self.y0)}" '
                        f'x2="{self.X(self.x1)}" y2="{self.Y(self.y0)}"/>')
        self.out.append(f'<line class="ax" x1="{self.X(self.x0)}" y1="{self.Y(self.y0)}" '
                        f'x2="{self.X(self.x0)}" y2="{self.Y(self.y1)}"/>')
        if xlabel:
            self.out.append(f'<text class="ti" x="{(self.l + self.w - self.r) / 2}" '
                            f'y="{self.h - 6}" text-anchor="middle">{xlabel}</text>')
        if ylabel:
            cy = (self.t + self.h - self.b) / 2
            self.out.append(f'<text class="ti" x="13" y="{cy}" text-anchor="middle" '
                            f'transform="rotate(-90 13 {cy})">{ylabel}</text>')
        if title:
            self.out.append(f'<text class="ti" x="{(self.l + self.w - self.r) / 2}" '
                            f'y="13" text-anchor="middle">{title}</text>')
        return self

    def dots(self, points, r=3.4):
        for x, y in points:
            self.out.append(f'<circle class="pt" cx="{self.X(x)}" cy="{self.Y(y)}" r="{r}"/>')
        return self

    def straight(self, m, b, cls="bf"):
        """y = mx + b, clipped to the window so it never leaves the axes."""
        m, b = Q(m), Q(b)
        xa, xb = self.x0, self.x1
        if m != 0:
            for edge in (self.y0, self.y1):
                xe = (edge - b) / m
                if self.x0 <= xe <= self.x1:
                    if (m > 0) == (edge == self.y0):
                        xa = max(xa, xe)
                    else:
                        xb = min(xb, xe)
        if xb <= xa:
            raise ValueError("the line of best fit does not cross the window")
        self.out.append(f'<line class="{cls}" x1="{self.X(xa)}" y1="{self.Y(m * xa + b)}" '
                        f'x2="{self.X(xb)}" y2="{self.Y(m * xb + b)}"/>')
        return self

    def path(self, points, cls):
        d = " ".join(f"{self.X(x)},{self.Y(y)}" for x, y in points)
        self.out.append(f'<polyline class="{cls}" points="{d}"/>')
        return self

    def done(self) -> str:
        self.out.append("</svg>")
        return "".join(self.out)


def _frame(x0, x1, y0, y1, w, h, pad):
    return _Frame(x0, x1, y0, y1, w, h, pad)


def _pad(y0, y1, ystep, ylabel_every, pad):
    """Room on the left for the longest printed y label, and no more.

    A fixed gutter puts "100,000" under the axis title; the width of the widest
    label is what actually decides how much room the numbers need.
    """
    if pad is not None:
        return pad
    ticks = ticks_between(y0, y1, Q(ystep) * ylabel_every)
    wide = max((len(fmt_tick(t)) for t in ticks), default=2)
    return (max(46, 24 + round(6.6 * wide)), 16, 24, 46)


def scatter(points, *, x0, x1, y0, y1, xstep, ystep, xlabel="", ylabel="",
            title="", line=None, xlabel_every=1, ylabel_every=1, xlabels=None,
            xgroup=True, width=390, height=272, pad=None) -> str:
    """A scatterplot on a stated window, optionally with a line drawn through it.

    `line` is `(slope, intercept)` and is drawn exactly as given: this file
    never fits one, so the picture can only disagree with the answer if the
    template handed it the wrong line.
    """
    f = _frame(x0, x1, y0, y1, width, height,
               _pad(y0, y1, ystep, ylabel_every, pad))
    f.grid(xstep, ystep, xlabel_every, ylabel_every, xlabels, xgroup)
    f.axes(xlabel, ylabel, title)
    if line is not None:
        f.straight(line[0], line[1])
    f.dots(points)
    return f.done()


def series(points, *, x0, x1, y0, y1, xstep, ystep, xlabel="", ylabel="",
           title="", xlabel_every=1, ylabel_every=1, xlabels=None, xgroup=True,
           width=390, height=272, pad=None) -> str:
    """A line graph: the same points, joined in the order given."""
    f = _frame(x0, x1, y0, y1, width, height,
               _pad(y0, y1, ystep, ylabel_every, pad))
    f.grid(xstep, ystep, xlabel_every, ylabel_every, xlabels, xgroup)
    f.axes(xlabel, ylabel, title)
    f.path(points, "sr")
    f.dots(points, r=3.0)
    return f.done()


def curve(fn, *, x0, x1, y0, y1, xstep, ystep, xlabel="", ylabel="", title="",
          points=(), steps=96, xlabel_every=1, ylabel_every=1,
          width=390, height=272, pad=None) -> str:
    """y = fn(x) over the window, with the plotted observations on top of it."""
    f = _frame(x0, x1, y0, y1, width, height,
               _pad(y0, y1, ystep, ylabel_every, pad))
    f.grid(xstep, ystep, xlabel_every, ylabel_every)
    f.axes(xlabel, ylabel, title)
    span = Q(x1) - Q(x0)
    drawn = []
    for i in range(steps + 1):
        x = Q(x0) + span * Q(i, steps)
        y = Q(fn(x))
        if Q(y0) <= y <= Q(y1):
            drawn.append((x, y))
    f.path(drawn, "cv")
    f.dots(points)
    return f.done()
