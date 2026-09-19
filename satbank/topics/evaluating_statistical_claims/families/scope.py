"""How far a study's results reach.

The one rule, and it is the whole family:

    a result reaches exactly the population the units were **randomly
    selected from**, and no further; when they were not randomly selected it
    reaches only the units measured.

So a population is licensed when it sits inside the sampling frame, the
measured sample is always licensed, and the answer to "the largest population"
is the unique largest licensed one. Nothing here is told which option that is:
the frame is a parameter *because the stem is written from it*, so a caller
that moves the frame moves the printed study with it.
"""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text
from ..world import (SCOPES, TABLES, canon, descends, option_phrase, plainest,
                     pops_of, unit_phrase, within)

__all__ = ["generalize", "generalize_table"]

# A method that selects units at random from the frame earns generalization to
# that frame. Anything else -- the first to arrive, those who volunteered --
# earns nothing beyond the units actually measured.
GENERALIZES = {"random": True, "convenience": False, "volunteer": False}


def _candidates(sc, n: int, extra: dict) -> dict[str, dict]:
    """Every option this context can print, as {id: record}.

    A record is `kind` ("pop", "sample", "subsample"), the printed text, and
    for a population its spec. The spec is what the lattice compares; the text
    is assembled from the context's own fragments, so a spec and its sentence
    cannot drift apart.
    """
    out: dict[str, dict] = {}
    for pid, spec in pops_of(sc).items():
        out[pid] = dict(kind="pop", spec=spec,
                        text=option_phrase(sc, spec).format(**extra))
    if sc.sample:
        out["sample"] = dict(kind="sample", spec=None,
                             text=sc.sample.format(n=n, **extra))
    if sc.subsample:
        out["subsample"] = dict(kind="subsample", spec=None,
                                text=sc.subsample.format(n=n, **extra))
    return out


def _licensed(sc, cand: dict, frame: dict, generalizes: bool) -> bool:
    """Do the results reach this population?"""
    if cand["kind"] in ("sample", "subsample"):
        return True                     # the units that were actually measured
    return generalizes and within(sc, cand["spec"], frame)


def _reaches(sc, a: dict, b: dict, frame: dict) -> bool:
    """Is population `a` contained in population `b`?

    The sample was drawn from the frame, so it sits inside every population
    the frame sits inside; a named part of the sample sits inside the sample.
    """
    if a is b:
        return True
    if b["kind"] == "subsample":
        return a["kind"] == "subsample"
    if b["kind"] == "sample":
        return a["kind"] in ("sample", "subsample")
    if a["kind"] in ("sample", "subsample"):
        return within(sc, frame, b["spec"])
    return within(sc, a["spec"], b["spec"])


def _largest(sc, cands: list[dict], frame: dict, generalizes: bool):
    """The unique largest licensed population, or None when there is no unique one."""
    live = [c for c in cands if _licensed(sc, c, frame, generalizes)]
    top = [c for c in live if all(_reaches(sc, o, c, frame) for o in live)]
    return top[0] if len(top) == 1 else None


def _why(sc, cand: dict, frame: dict, generalizes: bool) -> str:
    unit, who = sc.unit, sc.pronoun
    """The mistake a student makes by choosing this option."""
    if cand["kind"] == "subsample":
        return (f"read the table as the study, and applied the result only to the "
                f"part of the sample the table reports")
    if cand["kind"] == "sample":
        return (f"stopped at the {unit} {who} were measured, although selecting them "
                f"at random earns the population they were drawn from")
    spec = cand["spec"]
    if not generalizes:
        return ("read a sample that was not selected at random as if it had been, "
                "and generalized from it")
    if within(sc, spec, frame):
        return ("named a population the sample can speak for, but not the largest "
                "one it can speak for")
    cs, cf = canon(sc, spec), canon(sc, frame)
    wider = [d for d in sc.dims if cs[d.name] != cf[d.name]
             and descends(d, cf[d.name], cs[d.name])]
    apart = [d for d in sc.dims if cs[d.name] != cf[d.name]
             and not descends(d, cf[d.name], cs[d.name])]
    if apart:
        return ("applied the result to a group the sample was never drawn from, "
                "rather than to the group it was drawn from")
    place = any(d.slot == "place" for d in wider)
    trait = any(d.slot != "place" for d in wider)
    if place and trait:
        return ("generalized past the sampling frame twice over, to a wider group in "
                "a wider place than the one sampled")
    if place:
        return ("generalized past the sampling frame: the units were drawn from one "
                "place, so the result stops there")
    return ("dropped the trait the units were selected on and generalized to the "
            "whole group")


def _build(sc, rng, seed, template, tier, n, method, frame, wrongs,
           extra, stem, table=None) -> Item:
    generalizes = GENERALIZES[method]
    cand = _candidates(sc, n, extra)
    key = _largest(sc, list(cand.values()), frame, generalizes)
    if key is None:
        raise ItemError("no single largest population among the printed ones")
    key_id = next(k for k, v in cand.items() if v is key)

    pool = [k for k in cand if k != key_id]
    if wrongs is None:
        rng.shuffle(pool)
        picked = pool[:3]
    else:
        for w in wrongs:
            if w not in cand:
                raise ItemError(f"{sc.key} cannot print the option {w!r}")
            if w == key_id:
                raise ItemError(f"{w!r} is the population this study licenses; "
                                "it cannot be printed as a wrong answer")
        picked = list(wrongs)
    if len(picked) != 3:
        raise ItemError("need exactly three wrong populations")

    unit, who = sc.unit, sc.pronoun
    wrong = [Mis(_why(sc, cand[w], frame, generalizes), cand[w]["text"])
             for w in picked]
    choices, reasons, letter = assemble_text(key["text"], wrong, rng)
    if len(set(choices)) != 4:
        raise ItemError("two options name the same population")

    frame_text = option_phrase(sc, plainest(sc, frame)).format(**extra)
    frame_text = frame_text[0].lower() + frame_text[1:]
    why = (f"The {unit} were selected at random from {frame_text}, so the results "
           f"reach that population and no wider one."
           if generalizes else
           f"The {unit} were not selected at random, so the results reach only the "
           f"{unit} {who} were measured.")
    P = dict(kind=template, scope=sc.key, n=n, method=method,
             frame=dict(frame), texts=list(choices), extra=dict(extra))
    return Item(template, "evaluating a statistical claim", tier, seed, stem, "mcq",
                E(0), letter, why, choices, reasons, list(choices),
                table=table, params=P)


# --------------------------------------------------------------- the family

def generalize(rng: random.Random, seed: int, *, ctx=None, n=None, method=None,
               frame=None, wrongs=None, k=None, years=None, tier="hard") -> Item:
    """Which population the results of a survey or an experiment reach."""
    sc = SCOPES[ctx] if ctx is not None else SCOPES[rng.choice(sorted(SCOPES))]
    method = method or sc.methods[rng.randrange(len(sc.methods))]
    if method not in sc.draw:
        raise ItemError(f"{sc.key} is not worded for a {method} sample")
    frame = dict(frame) if frame else dict(sc.frame)
    if set(frame) != {d.name for d in sc.dims}:
        raise ItemError("a frame names one value for every dimension")

    lo, hi = sc.nrange
    n = int(n) if n is not None else (rng.randrange(lo, hi + 1, sc.nstep) if hi else 0)
    extra = {}
    if "years" in sc.extra:
        y0, y1 = sc.extra["years"]
        extra["years"] = int(years) if years is not None else rng.randint(y0, y1)
    if "share" in sc.extra:
        s0, s1 = sc.extra["share"]
        k = int(k) if k is not None else n * rng.randint(s0, s1) // 10
        if not 0 < k < n:
            raise ItemError("the reported count has to be part of the sample")
        extra["k"] = k

    stem = (sc.draw[method].format(n=n,
                                   pop=unit_phrase(sc, plainest(sc, frame)).format(**extra),
                                   frm=sc.dim("place").values[frame["place"]].stem,
                                   **extra)
            + " " + sc.ask)
    return _build(sc, rng, seed, "esc.generalize", tier, n, method, frame, wrongs,
                  extra, stem)


def generalize_table(rng: random.Random, seed: int, *, ctx=None, n=None, cut=None,
                     cut2=None, lo=None, mid=None, hi=None, counts=None,
                     wrongs=None, tier="hard") -> Item:
    """The same question with a two-way table reporting part of the sample."""
    sc = TABLES[ctx] if ctx is not None else TABLES[rng.choice(sorted(TABLES))]
    e = sc.extra
    cut = int(cut) if cut is not None else rng.randint(*e["cut"])
    cut2 = int(cut2) if cut2 is not None else cut + rng.randint(2, 3)
    lo = int(lo) if lo is not None else rng.randint(*e["band"])
    mid = int(mid) if mid is not None else lo + rng.randint(4, 8)
    hi = int(hi) if hi is not None else mid + 1
    if not cut < cut2 or not lo < mid < hi:
        raise ItemError("the table's bands must not overlap")

    if counts is None:
        a = rng.randrange(4, 12)
        b = rng.randrange(2, 8)
        c = rng.randrange(2, 8)
        d = rng.randrange(14, 34, 2)
        counts = (a, b, c, d)
    a, b, c, d = (int(v) for v in counts)
    m = a + b + c + d
    lo_n, hi_n = sc.nrange
    n = int(n) if n is not None else rng.randrange(max(lo_n, m + 5), hi_n + 1, sc.nstep)
    if n <= m:
        raise ItemError("the table reports a part of the sample, so it is smaller")
    if a + b <= 0 or c + d <= 0:
        raise ItemError("an empty row in the table")

    extra = dict(cut=cut, cut2=cut2, lo=lo, mid=mid, hi=hi, m=m)
    frame = dict(sc.frame)
    stem = (sc.draw["random"].format(n=n, frm=sc.dim("place").values[frame["place"]].stem,
                                     pop=unit_phrase(sc, plainest(sc, frame)).format(**extra),
                                     **extra)
            + " " + sc.ask)
    col1, col2 = (s.format(**extra) for s in e["cols"])
    row1, row2 = (s.format(**extra) for s in e["rows"])
    table = [[e["rowhead"], col1, col2, "Total"],
             [row1, str(a), str(b), str(a + b)],
             [row2, str(c), str(d), str(c + d)],
             ["Total", str(a + c), str(b + d), str(m)]]
    return _build(sc, rng, seed, "esc.generalize_table", tier, n, "random", frame,
                  wrongs, extra, stem, table=table)
