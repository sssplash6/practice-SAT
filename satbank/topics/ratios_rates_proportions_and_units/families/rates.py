"""A rate: one quantity per one unit of another, and what it is asked for.

    unit_rate        a total and a count -> the rate, or either one back again
    rate_convert     the same rate, timed in a different unit
    rate_product     one rate multiplied by a second to reach a third
    gap              two rates over one base -> the amount between them
    growth_table     a rate read off a table of species -> ten years of it
    table_unit_price two foods in a table -> the ratio of their unit prices
    exchange_fee     a rate applied and then a percent taken off it

The error these templates are built around is the inverted rate: dividing
where the item needs a multiplication, or the reverse. It is the one mistake
that survives every context on this topic, so it is a named option on every
template here that has options at all, and the rationale always says which
way the factor goes rather than just naming it.
"""

from __future__ import annotations

import random

from ....item import Item, ItemError
from ..values import (Q, dec, mcq, places_needed, q, sig, snap, spr, text_mcq,
                      unambiguous)

__all__ = ["unit_rate", "rate_convert", "rate_product", "gap", "growth_table",
           "table_unit_price", "exchange_fee"]

SECONDS = {"second": Q(1), "minute": Q(60), "hour": Q(3600), "day": Q(86400)}
NEXT_UP = {"second": "minute", "minute": "hour", "hour": "day"}

# ------------------------------------------------------------------ contexts

FLIERS = [("monarch butterflies", "a group of monarch butterflies",
           "Chicago, Illinois", "Michoacán, Mexico", "butterfly"),
          ("Arctic terns", "a flock of Arctic terns", "Nome, Alaska",
           "Punta Arenas, Chile", "tern"),
          ("gray whales", "a pod of gray whales", "the Bering Sea",
           "Baja California", "whale"),
          ("green turtles", "a group of green turtles", "Ascension Island",
           "the coast of Brazil", "turtle")]

MACHINES = [("wind turbine", "revolutions"), ("centrifuge", "rotations"),
            ("conveyor", "cycles"), ("printing press", "impressions"),
            ("water wheel", "turns")]

HOSTS = [("Makayla", "an event"), ("Devon", "a banquet"), ("Imani", "a fair"),
         ("Raul", "a conference"), ("Beatriz", "a reception")]

PRODUCE = [("oranges", "pound"), ("apples", "pound"), ("walnuts", "pound"),
           ("rice", "kilogram"), ("coffee", "pound")]

GLASSES = [("drinking glass", "Jenny"), ("tumbler", "Owen"), ("mug", "Carla"),
           ("flask", "Nikhil")]


def _s(n) -> str:
    return "" if q(n) == 1 else "s"


def _art(word: str) -> str:
    """'a' or 'an', with the h of 'hour' counted as a vowel the way speech does."""
    return "an" if word[0].lower() in "aeiou" or word.lower().startswith("hou") \
        else "a"


# -------------------------------------------------------------- UNIT RATE

def unit_rate(rng: random.Random, seed: int, *, frame=None, total=None, per=None,
              count=None, vol=None, fmt=None, ctx=None) -> Item:
    """A total, a rate and a count, with one of the three missing.

    total = rate × count, so which of the three the item withholds is what
    makes a migration item and a shopping item two questions rather than one.
    """
    frame = frame or rng.choices(
        ["migration", "turbine", "speed", "room", "buy", "price", "fill"],
        weights=[3, 3, 4, 3, 3, 3, 2])[0]
    ask = {"migration": "rate", "turbine": "rate", "speed": "count",
           "room": "count", "buy": "count", "fill": "count",
           "price": "total"}[frame]
    one, ones, many = "unit", "units", "of the total"
    difficulty = "easy"
    round_to = None
    style = "plain"

    if frame == "migration":
        kind, group, start, finish, one = ctx or rng.choice(FLIERS)
        total = q(total) if total is not None else q(rng.randrange(400, 6000, 50))
        count = q(count) if count is not None else q(rng.randrange(20, 300, 5))
        stem = (f"A group of {kind} migrated from {start} to {finish}, flying a "
                f"total of {dec(total, 0)} miles. It took a single {one} in the "
                f"group {dec(count, 0)} days to travel this route one way. On "
                f"average, how many miles did the {one} travel per day?")
        order = ["inverted", "per_hour", "minus", "plus"]
        one, ones, many = "day", "days", "miles"
        round_to = Q(1, 1000)
        skill = "a unit rate from a total"
    elif frame == "turbine":
        machine, turns = ctx or rng.choice(MACHINES)
        total = q(total) if total is not None else q(rng.randrange(120, 4000, 20))
        count = q(count) if count is not None else q(rng.randrange(5, 120, 5))
        stem = (f"A {machine} completes {dec(total, 0)} {turns} in "
                f"{dec(count, 0)} minutes. At this rate, how many {turns} per "
                f"minute does this {machine} complete?")
        order = ["minus", "plus", "product", "inverted"]
        one, ones, many = "minute", "minutes", turns
        round_to = Q(1, 1000)
        skill = "a unit rate from a total"
    elif frame == "speed":
        per = q(per) if per is not None else q(rng.randrange(2, 40))
        total = q(total) if total is not None else per * q(rng.randrange(2, 60))
        stem = (f"An object travels at a constant speed of {dec(per, 0)} "
                f"centimeters per second. At this speed, what is the time, in "
                f"seconds, that it would take for the object to travel "
                f"{dec(total, 0)} centimeters?")
        order = ["minus", "plus", "product", "rate_itself"]
        one, ones, many = "second", "seconds", "centimeters"
        skill = "a time from a rate"
    elif frame == "room":
        who, event = ctx or rng.choice(HOSTS)
        per = q(per) if per is not None else q(rng.choice([6, 8, 9, 10, 12, 15]))
        total = q(total) if total is not None else per * q(rng.randrange(40, 900))
        stem = (f"{who} is planning {event} in a {dec(total, 0)}-square-foot "
                f"room. If there should be at least {dec(per, 0)} square feet per "
                f"person, what is the maximum number of people that could attend "
                f"this {event.split(' ', 1)[1]}?")
        order = ["product", "minus", "plus", "rate_itself"]
        one, ones, many = "person", "people", "square feet"
        skill = "a count from a rate"
    elif frame == "buy":
        fruit, pound = ctx or rng.choice(PRODUCE)
        per = q(per) if per is not None else q(rng.randrange(2, 20))
        total = q(total) if total is not None else per * q(rng.randrange(2, 40))
        stem = (f"A customer spent ${dec(total, 0)} to purchase {fruit} at "
                f"${dec(per, 0)} per {pound}. How many {pound}s of {fruit} did "
                f"the customer purchase?")
        order = ["minus", "plus", "rate_itself", "product"]
        one, ones, many = pound, pound + "s", "dollars"
        skill = "a count from a rate"
    elif frame == "fill":
        vessel, who = ctx or rng.choice(GLASSES)
        per = q(per) if per is not None else q(rng.choice([4, 8, 10, 12, 16, 20]))
        total = q(total) if total is not None else per * q(rng.randrange(2, 20))
        vol = q(vol) if vol is not None else snap(per * Q(2957, 100), 1)
        stem = (f"A {vessel} can hold a maximum volume of {dec(vol, 0)} cubic "
                f"centimeters, which is approximately {dec(per, 0)} fluid ounces. "
                f"{who} has a pitcher that contains {dec(total, 0)} fluid ounces "
                f"of water. How many times could {who} completely fill the "
                f"{vessel} from the pitcher?")
        order = ["rate_itself", "vol_over_total", "vol_floor", "minus"]
        one, ones, many = "glassful", "glassfuls", "fluid ounces"
        skill = "a count from a rate"
        difficulty = "medium"
    else:                                                            # price
        fruit, pound = ctx or rng.choice(PRODUCE)
        per = q(per) if per is not None else q(rng.randrange(150, 3000)) / 100
        count = q(count) if count is not None else q(rng.randrange(2, 40))
        stem = (f"A product costs {dec(per, 2)} dollars per {pound}. What is the "
                f"cost, in dollars, for {dec(count, 0)} {pound}s of the product?")
        order = ["plus", "minus", "quotient"]
        one, ones, many = pound, pound + "s", "dollars"
        skill = "a total from a rate"

    if ask == "rate":
        if count <= 0 or total <= 0:
            raise ItemError("a rate needs a positive total and a positive count")
        key = total / count
    elif ask == "count":
        if per <= 0 or total <= 0:
            raise ItemError("a count needs a positive rate and a positive total")
        key = total / per
        count = key
    else:
        if per <= 0 or count <= 0:
            raise ItemError("a total needs a positive rate and a positive count")
        key = per * count
        total = key
    if frame in ("room", "fill") and key.denominator != 1:
        raise ItemError("a count of people or of glassfuls has to come out whole")
    if key <= 0:
        raise ItemError("the answer has to be a positive amount")

    P = {"kind": "rr_unit_rate", "ask": ask, "frame": frame,
         "total": float(total), "count": float(count),
         "per": float(per if ask != "rate" else key),
         "vol": float(vol) if vol is not None else 0.0}
    pool = {
        "inverted": ("divided the two the wrong way round, giving the days for "
                     "one mile rather than the miles in one day", count / total),
        "per_hour": ("divided by the hours in those days rather than by the days "
                     "themselves", total / (24 * count) if count else None),
        "minus": ("subtracted one given number from the other, treating a rate "
                  "as a difference", abs(total - (per if ask != "rate" else count))),
        "plus": ("added the two given numbers, treating a rate as a sum",
                 total + (per if ask != "rate" else count)),
        "product": ("multiplied where the total had to be divided by the rate",
                    total * (per if ask != "rate" else count)),
        "rate_itself": ("repeated the rate the item already gave", per),
        "quotient": ("divided the two given numbers instead of multiplying them",
                     (count / per) if ask == "total" and per else None),
        "vol_over_total": ("divided the cubic centimeters by the fluid ounces in "
                           "the pitcher, two measures that do not divide",
                           snap(vol / total, 1) if vol else None),
        "vol_floor": ("did that and dropped the fraction rather than counting "
                      "whole glassfuls", ((vol / total).numerator
                                          // (vol / total).denominator) if vol else None),
    }
    mistakes = [(pool[name][0], pool[name][1]) for name in order
                if pool[name][1] is not None]
    rationale = _unit_rate_why(ask, total, per if ask != "rate" else key,
                               count, key, one, ones, many)
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    if fmt == "spr":
        return spr("rr.unit_rate", skill, difficulty, seed, stem, key, rationale,
                   params=P)
    return mcq("rr.unit_rate", skill, difficulty, seed, stem, key, mistakes, rng,
               rationale, style=style, round_to=round_to, params=P)


def _unit_rate_why(ask, total, per, count, key, one, ones, many) -> str:
    t, r, c = (dec(total, places_needed(total)), dec(per, places_needed(per)),
               dec(count, places_needed(count)))
    k = dec(key, places_needed(key, 3))
    if ask == "rate":
        return (f"A rate per {one} comes from dividing the total by the number "
                f"of {ones}, not the other way round: {t} ÷ {c} = {k} {many} in "
                f"each {one}.")
    if ask == "count":
        return (f"Each {one} accounts for {r} {many}, so the number of {ones} "
                f"is the total divided by that rate: {t} ÷ {r} = {k}.")
    return (f"Each {one} costs {r} {many}, so {c} of them cost {r} × {c} = {k}; "
            f"the rate multiplies here because the count is what grew.")


# ----------------------------------------------------------- RATE CONVERT

MOVERS = [("The International Space Station orbits Earth", "space station"),
          ("A research probe passes the outer planets", "probe"),
          ("A hypersonic aircraft cruises", "aircraft")]

CRAWLERS = [("An insect", "insect"), ("A snail", "snail"),
            ("A tortoise", "tortoise"), ("A glacier", "glacier")]

RIDES = [("On April 18, 1775, Paul Revere set off on his midnight ride from "
          "Charlestown to Lexington. If he had ridden straight to Lexington "
          "without stopping, he would have traveled", "his horse"),
         ("In 1860 a Pony Express rider left Saint Joseph for Marysville. Riding "
          "straight through, he would have traveled", "his horse"),
         ("A courier left the depot for the harbor. Riding straight through "
          "without stopping, she would have traveled", "her bicycle")]


def rate_convert(rng: random.Random, seed: int, *, frame=None, value=None,
                 per_from=None, per_to=None, factor=None, unit_from=None,
                 unit_to=None, dist=None, time=None, places=None, fmt=None,
                 unit="", ctx=None) -> Item:
    """The same speed, timed in a different unit and sometimes measured in one too."""
    frame = frame or rng.choices(["rate", "trip"], weights=[3, 2])[0]

    if frame == "rate":
        per_from = per_from or rng.choice(["second", "minute", "hour"])
        per_to = per_to or rng.choice([u for u in ("second", "minute", "hour")
                                       if u != per_from])
        if per_from == per_to:
            raise ItemError("converting an hour into an hour asks nothing")
        factor = q(factor) if factor is not None else Q(1)
        value = q(value) if value is not None else q(rng.randrange(120, 9000)) / 100
        unit_from = unit_from or "miles"
        unit_to = unit_to or unit_from
        if factor == 1:
            story, who = ctx or rng.choice(MOVERS)
            stem = (f"{story} at an average speed of "
                    f"{dec(value, places_needed(value))} {unit_from} per "
                    f"{per_from}. What is the {who}'s average speed in "
                    f"{unit_to} per {per_to}?")
        else:
            stem = (f"Which of the following speeds is equivalent to "
                    f"{dec(value, places_needed(value))} {unit_from} per "
                    f"{per_from} (1 {unit_from[:-1]} = {dec(factor, 0)} "
                    f"{unit_to})?")
        scale = factor * SECONDS[per_to] / SECONDS[per_from]
        key = value * scale
        skill = "converting the units of a rate"
        difficulty = "medium"
    else:
        story, who = ctx or rng.choice(RIDES)
        dist = q(dist) if dist is not None else q(rng.randrange(4, 60))
        time = q(time) if time is not None else q(rng.randrange(8, 120))
        per_from, per_to = "minute", "hour"
        factor, unit_from, unit_to = Q(1), "mile", "miles"
        value = dist / time
        scale = SECONDS[per_to] / SECONDS[per_from]
        key = value * scale
        places = 1 if places is None else places
        stem = (f"{story} {dec(dist, 0)} miles in {dec(time, 0)} minutes. In such "
                f"a ride, what would the average speed of {who} have been, to the "
                f"nearest tenth of a mile per hour?")
        skill = "a speed in a different unit of time"
        difficulty = "medium"

    if places is not None:
        # a speed that lands exactly between two tenths is answered by a rounding
        # convention the stem never states, so the draw goes back
        key = unambiguous(key, Q(1, 10 ** places))
    if key <= 0:
        raise ItemError("a speed has to be positive")

    P = {"kind": "rr_rate_convert", "value": [value.numerator, value.denominator],
         "per_from": per_from, "per_to": per_to,
         "factor": [factor.numerator, factor.denominator],
         "places": places}
    mid = NEXT_UP.get(per_from) if SECONDS[per_to] > SECONDS[per_from] else None
    if mid and SECONDS[mid] >= SECONDS[per_to]:
        mid = None
    pool = {
        "mid": (f"converted as far as {per_from}s in a {mid} and stopped there"
                if mid else "", value * factor * SECONDS[mid] / SECONDS[per_from]
                if mid else None),
        "sum_factors": ("added the two conversions instead of multiplying them",
                        value * factor * (SECONDS[mid] / SECONDS[per_from]
                                          + SECONDS[per_to] / SECONDS[mid])
                        if mid else None),
        "slip_down": ("moved the decimal point one place", key / 10),
        "slip_up": ("moved the decimal point one place the other way", key * 10),
        "added": ("added the conversion factor instead of multiplying by it",
                  value * factor + (scale if scale > 1 else 1 / scale)),
        "twice": ("converted twice over, applying the same factor again",
                  value * factor * scale * scale),
        "inverted": (f"used the whole conversion upside down, multiplying by "
                     f"{dec(1 / scale, places_needed(1 / scale, 3))} where the "
                     f"rate had to be divided by it" if scale < 1 else
                     f"used the whole conversion upside down, dividing by "
                     f"{dec(scale, places_needed(scale, 3))} where the rate had "
                     f"to be multiplied by it", value / scale),
    }
    order = (["mid", "sum_factors", "slip_down", "added", "inverted", "twice"]
             if SECONDS[per_to] > SECONDS[per_from]
             else ["inverted", "slip_up", "slip_down", "added", "mid",
                   "sum_factors", "twice"])
    mistakes = [(pool[n][0], pool[n][1]) for n in order if pool[n][1] is not None]
    up = SECONDS[per_to] / SECONDS[per_from]
    n_per = dec(max(up, 1 / up), 0)
    if frame == "trip":
        rationale = (f"{dec(dist, 0)} miles in {dec(time, 0)} minutes is a rate "
                     f"of {dec(dist, 0)} ÷ {dec(time, 0)} miles per minute, and "
                     f"there are 60 minutes in an hour, so that rate is "
                     f"multiplied by 60, not divided: {dec(dist, 0)} ÷ "
                     f"{dec(time, 0)} × 60 = {dec(key, places_needed(key, 3))} "
                     f"miles per hour.")
    else:
        rationale = (
            f"There are {n_per} {per_from}s in {_art(per_to)} {per_to}, so a rate "
            f"per {per_from} is {'multiplied' if up > 1 else 'divided'} by "
            f"{n_per} to become a rate per {per_to}"
            + (f", and each {unit_from[:-1]} is {dec(factor, 0)} {unit_to}: "
               f"{dec(value, places_needed(value))} × {dec(factor, 0)} "
               f"{'×' if up > 1 else '÷'} {n_per} = "
               f"{dec(key, places_needed(key, 3))}." if factor != 1 else
               f": {dec(value, places_needed(value))} "
               f"{'×' if up > 1 else '÷'} {n_per} = "
               f"{dec(key, places_needed(key, 3))}."))
    fmt = fmt or ("spr" if rng.random() < 0.35 else "mcq")
    if fmt == "spr":
        return spr("rr.rate_convert", skill, difficulty, seed, stem, key, rationale,
                   params=P)
    return mcq("rr.rate_convert", skill, difficulty, seed, stem, key, mistakes, rng,
               rationale, places=places, unit=unit, params=P)


# ----------------------------------------------------------- RATE PRODUCT

WAXES = [("Pure beeswax", "pure beeswax"), ("Raw honey", "honey"),
         ("Linseed oil", "the oil"), ("Pine resin", "the resin")]
BAKES = [("chocolate", "chocolate muffins", "muffin"),
         ("butter", "shortbread rounds", "round"),
         ("almond paste", "marzipan fruits", "fruit"),
         ("cocoa", "brownies", "brownie")]


def rate_product(rng: random.Random, seed: int, *, frame=None, first=None,
                 second=None, other=None, fmt=None, ctx=None) -> Item:
    """One rate multiplied by a second, so that a unit cancels between them."""
    frame = frame or rng.choice(["density_price", "power_hours", "recipe"])

    if frame == "density_price":
        full, short = ctx or rng.choice(WAXES)
        first = q(first) if first is not None else q(rng.randrange(150, 1500)) / 1000
        second = q(second) if second is not None else q(rng.randrange(200, 2000)) / 100
        key = first * second
        stem = (f"{full} has a density of {dec(first, places_needed(first, 3))} "
                f"ounce per cubic inch. An online company sells {short} at a price "
                f"of ${dec(second, 2)} per ounce. What is the selling price, in "
                f"dollars per cubic inch, for {short} purchased from this company?")
        mistakes = [
            ("divided the price by the density, which cancels nothing",
             second / first),
            ("divided the density by the price", first / second),
            ("added the two rates", first + second),
        ]
        rationale = (f"An ounce costs ${dec(second, 2)} and a cubic inch holds "
                     f"{dec(first, places_needed(first, 3))} ounce, so the ounces "
                     f"cancel when the two are multiplied: "
                     f"{dec(first, places_needed(first, 3))} × {dec(second, 2)} = "
                     f"{dec(key, places_needed(key, 3))}.")
        skill = "multiplying two rates"
        difficulty = "medium"
        figures = None
    elif frame == "power_hours":
        first = q(first) if first is not None else q(rng.randrange(600, 9000))
        second = q(second) if second is not None else q(rng.choice([12, 18, 24, 36, 48]))
        other = q(other) if other is not None else first * q(rng.randrange(150, 400)) / 100
        if other <= first:
            raise ItemError("the whole country cannot hold less than one state")
        key = sig(first * second, 2, strict=True)
        stem = (f"The total power capacity of the nine largest wind projects in "
                f"one state was {dec(first, 0)} megawatts (MW), and the total "
                f"power capacity of the twenty largest wind projects in the "
                f"country was {dec(other, 0)} MW. The amount of energy produced "
                f"in one hour at a rate of one megawatt is one megawatt-hour. If "
                f"each of the nine projects had operated continuously for "
                f"{dec(second, 0)} hours at its maximum rate of power generation, "
                f"approximately how many megawatt-hours of energy would the nine "
                f"projects have produced?")
        mistakes = [
            (f"gave the power capacity itself, never multiplying by the "
             f"{dec(second, 0)} hours it ran for", sig(first, 2)),
            ("used the capacity of all twenty projects rather than the nine",
             sig(other, 2)),
            (f"divided by the {dec(second, 0)} hours where the hours multiply",
             sig(first / second, 2)),
            ("multiplied the twenty projects by the hours instead",
             sig(other * second, 2)),
        ]
        rationale = (f"One megawatt running for one hour is one megawatt-hour, so "
                     f"{dec(first, 0)} MW running for {dec(second, 0)} hours is "
                     f"{dec(first, 0)} × {dec(second, 0)} = "
                     f"{dec(first * second, 0)} megawatt-hours, which is about "
                     f"{dec(key, 0)}.")
        skill = "multiplying a rate by a time"
        difficulty = "hard"
        figures = 2
    else:                                                            # recipe
        stuff, goods, one = ctx or rng.choice(BAKES)
        first = q(first) if first is not None else q(rng.randrange(5, 60)) / 10
        second = q(second) if second is not None else q(rng.randrange(12, 200))
        key = first * second / 16
        stem = (f"To make a bakery's signature {goods}, a baker needs "
                f"{dec(first, places_needed(first))} ounces of {stuff} for each "
                f"{one}. How many pounds of {stuff} are needed to make "
                f"{dec(second, 0)} signature {goods} (1 pound = 16 ounces)?")
        mistakes = [
            ("stopped at the ounces and never divided by the 16 ounces in a "
             "pound", first * second),
            ("added the two given numbers", first + second),
            ("divided by 12 rather than by the 16 ounces in a pound",
             first * second / 12),
            ("multiplied by 16 where the ounces had to be divided by it",
             first * second * 16),
        ]
        rationale = (f"{dec(second, 0)} {goods} need "
                     f"{dec(first, places_needed(first))} × {dec(second, 0)} = "
                     f"{dec(first * second, places_needed(first * second))} ounces, "
                     f"and each pound is 16 ounces, so the ounces are divided by "
                     f"16 to come back to pounds: "
                     f"{dec(key, places_needed(key, 3))}.")
        skill = "a rate with a unit conversion"
        difficulty = "easy"
        figures = None

    if key <= 0:
        raise ItemError("the product has to be a positive amount")
    P = {"kind": "rr_rate_product", "frame": frame, "first": float(first),
         "second": float(second), "other": float(other) if other else 0.0,
         "figures": figures}
    fmt = fmt or ("spr" if rng.random() < 0.3 else "mcq")
    if fmt == "spr":
        return spr("rr.rate_product", skill, difficulty, seed, stem, key, rationale,
                   params=P)
    return mcq("rr.rate_product", skill, difficulty, seed, stem, key, mistakes, rng,
               rationale, params=P)


# ------------------------------------------------------------------- GAP

PLANETS = [("Venus", "Jupiter"), ("Mars", "Neptune"), ("Mercury", "Saturn")]
MOONS = ["a planet", "a gas giant", "the outer planet"]
COUNTRIES = [("Iceland", 1990, 2014), ("Namibia", 1985, 2015),
             ("Mongolia", 1995, 2020), ("Guyana", 1980, 2010)]


def gap(rng: random.Random, seed: int, *, frame=None, base=None, low=None,
        high=None, fmt=None, ctx=None) -> Item:
    """Two rates over the same base, and the amount that lies between them."""
    frame = frame or rng.choice(["planet", "moons", "density"])

    if frame == "planet":
        near, far = ctx or rng.choice(PLANETS)
        base = q(base) if base is not None else q(rng.randrange(50, 500, 10))
        low = q(low) if low is not None else q(rng.randrange(2, 10)) / 10
        high = q(high) if high is not None else q(rng.randrange(12, 40)) / 10
        if high <= low:
            raise ItemError("the far planet has to pull harder")
        key = base * (high - low)
        stem = (f"The weight of an object on {near} is approximately "
                f"{low.numerator}/{low.denominator} of its weight on Earth. The "
                f"weight of an object on {far} is approximately "
                f"{high.numerator}/{high.denominator} of its weight on Earth. If "
                f"an object weighs {dec(base, 0)} pounds on Earth, approximately "
                f"how many more pounds does it weigh on {far} than it weighs on "
                f"{near}?")
        order = ["b_high", "b_low", "b_sum", "b_ratio"]
        skill = "the difference between two proportional amounts"
        difficulty = "easy"
        whole = False
    elif frame == "moons":
        planet = ctx or rng.choice(MOONS)
        low = q(low) if low is not None else q(rng.randrange(30, 400))
        high = q(high) if high is not None else low + q(rng.randrange(5, 120))
        base = q(base) if base is not None else q(rng.randrange(3, 60))
        if high <= low:
            raise ItemError("the second moon has to be the slower one")
        key = base * (high - low)
        stem = (f"One of {planet}'s moons orbits the planet every {dec(low, 0)} "
                f"days. A second moon orbits the planet every {dec(high, 0)} days. "
                f"How many more days does it take the second moon to orbit the "
                f"planet {dec(base, 0)} times than it takes the first moon to "
                f"orbit the planet {dec(base, 0)} times?")
        order = ["b_high", "b_low", "gap_alone", "b_sum"]
        skill = "the difference between two proportional amounts"
        difficulty = "medium"
        whole = False
    else:                                                            # density
        country, y1, y2 = ctx or rng.choice(COUNTRIES)
        low = q(low) if low is not None else q(rng.randrange(8, 60)) / 10
        high = q(high) if high is not None else low + q(rng.randrange(2, 30)) / 10
        base = q(base) if base is not None else q(rng.randrange(20000, 400000, 250))
        if high <= low:
            raise ItemError("the density has to have risen")
        key = base * (high - low)
        stem = (f"The population density of {country}, in people per square "
                f"kilometer of land area, increased from "
                f"{dec(low, places_needed(low))} in {y1} to "
                f"{dec(high, places_needed(high))} in {y2}. During this time "
                f"period, the land area of {country} was {dec(base, 0)} square "
                f"kilometers. By how many people did {country}'s population "
                f"increase from {y1} to {y2}?")
        order = ["b_high", "b_ratio", "b_over_gap", "b_low"]
        skill = "a population change from a density change"
        difficulty = "medium"
        whole = True

    if key <= 0 or places_needed(key, 4) > 3:
        raise ItemError("the difference does not print cleanly")
    P = {"kind": "rr_gap", "frame": frame, "base": [base.numerator, base.denominator],
         "low": [low.numerator, low.denominator],
         "high": [high.numerator, high.denominator]}
    pool = {
        "b_high": ("gave the whole of the larger amount instead of the amount "
                   "between the two", base * high),
        "b_low": ("gave the whole of the smaller amount", base * low),
        "b_sum": ("added the two rates rather than taking the difference",
                  base * (high + low)),
        "b_ratio": ("scaled the base by the ratio of the two rates instead of by "
                    "their difference", base * high / low),
        "b_over_gap": ("divided by the difference of the two rates where the "
                       "difference multiplies", base / (high - low)),
        "gap_alone": ("gave the difference for a single orbit, never multiplying "
                      "by the number of orbits", high - low),
    }
    mistakes = []
    for name in order:
        why, v = pool[name]
        if v is None:
            continue
        if whole:
            v = q(v)
            v = Q(v.numerator // v.denominator)          # a count of people is whole
        mistakes.append((why, v))
    rationale = (f"Both amounts sit on the same base of {dec(base, 0)}, so the "
                 f"amount between them is the base times the difference of the "
                 f"two rates: {dec(base, 0)} × ({dec(high, places_needed(high))} − "
                 f"{dec(low, places_needed(low))}) = {dec(key, places_needed(key, 3))}.")
    fmt = fmt or ("spr" if rng.random() < 0.3 else "mcq")
    if fmt == "spr":
        return spr("rr.gap", skill, difficulty, seed, stem, key, rationale, params=P)
    return mcq("rr.gap", skill, difficulty, seed, stem, key, mistakes, rng,
               rationale, params=P)


# --------------------------------------------------------------- GROWTH TABLE

SPECIES = [("Red maple", Q(45, 10)), ("River birch", Q(35, 10)),
           ("Cottonwood", Q(2)), ("Black walnut", Q(45, 10)),
           ("White birch", Q(5)), ("American elm", Q(4)), ("Pin oak", Q(3)),
           ("Shagbark hickory", Q(75, 10)), ("Sugar maple", Q(55, 10)),
           ("Basswood", Q(3)), ("Quaking aspen", Q(2)), ("Green ash", Q(4)),
           ("Silver maple", Q(3)), ("White oak", Q(5)), ("Ironwood", Q(7)),
           ("Redbud", Q(7))]

# the eight species the source item prints, in its order
TREE_TABLE = SPECIES[:8]


def growth_table(rng: random.Random, seed: int, *, fast=None, slow=None,
                 years=None, feet=None, species=None) -> Item:
    """A table of growth factors, and ten years of the two slowest-agreeing trees."""
    rows = list(species) if species else rng.sample(SPECIES, 8)
    names = [n for n, _ in rows]
    factors = dict(rows)
    fast = fast or rng.choice(names)
    slow = slow or rng.choice([n for n in names if factors[n] != factors[fast]])
    if fast not in factors or slow not in factors:
        raise ItemError("that species is not in the table")
    gf, gs = factors[fast], factors[slow]
    if gf == gs:
        raise ItemError("two species with one growth factor grow alike")
    if gs < gf:
        gf, gs, fast, slow = gs, gf, slow, fast          # `fast` has the smaller factor
    years = int(years) if years is not None else rng.randrange(4, 26)
    feet = int(feet) if feet is not None else rng.choice([1, 1, 2, 3])
    start = 12 * feet
    exact = years * (Q(1) / gf - Q(1) / gs)
    # 21 years of a 3.5 tree and a 4.0 tree differ by exactly 0.75 inches, and
    # "closest to" then has two answers: 0.7 and 0.8 are the same distance away
    # and the pool prints both. `unambiguous` throws that draw away.
    key = unambiguous(exact, Q(1, 10))
    if key <= 0:
        raise ItemError("the two trees would not separate")
    table = [["Species of tree", "Growth factor"]] + \
            [[n, dec(g, 1)] for n, g in rows]
    stem = (f"One method of calculating the approximate age, in years, of a tree "
            f"of a particular species is to multiply the diameter of the tree, in "
            f"inches, by a constant called the growth factor for that species. The "
            f"table above gives the growth factors for {_word(len(rows))} species "
            f"of trees. If {_an(fast)} tree and {_an(slow)} tree each now have a "
            f"diameter of {feet} {'foot' if feet == 1 else 'feet'}, which of the "
            f"following will be closest to "
            f"the difference, in inches, of their diameters {years} years from "
            f"now (1 foot = 12 inches)?")
    P = {"kind": "rr_growth_table", "fast": [gf.numerator, gf.denominator],
         "slow": [gs.numerator, gs.denominator], "years": years, "start": start}
    d_fast, d_slow = start + years / gf, start + years / gs
    mistakes = [
        ("rounded each diameter to a whole number of inches before subtracting",
         snap(d_fast, 1) - snap(d_slow, 1)),
        ("rounded each diameter up to the next tenth of an inch instead of to "
         "the nearest one", _ceil(d_fast, Q(1, 10)) - _ceil(d_slow, Q(1, 10))),
        (f"gave the growth of the {fast.lower()} alone, never subtracting the "
         f"{slow.lower()}", Q(years) / gf),
        ("divided the years by the difference of the two growth factors",
         Q(years) / (gs - gf)),
        ("read the growth factors as inches of growth a year rather than years "
         "per inch of diameter", years * (gs - gf)),
    ]
    rationale = (f"A growth factor of g means g years for each inch of diameter, "
                 f"so a tree gains 1 ÷ g inch a year: the {fast.lower()} gains "
                 f"{years} ÷ {dec(gf, places_needed(gf))} = "
                 f"{dec(years / gf, places_needed(years / gf, 3))} inches in "
                 f"{years} years and the {slow.lower()} gains "
                 f"{dec(years / gs, places_needed(years / gs, 3))}, a difference "
                 f"of about {dec(key, 1)} inches; the starting diameter is the "
                 f"same for both and cancels.")
    return mcq("rr.growth_table", "a rate read from a table", "hard", seed, stem,
               key, mistakes, rng, rationale, places=1, params=P, table=table)


def _ceil(v, step) -> Q:
    """Up to the next multiple of `step`, which is not how rounding works."""
    k = q(v) / q(step)
    n = k.numerator // k.denominator
    return q(step) * (n + (1 if k > n else 0))


def _an(name: str) -> str:
    return ("an " if name[0].lower() in "aeiou" else "a ") + name.lower()


_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
          8: "eight", 9: "nine", 10: "ten"}


def _word(n: int) -> str:
    return _WORDS.get(n, str(n))


# ------------------------------------------------------------ TABLE UNIT PRICE

FOODS = [("1 large egg", "1 cup of milk", "protein", "grams"),
         ("1 slice of bread", "1 cup of oats", "fiber", "grams"),
         ("1 apple", "1 handful of raisins", "sugar", "grams"),
         ("1 can of beans", "1 cup of lentils", "protein", "grams")]


def table_unit_price(rng: random.Random, seed: int, *, amounts=None, costs=None,
                     ctx=None) -> Item:
    """Two foods in a table, and the ratio of what a gram of each costs."""
    first, second, nutrient, unit = ctx or rng.choice(FOODS)
    a1, a2 = amounts or (rng.randrange(2, 20), rng.randrange(2, 20))
    c1, c2 = costs or (q(rng.randrange(5, 99)) / 100, q(rng.randrange(5, 99)) / 100)
    a1, a2, c1, c2 = q(a1), q(a2), q(c1), q(c2)
    if min(a1, a2, c1, c2) <= 0:
        raise ItemError("every entry in the table has to be positive")
    r1, r2 = c1 / a1, c2 / a2
    if r1 == r2:
        raise ItemError("two foods at one unit price make the ratio 1 to 1")
    ratio = r1 / r2
    if max(ratio.numerator, ratio.denominator) > 12:
        raise ItemError("a ratio this unwieldy is not what the item is testing")
    key = _ratio_text(ratio)
    if key == _ratio_text(a1 / a2) or key == _ratio_text(c2 / c1):
        raise ItemError("a wrong route lands on the right ratio")
    table = [["Food", nutrient.capitalize(), "Cost"],
             [first, f"{dec(a1, 0)} {unit}", f"${dec(c1, 2)}"],
             [second, f"{dec(a2, 0)} {unit}", f"${dec(c2, 2)}"]]
    one, two = _named(first), _named(second)
    stem = (f"The table above shows the amount of {nutrient} in two foods and the "
            f"cost of each food. Based on the table, what is the ratio of the cost "
            f"per {unit[:-1]} of {nutrient} in {one} to the cost per "
            f"{unit[:-1]} of {nutrient} in {two}?")
    if (c1 * 100).denominator != 1 or (c2 * 100).denominator != 1:
        raise ItemError("a price has to be a whole number of cents")
    P = {"kind": "rr_table_unit_price", "a1": int(a1), "a2": int(a2),
         "c1": int(c1 * 100), "c2": int(c2 * 100)}
    wrong = [
        ("gave the ratio the other way round", _ratio_text(r2 / r1)),
        (f"compared the two amounts of {nutrient} and never brought the costs in",
         _ratio_text(a1 / a2)),
        ("compared the two costs, ignoring how much each food carries",
         _ratio_text(c2 / c1)),
        ("divided each amount by its cost, the unit rate upside down",
         _ratio_text((a1 / c1) / (a2 / c2))),
    ]
    rationale = (f"A {unit[:-1]} of {nutrient} costs ${dec(c1, 2)} ÷ "
                 f"{dec(a1, 0)} = ${dec(r1, places_needed(r1, 4))} in {one} and "
                 f"${dec(c2, 2)} ÷ {dec(a2, 0)} = ${dec(r2, places_needed(r2, 4))} "
                 f"in {two}, and those two divide to {key}.")
    return text_mcq("rr.table_unit_price", "unit prices compared from a table",
                    "medium", seed, stem, key, wrong, rng, rationale, params=P,
                    table=table)


def _named(food: str) -> str:
    """'1 large egg' is referred to in the question as 'a large egg'."""
    rest = food.split(" ", 1)[1]
    return f"{_art(rest)} {rest}"


def _ratio_text(v) -> str:
    v = q(v)
    return f"{v.numerator} : {v.denominator}"


# ------------------------------------------------------------- EXCHANGE FEE

CURRENCIES = [("pesos", "peso", "Marta", "she"), ("rupees", "rupee", "Anjali", "she"),
              ("koruna", "koruna", "Pavel", "he"), ("forint", "forint", "Eszter", "she"),
              ("rand", "rand", "Thabo", "he"), ("baht", "baht", "Niran", "he")]


def exchange_fee(rng: random.Random, seed: int, *, amount=None, rate=None,
                 fee=None, ctx=None, fmt=None) -> Item:
    """A currency converted at a stated rate, less a percent fee on the result."""
    plural, single, who, they = ctx or rng.choice(CURRENCIES)
    amount = q(amount) if amount is not None else q(rng.randrange(500, 40000, 100))
    rate = q(rate) if rate is not None else q(rng.randrange(15, 400)) / 1000
    fee = q(fee) if fee is not None else q(rng.choice([1, 2, 3, 4, 5]))
    converted = amount * rate
    key = converted * (1 - fee / 100)
    if key <= 0 or places_needed(key, 4) > 2:
        raise ItemError("the payout does not come out to a whole number of cents")
    stem = (f"{who} has {dec(amount, 0)} {plural} {they} will convert to US dollars "
            f"using a currency exchange service. At this time, the currency "
            f"exchange rate is 1 {single} = {dec(rate, places_needed(rate, 4))} US "
            f"dollars. The exchange service will charge {who} a {dec(fee, 0)}% fee "
            f"on the converted US dollar amount. How many US dollars will {who} "
            f"receive from the currency exchange after the {dec(fee, 0)}% fee is "
            f"applied?")
    P = {"kind": "rr_exchange_fee", "amount": float(amount),
         "rate": [rate.numerator, rate.denominator], "fee": float(fee)}
    mistakes = [
        ("converted correctly but never took the fee off", converted),
        ("moved the decimal point one place in the rate", converted * 10),
        (f"divided by the {dec(rate, places_needed(rate, 4))} where each "
         f"{single} buys that many dollars and so multiplies",
         (amount / rate) * (1 - fee / 100)),
        ("subtracted the fee as though it were a number of dollars",
         converted - fee),
    ]
    rationale = (f"Each {single} is worth {dec(rate, places_needed(rate, 4))} US "
                 f"dollars, so the dollars are found by multiplying: "
                 f"{dec(amount, 0)} × {dec(rate, places_needed(rate, 4))} = "
                 f"${dec(converted, 2)}. The fee takes {dec(fee, 0)}% of that, "
                 f"leaving {dec(100 - fee, 0)}%: ${dec(key, 2)}.")
    fmt = fmt or ("spr" if rng.random() < 0.15 else "mcq")
    if fmt == "spr":
        return spr("rr.exchange_fee", "a rate applied and then a fee taken off",
                   "easy", seed, stem, key, rationale, params=P)
    return mcq("rr.exchange_fee", "a rate applied and then a fee taken off", "easy",
               seed, stem, key, mistakes, rng, rationale, style="money", cents=True,
               params=P)
