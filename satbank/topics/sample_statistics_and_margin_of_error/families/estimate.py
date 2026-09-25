"""Scaling a sample statistic up to the population it was drawn from.

Five generators, all built on one exact idea: a sample of `n` units in which
`k` had the trait estimates the population's count as `population * k / n`.
Nothing is ever a float -- `k / n` is a `Fraction`, and a stem that says
"about", "best estimate" or "round to the nearest whole number" rounds once,
through `values.unambiguous`, which throws the draw away rather than ship a
value sitting exactly between two printable answers.

The wrong answers are the arithmetic a student actually does: the count
inside the sample, the rate applied to the part of the population that was
*not* sampled, the sample's percent written down as though it were a
headcount, the population divided by the count instead of scaled by the rate.
Each is named where it is computed.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from fractions import Fraction as Q

from ....item import Item, ItemError, Mis, assemble, gridin_mistakes
from ..values import Num, dec, grid, q, snap, tidy, unambiguous

__all__ = ["scale_count", "scale_group", "scale_range", "scale_two_way",
           "scale_frequency", "SCALE", "GROUP", "RANGE", "TWO_WAY", "FREQ"]


@dataclass(frozen=True)
class Kit:
    key: str
    stem: str
    ranges: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)


def _spread(vals, frac=Q(1, 10)) -> None:
    """Four options a student has to be able to tell apart.

    A stem that says "about" or "best estimate" is unanswerable when two of
    its options are within rounding of each other, and no gate check reads
    the gap. The floor is a tenth of the larger value; the closest pair in
    any official item here is a third apart.
    """
    for i, a in enumerate(vals):
        for b in vals[i + 1:]:
            if abs(a - b) * (1 / frac) < max(abs(a), abs(b)):
                raise ItemError(f"the options {a} and {b} are too close to tell "
                                f"apart on a stem that says 'about'")


def _pick(pool: dict, order, wrongs=None) -> list[Mis]:
    """The misconceptions this draw offers, in the order it offers them.

    A free draw takes the template's own order; a source item passes
    `wrongs`, naming the three College Board reached for. An entry whose
    value is None does not apply to this draw and is skipped.
    """
    names = list(order if wrongs is None else wrongs)
    out = []
    for name in names:
        if name not in pool:
            raise ItemError(f"no misconception named {name!r} in this pool")
        why, value = pool[name]
        if value is not None:
            out.append(Mis(why, Num(value)))
    return out


# ------------------------------------------------------- k of n, scaled up

SCALE = {
    "council": Kit(
        key="council",
        stem="A city has {N} city council members. A reporter polled a random "
             "sample of {n} city council members and found that {k} of those "
             "polled supported a specific bill. Based on the sample, which of "
             "the following is the best estimate of the number of city council "
             "members in the city who support the bill?",
        ranges=dict(N=(40, 120), Nstep=2, n=(10, 30), nstep=2),
        extra=dict(unit="members", polled="polled")),
    "icecream": Kit(
        key="icecream",
        stem="A random sample of {n} people from a town with a population of "
             "{N} were asked to name their favorite flavor of ice cream. If {k} "
             "people in the sample named chocolate as their favorite ice-cream "
             "flavor, about how many people in the town would be expected to "
             "name chocolate?",
        ranges=dict(N=(8000, 40000), Nstep=1, n=(40, 120), nstep=10),
        extra=dict(unit="people", polled="in the sample")),
    "seedlings": Kit(
        key="seedlings",
        stem="A nursery has {N} spruce seedlings. An inspector selected a random "
             "sample of {n} of the seedlings and found that {k} of them had "
             "reached the required height. Based on the sample, which of the "
             "following is the best estimate of the number of seedlings at the "
             "nursery that have reached the required height?",
        ranges=dict(N=(400, 2000), Nstep=20, n=(20, 80), nstep=5),
        extra=dict(unit="seedlings", polled="selected")),
}


def scale_count(rng: random.Random, seed: int, *, ctx=None, N=None, n=None,
                k=None, base=None, wrongs=None, tier="easy") -> Item:
    """`k` of `n` in the sample; estimate the count in a population of `N`.

    `base` is the population figure the four options are built on. It is `N`
    for a round population and a rounded `N` when the source item's options
    are -- official item 1.2 prints a town of 14,878 and then offers 350,
    2,100, 7,500 and 10,500, every one of which is built on 15,000. The draw
    is refused unless the printed key really is the option closest to the
    exact estimate, which is what the stem's "about" promises.
    """
    kit = SCALE[ctx] if ctx is not None else SCALE[rng.choice(sorted(SCALE))]
    r = kit.ranges
    N = int(N) if N is not None else rng.randrange(r["N"][0], r["N"][1] + 1, r["Nstep"])
    n = int(n) if n is not None else rng.randrange(r["n"][0], r["n"][1] + 1, r["nstep"])
    k = int(k) if k is not None else rng.randint(1, n - 1)
    if not 0 < k < n or n >= N:
        raise ItemError("the sample is a proper part of the population")
    base = Q(N) if base is None else q(base)
    if not Q(99, 100) <= base / N <= Q(101, 100):
        raise ItemError("the figure the options are built on has to be the "
                        "population, give or take a rounding")

    rate = Q(k, n)
    key = base * rate
    exact = Q(N) * rate
    if key.denominator != 1:
        raise ItemError("the estimate has to be a whole number of units")

    pool = {
        "sample_count": ("gave the number in the sample rather than an estimate "
                         "for the whole population", Q(k)),
        "unpolled": ("applied the sample's rate only to the members who were not "
                     f"{kit.extra['polled']}", (base - n) * rate),
        "rate_as_count": ("read the sample's percent as a number of units",
                          100 * rate),
        "times_n": ("multiplied the count in the sample by the size of the "
                    "sample instead of scaling it to the population", Q(k * n)),
        "tenth_rate": (f"read the sample as {k} out of 10 rather than {k} out "
                       f"of {n}", base * Q(k, 10)),
        "n_as_percent": ("read the size of the sample as a percent of the "
                         "population", base * Q(n, 100)),
        "complement": ("estimated the units that did not have the trait",
                       base * Q(n - k, n)),
    }
    # two options a tenth of a percent apart cannot both be read off a stem
    # that says "about how many": 774 against 779 has no answer a student can
    # pick. College Board's own sets are never closer than a third apart.
    pool = {a: (w, v if (v is not None and q(v).denominator == 1 and q(v) > 0
                         and q(v) < Q(N) and abs(q(v) - key) * 10 >= key)
                else None) for a, (w, v) in pool.items()}
    order = ["sample_count", "unpolled", "rate_as_count", "times_n",
             "tenth_rate", "n_as_percent", "complement"]
    mistakes = _pick(pool, order, wrongs)
    choices, latex, reasons, letter = assemble(Num(key), mistakes, rng)

    # "about how many" and "best estimate" promise that one printed option is
    # nearer the truth than the others; a tie has no answer
    vals = [q(c.replace(",", "")) for c in choices]
    best = min(vals, key=lambda v: abs(v - exact))
    if sum(1 for v in vals if abs(v - exact) == abs(best - exact)) != 1 or best != key:
        raise ItemError("the keyed option is not the one closest to the estimate")
    _spread(vals)

    stem = tidy(kit.stem.format(N=f"{N:,}", n=f"{n:,}", k=f"{k:,}"))
    why = (f"{k} of {n} is {rate}, so the estimate for {dec(base, 0)} is "
           f"{dec(key, 0)}.")
    P = dict(kind="sstat.scale_count", ctx=kit.key, N=N, n=n, k=k,
             base=str(base), choices=list(choices))
    return Item("sstat.scale_count", "sample statistics and margin of error",
                tier, seed, stem, "mcq", Num(key), letter, why, choices, reasons,
                latex, params=P)


# ------------------------------------------- one group, scaled to many groups

GROUP = {
    "siblings": Kit(
        key="siblings",
        stem="In State X, Mr. Camp's eighth-grade class consisting of {n} "
             "students was surveyed and {pct} percent of the students reported "
             "that they had at least two siblings. The average eighth-grade "
             "class size in the state is {n}. If the students in Mr. Camp's "
             "class are representative of students in the state's eighth-grade "
             "classes and there are {g} eighth-grade classes in the state, which "
             "of the following best estimates the number of eighth-grade "
             "students in the state who have fewer than two siblings?",
        ranges=dict(n=(18, 32), g=(600, 2600), gstep=100),
        extra=dict(who="students", whole="the state's eighth-grade students",
                   trait="have at least two siblings",
                   asked="have fewer than two siblings")),
    "commuters": Kit(
        key="commuters",
        stem="A transit agency surveyed the {n} riders on one of its buses and "
             "{pct} percent of them reported that they hold a monthly pass. The "
             "average number of riders on a bus in the agency's fleet is {n}. If "
             "the riders on the surveyed bus are representative of the agency's "
             "riders and the fleet carries {g} busloads of riders each day, "
             "which of the following best estimates the number of the agency's "
             "daily riders who do not hold a monthly pass?",
        ranges=dict(n=(20, 44), g=(200, 1500), gstep=50),
        extra=dict(who="riders", whole="the agency's daily riders",
                   trait="hold a monthly pass", asked="do not hold a monthly pass")),
}


def scale_group(rng: random.Random, seed: int, *, ctx=None, n=None, k=None,
                g=None, wrongs=None, tier="hard") -> Item:
    """One group of `n` reports `k` with the trait; `g` such groups in all.

    The stem prints the percent rounded to a tenth, which is what makes the
    item hard: the exact statistic is `k / n`, and the answer is the
    complement scaled by the number of groups. The printed percent is
    derived from `k` and `n` and refused when it lands on a half-tenth.
    """
    kit = GROUP[ctx] if ctx is not None else GROUP[rng.choice(sorted(GROUP))]
    r = kit.ranges
    n = int(n) if n is not None else rng.randrange(r["n"][0] + r["n"][0] % 2,
                                                   r["n"][1] + 1, 2)
    k = int(k) if k is not None else rng.randint(2, n - 2)
    g = int(g) if g is not None else rng.randrange(r["g"][0], r["g"][1] + 1, r["gstep"])
    if not 0 < k < n:
        raise ItemError("the reported group is a proper part of the class")
    # the class must not split down the middle: when it does, the group that
    # was asked about, the group that was not, and half the total are all the
    # same number, and three of the four options collapse onto the key
    if n % 2 or 2 * k == n:
        raise ItemError("an evenly split class leaves nothing to tell apart")
    pct = unambiguous(Q(100 * k, n), Q(1, 10))
    if pct.denominator == 1:
        # the item is about recovering the count from a percent printed to a
        # tenth; a whole-number percent prints as "50.0 percent", which no
        # source item does, and gives the count away
        raise ItemError("this class gives a whole-number percent")
    total = n * g
    key = Q((n - k) * g)
    pool = {
        "reported_group": (f"estimated the {kit.extra['who']} who "
                           f"{kit.extra['trait']}, the group the question "
                           f"leaves out", Q(k * g)),
        "all_units": (f"gave every one of {kit.extra['whole']} without using "
                      f"the survey at all", Q(total)),
        "half": ("assumed the group splits evenly and took half of the total",
                 Q(total, 2)),
    }
    pool = {a: (w, v if v is not None and q(v).denominator == 1 and q(v) > 0
                else None) for a, (w, v) in pool.items()}
    order = ["reported_group", "half", "all_units"]
    mistakes = _pick(pool, order, wrongs)
    choices, latex, reasons, letter = assemble(Num(key), mistakes, rng)
    _spread([q(c.replace(",", "")) for c in choices])
    stem = tidy(kit.stem.format(n=n, pct=dec(pct, 1), g=f"{g:,}"))
    why = (f"{dec(pct, 1)} percent of {n} is {k} {kit.extra['who']}, so {n - k} "
           f"of the {n} {kit.extra['asked']}, and {n - k} x {g:,} = "
           f"{dec(key, 0)}.")
    P = dict(kind="sstat.scale_group", ctx=kit.key, n=n, k=k, g=g,
             pct=str(pct), choices=list(choices))
    return Item("sstat.scale_group", "sample statistics and margin of error",
                tier, seed, stem, "mcq", Num(key), letter, why, choices, reasons,
                latex, params=P)


# ------------------------------------------- the mean of a few units, scaled

RANGE = {
    "forest": Kit(
        key="forest",
        stem="A certain forest is {T} acres. To estimate the number of trees in "
             "the forest, a ranger randomly selects {j} different 1-acre parcels "
             "in the forest and determines the number of trees in each parcel. "
             "The numbers of trees in the sample acres are {vals}. Based on the "
             "mean of the sample, which of the following ranges contains the "
             "best estimate for the number of trees in the entire forest?",
        ranges=dict(T=(160, 420), j=(5, 5), v=(30, 90)),
        extra=dict(width=1000)),
    "shelves": Kit(
        key="shelves",
        stem="A library has {T} shelves of the same length. To estimate the "
             "number of books in the library, a librarian randomly selects {j} "
             "of the shelves and counts the books on each. The numbers of books "
             "on the sample shelves are {vals}. Based on the mean of the sample, "
             "which of the following ranges contains the best estimate for the "
             "number of books in the library?",
        ranges=dict(T=(120, 380), j=(5, 5), v=(24, 74)),
        extra=dict(width=500)),
}


def _band(v, width: int) -> tuple[Q, Q]:
    """The printed range that holds `v`: width `width`, centred on `v` rounded
    to the nearest half-width. Official item 1.3's four ranges are exactly
    this, and it is the only rule that produces all four."""
    half = Q(width, 2)
    mid = unambiguous(v, half)
    return mid - half, mid + half


def scale_range(rng: random.Random, seed: int, *, ctx=None, T=None, vals=None,
                wrongs=None, tier="easy") -> Item:
    """The sample mean scaled to the whole, answered by a range rather than a
    number. The wrong ranges hold the other summaries of the same sample."""
    kit = RANGE[ctx] if ctx is not None else RANGE[rng.choice(sorted(RANGE))]
    r, width = kit.ranges, kit.extra["width"]
    T = int(T) if T is not None else rng.randint(*r["T"])
    j = r["j"][0]
    if vals is None:
        vals = sorted(rng.randint(*r["v"]) for _ in range(j))
        rng.shuffle(vals)
    vals = [int(v) for v in vals]
    if len(vals) != j or len(set(vals)) != j:
        raise ItemError(f"the sample is {j} different parcels")
    s = sorted(vals)
    mean = Q(sum(vals), j)
    stats = {
        "mean": (None, mean * T),
        "median": ("used the middle value of the sample instead of its mean",
                   Q(s[j // 2]) * T),
        "low": ("used the smallest count in the sample instead of its mean",
                Q(s[0]) * T),
        "high": ("used the largest count in the sample instead of its mean",
                 Q(s[-1]) * T),
        "total": ("scaled the total of the sample rather than its mean",
                  Q(sum(vals)) * T // j * j),
    }
    order = ["low", "median", "high", "total"]
    names = list(wrongs if wrongs is not None else order)
    bands = {"mean": _band(stats["mean"][1], width)}
    for nm in names:
        if nm not in stats or nm == "mean":
            raise ItemError(f"no sample summary named {nm!r}")
        bands[nm] = _band(stats[nm][1], width)
    picked = ["mean"] + names[:3]
    if len(picked) != 4 or len({bands[p] for p in picked}) != 4:
        raise ItemError("two of the printed ranges are the same range")
    inside = [p for p in picked
              if bands[p][0] <= stats["mean"][1] <= bands[p][1]]
    if inside != ["mean"]:
        raise ItemError("the sample mean falls in more than one printed range")

    rows = sorted(picked, key=lambda p: bands[p][0])
    choices = [f"{dec(bands[p][0], 0)} to {dec(bands[p][1], 0)}" for p in rows]
    reasons = ["" if p == "mean" else stats[p][0] for p in rows]
    letter = "ABCD"[rows.index("mean")]
    if len(set(choices)) != 4:
        raise ItemError("two options print the same range")
    listed = ", ".join(str(v) for v in vals[:-1]) + f", and {vals[-1]}"
    stem = tidy(kit.stem.format(T=f"{T:,}", j=j, vals=listed))
    why = (f"The mean of the sample is {dec(mean, 2)}, so the estimate is "
           f"{dec(mean, 2)} x {T:,} = {dec(stats['mean'][1], 0)}.")
    P = dict(kind="sstat.scale_range", ctx=kit.key, T=T, vals=list(vals),
             width=width, choices=list(choices))
    return Item("sstat.scale_range", "sample statistics and margin of error",
                tier, seed, stem, "mcq", Num(stats["mean"][1]), letter, why,
                choices, reasons, list(choices), params=P)


# ----------------------------------------------- a two-way table, gridded in

TWO_WAY = {
    "mayor": Kit(
        key="mayor",
        stem="A random sample of {n} town voters were asked if they plan to vote "
             "for Candidate A or Candidate B for mayor. The results were sorted "
             "by gender and are shown in the table below. The town has a total "
             "of {N} voters. Based on the table, what is the best estimate of "
             "the number of voters who plan to vote for Candidate A?",
        ranges=dict(N=(3000, 12000), Nstep=500),
        extra=dict(corner="", cols=("Plan to vote for Candidate A",
                                    "Plan to vote for Candidate B"),
                   rows=("Female", "Male"), focus=0)),
    "shift": Kit(
        key="shift",
        stem="A random sample of {n} employees at a company were asked whether "
             "they prefer an earlier start or a later start to the working day. "
             "The results were sorted by shift and are shown in the table below. "
             "The company has {N} employees in all. Based on the table, what is "
             "the best estimate of the number of employees who prefer an earlier "
             "start?",
        ranges=dict(N=(2000, 9000), Nstep=250),
        extra=dict(corner="", cols=("Prefer an earlier start",
                                    "Prefer a later start"),
                   rows=("Day shift", "Night shift"), focus=0)),
}


def scale_two_way(rng: random.Random, seed: int, *, ctx=None, N=None, counts=None,
                  tier="medium") -> Item:
    """A two-way table of a sample, scaled to the population. Grid-in.

    The sample size is the sum of the table's own cells, never a separate
    number: a table that does not add up cannot describe the sample the stem
    names.
    """
    kit = TWO_WAY[ctx] if ctx is not None else TWO_WAY[rng.choice(sorted(TWO_WAY))]
    e = kit.extra
    if counts is None:
        counts = [[rng.randrange(10, 220) for _ in e["cols"]] for _ in e["rows"]]
    counts = [[int(c) for c in row] for row in counts]
    n = sum(sum(r) for r in counts)
    col = sum(row[e["focus"]] for row in counts)
    if not 0 < col < n:
        raise ItemError("the column has to be a proper part of the sample")
    r = kit.ranges
    N = int(N) if N is not None else rng.randrange(r["N"][0], r["N"][1] + 1, r["Nstep"])
    if N <= n:
        raise ItemError("the population is larger than the sample")
    # "the best estimate" rounds, so the draw is refused only when the exact
    # value sits halfway between two whole counts and the stem cannot say
    # which of them it means
    key = unambiguous(Q(N * col, n), 1)
    table = [[e["corner"]] + list(e["cols"])]
    for name, row in zip(e["rows"], counts):
        table.append([name] + [f"{c:,}" for c in row])
    stem = tidy(kit.stem.format(n=f"{n:,}", N=f"{N:,}"))
    why = (f"{col:,} of the {n:,} in the sample answered {e['cols'][e['focus']].lower()}, "
           f"and {col:,}/{n:,} of {N:,} is {dec(key, 0)}.")
    P = dict(kind="sstat.scale_two_way", ctx=kit.key, N=N, counts=counts,
             focus=e["focus"])
    return Item("sstat.scale_two_way", "sample statistics and margin of error",
                tier, seed, stem, "spr", Num(key), grid(key), why,
                table=table, params=P,
                spr_mistakes=gridin_mistakes(Num(key), [
                    Mis("reported the count in the sample instead of scaling to the population",
                        Num(col)),
                    Mis("scaled the other response column instead of the asked-for column",
                        Num(snap(Q(N * (n - col), n), 1))),
                    Mis("scaled only the population outside the sample",
                        Num(snap(Q((N - n) * col, n), 1))),
                ]))


# ------------------------------------- a frequency table, differenced, gridded

FREQ = {
    "nuclear": Kit(
        key="nuclear",
        stem="A researcher interviewed {n} randomly selected US residents and "
             "asked about their views on the use of nuclear energy. The table "
             "above summarizes the responses of the interviewees. If the "
             "population of the United States was {P} million when the survey "
             "was given, based on the sample data for the {n} US residents, what "
             "is the best estimate, in millions, of the difference between the "
             "number of US residents who somewhat favor or strongly favor the "
             "use of nuclear energy and the number of those who somewhat oppose "
             "or strongly oppose it? (Round your answer to the nearest whole "
             "number.)",
        ranges=dict(P=(150, 400), Pstep=25, f=(30, 240)),
        extra=dict(title="Views on Nuclear Energy Use", head=("Response", "Frequency"),
                   rows=("Strongly favor", "Somewhat favor", "Somewhat oppose",
                         "Strongly oppose"), plus=(0, 1), minus=(2, 3))),
    "library": Kit(
        key="library",
        stem="A librarian asked {n} randomly selected members of a county "
             "library system how often they borrow an e-book. The table above "
             "summarizes the responses. If the county has {P} thousand library "
             "members, based on the sample data for the {n} members, what is the "
             "best estimate, in thousands, of the difference between the number "
             "of members who borrow an e-book weekly or monthly and the number "
             "of those who borrow one yearly or never? (Round your answer to the "
             "nearest whole number.)",
        ranges=dict(P=(40, 180), Pstep=5, f=(25, 200)),
        extra=dict(title="How Often Members Borrow an E-Book",
                   head=("Response", "Frequency"),
                   rows=("Weekly", "Monthly", "Yearly", "Never"),
                   plus=(0, 1), minus=(2, 3))),
}


def scale_frequency(rng: random.Random, seed: int, *, ctx=None, P=None,
                    freq=None, tier="hard") -> Item:
    """A frequency table, two groups differenced and scaled. Grid-in."""
    kit = FREQ[ctx] if ctx is not None else FREQ[rng.choice(sorted(FREQ))]
    e, r = kit.extra, kit.ranges
    if freq is None:
        freq = [rng.randint(*r["f"]) for _ in e["rows"]]
    freq = [int(f) for f in freq]
    if len(freq) != len(e["rows"]) or any(f <= 0 for f in freq):
        raise ItemError("every response in the table has a positive frequency")
    n = sum(freq)
    plus = sum(freq[i] for i in e["plus"])
    minus = sum(freq[i] for i in e["minus"])
    if plus <= minus or 8 * (plus - minus) < n:
        raise ItemError("the two groups are too close for the difference the "
                        "stem asks for to survive being scaled and rounded")
    P = int(P) if P is not None else rng.randrange(r["P"][0], r["P"][1] + 1, r["Pstep"])
    key = unambiguous(Q((plus - minus) * P, n), 1)
    if key < 5:
        raise ItemError("the estimate is too small to be worth rounding to a "
                        "whole number")
    table = [list(e["head"])] + [[name, f"{f:,}"] for name, f in zip(e["rows"], freq)]
    stem = tidy(kit.stem.format(n=f"{n:,}", P=f"{P:,}"))
    why = (f"{plus:,} of the {n:,} responses are on one side and {minus:,} on the "
           f"other, a difference of {plus - minus:,}, and "
           f"{plus - minus:,}/{n:,} of {P:,} rounds to {dec(key, 0)}.")
    P_ = dict(kind="sstat.scale_frequency", ctx=kit.key, P=P, freq=list(freq))
    return Item("sstat.scale_frequency", "sample statistics and margin of error",
                tier, seed, stem, "spr", Num(key), grid(key), why,
                table=table, params=P_,
                spr_mistakes=gridin_mistakes(Num(key), [
                    Mis("scaled only the favorable responses, without subtracting the opposing ones",
                        Num(snap(Q(P * plus, n), 1))),
                    Mis("scaled only the opposing responses, without finding the difference",
                        Num(snap(Q(P * minus, n), 1))),
                    Mis("reported the difference in the sample without scaling it",
                        Num(plus - minus)),
                    Mis("added the two response groups instead of subtracting them", Num(P)),
                ]))
