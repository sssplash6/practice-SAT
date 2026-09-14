"""How a linear equation is printed, and how its options are assembled.

Every template in this topic writes an equation, so the rendering lives here
once: a term, a linear side, a bracketed product, and the eight sentence
shapes the source items use to wrap an equation. Nothing here computes an
answer -- the algebra stays in the templates, and is re-derived in `audit.py`
from the parameters alone.
"""

from __future__ import annotations

import random
import re
from fractions import Fraction as Q

from ....exact import E, Exact
from ....expr import fmt_frac, fmt_num, sign_join
from ....item import ItemError, Mis, assemble

__all__ = ["Q", "E", "num", "dec", "term", "side", "paren", "eq_of", "frame_stem",
           "choices", "sent", "money", "over", "VARS", "FRAMES",
           "griddable", "plainly", "article"]

VARS = ["x", "n", "p", "t", "w", "y", "m", "z", "q", "j"]


# ----------------------------------------------------------------- numbers

def num(v, decimal: bool = False) -> str:
    """A number as an SAT option prints it: 8, -11, 1,100, 1/2, 0.001."""
    v = Q(v)
    if decimal:
        return dec(v)
    if v.denominator == 1:
        n = v.numerator
        return f"{n:,}" if abs(n) >= 1000 else str(n)
    return fmt_frac(v)


def dec(v) -> str:
    s = f"{float(Q(v)):.10f}".rstrip("0").rstrip(".")
    return s or "0"


GRID_DENOMS = (1, 2, 4, 5, 10, 20, 25, 50, 100)


def griddable(v, loose: bool = False) -> bool:
    """What a student can actually enter. The source's grid-ins are whole
    numbers or one or two decimal places, except where the answer is a
    fraction the item itself forces."""
    d = Q(v).denominator
    return d <= 1000 if loose else d in GRID_DENOMS


def plainly(v) -> str:
    """A number inside a rationale: 8, 22.4, and 6/7 when it has no decimal."""
    v = Q(v)
    if v.denominator == 1:
        return num(v)
    d = v.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    return dec(v) if d == 1 and v.denominator <= 10_000 else num(v)


def article(n) -> str:
    """'a 30-sided polygon', but 'an 80-sided polygon'."""
    head = str(abs(int(n)))
    return "an" if head[0] == "8" or head[:2] in ("11", "18") else "a"


def money(v, cents: bool = True) -> str:
    v = Q(v)
    if cents:
        return f"${float(v):,.2f}"
    return f"${int(v):,}"


# ------------------------------------------------------------- expressions

def term(c, var: str, decimal: bool = False) -> str:
    """The x-term: 'x', '-x', '3x', '-(1/6)x', '0.8t'."""
    c = Q(c)
    if c == 1:
        return var
    if c == -1:
        return f"-{var}"
    if c.denominator != 1 and not decimal:
        sign = "-" if c < 0 else ""
        return f"{sign}({fmt_frac(abs(c))}){var}"
    return f"{num(c, decimal)}{var}"


def side(m, b, var: str, const_first: bool = False, decimal: bool = False) -> str:
    """One side of an equation: '5p + 180', '112 - x', '2 + x', '60'."""
    m, b = Q(m), Q(b)
    if m == 0:
        return num(b, decimal)
    if b == 0:
        return term(m, var, decimal)
    parts = [num(b, decimal), term(m, var, decimal)] if const_first else \
            [term(m, var, decimal), num(b, decimal)]
    return sign_join(parts)


def paren(c, inner: str, decimal: bool = False) -> str:
    """A coefficient against a bracket: '2(w + 5)', '-(x - 3)', '(1/4)(x + 5)'."""
    c = Q(c)
    if c == 1:
        return f"({inner})"
    if c == -1:
        return f"-({inner})"
    if c.denominator != 1 and not decimal:
        sign = "-" if c < 0 else ""
        return f"{sign}({fmt_frac(abs(c))})({inner})"
    return f"{num(c, decimal)}({inner})"


def over(a, den, var: str) -> str:
    """The variable written over a denominator: '4x/5', 'x/8', '2n/5'."""
    return f"{term(a, var)}/{num(den)}"


def eq_of(lhs: str, rhs: str) -> str:
    return f"{lhs} = {rhs}"


def sent(text: str) -> str:
    """One space between words, and nothing hanging off the end."""
    return re.sub(r"\s+", " ", text).strip()


# -------------------------------------------------------------- the frames

# How the source wraps an equation in a question. Each takes the equation and
# the variable and returns the whole stem.
FRAMES = {
    "displayed": lambda eq, v: f"{eq} What value of {v} is the solution to the given equation?",
    "above": lambda eq, v: f"{eq} In the equation above, what is the value of {v} ?",
    "of_above": lambda eq, v: f"{eq} What value of {v} is the solution of the equation above?",
    "satisfies": lambda eq, v: f"What value of {v} satisfies the equation {eq}?",
    "solution_to": lambda eq, v: f"What is the solution to the equation {eq}?",
    "value_solution": lambda eq, v: f"What value of {v} is the solution to the equation {eq}?",
    "for_what": lambda eq, v: f"For what value of {v} does {eq} ?",
    "if_value": lambda eq, v: f"If {eq}, what is the value of {v} ?",
}
FRAME_NAMES = list(FRAMES)


def frame_stem(frame: str, eq: str, var: str) -> str:
    return sent(FRAMES[frame](eq, var))


# ------------------------------------------------------------ option sets

_LETTERS = re.compile(r"[a-zA-Z]")


def _surface(opt: str) -> tuple:
    """What an option looks like at a glance -- the signature the quality gate
    uses. The sign is part of it: a lone negative key is guessable."""
    return (bool(_LETTERS.search(opt.replace("pi", "").replace("π", ""))),
            "π" in opt or "pi" in opt, "√" in opt or "sqrt" in opt,
            "/" in opt, "." in opt, opt.strip().startswith("-"))


def _sign_first(key: Exact, mistakes: list[Mis]) -> list[Mis]:
    """Reorder so a distractor that shares the key's sign is offered first.

    `assemble` already refuses to leave the key alone as the only fraction,
    but it does not see the minus sign, and a negative answer among three
    positive options can be picked without solving anything.
    """
    neg = float(key) < 0

    def rank(m: Mis) -> int:
        if m.value is None:
            return 2
        return 0 if (float(m.value) < 0) == neg else 1

    return sorted(mistakes, key=rank)


def _exact(m: Mis) -> Mis:
    """Templates work in Fractions; `assemble` compares Exacts."""
    if m.value is None or isinstance(m.value, Exact):
        return m
    return Mis(m.reason, E(Q(m.value)))


def choices(key: Exact, mistakes: list[Mis], rng: random.Random, fmt_value=None):
    """assemble(), and then the rule the gate enforces about surface form.

    Equation answers are signed, so `signed=True`; they solve rather than
    measure, so the fallback near-misses shift rather than scale.
    """
    mistakes = [_exact(m) for m in mistakes if m.value is not None]
    tried = []
    for cand in (mistakes, _sign_first(key, mistakes)):
        try:
            built = assemble(key, cand, rng, fmt_value=fmt_value,
                             signed=True, fillers="shift")
        except ItemError:
            continue
        if len(set(built[0])) != 4:
            continue                       # two values rendered the same way
        shapes = [_surface(c) for c in built[0]]
        if shapes.count(shapes["ABCD".index(built[3])]) > 1:
            return built
        tried.append(built)
    if tried:
        raise ItemError("the key would be the only option of its printed form")
    raise ItemError("could not build three distinct distractors")
