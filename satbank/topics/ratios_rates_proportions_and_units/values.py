"""How a ratio, a rate and a converted measure are written down.

This topic answers in five surface forms and the difference is visible on the
page: a count (``40,260``), a decimal measure (``14.1``), a fraction
(``14/3``), money (``$551.25``) and a value carrying its unit (``25 meters
per second``). The shared ``Exact`` renders every rational as a fraction, so
``Num`` is an ``Exact`` that knows which of the five its item prints, and the
option text and ``key.plain()`` are then the same string all the way down.

Arithmetic is never done on a ``Num``. A template computes in exact
``Fraction`` and wraps once, at the end, when a value becomes an option.
Nothing here uses a float: a square root and a cube root are found by integer
bisection so that a rounded answer is rounded the same way twice.
"""

from __future__ import annotations

import random
import re
from fractions import Fraction as Q

from ...exact import Exact
from ...expr import fmt_money
from ...item import Item, ItemError, Mis, assemble, assemble_text

__all__ = ["Q", "q", "Num", "dec", "frac_text", "places_needed", "grid",
           "tidy", "snap", "sig", "root", "mcq", "spr", "text_mcq"]


def q(v) -> Q:
    """Anything numeric to an exact Fraction. A float arrives as its decimal."""
    if isinstance(v, Q):
        return v
    if isinstance(v, float):
        return Q(str(v))
    if isinstance(v, Exact):
        if not v.is_rational:
            raise ValueError(f"{v!r} is not rational")
        return v.coef
    return Q(v)


def snap(v, step) -> Q:
    """Round to the nearest multiple of `step`, halves upward.

    An item that says "closest to" or "to the nearest tenth" rounds, and it
    has to round the same way twice -- here and in the independent solver --
    or the audit reports a disagreement that is really a tie-break.
    """
    v, step = q(v), q(step)
    k = v / step
    n = k.numerator // k.denominator
    if 2 * (k - n) >= 1:
        n += 1
    return n * step


def sig(v, figures: int = 3, strict: bool = False) -> Q:
    """Round to `figures` significant figures: 7,685.6 -> 7,690, 206.3 -> 210.

    `strict` refuses a value sitting exactly on the half, where this rounder
    (half up) and the independent solver's (the language's own) would part
    company over a tie rather than over any mathematics.
    """
    v = q(v)
    if v == 0:
        return Q(0)
    a = abs(v)
    e = 0
    while a >= Q(10) ** (e + 1):
        e += 1
    while a < Q(10) ** e:
        e -= 1
    step = Q(10) ** (e - figures + 1)
    if strict:
        k = v / step
        if 2 * (k - k.numerator // k.denominator) == 1:
            raise ItemError("this value rounds off an exact half")
    return snap(v, step)


def _iroot(x: Q, n: int) -> int:
    """The integer part of the n-th root of a nonnegative rational."""
    if x < 0:
        raise ValueError("negative radicand")
    lo, hi = 0, 1
    while Q(hi ** n) <= x:
        hi *= 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if Q(mid ** n) <= x:
            lo = mid
        else:
            hi = mid
    return lo


def root(value, n: int = 2, places: int = 2) -> Q:
    """The n-th root of a positive rational, rounded to `places` decimals.

    Integer bisection only -- an edge length that the item asks for "to the
    nearest hundredth" is a rounded value, and rounding it through a float
    would make the two routes disagree in the last place.
    """
    v = q(value)
    if v <= 0:
        raise ItemError("a root of a nonpositive quantity")
    scale = 10 ** places
    target = v * scale ** n
    c = _iroot(target, n)
    if Q((2 * c + 1) ** n, 2 ** n) <= target:          # round half up
        c += 1
    return Q(c, scale)


def dec(v, places: int, group: bool = True) -> str:
    """An exact rational as a decimal string, rounded half up.

    ``dec(Q(171,10), 1)`` is ``'17.1'`` and ``dec(Q(40260), 0)`` is
    ``'40,260'`` -- the thousands separator the source items print.
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


def frac_text(v) -> str:
    """A rational the way the source prints a fraction option: 1/20, 6, 3/4."""
    v = q(v)
    if v.denominator == 1:
        return f"{v.numerator:,}"
    sign = "-" if v < 0 else ""
    return f"{sign}{abs(v.numerator)}/{v.denominator}"


def grid(v) -> str:
    """Student-produced-response form: the shortest exact entry, no separators."""
    v = q(v)
    if v.denominator == 1:
        return str(v.numerator)
    for p in range(1, 7):
        if (v * 10 ** p).denominator == 1:
            return dec(v, p, group=False)
    return f"{v.numerator}/{v.denominator}"


def tidy(text: str) -> str:
    """One space between words, whatever the f-string did with the line breaks."""
    return re.sub(r"\s+", " ", text).strip()


class Num(Exact):
    """An exact rational that prints the way its item prints it.

    ``style`` is ``plain`` (a count or a decimal), ``money``, or ``frac``;
    ``unit`` is the unit an option carries when the source item prints one
    ("25 meters per second") and is empty when the stem keeps the unit, which
    is what most of the source items do. Equality and hashing ignore the
    surface form, so a distractor that lands on the key is still recognised
    as a duplicate and dropped.
    """

    def __init__(self, value, style: str = "plain", places: int | None = None,
                 unit: str = ""):
        object.__setattr__(self, "coef", q(value))
        object.__setattr__(self, "pi_exp", Q(0))
        object.__setattr__(self, "rad", 1)
        object.__setattr__(self, "style", style)
        object.__setattr__(self, "places", places)
        object.__setattr__(self, "unit", unit)

    def __eq__(self, other):
        return (isinstance(other, Exact)
                and (self.coef, self.pi_exp, self.rad)
                == (other.coef, other.pi_exp, other.rad))

    def __hash__(self):
        return hash((self.coef, self.pi_exp, self.rad))

    @property
    def form(self) -> tuple:
        """What the option looks like at a glance.

        For an ``Exact`` that is read off the value -- a fraction looks unlike
        an integer. Here it cannot be: whether ``17,136`` prints as
        ``17,136.0`` beside ``285.6`` is decided at print time, by
        ``_resolve_places``, and not by the denominator the value happens to
        carry. So every ``Num`` reports the surface of a plain number, the
        printer keeps the four options in one form, and the gate's own
        structure check does the verifying, on the strings that are actually
        printed.
        """
        return (Q(0), False, False)

    def plain(self) -> str:
        if self.style == "frac":
            body = frac_text(self.coef)
        elif self.style == "money":
            # the shared money renderer: exact until the moment it prints
            body = fmt_money(self.coef,
                             2 if self.places is None else self.places)
        else:
            p = places_needed(self.coef, 3) if self.places is None else self.places
            body = dec(self.coef, p)
        return f"{body} {self.unit}" if self.unit else body

    def latex(self) -> str:
        return self.plain()

    def __repr__(self) -> str:
        return f"Num({self.plain()})"


_STRIP = re.compile(r"[$,]")


def _parse(text: str, unit: str) -> Q:
    """A rendered option back to its exact value."""
    if unit and text.endswith(" " + unit):
        text = text[:-(len(unit) + 1)]
    return Q(_STRIP.sub("", text))


def _resolve_places(key: Q, vals: list[Q], style: str, places, cents) -> int | None:
    """How many decimals the four options print with.

    Three rules, all taken from the source set. A stem that pins the precision
    ("to the nearest hundredth of a meter") passes `places` and every option
    obeys it. Money prints cents unless every option is a whole number of
    dollars. Otherwise each option prints at its own length -- ``17.5``,
    ``0.057``, ``24`` -- unless that would leave the key as the only option
    with a decimal point, or the only one without, which is how ``17,136.0``
    comes to be printed beside ``285.6``.
    """
    if places is not None:
        return places
    if style == "money":
        if cents:
            return 2
        return 0 if all(v.denominator == 1 for v in vals) else 2
    ds = [places_needed(v, 3) for v in vals]
    kd = places_needed(key, 3)
    others = [d for v, d in zip(vals, ds) if v != key]
    if others and all((d > 0) != (kd > 0) for d in others):
        return max(ds)
    return None


def _options(key: Q, mistakes, rng: random.Random, style: str, places, cents,
             unit: str, round_to):
    """Assemble four options, then print them in one consistent surface form."""
    ms = []
    for reason, value in mistakes:
        if value is None:
            continue
        v = q(value)
        if round_to is not None:
            v = snap(v, round_to)
        if v <= 0:
            # a wrong answer that rounds away to nothing is not an option a
            # student would ever pick; the next misconception takes its place
            continue
        ms.append(Mis(reason, Num(v, style, unit=unit)))
    choices, _, reasons, letter = assemble(Num(key, style, unit=unit), ms, rng)
    vals = [_parse(c, unit) for c in choices]
    if style == "frac":
        # the printer cannot rescue a fraction: if the key is the only option
        # written over a bar, it is guessable, so the draw goes back
        others = [v for v in vals if v != q(key)]
        if all((v.denominator != 1) != (q(key).denominator != 1) for v in others):
            raise ItemError("the key would be the only fraction among the options")
    p = None if style == "frac" else _resolve_places(q(key), vals, style, places, cents)
    shown = [Num(v, style, p, unit).plain() for v in vals]
    if len(set(shown)) != 4:
        raise ItemError("two options print as the same value once rounded")
    return shown, reasons, letter, Num(key, style, p, unit)


def mcq(template: str, skill: str, difficulty: str, seed: int, stem: str, key,
        mistakes, rng: random.Random, rationale: str, *, style: str = "plain",
        places=None, cents=None, unit: str = "", round_to=None, params=None,
        table=None, figure=None) -> Item:
    """Four numeric options, ascending, each wrong one named."""
    key = q(key)
    if style != "frac" and places is None and places_needed(key, 7) > 3:
        raise ItemError("this key needs more decimals than an option prints; "
                        "round it in the template and say so in the stem")
    if round_to is None and places is not None:
        # an item that pins its precision rounds its wrong answers there too:
        # 0.005 printed to the nearest tenth is 0.0, which is not an option
        round_to = Q(1, 10 ** places)
    choices, reasons, letter, keyval = _options(
        key, mistakes, rng, style, places, cents, unit, round_to)
    return Item(template, skill, difficulty, seed, tidy(stem), "mcq", keyval, letter,
                tidy(rationale), choices, reasons, list(choices),
                figure=figure, table=table, params=params or {})


def spr(template: str, skill: str, difficulty: str, seed: int, stem: str, key,
        rationale: str, *, params=None, table=None, figure=None) -> Item:
    """A grid-in: no options, so the answer is the entry the student types."""
    key = q(key)
    if key <= 0:
        raise ItemError("a grid-in answer here has to be a positive amount")
    entry = grid(key)
    if len(entry.replace("-", "")) > 6:
        raise ItemError(f"{entry} does not fit the grid")
    return Item(template, skill, difficulty, seed, tidy(stem), "spr", Num(key), entry,
                tidy(rationale), figure=figure, table=table, params=params or {})


def text_mcq(template: str, skill: str, difficulty: str, seed: int, stem: str,
             key: str, wrong, rng: random.Random, rationale: str, *,
             params=None, table=None, figure=None) -> Item:
    """Options that are expressions, ratios or sentences, so there is no
    ascending order to hide the key behind: its position is randomized."""
    choices, reasons, letter = assemble_text(
        key, [Mis(reason, value) for reason, value in wrong], rng)
    return Item(template, skill, difficulty, seed, tidy(stem), "mcq", Num(0), letter,
                tidy(rationale), choices, reasons, list(choices),
                figure=figure, table=table, params=params or {})
