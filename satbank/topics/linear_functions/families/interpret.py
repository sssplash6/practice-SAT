"""What the numbers mean.

The options here are sentences, and the wrong ones are the famous wrong
readings: the rate read as a total, the intercept read as the rate, the two
quantities swapped, the intercept of the wrong axis. Each option is tagged
with the role it plays, and the independent solver checks that the keyed
option is the one whose role the question actually asks for -- which is what
goes wrong when an interpretation item is mis-keyed.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text
from ....plot import line_graph
from ...linear_functions.common import dec, money, numtext, q, year_text

__all__ = ["interpret_slope", "interpret_constant", "interpret_x_intercept"]


def _role_item(template, skill, difficulty, seed, stem, ctx, roles, key_role, rng,
               extra, rationale, figure=None):
    """Four sentences, one per role, with the roles recorded for the audit."""
    key = roles[key_role]
    wrong = [Mis(r, roles[k]) for k, r in extra if k in roles and roles[k] != key]
    seen, picked = {key}, []
    for m in wrong:
        if m.value in seen:
            continue
        seen.add(m.value)
        picked.append(m)
    if len(picked) < 3:
        raise ItemError("could not build three distinct interpretations")
    choices, reasons, letter = assemble_text(key, picked, rng)
    by_text = {roles[k]: k for k in roles}
    P = dict(ctx)
    P["roles"] = [by_text[c] for c in choices]
    P["texts"] = list(choices)
    return Item(template, skill, difficulty, seed, stem, "mcq", E(0), letter, rationale,
                choices, reasons, list(choices), figure=figure, params=P)


def _scaleless_line(m, b) -> str:
    """A line with axes but no scale -- the source draws one when the question
    is about which quantity the slope is, not how big it is."""
    x0, x1 = 30.0, 250.0
    top, bot = 20.0, 200.0
    span = float(m) * 9 + float(b)
    y0 = bot - (float(b) / span) * (bot - top) if span else bot - 20
    y1 = top + 6
    return ('<svg viewBox="0 0 300 230" width="300" height="230" role="img" '
            'xmlns="http://www.w3.org/2000/svg"><style>'
            '.ax{stroke:currentColor;stroke-width:2;fill:none}'
            '.ln{stroke:currentColor;stroke-width:2;fill:none}'
            '.it{fill:currentColor;font:italic 13px ui-serif,Georgia,serif}</style>'
            f'<line class="ax" x1="{x0}" y1="{bot}" x2="275" y2="{bot}"/>'
            f'<line class="ax" x1="{x0}" y1="{bot}" x2="{x0}" y2="{top}"/>'
            f'<line class="ln" x1="{x0}" y1="{round(y0, 1)}" x2="{x1}" y2="{round(y1, 1)}"/>'
            f'<text class="it" x="282" y="{bot + 5}">x</text>'
            f'<text class="it" x="{x0 - 12}" y="{top}">y</text>'
            f'<text class="it" x="{x0 - 14}" y="{bot + 14}">O</text></svg>')


# ------------------------------------------------------------- the slope

SLOPE_CTX = [
    dict(kind="equation",
         stem="d = {m}t The given equation represents the distance d, in inches, where t "
              "represents the number of seconds since an object started moving. Which of "
              "the following is the best interpretation of {m} in this context?",
         roles=lambda m, b: {
             "rate": f"The object is moving at a rate of {m} inches per second.",
             "total": f"The object moved a total of {m} inches.",
             "total_expr": f"The object moved a total of {m}t inches.",
             "inverted": f"The object is moving at a rate of 1/{m} inches per second."},
         order=["total", "total_expr", "inverted"], proportional=True,
         mrange=(3, 60)),
    dict(kind="equation",
         stem="Marisol drove 3 hours from City A to City B. The equation below estimates "
              "the distance d, in miles, Marisol traveled after driving for t hours. "
              "d = {m}t Which of the following does {m} represent in the equation?",
         roles=lambda m, b: {
             "rate": f"Marisol drove at an average speed of about {m} miles per hour.",
             "count": f"Marisol took {m} trips from City A to City B.",
             "total": f"The distance between City A and City B is {m} miles.",
             "duration": f"It took Marisol {m} hours to drive from City A to City B."},
         order=["count", "total", "duration"], proportional=True, mrange=(25, 75)),
    dict(kind="equation",
         stem="An object hangs from a spring. The formula l = {b} + {m}w relates the "
              "length l, in centimeters, of the spring to the weight w, in newtons, of the "
              "object. Which of the following describes the meaning of the {m} in this "
              "context?",
         roles=lambda m, b: {
             "rate": "The increase in the length, in centimeters, of the spring for each "
                     "one-newton increase in the weight of the object",
             "intercept": "The length, in centimeters, of the spring with no weight "
                          "attached",
             "inverse_at_intercept": f"The weight, in newtons, of an object that will "
                                     f"stretch the spring {b} centimeters",
             "swapped": "The increase in the weight, in newtons, of the object for each "
                        "one-centimeter increase in the length of the spring"},
         order=["intercept", "inverse_at_intercept", "swapped"], mrange=(2, 12),
         brange=(10, 60)),
    dict(kind="graph",
         stem="The graph of the function f, where y = f(x), gives the total cost y, in "
              "dollars, for a certain video game system and x games. What is the best "
              "interpretation of the slope of the graph in this context?",
         roles=lambda m, b: {
             "rate": f"Each game costs ${m}.",
             "intercept": f"The video game system costs ${b}.",
             "intercept_as_rate": f"The video game system costs ${m}.",
             "rate_as_fixed": f"Each game costs ${b}."},
         order=["intercept", "intercept_as_rate", "rate_as_fixed"], mrange=(15, 60),
         brange=(50, 250), scaled=True, xmax=10,
         xlabel="Number of games", ylabel="Total cost (dollars)"),
    dict(kind="label",
         stem="The graph represents the total charge, in dollars, by an electrician for x "
              "hours of work. The electrician charges a onetime fee plus an hourly rate. "
              "What is the best interpretation of the slope of the graph?",
         roles=lambda m, b: {
             "rate": "The electrician's hourly rate",
             "intercept": "The electrician's onetime fee",
             "maximum": "The maximum amount that the electrician charges",
             "total": "The total amount that the electrician charges"},
         order=["intercept", "maximum", "total"], mrange=(30, 120), brange=(20, 90)),
    dict(kind="label",
         stem="The graph represents the total cost, in dollars, of a catering order for x "
              "guests. The caterer charges a fixed setup charge plus an amount for each "
              "guest. What is the best interpretation of the slope of the graph?",
         roles=lambda m, b: {
             "rate": "The cost for each guest",
             "intercept": "The caterer's fixed setup charge",
             "maximum": "The largest order the caterer will take",
             "total": "The total cost of the order"},
         order=["intercept", "maximum", "total"], mrange=(12, 70), brange=(40, 300)),
]

SLOPE_WHY = {
    "total": "read the rate as a total",
    "total_expr": "read the rate as a total and kept the variable with it",
    "inverted": "inverted the rate",
    "count": "read the rate as a count of repetitions",
    "duration": "attached the rate to the wrong quantity",
    "intercept": "interpreted the constant term rather than the rate",
    "inverse_at_intercept": "swapped the two quantities and used the constant term",
    "swapped": "swapped the two quantities in the rate",
    "intercept_as_rate": "read the rate as the value of the fixed item",
    "rate_as_fixed": "attached the constant term to the per-unit quantity",
    "maximum": "read the slope as the largest value the graph reaches",
}


def interpret_slope(rng: random.Random, seed: int, *, ctx=None, m=None, b=None) -> Item:
    """What the coefficient of x means in the situation."""
    d = SLOPE_CTX[rng.randrange(len(SLOPE_CTX))] if ctx is None else SLOPE_CTX[ctx]
    m = q(m if m is not None else rng.randint(*d["mrange"]))
    b = q(b if b is not None else rng.randint(*d.get("brange", (5, 80))))
    if d.get("proportional"):
        b = Q(0)
    if m == b:
        raise ItemError("the rate and the constant must be told apart")
    roles = d["roles"](numtext(m), numtext(b))
    stem = d["stem"].format(m=numtext(m), b=numtext(b))
    if d.get("scaled"):
        # a scaleless picture is only honest when the options name no numbers.
        # This context's options do -- "Each game costs $25" against "Each game
        # costs $100" -- and bare axes leave a student no way to tell which
        # number is the slope, so the graph has to carry a readable scale.
        x1 = d["xmax"]
        fig = line_graph([(0, b), (x1, m * x1 + b)], d["xlabel"], d["ylabel"])
    elif d["kind"] in ("graph", "label"):
        fig = _scaleless_line(m, b)
    else:
        fig = None
    P = {"kind": "lf_interpret_slope", "ask": "slope",
         "m": [m.numerator, m.denominator], "b": [b.numerator, b.denominator]}
    rationale = (f"The coefficient of the variable is the constant rate of change, so "
                 f"{numtext(m)} is a rate.")
    extra = [(k, SLOPE_WHY[k]) for k in d["order"]]
    return _role_item("lin.interpret_slope", "interpreting a rate of change", "medium",
                      seed, stem, P, roles, "rate", rng, extra, rationale, figure=fig)


# ----------------------------------------------------------- the constant

CONST_CTX = [
    dict(mode="start",
         stem="As part of a science project on evaporation, Amaya measured the height of a "
              "liquid in a container over a period of time. The function f(x) = {b} − {m}x "
              "gives the estimated height, in centimeters (cm), of the liquid in the "
              "container x days after the start of the project. Which of the following is "
              "the best interpretation of {b} in this context?",
         roles=lambda b, m: {
             "start": "The estimated height, in cm, of the liquid at the start of the "
                      "project",
             "end": "The estimated height, in cm, of the liquid at the end of the project",
             "rate": "The estimated change in the height, in cm, of the liquid each day",
             "zero_time": "The estimated number of days for all of the liquid to "
                          "evaporate"},
         order=["end", "rate", "zero_time"], brange=(2000, 4500), mrange=(8, 40)),
    dict(mode="start",
         stem="In science class, Diego conducted an experiment to learn about evaporation. "
              "Diego measured the height of fluid in a beaker over a period of time. The "
              "function f(x) = {b} − {m}x gives the estimated height, in centimeters (cm), "
              "of the fluid in the beaker x days after the start of the experiment. Which "
              "of the following is the best interpretation of {b} in this context?",
         roles=lambda b, m: {
             "start": "The estimated height, in cm, of the fluid at the start of the "
                      "experiment",
             "end": "The estimated height, in cm, of the fluid at the end of the "
                    "experiment",
             "rate": "The estimated change in the height, in cm, of the fluid each day",
             "zero_time": "The estimated number of days for all the fluid to evaporate"},
         order=["end", "rate", "zero_time"], brange=(2000, 4500), mrange=(8, 40)),
    dict(mode="start",
         stem="A technician recorded the charge remaining in a battery over a period of "
              "time. The function f(x) = {b} − {m}x gives the estimated charge, as a "
              "percent, remaining in the battery x hours after the recording began. Which "
              "of the following is the best interpretation of {b} in this context?",
         roles=lambda b, m: {
             "start": "The estimated charge, as a percent, in the battery when the "
                      "recording began",
             "end": "The estimated charge, as a percent, in the battery when the recording "
                    "ended",
             "rate": "The estimated change in the charge, as a percent, each hour",
             "zero_time": "The estimated number of hours until the battery is empty"},
         order=["end", "rate", "zero_time"], brange=(6000, 9900), mrange=(30, 90)),
]

SHIFT_CTX = [
    dict(stem="According to data provided by the US Department of Energy, the average "
              "price per gallon of regular gasoline in the United States from September 1, "
              "2014, to December 1, 2014, is modeled by the function F defined below, "
              "where F(x) is the average price per gallon x months after September 1. "
              "F(x) = {b} − {m}(x − {k}) The constant {b} in this function estimates which "
              "of the following?",
         roles=lambda b, m, k: {
             "at_k": "The average price per gallon on December 1, 2014",
             "at_zero": "The average price per gallon on September 1, 2014",
             "rate": "The average monthly decrease in the price per gallon",
             "difference": "The difference in the average price per gallon from "
                           "September 1, 2014, to December 1, 2014"},
         order=["rate", "difference", "at_zero"], brange=(180, 420), mrange=(8, 35),
         k=3, scale=100),
]

POINT_CTX = [
    dict(stem="P(t) = {b} + {m}t The population of snow leopards in a certain area can be "
              "modeled by the function P defined above, where P(t) is the population t "
              "years after {y0}. Of the following, which is the best interpretation of the "
              "equation P({t}) = {v} ?",
         noun="snow leopard population in this area", brange=(150, 400), mrange=(5, 30),
         y0range=(1960, 1995), trange=(10, 40)),
    dict(stem="N(t) = {b} + {m}t\nThe number of registered bicycles in a certain town can "
              "be modeled by the function N defined above, where N(t) is the number "
              "registered t years after {y0}. Of the following, which is the best "
              "interpretation of the equation N({t}) = {v} ?",
         noun="number of registered bicycles in this town", brange=(200, 900),
         mrange=(8, 45), y0range=(1960, 1995), trange=(10, 40)),
]

CONST_WHY = {
    "end": "read the starting value as the final value",
    "rate": "interpreted the rate of change rather than the constant term",
    "zero_time": "read the constant term as the time at which the quantity runs out",
    "at_zero": "ignored the shift and read the constant at x = 0",
    "difference": "read the constant term as the change over the whole period",
}


def interpret_constant(rng: random.Random, seed: int, *, mode=None, ctx=None, b=None,
                       m=None, k=None, y0=None, t=None) -> Item:
    """What the constant term, or a stated function value, means."""
    mode = mode or rng.choice(["start", "shifted", "point"])
    if mode == "start":
        d = CONST_CTX[rng.randrange(len(CONST_CTX))] if ctx is None else CONST_CTX[ctx]
        b = q(b) if b is not None else Q(rng.randint(*d["brange"]), 100)
        m = q(m) if m is not None else Q(rng.randint(*d["mrange"]), 100)
        roles = d["roles"](numtext(b, "dec"), numtext(m, "dec"))
        stem = d["stem"].format(b=numtext(b, "dec"), m=numtext(m, "dec"))
        extra = [(kk, CONST_WHY[kk]) for kk in d["order"]]
        key_role = "start"
        P = {"kind": "lf_interpret_constant", "mode": mode, "ask": "start"}
        rationale = (f"At x = 0 the model gives {numtext(b, 'dec')}, which is the value at "
                     f"the start.")
    elif mode == "shifted":
        d = SHIFT_CTX[rng.randrange(len(SHIFT_CTX))] if ctx is None else SHIFT_CTX[ctx]
        b = q(b) if b is not None else Q(rng.randint(*d["brange"]), d["scale"])
        m = q(m) if m is not None else Q(rng.randint(*d["mrange"]), d["scale"])
        k = int(k if k is not None else d["k"])
        roles = d["roles"](numtext(b, "dec"), numtext(m, "dec"), numtext(k))
        stem = d["stem"].format(b=numtext(b, "dec"), m=numtext(m, "dec"), k=numtext(k))
        extra = [(kk, CONST_WHY[kk]) for kk in d["order"]]
        key_role = "at_k"
        P = {"kind": "lf_interpret_constant", "mode": mode, "ask": "at_k", "k": k}
        rationale = (f"The constant sits outside a factor of (x − {numtext(k)}), so it is "
                     f"the value when x = {numtext(k)}.")
    else:
        d = POINT_CTX[rng.randrange(len(POINT_CTX))] if ctx is None else POINT_CTX[ctx]
        b = q(b if b is not None else rng.randint(*d["brange"]))
        m = q(m if m is not None else rng.randint(*d["mrange"]))
        y0 = int(y0 if y0 is not None else rng.randrange(*d["y0range"], 5))
        t = int(t if t is not None else rng.randrange(*d["trange"], 5))
        v = b + m * t
        year, wrong_year = y0 + t, 2000 + t
        if year == wrong_year or t == v:
            raise ItemError("the two years must differ and the input must not be the value")
        noun = d["noun"]
        roles = {
            "value_year": f"The {noun} is predicted to be {numtext(v)} in the year "
                          f"{year_text(year)}.",
            "value_wrong_year": f"The {noun} is predicted to be {numtext(v)} in the year "
                                f"{wrong_year}.",
            "input_year": f"The {noun} is predicted to be {numtext(t)} in the year "
                          f"{year_text(year)}.",
            "input_wrong_year": f"The {noun} is predicted to be {numtext(t)} in the year "
                                f"{wrong_year}."}
        stem = d["stem"].format(b=numtext(b), m=numtext(m), y0=year_text(y0), t=numtext(t),
                                v=numtext(v))
        extra = [("input_year", "read the input as the population"),
                 ("input_wrong_year", "read the input as the population and as the year"),
                 ("value_wrong_year", "read the input as the year rather than as years "
                                      "after the starting year")]
        key_role = "value_year"
        P = {"kind": "lf_interpret_constant", "mode": mode, "ask": "value_year"}
        rationale = (f"t is measured from {year_text(y0)}, so t = {numtext(t)} is the year "
                     f"{year} and the value there is {numtext(v)}.")
    return _role_item("lin.interpret_constant", "interpreting a constant term", "medium",
                      seed, stem, P, roles, key_role, rng, extra, rationale)


# --------------------------------------------------------- the x-intercept

XINT_CTX = [
    dict(stem="A team of workers has been moving cargo off of a ship. The equation below "
              "models the approximate number of tons of cargo, y, that remains to be moved "
              "x hours after the team started working. y = {b} − {m}x The graph of this "
              "equation in the xy-plane is a line. What is the best interpretation of the "
              "x-intercept in this context?",
         roles=lambda b, m, xi: {
             "time": f"The team will have moved all the cargo in about {xi} hours.",
             "rate_wrong_units": f"The team has been moving about {xi} tons of cargo per "
                                 f"hour.",
             "rate": f"The team has been moving about {m} tons of cargo per hour.",
             "initial": f"The team started with {b} tons of cargo to move."},
         order=["rate_wrong_units", "rate", "initial"], brange=(60, 300), mrange=(5, 40),
         places=1),
    dict(stem="y = {b} − {m}x The equation above represents the speed y, in feet per "
              "second, of Sheila's bicycle x seconds after she applied the brakes at the "
              "end of a ride. If the equation is graphed in the xy-plane, which of the "
              "following is the best interpretation of the x-coordinate of the line's "
              "x-intercept in the context of the problem?",
         roles=lambda b, m, xi: {
             "time": "The number of seconds it took from the time Sheila began applying "
                     "the brakes until the bicycle came to a complete stop",
             "initial": "The speed of Sheila's bicycle, in feet per second, before Sheila "
                        "applied the brakes",
             "rate": "The number of feet per second the speed of Sheila's bicycle "
                     "decreased each second after Sheila applied the brakes",
             "distance": "The number of feet Sheila's bicycle traveled from the time she "
                         "began applying the brakes until the bicycle came to a complete "
                         "stop"},
         order=["initial", "rate", "distance"], brange=(10, 60), mrange=(2, 12),
         places=None),
    dict(stem="A tank is being drained. The equation below models the number of gallons of "
              "water, y, left in the tank x minutes after the draining began. "
              "y = {b} − {m}x The graph of this equation in the xy-plane is a line. What "
              "is the best interpretation of the x-intercept in this context?",
         roles=lambda b, m, xi: {
             "time": f"The tank will be empty in about {xi} minutes.",
             "rate_wrong_units": f"The tank is draining at about {xi} gallons per minute.",
             "rate": f"The tank is draining at about {m} gallons per minute.",
             "initial": f"The tank held {b} gallons before the draining began."},
         order=["rate_wrong_units", "rate", "initial"], brange=(80, 600), mrange=(4, 30),
         places=1),
]

XINT_WHY = {
    "rate_wrong_units": "attached the x-intercept to the wrong quantity",
    "rate": "interpreted the slope instead of the x-intercept",
    "initial": "interpreted the y-intercept instead of the x-intercept",
    "distance": "read the x-intercept as a distance rather than a time",
}


def interpret_x_intercept(rng: random.Random, seed: int, *, ctx=None, b=None,
                          m=None) -> Item:
    """What it means for the modelled quantity to reach zero."""
    d = XINT_CTX[rng.randrange(len(XINT_CTX))] if ctx is None else XINT_CTX[ctx]
    b = q(b if b is not None else rng.randint(*d["brange"]))
    m = q(m if m is not None else rng.randint(*d["mrange"]))
    if m == 0 or b == m:
        raise ItemError("the rate must be non-zero and distinct from the starting amount")
    xi = b / m
    shown = dec(xi, d["places"]) if d["places"] is not None else numtext(xi)
    roles = d["roles"](numtext(b), numtext(m), shown)
    stem = d["stem"].format(b=numtext(b), m=numtext(m))
    extra = [(k, XINT_WHY[k]) for k in d["order"]]
    P = {"kind": "lf_interpret_x_intercept", "ask": "time",
         "b": [b.numerator, b.denominator], "m": [m.numerator, m.denominator]}
    rationale = (f"y = 0 when x = {numtext(b)}/{numtext(m)} = {shown}, the moment the "
                 f"quantity runs out.")
    return _role_item("lin.interpret_x_intercept", "interpreting an x-intercept", "medium",
                      seed, stem, P, roles, "time", rng, extra, rationale)
