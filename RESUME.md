# Where this stands, and what is next

Last updated 2026-09-17. Waves 1 and 2 are committed and green. **Wave 3 is
encoded but paused mid-verification** — read "Wave 3" below before touching it.

## Done: 11 of 19 topics, 659 of 1,039 official items

656 encoded, 3 excluded with reasons recorded on their own `sources.py` rows.

| topic | templates | official answers | distractor fidelity |
|---|---|---:|---:|
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

## Wave 3: all 315 items encoded, three topics green, two not

Every one of the five topics is transcribed from its question images and
encoded, and nothing in the shared core was changed to do it. Fidelity across
the wave averages 94%, against 90% for waves 1 and 2.

| topic | templates | answers | fidelity | excluded | state |
|---|---:|---|---:|---:|---|
| Right Triangles and Trigonometry | 19 | 33/33 | 100% | 0 | **full gate green, option_check clean** |
| Nonlinear Functions | 36 | 105/105 | 96% | 5 | **full gate green, option_check clean** |
| Two-Variable Data | 18 | 39/39 | 90% | 0 | **full gate green, option_check clean** |
| Lines, Angles, and Triangles | 31 | 48/48 | 88% | 0 | gate green; **option_check never run** |
| Nonlinear Equations and Systems | 32 | 79/84 | 99% | 1 | **gate NOT green**, 3 open defects |

Each topic's `HANDOFF.md` is the authority on its own state. They are detailed
and were written to be picked up cold.

### What is left, in the order it should be done

1. **Nonlinear Equations and Systems, three named defects.** (a) a regression
   from widening `square_equation` for capacity: `spare=0` became `spare=None`
   and broke 5 source rows that pass `k` only — draw `spare` only when `k` is
   also None; (b) `scaled_quadratic` draws coefficients with no real solution —
   fix the template, not the audit; (c) `curve_line_system` seed 1 prints **two
   points that both satisfy both equations**, a real two-correct-answers defect.
2. **Lines, Angles, and Triangles: run `option_check.py`.** It is written but
   has never been executed, and carries two half-written helpers (`_leg_scale`,
   a dead dict in `check_vertical_similar`). Treat it as a draft. In this topic
   the figure carries the question, so this is the highest-value unrun check in
   the wave. Its author names six templates whose figure/answer agreement they
   were least sure of.
3. **`option_check.py` for Nonlinear Equations and Systems** — the one wholly
   missing deliverable there. Its `HANDOFF.md` specifies it per template;
   substituting each printed option back into the **printed** equation
   (extraneous roots) and the SVG read-back are the two that matter.
4. **`OPTION-CHECK.md` in all five topics.** Every script exists or is drafted;
   none of the prose notes are written. The content is in each `HANDOFF.md`.
5. **Read a page of items** in Nonlinear Functions and Nonlinear Equations —
   the only two topics that never had the eyeball pass. It has never once come
   back empty.
6. `kit.approx_free` in Nonlinear Equations is **unwired** — wire it into
   `tangent_constant` or delete it. Do not leave a guard nothing calls.

### Wave 3's own lessons, which cost real time

* **A failing audit is not always the template's fault.** `nleq.isolate_factor`
  looked like float residue in the error text and was diagnosed as such by the
  coordinator; it was actually `expr.parse` lexing a printed `jb` as one
  variable named `jb` and raising before any arithmetic. "**0** of four options
  are correct" means no comparison was reached — read that as a reader failure,
  not a rounding one. The same blind spot silently disabled `kit.text_choices`'
  duplicate-key check for every juxtaposed-product option.
* **`expr.agree` swallows `ParseError` and returns "not equal".** Any check
  built on it is a no-op on input it cannot parse, and says nothing about it.
  This is a core sharp edge, not a topic bug.
* **`check._prose` rejects any stem ending in `)`**, so no topic can print
  College Board's own "(Disregard the degree symbol…)" grid-in parenthetical.
* **Picture-valued options are the honest exclusion.** All 6 exclusions in the
  wave are items whose four options are drawn graphs or tables. Rendering a
  table option as text was considered and rejected: the acceptance check would
  then compare the engine against a format the engine invented. If these are
  wanted back, the route is a table-valued option type in the core.

## Then wave 4, 65 items

Probability 36, Sample Statistics and Margin of Error 18, Evaluating
Statistical Claims 11. Then the serving layer — see "Before a student sees
this" in the README. Correct items are not a usable bank.

## How to run a wave

One agent per topic, in parallel, each given: `TOPIC-GUIDE.md` (the contract),
the nearest finished sibling to read first, and its own topic's sharpest
exposure. Then **re-run the gate yourself and read a page of items** —
`tools/preview.py <slug> --per 3` — rather than trusting the report.

## The things that cost us most, so they are not paid for twice

1. **The gate only ever checks the key.** Every topic needs `option_check.py`.
   Eleven for eleven found defects in waves 1-2; in wave 3 it found 13 more in
   the three topics that ran it, including **four items with two correct
   options** that had passed all seven gate checks.
2. **Anything saying "closest", "nearest", "approximately", or printing money
   needs a halfway guard.** But do not add a fake one where nothing rounds —
   an unwired guard is worse than none.
3. **A distractor pool must be named and filtered per source item** (`wrongs=`)
   or College Board's own option sets get crowded out.
4. **Fidelity is only meaningful while it is honest.** An honest 85% with the
   unreachable ones named beats a fabricated 95%.
5. **Read the items on a page.** Every prose defect found so far was found by
   eye, never by a check.
6. **Prove the checker can fail.** Every wave-3 `option_check` that ran ships a
   `--selftest` that injects known-bad items and must catch all of them.
