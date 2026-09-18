# Two-Variable Data — handoff

**Resolved.** This note was written at a mid-wave pause. Everything it lists as
outstanding is now done: `OPTION-CHECK.md` is written, and the full gate and the
400-draw `option_check` sweep were both re-run clean after the cosmetic edits.
The record of what was found and how it is checked lives in `OPTION-CHECK.md`;
this file is kept only for the history.

## Gate

```
PYTHONPATH=. python3 -m satbank check --topic two_variable_data          # last full run: PASS
  ok coverage    39/39 encoded, 0 excluded
  ok transcript  39/39 items
  ok acceptance  39/39 answers, 90% of official distractors recreated, 28/35 option sets complete
  ok audit       5,392 items re-derived
  ok structure   100% of distractors named
  ok prose       5,392 items read
  ok capacity    19,215+ distinct items
```

Re-run in full after the cosmetic edits (axis-label thinning, shorter axis
titles, realistic value bands in `interval_change`): **PASS, same 39/39 and 90%,
capacity 19,216+**.

## Templates — all 18 done

`read.py` point_read · interval_change · series_extreme · curve_read ·
rate_of_change
`fit.py` predict_from_line · fit_slope · fit_equation · residual · slope_scaled
`describe.py` association · interpret_slope · model_type · graph_statement
`models.py` best_model · growth_compare · invest_compare · nonlinear_table

All 39 official items are encoded in `sources.py`; `EXCLUDED` is empty.

## option_check.py — complete, and it has been seen to fail

* Covers **all 18 templates**. None uncovered.
* Decides **every one of the four options**, not just the key, for every
  template. For the sentence-valued families (`association`, `interpret_slope`,
  `model_type`, `graph_statement`, `growth_compare`, `invest_compare`) and the
  expression- and table-valued ones (`fit_equation`, `best_model`,
  `nonlinear_table`) it reads each printed option and decides its truth from the
  model, then asserts exactly one is true and that it is the keyed one.
* **Reads its own SVG back.** `chart()` recovers the pixels-to-data map from the
  printed gridline labels alone, checks it against every label it was not fitted
  through, and recovers the plotted dots, the drawn line of best fit, the drawn
  curve and the drawn line graph. Every line-of-best-fit item is refitted from
  the recovered dots by the normal equations and the refit must agree with the
  drawn line to within a pixel.
* Last run: `--draws 400`, **0 defects** on all 18.
* **Proved it can fail.** `--prove` injects four known-bad items and all four are
  caught: a prediction keyed to the wrong option, a line of best fit redrawn 12
  pixels off its own points, an association item with two true sentences, and a
  table item with two nonlinear tables.

### What it found while being written (all fixed)

1. `ordinal(1)` printed **"11st"** — every 1st/2nd/3rd stem was malformed.
2. `point_read` could name an x with three dots inside half a gridline of it:
   unanswerable.
3. `residual` could name "the charity with the greatest percent" when two dots
   were within a quarter gridline of each other.
4. `residual` printed a fractional x — "the data point with x = 5/7".
5. `curve_read` rounded its key with Python's banker's rounding while the audit
   rounded half away from zero: the two disagreed on exact halves.
6. `best_model` and `fit_equation` had no guard that a distractor misses the
   data visibly, so two options could both fit.
7. By eye on the preview: `predict_from_line` printed "rounded to the nearest ,"
   with an empty placeholder; axes labelled 0.5, 2.5, 4.5; eleven four-digit year
   labels overlapping; two y-axis titles clipped by the frame; a stem saying
   "every 5 years" over a chart drawn every 10; a June temperature of 250 °F.

## Gridline separation — enforced, in both places

`common.separated(key, others, step)` raises `ItemError` on any draw whose key
is closer to another option than the chart's own gridline spacing, and it is
called inside `point_read`, `interval_change`, `series_extreme`, `curve_read`,
`predict_from_line`, `fit_slope` (resolution = one gridline over the drawn
line's length) and `residual`. `option_check.py` asserts it again from the
gridline spacing it recovers from the SVG, so a template that stopped calling it
would be caught.

`common.closest_guard(value, key, others)` is the halfway guard for every stem
saying *closest*, *nearest*, *approximately* or *best estimate*, and
`common.snap(v, step, strict=True)` refuses a value sitting exactly halfway
between two printable answers.

## Statement-valued options

Decided for truth on **all four options**, in `audit.py` and again in
`option_check.py`, both from the printed sentence rather than from the
generator's parameters.

## What is left

Only distractor fidelity, and only where it would have to be invented: 2.4, 2.12
and 3.2 print wrong answers no modelled misconception reaches. The honest 90%
with those three named is the number; curve-fitting to College Board's digits
would hollow it out.
