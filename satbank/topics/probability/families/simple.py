"""Probability from counts the stem states, with no table to read.

Six question shapes, all of them the same fraction -- favourable over total --
dressed differently. What varies is the surface the answer is printed in and
which count a careless reader reaches for, so each template's wrong answers
are built from the *other* counts in its own stem rather than from arithmetic
on the key.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import ItemError
from ..values import (decimal, griddable, mcq, pick, q, ratio, reduced, spr,
                      text_mcq, unambiguous)

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


def exact_decimal(num, den, places=None):
    """A decimal option must print the value it stands for, to the last digit."""
    v = Q(num, den)
    for p in range(9):
        if (v * 10 ** p).denominator == 1:
            if places is not None and p > places:
                raise ItemError("this probability needs more decimals than the item "
                                "prints")
            return p if places is None else places
    raise ItemError("this probability has no terminating decimal, so it cannot be "
                    "printed as one")


def order_of(pool, prefer):
    return [k for k in prefer if k in pool] + [k for k in pool if k not in prefer]


# ------------------------------------------------------------------ prob.bag

BAGS = [
    ("a bag", "button", "buttons", ["white", "orange", "brown", "black", "gray"]),
    ("a bag", "cube", "cubes", ["red", "white", "blue", "yellow", "green"]),
    ("a box", "pen", "pens", ["red", "blue", "black", "green"]),
    ("a jar", "marble", "marbles", ["red", "blue", "green", "yellow", "purple"]),
    ("a drawer", "sock", "socks", ["black", "white", "gray"]),
    ("a basket", "apple", "apples", ["red", "green", "yellow"]),
    ("a box", "bead", "beads", ["silver", "gold", "white", "clear"]),
    ("a case", "marker", "markers", ["red", "blue", "orange", "black"]),
]


def _bag_list(counts, colors, noun, nouns, style):
    bare = style == "inline"
    parts = [f"{k:,} {c}" if bare else f"{k:,} {c} {nouns}"
             for k, c in zip(counts, colors)]
    tail = f" {nouns}" if bare else ""
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}{tail}"
    return ", ".join(parts[:-1]) + f", and {parts[-1]}{tail}"


def bag(rng: random.Random, seed: int, *, which=None, counts=None, colors=None,
        idx=None, neither=None, style=None, surface=None, places=None, fmt="mcq",
        wrongs=None, tier="easy"):
    """Counts of each kind are listed in the stem; pick one kind, or rule two out."""
    where, noun, nouns, palette = BAGS[rng.randrange(len(BAGS))] if which is None \
        else next(b for b in BAGS if b[2] == which)
    k = len(counts) if counts else rng.randint(3, min(4, len(palette)))
    colors = colors or palette[:k]
    counts = counts or [rng.randint(2, 40) for _ in range(k)]
    if len(counts) != len(colors) or len(colors) < 2:
        raise ItemError("a bag needs a count for every colour named")
    N = sum(counts)
    style = style or rng.choice(("colon", "contains", "inline"))
    surface = surface or rng.choice(SURFACES)

    if neither:
        out = tuple(neither)
        kept = [i for i in range(len(colors)) if i not in out]
        num = sum(counts[i] for i in kept)
        ask = (f"what is the probability of selecting a {noun} that is neither "
               f"{colors[out[0]]} nor {colors[out[1]]}?")
        pool = {"complement": (f"found the probability of selecting a "
                               f"{colors[out[0]]} or {colors[out[1]]} {noun}",
                               (N - num, N))}
        for i in kept:
            pool[f"over_subset{i}"] = (
                f"divided the {counts[i]:,} {colors[i]} {nouns} by the {num:,} that "
                f"are neither {colors[out[0]]} nor {colors[out[1]]}", (counts[i], num))
            pool[f"kept{i}"] = (f"used only the {colors[i]} {nouns}",
                                (counts[i], N))
        for i in out:
            pool[f"subset_over{i}"] = (
                f"divided by the {counts[i]:,} {colors[i]} {nouns} instead of by all "
                f"{N:,} {nouns}", (num, counts[i]))
        prefer = ["complement"] + [f"over_subset{i}" for i in kept] + \
                 [f"subset_over{i}" for i in out]
    else:
        idx = rng.randrange(len(colors)) if idx is None else idx
        num = counts[idx]
        ask = f"what is the probability of selecting a {colors[idx]} {noun}?"
        pool = {"complement": (f"found the probability that the {noun} is not "
                               f"{colors[idx]}", (N - num, N)),
                "over_rest": (f"divided by the {N - num:,} {nouns} that are not "
                              f"{colors[idx]} instead of by all {N:,}", (num, N - num))}
        for j, col in enumerate(colors):
            if j == idx:
                continue
            pool[f"other{j}"] = (f"counted the {col} {nouns} instead of the "
                                 f"{colors[idx]} ones", (counts[j], N))
            pool[f"over{j}"] = (f"divided by the {counts[j]:,} {col} {nouns} instead "
                                f"of by all {N:,} {nouns}", (num, counts[j]))
        prefer = [f"other{j}" for j in range(len(colors)) if j != idx] + ["complement"]

    if not 0 < num < N:
        raise ItemError("a probability of 0 or 1 is not what this question asks")
    if fmt == "spr":
        surface = "reduced"
    if surface == "decimal":
        places = exact_decimal(num, N, places)

    listed = _bag_list(counts, colors, noun, nouns, style)
    if style == "colon":
        intro = f"There are {N:,} {nouns} in {where}: {listed}."
    elif style == "contains":
        intro = f"{where.capitalize()} contains {listed}."
    else:
        intro = f"In {where}, there are {listed}."
    stem = f"{intro} If one of these {nouns} is selected at random, {ask}"
    key = render(num, N, surface, places)
    P = {"kind": "prob_bag", "counts": list(counts), "num": num,
         "surface": surface, "places": places}
    counted = (f"are neither {colors[neither[0]]} nor {colors[neither[1]]}"
               if neither else f"are {colors[idx]}")
    rationale = (f"{num:,} of the {N:,} {nouns} {counted}, so the probability is "
                 f"{key.plain()}.")
    if fmt == "spr":
        if not griddable(Q(num, N)):
            raise ItemError("this probability is not enterable in five characters")
        return spr("prob.bag", "counting", tier, seed, stem + GRID_NOTE, Q(num, N),
                   rationale, params=P)
    mistakes = [(why, render(a, b, surface, places))
                for why, (a, b) in pick(pool, wrongs or order_of(pool, prefer), wrongs)
                if b]
    return mcq("prob.bag", "counting", tier, seed, stem, key, mistakes, rng,
               rationale, params=P)


GRID_NOTE = " (Express your answer as a decimal or fraction, not as a percent.)"


# --------------------------------------------------------------- prob.subset

SUBSETS = {
    "planets": ("Of the {n} planets in our solar system, {k} are considered rocky.",
                "If a student randomly selects 1 of those {n} planets as a topic for "
                "a report, what is the probability that the selected planet will be "
                "rocky?", "planet", False,
                "{k} of the {n} planets are rocky."),
    "shipment": ("A store received a shipment of {n} {things}, {k} of which were "
                 "defective.",
                 "If {a} {thing} is randomly selected from this shipment, what is the "
                 "probability that it is defective?", "{thing}", True,
                 "{k} of the {n} {things} are defective."),
    "polygon": ("Each vertex of a {n}-sided polygon is labeled with one of the {n} "
                "letters A through {last}, with a different letter at each vertex.",
                "If one vertex is selected at random, what is the probability that "
                "the letter {pick} will be at the selected vertex?", "vertex", False,
                "Exactly 1 of the {n} vertices carries the letter {pick}."),
    "class": ("Of the {n} students in a class, {k} are left-handed.",
              "If one of these students is selected at random, what is the "
              "probability that the student is left-handed?", "student", False,
              "{k} of the {n} students are left-handed."),
    "shelf": ("Of the {n} books on a shelf, {k} are paperbacks.",
              "If one of these books is selected at random, what is the probability "
              "that the book is a paperback?", "book", False,
              "{k} of the {n} books are paperbacks."),
    "orchard": ("An orchard has {n} trees, {k} of which are apple trees.",
                "If one of these trees is selected at random, what is the probability "
                "that it is an apple tree?", "tree", False,
                "{k} of the {n} trees are apple trees."),
}
THINGS = [("MP3 player", "MP3 players"), ("light bulb", "light bulbs"),
          ("battery", "batteries"), ("phone charger", "phone chargers"),
          ("headphone set", "headphone sets")]


def subset(rng: random.Random, seed: int, *, scenario=None, n=None, k=None,
           letter=None, surface=None, places=None, fmt="mcq", wrongs=None,
           tier="easy"):
    """Of N things, k have a trait; find the probability of that trait."""
    scenario = scenario or rng.choice([s for s in SUBSETS if s != "planets"])
    intro, ask, unit, big, why = SUBSETS[scenario]
    if scenario == "planets":
        n, k = 8, 4
    elif scenario == "polygon":
        n = n or rng.randint(5, 20)
        k = 1
    elif big:
        n = n or rng.choice([100, 200, 250, 500, 1_000, 2_000])
        k = k or rng.randint(1, 20)
    else:
        n = n or rng.randint(8, 60)
        k = k or rng.randint(2, n - 2)
    if not 0 < k < n:
        raise ItemError("a probability of 0 or 1 is not what this question asks")
    thing, things = THINGS[rng.randrange(len(THINGS))]
    last = chr(ord("A") + n - 1)
    fill = {"n": f"{n:,}", "k": f"{k:,}", "thing": thing, "things": things,
            "last": last, "a": "an" if thing[0] in "aeiou" else "a",
            "pick": letter or chr(ord("A") + rng.randrange(min(n, 26)))}
    surface = "reduced" if fmt == "spr" else (surface or rng.choice(SURFACES))
    if surface == "decimal":
        places = exact_decimal(k, n, places)

    pool = {
        "one_over_total": (f"used 1 as the numerator -- the one item selected -- "
                           f"instead of the {k:,} that have the property", (1, n)),
        "one_over_part": (f"used the {k:,} as the denominator instead of the {n:,}",
                          (1, k)),
        "inverted": (f"inverted the fraction, dividing {n:,} by {k:,}", (n, k)),
        "complement": (f"found the probability of the other {n - k:,}", (n - k, n)),
        "over_rest": (f"divided by the {n - k:,} that do not instead of by all {n:,}",
                      (k, n - k)),
        "count": (f"gave the count {k:,} itself rather than a probability", (k, 1)),
        "shift1": (f"moved the decimal point one place", (k * 10, n)),
        "shift2": (f"moved the decimal point two places", (k * 100, n)),
    }
    stem = f"{intro.format(**fill)} {ask.format(**fill)}"
    key = render(k, n, surface, places)
    P = {"kind": "prob_bag", "counts": [k, n - k], "num": k, "surface": surface,
         "places": places}
    rationale = f"{why.format(**fill)} The probability is {key.plain()}."
    if fmt == "spr":
        if not griddable(Q(k, n)):
            raise ItemError("this probability is not enterable in five characters")
        return spr("prob.subset", "counting", tier, seed, stem + GRID_NOTE, Q(k, n),
                   rationale, params=P)
    prefer = ["one_over_total", "one_over_part", "inverted", "complement"]
    mistakes = []
    for why, (a, b) in pick(pool, wrongs or order_of(pool, prefer), wrongs):
        if surface == "decimal" and b != 1:
            mistakes.append((why, decimal(Q(a, b), exact_decimal(a, b, None))))
        elif surface == "decimal":
            mistakes.append((why, decimal(Q(a, b), 0)))
        else:
            mistakes.append((why, render(a, b, surface, places)))
    return mcq("prob.subset", "counting", tier, seed, stem, key, mistakes, rng,
               rationale, params=P)


# ------------------------------------------------------------- prob.data_set

TRAITS = {
    "negative": ("a negative number", "negative", lambda v: v < 0),
    "positive": ("a positive number", "positive", lambda v: v > 0),
    "even": ("an even number", "even", lambda v: v % 2 == 0),
    "odd": ("an odd number", "odd", lambda v: v % 2 != 0),
}


def data_set(rng: random.Random, seed: int, *, values=None, trait=None, size=None,
             fmt="mcq", wrongs=None, tier="easy"):
    """A short list of numbers is printed; how likely is one with a given trait?"""
    size = size or rng.randint(3, 7)
    values = values or sorted(rng.sample(range(-30, 31), size))
    trait = trait or rng.choice(sorted(TRAITS))
    phrase, adj, test = TRAITS[trait]
    n = len(values)
    hits = sum(1 for v in values if test(v))
    if not 0 < hits < n:
        raise ItemError("every number, or none of them, has this property")
    listed = ", ".join(f"{v:,}".replace("-", "−") for v in values)
    word = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}[n]
    stem = (f"{listed}\nA data set of {word} numbers is shown. If a number from this "
            f"data set is selected at random, what is the probability of selecting "
            f"{phrase}?")
    key = reduced(Q(hits, n))
    P = {"kind": "prob_data_set", "values": list(values), "trait": trait}
    rationale = (f"{hits} of the {n} numbers listed "
                 f"{'is' if hits == 1 else 'are'} {adj}, so the probability is "
                 f"{key.plain()}.")
    if fmt == "spr":
        if not griddable(Q(hits, n)):
            raise ItemError("this probability is not enterable in five characters")
        return spr("prob.data_set", "counting", tier, seed, stem + GRID_NOTE,
                   Q(hits, n), rationale, params=P)
    pool = {
        "none": (f"read none of the numbers as {adj}", (0, 1)),
        "all": (f"read every number as {adj}", (1, 1)),
        "complement": (f"counted the numbers that are not {adj}", (n - hits, n)),
        "over_hits": (f"divided the count of the other numbers by the {hits} that "
                      f"are {adj}", (n - hits, hits)),
        "one": (f"used 1 as the numerator instead of the {hits} that qualify", (1, n)),
    }
    mistakes = [(why, reduced(Q(a, b))) for why, (a, b) in
                pick(pool, wrongs or order_of(pool, ["none", "complement", "all"]),
                     wrongs)]
    return mcq("prob.data_set", "counting", tier, seed, stem, key, mistakes, rng,
               rationale, params=P, signed=True)


# ------------------------------------------------------ prob.count_from_prob

COUNTERS = [
    ("marbles", "A bag contains a total of {n} marbles. A marble is to be chosen at "
     "random from the bag.", "If the probability that a {adj} marble will be chosen "
     "is {p}, how many marbles in the bag are {adj}?", "marble", ["blue", "red",
     "green", "yellow"]),
    ("club", "A club has {n} members.", "If the probability that a member selected at "
     "random plays the {adj} is {p}, how many members play the {adj}?", "member",
     ["guitar", "violin", "cello", "flute"]),
    ("crates", "A warehouse holds {n} crates.", "If the probability that a crate "
     "selected at random is {adj} is {p}, how many of the crates are {adj}?", "crate",
     ["empty", "sealed", "damaged", "refrigerated"]),
]


def count_from_prob(rng: random.Random, seed: int, *, mode=None, n=None, p=None,
                    p2=None, scenario=None, before=None, unit=None, fmt=None,
                    wrongs=None, tier="easy"):
    """The total and the probability are given; the count is the answer."""
    mode = mode or rng.choice(("single", "third", "round"))
    if mode == "round":
        n = n or rng.randint(40, 300)
        before = before or n - rng.randint(5, 40)
        p = q(p) if p is not None else Q(rng.randint(15, 85), 100)
        unit = unit or rng.choice(["million", "thousand"])
        exact = p * n
        key = unambiguous(exact, 1)
        stem = (f"On May 10, 2015, there were {before:,} {unit} Internet subscribers "
                f"in a certain country. By September 30, 2015, the number of Internet "
                f"subscribers in that country had increased to {n:,} {unit}. If an "
                f"Internet subscriber in that country on September 30, 2015, is "
                f"selected at random, the probability that the person selected was a "
                f"subscriber of a particular provider is {_dp(p)}. There were p "
                f"{unit} subscribers of that provider in that country on September "
                f"30, 2015. To the nearest integer, what is the value of p ?")
        rationale = (f"{_dp(p)} of {n:,} is {_dp(exact)}, which is {key} to the "
                     f"nearest integer.")
        P = {"kind": "prob_count", "mode": mode, "n": n, "p": [p.numerator,
             p.denominator], "p2": None}
        return spr("prob.count_from_prob", "counting", tier, seed, stem, key,
                   rationale, params=P)

    name, intro, ask, noun, adjs = (COUNTERS[rng.randrange(len(COUNTERS))]
                                    if scenario is None else
                                    next(c for c in COUNTERS if c[0] == scenario))
    if mode == "third":
        n = n or rng.choice([100, 150, 200, 250, 275, 300, 400, 500])
        p = q(p) if p is not None else Q(rng.randint(20, 55), 100)
        p2 = q(p2) if p2 is not None else Q(rng.randint(15, 40), 100)
        rest = 1 - p - p2
        if rest <= 0 or (rest * n).denominator != 1:
            raise ItemError("the three groups do not split into whole numbers")
        key = rest * n
        stem = (f"At a conference, there are a total of {n:,} attendees. Each attendee "
                f"is assigned to either group A, group B, or group C. If one of these "
                f"attendees is selected at random, the probability of selecting an "
                f"attendee who is assigned to group A is {_dp(p)} and the probability "
                f"of selecting an attendee who is assigned to group B is {_dp(p2)}. "
                f"How many attendees are assigned to group C?")
        rationale = (f"The probability of group C is 1 − {_dp(p)} − "
                     f"{_dp(p2)} = {_dp(rest)}, and {_dp(rest)} of {n:,} is "
                     f"{int(key):,}.")
        P = {"kind": "prob_count", "mode": mode, "n": n,
             "p": [p.numerator, p.denominator], "p2": [p2.numerator, p2.denominator]}
        return spr("prob.count_from_prob", "counting", tier, seed, stem, key,
                   rationale, params=P)

    n = n or rng.choice([20, 25, 40, 50, 60, 80, 100, 120, 200])
    p = q(p) if p is not None else Q(rng.randint(5, 95), 100)
    if (p * n).denominator != 1:
        raise ItemError("this probability does not give a whole number of items")
    key = p * n
    if not 0 < key < n:
        raise ItemError("a probability of 0 or 1 is not what this question asks")
    adj = rng.choice(adjs)
    stem = f"{intro.format(n=f'{n:,}')} {ask.format(adj=adj, p=_dp(p))}"
    digits = int(str(_dp(p)).replace("0.", "").lstrip("0") or "0")
    P = {"kind": "prob_count", "mode": "single", "n": n,
         "p": [p.numerator, p.denominator], "p2": None}
    rationale = f"{_dp(p)} of {n:,} is {int(key):,}."
    if fmt == "spr":
        return spr("prob.count_from_prob", "counting", tier, seed, stem, key,
                   rationale, params=P)
    from ..values import count as C
    pool = {
        "prob_as_count": (f"read the probability {_dp(p)} as a count of {digits:,}",
                          digits),
        "complement": (f"found how many are not {adj}", int(n - key)),
        "total_minus_digits": (f"subtracted the digits of {_dp(p)} from the total "
                               f"{n:,}", int(n - digits)),
        "tenth": (f"took one tenth of the total", n // 10 if n % 10 == 0 else None),
        "half_of_key": (f"halved the answer", int(key) // 2 if key % 2 == 0 else None),
    }
    mistakes = [(why, C(v)) for why, v in
                pick(pool, wrongs or order_of(pool, ["prob_as_count", "complement",
                                                     "total_minus_digits"]), wrongs)
                if v and 0 < v]
    return mcq("prob.count_from_prob", "counting", tier, seed, stem, C(key),
               mistakes, rng, rationale, params=P)


def _dp(v) -> str:
    """A probability written the way the stem writes it: 0.35, 0.4, 1."""
    v = q(v)
    if v.denominator == 1:
        return str(v.numerator)
    for p in range(1, 7):
        if (v * 10 ** p).denominator == 1:
            s = f"{float(v):.{p}f}"
            return s
    raise ItemError("this probability does not print as a short decimal")


# -------------------------------------------------------------- prob.symbolic

SHELVES = [("nonfiction books", "fiction books", "bookshelf", "books", "book"),
           ("red marbles", "blue marbles", "bag", "marbles", "marble"),
           ("blue pens", "black pens", "box", "pens", "pen"),
           ("green tiles", "white tiles", "crate", "tiles", "tile"),
           ("small candles", "large candles", "shelf", "candles", "candle")]


def symbolic(rng: random.Random, seed: int, *, which=None, k=None, ask_first=None,
             wrongs=None, tier="easy"):
    """n of one kind and a stated number of another; the answer is in terms of n."""
    a, b, place, plural, one = (SHELVES[rng.randrange(len(SHELVES))] if which is None
                                else next(s for s in SHELVES if s[0] == which))
    k = k or rng.randint(3, 40)
    ask_first = rng.choice((True, False)) if ask_first is None else ask_first
    want, other = (a, b) if ask_first else (b, a)
    want_s = want.rsplit(" ", 1)[0]
    stem = (f"There are n {a} and {k:,} {b} on a {place}. If one of these {plural} is "
            f"selected at random, what is the probability of selecting a {want_s} "
            f"{one}, in terms of n ?")
    top, bottom = ("n", f"{k:,}") if ask_first else (f"{k:,}", "n")
    key = f"{top}/(n + {k:,})"
    pool = {
        "over_other": (f"used the number of {other} as the total instead of the whole "
                       f"collection", f"{top}/{bottom}"),
        "inverted": (f"inverted the fraction", f"{bottom}/{top}"),
        "other_over_total": (f"found the probability of selecting a "
                             f"{other.rsplit(' ', 1)[0]} {one} instead",
                             f"{bottom}/(n + {k:,})"),
        "total_over": (f"put the total on top of the count instead of underneath",
                       f"(n + {k:,})/{top}"),
    }
    P = {"kind": "prob_symbolic", "k": k, "ask_first": bool(ask_first)}
    rationale = (f"There are n + {k:,} {plural} in all and {top} of them are the ones "
                 f"asked about, so the probability is {key}.")
    wrong = pick(pool, wrongs or order_of(pool, ["over_other", "inverted",
                                                 "other_over_total"]), wrongs)
    return text_mcq("prob.symbolic", "counting", tier, seed, stem, key, wrong, rng,
                    rationale, params=P)


# ------------------------------------------------------------ prob.rate_share

RATES = [("customers register for new accounts at a social media website",
          "new accounts", "registered"),
         ("visitors enter a museum", "visitors", "admitted"),
         ("packages arrive at a sorting centre", "packages", "sorted"),
         ("messages are posted to a forum", "messages", "posted")]


def rate_share(rng: random.Random, seed: int, *, rate=None, total=None, days=None,
               which=None, wrongs=None, tier="medium"):
    """A steady daily rate; what share of a target total falls in the first d days?"""
    verb, things, done = (RATES[rng.randrange(len(RATES))] if which is None
                          else next(r for r in RATES if r[1] == which))
    rate = rate or rng.choice([200, 250, 400, 500, 800, 1_000, 1_200, 1_500, 2_000])
    span = days or rng.randint(2, 12)
    total = total or rate * rng.choice([20, 25, 40, 50, 60, 80, 100])
    if total % rate or span >= total // rate:
        raise ItemError("the target is not a whole number of days at this rate")
    all_days = total // rate
    num, den = rate * span, total
    key = reduced(Q(num, den))
    scaled = total // 1_000 if total % 1_000 == 0 else None
    pool = {
        "one_over_days": (f"gave one over the {span} days instead of the share of the "
                          f"whole target", (1, span)),
        "one_day": (f"found the share {done} in a single day", (rate, total)),
        "days_over_scaled": (f"read {total:,} as {scaled} and divided the {span} days "
                             f"by it", (span, scaled) if scaled else (0, 0)),
        "days_over_all": (f"divided the {span} days by the {rate:,} {things} a day "
                          f"rather than by the {all_days} days the target takes",
                          (span, rate)),
        "complement": (f"found the share {done} after the first {span} days",
                       (total - num, total)),
    }
    stem = (f"If {rate:,} {verb} every day, what fraction of the first {total:,} "
            f"{things} are {done} in the first {span} days?")
    P = {"kind": "prob_rate", "rate": rate, "total": total, "days": span}
    rationale = (f"In {span} days, {rate:,} × {span} = {num:,} of the {total:,} "
                 f"{things} are {done}, so the fraction is {key.plain()}.")
    mistakes = [(why, reduced(Q(a, b))) for why, (a, b) in
                pick(pool, wrongs or order_of(pool, ["one_over_days", "one_day",
                                                     "days_over_scaled"]), wrongs)
                if b]
    return mcq("prob.rate_share", "counting", tier, seed, stem, key, mistakes, rng,
               rationale, params=P)
