"""Arcs and central angles.

Everything here is one proportion -- arc length is to the circumference as the
central angle is to 360 degrees -- read in whichever direction the item leaves
unknown, plus the two places the source dresses it up: a circle cut into two
arcs, and a chord whose base angle has to become a central angle first.
"""

from __future__ import annotations

import random
from fractions import Fraction as F

from ....exact import E, PI, Exact
from ....item import Item, ItemError, Mis, assemble
from ....shapes import UNITS
from ..figures import circle_with_points
from ..render import pi_style

__all__ = ["arc", "arc_pair", "arc_fraction", "arc_angle", "chord_angle", "sector"]

# Central angles that cut a circle into a tidy fraction, as the source uses.
ANGLES = (10, 15, 18, 20, 24, 30, 36, 40, 45, 50, 60, 72, 75, 80, 90, 100, 108,
          120, 135, 140, 144, 150, 160, 180, 200, 210, 216, 225, 240, 270, 300, 315, 330)

PAIRS = (("A", "B"), ("A", "C"), ("B", "C"), ("M", "N"), ("P", "Q"), ("R", "S"),
         ("J", "K"), ("X", "Y"))

CM, IN, M, FT, U = UNITS
ARC_UNITS = (None, CM, IN, M, FT)


def _unit_words(unit) -> str:
    return "" if unit is None else f" {unit.many()}"


def _in_units(noun: str, unit) -> str:
    """'the length, in inches,' -- the SAT's construction, dropped when the
    source states no unit at all."""
    return f"the {noun}, in {unit.many()}," if unit else f"the {noun}"


def _amount(text: str, unit) -> str:
    return f"{text}{_unit_words(unit)}"


def _place(rng: random.Random, theta: int) -> dict:
    """Where the two named points sit on the drawn circle."""
    start = rng.choice((20, 40, 60, 110, 135, 150, 200, 250, 300, 340))
    return start, (start + theta) % 360


def _spr(key: Exact) -> str:
    if not key.is_rational:
        raise ItemError("an arc length with pi in it cannot be entered in a grid-in")
    return key.gridin()


# ------------------------------------------------------------------ arc <-> C

def arc(rng: random.Random, seed: int, *, mode=None, given=None, theta=None,
        size=None, unit=..., fmt=None, frame=None, labels=None, style=None) -> Item:
    """The proportion itself: a circle's size and a central angle give the arc,
    and an arc with its degree measure gives the circle back."""
    mode = mode or rng.choice(["arc", "arc", "whole"])
    theta = theta or rng.choice(ANGLES)
    if unit is ...:
        unit = rng.choice(ARC_UNITS)
    style = style or "back"
    fmt = fmt or ("spr" if rng.random() < 0.3 else "mcq")
    a, b = labels or rng.choice(PAIRS)
    frac = F(theta, 360)

    if mode == "arc":
        given = given or rng.choice(["circumference", "circumference", "radius", "diameter"])
        if given == "circumference":
            c = E(size) if size else E(frac.denominator * rng.randint(2, 16))
            circumference = c
            stated = f"a circumference of {_amount(c.plain(), unit)}"
        else:
            d = E(size) if size else E(rng.randint(2, 30))
            circumference = E(2) * PI * d if given == "radius" else PI * d
            if F(int(d.coef) * theta, 180).denominator > 4:
                raise ItemError("this radius and angle give an untidy arc")
            stated = f"a {given} of {_amount(d.plain(), unit)}"
        key = circumference * E(frac)
        mistakes = [
            Mis("gave the whole circumference instead of the arc", circumference),
            Mis("used half the circle instead of the given central angle",
                circumference / E(2)),
            Mis("gave the rest of the circle, the major arc", circumference - key),
            Mis("used 360/theta in place of theta/360", circumference / E(frac)),
            Mis("used 180 degrees for a whole circle", circumference * E(frac) * E(2)),
        ]
        frame = frame or rng.choice(["figure", "text", "text"])
        fig = None
        if frame == "figure":
            p1, p2 = _place(rng, theta)
            fig = circle_with_points({a: p1, b: p2}, radii=(a, b), angle=(a, b),
                                     angle_label=None if theta == 90 else f"{theta}°")
            stem = rng.choice([
                f"The circle above with center O has {stated}. "
                f"What is {_in_units('length', unit)} of minor arc {a}{b}?",
                f"The circle shown has center O and {stated}. "
                f"What is {_in_units('length', unit)} of arc {a}{b}?",
            ])
        else:
            stem = rng.choice([
                f"A circle has {stated}. What is {_in_units('length', unit)} of an arc on "
                f"this circle whose central angle measures {theta}°?",
                f"Points {a} and {b} lie on a circle with {stated}. The measure of arc "
                f"{a}{b} is {theta}°. What is {_in_units('length', unit)} of arc {a}{b}?",
                f"In a circle with {stated}, central angle {a}O{b} measures {theta}°. "
                f"What is {_in_units('length', unit)} of arc {a}{b}?",
            ])
        rationale = (f"The arc takes {theta}/360 of the circle, so its length is "
                     f"({theta}/360)({circumference.plain()}) = {key.plain()}.")
        P = {"kind": "circles_arc", "mode": "arc", "theta": theta,
             "circumference": float(circumference)}
        skill = "arc length"
    else:
        length = E(size) if size else E(frac.numerator * rng.randint(1, 20))
        circumference = length / E(frac)
        key = circumference
        mistakes = [
            Mis("gave the length of the arc again instead of the whole circumference", length),
            Mis("doubled the arc, as if any arc were half the circle", E(2) * length),
            Mis("used 180 degrees for a whole circle", length / E(frac) / E(2)),
            Mis("multiplied by theta/360 instead of dividing", length * E(frac)),
            Mis("gave the length of the rest of the circle", circumference - length),
        ]
        stem = rng.choice([
            f"A circle has center O, and points {a} and {b} lie on the circle. The measure of "
            f"arc {a}{b} is {theta}° and the length of arc {a}{b} is "
            f"{_amount(length.plain(), unit)}. What is {_in_units('circumference', unit)} of "
            f"the circle?",
            f"An arc of a circle has a measure of {theta}° and a length of "
            f"{_amount(length.plain(), unit)}. What is {_in_units('circumference', unit)} of "
            f"the circle?",
            f"On a circle, arc {a}{b} has a measure of {theta}° and a length of "
            f"{_amount(length.plain(), unit)}. What is {_in_units('circumference', unit)} of "
            f"the circle?",
        ])
        rationale = (f"The arc is {theta}/360 of the circle, so the circumference is "
                     f"{length.plain()} ÷ ({theta}/360) = {key.plain()}.")
        P = {"kind": "circles_arc", "mode": "whole", "theta": theta, "length": float(length)}
        fig = None
        skill = "circumference from an arc"

    if fmt == "spr":
        return Item("circles.arc", skill, "medium", seed, stem, "spr", key,
                    _spr(key), rationale, figure=fig, params=P)
    choices, latex, reasons, letter = assemble(key, mistakes, rng, fmt_value=pi_style(style))
    return Item("circles.arc", skill, "medium", seed, stem, "mcq", key, letter,
                rationale, choices, reasons, latex, figure=fig, params=P)


# ---------------------------------------------------------- two arcs, one circle

def arc_pair(rng: random.Random, seed: int, *, mode=None, minor=None, ratio=None,
             theta=None, length=None, pi=None, unit=..., fmt=None, labels=None,
             style=None, figure=None) -> Item:
    """Two points cut a circle into a minor and a major arc.

    Either both arcs are given and the circumference is wanted, or one arc and
    its central angle are given and the other arc is wanted.
    """
    mode = mode or rng.choice(["sum", "other"])
    if unit is ...:
        unit = rng.choice(ARC_UNITS)
    style = style or "back"
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    a, b = labels[:2] if labels else rng.choice(PAIRS)
    c = labels[2] if labels and len(labels) > 2 else rng.choice(
        [p for p in "PQRSTVW" if p not in (a, b)])

    if mode == "sum":
        small = E(minor) if minor else E(rng.randint(3, 60))
        mult = ratio or rng.choice([2, 3, 4, 5, 6, 7])
        big = small * E(mult)
        key = small + big
        mistakes = [
            Mis("gave the minor arc instead of the whole circumference", small),
            Mis("gave the major arc instead of the whole circumference", big),
            Mis("subtracted the two arcs instead of adding them", big - small),
            Mis("doubled the major arc", E(2) * big),
        ]
        stem = rng.choice([
            f"Points {a}, {b}, and {c} lie on the circle shown. On this circle, minor arc "
            f"{a}{b} has a length of {_amount(small.plain(), unit)} and major arc {a}{c}{b} "
            f"has a length of {_amount(big.plain(), unit)}. What is "
            f"{_in_units('circumference', unit)} of the circle shown?",
            f"Points {a}, {b}, and {c} lie on a circle. Minor arc {a}{b} has a length of "
            f"{_amount(small.plain(), unit)} and major arc {a}{c}{b} has a length of "
            f"{_amount(big.plain(), unit)}. What is {_in_units('circumference', unit)} of "
            f"the circle?",
        ])
        rationale = (f"The two arcs make up the whole circle, so the circumference is "
                     f"{small.plain()} + {big.plain()} = {key.plain()}.")
        P = {"kind": "circles_arc_pair", "mode": "sum", "minor": float(small),
             "major": float(big)}
        share = float(small) / float(key)
        half = 180.0 * share
        fig = (circle_with_points({a: round(90 + half, 1), b: round(90 - half, 1), c: 270},
                                  center=None)
               if figure is not False else None)
    else:
        theta = theta or rng.choice([t for t in ANGLES if t < 180])
        frac = F(theta, 360)
        step = frac.numerator
        if length is not None:
            given = E(length, 1 if pi else 0)
        else:
            pi = rng.random() < 0.5 if pi is None else pi
            given = (E(step * rng.randint(1, 9), 1) if pi
                     else E(step * rng.randint(1, 14)))
        circumference = given / E(frac)
        key = circumference - given
        mistakes = [
            Mis("gave the whole circumference instead of the remaining arc", circumference),
            Mis("halved the circumference instead of subtracting the given arc",
                circumference / E(2)),
            Mis("halved the remaining arc", key / E(2)),
            Mis("gave the arc that was already given", given),
        ]
        p1, p2 = _place(rng, theta)
        d_lab = rng.choice([p for p in "DEFGH" if p not in (a, b, c)])
        fig = circle_with_points({a: p1, b: (p1 + 180 + theta // 2) % 360,
                                  c: p2, d_lab: (p1 + theta / 2) % 360},
                                 radii=(a, c), angle=(a, c),
                                 angle_label="x°") if figure is not False else None
        stem = rng.choice([
            f"The circle above has center O, the length of arc {a}{d_lab}{c} "
            f"is {_amount(given.plain(), unit)}, and x = {theta}. What is "
            f"{_in_units('length', unit)} of arc {a}{b}{c}?",
            f"In the circle shown with center O, arc {a}{d_lab}{c} has a central angle of "
            f"x = {theta} degrees and a length of {_amount(given.plain(), unit)}. What is "
            f"{_in_units('length', unit)} of arc {a}{b}{c}?",
        ])
        rationale = (f"The given arc is {theta}/360 of the circle, so the circumference is "
                     f"{circumference.plain()} and the rest of the circle is "
                     f"{circumference.plain()} - {given.plain()} = {key.plain()}.")
        P = {"kind": "circles_arc_pair", "mode": "other", "theta": theta,
             "given": float(given)}

    if fmt == "spr":
        return Item("circles.arc_pair", "arcs of a circle", "medium", seed, stem, "spr",
                    key, _spr(key), rationale, figure=fig, params=P)
    choices, latex, reasons, letter = assemble(key, mistakes, rng, fmt_value=pi_style(style))
    return Item("circles.arc_pair", "arcs of a circle", "medium", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex, figure=fig, params=P)


# --------------------------------------------------- what share of the circle

def arc_fraction(rng: random.Random, seed: int, *, r=None, frac=None, fmt=None,
                 labels=None) -> Item:
    """An arc length against the radius: what fraction of the circumference is it."""
    fmt = fmt or ("spr" if rng.random() < 0.6 else "mcq")
    a, b = labels or rng.choice(PAIRS)
    r = E(r) if r else E(rng.randint(1, 24))
    frac = (F(*frac) if isinstance(frac, tuple) else F(frac)) if frac else F(
        rng.choice([1, 1, 1, 2, 3, 5]), rng.choice([3, 4, 5, 6, 8, 9, 10, 12]))
    if not 0 < frac < 1 or frac == F(1, 2):
        raise ItemError("the arc must be a proper part of the circle, and not a half")
    length = E(2) * PI * r * E(frac)
    key = E(frac)
    mistakes = [
        Mis("compared the arc with half the circumference", key * E(2)),
        Mis("compared the arc with twice the circumference", key / E(2)),
        Mis("gave the share the rest of the circle takes up", E(1) - key),
        Mis("compared the arc with a quarter of the circumference", key * E(4)),
    ]
    stem = rng.choice([
        f"Points {a} and {b} lie on a circle with radius {r.plain()}, and arc {a}{b} has "
        f"length {length.plain()}. What fraction of the circumference of the circle is the "
        f"length of arc {a}{b} ?",
        f"On a circle with radius {r.plain()}, arc {a}{b} has length {length.plain()}. What "
        f"fraction of the circumference of the circle is the length of arc {a}{b} ?",
    ])
    rationale = (f"The circumference is 2π({r.plain()}) = {(E(2) * PI * r).plain()}, so "
                 f"the arc is {length.plain()} ÷ {(E(2) * PI * r).plain()} = "
                 f"{key.plain()} of it.")
    P = {"kind": "circles_arc_fraction", "r": float(r), "num": frac.numerator,
         "den": frac.denominator, "length": float(length)}
    if fmt == "spr":
        return Item("circles.arc_fraction", "arc as a share of the circle", "hard", seed,
                    stem, "spr", key, key.gridin(), rationale, params=P)
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("circles.arc_fraction", "arc as a share of the circle", "hard", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex, params=P)


# ------------------------------------------------- arc measure and its angle

def arc_angle(rng: random.Random, seed: int, *, theta=None, ask=None, fmt=None,
              labels=None) -> Item:
    """The degree measure of an arc is the measure of its central angle.

    Simple enough to look like a trick, which is why the source asks it: the
    distractors are the inscribed-angle halving and the major arc.
    """
    theta = theta or rng.randint(1, 359)
    ask = ask or rng.choice(["angle", "arc", "major"])
    fmt = fmt or ("spr" if rng.random() < 0.5 else "mcq")
    a, b = labels or rng.choice(PAIRS)
    key = E(360 - theta) if ask == "major" else E(theta)
    if key.coef <= 0:
        raise ItemError("a major arc needs a minor arc to be left over")
    if ask == "angle":
        stem = rng.choice([
            f"Point O is the center of a circle. The measure of arc {a}{b} on this circle is "
            f"{theta}°. What is the measure, in degrees, of its associated angle "
            f"{a}O{b}?",
            f"In a circle with center O, the measure of arc {a}{b} is {theta}°. What is "
            f"the measure, in degrees, of central angle {a}O{b}?",
        ])
        rationale = (f"A central angle has the same measure as the arc it cuts off, so angle "
                     f"{a}O{b} measures {theta}°.")
    elif ask == "arc":
        stem = rng.choice([
            f"Point O is the center of a circle, and points {a} and {b} lie on the circle. "
            f"The measure of angle {a}O{b} is {theta}°. What is the measure, in degrees, "
            f"of arc {a}{b}?",
            f"In a circle with center O, central angle {a}O{b} measures {theta}°. What "
            f"is the measure, in degrees, of minor arc {a}{b}?",
        ])
        rationale = (f"An arc has the same measure as its central angle, so arc {a}{b} "
                     f"measures {theta}°.")
    else:
        stem = rng.choice([
            f"Point O is the center of a circle, and points {a} and {b} lie on the circle. "
            f"The measure of angle {a}O{b} is {theta}°. What is the measure, in degrees, "
            f"of major arc {a}{b}?",
            f"In a circle with center O, minor arc {a}{b} measures {theta}°. What is the "
            f"measure, in degrees, of major arc {a}{b}?",
        ])
        rationale = (f"The two arcs make a full turn, so the major arc measures 360 - "
                     f"{theta} = {key.plain()} degrees.")
    minor = E(360) - key if ask == "major" else key
    mistakes = [
        Mis("gave the major arc instead of the minor one" if ask != "major"
            else "gave the minor arc instead of the major one", E(360) - key),
        Mis("halved the measure, as an inscribed angle would", key / E(2)),
        Mis("doubled the measure, as if the angle were inscribed", key * E(2)),
        Mis("subtracted from 180 degrees instead of 360", E(180) - key),
        Mis("halved the arc that was given", minor / E(2)),
        Mis("took a quarter of the measure", key / E(4)),
    ]
    # nothing on a circle measures more than a full turn, and no source item
    # prints half a degree, so either would be crossed off without arithmetic
    mistakes = [m for m in mistakes
                if m.value is not None and m.value.is_integer and 0 < float(m.value) <= 360]
    P = {"kind": "circles_arc_angle", "theta": theta, "ask": ask}
    if fmt == "spr":
        return Item("circles.arc_angle", "arc measure", "easy", seed, stem, "spr", key,
                    key.gridin(), rationale, params=P)
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    if any(float(c.replace(",", "")) > 360 for c in choices):
        # a filler slipped past the named mistakes; no arc measures more than a
        # full turn, so the draw is thrown away rather than shipped
        raise ItemError("an option came out larger than a full turn")
    return Item("circles.arc_angle", "arc measure", "easy", seed, stem, "mcq", key, letter,
                rationale, choices, reasons, latex, params=P)


# --------------------------------------------- a chord, and the triangle it makes

def chord_angle(rng: random.Random, seed: int, *, base=None, r=None, ask=None,
                fmt=None, labels=None, via=None, style=None, figure=None) -> Item:
    """Two radii and a chord make an isosceles triangle.

    The item gives a base angle, so the central angle has to be recovered as
    180 - 2*base before the arc can be found -- which is what the distractors
    are built out of.
    """
    base = base or rng.choice([10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75])
    central = 180 - 2 * base
    if central <= 0:
        raise ItemError("the base angles leave no central angle")
    r = E(r) if r else E(rng.randint(2, 40))
    ask = ask or rng.choice(["arc", "arc", "central"])
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    style = style or "back"
    a, b = labels[:2] if labels else rng.choice(PAIRS)
    third = via or (labels[2] if labels and len(labels) > 2 else
                    rng.choice([p for p in "CDEFG" if p not in (a, b)]))
    circumference = E(2) * PI * r
    frac = F(central, 360)
    if F(int(r.coef) * central, 180).denominator > 4:
        raise ItemError("this radius and base angle give an untidy arc")

    if ask == "central":
        key = E(central)
        mistakes = [
            Mis("used the base angle as the central angle", E(base)),
            Mis("doubled the base angle instead of subtracting twice it from 180",
                E(2 * base)),
            Mis("subtracted the base angle from 180 only once", E(180 - base)),
            Mis("subtracted the base angle from 90", E(90 - base)),
        ]
        asked = f"what is the measure, in degrees, of angle {a}O{b}?"
        rationale = (f"O{a} and O{b} are radii, so the triangle is isosceles and angle O{b}{a} "
                     f"also measures {base} degrees. That leaves 180 - 2({base}) = {central} "
                     f"degrees at the center.")
    else:
        key = circumference * E(frac)
        mistakes = [
            Mis("used 180 - base as the central angle, forgetting the second base angle",
                circumference * E(F(180 - base, 360))),
            Mis("treated the chord as a diameter and halved the circumference",
                circumference / E(2)),
            Mis("used the base angle itself as the central angle",
                circumference * E(F(base, 360))),
            Mis("doubled the base angle, as if it were an inscribed angle",
                circumference * E(F(2 * base, 360))),
            Mis("gave the whole circumference", circumference),
        ]
        asked = f"what is the length of arc {a}{b} ?"
        rationale = (f"O{a} and O{b} are radii, so angle O{b}{a} also measures {base} degrees "
                     f"and the central angle is 180 - 2({base}) = {central} degrees. The "
                     f"circumference is {circumference.plain()}, so the arc is "
                     f"({central}/360)({circumference.plain()}) = {key.plain()}.")

    fig = (circle_with_points({a: 90 + central / 2, b: 90 - central / 2, third: 270},
                              radii=(a, b, third), chords=((a, b),))
           if figure is not False else None)
    if via is not None or rng.random() < 0.5:
        lead = (f"Point O is the center of the circle above, and the measure of angle O{a}{b} "
                f"is {base}°. If the length of O{third} is {r.plain()}, ")
    else:
        lead = (f"Point O is the center of the circle above, the measure of angle O{a}{b} is "
                f"{base}°, and the radius of the circle is {r.plain()}. ")
    stem = lead + (asked[0].upper() + asked[1:] if lead.rstrip().endswith(".") else asked)
    P = {"kind": "circles_chord_angle", "base": base, "r": float(r), "ask": ask}
    if fmt == "spr":
        return Item("circles.chord_angle", "chords and central angles", "hard", seed, stem,
                    "spr", key, _spr(key), rationale, figure=fig, params=P)
    choices, latex, reasons, letter = assemble(key, mistakes, rng, fmt_value=pi_style(style))
    return Item("circles.chord_angle", "chords and central angles", "hard", seed, stem, "mcq",
                key, letter, rationale, choices, reasons, latex, figure=fig, params=P)


# ------------------------------------------------------------------- sectors

def sector(rng: random.Random, seed: int, *, r=None, theta=None, ask=None, fmt=None,
           style=None, unit=...) -> Item:
    """The slice, not the crust: theta/360 of the area, and the angle back out of it."""
    theta = theta or rng.choice([t for t in ANGLES if t < 360])
    r = E(r) if r else E(rng.randint(2, 24))
    ask = ask or rng.choice(["area", "area", "angle"])
    fmt = fmt or ("spr" if rng.random() < 0.3 else "mcq")
    style = style or "back"
    if unit is ...:
        unit = rng.choice(ARC_UNITS)
    frac = F(theta, 360)
    whole = PI * r ** 2
    area = whole * E(frac)

    if ask == "area":
        key = area
        area_units = (f"the area, in square {unit.many()}," if unit else "the area")
        mistakes = [
            Mis("found the arc length, not the sector area", E(2) * PI * r * E(frac)),
            Mis("found the area of the whole circle", whole),
            Mis("forgot to square the radius", PI * r * E(frac)),
            Mis("used the diameter in place of the radius", PI * (E(2) * r) ** 2 * E(frac)),
            Mis("used 180 degrees for a whole circle", area * E(2)),
        ]
        stem = rng.choice([
            f"A sector of a circle with a radius of {_amount(r.plain(), unit)} has a central "
            f"angle measuring {theta}°. What is {area_units} of this sector?",
            f"In a circle with a radius of {_amount(r.plain(), unit)}, a sector has a central "
            f"angle of {theta}°. What is {area_units} of the sector?",
        ])
        rationale = (f"The sector is {theta}/360 of the circle, whose area is "
                     f"{whole.plain()}, so the sector has area {key.plain()}.")
    else:
        key = E(theta)
        mistakes = [
            Mis("did not square the radius when finding the whole circle's area", key * r),
            Mis("divided by the circumference instead of by the area", key * r / E(2)),
            Mis("used 180 degrees for a whole circle", key / E(2)),
            Mis("compared the circle with the sector instead of the sector with the circle",
                E(360) / E(frac) / E(1)),
            Mis("subtracted the sector's share from 360 degrees", E(360) - key),
        ]
        stem = rng.choice([
            f"A sector of a circle with a radius of {r.plain()} has an area of "
            f"{area.plain()}. What is the measure, in degrees, of the central angle of this "
            f"sector?",
            f"In a circle with a radius of {r.plain()}, a sector has an area of "
            f"{area.plain()}. What is the measure, in degrees, of the sector's central angle?",
        ])
        rationale = (f"The whole circle has area {whole.plain()}, so the sector is "
                     f"{frac.numerator}/{frac.denominator} of it and its central angle is "
                     f"{theta} degrees.")
    P = {"kind": "circles_sector", "r": float(r), "theta": theta, "ask": ask,
         "area": float(area)}
    if fmt == "spr":
        return Item("circles.sector", "sector area", "medium", seed, stem, "spr", key,
                    _spr(key), rationale, params=P)
    choices, latex, reasons, letter = assemble(key, mistakes, rng, fmt_value=pi_style(style))
    return Item("circles.sector", "sector area", "medium", seed, stem, "mcq", key, letter,
                rationale, choices, reasons, latex, params=P)
