# Reading the wrong answers back

`satbank check` asks whether the key is right. It never asks whether a
distractor is *also* right.

Nothing in the engine reads a wrong option as mathematics. `assemble` sorts four
values and records which one is the key; `assemble_text` shuffles four strings
and does the same; `audit` re-derives the key and compares; `structure` counts
surface forms and `prose` looks for placeholders. All of that is satisfied by an
item with two correct answers, and by an item whose key answers a different
question from the one the stem prints. The hole is structural, not a gap someone
forgot to fill: an option that no code ever solves cannot be found wrong by any
amount of solving the key.

`option_check.py` closes it for this topic. It parses the printed stem, the four
printed options and — where a figure carries part of the question — the SVG's own
pixel geometry back into circle geometry, decides each option's status from that
geometry alone, and asserts that exactly one option has the property the stem
asks for and that it is the keyed one.

```bash
PYTHONPATH=. python3 satbank/topics/circles/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 2000 --template circles.arc
PYTHONPATH=. python3 .../option_check.py --selftest
PYTHONPATH=. python3 .../option_check.py --sources
```

```
  ok   circles.arc                  600 items (454 with options), 0 defects
  ok   circles.arc_pair             600 items (489 with options), 0 defects
  ok   circles.arc_fraction         600 items (238 with options), 0 defects
  ok   circles.arc_angle            600 items (220 with options), 0 defects
  ok   circles.chord_angle          600 items (540 with options), 0 defects
  ok   circles.sector               600 items (512 with options), 0 defects
  ok   circles.degree_radian        600 items (351 with options), 0 defects
  ok   circles.unit_circle_angle    600 items (600 with options), 0 defects
  ok   circles.coterminal           600 items (600 with options), 0 defects
  ok   circles.exact_trig           600 items (600 with options), 0 defects
  ok   circles.equation_read        600 items (525 with options), 0 defects
  ok   circles.equation_write       600 items (511 with options), 0 defects
  ok   circles.point_on             600 items (443 with options), 0 defects
  ok   circles.interior             600 items (600 with options), 0 defects
  ok   circles.tangent_slope        600 items (600 with options), 0 defects
  ok   circles.transform            600 items (372 with options), 0 defects
  ok   the 32 official items         32 items, 0 defects
```

A grid-in is checked as an option set of one: the value the student must type
has to be the value the stem asks for, or nothing is right. The first failing
draw of each defect below was a grid-in.

## What it parses

The reader is deliberately naive. It knows how an SAT page prints a circle and
nothing else — no `Exact`, no `render.py`, no `figures.py`. `generate` is the
only thing it imports from the engine, and only to obtain the finished item, in
the state a student would receive it. `Val` is a second, private implementation
of `coef * pi**e * sqrt(rad)`, squarefree normaliser and all, so that a printed
value and the `Exact` that produced it are compared through two separate pieces
of code.

| printed form | read as |
|---|---|
| `36`, `2,592π/5`, `π/3`, `-13π/2`, `√2/2`, `√40`, `0.5`, `135/8` | an exact `Val` — `√40` and `2√10` are one number |
| `13/2 π` | the same `Val` as `13π/2`; the stacked-fraction spelling is not a different answer |
| `(3, -15)`, `(3/2, -1/2)` | an exact ordered pair |
| `(x - 3)² + (y + 15)² = 1`, `x² + (y - 7)² = 64` | a centre and a right-hand side, with `x²` and `(x - 0)²` reading alike |
| `5x² - 30x + 5y² + 150y = -1,165`, `8x² + 112px + 8y² - 64py = -448p²` | the same, after completing both squares — a symbol on the coefficients folded to 1 and its name kept |
| `144p²` versus `144p` | `(144, p, 2)` versus `(144, p, 1)` — r² = 144p² is a radius of 12p and r² = 144p is not |
| a `circle_with_points` SVG | the centre, the radius, every labelled point's bearing, every drawn radius and chord, and the marked central angle with its sweep |
| a `circle_on_grid` SVG | the plotted circle's centre and radius in data units |

The two figure readers are the part worth stealing. `dial` takes the centre and
radius from the drawn circle, converts every `class="pt"` marker to a bearing
with `atan2`, and reads the marked angle off the `A`-command endpoints of the
arc marker — checking the large-arc flag against the span it computed, so a
reflex angle drawn as an acute one is caught. `grid_circle` locates the origin
from the two axes, gets pixels-per-unit from the gridline spacing, and maps the
plotted circle back. Neither consults a single parameter of the item: they are
what a reader with a protractor and a ruler would get, so they check the picture
against the options rather than the options against each other.

## What it asserts

Every check is the same shape — classify all four, demand exactly one hit,
demand it is the keyed one — so a second correct answer fails as loudly as a
wrong key.

| template | property, decided from the printed text and the drawn figure |
|---|---|
| `circles.arc` | the arc named, as a share of the circumference the stem prints; the share comes from the angle the **figure** marks, and `minor arc` means the shorter of the two arcs whatever that angle is |
| `circles.arc_pair` | the two arcs sum to the circle; the figure's split must match the stem's ratio, the marked angle must equal the stated `x`, and the letter naming each arc must sit on the right side of the mark |
| `circles.arc_fraction` | the printed arc divided by 2πr, which must come out rational |
| `circles.arc_angle` | an arc and its central angle have one measure; `minor` and `major` are then taken at their word, and a minor arc over 180° is a contradiction |
| `circles.chord_angle` | 180 − 2·base, cross-checked against the angle the figure draws; the segment whose length is given must be drawn as a radius, and the chord must be drawn |
| `circles.sector` | θ/360 of πr², or the angle back out of a printed area |
| `circles.degree_radian` | 180° is π radians, in whichever direction the stem runs it |
| `circles.unit_circle_angle` | the angle the **figure** leaves between the two marked ones, after checking that the two outer points are a diameter apart and that each marked angle is drawn at the size the stem states |
| `circles.coterminal` | the second point's bearing is solved off the circle; an option is right iff 180·c degrees lands on it, so **every** odd multiple of π counts, not merely the keyed one |
| `circles.exact_trig` | whole turns come off the printed angle exactly, then cos or sin of what is left |
| `circles.equation_read` | centre, radius or diameter completed out of the printed coefficients; for the symbolic form, that the constant the stem names is the one the equation carries |
| `circles.equation_write` | centre **and** r² as values, so two spellings of one circle are one answer and `= 144p` is a different circle from `= 144p²` |
| `circles.point_on` | the coordinate the circle forces (and that it forces only one), or the far end of the printed diameter |
| `circles.interior` | the squared distance of every printed point from the centre, against r² |
| `circles.tangent_slope` | the negative reciprocal of the radius through the printed point |
| `circles.transform` | circle A as printed **and** as plotted, then slid or grown; options compared as circles, not as strings |

## What it caught

**Two live defects, one family.** The engine treated the stated or marked
central angle as "the minor arc" however large it was. In both templates the
correct answer was already sitting in the option set as a distractor, and the
whole gate — coverage, transcript, acceptance, audit, structure, prose and
capacity — was green on every one of them, because all seven stop at the key.

`circles.arc_angle`, 111 defects in 400 draws — better than a quarter of
everything the template made:

```
In a circle with center O, central angle AOC measures 316°. What is the measure, in degrees, of minor arc AC?
    A) 44     <- offered as "gave the major arc instead of the minor one"; it is the minor arc, and the answer
    B) 79
    C) 158
  * D) 316    <- the key: the major arc

In a circle with center O, minor arc AC measures 286°. ...     <- a minor arc cannot measure 286°
Point O is the center of a circle ... angle POQ is 221°. What is the measure of major arc PQ?
  * B) 139    <- the key: the minor arc. 221, offered as a distractor, is the major one.
```

`circles.arc`, 10 defects in 400 draws, all with the figure carrying the angle:

```
[figure: two radii, the 300° angle between them marked and labelled]
The circle above with center O has a circumference of 54 feet.
What is the length, in feet, of minor arc BC?
    A) 9      <- offered as "gave the rest of the circle, the major arc"; it is the minor arc, and the answer
    B) 27
  * C) 45     <- the key: 300/360 of the circle, which is the major arc
    D) 54
```

Both are in the same figure the student sees, and neither is visible to anything
that stops at the key. The fixes are in `families/arc.py`:

* `arc` drops the word "minor" when the marked angle is not under a half turn —
  the arc the marked angle cuts is still the answer, it is just not the minor
  one, so the stem stops claiming it is;
* `arc_angle` rejects a draw that asks for a major arc when the angle it was
  given is already the reflex one, and uses the plain wording when a central
  angle over 180° is quoted;
* the distractor that swaps the two arcs now names itself by which arc it
  actually is, instead of always claiming to be the major one.

The gate is unchanged by the fix: `PASS`, 32/32 official answers, 89% of
official distractors recreated, capacity 18,008 (from 18,017).

**One near miss, already handled.** At radius 2 the arc length of a sector and
its area are the same number — `2πr·θ/360` and `πr²·θ/360` coincide — so the
"found the arc length, not the sector area" distractor *is* the key there.
`assemble` drops it, because it dedupes by value before it renders; the check
confirms that over all 1,584 radius-and-angle pairs the template can draw, the
four options stay distinct and exactly one is right. Two more collisions end the
same way: in `exact_trig` the "gave the sine instead" distractor equals the key
at 45° and 225°, where cosine and sine agree (the reference-angle distractor
never can — it is built on the other radical), and in `equation_read` the
swapped-coordinate distractor equals the key on the diagonal h = k, where
`assemble_text` dedupes by string. Every one of these is a distractor that
becomes the key at particular parameters; none of them survives to the page.

**Ten injected faults**, because a check nobody has seen fail is worth nothing.
`--selftest` builds each by hand and confirms each is caught:

| injected | what it proves |
|---|---|
| the key's value a second time as `5/2 π` beside `5π/2` | the reader compares numbers, not strings |
| the keyed circle a second time as `(x - 0)²` beside `x²` | two spellings of one circle are one answer |
| a fourth point that is also outside the circle | `interior` counts all four, not just the key |
| the key a second time with an ASCII `sqrt` for `√` | the radical spelling is not a second answer |
| a reflex marked angle whose arc the stem calls minor | the defect above, put back by hand |
| the key moved to another letter | `hits[keyed]`, the half the engine already does |
| the key's minus sign dropped in rendering | zero correct options fails as loudly as two |
| an arc figure spliced from a draw at another angle | the picture is read, not trusted |
| a grid figure plotting a circle the equation does not describe | same, for the xy-plane |
| a unit-circle figure whose marked angles are not the stated ones | same, for the angles a stem quotes |

## Two notes for the next topic

**Check generated draws, not just the source items** — but check those too. The
defect above lives in stem variants no official item uses, which is the whole
argument for drawing at volume. The argument runs the other way as well: two
option shapes in this topic, a radius written as a multiple of a constant
(`7k`) and a radius given by a point on the circle, are reachable only from the
encoded source parameters, and no `generate` call will ever produce one. Without
the `--sources` pass those option sets would never be read by anything.

**A renderer's spelling can outrun the engine's own reader.** `render.pi_front`
prints `2/3 π`, which is how College Board prints it and how two official items
(2.4 and 2.8) are reproduced — but `item.numeral` cannot read it, so the shared
`audit` would reject such an item if one ever came out of `generate`. It never
does: no template randomises `style`, so the front spelling is reachable only
through the encoded source parameters, which `check` builds without auditing.
The option check reads those two option sets and finds each one uniquely
correct, which makes it the only thing in the repo that verifies them as
mathematics. Worth knowing before anyone randomises `style`.
