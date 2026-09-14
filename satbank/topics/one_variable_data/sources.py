"""The 49 official One-Variable Data items, encoded as the parameters that
reproduce them.

No answer appears here. Each record pins a template to the source item's own
numbers; the check drives the template and asks whether the engine lands on
the answer in `material/keys/one_variable_data.json`. Where a record names
which misconceptions to use (`only=`), it is saying which wrong answers the
College Board itself offered -- never which answer is right.
"""

from __future__ import annotations

from ...topic import S, Source
from .families.basic import BAR_CONTEXTS, bar_read, list_stat, table_stat
from .families.boxes import BOX_CONTEXTS, PAIR_BOX, box_compare, box_read
from .families.compare import (ODD_CONTEXTS, SD_HIST, SD_SUMMARY, compare_sets,
                               measure_effect, new_data_set, odd_measure, sd_compare)
from .families.freq import FREQ_CONTEXTS, freq_choose, freq_order, freq_stat, freq_two_groups
from .families.means import (CALC_CONTEXTS, FISH_CONTEXTS, REMOVE_CONTEXTS,
                             ROCK_CONTEXTS, TEAM_CONTEXTS, mean_identity, mean_totals,
                             must_be_true, reason_center, unknown_value)

BAR = {c["xlabel"]: c for c in BAR_CONTEXTS}
DOT_VALUES = ("values", "samples", "sample", "samples")
DOT_BURSTS = ("bursts", "eruptions of a steam vent", "eruption", "eruptions")

ALL: list[Source] = [
    # ---------------------------------------------------------------- set 1
    S("1.1", lambda r: list_stat(r, 0, values=[2, 2, 2, 3, 4, 4, 11], stat="median",
                                 presentation="list", frame="count_shown", fmt="mcq")),
    S("1.2", lambda r: unknown_value(r, 0, mode="equal_means", a=[72, 73, 73, 76, 76],
                                     b=[61, 64, 74, 85], presentation="lists",
                                     only=("in_list", "gap", "target"))),
    S("1.3", lambda r: reason_center(r, 0, mode="calculable", n=10, total=90,
                                     context=CALC_CONTEXTS[0])),
    S("1.4", lambda r: list_stat(r, 0, values=[2, 9, 14, 23, 32], stat="mean",
                                 presentation="list", frame="data_shown", fmt="mcq")),
    S("1.5", lambda r: table_stat(
        r, 0, values=[49, 37, 41, 54, 63], other=[73, 56, 62, 75, 81], layout="two_row",
        stat="mean", labels=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        heading="Low temperature", other_label="High temperature",
        only=("median", "both_median", "both_mean"),
        intro="The table below shows the high and low temperatures in Houston, Texas, "
              "during a five-day period.",
        ask_phrase="What was the mean low temperature, in degrees Fahrenheit, during "
                   "the five-day period?")),
    S("1.6", lambda r: compare_sets(r, 0, a=[1, 2, 3, 4, 5, 6, 7],
                                    b=[1, 1, 2, 2, 3, 3, 4], ask="means_statement",
                                    presentation="lists")),
    S("1.7", lambda r: box_read(r, 0, summary=[1126, 4399, 7067, 10595, 13263],
                                ask="median", n=13, context=BOX_CONTEXTS[0],
                                closest=True, only=("q1", "q3", "q1_hi_mid"))),
    S("1.8", lambda r: table_stat(
        r, 0, values=[24, 24, 21, 21, 21, 19, 24, 24, 19, 22, 23], layout="rows",
        stat="range", labels=list("ABCDEFGHIJK"), quantity="One-hour period",
        heading="Number of wheels made", places=1, table_places=0,
        intro="A study was conducted on the production rates for a company that "
              "produces tractor wheels. The table below shows the number of wheels "
              "made during 11 consecutive one-hour production periods.",
        ask_phrase="What is the range of the number of wheels made for the 11 one-hour "
                   "periods?"), "the source lists the options in descending order"),
    S("1.9", lambda r: table_stat(
        r, 0, stat="pair_sum", values=[3, 16, 26, 73, 53, 29], pair=(5, 4),
        labels=["Once a week or more", "Two or three times a month",
                "About once a month", "A few times a year", "Almost never", "Never"],
        quantity="Response", heading="Frequency",
        intro="The table gives the results of a survey of 200 people who were asked "
              "how often they see a movie in a theater.",
        ask_phrase="How many people responded either “never” or “almost "
                   "never”?")),
    S("1.10", lambda r: table_stat(
        r, 0, values=[2.0, 21, 61, 26, 0.44], layout="rows", stat="mean", rounding=0,
        labels=["Monaco", "Nauru", "San Marino", "Tuvalu", "Vatican City"],
        quantity="Country", heading="Land area (square kilometers)",
        only=("max", "total", "median"),
        intro="The table above shows the land area, in square kilometers, of the five "
              "smallest countries of the world in 2016.",
        ask_phrase="Based on the table, what is the mean land area of the 5 smallest "
                   "countries in 2016, to the nearest square kilometer?")),
    S("1.11", lambda r: bar_read(r, 0, values=[30, 62, 36, 50, 46, 40, 54, 60, 16, 20],
                                 ask="value", target=0, context=BAR["Group"],
                                 state_total=True, fmt="spr")),
    S("1.12", lambda r: bar_read(r, 0, values=[4, 7, 1, 3, 6], ask="mean",
                                 context=BAR["Trial"], places=1)),
    S("1.13", lambda r: odd_measure(
        r, 0, values=[81, 80, 81, 81, 82], context=ODD_CONTEXTS[0],
        intro="The high temperature, in degrees Fahrenheit (°F), in a certain city "
              "was recorded for each of 5 days. The data are shown below.",
        ask_phrase="Over this 5-day period, which of the following is NOT equal to "
                   "81°F?")),
    S("1.14", lambda r: compare_sets(
        r, 0, a=[87, 80, 75, 76, 70], b=[44, 54, 65, 76, 82], ask="one_two",
        presentation="table", labels=["2008", "2009", "2010", "2011", "2012"],
        row_names=("Foothill", "Valley"), row_label="High school", totals=True,
        intro="The table above shows the number of students from two different high "
              "schools who completed summer internships in each of five years. No "
              "student attended both schools.",
        ask_phrase="Which of the following statements are true about the number of "
                   "students who completed summer internships for the 5 years shown?",
        statements=("The mean number from Foothill High School is greater than the mean "
                    "number from Valley High School.",
                    "The median number from Foothill High School is greater than the "
                    "median number from Valley High School."))),
    S("1.15", lambda r: bar_read(r, 0, values=[5, 7, 8, 9, 11], ask="difference",
                                 target=4, other=0, context=BAR["Type of monkey"],
                                 only=("taller", "shorter", "other_2")),
      "the source lists the options in descending order"),
    S("1.16", lambda r: bar_read(r, 0, values=[14, 8, 18, 3], ask="value", target=2,
                                 context=BAR["Gift"], state_total=True)),
    S("1.17", lambda r: list_stat(r, 0, values=[6, 8, 16, 4, 17, 26, 8, 5, 5, 5],
                                  stat="mean", presentation="list", frame="list_intro",
                                  fmt="spr")),
    S("1.18", lambda r: freq_choose(r, 0, ask="match_list",
                                    data=[4, 4, 4, 4, 8, 8, 8, 13, 13])),
    S("1.19", lambda r: list_stat(r, 0, values=[71, 72, 73, 76, 77, 79, 83, 87, 93],
                                  stat="median", presentation="list",
                                  frame="data_shown", fmt="mcq")),
    S("1.20", lambda r: bar_read(r, 0, values=[29, 31, 39, 43, 48], ask="value",
                                 target=2, context=BAR["Activity"],
                                 only=("bar_4", "top", "bar_0"))),
    S("1.21", lambda r: bar_read(r, 0, values=[40, 50, 67, 52], ask="difference",
                                 target=1, other=0, context=BAR["Month"]),
      "the source lists the options in descending order"),

    # ---------------------------------------------------------------- set 2
    S("2.1", lambda r: freq_order(
        r, 0, values=[18, 19, 20, 21, 22, 23, 30], freqs=[6, 5, 4, 2, 1, 1, 1],
        context=FREQ_CONTEXTS[0],
        intro="The table above shows the distribution of ages of the 20 students "
              "enrolled in a college class.",
        ask_phrase="Which of the following gives the correct order of the mean, median, "
                   "and mode of the ages?")),
    S("2.2", lambda r: sd_compare(r, 0, presentation="summary", n=2500, mu=186,
                                  sd_a=12.5, sd_b=19.1, context=SD_SUMMARY[0])),
    S("2.3", lambda r: unknown_value(r, 0, mode="mean_equals_median",
                                     values=[15, 14, 18, 17], wrong=6)),
    S("2.4", lambda r: table_stat(
        r, 0, layout="rows2", stat="median", fmt="spr", table_places=1,
        values=[84.7, 69.8, 60.7, 55.7, 47.7, 37.8, 31.5, 32.2, 28.4],
        other=[83.0, 66.7, 57.5, 57.7, 46.4, 35.7, 30.4, 26.3, 24.7], compare_other=True,
        labels=["France", "United States", "Spain", "China", "Italy", "Turkey",
                "Germany", "United Kingdom", "Russia"],
        quantity="Country", heading="2013", other_label="2012",
        intro="The table above shows the number of international tourist arrivals, "
              "rounded to the nearest tenth of a million, to the top nine tourist "
              "destinations in both 2012 and 2013.",
        ask_phrase="Based on the information given in the table, how much greater, in "
                   "millions, was the median number of international tourist arrivals "
                   "to the top nine tourist destinations in 2013 than the median number "
                   "in 2012, to the nearest tenth of a million?")),
    S("2.5", lambda r: table_stat(
        r, 0, values=[3.699, 3.609, 3.729, 3.679, 3.729], layout="columns",
        stat="median", prefix="$", places=3,
        labels=["Station 1", "Station 2", "Station 3", "Station 4", "Station 5"],
        only=("mean", "mode", "one_short"),
        intro="In the table above, Melissa recorded the price of one gallon of regular "
              "gas from five different local gas stations on the same day.",
        ask_phrase="What is the median of the gas prices Melissa recorded?")),
    S("2.6", lambda r: freq_choose(
        r, 0, ask="mean_over_median",
        lists=[[2, 4, 8, 16, 32, 64, 128, 256, 512], [5] * 9,
               [0, 10, 20, 30, 40, 50, 60, 70, 80],
               [7, 107, 107, 207, 207, 207, 307, 307, 307]])),
    S("2.7", lambda r: measure_effect(
        r, 0, edit="correct_low", ask="unchanged", n=15, k=10,
        context=("horses in a stable", "weights", "pounds", "horse", "weight"),
        body="The horse with the lowest reported weight was found to actually weigh 10 "
             "pounds less than its reported weight.",
        ask_phrase="What value remains unchanged if the four values are reported using "
                   "the corrected weight?")),
    S("2.8", lambda r: compare_sets(r, 0, a=[5] * 9, b=[5] * 9 + [100],
                                    ask="which_differ", presentation="lists")),
    S("2.9", lambda r: mean_identity(r, 0, mode="consecutive", n=9, fmt="spr")),
    S("2.10", lambda r: reason_center(r, 0, mode="median_interval", counts=[10, 11, 12],
                                      bounds=[5, 13], options=[8, 4.5, 13.5, 15],
                                      context=FISH_CONTEXTS[0])),
    S("2.11", lambda r: mean_identity(r, 0, mode="fraction_of_sum",
                                      values=[2, 10, 3, 7, 6], fmt="spr")),
    S("2.12", lambda r: sd_compare(
        r, 0, presentation="histograms", counts_a=[0, 0, 42, 49, 42, 0, 0],
        counts_b=[31, 22, 12, 3, 12, 22, 31], context=SD_HIST[0],
        ask_phrase="Which statement best compares the standard deviations of number of "
                   "units sold for these companies?")),
    S("2.13", lambda r: new_data_set(
        r, 0, mode="shift", c=46, context=DOT_VALUES,
        values=[22] * 5 + [23] * 4 + [24] * 3 + [25] * 2 + [26],
        intro="Data set A has 15 values and is represented by the dot plot shown. Data "
              "set B is created by adding 46 to each of the values in data set A.",
        ask_phrase="Which of the following correctly compares the medians and the "
                   "ranges of data sets A and B?")),

    # ---------------------------------------------------------------- set 3
    S("3.1", lambda r: measure_effect(
        r, 0, edit="spread_about_median", ask="changed", n=27, k=7, key_measure="sd",
        measures=["sd", "mean", "median", "sum"],
        intro="A data set of 27 different numbers has a mean of 33 and a median of "
              "33.")),
    S("3.2", lambda r: freq_stat(r, 0, values=[1, 2, 3, 4, 5], freqs=[1, 2, 3, 2, 1],
                                 ask="mean_minus_median", symbolic=True, head_v="Value",
                                 only=("row_above", "max_gap", "mean_itself"))),
    S("3.3", lambda r: must_be_true(r, 0, mode="two_means", n=10, m1=3.41, m2=3.79,
                                    context=TEAM_CONTEXTS[0])),
    S("3.4", lambda r: mean_totals(r, 0, mode="removed", n=8, m1=14.5, m2=12,
                                   context=REMOVE_CONTEXTS[0])),
    S("3.5", lambda r: freq_choose(r, 0, ask="greatest_mean", values=[70, 80, 90, 100],
                                   f=4, g=6, h=6)),
    S("3.6", lambda r: mean_totals(r, 0, mode="removed", n=20, m1=6.7, m2=6.25,
                                   context=REMOVE_CONTEXTS[1], places=2,
                                   only=("same_count", "mean_drop", "swapped"))),
    S("3.7", lambda r: must_be_true(r, 0, mode="append_extreme", size=55, lo=170,
                                    hi=290, extra=10, direction="below", first="mean",
                                    names=("F", "G"))),
    S("3.8", lambda r: table_stat(
        r, 0, values=[21.9, 27.9, 25.9, 19.5, 30.1, 36.4, 35.5], layout="rows",
        stat="median", suffix="%", places=2, table_places=1, reference=26.95, rounding=2,
        labels=["State A", "State B", "State C", "State D", "State E", "State F",
                "State G"],
        quantity="State", heading="Percent of residents",
        only=("mean", "even_down", "min"),
        intro="A survey was given to residents of all 50 states asking if they had "
              "earned a bachelor's degree or higher. The results from 7 of the states "
              "are given in the table above. The median percent of residents who earned "
              "a bachelor's degree or higher for all 50 states was 26.95%.",
        ask_phrase="What is the difference between the median percent of residents who "
                   "earned a bachelor's degree or higher for these 7 states and the "
                   "median for all 50 states?")),
    S("3.9", lambda r: unknown_value(
        r, 0, mode="equal_means", a=[2.4, 2.5, 3.6, 3.1, 2.5, 2.7],
        b=[3.1, 2.7, 2.9, 3.3, 2.8], d=0.1, presentation="table", fmt="spr",
        context=ROCK_CONTEXTS[0])),
    S("3.10", lambda r: freq_two_groups(
        r, 0, values=[2, 3, 4, 5, 6, 7, 8, 9, 10], fa=[1, 1, 2, 1, 3, 0, 0, 1, 0],
        fb=[0, 0, 0, 4, 2, 0, 2, 1, 2], ask="median_difference", fmt="spr",
        label="Score", col_labels=("Group A", "Group B"),
        intro="For a certain computer game, individuals receive an integer score that "
              "ranges from 2 through 10. The table below shows the frequency "
              "distribution of the scores of the 9 players in group A and the 11 "
              "players in group B.",
        ask_phrase="The median of the scores for group B is how much greater than the "
                   "median of the scores for group A?")),
    S("3.11", lambda r: new_data_set(
        r, 0, mode="append", extra=11, context=DOT_BURSTS,
        values=[1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 4, 5], first="median")),
    S("3.12", lambda r: mean_totals(r, 0, mode="combined", n1=75, n2=50, m1=25, m2=65,
                                    fmt="spr",
                                    context=("objects", "heights", "meters"))),
    S("3.13", lambda r: unknown_value(
        r, 0, mode="integer_mean", values=[43, 45, 44, 43, 38, 39, 40, 46, 40],
        bound=60, fmt="spr")),
    S("3.14", lambda r: freq_two_groups(
        r, 0, values=[30, 34, 38, 42, 46], fa=[2, 4, 5, 7, 9], fb=[9, 7, 5, 4, 2],
        ask="compare_means",
        intro="Data set A and data set B each consist of 27 values. The table shows the "
              "frequencies of the values for each data set.")),
    S("3.15", lambda r: box_compare(r, 0, first=[21, 22, 25, 26, 28],
                                    second=[22, 23, 24, 25, 28],
                                    context=PAIR_BOX[0])),
]


# Every official item is encoded above; nothing in this topic depends on a
# picture that cannot be regenerated from its own numbers.
EXCLUDED: dict[str, str] = {}
