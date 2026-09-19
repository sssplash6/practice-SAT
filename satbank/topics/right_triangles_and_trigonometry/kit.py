"""The parts every Right Triangles template shares.

Three things live here.

**Named distractor pools.** `pick` is the house pattern: a template keeps its
wrong answers as `{key: Mis}` and a source item names the three College Board
printed, in printed order, with `wrongs=[...]`. Trigonometry's mistakes are
*named* mistakes -- used cosine where sine is needed, took the reciprocal, used
the adjacent leg as the hypotenuse, found the complement's ratio -- so the pool
reads as the errors an item is testing rather than as filler.

**`Surd`.** `Exact` covers `coef · π^e · √rad`, which is every answer in the
set but one shape: a perimeter like `58 + 58√2`, where a rational and a
radical are added and cannot be folded together. `Surd` is `a + b√d` with `a`
and `b` exact Fractions, so those answers stay exact to the printed page. It
was written here and now lives in `exact.py` beside `Exact`; this module
re-exports it, and `assemble_surd` below is the assembler that uses its
`.form`.

**A halfway guard.** A stem that says *closest* has an answer only while one
printed option is nearer the true value than every other, so `closest_only`
refuses a draw where two options tie or the key is not the nearest.
"""

from __future__ import annotations

import math
from fractions import Fraction as Q

from ...exact import E, Exact, Surd, squarefree
from ...item import ItemError, Mis, assemble

__all__ = ["pick", "attempt", "Surd", "S0", "assemble_surd", "assemble_exact",
           "closest_only", "places_text", "ratio_text", "TRIPLES", "triple_for",
           "squarefree", "grid_ok"]

# --------------------------------------------------------------- the pool

def pick(pool: dict, wrongs=None) -> list[Mis]:
    """The misconceptions this draw offers, in the order they are offered.

    A free draw is handed the whole pool and lets `assemble` choose; a source
    item names the three it wants. Without this a well-modelled misconception
    sitting fourth in a list is invisible, which is how a topic ends up
    knowing the mistake and printing something else.
    """
    keys = list(pool) if wrongs is None else list(wrongs)
    out = []
    for k in keys:
        if k not in pool:
            raise ItemError(f"no misconception named {k!r}")
        m = pool[k]
        if m is not None and m.value is not None:
            out.append(m)
    return out


def attempt(fn):
    """A wrong route that does not always evaluate -- a nested radical, say.

    A student cannot produce a value that cannot be written down, so a route
    that will not evaluate is simply not offered.
    """
    try:
        return fn()
    except (ValueError, ZeroDivisionError, TypeError, ArithmeticError):
        return None


# ------------------------------------------------------- a + b*sqrt(d)

S0 = Surd.of(0)


def assemble_surd(key: Surd, mistakes, rng, *, enforce_form=True):
    """Four options ordered the way the SAT orders them, for `a + b√d` answers.

    `item.assemble` works on `Exact` and cannot hold `58 + 58√2`, so this is
    the same contract on `Surd`: distinct values, ascending, and -- unless a
    source item has named its own three -- the key never the only option of
    its surface form.
    """
    seen = {key}
    same, other = [], []
    for m in mistakes:
        v = m.value
        if not isinstance(v, Surd) or v in seen or float(v) <= 0:
            continue
        seen.add(v)
        (same if v.form == key.form else other).append(m)
    picked = (same + other)[:3] if not enforce_form else (same[:3] + other)[:3]
    if len(picked) < 3:
        raise ItemError("could not build three distinct distractors")
    if enforce_form and not any(m.value.form == key.form for m in picked):
        raise ItemError("key would be the only option of its form")
    options = [(key, "")] + [(m.value, m.reason) for m in picked]
    options.sort(key=lambda t: float(t[0]))
    choices = [v.plain() for v, _ in options]
    reasons = [r for _, r in options]
    letter = "ABCD"[next(i for i, (_, r) in enumerate(options) if r == "")]
    return choices, choices, reasons, letter


def assemble_exact(key: Exact, mistakes, rng, *, fmt_value=None, signed=False,
                   strict=True):
    """`item.assemble`, except that a source item may name its own three.

    A free draw goes through the shared assembler and keeps its rule that the
    key is never the only option of its surface form. A source item hands over
    the three College Board actually printed, and College Board is allowed to
    print 250 among three radicals -- reproducing that option set is the whole
    point of encoding the item, so the rule is not applied to it.
    """
    if strict:
        return assemble(key, mistakes, rng, fmt_value=fmt_value, signed=signed)
    seen, picked = {key}, []
    for m in mistakes:
        v = m.value
        if not isinstance(v, Exact) or v in seen or (not signed and float(v) <= 0):
            continue
        seen.add(v)
        picked.append(m)
    if len(picked) < 3:
        raise ItemError("could not build three distinct distractors")
    options = [(key, "")] + [(m.value, m.reason) for m in picked[:3]]
    options.sort(key=lambda t: float(t[0]))
    choices = [fmt_value(v) if fmt_value else v.plain() for v, _ in options]
    latex = [fmt_value(v) if fmt_value else v.latex() for v, _ in options]
    reasons = [r for _, r in options]
    letter = "ABCD"[next(i for i, (_, r) in enumerate(options) if r == "")]
    return choices, latex, reasons, letter


# ------------------------------------------------------- "closest to" items

def places_text(v: float, places: int = 1) -> str:
    """A decimal option the way the source prints one: 7.6, 5, 58.5, 10.8.

    Rounds half away from zero -- the way a student's calculator does -- and
    drops a trailing zero, because the source writes 5 rather than 5.0.
    """
    scale = 10 ** places
    n = math.floor(abs(v) * scale + 0.5)
    sign = "-" if v < 0 else ""
    whole, frac = divmod(n, scale)
    if frac == 0:
        return f"{sign}{whole:,}"
    text = f"{frac:0{places}d}".rstrip("0")
    return f"{sign}{whole:,}.{text}"


def closest_only(true_value: float, printed: list[float], key: float) -> None:
    """Refuse a draw whose printed page cannot single the key out.

    Three topics shipped an item whose stem said *closest* and whose true
    value sat halfway between two printed options; the audit cannot see it,
    because the audit re-derives from the parameters and never from the string
    the student reads. So the comparison is made here, on the printed numbers.
    """
    gaps = sorted((abs(p - true_value), p) for p in printed)
    if len(gaps) < 2:
        return
    if abs(gaps[0][1] - key) > 1e-12:
        raise ItemError("the nearest printed option is not the key")
    if gaps[1][0] - gaps[0][0] <= 1e-9 * max(1.0, abs(true_value)):
        raise ItemError("two printed options are equally close to the true value")


def grid_ok(v: Exact) -> Exact:
    """A grid-in answer has to be enterable as digits."""
    if not v.is_rational or float(v) < 0:
        raise ItemError("this answer cannot be entered in a grid-in")
    return v


# --------------------------------------------------------------- ratios

def ratio_text(p, q) -> str:
    """A trigonometric ratio the way a stem prints one: 21/20, 3/5, 24/51.

    Never reduced: the source writes cos K = 24/51 and expects the student to
    do the reducing, so the numerator and denominator are the item's own.
    """
    return f"{int(p):,}/{int(q):,}"


# Primitive Pythagorean triples (leg, leg, hypotenuse), smallest first. Every
# template that needs a rational trigonometric ratio draws one of these and a
# scale factor, so no template is built around a single triple.
TRIPLES = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29),
           (9, 40, 41), (12, 35, 37), (11, 60, 61), (28, 45, 53), (33, 56, 65),
           (16, 63, 65), (48, 55, 73), (13, 84, 85), (36, 77, 85), (39, 80, 89),
           (65, 72, 97)]


def triple_for(p: int, q: int) -> tuple[int, int, int]:
    """The right triangle in which one ratio of two legs is p : q."""
    h2 = p * p + q * q
    h = math.isqrt(h2)
    if h * h != h2:
        raise ItemError(f"{p} and {q} are not the legs of a rational right triangle")
    return p, q, h


def leg_from(hyp: int, leg: int) -> int:
    """The third side of a right triangle, when it comes out whole."""
    d = hyp * hyp - leg * leg
    if d <= 0:
        raise ItemError("that leg is not shorter than the hypotenuse")
    r = math.isqrt(d)
    if r * r != d:
        raise ItemError("the third side is not a whole number")
    return r


def rational(v) -> Q:
    """An `Exact`, an int or a Fraction as an exact Fraction.

    The point is that nothing goes through `float` on the way: √(53² − 52²) is
    √105 because 2,809 and 2,704 are integers, not because two doubles
    subtracted to something near 105.
    """
    if isinstance(v, Exact):
        if not v.is_rational:
            raise ItemError(f"{v.plain()} is not a rational length")
        return v.coef
    return Q(v)


def exact_leg(hyp, leg) -> Exact:
    """The third side, exactly -- a whole number or a radical, never a float."""
    d = rational(hyp) ** 2 - rational(leg) ** 2
    if d <= 0:
        raise ItemError("that leg is not shorter than the hypotenuse")
    return E(1, 0, d)


__all__ += ["leg_from", "exact_leg", "rational"]
