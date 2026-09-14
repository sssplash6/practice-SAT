"""Every generator, addressable by name, with retry on rejected parameters.

Templates come from the topics; nothing is listed here by hand. Rejecting a
draw is normal: a template refuses parameters that would produce a nested
radical, a non-monomial inverse, a degenerate triangle or an answer that
cannot be entered in a grid-in. The registry just draws again.
"""

from __future__ import annotations

import random
from typing import Callable

from .audit import audit
from .item import Item, ItemError
from .topic import Topic, load_topics

__all__ = ["templates", "topic_of", "generate", "generate_many"]

_TEMPLATES: dict[str, Callable] = {}
_OWNER: dict[str, str] = {}


def templates() -> dict[str, Callable]:
    """Name -> generator, across every topic. Names are unique engine-wide."""
    if not _TEMPLATES:
        for slug, topic in load_topics().items():
            for name, fn in topic.templates.items():
                if name in _TEMPLATES:
                    raise RuntimeError(
                        f"{slug} and {_OWNER[name]} both define the template {name!r}")
                _TEMPLATES[name] = fn
                _OWNER[name] = slug
    return _TEMPLATES


def topic_of(name: str) -> str:
    templates()
    return _OWNER[name]


def generate(name: str, seed: int, attempts: int = 60, verify: bool = True, **kw) -> Item:
    """Deterministic in `seed`: the same seed always yields the same item.

    Every item is re-derived by `audit` before it is returned. A failed audit
    is a bug in a template, not an unlucky draw, so AuditError propagates
    instead of being retried away -- nothing wrong should ever leave here
    quietly. Pass verify=False only to measure the cost of the check.
    """
    fn = templates()[name]
    for i in range(attempts):
        try:
            item = fn(random.Random(seed * 1_000_003 + i), seed, **kw)
        except (ItemError, ValueError, ZeroDivisionError, KeyError, StopIteration):
            continue
        if verify:
            audit(item)
        return item
    raise ItemError(f"{name}: no valid item after {attempts} attempts (seed {seed})")


def generate_many(n: int, seed0: int = 0, names: list[str] | None = None,
                  topics: list[str] | None = None):
    names = names or [n_ for n_ in templates()
                      if not topics or topic_of(n_) in topics]
    for i in range(n):
        yield generate(names[i % len(names)], seed0 + i)
