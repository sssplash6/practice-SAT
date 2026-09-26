"""Simple circle measurements with numeric grid-in answers."""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, Mis, gridin_mistakes


def radius_from_circumference(rng: random.Random, seed: int) -> Item:
    r = rng.randint(3, 18)
    key = E(r)
    return Item(
        "circles.radius_from_circumference", "circle circumference", "easy", seed,
        f"A circle has circumference {2 * r}π units. What is its radius "
        "in units?",
        "spr", key, key.gridin(),
        f"Since C = 2πr, dividing {2 * r}π by 2π gives r = {r}.",
        params={"kind": "circles_supply_radius", "pi_coefficient": 2 * r},
        spr_mistakes=gridin_mistakes(key, [
            Mis("used the diameter as the radius", E(2 * r)),
            Mis("halved the radius a second time", E(r / 2)),
            Mis("squared the radius as though using area", E(r * r)),
        ]),
    )


def diameter_from_area(rng: random.Random, seed: int) -> Item:
    r = rng.randint(3, 15)
    key = E(2 * r)
    return Item(
        "circles.diameter_from_area", "area of circles", "easy", seed,
        f"The area of a circle is {r * r}π square units. What is its "
        "diameter in units?",
        "spr", key, key.gridin(),
        f"From A = πr², r² = {r * r}, so r = {r} and the diameter is {2 * r}.",
        params={"kind": "circles_supply_diameter", "area_pi_coefficient": r * r},
        spr_mistakes=gridin_mistakes(key, [
            Mis("gave the radius instead of the diameter", E(r)),
            Mis("doubled r² instead of r", E(2 * r * r)),
            Mis("used the area coefficient as the diameter", E(r * r)),
        ]),
    )
