"""Reading a modelled inequality back into English.

Two of the official items give the inequality and ask what one piece of it
means: a coefficient times its variable, or an ordered pair of values that
satisfies it. Nothing is solved -- what is tested is whether a term is read as
a total or as a unit price, and whether the pair is read in the order the stem
declared. Both mistakes have the same shape, which is why they share a
template: the student keeps the arithmetic and loses the labels.
"""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, ItemError, Mis
from .kit import FLIP, LONG, Q, money, num, rel, sent, side, text_choices

__all__ = ["interpret"]

SHAPES = ["term", "pair"]


# ------------------------------------------------- what one term stands for

BUYERS = ["Anthony", "Rosalind", "Deshawn", "Marta", "Yusuf", "Hana"]
GOODS = [("small cheese pizzas", "large cheese pizzas", "a team dinner"),
         ("paperback books", "hardcover books", "a classroom library"),
         ("small candles", "large candles", "a craft fair"),
         ("ground-floor tickets", "balcony tickets", "a school trip")]


def _term(rng, kw):
    u, v = kw.get("u", "x"), kw.get("v", "y")
    a = Q(kw.get("a") or rng.randrange(3, 30))
    b = Q(kw.get("b") or rng.randrange(3, 30))
    total = Q(kw.get("total") or rng.randrange(50, 400, 5))
    if a == b:
        raise ItemError("two equal prices make the two readings the same")
    who = kw.get("who") or rng.choice(BUYERS)
    small, large, event = kw.get("goods") or rng.choice(GOODS)
    piece = kw.get("piece", "second")
    coef, other, item, alt = ((b, a, large, small) if piece == "second"
                              else (a, b, small, large))
    var = v if piece == "second" else u
    shown = f"{num(coef)}{var}"
    key = f"The total amount, in dollars, {who} will spend on {item}"
    wrong = [
        Mis(f"read {shown} as the price of one {_one(item)} rather than as "
            f"that price times the number bought",
            f"The amount, in dollars, {who} will spend on each {_one(item)}"),
        Mis(f"read {shown} as a price per item and attached it to the other "
            f"kind of item",
            f"The amount, in dollars, {who} will spend on each {_one(alt)}"),
        Mis("attached the term to the other kind of item",
            f"The total amount, in dollars, {who} will spend on {alt}"),
        Mis("read the whole left side rather than the one term asked about",
            f"The total amount, in dollars, {who} will spend on {small} and "
            f"{large} together"),
        Mis(f"read {shown} as a number of items rather than an amount of money",
            f"The number of {item} {who} will buy")]
    displayed = rel(side([(a, u), (b, v)]), "<=", num(total))
    stem = (f"{displayed}\n{who} will spend at most {money(total, cents=False)} "
            f"to purchase {u} {small} and {v} {large} for {event}. The given "
            f"inequality represents this situation. Which of the following is "
            f"the best interpretation of {shown} in this context?")
    P = {"shape": "term", "a": float(a), "b": float(b), "piece": piece,
         "who": who, "small": small, "large": large}
    rationale = (f"Each {_one(item)} costs {money(coef, cents=False)}, and "
                 f"{var} is how many are bought, so {shown} is what all of the "
                 f"{item} come to, not the price of one.")
    return key, wrong, stem, P, rationale, "hard"


def _one(plural: str) -> str:
    """The singular of an option's noun phrase: 'large cheese pizzas' -> one."""
    if plural.endswith("ies"):
        return plural[:-3] + "y"
    if plural.endswith("es") and plural.endswith(("ches", "shes", "xes")):
        return plural[:-2]
    return plural[:-1] if plural.endswith("s") else plural


# -------------------------------------------- what an ordered pair stands for

FIGURES = [("rectangle", "length", "width", "perimeter"),
           ("garden plot", "length", "width", "perimeter"),
           ("banner", "length", "width", "perimeter")]


def _pair(rng, kw):
    u, v = kw.get("u", "ℓ"), kw.get("v", "w")
    first = Q(kw.get("first") or rng.randint(4, 20))
    second = Q(kw.get("second") or rng.randint(2, 18))
    cap = Q(kw.get("cap") or rng.randrange(20, 90))
    op = kw.get("op", "<=")
    if first <= second:
        raise ItemError("a rectangle is named length first, so it is the longer")
    if 2 * (first + second) > cap and op == "<=":
        raise ItemError("the pair given does not satisfy the inequality")
    if 2 * (first + second) == cap:
        # on the boundary both readings of the relation are true, so the
        # option that turns it round is a second correct answer
        raise ItemError("a pair on the boundary makes the reversed statement "
                        "true as well")
    thing, n1, n2, measure = kw.get("figure") or rng.choice(FIGURES)
    displayed = rel(side([(2, u), (2, v)]), op, num(cap))
    word = LONG[op]

    def say(a, b, relation) -> str:
        return (f"If the {thing} has {n1} {num(a)} and {n2} {num(b)}, its "
                f"{measure} is {LONG[relation]} {num(cap)}.")

    key = say(first, second, op)
    wrong = [
        Mis(f"read the pair in the other order, although the stem names {u} "
            f"first", say(second, first, op)),
        Mis("read the pair in the other order and turned the relation round",
            say(second, first, FLIP[op])),
        Mis("turned the relation round, so the cap became a floor",
            say(first, second, FLIP[op])),
        Mis(f"read the {measure} as exactly {num(cap)} rather than as a limit "
            f"it may not pass",
            f"If the {thing} has {n1} {num(first)} and {n2} {num(second)}, its "
            f"{measure} is {num(cap)}.")]
    stem = (f"{displayed}\nA {thing} has {n1} {u} and {n2} {v}. The inequality "
            f"gives the possible values of {u} and {v} for which the {measure} "
            f"of this {thing} is {word} {num(cap)}. Which statement is the "
            f"best interpretation of ({u}, {v}) = ({num(first)}, "
            f"{num(second)}) in this context?")
    P = {"shape": "pair", "first": float(first), "second": float(second),
         "cap": float(cap), "op": op, "thing": thing, "n1": n1, "n2": n2,
         "measure": measure}
    rationale = (f"The stem names {u} first, so {num(first)} is the {n1} and "
                 f"{num(second)} is the {n2}; the inequality then says the "
                 f"{measure}, {num(2 * (first + second))}, is {word} "
                 f"{num(cap)}.")
    return key, wrong, stem, P, rationale, "easy"


def interpret(rng: random.Random, seed: int, *, shape=None, **kw) -> Item:
    """What one piece of a modelled inequality means, in words."""
    shape = shape or rng.choice(SHAPES)
    key, wrong, stem, P, rationale, tier = {"term": _term, "pair": _pair}[shape](
        rng, kw)
    P["kind"] = "ineq_interpret"
    ch, why, letter = text_choices(key, wrong, rng)
    return Item("ineq.interpret", "reading a modelled inequality back into "
                "words", tier, seed, sent(stem), "mcq", E(0), letter, rationale,
                ch, why, list(ch), params=P)
