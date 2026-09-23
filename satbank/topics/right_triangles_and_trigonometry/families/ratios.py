"""The three ratios, and the mistakes that have names.

Every distractor in this family is a *named* error a teacher would recognise --
used cosine where sine is needed, took the reciprocal, used the adjacent leg as
the hypotenuse, found the complement's ratio, answered the angle when the
question asked for the ratio -- and the pools are keyed by those names so a
source item can ask for the three College Board printed, in printed order.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E, Exact
from ....item import Item, ItemError, Mis, assemble, assemble_text, gridin_mistakes
from ..figures import right_triangle
from ..kit import TRIPLES, attempt, exact_leg, pick, ratio_text

__all__ = ["trig_ratio", "ratio_to_side", "cofunction_match", "cofunction_angles",
           "complement_tangent", "complement_ratio", "split_right_angle"]

MINUS = "\N{MINUS SIGN}"
FN_NAME = {"sin": "sine", "cos": "cosine", "tan": "tangent"}
TRIOS = (("A", "B", "C"), ("P", "Q", "R"), ("R", "S", "T"), ("X", "Y", "Z"),
         ("D", "E", "F"), ("J", "K", "L"), ("L", "M", "N"), ("U", "V", "W"),
         ("G", "H", "K"), ("M", "N", "P"))
ANGLE_LETTERS = ("x", "y", "z", "a", "b", "t", "w")


def _rational(v):
    """A ratio only goes on the page when it is a ratio a student can write."""
    return v if isinstance(v, Exact) and v.is_rational and float(v) > 0 else None


# ================================================= a ratio read off a triangle

def trig_ratio(rng: random.Random, seed: int, *, hyp=None, leg=None, mode=None,
               fn=None, at=None, names=None, letter=None, layout=None, fmt=None,
               note=True, wrongs=None) -> Item:
    """A right triangle with two sides known; find sin, cos or tan of an angle.

    `mode="two_sides"` labels one leg and the hypotenuse and asks for the ratio
    those two make; `mode="third_side"` states the *other* leg as a radical, so
    the student has to find the labelled one first; `mode="triple"` labels all
    three and will ask for any of the six ratios.
    """
    c = int(hyp if hyp is not None else rng.randint(5, 90))
    q_leg = int(leg if leg is not None else rng.randint(2, c - 1))
    p_leg = exact_leg(c, q_leg)                     # the other leg, exactly
    mode = mode or rng.choice(["two_sides", "two_sides", "triple", "third_side"])
    if mode == "triple" and not p_leg.is_integer:
        raise ItemError("all three sides are labelled, so all three must be whole")
    layout = layout or rng.choice(["left", "right"])
    fmt = fmt or ("spr" if rng.random() < 0.3 else "mcq")
    hyp_e, q_e = E(c), E(q_leg)
    if not 0.125 <= float(p_leg) / q_leg <= 8.0:
        raise ItemError("a triangle this thin cannot be drawn legibly")

    # the angle at p is opposite the leg q, and the angle at q opposite the leg p
    ratios = {
        ("sin", "p"): q_e / hyp_e, ("cos", "p"): p_leg / hyp_e,
        ("tan", "p"): q_e / p_leg,
        ("sin", "q"): p_leg / hyp_e, ("cos", "q"): q_e / hyp_e,
        ("tan", "q"): p_leg / q_e,
    }
    if mode == "triple":
        at = at or rng.choice(["p", "q"])
        fn = fn or rng.choice(["sin", "cos", "tan"])
    else:
        at, fn = (at or "p"), (fn or "sin")
        if (fn, at) not in (("sin", "p"), ("cos", "q")):
            raise ItemError("only the ratio of the two labelled sides can be asked for")
    key = ratios[(fn, at)]
    if not key.is_rational:
        raise ItemError("this ratio is not a ratio the student can write down")

    # ---------------------------------------------------------- the figure
    trio = names or rng.choice(TRIOS)
    use_names = mode == "third_side" or (mode == "triple" and names is not False) \
        or (names is not None and names is not False)
    mark = None if use_names else (letter or rng.choice(ANGLE_LETTERS))
    sides = {"hyp": str(c)}
    if mode == "two_sides":
        sides["q"] = str(q_leg)
    elif mode == "triple":
        sides["q"] = str(q_leg)
        sides["p"] = p_leg.plain()
    named = {"rt": trio[0], "p": trio[1], "q": trio[2]} if use_names else None
    angles = None if use_names else {at: f"{mark}°"}
    fig = right_triangle(float(p_leg), float(q_leg), layout=layout, sides=sides,
                         names=named, angles=angles, note=note)

    # ----------------------------------------------------------- the stem
    if use_names:
        spoken = f"{fn} {trio[1] if at == 'p' else trio[2]}"
    else:
        spoken = f"{fn} {mark}°"
    if mode == "third_side":
        side_name = "".join(sorted((trio[0], trio[1])))
        lead = (f"In the triangle shown, {side_name} = {p_leg.plain()}. "
                f"What is the value of {spoken} ?")
        stem = lead
    else:
        stem = rng.choice([
            f"In the right triangle shown, what is the value of {spoken} ?",
            f"In the triangle shown, what is the value of {spoken} ?",
            f"In the figure above, what is the value of {spoken} ?",
        ])

    # --------------------------------------------------------- the mistakes
    other_at = "q" if at == "p" else "p"
    named_sides = {"sin": ("the opposite leg", "the hypotenuse"),
                   "cos": ("the adjacent leg", "the hypotenuse"),
                   "tan": ("the opposite leg", "the adjacent leg")}[fn]
    pool = {}
    for g in ("sin", "cos", "tan"):
        if g == fn:
            continue
        pool[g] = Mis(f"used {FN_NAME[g]} where the question asks for {FN_NAME[fn]}",
                      _rational(ratios[(g, at)]))
    pool["reciprocal"] = Mis(f"took the reciprocal, dividing {named_sides[1]} by "
                             f"{named_sides[0]}", _rational(E(1) / key))
    pool["complement"] = Mis("found the complement's ratio, using the other acute angle",
                             _rational(ratios[(fn, other_at)]))
    pool["adjacent_as_hyp"] = Mis("used the adjacent leg as the hypotenuse",
                                  _rational(ratios[("tan", at)]) if fn == "sin" else None)
    pool["diff_over_hyp"] = Mis("took the difference of the two given lengths for the "
                                "third side", _rational(E(c - q_leg) / hyp_e))
    pool["sum_over_hyp"] = Mis("took the sum of the two given lengths for the third "
                               "side", _rational(E(c + q_leg) / hyp_e))
    pool["unit_leg"] = Mis("took the unknown leg to be 1", _rational(E(1) / hyp_e))
    pool["hyp_over_sum"] = Mis("divided the hypotenuse by the sum of the two legs",
                               _rational(attempt(lambda: hyp_e / (q_e + p_leg))))

    rationale = (f"{named_sides[0].capitalize()} is "
                 f"{(q_e if (fn, at) in (('sin', 'p'), ('cos', 'q'), ('tan', 'p')) else p_leg).plain()}"
                 f" and {named_sides[1]} is "
                 f"{(hyp_e if fn != 'tan' else (p_leg if at == 'p' else q_e)).plain()}, "
                 f"so {spoken} = {key.plain()}.")
    P = {"kind": "rtt_trig_ratio", "hyp": c, "leg": q_leg, "fn": fn, "at": at}
    if fmt == "spr":
        # these work the third side out of c and q: triple mode labels all
        # three, and third-side mode gives c and p, leaving q unknown
        if mode in ("triple", "third_side"):
            pool["diff_over_hyp"] = pool["sum_over_hyp"] = None
        if mode == "triple":
            pool["unit_leg"] = None
        pool["hyp_over_sum"] = None     # no route to a sine or cosine runs through it
        return Item("rtt.trig_ratio", "trigonometric ratios", "medium", seed, stem,
                    "spr", key, key.gridin(), rationale, figure=fig, params=P,
                    spr_mistakes=gridin_mistakes(key, pick(pool, wrongs)))
    choices, latex, reasons, letter_ = assemble(key, pick(pool, wrongs), rng)
    return Item("rtt.trig_ratio", "trigonometric ratios", "medium", seed, stem, "mcq",
                key, letter_, rationale, choices, reasons, latex, figure=fig, params=P)


# ================================================= a ratio and a side, find a side

def ratio_to_side(rng: random.Random, seed: int, *, triple=None, swap=False, scale=None,
                  fn=None, given=None, ask=None, names=None, right=None, at=None,
                  unit=None, fmt=None, figure=False, layout=None, note=False,
                  wrongs=None) -> Item:
    """A trigonometric ratio fixes the shape; one length fixes the size.

    The triangle is drawn from a Pythagorean triple and a scale factor, both
    of them parameters, so the template is not built round 3-4-5. `names` is
    the triangle as the stem prints it and `right` says which of those three
    vertices carries the right angle, so relabelling never moves the geometry.
    """
    u, v, w = triple or rng.choice(TRIPLES)
    if swap:
        u, v = v, u
    t = int(scale if scale is not None else rng.randint(1, 40))
    trio = names or rng.choice(TRIOS)
    right = 2 if right is None else int(right)
    rest = [i for i in (0, 1, 2) if i != right]
    at = rest[0] if at is None else int(at)
    if at == right or at not in rest:
        raise ItemError("the ratio belongs to an acute vertex, not the right angle")
    # X is the vertex whose ratio is given, Z the right angle, Y the third
    Z = trio[right]
    X = trio[at]
    Y = trio[next(i for i in rest if i != at)]
    adj, opp, hypo = E(u * t), E(v * t), E(w * t)
    seg = {"adj": "".join(sorted((X, Z))), "opp": "".join(sorted((Y, Z))),
           "hyp": "".join(sorted((X, Y)))}
    length = {"adj": adj, "opp": opp, "hyp": hypo}

    fn = fn or rng.choice(["sin", "cos", "tan"])
    pair = {"sin": (v, w), "cos": (u, w), "tan": (v, u)}[fn]
    given = given or rng.choice(["adj", "opp", "hyp"])
    ask = ask or rng.choice([k for k in ("adj", "opp", "hyp") if k != given])
    if ask == given:
        raise ItemError("the stem would be asking for the number it states")
    key = length[ask]

    unit_words = unit.many() if unit else None
    tail = f", in {unit_words}," if unit_words else ""
    stated = f"{length[given].plain()} {unit_words}" if unit_words else length[given].plain()
    ratio = ratio_text(*pair)
    if figure:
        layout = layout or rng.choice(["left", "right"])
        if not 0.125 <= float(adj) / float(opp) <= 8.0:
            raise ItemError("a triangle this thin cannot be drawn legibly")
        # the leg from the right angle to X is the one adjacent to X; the leg
        # from the right angle to Y is the one opposite it
        marks = {{"adj": "p", "opp": "q", "hyp": "hyp"}[given]: length[given].plain()}
        fig = right_triangle(float(adj), float(opp), layout=layout, sides=marks,
                             names={"rt": Z, "p": X, "q": Y}, note=note)
        stem = (f"Triangle {trio[0]}{trio[1]}{trio[2]} above is a right triangle, and "
                f"{fn} {X} = {ratio}. What is the length of side {seg[ask]} ?")
    else:
        fig = None
        stem = (f"In triangle {trio[0]}{trio[1]}{trio[2]}, angle {Z} is a right angle "
                f"and the length of {seg[given]} is {stated}. If {fn} {X} = {ratio}, "
                f"what is the length{tail} of {seg[ask]} ?")

    pool = {
        "hypotenuse": Mis("gave the hypotenuse instead of the leg asked for", hypo),
        "given": Mis("gave the side the stem states rather than the one it asks for",
                     length[given]),
        "hyp_minus_given": Mis("subtracted the given leg from the hypotenuse",
                               hypo - length[given] if float(hypo) > float(length[given])
                               else None),
        "other_leg": Mis("gave the other leg",
                         length["opp"] if ask == "adj" else length["adj"]),
        "times_ratio": Mis("multiplied by the ratio where it should have divided",
                           length[given] * E(Q(pair[0], pair[1]))),
        "over_ratio": Mis("divided by the ratio where it should have multiplied",
                          length[given] / E(Q(pair[0], pair[1]))),
        "scale": Mis("stopped at the scale factor instead of the side length", E(t)
                     if t > 1 else None),
    }
    rationale = (f"{fn} {X} = {ratio} makes the sides {u * t}, {v * t} and {w * t}, so "
                 f"{seg[ask]} = {key.plain()}.")
    P = {"kind": "rtt_ratio_to_side", "u": u, "v": v, "w": w, "t": t, "fn": fn,
         "given": given, "ask": ask}
    fmt = fmt or ("spr" if rng.random() < 0.3 else "mcq")
    if fmt == "spr":
        if ask == "hyp":                # the hypotenuse is the unknown
            pool["hyp_minus_given"] = None
        # multiplying where one should divide needs a ratio that joins the side
        # given to the side asked for
        if {given, ask} != set({"sin": ("opp", "hyp"), "cos": ("adj", "hyp"),
                                "tan": ("opp", "adj")}[fn]):
            pool["times_ratio"] = pool["over_ratio"] = None
        return Item("rtt.ratio_to_side", "trigonometric ratios", "medium", seed, stem,
                    "spr", key, key.gridin(), rationale, figure=fig, params=P,
                    spr_mistakes=gridin_mistakes(key, pick(pool, wrongs)))
    choices, latex, reasons, letter = assemble(key, pick(pool, wrongs), rng)
    return Item("rtt.ratio_to_side", "trigonometric ratios", "medium", seed, stem, "mcq",
                key, letter, rationale, choices, reasons, latex, figure=fig, params=P)


# ====================================================== which has the same value

def cofunction_match(rng: random.Random, seed: int, *, leg_p=None, leg_q=None, fn=None,
                     at=None, names=None, right=None, layout=None, note=True) -> Item:
    """sin of one acute angle is cos of the other, and nothing else on offer is.

    The two legs are the parameters, so the hypotenuse is free to be a radical
    -- it is never printed, and none of the four options needs it whole.
    """
    a = int(leg_p if leg_p is not None else rng.randint(2, 60))
    b = int(leg_q if leg_q is not None else rng.randint(2, 60))
    if a == b:
        raise ItemError("in a 45-45-90 triangle three of the four options agree")
    if not 0.125 <= a / b <= 8.0:
        raise ItemError("a triangle this thin cannot be drawn legibly")
    trio = names or rng.choice(TRIOS)
    right = 2 if right is None else int(right)
    rest = [i for i in (0, 1, 2) if i != right]
    Z, P_, Q_ = trio[right], trio[rest[0]], trio[rest[1]]
    at = at or rng.choice(["p", "q"])
    fn = fn or rng.choice(["sin", "cos"])
    layout = layout or rng.choice(["left", "right"])

    c = E(1, 0, a * a + b * b)                  # the hypotenuse, exactly
    p_leg, q_leg = E(a), E(b)
    ratios = {("sin", "p"): q_leg / c, ("cos", "p"): p_leg / c,
              ("tan", "p"): q_leg / p_leg,
              ("sin", "q"): p_leg / c, ("cos", "q"): q_leg / c,
              ("tan", "q"): p_leg / q_leg}
    other = "q" if at == "p" else "p"
    g = "cos" if fn == "sin" else "sin"
    want = ratios[(fn, at)]
    key_text = f"{g} {P_ if other == 'p' else Q_}"
    wrong = [
        Mis("the tangent compares the two legs, not a leg with the hypotenuse",
            f"tan {P_}"),
        Mis("the tangent compares the two legs, not a leg with the hypotenuse",
            f"tan {Q_}"),
        Mis(f"used the other function at the same vertex instead of the same "
            f"function at the other one", f"{g} {P_ if at == 'p' else Q_}"),
    ]
    for name, value in ((f"tan {P_}", ratios[("tan", "p")]),
                        (f"tan {Q_}", ratios[("tan", "q")]),
                        (f"{g} {P_ if at == 'p' else Q_}", ratios[(g, at)])):
        if float(value) == float(want):
            raise ItemError(f"{name} also equals the ratio the stem asks about")

    fig = right_triangle(a, b, layout=layout, sides={"p": str(a), "q": str(b)},
                         names={"rt": Z, "p": P_, "q": Q_}, note=note)
    name = "".join(trio)
    asked = f"{fn} {P_ if at == 'p' else Q_}"
    stem = rng.choice([
        f"Triangle {name} shown is a right triangle. Which of the following has "
        f"the same value as {asked} ?",
        f"Triangle {name} shown is a right triangle. Which of the following is "
        f"equal to {asked} ?",
    ])
    rationale = (f"The two acute angles are complementary, so the {FN_NAME[fn]} of one "
                 f"is the {FN_NAME[g]} of the other: {asked} = {key_text}.")
    P = {"kind": "rtt_cofunction_match", "a": a, "b": b, "fn": fn, "at": at,
         "names": [Z, P_, Q_]}
    choices, reasons, letter = assemble_text(key_text, wrong, rng)
    return Item("rtt.cofunction_match", "cofunctions", "medium", seed, stem, "mcq",
                E(0), letter, rationale, choices, reasons, choices, figure=fig,
                params=P)


# ============================================ complementary angles as expressions

def cofunction_angles(rng: random.Random, seed: int, *, m1=None, b1=None, m2=None,
                      b2=None, names=None, fn=None, fmt=None, wrongs=None) -> Item:
    """cos Q = sin R only when the two acute angles are complementary."""
    m1 = m1 if m1 is not None else rng.randint(1, 8)
    m2 = m2 if m2 is not None else rng.randint(1, 8)
    b1 = b1 if b1 is not None else rng.randint(1, 80)
    b2 = b2 if b2 is not None else rng.randint(1, 80)
    if m1 + m2 == 0:
        raise ItemError("the two measures do not pin x down")
    x = Q(90 - b1 - b2, m1 + m2)
    if x.denominator != 1 or x <= 0:
        raise ItemError("x is not a whole positive number")
    a1, a2 = m1 * x + b1, m2 * x + b2
    if not (0 < a1 < 90 and 0 < a2 < 90):
        raise ItemError("one of the two angles is not acute")
    fn = fn or rng.choice(["cos_sin", "sin_cos"])
    first, second = ("cos", "sin") if fn == "cos_sin" else ("sin", "cos")
    trio = names or rng.choice([("Q", "R"), ("A", "B"), ("P", "S"), ("X", "Y"),
                                ("J", "K"), ("M", "N")])
    U, V = trio
    key = E(x)

    def expr(m, b):
        head = "x" if m == 1 else f"{m}x"
        return f"{head} + {b}" if b >= 0 else f"{head} {MINUS} {-b}"

    stem = rng.choice([
        f"For two acute angles, angle {U} and angle {V}, {first} {U} = {second} {V}. "
        f"The measures, in degrees, of angle {U} and angle {V} are {expr(m1, b1)} and "
        f"{expr(m2, b2)}, respectively. What is the value of x ?",
        f"Angle {U} and angle {V} are acute angles for which {first} {U} = {second} {V}. "
        f"The measure of angle {U} is {expr(m1, b1)} degrees and the measure of angle "
        f"{V} is {expr(m2, b2)} degrees. What is the value of x ?",
    ])

    def root(target, den, num):
        val = Q(num, den) if den else None
        return E(val) if val is not None and val.denominator == 1 else None

    pool = {
        "set_equal": Mis("set the two measures equal instead of complementary",
                         root(0, m1 - m2, b2 - b1)),
        "supplementary": Mis("made the two angles supplementary instead of "
                             "complementary", root(0, m1 + m2, 180 - b1 - b2)),
        "first_right": Mis("set only the first angle equal to 90 degrees",
                           root(0, m1, 90 - b1)),
        "second_right": Mis("set only the second angle equal to 90 degrees",
                            root(0, m2, 90 - b2)),
        "angle": Mis("gave the measure of an angle rather than the value of x",
                     E(a1) if a1 != x else None),
    }
    rationale = (f"Complementary angles give ({expr(m1, b1)}) + ({expr(m2, b2)}) = 90, "
                 f"so {m1 + m2}x = {90 - b1 - b2} and x = {key.plain()}.")
    P = {"kind": "rtt_cofunction_angles", "m1": m1, "b1": b1, "m2": m2, "b2": b2}
    mistakes = [m for m in pick(pool, wrongs) if m.value is not None]
    if fmt == "spr":
        return Item("rtt.cofunction_angles", "cofunctions", "hard", seed, stem, "spr",
                    key, key.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble(key, mistakes, rng, signed=True,
                                               fillers="shift")
    return Item("rtt.cofunction_angles", "cofunctions", "hard", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex, params=P)


# ================================================ the tangent of the other angle

# Printed as the source prints it: a numerator over a denominator, never
# simplified, so that the reciprocal is the same two pieces the other way up.
# Only 1/√n forms are offered -- a coefficient in the numerator would make the
# flipped spelling ("3/2√3") ambiguous on the page.
RADICAL_TANGENTS = [(f"√{n}", str(n), n, Q(1, n))
                    for n in (2, 3, 5, 6, 7, 10, 11, 13, 14, 15)]


def complement_tangent(rng: random.Random, seed: int, *, num=None, den=None,
                       radical=None, fmt=None, wrongs=None) -> Item:
    """The two acute angles of a right triangle have reciprocal tangents.

    A source item may name a radical tangent, and then the options are printed
    the way the source prints them -- √3/3 and 3/√3 are the same two pieces the
    other way up, never simplified -- so the surface is carried alongside the
    value rather than recomputed from it. A free draw stays with a rational
    tangent: the flipped radical spelling is one the shared `item.numeral`
    cannot read back, and a page the engine's own reader cannot parse is a page
    no generated item should carry.
    """
    flipped = radical is not None
    if flipped:
        top, bottom, rad, coef = next(r for r in RADICAL_TANGENTS
                                      if f"{r[0]}/{r[1]}" == radical)
        given = E(coef, 0, rad)
        key = E(1) / given
        given_text, key_text = f"{top}/{bottom}", f"{bottom}/{top}"
    else:
        p_ = int(num if num is not None else rng.randint(2, 30))
        q_ = int(den if den is not None else rng.randint(2, 30))
        if p_ == q_ or p_ % q_ == 0 or q_ % p_ == 0:
            raise ItemError("one of the two tangents would be a whole number")
        given, key = E(Q(p_, q_)), E(Q(q_, p_))
        given_text, key_text = given.plain(), key.plain()

    surface = {key: key_text, given: given_text,
               -key: f"{MINUS}{key_text}", -given: f"{MINUS}{given_text}"}
    pool = {
        "same": Mis("gave the tangent of the same angle over again", given),
        "negative_reciprocal": Mis("took the negative reciprocal, as though the two "
                                   "legs pointed in perpendicular directions", -key),
        "negative": Mis("changed the sign instead of inverting the ratio", -given),
    }
    stem = rng.choice([
        f"In a right triangle, the tangent of one of the two acute angles is "
        f"{given_text}. What is the tangent of the other acute angle?",
        f"One of the two acute angles of a right triangle has a tangent of "
        f"{given_text}. What is the tangent of the other acute angle?",
    ])
    rationale = (f"The two acute angles are complementary, so their tangents are "
                 f"reciprocals: the other tangent is {key_text}.")
    P = {"kind": "rtt_complement_tangent", "given": [str(given.coef), given.rad]}
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("a radical cannot be entered in a grid-in")
        return Item("rtt.complement_tangent", "cofunctions", "hard", seed, stem, "spr",
                    key, key.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(key, pick(pool, wrongs)))
    choices, latex, reasons, letter = assemble(
        key, pick(pool, wrongs), rng, signed=True,
        fmt_value=lambda v: surface.get(v, v.plain()))
    return Item("rtt.complement_tangent", "cofunctions", "hard", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex, params=P)


# ============================== a ratio at one acute angle, asked at the other

def complement_ratio(rng: random.Random, seed: int, *, triple=None, swap=False,
                     scale=None, fn=None, ask=None, names=None, fmt=None,
                     wrongs=None) -> Item:
    """One acute angle's ratio, asked again at the other acute angle."""
    u, v, w = triple or rng.choice(TRIPLES)
    if swap:
        u, v = v, u
    t = int(scale if scale is not None else rng.randint(1, 9))
    fn = fn or rng.choice(["sin", "cos", "tan"])
    ask = ask or rng.choice(["sin", "cos", "tan"])
    trio = names or rng.choice(TRIOS)
    J, K, L = trio                      # J is the right angle, K and L the acute ones
    shown = {"sin": (v * t, w * t), "cos": (u * t, w * t), "tan": (v * t, u * t)}[fn]
    # the other acute angle swaps opposite and adjacent
    key = {"sin": E(Q(u, w)), "cos": E(Q(v, w)), "tan": E(Q(u, v))}[ask]

    pool = {
        "same_angle": Mis(f"gave {fn} {K}, the ratio the stem states",
                          E(Q(shown[0], shown[1]))),
        "reciprocal": Mis("took the reciprocal of the ratio", E(1) / key),
        "sin": Mis(f"used sine where the question asks for {FN_NAME[ask]}",
                   E(Q(u, w)) if ask != "sin" else None),
        "cos": Mis(f"used cosine where the question asks for {FN_NAME[ask]}",
                   E(Q(v, w)) if ask != "cos" else None),
        "tan": Mis(f"used tangent where the question asks for {FN_NAME[ask]}",
                   E(Q(u, v)) if ask != "tan" else None),
        "unreduced": Mis("wrote the third side as the difference of the two given "
                         "lengths", E(Q(abs(shown[1] - shown[0]), shown[1]))),
    }
    stem = rng.choice([
        f"In triangle {J}{K}{L}, {fn} {K} = {ratio_text(*shown)} and angle {J} is a "
        f"right angle. What is the value of {ask} {L} ?",
        f"Angle {J} is a right angle in triangle {J}{K}{L}, and {fn} {K} = "
        f"{ratio_text(*shown)}. What is the value of {ask} {L} ?",
    ])
    rationale = (f"The sides are {u * t}, {v * t} and {w * t}, and angle {L} is the "
                 f"complement of angle {K}, so {ask} {L} = {key.plain()}.")
    P = {"kind": "rtt_complement_ratio", "u": u, "v": v, "w": w, "t": t, "fn": fn,
         "ask": ask}
    mistakes = [m for m in pick(pool, wrongs) if m.value is not None]
    if fmt == "spr":
        # the difference is the third side only when both ratios use it
        if (fn, ask) not in (("sin", "sin"), ("cos", "cos")):
            mistakes = [m for m in mistakes if m is not pool["unreduced"]]
        return Item("rtt.complement_ratio", "cofunctions", "hard", seed, stem, "spr",
                    key, key.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("rtt.complement_ratio", "cofunctions", "hard", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex, params=P)


# ====================================== a right angle split by a ray through it

def split_right_angle(rng: random.Random, seed: int, *, leg_p=None, leg_q=None,
                      names=None, right=None, inner=None, order=None, layout=None,
                      note=False) -> Item:
    """A ray from the right angle splits it into two complementary angles.

    Whatever the ray does, the cosine of one piece is the sine of the other, so
    their difference is 0 -- and the triangle's own side lengths never enter it.
    """
    a = int(leg_p if leg_p is not None else rng.randint(2, 40))
    b = int(leg_q if leg_q is not None else rng.randint(2, 40))
    if a == b:
        raise ItemError("an isosceles right triangle makes the ray's two pieces alike")
    if not 0.125 <= a / b <= 8.0:
        raise ItemError("a triangle this thin cannot be drawn legibly")
    trio = names or rng.choice(TRIOS)
    right = 1 if right is None else int(right)
    rest = [i for i in (0, 1, 2) if i != right]
    S, R, T = trio[right], trio[rest[0]], trio[rest[1]]      # S is the right angle
    W = inner or rng.choice([c for c in "WXYZMNUV" if c not in trio])
    order = order or rng.choice(["cos_sin", "sin_cos"])
    first, second = ("cos", "sin") if order == "cos_sin" else ("sin", "cos")
    layout = layout or rng.choice(["apex", "apex", "left", "right"])
    key = E(0)

    fig = right_triangle(a, b, layout=layout, sides={"p": str(a), "q": str(b)},
                         names={"rt": S, "p": R, "q": T}, note=note)
    name = "".join(trio)
    stem = rng.choice([
        f"In triangle {name} above, point {W} (not shown) lies on {R}{T}. What is "
        f"the value of {first}(∠{R}{S}{W}) {MINUS} {second}(∠{W}{S}{T}) ?",
        f"In the triangle shown, point {W} (not shown) lies on {R}{T}. What is the "
        f"value of {first}(∠{R}{S}{W}) {MINUS} {second}(∠{W}{S}{T}) ?",
    ])
    rationale = (f"Angle {R}{S}{W} and angle {W}{S}{T} make up the right angle at {S}, "
                 f"so they are complementary and the {FN_NAME[first]} of one equals "
                 f"the {FN_NAME[second]} of the other. The difference is 0.")
    P = {"kind": "rtt_split_right_angle", "a": a, "b": b, "order": order}
    return Item("rtt.split_right_angle", "cofunctions", "hard", seed, stem, "spr", key,
                key.gridin(), rationale, figure=fig, params=P)
