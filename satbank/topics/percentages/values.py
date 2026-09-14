"""How a percentage answer is written down, and how four of them are chosen.

A percent item answers in three surface forms and the difference matters on
the page: a count (``1,170,000``), a percent (``94.25%``) and money
(``$21.00``). The shared ``Exact`` renders a rational as a fraction --
``125/2`` where the College Board prints ``62.5%`` -- and the shared audit
accepts an option whose text is not ``key.plain()`` only if it parses as a
bare float, which ``$21.00`` and ``5.4%`` do not.

``Num`` is an ``Exact`` that knows its own surface form, so the printed option
and ``key.plain()`` are the same string and every layer downstream agrees.
Arithmetic is never done on a ``Num``: templates compute in exact
``Fraction`` and wrap once, at the end, when the value becomes an option.
"""

from __future__ import annotations

import random
import re
from fractions import Fraction as Q

from ...exact import Exact
from ...item import Item, ItemError, Mis, assemble, assemble_text

__all__ = ["Q", "q", "Num", "dec", "places_needed", "grid", "tidy", "snap",
           "mcq", "spr", "text_mcq"]


def q(v) -> Q:
    """Anything numeric to an exact Fraction. A float arrives as its decimal."""
    if isinstance(v, Q):
        return v
    if isinstance(v, float):
        return Q(str(v))
    return Q(v)


def snap(v, step) -> Q:
    """Round to the nearest multiple of `step`, halves upward.

    An item that says "closest to" or "to the nearest tenth of a percent"
    rounds, and it has to round the same way twice -- here and in the
    independent solver -- or the audit reports a disagreement that is really
    a tie-break.
    """
    v, step = q(v), q(step)
    k = v / step
    n = k.numerator // k.denominator
    if 2 * (k - n) >= 1:
        n += 1
    return n * step


def dec(v, places: int, group: bool = True) -> str:
    """An exact rational as a decimal string, rounded half up.

    ``dec(Q(27,5), 1)`` is ``'5.4'`` and ``dec(Q(145770), 0)`` is
    ``'145,770'`` -- the thousands separator the source items print.
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
    return ("-" + out) if neg else out


def places_needed(v, cap: int = 2) -> int:
    """Fewest decimals that print `v` exactly, or `cap` when it does not end."""
    v = q(v)
    for p in range(cap + 1):
        if (v * 10 ** p).denominator == 1:
            return p
    return cap


class Num(Exact):
    """An exact rational that prints the way its item prints it.

    ``style`` is ``plain`` (a count), ``percent`` or ``money``; ``places``
    fixes the number of decimals, or is left to the value itself. Equality
    and hashing ignore the surface form, so a distractor that lands on the
    key is still recognised as a duplicate and dropped.
    """

    def __init__(self, value, style: str = "plain", places: int | None = None):
        object.__setattr__(self, "coef", q(value))
        object.__setattr__(self, "pi_exp", Q(0))
        object.__setattr__(self, "rad", 1)
        object.__setattr__(self, "style", style)
        object.__setattr__(self, "places", places)

    def __eq__(self, other):
        return (isinstance(other, Exact)
                and (self.coef, self.pi_exp, self.rad)
                == (other.coef, other.pi_exp, other.rad))

    def __hash__(self):
        return hash((self.coef, self.pi_exp, self.rad))

    def plain(self) -> str:
        p = places_needed(self.coef) if self.places is None else self.places
        body = dec(self.coef, p)
        if self.style == "percent":
            return body + "%"
        if self.style == "money":
            return ("-$" + body[1:]) if body.startswith("-") else "$" + body
        return body

    def latex(self) -> str:
        return self.plain()

    def __repr__(self) -> str:
        return f"Num({self.plain()})"


_STRIP = re.compile(r"[$,%]")


def _parse(text: str) -> Q:
    """A rendered option back to its exact value, fillers included."""
    return Q(_STRIP.sub("", text))


def grid(v) -> str:
    """Student-produced-response form: the shortest exact entry."""
    v = q(v)
    if v.denominator == 1:
        return str(v.numerator)
    for p in range(1, 9):
        if (v * 10 ** p).denominator == 1:
            return dec(v, p, group=False)
    return f"{v.numerator}/{v.denominator}"


def tidy(text: str) -> str:
    """One space between words, whatever the f-string did with the line breaks."""
    return re.sub(r"\s+", " ", text).strip()


def _resolve_places(key: Q, vals: list[Q], style: str, places, cents) -> int | None:
    """How many decimals the four options print with.

    Three rules, all taken from the source set. A stem that pins the precision
    ("to the nearest tenth of a percent") passes `places` and every option
    obeys it. Money prints cents unless every option is a whole number of
    dollars. Otherwise each option prints at its own length -- ``36``,
    ``3.6``, ``1.36``, ``0.36`` -- unless that would leave the key as the only
    option with a decimal point, or the only one without, which is guessable
    without doing any arithmetic.
    """
    if places is not None:
        return places
    if style == "money":
        if cents:
            return 2
        return 0 if all(v.denominator == 1 for v in vals) else 2
    ds = [places_needed(v) for v in vals]
    kd = places_needed(key)
    others = [d for v, d in zip(vals, ds) if v != key]
    if others and all((d > 0) != (kd > 0) for d in others):
        return max(ds)                    # the key would be the only one of its look
    return None                           # each option at its own length


def _options(key: Q, mistakes, rng: random.Random, style: str, places, cents,
             signed: bool, fillers: str):
    """Assemble four options, then print them in one consistent surface form."""
    # a distractor is a number a student writes down, so it is rounded to the
    # cent or the hundredth before it is offered; the key is never rounded
    # here, because an item that needs rounding says so and passes `places`
    ms = [Mis(reason, Num(snap(value, Q(1, 100)), style)) for reason, value in mistakes
          if value is not None and (signed or q(value) > 0)]
    choices, _, reasons, letter = assemble(Num(key, style), ms, rng,
                                           signed=signed, fillers=fillers)
    vals = [_parse(c) for c in choices]
    p = _resolve_places(q(key), vals, style, places, cents)
    shown = [Num(v, style, p).plain() for v in vals]
    if len(set(shown)) != 4:
        raise ItemError("two options print as the same number once rounded")
    return shown, reasons, letter, Num(key, style, p)


def mcq(template: str, skill: str, difficulty: str, seed: int, stem: str, key,
        mistakes, rng: random.Random, rationale: str, *, style: str = "plain",
        places=None, cents=None, signed: bool = False, fillers: str = "scale",
        params=None, table=None, figure=None) -> Item:
    if places is None and places_needed(key, 6) > 2:
        raise ItemError("this key needs more decimals than an option prints; "
                        "round it in the template and say so in the stem")
    choices, reasons, letter, keyval = _options(
        q(key), mistakes, rng, style, places, cents, signed, fillers)
    return Item(template, skill, difficulty, seed, tidy(stem), "mcq", keyval, letter,
                tidy(rationale), choices, reasons, list(choices),
                figure=figure, table=table, params=params or {})


def spr(template: str, skill: str, difficulty: str, seed: int, stem: str, key,
        rationale: str, *, params=None, table=None, figure=None) -> Item:
    key = q(key)
    if key < 0:
        raise ItemError("a grid-in answer cannot be negative here")
    return Item(template, skill, difficulty, seed, tidy(stem), "spr", Num(key), grid(key),
                tidy(rationale), figure=figure, table=table, params=params or {})


def text_mcq(template: str, skill: str, difficulty: str, seed: int, stem: str,
             key: str, wrong, rng: random.Random, rationale: str, *,
             params=None, table=None, figure=None) -> Item:
    """Options that are expressions or sentences, so there is no order to sort by."""
    choices, reasons, letter = assemble_text(
        key, [Mis(reason, value) for reason, value in wrong], rng)
    return Item(template, skill, difficulty, seed, tidy(stem), "mcq", Num(0), letter,
                tidy(rationale), choices, reasons, list(choices),
                figure=figure, table=table, params=params or {})
