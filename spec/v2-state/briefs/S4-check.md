# Check brief for S4: Practice builder and session pages

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

**S4 · Practice builder and session** (wave 2, port 8024). Builds Part 3.3 in full
(components come from F3, report and sets from F6, the body from F5), Compete §8 for the
practice session (R28), Review §10's session strip, Words' session hooks, Plan's session
summary. Owns `web/practice/**`, `server/drill.py`, `practice.py`, `api_practice.py`
(adds `/api/bank`, the session endpoints, `GET /api/drill`), `server/checks/s4.py`.
State: not started.


## The section's acceptance list

### 3.3.8 Acceptance checks

1. curl -s localhost:8000/api/bank -H 'X-Learner: a:v2revacc1' | python3 -c "import json,sys; d=json.load(sys.stdin); t=d['totals']; assert (t['domains'],t['skills'],t['types'])==(4,19,386); sk={s['slug']:s for x in d['domains'] for s in x['skills']}; assert len(sk)==19 and sum(len(s['types']) for s in sk.values())==386; assert len(sk['evaluating_statistical_claims']['types'])==6; ty=[y for s in sk.values() for y in s['types']]; assert all(y['name'] for y in ty) and sum(1 for y in ty if y['about'])>=378; assert all(set(y['tiers'])<={'easy','medium','hard'} and set(y['formats'])<={'mcq','spr'} for y in ty)"
2. POST /api/drill/preview {topics:['evaluating_statistical_claims'], formats:['spr']} returns servable:false with a reason containing 'grid-in'. POST /api/drill with the same body returns 409.
3. POST /api/drill {templates:['lin.evaluate'], count:5}, then answer and next five times. Server-side, every served key is 'lin.evaluate' and the five seeds are distinct.
4. POST /api/drill {topics:['linear_functions'], tiers:['hard'], count:6}: every served question in state has difficulty 'hard'.
5. Fresh learner, db as shipped: every /api/bank type has level null and level_range set. POST /api/drill {topics:['linear_functions'], levels:[1], unmeasured:false} returns 409 naming 'level 1'. The same with unmeasured:true returns 200, and every served question is easy.
6. test_flow seeds 20 first tries on (lin.evaluate, easy) with 18 right under other learner codes. /api/bank then shows lin.evaluate level 1 and measured_n >= 20, and an answer's feedback carries crowd with rate 0.9.
7. feedback='end': the answer response has none of answer, answer_index, rationale, mistake or reasons. Re-answering the same qid succeeds. The attempts table gains rows only after /finish, and /finish returns questions[] with statuses.
8. A timed feedback='end' set whose clock has run out (started moved into the past in the test): GET /api/drill/{id} returns finished, and the attempts rows exist.
9. feedback='retry': a wrong first MCQ answer returns final:false, tries_left:2, a non-empty mistake, and no answer or answer_index. The right second pick returns final:true. finish reports mixed:1, and right counts first tries only.
10. POST /api/drill/{id}/next {skip:true, ms:4000} returns a new question id. State shows the previous question with status 'skipped' and ms >= 4000. Answering it later succeeds and clears the skipped status.
11. POST /api/drill/{id}/time {question_id, ms:3000} raises served[].ms by 3000 and sets state.at to that qid.
12. POST /api/drill/{id}/strike {question_id, choice:2, on:true}, then GET /api/drill/{id} with the same X-Learner: that served entry has strikes [2].
13. POST /api/drill/{id}/more {question_id}: total rises by 1, and the next served question has the same template and a different seed.
14. Timed set: POST /pause, wait 3 s, GET state: seconds_left is unchanged within ±1, and answer returns 409. After /resume, seconds_left decreases again.
15. POST /api/drill {retake: sid} serves identical stems in order. A second learner POSTs /api/drill {share: code} and gets identical stems. GET /api/share/{code} shows taken:1. GET /api/share/{code}/results works for the owner and returns 403 for the second learner. After DELETE, POST {share} returns 410.
16. A multipart POST /api/report with one small PNG returns 200. sqlite3 server/satfreshman.db "select r.template, r.seed, count(f.report_id) from reports r join report_files f on f.report_id=r.id order by r.id desc limit 1" shows the question's template and seed with 1 file. A 6 MB file returns 413.
17. POST /api/notes {session, question_id, note:'check sign'}. After POST /api/drill {retake}, GET /api/drill/{new}/q/{same n} returns note 'check sign'.
18. PUT /api/me {prefs:{timing:'pace', feedback:'retry'}}, then load /practice/ in a browser: Test pace and 'After I retry' are selected.
19. GET /api/drill lists a new set under active once it has 1 answer, and under recent after /finish, with answered and right. A set finished with 0 answered appears in neither list.
20. A guessed-right answer (guess:true) on a template with an open trap leaves traps.owed unchanged.
21. A grid-in template that carries spr_mistakes, answered with one of those wrong values: the response mistake equals that reason, and the traps row uses it as label.
22. Challenge sitting: POST /pause, /more and next {skip:true} each return 409. state.can.permalink is false. Details shows 'Shown after today's challenge closes'.
23. POST /api/mock/{num} with a learner, then open module 1: practice_seen gains rows for its questions.
24. PYTHONPATH=. python3 server/test_flow.py passes.
25. Browser 1280 (shot.py a:v2revacc2 1280 .../practice/): 4 domain cards and 19 skill rows are visible, each with an answered count or 'Not practised' and a mastery word. Expanding Statistical claims lists 6 types, each with an about line. Unchecking one type makes the skill's and the domain's checkboxes aria-checked='mixed'. Unchecking a whole domain changes the Action bar's type count at once.
26. Browser: typing 'margin' in Search shows 'N types match' with N >= 1 and hides the non-matching rows. Esc clears it.
27. Browser: with no skill selected, Start is disabled and 'Pick at least one skill' is visible beside it. Choosing Format 'Grid-in' dims Statistical claims with the text 'no grid-in types'. The disabled 'Weakest 3' chip shows its reason as visible text, for a new learner.
28. Browser 390: document.documentElement.scrollWidth <= 390 on /practice/, on /practice/session/?id=..., on the summary and on ?print=1. The Settings controls (Questions from, Timing) are visible in the page after scrolling, without opening any dialog. Every domain header shows an answered count. The action bar and Start sit above the tabs without overlapping them.
29. Session: pressing 'b' selects B without submitting (no .verdict visible). Enter submits. Shift+'c' strikes C and shows Undo. Escape closes an open Navigator. document.elementFromPoint at the centre of Check returns the Check button (nothing floats over it).
30. Session: after a wrong MCQ answer, a line starting 'Your answer:' appears directly under the chosen option, and each other distractor shows its reason with no toggle pressed.
31. Session: answer question 3 and reload without pressing Next. Question 3 shows with its verdict, and the stopwatch shows at least the time already spent.
32. Session: highlight a word in the stem and reload. The highlight is still there. The navigator cell of a question with a note shows the note glyph.
33. SPR: the placeholder is 'e.g. 2/3, −1.5, 12' and the rule line is visible. Typing '123456' shows 'Too long' and disables Check. Typing '-2/3' shows a stacked fraction preview with '≈ −0.6667'. After a correct check on a 2/3 key, 'Also accepted' lists '.6666' or '.6667'.
34. Session: Hide replaces the timer digits with '— : —', and a reload keeps them hidden. Untimed sets show the caption 'elapsed'. Exit with 1 or more answered opens 'Leave this set?' with 'Keep it for later'.
35. Summary: the StatTiles show Correct, Incorrect, Skipped, Time and Per question, and 'Before this set' is visible. The ReviewList filter 'Incorrect' shows exactly the incorrect rows. 'Retake these exact questions' opens a set whose first stem matches. Print, with emulateMedia('print'), shows every key and explanation.


## The upgrades' acceptance items (spec/v2-upgrades/practice.md)

**Acceptance.**
1. `python3 tools/steps_coverage.py` prints "of 386 templates have worked steps" and exits 0
   only when steps cover at least 50% of U8 weight (a run on a bank below it exits 1).
   `PYTHONPATH=. python3 -m satbank` passes 200 seeds of every template with steps.
2. On a covered template, a wrong MC answer's feedback has non-empty `steps`, and `diverge`
   equals `option_steps[chosen]`. In end mode the answer response has no `steps`.
3. Browser: after that miss the Steps tab is selected, one row has the outline, and it
   contains "Your B:" (or the chosen letter).
4. "Practise this trap" on option C: the next served question has the same template, a new
   seed, and an option whose `progress.norm(reason)` equals C's norm.
5. On a template without steps the explanation shows no Steps tab.
6. For every template without steps, 200 seeds: `item.method(item)` has at least 40 words and
   contains the key's printed value, and the explanation's first tab reads "Method".


**Acceptance.**
1. `/hint` on an MC question with a named distractor returns `kind:'strike'` and a `choice`
   whose reason is non-empty and is not the key. `GET /api/drill/{id}` shows it struck. The
   response has no `answer` or `answer_index`.
2. Answer right after one hint: `attempts.hints == 1`, an open trap on the template keeps its
   `owed`, and the mastery change is half that of a clean right (compare `mastery_of`).
3. `/hint` in an end-mode set → 409; in the challenge → 409.
4. The T4 body: card 0's seed ≥ 900000 and has no attempt row. "Show the example" on
   question 1 → `attempts.hints == 1` and `guess == 0`.
5. Two first-try misses on one template in one set: the second verdict contains "Missed this
   type twice", and `/more {ladder:true}` raises `total` by 3.
6. `worked_first` on, a 5-question untimed set over 2 skills for a new learner: at most 2
   example cards are served.
7. An MC question on a template without steps has `rungs == ['strike', 'example']`, and the
   button reads "Hint · 1 of 2".


**Acceptance.**
1. `python3 tools/desmos_coverage.py` exits 0 only when all 175 floor templates carry
   `desmos` (removing one from a fixture makes it exit 1). The audit passes 200 seeds of every
   template with `desmos`.
2. A covered systems item's instant feedback has `desmos.exprs` with 2 entries. End-mode
   answers carry no `desmos`.
3. Browser: Show me in Desmos → `Calc.getExpressions().length == 2` within 1 s. Back to my
   graph restores the previous expression count.
4. Type an expression while question 3 is on screen, then answer it: `attempts.calc == 1`, and
   the ReviewSheet lists it under "What you typed in Desmos".
5. `POST /api/drill/preview {has:['desmos']}` counts only templates whose items carry `desmos`.
6. With `DESMOS_WAY` off, a covered systems item's instant feedback has no `desmos`, and the
   Desmos way tab is absent.


**Acceptance.**
1. A template and seed whose MC version matches (the check script lists one): answering the
   grid-in with the MC item's option-C value returns `mistake == reasons[2]`, and the traps
   row uses that reason.
2. The check script prints a borrowed count of at least 80 templates.
3. A seed whose MC version differs in key or params carries no borrowed `spr_reasons`.


**Acceptance.**
1. A covered item whose option C is a numeric distractor: `POST /answer {own: <C's value>}` →
   `correct:false`, `cover:'distractor'`, `mistake == reasons[2]`, `attempts.cover == 1`.
2. `own` equal to the key → `correct:true`, `cover:'key'`.
3. `own` matching nothing → `cover:'none'`, the attempts count unchanged, and a `tries` row
   with `n = 0`. The next `/answer {answer:'B'}` files the attempt.
4. Browser: `V` hides the choices and focuses the field.


**Acceptance.**
1. After an MC answer, `select offered from attempts order by id desc limit 1` is a JSON list
   of 3 norms (fewer when fillers were shown).
2. Strike the key, then answer another option: the feedback has `struck_key:true`, and
   `attempts.struck` contains the key's index.
3. `GET /api/bank?subject=math` has `habits: [{id, caught, dodged, offered, open, skills}]`
   for a learner with 5 answers.
4. `POST /api/drill {source:'habit', habits:['whole_part','sign'], count:6}` → 6 questions,
   each with an option whose norm maps to one of the two families.


**Acceptance.**
1. `POST /answer {answer:'B', conf:'sure'}` on a wrong option → `attempts.conf == 'sure'`, and
   the next `GET /api/bank` coach reasons for that skill include `confident`.
2. `conf:'guess'` → `attempts.guess == 1`; a right answer leaves the trap's `owed` unchanged.
3. `conf:'unsure'` on a right answer → `/api/review/redo` gains an `unsure` item owing 1.
4. Browser: with a choice selected, `Shift+Enter` submits with `conf:'unsure'` (network log).
   With `prefs.confidence == 'off'`, the footer shows a single Check.
5. A set with 6 Sure answers, 5 right: the summary shows "Sure 6 · 5 right (83%)".
6. A learner with no Unsure or Guess in their last 50 first tries presses Enter on a wrong
   option: `attempts.conf` is null, the verdict has no "You were sure" note, the coach reasons
   gain no `confident`, and the Calibration card shows an Unrated bar.
7. The same learner after 6 Unsure answers in their last 50 (12%): `conf_active` is true, the
   pill reads "Check · Sure", and Enter files `conf == 'sure'`.


**Acceptance.**
1. A wrong answer on a template the learner got right on 4 of the previous 5 first tries: the
   verdict pre-selects "Slip: I knew it". `POST /why {kind:'misread'}` sets
   `attempts.miss_kind == 'misread'`, and `progress.causes` then counts it under `misread`.
2. Two misreads in circles, then a new circles question: `q.ask_span` is a two-integer list,
   and the browser draws a dashed underline over that span.
3. The summary's "Why you missed" bar counts add up to the first-try misses.
4. A slip-tagged miss is not counted in `drill.levels()`'s top mistake for its type.


**Acceptance.**
1. A learner with an open trap owed 1 on t answers a fresh t question right: `next_step`
   contains "closes", and the trap is closed afterwards.
2. A learner who missed t on day 1 answers t right on day 3: `then` contains the day-1 letter
   and "today: right".
3. `progress.steps_to` has an assert self-check: a topic at mastery ≥ `STRONG` returns 0.
4. `GET /api/types/{t}/history` (R23's source) for 5 first tries returns `trend` with 5
   entries and `median_first`, `median_last`.


**Acceptance.**
1. A learner seeded as in U4's first check: `GET /api/bank` skills carry `gain`, and the
   tree's default sort puts Circles above Linear functions.
2. `python3 server/estimate.py` passes a `route` assert: all-right gives 'upper', all-wrong
   'lower'.
3. A learner with 12 answers: the header reads "Points show after 30 answers" and there is no
   route line.
4. The Route-up chip selects tiers easy and medium and 5 skills.


**Acceptance.**
1. A fresh learner on the shipped db: every `/api/bank` type has `level` in 1..7 and `rough`
   true, and at least one type sits at each level 1–7. `POST /api/drill
   {topics:['linear_functions'], levels:[1], unmeasured:false}` (where `unmeasured` now means
   rough) returns 409 naming 'level 1'.
2. After one clean first try on (t, tier), `item_ratings.n` has risen by 1 and `skill_ratings`
   has a row for the topic. A guessed or hinted answer changes neither.
3. A learner placed in circles (8 clean first tries): `POST /api/drill {topics:['circles'],
   zone:'stretch', count:5}`: each `q.odds` is within 0.15 of 0.70, or is the closest
   available in the selection (a check computes the minimum).
4. `POST /api/drill {topics:['linear_functions','circles'], tier_mix:'module2_upper',
   count:22}` → 3 easy, 8 medium, 11 hard.
5. `POST /api/drill {source:'probe', topics:['circles'], count:8}`: `cfg.feedback == 'end'`, and
   after a scripted right on slot 1 the next slot's tier is above slot 1's.
6. `python3 server/ratings.py` exits 0.
7. A fresh learner with default settings, 10 questions over three skills: at least 3 are
   Medium or Hard, and the strip reads "For me starts after 8 answers here".
8. A learner with `current = 700`: their new `skill_ratings` rows are created with `seed
   'score'` and rating 1304. After 8 scripted answers per skill that leave each rating within
   50 of 1304, a default 10-question set over two of those skills serves at least 2 Hard.
9. Every item in `material/cb_index.json` has `band` in 1..7, and `item_ratings` priors for a
   template mapped to band-7 items are at least 1350.


**Acceptance.**
1. A 10-question set with 2 first-try misses on different templates, `final_round` on: after
   slot 10, Start makes `total == 12`, and slots 11–12 have those templates, new seeds and
   `why.kind == 'final'`.
2. The same set in end mode never appends a final round.
3. A learner with 3 fading templates in circles: `POST /api/drill {topics:['circles'],
   count:10}` (default `review_mix`) serves at least 2 questions with `why.kind == 'due'`, none
   at positions 1–2.
4. A flag 3 days old with no right answer since: `warmup_candidates` includes that template
   with kind `marked`.
5. `POST /api/drill/preview {pool:'review'}` counts exactly T3's fading templates with no open
   trap.


**Acceptance.**
1. `POST /api/drill {pool:'official', ids:['23c5fcce'], each:3}` → 3 questions, each on the
   template U2's map gives, with `difficulty` equal to the key file's tier and `why.kind ==
   'official'`.
2. None has params equal to the pinned Source params, and no response contains a 40-character
   substring of the official reproduction's stem.
3. Browser: pasting "23c5fcce 84664a7c" into Search shows "2 of 2 found" and "Practise twins ·
   6 questions".
4. After finishing, `GET /api/drill` lists `official[0].cb_id == '23c5fcce'` with `twins == 3`.
5. `POST /api/drill/preview {has:['official']}` counts only templates whose U8 `official` count
   is at least 1.
6. 20 random Math IDs from `material/cb_index.json` that are not in `material/keys`: each
   `POST /api/drill {pool:'official', ids:[id], each:3}` returns 3 questions in the index's
   skill at the index's tier, and none reads "Not in our map".
7. `python3 tools/pinned_check.py`: for every template with a `Source`, seeds 0–5000 through
   `_fresh` never yield a params tuple or normalised stem in `PINNED` (a standalone check, a
   few minutes; not in test_flow).
8. Browser: a SkillPanel shows "Official questions on College Board ·" with a count, and
   pasting two IDs into its field shows the result list.


**Acceptance.**
1. Browser 1280: Map shows 386 cells, and the legend counts add up to 386.
2. "Select unmet", then Start → `cfg.pool == 'untried'`, and the served templates are among the
   selected cells.
3. `POST /api/drill {source:'finish', topics:['circles']}` for a learner with 1 open circles
   trap: slot 1's template is the trap's; `total ≤ 30`; the preview's count equals `total`.
4. Browser 390: `scrollWidth <= 390` with Map open.


**Acceptance.**
1. `UI.parseSet('circles hard 10 timed')` returns `body` with `topics:['circles']`,
   `tiers:['hard']`, `count:10`, `timing:'pace'`, and 4 chips.
2. Browser: `/`, type "percentages 5 grid-in", Enter → `/practice/session/?id=`, and the state
   has 5 slots, all `fmt 'spr'`.
3. "15 min" → the set has `cfg.box == 15` and `count == null`.
4. `PUT /api/me {prefs:{presets:[…9 items]}}` → 422 naming `presets`.
5. With `GET /api/next` returning a `checks` item first, Enter in the empty command line opens
   a session whose `cfg.pool == 'checks'`.
6. The Reading & Writing seg shows the 10 R&W skills with College Board links, the Log it
   form and the Words drills, and no Math skill tree.
7. `POST /api/mistakes/log {subject:'rw', cb_id:<an R&W ID from cb_index>, letter:'B'}` →
   200; the entry lists in `GET /api/review/counts`' outside count with `subject 'rw'`, and
   touches no Math mastery or trap.


**Acceptance.**
1. A fresh db: a served medium question has `budget_ms == 95000`, a hard one 126000.
2. `POST /api/drill {timing:'pace', count:10}`: `seconds_left` at start equals the sum of the
   planned budgets over `cfg.plan`, rounded up to the minute. After a first-try miss with
   repairs `next`, `seconds_left` rises by that repair's `budget_ms / 1000`, and `clock_log`
   has an entry with `why 'repair'`.
3. Two clean rights on t, each under budget → the `/api/bank` type has `fluent == true`.
4. Browser: a timed question left open for 1.5× its budget shows "Skip for now?".
5. A right answer faster than the learner's `best_ms` on the type: the verdict contains "New
   best on this type".
6. A set with one answer over 2× budget lists it under "Time sinks · 1".
7. A timed 10-question set with 2 first-try misses (repairs `next`) and the final round
   started: when the first final-round question is served, `seconds_left` equals the start
   value, minus the time spent, plus the 2 repairs' and the 2 final-round slots' budgets.


**Acceptance.**
1. `POST /api/drill {templates:['pct.change'], order:'mixup', count:8}` → at least 3 distinct
   templates, all in `lookalikes('pct.change') ∪ {'pct.change'}`, with no two adjacent equal.
2. `GET /api/drill/{id}` has `cfg.hide_skill == true`; at 1280 the strip reads "Mix-up" before
   Check and the type name after.
3. `python3 -c "from server.blueprint import lookalikes; assert 'pct.change' not in
   lookalikes('pct.change')"` exits 0.


**Acceptance.**
1. `/more {axis:'grid'}` on an MC question of a template with SPR in kinds: the next question
   has the same template, `fmt 'spr'` and a different seed.
2. `/more {axis:'ask'}` on a confirmed template: params equal except `ask`, and the stem
   differs. On an unconfirmed template → 409.
3. `/more {axis:'harder'}` on a one-tier medium template with a same-label hard sibling: the
   next question is that sibling at hard.
4. `python3 -c "from server.blueprint import siblings; …"` asserts that at least 150 templates
   have a same-label sibling or a second tier.
5. Browser: `Shift+T` opens the menu and lists only supported axes.


**Acceptance.**
1. `POST /api/drill {rematch: sid}` serves the same templates, tiers and formats as `sid`, in
   order, every seed different.
2. `finish()` on it returns one `slots` entry per original slot, `change` in the allowed set.
3. A challenge sid → 409.
4. With `cfg.rematch_due` = today, `GET /api/next` has an item whose title starts "Rematch".


**Acceptance.**
1. Browser: tap "Incorrect 2" in the legend → exactly 2 cells stay at full opacity.
2. "Twins of these (2)" raises `total` by 2, and the new slots have the filtered templates.
3. `U` moves to the lowest-numbered unanswered question.
4. An end-mode set with 2 unanswered and 3 Unsure answers: Check Your Work lists the
   unanswered line first with 2 Go-to buttons, then the Unsure line.


**Acceptance.**
1. `POST /api/drill {pool:'saved'}` (default `exact:false`) serves templates from `saved` with
   seeds not in `saved`.
2. A type rule on t, then a fresh t question: `GET /api/drill/{id}/q/{n}` returns
   `type_note == 'check the sign'`, and answering it leaves `attempts.hints == 0`.
3. `POST /api/drill {pool:'marked'}` defaults to exact: its served (template, seed) equal the
   rows of `flags`, not of `attempts`.
4. `?print=rules` renders every type rule, grouped under 4 domain headings.
5. `POST /api/drill/preview` returns counts for `marked` and `saved` separately, and the
   builder shows both rows; the Seen-before row has no Marked checkbox.
6. A type rule on t and `prefs.type_rules = false`: a fresh t question's `/q` has no
   `type_note`.


**Acceptance.** Two learners take one twin code: the same templates in the same order with
different seeds. The owner's results list both takers with per-slot `right` and `top_mistake`.


**Acceptance.**
1. Playwright network log: from Check to the next stem painting after Next, exactly one POST
   `/answer`, plus the fire-and-forget `/time`.
2. Touch emulation: a second tap on the selected choice produces a verdict with `conf:'auto'`
   in the request (filed per P7's rule); a double tap within 250 ms produces one answer.
3. The instant-mode payload of an unanswered question has no `answer`, `answer_index`,
   `reasons` or `steps`.
4. Answer a question, then `POST /more {axis:'same'}`: `state.served` contains no question the
   student was not shown, `total` rose by exactly 1, and `practice_seen` has no row for the
   discarded preview's seed.


**Acceptance.**
1. `python3 -c "from satbank.formulas import USES, SHEET, KNOW; …"` asserts that `USES` has
   exactly 386 keys, equal to the registry's templates, that every id is in `SHEET` or `KNOW`,
   and that no verdict line in a 386-template sample contains "Formulas for".
2. After the reveal on a cylinder-volume template, the line contains "on the reference sheet",
   and the dialog's highlighted element has id `ref-cylinder`.
3. "Drill it · 5" on the circle equation → 5 questions, each from a template whose `USES`
   include `circle_equation`.


**Acceptance.** A fixture that makes `check_item` fail on the served seed: after the report,
the served list has a new question with the same template and another seed, `total` is
unchanged relative to before the void (+1 slot, −1 counted), and the old slot's status is
`voided`.

---

## 3. Spec overrides


## Contracts and amended checks

| # | topic | what disagreed | decision | owner |
| R3 | Challenge | Shell keeps `/challenge/` and a practice-rank board at `/challenge/#practice`; Compete replaces it | Compete owns all competition. `/challenge/` redirects (307, served by `api_compete.py`, as Compete §2 says) to `/compete/contest/?id=daily`. Shell's **practice rank** (right answers, rolling 7 days, scopes everyone / same exam date / each class) is Compete's leaderboard metric `right` with period `7d` and a new scope `exam`; the Me snapshot reads it from Compete. `/challenge/#practice` links become `/compete/leaderboard/?metric=right&period=7d`. | S8 |
| R5 | Mark vs Save | QBank merges marking into saving (as TopTierPrep does); Review keeps them apart | **Two things everywhere** (Review model). *Mark for review* = a flag on one question in one sitting (`flags` table, flag icon, per sitting). *Save* = keep a question for good (`saved` table, bookmark icon). QBank's "rename Saved to Marked for review" is not done; its builder gets two pools, Marked and Saved. QBank's "a right replay removes it from Marked" is not built; Review has Unmark / Unsave with Undo. The Report button's icon is a speech bubble with "!", never a flag. | F4 (tables), S10 (endpoints) |
| R6 | Highlights and notes | QBank stores notes per (template, seed); Tests stores marks per sitting in `qstate`; Review stores a note on `saved` | **One store:** `notes(learner, template, seed, note ≤1000, marks JSON ≤50)`. Written with `POST /api/notes {session, question_id, note?, marks?}` from any sitting kind; the server resolves (template, seed) and never trusts the client for them. Mark styles are Tests' seven: highlight, strong, underline, dashed, dotted, box, strike (each mark may carry a note ≤500). A saved question's note (Review §5) is the same note. Notes come back wherever that exact question appears: replay, retake, review, report, Saved. | F4 (`api_notes.py`), F3 (`UI.annotate`) |
| R8 | Attempts columns and what counts | Review adds norm/repeat/repair/flagged/stem; QBank guess; Shell disputed; Compete sms/void | **One set of new `attempts` columns:** `norm, repeat, repair, flagged, guess, disputed, sms, void, stem`. Mastery, accuracy, boards and ranks leave out rows with `repeat=1`, `disputed=1` or `void` set; a right answer with `guess=1` counts half. Study time and question counts keep every row. A **clean answer** (closes a mistake, counts as a check-in) is right, not a repeat, not flagged and not a guess. `progress.record` computes `repeat` itself for every caller. | F4 |
| R9 | Traps and check-ins | Review rebuilds traps (id, norm, kinds, relapses) with check-ins at 7/21 days; Plan wants rechecks at 3/10/30 via stage/due; Shell adds source/note/origin | **One `traps` table:** Review's rebuild (integer `id`, `norm`, `reason` = latest concrete text, `closed_how`, `relapses`, `seed`, `session`) plus Shell's `source` ('outside'), `note`, `origin`, plus **one check-in schedule: 3, 10 and 30 days after fixing** (Plan's), stored as `due` + `checks` (0 to 3). A miss on a due check reopens it as Relapsed. Plan's Rechecks task is the drill pool `checks` (R10); Review's "Check these now" and "CHECK-INS DUE" use the same. Kinds: misconception, gridin (named when the template has `spr_mistakes`), slip, unsure. | F4 |
| R10 | Drill body | Nine sections add their own fields to `POST /api/drill` | **One body contract (§2.6)**, validated in one place and built by F5. Section field names map onto it (table in §2.6). Fields that need another section's data stay on `POST /api/drill` and are resolved by the owner's module through a registry: `like` (S3, `daily.resolve_drill`), `word` and `confusion` (S9, `words.resolve_drill`), `assignment` (S2, `classes.resolve_drill`); contests are started by S8's own routes. `list` is accepted as an alias of `pool`, so Review's bodies work unchanged. | F5 |
| R11 | Preferences | Shell prefs, QBank prefs, Tests `learners.test_prefs`, Words `words_goal/words_from/gloss` columns, Shell `study_time` column | **One `learners.prefs` JSON and one registry `server/prefs.py`** with every key in §2.7. The separate columns are not added. Settings (S1) renders every key; the Practice builder, the test start sheet, Plan step 4, Me and the session's More menu write the same keys. Unknown key or bad value → 422 naming the key; only non-default values are stored; GET returns defaults merged. | F4 |
| R17 | Report a problem | Shell (10 images downscaled, disputes, admin), QBank (3 × 5 MB BLOBs), Tests (R-#### ids, tools), Report (3 screenshots), Words (10 images) | **One system:** Shell §2.10 and §10 are canonical: one modal `UI.report(ctx)`, up to 10 images (PNG, JPEG, WebP, GIF), stills downscaled in the browser to 2000px, 10 MB server cap, files on disk under `server/reports/{id}/` (git-ignored), bounded disputes (5 open), Your reports with replies in Settings, `/admin/reports` behind `SATF_ADMIN_TOKEN`. Categories per context are the union: Shell's lists, plus Tests' "More than one right answer" and "No right answer", plus Words' "Wrong or unclear definition" (word context). Mid-test reports never show marking and hide key disputes. Rate limit: 10 an hour and 20 a day per learner (429). Ids are integers. `tools/reports.py` is an optional CLI over the same table. | F6 |
| R18 | Sharing | Five specs define share tokens with colliding routes | **Three kinds, one each.** (a) **Progress link** for a parent or tutor: `links(kind='progress')`, view `/share/?t=`; it shows Me's cards, the Results overview and the plan read-only. Report's `learners.share` and Plan's `view_token` are this token (`/results/?share=` and `/plan/?view=` accept it). (b) **Calendar feed:** `links(kind='cal')`, one server `.ics` builder in `plan.py`, served at `/api/cal/{token}.ics`; the download is `GET /api/plan/ics`. Shell's client-side `UI.ics(plan)` is not built; a single-event helper `UI.ics(event)` (SAT date, a contest, the daily reminder) is in kit. (c) **Question sets:** `sets(code, owner, kind 'set' \| 'test' \| 'items', session, items, cfg, title, show_score, show_name, created, revoked)` for QBank shared sets, Tests shared tests and Review shares; `POST /api/sets`, `GET /api/sets/{code}` (public summary, no stems), `GET /api/sets/{code}/results` (owner only), `DELETE`; landing `/s/?c=CODE` forwards to `/practice/?share=` or `/tests/?shared=`. `navigator.share` is only ever called from a tap on "More ways to share". | F6 (sets), F4 (links table), S1 (progress view), S7 (cal) |
| R19 | Access to keys and re-serving | Review defines `access()`; others re-serve items ad hoc | **One rule, `deps.access(learner, template, seed)` → `reveal` \| `kept` \| None** (Review §server). Everything that returns a key or re-serves an exact (template, seed) goes through it: review endpoints, sets, worksheets, the report, the challenge review, permalinks, Words examples. Live-test items and unanswered or same-day challenge items never leak. The permalink `/practice/session/?q=TEMPLATE:SEED` (QBank; Shell's `/q/` is the same route) serves any catalogue item that is not in today's challenge as a fresh one-question drill; the key shows after answering, as always. | F4 |
| R20 | Status colours and glyphs | Report flips nothing; QBank uses wash for correct; Compete/Review differ | **The practice session's semantics, with glyphs everywhere** (§2.3): right = orange, wrong = graphite, plus Mixed (right on a retry) and Repaired (right on the repair after a miss) as two states, skipped, blank, voided, repeat, not reached, answered (exam), flagged, saved, has note, current. One legend component. | F1 |
| R21 | One question format | QBank `UI.workspace`, Tests runner shell, Today confirm mode, Words quiz mode | **One component `UI.workspace` (question.js) and one runner shell (runner.js/css).** Modes: `practice` (feedback instant / retry / end), `exam`, `review` (read-only, Hide answers, re-answer files a repeat), `quiz` (Words), `inline` (quick sheet, Today's Try one, sheets). The practice session and the exam runner use the same runner shell: sticky top bar, progress rail, question strip, footer (Back · "Question N of M ⌃" · Check/Next), navigator, Check your work, timer, calculator dock, highlights. The exam runner's look is the practice session's (Tests §1). `UI.question` stays as a thin alias. | F3 |
| R22 | Keyboard | QBank uses C for calculator and S for skip; Review S for save; clashes with choosing C | **One registry `UI.keys` (F2) and one map (§2.8).** Calculator G, reference F, save B, skip S, history Y, highlights L, confidence K. Shortcuts are ignored while typing (Enter and Esc aside) and when `prefs.keys` is off. | F2, F3 |
| R23 | Review player, pane and history | Report's `UI.review` player, Review's `UI.questionReview` pane, QBank's review sheet | **One component `UI.review(host, items, opts)`** with `mode: 'dialog'` (Report §1.13 layout) and `mode: 'pane'` (Review §8), plus **`UI.history`** (Review §9 attempt history for the whole question type), used by the session, the report, Review and the challenge review. Report's "Try one like this" tile and Review's inline mini-session are the same inline drill. | F3 |
| R24 | Drills that are not sittings | twin, try, word-example, review pane, spot, quick each have their own list rule | `cfg.inline = true` for sources `twin, try, word-example, review, spot`: never listed as a sitting, never in history, In progress or Resume; their answers file normally (a twin counts on its parent). `quick` sittings are listed in history as "Quick questions", never offered as Resume, and deleted when finished with 0 answers. Any set finished with 0 answered is never listed. | F5 (flag), S6 (history), S4 (drill list) |
| R33 | Adaptive difficulty | Shell maps mastery to a tier; QBank steps up after 2 first-try rights | QBank's rule (step up a tier after 2 first-try rights in a skill, down after a miss, within the selected tiers). Shell's "Adaptive" option is `adaptive: true` with all tiers. | F5 |
| R34 | Test pace | several pace numbers | 95 seconds a question everywhere (2100 s ÷ 22, as `MODULE_SECONDS // MODULE_SIZE`). A 10-question challenge is 950 s. | F5 |
| R37 | Mastery display | bar vs % | A bar plus `UI.masteryWord(m, answered)` (Not started / Learning / Getting there / Strong), with accuracy printed beside it as its own %. | F1 |
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
| F6 | `UI.report`, `POST /api/report`, `GET /api/reports`; `sets` endpoints and `/s/` | every page with a question; S4, S5, S10 (share); S6 (peers) |
| S4 | `/api/bank`, `/api/drill` list (Your sets), permalink `?q=` | S1 (question types met), S3 (Continue), palette |
| S7 | `plan.today_summary(learner, tz)`, `plan.mirror(learner, fields)`, `PATCH /api/plan/{id}/tasks/{task}`, `GET /api/plan/ics` and the cal feed, `UI.taskRow` | S3 (plan card, Today list), F2 (metas), F4 (`PUT /api/me` mirror), S1 (goals card, Settings calendar), S4 (next in plan) |
| S8 | `compete.clock`, `twin_questions`, `finish_contest`, `state_extra`, `rate`, `challenge_streak`, `rank_snapshot`, `/api/contest/daily`, `UI.board`, `UI.level` | S4 and S5 (contest sittings, R28), F4 (`record` rating hook), S3 (challenge card), S1 (snapshot, Boards block) |
| S9 | `words.of_reason`, `words.minutes_today`, `words.today_summary`, `words.me_stats`, `/api/words/today`, `UI.gloss`, `UI.addWord`, `UI.addWordFromSelection` | F5 (feedback words), S7 (Words task), S3 (Words tile), S1 (Me stats), F2 (quick sheet tab), S4, S3, S6, S8 (gloss and add-from-selection hooks) |
| S10 | `/api/review/counts`, `/api/review/item`, `/api/review/family`, flag endpoints (`POST /api/session/{sid}/flag`, `POST /api/flags`) | S3 (Review card), S1 (Saved & in progress), F3 (`UI.review` pane, `UI.history`), S4 and S5 (Mark), S6 (flagged in results reads `flags`) |
| T-bank | `Item.spr_mistakes` in the bank | F4 (`record` names a grid-in mistake), S4 (verdict line) |
### 2.13 Acceptance checks changed by the resolutions
| section | the check says | read it as | why |
| 3.3 Practice | a report row joined to `report_files`; "a 6 MB file returns 413" | `reports.files` lists 1 file under `server/reports/{id}/`; an 11 MB file returns 413 | R17 |
| 3.3 Practice | `PUT /api/me {prefs:{timing:'pace', feedback:'retry'}}` | `{prefs:{clock:'pace', feedback:'retry'}}` | R11 |
| 3.3 Practice | shares: `POST /api/drill {share: code}`, `GET /api/share/{code}`, `/api/share/{code}/results` | `POST /api/drill {pool:'set', ids:code}`, `GET /api/sets/{code}`, `GET /api/sets/{code}/results`; revoke → 410 | R18(c) |
