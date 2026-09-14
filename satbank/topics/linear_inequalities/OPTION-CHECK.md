# Reading the wrong answers back

`satbank check` asks whether the key is right. It never asks whether a
*distractor* is also right.

Nothing in the engine reads a wrong option as mathematics. `assemble_text` takes
four strings, shuffles them and records which one is the key; `audit` re-derives
the key and compares; `structure` counts surface forms and `prose` looks for
placeholders. An item with two correct answers satisfies every one of them. In
this topic the hole is wider than most, because two printed inequalities can
describe one solution set while looking nothing alike — `−2x > 6` and `x < −3`,
a system and the same system with its rows in another order, or two options that
are both empty because the conditions cannot all be met.

`option_check.py` closes it. It parses the four printed option strings back into
relations, decides each option's truth set **by putting numbers in on both sides
of every boundary**, and asserts that exactly one option has the property the
stem asks for and that it is the keyed one.

```bash
PYTHONPATH=. python3 satbank/topics/linear_inequalities/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 1500
PYTHONPATH=. python3 .../option_check.py --template ineq.model_system
PYTHONPATH=. python3 .../option_check.py --sources     # the 46 official sets
PYTHONPATH=. python3 .../option_check.py --selftest    # three injected faults
```

```
  ok   ineq.solve_linear          1,500 items, 0 defects  (the values the printed inequality allows)
  ok   ineq.model_system          1,500 items, 0 defects  (same solution set)
  ok   ineq.point_solution        1,500 items, 0 defects  (the pairs that satisfy the inequality)
  ...
27,000 option sets read back
```

## What it parses

The reader is deliberately naive, and shares nothing with the renderer:
`generate` is the only thing it imports from the engine, and only to obtain the
finished item in the state a student would receive it. Everything else is
re-implemented here — about a hundred and fifty lines of tokenizer, expression
parser and comparator — so a renderer that drops a minus sign or prints `≥` for
`≤` is visible rather than invisible.

| printed form | read as |
|---|---|
| `2x + 100 ≤ 210`, `x ≤ −7` | one comparison between two expressions |
| `1,510 ≤ d ≤ 4,130` | the two comparisons a band stands for |
| `x + y ≥ 20, 3x + 4y ≤ 80` | a conjunction — a system is read like a rider |
| `p + 36 > 0.20(300), where p ≤ 150` | the same: a conjunction |
| `x < 6 or x > 18` | a union |
| `165(12.7)`, `(72)(16)`, `2x`, `0.20(300)` | implicit multiplication |
| `0 < x ≤ 11 2/3` | a mixed number: the one place a space sits inside a number |
| `(3, 21), (5, 35), (8, 56)` | three ordered pairs |
| `I and II only` | the set {I, II} |
| `97.9°F`, `2,300`, `−14` | a Fraction; the typeset minus and the separators are handled |

## What it asserts

Every check has the same shape — classify all four options, demand exactly one
hit, demand it is the keyed one — so a second correct answer fails as loudly as a
wrong key.

Two kinds of property are decided. Where the stem carries the mathematics, the
property comes from the printed stem: `ineq.solve_linear` compares each option
with the inequality printed above the question, and `ineq.point_solution` tests
each candidate against the rows printed above it. Where the mathematics is in the
prose — every modelling template — the property is a relation built here from the
item's own numbers in `params`, never from the renderer; the option still has to
be *parsed* and *evaluated* to be compared with it.

| template | property, decided by putting values in |
|---|---|
| `ineq.solve_linear` | the option allows exactly the values the printed inequality allows |
| `ineq.y_range_from_system` | the y-bound is recovered from the two printed rows, then compared |
| `ineq.range_solve`, `ineq.model_two_var`, `ineq.model_one_var`, `ineq.model_system` | the option's set equals the modelled constraint's set |
| `ineq.band_from_extremes`, `ineq.band_scale`, `ineq.band_formula` | the option's set equals the band |
| `ineq.triangle_third_side`, `ineq.allowable_dimension` | the option's set equals the lengths a triangle, or a box, admits |
| `ineq.which_interval` | every value the interval allows is past the threshold parsed from the stem |
| `ineq.value_in_range` | exactly one printed value lies inside the band |
| `ineq.whole_number_bound`, `ineq.pair_max`, `ineq.greatest_value` | the option is the extreme value that works, and the next one along does not |
| `ineq.point_solution` | the point, the table of pairs, the roman-numeral subset or the system is tested against the printed rows |
| `ineq.interpret` | the sentence's own numbers and relation word are read out and tested |

### Comparing two sets by value

`same_set` never compares strings. It collects every boundary of both relations
— found by evaluating each side at two points, since both are linear — and puts
into both relations the boundary itself, a value either side of it, the midpoints
between boundaries and a value far outside them all. Two relations that differ by
a sign that failed to turn over disagree at the first such value.

For a relation in two variables, one variable moves and the other is pinned. The
pins matter: pinning at arbitrary numbers (0, 3, −2) was the first thing tried,
and it reported two four-row staffing systems as equal because *every* slice
through those numbers was empty for both. The pins are now taken from the rows'
own boundaries, which is where the region that separates two systems lives.

## What it caught

**Two live defects, both in stem variants no official item uses.**

1. `ineq.model_system`, staffing shape — an **infeasible key**. The template
   checked that the budget could pay the smallest *team*, but not that it could
   pay a team meeting both role minimums:

   ```
   Valentina needs to hire at least 15 staff members ... $520 per week ... $800
   per week ... budget no more than $8,000 ... at least 5 junior directors and
   at least 1 senior director.
       520x + 800y ≥ 8,000, x + y ≥ 15, x ≤ 5, y ≤ 1   <- also empty
     * 520x + 800y ≤ 8,000, x + y ≥ 15, x ≥ 5, y ≥ 1   <- the key, empty
   ```

   Fourteen juniors and one senior already cost $8,080. The keyed system has no
   solutions at all, and the option that reads both floors as caps is empty too:
   two options describing the same set, and nothing in the gate can see it. The
   fix is a feasibility guard — the budget has to cover the cheapest team that
   meets every condition, with room to spare.

2. `ineq.interpret`, pair shape — a **pair on the boundary**. When the perimeter
   the pair gives equals the cap exactly, the option that turns the relation
   round is true as well:

   ```
   2ℓ + 2w ≤ 44 ... interpretation of (ℓ, w) = (15, 7)?
     * If the banner has length 15 and width 7, its perimeter is less than or equal to 44.
       If the banner has length 15 and width 7, its perimeter is greater than or equal to 44.
   ```

   44 ≤ 44 and 44 ≥ 44 are both true. The fix rejects a pair that lands on the
   cap.

Both items pass coverage, transcript, acceptance, audit, structure, prose and
capacity, because every one of those stops at the key.

**Three injected faults** (`--selftest`), because a check nobody has seen fail is
worth nothing: the key repeated as a distractor with its rows reordered, the key
moved a letter, and a distractor rewritten as the key multiplied through by −2.
All three are reported, and between them they exercise both halves of the
assertion.

**Nothing in the official sets.** `--sources` runs the same assertions over the
46 transcribed option sets; all of them read back with exactly one right answer.
