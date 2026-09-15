# Reading the wrong answers back

`satbank check` asks whether the key is right. It never asks whether a
distractor is *also* right.

Nothing in the engine reads a wrong option as mathematics. `assemble_text` takes
four strings, shuffles them and records which one is the key; `audit` re-derives
the key and compares; `structure` counts surface forms and `prose` looks for
placeholders. All seven gate checks are satisfied by an item with two correct
answers. The hole is structural, not a gap someone forgot to fill: an option that
no code ever solves cannot be found wrong by any amount of solving the key.

`option_check.py` closes it for all twenty-two templates. It parses the four
printed option strings — and the printed stem, and the printed table — back into
arithmetic, decides each option's status from that alone, and asserts that
exactly one option has the property the stem asks for and that it is the keyed
one.

```bash
PYTHONPATH=. python3 satbank/topics/ratios_rates_proportions_and_units/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 2000 --template rr.simplify
PYTHONPATH=. python3 .../option_check.py --selftest
PYTHONPATH=. python3 .../option_check.py --sources
```

```
  ok   rr.partner             1,605 items, 0 defects   (the partner of the given term)
  ok   rr.equivalent          1,117 items, 0 defects   (the missing term)
  ok   rr.table_constant      1,580 items, 0 defects   (the constant ratio applied)
  ok   rr.simplify            2,000 items, 0 defects   (the ratio of the two counts)
  ok   rr.similar_rect        2,000 items, 0 defects   (the width that keeps the ratio)
  ok   rr.dimension_shift     2,000 items, 0 defects   (the matching change, in size and direction)
  ok   rr.mix_statement       2,000 items, 0 defects   (the one description that keeps the ratio)
  ok   rr.expression          2,000 items, 0 defects   (the substitution carried through)
  ok   rr.multiple            2,000 items, 0 defects   (how many times, free of k)
  ok   rr.chain_unknown         930 items, 0 defects   (the constant between the two ratios)
  ok   rr.repeated_factor       979 items, 0 defects   (the deposit run backwards)
  ok   rr.unit_rate           1,443 items, 0 defects   (the distance over the speed)
  ok   rr.rate_convert        1,303 items, 0 defects   (the nearest tenth of a mile per hour)
  ok   rr.rate_product        1,364 items, 0 defects   (approximately, to two figures)
  ok   rr.gap                 1,399 items, 0 defects   (the base times the difference)
  ok   rr.growth_table        2,000 items, 0 defects   (the closest tenth of an inch)
  ok   rr.table_unit_price    1,864 items, 0 defects   (the ratio of the two unit prices)
  ok   rr.exchange_fee        1,868 items, 0 defects   (the conversion, less the fee)
  ok   rr.convert             1,432 items, 0 defects   (the factor applied 1 time(s))
  ok   rr.convert_chain       1,185 items, 0 defects   (both factors applied in turn)
  ok   rr.pop_density         1,304 items, 0 defects   (the population over the density)
  ok   rr.cube_density        1,197 items, 0 defects   (the nearest whole number of kilograms)
```

34,570 generated items, and the 36 official option sets under `--sources`.

## What it parses

The reader is deliberately naive and shares nothing with the renderer. It knows
how an SAT page prints a ratio, a rate and a converted measure, and nothing else.
`generate` is the only thing it imports from the engine, and only to obtain the
finished item, in the state a student would receive it.

| printed form | read as |
|---|---|
| `56.7`, `2,604`, `$8,948.61`, `3/20`, `−5` | an exact Fraction |
| `5 to 8`, `10 : 11` | the rational the ratio names, so two spellings of one ratio compare equal |
| `8(9.07z)`, `6z + 19.78z`, `(29/27)w`, `w − 13`, `40n`, `t/186`, `2k` | a function of one variable, by parsing and evaluating |
| `It must increase by 47.2 units.` | a direction and a size |
| `1.5 times the amount of blue paint used in the second batch` | an amount, resolved against the two batches the stem describes |
| `25 meters per second` | a value and the unit it carries |
| a printed table | rows of exact values, addressed by the heading the stem names |

The expression reader is the part worth stealing. It is a real recursive-descent
parser — sum, product, unary, atom, with juxtaposition as multiplication — not a
list of shapes, and every option is decided by **evaluating it at five values**.
That is the whole point: `40n` and `160n/4` are two strings and one function, and
a string comparison cannot see it. `3x/4` against `0.75x` is the same trap. Five
values rather than one, because `8(9.07z)` and `8z + 9.07z` agree at exactly one
z, and a one-point check is how a second right answer gets in.

Anything the reader does not recognise raises `Unreadable` rather than being
scored "not right". An option shape nobody taught it about is an unchecked
option, which is the thing the script exists to stop.

## What it asserts

Every check is the same shape — classify all four, demand exactly one hit, demand
it is the keyed one — so a second correct answer fails as loudly as a wrong key.
Three assertion styles cover the topic:

* **`equals`** — the stem's own printed numbers give one value, and exactly one
  option carries it. Used wherever the stem does not round.
* **`rounded`** — used wherever a stem says "approximately", "closest to", "to
  the nearest tenth" or "to the nearest whole number". It is `unambiguous`
  followed by `closest`: the true value must not sit exactly on the half, and
  exactly one printed option must be nearer it than every other.
* **`verdict` over a decided list** — used for the option sets that are
  expressions, ratios or sentences, where each option is evaluated in its own
  terms.

| template | property, decided from the printed text |
|---|---|
| `rr.partner` | the partner of whichever term the stem gives a value for — which is not always the first one named |
| `rr.equivalent` | the missing term of the second ratio |
| `rr.table_constant` | the printed rows share one ratio, and the missing entry follows it |
| `rr.simplify` | the printed ratio **is** the ratio of the two counts — not "is in lowest terms", so `10 to 16` beside `5 to 8` is two right answers |
| `rr.similar_rect` | the printed expression equals `(l₂/l₁)·w` at every w |
| `rr.dimension_shift` | the sentence names the right size *and* the right direction |
| `rr.mix_statement` | the sentence resolves to the amount the ratio actually calls for |
| `rr.expression` | the printed expression is the true function, at five values |
| `rr.multiple` | the option is the constant `big/small`, free of k — decided by evaluating at two different k, not by looking for the letter |
| `rr.chain_unknown` | the two values the stem prints give the printed constant |
| `rr.repeated_factor` | the total divided by the factor, once per year between the two printed dates |
| `rr.unit_rate` | the rate used once, in whichever of seven frames the stem is in |
| `rr.rate_convert` | the speed per the other unit of time; in the trip frame, to the nearest tenth, with no halfway value |
| `rr.rate_product` | the two rates multiplied; in the power frame, "approximately" against two significant figures |
| `rr.gap` | the base times the difference of the two rates |
| `rr.growth_table` | the two growth factors read off the printed table, and the closest tenth of an inch, with no halfway value |
| `rr.table_unit_price` | the ratio of the two unit prices computed from the printed table |
| `rr.exchange_fee` | the conversion less the fee — and that the payout **is** a whole number of cents |
| `rr.convert` | the bracketed factor applied the way the question asks, once or squared |
| `rr.convert_chain` | both bracketed factors applied in turn, with the chain's middle unit checked |
| `rr.pop_density` | the population over the density, or the land-area frame's "closest to" |
| `rr.cube_density` | mass, density or edge from the other two, to the precision the stem names, with no halfway value |

## What it caught

**Five live defects, in five templates.** Every one of them passed the full gate.

### 1. `rr.simplify`: the key, printed twice, as a ratio

The pool offered "never reduced the two counts" — the two counts as they stand.
That is the key written another way, and `assemble_text` de-duplicates on the
*string*, so it sails straight past. It reached the page whenever the reducing
factor happened to equal the second reduced term, which collapsed the two pool
entries above it into duplicates and pulled the unreduced ratio up into the
printed three:

```
Dominic has 21 brass keys and 9 nickel keys. What is the ratio of brass keys
to nickel keys that Dominic has?
  * A) 7 to 3      <- the key
    B) 21 to 9     <- the same ratio
    C) 3 to 7
    D) 7 to 10
```

114 draws in 2,000. Removing that one entry left a second shape behind: the
distractor `{g} to {a}` — "reversed that, and divided by the wrong count as
well" — is also the key whenever `g·b = a²`, which is `4 to 2` printed beside a
key of `2 to 1`. 15 draws in 2,000.

Patching the entries one at a time is how the second one survived the first fix,
so the fix is on the pool rather than on any entry: every candidate is decided
**as a ratio** and dropped if it equals the key's. Two more real slips —
reducing one count and leaving the other — were added so the pool never runs
short when an entry is dropped.

### 2. `rr.growth_table`: two options equally close

The stem says "closest to the difference, in inches". The difference lands
exactly on a half-tenth in 222 draws in 4,000 — and in **116 of those the pool
prints both neighbouring tenths**, so the item has two equally defensible
answers:

```
If a river birch tree and an american elm tree each now have a diameter of
1 foot, which of the following will be closest to the difference, in inches,
of their diameters 21 years from now?
    River birch 3.5      21 ÷ 3.5 = 6
    American elm 4.0     21 ÷ 4.0 = 5.25      difference: exactly 0.75
    A) 0.7   * B) 0.8   C) 1.0   D) 6.0
```

0.7 and 0.8 are the same distance from 0.75. Coverage, transcript, acceptance,
audit, structure, prose and capacity are all green on that item, because every
one of them stops at the key. One draw in thirty-four.

### 3. `rr.chain_unknown`: a stem that does not give its own answer

`second` is printed with two decimals, and it was not always a two-decimal
number. The stem then prints a value the key was not derived from:

```
If 8a/b = 28.2 and a/(bn) = 17.63, what is the value of n?
  * A) 0.2     B) 1.6     C) 5     D) 12.8
        the key comes from 17.625; 3.525 ÷ 17.63 is 0.19994
```

The rationale prints the false arithmetic too — "3.525 ÷ 17.63 = 0.2". 43 draws
in 934. The fix refuses a draw whose stated values do not print exactly in the
decimals the stem gives them, alongside the guard already there for the ratio
between the two letters.

### 4 and 5. `rr.rate_convert` and `rr.cube_density`: an unstated convention

"To the nearest tenth of a mile per hour" and "to the nearest whole number" have
an answer only while one multiple is nearer than every other. 54 miles in 32
minutes is exactly 101.25 miles an hour; 124 kilograms per cubic meter in a cube
of edge 0.50 is exactly 15.5 kilograms. Whether those round up or down is a
convention the stem never states — round-half-up says one thing and
round-half-to-even the other — so a student taught the other one does the
mathematics correctly and is marked wrong. 32 draws in 2,553 and 40 in 2,371.

In neither case was *both* neighbour printed, so these are items resting on an
unstated convention rather than items with two printed right answers. It is the
same hole, found the same way, and the gate is green on every one of them.

The fix for all three rounding templates is `values.unambiguous(value, step)`,
taken from Percentages rather than invented here: it rounds exactly as `snap`
does and throws the draw away when the value sits halfway. Rejecting is free;
the registry redraws. `rr.growth_table`'s `key = snap(exact, 1/10)` becomes
`unambiguous(exact, 1/10)`, and the same one-line change covers `rr.rate_convert`
and `rr.cube_density`.

### What it cleared

Seventeen templates read back clean over 34,570 draws, and several of them are
clean for a reason worth recording rather than by luck. `rr.mix_statement`
already refuses `again == second` and `first == second`, which are exactly the
two parameterizations that make a second sentence true. `rr.table_unit_price`
already compares the key against the amounts-only and costs-only routes as
strings, and `_ratio_text` reduces, so that string comparison is a value
comparison. `rr.expression`'s four frames cannot collide: `k·r = k + r` needs a
rate of `k/(k−1)`, which is under $2 for every multiplier the template draws, and
the pool never reaches it. And the numeric templates are protected against exact
collisions by `assemble`, which drops a duplicate value, and against rounding
collisions by `_options`, which refuses a set where two options print the same
once rounded. What neither of those can see is a **tie**, which is why
`rounded` exists.

## Proving the check can fail

`--selftest` injects seven faults, one for each way an option set of this topic
can be wrong. A check nobody has seen fail is worth nothing.

```
  ok   the key again, written as a quotient: 2 of the four options are right: '40n', '160n/4'
  ok   the key ratio, unreduced: 2 of the four options are right: '5 to 8', '15 to 24'
  ok   the key moved a letter: the right option is '384', but the key is '512'
  ok   the key said twice, as a plain amount: 2 of the four options are right: '1.5 times the amount of blue paint used in the second batch', 'Exactly 10.5 ounces'
  ok   two options equally close on a 'closest to' stem: the exact value is 1.25, exactly halfway between two tenths of an inch: which one is nearest is a convention, not mathematics
  ok   a value exactly halfway between two whole numbers: the exact value is 15.5, exactly halfway between two whole kilograms: which one is nearest is a convention, not mathematics
  ok   an option mirrored across the true value: 2 options are equally close to 89880.0: ['89,760', '90,000']
```

Between them they exercise both halves of the assertion and every reader:
an algebraically equal expression that looks nothing like the key; a ratio
written in different terms; a right answer on the wrong letter; a sentence
restating the key as a number; the halfway value that `unambiguous` refuses; and
a tie between two printed options where nothing is halfway at all — the last one
on `rr.rate_product`, so the tie branch of `closest` is proved separately from
the rounding guard that usually fires first.

The fifth injection rebuilds the live `rr.growth_table` defect rather than
inventing one: it takes a real drawn table, finds a pair of species and a number
of years inside it whose difference lands on a half-tenth, rewrites the stem to
name them, and prints both straddling tenths. The guard now refuses that draw, so
the selftest has to put it back.

## Running the same check on another topic

Three things are needed, and the third is the one people skip.

1. **A property each option has or does not have, decided from its printed
   text.** "Which is the ratio of these two counts" becomes a Fraction
   comparison; "which expression gives the amount" becomes evaluation at several
   values; "which of the following is closest to" becomes a distance, and then a
   check that the distance is not tied. If the property cannot be decided from
   the printed option, say so rather than skipping quietly — `Unreadable` is
   raised, not swallowed.

2. **A reader that shares nothing with the renderer.** Parse the string; do not
   re-render it and compare. A renderer bug that drops a minus sign is invisible
   to any check that goes back through the renderer. This file re-implements the
   printing rules it needs — a number reader, a ratio reader, an expression
   parser, a sentence reader — in about two hundred lines. That duplication is
   the point. It is also what made `rr.chain_unknown` visible: the key was
   correct, the parameters were correct, and only the *printed stem* was wrong.

3. **Both halves of the assertion.** `hits.count(True) == 1` catches the second
   correct answer; `hits[keyed]` catches the right answer attached to the wrong
   letter. Checking only the second is what the engine already does.

Two further notes from doing it here. Assert over generated *draws*, not over the
source items: all 36 official option sets were clean, and every one of the five
defects lived in a parameterization no official item uses. And where a stem
rounds, check the rounding as well as the option set — three of the five defects
here were a stem asking for something that has no single answer, which no amount
of reading the options can find.
