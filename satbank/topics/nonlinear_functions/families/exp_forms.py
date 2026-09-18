"""Reading an exponential's own numbers back out of the form it is written in.

An exponential can be written a great many equivalent ways, and the SAT asks
which of them *shows* something: the growth factor, the y-intercept, the
coefficient of x, the greatest value on a half-line. Equivalence alone is
never the answer -- three of the four options are usually equivalent too --
so every option here is decided by what it displays as well as by what it
means.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction as Q

from ....item import ItemError, Mis
from ..common import (MINUS, dec, num, ordinal, pair, pick, q, sig, signed, sup,
                      text_item, value_item, year)

__all__ = ["exp_rate", "exp_two_points", "exp_display", "exp_rewrite",
           "exp_steps", "exp_power_table"]

BASE_PCT = ("{rule} The function {n} above models the annual salary, in dollars, of "
            "an employee {v} years after starting a job, where a is a constant. If "
            "the employee's salary increases by {pct} each year, what is the value "
            "of a?")
PERIOD_PCT = ("{rule} The function f gives the value, in dollars, of a certain piece "
              "of equipment after x months of use. If the value of the equipment "
              "decreases each year by p% of its value the preceding year, what is "
              "the value of p?")
SIGN = ("The population P of a certain city y years after the last census is modeled "
        "by the equation below, where r is a constant and P₀ is the population when "
        "y = 0. P = P₀(1 + r)^y If during this time the population of the city "
        "{how} by a fixed percent each year, which of the following must be true?")


def exp_rate(rng: random.Random, seed: int, *, mode=None, a=None, r=None, base=None,
             k=None, name=None, var=None, rising=None, fmt="mcq", wrongs=None) -> object:
    """The rate a model grows at, read out of the form it is printed in."""
    mode = mode or rng.choice(["base_from_percent", "percent_from_period", "sign"])

    if mode == "base_from_percent":
        name = name or rng.choice(["S", "V", "A"])
        var = var or rng.choice(["n", "t", "x"])
        a = int(a if a is not None else rng.randrange(15, 90) * 1000)
        r = q(r if r is not None else Q(rng.randint(1, 9), 100))
        key = 1 + r
        rule = f"{name}({var}) = {num(a)}a^{var}"
        pool = {
            "raw": ("gave the percent itself rather than the growth factor", r),
            "ten_raw": ("moved the decimal point one place in the percent", 10 * r),
            "ten_factor": ("moved the decimal point one place before adding 1",
                           1 + 10 * r),
            "decay": ("subtracted the percent from 1 instead of adding it", 1 - r),
        }
        order = ["raw", "ten_raw", "ten_factor", "decay"]
        stem = BASE_PCT.format(rule=rule, n=name, v=var, pct=dec(r * 100) + "%")
        why = (f"A rise of {dec(r * 100)}% multiplies the salary by 1 + {dec(r)}, so "
               f"a = {dec(key)}.")
        P = {"kind": "nlf_exp_rate", "mode": mode, "r": [r.numerator, r.denominator]}
        return value_item("nlfunc.exp_rate", "the growth factor behind a percent",
                          "medium", seed, stem, key, pick(pool, order, wrongs), rng, P,
                          why, fmt=fmt, fmt_value=lambda v: dec(v), signed=False)

    if mode == "percent_from_period":
        a = int(a if a is not None else rng.randrange(10, 90) * 100 + rng.randrange(10, 90))
        base = q(base if base is not None else Q(rng.randrange(35, 96), 100))
        k = int(k if k is not None else 12)
        if k != 12:
            raise ItemError("the stem counts months and asks per year, so the "
                            "exponent's divisor must be twelve")
        key = 100 * (1 - base)
        if key.denominator != 1:
            raise ItemError("the printed percent must be a whole number")
        rule = f"f(x) = {num(a)}({dec(base, 2)})^(x/{k})"
        monthly = round(100 * (1 - float(base) ** (1 / k)))
        pool = {
            "monthly": ("gave the percent lost in one month rather than in a year",
                        q(monthly) if monthly > 0 else None),
            "base_over_k": ("divided the printed base by the number of months in a year",
                            q(round(100 * float(base) / k))),
            "base": ("gave the base itself as a percent", 100 * base),
            "complement_over_k": ("divided the yearly percent by the months in a year",
                                  q(round(float(key) / k))),
        }
        order = ["monthly", "base_over_k", "base", "complement_over_k"]
        why = (f"After 12 months the exponent is 1, so a year multiplies the value "
               f"by {dec(base, 2)} -- a loss of {num(key)}%.")
        P = {"kind": "nlf_exp_rate", "mode": mode,
             "base": [base.numerator, base.denominator], "k": k}
        return value_item("nlfunc.exp_rate", "the yearly percent behind a period form",
                          "hard", seed, PERIOD_PCT.format(rule=rule), key,
                          pick(pool, order, wrongs), rng, P, why, fmt=fmt, signed=False)

    # a *fall* by a fixed percent forces −1 < r < 0; a rise only forces r > 0,
    # which none of the four printed ranges says, so only the fall is drawn
    rising = False
    how = "decreases"
    key = "0 < r < 1" if rising else f"{MINUS}1 < r < 0"
    pool = {
        "below": ("chose the range that would make the factor 1 + r negative",
                  pair(f"r < {MINUS}1", -2)),
        "below_pair": ("chose a range in which 1 + r is negative, so the population "
                       "would change sign from one year to the next",
                       pair(f"{MINUS}2 < r < {MINUS}1", -3)),
        "neg": ("chose a negative r where the population is rising",
                pair(f"{MINUS}1 < r < 0", -1)),
        "pos": ("chose a positive r where the population is falling", pair("0 < r < 1", 1)),
        "big": ("chose r > 1, which would more than double the population each year",
                pair("r > 1", 2)),
    }
    # a free draw needs a second range that opens with a minus sign, or the key
    # is the only option of its printed shape
    order = ["below_pair", "pos", "big"]
    why = (f"The factor 1 + r must be {'greater' if rising else 'less'} than 1 but "
           f"{'' if rising else 'still '}positive, so "
           f"{'r is between 0 and 1' if rising else 'r is between −1 and 0'}.")
    P = {"kind": "nlf_exp_rate", "mode": "sign", "rising": bool(rising)}
    return text_item("nlfunc.exp_rate", "the sign of a growth rate", "hard", seed,
                     SIGN.format(how=how), key, sig(1 if rising else -1),
                     pick(pool, order, wrongs), rng, P, why)


# --------------------------------------------- constants from two conditions

SHIFTED = ("Function {n} is defined by {n}(x) = {MINUS}a^x + b, where a and b are "
           "constants. In the xy-plane, the graph of y = {n}(x) {MINUS} {shift} has "
           "a y-intercept at (0, {v}). The product of a and b is {prod}. What is the "
           "value of a?")
INTERCEPTS = ("The function {n} is defined by {n}(x) = a^x + b, where a and b are "
              "constants. In the xy-plane, the graph of y = {n}(x) has an "
              "x-intercept at ({p}, 0) and a y-intercept at (0, {v}). What is the "
              "value of b?")
TWO_POINTS = ("The function {n} is defined by {n}(x) = a^x + b, where a and b are "
              "positive constants. The graph of y = {n}(x) in the xy-plane passes "
              "through the points (0, {p}) and ({MINUS}{e}, {v}). What is the value "
              "of ab?")


def exp_two_points(rng: random.Random, seed: int, *, mode=None, a=None, b=None,
                   shift=None, e=None, name=None, fmt=None, wrongs=None) -> object:
    """f(x) = ±a^x + b, with a and b pinned down by two printed conditions."""
    mode = mode or rng.choice(["shifted", "intercepts", "two_points"])
    name = name or rng.choice(["f", "g", "h"])

    if mode == "shifted":
        a = q(a if a is not None else rng.randrange(4, 40))
        den = rng.randint(3, 11)
        b = q(b if b is not None else Q(rng.randrange(8, 40), den))
        shift = q(shift if shift is not None else rng.randint(5, 20))
        if a <= 0 or b <= 0:
            raise ItemError("both constants must be positive")
        v = b - 1 - shift
        prod = a * b
        stem = SHIFTED.format(n=name, MINUS=MINUS, shift=num(shift), v=num(v),
                              prod=num(prod))
        why = (f"{name}(0) = {MINUS}1 + b, so b {MINUS} 1 {MINUS} {num(shift)} = "
               f"{num(v)} gives b = {num(b)}, and a = {num(prod)}/{num(b)} = {num(a)}.")
        key = a
        P = {"kind": "nlf_exp_two_points", "mode": mode,
             "shift": [shift.numerator, shift.denominator],
             "v": [v.numerator, v.denominator], "prod": [prod.numerator, prod.denominator]}
        return value_item("nlfunc.exp_two_points", "constants in a shifted exponential",
                          "hard", seed, stem, key, [], rng, P, why, fmt="spr")

    if mode == "intercepts":
        a = int(a if a is not None else rng.randint(2, 20))
        e = int(e if e is not None else rng.choice([2, 2, 3]))
        b = -q(a) ** e
        v = 1 + b
        stem = INTERCEPTS.format(n=name, p=num(e), v=num(v))
        why = (f"{name}(0) = 1 + b = {num(v)} gives b = {num(b)}.")
        P = {"kind": "nlf_exp_two_points", "mode": mode, "e": e,
             "v": [v.numerator, v.denominator]}
        return value_item("nlfunc.exp_two_points", "constants from two intercepts",
                          "hard", seed, stem, b, [], rng, P, why, fmt="spr")

    a = int(a if a is not None else rng.randint(2, 9))
    b = int(b if b is not None else rng.randint(2, 30))
    e = int(e if e is not None else rng.choice([2, 2, 3]))
    p = 1 + b
    v = Q(1, a ** e) + b
    key = q(a * b)
    stem = TWO_POINTS.format(n=name, MINUS=MINUS, p=num(p), e=num(e), v=num(v))
    pool = {
        "used_p": ("used the printed y-value instead of the constant b",
                   q(a) * q(p)),
        "recip": ("took the reciprocal of a rather than a itself", q(b) / q(a)),
        "sum": ("added the two constants instead of multiplying them", q(a) + q(b)),
        "power": ("used a raised to the power instead of a", q(a) ** e * q(b)),
    }
    order = ["used_p", "recip", "sum", "power"]
    why = (f"{name}(0) = 1 + b = {num(p)} gives b = {num(b)}, and "
           f"a^({MINUS}{num(e)}) = {num(v)} {MINUS} {num(b)} = {num(v - b)} gives "
           f"a = {num(a)}, so ab = {num(key)}.")
    P = {"kind": "nlf_exp_two_points", "mode": "two_points",
         "p": [q(p).numerator, q(p).denominator],
         "v": [v.numerator, v.denominator], "e": e}
    return value_item("nlfunc.exp_two_points", "constants from two printed points",
                      "hard", seed, stem, key, pick(pool, order, wrongs), rng, P, why,
                      fmt=fmt or "mcq", signed=False)


# ------------------------------------------- which form displays the extreme

DISPLAY = ("The functions {n1} and {n2} are defined by the given equations, where "
           "x ≥ 0. I. {one} II. {two} Which of the following equations displays, as "
           "a constant or coefficient, the {what} value of the function it defines, "
           "where x ≥ 0?")
ANSWERS = {(True, False): "I only", (False, True): "II only",
           (True, True): "I and II", (False, False): "Neither I nor II"}
REASON = {
    "I only": "only the first equation shows it",
    "II only": "only the second equation shows it",
    "I and II": "both equations show it",
    "Neither I nor II": "neither equation shows it",
}


def exp_display(rng: random.Random, seed: int, *, A=None, base=None, form1=None,
                form2=None, s1=None, s2=None, c1=None, c2=None, rising=None,
                names=None, wrongs=None) -> object:
    """Two equivalent-looking exponentials; which one puts the extreme on show?

    On x ≥ 0 a monotone exponential takes its extreme value at x = 0, so the
    question is only whether the number the form prints in front *is* that
    value. `A(b)^(x + s)` starts at A·b^s, not at A; `A(b^s)(b)^(x − s)`
    starts at A exactly. Which of the two shapes each equation takes, and
    whether its coefficient happens to cancel the shift, are the draw.
    """
    n1, n2 = names or rng.sample(["f", "g", "h", "j"], 2)
    rising = rng.choice([True, False]) if rising is None else rising
    A = int(A if A is not None else rng.randint(11, 90))
    base = q(base if base is not None else
             (Q(rng.randrange(105, 190), 100) if rising else Q(rng.randrange(15, 90), 100)))
    if (base > 1) != bool(rising) or base == 1:
        raise ItemError("a rising model needs a base above 1")
    form1 = form1 or rng.choice(["plain", "shift_up", "coef_down", "coef_up"])
    form2 = form2 or rng.choice(["plain", "shift_up", "coef_down", "coef_up"])
    s1 = int(s1 if s1 is not None else rng.randint(1, 4))
    s2 = int(s2 if s2 is not None else rng.randint(1, 4))

    def build(name, form, sh, c):
        """The printed equation, and the factor its value at 0 differs by."""
        if form == "plain":
            return f"{name}(x) = {num(A)}({dec(base)})^x", q(1)
        if form == "shift_up":
            return (f"{name}(x) = {num(A)}({dec(base)})^(x + {num(sh)})",
                    base ** sh)
        c = q(c) if c is not None else base ** sh
        if len(dec(c).split(".")[-1]) > 4 or c <= 0:
            raise ItemError("the printed coefficient would not be exact")
        if form == "coef_down":
            return (f"{name}(x) = {num(A)}({dec(c)})({dec(base)})^(x {MINUS} {num(sh)})",
                    c * base ** (-sh))
        return (f"{name}(x) = {num(A)}({dec(c)})({dec(base)})^(x + {num(sh)})",
                c * base ** sh)

    one, m1 = build(n1, form1, s1, c1)
    two, m2 = build(n2, form2, s2, c2)
    if one.split("=", 1)[1] == two.split("=", 1)[1]:
        raise ItemError("the two equations would say exactly the same thing")
    shows1, shows2 = m1 == 1, m2 == 1
    key = ANSWERS[(shows1, shows2)]
    pool = {}
    for combo, text in ANSWERS.items():
        if text == key:
            continue
        pool[text] = (REASON[text] + ", which is not what the printed forms do",
                      pair(text, 1 if combo[0] else 0, 1 if combo[1] else 0))
    order = [t for t in ("I only", "II only", "I and II", "Neither I nor II")
             if t != key]
    what = "maximum" if not rising else "minimum"
    why = (f"Both functions are {'increasing' if rising else 'decreasing'}, so each "
           f"takes its {what} value at x = 0; the answer is {key}.")
    P = {"kind": "nlf_exp_display", "A": A, "base": [base.numerator, base.denominator],
         "form1": form1, "form2": form2, "s1": s1, "s2": s2,
         "c1": None if c1 is None else [q(c1).numerator, q(c1).denominator],
         "c2": None if c2 is None else [q(c2).numerator, q(c2).denominator],
         "rising": bool(rising)}
    return text_item("nlfunc.exp_display", "which form shows the extreme value",
                     "hard", seed, DISPLAY.format(n1=n1, n2=n2, what=what, one=one,
                                                  two=two),
                     key, sig(1 if shows1 else 0, 1 if shows2 else 0),
                     pick(pool, order, wrongs), rng, P, why)


# ----------------------------------------- an equivalent form that shows s

REWRITE_Y = ("y = {N}^({k}x + {k}) The graph of the given equation in the xy-plane "
             "has a y-intercept of (r, s). Which of the following equations displays "
             "the value of s as a constant, a coefficient, or the base?")
REWRITE_C = ("For the function f, for each increase in the value of x by c, where c "
             "is a positive constant, the value of f(x) increases by a factor of {F}. "
             "Which of the following equivalent forms of the function f displays 1/c "
             "as a coefficient of x?")


def exp_rewrite(rng: random.Random, seed: int, *, mode=None, m=None, j=None, A=None,
                i=None, c=None, wrongs=None) -> object:
    """Four equivalent equations; only one shows the number the stem names."""
    mode = mode or rng.choice(["yintercept", "coefficient"])

    if mode == "yintercept":
        m = int(m if m is not None else rng.randint(10, 60))
        j = int(j if j is not None else 2)
        kk = int(c if c is not None else rng.choice([2, 2, 3]))
        N = m ** j
        s = N ** kk
        if s > 10 ** 10:
            raise ItemError("the printed y-intercept would run to eleven digits")
        key = f"y = {num(s)}^(x + 1)"
        pool = {
            "root_base": ("rewrote the base as its own root, which shows m rather "
                          "than s",
                          pair(f"y = {num(m)}^({num(j * kk)}x + {num(j * kk)})",
                               m, "root")),
            "coefficient": ("collected a coefficient that comes to the base, not to s",
                            pair(f"y = (1/{num(m)})({num(m ** (j + 1))})"
                                 f"({num(N)})^({num(kk)}x)", N, "coef")),
            "shift": ("moved one factor out of the exponent, which leaves the base on "
                      "show and not s",
                      pair(f"y = (1/{num(N)}){num(N)}^({num(kk)}x + {num(kk + 1)})",
                           N, "shift")),
        }
        order = ["root_base", "coefficient", "shift"]
        why = (f"At x = 0 the equation gives {num(N)}{sup(kk)} = {num(s)}, and "
               f"{num(s)}^(x + 1) has {num(s)} as its base.")
        P = {"kind": "nlf_exp_rewrite", "mode": mode, "m": m, "j": j, "kk": kk}
        return text_item("nlfunc.exp_rewrite", "the form that shows the y-intercept",
                         "hard", seed, REWRITE_Y.format(N=num(N), k=num(kk)), key,
                         sig(s, "base"), pick(pool, order, wrongs), rng, P, why)

    m = int(m if m is not None else rng.choice([2, 3, 5, 6, 7, 10]))
    i = int(i if i is not None else rng.choice([2, 3, 4]))
    A = int(A if A is not None else rng.randrange(12, 90))
    c = int(c if c is not None else i * rng.choice([2, 3, 4]))
    F = m ** i
    if c % i or c == i:
        raise ItemError("the displayed coefficient must be a unit fraction")
    p = Q(i, c)

    def form(iprime):
        coef = Q(i, c * iprime)
        head = num(m) if iprime == 1 else (f"{num(m)}{sup(iprime)}" if iprime == i
                                           else num(m ** iprime))
        return f"f(x) = {num(A)}({head})^(({num(coef)})x)"

    key = form(i)
    pool = {}
    for ip in (1, 2, 3, 4, 6):
        if ip == i or Q(i, c * ip).numerator != 1:
            continue
        if c * ip % i:
            continue
        pool[f"base{ip}"] = (
            f"shows {num(Q(i, c * ip))} as the coefficient of x rather than 1/c",
            pair(form(ip), m ** ip, Q(i, c * ip)))
    if c % i == 0 and c // i >= 2:
        outer = Q(1, c // i)
        pool["nested"] = (
            f"shows {num(Q(1, i))} inside the bracket rather than 1/c",
            pair(f"f(x) = {num(A)}({num(m ** i)}^(({num(Q(1, i))})x))^({num(outer)})",
                 m ** i, Q(1, i)))
    order = sorted(pool)
    if len(pool) < 3:
        raise ItemError("not enough equivalent forms to print four options")
    why = (f"f increases by a factor of {num(F)} whenever x rises by {num(c)}, so "
           f"f(x) = {num(A)}({num(F)})^(x/{num(c)}), and writing the base as "
           f"{num(m)}{sup(i)} shows 1/{num(c)} as the coefficient of x.")
    P = {"kind": "nlf_exp_rewrite", "mode": "coefficient", "m": m, "i": i, "A": A,
         "c": c}
    return text_item("nlfunc.exp_rewrite", "the form that shows 1/c", "hard", seed,
                     REWRITE_C.format(F=num(F)), key, sig(m ** i, Q(1, c)),
                     pick(pool, order, wrongs), rng, P, why)


# --------------------------------------------------- geometric step counting

BOUNCE = ("A rubber ball bounces upward one-{word} the height that it falls each "
          "time it hits the ground. If the ball was originally dropped from a "
          "distance of {h} feet above the ground, what was its maximum height above "
          "the ground, in feet, between the {n1} and {n2} time it hit the ground?")
DROP = ("For the function f, f(0) = {a}, and for each increase in x by 1, the value "
        "of f(x) decreases by {pct}. What is the value of f({n})?")
MOORE = ("According to Moore's law, the number of transistors included on "
         "microprocessors doubles every {k} years. In {y0}, a microprocessor was "
         "introduced that had {a} transistors. Based on this information, in which "
         "of the following years does Moore's law estimate the number of transistors "
         "to reach {target}?")
CULTURE = ("A culture of bacteria is growing at an exponential rate, as shown in the "
           "table above. At this rate, on which day would the number of bacteria per "
           "milliliter reach {target}?")
WORDS = {2: "half", 3: "third", 4: "fourth", 5: "fifth"}


def exp_steps(rng: random.Random, seed: int, *, ask=None, mode=None, a=None, den=None,
              n=None, r=None, k=None, y0=None, start=None, power=None,
              wrongs=None) -> object:
    """A geometric sequence: the value after so many steps, or the step it reaches."""
    ask = ask or rng.choice(["value", "steps"])

    if ask == "value":
        mode = mode or rng.choice(["bounce", "drop"])
        if mode == "bounce":
            den = int(den if den is not None else rng.choice([2, 3, 4, 5]))
            a = q(a if a is not None else rng.randrange(8, 80) * Q(5, 10) * 2)
            n = int(n if n is not None else rng.randint(2, 4))
            key = a / q(den) ** n
            if not (q(key) * 100).denominator == 1:
                raise ItemError("the answer must be enterable to the nearest cent")
            stem = BOUNCE.format(word=WORDS[den], h=dec(a, 1), n1=ordinal(n),
                                 n2=ordinal(n + 1))
            why = (f"Each bounce reaches one-{WORDS[den]} of the previous height, so "
                   f"after {num(n)} bounces the height is {dec(a, 1)}/{num(den ** n)} "
                   f"= {dec(key)} feet.")
            P = {"kind": "nlf_exp_steps", "ask": ask, "mode": mode,
                 "a": [q(a).numerator, q(a).denominator], "den": den, "n": n}
        else:
            a = q(a if a is not None else rng.randint(12, 400))
            r = q(r if r is not None else Q(rng.randrange(10, 95, 5), 100))
            n = int(n if n is not None else rng.randint(2, 3))
            key = a * (1 - r) ** n
            if (q(key) * 100).denominator != 1:
                raise ItemError("the answer must be enterable to the nearest hundredth")
            stem = DROP.format(a=num(a), pct=dec(r * 100) + "%", n=num(n))
            why = (f"Each step multiplies by {dec(1 - r)}, so f({num(n)}) = "
                   f"{num(a)}({dec(1 - r)}){sup(n)} = {num(key)}.")
            P = {"kind": "nlf_exp_steps", "ask": ask, "mode": mode,
                 "a": [q(a).numerator, q(a).denominator],
                 "r": [r.numerator, r.denominator], "n": n}
        return value_item("nlfunc.exp_steps", "a geometric sequence step by step",
                          "medium", seed, stem, key, [], rng, P, why, fmt="spr")

    mode = mode or rng.choice(["moore", "culture"])
    power = int(power if power is not None else rng.randint(2, 5))
    if mode == "moore":
        k = int(k if k is not None else rng.choice([2, 3]))
        y0 = int(y0 if y0 is not None else rng.randrange(1970, 2005))
        a = int(a if a is not None else rng.randrange(20, 90) * 10000)
        target = a * 2 ** power
        key = q(y0 + k * power)
        pool = {
            "one_period": ("counted a single doubling", q(y0 + k)),
            "one_too_many": ("counted one doubling too many", q(y0 + k * (power + 1))),
            "period_ratio": ("multiplied the period by the ratio rather than by the "
                             "number of doublings", q(y0 + k * 2 ** power)),
            "ratio_years": ("added one year for each doubling of the ratio rather "
                            "than the period", q(y0 + 2 ** power)),
            "one_short": ("counted one doubling too few", q(y0 + k * (power - 1))),
        }
        order = ["one_period", "one_too_many", "period_ratio", "ratio_years",
                 "one_short"]
        stem = MOORE.format(k=num(k), y0=year(y0), a=num(a), target=num(target))
        why = (f"{num(target)} is {num(2 ** power)} times {num(a)}, which is "
               f"{num(power)} doublings, so it takes {num(k * power)} years: "
               f"{year(y0 + k * power)}.")
        P = {"kind": "nlf_exp_steps", "ask": ask, "mode": mode, "y0": y0, "k": k,
             "a": a, "power": power}
        return value_item("nlfunc.exp_steps", "how long a doubling takes", "medium",
                          seed, stem, key, pick(pool, order, wrongs), rng, P, why,
                          fmt_value=lambda v: year(v), signed=False)

    start = int(start if start is not None else rng.choice([25, 50, 15, 20]))
    exp0 = int(k if k is not None else rng.choice([4, 5, 6]))
    power = int(power) if power is not None else rng.randint(7, 14)
    if power < rows_shown() + 2:
        raise ItemError("the target must lie well past the rows the table prints")
    table = [["Day", "Number of bacteria per milliliter at end of day"]]
    for i in range(3):
        table.append([str(i + 1), _sci(q(start) * 2 ** i / 10, exp0)])
    target = _sci(q(start) * 2 ** power / 10, exp0)
    key = f"Day {power + 1}"
    pool = {
        "no_offset": ("counted the doublings but forgot that the table starts on day 1",
                      pair(f"Day {power}", power)),
        "half": ("halved the number of doublings", pair(f"Day {power // 2 + 1}",
                                                        power // 2 + 1)),
        "from_third": ("counted the doublings from the third row of the table and "
                       "forgot to add those first days on",
                       pair(f"Day {power - 2}", power - 2)),
        "two_short": ("counted two doublings too few", pair(f"Day {power - 1}",
                                                            power - 1)),
        "plus_two": ("counted one doubling too many", pair(f"Day {power + 2}",
                                                           power + 2)),
    }
    order = [n for n in ("no_offset", "from_third", "half", "two_short", "plus_two")
             if _day_of(pool[n]) >= 1]
    why = (f"The count doubles every day, so it is multiplied by {num(2 ** power)} "
           f"after {num(power)} more days: day {num(power + 1)}.")
    P = {"kind": "nlf_exp_steps", "ask": ask, "mode": "culture", "start": start,
         "exp0": exp0, "power": power}
    return text_item("nlfunc.exp_steps", "the day a doubling count is reached",
                     "hard", seed, CULTURE.format(target=target), key, sig(power + 1),
                     pick(pool, order, wrongs), rng, P, why, table=table)


def _day_of(entry) -> int:
    return int(entry[1][1][0])


def rows_shown() -> int:
    """How many days the culture table prints."""
    return 3


def _sci(mant, exp0: int) -> str:
    """'2.5 × 10⁵' -- the way the source prints a bacterial count."""
    m = q(mant)
    e = exp0
    while m >= 10:
        m /= 10
        e += 1
    while m < 1:
        m *= 10
        e -= 1
    return f"{dec(m, 1)} × 10{sup(e)}"


# ------------------------------------------ an exponent read off a table

POWER_TABLE = ("For the exponential function {n}, the table above shows several "
               "values of x and their corresponding values of {n}(x), where a is a "
               "constant greater than 1. If k is a constant and {n}(k) = a{target}, "
               "what is the value of k?")


def exp_power_table(rng: random.Random, seed: int, *, step=None, first=None, k=None,
                    rows=None, name=None) -> object:
    """f(x) = a^(mx + c), given as a column of powers of a; solve f(k) = a^N."""
    name = name or rng.choice(["f", "g", "h"])
    step = int(step if step is not None else rng.randint(2, 6))
    first = int(first if first is not None else rng.randint(1, 6))
    rows = int(rows if rows is not None else 3)
    k = int(k if k is not None else rng.randint(5, 20))
    if k <= rows:
        raise ItemError("the question must reach past the printed rows")
    target = first + step * (k - 1)
    if target > 400:
        raise ItemError("the printed exponent would be unreadably large")
    table = [["x", f"{name}(x)"]]
    for i in range(rows):
        e = first + step * i
        table.append([str(i + 1), "a" if e == 1 else "a" + sup(e)])
    shape = signed(f"{num(step)}x", first - step)
    why = (f"The exponent rises by {num(step)} for each step in x, so {name}(x) = "
           f"a^({shape}); setting that exponent to {num(target)} gives x = {num(k)}.")
    P = {"kind": "nlf_exp_power_table", "step": step, "first": first, "rows": rows,
         "target": target}
    return value_item("nlfunc.exp_power_table", "an exponent read off a table", "hard",
                      seed, POWER_TABLE.format(n=name, target=sup(target)), q(k), [],
                      rng, P, why, fmt="spr", table=table)
