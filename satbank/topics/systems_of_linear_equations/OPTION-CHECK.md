# Reading the wrong answers back

`satbank check` asks whether the key is right. It never asks whether a
distractor is *also* right.

Nothing in the engine reads a wrong option as mathematics. `assemble_text` takes
four strings, shuffles them and records which one is the key; `audit` re-derives
the key and compares; `structure` counts surface forms and `prose` looks for
placeholders. All of that is satisfied by an item with two correct answers. The
hole is structural, not a gap someone forgot to fill: an option that no code ever
solves cannot be found wrong by any amount of solving the key.

`option_check.py` closes it for this topic. It parses the four printed option
strings — and, for the graph items, the drawn SVG — back into linear algebra,
decides each option's status from that algebra alone, and asserts that exactly
one option has the property the stem asks for and that it is the keyed one.

```bash
PYTHONPATH=. python3 satbank/topics/systems_of_linear_equations/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 2000 --template sys.solve_pair
```

```
  ok   sys.pick_no_solution         600 items, 0 defects   (many)
  ok   sys.solve_pair               600 items, 0 defects   (one point)
  ok   sys.graph_solution           600 items, 0 defects   (drawn crossing as a point)
  ok   sys.other_equation           600 items, 0 defects   (empty system)
  ok   sys.all_solutions            600 items, 0 defects   (every point of the line)
```

## What it parses

The reader is deliberately naive. It knows how an SAT page prints a linear
equation and nothing else — no `Poly`, no `Exact`, no `kit.py`. `generate` is the
only thing it imports from the engine, and only to obtain the finished item, in
the state a student would receive it.

| printed form | read as |
|---|---|
| `4x + 2y = 86`, `3y = 5x`, `x = 8`, `y = −(1/9)x` | a row `(coefficients, constant)`, everything moved left of the equals sign |
| `eq1, eq2` (one option) | a two-row system |
| `(−4, −8)` | an ordered pair of exact Fractions |
| `(r, −8r/7 + 9/7)` | two affine functions of the named parameter |
| `−11`, `2,300`, `9/7`, `3.5`, `(1/2)x` | a Fraction — the typeset minus, thousands separators and bracketed fractions are all handled |
| the SVG of a coordinate grid | two lines as `(slope, intercept)` |

The grid reader is the part worth stealing. It locates the origin from the two
`class="ax"` lines, gets pixels-per-unit from the spacing of the `class="gr"`
lines, and maps each `class="sg"` segment endpoint back to data coordinates. It
consults none of the item's parameters: it is what a reader with a ruler would
get, so it checks the picture against the options rather than checking the
options against each other.

## What it asserts

Every check is the same shape — classify all four, demand exactly one hit, demand
it is the keyed one — so a second correct answer fails as loudly as a wrong key.

| template | property, decided from the printed text |
|---|---|
| `sys.pick_no_solution` | each option's solution set from its two determinants; exactly one is the one the stem names (`no solution` or `infinitely many solutions`) |
| `sys.solve_pair` | exactly one printed point satisfies both printed equations |
| `sys.graph_solution` | the two drawn lines are recovered from the SVG and intersected; exactly one option names that point (or, when the options are systems, has it as its unique solution) |
| `sys.other_equation` | exactly one option, paired with the equation in the stem, gives a system with no solution |
| `sys.all_solutions` | exactly one parameterized point lies on both lines at r = 0, 1, −3 and 7/2 |

## What it caught

**One live defect.** `sys.pick_no_solution` draws its stem between "no solution"
and "infinitely many solutions". In the second case the pool still offered the
distractor whose second equation is the first multiplied by −1 — which has
infinitely many solutions too. Two correct answers:

```
Which of the following systems of linear equations in t and w has infinitely many solutions?
    −4t + 6w = 16,  4t − 6w = −16      <- many   (offered as a distractor)
    −4t + 6w = 16, −12t + 18w = 57     <- none
    −4t + 6w = 16,   6t − 4w = 16      <- one
    −4t + 6w = 16, −12t + 18w = 48     <- many   (the key)
```

The full gate passes this item. Coverage, transcript, acceptance, audit,
structure, prose and capacity are all green on it, because every one of them
stops at the key. The fix was a set of pool keys — `same_line`, `same_line_neg`,
`same_multiple` — that may never be offered against an "infinitely many" stem.

**Three injected faults**, because a check nobody has seen fail is worth nothing.
Rebuilding the option set above by hand, swapping a graph item's answer letter,
and duplicating the key into a second slot of a pair item are all caught, with
the message naming what went wrong.

## Running the same check on another topic

The reader is topic-agnostic; the assertions are not, and should not be. Three
things are needed.

1. **A property each option has or does not have, decided from its printed
   text.** This is the whole design. "Which system has no solution" becomes two
   determinants; "which expression is equivalent" becomes evaluation at several
   values; "which statement must be true" becomes the statement tested against
   the parameters. If the property cannot be decided from the printed option,
   the option set cannot be checked this way — say so rather than skipping
   quietly.

2. **A reader that shares nothing with the renderer.** Parse the string, do not
   re-render it and compare. A renderer bug that drops a minus sign will be
   invisible to any check that goes back through the renderer, and a distractor
   printed `x + 3y = 5` when it was meant to be `x + 3y = −5` is exactly the kind
   of defect this is for. `option_check.py` re-implements the printing rules it
   needs in about eighty lines; that duplication is the point.

3. **Both halves of the assertion.** `hits.count(True) == 1` catches the second
   correct answer; `hits[keyed]` catches the right answer attached to the wrong
   letter. Checking only the second is what the engine already does.

Two further notes from doing it here. Assert over generated *draws*, not over the
source items — the official option sets are the ones most likely to be right, and
the defect above only appeared in a stem variant no source item uses. And where a
figure carries part of the question, read the figure: recovering the drawn lines
from the SVG is the only check in this topic that can catch a picture and an
answer drifting apart, which is a failure mode `satbank check` has no way to see.
