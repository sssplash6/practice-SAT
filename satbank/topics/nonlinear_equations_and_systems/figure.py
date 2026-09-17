"""The xy-plane, with a curve on it.

`satbank.figures.coordinate_grid` draws points and straight segments, which is
all a linear topic needs. A parabola, a V and an exponential are not segments, so
this module draws the same grid with polylines added -- same CSS class names, so
anything that reads one figure back reads the other.

Everything is drawn in `currentColor`, and every coordinate comes from the same
parameters as the stem, so a regenerated item cannot keep a stale picture. The
polyline is emitted at whole pixel-sixteenths, which is what lets
`option_check.py` recover the drawn curve from the file and check it against the
printed options.
"""

from __future__ import annotations

__all__ = ["plane"]

_CSS = (".ax{stroke:currentColor;stroke-width:1.4;fill:none}"
        ".gr{stroke:currentColor;stroke-width:.5;opacity:.28}"
        ".pt{fill:currentColor}"
        ".sg{stroke:currentColor;stroke-width:2.2;fill:none}"
        ".cv{stroke:currentColor;stroke-width:2.2;fill:none}"
        ".lb{fill:currentColor;font:11px ui-sans-serif,system-ui,sans-serif}"
        ".it{fill:currentColor;font:italic 13px ui-serif,Georgia,serif}")


def _r(v: float) -> str:
    return f"{round(float(v), 2):g}"


def plane(xmin, xmax, ymin, ymax, curves=(), segments=(), points=(), step=2,
          px=None, pad=26, labels=()) -> str:
    """A unit grid with labelled axes, straight segments and sampled curves.

    `curves` are functions of x; each is sampled across the window and clipped to
    it, and a sample that leaves the window ends the stroke rather than being
    pulled back to the border, so a steep branch does not acquire a corner it
    does not have.
    """
    xmin, xmax, ymin, ymax = int(xmin), int(xmax), int(ymin), int(ymax)
    if px is None:
        span = max(xmax - xmin, ymax - ymin, 1)
        px = max(13, min(26, 420 // span))
    w, h = (xmax - xmin) * px + 2 * pad, (ymax - ymin) * px + 2 * pad

    def X(x):
        return pad + (float(x) - xmin) * px

    def Y(y):
        return h - pad - (float(y) - ymin) * px

    out = [f'<svg viewBox="0 0 {_r(w)} {_r(h)}" width="{_r(w)}" height="{_r(h)}" '
           f'role="img" xmlns="http://www.w3.org/2000/svg"><style>{_CSS}</style>']
    for x in range(xmin, xmax + 1):
        out.append(f'<line class="gr" x1="{_r(X(x))}" y1="{_r(Y(ymin))}" '
                   f'x2="{_r(X(x))}" y2="{_r(Y(ymax))}"/>')
    for y in range(ymin, ymax + 1):
        out.append(f'<line class="gr" x1="{_r(X(xmin))}" y1="{_r(Y(y))}" '
                   f'x2="{_r(X(xmax))}" y2="{_r(Y(y))}"/>')
    out.append(f'<line class="ax" x1="{_r(X(xmin))}" y1="{_r(Y(0))}" '
               f'x2="{_r(X(xmax) + 12)}" y2="{_r(Y(0))}"/>')
    out.append(f'<line class="ax" x1="{_r(X(0))}" y1="{_r(Y(ymin))}" '
               f'x2="{_r(X(0))}" y2="{_r(Y(ymax) - 12)}"/>')
    out.append(f'<path class="pt" d="M{_r(X(xmax) + 12)},{_r(Y(0))} '
               f'l-6,-3.5 v7 z"/>')
    out.append(f'<path class="pt" d="M{_r(X(0))},{_r(Y(ymax) - 12)} '
               f'l-3.5,6 h7 z"/>')
    out.append(f'<text class="it" x="{_r(X(xmax) + 8)}" y="{_r(Y(0) + 18)}">x</text>')
    out.append(f'<text class="it" x="{_r(X(0) - 14)}" y="{_r(Y(ymax) - 10)}">y</text>')
    for x in range(xmin, xmax + 1):
        if x and x % step == 0:
            out.append(f'<text class="lb" x="{_r(X(x))}" y="{_r(Y(0) + 15)}" '
                       f'text-anchor="middle">{x}</text>')
    for y in range(ymin, ymax + 1):
        if y and y % step == 0:
            out.append(f'<text class="lb" x="{_r(X(0) - 7)}" y="{_r(Y(y) + 4)}" '
                       f'text-anchor="end">{y}</text>')
    out.append(f'<text class="it" x="{_r(X(0) - 11)}" y="{_r(Y(0) + 15)}">O</text>')

    for (x1, y1), (x2, y2) in segments:
        out.append(f'<line class="sg" x1="{_r(X(x1))}" y1="{_r(Y(y1))}" '
                   f'x2="{_r(X(x2))}" y2="{_r(Y(y2))}"/>')
    for fn in curves:
        for run in _runs(fn, xmin, xmax, ymin, ymax):
            pts = " ".join(f"{_r(X(x))},{_r(Y(y))}" for x, y in run)
            out.append(f'<polyline class="cv" points="{pts}"/>')
    for x, y in points:
        out.append(f'<circle class="pt" cx="{_r(X(x))}" cy="{_r(Y(y))}" r="4.5"/>')
    for x, y, text in labels:
        out.append(f'<text class="it" x="{_r(X(x))}" y="{_r(Y(y))}">{text}</text>')
    out.append("</svg>")
    return "".join(out)


def _runs(fn, xmin, xmax, ymin, ymax, steps: int = 200):
    """The curve, split into the stretches that stay inside the window."""
    runs, run = [], []
    for i in range(steps + 1):
        x = xmin + (xmax - xmin) * i / steps
        try:
            y = float(fn(x))
        except (ValueError, ZeroDivisionError, OverflowError):
            y = None
        if y is None or not (ymin <= y <= ymax):
            if len(run) > 1:
                runs.append(run)
            run = []
            continue
        run.append((x, y))
    if len(run) > 1:
        runs.append(run)
    return runs
