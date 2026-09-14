"""Writing the system down rather than solving it.

Every option is a pair of equations, so the wrong answers are the pairings a
student actually writes: the two counts read down the columns instead of across
the rows, the money total attached to the count equation, the multiplier applied
to the wrong quantity. The mathematics is only the modelling, and `audit.py`
rebuilds each model from the story's numbers rather than from these strings.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text
from ..kit import MINUS, dec, money, num, opt_pair, pick, q, sent, solved, std

__all__ = ["model_purchase", "model_total_value", "model_relation"]


# --------------------------------------------------- two buyers, two goods

PURCHASE = [
    dict(key="shop", a="Hiro", b="Sofia", one="shirt", ones="shirts",
         two="pair of pants", twos="pairs of pants", twos_lead="pants",
         vx="x", vy="y",
         lead="{a} and {b} purchased {ones} and {twos_lead} from a store. The price of "
              "each {one} purchased was the same and the price of each {two} "
              "purchased was the same. {a} purchased {p1} {ones} and {q1} {twos} for "
              "{t1}, and {b} purchased {p2} {ones} and {q2} {twos} for {t2}.",
         ask="Which of the following systems of linear equations represents the "
             "situation, if {vx} represents the price, in dollars, of each {one} and "
             "{vy} represents the price, in dollars, of each {two}?",
         currency=True),
    dict(key="game", a="Angela", b="", one="coin", ones="coins", two="star",
         twos="stars", vx="c", vy="s",
         lead="{a} is playing a video game. In this game, players can score points "
              "only by collecting {ones} and {twos}. Each {one} is worth {vx} points, "
              "and each {two} is worth {vy} points. The first time she played, {a} "
              "scored {t1} points. She collected {p1} {ones} and {q1} {twos}. The "
              "second time she played, {a} scored {t2} points. She collected {p2} "
              "{ones} and {q2} {twos}.",
         ask="Which system of equations can be used to correctly determine the values "
             "of {vx} and {vy}?",
         currency=False),
    dict(key="market", a="Dana", b="Luis", one="melon", ones="melons", two="squash",
         twos="squashes", vx="m", vy="s",
         lead="{a} and {b} bought {ones} and {twos} at a farm stand. Every {one} cost "
              "the same amount and every {two} cost the same amount. {a} bought {p1} "
              "{ones} and {q1} {twos} for {t1}, and {b} bought {p2} {ones} and {q2} "
              "{twos} for {t2}.",
         ask="Which of the following systems of equations represents this situation, "
             "if {vx} is the price, in dollars, of each {one} and {vy} is the price, "
             "in dollars, of each {two}?",
         currency=True),
    dict(key="lab", a="A technician", b="", one="small vial", ones="small vials",
         two="large vial", twos="large vials", vx="p", vy="q",
         lead="A technician filled {ones} and {twos} from a tank on two days. Each "
              "{one} holds {vx} milliliters and each {two} holds {vy} milliliters. On "
              "the first day the technician filled {p1} {ones} and {q1} {twos}, using "
              "{t1} milliliters. On the second day the technician filled {p2} {ones} "
              "and {q2} {twos}, using {t2} milliliters.",
         ask="Which system of equations can be solved to find {vx} and {vy}?",
         currency=False),
]


def model_purchase(rng: random.Random, seed: int, *, scene=None, p1=None, q1=None,
                   t1=None, p2=None, q2=None, t2=None, wrongs=None) -> Item:
    """Two buyers, two goods, two totals: which pair of equations says that?"""
    d = PURCHASE[rng.randrange(len(PURCHASE))] if scene is None else \
        next(s for s in PURCHASE if s["key"] == scene)
    p1 = int(p1 if p1 is not None else rng.randint(2, 9))
    q1 = int(q1 if q1 is not None else rng.randint(2, 9))
    p2 = int(p2 if p2 is not None else rng.randint(2, 9))
    q2 = int(q2 if q2 is not None else rng.randint(2, 9))
    if p1 * q2 == p2 * q1:
        raise ItemError("the two purchases say the same thing")
    if len({p1, q1, p2, q2}) < 4:
        raise ItemError("a repeated count would make two options read the same")
    t1 = int(t1 if t1 is not None else p1 * rng.randint(4, 30) + q1 * rng.randint(4, 30))
    t2 = int(t2 if t2 is not None else p2 * rng.randint(4, 30) + q2 * rng.randint(4, 30))
    if t1 == t2:
        raise ItemError("equal totals would make two options read the same")
    vx, vy = d["vx"], d["vy"]
    shown = (lambda v: money(v, 0)) if d["currency"] else num
    lead = d["lead"].format(a=d["a"], b=d["b"], one=d["one"], ones=d["ones"],
                            two=d["two"], twos=d["twos"],
                            twos_lead=d.get("twos_lead", d["twos"]), vx=vx, vy=vy,
                            p1=p1, q1=q1, p2=p2, q2=q2,
                            t1=shown(t1), t2=shown(t2))
    stem = sent(lead + " " + d["ask"].format(one=d["one"], two=d["two"], vx=vx, vy=vy))

    def sys_(A, B, C, D, E_, F):
        return opt_pair(std(A, B, C, vx, vy), std(D, E_, F, vx, vy))

    key = sys_(p1, q1, t1, p2, q2, t2)
    pool = {
        "transpose": Mis("read the two counts down the columns instead of across the "
                         "rows, pairing both first-item counts in one equation",
                         sys_(p1, p2, t1, q1, q2, t2)),
        "swap_totals": Mis("gave each purchase the other purchase's total",
                           sys_(p1, q1, t2, p2, q2, t1)),
        "transpose_swap": Mis("read the counts down the columns and gave each "
                              "equation the other total",
                              sys_(p1, p2, t2, q1, q2, t1)),
        "swap_within": Mis("attached each count to the other item's price",
                           sys_(q1, p1, t1, q2, p2, t2)),
        "total_as_coef1": Mis("put the total where the second count belongs and the "
                              "second count on the right",
                              sys_(p1, t1, q1, p2, t2, q2)),
        "total_as_coef2": Mis("put the total where the first count belongs and the "
                              "second count on the right",
                              sys_(t1, p1, q1, t2, p2, q2)),
    }
    P = {"kind": "sys_model_purchase", "scene": d["key"], "p1": p1, "q1": q1,
         "t1": t1, "p2": p2, "q2": q2, "t2": t2, "vx": vx, "vy": vy}
    rationale = sent(f"Each purchase gives one equation: {p1} at {vx} each and {q1} "
                     f"at {vy} each come to {num(t1)}, and {p2} and {q2} come to "
                     f"{num(t2)}.")
    ch, why, letter = assemble_text(key, pick(pool, wrongs), rng)
    return Item("sys.model_purchase", "modelling two purchases", "easy", seed, stem,
                "mcq", E(1), letter, rationale, ch, why, ch, params=P)


# ------------------------------------------- a count total and a value total

TOTALS = [
    dict(key="zoo", vx="s", vy="p", one="standard ticket", two="premium ticket",
         lead="A petting zoo sells two types of tickets. The standard ticket, for "
              "admission only, costs {p}. The premium ticket, which includes "
              "admission and food to give to the animals, costs {q}. One Saturday, "
              "the petting zoo sold a total of {n} tickets and collected a total of "
              "{t} from ticket sales.",
         ask="Which of the following systems of equations can be used to find the "
             "number of standard tickets, {vx}, and premium tickets, {vy}, sold on "
             "that Saturday?", currency=True, cents=False),
    dict(key="outfits", vx="b", vy="g", one="outfit for boys", two="outfit for girls",
         lead="A dance teacher ordered outfits for students for a dance recital. "
              "Outfits for boys cost {p}, and outfits for girls cost {q}. The dance "
              "teacher ordered a total of {n} outfits and spent {t}.",
         ask="If {vx} represents the number of outfits the dance teacher ordered for "
             "boys and {vy} represents the number of outfits the dance teacher "
             "ordered for girls, which of the following systems of equations can be "
             "solved to find {vx} and {vy}?", currency=True, cents=False),
    dict(key="airline", vx="x", vy="y", one="discount ticket", two="full ticket",
         lead="A discount airline sells a certain number of tickets, {vx}, for a "
              "flight for {p} each. It sells the number of remaining tickets, {vy}, "
              "for {q} each. For a particular flight, the airline sold {n} tickets "
              "and collected a total of {t} from the sale of those tickets.",
         ask="Which system of equations represents this relationship between {vx} and "
             "{vy}?", currency=True, cents=False),
    dict(key="cinema", vx="f", vy="r", one="full-price ticket",
         two="reduced-price ticket",
         lead="A movie theater charges {p} for each full-price ticket and {q} for "
              "each reduced-price ticket. For one movie showing, the theater sold a "
              "total of {n} full-price and reduced-price tickets for {t}.",
         ask="Which of the following systems of equations could be used to determine "
             "the number of full-price tickets, {vx}, and the number of "
             "reduced-price tickets, {vy}, sold?", currency=True, cents=True),
    dict(key="bakery", vx="m", vy="c", one="muffin", two="cookie",
         lead="A bakery sells muffins for {p} each and cookies for {q} each. On one "
              "morning the bakery sold {n} muffins and cookies altogether and took "
              "in {t}.",
         ask="Which of the following systems of equations can be used to find the "
             "number of muffins, {vx}, and the number of cookies, {vy}, sold that "
             "morning?", currency=True, cents=True),
]


def model_total_value(rng: random.Random, seed: int, *, scene=None, n=None, p=None,
                      qq=None, t=None, order="count_first", wrongs=None,
                      product=False) -> Item:
    """x + y = a count, p·x + q·y = a money total: which pair says that?"""
    d = TOTALS[rng.randrange(len(TOTALS))] if scene is None else \
        next(s for s in TOTALS if s["key"] == scene)
    n = int(n if n is not None else rng.randint(20, 400))
    p = q(p) if p is not None else Q(rng.randint(2, 30))
    qq = q(qq) if qq is not None else Q(rng.choice([i for i in range(2, 40)]))
    if p == qq:
        raise ItemError("two equal prices make the swapped option identical")
    t = int(t) if t is not None else int(p * rng.randint(1, n - 1)
                                         + qq * (n - rng.randint(1, n - 1)))
    if t == n:
        raise ItemError("equal totals would make two options read the same")
    vx, vy = d["vx"], d["vy"]
    cents = d["cents"]
    # the source prints $11 and $8.25 side by side: cents appear only when the
    # price has them
    show = (lambda v: money(v, 0 if q(v).denominator == 1 else 2)) \
        if d["currency"] else num
    style = "dec" if cents else "frac"
    stem = sent(d["lead"].format(p=show(p), q=show(qq), n=num(n), t=show(t),
                                 vx=vx, vy=vy)
                + " " + d["ask"].format(vx=vx, vy=vy))

    count = lambda total: std(1, 1, total, vx, vy)                      # noqa: E731
    value = lambda a, b, total: std(a, b, total, vx, vy, style=style)    # noqa: E731

    def build(first_is_count, a, b, ct, vt, swapped=None):
        if swapped is None:
            v = value(a, b, vt)
        else:                       # the same swap, printed second unknown first
            v = std(swapped[0], swapped[1], vt, vy, vx, style=style)
        c = count(ct)
        return opt_pair(c, v) if first_is_count else opt_pair(v, c)

    first_count = order == "count_first"
    key = build(first_count, p, qq, n, t)
    prod = f"{num(n)}({num(t)})"
    pool = {
        "swap_prices": Mis("swapped the two prices, so each unknown carries the "
                           "other one's price",
                           build(first_count, qq, p, n, t)),
        "swap_vars": Mis("swapped the two prices and wrote the second unknown first",
                         build(first_count, None, None, n, t,
                               swapped=(p, qq))),
        "swap_vars_totals": Mis("swapped the two prices and also swapped the two "
                                "totals",
                                build(first_count, None, None, t, n,
                                      swapped=(p, qq))),
        "swap_totals": Mis("used the money total as the number sold and the number "
                           "sold as the money total", build(first_count, p, qq, t, n)),
        "swap_prices_totals": Mis("swapped the two prices and also swapped the two "
                                  "totals", build(first_count, qq, p, t, n)),
        "reorder_swap": Mis("gave each equation the other equation's total",
                            build(not first_count, p, qq, t, n)),
        "swap_prices_reorder": Mis("swapped the two prices and gave each equation the "
                                   "other equation's total",
                                   build(not first_count, qq, p, t, n)),
        "product_total": Mis("multiplied the money total by the number sold instead "
                             "of leaving it as the total",
                             opt_pair(count(n),
                                      f"{_lhs(p, qq, vx, vy, style)} = {prod}")),
        "product_and_count": Mis("multiplied the money total by the number sold and "
                                 "used that money total as the number sold",
                                 opt_pair(count(t),
                                          f"{_lhs(p, qq, vx, vy, style)} = {prod}")),
        "revenues_equal": Mis("set the two ticket revenues equal and used the number "
                              "sold as the coefficient of each unknown",
                              opt_pair(f"{_term(p, vx, style)} = {_term(qq, vy, style)}",
                                       std(n, n, t, vx, vy))),
    }
    P = {"kind": "sys_model_total", "scene": d["key"], "n": n, "p": _p(p),
         "q": _p(qq), "t": t, "order": order, "vx": vx, "vy": vy,
         "style": style}
    rationale = sent(f"Counting the items gives {count(n)}, and adding up what they "
                     f"cost gives {value(p, qq, t)}, because {vx} of them cost "
                     f"{show(p)} each and {vy} of them cost {show(qq)} each.")
    ch, why, letter = assemble_text(key, pick(pool, wrongs), rng)
    return Item("sys.model_total_value", "modelling a count and a total", "easy",
                seed, stem, "mcq", E(1), letter, rationale, ch, why, ch, params=P)


def _lhs(a, b, vx, vy, style) -> str:
    return std(a, b, 0, vx, vy, style=style).rsplit(" = ", 1)[0]


def _term(a, v, style) -> str:
    from ..kit import coef
    return coef(a, v, style)


# ------------------------------------------ a multiple and a sum or a offset

def model_relation(rng: random.Random, seed: int, *, shape=None, k=None, total=None,
                   add=None, gap=None, scene=None, wrongs=None) -> Item:
    """One quantity is a multiple of the other; write the pair of equations."""
    shape = shape or rng.choice(["times_total", "sum_twice"])
    if shape == "times_total":
        d = TIMES[rng.randrange(len(TIMES))] if scene is None else \
            next(s for s in TIMES if s["key"] == scene)
        k = int(k if k is not None else rng.randint(2, 9))
        total = int(total if total is not None else rng.randint(10, 400))
        if k == total:
            raise ItemError("the multiplier and the total would make two options match")
        vx, vy = d["vx"], d["vy"]
        stem = sent(d["lead"].format(vx=vx, vy=vy, k=k, t=d["show"](total))
                    + " " + d["ask"])
        pair = lambda a, b: opt_pair(f"{a}", f"{b}")                     # noqa: E731
        first = lambda m, w: f"{vx} = {_scaled(m, vy)}" if w else \
            f"{vy} = {_scaled(m, vx)}"                                   # noqa: E731
        second = lambda tt: std(1, 1, tt, vx, vy)                        # noqa: E731
        key = pair(first(k, True), second(total))
        pool = {
            "reverse": Mis("made the smaller quantity the multiple of the larger one",
                           pair(first(k, False), second(total))),
            "swap_numbers": Mis("used the total as the multiplier and the multiplier "
                                "as the total", pair(first(total, True), second(k))),
            "reverse_swap": Mis("reversed the multiple and also swapped the "
                                "multiplier with the total",
                                pair(first(total, False), second(k))),
            "sum_as_multiple": Mis("wrote the total as a multiple instead of a sum",
                                   pair(first(k, True), f"{vx} = {_scaled(total, vy)}")),
        }
        P = {"kind": "sys_model_relation", "shape": shape, "k": k, "total": total,
             "scene": d["key"], "add": 0, "gap": 0, "vx": vx, "vy": vy}
        rationale = sent(f"'{k} times as many' gives {first(k, True)}, and 'together' "
                         f"gives {second(total)}.")
    else:
        add = int(add if add is not None else rng.randint(2, 20))
        k = int(k if k is not None else rng.randint(2, 6))
        gap = int(gap if gap is not None else rng.randint(2, 20))
        if add == gap or k in (add, gap):
            raise ItemError("a repeated number would make two options read the same")
        stem = sent(f"The sum of a number x and {add} is {_times(k)} as large as a "
                    f"number y. The number y is {gap} less than the number x. Which "
                    f"system of equations describes this situation?")
        left = f"x + {num(add)} = {_scaled(k, 'y')}"
        bracket = f"{_scaled(k, f'(x + {num(add)})')} = y"
        right = f"y = x {MINUS} {num(gap)}"
        flipped = f"y = {num(gap)} {MINUS} x"
        key = opt_pair(left, right)
        pool = {
            "reverse_diff": Mis("subtracted the number from the gap instead of the "
                                "gap from the number", opt_pair(left, flipped)),
            "multiply_left": Mis("multiplied the sum by the multiplier instead of the "
                                 "other number", opt_pair(bracket, right)),
            "both": Mis("multiplied the wrong side and subtracted the wrong way round",
                        opt_pair(bracket, flipped)),
        }
        P = {"kind": "sys_model_relation", "shape": shape, "k": k, "total": 0,
             "scene": "", "add": add, "gap": gap, "vx": "x", "vy": "y"}
        rationale = sent(f"'{_times(k)} as large as y' multiplies y, not the sum, so "
                         f"the first equation is {left}; '{gap} less than x' gives "
                         f"{right}.")
    ch, why, letter = assemble_text(key, pick(pool, wrongs), rng)
    return Item("sys.model_relation", "modelling a stated relation", "easy", seed,
                stem, "mcq", E(1), letter, rationale, ch, why, ch, params=P)


TIMES = [
    dict(key="dollars", vx="c", vy="m", show=lambda v: money(v, 2),
         lead="Connor has {vx} dollars and Maria has {vy} dollars. Connor has {k} "
              "times as many dollars as Maria, and together they have a total of {t}.",
         ask="Which system of equations represents this situation?"),
    dict(key="stamps", vx="j", vy="p", show=num,
         lead="Jae has {vx} stamps and Priya has {vy} stamps. Jae has {k} times as "
              "many stamps as Priya, and together they have {t} stamps.",
         ask="Which system of equations represents this situation?"),
    dict(key="laps", vx="r", vy="w", show=num,
         lead="A runner completed {vx} laps and a walker completed {vy} laps. The "
              "runner completed {k} times as many laps as the walker, and together "
              "they completed {t} laps.",
         ask="Which system of equations represents this situation?"),
]


def _scaled(k, v) -> str:
    k = q(k)
    return v if k == 1 else f"{num(k)}{v}"


def _times(k: int) -> str:
    return {2: "twice", 3: "three times", 4: "four times", 5: "five times",
            6: "six times"}.get(int(k), f"{int(k)} times")


def _p(v) -> list:
    v = q(v)
    return [v.numerator, v.denominator]
