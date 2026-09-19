"""The scenarios, as the fragments a page is assembled from.

A scene is vocabulary, never an answer. It says how this scenario names its
population, what its members are called, what was measured and in what units,
and how it words a statement about an interval -- the same kind of fact as
"a school is in a county" in `evaluating_statistical_claims`. Which of the
sentences built from those fragments a study supports is worked out in
`study.py`, from the study, every time.

Two constraints on the vocabulary, both learned the hard way by other topics:

* `check._shape` reads the letters **pi** inside ordinary English, so an
  option naming *participants*, *opinion*, *a hospital* or *the capital* is
  read as a pi-bearing option and the key becomes "the only option that looks
  like this". Every scene's words are checked for the substring by
  `option_check`. Say *respondents*, *view*, *medical center*, *largest city*.
* Numbers are exact. `estimate` and `margin` are `Fraction`s in the units the
  stem prints -- percentage points for a percent, the measure's own units for
  a mean -- and the page is rendered from them, never from a float.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as Q

from .values import dec, places_needed

__all__ = ["Scene", "SCENES", "MEAN_SCENES", "PCT_SCENES", "TABLE_SCENES",
           "SUBGROUP_SCENES", "COUNT_SCENES", "SCALE_SCENES", "RANGE_SCENES",
           "TWO_WAY", "FREQ_SCENES", "DESIGN_SCENES"]


@dataclass(frozen=True)
class Scene:
    """One scenario's words.

    `style` is how this scenario words an interval statement, and it is the
    reason a catalogue never holds two sentences with the same meaning: a
    scene words an interval one way, so exactly one sentence in the catalogue
    can be the interval claim.
    """
    key: str
    quantity: str                       # percent | proportion | mean
    draw: str                           # the sampling sentence(s); takes {n}
    report: str                         # takes {est} and {moe}
    ask: str
    subject: str                        # "The percent of the students who ..."
    subject_lc: str
    style: str = "plain"                # plain | plausible_values | it_is_plausible
                                        # | between_pop
    pop_all: str = ""                   # "all adults who own televisions"
    trait: str = ""                     # "use their televisions to watch nature shows"
    count_np: str = ""                  # "the number of the students who ..."
    indiv: str = ""                     # "The actual weights of all handbags ..."
    indiv_sample: str = ""
    members: str = ""                   # "visitors"
    member: str = ""                    # "visitor"
    did: str = ""                       # "hiked"
    label: str = ""                     # "heavy texters"
    unit: str = ""
    unit_each: bool = False
    places: int | None = None
    nrange: tuple = (200, 900)
    nstep: int = 20
    erange: tuple = ()                  # (lo, hi) for the estimate, in printed units
    estep: Q = Q(1)
    mrange: tuple = ()                  # (lo, hi) for the margin
    mstep: Q = Q(1)
    extra: dict = field(default_factory=dict)

    # ------------------------------------------------------------ printing

    def num(self, v) -> str:
        p = self.places if self.places is not None else places_needed(v)
        return dec(v, p)

    def one(self, v) -> str:
        return self.num(v) + self.unit

    def pair(self, lo, hi) -> str:
        if self.unit_each:
            return f"{self.num(lo)}{self.unit} and {self.num(hi)}{self.unit}"
        return f"{self.num(lo)} and {self.num(hi)}{self.unit}"


PCT = dict(unit="%", unit_each=True)


# --------------------------------------------------------------- percent scenes

PCT_SCENES = {
    "menu": Scene(
        key="menu", quantity="percent", style="plausible_values",
        draw="At a large high school, {n} students were selected at random and "
             "were asked in a survey about a menu change in the school cafeteria. "
             "All {n} students completed the survey.",
        report="It was estimated that {est} of the students were in support of a "
               "menu change, with a margin of error of {moe}.",
        ask="Which of the following is the best interpretation of the survey results?",
        subject="The percent of the students at the school who support a menu change",
        subject_lc="the percent of the students at the school who support a menu change",
        pop_all="the students at the school", trait="support a menu change",
        count_np="the number of the students at the school who support a menu change",
        members="students", member="student", label="supporters of a menu change",
        nrange=(150, 600), nstep=50, erange=(24, 62), mrange=(Q(5, 2), Q(13, 2)),
        mstep=Q(1, 2), **PCT),
    "television": Scene(
        key="television", quantity="percent", style="between_pop",
        draw="A sample consisting of {n} adults who own televisions was selected "
             "at random for a study.",
        report="Based on the sample, it is estimated that {est} of all adults who "
               "own televisions use their televisions to watch nature shows, with "
               "an associated margin of error of {moe}.",
        ask="Which of the following is the most plausible conclusion about all "
            "adults who own televisions?",
        subject="The percent of all adults who own televisions who use their "
                "televisions to watch nature shows",
        subject_lc="the percent of all adults who own televisions who use their "
                   "televisions to watch nature shows",
        pop_all="all adults who own televisions",
        trait="use their televisions to watch nature shows",
        count_np="the number of adults who own televisions who use their "
                 "televisions to watch nature shows",
        members="adults", member="adult", label="nature show viewers",
        nrange=(400, 1200), nstep=40, erange=(22, 68),
        mrange=(Q(201, 100), Q(499, 100)), mstep=Q(1, 100),
        extra=dict(no_conc=(
            "Since the sample included adults who own televisions and not just "
            "those who use their televisions to watch nature shows, no conclusion "
            "can be made.",
            "Since the sample did not include all the people who watch nature "
            "shows, no conclusion can be made.")),
        **PCT),
    "recycling": Scene(
        key="recycling", quantity="percent", style="it_is_plausible",
        draw="A city council selected {n} of the city's residents at random and "
             "asked each of them whether they recycle at home.",
        report="Based on the responses, it is estimated that {est} of the city's "
               "residents recycle at home, with an associated margin of error "
               "of {moe}.",
        ask="Which of the following is the most appropriate conclusion about all "
            "of the city's residents?",
        subject="The percent of the city's residents who recycle at home",
        subject_lc="the percent of the city's residents who recycle at home",
        pop_all="the city's residents", trait="recycle at home",
        count_np="the number of the city's residents who recycle at home",
        members="residents", member="resident", label="residents who recycle",
        nrange=(250, 800), nstep=50, erange=(31, 74), mrange=(2, 7),
        extra=dict(no_conc=(
            "Since the sample included residents who do not recycle at home and "
            "not just those who do, no conclusion can be made.",
            "Since the sample did not include all of the city's residents, no "
            "conclusion can be made.")),
        **PCT),
    "bus": Scene(
        key="bus", quantity="percent", style="plausible_values",
        draw="A transit agency surveyed {n} riders selected at random from all "
             "the riders on its bus routes.",
        report="Based on the survey, it is estimated that {est} of the riders on "
               "the agency's bus routes ride a bus every weekday, with an "
               "associated margin of error of {moe}.",
        ask="Which of the following is the best interpretation of the survey results?",
        subject="The percent of the riders on the agency's bus routes who ride a "
                "bus every weekday",
        subject_lc="the percent of the riders on the agency's bus routes who ride "
                   "a bus every weekday",
        pop_all="the riders on the agency's bus routes",
        trait="ride a bus every weekday",
        count_np="the number of riders on the agency's bus routes who ride a bus "
                 "every weekday",
        members="riders", member="rider", label="weekday riders",
        nrange=(300, 900), nstep=25, erange=(35, 71), mrange=(Q(3, 2), Q(11, 2)),
        mstep=Q(1, 2), **PCT),
}

PROP_SCENES = {
    "characteristic": Scene(
        key="characteristic", quantity="proportion", style="it_is_plausible",
        draw="To estimate the proportion of a population that has a certain "
             "characteristic, a random sample was selected from the population.",
        report="Based on the sample, it is estimated that the proportion of the "
               "population that has the characteristic is {est}, with an "
               "associated margin of error of {moe}.",
        ask="Based on this estimate and margin of error, which of the following "
            "is the most appropriate conclusion about the proportion of the "
            "population that has the characteristic?",
        subject="The proportion", subject_lc="the proportion",
        pop_all="the population", trait="have the characteristic",
        count_np="the number of members of the population that have the "
                 "characteristic",
        members="members", member="member", label="members with the characteristic",
        places=2, nrange=(0, 0), nstep=1,
        erange=(Q(31, 100), Q(72, 100)), estep=Q(1, 100),
        mrange=(Q(2, 100), Q(9, 100)), mstep=Q(1, 100)),
    "seeds": Scene(
        key="seeds", quantity="proportion", style="it_is_plausible",
        draw="A seed supplier selected a random sample of {n} seeds from a large "
             "shipment and planted them under identical conditions.",
        report="Based on the sample, it is estimated that the proportion of the "
               "seeds in the shipment that will sprout is {est}, with an "
               "associated margin of error of {moe}.",
        ask="Which of the following is the most appropriate conclusion about the "
            "proportion of the seeds in the shipment that will sprout?",
        subject="The proportion of the seeds in the shipment that will sprout",
        subject_lc="the proportion of the seeds in the shipment that will sprout",
        pop_all="the seeds in the shipment", trait="will sprout",
        count_np="the number of seeds in the shipment that will sprout",
        members="seeds", member="seed", label="seeds that sprout",
        places=2, nrange=(120, 480), nstep=20,
        erange=(Q(58, 100), Q(93, 100)), estep=Q(1, 100),
        mrange=(Q(2, 100), Q(6, 100)), mstep=Q(1, 100)),
}

# --------------------------------------------------------------- mean scenes

MEAN_SCENES = {
    "study_mean": Scene(
        key="study_mean", quantity="mean", style="plain",
        draw="In a study, the data from a random sample of a population had a "
             "mean of {est}, with an associated margin of error of {moe}.",
        report="",
        ask="Which of the following is the most appropriate conclusion that can "
            "be made about the population mean?",
        subject="It", subject_lc="the population mean",
        pop_all="the population", trait="",
        # no verb: an anonymous study has nothing its members can be said to
        # have *done*, and the sentences that need one read as nonsense
        # ("It is likely that all members measured between 69 and 73"). The
        # two `indiv` fragments carry the individual-value claims instead.
        members="members", member="member", did="",
        indiv="The actual values for all members of the population",
        indiv_sample="The actual values for all members of the sample",
        nrange=(0, 0), nstep=1, erange=(18, 96), mrange=(2, 9)),
    "handbags": Scene(
        key="handbags", quantity="mean", style="plain",
        draw="A company designs and makes handbags. To estimate the mean weight "
             "of the handbags made by the company on a particular day, a sample "
             "of the handbags made by the company on that day was selected at "
             "random.",
        report="Based on the sample, it is estimated that the mean weight of all "
               "handbags made by the company on that day is {est}, with an "
               "associated margin of error of {moe}.",
        ask="Based on this estimate and associated margin of error, which of the "
            "following is the most plausible conclusion?",
        subject="The mean weight of all handbags made by the company on that day",
        subject_lc="the mean weight of all handbags made by the company on that day",
        pop_all="all handbags made by the company on that day",
        trait="were made on that day",
        indiv="The actual weights of all handbags made by the company on that day",
        indiv_sample="The actual weights of all handbags from the sample",
        members="handbags", member="handbag", did="weighed",
        unit=" oz", unit_each=True,
        nrange=(0, 0), nstep=1,
        erange=(Q(212, 10), Q(348, 10)), estep=Q(1, 10),
        mrange=(Q(1, 100), Q(9, 100)), mstep=Q(1, 100),
        extra=dict(first_use="ounces (oz)")),
    "hiking": Scene(
        key="hiking", quantity="mean", style="it_is_plausible",
        draw="A park ranger asked a random sample of visitors how far they hiked "
             "during their visit.",
        report="Based on the responses, the estimated mean was found to be {est}, "
               "with an associated margin of error of {moe}.",
        ask="Which of the following is the best conclusion from these data?",
        subject="The mean distance hiked for all visitors",
        subject_lc="the mean distance hiked for all visitors",
        pop_all="all visitors", trait="hiked during their visit",
        indiv="The actual distances hiked by all visitors",
        indiv_sample="The actual distances hiked by the visitors in the sample",
        members="visitors", member="visitor", did="hiked",
        unit=" miles", unit_each=False,
        nrange=(0, 0), nstep=1,
        erange=(Q(21, 10), Q(88, 10)), estep=Q(1, 10),
        mrange=(Q(3, 10), Q(12, 10)), mstep=Q(1, 10)),
    "batteries": Scene(
        key="batteries", quantity="mean", style="plausible_values",
        draw="A manufacturer tested a random sample of {n} batteries from a "
             "production run to estimate how long the batteries in the run last.",
        report="Based on the sample, the mean life of the batteries in the run is "
               "estimated to be {est}, with an associated margin of error of {moe}.",
        ask="Which of the following is the best interpretation of the estimate and "
            "its margin of error?",
        subject="The mean life of the batteries in the production run",
        subject_lc="the mean life of the batteries in the production run",
        pop_all="the batteries in the production run", trait="were tested",
        indiv="The actual lives of all the batteries in the production run",
        indiv_sample="The actual lives of the batteries in the sample",
        members="batteries", member="battery", did="lasted",
        unit=" hours", unit_each=False,
        nrange=(40, 200), nstep=10,
        erange=(Q(146, 10), Q(392, 10)), estep=Q(1, 10),
        mrange=(Q(2, 10), Q(15, 10)), mstep=Q(1, 10)),
}

PCT_SCENES = {**PCT_SCENES, **PROP_SCENES}
SCENES = {**PCT_SCENES, **MEAN_SCENES}


# a scenario worded for a sample that selected itself. The study then reports
# nothing about the population, so "no conclusion can be made" stops being a
# distractor and becomes the answer -- which is how that branch of the rule
# is kept reachable rather than merely written down.
SELF_SELECTED = {
    "television": "A television magazine printed a survey in one issue, and {n} "
                  "adults who own televisions chose to mail in a response.",
    "recycling": "A city council posted a survey on its website, and {n} of the "
                 "city's residents chose to complete it.",
}
NO_CONCLUSION_SELF = {
    "television": "Since the adults who responded chose to take part themselves, "
                  "no conclusion can be made about all adults who own televisions.",
    "recycling": "Since the residents who responded chose to take part themselves, "
                 "no conclusion can be made about all of the city's residents.",
}

for _k, _v in NO_CONCLUSION_SELF.items():
    SCENES[_k].extra["no_conc_self"] = _v
for _k, _v in SELF_SELECTED.items():
    SCENES[_k].extra["draw_self"] = _v


# --------------------------------------------- the estimate read off a table

TABLE_SCENES = {
    "texting": Scene(
        key="texting", quantity="percent", style="plain",
        draw="In a study of cell phone use, {n} randomly selected US teens were "
             "asked how often they talked on a cell phone and about their "
             "texting behavior. The data are summarized in the table above.",
        report="Based on the data from the study, an estimate of the percent of "
               "US teens who are heavy texters is {est} and the associated "
               "margin of error is {moe}.",
        ask="Which of the following is a correct statement based on the given "
            "margin of error?",
        subject="The percent of all US teens who are heavy texters",
        subject_lc="the percent of all US teens who are heavy texters",
        pop_all="all US teens", trait="are heavy texters",
        count_np="the number of all US teens who are heavy texters",
        members="teens", member="teen", label="heavy texters",
        mrange=(2, 5),
        extra=dict(corner="Texting behavior",
                   cols=("Talks on cell phone daily",
                         "Does not talk on cell phone daily"),
                   rows=("Light", "Medium", "Heavy"), focus=2),
        **PCT),
    "commute": Scene(
        key="commute", quantity="percent", style="plain",
        draw="A regional authority asked {n} randomly selected workers in the "
             "region how they travel to work and how far they travel. The "
             "responses are summarized in the table above.",
        report="Based on the data from the study, an estimate of the percent of "
               "workers in the region whose journey is long is {est} and the "
               "associated margin of error is {moe}.",
        ask="Which of the following is a correct statement based on the given "
            "margin of error?",
        subject="The percent of all workers in the region whose journey to work "
                "is long",
        subject_lc="the percent of all workers in the region whose journey to "
                   "work is long",
        pop_all="all workers in the region", trait="have a long journey to work",
        count_np="the number of workers in the region whose journey to work is long",
        members="workers", member="worker", label="long-journey workers",
        mrange=(2, 5),
        extra=dict(corner="Length of journey",
                   cols=("Travels by car", "Does not travel by car"),
                   rows=("Short", "Medium", "Long"), focus=2),
        **PCT),
}


# ------------------------------------------ a statistic measured on a subgroup

SUBGROUP_SCENES = {
    "pond": Scene(
        key="pond", quantity="percent", style="plain",
        draw="A study was done on the weights of different types of fish in a "
             "pond. A random sample of fish were caught and marked in order to "
             "ensure that none were weighed more than once.",
        report="The sample contained {n} largemouth bass, of which {est} weighed "
               "more than 2 pounds.",
        ask="Which of the following conclusions is best supported by the sample "
            "data?",
        subject="The percent of all largemouth bass in the pond that weigh more "
                "than 2 pounds",
        subject_lc="the percent of all largemouth bass in the pond that weigh "
                   "more than 2 pounds",
        pop_all="all largemouth bass in the pond",
        trait="weigh more than 2 pounds",
        members="largemouth bass", member="largemouth bass",
        nrange=(100, 300), nstep=25, erange=(20, 76), mrange=(1, 1),
        extra=dict(wider_all="all fish in the pond",
                   wider_claims=dict(
                       majority="The majority of all fish in the pond weigh less "
                                "than 2 pounds.",
                       mean="The average weight of all fish in the pond is "
                            "approximately 2 pounds.")),
        **PCT),
    "orchard": Scene(
        key="orchard", quantity="percent", style="plain",
        draw="A grower surveyed the trees in an orchard by walking a randomly "
             "chosen route and recording every tree along it.",
        report="The sample contained {n} apple trees, of which {est} were in "
               "blossom.",
        ask="Which of the following conclusions is best supported by the sample "
            "data?",
        subject="The percent of all apple trees in the orchard that are in blossom",
        subject_lc="the percent of all apple trees in the orchard that are in "
                   "blossom",
        pop_all="all apple trees in the orchard", trait="are in blossom",
        members="apple trees", member="apple tree",
        nrange=(80, 260), nstep=20, erange=(15, 80), mrange=(1, 1),
        extra=dict(wider_all="all trees in the orchard",
                   wider_claims=dict(
                       majority="The majority of all trees in the orchard are "
                                "not in blossom.",
                       mean="The average height of all trees in the orchard is "
                            "approximately 3 meters.")),
        **PCT),
}


# ------------------------------------------------- a scaled-up count, or not

COUNT_SCENES = {
    "fruit": Scene(
        key="fruit", quantity="proportion", style="plain",
        draw="A store manager reviewed the receipts from {n} customers who were "
             "selected at random from all the customers who made purchases last "
             "Thursday. Of those selected, {k} receipts showed that the customer "
             "had purchased fruit.",
        report="",
        ask="If {size} customers made purchases last Thursday, which of the "
            "following is the most appropriate conclusion?",
        subject="The number of customers who purchased fruit last Thursday",
        subject_lc="the number of customers who purchased fruit last Thursday",
        pop_all="all the customers who made purchases last Thursday",
        trait="purchased fruit", members="customers", member="customer",
        count_np="the number of customers who purchased fruit last Thursday",
        nrange=(40, 200), nstep=20,
        extra=dict(size=(600, 4000), sstep=100,
                   must="Exactly {v} customers must have purchased fruit last "
                        "Thursday.",
                   best="The best estimate for the number of customers who "
                        "purchased fruit last Thursday is {v}.")),
    "badges": Scene(
        key="badges", quantity="proportion", style="plain",
        draw="An event organizer checked {n} badges chosen at random from all "
             "the badges scanned at the entrance on Saturday. Of those checked, "
             "{k} badges belonged to members of the host club.",
        report="",
        ask="If {size} badges were scanned on Saturday, which of the following "
            "is the most appropriate conclusion?",
        subject="The number of badges scanned on Saturday that belonged to "
                "members of the host club",
        subject_lc="the number of badges scanned on Saturday that belonged to "
                   "members of the host club",
        pop_all="all the badges scanned on Saturday",
        trait="belonged to members of the host club",
        members="badges", member="badge",
        count_np="the number of badges scanned on Saturday that belonged to "
                 "members of the host club",
        nrange=(50, 250), nstep=25,
        extra=dict(size=(800, 5000), sstep=100,
                   must="Exactly {v} of the badges scanned on Saturday must have "
                        "belonged to members of the host club.",
                   best="The best estimate for the number of badges scanned on "
                        "Saturday that belonged to members of the host club "
                        "is {v}.")),
}
