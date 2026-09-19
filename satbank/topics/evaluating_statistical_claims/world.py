"""What a study is, and which populations its results reach.

Nothing in this file knows which option is correct, and nothing in it may be
given the answer. It holds two things:

* **the lattice** -- a population is one value per dimension, each dimension a
  tree of values whose edges record containment ("the school is in the
  county", "fourth-grade students are students"). `within` decides whether one
  population sits inside another;
* **the catalogue** -- the study contexts, as data. A context says what is
  being sampled, what the places are called, how the stem words the draw, and
  nothing else.

The rule that turns those into an answer lives in `families/scope.py`, is
written a second time in `audit.py`, and a third time in `option_check.py`.
Containment facts are scenario facts of the same kind as a scatterplot's
points: the page assumes a school is in a county, and no amount of reading the
page recovers it. Which of four populations a study *licenses* is never data.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["Val", "Dim", "Scope", "SCOPES", "TABLES", "canon", "within",
           "descends", "pops_of", "option_phrase", "unit_phrase", "pop_id",
           "plainest"]


# --------------------------------------------------------------- the lattice

@dataclass(frozen=True)
class Val:
    """One value a dimension can take.

    `parent` is the immediately broader value, or None at the top of the tree.
    Two values with the same parent and neither above the other -- 17 years old
    and 19 years old -- are incomparable: a study of one says nothing about the
    other.
    """
    parent: str | None = None
    frag: str = ""          # how an option names it, spaces included
    stem: str = ""          # how the stem names it, for a place


@dataclass(frozen=True)
class Dim:
    """One dimension of a population: a trait of the unit, or a place."""
    name: str
    slot: str                               # "pre" | "post" | "place"
    values: dict[str, Val]

    def top(self) -> str:
        return next(k for k, v in self.values.items() if v.parent is None)

    def depth(self, value: str) -> int:
        d, v = 0, value
        while self.values[v].parent is not None:
            v, d = self.values[v].parent, d + 1
        return d


def descends(dim: Dim, a: str, b: str) -> bool:
    """Is every member of value `a` also a member of value `b`?"""
    v = a
    while True:
        if v == b:
            return True
        nxt = dim.values[v].parent
        if nxt is None:
            return False
        v = nxt


def canon(sc: "Scope", spec: dict) -> dict:
    """The same population written without a redundant qualifier.

    "All students at the school" and "All middle school students at the
    school" are one population when the school is a middle school, and the
    lattice has to see them as one or an item can print both.
    """
    out = dict(spec)
    for _ in range(len(sc.dims) + 1):
        before = dict(out)
        for d in sc.dims:
            for dim2, val2 in sc.implies.get((d.name, out[d.name]), {}).items():
                other = sc.dim(dim2)
                if descends(other, val2, out[dim2]):
                    out[dim2] = val2
        if out == before:
            break
    return out


def within(sc: "Scope", a: dict, b: dict) -> bool:
    """Is population `a` contained in population `b`?"""
    ca, cb = canon(sc, a), canon(sc, b)
    return all(descends(d, ca[d.name], cb[d.name]) for d in sc.dims)


# --------------------------------------------------------------- a study
#
# A scope context. `draw` is keyed by sampling method, because a convenience
# sample is not worded as a random one with a word changed.

@dataclass(frozen=True)
class Scope:
    key: str
    unit: str                               # "students", "baobab trees"
    article: str                            # "All " or "All the "
    dims: tuple[Dim, ...]
    order: tuple[str, ...]                  # slots, in the order they print
    draw: dict[str, str]                    # method -> the stem's study sentences
    ask: str                                # the question sentence
    frame: dict                             # the default sampling frame
    pronoun: str = "who"                    # "who" for people, "that" for trees
    sample: str | None = None               # how an option names the sample
    subsample: str | None = None            # a named part of the sample
    nrange: tuple[int, int] = (20, 60)
    nstep: int = 5
    extra: dict = field(default_factory=dict)
    implies: dict = field(default_factory=dict)
    methods: tuple[str, ...] = ("random",)
    assignment: bool = False

    def dim(self, name: str) -> Dim:
        return next(d for d in self.dims if d.name == name)


def pop_id(sc: Scope, spec: dict) -> str:
    """A short name for a population, so a source item can ask for it."""
    return ",".join(spec[d.name] for d in sc.dims)


def unit_phrase(sc: Scope, spec: dict) -> str:
    """"fourth-grade students", "baobab trees that were 17 years old"."""
    pre = "".join(sc.dim(d.name).values[spec[d.name]].frag
                  for d in sc.dims if d.slot == "pre")
    post = "".join(sc.dim(d.name).values[spec[d.name]].frag
                   for d in sc.dims if d.slot == "post")
    return f"{pre}{sc.unit}{post}"


def option_phrase(sc: Scope, spec: dict) -> str:
    """How an option names a population, assembled from its own parts."""
    part = {"pre": "", "post": "", "place": "", "unit": sc.unit}
    for d in sc.dims:
        part[d.slot] += d.values[spec[d.name]].frag
    return sc.article + "".join(part[s] for s in sc.order)


def plainest(sc: Scope, spec: dict) -> dict:
    """The same population written the way the page words it.

    A frame of "middle school students at the school" is written "students at
    the school" when the school is a middle school, and the stem has to say it
    the way the option says it or the two stop being comparable.
    """
    want = pop_id(sc, canon(sc, spec))
    for other in pops_of(sc).values():
        if pop_id(sc, canon(sc, other)) == want:
            return other
    return spec


def pops_of(sc: Scope) -> dict[str, dict]:
    """Every population this context can name, one per distinct set.

    The candidates are the whole product of the dimensions. Two specs that
    describe the same set -- because the place already implies the trait --
    collapse to one, and the survivor is the one that says it with the fewest
    qualifiers, which is how the page words it.
    """
    specs: list[dict] = [{}]
    for d in sc.dims:
        specs = [dict(s, **{d.name: v}) for s in specs for v in d.values]
    best: dict[str, dict] = {}
    for spec in specs:
        ck = pop_id(sc, canon(sc, spec))
        weight = sum(sc.dim(d.name).depth(spec[d.name]) for d in sc.dims)
        if ck not in best or weight < best[ck][0]:
            best[ck] = (weight, spec)
    return {pop_id(sc, spec): spec for _, spec in best.values()}


# ------------------------------------------------------------- the catalogue

def _place(**kw) -> Dim:
    return Dim("place", "place", {k: v for k, v in kw.items()})


SCOPES: dict[str, Scope] = {}


def _add(sc: Scope) -> Scope:
    SCOPES[sc.key] = sc
    return sc


# 3.1 -- a school inside its county
_add(Scope(
    key="announcements",
    unit="students", article="All ",
    dims=(Dim("grade", "pre", {
              "fourth": Val("any", "fourth-grade "),
              "any": Val(None, "")}),
          _place(school=Val("county", " at the school", "a certain school"),
                 county=Val(None, " in the county in which the school is located",
                            "the county in which a certain school is located"))),
    order=("pre", "unit", "post", "place"),
    draw={"random": "A sample of {n} {pop} was selected at random from {frm}. "
                    "The {n} students completed a survey about the morning "
                    "announcements, and {k} thought the announcements were helpful.",
          "convenience": "A sample of {n} {pop} was formed from the students who "
                         "arrived earliest at {frm} one morning. The {n} students "
                         "completed a survey about the morning announcements, and "
                         "{k} thought the announcements were helpful."},
    ask="Which of the following is the largest population to which the results of "
        "the survey can be applied?",
    frame={"grade": "fourth", "place": "school"},
    sample="The {n} students who were surveyed",
    nrange=(20, 60), nstep=5, methods=("random", "convenience"),
    extra={"share": (5, 9)}))

# 2.2 -- no sample size is printed, so no option names the sample
_add(Scope(
    key="textbooks",
    unit="professors", article="All ",
    dims=(Dim("field", "pre", {
              "history": Val("any", "history "),
              "any": Val(None, "")}),
          _place(csu=Val("us", " at all California State Universities",
                         "the California State Universities"),
                 us=Val(None, " in the United States", "universities across the "
                        "United States"))),
    order=("pre", "unit", "post", "place"),
    draw={"random": "A survey was conducted using a sample of {pop} selected at "
                    "random from {frm}. The professors surveyed were asked to name "
                    "the publishers of their current texts."},
    ask="What is the largest population to which the results of the survey can be "
        "generalized?",
    frame={"field": "history", "place": "csu"},
    sample=None, nrange=(0, 0)))

# 3.3 -- the school is a middle school, so "all students at the school" and
# "all middle school students at the school" are the same population
_add(Scope(
    key="fractions_game",
    unit="students", article="All ",
    dims=(Dim("level", "pre", {
              "middle": Val("any", "middle school "),
              "any": Val(None, "")}),
          _place(school=Val("city", " at the school",
                            "one of the middle schools in a large city"),
                 city=Val(None, " in the city", "the schools of a large city"))),
    order=("pre", "unit", "post", "place"),
    draw={"random": "A psychologist designed and conducted a study to determine "
                    "whether playing a certain educational game increases middle "
                    "school students’ accuracy in adding fractions. For the "
                    "study, the psychologist chose a random sample of {n} {pop} from "
                    "all of the students at {frm}. The psychologist found that "
                    "students who played the game showed significant improvement in "
                    "accuracy when adding fractions.",
          "volunteer": "A psychologist designed and conducted a study to determine "
                       "whether playing a certain educational game increases middle "
                       "school students’ accuracy in adding fractions. For the "
                       "study, the psychologist enrolled the {n} {pop} at {frm} who "
                       "volunteered to take part. The psychologist found that "
                       "students who played the game showed significant improvement "
                       "in accuracy when adding fractions."},
    ask="What is the largest group to which the results of the study can be "
        "generalized?",
    frame={"level": "middle", "place": "school"},
    sample="The {n} students in the sample",
    implies={("place", "school"): {"level": "middle"}},
    nrange=(25, 70), nstep=5, methods=("random", "volunteer")))

# 3.6 -- random assignment on top of random selection; the scope still stops
# at the frame, and 19-year-old trees are a different set, not a wider one
_add(Scope(
    key="baobab", pronoun="that",
    unit="baobab trees", article="All the ",
    dims=(Dim("age", "post", {
              "a17": Val("any", " that were 17 years old"),
              "a19": Val("any", " that were 19 years old"),
              "any": Val(None, "")}),
          _place(habitat=Val("country", " in this habitat", "this habitat"),
                 country=Val(None, " in South Africa", "South Africa"))),
    order=("pre", "unit", "post", "place"),
    draw={"random": "For a baobab tree habitat in South Africa, a scientist randomly "
                    "selected {n} {pop} from {frm} and randomly assigned them to two "
                    "groups. Each group was subjected to a different watering pattern "
                    "for {years} consecutive years to observe whether the watering "
                    "pattern affects the trees’ growth rate."},
    ask="Based on the design of the study, what is the largest group to which these "
        "results can be applied?",
    frame={"age": "a17", "place": "habitat"},
    sample="All the {n} baobab trees that were selected in this habitat",
    nrange=(30, 80), nstep=10, assignment=True,
    extra={"years": (2, 4)}))

# ----- contexts written for the bank rather than copied from an official item

_add(Scope(
    key="library",
    unit="patrons", article="All ",
    dims=(Dim("age", "pre", {
              "adult": Val("any", "adult "),
              "any": Val(None, "")}),
          _place(branch=Val("system", " at the branch", "a certain library branch"),
                 system=Val(None, " in the county library system",
                            "the county library system to which a certain branch "
                            "belongs"))),
    order=("pre", "unit", "post", "place"),
    draw={"random": "A sample of {n} {pop} was selected at random from {frm}. The "
                    "{n} patrons completed a survey about the opening hours, and {k} "
                    "said the hours were convenient.",
          "convenience": "A sample of {n} {pop} was formed by surveying the patrons "
                         "who came to {frm} on one Saturday morning. The {n} patrons "
                         "completed a survey about the opening hours, and {k} said "
                         "the hours were convenient."},
    ask="Which of the following is the largest population to which the results of "
        "the survey can be applied?",
    frame={"age": "adult", "place": "branch"},
    sample="The {n} patrons who were surveyed",
    nrange=(30, 90), nstep=10, methods=("random", "convenience"),
    extra={"share": (5, 9)}))

_add(Scope(
    key="dinner",
    unit="customers", article="All ",
    dims=(Dim("meal", "pre", {
              "dinner": Val("any", "dinner "),
              "any": Val(None, "")}),
          _place(restaurant=Val("chain", " at the restaurant", "a certain restaurant"),
                 chain=Val(None, " at all the restaurants in the chain",
                           "all the restaurants in the chain to which a certain "
                           "restaurant belongs"))),
    order=("pre", "unit", "post", "place"),
    draw={"random": "A sample of {n} {pop} was selected at random from {frm}. The {n} "
                    "customers were asked to rate the service, and {k} rated it as "
                    "excellent.",
          "convenience": "A sample of {n} {pop} was formed from the customers seated "
                         "nearest the door at {frm}. The {n} customers were asked to "
                         "rate the service, and {k} rated it as excellent."},
    ask="Which of the following is the largest population to which the results of "
        "the survey can be applied?",
    frame={"meal": "dinner", "place": "restaurant"},
    sample="The {n} customers who were surveyed",
    nrange=(25, 75), nstep=5, methods=("random", "convenience"),
    extra={"share": (5, 9)}))

_add(Scope(
    key="bus",
    unit="riders", article="All ",
    dims=(Dim("time", "pre", {
              "morning": Val("any", "morning "),
              "any": Val(None, "")}),
          _place(route=Val("system", " on the route", "a certain bus route"),
                 system=Val(None, " in the city’s bus system",
                            "the bus system of the city in which a certain route "
                            "runs"))),
    order=("pre", "unit", "post", "place"),
    draw={"random": "A sample of {n} {pop} was selected at random from {frm}. The {n} "
                    "riders were asked whether the buses run often enough, and {k} "
                    "said that they do.",
          "convenience": "A sample of {n} {pop} was formed by handing a survey to the "
                         "riders waiting at the busiest stop on {frm}. The {n} riders "
                         "were asked whether the buses run often enough, and {k} said "
                         "that they do."},
    ask="Which of the following is the largest population to which the results of "
        "the survey can be applied?",
    frame={"time": "morning", "place": "route"},
    sample="The {n} riders who were surveyed",
    nrange=(40, 120), nstep=10, methods=("random", "convenience"),
    extra={"share": (5, 9)}))

_add(Scope(
    key="nurses",
    unit="nurses", article="All ",
    dims=(Dim("ward", "pre", {
              "pediatric": Val("any", "pediatric "),
              "any": Val(None, "")}),
          _place(center=Val("network", " at the medical center", "a certain medical center"),
                 network=Val(None, " at all the medical centers in the network",
                             "all the medical centers in the network to which a "
                             "certain center belongs"))),
    order=("pre", "unit", "post", "place"),
    draw={"random": "A sample of {n} {pop} was selected at random from {frm}. The {n} "
                    "nurses were asked whether the new scheduling software saves them "
                    "time, and {k} said that it does.",
          "volunteer": "A sample of {n} {pop} was formed from those at {frm} who "
                       "volunteered to take part. The {n} nurses were asked whether "
                       "the new scheduling software saves them time, and {k} said "
                       "that it does."},
    ask="Which of the following is the largest population to which the results of "
        "the survey can be applied?",
    frame={"ward": "pediatric", "place": "center"},
    sample="The {n} nurses who were surveyed",
    nrange=(20, 60), nstep=5, methods=("random", "volunteer"),
    extra={"share": (5, 9)}))

_add(Scope(
    key="orchard", pronoun="that",
    unit="apple trees", article="All the ",
    dims=(Dim("age", "post", {
              "a5": Val("any", " that were 5 years old"),
              "a8": Val("any", " that were 8 years old"),
              "any": Val(None, "")}),
          _place(orchard=Val("county", " in this orchard", "this orchard"),
                 county=Val(None, " in the county", "the county"))),
    order=("pre", "unit", "post", "place"),
    draw={"random": "For an apple orchard in a certain county, a grower randomly "
                    "selected {n} {pop} from {frm} and randomly assigned them to two "
                    "groups. Each group was pruned by a different method for {years} "
                    "consecutive years to observe whether the pruning method affects "
                    "the trees’ yield."},
    ask="Based on the design of the study, what is the largest group to which these "
        "results can be applied?",
    frame={"age": "a5", "place": "orchard"},
    sample="All the {n} apple trees that were selected in this orchard",
    nrange=(40, 100), nstep=10, assignment=True,
    extra={"years": (2, 5)}))

_add(Scope(
    key="seedlings", pronoun="that",
    unit="spruce seedlings", article="All the ",
    dims=(Dim("height", "post", {
              "h12": Val("any", " that were 12 inches tall"),
              "h18": Val("any", " that were 18 inches tall"),
              "any": Val(None, "")}),
          _place(nursery=Val("region", " at this nursery", "this nursery"),
                 region=Val(None, " in the region", "the region"))),
    order=("pre", "unit", "post", "place"),
    draw={"random": "At a tree nursery in a certain region, a botanist randomly "
                    "selected {n} {pop} from {frm} and randomly assigned them to two "
                    "groups. Each group was given a different fertilizer for {years} "
                    "consecutive growing seasons to observe whether the fertilizer "
                    "affects the seedlings’ growth rate."},
    ask="Based on the design of the study, what is the largest group to which these "
        "results can be applied?",
    frame={"height": "h12", "place": "nursery"},
    sample="All the {n} spruce seedlings that were selected at this nursery",
    nrange=(30, 90), nstep=10, assignment=True,
    extra={"years": (2, 4)}))

_add(Scope(
    key="cyclists",
    unit="cyclists", article="All ",
    dims=(Dim("club", "pre", {
              "club": Val("any", "club "),
              "any": Val(None, "")}),
          _place(town=Val("region", " in the town", "a certain town"),
                 region=Val(None, " in the region", "the region in which a certain "
                            "town lies"))),
    order=("pre", "unit", "post", "place"),
    draw={"random": "A sample of {n} {pop} was selected at random from {frm}. The {n} "
                    "cyclists were asked whether the new bicycle lanes feel safe, and "
                    "{k} said that they do.",
          "convenience": "A sample of {n} {pop} was formed by stopping cyclists at one "
                         "junction in {frm} on a weekday morning. The {n} cyclists "
                         "were asked whether the new bicycle lanes feel safe, and {k} "
                         "said that they do."},
    ask="Which of the following is the largest population to which the results of "
        "the survey can be applied?",
    frame={"club": "club", "place": "town"},
    sample="The {n} cyclists who were surveyed",
    nrange=(30, 80), nstep=10, methods=("random", "convenience"),
    extra={"share": (5, 9)}))


# --------------------------------------------- contexts that carry a table
#
# The table is the distraction: it reports only a part of the sample, and two
# of the printed populations are read off it rather than out of the draw.

TABLES: dict[str, Scope] = {}


def _table(sc: Scope, spec: dict) -> Scope:
    TABLES[sc.key] = sc
    sc.extra.update(spec)
    return sc


_table(Scope(
    key="trivia",
    unit="trivia teams", article="All ",
    dims=(Dim("score", "post", {
              "high": Val("any", " that scored {hi} or more points in the round"),
              "any": Val(None, "")}),
          _place(tournament=Val(None, " in the tournament",
                                "all trivia teams in a certain tournament")),),
    order=("pre", "unit", "place", "post"),
    draw={"random": "A trivia tournament organizer wanted to study the relationship "
                    "between the number of points a team scores in a trivia round and "
                    "the number of hours that a team practices each week. For the "
                    "study, the organizer selected {n} teams at random from {frm}. The "
                    "table displays the information for the {m} teams in the sample "
                    "that practiced for at least {cut} hours per week."},
    ask="Which of the following is the largest population to which the results of the "
        "study can be generalized?",
    frame={"score": "any", "place": "tournament"},
    sample="The {n} trivia teams in the sample",
    subsample="The {m} trivia teams in the sample that practiced for at least {cut} "
              "hours per week",
    nrange=(40, 80), nstep=5),
    dict(rowhead="Hours practiced", colhead="Number of points per round",
         rows=("{cut} to {cut2} hours", "More than {cut2} hours"),
         cols=("{lo} to {mid} points", "{hi} or more points"),
         cut=(2, 4), band=(6, 14)))

_table(Scope(
    key="clinic",
    unit="patients", article="All ",
    dims=(Dim("visits", "post", {
              "high": Val("any", " who attended {hi} or more sessions"),
              "any": Val(None, "")}),
          _place(clinic=Val(None, " at the clinic",
                            "all the patients at a certain clinic")),),
    order=("pre", "unit", "place", "post"),
    draw={"random": "A physiotherapist wanted to study the relationship between the "
                    "number of therapy sessions a patient attends and the number of "
                    "weeks a patient spends recovering. For the study, the "
                    "physiotherapist selected {n} patients at random from {frm}. The "
                    "table displays the information for the {m} patients in the sample "
                    "who recovered in at least {cut} weeks."},
    ask="Which of the following is the largest population to which the results of the "
        "study can be generalized?",
    frame={"visits": "any", "place": "clinic"},
    sample="The {n} patients in the sample",
    subsample="The {m} patients in the sample who recovered in at least {cut} weeks",
    nrange=(50, 90), nstep=5),
    dict(rowhead="Weeks recovering", colhead="Number of sessions attended",
         rows=("{cut} to {cut2} weeks", "More than {cut2} weeks"),
         cols=("{lo} to {mid} sessions", "{hi} or more sessions"),
         cut=(3, 5), band=(4, 10)))

_table(Scope(
    key="bookshop",
    unit="members", article="All ",
    dims=(Dim("spend", "post", {
              "high": Val("any", " who bought {hi} or more books"),
              "any": Val(None, "")}),
          _place(shop=Val(None, " in the reading club",
                          "all the members of a certain reading club")),),
    order=("pre", "unit", "place", "post"),
    draw={"random": "The owner of a bookshop wanted to study the relationship between "
                    "the number of books a member buys in a year and the number of "
                    "club meetings a member attends. For the study, the owner selected "
                    "{n} members at random from {frm}. The table displays the "
                    "information for the {m} members in the sample who attended at "
                    "least {cut} meetings."},
    ask="Which of the following is the largest population to which the results of the "
        "study can be generalized?",
    frame={"spend": "any", "place": "shop"},
    sample="The {n} members in the sample",
    subsample="The {m} members in the sample who attended at least {cut} meetings",
    nrange=(45, 85), nstep=5),
    dict(rowhead="Meetings attended", colhead="Number of books bought",
         rows=("{cut} to {cut2} meetings", "More than {cut2} meetings"),
         cols=("{lo} to {mid} books", "{hi} or more books"),
         cut=(3, 6), band=(5, 12)))
