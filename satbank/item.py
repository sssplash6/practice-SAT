"""The item model, and the part that actually decides item quality:
turning a key plus a list of misconceptions into four defensible options.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from fractions import Fraction

from .exact import E, Exact

__all__ = ["Item", "Mis", "assemble", "ItemError"]

LETTERS = "ABCD"


class ItemError(Exception):
    """Raised when a parameterization cannot yield a shippable item.

    Generators catch this and reroll. Rejecting is normal and cheap; shipping
    a flawed item is not.
    """


@dataclass
class Mis:
    """One wrong option and the specific mistake that produces it."""
    reason: str
    value: Exact | None


@dataclass
class Item:
    template: str
    skill: str
    difficulty: str
    seed: int
    stem: str
    fmt: str                       # "mcq" | "spr"
    key: Exact
    answer: str                    # letter for mcq, entered value for spr
    rationale: str
    choices: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    latex_choices: list[str] = field(default_factory=list)
    figure: str | None = None
    source_id: str | None = None   # official item this template was learned from

    def pretty(self, show_reasons: bool = True) -> str:
        head = f"[{self.template} | {self.difficulty} | seed={self.seed}]"
        if self.source_id:
            head += f"  (learned from {self.source_id})"
        out = [head]
        if self.figure:
            out.append("  <figure: %d bytes of SVG>" % len(self.figure))
        out.append(self.stem)
        if self.fmt == "spr":
            out.append(f"  [grid-in]  answer: {self.answer}")
        else:
            for i, ch in enumerate(self.choices):
                mark = "*" if LETTERS[i] == self.answer else " "
                tail = ""
                if show_reasons:
                    tail = f"   <- {self.reasons[i]}" if self.reasons[i] else "   <- KEY"
                out.append(f"  {mark} {LETTERS[i]}) {ch}{tail}")
        out.append(f"    why: {self.rationale}")
        return "\n".join(out)


def _usable(v, key: Exact) -> bool:
    """Geometry measures are positive; a negative or zero option is a freebie."""
    return isinstance(v, Exact) and float(v) > 0 and v != key


def _fillers(key: Exact):
    """Neutral near-misses, used only when the misconception list runs short.

    Multiplicative so the pi/radical form of the key is preserved.
    """
    for f in (Fraction(2), Fraction(1, 2), Fraction(3), Fraction(1, 3),
              Fraction(4), Fraction(3, 2), Fraction(10), Fraction(2, 3)):
        yield Mis("near-miss arithmetic slip", key * E(f))


def assemble(key: Exact, mistakes: list[Mis], rng: random.Random):
    """Choose three distractors, then order all four the way the SAT does.

    Two rules do most of the work:
      * every option must be reachable by a real mistake (misconceptions first,
        fillers only to patch a short list);
      * the key must never be the only option of its surface form -- a lone
        integer among radicals, or the only fraction, is guessable without
        doing any geometry.
    """
    seen = {key}
    same_form: list[Mis] = []
    other_form: list[Mis] = []
    for m in mistakes:
        if not _usable(m.value, key) or m.value in seen:
            continue
        seen.add(m.value)
        (same_form if m.value.form == key.form else other_form).append(m)

    picked = same_form[:3]
    for m in other_form:
        if len(picked) >= 3:
            break
        picked.append(m)
    for m in _fillers(key):
        if len(picked) >= 3:
            break
        if not _usable(m.value, key) or m.value in seen or m.value.form != key.form:
            continue
        seen.add(m.value)
        picked.append(m)

    if len(picked) < 3:
        raise ItemError("could not build three distinct distractors")
    if sum(1 for m in picked if m.value.form == key.form) == 0:
        raise ItemError("key would be the only option of its form")

    options = [(key, "")] + [(m.value, m.reason) for m in picked]
    options.sort(key=lambda t: float(t[0]))            # SAT orders choices ascending
    choices = [v.plain() for v, _ in options]
    latex = [v.latex() for v, _ in options]
    reasons = [r for _, r in options]
    letter = LETTERS[next(i for i, (_, r) in enumerate(options) if r == "")]
    return choices, latex, reasons, letter
