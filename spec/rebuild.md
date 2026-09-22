# The rebuild

Started 2026-09-23, from the TopTierPrep teardown (`spec/toptierprep-teardown.md`)
and the Practice Map artifact (https://claude.ai/artifact/VsZB7wvWXKCaVDZsQtowJW).
The object-era site is archived in `archive/site-v1/` and tagged `site-v1`.

The brief, in the user's words: rebuild everything they have, better in function
and in UI/UX; completely free; super minimal, no extra explanations, convenient,
straightforward, interactive; orange and nothing else; and "you have hundreds of
thousands of questions, basically infinite -- abuse that power".

This file is the plan and the state. Update the state section as work lands.

## What we have that they cannot

TopTierPrep sells a finite bank: 1,921 College Board Math items, 3,867 of their
own, 29 papers, and quotas on all of it. We have 19 topics of templates that make
a verified item for any seed, with every wrong option naming the mistake that
produces it (`Item.reasons`) and a rationale for the key. So:

* **Nothing runs out and nothing repeats.** Every practice set, test and challenge
  is generated for the student at the moment they ask, against their own history.
* **A wrong answer is a diagnosis.** The option a student picked names their
  mistake. The next question is the same template with a fresh seed -- the same
  trap, new numbers -- until they have beaten it twice.
* **A test is never used up.** A full adaptive section is built fresh per sitting,
  to the published blueprint, and module 2 is built when module 1 routes.
* **Everyone can get the same question.** A seed shared by date makes the question
  of the day and the daily challenge identical for every student, which is what
  makes a leaderboard fair.
* **Free.** No plans, no quotas, no upgrade cards. Their whole subscription layer
  is a thing we do not build.

## Principles (the UI)

* One primary action per screen, and it is the only pill. Everything else is
  plain text, an icon, or a tile.
* No narration. A control does not say what it does; the object carries its state
  (a filled bar is mastery, an orange tile is selected, an orange dot is an open
  mistake). Data keeps its units; nothing explains the interface to itself.
* Orange means "yours / live": what you picked, what you are about to practise, the
  mistakes you still have. Graphite for ink, warm greys for structure, paper white.
  Orange fills carry a near-black label (white on #F18508 is 2.4:1).
* Shapes by role: pill for the primary action, 10px tiles for content, circles for
  answer letters and marks. No borders by default -- fills separate.
* The coach decides by default and the student can override: every screen opens
  already set to the best next thing.
* Entry motion only; nothing loops. `prefers-reduced-motion` is honoured.
* Type: Archivo for UI (a placeholder; the brand face is unknown, `brand/BRAND.md`),
  DM Mono for small data, Source Serif 4 for question text as the test window does.

## Map: theirs -> ours

| theirs | ours |
|---|---|
| Dashboard: greeting banner, two QOTDs, study-time calendar, plan CTA, score, countdown, recent tests | **Today** `/`: the coach's next session as the one action; question of the day answered inline; daily challenge; score band, countdown and the week |
| Question Bank builder: 2 banks x 2 subjects, domain accordions, Bluebook include, difficulty pills, 1-7 slider, solved/marked/redo selects, volume, mode | **Practice** `/practice/`: the map of 19 skills (mastery, open mistakes), how many (5, 10, 22, endless), difficulty, timer, Start. Preselected by the coach |
| QBank session: retries until right, key hidden, no end | **Session** `/practice/session/`: one tap to answer, the key shown, the mistake named, the same trap again with new numbers, rationale, Desmos, reference, a summary that moves the map |
| Practice tests: 29 papers, most paywalled, one free attempt | **Tests** `/tests/`: a new adaptive section for every sitting, or one module; history below |
| Bluebook-style exam runner | `web/test/` kept: it is already a copy of Bluebook on purpose |
| Score report: rings, domain %, question grid, review modal | **Report** `/results/report/`: band, domains, every question with the named mistake, and "Fix these", which turns the misses into a repair set |
| Results list | **Results** `/results/`: score over time, the 19 skills, every session |
| Study plan: 4-step wizard, 1 plan per cycle | **Plan** `/plan/`: exam date, minutes, days -- the rest comes from results; the week, today's task, a test day each week; recomputed daily so nothing piles up |
| Redo list, marked for review, saved | **Mistakes** `/mistakes/`: every open mistake by name, fix one or all; saved questions, served again by their exact (template, seed) |
| Contests, rankings, leaderboards (empty) | **Challenge** `/challenge/`: ten questions a day, the same for everyone, ranked by right then time; the week's board |
| Profile, subscription, billing | **Me** `/me/`: name for the board, exam date, target, daily minutes, and a device code to carry progress to another device. No billing |
| Vocabulary (R&W) | not now: the bank is Math. Later, with an R&W bank |
| Comments on papers | not built: theirs are noise |

## Server additions

Identity stays anonymous-first: a learner token in `localStorage` (`satf.learner`),
sent as the `X-Learner` header. Accounts remain the diagnostic's signup.

Tables: `learners` (profile and plan settings), `attempts` (every answer: template,
seed, topic, difficulty, correct, the mistake it named, ms), `traps` (an open
mistake per learner, template and reason; closed after two clean answers on that
template), `saved`, `challenges` (the day's set, built once).

Endpoints: `GET/PUT /api/me`; `GET /api/map` (mastery, traps, coach pick);
`POST /api/drill`, `GET /api/drill/{id}/next`, `POST /api/drill/{id}/answer`,
`POST /api/drill/{id}/finish`; `POST /api/mock/new`; `GET /api/history`;
`GET/POST /api/qotd`; `GET /api/challenge`, `POST /api/challenge/start`,
`GET /api/challenge/board`; `GET /api/mistakes`, `POST /api/saved`.

Grid-in marking uses the bank's own equality plus the SAT's grid rule (a decimal
truncated or rounded at the fourth digit is accepted), replacing the string
compare that marked 0.125 wrong against 1/8.

## Order

1. Marking fix and the data layer (attempts, traps, learners), with tests.
2. Drill: the practice session API with feedback and repair.
3. The shell and design system (`web/assets/ui.css`, `ui.js`).
4. Practice map and session pages.
5. Fresh mocks per sitting; the tests page; the report.
6. Today, results, mistakes, me.
7. Plan.
8. Question of the day and the daily challenge with its board.
9. The diagnostic restyled into the new shell.
10. Walk it end to end in a browser; fix what that finds.

## State

2026-09-23: plan written, and all ten steps built the same day. Run it with
`PYTHONPATH=. python3 -m uvicorn server.app:app --port 8000`; the check is
`PYTHONPATH=. python3 server/test_flow.py`. Every page was walked in a browser
at 1280 and 390 px wide.

Decided while building, against the plan above:

* The diagnostic has no results page of its own. After sign-up it opens the
  same report as every other sitting, Fix these included -- its forms are
  templates like the rest.
* The object-era pages are gone from `web/` (the shelf, domain pages, sticker
  sheet, duels, `app.css`, `app.js`). The shelf's endpoints stay in the API,
  so the archived site still runs against it.
* Me carries progress between devices: typing another device's code moves this
  one's answers, mistakes, saved and seen questions onto it first
  (`/api/me/carry`). A code with nothing behind it is refused. Codes are
  minted from `crypto.getRandomValues`.

Found by the walk and fixed: a miss on a repair added another repair, so a
student who kept missing never finished (now one repair per miss, a set at most
twice its length); a missed grid-in was filed under the topic's own name
because the stored forms carry no skill (now read off the item); the results
chart shrank its labels to five pixels on a phone; the plan calendar marked
days before the student existed.

Not built, as planned: vocabulary (no R&W bank) and comments. Not built, and
not planned yet: contests beyond the daily challenge (`spec/rating.md` has the
thinking). Known edges: after a carry, a day's challenge can show two sittings
under one code; difficulty is still the inherited label; the UI face is a
placeholder until the brand face is known.
