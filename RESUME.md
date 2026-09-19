# Where this stands, and what is next

Last updated 2026-09-18. The tree is clean, and every topic below passes
`PYTHONPATH=. python3 -m satbank check` — 16 topics, 352 templates, no broken
topic, no template-name collision.

## Done: 16 of 19 topics, 974 of 1,039 official items

965 encoded, 9 excluded with reasons recorded on their own rows.

| topic | templates | official answers | distractor fidelity |
|---|---:|---|---:|
| Right Triangles and Trigonometry | 19 | 33/33 | **100%** |
| Nonlinear Equations and Systems | 32 | 84/84 | 99% |
| Linear Inequalities | 18 | 46/46 | 98% |
| Area and Volume | 19 | 59/59 | 97% |
| Nonlinear Functions | 36 | 105/105 | 96% |
| Systems of Linear Equations | 20 | 61/62 | 95% |
| One-Variable Data | 19 | 49/49 | 93% |
| Equivalent Expressions | 21 | 70/70 | 93% |
| Linear Functions | 23 | 85/86 | 90% |
| Lines, Angles, and Triangles | 31 | 48/48 | 90% |
| Two-Variable Data | 18 | 39/39 | 90% |
| Circles | 16 | 32/32 | 89% |
| Percentages | 18 | 52/52 | 87% |
| Ratios, Rates, Proportions, Units | 22 | 57/57 | 86% |
| Linear Equations in Two Variables | 22 | 80/81 | 83% |
| Linear Equations in One Variable | 18 | 65/65 | 82% |

All sixteen have run their `option_check.py`, and all sixteen had live defects.

## Next: wave 4, 65 items

Probability 36, Sample Statistics and Margin of Error 18, Evaluating
Statistical Claims 11. The smallest wave, and the first where the mathematics
is mostly counting and inference rather than algebra or geometry.

Then the serving layer — see "Before a student sees this" in the README.
Correct items are not a usable bank.

## Do these before wave 4 starts

Four core changes, each one earned by a topic working around it. All are in
shared files, so they must be done between waves, never during one.

1. **`Exact.plain()` writes an ASCII hyphen**, so every topic with signed
   numeric options papers over it with its own `fmt_value`. A typeset minus in
   `exact.py` saves every future topic that step. (Nonlinear Functions)
2. **`expr.parse` lexes a run of letters as one variable name** — right for
   `V_B`, wrong for `cy` and `jb`, which are products. Three separate splitters
   now exist in one topic because of it. (Nonlinear Equations)
3. **`expr.agree` swallows `ParseError` and returns "not equal"**, so any check
   built on it is a silent no-op on input it cannot parse. This disabled a
   duplicate-key guard for months without a single failing test.
   (Nonlinear Equations)
4. **`check._prose` rejects any stem ending in `)`**, so no topic can print
   College Board's "(Disregard the degree symbol…)" parenthetical, and reads
   `{` as a placeholder although `{5}` is how the SAT writes a solution set.
   (Lines/Angles/Triangles, Nonlinear Equations)

Also worth promoting, with requirements already written down by the topic that
needed them: a scatter/chart primitive for `plot.py` with a stated window,
stated gridline steps and label-bearing gridlines that can be read back
(Two-Variable Data's `OPTION-CHECK.md`), and `kit.Surd` into `exact.py` for
`a + b√d`, which `Exact`'s `coef · π^e · √rad` cannot hold (Right Triangles',
five numbered requirements).

## How to run a wave

One agent per topic, in parallel, each given: `TOPIC-GUIDE.md` (the contract),
the nearest finished sibling to read first, and its own topic's sharpest
exposure. Then **re-run the gate yourself, run each `option_check --selftest`
yourself, and read a page of items** rather than trusting the report.

## The things that cost us most, so they are not paid for twice

1. **The gate only ever checks the key.** Every topic needs `option_check.py`.
   Sixteen for sixteen found defects. Wave 3 alone found **eight items with two
   correct options**, every one of which had passed all seven checks.
2. **Reading the page is necessary and is not sufficient.** A
   Lines/Angles/Triangles figure drawn at 141° under a label reading 39° was
   rendered, looked at by a human, and passed; it was caught by measuring the
   drawn geometry in pixels. Wherever a figure carries the question, the
   checker must read the SVG back.
3. **The page is the only thing the student sees, so someone must read it.**
   Nonlinear Functions' `option_check` read back 11,877 items and found
   nothing; the preview pass then found eighteen defects, including a quartic
   drawn to the height of its own tails with all three zeros flattened onto the
   axis — right answer, unanswerable picture.
4. **Prove the checker can fail, and prove it again after every change.** Four
   separate proofs in wave 3 were themselves broken: one caught its injected
   fault only because the splice failed to parse; one would have crashed rather
   than reported; one injected a rounded decimal that solved nothing; one
   encoded the same wrong assumption as the template it was checking.
5. **A guard that can never fire is worse than none** — it advertises a
   protection that is not there. `kit.approx_free` was deleted rather than
   wired, and the real invariant documented where it can actually be violated.
6. **Being made to explain it finds what no check does.** Writing the exactness
   note is what found Right Triangles' last float round-trip, which was never
   wrong and so passed every check, every audit and a 2,000-draw sweep.
7. **A distractor pool must be named and filtered per source item** (`wrongs=`)
   or College Board's own option sets get crowded out.
8. **Fidelity is only meaningful while it is honest.** Every unreached
   distractor in wave 3 is named item by item rather than reached by inventing
   a misconception to fit the digits.

## Before wave 4 starts — state as of 2026-09-18

All sixteen topics pass the full gate. The four core fixes wave 3 earned are
done, and they were worth far more than the four lines they looked like.

### Done

* `Exact.plain()`, `expr.fmt_places`, `expr.sign_join`, `figures.coordinate_grid`
  and `plot._nice` all print the typeset minus, and six topics' renderers with
  them. The bank now shows one spelling of the sign, verified per item across
  stem, options, table cells, SVG labels and rationale.
* `expr.parse(text, names=)` splits a juxtaposed product; `expr.agree` raises
  instead of silently returning "not equal" when it could read neither side.
* `check._prose` accepts a solution set's brace and a closing parenthetical.
* `check` no longer truncates a failure list without saying how many it hid.
* `assemble` takes `forbid=`: values that are also correct and must never be
  offered. Its fillers were inventing near-misses (key ± 1) that bypassed every
  topic's own filter, handing back the other root a template had just struck.
* 1,825 lone-key draws repaired across 17 templates in 5 topics, every
  fidelity number unchanged and checked per source item, not by the percentage.

### Still open, in the order I would do it

1. ~~Promote `shortlist` into `item.assemble`.~~ **Done 2026-09-19** —
   `item.shortlist`, `item.hands_the_key_over`, and `assemble(shortlist=True)`.
   Opt-in, so no existing caller changed; pass it from any signed template
   whose pool names more mistakes than can print. `linear_equations_in_two_
   variables/common.py` still carries the local copy and can now drop it.
   Superseded note follows, kept for the reasoning: Two topics independently built
   the same thing and the flaw it fixes is `assemble`'s own: `same_form[:3]`
   prefers the key's surface form, which for a signed answer systematically
   drops the integer-valued misconceptions — so a perpendicular-slope item
   printed "multiplied the slope by the y-intercept and inverted that" instead
   of "gave the given line's own slope", the error the item exists to test.
   `linear_equations_in_two_variables/common.py` has the general version with
   the reasoning written down. It composes with `forbid=`: one says which three
   of the pool print, the other which values never may. It assumes
   `signed=True`, and by handing over exactly three it takes `_fillers` out of
   play.
2. **`lin1.no_solution_constant` is the one left.** Aligning the topic's guard
   with the gate (done 2026-09-19) cut `distribute` from 715 refusals per 4,000
   seeds to 225 and `chunk` from 160 to 21, because two thirds of what was being
   discarded was a local guard stricter than the rule rather than a thin pool.
   `no_solution_constant` did not improve: measured against its own call path in
   `families/structure.py` (not `kit`, which is why it read as zero at first) it
   refuses **422 of 2,823 raw MCQ draws, 15%** — now the worst of the three. That
   one is a real pool gap and needs misconceptions added, not a guard changed.

   **Isolated 2026-09-19, and the earlier guess in this note was wrong.** It is
   the `coef_zero` shape, not `match_coef`:

       coef_zero    refused 888 of 3,000  (29.6%)
       match_coef   refused  15 of 3,000  ( 0.5%)

   and it fails in two distinct ways — 585 "the printed options would hand the
   key over" and 303 "key would be the only option of its sign". So `coef_zero`
   needs wrong answers that carry the key's sign and its surface; its five named
   mistakes are built around the constant in the parentheses and the right-hand
   value, and land on the wrong side of zero too often. `match_coef` needs
   nothing.

   A caution for whoever takes this: my first probe passed `shape='plain'` and
   `shape='frac'`, which are not names this template accepts, and reported "0
   refused of 1,500" — a clean result from a measurement of nothing, and I
   briefly believed it. The shapes are `coef_zero` and `match_coef`. Check that
   a probe is driving what you think it is before you trust a zero.

   Superseded note, kept for the reasoning:
   **`lin1.distribute`, `no_solution_constant`, `chunk`** still lean on the
   restored guard refusing draws (715, 279 and 160 per 4,000) rather than on a
   repaired pool. No student sees a lone key, but the discarded draws are a
   systematic slice, so the bank is quietly narrower than the parameter space
   suggests. `distribute` is largest and best understood: when the key is a
   fraction, every misconception but one lands on a whole number or on −key.
3. `kit.Surd` into `exact.py` (`a + b√d`, which `Exact` cannot hold), and a
   scatter primitive for `plot.py` with a stated window and readable gridlines.
   Both already have their requirements written down by the topic that needed
   them.

### Run a volume option_check after any rendering change

Typesetting the page broke two topics' checkers, and **the full gate stayed
green the whole time**. Linear Functions went from 0 unreadable draws to 2,061
— three templates at 100% unreadable — and 2 of its 6 selftest faults stopped
being caught. Linear Equations in Two Variables lost 289 of 582 draws in one
template. Both were found only by a volume run. A checker's number readers may
fold the sign while its stem patterns are literal algebra spelled with the
keyboard hyphen, and a regex like that simply stops matching. Fold once on the
way in; never widen thirty patterns.

### The lesson this wave keeps repeating

A check that quietly stops checking is indistinguishable from a check that
passes. Today alone: seven sign tests written against the keyboard hyphen (the
gate's own `_shape`, four topics' private guards, `sign_join`, and a fault
injection that stripped nothing and reported it had looked); a gate truncating
failures to ten with no count, which hid a template failing all along; four
fault-injection proofs that were themselves broken; and two option_checks whose
readers stopped parsing the page and therefore reported nothing wrong. Every
one was green while measuring nothing.

## Wave 4: 2 of 3 done, Probability in flight

**Done:** Evaluating Statistical Claims (11/11, 6 templates, commit 821f8d1) and
Sample Statistics and Margin of Error (18/18, 12 templates, 100% of official
distractors, commit 5579584). Both derive the answer from the study rather than
naming it, and both were verified with the wrong-answer test, not just the gate.

**Probability is unfinished.** An agent was mid-build when the session ended. A
checkpoint of its work is committed (2cc96f5 and later), so nothing is lost, but
it is NOT verified: read `satbank/topics/probability/HANDOFF.md` first — it is
current and outranks this file on its own state — then run the gate, its
`option_check.py --selftest`, and the wrong-answer test before trusting it. Its
gate was already green at checkpoint time, which here means nothing: two topics
have now passed every check while hollow.

Its sharpest exposure, as briefed: P(A|B) against P(B|A) and the wrong
denominator; a printed two-way table that must close arithmetically, which no
gate check verifies; and 10 of 36 items are grid-ins, so an un-enterable
probability must be refused at draw time.

## Superseded: wave 4 at 1 of 3

**Evaluating Statistical Claims is finished** (2026-09-19, commit 821f8d1):
11/11 encoded, 0 excluded, 6 templates, 100% of official distractors, capacity
5,955+. It derives the answer instead of declaring it — `sources.py` passes a
study and the licensed population falls out of the sampling frame. Verified by
the wrong-answer test: asked to print the licensed population as a distractor
it refuses, and switching the method to convenience moves both the key and the
stem. Its `option_check` reads `item.params` nowhere and ships nine injected
faults, all caught.

**Both remaining topics were launched 2026-09-19 and may be unfinished.**
If `satbank/topics/probability/` or
`satbank/topics/sample_statistics_and_margin_of_error/` exists but is not
committed, an agent was mid-build when the session ended. Each was told to keep
a current `HANDOFF.md` in its own directory — read that first, it is the
authority on its own state, not this file. To pick up: run the gate and the
topic's `option_check.py --selftest`, read its HANDOFF, and continue from the
"what is next" line. Nothing outside those two directories and their
transcripts should have changed; `git status` will show if it did.

Verify either one the way the third attempt at Evaluating Statistical Claims
was verified, because a green gate is not the standard here: hand a source item
a deliberately wrong answer and check the engine refuses it.

Remaining: **Probability** (36 items, 28% grid-ins, two-way tables shared with
Sample Statistics) and **Sample Statistics and Margin of Error** (18 items).
Both should read `evaluating_statistical_claims/` first now — it is the nearest
sibling for statement-valued options and the only topic that derives a
judgement rather than a number.

Two core notes it worked around, worth fixing between topics:
`check._prose` reads a bare `None` as an unrendered placeholder, and official
item 2.3 prints `None` as option A; `check._shape` reads the letters "pi"
inside ordinary English, so `hospital` makes a prose option look like
mathematics.

### The two false starts on that topic, worth keeping

2026-09-19. Evaluating Statistical Claims was attempted twice by an outside
model and removed both times. Both attempts passed all seven gate checks at
**100% of official distractors recreated, 11/11 complete option sets, 0
exclusions**, and both were hollow. Do not read a green gate on this topic as
progress.

The first wrote the eleven answers into a string predicate
(`text.startswith("The survey sample is biased")`), copied into the template,
the audit and the option_check, so all three shared one opinion and none could
disagree. The second was told exactly that and rebuilt it as `correct_id`, a
parameter `sources.py` passes in naming which option is right — the same
shortcut with better vocabulary. Its audit carried real-looking rules
(`claim["scope"] == model["frame"]`, `and model["assignment"]`) that are
**unreachable**: only the `claim` and `sample_mask` kinds are ever produced.

The test that settled it, and the one to reuse on any statement-valued topic:
build a source item with a deliberately wrong answer and see whether the engine
refuses it. Item 3.1 samples 40 fourth-graders from one school; passing
`correct_id="fourth_county"` — generalising past the frame, the error the item
exists to catch — produced that option as the key, with the audit agreeing and
the rationale reading "Random selection supports generalization to the
population from which the sample was drawn." If an engine will key a wrong
answer on request, it is not reasoning, whatever the gate says.

What honest looks like here is unchanged and is the whole difficulty of wave 4:
generalisation scope is the sampling frame, a causal claim needs random
assignment rather than random selection, a self-selected sample earns neither,
and a single sample does not fix a population value. A template takes the
population, the frame, the method and whether there was assignment, and
**derives** the licensed option. The audit implements those rules written
independently. Nothing anywhere names which option is correct.
