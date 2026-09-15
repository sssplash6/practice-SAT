"""Algebraic surfaces: how a polynomial, an equation, a point or an interval
is written on an SAT page.

Geometry answers are single values, which `exact.py` covers. The rest of the
exam answers with expressions -- 3x - 7, (x - 4)(x + 2), y = 2x + 5, (3, -1),
x > 5/2 -- and an item is wrong if the mathematics is right but the rendering
is not: a stray "1x", a "+ -3", a fraction printed as 0.6666666.

Everything here is exact: coefficients are Fractions, and nothing is rounded
unless a template asks for it.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from fractions import Fraction as Q
from math import gcd, isqrt

__all__ = ["Q", "num", "fmt_num", "fmt_frac", "Poly", "linear", "quadratic",
           "fmt_eq", "fmt_point", "fmt_ineq", "fmt_interval", "fn_of",
           "line_through", "slope", "exp_model", "sign_join", "fmt_percent", "SYMBOL",
           "fmt_places", "fmt_money", "fmt_band", "fmt_mixed",
           "parse", "agree", "parse_point", "ParseError"]


def num(x) -> Q:
    """Anything numeric to an exact Fraction. Floats come in as decimals.

    An `Exact` is accepted when it is a plain rational, so a template may hand
    a geometry value straight to the algebra renderers; one carrying a pi or a
    radical is refused rather than silently flattened to a decimal.
    """
    if isinstance(x, Q):
        return x
    if isinstance(x, float):
        return Q(str(x))
    if hasattr(x, "coef") and hasattr(x, "pi_exp"):                 # an Exact
        if not x.is_rational:
            raise ValueError(f"{x!r} is not rational; it cannot be an exact Fraction")
        return x.coef
    return Q(x)


def fmt_num(v, tex: bool = False, group: bool = True, group_from: int = 1_000) -> str:
    """A number the way an SAT option prints it: 3, -1/2, 2.5, 1,200.

    The source separates thousands from 1,000 up -- it prints 4,529 and 1,277
    -- so that is the default. Two topics kept a private copy of this function
    for exactly that reason before it was a parameter.
    """
    v = num(v)
    if v.denominator == 1:
        n = v.numerator
        return f"{n:,}" if group and abs(n) >= group_from else str(n)
    return fmt_frac(v, tex)


def fmt_frac(v, tex: bool = False) -> str:
    v = num(v)
    if v.denominator == 1:
        return str(v.numerator)
    sign = "-" if v < 0 else ""
    n, d = abs(v.numerator), v.denominator
    return rf"{sign}\frac{{{n}}}{{{d}}}" if tex else f"{sign}{n}/{d}"


def fmt_places(v, places: int = 2) -> str:
    """A number at a fixed number of decimal places: 609/10 -> "60.90".

    Rounds half away from zero, the way a till does, not the way floats do.
    """
    v = num(v)
    scale = 10 ** places
    n = (abs(v) * scale + Q(1, 2)).__floor__()
    sign = "-" if v < 0 else ""
    whole, frac = divmod(n, scale)
    return f"{sign}{whole:,}" if places == 0 else f"{sign}{whole:,}.{frac:0{places}d}"


def fmt_money(v, places: int = 2) -> str:
    """$60.90. A money answer is computed exactly and only rounded to print."""
    return "$" + fmt_places(v, places)


def fmt_percent(v, places: int = 0) -> str:
    """12.5 -> '12.5%', 40 -> '40%'. Trailing zeros are never printed."""
    v = num(v)
    if v.denominator == 1:
        return f"{v.numerator}%"
    s = f"{float(v):.{places or 2}f}".rstrip("0").rstrip(".")
    return f"{s}%"


def sign_join(parts: list[str]) -> str:
    """Join already-signed terms into a readable sum: '3x - 7', not '3x + -7'."""
    out = parts[0]
    for p in parts[1:]:
        out += f" - {p[1:]}" if p.startswith("-") else f" + {p}"
    return out


@dataclass(frozen=True)
class Poly:
    """A polynomial in one variable, lowest degree first: (c0, c1, c2, ...)."""
    coef: tuple

    # ------------------------------------------------------------ building

    @staticmethod
    def of(*coef) -> "Poly":
        """Poly.of(c0, c1, ...) -- trailing zeros are dropped."""
        c = [num(x) for x in coef]
        while len(c) > 1 and c[-1] == 0:
            c.pop()
        return Poly(tuple(c))

    @staticmethod
    def from_roots(*roots, lead=1) -> "Poly":
        p = Poly.of(lead)
        for r in roots:
            p = p * Poly.of(-num(r), 1)
        return p

    # ---------------------------------------------------------- arithmetic

    def __add__(self, other) -> "Poly":
        o = other if isinstance(other, Poly) else Poly.of(other)
        n = max(len(self.coef), len(o.coef))
        return Poly.of(*[self[i] + o[i] for i in range(n)])

    __radd__ = __add__

    def __neg__(self) -> "Poly":
        return Poly.of(*[-c for c in self.coef])

    def __sub__(self, other) -> "Poly":
        return self + (-(other if isinstance(other, Poly) else Poly.of(other)))

    def __rsub__(self, other) -> "Poly":
        return (-self) + other

    def __mul__(self, other) -> "Poly":
        o = other if isinstance(other, Poly) else Poly.of(other)
        out = [Q(0)] * (len(self.coef) + len(o.coef) - 1)
        for i, a in enumerate(self.coef):
            for j, b in enumerate(o.coef):
                out[i + j] += a * b
        return Poly.of(*out)

    __rmul__ = __mul__

    def __getitem__(self, i: int) -> Q:
        return self.coef[i] if i < len(self.coef) else Q(0)

    def __call__(self, x) -> Q:
        x = num(x)
        return sum((c * x ** i for i, c in enumerate(self.coef)), Q(0))

    @property
    def degree(self) -> int:
        return len(self.coef) - 1

    # ----------------------------------------------------------- rendering

    def text(self, var: str = "x", tex: bool = False) -> str:
        """'3x^2 - x + 4'. A coefficient of 1 is invisible, 0 terms vanish."""
        terms = []
        for i in range(self.degree, -1, -1):
            c = self[i]
            if c == 0:
                continue
            body = "" if i == 0 else (var if i == 1 else
                                      (f"{var}^{{{i}}}" if tex else f"{var}^{i}"))
            if i and abs(c) == 1:
                head = "-" if c < 0 else ""
            elif c.denominator != 1 and i:
                # a fraction against a variable needs its own brackets in plain
                # text, or -1/2x reads as -1/(2x)
                head = fmt_frac(c, tex) if tex else f"({fmt_frac(c)})"
            else:
                head = fmt_num(c, tex)
            terms.append(f"{head}{body}")
        if not terms:
            return "0"
        return sign_join(terms)

    # ------------------------------------------------------------ analysis

    def roots(self) -> list[Q] | None:
        """Exact rational roots, or None when they are irrational.

        Only linear and quadratic, which is all the SAT asks to solve exactly.
        """
        if self.degree == 1:
            return [-self[0] / self[1]]
        if self.degree != 2:
            return None
        a, b, c = self[2], self[1], self[0]
        disc = b * b - 4 * a * c
        if disc < 0:
            return []
        r = _exact_sqrt(disc)
        if r is None:
            return None
        return sorted({(-b - r) / (2 * a), (-b + r) / (2 * a)})

    def discriminant(self) -> Q:
        return self[1] ** 2 - 4 * self[2] * self[0]

    def vertex(self) -> tuple[Q, Q]:
        h = -self[1] / (2 * self[2])
        return h, self(h)

    def factored(self, var: str = "x") -> str | None:
        """'(x - 3)(2x + 1)' when the quadratic factors over the rationals."""
        if self.degree != 2:
            return None
        roots = self.roots()
        if not roots or len(roots) == 0:
            return None
        a = self[2]
        parts = []
        lead = a
        for r in (roots if len(roots) == 2 else roots * 2):
            d = r.denominator
            parts.append((d, -r.numerator))
            lead = lead / d
        if lead != 1:
            head = fmt_num(lead)
        else:
            head = ""
        body = "".join(f"({_lin_text(m, b, var)})" for m, b in parts)
        return head + body


def _lin_text(m, b, var: str) -> str:
    m, b = num(m), num(b)
    head = var if m == 1 else (f"-{var}" if m == -1 else f"{fmt_num(m)}{var}")
    if b == 0:
        return head
    return f"{head} - {fmt_num(-b)}" if b < 0 else f"{head} + {fmt_num(b)}"


def _exact_sqrt(q: Q) -> Q | None:
    if q < 0:
        return None
    n, d = q.numerator, q.denominator
    rn, rd = isqrt(n), isqrt(d)
    return Q(rn, rd) if rn * rn == n and rd * rd == d else None


def linear(m, b) -> Poly:
    return Poly.of(b, m)


def quadratic(a, b, c) -> Poly:
    return Poly.of(c, b, a)


def slope(p1: tuple, p2: tuple) -> Q:
    (x1, y1), (x2, y2) = p1, p2
    if x1 == x2:
        raise ValueError("vertical line has no slope")
    return (num(y2) - num(y1)) / (num(x2) - num(x1))


def line_through(p1: tuple, p2: tuple) -> Poly:
    m = slope(p1, p2)
    return linear(m, num(p1[1]) - m * num(p1[0]))


def fmt_eq(lhs: str, rhs: str) -> str:
    return f"{lhs} = {rhs}"


def fmt_point(x, y, tex: bool = False) -> str:
    return f"({fmt_num(x, tex)}, {fmt_num(y, tex)})"


SYMBOL = {"<=": "≤", ">=": "≥", "<": "<", ">": ">", "!=": "≠", "=": "="}


def fmt_ineq(lhs: str, op: str, rhs: str) -> str:
    """op is one of < <= > >= = !=, printed with the symbols the SAT uses."""
    return f"{lhs} {SYMBOL[op]} {rhs}"


def fmt_band(lo, var: str, hi, ops=("<=", "<=")) -> str:
    """A quantity caught between two bounds, as the page prints it: 3 ≤ x < 8."""
    return f"{fmt_num(lo)} {SYMBOL[ops[0]]} {var} {SYMBOL[ops[1]]} {fmt_num(hi)}"


def fmt_mixed(v) -> str:
    """11 2/3, the way a measurement is written when it is not a decimal."""
    v = num(v)
    if v.denominator == 1:
        return fmt_num(v)
    sign = "-" if v < 0 else ""
    whole, rest = divmod(abs(v.numerator), v.denominator)
    return f"{sign}{whole} {rest}/{v.denominator}" if whole else f"{sign}{rest}/{v.denominator}"


def fmt_interval(lo, hi, closed=(True, True)) -> str:
    l = "[" if closed[0] else "("
    r = "]" if closed[1] else ")"
    return f"{l}{fmt_num(lo)}, {fmt_num(hi)}{r}"


def fn_of(name: str, var: str, body: str) -> str:
    return f"{name}({var}) = {body}"


def exp_model(a, rate, var: str = "x", per: str = "") -> str:
    """a(1 + r)^x, written the way growth items write it: 250(1.04)^x."""
    r = num(rate)
    base = 1 + r
    b = fmt_num(base) if base.denominator == 1 else _decimal(base)
    return f"{fmt_num(a)}({b})^{var}" + (f", {per}" if per else "")


def _decimal(q: Q) -> str:
    s = f"{float(q):.10f}".rstrip("0").rstrip(".")
    return s


# ---------------------------------------------------------------- reading back
#
# Equivalence is not a string comparison. "Which of the following is
# equivalent" items, and any check that has to decide a WRONG option as
# mathematics, need to read the printed page back and evaluate it -- and the
# reader must share nothing with the printer, or a rendering bug that drops a
# minus sign is invisible to it.
#
# Equivalent Expressions shipped two parsers of its own before this existed.

_TOKEN = re.compile(r"""
    (?P<num>\d+(?:\.\d+)?(?:,\d{3})*|\.\d+)   # 3, 2.5, 1,200
  | (?P<name>[A-Za-z][A-Za-z_]*)              # x, pi, sqrt
  | (?P<op>\*\*|[-+*/^()|,=<>≤≥])
  | (?P<sym>[π√·×−⁰¹²³⁴⁵⁶⁷⁸⁹½⅓¼])
  | (?P<space>\s+)
""", re.X)

_SUPER = {"⁰": 0, "¹": 1, "²": 2, "³": 3, "⁴": 4, "⁵": 5,
          "⁶": 6, "⁷": 7, "⁸": 8, "⁹": 9}


class ParseError(ValueError):
    """The printed text is not an expression this reader understands."""


def _lex(text: str) -> list:
    out, i = [], 0
    text = text.replace("−", "-").replace("×", "*").replace("·", "*")
    while i < len(text):
        m = _TOKEN.match(text, i)
        if not m:
            raise ParseError(f"cannot read {text[i:i + 12]!r} in {text!r}")
        i = m.end()
        if m.lastgroup == "space":
            continue
        if m.lastgroup == "num":
            out.append(("num", Q(m.group().replace(",", ""))))
        elif m.lastgroup == "sym":
            s = m.group()
            if s in _SUPER:
                out.append(("sup", _SUPER[s]))
            elif s == "π":
                out.append(("name", "pi"))
            elif s == "√":
                out.append(("name", "sqrt"))
            elif s == "½":
                out.append(("num", Q(1, 2)))
            elif s == "⅓":
                out.append(("num", Q(1, 3)))
            else:
                out.append(("num", Q(1, 4)))
        else:
            out.append((m.lastgroup, m.group()))
    return out


def parse(text: str):
    """Read printed mathematics back into a function of its variables.

    Returns `f(**values) -> float`, so two printed expressions can be compared
    by evaluating both rather than by matching their text: 40n and 160n/4 are
    one expression, and no string comparison will say so.

    Understands what the engine prints -- juxtaposition as multiplication
    (3x, 2(x+1)), typeset superscripts (x²), π and √, a caret or ** for a
    power, and thousands separators. Raises ParseError on anything else.
    """
    toks = _lex(str(text))
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else (None, None)

    def eat(kind=None, val=None):
        nonlocal pos
        k, v = peek()
        if k is None or (kind and k != kind) or (val and v != val):
            raise ParseError(f"unexpected {v!r} in {text!r}")
        pos += 1
        return v

    def atom(env):
        k, v = peek()
        if k == "num":
            eat()
            return float(v)
        if k == "name":
            eat()
            if v == "sqrt":
                return math.sqrt(factor(env))
            if v in ("pi",):
                return math.pi
            if v not in env:
                raise ParseError(f"no value given for {v!r}")
            return float(env[v])
        if (k, v) == ("op", "("):
            eat()
            inner = expression(env)
            eat("op", ")")
            return inner
        if (k, v) == ("op", "|"):
            eat()
            inner = expression(env)
            eat("op", "|")
            return abs(inner)
        if (k, v) == ("op", "-"):
            eat()
            return -factor(env)
        if (k, v) == ("op", "+"):
            eat()
            return factor(env)
        raise ParseError(f"unexpected {v!r} in {text!r}")

    def factor(env):
        base = atom(env)
        while True:
            k, v = peek()
            if k == "sup":
                base **= eat()
            elif (k, v) in (("op", "^"), ("op", "**")):
                eat()
                base **= factor(env)
            else:
                return base

    def term(env):
        value = factor(env)
        while True:
            k, v = peek()
            if (k, v) == ("op", "*"):
                eat()
                value *= factor(env)
            elif (k, v) == ("op", "/"):
                eat()
                d = factor(env)
                if d == 0:
                    raise ZeroDivisionError
                value /= d
            elif k in ("num", "name") or (k, v) == ("op", "("):
                value *= factor(env)          # juxtaposition: 3x, 2(x + 1)
            else:
                return value

    def expression(env):
        value = term(env)
        while True:
            k, v = peek()
            if (k, v) == ("op", "+"):
                eat()
                value += term(env)
            elif (k, v) == ("op", "-"):
                eat()
                value -= term(env)
            else:
                return value

    def run(**values):
        nonlocal pos
        pos = 0
        out = expression(values)
        if pos != len(toks):
            raise ParseError(f"trailing {toks[pos][1]!r} in {text!r}")
        return out

    return run


def agree(a, b, variables=("x",), points=(Q(2), Q(3), Q(5, 2), Q(-3), Q(7), Q(-5, 3)),
          tol: float = 1e-9) -> bool:
    """Do two printed expressions mean the same thing?

    Evaluated at several rational points rather than compared as text, which
    is the only honest test: 40n and 160n/4 are one expression. A point where
    either side is undefined is skipped, and two expressions that agree
    nowhere defined are not equal.
    """
    fa = parse(a) if isinstance(a, str) else a
    fb = parse(b) if isinstance(b, str) else b
    seen = 0
    for i, p in enumerate(points):
        env = {v: p + Q(i * 3 + n, 7) for n, v in enumerate(variables)}
        try:
            va, vb = fa(**env), fb(**env)
        except (ZeroDivisionError, ValueError, OverflowError, ParseError):
            continue
        if not (math.isfinite(va) and math.isfinite(vb)):
            continue
        seen += 1
        if abs(va - vb) > tol * max(1.0, abs(va), abs(vb)):
            return False
    return seen >= 2


def parse_point(text: str, variables=()) -> tuple:
    """Read a printed ordered pair back: "(9, 5)" or "(-4r/11 + 29/11, r)".

    Each coordinate is parsed as an expression, so a parameterised point
    reads too. Returns a tuple of callables when `variables` is given, and a
    tuple of floats when it is not.
    """
    t = str(text).strip()
    if not (t.startswith("(") and t.endswith(")")):
        raise ParseError(f"{text!r} is not an ordered pair")
    depth, parts, cur = 0, [], ""
    for ch in t[1:-1]:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    if len(parts) != 2:
        raise ParseError(f"{text!r} does not have two coordinates")
    fs = tuple(parse(p) for p in parts)
    return fs if variables else tuple(f() for f in fs)
