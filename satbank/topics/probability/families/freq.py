"""One-way frequency tables: a category column and a count column.

Two questions live here. The first reads one category against the whole
collection; the second conditions on a band of the table -- "of those at least
50 years old, what fraction were at least 60?" -- which is the same
conditional the two-way templates ask, with the condition written as a cut
through an ordered list of intervals rather than as a column.

As everywhere in this topic, a total that is printed is a sum of the counts
above it and is never supplied.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import ItemError
from ..values import (decimal, griddable, mcq, percent, pick, ratio, reduced,
                      roll_fmt, spr, unambiguous)
from .simple import art, exact_decimal, order_of

SURFACES = ("ratio", "reduced", "decimal")


def render(num, den, surface, places=None):
    if den == 0:
        raise ItemError("a probability with an empty denominator")
    if surface == "ratio":
        return ratio(num, den)
    if surface == "reduced":
        return reduced(Q(num, den))
    if surface == "decimal":
        return decimal(Q(num, den), places)
    raise ItemError(f"no surface named {surface!r}")


# ------------------------------------------------------------ the scenarios

class FCtx:
    def __init__(self, key, head, count_head, intro, ask, cats, unit, units,
                 title="", lo=2, hi=40, total_row=None):
        self.key, self.head, self.count_head = key, head, count_head
        self.intro, self.ask, self.cats = intro, ask, cats
        self.unit, self.units, self.title = unit, units, title
        self.lo, self.hi = lo, hi
        self.total_row = total_row       # None: either; True/False: forced


FREQ = {c.key: c for c in [
    FCtx("marbles", "Color", "Number",
         "The table shows the number of different colors of marbles in a bag.",
         "If a marble is chosen at random from the bag, what is the probability that "
         "the marble will be {cat}?",
         ["Red", "Blue", "Green", "Yellow", "Purple"], "marble", "marbles",
         title="Colors of Marbles in a Bag", lo=4, hi=30, total_row=True),
    FCtx("singers", "Voice type", "Number of singers",
         "A total of {n} men registered for singing lessons. The frequency table "
         "shows how many of these singers have certain voice types.",
         "If one of these singers is selected at random, what is the probability he "
         "is {art} {cat}?",
         ["Countertenor", "Tenor", "Baritone", "Bass"], "singer", "singers",
         lo=3, hi=20, total_row=False),
    FCtx("rocks", "Classification", "Frequency",
         "Each rock in a collection of {n} rocks was classified as either igneous, "
         "metamorphic, or sedimentary, as shown in the frequency table.",
         "If one of these rocks is selected at random, what is the probability of "
         "selecting a rock that is {cat}?",
         ["igneous", "metamorphic", "sedimentary"], "rock", "rocks",
         lo=5, hi=45, total_row=False),
    FCtx("pets", "Type of pet", "Number of pets",
         "A veterinary clinic recorded the type of each of the {n} pets it treated "
         "in one week.",
         "If one of these pets is selected at random, what is the probability that "
         "it is {art} {cat}?",
         ["Dog", "Cat", "Rabbit", "Lizard"], "pet", "pets", lo=4, hi=35),
    FCtx("sandwiches", "Sandwich", "Number sold",
         "A shop recorded the number of each kind of sandwich it sold on one day.",
         "If one of these sandwiches is selected at random, what is the probability "
         "that it is {art} {cat} sandwich?",
         ["Turkey", "Cheese", "Tuna", "Egg"], "sandwich", "sandwiches",
         lo=6, hi=40, total_row=True),
    FCtx("seedlings", "Species", "Number planted",
         "A nursery recorded the species of each of the {n} seedlings it planted.",
         "If one of these seedlings is selected at random, what is the probability "
         "that it is {art} {cat} seedling?",
         ["Spruce", "Maple", "Willow", "Alder"], "seedling", "seedlings",
         lo=5, hi=40),
]}


def _rows(c, cats, counts, total_row):
    rows = [[c.head, c.count_head]]
    rows += [[lab, f"{k:,}"] for lab, k in zip(cats, counts)]
    if total_row:
        rows.append(["Total", f"{sum(counts):,}"])
    return rows


def freq_table(rng: random.Random, seed: int, *, scenario=None, counts=None, idx=None,
               cats=None, surface=None, places=None, total_row=None, fmt=None,
               wrongs=None, tier="easy"):
    """P(one category) read off a frequency table."""
    c = FREQ[scenario] if scenario else FREQ[rng.choice(sorted(FREQ))]
    cats = cats or c.cats[:len(counts)] if counts else c.cats[:rng.randint(3, len(c.cats))]
    counts = counts or [rng.randint(c.lo, c.hi) for _ in cats]
    if len(counts) != len(cats) or len(cats) < 3:
        raise ItemError("a frequency table needs at least three categories")
    N = sum(counts)
    idx = rng.randrange(len(cats)) if idx is None else idx
    num = counts[idx]
    if not 0 < num < N:
        raise ItemError("a probability of 0 or 1 is not what this question asks")
    total_row = (c.total_row if c.total_row is not None else rng.random() < 0.5) \
        if total_row is None else total_row
    fmt = roll_fmt(rng, fmt)
    surface = "reduced" if fmt == "spr" else (surface or rng.choice(SURFACES))
    if surface == "decimal":
        places = exact_decimal(num, N, places)

    lab = cats[idx]
    low = lab.lower()
    pool = {"count_as_decimal": (f"read the frequency {num:,} as a probability by "
                                 f"moving the decimal point", (num, 100)),
            "over_others": (f"divided by the {N - num:,} other {c.units} instead of "
                            f"by all {N:,}", (num, N - num)),
            "not": (f"found the probability that the {c.unit} is not {low}",
                    (N - num, N))}
    for j, other in enumerate(cats):
        if j == idx:
            continue
        pool[f"cat{j}"] = (f"counted the {other.lower()} {c.units} instead of the {low} ones",
                           (counts[j], N))
        pool[f"not{j}"] = (f"found the probability that the {c.unit} is not {other.lower()}",
                           (N - counts[j], N))
        pool[f"over{j}"] = (f"divided by the {counts[j]:,} {other.lower()} {c.units} instead "
                            f"of by all {N:,}", (num, counts[j]))

    intro = c.intro.format(n=f"{N:,}")
    stem = f"{intro} {c.ask.format(cat=low, art=art(low))}"
    key = render(num, N, surface, places)
    P = {"kind": "prob_freq", "counts": list(counts), "idx": idx, "surface": surface,
         "places": places}
    rationale = (f"{num:,} of the {N:,} {c.units} are {low}, so the "
                 f"probability is {key.plain()}.")
    table = _rows(c, cats, counts, total_row)
    if fmt == "spr":
        if not griddable(Q(num, N)):
            raise ItemError("this probability is not enterable in five characters")
        return spr("prob.freq_table", "frequency table", tier, seed,
                   stem + " (Express your answer as a decimal or fraction, not as a "
                   "percent.)", Q(num, N), rationale, params=P, table=table)
    prefer = [k for k in (f"cat{j}" for j in range(len(cats))) if k in pool] + \
             ["not", "over_others", "count_as_decimal"]
    mistakes = [(why, render(a, b, surface, places))
                for why, (a, b) in pick(pool, wrongs or order_of(pool, prefer), wrongs)
                if b]
    return mcq("prob.freq_table", "frequency table", tier, seed, stem, key, mistakes,
               rng, rationale, params=P, table=table)


# ------------------------------------------------------- prob.freq_grouped

GROUPED = {
    "presidents": ("Ages", "Number",
                   "The table gives the number of United States presidents from 1789 "
                   "to 2015 whose age at the time they first took office is within "
                   "the interval listed.",
                   "Of those presidents who were at least {a} years old when they "
                   "first took office, what fraction were at least {b} years old?",
                   "president", "presidents", "years old",
                   "United States Presidents from 1789 to 2015"),
    "trees": ("Heights (feet)", "Number of trees",
              "The table gives the number of trees in a park whose height, in feet, "
              "is within the interval listed.",
              "Of those trees that are at least {a} feet tall, what fraction are at "
              "least {b} feet tall?", "tree", "trees", "feet tall", ""),
    "scores": ("Scores", "Number of students",
               "The table gives the number of students in a school whose score on a "
               "test is within the interval listed.",
               "Of those students who scored at least {a}, what fraction scored at "
               "least {b}?", "student", "students", "points", ""),
}


def freq_grouped(rng: random.Random, seed: int, *, scenario=None, start=None,
                 width=None, bands=None, counts=None, cut=None, cut2=None,
                 total_row=None, fmt=None, wrongs=None, tier="medium"):
    """A conditional read off a table of ordered intervals: of those at least a,
    what fraction are at least b?"""
    key_s = scenario or rng.choice(sorted(GROUPED))
    head, chead, intro, ask, unit, units, _, title = GROUPED[key_s]
    bands = bands or rng.randint(5, 7)
    width = width or rng.choice([5, 10])
    start = start if start is not None else rng.choice([20, 30, 40, 50, 60])
    counts = counts or [rng.randint(1, 15) for _ in range(bands)]
    if len(counts) != bands or bands < 4:
        raise ItemError("a grouped table needs at least four intervals")
    lows = [start + i * width for i in range(bands)]
    labels = [f"{lo}–{lo + width - 1}" for lo in lows]

    cut = rng.randrange(1, bands - 2) if cut is None else cut
    cut2 = rng.randrange(cut + 1, bands - 1) if cut2 is None else cut2
    if not 0 <= cut < cut2 < bands:
        raise ItemError("the two cuts do not order")
    den = sum(counts[cut:])
    num = sum(counts[cut2:])
    if not 0 < num < den:
        raise ItemError("a conditional probability of 0 or 1 is not what this asks")
    N = sum(counts)
    a, b = lows[cut], lows[cut2]
    total_row = rng.random() < 0.4 if total_row is None else total_row
    fmt = roll_fmt(rng, fmt)

    pool = {
        "joint": (f"divided by all {N:,} {units} instead of by the {den:,} at or "
                  f"above {a}", (num, N)),
        "band": (f"divided by the {sum(counts[cut:cut2]):,} {units} below {b} "
                 f"instead of by the {den:,} at or above {a}",
                 (num, sum(counts[cut:cut2]))),
        "complement_in": (f"counted the {units} that fall below {b} rather than the "
                          f"ones at or above it", (den - num, den)),
        "reverse": (f"divided by the {num:,} at or above {b} instead of by the "
                    f"{den:,} at or above {a}", (den, num)),
        "one_band": (f"used only the single interval beginning at {b}",
                     (counts[cut2], den)),
        "above_over_all": (f"used the {num:,} at or above {b} over all {N:,} {units} "
                           f"and ignored the condition", (num, N)),
    }
    stem = f"{intro} {ask.format(a=a, b=b)}"
    key = ratio(num, den)
    P = {"kind": "prob_grouped", "counts": list(counts), "cut": cut, "cut2": cut2}
    rationale = (f"{den:,} {units} are at or above {a}, and {num:,} of those are at "
                 f"or above {b}, so the fraction is {key.plain()}.")
    rows = [[head, chead]] + [[lab, f"{k:,}"] for lab, k in zip(labels, counts)]
    if total_row:
        rows.append(["Total", f"{N:,}"])
    if fmt == "spr":
        if not griddable(Q(num, den)):
            raise ItemError("this probability is not enterable in five characters")
        return spr("prob.freq_grouped", "frequency table", tier, seed,
                   stem + " (Express your answer as a decimal or fraction, not as a "
                   "percent.)", Q(num, den), rationale, params=P, table=rows)
    mistakes = [(why, ratio(x, y)) for why, (x, y) in
                pick(pool, wrongs or order_of(pool, ["joint", "band",
                                                     "complement_in"]), wrongs) if y]
    return mcq("prob.freq_grouped", "frequency table", tier, seed, stem, key,
               mistakes, rng, rationale, params=P, table=rows)
