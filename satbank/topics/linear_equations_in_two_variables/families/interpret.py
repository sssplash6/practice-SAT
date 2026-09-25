"""What a number in ax + by = c means.

Eleven source items hand the student a finished equation and ask what one piece
of it stands for, and the four options are always the same two confusions
crossed: a per-unit rate against a total, and the first quantity against the
second. Modelling the options that way is what lets one template carry a yogurt
counter, a polygon and a township, and it is also what the independent solver
checks -- it works out which variable the queried piece belongs to and whether
that piece is a rate or an amount, and asks which option says so.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....figures import coordinate_grid
from ....item import Item, ItemError, Mis, gridin_mistakes
from ..common import ex, numtext, q, sig, std_text, text_item

__all__ = ["interpret_coefficient", "interpret_constant", "interpret_point"]


# ------------------------------------------------- a coefficient's meaning

COEF = [
    # 0 -- which expression is the price of one of the smaller containers (1.1)
    dict(ask="expression", places=2, cplaces=2, xv="x", yv="y", which="x", order="asc",
         gap=Q(60, 100), lo=Q(100, 100), hi=Q(999, 100), tlo=Q(20000, 100), thi=Q(400000, 100),
         stem="A store sells two different-sized containers of a certain Greek yogurt. "
              "The store's sales of this Greek yogurt totaled {c} dollars last month. "
              "The equation {eq} represents this situation, where x is the number of "
              "smaller containers sold and y is the number of larger containers sold. "
              "According to the equation, which of the following represents the price, "
              "in dollars, of each smaller container?",
         why="Each smaller container sold adds its own price to the total, so the "
             "number multiplying x is that price; {ax} is what all x of them cost."),
    # 1 -- the price of one salad (1.20)
    dict(ask="meaning", places=2, cplaces=None, xv="x", yv="y", which="y", display=True,
         order="asc", gap=Q(60, 100), lo=Q(100, 100), hi=Q(999, 100), tlo=Q(20),
         thi=Q(400),
         head="F = {a}x + {b}y",
         stem="In the equation above, F represents the total amount of money, in "
              "dollars, a food truck charges for x drinks and y salads. The price, in "
              "dollars, of each drink is the same, and the price, in dollars, of each "
              "salad is the same. Which of the following is the best interpretation "
              "for the number {b} in this context?",
         opts=[("rate", "y", "The price, in dollars, of one salad"),
               ("rate", "x", "The price, in dollars, of one drink"),
               ("count", "x", "The number of drinks bought during the day"),
               ("count", "y", "The number of salads bought during the day")],
         why="y counts the salads, so the number multiplying y is charged once for "
             "each salad."),
    # 2 -- the side length of the second polygon (2.8)
    dict(ask="meaning", places=None, cplaces=None, xv="x", yv="y", which="y",
         lo=Q(2), hi=Q(12), tlo=Q(20), thi=Q(300),
         stem="Figure A and figure B are both regular polygons. The sum of the "
              "perimeter of figure A and the perimeter of figure B is {c} inches. The "
              "equation {eq} represents this situation, where x is the number of sides "
              "of figure A and y is the number of sides of figure B. Which statement "
              "is the best interpretation of {b} in this context?",
         opts=[("rate", "y", "Each side of figure B has a length of {b} inches."),
               ("rate", "x", "Each side of figure A has a length of {b} inches."),
               ("count", "y", "The number of sides of figure B is {b}."),
               ("count", "x", "The number of sides of figure A is {b}.")],
         why="y is already the number of sides of figure B, so the {b} multiplying it "
             "is the length each of those sides contributes to the perimeter."),
    # 3 -- what the variable itself counts (2.23)
    dict(ask="variable", places=None, cplaces=None, xv="x", yv="y", which="x",
         order="asc", lo=Q(2), hi=Q(40), tlo=Q(1000), thi=Q(9000),
         stem="A certain township consists of a {a}-hectare industrial park and a {b}-"
              "hectare neighborhood. The total number of trees in the township is {c}. "
              "The equation {eq} represents this situation. Which of the following is "
              "the best interpretation of x in this context?",
         opts=[("rate", "x", "The average number of trees per hectare in the "
                             "industrial park"),
               ("rate", "y", "The average number of trees per hectare in the "
                             "neighborhood"),
               ("count", "x", "The total number of trees in the industrial park"),
               ("count", "y", "The total number of trees in the neighborhood")],
         why="{a}x has to come out in trees and {a} is already the {a} hectares of the "
             "industrial park, so x is the trees on each of those hectares."),
    # 4 -- how much dearer the second item is (2.24)
    dict(ask="difference", places=2, cplaces=0, xv="x", yv="y", display=True,
         lo=Q(500, 100), hi=Q(9999, 100), tlo=Q(200), thi=Q(3000),
         head="{a}x + {b}y = {c}",
         stem="Isabel ordered topsoil and crushed stone, which cost a total of ${c}, "
              "for her garden. The given equation represents the relationship between "
              "the number of cubic yards of topsoil, x, and the number of tons of "
              "crushed stone, y, Isabel ordered. How much more, in dollars, did a ton "
              "of crushed stone cost Isabel than a cubic yard of topsoil?",
         why="Each cubic yard of topsoil adds {a} to the bill and each ton of crushed "
             "stone adds {b}, so the gap between the two per-unit prices is what is "
             "asked for."),
    # 5 -- how many more points one token is worth (3.16)
    dict(ask="difference", places=None, cplaces=None, xv="G", yv="R", display=True,
         lo=Q(2), hi=Q(60), tlo=Q(100), thi=Q(900),
         head="{a}G + {b}R = {c}",
         stem="At a school fair, students can win colored tokens that are worth a "
              "different number of points depending on the color. One student won G "
              "green tokens and R red tokens worth a total of {c} points. The given "
              "equation represents this situation. How many more points is a red token "
              "worth than a green token?",
         why="G is a count of green tokens, so the {a} multiplying it is the points one "
             "green token carries, and likewise {b} for a red one."),
]


def _draw(rng, d, a, b, c):
    places, cplaces = d["places"], d["cplaces"]
    if a is None or b is None:
        if places:
            scale = 10 ** places
            A = Q(rng.randint(int(d["lo"] * scale), int(d["hi"] * scale)), scale)
            B = Q(rng.randint(int(d["lo"] * scale), int(d["hi"] * scale)), scale)
        else:
            A = q(rng.randint(int(d["lo"]), int(d["hi"])))
            B = q(rng.randint(int(d["lo"]), int(d["hi"])))
    else:
        A, B = q(a), q(b)
    if c is None:
        if cplaces:
            scale = 10 ** cplaces
            C = Q(rng.randint(int(d["tlo"] * scale), int(d["thi"] * scale)), scale)
        else:
            C = q(rng.randint(int(d["tlo"]), int(d["thi"])))
    else:
        C = q(c)
    if a is None and b is None:
        if d.get("order") == "asc" and A > B:
            A, B = B, A
        if d.get("order") == "desc" and A < B:
            A, B = B, A
    return A, B, C


def interpret_coefficient(rng: random.Random, seed: int, *, ctx=None, a=None, b=None,
                          c=None) -> Item:
    """What the number multiplying a variable stands for."""
    i = rng.randrange(len(COEF)) if ctx is None else ctx
    d = COEF[i]
    style = "dec" if d["places"] else "frac"
    A, B, C = _draw(rng, d, a, b, c)
    if A == B:
        raise ItemError("the two coefficients must differ")
    if abs(A - B) < d.get("gap", 0):
        raise ItemError("the two prices must be far enough apart to tell apart")
    xv, yv = d["xv"], d["yv"]
    at, bt = numtext(A, style, d["places"]), numtext(B, style, d["places"])
    ct = numtext(C, style, d["cplaces"])
    eq = std_text(A, B, C, xv, yv, style, d["places"], d["cplaces"])
    stem = d["stem"].format(a=at, b=bt, c=ct, eq=eq)
    if d.get("display"):
        stem = d["head"].format(a=at, b=bt, c=ct) + "\n" + stem
    why = d["why"].format(a=at, b=bt, c=ct, ax=f"{at}{xv}")
    queried = B if d.get("which") == "y" else A
    P = {"kind": "le2_coef", "ask": d["ask"], "which": d.get("which"),
         "queried": [queried.numerator, queried.denominator],
         "a": [A.numerator, A.denominator], "b": [B.numerator, B.denominator],
         "c": [C.numerator, C.denominator]}

    if d["ask"] == "difference":
        key = ex(abs(B - A))
        if key == 0:
            raise ItemError("the two per-unit prices must differ")
        return Item("le2.interpret_coefficient", "reading a coefficient", "medium", seed,
                    stem, "spr", key, key.gridin(), why, params=P,
                    spr_mistakes=gridin_mistakes(key, [
                        Mis("reported only the first per-unit price", ex(A)),
                        Mis("reported only the second per-unit price", ex(B)),
                        Mis("added the two per-unit prices instead of finding their difference",
                            ex(A + B)),
                        Mis("halved the difference between the two per-unit prices",
                            ex(abs(B - A) / 2)),
                    ]))

    if d["ask"] == "expression":
        key = at
        wrong = [Mis("gave the whole term for the smaller containers rather than the "
                     "price of one of them", (f"{at}{xv}", sig("term", "x"))),
                 Mis("gave the price of a larger container", (bt, sig("coef", "y"))),
                 Mis("gave the whole term for the larger containers",
                     (f"{bt}{yv}", sig("term", "y")))]
        return text_item("le2.interpret_coefficient", "reading a coefficient", "easy",
                         seed, stem, key, sig("coef", "x"), wrong, rng, P, why)

    want = ("rate", d["which"]) if d["ask"] == "meaning" else ("rate", d["which"])
    opts = [(k, w, t.format(a=at, b=bt, c=ct)) for k, w, t in d["opts"]]
    key = next(t for k, w, t in opts if (k, w) == want)
    named = {("rate", "x"): "named the rate for the other quantity",
             ("rate", "y"): "named the rate for the other quantity",
             ("count", "x"): "read the coefficient as a count of the first quantity "
                             "rather than as an amount per one of them",
             ("count", "y"): "read the coefficient as a count of the second quantity "
                             "rather than as an amount per one of them"}
    wrong = [Mis(named[(k, w)], (t, sig(k, w))) for k, w, t in opts if (k, w) != want]
    return text_item("le2.interpret_coefficient", "reading a coefficient", "medium",
                     seed, stem, key, sig(*want), wrong, rng, P, why)


# -------------------------------------------------- a constant's meaning

CONST = [
    # 0 -- a total of two times (1.4)
    dict(mode="total", display=True, head="x + y = {c}", a=1, b=1,
         tlo=20, thi=200,
         stem="The equation above relates the number of minutes, x, Maria spends "
              "running each day and the number of minutes, y, she spends biking each "
              "day. In the equation, what does the number {c} represent?",
         opts=[("total", "both", "The total number of minutes spent running and biking "
                                 "each day"),
               ("total", "x", "The number of minutes spent running each day"),
               ("total", "y", "The number of minutes spent biking each day"),
               ("rate", "both", "The number of minutes spent biking for each minute "
                                "spent running")],
         why="Neither x nor y is fixed -- only their sum is -- so the {c} is what the "
             "two of them come to together."),
    # 1 -- a total bill (1.11)
    dict(mode="total", display=True, head="{a}x + {b}y = {c}", tlo=12, thi=400,
         alo=2, ahi=9,
         stem="Mario purchased {a} binders that cost x dollars each and {b} notebooks "
              "that cost y dollars each. If the given equation represents this "
              "situation, which of the following is the best interpretation of {c} in "
              "this context?",
         opts=[("total", "both", "The total cost, in dollars, for all binders and "
                                 "notebooks purchased"),
               ("total", "x", "The total cost, in dollars, for all binders purchased"),
               ("total", "y", "The total cost, in dollars, for all notebooks "
                              "purchased"),
               ("diff", "both", "The difference in the total cost, in dollars, between "
                                "the number of binders and notebooks purchased")],
         why="{a}x is what the binders cost and {b}y is what the notebooks cost, and "
             "the equation sets their sum to {c}."),
    # 2 -- the perimeter of an isosceles triangle (2.12)
    dict(mode="total", display=True, head="{a}x + y = {c}", a=2, b=1, tlo=15, thi=120,
         stem="In triangle QRS, sides QR and RS each have a length of x centimeters "
              "and side SQ has a length of y centimeters. The given equation "
              "represents this situation. Which of the following is the best "
              "interpretation of {c} in this context?",
         opts=[("total", "both", "The sum of the lengths, in centimeters, of the three "
                                 "sides of the triangle"),
               ("diff", "x", "The difference, in centimeters, between the lengths of "
                             "sides QR and SQ"),
               ("diff", "y", "The difference, in centimeters, between the lengths of "
                             "sides QR and RS"),
               ("total", "x", "The length, in centimeters, of one of the two sides of "
                              "equal length")],
         why="Two sides measure x and the third measures y, so {a}x + y adds all three "
             "lengths up."),
    # 3 -- what a whole term means (2.20)
    dict(mode="term", display=False, tlo=12, thi=120, alo=2, ahi=9,
         stem="Lily made {c} cups of jam. Lily then filled x small containers and y "
              "large containers with all the jam she made. The equation {eq} "
              "represents this situation. Which is the best interpretation of {b}y in "
              "this context?",
         opts=[("amount", "y", "The total number of cups of jam in the large "
                               "containers"),
               ("amount", "x", "The total number of cups of jam in the small "
                               "containers"),
               ("count", "y", "The number of large containers Lily filled"),
               ("count", "x", "The number of small containers Lily filled")],
         why="Each large container holds {b} cups and y counts them, so multiplying the "
             "two gives the jam in the large containers alone."),
]


def interpret_constant(rng: random.Random, seed: int, *, ctx=None, a=None, b=None,
                       c=None) -> Item:
    """What the number on the right, or a whole term, stands for."""
    i = rng.randrange(len(CONST)) if ctx is None else ctx
    d = CONST[i]
    A = q(a if a is not None else d.get("a") or rng.randint(d.get("alo", 2),
                                                            d.get("ahi", 9)))
    B = q(b if b is not None else d.get("b") or rng.randint(d.get("alo", 2),
                                                            d.get("ahi", 9)))
    C = q(c if c is not None else rng.randint(d["tlo"], d["thi"]))
    if A <= 0 or B <= 0:
        raise ItemError("a count in this context is positive")
    if d["mode"] == "term" and A >= B:
        raise ItemError("the large containers have to hold more than the small ones")
    at, bt, ct = numtext(A), numtext(B), numtext(C)
    eq = std_text(A, B, C, "x", "y")
    stem = d["stem"].format(a=at, b=bt, c=ct, eq=eq)
    if d.get("display"):
        stem = d["head"].format(a=at, b=bt, c=ct) + "\n" + stem
    want = ("total", "both") if d["mode"] == "total" else ("amount", "y")
    opts = [(k, w, t.format(a=at, b=bt, c=ct)) for k, w, t in d["opts"]]
    key = next(t for k, w, t in opts if (k, w) == want)
    named = {
        ("total", "x"): "gave what one of the two terms on the left comes to, not what "
                        "the two of them come to together",
        ("total", "y"): "gave what one of the two terms on the left comes to, not what "
                        "the two of them come to together",
        ("diff", "both"): "read the plus sign between the terms as a comparison of the "
                          "two quantities",
        ("diff", "x"): "read the sum of the three lengths as a comparison of two of "
                       "them",
        ("diff", "y"): "compared the two sides the equation already says are equal",
        ("rate", "both"): "read the constant as a rate, though nothing in the equation "
                          "divides one quantity by the other",
        ("amount", "x"): "read the term as belonging to the other container size",
        ("count", "y"): "gave the number of containers, which is y alone, rather than "
                        "what they hold",
        ("count", "x"): "gave the number of the other containers rather than what they "
                        "hold",
    }
    wrong = [Mis(named[(k, w)], (t, sig(k, w))) for k, w, t in opts if (k, w) != want]
    P = {"kind": "le2_const", "mode": d["mode"], "a": [A.numerator, A.denominator],
         "b": [B.numerator, B.denominator], "c": [C.numerator, C.denominator]}
    why = d["why"].format(a=at, b=bt, c=ct)
    return text_item("le2.interpret_constant", "reading a constant term", "easy", seed,
                     stem, key, sig(*want), wrong, rng, P, why)


# ---------------------------------------------------- a point's meaning

def interpret_point(rng: random.Random, seed: int, *, mode=None, a=None, b=None, c=None,
                    px=None, py=None, perimeter=None) -> Item:
    """What an ordered pair says about the two quantities it pairs up."""
    mode = mode or rng.choice(["pair", "graph"])
    if mode == "pair":
        A = q(a if a is not None else rng.randint(3, 8))
        B = q(b if b is not None else rng.randint(3, 8))
        if A == B:
            raise ItemError("the two polygons must have different numbers of sides")
        X = q(px if px is not None else rng.randint(6, 60))
        Y = q(py if py is not None else rng.randint(6, 60))
        if X == Y:
            raise ItemError("the two counts must differ, or swapping them shows nothing")
        C = A * X + B * Y
        n1, n2 = {3: "triangles", 4: "rectangles", 5: "pentagons", 6: "hexagons",
                  7: "heptagons", 8: "octagons"}[int(A)], \
                 {3: "triangles", 4: "rectangles", 5: "pentagons", 6: "hexagons",
                  7: "heptagons", 8: "octagons"}[int(B)]
        eq = std_text(A, B, C, "x", "y")
        stem = (f"A total of {numtext(C)} paper straws of equal length were used to "
                f"construct two types of polygons: {n1} and {n2}. The {n1} and {n2} "
                f"were constructed so that no two polygons had a common side. The "
                f"equation {eq} represents this situation, where x is the number of "
                f"{n1} constructed and y is the number of {n2} constructed. What is the "
                f"best interpretation of (x, y) = ({numtext(X)}, {numtext(Y)}) in this "
                f"context?")
        xs, ys = numtext(X), numtext(Y)
        opts = [(("xy", "yn"), f"If {xs} {n1} were constructed, then {ys} {n2} were "
                               f"constructed."),
                (("xy", "total"), f"If {xs} {n1} were constructed, then {ys} paper "
                                  f"straws were used."),
                (("yx", "yn"), f"If {ys} {n1} were constructed, then {xs} {n2} were "
                               f"constructed."),
                (("yx", "total"), f"If {ys} {n1} were constructed, then {xs} paper "
                                  f"straws were used.")]
        want = ("xy", "yn")
        named = {("xy", "total"): "read the second coordinate as a number of straws, "
                                  "though y counts polygons",
                 ("yx", "yn"): "read the pair in the wrong order, taking the first "
                               "coordinate for y",
                 ("yx", "total"): "read the pair in the wrong order and the second "
                                  "coordinate as a number of straws"}
        why = (f"x is listed first, so {xs} is the number of {n1}; the pair then says "
               f"how many {n2} go with them.")
        P = {"kind": "le2_point", "mode": mode, "a": [A.numerator, A.denominator],
             "b": [B.numerator, B.denominator], "x": [X.numerator, X.denominator],
             "y": [Y.numerator, Y.denominator],
             "c": [C.numerator, C.denominator]}
        key = next(t for r, t in opts if r == want)
        wrong = [Mis(named[r], (t, sig(*r))) for r, t in opts if r != want]
        return text_item("le2.interpret_point", "reading an ordered pair", "easy", seed,
                         stem, key, sig(*want), wrong, rng, P, why)

    X = q(px if px is not None else rng.randint(2, 14))
    half = q(perimeter if perimeter is None else perimeter) / 2 if perimeter else None
    if half is None:
        Y = q(py if py is not None else rng.randint(2, 14))
        half = X + Y
    else:
        Y = half - X
    if X <= 0 or Y <= 0 or X == Y or half.denominator != 1:
        raise ItemError("the rectangle needs two different whole side lengths")
    P2 = 2 * half
    hi = int(half) + 2
    fig = coordinate_grid(0, hi, 0, hi, points=[(int(X), int(Y))],
                          segments=[((0, int(half)), (int(half), 0))], step=2)
    xs, ys = numtext(X), numtext(Y)
    stem = (f"The graph in the xy-plane models the possible combinations of length x, "
            f"in meters (m), and width y, in meters, for a rectangle with a perimeter "
            f"of {numtext(P2)} m. Which statement is the best interpretation of the "
            f"point ({xs}, {ys}) in this context?")
    opts = [(("direct", "xy"), f"The length is {xs} m, and the width is {ys} m."),
            (("direct", "yx"), f"The length is {ys} m, and the width is {xs} m."),
            (("less", "yx"), f"The length is {ys} m less than the perimeter, and the "
                             f"width is {xs} m less than the perimeter."),
            (("less", "xy"), f"The length is {xs} m less than the perimeter, and the "
                             f"width is {ys} m less than the perimeter.")]
    want = ("direct", "xy")
    named = {("direct", "yx"): "read the coordinates in the wrong order, giving the "
                               "width first",
             ("less", "yx"): "read the coordinates in the wrong order and as amounts "
                             "short of the perimeter rather than as the lengths "
                             "themselves",
             ("less", "xy"): "read each coordinate as how far the side falls short of "
                             "the perimeter rather than as the side itself"}
    why = (f"The axes are the length and the width themselves, so a point on the line "
           f"reads off directly: x = {xs} goes with y = {ys}, and the two do give a "
           f"perimeter of {numtext(P2)} m.")
    Pp = {"kind": "le2_point", "mode": mode, "x": [X.numerator, X.denominator],
          "y": [Y.numerator, Y.denominator], "p": [P2.numerator, P2.denominator]}
    key = next(t for r, t in opts if r == want)
    wrong = [Mis(named[r], (t, sig(*r))) for r, t in opts if r != want]
    return text_item("le2.interpret_point", "reading a point on a graph", "medium", seed,
                     stem, key, sig(*want), wrong, rng, Pp, why, figure=fig)
