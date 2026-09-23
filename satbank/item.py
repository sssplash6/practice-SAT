"""The item model, and the part that actually decides item quality:
turning a key plus a list of misconceptions into four defensible options.
"""

from __future__ import annotations

import itertools
import random
import re
from dataclasses import dataclass, field
from fractions import Fraction

from .exact import E, Exact

__all__ = ["Item", "Mis", "assemble", "assemble_text", "ItemError", "numeral",
           "norm_text", "shortlist", "hands_the_key_over", "gridin_mistakes"]

SUPERSCRIPT = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")

# a unit printed after the number, as some source items print their options:
# "8 cm²", "12 ft", "35 degrees". The stem has already said what the unit is.
UNIT_SUFFIX = re.compile(r"\s*(cm|mm|km|inches|inch|feet|foot|yards|yard|units|unit|"
                         r"degrees|degree|°[FC]?|%|m|in|ft|yd)[²³]?[23]?$", re.I)


def norm_text(s) -> str:
    """One spelling for an answer written two ways.

    3,025 is 3025; π is pi; a printed superscript is the digit it stands for;
    a multiplication dot is a star. The star is dropped inside an expression --
    4πr³ and 4pi*r^3 are one answer -- and kept between bare numerals, where
    3·39 and 339 are two different answers.
    """
    t = (str(s).translate(SUPERSCRIPT)
         .replace(",", "").replace(" ", "").replace("−", "-")
         .replace("·", "*").replace("×", "*").replace("π", "pi")
         .replace("√", "sqrt").replace("^", "")).lower()
    if any(c.isalpha() for c in t.replace("pi", "")):
        t = t.replace("*", "")
    return t.rstrip(".")


def numeral(text: str) -> float | None:
    """The number an option carries, or None when it is not a bare number.

    Only a known unit is stripped -- never a symbol that changes the value, so
    "12π" stays unreadable as a number and cannot be mistaken for 12.
    """
    raw = str(text).strip()
    # "6 m" is six metres; "6m" is six times m, and stripping the letter would
    # read an algebra option as a number. A unit has to stand apart from its
    # value, or be a symbol that cannot be a variable.
    t = raw if (re.search(r"[A-Za-z]$", raw) and not re.search(r"[\s°%]", raw)) \
        else UNIT_SUFFIX.sub("", raw)
    t = t.replace(",", "").replace(" ", "").replace("−", "-").lstrip("$")
    try:
        if "/" in t:
            a, b = t.split("/", 1)
            return float(a) / float(b)
        return float(t)
    except (ValueError, ZeroDivisionError):
        return None

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


def gridin_mistakes(key, mistakes: list[Mis]) -> list[Mis]:
    """The mistakes a grid-in can name: a value, not the key, first of its value.

    Compared by value, as a typed answer is matched, so 1/2 and 0.5 are one
    wrong answer. What this drops is what the audit refuses.
    """
    out: list[Mis] = []
    seen = [float(key)]
    for m in mistakes:
        if m.value is None:
            continue
        v = float(m.value)
        if any(abs(v - o) <= 1e-9 * max(1.0, abs(v), abs(o)) for o in seen):
            continue
        seen.append(v)
        out.append(m)
    return out


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
    # A grid-in's wrong answers, each with the mistake that produces it, so a
    # wrong typed value can be named the way a wrong option is. Build it with
    # `gridin_mistakes`. Keyword-only: the fields after it are passed by
    # position all over the topics.
    spr_mistakes: list[Mis] = field(default_factory=list, kw_only=True)
    latex_choices: list[str] = field(default_factory=list)
    figure: str | None = None
    table: list[list[str]] | None = None
    params: dict = field(default_factory=dict)   # what the audit re-derives from
    source_id: str | None = None   # official item this template was learned from

    def pretty(self, show_reasons: bool = True) -> str:
        head = f"[{self.template} | {self.difficulty} | seed={self.seed}]"
        if self.source_id:
            head += f"  (learned from {self.source_id})"
        out = [head]
        if self.figure:
            out.append("  <figure: %d bytes of SVG>" % len(self.figure))
        out.append(self.stem)
        if self.table:
            w = [max(len(r[i]) for r in self.table) for i in range(len(self.table[0]))]
            for row in self.table:
                out.append("      | " + " | ".join(c.ljust(w[i]) for i, c in enumerate(row)) + " |")
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


def _share_the_key_s_sign(key: Exact, picked: list[Mis], pool: list[Mis],
                          signed: bool) -> list[Mis]:
    """Make sure at least one distractor has the key's sign.

    Across the 147 official multiple-choice items with numeric options, the
    key is never the only option of its sign -- not once. A lone negative
    among three positives is the answer, and a student who notices that needs
    no algebra. One same-signed option is all it takes, though: the source
    sets are usually mixed, so demanding that every distractor match the key's
    sign would throw away the wrong options College Board actually uses.
    """
    if not signed or any((float(m.value) < 0) == (float(key) < 0) for m in picked):
        return picked
    swap = next((m for m in pool if m not in picked
                 and (float(m.value) < 0) == (float(key) < 0)), None)
    if swap is None:
        raise ItemError("key would be the only option of its sign")
    return picked[:-1] + [swap]


def _usable(v, key: Exact, signed: bool = False) -> bool:
    """A geometry measure is positive, so a negative option there is a freebie
    a student can cross out without doing any geometry. Algebra answers are
    signed, and `signed=True` says so.
    """
    if not isinstance(v, Exact) or v == key:
        return False
    return True if signed else float(v) > 0


def _fillers(key: Exact, style: str = "scale"):
    """Neutral near-misses, used only when the misconception list runs short.

    "scale" multiplies, which preserves the pi or radical form of the key --
    the right choice when the answer is a measure. "shift" adds, which is what
    a near-miss looks like when the answer is a solution to an equation.
    """
    if style == "shift":
        for d in (1, -1, 2, -2, 3, -3, 4, 5, -5, 10):
            yield Mis("near-miss arithmetic slip", key + E(d))
        return
    for f in (Fraction(2), Fraction(1, 2), Fraction(3), Fraction(1, 3),
              Fraction(4), Fraction(3, 2), Fraction(10), Fraction(2, 3)):
        yield Mis("near-miss arithmetic slip", key * E(f))


# `pi` as a word, not two letters inside one -- the same reading as
# `check._shape`, which this mirrors. A digit may precede it (12pi is twelve
# pi); a letter never can, which keeps opinion, hospital and camping out.
_PI_WORD = re.compile(r"(?<![A-Za-z])pi(?![A-Za-z])")


def _surface(opt: str) -> tuple:
    """What an option looks like at a glance. Mirrors `check._shape`.

    Kept here rather than imported because `check` imports this module; the
    two must agree, and a change to either belongs in both.
    """
    return (bool(re.search(r"[a-zA-Z]", _PI_WORD.sub("", opt.replace("π", "")))),
            "π" in opt or _PI_WORD.search(opt) is not None,
            "√" in opt or "sqrt" in opt,
            "/" in opt, "." in opt, opt.strip().startswith(("-", "\N{MINUS SIGN}")))


def hands_the_key_over(choices: list[str], letter: str) -> bool:
    """Do the four printed options give the answer away by their looks alone?

    The giveaway is the key standing alone in its printed shape while the
    other three form a crowd for it to stand out from -- the only negative,
    the only fraction, the only radical. Four options that all look different
    are not a giveaway: then nothing is lone, and the key does not stand out.
    """
    shapes = [_surface(c) for c in choices]
    key_i = LETTERS.index(letter)
    others = [s for i, s in enumerate(shapes) if i != key_i]
    return shapes.count(shapes[key_i]) == 1 and max(others.count(s) for s in others) > 1


def _shortlist(key: Exact, mistakes: list[Mis], fmt_value=None) -> list[Mis]:
    """Which three of a named pool print. Signed answers only.

    `assemble` takes the first three wrong answers it can use, preferring the
    key's own surface form, and for a signed answer that is the wrong three
    often enough to matter. A perpendicular slope is a negative reciprocal, so
    the key is a fraction, so the fractions go in first and the integers --
    the given line's own slope among them, the error the item is about -- are
    crowded out by weaker mistakes that happen to be fractions too. What
    prints is one negative fraction against three that are not, and a student
    who knows only that a perpendicular slope is a negative reciprocal picks
    it without computing anything.

    So a pool may name more mistakes than can print, and this chooses among
    them earliest first, so the pool's order still says which mistakes matter
    most and a pool whose first three already print well is left untouched. A
    trio is refused when no wrong answer carries the key's sign, or when the
    printed four would hand the key over.

    Nothing here reads the key's value: the choice is made on how the four
    options look, which is the property being protected, and every option that
    prints still carries the misconception that produces it. A source item
    naming its own three never reaches this -- College Board chose there.
    """
    def printed(v) -> str:
        return fmt_value(v) if fmt_value else v.plain()

    pool, seen = [], {key}
    for m in mistakes:
        if not isinstance(m.value, Exact) or m.value in seen:
            continue
        seen.add(m.value)
        pool.append((m, m.value, printed(m.value)))
    if len(pool) <= 3:
        return [m for m, _, _ in pool]

    key_text, negative = printed(key), float(key) < 0
    for trio in itertools.combinations(pool, 3):
        if not any((float(v) < 0) == negative for _, v, _ in trio):
            continue
        if not hands_the_key_over([key_text] + [t for _, _, t in trio], "A"):
            return [m for m, _, _ in trio]
    return [m for m, _, _ in pool[:3]]


shortlist = _shortlist          # public name; `assemble`'s keyword shadows it


def assemble(key: Exact, mistakes: list[Mis], rng: random.Random, fmt_value=None,
             signed: bool = False, fillers: str = "scale", forbid=(),
             shortlist: bool = False, named_only: bool = False):
    """Choose three distractors, then order all four the way the SAT does.

    Two rules do most of the work:
      * every option must be reachable by a real mistake (misconceptions first,
        fillers only to patch a short list);
      * the key must never be the only option of its surface form -- a lone
        integer among radicals, or the only fraction, is guessable without
        doing any geometry.

    `signed=True` allows negative and zero options, which an algebra answer
    needs and a measure must not have.

    `forbid` lists values that are also correct and so must never be offered --
    the other root of the quadratic, the second intersection, the solution the
    stem's "which of the following" would equally accept. Only the caller knows
    these; this function cannot work them out from a key. Passing them matters
    because the fillers below are near-misses built by arithmetic (key + 1,
    key - 2), so a template that carefully strikes the other root from its own
    pool can have this function hand it straight back when the pool runs short.
    That produces an item with two correct options, which is the one defect the
    gate cannot see.

    `named_only=True` takes the fillers out of play altogether: a pool that
    cannot name three wrong answers is a bug in the pool, and this raises
    rather than patching it with a near-miss no misconception explains. It is
    the same rule `probability` enforces on itself from the outside -- its
    `values.mcq` raises when a reason comes back reading "near-miss arithmetic
    slip" -- and it is why that topic's distractor naming is 100% rather than
    merely above the gate's 80% floor. A filler is a wrong answer a teacher
    cannot explain to the student who picked it, and the gate counts it as
    unnamed, so a topic that never reaches one is measurably better than the
    floor and knows why.

    It is off by default because nineteen topics were built against the
    fallback and it is not this function's business to decide when they change.
    """
    banned = {v for v in forbid if isinstance(v, Exact)}
    if shortlist and signed:
        mistakes = _shortlist(key, [m for m in mistakes
                                    if isinstance(m.value, Exact) and m.value not in banned],
                              fmt_value)
    seen = {key}
    same_form: list[Mis] = []
    other_form: list[Mis] = []
    for m in mistakes:
        if not _usable(m.value, key, signed) or m.value in seen or m.value in banned:
            continue
        seen.add(m.value)
        (same_form if m.value.form == key.form else other_form).append(m)

    picked = same_form[:3]
    for m in other_form:
        if len(picked) >= 3:
            break
        picked.append(m)
    if named_only and len(picked) < 3:
        raise ItemError(f"only {len(picked)} of the three distractors name a "
                        f"misconception, and named_only forbids patching the pool "
                        f"with a near-miss nothing explains")
    for m in _fillers(key, fillers):
        if len(picked) >= 3:
            break
        if (not _usable(m.value, key, signed) or m.value in seen
                or m.value in banned or m.value.form != key.form):
            continue
        seen.add(m.value)
        picked.append(m)

    if len(picked) < 3:
        raise ItemError("could not build three distinct distractors")
    if sum(1 for m in picked if m.value.form == key.form) == 0:
        raise ItemError("key would be the only option of its form")
    picked = _share_the_key_s_sign(key, picked, same_form + other_form, signed)

    options = [(key, "")] + [(m.value, m.reason) for m in picked]
    options.sort(key=lambda t: float(t[0]))            # SAT orders choices ascending
    choices = [fmt_value(v) if fmt_value else v.plain() for v, _ in options]
    latex = [fmt_value(v) if fmt_value else v.latex() for v, _ in options]
    reasons = [r for _, r in options]
    letter = LETTERS[next(i for i, (_, r) in enumerate(options) if r == "")]
    return choices, latex, reasons, letter


def assemble_text(key: str, distractors: list[Mis], rng: random.Random):
    """Assembly for options that are expressions or statements, not values.

    No ascending order to hide behind, so the key's position is randomized.
    """
    picked, seen = [], {key}
    for m in distractors:
        if m.value is None or m.value in seen:
            continue
        seen.add(m.value)
        picked.append(m)
        if len(picked) == 3:
            break
    if len(picked) < 3:
        raise ItemError("could not build three distinct expression distractors")
    options = [(key, "")] + [(m.value, m.reason) for m in picked]
    rng.shuffle(options)
    letter = LETTERS[next(i for i, (_, r) in enumerate(options) if r == "")]
    return [v for v, _ in options], [r for _, r in options], letter
