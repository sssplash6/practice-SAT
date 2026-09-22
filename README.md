# satbank

An SAT Math item generator. Each question **type** is a template — a parameter
space, a solver, a set of distractors derived from real student
misconceptions, and a verifier — so one template yields unlimited items whose
answers are computed, never guessed.

No model runs at generation time. An LLM's job here is offline: turning a
source question into a template. Generation itself is deterministic code, so
an item is reproducible from its seed and provably correct before it ships.

## Status

The engine is being built out across all nineteen SAT Math topics, from 1,039
official College Board items. Eleven are finished, covering 659 of them:

| topic | domain | templates | official items | distractor fidelity |
|---|---|---:|---:|---:|
| Linear Inequalities | Algebra | 18 | 46 / 46 | 98% |
| Area and Volume | Geometry and Trigonometry | 19 | 59 / 59 | 97% |
| Systems of Linear Equations | Algebra | 20 | 61 / 62 | 95% |
| One-Variable Data | Problem-Solving and Data Analysis | 19 | 49 / 49 | 93% |
| Equivalent Expressions | Advanced Math | 21 | 70 / 70 | 93% |
| Linear Functions | Algebra | 23 | 85 / 86 | 90% |
| Circles | Geometry and Trigonometry | 16 | 32 / 32 | 89% |
| Percentages | Problem-Solving and Data Analysis | 18 | 52 / 52 | 87% |
| Ratios, Rates, Proportions, Units | Problem-Solving and Data Analysis | 22 | 57 / 57 | 86% |
| Linear Equations in Two Variables | Algebra | 22 | 80 / 81 | 83% |
| Linear Equations in One Variable | Algebra | 18 | 65 / 65 | 82% |

"Official items" is how many of that topic's source questions the engine
reproduces the printed answer for, driven by the source item's own numbers.

"Distractor fidelity" is the only external check on the *wrong* answers:
of the three wrong options College Board printed, how many the engine
independently arrives at. Anyone can generate three numbers that are not the
key; landing on the same three the test writers chose is evidence the
misconception library models the errors students actually make. The key is
excluded from the count — acceptance already requires it to match, so
including it would put a free 25% under every figure.

The spread across topics is mostly chronology, not mathematics. Area and
Volume sat at 60% for a day, and the explanation offered for it — that
measurement distractors are formless arithmetic slips with no canonical value
— was comfortable and wrong. It was the oldest topic, built before the
misconception discipline the later ones used. Most of its misses turned out to
be ordinary named errors nobody had modelled (squared one dimension instead of
multiplying both; halved the area as though the figure were a triangle), and a
third of the gap needed no new mathematics at all: the right wrong answers
were already there, sitting fourth in a list where only three could print. It
is 97% now, and Percentages went 76% to 87% the same way.

Three items are excluded across the eleven, each with its reason recorded in
the topic's `sources.py`; all three offer four coordinate grids as options, so
the answer lives in artwork rather than in anything a template can vary.

Every topic has also run its own `option_check.py`, and **all eleven found a
live defect the seven gate checks cannot see** — see the section below.

## Run it

```bash
PYTHONPATH=. python3 -m satbank topics                    # what is built
PYTHONPATH=. python3 -m satbank templates --topic circles
PYTHONPATH=. python3 -m satbank generate --n 5            # items with answer rationales
PYTHONPATH=. python3 -m satbank generate --template circles.arc --n 3
PYTHONPATH=. python3 -m satbank check --topic circles     # the quality gate
PYTHONPATH=. python3 -m satbank capacity --topic circles  # distinct items per template
PYTHONPATH=. python3 -m satbank export --n 500 --out pool.json

PYTHONPATH=. python3 tools/preview.py circles --per 3     # a page to look at them on
```

## How it is put together

```
satbank/exact.py      coef * pi^e * sqrt(rad) arithmetic -- every answer form in the
                      geometry source set: 192pi, 135/8, 36sqrt13, 2sqrt(pi)
satbank/expr.py       exact polynomials, equations, points, intervals, money: how an
                      algebra answer is written on the page
satbank/item.py       choice assembly: misconception-driven, ascending order, the key
                      never alone in its surface form or its sign
satbank/figures.py    generated SVG -- coordinate grids, solids, similar rectangles
satbank/plot.py       generated charts -- scatter, bar, histogram, dot, box, line, curve
satbank/audit.py      the harness that re-derives every item before it ships
satbank/check.py      the quality gate: seven checks a topic must pass
satbank/topic.py      what a topic is, and how one is found
satbank/topics/       one self-contained package per topic
tools/extract_material.py   the College Board PDFs -> answer keys and question images
tools/preview.py            generated items -> a page you can read
```

### A topic is a plug-in

Everything a topic needs lives in `satbank/topics/<slug>/`: its templates, an
independently written solver for each of them, and the official items encoded
as the parameters that reproduce them. Topics are discovered, not registered,
so several can be written at once without two authors editing the same file,
and one that will not import fails alone instead of taking the engine down
with it.

`TOPIC-GUIDE.md` is the contract.

### Why every answer is computed twice

No item leaves `generate()` until a second, independently written solver has
re-derived its answer and agreed. That solver is written from the mathematics
rather than from the generator, shares none of its helpers, and checks inverse
items by root-finding rather than by any algebra the generator performed. A
wrong answer therefore has to be produced twice, identically, by two
separately written pieces of code, to escape.

### Why the answers come from the material

An author never writes an answer down. The official answer is extracted from
the PDF's own text layer into `material/keys/<slug>.json`, the question images
are cut out one per item, and the transcription of what is printed lives in
`material/transcripts/<slug>.json`. `satbank check` drives each encoded
template with its source item's own numbers and compares against that key, so
a template whose mathematics is wrong cannot be made to pass by restating the
answer — the answer is not the author's to state.

Seven checks, all of which must pass before a topic ships:

| check | what fails it |
|---|---|
| coverage | an official item neither encoded nor excluded; a thin exclusion reason |
| transcript | a missing stem, an answer that disagrees with the key table, a stem pointing at a table nobody recorded |
| acceptance | the engine misses an official answer; under 40% of official distractors recreated |
| audit | a generated item the independent solver disagrees with |
| structure | options out of order, the key alone in its surface form or its sign, under 80% of distractors named |
| prose | a placeholder, a doubled space, a stem that is not a sentence |
| capacity | a template that cannot make 200 distinct items |

### The check the gate cannot make

Every one of the seven checks stops at the key. Nothing in the engine reads a
**wrong** option as mathematics, so an item with two correct options — or none
— passes all seven and reaches a student as a question with no defensible
answer. Each topic therefore carries an `option_check.py` that reads the four
printed options back with a parser sharing nothing with the renderer, and
asserts exactly one is correct *and* that it is the keyed one.

Eleven topics, eleven with live defects, 23 in total: a minor arc keyed at
316° with the true answer printed beside it as a distractor; box plots drawn
far enough apart that they force their means; three equivalent equations in
one option set; an item whose axes carried no labels at all under options
reading "$41" and "$60".

The gate is necessary and not sufficient: it proves an item is right, not that
it reads like an SAT item. Every topic here has also been read on a page
(`tools/preview.py`), which is what caught `f (x)` printed with a space, a
rationale that restated the answer instead of explaining it, and stems that
said cm^2 where the page says cm².

## Known limits

**Some templates are finite.** Most are still growing at 20,000 draws, but a
few are genuinely bounded — `circle.equal_area_square` at 696 and
`lin.from_table` at 592 are the smallest. `satbank capacity` re-measures after
any change.

**Fidelity has a real ceiling, below 100%.** Some printed distractors have no
derivation at all — one item's three wrong options are 72.1%, 73.9% and 77.2%
of the total, numbers chosen to sit near the key rather than produced by any
error. Those are left unreached and named in the topic's `sources.py`. An
honest 87% with the unreachable ones recorded is worth more than a fabricated
95%: the figure only means anything while it measures whether wrong answers
are modelled.

## The serving layer

A student's first move is the diagnostic, and `server/` is what runs it.

```bash
PYTHONPATH=. python3 tools/build_diagnostics.py    # the ten forms, once
python3 -m uvicorn server.app:app --port 8000      # the site and the API
PYTHONPATH=. python3 server/test_flow.py           # the whole flow, end to end
```

**Ten fixed forms, drawn at random.** A diagnostic is twenty questions: four
domains, and from each of them one easy, two medium and two hard. That is not
the exam blueprint on purpose -- the real test weights Algebra and Advanced
Math at 35% each against 15% for the other two -- because a diagnostic is
measuring four things rather than predicting one, so it spends its questions
evenly. Two hard per domain rather than one, because a single hard question is
a coin toss and the top of the range is exactly where a diagnostic has to
separate people. The forms are built ahead of time rather than drawn per
student: live draws would hit the repeat described below, and would make one
student's result impossible to reproduce. All 200 questions are distinct,
seventeen of the nineteen topics appear in every form, and each form runs
easiest to hardest the way a real module does.

**The key never leaves the process.** Questions go out without the answer, the
rationale or the distractor reasons; responses come back; marking happens
server-side. `server/test_flow.py` asserts this against the live payload rather
than trusting it, along with the blueprint, the ordering and the gates.

The clock is derived from the form's length at the real test's pace -- 35
minutes for 22 math questions, so about 95 seconds each -- and counts from the
session's start time on the server, so a reload is not free time.

**What the report is allowed to claim.** The digital SAT is scored by item
response theory over items calibrated on real test-takers, and no raw-to-scaled
table exists or could. None of those parameters are public, so `scoring.py`
uses an ordinal heuristic over the College Board's own easy/medium/hard labels
and says so; calling it IRT would be the one false claim available. The real
test reports a standard error near 20 points per section off ninety calibrated
adaptive items. Twenty uncalibrated ones cannot beat that, so the result is a
200-point band, and each domain gets a bar and a word rather than a number --
which is also what the College Board's own report does, with its own warning
that a four-item domain estimate can make a strong student look weak by chance.

**The test window** (`web/test/`) is deliberately a copy of Bluebook's layout,
because anything a student has to re-learn on test day is a cost we handed
them. It keeps the brand orange for every highlight and nothing else.

## Before a student sees this

Everything above measures whether an item is *right*. None of it measures
whether the bank is usable as practice. Three gaps, measured rather than
guessed. The first two now have an answer in `server/`; the third does not:

**Difficulty is an inherited label, not a measurement.** A template keeps the
tier of the source item it was learned from, and nothing checks that a
generated instance is as hard as its parent. Drawing evenly across templates
therefore skews hard — Area and Volume generates 106 easy / 146 medium / 223
hard from a source set that was 20 / 21 / 18, and Circles 50 / 170 / 180 from
3 / 11 / 18. A student asking for easy practice cannot reliably get it.

**Random draws repeat.** Seeds collide on the same parameters. Across 1,000
items drawn in twenty-item sets, Circles, Percentages and Linear Equations
repeated a stem zero times, but Area and Volume repeated 25 and One-Variable
Data 22 — about one visible repeat every second set. Serving needs
enumeration by seed plus per-student history, not `random()`. The diagnostic
sidesteps this by building its forms once and checking all 200 questions
against each other; practice, which is unbounded, still needs the history.

**There is no exam blueprint.** The real test weights its domains; nothing
here knows that, so a practice set drawn from this bank has a distribution
unlike the SAT's.

And the one that cannot be coded: **real difficulty comes from real students.**
Until items have been sat and there are p-values, easy/medium/hard is an
informed guess, however well the engine is built. That is an argument for
getting this in front of a class early, not for calibrating harder in private.

## Adding a topic

Read `TOPIC-GUIDE.md`. In short: transcribe every question image, group the
items into families, write the templates and an independent solver for each of
them, encode every official item in `sources.py`, and get `satbank check
--topic <slug>` to print PASS.
