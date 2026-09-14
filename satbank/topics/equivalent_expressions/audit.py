"""Independent re-derivation of every Equivalent Expressions answer.

Two expressions being equivalent is not a string comparison, so nothing here
compares strings. This file reads the expressions the item actually prints --
the one in the stem and the four in the options -- with its own parser, and
then decides equivalence the only way that is honest: it evaluates both at a
spread of rational points chosen away from any pole and asks whether they
agree everywhere.

Nothing is imported from a template. The generator builds `4x² + 21x + 33` by
multiplying polynomials; this file gets the printed string back, parses it,
and puts numbers through it. A template that expands a bracket wrongly cannot
survive, because the wrong expansion has to agree numerically with the source
expression at a dozen points, which only the right one does.

The same machinery does the rest of the work. A factor is tested by checking
that the polynomial vanishes where the candidate factor vanishes. A constant
hidden in an identity is found by solving for it numerically and then
verifying the identity at fresh points. An exponent is recovered as a
logarithm. None of it re-runs the algebra the template performed.
"""

from __future__ import annotations

import math
from fractions import Fraction as Q

from ...audit import AuditError

TOL = 1e-7
BIG = 1e13

_SUPD = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
         "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-"}
_MINUS = "−-"
_TIMES = "·×*"
_DIGITS = "0123456789"


class ParseError(AuditError):
    pass


# --------------------------------------------------------------- the parser
#
# expr   := ['+'|'−'] term (('+'|'−') term)*
# term   := factor (('·'|'/'|<adjacent>) factor)*
# factor := ['−'] primary [exponent]
# primary:= number | letter | '(' expr ')' | ['ⁿ'] '√' factor
#
# Everything evaluates to a closure env -> float, so a parsed expression can
# be pushed through as many sample points as the check wants.


class _Reader:
    def __init__(self, text: str):
        self.s = text
        self.i = 0

    # -- character helpers

    def _ws(self) -> None:
        while self.i < len(self.s) and self.s[self.i] in " \t\n":
            self.i += 1

    def peek(self) -> str:
        self._ws()
        return self.s[self.i] if self.i < len(self.s) else ""

    def here(self) -> str:
        return self.s[self.i] if self.i < len(self.s) else ""

    def _starts_primary(self) -> bool:
        c = self.peek()
        return bool(c) and (c in _DIGITS or c == "." or (c.isalpha() and c not in _SUPD)
                            or c in "(√" or c in _SUPD)

    # -- grammar

    def expr(self):
        sign = 1
        c = self.peek()
        if c and c in "+" + _MINUS:
            self.i += 1
            sign = -1 if c in _MINUS else 1
        node = self.term()
        if sign < 0:
            node = _neg(node)
        while True:
            c = self.peek()
            if c == "+":
                self.i += 1
                node = _bin(node, self.term(), lambda a, b: a + b)
            elif c and c in _MINUS:
                self.i += 1
                node = _bin(node, self.term(), lambda a, b: a - b)
            else:
                return node

    def term(self):
        node = self.factor()
        while True:
            c = self.peek()
            if c and c in _TIMES:
                self.i += 1
                node = _bin(node, self.factor(), lambda a, b: a * b)
            elif c == "/":
                self.i += 1
                node = _bin(node, self.factor(), _divide)
            elif self._starts_primary():
                node = _bin(node, self.factor(), lambda a, b: a * b)
            else:
                return node

    def factor(self):
        if self.peek() in tuple(_MINUS):
            self.i += 1
            return _neg(self.factor())
        node = self.primary()
        e = self.exponent()
        return node if e is None else _bin(node, e, _power)

    def exponent(self):
        """A superscript run or a '^' -- but a run that belongs to a root index
        is left alone, so 'x²·³√x' reads as x² times the cube root of x."""
        j, run = self.i, ""
        while j < len(self.s) and self.s[j] in _SUPD:
            run += _SUPD[self.s[j]]
            j += 1
        if run:
            if j < len(self.s) and self.s[j] == "√":
                return None
            self.i = j
            return _const(float(int(run)))
        if self.here() == "^":
            self.i += 1
            if self.here() == "(":
                self.i += 1
                node = self.expr()
                if self.peek() != ")":
                    raise ParseError(f"unclosed exponent in {self.s!r}")
                self.i += 1
                return node
            j, digits = self.i, ""
            while j < len(self.s) and (self.s[j] in _DIGITS
                                       or (self.s[j] in _MINUS and not digits)):
                digits += "-" if self.s[j] in _MINUS else self.s[j]
                j += 1
            if not digits:
                raise ParseError(f"'^' with no exponent in {self.s!r}")
            self.i = j
            return _const(float(int(digits)))
        return None

    def primary(self):
        c = self.peek()
        if c == "(":
            self.i += 1
            node = self.expr()
            if self.peek() != ")":
                raise ParseError(f"unclosed bracket in {self.s!r}")
            self.i += 1
            return node
        if c == "√":
            self.i += 1
            return _nth_root(self.factor(), 2)
        if c in _SUPD:
            j, run = self.i, ""
            while j < len(self.s) and self.s[j] in _SUPD:
                run += _SUPD[self.s[j]]
                j += 1
            if j < len(self.s) and self.s[j] == "√":
                self.i = j + 1
                return _nth_root(self.factor(), int(run))
            raise ParseError(f"stray superscript in {self.s!r}")
        if c in _DIGITS or c == ".":
            j, body = self.i, ""
            while j < len(self.s) and (self.s[j] in _DIGITS or self.s[j] in ".,"):
                if self.s[j] != ",":
                    body += self.s[j]
                j += 1
            self.i = j
            return _const(float(body))
        if c.isalpha():
            self.i += 1
            return _var(c)
        raise ParseError(f"cannot read {self.s[self.i:self.i + 12]!r} in {self.s!r}")


def _const(v):
    return lambda env: v


def _var(name):
    def read(env):
        if name not in env:
            raise ParseError(f"no value for {name!r}")
        return env[name]
    return read


def _neg(f):
    return lambda env: -f(env)


def _bin(a, b, op):
    return lambda env: op(a(env), b(env))


def _divide(a, b):
    if b == 0:
        raise ZeroDivisionError
    return a / b


def _power(a, e):
    if a < 0 and e != int(e):
        raise ValueError("negative base with a fractional exponent")
    if a == 0 and e < 0:
        raise ZeroDivisionError
    return a ** e


def _nth_root(f, n: int):
    def take(env):
        v = f(env)
        if v < 0:
            if n % 2 == 0:
                raise ValueError("even root of a negative number")
            return -((-v) ** (1.0 / n))
        return v ** (1.0 / n)
    return take


def parse(text: str):
    """A printed expression -> a function of an environment."""
    r = _Reader(str(text))
    node = r.expr()
    if r.peek():
        raise ParseError(f"trailing {r.s[r.i:]!r} in {text!r}")
    return node


# -------------------------------------------------------- numeric machinery

# Three windows of sample points, tried in turn. The first is the working one;
# the second keeps a degree-thirty power inside double precision; the third is
# for expressions that are undefined above 1.
WINDOWS = ((1.05, 4.25), (1.02, 1.43), (0.21, 0.94))


def _points(names: list[str], n: int = 18, window: int = 0) -> list[dict]:
    """A deterministic spread of rational sample points.

    Kept off the small rationals where the source's denominators -- x − 2,
    4x − 5, x + 7 -- have their poles, and away from 1, where every power of a
    variable takes the same value.
    """
    lo, hi = WINDOWS[window]
    out, s = [], 12345
    for _ in range(n):
        env = {}
        for v in names:
            s = (s * 1103515245 + 12345) % 2147483648
            env[v] = round(lo + (hi - lo) * (s / 2147483648), 6)
        out.append(env)
    return out


def _with_defs(env: dict, defs: dict) -> dict:
    """Resolve 'p = 3x + 4' style definitions into the environment."""
    env = dict(env)
    for name, body in (defs or {}).items():
        env[name] = parse(body)(env)
    return env


def _value(fn, env: dict, defs: dict):
    v = fn(_with_defs(env, defs))
    if not math.isfinite(v) or abs(v) > BIG:
        return None
    return v


def agree(f, g, names: list[str], defs: dict | None = None,
          need: int = 6) -> bool:
    """Do two parsed expressions take the same value everywhere they are defined?

    Two different polynomials of degree d agree at no more than d points, and
    nothing in this topic runs past degree eleven, so agreement at eight or
    more spread-out points is agreement.
    """
    for window in range(len(WINDOWS)):
        seen, same = 0, True
        for env in _points(names, 24, window):
            try:
                a, b = _value(f, env, defs), _value(g, env, defs)
            except (ZeroDivisionError, ValueError, OverflowError, ParseError):
                continue
            if a is None or b is None:
                continue
            if abs(a - b) > TOL * max(1.0, abs(a), abs(b)):
                same = False
                break
            seen += 1
        if not same:
            return False
        if seen >= need:
            return True
    raise AuditError("could not sample the expression away from its poles")


def _names(p: dict) -> list[str]:
    return list(p.get("vars") or ["x"])


def _pick(p: dict, source: str) -> str:
    """The one option that is equivalent to the source expression.

    Two matches is a broken item -- a distractor that is also right -- and is
    reported as loudly as no match at all.
    """
    src = parse(source)
    names, defs = _names(p), p.get("defs") or {}
    hits = [o for o in p["options"] if agree(src, parse(o), names, defs)]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise AuditError(f"no option is equivalent to {source!r}")
    raise AuditError(f"{len(hits)} options are equivalent to {source!r}: {hits}")


# ------------------------------------------------------- polynomial reading

def coeffs_of(fn, var: str, degree: int, defs: dict | None = None) -> list[float]:
    """Read a printed polynomial's coefficients back out of it, numerically.

    Evaluate at degree+1 points and solve the Vandermonde system. Nothing is
    assumed about how the expression was built.
    """
    xs = [1.13 + 0.37 * k for k in range(degree + 1)]
    rows = []
    for x in xs:
        env = _with_defs({var: x}, defs or {})
        rows.append([x ** j for j in range(degree + 1)] + [fn(env)])
    return _solve(rows)


def _solve(rows: list[list[float]]) -> list[float]:
    """Gaussian elimination with partial pivoting."""
    n = len(rows)
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(rows[r][c]))
        if abs(rows[piv][c]) < 1e-12:
            raise AuditError("the sample points do not determine the coefficients")
        rows[c], rows[piv] = rows[piv], rows[c]
        for r in range(n):
            if r == c:
                continue
            f = rows[r][c] / rows[c][c]
            for k in range(c, n + 1):
                rows[r][k] -= f * rows[c][k]
    return [rows[i][n] / rows[i][i] for i in range(n)]


def _roots(fn, var: str, lo: float = -260.0, hi: float = 260.0,
           step: float = 0.25) -> list[float]:
    """Every real root in a window, by scanning for sign changes and bisecting."""
    out, x, prev = [], lo, None
    while x <= hi:
        try:
            v = fn({var: x})
        except (ZeroDivisionError, ValueError, OverflowError):
            v = None
        if v is not None and prev is not None and prev[1] is not None:
            if v == 0:
                out.append(x)
            elif (v > 0) != (prev[1] > 0):
                out.append(_bisect(fn, var, prev[0], x))
        prev = (x, v)
        x = round(x + step, 6)
    return out


def _bisect(fn, var: str, lo: float, hi: float) -> float:
    flo = fn({var: lo})
    for _ in range(120):
        mid = (lo + hi) / 2
        if mid == lo or mid == hi:
            break
        if (fn({var: mid}) > 0) == (flo > 0):
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _is_factor(poly_text: str, factor_text: str, names: list[str]) -> bool:
    """A polynomial has a linear factor exactly when it vanishes on that factor.

    The candidate is solved for the first variable -- numerically -- with the
    other variables held at sample values, and the polynomial is read there.
    No division is performed.
    """
    P, F = parse(poly_text), parse(factor_text)
    first, rest = names[0], names[1:]
    tested = 0
    for env0 in _points(rest or [], 5) if rest else [{}]:
        fn = lambda env: F({**env0, **env})                          # noqa: E731
        rts = _roots(fn, first, -60.0, 60.0, 0.5)
        if not rts:
            continue
        r = rts[0]
        here = P({**env0, first: r})
        near = max(abs(P({**env0, first: r + d})) for d in (0.5, -0.5, 1.0))
        if abs(here) > 1e-6 * max(1.0, near):
            return False
        tested += 1
    if not tested:
        raise AuditError(f"could not locate the zero of {factor_text!r}")
    return True


def _affine_letter(lhs: str, rhs: str, letter: str, names: list[str],
                   defs: dict | None = None) -> float:
    """The value of the constant that makes an identity true.

    Solved by fitting, not by rearranging: the difference between the two
    sides is read at two trial values of the letter, the crossing is taken,
    and the identity is then verified at a spread of fresh points. When the
    difference turns out not to be affine in the letter -- a constant inside a
    denominator -- the crossing is bracketed and bisected instead.
    """
    L, R = parse(lhs), parse(rhs)
    base = _points(names, 12)

    def residual(u: float, env: dict):
        e = _with_defs({**env, letter: u}, defs or {})
        return L(e) - R(e)

    def check(u: float) -> bool:
        ok = 0
        for env in base:
            try:
                e = _with_defs({**env, letter: u}, defs or {})
                d, scale = L(e) - R(e), abs(R(e))
            except (ZeroDivisionError, ValueError, OverflowError, ParseError):
                continue
            if not (math.isfinite(d) and math.isfinite(scale)):
                continue
            if abs(d) > 1e-6 * max(1.0, scale):
                return False
            ok += 1
        return ok >= 4

    for env in base[:4]:
        try:
            r0, r1 = residual(0.0, env), residual(1.0, env)
        except (ZeroDivisionError, ValueError, OverflowError, ParseError):
            continue
        if not (math.isfinite(r0) and math.isfinite(r1)):
            continue
        if abs(r1 - r0) > 1e-12:
            u = -r0 / (r1 - r0)
            if check(u):
                return u
    # not affine in the letter: bracket the crossing and bisect
    for env in base[:4]:
        grid = [-400 + 0.5 * k for k in range(1601)]
        prev = None
        for u in grid:
            try:
                d = residual(u, env)
            except (ZeroDivisionError, ValueError, OverflowError, ParseError):
                prev = None
                continue
            if not math.isfinite(d):
                prev = None
                continue
            if prev is not None and (d > 0) != (prev[1] > 0):
                lo, hi = prev[0], u
                for _ in range(120):
                    mid = (lo + hi) / 2
                    try:
                        dm = residual(mid, env)
                    except (ZeroDivisionError, ValueError, OverflowError):
                        break
                    if (dm > 0) == (prev[1] > 0):
                        lo = mid
                    else:
                        hi = mid
                cand = (lo + hi) / 2
                if check(cand):
                    return cand
            prev = (u, d)
    raise AuditError(f"no value of {letter!r} makes {lhs!r} equal {rhs!r}")


def _tidy(v: float) -> float:
    """Snap a solved constant to the nearby simple rational it plainly is."""
    f = Q(v).limit_denominator(2000)
    return float(f) if abs(float(f) - v) < 1e-7 else v


# ----------------------------------------------------------- the solvers
#
# One question -- "which printed option is equivalent to the printed
# expression?" -- serves every template whose options are expressions. The
# templates whose answer is a number each get their own derivation.

def equivalent(p: dict) -> str:
    return _pick(p, p["expr"])


def which_factor(p: dict) -> str:
    names = _names(p)
    if p["shape"] == "roman":
        flags = [_is_factor(p["poly"], c, names) for c in p["candidates"]]
        return p["verdicts"]["".join("1" if f else "0" for f in flags)]
    hits = [o for o in p["options"] if _is_factor(p["poly"], o, names)]
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} of the options divide {p['poly']!r}")
    return hits[0]


def coef_combination(p: dict) -> float:
    fn = parse(p["expr"])
    c = coeffs_of(fn, p["var"], p["degree"], p.get("defs"))
    return _tidy(sum(w * c[i] for i, w in p["weights"]))


def match_constant(p: dict) -> float:
    if p["shape"] == "cubic_pair":
        # (a·v + c)(d·v² − b·v + e) spreads to
        #   a·d v³ + (c·d − a·b) v² + (a·e − c·b) v + c·e,
        # so the cubic that is printed hands back a and then b.
        c, d, e = float(p["c"]), float(p["d"]), float(p["e"])
        r = coeffs_of(parse(p["rhs"]), p["var"], 3)
        if abs(d) < 1e-12:
            raise AuditError("the quadratic factor has no leading coefficient")
        a = r[3] / d
        if abs(a) < 1e-12:
            raise AuditError("the product would not be a cubic")
        b = (c * d - r[2]) / a
        if abs(a * e - c * b - r[1]) > 1e-6 * max(1.0, abs(r[1])):
            raise AuditError("the printed cubic is not that product")
        if abs(c * e - r[0]) > 1e-6 * max(1.0, abs(r[0])):
            raise AuditError("the constant terms do not agree")
        return _tidy({"product": a * b, "sum": a + b}[p["ask"]])
    u = _affine_letter(p["lhs"], p["rhs"], p["letter"], _names(p), p.get("defs"))
    return _tidy(u)


def factor_constant(p: dict) -> float:
    var = p["var"]
    if p["shape"] == "cubic_root":
        fn = parse(p["expr"])
        bs = sorted(-r for r in _roots(lambda env: fn(env), var) if -r > 1e-6)
        if not bs:
            raise AuditError("the polynomial has no factor of that form")
        return _tidy(bs[0] if p["ask"] == "smallest" else bs[-1])
    if p["shape"] == "sq_diff":
        # c·v² + k is c(v − K)(v + K) exactly when K² = −k/c
        L = parse(p["expr"])
        lead = float(p["lead"])
        env = {var: 2.3}
        k = L(env) - lead * env[var] ** 2
        if -k / lead <= 0:
            raise AuditError("that difference of squares has no real constant")
        return _tidy(math.sqrt(-k / lead))
    # (v² − c)/(v − b) is v + b only when c = b²; try each printed candidate
    good = []
    for v in p["candidates"]:
        for b in range(1, int(p.get("max_b", 200)) + 1):
            src = parse(p["numerator"].replace("@c", repr(float(v)))
                        .replace("@b", str(b)))
            tgt = parse(p["target"].replace("@b", str(b)))
            den = parse(p["denominator"].replace("@b", str(b)))
            try:
                if agree(_bin(src, den, _divide), tgt, [var], need=4):
                    good.append(float(v))
                    break
            except AuditError:
                continue
    if len(good) != 1:
        raise AuditError(f"{len(good)} of the candidates can be the constant")
    return good[0]


def exponent_value(p: dict) -> float:
    """The expression is a power of its base; read the exponent as a logarithm."""
    fn, base = parse(p["expr"]), parse(p["base"])
    names = _names(p)
    got = []
    for env in _points(names, 8):
        try:
            v, b = fn(env), base(env)
        except (ZeroDivisionError, ValueError, OverflowError, ParseError):
            continue
        if v is None or v <= 0 or b <= 0 or abs(b - 1) < 0.05:
            continue
        got.append(math.log(v) / math.log(b))
    if len(got) < 4:
        raise AuditError("could not read the exponent off the expression")
    if max(got) - min(got) > 1e-6 * max(1.0, abs(got[0])):
        raise AuditError("the expression is not a single power of that base")
    return _tidy(sum(got) / len(got) / float(p.get("mult", 1)))


def rational_combine(p: dict):
    """Two fractions over one denominator, or the numerator that results."""
    if p["shape"] != "identity":
        return _pick(p, p["expr"])
    # multiply the printed sum by the printed denominator and read the linear
    # numerator back out of the product
    lhs, den = parse(p["expr"]), parse(p["denominator"])
    top = _bin(lhs, den, lambda a, b: a * b)
    t, r = coeffs_of(top, p["var"], 1)
    return _tidy({"product": r * t, "sum": r + t}[p["ask"]])


def divide_remainder(p: dict):
    """The quotient of a division, as an expression or as a pair of integers."""
    if p["shape"] != "coef_sum":
        return _pick(p, p["expr"])
    return coef_combination(p)


AUDITS = {
    "eqx_combine_like": equivalent,
    "eqx_add_polys": equivalent,
    "eqx_distribute": equivalent,
    "eqx_product": equivalent,
    "eqx_expand_square": equivalent,
    "eqx_substitute": equivalent,
    "eqx_factor_gcf": equivalent,
    "eqx_factor_quadratic": equivalent,
    "eqx_difference_squares": equivalent,
    "eqx_complete_square": equivalent,
    "eqx_monomial_power": equivalent,
    "eqx_radical_form": equivalent,
    "eqx_telescope": equivalent,
    "eqx_rational_simplify": equivalent,
    "eqx_rational_combine": rational_combine,
    "eqx_divide_remainder": divide_remainder,
    "eqx_which_factor": which_factor,
    "eqx_coef_combination": coef_combination,
    "eqx_match_constant": match_constant,
    "eqx_factor_constant": factor_constant,
    "eqx_exponent_value": exponent_value,
}
