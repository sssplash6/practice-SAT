"""How an equation in two variables is written on an SAT page.

This topic's answers are equations far more often than they are numbers, so
most of the work here is rendering: `5.48x + 7.30y = 1,277.94` keeps its
trailing zero and its thousands separator, `x + 3y = 70` keeps neither, and an
option that is right mathematically but printed in the wrong shape is a wrong
option.

Nothing in this module knows any mathematics. It is rendering and option
assembly only, so the solvers in `audit.py` share none of it.
"""

from __future__ import annotations

import re
from fractions import Fraction as Q

from ...exact import E, Exact
from ...item import Item, ItemError, Mis, assemble, assemble_text

__all__ = ["q", "ex", "numtext", "dec", "money", "coef_text", "lin_text", "std_text",
           "term_text", "point_text", "signed_join", "choose", "sig", "pair",
           "text_item", "GROUP_FROM", "plural"]

GROUP_FROM = 1000          # the source prints 1,277.94 and 4,529 but not 641


def q(v) -> Q:
    """Anything numeric to an exact Fraction; a float arrives as its decimal.

    `assemble` hands an option's Exact to `fmt_value`, so the renderers have to
    accept one. Every numeric answer in this topic is rational, so an Exact
    carrying a pi or a radical is a bug rather than a case to handle.
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


def dec(v, places: int | None = None) -> str:
    """'60.90' at two places, or the shortest exact decimal when places is off.

    Rounds half away from zero, the way a price list does.
    """
    v = q(v)
    if places is None:
        d, twos, fives = v.denominator, 0, 0
        while d % 2 == 0:
            d //= 2
            twos += 1
        while d % 5 == 0:
            d //= 5
            fives += 1
        if d != 1:
            raise ValueError(f"{v} has no finite decimal expansion")
        places = max(twos, fives)
    scale = 10 ** places
    n = (abs(v) * scale + Q(1, 2)).__floor__()
    whole, frac = divmod(n, scale)
    body = f"{whole:,}" if whole >= GROUP_FROM else str(whole)
    if places:
        body = f"{body}.{frac:0{places}d}"
    return ("-" if v < 0 else "") + body


def money(v, places: int = 2) -> str:
    return "$" + dec(v, places)


def numtext(v, style: str = "frac", places: int | None = None) -> str:
    """A bare number as the source prints it: 162, 4,529, 7.30, 3/4, -1/2."""
    v = q(v)
    if places is not None or style == "dec":
        return dec(v, places)
    if v.denominator == 1:
        n = v.numerator
        return f"{n:,}" if abs(n) >= GROUP_FROM else str(n)
    return f"{'-' if v < 0 else ''}{abs(v.numerator)}/{v.denominator}"


def coef_text(m, var: str, style: str = "frac", places: int | None = None) -> str:
    """'4x', '-x', '(3/4)x', '0.50x'. A bare fraction against a variable needs
    its brackets, or -1/2x reads as -1/(2x)."""
    m = q(m)
    if m == 1:
        return var
    if m == -1:
        return f"-{var}"
    if m.denominator != 1 and style != "dec" and places is None:
        return f"({numtext(m)}){var}"
    return f"{numtext(m, style, places)}{var}"


def term_text(m, var: str, style: str = "frac", places: int | None = None) -> str:
    """A term on its own, where a coefficient of 1 is still printed: '1x' never
    happens, but '$5.48x' does, so this is coef_text with no special case for
    a decimal one."""
    return coef_text(m, var, style, places)


def signed_join(head: str, b, style: str = "frac", places: int | None = None) -> str:
    b = q(b)
    if b == 0:
        return head
    sign = "+" if b > 0 else "-"
    return f"{head} {sign} {numtext(abs(b), style, places)}"


def lin_text(m, b, var: str = "x", style: str = "frac", places: int | None = None) -> str:
    """'6x + 8', '-x - 4', '(1/4)x'. The slope-intercept right-hand side."""
    m, b = q(m), q(b)
    if m == 0:
        return numtext(b, style, places)
    return signed_join(coef_text(m, var, style, places), b, style, places)


def std_text(a, b, c, xv: str = "x", yv: str = "y", style: str = "frac",
             places: int | None = None, cplaces: int | None = None,
             rhs: str | None = None) -> str:
    """'3a + 4b = 25', '0.04x + 0.48y = 661.76'. Standard form as printed.

    `rhs` replaces the right-hand side outright, for the source's '(0.04)(24)'
    and '35(1.49)' layouts.
    """
    a, b = q(a), q(b)
    if a == 0 or b == 0:
        raise ItemError("an equation in two variables needs both variables")
    left = signed_join_term(coef_text(a, xv, style, places), b, yv, style, places)
    right = rhs if rhs is not None else numtext(
        c, style, cplaces if cplaces is not None else places)
    return f"{left} = {right}"


def signed_join_term(head: str, m, var: str, style: str = "frac",
                     places: int | None = None) -> str:
    """Join a second variable term onto a first: '3a + 4b', '0.48x - 0.04y'."""
    m = q(m)
    sign = "+" if m > 0 else "-"
    return f"{head} {sign} {coef_text(abs(m), var, style, places)}"


def point_text(x, y, style: str = "frac", places: int | None = None) -> str:
    return f"({numtext(x, style, places)}, {numtext(y, style, places)})"


def plural(n, one: str, many: str) -> str:
    return one if q(n) == 1 else many


# ------------------------------------------------------- option assembly

def sig(*vals) -> list:
    """A signature the audit can recompute: every rational as num, den."""
    out: list[int] = []
    for v in vals:
        if isinstance(v, str):
            out.append(v)                                   # a role name
            continue
        f = q(v)
        out += [f.numerator, f.denominator]
    return out


def pair(text: str, *vals) -> tuple:
    return (text, sig(*vals))


def _surface(opt: str) -> tuple:
    """What an option looks like at a glance -- the gate's own signature."""
    return (bool(re.search(r"[a-zA-Z]", opt.replace("pi", "").replace("π", ""))),
            "π" in opt or "pi" in opt, "√" in opt or "sqrt" in opt,
            "/" in opt, "." in opt, opt.strip().startswith("-"))


def choose(key, mistakes, rng, **kw):
    """assemble(), with the draw rejected when the key ends up alone in its form.

    A lone negative among three positive options is crossed off without doing
    any algebra. Every pool here already carries misconceptions that produce a
    same-signed option, so when none of them survives the right answer is to
    redraw rather than to invent one.
    """
    choices, latex, reasons, letter = assemble(key, mistakes, rng, **kw)
    shapes = [_surface(c) for c in choices]
    if shapes.count(shapes["ABCD".index(letter)]) == 1:
        raise ItemError("the key would be the only option of its surface form")
    return choices, latex, reasons, letter


def text_item(template, skill, difficulty, seed, stem, key_text, key_sig, wrong, rng, P,
              rationale, figure=None, table=None):
    """Four written options, one of them right, with the signatures recorded.

    The options here are equations, points and sentences rather than values, so
    there is no ascending order to hide the key in and `assemble_text` shuffles
    instead. What each option encodes is recorded in `params`, and the
    independent solver recomputes that signature from the raw numbers and asks
    which option it belongs to -- so the mathematics is checked head on and the
    rendering as a side effect.
    """
    picked, seen, sigs = [], {key_text}, {tuple(key_sig)}
    for m in wrong:
        if m.value is None:
            continue
        text, s = m.value
        if text in seen or tuple(s) in sigs:
            continue
        seen.add(text)
        sigs.add(tuple(s))
        picked.append(m)
        if len(picked) == 3:
            break
    if len(picked) < 3:
        raise ItemError("could not build three distinct written distractors")
    choices, reasons, letter = assemble_text(
        key_text, [Mis(m.reason, m.value[0]) for m in picked], rng)
    by_text = {m.value[0]: m.value[1] for m in picked}
    by_text[key_text] = list(key_sig)
    P["texts"] = list(choices)
    P["sigs"] = [by_text[c] for c in choices]
    return Item(template, skill, difficulty, seed, stem, "mcq", E(0), letter, rationale,
                choices, reasons, list(choices), figure=figure, table=table, params=P)
