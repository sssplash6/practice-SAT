"""The equation wrapped in a sentence.

Four things the source does with a context: state one and ask for the unknown,
state one and ask which equation models it, ask for an expression in terms of
the variable, and ask what one coefficient means. The last family here is the
only item in the topic that carries a table.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q
from math import gcd

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text
from .kit import article, choices, dec, money, num, plainly, sent, spr_mistakes

__all__ = ["context_solve", "model_count_mix", "model_context",
           "expression_in_terms", "interpret_coefficient", "percent_original"]

SCENES = ["membership", "books", "coupon", "candle", "plant", "museum",
          "overtime", "auger", "flags", "isosceles"]


# ------------------------------------------------------- a context to solve

def _scene(rng: random.Random, scene: str, kw: dict) -> dict:
    """(stem, m, k, total) with m*u + k = total, plus the scene's own slips."""
    g = lambda k_, d: Q(kw[k_]) if k_ in kw else Q(d)                   # noqa: E731

    if scene == "membership":
        fee = g("fee", rng.randint(15, 60))
        rate = g("rate", rng.randint(9, 45))
        months = g("months", rng.randint(3, 18))
        total = rate * months + fee
        place = kw.get("place", rng.choice(["gym", "swimming club", "climbing centre",
                                            "art studio", "music school"]))
        stem = (f"A {place} charges its members a onetime ${num(fee)} enrollment fee and "
                f"a membership fee of ${num(rate)} per month. If there are no charges "
                f"other than the enrollment fee and the membership fee, after how many "
                f"months will a member have been charged a total of ${num(total)} at "
                f"the {place}?")
        return {"stem": stem, "m": rate, "k": fee, "total": total,
                "extra": [("used twice the monthly fee", (total - fee) / (2 * rate))]}

    if scene == "books":
        each = g("each", rng.randint(2, 6))
        left = g("left", rng.randint(2, 12))
        kids = g("kids", rng.randint(8, 30))
        total = each * kids + left
        thing = kw.get("thing", rng.choice(["books", "pencils", "notebooks", "stickers"]))
        who = kw.get("who", rng.choice(["A librarian", "A teacher", "A volunteer"]))
        stem = (f"{who} has {num(total)} {thing} to distribute to a group of children. "
                f"If he gives each child {num(each)} {thing}, he will have {num(left)} "
                f"{thing} left over. How many children are in the group?")
        return {"stem": stem, "m": each, "k": left, "total": total,
                "extra": [("added the leftover instead of subtracting it",
                           (total + left) / each)]}

    if scene == "coupon":
        n = g("n", rng.randint(4, 12))
        price = g("price", rng.randint(6, 40))
        off = g("off", rng.randint(10, 80))
        total = n * price - off
        if total <= 0:
            raise ItemError("the coupon is worth more than the purchase")
        name = kw.get("name", rng.choice(["Nasir", "Priya", "Marco", "Elena", "Dwayne"]))
        thing = kw.get("thing", rng.choice(["storage bins", "plant pots", "folding chairs",
                                            "picture frames"]))
        stem = (f"{name} bought {num(n)} {thing} that were each the same price. "
                f"{name} used a coupon for ${num(off)} off the entire purchase. The cost "
                f"for the entire purchase after using the coupon was ${num(total)}. What "
                f"was the original price, in dollars, for 1 {thing[:-1]}?")
        return {"stem": stem, "m": n, "k": -off, "total": total,
                "extra": [("divided the discounted total by the number bought",
                           total / n)]}

    if scene == "candle":
        start = g("start", rng.randint(10, 30))
        hours = g("hours", rng.randint(2, 8))
        left = g("left", rng.randint(2, 9))
        if left >= start:
            raise ItemError("the candle would have gained wax")
        stem = (f"A candle is made of {num(start)} ounces of wax. When the candle is "
                f"burning, the amount of wax in the candle decreases by 1 ounce every "
                f"{num(hours)} hours. If {num(left)} ounces of wax remain in this candle, "
                f"for how many hours has it been burning?")
        return {"stem": stem, "m": -Q(1) / hours, "k": start, "total": left,
                "extra": [("reported the wax that is left rather than the time", left),
                          ("multiplied the wax that is left by the hours per ounce",
                           left * hours)]}

    if scene == "plant":
        rate = g("rate", Q(rng.randint(5, 30), 10))
        days = g("days", rng.randint(5, 20))
        start = g("start", Q(rng.randint(50, 400), 10))
        total = start + rate * days
        plant = kw.get("plant", rng.choice(["corn", "sunflower", "bean", "wheat"]))
        stem = (f"An agricultural scientist studying the growth of {plant} plants "
                f"recorded the height of a {plant} plant at the beginning of a study and "
                f"the height of the plant each day for the next {num(days)} days. The "
                f"scientist found that the height of the plant increased by an average "
                f"of {dec(rate)} centimeters per day for the {num(days)} days. If the "
                f"height of the plant on the last day of the study was {dec(total)} "
                f"centimeters, what was the height, in centimeters, of the {plant} plant "
                f"at the beginning of the study?")
        return {"stem": stem, "m": Q(1), "k": rate * days, "total": total, "dec": True,
                "extra": [("added a day's growth instead of subtracting it",
                           total + rate * days)]}

    if scene == "museum":
        per = g("per", rng.randint(5, 30))
        n = g("n", rng.randint(12, 60))
        costs = g("costs", rng.randint(40, 300))
        profit = per * n - costs
        if profit <= 0:
            raise ItemError("the day made a loss")
        thing = kw.get("thing", rng.choice(["tablets", "audio guides", "lockers", "bicycles"]))
        place = kw.get("place", rng.choice(["museum", "gallery", "aquarium", "science centre"]))
        day = kw.get("day", rng.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]))
        stem = (f"A {place} rents {thing} to visitors. The {place} earns revenue of "
                f"${num(per)} for each {thing[:-1]} rented for the day. On {day}, the "
                f"{place} earned ${num(profit)} in profit from renting {thing} after "
                f"paying daily expenses of ${num(costs)}. How many {thing} did the "
                f"{place} rent on {day}? (profit = total revenue - total expenses).")
        return {"stem": stem, "m": per, "k": -costs, "total": profit,
                "extra": [("left the expenses out of the revenue", profit / per)]}

    if scene == "overtime":
        base = g("base", 8)
        worked = g("worked", rng.randint(9, 12))
        wage = g("wage", Q(rng.randint(36, 96), 4))
        rate = g("rate", Q(3, 2))
        total = wage * (base + rate * (worked - base))
        # The stem prints the total in dollars and cents, so a total that needs
        # a third decimal place is rounded on the page, and the wage the page
        # then implies is not the answer: $206.62 over 9.5 hours is not $21.75.
        if (total * 100).denominator != 1:
            raise ItemError("the total would not print exactly in cents")
        name = kw.get("name", rng.choice(["Megan", "Andre", "Priya", "Tomas", "Lucia"]))
        stem = (f"{name}'s regular wage at her job is p dollars per hour for the first "
                f"{num(base)} hours of work in a day plus {dec(rate)} times her regular "
                f"hourly wage for work in excess of {num(base)} hours that day. On a "
                f"given day, {name} worked for {num(worked)} hours, and her total "
                f"earnings for that day were {money(total)}. What is {name}'s regular "
                f"hourly wage?")
        m = base + rate * (worked - base)
        return {"stem": stem, "m": m, "k": Q(0), "total": total, "money": True,
                "extra": [("divided by the hours worked, ignoring the overtime rate",
                           total / worked),
                          ("used the regular hours only", total / base)]}

    if scene == "auger":
        start = g("start", rng.randint(120, 400) * 100)
        rate = g("rate", rng.randint(300, 1200))
        t1 = g("t1", rng.randint(3, 8))
        t2 = g("t2", t1 + rng.randint(3, 12))
        mid = start - rate * t1
        left = start - rate * t2
        if left <= 0 or mid <= 0:
            raise ItemError("the bin would be empty before the second reading")
        who = kw.get("who", rng.choice(["Hector", "Marisol", "Owen", "Ingrid"]))
        crop = kw.get("crop", rng.choice(["corn", "wheat", "barley", "oats"]))
        stem = (f"{who} used a tool called an auger to remove {crop} from a storage bin "
                f"at a constant rate. The bin contained {num(start)} bushels of {crop} "
                f"when {who} began to use the auger. After {num(t1)} hours of using the "
                f"auger, {num(mid)} bushels of {crop} remained in the bin. If the auger "
                f"continues to remove {crop} at this rate, what is the total number of "
                f"hours {who} will have been using the auger when {num(left)} bushels of "
                f"{crop} remain in the bin?")
        return {"stem": stem, "m": -rate, "k": start, "total": left,
                "extra": [("found the extra hours after the first reading instead of "
                           "the total", t2 - t1),
                          ("used the first reading as the starting amount",
                           (mid - left) / rate)]}

    if scene == "flags":
        total = g("total", rng.randint(15, 60))
        one = g("one", rng.randint(5, 40))
        if one >= total:
            raise ItemError("one colour already uses every flag")
        c1, c2 = kw.get("c1"), kw.get("c2")
        if not c1:
            c1, c2 = rng.sample(["blue", "yellow", "green", "red", "purple"], 2)
        who = kw.get("who", rng.choice(["A principal", "A coach", "A scout leader"]))
        event = kw.get("event", rng.choice(["field day", "sports day", "the fun run"]))
        stem = (f"{who} used a total of {num(total)} flags that were either {c1} or {c2} "
                f"for {event}. The {who.split()[-1]} used {num(one)} {c1} flags. How many "
                f"{c2} flags were used?")
        return {"stem": stem, "m": Q(1), "k": one, "total": total,
                "extra": [("reported the flags of the other colour", one),
                          ("reported the total number of flags", total)]}

    # isosceles
    leg = g("leg", rng.randint(8, 40))
    third = g("third", rng.randint(4, 50))
    perim = leg * 2 + third
    if third >= 2 * leg or third <= 0:
        raise ItemError("those three lengths do not close a triangle")
    stem = (f"The perimeter of an isosceles triangle is {num(perim)} inches. Each of the "
            f"two congruent sides of the triangle has a length of {num(leg)} inches. "
            f"What is the length, in inches, of the third side?")
    return {"stem": stem, "m": Q(1), "k": 2 * leg, "total": perim,
            "extra": [("subtracted only one of the congruent sides", perim - leg),
                      ("halved the perimeter and subtracted a side", perim / 2 - leg)]}


def context_solve(rng: random.Random, seed: int, *, scene=None, fmt=None, **kw) -> Item:
    """A sentence that becomes m*u + k = total, solved for the unknown."""
    scene = scene or rng.choice(SCENES)
    s = _scene(rng, scene, kw)
    m, k, total = Q(s["m"]), Q(s["k"]), Q(s["total"])
    if m == 0:
        raise ItemError("no rate to divide by")
    key = (total - k) / m
    if key <= 0:
        raise ItemError("a count or a price has to come out positive")
    fmt = fmt or ("spr" if rng.random() < 0.35 else "mcq")
    P = {"kind": "lin1_context", "scene": scene, "m": float(m), "k": float(k),
         "total": float(total), "money": bool(s.get("money")) and fmt == "mcq"}
    u = "u" if m == 1 else ("-u" if m == -1 else f"{plainly(m)}u")
    if m < 0 and k != 0:                       # 24,000 - 930u reads better
        u = f"{plainly(k)} - {plainly(-m)}u"
    elif k > 0:
        u = f"{u} + {plainly(k)}"
    elif k < 0:
        u = f"{u} - {plainly(-k)}"
    rationale = (f"The sentence gives {u} = {plainly(total)}, where u is the unknown, "
                 f"so u = {plainly(key)}.")
    ex = E(key)
    mistakes = [Mis(why, E(Q(v))) for why, v in s.get("extra", [])]
    mistakes += [
        Mis("added the fixed amount instead of subtracting it", E((total + k) / m)),
        Mis("reported the fixed amount given in the problem", E(k) if k else None),
        Mis("reported the total given in the problem", E(total)),
        Mis("forgot to divide by the rate", E(total - k)),
        Mis("divided the total by the rate without removing the fixed amount",
            E(total / m)),
    ]
    # a count, a price and a length of time are positive: where the model's rate
    # or fixed amount is negative, a mistake's value has the wrong sign
    positive = [x for x in mistakes if x.value is not None and x.value.coef > 0]
    if fmt == "spr":
        if ex.coef.denominator > 1000:
            raise ItemError("this grid-in answer would not be enterable")
        return Item("lin1.context_solve", "linear equation in context", "medium", seed,
                    sent(s["stem"]), "spr", ex, ex.gridin(), rationale, params=P,
                    spr_mistakes=spr_mistakes(ex, positive))
    # and an option orders of magnitude away from the answer is crossed out
    # without any algebra
    lo, hi = key / 25, key * 25
    usable = [x for x in positive if lo <= Q(x.value.coef) <= hi]
    fv = (lambda v: money(v.coef)) if s.get("money") else None
    ch, tex, why, letter = choices(ex, usable, rng, fmt_value=fv)
    return Item("lin1.context_solve", "linear equation in context", "medium", seed,
                sent(s["stem"]), "mcq", ex, letter, rationale, ch, why, tex, params=P)


# ------------------------------------------- which equation models the counts

MIX = {
    "polygon": {"maker": None, "unit": "cm"},
    "factory": {"maker": "factory", "unit": "inch"},
    "plant": {"maker": "manufacturing plant", "unit": "inch"},
}


def model_count_mix(rng: random.Random, seed: int, *, scene=None, var="n", l1=None,
                    l2=None, l3=None, mult=None, fixed=None, total=None,
                    thing=None) -> Item:
    """Three sizes, one of them a multiple of another: which equation counts them?"""
    scene = scene or rng.choice(list(MIX))
    l1 = int(l1 if l1 is not None else rng.randint(5, 15))
    l2 = int(l2 if l2 is not None else rng.choice([i for i in range(2, 15) if i != l1]))
    l3 = int(l3 if l3 is not None else rng.choice([i for i in range(2, 15)
                                                   if i not in (l1, l2)]))
    mult = int(mult if mult is not None else rng.randint(2, 8))
    fixed = int(fixed if fixed is not None else rng.randint(4, 40))
    total = int(total if total is not None else rng.choice([30, 50, 60, 80, 100, 120]))
    if len({l1, l2, l3}) != 3 or fixed >= total:
        raise ItemError("the three lengths must differ and leave room for the rest")
    if (total - fixed) % (mult + 1):
        raise ItemError("the counts would not come out whole")
    # Every option is an equation, and two equations that hold for the same n
    # are one equation however differently they print. The pieces-times-lengths
    # option is the one that collides: 9n + 7n + 4n = 60 and 8n + 36 = 60 both
    # say n = 3.
    n = Q(total - fixed, mult + 1)
    for A, B in ((l1 * mult + l2, l3 * fixed), (l1 + l2 + l3, 0), (mult, fixed)):
        if A * n + B == total:
            raise ItemError("a wrong equation would be true for the same n")

    if scene == "polygon":
        thing = thing or "polygon"
        stem = (f"Each side of {article(total)} {total}-sided {thing} has one of three "
                f"lengths. The "
                f"number of sides with length {l1} centimeters (cm) is {mult} times the "
                f"number of sides {var} with length {l2} cm. There are {fixed} sides "
                f"with length {l3} cm. Which equation must be true for the value of "
                f"{var}?")
    else:
        thing = thing or rng.choice(["concrete screws", "frying pans", "steel brackets",
                                     "copper pipes", "ceramic tiles"])
        maker = MIX[scene]["maker"]
        stem = (f"A {maker} makes {l1}-inch, {l2}-inch, and {l3}-inch {thing}. During a "
                f"certain day, the number of {l1}-inch {thing} that the {maker} makes is "
                f"{mult} times the number {var} of {l2}-inch {thing} it makes, and the "
                f"number of {l3}-inch {thing} it makes is {fixed}. During this day, the "
                f"{maker} makes {total} {thing} total. Which equation represents this "
                f"situation?")
    key = f"{mult + 1}{var} + {num(fixed)} = {num(total)}"
    mistakes = [
        Mis("weighted each count by its length instead of counting the pieces",
            f"{l1}({mult}{var}) + {l2}{var} + {l3}({num(fixed)}) = {num(total)}"),
        Mis("multiplied by the lengths and used the same count for all three",
            f"{l1}{var} + {l2}{var} + {l3}{var} = {num(total)}"),
        Mis(f"left out the {var} pieces of the second length",
            f"{mult}{var} + {num(fixed)} = {num(total)}"),
    ]
    P = {"kind": "lin1_count_mix", "scene": scene, "var": var, "l1": l1, "l2": l2,
         "l3": l3, "mult": mult, "fixed": fixed, "total": total}
    ch, why, letter = assemble_text(key, mistakes, rng)
    rationale = (f"There are {mult}{var} of the first length, {var} of the second and "
                 f"{fixed} of the third, and they total {total}.")
    return Item("lin1.model_count_mix", "modelling", "hard", seed, sent(stem), "mcq",
                E(1), letter, rationale, ch, why, ch, params=P)


# ----------------------------------------- which equation models the sentence

def model_context(rng: random.Random, seed: int, *, shape=None, var=None, **kw) -> Item:
    """The numbers are given; pick the equation, not the answer."""
    shape = shape or rng.choice(["phrase", "base_after", "fuel", "unit_profit"])
    g = lambda k_, d: Q(kw[k_]) if k_ in kw else Q(d)                   # noqa: E731

    if shape == "phrase":
        var = var or kw.get("var", rng.choice(["x", "n", "y", "p"]))
        mlt = g("mult", rng.randint(2, 12))
        add = g("add", rng.randint(2, 20))
        tot = g("total", rng.randint(20, 120))
        if mlt == add:
            raise ItemError("two options would read the same")
        stem = (f"{num(add)} more than {num(mlt)} times a number {var} is equal to "
                f"{num(tot)}. Which equation represents this situation?")
        key = f"{num(mlt)}{var} + {num(add)} = {num(tot)}"
        mistakes = [
            Mis("multiplied the two numbers together instead of adding one of them",
                f"({num(add)})({num(mlt)}){var} = {num(tot)}"),
            Mis("added the smaller number to the wrong side of the equation",
                f"{num(mlt)}{var} = {num(tot)} + {num(add)}"),
            Mis("swapped the multiplier and the number added",
                f"{num(add)}{var} + {num(mlt)} = {num(tot)}")]
        root = (tot - add) / mlt
        wrong = [tot / (add * mlt), (tot + add) / mlt, (tot - mlt) / add]
        P = {"mult": float(mlt), "add": float(add), "total": float(tot)}

    elif shape == "base_after":
        var = var or kw.get("var", "t")
        base = g("base", rng.randint(200, 1200))
        hrs = g("hrs", rng.randint(2, 5))
        rate = g("rate", rng.randint(20, 90))
        extra = g("extra", rng.randint(1, 8))
        tot = g("total", base + rate * extra)
        thing = kw.get("thing", rng.choice(["a commercial fishing boat", "a party bus",
                                            "a mobile crane", "a recording studio"]))
        stem = (f"The cost to rent {thing} from a certain company is ${num(base)} for the "
                f"first {num(hrs)} hours and an additional ${num(rate)} per hour for each "
                f"hour after the first {num(hrs)} hours. If the total cost to rent "
                f"{thing} from the company for {var} hours, where {var} > {num(hrs)}, is "
                f"${num(tot)}, which equation represents this situation?")
        key = f"{num(base)} + {num(rate)}({var} - {num(hrs)}) = {num(tot)}"
        mistakes = [
            Mis("charged the flat fee for every hour and the hourly rate from the start",
                f"{num(base)}({var} - {num(hrs)}) + {num(rate)}{var} = {num(tot)}"),
            Mis("multiplied the hours by the opening period instead of subtracting it",
                f"{num(base)}({num(hrs)}{var}) + {num(rate)}{var} = {num(tot)}"),
            Mis("multiplied the hours by the opening period inside the brackets",
                f"{num(base)} + {num(rate)}({num(hrs)}{var}) = {num(tot)}")]
        root = hrs + (tot - base) / rate
        wrong = [(tot + base * hrs) / (base + rate), tot / (base * hrs + rate),
                 (tot - base) / (rate * hrs)]
        P = {"base": float(base), "hrs": float(hrs), "rate": float(rate),
             "total": float(tot)}

    elif shape == "fuel":
        var = var or kw.get("var", "m")
        miles = g("miles", rng.randint(60, 300))
        mpg = g("mpg", rng.randint(15, 45))
        cost = g("cost", rng.randint(2, 6))
        cut = g("cut", rng.randint(2, 12))
        if gcd(int(cost), int(mpg)) != 1 or cut >= miles:
            raise ItemError("the rate would print as a fraction that cancels")
        name = kw.get("name", rng.choice(["Alan", "Rosa", "Dmitri", "Naomi"]))
        stem = (f"{name} drives an average of {num(miles)} miles each week. {name}'s car "
                f"can travel an average of {num(mpg)} miles per gallon of gasoline. "
                f"{name} would like to reduce the weekly expenditure on gasoline by "
                f"${num(cut)}. Assuming gasoline costs ${num(cost)} per gallon, which "
                f"equation can {name} use to determine how many fewer average miles, "
                f"{var}, should be driven each week?")
        key = f"({num(cost)}/{num(mpg)}){var} = {num(cut)}"
        mistakes = [
            Mis("inverted the rate, putting miles per gallon over dollars per gallon",
                f"({num(mpg)}/{num(cost)}){var} = {num(cut)}"),
            Mis("set the equation equal to the miles left rather than the dollars saved",
                f"({num(cost)}/{num(mpg)}){var} = {num(miles - cut)}"),
            Mis("inverted the rate and used the miles left rather than the dollars saved",
                f"({num(mpg)}/{num(cost)}){var} = {num(miles - cut)}")]
        root = cut * mpg / cost
        wrong = [cut * cost / mpg, (miles - cut) * mpg / cost,
                 (miles - cut) * cost / mpg]
        P = {"miles": float(miles), "mpg": float(mpg), "cost": float(cost),
             "cut": float(cut)}

    else:                                   # unit_profit
        var = var or kw.get("var", "u")
        price = g("price", rng.randint(40, 200))
        make = g("make", rng.randint(10, 90))
        comm = g("comm", Q(rng.choice([5, 10, 15, 20, 25]), 100))
        units = g("units", rng.randint(60, 600))
        unit_profit = price * (1 - comm) - make
        if unit_profit <= 0 or unit_profit.denominator != 1:
            raise ItemError("the profit per unit must be a positive whole number")
        tot = g("total", unit_profit * units)
        thing = kw.get("thing", "product")
        stem = (f"A certain {thing} costs a company ${num(make)} to make. The {thing} is "
                f"sold by a salesperson who earns a commission that is equal to "
                f"{num(comm * 100)}% of the sales price of the {thing}. The profit the "
                f"company makes for each unit is equal to the sales price minus the "
                f"combined cost of making the {thing} and the commission. If the sales "
                f"price of the {thing} is ${num(price)}, which of the following equations "
                f"gives the number of units, {var}, of the {thing} the company sold to "
                f"make a profit of ${num(tot)}?")
        key = f"({num(price)}(1 - {dec(comm)}) - {num(make)}){var} = {num(tot)}"
        mistakes = [
            Mis("took the commission off the profit rather than off the sales price",
                f"({num(price)} - {num(make)})(1 - {dec(1 - comm)}){var} = {num(tot)}"),
            Mis("left the number of units off the cost of making the product",
                f"{dec(1 - comm)}({num(price)}) - {num(make)}{var} = {num(tot)}"),
            Mis("added the commission to the cost instead of subtracting it from the "
                "price", f"({dec(comm)}({num(price)}) + {num(make)}){var} = {num(tot)}")]
        root = tot / unit_profit
        wrong = [tot / ((price - make) * comm),
                 ((1 - comm) * price - tot) / make,
                 tot / (comm * price + make)]
        P = {"price": float(price), "make": float(make), "comm": float(comm),
             "total": float(tot)}

    # Every option here is an equation, and two equations with the same solution
    # are the same equation however differently they print. The commission
    # distractor is the one that collides: at make = price(1 - 2c)/2 the price
    # less the commission less the cost and the commission plus the cost are the
    # same number, so (160(1 - 0.15) - 56)u and (0.15(160) + 56)u both give
    # u = 234.
    if any(w == root for w in wrong):
        raise ItemError("a wrong equation would have the same solution as the key")
    P.update({"kind": "lin1_model_context", "shape": shape, "var": var})
    ch, why, letter = assemble_text(key, mistakes, rng)
    return Item("lin1.model_context", "modelling", "medium", seed, sent(stem), "mcq",
                E(1), letter, _model_why(shape, P, var, key), ch, why, ch, params=P)


def _model_why(shape: str, P: dict, var: str, key: str) -> str:
    """Why the equation is that one -- which phrase of the sentence became
    which term. Saying "the situation is exactly <key>" teaches nobody what
    they got wrong."""
    n = lambda k: num(Q(P[k]))                                      # noqa: E731
    if shape == "phrase":
        return (f"\"{n('mult')} times a number\" is {n('mult')}{var}, and \"{n('add')} "
                f"more than\" adds {n('add')} to it, so {key}.")
    if shape == "base_after":
        return (f"The ${n('base')} buys the first {n('hrs')} hours, so only the "
                f"{var} - {n('hrs')} hours after that are charged at ${n('rate')}, "
                f"giving {key}.")
    if shape == "fuel":
        return (f"One mile costs ${n('cost')} divided by {n('mpg')} miles per gallon, so "
                f"cutting {var} miles a week saves that much for each of them: {key}.")
    return (f"Each unit earns the ${n('price')} price less the commission on it and less "
            f"the ${n('make')} it costs to make, and {var} units earn that many times "
            f"over, so {key}.")


# --------------------------------------- an expression in terms of a variable

def expression_in_terms(rng: random.Random, seed: int, *, shape=None, var=None,
                        **kw) -> Item:
    """The options are expressions, so the answer is the translation itself."""
    shape = shape or rng.choice(["unit_rate", "more_than_times", "perimeter", "two_kinds"])
    g = lambda k_, d: Q(kw[k_]) if k_ in kw else Q(d)                   # noqa: E731

    if shape == "unit_rate":
        var = var or kw.get("var", "c")
        price = g("price", rng.randint(2, 20))
        thing = kw.get("thing", rng.choice(["grapes", "walnuts", "flour", "coffee beans",
                                            "rice"]))
        stem = (f"One pound of {thing} costs ${num(price)}. At this rate, how many "
                f"dollars will {var} pounds of {thing} cost?")
        key = f"{num(price)}{var}"
        mistakes = [Mis("added the price to the weight instead of multiplying",
                        f"{num(price)} + {var}"),
                    Mis("divided the price by the weight", f"{num(price)}/{var}"),
                    Mis("divided the weight by the price", f"{var}/{num(price)}")]
        P = {"price": float(price)}

    elif shape == "more_than_times":
        var = var or kw.get("var", "n")
        mlt = g("mult", rng.randint(2, 9))
        add = g("add", rng.choice([i for i in range(2, 12)]))
        if mlt == add:
            raise ItemError("two options would read the same")
        thing = kw.get("thing", rng.choice(["CDs", "marbles", "stamps", "badges", "comics"]))
        a, b = kw.get("a"), kw.get("b")
        if not a:
            a, b = rng.sample(["Cathy", "Gerry", "Hana", "Luis", "Priya", "Owen"], 2)
        times = "twice" if mlt == 2 else f"{num(mlt)} times"
        stem = (f"{a} has {var} {thing}. {b} has {num(add)} more than {times} "
                f"the number of {thing} that {a} has. In terms of {var}, how many "
                f"{thing} does {b} have?")
        key = f"{num(mlt)}{var} + {num(add)}"
        mistakes = [
            Mis("swapped the multiplier and the constant, and subtracted",
                f"{num(add)}{var} - {num(mlt)}"),
            Mis("swapped the multiplier and the constant", f"{num(add)}{var} + {num(mlt)}"),
            Mis("subtracted the constant instead of adding it",
                f"{num(mlt)}{var} - {num(add)}")]
        P = {"mult": float(mlt), "add": float(add)}

    elif shape == "perimeter":
        var = var or kw.get("var", "w")
        d = g("d", rng.randint(2, 20))
        thing = kw.get("thing", rng.choice(["dance floor", "garden bed", "patio",
                                            "swimming pool", "rug"]))
        short = thing.split()[-1]
        stem = (f"The width of a rectangular {thing} is {var} feet. The length of the "
                f"{short} is {num(d)} feet longer than its width. Which of the "
                f"following expresses the perimeter, in feet, of the {thing} in terms "
                f"of {var}?")
        key = f"4{var} + {num(2 * d)}"
        mistakes = [
            Mis("added the two different sides and stopped", f"2{var} + {num(d)}"),
            Mis("found the area and left the width out of the second term",
                f"{var}^2 + {num(d)}"),
            Mis("found the area instead of the perimeter", f"{var}^2 + {num(d)}{var}")]
        P = {"d": float(d)}

    else:                                   # two_kinds
        var = var or kw.get("var", "x")
        n = g("n", rng.randint(4, 12))
        p = g("p", rng.randint(3, 12))
        q = g("q", rng.choice([i for i in range(2, 11)]))
        if p == q or p < q:
            raise ItemError("the first requirement must be the larger of the two")
        unit = kw.get("unit", rng.choice(["teaspoons of salt", "grams of sugar",
                                          "millilitres of dye"]))
        stem = (f"A science teacher is preparing the {num(n)} stations of a science "
                f"laboratory. Each station will have either Experiment A materials or "
                f"Experiment B materials, but not both. Experiment A requires {num(p)} "
                f"{unit}, and Experiment B requires {num(q)} {unit}. If {var} is the "
                f"number of stations that will be set up for Experiment A and the "
                f"remaining stations will be set up for Experiment B, which of the "
                f"following expressions represents the total number of {unit} required?")
        key = f"{num(p - q)}{var} + {num(q * n)}"
        mistakes = [
            Mis("counted the stations and forgot the two different requirements",
                f"{num(n)}{var}"),
            Mis("added the two requirements and applied them to every station",
                f"{num(p + q)}{var}"),
            Mis("added the two requirements instead of subtracting one from the other",
                f"{num(p + q)}{var} + {num(q * n)}")]
        P = {"n": float(n), "p": float(p), "q": float(q)}

    P.update({"kind": "lin1_expression", "shape": shape, "var": var})
    ch, why, letter = assemble_text(key, mistakes, rng)
    return Item("lin1.expression_in_terms", "modelling", "easy", seed, sent(stem), "mcq",
                E(1), letter, f"In terms of {var} the total is {key}.", ch, why, ch,
                params=P)


# --------------------------------------- what one coefficient means in context

def interpret_coefficient(rng: random.Random, seed: int, *, scene=None, **kw) -> Item:
    """The number is in the equation; the question is what it measures."""
    scene = scene or rng.choice(["growth", "revenue"])
    g = lambda k_, d: Q(kw[k_]) if k_ in kw else Q(d)                   # noqa: E731

    if scene == "growth":
        var = kw.get("var", "n")
        rate = g("rate", rng.randint(2, 9))
        start = g("start", rng.randint(2, 20))
        years = g("years", rng.randint(2, 12))
        final = start + rate * years
        # The three wrong readings are numbers too: the years to double the
        # height, the height after one year, and the years to grow the final
        # height. When one of them comes out at the rate itself -- start = rate^2
        # or final = rate^2 -- that sentence is a true interpretation of the very
        # number the stem asks about, and the item has two right answers.
        for also in (start / rate, start + rate, final / rate):
            if also == rate:
                raise ItemError("a wrong interpretation would be true of this number")
        thing = kw.get("thing", rng.choice(["tree", "hedge", "sapling", "bamboo stalk"]))
        eq = f"{num(rate)}{var} + {num(start)} = {num(final)}"
        stem = (f"{eq} A {thing} had a height of {num(start)} feet when it was planted. "
                f"The equation above can be used to find how many years {var} it took the "
                f"{thing} to reach a height of {num(final)} feet. Which of the following "
                f"is the best interpretation of the number {num(rate)} in this context?")
        key = f"The average number of feet that the {thing} grew per year"
        mistakes = [
            Mis("read the coefficient as a count of years rather than a rate",
                f"The number of years it took the {thing} to double its height"),
            Mis("read the coefficient as a height rather than a rate of change",
                f"The height, in feet, of the {thing} when the {thing} was 1 year old"),
            Mis("attached the rate to the final height instead of to each year",
                f"The average number of years it takes similar {thing}s to grow "
                f"{num(final)} feet")]
        P = {"rate": float(rate), "start": float(start), "years": float(years)}
    else:
        var = kw.get("var", "x")
        price = g("price", Q(rng.randint(150, 900), 100))
        costs = g("costs", rng.randint(1000, 9000))
        profit = g("profit", rng.randint(5000, 40000))
        thing = kw.get("thing", rng.choice(["tape dispensers", "phone cases",
                                            "bicycle bells", "desk lamps"]))
        eq = f"{num(profit)} = {dec(price)}{var} - {num(costs)}"
        stem = (f"A company that creates and sells {thing} calculates its monthly profit, "
                f"in dollars, by subtracting its fixed monthly costs, in dollars, from "
                f"its monthly sales revenue, in dollars. The equation {eq} represents "
                f"this situation for a month where {var} {thing} are created and sold. "
                f"Which statement is the best interpretation of {dec(price)}{var} in this "
                f"context?")
        key = f"The monthly sales revenue, in dollars, from selling {var} {thing}"
        mistakes = [
            Mis("read the whole term as the price of a single unit",
                f"The monthly sales revenue, in dollars, from each {thing[:-1]} sold"),
            Mis("read revenue as cost and the term as a single unit",
                f"The monthly cost, in dollars, of creating each {thing[:-1]}"),
            Mis("read revenue as cost", f"The monthly cost, in dollars, of creating "
                                        f"{var} {thing}")]
        P = {"price": float(price), "costs": float(costs), "profit": float(profit)}

    P.update({"kind": "lin1_interpret", "scene": scene, "thing": thing,
              "var": var})
    ch, why, letter = assemble_text(key, mistakes, rng)
    return Item("lin1.interpret_coefficient", "modelling", "medium", seed, sent(stem),
                "mcq", E(1), letter,
                f"A rate multiplied by {var} gives the total across all {var}, not the "
                f"amount for one of them, so the term is {key.lower()}.",
                ch, why, ch, params=P)


# ------------------------------------------- two discounts, back to the original

STREETS = ["Clearwater Lane", "Driftwood Drive", "Edgemont Street", "Glenview Street",
           "Hamilton Circle", "Alder Court", "Bayview Road", "Fernwood Way",
           "Juniper Place", "Kingsley Avenue", "Larkspur Lane", "Milton Crescent",
           "Northgate Row", "Sandpiper Close"]
GROUPS = ["Townsend Realty Group", "Halloway Property Partners", "Brightwater Holdings",
          "Marchmont Estates", "Cordova Realty Group", "Pinehurst Property Group"]


def percent_original(rng: random.Random, seed: int, *, group=None, target=None,
                     d1=None, d2=None, price=None, rents=None, prices=None,
                     streets=None) -> Item:
    """Two discounts in a row, and the original price they came off."""
    group = group or rng.choice(GROUPS)
    streets = list(streets) if streets else sorted(rng.sample(STREETS, 5))
    target = target or rng.choice(streets)
    if target not in streets:
        raise ItemError("the property asked about is not in the table")
    d1 = Q(d1 if d1 is not None else rng.choice([10, 15, 20, 25, 30, 35, 40, 45, 50]), 100)
    d2 = Q(d2 if d2 is not None else rng.choice([5, 10, 15, 20, 25, 30]), 100)
    if d1 == d2:
        raise ItemError("two equal discounts make two options identical")
    prices = list(prices) if prices else sorted(
        rng.sample([n * 1000 for n in range(60, 480, 2)], 5))
    rents = list(rents) if rents else [round(p * 0.0074 / 5) * 5 for p in prices]
    paid = Q(price if price is not None else prices[streets.index(target)])

    def to_hundred(v):
        return Q(round(float(v) / 100) * 100)

    key = to_hundred(paid / ((1 - d1) * (1 - d2)))
    wrong = [("applied only the larger discount and stopped", to_hundred(paid / (1 - d1))),
             ("applied only the additional discount", to_hundred(paid / (1 - d2))),
             ("treated the first discount as the fraction that was paid, not the "
              "fraction taken off", to_hundred(paid / d1)),
             ("added the two discounts and took them off once",
              to_hundred(paid / (1 - d1 - d2)) if d1 + d2 < 1 else None),
             ("multiplied by the discounts instead of dividing",
              to_hundred(paid * (1 - d1) * (1 - d2)))]
    table = [["Property address", "Purchase price (dollars)", "Monthly rental price (dollars)"]]
    for s, p_, r_ in zip(streets, prices, rents):
        table.append([s, f"{int(p_):,}", f"{int(r_):,}"])
    stem = (f"The {group} invested in the five different properties listed in the table "
            f"above. The table shows the amount, in dollars, the company paid for each "
            f"property and the corresponding monthly rental price, in dollars, the "
            f"company charges for the property at each of the five locations. {group} "
            f"purchased the {target} property and received a {num(d1 * 100)}% discount "
            f"off the original price along with an additional {num(d2 * 100)}% off the "
            f"discounted price for purchasing the property in cash. Which of the "
            f"following best approximates the original price, in dollars, of the "
            f"{target} property?")
    P = {"kind": "lin1_percent_original", "paid": float(paid), "d1": float(d1),
         "d2": float(d2)}
    mistakes = [Mis(w, E(v)) for w, v in wrong if v is not None and v != key]
    ex = E(key)
    ch, tex, why, letter = choices(ex, mistakes, rng,
                                   fmt_value=lambda v: money(v.coef, cents=False))
    rationale = (f"The company paid {money(paid, cents=False)} for "
                 f"(1 - {dec(d1)})(1 - {dec(d2)}) of the original price, so the original "
                 f"price was about {money(key, cents=False)}.")
    return Item("lin1.percent_original", "linear equation in context", "hard", seed,
                sent(stem), "mcq", ex, letter, rationale, ch, why, tex, table=table,
                params=P)
