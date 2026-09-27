# Check brief for S8: Compete pages (the server is merged)

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

7. **A calm, quiet interface: show only what the student needs (2026-09-27).** The user: "lets show students stuff that they
   only really indeed need to know ... make it easy and less tiring for eyes. convinience matters". Every page follows this:
   - Show what the student needs to decide or act on now. Hide zeros and defaults ("0 open", "Not practised", "0 of 107
     types ready", "Easy Medium Hard" when all are on); show a count only when it says something.
   - One number per idea, said once. Never repeat a fact in two places on the same screen (a selection shown by checkmarks is
     not also listed as chips; "Not started" is not beside "Not practised").
   - Details on demand, one tap away: expand a row, hover or focus for a tooltip, or open a Details / Settings sheet. Settings
     summaries collapse into one control; explanatory sentences become tooltips or help, not permanent text.
   - Easy on the eyes: generous spacing, few text sizes and weights, the primary fact in normal ink, secondary facts muted, mono
     only for numbers that matter, orange only for the one action or state that needs attention.
   - No feature is removed (this is not minimalism; decision 4 still holds): everything stays reachable and fast to use.


## Task entry

**S8 · Compete** (wave 2, port 8028). Builds Part 3.7 in full except the runner pages
(R28: S4 and S5 build those on its hooks), R3 (practice rank), R12's boards. Owns
`web/compete/**`, `web/challenge/**`, `server/compete.py`, `server/challenge.py`,
`server/api_compete.py`, `web/assets/compete-ui.js`, `server/checks/s8.py`.
State: not started.


## The section's acceptance list

### 3.7.8 Acceptance checks

1. curl -s -H 'X-Learner: a:v2revacc1' -H 'X-Tz: 0' localhost:8000/api/contest/daily | jq '{id, count, seconds, twin: .spec.twin}' → id == 'daily-'+today (UTC), count == 10, seconds == 950, twin == true.
2. curl -s -o /dev/null -w '%{http_code} %{redirect_url}' localhost:8000/challenge/ → 307 …/compete/contest/?id=daily
3. curl -s localhost:8000/api/contests?status=upcoming -H 'X-Learner: a:v2revacc1' | jq '[.contests[].kind]' contains 'sprint' and 'weekly' (or 'final' on the weekend a week before a SAT date), each with opens > now.
4. POST /api/contest/daily/start twice with a:v2revacc1 → the same .session both times, and the dev DB has exactly 1 sessions row with contest='daily-…' for that learner.
5. Twins: start today's daily for a:v2revtwA and a:v2revtwB and answer through. For each position the two questions share key (template), difficulty and type. The sha1 of stem+choices+figure differs in at least 9 of 10 positions, and no (template, seed) appears twice in contest_items for that contest.
6. Answer clock: start a daily, answer Q1, wait 10 s without calling next, then GET /api/drill/{sid} → .clock.running == false and .clock.left differs from its value right after the answer by < 1 s.
7. Skip: POST /api/drill/{sid}/skip {question_id} → 200 with .answer and .rationale. attempts has no row for that qid, and traps gained no row. The finished result has skipped == 1.
8. Void: POST /api/drill/{sid}/void {question_id, why:'left', secs:12}, then answer it correctly → the feedback has voided == true. The attempt row has void='left'. The finished result has voided == 1, and that question adds 0 points.
9. Points: a daily sitting with 3 easy, 4 medium and 3 hard right, all within 95 s, none skipped → .me.result.points == 260 and points_parts == {base:200, pace:50, finish:10}.
10. Ties: two learners (a:v2revtieA, a:v2revtieB) with equal points and equal secs → GET /api/contest/{cid}/board gives both rank 1 with tie:true, and the next distinct entry has rank 3.
11. A daily with all answers inside 1 s and ≥ 5 right → /api/contest/daily .me.ranked == false and .me.why == 'fast'. It is absent from the board entries.
12. GET /api/contest/daily/review before finishing → 403. After finishing → 200 with 10 items, each with field.mistakes (twins), and the shares of each item sum to 1 ± 0.01.
13. Sprint: three runs by one learner with points 60/140/90 → GET /api/leaderboard?metric=points&period=week lists that learner once, and the sprint part is 140.
14. GET /api/leaderboard?metric=points&period=week&scope=near for a ranked learner → ≤ 11 entries, with .you at index min(5, rank-1).
15. PUT /api/me {public:false} for a:v2revhid → in another learner's board that row reads name 'Anonymous', anon:true, the same rank as before, and .players is unchanged. Its own board response shows its real name with .you.anon == true.
16. PUT /api/me {country:'US'} for two learners, then GET /api/leaderboard?scope=country from one → only US learners, including both.
17. PUT /api/me {name:'Ada'} from a second learner when 'Ada' exists (any case) → 409. {name:'mike2027'} → 200. {name:'Student 1A2B'} and {name:'Anonymous'} → 422.
18. POST /api/contests {count:10, topics:[…], open_for:24, twin:true} → .code matches ^[A-HJ-NP-Z2-9]{6}$ and is not a group code. POST /api/join {code} from another learner → {kind:'contest'}. After both sit it the board has 2 players, and GET /api/contest/{cid}/results is 200 for the owner and 403 for the other learner.
19. POST /api/report-name {pid} from three fresh codes with no ranked sitting → the name is unchanged. From three codes that each finished a ranked contest → the name resets to its default handle.
20. After a learner's first ranked sitting: /api/compete/me has .rating != 1000, .provisional == true, and badges includes first-contest with an earned date. After 30 rated answers provisional == false.
21. POST /api/me/carry from a code that sat today's daily into one that also sat it → exactly one ranked sitting remains, and the other has unranked_why 'repeat'.
22. GET /api/qotd?day=<yesterday> → 200 with that day's question. POST /api/qotd {day:<yesterday>, answer:0} → 200, and .streak doesn't count it. A future day → 422.
23. GET /api/compete → .season.closes is the next date in sat_dates, and .season.name == 'Road to ' + that date formatted 'Mon D'.
24. GET /api/session/{sid}/results for an untimed full section → .ranked == {ok:false, why:'untimed'} and no percentile.
25. Browser at 1280 and 390 (shot.py with a:v2rev codes) on /compete/, /compete/contest/?id=daily, /compete/leaderboard/ and /compete/rankings/: no page errors, and document.documentElement.scrollWidth <= innerWidth.
26. Browser: on every /compete/* page, and in a contest sitting of /practice/session/, the nav/tab 'Compete' link has aria-current='page'. The phone tab bar shows 6 labelled tabs.
27. Browser: in a daily sitting with a question open, X opens 'Leave the challenge?'. 'Leave' goes to the contest page showing 'Resume', GET /api/drill/{id} .finished is null, and that question's mark is 'skip'.
28. Browser: during a ranked daily, hiding the tab for 6 s (document.visibilityState via Playwright page emulation or a second tab) shows the voided banner on return.
29. Browser: after finishing a daily with no chosen name, the result panel shows 'On the board as Student ….' with a name field. Saving 'Tester9' updates the board row without a reload.
30. Browser: the result panel lists the topic mastery rows and the opened/closed mistakes, as the practice summary does.
31. Browser: on the leaderboard, changing metric/period/scope/domain updates the URL query, and a reload restores the same controls. With a:v2revpod on the podium, only that card has the amber edge and no podium card has an orange ground.
32. Browser: on a finished daily result, 'Copy result' puts text on the clipboard that starts with 'SAT Freshman · Daily Challenge' and whose third line is exactly 10 characters from the set ■□·.
33. PYTHONPATH=. python3 server/test_flow.py passes, including the new compete checks.


## The upgrades' acceptance items (spec/v2-upgrades/compete.md)

**Acceptance.**
1. A daily sitting with 2 wrong (two different reasons), 1 skip and 1 right-but-slow answer →
   `/debrief.lost` has 4 rows, Σ `pts` == `max − points`, and the wrong rows' `pts` equal their
   tier points (+5 when their time was within budget).
2. On a seeded board where one more medium right moves you from #4 to #2 → that row's
   `rank_if == 2` and `places == 2`.
3. **Fix it** on a trap row posts a body whose `want[template]` equals the attempt's norm; the
   three served questions each regenerate with an option whose norm equals it (check in s8.py).
4. Browser: clicking the "Traps" segment leaves only those questions visible in Review, and the
   filter underline reads "Selected · 2".


**Acceptance.**
1. After a daily with 2 wrong and 1 skipped, `POST /rematch {when:'later'}` sets `rematch_due`
   to the local day + 2, and `GET /api/next` for that day has an item whose title starts
   "Rematch".
2. `{when:'now'}` serves 3 questions with the original slots' templates, tiers and formats and
   different seeds. A slot with a named miss regenerates with an option whose norm equals the
   original's.
3. After the rematch with 2 of 3 right → `me.followup.won_back` equals those two slots' tier
   points, and the trap of each right slot is closed.
4. `POST /api/drill {rematch: <unfinished contest sitting>}` → 409.


**Acceptance.**
1. A daily where Q2 (easy) is right in 70 s and Q5 (medium) right in 90 s → Q2 earns no pace
   bonus and Q5 earns +5 (`result.points_parts.pace` counts one).
2. With every answer right within budget, `points == 260` and `points_parts == {base:200,
   pace:50, finish:10}` (§3.7.8 item 9 still holds).
3. `/api/compete/me.pace` equals `progress.pace(learner, days=90, only='contest')` field for
   field (s8.py).
4. The Final's session payload has `cfg.pace == false`, and the test window renders no pace
   tick for it.


**Acceptance.**
1. A Final with 2 wrong answers over 2× budget in circles → `final_focus.skip_first` contains
   `circles`.
2. With exam date = Final + 7 and `final_focus.traps = [t]`, `GET /api/next` during the taper
   lists trap `t` before any other trap, and `final_focus.mode == 'last_week'`.
3. With exam date = Final + 42 (or none), `mode == 'focus'`: the result panel has no eve-rest
   row and no day rows, and has the "3 traps to fix" and "Skip first" rows. With exam date =
   Final + 42, `GET /api/next` on day 36 after the Final (that student's taper) lists trap `t`
   first.
4. The card page has no `nav`, contains "Doors open by 7:45 AM", and a Playwright print-to-PDF
   of it is one page at A4 and Letter.

---


**Acceptance.**
1. `par` for `R_you = 1100` against three slots of 10 / 20 / 30 points whose items are all
   rated 1100 → `base == 30`, `right == 1.5` (s8.py).
2. The lobby's `me.par.base` equals the finished sitting's `result.par.base`.
3. A learner whose rating fell 150 in a week gets `result.par.rating == peak − 100`.
4. `/api/leaderboard?metric=net&period=week` lists no learner with fewer than 30 rated answers
   or fewer than 3 sittings in the week.


**Acceptance.**
1. A daily board with 1 player returns 4 or 5 `pars`; `players == 1` and the player's rank is 1.
2. A verdict on a slot with 3 contest answers and 40 first tries on the type → `field.source ==
   'type'` and `n == 40`. With 10 first tries → `'expected'`.
3. Browser: the par rows carry no rank text, and switching Pars off hides them after a reload.


**Acceptance.**
1. The warm-up drill's served templates never include any template of the contest's `spec.slots`
   (s8.py over 20 seeds).
2. With 9 ranked players `me.forecast` is null; with 10 it has `lo <= hi`.
3. `ladder[i].chance` equals `E_i` for the learner's frozen rating, to 2 decimals, and
   `ladder[i]` has `topic` and `tier` but no `template` before the sitting starts.
4. The warm-up's served topics equal the `topic` of the 3 lowest-chance `ladder` cells.


**Acceptance.**
1. `GET /api/drill/{sid}` after answering 3 of 10 in a race → `pacer.marks` has exactly 3 items.
2. With a verdict showing for 10 s (clock not running), `pacer.at` doesn't change between two
   reads.
3. `?race=<pid of a hidden learner>` → 403. `?race=<pid of a named learner>` → 200.
4. A race started on today's live daily by a learner with no sitting → the finished sitting has
   `ranked == 1`.
5. Copy result's text: line 3 is 10 characters from `■□·`, and line 4 starts `Beat ` and
   contains `&race=`.


**Acceptance.**
1. A learner at 1,080 with public learners active at 1,050, 1,120 and 1,400 → rivals are the
   first two, then the third.
2. A hidden learner is never an auto rival, and `POST /api/follows` on their pid → 403.
3. `scope=following` returns only followed learners and you; `scope=level` returns only levels
   within ± 1 of yours.
4. `find=ada` (a public "Ada" at rank 212) → `offset == 200` with a page size of 50.


**Acceptance.**
1. After two days of snapshots, a learner who moved from #9 to #6 on `points:week` has `move ==
   3` on day 2's board.
2. With you at 150 and the row above at 171, the you-bar reads "22 pts to pass #211" and the
   step "one medium right at pace". At 160 above you: "11 pts" and "one easy right at pace".
3. `/api/me.ranks` and `/api/compete.me` give equal week, country and all-time ranks.
4. `GET /api/leaderboard?metric=climb` ignores `period` and returns `window` from
   `compete.climb`.
5. `GET /api/compete` → `board_preview` has the top 5 entries plus you ± 2; with you at #12 it
   has 10 rows with a separator after #5, and with you at #6 it has 8 rows and no separator.


**Acceptance.**
1. One clean right Geometry practice answer changes that topic's `skill_ratings` row and the
   Geometry aggregate, leaves the other domains' aggregates unchanged, and leaves
   `learners.rating` unchanged.
2. `/api/leaderboard?metric=skill&domain=Geometry%20%26%20Trigonometry` orders by the Geometry
   aggregate; `?metric=rating&domain=…` → 400 `{"error": "domain applies to metric=skill"}`.
3. Browser: on Your rankings, the Leaderboard and the result panel, every rating number sits
   under or beside the words "Contest rating" or "Skill rating", and no surface shows a Skill
   rating row inside the Contest rating block.
4. With 19 learners at Level 5 holding a recent timed section, that ladder cell is "—"; with 20
   it shows a number.
5. The "Level N in" line for rating 1,084 (K 12, hard items at 1,300) reads "+17 ≈ 2 hard
   rights".

---


**Acceptance.**
1. For this week's trap contest, every slot's twin for two different learners regenerates with
   an option whose reason matches the family regex (s8.py).
2. `trap_theme` of a week never equals any of the W previous weeks' themes, and is never
   `slip`.
3. A learner with 5 resisted chances over 3 templates in 30 days → that family has `proven:
   true`.
4. `GET /api/contests?status=live` always contains a `trap` row.
5. On the shipped bank, `s8.py --traps` builds 12 consecutive `trap_theme` weeks (with no
   answer data, so the walk is used), and every one has 10 slots, 3E / 4M / 3H, over at least
   the topic floor it printed.


**Acceptance.**
1. After a right answer, the next served item's rating is ≥ the previous one's; after a miss it is
   lower.
2. The run ends on the third strike, and no template repeats within a run.
3. The weekly board lists each learner once, with their best run.
4. For a learner with a Skill rating of 1,600, the first 5 right answers in a run serve strictly
   rising item ratings, or the header reads "Top of the bank" from the answer where they stop
   rising.
5. `python3 server/ratings.py` reports ≥ 8 distinct priors per tier on the shipped bank, and
   no Rush screen (runner, end, board) contains the word "Level" next to an item.


**Acceptance.**
1. `GET /api/contests?status=live` has a row with `kind == 'words'` and `subject == 'rw'`.
2. `GET /api/leaderboard?metric=points&subject=math` never includes Word Sprint runs, and no
   Word Sprint answer adds a row to `attempts`.
3. A run with 9 right and 3 wrong → `result.score == 8.0`.
4. A word missed in a Word Sprint has its Missed lately flag set and its `box` unchanged (W16's
   rule).
5. A run with 2 wrong W1 answers whose chosen options name trap T → `result.traps` has `{trap:
   T, n: 2}`, and the end screen's Traps line names it.
6. Every served item has `kind` in `incontext`, `transition` (W1, W2 item types), never a
   definition-to-word tile.

---


**Acceptance.**
1. Flag a right answer (`void {why:'left', secs:12}`), then answer its confirm twin right → the
   slot scores its base points, `voided == 0`, and the breakdown says "1 confirmed".
2. Forfeit the confirm (a second void call during it) → the slot adds 0, `voided == 1`, and the
   original attempt has `void = 'left'`.
3. A sitting with 6 right answers each in 1 s → `ranked == 0`, `why == 'fast'`, no confirm step.
   With 3 such answers → a confirm step of 3.
4. Browser: a copy event in the stem and a paste into the calculator during a ranked daily raise
   no banner; a paste into the grid-in field does.
5. Playwright: during a ranked daily, open a second window and focus it for 6 s → the confirm
   banner ("out of focus") shows on return. Focusing the calculator for 30 s raises nothing.
6. Playwright: copy text in the stem, then focus a second window for 2 s → the banner ("copied
   and the window left") shows.
7. During a confirm twin, focusing a second window for 1 s forfeits it (`voided == 1`).
8. A Final with 2 flagged right answers in module 1 → both confirms are served at the module
   break before `GET /api/session/{sid}` returns module 2's questions, and `route` equals the
   route for module 1's as-given right count. One failed confirm → `route` unchanged, that slot
   scores 0, and the result has `route_kept: true`.
9. A daily board with 3 clean sittings and 1 with a held confirm → the legend reads "3 clean ·
   1 with confirms", and the entries carry `mark: 'clean'` × 3 and `mark: 'confirmed', n: 1`.


**Acceptance.**
1. Two learners with equal points and different answer times → both have rank 1 with `tie:
   true`, and the next distinct entry has rank 3.
2. §3.7.8 item 10 still passes.


**Acceptance.**
1. With `test_timing: 'x1.5'`, `POST /api/contest/daily/start` → `clock.left == 1425`.
2. That learner's finished daily is absent from the daily board's entries and `players`; its
   board response has `you.extended == {rank, of}`.
3. The same learner appears on `metric=net` and `metric=rating`.
4. Copy result's text of an extended sitting equals the official format, character for
   character, apart from the numbers.
5. A learner with `test_timing: 'x1.5'` sees the consequence line on the daily lobby and, on
   the first extended start, the confirm sheet; "Use official time for contests" makes the
   next `start` return `clock.left == 950` while Tests still start at 1.5×.
6. That learner's finished private contest sitting is in that contest's board `entries` at its
   real rank, and no entry field names the timing.


**Acceptance.**
1. Simulate 500 entrants on today's daily (`s8.py --simulate 500`): no slot has a duplicate
   `qhash`, and every entrant's template list equals the canonical `spec.slots` templates, in
   order.
2. A pair with 201 distinct is excluded from the pool once F ≥ 101, and included while F ≤ 100.
3. With the cache file deleted, startup serves a daily without error, and the file reappears
   with the current bank hash.

---


**Acceptance.**
1. `POST /api/contests {repeat: {every: 'day', rounds: 3}, …}` → one code; rounds 1–3 open on
   consecutive local days; a learner who joined in round 1 is an entrant of round 2 with no
   second join.
2. A 3-entrant series where all 3 finished rounds 1 and 2 → `series_streak == 2`. One entrant
   missing round 3 → it holds at 2 until round 3 closes, then 0.
3. A second nudge from one sender to one entrant in one round → 429.
4. The series board with round 2 unsat by one entrant shows "–" for that round and ranks Σ
   points; `sort=net` orders by Σ Net.
5. `GET /api/groups` and `GET /api/classes` → 404; `db.py` has no `groups`, `group_members`,
   `classes` or `class` column (decision 5).


**Acceptance.**
1. A series round from our open mistakes with 3 entrants each holding norm X open → at least one
   slot regenerates with an option whose norm is X.
2. `our_traps` on a one-off contest or a series' round 1 → 400 "Our open mistakes starts from
   round 2."
3. `GET /api/contest/{cid}/results` → 404; `/grid` for a finished entrant has `footer[i].top`
   and `where`, and is 403 before they finish (C20).

---


**Acceptance.**
1. `/grid` before finishing → 403; after → rows whose `marks` length equals the slot count.
2. Browser at 390: `document.documentElement.scrollWidth <= innerWidth` with the grid open.


**Acceptance.**
1. A Daily of 245 after a best of 230 → `records_new` contains `{kind:'daily', value:245,
   was:230}`.
2. The recap's contest count equals `/api/compete/history` rows within the season window.
3. Browser with reduced motion: the result panel renders with no running animation.


**Acceptance.**
1. `/compete/rankings/` has no contest `<select>`.
2. `GET /api/compete/history?followup=open` returns only rows with an unfinished rematch or an
   open trap from that sitting.
3. Browser: expanding a Daily row shows its strip and a mini board without leaving the page.


**Acceptance.**
1. For every id in v2's 18-badge list and every rule in `compete.ACHIEVEMENTS`, resolved through
   `FOLDED` where folded: a learner with `have < next` on that rule gets a row whose `go` is
   non-null (`s8.py` walks the list against a seeded learner).
2. `compete.go_for(<Shell's Challenge rule id>, learner)` equals `go_for('first-contest',
   learner)`.
3. Resisting all 10 in a trap contest adds `earned (id 'trap-week', tier 1)`.


**Acceptance.**
1. Browser: with `satf.rules.daily` set, one click on Today's challenge pill lands on the runner
   with question 1 on screen.
2. On the Leaderboard, `/` focuses Find a student, and `M` changes `?metric=` in the URL.
3. Switching scope after the first load issues no blocking request before the table renders
   (Playwright network trace).
4. Browser: on the contest page with a review item focused, `B` saves the question (the Saved
   state shows) and the page does not scroll to the board; `Shift+B` scrolls to the board.
   With a board row focused, `J` moves row focus and does not move the review.


**Acceptance.**
1. A learner who sat days 1–5, missed day 6 and sat day 6's ghost on day 7 → `challenge_streak ==
   7` after day 7's Daily. The same ghost sat on day 9 → the streak restarts.
2. With push kind `daily` on and today's Daily unsat, `POST /api/push/next` at 21:59 local
   returns text starting "Daily Challenge".


**Acceptance.**
1. After a week closes, `GET /api/leaderboard?period=week&at=<last week>` returns the same
   ranks and values before and after new Dailies are sat this week.
2. The first leaderboard request after Monday 12:00 UTC writes 3 `champions` rows per board
   (Points, Over par, Most improved) and 1 per band for the closed week; a second request
   writes none.
3. A learner in a closed season's top 3 has `ring: true` on their board entries throughout the
   next season, and `false` after it.
4. A hidden learner on a podium appears as "Anonymous" in `/api/compete/champions` to others,
   and by name to themselves.
5. `?period=season&at=road-2026-09-12` equals that season's stored `seasons.standings` order.

---

## 3. Spec overrides


## Contracts and amended checks

| # | topic | what disagreed | decision | owner |
| R1 | Navigation | Shell keeps 5 phone tabs; Compete, Words and Review each add a 6th tab | **Desktop sidebar (Shell §2.2), final items.** STUDY: Today, Practice, **Review** (badge: open mistakes; replaces "Mistakes"), **Words**, Tests, Plan, Class (only when in or teaching one). PROGRESS: Results, **Compete** (replaces "Challenge"). **Phone: 5 tabs stay** Today · Practice · Tests · Plan · Results. Review, Words, Compete, Class, Profile, Settings and Help sit in the avatar menu sheet, each at most two taps away; the phone top bar's count chip is Review's. The 6-tab bars in Compete §2, Words §1 and Review §1 are not built. G-keys: G M Review, G W Words, G C Compete (see §2.8). Nav metas: Review "● 14"; Words "12 due"; Compete as Shell's Challenge meta (New / Resume / #4). | F2 |
| R3 | Challenge | Shell keeps `/challenge/` and a practice-rank board at `/challenge/#practice`; Compete replaces it | Compete owns all competition. `/challenge/` redirects (307, served by `api_compete.py`, as Compete §2 says) to `/compete/contest/?id=daily`. Shell's **practice rank** (right answers, rolling 7 days, scopes everyone / same exam date / each class) is Compete's leaderboard metric `right` with period `7d` and a new scope `exam`; the Me snapshot reads it from Compete. `/challenge/#practice` links become `/compete/leaderboard/?metric=right&period=7d`. | S8 |
| R4 | Classes vs groups | Shell has classes/members/assignments; Compete has groups/group_members | **One concept: Class** (Shell §7 tables and `/api/classes`). Compete's groups are classes: the Group board scope is a class's current members; a group contest is a private contest with `grp` = class id and a due time; Me's "Groups" list is the classes list. Creating a class needs a saved email (Shell rule, also for Compete's "Create a group"). Joining needs nothing. One code alphabet and namespace for class codes and contest codes (`^[A-HJ-NP-Z2-9]{6}$`, `db.new_code()`), and `/join/?c=` resolves either. `/api/groups` is not built. | S2 (Compete reads `members`) |
| R7 | Per-question time, trail, strikes in tests | Report adds `sessions.times` and `sessions.trail`; Review adds `sessions.times`; Tests adds `sessions.qstate` | **One column `sessions.qstate`** (JSON): per qid `{ms, struck, conf, trail, first, changes}` and `_session {away_ms, away_n, late}`. Flags are not in it (R5). The runner sends `ms` (dwell delta) and `made_left` with each answer save and other deltas with `POST /api/session/{sid}/state`. `record_paper` passes `qstate[qid].ms` into `attempts.ms`, so tests count as study time and per-question time. Report's `/flag` and `/time` endpoints are served by Review (flags) and Tests (`/state`). | F4 (column, record_paper), S5 (endpoints) |
| R8 | Attempts columns and what counts | Review adds norm/repeat/repair/flagged/stem; QBank guess; Shell disputed; Compete sms/void | **One set of new `attempts` columns:** `norm, repeat, repair, flagged, guess, disputed, sms, void, stem`. Mastery, accuracy, boards and ranks leave out rows with `repeat=1`, `disputed=1` or `void` set; a right answer with `guess=1` counts half. Study time and question counts keep every row. A **clean answer** (closes a mistake, counts as a check-in) is right, not a repeat, not flagged and not a guess. `progress.record` computes `repeat` itself for every caller. | F4 |
| R9 | Traps and check-ins | Review rebuilds traps (id, norm, kinds, relapses) with check-ins at 7/21 days; Plan wants rechecks at 3/10/30 via stage/due; Shell adds source/note/origin | **One `traps` table:** Review's rebuild (integer `id`, `norm`, `reason` = latest concrete text, `closed_how`, `relapses`, `seed`, `session`) plus Shell's `source` ('outside'), `note`, `origin`, plus **one check-in schedule: 3, 10 and 30 days after fixing** (Plan's), stored as `due` + `checks` (0 to 3). A miss on a due check reopens it as Relapsed. Plan's Rechecks task is the drill pool `checks` (R10); Review's "Check these now" and "CHECK-INS DUE" use the same. Kinds: misconception, gridin (named when the template has `spr_mistakes`), slip, unsure. | F4 |
| R10 | Drill body | Nine sections add their own fields to `POST /api/drill` | **One body contract (§2.6)**, validated in one place and built by F5. Section field names map onto it (table in §2.6). Fields that need another section's data stay on `POST /api/drill` and are resolved by the owner's module through a registry: `like` (S3, `daily.resolve_drill`), `word` and `confusion` (S9, `words.resolve_drill`), `assignment` (S2, `classes.resolve_drill`); contests are started by S8's own routes. `list` is accepted as an alias of `pool`, so Review's bodies work unchanged. | F5 |
| R12 | Board identity and names | Shell `learners.board` name/anon/hidden and NAME_OK (no digits); Compete `learners.public`, `country`, HANDLE_OK, uniqueness | `learners.board` = `name` \| `anon` \| `hidden` plus `learners.country` (ISO alpha-2, blank by default). `anon` lists the handle ("Student 4F2A"); `hidden` keeps the row at its real rank with the name "Anonymous" and no row menu, so nobody else's rank moves (Compete's fix). A student always sees their own rank. **Board names follow Compete's rule:** 3 to 24 characters (letters, digits, space, `_ . -`), unique case-insensitively (409), reserved and default-looking names refused (422). NAME_OK stays for the diagnostic sign-up; class display names are 1 to 40 characters. Deleted learners' challenge rows are keyed `gone:…` and show as a handle. | F4 (validation), S8 (boards) |
| R15 | Goals and SAT dates | Target/exam date edited on Today, Me and Plan; R&W fields; three copies of SAT_DATES | `target, exam_date, current, minutes, days, tests, focus, rw_now, rw_target` live on `learners`; the active plan mirrors them both ways (Plan §5, `plan.mirror()`), so one edit shows everywhere. Dashboard's `plan_started` is `plans.start`. Upcoming official dates: one constant in `server/satdates.py`, served in `/api/shell.dates`, read by the date pickers on Today, Me, Plan and Compete's seasons. Past dates are never offered. A new `exam_date` must be today or later in the learner's zone. | F4 |
| R16 | Estimate, confidence, percentile, drift | Report, Tests, Today and Plan each define an estimate or percentile; Compete adds a report percentile | **One module `server/estimate.py`:** `estimate(learner)` returns latest, previous, best, range, `mean3` (mean midpoint of the last up to 3 scored sittings within 45 days, added outside Math scores included), combined (≥2 standard sections: mean ± 70/√n), confidence `{level, reason}` with **Tests §2.2's rules and wording**, trend (±20 = steady), routed_up and counted. `percentile(sid)` ranks a sitting among **each learner's first standard sitting of the same kind** (a paper: of that paper), shown only when n ≥ 20; standard = timed official, adaptive, standard module 1, not fixed-route or extended. The Report hero, Tests cards, Results, Today's score card and the report's Ranked pill all use it; Compete's "last 90 days" variant is not built. **Drift** is Plan's rule (mean3 vs the plan's start, ≥ 40 either way; target reached) and Today's drift line shows Plan's `suggest`. | F4 |
| R18 | Sharing | Five specs define share tokens with colliding routes | **Three kinds, one each.** (a) **Progress link** for a parent or tutor: `links(kind='progress')`, view `/share/?t=`; it shows Me's cards, the Results overview and the plan read-only. Report's `learners.share` and Plan's `view_token` are this token (`/results/?share=` and `/plan/?view=` accept it). (b) **Calendar feed:** `links(kind='cal')`, one server `.ics` builder in `plan.py`, served at `/api/cal/{token}.ics`; the download is `GET /api/plan/ics`. Shell's client-side `UI.ics(plan)` is not built; a single-event helper `UI.ics(event)` (SAT date, a contest, the daily reminder) is in kit. (c) **Question sets:** `sets(code, owner, kind 'set' \| 'test' \| 'items', session, items, cfg, title, show_score, show_name, created, revoked)` for QBank shared sets, Tests shared tests and Review shares; `POST /api/sets`, `GET /api/sets/{code}` (public summary, no stems), `GET /api/sets/{code}/results` (owner only), `DELETE`; landing `/s/?c=CODE` forwards to `/practice/?share=` or `/tests/?shared=`. `navigator.share` is only ever called from a tap on "More ways to share". | F6 (sets), F4 (links table), S1 (progress view), S7 (cal) |
| R25 | Achievements | Shell 43 tiered rules and `earned`; Compete 18 badges and `badges`; Words rules | **One engine `server/achievements.py`** and table `earned(learner, id, tier, at)`. Shell's tiered rules are the base. Compete adds only its unique badges (pace-setter, top-ten, weekly-4, sprinter, dress-rehearsal, season-top-10, level-5, level-8, all-rounder); Words adds 50 / 250 / 1,000 known, a collection complete, a 7-day review streak. Overlaps take Shell's tiered rule. Compete's and Words' rules are declared in their own modules (`ACHIEVEMENTS = [...]` in `compete.py`, `words.py`) and imported when present. | S1 |
| R27 | Question of the day | Today reshapes QOTD (two slots, crowd, past days); Compete wants the spread, a streak and past days | **Today owns QOTD** (`daily.py`), and its API covers Compete's needs: the option spread with misconceptions, the day's-questions streak, 30 past days, graced answers. Compete's contest-page QOTD panel reads `/api/qotd?day=`. | S3 |
| R28 | Contest sittings inside the runners | Compete specifies changes to the practice session and the test window, which S4 and S5 own | S4 and S5 build Compete §8 on their pages and in `drill.py` / `api_tests.py`, through hooks that Compete provides: `compete.clock(row)` (the answer clock), `compete.twin_questions(learner, cid, slots)`, `compete.finish_contest(row)` (points, secs, ranked), `compete.state_extra(row)` (ranked chip, field line). Skip, voiding, reveal-at-end, sprint mode and the leave sheet are generic runner features any sitting can switch on. | S4, S5 (hooks), S8 (functions) |
| R34 | Test pace | several pace numbers | 95 seconds a question everywhere (2100 s ÷ 22, as `MODULE_SECONDS // MODULE_SIZE`). A 10-question challenge is 950 s. | F5 |
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
| S2 | `/api/classes`, `/api/assignments`, `members` | F2 (Class nav item), S3 (due assignments first), S7 (assignment minutes), S8 (class scope) |
| S3 | `/api/qotd?day=`, the "like" drill route, `/api/scores` | S8 (contest page QOTD panel), S6 and S7 (added scores on charts and the plan's test day) |
| S8 | `compete.clock`, `twin_questions`, `finish_contest`, `state_extra`, `rate`, `challenge_streak`, `rank_snapshot`, `/api/contest/daily`, `UI.board`, `UI.level` | S4 and S5 (contest sittings, R28), F4 (`record` rating hook), S3 (challenge card), S1 (snapshot, Boards block) |
| S9 | `words.of_reason`, `words.minutes_today`, `words.today_summary`, `words.me_stats`, `/api/words/today`, `UI.gloss`, `UI.addWord`, `UI.addWordFromSelection` | F5 (feedback words), S7 (Words task), S3 (Words tile), S1 (Me stats), F2 (quick sheet tab), S4, S3, S6, S8 (gloss and add-from-selection hooks) |
### 2.13 Acceptance checks changed by the resolutions
| section | the check says | read it as | why |
| 3.7 Compete | "PUT /api/me {public:false}" | `PUT /api/me {board:'hidden'}` | R12 |
| 3.7 Compete | "badges includes first-contest with an earned date" | `/api/me/achievements` has the Challenge rule at tier I with an earned date | R25 |
| 3.7 Compete | "the phone tab bar shows 6 labelled tabs"; Compete link `aria-current` in the tab bar | 5 tabs; the sidebar Compete item (desktop) and the menu-sheet row (phone) carry `aria-current` | R1 |
