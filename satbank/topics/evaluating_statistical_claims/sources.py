"""The 11 official Evaluating Statistical Claims items, as the studies that
reproduce them.

No answer appears here, and none can. Every record describes a *study* -- who
was sampled, from what population, by what method, whether there was random
assignment, and what was reported -- and the template renders that study into
the stem and then works out which of the printed options it licenses. Move a
frame and the stem moves with it; name a sampling method the item does not
describe and the key moves to the option that method supports.

Where a record names `wrongs=`, it is naming the options College Board itself
printed as the other three. That is never a statement about which answer is
right: a template refuses a `wrongs` list that names the option its own study
licenses, so a wrong claim cannot be keyed by asking for it.
"""

from __future__ import annotations

from ...topic import S
from .families.claims import inference, must_be_true
from .families.conclude import conclusion               # noqa: F401  (bank template)
from .families.method import sample_quality
from .families.scope import generalize, generalize_table

ALL = [
    # ---- easy
    S("1.1", lambda r: sample_quality(r, 0, ctx="dog_park", n=500, tier="easy")),
    S("1.2", lambda r: inference(r, 0, ctx="book_movie", n=200, p=95, said=0,
                                 wrongs=["wide_strong", "read_strong",
                                         "opposite_group"], tier="easy")),
    # ---- medium
    S("2.1", lambda r: must_be_true(r, 0, ctx="concession", n=200, p=87,
                                    stmts=["population_exact", "repeat_exact"],
                                    tier="medium")),
    S("2.2", lambda r: generalize(r, 0, ctx="textbooks",
                                  wrongs=["any,us", "history,us", "any,csu"],
                                  tier="medium")),
    # the source prints its three statements numbered 1, 2, 3 and then refers to
    # them as I, II and III in the options
    S("2.3", lambda r: must_be_true(r, 0, ctx="air_quality", n=1_000, p=78,
                                    stmts=["population_exact", "repeat_exact",
                                           "other_population"],
                                    numbering="arabic",
                                    wrongs=["II", "I II", "I III"], tier="medium")),
    # ---- hard
    S("3.1", lambda r: generalize(r, 0, ctx="announcements", n=40, k=32,
                                  method="random",
                                  wrongs=["sample", "any,school", "fourth,county"])),
    S("3.2", lambda r: generalize_table(r, 0, ctx="trivia", n=55, cut=3, cut2=5,
                                        lo=6, mid=13, hi=14, counts=(6, 4, 4, 26),
                                        wrongs=["high,tournament", "sample",
                                                "subsample"])),
    S("3.3", lambda r: generalize(r, 0, ctx="fractions_game", n=35, method="random",
                                  wrongs=["sample", "middle,city", "any,city"])),
    S("3.4", lambda r: sample_quality(r, 0, ctx="cable_poll", yes=28, no=70)),
    S("3.5", lambda r: sample_quality(r, 0, ctx="playground", n=20, mean=24)),
    S("3.6", lambda r: generalize(r, 0, ctx="baobab", n=50, years=2,
                                  wrongs=["sample", "a19,habitat", "a17,country"])),
]

EXCLUDED: dict[str, str] = {}
