"""Solving a linear equation in one variable, in the five ways the source asks.

  SOLVE        the equation is already gathered; find the unknown
  DISTRIBUTE   a bracket has to be expanded before it is gathered
  THEN_VALUE   solve, then evaluate a different expression in the unknown
  CHUNK        the unknown appears only inside a repeated bracket
  RECIPROCAL   x is given as a quotient and the reciprocal quotient is asked

The distractors are the ones College Board actually printed: the number on the
right reported unchanged, the constant moved without changing its sign, the
coefficient multiplied rather than divided, the bracket left half expanded.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis
from . import forms
from .kit import (VARS, choices, dec, eq_of, griddable, num, over, paren,
                  pick, sent, side, sign_join, spr_mistakes, term)

__all__ = ["solve", "distribute", "then_value", "chunk", "reciprocal"]

SOLVE_SHAPES = ["standard", "over", "split"]
DIST_SHAPES = ["sum_left", "paren_right", "two_paren", "paren_sum", "paren_both"]
SOLVE_FRAMES = ["displayed", "above", "of_above", "satisfies", "solution_to",
                "value_solution", "for_what", "if_value"]


def _shown_rhs(shape: str, p: dict):
    """The bare number printed on the right, when there is one."""
    if shape in ("over", "split", "sum_left"):
        return Q(p["d"])
    if shape == "standard" and Q(p.get("c", 0)) == 0:
        return Q(p["d"])
    return None


def _stem(frame: str, eq: str, v: str) -> str:
    from .kit import frame_stem
    return frame_stem(frame, eq, v)


# ------------------------------------------------------------------ mistakes

def _solve_mistakes(shape: str, p: dict, A: Q, C: Q, key: Q) -> dict[str, Mis]:
    """The wrong values a student actually produces when solving for the unknown.

    A named pool rather than a list, so a source item can ask for the three
    College Board printed instead of taking whichever three `assemble` happens
    to prefer. See TOPIC-GUIDE, "Naming the distractors a source item printed".
    """
    g = lambda k, d=0: Q(p.get(k, d))                                   # noqa: E731
    D = _shown_rhs(shape, p)
    M: list[tuple[str, Mis]] = []

    if shape == "over":
        a, den = g("a"), g("den", 1)
        M += [("times_coefficient",
               Mis("multiplied by the fraction instead of dividing by it", C * A)),
              ("add_numerator",
               Mis("added the numerator to the right side instead of dividing", C + a)),
              ("sub_denominator",
               Mis("subtracted the denominator instead of multiplying by it", C - den)),
              ("over_numerator",
               Mis("divided by the numerator but never multiplied by the denominator",
                   C / a)),
              ("times_denominator",
               Mis("multiplied by the denominator but never divided by the numerator",
                   C * den))]
    elif shape == "split":
        f1, f2 = g("f1"), g("f2")
        d1, d2 = Q(1) / f1, Q(1) / f2
        M += [("combined_coefficient",
               Mis("reported the combined coefficient instead of the value of the "
                   "unknown", A)),
              ("denominator_difference",
               Mis("subtracted the denominators instead of finding a common "
                   "denominator", C * (d1 - d2) if d1 != d2 else None)),
              ("second_coefficient",
               Mis("divided by the second coefficient only", C / f2)),
              ("coefficient_sum",
               Mis("added the two coefficients instead of subtracting them",
                   C / (f1 + f2) if f1 + f2 else None)),
              # The shape prints as a subtraction, so the two terms a student
              # may work with alone carry different signs: the coefficient of
              # the second one is negative. Whichever term is kept, dividing by
              # its coefficient lands on the key's own side of zero for one of
              # the two -- so a negative key always has a plain negative among
              # the wrong answers and is never the only minus sign on the page.
              ("subtracted_term",
               Mis("divided by the coefficient of the subtracted term, keeping its "
                   "minus sign, and ignored the first term", C / -f2)),
              ("first_term",
               Mis("divided by the coefficient of the first term and ignored the "
                   "term subtracted from it", C / f1))]
    elif g("b") == 0 and shape == "standard" and D is not None:
        M += [("sub_coefficient",
               Mis("subtracted the coefficient instead of dividing by it", C - A)),
              ("add_coefficient",
               Mis("added the coefficient instead of dividing by it", C + A)),
              ("times_coefficient",
               Mis("multiplied by the coefficient instead of dividing by it", C * A)),
              ("right_side",
               Mis("reported the number on the right side of the equation", D))]
    else:
        b = g("b")
        if D is not None:
            M += [("add_constant",
                   Mis("added the constant instead of subtracting it when moving it "
                       "across the equals sign", (D + b) / A)),
                  ("sub_coefficient",
                   Mis("subtracted the coefficient instead of dividing by it", C - A)),
                  ("right_side",
                   Mis("reported the number on the right side of the equation", D)),
                  ("no_divide",
                   Mis("forgot to divide by the coefficient of the unknown", C)),
                  ("constant_over_coefficient",
                   Mis("divided the constant by the coefficient and stopped",
                       b / A if A else None)),
                  # Dividing by the coefficient is the step a student remembers;
                  # clearing the constant first is the one they skip. The answer
                  # then takes its sign from the coefficient, as the key does,
                  # which is what a negative key needs beside it on the page
                  # when multiplying by the coefficient lands back on the key.
                  ("divide_before_moving",
                   Mis("divided the right side by the coefficient without first "
                       "moving the constant across", D / A))]
        else:
            M += [("no_divide",
                   Mis("forgot to divide by the coefficient of the unknown", C)),
                  ("sign_flip",
                   Mis("changed the sign when moving a term across the equals sign",
                       -key)),
                  ("times_coefficient",
                   Mis("multiplied by the coefficient instead of dividing by it", C * A))]
    if shape != "split":
        M += [("times_coefficient",
               Mis("multiplied by the coefficient instead of dividing by it", C * A)),
              ("sign_flip",
               Mis("changed the sign when moving a term across the equals sign", -key)),
              ("reciprocal",
               Mis("divided the coefficient by the constant instead of the other way "
                   "round", Q(1) / key if key else None))]
    if shape == "standard" and g("c") != 0:
        M.insert(0, ("added_variable_terms",
                     Mis("added the two variable terms instead of subtracting one from "
                         "the other", C / (g("a") + g("c")) if g("a") + g("c") else None)))
    return {n: m for n, m in M if m.value is not None}


def _dist_mistakes(shape: str, p: dict, A: Q, C: Q, key: Q,
                   gridin: bool = False) -> list[Mis]:
    """The extra ways a bracket goes wrong, on top of the ordinary ones.

    A grid-in names the mistake behind the exact value typed, so it leaves out
    a value that needs a second, unnamed slip to reach.
    """
    g = lambda k, d=0: Q(p.get(k, d))                                   # noqa: E731
    M: list[Mis] = []
    part = _partial(shape, p)          # coefficient distributed to the first term only
    if shape == "sum_left":
        M += [Mis("forgot to divide by the combined coefficient of the unknown", C),
              # d - c, never divided by A
              Mis("subtracted the number inside the parentheses from the total instead "
                  "of the product", None if gridin else g("d") - g("c")),
              Mis("reported the combined coefficient of the unknown rather than its value", A),
              Mis("multiplied only the unknown by the coefficient outside the "
                  "parentheses", part)]
    elif shape == "paren_right":
        M += [Mis("reported the number inside the parentheses", g("d")),
              Mis("multiplied only the unknown by the coefficient outside the "
                  "parentheses", part),
              Mis("changed the sign when moving a term across the equals sign", -key),
              Mis("forgot to divide by the combined coefficient of the unknown", C)]
    else:
        M += [Mis("multiplied only the unknown by the coefficient outside the "
                  "parentheses", part),
              Mis("forgot to divide by the combined coefficient of the unknown", C),
              Mis("changed the sign when moving a term across the equals sign", -key)]
    M += [Mis("multiplied by the combined coefficient instead of dividing by it", C * A),
          Mis("reported the combined coefficient of the unknown rather than its value", A),
          Mis("moved the constant across the equals sign without changing its sign",
              _kept_sign(shape, p, A, C))]
    return [m for m in M if m.value is not None]


def _kept_sign(shape: str, p: dict, A: Q, C: Q):
    """Solving after moving the left-hand constant across without negating it.

    The classic sign error, and the one wrong answer of this family that keeps
    the key's own denominator: the coefficient is gathered correctly, only the
    constant is wrong, so the answer is a fraction over the same A the key is
    over. Every other mistake here lands on a whole number or on -key, which is
    why a fractional key used to be the only option of its shape on the page.

    `two_paren` is left out: its whole constant is the term being moved, so
    keeping its sign is exactly -key, which the pool already names.
    """
    g = lambda k, d=0: Q(p.get(k, d))                                   # noqa: E731
    if A == 0:
        return None
    if shape == "sum_left":                 # a*v + b(v + c) = d
        moved = -g("b") * g("c")
    elif shape == "paren_right":            # a*v + b = c(v + d) + e
        moved = -g("b")
    elif shape == "paren_sum":              # a(b*v + c) + d*v = e + f*v
        moved = -g("a") * g("c")
    elif shape == "paren_both":             # a(b*v + c) + d = e(v + f) + g
        moved = -g("d") - g("a") * g("c")
    else:
        return None
    if moved == 0:
        return None
    return (C - 2 * moved) / A


def _partial(shape: str, p: dict):
    """Solving after distributing the coefficient to the first term only."""
    g = lambda k, d=0: Q(p.get(k, d))                                   # noqa: E731
    try:
        if shape == "sum_left":                 # a*v + b*v + c = d
            return (g("d") - g("c")) / (g("a") + g("b"))
        if shape == "paren_right":              # a*v + b = c*v + d + e
            return (g("d") + g("e") - g("b")) / (g("a") - g("c"))
        if shape == "two_paren":                # a*v + b + c*v + d = e*v
            return -(g("b") + g("d")) / (g("a") + g("c") - g("e"))
        if shape == "paren_sum":                # a*b*v + c + d*v = e + f*v
            return (g("e") - g("c")) / (g("a") * g("b") + g("d") - g("f"))
        if shape == "paren_both":               # a*b*v + c + d = e*v + f + g
            return (g("f") + g("g") - g("d") - g("c")) / (g("a") * g("b") - g("e"))
    except ZeroDivisionError:
        return None
    return None


# --------------------------------------------------------------------- SOLVE

def _build_solve(rng, seed, shape, p, var, frame, fmt, decimal, mistakes,
                 template, difficulty, skill, kind, dec_opts=False) -> Item:
    forms.nice(shape, p)
    A, C = forms.collapse(shape, p)
    key = C / A
    eq = forms.render(shape, p, var, decimal)
    stem = _stem(frame, eq, var)
    P = {"kind": kind, "shape": shape, "p": forms.params_of(shape, p)}
    rationale = (f"{eq} gathers to {term(A, var)} = {num(C)}, "
                 f"so {var} = {num(key)}.")
    ex = E(key)
    if fmt == "spr":
        return Item(template, skill, difficulty, seed, stem, "spr", ex,
                    ex.gridin(), rationale, params=P,
                    spr_mistakes=spr_mistakes(ex, mistakes))
    fv = (lambda v: dec(v.coef)) if dec_opts else None
    ch, tex, why, letter = choices(ex, mistakes, rng, fmt_value=fv)
    return Item(template, skill, difficulty, seed, stem, "mcq", ex, letter,
                rationale, ch, why, tex, params=P)


def solve(rng: random.Random, seed: int, *, shape=None, var=None, frame=None,
          fmt=None, decimal=False, dec_opts=False, wrongs=None, **kw) -> Item:
    """A gathered linear equation, solved for its unknown."""
    shape = shape or rng.choice(SOLVE_SHAPES)
    var = var or rng.choice(VARS)
    frame = frame or rng.choice(SOLVE_FRAMES)
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    p = kw if kw else forms.draw_shape(rng, shape)
    forms.nice(shape, p)
    A, C = forms.collapse(shape, p)
    key = C / A
    if key == 0:
        raise ItemError("a zero solution makes half the distractors collapse")
    mistakes = pick(_solve_mistakes(shape, p, A, C, key), wrongs)
    if fmt == "spr" and not griddable(key):
        raise ItemError("this grid-in answer would not be enterable")
    return _build_solve(rng, seed, shape, p, var, frame, fmt, decimal, mistakes,
                        f"lin1.solve.{shape}", "easy", "linear equation",
                        "lin1_solve", dec_opts)


def distribute(rng: random.Random, seed: int, *, shape=None, var=None, frame=None,
               fmt=None, decimal=False, **kw) -> Item:
    """A linear equation with a bracket that has to be expanded first."""
    shape = shape or rng.choice(DIST_SHAPES)
    var = var or rng.choice(VARS)
    frame = frame or rng.choice(SOLVE_FRAMES)
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    p = kw if kw else forms.draw_shape(rng, shape)
    forms.nice(shape, p)
    A, C = forms.collapse(shape, p)
    key = C / A
    if key == 0:
        raise ItemError("a zero solution makes half the distractors collapse")
    if fmt == "spr" and not griddable(key, loose=decimal):
        raise ItemError("this grid-in answer would not be enterable")
    mistakes = _dist_mistakes(shape, p, A, C, key, gridin=fmt == "spr")
    return _build_solve(rng, seed, shape, p, var, frame, fmt, decimal, mistakes,
                        f"lin1.distribute.{shape}", "medium", "linear equation",
                        "lin1_distribute")


# ---------------------------------------------------------------- THEN_VALUE

def then_value(rng: random.Random, seed: int, *, shape=None, var=None, m=None, k=None,
               fmt=None, frame="if_value", cf_expr=False, decimal=False, **kw) -> Item:
    """Solve the equation, then evaluate m*v + k -- the source's commonest ask."""
    shape = shape or rng.choice(["standard", "standard", "over", "paren_sum", "paren_both"])
    var = var or rng.choice(VARS)
    fmt = fmt or ("spr" if rng.random() < 0.3 else "mcq")
    p = kw if kw else forms.draw_shape(rng, shape)
    forms.nice(shape, p)
    A, C = forms.collapse(shape, p)
    x0 = C / A
    m = Q(rng.choice([2, 3, 4, 5, 6, 8, 9, 10, 12, 15])) if m is None else Q(m)
    k = Q(rng.randint(-20, 20)) if k is None else Q(k)
    if m == 0:
        raise ItemError("the asked expression must still contain the unknown")
    key = m * x0 + k
    if key == x0 or key == 0:
        raise ItemError("the asked expression is the unknown itself")
    if fmt == "spr" and not griddable(key):
        raise ItemError("this grid-in answer would not be enterable")

    expr = side(m, k, var, const_first=cf_expr, decimal=decimal)
    eq = forms.render(shape, p, var, decimal)
    if frame == "if_value":
        stem = sent(f"If {eq}, what is the value of {expr}?")
    else:
        stem = sent(f"{eq} If {var} is the solution to the equation above, "
                    f"what is the value of {expr}?")
    P = {"kind": "lin1_then_value", "shape": shape, "p": forms.params_of(shape, p),
         "m": float(m), "k": float(k)}
    rationale = (f"{eq} gives {var} = {num(x0)}, so {expr} = {num(key)}.")
    ex = E(key)
    mistakes = _then_mistakes(p, shape, A, C, x0, m, k, expr, var)
    if fmt == "spr":
        return Item("lin1.then_value", "linear equation", "easy", seed, stem, "spr",
                    ex, ex.gridin(), rationale, params=P,
                    spr_mistakes=spr_mistakes(ex, mistakes))
    ch, tex, why, letter = choices(ex, mistakes, rng)
    return Item("lin1.then_value", "linear equation", "medium", seed, stem, "mcq",
                ex, letter, rationale, ch, why, tex, params=P)


def _then_mistakes(p, shape, A, C, x0, m, k, expr, var) -> list[Mis]:
    D = _shown_rhs(shape, p)
    r = m / A if A else None
    b = Q(p.get("b", 0))
    named_x0 = Mis(f"solved for {var} but the question asked for {expr}", x0)
    used_x0 = Mis(f"used {var} in place of the whole expression", x0 + k)
    if k == 0 and r is not None and r != 1:
        M = [Mis("multiplied the unknown by the ratio of the two coefficients "
                 "instead of by the new one", r * x0),
             Mis("added the ratio of the coefficients instead of multiplying by it",
                 x0 + r),
             Mis("applied the ratio to the number on the right instead of to the "
                 "expression", D + r if D is not None else None),
             named_x0,
             Mis("reported the number on the right side of the equation", D)]
    elif r is not None and r != 1 and b == 0:
        M = [used_x0,
             Mis("left the constant term out of the expression", m * x0),
             Mis("multiplied by the coefficient a second time", m * m * x0 + k),
             named_x0,
             Mis("reported the number on the right side of the equation", D)]
    elif r is not None and r != 1:
        # the asked expression is a multiple of the given one, so the wrong
        # routes stay in its own arithmetic: scaling the wrong way, or stopping
        M = [named_x0,
             Mis("divided the number on the right by the ratio instead of "
                 "multiplying by it", D / r if D is not None else None),
             used_x0,
             Mis("left the constant term out of the expression", m * x0)]
    else:
        M = [named_x0,
             used_x0,
             Mis("applied the constant to the number on the right instead of to the "
                 "expression", D - k if D is not None else None),
             Mis("subtracted the constant instead of adding it", m * x0 - k),
             Mis("reported the number on the right side of the equation", D),
             Mis("left the constant term out of the expression", m * x0),
             Mis("changed the sign of the whole expression", -(m * x0 + k))]
    return [mm for mm in M if mm.value is not None]


# --------------------------------------------------------------------- CHUNK

CHUNK_SHAPES = ["two_left", "two_sides", "single_right"]


def chunk(rng: random.Random, seed: int, *, shape=None, var=None, ask=None, a=None,
          b=None, c=None, d=None, e=None, fmt=None, frame=None) -> Item:
    """The unknown only ever appears inside (v + c), so the bracket is the unknown."""
    shape = shape or rng.choice(CHUNK_SHAPES)
    var = var or rng.choice(VARS)
    ask = ask or rng.choice(["chunk", "chunk", "var", "term"])
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    c = Q(rng.choice([i for i in range(-12, 13) if i]) if c is None else c)
    if c == 0:
        raise ItemError("an empty bracket is not a chunk")
    inner = side(1, c, var)

    if shape == "two_left":                     # a(v+c) + b(v+c) = d
        a = Q(rng.choice([2, 3, 4, 5, 6, 7, 8]) if a is None else a)
        b = Q(rng.choice([i for i in (-9, -8, -7, -5, -4, -3, -2, 2, 3, 4, 5, 6, 7)])
              if b is None else b)
        d = Q(rng.choice([i for i in range(-40, 41) if i]) if d is None else d)
        if a + b == 0:
            raise ItemError("the bracket cancels")
        u, coef = d / (a + b), a + b
        lhs = sign_join([paren(a, inner), paren(b, inner)])
        eq = eq_of(lhs, num(d))
        wrong_coef = a - b
    elif shape == "two_sides":                  # a(v+c) = b(v+c) + d
        a = Q(rng.choice([3, 4, 5, 6, 7, 8, 9]) if a is None else a)
        b = Q(rng.choice([2, 3, 4, 5, 6, 7, 8]) if b is None else b)
        d = Q(rng.choice([i for i in range(-40, 41) if i]) if d is None else d)
        if a == b:
            raise ItemError("the bracket cancels")
        u, coef = d / (a - b), a - b
        eq = eq_of(paren(a, inner), sign_join([paren(b, inner), num(d)]))
        wrong_coef = a + b
    else:                                       # e = d + a(v+c)
        a = Q(rng.choice([2, 3, 4, 5, 6, 7, 8]) if a is None else a)
        d = Q(rng.randint(-30, 40) if d is None else d)
        e = Q(rng.choice([i for i in range(-60, 81) if i]) if e is None else e)
        if e == d:
            raise ItemError("the bracket would be zero")
        u, coef = (e - d) / a, a
        eq = eq_of(num(e), sign_join([num(d), paren(a, inner)]))
        wrong_coef = None
    v0 = u - c
    key = {"chunk": u, "var": v0, "term": coef * u}[ask]
    asked = {"chunk": inner, "var": var, "term": paren(coef, inner)}[ask]
    if key == 0 or v0 == 0 or u == 0:
        raise ItemError("a zero here collapses the distractors")
    frame = frame or rng.choice(["if_value", "displayed"])
    if ask == "var" and frame == "displayed":
        stem = sent(f"{eq} What value of {var} is the solution to the given equation?")
    elif frame == "displayed":
        stem = sent(f"{eq} What is the value of {asked}?")
    else:
        stem = sent(f"If {eq}, what is the value of {asked}?")
    if fmt == "spr" and not griddable(key):
        raise ItemError("this grid-in answer would not be enterable")

    P = {"kind": "lin1_chunk", "shape": shape, "ask": ask, "a": float(a),
         "b": float(b) if b is not None else 0.0, "c": float(c), "d": float(d),
         "e": float(e) if e is not None else 0.0}
    rationale = (f"The unknown appears only inside {inner}, so {eq} gives "
                 f"{inner} = {num(u)}"
                 + ("." if asked == inner else f", and {asked} = {num(key)}."))
    ex = E(key)
    mistakes = _chunk_mistakes(ask, u, v0, c, coef, d, e, shape, wrong_coef, var, inner,
                               gridin=fmt == "spr")
    if fmt == "spr":
        return Item("lin1.chunk", "linear equation", "medium", seed, stem, "spr",
                    ex, ex.gridin(), rationale, params=P,
                    spr_mistakes=spr_mistakes(ex, mistakes))
    ch, tex, why, letter = choices(ex, mistakes, rng)
    return Item("lin1.chunk", "linear equation", "medium", seed, stem, "mcq", ex,
                letter, rationale, ch, why, tex, params=P)


def _chunk_mistakes(ask, u, v0, c, coef, d, e, shape, wrong_coef, var, inner,
                    gridin=False):
    """A grid-in leaves out a value its reason alone does not reach."""
    adds = (v0 - c, u + c) if c < 0 else (u + c, v0 - c)
    M: list[Mis] = []
    if ask == "chunk":
        M += [Mis(f"solved for {var} but the question asked for {inner}", v0),
              Mis("reported the number inside the parentheses", -c),
              Mis("added the number inside the parentheses instead of subtracting it",
                  adds[0]),
              Mis("added the number inside the parentheses to the wrong value", adds[1])]
    elif ask == "var":
        M += [Mis(f"stopped at {inner} instead of solving for {var}", u),
              Mis("reported the number inside the parentheses", -c),
              Mis("added the number inside the parentheses instead of subtracting it",
                  u + c),
              Mis("changed the sign of the bracket when solving back", -v0)]
    else:
        M += [Mis("reported the number already on the right side", d),
              Mis(f"solved for {var} but the question asked for {paren(coef, inner)}", v0),
              Mis("added the number inside the parentheses to the answer", coef * u - c),
              Mis(f"stopped at {inner} instead of the whole product", u)]
    if wrong_coef and not (gridin and ask != "chunk"):   # d / wrong_coef is the bracket
        mixed = Mis("subtracted the two coefficients instead of adding them"
                    if shape == "two_left" else
                    "added the two coefficients instead of subtracting them",
                    d / wrong_coef)
        M.insert(2, mixed) if ask == "var" else M.append(mixed)
    M += [Mis("expanded the brackets but dropped the products of the constants",
              None if gridin and ask != "term" else d),  # neither bracket nor unknown
          Mis("divided by one coefficient only", d / coef if coef else None)]
    return [m for m in M if m.value is not None and m.value != 0]


# ---------------------------------------------------------------- RECIPROCAL

def reciprocal(rng: random.Random, seed: int, *, var=None, a=None, b=None, c=None,
               fmt=None) -> Item:
    """x is given as a quotient; the reciprocal quotient is asked for."""
    var = var or rng.choice(VARS)
    a = Q(rng.randint(2, 20) if a is None else a)
    b = Q(rng.randint(2, 40) if b is None else b)
    c = Q(a if c is None else c)
    x = a * b
    key = c / x
    if key == 0 or x == 0:
        raise ItemError("a zero quotient")
    fmt = fmt or ("spr" if rng.random() < 0.4 else "mcq")
    if fmt == "spr" and not griddable(key):
        raise ItemError("this grid-in answer would not be enterable")
    eq = eq_of(over(1, a, var), num(b))
    asked = f"{num(c)}/{var}"
    stem = sent(f"If {eq}, what is the value of {asked}?")
    P = {"kind": "lin1_reciprocal", "a": float(a), "b": float(b), "c": float(c)}
    rationale = f"{eq} gives {var} = {num(x)}, so {asked} = {num(key)}."
    ex = E(key)
    mistakes = [Mis(f"inverted the quotient and reported {var} over the numerator", x / c),
                Mis(f"used the given value in place of {var}", c / b),
                Mis(f"used the denominator in place of {var}", c / a),
                Mis(f"reported {var} rather than the quotient asked for", x),
                Mis("multiplied the two given numbers into the numerator", c * b),
                Mis("divided the two given numbers the wrong way round", b / a)]
    if fmt == "spr":
        return Item("lin1.reciprocal", "linear equation", "medium", seed, stem, "spr",
                    ex, ex.gridin(), rationale, params=P,
                    spr_mistakes=spr_mistakes(ex, mistakes))
    ch, tex, why, letter = choices(ex, mistakes, rng)
    return Item("lin1.reciprocal", "linear equation", "medium", seed, stem, "mcq", ex,
                letter, rationale, ch, why, tex, params=P)
