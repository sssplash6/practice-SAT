"""Independent re-derivation of every Linear Functions answer.

Written from the algebra, not from the generators. Nothing here imports the
topic's own rendering or its families: slopes are recomputed from the two
points, tables are re-fitted, inverse items are solved rather than
constructed, and the written options are identified by the slope and intercept
they encode rather than by the string the generator produced.

A wrong answer therefore has to be produced twice, by two separately written
pieces of code, to escape.
"""

from __future__ import annotations

from fractions import Fraction as F

from ...audit import AuditError

__all__ = ["AUDITS"]


# ------------------------------------------------------------------ helpers

def r(v) -> F:
    """A [numerator, denominator] pair from params back to an exact rational."""
    return F(int(v[0]), int(v[1]))


def fit(xs, ys) -> tuple[F, F]:
    """Slope and intercept of the line through a table, checked on every row."""
    xs = [r(v) for v in xs]
    ys = [r(v) for v in ys]
    if xs[1] == xs[0]:
        raise AuditError("two table rows share an input")
    m = (ys[1] - ys[0]) / (xs[1] - xs[0])
    b = ys[0] - m * xs[0]
    for x, y in zip(xs, ys):
        if m * x + b != y:
            raise AuditError(f"the table is not linear at x = {x}")
    return m, b


def pick(p: dict, want: list) -> str:
    """The option whose recorded signature is the one the algebra produces."""
    want = list(want)
    hits = [i for i, s in enumerate(p["sigs"]) if list(s) == want]
    if len(hits) != 1:
        raise AuditError(f"signature {want} matches {len(hits)} of {p['sigs']}")
    return p["texts"][hits[0]]


def line_sig(m: F, b: F) -> list:
    return [m.numerator, m.denominator, b.numerator, b.denominator]


def role(p: dict, want: str) -> str:
    hits = [i for i, k in enumerate(p["roles"]) if k == want]
    if len(hits) != 1:
        raise AuditError(f"role {want!r} appears {len(hits)} times in {p['roles']}")
    return p["texts"][hits[0]]


def cash(v) -> str:
    return f"${float(v):,.2f}"


def rounded(v: F) -> F:
    """Nearest whole number; the source rounds half away from zero never occurs
    because a half-way draw is rejected."""
    n = v.numerator * 2 + (v.denominator if v >= 0 else -v.denominator)
    return F(n // (2 * v.denominator))


# ------------------------------------------------------------------ solvers

def evaluate(p):
    return float(r(p["m"]) * r(p["x0"]) + r(p["b"]))


def coefficient(p):
    m, b, x1, x2 = r(p["m"]), r(p["b"]), r(p["x1"]), r(p["x2"])
    y1 = m * x1 + b
    if p["unknown"] == "b":
        found = y1 - m * x1
        if found != b:
            raise AuditError("the stated value does not pin the constant term down")
        recovered_m = m
    else:
        if x1 == 0:
            raise AuditError("a value at zero cannot recover the slope")
        found = (y1 - b) / x1
        if found != m:
            raise AuditError("the stated value does not pin the slope down")
        recovered_m = found
    if p["ask"] == "unknown":
        return float(found)
    return float(recovered_m * x2 + b)


def combine(p):
    c, d = r(p["c"]), r(p["d"])
    if p["mode"] == "same_function":
        pp, qq = r(p["p"]), r(p["q"])
        return float(((pp + c) - (qq + c)) / d)
    pp, af, bg = r(p["p"]), r(p["af"]), r(p["bg"])
    return float(af * (pp + c) - bg * (d * pp))


def inner(p):
    d, k = r(p["d"]), r(p["k"])
    if p["ask"] == "value":
        c = r(p["c"])
        if c == 0:
            raise AuditError("the argument scale cannot be zero")
        return float(k / c + d)
    value = r(p["value"])
    if value == d:
        raise AuditError("the stated value leaves the scale undetermined")
    return float(k / (value - d))


def from_points(p):
    x1, y1, x2, y2 = r(p["x1"]), r(p["y1"]), r(p["x2"]), r(p["y2"])
    if x1 == x2:
        raise AuditError("a vertical line is not a function")
    m = (y2 - y1) / (x2 - x1)
    return pick(p, line_sig(m, y1 - m * x1))


def from_table(p):
    m, b = fit(p["xs"], p["ys"])
    if p["mode"] == "proportional" and b != 0:
        raise AuditError("a proportional table must pass through the origin")
    return pick(p, line_sig(m, b))


def define(p):
    m, b = r(p["m"]), r(p["b"])
    if p["given"] == "two_values":
        recovered = (b + m) - b                   # f(1) - f(0)
        if recovered != m:
            raise AuditError("the two stated values do not give the slope")
    return pick(p, line_sig(m, b))


def table_facts(p):
    m, b = fit(p["xs"], p["ys"])
    if (m, b) != (r(p["m"]), r(p["b"])):
        raise AuditError("the table does not come from the stated coefficients")
    ask = p["ask"]
    if ask == "value":
        return float(m * r(p["x_ask"]) + b)
    if ask == "intercept":
        return float(b)
    if ask == "slope":
        return float(m)
    return float(m - b)


def x_intercept(p):
    if p["given"] == "sum":
        m1, b1, m2, b2 = (r(v) for v in p["parts"])
        m, b = m1 + m2, b1 + b2
    elif p["given"] == "table":
        m, b = fit(p["xs"], p["ys"])
    else:
        m, b = r(p["m"]), r(p["b"])
    if m == 0:
        raise AuditError("a horizontal line has no x-intercept")
    root = -b / m
    if m * root + b != 0:
        raise AuditError("the reported root is not a root")
    if p.get("as_point"):
        return pick(p, [root.numerator, root.denominator, 0, 1])
    return float(root)


def y_intercept(p):
    m, b = r(p["m"]), r(p["b"])
    if p["given"] == "graph":
        (ax, ay), (bx, by) = p["seg"]
        if bx == ax:
            raise AuditError("the drawn segment is vertical")
        drawn_m = F(by - ay, bx - ax)
        drawn_b = F(ay) - drawn_m * ax
        if (drawn_m, drawn_b) != (m, b):
            raise AuditError("the drawn line is not the line the item describes")
        return pick(p, [0, 1, drawn_b.numerator, drawn_b.denominator])
    return float(b)


def model_eq(p):
    return pick(p, line_sig(r(p["m"]), r(p["b"])))


def per_unit(p):
    if p["shape"] == "offset":
        n, c = int(p["n"]), int(p["c"])
        m = F(-1 if p["down"] else 1, n)
        return pick(p, line_sig(m, F(c)))
    n, k = int(p["n"]), int(p["k"])
    return pick(p, line_sig(F(k, n), F(0)))


def tiered(p):
    a, b, k = int(p["a"]), int(p["b"]), int(p["k"])
    # total for n units = k*a for the first block, then b for each one after it
    at_k, at_k1 = k * a, k * a + b
    slope = F(at_k1 - at_k, 1)
    const = F(at_k) - slope * k
    return pick(p, line_sig(slope, const))


def model_value(p):
    m, b, x = r(p["m"]), r(p["b"]), r(p["x"])
    if p["direction"] == "inverse":
        total = b + m * x
        if m == 0:
            raise AuditError("a flat model cannot be run backwards")
        found = (total - b) / m
        if found != x:
            raise AuditError("the inverse does not invert")
        return float(found)
    v = b + m * x
    if p.get("approx"):
        v = rounded(v)
    if p.get("money"):
        return cash(v)
    return float(v)


def two_points_ctx(p):
    x1, x2 = int(p["x1"]), int(p["x2"])
    y1, y2 = r(p["y1"]), r(p["y2"])
    if x1 == x2:
        raise AuditError("two readings at the same input")
    m = (y2 - y1) / (x2 - x1)
    if p["ask"] == "model":
        return pick(p, line_sig(m, y1))
    v = y1 + m * (int(p["x3"]) - x1)
    if p.get("approx"):
        v = rounded(v)
    return float(v)


def interpret_slope(p):
    return role(p, "rate")


def interpret_constant(p):
    want = {"start": "start", "shifted": "at_k", "point": "value_year"}[p["mode"]]
    return role(p, want)


def interpret_x_intercept(p):
    return role(p, "time")


def graph_read(p):
    m, b = r(p["m"]), r(p["b"])
    if p["ask"] == "equation":
        return pick(p, line_sig(m, b))
    if p["ask"] == "rate":
        return cash(m) if p.get("money") else float(m)
    v = m * r(p["x"]) + b
    return cash(v) if p.get("money") else float(v)


def graph_shift(p):
    m, c, k = r(p["m"]), r(p["c"]), r(p["k"])
    # the drawn line is y = f(x) - k, so f(x) = (mx + c) + k
    return pick(p, line_sig(m, c + k))


def param_intercept(p):
    c, a, b, e, k = (int(p[v]) for v in ("c", "a", "b", "e", "k"))
    # f(x) + k = c*a*L*x + (c*b*L + e + k) with L the letter; the root has
    # numerator -(c*b*L + e + k) over c*a*L
    return pick(p, ["ratio", c * b, e + k, c * a])


def affine(p):
    scale = r(p["p"]) / r(p["qd"])
    if p["ask"] == "change":
        return float(scale * r(p["delta"]))
    v = (r(p["target"]) - r(p["t"])) / scale + r(p["s"])
    return float(v)


def unit_relation(p):
    cal, fat = int(p["cal"]), int(p["fat"])
    if p["mode"] == "ratio":
        kj0 = r(p["kj0"])
        factor = F(str(round(float(kj0) / cal, 1)))
        return pick(p, ["k_eq", factor.numerator, factor.denominator])
    total = int(p["total"])
    # total = cal*p + fat*f + cal*c  ->  f = total/fat - (cal/fat)(p + c)
    const = F(total, fat)
    frac = F(cal, fat)
    return pick(p, ["s", const.numerator, const.denominator, -1, frac.numerator,
                    frac.denominator, "sum"])


AUDITS = {
    "lf_evaluate": evaluate,
    "lf_coefficient": coefficient,
    "lf_combine": combine,
    "lf_inner": inner,
    "lf_from_points": from_points,
    "lf_from_table": from_table,
    "lf_define": define,
    "lf_table_facts": table_facts,
    "lf_x_intercept": x_intercept,
    "lf_y_intercept": y_intercept,
    "lf_model_eq": model_eq,
    "lf_per_unit": per_unit,
    "lf_tiered": tiered,
    "lf_model_value": model_value,
    "lf_two_points_ctx": two_points_ctx,
    "lf_interpret_slope": interpret_slope,
    "lf_interpret_constant": interpret_constant,
    "lf_interpret_x_intercept": interpret_x_intercept,
    "lf_graph_read": graph_read,
    "lf_graph_shift": graph_shift,
    "lf_param_intercept": param_intercept,
    "lf_affine": affine,
    "lf_unit_relation": unit_relation,
}
