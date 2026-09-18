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

import itertools
import re
from fractions import Fraction as Q

from ...exact import E, Exact
from ...expr import fmt_money, fmt_places, sign_join
from ...item import Item, ItemError, Mis, assemble, assemble_text

__all__ = ["q", "ex", "numtext", "dec", "money", "coef_text", "lin_text", "std_text",
           "term_text", "point_text", "signed_join", "choose", "shortlist",
           "shortlist_text", "sig", "pair", "text_item", "GROUP_FROM", "MINUS",
           "plural"]

GROUP_FROM = 1000          # the source prints 1,277.94 and 4,529 but not 641

# The SAT typesets a minus as U+2212, and so does `Exact.plain`, which renders
# every option `assemble` orders. A stem rendered in this module and an option
# rendered there land on the same page, so the two have to spell the sign the
# same way: an ASCII hyphen beside a typeset minus is visible on the page. The
# hyphen that joins words -- "a 4-hectare park", "the x-axis" -- is a hyphen and
# stays one; only a sign or an operator becomes U+2212.
MINUS = "\N{MINUS SIGN}"


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

    The rounding is the shared `expr.fmt_places` -- half away from zero, the way
    a price list does it. What is added here is the second mode: several source
    items print a coefficient at whatever length it actually has, so 5 stays 5
    where 2.5 stays 2.5, and a fraction with no finite expansion is a bug rather
    than something to round.
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
    return fmt_places(v, places).replace("-", MINUS)


def money(v, places: int = 2) -> str:
    return fmt_money(v, places).replace("-", MINUS)


def numtext(v, style: str = "frac", places: int | None = None) -> str:
    """A bare number as the source prints it: 162, 4,529, 7.30, 3/4, −1/2.

    The sign is the typeset minus. Everything printed in this topic goes
    through here, so this is the one place that has to get it right.
    """
    v = q(v)
    if places is not None or style == "dec":
        return dec(v, places)
    if v.denominator == 1:
        n = v.numerator
        return (f"{n:,}" if abs(n) >= GROUP_FROM else str(n)).replace("-", MINUS)
    return f"{MINUS if v < 0 else ''}{abs(v.numerator)}/{v.denominator}"


def coef_text(m, var: str, style: str = "frac", places: int | None = None) -> str:
    """'4x', '−x', '(3/4)x', '0.50x'. A bare fraction against a variable
    needs its brackets, or −1/2x reads as −1/(2x)."""
    m = q(m)
    if m == 1:
        return var
    if m == -1:
        return f"{MINUS}{var}"
    if m.denominator != 1 and style != "dec" and places is None:
        # the sign sits outside the brackets, as the SAT prints it: −(1/4)x
        return f"{MINUS}({numtext(-m)}){var}" if m < 0 else f"({numtext(m)}){var}"
    return f"{numtext(m, style, places)}{var}"


def term_text(m, var: str, style: str = "frac", places: int | None = None) -> str:
    """A term on its own, where a coefficient of 1 is still printed: '1x' never
    happens, but '$5.48x' does, so this is coef_text with no special case for
    a decimal one."""
    return coef_text(m, var, style, places)


def signed_join(head: str, b, style: str = "frac", places: int | None = None) -> str:
    """Join a constant onto a term: '6x + 8', '6x − 8'.

    The join itself is the shared `expr.sign_join`, which reads a term's own
    printed sign and writes the typeset one. Deciding here instead would mean a
    second place that has to agree with `numtext` about how a negative is
    spelled, and the two drifting apart is what puts an ASCII hyphen next to a
    typeset minus on the same page.
    """
    b = q(b)
    if b == 0:
        return head
    return sign_join([head, numtext(b, style, places)])


def lin_text(m, b, var: str = "x", style: str = "frac", places: int | None = None) -> str:
    """'6x + 8', '−x − 4', '(1/4)x'. The slope-intercept right-hand side."""
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
    """Join a second variable term onto a first: '3a + 4b', '0.48x − 0.04y'.

    `coef_text` already signs the term, so the shared `expr.sign_join` reads
    that sign back rather than this deciding it a second time.
    """
    return sign_join([head, coef_text(q(m), var, style, places)])


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
    """What an option looks like at a glance -- the gate's own signature.

    A negative is spelled with the typeset minus, U+2212, because that is what
    `Exact.plain` prints and what the page shows; an option written out by hand
    here may still carry the ASCII hyphen. Reading only one of the two is how
    this signature quietly stops seeing negatives at all, which is the single
    thing it exists to see: a lone negative among three positives is the answer.
    """
    return (bool(re.search(r"[a-zA-Z]", opt.replace("pi", "").replace("π", ""))),
            "π" in opt or "pi" in opt, "√" in opt or "sqrt" in opt,
            "/" in opt, "." in opt, opt.strip().startswith(("-", "\N{MINUS SIGN}")))


def _hands_the_key_over(choices: list[str], letter: str) -> bool:
    """Do the four printed options give the answer away by their looks alone?

    The giveaway is the key standing alone in its printed shape while the other
    three form a crowd for it to stand out from -- the only negative, the only
    fraction, the only radical. Four options that all look different are not a
    giveaway, because then nothing is lone: every option is the only one of its
    own shape and the key does not stand out among them.
    """
    shapes = [_surface(c) for c in choices]
    key_i = "ABCD".index(letter)
    others = [s for i, s in enumerate(shapes) if i != key_i]
    return shapes.count(shapes[key_i]) == 1 and max(others.count(s) for s in others) > 1


def shortlist(key, mistakes: list[Mis], fmt_value=None) -> list[Mis]:
    """Which three of a named pool print. Signed answers only.

    `assemble` takes the first three wrong answers it can use, preferring ones
    of the key's own surface form, and for a signed answer that is the wrong
    three often enough to matter. A perpendicular slope is a negative
    reciprocal, so the key is a fraction, so the fractions in the pool go in
    first and the integers -- the given line's own slope among them, which is
    the error the whole item is about -- are crowded out by weaker mistakes
    that happen to be fractions too. What prints is then one negative fraction
    against three options that are not, and a student who knows only that a
    perpendicular slope is a negative reciprocal picks it without computing
    anything.

    So the pools here name more mistakes than can print, and this chooses among
    them, earliest first, so that the most telling misconceptions print
    whenever they can. A trio is refused when

      * no wrong answer carries the key's sign -- `assemble` would then have to
        swap one in, and would rather raise than print a lone negative; or
      * the printed four would hand the key over by their looks.

    Nothing here recomputes or even reads the key's value: the choice is made
    on how the four options look, which is the property being protected, and
    every option that prints still carries the misconception that produces it.
    A source item that names its own three in `wrongs` never reaches this --
    College Board already chose there.
    """
    def printed(v) -> str:
        return fmt_value(v) if fmt_value else v.plain()

    key = ex(key)
    pool, seen = [], {key}
    for m in mistakes:
        v = ex(m.value)
        if v in seen:                       # `assemble` would drop it anyway
            continue
        seen.add(v)
        pool.append((m, v, printed(v)))
    if len(pool) <= 3:
        return [m for m, _, _ in pool]
    key_text, negative = printed(key), float(key) < 0
    for trio in itertools.combinations(pool, 3):
        if not any((float(v) < 0) == negative for _, v, _ in trio):
            continue
        if not _hands_the_key_over([key_text] + [t for _, _, t in trio], "A"):
            return [m for m, _, _ in trio]
    return [m for m, _, _ in pool[:3]]


def choose(key, mistakes, rng, **kw):
    """assemble(), over the three of the pool that print, and never a giveaway.

    Two steps, and the order is the point. `shortlist` decides which named
    mistakes print, because a pool that names six and prints three can print
    the three that leave the key looking like every other option. Only then is
    the draw refused, when even the best trio in the pool would leave the key
    alone on the page: that is a thin pool, and the honest answer is to redraw
    rather than to invent a wrong answer nobody would reach.
    """
    if kw.get("signed"):
        mistakes = shortlist(key, mistakes, kw.get("fmt_value"))
    choices, latex, reasons, letter = assemble(key, mistakes, rng, **kw)
    if _hands_the_key_over(choices, letter):
        raise ItemError("the printed options would hand the key over")
    return choices, latex, reasons, letter


def shortlist_text(key_text: str, eligible: list[Mis]) -> list[Mis]:
    """Which three written options print, when the pool names more than three.

    The same choice `shortlist` makes for numeric options, on the same grounds
    and with none of the sign arithmetic, because a written option has no sign
    to share. A symbolic slope printed as (2n - 4)/8 beside (n + 4)/(-8) leaves
    -1/2 the only option on the page with no letter in it, and "changed the
    sign of the slope" -- which prints as 1/2, and was sitting fourth in a pool
    where only three can appear -- breaks up the pair that gives it away.

    Earliest first, so the pool's own order still says which mistakes matter
    most and a pool whose first three already print well is left alone.
    """
    if len(eligible) <= 3:
        return list(eligible)
    for trio in itertools.combinations(eligible, 3):
        if not _hands_the_key_over([key_text] + [m.value[0] for m in trio], "A"):
            return list(trio)
    return list(eligible[:3])


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
    eligible, seen, sigs = [], {key_text}, {tuple(key_sig)}
    for m in wrong:
        if m.value is None:
            continue
        text, s = m.value
        if text in seen or tuple(s) in sigs:
            continue
        seen.add(text)
        sigs.add(tuple(s))
        eligible.append(m)
    if len(eligible) < 3:
        raise ItemError("could not build three distinct written distractors")
    picked = shortlist_text(key_text, eligible)
    choices, reasons, letter = assemble_text(
        key_text, [Mis(m.reason, m.value[0]) for m in picked], rng)
    by_text = {m.value[0]: m.value[1] for m in picked}
    by_text[key_text] = list(key_sig)
    P["texts"] = list(choices)
    P["sigs"] = [by_text[c] for c in choices]
    return Item(template, skill, difficulty, seed, stem, "mcq", E(0), letter, rationale,
                choices, reasons, list(choices), figure=figure, table=table, params=P)
