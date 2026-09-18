"""Rearranging a printed formula for one of its letters.

Nineteen of the eighty-five official items are this: a relation among three or
four quantities is printed, and the four options are four ways of solving it for
one of them. Nothing about the arithmetic is nonlinear -- what makes these hard
is that every step is invisible, so the wrong options are exactly the steps a
student botches: a term moved across the equals sign with its sign intact, a
divisor that divides only the first term, a reciprocal taken instead of a
multiplication.

The options are equations, not numbers, so `assemble` has no ascending order to
hide the key in. Every distractor is therefore decided against the key before it
is printed (`kit.text_choices`): an option that is the key in a different jacket
is a question with no defensible answer, and no check in the engine would ever
notice it.
"""

from __future__ import annotations

import math
import random
import re
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis
from ..kit import (MINUS, cap, coef_times, dec, displayed, eq, gridin,
                   griddable, mono, num, paren, pick, prod, q, sent,
                   signed_terms, sup, text_choices)

__all__ = ["isolate_sum", "isolate_bracket", "isolate_factor",
           "isolate_denominator", "scale_relation"]

LETTERS = ["b", "c", "d", "f", "g", "h", "j", "k", "m", "n", "p", "q", "r",
           "s", "t", "u", "v", "w", "y", "z"]


# --------------------------------------------------------------- the frames

FRAMES = {
    "relates_positive": "The given equation relates the positive numbers {vars}. "
                        "Which equation correctly expresses {t} in terms of {rest}?",
    "relates_distinct": "The given equation relates the distinct positive numbers "
                        "{vars}. Which equation correctly expresses {t} in terms of "
                        "{rest}?",
    "relates_plain": "The given equation relates the numbers {vars}. Which equation "
                     "correctly expresses {t} in terms of {rest}?",
    "relates_vars": "The given equation relates the variables {vars}. Which equation "
                    "correctly expresses {t} in terms of {rest}?",
    "gives": "The given equation relates the positive numbers {vars}. Which equation "
             "correctly gives {t} in terms of {rest}?",
}
FRAME_NAMES = list(FRAMES)


def _listed(names) -> str:
    names = list(names)
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"


def _order_vars(text: str, names) -> list:
    """The letters of an equation in the order the page prints them."""
    out = []
    for m in re.finditer(r"[A-Za-z][A-Za-z_]*", text):
        s = m.group()
        if s in names and s not in out:
            out.append(s)
    for s in names:                         # anything the regex could not see
        if s not in out:
            out.append(s)
    return out


def _stem(equation: str, frame: str | None, story: str | None, target: str,
          names) -> str:
    """The printed question: the equation, then the sentence that asks for it."""
    if story is not None:
        return sent(story.format(eq=equation) if "{eq}" in story
                    else displayed(equation, story))
    others = [s for s in names if s != target]
    ask = FRAMES[frame].format(vars=_listed(names), t=target, rest=_listed(others))
    return sent(displayed(equation, ask))


def _build(template: str, difficulty: str, seed: int, stem: str, key: str,
           pool: dict, wrongs, rng, rationale: str, variables,
           params: dict) -> Item:
    """One item whose four options are equations. A free draw (no `wrongs`) is
    additionally refused when the key stands alone in its printed shape."""
    ch, why, letter = text_choices(key, pick(pool, wrongs), rng,
                                   variables=tuple(variables),
                                   guard=wrongs is None)
    params = dict(params, options=list(ch))
    return Item(template, "rearranging a formula", difficulty, seed, sent(stem),
                "mcq", E(1), letter, sent(rationale), ch, why, list(ch),
                params=params)


# -------------------------------------------------------------- small print

def _n(v, style: str) -> str:
    return dec(v) if style == "dec" else num(v)


def _simple(piece: str) -> bool:
    """A single printed atom -- one letter, one subscripted letter, one number.

    `mv²` is two atoms, and `L/mv²` is not what the printed fraction bar
    means, so the test has to be this narrow.
    """
    return bool(re.fullmatch(r"[A-Za-z](_[A-Za-z0-9])?[²³]?|[\d,]+(\.\d+)?",
                             piece.strip()))


def _top_sum(piece: str) -> bool:
    """Is this a sum at its outermost level? `k + 15m` is; `2(n + p)` is not."""
    depth = 0
    for i, ch in enumerate(piece):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 0 and ch in ("+", MINUS) and i and piece[i - 1] == " ":
            return True
    return False


def over(top: str, bottom: str) -> str:
    """A quotient, bracketed wherever plain text would otherwise re-associate.

    `s/(29r)` and `s/29r` are different numbers, and only the first is what the
    printed fraction bar means; `15m/8` and `2(n + p)/7`, on the other hand,
    already read the way the bar does, and the source prints them bare.
    """
    if bottom in ("1", ""):
        return top
    t = paren(top) if _top_sum(top) else top
    b = bottom if _simple(bottom) else paren(bottom)
    return f"{t}/{b}"


def _sum_over(terms, coef, style: str) -> str:
    """A signed sum divided by a coefficient, as the page prints it."""
    body = signed_terms(terms, style)
    return over(body, _n(coef, style)) if q(coef) != 1 else body


def _neg(terms) -> list:
    return [(-q(c), s) for c, s in terms]


def _scaled(terms, k) -> list:
    return [(q(c) * q(k), s) for c, s in terms]


def _positive_first(terms) -> list:
    """Reorder so a leading minus sign does not start the line."""
    return [t for t in terms if q(t[0]) > 0] + [t for t in terms if q(t[0]) <= 0]


# ------------------------------------------- the target sits inside a sum

def isolate_sum(rng: random.Random, seed: int, *, target=None, coef=None,
                extras=None, other=None, divisor=1, order="target_left",
                style="frac", frame=None, story=None, fmt="mcq", wrongs=None,
                difficulty="easy") -> Item:
    """(α·t + extras)/δ = other -- move the extras across, then divide by α.

    The printed equation puts the target on whichever side the source put it;
    the mathematics does not care, and a student who reads only the left-hand
    side is exactly who the `sign` distractor is for.
    """
    if target is None:
        target, coef, extras, other, divisor = _draw_sum(rng)
    coef, divisor = q(coef if coef is not None else 1), q(divisor)
    extras = [(q(c), s) for c, s in (extras or [])]
    other = [(q(c), s) for c, s in (other or [])]
    if coef == 0 or divisor == 0:
        raise ItemError("a coefficient of zero leaves no equation")
    names = [s for _, s in extras + other if s]
    if target in names or len(set(names)) != len(names) or not names:
        raise ItemError("the letters of this draw do not make a usable formula")

    target_side = signed_terms([(coef, target)] + extras, style)
    if divisor != 1:
        target_side = over(target_side, _n(divisor, style))
    other_side = signed_terms(other, style)
    lhs, rhs = ((target_side, other_side) if order == "target_left"
                else (other_side, target_side))
    equation = eq(lhs, rhs)
    frame = frame or rng.choice(FRAME_NAMES)
    listed = _order_vars(equation, [target] + names)
    stem = _stem(equation, frame, story, target, listed)

    top = _scaled(other, divisor) + _neg(extras)          # δ·other − extras
    key = eq(target, _sum_over(top, coef, style))
    pool = _sum_pool(target, coef, divisor, extras, other, style)
    P = {"kind": "nleq_isolate_sum", "target": target, "coef": _p(coef),
         "divisor": _p(divisor), "extras": _pack(extras), "other": _pack(other),
         "order": order, "style": style}

    step = (f"Multiplying both sides by {_n(divisor, style)} and "
            if divisor != 1 else "")
    step += (f"taking {signed_terms(extras, style)} across leaves "
             if extras else "reading the equation the other way round gives ")
    step += eq(signed_terms([(coef, target)], style), signed_terms(top, style))
    story_text = cap(step + (f", and dividing by {_n(coef, style)} gives {key}."
                             if coef != 1 else "."))

    if fmt == "spr":
        syms = [(c, s) for c, s in top if s]
        if len(syms) != 1:
            raise ItemError("the rearranged form has no single coefficient to ask for")
        want = syms[0][0] / coef
        if not griddable(want) or want == 0:
            raise ItemError("that coefficient could not be entered in the grid")
        keyx = E(want)
        return Item("nleq.isolate_sum", "rearranging a formula", difficulty, seed,
                    sent(stem), "spr", keyx, gridin(want), sent(story_text),
                    params=dict(P, ask="coefficient"))
    return _build("nleq.isolate_sum", difficulty, seed, stem, key, pool, wrongs,
                  rng, story_text, [target] + names, dict(P, ask="equation"))


def _draw_sum(rng: random.Random):
    pool = list(LETTERS)
    rng.shuffle(pool)
    target, a, b = pool[0], pool[1], pool[2]
    coef = Q(rng.choice([1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 14, 15]))
    shape = rng.choice(["two_right", "extra_left", "const_left", "const_right"])
    if shape == "two_right":
        return target, coef, [], [(1, a), (rng.randint(2, 40), b)], 1
    if shape == "extra_left":
        return target, coef, [(-rng.randint(2, 40), a)], [(1, b)], 1
    if shape == "const_left":
        return target, coef, [(rng.randint(2, 60), "")], [(1, a), (1, b)], 1
    return target, coef, [], [(rng.randint(2, 60), ""), (rng.randint(2, 20), a)], 1


def _sum_pool(target, coef, divisor, extras, other, style) -> dict:
    moved = _scaled(other, divisor)
    top = moved + _neg(extras)
    consts = [c for c, s in extras if not s]
    vars_other = [(c, s) for c, s in other if s]

    pool = {
        "sign": Mis("moved the term across the equals sign without changing its sign",
                    eq(target, _sum_over(moved + list(extras), coef, style))),
        "negate_all": Mis("negated every term on the far side instead of the one "
                          "being moved",
                          eq(target, _sum_over(_neg(moved) + _neg(extras), coef, style))),
        "negate_all_sign": Mis("negated the far side and kept the moved term's sign "
                               "as well",
                               eq(target, _sum_over(_neg(moved) + list(extras), coef,
                                                    style))),
        "reversed": Mis("subtracted the two sides in the wrong order",
                        eq(target, _sum_over(_positive_first(_neg(top)), coef, style))),
    }
    if coef != 1:
        pool["no_divide"] = Mis("never divided by the coefficient of the unknown",
                                eq(target, signed_terms(top, style)))
        pool["multiply"] = Mis("multiplied by the coefficient of the unknown instead "
                               "of dividing by it",
                               eq(target, coef_times(coef, signed_terms(top, style),
                                                     style)))
        if len(top) >= 2:
            first, rest, last, head = top[0], top[1:], top[-1], top[:-1]
            pool["first_only"] = Mis(
                "divided only the first term by the coefficient",
                eq(target, _lead(over(mono(first[0], first[1], style=style),
                                      _n(coef, style)), rest, style)))
            pool["first_only_coef"] = Mis(
                "divided only the first term, writing the fraction in front of it",
                eq(target, signed_terms([(first[0] / coef, first[1])] + list(rest),
                                        "frac")))
            pool["last_only"] = Mis(
                "divided only the last term by the coefficient",
                eq(target, _trail(head, over(mono(last[0], last[1], style=style),
                                             _n(coef, style)), style)))
            pool["multiply_first"] = Mis(
                "multiplied the first term by the coefficient instead of dividing "
                "the whole side",
                eq(target, signed_terms([(first[0] * coef, first[1])] + list(rest),
                                        style)))
    if consts and coef != 1:
        k = abs(consts[0])
        pool["swap_over"] = Mis(
            "divided by the constant term and subtracted the coefficient, instead "
            "of the other way round",
            eq(target, over(signed_terms(moved + [(-coef, "")], style),
                            _n(k, style))))
        pool["swap_over_sign"] = Mis(
            "divided by the constant term, subtracted the coefficient and kept its "
            "sign", eq(target, over(signed_terms(moved + [(coef, "")], style),
                                    _n(k, style))))
    if len(extras) == 1 and extras[0][1] and len(vars_other) == 1 and coef == 1:
        c, s = extras[0]
        o = vars_other[0][1]
        pool["product"] = Mis("multiplied the two letters together instead of moving "
                              "one across",
                              eq(target, prod(num(abs(c)) if abs(c) != 1 else "", s, o)))
        pool["quotient"] = Mis("divided by the moved term instead of adding it back",
                               eq(target, MINUS + over(o, prod(
                                   num(abs(c)) if abs(c) != 1 else "", s))))
    return pool


def _lead(head_text: str, rest, style: str) -> str:
    """A ready-printed leading piece, then the remaining signed terms."""
    return _glue([head_text] + [mono(c, s, style=style) for c, s in rest])


def _trail(head, tail_text: str, style: str) -> str:
    return _glue([mono(c, s, style=style) for c, s in head] + [tail_text])


def _glue(parts) -> str:
    """Join already-signed pieces: `3x − 7`, never `3x + −7`.

    Both minus signs are read. Everything this file prints carries the typeset
    one, but a test for a single spelling of the sign is how a guard stops
    guarding without saying so, and this is the same shape of test that did.
    """
    parts = [p for p in parts if p not in ("", "0")]
    out = parts[0]
    for p in parts[1:]:
        out += f" {MINUS} {p[1:]}" if p.startswith((MINUS, "-")) else f" + {p}"
    return out


# ------------------------------------------- the target sits by a bracket

def isolate_bracket(rng: random.Random, seed: int, *, target=None, left=None,
                    head=None, c=None, inner=None, style="frac", frame=None,
                    story=None, wrongs=None, difficulty="medium") -> Item:
    """left = head + c(inner) -- a bracketed multiple, solved for one letter.

    The target is either the bare letter outside the bracket or one of the
    letters inside it. Both shapes are in the source, and both invite the same
    mistake: doing something to the bracket's coefficient other than dividing.
    """
    if target is None:
        target, left, head, c, inner = _draw_bracket(rng)
    c = q(c)
    left = [(q(a), s) for a, s in left]
    head = [(q(a), s) for a, s in (head or [])]
    inner = [(q(a), s) for a, s in inner]
    if c == 0 or not any(s for _, s in inner):
        raise ItemError("that bracket carries no unknown")

    bracket = coef_times(c, signed_terms(inner, style), style)
    rhs = _glue([mono(a, s, style=style) for a, s in head] + [bracket])
    equation = eq(signed_terms(left, style), rhs)
    names = []
    for _, s in left + head + inner:
        if s and s not in names:
            names.append(s)
    if target not in names or len(names) < 2:
        raise ItemError("the target is not a letter of this formula")
    frame = frame or rng.choice(FRAME_NAMES)
    listed = _order_vars(equation, names)
    stem = _stem(equation, frame, story, target, listed)

    outside = {s for _, s in left + head if s}
    if target in outside:
        a = next(cc for cc, s in left if s == target)
        rest = [(cc, s) for cc, s in left if s != target]
        front = head + _neg(rest)
        key_expr = _bracket_over(c, inner, front, a, style)
        pool = _bracket_outside_pool(target, a, c, inner, front, style)
        route = "outside"
    else:
        s_in = next(cc for cc, s in inner if s == target)
        rest = [(cc, s) for cc, s in inner if s != target]
        diff = left + _neg(head)
        k = 1 / (c * s_in)
        trail = _scaled(rest, -1 / s_in)
        key_expr = _bracket_inside(k, diff, trail, style)
        pool = _bracket_inside_pool(target, k, diff, trail, c, style)
        route = "inside"
    key = eq(target, key_expr)
    P = {"kind": "nleq_isolate_bracket", "target": target, "left": _pack(left),
         "head": _pack(head), "c": _p(c), "inner": _pack(inner), "style": style,
         "route": route}
    rationale = (f"Undoing the terms around the bracket in {equation} and then its "
                 f"coefficient gives {key}.")
    return _build("nleq.isolate_bracket", difficulty, seed, stem, key, pool, wrongs,
                  rng, rationale, names, P)


def _draw_bracket(rng: random.Random):
    pool = list(LETTERS)
    rng.shuffle(pool)
    if rng.random() < 0.5:                       # the target is the bare side
        t, a, b = pool[0], pool[1], pool[2]
        return (t, [(rng.randint(2, 12), t)], [],
                Q(rng.choice([2, 3, 4, 5, 6, 7])), [(1, a), (1, b)])
    t, a = pool[0], pool[1]
    return (t, [(1, a)], [], Q(rng.choice([2, 3, 4, 5, 8, 10, 20])),
            [(1, t), (-rng.randint(2, 60), "")])


def _bracket_over(c, inner, front, a, style) -> str:
    body = coef_times(c, signed_terms(inner, style), style)
    if front:
        body = _glue([mono(cc, s, style=style) for cc, s in front] + [body])
    return over(body, _n(a, style)) if q(a) != 1 else body


def _bracket_inside(k, diff, trail, style) -> str:
    head = coef_times(k, signed_terms(diff, style), style)
    return _glue([head] + [mono(c, s, style=style) for c, s in trail])


def _bracket_outside_pool(target, a, c, inner, front, style) -> dict:
    plain = _bracket_over(c, inner, front, 1, style)
    letters = [(1, s) for _, s in inner if s]
    return {
        "no_divide": Mis("never divided by the coefficient of the unknown",
                         eq(target, plain) if a != 1 else None),
        "subtract_divisor": Mis("subtracted the coefficient of the unknown instead "
                                "of dividing by it",
                                eq(target, _glue([plain, mono(-a, "", style=style)]))
                                if a != 1 else None),
        "strip_brackets": Mis("dropped the bracket, subtracted every letter inside "
                              "it and then the coefficient as well",
                              eq(target, signed_terms([(c, "")] + _neg(letters)
                                                      + [(-a, "")], style))
                              if a != 1 else None),
        "multiply": Mis("multiplied by the coefficient of the unknown instead of "
                        "dividing by it",
                        eq(target, coef_times(a, plain, style)) if a != 1 else None),
        "inner_over": Mis("divided only the bracket's coefficient by the "
                          "coefficient of the unknown",
                          eq(target, coef_times(c / a, signed_terms(inner, style),
                                                style))
                          if a != 1 and not front else None),
        "over_bracket": Mis("divided by the bracket's own coefficient instead of "
                            "by the coefficient of the unknown",
                            eq(target, over(_bracket_over(1, inner, front, 1, style),
                                            _n(c, style)))
                            if a != 1 and c != 1 else None),
        "over_both": Mis("divided by the bracket's coefficient as well as by the "
                         "coefficient of the unknown",
                         eq(target, over(plain, _n(a * c, style)))
                         if a != 1 and c != 1 else None),
    }


def _bracket_inside_pool(target, k, diff, trail, c, style) -> dict:
    consts = [cc for cc, s in trail if not s]
    scaled = [(cc * abs(c) if not s else cc, s) for cc, s in trail]
    return {
        "sign": Mis("moved the constant across the equals sign without changing its "
                    "sign", eq(target, _bracket_inside(k, diff, _neg(trail), style))),
        "both_signs": Mis("added the two quantities inside the bracket instead of "
                          "subtracting them",
                          eq(target, _bracket_inside(k, _abs_terms(diff), trail,
                                                     style))),
        "both_signs_sign": Mis("added the two quantities inside the bracket and kept "
                               "the constant's sign as well",
                               eq(target, _bracket_inside(k, _abs_terms(diff),
                                                          _neg(trail), style))),
        "reciprocal": Mis("multiplied by the bracket's coefficient instead of "
                          "dividing by it",
                          eq(target, _bracket_inside(1 / k, diff, trail, style))
                          if abs(k) != 1 else None),
        "const_scaled": Mis("multiplied the constant inside the bracket by the "
                            "bracket's coefficient instead of leaving it alone",
                            eq(target, _bracket_inside(k, diff, scaled, style))
                            if consts and abs(c) != 1 else None),
        "const_scaled_sign": Mis("multiplied the constant inside the bracket by the "
                                 "bracket's coefficient and kept its sign",
                                 eq(target, _bracket_inside(k, diff, _neg(scaled),
                                                            style))
                                 if consts and abs(c) != 1 else None),
    }


def _abs_terms(terms) -> list:
    return [(abs(q(c)), s) for c, s in terms]


# ----------------------------------------- the target is a factor of a product

def isolate_factor(rng: random.Random, seed: int, *, target=None, left=None, k=1,
                   top=None, bottom=None, style="frac", frame=None, story=None,
                   distribute=False, order=None, wrongs=None,
                   difficulty="easy") -> Item:
    """left = k·(top)/(bottom) -- undo a multiplication or a division.

    `left` is the printed side the target is not in: a letter, a letter squared,
    or a letter less a constant. Everything else is a bag of single letters above
    and below the line. `order` fixes the order the letters of a product are
    printed in, which the source varies from option to option.
    """
    if target is None:
        target, left, k, top, bottom = _draw_factor(rng)
    k = q(k)
    top, bottom = list(top or []), list(bottom or [])
    if k == 0 or target not in top + bottom:
        raise ItemError("the target is not a factor of this product")
    if len(set(top + bottom)) != len(top + bottom):
        raise ItemError("a letter appears twice in the product")
    left_text, left_terms, left_vars = _left_side(left, style)
    if target in left_vars:
        raise ItemError("the target appears on both sides")

    rank = _rank(order or ([left_text] + top + bottom))
    equation = eq(left_text, _quotient(k, top, bottom, left_text, left_terms,
                                       style, rank=rank))
    names = []
    for s in left_vars + top + bottom:
        if s not in names:
            names.append(s)
    if len(names) < 2:
        raise ItemError("nothing to express the target in terms of")
    frame = frame or rng.choice(FRAME_NAMES)
    stem = _stem(equation, frame, story, target, _order_vars(equation, names))

    up = target in top
    rest_top = [s for s in top if s != target]
    rest_bot = [s for s in bottom if s != target]
    if up:
        scale, upper, lower = 1 / k, [left_text] + bottom, rest_top
    else:
        scale, upper, lower = k, top, [left_text] + rest_bot
    key = eq(target, _quotient(scale, upper, lower, left_text, left_terms, style,
                               distribute, rank))
    pool = _factor_pool(target, k, left_text, left_terms, top, bottom, up, style,
                        distribute, rank)
    P = {"kind": "nleq_isolate_factor", "target": target,
         "left": _pack(left_terms), "k": _p(k), "top": list(top),
         "bottom": list(bottom), "style": style, "distribute": bool(distribute)}
    rationale = (f"Multiplying both sides of {equation} by whatever divides "
                 f"{target} and dividing by whatever multiplies it gives {key}.")
    return _build("nleq.isolate_factor", difficulty, seed, stem, key, pool, wrongs,
                  rng, rationale, names, P)


def _rank(order) -> dict:
    return {piece: i for i, piece in enumerate(order)}


def _sorted(pieces, rank: dict) -> list:
    return sorted(pieces, key=lambda p: rank.get(p, len(rank)))


def _draw_factor(rng: random.Random):
    pool = list(LETTERS)
    rng.shuffle(pool)
    a, b, c = pool[0], pool[1], pool[2]
    shape = rng.choice(["times", "over", "coef", "coef_over"])
    if shape == "times":
        return b, [(1, a)], Q(1), [b, c], []
    if shape == "over":
        return b, [(1, a)], Q(1), [b], [c]
    if shape == "coef":
        return b, [(1, a)], Q(rng.randint(2, 60)), [b, c], []
    return b, [(1, a)], Q(rng.randint(2, 60)), [b], [c]


def _left_side(left, style):
    """The side the target is not in, as (printed text, terms, letters)."""
    if isinstance(left, tuple) and left and left[0] == "square":
        v = left[1]
        return v + sup(2), [(1, v + sup(2))], [v]
    terms = [(q(c), s) for c, s in left]
    return signed_terms(terms, style), terms, [s for _, s in terms if s]


def _quotient(scale, upper, lower, left_text, left_terms, style,
              distribute=False, rank=None) -> str:
    """A signed coefficient times a product over a product, as the page prints it.

    A coefficient of 1/150 is printed by putting 150 under the line -- the source
    writes −w/(150x), never −(1/150)w/x -- and a bracketed left-hand side is
    multiplied out where the source multiplies it out.
    """
    scale = q(scale)
    rank = rank or {}
    upper = _sorted(upper, rank)
    lower = _sorted(lower, rank)
    if distribute and left_text in upper and len(left_terms) > 1 and not lower:
        others = [u for u in upper if u != left_text]
        return _glue([mono(c * scale, prod(s, *others) if s else prod(*others),
                           style=style) for c, s in left_terms])
    head, low_head = "", ""
    a = abs(scale)
    if a != 1:
        if a.numerator == 1:
            low_head = _n(a.denominator, style)
        elif a.denominator != 1 and style == "frac":
            head = paren(num(a))
        else:
            head = _n(a, style)
    body = over(prod(head, *[_wrap(u) for u in upper]) or "1",
                prod(low_head, *[_wrap(l) for l in lower]) or "1")
    return (MINUS if scale < 0 else "") + body


def _wrap(piece: str) -> str:
    return piece if _simple(piece) else paren(piece)


def _factor_pool(target, k, left_text, left_terms, top, bottom, up, style,
                 distribute, rank) -> dict:
    rest_top = [s for s in top if s != target]
    rest_bot = [s for s in bottom if s != target]
    if up:
        scale, good_up, good_down = 1 / k, [left_text] + bottom, rest_top
        moved = list(bottom)
    else:
        scale, good_up, good_down = k, top, [left_text] + rest_bot
        moved = list(rest_bot)
    others = [s for s in top + bottom if s != target]
    stay = [u for u in good_up if u not in moved]

    def shown(sc, u, d, dist=False):
        return eq(target, _quotient(sc, u, d, left_text, left_terms, style, dist,
                                    rank))

    pool = {
        "invert": Mis("turned the fraction upside down",
                      shown(scale, good_down or ["1"], good_up)),
        "full_invert": Mis("wrote the whole right-hand side upside down",
                           shown(1 / scale, good_down or ["1"], good_up)),
        "divide_instead": Mis("divided by the letter that was dividing the unknown "
                              "instead of multiplying by it",
                              shown(scale, stay, moved) if moved and stay else None),
        "divide_instead_flip": Mis("divided by the letter that was dividing the "
                                   "unknown and then wrote the fraction upside down",
                                   shown(1 / scale, moved, stay)
                                   if moved and stay else None),
        "denom_swap": Mis("left the squared side under the line instead of bringing "
                          "it up",
                          shown(scale, [u for u in good_up if u != left_text] or ["1"],
                                good_down + [left_text])
                          if len(good_up) > 1 else None),
        "left_below": Mis("put the left-hand side under the line and brought the "
                          "other letter up",
                          shown(scale, [u for u in good_up if u != left_text]
                                + good_down, [left_text])
                          if len(good_up) > 1 and good_down else None),
        "keep_coef": Mis("kept the coefficient on the side it started on instead of "
                         "moving it across",
                         shown(1 / scale, good_up, good_down) if abs(k) != 1 else None),
        "product_all": Mis("multiplied every letter together instead of dividing",
                           shown(abs(k) if abs(k) != 1 else 1, [left_text] + others,
                                 [])),
        "sum_all": Mis("added the letters instead of multiplying them",
                       eq(target, signed_terms([(1, left_text)] +
                                               [(1, s) for s in others], style))
                       if others else None),
        "coef_sum": Mis("added the letters, keeping the coefficient against the "
                        "second one",
                        eq(target, signed_terms(
                            [(1, left_text)] + [(1 / abs(k) if i == 0 else 1, s)
                                                for i, s in enumerate(others)], style))
                        if others and abs(k) != 1 else None),
        "difference": Mis("subtracted one letter from the other instead of dividing",
                          eq(target, signed_terms([(1, left_text)] +
                                                  [(-1, s) for s in others], style))
                          if others else None),
        "coef_added": Mis("added the coefficient instead of multiplying by it",
                          eq(target, signed_terms(
                              [(abs(k), "")] + [(1, s) for s in [left_text] + others],
                              style)) if abs(k) != 1 else None),
        "recip_added": Mis("added the coefficient the wrong way up instead of "
                           "multiplying by it",
                           eq(target, signed_terms(
                               [(1 / abs(k), "")] +
                               [(1, s) for s in [left_text] + others], style))
                           if abs(k) != 1 else None),
        "coef_subtracted": Mis("subtracted the coefficient instead of dividing by it",
                               shown(1, [signed_terms([(1, left_text), (-abs(k), "")],
                                                      style)], good_down)
                               if abs(k) != 1 and len(left_terms) == 1 else None),
        "subtract_all": Mis("subtracted both letters from the coefficient instead of "
                            "dividing",
                            eq(target, signed_terms(
                                [(abs(k), "")] + [(-1, s) for s in
                                                  [left_text] + others], style))
                            if abs(k) != 1 else None),
        "sign": Mis("dropped the minus sign in front of the fraction",
                    shown(-scale, good_up, good_down) if k < 0 else None),
    }
    if distribute:
        extra = [u for u in good_up if u != left_text]
        partial = _partial(scale, left_terms, extra, style)
        pool["no_distribute"] = Mis(
            "divided by the letter instead of multiplying by it",
            shown(scale, [left_text], good_down + extra))
        pool["partial"] = Mis("multiplied only the first term inside the bracket",
                              eq(target, partial))
        pool["partial_over"] = Mis("multiplied only the first term and then divided "
                                   "the whole thing by the letter again",
                                   eq(target, over(partial, prod(*extra))))
    return pool


def _partial(scale, left_terms, others, style) -> str:
    parts = []
    for i, (c, s) in enumerate(left_terms):
        if i == 0:
            parts.append(mono(c * q(scale), prod(s, *others) if s else prod(*others),
                              style=style))
        else:
            parts.append(mono(c, s, style=style))
    return _glue(parts)


# --------------------------------------- the target sits under the line

def isolate_denominator(rng: random.Random, seed: int, *, target=None, left=None,
                        head=0, top=None, sigma=1, const=0, combine=False,
                        style="frac", frame=None, story=None, wrongs=None,
                        difficulty="medium") -> Item:
    """left = head + top/(σ·target + const) -- the unknown is a denominator.

    Clearing it takes two reciprocals, and the options are the places a student
    stops: after one of them, or having inverted the wrong side.
    """
    if target is None:
        target, left, head, top, sigma, const = _draw_denominator(rng)
    head, sigma, const = q(head), q(sigma), q(const)
    if sigma == 0:
        raise ItemError("the unknown has vanished from the denominator")
    left_text, left_terms, left_vars = _left_side(left, style)
    top_c, top_s = q(top[0]), top[1]
    if target in left_vars or top_s == target or top_c == 0:
        raise ItemError("the target appears twice")

    den = signed_terms(_positive_first([(sigma, target), (const, "")]), style)
    ratio_in = over(mono(top_c, top_s, style=style), den)
    rhs = _glue(([mono(head, "", style=style)] if head else []) + [ratio_in])
    equation = eq(left_text, rhs)
    names = []
    for s in left_vars + ([top_s] if top_s else []) + [target]:
        if s and s not in names:
            names.append(s)
    if len(names) < 2:
        raise ItemError("nothing to express the target in terms of")
    frame = frame or rng.choice(FRAME_NAMES)
    stem = _stem(equation, frame, story, target, _order_vars(equation, names))

    base_terms = left_terms + [(-head, "")]
    base = signed_terms(base_terms, style)
    trail = -const / sigma
    ratio = over(mono(top_c / sigma, top_s, style=style), base)
    if combine:
        if top_s or trail == 0:
            raise ItemError("this shape cannot be gathered into one fraction")
        gathered = _collect(_scaled(base_terms, trail) + [(top_c / sigma, "")])
        key_expr = over(signed_terms(gathered, style), base)
    else:
        key_expr = _lead_positive(ratio, trail, style)
    key = eq(target, key_expr)
    pool = _den_pool(target, left_terms, head, top_c, top_s, sigma, style, ratio,
                     trail, base)
    P = {"kind": "nleq_isolate_denominator", "target": target,
         "left": _pack(left_terms), "head": _p(head),
         "top": [_p(top_c), top_s or ""], "sigma": _p(sigma), "const": _p(const),
         "combine": bool(combine), "style": style}
    rationale = (f"Taking the reciprocal of both sides of {equation}, once the "
                 f"constant is out of the way, gives {key}.")
    return _build("nleq.isolate_denominator", difficulty, seed, stem, key, pool,
                  wrongs, rng, rationale, names, P)


def _collect(terms) -> list:
    """Gather like terms, keeping the order they were first written in."""
    order, bag = [], {}
    for c, s in terms:
        if s not in bag:
            order.append(s)
            bag[s] = Q(0)
        bag[s] += q(c)
    return [(bag[s], s) for s in order if bag[s] != 0]


def _lead_positive(ratio: str, trail, style: str) -> str:
    """`1 − V_P/V_B`, not `−V_P/V_B + 1`: a line does not open with a minus."""
    trail = q(trail)
    if trail == 0:
        return ratio
    piece = mono(trail, "", style=style)
    if ratio.startswith((MINUS, "-")) and trail > 0:
        return _glue([piece, MINUS + ratio[1:]]).replace(f"+ {MINUS}", MINUS)
    return _glue([ratio, piece])


def _draw_denominator(rng: random.Random):
    pool = list(LETTERS)
    rng.shuffle(pool)
    t, a = pool[0], pool[1]
    head = rng.choice([0, 0, rng.randint(2, 20)])
    return t, [(1, a)], head, (rng.randint(2, 40), ""), Q(1), Q(0)


def _den_pool(target, left_terms, head, top_c, top_s, sigma, style, ratio, trail,
              base) -> dict:
    top_text = mono(top_c, top_s, style=style)
    lvar = next((s for _, s in left_terms if s), None)
    lconst = next((c for c, s in left_terms if not s), Q(0))
    left_plain = signed_terms(left_terms, style)
    return {
        "invert": Mis("turned the fraction upside down at the last step",
                      eq(target, over(base, top_text))),
        "split": Mis("divided each term on the left by the numerator separately, "
                     "keeping the constant's sign",
                     eq(target, _glue([over(left_plain, top_text),
                                       mono(head, "", style=style)]))
                     if head else None),
        "split_minus": Mis("divided each term on the left by the numerator and "
                           "subtracted the constant as well",
                           eq(target, _glue([over(left_plain, top_text),
                                             mono(-head, "", style=style)]))
                           if head else None),
        "flip_ratio_plus": Mis("wrote the ratio upside down and added the constant "
                               "instead of subtracting it",
                               eq(target, _glue([mono(trail, "", style=style),
                                                 over(base, top_text)]))
                               if trail else None),
        "difference": Mis("subtracted the two given quantities instead of dividing "
                          "them",
                          eq(target, signed_terms(left_terms + [(-1, top_s)], style))
                          if top_s else None),
        "unit_numerator": Mis("cleared the numerator instead of dividing by it",
                              eq(target, over("1", base)) if abs(top_c) != 1 else None),
        "reciprocal_only": Mis("took the reciprocal of the left-hand letter and "
                               "stopped there",
                               eq(target, over("1", lvar)) if lvar else None),
        "mixed_combine": Mis("gathered the two terms over the left-hand letter alone "
                             "and added the two constants",
                             eq(target, over(signed_terms(
                                 [(trail, lvar), (top_c / sigma - lconst, "")],
                                 style), lvar))
                             if lvar and trail and lconst else None),
        "sign": Mis("moved the constant out of the denominator without changing its "
                    "sign",
                    eq(target, _lead_positive(ratio, -trail, style))
                    if trail else None),
    }


# ------------------------------------------------------------ params packing

def _p(v) -> list:
    v = q(v)
    return [v.numerator, v.denominator]


def _pack(terms) -> list:
    return [[_p(c), s or ""] for c, s in terms]


# ------------------------------------ the same relation, divided through

def scale_relation(rng: random.Random, seed: int, *, a=None, b=None, c=None, g=None,
                   op=">", vx="x", vy="y", frame="above", wrongs=None,
                   difficulty="easy") -> Item:
    """a·x − b·y > c, divided through by the factor all three share.

    Nothing is solved; the whole item is whether the divisor reaches every term.
    The wrong options are the three ways it does not: each term divided by its own
    coefficient, the two coefficients exchanged, and the sides written the other
    way round with the constant still divided by the first coefficient.
    """
    a = Q(rng.choice([2, 3, 4, 6, 8, 9, 10, 12, 15, 16, 18, 20])) if a is None else q(a)
    b = Q(rng.choice([2, 3, 4, 6, 8, 9, 10, 12, 15, 16, 18, 20])) if b is None else q(b)
    c = Q(rng.choice([i for i in range(-40, 41) if i])) if c is None else q(c)
    if a.denominator != 1 or b.denominator != 1 or c.denominator != 1:
        raise ItemError("this item is printed with whole-number coefficients")
    g = Q(math.gcd(math.gcd(int(a), int(b)), int(c))) if g is None else q(g)
    if g <= 1:
        raise ItemError("the three numbers share no factor to divide out")
    if a == b:
        raise ItemError("the two coefficients would be indistinguishable")

    printed = f"{signed_terms([(a, vx), (-b, vy)])} {op} {num(c)}"
    stem = displayed(printed,
                     "Which of the following inequalities is equivalent to the "
                     "inequality above?" if frame == "above" else
                     "Which inequality is equivalent to the given inequality?")
    key = f"{signed_terms([(a / g, vx), (-b / g, vy)])} {op} {num(c / g)}"
    pool = {
        "divide_each": Mis("divided each term by its own coefficient instead of by "
                           "the factor all three share",
                           f"{signed_terms([(1, vx), (-1, vy)])} {op} {num(c / a)}"),
        "swap_coefs": Mis("divided correctly but then exchanged the two "
                          "coefficients",
                          f"{signed_terms([(b / g, vx), (-a / g, vy)])} {op} "
                          f"{num(c / g)}"),
        "reverse_terms": Mis("wrote the two terms the other way round and divided "
                             "the constant by the first coefficient",
                             f"{signed_terms([(b / g, vy), (-a / g, vx)])} {op} "
                             f"{num(c / a)}"),
        "half_divide": Mis("divided the two coefficients but left the constant "
                           "alone",
                           f"{signed_terms([(a / g, vx), (-b / g, vy)])} {op} "
                           f"{num(c)}"),
        "constant_only": Mis("divided the constant but left the two coefficients "
                             "alone",
                             f"{signed_terms([(a, vx), (-b, vy)])} {op} "
                             f"{num(c / g)}"),
    }
    P = {"kind": "nleq_scale_relation", "a": _p(a), "b": _p(b), "c": _p(c),
         "g": _p(g), "op": op, "vx": vx, "vy": vy}
    rationale = sent(f"Every term of {printed} is a multiple of {num(g)}, and "
                     f"dividing a strict inequality by a positive number leaves it "
                     f"pointing the same way, so it is {key}.")
    ch, why, letter = text_choices(key, pick(pool, wrongs), rng, check=False)
    return Item("nleq.scale_relation", "dividing a relation through", difficulty,
                seed, sent(stem), "mcq", E(1), letter, sent(rationale), ch, why,
                list(ch), params=dict(P, options=list(ch)))
