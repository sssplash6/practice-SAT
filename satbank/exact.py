"""Exact arithmetic for SAT geometry answers.

Every answer in the source set has the shape

    coef * pi**pi_exp * sqrt(rad)

with `coef` rational, `pi_exp` rational (0, 1/2, 1, ...) and `rad` a squarefree
positive integer. That one form covers all of it: integers (3,025), fractions
(135/8), pi-multiples (192*pi, 19,652*pi/375), radicals (36*sqrt(13),
1/sqrt(3) -> sqrt(3)/3) and sqrt-of-pi (2*sqrt(pi)).

Floats are never used to compute a key -- only to sort choices and to render
"which of the following is closest to" items.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction

MINUS = "\N{MINUS SIGN}"        # U+2212, the sign a typeset page prints

__all__ = ["Exact", "E", "PI"]


def _squarefree(n: int) -> tuple[int, int]:
    """Factor n = m**2 * k with k squarefree. Returns (m, k)."""
    m, k, d = 1, n, 2
    while d * d <= k:
        while k % (d * d) == 0:
            k //= d * d
            m *= d
        d += 1
    return m, k


def _group(n: int) -> str:
    """3025 -> '3,025'. The source items use thousands separators."""
    return f"{n:,}"


@dataclass(frozen=True, order=False)
class Exact:
    coef: Fraction
    pi_exp: Fraction = Fraction(0)
    rad: int = 1

    # ---------------------------------------------------------- construction

    @staticmethod
    def of(coef=1, pi_exp=0, rad=1) -> "Exact":
        """Build and normalize. `rad` may be any nonnegative rational."""
        coef, pi_exp, rad = Fraction(coef), Fraction(pi_exp), Fraction(rad)
        if rad < 0:
            raise ValueError("negative radicand")
        if rad == 0 or coef == 0:
            return Exact(Fraction(0), Fraction(0), 1)
        # sqrt(p/q) == sqrt(p*q)/q
        m, k = _squarefree(rad.numerator * rad.denominator)
        return Exact(coef * Fraction(m, rad.denominator), pi_exp, k)

    # ------------------------------------------------------------ arithmetic

    def __mul__(self, other) -> "Exact":
        o = _coerce(other)
        return Exact.of(self.coef * o.coef, self.pi_exp + o.pi_exp, Fraction(self.rad * o.rad))

    __rmul__ = __mul__

    def __truediv__(self, other) -> "Exact":
        o = _coerce(other)
        if o.coef == 0:
            raise ZeroDivisionError
        return Exact.of(self.coef / o.coef, self.pi_exp - o.pi_exp, Fraction(self.rad, o.rad))

    def __rtruediv__(self, other) -> "Exact":
        return _coerce(other) / self

    def __add__(self, other) -> "Exact":
        o = _coerce(other)
        if self.coef == 0:
            return o
        if o.coef == 0:
            return self
        if (self.pi_exp, self.rad) != (o.pi_exp, o.rad):
            raise ValueError(f"cannot add unlike terms: {self.plain()} + {o.plain()}")
        return Exact.of(self.coef + o.coef, self.pi_exp, Fraction(self.rad))

    __radd__ = __add__

    def __neg__(self) -> "Exact":
        return Exact(-self.coef, self.pi_exp, self.rad)

    def __sub__(self, other) -> "Exact":
        return self + (-_coerce(other))

    def __rsub__(self, other) -> "Exact":
        return _coerce(other) + (-self)

    def __pow__(self, n: int) -> "Exact":
        if n < 0:
            return Exact.of(1) / (self ** -n)
        return Exact.of(self.coef ** n, self.pi_exp * n, Fraction(self.rad) ** n)

    def sqrt(self) -> "Exact | None":
        """Exact square root, or None when it would need a nested radical."""
        if self.coef < 0 or self.rad != 1:
            return None
        return Exact.of(1, self.pi_exp / 2, self.coef)

    # ------------------------------------------------------------ predicates

    @property
    def is_rational(self) -> bool:
        return self.pi_exp == 0 and self.rad == 1

    @property
    def is_integer(self) -> bool:
        return self.is_rational and self.coef.denominator == 1

    @property
    def form(self) -> tuple:
        """Surface signature. Options that differ here are visually sortable
        by a student who cannot do the math, so a key must never be alone.

        The pi exponent is compared by value, not merely by presence: 2*pi and
        2*sqrt(pi) look nothing alike on the page, and treating them as one
        form let a lone integer key slip through as the odd one out.
        """
        return (self.pi_exp, self.rad != 1, self.coef.denominator != 1)

    def __float__(self) -> float:
        return float(self.coef) * (math.pi ** float(self.pi_exp)) * math.sqrt(self.rad)

    def __lt__(self, other) -> bool:
        return float(self) < float(_coerce(other))

    def __le__(self, other) -> bool:
        return float(self) <= float(_coerce(other))

    def __gt__(self, other) -> bool:
        return float(self) > float(_coerce(other))

    def __ge__(self, other) -> bool:
        return float(self) >= float(_coerce(other))

    def __hash__(self):
        return hash((self.coef, self.pi_exp, self.rad))

    # ------------------------------------------------------------- rendering

    def _parts(self, tex: bool) -> tuple[str, int]:
        """Returns (numerator string, denominator)."""
        n, d = abs(self.coef.numerator), self.coef.denominator
        sym = _pi_str(self.pi_exp, tex) + _rad_str(self.rad, tex)
        head = "" if (n == 1 and sym) else _group(n)
        return head + sym, d

    def plain(self) -> str:
        """The value as the SAT prints it, typeset minus and all.

        The sign is U+2212, not the ASCII hyphen: the page is typeset, so an
        option reads -8 nowhere and −8 everywhere. Every reader in the engine
        folds the two together (`item.norm_text`, `item.numeral`, and each
        topic's own option reader), so this changes what is printed and not
        what compares equal. `gridin` keeps the ASCII sign, because that is a
        student's keystroke rather than a printed page.
        """
        if self.coef == 0:
            return "0"
        num, den = self._parts(tex=False)
        sign = MINUS if self.coef < 0 else ""
        return f"{sign}{num}" if den == 1 else f"{sign}{num}/{den}"

    def latex(self) -> str:
        if self.coef == 0:
            return "0"
        num, den = self._parts(tex=True)
        sign = "-" if self.coef < 0 else ""
        return f"{sign}{num}" if den == 1 else rf"{sign}\frac{{{num}}}{{{den}}}"

    def gridin(self) -> str:
        """Student-produced-response form: digits only, no separators."""
        if not self.is_rational:
            raise ValueError(f"{self.plain()} is not enterable as a grid-in")
        if self.coef.denominator == 1:
            return str(self.coef.numerator)
        as_float = float(self.coef)
        if as_float == round(as_float, 2):          # 518.4 and 24.5, but not 16.875
            return f"{as_float:g}"
        return f"{self.coef.numerator}/{self.coef.denominator}"

    def approx(self, sig: int = 3) -> float:
        v = float(self)
        if v == 0:
            return 0.0
        return round(v, -int(math.floor(math.log10(abs(v)))) + (sig - 1))

    def __repr__(self) -> str:
        return f"Exact({self.plain()})"


def _pi_str(e: Fraction, tex: bool) -> str:
    if e == 0:
        return ""
    pi = r"\pi" if tex else "π"
    if e == 1:
        return pi
    if e == Fraction(1, 2):
        return rf"\sqrt{{{pi}}}" if tex else f"√{pi}"
    exp = str(e.numerator) if e.denominator == 1 else f"{e.numerator}/{e.denominator}"
    return f"{pi}^{{{exp}}}" if tex else f"{pi}^{exp}"


def _rad_str(rad: int, tex: bool) -> str:
    if rad == 1:
        return ""
    return rf"\sqrt{{{rad}}}" if tex else f"√{rad}"


def _coerce(v) -> Exact:
    return v if isinstance(v, Exact) else Exact.of(v)


def E(coef=1, pi_exp=0, rad=1) -> Exact:
    return Exact.of(coef, pi_exp, rad)


PI = E(1, 1)
