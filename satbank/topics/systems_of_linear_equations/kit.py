"""How a system of two linear equations is printed, and how its options are built.

Every template in this topic puts two equations on the page, so the rendering
lives here once: a coefficient, a standard-form side, an equation solved for one
variable, an ordered pair, and the stacked layout a displayed system uses. The
SAT prints a typeset minus, so `num` writes U+2212 and never a hyphen.

Nothing here does any algebra. The solving lives in the templates and is
re-derived from scratch, by a different route, in `audit.py`.
"""

from __future__ import annotations

import random
import re
from fractions import Fraction as Q

from ...exact import E, Exact
from ...item import ItemError, Mis, assemble

__all__ = ["Q", "E", "MINUS", "q", "ex", "num", "dec", "money", "coef", "join",
           "std", "solved", "point", "opt_pair", "displayed", "sent", "choices",
           "griddable", "ASKS", "ask_label", "ask_value", "terminating",
           "opt_dec", "pick", "side"]

MINUS = "−"            # the typeset minus sign, as the source prints it
GROUP_FROM = 1000           # the source writes 2,300 and 27,600 but not 881


# ------------------------------------------------------------------ numbers

def q(v) -> Q:
    """Anything numeric to an exact Fraction. Floats arrive as their decimals."""
    if isinstance(v, Q):
        return v
    if isinstance(v, float):
        return Q(str(v))
    if isinstance(v, Exact):
        if v.pi_exp != 0 or v.rad != 1:
            raise ValueError(f"{v.plain()} is not a rational answer")
        return v.coef
    return Q(v)


def ex(v) -> Exact:
    return v if isinstance(v, Exact) else E(q(v))


def terminating(v) -> bool:
    d = q(v).denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def num(v, group: bool = True) -> str:
    """A bare number as the source prints one: 8, −11, 2,300, 1/2."""
    v = q(v)
    if v.denominator == 1:
        n = abs(v.numerator)
        body = f"{n:,}" if group and n >= GROUP_FROM else str(n)
    else:
        body = f"{abs(v.numerator)}/{v.denominator}"
    return (MINUS if v < 0 else "") + body


def dec(v, places: int | None = None) -> str:
    """A decimal: 8.25, 3.5, 202. Falls back to a fraction when it repeats."""
    v = q(v)
    if places is None:
        if not terminating(v):
            return num(v)
        d, twos, fives = v.denominator, 0, 0
        while d % 2 == 0:
            d //= 2
            twos += 1
        while d % 5 == 0:
            d //= 5
            fives += 1
        places = max(twos, fives)
    head = MINUS if v < 0 else ""
    a = abs(v)
    if places == 0:
        return head + f"{int(a):,}"
    return head + f"{float(a):,.{places}f}"


def money(v, places: int = 2) -> str:
    return "$" + dec(abs(q(v)), places) if q(v) >= 0 else MINUS + "$" + dec(abs(q(v)), places)


def opt_dec(v) -> str:
    """An option printed as a decimal where the source prints one: 2.5, not 5/2.

    The choice machinery compares and sorts options as numbers, so this keeps the
    plain hyphen; the typeset minus belongs in the stem, which is prose.
    """
    f = q(v)
    if f.denominator == 1:
        return f"{f.numerator:,}"
    if terminating(f):
        d, twos, fives = f.denominator, 0, 0
        while d % 2 == 0:
            d //= 2
            twos += 1
        while d % 5 == 0:
            d //= 5
            fives += 1
        return f"{float(f):,.{max(twos, fives)}f}"
    return f"{f.numerator}/{f.denominator}"


def griddable(v) -> bool:
    """What a student can actually enter: a whole number, a short decimal, or a
    fraction that fits the five boxes."""
    v = q(v)
    if v.denominator == 1:
        return abs(v.numerator) < 100_000
    if terminating(v) and v.denominator <= 1000:
        return True
    return abs(v.numerator) < 1000 and v.denominator < 1000


# -------------------------------------------------------------- expressions

def coef(c, var: str, style: str = "frac") -> str:
    """The term against a variable: x, −x, 3x, (1/2)y, −(1/2)y, 8.25r."""
    c = q(c)
    if c == 1:
        return var
    if c == -1:
        return MINUS + var
    if c.denominator != 1 and style == "frac":
        return (MINUS if c < 0 else "") + f"({num(abs(c))}){var}"
    body = dec(c) if style == "dec" else num(c)
    return f"{body}{var}"


def join(parts: list[str]) -> str:
    """Join already-signed terms: '4x + 2y', 'x − 2y', not 'x + −2y'."""
    out = parts[0]
    for p in parts[1:]:
        out += f" {MINUS} {p[1:]}" if p.startswith(MINUS) else f" + {p}"
    return out


def side(a, b, vx: str = "x", vy: str = "y", style: str = "frac") -> str:
    """The left side of a standard-form equation: '4x + 2y', '−4x + y', '3y'."""
    parts = [coef(c, v, style) for c, v in ((q(a), vx), (q(b), vy)) if q(c) != 0]
    return join(parts) if parts else "0"


def std(a, b, c, vx: str = "x", vy: str = "y", style: str = "frac") -> str:
    """A standard-form equation: '4x + 2y = 86', 'x = 8'."""
    rhs = dec(c) if style == "dec" else num(c)
    return f"{side(a, b, vx, vy, style)} = {rhs}"


def solved(p, v: str, m, w: str, b, style: str = "frac",
           const_first: bool = False) -> str:
    """One variable on its own: 'y = 2x − 3', '3y = 5x', 'x = 10', 'ty = 1/2 + 2x'."""
    terms = []
    if q(m) != 0:
        terms.append(coef(m, w, style))
    if q(b) != 0 or not terms:
        terms.append(dec(b) if style == "dec" else num(b))
    if const_first:
        terms.reverse()
    return f"{coef(p, v, style)} = {join(terms)}"


def point(x, y) -> str:
    return f"({num(x)}, {num(y)})"


def opt_pair(e1: str, e2: str) -> str:
    """A system as one option. The page stacks the two equations; an option is a
    single string, so they are joined by the comma the plain-text form uses."""
    return f"{e1}, {e2}"


def displayed(*lines: str) -> str:
    """A displayed system gets its own lines above the sentence, as printed."""
    return "\n".join(lines)


def sent(text: str) -> str:
    """One space between words; nothing hanging off either end."""
    return re.sub(r"[ \t]+", " ", text).strip()


# ---------------------------------------------------------- what is asked for

ASKS = ("x", "y", "sum", "diff", "prod", "k_sum", "kx")


def ask_label(ask: str, k=1, vx: str = "x", vy: str = "y") -> str:
    if ask == "x":
        return vx
    if ask == "y":
        return vy
    if ask == "sum":
        return f"{vx} + {vy}"
    if ask == "diff":
        return f"{vx} {MINUS} {vy}"
    if ask == "prod":
        return f"{vx}{vy}"
    if ask == "kx":
        return coef(k, vx)
    if ask == "k_sum":
        return f"{coef(k, vx)} + {coef(k, vy)}"
    raise ItemError(f"unknown ask {ask!r}")


def ask_value(ask: str, x, y, k=1):
    x, y, k = q(x), q(y), q(k)
    return {"x": x, "y": y, "sum": x + y, "diff": x - y, "prod": x * y,
            "kx": k * x, "k_sum": k * (x + y)}[ask]


# --------------------------------------------------------------- option sets

_LETTERS = re.compile(r"[a-zA-Z]")


def _surface(opt: str) -> tuple:
    """What an option looks like at a glance -- the signature the gate uses."""
    return (bool(_LETTERS.search(opt)), "/" in opt, "." in opt,
            opt.strip().startswith("-"))


def choices(key, mistakes: list[Mis], rng: random.Random, fmt_value=None):
    """assemble(), then redraw if the key ends up alone in its printed form.

    A system answer is signed, so `signed=True`; it solves rather than measures,
    so the fallback near-misses shift rather than scale. The sign rule itself is
    `assemble`'s -- nothing here reorders the pool to game it.
    """
    key = ex(key)
    pool = [Mis(m.reason, ex(m.value)) for m in mistakes if m.value is not None]
    built = assemble(key, pool, rng, fmt_value=fmt_value, signed=True,
                     fillers="shift")
    if len(set(built[0])) != 4:
        raise ItemError("two options render the same way")
    shapes = [_surface(c) for c in built[0]]
    if shapes.count(shapes["ABCD".index(built[3])]) == 1:
        raise ItemError("the key would be the only option of its printed form")
    return built


def pick(pool: dict, wrongs: list | None) -> list[Mis]:
    """The misconceptions this draw offers, in the order they are offered.

    A source item names the three College Board actually printed; a free draw
    gets the whole pool and lets `assemble` choose.
    """
    keys = list(pool) if wrongs is None else list(wrongs)
    out = []
    for k in keys:
        if k not in pool:
            raise ItemError(f"no misconception named {k!r}")
        m = pool[k]
        if m.value is not None:
            out.append(m)
    return out
