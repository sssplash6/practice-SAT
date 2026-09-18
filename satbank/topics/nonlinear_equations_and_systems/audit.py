"""Independent re-derivation of every Nonlinear Equations and Systems answer.

Nothing here imports a template. Where a family factors a quadratic, this file
**brackets and bisects** the printed polynomial numerically and never forms a
discriminant; where a family forms a discriminant to count solutions, this file
**counts sign changes** in that same numeric sweep. Where a family rearranges a
formula symbolically, this file assigns numbers to the other letters, solves the
relation for the target by evaluating it, and then reads the four printed options
back and asks which of them produces that number -- so a rearrangement that is
right in the algebra and wrong on the page is still caught.

The one thing it deliberately does not reuse is the printing: a solver that
rebuilt an option string through the same renderer would agree with a renderer
bug twice over.
"""

from __future__ import annotations

import math
import re
from fractions import Fraction as Q

from ...audit import AuditError
from ...expr import ParseError, parse

TOL = 1e-9


# ------------------------------------------------------------ reading params

def _q(pair) -> Q:
    return Q(int(pair[0]), int(pair[1]))


def _terms(packed) -> list:
    return [(_q(c), s) for c, s in packed]


# ------------------------------------------------- numbers, found numerically

def _poly_at(coeffs, x: float) -> float:
    """Σ cᵢ xⁱ, lowest degree first."""
    out = 0.0
    for i, c in enumerate(coeffs):
        out += float(c) * x ** i
    return out


def _deriv(coeffs) -> list:
    return [i * c for i, c in enumerate(coeffs)][1:]


def _bound(coeffs) -> float:
    """Cauchy's bound: every real root lies inside it."""
    lead = abs(coeffs[-1])
    return 1.0 + max((abs(c) / lead for c in coeffs[:-1]), default=0.0)


def _real_roots(coeffs) -> list:
    """Every real root of a polynomial, without any root formula.

    Between two consecutive stationary points a polynomial is monotone, so every
    root is either a sign change across one of those intervals or a stationary
    point sitting on the axis. The stationary points are the roots of the
    derivative, found the same way, and the recursion bottoms out at a linear
    polynomial. Each bracketed root is then squeezed by bisection.

    Nothing here forms a discriminant, factors anything, or completes a square,
    which is the whole point: the families do all three, and a solver that
    repeated any of them would agree with a broken template twice over.
    """
    coeffs = [float(c) for c in coeffs]
    while len(coeffs) > 1 and abs(coeffs[-1]) < 1e-15:
        coeffs.pop()
    if len(coeffs) <= 1:
        return []
    if len(coeffs) == 2:
        return [-coeffs[0] / coeffs[1]]

    scale = max(abs(c) for c in coeffs)
    tol = 1e-12 * max(1.0, scale)
    crit = _real_roots(_deriv(coeffs))
    r = _bound(coeffs)
    nodes = [-r] + [c for c in sorted(crit) if -r < c < r] + [r]

    out = []
    for u, v in zip(nodes, nodes[1:]):
        fu, fv = _poly_at(coeffs, u), _poly_at(coeffs, v)
        if abs(fu) <= tol:
            out.append(u)
        if abs(fv) <= tol:
            out.append(v)
        elif abs(fu) > tol and (fu > 0) != (fv > 0):
            out.append(_bisect(coeffs, u, v))
    return sorted(_dedupe(out))


def _bisect(coeffs, a: float, b: float) -> float:
    """Squeeze a bracketed root. The interval is monotone, so this converges."""
    fa = _poly_at(coeffs, a)
    for _ in range(120):
        m = (a + b) / 2
        fm = _poly_at(coeffs, m)
        if fm == 0.0:
            return m
        if (fm > 0) == (fa > 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


def _dedupe(values, tol: float = 1e-7) -> list:
    out = []
    for v in sorted(values):
        if not out or abs(v - out[-1]) > tol * max(1.0, abs(v)):
            out.append(v)
    return out


def _count_roots(coeffs) -> int:
    return len(_real_roots(coeffs))


# ------------------------------------------- printed options, read back again

_NAME = re.compile(r"[A-Za-z][A-Za-z_0-9]*")


def _split_names(text: str, env: dict) -> str:
    """`jb` is j times b, and the shared reader cannot know that.

    `expr.parse` lexes a run of letters as one variable name, which is right for
    `V_B` and wrong for `cy` -- and a page that prints `c = cy/55` means the
    product. Every letter run is therefore split greedily into the longest names
    the caller has actually given values to, which turns `cy` into `c*y` and
    leaves `V_B` alone. A run that cannot be split is left as it is, and the
    parse then fails, which counts as an option nobody can read.
    """
    def repl(m):
        run = m.group()
        if run in env or run in ("sqrt", "pi"):
            return run
        parts, i = [], 0
        while i < len(run):
            for j in range(len(run), i, -1):
                if run[i:j] in env:
                    parts.append(run[i:j])
                    i = j
                    break
            else:
                return run
        return "*".join(parts)

    return _NAME.sub(repl, text)


def _value_of(text: str, env: dict) -> float:
    """What a printed expression comes to, once the letters have values."""
    return parse(_split_names(text, env))(**env)


def _decide(options, env: dict, want: float, target: str) -> str:
    """The printed option whose right-hand side comes to `want`.

    Every option is `target = <expression>`; the expression is parsed from the
    page and evaluated, and the one that lands on the independently computed
    value is the answer. Anything that will not parse counts as wrong, which is
    the right way round: an option nobody can read is not an answer.
    """
    hits = []
    for opt in options:
        rhs = opt.split(" = ", 1)[1] if " = " in opt else opt
        try:
            got = _value_of(rhs, env)
        except (ParseError, ZeroDivisionError, ValueError, OverflowError,
                TypeError):
            continue
        if math.isfinite(got) and abs(got - want) <= 1e-7 * max(1.0, abs(want)):
            hits.append(opt)
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} of the four printed options give "
                         f"{target} = {want!r}")
    return hits[0]


def _env(names) -> dict:
    """Distinct, safely non-zero values for the letters of a formula.

    Every one is a dyadic rational -- a whole number of eighths -- so a product
    or a difference of them is exact in binary floating point and the comparison
    that follows is not measuring the arithmetic's own residue.
    """
    picks = [2.25, 3.5, 5.125, 7.75, 11.375, 13.625, 17.875, 19.25, 23.5,
             29.125, 31.75]
    return {n: picks[i % len(picks)] for i, n in enumerate(names)}


def _sym_value(sym: str, env: dict) -> float:
    """A packed symbol, which may be a squared letter, evaluated."""
    if not sym:
        return 1.0
    if sym.endswith("²"):
        return env[sym[:-1]] ** 2
    return env[sym]


def _sum(terms, env: dict) -> float:
    return sum(float(c) * _sym_value(s, env) for c, s in terms)


def _names(*groups) -> list:
    out = []
    for g in groups:
        for _, s in g:
            base = s[:-1] if s.endswith("²") else s
            if base and base not in out:
                out.append(base)
    return out


# ================================================================== literal

def _isolate_sum(p):
    target = p["target"]
    coef, div = _q(p["coef"]), _q(p["divisor"])
    extras, other = _terms(p["extras"]), _terms(p["other"])
    names = _names(extras, other)
    env = _env(names)
    # (coef·t + extras)/div = other  ->  t = (div·other − extras)/coef
    want = (float(div) * _sum(other, env) - _sum(extras, env)) / float(coef)
    if p.get("ask") == "coefficient":
        moving = [s for _, s in other + extras if s]
        if len(moving) != 1:
            raise AuditError("the rearranged form has no single coefficient")
        shifted = dict(env)
        shifted[moving[0]] += 1.0
        want2 = ((float(div) * _sum(other, shifted) - _sum(extras, shifted))
                 / float(coef))
        return want2 - want
    return _decide(p["options"], dict(env), want, target)


def _isolate_bracket(p):
    target = p["target"]
    c = _q(p["c"])
    left, head, inner = _terms(p["left"]), _terms(p["head"]), _terms(p["inner"])
    names = _names(left, head, inner)
    env = _env([n for n in names if n != target])
    # left = head + c·inner, affine in the target: solve by two evaluations
    def f(t):
        e = dict(env, **{target: t})
        return _sum(left, e) - _sum(head, e) - float(c) * _sum(inner, e)

    a1, a0 = f(1.0) - f(0.0), f(0.0)
    if abs(a1) < 1e-12:
        raise AuditError("the target does not appear linearly")
    want = -a0 / a1
    return _decide(p["options"], dict(env), want, target)


def _isolate_factor(p):
    target = p["target"]
    k = float(_q(p["k"]))
    left = _terms(p["left"])
    top, bottom = list(p["top"]), list(p["bottom"])
    names = _names(left) + [s for s in top + bottom if s != target]
    env = _env([n for n in dict.fromkeys(names)])
    lv = _sum(left, env)
    if target in top:
        others = [env[s] for s in top if s != target]
        below = [env[s] for s in bottom]
        want = lv / k
        for v in others:
            want /= v
        for v in below:
            want *= v
    else:
        above = [env[s] for s in top]
        others = [env[s] for s in bottom if s != target]
        want = k / lv
        for v in above:
            want *= v
        for v in others:
            want /= v
    return _decide(p["options"], dict(env), want, target)


def _isolate_denominator(p):
    target = p["target"]
    head, sigma, const = _q(p["head"]), _q(p["sigma"]), _q(p["const"])
    top_c, top_s = _q(p["top"][0]), p["top"][1]
    left = _terms(p["left"])
    names = _names(left) + ([top_s] if top_s else [])
    env = _env([n for n in dict.fromkeys(names)])
    lv = _sum(left, env) - float(head)
    if abs(lv) < 1e-12:
        raise AuditError("the left-hand side vanishes")
    numerator = float(top_c) * (env[top_s] if top_s else 1.0)
    want = (numerator / lv - float(const)) / float(sigma)
    return _decide(p["options"], dict(env), want, target)


_REL = re.compile(r"^(.*?)\s*(≤|≥|<|>|=)\s*(.*)$")


def _scale_relation(p):
    """The option that describes the same half-plane as the printed inequality.

    Each side is read off the page by evaluating it at three points -- (0, 0),
    (1, 0) and (0, 1) -- which recovers the option's own coefficients without
    looking at how it was built. Two strict inequalities describe the same
    half-plane exactly when one coefficient triple is a positive multiple of the
    other, or a negative multiple with the sense turned round, and that is
    decided here in exact arithmetic on Fractions.
    """
    a, b, c = _q(p["a"]), _q(p["b"]), _q(p["c"])
    vx, vy, op = p["vx"], p["vy"], p["op"]
    want = (a, -b, c)
    hits = []
    for opt in p["options"]:
        m = _REL.match(opt)
        if m is None:
            continue
        try:
            got = _coefficients(m.group(1), m.group(3), vx, vy)
        except (ParseError, ZeroDivisionError, ValueError):
            continue
        flipped = m.group(2) in (">", "\u2265")
        if _same_half_plane(want, got, flipped == (op in (">", "\u2265"))):
            hits.append(opt)
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} options describe the printed half-plane")
    return hits[0]


def _coefficients(lhs: str, rhs: str, vx: str, vy: str):
    """(A, B, C) with the printed relation read as A·x + B·y against C."""
    def at(x, y):
        env = {vx: x, vy: y}
        return _value_of(lhs, env) - _value_of(rhs, env)

    base = at(0.0, 0.0)
    return (_exact(at(1.0, 0.0) - base), _exact(at(0.0, 1.0) - base),
            _exact(-base))


def _exact(v: float) -> Q:
    """A coefficient read off the page, back to the rational it plainly is."""
    return Q(v).limit_denominator(10_000)


def _same_half_plane(want, got, same_sense: bool) -> bool:
    a1, b1, c1 = want
    a2, b2, c2 = got
    if (a2, b2) == (0, 0):
        return False
    lam = (a2 / a1 if a1 else b2 / b1)
    if lam == 0:
        return False
    if (a2, b2, c2) != (lam * a1, lam * b1, lam * c1):
        return False
    return (lam > 0) == same_sense


# ==================================================================== solving

def _square(p):
    a, h, k, spare = _q(p["a"]), _q(p["h"]), _q(p["k"]), _q(p["spare"])
    # a(x + h)² + spare = k   ->   a x² + 2ah x + (a h² + spare − k) = 0
    roots = _real_roots([a * h * h + spare - k, 2 * a * h, a])
    return _pick(p["ask"], roots)


def _absolute(p):
    a, b, h, k = _q(p["a"]), _q(p["b"]), _q(p["h"]), _q(p["k"])
    m = float(k) / float(a + b)
    roots = sorted({float(h) - m, float(h) + m})
    return _pick(p["ask"], roots)


def _pick(ask, roots):
    if not roots:
        raise AuditError("no real solutions")
    if ask == "sum":
        return sum(roots)
    if ask == "product":
        out = 1.0
        for r in roots:
            out *= r
        return out
    if ask in ("positive", "a_positive"):
        live = [r for r in roots if r > 0]
        if len(live) != 1:
            raise AuditError("not exactly one positive solution")
        return live[0]
    if ask == "negative":
        live = [r for r in roots if r < 0]
        if len(live) != 1:
            raise AuditError("not exactly one negative solution")
        return live[0]
    if ask in ("one_possible", "which", "which_above"):
        return max(roots)
    if ask == "which_value":
        return min(roots)
    raise AuditError(f"unknown question {ask!r}")


def _quadratic(p):
    a, b, c = _q(p["a"]), _q(p["b"]), _q(p["c"])
    if p["ask"] == "sum":
        # the two roots of a quadratic add to −b/a, which is read off the
        # coefficients and needs no roots at all
        if _count_roots([c, b, a]) == 0:
            raise AuditError("no real solutions to add up")
        return -float(b) / float(a)
    return _pick(p["ask"], _real_roots([c, b, a]))


def _formula(p):
    """Which printed option names the solutions of the printed quadratic.

    Every option is read as text and evaluated at the two branches of its own ±
    where it has one; the option that lands on roots this file found numerically
    is the answer.
    """
    a, b, c = _q(p["a"]), _q(p["b"]), _q(p["c"])
    roots = _real_roots([c, b, a])
    if len(roots) != 2:
        raise AuditError("this quadratic does not have two real solutions")
    hits = []
    for opt in p["options"]:
        vals = _branch_values(opt)
        if vals is None:
            continue
        if p["style"] == "single":
            ok = any(abs(v - r) < 1e-6 * max(1.0, abs(r))
                     for v in vals for r in roots)
        else:
            ok = len(vals) == 2 and all(
                any(abs(v - r) < 1e-6 * max(1.0, abs(r)) for r in roots)
                for v in vals) and abs(vals[0] - vals[1]) > 1e-9
        if ok:
            hits.append(opt)
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} options name the solutions {roots}")
    return hits[0]


def _branch_values(option: str):
    """The numbers a printed option stands for, ± expanded and `x =` stripped."""
    out = []
    for piece in option.split(" and "):
        piece = piece.split("=", 1)[1] if "=" in piece else piece
        forms = ([piece.replace("±", "+"), piece.replace("±", "-")]
                 if "±" in piece else [piece])
        for f in forms:
            try:
                out.append(_value_of(f, {}))
            except (ParseError, ZeroDivisionError, ValueError, OverflowError):
                return None
    return out or None


def _factored(p):
    roots = [float(_q(r)) for r in p["roots"]]
    if p["ask"] == "sum":
        return sum(roots)
    out = 1.0
    for r in roots:
        out *= r
    return out


def _shared_factor(p):
    a, b, k, m = _q(p["a"]), _q(p["b"]), _q(p["k"]), _q(p["m"])
    # a(x + k) − b(x − m)(x + k) = 0, expanded and solved numerically
    # −b x² + (a + b m − b k) x + (a k + b m k)
    coeffs = [a * k + b * m * k, a + b * m - b * k, -b]
    return _pick(p["ask"], _real_roots(coeffs))


def _cancel_squares(p):
    pp, r, k = _q(p["p"]), _q(p["r"]), _q(p["k"])
    # (x + p)(x + r) − (x − p)(x − r) − k = 0
    coeffs = [-k, 2 * (pp + r), 0]
    roots = _real_roots(coeffs)
    if len(roots) != 1:
        raise AuditError("the squares did not cancel")
    return roots[0]


def _scaled(p):
    if p["shape"] == "divide":
        k, b, c = _q(p["k"]), _q(p["b"]), _q(p["c"])
        roots = _real_roots([c, k * b, k])
        if not roots:
            raise AuditError("no real solutions")
        x = roots[0]
        return x * x + float(b) * x
    n, k = _q(p["n"]), _q(p["k"])
    roots = _real_roots([-n, 0, k])
    if not roots:
        raise AuditError("no real solutions")
    x = roots[0]
    return float(k) * x * x


def _radical(p):
    a, b = _q(p["a"]), _q(p["b"])
    if p["shape"] == "simple":
        c = _q(p["c"])
        return (float(c) ** 2 - float(b)) / float(a)
    d, e = _q(p["d"]), _q(p["e"])

    def holds(x):
        inside = float(a) * x + float(b)
        if inside < -1e-12:
            return False
        return abs(math.sqrt(max(inside, 0.0)) + float(d) - (x + float(e))) < 1e-7

    shift = e - d
    cand = _real_roots([shift * shift - b, 2 * shift - a, 1])
    live = [x for x in cand if holds(x)]
    if len(live) != 1:
        raise AuditError(f"{len(live)} candidates satisfy the printed equation")
    if p["ask"] == "what_value":
        return live[0]
    want = "{" + f"{_fmt(live[0])}" + "}"
    hits = [o for o in p["options"] if _set_of(o) == [round(live[0], 9)]]
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} options name the solution set {want}")
    return hits[0]


def _set_of(option: str):
    body = option.strip().strip("{}")
    if not body:
        return []
    try:
        return sorted(round(float(v.replace("−", "-").strip()), 9)
                      for v in body.split(","))
    except ValueError:
        return None


def _fmt(v: float) -> str:
    return str(int(round(v))) if abs(v - round(v)) < 1e-9 else f"{v:g}"


def _rational_linear(p):
    pp, a, b, r, m = (_q(p["p"]), _q(p["a"]), _q(p["b"]), _q(p["r"]), _q(p["m"]))

    def f(x):
        den = x + float(b)
        if abs(den) < 1e-12:
            return None
        return float(pp) * (x + float(a)) / den - (float(r) - float(m) / den)

    # p(x + a) − r(x + b) + m = 0 once the denominator is cleared
    cand = _real_roots([pp * a - r * b + m, pp - r])
    live = [x for x in cand if f(x) is not None and abs(f(x)) < 1e-7]
    if len(live) != 1:
        raise AuditError(f"{len(live)} candidates satisfy the printed equation")
    return live[0]


def _rational_quadratic(p):
    if p["shape"] == "cross":
        n, b = _q(p["n"]), _q(p["b"])
        cand = _real_roots([-n, b, 1])
        live = [x for x in cand if abs(x + float(b)) > 1e-9]
        return _pick(p["ask"], live)
    h, k = _q(p["h"]), _q(p["k"])
    # 1/(x + h)² = k  ->  x + h = ±1/√k, and the question asks for x + h
    v = 1.0 / math.sqrt(float(k))
    return v


def _rational_combine(p):
    A, B, C, h = _q(p["A"]), _q(p["B"]), _q(p["C"]), _q(p["h"])

    def f(x):
        if abs(x - float(h)) < 1e-12 or abs(x + float(h)) < 1e-12:
            return None
        return (A * x * x / (x * x - float(h) ** 2) - B * x / (x + float(h))
                - C / (x - float(h)))

    cand = _real_roots([-C * h, B * h - C, A - B])
    live = [x for x in cand if f(x) is not None and abs(f(x)) < 1e-7]
    if len(live) != 1:
        raise AuditError(f"{len(live)} candidates satisfy the printed equation")
    return live[0]


def _product_constant(p):
    pp, u, v, w, g, s, t = (_q(p["p"]), _q(p["u"]), _q(p["v"]), _q(p["w"]),
                            _q(p["g"]), _q(p["s"]), _q(p["t"]))
    # the stated total is s/w − p/u; recovering p from it inverts that
    roots = set()
    roots |= set(_real_roots([pp, u]))
    roots |= set(_real_roots([-g, 0, v]))
    roots |= set(_real_roots([t * pp, -s, w]))
    total = sum(_dedupe(sorted(roots)))
    return (float(s) / float(w) - total) * float(u)


def _paired(p):
    b1, c1, b2, c2 = _q(p["b1"]), _q(p["c1"]), _q(p["b2"]), _q(p["c2"])
    r, s = _real_roots([c1, b1, 1])
    t, u = _real_roots([c2, b2, 1])
    return (r + t) * (s + u)


# ==================================================================== systems

def _curve_line(p):
    A1, B1, C1, D1 = _spec(p["curve"])
    A2, B2, C2, D2 = _spec(p["line"])
    qa = A1
    qb = B1 - C1 * B2 / C2
    qc = D1 - C1 * D2 / C2
    xs = _real_roots([qc, qb, qa])
    if not xs:
        raise AuditError("the line misses the curve")
    ys = [(-float(D2) - float(B2) * x) / float(C2) for x in xs]
    pts = list(zip(xs, ys))
    ask = p["ask"]
    if ask in ("possible_x", "could_be_x", "one_possible_x", "one_solution_x",
               "intersect_x", "solution_x", "meets_at"):
        if ask == "solution_x":
            if len(xs) != 1:
                raise AuditError("the stem promises a single solution")
            return xs[0]
        if ask == "meets_at":
            live = [x for x in xs if abs(x) > 1e-9]
            if len(live) != 1:
                raise AuditError("the stem names one non-zero meeting point")
            return live[0]
        return _closest(p, xs)
    if ask == "y_coordinate":
        if len({round(y, 9) for y in ys}) != 1:
            raise AuditError("the two graphs meet at two different heights")
        return ys[0]
    if ask in ("possible_xy", "positive_xy"):
        prods = [x * y for x, y in pts]
        if ask == "positive_xy":
            live = [x * y for x, y in pts if x > 0]
            if len(live) != 1:
                raise AuditError("not exactly one point with positive x")
            return live[0]
        return _closest(p, prods)
    if ask == "sum_y":
        if len(ys) != 2:
            raise AuditError("the stem names two solutions")
        return ys[0] + ys[1]
    if ask in ("which_pair", "the_pair", "which_pair_plain"):
        return _pair_option(p["options"], pts)
    if ask == "both_pairs":
        return _pairs_option(p["options"], pts)
    raise AuditError(f"unknown question {ask!r}")


def _closest(p, values):
    """Which of the two solutions the item actually keyed.

    Both roots answer "which of the following is a possible value of x", so
    which one is keyed is a property of the item rather than of the mathematics.
    Where there are four printed options it is read off the page -- the root that
    appears among them -- and the check then also catches an option set in which
    *both* roots are printed, which is a question with two right answers. A
    grid-in prints no options, so there the branch the item was built to report
    is taken from its parameters; the roots themselves are still derived here.
    """
    opts = p.get("options")
    if not opts:
        return max(values) if p.get("branch") == "hi" else min(values)
    shown = [v for v in (_as_number(o) for o in opts) if v is not None]
    # the two solutions can share a value -- a line through a parabola can meet
    # it at two points with the same product xy -- and that is one answer, not two
    hits = [v for v in _dedupe(values) if any(abs(v - s) < 1e-7 * max(1.0, abs(v))
                                              for s in shown)]
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} of the solutions appear among the options")
    return hits[0]


def _as_number(text: str):
    """A printed option as a number: 40, −15, −550/9, 20.25, 1,200."""
    t = text.replace("−", "-").replace(",", "").strip()
    try:
        if "/" in t:
            a, b = t.split("/", 1)
            return float(a) / float(b)
        return float(t)
    except (ValueError, ZeroDivisionError):
        return None


def _spec(packed):
    kind = packed[0]
    if kind == "terms":
        out = {"x2": Q(0), "x": Q(0), "y": Q(0), "": Q(0)}
        for c, mon in packed[1]:
            out[mon] += _q(c)
        for c, mon in packed[2]:
            out[mon] -= _q(c)
        return out["x2"], out["x"], out["y"], out[""]
    if kind == "factored":
        r, s = _q(packed[1]), _q(packed[2])
        return Q(1), -(r + s), Q(-1), r * s
    if kind == "square":
        h = _q(packed[1])
        return Q(1), -2 * h, Q(-1), h * h
    pp, k, c, d = (_q(packed[1]), _q(packed[2]), _q(packed[3]), _q(packed[4]))
    return Q(0), -c, pp, k - c * d


def _top_level_groups(text: str) -> list:
    """Every outermost (...) group, so a nested bracket does not end one early.

    `(2/3 \u2212 (1/3)\u221a46, 14/3 + (2/3)\u221a46)` is one point whose
    coordinates carry brackets of their own; a regular expression that stops at
    the first `)` reads it as something else entirely.
    """
    out, depth, start = [], 0, None
    for i, ch in enumerate(text):
        if ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and start is not None:
                out.append(text[start + 1:i])
                start = None
    return out


def _top_level_split(body: str) -> list:
    out, depth, cur = [], 0, ""
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return out


def _read_points(option: str):
    out = []
    for body in _top_level_groups(option):
        parts = _top_level_split(body)
        if len(parts) != 2:
            return None
        try:
            out.append((_value_of(parts[0], {}), _value_of(parts[1], {})))
        except (ParseError, ZeroDivisionError, ValueError):
            return None
    return out or None


def _pair_option(options, pts):
    hits = []
    for o in options:
        got = _read_points(o)
        if got and len(got) == 1 and any(_same_point(got[0], p) for p in pts):
            hits.append(o)
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} options name a point the graphs share")
    return hits[0]


def _pairs_option(options, pts):
    hits = []
    for o in options:
        got = _read_points(o)
        if got and len(got) == len(pts) and all(
                any(_same_point(g, p) for p in pts) for g in got):
            hits.append(o)
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} options name both shared points")
    return hits[0]


def _same_point(a, b, tol: float = 1e-6) -> bool:
    return (abs(a[0] - b[0]) <= tol * max(1.0, abs(b[0]))
            and abs(a[1] - b[1]) <= tol * max(1.0, abs(b[1])))


def _sum_product(p):
    total, product = _q(p["total"]), _q(p["product"])
    roots = _real_roots([product, -total, 1])
    if len(roots) != 2:
        raise AuditError("no pair has that sum and that product")
    return max(roots)


def _secant(p):
    a, b, c = _q(p["a"]), _q(p["b"]), _q(p["c"])
    x1, x2 = _q(p["x1"]), _q(p["x2"])
    y1 = _poly_at([c, b, a], float(x1))
    y2 = _poly_at([c, b, a], float(x2))
    return (y2 - y1) / (float(x2) - float(x1))


# ================================================================ conditions

def _count_equation(p):
    a, b, c = _q(p["a"]), _q(p["b"]), _q(p["c"])
    n = _count_roots([c, b, a])
    return {0: "Zero", 1: "Exactly one", 2: "Exactly two"}[n]


def _count_system(p):
    a, b, c = _q(p["a"]), _q(p["b"]), _q(p["c"])
    m, d = _q(p["m"]), _q(p["d"])
    n = _count_roots([c - d, b - m, a])
    return {0: "There are no solutions.", 1: "There is exactly 1 solution.",
            2: "There are exactly 2 solutions."}[n]


def _symbolic(p):
    """Count the crossings by trying the letters at many positive values."""
    sign, line = int(p["sign"]), p["line"]
    counts = set()
    for av in (0.3, 1.0, 2.5, 7.0):
        for cv in (0.2, 1.5, 4.0, 9.0):
            rhs = {"sum": av + cv, "difference": av - cv, "reverse": cv - av,
                   "negative": -av - cv}[line]
            counts.add(_count_roots([sign * cv - rhs, 0, av]))
    if len(counts) != 1:
        raise AuditError("the count depends on which positive values are chosen")
    return {0: "Zero", 1: "One", 2: "Two"}[counts.pop()]


def _discriminant_constant(p):
    a, b = _q(p["a"]), _q(p["b"])
    c = _q(p.get("c", [0, 1]))
    slot = p.get("slot", "constant")
    side, condition = p.get("side", "left"), p["condition"]
    sgn = 1 if side == "left" else -1
    if condition == "one":
        want = _solve_for_one(a, b, sgn)
        return want
    key = _q(p["key"])
    if slot == "constant":
        n = _count_roots([sgn * key, b, a])
    else:
        n = _count_roots([c, key, a])
    if (condition == "none") != (n == 0):
        raise AuditError(f"the keyed constant leaves {n} real solutions")
    if condition == "more" and n <= 1:
        raise AuditError(f"the keyed constant leaves {n} real solutions")
    return float(key)


def _solve_for_one(a, b, sgn):
    """The constant that leaves exactly one solution, found by bisection.

    The number of real roots is a step function of the constant, so the boundary
    is found by narrowing the interval where that step happens -- never by
    setting a discriminant to zero.
    """
    lo, hi = -1e6, 1e6
    if _count_roots([sgn * lo, b, a]) == _count_roots([sgn * hi, b, a]):
        raise AuditError("no constant changes the number of solutions")
    two_at_lo = _count_roots([sgn * lo, b, a]) == 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if (_count_roots([sgn * mid, b, a]) == 2) == two_at_lo:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2 * (1 if sgn == 1 else 1)


def _tangent_constant(p):
    a, b, pp = _q(p["a"]), _q(p["b"]), _q(p["p"])
    h = _q(p["height"])
    if p["ask"] == "height":
        return float(pp) * float(h)
    # b is the unknown: the value that leaves the line touching the curve once
    lo, hi = 0.0, 1e5
    if _count_roots([-h, lo, a]) == _count_roots([-h, hi, a]):
        raise AuditError("no positive coefficient makes the line a tangent")
    two_at_hi = _count_roots([-h, hi, a]) == 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if (_count_roots([-h, mid, a]) == 2) == two_at_hi:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def _tangent_point(p):
    a, b, c, m = _q(p["a"]), _q(p["b"]), _q(p["c"]), _q(p["m"])
    # the constant slides the line without turning it, so the single meeting
    # point is where the curve's own slope equals the line's -- found here by
    # narrowing in on the x where the gap between them is least
    lo, hi = -1e5, 1e5
    for _ in range(300):
        a1 = lo + (hi - lo) / 3
        a2 = hi - (hi - lo) / 3
        f1 = _gap(a, b, c, m, a1)
        f2 = _gap(a, b, c, m, a2)
        if (f1 < f2) == (a > 0):
            hi = a2
        else:
            lo = a1
    return (lo + hi) / 2


def _gap(a, b, c, m, x):
    return _poly_at([c, b - m, a], x)


def _integer_roots(p):
    k = int(_q(p["k"]))
    sums = sorted({d + k // d for d in range(1, k + 1) if k % d == 0 and d * d <= k})
    return float(sums[0])


# ==================================================================== graphs

def _graph_solution(p):
    kind = p["curve"]
    a, h, k = _q(p["a"]), _q(p["h"]), _q(p["k"])
    m, b = _q(p["m"]), _q(p["b"])
    xs = _drawn_crossings(kind, a, h, k, m, b)
    if len(xs) != 1:
        raise AuditError(f"the drawn graphs cross {len(xs)} times")
    x = xs[0]
    y = float(m) * x + float(b)
    hits = []
    for o in p["options"]:
        got = _read_points(o)
        if got and len(got) == 1 and _same_point(got[0], (x, y)):
            hits.append(o)
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} options name the drawn crossing")
    return hits[0]


def _drawn_crossings(kind, a, h, k, m, b):
    if kind == "parabola":
        return _real_roots([a * h * h + k - b, -(2 * a * h + m), a])
    if kind == "absolute":
        out = []
        for branch in (1, -1):
            roots = _real_roots([k - b - branch * a * h, branch * a - m])
            for x in roots:
                if (branch == 1 and x >= float(h)) or (branch == -1
                                                       and x <= float(h)):
                    out.append(x)
        return _dedupe(out)
    out, prev_x, prev = [], -60.0, None
    x = -60.0
    while x <= 60.0:
        try:
            v = float(k) + float(a) ** (x - float(h)) - (float(m) * x + float(b))
        except OverflowError:
            break
        if prev is not None and (v == 0 or (v > 0) != (prev > 0)):
            out.append(x)
        prev_x, prev = x, v
        x += 0.001
    return _dedupe(out, 1e-2)


def _graph_count(p):
    a, h, k = _q(p["a"]), _q(p["h"]), _q(p["k"])
    m, b = _q(p["m"]), _q(p["b"])
    return float(_count_roots([a * h * h + k - b, -(2 * a * h + m), a]))


def _function_meets(p):
    a, h, k = _q(p["a"]), _q(p["h"]), _q(p["k"])
    m, b = _q(p["m"]), _q(p["b"])
    xs = _real_roots([a * h * h + k - b, -(2 * a * h + m), a])
    if len(xs) != 2:
        raise AuditError("the two functions do not agree at two places")
    return max(xs)


AUDITS = {
    "nleq_isolate_sum": _isolate_sum,
    "nleq_isolate_bracket": _isolate_bracket,
    "nleq_isolate_factor": _isolate_factor,
    "nleq_isolate_denominator": _isolate_denominator,
    "nleq_scale_relation": _scale_relation,
    "nleq_square": _square,
    "nleq_absolute": _absolute,
    "nleq_quadratic": _quadratic,
    "nleq_formula": _formula,
    "nleq_factored": _factored,
    "nleq_shared_factor": _shared_factor,
    "nleq_cancel_squares": _cancel_squares,
    "nleq_scaled": _scaled,
    "nleq_radical": _radical,
    "nleq_rational_linear": _rational_linear,
    "nleq_rational_quadratic": _rational_quadratic,
    "nleq_rational_combine": _rational_combine,
    "nleq_product_constant": _product_constant,
    "nleq_paired": _paired,
    "nleq_curve_line": _curve_line,
    "nleq_sum_product": _sum_product,
    "nleq_secant": _secant,
    "nleq_count_equation": _count_equation,
    "nleq_count_system": _count_system,
    "nleq_symbolic_intersections": _symbolic,
    "nleq_discriminant_constant": _discriminant_constant,
    "nleq_tangent_constant": _tangent_constant,
    "nleq_tangent_point": _tangent_point,
    "nleq_integer_roots": _integer_roots,
    "nleq_graph_solution": _graph_solution,
    "nleq_graph_count": _graph_count,
    "nleq_function_meets": _function_meets,
}
