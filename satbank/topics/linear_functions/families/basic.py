"""Function values: substitute, or recover a coefficient from a value.

Four generators cover the twenty-two source items that hand you a linear rule
and ask what it does to a number. The axes the source actually varies are the
surface form of the rule (mx + b, b - kx, (ax + c)/d), how the question is
framed, and which family of wrong answers the item writer chose -- the source
uses a different one depending on whether the numbers invite a sign slip, a
dropped term, or a given number reported back.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import Item, ItemError, Mis, assemble, gridin_mistakes
from ...linear_functions.common import (MINUS, choose, coef_text, ex, lin_text,
                                        numtext, q)

__all__ = ["evaluate", "coefficient", "combine", "inner_scale"]

NAMES = ["f", "g", "h", "j", "k", "p"]
VARS = ["x", "x", "x", "t", "n"]
WRONGS = ["structural", "given", "sign"]


def _concat(a: Q, b: Q):
    """50 and 200 written side by side as 50,200 -- the slip that produces the
    source's largest option when a function is x + 200."""
    if a.denominator != 1 or b.denominator != 1 or a <= 0 or b <= 0:
        return None
    return Q(int(f"{a.numerator}{b.numerator}"))


# ------------------------------------------------------------------ evaluate

def _eval_mistakes(m: Q, b: Q, x0: Q, key: Q, form: str, wrong: str,
                   a: Q = None, c: Q = None, d: Q = None, spr: bool = False) -> list[Mis]:
    """spr: the grid-in list. A typed value is filed under its reason, so there
    every reason must be exactly the route to its value on these numbers: a
    sign slip is named by the sign actually printed, and a slip these numbers
    cannot produce is None."""
    M: list[Mis] = []
    if form == "quotient":
        return [Mis("did not divide by the denominator", a * x0 + c),
                Mis("left out the coefficient of x in the numerator", (x0 + c) / d),
                Mis("added the coefficient and the input instead of multiplying them",
                    (a + x0 + c) / d if spr else (a + x0) / d),
                Mis("divided only the constant term by the denominator", a * x0 + c / d),
                Mis("added the constant instead of subtracting it" if spr and c < 0
                    else "subtracted the constant instead of adding it", (a * x0 - c) / d),
                # the mirror of "divided only the constant term": it divides the x-term
                # and leaves the constant whole, so it keeps the denominator d the key
                # is printed over instead of clearing it
                Mis("divided only the coefficient of x by the denominator",
                    (a / d) * x0 + c),
                Mis("substituted the input without its negative sign",
                    (a * abs(x0) + c) / d),
                Mis("divided by the coefficient of x instead of by the denominator",
                    (a * x0 + c) / a),
                Mis("inverted the fraction, dividing the denominator by the value of "
                    "the numerator", d / (a * x0 + c) if a * x0 + c != 0 else None)]
    if form == "constant_first":
        k = -m
        M = [Mis("subtracted the coefficient instead of the whole product", b - k),
             Mis("added the input instead of multiplying it by the coefficient",
                 b - k + x0),
             Mis("added the coefficient and the input", k + x0),
             Mis("found the amount subtracted rather than what is left", k * x0),
             Mis("gave the constant term instead of evaluating the function", b),
             Mis("subtracted the constant from the product", k * x0 - b)]
        return M
    if wrong == "sign":
        M = [Mis("used the sign of the input rather than its value",
                 None if spr and x0 == 0 else (Q(1) if x0 >= 0 else Q(-1)) * m + b),
             Mis("added the coefficient to the constant, ignoring its sign",
                 None if spr and b > 0 else m + abs(b)),
             Mis("dropped the negative sign from the result",
                 None if spr and key >= 0 else -key),
             Mis("substituted the input without its negative sign", m * abs(x0) + b),
             Mis("left out the constant term", m * x0)]
    elif wrong == "given":
        M = [Mis("gave the constant term instead of evaluating the function", b),
             Mis("gave the coefficient of x instead of evaluating the function", m),
             Mis("subtracted the constant term from the input", x0 - b),
             Mis("multiplied the input and the constant term instead of adding them",
                 None if spr and m != 1 else x0 * b),
             Mis("gave the input instead of the output", x0)]
    else:
        M = [Mis("left out the constant term", m * x0),
             Mis("added the coefficient, the input and the constant term", m + x0 + b),
             Mis("multiplied the input by the constant term and added the coefficient",
                 b * x0 + m),
             Mis("multiplied the input and the constant term instead of adding them",
                 None if spr and m != 1 else x0 * b),
             Mis("added the constant term instead of subtracting it" if spr and b < 0
                 else "subtracted the constant term instead of adding it", m * x0 - b)]
    if abs(m) == 1:
        # side by side is x + 200 at 50 written 50200; with a sign in the rule
        # or in the input, nothing a student writes side by side gives it
        cat = (_concat(x0, b) if m == 1 else None) if spr else _concat(abs(x0), abs(b))
        M = [Mis("gave the constant term instead of evaluating the function", b),
             Mis("multiplied the input and the constant term instead of adding them",
                 None if spr and m != 1 else x0 * b),
             Mis("wrote the input beside the constant instead of adding them", cat),
             Mis("subtracted the constant term from the input", x0 - b),
             Mis("doubled the constant term", 2 * b)] + M
    return M


EVAL_FRAMES = ["defined_by", "if_defined", "equation_when", "when_defined_by",
               "bare_y", "given_equation"]


def evaluate(rng: random.Random, seed: int, *, m=None, b=None, x0=None, form=None,
             name=None, var=None, frame=None, fmt=None, wrong=None,
             a=None, c=None, d=None, style="frac", places=None) -> Item:
    """A linear rule and an input. The whole of the easy tier starts here."""
    if form is None:
        # a caller who names a numerator, or a slope and a constant, has already
        # chosen the surface form; only a bare draw picks one
        if a is not None or c is not None or d is not None:
            form = "quotient"
        elif m is not None or b is not None:
            form = "slope_first"
        else:
            form = rng.choices(["slope_first", "constant_first", "quotient"],
                               weights=[6, 2, 2])[0]
    name = name or rng.choice(NAMES)
    var = var or rng.choice(VARS)
    frame = frame or rng.choice(EVAL_FRAMES)
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    wrong = wrong or rng.choice(WRONGS)

    if form == "quotient":
        a = q(a if a is not None else rng.choice([2, 3, 4, 5, -2, -3]))
        c = q(c if c is not None else rng.randint(-9, 9))
        d = q(d if d is not None else rng.randint(2, 6))
        m, b = a / d, c / d
        body = f"({lin_text(a, c, var)})/{numtext(d)}"
    else:
        if form == "constant_first":
            b = q(b if b is not None else rng.randint(12, 99))
            k = q(-m if m is not None else rng.randint(2, 12))
            m = -k
            body = (f"{numtext(b, style, places)} {MINUS} "
                    f"{coef_text(k, var, style, places)}")
        else:
            m = q(m if m is not None else rng.choice(
                [rng.randint(2, 12), rng.randint(-12, -2), 1, -1, 10, 100]))
            b = q(b if b is not None else rng.randint(-99, 250))
            body = lin_text(m, b, var, style, places)
    x0 = q(x0 if x0 is not None else rng.randint(-9, 12))
    if b == 0 or m == 0:
        raise ItemError("a linear rule needs both a coefficient and a constant")
    key = m * x0 + b

    lhs = f"{name}({var})"
    call = f"{name}({numtext(x0)})"
    if frame == "defined_by":
        stem = f"The function {name} is defined by {lhs} = {body}. What is the value of {call}?"
    elif frame == "if_defined":
        stem = (f"If {name} is the function defined by {lhs} = {body}, what is the value "
                f"of {call}?")
    elif frame == "equation_when":
        stem = (f"The function {name} is defined by the equation {lhs} = {body}. What is "
                f"the value of {lhs} when {var} = {numtext(x0)}?")
    elif frame == "when_defined_by":
        stem = (f"The function {name} is defined by {lhs} = {body}. What is the value of "
                f"{lhs} when {var} = {numtext(x0)}?")
    elif frame == "bare_y":
        stem = (f"If y = {body}, what is the value of y when {var} = {numtext(x0)}?")
    else:
        stem = (f"{lhs} = {body} The function {name} is defined by the given equation. "
                f"What is the value of {lhs} when {var} = {numtext(x0)}?")

    P = {"kind": "lf_evaluate", "m": [m.numerator, m.denominator],
         "b": [b.numerator, b.denominator], "x0": [x0.numerator, x0.denominator]}
    rationale = (f"Substituting {var} = {numtext(x0)} into {body} gives "
                 f"{numtext(key)}.")
    keyx = ex(key)
    def named(spr=False):
        return [Mis(r.reason, ex(r.value)) for r in
                _eval_mistakes(m, b, x0, key, form, wrong, a, c, d, spr)
                if r.value is not None]
    if fmt == "spr":
        if keyx.gridin().lstrip("-").replace("/", "").replace(".", "") == "":
            raise ItemError("no grid-in form")
        return Item("lin.evaluate", "evaluating a linear function", "easy", seed, stem,
                    "spr", keyx, keyx.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(keyx, named(True)))
    mistakes = named()
    choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True)
    return Item("lin.evaluate", "evaluating a linear function", "easy", seed, stem, "mcq",
                keyx, letter, rationale, choices, reasons, latex, params=P)


# --------------------------------------------------------------- coefficient

def coefficient(rng: random.Random, seed: int, *, m=None, b=None, x1=None, x2=None,
                unknown=None, ask=None, name=None, var=None, fmt=None,
                b_given=None, letter_name=None) -> Item:
    """One coefficient is a letter; a single function value pins it down.

    unknown='b'  ->  g(x) = 5x + a with g(4) = 31
    unknown='m'  ->  c(x) = mx + 500 with c(100) = 800
    ask='value'  ->  having found it, evaluate somewhere else
    """
    name = name or rng.choice(NAMES)
    var = var or rng.choice(VARS)
    unknown = unknown or rng.choice(["m", "b"])
    ask = ask or ("unknown" if unknown == "b" or rng.random() < 0.4 else "value")
    fmt = fmt or ("spr" if rng.random() < 0.5 else "mcq")
    b_given = b_given or ("equation" if unknown == "m" else "equation")
    letter_name = letter_name or ("a" if unknown == "b" else "m")

    m = q(m if m is not None else rng.choice([rng.randint(2, 20), rng.randint(-20, -2)]))
    b = q(b if b is not None else rng.choice([rng.randint(-60, 600), 144, 500]))
    x1 = q(x1 if x1 is not None else rng.randint(2, 20))
    if x1 == 0:
        raise ItemError("the given value must pin the unknown down")
    y1 = m * x1 + b
    x2 = q(x2 if x2 is not None else rng.randint(2, 30))

    if unknown == "b":
        body = f"{coef_text(m, var)} + {letter_name}"
    else:
        body = f"{letter_name}{var} + {numtext(b)}"
    lhs = f"{name}({var})"
    if b_given == "two_values" and unknown == "m":
        head = (f"The function {name} is defined by {lhs} = {letter_name}{var} + b, where "
                f"{letter_name} and b are constants. If {name}(0) = {numtext(b)} and "
                f"{name}({numtext(x1)}) = {numtext(y1)}, ")
        ask_text = f"what is the value of {letter_name} ?"
        stem = head + ask_text
    elif ask == "unknown":
        stem = (f"The function {name} is defined as {lhs} = {body}, where {letter_name} is "
                f"a constant. If {name}({numtext(x1)}) = {numtext(y1)}, what is the value "
                f"of {letter_name} ?")
    else:
        stem = (f"{lhs} = {body} For the linear function {name}, {letter_name} is a "
                f"constant and {name}({numtext(x1)}) = {numtext(y1)}. What is the value of "
                f"{name}({numtext(x2)})?")

    if ask == "unknown":
        key = b if unknown == "b" else m
    else:
        key = m * x2 + b
    P = {"kind": "lf_coefficient", "m": [m.numerator, m.denominator],
         "b": [b.numerator, b.denominator], "x1": [x1.numerator, x1.denominator],
         "x2": [x2.numerator, x2.denominator], "unknown": unknown, "ask": ask}
    rationale = (f"{numtext(y1)} = {numtext(m)}({numtext(x1)}) + {numtext(b)} gives "
                 f"{letter_name} = {numtext(key)}"
                 + (f", so {name}({numtext(x2)}) = {numtext(m * x2 + b)}."
                    if ask == "value" else "."))
    keyx = ex(key)
    if ask == "unknown" and unknown == "b":
        mistakes = [Mis("added the coefficient and the input instead of multiplying them",
                        y1 - (m + x1)),
                    Mis("subtracted the input instead of the product", y1 - x1),
                    Mis("added the product instead of subtracting it", y1 + m * x1),
                    Mis("subtracted the given value from the product", m * x1 - y1),
                    Mis("subtracted the coefficient instead of the product", y1 - m)]
    elif ask == "unknown":
        mistakes = [Mis("did not remove the constant term before dividing", y1 / x1),
                    Mis("subtracted the input instead of dividing by it", y1 - b - x1),
                    Mis("did not divide by the input", y1 - b),
                    Mis("divided the constant term by the input", b / x1)]
    else:
        mistakes = [Mis("used the first input again instead of the second", y1),
                    Mis("left out the constant term", m * x2),
                    Mis("scaled the given value by the ratio of the inputs", y1 * x2 / x1),
                    Mis("added the constant term twice", m * x2 + 2 * b)]
    mistakes = [Mis(r.reason, ex(r.value)) for r in mistakes if r.value is not None]
    if fmt == "spr":
        return Item("lin.coefficient", "an unknown coefficient", "medium", seed, stem,
                    "spr", keyx, keyx.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(keyx, mistakes))
    choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True,
                                               fillers="shift")
    return Item("lin.coefficient", "an unknown coefficient", "medium", seed, stem, "mcq",
                keyx, letter, rationale, choices, reasons, latex, params=P)


# ------------------------------------------------------------------- combine

def combine(rng: random.Random, seed: int, *, mode=None, c=None, d=None, p=None,
            qv=None, af=None, bg=None, fmt="mcq") -> Item:
    """Two function values put together: 4f(2) − g(2), or f(9) − f(1)."""
    mode = mode or rng.choice(["same_function", "two_functions"])
    if mode == "same_function":
        c = q(c if c is not None else rng.randint(1, 12))
        d = q(d if d is not None else rng.randint(2, 8))
        p = q(p if p is not None else rng.randint(5, 20))
        qv = q(qv if qv is not None else rng.randint(1, 4))
        if p == qv:
            raise ItemError("the two inputs must differ")
        key = (p - qv) / d
        stem = (f"f(x) = (x + {numtext(c)})/{numtext(d)} For the function f defined above, "
                f"what is the value of f({numtext(p)}) {MINUS} f({numtext(qv)}) ?")
        mistakes = [Mis("divided by the denominator twice, once in each term",
                        (p - qv) / (2 * d)),
                    Mis("subtracted the constant from the difference of the inputs",
                        (p - qv - c) / d),
                    Mis("evaluated the first term only and dropped the constant", p / d),
                    Mis("added the two values instead of subtracting them",
                        (p + qv + 2 * c) / d),
                    Mis("subtracted the inputs without dividing", p - qv)]
        spr = [Mis("added the denominators when subtracting the fractions",
                   mistakes[0].value)] + mistakes[1:]
        rationale = (f"f({numtext(p)}) = {numtext((p + c) / d)} and f({numtext(qv)}) = "
                     f"{numtext((qv + c) / d)}, so the difference is {numtext(key)}.")
        P = {"kind": "lf_combine", "mode": mode, "c": [c.numerator, c.denominator],
             "d": [d.numerator, d.denominator], "p": [p.numerator, p.denominator],
             "q": [qv.numerator, qv.denominator]}
    else:
        c = q(c if c is not None else rng.randint(2, 15))          # f(x) = x + c
        d = q(d if d is not None else rng.randint(2, 15))          # g(x) = dx
        p = q(p if p is not None else rng.randint(2, 9))           # the shared input
        af = q(af if af is not None else rng.randint(2, 6))
        bg = q(bg if bg is not None else 1)
        key = af * (p + c) - bg * d * p
        gpart = (f"g({numtext(p)})" if bg == 1
                 else f"{numtext(bg)}g({numtext(p)})")
        stem = (f"If f(x) = x + {numtext(c)} and g(x) = {coef_text(d, 'x')}, what is the "
                f"value of {numtext(af)}f({numtext(p)}) {MINUS} {gpart}?")
        mistakes = [Mis("multiplied the input by the outside factor instead of the value",
                        af * p + c - bg * d * p),
                    Mis("left the outside factor off the first value",
                        (p + c) - bg * d * p),
                    Mis("added the two values instead of subtracting them",
                        af * (p + c) + bg * d * p),
                    Mis("multiplied the second function's coefficient by the outside "
                        "factor", af * (p + c) - af * d * p)]
        rationale = (f"f({numtext(p)}) = {numtext(p + c)} and g({numtext(p)}) = "
                     f"{numtext(d * p)}, so the value is {numtext(key)}.")
        P = {"kind": "lf_combine", "mode": mode, "c": [c.numerator, c.denominator],
             "d": [d.numerator, d.denominator], "p": [p.numerator, p.denominator],
             "af": [af.numerator, af.denominator], "bg": [bg.numerator, bg.denominator]}
        spr = mistakes
    keyx = ex(key)
    mistakes = [Mis(r.reason, ex(r.value)) for r in mistakes if r.value is not None]
    if fmt == "spr":
        return Item("lin.combine", "combining function values", "medium", seed, stem,
                    "spr", keyx, keyx.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(
                        keyx, [Mis(r.reason, ex(r.value)) for r in spr]))
    choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True)
    return Item("lin.combine", "combining function values", "medium", seed, stem, "mcq",
                keyx, letter, rationale, choices, reasons, latex, params=P)


# --------------------------------------------------------------- inner_scale

def inner_scale(rng: random.Random, seed: int, *, c=None, d=None, k=None, ask=None,
                fmt=None, value=None) -> Item:
    """f(cx) = x + d defines f only through a scaled argument.

    ask='value'    f(k), which needs cx = k solved first
    ask='constant' the scale c itself, recovered from one stated value
    """
    ask = ask or rng.choice(["value", "constant"])
    d = q(d if d is not None else rng.choice([rng.randint(-12, -2), rng.randint(2, 12)]))
    if ask == "value":
        c = q(c if c is not None else rng.randint(2, 9))
        t = q(rng.randint(1, 9)) if k is None else q(k) / c
        k = q(k) if k is not None else c * t
        key = k / c + d
        stem = (f"For the function f, if f({coef_text(c, 'x')}) = {lin_text(1, d)} for all "
                f"values of x, what is the value of f({numtext(k)}) ?")
        mistakes = [Mis("substituted the argument directly, ignoring the scale factor",
                        k + d),
                    Mis("gave the value of x that makes the argument match", k / c),
                    Mis("used the constant term as the value", d),
                    Mis("multiplied by the scale factor instead of dividing", k * c + d),
                    Mis("subtracted the constant instead of adding it", k / c - d)]
        # a grid-in names the sign actually printed: x - 5 had 5 added
        spr = mistakes[:4] + [Mis("added the constant instead of subtracting it"
                                  if d < 0 else mistakes[4].reason, k / c - d)]
        rationale = (f"{coef_text(c, 'x')} = {numtext(k)} when x = {numtext(k / c)}, so "
                     f"f({numtext(k)}) = {numtext(k / c)} + ({numtext(d)}) = "
                     f"{numtext(key)}.")
        P = {"kind": "lf_inner", "ask": ask, "c": [c.numerator, c.denominator],
             "d": [d.numerator, d.denominator], "k": [k.numerator, k.denominator]}
        fmt = fmt or "mcq"
    else:
        k = q(k if k is not None else rng.randint(2, 9))
        value = q(value if value is not None else rng.randint(20, 60))
        if value == d:
            raise ItemError("the stated value must not equal the constant term")
        key = k / (value - d)
        c = key
        stem = (f"For the function f, f(cx) = {lin_text(1, d)} for all values of x, where c "
                f"is a positive constant. If f({numtext(k)}) = {numtext(value)}, what is "
                f"the value of c?")
        if key <= 0:
            raise ItemError("c must be positive")
        # a signed constant reads "- 3", never "+ (-3)"
        tail = f"{MINUS} {numtext(-d)}" if d < 0 else f"+ {numtext(d)}"
        rationale = (f"f({numtext(k)}) means x = {numtext(k)}/c, so {numtext(k)}/c {tail} "
                     f"= {numtext(value)} and c = {numtext(key)}.")
        P = {"kind": "lf_inner", "ask": ask, "d": [d.numerator, d.denominator],
             "k": [k.numerator, k.denominator],
             "value": [value.numerator, value.denominator]}
        mistakes = [Mis("divided the stated value by the argument", (value - d) / k),
                    Mis("added the constant instead of subtracting it", k / (value + d)),
                    Mis("left the constant out altogether", k / value)]
        # (value - d)/k is k/c = value - d solved for c upside down, and when
        # the rule prints x - 5 its slip subtracts the 5 rather than adding it
        spr = [Mis("inverted the ratio after removing the constant", (value - d) / k),
               Mis("subtracted the constant instead of adding it" if d < 0
                   else mistakes[1].reason, k / (value + d)),
               mistakes[2]]
        fmt = fmt or "spr"
    keyx = ex(key)
    mistakes = [Mis(r.reason, ex(r.value)) for r in mistakes if r.value is not None]
    if fmt == "spr":
        return Item("lin.inner_scale", "a function of a scaled argument", "hard", seed,
                    stem, "spr", keyx, keyx.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(
                        keyx, [Mis(r.reason, ex(r.value)) for r in spr if r.value is not None]))
    choices, latex, reasons, letter = choose(keyx, mistakes, rng, signed=True)
    return Item("lin.inner_scale", "a function of a scaled argument", "hard", seed, stem,
                "mcq", keyx, letter, rationale, choices, reasons, latex, params=P)
