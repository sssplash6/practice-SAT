"""The pictures this topic draws, and the contract for reading them back.

`plot.curve` fits its own axis to its own data and places gridlines with
`_ticks`, which is right for a chart and wrong here: an item that asks a
student to read a y-intercept off a curve is only answerable if the gridlines
sit at whole numbers the reader can count. So these draw a plane with a grid
the caller chooses, and label it the way the source items label one.

Every figure is generated from the same numbers as the stem. The SVG keeps the
engine's class vocabulary -- `gr` gridlines, `ax` axes, `lb` labels, `ln` the
curve -- so `option_check.py` can recover the drawn curve from the picture's
own pixel geometry rather than from any parameter the template held.
"""

from __future__ import annotations

__all__ = ["plane_curve", "context_curve"]

_CSS = (".ax{stroke:currentColor;stroke-width:1.4;fill:none}"
        ".gr{stroke:currentColor;stroke-width:.5;opacity:.28}"
        ".pt{fill:currentColor}"
        ".ln{stroke:currentColor;stroke-width:2;fill:none}"
        ".lb{fill:currentColor;font:11px ui-sans-serif,system-ui,sans-serif}"
        ".it{fill:currentColor;font:italic 13px ui-serif,Georgia,serif}"
        ".ti{fill:currentColor;font:600 12px ui-sans-serif,system-ui,sans-serif}")


def _nice(v: float) -> str:
    return str(int(round(v))) if abs(v - round(v)) < 1e-9 else f"{v:g}"


def _frange(lo: float, hi: float, step: float):
    n = int(round((hi - lo) / step))
    return [lo + i * step for i in range(n + 1)]


def plane_curve(branches, xmin, xmax, ymin, ymax, xstep=1, ystep=1,
                xlabel_every=2, ylabel_every=2, dots=(), px=None) -> str:
    """An xy-plane with a grid, arrowed axes through the origin, and a curve.

    `branches` is a list of callables; each is sampled across the window and
    drawn as its own polyline, so a curve with a break (a rational function)
    is not joined across it. `dots` are points printed as filled circles --
    the source marks the y-intercept that way on several items.
    """
    xmin, xmax, ymin, ymax = float(xmin), float(xmax), float(ymin), float(ymax)
    wide, tall = (xmax - xmin) / xstep, (ymax - ymin) / ystep
    if px is None:
        px = max(9.0, min(30.0, 340.0 / max(wide, tall, 1)))
    pad = 30
    w = wide * px + 2 * pad
    h = tall * px + 2 * pad

    def X(x):
        return round(pad + (float(x) - xmin) / xstep * px, 2)

    def Y(y):
        return round(h - pad - (float(y) - ymin) / ystep * px, 2)

    out = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" '
           f'role="img" xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>']
    for x in _frange(xmin, xmax, xstep):
        out.append(f'<line class="gr" x1="{X(x)}" y1="{Y(ymin)}" '
                   f'x2="{X(x)}" y2="{Y(ymax)}"/>')
    for y in _frange(ymin, ymax, ystep):
        out.append(f'<line class="gr" x1="{X(xmin)}" y1="{Y(y)}" '
                   f'x2="{X(xmax)}" y2="{Y(y)}"/>')
    out.append(f'<line class="ax" x1="{X(xmin)}" y1="{Y(0)}" '
               f'x2="{X(xmax) + 12}" y2="{Y(0)}"/>')
    out.append(f'<line class="ax" x1="{X(0)}" y1="{Y(ymin)}" '
               f'x2="{X(0)}" y2="{Y(ymax) - 12}"/>')
    out.append(f'<path class="pt" d="M{X(xmax) + 12},{Y(0)} l-6,-3.5 v7 z"/>')
    out.append(f'<path class="pt" d="M{X(0)},{Y(ymax) - 12} l-3.5,6 h7 z"/>')
    out.append(f'<text class="it" x="{X(xmax) + 8}" y="{Y(0) + 18}">x</text>')
    out.append(f'<text class="it" x="{X(0) - 14}" y="{Y(ymax) - 10}">y</text>')
    out.append(f'<text class="it" x="{X(0) - 12}" y="{Y(0) + 15}">O</text>')
    for x in _frange(xmin, xmax, xstep):
        if abs(x) > 1e-9 and abs(round(x / xstep)) % xlabel_every == 0:
            out.append(f'<text class="lb" x="{X(x)}" y="{Y(0) + 15}" '
                       f'text-anchor="middle">{_nice(x)}</text>')
    for y in _frange(ymin, ymax, ystep):
        if abs(y) > 1e-9 and abs(round(y / ystep)) % ylabel_every == 0:
            out.append(f'<text class="lb" x="{X(0) - 7}" y="{Y(y) + 4}" '
                       f'text-anchor="end">{_nice(y)}</text>')

    for fnc in branches:
        run, steps = [], 240
        for i in range(steps + 1):
            x = xmin + (xmax - xmin) * i / steps
            try:
                y = float(fnc(x))
            except (TypeError, ValueError, ZeroDivisionError, OverflowError):
                y = None
            if y is None or not (ymin - 1e-9 <= y <= ymax + 1e-9):
                if len(run) > 1:
                    out.append(f'<polyline class="ln" points="'
                               + " ".join(run) + '"/>')
                run = []
                continue
            run.append(f"{X(x)},{Y(y)}")
        if len(run) > 1:
            out.append(f'<polyline class="ln" points="' + " ".join(run) + '"/>')
    for x, y in dots:
        out.append(f'<circle class="pt" cx="{X(x)}" cy="{Y(y)}" r="4"/>')
    out.append("</svg>")
    return "".join(out)


def context_curve(fnc, x0, x1, y0, y1, xlabel="", ylabel="", xstep=2, ystep=5,
                  dots=(), width=380, height=260) -> str:
    """A labelled chart: a curve over a context's own axes, both starting at 0.

    Used where the horizontal axis counts something -- years after 2010,
    elapsed hours -- rather than being a signed coordinate axis.
    """
    x0, x1, y0, y1 = float(x0), float(x1), float(y0), float(y1)
    left, bottom, top, right = 62, 52, 18, 18

    def X(x):
        return round(left + (float(x) - x0) / (x1 - x0) * (width - left - right), 2)

    def Y(y):
        return round(height - bottom - (float(y) - y0) / (y1 - y0)
                     * (height - bottom - top), 2)

    out = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
           f'role="img" xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>']
    for x in _frange(x0, x1, xstep):
        out.append(f'<line class="gr" x1="{X(x)}" y1="{Y(y0)}" '
                   f'x2="{X(x)}" y2="{Y(y1)}"/>')
        if abs(x - x0) > 1e-9:
            out.append(f'<text class="lb" x="{X(x)}" y="{Y(y0) + 16}" '
                       f'text-anchor="middle">{_group(x)}</text>')
    for y in _frange(y0, y1, ystep):
        out.append(f'<line class="gr" x1="{X(x0)}" y1="{Y(y)}" '
                   f'x2="{X(x1)}" y2="{Y(y)}"/>')
        if abs(y - y0) > 1e-9:
            out.append(f'<text class="lb" x="{X(x0) - 7}" y="{Y(y) + 4}" '
                       f'text-anchor="end">{_group(y)}</text>')
    out.append(f'<line class="ax" x1="{X(x0)}" y1="{Y(y0)}" '
               f'x2="{X(x1) + 10}" y2="{Y(y0)}"/>')
    out.append(f'<line class="ax" x1="{X(x0)}" y1="{Y(y0)}" '
               f'x2="{X(x0)}" y2="{Y(y1) - 10}"/>')
    out.append(f'<text class="it" x="{X(x1) + 8}" y="{Y(y0) + 18}">x</text>')
    out.append(f'<text class="it" x="{X(x0) - 14}" y="{Y(y1) - 8}">y</text>')
    out.append(f'<text class="it" x="{X(x0) - 12}" y="{Y(y0) + 15}">O</text>')

    run, steps = [], 240
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        y = float(fnc(x))
        if not (y0 - 1e-9 <= y <= y1 + 1e-9):
            continue
        run.append(f"{X(x)},{Y(y)}")
    if len(run) > 1:
        out.append('<polyline class="ln" points="' + " ".join(run) + '"/>')
    for x, y in dots:
        out.append(f'<circle class="pt" cx="{X(x)}" cy="{Y(y)}" r="4"/>')
    if xlabel:
        out.append(f'<text class="ti" x="{(left + width - right) / 2}" '
                   f'y="{height - 8}" text-anchor="middle">{xlabel}</text>')
    if ylabel:
        cy = (top + height - bottom) / 2
        out.append(f'<text class="ti" x="13" y="{cy}" text-anchor="middle" '
                   f'transform="rotate(-90 13 {cy})">{ylabel}</text>')
    out.append("</svg>")
    return "".join(out)


def _group(v: float) -> str:
    n = round(v)
    if abs(v - n) < 1e-9:
        return f"{n:,}" if abs(n) >= 1000 else str(n)
    return f"{v:g}"
