"""Association or cause, and for whom.

Two rules, and they are independent of each other:

* **random selection earns a population.** The conclusion reaches the group
  the units were selected from, and no further; when they were not selected at
  random it reaches only the units in the study.
* **random assignment earns a cause.** Without it, a difference between two
  groups is an association and nothing more, however the units were chosen.

The most appropriate conclusion is therefore the strongest one the design
supports, about the largest group it supports it for -- the maximum of the
supported claims under "at least as strong, and at least as wide". A draw
whose printed options have no single maximum is refused.

No official item in this topic asks the question this way. The template is
here because the assignment rule has to be *reachable*: an earlier attempt at
this topic carried assignment logic that no draw could run, which is a rule
nobody can be wrong about and therefore no rule at all.
"""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text

__all__ = ["conclusion", "TRIALS"]

# how far a conclusion may reach: the units in the study, the group they were
# selected from, or wider still
LEVEL = {"sample": 0, "frame": 1, "wider": 2}


def _supported(strength: str, scope: str, selected_at_random: bool,
               assigned_at_random: bool) -> bool:
    """Does the design support this claim?"""
    reach = 1 if selected_at_random else 0
    if LEVEL[scope] > reach:
        return False
    return assigned_at_random if strength == "cause" else True


def _stronger_or_equal(a: tuple, b: tuple) -> bool:
    """Is claim `a` at least as strong as `b`, and at least as wide?"""
    rank = {"association": 0, "cause": 1}
    return rank[a[0]] >= rank[b[0]] and LEVEL[a[1]] >= LEVEL[b[1]]


TEXT = {
    "cause": "The {treatment} causes an increase in {outcome} for {pop}.",
    "association": "There is an association between the {treatment} and an "
                   "increase in {outcome} for {pop}.",
}

TRIALS: dict[str, dict] = {
    "sleep_app": dict(
        unit="members", treatment="sleep app", outcome="nightly sleep",
        frame="the members of the health center",
        wider="all adults in the city", sample="the {n} members in the study",
        draw={("random", True):
              "A researcher selected {n} members at random from the members of a "
              "health center and randomly assigned them to two groups. One group "
              "used a sleep app for {weeks} weeks and the other did not. The group "
              "that used the app slept significantly longer each night.",
              ("random", False):
              "A researcher selected {n} members at random from the members of a "
              "health center and asked each of them whether they use a sleep app. "
              "Over the next {weeks} weeks, the members who use the app slept "
              "significantly longer each night than those who do not.",
              ("volunteer", True):
              "A researcher enrolled {n} members of a health center who volunteered "
              "for a study and randomly assigned them to two groups. One group used "
              "a sleep app for {weeks} weeks and the other did not. The group that "
              "used the app slept significantly longer each night."},
        nrange=(60, 200), nstep=20, weeks=(4, 12)),
    "fertilizer": dict(
        unit="plots", treatment="new fertilizer", outcome="yield",
        frame="the plots on this farm",
        wider="all the plots in the region", sample="the {n} plots in the study",
        draw={("random", True):
              "An agronomist selected {n} plots at random from the plots on a farm "
              "and randomly assigned them to two groups. One group was given a new "
              "fertilizer for {weeks} weeks and the other was given the usual one. "
              "The group given the new fertilizer had a significantly higher yield.",
              ("random", False):
              "An agronomist selected {n} plots at random from the plots on a farm "
              "and recorded which of them the farmer had chosen to treat with a new "
              "fertilizer. Over {weeks} weeks, the plots treated with the new "
              "fertilizer had a significantly higher yield.",
              ("volunteer", True):
              "An agronomist worked with {n} plots on a farm whose owner offered "
              "them for a study and randomly assigned them to two groups. One group "
              "was given a new fertilizer for {weeks} weeks and the other was given "
              "the usual one. The group given the new fertilizer had a significantly "
              "higher yield."},
        nrange=(40, 120), nstep=20, weeks=(6, 16)),
    "tutoring": dict(
        unit="students", treatment="tutoring program", outcome="test scores",
        frame="the students at this college",
        wider="all students in the state", sample="the {n} students in the study",
        draw={("random", True):
              "A college selected {n} students at random from its own students and "
              "randomly assigned them to two groups. One group joined a tutoring "
              "program for {weeks} weeks and the other did not. The group that "
              "joined the program scored significantly higher on the end-of-term "
              "test.",
              ("random", False):
              "A college selected {n} students at random from its own students and "
              "recorded which of them had joined a tutoring program. After {weeks} "
              "weeks, the students who had joined the program scored significantly "
              "higher on the end-of-term test.",
              ("volunteer", True):
              "A college enrolled {n} of its students who volunteered for a study "
              "and randomly assigned them to two groups. One group joined a tutoring "
              "program for {weeks} weeks and the other did not. The group that "
              "joined the program scored significantly higher on the end-of-term "
              "test."},
        nrange=(50, 150), nstep=25, weeks=(6, 14)),
    "standing_desk": dict(
        unit="employees", treatment="standing desk",
        outcome="comfort reported at work",
        frame="the employees of this company",
        wider="all office employees in the country",
        sample="the {n} employees in the study",
        draw={("random", True):
              "A company selected {n} employees at random from its own employees and "
              "randomly assigned them to two groups. One group used a standing desk "
              "for {weeks} weeks and the other used a seated desk. The group that "
              "used the standing desk reported significantly greater comfort at "
              "work.",
              ("random", False):
              "A company selected {n} employees at random from its own employees and "
              "recorded which of them had asked for a standing desk. After {weeks} "
              "weeks, the employees with a standing desk reported significantly "
              "greater comfort at work.",
              ("volunteer", True):
              "A company enrolled {n} of its employees who volunteered for a study "
              "and randomly assigned them to two groups. One group used a standing "
              "desk for {weeks} weeks and the other used a seated desk. The group "
              "that used the standing desk reported significantly greater comfort "
              "at work."},
        nrange=(40, 160), nstep=20, weeks=(8, 20)),
    "seed_light": dict(
        unit="seedlings", treatment="blue lamp", outcome="stem growth",
        frame="the seedlings in this greenhouse",
        wider="all seedlings of this species",
        sample="the {n} seedlings in the study",
        draw={("random", True):
              "A botanist selected {n} seedlings at random from the seedlings in a "
              "greenhouse and randomly assigned them to two groups. One group was "
              "grown under a blue lamp for {weeks} weeks and the other under the "
              "usual lamp. The group grown under the blue lamp put on significantly "
              "more stem growth.",
              ("random", False):
              "A botanist selected {n} seedlings at random from the seedlings in a "
              "greenhouse and recorded which of them a grower had already placed "
              "under a blue lamp. Over {weeks} weeks, the seedlings under the blue "
              "lamp put on significantly more stem growth."},
        nrange=(50, 150), nstep=25, weeks=(3, 9)),
}

ASK = "Which of the following is the most appropriate conclusion from this study?"

# The misconception is worked out from how the claim misses, not looked up by
# name: too strong for the design, too wide for the selection, or both.
AS_ASSIGNED = ("read random selection as random assignment: selecting units at "
               "random earns a population, not a cause")
TOO_NARROW = ("kept the conclusion inside the study although the units were "
              "selected at random from a whole group")
TOO_WEAK = ("settled for an association although the units were randomly "
            "assigned, which is what earns a cause")
BOTH_SMALL = ("under-claimed twice over: random assignment earns a cause, and "
              "random selection earns the group the units came from")


def conclusion(rng: random.Random, seed: int, *, ctx=None, n=None, weeks=None,
               selection=None, assignment=None, wrongs=None, tier="hard") -> Item:
    """Which conclusion the design supports, and for which group."""
    d = TRIALS[ctx] if ctx is not None else TRIALS[rng.choice(sorted(TRIALS))]
    shapes = sorted(d["draw"])
    if selection is None or assignment is None:
        fit = [s for s in shapes if (selection is None or s[0] == selection)
               and (assignment is None or s[1] == assignment)]
        if not fit:
            raise ItemError("no wording for that design")
        selection, assignment = fit[rng.randrange(len(fit))]
    if (selection, assignment) not in d["draw"]:
        raise ItemError(f"no wording for a {selection} sample with assignment "
                        f"{assignment}")
    at_random = selection == "random"
    lo, hi = d["nrange"]
    n = int(n) if n is not None else rng.randrange(lo, hi + 1, d["nstep"])
    w0, w1 = d["weeks"]
    weeks = int(weeks) if weeks is not None else rng.randint(w0, w1)

    claims = {}
    for strength in ("cause", "association"):
        for scope in ("sample", "frame", "wider"):
            pop = d[scope].format(n=n) if scope == "sample" else d[scope]
            claims[f"{strength}_{scope}"] = dict(
                strength=strength, scope=scope,
                text=TEXT[strength].format(treatment=d["treatment"],
                                           outcome=d["outcome"], pop=pop))

    live = [k for k, c in claims.items()
            if _supported(c["strength"], c["scope"], at_random, assignment)]
    top = [k for k in live
           if all(_stronger_or_equal((claims[k]["strength"], claims[k]["scope"]),
                                     (claims[o]["strength"], claims[o]["scope"]))
                  for o in live)]
    if len(top) != 1:
        raise ItemError(f"{len(top)} conclusions are maximal; the study picks none")
    key = top[0]

    names = [k for k in claims if k != key]
    if wrongs is None:
        rng.shuffle(names)
        picked = names[:3]
    else:
        for w in wrongs:
            if w == key:
                raise ItemError(f"{w!r} is the conclusion this design supports")
            if w not in claims:
                raise ItemError(f"no such conclusion as {w!r}")
        picked = list(wrongs)
    if len(picked) != 3:
        raise ItemError("need three wrong conclusions")

    reach = 1 if at_random else 0
    beyond = (f"generalized past {d['frame']}, the group the {d['unit']} were "
              f"selected from"
              if at_random else
              f"generalized from {d['unit']} who were not selected at random, so "
              f"the conclusion reaches only the {d['unit']} in the study")
    wrong = []
    for name in picked:
        c = claims[name]
        wide = LEVEL[c["scope"]] > reach
        narrow = LEVEL[c["scope"]] < reach
        strong = c["strength"] == "cause" and not assignment
        weak = c["strength"] == "association" and assignment
        if strong and wide:
            why = f"read selection as assignment, and {beyond}"
        elif strong:
            why = AS_ASSIGNED
        elif wide:
            why = beyond
        elif narrow and weak:
            why = BOTH_SMALL
        elif narrow:
            why = TOO_NARROW
        elif weak:
            why = TOO_WEAK
        else:
            raise ItemError(f"{name!r} is the conclusion this design supports")
        wrong.append(Mis(why, c["text"]))
    choices, reasons, letter = assemble_text(claims[key]["text"], wrong, rng)

    why = ((f"The {d['unit']} were randomly assigned, so the difference between the "
            f"groups is a cause; " if assignment else
            f"The {d['unit']} were not randomly assigned, so the difference between "
            f"the groups is an association and not a cause; ")
           + (f"they were selected at random from {d['frame']}, so the conclusion "
              f"reaches that group."
              if at_random else
              f"they were not selected at random, so the conclusion reaches only "
              f"the {d['unit']} in the study."))
    P = dict(kind="esc.conclusion", trial=[k for k, v in TRIALS.items() if v is d][0],
             n=n, weeks=weeks, selection=selection, assignment=bool(assignment),
             frame=d["frame"], sample=d["sample"].format(n=n), wider=d["wider"],
             texts=list(choices))
    stem = d["draw"][(selection, assignment)].format(n=n, weeks=weeks) + " " + ASK
    return Item("esc.conclusion", "evaluating a statistical claim", tier, seed, stem,
                "mcq", E(0), letter, why, choices, reasons, list(choices), params=P)
