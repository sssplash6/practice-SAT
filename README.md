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

`server/` runs the site in `web/`: FastAPI over sqlite, the pages served
statically at `/`, free and with no plans or quotas.

```bash
PYTHONPATH=. python3 -m uvicorn server.app:app --port 8000   # the site and the API: http://localhost:8000
PYTHONPATH=. python3 server/test_flow.py           # the whole flow, end to end
PYTHONPATH=. python3 tools/build_diagnostics.py    # the ten diagnostic forms
PYTHONPATH=. python3 tools/build_mocks.py         # the seven shelf sections
PYTHONPATH=. python3 tools/measure_mix.py          # how repetitive practice is
SATF_DB=$PWD/server/v2.db PYTHONPATH=. python3 -m uvicorn server.app:app --port 8010   # a worktree's own server and database
```

**The site** is one shell (`web/assets/ui.css`, `ui.js`) and these pages,
rebuilt from a teardown of TopTierPrep (`spec/toptierprep-teardown.md`; the
plan is `spec/rebuild.md`). The site before it is kept in `archive/site-v1/`.

| page | what it is | API |
|---|---|---|
| `/` Today | the coach's next set, the question of the day, score band, countdown, the week, the challenge | `/api/today`, `/api/qotd` |
| `/practice/` | the map of the 19 skills with mastery and open mistakes; how many (5, 10, 22, endless), difficulty, clock | `/api/map`, `POST /api/drill` |
| `/practice/session/` | one question at a time: the key, the mistake named, a repair, the rationale, a summary | `/api/drill/{id}/...` |
| `/tests/` | a new adaptive section or one module for every sitting; the diagnostic | `POST /api/mock/new` |
| `/test/` | the Bluebook-shaped test window | `/api/session/{id}/...` |
| `/results/report/` | one sitting: band, domains, each miss by its mistake, and Fix these | `/api/session/{id}/results` |
| `/results/` | the band over time, the 19 skills, every sitting | `/api/history` |
| `/plan/` | exam date, minutes, days; today's task and a calendar to the exam | `GET`/`PUT /api/me` |
| `/mistakes/` | every open mistake by name, fixed one topic or all at once; saved questions | `/api/mistakes`, `/api/saved` |
| `/challenge/` | today's ten, the same for everyone, and the board | `/api/challenge`, `/api/challenge/start`, `/api/challenge/board` |
| `/me/` | a name for the board, and the device code | `/api/me`, `/api/me/carry` |
| `/diagnostic/` | the diagnostic's door, its sign-up and the email confirmation | `/api/session/...` |

From the v2 rebuild on (`spec/rebuild-v2.md`), each task keeps one subsection
below and edits only its own.

### F0 · Repo prep

**The app is a list of routers.** `server/app.py` keeps startup, `/api/health`,
the cache header and the static mount. The endpoints are in one router per
section: `api_tests.py` (sessions and mocks, and the paper helpers the others
read a sitting through), `api_account.py` (sign-up, verify), `api_results.py`
(results, history), `api_me.py`, `api_practice.py` (map, drill), `api_today.py`
(today, the question of the day), `api_review.py` (mistakes, saved),
`api_compete.py` (challenge) and `api_legacy.py` (`POST /api/practice`, frozen
for the archive). `server/deps.py` has what they share: `learner_of`, `tz_of`,
`mine()`, `session_or_404`, the validators, and `part(module, name)`, which is
None while a module does not exist yet. `ROUTERS` in app.py names every router
the plan has, each included before the static mount once its module exists,
and `STARTUP` names the modules whose `init()` runs at startup, so a task adds
a router or a migration without editing app.py.

**A worktree has its own database**: `SATF_DB` is the sqlite file, and unset
it is `server/satfreshman.db`.

**Each task's checks** are `server/checks/<task>.py`, a `check(c)` that
test_flow runs with its client after its own. `f0.py` checks the manifest and
that every page carries the head.

**Every page's head** loads `/assets/head.js`, which applies `satf.look` (theme,
text size, motion) before first paint, links `/manifest.webmanifest` and the
apple-touch icon, and sets theme-color. The pages that load `ui.js` load
`kit.js` and `charts.js` after it. The icons are `mark.svg` on white at 192, 512
and 180.

### F1 · Design system

Not built yet.

### F2 · Shell

Not built yet.

### F3 · Question workspace and runner

Not built yet.

### F4 · Data layer

**A wrong answer is a diagnosis.** Every wrong option in the bank names the
mistake that produces it (`Item.reasons`), so a miss says which one, shows the
key and the rationale, and opens a trap on that template and mistake. The next
question is its repair: the same template on a fresh seed, the same trap with
new numbers. A miss gets one repair and a missed repair gets none, or a student
who kept missing would never reach the end of the set; the trap stays open and
comes back later. Two clean answers on the template close it. A grid-in names
no mistake, so it is filed under the bank's skill for it.

**Mastery and the coach** (`server/progress.py`). A topic's mastery is a
difficulty-weighted average of its last forty answers, each older one counting
0.93 of the next, and pulled toward zero while there are few. The coach picks
the next set: open mistakes first, then topics never practised weighted by the
blueprint, then the weakest, then a strong topic unseen for ten days, never
more than two from one domain. Every screen opens set to its pick, and the
student can change it.

**Grid-ins are marked by value** (`scoring.grid_equal`): the bank's own
equality, plus the SAT's rule that a decimal filling the grid may be cut off or
rounded at its last place, so 0.6666 and 0.6667 both match 2/3 and 0.66 does
not.

### F5 · Drill engine and bank catalogue

**Nothing is used up.** A practice set generates each question when it is
asked for, against the learner's history, and can be endless
(`server/drill.py`). A section is built for its sitting by
`server/blueprint.py` -- module 1 when it starts, module 2 for the route module
1 earned -- from questions this learner has never been given. Fix these turns a
sitting's misses into fresh questions on the same templates.

**Practice is scheduled, not sampled.** A student picks topics on the map,
or the coach does, and asks for a number of questions; `server/practice.py`
fills every slot, one at a time as the set is played, by scoring a handful of
candidates against what they have just seen and taking the least similar. Never repeating a question is the easy half. The
hard half is that sixty questions from one subtopic can all be distinct and
still feel like the same question sixty times, so sameness is counted on seven
features at once -- template, skill, opening words, format, difficulty, whether
there is a figure, and the shape of the answer -- each weighted by how much it
shows and faded by how far back it was. A template used earlier in the same set
is penalised on its own, so a set spreads over every template a topic has.

`tools/measure_mix.py` is the evidence. Across all nineteen topics at sixty
questions each, the scheduler never repeats a template or an opening sentence
back to back, uses every template the topic owns, and produces sixty distinct
stems. Drawing at random instead loses up to fifteen of the sixty to duplicates
and runs the same template four deep. Sets build in 9 to 260 ms.

### F6 · Reports and question sets

Not built yet.

### T-bank · Named grid-in mistakes in the bank

Not built yet.

### S1 · Account, Me, Settings, Help

**A learner is a code, not an account.** The browser mints twelve random
bytes (`satf.learner` in localStorage) and sends them as `X-Learner` on every
call; the server checks their shape and nothing else. Every answer
(`attempts`), open mistake (`traps`), saved question, seen question and the
profile hang off that code. Me shows it, and typed into another device it makes
that device the same learner -- `/api/me/carry` first moves whatever the second
device had done onto it, so switching loses nothing. The diagnostic's sign-up
is still the only account.

### S2 · Classes

Not built yet.

### S3 · Today

**The question of the day is the same for everyone** (`server/daily.py`): it
is chosen from a hash of the date in the student's own timezone (`X-Tz`).

### S4 · Practice builder and session

Not built yet.

### S5 · Tests and the test window

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

**Mock sections are the real shape.** The shelf holds seven, built by
`tools/build_mocks.py` into `server/mocks.json`; the Tests page instead builds
one per sitting with the same code (`server/blueprint.py`), to the same rules
below. Each is a full digital SAT
Math section: two modules of 22 questions, 35 minutes each, 44 in total, and
the second module chosen from how the first went. Domain counts follow the
published weights -- 15 Algebra, 15 Advanced Math, 7 Problem-Solving and Data
Analysis, 7 Geometry and Trigonometry -- with about half of each domain in each
module, so a student who only reaches module 1 has still met all four.
Modules run easiest to hardest across all 22 positions with no domain
grouping, which is College Board's stated rule for Math and the one homemade
sections break most often. Domains are spread across the positions rather than
dealt round-robin, which ran the small domains out early and left every hard
position to Algebra and Advanced Math. 462 questions, all distinct, and none of
them shared with the diagnostic forms.

Grid-ins sit at positions 6, 7, 13, 14, 21 and 22 of every module. That is not
a guess: College Board's answer keys for the linear practice forms put the
student-produced responses at 6, 7, 13, 14, 20, 21 and 27 of 27, across seven
published tests and fourteen modules, without an exception. They are
interleaved in small clusters with one at the end, not banked up at the finish.
Hitting those slots needs a survey of what each template can produce, since a
grid-in slot cannot be filled by a template that only makes multiple choice.

The adaptive half is the point of the format. Module 1 is marked on its own and
routes: above 60% earns the harder second module. College Board sets that cut
at the population median and says so in the Technical Manual, but never
publishes the threshold, so the 60 is a stated choice and `scoring.py` says so.
The ceiling is not a choice -- their own simulation of a student who takes the
easier module and answers every question in it correctly reports a maximum of
580, so a low route caps there, and the report says that is why the number
stopped.

Three things College Board does not publish, which are therefore stated choices
in the code rather than reported facts: the per-module domain counts (every
table they print is scoped to the whole section), the easy/medium/hard
proportions in any module ("differing proportions" is the entire statement),
and the routing threshold itself ("around the median" is all there is). What this cannot copy: the real section carries two unscored
pretest items per module and scores the rest by item response theory. There is
nothing to pretest here and no calibration to score with, so all 22 count.

**The test window** (`web/test/`) is deliberately a copy of Bluebook's layout,
because anything a student has to re-learn on test day is a cost we handed
them. It keeps the brand orange for every highlight and nothing else.

### S6 · Results and the score report

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

### S7 · Plan

Not built yet.

### S8 · Compete

**The daily challenge is the same for everyone** (`server/challenge.py`): ten
questions, easiest to hardest, two of them grid-ins, chosen from a hash of the
date in the student's own timezone and stored once, so everyone sits the same
ten, once each. The board ranks by right answers, then time.

### S9 · Words

Not built yet.

### S10 · Review

Not built yet.

### I1 · Integration and the walk

Not built yet.

## Before a student sees this

Everything above measures whether an item is *right*. None of it measures
whether the bank is usable as practice. Three gaps, measured rather than
guessed. All three now have an answer in `server/`, the third only in part:

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
against each other, and practice keeps the per-student history the note asks
for: seeds are walked from a per-learner offset, never reissued, and checked by
stem as well as by seed, because two seeds can land on the same question.

**There is no exam blueprint.** The real test weights its domains, and the
bank alone does not know that. Sections now follow the published weights
(`server/blueprint.py`) -- the diagnostic is even across domains on purpose,
as above -- and the coach weights topics a student has not yet practised by
them, but a set the student picks is whatever mix they picked.

And the one that cannot be coded: **real difficulty comes from real students.**
Until items have been sat and there are p-values, easy/medium/hard is an
informed guess, however well the engine is built. That is an argument for
getting this in front of a class early, not for calibrating harder in private.

## Adding a topic

Read `TOPIC-GUIDE.md`. In short: transcribe every question image, group the
items into families, write the templates and an independent solver for each of
them, encode every official item in `sources.py`, and get `satbank check
--topic <slug>` to print PASS.

## Running and operating SAT Freshman

Run these from the repository root with the Python dependencies installed.
The site and API listen on port 8000; `SATF_DB` can point a worktree or deployment
at its own SQLite file.

```bash
PYTHONPATH=. python3 -m uvicorn server.app:app --port 8000
```

Run the gates before a release. `test_flow.py` uses a scratch database and runs
the check entry point in every `server/checks/*.py` (apart from `__init__.py`).
The bank and Words commands check authored content. The bank lint prints review leads
and can exit successfully with findings.

```bash
PYTHONPATH=. python3 server/test_flow.py
PYTHONPATH=. python3 -m satbank check
PYTHONPATH=. python3 tools/build_words.py
PYTHONPATH=. python3 tools/lint_bank.py
```

Environment read by the server (unset unless a default is shown):

| Variable | Effect and default |
|---|---|
| `SATF_DB` | SQLite path; `server/satfreshman.db` by default. |
| `SATF_ADMIN_TOKEN` | Enables and protects `/admin/reports/`; unset makes its API return 404. |
| `SATF_REPORTS` | Report upload directory; `server/reports/` by default. |
| `SATF_REPORTS_TO` | Email address for new report notices; unset sends none. |
| `SATF_WORDS_UNREVIEWED` | `1` allows unreviewed Words frames for development; unset serves only reviewed frames. |
| `SATF_BASE_URL` | Origin in email links; `http://localhost:8000` by default. |
| `SATF_MAIL_FROM` | Sender address; `SAT Freshman <no-reply@localhost>` by default. |
| `SATF_SMTP_HOST` | SMTP host; unset writes mail to `server/outbox/` instead of sending. |
| `SATF_SMTP_PORT` | SMTP STARTTLS port; `587` by default. |
| `SATF_SMTP_USER`, `SATF_SMTP_PASS` | SMTP login; unset means no SMTP authentication. |
| `DESMOS_WAY` | `1`, `on`, or `true` enables the Desmos question filter; unset disables it. |

`SATF_BACKUPS` is read by the backup tool, not the server. Set it to a directory
outside the repository and set `SATF_DB` to the live database before running
`python3 tools/backup_db.py`. It takes a consistent SQLite snapshot, verifies
it, keeps the latest daily copy for each of 14 days and eight weekly copies.
Use `python3 tools/backup_db.py --verify` for the latest daily copy (or
`--verify FILE` for one file). With the server stopped, use
`python3 tools/backup_db.py --restore FILE TARGET`; an existing nonempty target
requires `--force`.

`python3 tools/load_test.py --seconds 1 --learners 200 --stages 10` starts a
temporary server and database, then reports request rates, latency and errors.
`PYTHONPATH=. python3 tools/reports.py list` opens the reports inbox on the
database selected by `SATF_DB`; `show`, `reply`, `status`, `key`, `stop`,
`release`, and `labels` are its other operator commands.

Launch still needs an SMTP server for email sign-in and a Desmos production key
in place of the trial key embedded in the frontend. No server code currently
reads `SATF_GOOGLE_CLIENT_ID`; setting it does not enable Google sign-in.
