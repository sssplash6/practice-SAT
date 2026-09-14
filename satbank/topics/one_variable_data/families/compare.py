"""Comparing two distributions, and saying what an edit does to one.

These are the items with sentences for options. A sentence cannot be sorted
into ascending order, so the only thing keeping a student from guessing is
that all four sentences are defensible: each wrong one is what you get from a
specific wrong idea about centre or spread, and the reason says which.
"""

from __future__ import annotations

import random
from fractions import Fraction as F

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text
from ....plot import dotplot
from ..charts import paired_histogram
from ..common import (count_word, listing, mean, median, mode, num_str, q,
                      sentence_case, spread, values_line)

__all__ = ["compare_sets", "sd_compare", "measure_effect", "new_data_set",
           "odd_measure"]

ONE_TWO = ["I only", "II only", "I and II", "Neither I nor II"]


def one_two_options(truth: tuple[bool, bool]) -> str:
    return {(True, True): "I and II", (True, False): "I only",
            (False, True): "II only", (False, False): "Neither I nor II"}[truth]


def one_two(key_text: str, why: dict, rng: random.Random):
    missing = [o for o in ONE_TWO if o != key_text and o not in why]
    if missing:
        raise ItemError(f"no reason written for {missing}")
    return assemble_text(key_text, [Mis(why[o], o) for o in ONE_TWO if o != key_text],
                         rng)


def _text_item(name, skill, difficulty, seed, stem, options, reasons, letter,
               rationale, params, figure=None, table=None) -> Item:
    return Item(name, skill, difficulty, seed, stem, "mcq", E(0), letter, rationale,
                options, reasons, list(options), figure=figure, table=table,
                params=params)


# -------------------------------------------------------- TWO DATA SETS

PAIR_CONTEXTS = [
    ("students", "the number of students from two different high schools who completed "
     "summer internships in each of five years"),
    ("machines", "the number of parts two machines produced in each of five hours"),
    ("stores", "the number of items two stores sold on each of five days"),
    ("teams", "the number of points two teams scored in each of five games"),
]


def compare_sets(rng: random.Random, seed: int, *, a=None, b=None, ask=None,
                 presentation=None, names=("A", "B"), labels=None, row_names=None,
                 row_label=None, intro=None, ask_phrase=None, statements=None,
                 totals=False) -> Item:
    """Two data sets side by side: how do their centres compare?"""
    ask = ask or rng.choice(["means_statement", "one_two", "which_differ"])
    presentation = presentation or ("table" if ask == "one_two" else "lists")
    if a is None:
        n = rng.choice([5, 7])
        base = rng.randint(20, 70)
        a = [base + rng.randint(0, 30) for _ in range(n)]
        b = [base + rng.randint(-20, 10) for _ in range(n)]
    A = [q(v) for v in a]
    B = [q(v) for v in b]
    an, bn = names
    ma, mb, da, db = mean(A), mean(B), median(A), median(B)
    P = {"kind": "ovd_compare_sets", "a": [float(v) for v in A],
         "b": [float(v) for v in B], "ask": ask, "order": ["mean", "median"]}

    table = None
    if presentation == "table":
        labels = labels or [str(i + 1) for i in range(len(A))]
        rn = row_names or (f"data set {an}", f"data set {bn}")
        table = [[row_label or ""] + list(labels),
                 [sentence_case(rn[0])] + [num_str(v) for v in A],
                 [sentence_case(rn[1])] + [num_str(v) for v in B]]
        if totals:
            table.append(["Total"] + [num_str(x + y) for x, y in zip(A, B)])
        head = intro or (f"The table shows the values in {rn[0]} and {rn[1]}.")
    else:
        rn = (f"data set {an}", f"data set {bn}")
        head = (f"Data set {an}: {values_line(A)}\n"
                f"Data set {bn}: {values_line(B)}")
        if intro:
            head = f"{intro}\n{head}"

    if ask == "means_statement":
        if ma == mb:
            raise ItemError("the two means are equal, so no statement is sharper")
        key = (f"The mean of data set {an} is {'greater' if ma > mb else 'less'} than "
               f"the mean of data set {bn}.")
        distractors = [
            Mis(f"found the median of data set {bn} and reported it as the mean of "
                f"both", f"The mean of each data set is {num_str(db)}."),
            Mis(f"found the median of data set {an} and reported it as the mean of "
                f"both", f"The mean of each data set is {num_str(da)}."),
            Mis("read the direction of the comparison backwards",
                f"The mean of data set {an} is {'less' if ma > mb else 'greater'} than "
                f"the mean of data set {bn}."),
            Mis("assumed two data sets of the same size must share a mean",
                f"The mean of data set {an} is equal to the mean of data set {bn}."),
        ]
        P["claim"] = (f"The mean of data set {an} is {{rel}} than the mean of data "
                      f"set {bn}.")
        stem = f"{head}\n" + (ask_phrase or f"Which of the following statements "
                              f"correctly compares the means of data set {an} and data "
                              f"set {bn}?")
        options, reasons, letter = assemble_text(key, distractors, rng)
        rationale = (f"Data set {an} has mean {num_str(ma)} and data set {bn} has mean "
                     f"{num_str(mb)}.")
    elif ask == "which_differ":
        same_mean, same_med = ma == mb, da == db
        if same_mean and same_med:
            raise ItemError("nothing differs, so the question has no bite")
        key = {(False, True): "Only the means are different.",
               (True, False): "Only the medians are different.",
               (False, False): "Both the means and the medians are different."}[
                   (same_mean, same_med)]
        why = {
            "Only the means are different.":
                "took the one value that stands apart to move the average only",
            "Only the medians are different.":
                "took the one value that stands apart to move the middle value rather "
                "than the average",
            "Both the means and the medians are different.":
                "assumed any change to a data set moves both measures",
            "Neither the means nor the medians are different.":
                "saw the same repeated value in both data sets and stopped there",
        }
        distractors = [Mis(w, t) for t, w in why.items() if t != key]
        stem = f"{head}\n" + (ask_phrase or f"Which of the following statements about "
                              f"the means and medians of data set {an} and data set "
                              f"{bn} is true?")
        options, reasons, letter = assemble_text(key, distractors, rng)
        rationale = (f"Data set {an}: mean {num_str(ma)}, median {num_str(da)}. Data "
                     f"set {bn}: mean {num_str(mb)}, median {num_str(db)}.")
    else:                                                        # one_two
        truth = (ma > mb, da > db)
        key = one_two_options(truth)
        s1, s2 = statements or (
            f"The mean of {rn[0]} is greater than the mean of {rn[1]}.",
            f"The median of {rn[0]} is greater than the median of {rn[1]}.")
        why = {
            "I only": "compared the means and assumed the medians cannot agree",
            "II only": "compared the medians and did not test the means",
            "I and II": "assumed the medians must follow wherever the means lead",
            "Neither I nor II": "assumed neither centre can be compared from the table",
        }
        stem = (f"{head} " if presentation == "table" else f"{head}\n") + (
            ask_phrase or "Which of the following statements are true?") + \
            f"\nI. {s1}\nII. {s2}"
        options, reasons, letter = one_two(key, why, rng)
        rationale = (f"{sentence_case(rn[0])}: mean {num_str(ma)}, median "
                     f"{num_str(da)}. {sentence_case(rn[1])}: mean {num_str(mb)}, "
                     f"median {num_str(db)}.")
    return _text_item(f"ovd.compare.{ask}", "comparing two data sets", "medium", seed,
                      stem, options, reasons, letter, rationale, P, table=table)


# ------------------------------------------------------------------ SPREAD

SD_SUMMARY = [
    {"title": "Men's Height", "quantity": "heights", "member": "men",
     "one": "participant", "super": "tallest", "unit": "centimeters"},
    {"title": "Seedling Height", "quantity": "heights", "member": "seedlings",
     "one": "seedling", "super": "tallest", "unit": "centimeters"},
    {"title": "Commute Time", "quantity": "times", "member": "commuters",
     "one": "commuter", "super": "longest", "unit": "minutes"},
    {"title": "Package Mass", "quantity": "masses", "member": "packages",
     "one": "package", "super": "heaviest", "unit": "kilograms"},
]

SD_HIST = [
    {"thing": "number of units sold", "unit": "in thousands", "a": "company A",
     "b": "company B", "lo": 15, "step": 5,
     "intro": "The histograms summarize the distributions of number of units sold, in "
              "thousands, for company A and company B."},
    {"thing": "number of minutes", "unit": "", "a": "class A", "b": "class B",
     "lo": 10, "step": 5,
     "intro": "The histograms summarize the distributions of the number of minutes "
              "spent reading for class A and class B."},
    {"thing": "mass", "unit": "grams", "a": "sample A", "b": "sample B",
     "lo": 20, "step": 4,
     "intro": "The histograms summarize the distributions of mass, in grams, for "
              "sample A and sample B."},
]


def sd_compare(rng: random.Random, seed: int, *, presentation=None, n=None, mu=None,
               sd_a=None, sd_b=None, context=None, counts_a=None, counts_b=None,
               groups=("A", "B"), intro=None, ask_phrase=None) -> Item:
    """Standard deviation the way the SAT asks about it: compared, never computed."""
    presentation = presentation or rng.choice(["summary", "histograms"])
    ga, gb = groups
    if presentation == "summary":
        ctx = context or rng.choice(SD_SUMMARY)
        n = n or rng.choice([500, 1000, 1500, 2000, 2500])
        mu = mu if mu is not None else rng.randint(60, 200)
        sd_a = sd_a if sd_a is not None else round(rng.uniform(4, 12), 1)
        sd_b = sd_b if sd_b is not None else round(float(sd_a) + rng.uniform(2, 9), 1)
        if q(sd_a) == q(sd_b):
            raise ItemError("the two standard deviations are equal")
        wide, narrow = (gb, ga) if q(sd_b) > q(sd_a) else (ga, gb)
        table = [["Group", "Sample size", f"Mean ({ctx['unit']})",
                  f"Standard deviation ({ctx['unit']})"],
                 [ga, num_str(q(n)), num_str(q(mu)), num_str(q(sd_a))],
                 [gb, num_str(q(n)), num_str(q(mu)), num_str(q(sd_b))]]
        key = (f"The {ctx['quantity']} of the {ctx['member']} in Group {wide} had a "
               f"larger spread than the {ctx['quantity']} of the {ctx['member']} in "
               f"Group {narrow}.")
        distractors = [
            Mis("read equal means as meaning the two data sets are the same",
                f"The Group {ga} data set was identical to the Group {gb} data set."),
            Mis("read the larger standard deviation as naming the single most extreme "
                f"value", f"Group {wide} contained the {ctx['super']} {ctx['one']}."),
            Mis("read the equal means as saying something about the medians",
                f"The median {ctx['quantity'][:-1]} of Group {gb} is larger than the "
                f"median {ctx['quantity'][:-1]} of Group {ga}."),
        ]
        stem = (intro or "The results of two independent surveys are shown in the table "
                "below.") + " " + (ask_phrase or "Which statement is true based on the "
                                   "table?")
        figure = None
        P = {"kind": "ovd_sd_compare", "presentation": "summary", "n": int(n),
             "mu": float(q(mu)), "sd_a": float(q(sd_a)), "sd_b": float(q(sd_b)),
             "groups": [ga, gb],
             "claim": (f"The {ctx['quantity']} of the {ctx['member']} in Group {{wide}} "
                       f"had a larger spread than the {ctx['quantity']} of the "
                       f"{ctx['member']} in Group {{narrow}}.")}
        rationale = (f"Both groups have the same mean, so the only difference the table "
                     f"reports is the spread: {num_str(q(sd_b))} against "
                     f"{num_str(q(sd_a))}.")
    else:
        ctx = context or rng.choice(SD_HIST)
        k = 7
        if counts_a is None:
            mid = k // 2
            peak = rng.randint(30, 50)
            counts_a = [0] * k
            for i in (mid - 1, mid, mid + 1):
                counts_a[i] = peak - abs(i - mid) * rng.randint(0, 8)
            edge = rng.randint(20, 40)
            counts_b = [edge, edge - 8, edge - 18, max(1, edge - 28), edge - 18,
                        edge - 8, edge]
        if len(counts_a) != k or len(counts_b) != k:
            raise ItemError("both histograms need the same bins")
        edges = [ctx["lo"] + i * ctx["step"] for i in range(k + 1)]
        mids = [q(edges[i] + edges[i + 1]) / 2 for i in range(k)]
        sa, sb = _bin_sd(mids, counts_a), _bin_sd(mids, counts_b)
        if sb < sa * 2:
            raise ItemError("the two spreads are too close to call from a picture")
        an, bn = ctx["a"], ctx["b"]
        thing = ctx["thing"]
        key = (f"The standard deviation of {thing} for {an} is less than the standard "
               f"deviation of {thing} for {bn}.")
        distractors = [
            Mis(f"read the taller bars as the wider spread: the values for {an} are "
                f"packed together, not spread out",
                f"The standard deviation of {thing} for {an} is greater than the "
                f"standard deviation of {thing} for {bn}."),
            Mis("read the two axes as identical and concluded the spreads must match; "
                "standard deviation measures distance from the mean, not the width of "
                "the axis",
                f"The standard deviation of {thing} for {an} is equal to the standard "
                f"deviation of {thing} for {bn}."),
            Mis("assumed a histogram cannot settle which distribution is more spread "
                "out", "There is not enough information to compare the standard "
                "deviations."),
        ]
        figure = paired_histogram(edges, [counts_a, counts_b],
                                  [an.title(), bn.title()],
                                  xlabel=(f"{thing.capitalize()} ({ctx['unit']})"
                                          if ctx["unit"] else thing.capitalize()))
        stem = (intro or ctx["intro"]) + " " + (
            ask_phrase or f"Which statement best compares the standard deviations of "
            f"{thing} for these two groups?")
        P = {"kind": "ovd_sd_compare", "presentation": "histograms",
             "edges": [float(e) for e in edges], "counts_a": list(counts_a),
             "counts_b": list(counts_b), "groups": [an, bn],
             "claim": (f"The standard deviation of {thing} for {an} is {{rel}} the "
                       f"standard deviation of {thing} for {bn}.")}
        rationale = (f"The values for {an} sit in the middle bins, while {bn} piles its "
                     f"values at both ends, so {bn} is further from its mean on "
                     f"average.")
        table = None
    options, reasons, letter = assemble_text(key, distractors, rng)
    return _text_item(f"ovd.spread.{presentation}", "comparing spread", "medium", seed,
                      stem, options, reasons, letter, rationale, P, figure=figure,
                      table=table)


def _bin_sd(mids, counts) -> F:
    total = sum(counts)
    if total <= 0:
        raise ItemError("an empty histogram")
    mu = sum(m * c for m, c in zip(mids, counts)) / total
    return sum((m - mu) ** 2 * c for m, c in zip(mids, counts)) / total


# ------------------------------------------------------------ AN EDIT

MEASURE_NAMES = {"mean": "Mean", "median": "Median", "range": "Range",
                 "sd": "Standard deviation", "sum": "Sum of the numbers"}

# True where the edit moves the measure.
EDITS = {
    "correct_low": {"mean": True, "median": False, "range": True, "sd": True,
                    "sum": True},
    "spread_about_median": {"mean": False, "median": False, "range": True, "sd": True,
                            "sum": False},
    "add_constant": {"mean": True, "median": True, "range": False, "sd": False,
                     "sum": True},
    "raise_max": {"mean": True, "median": False, "range": True, "sd": True,
                  "sum": True},
}

CHANGED_WHY = {           # why a student wrongly calls this one unchanged
    "mean": "assumed the average is fixed by the middle of the list rather than by "
            "every value in it",
    "median": "assumed the middle value is fixed by its position, whatever the values "
              "around it do",
    "range": "assumed the range depends only on the greatest value",
    "sd": "assumed the spread cannot change while the values stay in the same order",
    "sum": "assumed the total is fixed by how many values there are",
}

UNCHANGED_WHY = {         # why a student wrongly calls this one changed
    "mean": "assumed the mean must move when the values move, without noticing that "
            "the increases and the decreases cancel",
    "median": "assumed the middle value moves whenever any value moves",
    "range": "assumed the spread of the values changed with them",
    "sd": "assumed the spread is unchanged because the centre is",
    "sum": "assumed the total changes whenever any value does",
}

CANON = ["mean", "median", "range", "sd", "sum"]


def _named(pool):
    return [MEASURE_NAMES[m].lower() for m in CANON if m in pool]


EFFECT_CONTEXTS = [
    ("horses in a stable", "weights", "pounds", "horse", "weight"),
    ("trees in an orchard", "heights", "inches", "tree", "height"),
    ("packages in a van", "masses", "kilograms", "package", "mass"),
    ("runners in a race", "times", "seconds", "runner", "time"),
    ("books on a shelf", "thicknesses", "millimeters", "book", "thickness"),
]


VALID_EFFECT = [(e, a) for e in EDITS for a in ("unchanged", "changed")
                if sum(1 for m in EDITS[e] if EDITS[e][m] == (a == "changed")) >= 1
                and sum(1 for m in EDITS[e] if EDITS[e][m] != (a == "changed")) >= 3]


ODD_CONTEXTS = [
    ("The high temperature, in degrees Fahrenheit (\u00b0F), in a certain city was "
     "recorded for each of {n} days. The data are shown below.", "high temperatures",
     "Day", "High temperature (\u00b0F)", "\u00b0F",
     "Over this {n}-day period, which of the following is NOT equal to {v}\u00b0F?"),
    ("The number of customers in a shop was counted in each of {n} hours. The data are "
     "shown below.", "numbers of customers", "Hour", "Number of customers", "",
     "Over these {n} hours, which of the following is NOT equal to {v}?"),
    ("The number of goals a team scored was recorded for each of {n} matches. The data "
     "are shown below.", "numbers of goals", "Match", "Number of goals", "",
     "Over these {n} matches, which of the following is NOT equal to {v}?"),
    ("The mass, in grams, of each of {n} samples was recorded. The data are shown "
     "below.", "masses", "Sample", "Mass (grams)", " grams",
     "For these {n} samples, which of the following is NOT equal to {v} grams?"),
]


def odd_measure(rng: random.Random, seed: int, *, values=None, target=None,
                context=None, measures=None, intro=None, ask_phrase=None) -> Item:
    """Four measures of one small data set; three agree and one does not."""
    opening, plural, col, head, unit, question = context or rng.choice(ODD_CONTEXTS)
    if values is None:
        base = rng.randint(10, 90)
        n = rng.choice([5, 7])
        values = [base] * (n - 2) + [base - rng.randint(1, 3), base + rng.randint(1, 3)]
        rng.shuffle(values)
    vals = [q(v) for v in values]
    n = len(vals)
    if n % 2 == 0:
        raise ItemError("an even count leaves the median between two values")
    named = {"median": median(vals), "mean": mean(vals), "mode": _mode_or_none(vals),
             "range": spread(vals)}
    pool = list(measures or ["median", "mean", "mode", "range"])
    if any(named[m] is None for m in pool):
        raise ItemError("this data set has no single most common value")
    target = q(target) if target is not None else None
    if target is None:
        counts = {}
        for m in pool:
            counts[named[m]] = counts.get(named[m], 0) + 1
        agreed = [v for v, c in counts.items() if c == len(pool) - 1]
        if len(agreed) != 1:
            raise ItemError("three of the four measures must agree")
        target = agreed[0]
    odd = [m for m in pool if named[m] != target]
    if len(odd) != 1:
        raise ItemError(f"{len(odd)} measures differ from the stated value, not one")
    labels = {m: f"{m.capitalize()} of the {plural}" for m in pool}
    key = labels[odd[0]]
    distractors = [Mis(f"the {m} of these {n} values is {num_str(target)}{unit}, so it "
                       f"does match -- the question asks which does not",
                       labels[m]) for m in pool if m != odd[0]]
    table = [[col] + [str(i + 1) for i in range(n)],
             [head] + [num_str(v) for v in vals]]
    stem = ((intro or opening.format(n=n)) + "\n"
            + (ask_phrase or question.format(n=n, v=num_str(target))))
    options, reasons, letter = assemble_text(key, distractors, rng)
    P = {"kind": "ovd_odd_measure", "values": [float(v) for v in vals],
         "target": float(target), "measures": pool, "labels": labels}
    rationale = (f"The {listing([m for m in pool if m != odd[0]])} are all "
                 f"{num_str(target)}{unit}; the {odd[0]} is {num_str(named[odd[0]])}"
                 f"{unit}.")
    return _text_item("ovd.odd_measure", "measures of one data set", "easy", seed, stem,
                      options, reasons, letter, rationale, P, table=table)


def _mode_or_none(vals):
    try:
        return mode(vals)
    except ItemError:
        return None


def measure_effect(rng: random.Random, seed: int, *, edit=None, ask=None, n=None,
                   k=None, context=None, measures=None, key_measure=None, intro=None,
                   body=None, ask_phrase=None) -> Item:
    """An edit to one data set, and which summary measure survives it."""
    if edit is None or ask is None:
        pick = rng.choice([p for p in VALID_EFFECT
                           if (edit is None or p[0] == edit)
                           and (ask is None or p[1] == ask)])
        edit, ask = edit or pick[0], ask or pick[1]
    moves = EDITS[edit]
    n = n or rng.choice([11, 13, 15, 17, 19, 21, 25, 27])
    k = k or rng.choice([2, 3, 5, 7, 10, 12])
    where, quantity, unit, one, single = context or rng.choice(EFFECT_CONTEXTS)

    want = (ask == "changed")
    fits = [m for m in MEASURE_NAMES if moves[m] == want]
    others = [m for m in MEASURE_NAMES if moves[m] != want]
    if not fits or len(others) < 3:
        raise ItemError("this edit does not single out one measure")
    key_m = key_measure or (fits[0] if len(fits) == 1 else rng.choice(fits))
    if key_m not in fits:
        raise ItemError(f"{key_m} is not the measure this edit singles out")
    pool = measures or ([key_m] + [m for m in ["mean", "median", "range", "sd", "sum"]
                                   if m in others][:3])
    if any(moves[m] == want for m in pool if m != key_m):
        raise ItemError("more than one option answers the question")
    if key_m not in pool or len(pool) != 4:
        raise ItemError("the options must hold the answer and three others")

    if edit == "correct_low":
        body_text = (f"The {one} with the lowest reported {single} was found to actually "
                f"have a {single} {k} {unit} less than its reported {single}.")
        opening = (f"The {quantity}, in {unit}, for {n} {where} were reported, and the "
                   f"{listing(_named(pool))} for the data were found.")
    elif edit == "raise_max":
        body_text = (f"The {one} with the greatest reported {single} was found to actually "
                f"have a {single} {k} {unit} more than its reported {single}.")
        opening = (f"The {quantity}, in {unit}, for {n} {where} were reported, and the "
                   f"{listing(_named(pool))} for the data were found.")
    elif edit == "add_constant":
        body_text = (f"A new data set is created by adding {k} to each number in the "
                f"original data set.")
        opening = f"A data set of {n} different numbers is recorded."
    else:
        body_text = (f"A new data set is created by adding {k} to each number in the "
                f"original data set that is greater than the median and subtracting "
                f"{k} from each number in the original data set that is less than the "
                f"median.")
        centre = rng.randint(20, 60)
        opening = (f"A data set of {n} different numbers has a mean of {centre} and a "
                   f"median of {centre}.")

    if ask == "unchanged":
        question = ask_phrase or ("What value remains unchanged if the values are "
                                  "reported using the corrected data?"
                                  if edit in ("correct_low", "raise_max") else
                                  "Which of the following measures has the same value "
                                  "in both the original and new data sets?")
        why = CHANGED_WHY
    else:
        question = ask_phrase or ("Which of the following measures does NOT have the "
                                  "same value in both the original and new data sets?")
        why = UNCHANGED_WHY
    stem = f"{intro or opening} {body or body_text} {question}"
    key = MEASURE_NAMES[key_m]
    distractors = [Mis(why[m], MEASURE_NAMES[m]) for m in pool if m != key_m]
    options, reasons, letter = assemble_text(key, distractors, rng)
    P = {"kind": "ovd_measure_effect", "edit": edit, "ask": ask, "n": int(n),
         "k": float(q(k)), "measures": list(pool),
         "labels": {m: MEASURE_NAMES[m] for m in pool}}
    rationale = _effect_rationale(edit, key_m, ask)
    return _text_item(f"ovd.change.{edit}", "effect of an edit", "hard", seed, stem,
                      options, reasons, letter, rationale, P)


def _effect_rationale(edit, key_m, ask) -> str:
    if edit == "correct_low":
        return ("Only the least value moves, so the total, the spread and the average "
                "all change; the value in the middle of the ordered list does not.")
    if edit == "raise_max":
        return ("Only the greatest value moves, so the total, the spread and the "
                "average all change; the value in the middle does not.")
    if edit == "add_constant":
        return ("Every value moves by the same amount, so every centre moves with them "
                "and the distances between the values -- the spread -- do not change.")
    return ("The same amount is added above the median as is taken away below it, so "
            "the total, the mean and the median are untouched; the values are further "
            "from the centre than they were, so the spread is not.")


# ------------------------------------------------------- A NEW DATA SET

SHIFT_CONTEXTS = [
    ("Data Set A", "data set A", "data set B"),
]

DOT_CONTEXTS = [
    ("bursts", "eruptions of a steam vent", "eruption", "eruptions"),
    ("goals", "matches", "match", "matches"),
    ("deliveries", "days", "day", "days"),
    ("calls", "shifts", "shift", "shifts"),
    ("seedlings", "trays", "tray", "trays"),
]


def new_data_set(rng: random.Random, seed: int, *, values=None, mode=None, c=None,
                 extra=None, context=None, names=("A", "B"), intro=None,
                 ask_phrase=None, first=None) -> Item:
    """Data set B is made from data set A. What happened to the centre and the spread?"""
    mode = mode or rng.choice(["shift", "append"])
    thing, unit, one, short = context or rng.choice(DOT_CONTEXTS)
    if values is None:
        base = rng.randint(1, 40)
        width = rng.choice([4, 5, 6])
        values = []
        for i in range(width + 1):
            values += [base + i] * rng.randint(1, 5)
        rng.shuffle(values)
    vals = [q(v) for v in values]
    n = len(vals)
    an, bn = names
    figure = dotplot([float(v) for v in vals], xlabel=f"Number of {thing}")
    P = {"kind": "ovd_new_data_set", "values": [float(v) for v in vals], "mode": mode}

    if mode == "shift":
        c = c if c is not None else rng.randint(2, 60)
        if c == 0:
            raise ItemError("adding nothing changes nothing")
        P["c"] = float(q(c))
        up = q(c) > 0
        rel1 = "greater than" if up else "less than"
        key = (f"The median of data set {bn} is {rel1} the median of data set {an}, and "
               f"the range of data set {bn} is equal to the range of data set {an}.")

        def sent(r1, r2):
            return (f"The median of data set {bn} is {r1} the median of data set {an}, "
                    f"and the range of data set {bn} is {r2} the range of data set "
                    f"{an}.")

        distractors = [
            Mis("added the constant to the range as well, but moving every value "
                "together leaves the distances between them alone",
                sent(rel1, "greater than" if up else "less than")),
            Mis("assumed adding a constant stretches the data instead of sliding it",
                sent("equal to", "greater than" if up else "less than")),
            Mis("assumed adding the same number to every value changes nothing at all",
                sent("equal to", "equal to")),
        ]
        stem = (intro or f"Data set {an} has {n} values and is represented by the dot "
                f"plot shown. Data set {bn} is created by "
                f"{'adding' if up else 'subtracting'} {num_str(abs(q(c)))} to each of "
                f"the values in data set {an}.".replace("subtracting {} to".format(
                    num_str(abs(q(c)))), "subtracting {} from".format(
                    num_str(abs(q(c)))))) + " " + (
            ask_phrase or f"Which of the following correctly compares the medians and "
            f"the ranges of data sets {an} and {bn}?")
        P["claim"] = sent("{r1}", "{r2}")
        options, reasons, letter = assemble_text(key, distractors, rng)
        rationale = (f"Every value moves by {num_str(abs(q(c)))}, so the median moves "
                     f"with them and the distance from the least value to the greatest "
                     f"does not change.")
        return _text_item("ovd.change.shift", "shifting every value", "medium", seed,
                          stem, options, reasons, letter, rationale, P, figure=figure)

    extra = extra if extra is not None else max(vals) + rng.randint(2, 10)
    P["extra"] = float(q(extra))
    new = vals + [q(extra)]
    first = first or "median"
    grew = {"median": median(new) > median(vals), "mean": mean(new) > mean(vals)}
    order = [first, "mean" if first == "median" else "median"]
    truth = (grew[order[0]], grew[order[1]])
    key = one_two_options(truth)
    why = {
        "I only": f"took the extra value to move the middle of the list without "
                  f"changing the average",
        "II only": "took the extra value to move the average without changing the "
                   "middle of the list",
        "I and II": "assumed one more value above the rest lifts every measure",
        "Neither I nor II": "assumed one value among many cannot move either measure",
    }
    stem = (intro or f"The dot plot represents a data set of the number of {thing} for "
            f"{n} {unit}. If an additional {one} with {num_str(q(extra))} {thing} is "
            f"added to this data set to create a new data set of {n + 1} {short}, ") + (
        ask_phrase or "which of the following measures will be greater for the new data "
        "set than for the original data set?") + \
        f"\nI. The {order[0]} number of {thing}.\nII. The {order[1]} number of {thing}."
    options, reasons, letter = one_two(key, why, rng)
    rationale = (f"The median goes from {num_str(median(vals))} to "
                 f"{num_str(median(new))} and the mean from {num_str(mean(vals))} to "
                 f"{num_str(mean(new))}.")
    P["order"] = order
    return _text_item("ovd.change.append", "adding one value", "hard", seed, stem,
                      options, reasons, letter, rationale, P, figure=figure)
