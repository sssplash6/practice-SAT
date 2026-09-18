"""Read the printed page back, and check only one of the four options is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct, because nothing in the engine reads a wrong option
as mathematics. An item with two right answers therefore passes every gate the
engine has.

For this topic that hole is not theoretical. Squaring a radical and clearing a
denominator both invent roots the printed equation does not have, and a line
meets a curve twice, so "which of the following is a solution" has two answers
unless something stops it. This script substitutes every printed option back into
the **printed** equation -- the radical still a radical, the denominators still
denominators -- and asserts that exactly one of them satisfies it and that it is
the keyed one. Where the options are points, equations, solution sets or
statements, the same shape applies to those. Where the item carries a figure, the
figure is read back out of its own SVG and the options are checked against the
picture rather than against the parameters that drew it.

It imports `generate` to obtain a finished item, exactly as a student would
receive it, and `expr.parse` to evaluate printed text. It imports nothing from
this topic: no template, no renderer, no `kit`, no `audit`.

    PYTHONPATH=. python3 satbank/topics/nonlinear_equations_and_systems/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 2000 --template nleq.radical_equation
    PYTHONPATH=. python3 .../option_check.py --selftest

Exits non-zero on the first kind of defect it finds, and prints the item.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from fractions import Fraction as Q

from satbank.expr import ParseError, parse
from satbank.item import ItemError
from satbank.registry import generate

MINUS = "−"
TOL = 1e-7


class Unreadable(Exception):
    """The printed page is not something this reader understands."""


# ------------------------------------------------------- printed text -> value

_RUN = re.compile(r"[A-Za-z][A-Za-z_0-9]*")


def _split(text: str, env: dict) -> str:
    """`cy` is c times y. `expr.parse` lexes a letter run as a single name,
    which is right for `V_B` and wrong for a product, so the run is split into
    the longest names the caller has values for."""
    def repl(m):
        run = m.group()
        if run in env or run in ("sqrt", "pi"):
            return run
        parts, i = [], 0
        while i < len(run):
            for j in range(len(run), i, -1):
                if run[i:j] in env:
                    parts.append(run[i:j])
                    i = j
                    break
            else:
                return run
        return "*".join(parts)

    return _RUN.sub(repl, text)


def value(text: str, **env) -> float:
    """What a printed expression comes to. Raises on anything unreadable."""
    return parse(_split(text, env))(**env)


def number(text: str):
    """A printed option as a number: 40, −15, −550/9, 20.25, 1,200; else None."""
    t = text.replace(MINUS, "-").replace(",", "").strip()
    try:
        if "/" in t:
            a, b = t.split("/", 1)
            return float(a) / float(b)
        return float(t)
    except (ValueError, ZeroDivisionError):
        return None


def sides(line: str) -> tuple:
    """A printed equation as its two sides."""
    if line.count("=") != 1:
        raise Unreadable(f"not a single equation: {line!r}")
    return tuple(s.strip() for s in line.split("="))


def holds(line: str, **env) -> bool:
    """Does the printed equation hold at these values?

    An option that makes a denominator zero, or puts a negative under a printed
    radical, does not satisfy the equation -- and that is the whole extraneous
    root check: it falls out of evaluating what is printed rather than what
    squaring or cross-multiplying produced.
    """
    lhs, rhs = sides(line)
    try:
        a, b = value(lhs, **env), value(rhs, **env)
    except (ParseError, ZeroDivisionError, ValueError, OverflowError):
        return False
    if not (math.isfinite(a) and math.isfinite(b)):
        return False
    return abs(a - b) <= TOL * max(1.0, abs(a), abs(b))


# ------------------------------------------------------- the printed equations

_LEAD = re.compile(r"^(?:If|When|In|For|Given|That|the|given|equation)\b[,\s]*")


def _clean(text: str) -> str:
    """Strip the English that leads into an equation printed inside a sentence."""
    prev = None
    while prev != text:
        prev = text
        text = _LEAD.sub("", text).strip()
    return text


def equations(item) -> list:
    """Every displayed equation the stem carries, in printed order."""
    out = []
    for line in item.stem.split("\n"):
        line = line.strip()
        if line.count("=") == 1 and not _is_prose(line):
            out.append(line)
    if not out:                       # an equation printed inside a sentence
        for chunk in re.split(r"[,.?]", item.stem):
            cand = _clean(chunk.strip())
            if cand.count("=") == 1 and not _is_prose(cand):
                out.append(cand)
    if not out:
        raise Unreadable(f"no equation in {item.stem!r}")
    return out


_WORDS = re.compile(r"\b(what|which|the|is|are|value|solution|graph|given|if|in|"
                    r"equation|following|constant|where|and|of|to|system)\b", re.I)


def _is_prose(line: str) -> bool:
    return len(_WORDS.findall(line)) >= 2


def question(item) -> str:
    """The sentence that asks for something."""
    for line in reversed(item.stem.split("\n")):
        if "?" in line:
            return line.strip()
    return item.stem.strip()


# --------------------------------------------- the polynomial a page prints

def _interpolate(f, degree: int):
    """The coefficients of a printed polynomial, recovered by evaluating it.

    Nothing about the item's parameters is consulted: the printed side is
    evaluated at whole numbers and the polynomial through those points is
    solved for, then checked at points that were not used to build it.
    """
    nodes = list(range(degree + 1))
    ys = [f(float(n)) for n in nodes]
    coeffs = [0.0] * (degree + 1)
    for i, xi in enumerate(nodes):
        basis = [1.0]
        denom = 1.0
        for j, xj in enumerate(nodes):
            if i == j:
                continue
            basis = _mul_linear(basis, -float(xj))
            denom *= float(xi - xj)
        for k, c in enumerate(basis):
            coeffs[k] += ys[i] * c / denom
    for probe in (0.5, -1.5, 3.25, 12.5, -9.75, 41.5, -57.25):
        got = sum(c * probe ** k for k, c in enumerate(coeffs))
        if abs(got - f(probe)) > 1e-6 * max(1.0, abs(got)):
            raise Unreadable("the printed side is not a polynomial of that degree")
    return coeffs


def _mul_linear(coeffs, c: float) -> list:
    """Multiply a polynomial by (x + c)."""
    out = [0.0] * (len(coeffs) + 1)
    for i, a in enumerate(coeffs):
        out[i] += a * c
        out[i + 1] += a
    return out


def _poly_at(coeffs, x: float) -> float:
    return sum(c * x ** i for i, c in enumerate(coeffs))


def _roots(coeffs) -> list:
    """The real roots of a polynomial, by monotone intervals and bisection."""
    coeffs = list(coeffs)
    while len(coeffs) > 1 and abs(coeffs[-1]) < 1e-9:
        coeffs.pop()
    if len(coeffs) <= 1:
        return []
    if len(coeffs) == 2:
        return [-coeffs[0] / coeffs[1]]
    scale = max(abs(c) for c in coeffs)
    tol = 1e-9 * max(1.0, scale)
    crit = _roots([i * c for i, c in enumerate(coeffs)][1:])
    r = 1.0 + max(abs(c) / abs(coeffs[-1]) for c in coeffs[:-1])
    nodes = [-r] + [c for c in sorted(crit) if -r < c < r] + [r]
    out = []
    for u, v in zip(nodes, nodes[1:]):
        fu, fv = _poly_at(coeffs, u), _poly_at(coeffs, v)
        if abs(fu) <= tol:
            out.append(u)
        if abs(fv) <= tol:
            out.append(v)
        elif abs(fu) > tol and (fu > 0) != (fv > 0):
            out.append(_bisect(coeffs, u, v))
    return _dedupe(out)


def _bisect(coeffs, a, b):
    fa = _poly_at(coeffs, a)
    for _ in range(120):
        m = (a + b) / 2
        fm = _poly_at(coeffs, m)
        if fm == 0.0:
            return m
        if (fm > 0) == (fa > 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


def _dedupe(values, tol: float = 1e-6) -> list:
    out = []
    for v in sorted(values):
        if not out or abs(v - out[-1]) > tol * max(1.0, abs(v)):
            out.append(v)
    return out


def printed_roots(line: str, var: str = "x", degree: int = 3) -> list:
    """Every solution of a printed equation, read off the page.

    A polynomial is recovered by interpolation and solved exactly; anything else
    -- an absolute value, a radical, a quotient -- is scanned for sign changes
    and each bracket squeezed, with every candidate finally put back into the
    printed equation so that a pole is never mistaken for a root.
    """
    lhs, rhs = sides(line)

    def g(x):
        return value(lhs, **{var: x}) - value(rhs, **{var: x})

    for d in range(1, degree + 1):
        try:
            return _roots(_interpolate(g, d))
        except (Unreadable, ParseError, ZeroDivisionError, ValueError,
                OverflowError):
            continue
    return _scan_roots(line, var)


def _scan_roots(line: str, var: str = "x", lo: float = -260.0, hi: float = 260.0,
                step: float = 0.05) -> list:
    """Sign-change scan for an equation no polynomial fits."""
    lhs, rhs = sides(line)

    def g(x):
        try:
            a, b = value(lhs, **{var: x}), value(rhs, **{var: x})
        except (ParseError, ZeroDivisionError, ValueError, OverflowError):
            return None
        return a - b if math.isfinite(a) and math.isfinite(b) else None

    found, prev_x, prev = [], lo, g(lo)
    x = lo
    while x <= hi:
        v = g(x)
        if v is not None:
            if v == 0.0:
                found.append(x)
            elif prev is not None and (v > 0) != (prev > 0):
                found.append(_squeeze(g, prev_x, x))
            prev_x, prev = x, v
        else:
            prev = None
        x += step
    return [r for r in _dedupe(found) if holds(line, **{var: r})]


def _squeeze(g, a: float, b: float) -> float:
    fa = g(a)
    for _ in range(100):
        m = (a + b) / 2
        fm = g(m)
        if fm is None:
            return (a + b) / 2
        if fm == 0.0:
            return m
        if (fm > 0) == (fa > 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


# ------------------------------------------------------------------- helpers

def keyed(item) -> int:
    return "ABCD".index(item.answer)


def one_hit(hits, item, what: str):
    if hits.count(True) != 1:
        raise AssertionError(f"{hits.count(True)} of the four options {what}")
    if not hits[keyed(item)]:
        raise AssertionError(f"the keyed option does not {what}")


# ============================================================ the checks

def check_substitution(item) -> str:
    """Every printed option put back into the printed equation.

    This is the extraneous-root check. A radical is evaluated as a radical, so a
    candidate that makes it negative fails; a denominator is evaluated as a
    denominator, so a candidate that makes it zero fails. Neither failure needs
    to be looked for -- the arithmetic simply does not work, exactly as it does
    not work for the student.
    """
    line = equations(item)[0]
    ask = question(item)
    want_sign = 1 if "positive solution" in ask else (
        -1 if "negative solution" in ask else 0)

    def good(v):
        if v is None or not holds(line, x=v):
            return False
        return want_sign == 0 or (v > 0) == (want_sign > 0)

    if item.fmt == "spr":
        v = number(item.answer)
        if not good(v):
            raise AssertionError(f"the gridded answer {item.answer!r} does not "
                                 f"satisfy {line!r}")
        return "the gridded answer satisfies the printed equation"
    hits = [good(number(c)) for c in item.choices]
    one_hit(hits, item, f"satisfy {line!r}")
    return "exactly one printed option satisfies the printed equation"


def check_expression(item) -> str:
    """The solutions are found from the printed equation, then combined.

    "The sum of the solutions", "the product of the solutions", "the value of
    x² − 6x": the quantity is worked out from roots this file finds on the page,
    and no other option may equal it.
    """
    line = equations(item)[0]
    ask = question(item)
    roots = printed_roots(line)
    if not roots:
        raise AssertionError(f"{line!r} has no real solutions to combine")
    if "sum of the solutions" in ask:
        want = sum(roots)
    elif "product of the solutions" in ask:
        want = 1.0
        for r in roots:
            want *= r
    else:
        m = re.search(r"value of ([^?]+)\?", ask)
        if m is None:
            raise Unreadable(ask)
        want = value(m.group(1).strip(), x=roots[0])
        for r in roots[1:]:
            if abs(value(m.group(1).strip(), x=r) - want) > TOL * max(1.0, abs(want)):
                raise AssertionError("the expression asked for takes two different "
                                     "values at the two solutions")
    if item.fmt == "spr":
        got = number(item.answer)
        if got is None or abs(got - want) > 1e-6 * max(1.0, abs(want)):
            raise AssertionError(f"gridded {item.answer!r}, the page gives {want!r}")
        return "the gridded value matches the printed equation's solutions"
    hits = [c is not None and abs(c - want) <= 1e-6 * max(1.0, abs(want))
            for c in map(number, item.choices)]
    one_hit(hits, item, f"equal {want!r}")
    return "exactly one printed option is the quantity asked for"


def check_literal(item) -> str:
    """Each option is `t = <expression>`; put it back into the printed formula.

    The other letters are given values, the option says what the target is, and
    the whole lot goes into the equation as printed. An option that rearranges
    wrongly fails; an option that rearranges the same way as the key by a
    different route is a second correct answer and fails the count.
    """
    line = equations(item)[0]
    target = item.choices[0].split(" = ", 1)[0].strip()
    others = [l for l in _letters(line) if l != target]
    if not others:
        raise Unreadable(f"no free letters in {line!r}")
    hits = []
    for trial in range(6):
        env = {l: 2.25 + 1.5 * i + 0.125 * trial for i, l in enumerate(others)}
        row = []
        for opt in item.choices:
            if " = " not in opt:
                row.append(False)
                continue
            rhs = opt.split(" = ", 1)[1]
            try:
                t = value(rhs, **env)
            except (ParseError, ZeroDivisionError, ValueError, OverflowError):
                row.append(False)
                continue
            row.append(holds(line, **dict(env, **{target: t})))
        if not hits:
            hits = row
        else:
            hits = [a and b for a, b in zip(hits, row)]
    one_hit(hits, item, f"rearrange {line!r} correctly")
    return "exactly one printed option rearranges the printed formula"


def _letters(line: str) -> list:
    """The letters of a printed formula.

    `8yv` is a product of two of them and `V_B` is one of them, so a run is kept
    whole only when it carries an underscore; otherwise it is a juxtaposition and
    comes apart into single letters.
    """
    out = []
    for run in _RUN.findall(line):
        if run in ("sqrt", "pi"):
            continue
        for name in ([run] if "_" in run else list(run)):
            if name not in out:
                out.append(name)
    return out


def _top_level_groups(text: str) -> list:
    """Every outermost (...) group, so a nested bracket does not end one early.

    `(2/3 \u2212 (1/3)\u221a46, 14/3 + (2/3)\u221a46)` is one point whose
    coordinates carry brackets of their own; a regular expression that stops at
    the first `)` reads it as something else entirely.
    """
    out, depth, start = [], 0, None
    for i, ch in enumerate(text):
        if ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and start is not None:
                out.append(text[start + 1:i])
                start = None
    return out


def _top_level_split(body: str) -> list:
    out, depth, cur = [], 0, ""
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return out


def _points(option: str):
    out = []
    for body in _top_level_groups(option):
        parts = _top_level_split(body)
        if len(parts) != 2:
            return None
        try:
            out.append((value(parts[0]), value(parts[1])))
        except (ParseError, ZeroDivisionError, ValueError, OverflowError):
            return None
    return out or None


def check_points(item) -> str:
    """Each printed point is substituted into both printed equations."""
    eqs = equations(item)
    if len(eqs) != 2:
        raise Unreadable(f"{len(eqs)} equations, not two")
    ask = question(item)
    want = 2 if "points of intersection" in ask else 1
    hits = []
    for opt in item.choices:
        pts = _points(opt)
        ok = (pts is not None and len(pts) == want
              and all(all(holds(e, x=x, y=y) for e in eqs) for x, y in pts)
              and len({(round(x, 9), round(y, 9)) for x, y in pts}) == want)
        hits.append(ok)
    one_hit(hits, item, "lie on both printed graphs")
    return f"exactly one option names {'both points' if want == 2 else 'a point'} "\
           "the printed graphs share"


def check_solution_set(item) -> str:
    """`{5}` against `{−1, 5}`: the set has to be the solution set, exactly."""
    line = equations(item)[0]
    hits = []
    for opt in item.choices:
        body = opt.strip().strip("{}").strip()
        vals = [] if not body else [number(v) for v in body.split(",")]
        if any(v is None for v in vals):
            hits.append(False)
            continue
        satisfied = all(holds(line, x=v) for v in vals)
        hits.append(satisfied and _complete(line, vals))
    one_hit(hits, item, f"is the solution set of {line!r}")
    return "exactly one printed set is the solution set"


def _complete(line: str, vals) -> bool:
    """Does this set leave no solution out?

    The equation is squared to find every candidate the page could have, then
    each candidate is tested against the printed equation -- so a set that drops
    a genuine solution fails as loudly as one that keeps an extraneous root.
    """
    lhs, rhs = sides(line)

    def g(x):
        try:
            return value(lhs, x=x) - value(rhs, x=x)
        except (ParseError, ZeroDivisionError, ValueError, OverflowError):
            return None

    found = []
    x = -60.0
    prev = None
    while x <= 60.0:
        v = g(x)
        if v is not None and prev is not None and abs(v) < 1e9:
            if v == 0 or (v > 0) != (prev > 0):
                lo, hi = x - 0.05, x
                for _ in range(80):
                    mid = (lo + hi) / 2
                    gm = g(mid)
                    if gm is None:
                        break
                    if (gm > 0) == (prev > 0):
                        lo = mid
                    else:
                        hi = mid
                found.append((lo + hi) / 2)
        prev = v if v is not None and abs(v) < 1e9 else None
        x += 0.05
    real = [r for r in _dedupe(found) if holds(line, x=r)]
    if len(real) != len(vals):
        return False
    return all(any(abs(r - v) < 1e-5 * max(1.0, abs(v)) for v in vals) for r in real)


def check_formula(item) -> str:
    """Each option is a way of writing the roots; only one writes them right."""
    line = equations(item)[0]
    roots = printed_roots(line, degree=2)
    if len(roots) != 2:
        raise AssertionError("the printed quadratic does not have two solutions")
    single = "is a solution" in question(item)
    hits = []
    for opt in item.choices:
        vals = _branches(opt)
        if vals is None:
            hits.append(False)
            continue
        if single:
            hits.append(any(_near(v, r) for v in vals for r in roots))
        else:
            hits.append(len(vals) == 2 and all(any(_near(v, r) for r in roots)
                                               for v in vals)
                        and not _near(vals[0], vals[1]))
    one_hit(hits, item, f"give the solutions of {line!r}")
    return "exactly one printed option names the solutions"


def _branches(option: str):
    out = []
    for piece in option.split(" and "):
        piece = piece.split("=", 1)[1] if "=" in piece else piece
        forms = ([piece.replace("±", "+"), piece.replace("±", "-")]
                 if "±" in piece else [piece])
        for f in forms:
            try:
                out.append(value(f))
            except (ParseError, ZeroDivisionError, ValueError, OverflowError):
                return None
    return out or None


def _near(a, b) -> bool:
    return abs(a - b) <= 1e-6 * max(1.0, abs(b))


COUNT_WORDS = {"Zero": 0, "Exactly one": 1, "One": 1, "Exactly two": 2, "Two": 2,
               "There are no solutions.": 0, "There is exactly 1 solution.": 1,
               "There are exactly 2 solutions.": 2,
               "There are exactly 4 solutions.": 4, "0": 0, "1": 1, "2": 2,
               "3": 3}
UNCOUNTABLE = {"Infinitely many", "More than two"}


def check_count(item) -> str:
    """The options are claims about a number; decide the number from the page."""
    eqs = equations(item)
    if len(eqs) == 1:
        want = len(printed_roots(eqs[0], degree=2))
    else:
        lhs1, rhs1 = sides(eqs[0])
        lhs2, rhs2 = sides(eqs[1])

        def g(x):
            y = _solve_for_y(lhs2, rhs2, x)
            return value(lhs1, x=x, y=y) - value(rhs1, x=x, y=y)

        want = len(_roots(_interpolate(g, 2)))
    hits = []
    for opt in item.choices:
        if opt in UNCOUNTABLE:
            hits.append(False)
        elif opt in COUNT_WORDS:
            hits.append(COUNT_WORDS[opt] == want)
        else:
            raise Unreadable(f"unreadable count option {opt!r}")
    one_hit(hits, item, f"say the printed system has {want} solutions")
    return f"exactly one option gives the printed count ({want})"


def _solve_for_y(lhs: str, rhs: str, x: float) -> float:
    """The y the printed linear equation pairs with this x, read off the page."""
    def g(y):
        return value(lhs, x=x, y=y) - value(rhs, x=x, y=y)

    a0, a1 = g(0.0), g(1.0) - g(0.0)
    if abs(a1) < 1e-12:
        raise Unreadable("the second equation does not carry y")
    return -a0 / a1


def check_relation(item) -> str:
    """Two inequalities are the same when one is a positive multiple of the other."""
    line = equations(item)[0] if "=" in item.stem.split("\n")[0] else None
    printed = item.stem.split("\n")[0].strip()
    want = _relation(printed)
    hits = []
    for opt in item.choices:
        try:
            got = _relation(opt)
        except (Unreadable, ParseError, ValueError, ZeroDivisionError):
            hits.append(False)
            continue
        hits.append(_same_half_plane(want, got))
    one_hit(hits, item, f"describe the same region as {printed!r}")
    return "exactly one printed inequality is equivalent"


_REL = re.compile(r"^(.*?)\s*(≤|≥|<|>)\s*(.*)$")


def _relation(text: str):
    m = _REL.match(text.strip())
    if m is None:
        raise Unreadable(f"not an inequality: {text!r}")
    lhs, op, rhs = m.group(1), m.group(2), m.group(3)

    def at(x, y):
        return value(lhs, x=x, y=y) - value(rhs, x=x, y=y)

    base = at(0.0, 0.0)
    a = at(1.0, 0.0) - base
    b = at(0.0, 1.0) - base
    return (a, b, -base, op in (">", "≥"))


def _same_half_plane(want, got) -> bool:
    a1, b1, c1, up1 = want
    a2, b2, c2, up2 = got
    if abs(a2) < 1e-12 and abs(b2) < 1e-12:
        return False
    lam = a2 / a1 if abs(a1) > 1e-12 else b2 / b1
    if abs(lam) < 1e-12:
        return False
    for u, v in ((a1, a2), (b1, b2), (c1, c2)):
        if abs(lam * u - v) > 1e-9 * max(1.0, abs(v)):
            return False
    return (lam > 0) == (up1 == up2)


# ------------------------------------------------- the picture, read back

def _floats(text: str) -> list:
    return [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", text)]


class Picture:
    """A drawn xy-plane, recovered from the SVG a reader actually receives."""

    def __init__(self, svg: str):
        ax = re.findall(r'<line class="ax" x1="([^"]+)" y1="([^"]+)" '
                        r'x2="([^"]+)" y2="([^"]+)"/>', svg)
        if len(ax) != 2:
            raise Unreadable("a grid with something other than two axes")
        horizontal = [a for a in ax if a[1] == a[3]]
        vertical = [a for a in ax if a[0] == a[2]]
        if len(horizontal) != 1 or len(vertical) != 1:
            raise Unreadable("the axes are not one horizontal and one vertical")
        self.y0 = float(horizontal[0][1])
        self.x0 = float(vertical[0][0])
        gr = re.findall(r'<line class="gr" x1="([^"]+)" y1="[^"]+" '
                        r'x2="([^"]+)" y2="[^"]+"/>', svg)
        xs = sorted({float(a) for a, b in gr if a == b})
        gaps = _dedupe([b - a for a, b in zip(xs, xs[1:])], 1e-9)
        if len(gaps) != 1:
            raise Unreadable("the gridlines are not evenly spaced")
        self.px = gaps[0]
        self.segments = [tuple(_floats(" ".join(g))) for g in
                         re.findall(r'<line class="sg" x1="([^"]+)" y1="([^"]+)" '
                                    r'x2="([^"]+)" y2="([^"]+)"/>', svg)]
        self.curves = [[self.data(*p.split(",")) for p in pts.split()]
                       for pts in re.findall(r'<polyline class="cv" points="([^"]+)"/>',
                                             svg)]
        self.points = [self.data(cx, cy) for cx, cy in
                       re.findall(r'<circle class="pt" cx="([^"]+)" cy="([^"]+)"',
                                  svg)]

    def data(self, px, py) -> tuple:
        return ((float(px) - self.x0) / self.px, (self.y0 - float(py)) / self.px)

    def line(self):
        if len(self.segments) != 1:
            raise Unreadable(f"{len(self.segments)} drawn lines, not one")
        x1, y1, x2, y2 = self.segments[0]
        a = self.data(x1, y1)
        b = self.data(x2, y2)
        if abs(a[0] - b[0]) < 1e-9:
            raise Unreadable("a vertical drawn line has no slope")
        m = (b[1] - a[1]) / (b[0] - a[0])
        return m, a[1] - m * a[0]

    def on_curve(self, x, y, tol: float = 0.06) -> bool:
        for run in self.curves:
            for (ax_, ay), (bx, by) in zip(run, run[1:]):
                if min(ax_, bx) - tol <= x <= max(ax_, bx) + tol:
                    if abs(bx - ax_) < 1e-12:
                        continue
                    t = (x - ax_) / (bx - ax_)
                    if abs(ay + t * (by - ay) - y) <= tol:
                        return True
        return False


def check_graph_point(item) -> str:
    """The drawn crossing, recovered from the picture, against the options.

    Nothing about the item's parameters is consulted: the origin comes from the
    two axes, the scale from the gridline spacing, the marked point from its own
    circle, the line from its segment and the curve from its polyline. This is
    the only check in the topic that can catch a figure drifting away from its
    answer.
    """
    pic = Picture(item.figure)
    if len(pic.points) != 1:
        raise Unreadable(f"{len(pic.points)} marked points, not one")
    x, y = pic.points[0]
    m, b = pic.line()
    if abs(m * x + b - y) > 0.05:
        raise AssertionError(f"the marked point ({x:.3f}, {y:.3f}) is not on the "
                             f"drawn line")
    if not pic.on_curve(x, y):
        raise AssertionError(f"the marked point ({x:.3f}, {y:.3f}) is not on the "
                             f"drawn curve")
    hits = []
    for opt in item.choices:
        pts = _points(opt)
        hits.append(pts is not None and len(pts) == 1
                    and abs(pts[0][0] - x) < 0.05 and abs(pts[0][1] - y) < 0.05)
    one_hit(hits, item, f"name the drawn crossing ({round(x)}, {round(y)})")
    return "exactly one option names the point the picture marks"


def check_graph_count(item) -> str:
    """Count the crossings in the picture, and check the options against that.

    The curve is a polyline, so a crossing shows up either as a sample sitting
    exactly on the line or as a sign change between two samples. Both have to be
    counted: the sampler lands exactly on a lattice crossing often enough that
    ignoring the zeros loses them, and skipping a pair because one of its gaps is
    zero loses the sign change as well.
    """
    pic = Picture(item.figure)
    m, b = pic.line()
    crossings, grazed = 0, None
    for run in pic.curves:
        gaps = [y - (m * x + b) for x, y in run]
        if not gaps:
            continue
        closest = min(abs(g) for g in gaps)
        grazed = closest if grazed is None else min(grazed, closest)
        # compress the run into a sequence of signs, then count every stretch of
        # zeros and every direct flip as one meeting point
        signs = [0 if g == 0.0 else (1 if g > 0 else -1) for g in gaps]
        prev_nonzero, in_zero = None, False
        for sg in signs:
            if sg == 0:
                if not in_zero:
                    crossings += 1
                    in_zero = True
                continue
            if in_zero:
                in_zero = False
            elif prev_nonzero is not None and sg != prev_nonzero:
                crossings += 1
            prev_nonzero = sg
    if crossings == 0 and grazed is not None:
        step = 1.0 / pic.px
        if grazed <= 0.5 * step:
            crossings = 1
        elif grazed <= 2.0 * step:
            raise Unreadable("the picture cannot be read as touching or missing")
    hits = [number(o) == crossings for o in item.choices]
    one_hit(hits, item, f"give the crossings the picture shows ({crossings})")
    return f"exactly one option gives the drawn count ({crossings})"


def check_function_meets(item) -> str:
    """f is drawn and g is printed; the gridded answer must satisfy f(a) = g(a)."""
    fm = re.search(r"f\(x\) = (.+?), is shown", item.stem)
    gm = re.search(r"g\(x\) = (.+?), what is", item.stem)
    if fm is None or gm is None:
        raise Unreadable(item.stem)
    a = number(item.answer)
    if a is None:
        raise Unreadable(item.answer)
    fa, ga = value(fm.group(1), x=a), value(gm.group(1), x=a)
    if abs(fa - ga) > TOL * max(1.0, abs(fa)):
        raise AssertionError(f"f({a}) = {fa} but g({a}) = {ga}")
    pic = Picture(item.figure)
    if not pic.on_curve(a, fa):
        raise AssertionError(f"({a}, {fa}) is not on the drawn graph of f")
    return "the gridded value satisfies f(a) = g(a) and sits on the drawn curve"


def check_condition_value(item) -> str:
    """A constant bounded by a condition: only one option may satisfy it.

    "No real solutions" and "more than one real solution" are true of a whole
    range of constants, so an option set can easily print two that qualify. Each
    printed option is substituted into the printed equation and the solutions of
    the result are counted from the page.
    """
    line = equations(item)[0]
    ask = question(item)
    letter = _unknown_letter(line)
    if letter is None:
        raise Unreadable(f"no constant to substitute in {line!r}")
    if "no real solutions" in ask:
        want = lambda n: n == 0                                   # noqa: E731
    elif "more than one real solution" in ask:
        want = lambda n: n > 1                                    # noqa: E731
    elif "exactly one solution" in ask:
        want = lambda n: n == 1                                   # noqa: E731
    else:
        raise Unreadable(ask)
    hits = []
    for opt in item.choices:
        v = number(opt)
        if v is None:
            hits.append(False)
            continue
        try:
            hits.append(want(len(printed_roots(_substitute(line, letter, v),
                                               degree=2))))
        except (Unreadable, ParseError, ZeroDivisionError, ValueError):
            hits.append(False)
    one_hit(hits, item, f"satisfy the condition the stem states")
    return "exactly one printed constant meets the stated condition"


def _unknown_letter(line: str):
    names = [n for n in _RUN.findall(line) if n not in ("x", "sqrt", "pi")]
    return names[0] if names else None


def _substitute(line: str, letter: str, v: float) -> str:
    body = f"({v!r})"
    return re.sub(rf"(?<![A-Za-z_]){re.escape(letter)}(?![A-Za-z_0-9])", body, line)


def check_symbolic(item) -> str:
    """Two positive constants and no numbers: count by trying many values."""
    curve = equations(item)[0]
    m = re.search(r"the equation y = (.+?) in the xy-plane", item.stem)
    if m is None:
        raise Unreadable(item.stem)
    rhs_line = f"y = {m.group(1)}"
    # every constant here is a single letter, and a letter run like `vx` is a
    # product, so the letters are taken one at a time
    letters = sorted({c for c in re.findall(r"[A-Za-z]", curve)
                      if c not in ("x", "y")})
    if len(letters) != 2:
        raise Unreadable(f"{len(letters)} constants, not two")
    counts = set()
    for u in (0.25, 1.0, 3.5, 9.0):
        for w in (0.5, 2.0, 6.25, 11.0):
            env = {letters[0]: u, letters[1]: w}
            lhs, rhs = sides(curve)
            lhs2, rhs2 = sides(rhs_line)

            def g(x, env=env, rhs=rhs, rhs2=rhs2):
                return value(rhs, x=x, **env) - value(rhs2, x=x, **env)

            counts.add(len(_roots(_interpolate(g, 2))))
    if len(counts) != 1:
        raise Unreadable("the count depends on which positive values are chosen")
    want = counts.pop()
    hits = []
    for opt in item.choices:
        if opt in UNCOUNTABLE:
            hits.append(False)
        elif opt in COUNT_WORDS:
            hits.append(COUNT_WORDS[opt] == want)
        else:
            raise Unreadable(f"unreadable count option {opt!r}")
    one_hit(hits, item, f"give the count the letters force ({want})")
    return f"exactly one option gives the count the signs force ({want})"


def check_sum_product(item) -> str:
    """x + y = S and xy = P: the gridded x must belong to a real pair."""
    eqs = equations(item)
    if len(eqs) != 2:
        raise Unreadable(f"{len(eqs)} equations, not two")
    x = number(item.answer)
    if x is None:
        raise Unreadable(item.answer)
    lhs, rhs = sides(eqs[0])
    y = _solve_for_y(lhs, rhs, x)
    if not holds(eqs[1], x=x, y=y):
        raise AssertionError(f"x = {x} gives y = {y}, which fails {eqs[1]!r}")
    return "the gridded value belongs to a pair satisfying both equations"


CHECKS = {
    "nleq.isolate_sum": check_literal,
    "nleq.isolate_bracket": check_literal,
    "nleq.isolate_factor": check_literal,
    "nleq.isolate_denominator": check_literal,
    "nleq.scale_relation": check_relation,
    "nleq.square_equation": check_substitution,
    "nleq.absolute_equation": check_substitution,
    "nleq.quadratic_solve": check_substitution,
    "nleq.quadratic_formula": check_formula,
    "nleq.factored_equation": check_expression,
    "nleq.shared_factor": check_expression,
    "nleq.cancel_squares": check_substitution,
    "nleq.scaled_quadratic": check_expression,
    "nleq.radical_equation": check_substitution,
    "nleq.rational_linear": check_substitution,
    "nleq.rational_quadratic": check_substitution,
    "nleq.rational_combine": check_substitution,
    "nleq.curve_line_system": check_substitution,
    "nleq.count_real_solutions": check_count,
    "nleq.count_system_solutions": check_count,
    "nleq.graph_solution": check_graph_point,
    "nleq.graph_count": check_graph_count,
    "nleq.function_meets": check_function_meets,
    "nleq.discriminant_constant": check_condition_value,
    "nleq.symbolic_intersections": check_symbolic,
    "nleq.sum_product": check_sum_product,
}

def route(item):
    """The reader this item needs, chosen from what its page actually asks."""
    ask = question(item)
    base = CHECKS[item.template]
    if base is check_condition_value and item.fmt == "spr":
        return check_condition_grid
    if base is check_substitution:
        if "sum of the solutions" in ask or "product of the solutions" in ask:
            return check_expression
        if re.search(r"value of (x²|7x²|xy)", ask):
            return check_expression if "xy" not in ask else check_pair_product
        if "ordered pair" in ask or "points of intersection" in ask:
            return check_points
        if "solution set" in ask:
            return check_solution_set
        if item.template == "nleq.curve_line_system":
            return check_system_value
    return base


def check_condition_grid(item) -> str:
    """A grid-in constant: substitute it back and count the solutions."""
    line = equations(item)[0]
    letter = _unknown_letter(line)
    v = number(item.answer)
    if letter is None or v is None:
        raise Unreadable(line)
    n = len(printed_roots(_substitute(line, letter, v), degree=2))
    if n != 1:
        raise AssertionError(f"the gridded constant leaves {n} solutions, not one")
    return "the gridded constant leaves the printed equation one solution"


def check_pair_product(item) -> str:
    return check_system_value(item)


def check_system_value(item) -> str:
    """A value asked of a system: x, y or xy at a point the two graphs share.

    The printed options are numbers, so the option alone does not name a point.
    Every solution of the printed system is found from the page, the quantity the
    stem asks for is computed at each, and exactly one option must be one of
    those values -- which is what makes "a possible value of x" with both roots
    printed come out as two correct answers.
    """
    eqs = equations(item)
    if len(eqs) != 2:
        raise Unreadable(f"{len(eqs)} equations, not two")
    lhs1, rhs1 = sides(eqs[0])
    lhs2, rhs2 = sides(eqs[1])

    def g(x):
        y = _solve_for_y(lhs2, rhs2, x)
        return value(lhs1, x=x, y=y) - value(rhs1, x=x, y=y)

    xs = _roots(_interpolate(g, 2))
    pts = [(x, _solve_for_y(lhs2, rhs2, x)) for x in xs]
    if not pts:
        raise AssertionError("the printed graphs never meet")
    ask = question(item)
    if "value of xy" in ask:
        wants = [x * y for x, y in pts]
        if "x > 0" in ask:
            wants = [x * y for x, y in pts if x > 0]
    elif "y₁ + y₂" in ask:
        wants = [sum(y for _, y in pts)]
    elif "y-coordinate" in ask:
        wants = [y for _, y in pts]
    else:
        wants = [x for x, _ in pts]
        if "(a, a)" in ask:
            wants = [x for x in wants if abs(x) > 1e-9]
    wants = _dedupe(wants)
    if item.fmt == "spr":
        got = number(item.answer)
        if got is None or not any(_near(got, w) for w in wants):
            raise AssertionError(f"gridded {item.answer!r}, the page gives {wants!r}")
        return "the gridded value is one the printed system produces"
    hits = [c is not None and any(_near(c, w) for w in wants)
            for c in map(number, item.choices)]
    one_hit(hits, item, f"give a value the printed system produces {wants!r}")
    return "exactly one printed option answers the printed system"


# ------------------------------------------------------------------ the driver

def run(names, draws: int, verbose: bool = False) -> int:
    worst = 0
    for name in names:
        made, bad, unread, what = 0, 0, 0, ""
        for seed in range(draws):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            made += 1
            try:
                what = route(item)(item)
            except Unreadable as exc:
                unread += 1
                if verbose:
                    print(f"  ? {name} seed {seed}: {exc}")
            except AssertionError as exc:
                bad += 1
                if bad == 1:
                    print(f"\n{name} seed {seed}: {exc}")
                    print(item.pretty())
        mark = "  ok  " if not bad else " FAIL "
        tail = f", {unread} unreadable" if unread else ""
        print(f"{mark} {name:<30} {made:>5,} items, {bad} defects{tail}   ({what})")
        worst |= 1 if bad else 0
    return worst


# ----------------------------------------------------------------- self-test
#
# A check nobody has seen fail is worth nothing. Each case below breaks a real
# item in a way the engine's own gate cannot see, and every one must be caught.

def _broken(item, **fields):
    from copy import deepcopy
    out = deepcopy(item)
    for k, v in fields.items():
        setattr(out, k, v)
    return out


def _first(name, want=lambda it: True, draws: int = 400, **kw):
    """The first generated item of this shape. `kw` reaches the template, which
    is how a surface a free draw does not offer -- the braced solution set, which
    only a source item asks for -- is still put in front of the checker."""
    for seed in range(draws):
        try:
            item = generate(name, seed, **kw)
        except ItemError:
            continue
        if want(item):
            return item
    raise RuntimeError(f"no suitable {name} item in {draws} draws")


def selftest() -> int:
    cases = []

    # 1. a second correct answer: the other point the two graphs share, printed
    #    as a distractor. This is the defect the topic actually shipped.
    it = _first("nleq.curve_line_system",
                lambda i: (i.fmt == "mcq" and "ordered pair" in i.stem
                           and "\u221a" not in "".join(i.choices)))
    eqs = equations(it)
    lhs1, rhs1 = sides(eqs[0])
    lhs2, rhs2 = sides(eqs[1])

    def _gap(x):
        y = _solve_for_y(lhs2, rhs2, x)
        return value(lhs1, x=x, y=y) - value(rhs1, x=x, y=y)

    xs = _roots(_interpolate(_gap, 2))
    kx = _points(it.choices[keyed(it)])[0]
    far = [x for x in xs if abs(x - kx[0]) > 1e-9]
    if far:
        x = far[0]
        point = (x, _solve_for_y(lhs2, rhs2, x))
        spoiled = list(it.choices)
        spoiled[(keyed(it) + 1) % 4] = f"({_show(point[0])}, {_show(point[1])})"
        cases.append(("a distractor that is the other intersection",
                      _broken(it, choices=spoiled),
                      # the injection is only a fault if the point really is a
                      # second answer, so the self-test checks its own premise
                      lambda p=point, e=eqs: all(holds(q, x=p[0], y=p[1])
                                                 for q in e)))

    # 2. an extraneous root kept: the solution set that squaring produces
    it = _first("nleq.radical_equation",
                lambda i: i.fmt == "mcq" and "solution set" in i.stem,
                shape="linear", ask="solution_set")
    spoiled = list(it.choices)
    both = next(c for c in it.choices if c.count(",") == 1 and "{" in c)
    spoiled[keyed(it)] = both
    cases.append(("the key replaced by the set that keeps the extraneous root",
                  _broken(it, choices=spoiled),
                  lambda b=both, k=it.choices[keyed(it)]: b != k))

    # 3. the right answer attached to the wrong letter
    it = _first("nleq.square_equation", lambda i: i.fmt == "mcq")
    cases.append(("the answer letter moved one place",
                  _broken(it, answer="ABCD"[(keyed(it) + 1) % 4]), None))

    # 4. a rearrangement printed twice: the key in a different jacket
    it = _first("nleq.isolate_sum", lambda i: i.fmt == "mcq")
    key = it.choices[keyed(it)]
    target, rhs = key.split(" = ", 1)
    spoiled = list(it.choices)
    spoiled[(keyed(it) + 2) % 4] = f"{target} = ({rhs})/1"
    cases.append(("a distractor that is the key written differently",
                  _broken(it, choices=spoiled), None))

    # 5. a figure that drifts from its answer: the marked point moved one unit
    it = _first("nleq.graph_solution")
    pic = Picture(it.figure)
    m = re.search(r'<circle class="pt" cx="([^"]+)" cy="([^"]+)"', it.figure)
    moved = it.figure.replace(m.group(0),
                              f'<circle class="pt" cx="{float(m.group(1)) + pic.px}" '
                              f'cy="{m.group(2)}"')
    cases.append(("the marked point moved one gridline", _broken(it, figure=moved),
                  lambda a=it.figure, b=moved: a != b))

    # 6. a count item keyed to the wrong statement
    it = _first("nleq.count_real_solutions")
    cases.append(("a count keyed to the wrong statement",
                  _broken(it, answer="ABCD"[(keyed(it) + 1) % 4]), None))

    # 7. a grid-in whose answer squaring produced but the page rejects
    it = _first("nleq.rational_quadratic",
                lambda i: i.fmt == "spr" and "/" in i.stem.split("\n")[0])
    line = equations(it)[0]
    bad_x = -number(re.search(r"x \+ (\d+)", line).group(1)) if re.search(
        r"x \+ (\d+)", line) else None
    if bad_x is not None:
        cases.append(("a grid-in answer that makes a denominator zero",
                      _broken(it, answer=str(int(bad_x))), None))

    worst = 0
    for label, item, premise in cases:
        if premise is not None and not premise():
            print(f" FAIL  the injection for {label!r} is not actually a fault")
            worst = 1
            continue
        try:
            route(item)(item)
        except (AssertionError, Unreadable) as exc:
            print(f"  ok   caught: {label}\n         -> {exc}")
            continue
        print(f" FAIL  NOT caught: {label}")
        print(item.pretty())
        worst = 1
    print(f"\n{len(cases)} injected faults, {'all caught' if not worst else 'SOME MISSED'}")
    return worst


def _show(v: float) -> str:
    """A number as this topic prints one. Only used to build injected faults."""
    r = round(v)
    if abs(v - r) > 1e-9:
        raise RuntimeError(f"{v!r} is not a whole number; the injection would "
                           f"print an approximation and prove nothing")
    return str(r).replace("-", MINUS)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--draws", type=int, default=400,
                    help="seeds to try per template (default 400)")
    ap.add_argument("--template", action="append",
                    help="check only this template; repeatable")
    ap.add_argument("--selftest", action="store_true",
                    help="inject known-bad items and confirm each is caught")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return run(args.template or list(CHECKS), args.draws, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
