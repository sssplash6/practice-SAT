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
2. **`lin1.distribute`, `no_solution_constant`, `chunk`** still lean on the
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

## Wave 4 is not started — and one false start is worth knowing about

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
