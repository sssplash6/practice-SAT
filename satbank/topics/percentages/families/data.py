"""Percents read off a table, and the one item whose options are sentences.

A table changes what the mistake is. The arithmetic is the same division it
always was, but the student now has to choose a denominator, and the wrong
denominator is right there in the table: the column total, the grand total,
the count itself. Those three are the options.

    table_share     counts in a table -> a percent of the right total
    percent_table   percents in a table -> a count out of a stated total
    series_change   a value per year -> the percent between two of them
    conclusion      percentages of a vote -> which statement they support
"""

from __future__ import annotations

import random

from ....item import Item, ItemError
from ....plot import line_graph
from ..values import (Q, dec, mcq, pick, places_needed, q, snap, spr,
                      text_mcq, unambiguous)

__all__ = ["table_share", "percent_table", "series_change", "conclusion"]


# --------------------------------------------------------------- scenarios

CALLS = {
    "key": "calls",
    "title": "Call Ratings",
    "rows": ["Employee A", "Employee B", "Employee C", "Employee D"],
    "cols": ["1 Star", "2 Stars", "3 Stars", "4 Stars"],
    "colref": ["a rating of 1 star", "a rating of 2 stars", "a rating of 3 stars",
               "a rating of 4 stars"],
    "unit": "calls",
    "own": "{row}'s calls",
    "verb": "received",
    "lead": ("A supervisor at a call center reviewed {total} calls taken by four "
             "employees and rated the employees' performance on each call on a scale "
             "from 1 star to 4 stars. The ratings for each employee are shown in the "
             "table above."),
    "groupable": False,
}

CLIMATE = {
    "key": "climate",
    "title": "Climate Preferences",
    "rows": ["18-35 years old", "36-50 years old", "51-65 years old",
             "Greater than 65 years old"],
    "cols": ["Warm", "Cool", "No preference"],
    "colref": ['a preference for "warm"', 'a preference for "cool"', "no preference"],
    "unit": "responses",
    "own": "adults {row}",
    "verb": "responded with",
    "lead": ("In a survey, a randomly chosen sample of {total} adults aged 18 years or "
             "greater was asked about their preference to live in a warm climate or a "
             "cool climate. The table above displays a summary of the survey results."),
    "groupable": True,
    "groups": ("adults aged 18-50 years", "adults aged 51 years or greater"),
}

COMMUTE = {
    "key": "commute",
    "title": "How Employees Travel to Work",
    "rows": ["Branch W", "Branch X", "Branch Y", "Branch Z"],
    "cols": ["Car", "Bus", "Bicycle", "On foot"],
    "colref": ["travelling by car", "travelling by bus", "travelling by bicycle",
               "travelling on foot"],
    "unit": "employees",
    "own": "the employees at {row}",
    "verb": "reported",
    "lead": ("A company surveyed all {total} of its employees about how they travel to "
             "work. The responses from each branch are shown in the table above."),
    "groupable": False,
}

TWO_WAY = [CALLS, CLIMATE, COMMUTE]

ONE_WAY = [("Group", ["A", "B", "C", "D"], "objects"),
           ("Site", ["I", "II", "III", "IV"], "specimens"),
           ("Lot", ["1", "2", "3", "4"], "parcels"),
           ("Batch", ["P", "Q", "R", "S"], "castings")]


def _grid(rng, nrows, ncols, lo, hi):
    return [[rng.randrange(lo, hi) for _ in range(ncols)] for _ in range(nrows)]


def _table(rows, cols, counts, corner="", totals_col=True):
    header = [corner] + list(cols) + (["Total"] if totals_col else [])
    out = [header]
    for i, label in enumerate(rows):
        line = [label] + [f"{c:,}" for c in counts[i]]
        if totals_col:
            line.append(f"{sum(counts[i]):,}")
        out.append(line)
    foot = ["Total"] + [f"{sum(counts[i][j] for i in range(len(rows))):,}"
                        for j in range(len(cols))]
    if totals_col:
        foot.append(f"{sum(sum(r) for r in counts):,}")
    out.append(foot)
    return out


# -------------------------------------------------------------- TABLE SHARE

def table_share(rng: random.Random, seed: int, *, scenario=None, counts=None, ask=None,
                row=None, col=None, rows_a=None, rows_b=None, fmt=None, places=None,
                ctx=None, wrongs=None) -> Item:
    """A percent whose denominator the student has to pick out of the table."""
    ask = ask or rng.choices(["row_share", "ratio", "group_diff"], weights=[4, 3, 3])[0]

    if ask == "ratio":
        word, labels, noun = ctx or rng.choice(ONE_WAY)
        counts = counts or [[rng.randrange(30, 900)] for _ in labels]
        ia = rows_a if rows_a is not None else rng.randrange(len(labels))
        ib = rows_b if rows_b is not None else rng.choice(
            [i for i in range(len(labels)) if i != ia])
        a, b = q(counts[ia][0]), q(counts[ib][0])
        key = 100 * a / b
        total = sum(c[0] for c in counts)
        table = [[word, f"Number of {noun}"]]
        table += [[labels[i], f"{counts[i][0]:,}"] for i in range(len(labels))]
        table.append(["Total", f"{total:,}"])
        stem = (f"The table summarizes the number of {noun} in each {word.lower()}. The "
                f"number of {noun} in {word.lower()} {labels[ib]} is p% of the number of "
                f"{noun} in {word.lower()} {labels[ia]}. What is the value of p ?")
        a, b = b, a                                   # the item names the base second
        key = 100 * a / b
        if places is None and places_needed(key, 6) > 2:
            raise ItemError("this percent does not print in two decimals")
        if places is not None:
            key = snap(key, Q(1, 10) ** places)
        pool = {
            "inverted": ("divided the two counts the other way round", 100 * b / a),
            "difference": ("subtracted the two counts and read the difference as the "
                           "percent", abs(a - b) if abs(a - b) <= 400 else None),
            "against_the_table": (f"compared {word.lower()} {labels[ib]} with the whole "
                                  f"table instead of with {word.lower()} {labels[ia]}",
                                  100 * a / total),
            "excess": ("found the percent by which one count exceeds the other, not the "
                       "percent it is of it", 100 * abs(a - b) / b),
        }
        order = ["inverted", "difference", "against_the_table", "excess"]
        rationale = (f"{dec(a, 0)}/{dec(b, 0)} = {dec(key / 100, places_needed(key / 100, 6))}, "
                     f"so p = {dec(key, places_needed(key, 4))}.")
        P = {"kind": "pct_table", "ask": "ratio", "a": float(a), "b": float(b),
             "total": float(total), "round": float(places) if places is not None else None}
        style, difficulty = "plain", "medium"
    else:
        sc = scenario if isinstance(scenario, dict) else (
            {"calls": CALLS, "climate": CLIMATE, "commute": COMMUTE}[scenario]
            if scenario else rng.choice(TWO_WAY))
        if ask == "group_diff" and not sc["groupable"]:
            sc = CLIMATE
        rows, cols = sc["rows"], sc["cols"]
        counts = counts or _grid(rng, len(rows), len(cols), 20, 300)
        row_tot = [sum(r) for r in counts]
        col_tot = [sum(counts[i][j] for i in range(len(rows))) for j in range(len(cols))]
        grand = sum(row_tot)
        table = _table(rows, cols, counts)
        lead = sc["lead"].format(total=f"{grand:,}")

        if ask == "row_share":
            i = row if row is not None else rng.randrange(len(rows))
            j = col if col is not None else rng.randrange(len(cols))
            places = 0 if places is None else places
            key = unambiguous(100 * q(counts[i][j]) / row_tot[i], 1)
            who = sc["own"].format(row=rows[i])
            stem = (f"{lead} According to the table, to the nearest whole percent, what "
                    f"percent of {who} {sc['verb']} {sc['colref'][j]}?")
            pool = {
                "grand_total": ("divided by the total for the whole table instead of by "
                                f"the total for {rows[i]}", 100 * q(counts[i][j]) / grand),
                "cell_as_percent": ("read the count in the cell as the percent",
                                    q(counts[i][j]) if counts[i][j] <= 150 else None),
                "column_total": (f"divided by the total for the {cols[j]} column instead "
                                 f"of by the total for {rows[i]}",
                                 100 * q(counts[i][j]) / col_tot[j]),
                "row_of_table": (f"gave {rows[i]}'s share of the whole table rather than "
                                 "the share asked about", 100 * q(row_tot[i]) / grand),
            }
            order = ["grand_total", "cell_as_percent", "column_total", "row_of_table"]
            rationale = (f"{counts[i][j]:,} of {rows[i]}'s {row_tot[i]:,} {sc['unit']} is "
                         f"{dec(100 * q(counts[i][j]) / row_tot[i], 2)}%, which is "
                         f"{dec(key, 0)}% to the nearest whole percent.")
            P = {"kind": "pct_table", "ask": "row_share", "cell": counts[i][j],
                 "row_total": row_tot[i], "col_total": col_tot[j], "grand": grand,
                 "round": 0.0}
            difficulty = "easy"
        else:                                                  # group_diff
            ga = rows_a if rows_a is not None else [0, 1]
            gb = rows_b if rows_b is not None else [2, 3]
            j = col if col is not None else 0
            places = 0 if places is None else places
            a_cell = sum(counts[i][j] for i in ga)
            b_cell = sum(counts[i][j] for i in gb)
            a_tot = sum(row_tot[i] for i in ga)
            b_tot = sum(row_tot[i] for i in gb)
            pa, pb = 100 * q(a_cell) / a_tot, 100 * q(b_cell) / b_tot
            key = unambiguous(abs(pa - pb), 1)
            if key == 0:
                raise ItemError("the two groups answer at the same rate")
            g1, g2 = sc["groups"]
            stem = (f"{lead} Which of the following is closest to the difference between "
                    f"the percentage of {g1} who responded with {sc['colref'][j]} and the "
                    f"percentage of {g2} who responded with {sc['colref'][j]}?")
            pool = {
                "both_over_grand": ("divided both counts by the total for the whole table "
                                    "instead of by each group's own total",
                                    snap(abs(100 * q(a_cell) / grand
                                             - 100 * q(b_cell) / grand), 1)),
                "diff_over_column": ("divided the difference in the counts by the column "
                                     "total",
                                     snap(100 * q(abs(a_cell - b_cell)) / col_tot[j], 1)),
                "larger_share": ("gave the larger of the two percentages rather than the "
                                 "difference", snap(max(pa, pb), 1)),
                "shares_added": ("added the two percentages instead of subtracting them",
                                 snap(pa + pb, 1)),
            }
            order = ["both_over_grand", "diff_over_column", "larger_share", "shares_added"]
            rationale = (f"{a_cell:,}/{a_tot:,} = {dec(pa, 2)}% and {b_cell:,}/{b_tot:,} = "
                         f"{dec(pb, 2)}%, a difference of {dec(abs(pa - pb), 2)}%.")
            P = {"kind": "pct_table", "ask": "group_diff", "a_cell": a_cell,
                 "a_total": a_tot, "b_cell": b_cell, "b_total": b_tot,
                 "col_total": col_tot[j], "grand": grand, "round": 0.0}
            difficulty = "hard"
        style = "percent"

    mistakes = pick(pool, order, wrongs)
    fmt = fmt or ("spr" if ask == "ratio" and rng.random() < 0.6 else "mcq")
    if fmt == "spr":
        return spr("pct.table_share", "a percent read from a table", difficulty, seed,
                   stem, key, rationale, mistakes=mistakes, params=P, table=table)
    return mcq("pct.table_share", "a percent read from a table", difficulty, seed, stem,
               key, mistakes, rng, rationale, style=style, places=places, params=P,
               table=table)


# ------------------------------------------------------------ PERCENT TABLE

SURVEYS = [
    {"title": "Where Do People Get Most of Their Medical Information?",
     "head": ["Source", "Percent of those surveyed"],
     "cats": ["Doctor", "Internet", "Magazines/brochures", "Pharmacy", "Television",
              "Other/none of the above"],
     "lead": "The table above shows a summary of {total} responses to a survey question.",
     "ask": "how many of those surveyed get most of their medical information from {cats}",
     "neg": "how many of those surveyed do not get most of their medical information from "
            "{cats}",
     "join": {"Doctor": "a doctor", "Internet": "the Internet",
              "Magazines/brochures": "a magazine or a brochure", "Pharmacy": "a pharmacy",
              "Television": "television", "Other/none of the above": "some other source"}},
    {"title": "How Residents Travel to the City Center",
     "head": ["Mode", "Percent of those surveyed"],
     "cats": ["Car", "Bus", "Train", "Bicycle", "On foot", "Other"],
     "lead": "The table above summarizes the responses of {total} residents to a survey.",
     "ask": "how many of those surveyed travel to the city center by {cats}",
     "neg": "how many of those surveyed do not travel to the city center by {cats}",
     "join": {"Car": "car", "Bus": "bus", "Train": "train", "Bicycle": "bicycle",
              "On foot": "walking", "Other": "some other means"}},
    {"title": "Reasons Given for Visiting the Library",
     "head": ["Reason", "Percent of those surveyed"],
     "cats": ["Borrowing books", "Using a computer", "Studying", "Attending an event",
              "Meeting people", "Other"],
     "lead": "The table above shows a summary of {total} responses to a survey question.",
     "ask": "how many of those surveyed gave {cats} as their reason for visiting",
     "neg": "how many of those surveyed did not give {cats} as their reason for visiting",
     "join": {"Borrowing books": "borrowing books", "Using a computer": "using a computer",
              "Studying": "studying", "Attending an event": "attending an event",
              "Meeting people": "meeting people", "Other": "some other reason"}},
]


def percent_table(rng: random.Random, seed: int, *, survey=None, pcts=None, total=None,
                  picks=None, fmt=None, ask=None) -> Item:
    """The table holds percents; the item wants a count out of a stated total."""
    sc = survey if isinstance(survey, dict) else SURVEYS[survey or 0] if survey is not None \
        else rng.choice(SURVEYS)
    cats = sc["cats"]
    if pcts is None:
        while True:
            pcts = [rng.randrange(1, 45) for _ in cats[:-1]]
            if 40 < sum(pcts) < 97:
                break
        pcts.append(100 - sum(pcts))
    pcts = [q(p) for p in pcts]
    if sum(pcts) != 100:
        raise ItemError("the percentages in the table have to total 100")
    total = q(total if total is not None else rng.randrange(400, 5000, 100))
    ask = ask or rng.choice(["two", "two", "one", "neither"])
    picks = picks or (rng.sample(range(len(cats)), 2) if ask != "one"
                      else [rng.randrange(len(cats))])
    share = sum(pcts[i] for i in picks)
    key = total * share / 100 if ask != "neither" else total * (100 - share) / 100
    if key.denominator != 1 or key <= 0:
        raise ItemError("a count of people has to come out whole")

    named = " or ".join(sc["join"][cats[i]] for i in picks)
    if len(picks) > 1:
        named = "either " + named
    body = (sc["neg"] if ask == "neither" else sc["ask"]).format(cats=named)
    stem = sc["lead"].format(total=dec(total, 0)) + " Based on the table, " + body + "?"

    table = [list(sc["head"])] + [[cats[i], dec(pcts[i], places_needed(pcts[i])) + "%"]
                                 for i in range(len(cats))]
    P = {"kind": "pct_percent_table", "pcts": [float(p) for p in pcts],
         "total": float(total), "picks": list(picks), "ask": ask}
    first = picks[0]
    shown = share if ask != "neither" else 100 - share
    mistakes = [
        ("gave the percentage rather than the number of people it stands for", shown),
        ("found the people the question leaves out rather than the people it asks about",
         total * (100 - share) / 100 if ask != "neither" else total * share / 100),
    ]
    if len(picks) > 1:
        mistakes = [(f"used the {cats[first]} row alone", total * pcts[first] / 100),
                    ("multiplied the two percentages instead of adding them",
                     snap(total * pcts[picks[0]] * pcts[picks[-1]] / 10000, 1))] + mistakes
    else:
        mistakes += [("moved the decimal point one place when converting the percent",
                      snap(total * pcts[first] / 1000, 1)),
                     ("subtracted the percent from the total as though it were a count",
                      total - pcts[first])]
    rationale = (f"{dec(share if ask != 'neither' else 100 - share, places_needed(share))}% "
                 f"of {dec(total, 0)} is {dec(key, 0)}.")
    fmt = fmt or ("spr" if rng.random() < 0.2 else "mcq")
    if fmt == "spr":
        return spr("pct.percent_table", "a count from a table of percents", "easy", seed,
                   stem, key, rationale, mistakes=mistakes, params=P, table=table)
    return mcq("pct.percent_table", "a count from a table of percents", "easy", seed,
               stem, key, mistakes, rng, rationale, params=P, table=table)


# ------------------------------------------------------------ SERIES CHANGE

SERIES_CTX = [
    {"what": "the US minimum wage", "head": ["Year", "US minimum wage (dollars per hour)"],
     "noun": "minimum wage", "places": 2, "period": "years", "mono": True},
    {"what": "the average price of a movie ticket",
     "head": ["Year", "Average ticket price (dollars)"], "noun": "average ticket price",
     "places": 2, "period": "years", "mono": True},
    {"what": "the number of nesting pairs recorded on an island",
     "head": ["Year", "Nesting pairs"], "noun": "number of nesting pairs", "places": 0,
     "period": "years", "mono": False},
    {"what": "the annual rainfall recorded at a weather station",
     "head": ["Year", "Rainfall (inches)"], "noun": "annual rainfall", "places": 0,
     "period": "years", "mono": False},
]

# The same series, drawn rather than tabulated. A line graph carries a value
# per year for a dozen years and prints only the two the question turns on, so
# the reader takes those two off the labels and the rest of the curve is
# context. `places` is 0 throughout: a graph is read off gridlines.
GRAPHED = [
    {"what": "the total amount of snow, in inches, recorded each year in Washington, DC,",
     "ylabel": "Annual snowfall (inches)", "noun": "annual snowfall", "places": 0},
    {"what": "the number of rainy days recorded each year at a weather station",
     "ylabel": "Rainy days", "noun": "number of rainy days", "places": 0},
    {"what": "the number of nesting pairs counted each year on an island",
     "ylabel": "Nesting pairs", "noun": "number of nesting pairs", "places": 0},
    {"what": "the number of building permits issued each year in a county",
     "ylabel": "Building permits issued", "noun": "number of building permits issued",
     "places": 0},
    {"what": "the number of manatees counted each year in a coastal survey",
     "ylabel": "Manatees counted", "noun": "number of manatees counted", "places": 0},
]

SOLD = [("an online news service", "subscriptions", "the service"),
        ("a garden center", "rose bushes", "the center"),
        ("a bicycle shop", "touring bicycles", "the shop"),
        ("a theater company", "season tickets", "the company")]


def series_change(rng: random.Random, seed: int, *, values=None, start_year=None,
                  step=None, i=None, j=None, ask=None, fmt=None, places=None, ctx=None,
                  multiple=None, wrongs=None, show=None) -> Item:
    """A value per year, and the percent between two of the years."""
    ask = ask or rng.choices(["change", "project"], weights=[3, 2])[0]

    if ask == "project":
        who, thing, short = ctx or rng.choice(SOLD)
        y0 = start_year or rng.choice([2009, 2011, 2012, 2014, 2016])
        multiple = multiple or rng.choice([2, 2, 3])
        v0 = q(values[0] if values else rng.randrange(10, 60) * 200)
        rate = q(rng.choice([Q(1, 20), Q(1, 10), Q(3, 20), Q(1, 5), Q(1, 4)]))
        v1 = q(values[1] if values else v0 * (1 + rate))
        d = v1 - v0
        r = d / v0
        key = v1 * (1 + r / multiple)
        if v1.denominator != 1 or key.denominator != 1:
            raise ItemError("a number of things sold has to come out whole")
        word = {2: "double", 3: "triple"}[multiple]
        table = [["Year", f"{thing.capitalize()} sold"], [str(y0), dec(v0, 0)],
                 [str(y0 + 1), dec(v1, 0)]]
        stem = (f"The manager of {who} received the report above on the number of {thing} "
                f"sold by {short}. The manager estimated that the percent increase from "
                f"{y0} to {y0 + 1} would be {word} the percent increase from {y0 + 1} to "
                f"{y0 + 2}. How many {thing} did the manager expect would be sold in "
                f"{y0 + 2}?")
        pool = {
            "share_of_the_rise": (f"added {'half' if multiple == 2 else 'a third'} of the "
                                  f"previous rise in {thing} instead of "
                                  f"{'half' if multiple == 2 else 'a third'} of the "
                                  "percent increase", v1 + d / multiple),
            "multiplied_the_rate": (f"{word}d the percent increase instead of dividing it "
                                    f"by {multiple}", v1 * (1 + r * multiple)),
            "multiples_of_the_rise": (f"added {multiple} times the previous rise in "
                                      f"{thing}", v1 + multiple * d),
            "same_rate_again": ("used the same percent increase again", v1 * (1 + r)),
        }
        order = ["share_of_the_rise", "multiplied_the_rate", "multiples_of_the_rise",
                 "same_rate_again"]
        mistakes = pick(pool, order, wrongs)
        rationale = (f"The increase from {y0} to {y0 + 1} is "
                     f"{dec(100 * r, places_needed(100 * r, 4))}%, so the next increase is "
                     f"{dec(100 * r / multiple, places_needed(100 * r / multiple, 4))}%: "
                     f"{dec(v1, 0)} x "
                     f"{dec(1 + r / multiple, places_needed(1 + r / multiple, 6))} = "
                     f"{dec(key, places_needed(key, 4))}.")
        P = {"kind": "pct_series", "ask": "project", "v0": float(v0), "v1": float(v1),
             "multiple": multiple, "round": float(places) if places is not None else None}
        return _finish_series(rng, seed, stem, key, mistakes, rationale, P, table, fmt,
                              places, "plain", "hard")

    if isinstance(ctx, dict):                    # a source item names its own context
        sc, graph = ctx, "ylabel" in ctx
    else:
        graph = (show or rng.choices(["table", "graph"], weights=[3, 1])[0]) == "graph"
        sc = rng.choice(GRAPHED if graph else SERIES_CTX)
    step = step or (1 if graph else rng.choice([1, 5, 10]))
    unit = Q(1) if sc["places"] == 0 else Q(1, 100)
    mono = sc.get("mono", False)
    if values is None:
        # the two years the question names are pinned to an exact ratio, so the
        # percent between them prints in two decimals; the other years wander,
        # except in a series that only ever rises
        n = rng.choice([9, 11, 13]) if graph else rng.choice([4, 5, 6, 6])
        # on a graph the two printed labels have to stand clear of each other,
        # so the years they name are several apart; a table can name any two
        i = (rng.randrange(n - 4) if graph else rng.randrange(n - 1)) if i is None else i
        j = (i + rng.choice([3, 4]) if graph else i + 1) if j is None else j
        choices = ([Q(21, 20), Q(11, 10), Q(5, 4), Q(3, 2), Q(8, 5), 2] if mono
                   else [Q(1, 2), Q(4, 5), Q(9, 10), Q(19, 20), Q(21, 20), Q(11, 10),
                         Q(5, 4), Q(3, 2), Q(8, 5), 2, Q(5, 2), 3])
        ratio = q(rng.choice(choices))
        den = ratio.denominator

        def drift():
            return q(rng.randrange(105, 145) if mono else rng.randrange(45, 230)) / 100

        if graph:
            # a dozen years of weather or wildlife counts: each year is its own
            # draw around a base, the way an annual total actually behaves, and
            # only the two the question names are pinned to each other
            base = rng.randrange(2, 13) * 5
            u = [rng.randrange(1, 2 * base + 1) for _ in range(n)]
            u[i] = -(-u[i] // den) * den
            u[j] = int(u[i] * ratio)
        else:
            u = [rng.randrange(1, 21) * 20]
            for _ in range(n - 1):
                u.append(max(1, int(snap(u[-1] * drift(), 1))))
            u[i] = -(-u[i] // den) * den                  # up to a multiple of den
            u[j] = int(u[i] * ratio)
            for k in range(j + 1, n):
                u[k] = max(1, int(snap(u[k - 1] * drift(), 1)))
            for k in range(i - 1, -1, -1):
                u[k] = max(1, int(snap(u[k + 1] / drift(), 1)))
        values = [x * unit for x in u]
        start_year = start_year or rng.randint(1960, 2020 - (n - 1) * step)
    else:
        i = 0 if i is None else i
        j = 1 if j is None else j
    y0 = start_year or rng.choice([1960, 1970, 1980, 1990, 2000, 2004])
    values = [q(v) for v in values]
    if any(places_needed(v, 6) > sc["places"] or v <= 0 for v in values):
        raise ItemError("a value in this series does not print at the stated precision")
    if max(values) > (20 if sc["places"] == 2 else 20000):
        raise ItemError("this series runs away to values the context cannot carry")
    a, b = values[i], values[j]
    if a <= 0 or b <= 0 or a == b:
        raise ItemError("the two years have to differ")
    if graph and j - i < 3:
        raise ItemError("two labels this close together would print on top of each other")
    key = 100 * abs(b - a) / a
    up = b > a
    if places is None and places_needed(key, 6) > 2:
        raise ItemError("this percent does not print in two decimals")
    if places is not None:
        key = snap(key, Q(1, 10) ** places)
    years = [y0 + k * step for k in range(len(values))]
    if graph:
        # only the two years the question names carry a printed value, exactly
        # as the source item labels them; the rest of the curve is context
        table, figure = None, line_graph(
            [(years[k], float(values[k])) for k in range(len(values))],
            xlabel="Year", ylabel=sc["ylabel"],
            labels={i: f"({years[i]}, {dec(a, sc['places'], group=False)})",
                    j: f"({years[j]}, {dec(b, sc['places'], group=False)})"})
        stem = (f"The line graph shows {sc['what']} from {years[0]} to {years[-1]}. If p% "
                f"is the percent {'increase' if up else 'decrease'} in the {sc['noun']} "
                f"from {years[i]} to {years[j]}, what is the value of p ?")
    else:
        figure = None
        table = [list(sc["head"])] + [[str(years[k]), dec(values[k], sc["places"])]
                                      for k in range(len(values))]
        stem = (f"A table of {sc['what']} for {len(values)} different {sc['period']} is "
                f"shown below. What was the percent "
                f"{'increase' if up else 'decrease'} of the {sc['noun']} from {years[i]} "
                f"to {years[j]}?")
    pool = {
        "earlier_of_later": (f"found what the {years[i]} value is as a percent of the "
                             f"{years[j]} value", 100 * a / b),
        "later_of_earlier": (f"found what the {years[j]} value is as a percent of the "
                             f"{years[i]} value", 100 * b / a),
        "over_the_later": ("divided the change by the later value instead of by the "
                           "earlier one", 100 * abs(b - a) / b),
        "halved": ("halved the percent change", key / 2),
        "doubled": ("doubled the percent change", key * 2),
        "difference": ("subtracted the two values and read the difference as the percent",
                       abs(b - a) if 0 < abs(b - a) <= 250 else None),
    }
    order = ["earlier_of_later", "later_of_earlier", "over_the_later", "halved", "doubled",
             "difference"]
    mistakes = pick(pool, order, wrongs)
    rationale = (f"The change is {dec(abs(b - a), sc['places'])}, and "
                 f"{dec(abs(b - a), sc['places'])}/{dec(a, sc['places'])} = "
                 f"{dec(key, places_needed(key, 4))}%.")
    P = {"kind": "pct_series", "ask": "change", "a": float(a), "b": float(b),
         "round": float(places) if places is not None else None}
    return _finish_series(rng, seed, stem, key, mistakes, rationale, P, table, fmt,
                          places, "percent" if not graph else "plain",
                          "hard" if graph else "medium", figure=figure)


def _finish_series(rng, seed, stem, key, mistakes, rationale, P, table, fmt, places,
                   style, difficulty, figure=None) -> Item:
    fmt = fmt or ("spr" if rng.random() < 0.3 else "mcq")
    if fmt == "spr":
        return spr("pct.series", "a percent across a series", difficulty, seed, stem, key,
                   rationale, mistakes=mistakes, params=P, table=table, figure=figure)
    return mcq("pct.series", "a percent across a series", difficulty, seed, stem, key,
               mistakes, rng, rationale, style=style, places=places, params=P, table=table,
               figure=figure)


# -------------------------------------------------------------- CONCLUSION

VOTES = [
    {"setting": "For the finale of a TV show", "who": "viewers",
     "field": "two contestants", "singular": "contestant", "name": "Contestant 2",
     "chan_a": "social media", "chan_b": "a text message",
     "phr_a": "voting by social media", "phr_b": "voting by text message",
     "use_a": "by social media", "use_b": "by text message"},
    {"setting": "For the final round of a baking competition", "who": "viewers",
     "field": "two finalists", "singular": "finalist", "name": "Finalist 2",
     "chan_a": "a mobile app", "chan_b": "a phone call",
     "phr_a": "voting through the app", "phr_b": "voting by phone",
     "use_a": "through the app", "use_b": "by phone"},
    {"setting": "In a club election", "who": "members", "field": "two candidates",
     "singular": "candidate", "name": "Candidate 2", "chan_a": "an online form",
     "chan_b": "a paper ballot", "phr_a": "voting online", "phr_b": "voting on paper",
     "use_a": "online", "use_b": "on paper"},
]


def conclusion(rng: random.Random, seed: int, *, turnout=None, split=None, rate_a=None,
               rate_b=None, ctx=None, wrongs=None) -> Item:
    """Percentages of a vote, and the one statement they actually support."""
    c = ctx or rng.choice(VOTES)
    who, name = c["who"], c["name"]
    turnout = q(turnout if turnout is not None else rng.choice([5, 8, 10, 12, 15, 20, 25]))
    split = q(split if split is not None else rng.choice([20, 25, 30, 35, 40, 45]))
    rate_a = q(rate_a if rate_a is not None else rng.choice([55, 60, 65, 70, 75, 80]))
    rate_b = q(rate_b if rate_b is not None else rng.choice([20, 25, 30, 35, 40, 45]))
    overall = split * rate_a / 100 + (100 - split) * rate_b / 100
    if rate_a <= 50 or rate_b >= 50 or overall >= 50:
        raise ItemError("the numbers have to leave the trailing candidate behind overall")

    stem = (f"{c['setting']}, {who} could use either {c['chan_a']} or {c['chan_b']} to "
            f"vote for their favorite of {c['field']}. The {c['singular']} receiving more "
            f"than 50% of the vote won. An estimated {dec(turnout, 0)}% of the {who} "
            f"voted, and {dec(split, 0)}% of the votes were cast {c['use_a']}. {name} "
            f"earned {dec(rate_a, 0)}% of the votes cast {c['use_a']} and "
            f"{dec(rate_b, 0)}% of the votes cast {c['use_b']}. Based on this "
            f"information, which of the following is an accurate conclusion?")
    key = (f"{who.capitalize()} {c['phr_a']} were more likely to prefer {name} than were "
           f"{who} {c['phr_b']}.")
    pool = {
        "all_had_voted": (f"extended a result about the {who} who voted to the {who} who "
                          "did not vote",
                          f"If all {who} had voted, {name} would have won."),
        "one_channel_for_all": (f"assumed the {dec(rate_a, 0)}% rate among one channel's "
                                "voters would hold for everybody who voted",
                                f"If all {who} who voted had voted {c['use_a']} instead of "
                                f"{c['use_b']}, {name} would have won."),
        "younger": ("invented a difference between the two groups that the survey "
                    "collected no data on",
                    f"{who.capitalize()} {c['phr_a']} were likely to be younger than "
                    f"{who} {c['phr_b']}."),
        "half_of_everybody": (f"read the two rates as shares of all the {who} rather than "
                              "of the votes cast through each channel",
                              f"More than half of all {who} preferred {name}."),
    }
    # `assemble_text` prints the first three it is handed, so a fixed order would
    # leave the fourth sentence in this file and never on a page
    order = ["all_had_voted", "one_channel_for_all", "younger", "half_of_everybody"]
    wrong = pick(pool, order if wrongs is not None else rng.sample(order, len(order)),
                 wrongs)
    P = {"kind": "pct_conclusion", "who": who, "name": name, "phr_a": c["phr_a"],
         "phr_b": c["phr_b"], "rate_a": float(rate_a), "rate_b": float(rate_b),
         "split": float(split)}
    rationale = (f"{dec(rate_a, 0)}% of one group and {dec(rate_b, 0)}% of the other "
                 f"preferred {name}, so the preference is stronger among {who} "
                 f"{c['phr_a']}; overall {name} took "
                 f"{dec(overall, places_needed(overall, 2))}% of the votes cast, which is "
                 f"not a majority.")
    return text_mcq("pct.conclusion", "reading a conclusion from percentages", "medium",
                    seed, stem, key, wrong, rng, rationale, params=P)
