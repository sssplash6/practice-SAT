"""A ratio and what a student is asked to do with one.

Eleven templates, and between them they cover every source item whose subject
is the ratio itself rather than a rate or a unit:

    partner          a part-to-part ratio, one part given -> the other
    equivalent       two equivalent ratios -> the missing term, or the factor
    table_constant   a table of pairs at one constant ratio -> the missing entry
    simplify         two counts -> the ratio between them, in lowest terms
    similar_rect     the same length-to-width ratio -> the second width
    dimension_shift  one side changes -> how the other must change
    mix_statement    a mixture scaled up -> which description of it is right
    expression       the same scaling, written as an expression
    multiple         a proportional model at 9k and at 3k -> the factor between
    chain_unknown    two given ratios sharing a and b -> the constant between them
    repeated_factor  a quantity doubling year on year -> what it started at

The mistake this family exists to model is the additive one: comparing two
rows of a proportional table by subtracting rather than by multiplying. It is
the single commonest wrong answer on a ratio item, and it appears here under
its own name, in the words a teacher would use.
"""

from __future__ import annotations

import random

from ....expr import Poly, fmt_frac
from ....item import Item, ItemError
from ..values import Q, dec, mcq, places_needed, q, spr, text_mcq

__all__ = ["partner", "equivalent", "table_constant", "simplify", "similar_rect",
           "dimension_shift", "mix_statement", "expression", "multiple",
           "chain_unknown", "repeated_factor"]

# ------------------------------------------------------------------ contexts

# (thing, first kind, second kind, container)
COLLECTIONS = [
    ("pens", "black pens", "red pens", "box"),
    ("beads", "glass beads", "wooden beads", "jar"),
    ("tiles", "white tiles", "blue tiles", "crate"),
    ("bulbs", "tulip bulbs", "daffodil bulbs", "sack"),
    ("cards", "red cards", "blue cards", "box"),
    ("buttons", "round buttons", "square buttons", "tin"),
    ("nails", "steel nails", "brass nails", "bin"),
    ("stamps", "domestic stamps", "foreign stamps", "album"),
    ("marbles", "green marbles", "yellow marbles", "bag"),
    ("keys", "brass keys", "nickel keys", "drawer"),
]

OWNERS = ["Shaquan", "Priya", "Marcus", "Ingrid", "Dominic", "Yara", "Leon",
          "Nadia", "Tomas", "Renata"]

LETTERS = [("t", "u"), ("j", "k"), ("m", "n"), ("p", "r"), ("a", "b"),
           ("c", "d"), ("v", "w"), ("g", "h")]

# (quantity, its unit, the partner quantity, its unit, the story)
ESTIMATES = [
    ("m", "miles", "k", "seconds",
     "For a person m miles from a flash of lightning, the length of the time "
     "interval from the moment the person sees the lightning to the moment the "
     "person hears the thunder is k seconds."),
    ("d", "miles", "s", "seconds",
     "For a ship d miles from a sonar buoy, the time an echo takes to return to "
     "the buoy is s seconds."),
    ("h", "meters", "t", "seconds",
     "For a stone dropped h meters down a well, the time before the splash is "
     "heard is t seconds."),
]

RATIO_PAIRS = [(1, 2), (1, 3), (1, 4), (1, 5), (2, 1), (3, 1), (4, 1), (5, 1),
               (8, 1), (1, 8), (2, 3), (3, 2), (3, 4), (4, 3), (2, 5), (5, 2),
               (3, 5), (5, 3), (5, 6), (6, 5), (7, 2), (2, 7), (9, 4), (4, 9),
               (11, 12), (12, 11), (7, 10), (10, 7)]


def _article(word: str) -> str:
    return "an" if word[0].lower() in "aeiou" else "a"


# --------------------------------------------------------------- PARTNER

def partner(rng: random.Random, seed: int, *, a=None, b=None, n=None,
            given: str = "first", frame=None, fmt=None, ctx=None) -> Item:
    """A ratio of a to b with one of the two quantities given as a count."""
    frame = frame or rng.choices(["objects", "letters", "estimate"],
                                 weights=[5, 4, 2])[0]
    a, b = (a, b) if a is not None else rng.choice(RATIO_PAIRS)
    a, b = q(a), q(b)
    if a == b:
        raise ItemError("a ratio of a to a asks nothing")
    # a drawn multiplier is a multiple of the other term, so that the inverted
    # rate -- the mistake this item exists to catch -- is itself a whole number
    mult = q(n) / (a if given == "first" else b) if n is not None else \
        (b if given == "first" else a) * q(rng.randrange(1, 9))
    if mult.denominator != 1 or mult <= 0:
        raise ItemError("the given count is not a whole number of ratio units")
    n = (a if given == "first" else b) * mult
    key = (b if given == "first" else a) * mult

    if frame == "objects":
        thing, first, second, holder = ctx or rng.choice(COLLECTIONS)
        got, want = (first, second) if given == "first" else (second, first)
        stem = (f"In {_article(holder)} {holder} of {thing}, the ratio of {first} "
                f"to {second} is {dec(a, 0)} to {dec(b, 0)}. There are {dec(n, 0)} "
                f"{got} in the {holder}. How many {want} are in the {holder}?")
        skill = "scaling a part-to-part ratio"
        difficulty = "easy"
    elif frame == "letters":
        x, y = ctx or rng.choice(LETTERS)
        got, want = (x, y) if given == "first" else (y, x)
        stem = (f"The ratio of {x} to {y} is {dec(a, 0)} to {dec(b, 0)}, and "
                f"{got} = {dec(n, 0)}. What is the value of {want} ?")
        skill = "scaling a part-to-part ratio"
        difficulty = "easy"
    else:
        x, xu, y, yu, story = ctx or rng.choice(ESTIMATES)
        if given == "first":
            raise ItemError("this frame states the second quantity")
        stem = (f"{story} The ratio of {x} to {y} can be estimated to be "
                f"{dec(a, 0)} to {dec(b, 0)}. According to this estimate, what is "
                f"the value of {x} when {y} is {dec(n, 0)}?")
        skill = "scaling a part-to-part ratio"
        difficulty = "easy"

    if key.denominator != 1 or key <= 0:
        raise ItemError("the partner count has to come out whole")
    if key == n:
        raise ItemError("the two counts would be equal")

    P = {"kind": "rr_partner", "a": [a.numerator, a.denominator],
         "b": [b.numerator, b.denominator], "n": [n.numerator, n.denominator],
         "given": given}
    inverted = n * (a / b if given == "first" else b / a)
    big, small = (a, b) if a > b else (b, a)
    mine, theirs = ((a, b) if given == "first" else (b, a))
    mistakes = [
        (f"multiplied by {dec(mine, 0)} and divided by {dec(theirs, 0)}, the "
         "ratio upside down", inverted if inverted.denominator == 1 else None),
        ("gave a term of the ratio itself rather than the quantity it scales",
         big),
        ("repeated the number the item already gave", n),
        ("found the two quantities together instead of the one asked for",
         n + key),
        ("gave the other term of the ratio", small),
        ("took the difference of the two quantities", abs(n - key)),
    ]
    rationale = (f"{dec(a, 0)} to {dec(b, 0)} means every {dec(a, 0)} goes with "
                 f"{dec(b, 0)}. Since {dec(n, 0)} ÷ {dec(mine, 0)} = "
                 f"{dec(mult, 0)}, there are {dec(mult, 0)} such groups, so the "
                 f"other quantity is {dec(mult, 0)} × {dec(theirs, 0)} = "
                 f"{dec(key, 0)}.")
    fmt = fmt or ("spr" if rng.random() < 0.2 else "mcq")
    if fmt == "spr":
        return spr("rr.partner", skill, difficulty, seed, stem, key, rationale, params=P)
    return mcq("rr.partner", skill, difficulty, seed, stem, key, mistakes, rng,
               rationale, params=P)


# ------------------------------------------------------------ EQUIVALENT

def equivalent(rng: random.Random, seed: int, *, first=None, c=None, d=None,
               ask: str = "term", p=None, r=None, n=None, fmt=None,
               ctx=None) -> Item:
    """Two ratios that are equal: the missing term, or the factor that keeps them so."""
    if ask == "term":
        c = q(c) if c is not None else q(rng.randrange(2, 30))
        d = q(d) if d is not None else q(rng.randrange(2, 40))
        if c == d:
            raise ItemError("a ratio of c to c fixes nothing")
        first = q(first) if first is not None else c * q(rng.randrange(2, 40))
        key = first * d / c
        if key.denominator != 1 or key <= 0 or key == first:
            raise ItemError("the missing term has to be a whole number")
        stem = (f"The ratio {dec(first, 0)} to m is equivalent to the ratio "
                f"{dec(c, 0)} to {dec(d, 0)}. What is the value of m?")
        P = {"kind": "rr_equivalent", "ask": "term", "first": float(first),
             "c": float(c), "d": float(d), "n": 0.0}
        mistakes = [
            (f"crossed the ratio the wrong way, multiplying by {dec(c, 0)} and "
             f"dividing by {dec(d, 0)}", _whole(first * c / d)),
            ("added on the difference between the two given terms instead of "
             "scaling", first + (d - c)),
            (f"gave the term {dec(d, 0)} from the second ratio unchanged", d),
            ("scaled the wrong term, leaving the ratio reversed",
             _whole(first * first / c)),
        ]
        rationale = (f"{dec(c, 0)} to {dec(d, 0)} scales up by "
                     f"{dec(first / c, places_needed(first / c))}, because "
                     f"{dec(first, 0)} ÷ {dec(c, 0)} = "
                     f"{dec(first / c, places_needed(first / c))}, so m is "
                     f"{dec(d, 0)} × {dec(first / c, places_needed(first / c))} = "
                     f"{dec(key, 0)}.")
        skill = "equivalent ratios"
    else:
        p = q(p) if p is not None else q(rng.randrange(2, 20))
        r = q(r) if r is not None else q(rng.randrange(2, 20))
        if p == r:
            raise ItemError("a ratio of p to p asks nothing")
        n = q(n) if n is not None else q(rng.randrange(3, 40))
        key = n
        x, y = ctx or rng.choice(LETTERS)
        stem = (f"For the values {x} and {y}, the ratio of {x} to {y} is "
                f"{dec(p, 0)} to {dec(r, 0)}. If {x} is multiplied by "
                f"{dec(n, 0)}, what is {y} multiplied by in order to maintain "
                f"the same ratio?")
        P = {"kind": "rr_equivalent", "ask": "factor", "first": 0.0,
             "c": float(p), "d": float(r), "n": float(n)}
        mistakes = [
            ("multiplied the factor by the ratio as well, as though the ratio "
             "itself had to be scaled", _whole(n * r / p)),
            ("added the difference of the ratio's terms to the factor", n + (r - p)),
            (f"gave the term {dec(r, 0)} of the ratio instead of the factor", r),
            ("squared the factor", n * n),
        ]
        rationale = (f"A ratio is unchanged when both quantities are multiplied "
                     f"by the same number, so {y} is multiplied by "
                     f"{dec(n, 0)} as well; "
                     f"{dec(p * n, 0)} to {dec(r * n, 0)} reduces to "
                     f"{dec(p, 0)} to {dec(r, 0)}.")
        skill = "equivalent ratios"

    fmt = fmt or ("spr" if rng.random() < 0.45 else "mcq")
    if fmt == "spr":
        return spr("rr.equivalent", skill, "medium", seed, stem, key, rationale,
                   params=P)
    return mcq("rr.equivalent", skill, "medium", seed, stem, key, mistakes, rng,
               rationale, params=P)


# ------------------------------------------------------- TABLE OF PAIRS

def table_constant(rng: random.Random, seed: int, *, ratio=None, xs=None,
                   last=None, letters=None, fmt=None) -> Item:
    """A table of ordered pairs at one constant ratio, with one entry missing."""
    ratio = q(ratio) if ratio is not None else q(rng.choice([2, 3, 4, 5, 6, 7, 8,
                                                             10, Q(1, 2), Q(3, 2),
                                                             Q(5, 2), Q(1, 4)]))
    if ratio <= 0 or ratio == 1:
        raise ItemError("a constant ratio of 1 makes the table say nothing")
    xs = list(xs) if xs else sorted(rng.sample(range(1, 12), 3))
    last = q(last) if last is not None else q(rng.randrange(14, 90))
    x, y = letters or rng.choice(LETTERS)
    # the missing entry needs a name of its own; k is the source's, unless a
    # column has already taken it
    unknown = next(c for c in "kpqrsw" if c not in (x, y))
    if last in xs:
        raise ItemError("the missing row repeats a row already in the table")
    key = last * ratio
    if key.denominator != 1 or any((q(v) * ratio).denominator != 1 for v in xs):
        raise ItemError("the table would print a fraction")

    rows = [[x, y]] + [[dec(v, 0), dec(q(v) * ratio, 0)] for v in xs]
    rows.append([dec(last, 0), unknown])
    stem = (f"In the table above, the ratio of {y} to {x} for each ordered pair "
            f"is constant. What is the value of {unknown} ?")
    P = {"kind": "rr_table_constant", "ratio": [ratio.numerator, ratio.denominator],
         "last": float(last), "xs": [float(v) for v in xs]}
    mistakes = [
        ("halved the constant ratio", key / 2),
        (f"compared {dec(last, 0)} with the table by subtracting the {y} beside "
         f"{x} = {dec(xs[0], 0)}, an additive comparison where the table is "
         "multiplicative", last - q(xs[0]) * ratio),
        (f"subtracted the {y} beside {x} = {dec(xs[1], 0)} from {dec(last, 0)} "
         "instead of multiplying by the constant ratio",
         last - q(xs[1]) * ratio),
        (f"added the constant ratio to {dec(last, 0)} rather than multiplying "
         "by it", last + ratio),
        ("divided by the constant ratio instead of multiplying", last / ratio),
    ]
    rationale = (f"Every row has {y} ÷ {x} = "
                 f"{dec(ratio, places_needed(ratio))}, so the last row has "
                 f"{unknown} = {dec(last, 0)} × "
                 f"{dec(ratio, places_needed(ratio))} = {dec(key, 0)}.")
    fmt = fmt or ("spr" if rng.random() < 0.2 else "mcq")
    if fmt == "spr":
        return spr("rr.table_constant", "a constant ratio in a table", "easy", seed,
                   stem, key, rationale, params=P, table=rows)
    return mcq("rr.table_constant", "a constant ratio in a table", "easy", seed,
               stem, key, mistakes, rng, rationale, params=P, table=rows)


# ---------------------------------------------------------------- SIMPLIFY

def simplify(rng: random.Random, seed: int, *, n1=None, n2=None, ctx=None,
             owner=None) -> Item:
    """Two counts, and the ratio between them in lowest terms."""
    thing, first, second, _ = ctx or rng.choice(COLLECTIONS)
    owner = owner or rng.choice(OWNERS)
    g = rng.randrange(2, 13)
    n1 = int(n1) if n1 is not None else g * rng.randrange(1, 9)
    n2 = int(n2) if n2 is not None else g * rng.randrange(1, 9)
    if n1 <= 0 or n2 <= 0 or n1 == n2:
        raise ItemError("two equal counts make a ratio of 1 to 1")
    g = _gcd(n1, n2)
    a, b = n1 // g, n2 // g
    if g == 1:
        raise ItemError("the counts are already in lowest terms, so nothing reduces")
    key = f"{a} to {b}"
    stem = (f"{owner} has {n1:,} {first} and {n2:,} {second}. What is the ratio "
            f"of {first} to {second} that {owner} has?")
    P = {"kind": "rr_simplify", "n1": n1, "n2": n2}
    # `{n1} to {n2}` is not on this list, and must never be: the counts
    # unreduced are the same ratio as the key, so offering them is a second
    # right answer rather than a misconception. It used to sit here, and reached
    # the page whenever g == b collapsed the two options above it into one --
    # `7 to 3` beside `21 to 9`, both correct, in 114 draws in 2,000.
    wrong = [
        (f"reversed the order, giving {second} to {first}", f"{b} to {a}"),
        (f"divided {n2:,} by {b} rather than by the {g} that reduces {n1:,} to "
         f"{a}", f"{a} to {g}"),
        ("reversed that, and divided by the wrong count as well", f"{g} to {a}"),
        (f"gave {first} to all the objects rather than {first} to {second}",
         f"{n1 // _gcd(n1, n1 + n2)} to {(n1 + n2) // _gcd(n1, n1 + n2)}"),
        (f"reduced the {first} and left the {second} as they were",
         f"{a} to {n2}"),
        (f"reduced the {second} and left the {first} as they were",
         f"{n1} to {b}"),
    ]
    # the one invariant that matters here, enforced on the pool rather than on
    # each entry: a wrong option must not be the key written another way. The
    # options are ratios, and `assemble_text` de-duplicates on the *string*, so
    # `4 to 2` sails past it beside a key of `2 to 1`. Deciding it as a ratio is
    # the only thing that catches that, and it catches the next one too.
    wrong = [(why, text) for why, text in wrong if _ratio_of(text) != Q(a, b)]
    rationale = (f"{n1:,} and {n2:,} share a factor of {g}, and dividing both by "
                 f"{g} gives {a} to {b}.")
    return text_mcq("rr.simplify", "a ratio in lowest terms", "easy", seed, stem,
                    key, wrong, rng, rationale, params=P)


def _ratio_of(text: str) -> Q:
    """`5 to 8` as the number it names, so two spellings of one ratio compare
    equal. Nothing else in this file needs it; nothing else prints a ratio."""
    left, right = text.split(" to ")
    return Q(int(left), int(right))


def _whole(v):
    """A value only when it is a whole number: a count of objects never has a
    half in it, and an option that does gives itself away."""
    v = q(v)
    return v if v.denominator == 1 else None


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


# ------------------------------------------------------------ SIMILAR RECTANGLE

def similar_rect(rng: random.Random, seed: int, *, l1=None, l2=None, var="w",
                 names=None) -> Item:
    """Two rectangles at one length-to-width ratio; the second width in terms of w."""
    l1 = q(l1) if l1 is not None else q(rng.randrange(3, 40))
    l2 = q(l2) if l2 is not None else q(rng.randrange(3, 40))
    if l1 == l2 or l1 <= 0 or l2 <= 0:
        raise ItemError("two equal lengths make the second rectangle the first")
    first, second = names or ("A", "B")
    ratio = l2 / l1
    if ratio.denominator != 1 and (1 / ratio).denominator == 1:
        raise ItemError("the key would be the only fraction among the options")
    key = _coef_var(ratio, var)
    stem = (f"Rectangle {first} has length {dec(l1, 0)} and width {var}. "
            f"Rectangle {second} has length {dec(l2, 0)} and the same "
            f"length-to-width ratio as rectangle {first}. What is the width of "
            f"rectangle {second} in terms of {var} ?")
    P = {"kind": "rr_similar_rect", "l1": float(l1), "l2": float(l2), "var": var}
    diff = abs(l2 - l1)
    wrong = [
        (f"scaled by {dec(l1, 0)} over {dec(l2, 0)}, the ratio upside down",
         _coef_var(l1 / l2, var)),
        (f"added the {dec(diff, 0)} the lengths differ by, comparing the "
         "rectangles by subtraction rather than by a ratio",
         _sum_var(var, diff)),
        (f"subtracted that {dec(diff, 0)} instead", _sum_var(var, -diff)),
        ("multiplied by the second length itself", _coef_var(l2, var)),
    ]
    rationale = (f"The two rectangles share one ratio, so the widths scale by the "
                 f"same factor as the lengths: {dec(l2, 0)} ÷ {dec(l1, 0)} = "
                 f"{fmt_frac(ratio)}, and the width of rectangle {second} is "
                 f"{key}.")
    return text_mcq("rr.similar_rect", "a ratio kept between two figures", "medium",
                    seed, stem, key, wrong, rng, rationale, params=P)


def _coef_var(c, var: str) -> str:
    """'(4/3)w', '2w', 'w' -- the engine's plain-text spelling of a coefficient."""
    return Poly.of(0, q(c)).text(var)


def _sum_var(var: str, k) -> str:
    """'w + 5', 'w − 5' -- with the minus sign the page prints, not a hyphen."""
    return Poly.of(q(k), 1).text(var).replace(" - ", " − ")


# ------------------------------------------------------------ DIMENSION SHIFT

def dimension_shift(rng: random.Random, seed: int, *, length=None, width=None,
                    change=None, up: bool = True, moved: str = "width") -> Item:
    """One side of a rectangle changes; how must the other change to keep the ratio?"""
    length = q(length) if length is not None else q(rng.randrange(4, 60))
    width = q(width) if width is not None else q(rng.randrange(2, 40))
    if length == width:
        raise ItemError("a ratio of 1 to 1 makes both changes equal")
    change = q(change) if change is not None else q(rng.randrange(2, 20))
    if change <= 0:
        raise ItemError("the change has to be an amount")
    ratio = (length / width) if moved == "width" else (width / length)
    shift = ratio * change
    if places_needed(shift, 3) > 2:
        raise ItemError("the matching change does not print in two decimals")
    other = "length" if moved == "width" else "width"
    word = "increases" if up else "decreases"
    stem = (f"For a certain rectangular region, the ratio of its length to its "
            f"width is {dec(length, 0)} to {dec(width, 0)}. If the {moved} of the "
            f"rectangular region {word} by {dec(change, 0)} units, how must the "
            f"{other} change to maintain this ratio?")
    P = {"kind": "rr_dimension_shift", "length": float(length),
         "width": float(width), "change": float(change), "up": up, "moved": moved}
    same = "increase" if up else "decrease"
    opposite = "decrease" if up else "increase"
    size = dec(shift, places_needed(shift))
    key = f"It must {same} by {size} units."
    wrong = [
        ("scaled by the right factor but sent the other side the wrong way",
         f"It must {opposite} by {size} units."),
        ("changed the other side by the same number of units, comparing the "
         "sides by subtraction rather than by their ratio",
         f"It must {same} by {dec(change, 0)} units."),
        ("did both: the same number of units, and the wrong direction",
         f"It must {opposite} by {dec(change, 0)} units."),
        (f"used the ratio upside down, {dec(width, 0)} to {dec(length, 0)}",
         f"It must {same} by "
         f"{dec(change / ratio, places_needed(change / ratio))} units."),
    ]
    rationale = (f"The ratio holds only if both sides scale by the same factor: "
                 f"the {other} is {fmt_frac(ratio)} of the {moved}, so a change "
                 f"of {dec(change, 0)} units in the {moved} needs "
                 f"{fmt_frac(ratio)} × {dec(change, 0)} = {size} units in the "
                 f"{other}, in the same direction.")
    return text_mcq("rr.dimension_shift", "a ratio kept while a side changes",
                    "medium", seed, stem, key, wrong, rng, rationale, params=P)


# ------------------------------------------------------------- MIX STATEMENT

# (what is made, the first component, the second, the unit, who, the pronoun)
MIXES = [("green paint", "blue paint", "yellow paint", "ounces", "Anita", "She"),
         ("lilac paint", "white paint", "red paint", "ounces", "Devon", "He"),
         ("bronze powder", "copper powder", "tin powder", "grams", "Priya", "She"),
         ("trail mix", "raisins", "peanuts", "grams", "Kofi", "He"),
         ("mortar", "cement", "sand", "kilograms", "Rosa", "She"),
         ("grout", "plaster", "marble dust", "kilograms", "Ivo", "He")]


def mix_statement(rng: random.Random, seed: int, *, first=None, second=None,
                  again=None, ctx=None) -> Item:
    """A mixture made again at the same ratio, described rather than counted."""
    made, one, two, unit, who, they = ctx or rng.choice(MIXES)
    first = q(first) if first is not None else q(rng.randrange(2, 9))
    second = q(second) if second is not None else q(rng.randrange(2, 12))
    again = q(again) if again is not None else q(rng.randrange(2, 15))
    scale = second / first
    if first == second:
        raise ItemError("a one-to-one mixture makes two of the options true")
    if again == second:
        raise ItemError("scaling by the yellow amount would make a wrong option right")
    if again == first:
        raise ItemError("the second batch repeats the first")
    if places_needed(scale, 3) > 2:
        raise ItemError("the scale factor does not print in two decimals")
    factor = dec(scale, places_needed(scale))
    stem = (f"{who} created a batch of {made} by mixing {dec(first, 0)} {unit} "
            f"of {one} with {dec(second, 0)} {unit} of {two}. {they} must mix a "
            f"second batch using the same ratio of {one} and {two} as the first "
            f"batch. If {who} uses {dec(again, 0)} {unit} of {one} for the second "
            f"batch, how much {two} should {who} use?")
    P = {"kind": "rr_mix_statement", "first": float(first), "second": float(second),
         "again": float(again), "one": one, "two": two, "unit": unit}
    key = f"{factor} times the amount of {one} used in the second batch"
    grew = dec(again - first, places_needed(abs(again - first))) if again > first \
        else dec(first - again, places_needed(abs(again - first)))
    more = "more than" if again > first else "less than"
    wrong = [
        (f"used the same amount as the {one}, as though the ratio were one to one",
         f"Exactly {dec(again, 0)} {unit}"),
        (f"kept the difference rather than the ratio: the {one} changed by {grew} "
         f"{unit}, so the {two} was changed by {grew} too",
         f"{grew} {unit} {more} the amount of {two} used in the first batch"),
        ("applied the scale factor to the wrong quantity",
         f"{factor} times the amount of {two} used in the first batch"),
        ("scaled by the ratio upside down",
         f"{dec(first / second, places_needed(first / second, 3))} times the "
         f"amount of {one} used in the second batch"),
    ]
    rationale = (f"The first batch has {dec(second, 0)} {unit} of {two} for every "
                 f"{dec(first, 0)} {unit} of {one}, which is {factor} times as "
                 f"much, and that factor is what the second batch has to keep.")
    return text_mcq("rr.mix_statement", "a ratio described rather than counted",
                    "hard", seed, stem, key, wrong, rng, rationale, params=P)


# ---------------------------------------------------------------- EXPRESSION

EARNERS = [("Tilly", "she"), ("Renzo", "he"), ("Aisha", "she"), ("Bode", "he"),
           ("Saoirse", "she"), ("Malik", "he")]
GOODS = [("objects", "kilograms"), ("crates", "kilograms"), ("bricks", "kilograms"),
         ("panels", "kilograms"), ("rolls", "kilograms")]


def expression(rng: random.Random, seed: int, *, form=None, n=None, var=None,
               partner=None, rate=None, ctx=None) -> Item:
    """The same proportional step, asked for as an expression rather than a value."""
    form = form or rng.choice(["scale_pay", "scale_mass", "substitute", "hourly"])

    if form in ("scale_pay", "scale_mass"):
        n = int(n) if n is not None else rng.randrange(3, 200)
        if n < 2:
            raise ItemError("scaling by one asks nothing")
        if form == "scale_pay":
            who, _ = ctx or rng.choice(EARNERS)
            var, partner = var or "p", partner or "w"
            stem = (f"{who} earns {var} dollars for every {partner} hours of work. "
                    f"Which expression represents the amount of money, in dollars, "
                    f"{who} earns for {n}{partner} hours of work?")
            key = f"{n}{var}"
            wrong = [
                (f"divided by {n} where the hours were multiplied by it",
                 f"{var}/{n}"),
                (f"added {n} instead of multiplying by it", f"{var} + {n}"),
                (f"subtracted {n}", f"{var} − {n}"),
                (f"scaled by {n} twice", f"{n * n}{var}"),
            ]
            skill = "a proportional relationship written as an expression"
        else:
            thing, unit = ctx or rng.choice(GOODS)
            var, partner = var or "t", partner or "r"
            stem = (f"The total mass, in {unit}, of {partner} identical {thing} is "
                    f"{var}. Which expression represents the total mass, in {unit}, "
                    f"of {n}{partner} of these {thing}?")
            key = f"{n}{var}"
            wrong = [
                (f"subtracted the mass from the count of {thing}",
                 f"{n} − {var}"),
                (f"added {n} instead of multiplying by it", f"{n} + {var}"),
                (f"divided by {n} where the count was multiplied by it",
                 f"{var}/{n}"),
                (f"scaled by {n} twice", f"{n * n}{var}"),
            ]
            skill = "a proportional relationship written as an expression"
        rationale = (f"{n} times as many {'hours' if form == 'scale_pay' else thing} "
                     f"is {n} times the {'money' if form == 'scale_pay' else 'mass'}, "
                     f"so the answer is {n} × {var} = {key}.")
        P = {"kind": "rr_expression", "form": form, "n": n, "var": var,
             "rate": 0.0, "partner": partner}

    elif form == "substitute":
        n = int(n) if n is not None else rng.randrange(2, 12)
        m = int(partner) if partner is not None else rng.randrange(2, 12)
        x, y = ctx or rng.choice(LETTERS)
        if n == 1 or m == 1 or n == m:
            raise ItemError("a coefficient of one makes two options the same")
        stem = f"If {x} = {m}{y}, which of the following is equivalent to {n}{x}?"
        key = f"{n * m}{y}"
        wrong = [
            (f"multiplied {y} by {n} and dropped the {m} that {x} carries",
             f"{n}{y}"),
            (f"divided by {m} where {x} = {m}{y} multiplies by it",
             _coef_var(Q(n, m), y)),
            ("cancelled both coefficients", f"{y}"),
            (f"added the two coefficients instead of multiplying them",
             f"{n + m}{y}"),
        ]
        rationale = (f"Since {x} = {m}{y}, {n}{x} is {n} × {m}{y} = {n * m}{y}.")
        P = {"kind": "rr_expression", "form": form, "n": n, "var": x,
             "rate": float(m), "partner": y}
        skill = "a proportional relationship written as an expression"

    else:                                                          # hourly
        n = int(n) if n is not None else rng.randrange(2, 10)
        rate = q(rate) if rate is not None else q(rng.randrange(825, 2500)) / 100
        who, she = ctx or rng.choice(EARNERS)
        var = var or "z"
        money = dec(rate, 2, group=False)
        stem = (f"{who} earns ${money} per hour at {'her' if she == 'she' else 'his'} "
                f"part-time job. When {she} works {var} hours, {she} earns "
                f"{money}{var} dollars. Which of the following expressions gives "
                f"the amount, in dollars, {who} will earn if {she} works {n}{var} "
                f"hours?")
        key = f"{n}({money}{var})"
        wrong = [
            (f"added {n} to the earnings instead of multiplying them by it",
             f"{n} + {money}{var}"),
            (f"added {n}{var} hours' worth of nothing to the earnings",
             f"{n}{var} + {money}{var}"),
            (f"added {n} to the hours inside the rate rather than multiplying "
             "the hours by it", f"{money}({var} + {n})"),
            (f"multiplied the rate by {n} and the hours by {n} as well",
             f"{n}({money}){n}{var}"),
        ]
        rationale = (f"{n}{var} hours is {n} times {var} hours, and the pay is "
                     f"proportional to the hours, so the amount is {n} times "
                     f"{money}{var}.")
        P = {"kind": "rr_expression", "form": form, "n": n, "var": var,
             "rate": float(rate), "partner": ""}
        skill = "a proportional relationship written as an expression"

    return text_mcq("rr.expression", skill, "easy", seed, stem, key, wrong, rng,
                    rationale, params=P)


# ------------------------------------------------------------------ MULTIPLE

def multiple(rng: random.Random, seed: int, *, rate=None, big=None, small=None,
             var="k") -> Item:
    """A proportional model read at two multiples of the same constant."""
    rate = int(rate) if rate is not None else rng.randrange(15, 80)
    small = int(small) if small is not None else rng.randrange(2, 8)
    big = int(big) if big is not None else small * rng.randrange(2, 7)
    if small <= 0 or big <= small or big % small:
        raise ItemError("the two multiples have to divide")
    times = big // small
    if times < 2:
        raise ItemError("the two periods would be the same")
    stem = (f"The equation d = {rate}t can be used to calculate the distance d, "
            f"in miles, traveled by a car moving at a speed of {rate} miles per hour "
            f"over a period of t hours. For any positive constant {var}, the "
            f"distance the car would have traveled after {big}{var} hours is how "
            f"many times the distance the car would have traveled after "
            f"{small}{var} hours?")
    key = f"{times}"
    P = {"kind": "rr_multiple", "rate": rate, "big": big, "small": small, "var": var}
    wrong = [
        (f"subtracted the two multiples instead of dividing them",
         f"{big - small}"),
        (f"kept the {var}, which cancels when one distance is divided by the "
         "other", f"{times}{var}"),
        (f"subtracted the multiples and kept the {var} as well",
         f"{big - small}{var}"),
        (f"divided the speed into the multiple", f"{big * small}"),
    ]
    rationale = (f"d = {rate}t is proportional, so the distances are "
                 f"{rate} × {big}{var} and {rate} × {small}{var}, and one divided "
                 f"by the other is {big} ÷ {small} = {times}; the {rate} and the "
                 f"{var} both cancel.")
    return text_mcq("rr.multiple", "reading a proportional model at two inputs",
                    "medium", seed, stem, key, wrong, rng, rationale, params=P)


# ------------------------------------------------------------- CHAIN UNKNOWN

def chain_unknown(rng: random.Random, seed: int, *, c=None, first=None,
                  second=None, letters=None, fmt=None) -> Item:
    """Two stated values of the same ratio, and the constant standing between them."""
    a, b, n = letters or ("a", "b", "n")
    c = q(c) if c is not None else q(rng.choice([2, 3, 4, 5, 6, 8, 10]))
    first = q(first) if first is not None else q(rng.randrange(12, 400)) / 10
    mult = q(rng.choice([2, 4, 5, 8, 10, 16, 20, 25, 32, 40]))
    second = q(second) if second is not None else first * mult / c
    if first <= 0 or second <= 0:
        raise ItemError("both stated values have to be positive")
    key = first / (c * second)
    if places_needed(second, 4) > 2:
        # the stem prints this value in two decimals: 17.625 would be shown as
        # 17.63, and a student solving the stem in front of them would not get
        # the keyed answer
        raise ItemError("the second stated value does not print exactly")
    if places_needed(first, 4) > 2:
        raise ItemError("the first stated value does not print exactly")
    if places_needed(first / c, 4) > 3:
        raise ItemError("the ratio between the two letters does not print exactly")
    if key <= 0 or places_needed(key, 5) > 4:
        raise ItemError("the constant does not print inside four decimals")
    stem = (f"If {dec(c, 0)}{a}/{b} = {dec(first, places_needed(first))} and "
            f"{a}/({b}{n}) = {dec(second, places_needed(second))}, what is the "
            f"value of {n}?")
    P = {"kind": "rr_chain_unknown", "c": float(c), "first": float(first),
         "second": float(second)}
    mistakes = [
        (f"divided the two stated values without first taking the {dec(c, 0)} off "
         f"the left-hand side", first / second),
        ("divided the second value by the first, the ratio upside down",
         second * c / first),
        (f"multiplied by {dec(c, 0)} where the {dec(c, 0)} had to be divided out",
         first * c / second),
    ]
    rationale = (f"{dec(c, 0)}{a}/{b} = {dec(first, places_needed(first))} makes "
                 f"{a}/{b} = {dec(first / c, places_needed(first / c, 4))}, and "
                 f"{a}/({b}{n}) is {a}/{b} divided by {n}, so {n} = "
                 f"{dec(first / c, places_needed(first / c, 4))} ÷ "
                 f"{dec(second, places_needed(second))} = "
                 f"{dec(key, places_needed(key, 4))}.")
    fmt = fmt or ("spr" if rng.random() < 0.5 else "mcq")
    if fmt == "spr":
        return spr("rr.chain_unknown", "a constant between two ratios", "hard", seed,
                   stem, key, rationale, params=P)
    return mcq("rr.chain_unknown", "a constant between two ratios", "hard", seed,
               stem, key, mistakes, rng, rationale, params=P)


# ----------------------------------------------------------- REPEATED FACTOR

SAVERS = [("Jeremy", "his"), ("Adaeze", "her"), ("Milo", "his"), ("Reva", "her"),
          ("Tobias", "his")]


def repeated_factor(rng: random.Random, seed: int, *, total=None, years=None,
                    factor=None, start_year=None, ctx=None, fmt=None) -> Item:
    """A quantity multiplied by the same factor year on year, run backwards."""
    who, whose = ctx or rng.choice(SAVERS)
    factor = int(factor) if factor is not None else rng.choice([2, 2, 2, 3, 4, 5])
    years = int(years) if years is not None else rng.randrange(2, 7)
    start_year = int(start_year) if start_year is not None else rng.randrange(1996, 2019)
    if factor < 2 or years < 1:
        raise ItemError("nothing grows by a factor of one")
    if total is None:
        total = q(rng.randrange(2, 60)) * factor ** years
    total = q(total)
    key = total / factor ** years
    if key.denominator != 1 or key <= 0:
        raise ItemError("the deposit has to be a whole number of dollars")
    word = {2: "doubled", 3: "tripled", 4: "quadrupled"}.get(
        factor, f"was multiplied by {factor}")
    stem = (f"{who} deposited x dollars in {whose} investment account on January 1, "
            f"{start_year}. The amount of money in the account {word} each year "
            f"until {who} had {dec(total, 0)} dollars in {whose} investment "
            f"account on January 1, {start_year + years}. What is the value of x ?")
    P = {"kind": "rr_repeated_factor", "total": float(total), "years": years,
         "factor": factor}
    mistakes = [
        (f"counted {years + 1} years rather than the {years} between the two dates",
         total / factor ** (years + 1)),
        (f"counted {years - 1} years", total / factor ** max(years - 1, 1)),
        (f"multiplied the {years} years by {factor} instead of using {factor} as a "
         "repeated factor", total / (factor * years)),
        (f"divided by {factor} once", total / factor),
    ]
    rationale = (f"From January 1, {start_year} to January 1, {start_year + years} "
                 f"is {years} years, and the money was multiplied by {factor} in "
                 f"each of them: x × {factor}{_sup(years)} = {dec(total, 0)}, so "
                 f"x = {dec(total, 0)} ÷ {factor ** years} = {dec(key, 0)}.")
    fmt = fmt or ("spr" if rng.random() < 0.5 else "mcq")
    if fmt == "spr":
        return spr("rr.repeated_factor", "a repeated factor run backwards", "hard",
                   seed, stem, key, rationale, params=P)
    return mcq("rr.repeated_factor", "a repeated factor run backwards", "hard", seed,
               stem, key, mistakes, rng, rationale, params=P)


_SUPS = "⁰¹²³⁴⁵⁶⁷⁸⁹"


def _sup(n: int) -> str:
    return "".join(_SUPS[int(d)] for d in str(n))
