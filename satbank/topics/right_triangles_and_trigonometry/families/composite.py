"""Figures made of two right triangles, where one shares its angles with the other.

An altitude dropped to a base, and a line drawn parallel to a leg, both cut a
right triangle into two that are similar to it. The figure is the question in
all three of these, so every one of them is drawn from the same numbers as the
stem -- change a length and the picture changes with it.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction as Q

from ....exact import E, Exact
from ....item import Item, ItemError, Mis, assemble, gridin_mistakes
from ..figures import altitude_triangle, cut_right_triangle
from ..kit import TRIPLES, pick, ratio_text

__all__ = ["altitude_special", "nested_similar", "parallel_similar"]

TAN = {30: E(Q(1, 3), 0, 3), 45: E(1), 60: E(1, 0, 3)}
SIN = {30: E(Q(1, 2)), 45: E(Q(1, 2), 0, 2), 60: E(Q(1, 2), 0, 3)}
COS = {30: E(Q(1, 2), 0, 3), 45: E(Q(1, 2), 0, 2), 60: E(Q(1, 2))}
TRIOS = (("A", "B", "C"), ("P", "Q", "R"), ("X", "Y", "Z"), ("J", "K", "L"),
         ("R", "S", "T"), ("D", "E", "F"))
FEET = "DEFGHMNW"


# =============================================== an altitude and two special angles

def altitude_special(rng: random.Random, seed: int, *, alpha=None, gamma=None,
                     side=None, ask=None, names=None, foot=None, fmt=None,
                     note=False, wrongs=None) -> Item:
    """A triangle cut by its altitude into two special right triangles.

    `alpha` is the angle the altitude makes with the left-hand side at the
    apex, `gamma` the angle at the right-hand base vertex, and `side` the
    length of the right-hand side, so both halves are 30-60-90 or 45-45-90 and
    every length stays exact.
    """
    alpha = alpha or rng.choice([30, 45, 60])
    gamma = gamma or rng.choice([30, 45, 60])
    bc = E(side if side is not None else rng.randint(2, 40))
    trio = names or rng.choice(TRIOS)
    A, B, C = trio
    D = foot or next(c for c in FEET if c not in trio)

    bd = bc * SIN[gamma]                      # the altitude
    dc = bc * COS[gamma]
    ad = bd * TAN[alpha]
    ab = bd / COS[alpha]
    lengths = {"ad": ad, "dc": dc, "bd": bd, "ab": ab, "bc": bc}
    ask = ask or rng.choice(["ad", "bd", "dc", "ab"])
    key = lengths[ask]
    if ask == "bc":
        raise ItemError("the stem would be asking for the number it states")
    if not 0.2 <= float(ad) / float(dc) <= 5.0:
        raise ItemError("the altitude falls too far off centre to draw")
    if float(key) == float(bc):
        # when alpha and gamma are complementary the triangle is isosceles, and
        # the side asked for is the side the figure already prints
        raise ItemError("the answer is a number the figure already states")

    seg = {"ad": A + D, "dc": D + C, "bd": B + D, "ab": A + B, "bc": B + C}
    fig = altitude_triangle(float(ad), float(dc), float(bd),
                            names={"a": A, "b": B, "c": C, "d": D},
                            sides={"bc": bc.plain()},
                            angles={"abd": f"{alpha}°", "c": f"{gamma}°"}, note=note)
    stem = rng.choice([
        f"In triangle {A}{B}{C} above, what is the length of {seg[ask]} ?",
        f"In the figure above, what is the length of {seg[ask]} ?",
    ])
    pool = {
        "altitude": Mis(f"gave the altitude {B}{D} instead of the segment asked for",
                        bd),
        "ratio_one_two_three": Mis("used 1 : 2 : 3 for the 30-60-90 side ratios instead "
                                   "of 1 : √3 : 2", bc / E(3)),
        "forty_five": Mis("used the 45-45-90 ratio in place of the ratios the marked "
                          "angles give", bc * E(Q(1, 2), 0, 2)),
        "other_piece": Mis(f"gave the other piece of the base", dc if ask == "ad" else ad),
        "given": Mis(f"gave {seg['bc']}, which the stem states", bc),
        "half_given": Mis("halved the given side", bc / E(2)),
        "hypotenuse": Mis(f"gave {seg['ab']} instead of the segment asked for", ab),
    }
    rationale = (f"The altitude makes two right triangles, and {B}{D} = "
                 f"{bc.plain()}·sin {gamma}° = {bd.plain()}."
                 + ("" if ask == "bd" else
                    f" With the {alpha}° angle at {B}, {seg[ask]} = {key.plain()}."))
    P = {"kind": "rtt_altitude_special", "alpha": alpha, "gamma": gamma,
         "side": float(bc), "ask": ask}
    fmt = fmt or ("spr" if rng.random() < 0.3 else "mcq")
    mistakes = [m for m in pick(pool, wrongs) if m.value is not None]
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("a radical cannot be entered in a grid-in")
        return Item("rtt.altitude_special", "altitudes and special triangles", "medium",
                    seed, stem, "spr", key, key.gridin(), rationale, figure=fig,
                    params=P, spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("rtt.altitude_special", "altitudes and special triangles", "medium",
                seed, stem, "mcq", key, letter, rationale, choices, reasons, latex,
                figure=fig, params=P)


# ============================ a line parallel to a leg, cutting off the top

def nested_similar(rng: random.Random, seed: int, *, triple=None, scale=None, cut=None,
                   ask=None, names=None, foot=None, edge=None, fmt=None, note=False,
                   wrongs=None) -> Item:
    """A right triangle with a smaller similar triangle cut off at the apex.

    `tan B` and the hypotenuse fix the big triangle; the distance from the
    right angle to the cut fixes the small one.
    """
    u, v, w = triple or rng.choice(TRIPLES)
    t = int(scale if scale is not None else rng.randint(1, 12))
    trio = names or rng.choice(TRIOS)
    A, B, C = trio                       # right angle at A, B at the top
    spare = [c for c in FEET if c not in trio]
    D = foot or spare[0]
    Ed = edge or spare[1]

    ac, ab, bc = E(u * t), E(v * t), E(w * t)      # AC opposite B, AB adjacent
    da = E(cut if cut is not None else rng.randint(1, max(1, v * t - 1)))
    # the cut is kept clear of both ends: a segment drawn almost on top of a
    # vertex gives a figure whose labels cannot be told apart by eye
    if not 0.25 <= float(da) / float(ab) <= 0.75:
        raise ItemError("the cut falls too close to an end of the leg")
    share = (ab - da) / ab
    lengths = {"de": ac * share, "bd": ab - da, "be": bc * share, "da": da,
               "ac": ac, "ab": ab, "bc": bc}
    ask = ask or rng.choice(["de", "bd", "be", "ac"])
    key = lengths[ask]
    # a busy figure needs a rounder triangle: five lettered points and a cut
    # have to stay far enough apart to be read off the page
    if not 0.25 <= float(ac) / float(ab) <= 4.0:
        raise ItemError("a triangle this shape cannot carry five labelled points")

    fig = cut_right_triangle(float(ab), float(ac), float(da), parallel="q",
                             layout="left",
                             names={"rt": A, "p": B, "q": C, "foot": D, "edge": Ed},
                             note=note)
    seg = {"de": D + Ed, "bd": B + D, "be": B + Ed, "ac": A + C}
    stem = rng.choice([
        f"In the figure above, tan {B} = {ratio_text(u, v)}. If {B}{C} = {bc.plain()} "
        f"and {D}{A} = {da.plain()}, what is the length of {seg[ask]} ?",
        f"In the figure shown, tan {B} = {ratio_text(u, v)}, {B}{C} = {bc.plain()} and "
        f"{D}{A} = {da.plain()}. What is the length of {seg[ask]} ?",
    ])
    pool = {
        "whole_leg": Mis(f"gave {A}{C}, the corresponding side of the whole triangle, "
                         "without scaling it down", ac),
        "wrong_share": Mis("scaled by the part cut off instead of the part left",
                           ac * da / ab),
        "given": Mis("gave a length the stem states", da),
        "hypotenuse": Mis(f"gave {B}{Ed} instead of the segment asked for",
                          bc * share if ask != "be" else ab - da),
        "unscaled_hyp": Mis(f"gave {B}{C}, the whole hypotenuse", bc),
        "difference": Mis("subtracted the cut from the wrong side", ac - da
                          if float(ac) > float(da) else None),
    }
    rationale = (f"tan {B} = {ratio_text(u, v)} with {B}{C} = {bc.plain()} gives "
                 f"{A}{C} = {ac.plain()} and {A}{B} = {ab.plain()}. Triangle "
                 f"{B}{D}{Ed} is similar to triangle {B}{A}{C} in the ratio "
                 f"{(ab - da).plain()} : {ab.plain()}, so {seg[ask]} = {key.plain()}.")
    P = {"kind": "rtt_nested_similar", "u": u, "v": v, "w": w, "t": t,
         "cut": float(da), "ask": ask}
    fmt = fmt or ("spr" if rng.random() < 0.4 else "mcq")
    mistakes = [m for m in pick(pool, wrongs) if m.value is not None]
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("a radical cannot be entered in a grid-in")
        return Item("rtt.nested_similar", "similar right triangles", "hard", seed, stem,
                    "spr", key, key.gridin(), rationale, figure=fig, params=P,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("rtt.nested_similar", "similar right triangles", "hard", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex, figure=fig,
                params=P)


# ============================== a segment parallel to a leg, near the far corner

def parallel_similar(rng: random.Random, seed: int, *, base=None, height=None,
                     factor=None, ask=None, names=None, foot=None, edge=None,
                     fmt=None, note=False, wrongs=None) -> Item:
    """Two nested right triangles, one parallel segment, one scale factor.

    The small triangle's legs are a Pythagorean pair so its hypotenuse is
    whole, and the factor says how much bigger the containing triangle is.
    """
    m = int(base if base is not None else rng.randint(2, 40))
    n = int(height if height is not None else rng.randint(2, 40))
    d2 = m * m + n * n
    d = math.isqrt(d2)
    if d * d != d2:
        raise ItemError("the small triangle's hypotenuse is not a whole number")
    k = Q(factor if factor is not None else rng.randint(2, 3))
    if not 2 <= k <= 3:
        raise ItemError("the cut falls too close to an end of the leg")
    trio = names or rng.choice(TRIOS)
    C, A, Ev = trio                       # right angle at A, C at the far corner
    spare = [c for c in FEET if c not in trio]
    B = foot or spare[0]
    Dp = edge or spare[1]

    cb, bd, cd = E(m), E(n), E(d)
    ca, ae, ce = E(k) * cb, E(k) * bd, E(k) * cd
    lengths = {"ce": ce, "ca": ca, "cd": cd, "ae": ae, "ab": ca - cb, "de": ce - cd}
    ask = ask or rng.choice(["ce", "ca", "cd", "ab"])
    key = lengths[ask]
    if not 0.4 <= float(ae) / float(ca) <= 2.5:
        raise ItemError("a triangle this shape cannot carry three labelled lengths")

    fig = cut_right_triangle(float(ae), float(ca), float(ca - cb), parallel="p",
                             layout="right",
                             names={"rt": A, "p": Ev, "q": C, "foot": B, "edge": Dp},
                             sides={"p": ae.plain(), "cut": bd.plain(),
                                    "upper": cb.plain()}, note=note)
    seg = {"ce": C + Ev, "ca": C + A, "cd": C + Dp, "ae": A + Ev, "ab": A + B,
           "de": Dp + Ev}
    stem = rng.choice([
        f"In the figure above, {B}{Dp} is parallel to {A}{Ev}. What is the length of "
        f"{seg[ask]} ?",
        f"In the figure shown, {B}{Dp} is parallel to {A}{Ev}. What is the length of "
        f"{seg[ask]} ?",
    ])
    pool = {
        "small": Mis(f"gave {C}{Dp}, the corresponding side of the small triangle, "
                     "without scaling it up", cd),
        "added": Mis("added the two given lengths instead of scaling", cb + bd),
        "scale": Mis("stopped at the scale factor", E(k) if k > 1 else None),
        "wrong_side": Mis(f"scaled the wrong side of the small triangle", E(k) * bd),
        "sum_scaled": Mis("added the scale factor instead of multiplying by it",
                          cd + E(k)),
        "difference": Mis("used the difference of the two parallel segments as the "
                          "scale", ae - bd),
    }
    rationale = (f"{B}{Dp} is parallel to {A}{Ev}, so triangle {C}{B}{Dp} is "
                 f"similar to triangle {C}{A}{Ev}, and its legs {cb.plain()} and "
                 f"{bd.plain()} give {C}{Dp} = {cd.plain()}."
                 + ("" if ask == "cd" else
                    f" The scale {ae.plain()} ÷ {bd.plain()} = {E(k).plain()} then "
                    f"gives {seg[ask]} = {key.plain()}."))
    P = {"kind": "rtt_parallel_similar", "m": m, "n": n, "k": [k.numerator,
                                                               k.denominator],
         "ask": ask}
    fmt = fmt or ("spr" if rng.random() < 0.4 else "mcq")
    mistakes = [m_ for m_ in pick(pool, wrongs) if m_.value is not None]
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("a radical cannot be entered in a grid-in")
        return Item("rtt.parallel_similar", "similar right triangles", "hard", seed,
                    stem, "spr", key, key.gridin(), rationale, figure=fig, params=P,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("rtt.parallel_similar", "similar right triangles", "hard", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex, figure=fig,
                params=P)
