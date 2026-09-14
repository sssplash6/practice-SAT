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

from dataclasses import dataclass
from fractions import Fraction as Q
from math import gcd, isqrt

__all__ = ["Q", "num", "fmt_num", "fmt_frac", "Poly", "linear", "quadratic",
           "fmt_eq", "fmt_point", "fmt_ineq", "fmt_interval", "fn_of",
           "line_through", "slope", "exp_model", "sign_join", "fmt_percent", "SYMBOL"]


def num(x) -> Q:
    """Anything numeric to an exact Fraction. Floats come in as decimals."""
    return x if isinstance(x, Q) else Q(str(x)) if isinstance(x, float) else Q(x)


def fmt_num(v, tex: bool = False, group: bool = True) -> str:
    """A number the way an SAT option prints it: 3, -1/2, 2.5, 1,200."""
    v = num(v)
    if v.denominator == 1:
        n = v.numerator
        return f"{n:,}" if group and abs(n) >= 10_000 else str(n)
    return fmt_frac(v, tex)


def fmt_frac(v, tex: bool = False) -> str:
    v = num(v)
    if v.denominator == 1:
        return str(v.numerator)
    sign = "-" if v < 0 else ""
    n, d = abs(v.numerator), v.denominator
    return rf"{sign}\frac{{{n}}}{{{d}}}" if tex else f"{sign}{n}/{d}"


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
