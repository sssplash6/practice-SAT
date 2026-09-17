"""How a wrong answer is chosen, and how a measure is written down.

Two things live here, both of them house patterns rather than inventions of
this topic.

**The named pool.** Every template keeps its wrong answers as `{key: Mis}` and
a default order. A free draw is offered the whole pool and lets `assemble`
choose; a source item passes `wrongs=[...]`, naming the three misconceptions
the College Board item writer actually reached for, in the order they were
printed. Without that, a well-modelled misconception sitting fourth in a list
is invisible -- `assemble` takes the first three it can use, and a topic whose
answers are all whole numbers of degrees has a great many usable ones.

**The halfway guard.** A stem that says *closest* has an answer only while one
of the printed options is nearer than every other, so a draw landing exactly
between two of them is refused rather than shipped. Three topics in earlier
waves shipped items whose printed page could not produce the key, and every
check was green on all three.
"""

from __future__ import annotations

from fractions import Fraction as Q

from ...exact import E, Exact
from ...item import ItemError, Mis

__all__ = ["Q", "q", "pick", "attempt", "deg", "plain", "dec", "snap",
           "unambiguous", "whole"]


# ------------------------------------------------------------- the pool

def pick(pool: dict, order, wrongs=None) -> list[Mis]:
    """The misconceptions this draw offers, in the order it offers them.

    An entry whose value is None does not apply to this draw -- the frame does
    not admit the mistake, or it produces a number no student would write down
    -- and is skipped rather than offered. Naming a key that is not in the
    pool is an authoring error and says so.
    """
    names = list(order if wrongs is None else wrongs)
    out: list[Mis] = []
    for name in names:
        if name not in pool:
            raise ItemError(f"no misconception named {name!r} in this pool")
        m = pool[name]
        if m is not None and m.value is not None:
            out.append(m)
    return out


def attempt(fn):
    """A wrong route that is not always expressible. Not offered when it fails."""
    try:
        return fn()
    except (ValueError, ZeroDivisionError, TypeError, ArithmeticError):
        return None


def q(v) -> Q:
    if isinstance(v, Q):
        return v
    if isinstance(v, float):
        return Q(str(v))
    if isinstance(v, Exact):
        if not v.is_rational:
            raise ValueError("not a rational measure")
        return v.coef
    return Q(v)


def whole(v) -> Exact | None:
    """An angle measure, but only when it is a whole number of degrees.

    The source set never prints 46.5 degrees as an option, so a route that
    lands between two degrees is a route no student writes down.
    """
    try:
        f = q(v)
    except (ValueError, TypeError):
        return None
    if f.denominator != 1 or f <= 0 or f >= 360:
        return None
    return E(f)


# ------------------------------------------------------------- rendering

def deg(v) -> str:
    """35 degrees printed as an option that carries its unit: 35°."""
    return f"{plain(v)}°"


def plain(v) -> str:
    """The bare number, with a terminating quotient written as a decimal.

    The source items print 4.5 and 17.5, never 9/2 and 35/2, and keep the
    fraction only where it repeats (44/3, 10/3).
    """
    f = q(v)
    if f.denominator == 1:
        return f"{f.numerator:,}"
    d = f.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    if d == 1:
        return f"{float(f):,g}"
    return f"{f.numerator}/{f.denominator}"


def dec(v, places: int) -> str:
    """An exact rational as a decimal, rounded half up -- 17.5, 19.6."""
    f = q(v)
    neg = f < 0
    a = -f if neg else f
    scaled = a * 10 ** places
    n = scaled.numerator // scaled.denominator
    if 2 * (scaled - n) >= 1:
        n += 1
    s = str(n).rjust(places + 1, "0")
    body = f"{s[:-places]}.{s[-places:]}" if places else s
    return ("-" if neg else "") + body


# ------------------------------------------------------- the halfway guard

def snap(v, step) -> Q:
    """Round to the nearest multiple of `step`, halves upward."""
    v, step = q(v), q(step)
    k = v / step
    n = k.numerator // k.denominator
    if 2 * (k - n) >= 1:
        n += 1
    return n * step


def unambiguous(v, step) -> Q:
    """`v` rounded to `step`, unless it sits exactly halfway between two.

    Which of two equally near options is "closest" is a rounding convention
    the stem never states, so the draw is thrown away instead.
    """
    v, step = q(v), q(step)
    k = v / step
    if 2 * (k - k.numerator // k.denominator) == 1:
        raise ItemError("this value sits exactly halfway between two printable "
                        "answers, so 'closest' has no answer")
    return snap(v, step)
