"""Count and budget inequality questions for the easy grid-in pool."""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, Mis, gridin_mistakes


def budget_max(rng: random.Random, seed: int) -> Item:
    price = rng.randint(3, 12)
    fee = rng.randint(2, 9)
    count = rng.randint(5, 18)
    budget = fee + price * count + rng.randrange(price)
    key = E(count)
    return Item(
        "ineq.budget_max_grid", "integer solutions to inequalities", "easy", seed,
        f"A club pays a one-time fee of ${fee} plus ${price} for each ticket. "
        f"It can spend at most ${budget}. What is the greatest whole number "
        "of tickets it can buy?",
        "spr", key, key.gridin(),
        f"After the fee, ${budget - fee} remains. Dividing by ${price} per "
        f"ticket and rounding down gives {count}.",
        params={"kind": "ineq_supply_budget", "price": price,
                "fee": fee, "budget": budget},
        spr_mistakes=gridin_mistakes(key, [
            Mis("ignored the one-time fee", E(budget // price)),
            Mis("rounded the number of affordable tickets up", E(count + 1)),
            Mis("subtracted the fee but did not divide by the ticket price", E(budget - fee)),
        ]),
    )


def interval_count(rng: random.Random, seed: int) -> Item:
    lower = rng.randint(1, 15)
    upper = lower + rng.randint(4, 14)
    key = E(upper - lower)
    return Item(
        "ineq.interval_count_grid", "integer solutions to inequalities", "easy", seed,
        f"How many integer values of x satisfy {lower} ≤ x < {upper}?",
        "spr", key, key.gridin(),
        f"The integers run from {lower} through {upper - 1}, inclusive, so "
        f"there are {upper - lower} values.",
        params={"kind": "ineq_supply_count", "lower": lower, "upper": upper},
        spr_mistakes=gridin_mistakes(key, [
            Mis("included the excluded upper endpoint", E(upper - lower + 1)),
            Mis("excluded the included lower endpoint", E(upper - lower - 1)),
            Mis("counted from zero instead of from the lower bound", E(upper)),
        ]),
    )
