"""Items whose line is drawn rather than written.

Every picture comes out of the same numbers as the stem, so a variation moves
the line as well as the words. Two quite different questions get asked of a
drawn line here: what its equation is, and -- when the axes are two things
bought for one fixed sum -- what the fixed sum or one of the prices must be.
The second kind is answered off the intercepts, and its wrong answers are the
intercepts combined the wrong way: multiplied together, added, or paired with
the wrong axis.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q
from math import gcd

from ....figures import coordinate_grid
from ....item import Item, ItemError, Mis
from ....plot import line_graph, scatter
from ..common import (MINUS, choose, coef_text, dec, ex, lin_text, numtext, q, sig,
                      std_text, text_item)

__all__ = ["line_from_graph", "graph_combinations"]


# ------------------------------------------- the equation of a drawn line

def line_from_graph(rng: random.Random, seed: int, *, ask=None, m=None, b=None, k=None,
                    c=None, name=None, wrongs=None, scale=None) -> Item:
    """A line on a grid: name its equation, or the function it was shifted from."""
    ask = ask or rng.choice(["equation", "equation", "parameter", "shifted"])
    name = name or rng.choice(["f", "g", "h"])

    if ask == "parameter":
        # the drawn line meets the axes at whole numbers, and one coefficient
        # of the standard form is left as a letter
        xi = int(c if c is not None else rng.choice([2, 3, 4, 5, 6, 8, 9]))
        yi = int(b if b is not None else rng.choice([3, 4, 6, 8, 9, 12]))
        if xi <= 0 or yi <= 0:
            raise ItemError("both coefficients are positive, so both intercepts are")
        K = int(scale if scale is not None else rng.randint(1, 8))
        C = abs(xi * yi) // gcd(abs(xi), abs(yi)) * K
        A, R = Q(C, xi), Q(C, yi)
        if A.denominator != 1 or R.denominator != 1 or R <= 0 or A == R:
            raise ItemError("both coefficients must be whole and the letter positive")
        lo, hi = min(xi, 0) - 2, max(xi, 0) + 2
        ylo, yhi = min(yi, 0) - 2, max(yi, 0) + 2
        if hi - lo > 22 or yhi - ylo > 22:
            raise ItemError("the drawn line would not fit a readable grid")
        fig = coordinate_grid(lo, hi, ylo, yhi, points=[(0, yi)],
                              segments=[((xi, 0), (0, yi))])
        stem = ("The graph shows a linear relationship between x and y. Which equation "
                "represents this relationship, where R is a positive constant?")
        at, ct = numtext(A), numtext(C)
        key = f"{coef_text(A, 'x')} + Ry = {ct}"
        ks = sig("param", A, C, "num_x")
        wrong = [Mis("attached the letter to x and the number to y, which swaps the two "
                     "intercepts", (f"Rx + {coef_text(A, 'y')} = {ct}",
                                    sig("param", A, C, "num_y"))),
                 Mis("changed the sign of the y term and of the right-hand side, which "
                     "puts the x-intercept on the wrong side of the origin",
                     (f"Rx {MINUS} {coef_text(A, 'y')} = {numtext(-C)}",
                      sig("param", A, -C, "neg_y"))),
                 Mis("changed the sign of the y term and of the right-hand side",
                     (f"{coef_text(A, 'x')} {MINUS} Ry = {numtext(-C)}",
                      sig("param", A, -C, "neg_num_x"))),
                 Mis("kept the right-hand side positive while negating the y term",
                     (f"{coef_text(A, 'x')} {MINUS} Ry = {ct}",
                      sig("param", A, C, "neg_num_x")))]
        P = {"kind": "le2_graph_line", "ask": ask, "xi": xi, "yi": yi, "scale": K}
        why = (f"The line crosses the x-axis at {numtext(xi)} and the y-axis at "
               f"{numtext(yi)}. Setting y = 0 leaves the x term alone, which fixes the "
               f"number in front of x; the letter has to sit with y, where it comes out "
               f"as {numtext(R)}.")
        return text_item("le2.line_from_graph", "an equation from a graph", "hard", seed,
                         stem, key, ks, wrong, rng, P, why, figure=fig)

    M = q(m) if m is not None else q(rng.choice(
        [rng.randint(1, 4), rng.randint(-4, -1), Q(1, rng.randint(2, 5)),
         Q(-1, rng.randint(2, 5))]))
    Bv = q(b) if b is not None else q(rng.randint(-9, 9))
    if M == 0 or Bv == 0:
        raise ItemError("the drawn line must slope and must miss the origin")
    den = M.denominator
    lo = -den * rng.randint(1, 3)
    hi = den * rng.randint(1, 3)
    ys = [M * lo + Bv, M * hi + Bv]
    if any(v.denominator != 1 for v in ys):
        raise ItemError("the drawn line must pass through lattice points")
    ylo, yhi = min(int(ys[0]), int(ys[1]), 0) - 1, max(int(ys[0]), int(ys[1]), 0) + 1
    if hi - lo > 22 or yhi - ylo > 22:
        raise ItemError("the drawn line would not fit a readable grid")
    fig = coordinate_grid(min(lo, 0) - 1, max(hi, 0) + 1, ylo, yhi,
                          segments=[((lo, int(ys[0])), (hi, int(ys[1])))])

    if ask == "shifted":
        K = q(k) if k is not None else q(rng.randint(2, 20))
        if K == 0:
            raise ItemError("a shift of nothing is no shift")
        fb = Bv - K
        stem = (f"The graph of y = {name}(x) + {numtext(K)} is shown. Which equation "
                f"defines function {name}?")
        key = f"{name}(x) = {lin_text(M, fb)}"
        ks = sig("fn", M, fb)
        wrong = [Mis("added the shift to the drawn constant term instead of taking it "
                     "off", (f"{name}(x) = {lin_text(M, Bv + K)}", sig("fn", M, Bv + K))),
                 Mis("read the drawn constant term as the function's own, leaving the "
                     "shift out", (f"{name}(x) = {lin_text(M, Bv)}", sig("fn", M, Bv))),
                 Mis("used the shift itself as the constant term",
                     (f"{name}(x) = {lin_text(M, -K)}", sig("fn", M, -K))),
                 Mis("took the shift off the slope instead of off the constant term",
                     (f"{name}(x) = {lin_text(M - K, Bv)}", sig("fn", M - K, Bv)))]
        P = {"kind": "le2_graph_line", "ask": ask, "m": [M.numerator, M.denominator],
             "b": [Bv.numerator, Bv.denominator], "k": [K.numerator, K.denominator]}
        why = (f"The line drawn is y = {lin_text(M, Bv)}, and that is already "
               f"{numtext(K)} higher than {name}, so {name} keeps the same slope and "
               f"sits {numtext(K)} lower.")
        return text_item("le2.line_from_graph", "a shifted graph", "hard", seed, stem,
                         key, ks, wrong, rng, P, why, figure=fig)

    stem = rng.choice([
        "Which of the following is an equation of the graph shown in the xy-plane "
        "above?",
        "What is the equation of the line shown in the xy-plane above?",
        "What is an equation of the graph shown?"]) if wrongs is None else \
        "What is an equation of the graph shown?"
    key = f"y = {lin_text(M, Bv)}"
    ks = sig("line", M, Bv)
    unit = q(1) if M > 0 else q(-1)

    def opt(u, v):
        return (f"y = {lin_text(u, v)}", sig("line", u, v))

    pool = {
        "invm": Mis("inverted the slope, counting the run for every one up instead of "
                    "the rise for every one along", opt(1 / M, Bv)),
        "swapinv": Mis("swapped the slope and the y-intercept and inverted the slope "
                       "along the way", opt(Bv, 1 / M)),
        "swap": Mis("swapped the slope and the y-intercept", opt(Bv, M)),
        "unit": Mis("read the slope as one down for every one along and wrote the true "
                    "slope as the constant term", opt(unit, M)),
        "negboth": Mis("changed the sign of both the slope and the y-intercept",
                       opt(-M, -Bv)),
        "inv_negboth": Mis("inverted the slope and changed the sign of both numbers",
                           opt(-1 / M, -Bv)),
        "double": Mis("counted the rise over two units along without halving it",
                      opt(2 * M, Bv)),
        "negm": Mis("read the line as rising where it falls", opt(-M, Bv)),
        "neg_double": Mis("doubled the slope and read the line as rising where it "
                          "falls", opt(-2 * M, Bv)),
    }
    order = wrongs or ["invm", "swapinv", "swap", "negboth", "inv_negboth", "double",
                       "negm", "neg_double", "unit"]
    wrong = [pool[nm] for nm in order if nm in pool] + \
            [mm for nm, mm in pool.items() if nm not in order]
    P = {"kind": "le2_graph_line", "ask": "equation",
         "m": [M.numerator, M.denominator], "b": [Bv.numerator, Bv.denominator],
         "seg": [[lo, int(ys[0])], [hi, int(ys[1])]]}
    why = (f"The line meets the y-axis at {numtext(Bv)}, and from there it moves "
           f"{numtext(M.numerator)} up for every {numtext(M.denominator)} along.")
    return text_item("le2.line_from_graph", "an equation from a graph", "easy", seed,
                     stem, key, ks, wrong, rng, P, why, figure=fig)


# ------------------------------- what a fixed sum buys, read off a graph

COMBO = [
    # 0 -- pounds of two fruits for one fixed sum (1.9)
    dict(ask="value", xlabel="Pounds of tangerines", ylabel="Pounds of lemons",
         xlo=4, xhi=12, ylo=4, yhi=26, cmax=60,
         stem="The graph shows the possible combinations of the number of pounds of "
              "tangerines and lemons that could be purchased for ${c} at a certain "
              "store. If Melvin purchased lemons and {x} pounds of tangerines for a "
              "total of ${c}, how many pounds of lemons did he purchase?",
         why="Spent on lemons alone the ${c} buys {yi} pounds, so a pound of "
             "tangerines costs what {ratio} pounds of lemons cost; {x} pounds of "
             "tangerines uses up {used} pounds' worth."),
    # 1 -- which equation the drawn line represents (2.17)
    dict(ask="equation", xlabel="Number of T-shirts", ylabel="Number of sweatshirts",
         xlo=40, xhi=120, ylo=20, yhi=60, xstep=5, ystep=5, cmax=2400,
         stem="The graph models the relationship between the number of T-shirts, x, and "
              "the number of sweatshirts, y, that Kira can purchase for a school "
              "fundraiser. Which equation could represent this relationship?",
         why="The same money buys {xi} T-shirts or {yi} sweatshirts, so {xi} T-shirts "
             "cost what {yi} sweatshirts cost; the smallest whole numbers in that "
             "ratio are {a} for each T-shirt and {b} for each sweatshirt, against a "
             "budget of {c}."),
    # 2 -- the total earned, from the two hourly rates (3.7)
    dict(ask="total", xlabel="Number of hours at job A",
         ylabel="Number of hours at job B", xlo=8, xhi=40, ylo=4, yhi=20,
         stem="To earn money for college, Avery works two part-time jobs: A and B. She "
              "earns ${a} per hour working at job A and ${b} per hour working at job B. "
              "In one week, Avery earned a total of s dollars for working at the two "
              "part-time jobs. The graph above represents all possible combinations of "
              "numbers of hours Avery could have worked at the two jobs to earn s "
              "dollars. What is the value of s ?",
         why="Working only at job A means {xi} hours at ${a}, and working only at job B "
             "means {yi} hours at ${b}; both ends of the line have to come to the same "
             "week's pay."),
    # 3 -- the price of one item, from plotted whole-number combinations (3.4)
    dict(ask="unit_price", xlabel="Number of cornflowers",
         ylabel="Number of wallflowers", scatter=True, xlo=6, xhi=24, ylo=6, yhi=24,
         stem="The points plotted in the coordinate plane above represent the possible "
              "numbers of wallflowers and cornflowers that someone can buy at the "
              "Garden Store in order to spend exactly ${c} total on the two types of "
              "flowers. The price of each wallflower is the same and the price of each "
              "cornflower is the same. What is the price, in dollars, of 1 cornflower?",
         why="The point furthest along the horizontal axis is the one where the whole "
             "${c} went on cornflowers: {xi} of them and no wallflowers at all."),
]


def graph_combinations(rng: random.Random, seed: int, *, ctx=None, xi=None, yi=None,
                       total=None, x=None, fmt=None) -> Item:
    """A line, or a row of points, showing what one fixed sum can buy."""
    i = rng.randrange(len(COMBO)) if ctx is None else ctx
    d = COMBO[i]
    XI = int(xi if xi is not None else rng.randrange(d["xlo"], d["xhi"] + 1,
                                                    d.get("xstep", 1)))
    YI = int(yi if yi is not None else rng.randrange(d["ylo"], d["yhi"] + 1,
                                                    d.get("ystep", 1)))
    if XI <= 1 or YI <= 1 or XI == YI:
        raise ItemError("the two intercepts must differ and must be more than one")
    step = XI * YI // gcd(XI, YI)                 # the smallest whole-number total
    if step > d.get("cmax", 10 ** 9):
        raise ItemError("the smallest whole-number total is implausibly large")
    A, B = Q(step, XI), Q(step, YI)

    if d["ask"] == "value":
        C = q(total) if total is not None else q(step)
        pa, pb = C / XI, C / YI
        X = q(x) if x is not None else q(rng.randint(2, max(2, XI - 1)))
        if not (0 < X < XI):
            raise ItemError("the reading has to be taken between the two intercepts")
        key = (C - pa * X) / pb
        if key.denominator != 1 or key <= 0:
            raise ItemError("the reading has to land on a whole number of pounds")
        fig = line_graph([(0, YI), (XI, 0)], d["xlabel"], d["ylabel"])
        stem = d["stem"].format(c=numtext(C), x=numtext(X))
        why = d["why"].format(c=numtext(C), yi=numtext(YI), x=numtext(X),
                              key=numtext(key), ratio=numtext(pa / pb),
                              used=numtext(YI - key))
        keyx = ex(key)
        mistakes = [Mis("took the pounds of tangerines straight off the lemons, as "
                        "though a pound of each cost the same", ex(YI - X)),
                    Mis("read the stated amount off the other axis, as pounds of "
                        "lemons, and answered with the tangerines",
                        ex((C - pb * X) / pa) if (C - pb * X) / pa > 0 else None),
                    Mis("read the value where the line meets the vertical axis, which "
                        "is what the whole sum buys of one kind alone", ex(YI)),
                    Mis("read the value where the line meets the horizontal axis",
                        ex(XI)),
                    Mis("gave the number of pounds the question already states", ex(X)),
                    Mis("added the two amounts instead of reading the line", ex(YI + X))]
        mistakes = [m for m in mistakes if m.value is not None]
        P = {"kind": "le2_combo", "ask": d["ask"], "xi": XI, "yi": YI,
             "c": [C.numerator, C.denominator], "x": [X.numerator, X.denominator]}
        choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True,
                                                 fillers="shift")
        return Item("le2.graph_combinations", "reading a combinations graph", "easy",
                    seed, stem, "mcq", keyx, letter, why, choices, reasons, latex,
                    figure=fig, params=P)

    if d["ask"] == "equation":
        fig = line_graph([(0, YI), (XI, 0)], d["xlabel"], d["ylabel"])
        stem = d["stem"]
        key = std_text(A, B, step, "x", "y")
        ks = sig("std", A, B, step)
        wrong = [Mis("read the two coefficients as a slope and a y-intercept",
                     (f"y = {lin_text(A, B)}", sig("line", A, B))),
                 Mis("read the two coefficients as a slope and a y-intercept, the wrong "
                     "way round", (f"y = {lin_text(B, A)}", sig("line", B, A))),
                 Mis("attached each price to the other kind of garment",
                     (std_text(B, A, step, "x", "y"), sig("std", B, A, step))),
                 Mis("scaled only one side of the equation",
                     (std_text(A, B, XI + YI, "x", "y"), sig("std", A, B, XI + YI)))]
        P = {"kind": "le2_combo", "ask": d["ask"], "xi": XI, "yi": YI}
        why = d["why"].format(xi=numtext(XI), yi=numtext(YI), a=numtext(A),
                              b=numtext(B), c=numtext(step))
        return text_item("le2.graph_combinations", "an equation from a combinations "
                         "graph", "medium", seed, stem, key, ks, wrong, rng, P, why,
                         figure=fig)

    if d["ask"] == "total":
        pa = q(total) if total is not None else q(rng.randrange(5, 35, 5))
        key = pa * XI
        pb = key / YI
        if pb.denominator != 1 or pb == pa or pb > 60:
            raise ItemError("both hourly rates must be whole dollars and must differ")
        fig = line_graph([(0, YI), (XI, 0)], d["xlabel"], d["ylabel"])
        stem = d["stem"].format(a=numtext(pa), b=numtext(pb))
        why = d["why"].format(xi=numtext(XI), yi=numtext(YI), a=numtext(pa),
                              b=numtext(pb))
        keyx = ex(key)
        mistakes = [Mis("multiplied the two intercepts together instead of pricing "
                        "either of them", ex(XI * YI)),
                    Mis("multiplied the two hourly rates together", ex(pa * pb)),
                    Mis("added what each end of the line is worth instead of seeing "
                        "that they are the same week's pay", ex(pa * XI + pb * YI)),
                    Mis("priced the hours at job A at job B's rate", ex(pb * XI)),
                    Mis("priced the hours at job B at job A's rate", ex(pa * YI))]
        P = {"kind": "le2_combo", "ask": d["ask"], "xi": XI, "yi": YI,
             "rate": [pa.numerator, pa.denominator]}
        choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True,
                                                 fillers="shift")
        return Item("le2.graph_combinations", "a total from a combinations graph",
                    "hard", seed, stem, "mcq", keyx, letter, why, choices, reasons,
                    latex, figure=fig, params=P)

    # ask == "unit_price": whole-number combinations plotted as points
    n = gcd(XI, YI)
    if n < 3 or n > 6:
        raise ItemError("the plot needs a handful of whole-number combinations")
    C = q(total) if total is not None else Q(step * rng.choice([1, 2, 4]), 4)
    pa, pw = C / XI, C / YI
    if not (Q(1, 4) <= pa <= 5 and Q(1, 4) <= pw <= 5) or pa == pw:
        raise ItemError("both prices must be plausible and must differ")
    if (pa * 100).denominator != 1 or (pw * 100).denominator != 1:
        raise ItemError("the prices have to come out in whole cents")
    pts = [(XI * j // n, YI - YI * j // n) for j in range(n + 1)]
    fig = scatter(pts, d["xlabel"], d["ylabel"])
    stem = d["stem"].format(c=dec(C, 2))
    why = d["why"].format(c=dec(C, 2), xi=numtext(XI))
    keyx = ex(pa)
    if not keyx.is_rational or len(keyx.gridin()) > 6:
        raise ItemError("the price does not fit a grid-in")
    P = {"kind": "le2_combo", "ask": d["ask"], "xi": XI, "yi": YI,
         "c": [C.numerator, C.denominator]}
    return Item("le2.graph_combinations", "a price from a combinations graph", "hard",
                seed, stem, "spr", keyx, keyx.gridin(), why, figure=fig, params=P)
