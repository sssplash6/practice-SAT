"""The angles inside one triangle, and the ones just outside it.

Everything here rests on the same two facts -- the three angles of a triangle
sum to a straight angle, and the two angles opposite equal sides are equal --
but the source set asks for them in eight different frames, and the frame is
most of what makes an item easy or hard. A bare "two angles are 24 and 98" is
the easy tier; the same fact reached through an isosceles triangle whose apex
is a vertical angle is the hard tier.

Each template draws its own figure from the angles it has just computed, so
the picture is never a stale copy: change 67 to 68 in the stem and the apex of
the drawn triangle moves with it.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction

from ....exact import E
from ....item import Item, ItemError, Mis, assemble, gridin_mistakes
from ..figures import Fig, P, direction, meet, polar, ray, triangle_pts
from ..kit import deg, pick, plain, whole

__all__ = ["triangle_sum", "isosceles", "isosceles_possible", "angle_algebra",
           "exterior_angle", "isosceles_cross", "vertical_isosceles",
           "crossing_triangles"]

TRIOS = [("A", "B", "C"), ("X", "Y", "Z"), ("J", "K", "L"), ("P", "Q", "R"),
         ("R", "S", "T"), ("D", "E", "F"), ("L", "M", "N"), ("W", "X", "Y")]

# The source set closes a grid-in that answers in degrees with "(Disregard the
# degree symbol when entering your answer.)". The engine's shared prose check
# refuses any stem that ends in a bracket, so no topic prints it; the note is
# a convention of the answer sheet rather than part of the question.
NOTES = {None: "", "": "", "enter": "", "grid": ""}


def cosd(d):
    return math.cos(math.radians(d))


def sind(d):
    return math.sin(math.radians(d))


def finish(name, skill, tier, seed, stem, key, mistakes, rng, rationale, *,
           unit=False, figure=None, params=None, fmt="mcq", shown=None):
    """Every template in this file ends the same way, so it is written once."""
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("this answer cannot be entered in a grid-in")
        return Item(name, skill, tier, seed, stem, "spr", key, key.gridin(),
                    rationale, figure=figure, params=params,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    shown = shown or (deg if unit else plain)
    choices, latex, reasons, letter = assemble(key, mistakes, rng, fmt_value=shown)
    return Item(name, skill, tier, seed, stem, "mcq", key, letter, rationale,
                choices, reasons, latex, figure=figure, params=params)


# ============================================================ the angle sum

SUM_FRAMES = ("plain", "equal", "right", "right_figure", "congruent")


def triangle_sum(rng: random.Random, seed: int, *, frame=None, a=None, b=None,
                 names=None, partner=None, ask=None, style=None, fmt=None,
                 unit=None, note=None, wrongs=None) -> Item:
    """Two of a triangle's angles are known; the third is what is left of 180.

    The five frames are the five ways the source set asks it: named vertices,
    a pair of equal angles, a right triangle with one acute angle, the same
    right triangle drawn, and a congruent partner that carries the answer
    across to a differently named vertex.
    """
    frame = frame or rng.choice(SUM_FRAMES)
    names = tuple(names or rng.choice(TRIOS))
    style = style or rng.choice(["word", "symbol"])
    right = frame in ("right", "right_figure", "congruent")

    if frame == "equal":
        a = a or rng.randrange(20, 86)
        b = a
    elif right:
        a = a or rng.randrange(8, 83)
        b = 90
    else:
        a = a or rng.randrange(15, 121)
        b = b or rng.randrange(15, 121)
    if a <= 0 or b <= 0 or a + b >= 180:
        raise ItemError("two angles that leave nothing for the third")
    third = 180 - a - b
    key = E(third)
    ask = 0 if ask is None else ask
    rest = [i for i in range(3) if i != ask]

    pool = {
        "sum": Mis("added the two given measures instead of subtracting them from "
                   "180 degrees", whole(a + b)),
        "diff": Mis("subtracted one given measure from the other", whole(abs(a - b))),
        "full": Mis("used 360 degrees for the angle sum of a triangle",
                    whole(360 - a - b)),
        "sum_right": Mis("added a right angle to the two given measures",
                         whole(a + b + 90)),
        "right_rest": Mis("used 90 degrees for the angle sum instead of 180",
                          whole(90 - a - b)),
        "same": Mis("gave back the acute angle the question supplies", whole(a)),
        "right": Mis("gave the right angle rather than the remaining acute angle",
                     whole(90) if right else None),
        # 90 - a done by hand: borrowing a ten for the ones column and leaving
        # the tens digit at 9 lands exactly 10 high, and only when there is a
        # ones digit to borrow for
        "hundred": Mis(f"borrowed a ten to subtract {a} from 90 but left the tens "
                       "digit at 9",
                       whole(100 - a) if right and a % 10 else None),
        # the two acute angles sit either side of 45: a is a - 45 above it, so
        # the other is that far below. Stopping at the difference lands on
        # a - 45 (College Board printed 6 beside 51 in source 1.12). Kept out of
        # the default order; only 1.12 asks for it.
        "iso45": Mis(f"found how far {a}° is from 45° and stopped, instead of "
                     "taking that difference off the other 45°",
                     whole(a - 45) if right and a > 45 else None),
        "one_only": Mis("subtracted only one of the two given measures from 180 "
                        "degrees", whole(180 - a)),
        "other_only": Mis("subtracted only the other given measure from 180 "
                          "degrees", whole(180 - b)),
    }
    order = ["sum", "diff", "full", "right_rest", "one_only", "other_only",
             "sum_right"]
    if right:
        order = ["same", "right", "sum", "hundred", "one_only"]

    ang = "∠" if style == "symbol" else "angle "
    tri = "△" if style == "symbol" else "triangle "
    fmt = fmt or ("spr" if frame in ("equal", "congruent") else "mcq")
    tail = NOTES[note] if fmt == "spr" else ""
    fig = None

    if frame == "plain":
        stem = (f"In {tri}{''.join(names)}, the measure of {ang}{names[rest[0]]} is "
                f"{a}° and the measure of {ang}{names[rest[1]]} is {b}°. "
                f"What is the measure of {ang}{names[ask]}?")
        skill, tier = "the angle sum of a triangle", "easy"
    elif frame == "equal":
        stem = (f"In {tri}{''.join(names)}, the measures of {ang}{names[rest[0]]} and "
                f"{ang}{names[rest[1]]} are each {a}°. What is the measure of "
                f"{ang}{names[ask]}, in degrees?{tail}")
        skill, tier = "an isosceles triangle's angle sum", "medium"
    elif frame == "right":
        stem = (f"In a right triangle, the measure of one of the acute angles is "
                f"{a}°. What is the measure, in degrees, of the other acute "
                f"angle?{tail}")
        skill, tier = "the acute angles of a right triangle", "easy"
    elif frame == "congruent":
        d, e, f = tuple(partner or rng.choice([t for t in TRIOS if t != names]))
        stem = (f"Triangles {''.join(names)} and {d}{e}{f} are congruent, where "
                f"{names[0]} corresponds to {d}, and {names[1]} and {e} are right "
                f"angles. The measure of angle {names[0]} is {a}°. What is the "
                f"measure, in degrees, of angle {f}?{tail}")
        skill, tier = "congruent triangles", "medium"
    else:
        corner, foot, top = triangle_pts(90, third, 1.0)
        fig = (Fig().path(corner, foot, top, corner)
               .right(corner, foot, top)
               .angle(top, corner, foot, f"{a}°", italic=False)
               .angle(foot, top, corner, "a°").render())
        stem = "In the right triangle shown, what is the value of a?"
        skill, tier = "the acute angles of a right triangle", "easy"

    if unit is None:
        unit = frame in ("plain", "equal")
    rationale = (f"The three angles sum to 180°, so the remaining angle measures "
                 f"180 − {a} − {b} = {third} degrees.")
    params = {"kind": "lat_triangle_sum", "a": a, "b": b, "frame": frame}
    return finish("lat.triangle_sum", skill, tier, seed, stem, key,
                  pick(pool, order, wrongs), rng, rationale, unit=unit,
                  figure=fig, params=params, fmt=fmt)


# ======================================================= isosceles triangles

def isosceles(rng: random.Random, seed: int, *, mode=None, base=None, ext=None,
              names=None, point=None, fmt="mcq", unit=False, wrongs=None) -> Item:
    """An isosceles triangle with one angle given and the apex asked for.

    `mode="base"` gives a base angle outright; `mode="exterior"` gives the
    angle outside the triangle at one base vertex, which is the same fact one
    subtraction further back.
    """
    mode = mode or rng.choice(["base", "exterior"])
    names = tuple(names or rng.choice([("A", "B", "C"), ("P", "Q", "R"),
                                       ("J", "K", "L"), ("X", "Y", "Z")]))
    A, B, C = names
    D = point or rng.choice([d for d in "DEFGMNST" if d not in names])

    if mode == "exterior":
        ext = ext or rng.randrange(95, 176)
        base = 180 - ext
    else:
        base = base or rng.randrange(25, 89)
        ext = 180 - base
    apex = 180 - 2 * base
    if apex <= 0 or base <= 0:
        raise ItemError("these base angles leave nothing for the apex")
    key = E(apex)

    pool = {
        "base_itself": Mis(f"gave the measure of angle {A}{B}{C} rather than the "
                           "apex angle", whole(base)),
        "supplement": Mis("took the supplement of the base angle", whole(180 - base)),
        "double": Mis("doubled the base angle instead of subtracting twice the base "
                      "angle from 180 degrees", whole(2 * base)),
        "half_supp": Mis("halved the supplement of the base angle",
                         whole(Fraction(180 - base, 2))),
        "complement": Mis("took the complement of the base angle", whole(90 - base)),
        "ext_itself": Mis("gave the exterior angle rather than the angle asked for",
                          whole(ext)),
        "base": Mis("stopped at the base angle of the triangle", whole(base)),
        "half_ext": Mis("halved the exterior angle", whole(Fraction(ext, 2))),
        "ext_rest": Mis("subtracted the exterior angle from 180 degrees once "
                        "instead of twice", whole(180 - ext)),
    }
    order = (["ext_itself", "base", "half_ext", "supplement", "double"]
             if mode == "exterior" else
             ["supplement", "base_itself", "double", "half_supp", "complement"])

    left, right, top = triangle_pts(base, base, 1.0)
    fig = Fig().path(left, right).path(left, top, right)
    fig.name(top, A, 90).name(left, B, 215).name(right, C, 325)
    if mode == "exterior":
        d_pt = polar(right, 0, 0.45)
        fig.seg(right, d_pt).name(d_pt, D, 315)
        fig.angle(right, top, d_pt, f"{ext}°", italic=False)
        fig.angle(top, left, right, "x°")
        stem = (f"In the given figure, {A}{C} extends to point {D}. If the measure of "
                f"∠{B}{A}{C} is equal to the measure of ∠{B}{C}{A}, what is "
                f"the value of x ?")
        rationale = (f"∠{B}{C}{A} = 180 − {ext} = {base}°, and "
                     f"∠{B}{A}{C} matches it, so x = 180 − 2({base}) = "
                     f"{apex}.")
        skill = "an exterior angle of an isosceles triangle"
    else:
        fig.angle(top, left, right, "x°")
        stem = (f"In the given triangle, {A}{B} = {A}{C} and ∠{A}{B}{C} has a "
                f"measure of {base}°. What is the value of x ?")
        rationale = (f"{A}{B} = {A}{C} makes ∠{A}{C}{B} equal to ∠{A}{B}{C}, "
                     f"so x = 180 − 2({base}) = {apex}.")
        skill = "the base angles of an isosceles triangle"
    params = {"kind": "lat_isosceles", "mode": mode, "base": base, "ext": ext}
    return finish("lat.isosceles", skill, "easy", seed, stem, key,
                  pick(pool, order, wrongs), rng, rationale, unit=unit,
                  figure=fig.render(), params=params, fmt=fmt)


def isosceles_possible(rng: random.Random, seed: int, *, a=None, names=None,
                       unit=True, wrongs=None) -> Item:
    """One angle of an isosceles triangle is known; which measure is impossible?

    A given angle leaves exactly three shapes -- it is one of the equal pair
    with the asked angle, it is the vertex angle, or the asked angle is the
    vertex angle -- so every measure outside those three is impossible, and
    the three that are possible are the item's distractors.
    """
    a = a or rng.randrange(20, 89)
    names = tuple(names or rng.choice(TRIOS))
    A, B, _ = names
    if (180 - a) % 2:
        raise ItemError("this angle does not split the rest of the triangle evenly")
    apex_here = Fraction(180 - a, 2)
    other = 180 - 2 * a
    reachable = {Fraction(a), apex_here, Fraction(other)}
    if len(reachable) != 3 or any(not (0 < v < 180) for v in reachable):
        raise ItemError("the three isosceles shapes are not three distinct angles")
    key_v = 2 * a
    if Fraction(key_v) in reachable or not 0 < key_v < 180:
        raise ItemError("the value picked for the key is in fact a possible measure")
    key = E(key_v)
    pool = {
        "same_pair": Mis(f"possible: angles {A} and {B} are the pair of equal angles",
                         whole(a)),
        "given_apex": Mis(f"possible: angle {A} is the vertex angle, so angle {B} is "
                          "one of the two base angles", whole(apex_here)),
        "asked_apex": Mis(f"possible: angle {B} is the vertex angle and the other two "
                          "angles are equal", whole(other)),
    }
    order = ["same_pair", "given_apex", "asked_apex"]
    stem = (f"In triangle {''.join(names)}, the measure of angle {A} is {a}°. If "
            f"triangle {''.join(names)} is isosceles, which of the following is NOT a "
            f"possible measure of angle {B} ?")
    rationale = (f"An isosceles triangle with a {a}° angle has angle {B} equal to "
                 f"{a}°, {plain(apex_here)}° or {other}°, so "
                 f"{key_v}° is the one that cannot happen.")
    params = {"kind": "lat_isosceles_possible", "a": a}
    return finish("lat.isosceles_possible", "isosceles triangles", "medium", seed,
                  stem, key, pick(pool, order, wrongs), rng, rationale, unit=unit,
                  params=params)


# =================================================== an angle written with x

def angle_algebra(rng: random.Random, seed: int, *, c=None, mult=None, a=None,
                  fmt="mcq", unit=False, wrongs=None) -> Item:
    """One angle of the triangle is a multiple of the unknown, so 180 is an equation.

    The whole difficulty is the last step: the angle sum gives the multiple,
    and the answer is that multiple divided by its coefficient.
    """
    c = c or rng.randrange(19, 90)
    mult = mult or rng.choice([2, 2, 3])
    a = a or rng.randrange(20, 100)
    rest = 180 - c - a
    if rest <= 0 or rest % mult:
        raise ItemError("this triangle does not leave a whole multiple for the unknown")
    b = rest // mult
    if b < 8 or rest < 15:
        raise ItemError("the unknown angle comes out too small to draw")
    key = E(b)
    pool = {
        "unreduced": Mis(f"stopped at {mult}b rather than dividing by {mult}",
                         whole(rest)),
        "sum_given": Mis("added the two known measures instead of subtracting them "
                         "from 180 degrees", whole(c + a)),
        "right_c": Mis("subtracted the marked angle from 90 degrees", whole(90 - c)),
        "supp_a": Mis("subtracted only the given value of a from 180 degrees",
                      whole(180 - a)),
        "half_c": Mis(f"divided the marked angle by {mult} instead of the remaining "
                      "angle", whole(Fraction(c, mult))),
    }
    order = ["unreduced", "sum_given", "right_c", "supp_a", "half_c"]
    left, right, top = triangle_pts(rest, a, 1.0)
    fig = (Fig().path(left, right, top, left)
           .angle(top, left, right, f"{c}°", italic=False)
           .angle(left, right, top, f"{mult}b°")
           .angle(right, top, left, "a°").render())
    stem = f"In the triangle above, a = {a}. What is the value of b ?"
    rationale = f"{c} + {mult}b + {a} = 180, so {mult}b = {rest} and b = {b}."
    params = {"kind": "lat_angle_algebra", "c": c, "mult": mult, "a": a}
    return finish("lat.angle_algebra", "an angle sum written as an equation", "easy",
                  seed, stem, key, pick(pool, order, wrongs), rng, rationale,
                  unit=unit, figure=fig, params=params, fmt=fmt)


# ====================================================== the exterior angle

def exterior_angle(rng: random.Random, seed: int, *, mode=None, p=None, q=None,
                   inner=None, ext=None, names=None, extra_label=None, fmt="mcq",
                   unit=False, wrongs=None) -> Item:
    """An exterior angle equals the two interior angles it is not next to.

    `mode="extended"` extends both of the other sides and marks the angle
    beside the vertical pair at the apex; `mode="extend_base"` extends the
    base, gives the exterior angle there, and leaves the far interior angle to
    be found.
    """
    mode = mode or rng.choice(["extended", "extend_base"])
    names = tuple(names or rng.choice([("P", "Q", "R"), ("A", "B", "C"),
                                       ("X", "Y", "Z"), ("J", "K", "L")]))

    if mode == "extended":
        p = p or rng.randrange(25, 86)
        q = q or rng.randrange(25, 86)
        if p + q >= 175 or abs(p - q) < 5:
            raise ItemError("these base angles do not make a readable figure")
        key = E(p + q)
        pool = {
            "supp_left": Mis("took the supplement of one base angle", whole(180 - p)),
            "supp_right": Mis("took the supplement of the other base angle",
                              whole(180 - q)),
            "apex": Mis("gave the angle at the apex instead of the one marked",
                        whole(180 - p - q)),
            "double_big": Mis("doubled the larger base angle", whole(2 * max(p, q))),
            "double_small": Mis("doubled the smaller base angle",
                                whole(2 * min(p, q))),
        }
        order = ["supp_left", "supp_right", "apex", "double_big", "double_small"]
        left, right, apex = triangle_pts(p, q, 1.0)
        past_left = polar(apex, direction(left, apex), 0.42)
        past_right = polar(apex, direction(right, apex), 0.42)
        fig = (Fig().path(left, right).path(left, apex, past_left)
               .path(right, apex, past_right)
               .angle(left, right, apex, f"{p}°", italic=False)
               .angle(right, apex, left, f"{q}°", italic=False)
               .angle(apex, left, past_right, "x°").render())
        stem = ("In the figure above, two sides of a triangle are extended. What is "
                "the value of x ?")
        rationale = (f"The apex angle is 180 − {p} − {q} = {180 - p - q}"
                     f"°, and x is its supplement, so x = {p} + {q} = {p + q}.")
        skill, tier = "an exterior angle of a triangle", "easy"
        params = {"kind": "lat_exterior_angle", "mode": mode, "p": p, "q": q}
    else:
        inner = inner or rng.randrange(95, 150)
        ext = ext or rng.randrange(min(inner + 12, 175), 176)
        at_r = 180 - ext
        third = ext - inner
        if at_r <= 4 or third <= 4 or inner + at_r >= 180:
            raise ItemError("these two angles do not close a triangle")
        key = E(third)
        pool = {
            "inner_r": Mis("gave the interior angle at the extended vertex instead",
                           whole(at_r)),
            "supp_q": Mis("took the supplement of the angle given inside the "
                          "triangle", whole(180 - inner)),
            "iso_half": Mis("assumed the triangle is isosceles and split what was "
                            "left of 180 degrees evenly",
                            whole(Fraction(180 - inner, 2))),
            "supp_ext": Mis("subtracted the exterior angle's supplement from the "
                            "exterior angle", whole(ext - at_r)),
            "sum_over": Mis("added the two given measures and took what was over a "
                            "straight angle", whole(inner + ext - 180)),
        }
        order = ["inner_r", "supp_q", "iso_half", "supp_ext", "sum_over"]
        Pn, Qn, Rn = names
        S = extra_label or rng.choice([s for s in "STUVW"
                                       if s not in names])
        r_pt, q_pt = P(0, 0), P(1, 0)
        p_pt = meet(ray(r_pt, -at_r), ray(q_pt, 180 + inner))
        s_pt = P(-0.4, 0)
        fig = (Fig().path(s_pt, r_pt, q_pt).path(q_pt, p_pt).path(r_pt, p_pt)
               .name(s_pt, S, 100).name(r_pt, Rn, 100).name(q_pt, Qn, 100)
               .name(p_pt, Pn, 300).render())
        stem = (f"In triangle {Pn}{Qn}{Rn}, {Qn}{Rn} is extended to point {S}. The "
                f"measure of ∠{Pn}{Qn}{Rn} is {inner}°, and the measure of "
                f"∠{Pn}{Rn}{S} is {ext}°. What is the measure of "
                f"∠{Qn}{Pn}{Rn}?")
        rationale = (f"∠{Pn}{Rn}{S} is exterior to the triangle at {Rn}, so it "
                     f"equals ∠{Pn}{Qn}{Rn} + ∠{Qn}{Pn}{Rn}: {ext} − "
                     f"{inner} = {third}°.")
        skill, tier = "an exterior angle of a triangle", "medium"
        params = {"kind": "lat_exterior_angle", "mode": mode, "inner": inner,
                  "ext": ext}
    return finish("lat.exterior_angle", skill, tier, seed, stem, key,
                  pick(pool, order, wrongs), rng, rationale, unit=unit,
                  figure=fig, params=params, fmt=fmt)


# ============================== an isosceles triangle reached through a chain

def isosceles_cross(rng: random.Random, seed: int, *, s=None, t=None, v=None,
                    ask=None, labels=None, in_stem=False, fmt="mcq", unit=False,
                    flip=False, wrongs=None) -> Item:
    """Two segments cross a triangle whose equal sides meet at the far vertex.

    R, V and U lie on a line, S is above it, T is on SU, and TR = TU. The
    isosceles triangle RTU turns its apex angle into the base angle at U, the
    angle sum of triangle SVU turns that into the angle at V, and the item is
    those two steps run in one direction or the other.
    """
    ask = ask or rng.choice(["v", "t"])
    S, T, U, R, V = tuple(labels or ("S", "T", "U", "R", "V"))
    s = s or rng.randrange(12, 60)
    if ask == "v":
        t = t or rng.randrange(90, 161)
        if (180 - t) % 2:
            raise ItemError("this apex angle does not halve into whole base angles")
        u = (180 - t) // 2
        v = s + u
    else:
        v = v or rng.randrange(s + 6, s + 46)
        u = v - s
        t = 180 - 2 * u
    if not (1 < u < 90) or not (0 < t < 180) or not (0 < v < 180):
        raise ItemError("this chain does not close into a drawable figure")
    if s >= 90 or s + u >= 175:
        raise ItemError("the angle at the crossing point is not readable")
    key = E(v if ask == "v" else t)

    pool = {
        "apex_supp": Mis("used the supplement of the apex angle as the base angle, "
                         "without halving it", whole(s + (180 - t))),
        "apex_only": Mis("stopped at the supplement of the apex angle, without "
                         "adding the angle at the top of the figure",
                         whole(180 - t)),
        "base_only": Mis("stopped at the base angle of the isosceles triangle",
                         whole(u)),
        "apex_half": Mis("halved the apex angle itself instead of what was left of "
                         "180 degrees", whole(s + Fraction(t, 2))),
        "given_only": Mis("gave back the angle at the top of the figure", whole(s)),
        "supp_v": Mis("took the supplement of the angle asked for", whole(180 - v)),
        "no_double": Mis("subtracted the base angle from 180 degrees once instead of "
                         "twice", whole(180 - u)),
        "double_base": Mis("doubled the base angle instead of subtracting twice the "
                           "base angle from 180 degrees", whole(2 * u)),
    }
    order = (["apex_supp", "apex_only", "base_only", "apex_half", "given_only",
              "supp_v"]
             if ask == "v" else ["no_double", "double_base", "supp_v", "base_only"])

    # U at the origin, the base line running left to R; T is where the two
    # u-degree rays meet, which is what makes TR = TU, and S lies beyond T.
    L = 1.0
    u_pt, r_pt = P(0, 0), P(-L, 0)
    t_pt = meet(ray(u_pt, 180 - u), ray(r_pt, u))
    m = (L / (2 * cosd(u))) * 1.95
    s_pt = polar(u_pt, 180 - u, m)
    vx = -m * sind(s) / sind(u + s)
    if not (-L * 0.92 < vx < -L * 0.10):
        raise ItemError("the crossing point would not land on the base of the figure")
    v_pt = P(vx, 0)
    pts = {"S": s_pt, "T": t_pt, "U": u_pt, "R": r_pt, "V": v_pt}
    if flip:
        pts = {k: P(-x, y) for k, (x, y) in pts.items()}
    s_pt, t_pt, u_pt, r_pt, v_pt = (pts["S"], pts["T"], pts["U"], pts["R"], pts["V"])
    side = 1 if flip else -1

    fig = Fig()
    fig.path(r_pt, u_pt).path(u_pt, s_pt).path(r_pt, t_pt).path(s_pt, v_pt)
    fig.name(s_pt, S, 90 + 45 * side).name(t_pt, T, 90 + 30 * side)
    fig.name(u_pt, U, 90 - 70 * side).name(r_pt, R, 90 + 110 * side)
    fig.name(v_pt, V, 280)
    fig.tick(r_pt, t_pt).tick(t_pt, u_pt)
    if ask == "v":
        fig.angle(v_pt, s_pt, r_pt, "x°")
        if not in_stem:
            fig.angle(s_pt, v_pt, u_pt, f"{s}°", italic=False)
            fig.angle(t_pt, r_pt, u_pt, f"{t}°", italic=False)
    else:
        fig.angle(t_pt, u_pt, r_pt, "x°")
    if in_stem and ask == "v":
        stem = (f"In the figure, {R}{T} = {T}{U}. The measure of angle {V}{S}{T} is "
                f"{s}°, and the measure of angle {R}{T}{U} is {t}°. What is "
                f"the value of x?")
    elif in_stem:
        stem = (f"In the figure, {R}{T} = {T}{U}, the measure of angle {V}{S}{T} is "
                f"{s}°, and the measure of angle {R}{V}{S} is {v}°. What is "
                f"the value of x?")
    else:
        stem = f"In the figure above, {R}{T} = {T}{U}. What is the value of x ?"
    rationale = (f"{R}{T} = {T}{U} makes ∠{T}{U}{R} = (180 − {t})/2 = {u}"
                 f"°, and ∠{R}{V}{S} is exterior to triangle {S}{V}{U}, so "
                 f"it measures {s} + {u} = {v}°.")
    params = {"kind": "lat_isosceles_cross", "s": s, "t": t, "v": v, "ask": ask}
    return finish("lat.isosceles_cross", "an isosceles triangle in a chain", "hard",
                  seed, stem, key, pick(pool, order, wrongs), rng, rationale,
                  unit=unit, figure=fig.render(), params=params, fmt=fmt)


# ================================= two isosceles triangles about one crossing

def vertical_isosceles(rng: random.Random, seed: int, *, apex=None, extra=None,
                       labels=None, fmt="spr", unit=False, wrongs=None) -> Item:
    """Two segments cross, each cutting the other into a pair of equal parts.

    The crossing makes two isosceles triangles whose apex angles are vertical
    to each other and supplementary to the marked one, so the base angle of
    the lower triangle is exactly half the marked angle.
    """
    apex = apex or 2 * rng.randrange(15, 60)
    extra = extra or rng.randrange(35, max(36, 175 - apex))
    if apex % 2 or not (20 <= apex <= 140):
        raise ItemError("this crossing angle does not halve into a whole number")
    if extra <= 0 or apex + extra >= 180 or abs(extra - (180 - apex) / 2) < 4:
        raise ItemError("the figure would be symmetric, or would not close")
    Ml, Nl, Ql, Rl, Pl = tuple(labels or ("M", "N", "Q", "R", "P"))
    key = E(Fraction(apex, 2))

    half = apex / 2.0
    o = P(0, 0)
    far = sind(extra) / sind(180 - apex - extra)
    if not 0.45 <= far <= 2.2:
        # one pair of arms many times the other squeezes the marked angle at Q
        # up against the one at P, and then which number names which stops
        # being readable
        raise ItemError("this draw makes one pair of arms far longer than the other")
    q_pt = polar(o, half, 1.0)
    n_pt = polar(o, 180 - half, 1.0)
    r_pt = polar(o, -half, far)
    m_pt = polar(o, 180 + half, far)
    fig = (Fig().path(m_pt, q_pt).path(n_pt, r_pt).path(n_pt, m_pt)
           .path(q_pt, r_pt).path(m_pt, r_pt)
           .name(n_pt, Nl, 100).name(q_pt, Ql, 80).name(m_pt, Ml, 200)
           .name(r_pt, Rl, 340).name(o, Pl, 118, gap=11)
           .angle(q_pt, o, r_pt, f"{extra}°", r=17, italic=False)
           .angle(o, q_pt, r_pt, f"{apex}°", r=16, italic=False).render())
    stem = (f"In the figure above, {Ml}{Ql} and {Nl}{Rl} intersect at point {Pl}, "
            f"{Nl}{Pl} = {Ql}{Pl}, and {Ml}{Pl} = {Pl}{Rl}. What is the measure, in "
            f"degrees, of ∠{Ql}{Ml}{Rl} ?")
    rationale = (f"∠{Ml}{Pl}{Rl} is the supplement of the {apex}° angle, so "
                 f"triangle {Ml}{Pl}{Rl} has apex {180 - apex}° and equal base "
                 f"angles of {apex // 2}°; {Ql} lies on {Ml}{Pl} extended, so "
                 f"∠{Ql}{Ml}{Rl} is one of them.")
    params = {"kind": "lat_vertical_isosceles", "apex": apex, "extra": extra}
    pool = {
        "apex_itself": Mis("gave the marked angle rather than the base angle",
                           whole(apex)),
        "supp": Mis("gave the supplement of the marked angle", whole(180 - apex)),
        "extra": Mis("gave the other angle marked in the figure", whole(extra)),
    }
    return finish("lat.vertical_isosceles", "isosceles triangles at a crossing",
                  "hard", seed, stem, key,
                  pick(pool, ["apex_itself", "supp", "extra"], wrongs), rng,
                  rationale, unit=unit, figure=fig, params=params, fmt=fmt)


# ============================ two triangles hinged on a pair of vertical angles

def crossing_triangles(rng: random.Random, seed: int, *, a=None, x=None, e=None,
                       labels=None, fmt="mcq", unit=False, wrongs=None) -> Item:
    """Two segments cross, making two triangles that share a vertical angle.

    Three of the four outer angles are given; the fourth follows because the
    two triangles have the same angle at the crossing.
    """
    A, B, C, D, Ee = tuple(labels or ("A", "B", "C", "D", "E"))
    a = a or rng.randrange(15, 61)
    x = x or rng.randrange(40, 130)
    mid = 180 - a - x
    if mid <= 12 or a + x <= 20:
        raise ItemError("the two segments would not cross at a readable angle")
    e = e or rng.randrange(15, max(16, 180 - mid))
    y = 180 - mid - e
    if y <= 8 or e <= 8:
        raise ItemError("one of the angles in this figure is too small to mark")
    key = E(y)
    pool = {
        "given_x": Mis(f"assumed the second triangle repeats angle {B}", whole(x)),
        "vertical": Mis(f"gave the angle at {C} rather than the angle at {D}",
                        whole(mid)),
        "sum_ax": Mis("added the two angles of the first triangle instead of "
                      "subtracting them from 180 degrees", whole(a + x)),
        "supp_e": Mis(f"took the supplement of the angle at {Ee}", whole(180 - e)),
        "supp_mid": Mis("used the supplement of the crossing angle in the second "
                        "triangle", whole(mid - e)),
        "right": Mis("gave a right angle, which the figure only looks like",
                     whole(90)),
    }
    order = ["given_x", "vertical", "sum_ax", "supp_e", "supp_mid", "right"]

    c_pt = P(0, 0)
    a_pt, d_pt = P(-1.0, 0), P(1.15, 0)
    cb = 1.0 * sind(a) / sind(x)
    ce = 1.15 * sind(y) / sind(e)
    # a triangle only a sliver deep puts the angle marked at its apex down on
    # the segment AD, where it reads as naming an angle at A instead
    if min(cb, ce) * sind(mid) < 0.125 * (a_pt[0] * -1 + d_pt[0]):
        raise ItemError("one of the two triangles is too shallow to mark")
    b_pt = polar(c_pt, 180 - mid, cb)
    e_pt = polar(c_pt, -mid, ce)
    fig = (Fig().path(a_pt, d_pt).path(b_pt, e_pt).path(a_pt, b_pt).path(d_pt, e_pt)
           .name(a_pt, A, 200).name(b_pt, B, 100).name(c_pt, C, 100, gap=12)
           .name(d_pt, D, 70).name(e_pt, Ee, 300)
           .angle(a_pt, b_pt, d_pt, f"{a}°", italic=False)
           .angle(b_pt, a_pt, e_pt, "x°", r=13)
           .angle(d_pt, a_pt, e_pt, "y°", r=13)
           .angle(e_pt, d_pt, b_pt, f"{e}°", italic=False).render())
    stem = (f"In the figure above, {A}{D} intersects {B}{Ee} at {C}. If x = {x}, what "
            f"is the value of y ?")
    rationale = (f"∠{A}{C}{B} = 180 − {a} − {x} = {mid}°, and "
                 f"∠{D}{C}{Ee} is vertical to it, so y = 180 − {mid} − "
                 f"{e} = {y}.")
    params = {"kind": "lat_crossing_triangles", "a": a, "x": x, "e": e}
    return finish("lat.crossing_triangles", "vertical angles across two triangles",
                  "easy", seed, stem, key, pick(pool, order, wrongs), rng, rationale,
                  unit=unit, figure=fig, params=params, fmt=fmt)
