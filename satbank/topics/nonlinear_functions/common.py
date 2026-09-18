"""How a nonlinear function is written on an SAT page.

Nothing in this module knows any mathematics. It renders, and it assembles
options; the algebra lives in the families and is re-derived from scratch in
`audit.py`, which imports none of this.

The source set prints powers as typeset superscripts (x², x⁵, a²⁹) and a
variable exponent with a caret, the way the rest of the engine does
(`expr.exp_model` prints `250(1.04)^x`). Decimals keep the digits the item
prints -- `0.90`, `1.70`, `0.66` -- because an exponential model's base is
read digit for digit.
"""

from __future__ import annotations

import random
import re
from fractions import Fraction as Q

from ...exact import E, Exact
from ...item import Item, ItemError, Mis, assemble, assemble_text

__all__ = ["MINUS", "Q", "q", "ex", "sup", "num", "dec", "power", "mono", "join",
           "signed", "linear_factor",
           "poly_text", "factored", "exp_text", "point", "fn", "money", "choose",
           "text_item", "sig", "pair", "unambiguous", "pick", "terminating",
           "ordinal", "year"]

MINUS = "−"                      # U+2212, the character the source prints
_SUP = str.maketrans("0123456789-/", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻ᐟ")

ORDINALS = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
            6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth"}


def q(v) -> Q:
    """Anything numeric to an exact Fraction; a float arrives as its decimal."""
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
    """True when the fraction has a finite decimal expansion."""
    d = q(v).denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def sup(n) -> str:
    """3 -> '³', -2 -> '⁻²', 29 -> '²⁹'."""
    return str(n).translate(_SUP)


def num(v, group_from: int = 1000) -> str:
    """A number as an option prints it: 8, −11, 3/4, 1,200."""
    v = q(v)
    if v.denominator == 1:
        n = v.numerator
        body = f"{abs(n):,}" if abs(n) >= group_from else str(abs(n))
        return (MINUS + body) if n < 0 else body
    body = f"{abs(v.numerator):,}/{v.denominator}" if abs(v.numerator) >= group_from \
        else f"{abs(v.numerator)}/{v.denominator}"
    return (MINUS + body) if v < 0 else body


def dec(v, places: int | None = None) -> str:
    """'0.90' at two places, or the shortest exact decimal when places is off."""
    v = q(v)
    if places is not None:
        body = f"{abs(float(v)):.{places}f}"
        whole, _, frac = body.partition(".")
        whole = f"{int(whole):,}" if int(whole) >= 1000 else whole
        return (MINUS if v < 0 else "") + (f"{whole}.{frac}" if frac else whole)
    if not terminating(v):
        raise ItemError(f"{v} has no finite decimal expansion")
    d, twos, fives = v.denominator, 0, 0
    while d % 2 == 0:
        d //= 2
        twos += 1
    while d % 5 == 0:
        d //= 5
        fives += 1
    return dec(v, max(twos, fives))


def power(var: str, e) -> str:
    """'x', 'x²', 'x⁵'. An exponent of 0 prints nothing."""
    e = int(e)
    if e == 0:
        return ""
    return var if e == 1 else var + sup(e)


def mono(coef, var: str, e, decimals: int | None = None) -> str:
    """One term: '4x²', '−x', '(3/4)x', '0.50x', '15'."""
    coef = q(coef)
    body = power(var, e)
    if coef == 0:
        return "0"
    if not body:
        return dec(coef, decimals) if decimals is not None else num(coef)
    if coef == 1:
        return body
    if coef == -1:
        return MINUS + body
    if coef.denominator != 1 and decimals is None:
        return f"{MINUS if coef < 0 else ''}({num(abs(coef))}){body}"
    head = dec(coef, decimals) if decimals is not None else num(coef)
    return f"{head}{body}"


def join(parts: list[str]) -> str:
    """Sum already-signed terms readably: '3x − 7', never '3x + −7'."""
    parts = [p for p in parts if p not in ("", "0")]
    if not parts:
        return "0"
    out = parts[0]
    for p in parts[1:]:
        if p.startswith(MINUS) or p.startswith("-"):
            out += f" {MINUS} {p[1:]}"
        else:
            out += f" + {p}"
    return out


def poly_text(coeffs, var: str = "x", decimals: int | None = None) -> str:
    """Coefficients lowest degree first -> '4x² − 50x + 126'."""
    parts = [mono(coeffs[i], var, i, decimals)
             for i in range(len(coeffs) - 1, -1, -1) if q(coeffs[i]) != 0]
    return join(parts) if parts else "0"


def _linear(m, b, var: str) -> str:
    m, b = q(m), q(b)
    head = var if m == 1 else (MINUS + var if m == -1 else f"{num(m)}{var}")
    if b == 0:
        return head
    return f"{head} {MINUS} {num(-b)}" if b < 0 else f"{head} + {num(b)}"


def factored(factors, lead=1, var: str = "x") -> str:
    """'(x + 6)(x − 4)', '2(x − 4)²', '11x(x − 1)'.

    `factors` is a list of (m, b, power) triples for (m·var + b)^power. A
    factor of (1, 0, 1) prints as the bare variable.
    """
    lead = q(lead)
    head = "" if lead == 1 else (MINUS if lead == -1 else num(lead))
    body = ""
    for m, b, p in factors:
        text = _linear(m, b, var)
        if q(m) == 1 and q(b) == 0:
            body += var if p == 1 else var + sup(p)
        else:
            body += f"({text})" + (sup(p) if p != 1 else "")
    return head + body


def exp_text(a, base, expo: str, base_places: int | None = None,
             a_places: int | None = None) -> str:
    """'53(2)^d', '600(0.85)^t', '233(1.70)^(x/2)', '9,000(0.66)^x'."""
    head = dec(a, a_places) if a_places is not None else num(a)
    b = dec(base, base_places) if base_places is not None else num(base)
    return f"{head}({b})^{expo}"


def signed(head: str, v, plus: str = " + ") -> str:
    """Append a signed term readably: '4(x − 3)² + 5', '… − 1', and nothing at 0."""
    v = q(v)
    if v == 0:
        return head
    return f"{head}{plus}{num(v)}" if v > 0 else f"{head} {MINUS} {num(-v)}"


def linear_factor(r, var: str = "x") -> str:
    """The factor a zero produces: 3 -> '(x − 3)', −3 -> '(x + 3)'."""
    r = q(r)
    if r == 0:
        return var
    return f"({var} {MINUS} {num(r)})" if r > 0 else f"({var} + {num(-r)})"


def point(x, y) -> str:
    return f"({num(x)}, {num(y)})"


def fn(name: str, var: str, body: str) -> str:
    return f"{name}({var}) = {body}"


def money(v) -> str:
    return "$" + dec(v, 2)


def year(v) -> str:
    """A year is a label, not a quantity: 2010, never 2,010."""
    return str(int(q(v)))


def ordinal(n: int) -> str:
    return ORDINALS.get(int(n), f"{int(n)}th")


# ----------------------------------------------------------------- guards

def unambiguous(value, step) -> bool:
    """False when the exact value sits halfway between two printable answers.

    A stem that says *closest*, *nearest* or *approximately*, or that prints
    money, has no defensible key when the truth lands on a half-step: both
    neighbours are equally close and both may be printed.
    """
    v, s = q(value), q(step)
    if s == 0:
        return True
    return (v / s - Q(1, 2)).denominator != 1


# ------------------------------------------------------------ assembling

def _surface(opt: str) -> tuple:
    """What an option looks like at a glance -- the gate's own signature.

    Deliberately the same crude test `check._shape` makes, both sign
    characters included: a guard stricter than the gate rejects draws the gate
    would have passed, and a looser one ships them. Reading only the ASCII
    hyphen here, while the page prints U+2212, is what let a lone positive
    fraction through before the core began typesetting the minus sign.
    """
    return (bool(re.search(r"[a-zA-Z]", opt.replace("pi", "").replace("π", ""))),
            "π" in opt or "pi" in opt, "√" in opt or "sqrt" in opt,
            "/" in opt, "." in opt, opt.strip().startswith(("-", MINUS)))


def choose(key, mistakes, rng, **kw):
    """assemble(), with the draw rejected when the key ends up alone in form.

    Unless a source item named its own wrong answers: there the College Board
    option set is the authority and the engine has nothing to guess at.
    """
    named = getattr(mistakes, "named", False)
    choices, latex, reasons, letter = assemble(key, mistakes, rng, **kw)
    shapes = [_surface(c) for c in choices]
    if not named and shapes.count(shapes["ABCD".index(letter)]) == 1:
        raise ItemError("the key would be the only option of its surface form")
    return choices, latex, reasons, letter


def sig(*vals) -> list:
    """A canonical signature for a written option, for the audit to match.

    A rational becomes [numerator, denominator]; anything else becomes its
    string. The audit recomputes the same list from the mathematics and asks
    which printed option carries it.
    """
    out: list = []
    for v in vals:
        if isinstance(v, str):
            out.append(v)
        else:
            f = q(v)
            out += [f.numerator, f.denominator]
    return out


def pair(text: str, *vals) -> tuple:
    return (text, sig(*vals))


class Named(list):
    """A list of misconceptions, remembering whether a source item named them."""
    named = False


def pick(pool: dict, order, wrongs=None) -> list:
    """The misconceptions this draw offers, in the order it offers them.

    A free draw takes the template's own order; a source item passes `wrongs`,
    naming the three the College Board item writer actually reached for. An
    entry whose value is None does not apply to this draw and is skipped.
    """
    names = list(order if wrongs is None else wrongs)
    out = Named()
    out.named = wrongs is not None
    for name in names:
        if name not in pool:
            raise ItemError(f"no misconception named {name!r} in this pool")
        why, value = pool[name]
        if value is not None:
            out.append(Mis(why, value))
    return out


def text_item(template: str, skill: str, difficulty: str, seed: int, stem: str,
              key_text: str, key_sig: list, wrong: list, rng: random.Random,
              params: dict, rationale: str, figure=None, table=None) -> Item:
    """Four written options, one of them right, with the signatures recorded.

    Deduplicated by signature as well as by text, so the same mathematics can
    never be printed twice under two spellings.
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
    shapes = [_surface(c) for c in choices]
    if (not getattr(wrong, "named", False)
            and shapes.count(shapes["ABCD".index(letter)]) == 1):
        raise ItemError("the key would be the only option of its surface form")
    by_text = {m.value[0]: m.value[1] for m in picked}
    by_text[key_text] = key_sig
    params = dict(params)
    params["texts"] = list(choices)
    params["sigs"] = [by_text[c] for c in choices]
    return Item(template, skill, difficulty, seed, stem, "mcq", E(0), letter,
                rationale, choices, reasons, list(choices), figure=figure,
                table=table, params=params)


def value_item(template: str, skill: str, difficulty: str, seed: int, stem: str,
               key, mistakes: list, rng: random.Random, params: dict,
               rationale: str, fmt: str = "mcq", fmt_value=None, signed: bool = True,
               fillers: str = "shift", figure=None, table=None) -> Item:
    """One numeric answer, as a grid-in or as four ordered options."""
    keyx = ex(key)
    if fmt == "spr":
        try:
            entered = keyx.gridin()
        except ValueError as exc:
            raise ItemError(str(exc))
        if len(entered.replace("-", "").replace(".", "").replace("/", "")) > 5:
            raise ItemError("a grid-in answer is at most five characters")
        return Item(template, skill, difficulty, seed, stem, "spr", keyx, entered,
                    rationale, figure=figure, table=table, params=params)
    if fmt_value is None:
        # Exact.plain() writes a hyphen; the source typesets a minus sign, and
        # every option on this topic is a plain rational
        fmt_value = num
    kept = Named(Mis(m.reason, ex(m.value)) for m in mistakes if m.value is not None)
    kept.named = getattr(mistakes, "named", False)
    mistakes = kept
    choices, latex, reasons, letter = choose(keyx, mistakes, rng, fmt_value=fmt_value,
                                             signed=signed, fillers=fillers)
    return Item(template, skill, difficulty, seed, stem, "mcq", keyx, letter,
                rationale, choices, reasons, latex, figure=figure, table=table,
                params=params)
