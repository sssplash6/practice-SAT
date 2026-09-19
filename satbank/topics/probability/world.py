"""Two-way tables: the arithmetic, the English, and the scenarios.

Everything this topic gets wrong, it gets wrong here, so three things are kept
apart on purpose.

**A table is built from its cells and never from its margins.** `Table` takes
the interior counts and *derives* every row total, column total and grand
total by summation. A printed table that does not add up is a question nobody
can answer, and no check in the gate reads a table as arithmetic -- so the
margins are not data a template supplies, they are a consequence of the data
it supplies. `option_check.py` then reads the printed rows back and adds them
up again, from the page, without touching this file.

**An event is a set of cells, not a cell.** `Sel` names a set of row indices
or column indices and the English for it; `Event` is a pair of them; `meet`
intersects two events and `Table.count` adds the cells inside one. Every
probability in this package is `count(meet(event, given)) / count(given)`,
with `given` the whole table when the question is unconditional. There is
nowhere for a template to divide by the wrong total, because no template ever
picks a denominator: it picks a *condition*, and the denominator follows.
P(A|B) and P(B|A) are therefore two different calls with the same cells, and
the wrong one of them is a named distractor rather than a silent bug.

**The scenario owns its English.** A `Ctx` carries the table's labels and, for
each category, four ways a sentence can name it: a noun phrase `n`, a
predicate `p`, a plural subset noun `g`, and a plural predicate `pl`. A
template chooses a frame and fills it; it never invents wording. That is what
lets `option_check.py` find the event in the printed stem by matching against
the printed labels, with no access to the parameters.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ...item import ItemError

__all__ = ["Sel", "Ctx", "Table", "Event", "meet", "cat", "TWO_WAY", "ctx"]


@dataclass(frozen=True)
class Sel:
    """A set of categories along one axis, with the English for naming it.

    `idx` holds one index for a printed category and several for a union the
    stem names in words ("at least 10 years of age"). `label` is what the
    table prints, and is empty for a union, which has no column of its own.
    """
    idx: tuple[int, ...]
    label: str
    n: str                      # "a hybrid car"          -- noun phrase
    p: str                      # "is a hybrid car"       -- predicate, singular
    g: str                      # "hybrid cars"           -- the subset, plural
    pl: str = ""                # "were hybrid cars"      -- predicate, plural

    def plural(self) -> str:
        return self.pl or self.p


def cat(label, n, p, g, pl="") -> Sel:
    """A printed category; its index is filled in when the axis is built."""
    return Sel((), label, n, p, g, pl)


@dataclass(frozen=True)
class Ctx:
    key: str
    intro: str                  # {n} is the grand total
    unit: str                   # "car"
    units: str                  # "cars"
    select: str                 # "If one of these cars is selected at random,"
    subject: str                # "the selected car"
    rows: tuple[Sel, ...]
    cols: tuple[Sel, ...]
    row_head: str = ""
    col_head: str = ""          # a spanning header the source prints, recorded only
    title: str = ""
    lo: int = 4                 # the range a free draw takes its cell counts from
    hi: int = 40
    row_unions: tuple[Sel, ...] = ()
    col_unions: tuple[Sel, ...] = ()
    join: str = "and"

    def row_sels(self) -> tuple[Sel, ...]:
        return self.rows + self.row_unions

    def col_sels(self) -> tuple[Sel, ...]:
        return self.cols + self.col_unions


def _axis(items) -> tuple[Sel, ...]:
    return tuple(Sel((i,), s.label, s.n, s.p, s.g, s.pl) for i, s in enumerate(items))


def _union(idx, n, p, g, pl="") -> Sel:
    return Sel(tuple(idx), "", n, p, g, pl)


# --------------------------------------------------------------- the events

@dataclass(frozen=True)
class Event:
    """A set of table cells: every row in `rows` crossed with every col in `cols`.

    `None` on an axis means "every category", so `Event(None, None)` is the
    whole table -- the condition an unconditional question is asked under.
    """
    rows: tuple[int, ...] | None = None
    cols: tuple[int, ...] | None = None


def meet(a: Event, b: Event) -> Event:
    """The cells both events contain."""
    def both(x, y):
        if x is None:
            return y
        if y is None:
            return x
        return tuple(i for i in x if i in y)
    return Event(both(a.rows, b.rows), both(a.cols, b.cols))


class Table:
    """A two-way table of counts, whose margins are computed and never given."""

    def __init__(self, cells: list[list[int]]):
        if not cells or not cells[0]:
            raise ItemError("a table needs at least one cell")
        w = len(cells[0])
        if any(len(r) != w for r in cells):
            raise ItemError("the rows of a table are not all the same length")
        if any(v < 0 for r in cells for v in r):
            raise ItemError("a count cannot be negative")
        self.cells = [list(r) for r in cells]
        self.nr = len(cells)
        self.nc = w

    # -- margins, every one of them a sum of the cells above or beside it
    def row_total(self, i: int) -> int:
        return sum(self.cells[i])

    def col_total(self, j: int) -> int:
        return sum(self.cells[i][j] for i in range(self.nr))

    @property
    def total(self) -> int:
        return sum(sum(r) for r in self.cells)

    def count(self, ev: Event) -> int:
        rows = range(self.nr) if ev.rows is None else ev.rows
        cols = range(self.nc) if ev.cols is None else ev.cols
        return sum(self.cells[i][j] for i in rows for j in cols)

    def printed(self, ctx: Ctx, margins: bool = True,
                hide: tuple[int, int] | None = None, mark: str = "?") -> list[list[str]]:
        """The rows the page shows, header first.

        Every total here is `row_total`/`col_total`/`total`, which are sums of
        `self.cells`. There is no path by which a margin can be written down
        independently of the cells it totals.
        """
        def body(i, j):
            return mark if hide == (i, j) else f"{self.cells[i][j]:,}"

        head = [ctx.row_head] + [c.label for c in ctx.cols] + (["Total"] if margins else [])
        out = [head]
        for i, r in enumerate(ctx.rows):
            row = [r.label] + [body(i, j) for j in range(self.nc)]
            if margins:
                row.append(f"{self.row_total(i):,}")
            out.append(row)
        if margins:
            out.append(["Total"] + [f"{self.col_total(j):,}" for j in range(self.nc)]
                       + [f"{self.total:,}"])
        return out


# ------------------------------------------------------------- the scenarios

def _ctx(key, intro, unit, units, select, subject, rows, cols, **kw) -> Ctx:
    return Ctx(key, intro, unit, units, select, subject,
               _axis(rows), _axis(cols), **kw)


TWO_WAY: dict[str, Ctx] = {}


def _add(c: Ctx) -> Ctx:
    TWO_WAY[c.key] = c
    return c


def ctx(key: str) -> Ctx:
    if key not in TWO_WAY:
        raise ItemError(f"no two-way scenario named {key!r}")
    return TWO_WAY[key]


_add(_ctx(
    "gas",
    "On Tuesday, a local gas station had {n} customers. The table summarizes whether "
    "or not the customers on Tuesday purchased gasoline, a beverage, both, or neither.",
    "customer", "customers",
    "Based on the data in the table,",
    "a gas station customer selected at random on that day",
    [cat("Gasoline purchased", "a customer who purchased gasoline", "purchased gasoline",
         "customers who purchased gasoline", "purchased gasoline"),
     cat("Gasoline not purchased", "a customer who did not purchase gasoline",
         "did not purchase gasoline", "customers who did not purchase gasoline",
         "did not purchase gasoline")],
    [cat("Beverage purchased", "a customer who purchased a beverage",
         "purchased a beverage", "customers who purchased a beverage",
         "purchased a beverage"),
     cat("Beverage not purchased", "a customer who did not purchase a beverage",
         "did not purchase a beverage", "customers who did not purchase a beverage",
         "did not purchase a beverage")],
    title="Customer Purchases at a Gas Station", lo=10, hi=70))

_add(_ctx(
    "kittens",
    "The data on the coat color and eye color for {n} Himalayan kittens available for "
    "adoption were collected and summarized in the table.",
    "kitten", "kittens",
    "If one of these kittens is selected at random,", "the selected kitten",
    [cat("Cream-tortoiseshell", "a cream-tortoiseshell kitten", "is cream-tortoiseshell",
         "cream-tortoiseshell kittens", "are cream-tortoiseshell"),
     cat("Chocolate", "a chocolate-colored kitten", "is chocolate-colored",
         "chocolate-colored kittens", "are chocolate-colored")],
    [cat("Deep blue", "a kitten with deep blue eyes", "has deep blue eyes",
         "kittens with deep blue eyes", "have deep blue eyes"),
     cat("Light brown", "a kitten with light brown eyes", "has light brown eyes",
         "kittens with light brown eyes", "have light brown eyes")],
    row_head="Coat color", col_head="Eye color", lo=4, hi=30))

_add(_ctx(
    "cars",
    "The table shows information about {n} cars listed for sale on an auto "
    "dealership's website.",
    "car", "cars",
    "If one of the cars listed for sale is selected at random,", "the selected car",
    [cat("Nonhybrid", "a nonhybrid car", "is a nonhybrid car", "nonhybrid cars",
         "are nonhybrid cars"),
     cat("Hybrid", "a hybrid car", "is a hybrid car", "hybrid cars", "are hybrid cars")],
    [cat("Priced at no more than $25,000", "a car priced at no more than $25,000",
         "is priced at no more than $25,000", "cars priced at no more than $25,000",
         "were priced at no more than $25,000"),
     cat("Priced greater than $25,000", "a car priced greater than $25,000",
         "is priced greater than $25,000", "cars priced greater than $25,000",
         "were priced greater than $25,000")],
    row_head="Type of car", title="Prices of the Cars Listed for Sale", lo=2, hi=18))

_add(_ctx(
    "rain",
    "For a science project, Anka recorded whether it rained on each of {n} days. Her "
    "results are summarized in the table.",
    "day", "days",
    "If one of these days is selected at random,", "the selected day",
    [cat("Number of weekdays", "a weekday", "was a weekday", "weekdays", "were weekdays"),
     cat("Number of weekend days", "a weekend day", "was a weekend day", "weekend days",
         "were weekend days")],
    [cat("Rain", "a day on which there was rain", "was a day on which there was rain",
         "days on which there was rain", "were days on which there was rain"),
     cat("No rain", "a day on which there was no rain",
         "was a day on which there was no rain", "days on which there was no rain",
         "were days on which there was no rain")],
    title="Weekday and Weekend Day Rain", lo=6, hi=60))

_add(_ctx(
    "dealership",
    "The table summarizes the {n} customers who visited a car dealership in the last "
    "month by age and by the number of visits they made to the dealership.",
    "customer", "customers",
    "If a customer from the last month is selected at random,", "the selected customer",
    [cat("Less than 40 years old", "a customer less than 40 years old",
         "is less than 40 years old", "customers less than 40 years old",
         "were less than 40 years old"),
     cat("At least 40 years old", "a customer at least 40 years old",
         "is at least 40 years old", "customers at least 40 years old",
         "were at least 40 years old")],
    [cat("1 visit", "a customer who made 1 visit", "made 1 visit",
         "customers who made 1 visit", "made 1 visit"),
     cat("2 or more visits", "a customer who made 2 or more visits",
         "made 2 or more visits", "customers who made 2 or more visits",
         "made 2 or more visits")],
    lo=8, hi=90))

_add(_ctx(
    "parks",
    "The table shows the number of state parks in a certain state that contain camping "
    "facilities and bicycle paths.",
    "state park", "state parks",
    "If one of these state parks is selected at random,", "the selected state park",
    [cat("Has camping facilities", "a state park that has camping facilities",
         "has camping facilities", "state parks that have camping facilities",
         "have camping facilities"),
     cat("Does not have camping facilities",
         "a state park that does not have camping facilities",
         "does not have camping facilities",
         "state parks that do not have camping facilities",
         "do not have camping facilities")],
    [cat("Has bicycle paths", "a state park that has bicycle paths",
         "has bicycle paths", "state parks that have bicycle paths",
         "have bicycle paths"),
     cat("Does not have bicycle paths",
         "a state park that does not have bicycle paths",
         "does not have bicycle paths",
         "state parks that do not have bicycle paths",
         "do not have bicycle paths")],
    join="but", lo=2, hi=24))

_add(_ctx(
    "degrees",
    "The table shows the number of people who work in the Human Resources and "
    "Accounting departments of a company and the highest level of education they have "
    "completed.",
    "person", "people",
    "If a person from one of these departments is chosen at random,", "the person chosen",
    [cat("Bachelor's degree", "a person whose highest level of education is a "
         "bachelor's degree", "has a bachelor's degree as the highest level of "
         "education completed",
         "people whose highest level of education is a bachelor's degree",
         "have a bachelor's degree as the highest level of education completed"),
     cat("Master's degree", "a person whose highest level of education is a "
         "master's degree", "has a master's degree as the highest level of education "
         "completed", "people whose highest level of education is a master's degree",
         "have a master's degree as the highest level of education completed")],
    [cat("Human Resources", "a person who works in the Human Resources department",
         "works in the Human Resources department",
         "people who work in the Human Resources department",
         "work in the Human Resources department"),
     cat("Accounting", "a person who works in the Accounting department",
         "works in the Accounting department",
         "people who work in the Accounting department",
         "work in the Accounting department")],
    lo=2, hi=14))

_add(_ctx(
    "tiles",
    "The table summarizes the distribution of color and shape for {n} tiles of equal "
    "area.",
    "tile", "tiles",
    "If one of these tiles is selected at random,", "the selected tile",
    [cat("Square", "a square tile", "is square", "square tiles", "are square"),
     cat("Pentagon", "a pentagon tile", "is a pentagon", "pentagon tiles",
         "are pentagons")],
    [cat("Red", "a red tile", "is red", "red tiles", "are red"),
     cat("Blue", "a blue tile", "is blue", "blue tiles", "are blue"),
     cat("Yellow", "a yellow tile", "is yellow", "yellow tiles", "are yellow")],
    lo=5, hi=30))

_add(_ctx(
    "flowers",
    "The table shows the distribution of two types of flowers at two different sites.",
    "flower", "flowers",
    "If a flower represented in the table is selected at random,", "the selected flower",
    [cat("Tulip", "a tulip", "is a tulip", "tulips", "are tulips"),
     cat("Daffodil", "a daffodil", "is a daffodil", "daffodils", "are daffodils")],
    [cat("Site A", "a flower from site A", "is from site A", "flowers from site A",
         "are from site A"),
     cat("Site B", "a flower from site B", "is from site B", "flowers from site B",
         "are from site B")],
    lo=8, hi=45))

_add(_ctx(
    "participants",
    "The table summarizes the distribution of age and assigned group for {n} "
    "participants in a study.",
    "participant", "participants",
    "One of these participants will be selected at random.", "the participant",
    [cat("Group A", "a participant from group A", "is from group A",
         "participants from group A", "were from group A"),
     cat("Group B", "a participant from group B", "is from group B",
         "participants from group B", "were from group B"),
     cat("Group C", "a participant from group C", "is from group C",
         "participants from group C", "were from group C")],
    [cat("0–9 years", "a participant less than 10 years of age",
         "is less than 10 years of age", "participants less than 10 years of age",
         "were less than 10 years of age"),
     cat("10–19 years", "a participant from 10 to 19 years of age",
         "is from 10 to 19 years of age", "participants from 10 to 19 years of age",
         "were from 10 to 19 years of age"),
     cat("20+ years", "a participant at least 20 years of age",
         "is at least 20 years of age", "participants at least 20 years of age",
         "were at least 20 years of age")],
    lo=1, hi=22,
    col_unions=(_union((1, 2), "a participant at least 10 years of age",
                       "is at least 10 years of age",
                       "participants at least 10 years of age",
                       "were at least 10 years of age"),
                _union((0, 1), "a participant less than 20 years of age",
                       "is less than 20 years of age",
                       "participants less than 20 years of age",
                       "were less than 20 years of age"))))

_add(_ctx(
    "teens",
    "In a study of cell phone use, {n} randomly selected US teens were asked how often "
    "they talked on a cell phone and about their texting behavior. The data are "
    "summarized in the table.",
    "teen", "teens",
    "If one of the {n} teens surveyed is selected at random,", "the teen",
    [cat("Light", "a light texter", "is a light texter", "light texters",
         "were light texters"),
     cat("Medium", "a medium texter", "is a medium texter", "medium texters",
         "were medium texters"),
     cat("Heavy", "a heavy texter", "is a heavy texter", "heavy texters",
         "were heavy texters")],
    [cat("Talks on cell phone daily", "a teen who talks on a cell phone daily",
         "talks on a cell phone daily", "teens who talk on a cell phone daily",
         "talk on a cell phone daily"),
     cat("Does not talk on cell phone daily",
         "a teen who does not talk on a cell phone daily",
         "does not talk on a cell phone daily",
         "teens who do not talk on a cell phone daily",
         "do not talk on a cell phone daily")],
    row_head="Texting behavior", lo=60, hi=180))

_add(_ctx(
    "penguins",
    "The number of penguins in a zoo exhibit, sorted by gender and type of penguin, is "
    "shown in the table.",
    "penguin", "penguins",
    "If one of these penguins is selected at random,", "the selected penguin",
    [cat("Chinstrap", "a chinstrap penguin", "is a chinstrap penguin",
         "chinstrap penguins", "are chinstrap penguins"),
     cat("Emperor", "an emperor penguin", "is an emperor penguin", "emperor penguins",
         "are emperor penguins"),
     cat("Gentoo", "a gentoo penguin", "is a gentoo penguin", "gentoo penguins",
         "are gentoo penguins"),
     cat("Macaroni", "a macaroni penguin", "is a macaroni penguin", "macaroni penguins",
         "are macaroni penguins")],
    [cat("Male", "a male penguin", "is male", "male penguins", "are male"),
     cat("Female", "a female penguin", "is female", "female penguins", "are female")],
    row_head="Type of penguin", title="Penguin Exhibit", lo=8, hi=60))

_add(_ctx(
    "calls",
    "Employees working for a customer service line at an electric company recorded all "
    "the calls last Monday and noted whether the caller asked for repairs and whether "
    "the caller asked about a bill. The results are summarized in the table.",
    "caller", "callers",
    "If a caller last Monday is selected at random,", "the caller",
    [cat("Asked about a bill", "a caller who asked about a bill",
         "asked about a bill", "callers who asked about a bill", "asked about a bill"),
     cat("Did not ask about a bill", "a caller who did not ask about a bill",
         "did not ask about a bill", "callers who did not ask about a bill",
         "did not ask about a bill")],
    [cat("Asked for repairs", "a caller who asked for repairs", "asked for repairs",
         "callers who asked for repairs", "asked for repairs"),
     cat("Did not ask for repairs", "a caller who did not ask for repairs",
         "did not ask for repairs", "callers who did not ask for repairs",
         "did not ask for repairs")],
    lo=40, hi=700))

_add(_ctx(
    "taxes",
    "The table shows the distribution of US states according to whether they have a "
    "state-level sales tax and a state-level income tax.",
    "state", "states",
    "If one of these states is selected at random,", "the selected state",
    [cat("State income tax", "a state that has a state-level income tax",
         "has a state-level income tax", "states that have a state-level income tax",
         "have a state-level income tax"),
     cat("No state income tax", "a state that does not have a state-level income tax",
         "does not have a state-level income tax",
         "states that do not have a state-level income tax",
         "do not have a state-level income tax")],
    [cat("State sales tax", "a state that has a state-level sales tax",
         "has a state-level sales tax", "states that have a state-level sales tax",
         "have a state-level sales tax"),
     cat("No state sales tax", "a state that does not have a state-level sales tax",
         "does not have a state-level sales tax",
         "states that do not have a state-level sales tax",
         "do not have a state-level sales tax")],
    title="State-Level Taxes", lo=1, hi=40))

_add(_ctx(
    "gardens",
    "A gardener recorded, for each of {n} seedlings, whether the seedling was grown "
    "under a lamp and whether it flowered. The results are summarized in the table.",
    "seedling", "seedlings",
    "If one of these seedlings is selected at random,", "the selected seedling",
    [cat("Grown under a lamp", "a seedling grown under a lamp", "was grown under a lamp",
         "seedlings grown under a lamp", "were grown under a lamp"),
     cat("Not grown under a lamp", "a seedling not grown under a lamp",
         "was not grown under a lamp", "seedlings not grown under a lamp",
         "were not grown under a lamp")],
    [cat("Flowered", "a seedling that flowered", "flowered",
         "seedlings that flowered", "flowered"),
     cat("Did not flower", "a seedling that did not flower", "did not flower",
         "seedlings that did not flower", "did not flower")],
    lo=5, hi=50))

_add(_ctx(
    "commute",
    "A company asked each of its {n} employees how they travel to work and whether "
    "they work on weekends. The responses are summarized in the table.",
    "employee", "employees",
    "If one of these employees is selected at random,", "the selected employee",
    [cat("Travels by bus", "an employee who travels by bus", "travels by bus",
         "employees who travel by bus", "travel by bus"),
     cat("Travels by car", "an employee who travels by car", "travels by car",
         "employees who travel by car", "travel by car"),
     cat("Travels by bicycle", "an employee who travels by bicycle",
         "travels by bicycle", "employees who travel by bicycle",
         "travel by bicycle")],
    [cat("Works weekends", "an employee who works on weekends", "works on weekends",
         "employees who work on weekends", "work on weekends"),
     cat("Does not work weekends", "an employee who does not work on weekends",
         "does not work on weekends", "employees who do not work on weekends",
         "do not work on weekends")],
    lo=6, hi=55))

_add(_ctx(
    "internships",
    "The table shows the number of students from two different high schools who "
    "completed summer internships in each of five years. No student attended both "
    "schools.",
    "student", "students",
    "If one of these students is selected at random,", "the selected student",
    [cat("Foothill", "a student from Foothill High School",
         "was from Foothill High School", "students from Foothill High School",
         "were from Foothill High School"),
     cat("Valley", "a student from Valley High School", "was from Valley High School",
         "students from Valley High School", "were from Valley High School")],
    [cat("2008", "a student who completed an internship in 2008",
         "completed a summer internship in 2008",
         "students who completed a summer internship in 2008",
         "completed a summer internship in 2008"),
     cat("2009", "a student who completed an internship in 2009",
         "completed a summer internship in 2009",
         "students who completed a summer internship in 2009",
         "completed a summer internship in 2009"),
     cat("2010", "a student who completed an internship in 2010",
         "completed a summer internship in 2010",
         "students who completed a summer internship in 2010",
         "completed a summer internship in 2010"),
     cat("2011", "a student who completed an internship in 2011",
         "completed a summer internship in 2011",
         "students who completed a summer internship in 2011",
         "completed a summer internship in 2011"),
     cat("2012", "a student who completed an internship in 2012",
         "completed a summer internship in 2012",
         "students who completed a summer internship in 2012",
         "completed a summer internship in 2012")],
    row_head="High school", col_head="Year",
    title="Number of High School Students Who Completed Summer Internships",
    lo=30, hi=95,
    col_unions=(_union((0, 1), "a student who completed an internship before 2010",
                       "completed a summer internship before 2010",
                       "students who completed a summer internship before 2010",
                       "completed a summer internship before 2010"),
                _union((3, 4), "a student who completed an internship after 2010",
                       "completed a summer internship after 2010",
                       "students who completed a summer internship after 2010",
                       "completed a summer internship after 2010"))))

_add(_ctx(
    "contestants",
    "The same {r} contestants, on each of 3 days, answered 5 questions in order to win "
    "a prize. Each contestant received 1 point for each correct answer. The number of "
    "contestants receiving a given score on each day is shown in the table. No "
    "contestant received the same score on two different days.",
    "contestant", "contestants",
    "If a contestant is selected at random,", "the selected contestant",
    [cat("Day 1", "a contestant who received that score on Day 1",
         "received that score on Day 1", "contestants who received that score on Day 1",
         "received that score on Day 1"),
     cat("Day 2", "a contestant who received that score on Day 2",
         "received that score on Day 2", "contestants who received that score on Day 2",
         "received that score on Day 2"),
     cat("Day 3", "a contestant who received that score on Day 3",
         "received that score on Day 3", "contestants who received that score on Day 3",
         "received that score on Day 3")],
    [cat("5 out of 5", "a contestant who scored 5 out of 5",
         "received a score of 5 out of 5",
         "contestants who received a score of 5 out of 5",
         "received a score of 5 out of 5"),
     cat("4 out of 5", "a contestant who scored 4 out of 5",
         "received a score of 4 out of 5",
         "contestants who received a score of 4 out of 5",
         "received a score of 4 out of 5"),
     cat("3 out of 5", "a contestant who scored 3 out of 5",
         "received a score of 3 out of 5",
         "contestants who received a score of 3 out of 5",
         "received a score of 3 out of 5"),
     cat("2 out of 5", "a contestant who scored 2 out of 5",
         "received a score of 2 out of 5",
         "contestants who received a score of 2 out of 5",
         "received a score of 2 out of 5"),
     cat("1 out of 5", "a contestant who scored 1 out of 5",
         "received a score of 1 out of 5",
         "contestants who received a score of 1 out of 5",
         "received a score of 1 out of 5"),
     cat("0 out of 5", "a contestant who scored 0 out of 5",
         "received a score of 0 out of 5",
         "contestants who received a score of 0 out of 5",
         "received a score of 0 out of 5")],
    title="Number of Contestants by Score and Day", lo=1, hi=8,
    row_unions=(_union((1, 2), "a contestant who received that score on Day 2 or Day 3",
                       "received that score on Day 2 or Day 3",
                       "contestants who received that score on Day 2 or Day 3",
                       "received that score on Day 2 or Day 3"),
                _union((0, 1), "a contestant who received that score on Day 1 or Day 2",
                       "received that score on Day 1 or Day 2",
                       "contestants who received that score on Day 1 or Day 2",
                       "received that score on Day 1 or Day 2"))))

_add(_ctx(
    "blood",
    "Human blood can be classified into four common blood types—A, B, AB, and O. It "
    "is also characterized by the presence (+) or absence (−) of the rhesus factor. "
    "The table shows the distribution of blood type and rhesus factor for a group of "
    "people.",
    "person", "people",
    "If one of these people is chosen at random,", "the person chosen",
    [cat("Positive (+)", "a person who is rhesus positive (+)", "is rhesus positive (+)",
         "people who are rhesus positive (+)", "are rhesus positive (+)"),
     cat("Negative (−)", "a person who is rhesus negative (−)",
         "is rhesus negative (−)", "people who are rhesus negative (−)",
         "are rhesus negative (−)")],
    [cat("Type A", "a person with blood type A", "has blood type A",
         "people with blood type A", "have blood type A"),
     cat("Type B", "a person with blood type B", "has blood type B",
         "people with blood type B", "have blood type B"),
     cat("Type AB", "a person with blood type AB", "has blood type AB",
         "people with blood type AB", "have blood type AB"),
     cat("Type O", "a person with blood type O", "has blood type O",
         "people with blood type O", "have blood type O")],
    row_head="Rhesus factor", col_head="Blood type", lo=2, hi=40,
    col_unions=(_union((0, 1), "a person with blood type A or blood type B",
                       "has blood type A or blood type B",
                       "people with blood type A or blood type B",
                       "have blood type A or blood type B"),)))


def _with_unions(key, rows=(), cols=()):
    """Give a scenario that was written without unions the ones its axis allows."""
    c = TWO_WAY[key]
    TWO_WAY[key] = Ctx(c.key, c.intro, c.unit, c.units, c.select, c.subject, c.rows,
                       c.cols, c.row_head, c.col_head, c.title, c.lo, c.hi,
                       c.row_unions + tuple(rows), c.col_unions + tuple(cols), c.join)


_with_unions("tiles", cols=[
    _union((0, 1), "a red tile or a blue tile", "is red or blue",
           "tiles that are red or blue", "are red or blue"),
    _union((1, 2), "a blue tile or a yellow tile", "is blue or yellow",
           "tiles that are blue or yellow", "are blue or yellow")])

_with_unions("teens", rows=[
    _union((1, 2), "a medium or heavy texter", "is a medium or heavy texter",
           "medium and heavy texters", "were medium or heavy texters"),
    _union((0, 1), "a light or medium texter", "is a light or medium texter",
           "light and medium texters", "were light or medium texters")])

_with_unions("penguins", rows=[
    _union((0, 2), "a chinstrap or gentoo penguin", "is a chinstrap or gentoo penguin",
           "chinstrap and gentoo penguins", "are chinstrap or gentoo penguins"),
    _union((1, 3), "an emperor or macaroni penguin", "is an emperor or macaroni penguin",
           "emperor and macaroni penguins", "are emperor or macaroni penguins")])

_with_unions("commute", rows=[
    _union((0, 2), "an employee who travels by bus or by bicycle",
           "travels by bus or by bicycle", "employees who travel by bus or by bicycle",
           "travel by bus or by bicycle")])

_add(_ctx(
    "sports_survey",
    "A survey taken by {n} students at a school asked whether they played school "
    "sports. The table summarizes all {n} responses from the students surveyed.",
    "student", "students",
    "If one of these students is selected at random,", "the selected student",
    [cat("Play a school sport", "a student who plays a school sport",
         "plays a school sport", "students who play a school sport",
         "play a school sport"),
     cat("Do not play a school sport", "a student who does not play a school sport",
         "does not play a school sport",
         "students who do not play a school sport", "do not play a school sport")],
    [cat("Males", "a male student", "is male", "males surveyed", "are male"),
     cat("Females", "a female student", "is female", "females surveyed",
         "are female")],
    lo=120, hi=400))

_add(_ctx(
    "sports",
    "A school recorded the sport played by each of its {n} athletes.",
    "athlete", "athletes",
    "If one of these athletes is selected at random,", "the selected athlete",
    [cat("Soccer", "a soccer player", "plays soccer", "soccer players",
         "play soccer"),
     cat("Rowing", "an athlete who competes in rowing", "competes in rowing",
         "athletes who compete in rowing", "compete in rowing"),
     cat("Track", "a track athlete", "runs track", "track athletes", "run track"),
     cat("Swimming", "an athlete who competes in swimming",
         "competes in swimming", "athletes who compete in swimming",
         "compete in swimming")],
    [cat("First year", "a first-year athlete", "is in the first year",
         "first-year athletes", "are in the first year"),
     cat("Returning", "a returning athlete", "is returning", "returning athletes",
         "are returning")],
    row_head="Sport", lo=8, hi=70,
    row_unions=(_union((0, 2), "a soccer player or a track athlete",
                       "plays soccer or runs track",
                       "soccer players and track athletes",
                       "play soccer or run track"),)))

_add(_ctx(
    "grove",
    "A botanist recorded the species and the site of each of the {n} trees in a "
    "survey.",
    "tree", "trees",
    "If one of these trees is selected at random,", "the selected tree",
    [cat("Maple", "a maple", "is a maple", "maples", "are maples"),
     cat("Birch", "a birch", "is a birch", "birches", "are birches"),
     cat("Alder", "an alder", "is an alder", "alders", "are alders"),
     cat("Willow", "a willow", "is a willow", "willows", "are willows")],
    [cat("North site", "a tree at the north site", "is at the north site",
         "trees at the north site", "are at the north site"),
     cat("South site", "a tree at the south site", "is at the south site",
         "trees at the south site", "are at the south site")],
    row_head="Species", lo=6, hi=60,
    row_unions=(_union((1, 3), "a birch or a willow", "is a birch or a willow",
                       "birches and willows", "are birches or willows"),)))
