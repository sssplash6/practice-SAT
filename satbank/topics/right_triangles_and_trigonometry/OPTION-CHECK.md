# Reading the figure and the wrong answers back

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct, and it never looks at the picture at all.

Nothing in the engine reads a wrong option as mathematics: `assemble` sorts four
values and records which one is the key, `audit` re-derives the key and compares,
`structure` counts surface forms and `prose` looks for placeholders. All of that
is satisfied by an item with two correct answers. And nothing anywhere opens the
SVG. In this topic **the figure carries the question** — the right-angle mark
says which vertex is which, the numbers beside the sides are the only numbers the
student has — so a figure that has drifted from its own stem is a wrong item that
every one of the seven checks calls green.

`option_check.py` closes both holes for the nineteen templates. It imports
`generate` and nothing else from the engine: no `Exact`, no `Surd`, no
`figures.py`, no template and no solver.

```bash
PYTHONPATH=. python3 satbank/topics/right_triangles_and_trigonometry/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 2000 --template rtt.trig_ratio
PYTHONPATH=. python3 .../option_check.py --selftest
PYTHONPATH=. python3 .../option_check.py --sources
```

```
  ok   rtt.pythagoras               2,000 items (1,990 with options), 0 defects
  ok   rtt.leg_expression           2,000 items (2,000 with options), 0 defects
  ok   rtt.rectangle_diagonal       2,000 items (1,174 with options), 0 defects
  ok   rtt.special_triangle         2,000 items (1,423 with options), 0 defects
  ok   rtt.special_perimeter        2,000 items (2,000 with options), 0 defects
  ok   rtt.equilateral_logo         2,000 items (2,000 with options), 0 defects
  ok   rtt.trig_ratio               2,000 items (1,394 with options), 0 defects
  ok   rtt.ratio_to_side            2,000 items (1,436 with options), 0 defects
  ok   rtt.cofunction_match         2,000 items (2,000 with options), 0 defects
  ok   rtt.cofunction_angles        1,978 items (1,978 with options), 0 defects
  ok   rtt.complement_tangent       2,000 items (2,000 with options), 0 defects
  ok   rtt.complement_ratio         2,000 items (2,000 with options), 0 defects
  ok   rtt.split_right_angle        2,000 items (    0 with options), 0 defects
  ok   rtt.similar_ratio            2,000 items (1,195 with options), 0 defects
  ok   rtt.similar_side             2,000 items (1,692 with options), 0 defects
  ok   rtt.similar_sides_ratio      2,000 items (1,492 with options), 0 defects
  ok   rtt.altitude_special         2,000 items (1,722 with options), 0 defects
  ok   rtt.nested_similar           2,000 items (1,201 with options), 0 defects
  ok   rtt.parallel_similar         1,399 items (  833 with options), 0 defects
  ok   the 33 official items            33 items, 0 defects
```

A grid-in is checked as an option set of one: the value the student must type has
to be the value the stem asks for, or nothing is right.

---

## The part worth stealing: reading the SVG back

Every figure in this topic is **drawn exactly to scale** from the item's own
parameters. That is not decoration and it is not for looks — it is the whole
reason the read-back means anything. A picture drawn to a fixed shape with the
numbers swapped in cannot be checked against those numbers by anybody; a picture
whose pixels *are* the mathematics can.

`Figure` in `option_check.py` is what a reader with a ruler and a protractor
gets. It consults no parameter of the item.

| recovered | how |
|---|---|
| **the three drawn vertices** | the `M x,y L x,y L x,y Z` of the triangle's `path` |
| **the right-angle mark's vertex** | the square is emitted as `M p1 L p2 L p3`, so the corner it marks is `p1 + p3 − p2`; that point is matched to a drawn vertex within 1 px |
| **the drawn side lengths** | the pixel distance between two recovered vertices |
| **which side each number names** | every `class="lb"` label is assigned to the segment midpoint it is *nearest*, competing against every other segment the figure draws |
| **the labelled angle** | every `class="an"` label is assigned to its nearest corner and read as degrees |
| **the vertex names** | every `class="vx"` label, assigned the same way |
| **the extra segments** | an altitude or a cut, from the `line class="ax"` elements |
| **the caption** | whether `class="nt"` is present at all |

`check_triangle` then asserts, on every item that carries a triangle:

* the right-angle square sits on a corner that is drawn at 90° ± 0.4°, and on the
  **only** such corner;
* every angle label that states a number is the angle actually drawn there, to
  0.6°;
* every pair of numerically labelled sides is drawn in the labelled ratio, to 1%.

On the composite figures a second layer applies: the altitude is perpendicular to
the base and its square is at the foot; the cut is square to the leg it crosses,
parallel to the other leg, and has both endpoints on the figure; and in
`nested_similar` the tangent the stem prints is the tangent the picture draws.

### Pixels assert, printed numbers decide

The first version of these checks computed the answer *from* the pixels and
compared it with the options at 3 × 10⁻³. That was too blunt. It reported two
draws as having two correct answers when the two options were 0.07% apart — `30`
against `52√3/3`, and `1,175/24` against `49`. Both are exactly distinguishable
and visually nothing alike; the check was wrong, not the items.

So the figure-carrying templates now do both halves separately:

* **decide** every option from the numbers the page prints, exactly, at 10⁻⁹ —
  `_solve_right` rebuilds all three sides of a right triangle from the two
  numbers on it, or from one number and one marked angle;
* **assert** that the drawn lengths are proportional to those numbers, to 0.5%.

A figure that has drifted fails the second half; a second correct option fails the
first. Neither can hide behind the other.

---

## What it parses

The reader is deliberately naive. It knows how an SAT page prints a right
triangle and nothing else. `Val` is a second, private implementation of
`a + b√d` — squarefree normaliser, rationalising division and all — so a printed
value and the `Exact` or `Surd` that produced it are compared through two
separate pieces of code.

| printed form | read as |
|---|---|
| `7.6`, `58`, `1,184`, `16/23`, `0.14` | an exact rational |
| `4√74`, `8√6`, `√17`, `125√3/2` | `a + b√d`; `√1,184` and `4√74` are one number |
| `3/√3` | the same `Val` as `√3` — the unsimplified spelling is not a different answer |
| `58 + 58√2`, `18 + 6√3` | a rational plus a radical, kept apart |
| `−√3/3` | the typeset minus is a minus |
| `√(21² − 6²)`, `21² − 6²`, `√(21 − 6)`, `(21² + 6²)/2` | hand-parsed and evaluated; no `eval` |
| `tan X`, `cos Y` | a function and a vertex, resolved against the drawn figure |
| `RS = 440` / `ST = 384` / `TR = 584` | three side lengths off a display block |
| `Triangle ABC is similar to triangle DEF, where A corresponds to D` | a correspondence, cross-checked against the order of the letters |

---

## What it asserts

Every check is the same shape — classify all four, demand exactly one hit, demand
it is the keyed one — so a second correct answer fails as loudly as a wrong key.

| template | property, decided from the printed text and the drawn figure |
|---|---|
| `rtt.pythagoras` | the third side, from the two the figure or the stem states; a *closest* stem picks the nearest printed option and refuses a tie |
| `rtt.leg_expression` | each printed expression evaluated and compared with the missing side |
| `rtt.rectangle_diagonal` | the diagonal and the stated side, through the theorem |
| `rtt.special_triangle` | the whole triangle rebuilt from what is printed on it, then the lettered side or the lettered angle read off |
| `rtt.special_perimeter` | the shape named in the stem gives the three ratios; the stated measure gives the scale |
| `rtt.equilateral_logo` | the triangles are **counted in the SVG**, the shaded ones counted separately, and both checked against the stem's own words |
| `rtt.trig_ratio` | all three sides resolved from the figure's labels plus any the stem adds, then the ratio at the named or marked vertex — and the figure must draw that same ratio |
| `rtt.ratio_to_side` | the angle recovered from the printed ratio with an inverse function, then the side |
| `rtt.cofunction_match` | all six ratios computed from the drawn legs; an option is right iff it *is* the one the stem names, found rather than recited |
| `rtt.cofunction_angles` | each printed value of x tested in `cos Q = sin R`, with both angles required to be acute |
| `rtt.complement_tangent` | the reciprocal of the printed tangent |
| `rtt.complement_ratio` | the complement's ratio, through `asin`/`acos`/`atan` |
| `rtt.split_right_angle` | solved on the drawn coordinates at three positions of W, so the answer is *shown* to be independent of where W lies rather than asserted to be |
| `rtt.similar_ratio` | the correspondence read from the stem, checked against the letter order, and the angle walked through it |
| `rtt.similar_side` | the tangent and the leg, with the right angle identified from the sentence that names it |
| `rtt.similar_sides_ratio` | the three printed sides checked to be a right triangle, the right angle found as the shared vertex, the correspondence taken from the triangle names and cross-checked against the sentence |
| `rtt.altitude_special` | the two marked angles fix the shape, the one labelled side fixes the scale, and every segment of the figure is checked against that shape |
| `rtt.nested_similar` | the big triangle from the stem's tangent and hypotenuse, the small one from the cut, every segment checked against the picture |
| `rtt.parallel_similar` | the scale from the two parallel segments the figure labels, then every segment of both triangles |

---

## What it caught

### Three figures that disagreed with their own stems

All three are items the full gate passes: coverage, transcript, acceptance,
audit, structure, prose and capacity are green on every one of them, because all
seven stop at the key and none of them opens the SVG.

* **`rtt.pythagoras`, the hypotenuse-and-leg variant.** The figure labelled the
  leg running from the right angle to `p` with the value of the *known* leg —
  but that leg is drawn as the *unknown* third side. The picture's short side
  carried the long side's number. The labels now go on `q` and the hypotenuse,
  which are the two sides the stem actually states.
* **`rtt.leg_expression`.** The same class of defect: the triangle was built as
  `(third, small)` while the labels were placed as `(small, third)`, so the leg
  labelled `6` was drawn twenty units long.
* **`rtt.ratio_to_side` with a figure.** The figure was drawn as
  `right_triangle(opp, adj)` with `p` and `q` named `Y` and `X` — which puts the
  leg *opposite* X on the side running to X. Opposite and adjacent were swapped,
  so the drawn triangle was the mirror of the one the printed ratio describes.

### Angle labels a reader could attribute to the wrong vertex

`_text` pushed every label ten pixels clear of the line it names. On an angle
label that push is applied *after* the offset along the bisector, and on a thin
triangle it carried the label past its own corner: the `x°` beside an acute angle
landed nearer the right-angle vertex than nearer its own. Six defects in a
thousand draws of `rtt.trig_ratio`, reported as *"the stem asks for a ratio at the
right angle"*. An angle nobody can attribute is a question nobody can answer.

Fixed in `figures.py`: the bisector offset shrinks with the shorter of the two
sides meeting at the corner, the text is centred rather than pushed clear, and a
figure that marks an angle is refused unless its legs are within 1 : 6.

### Label collisions in the cut figures

A number printed beside a line names that line — so two segments whose middles
are almost on top of each other make a figure nobody can read. In
`rtt.parallel_similar` the `30` labelling the cut `BD` sat nearer the middle of
the hypotenuse piece `CD` than nearer its own: 67 defects in 400 draws. The fix
is `_readable()` in `figures.py`, which takes every label the figure is about to
write, works out where it will sit, and refuses the draw unless it is nearer its
own segment than any other by a margin of 1.35. It now guards `right_triangle`,
`cut_right_triangle` and `altitude_triangle` alike.

### A clipped caption, a glyph, and a label on a line

Three more found by eye on `tools/preview.py`, none of them visible to any check.

* A thin triangle produced an SVG narrower than its own caption, so the page
  printed `te: Figure not drawn to sca`. A figure is now widened to at least
  210 px when it carries a note, and the drawing centred in it.
* `rtt.parallel_similar` wrote its rationale with `∥`, which the preview font
  renders as a single bar — `DE ǀ KL`. It says "is parallel to" now. A glyph the
  page cannot draw is not typography, it is a typo.
* The label on the cut was pushed *away from the right angle*, which on these
  figures is straight onto the small triangle's hypotenuse. It is pushed the
  other way now, into the empty quadrilateral between the cut and the right
  angle.

### A vertex name printed on top of a length

`_readable` compared side labels against segments, but nothing compared them
against the letters naming the corners — so a short piece of a leg could have its
length printed under its own endpoint's letter, `16D`. The rule now takes every
label the figure is about to write, side lengths and vertex letters alike, and
refuses the draw unless all of them are at least 17 px apart.

### Two degenerate items whose answer the figure already printed

Also found by eye. In `rtt.altitude_special`, when the marked apex angle and the
marked base angle are complementary the triangle is isosceles, so `AB = BC` — and
an item asking for `AB` has its answer already printed on `BC` in the picture. Two
of the three items on the preview page were that item. A draw whose key equals the
side the figure states is now refused.

### Two rationales that restated the answer

Both found by eye, both the same shape — a closing clause that repeated the
quantity it had just derived:

* `rtt.altitude_special` asking for the altitude: *"…BD = 12·sin 60° = 6√3, and
  then BD = 6√3."*
* `rtt.parallel_similar` asking for `CD`: *"…With CD = 34, CD = 34."*

Both closings are now conditional on the asked segment not being the one just
derived. A third, in `rtt.special_triangle`, said *"A 45-45-90 triangle with 34
for its leg has 34 for the side asked for"* and was replaced with one that names
the side ratio and says which leg is which.

### One item design nobody could defend

`rtt.equilateral_logo` could ask for the area of the *entire* logo while the
figure shaded part of it and the stem never mentioned the shading. The template
now asks only about the shaded region, which is what the shading is for.

### Collisions that never reach the page

A named pool offers every wrong route it knows, and at particular parameters some
of those routes land on the key. Over 300 draws of each template, 30 distinct
pool entries collide with the key at least once — and `assemble` drops every one
of them, because it dedupes by value before it renders. Three with their exact
mechanism:

* `rtt.altitude_special`, `other_piece` (56 draws in 300): "gave the other piece
  of the base" equals the key exactly when `AD = DC`, which is when the marked
  apex angle and the marked base angle are complementary.
* `rtt.trig_ratio`, `diff_over_hyp` (5 in 300): "took the difference of the two
  given lengths for the third side" equals the key exactly when the hypotenuse is
  twice the labelled leg, so that `(c − q)/c` and `q/c` are one number.
* `rtt.special_triangle`, `third_side` (5 in 300): "gave the third side" equals
  the key on a 45-45-90 draw, where the two legs are the same length.

A further group is structural rather than accidental: `rtt.special_perimeter`
names all four measures of the triangle in its pool, so whichever one the stem
asks for is the key and is dropped. That is the pool doing its job. The sweep
confirms that across every draw the nineteen templates can make, the four options
stay distinct and exactly one is right.

---

## Ten injected faults

A check nobody has seen fail is worth nothing. `--selftest` builds each of these
by hand and confirms each is caught — 10/10.

| injected | what it proves | caught with |
|---|---|---|
| the key a second time as `√1,184` beside `4√74` | the reader compares numbers, not strings | *2 of the options are the third side* |
| the key moved to another letter | `hits[keyed]`, the half the engine already does | *the key is A) '48/73', but the option that is tan W is D) '55/48'* |
| the key printed without its denominator | zero correct options fails as loudly as two | *0 of the options are tan A* |
| a figure spliced from a draw at other lengths | the picture is read, not trusted | *0 of the options are sin x°* |
| the right-angle square drawn on the wrong corner | the mark's vertex is recovered from pixels | *the right-angle square is drawn on a 59.7° corner* |
| **a marked angle that is not the angle drawn** | a label that lies about its own corner | *the corner labelled 30° is drawn at 45.00°* |
| a triangle drawn out of proportion to its labels | drawn lengths against printed ones | *the sides labelled 3 and 7 are drawn 162.9 and 190.0 pixels long* |
| two options equally close on a *closest* stem | the halfway guard, on the printed page | *two printed options are equally close to 7.615773105863909* |
| **a correspondence the letter order contradicts** | similarity is a correspondence, not a pair of names | *the stem says A corresponds to E, but the order of the letters pairs it with D* |
| a parallel segment drawn out of parallel | the cut's own geometry | *the cut does not end on the hypotenuse* |

The two in bold are the ones this topic exists to catch. **The lying angle
label** is the failure mode no gate can see: the stem is right, the key is right,
the audit re-derives the key from the parameters and agrees — and the student is
looking at a picture that says something else. **The scrambled correspondence** is
the one that is silent in a different way: "triangle ABC is similar to triangle
DEF, where A corresponds to D" is not decoration, and a template that pairs A with
E instead produces an item whose answer is the complement of the keyed one, with
every number in the stem unchanged.

---

## Exact to the printed page

Every length, ratio and radical in this topic is an `Exact` (or a `Surd`) from
the draw to the printed string. `float` appears in the templates in four places
and nowhere else: to *order* options, inside the shared `assemble`; to size and
shape a figure; in a comparison or a guard; and in `params`, which exists to feed
`audit.py`, whose whole job is to be a separate numeric route.

The one deliberate rounding is `kit.places_text`, for the source items that print
a decimal — and even that rounds an `Exact` to an `Exact` rational first
(`_round_to`), so the value the audit re-derives and the value the page prints
are the same number. `kit.closest_only` then refuses any draw whose printed
options cannot single the key out.

Writing this note found the last leak: `kit.exact_leg`, which computes the third
side of a right triangle, took its arguments as floats and did `int(hyp) ** 2`.
For the magnitudes here that is exact, but it is exactly the round-trip the rule
exists to forbid. It now takes `Exact`s and works in `Fraction`s, via a small
`kit.rational` helper — so `√(53² − 52²)` is `√105` because 2,809 and 2,704 are
integers, not because two doubles subtracted to something near 105.

---

## `kit.Surd` — the one place this topic reaches outside the shared core

**What it is.** A small exact type, `a + b√d`, with `a` and `b` exact
`Fraction`s and `d` a squarefree positive integer. It supports the four
operations, including division by another surd, which it rationalises through the
conjugate. It lives in `kit.py`, local to this topic. `exact.py` was not touched.

**Why `Exact` could not do it.** `Exact` is `coef · π^e · √rad` — one rational
coefficient, one radical. That covers every answer in this topic but one shape:
a rational **added to** a radical, which cannot be folded into a single
coefficient. Official item 3.16 is exactly that shape:

> An isosceles right triangle has a hypotenuse of length 58 inches. What is the
> perimeter, in inches, of this triangle?
> A) 29√2  B) 58√2  **C) 58 + 58√2**  D) 58 + 116√2

The leg is `58/√2 = 29√2` and the perimeter is `58 + 58√2`. There is no
`coef · √rad` that is that number. Three more official items — 3.12, 3.13 and
3.19 — print a surd *perimeter* in the stem and need the same arithmetic to undo
it: `(94 + 94√2) / (2 + √2)` has to come out as exactly `47√2`, and it does,
through the conjugate.

**How it keeps the shared audit working unchanged.** `Surd` implements
`__float__` and `.plain()`, which are the only two things `satbank/audit.py`
asks of `item.key`:

```python
got = float(item.key)                       # Surd.__float__
...
if keyed != item.key.plain():               # Surd.plain() -> "58 + 58√2"
```

So `Item.key` holds the `Surd` itself, the topic's own solver returns a plain
float, and the shared numeric audit path runs over it with no special case
anywhere. `kit.assemble_surd` mirrors `item.assemble` on the same contract —
distinct values, ascending order, and the key never the only option of its
surface form.

**For whoever promotes it.** This is a candidate for `exact.py`. The requirement
is not "support addition" — it is that a value of the form `a + b√d` must

1. stay exact from the draw to the printed string, never rounding;
2. print as the source prints it — `58 + 58√2`, not `58 + 82.02` and not
   `58(1 + √2)`;
3. divide by another surd exactly, because a stem states a perimeter and the
   template has to undo it;
4. answer `float()` and `.plain()`, because that is the whole of the contract
   `satbank/audit.py` has with `item.key`;
5. expose a surface signature, so an assembler can keep the key from being the
   only option of its form.

Everything else in `Surd` is convenience.

---

## Three notes for the next topic

**Draw the figure to scale, even when the source says not to.** "Note: Figure not
drawn to scale." is a disclaimer to the student, not an instruction to the
renderer. Reproducing the note where the source prints it costs nothing; drawing
the figure truthfully underneath it is what makes the whole read-back possible.
Every one of the three stem-disagreeing figures above was invisible until the
pixels could be compared against the numbers.

**Assign each label to the segment it is nearest, and make the renderer honour
that.** The reader's rule — a number beside a line names that line — is the only
rule a student has. Once the checker used it, it immediately found figures where
the rule gives the wrong answer, and the fix belonged in `figures.py`, not in the
checker. A figure whose labels cannot be attributed is a bad figure whatever the
mathematics behind it says.

**Check generated draws, and check the source items too.** The angle-attribution
defect lives in stem variants no official item uses, which is the argument for
`--draws 2000`. The argument runs the other way as well: two option shapes here —
the unsimplified `3/√3` of item 3.9 and the `√3` tangent of item 3.6, whose
option set College Board prints as three radicals around one integer — are
reachable only from the encoded source parameters. Without `--sources` nothing
would ever read them as mathematics.
