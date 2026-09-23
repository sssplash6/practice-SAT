"""One percent, one step: the seven ways the source set asks it.

Everything here moves between three quantities -- a whole, a part and a
percent -- and which one is missing decides the template:

    percent_of         whole and percent  -> part
    find_percent       whole and part     -> percent
    increase_decrease  whole and percent  -> the whole after the change
    reverse            the result         -> the whole it came from
    change             two wholes         -> the percent between them
    multiplier         percent <-> the number you multiply by
    expression         the same step written as an expression, not a value

The misconceptions are the point. A percent item goes wrong in a small
number of well-known ways -- the percent subtracted as though it were a
count, the decimal point one place out, the part and the whole the wrong way
round, the reverse of the change instead of the change -- and each of those
is a named option below, not a number invented to fill a slot.
"""

from __future__ import annotations

import random

from ....item import Item, ItemError
from ..values import (Q, dec, mcq, pick, places_needed, q, snap, spr,
                      text_mcq, unambiguous)

__all__ = ["percent_of", "find_percent", "increase_decrease", "reverse",
           "change", "multiplier", "expression"]

# ------------------------------------------------------------------ contexts

INVENTORY = [
    ("objects", "box", "balls", False),
    ("blocks", "container", "green", True),
    ("marbles", "jar", "blue", True),
    ("tiles", "crate", "chipped", True),
    ("seedlings", "tray", "flowering", True),
    ("bolts", "bin", "stainless steel", True),
    ("tickets", "roll", "unsold", True),
    ("beads", "bag", "wooden", True),
    ("cartons", "pallet", "damaged", True),
    ("samples", "rack", "labeled", True),
]

PROGRAMS = ["an interior design program", "a marine biology program",
            "a welding certificate program", "a community chorus",
            "an evening ceramics class", "a paramedic training program"]

DINERS = [("Rita", "she"), ("Marcus", "he"), ("Priya", "she"),
          ("Dominic", "he"), ("Yara", "she"), ("Leon", "he")]
EATERIES = ["a restaurant", "a diner", "a bistro", "a cafe"]
TIPPED = ["waiter", "server", "barista", "delivery driver", "hairdresser"]

SUBSTANCES = [("alloy", "phosphorus"), ("fertilizer", "cadmium"),
              ("solvent", "benzene"), ("glaze", "lead"),
              ("feed additive", "arsenic"), ("pigment", "mercury")]

WORKERS = [("Lani", "her"), ("Omar", "his"), ("Tess", "her"),
           ("Ravi", "his"), ("Noor", "her")]

SHOPS = ["a clothing store", "a hardware store", "a garden center",
         "a bookstore", "a sporting goods store"]
GARMENTS = ["jacket", "raincoat", "backpack", "pair of boots", "lamp", "kettle"]

TOWNS = ["Fairview", "Redbank", "Glenmore", "Ashton", "Port Clare"]
COUNTED = ["households", "registered voters", "library card holders",
           "licensed drivers", "season ticket holders"]

COLLECTIONS = [("coins", "collection"), ("stamps", "album"),
               ("fossils", "display case"), ("records", "crate")]

PCTS = [2, 4, 5, 6, 8, 10, 12, 15, 16, 18, 20, 24, 25, 30, 32, 35, 40, 45,
        48, 50, 55, 60, 64, 65, 70, 72, 75, 80, 85, 88, 90, 92, 95, 96]


def _article(word: str) -> str:
    return "an" if word[0].lower() in "aeiou" else "a"


# ------------------------------------------------------------- PERCENT OF

def percent_of(rng: random.Random, seed: int, *, pct=None, n=None, frame=None,
               fmt=None, round_to=None, cents=None, places=None, ctx=None,
               wrongs=None) -> Item:
    """`p`% of `n`. The part is missing and the whole and the percent are given."""
    frame = frame or rng.choices(
        ["bare", "inventory", "of_last_year", "tip_bill", "rate_closest",
         "workday", "by_mass"], weights=[6, 6, 3, 3, 2, 2, 2])[0]
    style, order = "plain", None
    difficulty = "easy"

    if frame == "bare":
        pct = pct if pct is not None else rng.choice(PCTS)
        n = n if n is not None else rng.choice([100, 100] + list(range(20, 990, 10)))
        stem = f"What is {dec(pct, places_needed(pct))}% of {dec(n, 0)}?"
        order = ["complement", "whole_less_percent", "part_less_percent",
                 "whole_plus_part", "doubled", "ten_times"]
    elif frame == "inventory":
        noun, holder, kind, adj = ctx or rng.choice(INVENTORY)
        pct = pct if pct is not None else rng.choice(PCTS)
        n = n if n is not None else rng.randrange(50, 900, 10)
        tail = (f"How many {noun} in the {holder} are {kind}?" if adj
                else f"How many {kind} are in the {holder}?")
        stem = (f"There are {dec(n, 0)} {noun} in {_article(holder)} {holder}. "
                f"Of these {noun}, {dec(pct, places_needed(pct))}% are {kind}. {tail}")
        order = ["whole_less_percent", "percent_itself", "complement",
                 "part_less_percent", "whole_plus_part"]
    elif frame == "of_last_year":
        program = rng.choice(PROGRAMS)
        pct = pct if pct is not None else rng.choice([104, 112, 115, 120, 125, 130,
                                                      135, 140, 147, 150, 160, 175])
        n = n if n is not None else rng.randrange(100, 900, 20)
        stem = (f"Last year, {dec(n, 0)} students enrolled in {program}. This year, "
                f"the number of students enrolled is {dec(pct, places_needed(pct))}% of "
                f"last year's number. How many students are enrolled in the "
                f"{program.split(' ', 1)[1]} this year?")
        order = ["whole_plus_percent", "whole_plus_excess", "doubled", "complement"]
        difficulty = "medium"
    elif frame == "tip_bill":
        name, pronoun = rng.choice(DINERS)
        place = rng.choice(EATERIES)
        pct = pct if pct is not None else rng.choice([15, 18, 20, 25])
        n = n if n is not None else Q(rng.randrange(1000, 9000, 50), 100)
        style = "money"
        stem = (f"{name}'s total bill at {place} was ${dec(n, 2)}, including tax. "
                f"If {pronoun} left a tip of {dec(pct, 0)}% of the total bill, what was "
                f"the amount of the tip?")
        order = ["standard_eighteen", "tenth_of_whole", "standard_tip", "complement"]
    elif frame == "rate_closest":
        job = rng.choice(TIPPED)
        pct = pct if pct is not None else rng.choice([15, 18, 20])
        n = n if n is not None else Q(rng.randrange(2000, 9900, 10), 100)
        style, cents = "money", True if cents is None else cents
        round_to = round_to if round_to is not None else 2
        stem = (f"A {job} receives tips from each customer. On average, the tip is "
                f"{dec(pct, 0)}% of the customer's bill. At this rate, which of the "
                f"following is closest to the tip the {job} can expect when a customer "
                f"has a bill that is ${dec(n, 2)}?")
        order = ["tenth_of_whole", "standard_eighteen", "double_the_rate",
                 "quarter_the_rate"]
    elif frame == "workday":
        name, pronoun = rng.choice(WORKERS)
        pct = pct if pct is not None else rng.choice([5, 10, 12, 15, 20, 25, 30, 40, 50])
        n = n if n is not None else rng.choice([6, 7, 8, 9, 10])
        doing = rng.choice(["in meetings", "on the telephone", "training new staff",
                            "answering email"])
        stem = (f"{name} spent {dec(pct, 0)}% of {pronoun} {dec(n, 0)}-hour workday "
                f"{doing}. How many minutes of {pronoun} workday did {name} spend "
                f"{doing}?")
        order = ["answer_in_hours", "percent_itself", "percent_of_one_hour",
                 "minutes_remaining"]
        difficulty = "medium"
    else:                                                      # by_mass
        substance, element = ctx or rng.choice(SUBSTANCES)
        pct = pct if pct is not None else rng.choice(
            [Q(1, 1000), Q(1, 100), Q(1, 20), Q(1, 10), Q(1, 4), Q(1, 2), 1, 2])
        n = n if n is not None else rng.randrange(40, 400, 10)
        stem = (f"According to a set of standards, a certain type of {substance} can "
                f"contain a maximum of {dec(pct, places_needed(pct, 5))}% {element} by "
                f"mass. If a sample of this {substance} has a mass of {dec(n, 0)} grams, "
                f"what is the maximum mass, in grams, of {element} the sample can contain "
                f"to meet these standards?")
        order = ["ten_times", "tenth_of_part", "percent_itself"]
        difficulty = "hard"

    pct, n = q(pct), q(n)
    part = n * pct / 100
    key = part * 60 if frame == "workday" else part
    if round_to:
        key = unambiguous(key, round_to)
    if frame in ("inventory", "of_last_year") and key.denominator != 1:
        raise ItemError("a count of people or objects has to come out whole")
    if frame == "workday" and key.denominator != 1:
        raise ItemError("a workday is measured in whole minutes")
    if key <= 0:
        raise ItemError("the part has to be a positive amount")

    P = {"kind": "pct_of", "p": float(pct), "n": float(n), "frame": frame,
         "round_to": float(round_to) if round_to else None}
    pool = {
        "complement": ("found the part that is not counted instead of the part asked for",
                       n - part),
        "whole_less_percent": ("subtracted the percent as though it were a count of the "
                               f"{'items' if frame != 'bare' else 'whole'}", n - pct),
        "part_less_percent": ("subtracted the percent from the part after finding it",
                              part - pct),
        "whole_plus_part": ("added the part to the whole instead of reporting the part",
                            n + part),
        "whole_plus_percent": ("added the percent to the whole as though it were a count",
                               n + pct),
        "whole_plus_excess": ("added only the amount by which the percent passes 100 as "
                              "a count", n + (pct - 100)),
        "doubled": ("doubled the part", 2 * part),
        "ten_times": ("moved the decimal point one place, using "
                      f"{dec(pct * 10, places_needed(pct * 10, 5))}% of the whole", 10 * part),
        "tenth_of_part": ("moved the decimal point one place the other way, using "
                          f"{dec(pct / 10, places_needed(pct / 10, 5))}% of the whole", part / 10),
        "percent_itself": ("gave the percent itself as the answer", pct),
        "tenth_of_whole": ("took a tenth of the bill, the tip that is quickest to work "
                           "out, rather than the stated rate", n / 10),
        "standard_tip": ("used the customary 15% rather than the rate the item states",
                         n * Q(15, 100)),
        "standard_eighteen": ("used the 18% many restaurants suggest rather than the rate "
                              "the item states", n * Q(18, 100)),
        "double_the_rate": (f"doubled the rate, tipping {dec(pct * 2, 0)}% of the bill",
                            n * pct / 50),
        "quarter_the_rate": ("moved the decimal point in the rate, tipping "
                             f"{dec(pct, 1)}% as {dec(pct / 10, places_needed(pct / 10, 3))}%",
                             n * pct / 1000),
        "answer_in_hours": ("gave the time in hours and did not convert it to minutes", part),
        "percent_of_one_hour": ("took the percent of a single hour instead of the whole "
                                "workday", pct * Q(60, 100)),
        "minutes_remaining": ("gave the minutes left over rather than the minutes spent",
                              n * 60 - part * 60),
    }
    mistakes = [(why, snap(value, round_to) if round_to else value)
                for why, value in pick(pool, order, wrongs)]

    rationale = (f"{dec(pct, places_needed(pct, 5))}% of {dec(n, places_needed(n))} is "
                 f"{dec(pct, places_needed(pct, 5))}/100 x {dec(n, places_needed(n))} = "
                 f"{dec(part, places_needed(part, 5))}"
                 + (f", and {dec(part, places_needed(part, 5))} hours is "
                    f"{dec(key, places_needed(key, 5))} minutes." if frame == "workday"
                    else "."))
    skill = "percent of a number"
    fmt = fmt or ("spr" if rng.random() < 0.22 else "mcq")
    if fmt == "spr":
        return spr("pct.of", skill, difficulty, seed, stem, key, rationale,
                   mistakes=mistakes, params=P)
    return mcq("pct.of", skill, difficulty, seed, stem, key, mistakes, rng, rationale,
               style=style, places=places, cents=cents, params=P)


# ----------------------------------------------------------- FIND PERCENT

def find_percent(rng: random.Random, seed: int, *, part=None, whole=None, frame=None,
                 fmt=None, places=None, ctx=None, wrongs=None) -> Item:
    """What percent of the whole the part is."""
    frame = frame or rng.choice(["what_percentage_of", "of_n_things",
                                 "is_p_percent_of", "nearest_whole"])
    whole = q(whole) if whole is not None else q(rng.randrange(20, 900, 5))
    if part is None:
        part = whole * q(rng.choice(PCTS)) / 100
        if part.denominator != 1:
            part = q(round(float(part)))
    part = q(part)
    if part <= 0 or part >= 4 * whole:
        raise ItemError("the part has to be a sensible share of the whole")
    key = 100 * part / whole
    difficulty = "easy"

    if frame == "what_percentage_of":
        stem = f"What percentage of {dec(whole, 0)} is {dec(part, 0)}?"
    elif frame == "of_n_things":
        noun, holder, kind, adj = ctx or rng.choice(INVENTORY)
        tail = (f"What percentage of the {noun} are {kind}?" if adj
                else f"What percentage of the {noun} are {kind}?")
        stem = (f"Of {dec(whole, 0)} {noun}, {dec(part, 0)} are {kind}. {tail}")
    elif frame == "is_p_percent_of":
        stem = f"{dec(part, 0)} is p% of {dec(whole, 0)}. What is the value of p ?"
    else:                                                      # nearest_whole
        noun, holder, kind, adj = ctx or rng.choice(INVENTORY)
        places = 0 if places is None else places
        key = unambiguous(key, 1)
        stem = (f"A shipment contains {dec(whole, 0)} {noun}, of which {dec(part, 0)} "
                f"are {kind}. To the nearest whole percent, what percent of the {noun} "
                f"in the shipment are {kind}?")
        difficulty = "medium"

    if places is None and places_needed(key, 6) > 2:
        raise ItemError("this percent does not print in two decimals")
    if places is not None:
        key = unambiguous(key, Q(1, 10) ** places)
    P = {"kind": "pct_find", "part": float(part), "whole": float(whole),
         "round": float(places) if places is not None else None}
    # a count in the thousands is read off the page in thousands -- a student
    # who subtracts 828,000 from 900,000 and offers the answer as a percent
    # writes 72, not 72,000, because 72 is the number in front of them
    scaled = ((whole - part) / 1000 if whole % 1000 == 0 and part % 1000 == 0
              and 0 < whole - part <= 250000 else None)
    pool = {
        "complement": ("found the percent that are not counted instead", 100 - key),
        "part_as_percent": ("read the part itself as the percent",
                            part if part <= 250 else None),
        "difference": ("subtracted the part from the whole and read the difference as "
                       "the percent", whole - part if whole - part <= 250 else None),
        "difference_in_thousands": ("subtracted the part from the whole and read the "
                                    "difference, in the thousands the counts are "
                                    "written in, as the percent", scaled),
        "inverted": ("divided the whole by the part instead of the part by the whole",
                     100 * whole / part if 100 * whole <= 500 * part else None),
        "ten_times": ("moved the decimal point one place", key * 10),
        "tenth": ("moved the decimal point one place the other way", key / 10),
        "halved": ("halved the percent", key / 2),
        "doubled": ("doubled the percent", key * 2),
    }
    order = ["complement", "part_as_percent", "difference", "difference_in_thousands",
             "inverted", "ten_times", "tenth", "halved", "doubled"]
    mistakes = pick(pool, order, wrongs)
    exact = 100 * part / whole
    rationale = (f"{dec(part, places_needed(part))} out of {dec(whole, places_needed(whole))} is "
                 f"{dec(part, places_needed(part))}/{dec(whole, places_needed(whole))} = "
                 f"{dec(exact, places_needed(exact, 4))}%"
                 + (f", which is {dec(key, places_needed(key, 4))}% to the nearest whole "
                    "percent." if exact != key else "."))
    fmt = fmt or ("spr" if rng.random() < 0.3 else "mcq")
    if fmt == "spr":
        return spr("pct.find_percent", "a part as a percent", difficulty, seed, stem,
                   key, rationale, mistakes=mistakes, params=P)
    return mcq("pct.find_percent", "a part as a percent", difficulty, seed, stem, key,
               mistakes, rng, rationale, style="percent", places=places, params=P)


# ------------------------------------------------------ INCREASE / DECREASE

def increase_decrease(rng: random.Random, seed: int, *, n=None, pct=None, up=None,
                      frame=None, fmt=None, round_to=None, cents=None, places=None,
                      ctx=None, wrongs=None) -> Item:
    """The whole after it has been moved by a percent of itself."""
    frame = frame or rng.choices(["bare", "sales_tax", "discount", "projection"],
                                 weights=[4, 3, 3, 3])[0]
    style, difficulty = "plain", "easy"
    up = (frame != "discount") if up is None else up

    if frame == "bare":
        pct = q(pct if pct is not None else rng.choice(PCTS))
        n = n if n is not None else rng.randrange(20, 900, 5)
        word = "greater" if up else "less"
        stem = f"What number is {dec(pct, places_needed(pct))}% {word} than {dec(n, 0)} ?"
        order = ["undo_the_change", "undo_the_other_way", "whole_plus_result",
                 "percent_as_count", "wrong_direction"]
    elif frame == "sales_tax":
        thing = rng.choice(["shirt", "jacket", "toaster", "desk lamp", "backpack",
                            "bicycle helmet"])
        pct = q(pct if pct is not None else rng.choice([3, 4, 5, 6, Q(15, 2), 8]))
        n = n if n is not None else rng.randrange(10, 300, 5)
        style = "money"
        stem = (f"The cost of a certain {thing} is ${dec(n, places_needed(n))} before a "
                f"{dec(pct, places_needed(pct))}% sales tax is added. What is the total "
                f"cost, including sales tax, to purchase the {thing}?")
        # only the three decimal-place slips: a whole-dollar near-miss would be
        # picked ahead of them by surface form and print the whole item without
        # cents, which is not how a price is written
        order = ["percent_as_count", "percent_as_dimes", "percent_as_cents"]
    elif frame == "discount":
        shop, thing = rng.choice(SHOPS), rng.choice(GARMENTS)
        pct = q(pct if pct is not None else rng.choice([10, 15, 20, 25, 30, 40, 50, 60]))
        n = n if n is not None else rng.randrange(10, 300, 5)
        style = "money"
        stem = (f"During a sale, the original prices of all the items in {shop} have "
                f"been reduced by {dec(pct, places_needed(pct))}%. What is the sale price "
                f"of a {thing} with an original price of ${dec(n, places_needed(n))} ?")
        order = ["percent_as_count", "change_only", "wrong_direction",
                 "percent_as_dimes", "undo_the_change"]
    else:                                                      # projection
        town, counted = rng.choice(TOWNS), rng.choice(COUNTED)
        pct = q(pct if pct is not None else rng.choice(PCTS))
        y0 = rng.choice([2008, 2010, 2012, 2014, 2016])
        span = rng.choice([5, 8, 10])
        n = n if n is not None else rng.randrange(11000, 900000, 1000)
        round_to = round_to if round_to is not None else 100
        word = "increase" if up else "decrease"
        stem = (f"There were approximately {dec(n, 0)} {counted} in {town} in {y0}. A "
                f"planning report has projected that this number will {word} by "
                f"{dec(pct, places_needed(pct))}% from {y0} to {y0 + span}. Of the "
                f"following, which is closest to the number of {counted} the report has "
                f"projected for {town} in {y0 + span}?")
        order = ["percent_as_count_thousands", "percent_as_count_hundreds",
                 "percent_decimal_slip", "change_only", "wrong_direction",
                 "percent_as_count"]
        difficulty = "medium"

    n = q(n)
    ratio = 1 + pct / 100 if up else 1 - pct / 100
    if ratio <= 0:
        raise ItemError("a decrease of a hundred percent or more leaves nothing")
    key = n * ratio
    if round_to:
        key = unambiguous(key, round_to)
    P = {"kind": "pct_shift", "n": float(n), "p": float(pct), "up": up,
         "round_to": float(round_to) if round_to else None}
    sign = 1 if up else -1
    big = n >= 10000 and n % 1000 == 0          # a number the page writes in thousands
    pool = {
        "undo_the_change": ("worked backwards, treating the given number as the result "
                            "of the change rather than the start of it", n / ratio),
        "undo_the_other_way": ("worked backwards and reversed the direction as well",
                               n / (1 - sign * pct / 100)),
        "whole_plus_result": ("added the changed number to the original instead of "
                              "reporting it", n + n * ratio),
        "percent_as_count": (f"{'added' if up else 'subtracted'} the percent as though it "
                             "were a count", n + sign * pct),
        "percent_as_dimes": ("moved the decimal point one place when converting the "
                             "percent", n + sign * pct / 10),
        "percent_as_cents": ("moved the decimal point two places the wrong way when "
                             "converting the percent", n + sign * pct / 100),
        "change_only": ("gave the size of the change instead of the amount after it",
                        n * pct / 100),
        "wrong_direction": (f"{'subtracted' if up else 'added'} the change instead of "
                            f"{'adding' if up else 'subtracting'} it",
                            n * (1 - sign * pct / 100)),
        "percent_decimal_slip": (f"used {dec(pct / 10, places_needed(pct / 10, 3))}% "
                                 f"instead of {dec(pct, places_needed(pct))}%",
                                 n * (1 + sign * pct / 1000)),
        # a population written as 113,000 is read as "113 thousand", and the
        # percent gets added to it at whichever place value the reader is
        # working in: 113 + 29 thousand, or 113,000 + 29 hundred
        "percent_as_count_thousands": (
            f"{'added the percent to' if up else 'subtracted the percent from'} the count "
            f"of thousands, as though {dec(n, 0)} were just {dec(n / 1000, 0)}",
            n + sign * pct * 1000 if big else None),
        "percent_as_count_hundreds": (
            f"{'added the percent to' if up else 'subtracted the percent from'} the count "
            f"of hundreds, as though {dec(n, 0)} were just {dec(n / 100, 0)}",
            n + sign * pct * 100 if big else None),
    }
    mistakes = [(why, snap(value, round_to) if round_to else value)
                for why, value in pick(pool, order, wrongs)]

    rationale = (f"{dec(n, places_needed(n))} x "
                 f"{dec(ratio, places_needed(ratio, 4))} = "
                 f"{dec(key, places_needed(key, 4))}.")
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    if fmt == "spr":
        return spr("pct.increase_decrease", "a percent change applied", difficulty, seed,
                   stem, key, rationale, mistakes=mistakes, params=P)
    return mcq("pct.increase_decrease", "a percent change applied", difficulty, seed,
               stem, key, mistakes, rng, rationale, style=style, places=places,
               cents=cents, params=P)


# ----------------------------------------------------------------- REVERSE

def reverse(rng: random.Random, seed: int, *, result=None, pct=None, frame=None,
            fmt=None, ask="original", round_to=None, places=None, ctx=None,
            wrongs=None) -> Item:
    """The whole is missing: the item gives what is left of it, or all of it plus more."""
    frame = frame or rng.choice(["is_p_of", "is_p_of", "increased_to", "removed_remained"])
    pct = q(pct if pct is not None else rng.choice(PCTS))
    difficulty = "medium"
    style = "plain"

    if frame == "is_p_of":
        if result is None:                    # build from the whole, so n comes out whole
            result = q(rng.randrange(20, 2000, 5)) * pct / 100
        result = q(result)
        key = 100 * result / pct
        if result.denominator != 1 or key.denominator != 1:
            raise ItemError("both the part and the whole have to be whole numbers")
        stem = (f"{dec(result, 0)} is {dec(pct, places_needed(pct))}% of what number?")
        order = ["part_over_percent", "part_less_percent", "part_plus_percent",
                 "percent_of_part", "halved"]
        difficulty = "easy"
    elif frame == "increased_to":
        pct = q(pct if pct is not None else rng.choice([4, 5, 6, 8, 10, 12, 15, 20, 25]))
        if result is None:                    # build from n, so n comes back out whole
            result = q(rng.randrange(20, 900, 5)) * (1 + pct / 100)
        result = q(result)
        key = result / (1 + pct / 100)
        # the distractors are rounded, the way the source item rounds them, but the
        # answer itself is exact or the draw is thrown away
        round_to = round_to if round_to is not None else 1
        if result.denominator != 1 or key.denominator != 1:
            raise ItemError("the number before the increase has to be a whole number")
        stem = (f"A number n is increased {dec(pct, places_needed(pct))}%. If the result "
                f"is {dec(result, 0)}, what is the value of n ?")
        order = ["increase_again", "decrease_instead", "decimal_multiplier",
                 "result_less_percent", "result_over_percent"]
    else:                                                      # removed_remained
        noun, holder, kind, adj = ctx or rng.choice(INVENTORY)
        pct = q(pct if pct is not None else rng.choice([10, 20, 25, 30, 40, 50, 60, 75, 80]))
        result = result if result is not None else rng.randrange(40, 900, 4)
        result = q(result)
        original = result / (1 - pct / 100)
        if original.denominator != 1:
            raise ItemError("the original count has to be a whole number of items")
        key = original - result if ask == "removed" else original
        round_to = round_to if round_to is not None else 1
        want = ("How many " + noun + " were removed from the group?" if ask == "removed"
                else "How many " + noun + " were originally in the group?")
        stem = (f"After {dec(pct, places_needed(pct))}% of the original number of {noun} "
                f"in a group were removed from the group, {dec(result, 0)} {noun} "
                f"remained in the group. {want}")
        order = (["the_original", "percent_of_remainder", "divided_by_the_percent",
                  "percent_as_count"] if ask == "removed" else
                 ["divided_by_the_percent", "added_the_percent_back", "the_removed",
                  "percent_as_count"])
        difficulty = "hard"

    if key <= 0:
        raise ItemError("the original has to be a positive amount")
    P = {"kind": "pct_reverse", "result": float(result), "p": float(pct),
         "frame": frame, "ask": ask, "round_to": float(round_to) if round_to else None}
    original = result / (1 - pct / 100) if frame == "removed_remained" else None
    pool = {
        "part_over_percent": ("divided the part by the percent and stopped, leaving the "
                              "100 out", result / pct),
        "part_less_percent": ("subtracted the percent from the part as though both were "
                              "counts", result - pct),
        "part_plus_percent": ("added the percent to the part as though both were counts",
                              result + pct),
        "percent_of_part": ("took the percent of the part instead of dividing by it",
                            result * pct / 100),
        "halved": ("treated the part as half of the whole", 2 * result),
        "increase_again": (f"increased by {dec(pct, places_needed(pct))}% again instead "
                           "of undoing the increase", result * (1 + pct / 100)),
        "decrease_instead": (f"took {dec(pct, places_needed(pct))}% off the result "
                             "instead of dividing by the increase",
                             result * (1 - pct / 100)),
        "result_less_percent": ("subtracted the percent from the result as a count",
                                result - pct),
        "result_over_percent": ("divided the result by the percent", result / pct),
        # a one-digit percent written straight after the decimal point: 6% as
        # 0.6 rather than 0.06, so the increase is undone by dividing by 1.6
        "decimal_multiplier": (f"wrote {dec(pct, places_needed(pct))}% as "
                               f"{dec(pct / 10, places_needed(pct / 10, 3))} instead of "
                               f"{dec(pct / 100, places_needed(pct / 100, 3))}, dividing by "
                               f"{dec(1 + pct / 10, places_needed(1 + pct / 10, 3))} rather "
                               f"than by {dec(1 + pct / 100, places_needed(1 + pct / 100, 3))}",
                               result / (1 + pct / 10)
                               if frame == "increased_to" and pct < 10 else None),
        "the_original": ("gave the original number of items instead of the number "
                         "removed", original),
        "the_removed": (f"gave the number of {ctx[0] if ctx else 'items'} removed instead "
                        "of the number the group started with",
                        original - result if original else None),
        "added_the_percent_back": (f"added {dec(pct, places_needed(pct))}% of what "
                                   "remained back on instead of dividing by the percent "
                                   "that was left", result * (1 + pct / 100)),
        "percent_of_remainder": (f"took {dec(pct, places_needed(pct))}% of what remained "
                                 "rather than of the original group", result * pct / 100),
        "divided_by_the_percent": (f"divided by {dec(pct / 100, places_needed(pct / 100, 3))} "
                                   f"instead of by "
                                   f"{dec(1 - pct / 100, places_needed(1 - pct / 100, 3))}",
                                   result * 100 / pct),
        "percent_as_count": ("subtracted the percent from the remaining count as though "
                             "it were a count", result - pct),
    }
    mistakes = [(why, snap(value, round_to) if round_to else value)
                for why, value in pick(pool, order, wrongs) if value >= 0]

    if frame == "removed_remained":
        rationale = (f"The {dec(result, 0)} that remained are "
                     f"{dec(100 - pct, places_needed(100 - pct))}% of the original, so the "
                     f"group held {dec(original, places_needed(original, 4))}"
                     + (f" and {dec(key, places_needed(key, 4))} were removed." if ask == "removed"
                        else "."))
    elif frame == "increased_to":
        rationale = (f"n x {dec(1 + pct / 100, places_needed(1 + pct / 100, 4))} = "
                     f"{dec(result, 0)}, so n = {dec(key, places_needed(key, 4))}.")
    else:
        rationale = (f"{dec(result, 0)} = {dec(pct, places_needed(pct))}/100 x n, so "
                     f"n = 100 x {dec(result, 0)}/{dec(pct, places_needed(pct))} = "
                     f"{dec(key, places_needed(key, 4))}.")
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    if fmt == "spr":
        return spr("pct.reverse", "the whole from a part", difficulty, seed, stem, key,
                   rationale, mistakes=mistakes, params=P)
    return mcq("pct.reverse", "the whole from a part", difficulty, seed, stem, key,
               mistakes, rng, rationale, style=style, places=places, signed=True,
               params=P)


# ------------------------------------------------------------------ CHANGE

def change(rng: random.Random, seed: int, *, old=None, new=None, frame=None, fmt=None,
           places=None, ctx=None, wrongs=None) -> Item:
    """Two values are given and the percent between them is missing."""
    frame = frame or rng.choice(["percent_increase", "bill", "p_greater", "p_less"])
    old = q(old) if old is not None else q(rng.randrange(4, 400, 2))
    if new is None:
        factor = q(rng.choice([Q(11, 10), Q(5, 4), Q(3, 2), 2, 3, 10, Q(4, 5), Q(1, 2)]))
        new = old * factor
    new = q(new)
    if new == old or old <= 0 or new <= 0:
        raise ItemError("a percent change needs two different positive values")
    key = 100 * (new - old) / old
    up = new > old
    difficulty = "medium"

    if frame == "percent_increase":
        noun, holder = ctx or rng.choice(COLLECTIONS)
        word = "increased" if up else "decreased"
        stem = (f"The number of {noun} in a {holder} {word} from {dec(old, 0)} to "
                f"{dec(new, 0)}. What was the percent {'increase' if up else 'decrease'} "
                f"in the number of {noun} in this {holder}?")
        order = ["difference", "the_new_value", "ratio", "over_the_new_value"]
        difficulty = "easy"
    elif frame == "bill":
        which = rng.choice(["water", "electricity", "internet", "heating"])
        places = 1 if places is None else places
        stem = (f"A customer's monthly {which} bill was ${dec(old, 2)}. Due to a rate "
                f"{'increase' if up else 'reduction'}, her monthly bill is now "
                f"${dec(new, 2)}. To the nearest tenth of a percent, by what percent did "
                f"the amount of the customer's {which} bill "
                f"{'increase' if up else 'decrease'}?")
        order = ["difference", "over_the_new_value", "ratio_times_100", "ratio"]
    elif frame == "p_greater":
        if not up:
            raise ItemError("this frame states an increase")
        stem = (f"{dec(new, 0)} is p% greater than {dec(old, 0)}. What is the value of p ?")
        order = ["difference", "the_new_value", "ratio_times_100", "ratio"]
        difficulty = "hard"
    else:                                                      # p_less
        if up:
            raise ItemError("this frame states a decrease")
        stem = (f"{dec(new, 0)} is p% less than {dec(old, 0)}. What is the value of p ?")
        order = ["difference", "the_new_value", "ratio_times_100", "over_the_new_value"]
        difficulty = "hard"

    style = "plain" if frame in ("p_greater", "p_less") else "percent"
    if places is None and places_needed(key, 6) > 2:
        raise ItemError("this percent does not print in two decimals")
    if places is not None:
        key = (unambiguous(key, Q(1, 10) ** places) if key > 0
               else -unambiguous(-key, Q(1, 10) ** places))
    P = {"kind": "pct_change", "old": float(old), "new": float(new),
         "round": float(places) if places is not None else None}
    pool = {
        "difference": ("subtracted the two values and read the difference as the percent",
                       abs(new - old)),
        "the_new_value": ("read the value after the change as the percent", new),
        "ratio": ("divided the new value by the old one and read the quotient itself as "
                  "the percent", new / old),
        "ratio_times_100": ("reported the new value as a percent of the old one instead "
                            "of the change", 100 * new / old),
        "over_the_new_value": ("divided the change by the new value instead of by the "
                               "original", 100 * abs(new - old) / new),
    }
    mistakes = pick(pool, order, wrongs)
    rationale = (f"The change is {dec(abs(new - old), places_needed(abs(new - old), 4))}, "
                 f"and {dec(abs(new - old), places_needed(abs(new - old), 4))}/"
                 f"{dec(old, places_needed(old, 4))} = "
                 f"{dec(abs(key), places_needed(abs(key), 4))}%.")
    key = abs(key)
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    if fmt == "spr":
        return spr("pct.change", "percent change between two values", difficulty, seed,
                   stem, key, rationale, mistakes=mistakes, params=P)
    return mcq("pct.change", "percent change between two values", difficulty, seed, stem,
               key, mistakes, rng, rationale, style=style, places=places, params=P)


# -------------------------------------------------------------- MULTIPLIER

def multiplier(rng: random.Random, seed: int, *, n=None, pct=None, up=True, ask=None,
               fmt=None, places=None, wrongs=None) -> Item:
    """The number you multiply by, and the percent it stands for, each from the other."""
    ask = ask or rng.choice(["factor", "percent"])
    pct = q(pct if pct is not None else rng.choice(PCTS))
    n = q(n if n is not None else rng.randrange(10, 500, 5))
    ratio = 1 + pct / 100 if up else 1 - pct / 100
    word = "greater" if up else "less"
    letter = rng.choice(["k", "z", "m", "t"])

    if ask == "factor":
        key = ratio
        stem = (f"The number {letter} is {dec(pct, places_needed(pct))}% {word} than "
                f"{dec(n, 0)}. If {letter} is the product of {dec(n, 0)} and r, what is "
                f"the value of r ?")
        pool = {
            "percent_itself": ("used the percent itself as the number to multiply by", pct),
            "decimal_slip": ("moved the decimal point one place when converting the "
                             "percent", pct / 10),
            "change_only": ("gave only the change as a decimal, leaving off the 1 for the "
                            "original", pct / 100),
            "wrong_direction": (f"{'subtracted' if up else 'added'} the change instead of "
                                f"{'adding' if up else 'subtracting'} it", 1 - (ratio - 1)),
        }
        order = ["percent_itself", "decimal_slip", "change_only", "wrong_direction"]
        style = "plain"
    else:                                                      # percent
        if not up:
            raise ItemError("this frame states a multiplier greater than one")
        key = pct
        stem = (f"The value of {letter} is {dec(ratio, places_needed(ratio, 4))} times "
                f"{dec(n, 0)}. The value of {letter} is what percent {word} than "
                f"{dec(n, 0)}?")
        pool = {
            "multiplier_ten_times": ("moved the decimal point one place, reading the "
                                     "multiplier itself as the percent", ratio * 10),
            "answer_ten_times": ("moved the decimal point one place in the answer",
                                 pct * 10),
            "added_the_hundred": ("added 100 to the whole multiplier instead of "
                                  "subtracting it", 100 + ratio * 100),
            "multiplier_as_percent": ("read the whole multiplier as the percent",
                                      ratio * 100),
        }
        order = ["multiplier_ten_times", "answer_ten_times", "added_the_hundred",
                 "multiplier_as_percent"]
        style = "plain"

    mistakes = pick(pool, order, wrongs)
    P = {"kind": "pct_multiplier", "n": float(n), "p": float(pct), "up": up, "ask": ask}
    rationale = (f"{dec(pct, places_needed(pct))}% {word} than {dec(n, 0)} is "
                 f"{dec(ratio, places_needed(ratio, 4))} x {dec(n, 0)}, so "
                 + (f"r = {dec(key, places_needed(key, 4))}." if ask == "factor"
                    else f"the increase is {dec(key, places_needed(key, 4))}%."))
    fmt = fmt or ("spr" if rng.random() < 0.2 else "mcq")
    if fmt == "spr":
        return spr("pct.multiplier", "percent and multiplier", "medium", seed, stem, key,
                   rationale, mistakes=mistakes, params=P)
    return mcq("pct.multiplier", "percent and multiplier", "medium", seed, stem, key,
               mistakes, rng, rationale, style=style, places=places, params=P)


# -------------------------------------------------------------- EXPRESSION

def _coef(v) -> str:
    return dec(v, places_needed(v, 6), group=False)


def expression(rng: random.Random, seed: int, *, pct=None, kind=None, var=None,
               ctx=None, wrongs=None) -> Item:
    """The same one step, written as an expression rather than evaluated."""
    kind = kind or rng.choice(["of", "increase", "decrease"])
    pct = q(pct if pct is not None else rng.randrange(2, 99))
    var = var or rng.choice(["h", "x", "n", "w"])
    r = pct / 100

    if kind == "of":
        shape, part, whole = ctx or rng.choice([
            ("parallelogram", "base", "height"), ("rectangle", "width", "length"),
            ("triangle", "base", "height"), ("trapezoid", "shorter side", "longer side")])
        stem = (f"The length of the {part} of a certain {shape} is "
                f"{dec(pct, places_needed(pct))}% of the {whole} of the {shape}. Which "
                f"expression represents the length of the {part} of the {shape}, where "
                f"{var} is the {whole} of the {shape}?")
        key = f"{_coef(r)}{var}"
        pool = {
            "whole_number": ("wrote the percent as a whole number instead of converting "
                             "it", f"{_coef(pct)}{var}"),
            "one_place_too_few": ("moved the decimal point one place too few",
                                  f"{_coef(pct / 10)}{var}"),
            "one_place_too_many": ("moved the decimal point one place too many",
                                   f"{_coef(pct / 1000)}{var}"),
            "added_instead": ("added the percent instead of multiplying by it",
                              f"{var} + {_coef(r)}"),
        }
        order = ["whole_number", "one_place_too_few", "one_place_too_many", "added_instead"]
    elif kind == "increase":
        stem = (f"Which of the following represents the result of increasing the quantity "
                f"{var} by {dec(pct, places_needed(pct))}%, where {var} > 0 ?")
        key = f"{_coef(1 + r)}{var}"
        pool = {
            "increase_only": ("gave only the increase and not the quantity it is added to",
                              f"{_coef(r)}{var}"),
            "percent_as_count": ("added the percent as though it were a count",
                                 f"{var} + {dec(pct, places_needed(pct))}"),
            "decimal_added": ("added the decimal form instead of multiplying by it",
                              f"{var} + {_coef(r)}"),
            "whole_number": ("wrote the percent as a whole number instead of converting "
                             "it", f"{_coef(pct)}{var}"),
        }
        order = ["increase_only", "percent_as_count", "decimal_added", "whole_number"]
    else:                                                      # decrease
        stem = (f"Which of the following represents the result of decreasing the quantity "
                f"{var} by {dec(pct, places_needed(pct))}%, where {var} > 0 ?")
        key = f"{_coef(1 - r)}{var}"
        pool = {
            "percent_as_count": ("subtracted the percent as though it were a count",
                                 f"{var} - {dec(pct, places_needed(pct))}"),
            "the_part_taken": ("gave the part taken away rather than what is left",
                               f"{_coef(r)}{var}"),
            "decimal_subtracted": ("subtracted the decimal form instead of multiplying by "
                                   "it", f"{var} - {_coef(r)}"),
            "wrong_direction": ("added the change instead of subtracting it",
                                f"{_coef(1 + r)}{var}"),
        }
        order = ["percent_as_count", "the_part_taken", "decimal_subtracted",
                 "wrong_direction"]

    # three of the four are printed, so a free draw shuffles rather than leaving
    # the last one in this file for ever
    wrong = pick(pool, order if wrongs is not None else rng.sample(order, len(order)),
                 wrongs)
    P = {"kind": "pct_expression", "p": float(pct), "form": kind, "var": var}
    rationale = f"Converting the percent to a decimal gives {key}."
    return text_mcq("pct.expression", "a percent as an expression", "easy", seed, stem,
                    key, wrong, rng, rationale, params=P)
