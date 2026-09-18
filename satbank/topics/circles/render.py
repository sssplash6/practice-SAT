"""How a circle item prints.

The source set writes the same quantity three different ways -- 13pi/2 in one
item and a stacked 13/2 followed by pi in another, a radius as 5 in one option
and as an unsimplified square root in the next -- so the surface form is a
parameter of the template, not a property of the number.
"""

from __future__ import annotations

from fractions import Fraction

from ...exact import Exact
from ...expr import fmt_num, sign_join

__all__ = ["pi_back", "pi_front", "pi_style", "radical", "point", "sq_term",
           "standard_equation", "general_equation", "coef_term", "degrees",
           "num", "MINUS"]

MINUS = "\N{MINUS SIGN}"       # U+2212, the sign a typeset page prints


def num(v, **kw) -> str:
    """A number as this page prints it: fmt_num's digits, with a typeset sign.

    `Exact.plain` already spells a negative U+2212, but the shared algebra
    formatters in `expr.py` spell it with the ASCII hyphen, and an item that
    takes its stem from one and its options from the other prints two
    different minus signs on one page. Everything in this module is read by a
    student, so it all goes out in the page's spelling. Nothing about equality
    changes: `item.norm_text`, `item.numeral` and this topic's `option_check`
    all fold the two together on the way in.

    A grid-in keeps the ASCII sign -- that is a keystroke, not a page -- so it
    is built from `Exact.gridin` and never comes through here.
    """
    return fmt_num(v, **kw).replace("-", MINUS)


# ------------------------------------------------------------- pi multiples

def pi_back(v: Exact) -> str:
    """13pi/2 -- the coefficient split around the symbol, as exact.py writes it."""
    return v.plain()


def pi_front(v: Exact) -> str:
    """13/2 pi -- the whole coefficient first, as a stacked fraction would print.

    The source uses this form whenever the coefficient is a fraction, and
    writes a bare pi as 1pi when it does, which is why the 1 is kept here.
    """
    if v.pi_exp != 1 or v.rad != 1:
        return v.plain()
    n, d = v.coef.numerator, v.coef.denominator
    sign = MINUS if n < 0 else ""
    n = abs(n)
    return f"{sign}{n}π" if d == 1 else f"{sign}{n}/{d} π"


def pi_style(style: str):
    return pi_front if style == "front" else pi_back


def radical(v: Exact) -> str:
    """sqrt(40) rather than 2*sqrt(10).

    A radius read off an equation is the square root of the constant, and the
    source prints it that way -- unsimplified -- so the option matches the
    arithmetic the student just did.
    """
    if v.rad == 1 or v.pi_exp != 0 or v.coef.denominator != 1 or v.coef < 0:
        return v.plain()
    return f"√{v.coef.numerator ** 2 * v.rad}"


def degrees(v) -> str:
    return f"{num(v)}°"


# -------------------------------------------------------------------- points

def point(x, y) -> str:
    return f"({num(x)}, {num(y)})"


# ----------------------------------------------------------------- equations

def sq_term(var: str, c) -> str:
    """(x − 6)², (x + 8)², x² -- the squared factor for a center coordinate."""
    c = Fraction(c)
    if c == 0:
        return f"{var}²"
    if c > 0:
        return f"({var} {MINUS} {num(c)})²"
    return f"({var} + {num(-c)})²"


def standard_equation(h, k, rhs: str) -> str:
    return f"{sq_term('x', h)} + {sq_term('y', k)} = {rhs}"


def coef_term(coef, body: str) -> str:
    """A signed term: 8x², −64py, x², −y. Empty when the coefficient is zero."""
    coef = Fraction(coef)
    if coef == 0:
        return ""
    if not body:
        return num(coef)
    if coef == 1:
        return body
    if coef == -1:
        return f"{MINUS}{body}"
    return f"{num(coef)}{body}"


def general_equation(a, d, e, rhs, *, sym: str = "") -> str:
    """a*x^2 + d*x + a*y^2 + e*y = rhs, in the order the source writes it.

    `sym` names a constant the linear coefficients carry, so the symbolic
    items print 112px rather than 112x, with the right-hand side in sym^2.
    """
    s = sym
    parts = [coef_term(a, "x²"), coef_term(d, f"{s}x"),
             coef_term(a, "y²"), coef_term(e, f"{s}y")]
    lhs = sign_join([p for p in parts if p])
    tail = f"{s}²" if s else ""
    right = coef_term(rhs, tail) if tail else num(rhs)
    return f"{lhs} = {right or '0'}"
