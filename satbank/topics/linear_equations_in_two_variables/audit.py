"""Independent re-derivation of every Linear Equations in Two Variables answer.

Written from the algebra, not from the generators. Nothing here imports the
topic's own rendering or its families: a slope is recomputed from the two
points, a table is re-fitted row by row and checked at every row, a drawn line
is re-read off the segment that was recorded rather than off the numbers the
stem printed, and the written options are identified by the coefficients they
encode rather than by the string the generator produced.

A wrong answer therefore has to be produced twice, by two separately written
pieces of code, to escape.
"""

from __future__ import annotations

from fractions import Fraction as F
from math import gcd

from ...audit import AuditError

__all__ = ["AUDITS"]


# ------------------------------------------------------------------ helpers

def r(v) -> F:
    """A [numerator, denominator] pair from params back to an exact rational."""
    return F(int(v[0]), int(v[1]))


def S(*vals) -> list:
    """The signature convention: a role name as itself, a number as num, den."""
    out: list = []
    for v in vals:
        if isinstance(v, str):
            out.append(v)
            continue
        f = F(v)
        out += [f.numerator, f.denominator]
    return out


def pick(p: dict, want: list) -> str:
    """The option whose recorded signature is the one the algebra produces."""
    want = list(want)
    hits = [i for i, s in enumerate(p["sigs"]) if list(s) == want]
    if len(hits) != 1:
        raise AuditError(f"signature {want} matches {len(hits)} of {p['sigs']}")
    return p["texts"][hits[0]]


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


def reduce_std(m: F, b: F) -> tuple[F, F, F]:
    """y = mx + b written as Ax + By = C with whole, coprime coefficients."""
    d = m.denominator * b.denominator // gcd(m.denominator, b.denominator)
    A = m.numerator * (d // m.denominator)
    B = -d
    C = -b.numerator * (d // b.denominator)
    g = gcd(gcd(abs(A), abs(B)), abs(C)) or 1
    A, B, C = A // g, B // g, C // g
    if A < 0 or (A == 0 and B < 0):
        A, B, C = -A, -B, -C
    return F(A), F(B), F(C)


def lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(abs(a), abs(b))


# ------------------------------------------------------------------ solvers

def model(p):
    a, b, c = r(p["a"]), r(p["b"]), r(p["c"])
    if p["shape"] == "grouped":
        a2 = F(int(p["n1"]) * int(p["s1"]))
        b2 = F(int(p["n2"]) * int(p["s2"]))
        if (a2, b2) != (a, b):
            raise AuditError("the coefficients are not the sides times the counts")
    elif p["shape"] == "split_total":
        if (a, b) != (1, -1):
            raise AuditError("a total split in two is one of each, one taken away")
    return pick(p, S("std", a, b, c))


def percent(p):
    mode = p["mode"]
    da, db = F(int(p["pa"]), 100), F(int(p["pb"]), 100)
    if mode == "growth":
        da, db = 1 + da, 1 + db
    if mode == "weight":
        rhs = S("plain", r(p["c"]))
    else:
        v, pm = r(p["v"]), F(int(p["pm"]), 100)
        if mode == "mixture":
            if pm * v != r(p["c"]):
                raise AuditError("the blend's own content does not match the right side")
            rhs = S("prod", pm, v)
        else:
            g = 1 + pm
            if g * v != r(p["c"]):
                raise AuditError("the grown total does not match the right side")
            rhs = S("scaled", v, g)
    return pick(p, S("p", da, db) + rhs)


def material(p):
    if p["ask"] == "interpret":
        xi, yi = int(p["xi"]), int(p["yi"])
        rest = sorted(set(range(4)) - {xi, yi})
        if len(rest) != 2:
            raise AuditError("the equation must leave exactly two rock types unpriced")
        return pick(p, S("pairnamed", rest[0], rest[1]))
    left = F(int(p["total"]) - int(p["known"]))
    if left <= 0:
        raise AuditError("the weighed-out rock cannot outweigh the garden")
    return pick(p, S("std", F(int(p["dx"])), F(int(p["dy"])), left))


def coefficient(p):
    a, b = r(p["a"]), r(p["b"])
    if p["ask"] == "difference":
        return float(abs(b - a))
    if p["ask"] == "expression":
        return pick(p, S("coef", "x"))
    if p["ask"] == "variable":
        return pick(p, S("rate", p["which"]))
    queried = r(p["queried"])
    hits = [name for name, v in (("x", a), ("y", b)) if v == queried]
    if len(hits) != 1:
        raise AuditError(f"the number asked about matches {len(hits)} coefficients")
    return pick(p, S("rate", hits[0]))


def constant(p):
    if p["mode"] == "total":
        return pick(p, S("total", "both"))
    if r(p["b"]) == r(p["a"]):
        raise AuditError("the two terms cannot be told apart")
    return pick(p, S("amount", "y"))


def point(p):
    x, y = r(p["x"]), r(p["y"])
    if p["mode"] == "pair":
        if r(p["a"]) * x + r(p["b"]) * y != r(p["c"]):
            raise AuditError("the pair does not satisfy the equation")
        return pick(p, S("xy", "yn"))
    if 2 * (x + y) != r(p["p"]):
        raise AuditError("the point is not on the perimeter line")
    return pick(p, S("direct", "xy"))


def substitute(p):
    a, b, c, g = r(p["a"]), r(p["b"]), r(p["c"]), r(p["given"])
    if p["form"] == "solved":
        return float(a * g)
    if p["solve"] == "y":
        if b == 0:
            raise AuditError("the variable asked for has vanished")
        found = (c - a * g) / b
        if a * g + b * found != c:
            raise AuditError("the value found does not satisfy the equation")
    else:
        if a == 0:
            raise AuditError("the variable asked for has vanished")
        found = (c - b * g) / a
        if a * found + b * g != c:
            raise AuditError("the value found does not satisfy the equation")
    return float(found)


def context(p):
    shape = p["shape"]
    if shape == "counts":
        a, b, c, g = r(p["a"]), r(p["b"]), r(p["c"]), r(p["given"])
        if a == 0:
            raise AuditError("the quantity asked for has no rate")
        found = (c - b * g) / a
        if a * found + b * g != c:
            raise AuditError("the value found does not satisfy the situation")
        return float(found)
    if shape == "ratio":
        a, b, c, k = r(p["a"]), r(p["b"]), r(p["c"]), r(p["k"])
        base = c / (a + k * b)
        if a * base + b * k * base != c:
            raise AuditError("the two purchases do not come to the total")
        return float(k * base)
    n1, n2, u1, c = int(p["n1"]), int(p["n2"]), r(p["u1"]), r(p["c"])
    if n2 == 0:
        raise AuditError("nothing to divide the remainder between")
    found = (c - n1 * u1) / n2
    if n1 * u1 + n2 * found != c:
        raise AuditError("the parts do not come to the whole")
    return float(found)


def mixture(p):
    p1, p2, pm, v = int(p["p1"]), int(p["p2"]), int(p["pm"]), r(p["v"])
    if p1 == pm:
        raise AuditError("a solution at the blend's own strength changes nothing")
    x = v * F(pm - p2, p1 - pm)
    if F(p1, 100) * x + F(p2, 100) * v != F(pm, 100) * (x + v):
        raise AuditError("the salt does not balance")
    return float(x)


def slope_form(p):
    m = F(int(p["p"]), int(p["d"]))
    if p["form"] == "grouped":
        m += int(p["s"])
    return float(m)


def par_perp(p):
    relation = p["relation"]
    if p["form"] == "axis":
        flat = (p["vertical"] and relation == "perpendicular") or \
               (not p["vertical"] and relation == "parallel")
        if not flat:
            raise AuditError("a line perpendicular to a horizontal one has no slope")
        return pick(p, S("zero"))
    if p["form"] == "slope_intercept":
        m = r(p["m"])
    else:
        A, B = r(p["A"]), r(p["B"])
        if B == 0:
            raise AuditError("a line with no y term has no slope")
        m = -A / B
    if m == 0:
        raise AuditError("a horizontal line has no perpendicular with a slope")
    want = m if relation == "parallel" else -1 / m
    if relation == "perpendicular" and want * m != -1:
        raise AuditError("the two slopes are not perpendicular")
    if p.get("ask") == "equation":
        A, B, C = reduce_std(want, r(p["bi"]))
        return pick(p, S("std", A, B, C))
    return float(want)


def two_points(p):
    x1, y1, x2, y2 = r(p["x1"]), r(p["y1"]), r(p["x2"]), r(p["y2"])
    if x1 == x2:
        raise AuditError("a vertical line has no slope")
    m = (y2 - y1) / (x2 - x1)
    if m == 0:
        raise AuditError("a horizontal line leaves the perpendicular undefined")
    return float(m if p["ask"] == "slope" else -1 / m)


def point_on_line(p):
    if p["ask"] == "constant":
        c, x1, y1, y2 = r(p["c"]), r(p["x1"]), r(p["y1"]), r(p["y2"])
        if y2 == 0:
            raise AuditError("the point on the y-axis pins nothing down")
        k = c / y2
        if x1 == 0:
            raise AuditError("the second point must be off the y-axis")
        a = (c - k * y1) / x1
        if a * x1 + k * y1 != c or k * y2 != c:
            raise AuditError("the two constants do not put both points on the line")
        return float(k)
    if p["mode"] == "two_points":
        b, x1, y1, x3 = r(p["b"]), r(p["x1"]), r(p["y1"]), r(p["x3"])
        if x1 == 0:
            raise AuditError("the second point sits on the y-axis too")
        m = (y1 - b) / x1
        return float(m * x3 + b)
    m, x3 = r(p["m"]), r(p["x3"])
    return float(m * x3)


def line_equation(p):
    m, b = r(p["m"]), r(p["b"])
    if p["given"] == "two_points":
        x2, y2 = r(p["x2"]), r(p["y2"])
        if x2 == 0:
            raise AuditError("the second point is on the y-axis as well")
        found = (y2 - b) / x2
        if found != m:
            raise AuditError("the two points do not give the stated slope")
    return pick(p, S("line", m, b))


def intercepts(p):
    mode = p["mode"]
    if mode == "equation_y":
        return float(r(p["b"]))
    if mode == "standard_x":
        A, C = r(p["A"]), r(p["C"])
        if A == 0:
            raise AuditError("the line never meets the x-axis")
        root = C / A
        if A * root != C:
            raise AuditError("the root found is not a root")
        return float(root)
    if mode == "ratio":
        A, B, C = r(p["A"]), r(p["B"]), r(p["C"])
        if A == 0 or B == 0:
            raise AuditError("the line misses one of the axes")
        a, b = C / A, C / B
        if a == 0:
            raise AuditError("the x-intercept is at the origin")
        return float(b / a)
    (ax, ay), (bx, by) = p["seg"]
    if bx == ax:
        raise AuditError("the drawn segment is vertical")
    m = F(by - ay, bx - ax)
    b = F(ay) - m * ax
    if (m, b) != (r(p["m"]), r(p["b"])):
        raise AuditError("the drawn line is not the line the item describes")
    return pick(p, S("pt", 0, b))


def equivalent(p):
    a, b, c, k = r(p["a"]), r(p["b"]), r(p["c"]), r(p["k"])
    if a == 0 or k < 2:
        raise AuditError("the second equation must be a genuine multiple of the first")
    # y = t puts x at (c - b*t)/a for every t, so the point is ((-b/a)t + c/a, t)
    t = F(3, 7)
    x = (c - b * t) / a
    if a * x + b * t != c or k * a * x + k * b * t != k * c:
        raise AuditError("the parameterised point does not satisfy both equations")
    return pick(p, S("x_first", -b / a, c / a))


def graph_line(p):
    if p["ask"] == "parameter":
        xi, yi = int(p["xi"]), int(p["yi"])
        C = F(lcm(xi, yi) * int(p["scale"]))
        A = C / xi
        if A * xi != C:
            raise AuditError("the x-intercept does not give a whole coefficient")
        return pick(p, S("param", A, C, "num_x"))
    if p["ask"] == "shifted":
        m, b, k = r(p["m"]), r(p["b"]), r(p["k"])
        return pick(p, S("fn", m, b - k))
    (ax, ay), (bx, by) = p["seg"]
    if bx == ax:
        raise AuditError("the drawn segment is vertical")
    m = F(by - ay, bx - ax)
    b = F(ay) - m * ax
    if (m, b) != (r(p["m"]), r(p["b"])):
        raise AuditError("the drawn line is not the line the options describe")
    return pick(p, S("line", m, b))


def combo(p):
    xi, yi = int(p["xi"]), int(p["yi"])
    ask = p["ask"]
    if ask == "value":
        c = r(p["c"])
        x = r(p["x"])
        pa, pb = c / xi, c / yi
        if pb == 0:
            raise AuditError("the second item is free")
        found = (c - pa * x) / pb
        if pa * x + pb * found != c:
            raise AuditError("the two purchases do not come to the total")
        return float(found)
    if ask == "equation":
        C = F(lcm(xi, yi))
        return pick(p, S("std", C / xi, C / yi, C))
    if ask == "total":
        return float(r(p["rate"]) * xi)
    return float(r(p["c"]) / xi)


def table_equation(p):
    m, b = fit(p["xs"], p["ys"])
    if p["form"] == "standard":
        A, B, C = reduce_std(m, b)
        k = r(p["k"])
        return pick(p, S("std", k * A, k * B, k * C))
    return pick(p, S("line", m, b))


def which_table(p):
    xs = [r(v) for v in p["xs"]]
    if p["form"] == "slope_intercept":
        m, b = r(p["m"]), r(p["b"])
        ys = [m * x + b for x in xs]
    else:
        A, B, C = r(p["A"]), r(p["B"]), r(p["C"])
        if B == 0:
            raise AuditError("the equation does not determine y")
        ys = [(C - A * x) / B for x in xs]
        for x, y in zip(xs, ys):
            if A * x + B * y != C:
                raise AuditError(f"the pair at x = {x} is not on the line")
    return pick(p, S("pairs", *xs, *ys))


def table_symbolic(p):
    if p["ask"] == "slope":
        step, d = int(p["step"]), int(p["d"])
        if step == 0:
            raise AuditError("the table's inputs do not move")
        # the outputs are n + 2d, n + d, n at x = -2s, -s, 0: the n cancels
        return pick(p, S("plain", F(-d, step)))
    m, x1, y1, y2, x3 = (r(p["m"]), r(p["x1"]), r(p["y1"]), r(p["y2"]), r(p["x3"]))
    if m == 0:
        raise AuditError("a flat line does not fix the missing input")
    b = y1 - m * x1
    k = (y2 - b) / m
    n = m * x3 + b
    if m * k + b != y2:
        raise AuditError("the missing input does not give the stated output")
    return float(k + n)


def table_line(p):
    if p["ask"] == "value":
        x1, y1, x2, y2 = r(p["x1"]), r(p["y1"]), r(p["x2"]), r(p["y2"])
        if x1 == x2:
            raise AuditError("the two rows share an input")
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        return float(m * r(p["x3"]) + b)
    m, b = fit(p["xs"], p["ys"])
    k = r(p["k"])
    if m == 0:
        raise AuditError("a flat line has no x-intercept")
    root = -(b - k) / m
    if m * root + (b - k) != 0:
        raise AuditError("the reported intercept is not an intercept")
    return pick(p, S("pt", root, 0))


AUDITS = {
    "le2_model": model,
    "le2_percent": percent,
    "le2_material": material,
    "le2_coef": coefficient,
    "le2_const": constant,
    "le2_point": point,
    "le2_substitute": substitute,
    "le2_context": context,
    "le2_mixture": mixture,
    "le2_slope_form": slope_form,
    "le2_par_perp": par_perp,
    "le2_two_points": two_points,
    "le2_point_on_line": point_on_line,
    "le2_line_equation": line_equation,
    "le2_intercepts": intercepts,
    "le2_equivalent": equivalent,
    "le2_graph_line": graph_line,
    "le2_combo": combo,
    "le2_table_equation": table_equation,
    "le2_which_table": which_table,
    "le2_table_symbolic": table_symbolic,
    "le2_table_line": table_line,
}
