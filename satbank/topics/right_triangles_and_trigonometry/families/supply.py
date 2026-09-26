"""Numeric right-triangle questions for the easy grid-in pool."""

from __future__ import annotations

import random
from fractions import Fraction

from ....exact import E
from ....item import Item, Mis, gridin_mistakes

TRIPLES = ((3, 4, 5), (5, 12, 13), (8, 15, 17))


def hypotenuse_grid(rng: random.Random, seed: int) -> Item:
    a, b, c = rng.choice(TRIPLES)
    k = rng.randint(1, 4)
    a, b, c = a * k, b * k, c * k
    key = E(c)
    return Item(
        "rtt.hypotenuse_grid", "Pythagorean theorem", "easy", seed,
        f"The legs of a right triangle are {a} and {b} units long. "
        "What is the length of its hypotenuse?",
        "spr", key, key.gridin(),
        f"By the Pythagorean theorem, the hypotenuse is "
        f"√({a}² + {b}²) = {c}.",
        params={"kind": "rtt_supply_hyp", "legs": [a, b]},
        spr_mistakes=gridin_mistakes(key, [
            Mis("added the two legs instead of their squares", E(a + b)),
            Mis("subtracted the legs", E(abs(b - a))),
            Mis("used the longer leg as the hypotenuse", E(b)),
        ]),
    )


def leg_grid(rng: random.Random, seed: int) -> Item:
    a, b, c = rng.choice(TRIPLES)
    k = rng.randint(1, 4)
    a, b, c = a * k, b * k, c * k
    key = E(b)
    return Item(
        "rtt.missing_leg_grid", "Pythagorean theorem", "easy", seed,
        f"A right triangle has a hypotenuse of {c} units and one leg of "
        f"{a} units. What is the length of its other leg?",
        "spr", key, key.gridin(),
        f"The missing leg satisfies b² = {c}² − {a}², so b = {b}.",
        params={"kind": "rtt_supply_leg", "hyp": c, "leg": a},
        spr_mistakes=gridin_mistakes(key, [
            Mis("subtracted the lengths without squaring", E(c - a)),
            Mis("used the hypotenuse as the missing leg", E(c)),
            Mis("added the known leg and hypotenuse", E(c + a)),
        ]),
    )


def sine_grid(rng: random.Random, seed: int) -> Item:
    a, b, c = rng.choice(TRIPLES)
    if rng.randrange(2):
        a, b = b, a
    key = E(Fraction(a, c))
    return Item(
        "rtt.sine_ratio_grid", "trigonometric ratios", "easy", seed,
        f"In a right triangle, the side opposite acute angle A is {a} units, "
        f"the adjacent leg is {b} units, and the hypotenuse is {c} units. "
        "What is sin A? Enter a fraction or decimal.",
        "spr", key, key.gridin(),
        f"Sine is opposite divided by hypotenuse, so sin A = {a}/{c} = "
        f"{key.plain()}.",
        params={"kind": "rtt_supply_sine", "opposite": a, "adjacent": b,
                "hyp": c},
        spr_mistakes=gridin_mistakes(key, [
            Mis("used adjacent over hypotenuse (cosine)", E(Fraction(b, c))),
            Mis("used opposite over adjacent (tangent)", E(Fraction(a, b))),
            Mis("reversed the sine ratio", E(Fraction(c, a))),
        ]),
    )
