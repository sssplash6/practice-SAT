"""How a linear function is written on an SAT page.

`expr.py` renders a Poly the way algebra items print one, which is most of
what this topic needs. The rest is here: the source set also prints decimals
("9.25 + 0.50x"), money ("$46.60"), thousands separators ("2,268x") and
constant-first layouts, and an option that is right mathematically but printed
in the wrong shape is a wrong option.

Nothing in this module knows any mathematics. It is rendering only, so the
solvers in `audit.py` share none of it.
"""

from __future__ import annotations

import re
from fractions import Fraction as Q

from ...exact import E, Exact
from ...expr import sign_join
from ...item import ItemError, assemble

__all__ = ["MINUS", "q", "ex", "numtext", "coef_text", "lin_text", "fn_eq", "money",
           "dec", "recip_text", "GROUP_FROM", "terminating", "signed_join", "choose"]

GROUP_FROM = 1000          # the source writes 2,268 and 1,000 but not 862

# The page is typeset, so every minus it prints -- the sign on a number, the
# operator between two terms -- is U+2212, the same character `Exact.plain`
# puts in front of an option. An ASCII hyphen on the page is the English one,
# in "y-intercept" and "two-way". Readers fold the two (`item.norm_text`,
# `item.numeral`, this topic's `option_check`), so this changes what is
# printed and not what compares equal. `Exact.gridin` keeps the ASCII sign,
# because a grid-in is a student's keystroke rather than a printed page.
MINUS = "\N{MINUS SIGN}"


def q(v) -> Q:
    """Anything numeric to an exact Fraction; a float comes in as its decimal.

    `assemble` hands an option's Exact to `fmt_value`, so the renderers have to
    accept one. Every answer in this topic is rational, so an Exact carrying a
    pi or a radical is a bug rather than a case to handle.
    """
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
    """A rational to the Exact the option machinery orders and prints."""
    return v if isinstance(v, Exact) else E(q(v))


def terminating(v) -> bool:
    """True when the fraction has a finite decimal expansion."""
    d = q(v).denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def dec(v, places: int | None = None) -> str:
    """'60.90' at two places, or the shortest exact decimal when places is off."""
    v = q(v)
    if places is not None:
        body = f"{abs(float(v)):.{places}f}"
        whole, _, frac = body.partition(".")
        whole = f"{int(whole):,}" if int(whole) >= GROUP_FROM else whole
        return (MINUS if v < 0 else "") + (f"{whole}.{frac}" if frac else whole)
    d, twos, fives = v.denominator, 0, 0
    while d % 2 == 0:
        d //= 2
        twos += 1
    while d % 5 == 0:
        d //= 5
        fives += 1
    digits = max(twos, fives)
    return (MINUS if v < 0 else "") + f"{float(abs(v)):.{digits}f}"


def numtext(v, style: str = "frac", places: int | None = None) -> str:
    """A bare number as the source prints it: 162, 2,268, 9.25, 3/4, −1/2."""
    v = q(v)
    if places is not None:
        return dec(v, places)
    if v.denominator == 1:
        n = abs(v.numerator)
        # format the magnitude and put the sign on by hand: "{-52:,}" would
        # spell the sign with Python's ASCII hyphen
        body = f"{n:,}" if n >= GROUP_FROM else str(n)
        return (MINUS if v < 0 else "") + body
    if style == "dec":
        return dec(v, places)
    return f"{MINUS if v < 0 else ''}{abs(v.numerator)}/{v.denominator}"


def coef_text(m, var: str, style: str = "frac", places: int | None = None) -> str:
    """'4x', '−x', '(3/4)x', '0.50x'. A bare fraction against a variable needs
    its brackets, or −1/2x reads as −1/(2x)."""
    m = q(m)
    if m == 1:
        return var
    if m == -1:
        return f"{MINUS}{var}"
    if m.denominator != 1 and style != "dec" and places is None:
        return f"({numtext(m)}){var}"
    return f"{numtext(m, style, places)}{var}"


def signed_join(head: str, b, style: str = "frac", places: int | None = None) -> str:
    """'8s + 15', '(3/4)x − 3'. The sign is `expr.sign_join`'s to decide.

    `numtext` renders the constant with its own typeset sign and the shared
    joiner reads it back, so nothing here tests a rendered string for a minus
    -- the one thing that goes wrong when a page stops using the ASCII hyphen.
    """
    b = q(b)
    if b == 0:
        return head
    return sign_join([head, numtext(b, style, places)])


def lin_text(m, b, var: str = "x", style: str = "frac", places: int | None = None,
             order: str = "var_first") -> str:
    """mx + b, in either of the two layouts the source set uses.

    order='var_first'  -> '8s + 15', '(3/4)x − 3', '−x + 41'
    order='var_second' -> '9.25 + 0.50x', '212 − x/550' is built elsewhere
    """
    m, b = q(m), q(b)
    if m == 0:
        return numtext(b, style, places)
    if order == "var_first":
        return signed_join(coef_text(m, var, style, places), b, style, places)
    if b == 0:
        return coef_text(m, var, style, places)
    sign = "+" if m > 0 else MINUS
    return (f"{numtext(b, style, places)} {sign} "
            f"{coef_text(abs(m), var, style, places)}")


def fn_eq(lhs: str, body: str) -> str:
    """'f(x) = 4x + 1'. The caller supplies the left side, which is sometimes a
    function value and sometimes a bare variable."""
    return f"{lhs} = {body}"


def recip_text(v, var: str) -> str:
    """The reciprocal coefficient, printed the way the source prints it:
    an integer divisor becomes (1/84)x or (−1/84)x, a decimal one x/5.7."""
    v = q(v)
    if v.denominator == 1:
        return (f"(1/{numtext(abs(v))}){var}" if v > 0
                else f"({MINUS}1/{numtext(abs(v))}){var}")
    return f"{var}/{dec(v)}"


def money(v) -> str:
    return f"${dec(v, 2)}"


def _surface(opt: str) -> tuple:
    """What an option looks like at a glance -- the same signature the gate uses.

    Both minus signs count. An Exact prints the typeset U+2212 and this topic's
    own renderers (`numtext`, `dec`, `money`) print the ASCII hyphen, so reading
    only one of them would leave this guard blind to negatives -- which is the
    one surface it exists to watch.
    """
    return (bool(re.search(r"[a-zA-Z]", opt.replace("pi", "").replace("\u03c0", ""))),
            "\u03c0" in opt or "pi" in opt, "\u221a" in opt or "sqrt" in opt,
            "/" in opt, "." in opt, opt.strip().startswith(("-", "\u2212")))


def choose(key, mistakes, rng, **kw):
    """assemble(), with the draw rejected when the key ends up alone in its form.

    A negative key among three positive options is crossed off without doing any
    algebra. The misconceptions that produce a same-signed option are already in
    every pool here, so when none of them survives the right answer is to redraw
    rather than to invent one.
    """
    choices, latex, reasons, letter = assemble(key, mistakes, rng, **kw)
    shapes = [_surface(c) for c in choices]
    if shapes.count(shapes["ABCD".index(letter)]) == 1:
        raise ItemError("the key would be the only option of its surface form")
    return choices, latex, reasons, letter


def year_text(v) -> str:
    """A year is a label, not a quantity: 1980, never 1,980.

    Everything else in a stem is a measurement and groups its thousands, which
    is why this cannot just be `numtext`.
    """
    return str(int(v))
