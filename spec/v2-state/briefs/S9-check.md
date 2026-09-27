# Check brief for S9: Words pages (the server is merged)

## Decisions

# v2: the user's decisions

Answers to the open questions in `spec/rebuild-v2.md` Part 5. Where this file and the plan
disagree, this file wins. Builders read it alongside the plan and `spec/v2-upgrades/`.

## 2026-09-23

1. **Daily Challenge: twins.** Every student gets the same ten question types in the same
   order, each with their own numbers, so answers cannot be passed around. (Open question 3,
   the default.)
2. **Words: SAT Reading & Writing (EBRW) vocabulary only, for now.** Ship the SAT word list
   and transitions -- no "Math language" deck. (Open question 2.) The reason is the roadmap
   below: Words is the first piece of EBRW on the site.
3. **Roadmap: the full SAT, later.** The site stays Math-first while the Reading & Writing
   question bank is built. When there are thousands of EBRW items, the platform expands to
   the full SAT (both sections, 1600 scale, R&W practice, tests and reports). Build v2 so that
   expansion is additive: subject-aware data and routes where it costs little, no Math-only
   assumptions baked into shared components that would have to be torn out.
4. **No visual budget.** "We are not limiting ourselves visually to miss on functionality...
   as long as we have useful functionality, we can use however much elements, space, and
   whatnot." A useful feature, stat, control, filter, panel or explanation is never cut,
   collapsed away or hidden to save space or look lighter. Pages may be as long and as dense
   as the functionality needs; organise it (sections, tabs, sticky bars, tables) rather than
   remove it. Something belongs if it helps a student study, OR if it makes the site clearer,
   more straightforward or more convenient to use (the user, same day: "not only if it helps to
   study, but even if it makes things clear, straightforward, and very convenient to use") --
   shortcuts, previews, confirmations of what will happen, visible state, counts, legends,
   explanations of a number, one-tap ways to the next step. The only reason to leave something
   out is that it does none of these.
5. **No classes.** "We have a separate platform for classes, drop it." Task S2 (Classes and
   homework, Shell spec §7) is removed: no teacher or student roles, classes, homework,
   assignments, class codes, `/class/` or `/join/` pages, class leaderboards or teacher views,
   and no data or endpoints for them. Anything elsewhere in the plan or the upgrades that
   depends on classes goes too. Compete keeps private contests, but not through classes: a
   private contest is an invite code or link that Compete owns (friends competing together),
   with no teacher or homework features. Resolution R4 of the plan ("Compete's groups are the
   same thing as classes") is void.

6. **No College Board Student-bank features (2026-09-27).** The public Question Bank index in `material/cb/cb_index.json`
   (3,770 questions with subject, domain, skill, difficulty and band) covers what we need: day-one levels and mapping official
   questions to our types. Do not build the two nice-to-haves that would need the signed-in Student Question Bank: resolving a
   Student-bank question ID when a student logs a missed official question (public-index IDs still work), and per-question
   "open on College Board" deep links. A plain link to College Board's Question Bank home is fine.


## Task entry

**S9 · Words** (wave 2, port 8029). Builds Part 3.8 in full, R29's third tab
(`UI.addWord`). Owns `web/words/**`, `web/vocabulary/**`, `web/assets/words-ui.js`,
`server/words.py`, `server/words/**`, `server/words_index.json`, `server/phrases.py`,
`server/api_words.py`, `tools/build_words.py`, `server/checks/s9.py`.
State: not started.


## The section's acceptance list

### 3.8.8 Acceptance checks

1. curl -s -o /dev/null -w '%{http_code}' for http://localhost:8000/words/, /words/study/?mode=cards, /words/study/?mode=quiz, /words/run/ and /words/mine/ each prints 200.
2. curl -s -H 'X-Learner: a:v2revwords01' localhost:8000/api/words | jq '[.words[]|select(.own|not)]|length' prints at least 1000.
3. On the same response, jq '[.words[]|select(.own|not)|(.word|ascii_downcase)+"|"+(.sense//"")]|(length==(unique|length))' prints true (no duplicates).
4. On the same response, jq '[.words[]|select(.collection|test("^sat|^transitions"))|select(.pos==null)]|length' prints 0.
5. On the same response, jq '.counts|keys' contains due, new, learning, known, saved, mine, mistakes, missed, lookedup, new_today and goal; jq '.forecast|length' prints 14; and ?days=60 gives 60.
6. PYTHONPATH=. python3 tools/build_words.py exits 0 and writes server/words_index.json. Breaking one confusion link regex in a copy of the content makes it exit 1 and name the link. Adding a second 'eloquent' makes it exit 1.
7. PYTHONPATH=. python3 server/phrases.py exits 0 (no distractor is equivalent to its key across 200 items per family).
8. POST /api/words/run {deck:{source:'new'}, mode:'quiz', count:10, formats:['meaning2word']} returns an item whose JSON contains none of answer, answer_index, reasons, tell, key, seed or the target slug. POST /api/words/run/{id}/save for that item before answering returns 409.
9. Over 200 quiz items across types from a mixed deck: no option is in the target's same list, and for SAT and transition targets every option shares the target's pos. Every 'transition' item's 4 options come from 4 different logic groups (checked in test_flow).
10. In a cards run on a new word, 'know' returns box.after=2 and due=today+3. 'dontknow' returns box.after=1, due=today and requeued=true, and the same word comes back within the next 4 items.
11. In a cards run, answering 'skip' files no word_reviews row, and the card reappears once at the end. A regrade of the previous card returns its box to box_before and applies the new grade. A regrade after that word has a later review returns 409.
12. A word at box 2 due in 3 days, graded 'know' today in a quiz, returns early=true with box.after=2 and an unchanged due. Graded 'dontknow', it returns box.after=1 and due=today.
13. After PUT /api/me {exam_date: today+5}, a due word at box 4 graded 'know' gets due ≤ exam_date−1. Grading the same word 'know' twice on one day moves it up only one box.
14. POST /api/drill {word:'vertex', count:5}: every stored question's key is in words_index.words.vertex.tests ∪ uses, including with difficulty:['hard'] (checked in test_flow against the stored session).
15. POST /api/drill {confusion:'radius~diameter', count:5}: at least 4 of 5 served items carry a reason matching the link regex. POST /api/drill {confusion:'percent~percentage-point'} (bankless) returns 409.
16. In a drill, picking an option whose reason is 'used the diameter as the radius' returns feedback.words containing the slugs radius and diameter.
17. GET /api/words/index with no X-Learner returns 200 with terms[] and an ETag. Repeating it with If-None-Match returns 304.
18. GET /api/words/today returns both math and sat words, the same for two different learners on the same day.
19. POST /api/words/mine with no meaning returns 400. A second 'Ubiquitous' after 'ubiquitous' returns 409 with existing_id. DELETE of another learner's id returns 404.
20. POST /api/words/mine/import with 3 lines (one tab-separated, one ' - ', one with no separator) returns added=2 and skipped[0].why set.
21. After POST /api/me/carry from code A to code B, B's GET /api/words shows A's saved and own words, and A has no rows left in word_state, word_reviews or my_words.
22. A learner with 12 card reviews today and no questions has days.streak ≥ 1 and days.total ≥ 12 in GET /api/me, and Me's 'use another code' accepts that code.
23. GET /api/history for a learner with a finished words run and an answered 'word-example' drill lists neither. GET /api/history?kind=words lists the run. /results/report/?id=<run id> ends at /words/run/?id=<run id>.
24. POST /api/report (multipart) with 2 PNGs returns 200 and the files exist under server/reports/{id}/. An 11th file, or a text file named .png, returns 400. details of 5001 characters returns 422. The 21st report of the day returns 429.
25. With words_goal 10 and minutes 60, GET /api/today coach.count equals max(5, round((60 − words.minutes)·60/95)).
26. Browser at 1280 (shot.py a:v2revwords01 1280 …/words/): the grid has 6 tiles per row (getComputedStyle(grid).gridTemplateColumns splits into 6), the Today strip shows 4 tiles, the collections show 3 group labels with counts on each tile, and the filter bar has Collection, Topic, Difficulty, Status, Part of speech and Sort chips.
27. Toggling Meanings on /words/ adds a short meaning under every visible tile and adds m=1 to the URL.
28. Browser at 390: document.scrollingElement.scrollWidth ≤ 390 on /words/, /words/mine/ and /words/run/?id=…; the grid has 2 columns; the study bar is visible above the 6-column tab bar.
29. The bar '+ word' button exists on /, /practice/ and /words/, and is absent on /practice/session/, /words/run/ and /test/.
30. In /practice/session/, selecting two words of the stem shows a .pop with 'Add to my words'. Clicking it opens the Add sheet with Word equal to the selection.
31. On /words/?w=vertex the sheet is open with MEANING, IN A REAL QUESTION (an excerpt with a highlighted span, and no /api/drill request made yet), NOT THE SAME AS and YOUR RECORD. Clicking Answer it makes exactly one POST /api/words/vertex/example. Esc closes the sheet and removes ?w from the URL.
32. On /words/?w=vertex, 'Flashcards from here' opens a cards run whose first card is vertex, shown front-first.
33. In a cards run: Space flips the card (the back face gets aria-hidden=false); 2 grades Know and a status line containing 'Back in' appears; ← shows the previous card with its grade; → on an unflipped card advances without a grade.
34. In a quiz run with the 15 s timer, waiting 16 s reveals the key with 'Out of time', and the progress segment is ink.
35. In /practice/session/, a stem containing 'median' has at least one button.term. Clicking it opens .pop with the meaning and fires one POST /api/words/lookup. Escape closes it and returns focus to the term. No .term is ever inside .opts.
36. In /test/ during a live sitting, document.querySelectorAll('.term').length is 0.
37. The Today page shows a Words tile whose due number equals GET /api/words counts.due, and two word-of-the-day lines matching GET /api/words/today.
38. Plan step 4 shows the Words switch, 5/10/20 and the From chips. After choosing 5 and Create plan, GET /api/me profile.words_goal is 5, and the day card shows a Words task with Review cards, Learn and Quiz.
39. On /words/, the sheet's speak button calls speechSynthesis.speak once per click when voices exist, and is hidden when speechSynthesis.getVoices() is empty.
40. With prefers-reduced-motion emulated, flipping a card applies no rotateY transform (the computed transform is none on both faces).


## The upgrades' acceptance items (spec/v2-upgrades/words.md)

**Acceptance.**
1. `PYTHONPATH=. python3 server/rw_items.py` exits 0 and prints a count per frame. In a temp
   copy where one frame's `hi` is raised so a too_strong distractor becomes legal as a key, it
   exits 1 naming that frame.
2. `PYTHONPATH=. python3 -c "import server.rw_items as r; a=r.item('rw.wic.weaken-01',77,'undermine');
   assert a==r.item('rw.wic.weaken-01',77,'undermine') and len(a['choices'])==4"` passes.
3. `POST /api/words/run {mode:'quiz', deck:{source:'collection', value:'sat-core'},
   formats:['incontext'], count:10}`: the first item's JSON contains none of `answer_index`,
   `reasons`, `traps`, `trap`, `template`, `seed`, `word`, `key`, and its `text` contains
   `____`.
4. A wrong answer's reply has `trap` in `traps.json`'s ids, 4 non-empty `reasons`, and a
   `spans` entry of kind `clue`.
5. `POST …/another {like:'word'}` after answering returns an item; test_flow finds the same
   `word` and a template this learner has not been served. Before answering it returns 409.
6. Over 2,000 generated items in test_flow: no option appears in its text; the four options
   share pos; no distractor is in the key's `same` list unless its trap is too_strong, too_weak
   or connotation.
7. Browser: `/words/?w=mitigate` shows IN AN SAT-STYLE QUESTION with 4 options and makes no
   request to `/api/words/run`. Answering shows 4 reason lines and a `.clue` element. In a quiz
   verdict, `T` loads a new item.
8. **Supply.** 30 calls in a row of `another(like='word')` on a core word return at least 6
   distinct templates. A 200-item `incontext` run for one learner repeats no template until
   every eligible one has been served (test_flow reads the stored items). `tools/build_words.py`
   exits 1, naming the sense, when a temp copy leaves an SAT sense with 5 legal frames or all 6
   in one subject, and prints the literature share of excerpt frames (at least 20%).
9. **Review gate.** In a temp copy, a frame with `reviewed: null` never appears in 500
   generated items; setting `reviewed` on a frame whose adjudications include one `more` makes
   the build exit 1 naming it.
10. **Right answers stay.** Browser at 390 px with touch emulation, `prefs.words_autonext`
    unset: after a right answer the verdict and its 4 reasons are still shown 5 s later. With it
    on, a touch on the verdict at 1 s holds it past 4 s; an answer marked `I` (guess) or given in
    under 3 s never moves on by itself.
11. **Migration.** test_flow copies the database, runs `words.RW_TO_ATTEMPTS`, and checks that
    every `attempts` column (from `PRAGMA table_info`) is either in the statement's column list
    or nullable or defaulted, that the migrated rows count equals `rw_answers()` with `correct`
    set, and that `deps.subject_of` gives `rw` for both topics. A grep finds no query on
    generated `word_reviews` rows (`template`) outside `words.rw_answers` and the writer.


**Acceptance.**
1. The `rw_items.py` self-check covers every family with no failure; the build exits 1 on a
   temp copy with 14 families of one logic or 149 in all.
2. A run of 20 `transition` items: in test_flow every stored item has 4 options from 4 logic
   groups, none in its family's `compatible`.
3. With `prefs.words_relation = 'on'`, the first public item has `step: 'logic'`, 4 logic names
   and no transitions; answering the step returns the 4 transitions.
4. `/words/?c=transitions` renders 9 `.logic-col` elements, each with a test line and tiles.
5. A wrong pick's reply has `logic_needed != logic_picked` and 2 spans of kind `idea`.


**Acceptance.**
1. `GET /api/words/refute` has `shades.words` sorted by intensity with `shades.at` pointing at
   refute.
2. A run of `order` items: answering with the right order returns `correct: true` and files 4
   `word_reviews` rows of kind `order` with unchanged `box_before`/box.
3. The sheet for a word in a class of 5 shows a `.shades` strip with 5 chips and one
   `[aria-current]`.


**Acceptance.**
1. `tools/build_words.py` exits 1 when a split in a temp copy does not re-join to its word.
2. `GET /api/words/circumspect` has `roots` naming circum and spect.
3. A `decode` item's 4 options never include two words from the served word's families.
4. `/words/?c=roots` shows root tiles each with a "family known" line.


**Acceptance.**
1. A learner with 4 in-context misses of trap `too_strong` in their last 10: `GET
   /api/words/insights` has `too_strong` in `open.traps`, and over 20 generated items for them
   at least 6 carry a too_strong option (test_flow reads the stored items).
2. `POST /api/words/run {mode:'quiz', deck:{source:'trap', value:'too_strong'}, count:10}`:
   every stored item has a too_strong option.
3. A learner with 2 concession items answered with contrast words: `insights.logic` has
   `{needed:'concession', picked:'contrast', n:2}`, and their next concession item has a
   contrast option.
4. `/words/mine/` shows `.trap-row` elements with a Drill it button each.


**Acceptance.**
1. With `prefs.words_method = 'on'`, the first in-context item's public JSON has `step:
   'predict'` and 3 predictions and no choices.
2. Answering the prediction right and the word wrong stores `gap = 'word'`; the prediction
   wrong stores `gap = 'reading'`.
3. `GET /api/words/insights` has `gaps: {word, reading}` over 7 days.


**Acceptance.**
1. A word at box 3, due, graded `know` in a cards run: the reply has `box.after == 3`, `due ==
   today+2` and the status line contains "Prove it". In the next cards run containing it, the
   item for that word has `kind == 'incontext'`.
2. The same word answered right in context with no `conf`: `box.after == 4` and the word's row
   has `proven` set. Answered right with `conf:'guess'`: `box.after == 3`, `due == today+1`.
3. No sequence of self-graded `know` answers over 60 simulated days lifts a word above box 3
   (test_flow drives the clock).
4. With 50 checked Knows at 60% held, the next cards run's cfg has `commit: true` and its first
   public card has 3 meanings.
5. `GET /api/words` has `counts.claimed`, and the Words H1 meta contains "claimed".


**Acceptance.**
1. Two cards runs on the same word on different days show different IN A NEW SENTENCE texts;
   both contain the word.
2. A `typed` item answered "Mitigate " for mitigate returns `correct: true`; "mitigat" returns
   `correct: true, spelling: 'mitigate'`; "mitigation" returns `correct: false`.
3. The `typed` public item carries no `word`, `also` or answer field.
4. Browser: with the focus in the Type it field, Alt+W (and a click on Hint · first letter)
   shows the first letter; the right answer then returns `hinted: true` and `box.after ==
   box.before`.
5. Six cards runs on one word show six distinct IN A NEW SENTENCE templates.


**Acceptance.**
1. A word with 4 lapses: `/api/words` marks it `stubborn: true`, and its next due item in a run
   has `kind == 'fix'` with `picks` listing the given words.
2. `PUT /api/words/elusive/hook {text: 'e-LUSive: it gets loose'}` then a cards run: the back
   carries that hook.
3. After right in-context answers on 2 different days the flag clears and `box == 2`.


**Acceptance.**
1. `POST /api/words/run {mode:'placement'}` returns 60 items; none carries `foil`, `band` or a
   key; 12 of the stored items are foils (test_flow).
2. Answering Yes to every item: `finish.estimate.n` is below the library size and the result
   carries the caution line.
3. After placement, a word answered Yes has `box == 3`, `placed == 1`, and `due` between today+3
   and today+14.
4. In a triage, `Z` after a Know it restores the word's previous box.
5. A placement whose core easy band estimates at 90%+: a core easy word not among the 48 has
   `placed == 2`, `box == 0`, is absent from the New deck, and the next Today's words run holds
   it as `kind == 'incontext'` (at least 1, at most 8 such proofs). Answered right with no
   `conf`: `box.after == 4` and `proven` set. Answered wrong: `placed == 0` and it is first in
   the New deck.
6. The result's copy counts match `finish.claimed_n` and `finish.probable_n`, and Confirm the
   rest starts a `sort` run of exactly `probable_n` words.


**Acceptance.**
1. A learner with 12 due, 2 Claimed due and a goal of 10: `POST /api/words/run {mode:'mix',
   deck:{source:'today'}}` stores items in the order Fix, due, proofs, …, with no two
   consecutive items sharing `word` (test_flow).
2. With `box: 5`, after 5 simulated minutes of `ms` the next answer's reply has `next: null` and
   the run is finished.
3. `GET /api/next` for that learner has an item with `kind == 'words'` whose `start.path` is
   `/api/words/run`.
4. The answer reply carries `next` with the next public item.
5. Browser: `/words/`, `/words/study/?mode=quiz` and `/words/mine/` each show `.today-words`
   with a Start button; `/words/run/` does not.
6. Browser: Today's Words tile, the Plan's Words task and the `/words/` panel each show 4
   visible buttons (Today's words, Review cards, Learn 10, Quiz) with no menu open; Review cards
   creates a `cards` run with `deck.source == 'due'`, Learn 10 a run with `deck.source ==
   'new'` and `count == 10`. The ⋯ menu contains no launch.


**Acceptance.**
1. `PYTHONPATH=. python3 -c "import server.words as w; w._simulate_selfcheck()"` passes.
2. With `exam_date` today+45 and 180 core words left, `insights.finish.chips` has 7 entries and
   the Auto chip's goal equals `ceil(left / 35)` clamped to 5–40.
3. A learner with 90 due and a 14-day median of 20: `/api/words` has `debt: {due: 90, spread:
   23}`. After `PUT /api/me {prefs:{words_spread: today+4}}`, a Today's words run holds 23 due
   items and no new words.
4. Over 30 words graded Know on one day at box 2, their due dates span at least 2 distinct days.
5. With `exam_date` today+8, the New deck contains no `tier: advanced` words.


**Acceptance.**
1. A learner with 50 on-time due reviews, 49 right: `insights.recall.scale == 1.2`, and the next
   box-2 Know sets due to today + round(7 × 1.2 ± fuzz).
2. `/words/mine/?view=wall` renders one `.wcell` per word of the collection, each with an
   aria-label naming its status.
3. `GET /api/words/mitigate` has `journey` with one entry per review, newest last.


**Acceptance.**
1. On `/words/` with `m` unset, clicking a tile opens the sheet with `.meaning` hidden and
   `.record` and `.journey` visible; Space shows the meaning; 2 makes exactly one `POST
   /api/words/{slug}/grade`.
2. `POST /api/words/mitigate/grade {ok:true}` on a box-0 word returns `box.after == 2`; on a
   box-3 word, `box.after == 3`; on a box-2 word not yet due, `box.after == 2`.
3. `/words/?w=mitigate&q=miti` opens the sheet uncovered with Meanings off.
4. A starred box-0 word is first in the next New deck.


**Acceptance.**
1. `POST /api/words/run {mode:'check'}` returns 12 public items and `timer_total == 852`.
2. In test_flow, 5 right of the first 6 makes items 7–12 one difficulty step up from 1–6.
3. No `.term` element exists on `/words/run/?id=<check>` before it finishes.


**Acceptance.** A sprint run's wrong answer leaves `box` unchanged and sets the word's `missed`
flag; `finish` returns `best` and `new_best`.


**Acceptance.**
1. `GET /api/words | jq '[.words[]|select(.own|not)]|length'` is at least 1100.
2. `jq '[.words[]|select(.own|not)|(.word|ascii_downcase)+"|"+(.sense//"")]|(length==(unique|length))'`
   is true.
3. `jq '[.words[]|select(.own|not)|select(.pos==null)]|length'` is 0.
4. `GET /api/words/qualify.limit` has `other_senses[0].slug == 'qualify.meet'`; grading one
   leaves the other's `box` unchanged.
5. `jq '[.words[]|select(.lists|index("answer-choice"))]|length'` is at least 80.
6. For 50 random SAT slugs, `GET /api/words/{slug}` returns a non-empty `confusions` (each with
   a `tell`), `same` of length 2 or more, and a non-empty `opposite` or `no_opposite: true`.
   `tools/build_words.py` exits 1 naming the sense when a temp copy removes one of them.
7. Every non-own row of `GET /api/words` has `freq_band` in 1–5.


**Acceptance.**
1. A word with prior .6 and no answers: `measured == {pct: 60, n: 0, prior: 0.6}` and its tile
   reads "est.". With 20 seeded first-try answers, 4 right: `measured.pct == 40` ((4 + 12) / 40),
   `n == 20`, and its tile `.dbars` reads Hard.
2. Two "also fits" reports from different learners on one (frame, word) create a
   `word_suppress` row for the pair and one with `word = '*'`; 200 later items never come from
   that frame, and `review-queue.json` lists it after the next build. 8 strong-learner first
   tries with 4 picks of one distractor trip it the same way; 3 of 8 do not.
3. `/words/?d=hardforyou` lists only this learner's words that meet the Hard for you rule.
4. The verdict's "Another choice also fits" makes exactly one `POST /api/report` with `kind:
   'word'` and no dialog opens.


**Acceptance.**
1. `POST /api/words/lists/match {text:"mitigate\nubiquitous\nzzqx"}` returns 2 found and
   `missing: ['zzqx']`.
2. `POST /api/words/outside {choices:['refute','question','support','describe'], key:'question',
   picked:'refute'}` returns `trap: 'too_strong'`, a list, and a run whose first item's stored
   options include a too_strong distractor.
3. Browser: pasting a 3-sentence text with two library words into From a text underlines exactly
   those two and makes no network request until Save.
4. Pasting "The researchers' measurements demonstrated that the population declined." offers
   nothing under Not in the library. `GET /api/words/index` has `common` with at least 10,000
   entries and an `ETag`; a repeat request with `If-None-Match` returns 304.


**Acceptance.**
1. `POST /api/sets {kind:'words', items:['mitigate','bolster']}` returns a code whose landing
   lists both words. `grep -rniE 'teacher|assignment|homework|/class/|/join/' server/words*.py
   web/words/` finds nothing (decision 5).
2. `POST /api/words/run {mode:'print', formats:['incontext'], count:10}` then `…/grade
   {letters:'AAAAAAAAAA'}` returns a summary with `asked == 10` and files 10 `word_reviews`.
3. Two `New version` prints of one sheet have the same words and different stored seeds.


**Acceptance.**
1. `GET /api/words/today` for two learners on one day returns the same `wic` and `transition`
   item ids and no key; `wic.word` is null for a learner who has not answered.
2. Answering the transition on `/words/` makes `GET /api/qotd` show `rw:transition` answered for
   that learner; a second `POST /api/qotd {slot:'rw:transition', …}` from Today files no new
   row and returns the first answer. The same holds for `rw:wic` in the other direction.
3. `grep -rn "sha256('qotd:rw\|sha256('wic:" server/` finds the hashes only inside
   `words.daily_item`.


**Acceptance.**
1. `POST /api/words/run/{id}/answer {…, at: now − 2h}` files the review with that `at`; `at: now
   − 80h` returns 422.
2. Browser, offline emulated after Take today's cards offline: the cards run advances through the
   stored cards, and reconnecting posts the queued grades.

---

## 3. Spec overrides


## Contracts and amended checks

| # | topic | what disagreed | decision | owner |
| R1 | Navigation | Shell keeps 5 phone tabs; Compete, Words and Review each add a 6th tab | **Desktop sidebar (Shell §2.2), final items.** STUDY: Today, Practice, **Review** (badge: open mistakes; replaces "Mistakes"), **Words**, Tests, Plan, Class (only when in or teaching one). PROGRESS: Results, **Compete** (replaces "Challenge"). **Phone: 5 tabs stay** Today · Practice · Tests · Plan · Results. Review, Words, Compete, Class, Profile, Settings and Help sit in the avatar menu sheet, each at most two taps away; the phone top bar's count chip is Review's. The 6-tab bars in Compete §2, Words §1 and Review §1 are not built. G-keys: G M Review, G W Words, G C Compete (see §2.8). Nav metas: Review "● 14"; Words "12 due"; Compete as Shell's Challenge meta (New / Resume / #4). | F2 |
| R10 | Drill body | Nine sections add their own fields to `POST /api/drill` | **One body contract (§2.6)**, validated in one place and built by F5. Section field names map onto it (table in §2.6). Fields that need another section's data stay on `POST /api/drill` and are resolved by the owner's module through a registry: `like` (S3, `daily.resolve_drill`), `word` and `confusion` (S9, `words.resolve_drill`), `assignment` (S2, `classes.resolve_drill`); contests are started by S8's own routes. `list` is accepted as an alias of `pool`, so Review's bodies work unchanged. | F5 |
| R11 | Preferences | Shell prefs, QBank prefs, Tests `learners.test_prefs`, Words `words_goal/words_from/gloss` columns, Shell `study_time` column | **One `learners.prefs` JSON and one registry `server/prefs.py`** with every key in §2.7. The separate columns are not added. Settings (S1) renders every key; the Practice builder, the test start sheet, Plan step 4, Me and the session's More menu write the same keys. Unknown key or bad value → 422 naming the key; only non-default values are stored; GET returns defaults merged. | F4 |
| R13 | Streak and study time | Shell, Today, Plan and Words each define a streak or minutes rule | **One function `progress.days(learner, tz, weeks)`**, used by the shell, Today, Me, Plan, Results and Words. A day is the learner's local day (X-Tz). A study day has at least one answer, or at least 10 word reviews, or a finished sitting. Rest days of the **active plan** (a weekday off, a day off, the exam's eve) neither break nor extend the streak; a rest day with practice extends it. Minutes = attempt ms (each capped at 10 min) + each finished sitting's elapsed time **only when its attempts carry no ms** (capped per module at its clock + 60s; untimed 90 min) + word reviews (each ≤ 60 s) + minutes of the student's own plan tasks marked done. Returns streak, best, active days, minutes and per-day rows for up to 53 weeks. Today's three labelled streaks are three facts: study (this), day's questions (`daily.qotd_streak`), challenge (`compete.challenge_streak`). The 60-minute after-midnight grace applies to the question of the day only. | F4 |
| R17 | Report a problem | Shell (10 images downscaled, disputes, admin), QBank (3 × 5 MB BLOBs), Tests (R-#### ids, tools), Report (3 screenshots), Words (10 images) | **One system:** Shell §2.10 and §10 are canonical: one modal `UI.report(ctx)`, up to 10 images (PNG, JPEG, WebP, GIF), stills downscaled in the browser to 2000px, 10 MB server cap, files on disk under `server/reports/{id}/` (git-ignored), bounded disputes (5 open), Your reports with replies in Settings, `/admin/reports` behind `SATF_ADMIN_TOKEN`. Categories per context are the union: Shell's lists, plus Tests' "More than one right answer" and "No right answer", plus Words' "Wrong or unclear definition" (word context). Mid-test reports never show marking and hide key disputes. Rate limit: 10 an hour and 20 a day per learner (429). Ids are integers. `tools/reports.py` is an optional CLI over the same table. | F6 |
| R18 | Sharing | Five specs define share tokens with colliding routes | **Three kinds, one each.** (a) **Progress link** for a parent or tutor: `links(kind='progress')`, view `/share/?t=`; it shows Me's cards, the Results overview and the plan read-only. Report's `learners.share` and Plan's `view_token` are this token (`/results/?share=` and `/plan/?view=` accept it). (b) **Calendar feed:** `links(kind='cal')`, one server `.ics` builder in `plan.py`, served at `/api/cal/{token}.ics`; the download is `GET /api/plan/ics`. Shell's client-side `UI.ics(plan)` is not built; a single-event helper `UI.ics(event)` (SAT date, a contest, the daily reminder) is in kit. (c) **Question sets:** `sets(code, owner, kind 'set' \| 'test' \| 'items', session, items, cfg, title, show_score, show_name, created, revoked)` for QBank shared sets, Tests shared tests and Review shares; `POST /api/sets`, `GET /api/sets/{code}` (public summary, no stems), `GET /api/sets/{code}/results` (owner only), `DELETE`; landing `/s/?c=CODE` forwards to `/practice/?share=` or `/tests/?shared=`. `navigator.share` is only ever called from a tap on "More ways to share". | F6 (sets), F4 (links table), S1 (progress view), S7 (cal) |
| R21 | One question format | QBank `UI.workspace`, Tests runner shell, Today confirm mode, Words quiz mode | **One component `UI.workspace` (question.js) and one runner shell (runner.js/css).** Modes: `practice` (feedback instant / retry / end), `exam`, `review` (read-only, Hide answers, re-answer files a repeat), `quiz` (Words), `inline` (quick sheet, Today's Try one, sheets). The practice session and the exam runner use the same runner shell: sticky top bar, progress rail, question strip, footer (Back · "Question N of M ⌃" · Check/Next), navigator, Check your work, timer, calculator dock, highlights. The exam runner's look is the practice session's (Tests §1). `UI.question` stays as a thin alias. | F3 |
| R24 | Drills that are not sittings | twin, try, word-example, review pane, spot, quick each have their own list rule | `cfg.inline = true` for sources `twin, try, word-example, review, spot`: never listed as a sitting, never in history, In progress or Resume; their answers file normally (a twin counts on its parent). `quick` sittings are listed in history as "Quick questions", never offered as Resume, and deleted when finished with 0 answers. Any set finished with 0 answered is never listed. | F5 (flag), S6 (history), S4 (drill list) |
| R25 | Achievements | Shell 43 tiered rules and `earned`; Compete 18 badges and `badges`; Words rules | **One engine `server/achievements.py`** and table `earned(learner, id, tier, at)`. Shell's tiered rules are the base. Compete adds only its unique badges (pace-setter, top-ten, weekly-4, sprinter, dress-rehearsal, season-top-10, level-5, level-8, all-rounder); Words adds 50 / 250 / 1,000 known, a collection complete, a 7-day review streak. Overlaps take Shell's tiered rule. Compete's and Words' rules are declared in their own modules (`ACHIEVEMENTS = [...]` in `compete.py`, `words.py`) and imported when present. | S1 |
| R29 | The quick sheet | Shell's floating-button equivalent has Quick question and Log a mistake; Words adds a "+ word" bar button | **One quick sheet (Q key, bolt in the sidebar and phone bar) with three tabs:** Quick question · Log a mistake · Add a word. The third calls `UI.addWord()` from `words-ui.js`. This is their add-your-own-word button, done without covering anything. Words' "+ word" bar button is not built; Words keeps Add to my words on selected text and N on its pages. | F2 (sheet), S9 (`UI.addWord`) |
| R31 | Me's tiles | Shell's 2×3 stat grid; Words and Compete want stats on Me | Me's identity grid becomes **2×4**: Streak, Answered, Accuracy, Study time, Tests, Mistakes fixed (Shell), plus **Words** ("31 known · 12 due") and **Rating** ("Level 3 · 1,084"). Me's Snapshot reads ranks from Compete; Saved & in progress reads Review's counts; Test defaults appear under Learning preferences. | S1 |
| R36 | Session kinds | new kinds from Tests and Words | New `sessions.kind` values: `custom` (Tests' custom test), `words` (Words runs), `spot` (Review). `UI.KIND` (kit) holds every label; `/api/history` lists `words` only with `?kind=words` and never lists `spot`. | F1, S6 |
| state | fill / edge | glyph | meaning |
| Correct | `--amber` fill, `--ink-deep` number | ✓ top-right | right on the first try |
| Incorrect | `--ink` fill, white number | ✕ | wrong |
| Mixed | diagonal split `--amber` / paper, 1.5px `--amber-deep` edge | ~ | right on try 2 or 3 in retry mode (only the first try counts) |
| Repaired | `--amber` fill with an ink ↻ corner | ↻ | right on the repair question that followed a miss |
| Fixed since | paper, 1.5px `--ink` edge, ink number | ✕ + small amber ✓ badge | wrong then, and the mistake has closed since (report) |
| Unanswered / Blank | paper, 1.5px dashed `--faint` edge, `--soft` number | – | not answered (a blank is never "Incorrect", R35) |
| Skipped | 1.5px dashed `--soft` edge | » | skipped, can still be answered before Finish |
| Voided | paper with a diagonal ink slash | ⊘ | a contest question voided by leaving or copying |
| Repeat | 1.5px ink outline, no fill | = | an exact re-attempt; left out of mastery |
| Not reached | dotted `--faint` edge | · | a set ended with this question on screen; left out of counts |
| Answered (exam, end mode) | `--ink` fill, white number | – | answered, no verdict shown |
| Flagged (overlay) | amber flag notch, top-right, 9px | flag | marked for review in that sitting |
| Saved (overlay, lists only) | bookmark | bookmark | kept |
| Has note (overlay) | 7px note glyph, bottom-left | note | a note or highlight exists |
| Current (overlay) | 2px ink ring, 2px paper gap | – | the question on screen |
| Filtered out | 30% opacity, skipped by Tab | – | outside the active filter |
| file | owner | components (signature, then who uses it) |
| `web/assets/head.js` | F0 → F2 | the theme / text size / motion snippet of Shell §2.13, run before first paint |
| `web/assets/ui.js` | F2 | `UI.learner()`, `UI.useLearner(code)`, `UI.api(path, opts)` (sends X-Learner and X-Tz; network error → offline banner; 401 retired → banner), `UI.shell(pageOverride?)` (sidebar 248 / rail 68 / phone bar + 5 tabs + menu sheet, skip link), `UI.refresh()` (alias `UI.me`), `UI.prefs()` (defaults merged), `UI.prefRow(host, key)`, `UI.keys.register(scope, map)` + the `?` shortcuts sheet, `UI.SAT_DATES`, `UI.chip`, `UI.ref`, `NAV`, `SECTION`, `TOPICS` + aliases |
| `web/assets/quick.js` | F2 | `UI.quick(tab?)`: Quick question · Log a mistake · Add a word (R29) |
| `web/assets/palette.js` | F2 | `UI.palette()`: pages, skills, 386 question types, named misconceptions, actions, "circles hard 5 timed" parsing |
| `web/assets/qr.js` | F2 | vendored MIT QR encoder, loaded by Settings (pairing) and Class (join code) |
| `web/assets/ui.css` | F1 | tokens (light + dark), status and level tokens, every shared class: `.card .card-head .card-err .skel .btn .quiet .pill .seg .switch .chips .field .counter .otp .stat .meter .badge .kbd .table .thumbs .legend .cell .strip .pips .dbars .menu .popover .tip .toast .banner .sheet .side .side-item .side-meta .side-day .rail .pbar .tabs` + print styles; the new header comment of §2.1 |
| `web/assets/kit.js` | F1 | overlays: `UI.sheet({title, body, actions, size})` (native `<dialog>`; a bottom sheet under 760px; Esc; focus returns), `UI.confirm({title, text, confirm, cancel, input}) → Promise`, `UI.pop(anchor \| rect, content, {role})` (anchored popover or listbox; Esc and outside click close; can anchor to a text selection), `UI.menu(trigger, items)`, `UI.tooltip(el, text)`, `UI.toast(text, {action, href, undo, ms})` (3 stacked, polite), `UI.banner(kind, text, actions)`. Controls: `UI.seg(host, options, {value, multi, onChange})`, `UI.tabs(host, tabs, {counts})`, `UI.switch`, `UI.chips`, `UI.dropdown(host, {label, options, groups, multi, counts})`, `UI.filterBar(host, filters, {url, store, sheet})` (URL sync, "Filters · n" bottom sheet on a phone, Clear), `UI.triCheck`, `UI.otp(host, onComplete)`, `UI.counter(field, max)`, `UI.scoreSlider(host, {min, max, step, value, onChange})` (range + number field + bubble), `UI.images(host, {max, maxBytes, maxEdge})` (the downscaling picker; paste and drop), `UI.examDate(anchor, {value, onSave})` (upcoming official dates with "in N days", Another date, No date yet). Data: `UI.tile(host, {label, value, sub, href, filter})` (count-up), `UI.meter`, `UI.skel(host, shape)`, `UI.cardError(host, retry)`, `UI.table(host, cols, rows, {sort})`, `UI.pips(owed, of)`, `UI.dbars(tier)`, `UI.cell(state, n, overlays)`, `UI.legend(host, states, counts)`, `UI.strip(host, marks, {onPick})`, `UI.masteryWord`, `UI.skillRow(host, skill, {practise})`, `UI.avatar(profile, size)`, `UI.countdown(el, iso)`. Formatters: `UI.dur`, `UI.mmss`, `UI.num`, `UI.date(d, 'long' \| 'short' \| 'eyebrow')`, `UI.relTime`, `UI.KIND` (every session kind and label, R36), `UI.copyText(text)` (clipboard, else select in a field), `UI.ics(event)` (one event, or a daily repeating reminder) |
| `web/assets/charts.js` | F1 | each with `role=img`, an aria summary and a visually hidden data table: `UI.bandChart(host, points, {height, target, exam, estimate, outside, onPick})` (Results, Today, Tests, Me, share view), `UI.gauge(host, {band, target, previous})` (Report), `UI.scale(host, {band, target, start})` (Today, Tests cards), `UI.barChart(host, rows, {planned, stacked, pace})` (study time, forecast, pace per question), `UI.calendar(host, {month, days, plan, marks, onPick, min, max})` (one Monday-first month grid with heat, plan marks, exam mark, roving tabindex; Today and Plan), `UI.heatmap(host, days, {weeks})` (Me, share view), `UI.lineChart(host, series, {bands})` (Compete rating / top %), `UI.spread(host, options)` (option or misconception spread; QOTD, contest review, class results) |
| `web/assets/question.js` | F3 | `UI.workspace(host, q, opts)` (R21; `UI.question` alias): modes practice (instant / retry / end), exam, review, quiz, inline; select-then-Check (prefs.first_tap restores one tap); strike with Undo; auto 2x2; the grid-in field with keystroke filter, rule line, stacked-fraction preview with its decimal, "All entry rules" popover, accepted forms; every option's misconception after the reveal (prefs.option_reasons); crowd bars; I'm guessing; the actions-row slot; Hide answers; `UI.annotate(host, marks, {editable, onChange})` (7 styles, notes, notes rail, read-only render) |
| `web/assets/runner.js` + `runner.css` | F3 | `UI.runner(host, {mode, top, footer})` (the shell shared by the session and the test window: sticky top bar, progress rail, question strip with labelled tools, footer Back · "Question N of M ⌃" · Check/Next), `UI.navigator(host, cells, {views})` (Status / Difficulty / Skill / Time, legend with counts, filters; popover or bottom sheet), `UI.checkYourWork(host, cells, opts)` (tiles, grid, Time view, warning, pacing line), `UI.timer(el, {secondsLeft, elapsed, hideKey, pause})`, `UI.calc(opts)` (float, dock at ≥1100px, resize, phone sheet, Desmos state per sitting), `UI.saveQueue(sid, send)` (ordered, retried, localStorage mirror, `made_left`, status callback), `UI.review(host, items, {mode: 'dialog' \| 'pane', filters, actions})` (R23), `UI.history({template} \| {session, question_id})` (attempt history modal), runner key maps (§2.8) |
| `web/assets/report.js` | F6 | `UI.report(ctx)` (R17): ctx `{kind: 'question' \| 'sitting' \| 'page' \| 'word' \| 'paper' \| 'catalog', source, session, question_id, day, word, paper, revealed}` |
| `web/assets/results-ui.js` | S6 | `UI.sittingCard(host, row, {actions})` (Tests T6 row design: band, route chips, M1/M2, time, wrong vs blank chips per module linking to `?q=`, actions line, note; In progress / Time's up / gated states), `UI.skillPanel(topic)` |
| `web/assets/plan-ui.js` | S7 | `UI.taskRow(host, task, {actions, compact})` (status circle or checkbox, title, type tag, meta, Start / Resume / Review, Why this?, ⋯ menu) |
| `web/assets/compete-ui.js` | S8 | `UI.board(host, data, {columns, onMore, youBar, rowMenu})`, `UI.level(rating, provisional, size)`, `UI.podium(host, top3)` |
| `web/assets/words-ui.js` | S9 | `UI.word.open(slug, {list})`, `UI.gloss(el)`, `UI.addWord(prefill)`, `UI.addWordFromSelection(root)`, `UI.speak(text)` |
| table | columns | written by |
| `flags` | learner, session, qid, template, seed, topic, at; PK (learner, session, qid) | S10 endpoints, S5 runner through them |
| `notes` | learner, template, seed, note, marks JSON, at; PK (learner, template, seed) | F4 `api_notes.py` |
| `links` | token PK, learner, kind ('progress' \| 'cal'), created, revoked, views INTEGER DEFAULT 0, last_view | S1 (progress), S7 (cal) |
| `pairs` | code PK, learner, created, expires, used, req_learner, req_device, req_answers INTEGER, state DEFAULT 'open' | S1 |
| `retired` | code PK, into, at | S1 (read by `deps.learner_of`, F4) |
| `reports` | id INTEGER PK AUTOINCREMENT, learner, kind, source, session, qid, paper, word, template, seed, category, title, answer, given, details, context JSON, device JSON, email, files JSON, dispute INTEGER DEFAULT 0, at, status DEFAULT 'new', reply, replied, seen | F6 |
| `sets` | code PK, owner, kind ('set' \| 'test' \| 'items'), session, items JSON, cfg JSON, title, show_score INTEGER DEFAULT 1, created, revoked | F6 |
| `earned` | learner, id, tier INTEGER, at; PK (learner, id, tier) | S1 |
| `classes` | id PK, name, code UNIQUE, owner, created, archived | S2 |
| `members` | class, learner, display, joined, left; PK (class, learner) | S2 |
| `assignments` | id PK, class, title, kind ('set' \| 'module' \| 'section'), cfg JSON, questions JSON, who JSON, due, created | S2 |
| `attachments` | assignment, learner, files JSON, at; PK (assignment, learner) | S2 |
| `tries` | learner, session, qid, n INTEGER, given, correct INTEGER, reason, ms INTEGER, at | S4 |
| `outside_scores` | id PK, learner, day, math, rw, source ('bluebook' \| 'official' \| 'other'), at | S3 (S7 records the exam result through S3's `add_outside_score()`) |
| `plans` | id PK, learner, name, cfg JSON, start, tz INTEGER, start_mastery JSON, created, updated, archived, result JSON, drift_seen | S7 |
| `plan_days` | plan, day, kind, minutes, test, phase, tasks JSON; PK (plan, day) | S7 |
| `plan_overrides` | plan, day, minutes, off INTEGER DEFAULT 0, test, topics JSON; PK (plan, day) | S7 |
| `plan_tasks` | id PK, plan, day, repeat, title, minutes INTEGER, created, removed | S7 |
| `plan_marks` | plan, day, task, status, to_day, at; PK (plan, day, task) | S7 |
| `papers` | n INTEGER PK, week UNIQUE, label, built, questions JSON | S5 |
| `posts` | id INTEGER PK, paper INTEGER, learner, name, at, edited, parent INTEGER, about, text, helpful INTEGER DEFAULT 0, reports INTEGER DEFAULT 0, hidden INTEGER DEFAULT 0 | S5 |
| `post_votes` | post, learner, kind ('helpful' \| 'report'); PK (post, learner, kind) | S5 |
| `contests` | id PK, kind, title, owner, code UNIQUE, grp, opens, closes, count INTEGER, seconds INTEGER, spec JSON, questions JSON, created | S8 |
| `contest_items` | contest, template, seed; PK | S8 |
| `contest_members` | contest, learner, joined; PK | S8 |
| `item_ratings` | template, tier, rating REAL, n INTEGER; PK (template, tier) | S8 |
| `name_reports` | target, reporter, at; PK | S8 |
| `seasons` | id PK, opens, closes, standings JSON, closed | S8 |
| `kv` | k PK, v | S8 (the HMAC secret for board ids) |
| `word_state` | learner, word, box INTEGER DEFAULT 0, due, reps, lapses, right, wrong, saved INTEGER DEFAULT 0, first, last, lastday, lastwrong; PK (learner, word) | S9 |
| `word_reviews` | id PK, learner, word, session, mode, kind, correct, given, confusion, box_before, due_before, ms, at | S9 |
| `my_words` | id PK, learner, word, meaning, pos, example, same JSON, opposite JSON, notes, list, source, created, updated | S9 |
| field | values | meaning |
| `topics` | [slug] | skills |
| `templates` | [template], ≤ 120, each in the catalogue | only these question types, round-robin |
| `exclude` | [[template, seed]] | never serve these (the day's own question for a "like" drill) |
| `want` | {template: regex} | walk up to 40 seeds for an item where some option's reason matches (a mix-up drill, same-mistake-elsewhere) |
| `count` | 1–120 or null | null = endless |
| `tiers` | subset of easy, medium, hard | legacy `difficulty` maps here; `'adaptive'` in it means `adaptive: true` |
| `levels`, `unmeasured` | [1..7], bool (default true) | measured levels (QBank) |
| `formats` | subset of mcq, spr | legacy `format`/`fmt`: both, mcq, grid, spr; `mix` = both with `spr_share: 0.5` |
| `spr_share` | 0–1 | share of grid-ins in the set (Plan's format tilt) |
| `adaptive` | bool | step up after 2 first-try rights in a skill, down after a miss (R33) |
| `order`, `mix` | mixed \| grouped \| ramp; even \| blueprint | QBank |
| `pool` | `new` (default) · `redo` (open mistakes) · `checks` (fixed mistakes due a check-in) · `review` (types right ≥ 10 days ago, no open trap) · `untried` (never answered; falls back to least answered) · `seen` (exact replays of past attempts) · `saved` · `marked` (flags) · `history` (attempt ids) · `items` ([[template, seed]]) · `set` (a sets code) · `related` (a norm) | where the questions come from |
| `ids` | selection within the pool | trap ids, [session, qid] pairs, [template, seed] pairs, attempt ids, a set code, a norm; null = all matching |
| `exact` | bool | serve those exact (template, seed) (each checked by `deps.access`, R19) instead of fresh seeds on their templates |
| `each` | 1–5 | fresh questions per template |
| `level` | as_missed \| any \| harder | tier for redo and checks |
| `result`, `marked`, `from` | any \| missed \| right \| guessed; bool; both \| practice \| tests | filters for `seen` |
| `from_session`, `only`, `scope`, `still_open` | sid; [qid]; misses \| all; bool | Fix these (Report); a diagnostic before sign-up → 403 |
| `retake`, `again`, `item` | sid; sid; 'template:seed' | exact retake; same settings new questions; permalink |
| `timed`, `minutes` / `timing` | bool, 1–180 / off \| pace \| custom | the clock (pace = 95 s a question) |
| `feedback` | instant \| retry \| end | stored in cfg; S4 implements retry and end |
| `repairs` | next \| end \| off | when the repair after a miss comes |
| `source` | map, coach, plan, today, mistakes, review, quick, palette, assignment, outside, twin, try, word-example, words, worksheet, shared, qotd, spot | a label; `twin, try, word-example, review, spot` set `cfg.inline` (R24); `quick` with no topics takes the coach's pick |
| `task` | `YYYY-MM-DD:(fix\|recheck\|focus\|extra\|test)` | Plan's tag |
| `parent` | sid | a twin drill's parent sitting |
| `like`, `word`, `confusion`, `assignment` | as in the owner's spec | resolved by the owner module's `resolve_drill(learner, body)` through `deps.part` into the fields above; 501 until that module exists |
| `contest` | set only by S8's server code, never from the client | |
| spec | its field | canonical |
| Shell | `unseen`, `trap {template, reason}`, `format`, `difficulty:'adaptive'`, `templates` | `pool:'untried'`, `pool:'redo', ids:[trap id]`, `formats`, `adaptive:true`, `templates` |
| Today | `like {day, slot}`; `mistakes:true, templates, count` | kept on the body; `daily.resolve_drill` (S3) turns it into `templates`, `exclude` (and the 409 "answer it first"); `pool:'redo', templates, count` |
| QBank | `pool:'mistakes'`, `saved:true`, `share`, `difficulty` | `pool:'redo'`, `pool:'saved', exact:true`, `pool:'set', ids:code`, `tiers` |
| Plan | `recheck:true`, `fmt`, `task` | `pool:'checks'`, `formats` / `spr_share`, `task` |
| Words | `word`, `confusion` | kept on the body; `words.resolve_drill` (S9) turns them into `templates`, `want` (409 for a bankless mix-up) |
| Review | `list`, `ids`, `exact`, `each`, `level` | `list` is an alias of `pool` (fixed → `checks`, templates → `templates`, share → `set`); same names otherwise |
| Report | `only`, `each`, `scope`, `still_open`, `source:'twin'` | same names; `parent` = the report's sitting |
| Compete | `templates` ("another like this") | same |
| key | values | default | also edited in |
| `set_length` | 0–120 (0 = endless) | 10 | builder, Me, quick sheet, palette |
| `clock`, `clock_minutes` | off \| pace \| custom; 1–180 | off; 16 | builder, Me |
| `tiers` | non-empty subset of easy, medium, hard | all | builder |
| `adaptive` | bool | false | builder, Me ("Adaptive" option) |
| `levels`, `unmeasured` | [1..7]; bool | all; true | builder |
| `formats` | non-empty subset of mcq, spr | both | builder |
| `feedback` | instant \| retry \| end | instant | builder, session More |
| `repairs` | next \| end \| off | next | builder |
| `rationale` | miss \| always \| tap | miss | Me, session More |
| `option_reasons` | bool | true | session More |
| `first_tap` | bool | false | session More |
| `order`, `mix` | mixed \| grouped \| ramp; even \| blueprint | mixed; even | builder |
| `pool` | new \| redo \| checks \| review \| untried \| seen \| saved \| marked | new | builder |
| `keep_warm` | bool | true | Settings (coach revisits strong skills after 10 days) |
| `confirm_end`, `keys` | bool | true | Settings |
| `show_timer`, `show_stopwatch`, `pace_alert` | bool | true | Settings, session More |
| `calc_button`, `calc_mode`, `ref_button` | bool; closed \| dock \| float; bool | true; closed; true | Settings, session More |
| `theme` | light \| dark \| system | light | Settings, palette (mirrored to localStorage `satf.look`) |
| `text` | small \| normal \| large | normal | Settings, runner More (A− A A+) |
| `motion` | system \| reduce | system | Settings |
| `week_start` | mon \| sun | mon | Settings |
| `gloss` | bool | true | Settings, Me (underline math words in questions) |
| `study_time`, `remind` | HH:MM or null; 0 \| 10 \| 30 | null; 10 | Settings, Plan step 3 |
| `test_timing` | official \| x1.5 \| x2 \| untimed | official | test start sheet, lobby, Me |
| `test_calculator`, `test_pace`, `test_confidence`, `test_reveal_route`, `test_fullscreen` | bool | true, true, false, false, true | test start sheet, lobby, Me |
| `words_goal` | 0 \| 5 \| 10 \| 20 (0 = no words in the plan) | 10 | Plan step 4, Me, Words |
| `words_from` | non-empty subset of math, sat, transitions | [math] | Plan step 4, Me |
| scope | keys |
| Global (pages with the shell) | `G` then `T` Today · `P` Practice · `M` Review · `W` Words · `E` Tests · `L` Plan · `K` Class · `R` Results · `C` Compete · `U` Profile · `S` Settings · `H` Help. `Q` quick sheet. ⌘K / Ctrl K palette (`/` too, except on pages where `/` focuses that page's search: Words, Review). `[` collapse the sidebar. `?` shortcuts |
| Runner: practice session and test window | `A–D` / `1–4` choose · `Shift+A–D` strike / undo · `Enter` Check, Next or Save & next · `←` `→` back / next · `E` eliminate mode · `M` mark for review · `B` save (practice) · `L` highlights & notes · `O` my note · `K` confidence (exam, when on) · `I` I'm guessing (practice) · `S` skip (practice) · `D` details · `N` navigator · `Y` attempt history (after answering) · `G` calculator · `F` reference (formula sheet) · `H` hide / show timer · `P` pause (practice) · `Shift+R` check your work · `?` · `Esc` |
| Player: report review, Review pane, challenge review | `←` `→` or `J` `K` move · `N` next miss · `H` hide / show answers · `T` try one like this · `E` again, exactly · `B` save · `M` mark · `Y` history · `I` details · `R` report · `A–D` / `1–4` pick while answers are hidden · `Esc` |
| Lists (Review, Words) | `J` `K` or `↑` `↓` move · `Enter` open · `X` select · `/` search · `N` add a word (Words) |
| Flashcards and word quizzes | `Space` flip · `1` / `2` grade · `←` `→` · `B` save (after the verdict in a quiz) · `P` speak · `O` open word · `A–D` / `1–4` |
### 2.9 Contracts: who provides what to whom
| F5 | the drill body; `GET /api/types`, `GET /api/types/{t}/example`, `POST /api/mistakes/log`; `drill.levels()`, `blueprint.kinds()` | F2 (palette, Log a mistake), S2 (assignment type search), S3, S4, S7, S8, S9, S10 |
| S6 | `/api/history` (R26), `/api/stats`, `/api/skill/{topic}`, `UI.sittingCard`, `?q=M1-3` on the report | S3, S5, S9 (words filter), S1 (recent activity links) |
| S9 | `words.of_reason`, `words.minutes_today`, `words.today_summary`, `words.me_stats`, `/api/words/today`, `UI.gloss`, `UI.addWord`, `UI.addWordFromSelection` | F5 (feedback words), S7 (Words task), S3 (Words tile), S1 (Me stats), F2 (quick sheet tab), S4, S3, S6, S8 (gloss and add-from-selection hooks) |
### 2.13 Acceptance checks changed by the resolutions
| section | the check says | read it as | why |
| 3.8 Words | "GET /api/me profile.words_goal is 5" | `profile.prefs.words_goal` is 5 | R11 |
| 3.8 Words | "the bar '+ word' button exists on /, /practice/ and /words/" | Q opens the quick sheet with an "Add a word" tab on those pages; the quick sheet is absent on `/practice/session/`, `/words/run/` and `/test/` | R29 |
| 3.8 Words | "the study bar is visible above the 6-column tab bar"; "the 21st report of the day returns 429" | above the 5-column tab bar; the 11th report within an hour returns 429 | R1, R17 |
