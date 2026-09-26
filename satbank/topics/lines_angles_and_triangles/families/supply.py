"""Short, diagram-free angle questions for the easy grid-in pool."""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, Mis, gridin_mistakes


def linear_pair(rng: random.Random, seed: int) -> Item:
    a = rng.randrange(35, 146, 5)
    key = E(180 - a)
    return Item(
        "lat.linear_pair_grid", "angles formed by intersecting lines", "easy", seed,
        f"Two adjacent angles form a straight line. One angle measures {a}°. "
        "What is the measure, in degrees, of the other angle?",
        "spr", key, key.gridin(),
        f"Adjacent angles on a straight line sum to 180°, so the other angle "
        f"is 180 − {a} = {180 - a}.",
        params={"kind": "lat_supply_pair", "given": a},
        spr_mistakes=gridin_mistakes(key, [
            Mis("copied the given angle instead of finding its supplement", E(a)),
            Mis("used a right angle instead of a straight angle", E(90 - a)),
            Mis("subtracted from a full turn", E(360 - a)),
        ]),
    )


def isosceles_base(rng: random.Random, seed: int) -> Item:
    vertex = rng.randrange(30, 121, 10)
    base = (180 - vertex) // 2
    key = E(base)
    return Item(
        "lat.isosceles_base_grid", "isosceles triangles", "easy", seed,
        f"An isosceles triangle has a vertex angle of {vertex}°. "
        "What is the measure, in degrees, of each base angle?",
        "spr", key, key.gridin(),
        f"The two equal base angles share 180 − {vertex} = {180 - vertex}°, "
        f"so each is {base}.",
        params={"kind": "lat_supply_base", "vertex": vertex},
        spr_mistakes=gridin_mistakes(key, [
            Mis("did not divide the remaining angle between the two bases", E(180 - vertex)),
            Mis("halved the vertex angle instead of the remainder", E(vertex // 2)),
            Mis("subtracted the vertex angle from a right angle", E(90 - vertex)),
        ]),
    )


def exterior_sum(rng: random.Random, seed: int) -> Item:
    a = rng.randrange(25, 81, 5)
    b = rng.randrange(25, 81, 5)
    key = E(a + b)
    return Item(
        "lat.exterior_sum_grid", "exterior angles of triangles", "easy", seed,
        f"Two remote interior angles of a triangle measure {a}° and {b}°. "
        "What is the measure, in degrees, of their exterior angle?",
        "spr", key, key.gridin(),
        f"The exterior angle equals the sum of the remote interior angles: "
        f"{a} + {b} = {a + b}.",
        params={"kind": "lat_supply_exterior", "a": a, "b": b},
        spr_mistakes=gridin_mistakes(key, [
            Mis("found the third interior angle instead of the exterior angle", E(180 - a - b)),
            Mis("used only the first remote interior angle", E(a)),
            Mis("used only the second remote interior angle", E(b)),
        ]),
    )
