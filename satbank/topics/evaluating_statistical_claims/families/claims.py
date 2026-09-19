"""What a single sample does and does not establish.

Two rules, and every statement in this file is decided by one of them:

* **a sample does not fix a population value.** 87% of a random sample is an
  estimate. It is not the town's percentage, it is not what the next sample
  would report, and it is certainly not what a different town would report.
* **a claim about the sampled group itself is just arithmetic**, and is true
  exactly when the arithmetic is.

`must_be_true` prints two or three numbered statements and asks which hold;
`inference` prints four claims and asks which one the frame and the majority
support. In both, the statement's *kind* decides its truth, the printed
numbers decide the rest, and no code here is told which option is keyed.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text

__all__ = ["must_be_true", "inference", "SURVEYS", "INFER"]

ROMAN = ("I", "II", "III")


# ------------------------------------------------------------ the statements
#
# Each kind renders one numbered statement and carries, in a teacher's words,
# the mistake a student makes by counting it in and the one they make by
# leaving it out. The truth of a kind is never written here: it is decided,
# from the printed sentence and the printed study, by `_holds` below.

def _pct(sv: dict, p) -> str:
    return f"{p}{sv['pc']}"


def _claim(sv: dict) -> str:
    """"would say they are satisfied ..." or "are satisfied ..."."""
    return f"would say they {sv['hold']}" if sv["mood"] == "say" else sv["hold"]


KINDS: dict[str, dict] = {
    "population_exact": dict(
        text=lambda sv, d: f"Of all {sv['pop']}, {_pct(sv, d['p'])} {_claim(sv)}.",
        if_in="read the sample's percentage as the whole population's, although one "
              "sample only estimates it",
        if_out="left out a statement that is in fact true of the population"),
    "repeat_exact": dict(
        text=lambda sv, d: (
            f"If another random sample of {d['n']:,} {sv['unit']} were surveyed, "
            f"{_pct(sv, d['p'])} would {sv['hold_short']}."
            if sv["repeat"] == "short" else
            f"If another {d['n']:,} {sv['unit']} selected at random from {sv['place']} "
            f"were surveyed, {_pct(sv, d['p'])} of them would report they "
            f"{sv['hold']}."),
        if_in="expected a second random sample to repeat the first sample's "
              "percentage exactly",
        if_out="left out a statement that is in fact true of a second sample"),
    "other_population": dict(
        text=lambda sv, d: (
            f"If {d['n']:,} {sv['unit']} selected at random from {sv['other']} were "
            f"surveyed, {_pct(sv, d['p'])} of them would report they {sv['hold']}."),
        if_in="carried the result across to a population that was never sampled",
        if_out="left out a statement that is in fact true of another population"),
    "sample_report": dict(
        text=lambda sv, d: (f"Of the {d['n']:,} {sv['unit']} surveyed, "
                            f"{_pct(sv, d['p'])} {sv['said']}."),
        if_in="counted in a statement that only restates what the sample reported",
        if_out="overlooked that the statement only restates what the sample itself "
               "reported, which cannot fail to be true"),
    "count_sample": dict(
        text=lambda sv, d: (f"Of the {d['n']:,} {sv['unit']} surveyed, {d['count']:,} "
                            f"{sv['said']}."),
        if_in="did not check the printed count against the percentage the survey "
              "reported",
        if_out="overlooked that the count is exactly the reported percentage of the "
               "sample"),
    "majority_sample": dict(
        text=lambda sv, d: (f"More than half of the {d['n']:,} {sv['unit']} surveyed "
                            f"{sv['said']}."),
        if_in="read a minority of those surveyed as a majority",
        if_out="overlooked that more than half of those surveyed gave that response"),
}


def _holds(kind: str, d: dict) -> bool:
    """Is this statement true of the study the stem describes?

    Nothing about which option is keyed is decided here: this is the statistics
    of a single sample, one line per rule.
    """
    if kind in ("population_exact", "repeat_exact", "other_population"):
        return False                    # one sample estimates; it does not fix
    if kind == "sample_report":
        return True                     # it restates the data
    if kind == "count_sample":
        return Q(d["count"]) == Q(d["p"], 100) * d["n"]
    if kind == "majority_sample":
        return Q(d["p"]) > 50
    raise ItemError(f"no rule for the statement kind {kind!r}")


def _label(sub: tuple, total: int) -> str:
    names = [ROMAN[i] for i in sub]
    if not names:
        return "Neither" if total == 2 else "None"
    if total == 2:
        return "I and II" if len(names) == 2 else f"{names[0]} only"
    if len(names) == 1:
        return f"{names[0]} only"
    if len(names) == 2:
        return f"{names[0]} and {names[1]} only"
    return "I, II, and III"


def _subsets(total: int) -> list[tuple]:
    out = [()]
    for i in range(total):
        out += [s + (i,) for s in out]
    return sorted(set(out), key=lambda s: (len(s), s))


# ------------------------------------------------------------- the contexts

SURVEYS: dict[str, dict] = {
    "concession": dict(
        unit="residents", pop="the town residents", place="the town",
        other="a different town", pc="%", mood="say", repeat="short",
        hold="are satisfied with the concession stand at the local park",
        hold_short="say they are satisfied",
        said="said they are satisfied",
        draw="Residents of a town were surveyed to determine whether they are "
             "satisfied with the concession stand at the local park. A random sample "
             "of {n} residents was selected. All {n} responded, and {p}% said they "
             "are satisfied.",
        ask="Based on this information, which of the following statements must be "
            "true?",
        nrange=(100, 400), nstep=50),
    "air_quality": dict(
        unit="adults", pop="adults in the city", place="the city",
        other="a different city", pc=" percent", mood="plain", repeat="long",
        hold="are satisfied with the quality of air in the city",
        hold_short="report they are satisfied",
        said="responded that they were satisfied",
        draw="A polling agency recently surveyed {n} adults who were selected at "
             "random from a large city and asked each of the adults, “Are you "
             "satisfied with the quality of air in the city?” Of those surveyed, "
             "{p} percent responded that they were satisfied with the quality of air "
             "in the city.",
        ask="Based on the results of the survey, which of the following statements "
            "must be true?",
        nrange=(500, 2_000), nstep=500),
    "recycling": dict(
        unit="households", pop="the households in the district", place="the district",
        other="a different district", pc="%", mood="say", repeat="short",
        hold="are willing to sort their recycling",
        hold_short="say they are willing", said="said they are willing",
        draw="Households in a district were surveyed to determine whether they are "
             "willing to sort their recycling. A random sample of {n} households was "
             "selected. All {n} responded, and {p}% said they are willing.",
        ask="Based on this information, which of the following statements must be "
            "true?",
        nrange=(100, 500), nstep=50),
    "commute": dict(
        unit="commuters", pop="the commuters in the city", place="the city",
        other="a different city", pc=" percent", mood="plain", repeat="long",
        hold="travel to work by train",
        hold_short="report they travel by train", said="reported that they travel by "
                                                       "train",
        draw="A transit authority surveyed {n} commuters who were selected at random "
             "from a large city and asked each of the commuters how they travel to "
             "work. Of those surveyed, {p} percent reported that they travel to work "
             "by train.",
        ask="Based on the results of the survey, which of the following statements "
            "must be true?",
        nrange=(400, 1_600), nstep=200),
    "library_hours": dict(
        unit="members", pop="the members of the library", place="the library",
        other="a different library", pc="%", mood="say", repeat="short",
        hold="are in favor of the longer opening hours",
        hold_short="say they are in favor", said="said they are in favor",
        draw="Members of a library were surveyed to determine whether they are in "
             "favor of the longer opening hours. A random sample of {n} members was "
             "selected. All {n} responded, and {p}% said they are in favor.",
        ask="Based on this information, which of the following statements must be "
            "true?",
        nrange=(100, 600), nstep=50),
    "fitness": dict(
        unit="members", pop="the members of the gym", place="the gym",
        other="a different gym", pc=" percent", mood="plain", repeat="long",
        hold="use the gym at least twice a week",
        hold_short="report they use the gym at least twice a week",
        said="reported that they use the gym at least twice a week",
        draw="A gym surveyed {n} members who were selected at random from all of its "
             "members and asked each of the members how often they use the gym. Of "
             "those surveyed, {p} percent reported that they use the gym at least "
             "twice a week.",
        ask="Based on the results of the survey, which of the following statements "
            "must be true?",
        nrange=(200, 800), nstep=100),
}

# Statements that can be false and statements that can be true, so that a free
# draw's answer is not fixed by the shape of the item.
FALSE_KINDS = ("population_exact", "repeat_exact", "other_population")
LIVE_KINDS = ("sample_report", "count_sample", "majority_sample")


def must_be_true(rng: random.Random, seed: int, *, ctx=None, n=None, p=None,
                 stmts=None, wrongs=None, numbering="roman", count_off=0,
                 tier="medium") -> Item:
    """Two or three numbered statements; which of them the survey establishes."""
    sv = SURVEYS[ctx] if ctx is not None else SURVEYS[rng.choice(sorted(SURVEYS))]
    lo, hi = sv["nrange"]
    n = int(n) if n is not None else rng.randrange(lo, hi + 1, sv["nstep"])
    p = int(p) if p is not None else rng.randrange(12, 95)
    if stmts is None:
        total = rng.choice((2, 2, 3))
        pool = list(FALSE_KINDS) + list(LIVE_KINDS)
        rng.shuffle(pool)
        stmts = pool[:total]
        if total == 3 and not any(k in LIVE_KINDS for k in stmts):
            # `check._prose` reads a bare "None" as an unrendered placeholder, so a
            # free three-statement draw never lands on the empty answer. The source
            # item that does print "None" reaches it through `stmts=`.
            stmts[rng.randrange(3)] = LIVE_KINDS[rng.randrange(len(LIVE_KINDS))]
    stmts = list(stmts)
    total = len(stmts)
    if total not in (2, 3) or len(set(stmts)) != total:
        raise ItemError("two or three different statements")
    if Q(p, 100) * n != int(Q(p, 100) * n) and "count_sample" in stmts:
        raise ItemError("the reported percentage is not a whole number of people")

    d = dict(n=n, p=p, count=int(Q(p, 100) * n) + int(count_off))
    lines = [KINDS[k]["text"](sv, d) for k in stmts]
    truth = tuple(i for i, k in enumerate(stmts) if _holds(k, d))

    mark = ROMAN if numbering == "roman" else ("1", "2", "3")
    stem = (sv["draw"].format(n=f"{n:,}", p=p) + " " + sv["ask"] + "\n"
            + "\n".join(f"{mark[i]}. {t}" for i, t in enumerate(lines)))

    if total == 3 and not truth and wrongs is None:
        # `check._prose` reads a bare "None" as an unrendered placeholder, so a free
        # three-statement draw may not land on the empty answer. The official item
        # that does print "None" reaches it by naming its own three wrong sets.
        raise ItemError("a free three-statement draw cannot print None as the key")

    subsets = [s for s in _subsets(total) if s != truth]
    if wrongs is None:
        if total == 2:
            picked = subsets                      # the complete set, as the SAT prints
        else:
            # the empty subset prints as "None", which `check._prose`
            # reads as an unrendered placeholder
            allowed = [s for s in subsets if s]
            rng.shuffle(allowed)
            picked = allowed[:3]
    else:
        picked = [tuple(sorted(ROMAN.index(r) for r in w.split()))
                  if w else () for w in wrongs]
        if any(s == truth for s in picked):
            raise ItemError("a named wrong answer is the set the survey establishes")
    if len(picked) != 3:
        raise ItemError("need exactly three wrong option sets")

    wrong = []
    for s in picked:
        i = next(i for i in range(total) if (i in s) != (i in truth))
        side = "if_in" if i in s else "if_out"
        wrong.append(Mis(KINDS[stmts[i]][side], _label(s, total)))
    choices, reasons, letter = assemble_text(_label(truth, total), wrong, rng)

    why = ("A single sample estimates the population but does not fix it, so "
           + ("no statement" if not truth else
              "only " + " and ".join(mark[i] for i in truth))
           + " must be true.")
    P = dict(kind="esc.must_be_true", survey=sv["pop"], n=n, p=p, count=d["count"],
             stmts=list(stmts), lines=lines, texts=list(choices), total=total)
    return Item("esc.must_be_true", "evaluating a statistical claim", tier, seed,
                stem, "mcq", E(0), letter, why, choices, reasons, list(choices),
                params=P)


# ------------------------------------------------------- the licensed inference

INFER: dict[str, dict] = {
    "book_movie": dict(
        unit="people", frame="people who like this book",
        others=("people who go see movies", "people who read books",
                "people who dislike this book"),
        draw="A market researcher selected {n} people at random from a group of "
             "people who indicated that they liked a certain book. The {n} people "
             "were shown a movie based on the book and then asked whether they liked "
             "or disliked the movie. Of those surveyed, {p}% said they {said}.",
        ask="Which of the following inferences can appropriately be drawn from this "
            "survey result?",
        verb=("dislike this movie", "like this movie"),
        said=("disliked the movie", "liked the movie"),
        nrange=(100, 400), nstep=50),
    "season_ticket": dict(
        unit="fans", frame="fans who hold a season ticket",
        others=("fans who watch the game on television", "people who follow the sport",
                "fans who do not hold a season ticket"),
        draw="A club selected {n} fans at random from a list of the fans who hold a "
             "season ticket. The {n} fans were shown the design for a new stadium and "
             "then asked whether they approved or disapproved of it. Of those "
             "surveyed, {p}% said they {said}.",
        ask="Which of the following inferences can appropriately be drawn from this "
            "survey result?",
        verb=("approve of the design", "disapprove of the design"),
        said=("approved of the design", "disapproved of the design"),
        nrange=(100, 500), nstep=50),
    "app_users": dict(
        unit="users", frame="users who paid for the app",
        others=("people who own a phone", "users who downloaded the free app",
                "users who deleted the app"),
        draw="A developer selected {n} users at random from the users who paid for a "
             "certain app. The {n} users were shown the new version of the app and "
             "then asked whether they found it easier or harder to use. Of those "
             "surveyed, {p}% said they {said}.",
        ask="Which of the following inferences can appropriately be drawn from this "
            "survey result?",
        verb=("find the new version easier to use",
              "find the new version harder to use"),
        said=("found it easier to use", "found it harder to use"),
        nrange=(150, 600), nstep=50),
    "allotment": dict(
        unit="gardeners", frame="gardeners who rent an allotment",
        others=("people who buy vegetables", "gardeners who grow flowers",
                "gardeners who gave up an allotment"),
        draw="A council selected {n} gardeners at random from the gardeners who rent "
             "an allotment. The {n} gardeners were shown a plan for a new water "
             "supply and then asked whether they supported or opposed it. Of those "
             "surveyed, {p}% said they {said}.",
        ask="Which of the following inferences can appropriately be drawn from this "
            "survey result?",
        verb=("support the plan", "oppose the plan"),
        said=("supported the plan", "opposed the plan"),
        nrange=(80, 300), nstep=20),
    "night_class": dict(
        unit="students", frame="students who take an evening class",
        others=("students at the college", "people who work during the day",
                "students who take a daytime class"),
        draw="A college selected {n} students at random from the students who take an "
             "evening class. The {n} students were shown a proposed timetable and "
             "then asked whether they preferred it to the current one. Of those "
             "surveyed, {p}% said they {said}.",
        ask="Which of the following inferences can appropriately be drawn from this "
            "survey result?",
        verb=("prefer the proposed timetable", "prefer the current timetable"),
        said=("preferred the proposed timetable", "preferred the current timetable"),
        nrange=(100, 400), nstep=50),
}

# "Most" is the only quantifier a sample supports: a percentage read off one
# sample is an estimate, so no option that repeats it exactly can be drawn.
QUANT = {"most": "Most {pop} will {verb}.",
         "at_least": "At least {p}% of {pop} will {verb}.",
         "all": "All {pop} will {verb}."}


def inference(rng: random.Random, seed: int, *, ctx=None, n=None, p=None, said=None,
              wrongs=None, tier="easy") -> Item:
    """Which inference the sampling frame and the reported majority support."""
    d = INFER[ctx] if ctx is not None else INFER[rng.choice(sorted(INFER))]
    lo, hi = d["nrange"]
    n = int(n) if n is not None else rng.randrange(lo, hi + 1, d["nstep"])
    p = int(p) if p is not None else rng.choice([20, 25, 30, 35, 65, 70, 75, 80,
                                                 85, 90, 92, 95])
    # which of the two responses the stem reports; the majority, and so the
    # direction of the licensed claim, follows from it together with p
    said = rng.randrange(2) if said is None else int(said)
    if not (p <= 35 or p >= 65):
        raise ItemError("a percentage this close to half supports no 'most' claim")

    reported = d["verb"][said]                   # what {p}% of the sample said
    other = d["verb"][1 - said]
    # the majority of the sample, which is the only direction a claim may take,
    # and the share that majority holds
    major, minor = (reported, other) if p > 50 else (other, reported)
    pm = p if p > 50 else 100 - p

    stem = (d["draw"].format(n=n, p=p, said=d["said"][said]) + " " + d["ask"])
    key = QUANT["most"].format(pop=d["frame"], verb=major, p=p)

    pool = {
        "wide_strong": Mis(
            "generalized past the sampling frame, and repeated the sample's "
            "percentage as if it held exactly",
            QUANT["at_least"].format(pop=d["others"][0], verb=major, p=pm)),
        "read_strong": Mis(
            "generalized to a population the sample was never drawn from",
            QUANT["at_least"].format(pop=d["others"][1], verb=major, p=pm)),
        "opposite_group": Mis(
            "swapped the group the sample came from for its complement, and the "
            "response with it",
            QUANT["most"].format(pop=d["others"][2], verb=minor, p=pm)),
        "frame_strong": Mis(
            "kept to the sampling frame but read the sample's percentage as the "
            "population's",
            QUANT["at_least"].format(pop=d["frame"], verb=major, p=pm)),
        "frame_flip": Mis(
            "read the minority response of the sample as its majority response",
            QUANT["most"].format(pop=d["frame"], verb=minor, p=pm)),
        "frame_all": Mis(
            "read a majority of the sample as every member of the population",
            QUANT["all"].format(pop=d["frame"], verb=major, p=pm)),
    }
    names = list(pool) if wrongs is None else list(wrongs)
    if wrongs is None:
        rng.shuffle(names)
    wrong = [pool[w] for w in names[:3]]
    if len(wrong) != 3:
        raise ItemError("need three wrong inferences")
    choices, reasons, letter = assemble_text(key, wrong, rng)

    why = (f"The {d['unit']} were selected at random from {d['frame']}, so only a "
           f"claim about that group is licensed; {pm}% of one sample estimates the "
           f"population rather than fixing it, so only “most” is "
           f"supported.")
    P = dict(kind="esc.inference", ctx=[k for k, v in INFER.items() if v is d][0],
             n=n, p=p, said=said, frame=d["frame"], verbs=list(d["verb"]),
             texts=list(choices))
    return Item("esc.inference", "evaluating a statistical claim", tier, seed, stem,
                "mcq", E(0), letter, why, choices, reasons, list(choices), params=P)
