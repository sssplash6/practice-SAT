"""Items whose options are sentences about an estimate and its margin of error.

The shape of every generator here is the same, and it is the point of the
topic:

    1. build the **study** the stem describes -- how the units were chosen,
       how many, what was estimated, with what margin, and whether the stem
       states the size of the population;
    2. render the stem from that study;
    3. render four **claims** into four sentences;
    4. ask `study.supported` which of the four the study supports, and refuse
       the draw unless exactly one does.

Step 4 is the key. Nothing here, and nothing in `sources.py`, says which
option is correct. A source item names the four sentences College Board
printed -- the same information the transcript holds -- and the engine works
out which of them the study licenses. Give it four sentences none of which
the study supports and it refuses; give it two and it refuses. Take the
margin out of the study and the interval sentences stop being licensed; take
the randomness out and nothing about the population is licensed at all, so
the answer becomes "no conclusion can be made".
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text
from ..claims import catalogue
from ..study import Study, supported
from ..values import Q as _Q
from ..values import dec, q, tidy, unambiguous
from ..world import MEAN_SCENES, PCT_SCENES, SCENES

__all__ = ["interpret_mean", "interpret_percent", "interpret_table",
           "subgroup_claim", "count_claim"]


# --------------------------------------------------------------- the shared part

def _pick_specs(sc, st, rng, pool: list[str]) -> list[str]:
    """Four sentences with exactly one the study supports.

    The split is made by evaluating every sentence the scene can print, not
    by knowing which one is the answer: whatever `supported` says is in the
    first list is a candidate key, and the other three come from the second.
    """
    good, bad = [], []
    for spec in pool:
        try:
            p = catalogue(sc, st, [spec])[0]
        except ItemError:
            continue
        (good if supported(st, p.claim) else bad).append(spec)
    if not good or len(bad) < 3:
        raise ItemError("this study cannot fill a page with one supported claim")
    rng.shuffle(good)
    rng.shuffle(bad)
    return [good[0]] + bad[:3]


def _assemble(sc, st, rng, specs, template, tier, seed, stem, table=None,
              extra_params=None) -> Item:
    printed = catalogue(sc, st, specs)
    good = [p for p in printed if supported(st, p.claim)]
    if len(good) != 1:
        raise ItemError(
            f"{len(good)} of the four printed statements are supported by this "
            f"study; an item has exactly one defensible answer "
            f"({[p.name for p in good]})")
    key = good[0]
    wrong = [Mis(_wrong_why(sc, st, p), p.text) for p in printed if p is not key]
    choices, reasons, letter = assemble_text(key.text, wrong, rng)
    if len(set(choices)) != 4:
        raise ItemError("two options print as the same sentence")

    P = dict(kind=template, scene=sc.key, quantity=sc.quantity,
             estimate=str(q(st.estimate)),
             margin=None if st.margin is None else str(q(st.margin)),
             n=st.n, random=st.random, size=st.size,
             texts=list(choices), extra=dict(sc.extra.get("audit", {})))
    if extra_params:
        P.update(extra_params)
    return Item(template, "sample statistics and margin of error", tier, seed,
                stem, "mcq", E(0), letter, _why(sc, st), choices, reasons,
                list(choices), table=table, params=P)


def _wrong_why(sc, st, p) -> str:
    """The mistake a distractor is made of, said in the draw's own terms.

    A claim's own reason is written for the ordinary page, where the sample
    was selected at random and the mistake is in the reading of the margin.
    When the sample selected itself, every statement about the population is
    wrong for one reason instead, and saying "took the bottom of the
    interval" there would name a mistake the student did not make.
    """
    if st.random:
        return p.why
    if p.claim.kind == "no_conclusion":
        return p.why
    return (f"generalized to {sc.pop_all} from a sample that selected itself, "
            f"which speaks for nobody but the units in it")


def _why(sc, st) -> str:
    if not st.random:
        return (f"The {sc.members} were not selected at random, so the study "
                f"estimates nothing about {sc.pop_all}.")
    if st.margin is None:
        return (f"A sample estimates the population it was drawn from, so the "
                f"study supports an approximate statement about {sc.pop_all} "
                f"and nothing about any wider group.")
    return (f"The margin of error gives an interval of plausible values for "
            f"{sc.subject_lc}: from {sc.one(st.lo)} to {sc.one(st.hi)}. It is a "
            f"statement about that value, it does not make it certain, and it "
            f"says nothing about any one {sc.member}.")


def _study_and_stem(sc, n, est, moe, self_selected: bool, size=None):
    st = Study(sc.quantity, q(est), None if moe is None else q(moe), n=int(n),
               random=not self_selected, size=size)
    draw = sc.extra["draw_self"] if self_selected else sc.draw
    # the SAT spells a unit out where it first appears and abbreviates it
    # afterwards: "27.8 ounces (oz), with an associated margin of error of
    # 0.02 oz", and then "27.78 oz" in the options
    first = sc.extra.get("first_use")
    shown = (f"{sc.num(st.estimate)} {first}" if first else sc.one(st.estimate))
    parts = [draw.format(n=f"{int(n):,}", est=shown,
                         moe=sc.one(st.margin) if st.margin is not None else "")]
    if sc.report:
        parts.append(sc.report.format(n=f"{int(n):,}", est=shown,
                                      moe=sc.one(st.margin)))
    parts.append(sc.ask)
    return st, tidy(" ".join(parts))


def _pool(sc, st) -> list[str]:
    """Every sentence this scene can print about this study."""
    names = ["interval", "point", "point_exact", "point_upper", "point_lower",
             "greater_est", "less_est", "outside", "more_than_upper",
             "less_than_lower", "not_possible_below", "not_possible_above",
             "plausible_below", "plausible_above", "count_from_sample",
             "individuals", "individuals_sample", "all_individuals",
             "most_exactly"]
    out = [n for n in names]
    if st.margin is not None:
        step = q(st.margin)
        out.append(f"doubtful:{dec(st.hi + step, 4, group=False)}")
        out.append(f"doubtful:{dec(st.estimate, 4, group=False)}")
        out.append(f"none_below:{dec(st.lo - step, 4, group=False)}")
    if "no_conc" in sc.extra:
        out += ["no_conclusion_a", "no_conclusion_b"]
    if not st.random and "no_conc_self" in sc.extra:
        out.append("no_conclusion_self")
    return out


def _draw_numbers(sc, rng, n, est, moe):
    lo, hi = sc.nrange
    if n is None:
        n = rng.randrange(lo, hi + 1, sc.nstep) if hi else 0
    if est is None:
        e0, e1 = sc.erange
        k = rng.randint(0, int((q(e1) - q(e0)) / sc.estep))
        est = q(e0) + k * sc.estep
    if moe is None:
        m0, m1 = sc.mrange
        k = rng.randint(0, int((q(m1) - q(m0)) / sc.mstep))
        moe = q(m0) + k * sc.mstep
    return int(n), q(est), q(moe)


def _interpret(rng, seed, scenes, template, ctx, n, est, moe, options, tier,
               self_selected=None):
    sc = scenes[ctx] if ctx is not None else scenes[rng.choice(sorted(scenes))]
    if self_selected is None:
        # a free draw sometimes describes a sample that selected itself. That
        # branch has to be *reachable*: a rule about what an unrandomised
        # sample supports which no draw can ever run is a rule nobody has
        # tested, and this topic's sibling was rejected twice for exactly
        # that. One draw in four, where the scene has the wording.
        self_selected = "draw_self" in sc.extra and rng.randrange(4) == 0
    if self_selected and "draw_self" not in sc.extra:
        raise ItemError(f"scene {sc.key!r} has no self-selected wording")
    n, est, moe = _draw_numbers(sc, rng, n, est, moe)
    if moe <= 0 or est - moe <= 0:
        raise ItemError("the interval has to sit above zero")
    if sc.quantity == "percent" and est + moe >= 100:
        raise ItemError("a percent interval has to stay under 100%")
    if sc.quantity == "proportion" and est + moe >= 1:
        raise ItemError("a proportion interval has to stay under 1")
    st, stem = _study_and_stem(sc, n, est, moe, self_selected)
    specs = options if options is not None else _pick_specs(sc, st, rng, _pool(sc, st))
    if len(specs) != 4:
        raise ItemError("an item prints four options")
    return _assemble(sc, st, rng, specs, template, tier, seed, stem)


# ------------------------------------------------------------------ the family

def interpret_mean(rng: random.Random, seed: int, *, ctx=None, n=None, est=None,
                   moe=None, options=None, tier="easy") -> Item:
    """An estimated mean with a margin of error, and four readings of it."""
    return _interpret(rng, seed, MEAN_SCENES, "sstat.interpret_mean", ctx, n, est,
                      moe, options, tier)


def interpret_percent(rng: random.Random, seed: int, *, ctx=None, n=None, est=None,
                      moe=None, options=None, tier="medium",
                      self_selected=None) -> Item:
    """An estimated percent or proportion with a margin of error."""
    return _interpret(rng, seed, PCT_SCENES, "sstat.interpret_percent", ctx, n,
                      est, moe, options, tier, self_selected)


# ------------------------------------------------- the estimate read off a table

def interpret_table(rng: random.Random, seed: int, *, ctx=None, counts=None,
                    moe=None, options=None, tier="hard") -> Item:
    """The same question, with the estimate read off a two-way table.

    The estimate is not a parameter here: it is computed from the table the
    page prints, so a table that does not add up cannot produce the stem's
    own number. The table's margins are computed too, never passed in.
    """
    from ..world import TABLE_SCENES
    sc = TABLE_SCENES[ctx] if ctx is not None else \
        TABLE_SCENES[rng.choice(sorted(TABLE_SCENES))]
    rows = sc.extra["rows"]
    if counts is None:
        counts = [[rng.randrange(60, 200) for _ in sc.extra["cols"]] for _ in rows]
    counts = [[int(c) for c in row] for row in counts]
    if len(counts) != len(rows) or any(len(r) != len(sc.extra["cols"]) for r in counts):
        raise ItemError("the table's shape does not match the scene")
    rtot = [sum(r) for r in counts]
    ctot = [sum(counts[i][j] for i in range(len(counts)))
            for j in range(len(counts[0]))]
    n = sum(rtot)
    hit = rtot[sc.extra["focus"]]
    if not 0 < hit < n:
        raise ItemError("the focus row has to be a proper part of the sample")
    # the whole percent the study would report, refused when the true value
    # sits exactly between two whole percents
    est = unambiguous(_Q(100 * hit, n), 1)
    if moe is None:
        m0, m1 = sc.mrange
        k = rng.randint(0, int((q(m1) - q(m0)) / sc.mstep))
        moe = q(m0) + k * sc.mstep
    moe = q(moe)
    if moe <= 0 or est - moe <= 0 or est + moe >= 100:
        raise ItemError("the interval has to sit inside 0% and 100%")

    table = [[sc.extra["corner"]] + list(sc.extra["cols"]) + ["Total"]]
    for name, row, tot in zip(rows, counts, rtot):
        table.append([name] + [f"{c:,}" for c in row] + [f"{tot:,}"])
    table.append(["Total"] + [f"{c:,}" for c in ctot] + [f"{n:,}"])

    st = Study(sc.quantity, est, moe, n=n, random=True)
    stem = tidy(" ".join([sc.draw.format(n=f"{n:,}"),
                          sc.report.format(est=sc.one(est), moe=sc.one(moe)),
                          sc.ask]))
    specs = options if options is not None else _pick_specs(sc, st, rng, _pool(sc, st))
    return _assemble(sc, st, rng, specs, "sstat.interpret_table", tier, seed, stem,
                     table=table,
                     extra_params=dict(counts=counts, focus=sc.extra["focus"]))


# ---------------------------------------- a statistic measured on a subgroup

def subgroup_claim(rng: random.Random, seed: int, *, ctx=None, n=None, est=None,
                   options=None, tier="medium") -> Item:
    """A percent measured on one kind of unit inside the sample.

    No margin of error is stated, so the study supports an *approximate*
    statement and nothing exact -- and it supports it about the group the
    units belong to, not about the wider population the stem also names.
    """
    from ..world import SUBGROUP_SCENES
    sc = SUBGROUP_SCENES[ctx] if ctx is not None else \
        SUBGROUP_SCENES[rng.choice(sorted(SUBGROUP_SCENES))]
    n, est, _ = _draw_numbers(sc, rng, n, est, 1)
    if not 0 < est < 100:
        raise ItemError("a percent of the subgroup, strictly between 0 and 100")
    if (n * est) % 100:
        raise ItemError("the reported percent has to be a whole number of units")
    st = Study(sc.quantity, est, None, n=n, random=True)
    stem = tidy(" ".join([sc.draw.format(n=f"{n:,}"),
                          sc.report.format(n=f"{n:,}", est=sc.one(est)),
                          sc.ask]))
    pool = ["approx_frame", "approx_wider", "point_exact", "point",
            "greater_est", "less_est"]
    if "wider_claims" in sc.extra:
        pool += ["wider_majority", "wider_mean"]
    specs = options if options is not None else _pick_specs(sc, st, rng, pool)
    return _assemble(sc, st, rng, specs, "sstat.subgroup_claim", tier, seed, stem)


# ------------------------------------------- an estimated count, exact or not

def count_claim(rng: random.Random, seed: int, *, ctx=None, n=None, k=None,
                size=None, options=None, tier="medium") -> Item:
    """Whether a scaled-up count is a certainty or an estimate.

    Two axes, and the study decides both: the count the sample scales up to,
    and whether the study can insist on it. With no margin of error the study
    reports the count only approximately, so a sentence saying the count
    *must* be that number asks for a certainty it has not got.
    """
    from ..world import COUNT_SCENES
    sc = COUNT_SCENES[ctx] if ctx is not None else \
        COUNT_SCENES[rng.choice(sorted(COUNT_SCENES))]
    lo, hi = sc.nrange
    n = int(n) if n is not None else rng.randrange(lo, hi + 1, sc.nstep)
    k = int(k) if k is not None else rng.randrange(max(2, n // 8), n * 3 // 4)
    s0, s1 = sc.extra["size"]
    size = int(size) if size is not None else rng.randrange(s0, s1 + 1, sc.extra["sstep"])
    if not 0 < k < n or size <= n:
        raise ItemError("the sample is a proper part of the population")
    st = Study("proportion", _Q(k, n), None, n=n, random=True, size=size)
    stem = tidy(" ".join([sc.draw.format(n=f"{n:,}", k=f"{k:,}"),
                          sc.ask.format(size=f"{size:,}")]))
    right = _Q(size * k, n)
    if right.denominator != 1:
        raise ItemError("the scaled-up count has to be a whole number of units")
    other = _Q(size, k)
    if other.denominator != 1 or other == right:
        raise ItemError("the divided-instead-of-multiplied slip is not a whole number")
    from ..count_claims import count_specs
    specs, printed = count_specs(sc, st, right, other, options)
    good = [p for p in printed if supported(st, p.claim)]
    if len(good) != 1:
        raise ItemError(f"{len(good)} of the printed statements are supported")
    key = good[0]
    wrong = [Mis(p.why, p.text) for p in printed if p is not key]
    choices, reasons, letter = assemble_text(key.text, wrong, rng)
    P = dict(kind="sstat.count_claim", scene=sc.key, quantity="proportion",
             estimate=str(_Q(k, n)), margin=None, n=n, random=True, size=size,
             k=k, texts=list(choices), specs=list(specs))
    why = (f"The sample is {k:,} of {n:,}, so the best estimate for the "
           f"population of {size:,} is {int(right):,}. One sample estimates that "
           f"count; it cannot make it certain.")
    return Item("sstat.count_claim", "sample statistics and margin of error", tier,
                seed, stem, "mcq", E(0), letter, why, choices, reasons,
                list(choices), params=P)
