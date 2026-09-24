"""Putting a number into a nonlinear rule, and taking one out again.

The commonest easy item in the set: a polynomial, a radical, a quotient or an
exponential is printed, and one input is named. What varies is the *shape* of
the rule, because the mistake a student makes is a mistake about that shape --
reading x³ as 3x, raising the coefficient along with the base, giving the
denominator instead of the quotient. Each shape therefore carries its own
named pool of wrong answers rather than a shared list of near-misses.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import ItemError, Mis
from ..common import (MINUS, dec, ex, factored, fn, num, pick, poly_text, power,
                      q, sup, unambiguous, value_item)

__all__ = ["evaluate", "exp_evaluate", "solve_value", "param_value", "abs_value"]

NAMES = ["f", "g", "h", "p"]

FRAMES = [
    "The function {n} is defined by {rule}. What is the value of {n}({a})?",
    "{rule} For the function {n} defined above, what is the value of {n}({a})?",
    "If {rule}, what is {n}({a})?",
    "The function {n} is defined by {rule}. What is the value of {n}(x) when "
    "x = {a}?",
]


def _stem(frame: int, name: str, rule: str, a: str) -> str:
    return FRAMES[frame % len(FRAMES)].format(n=name, rule=rule, a=a)


# ------------------------------------------------------- algebraic rules

def evaluate(rng: random.Random, seed: int, *, form=None, name=None, frame=None,
             fmt="mcq", wrongs=None, n=None, k=None, a=None, b=None, c=None,
             d=None, x0=None, s=None, p=None, qq=None) -> object:
    """f(x) = a rule that is not linear; what is f(x0)?"""
    form = form or rng.choice(["poly_k", "cubic", "radical", "rational",
                               "ratio_quad", "product"])
    name = name or rng.choice(NAMES)
    frame = rng.randrange(len(FRAMES)) if frame is None else frame

    if form == "poly_k":
        n = int(n if n is not None else rng.choice([2, 3, 3, 4]))
        k = q(k if k is not None else rng.randint(2, 40))
        x0 = q(x0 if x0 is not None else rng.randint(2, 5))
        if n == 2 and x0 == 2:
            raise ItemError("squaring and doubling agree at 2")
        rule = fn(name, "x", f"{power('x', n)} + {num(k)}")
        key = x0 ** n + k
        pool = {
            "swapped": ("raised the exponent to the input instead of the input to "
                        "the exponent", k + Q(n) ** int(x0)),
            "times_exponent": ("multiplied the input by the exponent instead of "
                               "raising it", k + n * x0),
            "sum": ("added the input and the exponent instead of raising", k + n + x0),
            "no_constant": ("left the constant term out", x0 ** n),
        }
        order = ["swapped", "times_exponent", "sum", "no_constant"]
        why = (f"{power('x', n)} at x = {num(x0)} is {num(x0 ** n)}, so "
               f"{name}({num(x0)}) = {num(x0 ** n)} + {num(k)} = {num(key)}.")
        skill = "evaluating a power function"

    elif form == "cubic":
        a = q(a if a is not None else 1)
        b = q(b if b is not None else rng.randint(-6, 6))
        c = q(c if c is not None else rng.randint(-9, 9))
        d = q(d if d is not None else rng.randint(-9, 9))
        x0 = q(x0 if x0 is not None else rng.choice([-2, -1, 1, 2]))
        if a == 0 or b == 0 or c == 0 or d == 0:
            raise ItemError("every term must be visible in the printed rule")
        rule = fn(name, "x", poly_text([d, c, b, a]))
        terms = [a * x0 ** 3, b * x0 ** 2, c * x0, d]
        key = sum(terms)
        pool = {
            "sign": ("changed the sign of the answer", -key),
            "abs": ("made every term positive before adding them",
                    sum(abs(t) for t in terms)),
            "neg_abs": ("made every term positive and then changed the sign",
                        -sum(abs(t) for t in terms)),
            "drop_constant": ("left the constant term out", key - d),
        }
        order = ["sign", "abs", "neg_abs", "drop_constant"]
        why = (f"{name}({num(x0)}) = " +
               " + ".join(num(t) for t in terms).replace("+ " + MINUS, MINUS) +
               f" = {num(key)}.")
        skill = "evaluating a cubic"

    elif form == "radical":
        k = q(k if k is not None else rng.randint(2, 12))
        s = int(s if s is not None else rng.randint(3, 15))
        x0 = q(s) ** 2
        rule = fn(name, "x", f"{num(k)} + √x")
        key = k + s
        pool = {
            "quarter": ("divided the radicand by 4 instead of taking its square root",
                        k + x0 / 4),
            "half": ("halved the radicand instead of taking its square root",
                     k + x0 / 2),
            "no_constant": ("gave the square root and left the constant out", q(s)),
            "product": ("multiplied by the constant instead of adding it", k * s),
            "radicand": ("added the radicand itself instead of its square root",
                         k + x0),
        }
        order = ["quarter", "half", "no_constant", "product", "radicand"]
        why = (f"√{num(x0)} = {s}, so {name}({num(x0)}) = {num(k)} + {s} = {num(key)}.")
        skill = "evaluating a square root function"

    elif form == "rational":
        k = q(k if k is not None else rng.randint(6, 40))
        x0 = q(x0 if x0 is not None else rng.randint(3, 40))
        if x0 == k or x0 == 0:
            raise ItemError("the quotient must not be 1")
        rule = fn(name, "x", f"{num(k)}/x")
        key = k / x0
        pool = {
            "inverted": ("inverted the quotient, dividing the input by the numerator",
                         x0 / k),
            "numerator": ("gave the numerator rather than the quotient", k),
            "input": ("gave the input rather than the quotient", x0),
            "difference": ("subtracted the input instead of dividing by it", k - x0),
        }
        order = ["inverted", "numerator", "input", "difference"]
        quotient = f"{num(k)}/{num(x0)}"
        why = (f"{name}(x) = {num(k)}/x, so {name}({num(x0)}) = {quotient}."
               if quotient == num(key) else
               f"{name}(x) = {num(k)}/x, so {name}({num(x0)}) = {quotient} = {num(key)}.")
        skill = "evaluating a rational function"

    elif form == "ratio_quad":
        b = q(b if b is not None else rng.randint(-9, 9))
        c = q(c if c is not None else rng.randint(-9, 9))
        d = q(d if d is not None else rng.randint(-6, 6))
        x0 = q(x0 if x0 is not None else rng.choice([-3, -2, -1, 2, 3, 4]))
        if b == 0 or c == 0 or d == 0 or x0 + d == 0:
            raise ItemError("the quotient must be defined and fully printed")
        top = x0 ** 2 + b * x0 + c
        bottom = x0 + d
        key = top / bottom
        rule = fn(name, "x", f"({poly_text([c, b, 1])})/({poly_text([d, 1])})")
        pool = {
            "inverted": ("inverted the quotient, dividing the denominator by the "
                         "numerator", bottom / top if top != 0 else None),
            "sign": ("changed the sign of the quotient", -key),
            "denominator": ("gave the denominator rather than the quotient", bottom),
            "abs_denominator": ("gave the denominator with its sign dropped",
                                abs(bottom)),
            "numerator": ("gave the numerator rather than the quotient", top),
            "no_constant": ("left the constant term out of the numerator before "
                            "dividing", (top - c) / bottom),
            "square_as_double": ("read x² as 2x in the numerator",
                                 (2 * x0 + b * x0 + c) / bottom),
        }
        # the inverted quotient leads, because it always carries the key's own
        # sign: a fractional key is then never the only fraction of its sign
        order = ["inverted", "sign", "denominator", "abs_denominator",
                 "no_constant", "square_as_double", "numerator"]
        why = (f"At x = {num(x0)} the numerator is {num(top)} and the denominator is "
               f"{num(bottom)}, so {name}({num(x0)}) = {num(key)}.")
        skill = "evaluating a rational function"

    else:                                                    # product of two sums
        p = q(p if p is not None else Q(rng.choice([25, 50, 75]), 100))
        qq = q(qq if qq is not None else rng.choice([30, 40, 50, 60]))
        x0 = q(x0 if x0 is not None else rng.randint(5, 25))
        if x0 >= qq or p == 0:
            raise ItemError("the second factor must stay positive")
        rule = fn(name, "x", f"(x + {dec(p)}x)({num(qq)} {MINUS} x)")
        first = x0 + p * x0
        key = first * (qq - x0)
        pool = {
            "scaled_only": ("used only the scaled part of the first factor and left "
                            "the subtraction out", p * x0 * qq),
            "second_is_input": ("used the input itself as the second factor",
                                first * x0),
            "doubled": ("read x + %sx as 2x and used %s rather than %s − x"
                        % (dec(p), num(qq), num(qq)), 2 * x0 * qq),
            "no_scale": ("left the scaled part of the first factor out",
                         x0 * (qq - x0)),
        }
        order = ["scaled_only", "second_is_input", "doubled", "no_scale"]
        why = (f"x + {dec(p)}x is {num(first)} at x = {num(x0)} and "
               f"{num(qq)} {MINUS} x is {num(qq - x0)}, so {name}({num(x0)}) = "
               f"{num(key)}.")
        skill = "evaluating a product of two factors"

    P = {"kind": "nlf_evaluate", "form": form,
         "x0": [x0.numerator, x0.denominator]}
    if form == "poly_k":
        P.update(n=n, k=[k.numerator, k.denominator])
    elif form == "cubic":
        P.update(coef=[[v.numerator, v.denominator] for v in (d, c, b, a)])
    elif form == "radical":
        P.update(k=[k.numerator, k.denominator])
    elif form == "rational":
        P.update(k=[k.numerator, k.denominator])
    elif form == "ratio_quad":
        P.update(b=[b.numerator, b.denominator], c=[c.numerator, c.denominator],
                 d=[d.numerator, d.denominator])
    else:
        P.update(p=[p.numerator, p.denominator], q=[qq.numerator, qq.denominator])

    return value_item("nlfunc.evaluate", skill, "easy", seed,
                      _stem(frame, name, rule, num(x0)), key,
                      pick(pool, order, wrongs), rng, P, why, fmt=fmt)


# ------------------------------------------------------- exponential rules

def exp_evaluate(rng: random.Random, seed: int, *, a=None, base=None, x0=None,
                 name=None, frame=None, fmt="mcq", wrongs=None, places=None,
                 bracket=True) -> object:
    """f(x) = a(b^x); what is f(x0)?  The base may be a whole number or a decimal."""
    name = name or rng.choice(NAMES)
    frame = rng.randrange(len(FRAMES)) if frame is None else frame
    a = q(a if a is not None else rng.choice([2, 3, 4, 5, 6, 10, 270, 500]))
    base = q(base if base is not None else rng.choice(
        [2, 3, 4, 5, Q(1, 10), Q(1, 2)]))
    x0 = q(x0 if x0 is not None else rng.choice([0, 2, 3]))
    if a <= 0 or base <= 0 or base == 1:
        raise ItemError("an exponential needs a positive base other than 1")
    if x0 == 1:
        # at an exponent of 1 the coefficient, the base and the product all
        # coincide, so three of the four misconceptions print the key
        raise ItemError("an exponent of 1 collapses the wrong answers onto the key")
    body = f"{num(a)}({dec(base, places) if places is not None else num(base)}^x)" \
        if bracket else f"{num(a)}({dec(base, places) if places is not None else num(base)})^x"
    rule = fn(name, "x", body)
    key = a * base ** int(x0)
    pool = {
        "no_coefficient": ("gave the power alone, leaving the coefficient out",
                           base ** int(x0)),
        "linear": ("multiplied by the base once for each unit of the input instead "
                   "of raising it to that power", a * base * x0),
        "product_power": ("raised the coefficient to the power as well as the base",
                          (a * base) ** int(x0)),
        "times_base": ("multiplied by the base once regardless of the exponent",
                       a * base),
    }
    order = ["no_coefficient", "linear", "product_power", "times_base"]
    why = (f"{num(base)} raised to the power {num(x0)} is {num(base ** int(x0))}, so "
           f"{name}({num(x0)}) = {num(a)} · {num(base ** int(x0))} = {num(key)}.")
    P = {"kind": "nlf_exp_evaluate", "a": [a.numerator, a.denominator],
         "base": [base.numerator, base.denominator], "x0": [x0.numerator, x0.denominator]}
    return value_item("nlfunc.exp_evaluate", "evaluating an exponential function",
                      "easy", seed, _stem(frame, name, rule, num(x0)), key,
                      pick(pool, order, wrongs), rng, P, why, fmt=fmt)


# --------------------------------------------------------- going backwards

SOLVE_POWER = ("The function {n} is defined by {rule}. What is the value of {v} when "
               "{n}({v}) is equal to {t}?")
SOLVE_KE = ("An object's kinetic energy, in joules, is equal to the product of "
            "one-half the object's mass, in kilograms, and the square of the "
            "object's speed, in meters per second. What is the speed, in meters per "
            "second, of an object with a mass of {m} kilograms and kinetic energy of "
            "{e} joules?")


def solve_value(rng: random.Random, seed: int, *, mode=None, k=None, m=None,
                root=None, mass=None, name=None, var=None, fmt="mcq",
                wrongs=None) -> object:
    """The output is given and the input is wanted: k·nᵐ = t, or ½mv² = E."""
    mode = mode or rng.choice(["power", "kinetic"])

    if mode == "power":
        name = name or rng.choice(NAMES)
        var = var or rng.choice(["n", "x", "t"])
        k = q(k if k is not None else rng.randint(2, 12))
        m = int(m if m is not None else rng.choice([2, 3, 3]))
        root = q(root if root is not None else rng.randint(2, 6))
        target = k * root ** m
        rule = fn(name, var, f"{num(k)}{power(var, m)}")
        key = root
        pool = {
            "over_both": ("divided by the coefficient and by the exponent instead of "
                          "taking a root", target / (k * m)),
            "coefficient": ("gave the coefficient rather than the input", k),
            "no_root": ("divided by the coefficient but did not take the root",
                        target / k),
            "over_exponent": ("divided by the exponent instead of taking the root",
                              target / m),
        }
        order = ["over_both", "coefficient", "no_root", "over_exponent"]
        stem = SOLVE_POWER.format(n=name, rule=rule, v=var, t=num(target))
        why = (f"{num(k)}{power(var, m)} = {num(target)} gives {power(var, m)} = "
               f"{num(target / k)}, so {var} = {num(root)}.")
        P = {"kind": "nlf_solve_value", "mode": mode, "k": [k.numerator, k.denominator],
             "m": m, "target": [target.numerator, target.denominator]}
        skill = "solving a power equation"
    else:
        mass = q(mass if mass is not None else rng.choice([2, 4, 6, 8, 10]))
        root = q(root if root is not None else rng.randint(2, 12))
        energy = mass * root ** 2 / 2
        if energy.denominator != 1:
            raise ItemError("the printed energy must be a whole number of joules")
        key = root
        pool = {
            "no_root": ("did not take the square root of the squared speed",
                        2 * energy / mass),
            "double_energy": ("doubled the energy and stopped there", 2 * energy),
            "root_double_energy": ("took the square root of twice the energy without "
                                   "dividing by the mass", None),
            "half_energy": ("halved the energy instead of doubling it",
                            energy / (2 * mass)
                            if (energy / (2 * mass)).denominator == 1 else None),
        }
        root2 = _int_sqrt(2 * energy)
        if root2 is not None:
            pool["root_double_energy"] = ("took the square root of twice the energy "
                                          "without dividing by the mass", q(root2))
        order = ["no_root", "double_energy", "root_double_energy", "half_energy"]
        stem = SOLVE_KE.format(m=num(mass), e=num(energy))
        why = (f"{num(energy)} = (1/2)({num(mass)})v² gives v² = {num(2 * energy / mass)}, "
               f"so v = {num(root)}.")
        P = {"kind": "nlf_solve_value", "mode": mode,
             "mass": [mass.numerator, mass.denominator],
             "energy": [energy.numerator, energy.denominator]}
        skill = "solving a squared relationship"

    return value_item("nlfunc.solve_value", skill, "medium", seed, stem, key,
                      pick(pool, order, wrongs), rng, P, why, fmt=fmt, signed=False)


def _int_sqrt(v) -> int | None:
    v = q(v)
    if v < 0 or v.denominator != 1:
        return None
    r = int(round(float(v) ** 0.5))
    return r if r * r == v.numerator else None


# ------------------------------------------- a rule with a hidden constant

PARAM = ("Let the function {n} be defined as {rule}, where c is a constant. If "
         "{n}(c) = {v}, what is the value of {n}({m})?")


def param_value(rng: random.Random, seed: int, *, K=None, v=None, m=None, name=None,
                fmt="mcq", wrongs=None) -> object:
    """p(x) = ((x − c)² + K)/(2c): the stated value pins c down first."""
    name = name or rng.choice(["p", "f", "g"])
    K = q(K if K is not None else rng.choice([40, 60, 90, 120, 160, 200, 240]))
    v = q(v if v is not None else rng.choice([5, 6, 8, 10, 12, 15]))
    c = K / (2 * v)
    if c <= 0 or c.denominator != 1:
        raise ItemError("the hidden constant must be a whole number")
    m = q(m if m is not None else c + rng.choice([2, 3, 4, 5, 6]))
    if m == c:
        raise ItemError("the second input must differ from the constant")
    key = ((m - c) ** 2 + K) / (2 * c)
    if (key * 100).denominator != 1:
        raise ItemError("the printed value must land exactly on a hundredth")
    rule = fn(name, "x", f"((x {MINUS} c)² + {num(K)})/(2c)")
    pool = {
        "stated": ("gave the stated value again", v),
        "no_square": ("did not square the difference", ((m - c) + K) / (2 * c)),
        "no_shift": ("used the input itself rather than its distance from c",
                     (m + K) / (2 * c)),
        "squared_input": ("squared the input instead of its distance from c",
                          (m ** 2 + K) / (2 * c)),
    }
    order = ["stated", "no_square", "no_shift", "squared_input"]
    why = (f"{name}(c) = {num(K)}/(2c) = {num(v)} gives c = {num(c)}, and then "
           f"{name}({num(m)}) = ({num((m - c) ** 2)} + {num(K)})/{num(2 * c)} = "
           f"{dec(key, 2)}.")
    P = {"kind": "nlf_param_value", "K": [K.numerator, K.denominator],
         "v": [v.numerator, v.denominator], "m": [m.numerator, m.denominator]}
    return value_item("nlfunc.param_value", "a rule with a constant to find first",
                      "hard", seed, PARAM.format(n=name, rule=rule, v=num(v), m=num(m)),
                      key, pick(pool, order, wrongs), rng, P, why, fmt=fmt,
                      fmt_value=lambda val: dec(val, 2), signed=False)


# ------------------------------------------------------- absolute values

ABS_COMPOSE = ("The functions f and g are defined by the given equations. {f} {g} If "
               "f({a}) = c, where c is a constant, what is the value of g(c)?")
ABS_SCALED = ("The function {n} is defined by {n}(x) = |x|/a {minus} {t}, where "
              "a < 0. What is the product of {n}({m}a) and {n}({k}a)?")


def abs_value(rng: random.Random, seed: int, *, mode=None, p=None, b=None, a=None,
              d=None, e=None, t=None, m=None, k=None, name=None, fmt="spr") -> object:
    """Absolute value inside a composition, or scaled by a negative constant."""
    mode = mode or rng.choice(["compose", "scaled"])

    if mode == "compose":
        p = q(p if p is not None else rng.randint(2, 9))
        b = q(b if b is not None else rng.randint(2, 6))
        a = q(a if a is not None else rng.choice([-5, -4, -3, 3, 4, 5]))
        d = q(d if d is not None else rng.randint(1, 3))
        e = q(e if e is not None else rng.randint(3, 8))
        inner = -b * a - a ** 2
        c = p + abs(inner)
        if c == d:
            raise ItemError("the second function is undefined at that value")
        key = abs(-c / (c - d)) - c + e
        if key.denominator not in (1, 2, 4, 5, 10, 20, 25, 50, 100):
            raise ItemError("the answer must be enterable as a decimal")
        f_txt = f"f(x) = {num(p)} + |{MINUS}{num(b)}x {MINUS} x²|"
        g_txt = f"g(w) = |{MINUS}w/(w {MINUS} {num(d)})| {MINUS} w + {num(e)}"
        stem = ABS_COMPOSE.format(f=f_txt, g=g_txt, a=num(a))
        why = (f"f({num(a)}) = {num(p)} + |{num(inner)}| = {num(c)}, and "
               f"g({num(c)}) = {num(abs(-c / (c - d)))} {MINUS} {num(c)} + {num(e)} = "
               f"{num(key)}.")
        P = {"kind": "nlf_abs_value", "mode": mode,
             "p": [p.numerator, p.denominator], "b": [b.numerator, b.denominator],
             "a": [a.numerator, a.denominator], "d": [d.numerator, d.denominator],
             "e": [e.numerator, e.denominator]}
    else:
        name = name or rng.choice(["g", "f", "h"])
        t = q(t if t is not None else rng.randint(5, 20))
        m = int(m if m is not None else rng.randint(8, 20))
        k = int(k if k is not None else rng.randint(2, 7))
        if m == k:
            raise ItemError("the two inputs must differ")
        key = (m + t) * (k + t)
        stem = ABS_SCALED.format(n=name, minus=MINUS, t=num(t), m=num(m), k=num(k))
        why = (f"Because a < 0, |{num(m)}a|/a = {MINUS}{num(m)}, so {name}({num(m)}a) = "
               f"{MINUS}{num(m + t)} and {name}({num(k)}a) = {MINUS}{num(k + t)}; their "
               f"product is {num(key)}.")
        P = {"kind": "nlf_abs_value", "mode": mode, "t": [t.numerator, t.denominator],
             "m": m, "k": k}

    return value_item("nlfunc.abs_value", "absolute value in a nonlinear rule", "hard",
                      seed, stem, key, [], rng, P, why, fmt="spr")
