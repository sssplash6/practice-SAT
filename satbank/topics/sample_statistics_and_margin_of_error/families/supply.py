"""Numeric sampling and margin questions for the easy grid-in pool."""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, Mis, gridin_mistakes


def sample_percent(rng: random.Random, seed: int) -> Item:
    n = rng.randrange(100, 3001, 100)
    pct = rng.randrange(20, 81, 5)
    count = n * pct // 100
    key = E(pct)
    return Item(
        "sstat.sample_percent_grid", "sample statistics", "easy", seed,
        f"In a random sample of {n} students, {count} preferred the later "
        "start time. What percent of the sampled students preferred it?",
        "spr", key, key.gridin(),
        f"The sample percentage is {count}/{n} × 100 = {pct}.",
        params={"kind": "sstat_supply_percent", "n": n, "count": count},
        spr_mistakes=gridin_mistakes(key, [
            Mis("used the number of supporters rather than the percentage", E(count)),
            Mis("used the percentage who did not prefer it", E(100 - pct)),
            Mis("used the fraction as a percentage without multiplying by 100", E(pct / 100)),
        ]),
    )


def population_estimate(rng: random.Random, seed: int) -> Item:
    population = rng.randrange(200, 5001, 100)
    pct = rng.randrange(10, 91, 5)
    estimate = population * pct // 100
    key = E(estimate)
    return Item(
        "sstat.population_estimate_grid", "using a sample estimate", "easy", seed,
        f"A random sample estimates that {pct}% of the {population} students "
        "at a school walk to school. Based on this estimate, about how "
        "many students at the school walk to school?",
        "spr", key, key.gridin(),
        f"Estimate {pct}% of {population}: {population} × {pct}/100 = {estimate}.",
        params={"kind": "sstat_supply_estimate", "population": population,
                "percent": pct},
        spr_mistakes=gridin_mistakes(key, [
            Mis("gave the percent as a count", E(pct)),
            Mis("estimated the students who do not walk", E(population - estimate)),
            Mis("treated the percent as a whole-number multiplier", E(population * pct)),
        ]),
    )


def interval_lower(rng: random.Random, seed: int) -> Item:
    estimate = rng.randint(20, 80)
    margin = rng.randint(2, 12)
    key = E(estimate - margin)
    return Item(
        "sstat.margin_lower_grid", "margin of error", "easy", seed,
        f"A survey reports an estimate of {estimate}% with a margin of error "
        f"of {margin} percentage points. What is the lower endpoint, in "
        "percent, of the reported interval?",
        "spr", key, key.gridin(),
        f"Subtract the margin from the estimate: {estimate} − {margin} = "
        f"{estimate - margin}.",
        params={"kind": "sstat_supply_lower", "estimate": estimate,
                "margin": margin},
        spr_mistakes=gridin_mistakes(key, [
            Mis("added the margin to find the upper endpoint", E(estimate + margin)),
            Mis("used the point estimate as the lower endpoint", E(estimate)),
            Mis("subtracted twice the margin", E(estimate - 2 * margin)),
        ]),
    )
