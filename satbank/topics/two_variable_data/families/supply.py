"""Linear-data calculations for the medium grid-in pool."""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, Mis, gridin_mistakes


def table_slope(rng: random.Random, seed: int) -> Item:
    x0 = rng.randint(1, 6)
    dx = rng.randint(2, 5)
    slope = rng.randint(2, 9)
    y0 = rng.randint(5, 30)
    y1 = y0 + dx * slope
    key = E(slope)
    return Item(
        "tvdata.table_slope_grid", "rate of change in a table", "medium", seed,
        "The table gives two points on a linear relationship. What is the "
        "rate of change of y with respect to x?",
        "spr", key, key.gridin(),
        f"The change in y is {y1} − {y0} = {y1 - y0}, and the change in x is "
        f"{dx}, so the rate is {slope}.",
        table=[["x", "y"], [str(x0), str(y0)], [str(x0 + dx), str(y1)]],
        params={"kind": "tvdata_supply_slope", "x0": x0, "x1": x0 + dx,
                "y0": y0, "y1": y1},
        spr_mistakes=gridin_mistakes(key, [
            Mis("used the total change in y without dividing by the change in x", E(y1 - y0)),
            Mis("divided the second y-value by the second x-value", E(y1 / (x0 + dx))),
            Mis("used the first y-value as the rate of change", E(y0)),
        ]),
    )


def model_prediction(rng: random.Random, seed: int) -> Item:
    slope = rng.randint(2, 8)
    intercept = rng.randint(4, 24)
    x = rng.randint(6, 15)
    key = E(slope * x + intercept)
    return Item(
        "tvdata.model_prediction_grid", "linear model predictions", "medium", seed,
        f"A linear model predicts y = {slope}x + {intercept}, where x is the "
        "number of weeks after an experiment began. What value does the "
        f"model predict when x = {x}?",
        "spr", key, key.gridin(),
        f"Substitute x = {x}: y = {slope}({x}) + {intercept} = "
        f"{slope * x + intercept}.",
        params={"kind": "tvdata_supply_predict", "slope": slope,
                "intercept": intercept, "x": x},
        spr_mistakes=gridin_mistakes(key, [
            Mis("used only the slope times x and omitted the intercept", E(slope * x)),
            Mis("added x to the intercept without multiplying by the slope", E(x + intercept)),
            Mis("multiplied x by the sum of slope and intercept", E(x * (slope + intercept))),
        ]),
    )


def residual(rng: random.Random, seed: int) -> Item:
    slope = rng.randint(2, 7)
    intercept = rng.randint(5, 25)
    x = rng.randint(5, 12)
    predicted = slope * x + intercept
    residual = rng.randint(3, 14)
    observed = predicted + residual
    key = E(residual)
    return Item(
        "tvdata.residual_grid", "residuals from a linear model", "medium", seed,
        f"A model predicts y = {slope}x + {intercept}. At x = {x}, the observed "
        f"y-value is {observed}. What is the residual (observed minus "
        "predicted)?",
        "spr", key, key.gridin(),
        f"The prediction is {slope}({x}) + {intercept} = {predicted}; "
        f"observed minus predicted is {observed} − {predicted} = {residual}.",
        params={"kind": "tvdata_supply_residual", "slope": slope,
                "intercept": intercept, "x": x, "observed": observed},
        spr_mistakes=gridin_mistakes(key, [
            Mis("gave the predicted value instead of the residual", E(predicted)),
            Mis("gave the observed value instead of subtracting the prediction", E(observed)),
            Mis("subtracted only the intercept from the observation", E(observed - intercept)),
        ]),
    )
