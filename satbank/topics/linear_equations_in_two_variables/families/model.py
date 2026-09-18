"""Turning a situation into ax + by = c.

The nine source items in this family differ in what the two coefficients are
made of -- a price, a time, a number of sides, a percentage by weight, a growth
factor -- and the wrong answers follow from that: a price item invites the two
prices being swapped, a polygon item invites the number of shapes being used
where the number of sides belongs, and a percentage item invites 60 where 0.6
belongs. The coefficients are therefore never drawn on their own; each context
says what it is counting and the distractors are built from that.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import Item, ItemError, Mis
from ..common import (MINUS, coef_text, dec, numtext, pair, q, sig, std_text,
                      text_item)

__all__ = ["model_standard", "model_percent", "material_table"]


def _round_to(v, places: int) -> Q:
    """The value a student would write after rounding to `places` decimals."""
    v = q(v)
    scale = 10 ** places
    n = (abs(v) * scale + Q(1, 2)).__floor__()
    return Q(-n if v < 0 else n, scale)


# ------------------------------------------------------ per-unit totals

STANDARD = [
    # 0 -- two preparation times
    dict(shape="per_unit", xv="x", yv="y", places=1, cplaces=1, order=None,
         wrongs=["swap", "count", "divide", "sub", "swapsub"],
         lo=Q(5, 10), hi=Q(99, 10), tlo=Q(200, 10), thi=Q(990, 10),
         stem="An employee at a restaurant prepares sandwiches and salads. It takes "
              "the employee {a} minutes to prepare a sandwich and {b} minutes to "
              "prepare a salad. The employee spends a total of {c} minutes preparing "
              "x sandwiches and y salads. Which equation represents this situation?",
         why="Each sandwich takes {a} minutes, so x sandwiches take {ax} minutes, and "
             "y salads take {by} minutes; together they fill the {c} minutes."),
    # 1 -- two kinds of transit pass
    dict(shape="per_unit", xv="g", yv="t", places=2, cplaces=0, order="desc",
         wrongs=["swap", "count", "sumrates", "sub", "swapsub"],
         lo=Q(50, 100), hi=Q(1999, 100), tlo=Q(40), thi=Q(300),
         stem="Tony spends ${c} per month on public transportation. A 10-ride pass "
              "costs ${a}, and a single-ride pass costs ${b}. If g represents the "
              "number of 10-ride passes Tony buys in a month and t represents the "
              "number of single-ride passes Tony buys in a month, which of the "
              "following equations best represents the relationship between g and t ?",
         why="Each 10-ride pass costs ${a}, so g of them cost ${ax}, and t single-ride "
             "passes cost ${by}; the two together are the ${c} Tony spends."),
    # 2 -- two supplies bought by the piece
    dict(shape="per_unit", xv="x", yv="y", places=2, cplaces=2, order="asc",
         wrongs=["swapsub", "sub", "swap", "count"],
         lo=Q(2, 100), hi=Q(199, 100), tlo=Q(10000, 100), thi=Q(99999, 100),
         stem="A food truck buys forks for ${a} each and plates for ${b} each. The "
              "total cost of x forks and y plates is ${c}. Which equation represents "
              "this situation?",
         why="x forks at ${a} each cost ${ax} and y plates at ${b} each cost ${by}, "
             "so the two costs add to the ${c} total."),
    # 3 -- questions worth different numbers of points
    dict(shape="per_unit", xv="x", yv="y", places=None, cplaces=None, order="asc",
         wrongs=["prod", "sumscale", "swap", "count"],
         lo=Q(1), hi=Q(9), tlo=Q(30), thi=Q(200), integer=True,
         stem="A teacher is creating an assignment worth {c} points. The assignment "
              "will consist of questions worth {a} {apt} and questions worth {b} "
              "{bpt}. Which equation represents this situation, where x represents "
              "the number of {a}-point questions and y represents the number of "
              "{b}-point questions?",
         why="Each of the x questions is worth {a} {apt}, so they carry {ax} points "
             "between them, and the y questions carry {by}; the two add to {c}."),
    # 4 -- perimeters of two kinds of regular polygon
    dict(shape="grouped", xv="r", yv="t", places=None, cplaces=None,
         wrongs=["sideswap", "counts", "countswap", "sides"],
         stem="A total of {n1} {p1} each have side length r. A total of {n2} {p2} each "
              "have side length t. None of these {p1} and {p2} shares a side. The sum "
              "of the perimeters of all these {p1} and {p2} is {c}. Which equation "
              "represents this situation?",
         why="Each of the {n1} {p1} has {s1} sides of length r, which is {a}r in all, "
             "and the {n2} {p2} contribute {b}t; the perimeters total {c}."),
    # 5 -- a total split into a variable part and a fixed part
    dict(shape="split_total", xv="x", yv="y", places=None, cplaces=None,
         tlo=Q(20), thi=Q(900),
         stem="A city's total expense budget for one year was x million dollars. The "
              "city budgeted y million dollars for departmental expenses and {c} "
              "million dollars for all other expenses. Which of the following "
              "represents the relationship between x and y in this context?",
         why="The y million dollars of departmental expenses and the {c} million "
             "dollars of other expenses make up the whole x million, so what is left "
             "of x after the departmental share is the {c} million."),
]

POLYGONS = [("triangles", 3), ("squares", 4), ("pentagons", 5), ("hexagons", 6),
            ("octagons", 8)]


def model_standard(rng: random.Random, seed: int, *, ctx=None, a=None, b=None, c=None,
                   n1=None, n2=None, poly1=None, poly2=None) -> Item:
    """A context, and the equation ax + by = c that records it."""
    i = rng.randrange(len(STANDARD)) if ctx is None else ctx
    d = STANDARD[i]
    shape, xv, yv = d["shape"], d["xv"], d["yv"]
    places, cplaces = d["places"], d["cplaces"]
    style = "dec" if places is not None else "frac"
    rhs = None
    extra = {}

    if shape == "grouped":
        j1 = POLYGONS.index(poly1) if isinstance(poly1, tuple) else (
            poly1 if poly1 is not None else rng.randrange(len(POLYGONS)))
        j2 = POLYGONS.index(poly2) if isinstance(poly2, tuple) else (
            poly2 if poly2 is not None else rng.randrange(len(POLYGONS)))
        if j1 == j2:
            raise ItemError("the two kinds of polygon must differ")
        (p1, s1), (p2, s2) = POLYGONS[j1], POLYGONS[j2]
        n1 = int(n1 if n1 is not None else rng.randint(2, 12))
        n2 = int(n2 if n2 is not None else rng.randint(2, 12))
        A, B = q(n1 * s1), q(n2 * s2)
        C = q(c if c is not None else rng.randrange(60, 900, 5))
        extra = dict(n1=n1, n2=n2, s1=s1, s2=s2, p1=p1, p2=p2)
        stem = d["stem"].format(n1=n1, n2=n2, p1=p1, p2=p2, c=numtext(C))
    elif shape == "split_total":
        A, B = q(1), q(-1)
        C = q(c if c is not None else rng.randint(int(d["tlo"]), int(d["thi"])))
        stem = d["stem"].format(c=numtext(C))
    else:
        if a is None or b is None:
            if d.get("integer"):
                A = q(rng.randint(int(d["lo"]), int(d["hi"])))
                B = q(rng.randint(int(d["lo"]), int(d["hi"])))
            else:
                scale = 10 ** places
                A = Q(rng.randint(int(d["lo"] * scale), int(d["hi"] * scale)), scale)
                B = Q(rng.randint(int(d["lo"] * scale), int(d["hi"] * scale)), scale)
            if d.get("order") == "desc" and A < B:
                A, B = B, A
            if d.get("order") == "asc" and A > B:
                A, B = B, A
        else:
            A, B = q(a), q(b)
        if A == B:
            raise ItemError("the two rates must differ, or the item has no question")
        if d.get("order") == "desc" and A < B:
            raise ItemError("the first item must be the dearer of the two")
        if d.get("order") == "asc" and A > B:
            raise ItemError("the second item must be the dearer of the two")
        if c is None:
            if cplaces:
                scale = 10 ** cplaces
                C = Q(rng.randint(int(d["tlo"] * scale), int(d["thi"] * scale)), scale)
            else:
                C = q(rng.randint(int(d["tlo"]), int(d["thi"])))
        else:
            C = q(c)
        at, bt, ct = (numtext(A, style, places), numtext(B, style, places),
                      numtext(C, style, cplaces))
        stem = d["stem"].format(a=at, b=bt, c=ct,
                                apt=("point" if A == 1 else "points"),
                                bpt=("point" if B == 1 else "points"))

    if A <= 0 or B == 0:
        raise ItemError("a rate must be positive")
    key = std_text(A, B, C, xv, yv, style, places, cplaces, rhs)
    ks = sig("std", A, B, C)

    def std_opt(u, v, w=None):
        w = C if w is None else w
        return pair(std_text(u, v, w, xv, yv, style, places, cplaces), "std", u, v, w)

    pool = {}
    if shape == "grouped":
        pool["sideswap"] = Mis("used the numbers of sides on the wrong shapes",
                               std_opt(n1 * s2, n2 * s1))
        pool["counts"] = Mis("used the numbers of polygons as the coefficients",
                             std_opt(n1, n2))
        pool["countswap"] = Mis("used the numbers of polygons, and on the wrong shapes",
                                std_opt(n2, n1))
        pool["sides"] = Mis("counted one side of each shape rather than the whole "
                            "perimeter", std_opt(s1, s2))
    elif shape == "split_total":
        pool["add"] = Mis("added the two parts instead of taking the departmental "
                          "share out of the total", std_opt(1, 1))
        pool["flip"] = Mis("subtracted the total from the part instead of the other "
                           "way round",
                           (f"{yv} {MINUS} {xv} = {numtext(C)}", sig("flip", C)))
        pool["twice"] = Mis("counted the whole budget twice", std_opt(2, -1))
    else:
        pool["swap"] = Mis("swapped the two rates", std_opt(B, A))
        pool["count"] = Mis("counted the items instead of what each one is worth",
                            std_opt(1, 1))
        pool["sub"] = Mis("subtracted the second amount instead of adding it",
                          std_opt(A, -B))
        pool["swapsub"] = Mis("swapped the two rates and subtracted one amount from "
                              "the other", std_opt(B, -A))
        if places is not None and max(C / A, C / B) <= 200:
            u, v = _round_to(C / A, places), _round_to(C / B, places)
            pool["divide"] = Mis(
                "divided the total by each rate, which is how many of one kind alone "
                "would fill it rather than how the two shares add up", std_opt(u, v))
        if cplaces is not None:
            pool["sumrates"] = Mis(
                "added the two prices on the right and counted the passes on the left",
                (f"{xv} + {yv} = {numtext(B, style, places)} + "
                 f"{numtext(A, style, places)}", sig("sumrates", B, A)))
        if d.get("integer"):
            k = A + B
            pool["prod"] = Mis("multiplied the two point values together and the two "
                               "counts with them",
                               (f"{numtext(k)}{xv}{yv} = {numtext(C)}",
                                sig("prod", k, C)))
            pool["sumscale"] = Mis("added the two point values and gave every question "
                                   "the sum", (f"{numtext(k)}({xv} + {yv}) = "
                                               f"{numtext(C)}", sig("sumscale", k, C)))
    order = d.get("wrongs") or list(pool)
    wrong = [pool[nm] for nm in order if nm in pool] + \
            [m for nm, m in pool.items() if nm not in order]

    P = {"kind": "le2_model", "shape": shape, "a": [A.numerator, A.denominator],
         "b": [B.numerator, B.denominator], "c": [C.numerator, C.denominator]}
    P.update({k: v for k, v in extra.items() if not isinstance(v, str)})
    at, bt, ct = (numtext(A, style, places), numtext(B, style, places),
                  numtext(C, style, cplaces))
    if shape == "grouped":
        why = d["why"].format(n1=n1, n2=n2, s1=s1, p1=p1, p2=p2, a=at, b=bt, c=ct)
    elif shape == "split_total":
        why = d["why"].format(c=ct)
    else:
        why = d["why"].format(a=at, b=bt, c=ct, ax=coef_text(A, xv, style, places),
                              by=coef_text(B, yv, style, places),
                              apt=("point" if A == 1 else "points"))
    return text_item("le2.model_standard", "an equation for a situation", "easy", seed,
                     stem, key, ks, wrong, rng, P, why)


# --------------------------------------------------------- percentages

PERCENT = [
    dict(mode="weight", xv="x", yv="y",
         stem="A gardener buys two kinds of fertilizer. Fertilizer A contains {pa}% "
              "filler materials by weight and Fertilizer B contains {pb}% filler "
              "materials by weight. Together, the fertilizers bought by the gardener "
              "contain a total of {c} pounds of filler materials. Which equation "
              "models this relationship, where x is the number of pounds of Fertilizer "
              "A and y is the number of pounds of Fertilizer B?",
         why="{pa}% of the x pounds of Fertilizer A is {da}x pounds of filler, and "
             "{pb}% of the y pounds of Fertilizer B is {db}y, so the two make up the "
             "{c} pounds."),
    dict(mode="mixture", xv="x", yv="y",
         stem="A chemist studying the impact of salt on a process mixes x kilograms of "
              "a low-salt mixture, which is {pa}% salt by weight, with y kilograms of "
              "a high-salt mixture, which is {pb}% salt by weight, to create {V} "
              "kilograms of a mixture that is {pm}% salt by weight. Which equation "
              "represents this situation?",
         why="The salt in the two mixtures is {da}x and {db}y kilograms, and the {V} "
             "kilograms of result is {pm}% salt, so the salt on each side must match."),
    dict(mode="growth", xv="a", yv="b",
         stem="In {y0}, a swim club had a total of {V} swimmers, each classified as "
              "either advanced or intermediate. From {y0} to {y1}, the number of "
              "advanced swimmers in the club increased by approximately {pa}%, and the "
              "number of intermediate swimmers in the club increased by approximately "
              "{pb}%. The total number of swimmers in the club increased by "
              "approximately {pm}%. Which equation best represents this situation, "
              "where a represents the number of advanced swimmers in the club in {y0} "
              "and b represents the number of intermediate swimmers in the club in "
              "{y0}?",
         why="A rise of {pa}% multiplies the advanced swimmers by {da}, and {pb}% "
             "multiplies the intermediate swimmers by {db}; the {V} swimmers as a "
             "whole rose by {pm}%."),
]


def model_percent(rng: random.Random, seed: int, *, ctx=None, pa=None, pb=None, pm=None,
                  c=None, volume=None, y0=None, y1=None) -> Item:
    """A percentage of each of two quantities, adding to a stated amount."""
    i = rng.randrange(len(PERCENT)) if ctx is None else ctx
    d = PERCENT[i]
    mode, xv, yv = d["mode"], d["xv"], d["yv"]
    pa = int(pa if pa is not None else rng.randrange(2, 96, 2))
    pb = int(pb if pb is not None else rng.randrange(2, 96, 2))
    if pa == pb:
        raise ItemError("the two percentages must differ")
    if d["mode"] == "mixture" and pa > pb:
        # the stem calls the first mixture the low-salt one
        raise ItemError("the low-salt mixture cannot be the stronger of the two")
    da, db = Q(pa, 100), Q(pb, 100)
    if mode == "growth":
        da, db = 1 + da, 1 + db

    if mode == "weight":
        C = q(c if c is not None else rng.randrange(40, 900, 10))
        rhs = numtext(C)
        rsig = sig("plain", C)
        stem = d["stem"].format(pa=pa, pb=pb, c=numtext(C))
    else:
        V = q(volume if volume is not None else rng.randint(8, 90))
        lo, hi = min(pa, pb), max(pa, pb)
        if hi - lo < 3:
            raise ItemError("the two strengths must be far enough apart to blend")
        pm = int(pm if pm is not None else rng.randint(lo + 1, hi - 1))
        if not (lo < pm < hi):
            raise ItemError("the blended percentage must lie between the two given")
        if mode == "mixture":
            dm = Q(pm, 100)
            rhs = f"({dec(dm)})({numtext(V)})"
            rsig = sig("prod", dm, V)
            C = dm * V
            stem = d["stem"].format(pa=pa, pb=pb, pm=pm, V=numtext(V))
        else:
            dm = 1 + Q(pm, 100)
            rhs = f"{numtext(V)}({dec(dm)})"
            rsig = sig("scaled", V, dm)
            C = dm * V
            y0 = int(y0 if y0 is not None else rng.randrange(1990, 2016))
            y1 = int(y1 if y1 is not None else y0 + rng.choice([5, 10, 10, 15, 20]))
            stem = d["stem"].format(pa=pa, pb=pb, pm=pm, V=numtext(V), y0=y0, y1=y1)

    key = std_text(da, db, C, xv, yv, "dec", None, None, rhs)
    ks = sig("p", da, db) + rsig

    def built(u, v, r, rs):
        text = std_text(u, v, C, xv, yv, "dec", None, None, r)
        return (text, sig("p", u, v) + rs)

    if mode == "weight":
        wrong = [Mis("attached each percentage to the other fertilizer",
                     built(db, da, rhs, rsig)),
                 Mis("used the percentages as whole numbers instead of as decimals",
                     built(pa, pb, rhs, rsig)),
                 Mis("used the percentages as whole numbers and attached each to the "
                     "other fertilizer", built(pb, pa, rhs, rsig))]
    elif mode == "mixture":
        plain = numtext(V)
        psig = sig("plain", V)
        wrong = [Mis("attached each percentage to the other mixture",
                     built(db, da, rhs, rsig)),
                 Mis("set the salt equal to the whole {} kilograms rather than to the "
                     "salt in it".format(numtext(V)), built(da, db, plain, psig)),
                 Mis("attached each percentage to the other mixture and set the salt "
                     "equal to the whole mixture", built(db, da, plain, psig))]
    else:
        dm = 1 + Q(pm, 100)
        rhs_a = f"{numtext(V)}({dec(db)})"
        sig_a = sig("scaled", V, db)
        wrong = [Mis("used the club's overall growth factor on the intermediate "
                     "swimmers and their own factor on the right-hand side",
                     built(da, dm, rhs_a, sig_a)),
                 Mis("used the overall factor on the advanced swimmers and the bare "
                     "percentage increase, not the growth factor, on the intermediate "
                     "ones", built(dm, Q(pb, 100), rhs_a, sig_a)),
                 Mis("attached each growth factor to the other group",
                     built(db, da, rhs, rsig))]
    wrong = [Mis(m.reason, m.value) for m in wrong if m.value[0] != key]
    P = {"kind": "le2_percent", "mode": mode, "pa": pa, "pb": pb,
         "c": [q(C).numerator, q(C).denominator]}
    if mode != "weight":
        P["pm"] = pm
        P["v"] = [q(V).numerator, q(V).denominator]
    why = d["why"].format(pa=pa, pb=pb, pm=pm, c=numtext(C) if mode == "weight" else "",
                          da=dec(da), db=dec(db), V=numtext(V) if mode != "weight" else "")
    return text_item("le2.model_percent", "a percentage model", "easy", seed, stem, key,
                     ks, wrong, rng, P, why)


# ------------------------------------------------- a table of materials

ROCKS = [("Basalt", 180, 18), ("Granite", 165, 9), ("Limestone", 120, 3),
         ("Sandstone", 135, 22), ("Marble", 170, 27), ("Slate", 174, 15),
         ("Shale", 160, 6), ("Quartzite", 166, 31), ("Gneiss", 175, 12),
         ("Dolomite", 181, 8)]
HEAD = ["Rock type", "Weight per volume (lb/ft³)", "Cost per pound"]
LEAD = ("A city is planning to build a rock retaining wall, a monument, and a garden in "
        "a park. The table above shows four rock types that will be considered for use "
        "in the project. Also shown for each rock type is its weight per volume, in "
        "pounds per cubic foot (lb/ft³), and the cost per pound, in dollars. ")


def material_table(rng: random.Random, seed: int, *, ask=None, picks=None, xi=None,
                   yi=None, zi=None, known=None, total=None, part=None) -> Item:
    """Four rock types in a table, and an equation built out of two of them."""
    ask = ask or rng.choice(["interpret", "equation"])
    if picks is None:
        picks = rng.sample(range(len(ROCKS)), 4)
    rows = [ROCKS[i] for i in picks]
    table = [list(HEAD)] + [[n, numtext(d), "$" + dec(Q(c, 100), 2)] for n, d, c in rows]
    names = [n.lower() for n, _, _ in rows]

    if ask == "interpret":
        xi = rng.randrange(4) if xi is None else xi
        yi = rng.choice([j for j in range(4) if j != xi]) if yi is None else yi
        if xi == yi:
            raise ItemError("the equation needs two different rock types")
        rest = [j for j in range(4) if j not in (xi, yi)]
        n1, d1, c1 = rows[xi]
        n2, d2, c2 = rows[yi]
        K = q(part if part is not None else Q(rng.randrange(50000, 900000), 100))
        T = q(total if total is not None else K + Q(rng.randrange(50000, 900000), 100))
        if T <= K:
            raise ItemError("the leftover cost must be part of the total")
        eq = (f"{dec(Q(c1, 100), 2)}({numtext(d1)}w) + {dec(Q(c2, 100), 2)}"
              f"({numtext(d2)}z) + {dec(K, 2)} = {dec(T, 2)}")
        stem = (LEAD + f"The equation {eq} gives the total cost, in dollars, of the "
                f"rocks used in the project in terms of the number of ft³ of {n1.lower()}, "
                f"w, and the number of ft³ of {n2.lower()}, z. All four rock types are "
                f"used in the project. Which of the following is the best interpretation "
                f"of {dec(K, 2)} in this context?")
        key = (f"The cost of the {names[rest[0]]} and {names[rest[1]]} needed for the "
               f"project")
        ks = sig("pairnamed", rest[0], rest[1])
        wrong = [Mis("named the two rock types the equation already prices, which are "
                     "the ones the variables stand for",
                     (f"The cost of the {names[xi]} and {names[yi]} needed for the "
                      f"project", sig("pairnamed", min(xi, yi), max(xi, yi)))),
                 Mis("named one of the rock types the equation already prices",
                     (f"The cost of the {names[yi]} needed for the project",
                      sig("onenamed", yi))),
                 Mis("named only one of the two rock types the fixed amount covers",
                     (f"The cost of the {names[rest[1]]} needed for the project",
                      sig("onenamed", rest[1]))),
                 Mis("named the other rock type the equation already prices",
                     (f"The cost of the {names[xi]} needed for the project",
                      sig("onenamed", xi))),
                 Mis("named only the first of the two rock types the fixed amount "
                     "covers", (f"The cost of the {names[rest[0]]} needed for the "
                                f"project", sig("onenamed", rest[0])))]
        P = {"kind": "le2_material", "ask": ask, "picks": list(picks), "xi": xi,
             "yi": yi}
        why = (f"Every rock type is used, so the {dec(T, 2)} covers all four. Two of "
               f"them are already priced by the terms in w and z, which leaves "
               f"{dec(K, 2)} for the {names[rest[0]]} and the {names[rest[1]]}.")
        return text_item("le2.material_table", "reading a materials table", "easy", seed,
                         stem, key, ks, wrong, rng, P, why, table=table)

    # ask == "equation": three rock types, one of them weighed out already
    if zi is None:
        zi, xi2, yi2 = rng.sample(range(4), 3)
    else:
        xi2, yi2 = (xi, yi) if xi is not None else tuple(
            j for j in range(4) if j != zi)[:2]
    if xi is not None:
        xi2 = xi
    if yi is not None:
        yi2 = yi
    if len({zi, xi2, yi2}) != 3:
        raise ItemError("the garden needs three different rock types")
    T = int(total if total is not None else rng.randrange(400, 4000, 50))
    W = int(known if known is not None else rng.randrange(50, 350, 10))
    if W >= T:
        raise ItemError("the weighed rock cannot outweigh the whole garden")
    used = sorted([zi, xi2, yi2])
    d_known = rows[zi][1]
    dx, dy = rows[xi2][1], rows[yi2][1]
    left = T - W
    stem = (LEAD + "Only " + ", ".join(names[j] for j in used[:-1]) +
            f", and {names[used[-1]]} will be used in the garden. The rocks in the "
            f"garden will have a total weight of {numtext(T)} pounds. If {numtext(W)} "
            f"pounds of {names[zi]} is used, which of the following equations could "
            f"show the relationship between the amounts, x and y, in ft³, for each of "
            f"the other rock types used?")
    key = std_text(dx, dy, left, "x", "y")
    ks = sig("std", dx, dy, left)
    cands = [("used the weighed-out rock's own weight per volume in place of one of "
              "the others", (d_known, dy, left)),
             ("used the weighed-out rock's weight per volume and kept the whole "
              "garden's weight", (d_known, dx, T)),
             ("kept the whole garden's weight instead of what is left after the "
              "weighed rock", (dx, dy, T)),
             ("swapped the two weights per volume", (dy, dx, left))]
    wrong = [Mis(r, pair(std_text(u, v, w, "x", "y"), "std", u, v, w))
             for r, (u, v, w) in cands if (q(u), q(v), q(w)) != (q(dx), q(dy), q(left))]
    P = {"kind": "le2_material", "ask": "equation", "picks": list(picks), "zi": zi,
         "xi": xi2, "yi": yi2, "total": T, "known": W, "dx": dx, "dy": dy,
         "dz": d_known}
    why = (f"The {numtext(W)} pounds of {names[zi]} is already accounted for, so the "
           f"other two rock types weigh {numtext(left)} pounds between them, at "
           f"{numtext(dx)} and {numtext(dy)} pounds per cubic foot.")
    return text_item("le2.material_table", "an equation from a materials table",
                     "medium", seed, stem, key, ks, wrong, rng, P, why, table=table)
