"""Units: a measure carried from one unit to another, and the two measures --
density and population density -- that are units in disguise.

    convert        one stated conversion factor, used once (or twice, for an area)
    convert_chain  two stated factors, one after the other
    pop_density    people per square mile <-> square miles
    cube_density   mass, volume and density of a cube, any one of the three missing

Every one of these can be got wrong in the same way: by multiplying where the
factor has to divide. That inverted rate is a named option on all four, and
the rationale never just names the factor -- it says which way it goes, which
is the only part a student who got it wrong did not already know.
"""

from __future__ import annotations

import random

from ....item import Item, ItemError
from ..values import (Q, dec, frac_text, mcq, places_needed, q, root, sig,
                      spr, unambiguous)

__all__ = ["convert", "convert_chain", "pop_density", "cube_density"]

# (plural small unit, singular small, singular big, plural big, factor)
UNITS = [
    ("inches", "inch", "yard", "yards", 36),
    ("inches", "inch", "foot", "feet", 12),
    ("feet", "foot", "yard", "yards", 3),
    ("yards", "yard", "mile", "miles", 1760),
    ("grams", "gram", "kilogram", "kilograms", 1000),
    ("milligrams", "milligram", "gram", "grams", 1000),
    ("millimeters", "millimeter", "meter", "meters", 1000),
    ("centimeters", "centimeter", "meter", "meters", 100),
    ("meters", "meter", "kilometer", "kilometers", 1000),
    ("ounces", "ounce", "pound", "pounds", 16),
    ("teaspoons", "teaspoon", "tablespoon", "tablespoons", 3),
    ("fluid ounces", "fluid ounce", "cup", "cups", 8),
    ("cups", "cup", "quart", "quarts", 4),
    ("quarts", "quart", "gallon", "gallons", 4),
    ("minutes", "minute", "hour", "hours", 60),
]

ANIMALS = [("kangaroo", "mass"), ("wombat", "mass"), ("condor", "mass"),
           ("otter", "mass"), ("tapir", "mass"), ("anteater", "mass")]

LENGTHS = [("rope", "length"), ("cable", "length"), ("garden hose", "length"),
           ("footbridge", "length"), ("ribbon", "length"), ("awning", "length")]

MASS_UNITS = {"grams", "kilograms", "milligrams", "ounces", "pounds"}
LENGTH_UNITS = {"inches", "feet", "yards", "miles", "millimeters",
                "centimeters", "meters", "kilometers"}

RACERS = [("A participant in a bicycle race completes the race with an average "
           "speed of", "average speed"),
          ("A triathlon is a multisport race consisting of three different legs. "
           "A triathlon participant completed the cycling leg with an average "
           "speed of", "average speed"),
          ("A competition consisted of four different events. One participant "
           "completed the first event with an average speed of", "average speed"),
          ("A rowing eight finishes the course at an average speed of",
           "average speed"),
          ("A skier completes the descent at an average speed of", "average speed")]

CRAWLERS = [("An insect", "insect"), ("A snail", "snail"), ("A beetle", "beetle")]

PARKS = [("park", "A certain park"), ("reserve", "A nature reserve"),
         ("estate", "A country estate"), ("airfield", "A disused airfield")]


def _show(v, style: str) -> str:
    return frac_text(v) if style == "frac" else dec(v, places_needed(v, 3))


def _art(word: str) -> str:
    """'a' or 'an', with the h of 'hour' counted as a vowel the way speech does."""
    return "an" if word[0].lower() in "aeiou" or word.lower().startswith("hou") \
        else "a"


# ---------------------------------------------------------------- CONVERT

def convert(rng: random.Random, seed: int, *, n=None, factor=None, op=None,
            power: int = 1, frame=None, units=None, stmt: str = "big_first",
            style: str = "plain", n_places=None, fmt=None, ctx=None) -> Item:
    """One stated conversion factor, applied in the direction the item asks for."""
    small, small1, big1, big, factor_default = units or rng.choice(UNITS)
    factor = q(factor) if factor is not None else q(factor_default)
    if factor <= 1 or factor.denominator != 1:
        raise ItemError("a conversion factor here is a whole number bigger than one")
    op = op or rng.choice(["mul", "div"])
    frame = frame or rng.choices(["bare", "object", "rate", "area"],
                                 weights=[5, 3, 3, 1])[0]
    if frame == "area" and (power != 2 or op != "div"):
        power, op = 2, "div"
    if power not in (1, 2):
        raise ItemError("a length converts once and an area twice")

    f = factor ** power
    if n is None:
        n = q(rng.randrange(2, 200)) * (f if op == "div" else 1)
    n = q(n)
    if n <= 0:
        raise ItemError("a measure has to be positive")
    key = n * f if op == "mul" else n / f
    from_u, to_u = (big, small) if op == "mul" else (small, big)
    if power == 2:
        from_u, to_u = f"square {from_u}", f"square {to_u}"
    said = (f"1 {big1} = {dec(factor, 0)} {small}" if stmt == "big_first"
            else f"{dec(factor, 0)} {small} = 1 {big1}")
    shown = _show(n, style) if n_places is None else dec(n, n_places)

    if frame == "bare":
        stem = f"How many {to_u} are equivalent to {shown} {from_u} ({said})?"
        skill = "converting between two units"
        difficulty = "easy"
    elif frame == "object":
        if ctx:
            thing, measure = ctx
        elif {small, big} <= MASS_UNITS:
            thing, measure = rng.choice(ANIMALS)
        elif {small, big} <= LENGTH_UNITS:
            thing, measure = rng.choice(LENGTHS)
        else:
            raise ItemError("nothing in this frame is measured in these units")
        stem = (f"{_art(thing).capitalize()} {thing} has a {measure} of {shown} "
                f"{from_u}. What is the {thing}'s {measure}, in {to_u} ({said})?")
        skill = "converting between two units"
        difficulty = "easy"
    elif frame == "rate":
        if not {small, big} <= LENGTH_UNITS:
            raise ItemError("nothing travels at so many quarts a second")
        per = "hour" if factor > 100 else "second"
        if op == "div" and factor <= 100:
            who, thing = ctx or rng.choice(CRAWLERS)
            stem = (f"{who} moves at a speed of {shown} {from_u} per {per}. What "
                    f"is this speed, in {to_u} per {per} ({said})?")
        else:
            story, _ = ctx or rng.choice(RACERS)
            stem = (f"{story} {shown} {from_u} per {per}. What is this "
                    f"speed, in {to_u} per {per} ({said})?")
        skill = "converting the units of a rate"
        difficulty = "medium"
    else:
        word, opening = ctx or rng.choice(PARKS)
        stem = (f"{opening} has an area of {shown} {from_u}. What is the area, "
                f"in {to_u}, of this {word} ({said})?")
        skill = "converting between two units of area"
        difficulty = "hard"

    if key <= 0:
        raise ItemError("the converted measure has to be positive")
    P = {"kind": "rr_convert", "n": [n.numerator, n.denominator],
         "factor": int(factor), "op": op, "power": power}
    whole = n.denominator == 1 and factor.denominator == 1
    pool = {
        "add": (f"added the {dec(factor, 0)} instead of multiplying by it", n + f),
        "factor_less": (f"used {dec(factor - 1, 0)} {small} to the {big1} rather "
                        f"than {dec(factor, 0)}", n * (factor - 1)),
        "factor_more": (f"used {dec(factor + 1, 0)} {small} to the {big1}",
                        n * (factor + 1)),
        "subtract": ("subtracted the two numbers, treating a conversion as a "
                     "difference", abs(n - f) if whole else None),
        "square": (f"multiplied the measure by itself instead of by "
                   f"{dec(factor, 0)}", n * n),
        "inverted": (f"divided by {dec(f, 0)} where each {big1} is {dec(f, 0)} "
                     f"{small} and so multiplies" if op == "mul" else
                     f"multiplied by {dec(f, 0)} where {dec(f, 0)} {small} make "
                     f"one {big1} and so divide", n / f if op == "mul" else n * f),
        "reciprocal": (f"divided the {dec(f, 0)} by the measure rather than the "
                       f"measure by the {dec(f, 0)}", f / n),
        "div_twice": (f"divided by {dec(factor, 0)} twice over", n / (f * factor)),
        "div_once": (f"divided by {dec(factor, 0)} once, as though an area "
                     f"converted like a length", n / factor),
        "sqrt_n": ("took the square root of the area, which gives a side length "
                   "rather than an area", root(n, 2, 2)),
        "sqrt_key": ("took the square root of the converted area as well",
                     root(key, 2, 2)),
    }
    if power == 2:
        order = ["div_once", "sqrt_n", "sqrt_key", "inverted"]
    elif op == "mul":
        order = (["add", "subtract", "square", "inverted"] if factor >= 100
                 else ["add", "factor_less", "factor_more", "subtract", "inverted"])
    else:
        order = ["inverted", "subtract", "reciprocal", "div_twice", "factor_less"]
    mistakes = [(pool[k][0], pool[k][1]) for k in order if pool[k][1] is not None]

    each = (f"each {big1} is {dec(factor, 0)} {small}" if power == 1 else
            f"each square {big1[:-1] if big1.endswith('s') else big1} is "
            f"{dec(factor, 0)} × {dec(factor, 0)} = {dec(f, 0)} square {small}")
    way = (f"so a number of {big} multiplies by {dec(f, 0)} to give the {small}"
           if op == "mul" else
           f"so the {small} divide by {dec(f, 0)} to come back to {big}")
    rationale = (f"{each.capitalize()}, {way}: {shown} "
                 f"{'×' if op == 'mul' else '÷'} {dec(f, 0)} = "
                 f"{_show(key, style)}.")
    fmt = fmt or ("spr" if rng.random() < 0.3 else "mcq")
    if fmt == "spr":
        return spr("rr.convert", skill, difficulty, seed, stem, key, rationale,
                   mistakes=mistakes, params=P)
    return mcq("rr.convert", skill, difficulty, seed, stem, key, mistakes, rng,
               rationale, style=style, round_to=Q(1, 1000) if style != "frac" else None,
               params=P)


# ---------------------------------------------------------- CONVERT CHAIN

CHAINS = [
    ("furlongs", "furlong", "yards", "yard", "feet", "foot", 220, 3),
    ("leagues", "league", "miles", "mile", "yards", "yard", 3, 1760),
    ("quarts", "quart", "cups", "cup", "fluid ounces", "fluid ounce", 4, 8),
    ("gallons", "gallon", "quarts", "quart", "pints", "pint", 4, 2),
    ("days", "day", "hours", "hour", "minutes", "minute", 24, 60),
    ("fathoms", "fathom", "yards", "yard", "inches", "inch", 2, 36),
    ("kilograms", "kilogram", "grams", "gram", "milligrams", "milligram", 1000, 1000),
    ("hectares", "hectare", "ares", "are", "square meters", "square meter", 100, 100),
]


def convert_chain(rng: random.Random, seed: int, *, n=None, f1=None, f2=None,
                  units=None, stmt: str = "forward", fmt=None) -> Item:
    """Two stated factors, one after the other: furlongs to yards to feet."""
    a, a1, b, b1, c, c1, d1, d2 = units or rng.choice(CHAINS)
    f1 = int(f1) if f1 is not None else d1
    f2 = int(f2) if f2 is not None else d2
    if f1 < 2 or f2 < 2:
        raise ItemError("a link in the chain has to be more than one")
    n = q(n) if n is not None else q(rng.randrange(2, 400))
    if n <= 0:
        raise ItemError("a distance has to be positive")
    key = n * f1 * f2
    said = (f"1 {a1} = {f1:,} {b} and 1 {b1} = {f2:,} {c}" if stmt == "forward"
            else f"{f2:,} {c} = 1 {b1} and {f1:,} {b} = 1 {a1}")
    stem = (f"A distance of {dec(n, 0)} {a} is equivalent to how many {c} ({said})?"
            if a in ("furlongs", "leagues", "fathoms")
            else f"How many {c} are equivalent to {dec(n, 0)} {a} ({said})?")
    P = {"kind": "rr_convert_chain", "n": [n.numerator, n.denominator],
         "f1": f1, "f2": f2}
    upside_down = n / (f1 * f2)
    mistakes = [
        (f"stopped at {b} and never took the {f2:,} {c} in {_a(b1)} {b1}",
         n * f1),
        (f"used only the {f2:,} and left the {f1:,} out", n * f2),
        ("divided by both factors where the chain multiplies by them",
         upside_down if upside_down >= Q(1, 100) else None),
        (f"multiplied by {f1:,} and divided by {f2:,}", n * f1 / f2),
        ("added the two factors instead of multiplying by both in turn",
         n * (f1 + f2)),
    ]
    rationale = (f"Each {a1} is {f1:,} {b} and each {b1} is {f2:,} {c}, so both "
                 f"factors multiply: {dec(n, 0)} × {f1:,} = "
                 f"{dec(n * f1, 0)} {b}, and {dec(n * f1, 0)} × {f2:,} = "
                 f"{dec(key, 0)} {c}.")
    fmt = fmt or ("spr" if rng.random() < 0.5 else "mcq")
    if fmt == "spr":
        return spr("rr.convert_chain", "a conversion in two steps", "medium", seed,
                   stem, key, rationale, mistakes=mistakes, params=P)
    return mcq("rr.convert_chain", "a conversion in two steps", "medium", seed, stem,
               key, mistakes, rng, rationale, params=P)


def _a(word: str) -> str:
    return _art(word)


# ------------------------------------------------------------- POP DENSITY

PLACES = ["Worthington", "Cedar County", "Ashford", "Lakemont", "Rivas County",
          "Bellhaven", "Draymoor", "Kestrel County"]
COASTALS = ["a coastal city", "an island borough", "a harbor district",
            "a lakeside township"]


def pop_density(rng: random.Random, seed: int, *, ask="area", density=None,
                people=None, total=None, water=None, year=None, place=None,
                fmt=None) -> Item:
    """People per square mile against square miles, the two ways round."""
    if ask == "area":
        place = place or rng.choice(PLACES)
        density = q(density) if density is not None else q(rng.randrange(20, 900, 10))
        area = q(rng.randrange(10, 900))
        people = q(people) if people is not None else density * area
        if density <= 0 or people <= 0:
            raise ItemError("a density and a population are both positive")
        key = people / density
        if key.denominator != 1:
            raise ItemError("the area has to come out to a whole number of miles")
        stem = (f"The population density of {place} is {dec(density, 0)} people "
                f"per square mile. {'The county' if 'County' in place else place} "
                f"has a population of {dec(people, 0)} people. What is the area, "
                f"in square miles, of {place}?")
        P = {"kind": "rr_pop_density", "ask": "area", "density": float(density),
             "people": float(people), "total": 0.0, "water": 0.0}
        mistakes = [
            ("added the density to the population, as though a density were a "
             "count of people", people + density),
            ("moved the decimal point one place", key / 10),
            ("squared the area because the unit is square miles, though the "
             "division has already produced an area", key * key),
            ("subtracted the density from the population", abs(people - density)),
            ("multiplied where the population had to be divided by the density",
             people * density),
        ]
        rationale = (f"Each square mile holds {dec(density, 0)} people, so the "
                     f"number of square miles is the population divided by that "
                     f"density: {dec(people, 0)} ÷ {dec(density, 0)} = "
                     f"{dec(key, 0)}.")
        skill = "an area from a population density"
        difficulty = "easy"
    else:
        place = place or rng.choice(COASTALS)
        total = q(total) if total is not None else q(rng.randrange(200, 2000)) / 10
        water = q(water) if water is not None else q(rng.randrange(10, int(total * 6))) / 10
        year = int(year) if year is not None else rng.randrange(1980, 2021)
        people = q(people) if people is not None else q(rng.randrange(20, 900)) * 1000
        land = total - water
        if land <= 0 or water <= 0 or people <= 0:
            raise ItemError("the land area has to be what is left after the water")
        key = sig(people / land, 3, strict=True)
        stem = (f"The total area of {place} is {dec(total, places_needed(total))} "
                f"square miles, of which {dec(water, places_needed(water))} square "
                f"miles is water. If the city had a population of "
                f"{dec(people, 0)} people in the year {year}, which of the "
                f"following is closest to the population density, in people per "
                f"square mile of land area, of the city at that time?")
        P = {"kind": "rr_pop_density", "ask": "density", "density": 0.0,
             "people": float(people), "total": float(total), "water": float(water)}
        mistakes = [
            ("divided by the total area, water included, rather than by the land "
             "area", sig(people / total, 3)),
            ("divided by the water area instead of by the land", sig(people / water, 3)),
            ("moved the decimal point one place", sig(people * 10 / land, 3)),
            ("subtracted the water area from the population", abs(people - water)),
        ]
        rationale = (f"The land area is "
                     f"{dec(total, places_needed(total))} − "
                     f"{dec(water, places_needed(water))} = "
                     f"{dec(land, places_needed(land))} square miles, and the "
                     f"density is people per square mile of it: {dec(people, 0)} ÷ "
                     f"{dec(land, places_needed(land))} ≈ {dec(key, 0)}.")
        skill = "a population density from a land area"
        difficulty = "medium"

    fmt = fmt or ("spr" if ask == "area" and rng.random() < 0.35 else "mcq")
    if fmt == "spr":
        return spr("rr.pop_density", skill, difficulty, seed, stem, key, rationale,
                   mistakes=mistakes, params=P)
    return mcq("rr.pop_density", skill, difficulty, seed, stem, key, mistakes, rng,
               rationale, params=P)


# ------------------------------------------------------------ CUBE DENSITY

SOLIDS = [("a certain type of wood", "kilograms", "cubic meter", "meter", "meters"),
          ("a certain solid substance", "kilograms", "cubic meter", "meter", "meters"),
          ("a certain polymer", "kilograms", "cubic meter", "meter", "meters")]

SAMPLES = [("To study fluctuations in composition, samples of pumice were taken "
            "from", "locations", "pumice"),
           ("To study the moisture content in a group of trees, samples from the "
            "trunk of each tree were taken from", "trees", "wood"),
           ("To study the porosity of a reef, samples of coral were taken from",
            "sites", "coral")]




def cube_density(rng: random.Random, seed: int, *, ask="mass", frame=None,
                 density=None, edge=None, mass=None, places=None, sites=None,
                 edge_places: int = 2, density_places=None, fmt=None,
                 ctx=None) -> Item:
    """Mass, density and the edge of a cube: any one of the three from the other two.

    Density is a rate like any other -- so many kilograms in each cubic meter
    -- and the cube is only there to turn one length into a volume. The
    mistakes are the rate's: multiplying by the edge rather than by the
    volume, and running the rate upside down.
    """
    frame = frame or ("solid" if ask != "density" else "sample")

    if ask == "edge":
        solid, munit, vunit, eunit, eunits = ctx or rng.choice(SOLIDS)
        density = q(density) if density is not None else q(rng.randrange(120, 1200))
        mass = q(mass) if mass is not None else q(rng.randrange(120, 1200))
        if density <= 0 or mass <= 0:
            raise ItemError("a density and a mass are both positive")
        places = 2 if places is None else places
        key = root(mass / density, 3, places)
        stem = (f"The density of {solid} is {dec(density, 0)} {munit} per "
                f"{vunit}. A sample of "
                f"{'this type of wood' if 'wood' in solid else 'this substance'} "
                f"is in the shape of a cube and has a mass of {dec(mass, 0)} "
                f"{munit}. To the nearest hundredth of a {eunit}, what is the "
                f"length of one edge of this sample?")
        P = {"kind": "rr_cube_density", "ask": "edge", "density": float(density),
             "mass": float(mass), "edge": 0.0, "places": places}
        mistakes = [
            ("gave the volume of the cube rather than the length of one edge",
             mass / density),
            ("divided the density by the mass, the rate upside down, and then "
             "took the cube root", root(density / mass, 3, places)),
            ("did both: the rate upside down, and the volume left as the edge",
             density / mass),
            ("took the square root instead of the cube root",
             root(mass / density, 2, places)),
        ]
        rationale = (f"Density is mass per unit of volume, so the volume is the "
                     f"mass divided by the density: {dec(mass, 0)} ÷ "
                     f"{dec(density, 0)} = "
                     f"{dec(mass / density, places_needed(mass / density, 4))} "
                     f"cubic {eunits}. A cube of that volume has an edge equal to "
                     f"its cube root, which is {dec(key, places)} to the nearest "
                     f"hundredth.")
        skill = "the edge of a cube from its density"
        round_to = Q(1, 10 ** places)
    elif ask == "mass":
        edge = q(edge) if edge is not None else q(rng.randrange(2, 32)) / 10
        if edge == 1:
            raise ItemError("a unit edge makes the mass equal the density")
        if frame == "solid":
            solid, munit, vunit, eunit, eunits = ctx or rng.choice(SOLIDS)
            density = q(density) if density is not None else q(rng.randrange(120, 1200))
            places = 0 if places is None else places
            stem = (f"The density of {solid} is {dec(density, 0)} {munit} per "
                    f"{vunit}. A sample of this substance is in the shape of a "
                    f"cube, where each edge has a length of "
                    f"{dec(edge, edge_places)} {eunits}. To the nearest whole "
                    f"number, what is the mass, in {munit}, of this sample?")
        else:
            opening, sitesword, stuff = ctx or rng.choice(SAMPLES)
            sites = int(sites) if sites is not None else rng.randrange(8, 60)
            density = q(density) if density is not None else q(rng.randrange(5, 400)) / 1000
            munit, eunit, eunits, vunit = "grams", "centimeter", "centimeters", \
                "cubic centimeter"
            dp = (places_needed(density, 4) if density_places is None
                  else density_places)
            stem = (f"{opening} {sites} {sitesword} and cut in the shape of a "
                    f"cube. The length of the edge of one of these cubes is "
                    f"{dec(edge, edge_places)} centimeters. This cube has a "
                    f"density of {dec(density, dp)} grams per cubic centimeter. "
                    f"What is the mass of this cube, in grams?")
        if density <= 0 or edge <= 0:
            raise ItemError("a density and an edge are both positive")
        exact = density * edge ** 3
        # "to the nearest whole number" needs one nearest whole number: 420 kg
        # per cubic meter in a 1.50 m cube is 1,417.5, which is a convention
        # rather than an answer
        key = (unambiguous(exact, Q(1, 10 ** places)) if places is not None
               else exact)
        P = {"kind": "rr_cube_density", "ask": "mass", "density": float(density),
             "mass": 0.0, "edge": [edge.numerator, edge.denominator],
             "places": places}
        mistakes = [
            ("multiplied by the edge instead of by the volume, so two of the "
             "three dimensions were never used", density * edge),
            ("divided by the edge where the density multiplies by the volume",
             density / edge),
            ("divided by the volume instead of multiplying by it",
             density / edge ** 3),
            ("multiplied by the area of one face rather than the volume",
             density * edge ** 2),
        ]
        rationale = (f"The cube's volume is "
                     f"{dec(edge, edge_places)}{_CUBE} = "
                     f"{dec(edge ** 3, places_needed(edge ** 3, 4))} cubic "
                     f"{eunits}, and each {vunit} has a mass of "
                     f"{dec(density, places_needed(density, 4))} {munit}, so the "
                     f"mass multiplies: {dec(density, places_needed(density, 4))} × "
                     f"{dec(edge ** 3, places_needed(edge ** 3, 4))} = "
                     f"{dec(key, places if places is not None else places_needed(key, 3))}.")
        skill = "the mass of a cube from its density"
        round_to = Q(1, 10 ** places) if places is not None else None
    else:                                                          # density
        opening, sitesword, stuff = ctx or rng.choice(SAMPLES)
        sites = int(sites) if sites is not None else rng.randrange(8, 60)
        edge = q(edge) if edge is not None else q(rng.randrange(10, 60)) / 10
        if edge == 1:
            raise ItemError("a unit edge collapses the density mistakes")
        mass = q(mass) if mass is not None else q(rng.randrange(20, 900)) / 100
        if edge <= 0 or mass <= 0:
            raise ItemError("an edge and a mass are both positive")
        key = mass / edge ** 3
        stem = (f"{opening} {sites} {sitesword} and cut in the shape of a cube. "
                f"The length of the edge of one of these cubes is "
                f"{dec(edge, edge_places)} centimeters. If this cube has a mass "
                f"of {dec(mass, 2)} grams, what is the density of this cube, in "
                f"grams per cubic centimeter?")
        P = {"kind": "rr_cube_density", "ask": "density", "density": 0.0,
             "mass": float(mass), "edge": [edge.numerator, edge.denominator],
             "places": places}
        mistakes = [
            ("divided by the edge rather than by the volume", mass / edge),
            ("multiplied the mass by the volume instead of dividing by it",
             mass * edge ** 3),
            ("divided by the area of one face", mass / edge ** 2),
            ("turned the rate upside down, giving the volume for each gram",
             edge ** 3 / mass),
        ]
        rationale = (f"The cube's volume is {dec(edge, edge_places)}{_CUBE} = "
                     f"{dec(edge ** 3, places_needed(edge ** 3, 4))} cubic "
                     f"centimeters, and density is the mass in one of those, so "
                     f"the mass is divided by the volume: {dec(mass, 2)} ÷ "
                     f"{dec(edge ** 3, places_needed(edge ** 3, 4))} = "
                     f"{dec(key, places_needed(key, 3))} g/cm{_CUBE}.")
        skill = "the density of a cube"
        round_to = None

    if key <= 0:
        raise ItemError("the answer has to be a positive measure")
    fmt = fmt or ("spr" if rng.random() < 0.4 else "mcq")
    if fmt == "spr":
        return spr("rr.cube_density", skill, "hard", seed, stem, key, rationale,
                   mistakes=mistakes, round_to=round_to, params=P)
    return mcq("rr.cube_density", skill, "hard", seed, stem, key, mistakes, rng,
               rationale, places=places, round_to=round_to, params=P)


_CUBE = "³"
