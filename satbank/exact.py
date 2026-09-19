"""Exact arithmetic for SAT geometry answers.

Two shapes, because two shapes are what the source set prints.

`Exact` is

    coef * pi**pi_exp * sqrt(rad)

with `coef` rational, `pi_exp` rational (0, 1/2, 1, ...) and `rad` a squarefree
positive integer. That one form covers most of it: integers (3,025), fractions
(135/8), pi-multiples (192*pi, 19,652*pi/375), radicals (36*sqrt(13),
1/sqrt(3) -> sqrt(3)/3) and sqrt-of-pi (2*sqrt(pi)).

`Surd` is

    a + b*sqrt(d)

with `a` and `b` exact Fractions and `d` squarefree. It is the one shape
`Exact` cannot hold: a rational *added* to a radical, which has no single
coefficient to fold into. An isosceles right triangle with a hypotenuse of 58
has a perimeter of 58 + 58*sqrt(2), and no `coef * sqrt(rad)` is that number.
Surds divide through the conjugate, so a template handed a surd perimeter in
the stem can undo it exactly: (94 + 94*sqrt(2)) / (2 + sqrt(2)) is 47*sqrt(2).

Both answer `float()` and `.plain()`, which is the whole of the contract
`audit.py` has with `item.key`, so the shared audit runs over either with no
special case. Both expose `.form`, the surface signature an assembler uses to
keep the key from being the only option of its shape.

Floats are never used to compute a key -- only to sort choices and to render
"which of the following is closest to" items.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction

MINUS = "\N{MINUS SIGN}"        # U+2212, the sign a typeset page prints

__all__ = ["Exact", "Surd", "E", "PI", "MINUS", "squarefree"]


def squarefree(n: int) -> tuple[int, int]:
    """Factor n = m**2 * k with k squarefree, so sqrt(8) and 2*sqrt(2) are one
    number. Returns (m, k)."""
    m, k, d = 1, int(n), 2
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
        m, k = squarefree(rad.numerator * rad.denominator)
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


# ------------------------------------------------------------- a + b*sqrt(d)
#
# The shape `Exact` cannot hold. A rational added to a radical has no single
# coefficient to fold into, and the source set prints it: 58 + 58*sqrt(2) is
# the perimeter of an isosceles right triangle with a hypotenuse of 58, and
# the stems that state such a perimeter need it divided back out exactly.


def _rational_text(v: Fraction) -> str:
    """A rational as the page prints it: 1,184 and −47/3."""
    sign = MINUS if v < 0 else ""
    n, d = abs(v.numerator), v.denominator
    return f"{sign}{_group(n)}" if d == 1 else f"{sign}{_group(n)}/{d}"


def _radical_text(b: Fraction, d: int) -> str:
    """b√d the way the source prints it: 58√2, √2, 47√2/3, −√3/3."""
    sign = MINUS if b < 0 else ""
    n, q = abs(b.numerator), b.denominator
    head = "" if n == 1 else _group(n)
    body = f"{head}√{d}"
    return f"{sign}{body}" if q == 1 else f"{sign}{body}/{q}"


@dataclass(frozen=True)
class Surd:
    """a + b√d, exactly. The one answer shape `Exact` cannot hold."""
    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)
    d: int = 1

    @staticmethod
    def of(a=0, b=0, d=1) -> "Surd":
        a, b, d = Fraction(a), Fraction(b), int(d)
        if d < 1:
            raise ValueError("a radicand is a positive integer")
        m, k = squarefree(d)
        b = b * m
        if k == 1:
            return Surd(a + b, Fraction(0), 1)
        if b == 0:
            return Surd(a, Fraction(0), 1)
        return Surd(a, b, k)

    @staticmethod
    def exact(v: Exact) -> "Surd":
        """An `Exact` with no π in it, as a Surd."""
        if v.pi_exp != 0:
            raise ValueError("π has no place in a + b√d")
        return Surd.of(0, v.coef, v.rad) if v.rad != 1 else Surd.of(v.coef)

    # ------------------------------------------------------------ arithmetic

    def _like(self, o) -> "Surd":
        o = o if isinstance(o, Surd) else Surd.of(o)
        if self.b and o.b and self.d != o.d:
            raise ArithmeticError(f"{self.plain()} and {o.plain()} are unlike radicals")
        return o

    def __add__(self, o) -> "Surd":
        o = self._like(o)
        return Surd.of(self.a + o.a, self.b + o.b, self.d if self.b else o.d)

    __radd__ = __add__

    def __neg__(self) -> "Surd":
        return Surd(-self.a, -self.b, self.d)

    def __sub__(self, o) -> "Surd":
        return self + (-self._like(o))

    def __rsub__(self, o) -> "Surd":
        return self._like(o) + (-self)

    def __mul__(self, o) -> "Surd":
        o = self._like(o)
        if not self.b or not o.b:
            d = self.d if self.b else o.d
            return Surd.of(self.a * o.a, self.a * o.b + self.b * o.a, d)
        return Surd.of(self.a * o.a + self.b * o.b * self.d,
                       self.a * o.b + self.b * o.a, self.d)

    __rmul__ = __mul__

    def __truediv__(self, o) -> "Surd":
        """Exact division, rationalised through the conjugate.

        A stem that states a surd perimeter has to be undone by the template
        that printed it, so this is a requirement and not a convenience:
        (94 + 94√2) / (2 + √2) comes out as exactly 47√2.
        """
        o = self._like(o)
        if o.a == 0 and o.b == 0:
            raise ZeroDivisionError
        if o.b == 0:
            return Surd.of(self.a / o.a, self.b / o.a, self.d)
        # rationalise: multiply above and below by the conjugate
        den = o.a * o.a - o.b * o.b * o.d
        if den == 0:
            raise ZeroDivisionError
        conj = Surd(o.a, -o.b, o.d)
        top = self * conj
        return Surd.of(top.a / den, top.b / den, top.d)

    def __rtruediv__(self, o) -> "Surd":
        return self._like(o) / self

    # ------------------------------------------------------------ predicates

    @property
    def rational(self) -> bool:
        return self.b == 0

    @property
    def form(self) -> tuple:
        """Surface signature, the way `assemble` uses one: two options that
        differ here are told apart by eye rather than by geometry."""
        return (self.a != 0, self.b != 0, self.d,
                self.a.denominator != 1 or self.b.denominator != 1)

    def __float__(self) -> float:
        return float(self.a) + float(self.b) * math.sqrt(self.d)

    def __hash__(self):
        return hash((self.a, self.b, self.d))

    # ------------------------------------------------------------- rendering

    def plain(self) -> str:
        """The value as the SAT prints it: 58 + 58√2, and never 58 + 82.02.

        This is half of the contract `audit.py` has with `item.key`; `float()`
        is the other half, and between them the shared audit runs over a Surd
        with no special case.
        """
        if self.b == 0:
            return _rational_text(self.a)
        rad = _radical_text(self.b, self.d)
        if self.a == 0:
            return rad
        join = f" {MINUS} " if self.b < 0 else " + "
        return f"{_rational_text(self.a)}{join}{_radical_text(abs(self.b), self.d)}"

    def __repr__(self) -> str:
        return f"Surd({self.plain()})"
