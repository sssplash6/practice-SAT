"""Whether the sampling method supports anything at all.

One rule decides every option in this family:

    **whether a sample can stand for a population is settled by how the
    sample was obtained, and by nothing the sample reported.**

So a statement is licensed only when it speaks about the method, and which of
those statements is licensed is settled by a single fact about the study: were
the units selected at random *from the population the claim is about*? A
sample drawn from a subgroup, a sample of whoever turned up, and a sample of
whoever chose to answer are all unsound, and every one of them supports the
same verdict -- the method may produce a biased estimate.

The statements about the responses -- that the percentages do not reach 100,
that the split was not even -- can be perfectly true and still explain
nothing, so they are never licensed. That is not a special case: it is the
rule above, read from the other side.
"""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, ItemError, Mis, assemble_text

__all__ = ["sample_quality", "STUDIES", "SOUND"]

# A method is sound when it selects units at random from the population the
# conclusion is about. Everything else is not.
SOUND = {"random": True, "subgroup": False, "convenience": False,
         "self_selected": False}


def _verdict(kind: str, sound: bool) -> bool:
    """Is this statement about the method a true one?"""
    if kind in ("biased", "not_random", "flawed", "random_remedy"):
        return not sound
    if kind == "not_flawed":
        return sound
    raise ItemError(f"{kind!r} is not a statement about the method")


# Every statement this family can print. `method` marks the ones that speak to
# how the sample was obtained; the rest report on the sample's answers, or
# propose a remedy that does not reach the population, and can never be the
# reason a sample does or does not represent a population.
SAYS: dict[str, dict] = {
    "biased": dict(method=True,
                   text="The survey sample is biased because it is not "
                        "representative of {pop_all}."),
    "not_random": dict(method=True,
                       text="Those who responded to the {poll} were not a random "
                            "sample of {pop_all}."),
    "flawed": dict(method=True,
                   text="The sampling method is flawed and may produce a biased "
                        "estimate of {quantity} in {place}."),
    "not_flawed": dict(method=True,
                       text="The sampling method is not flawed and is likely to "
                            "produce an unbiased estimate of {quantity} in {place}."),
    "random_remedy": dict(method=True,
                          text="The survey sample should have been selected at "
                               "random from {pop_all}."),
    "pop_majority": dict(
        method=False,
        text="It shows that the majority of {pop_short} are {stance}.",
        why="read a result about the sample as a result about the population"),
    "pop_mean": dict(
        method=False,
        text="{Quantity} in {place} is {value}.",
        why="read the sample's own figure as the population's"),
    "too_small": dict(
        method=False,
        text="A determination about {quantity} in {place} should not be made "
             "because the sample size is too small.",
        why="blamed the size of the sample, when it is the way the sample was "
            "chosen that decides whether the estimate is biased"),
    "more_sub": dict(
        method=False,
        text="The survey sample should have included more {sub}.",
        why={False: "proposed more of the very group that is already "
                    "over-represented",
             True: "proposed narrowing a sample that was already drawn at random "
                   "from the whole population"}),
    "only_other": dict(
        method=False,
        text="The survey sample should have consisted entirely of {othersub}.",
        why={False: "swapped one unrepresentative group for another instead of "
                    "sampling the whole population",
             True: "would replace a random sample of the population with one "
                   "subgroup of it"}),
    "pct_sum": dict(
        method=False, explains_only=True,
        text="The percentages do not add up to 100%, so any possible conclusions "
             "from the {poll} are invalid.",
        why="treated the missing percentage as a contradiction, when some of those "
            "asked simply gave neither answer"),
    "not_fifty": dict(
        method=False, explains_only=True,
        text="There were not 50% “Yes” responses and 50% “No” "
             "responses.",
        why="named a fact about the responses, which says nothing about who was "
            "asked"),
    "more_time": dict(
        method=False, explains_only=True,
        text="The show did not allow viewers enough time to respond to the poll.",
        why="invented a shortcoming the passage never reports"),
}

WHY_METHOD = {
    True: {"biased": "called a random sample of the population unrepresentative",
           "not_random": "called a random sample of the population not random",
           "flawed": "called a sound sampling method flawed",
           "random_remedy": "asked for the random selection the study already used",
           "not_flawed": ""},
    False: {"biased": "", "not_random": "", "flawed": "", "random_remedy": "",
            "not_flawed": "read a sample that was not drawn at random from the "
                          "population as if it had been"},
}

ASKS = {
    "true_about": "Which of the following is true about the {study}?",
    "must_be_true": "Which of the following statements must be true?",
    "best_explains": "Which of the following best explains why the results are "
                     "unlikely to represent the sentiments of {pop_all}?",
}


STUDIES: dict[str, dict] = {
    # 1.1 -- the target population is all city residents; the sample is drawn
    # at random, but from the dog owners among them
    "dog_park": dict(
        method="subgroup", ask="true_about", study="city council’s survey",
        pop_all="all city residents", pop_short="city residents",
        stance="in favor of the dog park", poll="survey",
        quantity="the level of support", place="the city",
        sub="residents who are dog owners", othersub="residents who do not own dogs",
        draw="The members of a city council wanted to assess the opinions of all "
             "city residents about converting an open field into a dog park. The "
             "council surveyed a sample of {n} city residents who own dogs. The "
             "survey showed that the majority of those sampled were in favor of the "
             "dog park.",
        says=("pop_majority", "more_sub", "only_other", "biased"),
        nrange=(200, 800), nstep=100),
    # 3.4 -- viewers of one show who chose to answer
    "cable_poll": dict(
        method="self_selected", ask="best_explains", study="poll",
        pop_all="the population of the United States",
        pop_short="people in the United States",
        stance="in support of the policy", poll="poll",
        quantity="the level of support", place="the United States",
        draw="Near the end of a US cable news show, the host invited viewers to "
             "respond to a poll on the show’s website that asked, “Do you "
             "support the new federal policy discussed during the show?” At the "
             "end of the show, the host reported that {yes}% responded “Yes,"
             "” and {no}% responded “No.”",
        says=("pct_sum", "not_random", "not_fifty", "more_time"),
        nrange=(0, 0), split=True),
    # 3.5 -- whoever happened to be at the playground
    "playground": dict(
        method="convenience", ask="must_be_true", study="survey",
        pop_all="all the households in the community",
        pop_short="households in the community",
        stance="families with children", poll="survey",
        quantity="the mean number of children per household",
        Quantity="The mean number of children per household",
        place="the community", value="{mean}",
        draw="To determine the mean number of children per household in a "
             "community, Tabitha surveyed {n} families at a playground. For the {n} "
             "families surveyed, the mean number of children per household was "
             "{mean}.",
        says=("pop_mean", "too_small", "flawed", "not_flawed"),
        nrange=(15, 40), nstep=5, mean=(15, 34)),
    # ----- contexts written for the bank
    "reading_minutes": dict(
        method="random", ask="must_be_true", study="survey",
        pop_all="all the students at the school",
        pop_short="students at the school",
        stance="reading every day", poll="survey",
        quantity="the mean number of minutes per day spent reading",
        Quantity="The mean number of minutes per day spent reading",
        place="the school", value="{mean}",
        draw="To determine the mean number of minutes per day that the students at a "
             "certain school spend reading, a teacher surveyed {n} students selected "
             "at random from all the students at the school. For the {n} students "
             "surveyed, the mean number of minutes per day spent reading was {mean}.",
        says=("pop_mean", "too_small", "flawed", "not_flawed"),
        nrange=(30, 90), nstep=10, mean=(180, 460)),
    "checkout_queue": dict(
        method="convenience", ask="must_be_true", study="survey",
        pop_all="all the shoppers at the supermarket",
        pop_short="shoppers at the supermarket",
        stance="shopping on a weekday", poll="survey",
        quantity="the mean amount spent per visit",
        Quantity="The mean amount spent per visit",
        place="the supermarket", value="${mean}",
        draw="To determine the mean amount spent per visit by the shoppers at a "
             "supermarket, a manager surveyed the {n} shoppers who used the busiest "
             "checkout on one Friday evening. For the {n} shoppers surveyed, the "
             "mean amount spent was ${mean}.",
        says=("pop_mean", "too_small", "flawed", "not_flawed"),
        nrange=(20, 60), nstep=10, mean=(2_100, 4_800), mean_fmt="money"),
    "staff_room": dict(
        method="subgroup", ask="true_about", study="principal’s survey",
        pop_all="all the staff at the school", pop_short="staff at the school",
        stance="in favor of the later start", poll="survey",
        quantity="the level of support", place="the school",
        sub="staff who teach a class", othersub="staff who do not teach a class",
        draw="The principal of a school wanted to assess the opinions of all the "
             "staff at the school about a later start to the school day. The "
             "principal surveyed a sample of {n} staff who teach a class. The survey "
             "showed that the majority of those sampled were in favor of the later "
             "start.",
        says=("pop_majority", "more_sub", "only_other", "biased"),
        nrange=(20, 60), nstep=5),
    "website_poll": dict(
        method="self_selected", ask="best_explains", study="poll",
        pop_all="the population of the county",
        pop_short="people in the county",
        stance="in support of the proposal", poll="poll",
        quantity="the level of support", place="the county",
        draw="At the end of an article about a planned bypass, a county newspaper "
             "invited readers to respond to a poll on its website that asked, "
             "“Do you support the planned bypass?” The newspaper later "
             "reported that {yes}% responded “Yes,” and {no}% responded "
             "“No.”",
        says=("pct_sum", "not_random", "not_fifty", "more_time"),
        nrange=(0, 0), split=True),
    "clinic_wait": dict(
        method="random", ask="true_about", study="survey",
        pop_all="all the patients of the clinic", pop_short="patients of the clinic",
        stance="satisfied with the waiting time", poll="survey",
        quantity="the level of satisfaction with the waiting time",
        place="the clinic",
        sub="patients who arrive before noon",
        othersub="patients who arrive after noon",
        draw="The manager of a clinic wanted to assess the opinions of all the "
             "patients of the clinic about the waiting time. The manager surveyed a "
             "sample of {n} patients selected at random from all the patients of the "
             "clinic. The survey showed that the majority of those sampled were "
             "satisfied with the waiting time.",
        says=("pop_majority", "more_sub", "only_other", "not_flawed"),
        nrange=(50, 200), nstep=25),
}


def _fill(text: str, d: dict, extra: dict) -> str:
    """Fill a statement's slots. Twice, because a context's `value` is itself a
    slot: "{Quantity} in {place} is {value}" with value = "${mean}"."""
    at = {**d, **extra}
    try:
        return text.format(**at).format(**at)
    except KeyError as exc:                 # this study has no such vocabulary
        raise ItemError(f"this study cannot say {exc} in {text!r}") from exc


def sample_quality(rng: random.Random, seed: int, *, ctx=None, n=None, says=None,
                   mean=None, yes=None, no=None, tier="hard") -> Item:
    """What a sampling method does, and does not, entitle anyone to say."""
    d = STUDIES[ctx] if ctx is not None else STUDIES[rng.choice(sorted(STUDIES))]
    sound = SOUND[d["method"]]
    extra = {}
    lo, hi = d["nrange"]
    n = int(n) if n is not None else (rng.randrange(lo, hi + 1, d["nstep"]) if hi else 0)
    extra["n"] = n
    if "mean" in d and d["mean"]:
        m0, m1 = d["mean"]
        v = int(mean) if mean is not None else rng.randint(m0, m1)
        extra["mean"] = (f"{v // 100}.{v % 100:02d}" if d.get("mean_fmt") == "money"
                         else f"{v // 10}.{v % 10}")
    if d.get("split"):
        yes = int(yes) if yes is not None else rng.randrange(18, 45)
        no = int(no) if no is not None else 98 - yes - rng.randrange(0, 4)
        if yes + no > 100 or no <= yes:
            raise ItemError("the two shares must leave room for the undecided")
        extra.update(yes=yes, no=no)

    names = list(says) if says is not None else list(d["says"])
    if len(names) != 4 or len(set(names)) != 4:
        raise ItemError("four different statements")
    ask = ASKS[d["ask"]].format(**{**d, **extra})

    printed, true_ones = [], []
    for name in names:
        s = SAYS[name]
        if s.get("explains_only") and d["ask"] != "best_explains":
            raise ItemError(f"{name!r} only answers a question about representation")
        text = _fill(s["text"], d, extra)
        holds = _verdict(name, sound) if s["method"] else False
        printed.append((name, text, holds))
        if holds:
            true_ones.append(name)
    if len(true_ones) != 1:
        raise ItemError(f"{len(true_ones)} of the four statements are true")

    key_name = true_ones[0]
    key_text = next(t for nm, t, _ in printed if nm == key_name)
    wrong = []
    for name, text, _ in printed:
        if name == key_name:
            continue
        s = SAYS[name]
        why = WHY_METHOD[sound][name] if s["method"] else s["why"]
        if isinstance(why, dict):
            why = why[sound]
        if not why:
            raise ItemError(f"no misconception recorded for {name!r}")
        wrong.append(Mis(why, text))
    choices, reasons, letter = assemble_text(key_text, wrong, rng)

    how = {"random": "selected at random from the population the question is about",
           "subgroup": "drawn only from one subgroup of the population",
           "convenience": "whoever happened to be there",
           "self_selected": "whoever chose to answer"}[d["method"]]
    why = (f"The sample was {how}, so the method "
           + ("supports an unbiased estimate for " if sound else
              "cannot be trusted to represent ")
           + d["pop_all"] + ".")
    P = dict(kind="esc.sample_quality", study=ctx or
             [k for k, v in STUDIES.items() if v is d][0],
             method=d["method"], n=n, says=names,
             statements=[t for _, t, _ in printed], ask=d["ask"],
             texts=list(choices))
    return Item("esc.sample_quality", "evaluating a statistical claim", tier, seed,
                _fill(d["draw"], d, extra) + " " + ask, "mcq", E(0), letter, why,
                choices, reasons, list(choices), params=P)
