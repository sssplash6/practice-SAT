"""The audit harness: no item leaves the engine un-re-derived.

Every template records, in `item.params`, the numbers that determine its
answer. A solver registered by the topic -- written from the mathematics, not
from the generator, and sharing none of its reasoning -- recomputes the answer
from those numbers alone. The item ships only if the two agree.

This file holds the part that is the same for every topic: the dispatch, the
tolerance, the root-finder that checks inverse items without algebra, and the
structural checks that catch a right answer attached to the wrong letter. The
mathematics lives in `topics/<slug>/audit.py`.
"""

from __future__ import annotations

import math
from typing import Callable

from .item import Item

__all__ = ["audit", "AuditError", "close", "sig3", "solve_for", "solvers"]

TOL = 1e-7


class AuditError(Exception):
    pass


def close(a: float, b: float, tol: float = TOL) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def sig3(v: float) -> float:
    """Round to three significant figures, the way the source items do."""
    if v == 0:
        return 0.0
    return round(v, -int(math.floor(math.log10(abs(v)))) + 2)


def solve_for(f: Callable[[float], float], target: float,
              lo: float = 1e-9, hi: float = 1e7) -> float:
    """Find x > 0 with f(x) = target, for a monotone-increasing f.

    Inverse items are checked this way -- by root-finding rather than by any
    algebra the generator performed -- so the two routes stay independent.
    """
    if f(lo) > target:
        raise AuditError("target below the formula's range")
    while f(hi) < target:
        hi *= 2
        if hi > 1e12:
            raise AuditError("target above the formula's range")
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


_SOLVERS: dict[str, Callable] = {}


def solvers() -> dict[str, Callable]:
    """Every registered solver, gathered the first time one is wanted."""
    if not _SOLVERS:
        from .topic import load_topics
        for topic in load_topics().values():
            for kind, fn in topic.audits.items():
                if kind in _SOLVERS:
                    raise RuntimeError(f"two topics both audit the kind {kind!r}")
                _SOLVERS[kind] = fn
    return _SOLVERS


def audit(item: Item) -> None:
    """Raise AuditError unless the item's own answer survives re-derivation."""
    if not item.params:
        raise AuditError("item carries no parameters to audit")
    kind = item.params.get("kind")
    solver = solvers().get(kind)
    if solver is None:
        raise AuditError(f"no independent solver for kind {kind!r}")
    want = solver(item.params)
    _structure(item)

    if isinstance(want, str):
        got = item.choices["ABCD".index(item.answer)] if item.fmt == "mcq" else item.answer
        if got.replace(" ", "") != want.replace(" ", ""):
            raise AuditError(f"keyed option {got!r}, independently derived {want!r}")
        return

    got = float(item.key)
    if not close(got, want):
        raise AuditError(f"item answers {item.key.plain()} ({got!r}), "
                         f"independently derived {want!r}")

    # the keyed option must be the key -- by value, since a template may render
    # its options in its own form (decimals rather than a canonical fraction)
    if item.fmt == "mcq":
        keyed = item.choices["ABCD".index(item.answer)]
        if keyed != item.key.plain():
            try:
                shown = float(keyed.replace(",", ""))
            except ValueError:
                raise AuditError(
                    f"answer letter points at {keyed!r}, key is {item.key.plain()!r}") from None
            if not close(shown, want, 1e-6):
                raise AuditError(f"keyed option reads {keyed!r} but the answer is {want!r}")
    elif item.fmt == "spr":
        txt = item.answer
        val = (float(txt.split("/")[0]) / float(txt.split("/")[1])) if "/" in txt else float(txt)
        if not close(val, want, 1e-6):
            raise AuditError(f"grid-in reads {txt!r}, independently derived {want!r}")


def _structure(item: Item) -> None:
    """The checks that need no mathematics: the shape of the item itself."""
    if not item.stem.strip():
        raise AuditError("empty stem")
    if item.fmt == "mcq":
        if len(item.choices) != 4:
            raise AuditError(f"{len(item.choices)} options, not four")
        if len(set(item.choices)) != len(item.choices):
            raise AuditError(f"an option is repeated: {item.choices}")
        if item.answer not in "ABCD":
            raise AuditError(f"answer letter {item.answer!r}")
        if len(item.reasons) != 4:
            raise AuditError("every option needs a reason, blank only for the key")
        if sum(1 for r in item.reasons if not r) != 1:
            raise AuditError("exactly one option is the key")
    elif item.fmt == "spr":
        if not item.answer.strip():
            raise AuditError("grid-in with no answer")
    else:
        raise AuditError(f"unknown format {item.fmt!r}")
