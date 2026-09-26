"""Transformations of center and spread with numeric answers."""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, Mis, gridin_mistakes


def shifted_mean(rng: random.Random, seed: int) -> Item:
    n = rng.randint(5, 15)
    mean = rng.randint(12, 40)
    shift = rng.randint(3, 12)
    key = E(mean + shift)
    return Item(
        "ovd.shifted_mean_grid", "mean of a data set", "easy", seed,
        f"The mean of {n} data values is {mean}. If {shift} is added to "
        "every value, what is the new mean?",
        "spr", key, key.gridin(),
        f"Adding {shift} to every value adds {shift} to the mean, so the "
        f"new mean is {mean + shift}.",
        params={"kind": "ovd_supply_shift_mean", "n": n,
                "mean": mean, "shift": shift},
        spr_mistakes=gridin_mistakes(key, [
            Mis("left the mean unchanged", E(mean)),
            Mis("added the change to the total before dividing by n",
                E(mean + shift / n)),
            Mis("multiplied the shift by the number of values", E(mean + n * shift)),
        ]),
    )


def scaled_range(rng: random.Random, seed: int) -> Item:
    spread = rng.randint(8, 25)
    factor = rng.randint(2, 5)
    key = E(spread * factor)
    return Item(
        "ovd.scaled_range_grid", "range of a data set", "easy", seed,
        f"The range of a data set is {spread}. If every value is "
        f"multiplied by {factor}, what is the range of the new data set?",
        "spr", key, key.gridin(),
        f"Multiplying every value by {factor} multiplies the difference "
        f"between the greatest and least values by {factor}, so the "
        f"new range is {spread * factor}.",
        params={"kind": "ovd_supply_scaled_range", "range": spread,
                "factor": factor},
        spr_mistakes=gridin_mistakes(key, [
            Mis("left the range unchanged", E(spread)),
            Mis("added the factor to the range", E(spread + factor)),
            Mis("divided the range by the factor", E(spread / factor)),
        ]),
    )
