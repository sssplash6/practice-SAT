"""One variable is known; find the other.

Fifteen source items come down to substituting and solving, and the wrong
answers cluster in three places: a number the stem already states handed back
as the answer, the total divided by a coefficient without the other term being
taken off first, and the other term taken off but never divided. Those three
are what the distractor pool is built from, and they are the same three
whether the equation is printed for the student or has to be written down
first.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import Item, ItemError, Mis
from ..common import choose, dec, ex, numtext, q, std_text

__all__ = ["substitute", "context_substitute", "mixture_solve"]


def _article(text: str) -> str:
    """'a 973-square-inch' but 'an 840-square-inch': the sound, not the letter."""
    lead = text.lstrip("-\N{MINUS SIGN}").replace(",", "")
    return "an" if lead[:1] == "8" or lead[:2] == "11" or lead[:2] == "18" else "a"


def _named(key, mistakes, whole=False):
    """Drop the candidates that coincide with the key, repeat, or cannot be one.

    `whole=True` throws away a candidate that is not a whole number: when the
    answer counts boxes, a wrong option of 16.75 boxes is not a mistake any
    student makes, it is an option nobody would read twice.
    """
    seen = {q(key)}
    out = []
    for reason, value in mistakes:
        if value is None:
            continue
        v = q(value)
        if v in seen or (whole and v.denominator != 1):
            continue
        seen.add(v)
        out.append(Mis(reason, ex(v)))
    return out


SUBST = [
    # 0 -- shipping small and large boxes (1.3)
    dict(xv="a", yv="b", solve="y", fmt="mcq", display=True, head="{a}{xv} + {b}{yv} = {c}",
         alo=2, ahi=9, glo=2, ghi=9, tlo=2, thi=9, places=None, whole=True,
         stem="A shipping company charged a customer ${c} to ship some small boxes and "
              "some large boxes. The equation above represents the relationship between "
              "a, the number of small boxes, and b, the number of large boxes, the "
              "customer had shipped. If the customer had {given} small boxes shipped, "
              "how many large boxes were shipped?",
         x1="small boxes", y1="large boxes",
         why="The {given} small boxes account for ${part} of the ${c} charge, so the "
             "large boxes account for the ${left} left, at ${b} each."),
    # 1 -- pieces of music in a practice session (1.6)
    dict(form="solved", xv="x", yv="y", solve="y", fmt="mcq", display=False,
         alo=Q(1, 10), ahi=Q(9, 10), glo=10, ghi=90, gstep=10, places=1, short=True,
         whole=True,
         stem="The equation y = {a}x models the relationship between the number of "
              "different pieces of music a certain pianist practices, y, during an "
              "x-minute practice session. How many pieces did the pianist practice if "
              "the session lasted {given} minutes?",
         why="The equation counts {a} of a piece for every minute at the piano, so a "
             "session of {given} minutes carries {given} times {a}."),
    # 2 -- sweaters and shirts (1.14)
    dict(xv="x", yv="y", solve="y", fmt="mcq", display=False, inline=True, order="desc",
         alo=10, ahi=60, glo=2, ghi=9, tlo=2, thi=9, places=None, step=10, whole=True,
         stem="The equation {eq} represents the number of sweaters, x, and number of "
              "shirts, y, that Yesenia purchased for ${c}. If Yesenia purchased {given} "
              "sweaters, how many shirts did she purchase?",
         x1="sweaters", y1="shirts",
         why="The {given} sweaters cost ${part} of the ${c}, leaving ${left} for the "
             "shirts at ${b} each."),
    # 3 -- the side lengths of a parallelogram (1.22)
    dict(xv="a", yv="b", solve="y", fmt="spr", display=False, inline=True,
         reversed=True, a=2, b=2, glo=3, ghi=40, tlo=3, thi=40, places=None, whole=True,
         stem="The equation {eq} gives the relationship between the side lengths a and "
              "b of a certain parallelogram. If a = {given}, what is the value of b?",
         why="A parallelogram has two sides of each length, so the two sides of length "
             "{given} use up {part} of the {c}, leaving {left} for the other pair."),
    # 4 -- the perimeter of a rug (1.29)
    dict(xv="x", yv="y", solve="x", fmt="spr", display=False, inline=True,
         reversed=True, a=2, b=2, glo=3, ghi=40, tlo=3, thi=40, places=None, whole=True,
         stem="The equation {eq} gives the perimeter of a rectangular rug that has "
              "length x, in feet, and width y, in feet. The width of the rug is {given} "
              "feet. What is the length, in feet, of the rug?",
         why="The two widths of {given} feet take up {part} feet of the {c}-foot "
             "perimeter, and the remaining {left} feet is shared by the two lengths."),
    # 5 -- two kinds of tree in a preserve (1.32)
    dict(xv="x", yv="y", solve="y", fmt="mcq", display=True, head="{xv} + {yv} = {c}",
         a=1, b=1, glo=40, ghi=900, tlo=40, thi=900, places=None, whole=True,
         decoy="acres",
         stem="The given equation relates the total number of maple trees, x, and the "
              "total number of birch trees, y, planted in a {acres}-acre forest "
              "preserve. If {given} maple trees were planted in the forest preserve, "
              "how many birch trees were planted in the forest preserve?",
         x1="maple trees", y1="birch trees",
         why="The two kinds of tree come to {c} altogether, so the birch trees make up "
             "whatever the {given} maple trees do not."),
    # 6 -- birds and reptiles at a pet care business (2.15)
    dict(xv="b", yv="r", solve="x", fmt="mcq", display=True,
         head="{a}{xv} + {b}{yv} = {c}", places=1, short=True, alo=Q(15, 10),
         ahi=Q(80, 10), glo=2, ghi=20, tlo=0, thi=20, whole=True,
         stem="The given equation describes the relationship between the number of "
              "birds, b, and the number of reptiles, r, that can be cared for at a pet "
              "care business on a given day. If the business cares for {given} reptiles "
              "on a given day, how many birds can it care for on this day?",
         x1="birds", y1="reptiles",
         why="The {given} reptiles use up {part} of the {c}, so only {left} is left for "
             "the birds at {a} each."),
    # 7 -- blue and green tiles (2.22)
    dict(xv="g", yv="b", solve="x", fmt="spr", display=False, inline=True,
         a=7, b=7, glo=20, ghi=90, tlo=20, thi=90, places=None, whole=True,
         stem="The equation {eq} represents the number of blue tiles, b, and the number "
              "of green tiles, g, an artist needs for {an} {c}-square-inch tile project. "
              "The artist needs {given} blue tiles for the project. How many green "
              "tiles does he need?",
         x1="green tiles", y1="blue tiles",
         why="Each tile covers {a} square inches, so the {given} blue tiles cover "
             "{part} and the green tiles have to cover the remaining {left}."),
]


def substitute(rng: random.Random, seed: int, *, ctx=None, a=None, b=None, given=None,
               other=None, acres=None) -> Item:
    """A printed equation in two variables, one value given, the other asked for."""
    i = rng.randrange(len(SUBST)) if ctx is None else ctx
    d = SUBST[i]
    scale = 10 ** (d["places"] or 0)
    # `places` fixes how many decimals the numbers are drawn on; the printed form
    # is the shortest exact decimal, so 5 stays 5 where 2.5 stays 2.5
    places = None
    style = "dec" if d["places"] else "frac"

    def draw(lo, hi, step=1):
        if d["places"]:
            return Q(rng.randrange(int(lo * scale), int(hi * scale) + 1), scale)
        return q(rng.randrange(int(lo), int(hi) + 1, step))

    A = q(a) if a is not None else q(d.get("a") or draw(d["alo"], d["ahi"],
                                                        d.get("step", 1)))
    B = q(b) if b is not None else q(d.get("b") or draw(d["alo"], d["ahi"],
                                                        d.get("step", 1)))
    if d.get("form") == "solved":
        B = q(1)
    if A <= 0 or B <= 0:
        raise ItemError("both coefficients count something, so both are positive")
    if a is None and b is None and d.get("order") == "desc" and A < B:
        A, B = B, A
    solve = d["solve"]
    # the two whole-number counts the situation actually holds
    g = q(given) if given is not None else q(rng.randrange(int(d["glo"]),
                                                           int(d["ghi"]) + 1,
                                                           d.get("gstep", 1)))
    o = q(other) if other is not None else q(rng.randint(int(d.get("tlo", 2)),
                                                         int(d.get("thi", 9))))
    if d.get("form") == "solved":
        key = A * g
        C = key
        eq = f"y = {numtext(A, style, places)}x"
    else:
        # `g` is the count that is stated, `o` the one that is asked for
        if solve == "y":
            C = A * g + B * o
            coef_known, coef_ask = A, B
        else:
            C = B * g + A * o
            coef_known, coef_ask = B, A
        key = o
        eq = (f"{numtext(C)} = " + std_text(A, B, C, d["xv"], d["yv"], style,
                                            places).split(" = ")[0]
              if d.get("reversed") else
              std_text(A, B, C, d["xv"], d["yv"], style, places))
    if key < 0:
        raise ItemError("the count asked for cannot be negative")

    head = d.get("head", "")
    acres = acres if acres is not None else rng.randint(5, 40)
    ct = numtext(C, style, places)
    stem = d["stem"].format(a=numtext(A, style, places), b=numtext(B, style, places),
                            c=ct, given=numtext(g), eq=eq, an=_article(ct),
                            acres=acres)
    if d.get("display"):
        stem = head.format(a=numtext(A, style, places), b=numtext(B, style, places),
                           c=numtext(C, style, places), xv=d["xv"], yv=d["yv"]) \
               + "\n" + stem
    keyx = ex(key)

    if d.get("form") == "solved":
        mistakes = _named(key, [
            ("gave the length of the session rather than the number of pieces", g),
            ("inverted the rate, treating it as minutes per piece", 1 / A),
            ("divided by the rate instead of multiplying by it", g / A),
            ("read the rate as one piece for the whole session", 1)], d.get("whole"))
        why = d["why"].format(a=numtext(A, style, places), given=numtext(g))
    else:
        part = coef_known * g
        left = C - part
        mistakes = _named(key, [
            (f"gave the number of {d.get('x1' if solve == 'y' else 'y1', 'items')} the "
             f"question already states", g),
            ("divided the total by what one of them accounts for without first taking "
             "off the other kind", C / coef_ask),
            ("took the other kind off the total but never divided by what one of them "
             "accounts for", left),
            ("subtracted the number of the other kind rather than what they account "
             "for", (C - g) / coef_ask),
            ("gave the total itself", C),
            ("divided by the other kind's coefficient", left / coef_known),
            ("gave what one of them accounts for rather than how many there are",
             coef_ask if coef_ask != 1 else None),
            ("gave what one of the other kind accounts for",
             coef_known if coef_known != 1 else None),
            ("gave a number the passage mentions that the equation does not involve",
             acres if d.get("decoy") == "acres" else None),
            ("halved the total, as though the two kinds came in equal numbers",
             C / 2)], d.get("whole"))
        why = d["why"].format(a=numtext(A, style, places),
                              b=numtext(coef_ask, style, places),
                              c=numtext(C, style, places), given=numtext(g),
                              part=numtext(part, style, places),
                              left=numtext(left, style, places))

    P = {"kind": "le2_substitute", "form": d.get("form", "standard"), "solve": solve,
         "a": [A.numerator, A.denominator], "b": [B.numerator, B.denominator],
         "c": [q(C).numerator, q(C).denominator], "given": [g.numerator, g.denominator]}
    if d["fmt"] == "spr":
        if not keyx.is_rational or len(keyx.gridin()) > 6:
            raise ItemError("the answer does not fit a grid-in")
        return Item("le2.substitute", "substituting into a two-variable equation",
                    "easy", seed, stem, "spr", keyx, keyx.gridin(), why, params=P)
    if len(mistakes) < 3:
        raise ItemError("these numbers leave too few of the named mistakes to choose "
                        "three distinct wrong answers from")
    choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True,
                                             fillers="shift")
    return Item("le2.substitute", "substituting into a two-variable equation", "easy",
                seed, stem, "mcq", keyx, letter, why, choices, reasons, latex, params=P)


# ------------------------------------- the equation has to be written first

CONTEXT = [
    # 0 -- boxes of two weights (1.18)
    dict(shape="counts", fmt="mcq", alo=2, ahi=12, glo=4, ghi=30, tlo=4, thi=30,
         whole=True, stem="A shipment consists of {a}-pound boxes and {b}-pound boxes with a total "
              "weight of {c} pounds. There are {given} {b}-pound boxes in the shipment. "
              "How many {a}-pound boxes are in the shipment?",
         unit="pound", asked="{a}-pound boxes", known="{b}-pound boxes",
         why="The {given} boxes of {b} pounds weigh {part} pounds, so the {a}-pound "
             "boxes make up the remaining {left} pounds."),
    # 1 -- two kinds of snail (1.27)
    dict(shape="counts", fmt="mcq", alo=2, ahi=14, glo=2, ghi=12, tlo=2, thi=12,
         money=True, whole=True,
         stem="Naomi bought both rabbit snails and nerite snails for a total of ${c}. "
              "Each rabbit snail costs ${a} and each nerite snail costs ${b}. If Naomi "
              "bought {given} nerite snails, how many rabbit snails did she buy?",
         asked="rabbit snails", known="nerite snails",
         why="The {given} nerite snails cost ${part}, leaving ${left} of the ${c} for "
             "the rabbit snails at ${a} each."),
    # 2 -- two legs of a drive (2.2)
    dict(shape="counts", fmt="spr", alo=40, ahi=75, glo=1, ghi=4, tlo=1, thi=5, step=5,
         stem="On a {c}-mile trip, Cameron drove at an average speed of {a} miles per "
              "hour for the first x hours. He then completed the trip, driving at an "
              "average speed of {b} miles per hour for the remaining y hours. If x = "
              "{given}, what is the value of y ?",
         swap=True, asked="hours at the second speed", known="hours at the first speed",
         why="{given} hours at {a} miles per hour covers {part} miles, so {left} miles "
             "of the {c} are left to drive at {b} miles per hour."),
    # 3 -- calories from two activities, quoted per half hour (2.4)
    dict(shape="counts", fmt="mcq", per30=True, alo=50, ahi=300, glo=1, ghi=4,
         tlo=2, thi=10, step=25,
         stem="In an article about exercise, it is estimated that a 160-pound adult "
              "uses {ah} calories for every 30 minutes of hiking and {bh} calories for "
              "every 30 minutes of bicycling. An adult who weighs 160 pounds has "
              "completed {given} {hr} of bicycling. Based on the article, how many "
              "hours should the adult hike to use a total of {c} calories from "
              "bicycling and hiking?",
         asked="hours of hiking", known="hours of bicycling",
         why="{bh} calories every half hour is {b} an hour, so {given} {hr} of "
             "bicycling uses {part}; the remaining {left} calories have to come from "
             "hiking at {a} an hour."),
    # 4 -- one quantity a multiple of the other (1.26)
    dict(shape="ratio", fmt="mcq", money=True,
         stem="Davio bought some potatoes and celery. The potatoes cost ${a} per pound, "
              "and the celery cost ${b} per pound. If Davio spent ${c} in total and "
              "bought {times} as many pounds of celery as pounds of potatoes, how many "
              "pounds of celery did Davio buy?",
         why="Every pound of potatoes comes with {pounds} pounds of celery, so each "
             "pound of potatoes costs ${block} once the celery with it is counted; "
             "${c} buys {base} of those."),
    # 5 -- the calcium in one banana (2.19)
    dict(shape="per_unit", fmt="mcq",
         stem="A batch of banana milkshakes consists of {n1} cups of ice cream and {n2} "
              "bananas and has {c} milligrams (mg) of calcium. There is {u1} mg of "
              "calcium in 1 cup of the ice cream used to make this batch of "
              "milkshakes. How much calcium, in mg, is in 1 banana?",
         why="The {n1} cups of ice cream carry {part} mg between them, so the {n2} "
             "bananas carry the remaining {left} mg."),
]


def context_substitute(rng: random.Random, seed: int, *, ctx=None, a=None, b=None,
                       given=None, other=None, times=None, n1=None, n2=None,
                       u1=None, u2=None) -> Item:
    """No equation is printed: the student writes one from the words and solves it."""
    i = rng.randrange(len(CONTEXT)) if ctx is None else ctx
    d = CONTEXT[i]
    shape = d["shape"]

    if shape == "counts":
        step = d.get("step", 1)
        A = q(a) if a is not None else q(rng.randrange(int(d["alo"]), int(d["ahi"]) + 1,
                                                       step))
        B = q(b) if b is not None else q(rng.randrange(int(d["alo"]), int(d["ahi"]) + 1,
                                                       step))
        if A == B or A <= 0 or B <= 0:
            raise ItemError("the two rates must differ")
        if d.get("money") and A < B:
            A, B = B, A
        g = q(given) if given is not None else q(rng.randint(int(d["glo"]),
                                                             int(d["ghi"])))
        o = q(other) if other is not None else q(rng.randint(int(d["tlo"]),
                                                             int(d["thi"])))
        ah, bh = A, B
        if d.get("per30"):
            ah, bh = A, B
            A, B = 2 * A, 2 * B
        C = A * o + B * g
        key = o
        part, left = B * g, C - B * g
        hr = "hour" if g == 1 else "hours"
        # some contexts name the given quantity first, so the two rates change places
        sa, sb = (B, A) if d.get("swap") else (A, B)
        stem = d["stem"].format(a=numtext(sa), b=numtext(sb), c=numtext(C),
                                given=numtext(g), ah=numtext(ah), bh=numtext(bh), hr=hr)
        why = d["why"].format(a=numtext(sa), b=numtext(sb), c=numtext(C),
                              given=numtext(g), part=numtext(part), left=numtext(left),
                              ah=numtext(ah), bh=numtext(bh), hr=hr)
        known = d["known"].format(a=numtext(A), b=numtext(B))
        mistakes = [(f"gave the number of {known} the question already states", g),
                    ("gave what one of the kind asked about is worth rather than how "
                     "many there are", A),
                    ("gave what one of the other kind is worth", B),
                    ("took the other kind off the total but never divided", left),
                    ("subtracted the number of the other kind rather than what they "
                     "account for", (C - g) / A),
                    ("divided the total by the rate asked about without taking off the "
                     "other kind", C / A),
                    ("gave what the other kind accounts for in total rather than how "
                     "many of the kind asked about there are", B * g),
                    ("took the number of the other kind off the total instead of what "
                     "they account for, and never divided", C - g)]
        if d.get("per30"):
            mistakes = [("used the half-hour figures as if they were hourly rates",
                         (C - bh * g) / ah),
                        ("divided the whole total by the half-hour hiking figure, "
                         "leaving the bicycling out", C / ah),
                        ("left the bicycling out of the total", C / A),
                        ("used the half-hour figure for the hiking only",
                         (C - B * g) / ah)] + mistakes
        P = {"kind": "le2_context", "shape": shape, "a": [A.numerator, A.denominator],
             "b": [B.numerator, B.denominator], "c": [C.numerator, C.denominator],
             "given": [g.numerator, g.denominator]}
    elif shape == "ratio":
        k = q(times) if times is not None else q(rng.randint(2, 4))
        A = q(a) if a is not None else Q(rng.randrange(25, 400), 100)
        B = q(b) if b is not None else Q(rng.randrange(25, 400), 100)
        base = q(other) if other is not None else q(rng.randint(2, 9))
        block = A + k * B
        C = base * block
        key = k * base
        if k <= 1 or A <= 0 or B <= 0:
            raise ItemError("the celery has to outnumber the potatoes")
        words = {2: "twice", 3: "three times", 4: "four times"}[int(k)]
        stem = d["stem"].format(a=dec(A, 2), b=dec(B, 2), c=dec(C, 2), times=words)
        why = d["why"].format(times=words, pounds=numtext(k), block=dec(block, 2),
                              c=dec(C, 2), base=numtext(base))
        mistakes = [("gave the pounds of potatoes rather than the pounds of celery",
                     base),
                    ("gave what one pound of potatoes costs once the celery bought with "
                     "it is counted", block),
                    ("divided the total by the two prices added, as though equal "
                     "amounts of each were bought", C / (A + B)),
                    ("divided the total by the price of celery alone", C / B),
                    ("divided the total by the price of potatoes alone, leaving the "
                     "celery out", C / A),
                    ("priced every pound at the celery's price", k * C / (B * (1 + k)))]
        P = {"kind": "le2_context", "shape": shape, "a": [A.numerator, A.denominator],
             "b": [B.numerator, B.denominator], "c": [C.numerator, C.denominator],
             "k": [k.numerator, k.denominator]}
    else:
        N1 = int(n1 if n1 is not None else rng.randint(2, 8))
        N2 = int(n2 if n2 is not None else rng.randint(2, 6))
        U1 = q(u1) if u1 is not None else q(rng.randrange(60, 400))
        U2 = q(u2) if u2 is not None else q(rng.randrange(2, 90))
        C = N1 * U1 + N2 * U2
        key = U2
        part, left = N1 * U1, N2 * U2
        stem = d["stem"].format(n1=N1, n2=N2, c=numtext(C), u1=numtext(U1))
        why = d["why"].format(n1=N1, n2=N2, part=numtext(part), left=numtext(left))
        mistakes = [("did not divide by the number of bananas", left),
                    ("gave the calcium the ice cream contributes", part),
                    ("subtracted the calcium in one cup rather than in all of them",
                     (C - U1) / N2),
                    ("gave the calcium in one cup of ice cream", U1),
                    ("divided the whole total by the number of bananas", C / N2)]
        P = {"kind": "le2_context", "shape": shape, "n1": N1, "n2": N2,
             "u1": [U1.numerator, U1.denominator],
             "c": [q(C).numerator, q(C).denominator]}

    keyx = ex(key)
    if float(keyx) <= 0:
        raise ItemError("the quantity asked for must be positive")
    if d["fmt"] == "spr":
        if not keyx.is_rational or len(keyx.gridin()) > 6:
            raise ItemError("the answer does not fit a grid-in")
        return Item("le2.context_substitute", "writing and solving an equation",
                    "medium", seed, stem, "spr", keyx, keyx.gridin(), why, params=P)
    named = _named(key, mistakes, d.get("whole", False))
    if len(named) < 3:
        raise ItemError("these numbers leave too few of the named mistakes to choose "
                        "three distinct wrong answers from")
    choices, latex, reasons, letter = choose(keyx, named, rng, signed=True,
                                             fillers="shift")
    return Item("le2.context_substitute", "writing and solving an equation", "medium",
                seed, stem, "mcq", keyx, letter, why, choices, reasons, latex, params=P)


# ------------------------------------------------------------- a mixture

def mixture_solve(rng: random.Random, seed: int, *, p1=None, p2=None, pm=None,
                  volume=None) -> Item:
    """Two strengths blended to a third: how much of the strong one is needed."""
    P1 = int(p1 if p1 is not None else rng.randrange(12, 60, 1))
    P2 = int(p2 if p2 is not None else rng.randrange(2, 40, 1))
    if P1 <= P2 + 5:
        raise ItemError("the added solution must be clearly the stronger of the two")
    PM = int(pm if pm is not None else rng.randint(P2 + 2, P1 - 2))
    if not (P2 + 1 < PM < P1 - 1):
        raise ItemError("the blend must land well between the two strengths")
    V = q(volume if volume is not None else rng.randint(2, 20))
    key = V * Q(PM - P2, P1 - PM)
    keyx = ex(key)
    if float(keyx) <= 0 or not keyx.is_rational or len(keyx.gridin()) > 6:
        raise ItemError("the answer does not fit a grid-in")
    if (key * 100).denominator != 1 or key > 4 * V:
        raise ItemError("the amount added must be a tidy and plausible quantity")
    stem = (f"How many liters of {_article(str(P1))} {P1}% saline solution must be "
            f"added to {numtext(V)} liters of {_article(str(P2))} {P2}% saline solution "
            f"to obtain {_article(str(PM))} {PM}% saline solution?")
    over, under = P1 - PM, PM - P2
    why = (f"Each liter added carries {P1}% salt into a blend that is only {PM}%, a "
           f"surplus of {over} percentage {'point' if over == 1 else 'points'}, and "
           f"each of the {numtext(V)} liters already there is {under} "
           f"{'point' if under == 1 else 'points'} short; the surpluses have to cancel "
           f"the shortfalls exactly.")
    P = {"kind": "le2_mixture", "p1": P1, "p2": P2, "pm": PM,
         "v": [V.numerator, V.denominator]}
    return Item("le2.mixture_solve", "a mixture of two concentrations", "hard", seed,
                stem, "spr", keyx, keyx.gridin(), why, params=P)
