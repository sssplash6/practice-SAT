# Reading the wrong answers back

`satbank check` asks whether the key is right. It never asks whether a
distractor is *also* right.

Nothing in the engine reads a wrong option as mathematics. `assemble_text` takes
four strings, shuffles them and records which one is the key; `audit` re-derives
the key and compares; `structure` counts surface forms and `prose` looks for
placeholders. All of that is satisfied by an item with two correct answers. For
the templates whose options are *values*, `assemble` closes the hole by
accident — two options that are the same number are the same option, and it
throws one away. For the templates whose options are **expressions** nothing
does, because `2(6 + 3)` and `6 * 3` are different strings and the same number.

There is a second hole of the same shape. Five of this topic's templates put
the question in a picture: the plotted points *are* the circle, the drawn
segment *is* the leg, the two rectangles carry their measurements as labels.
`audit` re-derives the answer from the parameters the figure was meant to be
drawn from, so a figure that disagrees with its own answer passes every check
the engine has.

`option_check.py` closes both. It parses the four printed option strings, the
printed stem, and — for the items with a figure — the drawn SVG, back into
arithmetic; decides each option's status from that arithmetic alone; and asserts
that exactly one option has the property the stem asks for and that it is the
keyed one.

```bash
PYTHONPATH=. python3 satbank/topics/area_and_volume/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 6000 --template scaling.solid
PYTHONPATH=. python3 .../option_check.py --self-test
```

```
  ok   expression.measure            4,000 items, 0 defects   (rectangle area)
  ok   expression.symbolic_volume    4,000 items, 0 defects   (square prism volume)
  ok   scaling.solid                 4,000 items, 0 defects   (the scaled volume)
  ok   coord.circle_3pt              4,000 items, 0 defects   (the drawn circle)
  ok   coord.triangle_area           4,000 items, 0 defects   (the drawn triangle, entered)
  ok   coord.square_diagonals        4,000 items, 0 defects   (the drawn quadrilateral's area)
  ok   coord.leg_from_area           4,000 items, 0 defects   (the other leg of the drawn triangle)
  ok   similar.linear                4,000 items, 0 defects   (the stated ratio)
```

## What it parses

The reader is deliberately naive. It knows how an SAT page prints an arithmetic
or algebraic expression, and how `figures.py` lays out a grid, and nothing else
— no `Exact`, no `shapes.py`, no `Mis`. `generate` is the only thing it imports
from the engine, and only to obtain the finished item.

| printed form | read as |
|---|---|
| `3 * 39`, `2 · 94 · 94` | a product of factors |
| `2(6 + 3)`, `π(2r)³`, `(s + 4)³` | a coefficient times a bracketed sum, to a power |
| `V = πr³ + 4πr²` | a sum of signed terms: a number, times π, times a power of the variable |
| `8√2`, `√(2π)`, `104/3`, `1,875/2`, `8.75` | a number; the thousands separator is dropped |
| `a height that is 4 inches longer than the radius` | the function `h(r) = r + 4` |
| `twice the radius and half the height` | the factors 2 and ½ |
| `a volume that is 63 times as large` | the multiple 63 |
| the SVG of a coordinate grid | the plotted points and drawn segments, in data coordinates |
| the SVG of two similar rectangles | the three side measurements printed on the figure |

Every algebraic option is evaluated at four probe values of the variable (2, 3,
5 and 7), so two expressions count as the same answer when they are the same
*function* — which is exactly the second defect below.

The grid reader is the part worth stealing. It locates the origin from the two
`class="ax"` lines, gets pixels-per-unit from the spacing of the `class="gr"`
lines, and maps each plotted `class="pt"` circle and each `class="sg"` segment
endpoint back to data coordinates. It consults none of the item's parameters:
it is what a reader with a ruler would get, so it checks the picture against the
options rather than the options against each other.

## What it asserts

Every check is the same shape — classify all four, demand exactly one hit,
demand it is the keyed one — so a second correct answer fails as loudly as a
wrong key. A grid-in has no options, so there the figure is checked against the
answer the student is expected to enter, which is a check `satbank check` cannot
make at all.

| template | property, decided from the printed text and the picture |
|---|---|
| `expression.measure` | the stem's own numbers give the area or perimeter it asks for; exactly one printed expression is worth it |
| `expression.symbolic_volume` | the stem's sentence gives the height as a function of the base dimension; exactly one printed expression is πr²h (or s²h) at every probe value — and no option may use a letter the stem never defines |
| `scaling.solid` | *which pair*: exactly one printed `R = ar and H = bh` has a²b equal to the stem's multiple. *volume multiple*: exactly one printed number is the stem's volume times (radius factor)² times the height factor |
| `coord.circle_3pt` | the circle through the three plotted points is constructed from the pixels; exactly one option is its 2r (or r²) |
| `coord.triangle_area` | the three plotted points give an area by the shoelace formula; exactly one option is it |
| `coord.square_diagonals` | the four drawn sides are walked round into a quadrilateral; exactly one option is the area, side or perimeter the stem asks for |
| `coord.leg_from_area` | the drawn segment's length, with the area the stem states, gives the other leg; exactly one option is it |
| `similar.linear` | the ratio comes off whichever of the figure's three labels, the table's two perimeters, or the sentence's own numbers the item uses; exactly one option is the scaled length or perimeter |

## What it caught

**Two live defects**, both items with two correct answers, both of which passed
the full gate.

`expression.measure` offers "found the perimeter" against an area stem. For a
6 by 3 rectangle the perimeter *is* the area:

```
A rectangle has a length of 6 centimeters and a width of 3 centimeters.
Which expression gives the area, in square centimeters, of this rectangle?
    2(6 + 3)      <- 18, offered as "found the perimeter"
    6 * 3         <- 18, the key
    2(6 * 3)      <- 36
    6 + 3         <- 9
```

It happens whenever `2(l + w) = lw` — (3, 6), (4, 4), (6, 3) — and on a
perimeter stem wherever `2(l * w) = 2(l + w)`, and at `l = w = 2`, where the sum
and the product are both 4. Three defective items in 6,000 draws.

`expression.symbolic_volume` offers "doubled the radius instead of using the
stated height", `V = π(2r)³`. That is 8πr³, which is the answer whenever the
stem says the height is 8 times the radius:

```
... right cylindrical drums with a height that is 8 times the radius ...
    V = πr² + 8πr
    V = πr² + 8
    V = π(2r)³    <- 8πr³, offered as a distractor
    V = 8πr³      <- 8πr³, the key
```

57 defective items in 6,000 draws — about one in a hundred, and every one of
them shippable as far as the seven gate checks are concerned.

Both fixes are in the generator, and both are the same rule: an option is
rejected when it has the same *value* as the key, not merely when it has the
same text. `expression_measure` carries the number each expression is worth and
refuses a draw in which two of the four coincide; `symbolic_volume` compares
each candidate against the key at four values of the variable.

**Four injected faults**, because a check nobody has seen fail is worth nothing.
`--self-test` rebuilds a real item with a second correct expression, moves a key
to the wrong letter, offers the key twice, and gives a triangle item another
item's picture. All four are caught, with a message naming what went wrong:

```
  ok   caught a second correct expression: 2 of the four options are correct
  ok   caught the key on the wrong letter: the keyed option is not the correct one
  ok   caught the key offered twice: 2 of the four options are correct
  ok   caught a figure that drifted from its answer: 0 of the four options are correct
```

## Where the check stops

The other eleven templates build their options with `assemble`, which compares
`Exact` values and cannot offer the same number twice: an option that is also
correct would have to *be* the key, and it is thrown away instead. The two
figures they do draw — the cylinder with r and h marked, and the triangle with
x, y and z marked — label their sides with letters the stem defines, not with
measurements, so there is no number on the page that could drift away from the
answer.
