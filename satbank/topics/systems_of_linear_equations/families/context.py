"""Systems that arrive as a story.

Four shapes carry every word problem in the source set: a count total beside a
money total, one purchase priced at two shops, one quantity stated as a multiple
of another, and two legs of a journey at two speeds. The unknowns are named in
the sentence, and the answer is a number rather than a pair of equations.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis, unit_word
from ..kit import (MINUS, choices, coef, dec, griddable, gridin_pool, money, num,
                   pick, q, sent)

__all__ = ["purchase_solve", "relation_pair", "two_rates"]


# ------------------------------------ a count total beside a value total

COUNT_VALUE = [
    dict(key="books", ask="first", spr=False,
         text="An online bookstore sells novels and magazines. Each novel sells for "
              "{p}, and each magazine sells for {q}. If Sadie purchased a total of "
              "{n} novels and magazines that have a combined selling price of {t}, "
              "how many novels did she purchase?", currency=True, cents=False,
         per="price", each="kind of book", kinds="kinds of book"),
    dict(key="tents", ask="first", spr=False,
         text="A group of {t} people went on an overnight camping trip, taking {n} "
              "tents with them. Some of the tents held {p} people each, and the rest "
              "held {q} people each. Assuming all the tents were filled to capacity "
              "and every person got to sleep in a tent, exactly how many of the tents "
              "were {p}-person tents?", currency=False, cents=False,
         per="tent capacity", each="size of tent", kinds="sizes of tent"),
    dict(key="trivia", ask="first", spr=True,
         text="The score on a trivia game is obtained by subtracting the number of "
              "incorrect answers from twice the number of correct answers. If a "
              "player answered {n} questions and obtained a score of {t}, how many "
              "questions did the player answer correctly?", currency=False,
         cents=False, fixed=True, per="point value",
         each="kind of answer", kinds="kinds of answer"),
    dict(key="cinema", ask="spend_first", spr=True,
         text="A movie theater sells two types of tickets, adult tickets for {p} and "
              "child tickets for {q}. If the theater sold {n} tickets for a total of "
              "{t}, how much, in dollars, was spent on adult tickets?",
         currency=True, cents=False, per="price", each="kind of ticket", kinds="kinds of ticket"),
    dict(key="coins", ask="second", spr=False,
         text="A jar holds only nickels and dimes. Each nickel is worth {p} cents and "
              "each dime is worth {q} cents. The jar holds {n} coins worth {t} cents "
              "altogether. How many dimes are in the jar?", currency=False,
         cents=False, per="coin value", each="kind of coin", kinds="kinds of coin"),
]

TWO_STORES = [
    dict(key="berries", one="raspberries", two="blackberries", unit="pint",
         units="pints", a="Store A", b="Store B",
         text="{a} sells {one} for {p1} per {unit} and {two} for {q1} per {unit}. "
              "{b} sells {one} for {p2} per {unit} and {two} for {q2} per {unit}. A "
              "certain purchase of {one} and {two} would cost {t1} at {a} or {t2} at "
              "{b}. How many {units} of {two} are in this purchase?"),
    dict(key="grains", one="rice", two="lentils", unit="pound", units="pounds",
         a="Market A", b="Market B",
         text="{a} sells {one} for {p1} per {unit} and {two} for {q1} per {unit}. "
              "{b} sells {one} for {p2} per {unit} and {two} for {q2} per {unit}. A "
              "certain order of {one} and {two} would cost {t1} at {a} or {t2} at "
              "{b}. How many {units} of {two} are in this order?"),
]


def purchase_solve(rng: random.Random, seed: int, *, shape=None, scene=None, n=None,
                   p=None, qq=None, t=None, p1=None, q1=None, t1=None, p2=None,
                   q2=None, t2=None, ask=None, value_style=None, wrongs=None) -> Item:
    """A story that is a system; the answer is one of the two counts, or a cost."""
    shape = shape or rng.choice(["count_value", "count_value", "two_stores"])
    if shape == "count_value":
        d = COUNT_VALUE[rng.randrange(len(COUNT_VALUE))] if scene is None else \
            next(s for s in COUNT_VALUE if s["key"] == scene)
        ask = ask or d["ask"]
        n = Q(int(n) if n is not None else rng.randint(10, 80))
        if d.get("fixed"):
            p, qq = Q(2), Q(-1)
        else:
            p = q(p) if p is not None else Q(rng.randint(2, 20))
            qq = q(qq) if qq is not None else Q(rng.randint(1, 20))
        if p == qq:
            raise ItemError("two equal prices leave nothing to solve")
        first = Q(int(rng.randint(1, int(n) - 1))) if t is None else None
        t = q(t) if t is not None else p * first + qq * (n - first)
        x0 = (t - qq * n) / (p - qq)
        y0 = n - x0
        if x0.denominator != 1 or x0 <= 0 or y0 <= 0:
            raise ItemError("the story would need a fraction of an item")
        key = {"first": x0, "second": y0, "spend_first": p * x0}[ask]
        show = (lambda v: money(v, 2 if d["cents"] else 0)) if d["currency"] else num
        wording = d["text"]
        if d["key"] == "coins" and (p, qq) != (Q(5), Q(10)):
            wording = ("A jar holds only bronze tokens and silver tokens. Each bronze "
                       "token is worth {p} {p_unit} and each silver token is worth "
                       "{q} {q_unit}. The jar holds {n} tokens worth {t} cents "
                       "altogether. How many silver tokens are in the jar?")
        stem = sent(wording.format(p=show(p), q=show(qq), n=num(n), t=show(t),
                                   p_unit=unit_word(p, "cent", "cents"),
                                   q_unit=unit_word(qq, "cent", "cents")))
        per, each, kinds = d["per"], d["each"], d["kinds"]
        pool = {
            "half_count": Mis(f"split the total evenly between the two {kinds}",
                              n / 2),
            "price1": Mis(f"read the first {per} out of the question instead of "
                          "counting", p),
            "price2": Mis(f"read the second {per} out of the question instead of "
                          "counting", qq),
            "total_over_price1": Mis(f"divided the grand total by the first {per} "
                                     "instead of solving the system", t / p),
            "total_over_price2": Mis(f"divided the grand total by the second {per} "
                                     "instead of solving the system",
                                     t / qq if qq else None),
            "other": Mis(f"counted the other {each} instead",
                         y0 if ask == "first" else x0),
            "off_by_one_up": Mis(f"assumed every one was the same {each}, then "
                                 "slipped by one when dividing the shortfall",
                                 key + 1),
            "off_by_one_down": Mis(f"assumed every one was the same {each} and slipped "
                                   "by one the other way", key - 1),
            "no_price": Mis(f"subtracted the two totals without using the {per}s",
                            t - n),
        }
        P = {"kind": "sys_purchase_solve", "shape": shape, "scene": d["key"],
             "n": _p(n), "p": _p(p), "q": _p(qq), "t": _p(t), "ask": ask}
        rationale = sent(f"Writing the second count as {num(n)} \u2212 x and putting "
                         f"it into the total equation leaves "
                         f"{coef(p - qq, 'x')} = {num(t - qq * n)}, so x = "
                         f"{num(x0)} and y = {num(y0)}."
                         + (f" The first kind then accounts for {num(p)}({num(x0)}) "
                            f"= {num(p * x0)}." if ask == "spend_first" else ""))
        spr = d["spr"]
    else:
        d = TWO_STORES[rng.randrange(len(TWO_STORES))] if scene is None else \
            next(s for s in TWO_STORES if s["key"] == scene)
        p1 = q(p1) if p1 is not None else Q(rng.randint(2, 18), 2)
        q1 = q(q1) if q1 is not None else Q(rng.randint(2, 18), 2)
        p2 = q(p2) if p2 is not None else Q(rng.randint(2, 18), 2)
        q2 = q(q2) if q2 is not None else Q(rng.randint(2, 18), 2)
        det = p1 * q2 - q1 * p2
        if det == 0:
            raise ItemError("the two shops price the purchase identically")
        rr = Q(rng.randint(1, 12)) if t1 is None else None
        bb = Q(rng.randint(1, 12)) if t1 is None else None
        t1 = q(t1) if t1 is not None else p1 * rr + q1 * bb
        t2 = q(t2) if t2 is not None else p2 * rr + q2 * bb
        x0 = (t1 * q2 - q1 * t2) / det
        y0 = (p1 * t2 - t1 * p2) / det
        if x0.denominator != 1 or y0.denominator != 1 or x0 <= 0 or y0 <= 0:
            raise ItemError("the purchase would need a fraction of a pint")
        if x0 == y0:
            raise ItemError("equal counts make the first distractor the key")
        key = y0
        stem = sent(d["text"].format(a=d["a"], b=d["b"], one=d["one"], two=d["two"],
                                     unit=d["unit"], units=d["units"],
                                     p1=money(p1), q1=money(q1), p2=money(p2),
                                     q2=money(q2), t1=money(t1), t2=money(t2)))
        pool = {
            "other": Mis(f"counted the {d['one']} instead", x0),
            "price_q2": Mis("read a price per " + d["unit"] + " as a number of "
                            + d["units"], q2 if q2.denominator == 1 else None),
            "cross_divide": Mis("divided one shop's total by the other shop's price "
                                "per " + d["unit"],
                                t2 / p1 if p1 and (t2 / p1).denominator == 1
                                else None),
            "total_over_q1": Mis("divided the first shop's total by its own price per "
                                 + d["unit"],
                                 t1 / q1 if q1 and (t1 / q1).denominator == 1
                                 else None),
            "sum": Mis("added the two counts instead of reporting one of them",
                       x0 + y0),
            "price_q1": Mis("read the first shop's price per " + d["unit"] + " for "
                            + d["two"] + " as a number of " + d["units"],
                            q1 if q1.denominator == 1 else None),
            "price_p1": Mis("read the first shop's price per " + d["unit"] + " for "
                            + d["one"] + " as a number of " + d["units"],
                            p1 if p1.denominator == 1 else None),
            "price_p2": Mis("read the second shop's price per " + d["unit"] + " for "
                            + d["one"] + " as a number of " + d["units"],
                            p2 if p2.denominator == 1 else None),
            "diff_totals": Mis("subtracted the two shop totals and read the "
                               "difference as a count", abs(t1 - t2)),
        }
        P = {"kind": "sys_purchase_solve", "shape": shape, "scene": d["key"],
             "p1": _p(p1), "q1": _p(q1), "t1": _p(t1), "p2": _p(p2), "q2": _p(q2),
             "t2": _p(t2)}
        rationale = sent(f"The two shops give {dec(p1)}r + {dec(q1)}b = {dec(t1)} "
                         f"and {dec(p2)}r + {dec(q2)}b = {dec(t2)}; multiplying the "
                         f"first by {dec(p2 / p1)} and subtracting removes r and "
                         f"leaves b = {num(y0)}.")
        spr = False

    keyx = E(key)
    if spr:
        if not griddable(key):
            raise ItemError("this answer could not be entered in the grid")
        # trivia never prints its −1
        grid, drop = pool, ("price2", "total_over_price2") if d.get("fixed") else ()
        if ask == "spend_first":
            # a dollar answer: the adult count is not "the other kind", ticket
            # counts (n/2, t/p, t/q) and dollars less tickets are not dollars,
            # a slip of one ticket is not a slip of one dollar, and the child
            # price is no adult spending; stopping at the count is the slip
            grid = {"count": Mis(f"found the number of the first {each} and stopped "
                                 f"before multiplying by its {per}", x0), **pool}
            drop = ("other", "half_count", "off_by_one_up", "off_by_one_down",
                    "total_over_price1", "total_over_price2", "no_price", "price2")
        return Item("sys.purchase_solve", "a system from a purchase", "medium", seed,
                    stem, "spr", keyx, keyx.gridin(), rationale, params=P)
    fmt_value = None
    ch, tex, why, letter = choices(keyx, pick(pool, wrongs), rng, fmt_value=fmt_value)
    return Item("sys.purchase_solve", "a system from a purchase", "medium", seed,
                stem, "mcq", keyx, letter, rationale, ch, why, tex, params=P)


# ------------------------------- one quantity as a multiple of the other

RELATIONS = [
    dict(key="ballot", link="difference", ask="second", spr=False,
         text="A proposal for a new library was included on an election ballot. A "
              "radio show stated that {k} times as many people voted in favor of the "
              "proposal as people who voted against it. A social media post reported "
              "that {g} more people voted in favor of the proposal than voted against "
              "it. Based on these data, how many people voted against the proposal?"),
    dict(key="wire", link="sum", ask="first", spr=True,
         text="A piece of wire with a length of {g} inches is cut into two parts. One "
              "part has a length of x inches, and the other part has a length of y "
              "inches. The value of x is {d} more than {k} times the value of y. What "
              "is the value of x?"),
    dict(key="shelf", link="sum", ask="first", spr=True,
         text="A shelf holds {g} books altogether, x of them hardcover and y of them "
              "paperback. The value of x is {d} more than {k} times the value of y. "
              "What is the value of x?"),
    dict(key="survey", link="difference", ask="second", spr=False,
         text="In a survey, {k} times as many people chose the first option as chose "
              "the second option, and {g} more people chose the first option than "
              "chose the second. How many people chose the second option?"),
]


def relation_pair(rng: random.Random, seed: int, *, scene=None, k=None, d=None,
                  g=None, wrongs=None) -> Item:
    """A is m times B (plus an offset); their sum or their difference is given."""
    s = RELATIONS[rng.randrange(len(RELATIONS))] if scene is None else \
        next(x for x in RELATIONS if x["key"] == scene)
    k = Q(int(k) if k is not None else rng.randint(2, 6))
    d = Q(int(d) if d is not None else (0 if s["link"] == "difference"
                                        else rng.randint(1, 12)))
    if s["link"] == "difference":
        if k < 3:
            raise ItemError("with this multiplier the answer is the stated difference")
        g = Q(int(g) if g is not None else rng.choice([1500, 2400, 15000, 240, 36]))
        second = (g - d) / (k - 1)
    else:
        g = Q(int(g) if g is not None else rng.randint(12, 90))
        second = (g - d) / (k + 1)
    first = k * second + d
    if second.denominator != 1 or second <= 0 or first <= 0 or first == second:
        raise ItemError("the story would need a fraction of a person")
    key = first if s["ask"] == "first" else second
    stem = sent(s["text"].format(k=num(k), d=num(d), g=num(g)))
    pool = {
        "gap": Mis("reported the stated difference itself", g),
        "other": Mis("counted the other quantity instead",
                     second if s["ask"] == "first" else first),
        "mult_gap": Mis("multiplied the stated difference by the multiplier instead "
                        "of dividing by one less than it", k * g),
        "half_gap": Mis("halved the stated difference whatever the multiplier is",
                        g / 2),
        "over_k": Mis("divided by the multiplier instead of by one less than it",
                      g / k),
    }
    P = {"kind": "sys_relation_pair", "scene": s["key"], "link": s["link"],
         "ask": s["ask"], "k": _p(k), "d": _p(d), "g": _p(g)}
    rationale = sent(f"Writing the first as {num(k)} times the second"
                     + (f" plus {num(d)}" if d else "")
                     + (" and subtracting" if s["link"] == "difference" else
                        " and adding")
                     + f" leaves {num(k - 1 if s['link'] == 'difference' else k + 1)} "
                       f"times the second equal to {num(g - d)}, so the second is "
                       f"{num(second)} and the first is {num(first)}.")
    keyx = E(key)
    if s["spr"]:
        if not griddable(key):
            raise ItemError("this answer could not be entered in the grid")
        return Item("sys.relation_pair", "a multiple and a total", "hard", seed, stem,
                    "spr", keyx, keyx.gridin(), rationale, params=P,
                    # the rest of the pool is worded for a stated difference
                    spr_mistakes=gridin_pool(keyx, pool, () if s["link"] == "difference"
                                             else ("gap", "mult_gap", "half_gap",
                                                   "over_k")))
    ch, tex, why, letter = choices(keyx, pick(pool, wrongs), rng)
    return Item("sys.relation_pair", "a multiple and a total", "medium", seed, stem,
                "mcq", keyx, letter, rationale, ch, why, tex, params=P)


# ------------------------------------------- two legs at two speeds

RATES = [
    dict(key="morgan", who="Morgan", slow="ran", fast="biked", u1="r", u2="b",
         text="During a month, {who} {slow} {u1} miles at {v1} miles per hour and "
              "{fast} {u2} miles at {v2} miles per hour. {pron} {slow} and {fast} a "
              "total of {m} miles that month, and {pron_l} {fast} for {k} as many "
              "hours as {pron_l} {slow}. What is the total number of miles that {who} "
              "{fast} during the month?", pron="She", pron_l="she"),
    dict(key="ferry", who="a ranger", slow="paddled", fast="motored", u1="p",
         u2="s",
         text="In one season, {who} {slow} {u1} miles at {v1} miles per hour and "
              "{fast} {u2} miles at {v2} miles per hour. The ranger {slow} and "
              "{fast} a total of {m} miles that season, and {pron_l} {fast} for {k} "
              "as many hours as {pron_l} {slow}. What is the total number of miles "
              "that the ranger {fast} that season?", pron="The ranger",
         pron_l="the ranger"),
    dict(key="delivery", who="a courier", slow="walked", fast="cycled", u1="w",
         u2="c",
         text="In one week, {who} {slow} {u1} miles at {v1} miles per hour and {fast} "
              "{u2} miles at {v2} miles per hour. The courier {slow} and {fast} a "
              "total of {m} miles that week, and {pron_l} {fast} for {k} as many hours "
              "as {pron_l} {slow}. What is the total number of miles that the courier "
              "{fast} that week?", pron="The courier", pron_l="the courier"),
]


TOTAL_MILES = [60, 72, 80, 90, 100, 110, 120, 125, 130, 140, 150, 160, 168, 175,
               180, 190, 200, 210, 220, 225, 240, 250, 260, 270, 280, 288, 300,
               320, 330, 350, 360, 375, 400, 420, 440, 450, 480, 500, 540, 600]


def two_rates(rng: random.Random, seed: int, *, scene=None, v1=None, v2=None, m=None,
              k=None, wrongs=None) -> Item:
    """One total distance and a ratio of times: how far on the faster leg?"""
    s = RATES[rng.randrange(len(RATES))] if scene is None else \
        next(x for x in RATES if x["key"] == scene)
    v1 = Q(int(v1) if v1 is not None else rng.choice([2, 3, 4, 5, 6, 8, 10, 12]))
    v2 = Q(int(v2) if v2 is not None
           else rng.choice([9, 10, 12, 14, 15, 16, 18, 20, 21, 24, 25, 30]))
    m = Q(int(m) if m is not None else rng.choice(TOTAL_MILES))
    k = Q(int(k) if k is not None else rng.randint(2, 5))
    if v2 <= v1:
        raise ItemError("the second leg has to be the faster one")
    ratio = k * v2 / v1                 # fast miles per slow mile
    slow = m / (1 + ratio)
    fast = m - slow
    if slow.denominator != 1 or fast.denominator != 1 or slow <= 0:
        raise ItemError("the two legs would not be whole numbers of miles")
    key = fast
    stem = sent(s["text"].format(who=s["who"], slow=s["slow"], fast=s["fast"],
                                 u1=s["u1"], u2=s["u2"], v1=num(v1), v2=num(v2),
                                 m=num(m), k=_times(k), pron=s["pron"],
                                 pron_l=s["pron_l"]))
    pool = {
        "k_times_slow": Mis("multiplied the slower leg by the number of times without "
                            "converting hours into miles", k * slow),
        "half": Mis("split the total distance evenly between the two legs", m / 2),
        "total_minus": Mis("took the slower leg times the number of times away from "
                           "the total", m - k * slow),
        "other": Mis("reported the slower leg instead", slow),
        "speed_share": Mis("split the total in the ratio of the two speeds",
                           m * v2 / (v1 + v2)),
    }
    P = {"kind": "sys_two_rates", "scene": s["key"], "v1": _p(v1), "v2": _p(v2),
         "m": _p(m), "k": _p(k)}
    rationale = sent(f"An hour of the faster leg covers {num(v2 / v1)} times as far, "
                     f"so {_times(k)} the hours means {num(ratio)} times the miles; "
                     f"{num(1 + ratio)} times the slower leg is {num(m)}, so the "
                     f"slower leg is {num(slow)} miles and the faster leg is "
                     f"{num(fast)} miles.")
    keyx = E(key)
    ch, tex, why, letter = choices(keyx, pick(pool, wrongs), rng)
    return Item("sys.two_rates", "two legs at two speeds", "hard", seed, stem, "mcq",
                keyx, letter, rationale, ch, why, tex, params=P)


def _times(k) -> str:
    return {2: "twice", 3: "three times", 4: "four times"}.get(int(q(k)),
                                                               f"{num(k)} times")


def _p(v) -> list:
    v = q(v)
    return [v.numerator, v.denominator]
