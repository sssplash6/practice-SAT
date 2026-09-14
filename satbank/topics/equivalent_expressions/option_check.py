"""Read all four printed options back as mathematics, and check only one is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct: nothing in the engine reads a wrong option as
mathematics, so an item with two right answers passes coverage, transcript,
acceptance, audit, structure, prose and capacity alike. For a topic whose whole
question is "which of these is equivalent", that is the sharpest hole there is.

This script closes it. It re-reads the item as a student receives it -- the
expression printed in the *stem*, and the four option strings -- with its own
reader, evaluates every option at a spread of rational points away from any
pole, and asserts both halves: that exactly one option is equivalent, and that
the equivalent one is the keyed letter.

Nothing is imported from a template, a renderer or a solver, and nothing is
taken from `item.params`: `generate` supplies the finished item and everything
else is parsed off the page. The reader is a second, independent implementation
-- a tokeniser and a shunting-yard evaluator, where `audit.py` uses recursive
descent -- so a bug in one cannot hide in the other.

    PYTHONPATH=. python3 satbank/topics/equivalent_expressions/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 1000 --template eqx.product

Exits non-zero on the first kind of defect it finds, and prints the item.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from fractions import Fraction as Q

from satbank.item import ItemError
from satbank.registry import generate
from satbank.topic import load_topics

MINUS = "−"
SUP = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6",
       "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-"}
DIGITS = "0123456789"


class Unreadable(Exception):
    """The printed text is not something this reader understands."""


# ------------------------------------------- printed expression -> a value
#
# Tokenise, insert the multiplication signs the page leaves out, convert to
# postfix, evaluate. The printing rules are re-implemented here from what the
# page shows, not shared with whatever produced it.

PREC = {"+": 1, "-": 1, "*": 2, "/": 2, "u-": 3, "root": 3, "^": 4}
RIGHT = {"^", "u-", "root"}


def _tokens(text: str) -> list[tuple]:
    out, i, s = [], 0, str(text)
    while i < len(s):
        c = s[i]
        if c in " \t\n":
            i += 1
        elif c in DIGITS or c == ".":
            j = i
            while j < len(s) and (s[j] in DIGITS or s[j] in ".,"):
                j += 1
            out.append(("num", float(s[i:j].replace(",", ""))))
            i = j
        elif c in SUP:
            j, run = i, ""
            while j < len(s) and s[j] in SUP:
                run += SUP[s[j]]
                j += 1
            if j < len(s) and s[j] == "√":            # a root index, not a power
                out.append(("root", int(run)))
                i = j + 1
            else:
                out += [("op", "^"), ("num", float(int(run)))]
                i = j
        elif c == "√":
            out.append(("root", 2))
            i += 1
        elif c == "^":
            out.append(("op", "^"))
            i += 1
        elif c in "+-−":
            out.append(("op", "-" if c in "-−" else "+"))
            i += 1
        elif c in "*·×":
            out.append(("op", "*"))
            i += 1
        elif c == "/":
            out.append(("op", "/"))
            i += 1
        elif c == "(":
            out.append(("lp", None))
            i += 1
        elif c == ")":
            out.append(("rp", None))
            i += 1
        elif c.isalpha():
            out.append(("var", c))
            i += 1
        else:
            raise Unreadable(f"{c!r} in {text!r}")
    return out


def _implicit(ts: list[tuple]) -> list[tuple]:
    """2x, xy, 4(x + 1), (x + 1)(x − 2), y√y -- the page omits the sign."""
    ends, starts = {"num", "var", "rp"}, {"num", "var", "lp", "root"}
    out: list[tuple] = []
    for t in ts:
        if out and out[-1][0] in ends and t[0] in starts:
            out.append(("op", "*"))
        out.append(t)
    return out


def _postfix(ts: list[tuple]) -> list[tuple]:
    out, ops, prev = [], [], None
    for kind, val in ts:
        if kind in ("num", "var"):
            out.append((kind, val))
        elif kind == "root":
            ops.append(("root", val))
        elif kind == "lp":
            ops.append(("lp", None))
        elif kind == "rp":
            while ops and ops[-1][0] != "lp":
                out.append(ops.pop())
            if not ops:
                raise Unreadable("unbalanced brackets")
            ops.pop()
            while ops and ops[-1][0] == "root":
                out.append(ops.pop())
        else:
            op = val
            if op == "-" and (prev is None or prev[0] in ("op", "lp", "root")):
                op = "u-"
            elif op == "+" and (prev is None or prev[0] in ("op", "lp", "root")):
                prev = (kind, val)
                continue
            while ops and ops[-1][0] != "lp":
                top = ops[-1][0] if ops[-1][0] == "root" else ops[-1][1]
                p = PREC[top]
                if p > PREC[op] or (p == PREC[op] and op not in RIGHT):
                    out.append(ops.pop())
                else:
                    break
            ops.append(("op", op))
        prev = (kind, val)
    while ops:
        if ops[-1][0] == "lp":
            raise Unreadable("unbalanced brackets")
        out.append(ops.pop())
    return out


def read(text: str) -> list[tuple]:
    return _postfix(_implicit(_tokens(text)))


def value(rpn: list[tuple], env: dict) -> float:
    stack: list[float] = []
    for kind, val in rpn:
        if kind == "num":
            stack.append(val)
        elif kind == "var":
            if val not in env:
                raise Unreadable(f"no value for {val!r}")
            stack.append(env[val])
        elif kind == "root":
            v = stack.pop()
            if v < 0:
                if val % 2 == 0:
                    raise ValueError("even root of a negative number")
                stack.append(-((-v) ** (1.0 / val)))
            else:
                stack.append(v ** (1.0 / val))
        elif val == "u-":
            stack.append(-stack.pop())
        else:
            b, a = stack.pop(), stack.pop()
            if val == "+":
                stack.append(a + b)
            elif val == "-":
                stack.append(a - b)
            elif val == "*":
                stack.append(a * b)
            elif val == "/":
                if b == 0:
                    raise ZeroDivisionError
                stack.append(a / b)
            else:
                if a < 0 and b != int(b):
                    raise ValueError("negative base, fractional exponent")
                if a == 0 and b < 0:
                    raise ZeroDivisionError
                stack.append(a ** b)
    if len(stack) != 1:
        raise Unreadable("the expression does not reduce to one value")
    return stack[0]


def letters(text: str) -> set:
    return {v for k, v in _tokens(text) if k == "var"}


# ------------------------------------------------------- sampling and equality

WINDOWS = ((1.09, 4.13), (1.03, 1.47), (0.23, 0.91))


def points(names: list[str], window: int, n: int = 22) -> list[dict]:
    """Rational points away from the small denominators the source uses."""
    lo, hi = WINDOWS[window]
    out, s = [], 98765
    for _ in range(n):
        s = (s * 214013 + 2531011) % (1 << 31)
        env = {}
        for k, v in enumerate(names):
            s = (s * 214013 + 2531011) % (1 << 31)
            env[v] = round(lo + (hi - lo) * (s / (1 << 31)), 6)
        out.append(env)
    return out


def _at(rpn, env: dict, defs: list) -> float | None:
    full = dict(env)
    for name, body in defs:
        full[name] = value(body, full)
    v = value(rpn, full)
    if not math.isfinite(v) or abs(v) > 1e13:
        return None
    return v


def same(a, b, names: list[str], defs: list, need: int = 6) -> bool:
    """Do two printed expressions take the same value wherever both are defined?"""
    for window in range(len(WINDOWS)):
        seen = 0
        for env in points(names, window):
            try:
                x, y = _at(a, env, defs), _at(b, env, defs)
            except (ZeroDivisionError, ValueError, OverflowError, Unreadable):
                continue
            if x is None or y is None:
                continue
            if abs(x - y) > 1e-7 * max(1.0, abs(x), abs(y)):
                return False
            seen += 1
        if seen >= need:
            return True
    raise Unreadable("could not sample away from the poles")


# ------------------------------------------------- the question, off the page
#
# What the item asks is read from the printed stem, so a stem and an option set
# that have drifted apart are visible here.

WHERE = re.compile(r",\s*(where|for)\s[^,]*$")
ASKS = [
    re.compile(r"^(?P<e>.+)\nWhich of the following(?: expressions)? is equivalent "
               r"to the (?:given expression|expression above)\?$", re.S),
    re.compile(r"^f\((?P<v>\w)\) = (?P<f>.+)\ng\((?P=v)\) = (?P<g>.+)\nWhich of the "
               r"following expressions is equivalent to f\((?P=v)\)/g\((?P=v)\), "
               r"for .+\?$"),
    re.compile(r"which of the following(?: expressions)? is equivalent to the sum "
               r"of (?P<a>.+?) and (?P<b>.+?)\s*\?$", re.I),
    re.compile(r"^Which expression represents the product of (?P<a>.+?) and "
               r"(?P<b>.+?)\s*\?$"),
    re.compile(r"^The expression (?P<e>.+?), where .+?, is equivalent to which of "
               r"the following\?$"),
    re.compile(r"^The expression (?P<e>.+?) is equivalent to which of the "
               r"following\?$"),
    re.compile(r"^If (?P<cond>.+?), which of the following(?: expressions)? is "
               r"(?:equivalent|equal) to (?:the expression )?(?P<e>.+?)\s*\?$"),
    re.compile(r"is (?:equivalent|equal) to (?:the expression )?(?P<e>.+?)\s*\?$"),
    re.compile(r"is an equivalent form of (?P<e>.+?)\s*\?$"),
]


def question(stem: str) -> tuple[str, list]:
    """The expression the stem asks about, and any letters it defines."""
    for rx in ASKS:
        m = rx.search(stem)
        if not m:
            continue
        g = m.groupdict()
        if "f" in g and g.get("f"):
            return f"({g['f']})/({g['g']})", []
        if g.get("a") is not None:
            joiner = "+" if "sum of" in stem else ")("
            expr = (f"({g['a']}) + ({g['b']})" if joiner == "+"
                    else f"({g['a']})({g['b']})")
            return _strip(expr), []
        expr = _strip(g["e"])
        defs = _defs(g.get("cond") or "")
        for name, body in defs:                       # x² = a + b is textual
            if name not in "abcdefghijklmnopqrstuvwxyz":
                expr = expr.replace(name, f"({body})")
        return expr, [(n, b) for n, b in defs if len(n) == 1]
    raise Unreadable(f"cannot see what is being asked in {stem!r}")


def _strip(expr: str) -> str:
    out = WHERE.sub("", expr.strip()).strip()
    return out


def _defs(cond: str) -> list:
    out = []
    for part in cond.split(" and "):
        if part.count("=") != 1 or "≠" in part:
            continue
        name, body = (p.strip() for p in part.split("="))
        if re.fullmatch(r"[a-z]²?", name):
            out.append((name, body))
    return out


# ----------------------------------------------------------------- the checks

def _keyed(item) -> int:
    return "ABCD".index(item.answer)


def check_equivalent(item) -> str:
    """Exactly one printed option is equivalent to the printed expression."""
    expr, defs = question(item.stem)
    names = sorted(letters(expr) | set().union(*(letters(o) for o in item.choices))
                   - {n for n, _ in defs})
    src = read(expr)
    parsed = [(name, read(body)) for name, body in defs]
    hits = [same(src, read(o), names, parsed) for o in item.choices]
    if sum(hits) != 1:
        raise AssertionError(
            f"{sum(hits)} of the four options are equivalent to {expr!r}: "
            + ", ".join(repr(o) for o, h in zip(item.choices, hits) if h))
    if not hits[_keyed(item)]:
        raise AssertionError(
            f"the keyed option {item.choices[_keyed(item)]!r} is not equivalent to "
            f"{expr!r}; {item.choices[hits.index(True)]!r} is")
    return "equivalent to the printed expression"


FACTOR_ASK = re.compile(r"^(?P<poly>.+)\nWhich of the following is a factor of the "
                        r"polynomial above\?$")
ROMAN_ASK = re.compile(r"^(?P<poly>.+)\nI\. (?P<one>.+)\nII\. (?P<two>.+)\nWhich of "
                       r"the expressions above is\(are\) a factor of the given "
                       r"polynomial\?$")


def _divides(poly: str, fac: str, names: list[str]) -> bool:
    """A polynomial has a linear factor exactly when it vanishes on it."""
    P, F = read(poly), read(fac)
    first, rest = names[0], names[1:]
    tested = 0
    for base in (points(rest, 0, 4) if rest else [{}]):
        root = _zero_of(F, first, base)
        if root is None:
            continue
        here = abs(value(P, {**base, first: root}))
        near = max(abs(value(P, {**base, first: root + d})) for d in (0.7, -0.7, 1.3))
        if here > 1e-6 * max(1.0, near):
            return False
        tested += 1
    if not tested:
        raise Unreadable(f"could not find where {fac!r} is zero")
    return True


def _zero_of(F, var: str, base: dict):
    lo, prev = -80.0, None
    while lo <= 80.0:
        try:
            v = value(F, {**base, var: lo})
        except (ZeroDivisionError, ValueError, OverflowError):
            v = None
        if v is not None and prev is not None and prev[1] is not None:
            if (v > 0) != (prev[1] > 0):
                a, b = prev[0], lo
                fa = prev[1]
                for _ in range(90):
                    mid = (a + b) / 2
                    if (value(F, {**base, var: mid}) > 0) == (fa > 0):
                        a = mid
                    else:
                        b = mid
                return (a + b) / 2
        prev = (lo, v)
        lo = round(lo + 0.25, 6)
    return None


def check_factor(item) -> str:
    m = FACTOR_ASK.match(item.stem)
    if m:
        poly = m.group("poly")
        names = sorted(letters(poly))
        hits = [_divides(poly, o, names) for o in item.choices]
        if sum(hits) != 1:
            raise AssertionError(f"{sum(hits)} of the four options divide {poly!r}")
        if not hits[_keyed(item)]:
            raise AssertionError("the keyed option is not a factor")
        return "a factor of the printed polynomial"
    m = ROMAN_ASK.match(item.stem)
    if not m:
        raise Unreadable(f"cannot see what is being asked in {item.stem!r}")
    poly, names = m.group("poly"), sorted(letters(m.group("poly")))
    flags = [_divides(poly, m.group("one"), names),
             _divides(poly, m.group("two"), names)]
    want = {(False, False): "Neither I nor II", (True, False): "I only",
            (False, True): "II only", (True, True): "I and II"}[tuple(flags)]
    hits = [o == want for o in item.choices]
    if sum(hits) != 1:
        raise AssertionError(f"{sum(hits)} options read {want!r}")
    if not hits[_keyed(item)]:
        raise AssertionError(f"the keyed option is {item.choices[_keyed(item)]!r}, "
                             f"but {want!r} is what divides the polynomial")
    return "the true verdict on the two candidates"


# --- the templates whose options are numbers: the letter is put back in
#
# Each of these stems prints an identity with one constant missing. Substituting
# an option's own printed value back into the printed identity decides that
# option on its own, which is what makes the wrong three readable.

LETTER_ASKS = [
    re.compile(r"^The expression (?P<lhs>.+?) is equivalent to (?P<rhs>.+?) for some "
               r"constant (?P<L>\w)\. What is the value of (?P=L) \?$"),
    re.compile(r"^(?P<lhs>.+)\nIf the given expression is rewritten in the form "
               r"(?P<rhs>.+?), where (?P<L>\w) is a constant, what is the value of "
               r"(?P=L) \?$"),
    re.compile(r"^The expression (?P<lhs>.+?) is equivalent to (?P<rhs>.+?), where "
               r"(?P<L>\w) is a constant and \w > 0\. What is the value of "
               r"(?P=L)\?$"),
    re.compile(r"^(?P<lhs>.+)\nThe given expression can be rewritten as (?P<rhs>.+?), "
               r"where (?P<L>\w) is a constant\. What is the value of (?P=L)\?$"),
    re.compile(r"^In the expression (?P<lhs>.+?), (?P<L>\w) is a constant\. This "
               r"expression is equivalent to the expression (?P<rhs>.+?)\. What is "
               r"the value of (?P=L) \?$"),
    re.compile(r"^The expression (?P<lhs>.+?) can be rewritten as (?P<rhs>.+?), where "
               r"(?P<L>\w) is a positive constant\. What is the value of "
               r"(?P=L) \?$"),
]


def check_letter(item) -> str:
    if item.fmt != "mcq":
        return "grid-in: no options to read"
    for rx in LETTER_ASKS:
        m = rx.match(item.stem)
        if m:
            break
    else:
        return check_pair(item)
    lhs, rhs, L = read(m.group("lhs")), read(m.group("rhs")), m.group("L")
    names = sorted((letters(m.group("lhs")) | letters(m.group("rhs"))) - {L})
    hits = []
    for opt in item.choices:
        try:
            u = value(read(opt), {})
        except (Unreadable, ValueError, ZeroDivisionError):
            raise Unreadable(f"cannot read the option {opt!r} as a number")
        ok, seen = True, 0
        for env in points(names, 0):
            try:
                e = {**env, L: u}
                a, b = value(lhs, e), value(rhs, e)
            except (ZeroDivisionError, ValueError, OverflowError):
                continue
            if abs(a - b) > 1e-6 * max(1.0, abs(a), abs(b)):
                ok = False
                break
            seen += 1
        hits.append(ok and seen >= 4)
    if sum(hits) != 1:
        raise AssertionError(f"{sum(hits)} of the four printed values satisfy the "
                             f"identity: {[o for o, h in zip(item.choices, hits) if h]}")
    if not hits[_keyed(item)]:
        raise AssertionError(f"the keyed value {item.choices[_keyed(item)]!r} does "
                             f"not satisfy the identity")
    return "the only constant that makes the identity true"


# --- the stems that hide TWO constants in one identity
#
# "(ky + 2)(3y² − ay + 4) = 12y³ − …  What is the value of ka?" cannot be decided
# one option at a time, so the pair is recovered from the printed equation -- by
# alternating least-squares fits, which needs no algebra on the page -- and all
# four printed numbers are then compared against the combination the stem asks
# for.

PAIR_ASKS = [
    re.compile(r"^(?P<lhs>.+?) = (?P<rhs>.+)\nThe equation above is true for all .+?,"
               r" where (?P<L1>\w) and (?P<L2>\w) are (?:positive )?constants\. What "
               r"is the value of (?P<ask>.+?) \?$"),
    re.compile(r"^The equation (?P<lhs>.+?) = (?P<rhs>.+?) is true for all .+?, where "
               r"(?P<L1>\w) and (?P<L2>\w) are integers\. What is the value of "
               r"(?P<ask>.+?) \?$"),
]


def _corners(lhs, rhs, L1: str, L2: str, env: dict):
    """The residual as r + A·u₁ + B·u₂ + C·u₁u₂, read off four trial values.

    Each letter appears once in the printed identity, so the difference between
    the two sides is bilinear in the pair -- which is all this needs to know.
    """
    def r(a: float, b: float) -> float:
        e = {**env, L1: a, L2: b}
        return value(lhs, e) - value(rhs, e)

    r00 = r(0.0, 0.0)
    A, B = r(1.0, 0.0) - r00, r(0.0, 1.0) - r00
    C = r(1.0, 1.0) - r00 - A - B
    if not all(math.isfinite(v) for v in (r00, A, B, C)):
        raise ValueError("not finite here")
    return r00, A, B, C


def _holds(lhs, rhs, u: dict, envs: list) -> bool:
    seen = 0
    for env in envs:
        try:
            a, b = value(lhs, {**env, **u}), value(rhs, {**env, **u})
        except (ZeroDivisionError, ValueError, OverflowError):
            continue
        if not (math.isfinite(a) and math.isfinite(b)):
            continue
        if abs(a - b) > 1e-6 * max(1.0, abs(a), abs(b)):
            return False
        seen += 1
    return seen >= 4


def _pair_values(lhs, rhs, L1: str, L2: str, envs: list):
    """Both constants, recovered from the printed identity by elimination."""
    rows = []
    for env in envs:
        try:
            rows.append(_corners(lhs, rhs, L1, L2, env))
        except (ZeroDivisionError, ValueError, OverflowError):
            continue
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            ri, Ai, Bi, Ci = rows[i]
            rj, Aj, Bj, Cj = rows[j]
            a2 = Aj * Ci - Cj * Ai
            a1 = rj * Ci + Aj * Bi - Bj * Ai - Cj * ri
            a0 = rj * Bi - Bj * ri
            if abs(a2) < 1e-12:
                if abs(a1) < 1e-12:
                    continue
                roots = [-a0 / a1]
            else:
                disc = a1 * a1 - 4 * a2 * a0
                if disc < 0:
                    continue
                q = math.sqrt(disc)
                roots = [(-a1 + q) / (2 * a2), (-a1 - q) / (2 * a2)]
            for u1 in roots:
                den = Bi + Ci * u1
                if abs(den) < 1e-12:
                    continue
                u = {L1: u1, L2: -(ri + Ai * u1) / den}
                if _holds(lhs, rhs, u, envs):
                    return u
    return None


def check_pair(item) -> str:
    for rx in PAIR_ASKS:
        m = rx.match(item.stem)
        if m:
            break
    else:
        return check_value(item)
    lhs, rhs = read(m.group("lhs")), read(m.group("rhs"))
    L1, L2, ask = m.group("L1"), m.group("L2"), m.group("ask").replace(" ", "")
    names = sorted((letters(m.group("lhs")) | letters(m.group("rhs"))) - {L1, L2})
    got = _pair_values(lhs, rhs, L1, L2, points(names, 0, 8))
    if got is None:
        raise Unreadable(f"no pair of constants closes {item.stem!r}")
    if ask in (L1 + L2, L2 + L1):
        target = got[L1] * got[L2]
    elif ask in (L1 + "+" + L2, L2 + "+" + L1):
        target = got[L1] + got[L2]
    else:
        raise Unreadable(f"cannot read what {ask!r} asks for")
    hits = []
    for opt in item.choices:
        v = value(read(opt), {})
        hits.append(abs(v - target) <= 1e-6 * max(1.0, abs(target)))
    if sum(hits) != 1:
        raise AssertionError(f"{sum(hits)} of the four printed values are "
                             f"{target:g}: {item.choices}")
    if not hits[_keyed(item)]:
        raise AssertionError(f"the keyed option {item.choices[_keyed(item)]!r} is not "
                             f"{target:g}")
    return "the only value the printed identity allows"


SQ_OVER = re.compile(r"^\((?P<v>\w)² − (?P<c>\w)\)/\((?P=v) − (?P<b>\w)\)\n.*could be "
                     r"the value of (?P=c) \?$", re.S)


def check_value(item) -> str:
    """The stems whose property is a fact about the printed number itself."""
    if SQ_OVER.match(item.stem):
        # (v² − c)/(v − b) is v + b only when c is a perfect square
        hits = []
        for opt in item.choices:
            n = value(read(opt), {})
            hits.append(abs(n - round(n)) < 1e-9 and round(n) > 0
                        and math.isqrt(round(n)) ** 2 == round(n))
        if sum(hits) != 1:
            raise AssertionError(f"{sum(hits)} of the four options are perfect "
                                 f"squares: {[o for o, h in zip(item.choices, hits) if h]}")
        if not hits[_keyed(item)]:
            raise AssertionError("the keyed option is not a perfect square")
        return "the only perfect square among the four"
    raise Unreadable(f"no option-level property for {item.stem!r}")


EXPRESSION_TEMPLATES = [
    "eqx.combine_like", "eqx.add_polys", "eqx.distribute", "eqx.product",
    "eqx.expand_square", "eqx.substitute", "eqx.factor_gcf",
    "eqx.factor_quadratic", "eqx.difference_squares", "eqx.complete_square",
    "eqx.monomial_power", "eqx.radical_form", "eqx.telescope",
    "eqx.rational_combine", "eqx.rational_simplify", "eqx.divide_remainder",
]

CHECKS = {name: check_equivalent for name in EXPRESSION_TEMPLATES}
CHECKS["eqx.which_factor"] = check_factor
CHECKS["eqx.match_constant"] = check_letter
CHECKS["eqx.factor_constant"] = check_letter
CHECKS["eqx.rational_combine"] = lambda it: (check_equivalent(it)
                                             if not _numeric(it) else check_pair(it))
CHECKS["eqx.divide_remainder"] = lambda it: (check_equivalent(it)
                                             if not _numeric(it) else check_pair(it))
# nothing to read: every draw of these two is a grid-in
CHECKS["eqx.coef_combination"] = lambda it: "grid-in: no options to read"
CHECKS["eqx.exponent_value"] = lambda it: "grid-in: no options to read"


def _numeric(item) -> bool:
    """Are the four options bare numbers rather than expressions?"""
    try:
        for opt in item.choices:
            float(str(opt).replace(MINUS, "-").replace(",", ""))
    except ValueError:
        return False
    return True


def _mixed(item):
    """A template that prints expressions for some draws and numbers for others."""
    if item.fmt != "mcq":
        return None
    return check_letter if _numeric(item) else check_equivalent


# ------------------------------------------------------------------ driver

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--draws", type=int, default=400,
                    help="seeds to try per template (default 400)")
    ap.add_argument("--template", action="append",
                    help="check only this template; repeatable")
    args = ap.parse_args()
    known = list(load_topics()["equivalent_expressions"].templates)
    missing = [n for n in known if n not in CHECKS]
    if missing:
        print(f"no option-level check for {missing}")
    names = args.template or known

    worst, total, defects = 0, 0, 0
    for name in names:
        checker = CHECKS[name]
        made, bad, what = 0, 0, ""
        for seed in range(args.draws):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            made += 1
            use = checker
            if checker is check_equivalent and item.fmt == "mcq":
                use = _mixed(item) or checker
            elif item.fmt != "mcq":
                what = "grid-in: no options to read"
                continue
            try:
                what = use(item)
            except (AssertionError, Unreadable) as exc:
                bad += 1
                if bad == 1:
                    print(f"\n{name} seed {seed}: {exc}")
                    print(item.pretty())
        total += made
        defects += bad
        mark = "  ok  " if not bad else " FAIL "
        print(f"{mark} {name:<26} {made:>5,} items, {bad} defects   ({what})")
        worst |= 1 if bad else 0
    print(f"\n{total:,} items read, {defects} defects")
    return worst


if __name__ == "__main__":
    sys.exit(main())
