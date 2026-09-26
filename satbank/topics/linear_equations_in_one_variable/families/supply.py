"""Two multi-step equations for the hard grid-in pool."""

from __future__ import annotations

import random
from fractions import Fraction

from ....exact import E
from ....item import Item, Mis, gridin_mistakes


def nested_distribution(rng: random.Random, seed: int) -> Item:
    a, b = rng.randint(2, 5), rng.randint(2, 5)
    d = rng.randint(2, a * b - 1)
    c, e = rng.randint(2, 9), rng.randint(2, 9)
    x = rng.randint(3, 12)
    rhs = a * (b * x + c) - d * (x + e)
    key = E(x)
    mistakes = [
        Mis("failed to distribute the subtraction to the second constant",
            E(Fraction(rhs - a * c, a * b - d))),
        Mis("omitted the subtracted bracket entirely",
            E(Fraction(rhs - a * c, a * b))),
        Mis("added the two x-coefficients instead of subtracting",
            E(Fraction(rhs - a * c + d * e, a * b + d))),
    ]
    return Item(
        "lin1.nested_distribution_grid", "multi-step linear equations", "hard", seed,
        f"If {a}({b}x + {c}) − {d}(x + {e}) = {rhs}, what is the "
        "value of x?",
        "spr", key, key.gridin(),
        f"Expanding and collecting terms gives ({a * b} − {d})x = "
        f"{rhs} − {a * c} + {d * e} = {(a * b - d) * x}, so x = {x}.",
        params={"kind": "lin1_supply_nested", "a": a, "b": b, "c": c,
                "d": d, "e": e, "rhs": rhs},
        spr_mistakes=gridin_mistakes(key, mistakes),
    )


def fraction_sum(rng: random.Random, seed: int) -> Item:
    m, n = rng.choice(((2, 3), (3, 4), (2, 5)))
    a, b = rng.randint(2, 8), rng.randint(2, 8)
    x = rng.randint(3, 12)
    rhs = Fraction(x + a, m) + Fraction(x + b, n)
    slope = Fraction(1, m) + Fraction(1, n)
    key = E(x)
    return Item(
        "lin1.fraction_sum_grid", "equations with fractions", "hard", seed,
        f"If (x + {a})/{m} + (x + {b})/{n} = {rhs}, "
        "what is the value of x?",
        "spr", key, key.gridin(),
        f"Combine the x-terms and constants, then clear the denominators; "
        f"the equation gives x = {x}.",
        params={"kind": "lin1_supply_fraction", "a": a, "b": b,
                "m": m, "n": n, "rhs_num": rhs.numerator,
                "rhs_den": rhs.denominator},
        spr_mistakes=gridin_mistakes(key, [
            Mis("omitted the constant in the second numerator",
                E((rhs - Fraction(a, m)) / slope)),
            Mis("omitted the constant in the first numerator",
                E((rhs - Fraction(b, n)) / slope)),
            Mis("subtracted the two fractions instead of adding",
                E((rhs - Fraction(a, m) + Fraction(b, n)) /
                  (Fraction(1, m) - Fraction(1, n)))),
        ]),
    )
