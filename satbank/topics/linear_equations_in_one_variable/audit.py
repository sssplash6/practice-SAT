"""Independent re-derivation of every Linear Equations answer.

Nothing here imports a template. Equations are re-read from the shape that was
printed and solved by bisection, so the generator's coefficient algebra is
never reused: a template that gathers `4(x - 3) + 6` wrongly has to be wrong
twice, in two differently written pieces of code, to escape.

The templates whose options are expressions rather than values are re-derived
the same way -- the modelling is done again from the numbers in the item, and
the sentence is rebuilt from the answer that derivation produces.
"""

from __future__ import annotations

from ...audit import AuditError

TOL = 1e-9


def supply_nested(p: dict) -> float:
    a, b, c, d, e = (p[k] for k in ("a", "b", "c", "d", "e"))
    return (p["rhs"] - a * c + d * e) / (a * b - d)


def supply_fraction(p: dict) -> float:
    from fractions import Fraction

    rhs = Fraction(p["rhs_num"], p["rhs_den"])
    numerator = rhs - Fraction(p["a"], p["m"]) - Fraction(p["b"], p["n"])
    coefficient = Fraction(1, p["m"]) + Fraction(1, p["n"])
    return float(numerator / coefficient)


# --------------------------------------------------------------- arithmetic

def _root(f, lo: float = -1.0e7, hi: float = 1.0e7) -> float:
    """The x where f changes sign. Linear equations have exactly one."""
    flo, fhi = f(lo), f(hi)
    if flo == 0:
        return lo
    if (flo > 0) == (fhi > 0):
        raise AuditError("the equation does not cross zero in the searched range")
    for _ in range(300):
        mid = (lo + hi) / 2.0
        if mid == lo or mid == hi:
            break
        if (f(mid) > 0) == (fhi > 0):
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2.0


def _grp(v: float) -> str:
    """A whole number the way the options print it: 8, -11, 1,100."""
    n = int(round(v))
    if abs(n - v) > 1e-6:
        raise AuditError(f"{v!r} should have been a whole number")
    return f"{n:,}" if abs(n) >= 1000 else str(n)


def _dec(v: float) -> str:
    s = f"{v:.10f}".rstrip("0").rstrip(".")
    return s or "0"


def _coef(c: float, var: str) -> str:
    if abs(c - 1) < TOL:
        return var
    if abs(c + 1) < TOL:
        return f"-{var}"
    return f"{_grp(c)}{var}"


def _sideof(m: float, b: float, var: str, const_first: bool = False) -> str:
    """One side of an equation, printed the way the source prints one."""
    if abs(m) < TOL:
        return _grp(b)
    if abs(b) < TOL:
        return _coef(m, var)
    head, tail = (_grp(b), _coef(m, var)) if const_first else (_coef(m, var), _grp(b))
    if tail.startswith("-"):
        return f"{head} - {tail[1:]}"
    return f"{head} + {tail}"


# ----------------------------------------------- reading a printed equation

def _sides(shape: str, p: dict):
    """(lhs, rhs) as functions of the unknown, read off the printed shape."""
    g = lambda k, d=0.0: float(p.get(k, d))                             # noqa: E731
    a, b, c, d = g("a"), g("b"), g("c"), g("d")
    e, f = g("e"), g("f")
    if shape == "standard":
        return (lambda x: a * x + b), (lambda x: c * x + d)
    if shape == "over":
        den = g("den", 1.0)
        return (lambda x: (a * x) / den), (lambda x: d)
    if shape == "split":
        f1, f2 = g("f1"), g("f2")
        return (lambda x: f1 * x - f2 * x), (lambda x: d)
    if shape == "sum_left":
        return (lambda x: a * x + b * (x + c)), (lambda x: d)
    if shape == "paren_right":
        return (lambda x: a * x + b), (lambda x: c * (x + d) + e)
    if shape == "two_paren":
        return (lambda x: a * (x + b) + c * (x + d)), (lambda x: e * x)
    if shape == "paren_sum":
        return (lambda x: a * (b * x + c) + d * x), (lambda x: e + f * x)
    if shape == "paren_both":
        return (lambda x: a * (b * x + c) + d), (lambda x: e * (x + f) + g("g"))
    raise AuditError(f"unknown equation shape {shape!r}")


def _solution(shape: str, p: dict) -> float:
    lhs, rhs = _sides(shape, p)
    return _root(lambda x: lhs(x) - rhs(x))


# ------------------------------------------------------------- the solvers

def solve(p: dict) -> float:
    return _solution(p["shape"], p["p"])


def then_value(p: dict) -> float:
    return p["m"] * _solution(p["shape"], p["p"]) + p["k"]


def chunk(p: dict) -> float:
    shape, a, b, c = p["shape"], p["a"], p["b"], p["c"]
    d, e = p["d"], p["e"]
    if shape == "two_left":
        f = lambda x: a * (x + c) + b * (x + c) - d                     # noqa: E731
        coef = a + b
    elif shape == "two_sides":
        f = lambda x: a * (x + c) - (b * (x + c) + d)                   # noqa: E731
        coef = a - b
    else:
        f = lambda x: e - (d + a * (x + c))                             # noqa: E731
        coef = a
    v = _root(f)
    return {"chunk": v + c, "var": v, "term": coef * (v + c)}[p["ask"]]


def reciprocal(p: dict) -> float:
    x = _root(lambda t: t / p["a"] - p["b"])
    if abs(x) < TOL:
        raise AuditError("the quotient asked for is not defined")
    return p["c"] / x


def _money(v: float, cents: bool = True) -> str:
    return f"${v:,.2f}" if cents else f"${int(round(v)):,}"


def context(p: dict):
    m, k, total = p["m"], p["k"], p["total"]
    found = _root(lambda u: m * u + k - total)
    # a wage prints as currency, and the option has to read that way too
    return _money(found) if p.get("money") else found


def percent_original(p: dict) -> str:
    kept = (1.0 - p["d1"]) * (1.0 - p["d2"])
    if kept <= 0:
        raise AuditError("the discounts leave nothing of the price")
    original = _root(lambda v: v * kept - p["paid"], 0.0, 1.0e9)
    return _money(round(original / 100.0) * 100, cents=False)


# ------------------------------------------------ answers that are sentences

WORDS = {"text": {"one": "Exactly one", "many": "Infinitely many", "none": "Zero"},
         "digit": {"one": "Exactly 1", "many": "Infinitely many", "none": "None"}}


def count_solutions(p: dict) -> str:
    if p["style"] == "plain":
        m1, k1, m2, k2 = p["a"], p["b"], p["c"], p["d"]
    else:
        m1, k1 = p["a"] * p["b"], p["a"] * p["c"]
        m2, k2 = p["d"] * p["f"], p["d"] * p["e"]
    if abs(m1 - m2) > TOL:
        which = "one"
    elif abs(k1 - k2) > TOL:
        which = "none"
    else:
        which = "many"
    return WORDS[p["words"]][which]


def identity_constant(p: dict) -> float:
    shape, a, b, c, d, f = p["shape"], p["a"], p["b"], p["c"], p["d"], p["f"]
    if shape == "same_coef":
        # a*v + L = a*v + c: the only L that makes the two sides agree at one
        # value of v, and therefore at every value
        cand = _root(lambda L: (a * 2.0 + L) - (a * 2.0 + c))
        if abs((a * 7.0 + cand) - (a * 7.0 + c)) > TOL:
            raise AuditError("that constant does not make the sides agree")
        return cand
    if shape == "factor":
        # a*v + b = L*(v + c): the v-terms force L = a, the constants need b = a*c
        if abs(b - a * c) > TOL:
            raise AuditError("no constant can make this an identity")
        return a
    # (a*v + b)/d - L/f = G*(v - c): the v-terms force G = a/d, and then the
    # constants give b/d - L/f = -G*c
    gcoef = a / d
    return f * (b / d + gcoef * c)


def no_solution_constant(p: dict) -> float:
    if p["shape"] == "coef_zero":
        if abs(p["d"]) < TOL:
            raise AuditError("with a zero on the right the equation is an identity")
        return p["c"]
    a, b, d, q, pp = p["a"], p["b"], p["d"], p["q"], p["p"]
    if abs(a * b - d) < TOL:
        raise AuditError("this equation is an identity, not an empty one")
    return pp / (q * a)


def identity_pair(p: dict) -> str:
    c, d, e = p["c"], p["d"], p["e"]
    a = e                                     # -a*v must match -e*v
    b = a * c - d                             # then a*c - b must match d
    return f"a = {_grp(a)} and b = {_grp(b)}"


def conditions(p: dict) -> str:
    m, c = p["m"], p["c"]
    # m*v + c = a*(v + b) is empty exactly when a = m and a*b != c
    truth = {"a_is_m": True, "a_not_m": False, "b_is_c": abs(c - c / m) < TOL,
             "b_not_ratio": True, "b_is_ratio": False, "a_is_c": abs(m - c) < TOL,
             "ab_not_c": True}
    flags = [truth[k] for k in p["picks"]]
    names = [n for n, t in zip(("I", "II", "III"), flags) if t]
    if not names:
        return "None"
    if len(names) == 3:
        return "I, II, and III"
    return f"{' and '.join(names)} only"


def zero_chunk(p: dict) -> str:
    if abs(p["p"] - p["q"]) < TOL:
        raise AuditError("equal denominators make the equation an identity")
    u = 0.0                                   # (v + c)/p = (v + c)/q only at zero
    hit = [(lo, hi) for lo, hi in p["spans"] if lo < u < hi]
    if len(hit) != 1:
        raise AuditError(f"{len(hit)} of the ranges contain the value")

    def one(v: float) -> str:
        return _grp(v) if abs(v - round(v)) < 1e-9 else _dec(v)

    return f"{one(hit[0][0])} and {one(hit[0][1])}"


def equivalent(p: dict) -> str:
    g, var = p["g"], p["var"]
    return f"{_sideof(p['a'] / g, p['b'] / g, var)} = {_grp(p['d'] / g)}"


def count_mix(p: dict) -> str:
    # mult*n of the first length, n of the second, `fixed` of the third
    var, mult, fixed, total = p["var"], p["mult"], p["fixed"], p["total"]
    return f"{_grp(mult + 1)}{var} + {_grp(fixed)} = {_grp(total)}"


def model_context(p: dict) -> str:
    shape, var = p["shape"], p["var"]
    if shape == "phrase":
        return (f"{_grp(p['mult'])}{var} + {_grp(p['add'])} = {_grp(p['total'])}")
    if shape == "base_after":
        return (f"{_grp(p['base'])} + {_grp(p['rate'])}({var} - {_grp(p['hrs'])}) "
                f"= {_grp(p['total'])}")
    if shape == "fuel":
        # gallons saved is miles/mpg, each costing `cost` dollars
        return f"({_grp(p['cost'])}/{_grp(p['mpg'])}){var} = {_grp(p['cut'])}"
    price, make, comm = p["price"], p["make"], p["comm"]
    return (f"({_grp(price)}(1 - {_dec(comm)}) - {_grp(make)}){var} = {_grp(p['total'])}")


def expression(p: dict) -> str:
    shape, var = p["shape"], p["var"]
    if shape == "unit_rate":
        return f"{_grp(p['price'])}{var}"
    if shape == "more_than_times":
        return f"{_grp(p['mult'])}{var} + {_grp(p['add'])}"
    if shape == "perimeter":
        # perimeter of w by (w + d) is 2w + 2(w + d)
        return f"{_grp(4)}{var} + {_grp(2 * p['d'])}"
    # p per station for x stations and q per station for the other n - x
    n, pp, q = p["n"], p["p"], p["q"]
    return f"{_grp(pp - q)}{var} + {_grp(q * n)}"


def interpret(p: dict) -> str:
    thing, var = p["thing"], p["var"]
    if p["scene"] == "growth":
        # the coefficient multiplies a number of years, so its units are feet
        # per year -- a rate, not a height and not a count of years
        if p["rate"] <= 0 or p["years"] <= 0:
            raise AuditError("a growth rate has to be positive")
        return f"The average number of feet that the {thing} grew per year"
    return f"The monthly sales revenue, in dollars, from selling {var} {thing}"


AUDITS = {
    "lin1_supply_nested": supply_nested,
    "lin1_supply_fraction": supply_fraction,
    "lin1_solve": solve,
    "lin1_distribute": solve,
    "lin1_then_value": then_value,
    "lin1_chunk": chunk,
    "lin1_reciprocal": reciprocal,
    "lin1_context": context,
    "lin1_percent_original": percent_original,
    "lin1_count": count_solutions,
    "lin1_identity_constant": identity_constant,
    "lin1_no_solution_constant": no_solution_constant,
    "lin1_identity_pair": identity_pair,
    "lin1_conditions": conditions,
    "lin1_zero_chunk": zero_chunk,
    "lin1_equivalent": equivalent,
    "lin1_count_mix": count_mix,
    "lin1_model_context": model_context,
    "lin1_expression": expression,
    "lin1_interpret": interpret,
}
