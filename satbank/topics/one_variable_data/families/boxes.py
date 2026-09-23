"""Box plots: five numbers, and the four things a student reads off them.

A box plot is the one display that says exactly what it shows and nothing
more. Reading a quartile where the median was asked for is the common slip;
reading a mean off it at all is the deeper one, and the comparison template
turns that into the answer.
"""

from __future__ import annotations

import random
from fractions import Fraction as F

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text, gridin_mistakes
from ....plot import boxplot
from ..charts import paired_boxplot
from ..common import assemble_num, count_word, num_str, q

__all__ = ["box_read", "box_compare"]

BOX_CONTEXTS = [
    {"quantity": "number of acres of useful timberland", "short": "number of acres",
     "plural": "numbers of acres", "things": "counties in California",
     "axis": "Acres of useful timberland"},
    {"quantity": "number of visitors recorded", "short": "number of visitors",
     "plural": "numbers of visitors", "things": "days at a museum",
     "axis": "Number of visitors"},
    {"quantity": "number of seeds counted", "short": "number of seeds",
     "plural": "numbers of seeds", "things": "sample plots",
     "axis": "Number of seeds"},
    {"quantity": "distance driven, in miles", "short": "distance",
     "plural": "distances", "things": "delivery vans", "axis": "Distance (miles)"},
    {"quantity": "mass, in grams", "short": "mass", "plural": "masses",
     "things": "rock samples", "axis": "Mass (grams)"},
]

PART = {"least": 0, "q1": 1, "median": 2, "q3": 3, "greatest": 4}
PART_WORD = {"least": "least value", "q1": "first quartile", "median": "median",
             "q3": "third quartile", "greatest": "greatest value"}


def box_read(rng: random.Random, seed: int, *, summary=None, ask=None, n=None,
             context=None, closest=None, intro=None, ask_phrase=None, only=None,
             fmt=None) -> Item:
    ask = ask or rng.choice(["median", "median", "q1", "q3"])
    ctx = context or rng.choice(BOX_CONTEXTS)
    if summary is None:
        lo = rng.randint(1, 40) * rng.choice([1, 10, 100])
        gaps = [rng.randint(2, 9) * max(1, lo // 8) for _ in range(4)]
        summary = [lo]
        for g in gaps:
            summary.append(summary[-1] + g)
    s = [q(v) for v in summary]
    if not all(s[i] < s[i + 1] for i in range(4)):
        raise ItemError("a box plot needs five values in increasing order")
    n = n or rng.choice([9, 11, 13, 15, 17, 19, 21])
    lo, q1, med, q3, hi = s
    key = E(s[PART[ask]])

    cands = {
        "q1": Mis("read the left edge of the box, the first quartile, rather than the "
                  "line inside it", E(q1)),
        "q3": Mis("read the right edge of the box, the third quartile, rather than the "
                  "line inside it", E(q3)),
        "least": Mis("read the end of the left whisker, the least value", E(lo)),
        "greatest": Mis("read the end of the right whisker, the greatest value", E(hi)),
        "midrange": Mis("used the middle of the range rather than the middle value",
                        E((lo + hi) / 2)),
        "q1_hi_mid": Mis("took the value halfway between the first quartile and the "
                         "greatest value, as if the middle of the data were the middle "
                         "of that span", E((q1 + hi) / 2)),
        "box_mid": Mis("took the value halfway across the box rather than the line "
                       "drawn inside it", E((q1 + q3) / 2)),
        "iqr": Mis("found the width of the box, the interquartile range, instead of "
                   "reading a value from it", E(q3 - q1)),
        "range": Mis("found the range instead of reading a value", E(hi - lo)),
    }
    cands.pop(ask, None)
    order = list(only) if only else [k for k in cands]
    # two options a pixel apart on the axis is not a choice, it is a coin toss
    gap, kept, taken = (hi - lo) / 25, [], [q(key)]
    for name in order:
        m = cands.get(name)
        if m is None or m.value is None:
            continue
        v = q(m.value)
        if any(abs(v - t) < gap for t in taken):
            continue
        taken.append(v)
        kept.append(m)
    mistakes = kept

    figure = boxplot(float(lo), float(q1), float(med), float(q3), float(hi),
                     xlabel=ctx["axis"])
    closest = rng.random() < 0.5 if closest is None else closest
    quantity = ctx["quantity"] + ("," if ", in " in ctx["quantity"] else "")
    head = intro or (f"The {quantity} in {n} {ctx['things']} is summarized in "
                     f"the box plot above.")
    if ask_phrase:
        question = ask_phrase
    else:
        # "the median number of acres", but "the first quartile of the number of acres"
        named = (f"the median {ctx['short']}" if ask == "median"
                 else f"the {PART_WORD[ask]} of the {ctx.get('plural', ctx['short'])}")
        question = (f"Which of the following is closest to {named}?" if closest
                    else f"What is {named}?")
    stem = f"{head} {question}"
    P = {"kind": "ovd_box_read", "summary": [float(v) for v in s], "ask": ask}
    rationale = (f"The box plot marks {num_str(lo)}, {num_str(q1)}, {num_str(med)}, "
                 f"{num_str(q3)} and {num_str(hi)}, so the {PART_WORD[ask]} is "
                 f"{num_str(q(key))}.")
    if fmt == "spr":
        return Item(f"ovd.box.{ask}", "reading a box plot", "medium", seed, stem, "spr",
                    key, key.gridin(), rationale, figure=figure, params=P,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble_num(key, mistakes, rng)
    return Item(f"ovd.box.{ask}", "reading a box plot", "medium", seed, stem, "mcq",
                key, letter, rationale, choices, reasons, latex, figure=figure,
                params=P)


PAIR_BOX = [
    {"quantity": "masses, in kilograms", "measure": "mass", "things": "gazelles",
     "axis": "Mass (kilograms)", "groups": ("group 1", "group 2")},
    {"quantity": "heights, in centimeters", "measure": "height", "things": "seedlings",
     "axis": "Height (centimeters)", "groups": ("group A", "group B")},
    {"quantity": "times, in minutes", "measure": "time", "things": "commuters",
     "axis": "Time (minutes)", "groups": ("group 1", "group 2")},
    {"quantity": "distances, in kilometers", "measure": "distance", "things": "runners",
     "axis": "Distance (kilometers)", "groups": ("group A", "group B")},
]


def _mean_band(s) -> tuple[F, F]:
    """How low and how high the mean of a data set with this summary can go.

    A quarter of the values sit in each of the four spans the plot draws, so
    the mean is bounded by putting every quarter at the bottom of its span and
    then at the top. Neither end is reached, so a mean can be anywhere strictly
    between them.
    """
    return (s[0] + s[1] + s[2] + s[3]) / 4, (s[1] + s[2] + s[3] + s[4]) / 4


def _means_overlap(A, B) -> bool:
    """Whether the two pictures leave the comparison of the means open.

    They must. The wrong answers here are the two that read a mean off a box
    plot, and a mean is only unreadable while the two bands overlap: box plots
    far enough apart force `mean A < mean B` as firmly as they force the
    medians, and then the item has two defensible answers.
    """
    (la, ha), (lb, hb) = _mean_band(A), _mean_band(B)
    return la < hb and lb < ha


def box_compare(rng: random.Random, seed: int, *, first=None, second=None, context=None,
                intro=None, ask_phrase=None) -> Item:
    """Two box plots on one scale. Only the medians can be compared."""
    ctx = context or rng.choice(PAIR_BOX)
    if first is None:
        lo = rng.randint(8, 60)
        step = rng.randint(1, 4)
        a = sorted(rng.sample(range(1, 10), 4))
        b = sorted(rng.sample(range(1, 10), 4))
        first = [lo] + [lo + o * step for o in a]
        second = [lo + step] + [lo + step + o * step for o in b]
    A = [q(v) for v in first]
    B = [q(v) for v in second]
    for s in (A, B):
        if not all(s[i] <= s[i + 1] for i in range(4)) or s[0] == s[4]:
            raise ItemError("a box plot needs five values in increasing order")
    if A[2] == B[2]:
        raise ItemError("the two medians are equal, so no statement must be true")
    if not _means_overlap(A, B):
        raise ItemError("these two box plots order the means as well as the medians")
    g1, g2 = ctx["groups"]
    mw = ctx["measure"]
    # every option keeps the same subject, as the source items do: what varies
    # is the measure and the direction, never which group is spoken about first
    rel = "greater" if A[2] > B[2] else "less"
    other = "less" if rel == "greater" else "greater"
    key = f"The median {mw} of {g1} is {rel} than the median {mw} of {g2}."
    # name the reading that actually points the other way in this picture
    flipped = {1: "the left edges of the two boxes", 3: "the right edges of the two "
               "boxes", 0: "the ends of the two left whiskers",
               4: "the ends of the two right whiskers"}
    same = (A[2] > B[2])
    why_rev = next((f"compared {flipped[i]} instead of the lines drawn inside them"
                    for i in (1, 3, 0, 4) if (A[i] > B[i]) != same and A[i] != B[i]),
                   "read the two medians the wrong way round")
    distractors = [
        Mis(why_rev,
            f"The median {mw} of {g1} is {other} than the median {mw} of {g2}."),
        Mis("read the wider box as the larger average; a box plot shows five summary "
            "values, not the individual measurements a mean needs",
            f"The mean {mw} of {g1} is greater than the mean {mw} of {g2}."),
        Mis("read a mean off a display that does not show one: the box plot gives "
            "only the least value, the quartiles, the median and the greatest value",
            f"The mean {mw} of {g1} is less than the mean {mw} of {g2}."),
    ]
    figure = paired_boxplot([[float(v) for v in A], [float(v) for v in B]],
                            [g1.title(), g2.title()], xlabel=ctx["axis"])
    quantity = ctx["quantity"] + ("," if ", in " in ctx["quantity"] else "")
    stem = (intro or f"The box plots summarize the {quantity} of two groups of "
            f"{ctx['things']}.") + " " + (
        ask_phrase or "Based on the box plots, which of the following statements must "
        "be true?")
    options, reasons, letter = assemble_text(key, distractors, rng)
    P = {"kind": "ovd_box_compare", "first": [float(v) for v in A],
         "second": [float(v) for v in B], "groups": [g1, g2],
         "claim": f"The median {mw} of {g1} is {{rel}} than the median {mw} of {g2}."}
    rationale = (f"The line inside the box is at {num_str(A[2])} for {g1} and "
                 f"{num_str(B[2])} for {g2}; no box plot reports a mean.")
    return Item("ovd.box.compare", "comparing two box plots", "hard", seed, stem,
                "mcq", E(0), letter, rationale, options, reasons, list(options),
                figure=figure, params=P)
