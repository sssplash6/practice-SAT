"""A table of values, and the line behind it.

Eleven source items print a table. Four ask what equation it comes from, three
print four tables and ask which of them fits a given equation, and the rest put
a letter in one of the cells. They share a single risk: a student who reads the
table's own numbers as the slope and the intercept rather than working out the
rate of change gets an answer that looks right, so the first distractor in
every pool here is built from the table's printed numbers.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q
from math import gcd

from ....item import Item, ItemError, Mis
from ..common import (choose, ex, lin_text, numtext, point_text, q, sig, std_text,
                      text_item)

__all__ = ["table_equation", "which_table", "table_symbolic", "table_line"]


def _count(n: int) -> str:
    return {2: "two", 3: "three", 4: "four", 5: "five"}.get(n, str(n))


def _reduce(m, b):
    """y = mx + b as the whole-number Ax + By = C a source item would print."""
    m, b = q(m), q(b)
    d = m.denominator * b.denominator // gcd(m.denominator, b.denominator)
    A, B, C = (m.numerator * (d // m.denominator), -d,
               -b.numerator * (d // b.denominator))
    g = gcd(gcd(abs(A), abs(B)), abs(C)) or 1
    A, B, C = A // g, B // g, C // g
    if A < 0 or (A == 0 and B < 0):
        A, B, C = -A, -B, -C
    return q(A), q(B), q(C)


# ------------------------------------------- the equation behind a table

def table_equation(rng: random.Random, seed: int, *, form=None, m=None, b=None, x0=None,
                   step=None, rows=None, scale=None, wrongs=None) -> Item:
    """A table of inputs and outputs, and the rule that produced it."""
    form = form or rng.choice(["slope_intercept", "context", "standard"])
    rows = int(rows if rows is not None else rng.choice([3, 3, 4]))
    S = q(step) if step is not None else q(rng.choice([1, 1, 2, 3]))
    X0 = q(x0) if x0 is not None else q(rng.choice([0, 1, 1, rng.randint(-8, 6)]))
    if S <= 0 or rows < 3:
        raise ItemError("a table needs at least three rows and a rising input")

    if form == "context":
        M = q(m) if m is not None else Q(rng.randint(4, 40), rng.randint(2, 4))
        Bv = q(b) if b is not None else q(rng.randint(-20, 20))
        X0 = q(x0) if x0 is not None else S
        head = ["Side length, s (inches)", "Price, P (dollars)"]
        var, dep = "s", "P"
        lead = ("An artist paints and sells square tiles. The selling price P, in "
                "dollars, of a painted tile is a linear function of the side length of "
                "the tile s, in inches, as shown in the table below. Which of the "
                "following could define the relationship between s and P ?")
        cell = 2
    else:
        M = q(m) if m is not None else q(rng.choice([rng.randint(2, 9),
                                                     rng.randint(-9, -2)]))
        Bv = q(b) if b is not None else q(rng.randint(-40, 60))
        head = ["x", "y"]
        var, dep = "x", "y"
        cell = None
        lead = None
    xs = [X0 + S * i for i in range(rows)]
    ys = [M * x + Bv for x in xs]
    if M == 0 or Bv == 0:
        raise ItemError("the line must slope and must miss the origin")
    if form == "context" and (any(v <= 0 for v in ys) or any(v <= 0 for v in xs)):
        raise ItemError("a price and a side length are both positive")
    if form == "context" and any((100 * v).denominator != 1 for v in ys):
        raise ItemError("every price has to come out in whole cents")
    table = [list(head)] + [[numtext(x), numtext(y, "frac", cell)]
                            for x, y in zip(xs, ys)]
    dy = ys[1] - ys[0]

    if form == "standard":
        K = q(scale) if scale is not None else q(rng.randint(2, 5))
        A, B, C = _reduce(M, Bv)
        if K < 2:
            raise ItemError("the printed equation is a whole multiple of the reduced one")
        key = std_text(K * A, K * B, K * C, "x", "y")
        ks = sig("std", K * A, K * B, K * C)
        stem = (f"The table shows {_count(rows)} values of x and their corresponding "
                f"values of y. There is a linear relationship between x and y. Which of "
                f"the following equations represents this relationship?")
        wrong = [Mis("swapped the coefficients of x and y",
                     (std_text(K * B, K * A, K * C, "x", "y"),
                      sig("std", K * B, K * A, K * C))),
                 Mis("scaled the two coefficients but left the multiplier itself on the "
                     "right-hand side", (std_text(K * A, K * B, K, "x", "y"),
                                         sig("std", K * A, K * B, K))),
                 Mis("swapped the coefficients and left the multiplier on the "
                     "right-hand side", (std_text(K * B, K * A, K, "x", "y"),
                                         sig("std", K * B, K * A, K))),
                 Mis("changed the sign of the right-hand side",
                     (std_text(K * A, K * B, -K * C, "x", "y"),
                      sig("std", K * A, K * B, -K * C)))]
        P = {"kind": "le2_table_equation", "form": form,
             "xs": [[v.numerator, v.denominator] for v in xs],
             "ys": [[v.numerator, v.denominator] for v in ys],
             "k": [q(K).numerator, q(K).denominator]}
        moved = (f"rise {numtext(dy)}" if dy > 0 else f"fall {numtext(-dy)}")
        why = (f"The outputs {moved} for every {numtext(S)} that x rises, so the line "
               f"is y = {lin_text(M, Bv)}; clearing the fractions and multiplying "
               f"through by {numtext(K)} gives the equation above.")
        return text_item("le2.table_equation", "an equation from a table", "medium",
                         seed, stem, key, ks, wrong, rng, P, why, table=table)

    # the table cells print money to two places, but the options print the slope
    # and the constant the way the source does -- as plain numbers and fractions
    style, places = "frac", None

    def opt(u, v):
        return (f"{dep} = {lin_text(u, v, var, style, places)}",
                sig("line", u, v))

    key = f"{dep} = {lin_text(M, Bv, var, style, places)}"
    ks = sig("line", M, Bv)
    stem = lead or (f"The table above shows some pairs of {var} values and {dep} values. "
                    f"Which of the following equations could represent the relationship "
                    f"between {var} and {dep} ?")
    pool = {
        "step_dy": Mis("used the step in the inputs as the slope and the change in the "
                       "outputs as the constant term", opt(S, dy)),
        "first_output": Mis("used the first output as the constant term instead of the "
                            "value the line would take at zero", opt(M, ys[0])),
        "swap_neg": Mis("swapped the slope and the constant term and changed the sign "
                        "of the constant", opt(Bv, -M)),
        "out_slope": Mis("used the first output as the slope with no constant term",
                         opt(ys[0], 0)),
        "dy_slope": Mis("used the change in the outputs as the slope without dividing "
                        "by the step in the inputs", opt(dy, Bv)),
        "invm": Mis("inverted the slope, dividing the step in the inputs by the change "
                    "in the outputs", opt(1 / M, Bv)),
        "invboth": Mis("inverted both the slope and the constant term",
                       opt(1 / M, 1 / Bv)),
        "negb": Mis("changed the sign of the constant term", opt(M, -Bv)),
    }
    order = wrongs or (["step_dy", "first_output", "invboth", "invm", "negb"]
                       if form == "context" else
                       ["swap_neg", "out_slope", "dy_slope", "first_output", "negb"])
    wrong = [pool[k] for k in order if k in pool] + \
            [v for k, v in pool.items() if k not in order]
    P = {"kind": "le2_table_equation", "form": form,
         "xs": [[v.numerator, v.denominator] for v in xs],
         "ys": [[v.numerator, v.denominator] for v in ys]}
    moved = (f"rises {numtext(dy, style, places)}" if dy > 0
             else f"drops {numtext(-dy, style, places)}")
    why = (f"Each step of {numtext(S)} in {var} {moved}, which fixes the slope; running "
           f"back to {var} = 0 from the first row fixes the constant term.")
    return text_item("le2.table_equation", "an equation from a table", "easy", seed,
                     stem, key, ks, wrong, rng, P, why, table=table)


# ---------------------------------------- which table of values fits a line

def which_table(rng: random.Random, seed: int, *, form=None, m=None, b=None, A=None,
                B=None, C=None, xs=None, wrongs=None) -> Item:
    """The four options are themselves tables; each is written as its pairs."""
    form = form or rng.choice(["slope_intercept", "standard", "standard"])
    if xs is None:
        step = rng.choice([1, 2, 2, 4])
        start = rng.choice([0, 0, 1, 2])
        XS = [q(start + step * i) for i in range(3)]
    else:
        XS = [q(v) for v in xs]
    if len(XS) != 3 or len(set(XS)) != 3:
        raise ItemError("the table shows three different inputs")

    if form == "slope_intercept":
        M = q(m) if m is not None else q(rng.choice([rng.randint(2, 90),
                                                     rng.randint(-90, -2)]))
        Bv = q(b) if b is not None else q(rng.randint(2, 40))
        if M == 0 or Bv == 0 or M == Bv:
            raise ItemError("the slope and the constant term must differ and must be "
                            "there")
        eq = f"y = {lin_text(M, Bv)}"
        ys = [M * x + Bv for x in XS]
        pool = {
            "row_add": ([M + Bv * i for i in range(3)],
                        "used the coefficient of x as the value at x = 0 and then added "
                        "the constant term once for each row of the table"),
            "row_mult": ([M * (x if x != 0 else 1) for x in XS],
                         "used the coefficient of x as the value at x = 0 and then "
                         "multiplied it by each input"),
            "m_minus_b": ([(M - Bv) * x + Bv for x in XS],
                          "subtracted the constant term from the coefficient of x and "
                          "used that as the slope"),
            "swapped": ([Bv * x + M for x in XS],
                        "swapped the coefficient of x and the constant term"),
            "no_const": ([M * x for x in XS],
                         "left the constant term out altogether"),
        }
        order = wrongs or ["row_add", "row_mult", "m_minus_b", "swapped", "no_const"]
        wrong = [Mis(pool[k][1], (_pairs(XS, pool[k][0]), sig("pairs", *XS, *pool[k][0])))
                 for k in order if k in pool]
        P = {"kind": "le2_which_table", "form": form,
             "m": [M.numerator, M.denominator], "b": [Bv.numerator, Bv.denominator],
             "xs": [[v.numerator, v.denominator] for v in XS]}
        why = (f"Each input goes into y = {lin_text(M, Bv)} on its own: the coefficient "
               f"of x multiplies the input, and the constant term is added afterwards, "
               f"not once per row.")
    else:
        Ac = q(A) if A is not None else q(rng.choice(
            [rng.randint(2, 9), Q(rng.randint(1, 5), rng.randint(2, 5))]))
        Bc = q(B) if B is not None else q(rng.choice(
            [rng.randint(2, 9), rng.randint(-9, -2), Q(rng.randint(1, 5),
                                                       rng.randint(2, 5))]))
        Cc = q(C) if C is not None else q(rng.randint(-90, 90))
        if Ac <= 0 or Bc == 0 or Cc == 0:
            raise ItemError("both variables and a right-hand side are needed, and the "
                            "coefficient of x is printed positive")
        if Ac == 1 or abs(Bc) == 1:
            raise ItemError("a coefficient of one makes the substitution no work")
        if Ac == Bc:
            # ax + ay = c is symmetric in x and y, so the option that reads the
            # table the wrong way round would be a second correct answer
            raise ItemError("the two coefficients must differ, or swapping the "
                            "columns still satisfies the equation")
        eq = std_text(Ac, Bc, Cc, "x", "y")
        ys = [(Cc - Ac * x) / Bc for x in XS]
        pool = {
            "reversed": (list(reversed(ys)),
                         "paired the right y-values with the inputs in the wrong order"),
            "nodivide": ([Cc - Ac * x for x in XS],
                         "took the x term off the right-hand side but never divided by "
                         "the coefficient of y"),
            "signflip": ([(Cc + Ac * x) / Bc for x in XS],
                         "added the x term to the right-hand side instead of taking it "
                         "off"),
            "dropA": ([(Cc - x) / Bc for x in XS],
                      "took the input itself off the right-hand side rather than the "
                      "whole x term"),
        }
        order = wrongs or ["reversed", "nodivide", "signflip", "dropA"]
        wrong = [Mis(pool[k][1], (_pairs(XS, pool[k][0]), sig("pairs", *XS, *pool[k][0])))
                 for k in order if k in pool]
        swapped = _pairs(ys, XS)
        wrong.insert(1, Mis("read the table the wrong way round, taking the y-values as "
                            "the inputs", (swapped, sig("pairs", *ys, *XS))))
        wrong.insert(2, Mis("read the table the wrong way round and in the wrong order",
                            (_pairs(list(reversed(ys)), XS),
                             sig("pairs", *reversed(ys), *XS))))
        P = {"kind": "le2_which_table", "form": form,
             "A": [Ac.numerator, Ac.denominator], "B": [Bc.numerator, Bc.denominator],
             "C": [Cc.numerator, Cc.denominator],
             "xs": [[v.numerator, v.denominator] for v in XS]}
        why = (f"Each input is put into {eq} and the equation solved for y: the x term "
               f"comes off the right-hand side first, and what is left is divided by "
               f"the coefficient of y.")
    if any(abs(v) >= 1000 for v in list(XS) + list(ys)):
        raise ItemError("a table of values printed with thousands separators is a "
                        "wall of commas, not a table")
    key = _pairs(XS, ys)
    ks = sig("pairs", *XS, *ys)
    stem = eq + "\nWhich table gives three values of x and their corresponding values " \
                "of y for the given equation?"
    return text_item("le2.which_table", "matching a table to an equation", "medium",
                     seed, stem, key, ks, wrong, rng, P, why)


def _pairs(xs, ys) -> str:
    return ", ".join(point_text(x, y) for x, y in zip(xs, ys))


# ------------------------------------------ a letter in one of the cells

def table_symbolic(rng: random.Random, seed: int, *, ask=None, step=None, d=None, m=None,
                   b=None, x1=None, y1=None, x3=None, y2=None) -> Item:
    """A table whose cells carry a constant, so the arithmetic has to stay general."""
    ask = ask or rng.choice(["slope", "constants"])

    if ask == "slope":
        S = int(step if step is not None else rng.randint(2, 9))
        D = int(d if d is not None else rng.randrange(4, 300, 2))
        if S == 0 or D == 0 or S == D or D % S == 0:
            raise ItemError("the slope must stay a fraction, or it is the only option "
                            "without a division in it")
        table = [["x", "y"], [numtext(-2 * S), f"n + {numtext(2 * D)}"],
                 [numtext(-S), f"n + {numtext(D)}"], ["0", "n"]]
        stem = ("The table shows three values of x and their corresponding values of y, "
                "where n is a constant, for the linear relationship between x and y. "
                "What is the slope of the line that represents this relationship in the "
                "xy-plane?")
        key = numtext(Q(-D, S))
        ks = sig("plain", Q(-D, S))
        wrong = [Mis("inverted the slope, dividing the step in x by the change in y",
                     (numtext(Q(-S, D)), sig("plain", Q(-S, D)))),
                 Mis("divided one row's output by its own input instead of dividing the "
                     "changes", (f"(n + {numtext(D)})/({numtext(-S)})",
                                 sig("row", D, -S))),
                 Mis("subtracted the two outputs the wrong way round, leaving an n "
                     "behind", (f"(2n - {numtext(D)})/{numtext(S)}",
                                sig("twon", D, S))),
                 Mis("changed the sign of the slope",
                     (numtext(Q(D, S)), sig("plain", Q(D, S))))]
        P = {"kind": "le2_table_symbolic", "ask": ask, "step": S, "d": D}
        why = ("Between any two rows the n cancels, so only the change in the added "
               f"amount is left: y falls {numtext(D)} for every {numtext(S)} that x "
               "rises.")
        return text_item("le2.table_symbolic", "a table with a constant in it", "medium",
                         seed, stem, key, ks, wrong, rng, P, why, table=table)

    M = q(m) if m is not None else q(rng.choice([rng.randint(2, 9), rng.randint(-9, -2)]))
    X1 = q(x1) if x1 is not None else q(rng.randint(1, 10))
    Bv = (q(y1) - M * X1 if y1 is not None else
          (q(b) if b is not None else q(rng.randint(-20, 20))))
    X3 = q(x3) if x3 is not None else q(rng.randint(11, 30))
    Y2 = q(y2) if y2 is not None else M * q(rng.randint(2, 20)) + Bv
    if M == 0:
        raise ItemError("a flat line hides the slope the item states")
    K = (Y2 - Bv) / M
    N = M * X3 + Bv
    if K in (X1, X3) or K.denominator != 1 or K <= 0:
        raise ItemError("the missing input must be a whole number of its own")
    y1 = M * X1 + Bv
    table = [["x", "y"], [numtext(X1), numtext(y1)], ["k", numtext(Y2)],
             [numtext(X3), "n"]]
    stem = (f"The table above shows the coordinates of three points on a line in the "
            f"xy-plane, where k and n are constants. If the slope of the line is "
            f"{numtext(M)}, what is the value of k + n ?")
    key = K + N
    keyx = ex(key)
    if not keyx.is_rational or len(keyx.gridin()) > 6:
        raise ItemError("the answer does not fit a grid-in")
    why = (f"The first row and the stated slope already fix the line as y = "
           f"{lin_text(M, Bv)}. k is the input that line sends to {numtext(Y2)}, and n "
           f"is what it gives back at x = {numtext(X3)}.")
    P = {"kind": "le2_table_symbolic", "ask": ask, "m": [M.numerator, M.denominator],
         "x1": [X1.numerator, X1.denominator], "y1": [y1.numerator, y1.denominator],
         "y2": [Y2.numerator, Y2.denominator], "x3": [X3.numerator, X3.denominator]}
    return Item("le2.table_symbolic", "a table with a constant in it", "hard", seed,
                stem, "spr", keyx, keyx.gridin(), why, table=table, params=P)


# --------------------------------------- one more fact about the same line

def table_line(rng: random.Random, seed: int, *, ask=None, m=None, b=None, x1=None,
               x2=None, x3=None, step=None, k=None, xs=None) -> Item:
    """The table fixes a line; the question is asked somewhere else on it."""
    ask = ask or rng.choice(["value", "shift_intercept"])
    M = q(m) if m is not None else q(rng.choice([rng.randint(2, 9),
                                                 rng.randint(-9, -2)]))
    Bv = q(b) if b is not None else q(rng.randint(-40, 60))
    if M == 0 or Bv == 0:
        raise ItemError("the line must slope and must miss the origin")

    if ask == "value":
        X1 = q(x1) if x1 is not None else q(rng.randint(-25, 0))
        X2 = q(x2) if x2 is not None else q(rng.randint(1, 25))
        if X1 == X2:
            raise ItemError("the two rows must differ")
        table = [["x", "y"], [numtext(X1), numtext(M * X1 + Bv)],
                 [numtext(X2), numtext(M * X2 + Bv)]]
        X3 = q(x3) if x3 is not None else Q(1, rng.randint(2, 9))
        if X3 in (X1, X2) or X3 == 0:
            raise ItemError("the point asked about must be off the table")
        key = M * X3 + Bv
        stem = ("The table shows two values of x and their corresponding values of y. In "
                "the xy-plane, the graph of the linear equation representing this "
                f"relationship passes through the point ({numtext(X3)}, a). What is the "
                f"value of a?")
        why = (f"The two rows give a rise of {numtext(M * (X2 - X1))} over a run of "
               f"{numtext(X2 - X1)}, and running back to x = 0 from the first row gives "
               f"the constant term; x = {numtext(X3)} then follows.")
        keyx = ex(key)
        mistakes = [Mis("left the constant term out and multiplied the input by the "
                        "slope alone", ex(M * X3)),
                    Mis("gave the constant term, which is the value at x = 0 rather "
                        "than at the point asked about", ex(Bv)),
                    Mis("inverted the slope before substituting", ex(X3 / M + Bv)),
                    Mis("added the input to the constant term instead of multiplying "
                        "it by the slope", ex(X3 + Bv)),
                    Mis("divided the constant term by the input", ex(Bv / X3))]
        P = {"kind": "le2_table_line", "ask": ask, "x1": [X1.numerator, X1.denominator],
             "y1": [(M * X1 + Bv).numerator, (M * X1 + Bv).denominator],
             "x2": [X2.numerator, X2.denominator],
             "y2": [(M * X2 + Bv).numerator, (M * X2 + Bv).denominator],
             "x3": [X3.numerator, X3.denominator]}
        choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True,
                                                 fillers="shift")
        return Item("le2.table_line", "a value off the line a table defines", "hard",
                    seed, stem, "mcq", keyx, letter, why, choices, reasons, latex,
                    table=table, params=P)

    K = q(k) if k is not None else q(rng.randint(2, 20))
    if xs is None:
        S = q(step) if step is not None else q(rng.randint(2, 9))
        X1 = q(x1) if x1 is not None else q(rng.randint(2, 20))
        xs = [X1, X1 + S, X1 + S + q(rng.randint(1, 6))]
    else:
        xs = [q(v) for v in xs]
    if len(xs) != 3 or len(set(xs)) != 3:
        raise ItemError("the three rows must show different inputs")
    ys = [M * x + Bv for x in xs]
    if any(v.denominator != 1 for v in ys) or any(v.denominator != 1 for v in xs):
        raise ItemError("the printed table must hold whole numbers")
    table = [["x", "y"]] + [[numtext(x), numtext(y)] for x, y in zip(xs, ys)]
    shifted = Bv - K
    if M == 0:
        raise ItemError("a flat line has no x-intercept")
    root = -shifted / M
    if root == 0:
        raise ItemError("the translated line must miss the origin")
    stem = (f"For line h, the table shows three values of x and their corresponding "
            f"values of y. Line k is the result of translating line h down "
            f"{numtext(K)} units in the xy-plane. What is the x-intercept of line k?")
    key = point_text(root, 0)
    ks = sig("pt", root, 0)
    why = (f"The table gives line h a slope of {numtext(M)} and a constant term of "
           f"{numtext(Bv)}; sliding it down {numtext(K)} leaves the slope alone and "
           f"takes {numtext(K)} off the constant term, and the x-intercept is where "
           f"that new line reaches zero.")
    wrong = [Mis("gave the x-intercept of the original line, leaving the translation "
                 "out", (point_text(-Bv / M, 0), sig("pt", -Bv / M, 0))),
             Mis("translated the line up instead of down",
                 (point_text(-(Bv + K) / M, 0), sig("pt", -(Bv + K) / M, 0))),
             Mis("changed the sign of the x-intercept",
                 (point_text(shifted / M, 0), sig("pt", shifted / M, 0))),
             Mis("took the translation off the slope instead of off the constant term",
                 (point_text(-Bv / (M - K), 0), sig("pt", -Bv / (M - K), 0))
                 if M != K else None)]
    P = {"kind": "le2_table_line", "ask": ask,
         "xs": [[v.numerator, v.denominator] for v in xs],
         "ys": [[v.numerator, v.denominator] for v in ys],
         "k": [K.numerator, K.denominator]}
    return text_item("le2.table_line", "a translated line from a table", "hard", seed,
                     stem, key, ks, wrong, rng, P, why, table=table)
