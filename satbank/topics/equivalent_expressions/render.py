"""How an algebraic expression is printed on this topic's page.

Every option in Equivalent Expressions *is* an expression, so the rendering is
the item: a lost bracket, a "+ -3", a coefficient of 1 left visible, and the
option is wrong on the page even though the mathematics behind it is right.
That printing lives here once, and nothing in this file computes an answer --
the algebra stays in the templates and is re-derived in `audit.py` from the
printed strings alone.

The SAT is typeset, so this is too: x², x⁻¹, ³√, and a real minus sign.
"""

from __future__ import annotations

import re
from fractions import Fraction as Q

__all__ = ["MINUS", "Q", "sup", "num", "dec", "power", "pow_of", "mono", "join",
           "poly", "paren", "coef_paren", "sent", "frac", "root", "VARS", "PAIRS",
           "pc", "terms", "show_terms"]

MINUS = "−"                      # U+2212, the character the source prints
_SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")

VARS = ["x", "n", "p", "t", "w", "y", "z", "d", "a", "r", "k", "j"]
PAIRS = [("x", "y"), ("a", "b"), ("y", "z"), ("p", "q"), ("s", "t"),
         ("c", "d"), ("u", "v")]


def sup(n: int) -> str:
    """3 -> '³', -2 -> '⁻²', 14 -> '¹⁴'."""
    return str(int(n)).translate(_SUP)


def dec(v) -> str:
    """A decimal the way the source prints one: 0.36, 12.16, −7.2."""
    v = Q(v)
    s = f"{float(abs(v)):.10f}".rstrip("0").rstrip(".") or "0"
    return (MINUS + s) if v < 0 else s


def num(v, decimal: bool = False) -> str:
    """A number as an option prints it: 8, −11, 1/2, 0.36."""
    v = Q(v)
    if decimal:
        return dec(v)
    if v.denominator == 1:
        n = v.numerator
        return (MINUS + str(-n)) if n < 0 else str(n)
    body = f"{abs(v.numerator)}/{v.denominator}"
    return (MINUS + body) if v < 0 else body


def frac(a, b) -> str:
    """A quotient of two already-printed expressions: '9/((x + 1)(4x − 5))'."""
    return f"{a}/{b}"


def power(var: str, e) -> str:
    """'x', 'x²', 'x⁻¹', 'x^(1/2)'. An exponent of 0 prints nothing."""
    e = Q(e)
    if e == 0:
        return ""
    if e == 1:
        return var
    if e.denominator == 1:
        return var + sup(int(e))
    return f"{var}^({num(e)})"


def pow_of(base: str, e) -> str:
    """A power of something already bracketed: '(x + 4)²', '(x + 4)^(1/2)'."""
    e = Q(e)
    if e == 1:
        return base
    if e == 0:
        return "1"
    if e.denominator == 1:
        return base + sup(int(e))
    return f"{base}^({num(e)})"


def root(index: int, radicand: str) -> str:
    """'√x', '³√(x³y⁶)'. The radicand arrives already bracketed if it needs to be."""
    return ("√" if index == 2 else sup(index) + "√") + radicand


def mono(coef, powers, decimal: bool = False) -> str:
    """A single term: '56y²z²', '−x', '(1/2)x', '8'.

    `powers` is a list of (variable, exponent). A fraction against a variable
    is bracketed, or −1/2x reads as −1/(2x).
    """
    coef = Q(coef)
    body = "".join(power(v, e) for v, e in powers if Q(e) != 0)
    if coef == 0:
        return "0"
    if not body:
        return num(coef, decimal)
    if coef == 1:
        return body
    if coef == -1:
        return MINUS + body
    if coef.denominator != 1 and not decimal:
        return f"{MINUS if coef < 0 else ''}({num(abs(coef))}){body}"
    return f"{num(coef, decimal)}{body}"


def join(parts: list[str]) -> str:
    """Sum already-signed terms readably: '3x − 7', never '3x + −7'."""
    parts = [p for p in parts if p != ""]
    if not parts:
        return "0"
    out = parts[0]
    for p in parts[1:]:
        if p.startswith(MINUS):
            out += f" {MINUS} {p[1:]}"
        elif p.startswith("-"):
            out += f" {MINUS} {p[1:]}"
        else:
            out += f" + {p}"
    return out


def poly(coeffs, var: str = "x", decimal: bool = False) -> str:
    """Coefficients lowest degree first -> '5x² − 2x + 3'."""
    parts = []
    for i in range(len(coeffs) - 1, -1, -1):
        if Q(coeffs[i]) != 0:
            parts.append(mono(coeffs[i], [(var, i)], decimal))
    return join(parts) if parts else "0"


def paren(body: str) -> str:
    return f"({body})"


def coef_paren(c, inner: str, decimal: bool = False) -> str:
    """'2(x + 5)', '−(x − 3)', '(1/3)(x − k)'."""
    c = Q(c)
    if c == 1:
        return f"({inner})"
    if c == -1:
        return f"{MINUS}({inner})"
    if c.denominator != 1 and not decimal:
        return f"{MINUS if c < 0 else ''}({num(abs(c))})({inner})"
    return f"{num(c, decimal)}({inner})"


def sent(text: str) -> str:
    """One space between words, and a displayed expression keeps its own line."""
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r" *\n *", "\n", text).strip()


# ------------------------------------------------- values, before they print
#
# A template compares candidate answers as values and only then prints them,
# so a "distractor" can never turn out to be the key in a different jacket.

def pc(coeffs) -> tuple:
    """A one-variable polynomial as a canonical tuple, lowest degree first."""
    c = [Q(x) for x in coeffs]
    while len(c) > 1 and c[-1] == 0:
        c.pop()
    return tuple(c)


def terms(*pairs) -> tuple:
    """A multivariable expression as a canonical bag of terms.

    Each pair is (powers, coefficient) with powers a list of (variable,
    exponent). Terms are collected, zeros dropped, and the bag is ordered the
    way the source prints one: by the exponent of the first variable, then of
    the second -- a² before abc before c², and x⁻²y³z¹⁰ before x⁻⁶y¹¹z⁻².
    """
    bag: dict = {}
    for powers, c in pairs:
        k = tuple(sorted((v, Q(e)) for v, e in powers if Q(e) != 0))
        bag[k] = bag.get(k, Q(0)) + Q(c)
    live = [(k, v) for k, v in bag.items() if v != 0]
    names = sorted({v for k, _ in live for v, _ in k})

    def order(kv):
        d = dict(kv[0])
        return tuple(-d.get(n, Q(0)) for n in names)

    return tuple(sorted(live, key=order))


def show_terms(t, decimal: bool = False) -> str:
    return join([mono(c, list(powers), decimal) for powers, c in t]) if t else "0"
