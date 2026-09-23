"""Frequency tables: the centre of a data set you are never shown.

A value-and-frequency table is the SAT's favourite way of hiding a data set in
plain sight, and it produces one misconception above all others: averaging the
values in the left-hand column and forgetting that the right-hand column says
how many times each one happened. Every template here offers that wrong answer.
"""

from __future__ import annotations

import random
from fractions import Fraction as F

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text, gridin_mistakes
from ..common import (assemble_num, clean, count_word, listing, mean, median,
                      midrange, mode, num_str, q, spread, values_line)

__all__ = ["freq_stat", "freq_order", "freq_two_groups", "freq_choose"]


def expand(values, freqs) -> list[F]:
    """The data set the table stands for."""
    out: list[F] = []
    for v, f in zip(values, freqs):
        if f < 0:
            raise ItemError("a frequency cannot be negative")
        out += [q(v)] * int(f)
    if not out:
        raise ItemError("an empty frequency table")
    return out


FREQ_CONTEXTS = [
    ("Ages of {n} Students Enrolled in a College Class", "Age", "age", "ages",
     "the {n} students enrolled in a college class"),
    ("Points Scored by {n} Players", "Points", "number of points", "numbers of points",
     "the {n} players on a team"),
    ("Number of Pets Owned by {n} Families", "Number of pets", "number of pets",
     "numbers of pets", "the {n} families in a survey"),
    ("Hours Volunteered by {n} Students", "Hours", "number of hours", "numbers of hours",
     "the {n} students in a club"),
    ("Number of Books Read by {n} Readers", "Number of books", "number of books",
     "numbers of books", "the {n} readers in a reading group"),
    ("Daily High Temperatures over {n} Days", "Temperature (°F)", "temperature",
     "temperatures", "the {n} days recorded"),
]


def _freq_table(values, freqs, head_v="Value", head_f="Frequency", symbol=None):
    rows = [[head_v, head_f]]
    for v, f in zip(values, freqs):
        rows.append([num_str(q(v)), symbol(f) if symbol else num_str(q(f))])
    return rows


def _draw_freq(rng: random.Random, k=None, skew=True):
    k = k or rng.randint(4, 7)
    start = rng.randint(1, 30)
    step = rng.choice([1, 1, 2, 5])
    values = [start + i * step for i in range(k)]
    freqs = [rng.randint(1, 8) for _ in range(k)]
    if skew:
        freqs = sorted(freqs, reverse=True)
        values[-1] += rng.randint(3, 12) * step
    return values, freqs


# -------------------------------------------------------------- ONE TABLE

def freq_stat(rng: random.Random, seed: int, *, values=None, freqs=None, ask=None,
              symbolic=False, context=None, fmt=None, intro=None, ask_phrase=None,
              head_v=None, only=None, prefer=()) -> Item:
    ask = ask or rng.choice(["mean", "median", "mean", "range", "mean_minus_median"])
    if values is None:
        values, freqs = _draw_freq(rng, skew=(ask != "mean_minus_median"))
    vals = [q(v) for v in values]
    fs = [int(f) for f in freqs]
    data = expand(vals, fs)
    n = sum(fs)
    title, _head, noun, nouns, who = context or rng.choice(FREQ_CONTEXTS)
    mu, med = mean(data), median(data)

    if ask == "mean_minus_median":
        if mu < med:
            raise ItemError("the mean does not exceed the median here")
        key = E(clean(mu - med))
        below = [v for v in vals if v < med]
        cands = {
            "row_above": Mis("read the row above the middle one as the mean",
                             E(mu - below[-1]) if below else None),
            "max_gap": Mis("compared the greatest value with the median instead of the "
                           "mean", E(max(vals) - med)),
            "mean_itself": Mis("reported the mean itself, not the amount by which it "
                               "exceeds the median", E(mu)),
            "unweighted": Mis("averaged the values themselves, forgetting the "
                              "frequencies, then subtracted the median",
                              E(mean(vals) - med) if mean(vals) > med else None),
            "median_itself": Mis("reported the median instead of the difference", E(med)),
        }
        question = ask_phrase or ("How much greater is the mean of the set of data than "
                                  "the median?")
        rationale = (f"The {n} values total {num_str(sum(data, F(0)))}, so the mean is "
                     f"{num_str(mu)}; the middle value is {num_str(med)}.")
    else:
        key = E(clean({"mean": mu, "median": med, "range": spread(data),
                       "mode": _mode_or_fail(data)}[ask]))
        cands = {
            "unweighted_mean": Mis("averaged the values themselves, forgetting the "
                                   "frequencies", E(mean(vals))),
            "middle_row": Mis("read the value in the middle row of the table instead of "
                              "the middle of the data", E(median(vals))),
            "mode": Mis("read the value with the greatest frequency instead",
                        _safe_mode(data)),
            "mean": Mis("found the mean instead", E(mu)),
            "median": Mis("found the median instead", E(med)),
            "freq_median": Mis("found the median of the frequencies instead of the "
                               "values", E(median([q(f) for f in fs]))),
            "freq_range": Mis("found the range of the frequencies instead of the "
                              "values", E(spread([q(f) for f in fs]))),
            "total": Mis("reported the total of the values instead",
                         E(sum(data, F(0)))),
            "value_range": Mis("found the range of the values instead",
                               E(spread(vals))),
        }
        cands.pop(ask, None)
        question = ask_phrase or (f"What is the {ask} of the {nouns} shown in the table?")
        rationale = _freq_rationale(ask, data, key, n)

    if key.coef < 0:
        raise ItemError("a negative answer is not what this question asks for")
    order = list(only) if only else list(prefer) + [k for k in cands if k not in prefer]
    mistakes = [cands[k] for k in order if k in cands and cands[k].value is not None]
    intro = intro or (f"The table shows the distribution of the {nouns} for "
                      f"{who.format(n=n)}.")
    stem = f"{intro} {question}"
    sym = (lambda f: ("a" if f == 1 else f"{f}a")) if symbolic else None
    table = _freq_table(vals, fs, head_v or _head, "Frequency", sym)
    P = {"kind": "ovd_freq_stat", "values": [float(v) for v in vals], "freqs": fs,
         "ask": ask, "symbolic": bool(symbolic)}
    if symbolic:
        stem = stem.replace("The table shows",
                            "The frequency distribution shown summarizes a set of data, "
                            "where a is a positive integer. The table shows", 1)
        stem = (f"The frequency distribution above summarizes a set of data, where a is "
                f"a positive integer. {question}")
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("a grid-in answer must be enterable as digits")
        return Item(f"ovd.freq.{ask}", "frequency table", "medium", seed, stem, "spr",
                    key, key.gridin(), rationale, table=table, params=P,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble_num(key, mistakes, rng)
    return Item(f"ovd.freq.{ask}", "frequency table", "medium", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex, table=table, params=P)


def _mode_or_fail(data):
    try:
        return mode(data)
    except ItemError:
        raise ItemError("this table has no single most common value")


def _safe_mode(data):
    try:
        return E(mode(data))
    except ItemError:
        return None


def _freq_rationale(ask, data, key, n) -> str:
    if ask == "mean":
        return (f"Weighting each value by its frequency gives a total of "
                f"{num_str(sum(data, F(0)))} over {n} values, so the mean is "
                f"{num_str(q(key))}.")
    if ask == "median":
        return (f"Counting down the frequencies, the middle of the {n} values is "
                f"{num_str(q(key))}.")
    if ask == "mode":
        return f"{num_str(q(key))} has the greatest frequency."
    return (f"The values run from {num_str(min(data))} to {num_str(max(data))}, a range "
            f"of {num_str(q(key))}.")


# ------------------------------------------------------------------ ORDER

def freq_order(rng: random.Random, seed: int, *, values=None, freqs=None, context=None,
               intro=None, ask_phrase=None, head_v=None) -> Item:
    """Which of mean, median and mode is biggest -- the shape of the distribution."""
    if values is None:
        values, freqs = _draw_freq(rng, skew=True)
    vals = [q(v) for v in values]
    fs = [int(f) for f in freqs]
    data = expand(vals, fs)
    n = sum(fs)
    mu, med, mo = mean(data), median(data), _mode_or_fail(data)
    if len({mu, med, mo}) != 3:
        raise ItemError("two of the three measures are equal, so there is no order")
    title, _head, noun, nouns, who = context or rng.choice(FREQ_CONTEXTS)

    names = {"mean": mu, "median": med, "mode": mo}
    true_order = sorted(names, key=lambda k: names[k])
    key = " < ".join(true_order)
    def swapped(a, b):
        order = list(true_order)
        i, j = order.index(a), order.index(b)
        order[i], order[j] = order[j], order[i]
        return " < ".join(order)

    rot = true_order[-1:] + true_order[:-1]
    distractors = [
        Mis("swapped the mean and the median: it is the mean that the values far from "
            "the centre pull, not the middle value", swapped("mean", "median")),
        Mis("swapped the mode and the median: the most common value need not sit in "
            "the middle of the list", swapped("mode", "median")),
        Mis("moved every measure one place along the order, so the mean sits at the "
            "wrong end", " < ".join(rot)),
        Mis("swapped the mode and the mean", swapped("mode", "mean")),
        Mis("reversed the order, reading the table from the bottom up",
            " < ".join(reversed(true_order))),
    ]
    intro = intro or (f"The table shows the distribution of the {nouns} for "
                      f"{who.format(n=n)}.")
    stem = (f"{intro} " + (ask_phrase or "Which of the following gives the correct "
            "order of the mean, median, and mode of the " + nouns + "?"))
    options, reasons, letter = assemble_text(key, distractors, rng)
    P = {"kind": "ovd_freq_order", "values": [float(v) for v in vals], "freqs": fs}
    rationale = (f"The mean is {num_str(mu)}, the median is {num_str(med)} and the mode "
                 f"is {num_str(mo)}, so {key}.")
    return Item("ovd.freq.order", "comparing centre measures", "medium", seed, stem,
                "mcq", E(0), letter, rationale, options, reasons, list(options),
                table=_freq_table(vals, fs, head_v or _head), params=P)


# ------------------------------------------------------------- TWO COLUMNS

TWO_GROUP_CONTEXTS = [
    ("Score", "scores", "players", 1, 6, (1, 1, 2)),
    ("Value", "values", "values", 10, 60, (2, 4, 5)),
    ("Number of pets", "numbers of pets", "households", 0, 2, (1,)),
    ("Points", "points", "students", 55, 85, (5, 10)),
    ("Number of goals", "numbers of goals", "matches", 0, 3, (1,)),
    ("Age", "ages", "members", 14, 40, (1, 2)),
]


def freq_two_groups(rng: random.Random, seed: int, *, values=None, fa=None, fb=None,
                    ask=None, names=("A", "B"), intro=None, ask_phrase=None,
                    fmt=None, label=None, col_labels=None, context=None) -> Item:
    ask = ask or rng.choice(["median_difference", "compare_means"])
    head, nouns, who, s_lo, s_hi, steps = context or rng.choice(TWO_GROUP_CONTEXTS)
    if values is None:
        k = rng.randint(4, 6)
        start = rng.randint(s_lo, s_hi)
        step = rng.choice(steps)
        values = [start + i * step for i in range(k)]
        fa = [rng.randint(0, 9) for _ in range(k)]
        fb = fa[::-1] if rng.random() < 0.5 else [rng.randint(0, 9) for _ in range(k)]
    vals = [q(v) for v in values]
    A, B = expand(vals, [int(f) for f in fa]), expand(vals, [int(f) for f in fb])
    na, nb = len(A), len(B)
    an, bn = names
    label = label or head
    if intro is None:
        intro = (f"Data set {an} consists of the {nouns} of {na} {who} and data set "
                 f"{bn} consists of the {nouns} of {nb} other {who}. The table shows "
                 f"the frequency distribution of the {nouns}.")
    cols = col_labels or (f"Data set {an} frequency", f"Data set {bn} frequency")
    table = [[label, cols[0], cols[1]]]
    for v, x, y in zip(vals, fa, fb):
        table.append([num_str(v), str(int(x)), str(int(y))])
    P = {"kind": "ovd_freq_two", "values": [float(v) for v in vals],
         "fa": [int(f) for f in fa], "fb": [int(f) for f in fb], "ask": ask,
         "claim": (f"The mean of data set {an} is {{rel}} than the mean of data set "
                   f"{bn}.")}

    if ask == "median_difference":
        diff = median(B) - median(A)
        if diff <= 0:
            raise ItemError("the second median is not the greater one")
        key = E(clean(diff))
        stem = (f"{intro} " if intro else "") + (
            ask_phrase or f"The median of the {nouns} for data set {bn} is how much "
            f"greater than the median of the {nouns} for data set {an}?")
        mistakes = [
            Mis(f"subtracted the means instead of the medians", E(mean(B) - mean(A))),
            Mis(f"took the median of data set {bn} and stopped", E(median(B))),
            Mis(f"took the median of data set {an} and stopped", E(median(A))),
            Mis("subtracted the two greatest values instead of the two medians",
                E(max(B) - max(A)) if max(B) > max(A) else None),
        ]
        rationale = (f"Data set {an} has {na} values with median {num_str(median(A))}; "
                     f"data set {bn} has {nb} values with median {num_str(median(B))}.")
        if fmt == "spr":
            return Item("ovd.freq.median_gap", "comparing two frequency tables", "hard",
                        seed, stem, "spr", key, key.gridin(), rationale, table=table,
                        params=P, spr_mistakes=gridin_mistakes(key, mistakes))
        choices, latex, reasons, letter = assemble_num(key, mistakes, rng)
        return Item("ovd.freq.median_gap", "comparing two frequency tables", "hard",
                    seed, stem, "mcq", key, letter, rationale, choices, reasons, latex,
                    table=table, params=P)

    ma, mb = mean(A), mean(B)
    if ma == mb:
        raise ItemError("the two means are equal, so no comparison is sharper")
    greater = ma > mb
    key = (f"The mean of data set {an} is "
           f"{'greater' if greater else 'less'} than the mean of data set {bn}.")
    distractors = [
        Mis("weighted the values the wrong way round: the frequencies say how many of "
            "each value there are, not how large they are",
            f"The mean of data set {an} is {'less' if greater else 'greater'} than the "
            f"mean of data set {bn}."),
        Mis("saw the same values and the same set of frequencies in both columns and "
            "concluded the means must match",
            f"The mean of data set {an} is equal to the mean of data set {bn}."),
        Mis("assumed a frequency table does not pin down a mean",
            "There is not enough information to compare the means of the data sets."),
    ]
    stem = (f"{intro} " if intro else "") + (
        ask_phrase or "Which of the following statements best compares the means of the "
        "two data sets?")
    options, reasons, letter = assemble_text(key, distractors, rng)
    rationale = (f"Data set {an} has mean {num_str(ma)} and data set {bn} has mean "
                 f"{num_str(mb)}.")
    return Item("ovd.freq.compare_means", "comparing two frequency tables", "hard",
                seed, stem, "mcq", E(0), letter, rationale, options, reasons,
                list(options), table=table, params=P)


# --------------------------------------------------------- FOUR TABLES

def _pick_skewed(rng, seed, lists, ask_phrase) -> Item:
    """Which of these data sets has its mean pulled above its middle value?"""
    if lists is None:
        k = rng.choice([7, 9, 11])
        base = rng.randint(2, 7)
        step = rng.randint(5, 20)
        lo = rng.randint(1, 20)
        skewed = [base * 2 ** i for i in range(k)]              # a long right tail
        flat = [rng.randint(2, 9)] * k                          # nothing to pull
        # the half step keeps the four options from reading as one long number
        even = [q(rng.randint(0, 10)) + F(1, 2) + i * step for i in range(k)]
        left = sorted([lo] + [lo + step] * (k // 3)
                      + [lo + 2 * step] * (k - 1 - k // 3))     # a long left tail
        lists = [skewed, flat, even, left]
    shaped = [[q(v) for v in lst] for lst in lists]
    ok = [i for i, lst in enumerate(shaped) if mean(lst) > median(lst)]
    if len(ok) != 1:
        raise ItemError(f"{len(ok)} of the four data sets have a mean above the median")
    key_i = ok[0]
    why = {}
    for i, lst in enumerate(shaped):
        if i == key_i:
            continue
        if len(set(lst)) == 1:
            why[i] = ("every value is the same, so the mean and the median are the "
                      "same number")
        elif mean(lst) == median(lst):
            why[i] = ("the values are spaced evenly about their middle, so the mean "
                      "and the median agree exactly")
        else:
            why[i] = ("the long tail runs to the left here, which pulls the mean below "
                      "the middle value, not above it")
    key = values_line(shaped[key_i])
    distractors = [Mis(why[i], values_line(lst)) for i, lst in enumerate(shaped)
                   if i != key_i]
    stem = ask_phrase or ("For which of the following data sets is the mean greater "
                          "than the median?")
    options, reasons, letter = assemble_text(key, distractors, rng)
    P = {"kind": "ovd_freq_choose", "ask": "mean_over_median",
         "lists": [[float(v) for v in lst] for lst in shaped]}
    rationale = (f"Its mean is {num_str(mean(shaped[key_i]))} and its median is "
                 f"{num_str(median(shaped[key_i]))}; the other three have a mean at or "
                 f"below their median.")
    return Item("ovd.freq.choose.mean_over_median", "shape of a distribution", "medium",
                seed, stem, "mcq", E(0), letter, rationale, options, reasons,
                list(options), params=P)


def _table_text(values, freqs) -> str:
    return ", ".join(f"{num_str(q(v))} (frequency {int(f)})"
                     for v, f in zip(values, freqs))


def freq_choose(rng: random.Random, seed: int, *, ask=None, values=None, freqs=None,
                data=None, f=None, g=None, h=None, lists=None,
                ask_phrase=None) -> Item:
    """Four data sets as options, and one property that picks out exactly one."""
    ask = ask or rng.choice(["match_list", "greatest_mean", "mean_over_median"])
    if ask == "mean_over_median":
        return _pick_skewed(rng, seed, lists, ask_phrase)
    if ask == "match_list":
        if data is None:
            k = rng.randint(3, 4)
            start = rng.randint(1, 20)
            vals = sorted(rng.sample(range(start, start + 20), k))
            fs = [rng.randint(2, 5) for _ in range(k)]
            data = [v for v, c in zip(vals, fs) for _ in range(c)]
        seen: dict[F, int] = {}
        for v in (q(x) for x in data):
            seen[v] = seen.get(v, 0) + 1
        vals = list(seen)
        fs = [seen[v] for v in vals]
        if len(vals) < 3:
            raise ItemError("too few different values to tell four tables apart")
        key = _table_text(vals, fs)
        distractors = [
            Mis("swapped the two columns, reading each count as a data value",
                _table_text(fs, vals)),
            Mis("multiplied each value by how many times it appears instead of counting "
                "the appearances", _table_text(vals, [v * f for v, f in zip(vals, fs)])),
            Mis("multiplied each value by its count and then swapped the columns",
                _table_text([v * f for v, f in zip(vals, fs)], vals)),
            Mis("counted how many values are at least as large as each one, not how "
                "many equal it",
                _table_text(vals, [sum(fs[i:]) for i in range(len(fs))])),
        ]
        stem = (values_line(data) + "\n" +
                (ask_phrase or "Which frequency table correctly represents the data "
                 "listed?"))
        rationale = ", ".join(f"{num_str(v)} appears {int(c)} times"
                              for v, c in zip(vals, fs)) + "."
        P = {"kind": "ovd_freq_choose", "ask": ask, "data": [float(x) for x in data],
             "values": [float(v) for v in vals], "freqs": [int(x) for x in fs]}
    else:
        if values is None:
            k = rng.choice([4, 4, 5])
            start = rng.choice([10, 20, 40, 50, 60, 70]) + rng.randint(0, 3) * 5
            step = rng.choice([5, 10, 10, 20])
            values = [start + i * step for i in range(k)]
            f = rng.randint(2, 6)
            g = rng.randint(f + 1, f + 4)
            h = rng.randint(f + 1, f + 4)
        vals = [q(v) for v in values]
        k = len(vals)
        rising = [f + i for i in range(k)]
        flat = [g] * k
        cup_a = [h + 1] + [h] * (k - 2) + [h + 1]
        cup_b = [h + 2] + [h - 1] * (k - 2) + [h + 2]
        if min(cup_b) < 1 or len({tuple(rising), tuple(flat), tuple(cup_a),
                                  tuple(cup_b)}) != 4:
            raise ItemError("two of the four tables are the same")
        means = [mean(expand(vals, fr)) for fr in (rising, flat, cup_a, cup_b)]
        if means[0] <= max(means[1:]):
            raise ItemError("the rising table does not have the greatest mean")
        key = _table_text(vals, rising)
        distractors = [
            Mis("every value occurs equally often, so its mean is the middle of the "
                "values, not the greatest mean here", _table_text(vals, flat)),
            Mis("gives the greatest value its largest frequency, but gives the least "
                "value the same one, so its mean is still the middle value",
                _table_text(vals, cup_a)),
            Mis("holds the most values of any table, chosen by comparing totals rather "
                "than means", _table_text(vals, cup_b)),
        ]
        stem = (ask_phrase or "Each of the following frequency tables represents a data "
                "set. Which data set has the greatest mean?")
        rationale = ("Only one table gives the larger values the larger frequencies; "
                     f"its mean is {num_str(means[0])}, against "
                     f"{listing([num_str(m) for m in means[1:]])} for the others.")
        P = {"kind": "ovd_freq_choose", "ask": ask, "values": [float(v) for v in vals],
             "rising": rising, "flat": flat, "cup_a": cup_a, "cup_b": cup_b}
    options, reasons, letter = assemble_text(key, distractors, rng)
    return Item(f"ovd.freq.choose.{ask}", "reading a frequency table", "hard", seed,
                stem, "mcq", E(0), letter, rationale, options, reasons, list(options),
                params=P)
