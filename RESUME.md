# Where wave 2 stopped

Paused deliberately on 2026-09-14, mid-wave. Nothing here is broken; five
topics are half-built and their expensive half is finished.

## What is done

Six topics are complete, committed and passing `satbank check`: Area and
Volume, Circles, Linear Equations in One Variable, Linear Functions,
One-Variable Data, Percentages. **390 of the 1,039 official items.**

## What wave 2 has on disk

Every question image in all five topics has been read and transcribed. That is
the slow part — roughly 316 questions — and it is complete and committed, so a
resumed author must **not** read the images again.

| topic | transcript | package written so far |
|---|---|---|
| Linear Equations in Two Variables | 81/81 | `common.py`, `model.py`, `__init__.py` — 681 lines, loads but has no templates registered yet |
| Linear Inequalities | 46/46 | `kit.py`, `model.py`, `__init__.py` — 823 lines, loads with 0 templates |
| Equivalent Expressions | 70/70 | `render.py` only — 152 lines |
| Systems of Linear Equations | 62/62 | nothing yet |
| Ratios, Rates, Proportions, and Units | 57/57 | nothing yet |

A topic that does not import fails alone — `satbank check --topic <finished>`
is unaffected, and `satbank topics` simply does not list it.

## How to resume

For each topic, the remaining work is: group the transcribed items into
families, write the templates, write an independently derived solver for every
template in `audit.py`, encode every official item in `sources.py`, and get
the full (non-quick) gate to print PASS.

```bash
PYTHONPATH=. python3 -m satbank check --topic <slug>          # the gate
PYTHONPATH=. python3 tools/preview.py <slug> --per 3           # read the items
```

`TOPIC-GUIDE.md` is the contract. Read a finished sibling first — Linear
Functions for the two linear topics, Linear Equations in One Variable for
Inequalities and Systems, Percentages for Ratios.

## What the last wave learned, so it is not rediscovered

- The SAT is typeset: π, ², ³, √, ≤, ≥, −, · as printed, never `pi`, `^2`,
  `<=`. An audit may keep an ASCII spelling; `item.norm_text` knows the two
  are one answer.
- An equation displayed above the question gets its own line in the stem, not
  run into the sentence after it.
- A rationale explains, it does not restate. "The situation is exactly
  782 + 52(t - 2) = 886" is worthless.
- `assemble` enforces the sign rule itself now — a key is never the only
  option of its sign. Do not write a local workaround; pass `signed=True` and
  `fillers="shift"` for equation answers.
- Money is exact and rounded only to print: `expr.fmt_money`, `expr.fmt_places`.
- Options carry a unit only where the source prints one, set per source item.

## What comes after

Wave 3: Nonlinear Functions (110), Nonlinear Equations and Systems (85),
Lines Angles and Triangles (48), Right Triangles and Trigonometry (33),
Two-Variable Data (39). Wave 4: Probability (36), Sample Statistics and
Margin of Error (18), Evaluating Statistical Claims (11).

Then the serving layer — see "Before a student sees this" in the README.
