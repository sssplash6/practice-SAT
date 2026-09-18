"""Angle measure: degrees, radians, and where an angle lands on the circle.

The source set spends a third of this topic on the conversion itself and on
what it means to go round more than once, so the two ideas get a template
each: the 180-degrees-is-pi proportion, and the fact that a point on the
circle is reached by infinitely many positive measures.
"""

from __future__ import annotations

import random
from fractions import Fraction as F

from ....exact import E, PI, Exact
from ....item import Item, ItemError, Mis, assemble
from ..figures import circle_with_points
from ..render import MINUS, num as printed, pi_back, pi_style

__all__ = ["degree_radian", "unit_circle_angle", "coterminal", "exact_trig"]

# Denominators that leave a whole number of degrees: every divisor of 180.
DIVISORS = (2, 3, 4, 5, 6, 9, 10, 12, 15, 18, 20, 30, 36, 45, 60, 90)
LETTERS = ("A", "B", "C", "D", "J", "K", "M", "N", "P", "Q", "R", "S", "T", "X", "Y", "Z")


def _radian_text(c: F) -> str:
    """9pi/20 -- how the source writes a radian measure inside a sentence."""
    return pi_back(E(c, 1))


# ------------------------------------------------------------- the conversion

def degree_radian(rng: random.Random, seed: int, *, mode=None, deg=None, num=None,
                  den=None, ask=None, fmt=None, style=None, frame=None,
                  label=None) -> Item:
    """180 degrees is pi radians, run in either direction.

    `ask="coefficient"` is the source's own variant: the answer is written as
    a multiple of pi and only the multiplier is wanted.
    """
    mode = mode or rng.choice(["to_radians", "to_degrees"])
    style = style or "back"
    lab = label or rng.choice(LETTERS)

    if mode == "to_radians":
        deg = deg or rng.choice(range(5, 901, 5))
        ask = ask or rng.choice(["value", "value", "coefficient"])
        fmt = fmt or ("spr" if ask == "coefficient" else
                      ("spr" if rng.random() < 0.15 else "mcq"))
        turns = F(deg, 180)
        key = E(turns) if ask == "coefficient" else E(turns, 1)
        mistakes = [
            Mis("divided by 360 instead of 180", key / E(2)),
            Mis("divided by 90 instead of 180", key * E(2)),
            Mis("gave pi, the measure of a straight angle, instead of converting",
                E(1) if ask == "coefficient" else PI),
            Mis("multiplied by 180 instead of dividing by it", E(deg * 180, key.pi_exp)),
            Mis("inverted the fraction before converting",
                E(F(180, deg), key.pi_exp) if deg else None),
        ]
        if ask == "coefficient":
            stem = rng.choice([
                f"The number of radians in a {deg}-degree angle can be written as api, where "
                f"a is a constant. What is the value of a ?",
                f"An angle measures {deg} degrees. Its measure in radians can be written as "
                f"api, where a is a constant. What is the value of a ?",
            ]).replace("api", "aπ")
            rationale = (f"{deg} degrees is {deg}/180 of a straight angle, so it is "
                         f"{_radian_text(turns)} radians and a = {key.plain()}.")
        else:
            stem = rng.choice([
                f"The measure of angle {lab} is {deg}°. What is the measure, in radians, "
                f"of angle {lab}?",
                f"An angle has a measure of {deg}°. What is the measure of the angle, in "
                f"radians?",
                f"What is the measure, in radians, of an angle that measures {deg}°?",
            ])
            rationale = (f"Multiplying by π/180 gives {deg}(π/180) = "
                         f"{_radian_text(turns)} radians.")
        skill = "degrees to radians"
    else:
        den = den or rng.choice(DIVISORS)
        num = num or rng.randint(1, 4 * den)
        c = F(num, den)
        if c.denominator == 1 or F(180 * num, den).denominator != 1:
            raise ItemError("this radian measure is not a whole number of degrees")
        ask = "value"
        fmt = fmt or ("spr" if rng.random() < 0.5 else "mcq")
        key = E(180 * c)
        mistakes = [
            Mis("multiplied by 360/pi instead of 180/pi", key * E(2)),
            Mis("used 90 degrees for a straight angle", key / E(2)),
            Mis("gave the measure of the rest of a full turn", E(360) - key),
            Mis("inverted the fraction before converting", E(180 / c)),
            Mis("multiplied only the numerator by 180", E(180 * num)),
        ]
        stem = rng.choice([
            f"An angle has a measure of {_radian_text(c)} radians. What is the measure of the "
            f"angle in degrees?",
            f"An angle has a measure of {_radian_text(c)} radians. What is the measure of the "
            f"angle, in degrees?",
            f"The measure of angle {lab} is {_radian_text(c)} radians. What is the measure, in "
            f"degrees, of angle {lab}?",
        ])
        rationale = (f"Multiplying by 180/π gives ({_radian_text(c)})(180/π) = "
                     f"{key.plain()} degrees.")
        skill = "radians to degrees"

    mistakes = [m for m in mistakes if m.value is not None]
    P = {"kind": "circles_degree_radian", "mode": mode, "ask": ask,
         "deg": deg if mode == "to_radians" else None,
         "num": None if mode == "to_radians" else num,
         "den": None if mode == "to_radians" else den}
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("a radian measure with pi in it cannot be gridded in")
        return Item("circles.degree_radian", skill, "medium", seed, stem, "spr", key,
                    key.gridin(), rationale, params=P)
    choices, latex, reasons, letter = assemble(key, mistakes, rng, fmt_value=pi_style(style))
    return Item("circles.degree_radian", skill, "medium", seed, stem, "mcq", key, letter,
                rationale, choices, reasons, latex, params=P)


# ------------------------------------------------- angles stacked on a circle

def unit_circle_angle(rng: random.Random, seed: int, *, a=None, b=None, ask=None,
                      fmt=None, style=None, labels=None) -> Item:
    """Two angles are marked off each end of a diameter; the third is left over."""
    a = a or rng.choice(range(10, 86, 5))
    b = b or rng.choice(range(10, 86, 5))
    middle = 180 - a - b
    if middle <= 0:
        raise ItemError("the two marked angles leave nothing between them")
    ask = ask or rng.choice(["radians", "radians", "degrees"])
    fmt = fmt or "mcq"
    style = style or "back"
    p, q, r, t = labels or rng.choice([("P", "Q", "R", "T"), ("A", "B", "C", "D"),
                                       ("J", "K", "L", "M"), ("W", "X", "Y", "Z")])

    def ang(deg):
        return E(F(deg, 180), 1) if ask == "radians" else E(deg)

    key = ang(middle)
    mistakes = [
        Mis("subtracted only one of the two marked angles from 180 degrees", ang(180 - a)),
        Mis("added the two marked angles instead of subtracting them from 180",
            ang(a + b)),
        Mis("subtracted the marked angles from a full turn instead of a straight angle",
            ang(360 - a - b)),
        Mis("halved the angle that was left", key / E(2)),
        Mis("subtracted only the other marked angle from 180 degrees", ang(180 - b)),
    ]
    same = a == b
    given = (f"The degree measures of angles {p}O{q} and {r}O{t} are each {a}°." if same
             else f"The degree measures of angles {p}O{q} and {r}O{t} are {a}° and "
                  f"{b}°, respectively.")
    asked = ("What is the radian measure of angle " if ask == "radians"
             else "What is the degree measure of angle ")
    stem = rng.choice([
        f"In the xy-plane above, points {p}, {q}, {r}, and {t} lie on the circle with center "
        f"O. {given} {asked}{q}O{r} ?",
        f"Points {p}, {q}, {r}, and {t} lie on the circle shown, which has center O. {given} "
        f"{asked}{q}O{r} ?",
    ])
    far, near = f"{t} ({MINUS}1, 0)", f"{p} (1, 0)"
    fig = circle_with_points({far: 180, near: 0, q: a, r: 180 - b},
                             radii=(far, near, q, r))
    rationale = (f"{p}, O and {t} are collinear, so angle {q}O{r} is "
                 f"180 {MINUS} {a} {MINUS} {b} = "
                 f"{middle} degrees, which is {key.plain()}" +
                 (" radians." if ask == "radians" else " degrees."))
    P = {"kind": "circles_unit_circle_angle", "a": a, "b": b, "ask": ask}
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("a radian answer with pi in it cannot be gridded in")
        return Item("circles.unit_circle_angle", "central angles", "medium", seed, stem,
                    "spr", key, key.gridin(), rationale, figure=fig, params=P)
    choices, latex, reasons, letter = assemble(key, mistakes, rng, fmt_value=pi_style(style))
    return Item("circles.unit_circle_angle", "central angles", "medium", seed, stem, "mcq",
                key, letter, rationale, choices, reasons, latex, figure=fig, params=P)


# --------------------------------------------------------- going round again

QUARTERS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def _at(spot: int, radius: int) -> str:
    x, y = QUARTERS[spot % 4]
    return f"({printed(x * radius)}, {printed(y * radius)})"


def coterminal(rng: random.Random, seed: int, *, spot=None, radius=None, k=None,
               alts=None, fmt="mcq", labels=None) -> Item:
    """One point on the circle, infinitely many positive measures that reach it.

    The two named points are opposite ends of a diameter, so every measure of
    the angle is an odd multiple of pi. The distractors are the other places a
    large multiple of pi can stop: back at the start, or a quarter turn away.
    """
    spot = rng.choice([0, 1, 2, 3]) if spot is None else spot
    radius = radius or rng.randint(1, 12)
    k = k if k is not None else rng.randint(1, 20)
    f, g, h = labels or rng.choice([("F", "G", "H"), ("A", "O", "B"), ("P", "C", "Q"),
                                    ("R", "G", "S"), ("X", "O", "Y"), ("J", "O", "K"),
                                    ("M", "C", "N"), ("U", "G", "V")])
    key = E(1 + 2 * k, 1)

    if alts is None:
        alts = [2 * rng.randint(max(1, k - 6), k + 6)]
        for half in (F(1, 2), F(3, 2)):
            alts.append(half + 2 * rng.randint(max(1, k - 6), k + 6))
    mistakes = []
    for c in alts:
        c = F(c)
        lands = (spot + 2 * c) % 4
        if lands.denominator != 1:
            continue
        lands = int(lands)
        if lands == (spot + 2) % 4:
            continue                    # that measure would also reach the far point
        if lands == spot % 4:
            why = (f"an even multiple of π is a whole number of full turns, which ends "
                   f"back at {f}")
        else:
            why = (f"a half-integer multiple of π stops a quarter turn away, at "
                   f"{_at(lands, radius)}")
        mistakes.append(Mis(why, E(c, 1)))

    axis = "y" if spot % 2 == 0 else "x"
    opp = _at(spot + 2, radius)
    unknown = (opp.split(", ")[0] + f", {axis})" if axis == "y"
               else f"({axis}, " + opp.split(", ")[1])
    circle = "a unit circle" if radius == 1 else f"a circle of radius {radius}"
    stem = rng.choice([
        f"Point {f} lies on {circle} in the xy-plane and has coordinates "
        f"{_at(spot, radius)}. Point {g} is "
        f"the center of the circle and has coordinates (0, 0). Point {h} also lies on the "
        f"circle and has coordinates {unknown}, where {axis} is a constant. Which of the "
        f"following could be the positive measure of angle {f}{g}{h}, in radians?",
        f"In the xy-plane, point {g} is the center of {circle}, point {f} on the circle has "
        f"coordinates {_at(spot, radius)}, and point {h} on the circle has coordinates "
        f"{unknown}, where {axis} is a constant. Which of the following could be the positive "
        f"measure of angle {f}{g}{h}, in radians?",
    ])
    rationale = (f"{h} must be {opp}, the far end of the diameter through {f}, so angle "
                 f"{f}{g}{h} is a half turn plus any whole number of full turns: "
                 f"π + {2 * k}π = {key.plain()}.")
    P = {"kind": "circles_coterminal", "spot": spot, "radius": radius, "k": k}
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("circles.coterminal", "coterminal angles", "hard", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex, params=P)


# ------------------------------------------------- exact values on the circle

HALF_ROOT3 = E(F(1, 2), 0, 3)
HALF_ROOT2 = E(F(1, 2), 0, 2)
HALF = E(F(1, 2))

COS = {0: E(1), 30: HALF_ROOT3, 45: HALF_ROOT2, 60: HALF, 90: E(0),
       120: -HALF, 135: -HALF_ROOT2, 150: -HALF_ROOT3, 180: E(-1),
       210: -HALF_ROOT3, 225: -HALF_ROOT2, 240: -HALF, 270: E(0),
       300: HALF, 315: HALF_ROOT2, 330: HALF_ROOT3}
TAN = {0: E(0), 30: E(F(1, 3), 0, 3), 45: E(1), 60: E(1, 0, 3),
       120: -E(1, 0, 3), 135: E(-1), 150: -E(F(1, 3), 0, 3), 180: E(0),
       210: E(F(1, 3), 0, 3), 225: E(1), 240: E(1, 0, 3),
       300: -E(1, 0, 3), 315: E(-1), 330: -E(F(1, 3), 0, 3)}


def _cos(deg: int) -> Exact:
    return COS[deg % 360]


def _sin(deg: int) -> Exact:
    return COS[(90 - deg) % 360]


def exact_trig(rng: random.Random, seed: int, *, fn=None, num=None, den=None,
               fmt="mcq") -> Item:
    """The cosine or sine of a large multiple of pi/6, pi/4 or pi/3.

    The work is the reduction: strip whole turns, land on a reference angle,
    read the value off the circle.
    """
    fn = fn or rng.choice(["cos", "sin"])
    den = den or rng.choice([3, 4, 6])
    num = num or rng.randint(2, 600)
    reduced = num % (2 * den)
    deg = 180 * reduced // den
    if 180 * reduced % den:
        raise ItemError("this angle is not a whole number of degrees")
    key = _cos(deg) if fn == "cos" else _sin(deg)
    if key.rad == 1:
        raise ItemError("only the radical values keep four look-alike options")

    other = _sin(deg) if fn == "cos" else _cos(deg)
    sign = E(1) if key.coef > 0 else E(-1)
    partner = sign * (HALF_ROOT2 if key.rad == 3 else HALF_ROOT3)
    mistakes = [
        Mis("used the 45-degree reference value" if key.rad == 3 else
            "used the 30-degree reference value", partner),
        Mis(f"gave the {'sine' if fn == 'cos' else 'cosine'} of the angle instead", other),
        Mis("dropped the 2 in the denominator of the reference value", key * E(2)),
        Mis("subtracted the wrong number of full turns and landed on 0 radians",
            _cos(0) if fn == "cos" else _sin(0)),
    ]
    tan = TAN.get(deg % 360)
    if tan is not None and tan.rad == 1 and tan.coef != 0:
        mistakes.append(Mis("gave the tangent of the angle instead", tan))

    c = F(num, den)
    stem = rng.choice([
        f"What is the value of {fn} {pi_back(E(c, 1))} ?",
        f"What is the value of {fn} {pi_back(E(c, 1))}, where the angle is measured in "
        f"radians?",
    ])
    rationale = (f"{pi_back(E(c, 1))} and {pi_back(E(F(reduced, den), 1))} differ by whole "
                 f"turns, so {fn} {pi_back(E(c, 1))} = {fn} {pi_back(E(F(reduced, den), 1))} "
                 f"= {key.plain()}.")
    P = {"kind": "circles_exact_trig", "fn": fn, "num": num, "den": den}
    choices, latex, reasons, letter = assemble(key, mistakes, rng, signed=True)
    return Item("circles.exact_trig", "the unit circle", "easy", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex, params=P)
