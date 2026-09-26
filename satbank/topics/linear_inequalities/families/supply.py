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
    lower = rng.randint(1, 50)
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


def two_sided_bound(rng: random.Random, seed: int) -> Item:
    coefficient = rng.randint(2, 5)
    offset = rng.randint(2, 15)
    max_x = rng.randint(6, 16)
    upper = coefficient * (max_x + 1) + offset
    lower = coefficient * (max_x - 3) + offset
    key = E(max_x)
    return Item(
        "ineq.two_sided_bound_grid", "compound inequalities", "medium", seed,
        f"What is the greatest integer value of x that satisfies "
        f"{lower} ≤ {coefficient}x + {offset} < {upper}?",
        "spr", key, key.gridin(),
        f"The strict upper bound gives x < {max_x + 1}, so the greatest "
        f"integer solution is {max_x}.",
        params={"kind": "ineq_supply_two_sided", "coefficient": coefficient,
                "offset": offset, "lower": lower, "upper": upper},
        spr_mistakes=gridin_mistakes(key, [
            Mis("treated the strict upper bound as inclusive", E(max_x + 1)),
            Mis("ignored the constant term when using the upper bound",
                E((upper - 1) // coefficient)),
            Mis("used the lower bound as the greatest value", E(max_x - 3)),
        ]),
    )


def perimeter_limit(rng: random.Random, seed: int) -> Item:
    difference = rng.randint(2, 8)
    max_width = rng.randint(5, 18)
    limit = 4 * max_width + 2 * difference + rng.randint(0, 3)
    key = E(max_width)
    return Item(
        "ineq.perimeter_limit_grid", "geometric inequalities", "medium", seed,
        f"A rectangle has width x and length x + {difference}. Its "
        f"perimeter is at most {limit} units. What is the greatest "
        "integer value of x?",
        "spr", key, key.gridin(),
        f"The perimeter is 2x + 2(x + {difference}) = 4x + "
        f"{2 * difference}. Solving 4x + {2 * difference} ≤ {limit} "
        f"gives greatest integer x = {max_width}.",
        params={"kind": "ineq_supply_perimeter", "difference": difference,
                "limit": limit},
        spr_mistakes=gridin_mistakes(key, [
            Mis("forgot to count both pairs of sides", E((limit - difference) // 2)),
            Mis("ignored the extra length of each longer side", E(limit // 4)),
            Mis("rounded the greatest whole-number width up", E(max_width + 1)),
        ]),
    )
