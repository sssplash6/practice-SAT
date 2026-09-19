# Evaluating Statistical Claims — handoff

Wave 4, first topic. **Complete and green**; nothing is stubbed. 11 official
items (2 easy / 3 medium / 6 hard), no grid-ins, 0 exclusions.

This topic was attempted twice before and rejected twice; read `RESUME.md` →
"Wave 4 is not started" before touching anything here. The short version: both
earlier attempts wrote the answer down (once as a string predicate, once as a
`correct_id` parameter) and every gate check stayed green.

## The rule this package exists to keep

**Nothing anywhere names which option is correct.** Not the template, not
`sources.py`, not `audit.py`, not `option_check.py`. Each template takes a
description of a *study* — the population, the sampling frame, the method,
whether there was random assignment, and what is claimed — renders that study
into the stem, and then *derives* which of the printed options the study
licenses. Changing the study changes the stem **and** the key together, so a
wrong answer cannot be keyed against a given printed page.

Every `wrongs=` list is checked against the derivation: naming the licensed
option as a wrong answer is refused, not obeyed.

```
refused a scope list that names the licensed population:
        'a17,habitat' is the population this study licenses; it cannot be
        printed as a wrong answer
refused a wrong-answer list that names the true set:
        a named wrong answer is the set the survey establishes
refused a conclusion list that names the supported claim:
        'cause_frame' is the conclusion this design supports
refused two true verdicts on one page: 2 of the four statements are true
refused no true verdict on the page:   0 of the four statements are true
```

## Gate

```
PYTHONPATH=. python3 -m satbank check --topic evaluating_statistical_claims
  ok   coverage    11/11 encoded, 0 excluded
  ok   transcript  11/11 items
  ok   acceptance  11/11 answers, 100% of official distractors recreated, 11/11 option sets complete
  ok   audit       1,800 items re-derived
  ok   structure   100% of distractors named
  ok   prose       1,800 items read
  ok   capacity    5,955+ distinct items

PYTHONPATH=. python3 satbank/topics/evaluating_statistical_claims/option_check.py --selftest
  nine injected faults, nine caught
```

## The six templates

| template | official items | distinct / 1,200 draws | what it asks |
|---|---|---:|---|
| `esc.generalize` | 2.2, 3.1, 3.3, 3.6 | 785 | largest population the results reach |
| `esc.generalize_table` | 3.2 | 1,200 | the same, with a two-way table in the way |
| `esc.must_be_true` | 2.1, 2.3 | 1,199 | two or three numbered statements, which hold |
| `esc.sample_quality` | 1.1, 3.4, 3.5 | 764 | what the sampling method does and does not support |
| `esc.inference` | 1.2 | 913 | which inference the frame and the statistic license |
| `esc.conclusion` | — | 976 | association or cause, and for whom |

`esc.conclusion` has no official item behind it, and that is deliberate: rule 2
below has to be *reachable*. The second rejected attempt carried assignment
logic that no draw could ever run. This template runs it on every draw — with
random assignment the licensed conclusion is causal, without it only an
association, and with volunteers it reaches only the units in the study — and
all three regimes appear in a 400-draw sample (153 / 158 / 89).

## The four rules, and where each is written three times

1. **Generalisation scope is the sampling frame.** No wider (the frame stops
   there), no narrower (the randomness earns it).
2. **A causal claim needs random assignment**, not merely random selection.
3. **A self-selected or convenience sample earns neither** — it supports a
   statement about the method.
4. **A single sample does not fix a population value.**

| | states them from |
|---|---|
| `families/*.py` | the study it was handed |
| `audit.py` | `item.params`, parsing the printed options itself |
| `option_check.py` | the printed stem and the printed options, nothing else |

## How the scope rule is derived, not stated

A population is a point in a small lattice: one value per dimension (a trait
such as *fourth-grade* or *17 years old*, and a place such as *the school*),
each dimension a tree of values whose edges say which is contained in which.
`world.py` holds the trees; they are scenario facts ("a school is in a
county"), never answers.

* `within(a, b)` — every dimension of `a` is a descendant-or-self of `b`'s.
* **licensed(P)** = `P ⊆ frame` when the units were selected at random; the
  measured sample only, when they were not.
* **the key** = the unique ⊆-maximum of the licensed set. A draw whose
  licensed set has no unique maximum is refused.

So the answer to 3.1 is not "option B": it is the maximum of `{the 40 sampled
students, all fourth-grade students at the school}`. Move the frame and the
page moves with it:

```
frame={"grade": "fourth", "place": "school"}
  stem: A sample of 40 fourth-grade students was selected at random from a certain school.
  key:  All fourth-grade students at the school

frame={"grade": "fourth", "place": "county"}
  stem: A sample of 40 fourth-grade students was selected at random from the county
        in which a certain school is located.
  key:  All fourth-grade students in the county in which the school is located

method="convenience"
  stem: A sample of 40 fourth-grade students was formed from the students who arrived
        earliest at a certain school one morning.
  key:  The 40 students who were surveyed
```

## Two things to know before changing anything

**`check._shape` reads "pi" inside "hospital".** The gate's surface signature
flags an option containing the letters `pi`, so an option naming a *hospital*
or a *pine* seedling reads as a π-option and the key becomes "the only option
that looks like this". The scenarios say *medical center* and *spruce
seedlings* for that reason. Check any new vocabulary for the substring.

**`check._prose` reads a bare `None` as an unrendered placeholder**, and item
2.3 prints `None` as option A. Free three-statement draws therefore never key
or offer the empty subset; the official item reaches it by naming its own
three wrong sets, and `option_check` reads the official items so the
configuration is still covered. Worth fixing in `check.py` between waves:
`(?<![A-Za-z])None(?=[,.\s]*$)` should not fire on an option that is exactly
`None`.

## Files

```
world.py              the scope lattice and the eleven scope contexts + three table contexts
families/scope.py     esc.generalize, esc.generalize_table
families/claims.py    esc.must_be_true, esc.inference
families/method.py    esc.sample_quality
families/conclude.py  esc.conclusion
audit.py              an independent solver for all six kinds
sources.py            11/11 encoded, EXCLUDED empty
option_check.py       six readers, nine injected faults, --selftest
OPTION-CHECK.md       what it reads, what it found, and why zero defects is the honest number
```

If you change any option wording, re-run `option_check.py --selftest` **and** a
volume sweep, and read the item count: the readers are literal about the
sentences they parse, and a reader that has stopped matching prints `0
defects` in the same words as one that checked everything.
