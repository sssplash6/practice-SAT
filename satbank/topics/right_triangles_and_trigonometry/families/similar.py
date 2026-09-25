"""Similar right triangles, where the correspondence is part of the mathematics.

"Triangle ABC is similar to triangle DEF, where A corresponds to D" is not
decoration: swap the correspondence and the same numbers answer a different
question. Every template here carries the correspondence in its parameters and
prints it in its stem, and the audit re-derives the answer through that
correspondence rather than through the template's own bookkeeping.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E, Exact
from ....item import Item, ItemError, Mis, assemble, gridin_mistakes
from ..kit import TRIPLES, assemble_exact, exact_leg, pick, ratio_text

__all__ = ["similar_ratio", "similar_side", "similar_sides_ratio"]

FN_NAME = {"sin": "sine", "cos": "cosine", "tan": "tangent"}
PAIRS = ((("A", "B", "C"), ("D", "E", "F")), (("A", "B", "C"), ("X", "Y", "Z")),
         (("P", "Q", "R"), ("S", "T", "U")), (("J", "K", "L"), ("M", "N", "P")),
         (("R", "S", "T"), ("U", "V", "W")), (("D", "E", "F"), ("G", "H", "J")))


def _rational(v):
    return v if isinstance(v, Exact) and v.is_rational and float(v) > 0 else None


def _sides_from(fn: str, at: str, p: int, q: int) -> dict:
    """The three sides of a right triangle from one ratio at one acute vertex.

    `at="A"` reads the ratio at the first acute vertex, whose opposite leg is
    `a`; `at="B"` at the second, whose opposite leg is `b`. The third side comes
    out of the theorem and may well be a radical -- which is fine, because only
    the ratio the stem asks for has to be writable.
    """
    if p <= 0 or q <= 0:
        raise ItemError("a ratio is built from positive lengths")
    opp, adj = ("a", "b") if at == "A" else ("b", "a")
    out = {}
    if fn == "sin":
        if p >= q:
            raise ItemError("a sine is less than 1")
        out[opp], out["c"] = E(p), E(q)
        out[adj] = exact_leg(q, p)
    elif fn == "cos":
        if p >= q:
            raise ItemError("a cosine is less than 1")
        out[adj], out["c"] = E(p), E(q)
        out[opp] = exact_leg(q, p)
    else:
        out[opp], out[adj] = E(p), E(q)
        out["c"] = (E(p) ** 2 + E(q) ** 2).sqrt()
        if out["c"] is None:
            raise ItemError("the hypotenuse is not expressible")
    return out


def _ratio(sides: dict, fn: str, at: str) -> Exact:
    opp, adj = ("a", "b") if at == "A" else ("b", "a")
    if fn == "sin":
        return sides[opp] / sides["c"]
    if fn == "cos":
        return sides[adj] / sides["c"]
    return sides[opp] / sides[adj]


# ==================================== one triangle's ratio, asked in the other

def similar_ratio(rng: random.Random, seed: int, *, given_fn=None, given_at=None,
                  p=None, q=None, ask_fn=None, ask_at=None, names=None, scale=None,
                  wording=None, fmt=None, wrongs=None) -> Item:
    """A ratio stated for one triangle and asked for in the similar one.

    Similar triangles have equal angles, so a corresponding angle keeps the
    ratio and the other acute angle takes its complement's. Which of the two
    it is comes from the correspondence the stem prints.
    """
    # "A" and "B" name the roles, not the letters: A is the acute vertex the
    # correspondence pairs with D, B the one it pairs with E. The letters the
    # stem prints come from `names`, so the correspondence survives a relabel.
    given_fn = given_fn or rng.choice(["sin", "cos", "tan"])
    given_at = given_at or rng.choice(["A", "B"])
    ask_fn = ask_fn or rng.choice(["sin", "cos", "tan"])
    ask_at = ask_at or rng.choice(["D", "E"])
    if given_at not in ("A", "B") or ask_at not in ("D", "E"):
        raise ItemError("the correspondence is named by role, not by letter")
    first, second = names or rng.choice(PAIRS)
    A, B, C = first
    D, Eq, F_ = second
    given_name = A if given_at == "A" else B
    ask_name = D if ask_at == "D" else Eq

    if p is None or q is None:
        u, v, w = rng.choice(TRIPLES)
        p, q = {"sin": (v, w), "cos": (u, w), "tan": (v, u)}[given_fn]
        k = rng.randint(1, 8)
        p, q = p * k, q * k
    p, q = int(p), int(q)
    sides = _sides_from(given_fn, given_at, p, q)
    here = "A" if ask_at == "D" else "B"          # D matches A, E matches B
    key = _ratio(sides, ask_fn, here)
    if not key.is_rational:
        raise ItemError("the ratio asked for is not one the student can write down")

    corr = (f"angle {A} corresponds to angle {D}" if wording != "plain"
            else f"{A} corresponds to {D}")
    right = f"angles {C} and {F_} are right angles"
    sentence = rng.choice([
        f"Triangle {A}{B}{C} is similar to triangle {D}{Eq}{F_}, where {corr}, and "
        f"{right}.",
        f"Triangle {A}{B}{C} is similar to triangle {D}{Eq}{F_}, where {corr} and "
        f"{right}.",
    ])
    if scale is not None:
        sentence += (f" The length of {A}{B} is {scale} times the length of "
                     f"{D}{Eq}.")
    asked = f"{ask_fn} {ask_name}"
    stem = (f"{sentence} If {given_fn} {given_name} = {ratio_text(p, q)}, what is the "
            f"value of {asked} ?")

    other_here = "B" if here == "A" else "A"
    pool = {
        "unchanged": Mis("kept the ratio the stem states, although the question asks "
                         "for a different one", _rational(E(Q(p, q)))),
        "reciprocal": Mis("took the reciprocal of the ratio", _rational(E(Q(q, p)))),
        "complement": Mis("found the complement's ratio, using the other acute angle",
                          _rational(_ratio(sides, ask_fn, other_here))),
        "third_by_subtracting": Mis("took the third side to be the difference of the "
                                    "two given lengths", _rational(E(Q(q - p, q)))
                                    if q > p else None),
        "sum_denominator": Mis("added the two given lengths for the hypotenuse",
                               _rational(E(Q(p, p + q)))),
        "swapped_sum": Mis("swapped the two lengths and added them for the hypotenuse",
                           _rational(E(Q(q, p + q)))),
    }
    for g in ("sin", "cos", "tan"):
        if g != ask_fn:
            pool[g] = Mis(f"used {FN_NAME[g]} where the question asks for "
                          f"{FN_NAME[ask_fn]}", _rational(_ratio(sides, g, here)))
    rationale = (f"Corresponding angles of similar triangles are equal, so angle "
                 f"{ask_name} matches angle {A if here == 'A' else B} and "
                 f"{asked} = {key.plain()}.")
    P = {"kind": "rtt_similar_ratio", "given_fn": given_fn, "given_at": given_at,
         "p": p, "q": q, "ask_fn": ask_fn, "ask_at": ask_at}
    fmt = fmt or ("spr" if rng.random() < 0.4 else "mcq")
    mistakes = [m for m in pick(pool, wrongs) if m.value is not None]
    if fmt == "spr":
        if ask_fn == "tan":
            mistakes = [m for m in mistakes if m not in
                        (pool["sum_denominator"], pool["swapped_sum"])]
        return Item("rtt.similar_ratio", "similar right triangles", "hard", seed, stem,
                    "spr", key, key.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("rtt.similar_ratio", "similar right triangles", "hard", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex, params=P)


# ============================= one triangle's ratio, the other triangle's side

RADICAL_TANS = {"√3": E(1, 0, 3), "√3/3": E(Q(1, 3), 0, 3), "√2": E(1, 0, 2),
                "2√3/3": E(Q(2, 3), 0, 3), "√5": E(1, 0, 5), "√2/2": E(Q(1, 2), 0, 2)}


def similar_side(rng: random.Random, seed: int, *, tan=None, p=None, q=None, leg=None,
                 ask=None, names=None, fmt=None, wrongs=None) -> Item:
    """A tangent fixes the shape of the second triangle; one leg fixes its size."""
    first, second = names or rng.choice(PAIRS)
    A, B, C = first
    D, Eq, F_ = second
    if tan is not None:
        tan_text, t = tan, RADICAL_TANS[tan]
    elif p is not None and q is not None:
        tan_text, t = ratio_text(p, q), E(Q(int(p), int(q)))
    else:
        if rng.random() < 0.5:
            tan_text = rng.choice(list(RADICAL_TANS))
            t = RADICAL_TANS[tan_text]
        else:
            u, v, w = rng.choice(TRIPLES)
            tan_text, t = ratio_text(v, u), E(Q(v, u))
    m = E(leg if leg is not None else rng.randint(2, 400))
    over_cos = (E(1) + t ** 2).sqrt()
    if over_cos is None:
        raise ItemError("the hypotenuse of this triangle is not expressible")
    ask = ask or rng.choice(["hyp", "opposite"])
    key = m * over_cos if ask == "hyp" else m * t
    want = f"{D}{Eq}" if ask == "hyp" else f"{Eq}{F_}"

    pool = {
        "divided": Mis("divided by the tangent instead of multiplying", m / t),
        "times_sine": Mis("multiplied the given leg by the sine of the angle instead "
                          "of dividing by its cosine", m * t / over_cos),
        "other_leg": Mis("gave the other leg instead of the hypotenuse", m * t)
        if ask == "hyp" else
        Mis("gave the hypotenuse instead of the leg asked for", m * over_cos),
        "given_leg": Mis("gave the leg the stem states rather than the one it asks "
                         "for", m),
        "doubled": Mis("doubled the given leg", E(2) * m),
    }
    stem = rng.choice([
        f"Triangle {A}{B}{C} is similar to triangle {D}{Eq}{F_}, where {A} corresponds "
        f"to {D} and {C} corresponds to {F_}. Angles {C} and {F_} are right angles. If "
        f"tan {A} = {tan_text} and {D}{F_} = {m.plain()}, what is the length of "
        f"{want} ?",
        f"Triangle {A}{B}{C} is similar to triangle {D}{Eq}{F_}, where angle {A} "
        f"corresponds to angle {D} and angles {C} and {F_} are right angles. Given that "
        f"tan {A} = {tan_text} and {D}{F_} = {m.plain()}, what is the length of "
        f"{want} ?",
    ])
    rationale = (f"tan {D} = tan {A} = {tan_text}, so with {D}{F_} = {m.plain()} the "
                 f"side {want} is {key.plain()}.")
    P = {"kind": "rtt_similar_side", "tan": [str(t.coef), t.rad], "leg": float(m),
         "ask": ask}
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    mistakes = [m_ for m_ in pick(pool, wrongs) if m_.value is not None]
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("a radical cannot be entered in a grid-in")
        mistakes = [m_ for m_ in mistakes if m_ is not pool["doubled"]]
        if ask == "opposite":
            mistakes = [m_ for m_ in mistakes if m_ is not pool["times_sine"]]
        return Item("rtt.similar_side", "similar right triangles", "hard", seed, stem,
                    "spr", key, key.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble_exact(
        key, mistakes, rng, strict=wrongs is None)
    return Item("rtt.similar_side", "similar right triangles", "hard", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex, params=P)


# ======================== three side lengths given, a ratio asked in the copy

def similar_sides_ratio(rng: random.Random, seed: int, *, triple=None, scale=None,
                        swap=False, ask_fn=None, ask_at=None, names=None, fmt=None,
                        wrongs=None) -> Item:
    """The three sides are printed; the correspondence says which angle to use."""
    u, v, w = triple or rng.choice(TRIPLES)
    if swap:
        u, v = v, u
    t = int(scale if scale is not None else rng.randint(1, 20))
    first, second = names or rng.choice(PAIRS)
    R, S, T = first[1], first[0], first[2]        # S is the right angle
    U, V, W = second[1], second[0], second[2]
    ask_fn = ask_fn or rng.choice(["sin", "cos", "tan"])
    ask_at = ask_at or rng.choice(["W", "U"])
    if ask_at not in ("W", "U"):
        raise ItemError("the correspondence is named by role, not by letter")
    # RS is opposite T, ST is opposite R, TR is the hypotenuse
    rs, st, tr = E(u * t), E(v * t), E(w * t)
    at_T = ask_at == "W"
    ask_name = W if at_T else U
    opp, adj = (rs, st) if at_T else (st, rs)
    key = {"sin": opp / tr, "cos": adj / tr, "tan": opp / adj}[ask_fn]

    display = f"{R}{S} = {rs.plain()}\n{S}{T} = {st.plain()}\n{T}{R} = {tr.plain()}"
    body = (f"The side lengths of right triangle {R}{S}{T} are given. Triangle {R}{S}{T} "
            f"is similar to triangle {U}{V}{W}, where {S} corresponds to {V} and {T} "
            f"corresponds to {W}. What is the value of {ask_fn} {ask_name} ?")
    stem = f"{display}\n{body}"
    pool = {}
    for g in ("sin", "cos", "tan"):
        if g != ask_fn:
            pool[g] = Mis(f"used {FN_NAME[g]} where the question asks for "
                          f"{FN_NAME[ask_fn]}",
                          {"sin": opp / tr, "cos": adj / tr, "tan": opp / adj}[g])
    pool["reciprocal"] = Mis("took the reciprocal of the ratio", E(1) / key)
    pool["complement"] = Mis("found the complement's ratio, using the other acute "
                             "angle", {"sin": adj / tr, "cos": opp / tr,
                                       "tan": adj / opp}[ask_fn])
    rationale = (f"The right angle is at {S}, and {ask_name} matches "
                 f"{T if at_T else R}, so {ask_fn} {ask_name} = {key.plain()}.")
    P = {"kind": "rtt_similar_sides_ratio", "u": u, "v": v, "w": w, "t": t,
         "ask_fn": ask_fn, "at_T": at_T}
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    mistakes = [m for m in pick(pool, wrongs) if m.value is not None]
    if fmt == "spr":
        return Item("rtt.similar_sides_ratio", "similar right triangles", "hard", seed,
                    stem, "spr", key, key.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("rtt.similar_sides_ratio", "similar right triangles", "hard", seed,
                stem, "mcq", key, letter, rationale, choices, reasons, latex, params=P)
