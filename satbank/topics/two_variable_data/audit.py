"""An independent solver for every template in this topic.

Each solver re-derives the answer from `item.params` alone and shares no code
with the generator: the line of best fit is refitted here from the recorded
points by the normal equations, the quadratic models are scored against the
recorded dots, and a sentence-valued item is decided by reading the four
printed sentences and working out which of them is true. A template that gets
the mathematics wrong therefore has to get it wrong twice, in two different
ways, to escape.
"""

from __future__ import annotations

import re
from fractions import Fraction as Q

from ...audit import AuditError

__all__ = ["AUDITS"]

MINUS = "−"


def supply_slope(p: dict) -> float:
    return float((Q(p["y1"]) - Q(p["y0"])) / (Q(p["x1"]) - Q(p["x0"])))


def supply_predict(p: dict) -> float:
    return float(Q(p["slope"]) * Q(p["x"]) + Q(p["intercept"]))


def supply_residual(p: dict) -> float:
    predicted = Q(p["slope"]) * Q(p["x"]) + Q(p["intercept"])
    return float(Q(p["observed"]) - predicted)


def _n(text) -> Q:
    """A number as this topic prints one: 480, 1,200, −0.7, 3/4."""
    t = str(text).replace(MINUS, "-").replace(",", "").replace("%", "").strip()
    t = t.replace("°F", "").replace("°C", "").replace("$", "").strip()
    if "/" in t:
        a, b = t.split("/", 1)
        return Q(int(a), int(b))
    return Q(t)


def _ns(seq) -> list:
    return [_n(v) for v in seq]


def _round(v, step) -> Q:
    """Round v to the nearest multiple of step, halves away from zero."""
    k = Q(v) / Q(step)
    a, b = k.numerator, k.denominator
    whole = (2 * a + b) // (2 * b) if a >= 0 else -((-2 * a + b) // (2 * b))
    return Q(whole) * Q(step)


def _fit(xs, ys) -> tuple:
    """Least squares by the normal equations: nΣxy − ΣxΣy over nΣx² − (Σx)²."""
    n = len(xs)
    sx = sum(xs, Q(0))
    sy = sum(ys, Q(0))
    sxy = sum((x * y for x, y in zip(xs, ys)), Q(0))
    sxx = sum((x * x for x in xs), Q(0))
    den = n * sxx - sx * sx
    if den == 0:
        raise AuditError("every plotted point has the same x-value")
    m = (n * sxy - sx * sy) / den
    return m, (sy - m * sx) / n


# ------------------------------------------------------------------- reading

def point_read(p) -> float:
    return float(_ns(p["ys"])[p["j"]])


def curve_read(p) -> float:
    a, c, x = _n(p["a"]), _n(p["c"]), _n(p["x"])
    f = lambda t: a * t * t + c * t
    v = f(x) - f(_n(p["x2"])) if p["x2"] is not None else f(x)
    return float(_round(v, _n(p["gap"])))


def rate_of_change(p) -> float:
    ys = _ns(p["ys"])
    i, j = p["i"], p["j"]
    return float((ys[j] - ys[i]) / Q(j - i))


def interval_change(p) -> str:
    vals = _ns(p["values"])
    moves = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
    if p["direction"] == "down":
        score = [-v for v in moves]
    elif p["direction"] == "up":
        score = list(moves)
    else:
        score = [abs(v) for v in moves]
    best = max(p["offer"], key=lambda i: score[i])
    if sum(1 for i in p["offer"] if score[i] == score[best]) != 1:
        raise AuditError("two of the offered intervals tie for the biggest move")
    return p["labels"][best]


def series_extreme(p) -> str:
    vals = _ns(p["values"])
    want = min if p["ask"] == "least" else max
    best = want(p["offer"], key=lambda i: vals[i])
    if sum(1 for i in p["offer"] if vals[i] == vals[best]) != 1:
        raise AuditError("two of the offered readings tie")
    return p["labels"][best]


# -------------------------------------------------------- lines of best fit

def predict_from_line(p) -> float:
    m, b = _fit(_ns(p["xs"]), _ns(p["ys"]))
    return float(_round(m * _n(p["xq"]) + b, _n(p["gap"])))


def fit_slope(p) -> float:
    m, _ = _fit(_ns(p["xs"]), _ns(p["ys"]))
    return float(_round(m, _n(p["gap"])))


def residual(p) -> float:
    xs, ys = _ns(p["xs"]), _ns(p["ys"])
    m, b = _fit(xs, ys)
    j = p["j"]
    return float(_round(abs(ys[j] - (m * xs[j] + b)), _n(p["gap"])))


def slope_scaled(p) -> float:
    return float(abs(_n(p["m"])) * _n(p["k"]))


LINE = re.compile(r"^\s*\w+\s*=\s*(.+)$")
TERM = re.compile(r"([+−-]?)\s*([\d.,]*)\s*([a-z]?)")


def _read_line(text: str, var: str) -> tuple:
    """`n = 16,090 + 4,680t` and `y = −x + 6` alike, as (slope, intercept)."""
    m = LINE.match(text)
    if m is None:
        raise AuditError(f"cannot read {text!r} as an equation")
    body = m.group(1).replace(" ", "")
    slope, const, i = Q(0), Q(0), 0
    while i < len(body):
        mt = TERM.match(body, i)
        if mt is None or mt.end() == i:
            raise AuditError(f"cannot read {text!r} at {body[i:]!r}")
        sign, digits, name = mt.groups()
        if name and name != var:
            raise AuditError(f"{text!r} mentions {name!r}, not {var!r}")
        v = _n(digits) if digits else Q(1)
        if sign in ("-", MINUS):
            v = -v
        if name:
            slope += v
        else:
            const += v
        i = mt.end()
    return slope, const


def fit_equation(p) -> str:
    """The one printed equation that is close to the refitted line of best fit."""
    xs, ys = _ns(p["xs"]), _ns(p["ys"])
    m, b = _fit(xs, ys)
    span = max(ys) - min(ys)
    good = []
    for text in p["texts"]:
        mm, bb = _read_line(text, p["var"])
        off = max(abs((mm - m) * x + (bb - b)) for x in xs)
        if off <= span / 6:
            good.append(text)
    if len(good) != 1:
        raise AuditError(f"{len(good)} of the four equations fit the plotted points")
    return good[0]


def association(p) -> str:
    """The direction is the sign of the refitted slope; only one sentence says it."""
    m, _b = _fit(_ns(p["xs"]), _ns(p["ys"]))
    X, Y = p["x"], p["y"]
    rising = {f"As the {X} increases, the {Y} tends to increase.",
              f"As the {X} decreases, the {Y} tends to decrease."}
    falling = {f"As the {X} increases, the {Y} tends to decrease.",
               f"As the {X} decreases, the {Y} tends to increase."}
    want = rising if m > 0 else falling
    hits = [t for t in p["texts"] if t in want]
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} of the four sentences describe the direction")
    return hits[0]


EACH = re.compile(r"^Each year between (\d+) and (\d+), the average increase in (.+) "
                  r"was ([\d.]+) (\w+)\.$")
DECADE = re.compile(r"^Every 10 years between (\d+) and (\d+), the average increase in "
                    r"(.+) was ([\d.]+) (\w+)\.$")


def interpret_slope(p) -> str:
    m = _n(p["m"])
    true = []
    for t in p["texts"]:
        e, d = EACH.match(t), DECADE.match(t)
        if e and _n(e.group(4)) == m:
            true.append(t)
        elif d and _n(d.group(4)) == 10 * m:
            true.append(t)
    if len(true) != 1:
        raise AuditError(f"{len(true)} of the four sentences are true of this slope")
    return true[0]


# ------------------------------------------------------------ model choices

def model_type(p) -> str:
    want = {"linear_up": "A linear model with a positive slope",
            "linear_down": "A linear model with a negative slope",
            "exp_growth": "An exponential growth model",
            "exp_decay": "An exponential decay model"}[p["shape"]]
    if p["texts"].count(want) != 1:
        raise AuditError("the four options do not name four different shapes once each")
    return want


QUAD = re.compile(r"^\s*\w+\s*=\s*(.+)$")


def _read_quad(text: str) -> tuple:
    """`y = 2x² − 11x + 20` as (a, b, c). Written from the printed string."""
    body = QUAD.match(text).group(1).replace(" ", "").replace(",", "")
    a = b = c = Q(0)
    i, seen = 0, False
    while i < len(body):
        m = re.match(r"([+−-]?)([\d.]*)(x²|x|)", body[i:])
        if m is None or m.end() == 0:
            raise AuditError(f"cannot read {text!r} at {body[i:]!r}")
        sign, digits, tail = m.groups()
        v = _n(digits) if digits else Q(1)
        if sign in ("-", MINUS):
            v = -v
        if tail == "x²":
            a += v
        elif tail == "x":
            b += v
        else:
            c += v
        seen = True
        i += m.end()
    if not seen:
        raise AuditError(f"cannot read {text!r} as a quadratic")
    return a, b, c


def best_model(p) -> str:
    xs, ys = _ns(p["xs"]), _ns(p["ys"])
    span = max(ys) - min(ys)
    good = []
    for text in p["texts"]:
        a, b, c = _read_quad(text)
        off = max(abs(a * x * x + b * x + c - y) for x, y in zip(xs, ys))
        if off <= span / 8:
            good.append(text)
    if len(good) != 1:
        raise AuditError(f"{len(good)} of the four models fit the plotted points")
    return good[0]


def growth_compare(p) -> str:
    base, m, k = p["base"], _n(p["m"]), _n(p["k"])
    var = p["var"]
    # a touch point is not a change of side, so the zeros are dropped and what
    # is left has to be one sign, or one change from below the line to above it
    diff = [float(base) ** (i / 20) - float(m * Q(i, 20) + k) for i in range(1, 1_601)]
    signs = [v > 0 for v in diff if v != 0]
    if all(not v for v in signs):
        shape = "less"
    elif all(signs):
        shape = "greater"
    else:
        flips = sum(1 for a, b in zip(signs, signs[1:]) if a != b)
        if flips != 1 or signs[0]:
            raise AuditError("the two graphs cross in a way no option describes")
        shape = "cross"
    hits = [t for t in p["texts"] if _shape_of(t, var) == shape]
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} of the four sentences match the shape")
    return hits[0]


def _shape_of(text: str, var: str) -> str:
    """Which of the four claims a printed sentence makes."""
    if text.startswith(f"For all {var} > 0"):
        return "less" if "<" in text else "greater"
    first = text.split(", but if")[0]
    return "cross" if "<" in first.split("then")[1] else "cross_back"


def invest_compare(p) -> str:
    """Compound interest is increasing, so only two of the four can ever be true."""
    pa, rate, fee = Q(p["pa"]), _n(p["rate"]), _n(p["fee"])
    A, B = p["a"], p["b"]
    # what A earns in year n is pa*rate*(1+rate)**(n-1): strictly increasing and
    # unbounded, so it passes any fixed amount exactly once, and never falls back
    first = pa * rate
    if first == fee:
        raise AuditError("the two accounts earn the same in the first year")
    if first > fee:
        want = f"{A} always earns more money per year than {B}."
    else:
        want = (f"{A} earns less money per year than {B} at first but eventually earns "
                f"more money per year.")
    if p["texts"].count(want) != 1:
        raise AuditError("the true sentence is not among the four printed once")
    return want


PAIRS = re.compile(r"x = (.+); y = (.+)")


def _list(text: str) -> list:
    return [_n(v) for v in text.replace(", and ", ", ").replace(" and ", ", ").split(", ")]


def nonlinear_table(p) -> str:
    curved = []
    for t in p["texts"]:
        m = PAIRS.match(t)
        if m is None:
            raise AuditError(f"cannot read {t!r} as a table")
        xs, ys = _list(m.group(1)), _list(m.group(2))
        if len(xs) != len(ys) or len(xs) < 3:
            raise AuditError("a table with mismatched rows")
        d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(len(xs) - 1)]
        if len(set(d)) != 1:
            curved.append(t)
    if len(curved) != 1:
        raise AuditError(f"{len(curved)} of the four tables are nonlinear")
    return curved[0]


def graph_statement(p) -> str:
    """Re-read the four sentences against the vertices and find the false one."""
    pts = [(_n(t), _n(v)) for t, v in p["pts"]]
    ts = [t for t, _ in pts]
    vs = [v for _, v in pts]
    total = ts[-1]
    name = p["name"]
    up = sum((ts[i + 1] - ts[i] for i in range(len(pts) - 1) if vs[i + 1] > vs[i]), Q(0))
    down = sum((ts[i + 1] - ts[i] for i in range(len(pts) - 1) if vs[i + 1] < vs[i]), Q(0))
    top = max(vs)
    t_top = ts[vs.index(top)]
    false = []
    for t in p["texts"]:
        if "constant speed for" in t:
            want = _word(t, "constant speed for")
            ok = any(ts[i + 1] - ts[i] == want and vs[i] == vs[i + 1]
                     for i in range(len(pts) - 1))
        elif "longer period of time" in t:
            ok = up > down
        elif "decreased at a constant rate during the last" in t:
            want = _word(t, "during the last")
            ok = total - ts[-2] == want and vs[-1] < vs[-2]
        elif "reached its maximum during the last" in t:
            want = _word(t, "during the last")
            ok = total - t_top <= want
        else:
            raise AuditError(f"cannot read the statement {t!r}")
        if not ok:
            false.append(t)
    if len(false) != 1:
        raise AuditError(f"{len(false)} of the four statements are untrue")
    if name not in false[0]:
        raise AuditError("the false statement is about somebody else")
    return false[0]


WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
         "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
         "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
         "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
         "twenty-one": 21, "twenty-two": 22, "twenty-three": 23, "twenty-four": 24,
         "twenty-five": 25}


def _word(text: str, after: str) -> Q:
    tail = text.split(after, 1)[1].strip().split(" ")[0]
    if tail in WORDS:
        return Q(WORDS[tail])
    return _n(tail)


AUDITS = {
    "tvdata_supply_slope": supply_slope,
    "tvdata_supply_predict": supply_predict,
    "tvdata_supply_residual": supply_residual,
    "tvdata.point_read": point_read,
    "tvdata.interval_change": interval_change,
    "tvdata.series_extreme": series_extreme,
    "tvdata.curve_read": curve_read,
    "tvdata.rate_of_change": rate_of_change,
    "tvdata.predict_from_line": predict_from_line,
    "tvdata.fit_slope": fit_slope,
    "tvdata.fit_equation": fit_equation,
    "tvdata.residual": residual,
    "tvdata.slope_scaled": slope_scaled,
    "tvdata.association": association,
    "tvdata.interpret_slope": interpret_slope,
    "tvdata.model_type": model_type,
    "tvdata.graph_statement": graph_statement,
    "tvdata.best_model": best_model,
    "tvdata.growth_compare": growth_compare,
    "tvdata.invest_compare": invest_compare,
    "tvdata.nonlinear_table": nonlinear_table,
}
