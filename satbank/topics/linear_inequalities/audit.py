"""Independent re-derivation of every Linear Inequalities answer.

Nothing here imports a template, and nothing here repeats a template's algebra.
An inequality is re-derived the only way that catches a sign that failed to
turn over: by **putting numbers in on both sides of the boundary** and seeing
which side survives. The boundary itself is found by interpolating the printed
relation rather than by gathering its terms, so a template that divides by a
negative coefficient and forgets to reverse the relation has to be wrong twice,
in two pieces of code written from different ends, to escape.

The items whose options are written rather than numeric are re-derived the same
way: the situation is modelled again from the numbers the item carries, and the
sentence is rebuilt from that model. The shared normaliser forgives a comma, a
space and the two spellings of a minus sign, so only the mathematics and the
relation symbols have to agree.
"""

from __future__ import annotations

from fractions import Fraction as F

from ...audit import AuditError

SYM = {"<": "<", "<=": "≤", ">": ">", ">=": "≥"}
BIG = 10 ** 7


def supply_budget(p: dict) -> float:
    if p["price"] <= 0 or p["budget"] < p["fee"]:
        raise AuditError("invalid budget")
    return float((p["budget"] - p["fee"]) // p["price"])


def supply_count(p: dict) -> float:
    return float(len(range(p["lower"], p["upper"])))


def supply_two_sided(p: dict) -> float:
    a, b, lo, hi = (p[k] for k in ("coefficient", "offset", "lower", "upper"))
    if a <= 0 or lo >= hi:
        raise AuditError("invalid compound inequality")
    candidate = (hi - b - 1) // a
    if a * candidate + b < lo:
        raise AuditError("no integer satisfies the compound inequality")
    return float(candidate)


def supply_perimeter(p: dict) -> float:
    return float((p["limit"] - 2 * p["difference"]) // 4)


# ------------------------------------------------------------ the relations

def true(a, op: str, b) -> bool:
    """Does the relation hold between these two numbers?"""
    if op == "<":
        return a < b
    if op == "<=":
        return a <= b
    if op == ">":
        return a > b
    if op == ">=":
        return a >= b
    raise AuditError(f"unknown relation {op!r}")


def q(v) -> F:
    """A parameter as an exact rational. Templates store floats; the numbers
    they store are small rationals, so nothing is lost."""
    if isinstance(v, (list, tuple)):
        return F(int(v[0]), int(v[1]))
    return F(v).limit_denominator(10 ** 6)


def root(f) -> F:
    """The x where a straight function crosses zero, by interpolation.

    Two samples fix a line, which is all a linear relation ever is. Nothing
    about how the relation was built is used.
    """
    y0, y1 = f(F(0)), f(F(1))
    if y1 == y0:
        raise AuditError("the relation does not depend on the variable")
    return -y0 / (y1 - y0)


def edge(pred, lo: float = -BIG, hi: float = BIG) -> float:
    """The value where a monotone predicate changes its mind."""
    if pred(lo) == pred(hi):
        raise AuditError("the condition does not change over the search range")
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if mid in (lo, hi):
            break
        if pred(mid) == pred(lo):
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# -------------------------------------------------------------- the printers

def n(v) -> str:
    """A number as an option prints one. Commas, spaces and the shape of the
    minus sign are the normaliser's business, not this file's."""
    v = q(v)
    if v.denominator == 1:
        return str(v.numerator)
    return f"{v.numerator}/{v.denominator}"


def d(v, least: int = 0) -> str:
    """The shortest exact decimal, or the fraction when there is not one."""
    v = q(v)
    den, twos, fives = v.denominator, 0, 0
    while den % 2 == 0:
        den //= 2
        twos += 1
    while den % 5 == 0:
        den //= 5
        fives += 1
    if den != 1:
        return n(v)
    places = max(twos, fives, least)
    return f"{float(v):.{places}f}"


def mix(v) -> str:
    """A mixed number, as an awkward bound is printed: 11 2/3."""
    v = q(v)
    if v.denominator == 1:
        return n(v)
    whole, rest = divmod(abs(v), 1)
    body = f"{rest.numerator}/{rest.denominator}"
    head = f"{whole} " if whole else ""
    return ("-" if v < 0 else "") + head + body


def term(c, var: str, dec: bool = False) -> str:
    c = q(c)
    if c == 1:
        return var
    if c == -1:
        return f"-{var}"
    if c.denominator != 1 and not dec:
        body = f"({n(abs(c))}){var}"
        return f"-{body}" if c < 0 else body
    return f"{d(c) if dec else n(c)}{var}"


def side(terms, const=0, dec: bool = False) -> str:
    parts = [term(c, v, dec) for c, v in terms if q(c) != 0]
    const = q(const)
    if not parts:
        return d(const) if dec else n(const)
    if const != 0:
        parts.append(d(const) if dec else n(const))
    out = parts[0]
    for p in parts[1:]:
        out += f" - {p[1:]}" if p.startswith("-") else f" + {p}"
    return out


def rel(lhs: str, op: str, rhs: str) -> str:
    return f"{lhs} {SYM[op]} {rhs}"


def span(lo, hi, var: str, op: str = "<=", dec: bool = False) -> str:
    lo, hi = (lo, hi) if q(lo) <= q(hi) else (hi, lo)
    show = d if dec else n
    return f"{show(lo)} {SYM[op]} {var} {SYM[op]} {show(hi)}"


# ------------------------------------------------- solving for the variable

def solve_linear(p: dict) -> str:
    """Read the printed relation, find its boundary, then test both sides.

    Which way the answer points is never deduced -- a number one above the
    boundary and a number one below are both put into the relation as printed,
    and the side that survives is the side the answer describes. A sign rule
    that was not applied cannot hide from that.
    """
    a, b, c, dd = q(p["a"]), q(p["b"]), q(p["c"]), q(p["d"])
    shape, op, var = p["shape"], p["op"], p["var"]
    if shape == "gathered":
        lhs, rhs = (lambda x: a * x + b), (lambda x: c)
    elif shape == "both_sides":
        lhs, rhs = (lambda x: a * x + b), (lambda x: c * x + dd)
    elif shape == "bracket":
        lhs, rhs = (lambda x: a * (x + b)), (lambda x: c * x + dd)
    else:
        raise AuditError(f"unknown printed shape {shape!r}")

    bound = root(lambda x: lhs(x) - rhs(x))
    above = true(lhs(bound + 1), op, rhs(bound + 1))
    below = true(lhs(bound - 1), op, rhs(bound - 1))
    if above == below:
        raise AuditError("both sides of the boundary behave the same way")
    at = true(lhs(bound), op, rhs(bound))
    key_op = (">" if above else "<") + ("=" if at else "")
    return rel(var, key_op, n(bound))


def greatest_value(p: dict) -> float:
    """The extreme value a one-sided bound allows, found by bisection."""
    m, k, y, sgn = q(p["m"]), q(p["k"]), q(p["y"]), q(p["sign"])
    op = p["op"]
    bound = m * y + sgn * k

    def ok(x: float) -> bool:
        return true(F(x).limit_denominator(10 ** 9), op, bound)

    got = edge(ok)
    if not ok(got - 1e-9 if op == "<=" else got + 1e-9):
        raise AuditError("the boundary found does not satisfy the condition")
    return got


def y_range(p: dict) -> str:
    """Two constraints bound x from below; carry that bound into y."""
    m, c, nn, t = q(p["m"]), q(p["c"]), q(p["n"]), q(p["t"])
    if nn <= 0 or m <= 0:
        raise AuditError("both coefficients have to be positive")
    x_edge = root(lambda x: nn * x - t)              # where n·x > t turns over
    if not true(nn * (x_edge + 1), ">", t):
        raise AuditError("the second constraint bounds x from above, not below")
    lowest = m * x_edge + c
    # a value of x just inside the allowed region puts y just above the bound
    if not m * (x_edge + F(1, 1000)) + c > lowest:
        raise AuditError("the bound on y is not approached from above")
    return rel(p["v"], ">", n(lowest))


def range_solve(p: dict) -> str:
    """Total = base + rate·s held inside a band of multiples of the base."""
    rate, k1, k2 = q(p["rate"]), q(p["k1"]), q(p["k2"])
    base, var = p["base"], p["var"]
    if rate <= 0 or k2 <= k1:
        raise AuditError("the band has to sit above the base earnings")
    # with a base salary of 1, find the sales that hit each end of the band
    lo = root(lambda s: 1 + rate * s - k1)
    hi = root(lambda s: 1 + rate * s - k2)
    a, b = lo * rate, hi * rate
    if a.denominator != 1 or b.denominator != 1:
        raise AuditError("the two ends do not come out as whole multiples")
    return (f"({n(a)}/{d(rate)}){base} ≤ {var} ≤ ({n(b)}/{d(rate)}){base}")


def triangle(p: dict) -> str:
    """The third side, found by testing lengths rather than by a formula."""
    a, b = q(p["a"]), q(p["b"])

    def fits(x: float) -> bool:
        x = F(x).limit_denominator(10 ** 9)
        return a + b > x and a + x > b and b + x > a

    inside = float(max(a, b))
    if not fits(inside):
        raise AuditError("no triangle is possible with these two sides")
    lo = edge(fits, inside, -1.0)
    hi = edge(fits, inside, float(a + b) * 4)
    return f"{n(lo)} < {p['var']} < {n(hi)}"


def dimension(p: dict) -> str:
    """The widest box the cap allows, found by widening until it stops fitting."""
    cap, height, factor = q(p["cap"]), q(p["height"]), q(p["factor"])

    def fits(x: float) -> bool:
        x = F(x).limit_denominator(10 ** 9)
        return 2 * (x + factor * x) + height <= cap

    if not fits(1e-9):
        raise AuditError("not even a sliver of width fits under the cap")
    widest = edge(fits, 1e-9, float(cap) * 4)
    return f"0 < {p['var']} ≤ {mix(F(widest).limit_denominator(10 ** 6))}"


# ----------------------------------------------------- modelling a situation

def model_two(p: dict) -> str:
    a, b, total = q(p["a"]), q(p["b"]), q(p["total"])
    dec = p["style"] == "percent"
    return rel(side([(a, p["u"]), (b, p["v"])], dec=dec), p["op"], n(total))


def model_one(p: dict) -> str:
    shape, var = p["shape"], p["var"]
    if shape == "perimeter":
        # two widths and two lengths, held under the stated perimeter
        return rel(side([(2, var)], 2 * q(p["length"])), p["op"], n(p["total"]))
    if shape == "payback":
        saved = f"({n(p['before'])} - {n(p['after'])}){var}"
        return rel(n(p["install"]), "<", saved)
    if shape == "two_group":
        gap, n1, n2 = q(p["gap"]), q(p["n1"]), q(p["n2"])
        earlier = f"{n(n1)}({var} + {n(gap)})"
        return rel(f"{earlier} + {term(n2, var)}", p["op"], n(p["total"]))
    if shape == "race":
        # waiting then riding beats walking exactly when it takes longer
        return rel(side([(1, var)], q(p["ride"])), ">", n(p["walk"]))
    if shape == "mean":
        scores = [q(s) for s in p["scores"]]
        listed = " + ".join(n(s) for s in scores)
        count = len(scores) + 1
        return rel(f"({var} + {listed})/{n(count)}", p["op"], n(p["target"]))
    if shape == "share":
        half, first, pct = q(p["half"]), q(p["first"]), q(p["pct"])
        share = d(pct / 100, least=2)
        return (f"{rel(side([(1, var)], first), '>', f'{share}({n(2 * half)})')}"
                f", where {rel(var, '<=', n(half))}")
    raise AuditError(f"unknown modelled shape {shape!r}")


def model_system(p: dict) -> str:
    shape, u, v = p["shape"], p["u"], p["v"]
    if shape == "count_cost":
        return (f"{rel(side([(1, u), (1, v)]), '>=', n(p['least']))}, "
                f"{rel(side([(q(p['a']), u), (q(p['b']), v)]), '<=', n(p['budget']))}")
    if shape == "ratio":
        k, cap = q(p["k"]), q(p["cap"])
        if p["weights"]:
            first = side([(q(p["w1"]), u), (q(p["w2"]), v)], dec=True)
        else:
            first = side([(1, u), (1, v)])
        return (f"{rel(first, '<=', n(cap))}, "
                f"{rel(u, p['ratio_op'], term(k, v))}")
    if shape == "staffing":
        rows = [rel(side([(q(p["pay1"]), u), (q(p["pay2"]), v)]), "<=",
                    n(p["budget"])),
                rel(side([(1, u), (1, v)]), ">=", n(p["staff"])),
                rel(u, ">=", n(p["min1"])), rel(v, ">=", n(p["min2"]))]
        return ", ".join(rows)
    raise AuditError(f"unknown system shape {shape!r}")


# ------------------------------------------------- answers that are a count

def whole_bound(p: dict) -> float:
    """Try every whole number and keep the extreme one that works."""
    fee, rate = q(p["fee"]), q(p["rate"])
    limit, scale = q(p["limit"]), q(p["scale"])
    op, want = p["op"], p["want"]
    works = [k for k in range(1, 5000) if true(scale * (fee + rate * k), op, limit)]
    if not works:
        raise AuditError("no whole number of units satisfies the condition")
    if want == "greatest":
        best = max(works)
        if len(works) != best - min(works) + 1:
            raise AuditError("the counts that work are not one unbroken run")
        return float(best)
    return float(min(works))


def pair_max(p: dict) -> float:
    """The most of the heavier kind, by trying every load."""
    w1, w2 = q(p["w1"]), q(p["w2"])
    least, cap = int(p["least"]), q(p["cap"])
    best = None
    for heavy in range(0, least + 1):
        light = max(0, least - heavy)
        if w1 * light + w2 * heavy <= cap:
            best = heavy
    if best is None:
        raise AuditError("no load meets the count without breaking the cap")
    return float(best)


def value_in_range(p: dict) -> str:
    """Which of the four printed values lands inside the band."""
    lo, hi, count = q(p["lo"]), q(p["hi"]), q(p["n"])
    inside = [text for text, v in p["opts"] if lo * count <= q(v) <= hi * count]
    if len(inside) != 1:
        raise AuditError(f"{len(inside)} of the four values lie in the range")
    return inside[0]


def which_interval(p: dict) -> str:
    """Which interval keeps every one of its values past the threshold."""
    thr = q(p["thr"])
    clear = [text for text, lo, hi in p["spans"] if q(lo) >= thr]
    if len(clear) != 1:
        raise AuditError(f"{len(clear)} of the intervals clear the threshold")
    return clear[0]


# ------------------------------------------------ testing a candidate point

def holds(row, x, y) -> bool:
    x, y = q(x), q(y)
    if row[0] == "y":
        return true(y, row[3], q(row[1]) * x + q(row[2]))
    if row[0] == "lin":
        return true(q(row[1]) * x + q(row[2]) * y, row[4], q(row[3]))
    return true(x if row[1] == "x" else y, row[3], q(row[2]))


def point_solution(p: dict) -> str:
    ask = p["ask"]
    if ask in ("point", "roman", "table"):
        rows = p["rows"]

        def good(x, y) -> bool:
            return all(holds(r, x, y) for r in rows)

    if ask == "point":
        hit = [text for text, x, y in p["cands"] if good(x, y)]
        if len(hit) != 1:
            raise AuditError(f"{len(hit)} of the four points are solutions")
        return hit[0]
    if ask == "table":
        hit = [text for text, pairs in p["tables"]
               if all(good(x, y) for x, y in pairs)]
        if len(hit) != 1:
            raise AuditError(f"{len(hit)} of the four tables are all solutions")
        return hit[0]
    if ask == "roman":
        names = [r for r, (x, y) in zip(("I", "II", "III"), p["pairs"])
                 if good(x, y)]
        if not names:
            raise AuditError("none of the three pairs is a solution")
        if len(names) == 3:
            return "I, II, and III"
        return f"{' and '.join(names)} only"
    x, y = p["point"]
    hit = [text for text, rows in p["systems"]
           if all(holds(r, x, y) for r in rows)]
    if len(hit) != 1:
        raise AuditError(f"the point satisfies {len(hit)} of the four systems")
    return hit[0]


# ------------------------------------------------------- bands of values

def band_extremes(p: dict) -> str:
    lo, hi = q(p["lo"]), q(p["hi"])
    if hi <= lo:
        raise AuditError("the two recorded values do not bound anything")
    return span(lo, hi, p["var"])


def band_scale(p: dict) -> str:
    lo, hi, rate = q(p["lo"]), q(p["hi"]), q(p["rate"])
    op, var = p["op"], p["var"]
    if p["shape"] == "divide":
        # a count of k spaces fits exactly when the curb length can be made up
        # of k widths, each somewhere inside the allowed band
        works = [k for k in range(1, 10000) if k * lo <= rate <= k * hi]
        if not works:
            raise AuditError("no whole number of spaces fits the curb")
        if len(works) != max(works) - min(works) + 1:
            raise AuditError("the counts that fit are not one unbroken run")
        return span(min(works), max(works), var, op)
    dec = p["decimal"]
    show = d if dec else n

    def prod(v) -> str:
        return (f"{show(rate)}({show(v)})" if p["order"] == "rate_first"
                else f"({show(v)})({show(rate)})")

    if rate <= 0:
        raise AuditError("a negative rate would turn the two ends round")
    return f"{prod(lo)} {SYM[op]} {var} {SYM[op]} {prod(hi)}"


def band_formula(p: dict) -> str:
    lo, hi = q(p["lo"]), q(p["hi"])
    mult, off = q(p["mult"]), q(p["off"])
    if mult <= 0:
        raise AuditError("a negative multiplier would turn the two ends round")
    ends = [off + mult * lo, off + mult * hi]
    middle = off + mult * (lo + hi) / 2
    if not ends[0] < middle < ends[1]:
        raise AuditError("the middle of the band does not land between the ends")
    return span(ends[0], ends[1], p["var"], p["op"])


# ----------------------------------------------- reading the model in words

def interpret(p: dict) -> str:
    if p["shape"] == "term":
        item = p["large"] if p["piece"] == "second" else p["small"]
        return f"The total amount, in dollars, {p['who']} will spend on {item}"
    first, second, cap = q(p["first"]), q(p["second"]), q(p["cap"])
    word = {"<=": "less than or equal to", ">=": "greater than or equal to",
            "<": "less than", ">": "greater than"}[p["op"]]
    if not true(2 * (first + second), p["op"], cap):
        raise AuditError("the pair given does not satisfy the inequality")
    return (f"If the {p['thing']} has {p['n1']} {n(first)} and {p['n2']} "
            f"{n(second)}, its {p['measure']} is {word} {n(cap)}.")


AUDITS = {
    "ineq_supply_budget": supply_budget,
    "ineq_supply_count": supply_count,
    "ineq_supply_two_sided": supply_two_sided,
    "ineq_supply_perimeter": supply_perimeter,
    "ineq_solve_linear": solve_linear,
    "ineq_greatest_value": greatest_value,
    "ineq_y_range": y_range,
    "ineq_range_solve": range_solve,
    "ineq_triangle": triangle,
    "ineq_dimension": dimension,
    "ineq_model_two": model_two,
    "ineq_model_one": model_one,
    "ineq_model_system": model_system,
    "ineq_whole_bound": whole_bound,
    "ineq_pair_max": pair_max,
    "ineq_value_in_range": value_in_range,
    "ineq_which_interval": which_interval,
    "ineq_point_solution": point_solution,
    "ineq_band_extremes": band_extremes,
    "ineq_band_scale": band_scale,
    "ineq_band_formula": band_formula,
    "ineq_interpret": interpret,
}
