"""Percents applied one after another, and the two answers that go with them.

A single percent is arithmetic. Two percents in a row are where the topic's
real misconception lives: that percents add. They do not -- a 167% rise
followed by a 16% fall is not a 151% rise -- and almost every option in this
file is a version of that mistake, or of the closely related one that applies
the second percent to the wrong quantity.

    compound_share      a percent of a percent: a share of the whole
    successive          the same or a second percent applied to a value
    two_step            two relations chained through a middle number
    markup_discount     cost -> consumer price -> discounted price
    repeated_rate       one month's rate, repeated over a period
    remainder_total     the categories are percents, the leftover is a count
    per_serving_model   a per-unit percent written as a model in x
"""

from __future__ import annotations

import random

from ....item import Item, ItemError
from ..values import (Q, dec, mcq, pick, places_needed, q, snap, spr,
                      text_mcq, unambiguous)

__all__ = ["compound_share", "successive", "two_step", "markup_discount",
           "repeated_rate", "remainder_total", "per_serving_model"]

ATTRS = ["red", "green", "blue", "rectangular", "metal", "wooden", "polished",
         "striped", "hollow", "labeled", "cracked", "magnetic"]
GROUPS = [("a group", "the group"), ("a box", "the box"), ("a bin", "the bin"),
          ("a shipment", "the shipment"), ("a display case", "the case")]

SERIES = [("An insurance company", "information sessions", "information session"),
          ("A community college", "orientation sessions", "orientation session"),
          ("A hospital", "training workshops", "training workshop"),
          ("A bicycle club", "safety clinics", "safety clinic"),
          ("A museum", "curator talks", "curator talk")]

ASSETS = [("stove", "restaurant", "installed"), ("delivery van", "bakery", "bought"),
          ("espresso machine", "cafe", "installed"), ("kiln", "pottery studio", "installed"),
          ("tractor", "orchard", "bought")]
OWNERS = [("Thomas", "his"), ("Adaeze", "her"), ("Miguel", "his"), ("Hannah", "her"),
          ("Sung-min", "her")]
COLLECTIBLES = ["collectible comic book", "first-edition novel", "vintage guitar",
                "signed baseball", "antique clock"]

BOOKS = ["books", "puzzles", "board games", "calendars", "posters"]
GOODS = ["smartphone", "fitness tracker", "cordless drill", "pair of headphones",
         "electric kettle"]

COMMITTEES = [("A school district", "committee", "plans for the construction of a new "
               "high school", ["parents of students", "teachers from the current high "
                               "school", "school and district administrators", "students"]),
              ("A city council", "panel", "a redesign of the riverfront park",
               ["local business owners", "residents of the riverfront district",
                "city planners", "students"]),
              ("A hospital", "board", "a new visiting policy",
               ["nurses", "physicians", "hospital administrators", "patients"])]

CEREALS = [("Crunchy Grain", "cereal", "potassium", "milligrams"),
           ("Morning Oats", "cereal", "iron", "milligrams"),
           ("Trail Crunch", "granola", "calcium", "milligrams"),
           ("Harvest Flakes", "cereal", "fiber", "grams")]


def _article(word: str) -> str:
    return "an" if word[0].lower() in "aeiou" else "a"


# ------------------------------------------------------------ COMPOUND SHARE

def compound_share(rng: random.Random, seed: int, *, pcts=None, base=None, ask=None,
                   fmt=None, places=None, ctx=None) -> Item:
    """A percent of a percent -- of a percent -- of the same whole."""
    ask = ask or rng.choices(["share", "count", "complement"], weights=[4, 3, 3])[0]
    if pcts is None:
        pcts = tuple(rng.choice([12, 15, 20, 24, 25, 30, 35, 36, 37, 40, 42, 45, 50,
                                 55, 60, 64, 70, 72, 75, 80])
                     for _ in range(3 if ask == "complement" else 2))
    pcts = tuple(q(p) for p in pcts)
    factor = Q(1)
    for p in pcts:
        factor *= p / 100
    share = 100 * factor
    difficulty = "medium"

    if ask == "count":
        who, plural, singular = ctx or rng.choice(SERIES)
        base = q(base if base is not None else rng.randrange(200, 4000, 50))
        key = base * factor
        if key.denominator != 1:
            raise ItemError("a count of people has to come out whole")
        ord_from = ["first", "first and second", "first, second, and third"]
        ord_to = ["second", "third", "fourth"]
        how_many = ["three", "four"][len(pcts) - 2]
        steps = [f"{dec(p, places_needed(p))}% of the people who attended the "
                 f"{ord_from[i]} {singular if i == 0 else plural} attended the "
                 f"{ord_to[i]} {singular}" for i, p in enumerate(pcts)]
        stem = (f"{who} offers a series of {how_many} {plural}. {dec(base, 0)} people "
                f"attended the first {singular}. "
                + ", and ".join([", ".join(steps[:-1]), steps[-1]] if len(steps) > 2
                                else steps)
                + f". How many people attended all {how_many} {plural}?")
        style = "plain"
        mistakes = [
            ("stopped at the stage before last, before the final percent was applied",
             base * _prefix(pcts, len(pcts) - 1)),
            (f"applied {dec(pcts[-1], places_needed(pcts[-1]))}% to everyone who started "
             "rather than to the people still taking part", base * pcts[-1] / 100),
            ("added the percentages and took that share of the starting group",
             base * sum(pcts) / 100),
            ("multiplied the percentages but divided by 100 only once",
             base * factor * 100),
        ]
        rationale = " -> ".join(
            [dec(base, 0)] + [dec(base * _prefix(pcts, i + 1),
                                  places_needed(base * _prefix(pcts, i + 1), 2))
                              for i in range(len(pcts))]) + "."
        difficulty = "hard" if len(pcts) > 2 else "medium"
    else:
        attrs = ctx or tuple(rng.sample(ATTRS, len(pcts)))
        holder, the_holder = rng.choice(GROUPS)
        if ask == "complement":
            places = 2 if places is None else places
            key = 100 - share
            body = " ".join(attrs)
            stem = (f"{dec(pcts[0], places_needed(pcts[0]))}% of the items in {holder} are "
                    f"{attrs[0]}. Of those, {dec(pcts[1], places_needed(pcts[1]))}% are also "
                    f"{attrs[1]}."
                    + (f" Of the {attrs[0]} {attrs[1]} items, "
                       f"{dec(pcts[2], places_needed(pcts[2]))}% are also {attrs[2]}."
                       if len(pcts) > 2 else "")
                    + f" Which of the following is closest to the percentage of the items "
                      f"in {the_holder} that are not {body} items?")
            total = sum(pcts)
            mistakes = [
                ("subtracted the sum of the percentages, written as decimals, from 100",
                 100 - total / 100),
                ("added the percentages as decimals and reported the sum",
                 total / 100),
                ("multiplied the percentages but left the decimal point one place out",
                 share * 10),
                ("gave the share that is described instead of the share that is not",
                 share),
            ]
            difficulty = "hard"
        else:
            key = share
            if places is None and places_needed(key, 6) > 2:
                places = 2
            both = " and ".join(attrs)
            question = (f"Which of the following is closest to the percentage of the items "
                        f"in {the_holder} that are {both}?" if places == 2
                        else f"What percentage of the items in {the_holder} are {both}?")
            stem = (f"In {holder}, {dec(pcts[0], places_needed(pcts[0]))}% of the items are "
                    f"{attrs[0]}. Of all the {attrs[0]} items in {the_holder}, "
                    f"{dec(pcts[1], places_needed(pcts[1]))}% are also {attrs[1]}."
                    + (f" Of the {attrs[0]} {attrs[1]} items, "
                       f"{dec(pcts[2], places_needed(pcts[2]))}% are also {attrs[2]}."
                       if len(pcts) > 2 else "")
                    + " " + question)
            mistakes = [
                ("added the percentages instead of taking a percent of a percent",
                 sum(pcts)),
                ("subtracted the percentages instead of taking a percent of a percent",
                 pcts[0] - pcts[1]),
                ("divided one percentage by the other", 100 * pcts[1] / pcts[0]),
                ("used the first percentage alone", pcts[0]),
            ]
        style = "percent"
        base = None
        if places is not None:
            key = unambiguous(key, Q(1, 10) ** places)
        exact = 100 - share if ask == "complement" else share
        rationale = (" x ".join(f"{dec(p, places_needed(p))}%" for p in pcts)
                     + f" of the whole is {dec(share, places_needed(share, 6))}%"
                     + (f", so {dec(exact, places_needed(exact, 6))}% are not, which is "
                        f"{dec(key, places_needed(key, 4))}% to the nearest hundredth."
                        if ask == "complement" else "."))

    if places is not None:
        key = unambiguous(key, Q(1, 10) ** places)
    P = {"kind": "pct_chain", "pcts": [float(p) for p in pcts],
         "base": float(base) if base is not None else None, "ask": ask,
         "round": float(places) if places is not None else None}
    fmt = fmt or ("spr" if ask == "count" and rng.random() < 0.5 else "mcq")
    if fmt == "spr":
        return spr("pct.compound_share", "a percent of a percent", difficulty, seed, stem,
                   key, rationale, mistakes=mistakes, params=P)
    return mcq("pct.compound_share", "a percent of a percent", difficulty, seed, stem,
               key, mistakes, rng, rationale, style=style, places=places, params=P)


def _prefix(pcts, upto):
    out = Q(1)
    for p in pcts[:upto]:
        out *= p / 100
    return out


# --------------------------------------------------------------- SUCCESSIVE

def successive(rng: random.Random, seed: int, *, start=None, pcts=None, ups=None,
               years=None, ask=None, frame=None, fmt=None, places=None, cents=None,
               ctx=None, wrongs=None) -> Item:
    """The same percent year after year, or one percent and then another."""
    frame = frame or rng.choice(["depreciation", "two_changes"])
    difficulty = "medium"

    if frame == "depreciation":
        asset, business, verb = ctx or rng.choice(ASSETS)
        owner, whose = rng.choice(OWNERS)
        pct = q(pcts[0] if pcts else rng.choice([5, 10, 12, 15, 20, 25, 30, 40]))
        years = years or rng.choice([2, 2, 3])
        start = q(start if start is not None else rng.randrange(400, 9000, 50))
        ratio = 1 - pct / 100
        key = start * ratio ** years
        ask = "value"
        stem = (f"{owner} {verb} a new {asset} for {whose} {business}. At that time, the "
                f"{asset} had a value of ${dec(start, places_needed(start))}. {owner} "
                f"estimates that each year the value of the {asset} will depreciate by "
                f"{dec(pct, places_needed(pct))}% of the previous year's estimated value. "
                f"What is the estimated value of the {asset} exactly {years} years after "
                f"{owner} {verb} it?")
        pool = {
            "years_added": (f"took {dec(pct * years, places_needed(pct * years))}% off in a "
                            "single step, adding the years' percentages together",
                            start * (1 - pct * years / 100)),
            "one_year": (f"depreciated for one year instead of {years}", start * ratio),
            "value_lost": ("gave the value the asset has lost rather than the value it "
                           "still has", start - key),
            "one_year_too_many": (f"depreciated for {years + 1} years",
                                  start * ratio ** (years + 1)),
            # "depreciates by 20%" read as "is divided by 1.20": the same figure
            # used as a growth factor and then undone, rather than 0.80 applied
            "divided_each_year": (f"divided by "
                                  f"{dec(1 + pct / 100, places_needed(1 + pct / 100, 3))} "
                                  f"each year instead of multiplying by "
                                  f"{dec(ratio, places_needed(ratio, 3))}",
                                  snap(start / (1 + pct / 100) ** years, 1)),
        }
        order = ["years_added", "one_year", "value_lost", "divided_each_year",
                 "one_year_too_many"]
        rationale = (f"${dec(start, places_needed(start))} x "
                     f"{dec(ratio, places_needed(ratio, 4))}^{years} = "
                     f"${dec(key, places_needed(key, 4))}.")
        P = {"kind": "pct_successive", "start": float(start), "pcts": [float(pct)],
             "ups": [False], "years": years, "ask": "value",
             "round": float(places) if places is not None else None}
        style = "money"
        pcts_used = (pct,)
    else:
        thing = ctx or rng.choice(COLLECTIBLES)
        art = _article(thing)
        y0 = rng.choice([2009, 2010, 2011, 2013, 2015])
        if pcts is None:
            pcts = (rng.choice([24, 35, 48, 60, 75, 110, 125, 140, 167, 180]),
                    rng.choice([8, 12, 16, 20, 25, 32, 40]))
        pcts = tuple(q(p) for p in pcts)
        ups = ups or (True, False)
        ask = ask or rng.choice(["net_percent", "value"])
        f1 = 1 + pcts[0] / 100 if ups[0] else 1 - pcts[0] / 100
        f2 = 1 + pcts[1] / 100 if ups[1] else 1 - pcts[1] / 100
        net = 100 * (f1 * f2 - 1)
        words = [("increased", "increase"), ("decreased", "decrease")]
        w1 = words[0] if ups[0] else words[1]
        w2 = words[0] if ups[1] else words[1]
        if ask == "net_percent":
            places = 2 if places is None else places
            key = unambiguous(abs(net), Q(1, 10) ** places)
            stem = (f"The value of {art} {thing} {w1[0]} by {dec(pcts[0], places_needed(pcts[0]))}% "
                    f"from the end of {y0} to the end of {y0 + 1} and then {w2[0]} by "
                    f"{dec(pcts[1], places_needed(pcts[1]))}% from the end of {y0 + 1} to the "
                    f"end of {y0 + 2}. What was the net percentage "
                    f"{'increase' if net > 0 else 'decrease'} in the value of the {thing} "
                    f"from the end of {y0} to the end of {y0 + 2}?")
            style = "percent"
            pool_pairs = [
                ("percents_subtracted",
                 "subtracted the second percent from the first instead of compounding "
                 "the two changes", abs(pcts[0] - pcts[1])),
                ("second_on_the_percent",
                 f"applied the {dec(pcts[1], places_needed(pcts[1]))}% to the percent "
                 "increase rather than to the value", abs(pcts[0] * f2)),
                ("second_reversed",
                 f"{'increased' if not ups[1] else 'decreased'} by "
                 f"{dec(pcts[1], places_needed(pcts[1]))}% in the second year instead of "
                 f"{'decreasing' if not ups[1] else 'increasing'}",
                 abs(100 * (f1 * (2 - f2) - 1))),
                ("percents_added", "added the two percents", pcts[0] + pcts[1]),
            ]
            start = None
        else:
            start = q(start if start is not None else rng.randrange(200, 9000, 25))
            key = start * f1 * f2
            stem = (f"The value of {art} {thing} was ${dec(start, places_needed(start))} at the "
                    f"end of {y0}. Its value {w1[0]} by {dec(pcts[0], places_needed(pcts[0]))}% "
                    f"from the end of {y0} to the end of {y0 + 1} and then {w2[0]} by "
                    f"{dec(pcts[1], places_needed(pcts[1]))}% from the end of {y0 + 1} to the "
                    f"end of {y0 + 2}. What was the value of the {thing} at the end of "
                    f"{y0 + 2}?")
            style = "money"
            pool_pairs = [
                ("percents_added", "added the two percents and applied them in one step",
                 start * (1 + (pcts[0] if ups[0] else -pcts[0]) / 100
                          + (pcts[1] if ups[1] else -pcts[1]) / 100)),
                ("first_only", "applied the first change only", start * f1),
                ("second_only", "applied the second change only", start * f2),
                ("second_reversed",
                 f"{'increased' if not ups[1] else 'decreased'} in the second year instead "
                 f"of {'decreasing' if not ups[1] else 'increasing'}", start * f1 * (2 - f2)),
            ]
        pool = {name: (why, value) for name, why, value in pool_pairs}
        order = [name for name, _, _ in pool_pairs]
        rationale = (f"{dec(f1, places_needed(f1, 4))} x {dec(f2, places_needed(f2, 4))} = "
                     f"{dec(f1 * f2, places_needed(f1 * f2, 6))}"
                     + (f", a net change of {dec(net, places_needed(net, 4))}%."
                        if ask == "net_percent" else "."))
        P = {"kind": "pct_successive", "start": float(start) if start is not None else None,
             "pcts": [float(p) for p in pcts], "ups": list(ups), "years": 1, "ask": ask,
             "round": float(places) if places is not None else None}
        difficulty = "hard"
        pcts_used = pcts

    mistakes = pick(pool, order, wrongs)
    fmt = fmt or ("spr" if rng.random() < 0.2 else "mcq")
    if fmt == "spr":
        return spr("pct.successive", "two changes in a row", difficulty, seed, stem, key,
                   rationale, mistakes=mistakes, params=P)
    return mcq("pct.successive", "two changes in a row", difficulty, seed, stem, key,
               mistakes, rng, rationale, style=style, places=places, cents=cents, params=P)


# ----------------------------------------------------------------- TWO STEP

def two_step(rng: random.Random, seed: int, *, pct1=None, up1=None, pct2=None, up2=None,
             start=None, ask=None, fmt=None, places=None, letters=None,
             wrongs=None) -> Item:
    """Three numbers in a chain: the first is a percent of the second, and so on."""
    ask = ask or rng.choice(["times", "value"])
    pct1 = q(pct1 if pct1 is not None else rng.choice(
        [10, 20, 25, 30, 40, 45, 50, 55, 60, 70, 75, 80, 90, 110, 150, 190]))
    pct2 = q(pct2 if pct2 is not None else rng.choice(
        [10, 20, 25, 30, 40, 45, 50, 55, 60, 70, 75, 80, 90, 110, 160, 180]))
    up1 = rng.random() < 0.5 if up1 is None else up1
    up2 = rng.random() < 0.5 if up2 is None else up2
    f1 = 1 + pct1 / 100 if up1 else 1 - pct1 / 100
    f2 = 1 + pct2 / 100 if up2 else 1 - pct2 / 100
    if f1 <= 0 or f2 <= 0:
        raise ItemError("a decrease of a hundred percent leaves nothing to work with")
    w1, w2 = ("greater" if up1 else "less"), ("greater" if up2 else "less")

    if ask == "times":
        a, b, c = letters or rng.choice([("a", "b", "c"), ("x", "y", "z"),
                                         ("m", "n", "p"), ("r", "s", "t")])
        key = f2 * f1
        stem = (f"The number {a} is {dec(pct1, places_needed(pct1))}% {w1} than the "
                f"positive number {b}. The number {c} is "
                f"{dec(pct2, places_needed(pct2))}% {w2} than {a}. The number {c} is how "
                f"many times {b} ?")
        pool = {
            "first_as_share": (f"read \"{dec(pct1, places_needed(pct1))}% {w1} than\" as "
                               f"\"{dec(pct1, places_needed(pct1))}% of\"", f2 * pct1 / 100),
            "second_as_share": (f"read \"{dec(pct2, places_needed(pct2))}% {w2} than\" as "
                                f"\"{dec(pct2, places_needed(pct2))}% of\"", f1 * pct2 / 100),
            "both_as_shares": ("read both percents as shares rather than as changes",
                               pct1 * pct2 / 10000),
            "changes_added": ("added the two changes instead of multiplying the two "
                              "factors", 1 + (f1 - 1) + (f2 - 1)),
        }
        order = ["first_as_share", "second_as_share", "both_as_shares", "changes_added"]
        style = "plain"
        start = None
    else:
        a, b = letters or rng.choice([("a", "b"), ("w", "z"), ("m", "n"), ("p", "q")])
        start = q(start if start is not None else rng.randrange(8, 300, 2))
        key = f1 * f2 * start
        stem = (f"The number {a} is {dec(pct1, places_needed(pct1))}% {w1} than the number "
                f"{b}. The number {b} is {dec(pct2, places_needed(pct2))}% {w2} than "
                f"{dec(start, places_needed(start))}. What is the value of {a} ?")
        net = (pct1 if up1 else -pct1) + (pct2 if up2 else -pct2)
        pool = {
            "first_as_share": (f"read \"{dec(pct1, places_needed(pct1))}% {w1} than\" as "
                               f"\"{dec(pct1, places_needed(pct1))}% of\"",
                               start * f2 * pct1 / 100),
            "both_as_shares": ("read both percents as shares rather than as changes",
                               start * pct1 * pct2 / 10000),
            "second_as_share": (f"read \"{dec(pct2, places_needed(pct2))}% {w2} than\" as "
                                f"\"{dec(pct2, places_needed(pct2))}% of\"",
                                start * f1 * pct2 / 100),
            # percents do not add: the student folds the two changes into one
            # percent and then takes that percent of the number the chain starts
            # from, instead of applying each change in turn
            "percents_netted": (f"added the two percents and took the "
                                f"{dec(net, places_needed(net))}% total as a share of "
                                f"{dec(start, places_needed(start))} instead of applying "
                                "each change in turn",
                                start * net / 100 if net > 0 else None),
            "wrong_end": ("worked the chain from the wrong end, dividing where the item "
                          "multiplies", start * f2 / f1),
        }
        order = ["first_as_share", "both_as_shares", "second_as_share", "percents_netted",
                 "wrong_end"]
        style = "plain"

    mistakes = pick(pool, order, wrongs)
    if places is None and places_needed(key, 6) > 2:
        raise ItemError("this chain does not land on two decimals")
    P = {"kind": "pct_two_step", "p1": float(pct1), "up1": up1, "p2": float(pct2),
         "up2": up2, "start": float(start) if start is not None else None, "ask": ask}
    rationale = (f"{dec(f1, places_needed(f1, 4))} x {dec(f2, places_needed(f2, 4))}"
                 + (f" x {dec(start, places_needed(start))}" if start is not None else "")
                 + f" = {dec(key, places_needed(key, 6))}.")
    fmt = fmt or ("spr" if rng.random() < 0.45 else "mcq")
    if fmt == "spr":
        return spr("pct.two_step", "a chain of two percent relations", "hard", seed, stem,
                   key, rationale, mistakes=mistakes, params=P)
    return mcq("pct.two_step", "a chain of two percent relations", "hard", seed, stem,
               key, mistakes, rng, rationale, style=style, places=places, params=P)


# ---------------------------------------------------------- MARKUP DISCOUNT

def markup_discount(rng: random.Random, seed: int, *, cost=None, markup=None,
                    discount=None, months=None, thing=None, fmt=None, places=None,
                    cents=None) -> Item:
    """Cost to consumer price to clearance price: a markup and then a discount."""
    cost = q(cost if cost is not None else Q(rng.randrange(200, 2500, 25), 100))
    markup = q(markup if markup is not None else rng.choice(
        [140, 150, 175, 180, 200, 220, 240, 250, 270, 300]))
    discount = q(discount if discount is not None else rng.choice(
        [10, 15, 20, 25, 30, 40, 50, 60, 70, 75]))
    months = months or rng.choice([2, 3, 4, 6])
    thing = thing or rng.choice(BOOKS)
    consumer = cost * markup / 100
    key = consumer * (1 - discount / 100)
    if places_needed(key, 6) > 2:
        raise ItemError("a price has to come out to the cent")

    stem = (f"A reseller buys certain {thing} for a purchase price of "
            f"{dec(cost, 2)} dollars each and then marks them each for sale at a consumer "
            f"price that is {dec(markup, places_needed(markup))}% of the purchase price. "
            f"After {months} months, any remaining {thing} not yet sold are marked at a "
            f"discounted price that is {dec(discount, places_needed(discount))}% off the "
            f"consumer price. What is the discounted price of each of the remaining "
            f"{thing}, in dollars?")
    P = {"kind": "pct_markup", "cost": float(cost), "markup": float(markup),
         "discount": float(discount)}
    mistakes = [
        ("gave the consumer price, stopping before the discount was taken", consumer),
        ("gave the size of the discount instead of the price after it",
         consumer * discount / 100),
        (f"read \"{dec(markup, places_needed(markup))}% of the purchase price\" as "
         f"\"{dec(markup, places_needed(markup))}% above the purchase price\"",
         cost * (1 + markup / 100) * (1 - discount / 100)),
        ("subtracted the discount from the markup and applied the difference to the cost",
         cost * (markup - discount) / 100),
        ("took the discount off the purchase price rather than off the consumer price",
         cost * (1 - discount / 100)),
    ]
    rationale = (f"The consumer price is {dec(markup, places_needed(markup))}% of "
                 f"${dec(cost, 2)}, or ${dec(consumer, 2)}, and "
                 f"{dec(100 - discount, places_needed(100 - discount))}% of that is "
                 f"${dec(key, 2)}.")
    fmt = fmt or ("spr" if rng.random() < 0.4 else "mcq")
    if fmt == "spr":
        return spr("pct.markup_discount", "markup then discount", "hard", seed, stem, key,
                   rationale, mistakes=mistakes, params=P)
    return mcq("pct.markup_discount", "markup then discount", "hard", seed, stem, key,
               mistakes, rng, rationale, style="money", places=places, cents=cents,
               params=P)


# ------------------------------------------------------------ REPEATED RATE

def repeated_rate(rng: random.Random, seed: int, *, units=None, pct=None, months=None,
                  thing=None, fmt=None) -> Item:
    """One month's rate held steady across a period: the percent, then the count."""
    units = q(units if units is not None else rng.randrange(50000, 2000000, 50000))
    pct = q(pct if pct is not None else rng.choice([2, 4, 5, 8, 10, 12, 15, 18, 20, 25]))
    months = months or rng.choice([3, 4, 5, 6, 8, 11])
    thing = thing or rng.choice(GOODS)
    per_month = units * pct / 100
    key = per_month * (months + 1)
    if key.denominator != 1:
        raise ItemError("a count of units has to come out whole")

    stem = (f"During the first month of sales, a company sold {dec(units, 0)} units of a "
            f"certain type of {thing}. During the same month, "
            f"{dec(pct, places_needed(pct))}% of the units sold were returned. If sales "
            f"and the return rate remain the same for each of the next {months} months, "
            f"about how many units of this {thing} will be returned to the company during "
            f"this {months + 1}-month period?")
    P = {"kind": "pct_repeated", "units": float(units), "p": float(pct), "months": months}
    mistakes = [
        ("gave the returns for a single month", per_month),
        (f"counted only the {months} later months and left out the first",
         per_month * months),
        (f"found the units that were kept rather than the units that came back",
         units * (1 - pct / 100) * (months + 1)),
        ("gave the units sold over the period instead of the units returned",
         units * (months + 1)),
    ]
    rationale = (f"{dec(pct, places_needed(pct))}% of {dec(units, 0)} is "
                 f"{dec(per_month, 0)} a month, and {dec(per_month, 0)} x {months + 1} = "
                 f"{dec(key, 0)}.")
    fmt = fmt or ("spr" if rng.random() < 0.2 else "mcq")
    if fmt == "spr":
        return spr("pct.repeated_rate", "a rate repeated over a period", "medium", seed,
                   stem, key, rationale, mistakes=mistakes, params=P)
    return mcq("pct.repeated_rate", "a rate repeated over a period", "medium", seed, stem,
               key, mistakes, rng, rationale, params=P)


# ---------------------------------------------------------- REMAINDER TOTAL

def remainder_total(rng: random.Random, seed: int, *, pcts=None, left=None, ask=None,
                    fmt=None, ctx=None) -> Item:
    """Three categories are given as percents and the fourth as a count of people."""
    ask = ask or rng.choice(["difference", "total", "one_group"])
    body, panel, purpose, roles = ctx or rng.choice(COMMITTEES)
    if pcts is None:
        while True:
            pcts = tuple(rng.choice([5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
                         for _ in range(3))
            if 40 <= sum(pcts) <= 90 and pcts[1] != pcts[2]:
                break
    pcts = tuple(q(p) for p in pcts)
    rest = 100 - sum(pcts)
    if rest <= 0:
        raise ItemError("the categories given already use up the whole committee")
    left = q(left if left is not None else rng.randrange(2, 40))
    total = left * 100 / rest
    if total.denominator != 1:
        raise ItemError("the committee has to have a whole number of members")
    counts = [total * p / 100 for p in pcts]
    if any(c.denominator != 1 for c in counts):
        raise ItemError("each group has to have a whole number of members")

    if ask == "difference":
        key = counts[1] - counts[2]
        want = (f"How many more {roles[1]} were invited to join the {panel} than "
                f"{roles[2]}?")
    elif ask == "total":
        key = total
        want = f"How many individuals in total were invited to join the {panel}?"
    else:
        key = counts[1]
        want = f"How many {roles[1]} were invited to join the {panel}?"
    if key <= 0:
        raise ItemError("the comparison has to come out positive")

    stem = (f"{body} is forming a {panel} to discuss {purpose}. Of those invited to join "
            f"the {panel}, " + ", ".join(
                f"{dec(p, places_needed(p))}% are {roles[i]}" for i, p in enumerate(pcts))
            + f", and the remaining {dec(left, 0)} individuals are {roles[3]}. {want}")
    P = {"kind": "pct_remainder", "pcts": [float(p) for p in pcts], "left": float(left),
         "ask": ask}
    common = [
        (f"gave the size of the whole {panel} rather than the group asked about", total),
        (f"treated the {dec(left, 0)} remaining individuals as the whole {panel}",
         left * abs(pcts[1] - pcts[2]) / 100 if ask == "difference"
         else left * pcts[1] / 100),
        (f"read the percentages printed for the {panel} as counts of people", sum(pcts)),
    ]
    if ask == "difference":
        mistakes = [("subtracted the two percentages and read the difference as a count "
                     "of people", abs(pcts[1] - pcts[2])),
                    (f"added the two groups instead of comparing them",
                     counts[1] + counts[2])] + common
    elif ask == "one_group":
        mistakes = [(f"read the {dec(pcts[1], places_needed(pcts[1]))}% as a count of "
                     "people", pcts[1]),
                    (f"applied {dec(pcts[1], places_needed(pcts[1]))}% to the "
                     f"{dec(left, 0)} remaining individuals rather than to the whole "
                     f"{panel}", left * pcts[1] / 100)] + common
    else:
        mistakes = [(f"divided the {dec(left, 0)} remaining individuals by the percentages "
                     "that were given rather than by the percentage they are",
                     left * 100 / sum(pcts)),
                    (f"read the {dec(rest, places_needed(rest))}% left over as a count of "
                     "people", rest)] + common
    rationale = (f"The {dec(left, 0)} remaining are {dec(rest, places_needed(rest))}% of the "
                 f"{panel}, so {dec(total, 0)} were invited"
                 + (f", and {dec(counts[1], 0)} - {dec(counts[2], 0)} = {dec(key, 0)}."
                    if ask == "difference" else
                    f", of whom {dec(pcts[1], places_needed(pcts[1]))}% is {dec(key, 0)}."
                    if ask == "one_group" else "."))
    fmt = fmt or ("spr" if rng.random() < 0.45 else "mcq")
    if fmt == "spr":
        return spr("pct.remainder_total", "a total from the leftover share", "hard", seed,
                   stem, key, rationale, mistakes=mistakes, params=P)
    return mcq("pct.remainder_total", "a total from the leftover share", "hard", seed,
               stem, key, mistakes, rng, rationale, params=P)


# -------------------------------------------------------- PER SERVING MODEL

def per_serving_model(rng: random.Random, seed: int, *, per=None, amount=None,
                      serving=None, ctx=None, wrongs=None) -> Item:
    """One serving is p% of a daily allowance; x servings is the model in x."""
    brand, food, nutrient, unit = ctx or rng.choice(CEREALS)
    per = q(per if per is not None else rng.choice([2, 4, 5, 6, 8, 15, 20, 25]))
    amount = amount or rng.randrange(20, 400, 10)
    serving = serving or rng.choice(["3/4 cup", "1 cup", "1/2 cup", "2/3 cup", "40 grams"])
    calories = rng.randrange(90, 260, 10)
    from_fat = rng.randrange(10, 80, 10)
    name = rng.choice(["Jennifer", "Aleks", "Marisol", "Ben", "Nadia"])

    stem = (f"{name} bought a box of {brand} {food}. The nutrition facts on the box state "
            f"that a serving size of the {food} is {serving} and provides {calories} "
            f"calories, {from_fat} of which are calories from fat. In addition, each "
            f"serving of the {food} provides {amount} {unit} of {nutrient}, which is "
            f"{dec(per, places_needed(per))}% of the daily allowance for adults. If p "
            f"percent of an adult's daily allowance of {nutrient} is provided by x "
            f"servings of {brand} {food} per day, which of the following expresses p in "
            f"terms of x ?")
    key = f"p = {dec(per, places_needed(per))}x"
    pool = {
        "decimal_slip": ("moved the decimal point one place when converting the percent",
                         f"p = {dec(per / 10, places_needed(per / 10, 3))}x"),
        "decimal_compounded": ("treated each extra serving as compounding, raising the "
                               "decimal form to the power of the number of servings",
                               f"p = ({dec(per / 100, places_needed(per / 100, 4))})^x"),
        "percent_compounded": ("treated each extra serving as multiplying the percent "
                               "again rather than adding another serving's worth of it",
                               f"p = {dec(per, places_needed(per))}^x"),
        "growth_factor": ("treated each extra serving as a repeated percent increase "
                          "rather than a repeated amount",
                          f"p = ({dec(1 + per / 100, places_needed(1 + per / 100, 4))})^x"),
        "divided": ("divided by the percent instead of multiplying by it",
                    f"p = x/{dec(per, places_needed(per))}"),
    }
    # three of the five are printed, so a free draw shuffles rather than leaving
    # the last two in this file for ever -- but the compounded percent is always
    # one of them, because `p = 5^x` is the only distractor printed in the key's
    # own surface form, and a key alone in its form is guessable without reading
    # the stem
    rest = ["decimal_slip", "decimal_compounded", "growth_factor", "divided"]
    order = (["decimal_slip"] + rest[1:] + ["percent_compounded"] if wrongs is not None
             else ["percent_compounded"] + rng.sample(rest, len(rest)))
    wrong = pick(pool, order, wrongs)
    P = {"kind": "pct_per_unit", "per": float(per)}
    rationale = (f"One serving is {dec(per, places_needed(per))}% of the allowance, so x "
                 f"servings is {dec(per, places_needed(per))}x percent of it.")
    return text_mcq("pct.per_serving_model", "a per-unit percent as a model", "hard", seed,
                    stem, key, wrong, rng, rationale, params=P)
