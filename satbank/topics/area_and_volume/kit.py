"""Choosing which wrong answers an item offers.

Every template in this topic builds its distractors as a *named pool* -- a dict
from a short key to the `Mis` that key produces -- rather than as a bare list.
A free draw is offered the whole pool and lets `assemble` choose; a source item
passes `wrongs=[...]`, naming the three misconceptions College Board actually
printed, in the order they are offered.

That separation is the whole point. The pool is the topic's library of student
errors and grows as the source items teach new ones; `wrongs` records what one
particular item writer reached for. Without it a well-modelled misconception
sitting fourth in the list is invisible, which is how this topic reached the
state where it knew the mistake and printed something else.
"""

from __future__ import annotations

from ...exact import Exact
from ...item import ItemError, Mis

__all__ = ["pick", "attempt", "decimal_text"]


def pick(pool: dict[str, Mis], wrongs: list[str] | None) -> list[Mis]:
    """The misconceptions this draw offers, in the order they are offered."""
    keys = list(pool) if wrongs is None else list(wrongs)
    out: list[Mis] = []
    for k in keys:
        if k not in pool:
            raise ItemError(f"no misconception named {k!r}")
        m = pool[k]
        if m is not None and m.value is not None:
            out.append(m)
    return out


def attempt(fn) -> Exact | None:
    """A wrong route that is not always expressible -- 45π − 5 units, say.

    A student cannot produce a value that cannot be written down, so a route
    that will not evaluate is simply not offered.
    """
    try:
        return fn()
    except (ValueError, ZeroDivisionError, TypeError):
        return None


def decimal_text(v: Exact) -> str:
    """4.5 where the source prints a decimal, 1/3 where it prints a fraction.

    The official items write a terminating quotient as a decimal -- 4.5, 7.5 --
    and keep the fraction only when it repeats. `Exact.plain` always writes the
    fraction, so the templates whose answers come out of a division pass their
    options through this.
    """
    if v.is_rational and v.coef.denominator != 1:
        d = v.coef.denominator
        while d % 2 == 0:
            d //= 2
        while d % 5 == 0:
            d //= 5
        if d == 1:
            return f"{float(v.coef):,g}"
    return v.plain()
