"""Similar figures: what a scale factor changes and what it leaves alone.

Half of these items exist to catch one misconception, and the source set says
so in its own option lists: a student who has learned that a dilation
multiplies the sides very often multiplies the angles too. So the pools here
are built around the scale factor -- angle times k, angle plus k, angle over
k, and the bare k itself -- and a source item names the three the College
Board printed.

The rest are the proportion items: shadows, a line drawn parallel to one side,
the altitude of a right triangle, and the two triangles a crossing pair of
segments makes.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction as Q

from ....exact import E, Exact
from ....item import Item, ItemError, Mis, assemble_text
from ..figures import Fig, P, along, dist, meet, polar, ray, triangle_pts
from ..kit import dec, pick, plain, snap, unambiguous, whole
from .triangles import cosd, finish, sind

__all__ = ["similar_angle", "similar_side", "shadow", "parallel_segments",
           "ratio_match", "similar_needed", "similar_sufficient",
           "vertical_similar", "altitude_legs", "geometric_mean",
           "parallel_cut_area", "area_range"]

TALL = [("a flagpole", "the flagpole"), ("a radio tower", "the radio tower"),
        ("a lighthouse", "the lighthouse"), ("a water tower", "the water tower"),
        ("a utility pole", "the utility pole")]
SHORT = [("a nearby oak tree", "the oak tree"), ("a nearby cherry tree", "the cherry tree"),
         ("a nearby street sign", "the street sign"),
         ("a nearby mailbox", "the mailbox"), ("a nearby fence post", "the fence post")]
# the altitude to the hypotenuse is pq/h, and the source set prints it as a
# decimal, so only the families whose altitude terminates are drawn from
TRIPLES = ([(3 * k, 4 * k, 5 * k) for k in range(1, 21)]
           + [(4 * k, 3 * k, 5 * k) for k in range(1, 21)]
           + [(7 * k, 24 * k, 25 * k) for k in range(1, 9)]
           + [(24 * k, 7 * k, 25 * k) for k in range(1, 9)])


def _num(v) -> Exact:
    return v if isinstance(v, Exact) else E(Q(v))


# ================================== an angle a scale factor cannot change

def similar_angle(rng: random.Random, seed: int, *, mode=None, angle=None, k=None,
                  shape=None, names=None, partner=None, side=None, fmt=None,
                  unit=False, note=None, wrongs=None) -> Item:
    """Similar figures have equal angles, whatever the scale factor is.

    The four modes are the four ways the source set hides that one fact: a
    drawn dilation, a ratio of side lengths written out, a symbolic scale
    factor whose options are left unevaluated, and a pair of quadrilaterals.
    """
    mode = mode or rng.choice(["dilate", "ratio", "expr", "quad"])
    angle = angle or rng.randrange(20, 141)
    k = k or rng.randrange(2, 9)
    names = tuple(names or ("A", "B", "C"))
    partner = tuple(partner or ("X", "Y", "Z"))
    key = E(angle)

    pool = {
        "divide": Mis("divided the angle by the scale factor, as if a dilation "
                      "shrank the angles too", whole(Q(angle, k))),
        "times": Mis("multiplied the angle by the scale factor", whole(angle * k)),
        "add": Mis("added the scale factor to the angle", whole(angle + k)),
        "sub": Mis("subtracted the scale factor from the angle", whole(angle - k)),
        "scale": Mis("gave the scale factor itself", whole(k)),
        "side": Mis("gave the side length rather than the angle measure",
                    whole(side) if side else None),
    }
    order = ["divide", "sub", "add", "times", "scale", "side"]

    if mode == "expr":
        Ca, Aa, Ea, Ba, Da = (tuple(names) if len(names) == 5
                              else ("C", "A", "E", "B", "D"))
        if not 15 <= 90 - angle <= 75:
            raise ItemError("this angle leaves the inner right triangle undrawable")
        a_pt, e_pt, c_pt = triangle_pts(angle, 90, 1.0)
        b_pt = along(a_pt, c_pt, 0.45)
        d_pt = along(e_pt, c_pt, 0.45)
        fig = (Fig().path(a_pt, e_pt, c_pt, a_pt).seg(b_pt, d_pt)
               .right(e_pt, a_pt, c_pt).right(d_pt, b_pt, c_pt)
               .name(a_pt, Aa, 200).name(e_pt, Ea, 320).name(c_pt, Ca, 60)
               .name(b_pt, Ba, 175).name(d_pt, Da, 0).render())
        key_text = f"{angle}°"
        wrong = [
            Mis("multiplied the angle by the scale factor",
                f"({k} · {angle})°"),
            Mis("added the scale factor to the angle", f"({k} + {angle})°"),
            Mis("gave the scale factor itself", f"{k}°"),
        ]
        stem = (f"In the figure shown, triangle {Ca}{Aa}{Ea} is similar to triangle "
                f"{Ca}{Ba}{Da}. The measure of angle {Ca}{Ba}{Da} is {angle}°, and "
                f"{Aa}{Ea} = {k}({Ba}{Da}). What is the measure of angle "
                f"{Ca}{Aa}{Ea}?")
        rationale = (f"Similar triangles have equal corresponding angles, so angle "
                     f"{Ca}{Aa}{Ea} measures {angle}° however long the sides are.")
        choices, reasons, letter = assemble_text(key_text, wrong, rng)
        params = {"kind": "lat_similar_angle", "mode": mode, "angle": angle, "k": k}
        return Item("lat.similar_angle", "angles under a dilation", "medium", seed,
                    stem, "mcq", key, letter, rationale, choices, reasons,
                    list(choices), figure=fig, params=params)

    fig = None
    if mode == "dilate":
        shape = shape or rng.randrange(25, 120)
        if angle + shape >= 170 or shape < 20:
            raise ItemError("the two triangles would not be drawable")
        small = triangle_pts(angle, shape, 1.0)
        big = triangle_pts(angle, shape, 1.0 * k)
        gap = 1.0 + max(p[0] for p in small) - min(p[0] for p in big) + 0.55
        big = tuple(P(p[0] + gap, p[1]) for p in big)
        f = Fig()
        f.path(*small, small[0]).path(*big, big[0])
        f.name(small[0], names[0], 200).name(small[1], names[2], 340)
        f.name(small[2], names[1], 90)
        f.name(big[0], partner[0], 200).name(big[1], partner[2], 340)
        f.name(big[2], partner[1], 90)
        f.angle(small[0], small[1], small[2], f"{angle}°", r=17, italic=False)
        f.side(small[0], small[1], "d", out=-13, italic=True)
        fig = f.render()
        stem = (f"For the triangles shown, triangle {''.join(names)} is dilated by a "
                f"scale factor of {k} to obtain triangle {''.join(partner)}, where "
                f"d = {side or 16}. What is the measure, in degrees, of angle "
                f"{partner[0]}?")
        rationale = (f"A dilation multiplies lengths and leaves angles alone, so "
                     f"angle {partner[0]} measures the same {angle}° as angle "
                     f"{names[0]}.")
        skill = "angles under a dilation"
    elif mode == "ratio":
        d, e, f2 = partner
        A, B, C = names
        stem = (f"Triangle {A}{B}{C} and triangle {d}{e}{f2} are shown. The "
                f"relationship between the side lengths of the two triangles is such "
                f"that {A}{B}/{d}{e} = {B}{C}/{e}{f2} = {A}{C}/{d}{f2} = {k}. If the "
                f"measure of angle {B}{A}{C} is {angle}°, what is the measure, "
                f"in degrees, of angle {e}{d}{f2} ?")
        rationale = (f"Every pair of corresponding sides is in the same ratio, so the "
                     f"triangles are similar and angle {e}{d}{f2} matches angle "
                     f"{B}{A}{C}: {angle}°.")
        shape = shape or rng.randrange(25, 120)
        if angle + shape >= 170:
            raise ItemError("the two triangles would not be drawable")
        small = triangle_pts(angle, shape, 1.0)
        big = triangle_pts(angle, shape, 1.0 / k)
        gap = 1.0 + max(p[0] for p in small) - min(p[0] for p in big) + 0.5
        big = tuple(P(p[0] + gap, p[1]) for p in big)
        f = Fig()
        f.path(*small, small[0]).path(*big, big[0])
        f.name(small[0], names[0], 200).name(small[1], names[2], 340)
        f.name(small[2], names[1], 90)
        f.name(big[0], partner[0], 200).name(big[1], partner[2], 340)
        f.name(big[2], partner[1], 90)
        fig = f.render()
        skill = "angles under a similarity"
    else:
        quad = tuple(names) if len(names) == 4 else ("P", "Q", "R", "S")
        other = tuple(partner) if len(partner) == 4 else ("W", "X", "Y", "Z")
        stem = (f"Quadrilaterals {''.join(quad)} and {''.join(other)} are similar, "
                f"where {quad[0]}, {quad[1]}, and {quad[2]} correspond to {other[0]}, "
                f"{other[1]}, and {other[2]}, respectively. The measure of "
                f"∠{quad[3]} is {angle}°, {quad[0]}{quad[3]} = "
                f"{side or k}, and {other[0]}{other[3]} = "
                f"{(side or k) // k}. What is the measure of ∠{other[3]}?")
        rationale = (f"Similar figures have equal corresponding angles, so "
                     f"∠{other[3]} measures {angle}°; the scale factor "
                     f"{k} changes the side lengths and nothing else.")
        skill = "angles under a similarity"

    params = {"kind": "lat_similar_angle", "mode": mode, "angle": angle, "k": k}
    return finish("lat.similar_angle", skill, "medium", seed, stem, key,
                  pick(pool, order, wrongs), rng, rationale, unit=unit, figure=fig,
                  params=params, fmt=fmt or "mcq")


def similar_side(rng: random.Random, seed: int, *, side=None, k=None, names=None,
                 partner=None, fmt="mcq", unit=False, wrongs=None) -> Item:
    """The scale factor multiplies a side, and the options are the other things
    a student does with it."""
    side = side or rng.randrange(4, 41)
    k = k or rng.randrange(2, 8)
    names = tuple(names or ("A", "B", "C"))
    partner = tuple(partner or ("X", "Y", "Z"))
    key = E(side * k)
    pool = {
        "same": Mis("left the side unchanged, as if similar meant congruent",
                    whole(side)),
        "add": Mis("added the scale factor instead of multiplying by it",
                   whole(side + k)),
        "sub": Mis("subtracted the scale factor from the side", whole(side - k)),
        "divide": Mis("divided by the scale factor instead of multiplying",
                      whole(Q(side, k))),
        "square": Mis("multiplied by the square of the scale factor, which is what "
                      "happens to an area", whole(side * k * k)),
    }
    order = ["sub", "same", "add", "divide", "square"]
    A, B, C = names
    X, Y, Z = partner
    stem = (f"Triangle {A}{B}{C} is similar to triangle {X}{Y}{Z}, such that {A}, "
            f"{B}, and {C} correspond to {X}, {Y}, and {Z} respectively. The length "
            f"of each side of triangle {X}{Y}{Z} is {k} times the length of its "
            f"corresponding side in triangle {A}{B}{C}. The measure of side {A}{B} "
            f"is {side}. What is the measure of side {X}{Y}?")
    rationale = (f"Every side of {X}{Y}{Z} is {k} times its match, so {X}{Y} = "
                 f"{k}({side}) = {side * k}.")
    params = {"kind": "lat_similar_side", "side": side, "k": k}
    return finish("lat.similar_side", "side lengths under a similarity", "medium",
                  seed, stem, key, pick(pool, order, wrongs), rng, rationale,
                  unit=unit, params=params, fmt=fmt)


# ============================================================ shadows

def shadow(rng: random.Random, seed: int, *, h1=None, s1=None, s2=None, story=None,
           closest=False, step=5, tall=None, short=None, fmt="mcq", unit=False,
           wrongs=None) -> Item:
    """Two upright objects and the sun: the shadows are in the same ratio as the
    heights, because the two triangles are similar."""
    free_dimensions = h1 is None and s1 is None and s2 is None
    story = story or rng.choice(["monument", "trees"])
    if story == "monument":
        h1 = h1 or 10 * rng.randrange(6, 60)
        s1 = s1 or 10 * rng.randrange(3, 40)
        s2 = s2 or rng.randrange(3, 40)
    else:
        h1 = h1 or rng.randrange(6, 41)
        s1 = s1 or rng.randrange(2, 21)
        s2 = s2 or rng.randrange(1, 20)
    if min(h1, s1, s2) <= 0 or s2 >= s1:
        raise ItemError("the second object must be the shorter of the two")
    if h1 == s1:
        if not free_dimensions:
            raise ItemError("equal height and shadow make the answer the other shadow")
        # Reject the equal-height draw and redraw its free height. For exact
        # tree questions, keep the resulting second height a whole number.
        heights = (range(6, 41) if story == "trees" else
                   (10 * n for n in range(6, 60)))
        choices = [height for height in heights if height != s1 and
                   (closest or (height * s2) % s1 == 0)]
        if not choices:
            raise ItemError("no nondegenerate height keeps a whole-number answer")
        h1 = rng.choice(choices)
    exact = Q(h1 * s2, s1)
    tall = tuple(tall or rng.choice(TALL))
    short = tuple(short or rng.choice(SHORT))

    def show(v):
        return E(unambiguous(v, Q(step))) if closest else (E(v) if Q(v) > 0 else None)

    pool = {
        "swap": Mis("multiplied the two shadows and divided by the known height",
                    _ok(show, Q(s1 * s2, h1))),
        "shadow_ratio": Mis("gave the ratio of the two shadows rather than the "
                            "height", _ok(show, Q(s1, s2))),
        "height_over_shadow": Mis("divided the known height by the second shadow",
                                  _ok(show, Q(h1, s2))),
        "invert_ratio": Mis("set up the proportion upside down, multiplying the "
                            "known height by the wrong shadow", _ok(show, Q(h1 * s1, s2))),
        "diff_shadows": Mis("subtracted one shadow from the other",
                            _ok(show, Q(s1 - s2))),
        "height_minus_shadow": Mis("subtracted the second shadow from the known "
                                   "height", _ok(show, Q(h1 - s2)) if h1 > s2 else None),
    }
    order = ["swap", "shadow_ratio", "height_over_shadow", "diff_shadows",
             "height_minus_shadow", "invert_ratio"]
    key = E(unambiguous(exact, Q(step))) if closest else E(exact)
    if not closest:
        # an exact answer here is a whole number of feet in every source item,
        # and a lone fraction among three integers is the answer without any
        # geometry, so a draw that does not divide evenly is thrown away
        if key.coef.denominator != 1:
            raise ItemError("this height is not a whole number of feet")
        for name, m in list(pool.items()):
            if m.value is not None and m.value.coef.denominator != 1:
                pool[name] = Mis(m.reason, None)

    if story == "monument":
        stem = (f"At a certain time and day, {tall[0]} casts a shadow that is {s1} "
                f"feet long. At the same time, {short[0]} casts a shadow that is {s2} "
                f"feet long. Given that {tall[1]} is approximately {h1} feet tall, "
                f"which of the following is closest to the height, in feet, of "
                f"{short[1]}?")
        skill = "similar triangles in a shadow problem"
    else:
        stem = (f"Two nearby trees are perpendicular to the ground, which is flat. "
                f"One of these trees is {h1} feet tall and has a shadow that is {s1} "
                f"feet long. At the same time, the shadow of the other tree is {s2} "
                f"feet long. How tall, in feet, is the other tree?")
        skill = "similar triangles in a shadow problem"
    if story == "monument" and not closest:
        raise ItemError("that story only makes sense as a closest-to item")
    rationale = (f"The two right triangles are similar, so height over shadow is the "
                 f"same for both: {h1}/{s1} = h/{s2} gives h = {plain(exact)}"
                 + (f", and the nearest option is {plain(key.coef)}." if closest
                    else "."))
    params = {"kind": "lat_shadow", "h1": h1, "s1": s1, "s2": s2,
              "closest": bool(closest), "step": step}
    return finish("lat.shadow", skill, "easy", seed, stem, key,
                  pick(pool, order, wrongs), rng, rationale, unit=unit,
                  params=params, fmt=fmt)


def _ok(show, v):
    try:
        return show(v)
    except (ItemError, ValueError, ZeroDivisionError):
        return None


# =============================== three parallel segments across two transversals

def parallel_segments(rng: random.Random, seed: int, *, ab=None, bc=None, fe=None,
                      places=1, labels=None, fmt="mcq", unit=False,
                      wrongs=None) -> Item:
    """Parallel lines cut two transversals in the same ratio."""
    A, B, C, D, Ee, F = tuple(labels or ("A", "B", "C", "D", "E", "F"))
    ab = ab if ab is not None else Q(rng.randrange(40, 200), 4)
    bc = bc if bc is not None else Q(rng.randrange(40, 200), 4)
    fe = fe if fe is not None else Q(rng.randrange(40, 200), 4)
    ab, bc, fe = Q(ab), Q(bc), Q(fe)
    if min(ab, bc, fe) <= 1:
        raise ItemError("a segment in this figure is too short to label")
    exact = fe * bc / ab
    step = Q(1, 10 ** places)
    key = E(unambiguous(exact, step))
    pool = {
        "swapped": Mis("matched the sides the wrong way round, dividing by the "
                       "shorter piece instead of the longer one",
                       _ok(lambda v: E(snap(v, step)), bc * ab / fe)),
        "inverted": Mis("inverted the proportion", _ok(lambda v: E(snap(v, step)),
                                                       fe * ab / bc)),
        "added": Mis("added the difference of the two known pieces instead of "
                     "scaling", _ok(lambda v: E(snap(v, step)), fe + bc - ab)
                     if fe + bc - ab > 0 else None),
        "whole": Mis("gave the whole of the second transversal rather than the "
                     "piece asked for", _ok(lambda v: E(snap(v, step)),
                                            fe + fe * bc / ab)),
    }
    order = ["swapped", "inverted", "added", "whole"]
    total1, total2 = ab + bc, fe + exact
    if not (Q(1, 2) <= total2 / total1 <= 2):
        raise ItemError("the two transversals are too different in length to draw")
    if not Q(1, 10) <= ab / bc <= 10:
        raise ItemError("the two pieces of the first transversal are too unlike "
                        "to draw")
    h = 0.93 * min(float(total1), float(total2))
    alpha = 180.0 - math.degrees(math.asin(h / float(total1)))
    beta = math.degrees(math.asin(h / float(total2)))
    a_pt = P(0, 0)
    f_pt = P(0.85 * h, 0)
    c_pt = polar(a_pt, alpha, float(total1))
    d_pt = polar(f_pt, beta, float(total2))
    b_pt = along(a_pt, c_pt, float(ab / total1))
    e_pt = along(f_pt, d_pt, float(fe / total2))
    fig = (Fig().seg(a_pt, f_pt).seg(b_pt, e_pt).seg(c_pt, d_pt)
           .seg(a_pt, c_pt).seg(f_pt, d_pt)
           .name(a_pt, A, 250).name(f_pt, F, 290).name(b_pt, B, 175)
           .name(e_pt, Ee, 5).name(c_pt, C, 135).name(d_pt, D, 45).render())
    stem = (f"In the figure above, {A}{F}, {B}{Ee}, and {C}{D} are parallel. Points "
            f"{B} and {Ee} lie on {A}{C} and {F}{D}, respectively. If {A}{B} = "
            f"{plain(ab)}, {B}{C} = {plain(bc)}, and {F}{Ee} = {plain(fe)}, what is "
            f"the length of {Ee}{D}, to the nearest tenth?")
    rationale = (f"{A}{B}/{B}{C} = {F}{Ee}/{Ee}{D}, so {Ee}{D} = {plain(fe)}"
                 f"({plain(bc)})/{plain(ab)} = {dec(exact, places + 3)}, which is "
                 f"{dec(key.coef, places)} to the nearest tenth.")
    params = {"kind": "lat_parallel_segments", "ab": [ab.numerator, ab.denominator],
              "bc": [bc.numerator, bc.denominator], "fe": [fe.numerator, fe.denominator],
              "places": places}
    return finish("lat.parallel_segments", "parallel lines cut proportionally",
                  "medium", seed, stem, key, pick(pool, order, wrongs), rng,
                  rationale, unit=unit, figure=fig, params=params, fmt=fmt,
                  shown=lambda v: dec(v, places))


# ============================== which ratio in one triangle matches another

def ratio_match(rng: random.Random, seed: int, *, a=None, names=None,
                partner=None) -> Item:
    """Two right triangles whose acute angles are complementary.

    A ratio taken in one is some other ratio taken in the other, and the
    options are the four ways of pairing two of the second triangle's sides.
    """
    a = a or rng.randrange(20, 71)
    if a == 45:
        raise ItemError("a 45 degree angle makes two of the options equal")
    pairs = [(("A", "B", "C"), ("D", "E", "F")), (("J", "K", "L"), ("P", "Q", "R")),
             (("R", "S", "T"), ("W", "X", "Y")), (("A", "B", "C"), ("X", "Y", "Z"))]
    fallback = rng.choice(pairs)
    A, B, C = tuple(names or fallback[0])
    D, Ee, F = tuple(partner or fallback[1])
    b = 90 - a
    key_text = f"{D}{F}/{D}{Ee}"
    wrong = [
        Mis("inverted the ratio", f"{D}{Ee}/{D}{F}"),
        Mis(f"used the side opposite {D} instead of the hypotenuse, which gives a "
            f"tangent rather than a sine", f"{D}{F}/{Ee}{F}"),
        Mis(f"matched the marked angles instead of pairing each with the other's "
            f"complement", f"{Ee}{F}/{D}{Ee}"),
    ]
    one = triangle_pts(a, 90, 1.0)
    two = triangle_pts(b, 90, 1.0)
    gap = max(p[0] for p in one) - min(p[0] for p in two) + 0.55
    two = tuple(P(p[0] + gap, p[1]) for p in two)
    fig = (Fig().path(*one, one[0]).path(*two, two[0])
           .right(one[1], one[0], one[2]).right(two[1], two[0], two[2])
           .name(one[0], A, 200).name(one[1], C, 330).name(one[2], B, 90)
           .name(two[0], D, 200).name(two[1], F, 330).name(two[2], Ee, 90)
           .angle(one[0], one[1], one[2], f"{a}°", r=17, italic=False)
           .angle(two[0], two[1], two[2], f"{b}°", r=17, italic=False).render())
    stem = rng.choice([
        f"Triangles {A}{B}{C} and {D}{Ee}{F} are shown above. Which of the following "
        f"is equal to the ratio {B}{C}/{A}{B} ?",
        f"Triangles {A}{B}{C} and {D}{Ee}{F} are shown. Which of the following is "
        f"equal to the ratio {B}{C}/{A}{B}?",
    ])
    rationale = (f"{B}{C}/{A}{B} is the side opposite the {a}° angle over the "
                 f"hypotenuse. In {D}{Ee}{F} the {b}° angle is its complement, "
                 f"so the same ratio is the side beside it over the hypotenuse: "
                 f"{D}{F}/{D}{Ee}.")
    choices, reasons, letter = assemble_text(key_text, wrong, rng)
    params = {"kind": "lat_ratio_match", "a": a, "names": list((A, B, C)),
              "partner": list((D, Ee, F))}
    return Item("lat.ratio_match", "matching ratios in similar right triangles",
                "medium", seed, stem, "mcq", E(a), letter, rationale, choices,
                reasons, list(choices), figure=fig, params=params)


# ======================================= what more is needed to decide similarity

def similar_needed(rng: random.Random, seed: int, *, a=None, b=None, names=None,
                   partner=None) -> Item:
    """Two triangles already share two angles, so nothing further is needed."""
    a = a or rng.randrange(20, 90)
    b = b or rng.randrange(20, 160 - a)
    if a + b >= 175 or abs(a - b) < 6:
        raise ItemError("these two angles do not make a readable triangle")
    D, Ee, F = tuple(names or ("D", "E", "F"))
    R, S, T = tuple(partner or ("R", "S", "T"))
    # printed without the source's full stop: the three wrong options are noun
    # phrases, and a lone option ending in one is visibly the odd one out
    key_text = "No additional information is needed"
    wrong = [
        Mis(f"the third angle of a triangle is fixed by the other two, so angle {F} "
            f"is already known", f"The measure of angle {F}"),
        Mis(f"angle {T} is fixed in the same way, and knowing it adds nothing",
            f"The measure of angle {T}"),
        Mis("both third angles are already determined, so neither measurement adds "
            "anything", f"The measure of angle {F} and the measure of angle {T}"),
    ]
    stem = (f"In triangle {D}{Ee}{F}, the measure of angle {D} is {a}° and the "
            f"measure of angle {Ee} is {b}°. In triangle {R}{S}{T}, the measure "
            f"of angle {R} is {a}° and the measure of angle {S} is {b}°. "
            f"Which of the following additional pieces of information is needed to "
            f"determine whether triangle {D}{Ee}{F} is similar to triangle "
            f"{R}{S}{T}?")
    rationale = (f"Two pairs of equal angles are enough for similarity, and both "
                 f"third angles are already {180 - a - b}°, so the two triangles "
                 f"are similar as they stand.")
    choices, reasons, letter = assemble_text(key_text, wrong, rng)
    params = {"kind": "lat_similar_needed", "a": a, "b": b}
    return Item("lat.similar_needed", "the angle-angle similarity test", "medium",
                seed, stem, "mcq", E(180 - a - b), letter, rationale, choices,
                reasons, list(choices), params=params)


def similar_sufficient(rng: random.Random, seed: int, *, a=None, m=None, k=None,
                       side=None, short=None, names=None, partner=None) -> Item:
    """One angle and one side apiece; only a second pair of angles settles it."""
    a = a or rng.randrange(30, 90)
    m = m or rng.randrange(20, 130 - a)
    k = k or rng.randrange(2, 6)
    side = side or rng.randrange(4, 30)
    short = short or rng.randrange(4, 30)
    third = 180 - a - m
    if third < 15 or m < 15 or abs(m - third) < 6:
        raise ItemError("the two remaining angles are too close to tell apart")
    if a == m:
        # then naming angles M and S as m and a would also force the two
        # triangles equiangular, and the item would have two right answers
        raise ItemError("this draw makes one of the wrong options sufficient too")
    L, M, N = tuple(names or ("L", "M", "N"))
    R, S, T = tuple(partner or ("R", "S", "T"))
    key_text = (f"The measures of angles {M} and {T} are {m}° and "
                f"{third}°, respectively.")
    wrong = [
        Mis(f"{M}{N} and {S}{T} lie opposite the angles that are given, so this is a "
            f"side-side-angle pairing, which does not fix a triangle's shape",
            f"{M}{N} = {side} and {S}{T} = {side}"),
        Mis(f"the ratio matches, but {M}{N} and {S}{T} are again opposite the given "
            f"angles rather than beside them",
            f"{M}{N} = {side} and {S}{T} = {side * k}"),
        Mis(f"this would make triangle {R}{S}{T} have angles {a}°, {a}° "
            f"and {180 - 2 * a}°, which does not match triangle {L}{M}{N}",
            f"The measures of angles {M} and {S} are {m}° and {a}°, "
            f"respectively."),
    ]
    stem = (f"In triangles {L}{M}{N} and {R}{S}{T}, angles {L} and {R} each have "
            f"measure {a}°, {L}{N} = {short}, and {R}{T} = {short * k}. Which "
            f"additional piece of information is sufficient to prove that triangle "
            f"{L}{M}{N} is similar to triangle {R}{S}{T}?")
    rationale = (f"Angle {M} = {m}° makes angle {N} = {third}°, and angle "
                 f"{T} = {third}° with angle {R} = {a}° makes angle {S} = "
                 f"{m}°, so the two triangles agree in all three angles.")
    choices, reasons, letter = assemble_text(key_text, wrong, rng)
    params = {"kind": "lat_similar_sufficient", "a": a, "m": m, "k": k,
              "side": side, "short": short, "names": [L, M, N],
              "partner": [R, S, T]}
    return Item("lat.similar_sufficient", "what proves two triangles similar",
                "hard", seed, stem, "mcq", E(third), letter, rationale, choices,
                reasons, list(choices), params=params)


# ============================ similar triangles hinged on a pair of vertical angles

def vertical_similar(rng: random.Random, seed: int, *, wq=None, xq=None, wx=None,
                     yq=None, labels=None, fmt="spr", unit=False,
                     wrongs=None) -> Item:
    """Two segments cross; equal angles at the far ends make the triangles similar."""
    W, X, Y, Z, Qp = tuple(labels or ("W", "X", "Y", "Z", "Q"))
    wq = wq or rng.randrange(20, 121)
    xq = xq or rng.randrange(20, 161)
    wx = wx or rng.randrange(20, 161)
    yq = yq or rng.randrange(20, 121)
    if not (abs(wq - xq) < wx < wq + xq):
        raise ItemError("those three lengths do not make a triangle")
    zq = Q(xq * yq, wq)
    yz = Q(wx * yq, wq)
    if yz.denominator > 4 or zq.denominator > 4:
        raise ItemError("this draw gives a length the source set would not print")
    key = E(yz)
    cos_t = (wq ** 2 + xq ** 2 - wx ** 2) / (2.0 * wq * xq)
    if not -0.98 < cos_t < 0.98:
        raise ItemError("the crossing angle is too flat to draw")
    theta = math.degrees(math.acos(cos_t))
    if theta < 12:
        raise ItemError("the crossing angle is too thin to mark")
    o = P(0, 0)
    w_pt = polar(o, 180 - theta / 2, wq)
    x_pt = polar(o, 180 + theta / 2, xq)
    y_pt = polar(o, theta / 2, yq)
    z_pt = polar(o, -theta / 2, float(zq))
    fig = (Fig().seg(w_pt, z_pt).seg(x_pt, y_pt).seg(w_pt, x_pt).seg(y_pt, z_pt)
           .name(w_pt, W, 110).name(x_pt, X, 250).name(y_pt, Y, 70)
           .name(z_pt, Z, 290).name(o, Qp, 250, gap=13)
           .angle(w_pt, x_pt, z_pt, "a°", r=17)
           .angle(y_pt, z_pt, x_pt, "a°", r=17).render())
    stem = (f"In the figure shown, {W}{Z} and {X}{Y} intersect at point {Qp}. "
            f"{Y}{Qp} = {yq}, {W}{Qp} = {wq}, {W}{X} = {wx}, and {X}{Qp} = {xq}. "
            f"What is the length of {Y}{Z}?")
    rationale = (f"The angles at {W} and {Y} are equal and the angles at {Qp} are "
                 f"vertical, so triangle {W}{Qp}{X} is similar to triangle "
                 f"{Y}{Qp}{Z}: {Y}{Z} = {wx}({yq})/{wq} = {plain(yz)}.")
    params = {"kind": "lat_vertical_similar", "wq": wq, "xq": xq, "wx": wx, "yq": yq}
    pool = {
        "swap": Mis("matched the sides the wrong way round", _ok(E, Q(wx * wq, yq))),
        "zq": Mis(f"found {Z}{Qp} rather than {Y}{Z}", _ok(E, zq)),
        "ratio": Mis("gave the scale factor instead of the length",
                     _ok(E, Q(yq, wq))),
    }
    return finish("lat.vertical_similar", "similar triangles at a crossing", "hard",
                  seed, stem, key, pick(pool, ["zq", "swap", "ratio"], wrongs), rng,
                  rationale, unit=unit, figure=fig, params=params, fmt=fmt)


# ================================== the altitude of a right triangle

def altitude_legs(rng: random.Random, seed: int, *, triple=None, labels=None,
                  fmt="mcq", unit=False, wrongs=None) -> Item:
    """The altitude to the hypotenuse is the product of the legs over the hypotenuse."""
    p, q, h = tuple(triple or rng.choice(TRIPLES))
    M, N, Pp, Qp = tuple(labels or rng.choice([("M", "N", "P", "Q"),
                                               ("A", "B", "C", "D"),
                                               ("R", "S", "T", "U"),
                                               ("J", "K", "L", "N"),
                                               ("W", "X", "Y", "Z")]))
    if p * p + q * q != h * h:
        raise ItemError("those three lengths are not a right triangle")
    key = E(Q(p * q, h))
    if key.coef.denominator > 10:
        raise ItemError("this altitude is not a length the source set would print")
    pool = {
        "median": Mis("gave half the hypotenuse, which is the median from the right "
                      "angle rather than the altitude", _ok(E, Q(h, 2))),
        "leg_sq_short": Mis("squared the shorter leg and divided by the hypotenuse, "
                            "which gives the piece of the hypotenuse beside that "
                            "leg rather than the altitude", _ok(E, Q(p * p, h))),
        "leg_sq_long": Mis("squared the longer leg and divided by the hypotenuse, "
                           "which gives the other piece of the hypotenuse",
                           _ok(E, Q(q * q, h))),
        "half_long": Mis("halved the longer leg", _ok(E, Q(q, 2))),
        "legs_over_sum": Mis("divided the product of the legs by their sum instead "
                             "of by the hypotenuse", _ok(E, Q(p * q, p + q))),
        "diff": Mis("subtracted the shorter leg from the hypotenuse",
                    _ok(E, Q(h - p))),
    }
    order = ["median", "leg_sq_short", "leg_sq_long", "half_long",
             "legs_over_sum", "diff"]
    corner, right_pt, left_pt = triangle_pts(90, 0 + math.degrees(math.atan2(p, q)),
                                             1.0)
    # place the triangle on its hypotenuse, so the altitude is vertical
    m_pt, p_pt = P(0, 0), P(float(h), 0)
    foot = P(float(Q(p * p, h)), 0)
    n_pt = P(foot[0], float(key.coef))
    del corner, right_pt, left_pt
    fig = (Fig().path(m_pt, p_pt).path(m_pt, n_pt, p_pt).seg(n_pt, foot)
           .right(n_pt, m_pt, p_pt).right(foot, n_pt, p_pt)
           .name(m_pt, M, 200).name(p_pt, Pp, 340).name(n_pt, N, 90)
           .name(foot, Qp, 270)
           .side(m_pt, n_pt, str(p), out=13).side(n_pt, p_pt, str(q), out=13)
           .render())
    stem = rng.choice([
        f"In the figure above, what is the length of {N}{Qp} ?",
        f"In the figure shown, what is the length of {N}{Qp}?",
    ])
    rationale = (f"The hypotenuse is {h}, and the area {p}({q})/2 also equals "
                 f"{h}({N}{Qp})/2, so {N}{Qp} = {p}({q})/{h} = {plain(key.coef)}.")
    params = {"kind": "lat_altitude_legs", "p": p, "q": q, "h": h}
    return finish("lat.altitude_legs", "the altitude to a hypotenuse", "hard", seed,
                  stem, key, pick(pool, order, wrongs), rng, rationale, unit=unit,
                  figure=fig, params=params, fmt=fmt)


def geometric_mean(rng: random.Random, seed: int, *, mode=None, ad=None, bd=None,
                   ab=None, dc=None, labels=None, fmt="spr", unit=False,
                   wrongs=None) -> Item:
    """The altitude from a right angle makes two triangles similar to the whole.

    That gives two mean proportionals at once: the altitude is the geometric
    mean of the two pieces of the hypotenuse, and each leg is the geometric
    mean of the whole hypotenuse and the piece beside it. `mode="alt"` gives
    the altitude and one piece; `mode="hyp"` gives a leg and the piece next
    to it, which is where the source item's radical comes from.
    """
    mode = mode or rng.choice(["alt", "hyp"])
    A, B, C, D = tuple(labels or rng.choice([("A", "B", "C", "D"),
                                             ("P", "Q", "R", "S"),
                                             ("W", "X", "Y", "Z"),
                                             ("J", "K", "L", "M"),
                                             ("R", "S", "T", "U")]))
    ad = Q(ad) if ad is not None else Q(rng.randrange(2, 61))
    ab_exact = ab2 = None
    if mode == "alt":
        bd = Q(bd) if bd is not None else Q(rng.randrange(2, 41))
        dc = bd * bd / ad
    elif ab is not None:
        ab_exact = ab
        ab2 = ab * ab
        if not ab2.is_rational:
            raise ItemError("that leg length does not square to a rational")
        ac = ab2.coef / ad
        dc = ac - ad
    else:
        dc = Q(dc) if dc is not None else Q(rng.randrange(1, 41))
        ab2 = E(ad * (ad + dc))
        ab_exact = ab2.sqrt()
        if ab_exact is None:
            raise ItemError("that hypotenuse gives a leg that cannot be written down")
    if dc <= 0 or dc > 400 or dc.denominator > 4:
        raise ItemError("the far piece of the hypotenuse is not a usable length")
    if not Q(1, 20) <= ad / dc <= 20:
        # one piece of the hypotenuse two hundred times the other puts the foot
        # of the altitude on top of a vertex, whatever scale it is drawn at
        raise ItemError("the two pieces of the hypotenuse are too unlike to draw")
    key = E(dc)
    height = math.sqrt(float(ad * dc))
    a_pt, c_pt = P(0, 0), P(float(ad + dc), 0)
    d_pt = P(float(ad), 0)
    b_pt = P(float(ad), height)
    fig = (Fig().path(a_pt, c_pt).path(a_pt, b_pt, c_pt).seg(b_pt, d_pt)
           .right(b_pt, a_pt, c_pt).right(d_pt, b_pt, c_pt)
           .name(a_pt, A, 210).name(c_pt, C, 330).name(b_pt, B, 90)
           .name(d_pt, D, 270).render())
    if mode == "alt":
        stem = (f"In the figure above, {B}{D} = {plain(bd)} and {A}{D} = "
                f"{plain(ad)}. What is the length of {D}{C} ?")
        rationale = (f"{B}{D} is the geometric mean of {A}{D} and {D}{C}, so "
                     f"{plain(bd)}\u00b2 = {plain(ad)}({D}{C}) and {D}{C} = "
                     f"{plain(dc)}.")
        pool = {
            "diff": Mis("subtracted the two given lengths",
                        _ok(E, ad - bd) if ad > bd else None),
            "sum": Mis("added the two given lengths", _ok(E, ad + bd)),
            "swapped": Mis("divided the wrong way round", _ok(E, ad * ad / bd)),
        }
    else:
        ac = ad + dc
        stem = (f"In the figure shown, {A}{D} = {plain(ad)} and {A}{B} = "
                f"{ab_exact.plain()}. What is the length of {D}{C}?")
        rationale = (f"{A}{B} is the geometric mean of {A}{D} and {A}{C}, so "
                     f"{A}{C} = {A}{B}\u00b2/{A}{D} = {plain(ac)} and {D}{C} = "
                     f"{plain(ac)} \u2212 {plain(ad)} = {plain(dc)}.")
        pool = {
            "whole": Mis("gave the whole hypotenuse rather than the far piece",
                         _ok(E, ac)),
            "swapped": Mis("divided the wrong way round", _ok(E, ad * ad / ac)),
            "sum": Mis("added the two pieces instead of subtracting",
                       _ok(E, ac + ad)),
        }
    params = {"kind": "lat_geometric_mean", "mode": mode,
              "ad": [ad.numerator, ad.denominator],
              "bd": None if mode != "alt" else [bd.numerator, bd.denominator],
              "ab2": None if mode == "alt" else [ab2.coef.numerator,
                                                 ab2.coef.denominator]}
    return finish("lat.geometric_mean", "the geometric mean in a right triangle",
                  "hard", seed, stem, key, pick(pool, list(pool), wrongs), rng,
                  rationale, unit=unit, figure=fig, params=params, fmt=fmt)


def _sqrt_q(v: Q):
    n = math.isqrt(v.numerator)
    d = math.isqrt(v.denominator)
    if n * n == v.numerator and d * d == v.denominator:
        return Q(n, d)
    return None


# ============================ a line parallel to one leg of a right triangle

def parallel_cut_area(rng: random.Random, seed: int, *, rt=None, lk=None, area=None,
                      labels=None, fmt="spr", unit=False, wrongs=None) -> Item:
    """A segment parallel to one leg cuts the other leg in the same ratio.

    The area gives the leg, the two parallel segments give the ratio, and what
    is left of the leg is the answer.
    """
    R, S, T, L, K = tuple(labels or ("R", "S", "T", "L", "K"))
    rt = rt or 12 * rng.randrange(2, 12)
    ratio_den = rng.randrange(2, 6)
    lk = lk if lk is not None else Q(rt, ratio_den)
    if Q(lk) <= 0 or Q(lk) >= rt:
        raise ItemError("the parallel segment must be shorter than the side it copies")
    st = area and Q(2 * area, rt)
    if st is None:
        st = Q(rng.randrange(20, 200), 2)
        area = Q(rt * st, 2)
    if st <= 0 or st.denominator > 2:
        raise ItemError("this area does not give a usable leg")
    kt = st * (1 - Q(lk) / rt)
    if kt <= 0 or kt.denominator > 6:
        raise ItemError("this draw gives a length the source set would not print")
    key = E(kt)
    pool = {
        "sk": Mis(f"gave {S}{K} rather than {K}{T}", _ok(E, st - kt)),
        "whole": Mis(f"gave the whole of {S}{T}", _ok(E, st)),
        "scaled_lk": Mis("scaled the parallel segment instead of the side it cuts",
                         _ok(E, Q(lk) * (1 - Q(lk) / rt))),
    }
    stem = (f"In triangle {R}{S}{T}, angle {T} is a right angle, point {L} lies on "
            f"{R}{S}, point {K} lies on {S}{T}, and {L}{K} is parallel to {R}{T}. If "
            f"the length of {R}{T} is {plain(rt)} units, the length of {L}{K} is "
            f"{plain(lk)} units, and the area of triangle {R}{S}{T} is "
            f"{plain(area)} square units, what is the length of {K}{T}, in units?")
    rationale = (f"The area gives {S}{T} = 2({plain(area)})/{plain(rt)} = "
                 f"{plain(st)}. Triangle {S}{L}{K} is similar to {S}{R}{T} with "
                 f"ratio {plain(lk)}/{plain(rt)}, so {S}{K} is that share of "
                 f"{plain(st)} and {K}{T} = {plain(kt)}.")
    params = {"kind": "lat_parallel_cut_area", "rt": rt,
              "lk": [Q(lk).numerator, Q(lk).denominator],
              "area": [Q(area).numerator, Q(area).denominator]}
    return finish("lat.parallel_cut_area", "a segment parallel to one leg", "hard",
                  seed, stem, key, pick(pool, list(pool), wrongs), rng, rationale,
                  unit=unit, params=params, fmt=fmt)


# ============================================= an area between two bounds

def area_range(rng: random.Random, seed: int, *, d1=None, d2=None, lo=None, hi=None,
               labels=None, fmt="spr", unit=False, wrongs=None) -> Item:
    """The area pins the height to a few whole numbers; any one of them answers."""
    A, B, C = tuple(labels or ("A", "B", "C"))
    d1 = d1 or rng.randrange(3, 13)
    d2 = d2 or rng.randrange(3, 13)
    base = d1 + d2
    lo = lo or 6 * rng.randrange(4, 20)
    hi = hi or lo + 6 * rng.randrange(1, 4)
    ys = [y for y in range(1, 200) if lo <= Q(base * y, 2) <= hi]
    if not ys or len(ys) > 5:
        raise ItemError("this area range does not pin the height to a few values")
    y = ys[0]
    x = Q(d1 * y, base)
    if x.denominator > 12:
        raise ItemError("this value of x is not one a grid-in accepts")
    key = E(x)
    a_pt, c_pt = P(0, 0), P(base, 0)
    b_pt = P(base, y)
    foot = P(d1, 0)
    top = P(d1, float(x))
    fig = (Fig().path(a_pt, c_pt, b_pt, a_pt).seg(foot, top)
           .right(c_pt, a_pt, b_pt).right(foot, a_pt, top)
           .name(a_pt, A, 200).name(c_pt, C, 340).name(b_pt, B, 90)
           .side(a_pt, foot, str(d1), out=-14).side(foot, c_pt, str(d2), out=-14)
           .side(foot, top, "x", out=-12, italic=True)
           .side(c_pt, b_pt, "y", out=-12, italic=True).render())
    stem = (f"The area of triangle {A}{B}{C} above is at least {lo} but no more than "
            f"{hi}. If y is an integer, what is one possible value of x ?")
    rationale = (f"The area is {base}y/2, so y is {', '.join(str(v) for v in ys)}. "
                 f"The small triangle is similar to {A}{B}{C}, so x = {d1}y/{base}; "
                 f"y = {y} gives x = {plain(x)}.")
    params = {"kind": "lat_area_range", "d1": d1, "d2": d2, "lo": lo, "hi": hi}
    return finish("lat.area_range", "an area between two bounds", "hard", seed, stem,
                  key, [], rng, rationale, unit=unit, figure=fig, params=params,
                  fmt=fmt)
