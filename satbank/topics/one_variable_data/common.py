"""Shared machinery for One-Variable Data.

Everything here is exact. A mean of 82/3 stays 82/3 until it is printed, and a
median of 7.5 is a Fraction, not a float, so an option can never drift by a
rounding error the student cannot see.

The one piece of real machinery is `assemble_num`. Options in this topic are
plain numbers, and a plain number betrays its own answer: if the key is the
only option with a decimal point, a student who cannot find a median can still
find the answer. So the options are built twice -- once to learn which values
were chosen, once to print them in a shape that gives nothing away.
"""

from __future__ import annotations

import random
from fractions import Fraction as F

from ...exact import E, Exact
from ...item import ItemError, Mis, assemble

__all__ = ["q", "mean", "median", "mode", "spread", "midrange", "num_str", "clean",
           "assemble_num", "listing", "count_word", "plural", "round_to",
           "sentence_case", "ordinal"]


# ------------------------------------------------------------------ numbers

def q(x) -> F:
    """Anything numeric to an exact Fraction. A float comes in as its digits."""
    if isinstance(x, F):
        return x
    if isinstance(x, Exact):
        if not x.is_rational:
            raise ItemError("value is not a rational number")
        return x.coef
    if isinstance(x, int):
        return F(x)
    return F(str(x))


def mean(vals) -> F:
    vals = [q(v) for v in vals]
    if not vals:
        raise ItemError("the mean of no values")
    return sum(vals, F(0)) / len(vals)


def median(vals) -> F:
    s = sorted(q(v) for v in vals)
    n = len(s)
    if n == 0:
        raise ItemError("the median of no values")
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def mode(vals) -> F:
    """The single most common value. A tie is not a mode a question may ask for."""
    s = [q(v) for v in vals]
    counts: dict[F, int] = {}
    for v in s:
        counts[v] = counts.get(v, 0) + 1
    top = max(counts.values())
    winners = [v for v, c in counts.items() if c == top]
    if len(winners) != 1 or top == 1:
        raise ItemError("no single most common value")
    return winners[0]


def spread(vals) -> F:
    s = [q(v) for v in vals]
    return max(s) - min(s)


def midrange(vals) -> F:
    s = [q(v) for v in vals]
    return (max(s) + min(s)) / 2


def round_to(v, places: int = 0) -> F:
    """Round half up, the way a test paper rounds. Exact in, exact out."""
    v = q(v)
    scale = F(10) ** places
    x = v * scale
    n, d = x.numerator, x.denominator
    whole = (2 * n + d) // (2 * d) if n >= 0 else -((-2 * n + d) // (2 * d))
    return F(whole) / scale


def _group(n: int) -> str:
    return f"{n:,}"


def _terminates(d: int) -> bool:
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    return d == 1


def num_str(v, places: int | None = None) -> str:
    """A number the way an SAT option prints it: 30, 4.2, 3,025, 48.8, 1/3."""
    f = q(v)
    if places is not None:
        f = round_to(f, places)
        sign = "-" if f < 0 else ""
        f = abs(f)
        whole = f.numerator // f.denominator
        rest = f - whole
        if places == 0:
            return sign + _group(whole)
        digits = str((rest * F(10) ** places).numerator).rjust(places, "0")
        return f"{sign}{_group(whole)}.{digits}"
    if f.denominator == 1:
        return _group(f.numerator)
    if _terminates(f.denominator):
        sign = "-" if f < 0 else ""
        a = abs(f)
        whole = a.numerator // a.denominator
        rest = a - whole
        digits = ""
        while rest != 0:
            rest *= 10
            digits += str(rest.numerator // rest.denominator)
            rest -= rest.numerator // rest.denominator
        return f"{sign}{_group(whole)}.{digits}"
    return f"{f.numerator}/{f.denominator}"


def clean(v, places: int = 3):
    """An SAT answer is a whole number or a short decimal, never 211/11.

    Every numeric answer in the 49 source items is an integer or a decimal of
    one or two places. A draw that lands on a repeating fraction is not wrong,
    it is just not a question this test asks, so it is rejected.
    """
    f = q(v)
    if f.denominator == 1:
        return f
    if _terminates(f.denominator) and _decimals(f) <= places:
        return f
    if f.numerator == 1 and f.denominator <= 20:
        return f
    raise ItemError(f"{f} is not an answer this test would print")


def _decimals(v, places=None) -> int:
    s = num_str(v, places)
    return len(s.split(".")[1]) if "." in s else 0


# ------------------------------------------------------------------ options

def assemble_num(key, mistakes: list[Mis], rng: random.Random, *,
                 prefix: str = "", suffix: str = "", places: int | None = None,
                 fillers: str = "shift"):
    """Build four numeric options, then print them so the key does not stand out.

    `assemble` itself never consults the Random it is handed, so running it
    twice with the same arguments picks the same three distractors: the first
    pass is only there to find out which values won, so the printing can be
    decided once all four are known.
    """
    if places is not None:
        # an option printed to one decimal place must BE that number: an
        # option of 5.25 shown as "5.3" is a wrong answer that happens to be
        # keyed wrong too
        mistakes = [m for m in mistakes if m.value is None
                    or round_to(m.value.coef, places) == m.value.coef]
    picked: list[Exact] = []

    def probe(v):
        picked.append(v)
        return v.plain()

    assemble(key, mistakes, rng, fmt_value=probe)
    if places is None:
        dec = [_decimals(v.coef) for v in picked]
        key_dec = _decimals(q(key))
        # a lone decimal point among three whole numbers is a free answer
        if key_dec > 0 and sum(1 for d in dec if d > 0) == 1:
            places = max(dec)

    def show(v):
        return prefix + num_str(v.coef, places) + suffix

    choices, latex, reasons, letter = assemble(key, mistakes, rng, fmt_value=show)
    if len(set(choices)) != 4:
        raise ItemError(f"two options print the same: {choices}")
    shapes = [_surface(c) for c in choices]
    if shapes.count(shapes["ABCD".index(letter)]) == 1:
        raise ItemError(f"the key is the only option that reads like "
                        f"{choices['ABCD'.index(letter)]!r}")
    return choices, latex, reasons, letter


def _surface(opt: str) -> tuple:
    """What an option looks like at a glance -- a lone fraction among three
    whole numbers is an answer a student can pick without doing any work."""
    return ("/" in opt, "." in opt, opt.strip().startswith("-"))


# -------------------------------------------------------------------- prose

WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
         7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
         12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
         16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen",
         20: "twenty"}

ORDINALS = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
            6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth"}


def count_word(n: int) -> str:
    return WORDS.get(n, str(n))


def ordinal(n: int) -> str:
    if n in ORDINALS:
        return ORDINALS[n]
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }".replace(" ", "")


def plural(n: int, noun: str, many: str | None = None) -> str:
    return f"{n} {noun}" if n == 1 else f"{n} {many or noun + 's'}"


def listing(parts: list[str], joiner: str = "and") -> str:
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} {joiner} {parts[1]}"
    return ", ".join(parts[:-1]) + f", {joiner} {parts[-1]}"


def sentence_case(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def values_line(vals, places: int | None = None) -> str:
    return ", ".join(num_str(v, places) for v in vals)


def cap_first(s: str) -> str:
    """Capitalize the first letter only: 'trial B' -> 'Trial B', never 'Trial b'."""
    return s[0].upper() + s[1:] if s else s
