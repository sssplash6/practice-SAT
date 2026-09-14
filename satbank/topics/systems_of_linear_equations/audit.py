"""Independent re-derivation of every Systems answer.

Nothing here imports a template. Every system is solved by **Cramer's rule** --
two determinants formed from coefficients this file reads off the printed shape
itself -- while the generators solve by **substitution**, isolating a variable in
one equation and putting it into the other. The two routes never touch: a
template that gathers `4x − 6y = 10y + 2` wrongly, or that isolates the wrong
variable, has to be wrong twice, in two separately written pieces of code, to get
out.

The templates whose options are systems or points rather than values are
re-derived the same way: the modelling is done again from the story's numbers and
the sentence is rebuilt from whatever that derivation produces.
"""

from __future__ import annotations

from fractions import Fraction as Q

from ...audit import AuditError

TOL = 1e-9


# ------------------------------------------------------------- reading params

def _q(pair) -> Q:
    """A number as the templates pack it: [numerator, denominator]."""
    return Q(int(pair[0]), int(pair[1]))


def _row(eq) -> tuple:
    """A printed equation as the row (A, B, C) of A·x + B·y = C.

    This is the one piece of reading the generators also do, and it is written
    here from the printed layout rather than copied: `p·v = m·w + b` puts the
    w-term on the left with its sign turned over, whichever of x and y is which.
    """
    if eq[0] == "std":
        return _q(eq[1]), _q(eq[2]), _q(eq[3])
    if eq[0] != "solved":
        raise AuditError(f"unknown equation shape {eq[0]!r}")
    p, v, m, b = _q(eq[1]), eq[2], _q(eq[3]), _q(eq[4])
    return (-m, p, b) if v == "y" else (p, -m, b)


# ---------------------------------------------------------------- Cramer only

def _cramer(r1, r2) -> tuple:
    """The one point two rows share, by determinants. No elimination anywhere."""
    (a1, b1, c1), (a2, b2, c2) = r1, r2
    det = a1 * b2 - a2 * b1
    if det == 0:
        raise AuditError("the two equations do not meet at a single point")
    return (c1 * b2 - c2 * b1) / det, (a1 * c2 - a2 * c1) / det


def _asked(ask: str, x: Q, y: Q, k: Q) -> Q:
    if ask == "x":
        return x
    if ask == "y":
        return y
    if ask == "sum":
        return x + y
    if ask == "diff":
        return x - y
    if ask == "prod":
        return x * y
    if ask == "kx":
        return k * x
    if ask == "k_sum":
        return k * x + k * y
    raise AuditError(f"unknown quantity {ask!r}")


# --------------------------------------------------------- printing, redone

def _n(f, style: str = "frac") -> str:
    """A number as an option prints it. Commas and the shape of the minus sign
    are the normaliser's business, so neither is used here."""
    f = Q(f)
    if f.denominator == 1:
        return str(f.numerator)
    if style == "dec":
        d, twos, fives = f.denominator, 0, 0
        while d % 2 == 0:
            d //= 2
            twos += 1
        while d % 5 == 0:
            d //= 5
            fives += 1
        if d == 1:
            places = max(twos, fives)
            return ("-" if f < 0 else "") + f"{float(abs(f)):.{places}f}"
    return f"{f.numerator}/{f.denominator}"


def _term(c, v: str, style: str = "frac") -> str:
    c = Q(c)
    if c == 1:
        return v
    if c == -1:
        return "-" + v
    if c.denominator != 1 and style != "dec":
        return ("-" if c < 0 else "") + f"({abs(c.numerator)}/{c.denominator}){v}"
    return f"{_n(c, style)}{v}"


def _sum(parts: list) -> str:
    out = parts[0]
    for p in parts[1:]:
        out += f" - {p[1:]}" if p.startswith("-") else f" + {p}"
    return out


def _lin(a, b, vx: str, vy: str, style: str = "frac") -> str:
    parts = [_term(c, v, style) for c, v in ((Q(a), vx), (Q(b), vy)) if Q(c) != 0]
    return _sum(parts) if parts else "0"


def _eq(a, b, c, vx="x", vy="y", style="frac") -> str:
    return f"{_lin(a, b, vx, vy, style)} = {_n(c, style)}"


def _both(e1: str, e2: str) -> str:
    return f"{e1}, {e2}"


def _point(x, y) -> str:
    return f"({_n(x)}, {_n(y)})"


# ------------------------------------------------------------- the solvers

def standard(p: dict) -> float:
    x, y = _cramer(_row(p["e1"]), _row(p["e2"]))
    return float(_asked(p["ask"], x, y, _q(p["k"])))


def pair(p: dict) -> str:
    x, y = _cramer(_row(p["e1"]), _row(p["e2"]))
    return _point(x, y)


def chunk(p: dict) -> float:
    """x + y = S and k(x + y) + m·y = T, read as two rows and solved by Cramer."""
    total, mult = _q(p["total"]), _q(p["mult"])
    coefy, grand = _q(p["coefy"]), _q(p["grand"])
    x, y = _cramer((Q(1), Q(1), total), (mult, mult + coefy, grand))
    return float(x if p["ask"] == "x" else y)


def graph(p: dict):
    m1, b1 = _q(p["m1"]), _q(p["b1"])
    m2, b2 = _q(p["m2"]), _q(p["b2"])
    x, y = _cramer((-m1, Q(1), b1), (-m2, Q(1), b2))
    if p["ask"] == "pair":
        return _point(x, y)
    return _both(_eq(0, 1, y), _eq(1, 0, x))


def model_purchase(p: dict) -> str:
    """Two buyers, so two equations: counts as coefficients, money on the right."""
    vx, vy = p["vx"], p["vy"]
    return _both(_eq(p["p1"], p["q1"], p["t1"], vx, vy),
                 _eq(p["p2"], p["q2"], p["t2"], vx, vy))


def model_total(p: dict) -> str:
    """One equation counts the items, the other adds up what they cost."""
    vx, vy, style = p["vx"], p["vy"], p["style"]
    count = _eq(1, 1, p["n"], vx, vy)
    value = _eq(_q(p["p"]), _q(p["q"]), p["t"], vx, vy, style)
    return _both(count, value) if p["order"] == "count_first" else _both(value, count)


def model_relation(p: dict) -> str:
    vx, vy = p["vx"], p["vy"]
    if p["shape"] == "times_total":
        k, total = Q(p["k"]), Q(p["total"])
        first = f"{vx} = {vy}" if k == 1 else f"{vx} = {_n(k)}{vy}"
        return _both(first, _eq(1, 1, total, vx, vy))
    k, add, gap = Q(p["k"]), Q(p["add"]), Q(p["gap"])
    left = f"x + {_n(add)} = " + ("y" if k == 1 else f"{_n(k)}y")
    return _both(left, f"y = x - {_n(gap)}")


def infinite_constant(p: dict) -> float:
    """Every point in common means both Cramer determinants vanish."""
    a, b, c, k = _q(p["a"]), _q(p["b"]), _q(p["c"]), _q(p["k"])
    if a * (k * b) - (k * a) * b != 0:
        raise AuditError("the two left sides are not proportional")
    # a·L − (k·a)·c = 0 is the determinant that has to vanish for consistency
    if a == 0:
        raise AuditError("no x-term to compare")
    return float((k * a) * c / a)


def infinite_normalized(p: dict) -> float:
    if p["shape"] == "scaled_standard":
        pp, r = _q(p["p"]), _q(p["r"])
        if r == 0:
            raise AuditError("the first equation has no y-term to match")
        # rows (p, r, s) and (A, 1, C): p·1 − A·r = 0
        return float(pp / r)
    m, b = _q(p["m"]), _q(p["b"])
    # rows (−m, 1, b) and (−M, 1, B): the determinant forces M = m, and then the
    # consistency determinant forces B = b
    return float(b if p["ask"] == "b" else m)


def no_solution_slope(p: dict) -> float:
    m, b1, b2 = _q(p["m"]), _q(p["b1"]), _q(p["b2"])
    if b1 == b2:
        raise AuditError("those two lines would coincide, not miss")
    return float(m)


def no_solution_gathered(p: dict) -> float:
    """α·x + β·y = δ and φ·x + τ·y = η are parallel when α·τ − φ·β = 0."""
    alpha, beta = _q(p["alpha"]), _q(p["beta"])
    delta, phi, eta = _q(p["delta"]), _q(p["phi"]), _q(p["eta"])
    if alpha == 0:
        raise AuditError("no x-term to compare")
    tau = phi * beta / alpha
    if alpha * eta - phi * delta == 0:
        raise AuditError("the two equations are consistent, so the system is not empty")
    return float(tau if p["shape"] == "x_first" else -tau)


def pick_none(p: dict) -> str:
    """Rebuild the system with the named solution set, after checking it has it.

    Two rows are parallel when their coefficient determinant vanishes; they are
    the same line when the two constant determinants vanish as well. That test
    decides which of the two shapes the sentence is asking for.
    """
    vx, vy, outcome = p["vx"], p["vy"], p["outcome"]
    if p["style"] == "slope_intercept":
        m, b, d = _q(p["m"]), _q(p["b"]), _q(p["d"])
        if b == d:
            raise AuditError("those two equations describe one line")
        line = lambda mm, bb, pp=Q(1): (                                  # noqa: E731
            _term(pp, vy) + " = " + _sum([_term(mm, vx)] + ([_n(bb)] if bb else [])))
        if outcome == "none":
            return _both(line(m, b), line(m, d))
        return _both(line(m, b), line(2 * m, 2 * b, Q(2)))
    a, b, c = _q(p["m"]), _q(p["b"]), _q(p["c"])
    k, d = _q(p["k"]), _q(p["d"])
    if a * (k * b) - (k * a) * b != 0:
        raise AuditError("those two rows are not parallel")
    if outcome == "none":
        if a * d - (k * a) * c == 0:
            raise AuditError("the two equations are consistent, so the system is not "
                             "empty")
        return _both(_eq(a, b, c, vx, vy), _eq(k * a, k * b, d, vx, vy))
    return _both(_eq(a, b, c, vx, vy), _eq(k * a, k * b, k * c, vx, vy))


def other_equation(p: dict) -> str:
    a, b, c, d = _q(p["a"]), _q(p["b"]), _q(p["c"]), _q(p["d"])
    g = Q(p["g"])
    if a % g or b % g or c % g:
        raise AuditError("the stated factor does not divide every term")
    if d == c / g:
        raise AuditError("that is the given line itself, so the system is not empty")
    return _eq(a / g, b / g, d)


def count_points(p: dict) -> float:
    m1, b1 = _q(p["m1"]), _q(p["b1"])
    m2, b2 = _q(p["m2"]), _q(p["b2"])
    det = (-m1) * Q(1) - (-m2) * Q(1)
    if det != 0:
        return 1.0
    if b1 == b2:
        raise AuditError("one line written twice has no countable answer")
    return 0.0


def unknown_coef(p: dict) -> float:
    c1, c2, k = _q(p["c1"]), _q(p["c2"]), _q(p["k"])
    if p["shape"] == "pair_ab":
        p2, x0 = _q(p["p2"]), _q(p["x0"])
        # unknowns (a, u) with u = b·y: x0·a + u = c1 and 0·a + k·u = c2 − p2·x0
        a, _u = _cramer((x0, Q(1), c1), (Q(0), k, c2 - p2 * x0))
        return float(a)
    p1, p2, y0 = _q(p["p1"]), _q(p["p2"]), _q(p["y0"])
    # unknowns (x, w): p1·x + (k·y0)·w = c1 and p2·x + (k·y0)·w = c2
    _x, w = _cramer((p1, k * y0, c1), (p2, k * y0, c2))
    return float(w)


def all_points(p: dict) -> str:
    a, b, c, k = _q(p["a"]), _q(p["b"]), _q(p["c"]), _q(p["k"])
    var = p["var"]
    if a * (k * b) - (k * a) * b != 0 or a * (k * c) - (k * a) * c != 0:
        raise AuditError("the two equations are not one line")
    if b == 0:
        raise AuditError("with no y-term the line is vertical")
    return f"({var}, {_frac_term(-a, b, var)} + {_n(c / b)})"


def _frac_term(n, d, var: str) -> str:
    """The coefficient printed as one fraction, the way the source prints it."""
    f = Q(n) / Q(d)
    head = var if abs(f.numerator) == 1 else f"{abs(f.numerator)}{var}"
    body = head if f.denominator == 1 else f"{head}/{f.denominator}"
    return ("-" if f < 0 else "") + body


def purchase_solve(p: dict) -> float:
    if p["shape"] == "count_value":
        n, pp, qq, t = _q(p["n"]), _q(p["p"]), _q(p["q"]), _q(p["t"])
        x, y = _cramer((Q(1), Q(1), n), (pp, qq, t))
        if p["ask"] == "first":
            return float(x)
        if p["ask"] == "second":
            return float(y)
        return float(pp * x)
    p1, q1, t1 = _q(p["p1"]), _q(p["q1"]), _q(p["t1"])
    p2, q2, t2 = _q(p["p2"]), _q(p["q2"]), _q(p["t2"])
    _r, b = _cramer((p1, q1, t1), (p2, q2, t2))
    return float(b)


def relation_pair(p: dict) -> float:
    k, d, g = _q(p["k"]), _q(p["d"]), _q(p["g"])
    # unknowns (first, second): first − k·second = d, and first ± second = g
    second_sign = Q(1) if p["link"] == "sum" else Q(-1)
    first, second = _cramer((Q(1), -k, d), (Q(1), second_sign, g))
    return float(first if p["ask"] == "first" else second)


def two_rates(p: dict) -> float:
    v1, v2 = _q(p["v1"]), _q(p["v2"])
    m, k = _q(p["m"]), _q(p["k"])
    if v1 == 0 or v2 == 0:
        raise AuditError("a leg with no speed takes no time")
    # unknowns (slow, fast): slow + fast = m, and fast/v2 − k·slow/v1 = 0
    _slow, fast = _cramer((Q(1), Q(1), m), (-k / v1, Q(1) / v2, Q(0)))
    return float(fast)


AUDITS = {
    "sys_standard": standard,
    "sys_substitution": standard,
    "sys_pair": pair,
    "sys_chunk": chunk,
    "sys_graph": graph,
    "sys_model_purchase": model_purchase,
    "sys_model_total": model_total,
    "sys_model_relation": model_relation,
    "sys_infinite_constant": infinite_constant,
    "sys_infinite_normalized": infinite_normalized,
    "sys_no_solution_slope": no_solution_slope,
    "sys_no_solution_gathered": no_solution_gathered,
    "sys_pick_none": pick_none,
    "sys_other_equation": other_equation,
    "sys_count_points": count_points,
    "sys_unknown_coef": unknown_coef,
    "sys_all_points": all_points,
    "sys_purchase_solve": purchase_solve,
    "sys_relation_pair": relation_pair,
    "sys_two_rates": two_rates,
}
