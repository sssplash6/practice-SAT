"""What the constants do to the solution set.

An equation in one variable has one solution, none, or every number, and the
source asks about that in five ways: count the solutions, supply the constant
that makes the two sides identical, supply the one that makes them
contradictory, say which conditions must hold, and -- when the same expression
sits over two different denominators -- locate the expression, which can only
be zero.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text
from ....expr import sign_join
from .kit import VARS, choices, dec, eq_of, num, paren, sent, side, term

__all__ = ["count_solutions", "identity_constant", "no_solution_constant",
           "identity_pair", "no_solution_conditions", "zero_chunk",
           "equivalent_equation"]

WORDS = {
    "text": {"one": "Exactly one", "many": "Infinitely many", "none": "Zero",
             "two": "Exactly two"},
    "digit": {"one": "Exactly 1", "many": "Infinitely many", "none": "None",
              "two": "Exactly 3"},
}
CONSTS = ["k", "a", "b", "c", "r", "s"]


# ----------------------------------------------------------- how many solutions

def count_solutions(rng: random.Random, seed: int, *, style=None, outcome=None,
                    var=None, words="text", frame=None, a=None, b=None, c=None,
                    d=None, e=None, f=None, cf_l=False, cf_r=False) -> Item:
    """One, none, or every number -- and the equation that decides which."""
    style = style or rng.choice(["plain", "plain", "paren"])
    outcome = outcome or rng.choice(["one", "one", "none", "many"])
    if style == "plain" and outcome == "many":
        raise ItemError("an identity in this style prints the same on both sides")
    var = var or rng.choice(VARS)
    frame = frame or rng.choice(["inline", "above"])

    if style == "plain":                            # a*v + b = c*v + d
        a = Q(rng.choice([0, 2, 3, 4, 5, 6, 7, 8, 9, 10]) if a is None else a)
        b = Q(rng.randint(-20, 30) if b is None else b)
        if outcome == "one":
            c = Q(rng.choice([i for i in range(-8, 11) if i != a]) if c is None else c)
            d = Q(rng.randint(-20, 40) if d is None else d)
        else:
            c = Q(a if c is None else c)
            d = Q((b if outcome == "many" else b + rng.choice([-9, -5, -3, 3, 5, 9]))
                  if d is None else d)
        m1, k1, m2, k2 = a, b, c, d
        eq = eq_of(side(a, b, var, cf_l), side(c, d, var, cf_r))
        P = {"style": style, "a": float(a), "b": float(b), "c": float(c), "d": float(d),
             "e": 0.0, "f": 0.0}
    else:                                           # a(b*v + c) = d(e + f*v)
        a = Q(rng.choice([2, 3, 4, 5, 6, 8, 10, -3, -5, -10]) if a is None else a)
        b = Q(rng.choice([i for i in range(-15, 16) if i]) if b is None else b)
        c = Q(rng.choice([i for i in range(-15, 16) if i]) if c is None else c)
        d = Q(rng.choice([i for i in (-15, -10, -6, -5, -3, -2, 2, 3, 5, 6, 10, 15)])
              if d is None else d)
        if outcome == "many":
            f = Q(a * b / d if f is None else f)
            e = Q(a * c / d if e is None else e)
        elif outcome == "none":
            f = Q(a * b / d if f is None else f)
            e = Q((a * c / d + rng.choice([-4, -2, 2, 4])) if e is None else e)
        else:
            f = Q(rng.choice([i for i in range(-15, 16) if i and i * d != a * b])
                  if f is None else f)
            e = Q(rng.randint(-15, 15) if e is None else e)
        if f.denominator != 1 or e.denominator != 1:
            raise ItemError("a bracketed side must print with whole numbers inside")
        m1, k1, m2, k2 = a * b, a * c, d * f, d * e
        eq = eq_of(paren(a, side(b, c, var)), paren(d, side(f, e, var, const_first=True)))
        P = {"style": style, "a": float(a), "b": float(b), "c": float(c), "d": float(d),
             "e": float(e), "f": float(f)}

    truth = "one" if m1 != m2 else ("many" if k1 == k2 else "none")
    if truth != outcome:
        raise ItemError("the draw does not have the solution set it was asked for")
    w = WORDS[words]
    key = w[truth]
    stem = (sent(f"How many solutions does the equation {eq} have?") if frame == "inline"
            else sent(f"{eq} How many solutions exist to the equation shown above?"))
    P.update({"kind": "lin1_count", "words": words})
    reasons = {
        "one": "solved as usual without noticing that the variable terms cancel",
        "none": "saw the variable terms cancel and stopped before comparing the constants",
        "many": "saw the same coefficient on both sides and called the equation an "
                "identity without comparing the constants",
        "two": "counted the terms rather than the solutions; a linear equation never "
               "has more than one",
    }
    mistakes = [Mis(reasons[t], w[t]) for t in ("one", "none", "many", "two") if t != truth]
    ch, why, letter = assemble_text(key, mistakes, rng)
    said = {"one": "exactly one solution", "none": "no solution",
            "many": "infinitely many solutions"}[truth]
    rationale = (f"Gathering gives {side(m1, k1, var)} on the left and "
                 f"{side(m2, k2, var)} on the right, so the equation has {said}.")
    return Item("lin1.count_solutions", "solution set", "medium", seed, stem, "mcq",
                E(1), letter, rationale, ch, why, ch, params=P)


# --------------------------------------------- the constant that makes it an identity

def identity_constant(rng: random.Random, seed: int, *, shape=None, var=None,
                      letter=None, other=None, fmt=None, a=None, b=None,
                      c=None, d=None, f=None, g=None) -> Item:
    """Infinitely many solutions pins one constant; find it."""
    shape = shape or rng.choice(["same_coef", "factor", "over_minus"])
    var = var or rng.choice(VARS)
    letter = letter or rng.choice([l for l in CONSTS if l != var])
    fmt = fmt or ("spr" if rng.random() < 0.5 else "mcq")

    if shape == "same_coef":                    # a*v + L = a*v + c
        a = Q(rng.randint(2, 15) if a is None else a)
        c = Q(rng.choice([i for i in range(-20, 31) if i]) if c is None else c)
        key = c
        eq = eq_of(sign_join([term(a, var), letter]), side(a, c, var))
        detail = f"{letter} is a constant"
        P = {"a": float(a), "b": 0.0, "c": float(c), "d": 1.0, "f": 1.0, "g": 0.0}
        mistakes = [Mis("changed the sign of the constant when matching the two sides", -c),
                    Mis("divided the constant by the coefficient of the unknown", c / a),
                    Mis("multiplied the constant by the coefficient of the unknown", c * a),
                    Mis("added the coefficient to the constant", c + a),
                    Mis("reported the coefficient of the unknown instead", a)]
    elif shape == "factor":                     # a*v + b = L(v + c)   with b = a*c
        a = Q(rng.randint(2, 12) if a is None else a)
        c = Q(rng.choice([i for i in range(-15, 16) if i]) if c is None else c)
        b = Q(a * c if b is None else b)
        if b != a * c:
            raise ItemError("the equation cannot be an identity for any constant")
        key = a
        eq = eq_of(side(a, b, var), f"{letter}({side(1, c, var)})")
        detail = f"{letter} is a constant"
        P = {"a": float(a), "b": float(b), "c": float(c), "d": 1.0, "f": 1.0, "g": 0.0}
        mistakes = [Mis("reported the constant term instead of the coefficient", b),
                    Mis("reported the number inside the parentheses", c),
                    Mis("divided the constant term by the number inside the "
                        "parentheses and then added", b / c + a if c else None),
                    Mis("added the two numbers on the left", a + b),
                    Mis("changed the sign of the coefficient", -a)]
    else:                                       # (a*v + b)/d - L/f = g(v - c)
        a = Q(rng.choice([4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 24]) if a is None else a)
        d = Q(rng.choice([2, 3, 4, 5, 6]) if d is None else d)
        b = Q(rng.choice([i for i in range(-40, 41) if i]) if b is None else b)
        f = Q(rng.choice([3, 4, 5, 7, 9, 11, 13]) if f is None else f)
        c = Q(rng.choice([i for i in range(-12, 13) if i]) if c is None else c)
        gl = other or rng.choice([l for l in CONSTS if l not in (var, letter)])
        if (a % d) != 0 or (b % d) != 0:
            raise ItemError("the quotient must print as whole numbers")
        key = f * (b / d + (a / d) * c)
        if key <= 0 or key.denominator != 1:
            raise ItemError("the stem promises a positive whole constant")
        eq = (f"({side(a, b, var)})/{num(d)} - {letter}/{num(f)} = "
              f"{gl}({side(1, -c, var)})")
        detail = f"{letter} and {gl} are constants, and {letter} > 0"
        P = {"a": float(a), "b": float(b), "c": float(c), "d": float(d),
             "f": float(f), "g": 0.0}
        mistakes = [Mis("matched the constants but left out the term the bracket "
                        "contributes", f * b / d),
                    Mis("used the wrong sign for the number inside the parentheses",
                        f * (b / d - (a / d) * c)),
                    Mis("forgot to multiply by the denominator under the constant",
                        b / d + (a / d) * c),
                    Mis("matched only the coefficients of the unknown", a / d)]
        shape = "over_minus"

    stem = sent(f"{eq} In the given equation, {detail}. If the equation has infinitely "
                f"many solutions, what is the value of {letter}?")
    P.update({"kind": "lin1_identity_constant", "shape": shape})
    rationale = (f"The two sides can only agree for every {var} if {letter} = "
                 f"{num(key)}.")
    ex = E(key)
    if fmt == "spr":
        if ex.coef.denominator > 1000:
            raise ItemError("this grid-in answer would not be enterable")
        return Item("lin1.identity_constant", "solution set", "medium", seed, stem,
                    "spr", ex, ex.gridin(), rationale, params=P)
    ch, tex, why, letter_ = choices(ex, [m for m in mistakes if m.value is not None], rng)
    return Item("lin1.identity_constant", "solution set", "medium", seed, stem, "mcq",
                ex, letter_, rationale, ch, why, tex, params=P)


# ------------------------------------------- the constant that removes the solution

def no_solution_constant(rng: random.Random, seed: int, *, shape=None, var=None,
                         letter=None, fmt=None, a=None, b=None, c=None, d=None,
                         p=None, q=None) -> Item:
    """No solution pins the coefficient; find the constant that does it."""
    shape = shape or rng.choice(["coef_zero", "match_coef"])
    var = var or rng.choice(VARS)
    letter = letter or rng.choice([l for l in CONSTS if l != var])
    fmt = fmt or ("spr" if rng.random() < 0.35 else "mcq")

    if shape == "coef_zero":                    # (L - c)v = d
        c = Q(rng.choice([i for i in range(-15, 16) if i]) if c is None else c)
        d = Q(rng.choice([i for i in range(-20, 41) if i]) if d is None else d)
        key = c
        eq = eq_of(f"({side(1, -c, letter)}){var}", num(d))
        detail = f"{letter} is a constant"
        P = {"a": 0.0, "b": 0.0, "c": float(c), "d": float(d), "p": 0.0, "q": 1.0}
        mistakes = [Mis("divided the right-hand value by the constant in the "
                        "parentheses", d / c if c else None),
                    Mis("added the constant in the parentheses to the right-hand value",
                        c + d),
                    Mis("subtracted the constant in the parentheses from the "
                        "right-hand value", d - c),
                    Mis("reported the right-hand value", d),
                    Mis("changed the sign of the constant in the parentheses", -c)]
    else:                                       # a(L*v + b) = (p/q)v + d
        a = Q(rng.randint(2, 9) if a is None else a)
        b = Q(rng.choice([i for i in range(-20, 21) if i]) if b is None else b)
        q = Q(rng.choice([3, 5, 7, 9, 11, 13, 17, 19]) if q is None else q)
        p = Q(rng.choice([i for i in range(2, 90) if i % int(q)]) if p is None else p)
        d = Q(rng.choice([i for i in range(-30, 61) if i]) if d is None else d)
        if a * b == d:
            raise ItemError("with these numbers the equation is an identity, not empty")
        key = p / (q * a)
        eq = eq_of(f"{num(a)}({sign_join([letter + var, num(b)])})",
                   side(Q(p) / q, d, var))
        detail = f"{letter} is a constant"
        P = {"a": float(a), "b": float(b), "c": 0.0, "d": float(d),
             "p": float(p), "q": float(q)}
        mistakes = [Mis("matched the coefficients but forgot the number outside the "
                        "parentheses", p / q),
                    Mis("multiplied by the number outside the parentheses instead of "
                        "dividing by it", p * a / q),
                    Mis("inverted the fraction", q / (p * a) if p else None),
                    Mis("used the constant term instead of the coefficient", b)]

    stem = sent(f"{eq} In the given equation, {detail}. If the equation has no "
                f"solution, what is the value of {letter}?")
    P.update({"kind": "lin1_no_solution_constant", "shape": shape})
    rationale = (f"The equation is contradictory only when the two coefficients of "
                 f"{var} agree, which needs {letter} = {num(key)}.")
    ex = E(key)
    if fmt == "spr":
        if ex.coef.denominator > 1000:
            raise ItemError("this grid-in answer would not be enterable")
        return Item("lin1.no_solution_constant", "solution set", "hard", seed, stem,
                    "spr", ex, ex.gridin(), rationale, params=P)
    ch, tex, why, ltr = choices(ex, [m for m in mistakes if m.value is not None], rng)
    return Item("lin1.no_solution_constant", "solution set", "hard", seed, stem, "mcq",
                ex, ltr, rationale, ch, why, tex, params=P)


# -------------------------------------------------- both constants, as a pair

def identity_pair(rng: random.Random, seed: int, *, var=None, c=None, d=None,
                  e=None) -> Item:
    """a(c - v) - b = d - e*v, for infinitely many solutions: name a and b."""
    var = var or rng.choice([v for v in VARS if v not in ("a", "b")])
    c = Q(rng.choice([i for i in range(2, 13)]) if c is None else c)
    d = Q(rng.choice([i for i in range(-20, 21) if i]) if d is None else d)
    e = Q(rng.choice([i for i in range(2, 10)]) if e is None else e)
    a, b = e, e * c - d
    if b == 0 or a == b or -d == b:
        raise ItemError("two of the four option pairs would read the same")
    eq = eq_of(sign_join([f"a({side(-1, c, var, const_first=True)})", "-b"]),
               side(-e, d, var, const_first=True))
    # the source displays the equation above the sentence, so it gets its own
    # line here; sent() would collapse the break, so it is joined afterwards
    stem = eq + "\n" + sent("In the equation above, a and b are constants. If the "
                            "equation has infinitely many solutions, what are the "
                            "values of a and b?")
    key = f"a = {num(a)} and b = {num(b)}"
    mistakes = [
        Mis("matched the constant terms without distributing a through the brackets",
            f"a = {num(a)} and b = {num(-d)}"),
        Mis("took the sign of the coefficient from the right side and then dropped "
            "the minus on the constant", f"a = {num(-a)} and b = {num(a * c + d)}"),
        Mis("took the sign of the coefficient from the right side without noticing "
            "the minus inside the brackets", f"a = {num(-a)} and b = {num(-a * c - d)}"),
        Mis("solved for b before a and used the right-hand coefficient",
            f"a = {num(a)} and b = {num(a * c + d)}")]
    P = {"kind": "lin1_identity_pair", "c": float(c), "d": float(d), "e": float(e)}
    ch, why, letter = assemble_text(key, mistakes, rng)
    rationale = (f"Matching the {var}-terms gives a = {num(a)}, and then the constants "
                 f"give {num(a)}({num(c)}) - b = {num(d)}, so b = {num(b)}.")
    return Item("lin1.identity_pair", "solution set", "hard", seed, stem, "mcq",
                E(1), letter, rationale, ch, why, ch, params=P)


# ------------------------------------------------ which statements must be true

LABELS = ["I only", "II only", "III only", "I and II only", "I and III only",
          "II and III only", "I, II, and III"]
LABEL_REASON = {
    "I only": "checked the coefficients and stopped before the constants",
    "II only": "matched the constants and never compared the coefficients",
    "III only": "compared the constants but not the coefficient of the unknown",
    "I and II only": "read the constant straight off the equation instead of dividing "
                     "it by the coefficient",
    "I and III only": "matched the coefficient and then demanded the constants differ",
    "II and III only": "worked on the constants only and left the coefficient open",
    "I, II, and III": "assumed every statement offered about the constants has to hold",
    "None": "read 'no solutions' as meaning nothing at all can be pinned down",
}


def _label(flags: list[bool]) -> str:
    names = [n for n, t in zip(("I", "II", "III"), flags) if t]
    if len(names) == 3:
        return "I, II, and III"
    return f"{' and '.join(names)} only"


def no_solution_conditions(rng: random.Random, seed: int, *, var=None, m=None, c=None,
                           picks=None, options=None) -> Item:
    """m*v + c = a(v + b) has no solutions -- which statements must hold?"""
    var = var or rng.choice([v for v in VARS if v not in ("a", "b")])
    m = Q(rng.choice([i for i in range(2, 20) if i != 1]) if m is None else m)
    c = Q(rng.choice([i for i in range(2, 30)]) if c is None else c)
    if m == 1 or c == m or Q(c, 1) / m == c:
        raise ItemError("two of the statements would say the same thing")
    pool = {
        "a_is_m": (f"a = {num(m)}", True),
        "a_not_m": (f"a ≠ {num(m)}", False),
        "b_is_c": (f"b = {num(c)}", False),
        "b_not_ratio": (f"b ≠ {num(c / m)}", True),
        "b_is_ratio": (f"b = {num(c / m)}", False),
        "a_is_c": (f"a = {num(c)}", False),
        "ab_not_c": (f"ab ≠ {num(c)}", True),
    }
    picks = picks or rng.sample(list(pool), 3)
    if len(picks) != 3 or len(set(picks)) != 3:
        raise ItemError("three distinct statements are needed")
    for pair in (("a_is_m", "a_not_m"), ("b_not_ratio", "b_is_ratio")):
        if set(pair) <= set(picks):
            raise ItemError("two of the statements contradict each other")
    texts = [pool[k][0] for k in picks]
    flags = [pool[k][1] for k in picks]
    if not any(flags):
        raise ItemError("at least one statement must be true, or the key is 'none'")
    key = _label(flags)
    numbered = " ".join(f"{r}. {t}" for r, t in zip(("I", "II", "III"), texts)) + "."
    stem = sent(f"The equation {side(m, c, var)} = a({side(1, 0, var)} + b), where a "
                f"and b are constants, has no solutions. Which of the following must "
                f"be true? {numbered}")
    pool_labels = options or [l for l in LABELS if l != key]
    mistakes = [Mis(LABEL_REASON.get(l, "picked a combination the algebra does not "
                                        "support"), l)
                for l in pool_labels if l != key]
    rng.shuffle(mistakes)
    P = {"kind": "lin1_conditions", "m": float(m), "c": float(c), "picks": list(picks)}
    ch, why, letter = assemble_text(key, mistakes, rng)
    rationale = (f"No solution needs a = {num(m)} with a*b ≠ {num(c)}, so b ≠ "
                 f"{num(c / m)}, which leaves {key} true.")
    return Item("lin1.no_solution_conditions", "solution set", "hard", seed, stem,
                "mcq", E(1), letter, rationale, ch, why, ch, params=P)


# ------------------------------------- the same expression over two denominators

def _span(lo, hi) -> str:
    def one(v):
        v = Q(v)
        return num(v) if v.denominator == 1 else dec(v)
    return f"{one(lo)} and {one(hi)}"


def zero_chunk(rng: random.Random, seed: int, *, var=None, c=None, p=None, q=None,
               spans=None) -> Item:
    """(v + c)/p = (v + c)/q forces the bracket to zero; locate it."""
    var = var or rng.choice(VARS)
    c = Q(rng.choice([i for i in range(-12, 13) if i]) if c is None else c)
    p = Q(rng.choice([2, 3, 4, 5, 6, 7]) if p is None else p)
    q = Q(rng.choice([i for i in (8, 9, 10, 11, 12, 13, 14, 15)]) if q is None else q)
    if p == q:
        raise ItemError("two equal denominators make the equation an identity")
    inner = side(1, c, var)
    v0 = -c
    targets = [
        (v0, f"solved for {var} and located that instead of {inner}"),
        (-c if c > 0 else c, "located the number printed inside the parentheses"),
        (c, "located the number printed inside the parentheses"),
        ((p + q) / 2, "averaged the two denominators instead of solving"),
        (-(p + q) / 2, "averaged the two denominators and kept the wrong sign"),
        (q - p, "subtracted the two denominators"),
        (p, "located the first denominator"),
        (q, "located the second denominator"),
        (-p, "located the first denominator with the sign reversed"),
        (-q, "located the second denominator with the sign reversed"),
    ]
    if spans is None:
        wanted = [-q, v0, q - p]
        if len(set(wanted)) != 3 or any(t == 0 for t in wanted):
            raise ItemError("two of the wrong ranges would mean the same thing")
        spans = [(-rng.randint(1, 4), rng.randint(1, 4))]
        for t in wanted:
            w = rng.randint(1, 3)
            lo, hi = t - w, t + w
            if lo <= 0 <= hi:
                raise ItemError("a wrong range would sit on the answer")
            spans.append((lo, hi))
    if len(spans) != 4:
        raise ItemError("four ranges are needed")

    key, mistakes, used = None, [], set()
    for lo, hi in spans:
        text = _span(lo, hi)
        if Q(lo) < 0 < Q(hi):
            if key is not None:
                raise ItemError("two option ranges contain zero")
            key = text
            continue
        why = next((r for t, r in targets
                    if Q(lo) < Q(t) < Q(hi) and r not in used), None)
        if why is None:
            raise ItemError("a range that no unused misconception would produce")
        used.add(why)
        mistakes.append(Mis(why, text))
    if key is None or len(mistakes) != 3:
        raise ItemError("the ranges do not make a usable option set")
    if not any(m.value.strip().startswith("-") for m in mistakes):
        raise ItemError("the key would be the only range that starts negative")

    eq = eq_of(f"({inner})/{num(p)}", f"({inner})/{num(q)}")
    stem = sent(f"If {eq}, the value of {inner} is between which of the following "
                f"pairs of values?")
    P = {"kind": "lin1_zero_chunk", "c": float(c), "p": float(p), "q": float(q),
         "spans": [[float(Q(lo)), float(Q(hi))] for lo, hi in spans]}
    ch, why, letter = assemble_text(key, mistakes, rng)
    rationale = (f"The two denominators differ, so {inner} can only be 0, which lies "
                 f"between {key}.")
    return Item("lin1.zero_chunk", "solution set", "hard", seed, stem, "mcq", E(0),
                letter, rationale, ch, why, ch, params=P)


# ---------------------------------------------------- an equivalent equation

def equivalent_equation(rng: random.Random, seed: int, *, var=None, a=None, b=None,
                        d=None, g=None) -> Item:
    """Which equation says the same thing? Divide every term by a common factor."""
    var = var or rng.choice(VARS)
    g = int(g or rng.choice([2, 2, 3, 3, 4, 5, 6]))
    a = Q(int(a) if a is not None else g * rng.randint(2, 12))
    b = Q(int(b) if b is not None else g * rng.choice([i for i in range(-9, 13) if i]))
    d = Q(int(d) if d is not None else g * rng.randint(2, 20))
    if any(x % g for x in (a.numerator, b.numerator, d.numerator)):
        raise ItemError("the stated factor does not divide every term")
    if a == b or a / g == a:
        raise ItemError("the divided equation would look identical")
    # Equivalent equations are the ones with the same solution set, so a wrong
    # option is only wrong if it moves the solution. It does not when b = d:
    # a*v + b = b and a*v + b/g = b/g both say v = 0, and so does the option
    # that subtracts the factor from every term. Two right answers.
    v0 = (d - b) / a
    for A, B, D in ((a / g, b, d / g), (a, b / g, d / g), (a / g, b / g, d),
                    (a - g, b - g, d - g)):
        if A != 0 and (D - B) / A == v0:
            raise ItemError("a wrong option would be equivalent to the equation too")
    eq = eq_of(side(a, b, var), num(d))
    key = eq_of(side(a / g, b / g, var), num(d / g))
    stem = sent(f"Which of the following is equivalent to {eq}?")
    mistakes = [
        Mis("divided the variable term and the right side but left the constant alone",
            eq_of(side(a / g, b, var), num(d / g))),
        Mis("divided the constants but left the variable term alone",
            eq_of(side(a, b / g, var), num(d / g))),
        Mis("divided the left side but forgot the right side",
            eq_of(side(a / g, b / g, var), num(d))),
        Mis("subtracted the common factor from every term instead of dividing by it",
            eq_of(side(a - g, b - g, var), num(d - g)))]
    P = {"kind": "lin1_equivalent", "a": float(a), "b": float(b), "d": float(d),
         "g": float(g), "var": var}
    ch, why, letter = assemble_text(key, [m for m in mistakes if m.value != key], rng)
    rationale = f"Dividing every term of {eq} by {g} gives {key}."
    return Item("lin1.equivalent_equation", "linear equation", "easy", seed, stem,
                "mcq", E(1), letter, rationale, ch, why, ch, params=P)
