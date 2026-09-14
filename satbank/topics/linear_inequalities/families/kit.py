"""How a linear inequality is printed, and how its options are assembled.

Every template in this topic prints a relation rather than an equation, so the
three things that go wrong in rendering live here once: the symbol (≤ and ≥ are
printed, never `<=`), the minus sign (− rather than a hyphen, wherever it sits
inside prose or inside an option), and the direction of a relation when it is
read from the other end.

Nothing here computes an answer. The mathematics stays in the templates and is
re-derived in `audit.py` from the parameters alone, by testing values on either
side of a boundary rather than by repeating any algebra done here.
"""

from __future__ import annotations

import random
import re
from fractions import Fraction as Q

from ....exact import E, Exact
from ....expr import SYMBOL, fmt_ineq
from ....item import ItemError, Mis, assemble, assemble_text, norm_text

__all__ = ["Q", "E", "MINUS", "OPS", "FLIP", "TURN", "STRICT", "WORD",
           "num", "dec", "term", "side", "rel", "band", "sent", "money",
           "griddable", "mixed", "text_choices", "value_choices", "signed_join",
           "plural", "VARS"]

MINUS = "−"                      # the printed minus sign, not a hyphen
GROUP = 1000                          # the source writes 1,100 and 9,700, but 862

OPS = ("<", "<=", ">", ">=")
# the same relation read from the other end: a < b is b > a
TURN = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}
# the relation a student writes when the sign is not reversed on a negative
# divide, and the one they write when "at least" is read as "at most"
FLIP = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}
STRICT = {"<", ">"}
WORD = {"<=": "at most", ">=": "at least", "<": "less than", ">": "greater than"}

VARS = ["x", "n", "t", "w", "p", "m", "h", "c", "k", "v"]


# ------------------------------------------------------------------ numbers

def num(v, decimal: bool = False, group: int = GROUP) -> str:
    """A number as the source prints one: 8, 1,100, 0.25, 3/4, −14."""
    v = Q(v)
    if decimal:
        return dec(v)
    if v.denominator == 1:
        n = v.numerator
        body = f"{abs(n):,}" if abs(n) >= group else str(abs(n))
        return (MINUS if n < 0 else "") + body
    return (MINUS if v < 0 else "") + f"{abs(v.numerator)}/{v.denominator}"


def dec(v) -> str:
    """The shortest exact decimal: 0.25, 7.35, 10.25, 165."""
    v = Q(v)
    d, twos, fives = v.denominator, 0, 0
    while d % 2 == 0:
        d //= 2
        twos += 1
    while d % 5 == 0:
        d //= 5
        fives += 1
    if d != 1:
        return num(v)
    places = max(twos, fives)
    whole = f"{float(abs(v)):.{places}f}"
    head, _, tail = whole.partition(".")
    head = f"{int(head):,}" if int(head) >= GROUP else head
    return (MINUS if v < 0 else "") + (f"{head}.{tail}" if tail else head)


def mixed(v) -> str:
    """A mixed number, the way the source prints an awkward bound: 11 2/3."""
    v = Q(v)
    if v.denominator == 1:
        return num(v)
    whole, rest = divmod(abs(v), 1)
    body = f"{rest.numerator}/{rest.denominator}"
    if whole:
        body = f"{num(whole)} {body}"
    return (MINUS if v < 0 else "") + body


def money(v, cents: bool = True) -> str:
    v = Q(v)
    return f"${float(v):,.2f}" if cents else f"${int(v):,}"


GRID_DENOMS = (1, 2, 4, 5, 10, 20, 25, 50, 100)


def griddable(v) -> bool:
    """What a student can enter: a whole number or one or two decimal places."""
    return Q(v).denominator in GRID_DENOMS


def plural(n, one: str, many: str | None = None) -> str:
    return one if abs(Q(n)) == 1 else (many or one + "s")


# -------------------------------------------------------------- expressions

def signed_join(parts: list[str]) -> str:
    """'15s + 25p', '2x − 100' -- the printed minus, never '+ −25p'."""
    out = parts[0]
    for p in parts[1:]:
        out += f" {MINUS} {p[1:]}" if p.startswith(MINUS) else f" + {p}"
    return out


def term(c, var: str, decimal: bool = False) -> str:
    """The variable term: 'x', '−x', '35r', '0.3x', '(3/4)x'."""
    c = Q(c)
    if c == 1:
        return var
    if c == -1:
        return f"{MINUS}{var}"
    if c.denominator != 1 and not decimal:
        return f"({num(abs(c))}){var}" if c > 0 else f"{MINUS}({num(abs(c))}){var}"
    return f"{num(c, decimal)}{var}"


def side(terms, const=0, decimal: bool = False, const_first: bool = False) -> str:
    """One side of a relation: '15s + 25p', '2x + 100', '220'.

    `terms` is a sequence of (coefficient, variable) pairs; a zero coefficient
    drops out, and a lone constant prints as the bare number.
    """
    parts = [term(c, v, decimal) for c, v in terms if Q(c) != 0]
    const = Q(const)
    if not parts:
        return num(const, decimal)
    if const != 0:
        parts = ([num(const, decimal)] + parts) if const_first else \
                (parts + [num(const, decimal)])
    return signed_join(parts)


def rel(lhs: str, op: str, rhs: str) -> str:
    """'2x + 100 ≤ 210'. The symbol is the one the page prints."""
    return fmt_ineq(lhs, op, rhs)


def band(lo: str, op1: str, var: str, op2: str, hi: str) -> str:
    """A compound relation: '1,510 ≤ d ≤ 4,130'."""
    return f"{lo} {SYMBOL[op1]} {var} {SYMBOL[op2]} {hi}"


def sent(text: str) -> str:
    """One space between words; a displayed relation keeps its own line."""
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"[ \t]*\n[ \t]*", "\n", text).strip()


# ------------------------------------------------------------- option sets

_LETTERS = re.compile(r"[a-zA-Z]")


def _surface(opt: str) -> tuple:
    """What an option looks like at a glance -- the signature the gate uses.

    A key that is the only option carrying a fraction, or the only one with a
    decimal point, can be picked out without reading the mathematics.
    """
    return (bool(_LETTERS.search(opt)), "/" in opt, "." in opt,
            opt.strip().startswith((MINUS, "-")))


def text_choices(key: str, mistakes: list[Mis], rng: random.Random):
    """Four written options -- relations, points, sentences -- one of them right.

    Options that print the same after normalisation are one option, so a
    duplicate is dropped rather than shipped as a fourth choice.
    """
    picked, seen = [], {norm_text(key)}
    for m in mistakes:
        if m.value is None:
            continue
        k = norm_text(m.value)
        if k in seen:
            continue
        seen.add(k)
        picked.append(m)
        if len(picked) == 3:
            break
    if len(picked) < 3:
        raise ItemError("could not build three distinct written distractors")
    choices, reasons, letter = assemble_text(key, picked, rng)
    shapes = [_surface(c) for c in choices]
    if shapes.count(shapes["ABCD".index(letter)]) == 1:
        raise ItemError("the key would be the only option of its printed form")
    return choices, reasons, letter


def _exact(m: Mis) -> Mis:
    if m.value is None or isinstance(m.value, Exact):
        return m
    return Mis(m.reason, E(Q(m.value)))


def value_choices(key: Exact, mistakes: list[Mis], rng: random.Random,
                  fmt_value=None):
    """assemble(), for the items whose options are numbers.

    An inequality's answer is signed and solves rather than measures, so the
    near-miss fallback shifts rather than scales.
    """
    pool = [_exact(m) for m in mistakes if m.value is not None]
    built = assemble(key, pool, rng, fmt_value=fmt_value, signed=True,
                     fillers="shift")
    if len(set(built[0])) != 4:
        raise ItemError("two options render the same way")
    shapes = [_surface(c) for c in built[0]]
    if shapes.count(shapes["ABCD".index(built[3])]) == 1:
        raise ItemError("the key would be the only option of its printed form")
    return built
