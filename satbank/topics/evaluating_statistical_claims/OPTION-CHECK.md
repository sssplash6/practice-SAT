# Reading the four sentences back, and the study they are printed under

`satbank check` asks whether the key is right. It never asks whether a
*distractor* is also right. In a topic whose options are sentences that is the
whole risk: an item that offers both

> The survey sample is biased because it is not representative of all city residents.

and

> The sampling method is flawed and may produce a biased estimate of the mean
> number of children per household in the community.

under one convenience sample has **two correct answers**, and passes coverage,
transcript, acceptance, audit, structure, prose and capacity without a mark
against it — because an option that no code ever decides cannot be found wrong
by any amount of deciding the key.

This topic has a second reason to need the check, and it is the reason the
topic was rejected twice. A template that has been *told* the answer and an
audit that has been told the same answer agree with each other forever. The
rejected attempts wrote the answer into a string predicate and then into a
`correct_id` parameter, and both passed all seven checks at 100% distractor
fidelity. `option_check.py` is the only thing in the package that could have
caught them: it is never told, it reads the printed page, and `--selftest`
shows it refusing a wrong key on the very item the review used —
`esc.generalize` item 3.1, keyed to the county.

```bash
PYTHONPATH=. python3 satbank/topics/evaluating_statistical_claims/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 2000
PYTHONPATH=. python3 .../option_check.py --template esc.must_be_true
PYTHONPATH=. python3 .../option_check.py --selftest
```

```
  ok   esc.generalize           2,000 items, 0 defects   (the largest population the study reaches)
  ok   esc.generalize_table     2,000 items, 0 defects   (the same, with the table read back)
  ok   esc.must_be_true         2,000 items, 0 defects   (which statements a sample establishes)
  ok   esc.inference            2,000 items, 0 defects   (the inference the frame and majority allow)
  ok   esc.sample_quality       2,000 items, 0 defects   (what the sampling method supports)
  ok   esc.conclusion           2,000 items, 0 defects   (association or cause, and for whom)
  ok   the official items          11 items, 0 defects   (read the same way)
```

All six templates are covered. None is exempt. The eleven official items are
read as well, because one configuration a free draw cannot reach lives there:
`check._prose` reads a bare `None` as an unrendered placeholder, so no
generated three-statement draw may key the empty set, and item 2.3 — whose
three statements are all false — would otherwise never be read.

## What is read off the page, and what is not

The reader imports `generate` and `ItemError` from the engine and **nothing
else**: no template, no `audit.py`, no solver. From the topic it imports the
study catalogues, and only for what no reader could recover from a page:

* **containment facts.** That a school lies in its county, that a history
  professor is a professor, that "this habitat" lies in South Africa. The page
  assumes them exactly as a scatterplot assumes its units.
* **vocabulary.** That this scenario's target population is called "all city
  residents", that "disliked the movie" and "dislike this movie" are the same
  response.

Everything that decides an answer is taken from the printed item:

| read from | how |
|---|---|
| the sampling method | the stem's own words — "at random", "randomly selected", "random sample" against "was formed", "volunteered" — and exactly one of the two must appear |
| the sampling frame | the place the stem names after "from", taking the longest match and the last one, then the traits named in that sentence before it |
| random assignment | whether the stem says "randomly assigned them to two groups" |
| the sample size | the first number in the stem's sampling sentence |
| the reported percentage | the stem's own `nn%` or `nn percent` |
| every option's population | the sentence taken apart: article, unit noun and one fragment per dimension must account for **every word** |
| every statement's kind | the sentence's own opening — "Of all", "If another", "Of the n … surveyed, …" |
| the table | every row and column re-added, and its total matched against the count the stem claims for it |
| which study it is | each catalogue wording's slot-free chunks must all appear, in order, in the printed stem |

That last row is the guard against a stem that drifted: a rendering that no
catalogue wording can account for matches nothing and is refused rather than
guessed at.

## The rules, stated a third time

The templates state them, `audit.py` states them again from the study's
parameters, and this file states them from the page. Three independent
statements of four rules:

1. **Scope is the frame.** A population is reached when it sits inside the
   population the units were randomly selected from; the units measured are
   always reached; the answer is the unique largest reached option. When the
   page does not say the units were selected at random, only the measured
   units are reached — so the same four options key differently, and the
   reader works out which from the stem's verb.
2. **Cause needs assignment.** A causal claim is supported only where the page
   says the units were randomly assigned. The most appropriate conclusion is
   the maximum under "at least as strong, and at least as wide", and a draw
   with no unique maximum is a defect.
3. **A sample does not fix a population value.** "Of all …, p% …", "if another
   sample were surveyed, p% would …" and "if a different population were
   surveyed, p% would …" are false whatever the sample said; a statement about
   the surveyed group is arithmetic and is checked as arithmetic.
4. **Only the method bears on representativeness.** A statement about the
   responses — that the percentages do not reach 100, that the split was not
   even — can be perfectly true and explain nothing. The reader refuses an item
   that prints such a statement where the question asks which statement *must
   be true*, because there the true-but-silent sentence is a second answer.

## Proving it can fail

A check nobody has seen fail is worth nothing, and four of wave 3's own
fault-injection proofs were themselves broken. `--selftest` injects nine
faults and each is caught, with the message it is caught by:

```
  ok   a scope item keyed to the population past the frame
         caught: the option that is the largest population the study reaches is
                 'All fourth-grade students at the school', but the key is
                 'All fourth-grade students in the county in which the school is located'
  ok   a scope item whose stem no longer samples at random
         caught: the option that is the largest population the study reaches is
                 'The 40 students who were surveyed', but the key is
                 'All fourth-grade students at the school'
  ok   a scope option that lost its qualifier in the rendering
         caught: two options name the same population
  ok   a must-be-true item whose printed count stopped matching
         caught: the option that names exactly the statements that must be true is
                 'Neither', but the key is 'II only'
  ok   a method item with two true verdicts on the page
         caught: 2 of the four options hold of this sampling method
  ok   a second true statement smuggled into a must-be-true item
         caught: 'There were not 50% "Yes" responses...' is true as printed, and the
                 question does not ask for an explanation, so the item has two answers
  ok   a causal conclusion keyed where nothing was randomly assigned
         caught: the option that is the strongest conclusion the design supports is
                 'There is an association ... for the members of the health center.',
                 but the key is 'The sleep app causes an increase ...'
  ok   a two-way table whose cells stopped adding up
         caught: a table row does not add up: [9, 4, 10]
  ok   an inference keyed to the option that fixes the population value
         caught: the option that the study licenses is 'Most people who like this book
                 will dislike this movie.', but the key is 'At least 95% of people who
                 like this book will dislike this movie.'
```

The first two are the ones to keep. **The first is the review's own test**:
take item 3.1, key the county option, and see whether anything objects. The
second is its mirror — the key left alone and the *stem's* sampling method
rewritten — and it is the one that a checker built on the parameters could
never catch, because nothing in the parameters changed.

The seventh was rewritten after it passed for the wrong reason. Its first
version deleted the assignment clause and replaced it with wording no
catalogue knew, so the reader refused the item as unrecognizable and never ran
the assignment rule at all — a green line that measured nothing. It now
generates a genuine observational study and moves the key onto the causal
claim.

## What it found

**No item with two correct answers, over 12,000 draws.** That is worth saying
plainly rather than dressing up: the sweep found nothing in the items, and its
value here is the nine proofs above and the independence they demonstrate.

What the pass did find is one defect in itself and one in the audit, and they
are the same defect written twice:

> `(%| percent)?\b` — **a per-cent sign is not a word character**, so the word
> boundary after it can never match. Every reported percentage was read as a
> headcount instead.

In `audit.py` it made 27 of 60 `esc.must_be_true` draws disagree with their
template. In `option_check.py` it made the reader refuse the same items as
unreadable. Both were found only because the two were written separately and
at different times — and the second was found only because `Unreadable` is
counted as a defect rather than skipped. A reader that shrugged at a sentence
it could not parse would have printed `0 defects` and meant nothing by it.
This is wave 3's own lesson arriving on schedule: *a check that quietly stops
checking is indistinguishable from a check that passes.*

Three more defects were found by the other passes, and are recorded here
because they are the kind the next author will meet:

1. **The gate's surface signature reads "pi" inside "hospital".** `check._shape`
   flags an option carrying `pi` or `π`, and "hospital", "hospitals" and "pine"
   all contain the letters. Every option naming the hospital read as a
   π-option, so the one that did not — the key — was "the only option that
   looks like this". The scenario now says *medical center* and *spruce
   seedlings*. Nothing is wrong with the check; a topic whose options are
   English prose simply has to keep out of its way.
2. **A free draw could offer `None` as a distractor**, which the prose check
   reads as an unrendered placeholder. Three-statement draws now never offer
   the empty subset, and the official item that prints it names its own three
   wrong sets.
3. **A conclusion item printed "causes an increase in reported back pain" over
   a stem reporting significantly *less* back pain.** No check reads an
   option's meaning against the stem's; it was found by reading a page of
   items, which is the third time in this project that the page found what the
   checks could not.

## For whoever changes an option's wording

Every reader here is literal about the sentences it parses. If you reword an
option, a statement or a stem, re-run `--selftest` **and** a volume sweep, and
read the count of items: a reader that has stopped matching reports `0
defects` in exactly the same words as a reader that has checked everything.
The `Unreadable` exception exists so that a sentence this file does not
understand is a failure rather than a silence, and it must stay that way.
