"""How a probability is written down, and how four of them are chosen.

A probability is a rational number, and the whole topic keeps it as one:
``fractions.Fraction`` from the first cell count to the printed option. No
float is ever used to compute or to compare a value -- only to sort four
options into ascending order, which ``item.assemble`` does for us.

The difficulty here is not the arithmetic, it is the *surface*. The College
Board prints the same number four different ways and the difference is the
item:

    10/40      unreduced over the grand total  (1.1, 1.2, 1.6, 1.12, 2.2)
    1/4        reduced                          (2.1, 2.6, 2.12, 3.8)
    0.40       a decimal                        (1.4, 1.9, 3.7)
    13.3%      a percent to a stated place      (3.6)

``Exact`` cannot hold any of the unreduced ones -- it normalises 12/16 to 3/4
the moment it is built -- so ``PVal`` carries the exact value *and the string
the page prints*, and equality is by value alone, so a distractor that lands
on the key is still recognised as a duplicate and dropped. Every reader in
this package parses the printed string back; nothing downstream has to know
which of the four surfaces an item chose.
"""

from __future__ import annotations

import random
import re
from fractions import Fraction as Q

from ...exact import MINUS, Exact
from ...item import Item, ItemError, Mis, assemble, assemble_text, gridin_mistakes

__all__ = ["Q", "q", "PVal", "ratio", "reduced", "decimal", "percent", "count",
           "grid", "griddable", "snap", "unambiguous", "places_needed", "dec",
           "pick", "mcq", "spr", "text_mcq", "tidy", "roll_fmt", "FILLER",
           "GRID_CHARS"]

FILLER = "near-miss arithmetic slip"       # item._fillers' reason; never shipped here
GRID_CHARS = 5                             # the digital SAT's student-response field


def q(v) -> Q:
    """Anything numeric to an exact Fraction. A float arrives as its decimal."""
    if isinstance(v, Q):
        return v
    if isinstance(v, float):
        return Q(str(v))
    return Q(v)


def places_needed(v, cap: int = 6) -> int | None:
    """Fewest decimal places that print `v` exactly, or None if it never ends."""
    v = q(v)
    for p in range(cap + 1):
        if (v * 10 ** p).denominator == 1:
            return p
    return None


def dec(v, places: int) -> str:
    """An exact rational as a decimal string, rounded half up.

    ``dec(Q(2,3), 2)`` is ``'0.67'``; ``dec(Q(1,250), 3)`` is ``'0.004'``.
    A negative prints U+2212, the sign the typeset page carries.
    """
    v = q(v)
    neg = v < 0
    a = -v if neg else v
    scaled = a * 10 ** places
    n = scaled.numerator // scaled.denominator
    if 2 * (scaled - n) >= 1:
        n += 1
    s = str(n).rjust(places + 1, "0")
    whole, frac = s[:len(s) - places] if places else s, s[len(s) - places:] if places else ""
    out = f"{int(whole):,}" + ("." + frac if places else "")
    return (MINUS + out) if neg else out


def snap(v, step) -> Q:
    """Round to the nearest multiple of `step`, halves upward."""
    v, step = q(v), q(step)
    k = v / step
    n = k.numerator // k.denominator
    if 2 * (k - n) >= 1:
        n += 1
    return n * step


def unambiguous(v, step) -> Q:
    """`v` rounded to `step`, unless it sits exactly halfway.

    Copied verbatim in behaviour from ``percentages/values.py`` -- `ratios`
    took the same copy, which makes it the house pattern rather than a
    borrowing. A stem that says *closest*, *nearest* or *approximately*, or
    that asks for a percent to a stated place, has an answer only while one
    printable value is nearer than every other. 6/45 is 13.33% and rounds
    cleanly; 37/40 is 92.5% and whether that is 92 or 93 is a convention the
    stem never states, so the draw is thrown away instead of shipped with an
    answer a carefully taught student gets wrong.
    """
    v, step = q(v), q(step)
    k = v / step
    if 2 * (k - k.numerator // k.denominator) == 1:
        raise ItemError("this value sits exactly halfway between two answers, and "
                        "which of them is nearest is a convention rather than "
                        "mathematics")
    return snap(v, step)


# ------------------------------------------------------------------ the value

class PVal(Exact):
    """An exact rational that prints the way its item prints it.

    `text` is the printed string and `coef` the exact value; the two are set
    together and never derived from one another downstream. Equality and
    hashing ignore the surface, so 12/16 and 3/4 are one option and only one
    of them can be offered.
    """

    def __init__(self, value, text: str):
        object.__setattr__(self, "coef", q(value))
        object.__setattr__(self, "pi_exp", Q(0))
        object.__setattr__(self, "rad", 1)
        object.__setattr__(self, "text", text)

    def __eq__(self, other):
        return (isinstance(other, Exact)
                and (self.coef, self.pi_exp, self.rad)
                == (other.coef, other.pi_exp, other.rad))

    def __hash__(self):
        return hash((self.coef, self.pi_exp, self.rad))

    @property
    def form(self) -> tuple:
        """Surface signature, read off the printed string rather than the value.

        `assemble` refuses a key that is the only option of its form, and for
        this topic the form a student sees is the *spelling*: 10/40 against
        three other fractions is not a lone option, although as a value it is
        the only one in lowest terms. Reading the value here would let a
        reduced key print among three unreduced ones and call it safe.
        """
        t = self.text
        return ("/" in t, "." in t, "%" in t, t.startswith((MINUS, "-")))

    def plain(self) -> str:
        return self.text

    def latex(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f"PVal({self.text})"


def ratio(num: int, den: int) -> PVal:
    """A fraction printed exactly as its two counts: 12/16, 415/799."""
    if den == 0:
        raise ItemError("a probability with an empty denominator")
    return PVal(Q(num, den), f"{num}/{den}")


def reduced(v) -> PVal:
    """A fraction in lowest terms, or a bare integer when it is one: 1/4, 0, 2."""
    v = q(v)
    return PVal(v, str(v.numerator) if v.denominator == 1
                else f"{v.numerator}/{v.denominator}")


def decimal(v, places: int) -> PVal:
    """A decimal to a fixed number of places. The stored value is the printed
    one: an option reading 0.67 *is* 67/100 for every comparison downstream."""
    text = dec(v, places)
    return PVal(q(text.replace(",", "").replace(MINUS, "-")), text)


def percent(v, places: int) -> PVal:
    """A percent to a fixed number of places; `v` is the probability, not the
    percentage. 6/45 at one place prints 13.3% and stores 133/1000."""
    body = dec(q(v) * 100, places)
    return PVal(q(body.replace(",", "").replace(MINUS, "-")) / 100, body + "%")


def count(n) -> PVal:
    """A whole number of things, with the thousands separator the source prints."""
    n = q(n)
    if n.denominator != 1:
        raise ItemError("a count must be a whole number")
    return PVal(n, f"{n.numerator:,}")


# ------------------------------------------------------------------ grid-ins

def _terminating(v: Q) -> bool:
    d = v.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def grid(v) -> str:
    """The digital SAT student-produced response, or a refusal.

    The answer field takes five characters. A probability that needs more is
    not a grid-in a student can enter, and the draw has to be refused *here*,
    at build time, rather than discovered when somebody reads the page: the
    audit re-derives the value and would agree with an unenterable one.

    A terminating decimal is preferred when it fits, which is what the source
    key gives -- 13/50 is keyed 0.26 and 3/10 is keyed 0.3 -- and the fraction
    is used otherwise: 1/14, 5/7 and 23/60 all fit, 415/799 does not and is
    refused.
    """
    v = q(v)
    if v < 0:
        raise ItemError("a probability is never negative")
    if v.denominator == 1:
        s = str(v.numerator)
    elif _terminating(v) and len(dec(v, places_needed(v, 8), )) <= GRID_CHARS:
        s = dec(v, places_needed(v, 8))
    else:
        s = f"{v.numerator}/{v.denominator}"
    if len(s) > GRID_CHARS or "," in s:
        raise ItemError(f"{s} needs more than the grid's {GRID_CHARS} characters, "
                        "so it is not an answer a student can enter")
    return s


def griddable(v) -> bool:
    try:
        grid(v)
        return True
    except ItemError:
        return False


# ------------------------------------------------------------------ assembly

def pick(pool: dict, order, wrongs=None) -> list:
    """The misconceptions this draw offers, in the order it offers them.

    Every template keeps its wrong answers in a named pool and a default
    order. A free draw takes that order; a source item passes `wrongs`, naming
    the three the College Board item writer actually reached for, so the
    engine offers those and no others. An entry whose value is None does not
    apply to this draw -- the frame does not admit the mistake, or it lands on
    a number nobody would write down -- and is skipped rather than offered.
    """
    names = list(order if wrongs is None else wrongs)
    out = []
    for name in names:
        if name not in pool:
            raise ItemError(f"no misconception named {name!r} in this pool")
        why, value = pool[name]
        if value is not None:
            out.append((why, value))
    return out


def roll_fmt(rng: random.Random, fmt):
    """A free draw picks its own format; a source item states one.

    Ten of the 36 official items are grid-ins, so a template that can only be
    reached as multiple choice from a free draw leaves a quarter of its own
    behaviour unswept by any volume check.
    """
    return fmt or ("spr" if rng.random() < 0.25 else "mcq")


def tidy(text: str) -> str:
    """One space between words, whatever the f-string did with the line breaks.
    A deliberate line break is written as \\n and survives; runs of spaces do not."""
    return re.sub(r"[ \t]+", " ", re.sub(r" *\n *", "\n", text)).strip()


def mcq(template: str, skill: str, difficulty: str, seed: int, stem: str,
        key: PVal, mistakes, rng: random.Random, rationale: str, *,
        params: dict, table=None, figure=None, signed: bool = False) -> Item:
    """Four options from a named pool. A filler is a failure, not a fallback.

    `item.assemble` patches a short misconception list with arithmetic
    near-misses (key ± 1, key × 2). Those are plain `Exact` values, so they
    would print reduced in an item whose other three options are unreduced --
    and, worse, they are wrong answers nobody can explain. This topic's pools
    are wide enough that the fallback is never needed, so reaching it is a bug
    in the pool and is raised as one.
    """
    ms = [Mis(why, val) for why, val in mistakes if val is not None]
    choices, latex, reasons, letter = assemble(key, ms, rng, signed=signed)
    if any(r == FILLER for r in reasons):
        raise ItemError("the misconception pool ran short and assemble reached for "
                        "an unexplainable near-miss")
    return Item(template, skill, difficulty, seed, tidy(stem), "mcq", key, letter,
                tidy(rationale), list(choices), list(reasons), list(choices),
                figure=figure, table=table, params=params)


def spr(template: str, skill: str, difficulty: str, seed: int, stem: str,
        value, rationale: str, *, params: dict, table=None, figure=None,
        mistakes=()) -> Item:
    """A grid-in. `grid` refuses anything the answer field cannot hold.
    `mistakes` is the (reason, value) list the multiple-choice path offers."""
    entry = grid(value)
    key = PVal(q(value), entry)
    return Item(template, skill, difficulty, seed, tidy(stem), "spr",
                key, entry, tidy(rationale),
                figure=figure, table=table, params=params,
                spr_mistakes=gridin_mistakes(key, [Mis(w, v) for w, v in mistakes]))


def text_mcq(template: str, skill: str, difficulty: str, seed: int, stem: str,
             key: str, wrong, rng: random.Random, rationale: str, *,
             params: dict, table=None, figure=None) -> Item:
    """Options that are words or expressions, so there is no order to sort by."""
    choices, reasons, letter = assemble_text(
        key, [Mis(why, val) for why, val in wrong], rng)
    return Item(template, skill, difficulty, seed, tidy(stem), "mcq", PVal(0, "0"),
                letter, tidy(rationale), list(choices), list(reasons), list(choices),
                figure=figure, table=table, params=params)
