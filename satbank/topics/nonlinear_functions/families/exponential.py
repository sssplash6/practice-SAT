"""Building an exponential model out of a situation.

Every option here is an equation, and two equations can be the same model
written differently, so each option carries the signature (coefficient, base,
exponent shape) the independent solver recomputes. What the source varies is
which of the four numbers a student puts where: the percent itself as the
base, the base and the coefficient swapped, the period folded into the
exponent the wrong way up.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import ItemError, Mis
from ..common import (MINUS, dec, num, ordinal, pair, pick, q, sig, text_item,
                      value_item, year)

__all__ = ["exp_model", "exp_period", "exp_from_table", "exp_offset", "exp_anchor",
           "exp_reach"]

# --------------------------------------------------------------- contexts

MODEL_CTX = [
    dict(kind="double",
         stem="At the time of posting a video, a social media channel had {a} "
              "subscribers. Each day for five days after the video was posted, the "
              "number of subscribers doubled from the number the previous day. Which "
              "equation gives the total number of subscribers, {y}, to the channel "
              "{x} days after the video was posted?",
         y="n", x="d", lhs="n = "),
    dict(kind="decay",
         stem="From {y0} through {y1}, the number of music CDs sold in the United "
              "States declined each year by approximately {pct} of the number sold "
              "the preceding year. In {y0}, approximately {a} million CDs were sold "
              "in the United States. Of the following, which best models {y}, the "
              "number of millions of CDs sold in the United States, {x} years after "
              "{y0}?",
         y="C", x="t", lhs="C = ", rate=(50, 300)),
    dict(kind="decay",
         stem="A certain college had {a} students enrolled in {y0}. The college "
              "predicts that after {y0}, the number of students enrolled each year "
              "will be {pct} less than the number of students enrolled the year "
              "before. Which of the following functions models the relationship "
              "between the number of students enrolled, f({x}), and the number of "
              "years after {y0}, {x}?",
         y="f", x="x", lhs="f(x) = ", rate=(10, 90)),
    dict(kind="growth",
         stem="A model predicts that the population of Bergen was {a} in {y0}. The "
              "model also predicts that each year for the next 5 years, the "
              "population {y} increased by {pct} of the previous year's population. "
              "Which equation best represents this model, where {x} is the number of "
              "years after {y0}, for {x} ≤ 5?",
         y="p", x="x", lhs="p = ", rate=(10, 95)),
    dict(kind="growth",
         stem="There were no jackrabbits in Australia before {y0} when {a} "
              "jackrabbits were introduced. By {y1} the population of jackrabbits had "
              "reached about {total}. If the population had grown exponentially, "
              "this would correspond to a {pct} increase, on average, in the "
              "population "
              "each year. Which of the following functions best models the "
              "population {y}({x}) of jackrabbits {x} years after {y0}?",
         y="p", x="t", lhs="p(t) = ", rate=(80, 260)),
]


def _magnitude(v) -> str:
    """A big number the way a sentence says it: '10 billion', '4 million'."""
    v = float(v)
    for cut, word in ((10 ** 9, "billion"), (10 ** 6, "million")):
        if v >= cut:
            n = round(v / cut)
            return f"{n:,} {word}"
    return f"{round(v):,}"


def _pct(r) -> str:
    r = q(r) * 100
    return (num(r) if r.denominator == 1 else dec(r)) + "%"


def exp_model(rng: random.Random, seed: int, *, ctx=None, a=None, r=None, y0=None,
              y1=None, wrongs=None) -> object:
    """Words to an exponential: the starting amount and the per-period factor."""
    d = MODEL_CTX[rng.randrange(len(MODEL_CTX))] if ctx is None else MODEL_CTX[ctx]
    x, lhs = d["x"], d["lhs"]

    if d["kind"] == "double":
        a = int(a if a is not None else rng.randint(12, 400))
        factor = q(2)
        r = q(1)
        places = None
    else:
        a = int(a if a is not None else rng.choice(
            [rng.randrange(2, 60) * 100, rng.randrange(3, 40) * 1000, rng.randint(12, 90)]))
        lo, hi = d.get("rate", (20, 300))
        r = q(r if r is not None else Q(rng.randrange(lo, hi), 1000))
        factor = 1 + r if d["kind"] == "growth" else 1 - r
        places = max(len(dec(r).split(".")[-1]) if "." in dec(r) else 0, 2)
    if a <= 0 or factor <= 0:
        raise ItemError("an exponential model needs a positive start and factor")
    y0 = int(y0 if y0 is not None else rng.randrange(1780, 2016))
    y1 = int(y1 if y1 is not None else y0 + rng.randint(5, 140))
    total = q(a) * factor ** (y1 - y0)
    if "{total}" in d["stem"] and not 10 ** 6 <= float(total) < 10 ** 13:
        raise ItemError("the population reached must be a readable magnitude")

    def eq(head, base, expo, head_places=None, base_places=places):
        h = dec(head, head_places) if head_places is not None else num(head)
        b = dec(base, base_places) if base_places is not None else num(base)
        return f"{lhs}{h}({b})^{expo}"

    key = eq(a, factor, x)
    pool = {
        "raw_rate": ("used the percent itself as the growth factor",
                     pair(eq(a, r, x, base_places=places), a, r, x)),
        "grow": ("added the percent instead of subtracting it",
                 pair(eq(a, 1 + r, x), a, 1 + r, x)),
        "decay": ("subtracted the percent instead of adding it",
                  pair(eq(a, 1 - r, x), a, 1 - r, x)),
        "one_plus_factor": ("added 1 to the decay factor as well as subtracting the "
                            "percent", pair(eq(a, 2 - r, x), a, 2 - r, x)),
        "swap_factor": ("swapped the starting amount and the growth factor",
                        pair(eq(factor, a, x, head_places=places, base_places=None),
                             factor, a, x)),
        "swap_raw": ("put the percent in front and the starting amount in the base",
                     pair(eq(r, a, x, head_places=places, base_places=None), r, a, x)),
        "swap_other": ("swapped the two numbers and moved the percent the wrong way",
                       pair(eq(2 - factor, a, x, head_places=places, base_places=None),
                            2 - factor, a, x)),
        "power_start": ("raised the starting amount to the power instead of the factor",
                        pair(f"{lhs}{num(a)}^{x}", a, 1, "power")),
        "root_plus": ("halved the exponent and added it on instead of using a factor",
                      pair(f"{lhs}{num(a)}^({x}/2) + {x}", a, 1, "root")),
        "base_two": ("used 2 as the base and put the factor in the exponent",
                     pair(f"{lhs}{num(a)}(2)^({dec(factor, places)}{x})", a, 2, "scaled")),
        "product_power": ("multiplied the starting amount by the factor and raised the "
                          "product to the power",
                          pair(f"{lhs}({num(a)} · {dec(factor, places)})^{x}",
                               a, factor, "product")),
    }
    if d["kind"] == "double":
        pool["halved"] = ("used one-half where the amount doubles",
                          pair(eq(a, Q(1, 2), x, base_places=1), a, Q(1, 2), x))
        order = ["power_start", "halved", "root_plus", "swap_factor"]
    elif d["kind"] == "decay":
        order = ["raw_rate", "grow", "one_plus_factor", "swap_raw", "swap_factor"]
    else:
        order = ["swap_decay", "swap_factor", "decay", "raw_rate"]
        pool["swap_decay"] = ("swapped the two numbers and subtracted the percent "
                              "instead of adding it",
                              pair(eq(1 - r, a, x, head_places=places, base_places=None),
                                   1 - r, a, x))

    stem = d["stem"].format(a=num(a), pct=_pct(r), y=d["y"], x=x, y0=year(y0),
                            y1=year(y1), total=_magnitude(total))
    why = (f"The amount starts at {num(a)} and is multiplied by "
           f"{dec(factor, places) if places else num(factor)} for each {x}, so "
           f"{key}.")
    P = {"kind": "nlf_exp_model", "a": a, "r": [r.numerator, r.denominator],
         "shape": d["kind"], "var": x, "lhs": lhs}
    return text_item("nlfunc.exp_model", "an exponential model from a situation",
                     "medium", seed, stem, key, sig(a, factor, x),
                     pick(pool, order, wrongs), rng, P, why)


# ------------------------------------------------- periods and time units

GATHER = ("On {month} 1, there were {a} views of an advertisement posted on a "
          "website. Every {k} days after {month} 1, the number of views of the "
          "advertisement had increased by {pct} of the number of views {k} days "
          "earlier. The function f gives the predicted number of views {x} days "
          "after {month} 1. Which equation defines f?")
RESCALE = [
    "{rule} The equation above models the number of members, M, of a gym {t} years "
    "after the gym opens. Of the following, which equation models the number of "
    "members of the gym {q} {unit} after the gym opens?",
    "{rule} The given function p models the population of Lowell {t} years after a "
    "census. Which of the following functions best models the population of Lowell "
    "{q} {unit} after the census?",
]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]


def exp_period(rng: random.Random, seed: int, *, mode=None, a=None, r=None, k=None,
               month=None, frame=None, base=None, wrongs=None) -> object:
    """The period the factor belongs to is not the unit the question counts in."""
    mode = mode or rng.choice(["gather", "rescale"])

    if mode == "gather":
        a = int(a if a is not None else rng.randint(40, 900))
        r = q(r if r is not None else Q(rng.randrange(10, 95, 5), 100))
        k = int(k if k is not None else rng.choice([2, 3, 4, 5]))
        month = MONTHS[rng.randrange(12)] if month is None else MONTHS[month]
        factor = 1 + r
        x = "x"

        def eq(base_, expo):
            return f"f(x) = {num(a)}({dec(base_, 2)})^{expo}"

        key = eq(factor, f"(x/{k})")
        pool = {
            "raw_over": ("used the percent itself as the factor",
                         pair(eq(r, f"(x/{k})"), a, r, f"/{k}")),
            "raw_times": ("used the percent itself and multiplied the exponent by the "
                          "period instead of dividing",
                          pair(eq(r, f"({k}x)"), a, r, f"*{k}")),
            "factor_times": ("multiplied the exponent by the period instead of "
                             "dividing by it", pair(eq(factor, f"({k}x)"), a, factor,
                                                    f"*{k}")),
            "no_period": ("applied the factor every day instead of every period",
                          pair(eq(factor, "x"), a, factor, "/1")),
        }
        order = ["raw_over", "raw_times", "factor_times", "no_period"]
        stem = GATHER.format(month=month, a=num(a), k=num(k), pct=_pct(r), x=x)
        why = (f"The count is multiplied by {dec(factor, 2)} every {num(k)} days, so "
               f"after x days it has been multiplied x/{num(k)} times: {key}.")
        P = {"kind": "nlf_exp_period", "mode": mode, "a": a,
             "r": [r.numerator, r.denominator], "k": k}
        return text_item("nlfunc.exp_period", "folding a period into the exponent",
                         "medium", seed, stem, key, sig(a, factor, f"/{k}"),
                         pick(pool, order, wrongs), rng, P, why)

    frame = rng.randrange(len(RESCALE)) if frame is None else frame
    unit, k = ("quarter years", 4) if (k or 4) == 4 else ("months", 12)
    k = int(k)
    a = int(a if a is not None else rng.choice([900, 1200, 1800, 2400, 50000, 90000]))
    base = q(base if base is not None else Q(rng.randrange(102, 112), 100))
    name, t, qv = ("M", "t", "q") if frame == 0 else ("r", "t", "m")
    lhs_key = "M = " if frame == 0 else "r(m) = "
    rule = (f"M = {num(a)}({dec(base, 2)})^t" if frame == 0
            else f"p(t) = {num(a)}({dec(base, 2)})^t")

    def eq(head, b, expo, head_txt=None, b_txt=None):
        h = head_txt if head_txt is not None else num(head)
        bb = b_txt if b_txt is not None else dec(b, 2)
        return f"{lhs_key}{h}({bb})^{expo}"

    key = eq(a, base, f"({qv}/{k})")
    pool = {
        "times": ("multiplied the exponent by the number of periods in a year "
                  "instead of dividing", pair(eq(a, base, f"({k}{qv})"), a, base,
                                              f"*{k}")),
        "divide_rate": ("divided the rate rather than the exponent",
                        pair(eq(a, 1 + (base - 1) / k, f"({k}{qv})",
                                b_txt=dec(1 + (base - 1) / k, 3)),
                             a, 1 + (base - 1) / k, f"*{k}")),
        "power_k": ("raised the base to the number of periods instead of dividing the "
                    "exponent", pair(eq(a, base ** k, qv, b_txt=dec(base ** k, 3)),
                                     a, base ** k, "/1")),
        "divide_coef": ("divided the starting amount by the number of periods",
                        pair(eq(a, base, qv, head_txt=f"{num(a)}/{k}"), Q(a, k), base,
                             "/1")),
        "divide_base": ("divided the base by the number of periods",
                        pair(eq(a, base / k, qv, b_txt=f"{dec(base, 2)}/{k}"),
                             a, base / k, "/1")),
        "divide_both": ("divided the base as well as the exponent",
                        pair(eq(a, base / k, f"({qv}/{k})", b_txt=f"{dec(base, 2)}/{k}"),
                             a, base / k, f"/{k}")),
    }
    order = (["times", "divide_coef", "power_k", "divide_rate"] if frame == 0
             else ["divide_coef", "divide_base", "divide_both", "times"])
    stem = RESCALE[frame].format(rule=rule, t=t, q=qv, unit=unit)
    why = (f"There are {num(k)} {unit} in a year, so {qv} {unit} is {qv}/{num(k)} "
           f"years and the exponent becomes {qv}/{num(k)}.")
    P = {"kind": "nlf_exp_period", "mode": "rescale", "a": a,
         "factor": [base.numerator, base.denominator], "k": k}
    return text_item("nlfunc.exp_period", "changing the unit of time in a model",
                     "hard", seed, stem, key, sig(a, base, f"/{k}"),
                     pick(pool, order, wrongs), rng, P, why)


# ------------------------------------------------------------ from a table

TABLE_MONEY = ("{who} opened a savings account at a bank. The table shows the "
               "exponential relationship between the time t, in years, since {who} "
               "opened the account and the total amount d, in dollars, in the "
               "account. If {who} made no additional deposits or withdrawals, which "
               "of the following equations best represents the relationship between "
               "t and d?")
TABLE_HALVES = ("The table above gives the values of the function f for some values "
                "of x. Which of the following equations could define f?")
WHO = ["Sara", "Maya", "Jonah", "Priya", "Owen", "Rosa"]


def exp_from_table(rng: random.Random, seed: int, *, mode=None, a=None, r=None,
                   base=None, who=None, rows=None, wrongs=None) -> object:
    """A table of an exponential, and the four equations it might come from."""
    mode = mode or rng.choice(["money", "halves"])

    if mode == "money":
        who = who or rng.choice(WHO)
        a = int(a if a is not None else rng.randrange(20, 90) * 10)
        r = q(r if r is not None else Q(rng.randrange(2, 40), 1000))
        rows = int(rows if rows is not None else 3)
        table = [["Time (years)", "Total amount (dollars)"]]
        for t in range(rows):
            table.append([str(t), dec(q(a) * (1 + r) ** t, 2)])
        key = f"d = {num(a)}(1 + {dec(r)})^t"
        pool = {
            "swap": ("put the rate in front and the starting amount inside the "
                     "bracket", pair(f"d = {dec(r)}(1 + {num(a)})^t", r, 1 + a, "t")),
            "linear_product": ("multiplied the rate by the starting amount and the "
                               "time", pair(f"d = {dec(r)}({num(a)}t)", r, a, "linear")),
            "sum": ("added the time to the rate instead of raising a factor to it",
                    pair(f"d = {num(a)}({dec(r)} + t)", a, r, "sum")),
            "no_one": ("left the 1 out of the growth factor",
                       pair(f"d = {num(a)}({dec(r)})^t", a, r, "t")),
        }
        order = ["swap", "linear_product", "sum", "no_one"]
        stem = TABLE_MONEY.format(who=who)
        why = (f"The amount starts at {dec(q(a), 2)} and is multiplied by "
               f"{dec(1 + r)} each year, so d = {num(a)}(1 + {dec(r)})^t.")
        P = {"kind": "nlf_exp_table", "mode": mode, "a": a,
             "r": [r.numerator, r.denominator], "rows": rows}
        return text_item("nlfunc.exp_from_table", "an exponential fitted to a table",
                         "medium", seed, stem, key, sig(a, 1 + r, "t"),
                         pick(pool, order, wrongs), rng, P, why, table=table)

    a = int(a if a is not None else rng.randint(2, 12))
    base = int(base if base is not None else rng.choice([2, 3, 4, 5]))
    rows = int(rows if rows is not None else 4)
    table = [["x", "f(x)"]]
    for t in range(rows):
        table.append([str(t), num(Q(a, base ** t))])
    key = f"f(x) = {num(a)}({base}^({MINUS}x))"
    pool = {
        "shift_up": ("shifted the exponent up by one instead of changing its sign",
                     pair(f"f(x) = {num(a)}({base}^(x + 1))", a, base, "x+1")),
        "no_sign": ("left the sign of the exponent positive",
                    pair(f"f(x) = {num(a)}({base}^x)", a, base, "x")),
        "shift_neg": ("negated a shifted exponent rather than the exponent itself",
                      pair(f"f(x) = {num(a)}({base}^({MINUS}(x + 1)))", a, base,
                           "-(x+1)")),
        "half_base": ("halved the base instead of inverting it",
                      pair(f"f(x) = {num(a)}(({base}/2)^x)", a, Q(base, 2), "x")),
    }
    order = ["shift_up", "no_sign", "shift_neg", "half_base"]
    why = (f"Each step divides the output by {num(base)}, so f(x) = "
           f"{num(a)}({base}^({MINUS}x)).")
    P = {"kind": "nlf_exp_table", "mode": "halves", "a": a, "base": base, "rows": rows}
    return text_item("nlfunc.exp_from_table", "an exponential fitted to a table",
                     "medium", seed, TABLE_HALVES, key, sig(a, base, "-x"),
                     pick(pool, order, wrongs), rng, P, why, table=table)


# ----------------------------------------------------- cooling toward a room

OFFSET = ("{who} measured the temperature of a cup of {drink} placed in a room with "
          "a constant temperature of {amb} degrees Fahrenheit (°F). The temperature "
          "of the {drink} was {t0}°F at {h}:00 p.m. when it started cooling. The "
          "temperature of the {drink} was {t1}°F at {h}:{m1} p.m. and {t2}°F at "
          "{h}:{m2} p.m. The {drink}'s temperature continued to decrease. Of the "
          "following functions, which best models the temperature T(m), in degrees "
          "Fahrenheit, of {who}'s {drink} m minutes after it started cooling?")
DRINKS = ["hot chocolate", "coffee", "tea"]


def exp_offset(rng: random.Random, seed: int, *, amb=None, t0=None, f=None, k=None,
               who=None, drink=None, hour=None, wrongs=None) -> object:
    """A cooling curve: the model approaches the room, it does not approach zero."""
    who = who or rng.choice(WHO + ["Kao", "Devi"])
    drink = drink or rng.choice(DRINKS)
    amb = int(amb if amb is not None else rng.randrange(60, 76))
    diff = int(rng.randrange(60, 140)) if t0 is None else int(t0) - amb
    t0 = amb + diff
    f = q(f if f is not None else rng.choice([Q(3, 4), Q(4, 5), Q(7, 10)]))
    k = int(k if k is not None else rng.choice([5, 10]))
    hour = int(hour if hour is not None else rng.randint(1, 9))
    if not (0 < f < 1) or diff <= 20:
        raise ItemError("the drink must start well above the room and cool toward it")
    v1, v2 = amb + diff * f, amb + diff * f * f
    for v in (v1, v2):
        if (v - Q(1, 2)).denominator == 1:
            raise ItemError("a printed temperature would sit halfway between degrees")
    t1, t2 = _round(v1), _round(v2)
    if not (amb < t2 < t1 < t0):
        raise ItemError("the printed temperatures must fall toward the room")
    key = f"T(m) = {num(amb)} + {num(diff)}({dec(f, 2)})^(m/{k})"
    pool = {
        "grow_per_minute": ("read the factor as a rise and applied it every minute",
                            pair(f"T(m) = {num(t0)}({dec(2 - f, 2)})^m", t0, 2 - f,
                                 f"/1", "none")),
        "decay_per_minute": ("applied the five-minute factor every minute and ignored "
                             "the room", pair(f"T(m) = {num(t0)}({dec(f, 2)})^m", t0, f,
                                              "/1", "none")),
        "diff_only": ("cooled the difference correctly but never added the room back "
                      "on", pair(f"T(m) = ({num(t0)} {MINUS} {num(amb)})({dec(f, 2)})"
                                 f"^(m/{k})", diff, f, f"/{k}", "none")),
        "start_only": ("started from the whole temperature rather than from the "
                       "difference", pair(f"T(m) = {num(amb)} + {num(t0)}"
                                          f"({dec(f, 2)})^(m/{k})", t0, f, f"/{k}",
                                          "amb")),
    }
    order = ["grow_per_minute", "decay_per_minute", "diff_only", "start_only"]
    m1 = f"{k:02d}" if k < 10 else str(k)
    m2 = f"{2 * k:02d}" if 2 * k < 10 else str(2 * k)
    stem = OFFSET.format(who=who, drink=drink, amb=num(amb), t0=num(t0), t1=num(t1),
                         t2=num(t2), h=hour, m1=m1, m2=m2)
    why = (f"Only the {num(diff)}°F above the room cools, and it is multiplied by "
           f"{dec(f, 2)} every {num(k)} minutes, so {key}.")
    P = {"kind": "nlf_exp_offset", "amb": amb, "diff": diff,
         "f": [f.numerator, f.denominator], "k": k}
    return text_item("nlfunc.exp_offset", "cooling toward a fixed temperature", "hard",
                     seed, stem, key, sig(diff, f, f"/{k}", "amb"),
                     pick(pool, order, wrongs), rng, P, why)


def _round(v) -> int:
    v = q(v)
    n = v.numerator * 2 + (v.denominator if v >= 0 else -v.denominator)
    return int(n // (2 * v.denominator))


# ---------------------------------------- the value given is not the start

ANCHOR = ("A model estimates that at the end of each year from {y0} to {y1}, the "
          "number of {thing} in a population was {pct} more than the number of "
          "{thing} in the population at the end of the previous year. The model "
          "estimates that at the end of {y2}, there were {v} {thing} in the "
          "population. Which of the following equations represents this model, where "
          "n is the estimated number of {thing} in the population t years after the "
          "end of {y0} and t ≤ {span}?")
CRITTERS = ["squirrels", "rabbits", "finches", "beetles"]


def exp_anchor(rng: random.Random, seed: int, *, r=None, v=None, y0=None, span=None,
               thing=None, wrongs=None) -> object:
    """A later reading is given; the model's coefficient has to be worked back."""
    thing = thing or rng.choice(CRITTERS)
    r = q(r if r is not None else Q(rng.randrange(50, 300, 25), 100))
    if r == 1:
        # the "read the percent as the factor" option would be a base of 1,
        # which is not a model at all
        raise ItemError("a rise of exactly 100% degenerates one of the options")
    factor = 1 + r
    span = int(span if span is not None else rng.randint(4, 6))
    y0 = int(y0 if y0 is not None else rng.randrange(1995, 2018))
    v = int(v if v is not None else rng.randrange(4, 40) * 10)
    start = q(v) / factor
    if start.denominator != 1 or start <= 0:
        raise ItemError("the starting count must be a whole number")
    key = f"n = {num(start)}({dec(factor)})^t"
    pool = {
        "wrong_factor": ("read the percent as the factor itself",
                         pair(f"n = {num(start)}({dec(r)})^t", start, r)),
        "given_value": ("used the count a year later as the starting count",
                        pair(f"n = {num(v)}({dec(factor)})^t", v, factor)),
        "given_wrong": ("used the later count and read the percent as the factor",
                        pair(f"n = {num(v)}({dec(r)})^t", v, r)),
        "double": ("doubled the factor instead of adding the percent to 1",
                   pair(f"n = {num(start)}({dec(2 * r)})^t", start, 2 * r)),
    }
    order = ["wrong_factor", "given_value", "given_wrong", "double"]
    stem = ANCHOR.format(y0=year(y0), y1=year(y0 + span), y2=year(y0 + 1),
                         pct=_pct(r), v=num(v), thing=thing, span=num(span))
    why = (f"A rise of {_pct(r)} multiplies by {dec(factor)}, so the count at the "
           f"end of {year(y0)} was {num(v)}/{dec(factor)} = {num(start)}.")
    P = {"kind": "nlf_exp_anchor", "v": v, "factor": [factor.numerator, factor.denominator]}
    return text_item("nlfunc.exp_anchor", "working an exponential back to its start",
                     "hard", seed, stem, key, sig(start, factor),
                     pick(pool, order, wrongs), rng, P, why)


# --------------------------------------- the equation that would be solved

REACH = ("The population of a town is currently {a}, and the population is estimated "
         "to increase each year by {pct} from the previous year. Which of the "
         "following equations can be used to estimate the number of years, t, it "
         "will take for the population of the town to reach {b}?")


def exp_reach(rng: random.Random, seed: int, *, a=None, b=None, r=None,
              wrongs=None) -> object:
    """Not the answer but the equation: which one would you solve for t?"""
    a = int(a if a is not None else rng.randrange(10, 90) * 1000)
    b = int(b if b is not None else a + rng.randrange(1, 9) * 5000)
    r = q(r if r is not None else Q(rng.randrange(2, 10), 100))
    if b <= a:
        raise ItemError("the target must be above the current population")
    factor = 1 + r
    key = f"{num(b)} = {num(a)}({dec(factor, 2)})^t"
    pool = {
        "swapped_raw": ("wrote the equation backwards and used the percent as the "
                        "factor", pair(f"{num(a)} = {num(b)}({dec(r, 2)})^t", a, b, r)),
        "swapped_percent": ("wrote the equation backwards and used the percent as a "
                            "whole number", pair(f"{num(a)} = {num(b)}({num(100 * r)})^t",
                                                 a, b, 100 * r)),
        "raw": ("used the percent itself as the growth factor",
                pair(f"{num(b)} = {num(a)}({dec(r, 2)})^t", b, a, r)),
        "swapped": ("wrote the equation with the two populations the wrong way round",
                    pair(f"{num(a)} = {num(b)}({dec(factor, 2)})^t", a, b, factor)),
    }
    order = ["swapped_raw", "swapped_percent", "raw", "swapped"]
    why = (f"Starting at {num(a)} and multiplying by {dec(factor, 2)} each year gives "
           f"{num(a)}({dec(factor, 2)})^t, and that reaches {num(b)}.")
    P = {"kind": "nlf_exp_reach", "a": a, "b": b,
         "factor": [factor.numerator, factor.denominator]}
    return text_item("nlfunc.exp_reach", "the equation a growth question would solve",
                     "hard", seed, REACH.format(a=num(a), b=num(b), pct=_pct(r)), key,
                     sig(b, a, factor), pick(pool, order, wrongs), rng, P, why)
