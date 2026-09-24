"""Arithmetic on the mean, and reasoning that stops short of arithmetic.

Everything here turns on one identity -- total = mean x count -- or on what
that identity does not tell you. The second half matters as much as the first:
a mean orders two totals, never two individuals, and the items that say so are
the ones students lose.
"""

from __future__ import annotations

import random
from fractions import Fraction as F

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text, gridin_mistakes
from ..common import (assemble_num, clean, count_word, listing, mean, median,
                      num_str, ordinal, plural, q, round_to, values_line)
from .compare import ONE_TWO, one_two, one_two_options

__all__ = ["unknown_value", "mean_totals", "mean_identity", "reason_center",
           "must_be_true"]


def _num_item(rng, name, skill, difficulty, seed, stem, fmt, key, mistakes, rationale,
              params, table=None, places=None) -> Item:
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("a grid-in answer must be enterable as digits")
        return Item(name, skill, difficulty, seed, stem, "spr", key, key.gridin(),
                    rationale, table=table, params=params,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble_num(key, mistakes, rng, places=places)
    return Item(name, skill, difficulty, seed, stem, "mcq", key, letter, rationale,
                choices, reasons, latex, table=table, params=params)


# ------------------------------------------------------- THE MISSING VALUE

ROCK_CONTEXTS = [
    ("Andrew", "Maria", "rocks", "masses", "kilogram", "Masses (kilograms)"),
    ("Priya", "Luis", "samples", "masses", "gram", "Masses (grams)"),
    ("Nadia", "Omar", "parcels", "weights", "pound", "Weights (pounds)"),
]


def unknown_value(rng: random.Random, seed: int, *, mode=None, a=None, b=None, d=0,
                  values=None, wrong=None, bound=None, names=("A", "B"),
                  context=None, presentation=None, intro=None, ask_phrase=None,
                  fmt=None, places=None, only=None) -> Item:
    """Solve a data set for the one value it does not show."""
    mode = mode or rng.choice(["equal_means", "mean_equals_median", "integer_mean"])
    if mode == "equal_means":
        return _equal_means(rng, seed, a, b, d, names, context, presentation, intro,
                            ask_phrase, fmt, places, only)
    if mode == "mean_equals_median":
        return _mean_equals_median(rng, seed, values, wrong, intro, ask_phrase)
    return _integer_mean(rng, seed, values, bound, intro, ask_phrase, fmt)


def _equal_means(rng, seed, a, b, d, names, context, presentation, intro, ask_phrase,
                 fmt, places, only) -> Item:
    presentation = presentation or rng.choice(["lists", "table"])
    if a is None:
        n = rng.choice([5, 6])
        base = rng.randint(20, 80)
        a = [base + rng.randint(-8, 8) for _ in range(n)]
        b = [base + rng.randint(-14, 14) for _ in range(n - 1)]
        d = 0
    A = [q(v) for v in a]
    known = [q(v) for v in b]
    n = len(A)
    if len(known) != n - 1:
        raise ItemError("exactly one value of the second data set is unknown")
    target = mean(A) + q(d)
    x = target * n - sum(known, F(0))
    if x <= 0:
        raise ItemError("the missing value must be positive")
    key = E(clean(x))
    an, bn = names
    cands = {
        "in_list": Mis(f"read off the greatest value data set {bn} already shows",
                       E(max(known))),
        "gap": Mis("added the gap between the two means to the mean instead of "
                   "scaling by the number of values",
                   E(target + (target - mean(known)))),
        "target": Mis("wrote down the mean the two data sets share, not the value that "
                      "produces it", E(target)),
        "known_mean": Mis(f"averaged only the values data set {bn} already shows",
                          E(mean(known))),
        "short_count": Mis("multiplied the mean by one less than the number of values",
                           E(target * (n - 1) - sum(known, F(0)))
                           if target * (n - 1) - sum(known, F(0)) > 0 else None),
        "median_match": Mis("found the value that makes the two medians agree instead "
                            "of the two means", E(median(A))),
    }
    order = list(only) if only else list(cands)
    mistakes = [cands[k] for k in order if k in cands and cands[k].value is not None]

    table = None
    if presentation == "table":
        p1, p2, things, quant, unit, head = context or rng.choice(ROCK_CONTEXTS)
        table = [[""] + [head] + [""] * (n - 1),
                 [p1] + [num_str(v) for v in A],
                 [p2] + ["x"] + [num_str(v) for v in known]]
        rel = (f"{num_str(abs(q(d)))} {unit} "
               f"{'greater' if q(d) > 0 else 'less'} than" if q(d) else "equal to")
        stem = (intro or f"{p1} and {p2} each collected {count_word(n)} {things}, and "
                f"the {quant} of the {things} are shown in the table above.") + " " + (
            ask_phrase or f"The mean of the {quant} of the {things} {p2} collected is "
            f"{rel} the mean of the {quant} of the {things} {p1} collected. What is the "
            f"value of x ?")
    else:
        rel = (f"{num_str(abs(q(d)))} {'greater' if q(d) > 0 else 'less'} than"
               if q(d) else "equal to")
        stem = (f"Data set {an}: {values_line(A)}\n"
                f"Data set {bn}: {values_line(known)}, x\n"
                + (intro or f"Data set {an} and data set {bn} each contain {n} numbers.")
                + " " + (ask_phrase or f"If the mean of data set {an} is {rel} the mean "
                         f"of data set {bn}, what is the value of x ?"))
    P = {"kind": "ovd_unknown_value", "mode": "equal_means",
         "a": [float(v) for v in A], "known": [float(v) for v in known],
         "d": float(q(d))}
    rationale = (f"The {n} values of the first data set have mean {num_str(mean(A))}, so "
                 f"the second must total {num_str(target * n)}; it already shows "
                 f"{num_str(sum(known, F(0)))}.")
    return _num_item(rng, "ovd.unknown.equal_means", "solving for a missing value",
                     "medium", seed, stem, fmt or "mcq", key, mistakes, rationale, P,
                     table=table, places=places)


def _mean_equals_median(rng, seed, values, wrong, intro, ask_phrase) -> Item:
    if values is None:
        base = rng.randint(8, 40)
        values = sorted({base + rng.randint(0, 9) for _ in range(6)})[:4]
    k = sorted(q(v) for v in values)
    if len(k) != 4:
        raise ItemError("this item shows four values and one unknown")
    S = sum(k, F(0))
    works: list[tuple[F, str]] = []
    low = 5 * k[1] - S
    if low <= k[1]:
        works.append((low, "as the least of the five, leaving the middle value where "
                           "it is"))
    mid = S / 4
    if k[1] <= mid <= k[2]:
        works.append((mid, "as the middle value of the five itself"))
    high = 5 * k[2] - S
    if high >= k[2]:
        works.append((high, "as the greatest of the five, leaving the middle value "
                            "where it is"))
    if len(works) < 3 or len({v for v, _ in works}) < 3:
        raise ItemError("this list does not give three separate possible values")
    lowest = min(v for v, _ in works)
    key = E(q(wrong) if wrong is not None else lowest - rng.randint(2, 8))
    if any(q(key.coef) == v for v, _ in works) or key.coef <= 0:
        raise ItemError("the value offered as impossible is in fact possible")
    mistakes = [Mis(f"a value that does make the mean and the median equal, with x "
                    f"{why}", E(v)) for v, why in works]
    stem = (f"{values_line(values)}, x\n"
            + (intro or "The mean and the median of the five numbers above are equal.")
            + " " + (ask_phrase or "Which of the following is NOT a possible value of "
                     "x ?"))
    P = {"kind": "ovd_unknown_value", "mode": "mean_equals_median",
         "values": [float(v) for v in k], "wrong": float(key.coef)}
    rationale = (f"x can be {listing([num_str(v) for v, _ in works])}, depending on "
                 f"where it falls in the order; {num_str(key.coef)} is not one of them.")
    return _num_item(rng, "ovd.unknown.mean_equals_median", "mean and median together",
                     "hard", seed, stem, "mcq", key, mistakes, rationale, P)


def _integer_mean(rng, seed, values, bound, intro, ask_phrase, fmt) -> Item:
    if values is None:
        n = rng.choice([9, 9, 11])
        m = rng.randint(20, 60)
        values = [m + rng.randint(-5, 5) for _ in range(n - 1)]
        values[-1] += m * (n - 1) - sum(values)
        bound = m + rng.randint(12, 25)
    vals = [q(v) for v in values]
    n = len(vals) + 1
    bound = bound or int(max(vals)) + 20
    S = sum(vals, F(0))
    m = S / len(vals)
    if m.denominator != 1:
        raise ItemError("the stated mean of the listed values must be a whole number")
    fits = [x for x in range(1, int(bound))
            if (S + x) % n == 0 and (S + x) / n > m]
    if len(fits) != 1:
        raise ItemError(f"{len(fits)} values of the missing integer fit, not one")
    x = q(fits[0])
    key = E(max(max(vals), x))
    stem = ((intro or f"Data set A consists of {n} positive integers less than "
             f"{bound}. The list shown gives {n - 1} of the integers from data set A.")
            + f"\n{values_line(vals)}\n"
            + (ask_phrase or f"The mean of these {n - 1} integers is {num_str(m)}. If "
               f"the mean of data set A is an integer that is greater than {num_str(m)}, "
               f"what is the value of the largest integer from data set A?"))
    mistakes = [
        Mis("read off the largest integer the list already shows", E(max(vals))),
        Mis("used the smallest whole-number mean above the one given", E((m + 1))),
        Mis("added the two means instead of the totals", E(m + x) if m + x != key.coef
            else None),
    ]
    P = {"kind": "ovd_unknown_value", "mode": "integer_mean",
         "values": [float(v) for v in vals], "bound": int(bound)}
    rationale = (f"The {n - 1} listed integers total {num_str(S)}. Only "
                 f"{num_str(x)} makes {num_str(S)} + x divide by {n} to give a whole "
                 f"number above {num_str(m)}.")
    return _num_item(rng, "ovd.unknown.integer_mean", "an integer mean", "hard", seed,
                     stem, fmt or "spr", key, mistakes, rationale, P)


# --------------------------------------------------------------- TOTALS

REMOVE_CONTEXTS = [
    {"who": "players in a basketball game", "quantity": "score", "plural": "scores",
     "unit": "points", "verb": "removed",
     "opening": "The mean score of {n} players in a basketball game was {m1} points.",
     "change": "If the highest individual score is removed, the mean score of the "
               "remaining {k} players becomes {m2} points.",
     "ask": "What was the highest score?"},
    {"who": "employees of a construction company", "quantity": "time",
     "plural": "times", "unit": "years", "verb": "left",
     "opening": "The mean amount of time that the {n} employees of a construction "
                "company have worked for the company is {m1} years.",
     "change": "After one of the employees leaves the company, the mean amount of time "
               "that the remaining employees have worked for the company is reduced to "
               "{m2} years.",
     "ask": "How many years did the employee who left the company work for the "
            "company?"},
    {"who": "trees in an orchard", "quantity": "height", "plural": "heights",
     "unit": "feet", "verb": "removed",
     "opening": "The mean height of the {n} trees in an orchard is {m1} feet.",
     "change": "After the tallest tree is cut down, the mean height of the remaining "
               "{k} trees is {m2} feet.",
     "ask": "What was the height, in feet, of the tree that was cut down?"},
]

COMBINE_CONTEXTS = [
    ("objects", "heights", "meters"), ("boxes", "masses", "kilograms"),
    ("trips", "distances", "kilometers"), ("plants", "heights", "centimeters"),
]


def mean_totals(rng: random.Random, seed: int, *, mode=None, n=None, m1=None, m2=None,
                n1=None, n2=None, context=None, names=("A", "B", "C"), intro=None,
                ask_phrase=None, fmt=None, places=None, only=None) -> Item:
    """total = mean x count, run forwards and backwards."""
    mode = mode or rng.choice(["removed", "combined"])
    if mode == "removed":
        ctx = context or rng.choice(REMOVE_CONTEXTS)
        n = n or rng.randint(6, 25)
        m1 = q(m1) if m1 is not None else q(rng.randint(8, 60)) + q(rng.choice([0, 5]))/10
        drop = q(rng.randint(1, 6)) / rng.choice([1, 2, 4])
        m2 = q(m2) if m2 is not None else m1 - drop
        m1, m2 = q(m1), q(m2)
        if m2 >= m1 or n < 3:
            raise ItemError("removing the largest value must pull the mean down")
        key = E(clean(n * m1 - (n - 1) * m2))
        if key.coef <= 0:
            raise ItemError("the removed value must be positive")
        cands = {
            "same_count": Mis(f"subtracted {n} times the new mean instead of {n - 1} "
                              f"times", E(n * m1 - n * m2)),
            "mean_drop": Mis("reported how far the mean fell, not the value that was "
                             "taken away", E(m1 - m2)),
            "swapped": Mis("swapped the two counts, using one fewer for the original "
                           "group", E((n - 1) * m1 - n * m2)),
            "sum_means": Mis("added the two means", E(m1 + m2)),
            "scaled_drop": Mis("multiplied the fall in the mean by one less than the "
                               "original count", E((n - 1) * (m1 - m2))),
        }
        order = list(only) if only else list(cands)
        mistakes = [cands[k] for k in order if k in cands]
        fill = {"n": n, "k": n - 1, "m1": num_str(m1), "m2": num_str(m2)}
        stem = ((intro or ctx["opening"].format(**fill)) + " "
                + ctx["change"].format(**fill) + " "
                + (ask_phrase or ctx["ask"].format(**fill)))
        P = {"kind": "ovd_mean_totals", "mode": "removed", "n": int(n),
             "m1": float(m1), "m2": float(m2)}
        rationale = (f"The {n} values total {num_str(n * m1)} and the {n - 1} that "
                     f"remain total {num_str((n - 1) * m2)}, a difference of "
                     f"{num_str(q(key.coef))}.")
        return _num_item(rng, "ovd.mean.removed", "mean and total", "hard", seed, stem,
                         fmt or "mcq", key, mistakes, rationale, P, places=places)

    things, quantity, unit = context or rng.choice(COMBINE_CONTEXTS)
    n1 = n1 or rng.randint(20, 90)
    n2 = n2 or rng.randint(20, 90)
    m1 = q(m1) if m1 is not None else q(rng.randint(10, 80))
    m2 = q(m2) if m2 is not None else q(rng.randint(10, 80))
    if m1 == m2:
        raise ItemError("two equal means make the weighting invisible")
    key = E(clean((n1 * m1 + n2 * m2) / (n1 + n2)))
    an, bn, cn = names
    mistakes = [
        Mis("averaged the two means without weighting them by the number of values "
            "in each data set", E((m1 + m2) / 2)),
        Mis("weighted each mean by the other data set's count",
            E((n2 * m1 + n1 * m2) / (n1 + n2))),
        Mis("added the two means", E(m1 + m2)),
        Mis(f"reported the mean of data set {an} alone", E(m1)),
        Mis(f"reported the mean of data set {bn} alone", E(m2)),
    ]
    stem = (intro or
            f"Data set {an} consists of the {quantity} of {n1} {things} and has a mean "
            f"of {num_str(m1)} {unit}. Data set {bn} consists of the {quantity} of "
            f"{n2} {things} and has a mean of {num_str(m2)} {unit}. Data set {cn} "
            f"consists of the {quantity} of the {n1 + n2} {things} from data sets {an} "
            f"and {bn}.") + " " + (
        ask_phrase or f"What is the mean, in {unit}, of data set {cn}?")
    P = {"kind": "ovd_mean_totals", "mode": "combined", "n1": int(n1), "n2": int(n2),
         "m1": float(m1), "m2": float(m2)}
    total = n1 * m1 + n2 * m2
    rationale = (f"The two data sets total {num_str(n1 * m1)} and {num_str(n2 * m2)}, "
                 f"so all {n1 + n2} values total {num_str(total)}, and the mean is "
                 f"{num_str(total)} ÷ {n1 + n2} = {num_str(q(key.coef))}.")
    return _num_item(rng, "ovd.mean.combined", "combining two data sets", "hard", seed,
                     stem, fmt or "spr", key, mistakes, rationale, P, places=places)


# ------------------------------------------------------------ IDENTITIES

def mean_identity(rng: random.Random, seed: int, *, mode=None, n=None, values=None,
                  start=None, intro=None, ask_phrase=None, fmt=None) -> Item:
    """Two facts about the mean that hold whatever the numbers are."""
    mode = mode or rng.choice(["consecutive", "fraction_of_sum"])
    if mode == "consecutive":
        n = n or rng.choice([5, 7, 9, 11, 13, 15, 21, 25])
        if n % 2 == 0:
            raise ItemError("the wording of this item assumes an odd count")
        key = E(0)
        stem = (intro or "") + (
            ask_phrase or f"If a is the mean and b is the median of {count_word(n)} "
            f"consecutive integers, what is the value of |a − b| ?")
        mistakes = [
            Mis("took the mean to sit one step above the middle integer", E(1)),
            Mis("took the difference between the middle integer and the one after it, "
                "doubled", E(2)),
            Mis(f"reported the count of the integers", E(n)),
            Mis("halved the count", E(F(n, 2))),
        ]
        P = {"kind": "ovd_mean_identity", "mode": "consecutive", "n": int(n)}
        rationale = (f"Consecutive integers are evenly spaced about their middle value, "
                     f"so the mean and the median are the same number.")
        return _num_item(rng, "ovd.mean.consecutive", "mean and median together",
                         "medium", seed, stem.strip(), fmt or "spr", key, mistakes,
                         rationale, P)

    if values is None:
        n = n or rng.choice([4, 5, 5, 8, 10, 20])
        values = [rng.randint(1, 20) for _ in range(n)]
    vals = [q(v) for v in values]
    n = len(vals)
    key = E(F(1, n))
    stem = (f"{values_line(vals)}\n" + (intro or "") +
            (ask_phrase or "The mean of the list of numbers above is what fraction of "
             "the sum of the five numbers?".replace("five", count_word(n))))
    mistakes = [
        Mis("reported the number of values instead of the fraction", E(n)),
        Mis("divided by one less than the number of values", E(F(1, n - 1))),
        Mis("divided by one more than the number of values", E(F(1, n + 1))),
        Mis("reported the mean itself rather than its share of the total",
            E(mean(vals))),
    ]
    P = {"kind": "ovd_mean_identity", "mode": "fraction_of_sum", "n": int(n),
         "values": [float(v) for v in vals]}
    rationale = (f"The mean is the sum divided by {n}, so it is one {ordinal(n)} of the "
                 f"sum whatever the numbers are.")
    return _num_item(rng, "ovd.mean.fraction_of_sum", "mean as a share of the total",
                     "medium", seed, stem, fmt or "spr", key, mistakes, rationale, P)


# ------------------------------------------------------------- REASONING

CALC_CONTEXTS = [
    ("For a school fund-raiser, {n} students sold a total of {t} boxes of cookies.",
     "boxes", "student", "students", "boxes sold"),
    ("On one shift, {n} volunteers answered a total of {t} calls.",
     "calls", "volunteer", "volunteers", "calls answered"),
    ("Over one week, {n} machines produced a total of {t} parts.",
     "parts", "machine", "machines", "parts produced"),
    ("During a food drive, {n} classes collected a total of {t} cans.",
     "cans", "class", "classes", "cans collected"),
]

FISH_CONTEXTS = [
    {"intro": "A fish hatchery has three tanks for holding fish before they are "
              "introduced into the wild.", "unit": "ounces", "thing": "fish",
     "plural": "fish", "verb": "weighing", "measure": "weights",
     "place": ["tank A", "tank B", "tank C"]},
    {"intro": "A nursery sorts its seedlings into three trays.", "unit": "centimeters",
     "thing": "seedling", "plural": "seedlings", "verb": "measuring",
     "measure": "heights", "place": ["tray 1", "tray 2", "tray 3"]},
]


def reason_center(rng: random.Random, seed: int, *, mode=None, n=None, total=None,
                  counts=None, bounds=None, options=None, context=None, intro=None,
                  ask_phrase=None) -> Item:
    """What a total, or a set of ranges, does and does not settle."""
    mode = mode or rng.choice(["calculable", "median_interval"])
    if mode == "calculable":
        opening, items, one, many, doing = context or rng.choice(CALC_CONTEXTS)
        n = n or rng.randint(5, 40)
        total = total or n * rng.randint(3, 30) + rng.randint(0, n - 1)
        key = f"The average number of {items} sold per {one}" if items == "boxes" else \
              f"The average number of {items} per {one}"
        verb = "sold" if items == "boxes" else ""
        def opt(word):
            return (f"The {word} number of {items} {verb} per {one}".replace("  ", " ")
                    if word == "median" else
                    f"The {word} number of {items} {verb} by one {one}".replace("  ", " "))
        key = opt("average")
        distractors = [
            Mis(f"the median needs each {one}'s own count, which a total does not give",
                opt("median")),
            Mis(f"a total cannot say how much the busiest {one} accounted for",
                opt("greatest")),
            Mis(f"a total cannot say how little the quietest {one} accounted for",
                opt("least")),
        ]
        key = f"The average number of {items} {verb} per {one}".replace("  ", " ")
        stem = (intro or opening.format(n=n, t=f"{total:,}")) + " " + (
            ask_phrase or "Which of the following can be calculated from this "
            "information?")
        opts, reasons, letter = assemble_text(key, distractors, rng)
        P = {"kind": "ovd_reason_center", "mode": "calculable", "n": int(n),
             "total": int(total),
             "claim": f"The {{word}} number of {items} {verb} per {one}".replace(
                 "  ", " ")}
        rationale = (f"Dividing the total by the number of {many} gives the average; "
                     f"nothing else here can be recovered without the individual "
                     f"counts.")
        return Item("ovd.reason.calculable", "what a total settles", "easy", seed, stem,
                    "mcq", E(0), letter, rationale, opts, reasons, list(opts), params=P)

    ctx = context or rng.choice(FISH_CONTEXTS)
    counts = counts or [rng.randint(6, 14) for _ in range(3)]
    if sum(counts) % 2 == 0:
        raise ItemError("an even total leaves the median between two values")
    bounds = bounds or sorted(rng.sample(range(3, 30), 2))
    b1, b2 = q(bounds[0]), q(bounds[1])
    N = sum(counts)
    pos = (N + 1) // 2
    band = 0 if pos <= counts[0] else (1 if pos <= counts[0] + counts[1] else 2)

    def could_be(v) -> bool:
        """Whether the median could be this value, with the boundaries read as
        the stem words them: below the first bound, from it up to the second,
        or above the second."""
        return [q(v) < b1, b1 <= q(v) <= b2, q(v) > b2][band]

    if options is None:
        inside = {0: b1 / 2, 1: (b1 + b2) / 2, 2: b2 + 2}[band]
        # more impossible values than the three that are wanted: bounds one
        # apart make several of them coincide, and three distinct ones are
        # still needed. Coming up short is worse than it sounds -- `assemble`
        # pads a short list with a multiple of the key, and half of a value
        # inside the band is another value inside the band
        pool = {0: [b1 + F(1, 2), (b1 + b2) / 2, b2 + 2, b2 + F(1, 2), b1, b2],
                1: [b1 / 2, b2 + F(1, 2), b2 + 2, b1 - F(1, 2), b2 + 3],
                2: [b1 / 2, (b1 + b2) / 2, b2 - F(1, 2), b1, b2]}[band]
        outside = []
        for v in pool:
            if len(outside) == 3:
                break
            if not could_be(v) and v > 0 and v not in outside:
                outside.append(v)
        if len(outside) < 3:
            raise ItemError("these bounds do not give three impossible values")
        options = [inside] + outside
    key = E(q(options[0]))
    if not could_be(key.coef):
        raise ItemError("the keyed value is not inside the band that holds the median")
    others = list(options[1:])
    if len(others) < 3 or any(could_be(v) for v in others):
        raise ItemError("an option other than the key could also be the median")
    where = ctx["place"]
    mistakes = []
    for v in others:
        v = q(v)
        if band != 0 and v <= b1:
            mistakes.append(Mis(f"counted in from the wrong end, landing among the "
                                f"{ctx['plural']} in {where[0]}", E(v)))
        elif band != 2 and v > b2:
            why = (f"stepped just past the largest value {where[1]} holds"
                   if v - b2 <= 1 else
                   f"picked a value from {where[2]}, but the {ordinal(pos)} of {N} "
                   f"{ctx['plural']} is in {where[1]}")
            mistakes.append(Mis(why, E(v)))
        elif band != 1 and b1 <= v <= b2:
            mistakes.append(Mis(f"picked a value from {where[1]}, but the "
                                f"{ordinal(pos)} of {N} {ctx['plural']} is in "
                                f"{where[band]}", E(v)))
        elif v != key.coef:
            mistakes.append(Mis(f"read the boundary of {where[band]} rather than a "
                                f"value inside it", E(v)))
    parts = [f"{count_word(counts[0]).capitalize()} {ctx['plural']} {ctx['verb']} less "
             f"than {num_str(b1)} {ctx['unit']} are placed in {where[0]}.",
             f"{count_word(counts[1]).capitalize()} {ctx['plural']} {ctx['verb']} at "
             f"least {num_str(b1)} {ctx['unit']} but no more than {num_str(b2)} "
             f"{ctx['unit']} are placed in {where[1]}.",
             f"{count_word(counts[2]).capitalize()} {ctx['plural']} {ctx['verb']} more "
             f"than {num_str(b2)} {ctx['unit']} are placed in {where[2]}."]
    stem = (intro or ctx["intro"]) + " " + " ".join(parts) + " " + (
        ask_phrase or f"Which of the following could be the median of the "
        f"{ctx['measure']}, in {ctx['unit']}, of these {N} {ctx['plural']}?")
    P = {"kind": "ovd_reason_center", "mode": "median_interval",
         "counts": [int(c) for c in counts], "bounds": [float(b1), float(b2)],
         "options": [float(key.coef)] + [float(q(v)) for v in others]}
    rationale = (f"With {N} values the median is the {ordinal(pos)} one in order, "
                 f"which falls in {where[band]}.")
    return _num_item(rng, "ovd.reason.median_interval", "where a median must lie",
                     "medium", seed, stem, "mcq", key, mistakes, rationale, P)


# ----------------------------------------------------------- MUST BE TRUE

TEAM_CONTEXTS = [
    {"unit": "minutes", "group": "team", "member": "member", "members": "members",
     "doing": "completed the race", "time": "completion time",
     "times": "completion times", "more": "took more time to complete the race",
     "less": "completed the race in less time"},
    {"unit": "seconds", "group": "class", "member": "student", "members": "students",
     "doing": "finished the puzzle", "time": "finishing time",
     "times": "finishing times", "more": "took more time to finish the puzzle",
     "less": "finished the puzzle in less time"},
]


def must_be_true(rng: random.Random, seed: int, *, mode=None, n=None, m1=None, m2=None,
                 size=None, lo=None, hi=None, extra=None, direction=None, first=None,
                 names=("A", "B"), context=None, intro=None, ask_phrase=None) -> Item:
    """What two means force, and what they leave open."""
    mode = mode or rng.choice(["two_means", "append_extreme"])
    an, bn = names
    if mode == "two_means":
        ctx = context or rng.choice(TEAM_CONTEXTS)
        n = n or rng.choice([8, 10, 12, 15])
        m1 = q(m1) if m1 is not None else q(rng.randint(200, 500)) / 100
        m2 = q(m2) if m2 is not None else m1 + q(rng.randint(10, 90)) / 100
        if m2 <= m1:
            raise ItemError("the second mean must be the larger one")
        g, mem, mems = ctx["group"], ctx["member"], ctx["members"]
        s1 = (f"Every {mem} of {g} {an} {ctx['less']} than any {mem} of {g} {bn}.")
        s2 = (f"The median time it took the {mems} of {g} {bn} to "
              f"{ctx['doing'].split()[0]} the {ctx['doing'].split()[-1]} is greater "
              f"than the median time it took the {mems} of {g} {an} to "
              f"{ctx['doing'].split()[0]} the {ctx['doing'].split()[-1]}.")
        s2 = (f"The median {ctx['time']} of the {mems} of {g} {bn} is greater than the "
              f"median {ctx['time']} of the {mems} of {g} {an}.")
        s3 = (f"There is at least one {mem} of {g} {bn} who {ctx['more']} than some "
              f"{mem} of {g} {an}.")
        key = "III only"
        distractors = [
            Mis(f"read the smaller mean as putting every {mem} of {g} {an} ahead of "
                f"every {mem} of {g} {bn}", "I and III only"),
            Mis("assumed the median must follow wherever the mean leads",
                "II and III only"),
            Mis("assumed one mean below another orders the individuals and the medians "
                "as well", "I, II, and III"),
        ]
        stem = ((intro or f"Two different {g}s consisting of {n} {mems} each "
                 f"{ctx['doing']}. Each {mem}'s {ctx['time']} was recorded. The mean of "
                 f"the {ctx['times']} for each {g} was calculated and is shown below.")
                + f"\n{g.capitalize()} {an}: {num_str(m1)} {ctx['unit']}"
                + f"\n{g.capitalize()} {bn}: {num_str(m2)} {ctx['unit']}\n"
                + (ask_phrase or "Which of the following MUST be true?")
                + f"\nI. {s1}\nII. {s2}\nIII. {s3}")
        opts, reasons, letter = assemble_text(key, distractors, rng)
        P = {"kind": "ovd_must_be_true", "mode": "two_means", "m1": float(m1),
             "m2": float(m2), "n": int(n)}
        rationale = (f"A larger mean forces at least one larger value, so III holds; it "
                     f"orders neither every individual nor the medians, so I and II do "
                     f"not.")
        return Item("ovd.reason.two_means", "what a mean must imply", "hard", seed,
                    stem, "mcq", E(0), letter, rationale, opts, reasons, list(opts),
                    params=P)

    size = size or rng.choice([25, 35, 45, 55, 75])
    lo = lo if lo is not None else rng.randint(50, 200)
    hi = hi if hi is not None else lo + rng.randint(50, 150)
    direction = direction or rng.choice(["below", "above"])
    extra = extra if extra is not None else (lo - rng.randint(10, 40) if
                                             direction == "below" else
                                             hi + rng.randint(10, 40))
    if direction == "below" and q(extra) >= lo:
        raise ItemError("the added integer must sit below every value in the data set")
    if direction == "above" and q(extra) <= hi:
        raise ItemError("the added integer must sit above every value in the data set")
    first = first or "mean"
    # the mean moves for certain; the median can land on the same value twice over
    mean_true = (direction == "above")
    truth = (mean_true, False) if first == "mean" else (False, mean_true)
    key = one_two_options(truth)
    why = {
        "I only": "took the extra value to move the mean and the median together"
                  if first == "median" else
                  "read the direction backwards: a value below every other one pulls "
                  "the mean down, so it is the larger data set that has the smaller "
                  "mean",
        "II only": "read the direction backwards: a value below every other one pulls "
                   "the mean down, so it is the larger data set that has the smaller "
                   "mean" if first == "median" else
                   "took the extra value to move the middle of the list for certain, "
                   "but with one value added the middle can land on the same number",
        "I and II": "assumed one extra value outside the range moves both measures",
        "Neither I nor II": "assumed one value among many can move neither measure",
    }
    labels = {"mean": "The mean", "median": "The median"}
    order = [first, "median" if first == "mean" else "mean"]
    stem = ((intro or f"Data set {an} consists of {size} integers between {lo} and "
             f"{hi}. Data set {bn} consists of all the integers in data set {an} as "
             f"well as the integer {num_str(q(extra))}.") + " "
            + (ask_phrase or f"Which of the following must be less for data set {an} "
               f"than for data set {bn}?")
            + f"\nI. {labels[order[0]]}.\nII. {labels[order[1]]}.")
    opts, reasons, letter = one_two(key, why, rng)
    P = {"kind": "ovd_must_be_true", "mode": "append_extreme", "size": int(size),
         "order": order,
         "lo": float(q(lo)), "hi": float(q(hi)), "extra": float(q(extra)),
         "first": first}
    rationale = (f"Adding a value {'above' if direction == 'above' else 'below'} every "
                 f"other one moves the mean {'up' if direction == 'above' else 'down'} "
                 f"for certain; the median can stay exactly where it was, so nothing "
                 f"about it must be true.")
    return Item("ovd.reason.append_extreme", "what an extra value must do", "hard",
                seed, stem, "mcq", E(0), letter, rationale, opts, reasons, list(opts),
                params=P)
