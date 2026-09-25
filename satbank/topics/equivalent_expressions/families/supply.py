"""Additional easy Advanced Math grid-ins for twin challenge supply.

Both questions ask for a coefficient in a printed equivalent expression. The
existing coefficient audit parses that expression and independently reads its
linear coefficient; it does not use the generator's answer arithmetic.
"""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, Mis, gridin_mistakes


def collect_coefficient(rng: random.Random, seed: int) -> Item:
    """Collect two like terms before identifying the coefficient."""
    a, b, c = rng.sample(range(2, 20), 3)
    var = rng.choice(("x", "y", "t"))
    expr = f"{a}{var} + {b}{var} + {c}"
    key = E(a + b)
    mistakes = gridin_mistakes(key, [
        Mis(f"used only the coefficient {a} of the first {var}-term", E(a)),
        Mis(f"used only the coefficient {b} of the second {var}-term", E(b)),
        Mis("multiplied the two coefficients instead of adding them", E(a * b)),
        Mis("included the constant in the coefficient", E(a + b + c)),
    ])
    return Item(
        "eqx.collect_coefficient", "equivalent expressions", "easy", seed,
        f"The expression {expr} is equivalent to k{var} + {c}. "
        "What is the value of k?",
        "spr", key, key.gridin(),
        f"The two {var}-terms combine: {a} + {b} = {a + b}, so k = {a + b}.",
        params={"kind": "eqx_coef_combination", "expr": expr, "var": var,
                "degree": 1, "weights": [(1, 1)]},
        spr_mistakes=mistakes,
    )


def distribute_coefficient(rng: random.Random, seed: int) -> Item:
    """Distribute and then combine the outside variable term."""
    p = rng.randint(2, 9)
    a = rng.randint(2, 12)
    b = rng.randint(1, 18)
    c = rng.randint(1, 18)
    d = rng.randint(1, 18)
    var = rng.choice(("x", "y", "t"))
    expr = f"{p}({a}{var} + {b}) + {c}{var} + {d}"
    answer = p * a + c
    key = E(answer)
    mistakes = gridin_mistakes(key, [
        Mis(f"omitted the outside {c}{var} term", E(p * a)),
        Mis(f"did not multiply the {a}{var} term by {p}", E(a + c)),
        Mis(f"distributed {p} to the outside {c}{var} term too", E(p * (a + c))),
        Mis(f"used the constant {b} in place of the outside coefficient {c}",
            E(p * a + b)),
    ])
    return Item(
        "eqx.distribute_coefficient", "equivalent expressions", "easy", seed,
        f"The expression {expr} is equivalent to k{var} + m, where k and m "
        "are constants. What is the value of k?",
        "spr", key, key.gridin(),
        f"Distributing {p} gives {p * a}{var} + {p * b}; adding the outside "
        f"{c}{var} term gives {p * a} + {c} = {answer}, so k = {answer}.",
        params={"kind": "eqx_coef_combination", "expr": expr, "var": var,
                "degree": 1, "weights": [(1, 1)]},
        spr_mistakes=mistakes,
    )
