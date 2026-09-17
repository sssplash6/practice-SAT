"""Independent re-derivation of every Nonlinear Functions answer.

Written from the mathematics, not from the generators. Nothing here imports
the topic's families or its renderers: exponentials are rebuilt from the
percent the stem states, vertices are found by completing the square or by
averaging the zeros, the constant term of a cubic is the product of its roots,
and a written option is identified by the signature its mathematics produces
rather than by the string a template happened to print.

A wrong answer therefore has to be produced twice, by two separately written
pieces of code, to escape.
"""

from __future__ import annotations

import math
from fractions import Fraction as F

from ...audit import AuditError

__all__ = ["AUDITS"]


# ------------------------------------------------------------------ helpers

def r(v) -> F:
    """A [numerator, denominator] pair from params back to an exact rational."""
    return F(int(v[0]), int(v[1]))


def S(*vals) -> list:
    """The signature encoding the templates use: a rational becomes [n, d]."""
    out: list = []
    for v in vals:
        if isinstance(v, str):
            out.append(v)
        else:
            f = F(v)
            out += [f.numerator, f.denominator]
    return out


def pick(p: dict, want: list) -> str:
    """The printed option whose recorded signature is the one the algebra gives."""
    want = list(want)
    hits = [i for i, s in enumerate(p["sigs"]) if list(s) == want]
    if len(hits) != 1:
        raise AuditError(f"signature {want} matches {len(hits)} of {p['sigs']}")
    return p["texts"][hits[0]]


def isqrt_exact(v: F) -> F:
    """The exact square root of a rational square, or an error."""
    if v < 0:
        raise AuditError("square root of a negative number")
    n, d = math.isqrt(v.numerator), math.isqrt(v.denominator)
    if n * n != v.numerator or d * d != v.denominator:
        raise AuditError(f"{v} is not a perfect square")
    return F(n, d)


def nth_root(v: F, n: int) -> F:
    """The exact nth root of a positive rational, or an error."""
    if v <= 0:
        raise AuditError("root of a non-positive number")
    a = round(float(v.numerator) ** (1.0 / n))
    b = round(float(v.denominator) ** (1.0 / n))
    if a ** n != v.numerator or b ** n != v.denominator:
        raise AuditError(f"{v} is not an exact {n}th power")
    return F(a, b)


def roots_of(b: F, c: F) -> list:
    """The two roots of x² + bx + c, exactly, smallest first."""
    disc = b * b - 4 * c
    root = isqrt_exact(disc)
    return sorted([(-b - root) / 2, (-b + root) / 2])


# ------------------------------------------------------------- evaluating

def evaluate(p):
    form, x0 = p["form"], r(p["x0"])
    if form == "poly_k":
        return float(x0 ** int(p["n"]) + r(p["k"]))
    if form == "cubic":
        c = [r(v) for v in p["coef"]]
        return float(sum(c[i] * x0 ** i for i in range(len(c))))
    if form == "radical":
        return float(r(p["k"]) + isqrt_exact(x0))
    if form == "rational":
        if x0 == 0:
            raise AuditError("the rule is undefined at zero")
        return float(r(p["k"]) / x0)
    if form == "ratio_quad":
        bottom = x0 + r(p["d"])
        if bottom == 0:
            raise AuditError("the quotient is undefined at that input")
        return float((x0 ** 2 + r(p["b"]) * x0 + r(p["c"])) / bottom)
    if form == "product":
        return float((x0 + r(p["p"]) * x0) * (r(p["q"]) - x0))
    raise AuditError(f"unknown evaluate form {form!r}")


def exp_evaluate(p):
    base, x0 = r(p["base"]), r(p["x0"])
    if x0.denominator != 1:
        raise AuditError("a whole-number exponent is expected here")
    return float(r(p["a"]) * base ** int(x0))


def solve_value(p):
    if p["mode"] == "power":
        k, m, target = r(p["k"]), int(p["m"]), r(p["target"])
        if k == 0:
            raise AuditError("the coefficient cannot be zero")
        return float(nth_root(target / k, m))
    mass, energy = r(p["mass"]), r(p["energy"])
    if mass <= 0:
        raise AuditError("a mass must be positive")
    return float(isqrt_exact(2 * energy / mass))


def param_value(p):
    K, v, m = r(p["K"]), r(p["v"]), r(p["m"])
    if v == 0:
        raise AuditError("the stated value cannot be zero")
    c = K / (2 * v)
    if c == 0:
        raise AuditError("the hidden constant cannot be zero")
    return float(((m - c) ** 2 + K) / (2 * c))


def abs_value(p):
    if p["mode"] == "compose":
        a, b, pp, d, e = r(p["a"]), r(p["b"]), r(p["p"]), r(p["d"]), r(p["e"])
        c = pp + abs(-b * a - a ** 2)
        if c == d:
            raise AuditError("the second function is undefined there")
        return float(abs(-c / (c - d)) - c + e)
    t, m, k = r(p["t"]), int(p["m"]), int(p["k"])
    return float((m + t) * (k + t))


# ------------------------------------------------------------- intercepts

def y_intercept(p):
    mode = p["mode"]
    if mode == "poly":
        return float(r(p["k"]))
    if mode == "expo":
        return pick(p, S(0, r(p["a"])))
    return pick(p, S(0))


def x_intercept(p):
    mode = p["mode"]
    if mode == "factored":
        z = [r(v) for v in p["roots"]]
        again = roots_of(-(z[0] + z[1]), z[0] * z[1])
        return float(again[0])
    if mode == "standard":
        lo, _ = roots_of(r(p["b"]), r(p["c"]))
        return pick(p, S(lo, 0))
    if mode == "not":
        m, r3 = r(p["m"]), r(p["r3"])
        if r3 == 0:
            raise AuditError("the third factor has no constant term")
        return pick(p, S(-m / r3, 0))
    return float(2 * r(p["h"]))


# ----------------------------------------------------------------- graphs

def _drawn_intercept(p) -> F:
    shape = p["shape"]
    if shape == "exp_asymptote":
        return F(int(p["c"]) - int(p["d"]))
    if shape in ("exp_decay", "exp_growth"):
        return F(int(p["a"]))
    if shape == "flat_poly":
        return F(int(p["c"]))
    if shape == "rational":
        return F(int(p["a"]), int(p["d"]))
    raise AuditError(f"unknown drawn shape {shape!r}")


def graph_intercept(p):
    y0 = _drawn_intercept(p)
    if "texts" in p:
        return pick(p, S(0, y0))
    return float(y0)


def graph_context(p):
    return float(p["a"] if p["mode"] == "start" else p["peak"])


def graph_zeros(p):
    crosses = (int(p["a"]) > 0) != (int(p["c"]) > 0)
    return pick(p, S(1 if crosses else 0))


def graph_equation(p):
    return pick(p, S(int(p["r"]), int(p["p"]), "second"))


# ----------------------------------------------------------- exponentials

def exp_model(p):
    rr = r(p["r"])
    factor = 1 + rr if p["shape"] in ("growth", "double") else 1 - rr
    return pick(p, S(int(p["a"]), factor, p["var"]))


def exp_period(p):
    k = int(p["k"])
    if p["mode"] == "gather":
        return pick(p, S(int(p["a"]), 1 + r(p["r"]), f"/{k}"))
    return pick(p, S(int(p["a"]), r(p["factor"]), f"/{k}"))


def exp_table(p):
    if p["mode"] == "money":
        return pick(p, S(int(p["a"]), 1 + r(p["r"]), "t"))
    return pick(p, S(int(p["a"]), int(p["base"]), "-x"))


def exp_offset(p):
    return pick(p, S(int(p["diff"]), r(p["f"]), f"/{int(p['k'])}", "amb"))


def exp_anchor(p):
    factor = r(p["factor"])
    if factor == 0:
        raise AuditError("a growth factor cannot be zero")
    return pick(p, S(F(int(p["v"])) / factor, factor))


def exp_reach(p):
    return pick(p, S(int(p["b"]), int(p["a"]), r(p["factor"])))


def exp_rate(p):
    mode = p["mode"]
    if mode == "base_from_percent":
        return float(1 + r(p["r"]))
    if mode == "percent_from_period":
        return float(100 * (1 - r(p["base"])))
    return pick(p, S(1 if p["rising"] else -1))


def exp_two_points(p):
    mode = p["mode"]
    if mode == "shifted":
        b = r(p["v"]) + 1 + r(p["shift"])
        if b == 0:
            raise AuditError("the second constant cannot be zero")
        return float(r(p["prod"]) / b)
    if mode == "intercepts":
        return float(r(p["v"]) - 1)
    b = r(p["p"]) - 1
    tail = r(p["v"]) - b
    if tail <= 0:
        raise AuditError("the second point is below the horizontal asymptote")
    a = nth_root(1 / tail, int(p["e"]))
    return float(a * b)


def exp_display(p):
    base = r(p["base"])

    def shows(form, sh, c):
        """Does the value at x = 0 equal the number printed in front?"""
        if form == "plain":
            return True
        if form == "shift_up":
            return base ** sh == 1
        c = r(c) if c is not None else base ** sh
        return (c * base ** (-sh) == 1) if form == "coef_down" \
            else (c * base ** sh == 1)

    one = shows(p["form1"], int(p["s1"]), p["c1"])
    two = shows(p["form2"], int(p["s2"]), p["c2"])
    return pick(p, S(1 if one else 0, 1 if two else 0))


def exp_rewrite(p):
    if p["mode"] == "yintercept":
        N = int(p["m"]) ** int(p["j"])
        return pick(p, S(N ** int(p["kk"]), "base"))
    return pick(p, S(int(p["m"]) ** int(p["i"]), F(1, int(p["c"]))))


def exp_steps(p):
    if p["ask"] == "value":
        if p["mode"] == "bounce":
            return float(r(p["a"]) / F(int(p["den"])) ** int(p["n"]))
        return float(r(p["a"]) * (1 - r(p["r"])) ** int(p["n"]))
    if p["mode"] == "moore":
        return float(int(p["y0"]) + int(p["k"]) * int(p["power"]))
    return pick(p, S(int(p["power"]) + 1))


# -------------------------------------------------------------- parabolas

def vertex(p):
    form, ask = p["form"], p["ask"]
    if form == "fan":
        return float(r(p["h"]))
    if form == "tickets":
        a, b = r(p["a"]), r(p["b"])
        if a == 0:
            raise AuditError("a parabola needs a nonzero leading coefficient")
        return float(-b / (2 * a))
    if form == "vertex":
        return float(r(p["k"]) if ask == "value" else r(p["h"]))
    if form == "standard":
        a, b, c = r(p["a"]), r(p["b"]), r(p["c"])
        if a == 0:
            raise AuditError("a parabola needs a nonzero leading coefficient")
        h = -b / (2 * a)
        return float(h if ask == "location" else a * h * h + b * h + c)
    r1, r2 = r(p["r1"]), r(p["r2"])
    if ask == "interval":
        mid = (r1 + r2) / 2
        cuts = [r(c) for c in p["cuts"]]
        holds = [i for i in range(len(cuts) - 1) if cuts[i] < mid < cuts[i + 1]]
        if len(holds) != 1:
            raise AuditError("the vertex does not lie in exactly one printed interval")
        return pick(p, S(cuts[holds[0]], cuts[holds[0] + 1]))
    mid = (r1 + r2) / 2
    return float(mid if ask == "location" else (mid - r1) * (mid - r2))


def symmetry(p):
    if p["mode"] == "other_intercept":
        return pick(p, S(2 * r(p["h"]) - r(p["given"]), 0))
    return float((r(p["r1"]) + r(p["r2"])) / 2)


def shift_max(p):
    return pick(p, S(r(p["k"]), r(p["a"])))


def must_be_true(p):
    b, pp, qv, t = r(p["b"]), r(p["p"]), r(p["q"]), r(p["t"])
    h = (pp + qv) / 2
    if h == 0:
        raise AuditError("the axis of symmetry must not sit on the y-axis")
    a = -b / (2 * h)
    if a <= 0:
        raise AuditError("the parabola must open upward")
    first = {"c_neg": False, "a_pos": True, "h_neg": h < 0}[p["first"]]
    return pick(p, S(1 if first else 0, 1 if a >= t else 0))


def quad_fit(p):
    mode = p["mode"]
    if mode == "vertex_value":
        a, h, t, y0 = r(p["a"]), r(p["h"]), r(p["t"]), r(p["y0"])
        k = y0 - a * h ** 2
        return float(k + a * (t - h) ** 2)
    if mode == "vertex_equation":
        a, h = r(p["a"]), r(p["h"])
        return pick(p, S(-a, h, -a * h ** 2))
    if mode == "three_points":
        t1, d1, t2, d2, t3 = (r(p["t1"]), r(p["d1"]), r(p["t2"]), r(p["d2"]),
                              r(p["t3"]))
        det = t1 ** 2 * t2 - t2 ** 2 * t1
        if det == 0:
            raise AuditError("the two readings do not pin a parabola down")
        a = (d1 * t2 - d2 * t1) / det
        b = (d1 - a * t1 ** 2) / t1
        return float(a * t3 ** 2 + b * t3)
    x0, step, a, peak = r(p["x0"]), r(p["step"]), r(p["a"]), r(p["peak"])
    if step == 0:
        raise AuditError("the table must show three different inputs")
    return float(a * x0 ** 2 + peak)


# ------------------------------------------------------------ in words

def interpret_value(p):
    ctx = p["ctx"]
    t = r(p["t"])
    if ctx == "height":
        v = -16 * t ** 2 + r(p["b"]) * t + r(p["a"])
    elif ctx == "isotope":
        v = r(p["a"]) / F(2) ** int(p["steps"])
    else:
        exact = r(p["a"]) * r(p["b"]) ** int(t)
        v = F((exact + F(1, 2)).__floor__())
    return pick(p, S("value", v))


def interpret_initial(p):
    return pick(p, S("start"))


def interpret_rate(p):
    return pick(p, S(int(p["step"]), "percent"))


def quad_feature(p):
    mode = p["mode"]
    if mode == "number":
        return pick(p, S("initial_height"))
    if mode == "kick":
        return float(r(p["c"]))
    if mode == "month":
        return pick(p, S(p["month"], r(p["c"])))
    if mode == "graph":
        return pick(p, S("start", int(p["start"])))
    if mode == "vertex":
        return pick(p, S("min", int(p["k"])))
    if mode == "time":
        return pick(p, S("ground_time"))
    return pick(p, S("zero_price"))


# ------------------------------------------------------------ situations

def quad_word(p):
    mode = p["mode"]
    if mode == "rect_double":
        w = r(p["w"])
        area = 2 * w ** 2
        return float(isqrt_exact(area / 2))
    if mode == "rect_offset":
        w, d = r(p["w"]), r(p["d"])
        area = w * (w - d)
        return float(max(roots_of(-d, -area)))
    if mode == "product":
        w, c, mult = r(p["w"]), r(p["c"]), int(p["mult"])
        product = (mult * w + c) * w
        both = roots_of(c / mult, -product / mult)
        pos = [x for x in both if x > 0]
        if len(pos) != 1:
            raise AuditError("the situation does not have one positive solution")
        other = mult * pos[0] + c
        return float(min(pos[0], other))
    if mode == "triangle":
        w, d = r(p["w"]), r(p["d"])
        area = w * (w + d) / 2
        return float(max(roots_of(d, -2 * area)))
    if mode == "garden":
        w, d = r(p["w"]), r(p["d"])
        area = w * (w + d)
        return float(max(roots_of(d, -area)) + d)
    c, d = r(p["c"]), r(p["d"])
    if c == d:
        raise AuditError("the two offsets must differ")
    return float(c * d / (c - d))


def build_expression(p):
    mode = p["mode"]
    if mode == "length":
        return pick(p, S("w+d"))
    if mode == "product":
        return pick(p, S("dx"))
    if mode == "volume":
        return pick(p, S(int(p["h"]), int(p["d"]), "minus"))
    return pick(p, S(F(4, int(p["den"]))))


def exp_power_table(p):
    step, first, target = int(p["step"]), int(p["first"]), int(p["target"])
    if step == 0:
        raise AuditError("the exponents must change from row to row")
    if (target - first) % step:
        raise AuditError("the target exponent is not one the table's rule reaches")
    return float((target - first) // step + 1)


def factor_table(p):
    return pick(p, S(int(p["z1"]), int(p["z2"])))


def zeros_constant(p):
    a, b, c = (int(v) for v in p["roots"])
    return float(-(a * b * c))


AUDITS = {
    "nlf_evaluate": evaluate,
    "nlf_exp_evaluate": exp_evaluate,
    "nlf_solve_value": solve_value,
    "nlf_param_value": param_value,
    "nlf_abs_value": abs_value,
    "nlf_y_intercept": y_intercept,
    "nlf_x_intercept": x_intercept,
    "nlf_graph_intercept": graph_intercept,
    "nlf_graph_context": graph_context,
    "nlf_graph_zeros": graph_zeros,
    "nlf_graph_equation": graph_equation,
    "nlf_exp_model": exp_model,
    "nlf_exp_period": exp_period,
    "nlf_exp_table": exp_table,
    "nlf_exp_offset": exp_offset,
    "nlf_exp_anchor": exp_anchor,
    "nlf_exp_reach": exp_reach,
    "nlf_exp_rate": exp_rate,
    "nlf_exp_two_points": exp_two_points,
    "nlf_exp_display": exp_display,
    "nlf_exp_rewrite": exp_rewrite,
    "nlf_exp_steps": exp_steps,
    "nlf_vertex": vertex,
    "nlf_symmetry": symmetry,
    "nlf_shift_max": shift_max,
    "nlf_must_be_true": must_be_true,
    "nlf_quad_fit": quad_fit,
    "nlf_interpret_value": interpret_value,
    "nlf_interpret_initial": interpret_initial,
    "nlf_interpret_rate": interpret_rate,
    "nlf_quad_feature": quad_feature,
    "nlf_quad_word": quad_word,
    "nlf_build_expression": build_expression,
    "nlf_factor_table": factor_table,
    "nlf_exp_power_table": exp_power_table,
    "nlf_zeros_constant": zeros_constant,
}
