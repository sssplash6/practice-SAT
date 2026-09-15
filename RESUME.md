# Where this stands, and what is next

Last updated 2026-09-15. The tree is clean and every topic below passes
`PYTHONPATH=. python3 -m satbank check --topic <slug>`.

## Done: 11 of 19 topics, 659 of 1,039 official items

656 encoded, 3 excluded with reasons recorded on their own `sources.py` rows.

| topic | templates | official answers | distractor fidelity |
|---|---:|---|---:|
| Linear Inequalities | 18 | 46/46 | 98% |
| Area and Volume | 19 | 59/59 | 97% |
| Systems of Linear Equations | 20 | 61/62 | 95% |
| One-Variable Data | 19 | 49/49 | 93% |
| Equivalent Expressions | 21 | 70/70 | 93% |
| Linear Functions | 23 | 85/86 | 90% |
| Circles | 16 | 32/32 | 89% |
| Percentages | 18 | 52/52 | 87% |
| Ratios, Rates, Proportions, Units | 22 | 57/57 | 86% |
| Linear Equations in Two Variables | 22 | 80/81 | 83% |
| Linear Equations in One Variable | 18 | 65/65 | 82% |

All eleven have run their `option_check.py`. **All eleven had live defects**
— 23 in total. See `TOPIC-GUIDE.md` and any topic's `OPTION-CHECK.md`.

## Next: wave 3, then wave 4

Five topics, 315 items, the heaviest wave:

| topic | items | what makes it hard |
|---|---:|---|
| Nonlinear Functions | 110 | the largest in the set; parabolas, exponentials, reading graphs |
| Nonlinear Equations and Systems | 85 | quadratics, radicals, a line meeting a curve |
| Lines, Angles, and Triangles | 48 | the figure carries the question |
| Two-Variable Data | 39 | scatterplots and lines of best fit |
| Right Triangles and Trigonometry | 33 | figures, exact values |

Then wave 4, 65 items: Probability 36, Sample Statistics and Margin of Error
18, Evaluating Statistical Claims 11.

Then the serving layer — see "Before a student sees this" in the README.
Correct items are not a usable bank.

## How to run a wave

One agent per topic, in parallel, each given: `TOPIC-GUIDE.md` (the contract),
the nearest finished sibling to read first, and its own topic's sharpest
exposure. Then **re-run the gate yourself and read a page of items** —
`tools/preview.py <slug> --per 3` — rather than trusting the report. That pass
has caught something in every topic: `f (x)` printed with a space, a year
printed as `1,960`, a rationale that restated the answer, a mass measured in
millimetres.

The core is ready and should not need working around. `expr.parse` /
`expr.agree` / `expr.parse_point` read printed mathematics back, which the two
nonlinear topics will need for "which of the following is equivalent".
`expr.fmt_money`, `fmt_places`, `fmt_band`, `fmt_mixed` print what the page
prints. `plot.boxplots` / `histograms` draw two distributions to one scale.
`assemble` enforces the sign rule centrally.

## The things that cost us most, so they are not paid for twice

1. **The gate only ever checks the key.** Every topic needs `option_check.py`.
   Eleven for eleven found defects.
2. **Anything saying "closest", "nearest", "approximately", or printing money
   needs a halfway guard.** Three topics shipped items whose printed page
   cannot produce the key.
3. **A distractor pool must be named and filtered per source item** (`wrongs=`)
   or College Board's own option sets get crowded out. This alone was a third
   of Area and Volume's rise from 60% to 97%.
4. **Fidelity is only meaningful while it is honest.** Tell authors plainly:
   an honest 85% with the unreachable ones named beats a fabricated 95%.
   Curve-fitting to CB's digits would hollow the metric out entirely.
5. **Read the items on a page.** Every prose defect found this week was found
   by eye, never by a check.
