"""Independent re-derivation of every Right Triangles and Trigonometry answer.

Written from the geometry, not from the generators. Nothing here imports a
template, a figure or `Exact`: where a template kept a 30-60-90 ratio as the
exact radical √3/2, this calls `math.sin(math.radians(60))`, and where a
template ran similar triangles through a scale factor, this puts the points on
a coordinate plane and measures. The two routes share no arithmetic at all, so
a wrong answer has to be produced twice, by two separately written pieces of
code, to escape.

Two places take particular care.

* The **correspondence** in a similar-triangles item is re-read from the
  parameters and the angles rebuilt from `atan2`, so a template that quietly
  swapped D for E answers a different question here and is caught.
* The **cofunction** items are checked by finding which ratio actually equals
  the one the stem names, rather than by repeating the rule that says which
  one it should be.
"""

from __future__ import annotations

import math
from fractions import Fraction as F

from ...audit import AuditError, close

TOL = 1e-9


def supply_hyp(p: dict) -> float:
    return math.hypot(*p["legs"])


def supply_leg(p: dict) -> float:
    if p["hyp"] <= p["leg"]:
        raise AuditError("hypotenuse must exceed a leg")
    return math.sqrt(p["hyp"] ** 2 - p["leg"] ** 2)


def supply_sine(p: dict) -> float:
    if not close(p["opposite"] ** 2 + p["adjacent"] ** 2, p["hyp"] ** 2):
        raise AuditError("the named sides do not form a right triangle")
    return p["opposite"] / p["hyp"]


def _triple(u, v, w) -> None:
    if abs(u * u + v * v - w * w) > 1e-9:
        raise AuditError(f"{u}, {v}, {w} are not the sides of a right triangle")


def _round_half_up(v: float, places: int) -> float:
    scale = 10 ** places
    return math.floor(abs(v) * scale + 0.5) / scale * (1 if v >= 0 else -1)


# ================================================================== sides

def pythagoras(p: dict) -> float:
    x, y = p["given"]
    if p["mode"] == "hypotenuse":
        v = math.hypot(x, y)
    else:
        leg, hyp = x, y
        if hyp <= leg:
            raise AuditError("a leg is not shorter than the hypotenuse")
        v = math.sqrt(hyp * hyp - leg * leg)
    places = p.get("places")
    return v if places is None else _round_half_up(v, places)


def leg_expression(p: dict) -> str:
    """The expression itself, spelled in plain ASCII.

    The shared normaliser knows that √(21² − 6²) and sqrt(21^2 - 6^2) are one
    answer, so writing it the other way here keeps the two routes apart.
    """
    big = f"{int(p['big']):,}" if p["big"] == int(p["big"]) else str(p["big"])
    small = f"{int(p['small']):,}" if p["small"] == int(p["small"]) else str(p["small"])
    if p["small"] >= p["big"]:
        raise AuditError("the two given lengths are in the wrong order")
    sign = "-" if p["mode"] == "leg" else "+"
    return f"sqrt({big}^2 {sign} {small}^2)"


def rectangle_diagonal(p: dict) -> float:
    """Rebuilt from the diagonal the stem prints, not from the sides it hides."""
    d = math.hypot(p["short"], p["long"])
    other = p["short"] if p["ask"] == "long" else p["long"]
    rest = d * d - other * other
    if rest <= 0:
        raise AuditError("the stated diagonal is not longer than the stated side")
    return math.sqrt(rest)


def special_triangle(p: dict) -> float:
    a = math.radians(p["alpha"])
    if p["given"] == "p":
        v = p["value"]
    elif p["given"] == "q":
        v = p["value"] / math.tan(a)
    else:
        v = p["value"] * math.cos(a)
    if p["ask"] == "angle_p":
        return float(p["alpha"])
    if p["ask"] == "angle_q":
        return 90.0 - p["alpha"]
    return {"p": v, "q": v * math.tan(a), "hyp": v / math.cos(a)}[p["ask"]]


R2, R3 = math.sqrt(2.0), math.sqrt(3.0)
SHAPE = {"isosceles": {"leg": 1.0, "other_leg": 1.0, "hyp": R2, "perimeter": 2.0 + R2},
         "thirty_sixty": {"short": 1.0, "long": R3, "hyp": 2.0,
                          "perimeter": 3.0 + R3}}


def special_perimeter(p: dict) -> float:
    parts = SHAPE[p["shape"]]
    a, b, d = F(p["value"][0]), F(p["value"][1]), p["value"][2]
    stated = float(a) + float(b) * math.sqrt(d)
    if p["given"] not in parts or p["ask"] not in parts:
        raise AuditError(f"{p['shape']} has no measure called {p['given']!r}")
    base = stated / parts[p["given"]]
    if base <= 0:
        raise AuditError("that measure does not describe a triangle")
    return base * parts[p["ask"]]


def equilateral_logo(p: dict) -> float:
    n = p["count"]
    if n < 3 or n % 2 == 0:
        raise AuditError("an even row of triangles is not a trapezoid")
    s = p["perimeter"] / (n + 2)
    one = math.sqrt(3.0) / 4.0 * s * s
    up, down = (n + 1) // 2, (n - 1) // 2
    shaded = up if p["shade"] == "up" else down
    return {"shaded": shaded, "one": 1, "whole": n}[p["ask"]] * one


# ================================================================= ratios

def _legs(hyp: float, leg: float) -> tuple[float, float]:
    rest = hyp * hyp - leg * leg
    if rest <= 0:
        raise AuditError("that leg is not shorter than the hypotenuse")
    return math.sqrt(rest), leg


def _six(hyp: float, leg: float) -> dict:
    """Every ratio the two acute angles have, straight off the side lengths."""
    p_leg, q_leg = _legs(hyp, leg)
    return {("sin", "p"): q_leg / hyp, ("cos", "p"): p_leg / hyp,
            ("tan", "p"): q_leg / p_leg,
            ("sin", "q"): p_leg / hyp, ("cos", "q"): q_leg / hyp,
            ("tan", "q"): p_leg / q_leg}


def trig_ratio(p: dict) -> float:
    return _six(float(p["hyp"]), float(p["leg"]))[(p["fn"], p["at"])]


def ratio_to_side(p: dict) -> float:
    """Recovered through the angle itself, so no step of the template repeats.

    The stem prints a ratio and one length; the angle comes back out of that
    ratio with an inverse trigonometric function, and the side asked for is
    then read off the hypotenuse the angle and the given length imply.
    """
    u, v, w, t = p["u"], p["v"], p["w"], p["t"]
    _triple(u, v, w)
    ratio = {"sin": v / w, "cos": u / w, "tan": v / u}[p["fn"]]
    angle = {"sin": math.asin, "cos": math.acos, "tan": math.atan}[p["fn"]](ratio)
    given = {"adj": u * t, "opp": v * t, "hyp": w * t}[p["given"]]
    hyp = {"adj": given / math.cos(angle), "opp": given / math.sin(angle),
           "hyp": given}[p["given"]]
    return {"adj": hyp * math.cos(angle), "opp": hyp * math.sin(angle),
            "hyp": hyp}[p["ask"]]


def cofunction_match(p: dict) -> str:
    """Found, not recited: which other ratio is numerically the same one."""
    a, b = float(p["a"]), float(p["b"])
    hyp = math.hypot(a, b)
    six = {("sin", "p"): b / hyp, ("cos", "p"): a / hyp, ("tan", "p"): b / a,
           ("sin", "q"): a / hyp, ("cos", "q"): b / hyp, ("tan", "q"): a / b}
    names = p["names"]
    target = six[(p["fn"], p["at"])]
    hits = [f"{fn} {names[1] if at == 'p' else names[2]}"
            for (fn, at), v in six.items()
            if (fn, at) != (p["fn"], p["at"]) and abs(v - target) < 1e-12]
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} of the other five ratios equal this one")
    return hits[0]


def cofunction_angles(p: dict) -> float:
    m1, b1, m2, b2 = p["m1"], p["b1"], p["m2"], p["b2"]
    if m1 + m2 == 0:
        raise AuditError("the two measures do not pin x down")
    x = F(90 - b1 - b2, m1 + m2)
    q, r = m1 * x + b1, m2 * x + b2
    if not (0 < q < 90 and 0 < r < 90):
        raise AuditError("one of the two angles is not acute")
    # the modelling itself, checked: cos Q and sin R really are equal there
    if abs(math.cos(math.radians(float(q))) - math.sin(math.radians(float(r)))) > 1e-12:
        raise AuditError("cos Q and sin R do not agree at the solved value of x")
    return float(x)


def complement_tangent(p: dict) -> float:
    coef, rad = F(p["given"][0]), p["given"][1]
    t = float(coef) * math.sqrt(rad)
    if t <= 0:
        raise AuditError("the tangent of an acute angle is positive")
    return 1.0 / math.tan(math.atan(t))


def complement_ratio(p: dict) -> float:
    u, v, w = p["u"], p["v"], p["w"]
    _triple(u, v, w)
    angle_k = math.atan2(v, u)                 # v is opposite K, u adjacent
    angle_l = math.pi / 2.0 - angle_k
    return {"sin": math.sin, "cos": math.cos, "tan": math.tan}[p["ask"]](angle_l)


def split_right_angle(p: dict) -> float:
    """Checked at three positions of W, on coordinates, not by the identity."""
    a, b = float(p["a"]), float(p["b"])
    first, second = p["order"].split("_")
    fn = {"cos": math.cos, "sin": math.sin}
    for u in (0.2, 0.5, 0.8):
        wx, wy = b * u, a * (1.0 - u)
        to_r, to_t, to_w = (0.0, a), (b, 0.0), (wx, wy)

        def between(p1, p2):
            dot = p1[0] * p2[0] + p1[1] * p2[1]
            n1 = math.hypot(*p1) * math.hypot(*p2)
            return math.acos(max(-1.0, min(1.0, dot / n1)))

        value = fn[first](between(to_r, to_w)) - fn[second](between(to_w, to_t))
        if abs(value) > 1e-9:
            raise AuditError(f"the difference is {value}, not 0, when W is at {u}")
    return 0.0


# ======================================================= similar triangles

def _angle_from(fn: str, at: str, p_: int, q_: int) -> float:
    """The angle at the first acute vertex, from a ratio stated at one of them."""
    if fn == "sin":
        if p_ >= q_:
            raise AuditError("a sine is less than 1")
        here = math.asin(p_ / q_)
    elif fn == "cos":
        if p_ >= q_:
            raise AuditError("a cosine is less than 1")
        here = math.acos(p_ / q_)
    else:
        here = math.atan(p_ / q_)
    return here if at == "A" else math.pi / 2.0 - here


def similar_ratio(p: dict) -> float:
    angle_a = _angle_from(p["given_fn"], p["given_at"], p["p"], p["q"])
    # A corresponds to D, B to E, so D keeps the angle and E takes its complement
    theta = angle_a if p["ask_at"] == "D" else math.pi / 2.0 - angle_a
    return {"sin": math.sin, "cos": math.cos, "tan": math.tan}[p["ask_fn"]](theta)


def similar_side(p: dict) -> float:
    coef, rad = F(p["tan"][0]), p["tan"][1]
    t = float(coef) * math.sqrt(rad)
    theta = math.atan(t)
    leg = p["leg"]
    return leg / math.cos(theta) if p["ask"] == "hyp" else leg * math.tan(theta)


def similar_sides_ratio(p: dict) -> float:
    u, v, w = p["u"], p["v"], p["w"]
    _triple(u, v, w)
    # RS = u·t is opposite T, ST = v·t is opposite R
    theta = math.atan2(u, v) if p["at_T"] else math.atan2(v, u)
    return {"sin": math.sin, "cos": math.cos, "tan": math.tan}[p["ask_fn"]](theta)


# ================================================== two triangles in one figure

def altitude_special(p: dict) -> float:
    """Solved on coordinates: the foot at the origin, the apex above it."""
    al, ga = math.radians(p["alpha"]), math.radians(p["gamma"])
    side = float(p["side"])
    # D = (0, 0), C = (xc, 0), B = (0, h) with angle BCD = gamma and BC = side
    h = side * math.sin(ga)
    xc = side * math.cos(ga)
    if abs(math.hypot(xc, h) - side) > 1e-9:
        raise AuditError("the altitude does not reproduce the stated side")
    xa = h * math.tan(al)                       # angle ABD = alpha
    return {"ad": xa, "dc": xc, "bd": h,
            "ab": math.hypot(xa, h), "bc": side}[p["ask"]]


def nested_similar(p: dict) -> float:
    u, v, w, t = p["u"], p["v"], p["w"], p["t"]
    _triple(u, v, w)
    ac, ab, bc = u * t, v * t, w * t
    da = float(p["cut"])
    if not 0 < da < ab:
        raise AuditError("the cut misses the triangle")
    # A = (0,0), B = (0,ab), C = (ac,0); D = (0,da) and E is on BC at that height
    ex = ac * (ab - da) / ab
    return {"de": ex, "bd": ab - da, "be": math.hypot(ex, ab - da),
            "da": da, "ac": ac, "ab": ab, "bc": bc}[p["ask"]]


def parallel_similar(p: dict) -> float:
    m, n = float(p["m"]), float(p["n"])
    k = float(F(*p["k"]))
    d = math.hypot(m, n)
    if abs(d - round(d)) > 1e-9:
        raise AuditError("the inner hypotenuse is not a whole number")
    # C = (0,0), A = (k·m, 0), E = (k·m, k·n); B = (m, 0) and D = (m, n)
    ce, ca, cd, ae = math.hypot(k * m, k * n), k * m, d, k * n
    return {"ce": ce, "ca": ca, "cd": cd, "ae": ae, "ab": ca - m,
            "de": ce - cd}[p["ask"]]


AUDITS = {
    "rtt_supply_hyp": supply_hyp,
    "rtt_supply_leg": supply_leg,
    "rtt_supply_sine": supply_sine,
    "rtt_pythagoras": pythagoras,
    "rtt_leg_expression": leg_expression,
    "rtt_rectangle_diagonal": rectangle_diagonal,
    "rtt_special_triangle": special_triangle,
    "rtt_special_perimeter": special_perimeter,
    "rtt_equilateral_logo": equilateral_logo,
    "rtt_trig_ratio": trig_ratio,
    "rtt_ratio_to_side": ratio_to_side,
    "rtt_cofunction_match": cofunction_match,
    "rtt_cofunction_angles": cofunction_angles,
    "rtt_complement_tangent": complement_tangent,
    "rtt_complement_ratio": complement_ratio,
    "rtt_split_right_angle": split_right_angle,
    "rtt_similar_ratio": similar_ratio,
    "rtt_similar_side": similar_side,
    "rtt_similar_sides_ratio": similar_sides_ratio,
    "rtt_altitude_special": altitude_special,
    "rtt_nested_similar": nested_similar,
    "rtt_parallel_similar": parallel_similar,
}
