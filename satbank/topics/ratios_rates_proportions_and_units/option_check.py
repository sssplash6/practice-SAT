"""Read the four printed options back, and check only one of them is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct: nothing in the engine reads a wrong option as
mathematics. `assemble_text` takes four strings, shuffles them and records which
one is the key; `audit` re-derives the key; `structure` counts surface forms and
`prose` looks for placeholders. An item with two right answers passes every one
of them.

This topic is exposed three ways, and this script covers all three.

  * Seven templates print **expressions, ratios or sentences**, assembled by
    `assemble_text`, which de-duplicates on the *string*. `3x/4` and `0.75x` are
    two strings and one function; `5 to 8` and `10 to 16` are two strings and one
    ratio. Those options are parsed here and decided by evaluation.
  * Five templates **round**: "approximately", "closest to", "to the nearest
    tenth", "to the nearest whole number". An answer exists only while one
    printed option is nearer the true value than every other, and only while the
    true value is not sitting exactly on the half, where which neighbour is
    "nearest" is a convention the stem never states.
  * The rest print numbers, and the assertion is simply that exactly one of them
    is the value the stem describes.

Every check has the same shape: decide the property for all four options from
their printed text and the printed stem, demand exactly one hit, and demand it is
the keyed one. The readers share nothing with the renderer -- they parse the
strings a student would read, and the expression reader is a real parser, so an
option nobody anticipated is evaluated rather than pattern-matched. `generate` is
the only thing imported from the engine, and only to obtain the finished item.

    PYTHONPATH=. python3 satbank/topics/ratios_rates_proportions_and_units/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 2000 --template rr.simplify
    PYTHONPATH=. python3 .../option_check.py --selftest
    PYTHONPATH=. python3 .../option_check.py --sources

Exits non-zero on the first kind of defect it finds, and prints the item.
"""

from __future__ import annotations

import argparse
import re
import sys
from fractions import Fraction as Q

from satbank.item import ItemError
from satbank.registry import generate

MINUS = "−"


class Unreadable(Exception):
    """The printed text is not something this reader understands.

    Raised rather than swallowed: an option shape nobody taught this reader
    about is an unchecked option, which is the thing the script exists to stop.
    """


# --------------------------------------------------- printed text -> numbers

def num(text: str) -> Q:
    """A printed number: 8, −11, 2,604, 9/7, 3.15, $8,948.61, 12%."""
    t = (str(text).replace(MINUS, "-").replace(",", "").replace("$", "")
         .replace("%", "").strip())
    if not t:
        raise Unreadable(f"{text!r} carries no number")
    try:
        if "/" in t:
            a, b = t.split("/", 1)
            return Q(int(a), int(b))
        return Q(t)
    except (ValueError, ZeroDivisionError):
        raise Unreadable(f"{text!r} is not a number") from None


def ratio(text: str) -> Q:
    """`5 to 8` or `10 : 11` as the exact rational it names."""
    m = re.fullmatch(r"\s*([\d,./]+)\s*(?:to|:)\s*([\d,./]+)\s*", str(text))
    if m is None:
        raise Unreadable(f"{text!r} is not a ratio this reader knows")
    b = num(m.group(2))
    if b == 0:
        raise Unreadable(f"{text!r} has nothing on the right of it")
    return num(m.group(1)) / b


# ------------------------------------------------ printed text -> a function
#
# The option strings of this topic are ordinary arithmetic -- `8(9.07z)`,
# `6z + 19.78z`, `(29/27)w`, `w − 13`, `40n`, `t/186`, `2k` -- so the reader is a
# real parser rather than a list of shapes. Evaluating is the whole point: two
# options can be algebraically equal and look nothing alike, which is exactly
# what a string comparison in `assemble_text` cannot see.

_TOKEN = re.compile(r"\s*(?:(\d+\.\d+|\d+)|([a-zA-Z])|([()+\-*/]))")


def _tokens(text: str) -> list:
    t = str(text).replace(MINUS, "-").replace(",", "").replace("×", "*")
    out, i = [], 0
    while i < len(t):
        m = _TOKEN.match(t, i)
        if m is None:
            raise Unreadable(f"{text!r} at {t[i:]!r}")
        if m.group(1):
            out.append(("n", Q(m.group(1))))
        elif m.group(2):
            out.append(("v", m.group(2)))
        else:
            out.append((m.group(3), None))
        i = m.end()
    if not out:
        raise Unreadable(f"{text!r} is empty")
    return out


class _Parse:
    """Sum -> Product -> Unary -> Atom, with juxtaposition as multiplication."""

    def __init__(self, toks, var):
        self.t, self.i, self.var = toks, 0, var

    def peek(self):
        return self.t[self.i][0] if self.i < len(self.t) else None

    def take(self):
        tok = self.t[self.i]
        self.i += 1
        return tok

    def sum_(self, x):
        v = self.product(x)
        while self.peek() in ("+", "-"):
            op, _ = self.take()
            r = self.product(x)
            v = v + r if op == "+" else v - r
        return v

    def product(self, x):
        v = self.unary(x)
        while True:
            k = self.peek()
            if k in ("*", "/"):
                self.take()
                r = self.unary(x)
                if k == "/":
                    if r == 0:
                        raise ZeroDivisionError
                    v = v / r
                else:
                    v = v * r
            elif k in ("n", "v", "("):            # juxtaposition: 40n, 8(9.07z)
                v = v * self.unary(x)
            else:
                return v

    def unary(self, x):
        if self.peek() == "-":
            self.take()
            return -self.unary(x)
        return self.atom(x)

    def atom(self, x):
        if self.peek() is None:
            raise Unreadable("the expression stops in the middle")
        kind, val = self.take()
        if kind == "n":
            return val
        if kind == "v":
            if val != self.var:
                raise Unreadable(f"the expression names {val!r}, not {self.var!r}")
            return x
        if kind == "(":
            v = self.sum_(x)
            if self.peek() != ")":
                raise Unreadable("an unclosed bracket")
            self.take()
            return v
        raise Unreadable(f"an expression cannot start with {kind!r}")


def value_of(text: str, var: str, x: Q) -> Q:
    """The printed expression evaluated at `var = x`, exactly."""
    p = _Parse(_tokens(text), var)
    v = p.sum_(x)
    if p.i != len(p.t):
        raise Unreadable(f"{text!r} has {p.t[p.i:]!r} left over")
    return v


AT = (Q(1), Q(2), Q(3), Q(7, 2), Q(11))


def agrees(text: str, var: str, truth) -> bool:
    """Two functions that agree at five values are one function here.

    Several test values on purpose: `8(9.07z)` and `8z + 9.07z` agree at one
    particular z, and a one-point check is how a second right answer gets in.
    """
    for x in AT:
        try:
            if value_of(text, var, x) != truth(x):
                return False
        except (ZeroDivisionError, OverflowError):
            return False
    return True


def is_constant(text: str, var: str, want: Q) -> bool:
    """The printed expression is the constant `want`, whatever `var` is."""
    return agrees(text, var, lambda _x, w=want: w)


# ---------------------------------------------------------- the assertions

def keyed(item) -> int:
    return "ABCD".index(item.answer)


def verdict(item, hits, what: str) -> str:
    """Both halves. `hits.count(True) == 1` catches the second right answer;
    `hits[keyed]` catches the right answer attached to the wrong letter."""
    if hits.count(True) != 1:
        right = ", ".join(repr(c) for c, h in zip(item.choices, hits) if h)
        raise AssertionError(f"{hits.count(True)} of the four options are right"
                             + (f": {right}" if right else ""))
    if not hits[keyed(item)]:
        raise AssertionError(f"the right option is "
                             f"{item.choices[hits.index(True)]!r}, but the key is "
                             f"{item.choices[keyed(item)]!r}")
    return what


def equals(item, exact: Q, what: str) -> str:
    """Exactly one printed option is the value the stem's own numbers give."""
    hits = [num(c) == exact for c in item.choices]
    if not any(hits):
        raise AssertionError(f"the stem's own numbers give {float(exact)}, which is "
                             f"none of {item.choices}")
    return verdict(item, hits, what)


def closest(item, exact: Q, what: str) -> str:
    """Exactly one printed option is nearest the value the stem describes.

    Numeric options are distinct values -- `assemble` drops a duplicate -- so
    two of them cannot be equal. What it cannot drop is a *tie*: a stem that
    says "approximately" or "closest to" has two right answers the moment the
    true value sits exactly between two printed options.
    """
    vals = [num(c) for c in item.choices]
    gaps = [abs(v - exact) for v in vals]
    best = min(gaps)
    hits = [g == best for g in gaps]
    if hits.count(True) != 1:
        tied = [item.choices[i] for i, h in enumerate(hits) if h]
        raise AssertionError(f"{len(tied)} options are equally close to "
                             f"{float(exact)}: {tied}")
    return verdict(item, hits, what)


def unambiguous(exact: Q, step: Q, unit: str) -> None:
    """The stem's own rounding has to have an answer.

    "To the nearest whole number" and "closest to" name a value only while one
    multiple of `step` is nearer than any other. A value exactly on the half is
    answered by a convention the stem never states -- round-half-up says one
    thing and round-half-to-even the other -- so a student who was taught the
    other one does the mathematics correctly and is marked wrong.
    """
    k = exact / step
    if 2 * (k - k.numerator // k.denominator) == 1:
        raise AssertionError(
            f"the exact value is {float(exact)}, exactly halfway between two "
            f"{unit}: which one is nearest is a convention, not mathematics")


def rounded(item, exact: Q, step: Q, unit: str, what: str) -> str:
    """A rounded stem: no halfway value, and exactly one nearest option."""
    unambiguous(exact, step, unit)
    return closest(item, exact, what)


# --------------------------------------------------------- reading the stem

def only(pattern: str, text: str, flags=0):
    m = re.search(pattern, text, flags)
    if m is None:
        raise Unreadable(f"{text[:120]!r} does not read as {pattern!r}")
    return m


def maybe(pattern: str, text: str, flags=0):
    return re.search(pattern, text, flags)


# ================================================================== RATIOS

def check_partner(item) -> str:
    """One term of a ratio given, the other asked for.

    Which term is given moves about: `m = 18` names the first, `There are 140
    red cards` names the first by its own words, and `what is the value of m
    when k is 25` names the second. The reader matches the name rather than
    assuming the order.
    """
    m = only(r"ratio of (.+?) to (.+?) (?:is|can be estimated to be) ([\d,]+) to "
             r"([\d,]+)", item.stem)
    terms = {m.group(1): num(m.group(3)), m.group(2): num(m.group(4))}
    g = (maybe(r"what is the value of (\w+) when (\w+) is ([\d,]+)", item.stem)
         or maybe(r", and (\w+) = ([\d,]+)\.", item.stem)
         or only(r"There are ([\d,]+) (.+?) in the", item.stem))
    if len(g.groups()) == 3:                       # ... when k is 25
        given, value = g.group(2), num(g.group(3))
    elif g.re.pattern.startswith("There are"):     # There are 140 red cards
        given, value = g.group(2), num(g.group(1))
    else:                                          # ... and m = 18
        given, value = g.group(1), num(g.group(2))
    if given not in terms:
        raise Unreadable(f"{given!r} is not one of {list(terms)}")
    other = next(t for t in terms if t != given)
    if terms[given] == 0:
        raise AssertionError("a ratio with a zero term")
    return equals(item, value * terms[other] / terms[given],
                  "the partner of the given term")


def check_equivalent(item) -> str:
    """Two equivalent ratios, one term missing."""
    m = only(r"ratio ([\d,]+) to \w+ is equivalent to the ratio ([\d,]+) to "
             r"([\d,]+)", item.stem)
    first, c, d = num(m.group(1)), num(m.group(2)), num(m.group(3))
    return equals(item, first * d / c, "the missing term")


def check_table_constant(item) -> str:
    """A table at one constant ratio, and the missing entry."""
    if item.table is None:
        raise Unreadable("this template prints a table")
    m = only(r"ratio of (\w+) to (\w+) for each ordered pair .*? what is the value "
             r"of (\w+) \?", item.stem, re.S | re.I)
    head = item.table[0]
    if head[::-1] != [m.group(1), m.group(2)]:
        raise Unreadable(f"the table is headed {head}, and the stem asks for the "
                         f"ratio of {m.group(1)} to {m.group(2)}")
    unknown, rows = m.group(3), item.table[1:]
    full = [r for r in rows if r[1] != unknown]
    last = [r for r in rows if r[1] == unknown]
    if not full or len(last) != 1:
        raise Unreadable(f"the table does not have one row with {unknown} in it")
    const = {num(r[1]) / num(r[0]) for r in full}
    if len(const) != 1:
        raise AssertionError(f"the printed rows do not share one ratio: {const}")
    return equals(item, num(last[0][0]) * const.pop(), "the constant ratio applied")


def check_simplify(item) -> str:
    """Two counts, and the ratio between them.

    An option is right when it *is* that ratio. `10 to 16` and `5 to 8` are one
    ratio written two ways, so printing both is two right answers however
    firmly the stem intends lowest terms.
    """
    m = only(r"has ([\d,]+) (.+?) and ([\d,]+) (.+?)\. What is the ratio of "
             r"(.+?) to (.+?) that", item.stem)
    n1, n2 = num(m.group(1)), num(m.group(3))
    if m.group(5) != m.group(2) or m.group(6) != m.group(4):
        raise AssertionError(f"the stem counts {m.group(2)!r} then {m.group(4)!r} "
                             f"but asks for {m.group(5)!r} to {m.group(6)!r}")
    return verdict(item, [ratio(c) == n1 / n2 for c in item.choices],
                   "the ratio of the two counts")


def check_similar_rect(item) -> str:
    """Two rectangles at one ratio; the second width in terms of w."""
    m = only(r"length ([\d,]+) and width (\w+)\. Rectangle \w+ has length "
             r"([\d,]+)", item.stem)
    l1, var, l2 = num(m.group(1)), m.group(2), num(m.group(3))
    return verdict(item, [agrees(c, var, lambda w, r=l2 / l1: r * w)
                          for c in item.choices],
                   "the width that keeps the ratio")


SHIFT = re.compile(r"It must (increase|decrease) by ([\d,.]+) units?\.")


def check_dimension_shift(item) -> str:
    """One side changes; how the other must change, said in a sentence."""
    m = only(r"ratio of its length to its width is ([\d,]+) to ([\d,]+)\. If the "
             r"(length|width) of the rectangular region (increases|decreases) by "
             r"([\d,.]+) units?, how must the (length|width) change", item.stem)
    length, width = num(m.group(1)), num(m.group(2))
    moved, way, change, other = m.group(3), m.group(4), num(m.group(5)), m.group(6)
    if moved == other:
        raise AssertionError(f"the stem moves the {moved} and asks about the "
                             f"{other}")
    scale = (length / width) if moved == "width" else (width / length)
    want = "increase" if way == "increases" else "decrease"
    hits = []
    for c in item.choices:
        s = SHIFT.fullmatch(c.strip())
        if s is None:
            raise Unreadable(f"{c!r} is not a sentence this reader knows")
        hits.append(s.group(1) == want and num(s.group(2)) == scale * change)
    return verdict(item, hits, "the matching change, in size and direction")


def check_mix_statement(item) -> str:
    """A mixture made again at the same ratio, described rather than counted.

    Each sentence is turned into the amount of the second ingredient it names,
    and compared with the amount the ratio actually calls for. A distractor
    that happens to be a true description of the mixture is the defect here.
    """
    m = only(r"by mixing ([\d,.]+) (\w+) of (.+?) with ([\d,.]+) \2 of (.+?)\. "
             r"(?:She|He) must mix a second batch .*? uses ([\d,.]+) \2 of \3 "
             r"for the second batch, how much \5 should", item.stem, re.S)
    first, unit, one = num(m.group(1)), m.group(2), m.group(3)
    second, two, again = num(m.group(4)), m.group(5), num(m.group(6))
    if first == 0:
        raise AssertionError("the first batch has none of the first ingredient")
    truth = again * second / first
    have = {(one, "first"): first, (two, "first"): second, (one, "second"): again}

    def amount(option: str):
        s = option.rstrip(".").strip()
        t = maybe(r"^([\d,.]+) times the amount of (.+?) used in the "
                  r"(first|second) batch$", s)
        if t:
            got = have.get((t.group(2), t.group(3)))
            if got is None:
                raise Unreadable(f"{option!r} names an amount the stem never gives")
            return num(t.group(1)) * got
        t = maybe(rf"^Exactly ([\d,.]+) {re.escape(unit)}$", s)
        if t:
            return num(t.group(1))
        t = maybe(rf"^([\d,.]+) {re.escape(unit)} (more|less) than the amount of "
                  rf"(.+?) used in the (first|second) batch$", s)
        if t:
            got = have.get((t.group(3), t.group(4)))
            if got is None:
                raise Unreadable(f"{option!r} names an amount the stem never gives")
            return got + (num(t.group(1)) if t.group(2) == "more" else -num(t.group(1)))
        raise Unreadable(f"{option!r} is not a description this reader can decide")

    return verdict(item, [amount(c) == truth for c in item.choices],
                   "the one description that keeps the ratio")


def check_expression(item) -> str:
    """The same proportional step, written as an expression rather than worked
    out. Four frames, each reduced to one variable and one true function."""
    m = maybe(r"earns \$([\d,.]+) per hour .*? works (\w+) hours, (?:she|he) earns "
              r"[\d,.]+\2 dollars\..*?works (\d+)\2 hours", item.stem, re.S)
    if m:
        rate, var, n = num(m.group(1)), m.group(2), num(m.group(3))
        truth, what = (lambda z: n * rate * z), "the pay for n times the hours"
    else:
        m = maybe(r"earns (\w+) dollars for every (\w+) hours of work\..*?earns for "
                  r"(\d+)\2 hours", item.stem, re.S)
        if m:
            var, n = m.group(1), num(m.group(3))
            truth, what = (lambda p: n * p), "the pay for n times the hours"
        else:
            m = maybe(r"total mass, in \w+, of (\w+) identical (.+?) is (\w+)\..*?"
                      r"total mass, in \w+, of (\d+)\1 of these \2", item.stem, re.S)
            if m:
                var, n = m.group(3), num(m.group(4))
                truth, what = (lambda t: n * t), "the mass of n times the count"
            else:
                m = only(r"If (\w+) = (\d+)(\w+), which of the following is "
                         r"equivalent to (\d+)\1\?", item.stem)
                var, inner, outer = m.group(3), num(m.group(2)), num(m.group(4))
                truth = lambda y, k=outer * inner: k * y            # noqa: E731
                what = "the substitution carried through"
    return verdict(item, [agrees(c, var, truth) for c in item.choices], what)


def check_multiple(item) -> str:
    """A proportional model read at two multiples of the same constant.

    The ratio of the two distances is `big/small` for every k, so an option
    that still carries the k cannot be it -- which is decided by evaluating the
    option at two different k, not by looking for the letter.
    """
    m = only(r"For any positive constant (\w+), the distance the car would have "
             r"traveled after ([\d,]+)\1 hours is how many times the distance the "
             r"car would have traveled after ([\d,]+)\1 hours", item.stem)
    var, big, small = m.group(1), num(m.group(2)), num(m.group(3))
    if small == 0:
        raise AssertionError("the second period is no time at all")
    return verdict(item, [is_constant(c, var, big / small) for c in item.choices],
                   "how many times, free of k")


def check_chain_unknown(item) -> str:
    """Two stated values of one ratio, and the constant between them."""
    m = only(r"If ([\d,.]+)(\w)/(\w) = ([\d,.]+) and \2/\(\3(\w)\) = ([\d,.]+), "
             r"what is the value of \5\?", item.stem)
    c, first, second = num(m.group(1)), num(m.group(4)), num(m.group(6))
    if c == 0 or second == 0:
        raise AssertionError("a zero in the stem")
    return equals(item, (first / c) / second, "the constant between the two ratios")


WORDS = {"doubled": 2, "tripled": 3, "quadrupled": 4}


def check_repeated_factor(item) -> str:
    """A quantity multiplied by one factor year on year, run backwards."""
    m = only(r"on January 1, (\d{4})\. The amount of money in the account "
             r"(doubled|tripled|quadrupled|was multiplied by \d+) each year until "
             r".*? had ([\d,]+) dollars .*? on January 1, (\d{4})\.", item.stem, re.S)
    y1, y2, total = int(m.group(1)), int(m.group(4)), num(m.group(3))
    word = m.group(2)
    factor = Q(WORDS.get(word) or int(word.rsplit(" ", 1)[1]))
    if y2 <= y1:
        raise AssertionError("the account ends before it starts")
    return equals(item, total / factor ** (y2 - y1), "the deposit run backwards")


# =================================================================== RATES

def check_unit_rate(item) -> str:
    """A rate used once, in whichever direction the stem asks for."""
    s = item.stem
    m = maybe(r"costs ([\d,.]+) dollars per (\w+)\. What is the cost, in dollars, "
              r"for ([\d,.]+) \2s? of the product", s)
    if m:
        return equals(item, num(m.group(1)) * num(m.group(3)), "the rate times the count")
    m = maybe(r"in a ([\d,]+)-square-foot room\. If there should be at least "
              r"([\d,.]+) square feet per person, what is the maximum number of "
              r"people", s)
    if m:
        return equals(item, num(m.group(1)) / num(m.group(2)), "the total over the rate")
    m = maybe(r"constant speed of ([\d,.]+) (\w+) per (\w+)\. At this speed, what "
              r"is the time, in \3s, that it would take .*? to travel ([\d,.]+) \2",
              s, re.S)
    if m:
        return equals(item, num(m.group(4)) / num(m.group(1)), "the distance over the speed")
    m = maybe(r"flying a total of ([\d,.]+) miles\. It took .*? ([\d,.]+) days to "
              r"travel this route one way\. On average, how many miles", s, re.S)
    if m:
        return equals(item, num(m.group(1)) / num(m.group(2)), "miles a day")
    m = maybe(r"spent \$([\d,.]+) to purchase .+? at \$([\d,.]+) per (\w+)\. How "
              r"many \3s", s)
    if m:
        return equals(item, num(m.group(1)) / num(m.group(2)), "the spend over the price")
    m = maybe(r"maximum volume of ([\d,.]+) cubic centimeters, which is "
              r"approximately ([\d,.]+) fluid ounces\. .*? pitcher that contains "
              r"([\d,.]+) fluid ounces .*? How many times", s, re.S)
    if m:
        return equals(item, num(m.group(3)) / num(m.group(2)), "pitcher over glass")
    m = maybe(r"completes ([\d,.]+) (\w+) in ([\d,.]+) minutes\. At this rate, how "
              r"many \2 per minute", s)
    if m:
        return equals(item, num(m.group(1)) / num(m.group(3)), "the count over the time")
    raise Unreadable(item.stem)


SECONDS = {"second": Q(1), "minute": Q(60), "hour": Q(3600)}


def check_rate_convert(item) -> str:
    """The same speed, timed in another unit -- and, in the trip frame, rounded."""
    m = maybe(r"traveled ([\d,.]+) miles in ([\d,.]+) minutes\..*?to the nearest "
              r"tenth of a mile per hour", item.stem, re.S)
    if m:
        exact = num(m.group(1)) / num(m.group(2)) * 60
        return rounded(item, exact, Q(1, 10), "tenths of a mile per hour",
                       "the nearest tenth of a mile per hour")
    m = maybe(r"average speed of ([\d,.]+) (.+?) per (second|minute|hour)\. What "
              r"is .*? average speed in (.+?) per (second|minute|hour)\?",
              item.stem, re.S)
    if m:
        value, per_from, per_to = num(m.group(1)), m.group(3), m.group(5)
        if m.group(2) != m.group(4):
            raise Unreadable(f"{m.group(2)!r} became {m.group(4)!r} with no factor")
        return equals(item, value * SECONDS[per_to] / SECONDS[per_from],
                      "the rate per the other unit of time")
    # "Which of the following speeds is equivalent to 90 kilometers per hour
    # (1 kilometer = 1,000 meters)?" -- the destination unit is printed on the
    # options, not in the stem, so it is read off them
    m = only(r"equivalent to ([\d,./]+) (\w+) per (second|minute|hour) \(1 (\w+) = "
             r"([\d,.]+) (\w+)\)", item.stem)
    value, per_from = num(m.group(1)), m.group(3)
    factor, to_u = num(m.group(5)), m.group(6)
    tails = set()
    heads = []
    for c in item.choices:
        t = only(r"^([\d,./]+) (.+? per (?:second|minute|hour))$", c.strip())
        heads.append(num(t.group(1)))
        tails.add(t.group(2))
    if len(tails) != 1:
        raise AssertionError(f"the four options are not in one unit: {tails}")
    said = tails.pop()
    unit, per_to = said.rsplit(" per ", 1)
    if not _names(to_u, unit):
        raise AssertionError(f"the stem converts to {to_u!r} and the options say "
                             f"{unit!r}")
    exact = value * factor * SECONDS[per_to] / SECONDS[per_from]
    return verdict(item, [h == exact for h in heads],
                   "the rate converted in both units")


def check_rate_product(item) -> str:
    """One rate multiplied by a second, so a unit cancels between them."""
    m = maybe(r"density of ([\d,.]+) ounce per cubic inch\. .*? price of "
              r"\$([\d,.]+) per ounce\. What is the selling price", item.stem, re.S)
    if m:
        return equals(item, num(m.group(1)) * num(m.group(2)),
                      "the two rates multiplied")
    m = maybe(r"needs ([\d,.]+) ounces of .+? for each \w+\. How many pounds .*? "
              r"to make ([\d,]+) signature .*?\(1 pound = 16 ounces\)", item.stem, re.S)
    if m:
        return equals(item, num(m.group(1)) * num(m.group(2)) / 16,
                      "the ounces, brought back to pounds")
    m = only(r"projects in one state was ([\d,]+) megawatts .*? operated "
             r"continuously for ([\d,]+) hours .*? approximately how many "
             r"megawatt-hours", item.stem, re.S)
    exact = num(m.group(1)) * num(m.group(2))
    # "approximately" against options printed to two significant figures
    step = Q(10) ** (len(str(int(exact))) - 2)
    return rounded(item, exact, step, f"multiples of {step}",
                   "approximately, to two figures")


def check_gap(item) -> str:
    """Two rates over one base, and the amount that lies between them."""
    m = maybe(r"on (\w+) is approximately ([\d/]+) of its weight on Earth\. .*? on "
              r"(\w+) is approximately ([\d/]+) of its weight on Earth\. If an "
              r"object weighs ([\d,]+) pounds on Earth, approximately how many more "
              r"pounds does it weigh on (\w+) than it weighs on (\w+)",
              item.stem, re.S)
    if m:
        near, low, far, high = m.group(1), num(m.group(2)), m.group(3), num(m.group(4))
        base = num(m.group(5))
        if (m.group(6), m.group(7)) != (far, near):
            raise AssertionError(f"the stem compares {m.group(6)} with {m.group(7)} "
                                 f"but gave the fractions for {near} and {far}")
        return equals(item, base * (high - low), "the base times the difference")
    m = maybe(r"orbits the planet every ([\d,]+) days\. A second moon orbits the "
              r"planet every ([\d,]+) days\. How many more days .*? orbit the "
              r"planet ([\d,]+) times than .*? ([\d,]+) times", item.stem, re.S)
    if m:
        low, high, base = num(m.group(1)), num(m.group(2)), num(m.group(3))
        if num(m.group(4)) != base:
            raise AssertionError("the two moons are counted over different orbits")
        return equals(item, base * (high - low), "the base times the difference")
    m = only(r"increased from ([\d,.]+) in \d{4} to ([\d,.]+) in \d{4}\. .*? land "
             r"area of \w+ was ([\d,]+) square kilometers\. By how many people",
             item.stem, re.S)
    low, high, base = num(m.group(1)), num(m.group(2)), num(m.group(3))
    return equals(item, base * (high - low), "the area times the density change")


def growth_exact(item) -> Q:
    """How far apart the two named trees are, in inches, read off the page.

    The diameters start equal, so the starting size cancels out of the
    difference and only the two growth factors and the years matter.
    """
    if item.table is None:
        raise Unreadable("this template prints a table")
    factors = {r[0].lower(): num(r[1]) for r in item.table[1:]}
    m = only(r"If an? ([a-z ]+?) tree and an? ([a-z ]+?) tree each now have a "
             r"diameter of ([\d,]+) (?:foot|feet), which of the following will be "
             r"closest to the difference, in inches, of their diameters ([\d,]+) "
             r"years from now", item.stem, re.S)
    for name in (m.group(1), m.group(2)):
        if name not in factors:
            raise Unreadable(f"{name!r} is not a row of the printed table")
    gf, gs = factors[m.group(1)], factors[m.group(2)]
    if gf == 0 or gs == 0:
        raise AssertionError("a growth factor of zero")
    years = num(m.group(4))
    return abs(years / gf - years / gs)


def check_growth_table(item) -> str:
    """A table of growth factors, and how far apart two trees end up.

    The stem says "closest to", so the reading has to be nearer one printed
    option than every other -- and the true difference must not sit exactly
    between two tenths of an inch, where "closest" stops being mathematics.
    """
    return rounded(item, growth_exact(item), Q(1, 10), "tenths of an inch",
                   "the closest tenth of an inch")


def check_table_unit_price(item) -> str:
    """Two foods in a table, and the ratio of what a gram of each costs."""
    if item.table is None:
        raise Unreadable("this template prints a table")
    (first, a1, c1), (second, a2, c2) = [(r[0], num(r[1].split()[0]), num(r[2]))
                                         for r in item.table[1:]]
    m = only(r"ratio of the cost per \w+ of \w+ in (.+?) to the cost per \w+ of "
             r"\w+ in (.+?)\?", item.stem)
    for row, asked in ((first, m.group(1)), (second, m.group(2))):
        if row.split(" ", 1)[1] not in asked:
            raise AssertionError(f"the stem asks about {asked!r}, and the table "
                                 f"row is {row!r}")
    if a1 == 0 or a2 == 0 or c2 == 0:
        raise AssertionError("a zero in the table")
    want = (c1 / a1) / (c2 / a2)
    return verdict(item, [ratio(c) == want for c in item.choices],
                   "the ratio of the two unit prices")


def check_exchange_fee(item) -> str:
    """A currency converted at a stated rate, less a percent fee on the result.

    Money prints to the cent, so the assertion is two-sided: the payout has to
    *be* a whole number of cents, or the printed key is a rounding the stem
    never asks for, and exactly one option has to carry it.
    """
    m = only(r"has ([\d,]+) (.+?) (?:she|he) will convert .*? 1 (.+?) = ([\d,.]+) "
             r"US dollars\. .*? a ([\d,.]+)% fee on the converted US dollar amount",
             item.stem, re.S)
    amount, rate, fee = num(m.group(1)), num(m.group(4)), num(m.group(5))
    exact = amount * rate * (1 - fee / 100)
    if (exact * 100).denominator != 1:
        raise AssertionError(f"the payout is {float(exact)} dollars, which is not a "
                             f"whole number of cents, so the printed answer is a "
                             f"rounding the stem never asks for")
    return equals(item, exact, "the conversion, less the fee")


# =================================================================== UNITS

# a unit as the page writes it: `yards`, `fluid ounces`, `square kilometers`
UNIT = r"(?:square )?(?:fluid )?[a-z]+"


def _factor(stem: str):
    """The conversion the stem states in brackets, as (big unit, factor, small)."""
    m = maybe(r"\(1 (.+?) = ([\d,]+) (.+?)\)", stem)
    if m:
        return m.group(1), num(m.group(2)), m.group(3)
    m = only(r"\(([\d,]+) (.+?) = 1 (.+?)\)", stem)
    return m.group(3), num(m.group(1)), m.group(2)


IRREGULAR = {"feet": "foot", "people": "person", "pence": "penny"}


def _singular(u: str) -> str:
    """`yards` -> `yard`, `inches` -> `inch`, `feet` -> `foot`."""
    if u in IRREGULAR:
        return IRREGULAR[u]
    if u.endswith("ches") or u.endswith("shes"):
        return u[:-2]
    return u[:-1] if u.endswith("s") else u


def _bare(u: str) -> str:
    return _singular(u.replace("square ", "").strip())


def _names(unit: str, word: str) -> bool:
    """Does `word`, as the stem writes a unit, name the same unit as `unit`?

    The page writes one unit four ways -- `yard`, `yards`, `square yard`,
    `square yards` -- and the reader has to see through all four without a
    table of units, which would be a second place for a unit to be wrong.
    """
    return _bare(unit) == _bare(word)


def check_convert(item) -> str:
    """One stated conversion factor, applied the way the stem asks for."""
    big, factor, small = _factor(item.stem)
    power = 2 if "square" in item.stem else 1
    m = maybe(r"How many (.+?) are equivalent to ([\d,./]+) (.+?) \(", item.stem)
    if m:
        to_u, n = m.group(1), num(m.group(2))
    else:
        m = maybe(r"(?:length|mass|area|speed) of ([\d,./]+) (.+?)\. What is (?:the|"
                  r"this) .*?, in (" + UNIT + r")", item.stem, re.S)
        if m is None:
            m = only(r"average speed of ([\d,./]+) (.+?) per (\w+)\. What is this "
                     r"speed, in (" + UNIT + r") per", item.stem)
            to_u, n = m.group(4), num(m.group(1))
        else:
            to_u, n = m.group(3), num(m.group(1))
    if _names(small, to_u):
        exact = n * factor ** power
    elif _names(big, to_u):
        exact = n / factor ** power
    else:
        raise Unreadable(f"{to_u!r} is neither {big!r} nor {small!r}")
    return equals(item, exact, f"the factor applied {power} time(s)")


def check_convert_chain(item) -> str:
    """Two stated factors, one after the other."""
    m = maybe(r"\(1 (.+?) = ([\d,]+) (.+?) and 1 (.+?) = ([\d,]+) (.+?)\)", item.stem)
    if m:
        a, f1, b, b2, f2, c = (m.group(1), num(m.group(2)), m.group(3),
                               m.group(4), num(m.group(5)), m.group(6))
    else:
        m = only(r"\(([\d,]+) (.+?) = 1 (.+?) and ([\d,]+) (.+?) = 1 (.+?)\)",
                 item.stem)
        c, f2, b2 = m.group(2), num(m.group(1)), m.group(3)
        b, f1, a = m.group(5), num(m.group(4)), m.group(6)
    if not _names(b, b2):
        raise AssertionError(f"the chain runs through {b!r} and then {b2!r}")
    g = maybe(r"How many (.+?) are equivalent to ([\d,.]+) (.+?) \(", item.stem) or \
        only(r"A distance of ([\d,.]+) (.+?) is equivalent to how many (.+?) \(",
             item.stem)
    if g.re.pattern.startswith("How many"):
        to_u, n, from_u = g.group(1), num(g.group(2)), g.group(3)
    else:
        n, from_u, to_u = num(g.group(1)), g.group(2), g.group(3)
    if not _names(a, from_u) or not _names(c, to_u):
        raise AssertionError(f"the chain is {a!r} -> {c!r} but the question asks "
                             f"{from_u!r} -> {to_u!r}")
    return equals(item, n * f1 * f2, "both factors applied in turn")


def check_pop_density(item) -> str:
    """People per square mile, and the area or the population it implies."""
    m = maybe(r"total area of .+? is ([\d,.]+) square miles, of which ([\d,.]+) "
              r"square miles is water\. .*? population of ([\d,]+) people .*? "
              r"closest to the population density, in people per square mile of "
              r"land area", item.stem, re.S)
    if m:
        land = num(m.group(1)) - num(m.group(2))
        if land <= 0:
            raise AssertionError("the city is all water")
        # the options are printed to three figures, so "closest to" is decided
        # against the step those figures move in
        exact = num(m.group(3)) / land
        step = Q(10) ** (len(str(int(exact))) - 3)
        return rounded(item, exact, step, f"multiples of {step}",
                       "the closest of the four, to three figures")
    m = only(r"population density of (.+?) is ([\d,.]+) people per square mile",
             item.stem)
    density = num(m.group(2))
    g = maybe(r"population of ([\d,]+) people\. What is the area, in square miles",
              item.stem)
    if g:
        if density == 0:
            raise AssertionError("a density of nobody")
        return equals(item, num(g.group(1)) / density, "the population over the density")
    g = only(r"area of ([\d,.]+) square miles\. .*?what is the population",
             item.stem, re.S)
    return equals(item, num(g.group(1)) * density, "the area times the density")


def _cbrt_near(v: Q, step: Q) -> Q:
    """The multiple of `step` nearest the cube root of `v`, by integer search.

    No float anywhere: a rounded edge length has to round the same way twice.
    Returns the exact cube root when there is one.
    """
    lo, hi = 0, 1
    scale = 1 / step
    if scale.denominator != 1:
        raise Unreadable("the rounding step is not a unit fraction")
    target = v * scale ** 3
    while Q(hi) ** 3 <= target:
        hi *= 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if Q(mid) ** 3 <= target:
            lo = mid
        else:
            hi = mid
    return Q(lo) * step, Q(lo + 1) * step, target


def check_cube_density(item) -> str:
    """Mass, density and the edge of a cube: any one from the other two."""
    m = maybe(r"density of .+? is ([\d,.]+) (kilograms|grams) per cubic (\w+)\..*?"
              r"each edge has a length of ([\d,.]+) \3s\. To the nearest whole "
              r"number, what is the mass", item.stem, re.S)
    if m:
        density, edge = num(m.group(1)), num(m.group(4))
        return rounded(item, density * edge ** 3, Q(1), "whole kilograms",
                       "the nearest whole number of kilograms")
    m = maybe(r"edge of one of these cubes is ([\d,.]+) centimeters\. This cube has "
              r"a density of ([\d,.]+) grams per cubic centimeter\. What is the "
              r"mass", item.stem, re.S)
    if m:
        return equals(item, num(m.group(2)) * num(m.group(1)) ** 3,
                      "the density times the volume")
    m = maybe(r"edge of one of these cubes is ([\d,.]+) centimeters\. If this cube "
              r"has a mass of ([\d,.]+) grams, what is the density", item.stem, re.S)
    if m:
        edge = num(m.group(1))
        if edge == 0:
            raise AssertionError("a cube with no edge")
        return equals(item, num(m.group(2)) / edge ** 3, "the mass over the volume")
    m = only(r"density of .+? is ([\d,.]+) (?:kilograms|grams) per cubic (\w+)\..*?"
             r"mass of ([\d,.]+) (?:kilograms|grams)\. To the nearest hundredth of "
             r"a \2, what is the length of one edge", item.stem, re.S)
    density, mass = num(m.group(1)), num(m.group(3))
    if density == 0:
        raise AssertionError("a density of nothing")
    lo, hi, target = _cbrt_near(mass / density, Q(1, 100))
    if lo ** 3 == mass / density:
        return equals(item, lo, "the exact cube root")
    # the cube root is irrational here, so it cannot sit exactly on a half-
    # hundredth; the nearest hundredth is whichever neighbour the cube is nearer
    # to, compared as exact integers rather than through a float
    exact = lo if target - (lo * 100) ** 3 < (hi * 100) ** 3 - target else hi
    return closest(item, exact, "the nearest hundredth of a meter")


CHECKS = {
    "rr.partner": check_partner,
    "rr.equivalent": check_equivalent,
    "rr.table_constant": check_table_constant,
    "rr.simplify": check_simplify,
    "rr.similar_rect": check_similar_rect,
    "rr.dimension_shift": check_dimension_shift,
    "rr.mix_statement": check_mix_statement,
    "rr.expression": check_expression,
    "rr.multiple": check_multiple,
    "rr.chain_unknown": check_chain_unknown,
    "rr.repeated_factor": check_repeated_factor,
    "rr.unit_rate": check_unit_rate,
    "rr.rate_convert": check_rate_convert,
    "rr.rate_product": check_rate_product,
    "rr.gap": check_gap,
    "rr.growth_table": check_growth_table,
    "rr.table_unit_price": check_table_unit_price,
    "rr.exchange_fee": check_exchange_fee,
    "rr.convert": check_convert,
    "rr.convert_chain": check_convert_chain,
    "rr.pop_density": check_pop_density,
    "rr.cube_density": check_cube_density,
}


# ------------------------------------------------- proving the check bites

def _draw(name: str, want=lambda it: True):
    for seed in range(600):
        try:
            item = generate(name, seed)
        except ItemError:
            continue
        if item.fmt == "mcq" and want(item):
            return item
    raise RuntimeError(f"no {name} draw to injure")


def _hurt(item, slot: int, text: str):
    """Put `text` in the slot `slot` places along from the key."""
    item.choices = list(item.choices)
    item.choices[(keyed(item) + slot) % 4] = text
    return item


def _growth_tie():
    """A `rr.growth_table` item rebuilt around a halfway difference.

    The defect as it was found: 21 years of a 3.5 tree and a 4.0 tree separate
    by exactly 0.75 inches, and the pool prints both 0.7 and 0.8. The guard in
    `growth_table` now refuses that draw, so the selftest has to put it back --
    the stem's two species and its number of years are rewritten inside a real
    table, and the two straddling tenths are printed as options.
    """
    for seed in range(600):
        try:
            item = generate("rr.growth_table", seed)
        except ItemError:
            continue
        if item.fmt != "mcq":
            continue
        rows = {r[0]: num(r[1]) for r in item.table[1:]}
        for a in rows:
            for b in rows:
                if rows[a] >= rows[b]:
                    continue
                for years in range(4, 26):
                    gap = years * (1 / rows[a] - 1 / rows[b])
                    if (gap * 10).denominator != 2:       # not on a half-tenth
                        continue
                    lo = (gap * 10 - Q(1, 2)) / 10
                    item.stem = re.sub(
                        r"If an? [a-z ]+? tree and an? [a-z ]+? tree",
                        f"If {_an(a)} tree and {_an(b)} tree", item.stem)
                    item.stem = re.sub(r"diameters \d+ years from now",
                                       f"diameters {years} years from now", item.stem)
                    item.choices = list(item.choices)
                    item.choices[keyed(item)] = f"{float(lo + Q(1, 10)):.1f}"
                    item.choices[(keyed(item) + 1) % 4] = f"{float(lo):.1f}"
                    return item
    raise RuntimeError("no growth table to injure")


def _an(name: str) -> str:
    return ("an " if name[0].lower() in "aeiou" else "a ") + name.lower()


def selftest() -> int:
    """Seven faults, injected on purpose, one for each way an option set of
    this topic can be wrong. A check nobody has seen fail is worth nothing."""
    cases = []

    # 1. a second correct expression: the key again, algebraically equal and
    #    printed differently -- 3x/4 against 0.75x, the shape this topic risks
    item = _draw("rr.expression",
                 lambda it: re.match(r"^\d+([a-z])$", it.choices[keyed(it)]))
    key = item.choices[keyed(item)]
    n, v = re.match(r"^(\d+)([a-z])$", key).groups()
    cases.append(("the key again, written as a quotient",
                  _hurt(item, 1, f"{int(n) * 4}{v}/4"), CHECKS["rr.expression"]))

    # 2. a second correct ratio: the key not reduced, which is what the
    #    `simplify` pool offers whenever the reducing factor collides
    item = _draw("rr.simplify")
    a, b = item.choices[keyed(item)].split(" to ")
    cases.append(("the key ratio, unreduced",
                  _hurt(item, 2, f"{int(a) * 3} to {int(b) * 3}"),
                  CHECKS["rr.simplify"]))

    # 3. the right answer attached to the wrong letter
    item = _draw("rr.convert")
    item.answer = "ABCD"[(keyed(item) + 1) % 4]
    cases.append(("the key moved a letter", item, CHECKS["rr.convert"]))

    # 4. a second true sentence: the key said about the other ingredient, in
    #    the units it actually comes to
    item = _draw("rr.mix_statement")
    m = re.search(r"by mixing ([\d.]+) (\w+) of (.+?) with ([\d.]+) \2 of (.+?)\."
                  r".*? uses ([\d.]+) \2 of \3 ", item.stem, re.S)
    first, unit, second, again = (Q(m.group(1)), m.group(2),
                                  Q(m.group(4)), Q(m.group(6)))
    truth = again * second / first
    cases.append(("the key said twice, as a plain amount",
                  _hurt(item, 2, f"Exactly {float(truth):g} {unit}"),
                  CHECKS["rr.mix_statement"]))

    # 5. two printed options equally close, on a "closest to" stem -- the live
    #    defect this script found, rebuilt: a pair of trees and a number of
    #    years whose difference lands exactly on a half-tenth, with both
    #    neighbouring tenths printed
    cases.append(("two options equally close on a 'closest to' stem",
                  _growth_tie(), CHECKS["rr.growth_table"]))

    # 6. a rounded stem with no answer at all: 124 kilograms per cubic meter in
    #    a cube of edge 0.50 is 15.5 kilograms, and "to the nearest whole
    #    number" is then a convention rather than a question
    item = _draw("rr.cube_density")
    item.stem = re.sub(r"is [\d,]+ kilograms per cubic meter",
                       "is 124 kilograms per cubic meter", item.stem)
    item.stem = re.sub(r"length of [\d.]+ meters", "length of 0.50 meters", item.stem)
    cases.append(("a value exactly halfway between two whole numbers", item,
                  CHECKS["rr.cube_density"]))

    # 7. two printed options equally close where nothing is halfway: an
    #    "approximately" stem with a distractor mirrored across the true value.
    #    This is the tie itself, not the rounding convention, so it exercises
    #    the other branch of the same assertion.
    item = _draw("rr.rate_product", lambda it: "megawatt-hours" in it.stem)
    m = only(r"was ([\d,]+) megawatts .*? for ([\d,]+) hours", item.stem, re.S)
    exact = num(m.group(1)) * num(m.group(2))
    mirror = 2 * exact - num(item.choices[keyed(item)])
    cases.append(("an option mirrored across the true value",
                  _hurt(item, 2, f"{int(mirror):,}"), CHECKS["rr.rate_product"]))

    bad = 0
    for what, item, checker in cases:
        try:
            checker(item)
            print(f" FAIL  {what}: not caught")
            bad = 1
        except (AssertionError, Unreadable) as exc:
            print(f"  ok   {what}: {exc}")
    return bad


def check_sources() -> int:
    """The same assertions over the official option sets, as transcribed."""
    import random

    from satbank.topic import load_topics

    bad = checked = 0
    topic = load_topics()["ratios_rates_proportions_and_units"]
    for src in topic.sources:
        item = src.build(random.Random(0))
        if item.fmt != "mcq" or item.template not in CHECKS:
            continue
        try:
            CHECKS[item.template](item)
            checked += 1
        except (AssertionError, Unreadable) as exc:
            bad += 1
            print(f" FAIL  {src.id} ({item.template}): {exc}")
            print(item.pretty())
    print(f"\n{checked} official option sets read back"
          + ("" if not bad else f", {bad} with a defect"))
    return 1 if bad else 0


# ------------------------------------------------------------------ driver

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--draws", type=int, default=600,
                    help="seeds to try per template (default 600)")
    ap.add_argument("--template", action="append",
                    help="check only this template; repeatable")
    ap.add_argument("--selftest", action="store_true",
                    help="inject seven faults and show each one caught")
    ap.add_argument("--sources", action="store_true",
                    help="check the official option sets instead of draws")
    ap.add_argument("--all", action="store_true",
                    help="print every defect, not just the first of each kind")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.sources:
        return check_sources()

    worst = 0
    for name in args.template or list(CHECKS):
        checker = CHECKS[name]
        made = bad = 0
        what = ""
        for seed in range(args.draws):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            if item.fmt != "mcq":
                continue
            made += 1
            try:
                what = checker(item)
            except (AssertionError, Unreadable) as exc:
                bad += 1
                if bad == 1 or args.all:
                    print(f"\n{name} seed {seed}: {exc}")
                    print(item.pretty())
        mark = "  ok  " if not bad else " FAIL "
        print(f"{mark} {name:<22} {made:>5,} items, {bad} defects   ({what})")
        worst |= 1 if bad else 0
    return worst


if __name__ == "__main__":
    sys.exit(main())
