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
