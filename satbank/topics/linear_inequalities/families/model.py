"""Turning a situation into an inequality -- the largest family in the source set.

Three templates, split by what the answer looks like on the page: one relation
in two variables, one relation in a single variable, and a system of two or
four. The distractors are the ones College Board actually prints, and they are
nearly always the same two mistakes in combination: the relation read the wrong
way round ("at most" heard as "at least"), and the two rates attached to the
wrong quantities.
"""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, ItemError, Mis
from .kit import (FLIP, MINUS, Q, WORD, dec, num, rel, sent, side, term,
                  text_choices)

__all__ = ["model_two_var", "model_one_var", "model_system"]


def _cap_word(op: str) -> str:
    return "a maximum" if op in ("<", "<=") else "a minimum"


def _flip_reason(op: str) -> str:
    return (f"read the limit as {_cap_word(FLIP[op])} instead of "
            f"{_cap_word(op)}")


# --------------------------------------------------------- two variables

TWO_VAR = {
    "beads": dict(
        style="percent",
        stem="{who} bought two containers of {thing}. In the first container "
             "{p1}% of the {thing} are {adj}, and in the second container {p2}% "
             "of the {thing} are {adj}. Together, the containers have {word} "
             "{total} {adj} {thing}. Which inequality shows this relationship, "
             "where {u} is the total number of {thing} in the first container "
             "and {v} is the total number of {thing} in the second container?",
        swap="attached each percentage to the other container"),
    "drive": dict(
        style="rate",
        stem="On a car trip, {a_name} and {b_name} each drove for part of the "
             "trip, and the total distance they drove was {word} {total} miles. "
             "{a_name} drove at an average speed of {p1} miles per hour (mph), "
             "and {b_name} drove at an average speed of {p2} mph. Which of the "
             "following inequalities represents this situation, where {u} is "
             "the number of hours {a_name} drove and {v} is the number of hours "
             "{b_name} drove?",
        swap="gave each driver the other driver's average speed"),
    "store": dict(
        style="price",
        stem="A clothing store is having a sale on {t1} and {t2}. During the "
             "sale, the cost of each {s1} is ${p1} and the cost of each {s2} is "
             "${p2}. {who} can spend {word} ${total} at the store. If {who} buys "
             "{u} {t1} and {v} {t2}, which of the following must be true?",
        swap="attached each price to the other kind of item"),
}
TWO_VAR_NAMES = list(TWO_VAR)

WHO = ["Valentina", "Geoff", "Amara", "Dmitri", "Priya", "Hassan", "Lena",
       "Marcus", "Sofia", "Tobias"]
PAIRS = [("Rhett", "Jessica"), ("Omar", "Nadia"), ("Callum", "Rosa"),
         ("Ines", "Peter"), ("Jamal", "Beatriz")]
BEADS = [("beads", "red"), ("beads", "blue"), ("marbles", "green"),
         ("tiles", "white"), ("buttons", "black")]
CLOTHES = [("shirts", "shirt", "pants", "pair of pants"),
           ("hats", "hat", "scarves", "scarf"),
           ("socks", "pair of socks", "belts", "belt"),
           ("ties", "tie", "jackets", "jacket")]


def model_two_var(rng: random.Random, seed: int, *, scene=None, a=None, b=None,
                  total=None, op=None, u="x", v="y", who=None, names=None,
                  thing=None, adj=None, clothes=None) -> Item:
    """Two unit rates and one bound: 15s + 25p ≤ 120."""
    scene = scene or rng.choice(TWO_VAR_NAMES)
    d = TWO_VAR[scene]
    op = op or rng.choice(["<=", ">=", "<", ">"])
    if d["style"] == "percent":
        p1 = 10 * rng.randint(1, 9) if a is None else int(Q(a) * 100)
        p2 = 10 * rng.randint(1, 9) if b is None else int(Q(b) * 100)
        ca, cb = Q(p1, 100), Q(p2, 100)
    else:
        p1 = rng.choice([5, 8, 10, 12, 15, 20, 25, 30, 35, 40, 45, 50]) \
            if a is None else a
        p2 = rng.choice([5, 8, 10, 12, 15, 20, 25, 30, 35, 40, 45, 50]) \
            if b is None else b
        ca, cb = Q(p1), Q(p2)
    if ca == cb:
        raise ItemError("two equal rates make the swapped option the key")
    total = total if total is not None else rng.choice(
        [80, 100, 120, 150, 180, 200, 220, 250, 300, 400, 500])
    decimal = d["style"] == "percent"

    lhs = side([(ca, u), (cb, v)], decimal=decimal)
    key = rel(lhs, op, num(total))
    swapped = side([(cb, u), (ca, v)], decimal=decimal)

    wrong = [Mis(f"{d['swap']} and {_flip_reason(op)}",
                 rel(swapped, FLIP[op], num(total)))]
    if d["style"] == "percent":
        wrong += [
            Mis("divided by the first digit of each percentage instead of "
                "multiplying by the decimal it stands for",
                rel(f"{u}/{p1 // 10} + {v}/{p2 // 10}", FLIP[op], num(total))),
            Mis("used the percentages as whole numbers instead of as decimals",
                rel(side([(p1, u), (p2, v)]), op, num(total)))]
    wrong += [Mis(_flip_reason(op), rel(lhs, FLIP[op], num(total))),
              Mis(d["swap"], rel(swapped, op, num(total)))]

    who = who or rng.choice(WHO)
    a_name, b_name = names or rng.choice(PAIRS)
    thing, adj = (thing, adj) if thing else rng.choice(BEADS)
    t1, s1, t2, s2 = clothes or rng.choice(CLOTHES)
    stem = sent(d["stem"].format(who=who, thing=thing, adj=adj, p1=p1, p2=p2,
                                total=num(total), word=WORD[op], u=u, v=v,
                                a_name=a_name, b_name=b_name,
                                t1=t1, s1=s1, t2=t2, s2=s2))
    P = {"kind": "ineq_model_two", "style": d["style"], "op": op,
         "a": [ca.numerator, ca.denominator], "b": [cb.numerator, cb.denominator],
         "total": float(total), "u": u, "v": v}
    rationale = (f"Each of the {u} counts {dec(ca) if decimal else num(ca)} toward "
                 f"the total and each of the {v} counts "
                 f"{dec(cb) if decimal else num(cb)}, and the total is "
                 f"{WORD[op]} {num(total)}, so {key}.")
    ch, why, letter = text_choices(key, wrong, rng)
    return Item("ineq.model_two_var", "modelling a constraint", "easy", seed,
                stem, "mcq", E(0), letter, rationale, ch, why, list(ch), params=P)


# ----------------------------------------------------------- one variable

ONE_VAR_SHAPES = ["perimeter", "payback", "two_group", "race", "mean", "share"]

SHAPES_IN = ["rectangle", "banner", "garden plot", "photograph", "flag"]
UNITS = ["inches", "feet", "centimeters", "meters"]
SUBJECTS = ["history", "biology", "geography", "chemistry", "literature"]
TRAVEL = [("walk", "bus ride", "bus"), ("walk", "train ride", "train"),
          ("bike ride", "ferry ride", "ferry")]


def model_one_var(rng: random.Random, seed: int, *, shape=None, var=None,
                  **kw) -> Item:
    """One relation in one unknown, written from a described situation."""
    shape = shape or rng.choice(ONE_VAR_SHAPES)
    fn = {"perimeter": _perimeter, "payback": _payback, "two_group": _two_group,
          "race": _race, "mean": _mean, "share": _share}[shape]
    key, wrong, stem, P, rationale, difficulty = fn(rng, var, kw)
    P["kind"] = "ineq_model_one"
    P["shape"] = shape
    ch, why, letter = text_choices(key, wrong, rng)
    return Item("ineq.model_one_var", "modelling a constraint", difficulty, seed,
                sent(stem), "mcq", E(0), letter, rationale, ch, why, list(ch),
                params=P)


def _perimeter(rng, var, kw):
    var = var or "x"
    length = kw.get("length") or rng.choice([12, 15, 18, 20, 24, 30, 40, 45, 50, 60])
    total = kw.get("total") or rng.choice([90, 120, 150, 180, 210, 240, 300])
    op = kw.get("op", "<=")
    unit = kw.get("unit", "inches")
    thing = kw.get("thing", "rectangle")
    if total <= 2 * length:
        raise ItemError("no positive width fits inside that perimeter")
    lhs = side([(2, var)], 2 * length)
    key = rel(lhs, op, num(total))
    half = side([(2, var)], length)
    wrong = [Mis(_flip_reason(op), rel(lhs, FLIP[op], num(total))),
             Mis("counted the length once instead of twice when writing the "
                 "perimeter", rel(half, op, num(total))),
             Mis("counted the length once instead of twice and "
                 + _flip_reason(op), rel(half, FLIP[op], num(total))),
             Mis("used only the two widths and left the length out altogether",
                 rel(side([(2, var)]), op, num(total)))]
    stem = (f"The length of a {thing} is {num(length)} {unit} and the width is "
            f"{var} {unit}. The perimeter is {WORD[op]} {num(total)} {unit}. "
            f"Which inequality represents this situation?")
    P = {"op": op, "length": float(length), "total": float(total), "var": var}
    rationale = (f"The perimeter is two widths and two lengths, which is "
                 f"{lhs}, and that must be {WORD[op]} {num(total)}, so {key}.")
    return key, wrong, stem, P, rationale, "medium"


def _payback(rng, var, kw):
    var = var or "t"
    before = kw.get("before") or rng.randrange(2200, 6000, 2)
    after = kw.get("after") or rng.randrange(1000, 2800, 2)
    install = kw.get("install") or rng.randrange(8000, 40000, 500)
    if before <= after:
        raise ItemError("the new system has to be the cheaper one")
    thing = kw.get("thing", "a geothermal heating system")
    saving = f"({num(before)} {MINUS} {num(after)}){var}"
    key = rel(num(install), "<", saving)
    wrong = [Mis("compared the two the wrong way round, so the saving never "
                 "catches the installation cost up",
                 rel(num(install), ">", saving)),
             Mis("subtracted one year's old cost from the installation cost "
                 "instead of finding the yearly saving",
                 rel(f"{num(install)} {MINUS} {num(before)}", ">",
                     term(after, var))),
             Mis("divided the two annual costs instead of subtracting them",
                 rel(num(install), ">", f"({num(before)}/{num(after)}){var}")),
             Mis("used only the new annual cost as the yearly saving",
                 rel(num(install), "<", term(after, var)))]
    stem = (f"The average annual energy cost for a certain home is "
            f"{num(before)} dollars. The homeowner plans to spend "
            f"{num(install)} dollars to install {thing}. The homeowner "
            f"estimates that the average annual energy cost will then be "
            f"{num(after)} dollars. Which of the following inequalities can be "
            f"solved to find {var}, the number of years after installation at "
            f"which the total amount of energy cost savings will exceed the "
            f"installation cost?")
    P = {"before": float(before), "after": float(after),
         "install": float(install), "var": var}
    rationale = (f"Each year saves {num(before)} {MINUS} {num(after)} dollars, so "
                 f"{var} years save {saving}, and that has to pass the "
                 f"{num(install)} dollars it cost to install, so {key}.")
    return key, wrong, stem, P, rationale, "medium"


def _two_group(rng, var, kw):
    var = var or "x"
    n1 = kw.get("n1") or rng.randrange(60, 400, 10)
    n2 = kw.get("n2") or rng.randrange(60, 400, 10)
    gap = kw.get("gap") or rng.randint(1, 6)
    total = kw.get("total") or rng.randrange(2000, 9000, 20)
    op = kw.get("op", ">=")
    thing = kw.get("thing", "new uniforms")
    if n1 == n2:
        raise ItemError("two equal ticket counts collapse the distractors")
    up = f"{num(n1)}({var} + {num(gap)}) + {term(n2, var)}"
    down = f"{num(n1)}({var} {MINUS} {num(gap)}) + {term(n2, var)}"
    key = rel(up, op, num(total))
    wrong = [Mis(_flip_reason(op), rel(up, FLIP[op], num(total))),
             Mis("subtracted the difference from the earlier price instead of "
                 "adding it", rel(down, op, num(total))),
             Mis("subtracted the difference from the earlier price and "
                 + _flip_reason(op), rel(down, FLIP[op], num(total))),
             Mis("charged both groups the same price",
                 rel(side([(n1 + n2, var)]), op, num(total)))]
    stem = (f"A team hosting an event to raise money for {thing} plans to sell "
            f"at least {num(n1)} tickets before this event and at least "
            f"{num(n2)} tickets during this event to raise a total of "
            f"{WORD[op]} ${num(total)} from all tickets sold. The price of a "
            f"ticket during this event is ${num(gap)} less than the price of a "
            f"ticket before this event. Which inequality represents this "
            f"situation, where {var} is the price, in dollars, of a ticket sold "
            f"during this event?")
    P = {"n1": float(n1), "n2": float(n2), "gap": float(gap),
         "total": float(total), "op": op, "var": var}
    rationale = (f"A ticket before the event costs {num(gap)} dollars more than "
                 f"one during it, so it costs {var} + {num(gap)} dollars, and "
                 f"the two groups together raise {up}, which must be "
                 f"{WORD[op]} {num(total)}, so {key}.")
    return key, wrong, stem, P, rationale, "hard"


def _race(rng, var, kw):
    var = var or "w"
    walk = kw.get("walk") or rng.choice([12, 15, 18, 20, 24, 25, 30, 35])
    ride = kw.get("ride") or rng.choice([3, 4, 5, 6, 8, 10])
    every = kw.get("every") or rng.choice([15, 20, 30, 40, 45, 60])
    name = kw.get("name") or rng.choice(WHO)
    slow, fast, vehicle = kw.get("travel") or rng.choice(TRAVEL)
    if ride >= walk:
        raise ItemError("the ride has to be the quicker of the two")
    key = rel(side([(1, var)], ride), ">", num(walk))
    wrong = [Mis("subtracted the riding time from the wait instead of adding "
                 "it, and compared the two the wrong way round",
                 rel(side([(1, var)], -ride), "<", num(walk))),
             Mis("subtracted the riding time from the wait instead of adding it",
                 rel(side([(1, var)], -ride), ">", num(walk))),
             Mis("compared the two journeys the wrong way round, so the "
                 "inequality gives the values for which riding is faster",
                 rel(side([(1, var)], ride), "<", num(walk))),
             Mis("left the riding time out of the comparison altogether",
                 rel(var, ">", num(walk)))]
    stem = (f"{name}'s school is a {num(walk)}-minute {slow} or a {num(ride)}"
            f"-minute {fast} away from {name}'s house. The {vehicle} runs once "
            f"every {num(every)} minutes, and the number of minutes, {var}, "
            f"that {name} waits for the {vehicle} varies between 0 and "
            f"{num(every)}. Which of the following inequalities gives the "
            f"values of {var} for which it would be faster for {name} to "
            f"{slow} to school?")
    P = {"walk": float(walk), "ride": float(ride), "var": var}
    rationale = (f"Taking the {vehicle} costs the wait plus the ride, "
                 f"{side([(1, var)], ride)} minutes, and the {slow} is faster "
                 f"exactly when that is more than {num(walk)}, so {key}.")
    return key, wrong, stem, P, rationale, "hard"


def _mean(rng, var, kw):
    var = var or "G"
    scores = kw.get("scores") or [rng.randint(60, 99) for _ in range(3)]
    target = kw.get("target") or rng.choice([70, 75, 80, 85, 88, 90, 92])
    subject = kw.get("subject") or rng.choice(SUBJECTS)
    name = kw.get("name") or rng.choice(WHO)
    op = kw.get("op", ">=")
    n = len(scores) + 1
    listed = " + ".join(num(s) for s in scores)
    key = rel(f"({var} + {listed})/{num(n)}", op, num(target))
    wrong = [
        Mis(f"multiplied the unknown score by {num(n)} instead of dividing the "
            f"whole total by it",
            rel(f"{term(n, var)} + {listed}", op, num(n * target))),
        Mis("subtracted the three known scores from the target mean instead of "
            "averaging all four",
            rel(f"{num(target)} {MINUS} ({listed})", FLIP[op], term(n, var))),
        Mis("left the unknown score out of the sum being averaged",
            rel(f"({listed})/{num(n)}", op,
                f"{num(target)} {MINUS} {term(n, var)}")),
        Mis("divided by the number of known scores rather than by all four",
            rel(f"({var} + {listed})/{num(n - 1)}", op, num(target)))]
    spelled = ", ".join(num(s) for s in scores[:-1]) + f", and {num(scores[-1])}"
    stem = (f"{name} scored {spelled} on the first {_count(n - 1)} exams in "
            f"{subject} class. Solving which inequality gives the score, {var}, "
            f"on {name}'s {_ordinal(n)} exam that will result in a mean score on "
            f"all {_count(n)} exams of {WORD[op]} {num(target)} ?")
    P = {"scores": [float(s) for s in scores], "target": float(target),
         "op": op, "var": var}
    rationale = (f"The mean of the {_count(n)} scores is the sum divided by "
                 f"{num(n)}, and that mean has to be {WORD[op]} "
                 f"{num(target)}, so {key}.")
    return key, wrong, stem, P, rationale, "easy"


def _count(n: int) -> str:
    return {2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}.get(n, str(n))


def _ordinal(n: int) -> str:
    return {2: "second", 3: "third", 4: "fourth", 5: "fifth",
            6: "sixth"}.get(n, f"{n}th")


def _share(rng, var, kw):
    var = var or "p"
    half = kw.get("half") or rng.randrange(50, 400, 10)
    first = kw.get("first") or rng.randint(10, 60)
    pct = kw.get("pct") or rng.choice([10, 15, 20, 25, 30, 40])
    pics = kw.get("pics") or rng.choice([3, 4, 5, 6])
    total = 2 * half
    if first >= half:
        raise ItemError("more chose the first picture than there were people")
    rate = dec(Q(pct, 100))
    if len(rate.split(".")[-1]) < 2:
        rate += "0"
    cap = rel(var, "<=", num(half))
    key = f"{rel(side([(1, var)], first), '>', f'{rate}({num(total)})')}, where {cap}"
    wrong = [
        Mis("subtracted the first group's count from the total number of "
            "participants instead of adding it to the unknown",
            f"{rel(var, '>', f'{rate}({num(total)} {MINUS} {num(first)})')}, "
            f"where {cap}"),
        Mis("added the first group's count to the total number of participants "
            "instead of to the unknown",
            f"{rel(var, '>', f'{rate}({num(total)} + {num(first)})')}, "
            f"where {cap}"),
        Mis("subtracted the first group's count instead of adding it",
            f"{rel(side([(1, var)], -first), '>', f'{rate}({num(total)})')}, "
            f"where {cap}"),
        Mis("compared the two groups the wrong way round",
            f"{rel(side([(1, var)], first), '<', f'{rate}({num(total)})')}, "
            f"where {cap}")]
    stem = (f"A psychologist set up an experiment to study the tendency of a "
            f"person to select the first item when presented with a series of "
            f"items. In the experiment, {num(total)} people were presented with "
            f"a set of {_count(pics)} pictures arranged in random order. Each "
            f"person was asked to choose the most appealing picture. Of the "
            f"first {num(half)} participants, {num(first)} chose the first "
            f"picture in the set. Among the remaining {num(half)} participants, "
            f"{var} people chose the first picture in the set. If more than "
            f"{num(pct)}% of all participants chose the first picture in the "
            f"set, which of the following inequalities best describes the "
            f"possible values of {var} ?")
    P = {"half": float(half), "first": float(first), "pct": float(pct),
         "var": var}
    rationale = (f"Altogether {side([(1, var)], first)} people chose the first "
                 f"picture, and that has to be more than {num(pct)}% of the "
                 f"{num(total)} participants; only {num(half)} people are left "
                 f"to choose, so {key}.")
    return key, wrong, stem, P, rationale, "hard"


# ---------------------------------------------------------------- systems

SYSTEM_SHAPES = ["count_cost", "ratio", "staffing"]


def model_system(rng: random.Random, seed: int, *, shape=None, **kw) -> Item:
    """Two or four constraints at once, printed as a stacked system."""
    shape = shape or rng.choice(SYSTEM_SHAPES)
    fn = {"count_cost": _count_cost, "ratio": _ratio, "staffing": _staffing}[shape]
    key, wrong, stem, P, rationale, difficulty = fn(rng, kw)
    P["kind"] = "ineq_model_system"
    P["shape"] = shape
    ch, why, letter = text_choices(key, wrong, rng)
    return Item("ineq.model_system", "modelling a system of constraints",
                difficulty, seed, sent(stem), "mcq", E(0), letter, rationale,
                ch, why, list(ch), params=P)


def _join(rows: list[str]) -> str:
    return ", ".join(rows)


SUPPLY = [("workbooks", "sets of flash cards", "each", "per set"),
          ("notebooks", "boxes of pencils", "each", "per box"),
          ("posters", "packs of markers", "each", "per pack"),
          ("folders", "reams of paper", "each", "per ream")]


def _count_cost(rng, kw):
    u, v = kw.get("u", "x"), kw.get("v", "y")
    a = kw.get("a") or rng.randint(2, 12)
    b = kw.get("b") or rng.randint(2, 12)
    least = kw.get("least") or rng.randrange(10, 60, 5)
    budget = kw.get("budget") or rng.randrange(40, 400, 10)
    if a == b:
        raise ItemError("equal unit costs make the two rows interchangeable")
    if budget <= least * min(a, b):
        raise ItemError("no order meets the count without breaking the budget")
    it1, it2, per1, per2 = kw.get("items") or rng.choice(SUPPLY)
    count = rel(side([(1, u), (1, v)]), ">=", num(least))
    cost = rel(side([(a, u), (b, v)]), "<=", num(budget))
    key = _join([count, cost])
    wrong = [
        Mis("read the budget as an amount that has to be reached rather than a "
            "cap", _join([count, rel(side([(a, u), (b, v)]), ">=", num(budget))])),
        Mis("attached the count to the costs and the budget to the plain total",
            _join([rel(side([(a, u), (b, v)]), "<=", num(least)),
                   rel(side([(1, u), (1, v)]), ">=", num(budget))])),
        Mis("read the order minimum as a cap and the budget as a total to be "
            "reached",
            _join([rel(side([(1, u), (1, v)]), "<=", num(least)),
                   rel(side([(a, u), (b, v)]), ">=", num(budget))])),
        Mis("read the order minimum as a cap",
            _join([rel(side([(1, u), (1, v)]), "<=", num(least)), cost]))]
    stem = (f"An elementary school teacher is ordering {u} {it1} and {v} {it2} "
            f"for a math class. The teacher must order at least {num(least)} "
            f"items, but the total cost of the order must not be over "
            f"${num(budget)}. If the {it1} cost ${num(a)} {per1} and the {it2} "
            f"cost ${num(b)} {per2}, which of the following systems of "
            f"inequalities models this situation?")
    P = {"a": float(a), "b": float(b), "least": float(least),
         "budget": float(budget), "u": u, "v": v}
    rationale = (f"At least {num(least)} items is {count}, and a total cost that "
                 f"cannot go over ${num(budget)} is {cost}.")
    return key, wrong, stem, P, rationale, "easy"


RATIO_SCENES = {
    "bushes": dict(
        weights=False, ratio_op="<=",
        stem="A city employee will plant two types of bushes, {n1} and {n2}, in "
             "a park. There will be no more than {cap} total bushes planted, and "
             "the number of {n1} planted will be at most {k} times the number of "
             "{n2} planted. Which of the following systems of inequalities best "
             "represents this situation, where {u} is the number of {n1} that "
             "will be planted, and {v} is the number of {n2} that will be "
             "planted?",
        pairs=[("azaleas", "boxwoods"), ("hollies", "junipers"),
               ("lilacs", "hydrangeas"), ("roses", "camellias")]),
    "laundry": dict(
        weights=True, ratio_op=">=",
        stem="A laundry service is buying {n1} and {n2} from its supplier. The "
             "supplier will deliver no more than {cap} pounds in a shipment. "
             "Each container of {n1} weighs {w1} pounds, and each container of "
             "{n2} weighs {w2} pounds. The service wants to buy at least {kword} "
             "as many containers of {n1} as containers of {n2}. Let {u} "
             "represent the number of containers of {n1}, and let {v} represent "
             "the number of containers of {n2}, where {u} and {v} are "
             "nonnegative integers. Which of the following systems of "
             "inequalities best represents this situation?",
        pairs=[("detergent", "fabric softener"), ("bleach", "starch"),
               ("soap", "stain remover")]),
}

KWORD = {2: "twice", 3: "three times", 4: "four times", 5: "five times"}


def _ratio(rng, kw):
    scene = kw.get("scene") or rng.choice(list(RATIO_SCENES))
    d = RATIO_SCENES[scene]
    u, v = kw.get("u", "a"), kw.get("v", "b")
    k = kw.get("k") or rng.randint(2, 5)
    cap = kw.get("cap") or rng.randrange(60, 400, 4)
    ratio_op = kw.get("ratio_op") or d["ratio_op"]
    if d["weights"]:
        w1 = kw.get("w1") or Q(rng.randrange(200, 1200), 100)
        w2 = kw.get("w2") or Q(rng.randrange(200, 1200), 100)
        if w1 == w2:
            raise ItemError("equal container weights collapse the distractors")
        first = side([(w1, u), (w2, v)], decimal=True)
        doubled = side([(k * w1, u), (w2, v)], decimal=True)
    else:
        w1 = w2 = Q(1)
        first = side([(1, u), (1, v)])
        doubled = None
    n1, n2 = kw.get("names") or rng.choice(d["pairs"])

    row1 = rel(first, "<=", num(cap))
    row1_flip = rel(first, FLIP["<="], num(cap))
    row2 = rel(u, ratio_op, term(k, v))
    row2_other = rel(term(k, u), ratio_op, v)
    row2_turned = rel(term(k, u), FLIP[ratio_op], v)
    key = _join([row1, row2])
    if d["weights"]:
        wrong = [
            Mis(f"applied the {KWORD[k]}-as-many condition to the wrong "
                f"container", _join([row1, row2_other])),
            Mis(f"multiplied the weight of one container by {num(k)} instead of "
                f"its count", _join([rel(doubled, "<=", num(cap)), row2])),
            Mis(f"multiplied the weight by {num(k)} and applied the condition to "
                f"the wrong container",
                _join([rel(doubled, "<=", num(cap)), row2_other])),
            Mis("read the delivery limit as an amount that has to be reached",
                _join([row1_flip, row2]))]
    else:
        wrong = [
            Mis(f"read the cap as a total that has to be reached and put the "
                f"{num(k)} on the wrong side", _join([row1_flip, row2_turned])),
            Mis("read the cap as a total that has to be reached",
                _join([row1_flip, row2])),
            Mis(f"put the {num(k)} on the wrong side of the second condition",
                _join([row1, row2_turned])),
            Mis(f"applied the {KWORD[k]}-as-many condition to the wrong plant",
                _join([row1, row2_other]))]
    stem = d["stem"].format(n1=n1, n2=n2, cap=num(cap), k=num(k), u=u, v=v,
                            kword=KWORD[k],
                            w1=dec(w1) if d["weights"] else "",
                            w2=dec(w2) if d["weights"] else "")
    P = {"k": float(k), "cap": float(cap), "ratio_op": ratio_op,
         "w1": [w1.numerator, w1.denominator], "w2": [w2.numerator, w2.denominator],
         "u": u, "v": v, "weights": bool(d["weights"])}
    rationale = (f"The shipment is capped, which is {row1}, and "
                 f"{'at least' if ratio_op == '>=' else 'at most'} {KWORD[k]} as "
                 f"many {n1} as {n2} is {row2}.")
    return key, wrong, stem, P, rationale, "medium"


ROLES = [("junior directors", "senior directors"), ("apprentices", "engineers"),
         ("servers", "chefs"), ("guides", "drivers")]


def _staffing(rng, kw):
    u, v = kw.get("u", "x"), kw.get("v", "y")
    pay1 = kw.get("pay1") or rng.randrange(400, 900, 20)
    pay2 = kw.get("pay2") or rng.randrange(500, 1200, 20)
    staff = kw.get("staff") or rng.randint(6, 20)
    budget = kw.get("budget") or rng.randrange(5000, 20000, 100)
    min1 = kw.get("min1") or rng.randint(2, 5)
    min2 = kw.get("min2") or rng.randint(1, 3)
    if pay1 >= pay2:
        raise ItemError("the senior role has to be the better paid one")
    if budget <= staff * pay1:
        raise ItemError("the budget cannot cover the smallest possible team")
    r1, r2 = kw.get("roles") or rng.choice(ROLES)
    name = kw.get("name") or rng.choice(WHO)
    cost = side([(pay1, u), (pay2, v)])
    rows = [rel(cost, "<=", num(budget)),
            rel(side([(1, u), (1, v)]), ">=", num(staff)),
            rel(u, ">=", num(min1)), rel(v, ">=", num(min2))]
    key = _join(rows)
    flip_cost = rel(cost, ">=", num(budget))
    flip_count = rel(side([(1, u), (1, v)]), "<=", num(staff))
    cap1, cap2 = rel(u, "<=", num(min1)), rel(v, "<=", num(min2))
    wrong = [
        Mis("read the budget as an amount to be reached and the staff minimum "
            "as a cap", _join([flip_cost, flip_count, rows[2], rows[3]])),
        Mis("read the budget as an amount to be reached and both role minimums "
            "as caps", _join([flip_cost, rows[1], cap1, cap2])),
        Mis("read every one of the four conditions as a cap",
            _join([rows[0], flip_count, cap1, cap2])),
        Mis("read the staff minimum as a cap",
            _join([rows[0], flip_count, rows[2], rows[3]]))]
    stem = (f"{name} needs to hire at least {num(staff)} staff members for an "
            f"upcoming project. The staff members will be made up of {r1}, who "
            f"will be paid ${num(pay1)} per week, and {r2}, who will be paid "
            f"${num(pay2)} per week. The budget for paying the staff members is "
            f"no more than ${num(budget)} per week. {name} must hire at least "
            f"{num(min1)} {r1} and at least {num(min2)} "
            f"{r2[:-1] if min2 == 1 else r2}. Which of the following systems of "
            f"inequalities represents the conditions described if {u} is the "
            f"number of {r1} and {v} is the number of {r2}?")
    P = {"pay1": float(pay1), "pay2": float(pay2), "staff": float(staff),
         "budget": float(budget), "min1": float(min1), "min2": float(min2),
         "u": u, "v": v}
    rationale = (f"The weekly wage bill is capped at ${num(budget)}, the team "
                 f"has to reach {num(staff)} people, and each role has its own "
                 f"floor, which together give {key}.")
    return key, wrong, stem, P, rationale, "medium"
