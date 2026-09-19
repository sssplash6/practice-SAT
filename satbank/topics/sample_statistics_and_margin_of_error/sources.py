"""The 18 official items, as the studies and the pages that reproduce them.

No answer appears here, and none can. Every record describes what the page
says -- how the units were chosen, how many, what was estimated, with what
margin, and what the four options say -- and the engine works out which of
those the study supports.

Two kinds of record, both of them transcription rather than instruction:

* `wrongs=` names the three misconceptions College Board reached for, out of
  a template's named pool. A template refuses a `wrongs` list that names the
  value or the reason its own study licenses, so a wrong answer cannot be
  keyed by asking for it.
* `options=` names the four **sentences** College Board printed, in printed
  order -- the same information the transcript holds, and nothing more. It
  says which sentences, never which of them is right: `study.supported`
  decides that, and the draw is refused when none of the four holds or when
  two of them do.

The wrong-answer test, which is the only one that settles whether an engine
is reasoning: take item 2.8 and ask for a set of four whose supported member
has been swapped out, and the engine refuses rather than keying one of the
three that are left. `option_check.py --selftest` runs it.
"""

from __future__ import annotations

from ...topic import S
from .families.design import margin_size, plausible_count
from .families.estimate import (scale_count, scale_frequency, scale_group,
                                scale_range, scale_two_way)
from .families.interpret import (count_claim, interpret_mean, interpret_percent,
                                 interpret_table, subgroup_claim)

ALL = [
    # ---------------------------------------------------------------- easy
    S("1.1", lambda r: scale_count(r, 0, ctx="council", N=50, n=20, k=6,
                                   wrongs=["sample_count", "unpolled",
                                           "rate_as_count"], tier="easy")),
    # the town holds 14,878 people and every option is built on 15,000 --
    # see `scale_count`'s `base`
    S("1.2", lambda r: scale_count(r, 0, ctx="icecream", N=14_878, n=50, k=7,
                                   base=15_000,
                                   wrongs=["times_n", "n_as_percent",
                                           "tenth_rate"], tier="easy")),
    S("1.3", lambda r: scale_range(r, 0, ctx="forest", T=253,
                                   vals=[51, 59, 45, 52, 73],
                                   wrongs=["low", "median", "high"], tier="easy")),
    S("1.4", lambda r: interpret_percent(r, 0, ctx="menu", n=300, est=38,
                                         moe="11/2",
                                         options=["point", "greater_est",
                                                  "interval", "count_from_sample"],
                                         tier="easy")),
    S("1.5", lambda r: interpret_mean(r, 0, ctx="study_mean", est=37, moe=3,
                                      options=["less_est", "greater_est",
                                               "interval", "outside"],
                                      tier="easy")),
    S("1.6", lambda r: interpret_mean(r, 0, ctx="handbags", est="139/5",
                                      moe="1/50",
                                      options=["interval", "individuals",
                                               "individuals_sample", "point"],
                                      tier="easy")),
    # -------------------------------------------------------------- medium
    S("2.1", lambda r: subgroup_claim(r, 0, ctx="pond", n=150, est=30,
                                      options=["wider_majority", "wider_mean",
                                               "approx_wider", "approx_frame"],
                                      tier="medium")),
    S("2.2", lambda r: interpret_mean(r, 0, ctx="hiking", est="9/2", moe="1/2",
                                      options=["all_individuals", "most_exactly",
                                               "none_below:3", "interval"],
                                      tier="medium")),
    S("2.3", lambda r: interpret_percent(r, 0, ctx="television", n=720, est=32,
                                         moe="341/100",
                                         options=["more_than_upper", "interval",
                                                  "no_conclusion_a",
                                                  "no_conclusion_b"],
                                         tier="medium")),
    S("2.4", lambda r: plausible_count(r, 0, ctx="beads", N=10_000, est=15, moe=2,
                                       wrongs=["above_upper", "margin_to_estimate",
                                               "below_lower"], tier="medium")),
    S("2.5", lambda r: count_claim(r, 0, ctx="fruit", n=80, k=20, size=1_500,
                                   options=["must_wrong", "must_right",
                                            "best_wrong", "best_right"],
                                   tier="medium")),
    S("2.6", lambda r: scale_two_way(r, 0, ctx="mayor", N=6_000,
                                     counts=[[202, 20], [34, 144]],
                                     tier="medium")),
    S("2.7", lambda r: plausible_count(r, 0, ctx="legislation", N=50_000, n=1_000,
                                       est=35, moe=3, off="-3/2",
                                       wrongs=["sample_yes", "sample_no",
                                               "pop_no"], tier="medium")),
    S("2.8", lambda r: interpret_percent(r, 0, ctx="characteristic", est="49/100",
                                         moe="1/25",
                                         options=["interval", "plausible_below",
                                                  "point_exact", "plausible_above"],
                                         tier="medium")),
    # ---------------------------------------------------------------- hard
    S("3.1", lambda r: interpret_table(r, 0, ctx="texting",
                                       counts=[[110, 146], [139, 164], [166, 74]],
                                       moe=3,
                                       options=["error_rate", "not_possible_below",
                                                "point_upper", "doubtful:35"],
                                       tier="hard")),
    S("3.2", lambda r: scale_frequency(r, 0, ctx="nuclear", P=300,
                                       freq=[56, 214, 104, 37], tier="hard")),
    S("3.3", lambda r: margin_size(r, 0, ctx="proposition", pcts=(52, 48),
                                   moes=("21/5", "8/5"),
                                   wrongs=["fewer_lost", "higher_pct",
                                           "larger_n"], tier="hard")),
    S("3.4", lambda r: scale_group(r, 0, ctx="siblings", n=26, k=9, g=1_800,
                                   wrongs=["reported_group", "half",
                                           "all_units"], tier="hard")),
]

EXCLUDED: dict[str, str] = {}
