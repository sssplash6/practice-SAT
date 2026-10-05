"""Every generator, addressable by name, with retry on rejected parameters.

Templates come from the topics; nothing is listed here by hand. Rejecting a
draw is normal: a template refuses parameters that would produce a nested
radical, a non-monomial inverse, a degenerate triangle or an answer that
cannot be entered in a grid-in. The registry just draws again.
"""

from __future__ import annotations

import random
import re
from typing import Callable

from .audit import audit
from .item import Item, ItemError
from .topic import Topic, load_topics

__all__ = ["templates", "topic_of", "generate", "generate_many", "typeset"]

_TEMPLATES: dict[str, Callable] = {}
_OWNER: dict[str, str] = {}
FALLBACK_ATTEMPTS = 2_000


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


_SPACED_MINUS = re.compile(r"(?<=[\w)²³.]) - (?=[\w(])")
_LEADING_MINUS = re.compile(r"(?<![\w)\-])-(?=\d)")
_RANGE = re.compile(r"(?<![\d-])(\d{1,3})-(?=\d{1,3}(?![\d-]))")


def typeset(text):
    """The typography every printed item shares: a minus sign is U+2212, a range takes an en dash and a product
    a times sign, whatever a template typed. Answers are compared normalised (norm_text), so this is display only."""
    if not isinstance(text, str):
        return text
    text = _SPACED_MINUS.sub(" \u2212 ", text)
    text = _LEADING_MINUS.sub("\u2212", text)
    text = _RANGE.sub("\\1\u2013", text)
    return text.replace(" * ", " \u00d7 ")


def _typeset_item(item: Item) -> Item:
    item.stem = typeset(item.stem)
    item.choices = [typeset(c) for c in item.choices]
    item.rationale = typeset(item.rationale)
    item.reasons = [typeset(r) for r in item.reasons]
    if item.table:
        item.table = [[typeset(c) for c in row] if isinstance(row, (list, tuple)) else row for row in item.table]
    return item


def generate(name: str, seed: int, attempts: int = 60, verify: bool = True, **kw) -> Item:
    """Deterministic in `seed`: the same seed always yields the same item.

    Every item is re-derived by `audit` before it is returned. A failed audit
    is a bug in a template, not an unlucky draw, so AuditError propagates
    instead of being retried away -- nothing wrong should ever leave here
    quietly. Pass verify=False only to measure the cost of the check.
    """
    fn = templates()[name]
    # A request with explicit parameters keeps its caller's retry limit. The
    # extra range is only for ordinary bank seeds that exhausted all 60 draws.
    fallback = attempts == 60 and not kw
    phases = (range(attempts), range(attempts, FALLBACK_ATTEMPTS)) if fallback \
        else (range(attempts),)
    for phase in phases:
        for i in phase:
            try:
                item = fn(random.Random(seed * 1_000_003 + i), seed, **kw)
            except (ItemError, ValueError, ZeroDivisionError, KeyError, StopIteration):
                continue
            if verify:
                audit(item)
            return _typeset_item(item)
    limit = FALLBACK_ATTEMPTS if fallback else attempts
    raise ItemError(f"{name}: no valid item after {limit} attempts (seed {seed})")


def generate_many(n: int, seed0: int = 0, names: list[str] | None = None,
                  topics: list[str] | None = None):
    names = names or [n_ for n_ in templates()
                      if not topics or topic_of(n_) in topics]
    for i in range(n):
        yield generate(names[i % len(names)], seed0 + i)
