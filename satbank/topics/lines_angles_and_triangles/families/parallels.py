"""Parallel lines, transversals, and the angles three lines make together.

A transversal item is not a calculation, it is a reading: eight angles are
made, four of one size and four of the other, and the whole question is which
two of the eight are marked. So the marked positions are what the templates
carry -- a spot is (which parallel line, above or below it, left or right of
the transversal) -- and both the printed relationship and the drawn figure come
from those spots and nothing else. That is what makes the figure checkable: a
reader with a protractor can measure the two drawn angles and see for itself
whether they are the equal pair or the supplementary one.
"""

from __future__ import annotations

import math
import random

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text
from ..figures import Fig, P, meet, polar, ray
from ..kit import pick, whole
from .triangles import cosd, finish, sind

__all__ = ["transversal", "transversal_proof", "transversal_inequality",
           "eight_angles", "parallel_triangle", "midsegment_angle",
           "perp_transversal", "two_transversals", "three_lines_point",
           "three_lines_triangle", "big_chain"]

LINE_PAIRS = [("m", "n"), ("ℓ", "k"), ("j", "k"), ("q", "t"), ("r", "s"),
              ("ℓ", "m"), ("a", "b")]
CUTTERS = ["t", "j", "ℓ", "k", "m", "p"]

# a spot is (line, vertical side, side of the transversal); the four angles at
# one crossing are the four spots with that line
THETA_SPOTS = {("above", "right"), ("below", "left")}


def spot_value(spot, theta: float) -> float:
    return theta if (spot[1], spot[2]) in THETA_SPOTS else 180.0 - theta


def _draw_angle(theta: float) -> tuple[float, bool]:
    """The slope the figure is drawn at, and whether that had to be faked.

    Every other figure in this topic is drawn to scale. A transversal is the
    one place where it cannot always be: a 170 degree angle at a crossing is a
    10 degree wedge, and two parallel lines cut at 10 degrees run off the page
    before the second crossing arrives. Those draws are drawn at a legible
    slope and carry the source set's own note, and the *relationship* between
    the two marked spots -- equal or supplementary, which is the whole item --
    survives the change untouched.
    """
    if 24.0 <= theta <= 156.0:
        return theta, False
    return (26.0 if theta < 90 else 154.0), True


def transversal_figure(theta: float, marks, labels, cutter, *, rotate=False,
                       note=False, gap: float = 1.0) -> str:
    """Two parallel lines, one transversal, and the marked angles.

    `marks` is a list of (spot, text, italic). The lower parallel line is
    crossed at the origin; everything else follows from `theta`.
    """
    t = math.radians(theta)
    if abs(math.sin(t)) < 1e-6:
        raise ItemError("a transversal cannot be parallel to the lines it crosses")
    dx = gap * math.cos(t) / math.sin(t)
    low, high = P(0, 0), P(dx, gap)
    xs = [0.0, dx]
    x0, x1 = min(xs) - 0.75, max(xs) + 1.15

    def turn_pt(p):
        return P(-p[1], p[0]) if rotate else P(p[0], p[1])

    fig = Fig()
    for y, lab in ((0.0, labels[1]), (gap, labels[0])):
        a, b = turn_pt(P(x0, y)), turn_pt(P(x1, y))
        fig.seg(a, b).name(b, lab, 90 if rotate else 0)
    ends = (polar(low, theta + 180, 0.62 * gap / abs(math.sin(t))),
            polar(high, theta, 0.62 * gap / abs(math.sin(t))))
    fig.seg(turn_pt(ends[0]), turn_pt(ends[1]))
    fig.name(turn_pt(ends[1]), cutter, 180 if rotate else 90)
    for spot, text, italic in marks:
        v = high if spot[0] == "upper" else low
        h_pt = polar(v, 0.0 if spot[2] == "right" else 180.0, 0.4)
        t_pt = polar(v, theta if spot[1] == "above" else theta + 180.0, 0.4)
        fig.angle(turn_pt(v), turn_pt(h_pt), turn_pt(t_pt), text, italic=italic)
    if note:
        fig.note()
    return fig.render()


# ================================================= one angle from another

def transversal(rng: random.Random, seed: int, *, given=None, given_spot=None,
                ask_spot=None, labels=None, cutter=None, unknown=None, fmt="mcq",
                unit=False, wrongs=None) -> Item:
    """One of the eight angles is printed; another of the eight is asked for.

    The two spots decide everything. Spots on the same side of their own
    parallel line and the same side of the transversal carry the same measure;
    any other pair is supplementary.
    """
    spots = [(ln, v, h) for ln in ("upper", "lower")
             for v in ("above", "below") for h in ("left", "right")]
    given_spot = tuple(given_spot or rng.choice(spots))
    ask_spot = tuple(ask_spot or rng.choice([s for s in spots if s != given_spot]))
    if given_spot == ask_spot:
        raise ItemError("the angle given and the angle asked for are the same one")
    given = given or rng.randrange(15, 166)
    if given in (90,):
        raise ItemError("a right angle makes every one of the eight angles equal")
    theta = float(given) if (given_spot[1], given_spot[2]) in THETA_SPOTS \
        else 180.0 - given
    ans = int(round(spot_value(ask_spot, theta)))
    if not 0 < ans < 180:
        raise ItemError("this pair of spots does not leave a usable measure")
    key = E(ans)
    same = ans == given

    labels = tuple(labels or rng.choice(LINE_PAIRS))
    cutter = cutter or rng.choice([c for c in CUTTERS if c not in labels])
    unknown = unknown or rng.choice(["w", "x", "a", "b"])

    pool = {
        "supplement": Mis("used the supplementary angle where the two marked angles "
                          "are equal" if same else
                          "treated the two marked angles as equal when they are "
                          "supplementary", whole(180 - ans)),
        "complement": Mis("subtracted the given measure from 90 degrees instead of "
                          "180", whole(90 - given)),
        "plus90": Mis("added 90 degrees to the given measure instead of subtracting "
                      "it from 180", whole(given + 90)),
        "lead2": Mis("copied only the leading two digits of the given measure",
                     whole(int(str(given)[:2])) if given >= 100 else None),
        "drop100": Mis("dropped the hundreds digit of the given measure",
                       whole(given - 100) if given >= 100 else None),
        "from200": Mis("subtracted the given measure from 200 rather than from a "
                       "straight angle", whole(200 - given) if given > 20 else None),
        "half": Mis("halved the given measure", whole(given / 2)),
        "double": Mis("doubled the given measure", whole(2 * given)),
    }
    order = ["supplement", "complement", "plus90", "half", "from200", "double"]

    theta_draw, faked = _draw_angle(theta)
    marks = [(given_spot, f"{given}°", False),
             (ask_spot, f"{unknown}°", True)]
    fig = transversal_figure(theta_draw, marks, labels, cutter, note=faked)

    same_crossing = given_spot[0] == ask_spot[0]
    where = ("at the same intersection" if same_crossing else
             "at the two intersections")
    rel = ("equal" if same else "supplementary")
    stem = rng.choice([
        f"In the figure, line {labels[0]} is parallel to line {labels[1]}. What is "
        f"the value of {unknown}?",
        f"In the figure above, lines {labels[0]} and {labels[1]} are parallel. What "
        f"is the value of {unknown} ?",
    ])
    rationale = (f"The marked angles {where} are {rel}, so {unknown} = "
                 f"{'the given ' + str(given) if same else '180 − ' + str(given)}"
                 f" = {ans}.")
    params = {"kind": "lat_transversal", "given": given,
              "given_spot": list(given_spot), "ask_spot": list(ask_spot)}
    return finish("lat.transversal", "parallel lines cut by a transversal", "easy",
                  seed, stem, key, pick(pool, order, wrongs), rng, rationale,
                  unit=unit, figure=fig, params=params, fmt=fmt)


# ========================================= what would make the lines parallel

def transversal_proof(rng: random.Random, seed: int, *, given=None, labels=None,
                      cutter=None, names=None) -> Item:
    """Two lines are cut by a transversal; what would prove them parallel?

    Only a fact about an angle at the *other* crossing can settle it. The three
    wrong options are all true of the figure already -- they say something
    about angles at one crossing, which no line through the other can change.
    """
    given = given or rng.randrange(20, 161)
    if given == 90:
        raise ItemError("a right angle makes the answer unreadable")
    labels = tuple(labels or rng.choice([p for p in LINE_PAIRS if len(p[0]) == 1]))
    cutter = cutter or rng.choice([c for c in CUTTERS if c not in labels])
    w, x, y, z = tuple(names or ("w", "x", "y", "z"))
    up, low = "upper", "lower"
    marks = [((up, "above", "right"), f"{w}°", True),
             ((up, "below", "left"), f"{x}°", True),
             ((low, "above", "right"), f"{given}°", False),
             ((low, "below", "left"), f"{y}°", True),
             ((low, "below", "right"), f"{z}°", True)]
    theta_draw, faked = _draw_angle(float(given))
    fig = transversal_figure(theta_draw, marks, labels, cutter, note=faked)

    key = f"{w} = {given}"
    wrong = [
        Mis(f"{x} is vertical to {w}, so this says the two lines make the "
            f"supplementary angle, not the equal one", f"{x} = {180 - given}"),
        Mis(f"{y} is vertical to the {given}° angle at the same crossing, so "
            f"this is already true and says nothing about line {labels[0]}",
            f"{y} = {given}"),
        Mis(f"{z} and the {given}° angle are a linear pair at the same "
            f"crossing, so this is already true whatever line {labels[0]} does",
            f"{z} = {180 - given}"),
    ]
    stem = (f"In the figure shown, line {cutter} intersects lines {labels[0]} and "
            f"{labels[1]}. Which additional piece of information is sufficient to "
            f"prove that lines {labels[0]} and {labels[1]} are parallel?")
    rationale = (f"{w}° and the {given}° angle are corresponding angles at "
                 f"the two crossings, so the lines are parallel exactly when "
                 f"{w} = {given}.")
    choices, reasons, letter = assemble_text(key, wrong, rng)
    params = {"kind": "lat_transversal_proof", "given": given,
              "names": [w, x, y, z]}
    return Item("lat.transversal_proof", "proving two lines parallel", "easy", seed,
                stem, "mcq", E(given), letter, rationale, choices, reasons,
                list(choices), figure=fig, params=params)


def transversal_inequality(rng: random.Random, seed: int, *, bound=None,
                           labels=None, cutter=None, names=None) -> Item:
    """The two marked angles are supplementary, so a bound on one bounds the other."""
    bound = bound or rng.randrange(20, 161)
    if bound == 90:
        raise ItemError("a right angle leaves the two options indistinguishable")
    labels = tuple(labels or rng.choice(LINE_PAIRS))
    cutter = cutter or rng.choice([c for c in CUTTERS if c not in labels])
    x, y = tuple(names or ("x", "y"))
    other = 180 - bound
    marks = [(("upper", "above", "right"), f"{x}°", True),
             (("lower", "below", "right"), f"{y}°", True)]
    theta_draw, _ = _draw_angle(float(rng.randrange(30, 151)))
    fig = transversal_figure(theta_draw, marks, labels, cutter, rotate=True)

    key = f"{x} > {other}"
    wrong = [
        Mis(f"reversed the inequality: a smaller {y} forces a larger {x}",
            f"{x} < {other}"),
        Mis(f"{x} + {y} is exactly 180, so it is never less than 180",
            f"{x} + {y} < 180"),
        Mis(f"{x} + {y} is exactly 180, so it is never more than 180",
            f"{x} + {y} > 180"),
    ]
    stem = (f"In the figure shown, lines {labels[0]} and {labels[1]} are parallel, "
            f"and line {cutter} intersects both lines. If {y} < {bound}, which of "
            f"the following must be true?")
    rationale = (f"The two marked angles are supplementary, so {x} = 180 − {y}. "
                 f"A value of {y} below {bound} therefore puts {x} above {other}.")
    choices, reasons, letter = assemble_text(key, wrong, rng)
    params = {"kind": "lat_transversal_inequality", "bound": bound,
              "names": [x, y]}
    return Item("lat.transversal_inequality", "parallel lines and an inequality",
                "medium", seed, stem, "mcq", E(other), letter, rationale, choices,
                reasons, list(choices), figure=fig, params=params)


# ============================================= the eight angles, all at once

def _lin(coef: int, const: int, var: str) -> str:
    minus = "−"
    if coef == 0:
        return f"{minus if const < 0 else ''}{abs(const):,}"
    head = (minus if coef < 0 else "") + ("" if abs(coef) == 1 else f"{abs(coef):,}") + var
    if const == 0:
        return head
    return f"{head} {'+' if const > 0 else minus} {abs(const):,}"


def eight_angles(rng: random.Random, seed: int, *, m=None, c=None, var="x",
                 wrongs=None) -> Item:
    """Four of the eight angles are summed; which sum is impossible?

    Four of the eight equal the given measure and four equal its supplement,
    so a sum of four of them is one of exactly five expressions -- and the item
    is a fifth expression that looks like one of them and is not.
    """
    m = m or rng.randrange(3, 13)
    c = c or rng.randrange(40, 401)
    given = _lin(m, -c, var)
    reach = {(4 * m, -4 * c): "all four of the angles equal to the given one",
             (2 * m, 180 - 2 * c): "three angles equal to the given one and one "
                                   "equal to its supplement",
             (0, 360): "two angles of each size, which always make a full turn",
             (-2 * m, 540 + 2 * c): "one angle equal to the given one and three "
                                    "equal to its supplement",
             (-4 * m, 720 + 4 * c): "all four angles equal to the supplement of the "
                                    "given one"}
    key_pair = (-2 * m, 540 + 4 * c)
    if key_pair in reach:
        raise ItemError("the value picked for the key is in fact reachable")
    key_text = _lin(*key_pair, var)
    pool = {
        "all_given": Mis(reach[(4 * m, -4 * c)], _lin(4 * m, -4 * c, var)),
        "three_given": Mis(reach[(2 * m, 180 - 2 * c)], _lin(2 * m, 180 - 2 * c, var)),
        "two_each": Mis(reach[(0, 360)], _lin(0, 360, var)),
        "one_given": Mis(reach[(-2 * m, 540 + 2 * c)], _lin(-2 * m, 540 + 2 * c, var)),
        "all_supp": Mis(reach[(-4 * m, 720 + 4 * c)], _lin(-4 * m, 720 + 4 * c, var)),
    }
    order = ["three_given", "all_supp", "two_each", "all_given", "one_given"]
    stem = (f"A line intersects two parallel lines, forming four acute angles and "
            f"four obtuse angles. The measure of one of these eight angles is "
            f"({given})°. The sum of the measures of four of the eight angles "
            f"is k°. Which of the following could NOT be equivalent to k, for "
            f"all values of {var}?")
    rationale = ("Four of the eight angles measure " + given + " and four measure "
                 "180 − (" + given + "), so a sum of four of them is "
                 + ", ".join(_lin(*p, var) for p in reach) + " and nothing else.")
    choices, reasons, letter = assemble_text(key_text, pick(pool, order, wrongs), rng)
    params = {"kind": "lat_eight_angles", "m": m, "c": c, "var": var}
    return Item("lat.eight_angles", "the eight angles at two parallel lines", "hard",
                seed, stem, "mcq", E(1), letter, rationale, choices, reasons,
                list(choices), params=params)


# ======================================== a triangle straddling two parallels

def parallel_triangle(rng: random.Random, seed: int, *, y=None, z=None,
                      labels=None, fmt="mcq", unit=False, wrongs=None) -> Item:
    """A triangle whose base is one parallel line and whose apex is above the other.

    The line between them cuts the two sides, and the angle it makes with the
    right-hand side is the same as the triangle's own angle there, so the apex
    is what is left of 180.
    """
    y = y or rng.randrange(15, 91)
    z = z or rng.randrange(15, 121)
    x = 180 - y - z
    if x < 15 or y < 15 or z < 15:
        raise ItemError("one angle of this triangle is too small to mark")
    key = E(x)
    up, low = tuple(labels or rng.choice([("ℓ", "m"), ("j", "k"), ("m", "n"),
                                          ("q", "t")]))
    pool = {
        "supp_z": Mis("subtracted only the angle at the upper line from 180 degrees",
                      whole(180 - z)),
        "supp_y": Mis("subtracted only the angle at the lower line from 180 degrees",
                      whole(180 - y)),
        "sum": Mis("added the two given measures instead of subtracting them from "
                   "180 degrees", whole(y + z)),
        "right": Mis("assumed the angle at the top of the triangle is a right angle",
                     whole(90)),
        "diff": Mis("subtracted one given measure from the other", whole(abs(y - z))),
    }
    order = ["supp_z", "sum", "right", "supp_y", "diff"]

    left, right, apex = (lambda t: t)(__triangle(y, z))
    h = apex[1] * 0.44
    cut_l = meet(ray(left, y), ray(P(0, h), 0))
    cut_r = meet(ray(right, 180 - z), ray(P(0, h), 0))
    span = (min(left[0], cut_l[0]) - 0.28, max(right[0], cut_r[0]) + 0.34)
    fig = (Fig().path(left, apex, right).path(left, right)
           .seg(P(span[0], 0), P(span[1], 0))
           .seg(P(span[0], h), P(span[1], h))
           .name(P(span[1], h), up, 0).name(P(span[1], 0), low, 0)
           .angle(apex, left, right, "x°")
           .angle(cut_r, P(span[0], h), apex, "z°")
           .angle(left, right, apex, "y°").render())
    stem = (f"In the figure above, lines {up} and {low} are parallel, y = {y}, and "
            f"z = {z}. What is the value of x ?")
    rationale = (f"z is the same angle the triangle makes at the lower line, so the "
                 f"triangle has angles x, {y} and {z}: x = 180 − {y} − {z} "
                 f"= {x}.")
    params = {"kind": "lat_parallel_triangle", "y": y, "z": z}
    return finish("lat.parallel_triangle", "a transversal pair through a triangle",
                  "easy", seed, stem, key, pick(pool, order, wrongs), rng, rationale,
                  unit=unit, figure=fig, params=params, fmt=fmt)


def __triangle(y, z):
    from ..figures import triangle_pts
    return triangle_pts(y, z, 1.0)


def midsegment_angle(rng: random.Random, seed: int, *, d=None, c=None, labels=None,
                     fmt="mcq", unit=True, wrongs=None) -> Item:
    """A segment parallel to one side of a triangle cuts the other two.

    The small triangle at the apex has the same angles as the whole one, so the
    angle at the base is what the two given angles leave.
    """
    A, B, C, D, Ee = tuple(labels or ("A", "B", "C", "D", "E"))
    d = d or rng.randrange(20, 121)
    c = c or rng.randrange(20, 121)
    ans = 180 - d - c
    if ans < 15 or d < 15 or c < 15:
        raise ItemError("one angle of this triangle is too small to mark")
    key = E(ans)
    pool = {
        "given_d": Mis(f"gave the angle at {D}, which matches the angle at {Ee}, not "
                       f"the one at {A}", whole(d)),
        "given_c": Mis(f"gave the angle at {C} rather than the angle at {A}",
                       whole(c)),
        "sum": Mis("added the two given measures instead of subtracting them from "
                   "180 degrees", whole(d + c)),
        "supp_d": Mis(f"took the supplement of the angle at {D}", whole(180 - d)),
    }
    order = ["given_d", "given_c", "sum", "supp_d"]
    a_pt, e_pt, c_pt = __triangle(ans, d)
    b_pt = _along(c_pt, a_pt, 0.45)
    d_pt = _along(c_pt, e_pt, 0.45)
    fig = (Fig().path(a_pt, e_pt).path(a_pt, c_pt, e_pt).seg(b_pt, d_pt)
           .name(a_pt, A, 200).name(e_pt, Ee, 340).name(c_pt, C, 90)
           .name(b_pt, B, 175).name(d_pt, D, 5)
           .angle(d_pt, b_pt, c_pt, f"{d}°", r=17, italic=False)
           .angle(c_pt, a_pt, e_pt, f"{c}°", italic=False).render())
    stem = (f"In the figure above, segments {A}{Ee} and {B}{D} are parallel. If angle "
            f"{B}{D}{C} measures {d}° and angle {A}{C}{Ee} measures {c}°, "
            f"what is the measure of angle {C}{A}{Ee} ?")
    rationale = (f"{B}{D} is parallel to {A}{Ee}, so angle {D}{B}{C} = 180 − {d} "
                 f"− {c} = {ans}°, and angle {C}{A}{Ee} matches it.")
    params = {"kind": "lat_midsegment_angle", "d": d, "c": c}
    return finish("lat.midsegment_angle", "a segment parallel to one side", "medium",
                  seed, stem, key, pick(pool, order, wrongs), rng, rationale,
                  unit=unit, figure=fig, params=params, fmt=fmt)


def _along(a, b, f):
    return P(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)


# ================================ a perpendicular among the two transversals

def perp_transversal(rng: random.Random, seed: int, *, given=None, labels=None,
                     fmt="mcq", unit=False, wrongs=None) -> Item:
    """Two transversals make equal angles with the parallels; one more is square to them.

    The angle between a transversal and a perpendicular is whatever is left of
    a right angle, so the figure's five lines come down to 90 minus one angle.
    """
    given = given or rng.randrange(105, 166)
    a = 180 - given
    b = 90 - a
    if not (15 <= a <= 75):
        raise ItemError("this slope makes the perpendicular's angle unreadable")
    key = E(b)
    m_lab, n_lab = tuple(labels or rng.choice([("m", "n"), ("ℓ", "k"),
                                               ("q", "t"), ("a", "b"),
                                               ("s", "t"), ("j", "k")]))
    j, k, el = [c for c in ("j", "k", "ℓ", "p", "r") if c not in (m_lab, n_lab)][:3]
    pool = {
        "a_itself": Mis("gave the angle the transversal makes with the parallel "
                        "lines instead", whole(a)),
        "half_given": Mis("halved the given measure", whole(given / 2)),
        "apex": Mis("gave the angle between the two transversals where they meet",
                    whole(180 - 2 * a)),
        "supp_b": Mis("took the supplement of the angle asked for", whole(180 - b)),
    }
    order = ["a_itself", "half_given", "apex", "supp_b"]

    top = P(0, 1.6)
    j_ray, k_ray = ray(top, 180 - a), ray(top, a)
    n_line, m_line = ray(P(0, 0), 0), ray(P(0, 1.0), 0)
    jn, kn = meet(j_ray, n_line), meet(k_ray, n_line)
    jm, km = meet(j_ray, m_line), meet(k_ray, m_line)
    x0, x1 = min(kn[0], km[0]) - 0.45, jn[0] + 0.5
    fig = (Fig().seg(P(x0, 0), P(x1, 0)).seg(P(x0, 1.0), P(x1, 1.0))
           .seg(polar(top, a, 0.4), polar(top, a + 180, 1.45 * 1.6))
           .seg(polar(top, 180 - a, 0.4), polar(top, -a, 1.45 * 1.6))
           .seg(P(jn[0], -0.35), P(jn[0], 1.45))
           .name(P(x1, 1.0), m_lab, 0).name(P(x1, 0), n_lab, 0)
           .name(polar(top, 180 - a, 0.4), j, 110)
           .name(polar(top, a, 0.4), k, 70)
           .name(P(jn[0], 1.45), el, 90)
           .right(P(jn[0], 1.0), P(x1, 1.0), P(jn[0], 1.45))
           .angle(km, P(x0, 1.0), polar(km, -a, 0.4), f"a°", r=17)
           .angle(jm, P(x1, 1.0), polar(jm, a + 180, 0.4), f"a°", r=17)
           .angle(kn, P(x0, 0), polar(kn, a, 0.4), f"{given}°", r=17,
                  italic=False)
           .angle(jn, P(jn[0], 1.45), polar(jn, 180 - a, 0.4), "b°", r=17)
           .render())
    stem = rng.choice([
        f"In the figure above, lines {m_lab} and {n_lab} are parallel. What is the "
        f"value of b ?",
        f"In the figure shown, line {m_lab} is parallel to line {n_lab}. What is the "
        f"value of b?",
    ])
    rationale = (f"The transversals make an angle of 180 − {given} = {a}° "
                 f"with the parallel lines, and line {el} is perpendicular to them, "
                 f"so b = 90 − {a} = {b}.")
    params = {"kind": "lat_perp_transversal", "given": given}
    return finish("lat.perp_transversal", "a perpendicular among transversals",
                  "easy", seed, stem, key, pick(pool, order, wrongs), rng, rationale,
                  unit=unit, figure=fig, params=params, fmt=fmt)


# ================================ two transversals and a bisected exterior angle

def two_transversals(rng: random.Random, seed: int, *, a=None, b=None, labels=None,
                     fmt="spr", unit=False, wrongs=None) -> Item:
    """Two lines cross above a pair of parallels; a ray splits the angle below.

    The triangle the three lines make fixes the angle at the lower crossing,
    and the two angles marked equal there share what is left of a straight
    angle.
    """
    a = a or rng.randrange(20, 91)
    b = b or rng.randrange(95, 161)
    c = 180 - b
    third = 180 - a - c
    if c < 15 or third < 15 or a < 15:
        raise ItemError("this triangle has an angle too small to draw")
    total = a + c
    key = E(total, 0) / E(2)
    if not key.is_rational:
        raise ItemError("this angle cannot be entered in a grid-in")

    apex = P(0, 2.0)
    s_ray, r_ray = ray(apex, c + 180), ray(apex, (c + a) - 180)
    q_line, t_line = ray(P(0, 1.0), 0), ray(P(0, 0), 0)
    sq, st = meet(s_ray, q_line), meet(s_ray, t_line)
    rq, rt = meet(r_ray, q_line), meet(r_ray, t_line)
    x0 = min(st[0], sq[0]) - 0.5
    x1 = max(rt[0], rq[0]) + 0.6
    bis = 180.0 + float(key.coef)
    q_lab, t_lab = tuple(labels or ("q", "t"))
    fig = (Fig().seg(P(x0, 1.0), P(x1, 1.0)).seg(P(x0, 0), P(x1, 0))
           .seg(polar(apex, c, 0.55), polar(st, c + 180, 0.5))
           .seg(polar(apex, c + a, 0.55), polar(rt, (c + a) - 180, 0.5))
           .seg(rt, polar(rt, bis, 0.55))
           .name(P(x0, 1.0), q_lab, 180).name(P(x0, 0), t_lab, 180)
           .name(polar(apex, c, 0.55), "s", 90).name(polar(apex, c + a, 0.55), "r", 90)
           .angle(apex, polar(apex, c, 0.4), polar(apex, c + a, 0.4), "a°", r=18)
           .angle(sq, P(x0, 1.0), polar(sq, c, 0.4), "b°", r=18)
           .angle(rt, P(x0, 0), polar(rt, bis, 0.4), "w°", r=19)
           .angle(rt, polar(rt, bis, 0.4), polar(rt, (c + a) - 180, 0.4), "w°",
                  r=19)
           .render())
    stem = (f"In the figure, parallel lines {q_lab} and {t_lab} are intersected by "
            f"lines r and s. If a = {a} and b = {b}, what is the value of w?")
    rationale = (f"s meets {t_lab} at 180 − {b} = {c}°, so the triangle's "
                 f"angle at the lower crossing is 180 − {a} − {c} = "
                 f"{third}°; the two w° angles share its supplement, "
                 f"{total}°.")
    params = {"kind": "lat_two_transversals", "a": a, "b": b}
    pool = {
        "whole": Mis("gave the whole angle instead of half of it", whole(total)),
        "triangle": Mis("gave the triangle's own angle at the lower crossing",
                        whole(third)),
        "half_third": Mis("halved the triangle's angle rather than its supplement",
                          whole(third / 2)),
    }
    return finish("lat.two_transversals", "two transversals across parallel lines",
                  "hard", seed, stem, key,
                  pick(pool, ["whole", "triangle", "half_third"], wrongs), rng,
                  rationale, unit=unit, figure=fig, params=params, fmt=fmt)


# ================================================ three lines, one crossing

def three_lines_point(rng: random.Random, seed: int, *, x=None, y=None, labels=None,
                      fmt="mcq", unit=False, wrongs=None) -> Item:
    """Three lines through one point: the three marked angles make a straight angle."""
    x = x or rng.randrange(20, 111)
    y = y or rng.randrange(20, 111)
    z = 180 - x - y
    if z < 15 or x < 15 or y < 15:
        raise ItemError("one of the three angles is too small to mark")
    key = E(z)
    pt = labels or rng.choice(["P", "Q", "O", "V", "T"])
    pool = {
        "sum": Mis("added the two given measures instead of subtracting them from "
                   "180 degrees", whole(x + y)),
        "leftover": Mis("took what was left of a full turn after counting each "
                        "given angle twice, forgetting that the third angle also "
                        "occurs twice", whole(360 - 2 * x - 2 * y)),
        "half": Mis("halved the angle that was left", whole(z / 2)),
        "supp": Mis("took the supplement of the angle asked for", whole(180 - z)),
    }
    order = ["sum", "leftover", "half", "supp"]
    o = P(0, 0)
    dirs = (0.0, float(z), float(180 - x))
    fig = Fig()
    for d in dirs:
        fig.seg(polar(o, d, 1.0), polar(o, d + 180, 1.0))
    fig.name(o, pt, 100, gap=12)
    fig.angle(o, polar(o, 180, .5), polar(o, 180 - x, .5), "x°", r=24)
    fig.angle(o, polar(o, 0, .5), polar(o, z, .5), "z°", r=24)
    fig.angle(o, polar(o, 180 + z, .5), polar(o, 360 - x, .5), "y°", r=24)
    stem = (f"In the figure, three lines intersect at point {pt}. If x = {x} and "
            f"y = {y}, what is the value of z ?")
    rationale = (f"The three marked angles together make a straight angle, so "
                 f"z = 180 − {x} − {y} = {z}.")
    params = {"kind": "lat_three_lines_point", "x": x, "y": y}
    return finish("lat.three_lines_point", "angles at a point", "easy", seed, stem,
                  key, pick(pool, order, wrongs), rng, rationale, unit=unit,
                  figure=fig.render(), params=params, fmt=fmt)


def three_lines_triangle(rng: random.Random, seed: int, *, p=None, q=None,
                         labels=None, fmt="spr", unit=False, wrongs=None) -> Item:
    """Three lines that make a triangle, with two of the outside angles given."""
    p = p or rng.randrange(95, 166)
    q = q or rng.randrange(15, 80)
    at_sr, at_rt = 180 - p, q
    at_st = 180 - at_sr - at_rt
    x = 180 - at_st
    if min(at_sr, at_rt, at_st) < 14 or x >= 180:
        raise ItemError("this triangle has an angle too small to mark")
    key = E(x)
    r_l, s_l, t_l = tuple(labels or ("r", "s", "t"))
    delta, gamma = 90.0 - p, 90.0 - p + q
    s_line = ray(P(0, 0), 90.0)
    r_line, t_line = ray(P(0, 1.0), delta), ray(P(0, 0), gamma)
    rt = meet(r_line, t_line)
    sr, st = P(0, 1.0), P(0, 0)
    fig = (Fig().seg(P(0, -0.45), P(0, 1.45))
           .seg(polar(sr, delta + 180, 0.45), polar(rt, delta, 0.22))
           .seg(polar(st, gamma + 180, 0.45), polar(rt, gamma, 0.55))
           .name(polar(rt, delta, 0.22), r_l, 40)
           .name(polar(rt, gamma, 0.55), t_l, 330)
           .name(P(0, 1.45), s_l, 90)
           .angle(sr, P(0, 1.45), polar(sr, delta, 0.4), f"{p}°", r=19,
                  italic=False)
           .angle(rt, polar(rt, delta + 180, 0.4), polar(rt, gamma + 180, 0.4),
                  f"{q}°", r=26, italic=False)
           .angle(st, P(0, 1.45), polar(st, gamma + 180, 0.4), "x°", r=19)
           .render())
    stem = (f"Intersecting lines {r_l}, {s_l}, and {t_l} are shown below. What is the "
            f"value of x ?")
    rationale = (f"The three lines make a triangle with angles 180 − {p} = "
                 f"{at_sr}°, {q}° and {at_st}°, and x is the "
                 f"supplement of the last of those: x = {x}.")
    params = {"kind": "lat_three_lines_triangle", "p": p, "q": q}
    pool = {
        "inside": Mis("gave the triangle's own angle rather than the marked one",
                      whole(at_st)),
        "supp_p": Mis("subtracted the given measure from 180 and stopped",
                      whole(at_sr)),
        "sum": Mis("added the two given measures", whole(p + q)),
    }
    return finish("lat.three_lines_triangle", "three intersecting lines", "hard",
                  seed, stem, key, pick(pool, ["inside", "supp_p", "sum"], wrongs),
                  rng, rationale, unit=unit, figure=fig, params=params, fmt=fmt)


# ======================================= a long chain hung off one line segment

def big_chain(rng: random.Random, seed: int, *, at_q=None, at_x=None, at_w=None,
              at_t=None, labels=None, fmt="spr", unit=False, wrongs=None) -> Item:
    """Two triangles hang below one segment and cross each other.

    The first triangle gives the angle its long side makes with the segment;
    the crossing turns that into the angle the second triangle's side makes;
    and the angle sum of the second triangle finishes it.
    """
    Pl, Ql, Rl, Sl, Tl, Vl, Xl, Ul, Wl = tuple(
        labels or ("P", "Q", "R", "S", "T", "V", "X", "U", "W"))
    at_q = at_q or rng.randrange(25, 71)
    at_x = at_x or rng.randrange(40, 111)
    at_s = 180 - at_q - at_x
    at_w = at_w or rng.randrange(at_s + 14, min(at_s + 75, 160))
    slope = at_w - at_s
    at_t = at_t or rng.randrange(140, 171)
    foot = 180 - at_t
    ans = 180 - slope - foot
    if min(at_s, slope, foot, ans) < 12 or at_q < 12:
        raise ItemError("this chain leaves an angle too small to draw")
    key = E(ans)

    q_pt, s_pt = P(0, 0), P(1.0, 0)
    x_pt = meet(ray(q_pt, -at_q), ray(s_pt, at_s - 180))
    w_pt = P(s_pt[0] + (x_pt[0] - s_pt[0]) * 0.45,
             s_pt[1] + (x_pt[1] - s_pt[1]) * 0.45)
    back = -w_pt[1] / sind(slope)
    r_pt = P(w_pt[0] - back * cosd(slope), 0.0)
    u_pt = polar(w_pt, -slope, 0.42)
    fwd = -u_pt[1] / sind(foot)
    t_pt = P(u_pt[0] + fwd * cosd(foot), 0.0)
    if not (0.02 < r_pt[0] < s_pt[0] - 0.05) or t_pt[0] < s_pt[0] + 0.08:
        raise ItemError("the points on the segment would not fall in order")
    p_pt, v_pt = P(min(q_pt[0], r_pt[0]) - 0.25, 0), P(t_pt[0] + 0.25, 0)
    fig = (Fig().seg(p_pt, v_pt).path(q_pt, x_pt, s_pt).path(r_pt, u_pt, t_pt)
           .name(p_pt, Pl, 95).name(q_pt, Ql, 95).name(r_pt, Rl, 95)
           .name(s_pt, Sl, 95).name(t_pt, Tl, 95).name(v_pt, Vl, 95)
           .name(x_pt, Xl, 250).name(u_pt, Ul, 270).name(w_pt, Wl, 20)
           .render())
    stem = (f"In the figure shown, points {Ql}, {Rl}, {Sl}, and {Tl} lie on line "
            f"segment {Pl}{Vl}, and line segment {Rl}{Ul} intersects line segment "
            f"{Sl}{Xl} at point {Wl}. The measure of ∠{Sl}{Ql}{Xl} is {at_q}"
            f"°, the measure of ∠{Sl}{Xl}{Ql} is {at_x}°, the measure "
            f"of ∠{Sl}{Wl}{Ul} is {at_w}°, and the measure of "
            f"∠{Vl}{Tl}{Ul} is {at_t}°. What is the measure, in degrees, "
            f"of ∠{Tl}{Ul}{Rl}?")
    rationale = (f"Triangle {Ql}{Xl}{Sl} gives ∠{Ql}{Sl}{Xl} = {at_s}°, so "
                 f"{Rl}{Ul} leaves {Pl}{Vl} at {at_w} − {at_s} = {slope}°; "
                 f"∠{Ul}{Tl}{Rl} = 180 − {at_t} = {foot}°, and the "
                 f"angle sum of triangle {Rl}{Tl}{Ul} leaves {ans}°.")
    params = {"kind": "lat_big_chain", "at_q": at_q, "at_x": at_x, "at_w": at_w,
              "at_t": at_t}
    pool = {
        "slope": Mis(f"stopped at the angle {Rl}{Ul} makes with the segment",
                     whole(slope)),
        "foot": Mis(f"gave the angle at {Tl} instead of the angle at {Ul}",
                    whole(foot)),
        "at_s": Mis(f"used ∠{Ql}{Sl}{Xl} as the angle {Rl}{Ul} makes with the "
                    "segment", whole(180 - at_s - foot)),
    }
    return finish("lat.big_chain", "a chain of angles along one segment", "hard",
                  seed, stem, key, pick(pool, ["slope", "foot", "at_s"], wrongs),
                  rng, rationale, unit=unit, figure=fig, params=params, fmt=fmt)
