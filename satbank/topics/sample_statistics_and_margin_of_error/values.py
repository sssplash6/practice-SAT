"""Exact numbers, and how this topic prints them.

Nothing here is a float. A percent is a `Fraction` of percentage points (32%
is ``Q(32)``, 3.41% is ``Q(341, 100)``), a proportion is a `Fraction` between
0 and 1, and a count is an integer `Fraction`. That matters more here than in
most topics: the whole subject is ``estimate +- margin``, and an endpoint that
drifts by a floating ulp prints ``27.779999999999998`` on the page a student
reads.

`Num` is the shared `Exact` taught to print the way this topic prints -- a
count with thousands separators, a percent with its sign, a decimal at a
fixed number of places -- so `assemble`'s ordering, the audit's comparison and
the printed option are all the same number.
"""

from __future__ import annotations

import re
from fractions import Fraction as Q

from ...exact import MINUS, Exact
from ...item import ItemError

__all__ = ["Q", "q", "Num", "dec", "places_needed", "grid", "tidy", "snap",
           "unambiguous", "parse_num"]


def q(v) -> Q:
    """Anything numeric to an exact Fraction. A float arrives as its decimal."""
    if isinstance(v, Q):
        return v
    if isinstance(v, float):
        return Q(str(v))
    return Q(v)


def snap(v, step) -> Q:
    """Round to the nearest multiple of `step`, halves upward."""
    v, step = q(v), q(step)
    k = v / step
    n = k.numerator // k.denominator
    if 2 * (k - n) >= 1:
        n += 1
    return n * step


def unambiguous(v, step):
    """`v` rounded to `step`, unless it sits exactly halfway.

    Every "best estimate", "about how many" and "round to the nearest whole
    number" stem in this topic rounds, and a value exactly between two
    printable answers has no answer -- which of them is nearest is a rounding
    convention the stem never states. The draw is thrown away instead.
    """
    v, step = q(v), q(step)
    k = v / step
    if 2 * (k - k.numerator // k.denominator) == 1:
        raise ItemError("this value sits exactly halfway between two answers, and "
                        "which of them is nearest is a convention rather than "
                        "mathematics")
    return snap(v, step)


def places_needed(v, cap: int = 4) -> int:
    """Fewest decimals that print `v` exactly, or `cap` when it does not end."""
    v = q(v)
    for p in range(cap + 1):
        if (v * 10 ** p).denominator == 1:
            return p
    return cap


def dec(v, places: int, group: bool = True) -> str:
    """An exact rational as a decimal string, rounded half up.

    A negative prints U+2212, the sign the rest of the engine prints. Readers
    fold the two spellings together, so this changes the page and not what
    compares equal.
    """
    v = q(v)
    neg = v < 0
    a = -v if neg else v
    scaled = a * 10 ** places
    n = scaled.numerator // scaled.denominator
    if 2 * (scaled - n) >= 1:
        n += 1
    s = str(n).rjust(places + 1, "0")
    whole = s[:len(s) - places] if places else s
    frac = s[len(s) - places:] if places else ""
    head = f"{int(whole):,}" if group else str(int(whole))
    out = head + ("." + frac if places else "")
    return (MINUS + out) if neg else out


class Num(Exact):
    """An exact rational that prints the way this topic prints it.

    ``style`` is ``plain`` (a count), ``percent`` (``3.41%``) or ``bare`` (a
    decimal with no thousands separator, which is how a proportion and a
    small measure print). ``places`` fixes the decimals, or the value picks
    the fewest that print it exactly. Equality ignores the surface, so a
    distractor landing on the key is still caught as a duplicate.
    """

    def __init__(self, value, style: str = "plain", places: int | None = None,
                 suffix: str = ""):
        object.__setattr__(self, "coef", q(value))
        object.__setattr__(self, "pi_exp", Q(0))
        object.__setattr__(self, "rad", 1)
        object.__setattr__(self, "style", style)
        object.__setattr__(self, "places", places)
        object.__setattr__(self, "suffix", suffix)

    def __eq__(self, other):
        return (isinstance(other, Exact)
                and (self.coef, self.pi_exp, self.rad)
                == (other.coef, other.pi_exp, other.rad))

    def __hash__(self):
        return hash((self.coef, self.pi_exp, self.rad))

    def plain(self) -> str:
        p = places_needed(self.coef) if self.places is None else self.places
        body = dec(self.coef, p, group=self.style == "plain")
        if self.style == "percent":
            body += "%"
        return body + self.suffix

    def latex(self) -> str:
        return self.plain()

    def __repr__(self) -> str:
        return f"Num({self.plain()})"


_STRIP = re.compile(r"[,%\s]")


def parse_num(text: str) -> Q:
    """A printed number back to its exact value. Either spelling of the sign."""
    return Q(_STRIP.sub("", str(text).replace(MINUS, "-")))


def grid(v) -> str:
    """Student-produced-response form: the shortest exact entry, ASCII sign."""
    v = q(v)
    if v.denominator == 1:
        return str(v.numerator)
    for p in range(1, 9):
        if (v * 10 ** p).denominator == 1:
            return dec(v, p, group=False).replace(MINUS, "-")
    return f"{v.numerator}/{v.denominator}"


def tidy(text: str) -> str:
    """One space between words, whatever the f-string did with the line breaks."""
    return re.sub(r"\s+", " ", str(text)).strip()
