# Where this stopped

Paused deliberately on 2026-09-15. The tree is clean, everything is
committed, and nothing is half-written.

## Done: 11 of 19 topics, 852 of 1,039 official items

| topic | templates | official answers | distractor fidelity | option check |
|---|---:|---|---:|---|
| Area and Volume | 19 | 59/59 | 97% | yes |
| Linear Inequalities | 18 | 46/46 | 98% | yes |
| Systems of Linear Equations | 20 | 61/62 | 95% | yes |
| One-Variable Data | 19 | 49/49 | 93% | **no** |
| Equivalent Expressions | 21 | 70/70 | 93% | yes |
| Circles | 16 | 32/32 | 89% | **no** |
| Linear Functions | 23 | 85/86 | 89% | **no** |
| Percentages | 18 | 52/52 | 87% | yes |
| Ratios, Rates, Proportions, Units | 22 | 57/57 | 86% | **no** |
| Linear Equations in Two Variables | 22 | 80/81 | 83% | yes |
| Linear Equations in One Variable | 18 | 65/65 | 81% | **no** |

Every one passes `PYTHONPATH=. python3 -m satbank check --topic <slug>`.

## Next, in this order

### 1. Five option checks, already briefed and interrupted

The gate never reads a **wrong** option as mathematics — every check stops at
the key — so an item with two correct options passes all seven and reaches a
student with no defensible answer. Six topics have run the check and **six
found a live defect**, including a keyed system of inequalities that was
infeasible and a distractor that was the key in 57 draws of 6,000.

The five marked "no" above have never run it, and all five use
`assemble_text`. They were briefed and stopped before writing anything. One
had already found something worth chasing:

> **Ratios: a live defect in `rr.growth_table`** — found, not yet quantified
> or fixed.

`satbank/topics/systems_of_linear_equations/option_check.py` and its
`OPTION-CHECK.md` are the reference implementation; `TOPIC-GUIDE.md` carries
the requirement and the three rules (read the printed string not your own
parameters; check generated draws not source items; prove the check can fail).

### 2. Promote an expression parser into the core

Equivalent Expressions ships **two** parsers of its own — a recursive-descent
one in `audit.py` and a shunting-yard one in `option_check.py` — because the
core has none. Nonlinear Functions and Nonlinear Equations, the two largest
topics left, will both need one, and will otherwise write a third and a
fourth. Lift one into `expr.parse(text) -> callable` with a numeric `agree()`.

### 3. Put the `wrongs=` pattern in TOPIC-GUIDE.md

Four topics independently hit `assemble` preferring distractors of the key's
own surface form, which crowds out the option set College Board printed. All
four solved it the same way: a per-source-item `wrongs=[...]` filter naming
the three CB actually used (see `systems_of_linear_equations/sources.py`).
That is better than any ordering heuristic the core could apply — it should be
documented as the standard rather than fixed in `assemble`.

### 4. Wave 3, then wave 4

Wave 3: Nonlinear Functions (110 — the largest in the set), Nonlinear
Equations and Systems (85), Lines Angles and Triangles (48), Right Triangles
and Trigonometry (33), Two-Variable Data (39).

Wave 4: Probability (36), Sample Statistics and Margin of Error (18),
Evaluating Statistical Claims (11).

### 5. Then the serving layer

See "Before a student sees this" in the README. Correct items are not a usable
bank: difficulty is an inherited label that skews hard, random draws repeat,
and nothing weights selection to the exam blueprint.

## What every author should be told, so it is not rediscovered

- The SAT is typeset: π ² ³ √ ≤ ≥ − ·, never `pi` `^2` `<=`. An audit may keep
  an ASCII spelling; `item.norm_text` knows they are one answer.
- A displayed equation gets its own line in the stem.
- A rationale explains which step produces the answer; it never restates it.
- `assemble` enforces the sign rule centrally — pass `signed=True`,
  `fillers="shift"`, and write no local workaround.
- Money is exact and rounded only to print: `expr.fmt_money`, `fmt_places`.
- Options carry a unit only where the source prints one, set per source item.
- Anything asking for the "nearest" or "closest" value needs a guard against a
  draw landing exactly halfway — see `percentages`' `values.unambiguous`.
