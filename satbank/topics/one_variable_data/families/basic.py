"""Reading a centre or a spread straight off the data.

Three presentations of the same question -- a printed list, a table, a bar
graph -- because that is the axis the source set actually varies. What is
asked (mean, median, mode, range) and what the wrong answers are stay the
same across all three, so the misconceptions are written once.
"""

from __future__ import annotations

import random
from fractions import Fraction as F

from ....exact import E
from ....item import Item, ItemError, Mis
from ....plot import bar, dotplot
from ..common import (assemble_num, cap_first, clean, count_word, listing, mean,
                      median, midrange, mode, num_str, ordinal, plural, q, round_to,
                      spread, values_line)

__all__ = ["list_stat", "table_stat", "bar_read"]

STAT_NOUN = {"mean": "mean", "median": "median", "mode": "mode", "range": "range"}


def _stat(values, stat):
    fn = {"mean": mean, "median": median, "mode": mode, "range": spread}[stat]
    return fn(values)


def _safe(fn, *a):
    try:
        return fn(*a)
    except (ItemError, ValueError, ZeroDivisionError):
        return None


# --------------------------------------------------------- the misconceptions

def centre_candidates(values, stat: str) -> dict[str, Mis]:
    """Every wrong answer this question type produces, named.

    Order matters: `assemble` takes the first three it can use, so the list
    runs from the mistake a teacher sees every week to the one they see once
    a term.
    """
    vals = [q(v) for v in values]
    s = sorted(vals)
    n = len(s)
    mid = (n - 1) // 2
    total = sum(vals, F(0))
    out: dict[str, Mis] = {}

    def put(name, reason, value):
        if value is not None:
            out[name] = Mis(reason, E(value))

    if stat == "median":
        put("mean", "found the mean instead of the median", mean(vals))
        put("mode", "read the mode instead of the median", _safe(mode, vals))
        if n % 2:
            put("even_down", "averaged the middle value with the one below it, as if "
                "the count were even", (s[mid - 1] + s[mid]) / 2 if mid else None)
            put("even_up", "averaged the middle value with the one above it, as if "
                "the count were even", (s[mid] + s[mid + 1]) / 2 if mid + 1 < n else None)
        put("min", "read the least value instead of the middle one", s[0])
        put("range", "found the range instead of the median", spread(vals))
        put("max", "read the greatest value instead of the middle one", s[-1])
        put("midrange", "used the middle of the range rather than the middle value",
            midrange(vals))
        put("printed", "took the middle value of the list as printed, without putting "
            "the values in order first", vals[mid])
        put("one_short", "stopped one value short when counting in to the middle of "
            "the ordered list", s[mid - 1] if mid else None)
    elif stat == "mean":
        put("median", "found the median instead of the mean", median(vals))
        put("mode", "read the most common value instead of the mean", _safe(mode, vals))
        put("midrange", "averaged only the least and the greatest value",
            midrange(vals))
        put("drop_least", "left out the least value and divided by one fewer",
            (total - s[0]) / (n - 1) if n > 1 else None)
        put("max", "read the greatest value instead of the mean", s[-1])
        put("total", "reported the total instead of the mean", total)
        put("min", "read the least value instead of the mean", s[0])
        put("range", "found the range instead of the mean", spread(vals))
        put("over_count", "divided the total by one more than the number of values",
            total / (n + 1))
        put("under_count", "divided the total by one less than the number of values",
            total / (n - 1) if n > 1 else None)
    elif stat == "mode":
        put("median", "found the median instead of the most common value", median(vals))
        put("mean", "found the mean instead of the most common value", mean(vals))
        put("count", "reported how many times the most common value occurs, not the "
            "value itself", max(vals.count(v) for v in set(vals)))
        put("max", "read the greatest value instead of the most common one", s[-1])
        put("min", "read the least value instead of the most common one", s[0])
        put("midrange", "used the middle of the range rather than the value that "
            "appears most often", midrange(vals))
        put("range", "found the range instead of the most common value", spread(vals))
        rest = [v for v in sorted(set(s)) if v != _stat(vals, "mode")]
        put("second", "read the next most common value", max(
            rest, key=lambda v: (vals.count(v), v)) if rest else None)
    else:                                                       # range
        put("max", "reported the greatest value instead of the difference", s[-1])
        put("min", "reported the least value instead of the difference", s[0])
        put("sum_ends", "added the greatest and least values instead of subtracting",
            s[-1] + s[0])
        put("second", "used the second-greatest value instead of the greatest",
            (sorted(set(s))[-2] - s[0]) if len(set(s)) > 1 else None)
        put("count", "counted how many values there are", n)
        put("distinct", "counted how many different values there are", len(set(s)))
        put("median", "found the median instead of the range", median(vals))
        put("midrange", "found the middle of the range instead of its width",
            midrange(vals))
    return out


def _shape_mistakes(cands: dict[str, Mis], key, stat: str, prefer=(), reference=None,
                    rounding=None, only=None) -> list[Mis]:
    """Apply the item's own ordering, then drop the options no student would read.

    A "range" offered against a median of 77 is not a distractor, it is
    padding: nobody mistakes 22 for the middle of numbers in the seventies.
    Anything more than three times the key, or less than a third of it, is cut
    when the mistake is a different kind of quantity from the answer.
    """
    order = list(only) if only else list(prefer) + [k for k in cands if k not in prefer]
    key_v = q(key)
    out = []
    for name in order:
        m = cands.get(name)
        if m is None:
            continue
        v = q(m.value)
        banded = (stat == "range"
                  or name in ("range", "midrange", "count", "distinct"))
        if banded and not only and key_v > 0 and not (key_v / 4 <= v <= key_v * 4):
            continue
        if reference is not None:
            v = abs(v - q(reference))
        if rounding is not None:
            v = round_to(v, rounding)
        if v <= 0:
            continue
        out.append(Mis(m.reason, E(v)))
    return out


def _pick(cands: dict[str, Mis], only=None, prefer=()) -> list[Mis]:
    order = list(only) if only else list(prefer) + [k for k in cands if k not in prefer]
    return [cands[k] for k in order if k in cands]


def _finish(rng, seed, name, skill, difficulty, stem, fmt, key, mistakes, rationale,
            params, figure=None, table=None, prefix="", suffix="", places=None):
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("a grid-in answer must be enterable as digits")
        return Item(name, skill, difficulty, seed, stem, "spr", key, key.gridin(),
                    rationale, figure=figure, table=table, params=params)
    choices, latex, reasons, letter = assemble_num(
        key, mistakes, rng, prefix=prefix, suffix=suffix, places=places)
    return Item(name, skill, difficulty, seed, stem, "mcq", key, letter, rationale,
                choices, reasons, latex, figure=figure, table=table, params=params)


# ------------------------------------------------------------------- LIST

LIST_CONTEXTS = [
    ("bursts", "eruptions of a steam vent"), ("goals", "matches"),
    ("books read", "students"), ("text messages", "days"),
    ("customers", "hours"), ("rainy days", "months"),
    ("seeds that sprouted", "trays"), ("laps", "swimmers"),
    ("bird sightings", "mornings"), ("repairs", "weeks"),
    ("absences", "classes"), ("home runs", "seasons"),
]

LIST_FRAMES = ("count_shown", "data_shown", "list_intro")


def list_stat(rng: random.Random, seed: int, *, values=None, stat=None,
              presentation=None, frame=None, fmt=None, context=None, prefer=(),
              only=None, places=None) -> Item:
    stat = stat or rng.choice(["mean", "median", "median", "range", "mode"])
    presentation = presentation or rng.choice(["list", "list", "dotplot"])
    if values is None:
        values = _draw_values(rng, stat, presentation)
    vals = [q(v) for v in values]
    if len(vals) < 4:
        raise ItemError("too few values to ask about")
    key = E(clean(_stat(vals, stat)))
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")
    n = len(vals)

    if presentation == "dotplot":
        thing, unit = context or rng.choice(LIST_CONTEXTS)
        figure = dotplot([float(v) for v in vals], xlabel=f"Number of {thing}")
        stem = (f"The dot plot shows the number of {thing} recorded for each of "
                f"{n} {unit}. What is the {STAT_NOUN[stat]} of the data shown?")
    else:
        figure = None
        frame = frame or rng.choice(LIST_FRAMES)
        line = values_line(vals, places)
        if frame == "count_shown":
            stem = (f"{line}\nWhat is the {STAT_NOUN[stat]} of the {count_word(n)} "
                    f"data values shown?")
        elif frame == "list_intro":
            stem = (f"A list of {n} data values is shown.\n{line}\n"
                    f"What is the {STAT_NOUN[stat]} of these data?")
        else:
            stem = f"{line}\nWhat is the {STAT_NOUN[stat]} of the data shown?"

    P = {"kind": "ovd_list_stat", "values": [float(v) for v in vals], "stat": stat,
         "rounding": None, "reference": None, "places": places, "prefix": "",
         "suffix": ""}
    mistakes = _shape_mistakes(centre_candidates(vals, stat), key, stat, prefer,
                               only=only)
    rationale = _centre_rationale(vals, stat, key)
    return _finish(rng, seed, f"ovd.list.{stat}.{presentation}",
                   f"{stat} of a data set", "easy", stem, fmt, key, mistakes,
                   rationale, P, figure=figure, places=places)


def _centre_rationale(vals, stat, key) -> str:
    s = sorted(q(v) for v in vals)
    n = len(s)
    if stat == "mean":
        return (f"The {n} values total {num_str(sum(s, F(0)))}, and "
                f"{num_str(sum(s, F(0)))} divided by {n} is {num_str(q(key))}.")
    if stat == "median":
        return (f"In order the values are {values_line(s)}, so the middle of the "
                f"{n} values is {num_str(q(key))}.")
    if stat == "mode":
        return f"{num_str(q(key))} appears more often than any other value."
    return (f"The greatest value is {num_str(s[-1])} and the least is "
            f"{num_str(s[0])}, so the range is {num_str(q(key))}.")


def _draw_values(rng: random.Random, stat: str, presentation: str) -> list[int]:
    n = rng.choice([5, 5, 7, 7, 9, 9, 10, 11])
    if presentation == "dotplot":
        lo = rng.randint(1, 30)
        vals = [rng.randint(lo, lo + rng.choice([4, 5, 6])) for _ in range(n)]
    else:
        lo = rng.randint(1, 60)
        vals = [rng.randint(lo, lo + rng.randint(8, 40)) for _ in range(n)]
    if stat == "mode":
        vals[0] = vals[1] = vals[2] = rng.choice(vals)
        rng.shuffle(vals)
    if stat == "median" and n % 2 == 0:
        raise ItemError("an even count makes the median a half value here")
    return vals


# ------------------------------------------------------------------ TABLE

TABLE_SHAPES = ("rows", "columns", "two_row")


SURVEY_DRAWS = [
    ("Response", ["Once a week or more", "Two or three times a month",
                  "About once a month", "A few times a year", "Almost never", "Never"],
     "Frequency", "people", "The table gives the results of a survey of {t} people who "
     "were asked how often they see a movie in a theater.",
     "How many people responded either \u201c{a}\u201d or \u201c{b}\u201d?"),
    ("Answer", ["Strongly agree", "Agree", "No opinion", "Disagree",
                "Strongly disagree"], "Frequency", "residents",
     "The table gives the results of a survey of {t} residents who were asked whether "
     "the library should open on Sundays.",
     "How many residents answered either \u201c{a}\u201d or \u201c{b}\u201d?"),
    ("Grade", ["Freshman", "Sophomore", "Junior", "Senior"], "Frequency", "students",
     "The table gives the results of a survey of {t} students who were asked which "
     "grade they are in.",
     "How many students are either a {a} or a {b}?"),
]


def table_stat(rng: random.Random, seed: int, *, values=None, stat=None, layout=None,
               fmt=None, labels=None, heading=None, quantity=None, unit_phrase=None,
               intro=None, other=None, other_label=None, reference=None, pair=None,
               total_row=False, compare_other=False,
               reference_phrase=None, rounding=None, prefix="", suffix="", places=None,
               table_places=None, prefer=(), only=None, ask_phrase=None) -> Item:
    """A statistic read out of a printed table.

    `other` is a second row of the same kind -- the high temperatures beside
    the low ones. It never changes the answer, but it supplies the wrong
    answers the source set actually uses: the other row's centre, and the
    centre of the two rows run together.
    """
    layout = layout or rng.choice(TABLE_SHAPES)
    stat = stat or rng.choice(["mean", "median", "median", "range", "pair_sum"])
    if stat == "pair_sum":
        return _pair_sum(rng, seed, values, labels, quantity, heading, intro,
                         ask_phrase, pair, fmt)
    if values is None:
        values, labels, heading, quantity, drawn_q, intro, other, other_label = \
            _draw_table(rng, layout, stat)
        ask_phrase = ask_phrase or drawn_q
    vals = [q(v) for v in values]
    n = len(vals)
    if labels is None:
        labels = [str(i + 1) for i in range(n)]
    if len(labels) != n:
        raise ItemError("a label for every value, please")

    raw = _stat(vals, stat)
    if compare_other:
        if other is None:
            raise ItemError("nothing to compare the second column with")
        reference = _stat([q(v) for v in other], stat)
    keyv = abs(raw - q(reference)) if reference is not None else raw
    if rounding is not None:
        keyv = round_to(keyv, rounding)
    if keyv <= 0:
        raise ItemError("a zero or negative answer is not what this asks for")
    key = E(clean(keyv))

    cands = centre_candidates(vals, stat)
    if other is not None:
        both = vals + [q(v) for v in other]
        cands[f"other_{stat}"] = Mis(
            f"found the {STAT_NOUN[stat]} of the {other_label.lower()} row instead",
            E(_stat([q(v) for v in other], stat)))
        cands["both_median"] = Mis(
            "used the median of both rows of the table together", E(median(both)))
        cands["both_mean"] = Mis(
            "averaged every number in the table instead of only the row asked about",
            E(mean(both)))
    mistakes = _shape_mistakes(cands, raw, stat, prefer, reference, rounding, only)

    tp = table_places if table_places is not None else places
    show = [num_str(v, tp) for v in vals]
    if layout == "columns":
        table = [list(labels), [prefix + s + suffix for s in show]]
    elif layout == "two_row":
        table = [[""] + list(labels),
                 [other_label] + [num_str(v, tp) for v in other],
                 [heading] + [prefix + s + suffix for s in show]]
    elif layout == "rows2":
        table = [[quantity or "Item", other_label or "First", heading or "Second"]] + \
                [[labels[i], num_str(q(other[i]), tp), prefix + show[i] + suffix]
                 for i in range(n)]
    else:
        table = [[quantity or "Item", heading or "Value"]] + \
                [[labels[i], prefix + show[i] + suffix] for i in range(n)]

    ask = ask_phrase or _table_question(stat, unit_phrase, rounding, reference,
                                        reference_phrase, heading, other_label)
    if rounding is not None and not ask_phrase:
        near = {0: "whole number", 1: "tenth", 2: "hundredth"}[rounding]
        ask = ask.rstrip("?") + f", to the nearest {near}?"
    stem = f"{intro}\n{ask}" if intro else ask
    P = {"kind": "ovd_table_stat", "values": [float(v) for v in vals], "stat": stat,
         "rounding": rounding, "reference": float(q(reference)) if reference is not None
         else None, "places": places, "prefix": prefix, "suffix": suffix}
    if compare_other:
        P["other"] = [float(q(v)) for v in other]
        P["compare_other"] = True
        P.pop("reference")
    rationale = _centre_rationale(vals, stat, raw)
    if reference is not None:
        rationale += (f" That differs from {prefix}{num_str(q(reference), places)}"
                      f"{suffix} by {prefix}{num_str(keyv, places)}{suffix}.")
    elif rounding is not None and keyv != raw:
        near = {0: "whole number", 1: "tenth", 2: "hundredth"}[rounding]
        rationale += f" To the nearest {near} that is {num_str(keyv, places)}."
    return _finish(rng, seed, f"ovd.table.{stat}.{layout}", f"{stat} from a table",
                   "medium", stem, fmt or "mcq", key, mistakes, rationale, P,
                   table=table, prefix=prefix, suffix=suffix, places=places)


def _pair_sum(rng, seed, values, labels, quantity, heading, intro, ask_phrase, pair,
              fmt) -> Item:
    """Two rows of a frequency table, added -- the survey item's own question."""
    if values is None:
        quantity, labels, heading, unit, intro_t, ask_t = rng.choice(SURVEY_DRAWS)
        values = [rng.randint(2, 80) for _ in labels]
        intro = intro or intro_t.format(t=num_str(sum(values)))
        pair = pair or tuple(rng.sample(range(len(labels)), 2))
        ask_phrase = ask_phrase or ask_t.format(a=labels[pair[0]].lower(),
                                                b=labels[pair[1]].lower())
    vals = [q(v) for v in values]
    n = len(vals)
    i, j = pair if pair else (n - 2, n - 1)
    if i == j or not (0 <= i < n and 0 <= j < n):
        raise ItemError("a pair of different rows, please")
    total = sum(vals, F(0))
    key = E(vals[i] + vals[j])
    big, small = (i, j) if vals[i] >= vals[j] else (j, i)
    mistakes = [
        Mis(f"read only the row for {labels[big]}", E(vals[big])),
        Mis("subtracted the two frequencies instead of adding them",
            E(abs(vals[i] - vals[j]))),
        Mis("counted everyone who answered something else", E(total - vals[i] - vals[j])),
        Mis(f"read only the row for {labels[small]}", E(vals[small])),
    ]
    table = [[quantity or "Response", heading or "Frequency"]] + \
            [[labels[r], num_str(vals[r])] for r in range(n)] + \
            [["Total", num_str(total)]]
    stem = f"{intro} {ask_phrase}"
    P = {"kind": "ovd_table_stat", "values": [float(v) for v in vals],
         "stat": "pair_sum", "pair": [int(i), int(j)], "rounding": None,
         "reference": None, "places": None, "prefix": "", "suffix": ""}
    rationale = (f"{num_str(vals[i])} + {num_str(vals[j])} = {num_str(q(key.coef))}.")
    return _finish(rng, seed, "ovd.table.pair_sum", "reading a frequency table", "easy",
                   stem, fmt or "mcq", key, mistakes, rationale, P, table=table)


def _table_question(stat, unit_phrase, rounding, reference, reference_phrase,
                    heading, other_label) -> str:
    of = f", {unit_phrase}," if unit_phrase else ""
    what = STAT_NOUN[stat]
    row = f" of the {other_label}" if False else ""
    if reference is not None:
        return (f"What is the difference between the {what}{of} shown in the table "
                f"and {reference_phrase}?")
    if rounding is not None:
        near = {0: "whole number", 1: "tenth", 2: "hundredth"}[rounding]
        return (f"Based on the table, what is the {what}{of} of the values shown, "
                f"to the nearest {near}?")
    return f"What is the {what}{of} of the values shown in the table?"


TABLE_DRAWS = [
    ("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
     "Number of visitors", "The table shows the number of visitors to a museum on each "
     "of {nw} days.", "What is the {what} of the numbers of visitors for the {nw} days shown?"),
    ("Week", ["1", "2", "3", "4", "5", "6"], "Number of packages",
     "The table shows the number of packages a courier delivered in each of {nw} weeks.",
     "What is the {what} of the numbers of packages delivered in the {nw} weeks?"),
    ("Machine", ["A", "B", "C", "D", "E", "F", "G"], "Number of parts",
     "The table shows the number of parts made by each of {nw} machines in one hour.",
     "What is the {what} of the numbers of parts made by the {nw} machines?"),
    ("Student", ["Ana", "Ben", "Cara", "Dev", "Eli"], "Number of points",
     "The table shows the number of points each of {nw} students scored on a quiz.",
     "What is the {what} of the numbers of points scored by the {nw} students?"),
    ("Town", ["Alder", "Birch", "Cedar", "Dale", "Elm", "Fern", "Grove"],
     "Rainfall (inches)", "The table shows last month's rainfall, in inches, in each of "
     "{nw} towns.", "What was the {what} of the rainfall amounts, in inches, for the {nw} towns?"),
    ("Trial", ["1", "2", "3", "4", "5", "6", "7"], "Time (seconds)",
     "The table shows how long a reaction took, in seconds, in each of {nw} trials.",
     "What was the {what} of the times, in seconds, for the {nw} trials?"),
]

TWO_ROW_DRAWS = [
    (["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "High temperature",
     "Low temperature", "The table shows the high and low temperatures, in degrees "
     "Fahrenheit, recorded in a city on each of {nw} days.",
     "What was the {what} of the low temperatures, in degrees Fahrenheit, over the {nw} days?"),
    (["1", "2", "3", "4", "5"], "Morning count", "Afternoon count",
     "The table shows the number of birds counted in a park in the morning and in the "
     "afternoon on each of {nw} days.",
     "What is the {what} of the afternoon counts for the {nw} days?"),
    (["A", "B", "C", "D", "E"], "Before training", "After training",
     "The table shows the number of push-ups each of {nw} athletes completed before and "
     "after a training program.",
     "What is the {what} of the numbers of push-ups completed after training?"),
]


def _draw_table(rng: random.Random, layout: str, stat: str):
    other = other_label = None
    if layout == "two_row":
        labels, other_label, heading, intro, ask = rng.choice(TWO_ROW_DRAWS)
        quantity = None
    else:
        quantity, labels, heading, intro, ask = rng.choice(TABLE_DRAWS)
    n = len(labels)
    if stat == "median" and n % 2 == 0:
        n -= 1
        labels = labels[:n]
    lo = rng.randint(5, 180)
    vals = [rng.randint(lo, lo + rng.randint(6, 60)) for _ in range(n)]
    if layout == "two_row":
        other = [v + rng.randint(6, 30) for v in vals]
    fill = {"n": n, "nw": count_word(n), "what": STAT_NOUN[stat]}
    return (vals, labels, heading, quantity, ask.format(**fill), intro.format(**fill),
            other, other_label)


# -------------------------------------------------------------------- BAR

BAR_CONTEXTS = [
    {"xlabel": "Activity", "ylabel": "Number of students", "labels": "numbers",
     "intro": "A group of students voted on {nw} after-school activities. The bar "
              "graph shows the number of students who voted for each of the {nw} "
              "activities.",
     "total_intro": "A group of {total} students voted on {nw} after-school "
                    "activities. The bar graph shows the number of students who voted "
                    "for each activity.",
     "ref": "activity {a}",
     "value_q": "How many students chose activity {a}?",
     "diff_q": "How many more students chose activity {a} than activity {b}?",
     "mean_q": "What is the mean number of students per activity?"},
    {"xlabel": "Type of monkey", "ylabel": "Number of monkeys",
     "labels": ["mandrill", "baboon", "pygmy marmoset", "bonnet macaque", "vervet"],
     "intro": "The bar graph shows the number of each type of monkey in a sanctuary.",
     "total_intro": "There are {total} monkeys in a sanctuary. The bar graph shows the "
                    "number of each type of monkey.",
     "ref": "{a}s",
     "value_q": "How many {a}s are in this sanctuary?",
     "diff_q": "How many more {a}s are in this sanctuary than {b}s?",
     "mean_q": "What is the mean number of monkeys per type?"},
    {"xlabel": "Group", "ylabel": "Number of books", "labels": "numbers",
     "intro": "The bar graph shows the number of books each of {nw} groups collected "
              "for a book drive.",
     "total_intro": "The bar graph shows the distribution of {total} books collected "
                    "by {n} different groups for a book drive.",
     "ref": "group {a}",
     "value_q": "How many books were collected by group {a}?",
     "diff_q": "How many more books were collected by group {a} than by group {b}?",
     "mean_q": "What is the mean number of books collected per group?"},
    {"xlabel": "Month", "ylabel": "Number of students",
     "labels": ["July", "August", "September", "October", "November"],
     "intro": "The bar graph shows the distribution of the number of students from one "
              "school who were born in one of {nw} months.",
     "total_intro": "The bar graph shows the distribution of the {total} students from "
                    "one school who were born in one of {nw} months.",
     "ref": "{a}",
     "value_q": "How many students were born in {a}?",
     "diff_q": "How many more students were born in {a} than were born in {b}?",
     "mean_q": "What is the mean number of students born per month?"},
    {"xlabel": "Trial", "ylabel": "Number of defective lightbulbs", "labels": "letters",
     "intro": "For quality control, a company that manufactures lightbulbs conducted "
              "{nw} different trials. In each trial, 500 different lightbulbs were "
              "tested. The bar graph shows the number of defective lightbulbs found in "
              "each trial.",
     "total_intro": "For quality control, a company that manufactures lightbulbs found "
                    "{total} defective lightbulbs across {nw} trials of 500 lightbulbs "
                    "each. The bar graph shows the number found in each trial.",
     "ref": "trial {a}",
     "value_q": "How many defective lightbulbs were found in trial {a}?",
     "diff_q": "How many more defective lightbulbs were found in trial {a} than in "
               "trial {b}?",
     "mean_q": "What is the mean number of defective lightbulbs for the {nw} trials?"},
    {"xlabel": "Gift", "ylabel": "Number of volunteers", "labels": "letters",
     "fixed_n": 4,
     "intro": "Each volunteer in a cleanup project was asked to choose a small gift "
              "labeled A, B, C, or D. The bar graph shows the number of volunteers who "
              "chose each gift.",
     "total_intro": "In April, there were {total} volunteers in a cleanup project. Each "
                    "volunteer was asked to choose a small gift labeled A, B, C, or D. "
                    "The bar graph shows the number of volunteers who chose each gift.",
     "ref": "gift {a}",
     "value_q": "How many volunteers chose gift {a}?",
     "diff_q": "How many more volunteers chose gift {a} than gift {b}?",
     "mean_q": "What is the mean number of volunteers per gift?"},
]


def _bar_labels(kind, n):
    if kind == "numbers":
        return [str(i + 1) for i in range(n)]
    if kind == "letters":
        return list("ABCDEFGHIJ")[:n]
    return list(kind)[:n]


def bar_read(rng: random.Random, seed: int, *, values=None, ask=None, target=None,
             other=None, context=None, fmt=None, state_total=False, places=None,
             prefer=(), only=None) -> Item:
    """A bar graph, and the three things the source set asks about one.

    The chart is drawn from the same list the answer is computed from, so a
    regenerated item cannot keep a stale picture.
    """
    ctx = context if isinstance(context, dict) else rng.choice(BAR_CONTEXTS)
    ask = ask or rng.choice(["value", "value", "difference", "mean"])
    if values is None:
        n = ctx.get("fixed_n") or rng.randint(4, min(6, len(_bar_labels(ctx["labels"], 10))))
        values = ([rng.randint(1, 9) for _ in range(n)] if ask == "mean"
                  else [rng.randint(3, 70) for _ in range(n)])
    vals = [q(v) for v in values]
    n = len(vals)
    labels = _bar_labels(ctx["labels"], n)
    if len(labels) != n or (ctx.get("fixed_n") and ctx["fixed_n"] != n):
        raise ItemError("this context does not have a label for every bar")
    total = sum(vals, F(0))
    if ask in ("value", "difference") and len(set(vals)) < n:
        raise ItemError("two bars of equal height make the question ambiguous")

    figure = bar(labels, [float(v) for v in vals], xlabel=ctx["xlabel"],
                 ylabel=ctx["ylabel"])
    fill = {"n": n, "nw": count_word(n), "total": num_str(total)}
    intro = (ctx["total_intro"] if state_total else ctx["intro"]).format(**fill)

    def ref(i):
        return ctx["ref"].format(a=labels[i])

    t = o = None
    if ask == "value":
        t = target if target is not None else rng.randrange(n)
        key = E(vals[t])
        stem = f"{intro} " + ctx["value_q"].format(a=labels[t], **fill)
        cands = {f"bar_{i}": Mis(f"read the bar for {ref(i)} instead of the one asked "
                                 f"about", E(vals[i])) for i in range(n) if i != t}
        top = int(max(vals)) + (10 - int(max(vals)) % 10) % 10
        cands["top"] = Mis("read the top of the vertical scale rather than the top of "
                           "the bar", E(top))
        mistakes = _pick(cands, only, prefer)
        rationale = f"The bar for {ref(t)} reaches {num_str(vals[t])}."
    elif ask == "difference":
        t = target if target is not None else rng.randrange(n)
        o = other if other is not None else rng.choice([i for i in range(n) if i != t])
        if vals[t] <= vals[o]:
            t, o = o, t
        key = E(vals[t] - vals[o])
        stem = f"{intro} " + ctx["diff_q"].format(a=labels[t], b=labels[o], **fill)
        cands = {"taller": Mis(f"read the taller bar, {ref(t)}, instead of the "
                               f"difference", E(vals[t])),
                 "shorter": Mis(f"read the shorter bar, {ref(o)}, instead of the "
                                f"difference", E(vals[o])),
                 "sum": Mis("added the two bars instead of subtracting",
                            E(vals[t] + vals[o]))}
        for i in range(n):
            if i not in (t, o) and vals[t] - vals[i] > 0:
                cands[f"other_{i}"] = Mis(f"subtracted the bar for {ref(i)}, which is "
                                          f"not the one asked about",
                                          E(vals[t] - vals[i]))
        mistakes = _pick(cands, only, prefer)
        rationale = (f"{cap_first(ref(t))} shows {num_str(vals[t])} and {ref(o)} shows "
                     f"{num_str(vals[o])}, and {num_str(vals[t])} \u2212 "
                     f"{num_str(vals[o])} = {num_str(vals[t] - vals[o])}.")
    else:
        key = E(clean(mean(vals)))
        stem = f"{intro} " + ctx["mean_q"].format(**fill)
        mistakes = _shape_mistakes(centre_candidates(vals, "mean"), q(key), "mean",
                                   prefer, only=only)
        rationale = (f"The {n} bars total {num_str(total)}, and {num_str(total)} "
                     f"divided by {n} is {num_str(q(key))}.")

    P = {"kind": "ovd_bar_read", "values": [float(v) for v in vals], "ask": ask,
         "target": t, "other": o, "places": places}
    return _finish(rng, seed, f"ovd.bar.{ask}", "reading a bar graph", "easy", stem,
                   fmt or "mcq", key, mistakes, rationale, P, figure=figure,
                   places=places)
