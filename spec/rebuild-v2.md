# SAT Freshman v2: the rebuild plan

Written 2026-09-23. This file replaces `spec/rebuild.md` as the plan and the state
for the site. `spec/rebuild.md` stays as the record of the first rebuild.
The inventory of TopTierPrep behind every section is `spec/toptierprep-teardown.md`
and the raw notes behind it (`ttp-notes.md`).

Contents:

1. What changed and why
2. Shared foundations: rules, cross-section decisions, schema, contracts, and the seven foundation tasks
3. Section specs, one per section, as reviewed
4. Build order: waves, tasks, file ownership, how to merge
5. Open questions for the user

---

## 1. What changed and why

The first rebuild copied TopTierPrep's sections under a set of rules: one pill per
screen, no labels ("nothing narrates"), no borders, the object carries its state.
Those rules are what made every section worse than theirs. We ended up with a
Mistakes page that names a mistake but never shows the question behind it, a Tests
page with two unlabelled doors, a builder with no filters or counts, a nav that
hides Mistakes, Challenge and Me, no search, no report button, no attempt history,
no filters on any list, and settings that exist nowhere.

The user, verbatim:

> "we degraded in every section while chasing minimalism. the goal was to create
> something a lot better than theirs, but we ended up in very bad position. DONT
> CHASE MINIMALISM NOW, review everything they have and PRODUCE SIMILAR STUFF IN WAY
> BETTER WAYS regarding ui/ux and functionality, think of extra functionalities,
> something they missed."

and earlier: "functionality over minimalism, because it is a study platform at the
end of the day", and the exam runner and the practice session share one format,
"the practice one is the best".

So this plan holds every section to one bar:

* **Parity first.** Every feature, filter, stat, control, step, state and page they
  have gets an equivalent here that is at least as capable and clearly better to use.
  Nothing is dropped for looks. Each section spec in Part 3 lists their inventory item
  by item, what we have now (have / partial / missing / worse), and the design that
  closes every gap.
* **Then what they missed.** Extras that only our bank can do: unlimited verified
  questions from ~386 templates, a named misconception behind every wrong option
  (`Item.reasons`), a rationale and skill label on every item, and an exact address
  `(template, seed)` for every question, so "another one like this" never runs out,
  a question can be regenerated exactly, and a fresh version is always possible.
* **Labels, legends, counts, units and one-line helper text are wanted.** Decorative
  fluff is not. Hierarchy comes from size and position, not from withholding.
* **Free.** No plans, quotas, paywalls or upgrade prompts. The slots they use for
  selling show the student's own day.
* **Brand.** Orange `#F18508` is the only accent; graphite `#3F3F3F` ink, warm greys,
  white paper. Archivo (UI), DM Mono (data), Source Serif 4 (question text).

The rules void from now on (and removed from the `ui.css` header by F1): "one pill per
screen", "nothing narrates", "no labels", "no borders", "the object carries its state",
"the pill is the one primary action". Their replacements are in §2.1.

What stays from the first rebuild: the anonymous-first identity, the drill engine's
repair loop, fresh adaptive sections per sitting, the question of the day and the
daily challenge generated from the date, the carry between devices, and the server
checks in `server/test_flow.py`.

Scope: 9 sections reviewed, 7 foundation tasks, 11 section tasks, 1 integration task.
The Math bank is the only bank; Reading & Writing appears only where a section needs
it without a bank (the Words section and optional R&W score fields).

---

## 2. Shared foundations

### How to read this document

* Part 3 holds each section's reviewed spec **verbatim**: their inventory, our state,
  the design, extras, server changes, files, shared needs, acceptance checks and the
  section's own open questions.
* Where two section specs disagree, **§2.2 Resolutions wins**. Each section in Part 3
  starts with a box that names the resolutions that change it. Read those first.
* Where a section spec names a file another task owns, **§2.9 Contracts** says how
  the need is met: the owner builds it, or the consumer adds a named hook on its own
  page. Part 3 prints, for every file a spec names, who owns it.
* Schema, prefs keys, the drill body, keys and status tokens are defined **once**
  here (§2.3 to §2.8). A section spec that defines its own version of any of these
  is read through the canonical one.

### 2.1 Design rules (they replace spec/rebuild.md's "Principles")

1. **Functionality first.** Every control that a student acts on has a visible text
   label. Legends carry counts. Numbers carry units. Every control that changes how
   practice behaves has a one-line helper under it. Every empty state says what will
   appear there and offers the action that fills it.
2. **One primary per region, not per screen.** A region is a page header, a card, a
   sheet, a player or an action bar. Its primary action is the filled orange pill.
   Secondary actions are `.btn` (`--tile-2` fill, 40px tall, 10px radius, Archivo
   600 14px, ink text). Tertiary actions are `.quiet` text buttons. Hierarchy comes
   from size and position.
3. **Borders where they separate.** A 1px `--line` border wherever grouping needs it.
   Cards are `--tile` on paper, radius 14, padding 20 to 24 (16 on a phone).
4. **Orange is the only accent.** It marks what is yours or live: the selection, the
   key, the recommended action, your row, open-mistake dots, goal fills. Status is
   never colour alone: every state has a glyph and text (§2.3). Destructive actions
   are graphite behind a confirm sheet, never red (the runner's `#b3261e` goes).
   Orange fills carry `--ink-deep` text.
5. **One source per fact.** Streak, study time, target, exam date, the estimate,
   the percentile, the open-mistake count, prefs: each comes from one server
   function and reads the same on every screen.
6. **Nothing floats over content.** No floating button. The practice session and the
   test window render no site chrome, so nothing can cover Next.
7. **Nothing a student does is lost.** Answers, flags, strikes, highlights, notes,
   confidence tags and time per question live on the server and come back after a
   reload or on another device with the same code.
8. **Every page has four states designed:** loading (static skeletons at final size,
   no looping shimmer), error (inside the failing card, with Retry; the rest still
   renders), new student (every card keeps its frame and its empty-state action),
   and lots of history (paging, collapse past N, server-side counts).
9. **Phone at 390px:** 16px gutters, no horizontal page scroll, 44px touch targets,
   sheets become bottom sheets, nothing hidden that desktop shows (it wraps or
   stacks instead).
10. **Motion is entry only.** Nothing loops. `prefers-reduced-motion` turns it off.
11. **Type:** Archivo for UI, DM Mono for counts, times, clocks and ids, Source Serif 4
    for question text at `--q-size` / `--q-opt` (small 17/15.5, normal 20/18.5, large
    23/21 by `prefs.text`).
12. **Copy:** no emoji; the flame, trophy and marks are our icons. "Question 7 of 22".
    Thousands separators. Times as `1:12`, durations as `42h 10m`.

### 2.2 Resolutions: one decision where section specs disagree

Numbered, so Part 3 and the tasks can cite them. "Wins" names the spec whose text is
canonical; the owner is the task that builds it.

| # | topic | what disagreed | decision | owner |
|---|---|---|---|---|
| R1 | Navigation | Shell keeps 5 phone tabs; Compete, Words and Review each add a 6th tab | **Desktop sidebar (Shell §2.2), final items.** STUDY: Today, Practice, **Review** (badge: open mistakes; replaces "Mistakes"), **Words**, Tests, Plan, Class (only when in or teaching one). PROGRESS: Results, **Compete** (replaces "Challenge"). **Phone: 5 tabs stay** Today · Practice · Tests · Plan · Results. Review, Words, Compete, Class, Profile, Settings and Help sit in the avatar menu sheet, each at most two taps away; the phone top bar's count chip is Review's. The 6-tab bars in Compete §2, Words §1 and Review §1 are not built. G-keys: G M Review, G W Words, G C Compete (see §2.8). Nav metas: Review "● 14"; Words "12 due"; Compete as Shell's Challenge meta (New / Resume / #4). | F2 |
| R2 | Mistakes page | Shell and Today link `/mistakes/`; Review replaces it | `/review/` is the page (Review spec). `/mistakes/` redirects (307, served by `api_review.py`) to `/review/?tab=redo`, keeping the query. Every "Mistakes" reference in other specs means Review. Mistakes logged from outside (Shell §2.7) appear in Review's Redo tab with a "Logged by you · Bluebook" chip and their note. | S10 |
| R3 | Challenge | Shell keeps `/challenge/` and a practice-rank board at `/challenge/#practice`; Compete replaces it | Compete owns all competition. `/challenge/` redirects (307, served by `api_compete.py`, as Compete §2 says) to `/compete/contest/?id=daily`. Shell's **practice rank** (right answers, rolling 7 days, scopes everyone / same exam date / each class) is Compete's leaderboard metric `right` with period `7d` and a new scope `exam`; the Me snapshot reads it from Compete. `/challenge/#practice` links become `/compete/leaderboard/?metric=right&period=7d`. | S8 |
| R4 | Classes vs groups | Shell has classes/members/assignments; Compete has groups/group_members | **One concept: Class** (Shell §7 tables and `/api/classes`). Compete's groups are classes: the Group board scope is a class's current members; a group contest is a private contest with `grp` = class id and a due time; Me's "Groups" list is the classes list. Creating a class needs a saved email (Shell rule, also for Compete's "Create a group"). Joining needs nothing. One code alphabet and namespace for class codes and contest codes (`^[A-HJ-NP-Z2-9]{6}$`, `db.new_code()`), and `/join/?c=` resolves either. `/api/groups` is not built. | S2 (Compete reads `members`) |
| R5 | Mark vs Save | QBank merges marking into saving (as TopTierPrep does); Review keeps them apart | **Two things everywhere** (Review model). *Mark for review* = a flag on one question in one sitting (`flags` table, flag icon, per sitting). *Save* = keep a question for good (`saved` table, bookmark icon). QBank's "rename Saved to Marked for review" is not done; its builder gets two pools, Marked and Saved. QBank's "a right replay removes it from Marked" is not built; Review has Unmark / Unsave with Undo. The Report button's icon is a speech bubble with "!", never a flag. | F4 (tables), S10 (endpoints) |
| R6 | Highlights and notes | QBank stores notes per (template, seed); Tests stores marks per sitting in `qstate`; Review stores a note on `saved` | **One store:** `notes(learner, template, seed, note ≤1000, marks JSON ≤50)`. Written with `POST /api/notes {session, question_id, note?, marks?}` from any sitting kind; the server resolves (template, seed) and never trusts the client for them. Mark styles are Tests' seven: highlight, strong, underline, dashed, dotted, box, strike (each mark may carry a note ≤500). A saved question's note (Review §5) is the same note. Notes come back wherever that exact question appears: replay, retake, review, report, Saved. | F4 (`api_notes.py`), F3 (`UI.annotate`) |
| R7 | Per-question time, trail, strikes in tests | Report adds `sessions.times` and `sessions.trail`; Review adds `sessions.times`; Tests adds `sessions.qstate` | **One column `sessions.qstate`** (JSON): per qid `{ms, struck, conf, trail, first, changes}` and `_session {away_ms, away_n, late}`. Flags are not in it (R5). The runner sends `ms` (dwell delta) and `made_left` with each answer save and other deltas with `POST /api/session/{sid}/state`. `record_paper` passes `qstate[qid].ms` into `attempts.ms`, so tests count as study time and per-question time. Report's `/flag` and `/time` endpoints are served by Review (flags) and Tests (`/state`). | F4 (column, record_paper), S5 (endpoints) |
| R8 | Attempts columns and what counts | Review adds norm/repeat/repair/flagged/stem; QBank guess; Shell disputed; Compete sms/void | **One set of new `attempts` columns:** `norm, repeat, repair, flagged, guess, disputed, sms, void, stem`. Mastery, accuracy, boards and ranks leave out rows with `repeat=1`, `disputed=1` or `void` set; a right answer with `guess=1` counts half. Study time and question counts keep every row. A **clean answer** (closes a mistake, counts as a check-in) is right, not a repeat, not flagged and not a guess. `progress.record` computes `repeat` itself for every caller. | F4 |
| R9 | Traps and check-ins | Review rebuilds traps (id, norm, kinds, relapses) with check-ins at 7/21 days; Plan wants rechecks at 3/10/30 via stage/due; Shell adds source/note/origin | **One `traps` table:** Review's rebuild (integer `id`, `norm`, `reason` = latest concrete text, `closed_how`, `relapses`, `seed`, `session`) plus Shell's `source` ('outside'), `note`, `origin`, plus **one check-in schedule: 3, 10 and 30 days after fixing** (Plan's), stored as `due` + `checks` (0 to 3). A miss on a due check reopens it as Relapsed. Plan's Rechecks task is the drill pool `checks` (R10); Review's "Check these now" and "CHECK-INS DUE" use the same. Kinds: misconception, gridin (named when the template has `spr_mistakes`), slip, unsure. | F4 |
| R10 | Drill body | Nine sections add their own fields to `POST /api/drill` | **One body contract (§2.6)**, validated in one place and built by F5. Section field names map onto it (table in §2.6). Fields that need another section's data stay on `POST /api/drill` and are resolved by the owner's module through a registry: `like` (S3, `daily.resolve_drill`), `word` and `confusion` (S9, `words.resolve_drill`), `assignment` (S2, `classes.resolve_drill`); contests are started by S8's own routes. `list` is accepted as an alias of `pool`, so Review's bodies work unchanged. | F5 |
| R11 | Preferences | Shell prefs, QBank prefs, Tests `learners.test_prefs`, Words `words_goal/words_from/gloss` columns, Shell `study_time` column | **One `learners.prefs` JSON and one registry `server/prefs.py`** with every key in §2.7. The separate columns are not added. Settings (S1) renders every key; the Practice builder, the test start sheet, Plan step 4, Me and the session's More menu write the same keys. Unknown key or bad value → 422 naming the key; only non-default values are stored; GET returns defaults merged. | F4 |
| R12 | Board identity and names | Shell `learners.board` name/anon/hidden and NAME_OK (no digits); Compete `learners.public`, `country`, HANDLE_OK, uniqueness | `learners.board` = `name` \| `anon` \| `hidden` plus `learners.country` (ISO alpha-2, blank by default). `anon` lists the handle ("Student 4F2A"); `hidden` keeps the row at its real rank with the name "Anonymous" and no row menu, so nobody else's rank moves (Compete's fix). A student always sees their own rank. **Board names follow Compete's rule:** 3 to 24 characters (letters, digits, space, `_ . -`), unique case-insensitively (409), reserved and default-looking names refused (422). NAME_OK stays for the diagnostic sign-up; class display names are 1 to 40 characters. Deleted learners' challenge rows are keyed `gone:…` and show as a handle. | F4 (validation), S8 (boards) |
| R13 | Streak and study time | Shell, Today, Plan and Words each define a streak or minutes rule | **One function `progress.days(learner, tz, weeks)`**, used by the shell, Today, Me, Plan, Results and Words. A day is the learner's local day (X-Tz). A study day has at least one answer, or at least 10 word reviews, or a finished sitting. Rest days of the **active plan** (a weekday off, a day off, the exam's eve) neither break nor extend the streak; a rest day with practice extends it. Minutes = attempt ms (each capped at 10 min) + each finished sitting's elapsed time **only when its attempts carry no ms** (capped per module at its clock + 60s; untimed 90 min) + word reviews (each ≤ 60 s) + minutes of the student's own plan tasks marked done. Returns streak, best, active days, minutes and per-day rows for up to 53 weeks. Today's three labelled streaks are three facts: study (this), day's questions (`daily.qotd_streak`), challenge (`compete.challenge_streak`). The 60-minute after-midnight grace applies to the question of the day only. | F4 |
| R14 | Plan arithmetic | Shell and Today compute plan days on the client (`UI.plan.dayOf/doneOf`) and add `plan_marks`; Plan puts all of it on the server | **Server only, `server/plan.py`** (Plan spec). `UI.plan.dayOf/testOf/doneOf` are deleted. Today's plan list, the shell's Today and Plan metas, the Today card and Me's week dots read `/api/today.plan` and `/api/shell.plan` (Plan provides `plan.today_summary()`). Today's Skip / Move use Plan's `PATCH /api/plan/{id}/tasks/{task}` (any study day up to the eve, not only this week). Dashboard's `plan_marks` table and `POST /api/plan/mark` are not built. | S7 |
| R15 | Goals and SAT dates | Target/exam date edited on Today, Me and Plan; R&W fields; three copies of SAT_DATES | `target, exam_date, current, minutes, days, tests, focus, rw_now, rw_target` live on `learners`; the active plan mirrors them both ways (Plan §5, `plan.mirror()`), so one edit shows everywhere. Dashboard's `plan_started` is `plans.start`. Upcoming official dates: one constant in `server/satdates.py`, served in `/api/shell.dates`, read by the date pickers on Today, Me, Plan and Compete's seasons. Past dates are never offered. A new `exam_date` must be today or later in the learner's zone. | F4 |
| R16 | Estimate, confidence, percentile, drift | Report, Tests, Today and Plan each define an estimate or percentile; Compete adds a report percentile | **One module `server/estimate.py`:** `estimate(learner)` returns latest, previous, best, range, `mean3` (mean midpoint of the last up to 3 scored sittings within 45 days, added outside Math scores included), combined (≥2 standard sections: mean ± 70/√n), confidence `{level, reason}` with **Tests §2.2's rules and wording**, trend (±20 = steady), routed_up and counted. `percentile(sid)` ranks a sitting among **each learner's first standard sitting of the same kind** (a paper: of that paper), shown only when n ≥ 20; standard = timed official, adaptive, standard module 1, not fixed-route or extended. The Report hero, Tests cards, Results, Today's score card and the report's Ranked pill all use it; Compete's "last 90 days" variant is not built. **Drift** is Plan's rule (mean3 vs the plan's start, ≥ 40 either way; target reached) and Today's drift line shows Plan's `suggest`. | F4 |
| R17 | Report a problem | Shell (10 images downscaled, disputes, admin), QBank (3 × 5 MB BLOBs), Tests (R-#### ids, tools), Report (3 screenshots), Words (10 images) | **One system:** Shell §2.10 and §10 are canonical: one modal `UI.report(ctx)`, up to 10 images (PNG, JPEG, WebP, GIF), stills downscaled in the browser to 2000px, 10 MB server cap, files on disk under `server/reports/{id}/` (git-ignored), bounded disputes (5 open), Your reports with replies in Settings, `/admin/reports` behind `SATF_ADMIN_TOKEN`. Categories per context are the union: Shell's lists, plus Tests' "More than one right answer" and "No right answer", plus Words' "Wrong or unclear definition" (word context). Mid-test reports never show marking and hide key disputes. Rate limit: 10 an hour and 20 a day per learner (429). Ids are integers. `tools/reports.py` is an optional CLI over the same table. | F6 |
| R18 | Sharing | Five specs define share tokens with colliding routes | **Three kinds, one each.** (a) **Progress link** for a parent or tutor: `links(kind='progress')`, view `/share/?t=`; it shows Me's cards, the Results overview and the plan read-only. Report's `learners.share` and Plan's `view_token` are this token (`/results/?share=` and `/plan/?view=` accept it). (b) **Calendar feed:** `links(kind='cal')`, one server `.ics` builder in `plan.py`, served at `/api/cal/{token}.ics`; the download is `GET /api/plan/ics`. Shell's client-side `UI.ics(plan)` is not built; a single-event helper `UI.ics(event)` (SAT date, a contest, the daily reminder) is in kit. (c) **Question sets:** `sets(code, owner, kind 'set' \| 'test' \| 'items', session, items, cfg, title, show_score, show_name, created, revoked)` for QBank shared sets, Tests shared tests and Review shares; `POST /api/sets`, `GET /api/sets/{code}` (public summary, no stems), `GET /api/sets/{code}/results` (owner only), `DELETE`; landing `/s/?c=CODE` forwards to `/practice/?share=` or `/tests/?shared=`. `navigator.share` is only ever called from a tap on "More ways to share". | F6 (sets), F4 (links table), S1 (progress view), S7 (cal) |
| R19 | Access to keys and re-serving | Review defines `access()`; others re-serve items ad hoc | **One rule, `deps.access(learner, template, seed)` → `reveal` \| `kept` \| None** (Review §server). Everything that returns a key or re-serves an exact (template, seed) goes through it: review endpoints, sets, worksheets, the report, the challenge review, permalinks, Words examples. Live-test items and unanswered or same-day challenge items never leak. The permalink `/practice/session/?q=TEMPLATE:SEED` (QBank; Shell's `/q/` is the same route) serves any catalogue item that is not in today's challenge as a fresh one-question drill; the key shows after answering, as always. | F4 |
| R20 | Status colours and glyphs | Report flips nothing; QBank uses wash for correct; Compete/Review differ | **The practice session's semantics, with glyphs everywhere** (§2.3): right = orange, wrong = graphite, plus Mixed (right on a retry) and Repaired (right on the repair after a miss) as two states, skipped, blank, voided, repeat, not reached, answered (exam), flagged, saved, has note, current. One legend component. | F1 |
| R21 | One question format | QBank `UI.workspace`, Tests runner shell, Today confirm mode, Words quiz mode | **One component `UI.workspace` (question.js) and one runner shell (runner.js/css).** Modes: `practice` (feedback instant / retry / end), `exam`, `review` (read-only, Hide answers, re-answer files a repeat), `quiz` (Words), `inline` (quick sheet, Today's Try one, sheets). The practice session and the exam runner use the same runner shell: sticky top bar, progress rail, question strip, footer (Back · "Question N of M ⌃" · Check/Next), navigator, Check your work, timer, calculator dock, highlights. The exam runner's look is the practice session's (Tests §1). `UI.question` stays as a thin alias. | F3 |
| R22 | Keyboard | QBank uses C for calculator and S for skip; Review S for save; clashes with choosing C | **One registry `UI.keys` (F2) and one map (§2.8).** Calculator G, reference F, save B, skip S, history Y, highlights L, confidence K. Shortcuts are ignored while typing (Enter and Esc aside) and when `prefs.keys` is off. | F2, F3 |
| R23 | Review player, pane and history | Report's `UI.review` player, Review's `UI.questionReview` pane, QBank's review sheet | **One component `UI.review(host, items, opts)`** with `mode: 'dialog'` (Report §1.13 layout) and `mode: 'pane'` (Review §8), plus **`UI.history`** (Review §9 attempt history for the whole question type), used by the session, the report, Review and the challenge review. Report's "Try one like this" tile and Review's inline mini-session are the same inline drill. | F3 |
| R24 | Drills that are not sittings | twin, try, word-example, review pane, spot, quick each have their own list rule | `cfg.inline = true` for sources `twin, try, word-example, review, spot`: never listed as a sitting, never in history, In progress or Resume; their answers file normally (a twin counts on its parent). `quick` sittings are listed in history as "Quick questions", never offered as Resume, and deleted when finished with 0 answers. Any set finished with 0 answered is never listed. | F5 (flag), S6 (history), S4 (drill list) |
| R25 | Achievements | Shell 43 tiered rules and `earned`; Compete 18 badges and `badges`; Words rules | **One engine `server/achievements.py`** and table `earned(learner, id, tier, at)`. Shell's tiered rules are the base. Compete adds only its unique badges (pace-setter, top-ten, weekly-4, sprinter, dress-rehearsal, season-top-10, level-5, level-8, all-rounder); Words adds 50 / 250 / 1,000 known, a collection complete, a 7-day review streak. Overlaps take Shell's tiered rule. Compete's and Words' rules are declared in their own modules (`ACHIEVEMENTS = [...]` in `compete.py`, `words.py`) and imported when present. | S1 |
| R26 | The sittings list | Tests, Report, Words, Review, Today each extend `/api/history` or add a list | **One endpoint `/api/history`** (S6) with every field in Report §server plus Tests' statuses, `all=1`, modules, blanks vs wrong, twin and paper labels, Words' `kind=words` filter and counts. Today's "Recent tests" reads `/api/history?kind=tests&all=1&limit=6`; Dashboard's separate `/api/tests/recent` is not built. The report page redirects a words-run id to `/words/run/?id=`. | S6 |
| R27 | Question of the day | Today reshapes QOTD (two slots, crowd, past days); Compete wants the spread, a streak and past days | **Today owns QOTD** (`daily.py`), and its API covers Compete's needs: the option spread with misconceptions, the day's-questions streak, 30 past days, graced answers. Compete's contest-page QOTD panel reads `/api/qotd?day=`. | S3 |
| R28 | Contest sittings inside the runners | Compete specifies changes to the practice session and the test window, which S4 and S5 own | S4 and S5 build Compete §8 on their pages and in `drill.py` / `api_tests.py`, through hooks that Compete provides: `compete.clock(row)` (the answer clock), `compete.twin_questions(learner, cid, slots)`, `compete.finish_contest(row)` (points, secs, ranked), `compete.state_extra(row)` (ranked chip, field line). Skip, voiding, reveal-at-end, sprint mode and the leave sheet are generic runner features any sitting can switch on. | S4, S5 (hooks), S8 (functions) |
| R29 | The quick sheet | Shell's floating-button equivalent has Quick question and Log a mistake; Words adds a "+ word" bar button | **One quick sheet (Q key, bolt in the sidebar and phone bar) with three tabs:** Quick question · Log a mistake · Add a word. The third calls `UI.addWord()` from `words-ui.js`. This is their add-your-own-word button, done without covering anything. Words' "+ word" bar button is not built; Words keeps Add to my words on selected text and N on its pages. | F2 (sheet), S9 (`UI.addWord`) |
| R30 | Today's cards | Today has a Mistakes card; Review wants a Review card; Words wants a Words tile | Today's `#mist` card **is** the Review card: Review's counts (open, half fixed, check-ins due, marked) plus Today's top 5, Fix and Try one now. A **Words tile** joins the grid: desktop `plan ×8 · words ×4` (the plan card spans 8, the Words tile 4); phone after the challenge card. | S3 |
| R31 | Me's tiles | Shell's 2×3 stat grid; Words and Compete want stats on Me | Me's identity grid becomes **2×4**: Streak, Answered, Accuracy, Study time, Tests, Mistakes fixed (Shell), plus **Words** ("31 known · 12 due") and **Rating** ("Level 3 · 1,084"). Me's Snapshot reads ranks from Compete; Saved & in progress reads Review's counts; Test defaults appear under Learning preferences. | S1 |
| R32 | Theme tokens in the test window | Shell tokenises `web/test/`; Tests rewrites it | The Tests rewrite ends with no hard-coded colours in `web/test/` (Shell's grep acceptance applies to S5). Me and the report page are tokenised by their owners (S1, S6). | S5, S1, S6 |
| R33 | Adaptive difficulty | Shell maps mastery to a tier; QBank steps up after 2 first-try rights | QBank's rule (step up a tier after 2 first-try rights in a skill, down after a miss, within the selected tiers). Shell's "Adaptive" option is `adaptive: true` with all tiers. | F5 |
| R34 | Test pace | several pace numbers | 95 seconds a question everywhere (2100 s ÷ 22, as `MODULE_SECONDS // MODULE_SIZE`). A 10-question challenge is 950 s. | F5 |
| R35 | Blank vs wrong | Report says blanks are never Incorrect; Tests shows blank chips | One bucket set everywhere: Correct / Incorrect / Unanswered; Incorrect never includes blanks; blanks are dashed-outline chips. | F1, S6 |
| R36 | Session kinds | new kinds from Tests and Words | New `sessions.kind` values: `custom` (Tests' custom test), `words` (Words runs), `spot` (Review). `UI.KIND` (kit) holds every label; `/api/history` lists `words` only with `?kind=words` and never lists `spot`. | F1, S6 |
| R37 | Mastery display | bar vs % | A bar plus `UI.masteryWord(m, answered)` (Not started / Learning / Getting there / Strong), with accuracy printed beside it as its own %. | F1 |
| R38 | Diagnostic gate | Today and Report respect the sign-up gate | Kept as today until the user decides (open question 8). Today, Report, Tests and Fix all respect it. | S3, S5, S6 |

### 2.3 Status and difficulty tokens (one set, every page; F1 builds, R20)

Every cell, strip segment, navigator square, list mark and chart point that shows a
question's state uses these, always with the glyph, and always next to a legend that
carries counts.

| state | fill / edge | glyph | meaning |
|---|---|---|---|
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

Difficulty is three ascending bars (▁▃▅, 1 to 3 filled, ink on `--mat`) plus the word
Easy / Medium / Hard, never colour alone. Where a view colours by difficulty (the
navigator's Difficulty view, the report's "Colour by"), the tints are `--lvl-easy
#FDEBD3`, `--lvl-med #F8BE7A`, `--lvl-hard #F18508` (with `--ink-deep` text), each
with a corner letter E / M / H, and a measured level adds its number ("M4").

Mastery is a bar plus `UI.masteryWord(m, answered)` (Not started / Learning below 0.4
/ Getting there / Strong at `progress.STRONG` = 0.8) with accuracy printed beside it
(R37). An open mistake is an orange dot.

Dark theme tokens are Shell §2.13's table; light stays the default.

### 2.4 Component inventory: who builds what, in which file

Pages load, in order: `/assets/head.js` (in `<head>`), `ui.css`, then at the end of
`<body>`: `ui.js`, `kit.js`, `charts.js`, and on the two runner pages `question.js` and
`runner.js` (+ `runner.css`). Every file below adds to `window.UI` with
`Object.assign(UI, {...})`. A section-owned file is loaded only by the pages that need
it. Signatures are the contract; a consumer may code against a signature before its
file lands.

| file | owner | components (signature, then who uses it) |
|---|---|---|
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

A consumer calls section-owned helpers defensively (`UI.gloss && UI.gloss(el)`), so a page
works before the provider's file lands.

### 2.5 Schema: every table and column, added once by F4

F4 adds all of these in `server/db.py` (new tables in `SCHEMA`, new columns in
`LATER_COLUMNS`), so no other task edits `db.py`. Empty tables cost nothing. A data
migration that belongs to a section's meaning (challenges → contests, points backfill)
runs from that section's module `init()` (§2.10), idempotently.

**Existing tables, new columns**

* `learners`: `avatar TEXT` (a topic slug; NULL = the initial), `prefs TEXT` (JSON, non-default keys only, R11), `board TEXT` (name | anon | hidden; NULL = name), `country TEXT`, `ach_seen TEXT`, `rw_now INTEGER`, `rw_target INTEGER`, `plan TEXT` (active plan id), `plan_draft TEXT` (JSON), `rating REAL DEFAULT 1000`, `rated INTEGER DEFAULT 0`. `db.ensure_learner(code)` inserts the row on first write (today a row exists only after `PUT /api/me`).
* `users`: `learner TEXT`, `login_token TEXT`, `login_code TEXT` (sha256 of the 6 digits), `login_for TEXT`, `login_sent TEXT`, `login_tries INTEGER DEFAULT 0`, `last_login TEXT`. First and last stay NOT NULL; email-only accounts insert `''`.
* `attempts`: `norm TEXT`, `repeat INTEGER NOT NULL DEFAULT 0`, `repair INTEGER NOT NULL DEFAULT 0`, `flagged INTEGER NOT NULL DEFAULT 0`, `guess INTEGER NOT NULL DEFAULT 0`, `disputed INTEGER NOT NULL DEFAULT 0`, `sms INTEGER` (server-measured ms), `void TEXT`, `stem TEXT` (first 200 characters, for search). A one-off startup backfill fills `stem` and `norm` for old rows (0.26 ms a regeneration).
* `traps`: rebuilt (as `_relax_form_id` rebuilds sessions): `id INTEGER PRIMARY KEY, learner, template, norm, reason, label, topic, hits, owed, opened, last, closed, closed_how, relapses INTEGER DEFAULT 0, seed INTEGER, session TEXT, due TEXT, checks INTEGER DEFAULT 0, source TEXT, note TEXT, origin TEXT`, `UNIQUE(learner, template, norm)`. The migration merges old rows with equal norm (hits summed, opened MIN, last and owed MAX, open if any merged row is open) and fills seed/session from the latest wrong attempt.
* `saved`: `session TEXT`, `qid TEXT` (the note is in `notes`, R6).
* `sessions`: `qstate TEXT DEFAULT '{}'` (R7), `paused_at TEXT`, `paused_ms INTEGER DEFAULT 0`, `pauses INTEGER DEFAULT 0`, `abandoned TEXT`, `number INTEGER`, `note TEXT`, `shared_from TEXT` (a set code), `assignment TEXT`, `contest TEXT`, `ranked INTEGER DEFAULT 1`, `points INTEGER`, `secs INTEGER`, `unranked_why TEXT`.

**New tables** (owner = the task whose module writes it; everyone may read)

| table | columns | written by |
|---|---|---|
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

Not added (superseded by the resolutions): Compete's `groups`, `group_members`,
`badges`; QBank's `report_files` and its own `shares`; Tests' `shares`; Review's
`shares`; Report's `sessions.flags`, `sessions.times`, `sessions.trail` and
`learners.share`; Plan's `cal_token`, `view_token`; Shell's `learners.cal_token`,
`learners.study_time`; Tests' `learners.test_prefs`; Words' `learners.words_goal /
words_from / gloss`; Compete's `learners.public`; Dashboard's `plan_marks` (its own
shape) and `learners.plan_started`.

Indexes: `attempts(learner, at)`, `attempts(at)`, `attempts(learner, template, seed)`,
`attempts(session, qid)`, `users(learner)`, `users(login_token)`, `sessions(mock_id,
finished)`, `sessions(learner, abandoned)`, `sessions(contest, ranked, points DESC,
secs)`, `sessions(learner, contest)`, `reports(learner, at)`, `posts(paper, parent, at)`,
`word_state(learner, due)`, `word_reviews(learner, at)`, `my_words(learner)`,
`flags(learner, session)`, `plans(learner, archived)`.

`progress.carry(src, dst)` (F4) moves every learner-keyed table above with the merge rule
each spec states (Shell, Plan, Words, Compete, Review). `db.LEARNER_TABLES` lists them for
S1's export and delete. `db.new_code()` makes a 6-character code unique across
`classes.code` and `contests.code` (R4).

### 2.6 The drill body (one contract; F5 builds it, R10)

`POST /api/drill`, and `POST /api/drill/preview` with the same body (creates nothing,
returns counts and the reason nothing can be served). Python callers use
`drill.create(learner, body: dict)`. Every field is optional; everything is validated
before anything is created; nothing servable → 409 with `reason`.

| field | values | meaning |
|---|---|---|
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

How section fields map in:

| spec | its field | canonical |
|---|---|---|
| Shell | `unseen`, `trap {template, reason}`, `format`, `difficulty:'adaptive'`, `templates` | `pool:'untried'`, `pool:'redo', ids:[trap id]`, `formats`, `adaptive:true`, `templates` |
| Today | `like {day, slot}`; `mistakes:true, templates, count` | kept on the body; `daily.resolve_drill` (S3) turns it into `templates`, `exclude` (and the 409 "answer it first"); `pool:'redo', templates, count` |
| QBank | `pool:'mistakes'`, `saved:true`, `share`, `difficulty` | `pool:'redo'`, `pool:'saved', exact:true`, `pool:'set', ids:code`, `tiers` |
| Plan | `recheck:true`, `fmt`, `task` | `pool:'checks'`, `formats` / `spr_share`, `task` |
| Words | `word`, `confusion` | kept on the body; `words.resolve_drill` (S9) turns them into `templates`, `want` (409 for a bankless mix-up) |
| Review | `list`, `ids`, `exact`, `each`, `level` | `list` is an alias of `pool` (fixed → `checks`, templates → `templates`, share → `set`); same names otherwise |
| Report | `only`, `each`, `scope`, `still_open`, `source:'twin'` | same names; `parent` = the report's sitting |
| Compete | `templates` ("another like this") | same |

Drill feedback (F5) also returns, per answer: `reasons` (every option's label, null at the
key), `filler` flags, `family {seen, right}`, `flagged`, `repeat`, trap ids opened or
closed, and `words` / `confusion` when `words.of_reason(template, reason)` exists (S9).
`public(q)` adds `seen` (attempts on this template) and `why` (why the scheduler chose it).

### 2.7 Preferences: every key (F4's `server/prefs.py`, R11)

Stored in `learners.prefs` as JSON with only non-default keys. `PUT /api/me {prefs: {...}}`
merges; an unknown key or bad value is 422 naming the key. `GET /api/me` and `/api/shell`
return the merged object. Settings (S1) shows every key with its helper line (Shell §4
and QBank §1.7 wording); the other surfaces listed edit the same key.

| key | values | default | also edited in |
|---|---|---|---|
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

Not prefs (their own columns): name, avatar, board, country, target, exam_date, current,
minutes, days, tests, focus, rw_now, rw_target. Per-viewer conveniences stay in
localStorage (sidebar collapse, filters, the hidden clock per sitting, calculator position,
checklist ticks, drafts), always inside try/catch.

### 2.8 Keyboard (one registry `UI.keys`, R22)

Ignored while focus is in an input, textarea, select or contenteditable (Enter and Esc
aside), while a dialog is open (Esc aside), and when `prefs.keys` is off. The `?` sheet
lists Global and This page.

| scope | keys |
|---|---|
| Global (pages with the shell) | `G` then `T` Today · `P` Practice · `M` Review · `W` Words · `E` Tests · `L` Plan · `K` Class · `R` Results · `C` Compete · `U` Profile · `S` Settings · `H` Help. `Q` quick sheet. ⌘K / Ctrl K palette (`/` too, except on pages where `/` focuses that page's search: Words, Review). `[` collapse the sidebar. `?` shortcuts |
| Runner: practice session and test window | `A–D` / `1–4` choose · `Shift+A–D` strike / undo · `Enter` Check, Next or Save & next · `←` `→` back / next · `E` eliminate mode · `M` mark for review · `B` save (practice) · `L` highlights & notes · `O` my note · `K` confidence (exam, when on) · `I` I'm guessing (practice) · `S` skip (practice) · `D` details · `N` navigator · `Y` attempt history (after answering) · `G` calculator · `F` reference (formula sheet) · `H` hide / show timer · `P` pause (practice) · `Shift+R` check your work · `?` · `Esc` |
| Player: report review, Review pane, challenge review | `←` `→` or `J` `K` move · `N` next miss · `H` hide / show answers · `T` try one like this · `E` again, exactly · `B` save · `M` mark · `Y` history · `I` details · `R` report · `A–D` / `1–4` pick while answers are hidden · `Esc` |
| Lists (Review, Words) | `J` `K` or `↑` `↓` move · `Enter` open · `X` select · `/` search · `N` add a word (Words) |
| Flashcards and word quizzes | `Space` flip · `1` / `2` grade · `←` `→` · `B` save (after the verdict in a quiz) · `P` speak · `O` open word · `A–D` / `1–4` |

### 2.9 Contracts: who provides what to whom

A task only edits files it owns (Part 4). When a section needs something from another
section, the provider builds it in its own files, and the consumer calls it from its own
page or module. Consumers code against the signature and degrade quietly until it lands.

| provider | provides | consumers |
|---|---|---|
| F2 | `/api/shell` with parts from other modules (§2.10) | every page with the shell |
| F4 | `progress.days`, `estimate.estimate`, `estimate.percentile`, `deps.access`, `satdates`, `prefs`, `POST /api/notes`, `scoring.accepted_forms`, `scoring.fraction_for` | all sections |
| F5 | the drill body; `GET /api/types`, `GET /api/types/{t}/example`, `POST /api/mistakes/log`; `drill.levels()`, `blueprint.kinds()` | F2 (palette, Log a mistake), S2 (assignment type search), S3, S4, S7, S8, S9, S10 |
| F6 | `UI.report`, `POST /api/report`, `GET /api/reports`; `sets` endpoints and `/s/` | every page with a question; S4, S5, S10 (share); S6 (peers) |
| S1 | `/signin/`, `/pair/`, account endpoints; `/api/me/summary`, `/feed`, `/activity`, `/achievements`, `/seen`; the progress-link view `/share/?t=` | F2 (menu links, toasts); S6 and S7 (their pages accept the progress token) |
| S2 | `/api/classes`, `/api/assignments`, `members` | F2 (Class nav item), S3 (due assignments first), S7 (assignment minutes), S8 (class scope) |
| S3 | `/api/qotd?day=`, the "like" drill route, `/api/scores` | S8 (contest page QOTD panel), S6 and S7 (added scores on charts and the plan's test day) |
| S4 | `/api/bank`, `/api/drill` list (Your sets), permalink `?q=` | S1 (question types met), S3 (Continue), palette |
| S5 | the lobby at `/test/?s=`; `POST /api/mock/new` (old body still works) | S3 and S7 start tests there, never on a running clock |
| S6 | `/api/history` (R26), `/api/stats`, `/api/skill/{topic}`, `UI.sittingCard`, `?q=M1-3` on the report | S3, S5, S9 (words filter), S1 (recent activity links) |
| S7 | `plan.today_summary(learner, tz)`, `plan.mirror(learner, fields)`, `PATCH /api/plan/{id}/tasks/{task}`, `GET /api/plan/ics` and the cal feed, `UI.taskRow` | S3 (plan card, Today list), F2 (metas), F4 (`PUT /api/me` mirror), S1 (goals card, Settings calendar), S4 (next in plan) |
| S8 | `compete.clock`, `twin_questions`, `finish_contest`, `state_extra`, `rate`, `challenge_streak`, `rank_snapshot`, `/api/contest/daily`, `UI.board`, `UI.level` | S4 and S5 (contest sittings, R28), F4 (`record` rating hook), S3 (challenge card), S1 (snapshot, Boards block) |
| S9 | `words.of_reason`, `words.minutes_today`, `words.today_summary`, `words.me_stats`, `/api/words/today`, `UI.gloss`, `UI.addWord`, `UI.addWordFromSelection` | F5 (feedback words), S7 (Words task), S3 (Words tile), S1 (Me stats), F2 (quick sheet tab), S4, S3, S6, S8 (gloss and add-from-selection hooks) |
| S10 | `/api/review/counts`, `/api/review/item`, `/api/review/family`, flag endpoints (`POST /api/session/{sid}/flag`, `POST /api/flags`) | S3 (Review card), S1 (Saved & in progress), F3 (`UI.review` pane, `UI.history`), S4 and S5 (Mark), S6 (flagged in results reads `flags`) |
| T-bank | `Item.spr_mistakes` in the bank | F4 (`record` names a grid-in mistake), S4 (verdict line) |

Hooks each page owner adds on its own pages (for others):

* **S4 session page**: `UI.gloss` on stem and rationale; `UI.addWordFromSelection`; Report (F6); Mark → flags (S10); History (F3 → S10); contest mode (R28); summary: next in today's plan (drill finish `plan`, S7), achievements toast (shell `new`), word chips in the verdict (`feedback.words`), "Review every answer" → report (S6), mistake rows → `/review/?open=trap:<id>` (S10), Share → sets (F6).
* **S5 test window**: `UI.learner()` instead of its own mint; Report (F6); flags (S10); notes (F4); contest chip, voids and finish hook (S8); starts from Today and Plan land on the lobby.
* **S6 report**: `UI.review` with Save, Mark, History and Report; the Flagged filter; `?q=`; redirect a words id to `/words/run/`; the percentile pill (F4); peers (F6 sets); "Back to your plan" from `satf.return` (S7); read-only notes, highlights, confidence, away time and answer changes (S5 `qstate`, F3 `UI.annotate`); gloss (S9).
* **S3 Today**: plan card and Today list (S7); Review card (S10); Words tile (S9); challenge card (S8); recent tests (S6 `UI.sittingCard`); Report on the day's questions (F6); gloss on the day's questions (S9).
* **S1 Me**: ranks (S8), Words stats (S9), Review counts (S10), plan tile and week dots (S7), question types met (F5 catalogue).
* **S8 contest page**: QOTD panel (S3 API), question review (F3 `UI.review`), Report (F6), gloss (S9).
* **S10 Review**: `UI.review`, `UI.history` (F3), Report (F6), Share (F6).
* **S7 Plan**: Words task (S9), Rechecks (pool `checks`), test tasks (S5 lobby), QOTD and challenge extras (S3, S8).

### 2.10 Registries (so parallel tasks never edit one another's files)

All use one helper, `deps.part(module, name)`, which returns the attribute or None when the
module is not there yet.

* **Routers.** `server/app.py` (after F0) lists every planned router module (`api_shell,
  api_legacy, api_me, api_notes, api_account, api_profile, api_practice, api_bank, api_tests,
  api_results, api_today, api_review, api_plan, api_compete, api_words, classes, reports,
  sets`) and includes each one that imports. No task edits `app.py` after F0.
* **Startup.** Each module may define `init()`; `app.py`'s startup calls those that exist
  (data migrations, warm caches, the weekly paper).
* **Shell parts.** `/api/shell` (F2) merges `shell_part(learner, tz) -> dict` from `plan`
  (plan), `compete` (challenge), `classes` (assignments), `reports` (report_replies),
  `achievements` (new.achievements), `words` (words due), and F4's own mistakes, saved,
  resume and today figures.
* **Achievements.** `achievements.py` (S1) reads `ACHIEVEMENTS` lists from `compete` and
  `words` when present (R25).
* **Hooks inside write paths.** `progress.record` calls `compete.rate(...)` for ranked contest
  answers; `drill.finish` and the test finish call `compete.finish_contest(row)` when
  `contest` is set and `classes.on_finish(row)` when `assignment` is set; `PUT /api/me`
  calls `plan.mirror(learner, changed)`. Each only when the module is present.

### 2.11 Working conventions

* **Worktrees.** One per task: `git worktree add ../satbank-<task> -b v2/<task> master`.
  Each runs its own server on its own port and database:
  `SATF_DB=$PWD/server/v2.db PYTHONPATH=. python3 -m uvicorn server.app:app --port 80NN`
  (F0 adds `SATF_DB`; ports in Part 4). The dev server on 8000 belongs to the main
  checkout and is never started or stopped by a task.
* **Seeing a page.** `shot.py a:v2rev<task><n> 1280|390 <out> http://localhost:80NN/<path>/`,
  then read the png. Learner codes start `a:v2rev`.
* **Checks.** New server checks go in `server/checks/<task>.py` (a `check(c)` function that
  `test_flow.py` runs after its own). An existing assert in `test_flow.py` that a task's
  change breaks is edited by that task in the smallest hunk. `PYTHONPATH=. python3
  server/test_flow.py` passes on every merge.
* **Docs.** README "The serving layer" has one subsection per task (F0 splits it); a task
  edits only its own. Each task keeps one State line under its entry in Part 4 of this file.
* **Foundation files after wave 1.** A wave-2 task that needs a change in a foundation file
  makes it as a separate small commit touching only that file, merges it first, and notes
  it in its State line.
* **Commits** follow the user's rule: one logical change, one commit with a descriptive
  message (never "wip"). There is no remote on this repo today, so "push" is skipped until
  one exists.
* **Done means:** the task's acceptance checks in Part 3 pass, test_flow passes, the task's
  pages are walked at 1280 and 390 with a new learner and a seeded one, and there are no
  console errors.

### 2.12 The foundation tasks

Each is a task in Part 4 with exclusive files. What each must build:

**F0 · Repo prep (serial, first).** Owns `server/app.py`, `server/deps.py` (then F4),
the new `server/api_*.py` files (each then passes to its owner), `server/challenge.py`
(then S8), `server/checks/`, `web/manifest.webmanifest`, `web/assets/icon-192.png`,
`icon-512.png`, `apple-touch-icon.png`, `web/assets/head.js` (then F2), `.gitignore`.

1. Split `app.py` into routers with **no behaviour change**: `deps.py` (learner_of, tz_of,
   `mine()`, NAME_OK, validators, `part()`); `api_tests.py` (`/api/session`, `/api/session/{sid}`,
   `/answer`, `/finish`, `/api/mocks`, `/api/mock/new`, `/api/mock/{num}`); `api_account.py`
   (`/api/session/{sid}/signup`, `/api/verify`); `api_results.py` (`/api/session/{sid}/results`,
   `/api/history`); `api_me.py` (`/api/me`, `/api/me/carry`); `api_practice.py` (`/api/map`,
   `/api/drill*`); `api_today.py` (`/api/today`, `/api/qotd`); `api_review.py`
   (`/api/mistakes`, `/api/saved`); `api_compete.py` (`/api/challenge*`); `api_legacy.py`
   (`/api/practice`, frozen for the archive). `app.py` keeps startup, health, middleware,
   GZip, the static mount and the registries of §2.10. Routers are included before the
   static mount, so a router may serve a page path (the `/challenge/`, `/mistakes/` and
   `/vocabulary/` redirects).
2. `daily.py` split: `challenge()` and `board()` move to `challenge.py`.
3. `SATF_DB` environment variable in `db.py` (default unchanged).
4. `server/checks/` and the runner at the end of `test_flow.py`.
5. Head sweep of all 14 pages: `head.js` (Shell §2.13 snippet) in `<head>`, the manifest link,
   `<meta name="theme-color" content="#FFFFFF">`, and `kit.js`, `charts.js` after `ui.js`
   (F0 creates both as empty stubs).
6. Manifest and icons (rendered from `mark.svg` at 192, 512 and 180).
7. README serving layer split into per-task subsections; `spec/rebuild.md` gets a first line
   pointing here; `.gitignore` adds `server/reports/` and `server/*.db` copies.

Acceptance: test_flow passes before and after; every page loads with no console error;
`curl -s localhost:80NN/manifest.webmanifest` is JSON; `grep -L head.js web/**/*.html` is
empty.

**F1 · Design system.** Owns `web/assets/ui.css`, `kit.js`, `charts.js`, `web/404.html`.
Builds every token and class of §2.3 and §2.4 for those files, the dark tokens of Shell
§2.13, the new `ui.css` header (§2.1), the print conventions, and a friendly 404 page
("That page does not exist." with links to Today and Practice; StaticFiles serves
`404.html`). Existing pages keep working (new classes only; existing ones restyled, not
renamed). Acceptance: a dev page `web/dev/kit.html` (owned by F1) shows every component in
light and dark, at 1280 and 390, with keyboard behaviour (Esc closes and returns focus;
arrow keys in seg, tabs, menus and listboxes); every chart renders its hidden table;
`/nope/` shows the 404 page.

**F2 · Shell.** Owns `web/assets/ui.js`, `head.js`, `quick.js`, `palette.js`, `qr.js`,
`server/api_shell.py`. Builds Shell spec §2 (except §2.10, which is F6): sidebar, rail,
phone bar and tabs, menu sheet, account menu, section mapping (R1), Today card, nav metas
from `/api/shell`, banners (retired, offline with backoff, storage blocked, first visit,
save nudge), toasts for achievements, replies and assignments, the quick sheet with its
three tabs (R29), the palette with parsing and aliases, `UI.keys` and the shortcuts sheet,
`UI.prefs` / `UI.prefRow`, theme apply (mirrored to `satf.look`), skip link, `/api/shell`
with the parts registry. Acceptance: Shell acceptance items on the sidebar, rail, phone
tabs and menu, `/api/shell` keys, account-menu keyboard, palette, quick sheet, offline
banner and theme.

**F3 · Question workspace and runner.** Owns `web/assets/question.js`, `runner.js`,
`runner.css`, `web/dev/workspace.html`. Builds R21 and R23 from QBank §2 (workspace,
strip, tools, navigator, overlays, calculator, SPR field, check flow in the three feedback
modes, review sheet), Tests §1 and §4.3–4.8 (runner shell, footer, navigator, Check your
work, timer, highlights and notes, calculator dock) and Report §1.13 / Review §8–9
(player, pane, history). Pure client components driven by props and callbacks; no page
logic. Acceptance: the dev page drives every mode with fixture questions (MC, grid-in,
figure, table) at 1280 and 390: select then Check, strike and Undo, highlight and
reload-restore through a fake store, navigator views and Esc, Check your work tiles adding
up, calculator dock and phone sheet, the review player's Hide answers persisting across
Next, and the key map of §2.8.

**F4 · Data layer.** Owns `server/db.py`, `progress.py`, `prefs.py`, `estimate.py`,
`satdates.py`, `scoring.py`, `deps.py`, `api_me.py`, `api_notes.py`. Builds §2.5 (schema,
migrations, backfills, carry, `LEARNER_TABLES`, `new_code`, `ensure_learner`), R8
(`record` computes repeat, repair, flagged, guess, norm, stem; clean answers; unsure,
relapse and check-in rules of R9; grid-in `spr_reasons` matching; `record_paper` with
qstate ms and flags), `progress.norm()` with its assert self-check, `progress.log_mistake`,
`progress.related()`, coach reasons, `keep_warm` and the `check` reason (R13 `days()`),
`estimate.py` (R16), `satdates.py` (R15, marked "verify against College Board"),
`scoring.accepted_forms` and `fraction_for`, `deps.access` (R19), retired codes in
`learner_of` (Shell), `PUT /api/me` validation of every prefs key, board, country, avatar,
name rules (R12), rw fields, exam date ≥ today, minutes without a plan, and the
`plan.mirror` call. Acceptance: `server/checks/f4.py` covers norm merging, repeat not moving
mastery, unsure opening with owed 1, a relapse, check-ins at 3/10/30, days() with a rest-day
plan (Shell's "streak equals 6" case), a module's minutes counted once, prefs 422 and merge,
access() on a live test item and today's challenge item, carry of every table.

**F5 · Drill engine and bank catalogue.** Owns `server/drill.py`, `practice.py`,
`blueprint.py`, `api_practice.py`, `api_bank.py` (drill and practice pass to S4 and
blueprint to S5 in wave 2). Builds §2.6 (every pool, filter, selection, resolver entry
point and the preview), R24's `cfg.inline`, R33, R34, measured levels (`drill.levels()`),
`why` on served questions, `blueprint.kinds()` (labels and reasons per template, whole-
question variety per template for Compete's twin slots), the Builder option to dedupe on
the whole question, the `cfg.only` fallback fix (Words), repairs that keep a `want`
regex, the feedback additions of §2.6, `GET /api/types`, `GET /api/types/{t}/example`
(seed range 900000+, never served in practice) and `POST /api/mistakes/log`. Acceptance:
`server/checks/f5.py` covers every pool and alias in §2.6, preview counts and 409 reasons,
templates-only and want-regex sets, exact items refused by access(), inline drills absent
from `/api/history`, and QBank's "templates", "tiers" and "levels" acceptance items.

**F6 · Reports and question sets.** Owns `server/reports.py`, `server/sets.py`,
`server/mail.py` (then S1), `web/assets/report.js`, `web/admin/reports/index.html`,
`web/s/index.html`, `tools/reports.py`. Builds R17 (Shell §2.10 and §10 in full, with the
category union and the word, paper and catalog contexts from Tests and Words) and R18(c)
(sets endpoints with the access rule, owner results with per-question right rates and the
most common named mistake, revoke, the `/s/` landing). Acceptance: Shell's report and admin
acceptance items; QBank's and Tests' share items read through sets (a second learner gets
identical stems; the public summary has no stems; results 403 for others; revoked → 410).

### 2.13 Acceptance checks changed by the resolutions

The acceptance lists in Part 3 are kept verbatim. These items are read as amended:

| section | the check says | read it as | why |
|---|---|---|---|
| 3.1 Shell | the sidebar lists "Search, Quick, Today, Practice, Mistakes, Tests, Plan, Results, Challenge, …" | "Search, Quick, Today, Practice, Review, Words, Tests, Plan, Results, Compete, the Today card, Help & FAQ, Send feedback, the user card" (Class only when in one); `/mistakes/` and `/challenge/` land on Review and Compete, which are then current | R1, R2, R3 |
| 3.1 Shell | the phone menu sheet lists "Mistakes, Challenge, …" | "Review, Words, Compete, Profile, Settings, Sign in, Pair a device, Join or teach a class, Help & FAQ, Send feedback, Leave this device" | R1 |
| 3.1 Shell | "the sidebar Mistakes item and the phone top-bar chip both show 14" | the sidebar Review item and the phone top-bar chip | R1 |
| 3.1 Shell | `PUT /api/me {prefs:{set_length:22, difficulty:'hard', format:'grid'}}` | `{prefs:{set_length:22, tiers:['hard'], formats:['spr']}}` | R11 |
| 3.1 Shell | "GET /api/cal/{token}.ics … matches UI.ics() for the same learner" | "… matches GET /api/plan/ics for the same learner" | R18(b) |
| 3.1 Shell | practice rank: "after the second sets board 'hidden', the first's line reads #1 of 1" | reads "#1 of 2", and the second is listed as "Anonymous" at #2 and still sees their own rank | R12 |
| 3.1 Shell | "with board 'hidden', GET /api/challenge/board omits the learner from entries and players" | the contest board keeps the row at its rank named "Anonymous"; `players` is unchanged | R12 |
| 3.2 Today | `POST /api/plan/mark {day, task, state:'skipped'}` | `PATCH /api/plan/{id}/tasks/{task_id} {day, status:'skipped'}`; `/api/today.plan` shows it; `{status:'todo'}` removes it | R14 |
| 3.2 Today | `GET /api/tests/recent` (fields and module split) | the same fields in `GET /api/history?kind=tests&all=1` | R26 |
| 3.2 Today | "PUT /api/me {exam_date, minutes, days} returns 200 with plan_started = today" | returns 200; a plan's start day comes from `POST /api/plan` (`plans.start`) | R14, R15 |
| 3.3 Practice | a report row joined to `report_files`; "a 6 MB file returns 413" | `reports.files` lists 1 file under `server/reports/{id}/`; an 11 MB file returns 413 | R17 |
| 3.3 Practice | `PUT /api/me {prefs:{timing:'pace', feedback:'retry'}}` | `{prefs:{clock:'pace', feedback:'retry'}}` | R11 |
| 3.3 Practice | shares: `POST /api/drill {share: code}`, `GET /api/share/{code}`, `/api/share/{code}/results` | `POST /api/drill {pool:'set', ids:code}`, `GET /api/sets/{code}`, `GET /api/sets/{code}/results`; revoke → 410 | R18(c) |
| 3.4 Tests | `POST /api/session/{finished}/share`, `GET /api/shared/{code}` | `POST /api/sets {session}`, `GET /api/sets/{code}` | R18(c) |
| 3.4 Tests | a report row `WHERE id='…'`; "the 21st report in a day gets 429" | integer ids; the 11th report within an hour gets 429 | R17 |
| 3.4 Tests | "Save these as my defaults updates GET /api/me profile.test_prefs" | updates the `test_*` keys of `profile.prefs` | R11 |
| 3.5 Report | `POST /api/me/share {on:true}` returns a token for `/results/?share=` | `POST /api/share` (the progress link, S1) returns a token that `/results/?share=` and `/share/?t=` both accept | R18(a) |
| 3.5 Report | `POST /api/session/{sid}/time {times}` | answers carry `ms`, or `POST /api/session/{sid}/state {question_id, ms}`; the attempts then carry ms | R7 |
| 3.6 Plan | `/cal/<token>.ics`; `POST /links {view:true}` | `/api/cal/<token>.ics`; `POST /api/share` (progress link), then `GET /api/plan/shared/<token>` | R18 |
| 3.7 Compete | "PUT /api/me {public:false}" | `PUT /api/me {board:'hidden'}` | R12 |
| 3.7 Compete | "badges includes first-contest with an earned date" | `/api/me/achievements` has the Challenge rule at tier I with an earned date | R25 |
| 3.7 Compete | "the phone tab bar shows 6 labelled tabs"; Compete link `aria-current` in the tab bar | 5 tabs; the sidebar Compete item (desktop) and the menu-sheet row (phone) carry `aria-current` | R1 |
| 3.8 Words | "GET /api/me profile.words_goal is 5" | `profile.prefs.words_goal` is 5 | R11 |
| 3.8 Words | "the bar '+ word' button exists on /, /practice/ and /words/" | Q opens the quick sheet with an "Add a word" tab on those pages; the quick sheet is absent on `/practice/session/`, `/words/run/` and `/test/` | R29 |
| 3.8 Words | "the study bar is visible above the 6-column tab bar"; "the 21st report of the day returns 429" | above the 5-column tab bar; the 11th report within an hour returns 429 | R1, R17 |
| 3.9 Review | `POST /api/shares …`, `{list:'share', ids:id}` | `POST /api/sets …`; `list:'share'` stays valid as an alias of `pool:'set'` | R18(c), R10 |

---

## 3. Section specs

One section per reviewed spec, verbatim. Each opens with the tasks that build it and the resolutions that change it.

## 3.1 App shell, navigation, profile and account

> **Spec title:** App shell, navigation, profile and account  
> **Built by:** F2 (§2 shell), F6 (§2.10 report, §10 admin), S1 (§1, §3–§6, §8, §9), S2 (§7 classes), F1 (§2.13 tokens, §11 CSS)  
> **Read with resolutions:** R1, R2, R3, R4, R11, R12, R13, R14, R15, R16, R17, R18, R19, R22, R25, R29, R31 (§2.2). Where this spec disagrees with them, they win.

### 3.1.1 What they have

- **Left sidebar**: About 220px wide. A toggle beside the logo collapses it to a ~60px icon rail. Stacked black 'TOP TIER PREP' wordmark at the top.
- **Primary nav (10 items, in order)**: Dashboard, Practice, Study Plan, Results, Question Bank, Contests & Challenges, Contests Rankings, Leaderboards, Vocabulary, Subscription. Each is its own route. No counts or badges on any item.
- **Active nav state**: Gray-blue pill background and a bold label.
- **Upgrade card**: Blue 'Upgrade to Pro · Unlimited tests & QBank' card with a TRIAL badge at the bottom of the sidebar, linking to /subscription.
- **User card**: Avatar, name, role ('User') and a chevron at the bottom of the sidebar. Plan badges in the bundle also include 'Trialing' and 'Teacher Seat'.
- **User popover**: Avatar, name and email, then My Profile, Send feedback, Sign out (red). Bug: it ignores Escape and needs an outside click to close.
- **Floating quick-add button**: Blue circle at the bottom right of every page: 'Add your own word (drag to move)'. Draggable; it adds to the vocab 'Custom Added Words' collection, so it is a capture tool for the student's own study list. It covers the Next button in QBank sessions.
- **Auth**: /auth ('Welcome back'). Google sign-in only; unauthenticated routes redirect there, so nothing works before signing in. Email/password can be added later from the profile.
- **Report / feedback modal**

  One modal for exams, questions and vocab.
  - A read-only 'Sent with your report' box (item type, title, UUID).
  - Title prefilled, with a 0/200 counter.
  - Category select: General feedback / Bug or something broken / Wrong answer key / Typo or content error / Feature request / Other.
  - Details, 0/5000.
  - Up to 10 image attachments, 50MB each (JPEG/PNG/WebP/GIF).
  - A full-width 'Send feedback' button.
  The student never sees what happens to a report.

- **Send feedback (general)**: Opened from the user popover: the same modal without item context. The bundle also has a /feedback route.
- **Toasts (bundle)**: Generic toasts, e.g. 'Task skipped / added / updated / removed', 'Switched to this plan', 'Share link copied to clipboard', and an error toast 'Could not start task. Please try again.'
- **Profile layout**: /profile: a left third and a right two-thirds.
- **Profile identity card**: Tinted card: avatar with a camera upload badge, name, email, a 'Not set yet' pill, and a 2x2 grid of stat tiles (icon chip, label, big value): Streak N Days, Tests N Taken, Solved N Qs, Vocab N Words. With data: Streak 0 Days while the QOTD pill said '1 day' (two streaks disagree), Tests 1 Taken, Solved 57 Qs, Vocab 2 Words.
- **Performance Snapshot (ranks)**: Global Rank (e.g. 128) and Country Rank (e.g. 43), both shown with no contests played, so the ranking basis is unstated.
- **Subscription & Credits card**: FREE badge; usage meters (label, n/max, bar) for Practice Exam Attempts, TopTierPrep Bank, New Words Today and AI Study Plan Generations; 'Upgrade for unlimited prep' with an Upgrade button.
- **Saved Content**: Counts for Saved Words, Redo Questions and Saved Questions (0 / 0 / 1 with data).
- **Account block**: Sign out; Name and Email, editable inline (bundle); Password: 'Your account uses Google Sign-In' + Set Password, or Change Password (at least 8 characters, with a confirm field); 'Google account connected'.
- **Avatar management (bundle)**: Upload, replace or remove a profile photo. The remove confirm reads 'Remove profile photo? Your initials will be shown instead…'.
- **Study Goals**: Target score (a bar; 'Not set' even after the wizard set 1400, because wizard, dashboard and profile are not synced); exam date with an 'N days remaining' progress bar; Daily goal (2 Hours); Weekly goal (12 Hours); Preferred time (Evening), which has no effect anywhere.
- **Target score modal (dashboard)**: A pencil opens 'Set Target Score': 'SAT scores range from 400 to 1600. Your current score is 1460.' (the wrong number), a big number input with placeholder 1500, a 400–1600 bar, and [Cancel] / [Save Score], disabled until you type.
- **Exam date select**: The dashboard pill is a select of official dates, past ones included: Aug 22 2026, Sep 12, Oct 3, Nov 7, Dec 5, Mar 6 2027, May 1, Jun 5. The wizard uses a free calendar instead.
- **Subject performance**: A per-subject performance block, empty on a new account.
- **Score trend**: A line chart with 'Latest: N'.
- **Achievements**: Four hard-coded badge tiles (7-Day Streak, 1000 Solved, Consistency, Top Rank) with no progress and no earned state. 'View All' has no click handler.
- **Learning Preferences**: On the profile itself: Practice Mode select (Timed / Untimed), Difficulty Level select (Adaptive / Fixed), and toggles for AI Explanations, Show Desmos Calculator and Include Vocab Review.
- **Recent Activity**: Rows like 'Custom Set · 2 Modules · 8h ago ›'. Empty on a new account.
- **Subscription page header**: 'Subscription & Billing' with a back link.
- **Current plan status**: 'Free Tier' with an Active badge, an 'Upgrade to Pro' button, and copy on what upgrading adds (full-length tests, daily TTP questions, AI plans).
- **Usage meters**: Practice Exam Attempts 0/1, TopTierPrep Bank 0/0 (unset on paid tiers, a bug), New Words Today 0/5, AI Study Plan Generations 0/1.
- **Plan cards**

  A Monthly | 3 months ('Save 15%') toggle.
  - Pro: $13.99, or $35.99 for 3 months, with a 7-day trial.
  - Elite: $23.99, or $59.99 for 3 months, marked 'Most Popular' with a blue border and tint.
  Feature lists, CTAs 'Start 7-Day Free Trial' / 'Subscribe to Elite', and a trust strip.

- **FAQ accordion**

  Six questions, first one open:
  1. The free trial.
  2. Cancelling or switching.
  3. Pro vs Elite.
  4. Whether history is lost on cancel.
  5. Moving from monthly to 3-month.
  6. Whether payment is safe.
  Billing only.

- **Payment history**: Table: Date, ID, Payment method, Amount, Status, Receipt, Invoice. 'Amounts shown in USD'.
- **Pricing route (bundle)**: /pricing.
- **Classes (hidden route)**: /my-classes: 'My Classes · Pick a class to see its homework.' Empty: 'You're not in any class yet. Your teacher will add you to one.' Not in the sidebar.
- **Homework runner (bundle)**: An assignment runs as 'a full practice test with timed modules and breaks' or 'a question-bank session — check answers as you go'. It has a time limit, 'Attach file', 'Your answers are saved as you go. Submit when you're done.' and [Finish Homework].
- **Teacher dashboard (bundle)**: /teacher: create a class, add students, assign work, set due dates.
- **Public single-question route (bundle)**: /question/:key, probably a public page for one question.
- **Shared session links (bundle)**: /question-bank/shared/:shareId with a 'Start Practice' landing page.
- **Canvas**: A light gray app canvas behind white cards with an 18px radius. Results uses a darker gray canvas.

### 3.1.2 What we have now

Status is have / partial / missing / worse, against theirs.

- **Primary nav**: *worse.* The top bar has 5 links (Today, Practice, Tests, Plan, Results). Mistakes, Challenge, Me and the diagnostic are in no nav; they are reached only through links inside pages. SECTION maps challenge to Today and mistakes to Practice, so those pages highlight the wrong item. No counts or badges.
- **Collapsible sidebar / rail**: *missing.* A fixed top bar with no room for more sections. No collapse, no tooltips.
- **Brand**: *partial.* The 26px mark links home. No wordmark.
- **Active state**: *have.* A 2px orange underline on desktop; a 2px bar above the icon on the phone tabs.
- **Phone nav**: *partial.* 5 bottom tabs (Today, Practice, Tests, Plan, Results). No way to reach Mistakes, Challenge or Me from the chrome, and no More.
- **Upgrade card slot**: *have.* Nothing to sell, correctly, but the slot shows nothing useful either.
- **Streak in the bar**: *have.* A flame and count linking to /results/, hidden until the first answer. Ours only. But planned rest days break it, so a Mon–Fri plan resets it every weekend.
- **User card + popover**: *worse.* A 34px avatar (an initial, or the mark) links straight to /me/. No name, no email, no menu, no feedback, no sign out.
- **Floating quick action**: *missing.* No action works from every page. There is no way to add anything of your own (their add-a-word capture).
- **Sign-in / account**: *worse.* An anonymous 'a:' + 24-char code in localStorage. After the browser is cleared, it can only be recovered from a hand-copied code. The diagnostic's email sign-up (users table) links only to that one sitting, never to the learner. web/test/test.js mints its own code with Math.random and a timestamp, so a first visit that starts at /test/ gets a guessable identity.
- **Sign-in page**: *missing.* There is no page for 'I have progress on another device'. The only way in is the 'From another device' field on /me/.
- **Sign out**: *missing.* Nothing. A shared computer cannot be left.
- **Feedback / report**: *missing.* No report button on any question, test or page; no general feedback; no endpoint; no admin view.
- **Toasts / banners**: *missing.* Pages flip button text ('Copied', 'Saved' paragraphs). No shared toast or banner.
- **Storage-blocked warning**: *have.* A red-dot paragraph prepended to main when localStorage and sessionStorage both refuse.
- **Offline / server down**: *worse.* paintMe swallows the error and every page quietly shows nothing.
- **Profile identity**: *worse.* The avatar initial and a Name field with Save. No email, goal pills, member-since or stats.
- **Profile stats**: *missing.* None on /me/. Results shows answered / right% / streak.
- **Study time**: *worse.* progress.days sums attempts.ms, but sections, modules and the diagnostic file their answers through record_paper with ms=None. A 70-minute section adds 0 minutes to Today, the week and every study-time figure.
- **Ranks / performance snapshot**: *missing.* Only today's challenge rank, on Challenge and Today. No overall or cohort rank.
- **Credits meters**: *have.* None, correctly: nothing is metered.
- **Saved content**: *partial.* Saved questions and open mistakes are on /mistakes/. Me shows no counts and no Resume.
- **Account block**: *partial.* Name, the device code with Copy, and a 'From another device' field that carries this device's progress into the typed code (/api/me/carry) with no confirmation. The code is shown unmasked.
- **Study goals on the profile**: *partial.* Target, exam date, minutes, days and focus are set in /plan/ and stored once in learners (so no sync bug like theirs). Me shows none of it and can't edit it. No preferred time. The weekly goal is never shown.
- **Subject performance**: *partial.* Results has 19 skill tiles with mastery bars. Nothing on Me.
- **Score trend**: *partial.* Results has the band over time. Nothing on Me.
- **Achievements**: *missing.* None.
- **Learning preferences**: *missing.* Practice always opens at 10 questions, all difficulties, untimed. Nothing is stored per learner.
- **Recent activity**: *partial.* Results lists finished sittings. There is no feed of closed mistakes, question-of-the-day answers, challenge ranks or badges.
- **Classes / homework**: *missing.* Nothing for teachers or classes.
- **FAQ / help**: *missing.* No help page. The explanations exist only in the README.
- **Subscription / payments**: *have.* Deliberately none: free.
- **Keyboard / search**: *missing.* No global shortcuts, no search, no skip link.
- **Theme / text size**: *missing.* Light only. web/test/index.html hard-codes 41 colours and me/report hard-code one each, so a dark theme needs tokenising first.
- **Install as app**: *missing.* No web manifest or touch icon.
- **Design rules in code**: *worse.* The ui.css header still codifies 'nothing narrates', 'the pill is the one primary action', 'nothing has a border': the rules that caused the degradation.

### 3.1.3 Design

##### Review changes

What this revision changes in the proposal, and why:

1. **Plan is back in the phone tabs.** The proposal's tabs (Today, Practice, Tests, Results, More) dropped Plan. Plan is one of our five tabs today and their priority section, so that was a regression. The tabs stay **Today · Practice · Tests · Plan · Results**. "More" becomes the avatar button in the phone top bar, which opens the same sheet. The phone bar also gets Search.
2. **Every nav item that can carry a count now does.** The proposal left Today, Practice and Results silent. Now:
   * Today shows "12/28" (today's questions against the plan) or "Done".
   * Results shows a "New" dot when a finished sitting hasn't been opened.
   * Tests shows "Test day" on the plan's test day.
3. **Learning preferences are back on the profile**, as on theirs. An inline card holds the five most-used defaults, saved instantly, plus "All settings". The proposal hid them all on /me/settings/.
4. **Goals are editable from the profile.** Target and exam date open quick-edit popovers. They write the same `learners` fields Plan and Today read, so the three can never disagree (theirs show 1400 in the wizard and 0 on the dashboard and profile). The exam-date picker lists only upcoming official dates (theirs lists past ones), plus any other date. Daily time and focus deep-link into the Plan wizard's step.
5. **Their global and country ranks get real equivalents.** A **practice rank** over the last 7 days (right answers), in three scopes:
   * among everyone;
   * among students **sitting the same exam date** (our "country rank": the cohort that matters);
   * within each class.

   The proposal had only the daily challenge. Board visibility applies.
6. **Skills are expanded on desktop.** All 19 show under their 4 domains. On the phone the domains collapse, and each names its weakest skill. The proposal collapsed them everywhere.
7. **The profile's Account card has Sign out**, as theirs does, not only the menu.
8. **The report modal is at least as capable as theirs.**
   * Up to 10 images, GIF included.
   * Each image is downscaled in the browser, so a 50 MB phone photo still goes through.
   * A prefilled Title with a 0/200 counter.
   * A **Your reports** list with status and our reply.

   The proposal allowed 3 × 5 MB and no title.
9. **Reporting mid-test no longer leaks the key.** In a live module or challenge, the proposal's "Sent with this" box printed "Your answer: B, marked wrong" and offered "Answer key is wrong". While a sitting is live, the box now shows only the answer given, and the key categories and dispute are hidden. They return in the report review.
10. **Disputes are bounded and actually resolved.**
    * At most 5 open disputes per student.
    * A dispute never changes a test or challenge score.
    * A disputed answer still counts for study time and streak. It is excluded only from accuracy, mastery and mistakes (the proposal dropped it from `days()` too).
    * A minimal **admin page** behind an env token lets someone confirm or overturn a dispute and reply, and the student sees the reply. The proposal left this open, so disputes could never close.
11. **Email sign-in is phishing-safe.** The email carries a 6-digit code and a link. Only the device that asked can finish with the code. A link opened elsewhere signs *that* browser in, never the requester. In the proposal, clicking the link completed a claim for whichever device asked, so anyone who typed your email got your progress the moment you tapped an unexpected email.
12. **Pairing needs approval on the device showing the code.** Learner codes are minted by the client, so a per-learner guess limit stops nothing, and a bare 6-digit code could be brute-forced. Now B asks, A taps Allow, and only then does B see a name. A per-IP limit is added.
13. **A real sign-in page, `/signin/`** (their `/auth`), with three tabs: Email code · Pairing code · Device code. `/pair/` is its short link. The users table takes `''` for first and last, so it needs no rebuild.
14. **Study time counts tests.** Found in the code: sections, modules and the diagnostic file answers with `ms=None`, so a 70-minute section adds 0 minutes to Today, the heatmap and every study-time stat. `days()` now adds each sitting's elapsed time.
15. **One streak everywhere, and planned rest days keep it.** Theirs shows 0 on the profile and 1 on the question of the day. Ours is one server value. A student following a Mon–Fri plan no longer loses the streak every weekend.
16. **Their floating button gets its capture half.** Theirs adds *your own* word from any page. Our quick sheet gets a second tab, **Log a mistake**. A question missed at school or in Bluebook becomes an open mistake on the matching question type, with its named misconception, and is drilled with fresh numbers.
17. **The palette searches the bank.** All 386 question types by skill label, and every named misconception. Enter practises exactly that type (new Drill option `templates`, served through the existing queue path).
18. **Classes and homework are now in the spec** (their hidden `/my-classes` and `/teacher`; the proposal skipped them).
    * Students join with a code.
    * Assignments can be a set, a module or a section. Questions are either fresh for each student, so answers can't be copied, or the same for everyone.
    * Students can attach their working, as theirs allows.
    * The teacher sees the roster and the named mistakes across the class, with "Assign a repair to these 9". Only our bank can produce that.
19. **Theme defaults to Light.** The brand is white paper, so Dark and System are opt-in. Dark ships with this section, which tokenises the 43 hard-coded colours (41 in the test window). That resolves the open question.
20. **Delete everything keeps challenge rows, anonymised**, so other students' past ranks don't shift. That resolves the open question.
21. **The calendar export works.** It uses RRULEs with reminders (VALARM at the preferred time), and a subscribable feed follows plan changes. No plan logic is copied into Python.
22. Smaller fixes:
    * Quick sessions finish on close with `fetch(…, {keepalive: true})`, because sendBeacon can't send `X-Learner`. A quick session with no answers is deleted, and none shows as Resume.
    * Skill rows and the palette use the student's set length, not a fixed 10.
    * "Question types met" counts answered types, not merely shown ones.
    * Week dots use the Plan section's "day done" rule.
    * No emoji in the copy: the flame is our icon.
    * The profile's left column is no longer sticky (it is taller than a laptop screen).
    * The site is installable (web manifest).
    * `?feedback` opens feedback on any page.
    * A first-visit banner: "Have progress on another device? Sign in".
    * The helper-text rule is flipped: every control that changes how practice behaves gets a one-line helper.
    * The `ui.css` header, which still states "nothing narrates / one pill / no borders", is rewritten to the rules below.

---

##### Rules for this section

* Every section is one click away on desktop and at most two taps away on a phone.
* A nav item shows what is waiting there whenever something is: a count, "New", "Resume", "Test day", or today's progress.
* Nothing is sold. The slots they use for selling show the student's own day.
* Settings save the moment they change and say "Saved". A failed save reverts and says so.
* Every control that changes how practice behaves has a one-line helper under it. Labels, legends, units and counts are always shown.
* Orange (#F18508) is the only accent. Destructive actions use graphite and a confirm dialog, not red.
* A 1px `--line` border goes wherever it separates. Cards are `--tile` on paper.
* **One source per fact.** Streak, target, exam date, study time and the open-mistake count each come from one server function, and read the same on every screen.

---

##### 1. Identity and account

Keep what already beats theirs: **no sign-up wall**. A new visitor practises on the first click under an anonymous code. Add what is missing: a safe, portable identity with no password and no copying.

| state | what the student has | how they got it |
|---|---|---|
| **Anonymous** | a device code (`a:` + 24 base-36 chars from `crypto.getRandomValues`) in `localStorage` `satf.learner`, with a `sessionStorage` fallback | first visit to any page. `/test/` must use `UI.learner()` |
| **Saved** | the same code, plus a verified email bound to it (`users.learner`) | Save progress → the 6-digit code from the email, or the email's link |
| **Signed in elsewhere** | another device adopts the saved code | email code, pairing code (approved on the first device), or the device code. This device's own answers are carried in first (`progress.carry`) |
| **Teacher** | a saved account that owns a class (not a separate account type) | Teach a class (§7) |

**Save to an email (no password).**
1. The student enters an email: in Settings › Account, on `/signin/`, in the save nudge, or from the menu callout. This sends POST `/api/account/link {email}`.
2. The email's subject is "Your SAT Freshman code: 482 913". It holds the code and a link to `/signin/?t=…`. Both work once and expire in 30 minutes.
3. **On the device that asked**, six code boxes wait: "Enter the code we sent to dana@gmail.com". Typing the code sends POST `/api/account/verify {code}` and finishes there.
4. **The link** opens `/signin/?t=` in whatever browser the mail app uses:
   * If that browser holds the requesting code, it finishes at once. The waiting tab notices through a `storage` event or its 3 s poll of `/api/account`.
   * In any other browser it reads: "You asked on another device. Type **482 913** there, or **sign in on this device instead**." The second option finishes for *this* browser.
   * A link opened elsewhere never finishes for the requester.
5. **Finishing** does one of three things:
   * The email has no code yet: it is bound to this code. Toast "Saved to dana@gmail.com".
   * It already belongs to this code: verified again.
   * It belongs to another code A: `progress.carry(this, A)`, the page adopts A (`UI.useLearner`) and reloads. Toast "Signed in as Dana · 24 answers moved here".

**Pairing (no email).**
1. Device A: "Show a pairing code". It shows 6 digits (482 913) and a QR code of `/pair/?c=482913`, valid 10 minutes and single use, then "Waiting for your other device…".
2. Device B: types or scans the code → "Approve on your other device", showing its own label ("Chrome on iPhone").
3. Device A: a prompt, "A device wants your progress: **Chrome on iPhone** · 24 answers there", with [Allow] [Deny].
4. After Allow, B shows the preview "Dana · 1,284 answers · since Sep 2", with "This device: 24 answers. They'll be added to Dana's." [Use Dana's progress here] → carry → adopt → reload. Toast "Signed in as Dana".
   * Deny → B reads "Your other device said no."

**Device code**: an advanced fallback, masked (`a:••••••••••••hist`) with Show and Copy. Typing another code opens a confirm dialog that shows both sides: "This device: 24 answers. That code: 1,284 answers. They'll be combined under that code."

**The diagnostic sign-up is the same account.** Signing up after a diagnostic sets `users.learner` to that sitting's learner when it is empty. Its confirmation email carries the same code and link, and counts as saving.

**Sign out of this device** clears `satf.learner` and the `satf.*` caches, keeping `satf.look` and `satf.rail`. It mints a fresh code, goes to `/` and shows the toast "Signed out". An unsaved device gets the warning dialog (§4.4) first.

**Sign out everywhere else** (saved accounts only):
1. The server moves everything to a new code and retires the old one.
2. This device adopts the new code.
3. Any other device still holding the old one gets `{retired: true}` from `/api/shell` and a 401 on writes.

**Privacy for minors**:
* No photo upload: the avatar is an initial or one of our 19 topic glyphs.
* No location is collected.
* Board visibility: with my name / anonymously / don't list me.
* A class sees only the name the student gives that class.
* A parent or tutor sees only what a share link shows.

---

##### 2. The shell (`UI.shell()` in `web/assets/ui.js`)

Every page keeps `<header id="bar">`, `<main class="page" id="main">` and `<nav id="tabs">`.
* The shell renders the sidebar (or the phone top bar) into `#bar` and the phone tabs into `#tabs`, and adds `body.has-side` / `body.has-rail`.
* `.page` keeps `max-width: 1120px` inside the width that is left.
* **The practice session (`/practice/session/`) and the test window (`/test/`) render no shell**: no sidebar, no quick sheet, nothing floating, so nothing can cover Next.
* The first focusable element is a **skip link**, "Skip to content". It is visible on focus and moves focus to `#main`.
* The `ui.css` header comment is rewritten to this section's rules.

###### 2.1 Breakpoints

| width | chrome |
|---|---|
| ≥ 1100px | **Sidebar**, 248px, expanded by default. The toggle or `[` collapses it to the 68px rail; the state is kept in `localStorage` `satf.rail` |
| 760–1099px | **Rail**, 68px, by default. The toggle opens the full sidebar as an overlay over a scrim (`rgba(40,38,34,.32)`); Esc, a scrim click or navigating closes it |
| < 760px | **Phone**: a 56px top bar and 5 bottom tabs. The avatar opens the menu sheet |

###### 2.2 Desktop sidebar (expanded, 248px)

Fixed, full height, `--tile` background, with a 1px `--line` right edge. Top to bottom:

1. **Brand row** (64px): the 26px mark and the wordmark "SAT FRESHMAN" (Archivo 800, 13px, letter-spacing .06em, two lines like the lockup), linking to `/`. At the right, the collapse button (`aria-label="Collapse sidebar"`, tooltip "Collapse · [").
2. **Search** (40px, paper, radius 10): a magnifier, "Search", and the `kbd` "⌘K" ("Ctrl K" off Mac). Opens the palette (§2.8).
3. **Quick** (40px, `--wash`, ink text): a bolt, "Quick", and the `kbd` "Q". Opens the quick sheet (§2.7). This is our version of their floating button: it reaches every page but sits in the chrome and never floats over content.
4. **Group "STUDY"** (label in DM Mono 10.5px uppercase, `--soft`):

   | item | route | meta on the right |
   |---|---|---|
   | **Today** | `/` | today's questions against the plan in DM Mono ("12/28"). A check and "Done" when the Plan section's day rule says the day is done. Without a plan, the count alone ("12"); at 0, nothing |
   | **Practice** | `/practice/` | none |
   | **Mistakes** | `/mistakes/` | an orange dot and the open count ("● 14"); hidden at 0 |
   | **Tests** | `/tests/` | a "Resume" chip (`--wash-2`, ink 600 11.5px) while an unfinished test has time left; otherwise "Test day" on the plan's untaken test day |
   | **Plan** | `/plan/` | today's kind in DM Mono 12px `--soft`: "28 q" / "Test day" / "Rest" / "Exam day". "Set up" when there is no plan |
   | **Class** | `/class/` | only when the student is in or teaches a class. Students: "2 due" (orange dot when one is due within 24 h). Teachers: none |

5. **Group "PROGRESS"**:

   | item | route | meta on the right |
   |---|---|---|
   | **Results** | `/results/` | an orange dot and "New" when a sitting has finished since the student last opened Results or its report (`localStorage` `satf.seen.report`, the newest finished id seen) |
   | **Challenge** | `/challenge/` | "New" while today's is unplayed, "Resume" once started, "#4" in DM Mono once finished |

6. Flexible space. On short viewports, items 4–5 scroll inside the sidebar and items 7–9 stay pinned.
7. **Today card**, in the slot where they sell upgrades. A paper card, radius 12, padding 14:
   * Header row: "TODAY" (k label), and on the right the flame icon and the streak ("6"). The flame is filled orange while the streak is above 0.
   * Bar 1: "18 of 45 min" (DM Mono), a 4px bar (`--amber` on `--mat`).
   * Bar 2: "12 of 28 questions".
   * "Due: Period 3 · Circles · Fri", when an assignment is due within 3 days (links to it).
   * Footer: "Exam in 45 days · Nov 7" (DM Mono 12 `--soft`).
   * Without a plan: "18 min · 12 questions today" and the link "Set a daily goal" (→ `/plan/`).
   * Brand-new student: "Nothing yet today" and "Set a daily goal".
   * The card body goes to `/plan/`; the flame goes to `/me/#activity`.
8. **Help & FAQ** (`/help/`) and **Send feedback** (§2.10, general mode): quiet 36px rows with icons.
9. **User card** (56px, a button with `aria-haspopup="menu"`). Opens the account menu (§2.6).
   * Avatar 34 (an initial, a glyph, or the mark).
   * Name (600 14px). The board handle "Student 4F2A" when unnamed.
   * A second line in DM Mono 12px: the masked email "d•••@gmail.com" when saved, or an orange dot and "Not saved yet".
   * A chevron.

**Nav item anatomy**: a 40px row, radius 10, 10px side padding, a 20px icon, the label in Archivo 500 14.5px `--ink`, and a fixed-width meta slot on the right, so badges never shift the labels.
* Hover: `--tile-2`.
* Active (`aria-current="page"`): `--wash` background, label 600, and a 3px orange bar on the inside left edge.
* Focus: the global 2px ink outline.

**Section mapping** for the active state:

| page | active item |
|---|---|
| session | Practice |
| mistakes | Mistakes |
| report | Results |
| challenge | Challenge |
| diagnostic | Tests |
| class | Class |
| me, settings, signin | the user card (it takes the active background) |
| help | Help & FAQ |

###### 2.3 Rail (68px)

The same order, icons only, centred in 44px targets.

Badges become:
* **Mistakes**: a count bubble (orange fill, ink-deep 10px mono, top-right of the icon).
* **Challenge "New"**, **Tests "Resume"**, **Results "New"** and **Class due**: a 7px orange dot.
* **Today**: a 2px progress ring around the icon.

Tooltips (`role="tooltip"`, on hover and on focus, 8px to the right) carry the name, the meta and the shortcut, e.g. "Mistakes · 14 open · G M".

The rest of the sidebar:
* **The Today card** becomes a 36px ring (today's minutes against the goal, as an orange arc) with the streak digit inside. Its tooltip carries the full card text.
* **Search, Quick, Help and Feedback** become icons with tooltips.
* **The avatar** sits at the bottom.
* **The expand toggle** sits under the mark.

###### 2.4 Phone (< 760px)

**Top bar** (56px + safe area, paper, with a 1px `--line` bottom border once scrolled 4px). From the left:
* the mark (→ `/`);
* a Search icon button (`aria-label="Search"`, opens the palette full-screen);
* a spacer;
* the Mistakes chip "● 14" (→ `/mistakes/`, hidden at 0, active style on /mistakes/);
* the streak (flame + "6", → `/me/#activity`);
* the Quick button (bolt, 40px target, `aria-label="Quick question or log a mistake"`);
* the avatar (40px target, `aria-label="Menu"`). It carries a 7px orange dot while today's challenge is unplayed or an assignment is due, and opens the **menu sheet**.

Everything fits 390px: 16 + 40 + 40 + flex + 64 + 48 + 40 + 40 + 16, with 8px gaps.

**Bottom tabs** (64px + safe area, 5 equal columns, 22px icon, 10.5px label): **Today, Practice, Tests, Plan, Results**, exactly today's five. Today and Tests carry the same meta as the sidebar, as a dot. `aria-current` follows the section mapping.

**Menu sheet**: a bottom sheet with a drag handle, max-height 85vh, 52px rows, grouped:
1. The Today card (§2.2.7, full width).
2. Mistakes (● 14) · Challenge (New / #4) · Class (2 due, if any).
3. A divider, then the account header: avatar, name, and the email or "Not saved yet". Tapping it goes to Profile.
4. Save your progress (when unsaved) · Settings · Sign in (when unsaved) · Pair a device · Join or teach a class · Help & FAQ · Send feedback · Sign out (or Leave this device).

That puts Mistakes, Challenge, Class, Profile, Settings and Help each at most two taps away.

No horizontal page scroll at 390px. The fixed tabs never cover content: `.page` has `padding-bottom: calc(96px + env(safe-area-inset-bottom))`.

###### 2.5 Pages without the shell

`/practice/session/` and `/test/` keep their own top strips. They still load `ui.js`, for:
* `UI.learner()` and `UI.report`;
* `UI.toast` and the theme head snippet;
* `UI.keys`, so their own keys appear in the `?` sheet.

`web/test/index.html` adds `<script src="/assets/ui.js">`, and `web/test/test.js` replaces its own `learner()` with `UI.learner()`. Global shortcuts are off on these pages, except `?` and each page's own keys.

###### 2.6 Account menu (`UI.menu`)

A 300px popover, above the user card on desktop and beside the rail avatar. On the phone it is the menu sheet above. It uses `role="menu"` with `role="menuitem"` items.
* ↑/↓ move, Home/End jump, Enter activates.
* Esc, or a click outside, closes it and returns focus to the trigger (this fixes their Esc bug).

Contents:
1. **Header** (not focusable):
   * avatar 40, name;
   * the full email, or "This device only";
   * the role line: "Student in Period 3", or "Teacher · Period 3, Period 5".
2. When unsaved, a **callout row**: an orange dot, "Save your progress", and the sub-line "So clearing this browser can't lose it". It links to `/me/settings/#account`.
3. Profile (`G U`) · Settings (`G S`), with an orange dot when a report has an unread reply · Sign in (only when unsaved; → `/signin/`) · Pair a device · Join or teach a class (→ `/class/`) · Keyboard shortcuts (`?`) · Help & FAQ · Send feedback.
4. A divider.
5. **Sign out** when saved (a confirm dialog). When unsaved: **Leave this device…** (the unsaved dialog, §4.4).

###### 2.7 Quick sheet (`UI.quick()`): Quick question | Log a mistake

A sheet, 640px centred on desktop and full-screen on the phone. Header: a segmented "Quick question | Log a mistake" (the last tab used is remembered in `satf.quick.tab`), then a close ×.

**Quick question**
1. On open, POST `/api/drill {topics: [], count: null, source: "quick", difficulty: prefs.difficulty}`. With source `quick` and no topics, the server fills in the coach's pick.
   * While it loads: three skeleton lines.
   * On failure: "Couldn't get a question." and Retry.
2. A header line shows the skill chip and a live tally, "3 answered · 2 right".
3. The body renders `UI.question()` exactly as the session does, with A–D / 1–4 / Enter when the Keyboard shortcuts preference is on.
4. After an answer, the verdict shows: the key, the named mistake, and the rationale (following the Explanations preference). Then an actions row:
   * **Another** (pill; Enter or N). This is `/next`, so a miss is followed by its repair: the same trap with new numbers.
   * **Save** (a bookmark toggle).
   * **Report** (§2.10, with this question's context).
   * **Practise {skill} · {prefs.set_length}** (quiet; starts a normal set).
5. Closing the sheet with at least one answer sends POST `/api/drill/{id}/finish` (`fetch` with `keepalive: true`, also on `pagehide`). The sitting shows in history as "Quick questions".
   * With zero answers, the same call deletes the row.
   * A quick sitting is never offered as Resume.
6. After closing, the shell refreshes its badges.

**Log a mistake** (their add-your-own-word, for Math: something from outside goes onto your study list)
1. **Which skill?** The 19 skill chips grouped by domain, with a filter field.
2. **Which kind of question?** The skill's question types from GET `/api/types?topic=`, one row each: the skill label (e.g. "Central angle from an arc") and **Show an example**.
   * Show an example renders one generated item read-only, from a seed range reserved for examples (never served in practice), so the student can say "yes, like that one".
   * A last row, **Not sure**, offers "Practise Circles · 5" instead of logging.
3. **What went wrong?** (optional) Radio rows of that type's named misconceptions (from the survey), plus "Something else" (a text field, 80 chars) and "I don't know".
4. **Where was it?** (optional) Chips: School · Bluebook · Official practice · Book · Other, and a note field (200 chars).
5. **Add to my mistakes** (pill) sends POST `/api/mistakes/log`.
   * Toast: "Added. Two clean answers on this type close it." [Practise now · 3], which runs `/api/drill {trap: …}`.
   * The mistake shows on /mistakes/ tagged "Logged by you · Bluebook".

###### 2.8 Command palette (`UI.palette()`)

Opens with ⌘K / Ctrl K / `/`, the Search button, or phone Search.
* The modal is 640px wide, 12vh from the top; full-screen on the phone.
* The input reads "Search skills, question types, pages and actions".

Results are grouped:

* **Suggested** (empty query only):
  * "Today's set · Probability, Equivalent expressions, Linear functions · 28 q"
  * "Fix all mistakes (14)"
  * "Resume module · 12/22"
  * "Today's challenge"
  * "Due: Period 3 · Circles" (for a student in a class)
* **Recent**: the last 5 run, kept in `localStorage` `satf.palette`.
* **Skills**: all 19.
  * Each row: the glyph, the name, a 48px mastery bar, and "● 2" open mistakes.
  * Enter practises `prefs.set_length` questions.
  * Tab reveals the sub-actions: Practise · Practise hard · Fix mistakes (n) · Open stats (→ `/results/#<slug>`).
* **Question types** (only a bank like ours can offer this): all 386 types, matched on their skill labels (from `/api/types`, cached in `sessionStorage`).
  * Row: the topic glyph, the skill label, the topic chip, and "Practise this type · 5". Enter sends `/api/drill {templates: [key], count: 5}`.
* **Mistakes**: the named misconceptions, matched on label, e.g. "Used the diameter as the radius · Circles · 3 types". Enter drills those templates.
* **Pages**: every nav destination, plus Profile, Settings, Help, Sign in and Class.
* **Actions**:
  * Quick question · Log a mistake
  * Start a module (22 q · 35 min) · Start a full section (44 q · 70 min) · Take the diagnostic
  * Practise saved (n) · Practise types I haven't met
  * Send feedback · Pair a device · Copy device code · Join a class
  * Theme: Light / Dark / System · Keyboard shortcuts

**Parsing**, which the never-ending bank makes possible. A query like "circles hard 5 timed" puts a composed first row on top: "Practise **Circles** · Hard · 5 questions · timed".
* Numbers 1–120 set the count; "endless" or "∞" makes it endless.
* easy / medium / hard / mixed / adaptive set the difficulty.
* "timed" / "untimed" set the clock; "mc" / "grid" set the format.
* Several skills combine: "circles percent 10".

Matching is a case-insensitive prefix and substring match over the names, plus an alias list kept beside `TOPICS` in ui.js:

| topic | aliases |
|---|---|
| nonlinear_functions | quadratic, exponential, parabola, vertex |
| right_triangles_and_trigonometry | trig, sin, cos, tan, sohcahtoa, pythagorean |
| circles | arc, sector, radian, chord |
| ratios_rates_proportions_and_units | ratio, rate, unit, proportion |
| sample_statistics_and_margin_of_error | margin, sample, inference |
| evaluating_statistical_claims | claim, study, experiment |

Keys: ↑↓ move, Enter runs, Esc closes. No match: "No match. Try a skill like "circles", a type like "central angle", or "percent 10 hard"."

###### 2.9 Keyboard shortcuts (`UI.keys`)

A registry with scopes. Shortcuts are ignored while focus is in an input, textarea, select or contenteditable, while a dialog is open (Esc aside), and when the Keyboard shortcuts preference is off.

* **Global**:
  * `G` then `T` Today, `P` Practice, `M` Mistakes, `E` Tests, `L` Plan, `R` Results, `C` Challenge, `K` Class, `U` Profile, `S` Settings, `H` Help.
  * `Q` opens the quick sheet.
  * ⌘K / Ctrl K / `/` open the palette.
  * `[` collapses the sidebar.
  * `?` opens the shortcuts sheet.
* **Session and test pages** register their own (A–D, 1–4, Enter, M mark, X strike, C calculator, R reference). The `?` sheet lists them under "This page".

The shortcuts sheet is a two-column table (keys as DM Mono `kbd` tiles, then the action), grouped Global / This page.

###### 2.10 Feedback and report (`UI.report(ctx)`, one component everywhere)

It opens from:
* **Send feedback** (general mode), or `?feedback` on any URL;
* **Report on every question**: session, test window, report review, question of the day, challenge and the quick sheet. Those sections add the button and call this;
* **Report on a test sitting**.

A 560px modal; full-screen on the phone.

* **Title**: "Report a problem with this question", or "Send feedback".
* **"Sent with this"** box (`--tile`, DM Mono 12.5):
  * For a question: the skill chip, the difficulty, "Question 7 of 10", "Your answer: B", and `circles/central_angle · seed 88213` (the exact address that regenerates it; theirs sends only a UUID).
    * "marked wrong" / "marked right" is added **only once the verdict has been shown**: practice after answering, report review, question of the day after answering, the quick sheet.
    * **Inside a live module, section or challenge, marking is never shown.**
  * For a sitting: its kind, date and band. For a page: the page name and path.
  * A checkbox "Include device details" (on), with a **Show** disclosure listing exactly what is sent: browser, OS, viewport, timezone, app version (from `/api/health`), page URL.
* **Summary** (their Title): prefilled ("Circles · Question 7", or the page name), with a counter "0 / 200".
* **What's wrong?** Radio chips, required:

  | context | categories |
  |---|---|
  | a question, verdict shown | Answer key is wrong · **The named mistake doesn't fit** (feedback on `Item.reasons`, which only we have) · Explanation unclear · Figure or table wrong · Typo or display · Difficulty label off · Other |
  | a question, live sitting | No right answer, or two right answers · Figure or table wrong · Typo or display · Other |
  | general | Bug · Idea · Confusing · Other |

* **Answer key is wrong** reveals two fields:
  * "What answer do you get?" (up to 40 characters).
  * A checkbox, checked by default: "Don't count this question against me while it's checked". This sets `attempts.disputed`, so mastery and accuracy ignore the answer and the mistake it opened is closed.
    * A dispute never changes a test or challenge score.
    * At most 5 open disputes: after that the box is disabled, with "You have 5 answers waiting to be checked."
* **Details**: a textarea with the placeholder "What happened? What did you expect?" and a live counter "0 / 5000". Required for Bug and Other.
* **Images**: an "Add images" button, paste (⌘V) and drop.
  * Up to **10**, as PNG, JPEG, WebP or GIF.
  * Each still image is downscaled in the browser to at most 2000px on its longest edge and re-encoded (WebP, or JPEG where WebP encoding is missing). A 50 MB phone photo sends as about 400 KB. A GIF is sent as-is.
  * Server cap: 10 MB per file.
  * 64px thumbnails with a remove ×.
  * Errors inline: "That GIF is over 10 MB." / "Up to 10 images." / "That isn't an image."
* **Reply to**: an optional email, prefilled when saved. Helper: "Replies also appear under Settings › Your reports."
* **Footer**: Cancel (quiet) and **Send** (pill, with a busy state).
* **On success** the body becomes "Thanks. Report #123 is in. You'll see our answer under Settings › Your reports." with Close. The question's Report button then reads "Reported" and is disabled for that question.
* **Drafts** (category, summary, text, answer) are kept in `sessionStorage` under the context key, so an accidental close loses nothing.
* **Errors**:
  * 429: "That's a lot of reports in an hour. Try again later."
  * A network error keeps the modal open with "Couldn't send. Your text is kept. Retry".

###### 2.11 Banners and toasts

`UI.banner(kind, text, actions)` puts a strip at the top of `main`: `--wash` for notices, `--tile` for system messages. At most one shows, in this priority order:

1. **Retired code**: "This device was signed out from another device." [Sign in] [Start fresh]
2. **Offline**, on a network error from any `api()` call (not a 4xx): "Can't reach SAT Freshman. Retrying in 5s" [Retry now].
   * Backoff 5, 10, 20, 30 s.
   * It clears itself when a call succeeds.
3. **Storage blocked** (replaces today's paragraph): "This browser is blocking site data, so progress can't be kept here." [How to fix] → `/help/#storage`
4. **First visit**: 0 answers and not saved. "Have progress on another device?" [Sign in] [Dismiss]. It stops after a dismissal or the first answer.
5. **Save nudge**: 50+ answers and no email.
   * At most once every 7 days; the dismissal is kept in `localStorage` `satf.nudge`.
   * "Your progress is only in this browser. Save it to an email so clearing the browser can't lose it." [Save progress] [Not now]

`UI.toast(text, {action, href, ms=4000})`:
* Position: bottom-left on desktop (clear of the sidebar); bottom-centre above the tabs on the phone.
* At most 3 stacked, `aria-live="polite"`.
* Used for Saved, Copied, "Code sent", "Signed out" and "24 answers moved here". Also:
  * **Achievements**: the badge, "Achievement · 7-day streak", and [See] → `/me/#achievements`.
  * **Report replies**: "Report #123 answered" [Read] → `/me/settings/#reports`.
  * **New assignments**: "New from Period 3: Circles · 10 q · due Fri" [Open].

After new achievements show, POST `/api/me/achievements/seen`. After replies show, POST `/api/reports/seen`.

###### 2.12 Shell data

GET `/api/shell` once per page load.
* `ui.js` keeps the last response in `sessionStorage` `satf.shell`, paints it at once, then revalidates.
* It refreshes on `visibilitychange` → visible, and wherever pages call `UI.me(true)` today. That call is renamed `UI.refresh()`, and `UI.me` stays as an alias.
* On failure the nav still works: badges stay hidden, and a network error shows the offline banner.
* `UI.plan.dayOf` and the Plan section's `UI.plan.doneOf` compute the Plan and Today metas client-side from `shell.plan` and `shell.today`, so no plan rule is copied into Python.

###### 2.13 Theme, text size, motion

`prefs.theme / text / motion` apply as `html[data-theme="dark"|"light"]`, `html[data-text="large"]` and `html[data-motion="reduce"]`.
* **The default theme is Light**: the brand is white paper. Dark and System are opt-in.
* The values are mirrored to `localStorage` `satf.look`, so one inline line in every page's `<head>` applies them before first paint:

`<script>try{var l=JSON.parse(localStorage.getItem('satf.look')||'{}');var d=document.documentElement;l.theme&&l.theme!=='system'&&(d.dataset.theme=l.theme);l.theme==='system'&&(d.dataset.theme=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');l.text&&(d.dataset.text=l.text);l.motion&&(d.dataset.motion=l.motion)}catch(e){}</script>`

Dark tokens go under `:root[data-theme="dark"]` (System resolves to one or the other in the snippet, so no media-query copy is needed):

| token | value |
|---|---|
| `--paper` | #1A1917 |
| `--ink` | #ECE8E1 |
| `--ink-deep` | #1E1E1E (stays: it is the label on orange) |
| `--amber` | #F18508 |
| `--amber-deep` | #F59B32 |
| `--wash` | rgba(241,133,8,.13) |
| `--wash-2` | rgba(241,133,8,.22) |
| `--tile` | #242220 |
| `--tile-2` | #2D2A27 |
| `--mat` | #3A3631 |
| `--line` | #34312C |
| `--soft` | #A39C92 |
| `--faint` | #6E685F |

* **This section converts every hard-coded page colour to tokens**: 41 in `web/test/index.html`, and one each in `web/me/` and `web/results/report/`. The `#8A847C` in `ui.js`'s avatar becomes `var(--soft)`.
* `.mbar` uses `--ink`.
* Question text uses `--q-size` (20px, or 23px large) and choices `--q-opt` (18.5px, or 21px). The test window uses them too.
* A `<meta name="theme-color">` follows the theme.

###### 2.14 Install as an app

* `web/manifest.webmanifest`:
  * name "SAT Freshman", `start_url` "/", display "standalone";
  * `background_color` and `theme_color` #FFFFFF;
  * icons at 192 and 512 made from the mark, plus a 180px `apple-touch-icon`.
* Every page links it.
* No service worker: the API is the app, and there is nothing useful to serve offline.
* Help explains "Add to Home Screen".

---

##### 3. Profile `/me/` (rebuild of web/me/index.html)

The document title is "Profile · SAT Freshman". The **H1 is the student's name** (or handle), inside the identity card.

**Desktop at 1280** (content ≈ 960px) has two columns. The left column is not sticky: it is taller than a laptop screen.
* **Left, 320px**: Identity, Snapshot, Saved & in progress, Account.
* **Right, fluid**: Goals, Learning preferences, Skills, Score trend, What keeps catching you, Achievements, Activity, Recent activity, Question types met.

**Phone at 390** has one column with 16px gutters, in this order: Identity, Goals, Snapshot, Skills, Score trend, What keeps catching you, Achievements, Activity, Recent activity, Learning preferences, Question types met, Saved & in progress, Account.

**Every card**:
* `--tile` background, radius 14, padding 20 (16 on the phone), with a 1px `--line` border.
* The header row has an H2 (700 16px) on the left and a quiet link on the right.
* It loads with a static skeleton: tile-2 blocks in the final layout, no shimmer.
* A card that fails shows "Couldn't load this." and Retry inside that card only; the rest still render.

**Data**: **GET `/api/me/summary`** (one call) builds the page. `/api/me/activity`, `/api/me/feed` and `/api/me/achievements` load in parallel.

###### 3.1 Identity card (`.id-card`)

`--wash` background.

* **Avatar** 72px: the initial on paper, a chosen topic glyph, or the mark when unnamed.
  * A 24px pencil badge at the bottom-right is a button labelled "Change avatar".
  * It opens a popover: "Initial" plus the 19 glyph tiles (5 a row, 44px; the selected one has a 2px orange ring).
  * A click saves (`PUT /api/me {avatar}`) and toasts "Saved". Esc closes.
* **Name**: the H1, 800 24px, with a pencil button "Edit name".
  * Editing swaps in an inline field (24 characters max). Enter saves, Esc cancels.
  * Errors inline: "Names can't contain digits, @, < or >." (the server's NAME_OK rule).
  * Below it: "On boards: Dana" / "On boards: Student 4F2A" / "Not listed on boards", with a link to change it.
* **Lines** (DM Mono 12.5 `--soft`):
  * "Studying since Sep 23" (the first attempt; hidden before one).
  * The account line. Saved: a check and "dana@gmail.com". Not saved: an orange dot and "This device only · **Save progress**".
  * The role line, when in a class: "Student in Period 3" / "Teacher · 2 classes".
* **Goal pills** (32px, paper): "Target 700" · "Nov 7 · 45 days". Each opens its quick-edit popover (§3.3). Without a plan: one pill, "Set a goal" → `/plan/`.
* **Stat tiles**: a 2×3 grid of paper tiles (radius 10, padding 12). Each has a label (k), a value (`.num` 28px) and a sub-line (DM Mono 12 `--soft`), and is a link.

  | label | value | sub-line | link |
  |---|---|---|---|
  | STREAK | "6 days" | "best 9 · rest days kept" | `#activity` |
  | ANSWERED | "1,284" | "84 this week" | `/results/` |
  | ACCURACY | "71%" | "76% last 7 days" | `/results/#skills` |
  | STUDY TIME | "42h 10m" | "3h 20m this week" (tests included) | `#activity` |
  | TESTS | "7" | "2 sections · 4 modules · 1 diagnostic" (every sitting counts, unlike theirs) | `/tests/#history` |
  | MISTAKES FIXED | "38" | "14 open" | `/mistakes/` |

  New student: the values are "0" (streak) and "—" (the rest), and the streak sub-line reads "Answer one question to start".

###### 3.2 Snapshot (their ranks, and more)

Rows separated by a 1px `--line`:

1. **Math score**:
   * The band "560–640" (`.num` 32), "Module · Sep 20", and a "Report" link (→ `/results/report/?id=`).
   * Next line: "Best 600–680 · Sep 12".
   * Empty: "No score yet", with two quiet buttons, "Take the diagnostic · 20 q" and "Start a module · 22 q".
2. **Practice rank**. The helper line reads "Right answers in the last 7 days". Up to three lines:
   * "Everyone **#128** of 2,410"
   * "Sitting Nov 7 **#4** of 37" (only with an exam date)
   * "Period 3 **#2** of 24" (one per class)

   Each line has "Board" → `/challenge/#practice`. Empty: "Answer a question this week to be ranked." When unlisted, the line keeps the rank and adds "(only you see this)".
3. **Daily challenge**: "This week **#4** of 37" · "Best day #1 · Sep 21" · "Played 12" · "Ahead of 62% today". The last only appears when played today, computed from today's board, never an invented percentile. Empty: "Not played yet" and "Play today's".
4. **Question of the day**: "18 answered · 14 right" and the streak of consecutive days answered.

###### 3.3 Study goals

Each row has a label (k), a value, a bar and an edit control. The header link is "Open plan" (→ `/plan/`).

* **Target**:
  * A 200–800 range bar, with the latest band shaded (ink 25%) and the target as a 3px orange tick.
  * Labels: "560–640 now · 700 target · +100 to go" (to go = target − band midpoint, floored at 0 → "Target reached").
  * **Edit** opens a popover:
    * a 200–800 slider in steps of 10, with a number field;
    * chips 600 · 650 · 700 · 750 · 800;
    * the live line "+100 from your latest band";
    * [Cancel] [Save], disabled until the value changes.
  * Save sends `PUT /api/me {target}` and toasts "Saved · your plan uses 700 now".
* **Exam**:
  * "Sat, Nov 7 · 45 days", with a countdown bar from the first activity day to the exam.
  * Next line: "6 test days · 32 study days left" (from `UI.plan.dayOf`).
  * **Edit** opens a popover with chips for the upcoming official dates, each with "in N days" (`SAT_DATES`, shared with Plan; past dates are never listed), "Another date" (a native date input, min tomorrow), and "No date yet". Save sends `PUT /api/me {exam_date}`.
* **Daily goal**: "45 min · 28 questions", then today's bars "18 of 45 min" and "12 of 28 questions". **Edit** → `/plan/?step=3`.
* **Weekly goal**: "3h 45m · Mon–Fri".
  * This week's bar: "1h 30m of 3h 45m".
  * 7 day dots Mo…Su: done (the Plan section's `UI.plan.doneOf`) is an orange fill, a study day is a 1.5px outline, a rest day is a faint dash, and today has a ring.
  * The week starts on the student's preference.
* **Focus**: "Focus: Advanced Math · Strong: Algebra", or "Nothing on focus". **Edit** → `/plan/?step=4`.
* **Preferred time**: "Evening · 19:00", with "Add to calendar" (§4.3) and "Change" → `/me/settings/#study`.

Without a plan, the card reads "No plan yet. Four questions, about a minute." with a **Build my plan** button, the card's one filled button. The target and exam quick edits still work without a plan.

###### 3.4 Learning preferences (inline, as on theirs)

These are the same controls as Settings (`UI.prefRow(key)`), saved instantly with "Saved" at the row's end:

| row | control | helper |
|---|---|---|
| Questions per set | seg 5 · 10 · 22 · ∞ | — |
| Clock | seg Off · SAT pace · Custom | "SAT pace is 95 seconds a question." |
| Difficulty | seg Adaptive · Mixed · Easy · Medium · Hard | "Adaptive gets harder as a skill's bar fills." |
| Explanations | seg Open when I miss · Always open · Tap to open | — |
| Calculator button | switch | — |

Footer link: "All settings" → `/me/settings/`.

###### 3.5 Skills (their subject performance)

The header's right side reads "Strongest: Circles · Weakest: Probability" (once there are answers), with "All skills in Results".

* **Desktop**: the four domains are expanded. Each is a domain header row (name 600 15, a 6px `.mbar`, "312 answered · 74% right") followed by its skill rows.
* **Phone**: the domains are collapsed. Each domain row adds "Weakest: Probability", and a chevron expands it. The state is kept in `localStorage`.
* **Skill rows** (the Results section's shared component):
  * the glyph, the name and a mastery bar;
  * the answered count and the accuracy;
  * open-mistake dots (up to 3, then "+n");
  * a "Practise" link (a `prefs.set_length` set on that skill).
* **New student**: bars at 0, and "Not started" in place of the counts.

###### 3.6 Score trend

`UI.trend(host, points, {target, exam})`, shared with Results. 200px tall (160 on the phone), y from 200 to 800 with gridlines every 100.
* **Bars**: each sitting is a vertical range bar from low to high. Sections are ink, modules ink at 50%, and the diagnostic a hollow diamond. The latest is orange.
* **Target and exam**: the target is a dashed line labelled "Target 700". The exam date is a vertical tick at the right edge when it falls in range.
* **Interaction**: hover or focus shows the tooltip "Module · Sep 20 · 560–640", and a click opens that report.
* **Header**: "Latest 560–640 · Best 600–680".
* **Legend** under the chart: "▮ Section  ▯ Module  ◇ Diagnostic".
* **Empty**: the frame with the target line, "Your first module puts a point here." and "Start a module".

###### 3.7 What keeps catching you (ours only: their bank names no mistakes)

The top 5 named misconceptions by hits, all time, open or fixed. Each row has:
* an orange dot (open) or a check (fixed);
* the label (600 14.5, e.g. "Used the base angle as the central angle");
* a small skill chip, "×3", and last seen "Sep 21";
* "Logged by you" when it came from Log a mistake;
* **Practise**: POST `/api/drill {trap: {template, reason}}` → the same template with fresh numbers, 3 questions.

Footer: "All mistakes". Empty: "No mistakes yet. When you miss, the mistake gets a name here."

###### 3.8 Achievements

The header has "View all (43)". The card shows 6 tiles in a 3-column grid (2 on the phone): the 3 most recently earned, then the 3 closest to their next tier.

**Tile anatomy**:
* A 44px badge circle. Earned: orange fill with an ink-deep icon or glyph. Locked: `--tile-2` with a `--faint` icon.
* The name (600 14) and the tier in Roman numerals ("II").
* Progress, "5 / 7 days", with a 3px bar.
* The earned date, "Sep 21".

**The View all sheet**:
* Filter chips: All · Earned · In progress.
* Grouped Habits / Volume / Mistakes / Skills / Tests / Challenge.
* The Skills group is the **19 topic-glyph badges** (each fills when that skill's mastery reaches 0.8), plus 4 domain badges and "Explorer" (question types met).
* Each row: the badge, the name, a one-line rule ("Answer on 7 study days in a row"), the tier ladder "3 · 7 · 14 · 30 · 60 · 100" with earned tiers in ink, and the dates.

New student: every badge is locked, with first-tier progress at 0. Earned tiers also show in the practice session's summary (shared need).

###### 3.9 Activity (heatmap; theirs is one month on the dashboard, drawn in UTC)

`UI.heatmap(host, days, {weeks})`. Days are the student's local days (from `X-Tz`), so late-evening study lands on the right day.
* **Grid**: 26 weeks × 7 rows of 12px cells with 3px gaps, radius 3. Month labels above; M / W / F at the left.
* **Colour** by questions answered: 0 is `--tile-2`; 1–9 / 10–24 / 25–49 / 50+ are orange at 25 / 50 / 75 / 100%. A planned rest day with nothing done shows a faint centre dash.
* **Tooltip** on hover or focus (the cells are focusable in a `role="grid"`, and arrow keys move): "Wed, Sep 23 · 24 questions · 33 min · 5 right", or "Sat, Sep 19 · rest day (plan) · streak kept".
* **Legend**: "Less ▢▢▢▢▢ More".
* **Stats row**: "Active days 34 · Current streak 6 · Best 9 · Study time 42h 10m".
* **Range**: a "26 weeks | 52 weeks" toggle on desktop. The phone shows the last 20 weeks and fits 358px with no scroll.
* Anchor `#activity`.

###### 3.10 Recent activity

Filter chips: All · Practice · Tests · Mistakes · Challenge · Class · Achievements.

Items are grouped under day headers ("Today", "Yesterday", "Mon, Sep 21"). Each row has an icon, a title, a detail, a time ("14:02 · 3h ago") and a chevron, and links wherever it can:

| kind | title | detail | link |
|---|---|---|---|
| Practice set | "Practice · 7/10" | "Circles, Percentages · 12 min" | `/results/report/?id=` |
| Quick questions | "Quick questions · 3/4" | the skills | the report |
| Module / Section / Diagnostic | "Module · 540–620" | "22 questions · 31 min" | the report |
| Assignment | "Period 3 · Circles · 8/10" | "on time" or "late" | the report |
| Challenge | "Daily challenge · #4 of 37" | "8/10 · 11:42" | `/challenge/?day=` |
| Question of the day | "Question of the day · right" or "missed" | the skill | — |
| Mistake fixed | "Fixed: Used the base angle as the central angle" | "Circles" | `/mistakes/` |
| Mistake logged | "Logged: Used the diameter as the radius" | "Circles · Bluebook" | `/mistakes/` |
| Achievement | "Earned: 7-day streak" | the tier | `#achievements` |
| Report answered | "Report #123 · Fixed" | the first line of our reply | `/me/settings/#reports` |

The list pages 20 at a time: "Show more" loads the next page by cursor. Empty: "Nothing yet. Your first set shows up here." and **Start today's set** (the coach's pick).

###### 3.11 Question types met (where they show usage meters)

Nothing is metered here, so the meter becomes a study tool.
* "57 of 386 question types", with a bar. A type counts once it has been answered.
* Four domain rows ("Algebra 22 / 101", with bars). Each expands to its topics ("Circles 9 / 16").
* Helper line: "A type is one kind of question: new numbers every time you meet it."
* **Practise types I haven't met** → POST `/api/drill {topics: all, unseen: true, count: prefs.set_length}`. Each topic row has its own "Practise unmet" link.
* When all 386 have been met: "Every type met." and the button hides.

###### 3.12 Saved & in progress

* "Saved questions **3**", with **Practise saved** (`/api/drill {saved: true}`) and "See all" → `/mistakes/#saved`.
* "Open mistakes **14**", with **Fix all** (`/api/drill {mistakes: true}`).
* "Assigned **2 due**" → `/class/`, for a student in a class.
* "In progress": up to 3 rows. For example "Module · 12/22 answered · 18 min left · **Resume**" (→ `/test/?s=`) or "Practice · 4/10 · **Resume**" (→ `/practice/session/?id=`). Quick sittings are never listed.
* Each part hides when its count is 0. When all are empty: "Nothing saved or in progress."

###### 3.13 Account

* **Saved**: "Progress saved to dana@gmail.com · since Sep 23", with **Manage** → `/me/settings/#account`, and **Sign out** (quiet, door icon, confirm dialog).
* **Not saved**: "This device only. Clearing this browser loses it.", with:
  * **Save progress** (filled);
  * "Pair a device" and "Share with a parent or tutor";
  * **Leave this device…** (the unsaved dialog).

###### States

* **Loading**: a skeleton per card.
* **Card error**: in-card Retry.
* **Offline**: the shell banner, with the last `satf.shell` data still painted.
* **Retired code**: the banner, and every card replaced by "This device was signed out. Sign in to see your progress."
* **New student**: every card still renders its frame and its empty-state action. No card is hidden.
* **Lots of history**:
  * Numbers use thousands separators (1,284) and hours ("42h 10m").
  * The feed pages, and the heatmap offers 52 weeks.
  * Achievements "View all" scrolls inside its sheet.
  * The page makes one summary call however much history there is (the server aggregates).

---

##### 4. Settings `/me/settings/` (new)

H1 "Settings".
* **Desktop**: a sticky section nav on the left (200px): Practice · Tools & display · Study · Account & devices · Your reports · Privacy & data. These are anchors, and the one in view is highlighted.
* **Phone**: the sections stack, with the same six as a wrapping chip row under the H1.

**Row anatomy**: the label (600 15) and a one-line helper (13px `--soft`) on the left, and the control on the right. On the phone the control goes under the label.
* Every change sends `PUT /api/me {prefs: {key: value}}` (a partial merge).
* Success: "Saved" (DM Mono 12.5 `--soft`) at the row's end for 1.6 s.
* Failure: the control reverts, with an inline "Couldn't save. Retry".

**Controls**: `.seg` (segmented, `role="radiogroup"`, arrow keys), `.switch` (`role="switch"`), `.field` and native time inputs.

###### 4.1 Practice

These are the defaults a new set opens with. The Practice page can still change them per set, and it offers "Save as my default" there. Today's coach set keeps the plan's length.

| row | control | default | helper |
|---|---|---|---|
| Questions per set | seg 5 · 10 · 22 · ∞, plus a number box 1–120 | 10 | "Endless keeps going until you stop." |
| Clock | seg Off · SAT pace · Custom (+ minutes 1–180) | Off | "SAT pace is 95 seconds a question." |
| Difficulty | seg Adaptive · Mixed · Easy · Medium · Hard | Mixed | "Adaptive gets harder as a skill's bar fills." |
| Question format | seg Both · Multiple choice · Grid-in | Both | "Grid-ins are about a quarter of the real test." |
| Feedback | seg After each question · At the end | After each | "At the end works like a test: no key until you finish." |
| Repair questions | seg Right after a miss · At the end of the set | Right after | "The same mistake with new numbers." |
| Explanations | seg Open when I miss · Always open · Tap to open | Open when I miss | — |
| Keep strong skills warm | switch | on | "Brings back a mastered skill after 10 days." |
| Confirm before ending a set | switch | on | — |
| Keyboard shortcuts | switch | on | "A–D, 1–4, Enter, and G-letter navigation." |

A "Reset practice defaults" quiet button ends the section.

###### 4.2 Tools & display

* Show the timer (on).
* Show the per-question stopwatch (on).
* Calculator button (on).
* Open the calculator when a set starts (off).
* Reference sheet button (on).
* **Theme**: seg Light · Dark · System (default Light).
* **Question text**: seg Normal · Large, with a live serif preview line, "If 3x + 5 = 20, what is x?"
* **Motion**: seg System · Reduce.
* **Week starts on**: seg Monday · Sunday.

###### 4.3 Study (`#study`)

* **Preferred study time**: seg Morning 7:00 · After school 16:00 · Evening 19:00 · Night 21:00, plus a custom time input.
* **Reminder**: seg None · 10 min before · 30 min before (default 10).
* **Calendar**. The helper reads "Your study days at your preferred time until the exam, with a reminder. Test days and the exam are marked."
  * **Download .ics**: built client-side from `days`, `minutes`, `exam_date` and `study_time`. It is RRULE-based, so it needs no copy of the plan logic: weekly on the study weekdays, until the day before the exam; the week's last study day titled "Test day"; the exam as an all-day event; a VALARM at the reminder lead.
  * **Subscribe**: copies a `webcal://…/api/cal/{token}.ics` link. The feed is the same file, served live, so edits to the plan move the calendar. "Turn off" revokes the token.
  * Both are disabled without a plan, with the helper "Build a plan first".
* The plan line "Nov 7 · 700 · 45 min · Mon–Fri" and "Edit plan".

###### 4.4 Account & devices (`#account`)

* **Name** (a field and Save), with the board preview underneath.
* **Avatar**: the 19-glyph grid, inline.
* **Show me on boards**: seg With my name · Anonymously · Don't list me. Helper: "Anonymous shows Student 4F2A. Unlisted still shows you your own rank." It applies to the challenge boards and the practice ranks.

**Email**, by state:
* *Not saved*: "Save your progress to an email. No password: we send a code." An email field and **Send code**.
  * 429 → "Wait a minute before asking for another code."
* *Code sent*: "Enter the 6-digit code we sent to dana@gmail.com."
  * 6 OTP boxes (`UI.otp`).
  * "Resend in 45s" and "Use a different email".
  * "Or tap the link in the email on this device."
  * Wrong code: "That code doesn't match. 4 tries left." After 5 wrong tries: "That code is used up. Send a new one."
* *Signed in* (the email belonged to other progress): the toast "Signed in as Dana · 24 answers moved here" and a reload.
* *Saved*: "Saved to dana@gmail.com · since Sep 23".
  * **Change email**: sends a code to the new address and switches on verify. 409 → "That email already has its own progress. Sign in with it instead."
  * **Unlink email**, with the confirm "Unlink? This device keeps its progress, but you won't be able to sign in with this email."

**Pair a device**:
* **Show a pairing code** opens a panel:
  * the 6 digits (DM Mono 32, grouped 482 913);
  * a 160px QR code of `/pair/?c=`;
  * "Expires in 9:41", counting down;
  * "On your other device, open **satfreshman…/pair** or scan this."
  * An incoming request turns the panel into the Allow / Deny prompt (§1). "New code" is offered after expiry.
* **I have a code** → `/signin/#pair`.

**Device code** (a `<details>`, "Device code, for moving progress by hand"):
* The masked code, with Show/Hide and Copy (toast "Copied").
* "Use a code from another device": a field and **Use**, then the two-sided confirm dialog (§1).
* Errors: "That is not a code." / "That is this device." / "Nothing is saved under that code."

**Sign out of this device** (a quiet button with a door icon):
* Saved → confirm: "Sign out? You can sign back in with dana@gmail.com." [Sign out] [Cancel]
* Not saved → confirm: "This device's progress isn't saved to an email. If you sign out, this browser forgets it." It shows the masked code with Copy, then [Save to email first] (filled) [Sign out anyway] [Cancel].

**Sign out everywhere else** (saved only): confirm "Other devices will need to sign in again." → POST `/api/account/rotate`, then the toast "Other devices signed out".

###### 4.5 Your reports (`#reports`)

Every report this learner has sent, newest first. Each row:
* "#123", the category, and the context chip (skill, or page);
* "Sep 23";
* a status chip: New · Being checked · Fixed · Checked, no change;
* our reply, expandable, with "Sep 24". Unread replies carry an orange dot.

A dispute's outcome says what it did:
* Key corrected: "This answer no longer counts against you."
* Key confirmed: "The key was right, so this answer counts again and the mistake is open."

Empty: "No reports yet. Use Report on any question, or Send feedback."

###### 4.6 Privacy & data

* **Share with a parent or tutor**: [Create a link] opens a list of links. Each shows "created Sep 23" · "Viewed 3 times, last Sep 22" · Copy · Turn off. Helper: "They see your stats, skills, score trend, activity and open mistakes. Never your email or device code."
* **Download my data**: GET `/api/me/export` → `sat-freshman-2026-09-23.json`.
* **Delete everything**: a dialog listing what goes (answers, mistakes, saved, sittings, plan, email link, share links, class memberships, reports). It adds: "Your past challenge results stay on the boards as an anonymous student."
  * A type-to-confirm field ("DELETE"), then [Delete everything].
  * Afterwards: a new anonymous code, a redirect to `/`, and the toast "Deleted".

---

##### 5. Sign in `/signin/` (new; their `/auth`) and `/pair/`

A centred card, 440px wide (full width on the phone), with the mark and the H1 "Sign in".
* Line: "This device has 24 answers. They'll be added to the progress you sign in to." (Hidden at 0.)
* Tabs: **Email code** · **Pairing code** · **Device code** (hash `#email` / `#pair` / `#code`).

**Email code**:
* The email field → Send code → 6 OTP boxes (`autocomplete="one-time-code"`, `inputmode="numeric"`; a paste splits across the boxes and backspace moves back).
* `?t=` in the URL runs the link flow (§1).

**Pairing code**:
* 6 OTP boxes → Continue → "Approve on your other device" (a waiting state with static dots under reduced motion) → the preview "Dana · 1,284 answers · since Sep 2" → [Use Dana's progress here] [Cancel].
* `?c=482913` prefills and continues on its own.
* Errors:
  * 404 "No code like that. Check the six digits."
  * 410 "That code has expired or was used. Make a new one on your other device."
  * 403 "Your other device said no."
  * 429 "Too many tries. Wait 10 minutes."

**Device code**: the paste field and the two-sided confirm.

**Already saved**: "You're signed in as Dana (dana@gmail.com). To sign in as someone else, sign out first." [Sign out]

**Success**: carry, adopt, then a reload to `/` with the toast "Signed in as Dana".

`/pair/` is a two-line page that redirects to `/signin/?c=…#pair`, because a short URL is easier to type on a phone.

##### 6. Shared view `/share/?t=` (new, read-only)

For a parent or tutor, with no login. A minimal bar: the mark, and "SAT Freshman" linking to `/`.
* H1 "Dana's SAT Math progress", with "Shared by Dana · live · updated 14:02".
* Cards:
  * the identity card, without email, avatar editing or goal edits, and with its stat tiles;
  * Snapshot; Goals (read-only); Skills; Score trend;
  * What keeps catching you (names and counts);
  * the Activity heatmap;
  * Recent activity (titles only, no links).
* No actions and no nav.
* A link that was turned off, or is unknown: "This link was turned off."
* The page adds `<meta name="robots" content="noindex">`.

##### 7. Classes `/class/` (new; their hidden `/my-classes` and `/teacher`)

Any saved account can teach. Creating a class needs a saved email ("So a cleared browser can't lose your class"). Joining needs nothing.

###### 7.1 Student view (`/class/`)

* **Join a class**:
  1. A 6-character code field ("K7M2QX"), or `/join/?c=`.
  2. The preview: "Period 3 · Ms. Rivera · 24 students".
  3. "Your name in this class": required, prefilled from the profile name, 1–40 characters, NAME_OK. Consent line: "Ms. Rivera will see this name, your assignment results, and your weekly practice totals, skills and open mistakes. Never your email or device code."
  4. **Join**.
* **Class cards**, one per class: the class name, the teacher, and "2 due".
* **Assignment rows**:
  * the title, skill chips, and "10 questions · due Fri 23:59" (or "Module · 22 q · 35 min");
  * the status: Not started / 4 of 10 / Done 8/10 / Late;
  * the actions: **Start** / **Resume** / **Review** (→ the report).
* **After finishing**: "Attach your working" (optional, up to 5 images, downscaled like the report modal), with thumbnails and remove, for a teacher who wants to see the working.
* "Leave class" (confirm).
* Empty: "You're not in a class. Ask your teacher for a code." with the join field.

###### 7.2 Teacher view (`/class/?id=`)

* **Header**:
  * the class name, editable;
  * the join code "K7M 2QX", with Copy link, QR and "New code";
  * "24 students" and "Archive class".
* **Tabs: Students · Assignments · Mistakes.**
* **Students**: a sortable table. The phone gets cards.
  * Columns: Name · Last active · This week (questions, % right) · Open mistakes · Latest band · the last 3 assignments' status ("8/10", "late", "—").
  * A row opens a read-only student view with the share-view cards, scoped to the consented data.
  * **Remove** (confirm).
* **Assignments**: a list (title, skills, count, due, done n/m, average right) and a **New assignment** sheet:

  | field | options |
  |---|---|
  | What | Practice set · Module (22 q · 35 min) · Full section (44 q · 70 min, adaptive) |
  | Skills (sets only) | the 19 chips, or question types found by search |
  | Count | 5–60 |
  | Difficulty | Mixed · Easy · Medium · Hard · Adaptive |
  | Clock | Off · SAT pace · Custom |
  | Questions | **Fresh for each student** (default; "No two students get the same numbers, so answers can't be shared") · **Same for everyone** ("Good for going over them together") |
  | Due | date and time |
  | Who | Everyone · chosen students |

* **Assignment detail**:
  * **Per student**: status, right/asked, time, finished at, late, and attached working.
  * **Per question**, for same-for-everyone assignments: Q1…Qn, % right, and the most-picked wrong option with its named mistake.
  * **Mistakes across the class** (only a misconception-labelled bank can give this): the named misconceptions ranked by students affected, e.g. "9 of 24 · Used the base angle as the central angle · Circles". Each has **Assign a repair to these 9**, which creates a 5-question assignment on those templates for just those students.
* **Mistakes tab**: the same ranking over all practice this term.
* **Empty class**: the join code large, with "Share this code or link with your students."

`/join/` redirects to `/class/?join=…`.

##### 8. Help `/help/` (new, in place of their billing FAQ)

H1 "Help". A search field filters the questions live. No match: "No question matches. Send feedback and ask."

Sections are `<details>`, each with an anchor id and a copy-link button:
* **Getting started**:
  * Is it really free? (Yes, all of it: no plans, trials or limits.)
  * Do I need an account? (No. Save to an email whenever you like.)
  * What does it cover? (SAT Math: 4 domains, 19 skills. Reading & Writing not yet.)
  * Can I put it on my home screen?
* **Practice & mistakes**:
  * What is an open mistake?
  * How does a mistake close? (Two clean answers on that type.)
  * What is a repair question?
  * How do I log a mistake from somewhere else?
  * What does the bar under a skill mean? (Recent answers, harder ones counting more, growing with evidence.)
  * Will I see the same question twice? (No. Saved ones come back exactly.)
* **Tests & scores**:
  * How is my score estimated, and why a band?
  * What decides module 2? (60% of module 1, a stated choice.)
  * Why did my score stop at 580? (The lower route's ceiling.)
  * How are grid-ins marked? (By value, with the fourth-digit rule.)
  * Can I retake a test? (Every sitting is new.)
* **Plan & streak**:
  * How does the plan choose what I do?
  * What if I miss a day? (It recomputes daily.)
  * Do rest days break my streak? (Planned ones don't.)
  * How do I put my plan in my calendar?
* **Classes**:
  * How do I join a class?
  * What does my teacher see?
  * How do I set homework?
* **Account & devices** (`#devices`, `#storage`):
  * How do I use my progress on another device?
  * What happens if I clear my browser?
  * What is the device code?
  * How do I sign out?
  * Why does it say site data is blocked?
* **Reports**:
  * What happens when I report a question?
  * What does "don't count this against me" do?
* **Privacy**:
  * Who sees my name?
  * What do you store?
  * How do I download or delete it?

Then a **Keyboard shortcuts** table and a **Still stuck? Send feedback** button.

Answers are drawn from the README's stated facts. Nothing is claimed that the README or this spec doesn't support.

##### 9. What replaces Subscription

No route, no plan cards, no meters, no "Upgrade". Their three selling surfaces become the student's own:

| theirs | ours |
|---|---|
| sidebar upgrade card | the **Today card** |
| profile credits card | **Question types met** |
| subscription FAQ | **/help/** |

"Is it really free?" is the first Help question.

##### 10. Reports admin `/admin/reports/` (new, minimal)

* **Access**: the page asks once for the admin token (kept in `sessionStorage`). All calls send `X-Admin`. With `SATF_ADMIN_TOKEN` unset, every admin endpoint is 404.
* **List**: filters for status, category, kind and template, newest first. Rows: #id, category, summary, context chip, age, dispute flag.
* **Detail**:
  * the summary, details, device, reply-to email and images;
  * the question **regenerated from (template, seed)** with its key, rationale and every option's named mistake (`/api/admin/question`).
  * **Actions**:
    * Status: New / Being checked / Fixed / Checked, no change.
    * Reply (text).
    * For a dispute: **Key was wrong** (the attempt stays disputed for good, and the template is flagged in the log) or **Key was right** (disputed returns to 0, and the mistake the dispute closed reopens).
* With `SATF_REPORTS_TO` set, each new report also emails that address.

##### 11. Component inventory (ui.js / ui.css)

**JS**:
* Shell and data: `UI.shell`, `UI.refresh` (with the `UI.me` alias), `UI.prefs()` (defaults merged), `UI.prefRow(key)`.
* Overlays: `UI.menu(trigger, items)`, `UI.sheet({title, body, actions, size})`, `UI.confirm({title, text, confirm, cancel, input})` (returns a Promise), `UI.toast`, `UI.banner`, `UI.tooltip`.
* Features: `UI.report(ctx)`, `UI.quick()`, `UI.palette()`, `UI.keys.register(scope, map)`.
* Data views and controls: `UI.trend`, `UI.heatmap`, `UI.otp(host, onComplete)`, `UI.avatar(profile, size)`, `UI.images(host, {max, maxBytes})` (the shared downscaling image picker, used by reports and assignments), `UI.ics(plan, prefs)`.
* Shared data: the `SAT_DATES` constant, shared with Plan.

**CSS**:
* Shell: `.side`, `.side-item`, `.side-meta`, `.side-day`, `.rail`, `.pbar` (the phone top bar), `.tabs`, `.more`.
* Overlays: `.menu`, `.popover`, `.tip`, `.toast`, `.banner`, `.palette`.
* Controls: `.seg`, `.switch`, `.chips` (radio chips), `.counter`, `.otp`.
* Data and cards: `.stat`, `.meter`, `.skel`, `.card`, `.kbd`, `.badge`, `.heat`, `.trend`, `.table` (sortable), `.thumbs`.

**New icons**: mistakes (a target), challenge (the existing trophy), class (a group), help, feedback (a speech bubble), search, bolt, sidebar, settings, profile, devices, link, signout, more, chevron, check, pencil, eye, eye-off, copy, download, trash, calendar, image.

**QR codes**: `web/assets/qr.js` is a vendored MIT QR encoder (qrcode-generator), loaded only by Settings and the class page.

**Dialogs** are native `<dialog>` (focus is trapped natively; Esc closes). Under 760px, `dialog.sheet` becomes a bottom sheet: full width, radius 16 16 0 0, a drag handle, max-height 90vh.

### 3.1.4 Extras: what they missed

- **Start without an account; save to an email later with a 6-digit code (no password)**: Theirs puts a Google wall in front of everything. Ours lets a student practise on the first click and still get a portable, recoverable account, so clearing the browser can no longer lose months of work. The code has to be finished on the device that asked, so an unexpected email can't be used to take someone's progress.
- **Pairing code + QR, approved on the first device**: Moving from laptop to phone becomes one scan and one tap, instead of copying a 26-character code. It works without email, e.g. on school-managed devices. The approval step makes guessing a code useless.
- **Sign out everywhere else (code rotation, with a retired-code banner)**: The device code is the whole credential, so a student who used a library computer can cut it off. Theirs has plain sign-out only.
- **Live nav badges: today's progress, open mistakes, test Resume / Test day, the plan's day, new report, challenge New / #rank, class assignments due**: Every section says what is waiting there. Their nav is ten silent labels.
- **Today card in the sidebar and the menu sheet**: Their upgrade-card slot is used for what a student should see on every page: minutes and questions against the goal, the streak, the exam countdown and the next assignment due.
- **Quick question from any page (Q), with the repair question next**: Our version of their floating button, without covering Next. One fresh question from the coach's pick, and a miss is followed by the same misconception with new numbers. Only a bank that never runs out can do that.
- **Log a mistake from anywhere (school, Bluebook, a book)**: This is the capture half of their add-your-own-word button, done for Math. The student picks the question type from a real generated example and the named misconception from our list. The outside miss becomes an open mistake drilled with fresh numbers until two clean answers close it. A finite bank has nothing to drill it with.
- **Command palette that searches the bank: 386 question types, every named misconception, and 'circles hard 5 timed' parsing**: 'central angle' + Enter practises exactly that kind of question; 'circles hard 5 timed' starts exactly that set. That needs a generated bank where any type × difficulty × count exists instantly. It is also the fastest way to any page or action.
- **Global keyboard shortcuts with a ? sheet**: For power users and accessibility. Their site has none, and their popovers ignore Esc.
- **Reports that carry (template, seed), a 'named mistake doesn't fit' category, a bounded dispute, and a Your reports list with replies**: A reported question can be regenerated exactly, and students check the misconception labels, our core asset. A disputed key stops hurting mastery while it is checked. The student sees the outcome, where theirs never hear back. Reports made mid-test never reveal marking.
- **Achievements tied to learning: 19 skill glyph badges, mistakes fixed, 'never twice', question types met, upper route, podium**: Theirs are four hard-coded tiles with no progress and a dead View All. Ours reward the behaviours that raise scores, and several can only exist with named mistakes and a template bank.
- **'What keeps catching you': your top named misconceptions, each with Practise**: A finite bank without distractor reasons cannot show this. It is the most actionable one-card summary of a student there is.
- **Question types met, 57 of 386, with 'Practise types I haven't met'**: It turns their usage meters into coverage, so a student has met every kind of problem before test day.
- **Practice rank among students sitting the same exam date**: Their country rank compares you with strangers on unstated terms. The cohort that matters is everyone sitting Nov 7, ranked on stated terms (right answers in the last 7 days), with board privacy respected.
- **Plan-aware streak: planned rest days don't break it**: A student following a Mon–Fri plan shouldn't be punished every weekend for following it. It is one value on every screen, where theirs shows 0 on the profile and 1 on the question of the day.
- **Study time that includes tests**: Tests are the longest study sessions there are. Today, the heatmap and the profile all count them.
- **Activity heatmap (26 or 52 weeks) in local days, with per-day questions, minutes and accuracy**: Consistency made visible. Theirs is one month on the dashboard, and it shows the wrong day because it is drawn in UTC.
- **Recent activity feed with filters, including mistakes fixed or logged, assignments, achievements and report replies**: Theirs is a list of sittings. Ours shows progress as events a student can go back to.
- **Resume unfinished sittings from the profile, the nav and the palette**: Their QBank sessions survive only by URL.
- **Classes with fresh-per-student homework and a class misconception report**: Their teacher tools are hidden and assign a fixed bank, so students can share answers. Ours can give every student different numbers on the same skills. Their teacher sees scores; ours sees '9 of 24 used the base angle as the central angle' and can assign a repair to exactly those 9.
- **Read-only share link for a parent or tutor, with view count and revoke**: Parents and tutors are part of SAT prep. Theirs can't show progress without handing over the account.
- **Board visibility: with my name / anonymously / don't list me**: Privacy for minors on public boards, while the student still sees their own rank.
- **Download my data / delete everything**: Trust and legal hygiene for a free site used by minors. Challenge rows stay anonymised, so nobody else's rank changes.
- **Dark theme (opt-in), large question text, reduced motion**: Evening study is the common case (their own 'Preferred time: Evening'), and larger serif text helps students with low vision. Theirs has no display settings.
- **Preferred study time that reaches the student's calendar: download or subscribe, with reminders**: Their 'Preferred time' has no effect anywhere. Ours puts the study days in the calendar with an alarm, and the subscribed feed moves when the plan changes.
- **Offline banner with retry, and a retired-code banner**: Ours currently fails silently. Theirs has no stated behaviour.
- **Help with search and deep links**: It explains what students actually ask about: bands, routing, the 580 cap, grid-in marking, how mistakes close, rest days. Theirs answers only billing questions.
- **Save-progress nudge after 50 answers (dismissible, at most weekly) and a first-visit Sign in banner**: These prevent the biggest way to lose work under an anonymous model, without an upsell.
- **Installable as a home-screen app**: Students study on phones. One tap from the home screen, with no browser chrome.
- **Question links: /q/?t=template&s=seed opens exactly that question for anyone, with the key held server-side (owned by the session section; the shell provides UI.share)**: 'Send this one to a friend' works because every question has an exact address. Their Share opened the OS sheet and froze the page.

### 3.1.5 Server changes

Tables and columns here are added by F4 as listed in §2.5; the drill fields map through §2.6; prefs through §2.7.

- **db.py: new columns (LATER_COLUMNS)**

  - learners: avatar TEXT (a topic slug, NULL = the initial); prefs TEXT (JSON, non-default keys only); board TEXT ('name'|'anon'|'hidden', NULL = name); study_time TEXT ('HH:MM'); ach_seen TEXT; cal_token TEXT.
  - users: learner TEXT; login_token TEXT; login_code TEXT (sha256 of the 6 digits); login_for TEXT; login_sent TEXT; login_tries INTEGER DEFAULT 0; last_login TEXT. first and last stay NOT NULL; email-only accounts insert ''. No table rebuild.
  - attempts: disputed INTEGER NOT NULL DEFAULT 0.
  - traps: source TEXT ('outside' for logged), note TEXT, origin TEXT (school|bluebook|official|book|other).
  - sessions: assignment TEXT.
  - Indexes: users(learner), users(login_token), attempts(learner, at), attempts(at).

- **db.py: new tables**

  - pairs(code TEXT PRIMARY KEY, learner TEXT NOT NULL, created, expires, used, req_learner, req_device, req_answers INTEGER, state TEXT DEFAULT 'open' -- open|asked|allowed|denied|used)
  - retired(code TEXT PRIMARY KEY, into TEXT, at TEXT)
  - reports(id INTEGER PRIMARY KEY AUTOINCREMENT, learner, kind ('question'|'sitting'|'page'), source, category, title, answer, details, context JSON, device JSON, email, files JSON, dispute INTEGER DEFAULT 0, at, status DEFAULT 'new', reply, replied, seen)
  - shares(token TEXT PRIMARY KEY, learner NOT NULL, created, revoked, views INTEGER DEFAULT 0, last_view)
  - earned(learner, id, tier INTEGER, at, PRIMARY KEY(learner, id, tier))
  - classes(id TEXT PRIMARY KEY, name, code TEXT UNIQUE, owner NOT NULL, created, archived)
  - members(class, learner, display, joined, left, PRIMARY KEY(class, learner))
  - assignments(id TEXT PRIMARY KEY, class, title, kind ('set'|'module'|'section'), cfg JSON, questions JSON (the fixed list when same-for-everyone), who JSON (NULL = everyone), due, created)
  - attachments(assignment, learner, files JSON, at, PRIMARY KEY(assignment, learner))

- **app.py learner_of: retired codes**

  After the shape check, a primary-key lookup in retired.
  - Writes (POST/PUT/DELETE) with a retired code → 401 {detail: {retired: true, into: null}}. The new code is never returned.
  - GET /api/shell returns {retired: true} in place of its data.
  - Other GETs return the (now empty) data as usual.

- **GET /api/shell**

  Returns:
  - me {name, handle (daily.handle), avatar, linked, email_masked, role {teaching: n, member: [class names]}}
  - streak, best_streak (progress.days: the one streak)
  - today {day, questions, right, minutes}
  - plan {exam_date, minutes, days, tests, per_session, target} | null
  - tested_today
  - mistakes (open count)
  - saved (count)
  - challenge {day, done, started, rank, players}
  - resume: {id, kind, answered, total, seconds_left, href} | null. The newest unfinished mock or module with time left, or a practice set started in the last 24h with at least one answer; never source 'quick'.
  - newest_report (id of the newest finished sitting)
  - assignments {due, soonest {title, class, due}}
  - report_replies (unread)
  - new {achievements: [{id, tier, name}], assignments: [...]}
  - prefs (defaults merged)
  Achievements are evaluated here. ponytail: a 60 s in-process memo per learner; move evaluation into the write paths if it shows in profiles.

- **GET/PUT /api/me: new fields**

  profile() adds avatar, board, study_time, prefs (defaults merged) and account {linked, email, since}.
  PUT validates:
  - avatar: a topic slug or null
  - board: name | anon | hidden
  - study_time: ^([01]\d|2[0-3]):[0-5]\d$
  - prefs: a dict whose keys are all in PREFS, each value checked against its enum or range
  PREFS:
  - set_length 0–120 (0 = endless)
  - clock off|pace|custom; clock_minutes 1–180
  - difficulty adaptive|mixed|easy|medium|hard
  - format both|mcq|grid
  - feedback each|end
  - repairs next|end
  - rationale miss|always|tap
  - keep_warm, confirm_end, keys, show_timer, show_stopwatch, calc_button, calc_autoopen, ref_button (bool)
  - theme light|dark|system (default light)
  - text normal|large
  - motion system|reduce
  - week_start mon|sun
  - remind 0|10|30
  An unknown key or bad value → 422 naming the key. prefs merge into the stored JSON, and only non-default values are stored. target and exam_date keep their current validation; the profile's quick edits write the same fields Plan reads.

- **progress.days: one streak, rest days kept, tests counted, any number of weeks**

  - Adds weeks: int = 2 (max 53) and best_streak.
  - The streak walks back over days with at least one answer. A day that is a rest day in the learner's current plan (learners.days, and the day before exam_date) neither breaks nor adds to it. ponytail: this uses the current plan's weekdays for past weeks; store a plan history if students change days often.
  - Minutes: attempts.ms (capped at MS_CAP) plus, for each finished mock/module/diagnostic sitting (whose attempts carry ms NULL), its elapsed time (finished − started, capped at the sitting's clock), on its finish day.
  - Disputed attempts still count for questions, minutes and streak, and are left out of right.
  - GET /api/me/activity?weeks=26 → {days: [{day, questions, right, minutes, rest}], streak, best_streak, active_days, minutes_total}.
  Today, Results and Plan already call days(), so every screen shows the same numbers.

- **progress.practice_rank(learner, scope)**

  Ranks learners with at least one attempt in the last 7 days (rolling, UTC) by SUM(correct), then COUNT(*), with disputed = 0.
  - scope 'all' | 'exam' (same learners.exam_date) | 'class:<id>' (current members).
  - Returns {rank, of, top: [{name, right, answered, you}] (20)}.
  - board 'anon' shows the handle; 'hidden' is left out of top and of others' rank maths but still gets its own rank.
  Used by /api/me/summary and the Challenge section's practice board (/challenge/#practice).

- **GET /api/me/summary**

  One payload for the profile:
  - stats {answered (all attempts), right, accuracy, accuracy7 (both over disputed = 0), minutes_total, minutes_week, active_days, streak, best_streak, since, tests, sections, modules, diagnostics, sets, mistakes_open, mistakes_fixed, saved, hard_right, qotd {answered, right, run}, challenges_played}
  - score {latest, best, points: [{at, low, high, kind, session}]}
  - ranks {all, exam, classes: [...]}
  - domains [{domain, mastery, answered, right, skills: [{topic, name, mastery, answered, right, traps}]}]
  - catching: the top 5 traps by hits, open or closed, [{template, reason, label, topic, hits, open, last, source}]
  - coverage [{topic, met, total}]: met = distinct templates in attempts (answered, not merely shown); total = len(catalogue.by_topic[topic])
  - challenge {week_rank, week_players, best_rank, best_day, played, ahead_today}
  - resume [up to 3], goals {plan fields, focus, first_day}, classes [{id, name, role, due}]

- **GET /api/me/feed**

  Parameters: before=<iso>, kind=all|practice|test|mistakes|challenge|class|achievements, limit=20 (max 50).
  It merges:
  - finished sessions (with kind, source, assignment, right/asked, estimate, topics, duration)
  - traps closed, and traps logged (source 'outside')
  - earned rows
  - qotd attempts
  - reports with a reply
  Ordered by time, newest first. Returns {items: [{kind, at, title, detail, href}], next}. Titles are built server-side with the copy in §3.10.

- **server/achievements.py (new)**

  RULES is a list of (id, name, group, rule text, tiers, counter-fn), evaluated from SQL aggregates. Earned tiers are upserted into earned with the time the tier was crossed (the n-th attempt's at; the day the streak reached n).
  - Habits: streak 3/7/14/30/60/100 (best, rest days kept); on_target (days meeting the plan's minutes) 5/20/50/100; consistency (weeks with every planned study day done) 1/4/8; qotd 7/30/100.
  - Volume: answered 50/100/250/500/1000/2500/5000; hard_right 10/50/150/500; hours 5/20/50/100.
  - Mistakes: fixed 1/10/25/50/100/250; clean_set (10 or more questions, no misses) 1/5/20; never_twice (closed and not reopened for 14 days) 5/25/100.
  - Skills: skill:<slug> ×19 (mastery ≥ progress.STRONG); domain:<name> ×4; explorer (types met) 50/100/200/300/386.
  - Tests: first_module, first_section, sections 1/5/10, upper_route 1/5, climbing (band midpoint above the first) 50/100/150/200.
  - Challenge: played 1/7/30/100, podium (top 3) 1/5/20, first_place 1/5, perfect (10/10) 1/5.
  That is 43 in all.
  - GET /api/me/achievements → [{id, name, group, rule, icon, tiers, tier, have, next, earned: [{tier, at}]}]
  - POST /api/me/achievements/seen sets ach_seen = now

- **server/account.py (new): email sign-in with a code**

  - POST /api/account/link {email}: EmailStr, lowercased. Upserts users (first = last = '' for a new email). Sets login_token (token_urlsafe(24)), login_code (sha256 of secrets.randbelow(10**6), zero-padded), login_for = X-Learner, login_sent = now, login_tries = 0. Sends mail.send_login(email, code, token). Rate limits (ponytail: in-process, reset on restart): 1 a minute per email; 5 an hour per learner and per client IP → 429. Returns {sent: true, delivery, email_masked}.
  - POST /api/account/verify {code} (X-Learner must equal login_for) or {token, here?: bool}. Expiry 30 minutes; 5 wrong codes → login cleared → 410.
    - A token whose login_for differs from X-Learner, without here=true → {other_device: true, code} (the link holder already has the email, so returning the code reveals nothing new). Nothing is finished.
    - Finish, for the requester (code) or this browser (token with here=true, or the same learner): verified = 1, last_login = now, and then:
      - users.learner NULL → set it to the finishing learner → {saved: true}.
      - users.learner equal to it → {saved: true}.
      - Otherwise A = users.learner, following retired.into: progress.carry(finisher, A) → {learner: A, moved}.
    - The login fields are cleared.
  - GET /api/account → {email_masked, email, verified, since, pending (a code was sent and not used)}.
  - PUT /api/account/email {email}: sends a code to the new address; on verify, the new row takes learner and the old row's learner becomes NULL. 409 if the new email already has a learner.
  - DELETE /api/account → users.learner = NULL.
  - POST /api/account/rotate → mints a new code server-side (same alphabet as ui.js: 'a:' + 24 base-36 chars from secrets), progress.carry(old, new), users.learner = new, INSERT retired(old, new, now) → {learner: new}.

- **server/account.py: pairing with approval**

  - POST /api/pair → deletes this learner's open codes and inserts a 6-digit code (secrets.randbelow, zero-padded, retried on collision) that expires in 10 minutes → {code, expires}.
  - POST /api/pair/request {code, device (≤ 40 chars)} as B → state 'asked', req_learner = B, req_answers = B's count → {pending: true}. It returns no name. 404 unknown; 410 expired or used; 409 your own code.
  - GET /api/pair/{code}/status as A → {state, device, answers}. As B → {state, and after 'allowed' only: name or handle, answers, since}.
  - POST /api/pair/{code}/allow | /deny as A.
  - POST /api/pair/claim {code} as B, state 'allowed' → state 'used', progress.carry(B, A) → {learner: A, moved}.
  - Failed lookups (404/410) are counted per client IP: 10 per 10 minutes → 429. They are also counted per learner, although learner codes are free to mint.

- **progress.carry: every new table**

  Also moves:
  - earned (INSERT OR IGNORE, then delete)
  - shares, reports and attachments
  - members (a class both codes joined keeps one membership)
  - classes.owner
  - users.learner
  - the new learner columns: avatar, prefs (the target's keys win), board, study_time, cal_token, ach_seen = MAX
  It deletes the source's pairs.

- **GET /api/me/export and DELETE /api/me**

  Export: Content-Disposition attachment, sat-freshman-YYYY-MM-DD.json. It holds profile, prefs, attempts, traps, saved, sessions (id, kind, started, finished, result; no question keys), earned, shares (without tokens), reports (without files), class memberships and the account email.
  Delete: body {confirm: 'DELETE'}, else 422.
  - It deletes this learner's rows in attempts, traps, saved, practice_seen, non-challenge sessions, learners, earned, shares, pairs, reports (and server/reports/{id}/), members, attachments, and classes they own (with their assignments).
  - Challenge sessions are kept but re-keyed to 'gone:' + token_hex(12), so they show as an anonymous student and other ranks don't move.
  - users.learner is set to NULL.
  - Returns {deleted: {table: n}}.

- **server/reports.py (new): POST /api/report and the student's list**

  POST /api/report is multipart: a data JSON field {kind, source ('drill'|'test'|'report'|'qotd'|'challenge'|'quick'|'page'), category, title (≤ 200), answer?, details? (≤ 5000; required for bug and other), email?, session?, question_id?, day?, page?, device?, dispute?} plus files[].
  - files: at most 10 → otherwise 400; image/png|jpeg|webp|gif → otherwise 415; ≤ 10 MB each → otherwise 413. Written to server/reports/{id}/.
  - Context is resolved on the server; nothing is trusted from the client. template, seed, topic, difficulty, skill, the learner's given answer and its marking come from:
    - sessions.questions (the learner must own the session: drill, test, quick);
    - daily.question(day) for qotd;
    - daily.challenge(day) for a challenge.
    The key is never returned.
  - Categories are checked against the list for the context. For an unfinished test or challenge sitting, key_wrong and dispute → 409.
  - dispute: true with key_wrong (finished or practice only) sets attempts.disputed = 1 for (learner, session, qid), and closes the trap that attempt opened if no other undisputed miss on that template remains. The closed trap is recorded in context.closed_trap. More than 5 open disputes → 409.
  - Rate limit: 10 an hour per learner → 429. Returns {id}. Log line 'report #id category'. With SATF_REPORTS_TO set, mail.send_report_notice.
  - GET /api/reports → this learner's reports [{id, at, kind, category, title, context_chip, status, reply, replied, unread}].
  - POST /api/reports/seen marks replies read.

- **server/reports.py: admin**

  Every endpoint requires X-Admin == SATF_ADMIN_TOKEN (compared with hmac.compare_digest); 404 when the env var is unset.
  - GET /api/admin/reports?status=&category=&template=&before=
  - GET /api/admin/reports/{id} (with file URLs)
  - GET /api/admin/question?t=&s= (the regenerated item with its key, rationale and reasons)
  - PUT /api/admin/reports/{id} {status, reply, dispute_outcome?: 'key_wrong'|'key_right'}
    - key_right sets disputed = 0 and reopens context.closed_trap (owed = OWED).
    - key_wrong leaves disputed = 1 and logs 'template flagged'.
    - Setting a reply sets replied and clears seen.
  - GET /api/admin/files/{id}/{name} serves images to the admin page only.

- **progress.py: disputed attempts**: topic_mastery(), board(), the trap filing in record(), accuracy in the summary, and practice_rank all add AND disputed = 0. days() keeps them for questions and minutes (study happened) and leaves them out of right. Challenge and test scores are stored results and are never recomputed.
- **Shares**

  - POST /api/share → {token (token_urlsafe(16)), url: '/share/?t=...'}
  - GET /api/share → [{token, created, views, last_view}] (not revoked)
  - DELETE /api/share/{token} → revoked = now
  - GET /api/shared/{token} (no X-Learner) → the summary minus email, code, resume, account and classes, plus feed titles; views += 1, last_view = now. 404 when revoked or unknown.

- **daily.board and every board: visibility**

  JOIN learners.board.
  - 'anon' → name = handle(learner, None).
  - 'hidden' → left out of entries and players, but `you` is still computed for the owner (their rank among all).
  The Challenge section's week, month and all-time boards and practice_rank apply the same rule. Rows keyed 'gone:…' show as a handle.

- **drill: new sources and options**

  The Drill body adds:
  - unseen: bool. Templates never answered go first, falling back to the least answered (topics required).
  - trap: {template, reason}. Queues that template 3 times (the existing queue path).
  - templates: list[str], at most 10, each in the catalogue. Queued round-robin up to count (the queue path).
  - format: both|mcq|grid (shared with the practice section).
  - difficulty 'adaptive': per question, a tier from the topic's mastery (< 0.35 easy/medium, 0.35–0.7 medium/hard, > 0.7 hard); shared with the practice section.
  - source adds 'quick', 'palette', 'assignment' and 'outside'. With source 'quick' and no topics, topics come from progress.coach(learner).
  Other changes:
  - POST /api/drill/{id}/finish on a quick session with 0 answers deletes the row → {deleted: true}.
  - /api/history and the feed label source 'quick' as 'Quick questions' and 'assignment' as the class and assignment title.
  - progress.coach honours prefs.keep_warm: false turns off the strong-topic revisit.

- **blueprint.survey: skills and reasons per template; GET /api/types**

  The startup survey already generates 18 items per template. It now also keeps each template's most common skill label and its distinct non-empty reasons.
  GET /api/types?topic= (public, cached, immutable per deploy) → [{template, topic, skill, reasons: [...], formats, tiers}]. There are no keys or answers in it.
  GET /api/types/{template}/example → one public item (no key) from a reserved seed range (900000+), never served in practice. Used by Log a mistake.

- **POST /api/mistakes/log**

  Body: {template, reason? (one of that template's surveyed reasons), note? (≤ 80, for 'something else'), origin? (school|bluebook|official|book|other), where_note? (≤ 200)}.
  - An unknown template → 422. A reason not in the survey → 422.
  - It opens or bumps the trap exactly as record() does: reason = the chosen reason or '', label = the reason, the note, or the skill; owed = OWED; source = 'outside'.
  - It files no attempt, so accuracy and mastery are untouched.
  - Rate limit 30 a day.
  - Returns {trap}. /api/mistakes includes source, note and origin.

- **server/classes.py (new)**

  - POST /api/classes {name ≤ 60}. 403 {need: 'save'} unless users.learner = X-Learner and verified. → {id, code} (6 characters from an unambiguous alphabet).
  - GET /api/classes → {teaching: [...], member: [{id, name, teacher, due}]}.
  - GET /api/classes/preview/{code} → {name, teacher (the owner's name or handle), students}. 404 unknown or archived; per-IP limit 20 per 10 minutes.
  - POST /api/classes/join {code, display (1–40, NAME_OK)} → membership.
  - POST /api/classes/{id}/leave.
  - Owner only:
    - GET /api/classes/{id} → roster [{member (an opaque id: sha1(class + learner)[:10]), display, joined, last_active, week {answered, right}, open_mistakes, band, assignments: {aid: {status, right, asked, finished, late}}}], plus assignments and mistakes (named traps ranked by distinct members, this term). Never emails or learner codes.
    - PUT /api/classes/{id} {name, archived}
    - POST /api/classes/{id}/code (a new join code)
    - DELETE /api/classes/{id}/members/{member}
    - POST /api/classes/{id}/assignments {title?, kind, topics?, templates?, count 5–60, difficulty, clock, minutes, same: bool, due, who?: [member]}. same = true with kind 'set' draws the list once with a practice.Builder seeded by the assignment id (as daily.challenge does) and stores it in questions.
    - GET /api/classes/{id}/assignments/{aid} → per student, per question (same only: % right, most-picked wrong option and its named mistake), and misconceptions [{template, reason, label, topic, members: n, of}].
    - POST /api/classes/{id}/repair {aid, template, reason} → a 5-question kind 'set' assignment on that template for the members who hit it.
  - Student:
    - GET /api/assignments → [{id, class, title, kind, skills, count, due, status, session}]
    - POST /api/assignments/{id}/start → the existing unfinished session, or a new one: kind 'set' → a drill (source 'assignment'; 'same' uses the exact items path that saved sets use, 'fresh' uses topics or templates); kind 'module'/'section' → the /api/mock/new path. sessions.assignment is set either way.
    - POST /api/assignments/{id}/attach (multipart, ≤ 5 images, same checks as reports) → attachments.
  - A student who leaves keeps their sessions. The teacher's view drops them.

- **Calendar feed**

  POST /api/cal → sets learners.cal_token (token_urlsafe(16)) → {url}.
  DELETE /api/cal → NULL.
  GET /api/cal/{token}.ics (no X-Learner) → text/calendar built from days, minutes, exam_date, study_time and prefs.remind, with no copy of the plan logic:
  - a weekly RRULE BYDAY for study days, UNTIL the day before the exam;
  - a second RRULE for the week's last study day titled 'Test day' (when tests are weekly);
  - the exam as an all-day event;
  - a VALARM at the reminder lead.
  404 when the token is unknown or the plan is unset. ui.js builds the same file client-side for Download (UI.ics), and a test compares the two.

- **mail.py**

  - send_login(to, code, token): subject 'Your SAT Freshman code: 482 913'. The body has the code, the link {BASE_URL}/signin/?t=..., '30 minutes, one use' and 'If you didn't ask for this, ignore it. Nobody can sign in without this code.' The HTML part shows the code in DM Mono and the link as an orange pill button with a graphite label.
  - send_report_notice(to, report) goes to SATF_REPORTS_TO.
  - The diagnostic's confirmation mail also carries a login code and link.
  - Same outbox fallback as today.

- **Diagnostic sign-up joins the account**: In signup(): after the user upsert, if users.learner is null and the session has a learner, set users.learner = session.learner. The verify link also sets last_login and counts as saving.
- **GET /api/health: version**: Adds version, the git short sha read once at startup ('dev' if unavailable). Report device details and the admin page use it.
- **test_flow.py**

  New checks:
  - /api/shell shape for a new learner and a seeded one.
  - Streak equality across shell, /api/me and /api/today, and rest days kept.
  - Test sitting minutes counted.
  - prefs: 422 on an unknown key and on a bad value; the merge; theme default light.
  - Pairing: request (no name) → allow → claim; deny; expired; used; self; IP 429.
  - Email: link → outbox code → verify binds. A second learner: link opened on another learner gives other_device and no claim; its code claims and carries; 5 wrong codes → 410. Rotate retires the old code (401 on write, retired flag on shell).
  - Export has the attempt count. Delete empties every table but keeps anonymised challenge rows.
  - Reports: context resolved on the server for drill, qotd and challenge; 11 files → 400; an 11 MB file → 413; a GIF accepted; key_wrong on a live mock → 409; dispute excludes the answer from mastery but not minutes; a 6th dispute → 409; admin key_right reopens the trap; admin endpoints 404 without the env var.
  - Board 'hidden' excluded, but you is present. Practice rank by exam cohort.
  - Share view has no email or code, and 404 after revoke.
  - Achievements: 50 answers earns 'answered' I, dated with the 50th attempt.
  - Feed pagination cursor.
  - Log a mistake opens a trap with source 'outside' and files no attempt.
  - Classes: create needs save; join; fresh assignment gives different stems to two students; 'same' gives identical (template, seed); the misconception count; the teacher payload contains no email or learner code.
  - The calendar feed has an RRULE and a VALARM, and 404 after DELETE.


### 3.1.6 Files this spec names, and who owns each

| file | owner |
|---|---|
| `web/assets/ui.js` | F2 |
| `web/assets/ui.css` | F1 |
| `web/assets/qr.js` | F2 |
| `web/assets/icon-192.png` | F0 |
| `web/assets/icon-512.png` | F0 |
| `web/assets/apple-touch-icon.png` | F0 |
| `web/manifest.webmanifest` | F0 |
| `web/me/index.html` | S1 |
| `web/me/settings/index.html` | S1 |
| `web/signin/index.html` | S1 |
| `web/pair/index.html` | S1 |
| `web/share/index.html` | S1 |
| `web/class/index.html` | S2 |
| `web/join/index.html` | S2 |
| `web/help/index.html` | S1 |
| `web/admin/reports/index.html` | F6 |
| `web/test/test.js` | S5 |
| `web/test/index.html` | S5 |
| `web/index.html` | S3 |
| `web/practice/index.html` | S4 |
| `web/practice/session/index.html` | S4 |
| `web/tests/index.html` | S5 |
| `web/results/index.html` | S6 |
| `web/results/report/index.html` | S6 |
| `web/plan/index.html` | S7 |
| `web/mistakes/index.html` | S10 |
| `web/challenge/index.html` | S8 |
| `web/diagnostic/index.html` | S5 |
| `web/diagnostic/signup.html` | S1 |
| `web/diagnostic/verified.html` | S1 |
| `server/db.py` | F4 |
| `server/app.py` | F0 (routers register themselves, §2.10) |
| `server/progress.py` | F4 |
| `server/account.py` | S1 |
| `server/achievements.py` | S1 |
| `server/reports.py` | F6 |
| `server/classes.py` | S2 |
| `server/blueprint.py` | F5 → S5 |
| `server/mail.py` | F6 → S1 |
| `server/daily.py` | S3 |
| `server/drill.py` | F5 → S4 |
| `server/test_flow.py` | shared: new checks go in server/checks/<task>.py |
| `README.md` | shared: each task edits its own subsection |
| `spec/rebuild.md` | F0 (superseded by this file) |

A file owned by another task is met through §2.9: the owner builds it, or this section's task adds its hook on its own page.

### 3.1.7 Shared needs

- UI.report(ctx), the one report/feedback modal. The session, test window, report review, question of the day, challenge and quick sheet each add a Report button that calls it with {kind:'question', source, session|day, question_id, revealed: bool}. revealed is false inside a live module, section or challenge, so no marking is shown and key disputes are hidden. A sitting uses {kind:'sitting', session}. → built in F6 report.js  
  ↳ R17: UI.report (F6 report.js)
- UI.sheet / UI.confirm (native <dialog>, a bottom sheet under 760px), UI.menu (a keyboard popover menu; Esc and outside click close it and focus returns), UI.tooltip, UI.toast, UI.banner. Filter dropdowns, the start-exam wizard, review modals and 'end set?' dialogs elsewhere should all use these. → built in F1 kit.js
- Form controls in ui.css: .seg (segmented radiogroup), .switch (role=switch), .chips (radio chips), .field with .counter, .otp. The practice builder, plan wizard, test wizard and class assignment sheet use the same ones.
- Card and data primitives: .card, .stat (label/value/sub tile), .meter (label + n/max + bar), .skel (static skeleton), .badge, .kbd, .table (sortable), and .empty with an action button. Results, Today, Challenge, Tests and Class share them.
- UI.trend(host, points, {target, exam}) and UI.heatmap(host, days, {weeks}): one implementation for Profile, Results, Today (study-time calendar) and the share view. Results owns the full-size trend; Profile uses the compact size. → built in F1 charts.js
- The skill-row component (glyph, name, mastery bar, answered, accuracy, open-mistake dots, Practise link), shared by Profile, Results and Practice. Practise uses prefs.set_length.
- **Need → built in F2 ui.js  
  ↳ R11: one prefs registry (F4 prefs.py), UI.prefs (F2)**

  UI.prefs(), read by every page that starts a set.
  - Practice opens at prefs.set_length / clock / difficulty / format and offers 'Save as my default'.
  - Session and test honour feedback, repairs, rationale, show_timer, show_stopwatch, calc_button, calc_autoopen, ref_button, confirm_end and keys.
  - The question renderer uses --q-size / --q-opt for prefs.text.

- The dark-theme tokens and the head snippet on every page. Every page uses tokens only; this section converts the 41 hard-coded colours in web/test/index.html and one each in web/me/ and web/results/report/.
- UI.keys.register(scope, map), so session and test key handlers appear in the ? sheet and don't collide with global shortcuts. → built in F2 ui.js  
  ↳ R22: one map, §2.8
- web/test/index.html loads /assets/ui.js, and web/test/test.js uses UI.learner() in place of its Math.random mint. → built in F2 ui.js
- drill.py options shared with the Practice section's builder: 'adaptive' difficulty, format, unseen, trap, templates.  
  ↳ R10: the drill body, §2.6 (F5)
- progress.days is the single source for streak (with plan rest days kept) and study minutes (with test sittings added). Today, Results and Plan must read it, not recompute.  
  ↳ R13: progress.days (F4)
- **Need  
  ↳ R14: plan days and marks live in server/plan.py (S7); pages read /api/today.plan; R15: server/satdates.py (F4), served in /api/shell (F2)**

  The Plan section:
  - owns UI.plan.doneOf(day, stats), the 'day done' rule used by the Today meta, the Today card and the profile's week dots;
  - supports /plan/?step=3 and ?step=4 deep links;
  - shares the SAT_DATES constant (upcoming only) with the profile's exam quick-edit;
  - reads target and exam_date written by the profile's quick edits.

- **Need**

  The Challenge section:
  - provides daily.standing(learner, period) for the profile snapshot;
  - adds a practice board at /challenge/#practice using progress.practice_rank;
  - applies board visibility ('anon'/'hidden'/'gone:') on every board.

- Anchors other pages must provide: /results/#skills and /results/#<topic-slug>, /tests/#history, /mistakes/#saved.
- The Mistakes section renders traps with source 'outside' tagged 'Logged by you · <origin>', showing the note.
- The session summary shows achievements earned during the set (from /api/shell new.achievements), and the Results history labels 'Quick questions' and assignment sittings.
- The Today section shows class assignments that are due first, and the Plan counts their minutes. Both use GET /api/assignments.
- UI.images(host, {max, maxBytes}), the downscaling image picker, used by reports and assignment attachments. → built in F1 kit.js
- Question links /q/?t=&s= (session section), using a UI.share(question) helper, if adopted.

### 3.1.8 Acceptance checks

1. At 1280x900, every page except /practice/session/ and /test/ shows a 248px left sidebar listing, in order: Search, Quick, Today, Practice, Mistakes, Tests, Plan, Results, Challenge, the Today card, Help & FAQ, Send feedback, the user card. Class is absent for a learner in no class. Exactly one nav link has aria-current="page" and it matches the page: /results/report/ → Results, /diagnostic/ → Tests, /mistakes/ → Mistakes, /challenge/ → Challenge.
2. Clicking the collapse button (or pressing [) makes the sidebar 68px (getBoundingClientRect().width === 68), and a reload keeps it collapsed (localStorage satf.rail). Focusing a rail item shows a role=tooltip containing its name.
3. At 900px wide the rail is the default. The toggle opens the full sidebar over a scrim, and Esc closes it.
4. At 390x844, document.documentElement.scrollWidth <= 390 on /, /me/, /me/settings/, /help/, /signin/, /class/ and /share/?t=…. The bottom tabs read exactly Today, Practice, Tests, Plan, Results. Tapping the avatar opens a sheet listing Mistakes, Challenge, Profile, Settings, Sign in (unsaved learner), Pair a device, Join or teach a class, Help & FAQ, Send feedback and Leave this device.
5. For a learner with 14 open traps, the sidebar Mistakes item and the phone top-bar chip both show 14. After all traps close, both are hidden.
6. The Today nav meta reads '12/28' for a learner with a 45-minute plan (per_session 28) who answered 12 today.
7. curl -s -H 'X-Learner: a:v2revshellA' localhost:8000/api/shell returns JSON with keys me, streak, best_streak, today, plan, tested_today, mistakes, saved, challenge, resume, newest_report, assignments, report_replies, new, prefs.
8. One streak: for a learner with plan days '1111100' and answers on Mon–Fri of last week and on today (a Monday), /api/shell streak, /api/me days.streak and /api/today days.streak all equal 6.
9. Study time: after finishing a module sitting that ran 20 minutes, /api/me/activity's today minutes rises by at least 19, although its attempts have ms NULL.
10. The account menu opens on Enter on the user card; ArrowDown moves focus through its items; Esc closes it and document.activeElement is the user card again.
11. Ctrl+K, then typing 'circles hard 5' and Enter, navigates to /practice/session/?id=X, and GET /api/drill/X shows topics ['circles'], count 5, difficulty ['hard']. Typing 'central angle' lists a Question types row; Enter starts a drill whose questions all carry that template.
12. Pressing Q on / opens the quick sheet with a question; answering shows the verdict, and Another (Enter) loads a new one. Closing with 0 answers leaves no sessions row with source 'quick'. Closing after 1 answer puts 'Quick questions' in /api/history, and /api/shell resume stays null. On /practice/session/ and /test/ there is no Quick button and Q does nothing.
13. Log a mistake: POST /api/mistakes/log {template: <a circles template>, reason: <one of GET /api/types?topic=circles reasons>, origin: 'bluebook'} → /api/mistakes lists it with source 'outside'. The attempts count is unchanged. An unknown template → 422.
14. Send feedback with category Bug and details 'x' → POST /api/report returns {id}, and sqlite shows a reports row with kind 'page'. Reporting a drill question, the question of the day and a challenge question each stores context.template and context.seed equal to the stored question, although the client never sent them.
15. POST /api/report with 11 files → 400; with one 11 MB PNG → 413; with one GIF → 200. With category key_wrong for a question in an unfinished mock → 409. In the test window, the report modal's 'Sent with this' box contains no 'marked' text.
16. A dispute (key_wrong, dispute true) on a finished drill miss sets that attempt's disputed = 1. The topic's mastery in /api/map ignores it, and today's minutes in /api/me/activity are unchanged. A 6th open dispute → 409.
17. Admin: with SATF_ADMIN_TOKEN unset, GET /api/admin/reports → 404. With it set, PUT {status:'no_change', reply:'Key checked', dispute_outcome:'key_right'} sets the attempt's disputed back to 0 and reopens the trap. The student's GET /api/reports shows the reply as unread, and /api/shell report_replies is 1.
18. Pairing: POST /api/pair as A → {code}. POST /api/pair/request as B → {pending:true} with no name in the body. A allows. B's status shows A's name. POST /api/pair/claim as B → {learner: A}, and B's attempts now carry learner A. Claiming again → 410. 11 wrong codes from one IP within 10 minutes → 429.
19. Email: POST /api/account/link as A writes a mail to server/outbox/ holding a 6-digit code and a /signin/?t= link; POST /api/account/verify {code} as A binds it. Then learner C links the same email. POST verify {token} with X-Learner D returns {other_device: true} and C is not signed in. POST verify {code} as C returns {learner: A}. Five wrong codes → 410.
20. POST /api/account/rotate as A → {learner: A2}. A PUT /api/me with header A → 401 with detail.retired true, and /api/shell with A → {retired: true}.
21. PUT /api/me {prefs:{set_length:22, difficulty:'hard', format:'grid'}} → 200, and /practice/ then opens with 22, only Hard and Grid-in selected. PUT /api/me {prefs:{colour:'x'}} → 422 naming 'colour'.
22. Theme: a fresh learner's page has no data-theme and getComputedStyle(document.body).backgroundColor is rgb(255, 255, 255). After Settings › Theme › Dark, it is rgb(26, 25, 23), and a reload has no light flash. grep -E '#[0-9A-Fa-f]{3,6}\b' on web/test/index.html, web/me/index.html and web/results/report/index.html finds nothing.
23. New learner a:v2revnew on /me/:
   - The H1 is 'Student XXXX'; the stat tiles show 0 / —.
   - Snapshot shows 'Take the diagnostic', 'Start a module' and 'Answer a question this week to be ranked.'
   - Goals shows 'Build my plan'; Learning preferences shows Questions per set 10 selected.
   - The feed shows 'Start today's set', and all 43 achievements are locked.
   - There are no console errors.
24. Seeded learner a:v2revshellhist on /me/: ANSWERED equals SELECT COUNT(*) FROM attempts WHERE learner=…, and ACCURACY equals round(100*SUM(correct)/COUNT(*)) over rows with disputed=0. The heatmap cell for today has a tooltip with today's questions and minutes.
25. The target quick edit on /me/ saves 700 (PUT /api/me {target:700}). /api/today profile.target and the Plan wizard's step 2 then both show 700. The exam-date popover lists no date earlier than today.
26. Practice rank: two learners with the same exam_date, where the first has more right answers in the last 7 days. The first is #1 of 2 in the 'Sitting …' line. After the second sets board 'hidden', the first's line reads #1 of 1, and the second still sees their own rank.
27. After a learner's 50th answer, the next shell page shows a toast containing 'Questions answered'. After POST /api/me/achievements/seen, the next load shows none. GET /api/me/achievements has answered.earned[0].at equal to the 50th attempt's at.
28. Board privacy: with board 'hidden', GET /api/challenge/board omits the learner from entries and players, but `you` still has a rank.
29. POST /api/share → token. GET /api/shared/{token} with no X-Learner returns stats, and its body contains neither the email nor the learner code. After DELETE /api/share/{token}, GET /api/shared/{token} → 404, and /share/?t= shows 'This link was turned off.'
30. GET /api/me/export returns Content-Disposition: attachment, and its attempts array length equals the DB count. DELETE /api/me {confirm:'DELETE'} leaves 0 rows for that learner in every listed table, and the players count of a challenge board they played is unchanged. Without confirm → 422.
31. A fresh browser whose first page is /test/?s=… ends up with localStorage satf.learner matching ^a:[0-9a-z]{24}$.
32. With /api blocked in the browser, pages show the offline banner 'Can't reach SAT Freshman' with Retry now, and the nav links still work.
33. Classes:
   - POST /api/classes as an unsaved learner → 403 {need:'save'}; as a saved one → {id, code}.
   - Two students join with display names.
   - A fresh 5-question set assignment gives the two students different stems.
   - same:true gives both identical (template, seed) lists.
   - After one student misses a question with a named reason, GET /api/classes/{id}/assignments/{aid} lists that label with members 1.
   - No teacher response contains an email or an 'a:' learner code.
34. GET /api/cal/{token}.ics contains 'RRULE:FREQ=WEEKLY;BYDAY=' and 'BEGIN:VALARM', and matches UI.ics() for the same learner. After DELETE /api/cal it returns 404.
35. /manifest.webmanifest is served and linked from every page, with 192 and 512 icons.
36. Every icon-only button in the shell has an aria-label. The skip link is the first Tab stop and moves focus to main. Every dialog closes on Esc and returns focus to its trigger.
37. PYTHONPATH=. python3 server/test_flow.py passes.

### 3.1.9 This section's open questions

Folded into Part 5 where they need a decision; kept here for context.

- Is SMTP configured for production (SATF_SMTP_*)? Without it, sign-in codes only reach server/outbox/, so email accounts can't work for real students. Pairing codes still work.
- Should we also offer Google sign-in? It needs an OAuth client ID and a privacy review. Or do email codes and pairing suffice?
- Age gate and consent: do we need a parental-consent step before an under-13 student saves an email or joins a class (COPPA)? For classes, is the teacher's school consent enough?
- Photo avatars are left out for minors' privacy (an initial or a topic glyph only). Confirm.
- Who staffs /admin/reports and answers disputes, and which address should SATF_REPORTS_TO be?
- The practice rank uses right answers over a rolling 7 days, which rewards volume. Keep it, or rank by the sum of skill mastery?
- SAT_DATES: the upcoming official 2026–27 dates must be checked against the College Board before shipping. Theirs lists Aug 22, Sep 12, Oct 3, Nov 7, Dec 5, Mar 6, May 1, Jun 5.
- Classes: should a teacher be vetted (e.g. a school email) before seeing minors' names and mistakes, or is any saved account fine for now?
- Should the share view and the teacher roster show the names of open mistakes, or only counts? The spec shows names, because they are the actionable part.
- Email reminders at the preferred time need SMTP and a scheduler. Are calendar alarms enough for now?

---

## 3.2 Today (the dashboard)

> **Spec title:** Dashboard (Today, `/`)  
> **Built by:** S3  
> **Read with resolutions:** R2, R10, R13, R14, R15, R16, R17, R26, R27, R30, R38 (§2.2). Where this spec disagrees with them, they win.

### 3.2.1 What they have

- **Hero banner**: Full-width blue rounded banner. Date eyebrow in caps (WEDNESDAY, SEPTEMBER 23), time-of-day greeting with the full name (Good Morning / Afternoon / Evening, Samandar Norboyev), a monochrome-blue illustration on the right. No stats and no action in it.
- **Two questions of the day, side by side**: One card, two columns visible at once: R&W on the left (whole passage plus question), Math on the right (KaTeX stem, can refer to a figure). Each column has an outline Answer button that opens a modal. The card header has a QOTD streak pill (flame, 1 day). The same questions for every student.
- **QOTD modal**: Dialog Question of the Day with a close X. Stem, choices as full-width rows (muted letter, 1px border, radius ~10). Picking gives a blue border and fill. Footer: More practice text link left, Check answer primary right, disabled until something is picked. After Check: the chosen row turns red or green, an Incorrect/Correct banner, a Show explanation link opens a grey box (Choice A is correct...). The correct choice is NOT highlighted. The primary becomes Done. One attempt only.
- **Study time card**: Two big figures, STUDY TIME TODAY and THIS MONTH (1m / 1h 13m with data). Under them a one-month calendar (Mo to Su, round cells): today filled black, days with activity filled blue, other months faded. Cells are buttons that do nothing. No month navigation. UTC-vs-local bug: a sitting finished 22:14 UTC shows on the 22nd while the Recent Tests card dates it 23/09/2026.
- **Study plan CTA (no plan)**: Full-width card: eyebrow PERSONALIZED CURRICULUM with a target icon, title Build Your Adaptive DSAT Study Plan, two lines of copy, three coloured-dot bullets (Custom daily time pacing / Dynamic score drift adjustments / Scheduled rest days), Build My Plan button. Building uses the one plan the free tier gets per cycle, and their generator failed 3 of 3 times on the re-walk.
- **Today's Plan card (plan exists, from their bundle)**: Title Today's Plan, an All Done badge with an emoji when finished, N of M completed, X min left (Y min total) or All time targets reached, a Full Plan button, and one checkbox row per task (aria Mark task as done). Error toast Could not start task. Please try again.
- **Plan view summaries the dashboard links to (bundle)**: 4 stat tiles: Days to exam (Keep the streak going / Exam day has arrived), Streak (Longest N days), Plan complete % (X of Y tasks), Score gap (1000 now, 1400 target). Week view with a pager (3 / 7) and a This week jump, 7 day tiles with done/total, rest or a dash. Adaptive banners: fallen behind (at least 4 tasks in 7 days and under 60% done) with Rebalance my plan, and score drift up at least 60 with Not now (3h snooze) / Rebuild with these scores. Tasks: Why this task?, Skip, Mark done, Practice again, Undo, Move to a later day of the same week.
- **Score progress**: SCORE PROGRESS big number left, TARGET SCORE big number with a pencil right. Empty copy: Complete a full-length test to start tracking your score. Stayed 0 after a 420 module-selection sitting. Target shows 0 even though the plan wizard set 1400: wizard, dashboard and profile targets are not synced.
- **Target editor**: Pencil opens Set Target Score: SAT scores range from 400 to 1600. Your current score is 1460 (a wrong number), a big number input with placeholder 1500, a 400-1600 bar, Cancel and Save Score (disabled until you type), a close X. Total score only.
- **Exam countdown**: A combobox pill EXAM DATE: 3 OCTOBER 2026 with a calendar icon and chevrons. Its listbox offers 8 official dates (Aug 22 2026, Sept 12, Oct 3, Nov 7, Dec 5, Mar 6 2027, May 1, Jun 5), two already past. Under it a live DD : HH : MM : SS labelled DAYS HOURS MINUTES SECONDS, ticking each second to an unstated time. No custom date.
- **Recent tests taken**: Grid of cards: TOTAL SCORE, date as dd/mm/yyyy, total (420), R&W 200 and Math 220 rows, a full-width Review button. Empty: No completed tests yet. No missed questions, no fix or retake, no in-progress tests.
- **Streaks**: QOTD pill says 1 day while the profile says Streak 0 Days: two numbers that disagree.
- **Shell around the dashboard**: 220px collapsible left sidebar, an Upgrade to Pro card, the user card (popover: My Profile, Send feedback, Sign out), and a draggable floating Add your own word button that covers content.
- **What it lacks**: No single next action (plan CTA, QOTD, countdown and score compete). Cannot resume an unfinished test or set, no mistakes view, no challenge, no per-day detail, no daily goal on the dashboard, no week view, timezone bugs in calendar and study time, targets out of sync.

### 3.2.2 What we have now

Status is have / partial / missing / worse, against theirs.

- **Hero greeting with date**: *missing.* No greeting or name. The only date is the QOTD eyebrow (SEP 23).
- **Next action**: *partial.* The coach's set (topic chips, trap dots, N questions, minutes, Start) or the plan's test on a test day. Better than theirs, which has none. No reason, no count or clock choice, no way to change skills, no resume of an unfinished set or of a running timed test, ignores rest days.
- **Today's plan task list**: *missing.* Nothing lists today's tasks, what is done, or minutes left. Their bundle has a Today's Plan card with N of M, minutes left and All Done.
- **Questions of the day**: *partial.* One multiple-choice question answered inline with one tap, so a misclick loses the day. Feedback beats theirs (key shown, mistake named, rationale, % of N right). Missing: a second question, a QOTD streak, more practice, per-option crowd picks, what each wrong answer means, past days, save, share.
- **Study time today / this month**: *missing.* /api/today has per-day minutes but the page never shows them. Tests and the QOTD add no time: record_paper files ms=None and POST /api/qotd takes no ms.
- **Daily / weekly goal**: *missing.* profile.minutes exists (plan step 3) but no goal is shown anywhere on Today; theirs has Daily 2 Hours / Weekly 12 Hours on the profile.
- **Month calendar**: *worse.* Seven dots for the last seven days with a hover title of question counts. No month, minutes, plan days, exam day or day detail.
- **Study plan CTA / plan status**: *missing.* No plan: only a Set a date link under an empty exam tile. With a plan: no week, no progress, no plan-complete figure.
- **Score progress**: *partial.* The latest band (200-350) with Math · Sep 23. No target, gap, trend, domains, drift. Empty state: a Take a test link. Unlike theirs, a module or the diagnostic does give a score.
- **Editable target**: *missing.* Settable only in plan step 2. Math only, so a student who thinks in a 1600 total has nowhere to put it.
- **Exam countdown**: *partial.* A days number and the date. No date picker, no live clock, no official dates, no study days or tests left, no exam-day or after-exam states.
- **Recent tests**: *missing.* None on Today. /tests/ and /results/ list sittings without missed numbers or Fix.
- **Daily challenge**: *have.* Start/Resume, then #rank and right/asked·time. Theirs has nothing like it. Lacks a board preview, progress and time left while in a sitting, a challenge streak, yesterday's result.
- **Mistakes**: *worse.* A small '23 mistakes' link at the bottom of the right column: the page's strongest asset is its least visible element.
- **Streak**: *partial.* A flame count in the top bar from /api/me days.streak. No best streak. One source, so it cannot disagree like theirs, but nothing else on Today shows it.
- **Diagnostic results gate**: *worse.* latest_score() returns a diagnostic's estimate whether or not it was signed up for, so Today shows a band that /results/report/ still hides behind sign-up (403).
- **Loading / error states**: *worse.* Cards show a bare dash while loading. One 'The server is not answering.' for everything, and the QOTD card silently hides on failure. No retry.
- **Phone layout**: *partial.* One column; Score and Exam tiles stack under the QOTD. No designed priority order.

### 3.2.3 Design

#### Today (`/`), rebuilt

##### Review changes

What the draft still got wrong, and what was changed. The pattern: every time it had to choose, it hid, trimmed or withheld something to look calm, which is the mistake that degraded the site.

**Hidden or cut for looks (reversed)**
1. The two questions of the day were behind tabs, so one was always hidden. Theirs shows both side by side. Now both are side by side at 1080px and wider, and tabs are used only on narrower screens, with a status mark on each tab.
2. "All four choices" sat in a closed `<details>`. Now each option shows, right under its own text after the reveal, what picking it means and how many picked it.
3. The top-3 lists grow: mistakes and the challenge board show 5. Recent tests show 6, with `Show 6 more` loading more in place.
4. The "only one orange pill on the page" rule left a rest day with no primary action. The rule is dropped. On a rest day the pill reads `Practice anyway`. The hierarchy comes from the size and position of Up next, not from withholding colour.
5. The hero chips are kept at every width, and a 4th chip shows plan progress. The draft had left this as an open question.

**Their features the draft left out (added)**
6. Their **Today's Plan** card (from the bundle): the task rows, `N of M completed`, `X min left (Y min total)`, All Done, and Full Plan. It is now a **Today list** inside Up next. Completion is automatic, taken from what the student actually did, so there is nothing to tick and nothing to fake. Each row has a progress count, a `Why` reason, `Skip` / `Undo skip`, and `Move to…` for a test. Students without a plan get a daily list too.
7. Their **total target** is on a 400–1600 scale; ours was Math only. The target dialog now takes an optional R&W score now and an R&W target, so the card can show the SAT total next to the Math band. There is one target field, shared by Today, Plan step 2 and Me. Theirs has three targets that disagree. Save stays disabled until something changes, and the number can be typed as well as dragged.
8. Their **daily and weekly goal** (on their profile) now sits on Today. It sets `profile.minutes`, the same field plan step 3 uses, and the goal bars work without a plan.
9. Their **score-drift banner** now appears in the Score card as `Update your plan's start`, with `Not now`.
10. Their **plan stat tiles and week pager**: the Plan card shows the plan day (`Day 12 of 45`), plan complete %, study days done, and a week pager (`Week 3 of 7`, with a `This week` jump). Each day in the strip is done, partial, missed, skipped or rest. A line appears when the student has fallen behind.
11. **Three separate streaks**, each labelled: study, day's questions, challenge. The study streak comes from one source and reads the same in the bar, the hero, the calendar and Me. Theirs shows 0 on the profile and 1 on the QOTD.

**Things that could not work as written (fixed)**
12. An unfinished **timed test keeps its clock running** on the server (`remaining()` counts wall-clock time). Up next now puts it first with the time left. A timed drill whose clock has run out is no longer offered as `Continue`, because its answers are refused with "time is up".
13. **"Harder, same skill"**: only 59 of 386 templates make more than one difficulty, so a harder version of the same template usually does not exist. It is now `Harder · {topic}`: hard questions from the same topic.
14. **Tapping one mistake** drilled every open mistake in its topic. A new `templates` filter on `POST /api/drill` fixes exactly that one.
15. **Mock misses were split at 22.** They are now split at module 1's actual length.
16. **A `like` drill before answering** could serve the day's own seed and show its key. The drill now requires an answer in that slot first and always excludes the day's seed.
17. **The diagnostic's gate**: Today already shows the band of a diagnostic nobody signed up for, while the report returns 403. Scores, recent tests and Fix now respect the gate.
18. **Midnight**: an answer to a question seen at 23:58 and sent at 00:01 would have been filed as late and cost the streak. There is now a 60-minute grace after local midnight.
19. **The week strip counted a single QOTD tap as a study day done.** Practice-day completion now uses the planned question count.
20. **"Every card fails on its own"** was not true: six cards read the one `/api/today` call. Those cards now each show their own error, and one Retry refetches the call for all of them. The QOTD, calendar, challenge and tests calls stay independent.
21. **`.clock` is defined on /tests/ only.** It moves to ui.css so this page can use it.

**Extras added**
22. `Try one now`: a fresh-seed repair of the top mistake, answered in a sheet without leaving Today.
23. `New one like this` on every test card: a never-seen test of the same shape.
24. A this-week-versus-last-week recap, with the skills that moved most.
25. `Add a score`: log a Bluebook practice test or an official SAT, shown in the trend.
26. An `.ics` export of the SAT date and the study days.
27. A personalised preview on the plan CTA.
28. Yesterday's challenge result.
29. `Report a problem` on the day's questions.
30. The native share sheet on phones, and copy-link on desktop.

**Open questions resolved**
- The second daily question is a grid-in. The personal question is `Try one now`.
- Late answers do move mastery and mistakes.
- The day's questions use a Check step.

---

##### 0. Rules for this page

- Every feature of their dashboard has an equivalent here that does more, and nothing is cut or hidden for looks.
- **Up next** is the page's main action: it comes first, it is the largest element, and its button is the filled pill.
  - Other actions are `.btn`, a new shared secondary button: `--tile-2` fill, 40px tall, 10px radius, 600 14px Archivo, ink text.
  - Lesser links are `.quiet`.
  - Orange also marks what is the student's or what is live: a selected control, the key's crowd bar, goal fills, open-mistake dots.
- Labels (`.k`), units, legends, counts and one line of helper text are used wherever they help a student decide.
- Difficulty is written as a word (`Easy` / `Medium` / `Hard`) with a 3-pip mark (●○○ / ●●○ / ●●●) in ink, never in extra colours.

##### 1. Layout

The content box stays `.page` (max 1120px, `--gutter`). The cards sit in one CSS grid, `#today`, with named areas and a 20px gap.

**Desktop (≥1080px)**, 12 columns:
```
hero  ×12
next  ×8   | mist ×4
qotd  ×12             (the two questions side by side, 6 + 6)
score ×6   | exam ×6
study ×8   | chal ×4
plan  ×12
tests ×12
```

**Tablet (760–1079px)**, 2 columns: `hero hero / next next / qotd qotd / score exam / study study / mist chal / plan plan / tests tests`. The questions of the day use tabs.

**Phone (<760px, designed at 390px)**, one column: hero, next, qotd, exam, score, mist, study, plan, chal, tests.
- Card padding drops to 18px 16px, and touch targets are at least 40px.
- `.page` keeps its 110px bottom padding so the last card clears the tab bar.
- The QOTD uses tabs, and every sheet or dialog opens as a bottom sheet.

**Cards**
- `.card`: `--tile` fill, 14px radius, 22px 24px padding.
- `.card-head`: a flex row with the `.k` label on the left and a meta or action on the right, 14px bottom margin.
- Up next uses `--wash`. The hero has no fill.
- Each card is a `<section aria-label>` with an id that the other cards link to: `#next #qotd #exam #score #study #plan #mist #chal #tests`.

**Loading**: a skeleton (`.sk`, static `--tile-2` blocks) at each card's final height, so nothing shifts when data arrives.

**Errors**
- The cards fed by `/api/today` are next, mist, score, plan, exam, and the hero chips. If that call fails, each of them shows `Couldn't load this.` with a `.btn` Retry. Any one of those Retry buttons refetches `/api/today` and repaints all of them.
- The QOTD, calendar, challenge and tests cards have their own calls, errors and Retry.

---

##### 2. Hero, `#hero`

**Eyebrow**: the local date, upper-cased (`WEDNESDAY, SEPTEMBER 23`), from `Intl.DateTimeFormat('en-US', {weekday:'long', month:'long', day:'numeric'})`, style `.k`.

**Heading** (`h1.h1`): `Good morning, Aziz`.
- Local hours 5–11 give `Good morning`, 12–17 `Good afternoon`, 18–4 `Good evening`.
- With no name, the heading reads `Good morning` and is followed by a `.quiet` `Add your name`.
  - It swaps in an inline field (`.field`, maxlength 24, the same validation as Me), a Save `.btn`, and the helper `Shown on the challenge board`.
  - Enter saves and Esc cancels. Saving sends `PUT /api/me {name}`, then calls `UI.me(true)` so the avatar in the bar updates. Server errors appear inline.

**Status chips** (`.hero-stats`): each is a link to its card, 32px tall, `--tile` fill.
- **Study streak**: flame + `4-day study streak`, adding `· best 9` when the best is higher. At zero it reads `No streak yet`. Links to `#study`.
- **Minutes today**: `38 of 60 min today`, or `38 min today` with no goal. Links to `#study`.
- **SAT**: `SAT in 10 days`. With no date it reads `Set your SAT date`. It turns ink-bold at 7 days or fewer. Links to `#exam`.
- **Plan** (only with a plan): `Plan · 1 of 2 done`, or `Plan · rest day`. Links to `#next`.

**Layout**: at desktop the chips sit right-aligned on the heading's baseline. At phone they wrap under it.

**Better than theirs**: the same greeting and date, with the decorative illustration replaced by four live facts that each lead somewhere.

---

##### 3. Up next and the Today list, `#next`

**Header**: `UP NEXT` on the left. On the right, when a plan is set: `Today in your plan · 60 min`, `Test day in your plan · 70 min` or `Rest day in your plan`.

###### 3a. The next thing, first match wins

**1. A running timed test** (`today.open.test`, timed, `seconds_left > 0`)
- Title `Module in progress`, or `Section · module 2 in progress`.
- Meta `14:22 left · 9 of 22 answered`.
- Helper `The clock keeps running while you're away.`
- Pill `Resume`, which opens `/test/?s=`.
- **When the clock has run out**, the title is `Time's up on module 1`.
  - Module 1 of a section: pill `Continue to module 2`, with the helper `Module 1 is handed in as it stands. Module 2 gets its own 35 minutes.`
  - Otherwise: pill `See results`. Opening the test window hands the module in.

**2. An unfinished drill** (`today.open.drill`)
- The pill is `Continue`, with meta `7 of 38 answered`, or `12 answered` for an endless set.
- A timed set adds `· 6:10 left`.
- The set's own topic chips are shown.
- A `.btn` `Start a new set` reveals the controls below.
- When `today.open.drills > 1`, a `.quiet` `+2 more unfinished sets` links to `/practice/#unfinished`.

**3. A plan test day** (`kind === 'test'`, and the test task is not done)
- Title `Module test` / `Section test`, with meta `22 questions · 35 min` / `44 questions · 70 min`.
- Timed/Untimed toggle (`.clock`, default Timed).
- Pill `Start test`: `POST /api/mock/new {full, timed}`, then `/test/?s=`.
- `.quiet` `I took a Bluebook test instead` opens Add a score (§9). Saving it marks the test task done.

**4. The coach's set**
- **Reason line** (15px, ink), from `coach.why`:
  - `mistakes`: `3 open mistakes in these skills`
  - `new`: `New skills, the biggest domains first`
  - `weak`: `Your weakest skills right now`
  - `review`: `Strong skills you haven't worked on for 10+ days`
  - With a plan focus, it appends `· Algebra is on focus`.
- **Topic chips**: `UI.chip(slug)` on a paper fill, each with its open-trap dots (up to 3) and a 2px mastery bar underneath (`.mbar`). The `aria-label` reads `Probability, 12 answered, 2 open mistakes`.
- **Count**: a `.choices` group of `5 · 10 · 22 · {coach.count} · Endless`, deduplicated. The coach's count is selected. `Endless` sends `count:null`.
- **Clock**: the `.clock` Timed/Untimed toggle, default Untimed.
- **Estimate**: meta `{n} questions · {minutesFor(n)} min`, updated live. Endless shows `as many as you like`.
- **More options**: a `.quiet` link to `/practice/?topics=a,b,c&count=n&timed=0|1`, which opens the builder with this set preselected.
- **Start**: the pill. It sends `POST /api/drill {topics, count, timed, minutes: timed ? minutesFor(count) : null, source:'coach'}`, then goes to `/practice/session/?id=`.

**Rest day**
- Title `Rest day`, with the helper `Your plan has today off. Rest is part of it.`
- The coach's set is shown underneath, and its pill reads `Practice anyway`.

**Goal met** (today's minutes ≥ `profile.minutes`)
- A line with a check: `Today's goal done · 64 of 60 min`.
- The coach's set is still offered, with the pill reading `Keep going`.

**New student**
- The coach's `new` pick.
- A `.quiet` `Or start from a score: Diagnostic · 20 questions · 32 min`, linking to `/diagnostic/`.

**Start fails**: an inline `.error` in the card, `aria-busy` is cleared, and the controls keep their values.

###### 3b. The Today list

The list sits under the next thing, separated by a hairline (`--line`).

**With a plan**, two groups:
- **Plan** header: `PLAN · 1 of 2 done · 22 min left of 60`.
  - When every task is done: `All done for today ✓ · 64 of 60 min`, or `All done · all time targets reached` when minutes ≥ goal.
- **Daily** header: `DAILY`. Its rows are the questions of the day and the challenge. They are not counted in the plan's figures.

**Without a plan**, one group, `TODAY · 1 of 3 done`:
- Rows: the coach's set, the questions of the day, and the challenge.
- A `.quiet` at the end: `Build a plan to set a daily goal`.

**A row, left to right**
- **Status box**:
  - done: an amber filled check,
  - in progress: an ink ring with the fraction filled,
  - to do: an empty ring,
  - skipped: a faint dash, with the row at 55% opacity.
- **Title and type tag**: `Practice set` · `Module test` · `Section test` · `Day's questions` · `Challenge`.
- **Meta**:
  - practice: `14 of 38 questions · 22 min`
  - test: `35 min · timed`
  - day's questions: `1 of 2`
  - challenge: `Not started`, `4 of 10 · 9:12 left`, or `#12 of 124`
- **`Why`**: a `.quiet` toggle that opens one line of reason, and turns into `Hide` while open.
  - Practice: the coach's reason.
  - Test: `Your week's test, on its last study day`, or `A test every study day, as you set it`.
  - Day's questions: `The same two for everyone, one try each`.
- **Action** (`.btn`): `Start`, `Continue`, `Resume`, or `Practice again` once done (a fresh coach set).
- **⋯ menu** (plan tasks only; label `More actions for {title}`):
  - `Skip for today`, or `Undo skip`.
  - On a test only: `Move to…`, listing the later study days up to next Sunday (`Thu, Sep 24`). With none, it reads `No study day left before the exam`.

**Completion rules**: derived from what the student did, so there is no checkbox to forget or to fake.
- **Practice task**: non-test answers today (drill, challenge and day's questions) ≥ the planned count.
- **Test task**: a module or section finished today, or an outside score added for today.
- **Day's questions**: both slots answered.
- **Challenge**: finished.

**Skip and Move**
- Both send `POST /api/plan/mark`.
- A skipped day shows as skipped in the week strip, not as missed.
- A moved test makes today a practice day and makes the chosen day a test day, through the marks in `UI.plan.dayOf`.
- The toasts are polite live-region lines under the list: `Skipped for today · Undo` and `Test moved to Thu · Undo`.
- If a mark fails, the row reverts and shows `Not saved. Try again.`

**Better than theirs**: their list needs manual ticks, and its only reschedule is a later day in the same week. Ours ticks itself from real work, shows progress inside each task, and shares one list with the next action.

---

##### 4. Mistakes, `#mist`

Theirs has no equivalent on the dashboard.

**Header**: `MISTAKES` on the left, `All mistakes` (`.quiet`, to `/mistakes/`) on the right.

**Figures**
- The open count in big type (`.num` 44px), labelled `open`.
- Meta under it: `3 fixed today · 12 this week · 2 new today`.

**Top 5 open traps** (`today.traps.top`, ordered by hits, then by most recent). Each row shows:
- an orange dot,
- the misconception label (`Added the percentages instead of multiplying them`),
- `×3` when hits > 1,
- two owed pips, filled for each clean answer already given (the `.owed` pattern from /mistakes/),
- the topic glyph with its short name in mono 11px.

**Row actions**
- The whole row is a button, `Fix · 2 questions`: `POST /api/drill {mistakes:true, templates:[template]}`, which opens the session.
- The first row also has a `.btn` **`Try one now`**, which opens `dialog.sheet#tryOne`:
  - It sends `POST /api/drill {mistakes:true, templates:[template], count:1, source:'try'}` and renders the question with `UI.question`, answered in one tap like practice.
  - The feedback shows the key, the mistake named, the rationale, and the owed pips updating.
  - Buttons: `Another` (`/drill/{id}/next`, which serves the repair if one is due) and `Done`. `Done` calls `/drill/{id}/finish`, closes the sheet and refetches `/today`.

**Footer**
- `.btn` `Fix all · {templates×2} questions` (`POST /api/drill {mistakes:true}`).
- When more than 5 are open, a link `+18 more` to `/mistakes/`.

**Empty**
- `No open mistakes.`
- The helper: `Every wrong answer lands here under the mistake it names, and leaves after two clean answers.`
- A `.quiet` `Practice` link to `#next`.

---

##### 5. Questions of the day, `#qotd`

Theirs gives one R&W and one Math. We have no R&W bank, so ours are **one multiple-choice and one grid-in Math question**. That covers both SAT Math formats, and grid-in entry rules are where points leak unnoticed. Both are the same for every student on the same local date.

###### Header
- Left: `QUESTIONS OF THE DAY` · `Wed, Sep 23`.
- Right: the day's-question streak, a flame with `3 days in a row`, or `Start a streak`. The `aria-label` reads `Day's questions streak, 3 days`.

###### Desktop (≥1080px): two columns, both visible
- Each column has a slot label with its status mark: `MULTIPLE CHOICE` / `GRID-IN`, with a hollow ring when unanswered, an amber filled check when right, an ink cross when wrong.
- Then the question.

###### Below 1080px: tabs
- A `role=tablist` with the same two labels and marks.
- It opens on the first unanswered slot.
- Left and right arrow keys switch tabs.

###### The question (shared `UI.question`)

**Skill line**: glyph, topic short name, `· Medium ●●○`, and the skill label (e.g. `Percent of a percent`).

**Body**: the figure or table, then the stem in Source Serif 4.

**Multiple choice uses confirm mode**
- A tap selects (`.picked`), and a `.btn` `Check` appears under the options. Tapping another option moves the selection.
- A–D or 1–4 select while the column has focus-within, and Enter checks.
- The reason: one attempt a day, so a misclick must not lose it. Theirs has the same Check step.

**Grid-in**
- The input, Check and the answer-preview line.
- Placeholder `e.g. 2/3, -1.5, 460`.
- A `.quiet` `Grid-in rules` opens the SAT's entry rules in a popover: up to 5 characters for a positive answer and 6 for a negative one, fractions or decimals, no mixed numbers.

**Timing**: `ms` is measured from first render to Check and sent with the answer.

###### After answering, in order
1. **The key is highlighted**, and the student's wrong pick is struck.
   - The named mistake is shown.
   - The rationale is open when the answer was wrong, and behind `Why` when it was right.
   - Theirs never shows the key.
2. **Every option explained and counted.** Each option row gets two additions.
   - A second line in 13.5px ink-soft: `Correct` for the key, and each distractor's misconception for the others (from `choices_explained`, e.g. `Took 70% of 75 as 70 − 75`).
   - A thin bar along the row's bottom edge, amber on the key and ink at 15% on the others, with `23%` in mono at the right.
   - The summary line: `62% of 1,204 got it right · most common trap: B (23%)`.
3. **Grid-in crowd**:
   - `% right`, then `Most common wrong answers: 14 (9%) · 1.4 (6%)`, with values grouped after normalising (`0.5` = `1/2`).
   - With fewer than 5 answers the line reads `You're one of the first 4 today`, and no per-option percentages are shown.
4. **Actions row** (`.btn`s):
   - `5 more like this`: `POST /api/drill {like:{day, slot}, count:5}`. The same template on fresh seeds, then the session page.
   - `Harder · Percentages`: `POST /api/drill {topics:[q.topic], difficulty:['hard'], count:5}`. When the day's question is already hard, it reads `More hard · Percentages`.
   - `Save` / `Saved`: a bookmark toggle, `POST /api/saved {qotd:day, slot, on}`.
   - `Share`: `navigator.share` on a coarse pointer when available. Otherwise it copies `{origin}/?day=YYYY-MM-DD` and shows `Link copied`; if the copy fails, the URL is selected in a read-only field.
   - `Report a problem`: the shared report sheet, from the Session section.

###### Past days strip (card footer)
- `PAST DAYS`, then 7 buttons for the 7 days before today. Each shows a weekday letter and two mini marks (MC, grid-in): amber filled for right, an ink stroke for wrong, hollow for not answered.
- `Older…` opens a date input, allowing up to 30 days back.
- A day opens **archive mode**:
  - The header date becomes `Tue, Sep 22`, with the tag `Late · not counted in the crowd or streak`.
  - A `.quiet` `Back to today` appears.
  - The body is the same, and the crowd shown is that day's on-time crowd.
- Loading the page with `?day=` opens archive mode. A day more than 30 days back, or in the future, falls back to today with the note `That day is out of range. Here is today's.`

###### States
- **Loading**: skeletons of the slot labels, 3 stem lines and 4 option rows per column.
- **Load error**: `Couldn't load today's questions.` with a Retry.
- **Answer failed**: `ctrl.unlock()`, the selection is kept, and an inline `Not sent. Try again.` appears.
- **Midnight rollover while open**: a 60-second check of the local date. When it changes, the page refetches everything and shows the note `It's a new day. Here are today's questions.`
  - An answer to yesterday's question sent within 60 minutes after local midnight counts on time for that day, crowd and streak included.
  - Later than that, it is filed as late.

---

##### 6. Study time and calendar, `#study`

###### Figures, a row of four
- `38m` **Today**, then `31 questions · 71% right`. With a goal, `of 60m` and a 4px amber goal bar. On a plan rest day it reads `Rest day`.
- `2h 5m` **This week** (Monday to Sunday). With a goal, `of 5h` and a bar; the weekly goal is the minutes times the study days.
- `4h 12m` **This month**.
- `9` **Active days** this month.
- Durations use `UI.dur(min)`: `0m`, `45m`, `1h 12m`.

###### Daily goal (`.quiet` `Set a daily goal`, or `Goal 60 min ✎`)
- A popover with `.choices` `15 · 30 · 45 · 60 · 90 · 120 · 180 · 240 min`.
- It sends `PUT /api/me {minutes}`, the same field as plan step 3.
- The helper line: `Your plan uses this as a study day's length.`

###### What counts as study time (server)
- Drill and challenge answer times, each capped at 10 minutes.
- The day's questions' answer times.
- Every finished test sitting's elapsed time, capped per module at the module clock plus 1 minute (90 minutes when untimed).
- Everything is counted on the student's local day (`X-Tz`), which fixes their timezone bug.
- `days`, `/api/today`, `/api/calendar` and `/api/me` all use this one function, so every number agrees.

###### Month calendar (the shared `UI.calendar`, also used by /plan/)

**Header**: `September 2026` with ‹ › buttons.
- Back stops at the month of the first activity.
- Forward stops at the exam's month, or the current month without an exam.
- `Today` jumps back when the calendar is showing another month.

**Grid**: `Mo Tu We Th Fr Sa Su`, 40px cells (34px at 390px), 6px radius.

**Heat**, from that day's minutes:
- With a goal: under 50% of it, 50% to under 100%, and 100% or more.
- Without a goal: 1–14, 15–44 and 45+ minutes.
- The three levels are `--wash`, `--wash-2`, and `--amber` with ink-deep text.

**Other marks**
- Today: a 1.5px ink ring.
- Days from other months: `--faint`.
- Plan days: a 5px dot for practice, a 6×4 square for a test, and a skipped day's dot with a slash.
- The exam day: an amber outline and `SAT` in 9px mono.
- `aria-label` on every cell, e.g. `Mon Sep 21, 42 minutes, 31 questions, 71% right`.

**Legend**, mono 11px: `Less ▢▢▢■ More · • study day · ▪ test day · SAT`.

**Day detail**: an inline panel, to the right of the grid at desktop and under it at phone. Today is selected by default, and a tapped cell gets an amber ring.
- **A past day or today**: `Mon, Sep 21 · 42 min · 31 questions · 71% right`, then that day's sittings as links.
  - They read `Practice · 10/12`, `Module · 520–600`, `Challenge · #4 · 9/10` or `Day's questions · ✓ ✗`.
  - With a plan, the day's state: `Plan: done` / `partial` / `missed` / `skipped`.
  - An empty day reads `Nothing that day.`
- **A future plan day**: `Planned · Practice · 38 questions` or `Planned · Module test`, plus `Open in plan` (`/plan/?day=`).
- **Keyboard**: roving focus with the arrow keys, Home and End for the ends of the week, Page Up and Page Down for the month. Enter selects.

###### This week vs last
- A row of deltas: `124 questions (+30) · 71% right (+4) · 3h 10m (+45m) · 6 fixed · 2 new mistakes`.
- **Moved**: up to 3 topics that rose and 2 that fell, where mastery changed by at least 0.05 since Monday, e.g. `Percentages ▲ · Circles ▲ · Probability ▼`. Each is a chip linking to `/practice/?topics=`.

**Footer**: `4-day study streak · best 9`.

**New student**: every figure reads `0m`, today is ringed, and the day detail reads `Your first answer starts the streak.`

---

##### 7. Daily challenge, `#chal`

**Header**: `DAILY CHALLENGE` on the left, `124 in today` on the right.

**Body**
- `10 questions · 16 min · the same for everyone · ranked by right answers, then time`.
- The top 5 from the board: rank, name, right/10, mm:ss.
- Once the student has finished, their own row is added, highlighted with `--wash` and an amber edge.

**Action by state**
- **Not started**: `.btn` `Start` (`POST /api/challenge/start`, then the session page).
- **In progress**: `.btn` `Resume · 4 of 10 · 9:12 left`.
- **Time's up**: `.btn` `See your result`.
- **Finished**: a big `#12`, meta `of 124 · 8/10 · 11:32`, and a `.quiet` `Full board` to `/challenge/`.

**Footer**
- `3-day challenge streak` when it is 2 or more.
- `Yesterday: #4 of 30 · 9/10`, linking to `/challenge/?day=`.

**Error**: `Couldn't load the challenge.` with a Retry.

---

##### 8. Plan, `#plan`

###### No plan, or the exam has passed

A full-width CTA:
- Eyebrow `STUDY PLAN`, title `Build your study plan`.
- The four steps as a numbered row, each a link to its step (`/plan/?step=N`): `1 Where you are · 2 Where you're going · 3 Time you have · 4 What to focus on`.
- **Preview from the student's own data**, when there is any: `Starts from 520–600 · first up: Probability, Nonlinear functions · 29 open mistakes to fix`.
- Three bullets:
  - `A set for every study day, picked from your results`
  - `Rest days you choose, and a test each week or every day`
  - `Redrawn every day, so a missed day never piles up`
- Helper `About a minute. Change it any time. Free, as many as you like.`
- `.btn` `Build my plan →`.

###### Plan set

**Header**: `YOUR PLAN` on the left. On the right: `Open plan` · `Change plan` (`/plan/?edit=1`) · `Add to calendar`.

**Stat row**, four compact figures:
- `Day 12 of 45`
- `20% done · 9 of 45 study days`
- `10 days to the SAT`
- `+140 to target`, with `560 → 700` under it

**Week strip**
- A pager: ‹ `Week 3 of 7` ›, with a `This week` jump when viewing another week.
- 7 columns, Monday to Sunday. Each column has:
  - the weekday and date,
  - a kind mark: a practice circle, a test square, a rest dash, or the amber SAT,
  - a state:
    - done: filled,
    - partial: an arc showing the fraction of the planned count,
    - missed: a hollow faint mark on a past study day with nothing done,
    - skipped: a dash through the mark,
    - future: an outline,
  - an ink ring on today,
  - the planned load: `38q` or `Module`.
- Tapping a day selects it in the calendar (§6) and scrolls to it.

**Row under the strip**
- `Next test: Fri · Module`.
- `Focus: Algebra · Geometry & Trig` when any domain is on focus.

**Behind**: shown when 2 or more of the last 7 study days were missed (skipped days don't count). It reads `2 study days missed this week. Nothing piles up: each day is redrawn from your results. If the days are too long, shorten them.` with the `.btn` `Change daily time` (`/plan/?step=2`).

**Add to calendar** builds an `.ics` file in the client:
- An all-day `SAT` event on the exam date, with an alarm at 18:00 the evening before.
- When a plan is set, a weekly repeating event on the study days (`BYDAY` from `profile.days`) at a time the student picks (default 17:00), lasting `profile.minutes`, until the day before the exam.
- The file is downloaded as `sat-freshman.ics`.

---

##### 9. Score, `#score`

**Header**: `SCORE` on the left, `Target 700 ✎` (`.quiet`) on the right.

**Band**
- The latest band in `.num` 48px, e.g. `520–600`.
- Meta `Math · Section · Sep 21`, linking to that report.
- When the band is capped: `Capped at 580: module 2 was the easier one`.

**SAT total** (when `rw_now` is set): `SAT total 1130–1210 · R&W 610 (yours)`, and `Target 1400` when `rw_target` is set. Without an R&W score it shows a `.quiet` `Add your R&W score for a total`.

**Scale bar**
- 200 to 800 across the card, 8px, on a `--mat` track.
- The band is an ink-30% segment with a 6px dot at its middle.
- The target is a 2px amber tick labelled `700`. The plan's start is a faint tick labelled `Start 560`.
- The ends read `200` and `800` in mono.

**Gap**
- `+140 to target · about 20 a week` = (target − band middle) ÷ weeks to the exam. Without a date, the pace is dropped.
- At or past the target: `At your target ✓`.

**Drift** (plan set; the mean middle of the last 3 scores, counting added Math scores, differs from `profile.current` by 30 or more)
- `Your last 3 tests average 610; your plan started from 560.`
- `.btn` `Update the plan's start to 610` sends `PUT /api/me {current:610}`.
- `.quiet` `Not now` hides the line until a newer score arrives (localStorage `satf.drift.{newest session id}`, try/catch).

**Trend** (`UI.bandChart`, lifted from the /results/ chart)
- The last 8 scores, 72px tall: bands as bars with their middles joined, the newest in amber, and a dashed amber target line.
- Added scores are hollow ink diamonds.
- Legend: `▮ our tests · ◇ Bluebook / official · -- target`.
- With 1 score: `1 scored sitting`. The trend links to `/results/`.

**Domains**
- 4 rows: the domain's short name, its mastery bar, `71% right of 120` in mono, and an orange dot with a count when it has open traps.
- Each row links to `/practice/?domain=`.
- The domain with the most traps gets the tag `Most points to fix`.

**Actions**: `.quiet` `Add a score`.

###### Target dialog, `dialog.sheet#targetSheet`
- Title `Target`, subtitle `Math, 200 to 800`.
- **Math target**:
  - a number input (type=number, step 10, 200–800) kept in sync with a range slider,
  - quick `.choices` of `500 550 600 650 700 750 800`.
- The reference line `Latest 520–600 · Plan start 560`.
- The note `Below your latest band` when the target is under the band's low end. It is still allowed.
- **SAT total (optional)**: `R&W now` and `R&W target`, each 200–800 in steps of 10, with the helper `We only test Math. Add your R&W from Bluebook or a real SAT to see your total.` With both set, a live `Total target 1400`.
- **Buttons**: `Clear target` (`.quiet`, left), `Cancel` (`.quiet`), and `Save` (`.btn`, disabled until something changes).
  - Save sends `PUT /api/me {target, rw_now, rw_target}` and repaints the card, the plan card and the hero without a reload.
- **Used everywhere**: the same `profile.target` is read by Plan step 2 and Me.
- Esc or a backdrop click cancels, and focus returns to the pencil.

###### Add a score, `dialog.sheet#scoreSheet`
- Source, a `.choices` group: `Bluebook practice test · Official SAT · Other`.
- The date, a date input no later than today.
- `Math`, required, 200–800 in steps of 10. `R&W`, optional.
- `Save` sends `POST /api/scores`.
- `Scores you added` lists them under the trend, each with × to delete (confirm: `Delete this score?`).
- When the student has no `rw_now`, a saved R&W offers `Use 610 as your R&W now`.

###### Empty (no scored sitting)
- `No score yet`. With a plan's `current`, `Your estimate: 560` appears faint on the scale.
- `.btn`s: `Module · 22 questions · 35 min` (`POST /api/mock/new {full:false}`) and `Diagnostic · 20 questions · 32 min` (`/diagnostic/`), plus `Add a score`.
- The target stays editable.
- Any module, the diagnostic, or an added score gives a score. Theirs needs a full test.

---

##### 10. SAT countdown, `#exam`

**Header**: `SAT` on the left. On the right, a date trigger: `Sat, Oct 3, 2026 ▾` (`aria-haspopup=listbox`).

###### Date popover (`UI.popover`, a bottom sheet under 760px)
- Only the **upcoming** official dates from `UI.SAT_DATES` (moved out of /plan/). Each reads `Oct 3, 2026 · Sat · in 10 days`, with a check on the current one.
- A divider, then `Another date…`, which reveals `<input type=date min=today>`.
- `Remove date`.
- Choosing sends `PUT /api/me {exam_date}` and repaints the countdown, the plan card, the hero and the score pace.
- **Keyboard**: up and down arrows move, Enter chooses, and Esc or an outside click closes and returns focus. Their popover ignored Esc.

###### Live countdown
- Four boxes, `DD : HH : MM : SS` (`.num` 56px, 40px at phone, tabular), labelled `DAYS HOURS MIN SEC` in `.k`. Days use 3 digits at 100 or more.
- It counts to 08:00 local time on the exam date, with the caption `to 8:00 AM, when doors close`.
- It ticks on a timer aligned to the second and pauses while the page is hidden.
- `role=timer` with `aria-live=off`, plus a visually hidden sentence: `10 days until your SAT on Saturday, October 3`.

###### Plan line
- `7 study days and 1 test left in your plan`, counted with `UI.plan.dayOf`, marks included.
- With no plan: `Build a plan for these 10 days` → `/plan/`.
- `Add to calendar`: the same `.ics` as §8.

###### Test-day checklist (7 days or fewer left)
- A `<details>`, open on the exam's eve and on exam day. Its checkboxes:
  - `Bluebook installed and updated`
  - `Exam setup done in Bluebook (it gives you your admission ticket)`
  - `Admission ticket`
  - `Acceptable photo ID`
  - `Pencils or pens for scratch work`
  - `Device charged, charger packed`
  - `Calculator, optional: Desmos is built in`
- A count in the summary: `Test-day checklist · 3 of 7`.
- Ticks are stored in localStorage `satf.checklist.{exam_date}`, with try/catch.

###### States
- **No date**:
  - The title `When is your SAT?`.
  - The next 4 official dates as one-tap `.choices`.
  - `Another date`.
- **Exam day**:
  - `Today. Doors close at 8:00 AM.`
  - The checklist open.
  - Meta `Good luck`.
- **Passed**:
  - `Your SAT was Oct 3.`
  - `.btn` `Add your official score` (Add a score, source Official).
  - `Pick your next date`, with the next official date preselected in the trigger.
  - The plan card shows its CTA until a new date is set.

---

##### 11. Recent tests, `#tests`

**Header**: `RECENT TESTS` on the left, `All tests (N)` → `/tests/` on the right.

**Layout**: 3 per row at desktop, 2 at tablet, a stacked list at phone.
- Every open test comes first, then the 6 newest finished ones.
- `.btn` `Show 6 more` loads the next page in place (`offset`).

###### Open test card (amber inside edge, `IN PROGRESS`)
- `Section · module 2` / `Module` / `Diagnostic`.
- `14:22 left · 9 of 22 answered`, or `Untimed · 9 of 22 answered`.
- `.btn` `Resume`.
- When the time is up, it reads `Time's up`, with `Continue to module 2` or `See results`.

###### Finished test card (the shared sitting card)
- **Top line**: `Sep 21 · Section · 44 questions`.
- **Score**: the band in `.num` 34px, e.g. `520–600`, with the route tag `Harder module 2`, or `Easier module 2 · capped 580`.
- **Meta**: `31/44 right · 64 min`.
- **Mini scale**: 200–800, with the band and the target tick.
- **Missed questions**, one row per module: `M1` then chips of question numbers.
  - A wrong answer is a filled chip and a blank is an outlined chip.
  - Up to 10 are shown, then `+N`.
  - The legend reads `■ wrong ▢ blank`.
  - Each chip links to `/results/report/?id=…&q=M1-3`.
- **Footer**:
  - `.btn` `Review` → `/results/report/?id=`.
  - `.btn` `Fix 13`: `POST /api/drill {from_session:id}`, the misses as fresh questions on the same templates.
  - `.btn` `New one like this`: `POST /api/mock/new {full: kind==='mock'}`, a never-seen test of the same shape.
  - With no misses, Fix is hidden and `All right` is shown.

###### Diagnostic not signed up for
- `Diagnostic · Sep 21`, then `Sign up to see your results`, linking to `/diagnostic/signup.html?s=`.
- No band, no misses and no Fix, which matches the report's gate.

###### Empty
- `No tests yet.`
- `.btn` `Module · 22 questions · 35 min`, `.btn` `Section · 44 questions · 70 min`, and `Add a score`.

---

##### 12. Data and refresh

**On load, in parallel**
- `/api/today`
- `/api/qotd`, or `/api/qotd?day=` in archive mode
- `/api/calendar?month=YYYY-MM`
- `/api/challenge`
- `/api/tests/recent?limit=6`

Each card paints when its own call resolves. The hero's date and greeting paint from the client clock before any call returns.

**After a day's-question answer**: `UI.me(true)` (the bar's streak), then refetch `/today` (minutes, the Today list and the hero chips), then patch today's calendar cell and the day detail.

**On return**
- On `visibilitychange` to visible, and on `pageshow` from the back-forward cache: refetch `/today`, `/challenge` and `/tests/recent`.
- If the local date has changed: refetch everything.

**Timezone**
- Every call sends `X-Tz`. Every "today", "this week" and "this month" is computed by the server in that zone.
- The countdown and the greeting use the client clock.

**One source per number**
- The study streak, minutes and questions come from `progress.days`.
- The target comes from `profile.target`.
- The plan day kinds come from `UI.plan.dayOf(d, profile, marks)`.

---

##### 13. States matrix

| state | what Today shows |
|---|---|
| brand-new (no attempts, no profile) | Greeting + `Add your name`; chips `No streak yet · 0 min today · Set your SAT date`; Up next = coach `new` pick + Diagnostic link; Today list `0 of 3`; both day's questions; Mistakes empty helper; calendar empty, today ringed; Challenge Start + board; Plan CTA (no preview); Score `No score yet` + doors; Countdown `When is your SAT?`; Tests empty + doors |
| some practice, no plan, no test | reason `mistakes`/`weak`; Today list with coach set progress; Mistakes top 5; heat; week recap; Score empty with doors; Plan CTA with preview |
| plan set, practice day | header plan context; Plan group `N of M · X min left`; goal bars; week strip with states; stat row; countdown plan line |
| plan test day, not tested | Up next = Start test (Timed) + `I took a Bluebook test instead`; Today list test row with Move to… |
| plan rest day | `Rest day` + pill `Practice anyway`; Plan group `rest day`; goal figure `Rest day` |
| plan all done | `All done for today ✓ · 64 of 60 min`; pill `Keep going` |
| running timed test | Up next = `Resume · 14:22 left`; Tests shows the IN PROGRESS card first |
| timed test out of time | Up next `Time's up on module 1` + `Continue to module 2` / `See results` |
| unfinished drill | Up next `Continue · 7 of 38 answered` (+ `+N more unfinished sets`) |
| behind (2+ missed study days in 7) | Plan card behind line + `Change daily time` |
| score drift ≥ 30 | Score card drift line + `Update the plan's start` / `Not now` |
| lots of history | Mistakes top 5 + `+N more`; score trend 8 points; calendar back to first activity; tests 6 + `Show 6 more` + `All tests (N)`; week pager across the plan |
| exam ≤ 7 days | checklist; hero SAT chip ink-bold |
| exam day | `Today. Doors close at 8:00 AM.`, checklist open |
| exam passed | `Your SAT was …` + `Add your official score` + next date; Plan CTA returns |
| diagnostic not signed up | tests card `Sign up to see your results`; the score ignores it |
| `/today` fails | next, mist, score, plan, exam, hero chips each show `Couldn't load this.` + Retry (one refetch); QOTD, calendar, challenge, tests unaffected |
| another call fails | only that card shows its error + Retry |
| site storage blocked | shell's existing notice; checklist ticks and drift snooze just don't persist |

---

##### 14. Accessibility and motion

- Each card is a landmark `section` with an `aria-label`.
- The tabs use `role=tablist` and arrow keys.
- Dialogs are `<dialog>`, which traps focus and returns it to the opener.
- The popover is a `listbox` with `aria-activedescendant`.
- Calendar cells are buttons with full `aria-label`s, so heat is never the only signal.
- Status boxes carry text: `Done`, `14 of 38`, `Skipped`.
- Verdicts keep `role=status`. The countdown is not announced every second.
- Motion is entry only (`.rise`, staggered by row), and nothing loops. `prefers-reduced-motion` turns off the rises and the count-up.
- Touch targets are at least 40px at phone width.

### 3.2.4 Extras: what they missed

- **Today list that ticks itself**: Their Today's Plan card needs manual checkboxes (easy to forget, easy to fake). Ours marks a task done from what the student actually did, shows progress inside each task (14 of 38), and works for students without a plan too.
- **Every option explained and counted after the day's questions**: Item.reasons names the misconception behind each wrong option, so each option row shows both what picking it means and how many picked it (23% took 70% of 75 as 70 - 75). A bank without labelled distractors can only report % right.
- **5 more like this / Harder in the same topic from the day's question**: The same template on fresh seeds never runs out, so a student who misses the day's question can drill that exact pattern at once. Their More practice goes to a generic bank.
- **Grid-in of the day next to the multiple-choice one**: It fills their two-question slot honestly without an R&W bank, and covers the SAT's other Math format, where entry rules cost points that multiple-choice practice never exercises.
- **Past days of the day's questions (30 days, shareable ?day= link)**: A day's question is regenerated from the date, so a missed day stays available and a link shows a friend the same question.
- **Try one now: a fresh-seed repair of the top mistake in a sheet**: The student closes a named mistake without leaving Today. Only a generator can make a new question of that exact misconception on demand.
- **Running timed test first in Up next**: The server clock keeps running while the student is away; Today says so and leads them back with the time left. Theirs lists nothing to resume.
- **Fix N and New one like this on every test card**: Misses become fresh questions on the same templates in one tap, and a never-seen test of the same shape is always available. Their card only offers Review.
- **Missed question numbers per module, wrong and blank told apart, each linking to its review**: Their list mixes wrong and unanswered in one red chip and the chips are not clickable.
- **Mistakes card with named misconceptions, hit counts and owed pips**: Our strongest asset on the home page: what keeps catching you, and how close each mistake is to closed.
- **Tap a calendar day for its detail, with plan state**: Minutes, questions, accuracy, that day's sittings as links and whether the plan day was done, partial, missed or skipped. Their cells are buttons that do nothing.
- **Daily goal settable on Today, with goal-relative heat and weekly goal**: Study time means something against the student's own goal, and it is the same field the plan uses.
- **This week vs last week, with the skills that moved**: Mastery is recomputable at any point in time from attempts, so the page can say Percentages went up and Probability slipped this week. Theirs has no week at all on the dashboard.
- **Plan week strip with done / partial / missed / skipped, a week pager, plan-complete % and a behind line**: It shows at a glance whether the student is on pace, and says what to change, without the fake-progress build screen theirs shows.
- **Move a test day and skip a task from Today**: Real schedules change. Theirs can only move a task to a later day in the same week, and only from the plan page.
- **Score scale with band, target, plan start, pace, drift prompt and trend**: It answers how far am I, how fast must I move, and whether the plan's start is stale. Theirs shows 0 until a full test and a target dialog that contradicts it.
- **SAT total from an optional R&W score, and one target shared everywhere**: Students think in a 1600 total. Ours shows it next to the Math band, and the target cannot drift between pages as theirs does.
- **Add a score (Bluebook practice test or official SAT)**: Many students also take Bluebook tests; logging them puts real scores on the trend, can mark a plan test day done and can calibrate the plan's start.
- **Countdown to doors-close with study days and tests left, upcoming official dates only, custom date, .ics export**: Their picker offers passed dates and no custom date. Ours turns days into plan units and puts the SAT and study days in the student's own calendar.
- **Test-day checklist in the final week**: Practical logistics students forget (Bluebook exam setup, admission ticket, ID), stored per exam date.
- **Daily challenge on Today with top 5, time left, challenge streak and yesterday's result**: A fair shared contest every day costs nothing because the ten questions are generated from the date. Theirs has no live contests.
- **Three labelled streaks from single sources**: Their profile and QOTD disagree about one streak. Ours shows study, day's-questions and challenge streaks, each named and each consistent across pages.
- **Personalised plan CTA preview**: Before building, the student sees where the plan would start and what it would put first, from their own results.
- **Per-card loading and errors with Retry; midnight rollover with a grace hour**: One failed call never blanks the page, a tab left open overnight moves to the new day, and a question seen at 23:58 still counts.

### 3.2.5 Server changes

Tables and columns here are added by F4 as listed in §2.5; the drill fields map through §2.6; prefs through §2.7.

- **progress.days: one source of daily study figures**

  Per local day (X-Tz):
  - questions, right
  - practice: non-test answers (drill, challenge, qotd)
  - tests: finished mock/module/diagnostic sittings
  - qotd: {mcq, spr}
  - minutes

  Minutes are attempt ms capped at MS_CAP, plus finished sittings' elapsed time:
  - mock: min(module_started − started, 35m + 60s) + min(finished − module_started, 35m + 60s)
  - module: min(finished − started, 35m + 60s)
  - diagnostic: min(finished − started, 20×95s + 60s)
  - untimed cfg: each module capped at 90m

  The time goes on the local day of `finished`. Test attempts carry ms=None, so nothing is counted twice.

  Also returns:
  - `streak`
  - `best` (the longest run of consecutive active days)
  - `recent`, extended to cover the plan week pager: today − 13 through today

  /api/me, /api/today and /api/calendar all call this function, so the bar, the hero, Me and the calendar agree.

- **GET /api/today: new fields**

  Existing fields stay.
  - `study`: {today, week, month, active_days_month, questions_today, right_today} in minutes; the week is Monday to Sunday.
  - `days.best`, and the richer `days.recent` rows.
  - `scores`: the last 8 estimates, newest first, `[{low, high, kind, session, at, capped, route}]`. Diagnostics with no user_id are excluded (the report's gate). latest_score gets the same filter.
  - `outside`: added scores, newest first.
  - `domains`: `[{domain, mastery, answered, right, traps, topics:[{topic, mastery, answered, traps}]}]` from a new `progress.domains()`. Domain mastery is the mean over the topics that have been answered.
  - `traps`: {open, templates, fixed_today, fixed_week, opened_today, top:[{label, topic, template, hits, owed, last}] (5, by hits then last)}.
  - `open`:
    - `drill`: the newest kind='drill' with finished NULL, started within 36h, ≥1 answer, source not 'try', and not overtime; {id, topics, answered, total, timed, seconds_left, started}.
    - `drills`: the count of the other such drills.
    - `test`: the newest unfinished mock/module/diagnostic: {id, kind, module, answered, asked, timed, seconds_left}.
  - `week`: {this:{questions, right, minutes, fixed, opened}, last:{…}, moved:[{topic, before, now}]}. `before` is mastery_of over the attempts before local Monday. Up to 3 risers and 2 fallers with |Δ| ≥ 0.05.
  - `plan_marks`: marks from today − 13 through the exam date.

  `mistakes` (int) stays for compatibility.

- **GET /api/calendar?month=YYYY-MM (new)**

  Response: `{month, today, first_active, days:[{day, questions, right, minutes, practice, tests, qotd:{mcq, spr}, sittings:[{id, kind, right, asked, estimate, rank, gated}]}], totals:{minutes, questions, right, active_days}}`.
  - Every day of the month in the X-Tz zone.
  - `rank` only for challenge sittings.
  - A diagnostic with no user_id is listed with `gated:true` and no estimate.
  - 422 unless the month matches ^\d{4}-(0[1-9]|1[0-2])$ and lies between 2020-01 and today + 12 months.

- **daily.question(day, fmt)**

  `fmt='mcq'` keeps today's pick and its session `qotd:{day}`, so history stays valid.
  `fmt='spr'`:
  - The pool is the templates whose `blueprint.abilities()` include 'spr' (153 of 386).
  - Hash salt `qotd-spr:{day}`.
  - Templates in the same domain as that day's mcq are skipped.
  - Seeds are walked until `item.fmt == 'spr'`, as draw_matching does.
  - `q['id'] = 'qotd-spr'`, session `qotd-spr:{day}`.

- **GET /api/qotd reshaped**

  Response: `{day, late, streak, slots:[{slot:'mcq', question, mine}, {slot:'spr', question, mine}], past:[{day, mcq, spr}] (the 7 days before)}`.
  - `question` is drill.public() output: no key, rationale or reasons.
  - `mine` is null until answered. For an answered slot, the question is rebuilt from the attempt's own (template, seed), so a bank change can't swap what the student saw.
  - `?day=YYYY-MM-DD` from today − 30 up to yesterday gives that day with late:true. Anything else is 422.
  - `streak`: consecutive days ending today or yesterday with at least one on-time answer (graced answers included).

- **POST /api/qotd: slot, ms, grace, late answers, richer feedback**

  Body: `{answer, day, slot:'mcq'|'spr', ms}`.

  **Routing**
  - `day == today` is on time.
  - `day == yesterday` within 60 minutes after local midnight is on time for that day.
  - Other days from today − 30 are late, filed under `qotd-late:{slot}:{day}`.
  - A future day is 422. This replaces the 409.

  **Filing**
  - Still `once=True`, so a double POST returns the first answer.
  - Filed through progress.record, so mastery and traps move for late answers too.
  - `db.remember(learner, [{key, seed, stem_hash}])`, so the day's seed is never served again.

  **Feedback** adds:
  - `slot`, `late`
  - `choices_explained`: 4 entries for mcq; null for the key, else the capitalised reason
  - `crowd`: {answered, right, picks:[n,n,n,n] (mcq), top_wrong:[{value, n}] (spr, top 3, values normalised with scoring's grid rule)}

  The crowd counts on-time sessions only, and is returned only once this learner has answered.

- **POST /api/drill: like, templates, count in mistakes mode**

  **`like: {day, slot}`**
  - 409 'answer it first' unless this learner has an attempt in that slot's session (on time or late).
  - 404 outside today − 30 to today.
  - The server regenerates the day's question, then queue = [template] × count (default 5, 1 to 20), topics = [topic], source = 'qotd'.
  - The day's own seed is always excluded, and the key never leaves the server.

  **`templates: [..]`** (mistakes mode): only the open traps on those templates, twice each. `count` (optional) truncates the queue, so the Try-one sheet sends count 1.

  source 'try' sets are excluded from open.drill.

- **POST /api/saved: save a day's question**

  Accepts `{qotd: day, slot, on}` in place of session/question_id.
  - Allowed only after this learner has an attempt in that slot (on time or late); otherwise 409 'answer it first'.
  - Stored as the (template, seed) that regenerates the question.

- **GET /api/tests/recent?limit=6&offset=0 (new)**

  Response: `{open:[…], recent:[…], total}`.
  - `open`: `{id, kind, module, answered, asked, timed, seconds_left, started}` for unfinished mock/module/diagnostic sessions.
  - `recent`: `{id, kind, started, finished, minutes, right, asked, estimate, route, capped, gated, modules:[{module, right, asked, wrong:[pos], blank:[pos]}], misses}`.
    - Positions are 1-based and split at len(mock_module(row, 1)), not 22.
    - `misses` = wrong + blank, as Fix counts them.
    - A diagnostic with no user_id returns gated:true, with no estimate or modules.
  - `total` is the count of finished tests.
  - limit is 1 to 20, and offset ≥ 0.

  POST /api/drill {from_session} gets the same gate: a diagnostic with no user_id gives 403.

- **GET /api/challenge: progress, time, streak, yesterday**

  Adds:
  - `answered` and `seconds_left` when a sitting is open
  - `streak`: consecutive days with a finished challenge, ending today or yesterday
  - `yesterday`: {rank, players, right, asked} or null

  `board` keeps limit=5, and the page shows all 5.

- **PUT /api/me: exam date, R&W fields, plan start**

  - A new exam_date must be today or later in the X-Tz zone (the header is added to this endpoint); otherwise 422 'exam_date is today or later'. Null clears it.
  - New optional `rw_now` and `rw_target`, each 200–800 in tens.
  - `minutes` may be set without a plan (the daily goal).
  - When exam_date, minutes and days are all set and exam_date or days changed, `plan_started` is stamped with today (local).
  - New learners columns rw_now, rw_target and plan_started go in LATER_COLUMNS, and profile() returns them.

- **POST /api/plan/mark (new, shared with Plan)**

  Table `plan_marks (learner, day, task, state, moved_to, at, PRIMARY KEY (learner, day, task))`.
  Body `{day, task:'practice'|'test', state:'skipped'|'moved'|null, moved_to}`.
  - day must be between today − 13 and the exam date.
  - `moved_to` must be a later study day before the exam's eve.
  - null deletes the mark.

  Returns the marks. UI.plan.dayOf(d, p, marks) applies moves: the source day becomes practice and moved_to becomes a test day.

- **GET/POST/DELETE /api/scores (new)**

  Table `outside_scores (id, learner, day, math, rw, source, at)`.
  - `source` is 'bluebook', 'official' or 'other'.
  - `math` is required, 200–800 in tens; `rw` is optional, same range.
  - `day` must be on or before today.

  GET lists them newest first. DELETE /api/scores/{id} removes only this learner's own.

- **progress.carry: new data**

  - COALESCE rw_now, rw_target and plan_started in the learners merge.
  - Move plan_marks with UPDATE OR IGNORE, then delete what's left.
  - Move outside_scores.

- **server/test_flow.py**

  Checks:
  - Two learners with the same X-Tz get identical mcq and spr stems, and spr's question.type == 'spr'.
  - No answer, rationale, reasons or key in GET /api/qotd before answering.
  - A double POST returns the first answer.
  - A graced answer at 00:30 counts in the crowd and streak; a late one changes neither.
  - A `like` drill before answering gives 409; after answering it serves the template and never its seed.
  - A `templates` mistakes drill serves only that template.
  - Study minutes include a finished module's elapsed time, and /me and /today agree on the streak.
  - The calendar month has every date, and a bad month gives 422.
  - tests/recent wrong/blank match the report, and the module split uses module 1's length.
  - An un-signed-up diagnostic is gated in scores, tests/recent and from_session.
  - open.drill appears after 1 answer and disappears after finish or overtime; open.test shows seconds_left.
  - A past exam_date gives 422.
  - plan/mark validation.
  - scores CRUD, and carry of the new tables.


### 3.2.6 Files this spec names, and who owns each

| file | owner |
|---|---|
| `web/index.html` | S3 |
| `web/assets/ui.js` | F2 |
| `web/assets/ui.css` | F1 |
| `web/plan/index.html` | S7 |
| `web/tests/index.html` | S5 |
| `web/results/index.html` | S6 |
| `web/me/index.html` | S1 |
| `server/app.py` | F0 (routers register themselves, §2.10) |
| `server/daily.py` | S3 |
| `server/progress.py` | F4 |
| `server/db.py` | F4 |
| `server/test_flow.py` | shared: new checks go in server/checks/<task>.py |
| `README.md` | shared: each task edits its own subsection |
| `spec/rebuild.md` | F0 (superseded by this file) |

A file owned by another task is met through §2.9: the owner builds it, or this section's task adds its hook on its own page.

### 3.2.7 Shared needs

- `.btn` secondary button, `.card`, `.card-head`, `.sk` skeleton and `.card-err` (error + Retry) in ui.css; `.clock` Timed/Untimed toggle moved from /tests/ into ui.css.
- UI.question upgrades shared with the session and report review: confirm mode (select, then Check; A–D/1–4, Enter), difficulty word + 3-pip mark and skill label in the skill line, per-option second line (choices_explained) and crowd bar after reveal, an actions-row slot, and a Grid-in rules popover. → built in F3 question.js / runner.js
- UI.calendar(host, {month, days, plan, marks, onPick, minMonth, maxMonth}): Monday-first month grid, goal-relative heat, today ring, plan marks (practice/test/skipped), exam mark, roving-tabindex keyboard, aria-labels. /plan/ switches its calendar to it. → built in F1 charts.js
- UI.plan.dayOf(d, p, marks) and UI.plan.today(profile, recent, marks, coach): one place that says what a day holds and what is done, used by Today and /plan/ (Plan section must agree on the marks and the completion rules).  
  ↳ R14: plan days and marks live in server/plan.py (S7); pages read /api/today.plan
- POST /api/plan/mark and the plan_marks table, owned jointly with the Plan section; plan_started stamped by PUT /api/me so the plan can show Day N of M and % done.  
  ↳ R14: plan days and marks live in server/plan.py (S7); pages read /api/today.plan
- UI.popover (anchored listbox, bottom sheet under 760px, Esc and outside click close, focus returns) and dialog.sheet form dialogs (target, add score, try one). → built in F1 kit.js
- UI.SAT_DATES moved from web/plan/index.html into ui.js.  
  ↳ R15: server/satdates.py (F4), served in /api/shell (F2)
- UI.dur(minutes) and long/short date formatters ('Wed, Sep 23', 'WEDNESDAY, SEPTEMBER 23'). → built in F1 kit.js
- UI.bandChart(host, points, {height, target, outside}) lifted from /results/, with hollow diamonds for added scores; /results/ uses it too and should list added scores. → built in F1 charts.js
- A shared sitting card (band, route tag, right/asked, minutes, wrong vs blank chips per module, Review, Fix N, New one like this, Resume / Time's up / gated states) used by Today, /tests/ and /results/.  
  ↳ UI.sittingCard (S6 results-ui.js)
- Target dialog and Add-a-score dialog shared with Plan step 2, Me and Results, all reading profile.target / rw_now / rw_target and /api/scores.  
  ↳ built by S3 on Today; Plan step 2 and Me edit the same learners fields with UI.scoreSlider and UI.examDate (F1)
- UI.ics(events) client-side calendar export, shared with /plan/. → built in F1 kit.js  
  ↳ R18(b): the plan's calendar file is built on the server (S7); single events use UI.ics(event) in F1 kit.js
- A report-a-problem sheet (owned by the Session section) reused on the day's questions.  
  ↳ R17: UI.report (F6 report.js)
- Practice builder preselect via URL: /practice/?topics=a,b&count=n&timed=1&difficulty=hard&domain=Algebra, and a #unfinished list of open sets (owned by Practice).
- Report deep link /results/report/?id=…&q=M1-3 (owned by Report).
- Plan deep links /plan/?step=0..3, /plan/?edit=1, /plan/?day=YYYY-MM-DD (owned by Plan).
- Challenge page ?day=YYYY-MM-DD to show a past board (owned by Challenge).  
  ↳ R3: Compete (S8) owns the challenge; past days at /compete/contest/?id=daily-YYYY-MM-DD
- Shell account menu (Me, Send feedback) is owned by the shell/Me section, not Today.

### 3.2.8 Acceptance checks

1. curl -s -H 'X-Learner: a:v2revacc1' -H 'X-Tz: 0' localhost:8000/api/today | jq '.study, .days.best, .scores, .open, .traps.open, .week.this' shows zeros, 0, [], {drill:null, drills:0, test:null}, 0 and zeroed week figures for a fresh code.
2. curl -s -H 'X-Tz: 0' localhost:8000/api/qotd | jq '.slots|map(.slot, .question.type)' gives ["mcq","mcq","spr","spr"]. The same call as a:v2revacc2 returns identical stems. jq '[.slots[].question|has("answer","rationale","reasons","key")]|flatten|any' gives false.
3. POST /api/qotd {answer:'999', day:<today>, slot:'spr', ms:40000} as a:v2revacc1 returns correct:false with answer and crowd.answered ≥ 1. A second identical POST returns the same given. GET /api/today then shows study.today ≥ 1, and /api/me days.streak equals /api/today days.streak.
4. POST /api/qotd {answer:0, day:<today-3>, slot:'mcq'} returns late:true. GET /api/qotd?day=<today-3> shows mine set while crowd.answered is unchanged, and .streak does not count that day.
5. POST /api/qotd with day=<tomorrow> gives 422. GET /api/qotd?day=<today-40> gives 422.
6. POST /api/drill {like:{day:<today>, slot:'mcq'}} before answering gives 409. After answering, count:5 gives a session whose served items in sqlite (sessions.questions) are all the QOTD's template and none has its seed.
7. With 2 open traps on different templates in one topic, POST /api/drill {mistakes:true, templates:[t1]} serves only t1 (twice).
8. After POST /api/mock/new {full:false} and /api/session/{id}/finish: GET /api/today .study.today includes the elapsed minutes; GET /api/tests/recent .recent[0].modules[0].wrong + blank equals the incorrect positions in /api/session/{id}/results .review; GET /api/calendar?month=<YYYY-MM> lists the sitting under today.
9. A finished mock's tests/recent modules[1] positions start at 1 and modules[0].asked equals len(module 1) from the results review.
10. A diagnostic finished with no signup: /api/today .scores excludes it, tests/recent shows gated:true without estimate, and POST /api/drill {from_session} gives 403.
11. GET /api/calendar?month=2026-13 gives 422. GET /api/calendar?month=2026-09 has 30 entries in days.
12. PUT /api/me {exam_date:'2020-01-01'} gives 422. PUT /api/me {exam_date:'2026-11-07', minutes:60, days:'1111100'} returns 200 with plan_started = today. PUT /api/me {rw_now:610, rw_target:700} returns 200, and profile carries both.
13. POST /api/scores {day:<today>, math:610, rw:600, source:'bluebook'} returns 201-ish with an id; GET lists it; DELETE removes it; as another learner, DELETE of that id gives 404.
14. POST /api/plan/mark {day:<today>, task:'practice', state:'skipped'} returns the mark; GET /api/today .plan_marks includes it; state:null removes it; a day before today − 13 gives 422.
15. shot.py a:v2revacc3 1280 … http://localhost:8000/ for a new code: every card shows its empty state with an action (Add your name, the Diagnostic link, Today list 0 of 3, When is your SAT?, No score yet with doors, No tests yet with doors, the Plan CTA). No page errors, and no card shows a bare dash.
16. At 1280 the two day's questions are side by side and both show their stems. At 390 they are tabs with status marks. At 390 the cards stack in the order hero, next, qotd, exam, score, mist, study, plan, chal, tests; document.documentElement.scrollWidth === 390; the last card clears the tab bar.
17. With a plan and a practice set of 5 answered out of 38: the Today list reads PLAN · 0 of 1 done with '5 of 38 questions', and the hero chip reads Plan · 0 of 1 done. After 38 answers the row shows a filled check and the header reads All done for today.
18. Plan rest day: Up next shows Rest day and an orange pill Practice anyway.
19. A timed module started and left: Up next shows Resume with the time left, counting down. With seconds_left 0 on module 1 of a section it shows Continue to module 2.
20. In the browser the SEC box changes within 1.1s, and with exam_date = today+10 at 07:00 local the DAYS box reads 10. With Playwright timezoneId 'Asia/Tashkent' at 00:30 local, the ringed calendar cell and the hero date are the local date.
21. Clicking Target ✎ opens dialog#targetSheet with Save disabled. Typing 650 enables Save; Save sends PUT /api/me {target:650}, and the score tick, gap line and plan stat row show 650 without a reload; /plan/ step 2 opens at 650. Esc closes without a request.
22. The exam trigger lists only official dates after today. Choosing Nov 7 updates the countdown, the hero chip and the plan line. Esc closes the popover and focus returns to the trigger.
23. MC day's question: the first tap only selects (no request in the network log); Check sends POST /api/qotd. After the reveal, every option row shows a percentage and each distractor shows its misconception line under it. 5 more like this opens /practice/session/?id=.
24. Start a drill from Up next, answer 2, return to / (pageshow): Up next shows Continue · 2 of N answered and links to the same session id.
25. Try one now opens dialog#tryOne with a question of the top trap's template. Answering it right fills one owed pip after Done.
26. Tapping a calendar day with activity shows 'Mon, Sep 21 · N min · N questions · N% right' and its sittings as links. A future plan day shows 'Planned · …'.
27. Aborting /api/challenge with Playwright route interception leaves every other card rendered, and the challenge card shows Couldn't load the challenge. with Retry. Aborting /api/today shows Couldn't load this. on next, mist, score, plan and exam, and one Retry repaints all of them.
28. PYTHONPATH=. python3 server/test_flow.py passes.

### 3.2.9 This section's open questions

Folded into Part 5 where they need a decision; kept here for context.

- Official 2026–27 SAT dates: /plan/ has Mar 13 2027 and TopTierPrep has Mar 6 2027 (both Saturdays). Verify every date against College Board before moving them into UI.SAT_DATES.
- Countdown target 8:00 AM local ('doors close') and the checklist wording (Bluebook exam setup, admission ticket, ID, calculator policy): verify against College Board's current SAT-day rules before shipping.
- Diagnostic gate: this spec makes Today respect it (no band, misses or Fix before sign-up). Is the gate still wanted, now that every other sitting is open without an account?
- R&W now/target on Today: should Plan steps 1–2 also take R&W, as theirs do, or stay Math-only with R&W only on Today and Me?
- Added scores (Bluebook/official): should they feed the coach or only the trend, the drift prompt and the plan's test-day completion (proposed)?
- Drift threshold: 30 Math points (theirs is 60 on the 1600 scale). Also offer it downward, or only upward as theirs does?
- Move-a-test from Today depends on the Plan section adopting plan_marks in UI.plan.dayOf. If Plan does not ship marks, drop Move and keep Skip.

---

## 3.3 Practice: the builder and the session

> **Spec title:** Question Bank: the practice builder (/practice/) and the practice session (/practice/session/)  
> **Built by:** S4 (pages, session server), F3 (workspace, strip, navigator, overlays), F5 (drill body, levels, kinds), F6 (report sheet, shares), T-bank (grid-in mistakes)  
> **Read with resolutions:** R5, R6, R10, R11, R17, R18, R19, R20, R21, R22, R24, R33, R34 (§2.2). Where this spec disagrees with them, they win.

### 3.3.1 What they have

- **One-screen builder**: /question-bank is a single screen with no page scroll. The skill list scrolls inside its own card, and the action bar is fixed to the bottom.
- **Bank toggle**: A top segmented control switches between two banks. Question Bank holds College Board items: 1,848 R&W and 1,921 Math. TTP Bank holds their own items: 1,315 R&W and 3,867 Math. TTP is lopsided (Rhetorical Synthesis 493, Transitions 10, SEC 22, Evaluating statistical claims 5), is quota-limited on free, and shows '0 a day' on paid tiers.
- **Live question count**: The 'SELECT DOMAINS' heading carries a live 'N questions' count. Bug: unchecking a domain does not update it (1921 stayed 1921).
- **Subject toggle**: Segmented: English and Writing | Math.
- **Domain accordions**: Each domain card has a check circle, its name, a count and a chevron, and expands to its skills. The parent unchecks when any child is unchecked, and there is no indeterminate state.
- **Skill checkboxes with counts**: Every skill has its own checkbox and item count. Examples: Linear functions 170 QB / 408 TTP; Evaluating statistical claims 12 / 5. Math has 4 domains and 19 skills; R&W has 4 domains.
- **Bluebook Include | Exclude**: QB tab only. It keeps out, or lets in, items that also appear in Bluebook practice tests.
- **Difficulty multi-select**: Easy / Medium / Hard toggle pills, all on by default.
- **Question Score 1-7**: A dual-thumb range slider for finer difficulty. It is not shown in the Details popover.
- **Solved filter**: Select: All / Solved Only / Unsolved Only. It combines (AND) with the other two selects.
- **Marked for Review filter**: Select: All / Saved Only. Marking for review IS their save list.
- **Redo List filter**: Select: All / Redo Only. The API has toggleRedo, but the session has no Redo button. Profile shows 'Redo Questions 0'.
- **Volume**: Segmented: 10 / 20 / 30 / 40 / 50 / All.
- **Mode**: Segmented: Timed | Untimed. Timed allows 6 min per question (10 questions = 60:00). Untimed shows an 'Untimed' pill where the timer sits.
- **Start Practice Session**: The primary button, at the right of the bottom bar.
- **Learning Preferences (Profile)**: Practice Mode Timed/Untimed; Difficulty Level Adaptive/Fixed; switches for AI Explanations, Show Desmos Calculator and Include Vocab Review. The Adaptive setting has no visible effect in QBank.
- **Saved content counts (Profile)**: Saved Words / Redo Questions / Saved Questions counts.
- **Session route**: /question-bank/session/{uuid}. The session is resumable only by its URL, and the app sidebar stays visible.
- **Go Back**: A top-left link back to the builder.
- **Details popover**: Shows QUESTION ID (e.g. 06469-DC), DOMAIN, SKILL and DIFFICULTY. It closes only on an outside click.
- **Explanation**: The button appears only after a check. It replaces the question card with a blue-tinted card and turns into '← Back to Question'. The report's version adds 'Justification:' plus 'Distractor Analysis:' with one line per wrong option.
- **Timer**: A centre mm:ss countdown pill with a Hide link. Timed sessions also have 'Go to Review Page →', 'Check Your Work' and 'Submit Module' (seen in the bundle).
- **Clear Session**: A red outline button. Its confirm reads: 'This removes answers, annotations, and attempts from this session only. Your question-bank progress from other sessions is kept.'
- **Share**: The UI calls navigator.share, which opens the OS sheet and froze the page. The bundle creates a shared session at /question-bank/shared/:shareId with a 'Start Practice' landing, plus toasts 'Share link copied to clipboard' / 'Share created (id: ...)'.
- **Calculator**: Desmos in a floating panel that can be dragged and resized. The question column shifts over to make room.
- **Reference**: A modal showing the formula sheet image.
- **Question number square**: A blue square with the number, at the start of the question strip.
- **Mark for Review**: A bookmark that fills when on. It shows in the overview and feeds the builder's Marked filter (Saved Only).
- **Eliminate**: A mode toggle that turns red and adds a ⊘ button to each choice. An eliminated choice greys out with its letter struck. Eliminations are saved to the server.
- **Annotate**: Annotate mode on passages: 'Annotating — click to stop', with Note / Save note / Remove. Bluebook-style Highlights & Notes in the exam runner offers 4 colours, 3 underline styles and notes.
- **Report**: A shared modal with a read-only context box, Title (0/200, prefilled), Category (General feedback / Bug / Wrong answer key / Typo / Feature request / Other), Details (0/5000), up to 10 images of 50 MB each (JPEG/PNG/WebP/GIF), and 'Send feedback'.
- **Attempts and Attempt History**: A ↻ button with a count badge opens a modal of rows like '#1 ⊗ Incorrect · Option A · 00:22 · Sep 23, 11:35 AM' with [Close]. Empty state: 'No attempts yet.'
- **Per-question stopwatch**: A count-up mm:ss in the strip. It resets to 00:00 on reload.
- **Stem rendering**: Text with KaTeX and images. An image floats beside the text, which is a layout bug.
- **MCQ layout**: A 2x2 grid of choice cards, each with a letter circle.
- **SPR input**: A full-width input with placeholder 'Enter your answer (e.g., 5.566, -5.566, 2/3, -2/3)'. A mono 'Answer Preview:' line under it renders fractions stacked with KaTeX. A correct answer turns the input green.
- **Check**: Right turns green with a filled letter and a ✓; wrong gets a red border and tint. The key is never shown and retries are unlimited. A wrong-then-right question counts as 'Mixed'. On reload, the earlier wrong pick shows as a plain 'selected' instead of red.
- **Bottom bar**: Previous; a centre 'Question N of 10' pill; Check; Next.
- **Question Overview**

  A popover with a Status | Difficulty toggle.
  - Status legend: Unanswered (outline), Correct, Incorrect, Mixed (a square split diagonally green/red), Marked (yellow with a bookmark corner), Current (blue, which overrides the other states).
  - Difficulty view: Easy green / Medium blue / Hard red.
  - It ignores Esc.

- **No end**: There is no summary, score, review flow or list of sessions. Next is disabled on the last question.
- **Homework (hidden)**: /my-classes and /teacher routes. An assignment can be 'a question-bank session — check answers as you go', with a time limit, 'Attach file' and [Finish Homework]. It is not linked from the sidebar.
- **Public single question (hidden)**: A /question/:key route, probably a public page for one question.
- **Floating vocab button**: A draggable 'Add your own word' button on every page. It covers Next.

### 3.3.2 What we have now

Status is have / partial / missing / worse, against theirs.

- **Bank toggle (QB | TTP)**: *missing.* There is one generated bank, so there is nothing to toggle. The equivalent is a clear statement of where the questions come from. Official-item replicas are an open question.
- **Subject toggle**: *missing.* Math only. There is no R&W bank.
- **Domain accordions with checkbox and count**: *partial.* Four mono domain headers toggle all their tiles. There is no checkbox, tri-state, count, collapse or domain stats.
- **Skill checkboxes with counts**: *partial.* 19 toggle tiles, each with a glyph, a short name, an unlabelled mastery hairline and up to 3 orange mistake dots. There is no answered count, accuracy, last-practised date or full name. Mistake names are in a hover-only tooltip that touch cannot reach.
- **Question types below skill level**

  *missing.* There are 386 templates, and 378 have a docstring that describes them. None can be picked.

  The skill labels are too coarse to group by. Measured:

  | skill | templates | skill labels |
  |---|---:|---:|
  | Evaluating statistical claims | 6 | 1 |
  | Margin of error | 12 | 1 |
  | Probability | 16 | 3 |
  | Equivalent expressions | 21 | 4 |

- **Type search**: *missing.* There is no way to find a type by name.
- **Live selection count**: *missing.* Nothing says what the selection holds.
- **Bluebook include/exclude**: *partial.* Practice never repeats (practice_seen), and freshly built test modules are remembered. The fixed shelf sections (/api/mock/{num}) and the 10 diagnostic forms never write practice_seen, so their questions can come back in practice. The page says nothing about any of this.
- **Difficulty multi-select**: *have.* Easy / Medium / Hard as underline toggles, with at least one kept on.
- **Question Score 1-7**: *missing.* Only the three tiers exist. The data cannot support a measured level yet: the db holds 283 attempts, and no (template, tier) has 20.
- **Solved / Unsolved**: *missing.* There is no pool of questions seen before, exact or fresh, filtered by result.
- **Marked for Review filter**: *partial.* A bookmark 'saves' a question. The saved set can only be started from /mistakes/ ({saved:true}), not from the builder.
- **Redo list**: *partial.* Open mistakes can be fixed from /mistakes/ ({mistakes:true}). Exact replay of a missed question is missing.
- **Volume**: *have.* 5 / 10 / 22 / ∞, plus a custom blank from 1 to 120. There are no 20/30/40/50 presets.
- **Timed / Untimed**: *have.* An unlabelled clock toggle and a minutes blank, at test pace (95 s a question) by default.
- **Start**: *have.* An orange pill, disabled until a skill is picked. Nothing says why it is disabled.
- **Coach preselection**: *have.* The coach's topics come preselected. There is no reason given per skill, no reset, and no other presets.
- **Practice preferences**: *missing.* The builder remembers nothing between visits, and learners has no prefs column.
- **Resume / sets list**: *missing.* A set can be resumed only by its URL.
- **Go back / exit**: *worse.* The X ends the set at once, with no confirm, no 'keep for later' and no pause.
- **Details popover**: *missing.* Only the topic short name is shown.
- **Explanation**: *have.* Shown inline after a miss. After a right answer it is behind a 'Why' toggle.
- **Named mistake on a miss**: *have.* The picked option's reason is shown. A grid-in never names one: SPR items carry no misconception values.
- **Key shown after a miss**: *have.* Better than theirs.
- **Repair question**: *have.* After a miss, the same template on a fresh seed, marked 'Again'.
- **Timer with Hide**: *partial.* A countdown when timed, worked out on the client from Date.parse(started). It cannot be hidden or paused, and there is no stopwatch when untimed.
- **Clear session / start over**: *missing.* There is no retake of the same questions.
- **Share**: *missing.* There is no link to a question or to a set.
- **Homework-style sharing with results**: *missing.* There is nothing for a tutor or study group.
- **Calculator**: *have.* Desmos, floating and draggable. It cannot be resized or docked, and on a phone it covers the question. The exam runner has its own separate calculator code (openCalc/dragCalc in test.js).
- **Reference**: *have.* The formula sheet in a dialog.
- **Mark for review**: *partial.* An unlabelled bookmark saves the question. No navigator shows it.
- **Eliminate / strike-out**: *missing.* It cannot exist while one tap submits.
- **Highlights and notes**: *missing.* There is no annotation of any kind in practice.
- **Report a problem**: *missing.* There is no reports table and no endpoint.
- **Attempts / attempt history**: *missing.* One try per question, and no history.
- **Per-question stopwatch**: *missing.* ms is measured and sent on answer, but never shown. Time on a question that is left without answering is lost.
- **Select then Check**: *worse.* One tap submits.
- **MCQ layout**: *have.* Full-width rows with letter circles. A-D and 1-4 on the keyboard.
- **SPR input + preview**: *partial.* The input has maxlength 6 and an empty placeholder. The preview only echoes the input, with a minus sign. There are no rules, no validation, no fraction preview and no accepted forms.
- **Question overview**: *missing.* Progress segments only: not clickable and with no legend. Above 24 questions they collapse to a count.
- **Previous / Next**: *partial.* Next only. There is no revisit and no skip.
- **Reload**: *partial.* state() returns only an unanswered current question. A reload after answering loses the verdict and serves the next question.
- **Difficulty and skill on each question**: *partial.* The topic short name only.
- **Everyone's stats per type**: *missing.* Attempts from all learners exist, but nothing aggregates them.
- **Mastery movement**: *have.* An animated before-to-after bar, with no label.
- **End-of-set summary**: *partial.* Shows the score, minutes, topic bars, mistakes opened and fixed, and Keep going. There are no tiles, no difficulty split, no review list, and no retake, fix-misses or print.
- **Print / export**: *missing.* There is no printable set or review.

### 3.3.3 Design

##### Review changes

I checked the proposed spec against spec/toptierprep-teardown.md, ttp-notes.md, the 2026-09-23 re-walk, and the code: drill.py, app.py, progress.py, practice.py, blueprint.py, ui.js, both practice pages, test.js and satfreshman.db. Each fix below has been applied in the spec that follows.

**Theirs, left out or covered by something weaker**

1. **Added highlights and notes.** Their session has Annotate (Note / Save note / Remove), and Bluebook has Highlights & Notes, but the spec had neither. It now has a Highlight tool with a wash fill and three ink underline styles, each able to carry a note, plus a per-question 'My note'. Both are stored on the server against (template, seed) and come back wherever that exact question appears.
2. **Strikes are saved on the server,** as theirs are. The spec used sessionStorage, which dies with the tab and never reaches a second device.
3. **Solved / Marked / Redo parity.** Their three selects combine with AND. The spec's single radio could not express 'marked and missed' or 'solved only'. The pool is now New · Open mistakes · Due for review · Never tried · **Seen before, exactly**. That last one has sub-filters: Result (Any / Missed / Right / Guessed), Marked only, and From (Practice / Tests / Both).
4. **Check Your Work in every mode.** Theirs has it in timed sessions; the spec had it only in end mode. Now Finish opens it whenever anything is skipped, unanswered or marked.
5. **Shared links always land first.** They go to the `/practice/?share=` landing, their 'Start Practice' equivalent. The spec's `/practice/session/?share=` auto-start is removed, because it contradicted 'never auto-starts'.
6. **Report attachments are restored:** up to 3 screenshots, plus automatic device context. Regenerating a question does not reproduce a rendering bug on one particular device. Their Title field is replaced by the category.
7. **Learning Preferences equivalent.** The spec stored builder settings in localStorage. That is per device, is lost when the device code moves, and conflicts with the Me section's practice preferences. They now live in `learners.prefs` on the server, remembered as last used, carried with the device code, and editable in the builder, the session's More menu and /me/.
8. **The stopwatch survives skip, reload and leaving.** Their stopwatch resets on reload. The spec added time only on answer, so time on skipped or abandoned questions was lost. It now saves through `/time` with `fetch(..., {keepalive:true})`. sendBeacon cannot be used because it cannot send X-Learner.
9. **A reload reopens the question you were on, with its verdict.** Their bug: a reload shows the wrong pick as a plain 'selected'. The spec's resume skipped to the first unanswered question, which lost the last verdict.
10. **Grid-in help is visible.** Their placeholder shows examples; the spec emptied it and moved the rules into a popover. Now there is a placeholder, a one-line rule under the field, a stacked-fraction preview with its decimal value, and a full-directions link.
11. **Timer caption:** 'left' or 'elapsed' under the digits, the equivalent of their 'Untimed' pill.

**Not clearly better**

12. **Question types are templates, not skill labels.** Grouping by label collapses Statistical claims (6 templates, 1 label), Margin of error (12→1), Probability (16→3), Equivalent expressions (21→4) and One-variable equations (18→4). That makes type choice useless exactly where their bank is thinnest. So there are now 386 types, each named from its slug with the template docstring as an 'about' line (378 of 386 have one), grouped under the skill's labels. This also fixes the spec's clash between '386 question types' and 'one row per label'.
13. **Level 1–7 as written could not work.** The db has 283 attempts, and no (template, tier) has 30 first tries. So every type would sit at its prior of 2, 4 or 6, and choosing level 1, 3, 5 or 7 would 409. Now the tier toggles always work, the level cells count only measured types (20+ first tries) and print their counts, unmeasured types come in through an explicit checkbox, and Details says 'estimated' or 'measured from N'. Levels use fixed accuracy thresholds, not ranks, so they stay stable when few types are measured.
14. **Every option's mistake shows by default** after answering. The spec hid it behind a toggle, and it is the one thing a finite bank cannot do. Filler distractors are labelled honestly.
15. **The coach's pick gives a reason per skill.** A disabled preset shows its reason as visible text, not as a tooltip that touch cannot reach.
16. **Spread** (even / like the test) is a visible setting. Before, only a preset could set it.
17. **Challenge IDs stay hidden until the day's challenge closes.** The spec showed them after answering, which let a student leak the question to friends who had not sat it yet.
18. **Exit with 0 answered** ends the set quietly and keeps it off the lists. Before, empty sets piled up under In progress.
19. **Checking with 'I'm guessing' on opens the explanation,** even when the guess was right.

**Minimalism creeping back (removed)**

20. **Phone domain headers** had swapped their stats for 'N of M selected'. They now show both on two lines, and open expanded.
21. **Phone RunBar** hid the set title. It now sits in the progress line.
22. **Phone action bar** was cut to '10 q · 3 skills'. It now shows two full lines.
23. **Settings were hidden** behind Edit at 640–1039 px and behind a modal sheet on phones. They are now shown in full, inline.
24. **The grid-in placeholder** had been emptied (see 10).

**Conflicts, and things that could not work**

25. **`UI.band` is already taken:** it is the score-range formatter in ui.js. The mastery helper is `UI.masteryWord`.
26. **The grid-in field's `maxlength=6`** made the '1234567' check impossible to type. The field now allows 7 characters and the check uses '123456'.
27. **'Nothing you've seen comes back' was false.** Shelf sections (/api/mock/{num}) and the diagnostic forms never write practice_seen. They now remember what they serve.
28. **Abandoned timed end-mode sets never filed their answers.** Now a set past its clock is finished on its next read (state or list).
29. **∞ disables Easiest first,** as it already disabled Test pace.
30. **Plan, Today and Mistakes launch sets directly** with `POST /api/drill` and their own `source`. The deep link only presets the builder.
31. **The acceptance checks are rewritten** to match all of the above.

**Extras added**

32. **Everyone's stats per type**, e.g. '58% right on the first try · most common mistake: …'.
33. **Named grid-in mistakes.** A typed value is matched against the template's own wrong values.
34. **Shared-set results for the sharer,** a free version of their hidden homework feature, with a name opt-in for takers.
35. **'Why this one'** on every question.
36. **Type search.**
37. **Printable worksheet, and print or save as PDF** of a set or its review. Their Export button is dead.
38. **More numbers:** the Easy/Medium/Hard split and average time per skill, plus by-type rows, time per question and 'before this set' accuracy in the summary.
39. **A due-for-review pool.**
40. **Marked tidies itself** after a right replay, unless Keep is ticked.
41. **Mark all incorrect** in the review list.
42. **Run length** in the progress line.

---

##### Ground rules for this section

- **Label everything a student acts on.**
  - At 760 px and wider, every tool is an icon plus a word.
  - Below that, an icon keeps a 10.5 px caption under it.
  - Every icon also has an aria-label.
- **Print stats as numbers.** Answered counts, first-try accuracy %, times and counts sit next to their bars.
- **Mastery is a bar plus a word, never a %.** The word comes from `UI.masteryWord(m, answered)`:
  - 'Not started' when nothing has been answered;
  - 'Learning' below 0.4;
  - 'Getting there' from 0.4 to 0.8;
  - 'Strong' at 0.8 and above (progress.STRONG).
  - Mastery is not accuracy, so accuracy is printed beside it as its own %.
- **Every count updates live** as the selection or a filter changes. (Their count froze when a domain was unchecked.)
- **Helper text.** A control may carry one --soft 13 px helper line when it changes with the value. Every colour or glyph encoding has a legend with counts.
- **Borders are allowed.** A 1 px var(--line) wherever grouping needs it.
- **Orange is the only accent.** Status is told by glyph and fill (section 3), never by green and red.
- **One question workspace.** UI.workspace serves the session, the summary review, the report review, the question of the day, Mistakes and the exam runner (feedback='end').
- **Nothing floats over the footer.** (Their vocab button covers Next.)

---

##### 1. Builder: `/practice/`

###### 1.1 Desktop layout (1040 px and up)

The page is max 1120 px wide, inside the normal shell. From top to bottom:

1. Page header.
2. Resume banner, or Shared-set banner.
3. Preset bar and coach line.
4. Search.
5. Two columns on a 12-column grid with a 24 px gap:
   - left, 7 columns: the Skill tree;
   - right, 5 columns: the Settings panel, sticky at top 80 px. If it is taller than calc(100vh − 176px), it scrolls inside itself.
6. Your sets.
7. The fixed Action bar: 72 px, full-bleed, paper, a 1 px top line and a shadow. Its content aligns to the 1120 px column, and the page gets 96 px of bottom padding.

The page scrolls. Their no-scroll screen only fits by hiding stats.

###### 1.2 Page header

**Left:**
- Eyebrow `SAT MATH` (.k).
- H1 'Practice'.
- Mono meta line: `19 skills · 386 question types · unlimited questions, never repeated`, from /api/bank totals.

**Right**, three links:
- `Mistakes · 4`, with an orange dot, to /mistakes/.
- `Marked · 6`, to /mistakes/#marked.
- `Your sets · 2 in progress`, which scrolls to Your sets.

Zero counts still show '· 0' in --soft, and the links stay enabled.

###### 1.3 Resume banner and Shared-set banner

**ResumeBanner** shows when GET /api/drill has an `active` set. It shows the newest one; if there are more, a `+2 more` link scrolls to Your sets.

- A panel with a --wash background and a 1.5 px amber left edge.
- Copy: `Set in progress · Linear functions, Percentages · 6 of 10 answered · 12:40 left` (or `· paused`, or `· untimed · 14:05 so far`).
- Buttons: `Resume` (small pill) and `End it` (quiet). End it opens a confirm popover: 'End this set and see its summary?' [End set] [Cancel].

**SharedSetBanner** shows when the URL has `?share=CODE` (GET /api/share/{code}).

- Copy: `Shared set · 10 questions · Linear functions, Circles · timed 16 min · answers after each`, then `from Maya · taken by 7 · average 6.4 / 10`.
- A checkbox `Show my name to the person who shared this`, off by default. It is disabled when learners.name is empty, with the text 'Set a board name on Me first' linking to /me/.
- A --soft line: 'Uses the sharer's questions and settings, not yours.'
- Buttons: `Start this set` (pill) and `Dismiss` (quiet).
- Errors, shown in an .error line with Dismiss:
  - bad code: 'That shared set does not exist.';
  - revoked: 'Whoever shared this set has stopped sharing it.'

###### 1.4 Preset bar and coach line

The chips are 36 px, 10 px radius, on var(--tile). A selected chip has a --wash fill and a 1.5 px amber inset. The row wraps.

A disabled chip keeps its label and shows its reason on a second line inside the chip, in 11 px mono. This is visible text, not a tooltip.

| chip | sets | disabled when |
|---|---|---|
| `Coach's pick · 2 mistakes` (the suffix comes from coach.why) | skills = coach.topics, count = coach.count, pool = New, all tiers. Selected on load unless a link overrides it. | never |
| `Weakest 3` | the 3 lowest-mastery skills with 5+ answered | 'needs 5 answers in 3 skills' |
| `Plan focus` | every skill in the plan's Focus domains | 'no Focus domain in your plan' (links /plan/) |
| `Full section mix` | all 19 skills, 44 questions, Spread = Like the test, Order = Mixed | never |
| `My mistakes · 4` | pool = Open mistakes, skills = those with open mistakes | '0 open' |
| `Missed · 7` | pool = Seen before, Result = Missed | '0 missed' |
| `Marked · 6` | pool = Seen before, Marked only | '0 marked' |
| `Due for review · 5` | pool = Due for review | 'nothing due' |
| `Custom` | lights when a manual change departs from the chip in use | inert |

A quiet `Reset` at the right end restores Coach's pick and your saved defaults.

**Coach line.** While Coach's pick is active, one line sits under the bar (13 px, wrapping), built from coach.reasons:

`Why these: Percentages: 2 open mistakes · Circles: weakest, Learning, 48% first try · Linear functions: not practised for 12 days`

###### 1.5 Search

A full-width field above the tree:

- Label 'Search'. Placeholder 'Skills and question types, e.g. circle equation, margin of error'.
- Filtering is live, over skill names, type names, about lines and skill labels. Matches are highlighted. Rows that do not match hide. Skills with matches expand.
- A count reads `12 types match`, next to a button `Select all 12`.
- Esc clears.
- Empty: 'No question type matches "xyz". Try a skill name.'

###### 1.6 Skill tree

**Tree header:**
- 'Skills' (.h2), then `3 of 19 skills · 41 of 386 types selected` in mono.
- Quiet buttons: `Select all`, `Clear`, `Expand all` / `Collapse all`.
- A native `<select>` 'Sort': Test order (the default), Weakest first, Most mistakes, Least practised, Recently practised. Sorting works within each domain.

**DomainCard.** One per domain, in blueprint order: 1 px line, 12 px radius, paper, 10 px gap between cards. The header is a 56 px row with aria-expanded, and holds:
- a tri-state Checkbox: 20 px, 5 px radius, 1.5 px ink border. Checked is an amber fill with an ink-deep tick; indeterminate is an amber fill with an ink-deep dash. Clicking an unchecked or indeterminate box selects all; clicking a checked box clears all;
- the name, 700 16 px;
- a weight chip: `35% of the test · ~15 of 44`;
- a 120 px mastery bar with its word;
- `128 answered · 74% first try`;
- `● 3 open`;
- `2 of 5 selected`;
- a chevron.

Cards are expanded by default. The open or closed state is kept in localStorage `satf.tree.open`, inside try/catch.

**SkillRow.** 52 px, on a grid of: checkbox 20 | glyph 22 | name 1fr | mastery 140 | record 150 | mistakes 80 | last 72 | chevron 28.

- **Name:** the full College Board name from catalogue topics[t].name (600 15 px). A mono sub-line under it: `23 types · Easy Medium Hard · 8 grid-in`.
- **Mastery:** the .mbar, 4 px tall, with its word under it (11 px mono).
- **Record:** `42 answered · 81% first try`, or 'Not practised' in --soft.
- **Mistakes:** `● 2 open`.
- **Last:** 'today', '3d ago', '2w ago' or '—'.
- **Chevron:** aria-label 'Show stats and question types'.
- Clicking the row, except the chevron, toggles it. Mouse drag-paint is kept from today. Space toggles and → expands.

**SkillPanel.** The expanded body, indented 42 px, in this order:

1. **Stats line** (mono 12.5 px):
   `Easy 12/14 · Medium 20/28 · Hard 3/9 · average 1:12 a question · everyone 64% first try`
   The 'everyone' part appears only once there are 20 or more first tries.
2. **'Open mistakes in this skill'** (only when there are any). Each row reads `● Left out the constant term · Count solutions · 1 of 2 clean answers left`, then a quiet `Fix` that starts {pool:'mistakes', templates:[t]}. This replaces the hover tooltip.
3. **Question types.** When the skill has more than one skill label, types are grouped under sub-headers, e.g. 'evaluating a linear function · 4 types'.

**TypeRow.** 44 px minimum; it wraps.
- A checkbox.
- The name, sentence-cased from the template slug (`lin1.count_solutions` → 'Count solutions').
- The about line under it, in 13 px --soft: the docstring's first sentence, e.g. 'One, none, or every number — and the equation that decides which.'
- Tier letters `E M H`, with the unavailable ones in --faint.
- Format chips `MC` and `Grid-in`.
- The level: `L4` when measured, or `L3–5 est.`.
- Your record: `5 · 4 right`, or 'New'.
- `Everyone 62%`, when there are 20 or more first tries.
- `● 1` for an open mistake.
- `Marked 2`.
- A quiet `Try one`, which starts a one-question set of this type with the current settings.

A skill with more than 12 types collapses behind `Show all 36 types`.

**Live availability.** A row whose types cannot produce the current Format, Difficulty or Level settings dims to 42%. It gets a --soft reason in its sub-line: 'no grid-in types', 'no Hard types', or 'no measured types at level 7'. It stays selectable. The Action bar counts only what can be served.

###### 1.7 Settings panel

A card with a 1 px line, 12 px radius and 20 px padding. Every control has a visible .k label, and a --soft helper line where noted.

**1. Questions from.** A radio list, 44 px per row, each row with a count on the right. Counts come from POST /api/drill/preview and cover the current skill and type selection with the current filters.

- `New questions · 41 types`. The default. Helper: 'Generated for you now. You have never seen any of them.'
- `Fresh numbers on my open mistakes · 4 types`. Helper: 'Each type you fell for, twice. Two clean answers close a mistake.'
- `Fresh numbers on types due for review · 5 types`. Helper: 'Types you got right more than 10 days ago, so they stay strong.'
- `Fresh numbers on types I've never tried · 23 types`.
- `Questions I've seen, exactly · 212`. Helper: 'The same questions again, exactly as they were.' Choosing it opens its sub-filters in place:
  - Result (Seg): `Any 212 · Missed 7 · Right 198 · Guessed 3`.
  - `Marked for review only · 6` (checkbox).
  - From (Seg): `Practice and tests · Practice · Tests`.
  - Helper: 'A marked question you get right here leaves your Marked list, unless you tick Keep marked on it.'
- A pool with 0 is disabled, with its '0' shown.
- An exact pool caps Questions at its size and shows `All 7`.

**2. Questions** (Seg). Equal buttons in a 1 px track; the selected one is amber-filled with an ink-deep label.
- Options: `5 · 10 · 20 · 30 · 40 · 50 · ∞`, plus an `Other` input (1–120; Enter starts).
- Helper: `≈16 min at test pace`, or for ∞: 'Endless: stop whenever you like.'

**3. Difficulty and level** (the LevelStrip).
- **Row 1:** three tier toggles, each with a count of types in the selection: `Easy · 14`, `Medium · 19`, `Hard · 8`. They always work, because every type has a tier.
- **Row 2:** seven level cells, 1–7, 36 px square, grouped under their tiers (1–2 / 3–5 / 6–7). Each cell shows how many measured types are at that level in the selection. A cell with 0 is disabled.
- **Levels are measured:** a (template, tier) needs 20 or more first tries from all students, excluding guesses. The level comes from accuracy on those tries:

  | tier | level by first-try accuracy |
  |---|---|
  | easy | 1 at 85% or more; 2 below |
  | medium | 3 at 70% or more; 4 from 50%; 5 below 50% |
  | hard | 6 at 40% or more; 7 below |

- **A tier header** toggles the tier and all of its cells. **A cell** toggles alone. A mouse drag paints across cells. The last on toggle cannot be turned off: it shakes, and the helper reads 'Keep at least one difficulty'.
- **Checkbox** `Include types not measured yet · 312`, on by default. When only some of a tier's cells are on, that tier's unmeasured types come along only while this is checked.
- **Helper:** `Levels come from students' first-try accuracy. 18 of 386 types measured so far.`
- **Toggle** `Adaptive: step up a tier after 2 first-try rights in a skill, down after a miss`. It works inside the selected tiers. It is disabled when Order is Easiest first, with the reason shown.

**4. Format** (Seg): `Both · Multiple choice · Grid-in`. Helper: `8 of 41 selected types make grid-ins`.

**5. Timing** (Seg): `Untimed · Test pace · Custom`.
- Untimed: a stopwatch counts up.
- Test pace: 95 s a question. Helper: `16:00 for 10 questions · 1:35 each, like the test`.
- Custom: a minutes input appears (1–180).
- With ∞: Test pace is disabled ('An endless set has no length to pace'), and Custom becomes `Sprint: as many as you can in N min`.
- Toggle `Pace alert on each question`, on by default when timed: the stopwatch turns amber-deep after 1:35.

**6. Answers shown** (radio, with helpers):
- `After each question`. The default. 'The key, your mistake by name and the explanation, right away.'
- `After I retry`. 'Wrong? We name the mistake your answer comes from, not the key. Up to 3 tries; only the first counts.'
- `At the end, like a test`. 'No feedback until you finish. Change answers, skip around, Check Your Work.'

**7. After a miss** (toggle, on by default): `Follow a miss with one like it (same trap, new numbers)`. It is disabled in end mode, with the helper 'In test mode, misses become a Fix set at the end.'

**8. Order** (Seg): `Mixed · Grouped by skill · Easiest first`. Easiest first orders by level where measured and by tier otherwise. It is disabled for ∞ ('An endless set has no end to ramp to').

**9. Spread** (Seg): `Even across skills · Like the test`. Helper: 'Like the test gives Algebra and Advanced Math 35% each, the other two 15%.' It is disabled when the selection sits in one domain.

**10. Repeats** (a fixed line with a lock glyph): `Never repeats. Nothing you were shown in a set, a test or the diagnostic comes back, except the exact replays you ask for above.` This is our answer to Bluebook include/exclude.

**11. Footer:** `Saved as your defaults` in --soft, and a quiet `Reset to defaults`.
- Settings 1–9 (not the skills) auto-save to prefs, as a debounced 600 ms PUT /api/me {prefs}.
- The same prefs are edited under Learning preferences on /me/.
- A deep link's settings apply to that visit only, and a note says so (see 1.10).

###### 1.8 Action bar (fixed bottom)

**Left:**
- Line 1, 600 15 px: `10 questions · 3 skills · 41 types · all levels · both formats`.
- Line 2, mono --soft: `Untimed · answers after each · repairs on · mixed · ≈16 min`.
- Up to 3 skill chips, then `+2`.

**Right:**
- `Printable worksheet` (quiet; see 2.12).
- `Start practice` (pill). While the set is being made: aria-busy, labelled 'Building…'.

**Disabled Start:** the reason is printed to its left, and every reason is taken from preview.reason:
- 'Pick at least one skill'
- 'Nothing here makes grid-ins at these levels'
- 'No open mistakes in these skills'

**Errors:** a create failure shows an .error line above the bar with the server's message and a quiet `Try again`.

**Live:** both lines update on every change.

###### 1.9 Your sets

'Your sets' (.h2), with tab Seg `In progress · 2` / `Finished · 48` / `Shared by me · 3`.

**Filters (Finished):**
- Skill `<select>`: All skills, plus the 19.
- Kind: All / Practice / Shared with me / Challenge.
- Result: All / With misses.

**Row (56 px):** started (`Sep 23, 14:05`) | skill chips (up to 3, then +n) | mode (`Timed 16 min` / `Untimed`, `After each` / `Retry` / `Test mode`) | progress (`6 / 10`, or `14 answered`) | `5 right · 83%` | time `11:42` | actions.

**Actions:**
- In progress: `Resume` (small pill) and `End`.
- Finished:
  - `Review` goes to the summary;
  - `Retake exact` sends {retake};
  - `Same settings` sends {again};
  - `Share` copies the link, with the toast 'Link copied: friends get these exact questions';
  - `Print`.

**Shared by me rows:** created | `10 questions · Linear functions + 1` | `Taken by 7 · average 6.4 / 10` | `Results` | `Copy link` | `Stop sharing`.

**SharedResults sheet:**
- Tiles: Taken / Average / Median time.
- A per-question table: `# · type · difficulty · right 5/7 · most common wrong answer: B, used the slope as the intercept (2)`.
- Takers: a name if they opted in, otherwise 'Student 3', each with a score and a time.
- Empty: 'Nobody has taken this set yet. Copy the link to send it.'

**Other rules:**
- 10 rows, then `Show 20 more`.
- Challenge sittings carry a trophy glyph, have no Retake or Share, and link to /challenge/.
- Sets finished with 0 answered are not listed.

**Empty states:**
- In progress: 'Nothing in progress. A set you leave halfway waits here, on any device with your code.'
- Finished: 'Sets you finish show up here, with their review.'
- Shared: 'Share a finished set to send the same questions to a friend or a class, and see how they did.'

###### 1.10 Deep links

`/practice/?skills=linear_functions,circles&types=lin.evaluate&count=20&pool=new|mistakes|review|untried|seen&result=any|missed|right|guessed&marked=1&from=practice|tests&tiers=easy,hard&levels=1-2,7&unmeasured=0&formats=spr&timing=pace|untimed|custom:25&feedback=instant|retry|end&repairs=0&order=mixed|grouped|ramp&mix=even|blueprint&search=margin&share=CODE`

- Every parameter is optional.
- A link overrides presets and prefs for that visit only. A --soft note says 'Settings from the link, not your defaults', with a quiet `Use my defaults`.
- The builder never auto-starts. Plan, Today and Mistakes buttons that mean 'start now' POST /api/drill themselves, with a `source` such as 'plan', 'today' or 'mistakes'.

###### 1.11 States

- **Loading:**
  - The tree shows 4 skeleton cards (grey 14 px bars in var(--tile), no shimmer).
  - Settings render from prefs cached in UI.me, or from the defaults.
  - Counts read '…'.
  - Start reads 'Loading…' and is disabled.
- **Server down:**
  - The tree area shows .error 'The server is not answering.' with a quiet `Retry`.
  - Settings stay editable, and Start stays disabled.
- **New student** (0 attempts):
  - Every row reads 'Not practised' and 'Not started'.
  - Coach's pick selects the big-domain skills, and the coach line reads 'Why these: not practised yet, and Algebra is 35% of the test'.
  - A line above the tree: `New here? The coach picked where the test puts the most questions. Or take the 20-question diagnostic for a starting score.` It links to /diagnostic/.
  - The Mistakes, Missed, Marked and Due chips show their disabled reasons, and the exact pools read 0.
- **Lots of history:**
  - The stats fill in, and Sort keeps the saved choice.
  - Your sets paginates and its filters apply.
  - Skills with 3 or more open mistakes show the real count (`● 5 open`).
- **Nothing servable:** as in the Action bar, with the offending rows dimmed and their reason shown.
- **Search with no match:** see 1.5.

###### 1.12 Widths

**640–1039 px:**
- One column.
- The full Settings panel sits above the tree, with its controls in two columns (Questions from, and Answers shown, span both).
- The Action bar stays.

**390 px phone:**
- 16 px gutters.
- **Header:** the eyebrow, the H1, the meta line wrapped, and the three links as a wrapping row.
- **Presets and search:** preset chips wrap 2–3 per row, and each disabled chip keeps its reason line. The coach line wraps. Search is full width.
- **Tree:** expanded by default. A DomainCard header runs to two lines:
  - line 1: checkbox, name, `2 of 5`, chevron;
  - line 2: bar with its word, `128 · 74%`, `● 3`, and the weight chip.
- **SkillRow**, two lines, 60 px or more:
  - line 1: checkbox, glyph, name, chevron;
  - line 2, indented 42 px: 80 px bar with its word, `42 · 81%`, `● 2`, last.
- **SkillPanel and TypeRow:** the stats line wraps. The TypeRow chips wrap under the about line.
- **Settings:**
  - Shown in full after the tree and before Your sets, in one column. No sheet, nothing hidden.
  - A jump row at the top of the tree, `Settings: 10 questions · Untimed · After each ↓`, scrolls to them.
  - The LevelStrip fits in 358 px: 7 × 44 px cells plus 6 × 6 px gaps is 344 px.
  - `Printable worksheet` moves into the Settings footer.
- **Action bar:**
  - Fixed above the tabs, at bottom: calc(62px + safe-area).
  - Two full summary lines (it may wrap to two lines each), then a full-width 52 px `Start practice`.
  - Tapping the summary scrolls to Settings.
- The page gets 230 px of bottom padding.
- document.documentElement.scrollWidth must be 390 or less.

---

##### 2. Session: `/practice/session/?id=ID`

**Entries:**
- `?id=ID`.
- `?q=TEMPLATE:SEED`: a permalink. The page POSTs /api/drill {item} and replaces the URL with the new id.
- `?id=ID&print=1`: the print view.
- Shared links go through the builder landing, never straight here.

The session has no site nav. It is a max-760 px column, with a calculator dock on the right when that is open.

###### 2.1 Desktop layout (760 px and up)

From top to bottom:

1. RunBar (sticky, 60 px).
2. ProgressRail.
3. QuestionStrip, and the 'Why this one' line under it.
4. Workspace.
5. Verdict and explanation.
6. RunFooter (fixed, 68 px).

With the calculator docked, the page splits into two columns: the question at minmax(0, 1fr) and the dock at 420 px, resizable from 320 to 640 px. Nothing overlaps the question.

###### 2.2 RunBar

**Left:**
- `Exit` (× icon plus the word).
- The set title, 600 14 px, truncated: `Linear functions + 2`, 'Daily challenge', 'Marked for review', 'Missed questions', or 'Fix: Sep 22 test'.

**Centre: the TimerBlock.**
- mm:ss in mono 18 px, tabular, with a 10.5 px caption `left` (countdown) or `elapsed` (untimed stopwatch).
- `Hide` / `Show`: a quiet 12 px button with an eye icon. Hidden, the digits read '— : —'. The choice is kept in prefs.hide_timer.
- Toasts at 5:00 and at 1:00 left. Under 60 s the digits go ink-deep 700.
- `Pause` (∥): drill sets only. It opens a paper overlay, 'Paused · 12:40 left', with a `Resume` pill. The questions are hidden while paused.
- The clock runs from the server's seconds_left and elapsed, never Date.parse(started).

**Right:** ToolButtons with an icon and a label:
- `Calculator` (aria-pressed; opens by default according to prefs.calc);
- `Reference`;
- `More ⋯`.

###### 2.3 ProgressRail

**Segments:** for fixed sets of 60 or fewer, one clickable segment per slot.
- Status fills follow section 3; future slots are --line.
- A repair adds a slot, which grows in with .seg.add.

**Continuous bar:** for endless sets and sets over 60, a single bar of answered over total.

**Text line:** mono 12 px, `Linear functions + 2 · 7 of 10 · 5 right · 1 skipped · 3 in a row`. For endless sets: `14 answered · 11 right`.

**Keyboard:** the rail is one keyboard group, and each segment has an aria-label.

###### 2.4 QuestionStrip

A 1 px bordered bar, 10 px radius, 48 px tall.

**Left:**
- The number square: 32 px, ink fill, paper text, 700.
- The skill chip (glyph plus short name), `·`, then the type name ('Count solutions').
- The difficulty chip: `Medium · L4` when measured, or `Medium` when not.
- `Grid-in`, on SPR questions.
- `Again`, with an orange dot, with the tooltip 'Same trap as question 6, new numbers'.

**Right**, ToolButtons with labels:
- `Mark for review` (bookmark; when on, amber-filled and labelled 'Marked').
- `Eliminate` (ABC struck; aria-pressed).
- `Highlight` (a marker; aria-pressed).
- `My note` (a note glyph, filled when a note exists).
- `Details` (i).
- `Report` (a flag).
- `Attempts` (↻ with a count badge). Shown when there has been a try, or there is any history on this type.
- The **QStopwatch**: mono mm:ss of time on this question, added up across visits. With the pace alert on, it turns amber-deep and gains a dot after 1:35.

Below 1000 px the labels become 10.5 px captions.

**'Why this one' line**, under the strip in 13 px --soft, taken from q.why:
- 'Open mistake: left out the constant term · 1 of 2 clean answers left'
- 'Same trap as question 6, new numbers'
- 'A type you have never tried'
- 'Your least-practised type in Circles'
- 'Stepped up to Hard after 2 right'
- 'Marked Sep 20'
- 'Missed on your Sep 22 test'
- 'Due for review: last right 14 days ago'

It is hidden in the challenge.

###### 2.5 Workspace

**Stem:** the figure, then the table, then the stem, in Source Serif 4 at 20 px. A figure always gets its own row above the text.

**Highlights and notes.** With Highlight on:
- Selecting text in the stem or a choice raises a small toolbar: `Highlight` (--wash fill), `Underline` in solid, dashed or dotted (ink), `Note`, and `Remove`.
- Clicking an existing mark opens its popover: the note text, `Edit`, `Remove`, `Close`.
- **My note** is a popover textarea for the whole question (0/1000), saved on blur, with the status line 'Saved'.
- Both are stored against (template, seed). They come back on replay, on retake, in the ReviewSheet, in Marked on /mistakes/ and in the report. A navigator cell of a question with a note shows a small note glyph.

**MCQ:**
- Rows by default.
- **Auto 2x2** when all four choices are 14 characters or fewer, the viewport is 640 px or wider, and there is no figure.

**Choosing: select, then Check.**
- A click, or A–D / 1–4, selects: a --wash fill and a 1.5 px amber inset.
- Clicking another choice moves the selection; clicking the selected one clears it.
- `Check` or Enter submits.
- prefs.first_tap ('Answer on first tap', in the More menu) brings back one-tap submit.

**Eliminate:**
- With Eliminate on, each row has a 32 px struck-letter circle at its right.
- Clicking the circle strikes the choice: 42% opacity, line-through, a dashed letter circle, and a quiet `Undo`.
- Shift+A–D strikes a choice without turning the mode on.
- A struck choice cannot be selected.
- Strikes are POSTed to /strike and restored from state on any device.

**SPR:**
- **Field:** labelled 'Your answer', 56 px tall. Placeholder 'e.g. 2/3, −1.5, 12'. Up to 7 characters are allowed so that the Too long error can show. No inputmode, so the phone keyboard keeps minus and slash.
- **Rule line** under the field, always visible, 13 px --soft: 'Up to 5 characters, 6 with a minus. Fractions with /, no mixed numbers. Long decimals may be cut or rounded.'
- **`All entry rules`** is a quiet link that opens the SprDirections popover: our wording plus an examples table (2/3 → accepted 2/3, .6666, .6667, 0.666, 0.667; not accepted 0.66, .67).
- **AnswerPreview**, mono, live: `Answer preview:` and the value typeset. A fraction is stacked with CSS (numerator over denominator, with a real minus), followed by `≈ −0.6667`.
- **Validation:** invalid input shows an inline .error and disables Check. The two messages are:
  - 'Use digits, one ".", one "/", and a leading "−"'
  - 'Too long: 5 characters at most, 6 with a minus'

**`I'm guessing`:** a toggle chip under the choices, off by default. Key I. When it is on at Check:
- a right answer counts half toward mastery;
- it does not pay down an open mistake;
- the explanation opens;
- the summary lists the question under 'Right, but guessed'.

**`Skip for now`:** a quiet button under the choices while unanswered. Hidden in the challenge.

###### 2.6 Check flow, by 'Answers shown'

###### After each question (instant)

**Right:**
- The chosen row turns .ok: an amber letter fill and a ✓ glyph.
- The Verdict reads `Correct · 0:48 · your average on this type 1:05`.
- The mastery bar animates, labelled `Linear functions · Getting there`.
- The explanation is collapsed behind `Explanation ▾`. It is open instead when prefs.open_explanations is on, or when I'm guessing was on.

**Wrong:**
- The chosen row turns .no: struck, with ✗. Under that row: `Your answer: left out the constant term`, with the mistake dot.
- The key row turns .ok, with the caption `Correct answer`.
- The Verdict reads `Incorrect · 1:12`.
- Notice: `New mistake to fix: Left out the constant term · 0 of 2 clean answers`, linking to /mistakes/.
- Notice: `Next: one like this, with new numbers`, when repairs are on and this was not itself a repair.
- The explanation is open.

**Every option explained**, shown by default (prefs.option_reasons can turn it off):
- Under each other distractor, in 13 px --soft, the mistake that produces it: 'C: used the slope as the intercept'.
- A filler reads 'D: a nearby value, not tied to a specific mistake'.

**Grid-in:**
- Right: the field takes the .ok state with ✓, and an `Also accepted: 2/3 · .6666 · .6667` line.
- Wrong: the key is shown in `Correct answer: 2/3 (also .6666, .6667)`. When the typed value matches one of the template's wrong values, the page also shows `Your answer 14 is what you get if you used the slope as the intercept`, and it is filed as that named mistake. When nothing matches: 'No named mistake for this value.'

**Everyone line** (when the type has 20 or more first tries; not in the challenge): `Everyone: 58% right on the first try · most common mistake: left out the constant term (41% of misses)`. Fillers are excluded.

**Mistake fixed:** `Fixed: Left out the constant term`, with a check glyph.

**Another one like this:** shown after any answer, with `easier` and `harder` split buttons when the type spans tiers. It calls POST /more, and a fixed set grows by 1.

**Replays of marked questions:** a right answer shows `Removed from Marked` with a `Keep marked` checkbox.

###### After I retry (retry)

**A wrong try:**
- That row is marked ✗ and disabled.
- Under it: `That answer comes from: left out the constant term. Try another.` A filler reads 'That's a near value. Check your arithmetic.' A grid-in reads its matched mistake, or 'Not right.'
- The key stays hidden.
- `2 tries left`, with buttons `Check` and a quiet `Show answer`.

**Right on try 2 or 3:** `Right on try 2 · counts as Mixed`, then the full reveal.

**Out of tries, or Show answer:** the full reveal, as Incorrect.

**What counts:** only the first try counts for accuracy and mastery. Every wrong try that names a mistake is filed as a mistake hit. A repair follows a first-try miss.

###### At the end, like a test (end)

- `Check` becomes `Save & next`, and there is no verdict.
- Answers can be changed until Finish, and skipping and jumping are free.
- The navigator shows Answered / Unanswered / Skipped / Marked only.
- The last question's button is `Review & finish`.

###### 2.7 RunFooter and moving around

**Left:** `Previous`, quiet with ←. Disabled on question 1.

**Centre:** the NavPill `Question 7 of 10 ⌃`, or `Question 14 · endless`. It opens the Navigator.

**Right:**
- `Check` (a pill), disabled until a choice or a valid entry.
- Then `Next →`.
- On the last question, `Finish`.
- In end mode, `Save & next` or `Review & finish`.
- A mono `Enter` hint shows on hover devices.

**Revisiting:**
- Previous or a navigator cell opens an answered question read-only, with its full reveal and the strip note `Answered · Incorrect · 1:12`. In end mode it stays editable.
- Next goes to the next served question, and at the frontier it asks the server for a new one.
- Skipped questions can be answered at any time before Finish.

**Finish, in any mode:** if anything is skipped, unanswered or marked, **CheckYourWork** opens first. It is the same component the test uses:
- tiles: Answered / Unanswered / Skipped / Marked;
- the cell grid;
- an amber note, e.g. '2 skipped. They count as unanswered.';
- `Finish set` / `Back to questions`.

**Time saving:** the client sends time on the current question with POST /time (fetch keepalive) whenever it leaves the question: Next, Previous, a navigator jump, Skip, Exit, visibilitychange to hidden, and pagehide.

###### 2.8 Navigator

**Shape:** a popover above the NavPill, 420 px wide, max 70 vh. On a phone it is a bottom sheet. Esc, an outside click or choosing a cell closes it.

**Header:** 'Question overview', then the view Seg `Status · Difficulty · Skill · Time`.

**Grid:** 8 columns of 40 px cells with a 6 px gap. Each served question is a button.
- A fixed set's future slots are dashed and disabled, with the tooltip 'Comes after question 7'.
- The corner glyphs are the marked notch and the note glyph.

**Views:**
- **Status:** a legend with live counts: `Unanswered 2 · Correct 5 · Incorrect 1 · Mixed 1 · Skipped 1 · Marked 2 · Has note 1 · Current · Again (repair)`. Current is a ring, so it never hides a question's status (theirs does).
- **Difficulty:** band tint plus a corner letter E, M or H. A measured level adds its number (`M4`). Legend: `Easy 3 · Medium 5 · Hard 2 · measured 4`.
- **Skill:** a skill glyph in each cell. The legend is skill chips with counts.
- **Time:** seconds in each cell, and cells over pace get a 1.5 px amber-deep ring. Legend: `Over 1:35: 2 · average 1:04`.

**Footer:** `6 answered · 1 skipped · 2 marked` and `Finish set`, or `Review & finish` in end mode.

**Aria:** each cell has a label such as 'Question 3, incorrect, marked, has note, medium level 4'.

###### 2.9 Overlays

All overlays are UI.popover, UI.menu or UI.sheet. Esc and an outside click close them, and focus returns to the opener.

**DetailsPopover**, a definition list:
- **Question ID:** `lin.affine_conversion · 48213`, with a copy button.
- **Domain / Skill / Question type:** each on its own row, with the type's about line.
- **Difficulty:** `Medium · level 4 of 7, measured from 212 first tries (58% right)`, or `Medium · level not measured yet (3 first tries so far)`.
- **Format.**
- **Why this one:** q.why.
- **You and this type:** `6 answered · 5 right · last Sep 20`, or 'First time'.
- **Everyone:** `58% right first try · most common mistake: …`, or 'Not enough answers yet'.
- **Link to this exact question:** a copy button for /practice/session/?q=lin.affine_conversion:48213, with the toast 'Link copied: anyone who opens it gets this exact question'.
- **Challenge:** the ID and the link read 'Shown after today's challenge closes' until the challenge day is over.

**AttemptsSheet**, 'Attempt history':
- **This question:** a table `# · Result · Answer · Mistake named · Time · When`, e.g. `1 · Incorrect · B · Left out the constant term · 0:41 · 14:05`.
- **This question type, all sets:** the last 20 first tries, e.g. `Sep 20 · Correct · 0:55`, each with `Open`, which replays that exact question as a one-question set.
- **Empty:** 'No attempts yet.'

**ReportSheet**, 'Report a problem':
- A read-only box, 'Sent with your report': the question ID, the skill, the type, the set, your answer, and the device (viewport, browser, light or dark).
- **Category** (radio):
  - Wrong answer key
  - More than one answer is right
  - Typo or unclear wording
  - Figure or table is wrong
  - Looks broken on my screen
  - Difficulty or skill label is wrong
  - Explanation is wrong or unclear
  - Other
- **`What's wrong?`:** a textarea with a 0/2000 counter.
- **`Add screenshots`:** up to 3 files, PNG/JPEG/WebP, 5 MB each, shown as thumbnails with remove buttons. Oversize files and wrong types get inline errors.
- **`Send report`:** a pill, enabled once a category is picked.
- **Success:** 'Thanks. We can regenerate this exact question to check it.' with `Close`.
- **Error:** an .error line, and everything typed is kept.

**MoreMenu** (role menu, arrow keys):
- `Start over with these exact questions`. It confirms: 'Starts a new copy of this set with the same questions. This one stays in your history.' Then it sends {retake}.
- `New set, same settings` sends {again}.
- `Share this set` sends POST share, copies the link, and toasts.
- `Print this set`.
- Checkbox items, saved to prefs:
  - `Answer on first tap`
  - `Always open explanations`
  - `Show every option's mistake` (on by default)
  - `Show question stopwatch` (on by default)
  - `Pace alert`
- `Calculator opens: Closed / Docked / Floating` (a submenu).
- `Keyboard shortcuts`.
- A divider, then `End set now`.

**ExitSheet**, 'Leave this set?', when anything has been answered:
- `Keep it for later`. If the set is timed and pausable, this reads `Pause and keep for later` and POSTs /pause first. It goes to /practice/.
- `End and see summary`.
- `Cancel`.
- In the challenge the first option carries the helper 'The clock keeps running while you are away.'
- With 0 answered, Exit POSTs finish silently and leaves. Such a set is not listed.

**TimeUpSheet:** modal and not dismissable. 'Time's up · 7 answered, 3 unanswered', with a `See summary` pill.

**ShortcutsSheet:** the table in 2.10.

**Calculator** (UI.calc, shared with the test):
- **Dock mode:** the default at 1100 px and wider. A right column with a resize handle on its left edge, and the header `Desmos · Float · ×`.
- **Float mode:** draggable, with a resize corner.
- **Phone:** a 62 vh bottom sheet with a grab bar.
- Its state is kept per set, and its expressions persist across questions.

**Reference:** the formula-sheet dialog.

###### 2.10 Keyboard

Keys are inactive while a text field, a dialog or the calculator has focus, except that Enter checks inside the SPR field.

| key | action |
|---|---|
| A–D, 1–4 | select |
| Shift+A–D | strike / unstrike |
| Enter | Check, Next, or Save & next |
| ← → | Previous / Next |
| S | skip |
| M | mark for review |
| E | eliminate mode |
| L | highlight mode |
| O | my note |
| I | I'm guessing |
| D | details |
| N | navigator |
| C | calculator |
| R | reference |
| H | hide / show timer |
| P | pause |
| ? | shortcuts |
| Esc | close overlay |

###### 2.11 Summary (same URL, when the set is finished)

The RunBar keeps only Exit and the title. The column is max 860 px wide.

1. **ScoreHead:**
   - an eyebrow, `Set complete · Sep 23, 14:22`;
   - a big `7 / 10` (.num, 96 px) beside `70% first-try accuracy`;
   - under that, `Before this set: 62% first try in these skills`;
   - the skill chips.
2. **StatTiles** (4 across, 6 on wide screens): Correct 7 · Incorrect 2 · Mixed 1 (retry only) · Skipped 0 · Unanswered 0 · Time 11:42 · Per question `1:10 · pace 1:35` · Right but guessed 1.
3. **By skill:** one row per skill with its glyph, name, `3 / 4`, `avg 1:05`, and a mastery bar. The bar shows the before value as a ghost fill and the after value in ink, with the words, e.g. `Learning → Getting there`. Each row has a `Practise` link (/practice/?skills=slug). An expandable `By question type` lists each type as `Count solutions · 1 / 2 · 1:30`.
4. **By difficulty:** `Easy 3 / 3 · 0:48`, `Medium 3 / 4 · 1:10`, `Hard 1 / 3 · 2:05`, each with a bar. Then `Levels seen: 2–6 (4 measured)`.
5. **Time per question:** a bar per question, in order, with a 1:35 pace line. Bars over pace are amber-deep. Legend: `Over pace 2 · fastest 0:21 · slowest 2:48`.
6. **Mistakes:**
   - `Opened · 2`: each row has its label, skill and `Fix now` ({pool:'mistakes', templates:[t]}).
   - `Fixed · 1`: each row has a check glyph.
   - `Still open from before · 3`, linking to /mistakes/.
7. **ReviewList:**
   - Filter Seg: `All 10 · Incorrect 2 · Mixed 1 · Marked 2 · Slow 2 · Guessed 1 · Skipped 0 · Has note 1`.
   - Rows: number cell (status fill) | skill glyph and type name | difficulty chip | time | the mistake named, or '—' | marked | note.
   - A quiet `Mark all incorrect for review` above the list.
   - A row opens the **ReviewSheet**. It is UI.workspace, read-only, with:
     - the stem, with your highlights and note;
     - your answer marked, the key, every option's mistake, and the explanation;
     - `Hide answers`, which persists across Next;
     - `Previous` / `Next`, and `3 of 10`;
     - `Mark for review`, `My note`, `Another one like this` (a one-question set), and `Report`;
     - ← → keys.
8. **NextActions:**
   - **With misses:** the primary pill is `Fix my 3 misses` ({from_session}), with the helper '3 new questions on the types you missed'.
   - **With none:** the coach's `Keep going`, with its chips and `10 questions · 16 min`.
   - **Quiet actions:** `Retake these exact questions`, `Same settings, new questions`, `Share this set`, `Print`, `Back to Practice`.
   - **Challenge:** the rank `#4 of 31` and `Board`, with no Retake or Share.
   - **Endless or sprint:** the ScoreHead reads `14 answered · 11 right`.

###### 2.12 Print view (`?id=ID&print=1`)

A print stylesheet: A4 or Letter, black on white, with the orange kept only for the logo mark.

**Worksheet (from the builder):**
- **Page header:** skills, date, count, and `Name ________`.
- **Questions:** numbered, each with its figure and table. MC choices are lettered. A grid-in gets an entry box.
- **Answer key and explanations:** a closing page with each key, its explanation and every option's mistake.
- **Controls:** a checkbox `Include answer key and explanations`, on by default, and a `Print / Save as PDF` pill that calls window.print(). A worksheet set is an end-mode set left In progress, so `Enter answers online` opens it for feedback and filing.

**From the summary:** the questions with your answer, the key, the named mistakes and the explanations.

###### 2.13 Challenge mode

The same page, with these differences:
- no Pause, Skip, Another one like this, Retake, Share, Print, I'm guessing, 'Why this one' or Everyone line;
- repairs are off;
- Answers shown is always After each;
- the ID and permalink stay hidden until the challenge day is over;
- Mark for review is allowed only after answering (the server already enforces this);
- Highlight and My note are allowed;
- the title is 'Daily challenge'.

###### 2.14 States

- **Loading:** the RunBar renders; the workspace shows a skeleton of 3 stem lines and 4 options; the footer is disabled.
- **404:** 'That set does not exist.' with `Back to Practice`.
- **403:** 'This set belongs to a different device code.' with `Back to Practice` and a /me/ link, 'Use that code here'.
- **Finished:** opens on the Summary.
- **Resumed:**
  - It opens on the question you were on: localStorage `satf.pos.ID`, or the server's `at` from another device. An answered question shows its verdict.
  - Marks, strikes, highlights, notes, tries, stopwatch totals, the hidden timer and the calculator are all restored.
  - Toast: 'Picked up where you left off'.
- **Paused on load:** the paused overlay.
- **Answer failed:** the choice unlocks, an .error reads 'Could not send your answer.', and there is a `Try again`. The selection is kept.
- **409 closed:** the TimeUpSheet or the Summary.
- **Exhausted:** the summary note reads 'We ran out of unseen questions for level 7 in Probability. Widen the levels to keep going.'
- **Offline:** the footer .error reads 'You're offline. Your answer will be sent when you're back.', and it retries once on the 'online' event.
- **100+ questions:** the navigator grid scrolls, and the rail becomes the continuous bar.

###### 2.15 Phone (390 px)

- **RunBar**, 52 px:
  - `×`, with a caption 'Exit';
  - the compact TimerBlock: the digits with their left/elapsed caption, a tap to hide, and a separate ∥ button;
  - Calculator, Reference and ⋯ at 40 px each, with 10 px captions.
- **ProgressRail:** 4 px segments. The text line under them starts with the set title: `Linear functions + 2 · 7 of 10 · 5 right`.
- **QuestionStrip**, two rows:
  - row 1: the number, the skill short name, the type name (ellipsis), the difficulty chip, Again;
  - row 2: Mark · Eliminate · Highlight · Note · Details · Report · Attempts, each with a 10 px caption, and the stopwatch at the right end. The row wraps and never scrolls.
- **'Why this one':** wraps under the strip.
- **Choices:** always rows (auto 2x2 is off). The strike circles are 36 px. On touch, highlighting uses long-press selection.
- **SPR:** the rule line and the preview stay visible.
- **Skip:** under the choices.
- **RunFooter:** 64 px plus the safe area, holding `←`, the NavPill `7 / 10 ⌃`, and a Check/Next pill of at least 128 px.
- **Overlays:** Navigator, Details, Attempts, Report, More and My note are bottom sheets with a grab bar, max 88 vh. The calculator is a 62 vh sheet.
- **Summary:** tiles 2 across, ReviewList rows on two lines, the time chart scrolls inside its own box, and NextActions are stacked full width.
- **No horizontal scroll:** figures are max-width 100%, and tables scroll inside .q-table.

---

##### 3. Status and difficulty tokens (orange only, added to ui.css)

| state | look |
|---|---|
| Correct | --wash fill, 1.5 px --amber inset, ✓ in amber-deep |
| Incorrect | paper fill, 1.5 px --ink inset, ✗ in ink |
| Mixed | diagonal split, half --wash and half paper, 1.5 px --amber-deep inset, '~' glyph |
| Skipped | 1.5 px dashed --soft border, '»' glyph |
| Unanswered | --tile |
| Answered (end mode) | --tile-2 with a dot |
| Marked | an ink bookmark notch, top right |
| Has note | a 7 px note glyph, bottom left |
| Current | 2 px --ink outer ring, so it never hides the status |
| Repair | 5 px amber dot, bottom centre |

Difficulty bands, each with a corner letter:

| band | colour | letter |
|---|---|---|
| --lvl-easy | #FDEBD3 | E |
| --lvl-med | #F8BE7A | M |
| --lvl-hard | #F18508 | H, ink-deep |

Level cells 1–7 step through the three bands. Every status carries a glyph, so none depends on colour alone.

### 3.3.4 Extras: what they missed

- **The misconception under every option, shown by default**: After answering, each wrong option shows the mistake that produces it, from Item.reasons, and fillers are labelled honestly. TopTierPrep has one long explanation per item. Only a bank that generates every distractor from a named misconception can do this at our scale.
- **Named mistakes on grid-ins**: The template's own wrong values are matched against the typed answer ('14 is what you get if you used the slope as the intercept'). Today, and at TopTierPrep, a grid-in miss names nothing.
- **Everyone's stats per type**: '58% right on the first try · most common mistake: left out the constant term (41% of misses)', from all learners' attempts. A bank with unnamed distractors can say which letter was popular, but not which misconception.
- **A retry hint that names the misconception, not the key**: In 'After I retry', a wrong try says which mistake it comes from and the key stays hidden. Only the first try counts, so accuracy stays honest. Their retry only says 'wrong', and unlimited retries make accuracy meaningless.
- **Repair: the same trap with new numbers**: The same template on a fresh seed follows a miss, and two clean answers close the mistake. A finite bank has no second copy of the trap.
- **Another one like this (easier / harder)**: One click queues the same type on a fresh seed, or on an adjacent tier. It never runs out.
- **386 question types, searchable**: Every template can be picked on its own, named from its slug and described by its docstring (378 of 386 have one). A search finds 'margin of error' or 'circle equation' across skills. TopTierPrep stops at 19 skills and has no search.
- **Seen before, exactly, with Result, Marked and From filters, plus Due for review**: This covers every combination of their Solved, Marked and Redo selects, and adds spaced review: fresh numbers on types you got right 10+ days ago. Their filters make no sense for an unlimited bank; ours work on types and on exact replays.
- **Shared sets with results for the sharer**: A tutor or study group sends a link, and everyone gets the same questions. The sharer sees takers, the right rate per question, and the most common named mistake on each. Takers choose whether to show their name. This is their hidden Classes/homework idea, free and working.
- **Why this one**: Every question says why the scheduler picked it: an open mistake, a repair, a new type, a step up, a marked question or a test miss. The adaptive system becomes visible and trustworthy, as their plan's 'Why this task?' tries to be.
- **Highlights, underlines and notes that follow the exact question**: They are stored against (template, seed), so a note comes back on replay, on retake, in the review and in Marked. Their annotations live and die with one session.
- **Printable worksheet, and print / save as PDF**: A generated worksheet has an optional key and explanations page, and the summary review can be printed too. A worksheet can also be answered online later for feedback. Their 'Share / Export' is a dead button.
- **End-of-set summary, review list and resumable sets**: Tiles; by skill, by type and by difficulty, with times; time per question against pace; accuracy before the set; mistakes opened and fixed; a filterable review with read-only replay; In progress / Finished / Shared lists. Theirs never ends.
- **Test-style mode in practice, with Check Your Work in every mode**: The same workspace and CheckYourWork as the exam runner, as the user asked ('one format').
- **Exact retake and question permalinks**: (template, seed) regenerates a question exactly, so 'Start over with these exact questions' and a link to one exact question come nearly free.
- **Measured levels 1–7, shown honestly**: Levels come from real first-try accuracy with fixed thresholds, and the page says 'measured from N' or 'not measured yet'. The tier filter always works. Their Question Score is opaque, and missing from their Details.
- **Adaptive difficulty inside a set**: Steps up after 2 first-try rights and down after a miss, per skill. Their 'Adaptive' preference has no visible effect.
- **Pace coaching per question**: A stopwatch that survives reloads, a pace alert at 1:35, 'your average on this type', a Time view in the navigator and a time chart in the summary.
- **'I'm guessing' flag**: A lucky right counts half toward mastery, does not close a mistake, and opens the explanation. This keeps mastery and the mistakes list honest.
- **Pause for practice sets**: The server stores the pause, and the questions are hidden while paused.
- **Skip and come back**: A Skipped state in the navigator, and an answer at any time before Finish.
- **Presets with visible reasons, and a coach line**: Coach's pick, Weakest 3, Plan focus, Full section mix, Mistakes, Missed, Marked and Due each set the tree and the settings in one tap. The coach line says why each skill was picked.
- **Preferences that follow the device code**: Builder defaults and session preferences are stored on the server and edited in one place, so a second device gets them too.
- **Marked tidies itself**: A marked question answered right on replay leaves the list unless you keep it, so Marked stays a to-do list.
- **Grid-in rules, validation, fraction preview and accepted forms**: The 5/6-character rule is checked live. The preview stacks fractions and shows the decimal. After answering, the page lists the other entries that would also have been accepted.
- **Blueprint weight on each domain**: '35% of the test · ~15 of 44' replaces their confusing '20% of test section, 1-5 questions'.
- **Full keyboard map**: Select, strike, check, skip, mark, highlight, note, guess and every tool, with a shortcuts sheet.
- **Endless and sprint sets**: No 'All' ceiling: a set can run forever, or be as many as you can do in N minutes.

### 3.3.5 Server changes

Tables and columns here are added by F4 as listed in §2.5; the drill fields map through §2.6; prefs through §2.7.

- **GET /api/bank (new)**

  The builder's one read.

  Response shape:
  - totals: {domains 4, skills 19, types 386, measured}.
  - domains: [{name, weight, mastery, answered, right, traps, skills}].
  - Each skill: {slug, name, short, mastery, answered, right, by_tier:{easy:[right,asked],...}, avg_ms, last, crowd_rate, traps:[{template,label,hits,owed}], marked, seen, missed, labels:[{label, templates}], types}.
  - Each type: {template, name, about, labels, tiers, formats, level, level_range, measured_n, crowd, answered, right, last, traps, marked, seen, missed, due}.
  - Also coach (with reasons) and counts {traps, marked, seen, missed, untried, due}.

  Where the fields come from:
  - name: the slug after the dot, humanised.
  - about: the first sentence of inspect.getdoc(templates()[t]); 378 of 386 have one.
  - The catalogue part is cached per process. The per-learner part is one GROUP BY template over attempts, plus open_traps, saved and missed.
  - missed = distinct (template, seed) whose first attempt was wrong and which has no later right attempt on the same pair.
  - due = the last first try was right, 10 or more days ago, and there is no open trap.

- **POST /api/drill/preview (new)**

  Takes the same body as POST /api/drill and creates nothing.

  It returns {servable, reason, types, questions (null when fresh), minutes, pools:{new, mistakes, review, untried, seen:{any, missed, right, guessed, marked}}}, counted within the selection and filters.

  The builder calls it debounced at 200 ms. It is the single source of truth for counts, for the Start button's disabled reason, and for the create-time 409, which reuses the same validation.

- **blueprint.kinds() and docstrings**

  The existing 18-seed survey also records it.skill per template:

  kinds() -> {template: {'kinds': set[(tier, fmt)], 'labels': Counter, 'about': str}}

  abilities() is derived from it, so its callers are unchanged. It is warmed at startup as today.

- **Measured levels and crowd stats (drill.levels(), cached for 10 min)**

  One pass over attempts, excluding guess=1, grouped by (template, difficulty). It gives n, first-try rate, and reason counts, with '' and 'near-miss arithmetic slip' excluded.

  Level, when n >= 20:

  | tier | level by rate |
  |---|---|
  | easy | 1 at 85% or more; 2 below |
  | medium | 3 at 70% or more; 4 from 50%; 5 below |
  | hard | 6 at 40% or more; 7 below |

  With fewer tries, level = null and level_range = the tier's band.

  The crowd object {n, rate, top_mistake, share} is present only when n >= 20.

  q['level'] is stored at serve time. The level also goes out through /api/bank, state, answer and finish.

- **POST /api/drill: new body fields**

  New fields, all validated before anything is created:
  - templates: list[str], checked against the catalogue. The topics become the union of topics and topic_of(templates).
  - tiers: list; the legacy difficulty maps here.
  - levels: list[int 1..7].
  - unmeasured: bool = True.
  - formats: ['mcq','spr'].
  - pool: 'new'|'mistakes'|'review'|'untried'|'seen'. mistakes:true maps to 'mistakes'; saved:true maps to 'seen' with marked=true.
  - result: 'any'|'missed'|'right'|'guessed'.
  - marked: bool.
  - from: 'both'|'practice'|'tests'. Tests are sessions of kind mock, module or diagnostic.
  - feedback: 'instant'|'retry'|'end'.
  - repairs: bool = True.
  - adaptive: bool.
  - order: 'mixed'|'grouped'|'ramp'.
  - mix: 'even'|'blueprint'.
  - retake: sid, meaning that set's served (key, seed) in order, with its cfg.
  - again: sid, meaning that set's cfg with new questions.
  - share: code, plus show_name: bool.
  - item: 'template:seed'.
  - source: e.g. 'map', 'plan', 'today', 'mistakes', 'worksheet'.

  Errors: 409 with a reason when nothing can be served; 400 for an unknown template or level; 410 for a revoked share. ramp with count=None gives 400, and so does pace with count=None.

- **drill._pick / _fresh honour the filters and record why**

  _fresh(b, template, tiers, formats, levels, unmeasured) rejects a card by format or by level, and keeps it (b.keep) so the seed advances. The template pool is pre-filtered through kinds().

  Pools:
  - 'untried': templates with 0 attempts.
  - 'review': the queue is the due templates.
  - 'seen': items from the filtered attempts, oldest first. order=mixed interleaves them by topic.

  Order and mix:
  - grouped: blocks per topic.
  - ramp: each slot's target is the level (or the tier) rising evenly.
  - mix blueprint: pick the topic with the largest deficit against domain weight / skills in domain.

  adaptive: cfg['adapt'][topic], stepped in answer().

  repairs=False skips cfg['repair'].

  Every served q gets why = {kind: repair|mistake|replay|new_type|least_used|step_up|step_down|due, detail}. Examples: the trap label and owed; 'Marked Sep 20'; 'Missed on your Sep 22 test'.

- **Skip, revisit, time and position**

  POST /api/drill/{id}/next takes {skip: bool, ms?: int}. skip adds the current unanswered qid to cfg['skipped'], adds ms to it, and serves a new question. It is 'done' when served >= total and nothing unanswered is left.

  answer() accepts any served, unanswered qid, including skipped ones, and removes it from skipped.

  New POST /api/drill/{id}/time {question_id, ms}:
  - ms is capped at progress.MS_CAP per call;
  - cfg['ms'][qid] += ms;
  - cfg['at'] = qid, which is the resume position across devices;
  - it is sent with fetch keepalive, because sendBeacon cannot carry X-Learner.

  New GET /api/drill/{id}/q/{qid} returns {question, status, given, ms, marked, strikes, note, marks, why, tries:[{n, given, correct, mistake, ms, at}], type_history (the last 20 first tries on the template for this learner), feedback}. feedback is included only when it can be revealed: instant or retry once final, or any mode once finished.

- **POST /api/drill/{id}/strike (new)**: Body {question_id, choice 0..3, on}. It updates cfg['strike'][qid], and state and /q return the strikes. It is allowed in the challenge too.
- **drill.state returns the whole set**

  New fields:
  - served: [{id, n, topic, skill, type_name, difficulty, level, why, repair, status, marked, has_note, strikes, ms, tries, guess}]. status is unanswered, answered (end mode), correct, incorrect, mixed or skipped.
  - current, at.
  - feedback, repairs, adaptive, order, mix.
  - paused, seconds_left and elapsed, computed on the server.
  - pace: 95.
  - can: {pause, skip, more, retake, share, guess, permalink}. For the challenge all are false; permalink turns true once its day has passed.

  A timed set past its clock plus GRACE is finished inside state() and inside the list, so end-mode answers are filed even if the tab was closed.

- **answer(): the three feedback modes, guess, grid-in mistakes and crowd**

  Body: {question_id, answer, ms, guess?}. ms adds to cfg['ms'][qid].

  instant: as today, and the response adds:
  - reasons (per option; '' for the key);
  - filler (per-option bool);
  - accepted (SPR, from scoring.accepted_forms);
  - status;
  - pace {ms, type_avg_ms};
  - crowd (null in the challenge);
  - removed_from_marked (on a right replay of a marked item, unless keep_marked).

  retry:
  - The first try claims and files the attempt as today.
  - A wrong first try returns {correct:false, final:false, mistake, filler, tries_left:2}, with no key or rationale.
  - Later tries go into the tries table, and a named reason files a trap hit via progress.record_trap.
  - final:true comes with the full feedback, and a right later try makes the status mixed.

  end:
  - set_answer without only_new.
  - Nothing is filed until finish.
  - The response is {saved:true, answered}.

  guess=true stores attempts.guess=1.

- **POST /api/drill/{id}/reveal, /more, /pause, /resume (new)**

  reveal: retry mode only. It ends the tries and returns the full feedback, with status incorrect.

  more: body {question_id, step:-1|0|1}. It queues the same template, at an adjacent tier when kinds() allows, as the next serve. A fixed total grows by 1. Returns {total}.

  pause and resume: record cfg['paused_at'] and cfg['paused_s']. overtime, seconds_left and elapsed subtract the paused time. While paused, answer, next and more return 409 'paused'.

  All of these return 409 for the challenge or a finished set.

- **finish(): a richer result**

  New fields:
  - mixed, skipped, unanswered;
  - accuracy (first try);
  - before_accuracy: first-try accuracy in these topics before started;
  - avg_ms, pace;
  - by_difficulty {tier: {right, asked, ms}};
  - by_type [{template, name, right, asked, ms}];
  - levels_seen, measured_seen;
  - guessed_right;
  - questions [{id, n, topic, skill, type_name, difficulty, level, status, ms, mistake, marked, has_note, repair, guess}];
  - fix: the count of missed templates.

  In end mode it first files every answered question through progress.record, in order, with cfg['ms']. It keeps one attempt per question for the counts. A finish with 0 answered stores asked 0, and such sets are not listed.

- **GET /api/drill (new): the learner's sets**

  Returns {active, recent, shared}.
  - active: unfinished and with 1 or more answered, newest first.
  - recent: the last 200 finished with asked > 0. It accepts ?topic=, ?kind= and ?misses=1.
  - shared: the owner's shares, with taken and avg.

  Each set row is {id, kind, source, started, finished, topics, total, answered, right, ms, timed, seconds_left, paused, feedback, pool, share}. kind 'challenge' is included.

- **Shares: POST /api/drill/{id}/share, GET /api/share/{code}, GET /api/share/{code}/results, DELETE /api/share/{code}**

  Table: shares(code TEXT PRIMARY KEY, owner, source, items, cfg, created, revoked). code = secrets.token_urlsafe(6), and sharing the same set twice returns the same code.

  GET /api/share/{code} is public and never includes answers: {count, topics, timed, minutes, feedback, owner_name, taken, avg_right}.

  GET /api/share/{code}/results is owner only (403 otherwise): {taken, avg_right, median_ms, questions:[{n, template, type_name, difficulty, right, asked, top_wrong:{given, reason, count}}], takers:[{name|null, right, asked, ms, at}]}. name appears only when that taker set cfg.show_name and has learners.name.

  DELETE revokes the share.

  POST /api/drill {share} copies the items and cfg and stores cfg.share and cfg.show_name. Challenge sets cannot be shared.

- **POST /api/report (new, multipart)**

  Fields:
  - session, question_id;
  - category: wrong_key|two_right|wording|figure|display|label|explanation|other;
  - details: 2000 characters or fewer;
  - context: JSON {viewport, ua, theme, url};
  - files: 0–3, PNG/JPEG/WebP, 5 MB each (413 / 415 otherwise).

  The server resolves template, seed and the given answer from the stored question and inserts:
  - reports(id INTEGER PRIMARY KEY, learner, session, qid, template, seed, category, details, given, context, at);
  - report_files(report_id, name, type, data BLOB).

  30 or more a day per learner returns 429. Each report is logged at warning level with the template and seed. The exam runner, the report review, the question of the day and the challenge use the same endpoint.

- **Notes and highlights: POST /api/notes (new)**

  Body {session, question_id, note?: ≤1000 characters, marks?: ≤50 × {start, end, style: 'hl'|'solid'|'dashed'|'dotted', target: 'stem'|'choice:0-3', note?: ≤300}}.

  The server resolves template and seed and upserts notes(learner, template, seed, note, marks, at), with PRIMARY KEY (learner, template, seed). Empty values delete the row.

  Notes are returned by /q, as state has_note, and in the /api/mistakes marked rows as a note excerpt. The exam runner's question payload should include them too; that is noted for the Test section.

- **Preferences: learners.prefs**

  LATER_COLUMNS gains ('learners','prefs','TEXT').

  PUT /api/me {prefs} merges partial keys and validates each one: count, timing, minutes, tiers, levels, unmeasured, formats, feedback, repairs, adaptive, order, mix, pool, first_tap, open_explanations, option_reasons, stopwatch, pace_alert, calc ('closed'|'dock'|'float'), hide_timer.

  GET /api/me returns profile.prefs. progress.carry uses COALESCE on prefs.

- **progress: coach reasons, guess-aware mastery, record_trap, grid-in mistakes**

  - coach() adds reasons: {slug: {kind: mistakes|new|weak|review|focus, traps, mastery, first_try_rate, since_days}}.
  - record_trap(learner, q, reason, when) is split out of record().
  - mastery_of takes (difficulty, correct, guess), and a guessed right adds half its weight.
  - board, topic_mastery and bank select guess.
  - A correct answer with guess=1 does not decrement owed.
  - For a wrong SPR, record() matches the given value against q['spr_reasons'] with scoring.grid_equal and files the matched reason instead of the skill label.

- **satbank Item.spr_mistakes (grid-in misconceptions)**

  Item gains spr_mistakes: list[Mis] (default []). In the SPR branches of templates that already compute a mistakes list, the list is computed before the branch and passed in. lin.evaluate is one: it computes mistakes after its SPR return today.

  practice.to_question stores spr_reasons: [[reason, value_text]], and audit checks that no spr_mistake value equals the key. Coverage grows template by template, and a check script prints '<n> of 133 grid-in templates name their mistakes'. Templates without them keep today's behaviour.

- **scoring.accepted_forms(answer) (new)**: For an SPR key, returns up to 5 entries that grid_equal accepts: the fraction, then the decimal truncated and rounded to fill 5 characters (6 with a minus), with and without the leading 0.
- **Repeats: shelf sections and diagnostic forms remember what they serve**: start_mock (/api/mock/{num}) and new_session (the diagnostic) call db.remember for the learner with every question they carry that has a key and seed. After that, the Repeats line is true.
- **Challenge permalink gate**: state.can.permalink and the /q ID fields for kind 'challenge' are withheld until the session's day is before daily.today() for the learner's time zone.
- **Saved is renamed 'Marked for review' in copy only**: The saved table and /api/saved stay as they are. /api/bank and state read the table as marked. A right replay of a marked question deletes the saved row unless the answer body has keep_marked:true.
- **Tables and columns (db.py)**

  New tables:
  - tries(learner, session, qid, n INTEGER, given TEXT, correct INTEGER, reason TEXT, ms INTEGER, at TEXT);
  - shares;
  - reports and report_files;
  - notes.

  LATER_COLUMNS gains:
  - ('attempts','guess','INTEGER NOT NULL DEFAULT 0');
  - ('learners','prefs','TEXT').

  progress.carry() also moves tries, shares.owner, reports.learner and notes. notes uses UPDATE OR IGNORE and then DELETE, like saved.

- **test_flow.py coverage**

  Add checks for:
  - /api/bank totals (4/19/386), with 6 types in Statistical claims;
  - preview counts, and the 409 on an unservable selection;
  - templates-only sets;
  - tiers, levels and unmeasured, with a seeded level measurement;
  - skip with ms, then answering later;
  - /time and at;
  - strike persistence;
  - retry mode hiding the key until final, and mixed at finish;
  - end mode leaking nothing and filing only at finish, including the lazy finish of an overtime set;
  - more growing the total, with the same template and a new seed;
  - pause freezing seconds_left;
  - retake giving identical stems;
  - share to a second learner, share results for the owner (403 for others), and revoke (410);
  - a multipart report with a file (413 on oversize);
  - notes round-trip across a retake;
  - prefs round-trip;
  - GET /api/drill lists, and 0-answered sets excluded;
  - guess not closing a trap;
  - a grid-in value matched to a named mistake;
  - challenge refusing pause, more and skip, and withholding the permalink;
  - a shelf mock writing practice_seen.


### 3.3.6 Files this spec names, and who owns each

| file | owner |
|---|---|
| `web/practice/index.html` | S4 |
| `web/practice/session/index.html` | S4 |
| `web/assets/ui.js` | F2 |
| `web/assets/ui.css` | F1 |
| `web/me/index.html` | S1 |
| `web/mistakes/index.html` | S10 |
| `server/drill.py` | F5 → S4 |
| `server/app.py` | F0 (routers register themselves, §2.10) |
| `server/progress.py` | F4 |
| `server/practice.py` | F5 → S4 |
| `server/db.py` | F4 |
| `server/blueprint.py` | F5 → S5 |
| `server/scoring.py` | F4 |
| `server/daily.py` | S3 |
| `server/test_flow.py` | shared: new checks go in server/checks/<task>.py |
| `satbank/item.py` | T-bank |
| `satbank/topics/*/families/*.py` | T-bank |
| `README.md` | shared: each task edits its own subsection |
| `spec/rebuild.md` | F0 (superseded by this file) |

A file owned by another task is met through §2.9: the owner builds it, or this section's task adds its hook on its own page.

### 3.3.7 Shared needs

- **Need → built in F3 question.js / runner.js**

  UI.workspace(host, q, opts): one question component that replaces UI.question. It is used by the practice session, the exam runner (web/test/, feedback='end'), the summary and report ReviewSheet, the question of the day and Mistakes. It covers:
  - the QuestionStrip and its tools;
  - select-then-Check;
  - Eliminate, saved to the server;
  - Highlights, underlines and notes;
  - auto 2x2;
  - the SPR field with its rule line, stacked-fraction preview and validation;
  - per-option misconceptions;
  - the retry state;
  - the read-only review with a persistent 'Hide answers';
  - I'm guessing.
  The user asked for the exam runner and practice to share one format.

- UI.navigator(host, cells, {views}): the Question Overview with Status / Difficulty / Skill / Time views, legends with counts, future slots, note and marked glyphs, and aria-labels. It is reused by the exam runner's navigator and the report's question grid. → built in F3 question.js / runner.js
- UI.checkYourWork: the tiles, the grid and the unanswered note. It is shared by practice Finish and the test module submit. → built in F3 question.js / runner.js
- UI.popover, UI.menu, UI.sheet: an anchored popover; a menu with arrow keys; a modal sheet that becomes a bottom sheet on phones. All close on Esc and an outside click and return focus to the opener. → built in F1 kit.js
- UI.report(context): the ReportSheet with screenshots and device context, posting to /api/report. It is shared with the exam runner, the report review, the question of the day and the challenge. → built in F6 report.js  
  ↳ R17: UI.report (F6 report.js)
- UI.timer: countdown or stopwatch with a left/elapsed caption, Hide (kept in prefs), Pause, and toasts at 5 min and 1 min, all driven by the server's seconds_left. The exam runner uses it without Pause. → built in F3 question.js / runner.js
- UI.calc extended: Dock (a resizable column), Float with a resize corner, and a phone sheet, with the default from prefs.calc and state kept per set. It replaces test.js's own openCalc and dragCalc. → built in F3 question.js / runner.js
- UI.masteryWord(m, answered): 'Not started' / 'Learning' / 'Getting there' / 'Strong'. It is named so, because UI.band already formats score ranges. Results, Today and Plan use it for the same labels. → built in F1 kit.js
- learners.prefs via GET/PUT /api/me: builder defaults and session preferences. The Me section's Learning preferences edit the same object, with no duplicate store.  
  ↳ R11: one prefs registry (F4 prefs.py), UI.prefs (F2)
- Notes and highlights keyed by (template, seed): the exam runner's payload and the Mistakes Marked list must show them.  
  ↳ R6: the notes table and POST /api/notes (F4), UI.annotate (F3)
- **Need**

  ui.css additions:
  - Seg, tri-state Checkbox, ToolButton with a caption;
  - status tokens (correct / incorrect / mixed / skipped / answered / marked / note / current / repair) and --lvl-easy/med/hard;
  - stat tiles, a fixed ActionBar above the phone tabs, skeleton rows, toasts;
  - a print stylesheet for worksheets and reviews.

- The SkillTree component (domain cards, tri-state rows, stats): reused by Results' skill list and Plan's focus step.
- Deep-link contract /practice/?skills=&types=&pool=&result=&marked=&tiers=&levels=...: it presets the builder only. Plan, Today and Mistakes start sets by POSTing /api/drill with their own source; the Plan section decides how a plan task is marked done.
- Rename 'Saved' to 'Marked for review' across Mistakes, Me and Results copy. Marked leaves the list after a right replay unless Keep is ticked.  
  ↳ R5: the flags table (F4), endpoints in S10; R5: not done; Mark and Save stay two things
- The exam runner adopts the RunFooter, CheckYourWork, the keyboard map, the highlight tool and /api/report, so practice's end mode and a test are the same experience.  
  ↳ R17: UI.report (F6 report.js); R22: one map, §2.8
- Shelf mocks and diagnostic forms write practice_seen (a server change the Tests and Diagnostic sections should know about).

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

### 3.3.9 This section's open questions

Folded into Part 5 where they need a decision; kept here for context.

- Reading & Writing: this is Math-only. The spec shows no R&W tab until an R&W bank exists; the eyebrow 'SAT MATH' states the subject. OK?
- Official-item replicas: the sources.py files pin templates to official College Board items' numbers. Should an 'Official-item replicas' pool stand in for their Question Bank | TTP Bank toggle? College Board's reuse terms need checking first. Left out for now.
- Levels: are the thresholds acceptable (easy 85%; medium 70/50%; hard 40%; at least 20 first tries), and is 'Level' the right name, versus 'Question score'? At launch almost nothing is measured, and the strip says so.
- The default for 'Answers shown': 'After each question' (as specified) or 'After I retry'?
- Select-then-Check replaces one-tap submit by default, with 'Answer on first tap' as a preference. OK?
- Pause in timed practice sets (never in the challenge), even though the real test cannot pause?
- Shared sets: names appear only when the taker opts in. Is 'Student N' acceptable otherwise, and does a revoked share also need to hide its results?
- Reports: screenshots stored as sqlite BLOBs (max 3 × 5 MB), read by a maintainer with sqlite for now. Is a /admin/reports page wanted?
- Grid-in named mistakes need template edits across up to 133 grid-in templates. Ship the UI with partial coverage and grow it, or wait for full coverage?
- Marked: a right replay removes the question from Marked unless 'Keep marked' is ticked. Is that the right default?
- Crowd stats minimum: 20 first tries across all learners before 'Everyone' lines show. Higher, to protect privacy on a small user base?

---

## 3.4 Practice tests and the test window

> **Spec title:** Practice tests: the catalog (/tests/) with the estimated score, test kinds, shared Papers and their discussion, and your sittings; the start sheet; and the test window (/test/) with its lobby and fullscreen gate, navigator, Check your work, the step between modules, time's up, Save and exit, resume and sharing  
> **Built by:** S5 (pages and server), F3 (runner shell, navigator, Check your work, calculator, highlights), F6 (report, shares)  
> **Read with resolutions:** R5, R6, R7, R16, R17, R18, R21, R22, R28, R32, R36, R38 (§2.2). Where this spec disagrees with them, they win.

### 3.4.1 What they have

- **Estimated Score card**: At the top of /practice/full-length. Empty state: 'Complete a full-length test or a practice module to get your score estimate.' It fills in from a full test or a single module. With data (live walk) it reads 'Math 200-280', a red 'LOW CONFIDENCE' chip, and 'Math estimate only. Practice Reading & Writing to see your total score range.' Behind it is summary {status PARTIAL, sections.math {average 220, min 200, max 280, attempts 1}, confidence {level, label, reason}, trend {direction, delta}, headline}. Bug: a section sitting at the 200 floor is dropped from the estimate even though it was practised.
- **Section tab bar**: One tab, 'Full-Length Tests' (outlined, full width), with room left for more test types. A hidden route /practice/diagnostic has the same filters minus Type and the empty state 'No diagnostic tests match the selected filters.' Nothing links to it.
- **Difficulty filter**: A Radix dropdown pill with radio items and a check on the chosen one: All / Easy / Medium / Hard. It is an editorial label on each paper.
- **Type filter**: All / Adaptive / Non-adaptive.
- **Status filter**: All / Not Attempted / In Progress / Completed.
- **Access filter**: All / Free / Paid.
- **Sort By**: Newest / Oldest / Hardest / Easiest. The chosen value is printed under the label, in orange.
- **Paper card grid**: Three columns, 29 to 31 cards: 'Paper #N', 'September Predictions', 'AUGUST PREDICTIONS (2026)'. Papers are dated like official forms. Every student who sits Paper #47 gets the same questions, which is what makes 'People took' and comments mean anything.
- **Card: Report button**: A flag button labelled 'Report' in the card header. It opens the shared report modal for that exam.
- **Card: tags**: Free (green) / Adaptive or Non-Adaptive / Standard.
- **Card: stat tiles**: Two tiles: 'People took N' (abbreviated, e.g. '1.6k') and 'Your last score' ('Not taken' when empty). A 'Custom Set · 2 Modules' sitting doesn't count, so the card still says 'Not taken' after one.
- **Card: Comments N**: A full-width gray button with the comment count. It opens the comments modal.
- **Card: Start Exam**: A full-width blue 'Start Exam >' button that opens the start wizard.
- **Paid-paper lock**: The same card, blurred, under an overlay: a lock circle, 'Paid exam', 'Unlock it with Pro or Elite' and 'See plans'. The free tier gets 1 exam attempt, and paid tiers get 20 or 30 exams plus 10 or 20 retakes a month.
- **Comments modal**: 'Comments 8 · Paper #47'. A threaded list (avatar, name, timestamp, text, Reply, and 'Show N reply' to expand), a sticky composer 'Add a comment...' with a round send button, and a skeleton while it loads. There is no spoiler guard, no sorting, no question reference and no visible moderation, so what people post is low-quality chatter.
- **Report modal**: 'Report this exam'. A read-only 'Sent with your report' box (Exam, title, Exam ID uuid). Title prefilled, with a 0/200 counter. Category: General feedback / Bug or something broken / Wrong answer key / Typo or content error / Feature request / Other. Details textarea 0/5000. 'Add images' (JPEG/PNG/WebP/GIF, up to 10, 50 MB each). 'Send feedback'. The same modal serves exams, questions and vocab. The student never hears back.
- **Start wizard: step 1**: A modal with a segmented progress bar. 'How do you want to practice?': Full Test (all 4 modules) or Select Modules (choose 1 or more).
- **Start wizard: step 2 (Select modules)**: A 2x2 grid of checkable cards, each with a coloured subject chip (R&W purple, MATH green) and 'Module 1 · 27 questions · 32 min'. A non-adaptive paper offers a fixed 'Module 2 · Hard'. It has Select all / Clear and 'N of 4 selected'.
- **Start wizard: step 3 (Timer mode)**: Timed ('Official time limits apply') or Untimed ('No time pressure'). Back / Start Exam. There are no extended-time options and no calculator or tool options. Preferences (Practice Mode Timed/Untimed, Show Desmos Calculator) live separately on the Profile.
- **Fullscreen gate**: A dark full page at /practice/session?id=: 'Enter Fullscreen Mode · This exam runs in fullscreen, just like the Digital SAT', an 'Enter Fullscreen' button, a 'Proceed without entering full screen mode' link, and a square badge showing '8'. It doesn't say what the test holds or how long it runs.
- **Runner chrome**: No app sidebar. A multicolour dashed rule (Bluebook trade dress) under the header, above the footer and under the question strip.
- **Header: section title + Directions**: 'Section 1, Module 1: Reading and Writing' and a Directions link that opens the official directions in a modal with Close.
- **Timer with hide**: A large mm:ss countdown in the centre with an eye-slash toggle. When hidden, only the eye icon shows.
- **Highlights & Notes toggle**: A pen icon labelled 'Highlights & Notes' in the header, on the right.
- **More menu**: ⋮ opens a menu with 'Save and Exit'.
- **Calculator**: Math only. The Desmos graphing calculator in a floating panel you can drag and resize. The header button shows an active state, and the question column moves over to make room. Its state is not kept.
- **Reference**: Math only. A modal with the official formula sheet as an image.
- **Layout**: R&W: two panes with a draggable divider that turns blue while dragging. Math: one centred column about 750px wide. On every math SPR item the left pane shows 'Student-Produced Response Directions' and an examples table (Answer / Acceptable / Unacceptable).
- **Question strip**: A number square; Mark for Review (a bookmark that turns yellow, with the label changing to 'Unmark'); Report; and an ABC toggle that adds a strike-out circle beside each choice. A struck choice gets an 'Undo' link.
- **Choices**: Full-width rows with a 2px black border, radius 8, and a circled letter. The selected choice gets a 3px blue border and a filled letter.
- **Highlights and notes**: With H&N on, selecting text shows a toolbar with 4 colours (yellow, green, blue, pink), 3 underline styles (solid/dashed/dotted) and Note. Clicking a highlight opens a popover: 'No note' / Remove (red) / Close. There is no list of notes.
- **SPR input**: Placeholder 'Enter your answer (e.g., 5.566, -5.566, 2/3, -2/3)' with a monospace 'Answer Preview:' line under it. The field accepts any characters.
- **Footer**: A light blue-gray bar. The student name on the left; a centre pill 'Question 1 of 27 ⌄' (filled blue); navy Back and Next pills on the right.
- **Module navigator**: A popover titled 'Section 1, Module 1: Reading and Writing Questions'. Legend: Current (pin), Unanswered (dashed), For Review (red flag), with no counts. A grid of question cells and a 'Go to Review Page' button. Esc doesn't close it.
- **Check Your Work page**: '← Back to Test' and the title. 'Review your answers / Select a question to return to it. Once you submit, you can't come back to this module.' Three stat cards (ANSWERED / UNANSWERED / FOR REVIEW) and a grid (answered solid gray, unanswered dashed, review yellow with a bookmark). An amber warning: '26 questions unanswered. Unanswered questions are marked incorrect.' Footer: Back to Test | '✓ Next Module', or '✓ Finish Module' on the last module.
- **Module sequence**: Modules run in order, with no break screen between selected modules. A handed-in module can't be reopened.
- **Resume in-progress**: Save and Exit, plus the 'In Progress' status filter on the catalog, let a student come back to an unfinished exam. It doesn't show how much time is left or where they stopped.
- **Share (QBank, from their bundle)**: Share creates a shared session at /question-bank/shared/:shareId with a 'Start Practice' landing, and toasts 'Share link copied to clipboard'. In the walk, navigator.share froze the page. There is no share for exams, and nobody sees how the other person did.
- **Classes and homework (hidden routes)**: /my-classes and /teacher: a teacher can assign 'a full practice test with timed modules and breaks' with a due date and a time limit. Students see 'Your answers are saved as you go. Submit when you're done.' and [Finish Homework]. Nothing in the sidebar links to it.
- **Score report handoff**: Finishing goes to /results/{sessionId}: rings per section, the total, a 'Practice test — not ranked' pill, tiles, domain performance, the question grid and a review modal. A percentile ('N% scored at or below you on their first attempt') appears only for ranked sittings. That page belongs to the Report section and is listed here only as the destination.

### 3.4.2 What we have now

Status is have / partial / missing / worse, against theirs.

- **Estimated score on the tests page**: *missing.* /tests/ has no score. The latest band is shown only on Results and Today. There is no confidence level, trend, route rate or count of sittings anywhere.
- **Catalog of test kinds**: *worse.* Two 'doors' (44 questions · 70 min, 22 · 35 min) and a Diagnostic text link. The cards have no tags, stats, report or options, and the unlimited bank is hidden behind two numbers.
- **Shared fixed forms (their paper grid)**: *partial.* server/mocks.json already holds 7 fixed adaptive sections (1.1–1.7, each with module1, module2_lower and module2_upper), served by POST /api/mock/{num} and GET /api/mocks. No page links to them any more (only the archived site did). /api/mock/{num} takes the learner in the body, not X-Learner, and invents an anon code when there is none.
- **Difficulty / Type / Status / Access / Sort filters**: *missing.* There are no filters, on the catalog or on the sittings list.
- **Per-kind and per-paper stats (people took N, your last score)**: *missing.* None on the doors.
- **Comments / discussion**: *missing.* Left out on purpose (spec/rebuild.md: 'theirs are noise'). Nothing replaces what comments were for.
- **Report a problem (exam, question)**: *missing.* There is no report anywhere on the site: no endpoint and no table.
- **Paywall / lock**: *have.* Everything is free, which is better than theirs, and nothing needs building.
- **Start flow: full vs select modules**: *partial.* Only the full section or module 1 on its own. There is no fixed module 2 (harder or easier) and no wizard.
- **Timer mode**: *partial.* The 'Timed' toggle shows only on the full door, but it sets one shared variable, so the module door silently inherits it. Untimed hides the clock completely, with no elapsed time. No extended time.
- **Test defaults / preferences**: *missing.* There is nowhere to set default timing or calculator, like their Profile's Learning Preferences.
- **Fullscreen gate / lobby**: *missing.* There is none. The clock also starts when the sitting is created (POST /api/mock/new sets module_started), not when the student begins. Today and Plan call /api/mock/new {full} and drop the student straight onto a running clock.
- **Runner format**: *worse.* web/test/ is a standalone Bluebook copy with its own CSS: dashed trade-dress .rule elements, a black number square, and none of ui.css. The user wants it in the practice session's format. The practice session (web/practice/session/) has a different top bar, options and fonts, and no footer.
- **Runner identity and loading**: *worse.* test.js mints its own learner code with Math.random and no storage fallback, bypassing UI.learner (crypto.getRandomValues, the fixes in d95bf35 and 23adce0). load() catches every failure (404, 500 or offline) and silently serves a built-in 4-question SAMPLE test whose answers go nowhere. Opening /test/ without ?s= POSTs a new diagnostic on every visit.
- **Section label**: *worse.* A fresh mock shows 'Section 2, Module 1: Math' when there is no section 1. A single module shows 'Module 1: Math'.
- **Directions**: *have.* A modal with College Board's math wording. It doesn't open by itself at the start of a module, as Bluebook's does.
- **Timer + hide + 5-minute warning**: *have.* Server-derived, so a reload is not free time. Hide/Show is a text button. At 5:00 it unhides with '5 minutes left'. This is better than theirs.
- **Highlights & Notes**: *missing.* #annotateBtn exists but is hidden unless the question has a passage, so math never gets it. There is no highlighter or notes code.
- **More menu → Save and Exit**: *worse.* More holds a single red 'End the test' (#b3261e, off-brand). On module 1 of a section it actually hands in module 1 and routes to module 2, so the label is wrong. There is no Save and exit and no pause.
- **Calculator**: *partial.* Desmos, draggable, with an Expand toggle. It can't be resized or docked, its state is lost on reload, and there is no no-calculator option.
- **Reference sheet**: *have.* A drawn SVG sheet in a dialog.
- **Mark for review**: *partial.* Works, but lives only in client memory (S.marked), so it is lost on reload or module change.
- **ABC eliminate + Undo**: *partial.* Works, but is client-only (S.out) and lost on reload. No keyboard shortcut.
- **Report question from the strip**: *missing.* No button.
- **SPR input + answer preview**: *partial.* maxlength 6 and a one-line rule. The preview is the raw text ('Answer: 2/3'). No character validation, no placeholder with examples, no examples table, no rendered fraction.
- **Footer: student name**: *missing.* #who is set from data.name, which the payload never sends, so it is always blank.
- **Module navigator**: *partial.* Legend: Current / Answered / For review, with no counts. No 'Go to review page' and no filters. It closes on an outside click and on Esc.
- **Check Your Work page**: *missing.* On the last question Next reads 'Finish' and hands the module in at once. Verified: with 1 of 22 answered it went straight to 'End of Module 1' with no warning about the 21 blanks.
- **Between modules**: *worse.* A modal: 'End of Module 1 · You cannot return to this module. The next one starts when you continue.' The server has already started module 2's clock (module_started=now() at routing), so time spent on the modal is lost.
- **Time's up**: *partial.* At 0 the client auto-finishes, with no screen that says what happened. The server accepts answers after time is up (put_answer never checks remaining()).
- **Resume an unfinished test**: *partial.* Only through the ?s= URL. /tests/ lists finished sittings only (history filters on finished), so a test left mid-module can't be found.
- **Sittings list on /tests/**: *partial.* Rows show the date, kind and band only. No per-module score, misses, time, route or status; no filters, sort, export, Review, Fix, share or retake actions.
- **Answer saving**: *worse.* post() chains fetches and swallows every error (.catch(() => {})) without checking the status. A dropped request is lost silently, and there is no save indicator.
- **Per-question time in tests**: *missing.* record_paper files test answers with ms=None, so tests add nothing to study time or pacing analysis.
- **Keyboard**: *have.* A–D choose, ←/→ move, Esc closes the navigator. That is more than theirs, but there are no keys for mark, eliminate or tools, and no shortcuts sheet.
- **Fresh test per sitting**: *have.* blueprint.py builds module 1 at the start and module 2 for the route earned, from unseen questions. This is our real edge, but the UI never says so.
- **Ownership of a sitting**: *partial.* GET/POST /api/session/{sid}/* and /results don't check X-Learner. Anyone holding the id can read or answer.
- **Plan test day on Today**: *partial.* /api/today 'tested' counts any finished mock or module today, which will wrongly include discarded, custom or practice-variant sittings once they exist.

### 3.4.3 Design

#### Tests, the start sheet and the test window

##### Review changes

What this review changed in the proposed spec, and why:

1. **Papers added: their paper grid had no equivalent.** The draft replaced their 29-paper catalog with seven "kind" cards and moved every filter onto the history list. That dropped the one thing a shared paper gives: everyone sits the same questions, so "People took", your rank and a discussion mean something.
   - The 7 fixed sections already in `server/mocks.json` become **Papers #1–#7**.
   - The server builds **one new paper every Monday**, the way the daily challenge is built: once, from a seed, the same for everyone. So the shelf grows forever instead of running out.
   - Their filters now apply to papers:
     - **Difficulty** is *measured* from everyone's first sittings (Easier than most / Typical / Harder than most), not an editorial label.
     - **Status**: Not sat / In progress / Completed.
     - **Sort**: Newest / Oldest / Hardest / Easiest / Most sat.
     - **Access** (paid) has nothing to filter, so it is replaced by **New to you**, which counts the paper's questions you have already met.
   - The draft's "Everyone" stat on fresh kinds compared different forms. Papers compare like with like, and the percentile counts first sittings only, as theirs does.
2. **Discussion added: their Comments had no equivalent.** Private notes don't replace a conversation. Discussion is per paper, threaded one level, and each post can be tagged to a question ("M1 Q17", which opens your review of it).
   - It opens only after you've sat the paper. That prevents spoilers and keeps out drive-by chatter.
   - Top / Newest sort, Helpful, report-to-hide at 3 reports, edit or delete your own for 15 minutes, 20 posts a day, and a moderation tool.
   - Private sitting notes and question notes stay.
3. **Estimated score card fixed.** It now shows everything theirs carries, and more:
   - a **confidence level with its reason**, a headline, the range of your sittings, and how many sittings are counted;
   - **Routed up (4 of 6 sections)**.
   - Floor-score sittings still count, which fixes their bug.
   - The Exam row shows "Set a date" instead of disappearing.
4. **Sittings list.**
   - Added a **Route** filter and **Hardest / Easiest / Most missed** sorts.
   - Blank questions show as outlined chips, apart from wrong ones. Theirs lumps them together, and that is the contradiction in their report.
   - **Export CSV** (their Share/Export button is dead), **Share**, **Retake**, and Paper and Shared kinds.
   - Actions sit on their own line and are never hidden behind a ⋯ menu.
5. **Share a test (extra; the equivalent of their QBank Share and teacher homework).** Any finished sitting's exact questions can go to a friend by link. Both scores show once both have finished.
6. **Keyboard map fixed.** In the draft, C meant both "choose C" and "calculator". Now the calculator is **G** and Highlights & Notes is **L**; the rest of the map has no clashes.
7. **Report.**
   - The button is labelled "Report" on the question header and on cards. The draft had it icon-only, against its own "labels everywhere" rule.
   - It takes up to **10 images including GIF**, matching theirs. They are shrunk on the device, so the server stays small.
   - The student sees what happened: "Your reports" with status in Me, and `tools/reports.py` to act on them.
8. **Grid-in directions.** At 1180px and wider, a left rail on *every* grid-in question, as their SPR pane does. Narrower, a disclosure that stays open until the student collapses it, and that choice is remembered. The placeholder with examples is added.
9. **Starting a test is faster.**
   - A card's **Start** is one tap into the lobby, using your defaults.
   - The lobby shows every setting with **Change**, editable until Begin (`POST /cfg`).
   - Defaults live in the profile (the equivalent of their Learning Preferences), not only in localStorage, so they follow the code to another device.
   - Today and Plan land on the lobby too, never on a running clock.
10. **Phone** keeps the × (Save and exit) in the top bar. The draft buried it in More.
11. **Server corrections to the draft.**
    - A sitting with a learner now *requires* a matching X-Learner. The draft let a missing header through.
    - **Discard no longer sets `finished`.** It would have counted as a plan test day on Today and been fed to Fix.
    - `scored` now excludes a single harder or easier module 2.
    - Fixed-route sittings are flagged and kept out of Combined and all percentiles.
    - An answer made before time ran out but delivered late (offline) is accepted within 15 minutes when it carries `made_left ≥ 0`, and is counted as late.
    - `/test/` without `?s=` no longer creates a diagnostic.
    - The built-in SAMPLE test that appeared on any load failure is removed.
    - The runner uses `UI.learner` instead of its own Math.random code.
    - Today's `tested` counts only whole sections, modules, papers, twins and shared tests.
12. **More extras from our bank.**
    - **Confidence tags** (Sure / Unsure / Guess) for calibration in the report.
    - A **Time view** on Check your work.
    - **Away time** (time out of the window while the clock ran).
    - **Custom test from your open mistakes, saved questions or a sitting's misses**, under test rules.
    - A sticky **section nav with counts** (their tab bar, done better).

**Ground rules**
- **Behaviour is Bluebook's**, so test day holds no surprises:
  - one module at a time, with answers changeable until the module is handed in;
  - mark for review, eliminate, the navigator and Check your work;
  - no way back into a handed-in module;
  - a clock that can be hidden, with a 5-minute warning.
- **The look is the practice session's**, which is the user's pick:
  - Paper white, and a centred 700px column.
  - Source Serif 4 stems at 20px, warm `--tile` options with circled letters, and DM Mono for clocks and counts.
  - A sticky top bar and a sticky footer.
  - The Bluebook dashed rules, black number square and ruled question strip go. They are College Board trade dress, and the teardown says to copy the behaviour, not the chrome.
- **Orange is the only accent.**
  - It marks the selected answer, marked-for-review, and the live or recommended thing.
  - Answered is graphite (`--ink`).
  - Destructive actions are graphite behind a confirm sheet, never red.
  - Low confidence is graphite with a dashed outline, never red.
- **Labels everywhere.** Every tool and action has a text label. Icon-only is allowed only below 760px, and then it carries an `aria-label` and a tooltip. Legends carry counts. Short helper lines appear where they help a student decide. No decorative copy.
- **Nothing a student does is lost.** Answers, marks, eliminations, highlights, notes, confidence tags and time per question live on the server. They come back after a reload, or on another device with the same code.

---

##### 1. One runner shell for tests and practice

The test window and the practice session become **one shell**, in `web/assets/runner.js` and `runner.css`, with a `mode` switch. It keeps the practice session's look and adds a sticky footer that both modes use. TopTierPrep's QBank session has the same bottom bar: Previous · Question N of 10 · Check/Next.

| region | practice (`mode:'practice'`) | test (`mode:'exam'`) |
|---|---|---|
| top-left | × End set | × Save and exit · title "Math · Module 1 of 2" · Directions ⌄ |
| top-centre | progress strip (right = amber, wrong = ink) + "4 / 10" | clock `34:57` + Hide; progress strip under it (answered / unanswered / marked / current) |
| top-right | Timer (if timed) · Save · Calculator · Reference · More | Highlights & Notes · Calculator · Reference · More |
| question header | skill glyph + skill + difficulty + mastery bar · Save · Eliminate · Report | `Q7` badge · Mark for review · (Sure/Unsure/Guess) · Eliminate · Report |
| choosing an option | locks; the key, the named mistake and the rationale appear | selects (can change), saved, nothing revealed |
| footer | Previous · "Question 3 of 10 ⌃" · Check / Next | Back · "Question 7 of 22 ⌃" · Next / Review |
| navigator | Status (unanswered / right / wrong / mixed / saved / current) or Difficulty | answered / unanswered / for review / current, with filters |
| end | summary | Check your work → next module, or hand in → report |

**Sizes, desktop:**
- top bar 64px;
- progress strip 16px hit area with 4px segments;
- column `max-width:700px`, top padding `clamp(20px,5vh,48px)`, bottom padding 120px;
- footer 68px;
- tool buttons auto width, min 56px.

**Phone (<760px):** top bar 56px; footer 64px plus `env(safe-area-inset-bottom)`; side gutters 16px.

---

##### 2. `/tests/`

###### 2.1 Desktop layout (1280, content max 1120)

```
[shell bar]
Tests                                                  How scoring works (quiet)
Every test is built when you start it, from questions you haven't seen. Papers are the same for everyone.
┌ T1 Estimated score (2fr) ─────────────────────┐ ┌ T2 Up next (1fr) ──────┐
└───────────────────────────────────────────────┘ └────────────────────────┘
┌ T3 In progress (full width, only when any) ─────────────────────────────┐
[sticky section nav]  New test 7 · Papers 8 · In progress 1 · Your sittings 12
New test
┌ T4 card ┐ ┌ T4 card ┐ ┌ T4 card ┐      (3 columns ≥1000px, 2 at 600–999, 1 below)
Papers  8                          [Difficulty ▾][Status ▾][New to you ▾][Sort ▾] Clear
┌ T5 paper ┐ ┌ T5 paper ┐ ┌ T5 paper ┐                              Show all 8
Your sittings  12      [Kind ▾][Status ▾][Route ▾][Timing ▾][Sort ▾] Clear   Export CSV
T6 rows…                                                          Show 20 more
```

**Section nav (`#secnav`)**
- Sticky under the shell bar: 44px, `--paper` background, with the shell's scrolled shadow.
- Items, 600 14px, each with a DM Mono count:
  - New test (the number of kinds);
  - Papers (the number of papers);
  - In progress (the number unfinished; this item is shown only when there are any);
  - Your sittings (the total).
- Clicking scrolls to the section. A scroll-spy sets `aria-current` and a 2px amber underline.
- On a phone the nav scrolls sideways inside itself (`overflow-x:auto`), so the page never does.

###### 2.2 T1: Estimated score card (`#score`)
A `--tile` card, radius 14px, padding 24px, in two columns.

**Left column**
- `k` label "Estimated Math score", then a confidence chip (600 12px, 24px high, radius 8px):
  - **High** on `--wash`;
  - **Medium** on `--paper`;
  - **Low** on `--paper` with a 1px dashed `--faint` outline.
- The band, e.g. "560–700" (`.num`, `clamp(48px,6vw,72px)`).
- **Headline** (15px ink), built from the trend and the target. It is one of:
  - "Your first estimate"
  - "Up 40 since Sep 12 · 100 short of your 700 target"
  - "Level with Sep 12"
  - "Down 30 since Sep 12"
  - "At your 700 target"
- Source (meta): "From Full section #4 · Sep 23 · harder module 2", plus "· 580 cap" when capped and "· extended time" when that applies.
- **Confidence reason** (12.5px soft). It is one of:
  - "Low: only a module or the diagnostic so far. One full section narrows it to about 140 points."
  - "Medium: one full section. Two within 100 points of each other make it high."
  - "Medium: your last sections are 120 points apart."
  - "High: 3 sections in the last 30 days within 100 points."

**Right column**
- A mini band chart of the last 8 scored sittings, 120px tall: `UI.bandChart(host, sittings, {height:120})`. The newest band is orange.
- A 2×3 grid of fact rows (label in `k`, value in 600 15px):
  - **Best**: 580–720.
  - **Combined, last 3 sections**: 590–690 **(extra)**. Shown when there are 2 or more full sections at standard settings. It is the mean midpoint ± 70/√n, rounded to 10. Fixed-route, extended-time and variant sittings are left out.
  - **Range of your sittings**: "480–620", the lowest and highest midpoints of every scored sitting.
  - **Routed up** **(extra)**: "4 of 6 sections". It tells a student how often module 1 earns the harder module 2, which is the gate to the 600s.
  - **Target**: "700 (Plan)", linking to `/plan/`. When none is set: "Set a target", linking to `/plan/`.
  - **Exam**: "Oct 3 · 10 days", from the profile. When none is set: "Set a date", linking to `/plan/`.
- Under the grid (meta): "Counted: 6 sittings · 4 sections, 1 module, 1 diagnostic". A sitting at the 200 floor still counts.

**States**
- **Empty** (no scored sitting):
  - The band reads "—" and the chip reads "No data".
  - Line: "No estimate yet. A full section gives a band about 140 points wide; one module or the diagnostic, about 200."
  - The chart area shows the 200–800 axis with no bands.
- **Loading:** skeleton blocks (`--tile-2`) where the band, the chart and the facts go.
- **Error:** "Couldn't load your score." plus a quiet "Retry".

###### 2.3 T2: Up next (`#next`), tied to the coach and the plan
A `--wash` card, radius 14px, padding 22px. It holds a `k` "Up next", a title (700 18px), a meta line, one orange pill, and an optional quiet alternative.

What it recommends, in this order:
1. **An unfinished sitting exists.**
   - Title: "Finish Full section #12".
   - Meta: "Paused · 21:40 left".
   - Pill: "Resume".
2. **Today is a plan test day** (`UI.plan.dayOf(today, profile)` = 'test') and `today.tested` is false.
   - Title: "Today's test: full section", or "module" when `plan.testOf(minutes)` = 'module'.
   - Meta: "44 questions · 70 min".
   - Pill: "Start". It goes straight to the lobby with your defaults.
   - Quiet alternative: "Sit this week's Paper #8 instead", shown when it is unsat.
3. **Brand-new learner** (no attempts).
   - Title: "Start with the diagnostic".
   - Meta: "20 questions · 32 min · all four domains evenly".
   - Pill: "Start".
4. **This week's paper is unsat** and the last test was at least 3 days ago.
   - Title: "New this week: Paper #8".
   - Meta: "Sat by 214 so far · 44 questions · 70 min".
   - Pill: "Start".
5. **Otherwise.**
   - Title: "Full section".
   - Meta: "Your last was 9 days ago", or "Next test day: Saturday" when a plan exists.
   - Pill: "Start".

Under the pill, when no plan is set: quiet "Plan your test days", linking to `/plan/`.

###### 2.4 T3: In progress (`#live`)
- Shown only when unfinished, non-discarded test sittings exist.
- Up to 3 rows, newest first. When there are more: "Show all 5", which sets the sittings Status filter to In progress and scrolls there.
- Each row is a `--wash` tile, radius 12px, padding 16px 18px, grid `1fr auto`.

**Left side**
- Title: "Full section #12" or "Paper #8" (700 15.5px).
- Meta: "Module 1 of 2 · 14 of 22 answered · 3 marked".
- State line (DM Mono 13px). It is one of:
  - "Paused · 21:40 left"
  - "Clock running · 12:03 left", when the student left without Save and exit and the clock kept going
  - "Time ran out · answers saved"
  - "Untimed · 18 min so far"
  - "Not begun", for a sitting that was built but never begun
- Started (meta): "Started today 9:14".

**Right side**
- Pill "Resume". Its label is "Continue" when time ran out, and "Begin" when the sitting was never begun.
- Quiet "Hand in": opens `/test/?s=ID#review`.
- Quiet "Discard": opens the confirm sheet "Discard Full section #12? Its 14 answers won't count anywhere. This can't be undone." with [Keep it] [Discard]. Discard calls `POST /api/session/{id}/discard`, and the row animates out.

###### 2.5 T4: New test (`#kinds`)
Each `.kind` card has a `--tile` background, radius 14px, padding 20px 20px 18px, and is a flex column with a 14px gap.

- **Header row:** the title (700 17px) and a quiet "Report" button (flag icon plus label, 13px). It opens `UI.report` with `context:'catalog'`.
- **Tags row:** chips 26px high, radius 8px, 600 12px, on `--paper`. The "Adaptive" tag is on `--wash`.
- **Facts line:** DM Mono 13px, ink.
- **Stat tiles:** two or three `.stat` tiles, each a `k` label over a 600 17px value.
  - "Everyone": "1,284 sittings". Once there are 30 or more scored sittings of that kind, a second line appears: "Your last beats 62% of fresh sections".
  - "You": your last result, or "Not taken". **Every sitting of the kind counts, including module-only and fixed-route ones**; a sitting marked as practice shows "17/22 · practice".
  - "Best": your best band, or "—".
- **Actions row:** Start, plus a quiet "Options" that opens the start sheet at that kind's step 2.
  - **Start is one tap.** It builds the sitting with your defaults and opens the lobby, where every setting can still be changed.
  - The recommended card (the same kind as T2) gets the orange pill.
  - The other cards get `.btn-2`: 44px, `--paper` background, ink text, radius 999px.

The cards, in order:
1. **Full section**
   - Tags: Adaptive · Official timing · 15/15/7/7 blueprint
   - Facts: "44 questions · 70 min · 2 modules"
   - Stats: Everyone / You (band) / Best
2. **Module 1**
   - Tags: Mixed difficulty · Official timing
   - Facts: "22 questions · 35 min"
   - Stats: Everyone / You ("17/22 · 460–660") / Best
3. **Module 2 · harder** (the upper module, fixed)
   - Tags: Fixed · Leans hard
   - Facts: "22 questions · 35 min"
   - Helper (12.5px soft): "What a strong module 1 earns you."
4. **Module 2 · easier** (the lower module, fixed)
   - Tags: Fixed · Leans easy
   - Facts: "22 questions · 35 min"
   - Helper: "Its score tops out at 580, as on the SAT."
5. **Custom test (extra)**
   - Tags: Your skills or mistakes · Test rules
   - Facts: "5–60 questions · you choose"
   - Helper: "No answers until you hand in, like a real module."
   - Start opens the start sheet at the custom step.
6. **Diagnostic**
   - Tags: All four domains evenly
   - Facts: "20 questions · 32 min"
   - Helper: "Asks for your name and email before the result." (see open questions)
7. **Twin of your last test (extra)**
   - Shown only when a finished section, paper or module exists.
   - Title: "Twin of Full section #11".
   - Tags: Same slots · New numbers
   - Facts: "44 questions · 70 min"
   - Helper: "Every question is the same kind, at the same difficulty and position, with new numbers. An equal test, to see whether you've improved."
   - Stat: "Original" band.

Everything is free, so there is no lock state and no Access filter.

###### 2.6 T5: Papers (`#papers`): shared forms, their paper grid done better
- **Header:** `k` "Papers", a count (DM Mono), and a helper line (13px soft): "The same questions for everyone who sits them, so your score compares directly. A new paper every Monday."
- **Filter bar (`#paperFilters`, `UI.dropdown`):**
  - **Difficulty:** All / Easier than most / Typical / Harder than most / Not rated yet. The rating is measured from everyone's first standard sittings, once a paper has at least 20. It compares the paper's mean share of weight earned with the mean across rated papers, with ±0.05 counting as Typical.
  - **Status:** All / Not sat / In progress / Completed.
  - **New to you:** All / Mostly new to me (90% or more of its questions unseen).
  - **Sort:** Newest / Oldest / Hardest / Easiest / Most sat. Unrated papers sort last for Hardest and Easiest.
  - "Clear" appears when any filter isn't All.
  - Filters are written to the URL (`?p.diff=hard&p.sort=new`) and to localStorage `satf.tests.paperFilters`, with every access in try/catch.
- **Grid:** 3/2/1 columns, like T4.
- **`.paper` card:** `--tile`, radius 14px, padding 20px.
  - **Header:** "Paper #8" (700 17px). The newest paper has a "New this week" chip on `--wash`. On the right, a quiet "Report" (flag plus label).
  - **Sub (meta):** "Week of Sep 21, 2026", or "Launch set" for #1–#7.
  - **Tags:** Adaptive · Official timing · the rating chip ("Harder than most", or "Not rated yet").
  - **Stats (three `.stat` tiles):**
    - "Sat by": 1,284, counting first sittings. It is written in full, with a thousands separator.
    - "Average": 540, the mean midpoint of first standard sittings. It reads "—" below 20.
    - "You": one of "560–700", "Not sat" or "In progress · 14/22".
  - **Line (meta):** "New to you: 63 of 66", plus, once you've sat it and it has at least 30 first sittings, "· your first sitting beats 62%".
  - **Actions:**
    - Start: `.btn-2`, or the orange pill when T2 recommends this paper. Its label is "Start", "Resume" or "Retake".
    - Quiet "Options".
    - Quiet "Discussion 12". Before you've finished the paper it reads "Discussion 12 · opens after you sit it", and it opens the sheet in its gated state.
- **States:**
  - Shows 6 papers, then "Show all 8".
  - Loading: 3 skeleton cards.
  - Filtered empty: "No papers match these filters." plus "Clear filters".
  - Error: "Couldn't load papers." plus Retry.
- **Retakes:** allowed at any time. A retake is labelled "Retake 2" in the sittings list, and it never counts toward the paper's Sat by, Average, rating or percentile.

###### 2.7 Discussion sheet (`#talk`, 640px `dialog.sheet`; full-height on a phone)
- **Header:** "Discussion · Paper #8" with the count, and ×. Under it:
  - Sort `.choices`: Top / Newest.
  - An "About" filter dropdown: All / The whole paper / Module 1 / Module 2 (harder) / Module 2 (easier) / a specific question.
- **Gated** (you haven't finished this paper):
  - "Sit Paper #8 first. The discussion talks about its answers."
  - The count of posts.
  - Pill "Start Paper #8".
  - No post text is sent to the client in this state.
- **Post:**
  - The board name (600 14px; the profile name). If a code has no name, it shows as "Student".
  - Relative time (DM Mono 12px soft), with "edited" when edited.
  - Plain text, pre-wrapped, never rendered as HTML, with links not linkified.
  - A question chip such as "M1 Q17". It opens your review of that question at `/results/report/?id=MYSID&q=M1-17`. For a module 2 you didn't get, the chip reads "M2 harder Q5 · not on your route" and opens nothing.
  - Actions (quiet, 13px):
    - Helpful, with a count. `aria-pressed`, one per code.
    - Reply.
    - Report.
    - Edit and Delete, on your own post within 15 minutes.
- **Replies:** one level. After two replies they collapse to "Show 3 more replies".
- **Composer:** sticky at the bottom.
  - A textarea (2 lines growing to 6, 0/500).
  - An "About" select: The whole paper / M1 Q1–Q22 / M2 harder Q1–Q22 / M2 easier Q1–Q22.
  - A round Send button with `aria-label` "Send".
  - With no board name, a line above it: "Your name on the board" [field, 24 max] [Save], which calls `PUT /api/me {name}`.
- **States:**
  - Loading: 3 skeleton posts.
  - Empty: "No posts yet. Ask about a question, or say how the paper went."
  - Error on load: inline, plus Retry.
  - Error on send: the text is kept, with "Couldn't send. Retry".
- **Moderation:**
  - 3 reports from different codes hide a post, which then shows as "Hidden after reports" to everyone but its author.
  - 20 posts a day per code (429 shows "You've posted 20 times today").
  - `tools/moderate.py` lists reported posts and can hide, restore, or mute a code.

###### 2.8 T6: Your sittings (`#sittings`)
- **Header:** `k` "Your sittings", a count (DM Mono), the filter bar `#filters`, and a quiet "Export CSV" **(extra)**.
  - Export downloads the rows as they are filtered, built on the client as a Blob, as `sat-freshman-sittings.csv`.
  - The columns are: number, date, kind, band, M1, M2, route, timing, minutes, misses, blanks and note.
- **Filter bar.** Each control is `UI.dropdown`: a button showing the label in `k` style with the value in 600 14px underneath (their "Sort By · Newest" pattern). It opens a listbox menu with radio items and a check. Esc closes it and the arrow keys move through it.
  - **Kind:** All / Full sections / Papers / Modules / Custom / Diagnostics / Twins / Shared.
  - **Status:** All / Completed / In progress / Timed out.
  - **Route:** All / Harder module 2 / Easier module 2 / Fixed route (the sitting was started with a fixed module 2).
  - **Timing:** All / Official / Extended / Untimed.
  - **Sort:** Newest / Oldest / Highest / Lowest / Hardest / Easiest / Most missed.
    - Highest and Lowest go by band midpoint, or by the share right when there is no band. Unscored rows sort last.
    - Hardest and Easiest go by the mean difficulty weight of the questions asked.
  - "Clear" (quiet) appears when any filter isn't All.
  - Filters are written to the URL (`?kind=section&sort=high`) and to localStorage `satf.tests.filters`, with every access in try/catch.
- **Row (desktop), two lines, padding 14px 16px, radius 10px, `--tile` on hover.**
  - **Line 1:** a grid `44px 120px minmax(0,1.2fr) 150px 70px 70px 90px minmax(0,1.4fr)`. The columns:
    - `#12` (DM Mono).
    - The date, "Sep 23 · 9:14" (DM Mono 12.5px soft).
    - The kind, e.g. "Full section", "Paper #8", "Paper #8 · Retake 2", "Shared by Ana" or "Twin of #11", with a sub-line "Adaptive · official" (12px soft).
    - The score:
      - "560–700" (800 17px), or "17/22" for unscored kinds, or "Practice" for kinds that give no estimate.
      - Chips under it: "Harder M2" or "Easier M2" when a route is set, "580 cap", "Fixed route", "Extended", "Paused 2×".
    - M1: "17/22".
    - M2: "15/22", or "—" for a single module.
    - Time: "64 min", or "Untimed · 81 min".
    - Misses, one group per module, e.g. "M1 3 8 14 · M2 2 9 +4" (at most 8 chips, then "+N"):
      - a **wrong** answer is a small ink chip with a white number;
      - a **blank** is an outlined chip (1.5px dashed `--faint`) with an ink number;
      - a chip links to `/results/report/?id=ID&q=M1-3`;
      - a tooltip reads "M1 Q3 · wrong" or "M1 Q9 · blank".
  - **Line 2:** the actions (quiet 13px buttons, wrapping), then the note.
    - "Review"
    - "Fix 7", shown only when there are misses. It calls `POST /api/drill {from_session}` and opens the session page.
    - "Twin"
    - "Retake" (papers)
    - "Try the harder module 2", on a section or paper that routed lower. It starts a single upper module 2 (the paper's own, for a paper).
    - "Share" (see 2.9)
    - "Note"
- **Note (extra):** a private note to yourself per sitting, e.g. "ran out of time on 18–22".
  - It shows at the end of line 2, in italic serif 14px.
  - Editing is inline: a textarea with 0/1000 and Save / Cancel, sent with `PUT /api/session/{id}/note`.
- **In-progress rows** appear here too when Status is All or In progress, with Resume in place of Review.
- **Pagination:** 20 rows, then "Show 20 more".
- **States:**
  - Loading: 4 skeleton rows.
  - Empty, new student: "Nothing sat yet. Your first full section gives your first score estimate."
  - Filtered empty: "No sittings match these filters." plus "Clear filters".
  - Error: "Couldn't load your sittings." plus Retry.

###### 2.9 Share a test (extra)
- **Share, from a finished sitting's row** (and from the report, which the Report section coordinates), opens `#shareSheet`:
  - A read-only link field `https://…/tests/?shared=K7Q2M9XA`, plus a "Copy" pill. It toasts "Link copied". If the clipboard is blocked, it selects the text.
  - A toggle "Show my score to people who sit it" (on).
  - The line: "Anyone with the link sits these exact questions. They see no answers until they finish, and you'll see how they did."
  - A quiet "More ways to share" calls `navigator.share` only when it exists and only on that tap. Theirs froze on an automatic call.
- **Landing (`/tests/?shared=CODE`):** the start sheet opens at a "Shared test" card.
  - It shows: "Full section shared by Ana", "Sep 23", "44 questions · 70 min" and "Sat by 3".
  - Beneath it: "Module 1 is the same as Ana's. Module 2 matches hers when you earn the same route."
  - Timing and Tools follow as usual. Start opens the lobby.
  - Error states: an unknown code shows "This link doesn't lead to a test." A code whose owner deleted their data shows the same.
- **After finishing**, the report shows everyone who sat that share: names, or "Someone", with their bands when the sharer allowed scores. The Report section renders this.

###### 2.10 How scoring works (`#howScored` sheet) (extra)
A plain-language version of scoring.py and the README. It covers:
- The ordinal heuristic, which is not IRT.
- The band widths: ±70 for a section or paper, ±100 for a module or the diagnostic.
- The route cut at 60% of module 1, and the 580 ceiling on the easier module 2.
- That harder or easier module 1, a single module 2 and custom tests show "Practice, not a score estimate".
- That fixed-route and extended-time sittings keep an estimate, flagged, but stay out of Combined and percentiles.
- How confidence is decided.
- That papers compare first sittings only.
- That floor-score sittings count.

###### 2.11 Phone (390)
One column, 16px gutters, no horizontal page scroll.
- **Section nav:** sticky, scrolling inside itself.
- **T1:**
  - The band at 48px, with the confidence chip beside the label.
  - The chart below the band at full width, 110px tall.
  - The fact rows as a 2-up grid.
- **T2 and T3:** stacked.
- **T4 and T5:** one column. Start and Options sit side by side; Discussion goes on the next line.
- **Filter bars:** the dropdowns in a 2-column grid, with "Clear" and "Export CSV" under them.
- **T6 row as a card:**
  - Line 1: `#12 · Sep 23`, with the score on the right.
  - Line 2: the kind · M1 17/22 · M2 15/22 · 64 min.
  - Line 3: the miss and blank chips, wrapping (at most 6, then "+N").
  - Line 4: the actions, wrapping.
  - Line 5: the note.
- **Dropdown menus and sheets** (Discussion, Share) open as bottom sheets or full-height sheets.

---

##### 3. The start sheet (`#start`, `dialog.sheet`, 640px; a full-height sheet on a phone)

- **Header:** the title "Start a test", a close ×, and a stepper of 4 segments (4px bars, amber when done or current) with labels under them: Test · Modules · Timing · Tools. The labels can be clicked to go back.
- **Footer:**
  - Quiet "Back".
  - A summary line in DM Mono, e.g. "Paper #8 · adaptive · 44 questions · 70 min · calculator on".
  - The pill "Next" or "Start".
- **Behaviour:**
  - Start is available from step 2 on; Timing and Tools are prefilled from your defaults.
  - Enter moves forward, Esc closes.
  - **Defaults** come from `profile.test_prefs`. A "Save these as my defaults" checkbox in Tools (on) writes them back with `PUT /api/me {test_prefs}`. The equivalent of their Learning Preferences, it follows the code to another device, and Me shows and edits the same settings.
  - **Deep link:** `/tests/?start=section|module1|module2u|module2l|custom|diagnostic|twin|paper:8` opens the sheet preset. `/tests/?shared=CODE` opens it at the shared card.

**Step 1 · "What do you want to sit?"**
Radio cards in a 2×4 grid (one column on a phone), each with a title and a facts line:
- Full section
- Choose modules
- A paper: a nested dropdown of papers, "Paper #8 · this week · not sat"
- Custom test
- Diagnostic
- Twin of #11 (only when there is a source)
- Shared test (only from a link)

The diagnostic goes straight to Start, with no Modules or Tools steps.

**Step 2 · Modules** (it depends on step 1)
- **Full section or a paper.** Two segmented controls:
  - "Module 2": **Adaptive** (like the SAT) / **Always harder** / **Always easier**. This is their Adaptive vs Non-adaptive.
  - "Module 1": **Standard** / **Harder** / **Easier** **(extra)**.
    - Sections only; a paper's module 1 is fixed.
    - Harder and Easier use the new tiers `module1_upper` (easy 3 / medium 8 / hard 11) and `module1_lower` (11/8/3). This is their Difficulty filter.
  - Helper lines, each shown only when it applies:
    - "Harder or easier module 1 is practice, not a score estimate."
    - "A fixed module 2 keeps an estimate, scored as if module 1 had routed you there. It is flagged and left out of Combined and percentiles."
    - For a paper: "Only the whole paper at official timing counts toward its Sat by and Average."
- **Choose modules** (for a section or a paper). This is their Select Modules.
  - Checkable cards, each with a DM Mono "MATH" chip on `--wash`:
    - "Module 1 · 22 questions · 35 min · mixed"
    - "Module 2 · harder · 22 questions · 35 min"
    - "Module 2 · easier · …"
  - The two module 2 cards exclude each other.
  - "Select all" checks Module 1 and Module 2 harder. "Clear" unchecks everything.
  - A counter: "2 of 2 modules · 44 questions · 70 min".
  - Module 1 plus a module 2 becomes a section with that fixed route. At least one card must be checked, or Start stays disabled with the note "Pick at least one module".
- **Custom test (extra):**
  - **"Questions from"** (segmented):
    - **Skills**
    - **My open mistakes (9)**: one question per open mistake, same template and new numbers, under test rules. It checks whether a fix holds under the clock.
    - **Saved (12)**: the exact saved questions.
    - **A sitting's misses**: a dropdown of finished sittings with misses, then the same templates with new numbers.
  - **Skills picker** (Skills only):
    - 4 domain groups of skill chips (`UI.chip` with glyph). A domain header toggles all of its skills.
    - An open-mistake dot sits on each chip, and each chip shows its mastery %.
    - Presets: "Weak spots" (the coach's `ahead[0]` plus open-mistake topics), "Focus domains" (from the plan's Focus), "All", "Clear".
  - **Length:** 10 / 22 / 44, plus a number field (5–60). For mistakes and saved the length is set by the count, capped at 60.
  - **Order:** "Easiest first, like a module" / "Mixed".
  - **Formats:** Both / Multiple choice only / Grid-in only.
  - **Difficulty:** Easy / Medium / Hard toggles, at least one.
  - A live line: "22 questions · 35:00 at test pace".
  - Start stays disabled until there is at least 1 skill, or the chosen source has at least 1 question.
- **Twin.** No choices. Shows the source ("Full section #11 · Sep 12 · 520–660") and "Same 44 slots, new numbers".
- **Shared.** No module choices. Shows the source card from 2.9.

**Step 3 · Timing**
Radio cards, each with a title and the resulting clock:
- **Official:** "35:00 a module" (custom: "95 s a question · 35:00").
- **Time and a half (extra):** "52:30 a module".
- **Double time (extra):** "70:00 a module".
- **Untimed:** "The clock counts up, so you still see your time".
- Custom only: **My own minutes**, a number field of 1–180.

**Step 4 · Tools** (defaults shown)
- Fullscreen: on.
- Calculator: on. Off gives no-calculator practice, and the tool is hidden **(extra)**.
- Pace guide on the progress strip: on **(extra)**.
- Confidence tags (Sure / Unsure / Guess on each question): off **(extra)**. Its helper: "Your report then shows how often your sure answers were right."
- Tell me which module 2 I got: off, as in Bluebook **(extra)**.
- Save these as my defaults: on.
- A summary card, e.g. "Full section · adaptive · official timing · calculator on".

**Start**
- The pill reads "Building…" with `aria-busy` while `POST /api/mock/new` is in flight (about 0.2s measured), then navigates to `/test/?s=ID`, which is the lobby.
- **Error:** inline under the footer, "Couldn't build the test. Check your connection and try again." The pill works again.

---

##### 4. `/test/`: the test window

###### 4.1 Screens and URL
The URL is `/test/?s=ID` plus a hash. The page updates the hash with `replaceState` when moving between questions, and with `pushState` for `#review`, so the browser's Back returns from review to the question.

`/test/` with no `?s=` creates nothing: it redirects to `/tests/?start=diagnostic`. The diagnostic page's Start does the same.

| screen | when | hash |
|---|---|---|
| Loading | fetching the session | — |
| Lobby | `begun:false` (fresh, or module 2 not yet begun), or paused | `#lobby` |
| Question | live | `#q7` |
| Check your work | from Next on the last question, the navigator or More | `#review` |
| Between modules | module 1 of a section handed in, module 2 not begun | `#between` |
| Time's up | the clock hit 0 | `#timeup` |
| Handing in | final finish in flight | — |
| Problem | 404 / 403 / network | — |

A finished sitting redirects to `/results/report/?id=ID`. A finished diagnostic goes to signup, as today. **There is no built-in sample test any more.** A failure shows the Problem screen.

###### 4.2 Lobby (`#lobby`): the fullscreen gate, done better
A centred 640px `--wash` card, radius 14px, padding 28px. The shell's top bar shows only the × (back to Tests).

**Fresh**
- `k` "Math", then "#12".
- The h1 (`.h1`): "Full section" / "Paper #8" / "Module 2 · harder" / "Custom test" / "Diagnostic" / "Twin of Full section #11" / "Shared by Ana".
- Fact rows, each with an icon and 15px text:
  - "2 modules · 22 questions each"
  - "Module 2 is chosen by how module 1 goes", or "Module 2 is the harder one, fixed"
  - "Once you move on, you can't go back to a module"
  - "Every question is new to you". For a paper or shared test: "63 of its 66 questions are new to you".
- **Settings rows**, each with its value and a quiet "Change":
  - Timing: "35:00 for each module", or "52:30 for each module · time and a half", or "Untimed · the clock counts up".
  - Calculator: "Calculator and reference sheet on every question", or "No calculator on this test".
  - Pace guide: on/off.
  - Confidence tags: on/off.
  - Tell me my module 2: on/off.
  - Change opens a small sheet with that control, saved with `POST /api/session/{id}/cfg`. It is allowed only before Begin. The module choices can't change here; for those, a quiet "Start over with other modules" discards this unbegun sitting and opens the start sheet.
- Buttons:
  - Pill "Enter fullscreen and begin", and quiet "Begin without fullscreen".
  - Only a "Begin" pill where `document.fullscreenEnabled` is false (iOS Safari), or when the Fullscreen tool is off.
- Quiet links under the buttons: "Directions" · "Keyboard shortcuts".

**Paused (resume)**
- `k` "Paused". h1 "Full section #12".
- Facts: "Module 1 of 2 · 14 of 22 answered · 3 marked" and "21:40 left. The clock is stopped until you resume."
- Pill "Resume" (with fullscreen), quiet "Hand in module 1", quiet "Discard this test".

**Left without Save and exit**
The same card, with the fact "You left without Save and exit, so the clock kept running: 12:03 left."

**Expired while away**
"Time ran out while you were away. Your 14 answers are saved." The pill "Continue" goes to `#timeup`.

**Behaviour**
- The server sends no questions before Begin or while paused, so neither the lobby nor a pause is free reading time.
- Begin calls `POST /api/session/{id}/begin`, and the clock starts then. This fixes today's clock, which starts at creation.
- On a section's first Begin, the Directions sheet opens over question 1 with a "Close" pill, as in Bluebook. A "Don't show at the start" checkbox is stored in localStorage.

###### 4.3 The question view

**Top bar (`#top`, sticky, 64px, grid `minmax(0,1fr) auto minmax(0,1fr)`)**
- **Left:**
  - `#exit`: a 40px × button with the label "Save and exit" at ≥1180px and `aria-label` "Save and exit". It opens a confirm sheet: "Save and exit? The clock stops until you come back, and this test waits under In progress on Tests." with [Keep going] [Save and exit].
  - `#title`: "Math · Module 1 of 2" (700 15px). Other titles: "Paper #8 · Module 1 of 2", "Math · Module 2 (harder)", "Custom test".
  - `#dirs`: quiet "Directions ⌄" (13.5px). It opens the Directions sheet.
- **Centre (`#clock`):**
  - `mm:ss` in DM Mono 500 22px, tabular.
  - The eye toggle `#clockHide`: a 32px icon with the label "Hide"/"Show" at 11.5px under it on desktop. When hidden, "Show time" takes the place of the digits.
  - The hidden state is kept per sitting (localStorage `satf.clock.{sid}`).
  - Under 5:00 the digits go `--ink-deep` 600, the clock unhides once, and a toast under the bar reads "5 minutes left" for 6s.
  - Under 1:00 the digits pulse once a minute. Reduced motion turns this off.
  - Untimed: the clock counts up, with an "Elapsed" label (`k`) above it.
- **Right (`#tools`).** Each tool is a button with a 20px icon over an 11.5px 600 label (auto width, min 56px). Pressed: ink label, amber icon fill, and a 2px amber underline.
  - **Highlights & Notes** (`#toolAnnotate`), Bluebook's own label.
  - **Calculator** (`#toolCalc`; hidden when the calculator is off).
  - **Reference** (`#toolRef`).
  - **More** (`#toolMore`).

**Progress strip (`#strip`, under the bar, centred at 700px)**
- 22 segments (`flex:1`, max 28px, gap 4px, 4px tall), in a 16px hit area.
- Segment states:
  - answered: `--ink`
  - unanswered: `--line`
  - current: a 1.5px inset ink ring
  - marked: a 5px amber dot above the segment
- **Pace tick (extra):** a 2×10px `--amber-deep` tick at the question you'd reach at the test's pace (elapsed ÷ (seconds per question × timing factor)). It shows when Pace guide is on and the test is timed, with the tooltip "Pace: question 12".
- Desktop: hovering a segment shows a tooltip, e.g. "Question 7 · answered · for review", and clicking jumps to it. Phone: tapping the strip opens the navigator.
- `role="progressbar"`, with `aria-valuetext` "14 of 22 answered".

**Question header (`.qhead`, 36px row)**
- `Q7` badge: DM Mono 500 13px, `--tile`, radius 8px, padding 0 10px.
- **Mark for review:** a bookmark icon plus "Mark for review" (600 13.5px). Pressed: an amber-filled bookmark, `--wash` background, and the label "Marked". `aria-pressed`.
- **Confidence (when on) (extra):** a 3-segment `.choices`, Sure / Unsure / Guess (600 12.5px). Clicking the chosen one again clears it. It is stored in qstate and never affects marking.
- A spacer.
- **Eliminate:** an ABC-with-a-stroke glyph plus "Eliminate". Pressed: `--wash` and an amber underline.
- **Report:** a flag icon plus "Report" (quiet 13px). `aria-label` "Report a problem with question 7".

**Stem.** Figure, then table, then `.q-stem` (serif 20px/1.58), in the order the current runner uses. The text size follows the setting: 17, 20 or 23px (`--stem`).

**Multiple choice.** `.opts` of `.opt` tiles.
- A click, or A–D / 1–4, selects. `.picked` is `--wash` with a 1.5px amber inset ring and a filled amber letter with `--ink-deep`.
- Choosing another option moves the selection. The chosen option can't be un-chosen except by eliminating it (Bluebook rules).
- `role="radiogroup"`; each option is `role="radio"` with `aria-checked`.
- **With Eliminate on**, each `li` becomes a `grid 1fr 40px` with a strike button: a 32px circle showing the letter with a stroke, `aria-label` "Eliminate B".
  - A struck option (`.opt.out`) has opacity .45, a line-through on `.t` and a faint letter.
  - Its strike button is replaced by a quiet "Undo".
  - Striking the selected option clears the answer, as today.
  - Eliminations stay visible whenever they exist, even with Eliminate off, as in Bluebook.

**Grid-in**
- A `.grid-in .field` (56px, serif 20px), with the placeholder "Enter your answer (e.g., 5.566, -5.566, 2/3, -2/3)". There is nothing beside it, since a test has no Check.
- **Keystroke filter:**
  - Digits, one `.` or one `/`, and a single leading `-` only.
  - At most 5 characters, or 6 with the minus.
  - A rejected key keeps the value and shows a hint under the field for 3s (12.5px soft): "Only digits, one decimal point or fraction bar, and a leading minus", or "5 characters at most, 6 with a minus sign".
  - `inputmode="text"`, because a decimal pad has no minus.
  - Enter moves to the next question.
- **Preview:** "Answer preview" (`k`), then the value rendered by KaTeX: `2/3` as a stacked fraction, `-` as a true minus. It is blank when the field is empty.
- **"Entering your answer"** (the College Board rules as five bullets, plus the examples table):
  - **≥1180px:** a 260px left rail card on every grid-in question, sticky beside the column, as their SPR pane is. A quiet "Hide" collapses it to a tab reading "Entering your answer ›". The collapsed state is remembered in localStorage `satf.sprhelp`.
  - **<1180px:** a disclosure "How to enter your answer ⌄" under the field. It is open until the student closes it, and that choice is remembered in `satf.sprhelp`.

  | Answer | Acceptable | Not acceptable |
  |---|---|---|
  | 3.5 | 3.5, 3.50, 7/2 | 31/2, 3 1/2 |
  | 2/3 | 2/3, .6666, .6667, 0.666, 0.667 | 0.66, .66, 0.67, .67 |
  | −1/3 | −1/3, −.3333, −0.333 | −.33, −0.33 |

**Footer (`#foot`, sticky, 68px, grid `1fr auto 1fr`)**
- **Left:**
  - `#who`: the profile name (600 14px). It shows "Set your name in Me" as a quiet link when there is none.
  - `#saved`: the save status (DM Mono 12px soft). One of:
    - "Saved"
    - "Saving…" (after 400ms in flight)
    - "Offline · 2 answers waiting"
    - "Couldn't save · Retry" (a button)
- **Centre:** `#navBtn`, a `--tile` button, 40px, radius 10px, reading "Question 7 of 22 ⌃" (600 14px). `aria-expanded`, `aria-controls="nav"`.
- **Right:**
  - `#back`: quiet, with a left arrow, "Back". Disabled on Q1.
  - `#next`: a pill (44px tall, padding 0 26px) reading "Next". On the last question it reads "Review" and opens Check your work.

**Question-level extras**
- **Question note (extra):** a quiet "Add a note" under the options. It opens a 3-line textarea (0/500) that is saved to the question's state. The report's review shows notes again.
- **Time on the question** is counted while the question is visible and the tab has focus. It is sent as a delta with `POST /state` when the student moves away, and every 30s.
- **Away time (extra):** while a timed module is live, time with `document.hidden` is counted as `away_ms` and `away_n`. It is shown on Between modules, Time's up and the report ("Away from the window 2 times · 3:10").

###### 4.4 Navigator (`#nav`)
- **Desktop:** a popover anchored above the footer centre, `min(560px, 100vw-32px)`, radius 14px, with the sheet shadow and padding 18px 20px 20px. **Phone:** a bottom sheet, max 70dvh.
- **Header:** "Module 1 of 2 · Math" (700 15px) and ×.
- **Legend with counts** (12.5px soft; counts in DM Mono ink): ◯ Current · ■ Answered 14 · ⬚ Unanswered 8 · ◣ For review 3.
- **Filters** (`.choices`): All / Unanswered / For review / Guesses (shown when Confidence tags are on).
- **Cells:** 40px squares (48px on a phone), radius 8px, gap 8px, 600 14px.
  - answered: `--ink` fill, white number
  - unanswered: a 1.5px dashed `--faint` border on paper
  - for review: an amber bookmark notch top-right, 9px
  - current: a 2px ink outline at 2px offset
  - Each cell's `aria-label` reads like "Question 7, answered, marked for review".
- **Footer:** quiet "Go to review page →".
- **Behaviour:**
  - Esc closes it (their popover ignores Esc), and focus returns to `#navBtn`.
  - Arrow keys move between cells; Enter goes to the cell's question.
  - An outside click closes it.
  - N toggles it.

###### 4.5 Check your work (`#review`)
It replaces the column. The top bar and the clock stay live.
- h1 "Check your work"; meta "Module 1 of 2 · Math · 6:12 left".
- A line (15px): "Select a question to go back to it. Once you move on, you can't come back to this module."
- **Three stat tiles** (`.stat`, `--tile`, radius 10px, padding 16px; a `k` label over a 40px `.num`): Answered 14 / Unanswered 8 / For review 3.
  - Each tile is a toggle filter for the grid (`aria-pressed`, amber underline). Pressing it again clears the filter.
  - A fourth tile, "Guesses 2", appears when Confidence tags are on.
- **A "Show" control** (`.choices`) over the grid: **Status** / **Time (extra)**.
  - Time prints each cell's time under its number (DM Mono 11px: "1:42").
  - Cells over twice the pace get a 2px ink ring.
  - A legend line: "Pace is 1:35 a question".
- **Grid:** the navigator cells at 44px, 11 per row. A click goes to that question.
- **Warning**, when unanswered > 0 (`.mistake` style with an amber dot): "8 questions unanswered. A blank is marked wrong, and a wrong answer costs no more than a blank, so guess before you move on." The no-penalty tip is an extra.
- **Pacing line**, when timed (extra): "6:12 left · about 46 s for each unanswered question".
- **Unsaved answers:** "2 answers are still saving" plus Retry. The move-on pill stays disabled until they are acknowledged. Offline: "You're offline. Your answers are kept on this device and sent when you reconnect."
- **Footer:** on the left, the save status. On the right, quiet "Back to question 22" and the pill "Move on to module 2", or "Hand in" on the last or only module.

###### 4.6 Between modules (`#between`)
- h1 "Module 1 is in".
- A row of small `.stat` tiles: Answered 20 of 22 · Left marked 2 · Time used 31:40 · Away 0:00.
- A card: "Module 2 · 22 questions · 35:00 · calculator and reference sheet on every question".
- When "Tell me my module 2" is on: "You earned the harder module 2." Otherwise nothing is said, as in Bluebook.
- The pill "Begin module 2". The server builds module 2 at routing time, and its clock starts only on this press. While busy the pill reads "Getting module 2 ready…".
- Quiet "Save and exit".
- There is no break screen: the SAT has none inside a section.

###### 4.7 Time's up and handing in
- **Time's up** (`#timeup`):
  - h1 "Time's up".
  - "Module 1 was handed in with 18 of 22 answered. Every answer you gave is saved."
  - When some were still pending: "2 answers you gave in time are being sent." with the queue status.
  - Pill "Continue to module 2", or "See your report".
  - Any open sheet or the calculator closes first.
- **Handing in:** the column shows "Marking your test…" with the bar skeleton, then redirects to `/results/report/?id=ID`. A diagnostic goes to signup, as today.

###### 4.8 Tools
- **Directions** (`#dirsSheet`): the existing College Board math text, plus the grid-in examples table, and a "Close" pill.
- **Reference:** the existing `UI.ref`.
- **Calculator:** `UI.calc`, extended.
  - A floating Desmos panel, dragged by its bar. Bar actions: **Dock** (≥1180px), **Expand / Shrink**, and ×.
  - A **resize grip** at the bottom right. Minimum size 320×360; maximum, the viewport.
  - **Docked:** fixed on the left, 420px wide, between the top bar and the footer. The column shifts right, as theirs does. The grid-in rail moves to the right side while it is docked.
  - Position, size and dock state are kept in localStorage `satf.calc.pos`.
  - **The Desmos state is kept per sitting** (`getState`/`setState`, key `satf.calc.{sid}`, saved on close and every 10s), so expressions survive a reload and a move between modules **(extra)**.
  - Phone: a bottom sheet at 60dvh, with a drag handle that snaps to 40, 60 or 90dvh. The question keeps scrolling above it.
- **Highlights & Notes** (over math stems, tables and options):
  - With it on, selecting text shows a floating toolbar above the selection, or below it near the top of the screen. It has 7 styles, in orange and graphite only:
    - Highlight (`--wash`)
    - Strong (`--wash-2` plus an amber underline)
    - Underline (solid amber)
    - Dashed
    - Dotted
    - Box (a 1px ink outline)
    - Strike (an ink line-through, for crossing out information that doesn't matter)
  - The toolbar also holds "Note" and, when the selection overlaps a mark, "Remove". Each swatch is 32px with an `aria-label`.
  - Clicking an existing mark opens a popover: the note text (or "No note"), Edit note, the 7 swatches to restyle it, Remove, and Close.
  - Marks are stored per question as `{start, end, style, note}`, with offsets into the stem's text node. Table cells and options are addressed as `t:r:c` and `o:i`.
  - **Notes rail (extra):** while it is on, a "Notes 3" button opens a 300px right rail (≥1180px) or a bottom sheet on a phone. It lists every note in the module by question, and each note jumps to its question.
- **More** (`#moreMenu`: a 260px popover under More, or a bottom sheet on a phone). Items, with icons:
  - Directions
  - Keyboard shortcuts
  - Text size [A− · A · A+] (17/20/23px, kept in localStorage `satf.textsize`)
  - Pace guide [toggle]
  - Confidence tags [toggle]
  - Notes
  - Report a problem with question 7
  - — (divider)
  - Hand in this module… (goes to `#review`)
  - Save and exit
  - Discard this test…
- **Report a problem** (`UI.report`, shared across the site):
  - A sheet titled "Report a problem".
  - A read-only box "Sent with your report": Test "Full section #12"; Question "Module 1 · Q7"; Item "linear_functions · lf_two_readings · seed 48213". Because the item is addressed by template and seed, it can be regenerated exactly.
  - **Category:** Wrong answer key / More than one right answer / No right answer / Unclear wording / Typo / Figure or table is wrong / Something broken / Idea or request / General feedback / Other.
  - **Title:** prefilled "Question 7, module 1", with 0/200.
  - **Details:** 0/5000.
  - **"Include my answer":** a checkbox, off by default.
  - **Screenshots:**
    - Up to 10 images (JPEG, PNG, WebP or GIF), added by picker, drag and drop, or paste (Ctrl/Cmd+V), shown as thumbnails with remove buttons.
    - Stills are shrunk on the device to 1600px on the long edge and re-encoded as WebP. A GIF is sent as it is.
    - Each image is at most 2 MB after that.
  - In a timed test, a footer note: "The clock keeps running."
  - The pill "Send report". Success: "Thanks. Report R-1042 is in. You'll see what happens to it under Me." plus Close. Error: inline, plus Retry.
  - Limit: 20 reports a day.
- **Keyboard shortcuts** (`#keysSheet`): a two-column table of the keys below.

###### 4.9 Saving, offline, leaving, errors
- **Answers:**
  - Painted optimistically.
  - Written to localStorage `satf.pending.{sid}` as `{qid: {value, made_left}}`, where `made_left` is the seconds left on the client clock when the answer was made.
  - Sent in order, and removed from pending only on a 2xx.
  - Retried with backoff (1, 2, 5, 10s) and on the `online` event. `#saved` reflects every state.
  - Responses:
    - A 409 "time is up" goes to `#timeup`.
    - A 409 "finished" redirects to the report.
    - A 409 "paused" shows the lobby.
    - A 409 "discarded" shows "This test was discarded." plus "Back to Tests".
- **State** (mark, strike, marks, notes, confidence, ms, away) uses the same queue.
- **Handing in** always waits for the queue. Offline at time-up, the screen reads "Handing in when you reconnect · 2 answers waiting".
- **Leaving the page:** while the test is timed, live and not paused, `beforeunload` asks the browser to confirm leaving.
- **Leaving fullscreen:** a 40px `--wash` banner under the top bar, "You left fullscreen.", with a quiet "Return to fullscreen" and ×.
- **Errors:**
  - 404: "This test doesn't exist." plus "Back to Tests".
  - 403: "This test belongs to another device's code. Open it there, or switch codes in Me."
  - A network failure on load: "Can't reach the server." plus Retry. Nothing is lost.

###### 4.10 Keyboard
The keys are ignored while typing in a field, except Enter and Esc. No letter key does two things.

| key | action |
|---|---|
| A–D or 1–4 | choose |
| Shift+A–D | eliminate / undo |
| E | Eliminate mode |
| M | Mark for review |
| K | cycle confidence Sure → Unsure → Guess → none (when on) |
| ← / → | Back / Next |
| N | navigator |
| Shift+R | Check your work |
| G | calculator (graphing) |
| F | reference (formula sheet) |
| L | Highlights & Notes |
| H | hide / show the clock |
| ? | shortcuts |
| Esc | close the top sheet, popover or menu |

The practice session uses the same map: `UI.keys`.

###### 4.11 Accessibility
- A live region announces "Answer saved", "Marked for review", "5 minutes left" and "Module 2 started".
- Every sheet traps focus and returns it to its trigger.
- Toggles use `aria-pressed`, and the navigator is a labelled grid.
- Hit targets are at least 44px on touch.
- Orange fills always carry `--ink-deep` text.
- `prefers-reduced-motion` turns motion off.
- Post text and note text are always set with textContent.

###### 4.12 Phone (390)
- **Top bar (56px):** [× Save and exit] [the clock, centred; tap to hide or show] [Highlights & Notes] [Calculator] [Reference] [⋮ More]. These are 40px icons with an `aria-label` and a long-press tooltip.
  - Directions moves into More.
  - The title "Module 1 of 2" moves into the footer button.
- **Progress strip:** 22 segments across 358px.
- **Question header:** `Q7`, Mark (icon plus "Mark"), Confidence (an icon that cycles, with its state in the label), Eliminate (icon), Report (icon).
- **Options:** full width. With Eliminate on, a 36px strike button sits at the right.
- **Grid-in:** the "How to enter your answer" disclosure under the field.
- **Footer:** [‹ 44px Back icon] [the "M1 · 7 of 22 ⌃" button] [Next pill, 44px tall].
- **Navigator and More:** bottom sheets. Navigator cells are 48px, 6 per row.
- **Check your work:** tiles 2-up (numbers at 32px), the grid 6 per row, and the pill full width in the footer.
- **Calculator:** a bottom sheet.
- **Highlights toolbar:** 9 buttons × 36px, wrapping to two rows under 360px.
- No horizontal page scroll anywhere. A wide table scrolls inside `.q-table`.

---

##### 5. Flows (calls)

1. **Start.**
   - Card Start or the start sheet → `POST /api/mock/new {…}` → `/test/?s=ID`.
   - `GET /api/session/ID` returns `begun:false` → the lobby.
   - An optional Change → `POST /cfg`.
   - Begin (plus `requestFullscreen`) → `POST /begin` → `GET` returns the questions → Q1, with Directions on the first start.
   - Today and Plan call the same endpoint and land on the lobby.
2. **Answer.** Select → `POST /api/session/ID/answer {question_id, answer, made_left}`. Mark, strike, highlight, note, confidence, time and away all go through `POST /api/session/ID/state {question_id?, …}`.
3. **Review and move on.**
   - Last question → Next ("Review") → `#review`, with no server call.
   - Move on → `POST /finish`, which returns `{next_module:2, summary}` → `#between`.
   - Begin module 2 → `POST /begin` → `GET` → module 2, Q1.
4. **Hand in.** `POST /finish` → `{finished}` → the report.
5. **Clock runs out.** The queue flushes, then the client calls `POST /finish` → `#timeup`.
6. **Save and exit.** `POST /pause` → `/tests/`.
7. **Resume.** Tests → Resume → the paused lobby → `POST /begin`.
8. **Discard.** `POST /discard`.
9. **From the history.**
   - Twin → `POST /api/mock/new {kind:'twin', twin_of}`.
   - Fix → `POST /api/drill {from_session}`.
   - Retake → `POST /api/mock/new {kind:'paper', paper}`.
   - Share → `POST /api/session/ID/share`.
10. **Papers.** `GET /api/tests` returns `papers`. Discussion: `GET/POST /api/papers/{n}/posts`, plus `/api/posts/{id}/helpful|report`, `PUT` and `DELETE`.
11. **Shared.** `/tests/?shared=CODE` → `GET /api/shared/CODE` → start sheet → `POST /api/mock/new {kind:'shared', shared:CODE}`.

### 3.4.4 Extras: what they missed

- **Papers that never run out: a new shared paper every Monday**: Their catalog is 29 fixed papers, mostly paywalled. Ours starts with the 7 shelf sections already in mocks.json, and the server builds one more each week, once, from a seed, the same way the daily challenge is built. Everyone gets the same questions, so Sat by, Average, rank and discussion are fair, and the shelf keeps growing.
- **Measured paper difficulty and a first-sitting percentile**: Their Easy/Medium/Hard is an editorial label. Ours rates each paper from everyone's first standard sittings (Easier than most / Typical / Harder than most), sorts Hardest and Easiest by that, and ranks you only against first sittings, so retakes can't inflate it.
- **'New to you' per paper**: It counts which of the paper's 66 questions you have met before (practice_seen by template and seed). It replaces their Access filter with one that means something to a free student.
- **Discussion that opens only after you've sat the paper, tagged by question**: Their comments are unmoderated chatter with spoilers. Ours shows nothing until you've finished the paper. Each post can point at 'M1 Q17', which opens your own review of that question, and it has Helpful sorting, report-to-hide and a moderation tool.
- **Share a test with a friend**: Any finished sitting's exact questions are sent by link, addressed by (template, seed). The friend sits them under test rules, and both see each other's band afterwards. Their share is QBank-only and froze the page. Their test assignment exists only in a hidden teacher area.
- **A fresh test for every sitting, said out loud**: Their papers get used up, and free users get one attempt. Ours never repeat a question, so a student can sit ten sections before test day. The lobby says so: 'Every question is new to you'.
- **Twin test (a parallel form of any finished sitting)**: It keeps the same template in every slot, at the same difficulty and position, with new seeds, which gives an equal test for measuring improvement. A finite bank can't build a parallel form on demand.
- **Fix N from any sitting row**: A sitting's misses become a repair drill on the same templates and the same misconceptions (the existing /api/drill from_session), without opening the report first.
- **Custom test from your open mistakes, saved questions or a sitting's misses**: It re-tests every open mistake under the clock, with no feedback until hand-in, so you see whether a fix holds under pressure. Only a bank that makes the same trap with new numbers can do this.
- **Try the other module 2**: A student who routed lower can sit the harder module 2 at once and see what the upper route asks. That needs generation on demand.
- **Harder and easier variants (module 1 harder or easier, module 2 fixed)**: This is their Difficulty and Type filters, made a property of the build instead of a filter over a fixed shelf, and honestly labelled 'Practice, not a score estimate'.
- **Custom test under test rules**: Any skills, 5–60 questions, the module's easiest-first ladder, and no feedback until hand-in. Their thin skills (SEC 22, Transitions 10, statistical claims 5) couldn't fill it.
- **Extended time (1.5x and 2x)**: Students with accommodations practise at the timing they will get. Bluebook supports it; TopTierPrep doesn't.
- **Confidence tags (Sure / Unsure / Guess) and calibration**: One optional tap per question. The report then shows how often your 'sure' answers were right. Because every wrong option names a misconception, it can show which misconception you were sure of, which is the most urgent kind of mistake.
- **Estimate with confidence, route rate and combined band**: Theirs shows one band and a red LOW CONFIDENCE chip. Ours gives the reason for the confidence and what would raise it, 'Routed up 4 of 6 sections', a tighter band across the last three sections, the range of your sittings, and the gap to your target. Floor-score sittings still count.
- **Save and exit that really stops the clock, and an In progress list**: Their resume is only a Status filter. Ours pauses on the server and shows time left. It handles 'left without saving' and 'expired while away'. No questions are sent while paused.
- **The clock starts on Begin, and module 2's on Begin module 2**: The lobby, the fullscreen prompt and the step between modules no longer take test time.
- **A lobby that shows and edits every setting**: Their gate only asks about fullscreen. Ours lists what the test is, how long it runs and which tools are on, each with Change, until Begin.
- **Test defaults that follow the student**: Timing, calculator, pace guide and confidence tags are stored in the profile, so they carry to another device with the code. This is the equivalent of their Profile Learning Preferences, and it is used by Me as well.
- **Everything persists on the server**: Marks, eliminations, highlights, notes, confidence, time per question, the hidden-clock state and the calculator's expressions all survive a reload, a crash or a change of device.
- **Save status and an offline queue that never loses an answer made in time**: Every answer is acknowledged or retried, pending ones are kept on the device, Check your work won't move on with unsaved answers, and answers made before time ran out are accepted when they arrive late.
- **Pace guide, a Time view on Check your work, and away time**: A slow student learns pacing during the test, sees which questions ate the clock before handing in, and sees how long they spent out of the window.
- **No-penalty guessing tip and a pacing line on Check your work**: 'A wrong answer costs no more than a blank' and 'about 46 s for each unanswered question' turn their bare warning into a decision.
- **Grid-in validator with a rendered preview and the official examples on every grid-in**: It rejects impossible input as it is typed (their field accepts anything), renders 2/3 as a fraction, and teaches the fourth-digit rule our marker applies (scoring.grid_equal).
- **7 annotation styles within the brand, a notes rail, and notes kept into the review**: It matches their 4 colours plus 3 underlines using only orange and graphite, adds a Strike style, lists every note, and shows your notes again when you review.
- **Private question notes and sitting notes**: A place for 'I ran out of time on 18–22' with no moderation burden. Discussion carries the public side.
- **Reports that point at the exact item, and a loop back to the student**: Each report carries (template, seed), so the item can be regenerated and a bad template fixed for every future seed. Students see their report's status in Me. Theirs sends an exam ID into silence.
- **Export your sittings as CSV**: Their 'Share / Export Report' button is dead. Ours downloads exactly the filtered rows.
- **Blanks shown apart from wrong answers everywhere**: Their list mixes them, and their report contradicts itself (25 Wrong vs 0 Incorrect / 45 Unanswered). Ours uses outlined chips for blanks and filled chips for wrong answers, with the same counts on every screen.
- **Up next, from the plan and the week's paper**: On a plan test day the page leads with that day's test. Otherwise it offers the new paper, or the next sensible sitting, so the catalog always has a default.
- **No-calculator mode**: Mental-math practice for the questions where the calculator is slower. One toggle.
- **Docked, resizable calculator that keeps its state**: Their panel resizes but forgets its state. Ours docks on wide screens and keeps its expressions for the whole sitting.
- **A full keyboard map with no clashes, and a shortcuts sheet**: It covers mark, eliminate (Shift+letter), confidence, tools and review, not just choosing. Esc works on every popover, which fixes their navigator bug.
- **Text size control**: 17, 20 or 23px stems, for reading comfort and accessibility on small screens.
- **Answer-change tracking**: The first answer and the number of changes are stored per question, so the report can show which changes went right→wrong and which went wrong→right.

### 3.4.5 Server changes

Tables and columns here are added by F4 as listed in §2.5; the drill fields map through §2.6; prefs through §2.7.

- **Clock starts at Begin (POST /api/session/{sid}/begin)**: New sittings are inserted with module_started NULL and cfg.lobby=true. remaining(): if cfg.lobby and module_started is NULL, it returns the full duration. POST /begin sets module_started=now() when it is NULL, or clears a pause (see below). It is owner-only and idempotent, and returns payload(row). It also calls db.remember for the live module's items, so a built but never begun sitting doesn't burn questions twice. Diagnostics (POST /api/session) take the same path. Older rows without cfg.lobby keep today's behaviour.
- **Pause and resume (Save and exit)**: New columns: sessions.paused_at TEXT, paused_ms INTEGER DEFAULT 0, pauses INTEGER DEFAULT 0. POST /api/session/{sid}/pause sets paused_at=now() and pauses+=1, only when the sitting is live, timed and unfinished; it is idempotent. POST /begin on a paused row adds now−paused_at to paused_ms and clears paused_at. remaining() subtracts paused_ms, plus now−paused_at while paused. paused_ms resets to 0 when module 2 begins. The result stores pauses, so the report can say 'Paused twice'.
- **Questions withheld before Begin and while paused**: payload() returns questions: [] and question_count: N when the sitting is not begun or is paused, and adds begun: bool and paused: bool.
- **Settings before Begin (POST /api/session/{sid}/cfg)**: Owner-only. Body: {timing?, minutes?, calculator?, pace?, confidence?, reveal_route?}, validated as in /api/mock/new. Allowed only while module 1 is not begun (409 'already begun'). Returns payload(row).
- **Per-question state (POST /api/session/{sid}/state)**

  New column sessions.qstate TEXT DEFAULT '{}'.
  Body: {question_id?, marked?: bool, struck?: [0..3], ms?: int delta 0..600000, conf?: 'sure'|'unsure'|'guess'|null, note?: str ≤500, marks?: [{start:int, end:int, style: highlight|strong|underline|dashed|dotted|box|strike, note?: str ≤500, at?: 'stem'|'t:r:c'|'o:i'}] ≤50, away_ms?: int delta 0..3600000, away_n?: int delta 0..10}.
  Per-question fields are written with json_set on $."qid".field, like db.set_answer, so two calls at once can't clobber each other. ms is added with COALESCE(json_extract)+?. away_* go to $._session.
  question_id, when given, must be in the live module. It returns 409 when the sitting is finished, discarded, paused or not begun.
  GET /api/session/{sid} returns qstate for the live module's ids only.

- **Ownership on every sitting endpoint**: New helper own(row, x_learner): when row.learner is set, X-Learner must be present AND equal (else 403 'that test belongs to another code'). It covers GET /api/session/{sid}, /answer, /state, /begin, /pause, /cfg, /finish, /discard, /note, /share and /results. Diagnostic rows created without a learner stay reachable by their 128-bit id, as today. /api/mock/{num} now takes X-Learner instead of body.learner (the body is still accepted for the archive).
- **Answer rules (POST /api/session/{sid}/answer)**

  Body adds made_left: int | null.
  Refused:
  - a different learner (403);
  - not begun (409 'press Begin first');
  - paused (409 'paused');
  - discarded (409 'discarded');
  - time up on a timed sitting (409 'time is up'), when remaining() < −15 s.
  An answer made in time but delivered late is accepted when it carries made_left ≥ 0, arrives within 15 min of time-up and the module is still unfinished. Each such answer increments qstate._session.late.
  Grid-in shape is validated: ^-?[0-9./]{1,5}$ with at most one . or /, otherwise 422 'not a grid-in answer'.
  It stores qstate[qid].first (the first non-null answer) and increments qstate[qid].changes when the value changes.

- **Module hand-in (POST /api/session/{sid}/finish)**

  Routing module 1 now sets module_started=NULL for module 2 (not now()), and module 2 is built then, as today. For a paper or a shared sitting, module 2 is copied, not built.
  The response adds summary: {answered, unanswered, marked, guesses, ms, away_ms, timed_out}.
  The final finish stores:
  - result.modules = [{n, right, asked, missed:[positions], blank:[positions]}];
  - result.timing, result.pauses, result.late, result.away and result.fixed_route;
  - result.scored.
  It passes per-question ms from qstate into progress.record_paper, so tests count toward study time.

- **Discard (POST /api/session/{sid}/discard)**: Owner-only; the sitting must be unfinished. It sets a new column sessions.abandoned=now() and does NOT set finished, so no code that reads finished can count it: /api/today tested, /api/drill from_session, latest_score, progress.days, papers' stats and history's completed rows. Nothing is filed to attempts. Every 'unfinished' query (in_progress, ?all=1, up_next) adds AND abandoned IS NULL. Answer, state, begin, finish and pause return 409 'discarded'.
- **Sitting options (POST /api/mock/new)**

  Body: {kind: 'section'|'module'|'custom'|'twin'|'paper'|'shared', module?: 'm1'|'m2u'|'m2l' (kind module or paper-module), m1?: 'standard'|'upper'|'lower' (sections), route?: 'adaptive'|'upper'|'lower', paper?: int, shared?: code, timing?: 'official'|'x1.5'|'x2'|'untimed', minutes?: 1..180 (custom), calculator?: bool, pace?: bool, confidence?: bool, reveal_route?: bool, twin_of?: sid, custom?: {source: 'skills'|'mistakes'|'saved'|'misses', from_session?: sid, topics:[slug], count: 5..60, order: 'ladder'|'mixed', formats: 'both'|'mcq'|'spr', tiers: ['easy'|'medium'|'hard'] ≥1}}.
  Unknown values give 422. The old body {full, timed} still works (full→section, timed:false→untimed), so Today and Plan keep working.
  Everything is stored in cfg. New column sessions.number = the learner's count of earlier non-abandoned test sittings + 1, computed in the INSERT.
  Kinds: a section, paper, twin or shared section is kind 'mock'. A single module (any tier) is kind 'module', with its questions under 'module1' whatever the tier, cfg.module set, and ids prefixed m1/m2u/m2l. Custom tests use the new kind 'custom', read through questions_of like 'module'.

- **Blueprint additions (server/blueprint.py)**

  TIERS adds module1_upper {easy 3, medium 8, hard 11} and module1_lower {11, 8, 3}. module(form) accepts them with DOMAIN_SPLIT[1] and the id prefix m1.
  New twin(source_qs, b): for each slot, draw_matching(b, q['key'], q['difficulty'], 'spr' if q['type']=='spr' else None). The fallback is the least-used template in the same topic with that tier and format. Ids and positions match the source. A twin section twins module 1 at the start. At routing it twins the source's module 2 when the route matches, and otherwise builds a fresh blueprint module 2.
  New custom(topics, count, tiers, order, formats, b, queue=None): positions dealt across topics with practice.interleave; a difficulty ladder in equal thirds of the allowed tiers, sorted when order='ladder'; grid-in slots at round(k·count/22) of SPR_AT when formats='both'. It is filled with draw_matching and practice.penalty. With queue (templates from open traps or a sitting's misses), each slot draws that template with a fresh seed. source 'saved' copies the saved (template, seed) items exactly. Ids c01..cNN.

- **Papers (shared forms)**

  New table papers (n INTEGER PRIMARY KEY, week TEXT UNIQUE, label TEXT, built TEXT, questions TEXT {module1, module2_lower, module2_upper}).
  At startup, mocks.json forms 1.1–1.7 are inserted as n=1..7 with label 'Launch set' (INSERT OR IGNORE).
  daily.paper(week) builds the ISO week's paper the first time anyone asks on or after Monday 00:00 UTC, exactly as challenge(day) does: practice.Builder(f'paper:{week}', seen=every earlier paper's (template, seed), set()), with blueprint.module for module1, module2_upper and module2_lower, then INSERT OR IGNORE and re-read.
  A paper sitting is sessions.kind='mock', mock_id='P{n}'. mock_module() reads 'P…' from the papers table (lru-cached) the way it reads the MOCKS shelf today. db.remember runs on begin and at routing.
  Stats for GET /api/tests:
  - first sittings = each learner's earliest finished, non-abandoned sitting of that paper at official timing, adaptive, with the whole paper;
  - sat_by = the count of first sittings;
  - average = the mean band midpoint, shown when there are at least 20;
  - rating from the mean earned/possible against all rated papers (±0.05 counts as Typical), at least 20;
  - percentile of your first sitting, at least 30;
  - new_to_you = 66 − |paper items ∩ practice_seen|.
  /api/mocks and /api/mock/{num} stay for the archive.

- **Discussion (papers only)**

  New table posts (id INTEGER PK, paper INTEGER, learner, name, at, edited, parent INTEGER NULL, about TEXT NULL (e.g. 'm1:17' or 'm2u:5'), text ≤500, helpful INTEGER DEFAULT 0, reports INTEGER DEFAULT 0, hidden INTEGER DEFAULT 0), with post_votes (post, learner, kind 'helpful'|'report', PRIMARY KEY (post, learner, kind)).
  Endpoints:
  - GET /api/papers/{n}/posts?sort=top|new&about=… returns {gated: true, count} until this learner has a finished sitting of paper n, and otherwise the threads (hidden posts shown only to their author).
  - POST /api/papers/{n}/posts {text, about?, parent?}: requires a finished sitting and a profile name (422 'set a name first'); 20 a day (429); a reply's parent must be top-level.
  - PUT/DELETE /api/posts/{id}: the author only, within 15 min.
  - POST /api/posts/{id}/helpful and /report are one per learner. The third report sets hidden=1.
  tools/moderate.py lists reported posts and hides, restores or mutes a learner code (a muted code's new posts are hidden).

- **Share a test**

  New table shares (code TEXT PK, 8 chars of Crockford base32 from secrets, session, learner, at, show_score INTEGER DEFAULT 1) and column sessions.shared_from.
  POST /api/session/{sid}/share {show_score} is owner-only and needs a finished test sitting. It returns {code, url}, reusing an existing code.
  GET /api/shared/{code} returns {kind_label, by: owner's name or null, at, questions, minutes, sat_by} and never questions or keys.
  POST /api/mock/new {kind:'shared', shared} copies the source's module 1 (ids, template, seed and all). At routing it copies the source's module 2 if the route matches, and otherwise builds a fresh blueprint module 2. cfg.shared_route_match is recorded.
  /api/session/{sid}/results adds peers [{name|null, band|null (when show_score), you}] for sittings of the same share, owner included. The Report section renders it.

- **Forced routes and scoring flags (app.py finish, scoring.py)**

  With route 'upper' or 'lower', finishing module 1 skips route_after and uses the fixed route; module1 is still recorded, as is route_after's verdict (result.would_route).
  result.scored is true for kind mock (section, paper, twin, shared) with m1 'standard', for kind diagnostic, and for kind module only when cfg.module == 'm1'. Otherwise result.estimate = null and result.not_scored is 'harder module 1', 'easier module 1', 'single module 2' or 'custom test'.
  Fixed-route sittings keep an estimate with result.fixed_route = true. x1.5 or x2 timing keeps the estimate with result.extended = true. Both are excluded from Combined, paper stats and every percentile.

- **Durations**: duration(row) is the module seconds (2100), or len(qs)·95 for a diagnostic or custom test, or cfg.minutes·60 — multiplied by 1.5 or 2 for extended timing. seconds is null for untimed. The client counts elapsed time up from the begin time plus the qstate ms total.
- **Section label**

  section_label():
  - mock → 'Math · Module {n} of 2';
  - paper → 'Paper #{n} · Module {m} of 2';
  - module → 'Math · Module 1', 'Math · Module 2 (harder)' or 'Math · Module 2 (easier)';
  - custom → 'Custom test';
  - diagnostic → 'Diagnostic'.
  This fixes 'Section 2, Module 1' with no section 1.

- **Session payload additions (GET /api/session/{sid})**: Adds name (learners.name), number, kind_label, paper, shared_by, modules (1 or 2), module, timing, factor, calculator, pace, confidence, reveal_route, begun, paused, pauses, qstate (live module only), and new_to_you (papers and shared). route is added only when reveal_route is set and module==2. The answer, rationale, reasons, key and seed never appear at any depth.
- **History (GET /api/history)**

  Each row adds:
  - number, status ('completed'|'in_progress'|'paused'|'timed_out'|'not_begun'), route, fixed_route, capped, timing, extended, scored, pauses;
  - modules [{n, right, asked, missed, blank}], ms, mean_weight (for the Hardest/Easiest sort);
  - twin_of, paper, retake (n ≥ 2 for that paper), shared_from, note;
  - module (the live one), answered and left_seconds, for in-progress rows.
  modules, missed and blank are computed lazily for old rows from their answers. A new query ?all=1 includes unfinished, non-abandoned test sittings.

- **Tests overview (GET /api/tests)**

  Returns, in one round trip for /tests/:
  - estimate: {latest, previous, delta, trend, headline_parts, best, range {low, high}, combined (≥2 standard sections: mean midpoint ± 70/√n rounded to 10, over the last 3), confidence {level: 'low'|'medium'|'high', reason}, routed_up {up, sections}, counted {sittings, sections, modules, diagnostics}}. Floor-score sittings are included.
  - target, and exam {date, days}.
  - up_next: {kind, reason: 'resume'|'plan'|'new'|'paper'|'default', session?, paper?}.
  - in_progress: [rows in the history shape].
  - kinds: [{id: 'section'|'module1'|'module2u'|'module2l'|'custom'|'diagnostic', everyone, yours, last, best, percentile (null below 30)}].
  - papers: [{n, label, week, newest, sat_by, average, rating, yours {status, last, sittings, first_percentile}, new_to_you, posts}].
  - twin: {source, label} or null.
  - prefs: profile.test_prefs.
  It builds this week's paper if it is missing.

- **Reports (POST /api/report, GET /api/reports)**

  POST body: {context: 'test'|'practice'|'review'|'catalog'|'paper'|'qotd'|'challenge', session?, question_id?, paper?, kind?, category (the 10 values), title ≤200, details ≤5000, include_answer: bool, images?: [data URL, ≤10, each ≤2 MB decoded, image/jpeg|png|webp|gif]}.
  The server resolves template, seed and given from the session and never trusts the client for these. Images are written to server/reports/{id}-{n}.{ext} after the magic bytes are checked.
  New table reports (id TEXT PK 'R-####', learner, at, context, session, qid, paper, template, seed, kind, category, title, details, given, images JSON, status DEFAULT 'open', resolution TEXT, updated).
  Limit: 20 a day per learner (429). Returns {id}.
  GET /api/reports returns this learner's reports with status ('open'|'fixed'|'not a problem'|'duplicate') and resolution, for Me.
  tools/reports.py lists open reports with a regenerate command for each (template, seed) and sets their status.

- **Sitting note (PUT /api/session/{sid}/note)**: {text ≤1000}. Owner-only, stored in the new column sessions.note, and returned in /api/history and /api/session/{sid}/results.
- **Test defaults in the profile**: New column learners.test_prefs TEXT (JSON: {timing, calculator, pace, confidence, reveal_route, fullscreen}). PUT /api/me accepts test_prefs, validated field by field (422 on unknown values). profile() returns it with defaults filled in. The start sheet and Me both read and write it.
- **Today and latest_score**: /api/today tested counts only sittings finished today of kind 'mock' (section, paper, twin or shared) or 'module' that are whole (cfg.module m1, or any module when the plan's test is a module), not abandoned and at any timing. Custom tests don't count. latest_score skips rows with no estimate, as today, so variants and custom tests drop out on their own.
- **Schema migration (server/db.py)**: LATER_COLUMNS adds sessions.qstate, paused_at, paused_ms, pauses, abandoned, number, note and shared_from, plus learners.test_prefs. SCHEMA adds the papers, posts, post_votes, shares and reports tables, and the indexes reports(learner, at), posts(paper, parent, at), sessions(mock_id, finished) and sessions(learner, abandoned).
- **Tests in study time (server/progress.py)**: record_paper(learner, session, questions, answers, ms_by_qid=None) passes min(ms, MS_CAP) for each question into record(), so the days and minutes in /api/me include tests.
- **test_flow.py checks**

  New checks:
  - begin and pause semantics; questions withheld before begin; cfg changes before begin and 409 after;
  - answers refused before begin, while paused and after time (by moving module_started back in the DB), and a late answer with made_left ≥ 0 accepted and counted;
  - the qstate round trip, including conf and away, with no key leak;
  - module 2's clock NULL until begin;
  - m1 upper tier counts 3/8/11 and scored false; a single m2u module scored false;
  - twin slot-by-slot equality; x1.5 and x2 durations;
  - history all=1 statuses and modules;
  - discard excluded everywhere, including /api/today tested;
  - papers 1–7 present, two learners get identical module 1 stems on P1, the week's paper built once, and first-sitting stats exclude retakes;
  - posts gated before a finished sitting, then allowed, with the third report hiding a post;
  - a share copies module 1 exactly and GET /api/shared leaks no questions;
  - a report stored with template and seed, with the 422 and 429 limits;
  - a foreign or missing X-Learner gets 403 on an owned sitting;
  - /test/ without ?s= creates no session.

- **README 'The serving layer'**: Table rows for /tests/ (GET /api/tests, /api/history?all=1, the POST /api/mock/new options, papers, /api/papers/{n}/posts, /api/shared/{code}) and /test/ (/begin, /pause, /cfg, /state, /answer, /finish, /discard, /note, /share). Lines for POST /api/report, GET /api/reports, tools/reports.py and tools/moderate.py.

### 3.4.6 Files this spec names, and who owns each

| file | owner |
|---|---|
| `web/tests/index.html` | S5 |
| `web/test/index.html` | S5 |
| `web/test/test.js` | S5 |
| `web/assets/runner.js` | F3 |
| `web/assets/runner.css` | F3 |
| `web/assets/ui.js` | F2 |
| `web/assets/ui.css` | F1 |
| `web/practice/session/index.html` | S4 |
| `web/results/report/index.html` | S6 |
| `web/results/index.html` | S6 |
| `web/diagnostic/index.html` | S5 |
| `web/index.html` | S3 |
| `web/plan/index.html` | S7 |
| `web/me/index.html` | S1 |
| `server/app.py` | F0 (routers register themselves, §2.10) |
| `server/blueprint.py` | F5 → S5 |
| `server/daily.py` | S3 |
| `server/db.py` | F4 |
| `server/scoring.py` | F4 |
| `server/progress.py` | F4 |
| `server/test_flow.py` | shared: new checks go in server/checks/<task>.py |
| `tools/reports.py` | F6 |
| `tools/moderate.py` | S5 |
| `README.md` | shared: each task edits its own subsection |

A file owned by another task is met through §2.9: the owner builds it, or this section's task adds its hook on its own page.

### 3.4.7 Shared needs

- The runner shell (web/assets/runner.js + runner.css): a sticky top bar with left, centre and tool zones; the progress strip; the 700px column; a sticky footer (Back / 'Question N of M ⌃' / Next); a toast; a live region. Used by /test/ (mode 'exam') and /practice/session/ (mode 'practice').  
  ↳ R21: F3 runner.js
- UI.question gains mode:'exam': select and change without locking, no reveal, restore the selected and struck options, and onSelect / onStrike callbacks. Eliminate (strike + Undo) works in both modes. KaTeX renders the latex choices when they differ from the plain ones. The stem uses the text-size variable --stem. The grid-in field gets the keystroke filter, the placeholder, the KaTeX preview and the 'Entering your answer' rail or disclosure. → built in F3 question.js / runner.js
- UI.navigator: a popover on desktop and a bottom sheet on a phone, with a legend that carries counts, filter chips, and cell states (answered/unanswered/marked/current for exam; right/wrong/mixed/saved/current plus a Difficulty view for practice). Esc and arrow keys work, and focus returns to the trigger. → built in F3 question.js / runner.js
- UI.report: the report-a-problem sheet (10 categories, up to 10 images shrunk on the device, paste and drop) plus POST /api/report. Used by the test window, the practice session, the report's review, catalog and paper cards, the question of the day and the challenge. Me lists GET /api/reports. → built in F6 report.js  
  ↳ R17: UI.report (F6 report.js)
- UI.calc upgrades: a resize grip, docking at ≥1180px, position and Desmos state kept per sitting, a phone bottom sheet with snap heights, and the option to hide it (no-calculator mode). → built in F3 question.js / runner.js
- UI.annotate: the highlight and note engine over the stem, tables and options (7 styles, offsets, popover, notes rail), with a read-only render for the report's review. → built in F3 question.js / runner.js  
  ↳ R6: the notes table and POST /api/notes (F4), UI.annotate (F3)
- UI.keys and a shortcuts sheet: one key map with no clashes, shared by the test window and the practice session (A–D/1–4, Shift+letter eliminate, E, M, K, N, Shift+R, G, F, L, H, ?, Esc). → built in F2 ui.js  
  ↳ R22: one map, §2.8
- UI.dropdown: a filter button showing the label and the current value, opening a radio listbox (a bottom sheet on a phone), synced to the URL and localStorage. Used by the Tests papers and sittings filters, and by Results and Mistakes. → built in F1 kit.js
- A .stat tile (k label + .num), a .btn-2 secondary button and a confidence chip in ui.css, used by Tests, Check your work, the report and the lobby.
- UI.bandChart(host, sittings, opts): the Results score chart extracted, so the Tests score card can draw it at 120px. → built in F1 charts.js
- UI.KIND: one kind-name map (mock→'Full section', paper→'Paper #N', module→'Module …', custom→'Custom test', diagnostic→'Diagnostic', drill→'Practice', challenge→'Challenge', twin_of→'Twin of …', shared_from→'Shared by …', retake→'Retake N'), used by Tests, Results, the report and Today. → built in F1 kit.js
- UI.saveQueue: an ordered, retried request queue with a localStorage mirror, a made_left stamp and a status callback. Used for test answers and state, and for practice (drill) answers. → built in F3 question.js / runner.js
- UI.sheet and UI.confirm helpers: a dialog.sheet with a title, a close button, focus return and an Esc guard. Used by the confirm sheets (Save and exit, Discard), Share, Discussion and every tool sheet. → built in F1 kit.js
- The profile's test_prefs: the start sheet's defaults and Me's Learning Preferences are the same stored setting.  
  ↳ R11: one prefs registry (F4 prefs.py), UI.prefs (F2)
- A text-size setting (localStorage satf.textsize → --stem on :root), shared by the test window, the practice session and the report's review.
- The report page must accept ?q=M1-3 (open that question in review), render notes, highlights, confidence calibration, away time and answer changes, and list share peers.

### 3.4.8 Acceptance checks

1. curl -s -X POST localhost:8000/api/mock/new -H 'X-Learner: a:v2revacc01' -H 'content-type: application/json' -d '{"kind":"section"}' returns begun:false, questions:[], question_count:22 and seconds:2100. A GET 3 s later still reports seconds 2100.
2. The old body {"full":false} still returns a module sitting (Today and Plan keep working), and it lands on the lobby with begun:false.
3. POST /api/session/{id}/answer before /begin returns 409. After POST /begin, GET returns 22 questions and seconds starts to fall.
4. POST /cfg {timing:'x1.5'} before begin changes seconds to 3150. After begin, the same call returns 409.
5. POST /pause, wait 4 s, then GET: seconds unchanged (±1), questions:[], paused:true. /answer returns 409. POST /begin resumes, and the clock falls again from the same value.
6. POST /state {question_id:'m1q01', marked:true, struck:[0,2], ms:12000, conf:'guess'}, then the ms part again, then GET: qstate.m1q01 shows marked true, struck [0,2], ms 24000, conf 'guess'.
7. A recursive key scan of the GET /api/session/{id} JSON (including qstate) finds none of: answer, rationale, reasons, key, seed.
8. GET /api/session/{id} with X-Learner a:v2revother returns 403. With no X-Learner header at all it also returns 403.
9. After finishing module 1: the response has next_module 2 and a summary where answered+unanswered == 22. GET shows begun:false and seconds 2100 for module 2, unchanged 3 s later, until /begin.
10. In test_flow: move module_started back 36 min in the DB. /answer then returns 409 'time is up'. The same answer with made_left:5 is accepted, and result.late is 1 after finish.
11. {"kind":"section","m1":"upper"}: module 1 difficulties count easy 3 / medium 8 / hard 11. After hand-in the results have estimate null and scored false. {"kind":"module","module":"m2u"} also finishes with scored false.
12. {"kind":"section","timing":"x1.5"} gives seconds 3150 after begin; x2 gives 4200; untimed gives null.
13. {"kind":"twin","twin_of":<finished section>}: slot by slot, module 1's stored template and difficulty equal the source's, every seed differs, and the grid-in positions are equal.
14. GET /api/tests lists papers with n 1..7 (label 'Launch set') and this ISO week's paper. Two learners starting {"kind":"paper","paper":1} and beginning get identical module 1 stems.
15. After a learner sits paper 1 twice, the paper's sat_by counts them once, and history marks the second sitting retake:2.
16. GET /api/papers/1/posts before any finished sitting of paper 1 returns gated:true and no text. After one it returns threads. POST without a profile name returns 422. A third report from different codes hides the post.
17. POST /api/session/{finished}/share returns a code. GET /api/shared/{code} contains no stems or keys. {"kind":"shared","shared":code} gives a module 1 whose template and seed equal the source's, slot by slot.
18. GET /api/history?all=1 lists an unfinished sitting with status in_progress and left_seconds. A finished section has modules[0].asked == 22 and separate missed and blank lists.
19. POST /api/session/{id}/discard, then: /api/history?all=1 no longer lists it, /api/tests.in_progress is empty, the row's finished is still NULL, and /api/today tested stays false.
20. Opening http://localhost:8000/test/ with no ?s= creates no row (sqlite3 server/satfreshman.db "SELECT count(*) FROM sessions" unchanged) and lands on /tests/ with the start sheet open at Diagnostic.
21. With the server returning 404 for a made-up id, /test/?s=nope shows 'This test doesn't exist.' and no sample questions.
22. POST /api/report with a question context returns an id, and sqlite3 server/satfreshman.db "SELECT template, seed FROM reports WHERE id='…'" is non-null. A 201-character title gets 422, the 21st report in a day gets 429, and GET /api/reports lists it with status 'open'.
23. Browser 1280, /test/?s=ID: the lobby shows 'Enter fullscreen and begin', 'Begin without fullscreen' and a Change link on Timing. 'Begin without fullscreen' reveals question 1 with the Directions sheet open.
24. Browser: press M. #markBtn gets aria-pressed=true, and strip segment 1 shows the amber dot. After a reload, both are still there.
25. Browser: press C on a multiple-choice question. Option C gets aria-checked=true and the calculator stays closed. Press G: the calculator opens.
26. Browser: turn Eliminate on and click the strike on B. B's text has a line-through and 'Undo' shows. Shift+C strikes C. A reload keeps both.
27. Browser: on question 22 the Next label is 'Review'. Clicking it shows 'Check your work', and the three tile numbers add up to 22. Switching Show to Time prints a time under each cell. Clicking cell 5 opens question 5, and the browser's Back from #review returns to the question.
28. Browser: N opens the navigator. Esc closes it, and document.activeElement is #navBtn.
29. Browser grid-in at 1280: the 'Entering your answer' rail is visible beside the column with the examples table. Typing '1/2/3' leaves '1/2', and the preview renders a KaTeX fraction. '-12345' is accepted; '123456' is refused with the hint shown.
30. Browser: with DevTools offline, choosing an answer shows 'Offline · 1 answer waiting' in #saved. Back online, it shows 'Saved', and the server's answers include it.
31. Browser: Save and exit lands on /tests/. The In progress card shows 'Paused · mm:ss left', matching the seconds from GET.
32. Browser: at 300 s left or less (use a custom test with minutes:6), the hidden clock unhides and the '5 minutes left' toast shows.
33. Browser /tests/ at 390: document.documentElement.scrollWidth === 390. At 1280, #kinds and #papers each compute 3 grid columns, and the section nav shows counts.
34. Browser /tests/ for a new learner a:v2revacc99: the score card shows 'No estimate yet' with the 'No data' chip, the sittings list shows 'Nothing sat yet', Up next recommends the diagnostic, Papers lists at least 7 cards each reading 'Not sat', and there are no page errors.
35. Browser /tests/ with scored sittings: the score card shows a confidence chip with a reason line, 'Routed up N of M sections' and 'Counted: …'.
36. Browser /tests/: setting Kind to Modules removes the section rows, and the URL gains ?kind=module. The filter survives a reload. Export CSV downloads a file whose row count equals the number of visible rows.
37. Browser: a sitting with blanks shows outlined chips for blanks and filled chips for wrong answers, and each chip links to /results/report/?id=…&q=M1-n.
38. Browser start sheet: choosing Full section with Module 1 'Harder' shows 'Harder or easier module 1 is practice, not a score estimate', and the summary line updates. Ticking 'Save these as my defaults' updates GET /api/me profile.test_prefs.
39. The runner at 390 shows no Bluebook dashed rule (.rule elements absent). Every option is a .opt tile from ui.css, and the × Save and exit button is visible in the top bar.
40. PYTHONPATH=. python3 server/test_flow.py passes, including the new checks.

### 3.4.9 This section's open questions

Folded into Part 5 where they need a decision; kept here for context.

- Discussion on papers: it is designed with a gate (you must have sat the paper), report-to-hide at 3 reports, a 20-a-day limit and a moderation tool. With anonymous codes, one person can mint many codes. Launch it as specified, or keep it behind a flag until someone is assigned to moderate?
- The weekly paper: Monday 00:00 UTC is proposed. Should its first week double as a 'this week' board (ranked like the daily challenge), or stay a percentile only?
- Save and exit pauses the clock on a timed sitting, and the number of pauses is shown on the report and flagged. Is pausing acceptable, or should timed sittings only allow Save and exit with the clock running?
- Should extended-time sittings (1.5x, 2x) appear on the score chart as estimates flagged 'extended time', as proposed, or be treated as practice?
- Should the route (harder or easier module 2) stay hidden until the report by default, as in Bluebook? Tools offers a toggle to reveal it.
- Share: should the sharer's score be shown to friends by default (the proposed default is on, with a toggle), and should a share link expire?
- Report screenshots: up to 10 images, shrunk on the device and stored on disk under server/reports/. Is storing uploads acceptable, given that (template, seed) already reproduces the item?
- The diagnostic still asks for a name and email before its result. Keep that gate, given the 'completely free, no gates' brief, or show the result directly like every other sitting?
- Desmos: the key is the public trial key (DESMOS_KEY in ui.js and test.js). A production key is needed before launch.
- The runner shell also changes the practice session: footer navigation, a navigator and the shared key map. Confirm that this section owns runner.js/css and UI.keys, and that the practice-session spec adopts them rather than writing its own.
- When a Reading and Writing bank exists: 4 modules, a 10-minute break between sections, and the split pane. The shell keeps a passage-pane slot for it. Build that now, or leave it until the bank exists?

---

## 3.5 Score report and results

> **Spec title:** Score report and results (/results/report/ and /results/)  
> **Built by:** S6, F3 (review player), F6 (report dialog)  
> **Read with resolutions:** R5, R7, R16, R17, R18, R20, R23, R24, R26, R35, R38 (§2.2). Where this spec disagrees with them, they win.

### 3.5.1 What they have

- **Report header**: “PRACTICE TEST REVIEW · Paper #47 · 2025-08-31”: the kind, the paper's name, and a date styled like an official form's.
- **Section ring gauges**: One ring per section (R&W, Math): score/800 and “2 Correct, 25 Wrong”. That line counts unanswered as wrong: the API says wrong 0 / unanswered 25, and the Performance Summary on the same page says 0 Incorrect / 45 Unanswered, so the page contradicts itself.
- **Total score card**: A blue centre card: Total Score 420/1600, a progress bar and “4 of 49 correct”.
- **Ranked pill and percentile (bundle)**: “N% scored at or below you on their {first} attempt”, shown only for ranked sittings (the first attempt). Otherwise a “Practice test — not ranked” pill (ranked:false, attemptNumber).
- **Count-up numbers**: The scores and tiles count up on load.
- **Performance summary tiles**: Correct / Incorrect / Unanswered / Accuracy % (e.g. 8.2% = 4/49), animated in.
- **Domain performance**: An R&W | Math segmented toggle, then a 2×2 grid of domain cards: name, %, a 7-segment level bar (level 0–7) and mislabelled copy (“13% · 13% of test section, 1-8 questions”, which means 1 of 8 correct). The API also returns a per-domain domainScore that the UI never shows.
- **Question review filters**: A segmented control: All / R&W / Math / Flagged (n).
- **Review legend**: Correct / Incorrect / Unanswered / Flagged for review (n).
- **Per-module colour grids**: Groups headed “R&W - M1  2/27”. Big squares: green correct, red incorrect, grey unanswered, and an orange corner dot when flagged.
- **Review modal: chrome**: Title “R&W - M1 · Q1”. Status chip (Correct / Unanswered) and a “Flagged for review” chip. Buttons: Hide answers, Report, “1 of 49”, Close. ← → arrow keys; Previous/Next run across all 49.
- **Review modal: body**: The passage in a grey box, the stem, then the choices with the key in green. YOUR ANSWER box (reads “Unanswered” when blank) and CORRECT ANSWER box. The explanation opens with “Justification:”, then “Distractor Analysis:” gives one line per wrong option.
- **Hide answers**: Shows an “Answers hidden” chip, removes the key box and the explanation, and turns the button into Show answers. The state persists across Next. You cannot re-answer.
- **Per-question data gaps**: The review payload has no domain, skill, difficulty or time spent, so the report cannot say which skill a question tested or how long it took.
- **Report-a-problem modal (shared)**: A read-only “Sent with your report” box (exam, title, ID). Title (0/200). Category: General / Bug / Wrong answer key / Typo / Feature request / Other. Details (0/5000). Up to 10 image attachments of 50 MB each. [Send feedback].
- **Details popover (QBank, same question data)**: QUESTION ID 06469-DC, DOMAIN, SKILL, DIFFICULTY. It does not show the 1–7 Question Score.
- **Attempt History (QBank)**: “#1 ⊗ Incorrect · Option A · 00:22 · Sep 23, 11:35 AM”. Empty: “No attempts yet.” Per question only; not in the report.
- **Question Overview Status | Difficulty (QBank)**: The grid can be coloured by status (Unanswered, Correct, Incorrect, Mixed = diagonal split, Marked, Current) or by difficulty (Easy / Medium / Hard tints). It lives in the session, not the report.
- **Results list: Score Overview card**: It renders “Total Estimated Score / Math / English” only after a full four-module test. Empty: “Complete a practice test to see your score overview.” The “Share / Export Report” button has no click handler (dead).
- **Results list: review cards**: “Paper #47”, “COMPLETED: 8H AGO” (relative time), then one row per module (“R&W Module 1”) of red chips for wrong and unanswered numbers together (“2 3 4 5 6 7 +19”). The chips are plain spans, not links. A full-width [Review]. No score on the card, although the API returns composite, RW and Math.
- **Results list paging and empty state**: Pages of 10 with Previous/Next. Empty: “No completed exams yet. / Complete a practice test to see your results here.”
- **Estimated Score card (Practice catalog)**: “Math 200-280 · LOW CONFIDENCE” (red) and “Math estimate only. Practice Reading & Writing to see your total score range.” It is built from summary {status PARTIAL, sections {math {average, min, max, attempts}}, confidence {level, label, reason}, trend {direction, delta}, headline}. A section sitting at the 200 floor is dropped.
- **Counting quirks**: A “Custom Set · 2 Modules” sitting never counts as a test (Your last score: Not taken; Exam Attempts 0/1).
- **Related: Profile**: A Score Trend chart (“Latest: 0”), a subject-performance snapshot, and Streak / Tests / Solved / Vocab tiles. The streak there differs from the QOTD streak.
- **Related: contest time analysis**: “Average seconds per answered question, by difficulty” (empty), plus per-contest Score / Correct / Incorrect / Skipped / Voided.
- **Related: dashboard**: Recent Tests card (“TOTAL SCORE · 23/09/2026 · 420 · R&W 200 · Math 220 · [Review]”), study time today/month, and an activity calendar.
- **Weaknesses**: The overview is empty until a full test. Domain copy is confusing. Unanswered counts as wrong in one place and not another. Nothing shows skill, difficulty or time per question. Export is a no-op. QBank sessions have no report at all. There is no way to get another question like the one you missed.

### 3.5.2 What we have now

Status is have / partial / missing / worse, against theirs.

- **Section score**: *partial.* A big band (“520–660”) and “Math · 31/44 · harder module 2”. No gauge, no target, no comparison with the last sitting, and nothing saying how the band is estimated.
- **Total /1600**: *missing.* The bank is Math only. There is no R&W score, so an honest total is impossible without a new input.
- **Percentile / ranked**: *missing.* Nothing compares a sitting with other students, although first sittings of every learner are in sessions.
- **Right of asked**: *have.* “31/44” under the band, and a big “5/12” for practice sets.
- **Summary tiles**: *missing.* No Correct / Incorrect / Unanswered / Accuracy / Time tiles. A test's time is never shown.
- **Domains**: *partial.* Four cards with a band word, a weighted bar and right/asked. No %, no share of the section, no skills, no change since last time. Practice sets get no domains (drill.finish stores none).
- **Skills in a sitting**: *partial.* Practice sets show topic rows with before → after mastery. Tests show no topics at all.
- **Accuracy by difficulty / format**: *missing.* Every review item carries difficulty and type, and nothing uses them.
- **Review filters**: *missing.* No All / Incorrect / Unanswered / Flagged / module / domain / difficulty filters.
- **Per-module grids**: *worse.* M1/M2 rows exist, but there is no legend and no per-module score. Status is by colour alone (orange right, graphite wrong, as in the session), with no glyphs.
- **Flagged questions**: *missing.* Mark for review lives only in test.js memory (S.marked = new Set()). It is never sent, is lost on reload, and the report cannot show it.
- **Answer changes**: *missing.* put_answer overwrites in place, so a right answer changed to a wrong one leaves no trace.
- **Review panel**: *partial.* An inline tile under the grid: key outlined, wrong pick struck, mistake, rationale, Previous/Next. Missing: Your/Correct answer labels, status chip, “n of N”, difficulty, skill ID, time, Hide answers, Report, Save and the other options' misconceptions. On a phone it sits at the bottom of a 2,800px page.
- **Named mistakes list**: *partial.* Unique to us, but broken three ways. It silently stops at 12 (a 13-miss section showed 12). It numbers questions globally (“Q26”) while the grid uses “M2 4”. It lists a missed grid-in under its skill name as if that were a misconception.
- **Fix these**: *have.* Ours only: POST /api/drill {from_session} turns every miss into a fresh question on the same template. There is one variant: all misses, blanks included, once each.
- **Report a problem**: *missing.* Not on the report or in the session.
- **Share / export**: *worse.* No print, CSV or link. GET /api/session/{sid}/results has no ownership check at all (200 with no header), so a shared link to today's challenge report would leak the answers of a live leaderboard.
- **Overview: score over time**: *partial.* Better than theirs because it fills from any scored sitting, with a trend line. But there is no legend, no target line and no tooltip, points cannot be clicked, same-day sittings are all “Sep 23”, and there are no range or kind filters.
- **Overview: estimate**: *missing.* Only the latest band. No combined estimate, confidence or trend (theirs has all three on Practice).
- **Overview: totals**: *worse.* “Answered” is all time but “Right 71%” covers the last 14 days, so they mix windows. No study time, test count, open/fixed mistakes or best. Tests add 0 study minutes, because record_paper files ms=None.
- **Overview: skills**: *partial.* 19 tiles with a mastery bar and an open-mistake dot. Every tile links to a generic /practice/, with no counts, no accuracy and no skill detail.
- **Overview: sittings list**: *worse.* Date, kind, topic glyphs and score only. No wrong-question chips, duration, filters, sort, Fix, or in-progress/resume. Same-second finishes tie because the order is finished DESC with no tie-break.
- **Empty / error states**: *worse.* A new learner sees a giant dash and a quiet “Take a test”. A bad id shows a dash, one error line and an orphan QUESTIONS heading. An unfinished drill's report redirects to /test/ instead of /practice/session/. The overview swallows API failures (.catch → return) and goes blank.
- **Practice session → report**: *missing.* The drill summary never links to /results/report/ for that set, although the endpoint serves drills. Review items also drop the repair flag (app public() strips it).

### 3.5.3 Design

##### Review changes

What I changed from the proposed spec, and why:

1. **Colour semantics follow the practice session. There is no site-wide flip.**
   - The session is the reference format (“the practice one is the best”). It paints right orange (`.seg.ok`, `.opt.ok`) and wrong graphite (`.seg.no`).
   - The proposal flipped that for this section only and asked other sections to follow.
   - Now the grid, the strips, the navigator and the option marks use the session's meanings. Every state also carries a glyph (✓ ✕ – bookmark ↻), and a legend is always visible. The key keeps the session's orange mark and gains a “Correct answer” tag.
2. **Percentile and a ranked pill added** (theirs: “N% scored at or below you on their first attempt” / “not ranked”). Ours is computed from SAT Freshman's own first sittings, says how many students it counts, and says why a sitting is not ranked.
3. **An estimate with confidence and trend added to Results** (theirs: “Math 200–280 · LOW CONFIDENCE” with a reason and a trend). Ours uses every scored sitting, including floor scores, which theirs drops.
4. **Minimalism removed from the proposal itself:**
   - The mistakes list no longer collapses after 8, and “Not answered” is no longer folded away.
   - “Why each wrong answer is wrong” is open by default. Theirs always prints the distractor analysis.
   - The domain card keeps its difficulty-weighted 7-segment level bar, next to the per-question strip.
   - Skills in a sitting are a visible section, not a “Skills ▾” disclosure.
   - The chart's trend line is back.
   - A filter with 0 shows disabled instead of disappearing.
   - The phone filter bar wraps instead of scrolling sideways.
   - Tools carry text labels on desktop.
5. **Their review details now match:**
   - Your answer / Correct answer boxes for multiple choice as well, reading “Not answered” when blank.
   - Hide answers persists across Previous/Next, with an “Answers hidden” chip.
   - A Details popover with the question ID (template · seed), domain, skill, difficulty, format and time.
   - Count-up numbers.
   - Relative time (“8 h ago”).
6. **A Module filter** (All / Module 1 / Module 2): our equivalent of their R&W / Math filter.
7. **Report-a-problem is at least as capable as theirs:**
   - A “Sent with your report” box and a prefilled title with a counter.
   - Their categories plus ours.
   - Details with a counter and up to 3 screenshots.
   - A “Reported” chip afterwards.
   - The flag icon is gone, because a flag already means “flagged for review”.
8. **Extras only our bank allows:**
   - Answer changes (right → wrong and the others).
   - A what-if line (“the 3 easy misses would have made it 560–700”).
   - Per-template history across every sitting (their Attempt History, but per question type and over time).
   - “×3 all time” on a misconception.
   - Before → after mastery for tests too.
   - Domains across the last five sections.
   - A 14-day activity chart.
   - Sequence numbers (“Section #7”).
   - How the crowd picked each option on the challenge.
   - A read-only progress link for a tutor or parent.
9. **“Redo with new numbers” is now two actions:**
   - **Retake as a test:** a parallel section, same templates on fresh seeds matched on tier and format through `blueprint.draw_matching`, with Module 2 routed afresh and scored like any section.
   - **Redo as practice:** a timed drill that shows answers. It cannot measure a score.
10. **Conflicts fixed:**
    - **Twin drills:** every “Try one like this” used to create a 1-question drill that would flood the sittings and in-progress lists. Twins are now one drill per question with `source:\"twin\"`, `parent`, left out of lists and counted on the parent.
    - **Challenge leaks:** a shared link to today's challenge report would leak a live leaderboard's answers. Challenge reports are now owner-only until the day is over everywhere.
    - **Drills ended early:** these leave one served, unanswered question. It is now “Not reached” and left out of counts, so the report agrees with `asked`.
    - **The band note:** a single module is ±100, like the diagnostic (`scoring.score`). Only the full section is ±70.
    - **The repair flag:** review items were missing `repair`, because `public()` drops it.
11. **Expired and untimed unfinished sittings** show in In progress (“Time ran out · See your report”), so none are stranded.
12. **Primary buttons:** “one primary per screen” became one primary per region (page header, player, skill panel).

---

#### Score report and results

This covers two pages, `/results/report/?id=` (one sitting) and `/results/` (the overview), plus the review player both of them open. The player is the practice session's layout, as asked.

##### 0. Rules for this section

- Several pills, borders, labels, legends, counts and one-line helpers are all allowed. There is one orange-filled primary per region: the page header, the player and the skill panel.

**Status semantics (the practice session's own, now with glyphs):**
- **Correct:** `--amber` fill, `--ink-deep` number, ✓ in the top-right corner. This is `.seg.ok` in the session.
- **Incorrect:** `--ink` fill, white number, ✕ corner. This is `.seg.no`.
- **Incorrect, fixed since:** paper fill, 1.5px `--ink` edge, ink number, ✕ corner, plus a small orange ✓ badge bottom-right. The trap has closed since the sitting.
- **Unanswered:** paper fill, 1.5px dashed `--faint` edge, `--soft` number, “–” corner.
- **Not reached** (practice set ended with a question on screen): dotted `--faint` edge, “·” corner, left out of every count.
- **Flagged:** a bookmark glyph in the top-left corner, ink on light cells and white on graphite ones.
- **Repair:** ↻ in the bottom-left corner.
- **Current:** a 2px ink ring with a 2px paper gap.
- **Filtered out:** 30% opacity.

**Other rules:**
- **Open mistakes in lists** keep the site's orange dot. The legend says so.
- **Buckets:** Correct / Incorrect / Unanswered are one set of buckets everywhere. Incorrect never includes blanks, so gauge, tiles, grid, list and CSV always agree. (Theirs contradict themselves.)
- **Numbering is one scheme:** “M1 Q7” / “M2 Q4” in a section; “Q7” in a module, diagnostic, practice set or challenge. The grid, mistakes, table, player, list chips, CSV and URL hash (`#q=m1-7`, `#q=7`) all use it.
- **Difficulty glyph:** three ascending bars (1, 2 or 3 filled) plus the word Easy / Medium / Hard. It is never colour alone.
- **Fonts:** DM Mono for every count, time and %; Source Serif 4 for question text; Archivo for the rest.
- **Motion:** numbers count up over 600 ms and bars grow on first paint, once. `prefers-reduced-motion` shows final values at once.

##### 1. Report page `/results/report/?id=<sid>`

###### 1.1 Layout
- **Desktop (≥1100):** `main.page` (max 1120), a 12-column grid, 24px gaps. Each section opens with a `.k` eyebrow and a one-line helper in `--soft` where it helps.
- **Section order:** header, hero, tiles, modules, domains, skills in this sitting, difficulty & format, pace, answer changes, mistakes, question review, up next.
- **Tablet (860–1099):** the same order; tiles 4 across.
- **Phone (390):** 16px gutters, one column.
  - Tiles run 2 across (4 rows) and domains 2×2.
  - Once the hero scrolls away, an action strip sticks under the top bar: the primary, plus “Review” and ⋯.
  - No horizontal page scroll.
  - Charts and grid scale to width; the table becomes stacked cards.

###### 1.2 Header (`#head`)

**Back link:** “← Results”.

**Eyebrow, by kind, with the learner's sequence number for that kind (`seq`):**
- mock: “PRACTICE TEST · FULL MATH SECTION #7 · ADAPTIVE” (shelf mocks add “· FORM 1.3”)
- module: “PRACTICE TEST · ONE MODULE #2”
- diagnostic: “DIAGNOSTIC”
- drill: “PRACTICE SET #45 · FROM SECTION #7”. The source label comes from cfg.source: Map / Mistakes / Saved / Fix these / Plan.
- challenge: “DAILY CHALLENGE · SEP 23”

**Title line:** “Wed, Sep 23, 2026 · 6:15 AM · 64 min · Timed”. Untimed sittings say “Untimed”; minutes are omitted when unknown.

**Actions** (right-aligned on desktop, a row under the title on phone):
1. **Primary split pill “Fix these · 13”.** The main part runs every miss once. ⌄ opens a menu:
   - “Incorrect only · 11”
   - “Not answered · 2”
   - “Still open only · 9” (skips misses whose trap has closed since)
   - “Each miss twice · 26”
   - “Just the 4 shown” (only while a review filter is set)

   Each item POSTs `/api/drill {from_session, only?, each?}` and goes to `/practice/session/?id=`.
2. **Outline “Review mistakes”:** opens the player filtered to Incorrect + Unanswered.
3. **Outline “Retake as a test”** (mock, module, diagnostic): POST `/api/mock/new {like: sid, full}`. It builds a parallel section on the same templates with fresh seeds, then goes to `/test/?s=`. The helper under it on hover/focus: “Same question types, new numbers. Scored like any section.”
4. **⋯ menu:**
   - “Redo as practice · answers shown · 44” (POST `/api/drill {from_session, scope:\"all\", timed:true}`)
   - “Copy share link”, with the toast “Link copied · read-only”
   - “Print / Save as PDF”
   - “Download CSV”
   - “Report a problem with this sitting”
   - For drills, “Retake as a test” becomes “Same set, new numbers” (the drill `scope:\"all\"`).

**No misses:** the primary becomes “Harder next · New section” (tests) or the coach's “Keep going” (drills), and the helper reads “Every question right.”

**Not the owner** (`mine:false`): a strip reads “Shared report · read-only”. Fix, Retake, Save, Try one like this, Report and every drill action are hidden. The review works.

###### 1.3 Score hero (`#hero`)

**Mock, module and diagnostic.** Gauge 5 columns and facts 7 columns on desktop; stacked on phone.

**`UI.gauge`:** a 240° arc from 200 to 800.
- Ticks 200 / 400 / 600 / 800.
- This sitting's band is an orange segment, low to high, with a graphite midpoint tick.
- The previous same-kind band is a `--mat` ghost segment.
- The target is a dashed ink tick labelled “Target 700”.
- Centre: “520–660” (Archivo 800, 56px desktop / 44px phone). Under it, “Math · middle 590”.
- Caption: “Math section only · Reading and Writing is not on SAT Freshman yet”.

**Facts:**
- “31 of 44 correct · 70%”.
- **Delta chip:** “+90 vs Section #6 (Sep 20)”, from the difference in midpoints. “First section” when there is none.
- **Target:** “Target 700 · 40 above this high end”, or “Target reached”. Omitted when no target is set, and replaced by the link “Set a target” (→ /plan/).
- **Percentile:** “62% of students here scored at or below you on their first section (148 students)”.
  - Pill “Ranked · your first section”.
  - Or “Not ranked · retake #3”, with the helper “Only first sittings are ranked, so retakes can't inflate it.”
  - With fewer than 20 first sittings of that kind: “A percentile needs 20 first sections; 8 so far.”
- **Route:**
  - Upper: “Module 1: 15/22 (68%). 60% or more earns the harder Module 2.”
  - Lower: “Module 1: 11/22 (50%) → easier Module 2, which tops out at 580.” Plus “Capped at 580 by the easier route.” when capped.
- **What-if** (from `whatif`): “3 easy misses. With them right: 560–700 on the same Module 2.” If there are no easy misses, it uses medium misses. Omitted when nothing was missed.
- **Twins:** “Tried 3 like this since · 2 right” (from `twins`), linking to the mistakes section.
- **`<details>` “How this is estimated”:**
  - “Each question counts by difficulty: easy 1, medium 2, hard 3.”
  - “The band is ±70 on a full section and ±100 on one module or the diagnostic, because these questions are not calibrated on real test-takers.”
  - “College Board's own simulation caps the easier Module 2 at 580.”
  - “The percentile compares SAT Freshman students only, not the national SAT.”

**Drill:**
- Big “5/12” and “42%”.
- Meta: “10 asked + 2 repairs · 17 min · Nonlinear functions, Probability”.
- “4 mistakes opened · 1 fixed”, each count linking to Mistakes.

**Challenge:**
- Big “8/10” and “9:42”.
- “#12 of 140 today · average 6.1/10” and a “Board” link.

###### 1.4 Summary tiles (`#tiles`, `UI.tile`)

Eight tiles: 4×2 on desktop and tablet, 2×4 on phone. Each has a label, a value (mono 26px) and a sub-line.

| label | value | sub-line |
|---|---|---|
| Correct | 31 | “70% of 44” |
| Incorrect | 11 | “9 still open” |
| Unanswered | 2 | “counted as not correct” |
| Accuracy | 70% | “76% of answered” |
| Time | 64:12 | “of 70:00”, or “untimed” |
| Per question | 1:27 | “test pace 1:35” |
| Flagged | 3 | “2 of them wrong” |
| Changed | 5 | “1 right → wrong” |

- **Drill:** the tiles become Correct / Incorrect / Repairs / Accuracy / Time / Per question / Opened / Fixed.
- **Missing data** (old sittings, from before flags, times or trail were recorded): the value is “—” and the sub-line reads “Not recorded for this sitting”. The tile stays, so the layout never jumps.
- Every tile that is a count also acts as a review filter (click → filter + scroll).

###### 1.5 Modules (`#modules`; mock, and module with one tile)
- Two tiles, stacked on phone:
  - “Module 1 · mixed · 15/22 · 68% · 31:40 of 35:00 · 2 flagged”
  - “Module 2 · harder · 16/22 · 73% · 34:05 of 35:00 · 1 flagged”
- Each has a 22-segment status strip; clicking a segment opens the player at that question.

###### 1.6 Domains (`#domains`)

Four cards: 4 across on desktop, 2×2 on phone. Each card has:
- The name.
- “73%” (mono 28px) and “11 of 15 correct”.
- A **7-segment level bar**, difficulty-weighted `mastery` × 7 rounded, with the band word (“Steady”) and the helper tooltip “Weighted by difficulty, like the domain bars on an official score report.”
- A **per-question strip**, one status segment per question in that domain, each clickable.
- **Share:** “15 of 44 questions · 35% of the section (the SAT's Algebra weight is 35%)”.
- **Delta:** “+2 correct vs Section #6”. Shown only when a previous same-kind sitting exists; otherwise “First section”.
- **Focus:** “Missed most: Linear inequalities, Systems” (scoring's existing `focus`).

Drills and challenges get domains too.

**Helper:** “A domain is a handful of questions, so read one weak card as a hint, not a verdict.”

###### 1.7 Skills in this sitting (`#skills`, every kind)
- A table, stacked rows on phone. One row per topic in the sitting, sorted by misses:
  - glyph and name, and the domain;
  - “4/6 · 67%”;
  - a mastery bar animating before → after (tests now too);
  - “2 open” in orange when there are open traps;
  - a “Practise” link to `/practice/?topics=<slug>`.
- Clicking the row applies the topic filter and scrolls to the review.

###### 1.8 Difficulty and format (`#split`)
- Easy / Medium / Hard rows: glyph, “6/6 · 100%”, bar, “avg 0:58”.
- Multiple choice / Grid-in rows in the same form.
- Clicking a row sets that filter.

###### 1.9 Pace (`#pace`)

**Chart:**
- One bar per question, with a gap between M1 and M2. Height is seconds and the fill is status.
- A dashed line at 95 s labelled “Test pace 1:35”.
- The y-axis caps at 5:00, with an arrow on bars past it.
- Hover or tap shows the tooltip “M2 Q19 · 4:12 · Incorrect · Hard”; a click opens the player.

**Chips (each one a filter):**
- “Rushed misses · 3 (under 0:30 and wrong)”
- “Long solves · 4 (over 3:10)”
- “Slowest: M2 Q19 4:12”

**Phone:** 44 bars fit in 358px.

**No time data:** the heading stays, with the line “Times were not recorded for this sitting.”

###### 1.10 Answer changes (`#changes`, tests)
- “You changed 5 answers: 2 wrong → right · 1 right → wrong · 2 wrong → wrong”. Each count is a filter (“Changed”).
- The helper: “Second-guessing cost 1 question; changing paid off twice.”
- No trail: “Answer changes were not recorded for this sitting.”

###### 1.11 Mistakes (`#mistakes`)

**Heading:** “Mistakes · 13”, with the helper “9 named misconceptions · 2 grid-ins · 2 not answered · 3 fixed since”.

**Sort select:** Question order / Open first / By topic / Most hit.

**Groups, all shown, never cut:** Open (n), Fixed since (n), Not answered (n).

**Misconception row:**
- Topic glyph, then the misconception text (600 15px).
- Meta: “M1 Q1 · Linear inequalities · Hard · ×3 all time”.
- State: “Open · 2 clean answers to close” with an orange dot, or “Fixed Sep 24” with a ✓ and a light strike.
- Buttons: “Review” (player), “Try one like this” (player, twin open) and “Fix” (`{from_session, only:[qid], each:2}`).

**Other rows:**
- **Repeats in one sitting:** one row with “×2 here” and both refs as chips.
- **Grid-in misses:** “Missed grid-in: 8/161”, with the skill in the meta line (“Two-way table”).
- **Not answered:** chips “M1 Q22 · M2 Q21” with the skill beside each, plus a “Practise these 2” link.

###### 1.12 Question review (`#review`)

**Toolbar**

It sticks under the page bar on desktop.
- **“Show” segmented with live counts:** All 44 · Incorrect 11 · Unanswered 2 · Correct 31 · Flagged 3 · Saved 1 · Changed 5.
  - A 0 count is disabled, not hidden.
  - Flagged and Changed are absent for drills and challenges, which have neither.
- **Selects:**
  - Module: All / Module 1 / Module 2 (sections only)
  - Domain: All + 4
  - Topic: filtered by the domain
  - Difficulty: All / Easy / Medium / Hard
  - Format: All / Multiple choice / Grid-in
  - Time: All / Rushed / Long
- **“Colour by”:** Status | Difficulty | Time.
- **“View”:** Grid | Table.
- “Reset” shows when any filter is set.
- **State lives in the query string** (`?id=..&show=incorrect&module=2&domain=Algebra`), so it survives reload and share.

**Phone:**
- The Show chips wrap to two rows.
- The selects move into a “Filters · 2” button that opens a bottom sheet.
- View stays visible.
- Nothing scrolls sideways.

**Legend** (always visible, follows Colour by)
- **Status:** Correct ✓ · Incorrect ✕ · Fixed since · Unanswered – · Flagged · Repair ↻ · Not reached, plus “● open mistake”.
- **Difficulty:** three swatches (`--tile` / `--mat` / `--ink` with a white number) plus the glyph.
- **Time:** a 4-step warm-grey ramp, “0:30 · 1:35 · 3:10 · 5:00+”.

**Grid**
- One group per module, headed “Module 1 · 15/22 · 68% · 31:40”. A single-group sitting is headed “Questions · 5/12”.
- Cells are `<button>`s, 40px on desktop and 44px on phone (7 per row), with an aria-label such as “M1 Q7, incorrect, hard, 1:42, flagged, changed B to D”.
- Filtered-out cells stay in place at 30% and are skipped by Tab and by prev/next.
- Challenge cells show the crowd % under the number.

**Table**
- **Columns:** # · Skill (glyph + topic, skill label under it) · Difficulty · Format · Time · Your answer · Correct · Result · Changed · Flag · Mistake.
- Sortable by #, Time, Difficulty and Result, with `aria-sort`.
- It is the default above 60 questions.
- **Phone:** stacked cards, “M1 Q7 · Hard · 1:42”, then the skill, then “You: B · Key: D”, then the mistake.

###### 1.13 Review player (`UI.review`, shared)

**Frame**
- A full-viewport `<dialog>` in the practice session's layout: sticky 60px top bar, 700px question column, sticky bottom bar.
- It opens from any cell, row, chip, mistake, strip segment or pace bar.
- The URL hash becomes `#q=m1-7`: Back closes the player, and a pasted link opens at that question.
- Esc closes it and returns focus to the element that opened it.

**Top bar**
- **Left:** × Close.
- **Centre, the navigator:**
  - 24 questions or fewer: the session's segment strip, in status colours, with the current one ringed.
  - More: the pill “M1 Q7 · 7 of 44 ⌄”, which opens a popover grid with the same cells, legend and filters. Esc closes it.
- **Right tools,** icon plus text label on desktop:
  - Details (i)
  - Hide answers (eye)
  - Save (bookmark)
  - Calculator
  - Reference
  - Report (a speech-bubble ! icon, never a flag)
- **Phone:** Details, Calculator, Reference and Report move into ⋯.

**Question header**
- The topic glyph and topic, then the skill (“Two-way table”).
- The difficulty glyph and word, “Multiple choice” / “Grid-in”, and “1:42 · pace 1:35”.
- Tags, when they apply:
  - “Flagged in test”
  - “Again” (a repair)
  - “Changed B → D”
  - “Reported”
- A status chip on the right: “Correct” / “Incorrect” / “Not answered” / “Incorrect · fixed since”.
- **Details popover:**
  - Question ID `lin_ineq.range · 48213`, with a Copy button
  - Domain, skill, difficulty and format
  - Time on it, the sitting, and its position (M1 Q7)

**Body** (`UI.question` in review mode, the session's rendering)
- The stem in serif, then the figure or table.
- **Multiple choice:**
  - The key has the session's orange `.opt.ok` mark, a ✓ and the tag “Correct answer”.
  - A wrong pick has the session's struck `.opt.no`, a ✕ and the tag “Your answer”.
  - A right pick has “Your answer · Correct”.
  - **Under every wrong option, its misconception** (`reasons[]`, 600 14.5px), with the picked one first in ink and the others in `--soft`. The block is headed “Why each wrong answer is wrong”. It is **open by default**, and it can be collapsed with the choice remembered in localStorage.
- **Answer boxes for every format:**
  - “Your answer: B · 111 ≤ t ≤ 184” and “Correct answer: D · 73 ≤ t ≤ 111”, side by side (stacked on phone).
  - Grid-ins: “Your answer −7” and “Correct answer 8/161”, plus “Also accepted: .0496, .0497” (`accepted`).
  - Blank: “Your answer: Not answered”.
- **Explanation card:** `--tile` fill, heading “Explanation”, the rationale in serif.
- **Mistake state:** “Open mistake · 2 clean answers to close · hit 3× all time”, or “Fixed Sep 24 ✓”.
- **“Earlier on this question type”:** the last 5 attempts on the same template from other sittings (`history`).
  - A row reads “✕ Sep 18 · Section #5 · picked ‘largest value as the bottom’ · 1:10” or “✓ Sep 20 · Fix these · 0:48”, each linking to its report.
  - Empty: “First time on this question type.”
- **Challenge:** “41% of 140 students got this right”, plus how the crowd picked each option: “A 12% · B 41% · C 9% · D 38%”, each wrong one naming its misconception.

**Actions row**
- **Primary “Try one like this”:**
  - On first use it POSTs `/api/drill {from_session, only:[qid], each:5, source:\"twin\"}`.
  - The fresh twin renders **inline** below, in a tile headed “Same question type, new numbers”, in normal answer mode.
  - Answers go through `/api/drill/{id}/answer`, so they file an attempt and can close the trap, and show the session's verdict.
  - “Another like this” calls `/api/drill/{id}/next`. A wrong twin's repair comes next, naturally.
  - “Back to the original” scrolls up.
  - Closing the player finishes a twin drill that has at least one answer.
- **Outline “Practise this skill”:** → `/practice/?topics=<slug>`.
- **Quiet “Keep going in a session”:** opens the twin drill in `/practice/session/`.

**Hide answers** (a mode, not a one-off)
- It hides the key marks, the answer boxes, the reasons, the explanation, the mistake line and the status chip, and makes the options pickable.
- An “Answers hidden” chip shows in the header.
- The mode **persists across Previous/Next** until it is turned off.
- A pick reveals locally (“B · wrong again” / “D · right this time”) without filing anything, and restores that question.

**Bottom bar:** “← Previous” | the position within the active filter (“7 of 11 incorrect”) | “Next →”. With the filter on All, a quiet “Next miss” also shows.

**Keys:**
- ← → or J K: move
- N: next miss
- H: hide answers
- S: save
- T: try one like this
- I: details
- R: report
- A–D or 1–4: pick while hidden
- Esc: close

A hint row on hover devices reads “← → move · N next miss · H hide · T try one”. It is hidden on touch.

###### 1.14 Report a problem (`UI.reportDialog`, shared with the session and the exam runner)
- **“Sent with your report”** (read-only): M1 Q7, the skill, question ID `template · seed`, your answer, the sitting and the date. The item regenerates exactly, so nothing needs a screenshot to be found.
- **Title:** prefilled “M1 Q7 · Linear inequalities”, with a 0/120 counter.
- **Category** (radio list):
  - Wrong answer key
  - Two answers are right
  - Misconception label is wrong
  - Figure or table is wrong
  - Typo
  - Explanation unclear
  - Bug
  - Feature request
  - Other
- **Details:** 0/2000 counter.
- **Screenshots:** “Add screenshots (optional, up to 3, PNG/JPEG/WebP, 5 MB each)”, shown as thumbnails with remove buttons.
- **[Send report].** The sending state is `aria-busy`. On success the toast reads “Report sent. Thanks — we check every one.” and the question gets a “Reported” tag. Failures show inline with a Retry.
- **The ⋯ “Report a problem with this sitting”** opens the same dialog with question fields blank.

###### 1.15 Up next (`#next`)
- The coach's pick from `/api/map`: topic chips, “10 questions · 16 min”, a “Start” pill and a “New section” link.
- It sits last, under a divider.

###### 1.16 States
- **Loading:** static skeletons at real sizes (a gauge circle, 8 tiles, cell rows), `aria-busy` on main. No dashes, no loops.
- **404:** “That sitting does not exist.” with links to All results and Tests. No section headings render.
- **403 diagnostic** (owner not signed up): → `/diagnostic/signup.html?s=`.
- **403 challenge** (another learner, day still live): “This challenge is still running today. Its report opens to others tomorrow.” with a “Sit today's challenge” pill.
- **409 unfinished:** redirect by `detail.kind`. A drill or challenge goes to `/practice/session/?id=`; mock, module and diagnostic go to `/test/?s=`.
- **Network error:** “Couldn't load this report.” with a Try again button that refetches.
- **Nothing answered:**
  - Tiles at 0 and every cell dashed.
  - The hero reads “Nothing answered, so there is no estimate.” and shows no gauge.
  - Fix these reads “Practise all 44”.
- **Old sittings:** the missing tiles show “—” with a reason. Pace and Changes show one line each. The Flagged and Changed filters are disabled with 0.
- **Long practice sets (up to 120):** the grid wraps, the navigator uses the pill, and the table is the default.

###### 1.17 Print (`@media print`)
- Hidden: the bar, the tabs, every button, the toolbar, the player and Up next.
- Printed:
  - hero (with percentile and what-if), tiles, modules and domains;
  - skills, split, pace and changes;
  - all mistakes;
  - the full question table (your answer, key, mistake, time).
- Page breaks avoid splitting a row.

##### 2. Results overview `/results/`

###### 2.1 Header
- H1 “Results”.
- The right ⋯ holds “Download CSV (all sittings)”, “Print” and “Share my progress”.
- **Share my progress** opens a sheet: a read-only link (`/results/?share=<token>`), Copy, and “Stop sharing”. A shared view shows the strip “Shared progress · read-only”, and hides every action and every per-question review.

###### 2.2 Current estimate (`#estimate`, 4 columns beside the chart)
- **The estimate:** “Math 540–680”, big.
  - Label: “Current estimate · from your last 3 scored sittings (sections count double)”.
  - A confidence pill: High / Medium / Low, with its reason, e.g. “Medium · one full section in the last 30 days” or “Low · only modules and the diagnostic so far”.
  - A trend chip: “↑ +40 since Sep 13” (up / down / steady, ±20 threshold).
- **Beside it:**
  - “Latest: 520–660 · Section #7 · Sep 23”
  - “Best: 550–750 · Module #2 · Sep 23”
  - “Target 700 · 20 above your estimate's high end”
  - “Exam Oct 3 · 10 days”
- **Footnote:** “Math section only · Reading and Writing is not on SAT Freshman yet.”
- **Empty:** “Your first test gives you an estimate.”, with buttons “Full section · 70 min” (pill) and “One module · 35 min” (outline). Both POST `/api/mock/new`. Plus a quiet “Diagnostic · 20 questions”.

###### 2.3 Score over time (`#overview`, 8 columns; full width on phone)
- **Marks:**
  - Each scored sitting is a vertical band (low–high) with a middle dot. The newest is orange; the others are graphite.
  - A trend line joins the midpoints.
  - A dashed target line is labelled at its right end.
  - The current estimate is a soft `--wash` horizontal zone.
- **x-axis:** by sitting. Labels add a time when two sittings share a day (“Sep 23 6:15”), and thin out as now.
- **Hover/tap:** a tooltip “Sep 23 · Section #7 · 520–660 · 31/44 · harder M2”, with “Open report”. A click opens the report.
- **Controls:** Range segmented Last 10 | 30 days | All; kind check-chips Sections ☑ · Modules ☑ · Diagnostic ☑.
- **Legend:** “Band = estimated range · dot = middle · line = trend · dashed = target · shaded = current estimate”.
- **Empty:** the axis frame, with a ghost band and “Your first test puts a point here.”

###### 2.4 Totals (`#totals`, 6 tiles; 3×2 on phone; every window is stated)

| label | value | sub-line |
|---|---|---|
| Questions | 1,284 | all time |
| Accuracy | 68% | “all time · last 14 days 72%” |
| Study time | 21 h 40 m | “this week 3 h 10 m” (tests included) |
| Tests | 7 | “5 sections · 2 modules · 1 diagnostic” |
| Streak | 4 days | “best 11” |
| Mistakes | 12 open | “48 fixed” → `/mistakes/` |

**Last 14 days** (under the tiles): a bar per day of questions, split right/wrong, with minutes in the tooltip (“Sep 22 · 34 questions · 71% · 41 min”). Zero days show as a baseline tick. The data is the existing `days.recent`.

###### 2.5 Accuracy split (`#split`)
- All-time rows for Easy / Medium / Hard and Multiple choice / Grid-in: right/answered, %, a bar and the average time.
- Line: “Average time: easy 0:58 · medium 1:31 · hard 2:24 (test pace 1:35)”.

###### 2.6 Domains across sections (`#domtrend`)
- A table: rows are the 4 domains, columns the last 5 scored sittings (“#3 · #4 · #5 · #6 · #7”).
- Each cell shows “11/15 · 73%”, shaded by %, with an arrow against the previous column.
- **Phone:** the last 3 columns.
- **Empty:** “Sit a section to start this table.”

###### 2.7 Skills (`#skills`)
- The 19 tiles, grouped by domain. Each tile has:
  - the glyph, name and mastery bar;
  - “42 answered · 71%” in mono;
  - an orange “2 open” badge;
  - “Not started” for a skill never practised.
- **Sort:** By domain / Weakest first / Most open mistakes / Least practised / Least recent. Any sort except By domain flattens the groups.
- **A click opens the Skill panel:** a right drawer of 420px, or a bottom sheet (max 85vh) on phone. It holds:
  - the name and domain;
  - the mastery bar with “A practice gauge: recent answers, hard ones counting more.”;
  - “Answered 42 · Right 30 · 71%”;
  - by-difficulty rows with average times;
  - “Recent run”: the last 20 as ✓/✕ dots, newest right;
  - open mistakes (label, “hit 3×”, “2 to close”), each with Fix and Review;
  - “Fixed 5”;
  - “Last worked 3 days ago”;
  - the last 5 sittings with the skill, each with its right/asked, as links.
- **Panel actions:** the pill “Practise this skill” (→ `/practice/?topics=<slug>`) and the outline “Fix its mistakes · 2” (`/api/drill {mistakes:true, topics:[slug]}`).

###### 2.8 Top misconceptions (`#traps`)
- The 10 most-hit traps of all time. A row: the label, topic glyph and name, “×4”, “Open · 2 to close” or “Fixed Sep 22”, “last Sep 23”, and Fix.
- The heading carries the pill “Fix all open · 12” and the link “All mistakes”.
- **Empty:** “No mistakes yet. Every miss you make lands here with its name.”

###### 2.9 Sittings (`#sittings`)

**Controls**
- Segmented: All 57 · Tests 9 · Practice 45 · Challenge 3.
- Tests adds a kind select: All / Section / Module / Diagnostic.
- Check-chip “Has open mistakes”.
- Sort: Newest / Oldest / Highest / Lowest.
- Kept in the query string.

**In progress** (a group on top, when there are any)
- “Section #8 · started 6:02 AM · Module 2 · 18:22 left” → Resume (`/test/?s=`).
- “Untimed module · 9 of 22 answered” → Resume.
- “Section #6 · time ran out” → “See your report”, which POSTs finish and opens the report.
- “Practice set · 4 of 10” → Resume (`/practice/session/?id=`).
- Twin drills never appear.

**Groups:** “This week”, “Last week”, then “Sep 7–13”.

**Sitting card** (`UI.sittingCard`, shared with Tests)
- One row on desktop, stacked on phone. The fields:
  - the relative time within 48 h (“8 h ago”), else “Sep 21 · 6:15 AM”;
  - kind, seq and subtitle: “Section #7 · harder M2” / “Practice #45 · Linear functions, Percentages, Circles” / “Daily challenge · #12 of 140”;
  - the score (band, or “10/11 · 91%”), and the delta vs the previous same kind;
  - the duration;
  - **wrong-question chips per module:** “M1 ✕ 1 6 7 11 15 +2”, “M2 ✕ 4 11 12 13”.
    - Overflow shows after 8 per module; “+2” expands inline.
    - Blanks are dashed chips.
    - Each chip links to `/results/report/?id=..#q=m1-6`.
  - “3 still open” when that applies;
  - “Tried 3 like this” when that applies;
  - buttons: “Review” (outline) and “Fix · 7” (text).

**Paging:** 20 at a time, “Showing 20 of 57”, and “Show 20 more” (`/api/history?offset=`).

**Empty:** “Nothing finished yet.” with a “Practise” pill and a “Tests” link.

###### 2.10 States
- **Loading:** skeletons.
- **API failure:** an inline error per section with Try again. The page never goes blank.
- **New learner:** the estimate empty state; tiles at 0; the 14-day chart as a baseline; skills all “Not started”; the traps and domain-table empty lines; the sittings empty state.
- **Lots of history:** the chart defaults to Last 10; the list is paged and grouped; CSV exports everything by looping over `limit=200`.
- **Shared view** (`?share=`): read-only, and every action is hidden.

##### 3. Changes elsewhere, needed for this section
- **Exam runner (`web/test/test.js`):**
  - Mark for review POSTs `/api/session/{sid}/flag`.
  - `S.marked` is restored from `payload.flags` on load and at module 2.
  - The time on each question is accumulated while it is visible, and POSTed to `/time` on every question change and before finish, chained on the existing `sent` promise.
- **Practice session summary:** a “Review every answer” outline → `/results/report/?id=`.
- **Tests page:** its history list uses `UI.sittingCard`, and it shows In progress.
- **Practice page:** accepts `?topics=a,b` to preselect.

##### 4. Accessibility
- **Status:** glyph and text as well as fill.
- **Filters:** `role=radiogroup` or `<select>`.
- **Player:** a `<dialog>` that returns focus on close.
- **Charts:** `role=img` with an aria-label summary, plus a visually hidden data table.
- **Motion:** entry only; `prefers-reduced-motion` respected.
- **Touch targets:** 44px or more on phone.
- **Count-up:** writes the final value to aria at once.

##### 5. Build order
1. **Server:** columns, results fields, the drill options, history, stats, the challenge guard.
2. **Components:** `UI.tile`, the status cell and legend, `UI.gauge`, `UI.review`.
3. **Report page.**
4. **Exam runner:** flags, times, trail.
5. **Overview.**
6. **Report dialog and share progress.**
7. **README and test_flow** at each step.

### 3.5.4 Extras: what they missed

- **Every wrong option's misconception, open by default**: Item.reasons names the misconception behind each distractor. The review shows all three under their options, not just the one picked, so a student learns the whole trap family. Their “Distractor Analysis” is prose; ours names the exact error behind each option, and the same label tracks that error in Mistakes.
- **Try one like this, inline, and it counts**: A fresh twin (same template, new seed) is answered right in the player, and a right answer can close the trap. A finite bank can only re-show an item whose key the student has already seen.
- **Retake as a test (parallel form)**: The same module-1 templates on fresh seeds, matched on tier and format, with Module 2 routed afresh and scored like any section. It answers “did I actually improve on these question types?”, which no fixed paper can.
- **Fix these in variants**: Incorrect only, blanks only, still-open only, each twice, just the filtered ones, and per mistake. Any slice of a report becomes a repair set of new questions.
- **What-if line**: “3 easy misses. With them right: 560–700.” It is recomputed with the real scoring, and turns careless errors into points a student can see.
- **Answer changes**: An answer trail per question shows right → wrong changes, the classic second-guessing leak. Theirs overwrites the answer and cannot know.
- **History of this question type across sittings**: Every question is addressed by template, so the player lists earlier attempts on the same type: date, result, the trap picked, the time. Theirs only has per-item Attempt History inside the QBank.
- **Live mistake status in an old report**: “Open · 2 clean answers to close” or “Fixed Sep 24”, read from traps now, so an old report reflects the work done since.
- **Before → after mastery for tests**: The skills in a sitting show how that sitting moved each skill's gauge, not only for practice sets.
- **Honest percentile**: The percentile is computed from first sittings only, so retakes can't inflate it. It states its student count and hides the number below 20.
- **Estimate with confidence and trend, using every sitting**: The confidence has a reason (“only modules so far”). Floor scores count, which theirs drops, and modules count, which theirs does not.
- **Pace analysis**: Seconds per question against the 1:35 test pace. Rushed misses and long solves are filters, which separate careless errors from hard ones.
- **Routing explained**: Module 1's score, the 60% cut, which Module 2 it earned, and the 580 ceiling. Adaptivity is the most misunderstood part of the digital SAT.
- **Compared with last time, the target and the exam date**: Deltas per sitting and per domain, the target tick on the gauge, the target line on the chart, and days to the exam.
- **Domains across the last five sections**: It shows which domain is actually moving, which a single report cannot.
- **Accuracy and average time by difficulty and format**: It shows whether points leak on easy questions or on grid-ins. This is their contest time analysis, on every sitting.
- **Colour by difficulty or time, and a sortable table**: Their difficulty view lives only in the QBank overview. The table makes 44 questions scannable, printable and exportable.
- **Challenge crowd %, per option**: Everyone sits the same ten, so each question can show “41% got this right” and how many fell for each named misconception.
- **Accepted grid-in forms**: “Also accepted: .0496, .0497” comes from the grid rule we already mark by. It teaches the entry rule that costs students points.
- **Deep links, share link, print/PDF, CSV**: A read-only report for a tutor or parent, a printable review, and exports. Their Share/Export button does nothing.
- **Read-only progress link**: A tutor or parent can follow the overview without an account. Theirs hides classes and teachers behind routes nobody links to.
- **Skill panel on Results**: Mastery, the recent run, per-difficulty accuracy and time, open and fixed traps, the sittings that included the skill, and Practise preselected.
- **Keyboard review**: J/K/N/H/T/S/I/R move through 44 questions without a mouse, as in the practice session.
- **Practice sets have full reports**: Their QBank sessions never end or summarise. Every set here gets the same report as a test.
- **Resume or close out any unfinished sitting**: In progress lists live, untimed and expired sittings. Theirs survive only by URL.
- **Tests count as study time; flags survive reload**: This fixes two real data holes: record_paper files ms=None, and S.marked lives only in memory.
- **Sequence numbers**: “Section #7” gives every fresh section a name a student can refer to. Theirs rely on paper names, and fresh sections have none.

### 3.5.5 Server changes

Tables and columns here are added by F4 as listed in §2.5; the drill fields map through §2.6; prefs through §2.7.

- **Store flags, per-question time and an answer trail on test sittings**

  db.py LATER_COLUMNS gains:
  - ("sessions","flags","TEXT"): a JSON list of qids.
  - ("sessions","times","TEXT"): JSON {qid: ms}.
  - ("sessions","trail","TEXT"): JSON {qid: [answers in order, null for a clear]}.

  New POST /api/session/{sid}/flag {question_id, on}:
  - 409 once finished, 403 for another learner, 400 for an unknown qid.
  - One UPDATE with json_insert/json_remove, as set_answer does.
  - Returns {flags}.

  New POST /api/session/{sid}/time {times: {qid: ms}}:
  - Adds each value (capped at 600000 per qid per call) with json_set.
  - Unfinished sittings only; 403 for another learner.

  put_answer and clear_answer append to trail in the same statement, capped at 20 entries per qid.

  payload() adds "flags".

- **Tests file their time**: progress.record_paper(learner, session, questions, answers, times) passes times.get(qid) as ms, so attempts.ms is set and days() minutes include tests. finish() reads row['times']. Unanswered questions still file nothing.
- **Extend GET /api/session/{sid}/results**

  Read X-Learner and add mine: bool. Keep every existing field.

  Ownership:
  - A challenge whose day is still today anywhere (day >= daily.today(-840)) returns 403 {need: 'owner'} to anyone but its learner.
  - The 409 detail becomes {need: 'finish', kind}.

  Sitting-level fields added:
  - seq: the learner's ordinal for that kind, by finished, rowid.
  - label: the subtitle.
  - source (drills: cfg.source).
  - ms: the sum of times, else wall clock (module_started-started + finished-module_started), else drill result.ms.
  - timed.
  - summary {correct, incorrect, unanswered, answered, accuracy, accuracy_answered, ms, avg_ms, pace_ms: 95455, flagged, flagged_wrong, changed {total, wrong_to_right, right_to_wrong, wrong_to_wrong}}.
  - modules [{n, route, right, asked, ms, flagged}].
  - route_rule {cut: 0.6, lower_ceiling: 580, half_band: 70|100}.
  - domains for every kind (scoring.score on the marked questions). Each gains pct, share (BLUEPRINT), level (round(mastery*7)), and previous {right, asked}|null.
  - topics for every kind: [{topic, name, domain, right, asked, before, after, open}]. before is mastery_of the attempts with id below this session's first attempt; after is the current mastery.
  - by_difficulty and by_format [{key, right, asked, avg_ms}].
  - mistakes, grouped by (template, reason): each {label, kind: misconception|gridin|blank, topic, qids, open, owed, closed, hits_all_time}, read from traps now.
  - previous: the last scored same-kind sitting {id, seq, finished, estimate, right, asked}.
  - rank {ranked, attempt, pct|null, n}: first finished sitting per learner of the same kind, compared by estimate midpoint; pct is null when n < 20.
  - whatif {tier, count, estimate}: flip the easy misses (else the medium ones) to correct, then re-run scoring.score, plus section_score on the same route.
  - twins {n, right}: attempts from drills with cfg.parent == sid.
  - profile {target, exam_date}.
  - challenge {day, rank, players, average}.

  Each review item gains:
  - n (1-based within its module) and module (1|2|null).
  - status: correct|incorrect|blank|not_reached. A drill's served-but-unanswered final question is not_reached and left out of every count.
  - reasons (4 strings, '' at the key).
  - ref (template · seed).
  - ms (times[qid], or the drill attempt's ms).
  - flagged, saved (join saved on learner+template+seed), reported, repair (q.get('repair')).
  - changes (the trail).
  - trap {open, owed, closed, hits}|null.
  - history: the last 5 attempts on the same template from other sessions {at, session, kind, seq, correct, reason, ms}, in one query for all the sitting's templates.
  - accepted (grid-in only).
  - crowd for challenges: {right, n, options [4 shares]}, from first attempts grouped by (template, seed) across that day's challenge sessions.

- **scoring.accepted_forms(key)**: For a grid-in key with more decimal places than fit in the grid, return the 4-character truncated and rounded decimals that grid_equal accepts (2/3 → .6666, .6667). Otherwise []. Add an assert-based check in test_flow.
- **POST /api/drill: only / each / scope / twin**

  Drill gains:
  - only: list[str] | None (qids of from_session)
  - each: int = 1, range 1–5
  - scope: 'misses' | 'all' = 'misses'
  - still_open: bool = False

  With from_session:
  - pick = the questions with a 'key' where (qid in only) if only, else (scope=='all' or not correct).
  - still_open further drops misses whose trap has closed.
  - Nothing picked → 409 'nothing to practise'.
  - queue = the pick's templates, each repeated `each` times; count = len(queue).
  - timed and minutes pass through.

  source may be 'twin'. drill.create stores cfg.parent = from_session.

  history and in_progress skip source 'twin'. mine() still applies.

- **POST /api/mock/new {like}**

  NewMock gains like: str | None.
  - The source must be this learner's finished mock/module/diagnostic.
  - Module 1 = for each source module-1 question (in order), blueprint.draw_matching(builder, key, tier, fmt) on a fresh seed. Falls back to fresh_module's slot fill for a template that has run out.
  - For a mock, cfg.like = sid.
  - At routing, if the new route equals the source's, module 2 is drawn the same way from the source's module-2 templates. Otherwise it is fresh_module for that route.
  - Everything is remembered as seen, and it is scored as a normal section.

- **POST /api/saved accepts finished tests**: Allow kind mock/module/diagnostic/practice when row.finished, finding the question in marked_questions(row). Live sittings stay refused, as now.
- **Extend GET /api/history**

  Query params:
  - kind (csv)
  - open (bool)
  - limit (default 20, max 200)
  - offset
  - share (a read-only token)

  Order by finished DESC, rowid DESC, which fixes same-second ties. Twin drills are skipped.

  Each item adds:
  - seq, label, ms, pct, route
  - delta (midpoint vs the previous same kind)
  - modules [{n, right, asked, wrong: [n...], blank: [n...]}], computed by marking the page's sittings
  - open (traps opened in it and still open)
  - twins

  The response adds:
  - counts {all, tests, practice, challenge}
  - in_progress [{id, kind, seq, started, module, answered, total, seconds_left|null, expired}]: unfinished mocks and modules (untimed and expired included), and unfinished non-twin drills with at least one answer.

  The 'sessions' key is kept for Tests and Today.

- **New GET /api/stats**

  progress.stats(learner, tz) returns:
  - answered, right, accuracy, recent_accuracy (14 d)
  - minutes_total, minutes_week
  - tests {mock, module, diagnostic}
  - streak, best_streak
  - days14 (days().recent)
  - by_difficulty [{difficulty, right, answered, avg_ms}], by_format
  - traps {open, closed}
  - top_traps [{label, topic, template, hits, open, owed, last, closed}] (top 10 by hits)
  - latest, previous, best {estimate, id, kind, seq, finished}
  - estimate (progress.estimate)
  - domains_over_time [{id, seq, finished, domains [{domain, right, asked}]}] (last 5 scored)
  - profile {target, exam_date}

  It accepts ?share=.

- **progress.estimate(learner) (shared with Today and Tests)**

  Weighted mean of the lows and of the highs of the last 3 scored sittings within 60 days (mock 2, module 1, diagnostic 1). Returns {low, high, basis [ids], confidence {level: high|medium|low, reason}, trend {direction: up|down|steady, delta, since}}.
  - High: 2+ sections in 30 days.
  - Medium: 1 section or 2+ modules.
  - Low otherwise, or when the newest is over 30 days old.
  - Trend: newest midpoint vs the previous one, ±20 = steady.

- **New GET /api/skill/{topic}**: 404 for an unknown slug. Otherwise {topic, name, domain, mastery, answered, right, by_difficulty [{difficulty, right, answered, avg_ms}], recent (last 20 correct flags, oldest first), last, traps_open [{template, label, hits, owed}], traps_closed, sittings (last 5 sessions with attempts in the topic: {id, kind, seq, finished, right, asked})}. It accepts ?share=.
- **Report a problem (shared with the session and the exam runner)**

  A reports table (id, learner, session, qid, template, seed, given, title, category, details, files JSON, at).

  POST /api/report is multipart: session, question_id?, title (≤120), category (one of: key, two_right, label, figure, typo, explanation, bug, feature, other), details (≤2000), and up to 3 images (png/jpeg/webp, ≤5 MB each, magic bytes checked). Images are saved under server/reports/<id>/.

  Template, seed and given are read server-side. The response is {ok, id}. Rate limit: 20 per learner per day, 429 after that. The results review marks reported=true by joining on learner+session+qid.

- **Share progress**

  LATER_COLUMNS gains ("learners","share","TEXT").
  - POST /api/me/share {on} mints a token (secrets.token_urlsafe(16)) or clears it, and returns {token|null}.
  - /api/stats, /api/history, /api/map and /api/skill accept ?share=<token>: GET only, resolved to that learner, and read-only (no in_progress).
  - A bad token is 404.

- **README and test_flow**

  The serving-layer rows for /results/ and /results/report/ list the new endpoints and fields. test_flow asserts:
  - the new shapes
  - flag, time and trail round-trips
  - test minutes in days()
  - the drill only/each/scope/still_open/twin paths, and that twins are left out of history
  - mock/new like (same templates, new seeds)
  - rank on first vs retake
  - whatif ≥ actual
  - crowd %
  - the challenge 403 for others today
  - the 409 kind
  - the history tie-break
  - accepted_forms


### 3.5.6 Files this spec names, and who owns each

| file | owner |
|---|---|
| `web/results/report/index.html` | S6 |
| `web/results/index.html` | S6 |
| `web/assets/ui.js` | F2 |
| `web/assets/ui.css` | F1 |
| `web/test/test.js` | S5 |
| `web/practice/session/index.html` | S4 |
| `web/tests/index.html` | S5 |
| `web/practice/index.html` | S4 |
| `server/app.py` | F0 (routers register themselves, §2.10) |
| `server/db.py` | F4 |
| `server/progress.py` | F4 |
| `server/scoring.py` | F4 |
| `server/drill.py` | F5 → S4 |
| `server/blueprint.py` | F5 → S5 |
| `server/daily.py` | S3 |
| `server/test_flow.py` | shared: new checks go in server/checks/<task>.py |
| `README.md` | shared: each task edits its own subsection |

A file owned by another task is met through §2.9: the owner builds it, or this section's task adds its hook on its own page.

### 3.5.7 Shared needs

- UI.question review mode (ui.js): reveal(fb, {labels, reasons, boxes, hidden}). It keeps the session's .opt.ok (orange key) and .opt.no (struck pick) and adds: 'Correct answer' / 'Your answer' tags with ✓/✕; the misconception under every wrong option, open by default; Your answer / Correct answer boxes for every format, including 'Not answered'; 'Also accepted'; and a hide-answers mode. The practice session, the exam runner's review, Mistakes and the question of the day use the same component. → built in F3 question.js / runner.js
- UI.review player (ui.js): a full-screen dialog in the practice-session layout. It has the navigator strip or popover, labelled tools (Details, Hide answers, Save, Calculator, Reference, Report), the question column, bottom prev / position-within-filter / next, keys, the #q= hash, and the inline twin tile. Mistakes, Challenge and Today reuse it. → built in F3 question.js / runner.js
- Status cell + legend component with the practice session's semantics: correct = orange ✓, incorrect = graphite ✕, fixed since = outlined ✕ with an orange ✓ badge, unanswered = dashed –, not reached = dotted, flagged = bookmark, repair = ↻, current = ring. The exam navigator, Check Your Work and the session's progress segments add the same glyphs. No section flips the colours.
- Difficulty glyph (three bars + word), used by Practice, the session header, Tests and here.
- UI.tile stat tile (label, mono value, sub-line, count-up, clickable as a filter), used by Today, Me, Challenge and here. → built in F1 kit.js
- UI.gauge (200–800 arc: band, midpoint, target, previous ghost) and UI.scoreChart (bands, trend line, target line, estimate zone, tooltip, range/kind filters), reused by Today, Tests and Me. → built in F1 charts.js
- progress.estimate(learner): one estimate with confidence and trend for Today, the Tests page and Results, so the three never disagree.  
  ↳ R16: server/estimate.py (F4)
- Filter bar component: segmented radio with counts (disabled at 0), selects, Reset, URL-query state, and a phone 'Filters · n' bottom sheet. Practice's builder and Mistakes need the same.
- UI.sittingCard, with In progress rows, shared with the Tests page. → built in S6 results-ui.js  
  ↳ UI.sittingCard (S6 results-ui.js)
- Bottom sheet / right drawer component (Skill panel, phone filters, share sheet), also for the Practice map's skill detail.
- UI.reportDialog plus multipart POST /api/report (meta box, title, categories, details, 3 screenshots, 'Reported' tag), shared with the practice session and the exam runner. → built in F6 report.js  
  ↳ R17: UI.report (F6 report.js)
- Split button and ⋯ menu components (Fix these ⌄, the header overflow).
- Toast component ('Link copied', 'Report sent').
- Practice page accepts ?topics=slug,slug to preselect.
- Exam runner posts flags and per-question times, and the server keeps an answer trail (POST /api/session/{sid}/flag, /time), built with the exam-runner section.  
  ↳ R5: the flags table (F4), endpoints in S10
- Drill source 'twin' with cfg.parent: the practice session, Tests and Today must skip twin drills in their lists.  
  ↳ R10: the drill body, §2.6 (F5)
- Print stylesheet conventions in ui.css (@media print hides .bar, .tabs, buttons and dialogs).

### 3.5.8 Acceptance checks

1. curl -s -H 'X-Learner: a:v2revresults01' localhost:8000/api/session/3gGTd2b44bXqmkY-2Y4hRg/results | jq checks:
   - summary.correct + summary.incorrect + summary.unanswered == asked
   - modules | length == 2, and modules[0].asked == 22
   - every review item has n in 1..22, module in [1,2], status set and ref non-empty
   - every mcq item has reasons | length == 4, with '' at index 'ABCD'.indexOf(answer)
   - mine == true, and seq >= 1
2. The same curl with 'X-Learner: a:v2revsomeoneelse' returns mine == false and the same review. For today's challenge session 0_vHIyVpr8ubxI2bFAqj1A it returns 403 with detail.need == 'owner'.
3. Results for drill bcZjxCZ4bKZZNlcwnv8yAw:
   - domains and topics are non-empty
   - topics[].before and topics[].after are numbers
   - review[].ms is non-null for answered items
   - repair is true for repair questions
   - a drill ended with a question on screen has exactly one review item with status 'not_reached', and summary counts equal asked
4. Start a mock and POST /api/session/{sid}/flag {question_id: first, on: true}. GET /api/session/{sid} includes it in flags. After both modules, results.review for that qid has flagged == true and summary.flagged == 1.
5. Start a mock. POST answers B, then D, then clear, then D for one question. After finishing, its review item has changes == [1, 3, null, 3], and summary.changed.total >= 1.
6. Start a mock and POST /api/session/{sid}/time {times: {qid: 90000}} for several questions, then answer and finish. Attempts rows for that session have ms not null, and GET /api/me days.recent[-1].minutes > 0 for a learner who only sat that test.
7. POST /api/drill {from_session: <mock>, only: [<a correct qid>], scope: 'all'} returns total 1, and its served template equals the original's key with a different seed. {from_session, each: 2} returns total == 2 × misses. {only: ['nope']} returns 409.
8. POST /api/drill {from_session: <mock>, only: [qid], each: 5, source: 'twin'}, then answer one: GET /api/history does not list it, and the parent's results.twins.n == 1.
9. POST /api/mock/new {like: <finished mock>} returns a module 1 whose sorted template keys equal the source's module-1 keys, and every seed differs.
10. GET /api/history?kind=mock&limit=1:
   - returns 1 session with modules[].wrong and modules[].blank arrays
   - an unfinished expired mock shows in in_progress with expired == true
   - two sittings finished in the same second come back newest-inserted first
11. GET /api/stats has estimate.confidence.level in [high, medium, low], days14 of length 14 and domains_over_time. GET /api/skill/linear_functions has recent and sittings. GET /api/skill/bogus is 404.
12. rank.ranked is true on a learner's first mock and false on their second. rank.pct is null while n < 20.
13. For a mock with at least one easy miss, whatif.tier == 'easy' and whatif.estimate.high >= estimate.high.
14. GET results on an unfinished drill returns 409 with detail.kind == 'drill', and the report page redirects to /practice/session/?id=.
15. Browser 1280 on the report:
   - eight tiles whose numbers match summary
   - the legend is visible
   - clicking 'Incorrect' leaves exactly summary.incorrect cells at full opacity
   - the Module 2 select leaves only M2 cells
   - Mistakes refs such as 'M2 Q4' match the grid labels, and all 13 miss rows are in the DOM with no 'Show all' needed
   - cells carry ✓/✕/– glyphs
16. Browser player:
   - clicking a cell sets location.hash to '#q=m1-N'
   - ArrowRight moves within the filter
   - H hides the key, boxes, reasons and explanation, shows 'Answers hidden', and it stays hidden after ArrowRight
   - Esc closes and document.activeElement is the originating cell
   - report/?id=..#q=m2-4 opens at M2 Q4
   - every wrong option shows its misconception without any click
17. Browser: 'Try one like this' renders a second question in the player without navigation. Answering it shows a verdict, and GET /api/map shows one more answered in that topic.
18. Browser: the Report dialog shows the 'Sent with your report' box with the question ID. Sending with category 'key' returns ok, and the question then shows a 'Reported' tag.
19. Browser 390 on the report and the overview:
   - document.documentElement.scrollWidth <= 390
   - grid cells >= 44px
   - the filter chips wrap, with no element whose scrollWidth > clientWidth in the toolbar
   - the player's bottom bar is not covered by #tabs
20. Browser, a new learner (a:v2revempty02) on /results/:
   - no '—' in the estimate card
   - the 'Full section · 70 min' button is visible
   - the 14-day chart renders 14 baseline ticks
   - the sittings empty text shows with a Practise pill
21. Browser: /results/report/?id=nope shows 'That sitting does not exist.' with links to /results/ and /tests/, and no 'QUESTIONS' heading.
22. Browser: the practice session summary contains a link to /results/report/?id=<that set>.
23. Browser: the sittings card for a mock shows 'M1 ✕' chips whose count equals modules[0].asked - modules[0].right - blank count. Clicking a chip opens that question in the report.
24. Browser, page.emulate_media(media='print') on the report: .bar, .tabs and buttons are display:none, and the table of all questions is visible.
25. Challenge: after two learners sit a day's challenge and the day has passed, results.review[i].crowd.n == 2 and crowd.options sums to about 100. The player shows 'x% of 2 students got this right'.
26. POST /api/me/share {on: true} returns a token. /results/?share=<token> in a fresh browser renders the overview read-only, with no Fix or Resume buttons. After {on: false}, the same URL shows a 404 message.
27. PYTHONPATH=. python3 server/test_flow.py passes with the new assertions.

### 3.5.9 This section's open questions

Folded into Part 5 where they need a decision; kept here for context.

- Total score: we are Math only. Should the hero show only the Math 200–800 gauge (the default here), or accept a self-reported R&W score to show an estimated /1600 total like theirs?
- National percentile: College Board publishes user percentiles for Math section scores. Should we add that table (with a cited source and year) next to our in-site percentile, or keep in-site only (the default) until it is sourced?
- Colour semantics: this spec keeps the practice session's meaning (orange = right, graphite = wrong) and adds glyphs everywhere. If misses should be the orange ones instead, the flip has to happen in the session, the exam runner and here together. Confirm the default.
- Share by link: reports stay readable by anyone with the sitting id (mine=false hides every action), except live challenges. Keep that, or require an explicit per-report share token?
- Report screenshots: store up to 3 images per report on disk (the default), or text-only reports, since template and seed already reproduce the question exactly?
- Share-progress link for a tutor or parent: build it with this section (the default), or defer it to Me?

---

## 3.6 Study plan

> **Spec title:** Study plan (/plan/): landing, four-step wizard, plan view in three tabs (Plan, Progress, Plans) with a task list you can change for each day, plus how Today, the practice session, the test report, Me and the diagnostic connect to it  
> **Built by:** S7  
> **Read with resolutions:** R9, R10, R11, R13, R14, R15, R16, R18 (§2.2). Where this spec disagrees with them, they win.

### 3.6.1 What they have

- **Landing hero**: Blue hero with decorative circles, a 'Personalized for you' pill, H1 'Your path to the score you want', and a line promising a week-by-week plan built from target, exam date and available time, with every task linking into practice. White CTA 'Create my plan', with 'Takes about a minute · 1 plan left this cycle' under it.
- **Landing stat cards**: Three cards: 10 Practice tests (full-length, scored like the real one), 6,933 Question bank (8 domains), 1,002 Vocabulary words (flashcards, quizzes, spaced review).
- **How it works**: Three numbered cards. 1 Answer four questions: target, date, hours; 'we fill in what we already know from your results'. 2 We build the plan: every study day gets its own tasks, weighted toward the domains costing the most points. 3 Work it day by day: each task opens a question set, a practice exam or the vocab deck.
- **Your study plans list on the landing**: A list of built plans. Empty state: 'You have not built a plan yet', with a line saying plans collect here so you can switch between them when your exam date or target changes.
- **Plan quota**: Capped per billing cycle ('1 plan left this cycle'). Subscription and Profile show an 'AI Study Plan Generations 0/1' meter. Failed plans are hidden and the landing still says 1 left.
- **Dashboard plan CTA (no plan)**: 'Build Your Adaptive DSAT Study Plan' with three bullets (custom daily time pacing, dynamic score drift adjustments, scheduled rest days) and 'Build My Plan ->'.
- **Wizard header**: 'Create your study plan', a subtitle saying the draft saves as you go, and an 'Exit setup' pill that is always visible.
- **Wizard stepper**: Four step cards (Where you are / Where you're going / Time you have / What to focus on). The number circle becomes a check when done; the active step has a blue border and tinted fill. Clicking a done step jumps back. You cannot jump forward. Step titles use Bricolage Grotesque 30/700 with a one-line subtitle each.
- **Draft autosave**: 'Save and continue' on every step saves the draft, and leaving and returning resumes it. After a failed build, Try again resets the draft: the exam date goes back to the profile date and the time back to 1h.
- **Step 1 Where you are**: Grey note 'Start with your best estimate. You can rebuild the plan after taking a full practice test.' R&W and Math sliders 200-800 with a value bubble, and an 'Overall score' sum. Prefilled from /exam-sessions/results/overview and /qbank/stats: measured scores are used only when tests exist and both sections are above 200.
- **Step 2 Where you're going**: R&W and Math target sliders 500-800 whose minimum is the current score. A NOW -> TARGET card: NOW 1000, '+400 points' pill, TARGET 1400, a 400 min / 1000 avg / 1600 max range bar with two markers, and per-section rows '500 -> 700 (+200)'. A hidden screen-reader sentence ('Starting score 1000, target score 1400, projected gain 400 points'). The exam date is a free calendar popover (any date), prefilled from the profile. The pace line updates live ('7 weeks to prepare · about 60 points per week') and never says whether that is realistic.
- **Step 3 Time you have**: Subtitle about a plan you can keep beating an ambitious one. Daily chips 30m/1h/1.5h/2h/2.5h/3h/4h (30-240 min). A 'Study days per week' slider with '5 days · 5h a week'. Mon-Sun tiles labelled STUDY (green) or REST (orange), kept in sync with the slider, plus 'Study days: 5 days / Rest days: 2 days'. A 'Solve a practice exam every day' toggle, locked below 150 min with 'a full practice test runs 134 minutes'. The at-a-glance summary rounds up (1.5h x 5 shows as '8 hours across 5 days').
- **Step 4 What to focus on**: Bar 'Set how much of your week each area should take' with '0/4 focus' (blue) and '0 strong' (green) badges. Groups READING & WRITING and MATH, each with its own 'N focus · N strong' count. Eight domain rows with a Focus (arrow-up) / Normal (dash) / Strong (check) segmented control. At most 4 on Focus: the other Focus buttons grey out and a visible helper reads '4 focus areas is the maximum. Move one back to Normal to pick a different one.' Focus rows are tinted blue and Strong rows green. Toggle 'Include vocabulary practice'. 'Your plan at a glance': current, target, exam date with weekday, weekly study time. Back / 'Create my study plan', disabled until something is on Focus.
- **Build screen**: 'Building your study plan' / 'This usually takes about a minute. You can leave this page and come back — it keeps building.' A % bar and 5 checklist steps with sub-lines (reading scores, mapping weeks and days off, choosing daily work weighted to weak areas, balancing daily time, almost there). The progress is fake: the server marks the plan FAILED in 0.3 s and the screen keeps playing. In the walk, 3 of 3 builds failed.
- **Error card**: 'We could not build your plan' / 'Nothing was charged against your plan allowance. Try again, and if it keeps failing, give it a few minutes...' with [Try again], which returns to step 1 with the draft reset.
- **Plan data model**: status BUILDING|ACTIVE|COMPLETED|REPLACED|FAILED, version, current/target per section, examDate, dailyStudyTime, weeklyStudyDays, weakAreas[], strengths[], vocabularyPreference, dailyPracticeExam, offDays[], totalTasks, completedTasks, and weeks[{weekNumber, theme, days[{date, isOffDay, tasks[{type, title, duration, domain, aiReason, completed, skipped, order}]}]}].
- **Plan endpoints**: generate, latest, list, get, activate, delete, createTask, updateTask, removeTask, moveTask (PUT tasks/move), completeTask {performance}, skipTask, startTask, progress, analytics, regenerate, adapt.
- **Plan page tabs**: Plan | Progress | History.
- **Four stat tiles**: Days to exam (hint 'Keep the streak going' or 'Exam day has arrived'); Streak (hint 'Longest N days'); Plan complete % (hint 'X of Y tasks'); Score gap (hint '1000 now, 1400 target').
- **Today card**: 'Today' chip with the date; 'N of M done · X min left · Y min planned'. Empty states: 'Rest day' / 'You marked this as a day off. Rest is part of the plan.' and 'No tasks scheduled' / 'Nothing is scheduled for today. Check the week below to work ahead.'
- **Task card**: Title; type badge (Practice test / Question set / Vocabulary / Reading / Practice game / Flashcards / Custom); 'N min'; domain; destination (Practice exam / Question bank / Vocab quiz / Vocabulary / Flashcards / On your own). A 'Skipped' outline badge. 'Why this task?' expands the AI-written aiReason; the label flips to 'Hide AI rationale'.
- **Task actions**: Open task: [Skip] (ghost), [Mark done] (outline), and a primary launch button per type (Start test / Start questions / Study words / Start reading / Play / Review cards). CUSTOM tasks get only [Mark done], with 'Work through this one on your own, then mark it done.' A done task shows a '✓ Done' badge, [Practice again] and [Undo]. Custom tasks can be created, updated and removed (API).
- **Week view**: 'Week N', 'X of Y tasks · Z%', the week's theme sentence and a progress bar. A pager ‹ '3 / 7' › and a [This week] jump when you are on another week. Seven day tiles: weekday, date, and 'done/total', 'rest' or '—'. Today has a top accent bar; the selected day is filled.
- **Selected day**: Header 'Today, Wednesday, September 23'. Empty day: 'Nothing scheduled' / 'No tasks on this day. Pick another day above, or move one here.'
- **Task rows in the week**: A checkbox ('Mark as done' / 'Mark as not done'), the aiReason inline, a ⋯ menu ('More actions for {title}') with 'Move to' and the later days of the same week, or 'No later day this week'. A launch button that becomes [Redo] once done. Skipped rows at 55% opacity. Rescheduling only moves a task to a later day in the same week.
- **Behind banner**: Shown when there were at least 4 tasks in the last 7 days and under 60% got done. 'You have fallen behind this week' / 'N tasks done over the last 7 days. We can rebuild the weeks ahead around the time you actually have — finished work stays untouched.' [Rebalance my plan]. Toast: 'Your remaining weeks have been rebalanced'.
- **Score drift banner**: Shown when measured R&W + Math beats the plan's starting score by at least 60, upward only. 'Your practice scores are up N points', or 'You have hit your target score'. 'This plan was built around X, but your recent tests average Y. Rebuilding uses your real scores…' [Not now] (snoozes 3h in localStorage) / [Rebuild with these scores].
- **Progress tab**: 'Accuracy by domain': horizontal bars, 'Weakest first. This is where your remaining time pays off most.', with an RW/MATH legend. 'Study time per day': hours logged across N days, Studied vs Planned. 'How your plan splits your time': planned minutes by task type across the whole plan. Empty state 'Nothing logged yet'.
- **History tab**: 'Your plans' / 'Every plan you have built. Open any of them to look around, or switch your active plan without losing the others.' Rows: status badge, Built / Exam / Days left / Tasks, 'you are here', [Open] / [Make active]. Older-plan banner: 'You are viewing an older plan', '… · not your active plan', [Back to active plan] / [Make this my plan]. Footer: 'Need a different plan? … This plan stays available under History.' [New plan].
- **Toasts**: Task skipped / added / updated / removed, 'Your remaining weeks have been rebalanced', 'Switched to this plan', 'Study plan archived', 'Could not start task. Please try again.'
- **Dashboard card with a plan**: 'Today's Plan' with an 'All Done 🎉' badge when finished; 'N of M completed'; 'X min left (Y min total)' or 'All time targets reached'; a [Full Plan →] button; checkbox rows ('Mark task as done').
- **Profile study goals**: Target score with a bar, an exam date countdown bar ('10 days remaining'), Daily goal 2 Hours, Weekly goal 12 Hours, Preferred time Evening. Nothing uses the preferred time.
- **Dashboard countdown, target and study time**: An exam-date pill select of official dates (it still lists past dates) above a live DD:HH:MM:SS countdown. 'Set Target Score' modal (400-1600, number input, bar), not synced with the wizard target (the dashboard shows 0 after the wizard set 1400). 'Study time today / this month' with a month calendar that marks days in UTC.

### 3.6.2 What we have now

Status is have / partial / missing / worse, against theirs.

- **Landing hero and create CTA**: *missing.* /plan/ opens straight into the wizard when there is no plan. Nothing says what a plan does or offers a way in.
- **Stat cards**: *missing.* Nothing shows what backs the plan (19 skills, 386 question types, tests and questions without limit).
- **How it works**: *missing.* Nothing explains what the plan will do each day.
- **Your plans list and switching**: *missing.* There is one plan, stored as columns on learners. Change wipes it. No history, no switching, no duplicate.
- **Draft autosave**: *partial.* The draft lives in sessionStorage for one tab ('plan-draft'). It is lost when the tab closes, does not follow the learner code, and nothing offers to continue it.
- **Exit setup**: *missing.* You can only leave through the nav. The Change button clears the draft.
- **Stepper**: *have.* Four steps, all clickable, even forward with nothing checked. Done steps show a filled number; the active step is outlined in orange. At 390px the labels are hidden and only numbers show.
- **Step 1 score slider**: *partial.* Math only, 200-800, a big number, and a line with the latest test band. With no history it links to the diagnostic, which does not come back to the plan. No number field, no R&W or total, no note that the plan can be updated after a test.
- **Step 2 target + gain**: *partial.* Big 500 -> 600 with a +100 pill; the slider paints current-to-target orange. No range bar with an average marker, no feasibility check, no note on what the target takes.
- **Step 2 exam date**: *have.* Chips for the published 2026-27 dates plus a date input; the pace reads 'N days · about X points a week'. The chips do not show each date's pace.
- **Step 3 daily time**: *partial.* Chips 15m, 30m, 45m, 1h, 1.5h, 2h, 3h, 4h. 2.5h (theirs) is missing, and every day gets the same minutes.
- **Step 3 days slider + weekday tiles**: *worse.* Slider and tiles stay in sync, but the tiles are single letters (T/T and S/S look alike) with no STUDY/REST label and no study/rest count.
- **Step 3 practice tests**: *have.* 'Each week' or 'Every study day', sized by the minutes (a module at 35 min or more, a section at 70 or more), with 'every day' disabled below 35. No twice a week, no choice of test day, no size override.
- **Step 4 focus per domain**: *partial.* Four domains with Focus / Normal / Strong, at most 2 on Focus, a mastery bar and an answered count, preset from results. At the cap, Focus is disabled with no visible reason. No row tint, no icons, no skill-level focus.
- **Focus actually changing time**: *worse.* progress.coach only adds 40 to a topic's rank. The plan cycles coach.ahead, which deals all 19 topics once per cycle, so a Focus domain comes earlier but gets no more days.
- **Include vocabulary / extras toggle**: *missing.* No equivalent, such as the question of the day, the challenge or rechecks in the plan, or R&W study of your own.
- **Plan at a glance**: *partial.* Step 4 only: score, exam, pace, study, tests, focus, strong. No totals to the exam and no split.
- **Build reliability**: *have.* Saving is one synchronous PUT /api/me, so there is nothing to fail in the background. Keep it synchronous.
- **Plan page tabs**: *missing.* One page: a countdown, one day card and a calendar.
- **Stat tiles**: *partial.* Only the countdown (a big number with the date, gain and rhythm). No plan-complete %, no streak with longest, no score gap tile.
- **Plan view daily tasks**: *partial.* One day card: a single coach set, or a test plus leftover practice. No task list, no per-task status, no record of what was done, no resume of a started set.
- **Why this task**: *missing.* No reason is shown for any day's topics, although the coach knows them (open mistakes, mastery, days since last worked).
- **Skip / mark done / undo / practice again**: *missing.* No per-task actions besides Start.
- **Custom tasks**: *missing.* You cannot add your own task, such as R&W study, so the plan cannot hold the half of the SAT we do not teach.
- **Move a task / take a day off / shorter day**: *missing.* No rescheduling of any kind after the wizard.
- **Week view**: *missing.* No week header, week progress or pager. The calendar is the only multi-day view.
- **Week-by-week structure**: *missing.* A flat calendar: no phases, no difficulty change over time, no timed practice near the exam.
- **Calendar**: *partial.* Monday-first, with markers for practice (circle), test (rectangle) and SAT (orange). It stops at 16 weeks (count < 16*7), so a later exam never shows. No month navigation. 'Done' means any answer that day, not the planned task.
- **Adherence / progress stats**: *missing.* No days done vs planned, minutes vs plan, or mistakes closed since the plan began.
- **Study time per day chart**: *missing.* Nothing compares studied with planned per day.
- **Plan split by task type**: *missing.* Nothing shows how the plan spends its minutes.
- **Accuracy by domain, weakest first**: *missing.* The plan page shows no accuracy at all.
- **Behind banner / rebalance**: *missing.* The plan redraws from today, so nothing piles up, but nothing tells a student the plan is bigger than the time they really have.
- **Score drift adjustment**: *partial.* The coach re-reads results daily, but a new test never offers to update the starting score or the target.
- **Score trajectory**: *missing.* No chart of where you are against where you should be by now.
- **Missed days**: *partial.* Nothing piles up, but a missed day is not shown and cannot be made up.
- **Streak**: *worse.* progress.days counts consecutive days with any answer, so a plan with weekend rest days breaks the streak every Saturday.
- **Study time**: *worse.* Test answers are filed with ms=None (record_paper), so time spent on a test counts as 0 minutes in progress.days.
- **Today's plan card on the dashboard**: *partial.* Today leads with the plan's test on a test day (UI.plan.dayOf) or else the coach set. No task counts, no minutes left, no done state.
- **Preferred time / reminders**: *missing.* No preferred time, no calendar export, no reminders.
- **Post-exam state**: *missing.* Once the exam date passes, the page silently opens the wizard. No way to log the real score and no summary.
- **Target / exam date as one value**: *partial.* Plan and Today read the same learners columns, so they agree. Me has no goals card yet.
- **Quota**: *have.* Free and unlimited. Keep it that way.

### 3.6.3 Design

##### Review changes

What the first spec got wrong, fixed below. The worst gap was its "theirs" list. It still said their plan view was "claimed, not seen", although the live walk recovered the whole plan view from their bundle. So their tabs, task actions, custom tasks, rescheduling, banners, Progress charts and History details were missing from the spec.

**A. Theirs, left out or covered by something weaker**
1. Added **page tabs** `Plan · Progress · Plans` (theirs: Plan | Progress | History). Before, ten blocks sat in one long scroll, which was worst on a phone.
2. The stat row was **3 tiles and is now 4**. Added **Plan done %** (theirs: 'Plan complete % · X of Y tasks'), and moved the **streak with its longest** into the week tile (theirs: 'Streak · Longest N days'). The first spec had no plan-complete figure and put the streak only in a side card, without the longest.
3. The **day progress line** now reads `2 of 4 tasks · 33 min left · 45 planned` (theirs: 'N of M done · X min left · Y min planned'). It used to show minutes only.
4. **Per-task actions** were missing. Added Skip, Undo, Mark done / Mark not done, and Again · new questions (theirs: Practice again). Skipped rows sit at 55% opacity with a `Skipped` tag.
5. **Custom tasks** were missing: theirs has CUSTOM with Mark done, plus create, update and remove. Added `Add a task`, with a title, minutes, a day or a repeat rule (every study day / weekly) and a checkbox. This is also how R&W study gets into the plan.
6. **Rescheduling** was missing. Theirs only moves a task to a later day in the same week. Ours moves any task to any day up to the eve, swaps a focus set's topics, takes a day off, shortens or lengthens a single day, and has Reset this day.
7. **'Why this task?'** was missing. Theirs is AI prose. Ours lists the facts the scheduler used: open mistakes by name, accuracy, days since last worked, focus state, and a timing or grid-in gap.
8. A **week header** was missing. Added `Week 3 of 7`, `8 of 12 tasks · 67%`, a bar, a server-written **week theme** line, and `done/total` in every day column.
9. Added a **Behind banner** (theirs: fallen behind + Rebalance). Ours shows the minutes you actually study and offers one tap to fit the plan to them, with its effect on totals and pace shown before you apply it.
10. **Drift** now also has the 'You hit your target' variant, which offers to raise the target. It averages recent tests instead of trusting one sitting, and works in both directions.
11. Added the **Progress tab** charts that were missing: **Study time per day, studied vs planned**, **How the plan splits your time** (by task type) and **Accuracy by domain, weakest first**.
12. The **Plans tab** now has Built date, days left, tasks done, `You are here`, `New plan`, and an older-plan banner with both `Back to active plan` and `Make this my plan`.
13. Added the missing **toasts**, each with Undo where an undo exists.
14. The **Today card** now matches their dashboard card: counts, minutes left, a done state, a `Full plan` link, and checkboxes for your own tasks.
15. **Step 4**: at the cap, a **visible helper line** replaces the `title` tooltip, which touch users never see. Focus and Strong rows are **tinted**.

**B. Not clearly better, redesigned**
- The **weekday tiles now carry each day's minutes as a visible select**, replacing the hidden 'Different time on some days' disclosure. **Days off** is a visible section with an empty state instead of a disclosure.
- The **R&W score** is a visible optional field, not a switch that is off by default. It is tied to custom R&W tasks.
- The **landing** gets an **Example day** built from the student's own data, so they see what a day holds before committing. Stat tile 3 shows a **real named mistake from the bank** instead of a bare '4'.
- Added a **Coming up** list: the next study days with their topics, the next test and the next phase change.
- The **skills list** (all 19, accuracy since the plan began) opens in place on the Progress tab, instead of only linking away.

**C. Minimalism creeping back, removed**
- Calendar minutes are **no longer hidden on phones**; they show at 9.5px mono.
- Mastery stays a bar (a deliberate honesty rule in progress.py), but **accuracy % and answered counts are printed** next to it.
- WeekMeter day dots now carry **weekday letters**.
- Each chart has a **visually hidden data table**.

**D. Could not work as described, fixed**
- **Target note**: '700 ≈ 39 of 44 right' was wrong, because scoring is difficulty-weighted. It now reads 'about 88% of the section's points (hard 3, medium 2, easy 1)'. `ANCHORS` top out at 780, so a target of 790 or 800 can never be 'hit' by a sitting's midpoint. Pace, drift and 'target hit' now cap the target at 780, and the note says so.
- **Band caption**: 'Bands are ±70' is only true for tests (`MOCK_HALF_BAND`). The diagnostic is ±100 (`HALF_BAND`). The caption now states both.
- **Pace status and drift** were computed from one sitting with a ±20 or ±30 window, which is inside a ±70 band, so the status would flip on noise. Both now use the mean of up to 3 recent sittings. On pace is ±35; drift needs 40 or more.
- **Task done**: a drill is only `finished` when /finish is called, so a student who answers the whole count and leaves would show 'active' forever. A task is now done when any of these holds:
  - the session finished;
  - it answered its planned count;
  - it was marked done;
  - (tests only) any module or section finished that day;
  - (focus only) that day's answers on its topics from any source reached the count.
- **Allocation**: Advanced Math has only 3 topics. The rule 'not used on the previous 2 practice days' plus 'up to 2 slots per domain' can therefore be impossible, so a fallback is specified.
- **Overrides**: Swap, move, skip and a changed day length must survive the daily re-deal. They are now stored in new tables `plan_overrides`, `plan_marks` and `plan_tasks`.
- **Time zones**: progress.coach uses the UTC date, but the plan must use the learner's local date. X-Tz is required on every plan endpoint, and the tz is stored at creation.
- **Streak**: the current rule breaks on every rest day. The plan streak skips rest days and days off, and the shell flame uses the same rule, so pages never disagree (their profile and QOTD streaks do).
- **Study time**: test minutes are added only when a session's answers carry no ms, so they are never counted twice once the runner sends per-question times (a Report-section need).
- **PUT /api/me**: it only accepts weekly or daily for `tests`. It is widened to the new values.
- **.ics**: one server-side builder replaces a client `UI.ics`, and the same builder serves a revocable subscription feed. The feed uses a random token, never the learner code.
- **Diagnostic return**: the diagnostic runs in /test/, so the return path is carried in sessionStorage and only `/plan/` paths are accepted. The report page shows `Back to your plan`.
- **Removed**: 'widen drill source to 40'. The tag lives in its own `task` field.
- **Open questions resolved**:
  - R&W: a visible optional field.
  - Focus caps: 2 domains, 6 skills.
  - Edit in place, with 'Save as new plan' beside it.
  - Logging study done elsewhere: custom tasks and Mark done.

**E. Extras added**
- The Behind banner fitted to the minutes you actually study.
- A format gap (grid-in vs multiple choice) and a pace gap (seconds per question), each read from attempts, which tilt focus sets and turn the clock on early.
- A revocable calendar feed and a revocable read-only link for a tutor or parent (their hidden Classes feature has no student-side sharing).
- An Example day on the landing.
- Rechecks passed in the Progress card.
- `Make it a section` on a test task when the day has time.
- Repeating custom tasks.

---

#### Study plan: rebuild spec

The section is one route, `/plan/`: `web/plan/index.html` holds the markup and CSS, and a new `web/plan/plan.js` holds the logic (the same split as `web/test/`). All plan arithmetic lives in `server/plan.py`, so the page, Today, the session summary and the report show the same numbers. `UI.plan.dayOf` and `testOf` are deleted from `ui.js`.

The mode lives in the URL. Changing mode or tab uses `pushState`; picking a day uses `replaceState`.

| URL | shows |
|---|---|
| `/plan/` | Plan view, Plan tab, when a plan is active; otherwise the Landing |
| `/plan/?tab=progress` · `?tab=plans` | Plan view on that tab |
| `/plan/?day=YYYY-MM-DD` | Plan tab with that day selected |
| `/plan/?setup=1&step=1..4` | Wizard for a new plan (server draft first) |
| `/plan/?edit=<id>&step=1..4` | Wizard editing that plan |
| `/plan/?id=<id>` | an archived plan, read-only |
| `/plan/?view=<token>` | a shared read-only plan, with no learner code needed |

**Copy rule.** Labels, units, counts, legends and one line of helper text that helps a student decide are all in. Only lines that narrate the interface are out.

**Visual rules.** Numbers use DM Mono. Orange marks what is yours or live: the selected option, the active step, today's next task, the target and the exam day. Status is never shown by colour alone; it always has a shape and text as well.

---

##### 1. Landing (no active plan)

Max width 1120px, on a 12-column grid.

**1a. Hero** (`PlanHero`)
- Full-width `--wash` card, radius 18px, 36px padding, two columns 1.4fr / 1fr.
- Left column:
  - Kicker: `STUDY PLAN`.
  - H1 (44/800): **A plan to your score, one day at a time**.
  - Line (16px, `--soft`): *Mistakes first, then your focus skills, and a fresh test each week, up to exam day. Skip, move or add anything; miss a day and it redraws from today.*
  - Pill `Create my plan`, which opens `?setup=1&step=1`.
  - Under the pill, mono 12px: `About a minute · free · as many plans as you like`.
- Right column, **HeroPreview**: three stacked mini tiles built from the student's own data.
  - `Math now`: the latest band, e.g. `590–730`, or `—` with the link `Take a test`.
  - `Next SAT`: e.g. `Oct 3 · 10 days`.
  - `Open mistakes`: the count, with an orange dot.
- **DraftBanner** (shown when a server draft exists):
  - A paper tile inside the hero reading `Draft · step 3 of 4 · Nov 7 · 560 → 700`.
  - Pill `Continue`.
  - Quiet `Discard`, confirmed in place: `Discard draft?` then `Discard` / `Keep`.
  - While a draft exists, the hero pill reads `Start over`.

**1b. BankStats**: three `--tile` tiles, each a big DM Mono 40 number with a label and one line. The data comes from `GET /api/plan` → `bank`.
1. `∞` **Practice sections**: *A new adaptive section every sitting, built to the published blueprint.*
2. `386` **Question types · 19 skills**: *Every question new to you. None repeat.*
3. **Every wrong answer is named**:
   - Shows a real example from the bank, `bank.example`, e.g. `“Distributed the minus to the first term only”`, with its skill chip.
   - Line: *The next question is the same trap with new numbers.*

**1c. HowItWorks**: three numbered tiles, the number in a 28px circle.
1. **Four questions**: *Your score, your target and date, your time, your focus. Filled in from your results where there are any.*
2. **Every day planned**: *Open mistakes first, then focus skills, a test on your test day. Harder and timed as the exam gets close.*
3. **It keeps up**: *Skip, move or add tasks; take a day off; a new test offers to move your starting score.*

**1d. ExampleDay**
- A tile titled `A day in your plan`.
- It renders `sample_day` from `POST /api/plan/preview`, called with defaults from the profile and results, using the same `UI.taskRow` as the real plan but read-only. Example rows:
  - `Fix mistakes · 8 questions · 13 min`
  - `Focus set · Circles, Percentages, Nonlinear functions · 20 questions · 32 min`
  - `Question of the day`
- A new student sees the blueprint-weighted focus set only.

**1e. PlansList**: the same component as the Plans tab (section 3k).
- With no plans, a dashed empty tile: *No plans yet. Plans you make stay here, so you can switch when your date or target changes.*

**At 390px**
- The hero becomes one column, with the preview as a 3-up row of small tiles under the pill.
- Stats, how-it-works and the example day stack one per row.
- 16px gutters.

---

##### 2. Wizard

###### 2a. Shell
- **Top row**:
  - H1 `Create your plan`, or `Edit plan · <name>`.
  - A line in `--soft`: *Your draft saves as you go.*
  - Right-aligned quiet `Exit`: goes back where you came from and keeps the draft.
- **Stepper**:
  - Four buttons, each a number circle plus the step name.
  - Done step: a filled ink circle with a check.
  - Active step: an orange inset outline on `--wash`, with `aria-current="step"`.
  - Future step: a grey outline. It becomes clickable once every step before it is valid (step 2 needs a date). This beats theirs, which never jumps forward.
  - A step holding a server error gets a red dot.
  - At 390: numbers only in the row, then a full-width line `Step 2 of 4 · Where you're going`.
- **Body**:
  - At 1280: two columns, the step at min(660px, 1fr) and a sticky `GlancePanel` of 320px (`top: 88px`).
  - At 390: the Glance becomes a bar above the footer, e.g. `560 → 700 · Nov 7 · 3h 45m/wk ⌃`. Tapping it opens a bottom sheet.
- **Footer**, sticky:
  - Quiet `Back`.
  - Mono `2 / 4`.
  - Pill `Next`. On step 4 it reads `Create plan`, or `Save changes` with a quiet `Save as new plan` when editing.
  - Tapping a disabled Next focuses the first invalid field and shows its reason under it.
  - Enter advances when focus is not in a text field.
- **Draft**:
  - Every change sends `PUT /api/plan/draft {step, fields}`, debounced 600ms.
  - It is mirrored to localStorage (try/catch) as a fallback for when the server is unreachable.
  - Boot order: server draft, then local fallback, then defaults from profile and results.
  - A failed create **never resets the draft**. Theirs resets it.
- **GlancePanel**: recomputed by `POST /api/plan/preview`, debounced 250ms. Stale rows dim to 60% while the call is in flight. Rows:
  - `Score 560 → 700 · +140`, plus `Total 1060 → 1400` when R&W is filled in
  - `Exam Sat, Nov 7 · 45 days`, plus a `not booked` tag when that box is ticked
  - `Pace 22 points a week` with its PaceTag
  - `Study 5 days · 3h 45m a week`, using the true total from per-day minutes
  - `To the exam 31 study days · 23 h · about 870 new questions`
  - `Tests 6 modules · Fridays`
  - `Phases Build to Oct 14 · Sharpen to Oct 28 · Final`
  - `Focus` and `Strong`: domain and skill names, or `—`
  - `Your own R&W 30 min × 5 a week`
  - `SplitBar`
  - `Extras Rechecks · Question of the day`

###### 2b. Step 1: Where you are
- H2 **Where you are**. Subline: *Start from your real number, so the plan is built for the gap you have.*
- **SourceNote** (a `--tile` row) has four variants:
  - **Two or more sittings in the last 45 days**: `Your last 2 tests average 650 · Sep 14, Sep 21`, with the quiet button `Use 650`.
  - **One sitting**: `Latest · Module · Sep 21 · 590–730`, with `Use 660` (the midpoint, rounded to 10).
  - **Practice only**: `No test yet · 142 practice answers`, with the link `Take a module (35 min)`.
  - **New student**: `Don't know? Take the diagnostic (20 questions, about 30 min)`.
    - This link sets sessionStorage `satf.return = '/plan/?setup=1&step=1'` before opening `/diagnostic/`.
    - The diagnostic's report shows `Back to your plan` when that key holds a `/plan/` path. Any other value is ignored.
  - Every variant ends with the line: *You can update this after any test; the plan will offer it.*
- **ScoreSlider** `Math`:
  - Range 200–800, step 10.
  - A DM Mono 72 value, with a bubble following the thumb.
  - A number field beside it (`inputmode=numeric`, snaps to 10 on blur).
- **RangeBar**: a 200–800 track with the ticks `200`, `avg 505` (`MATH_MEAN`, see open questions) and `800`, and an ink dot at the current value.
- **Reading & Writing** row, always visible:
  - Label `Reading & Writing · optional, for your total`.
  - A number field, 200–800, left empty.
  - When filled, it shows `Total 1060` and the note *The plan schedules Math. Add R&W study as your own task in step 4.*

###### 2c. Step 2: Where you're going
- H2 **Where you're going**. Subline: *Your target and date set the pace for every week.*
- **Target ScoreSlider** `Math target`, from the current score to 800, with a number field.
  - Quick chips: `+50 +100 +150 +200 700 750 800`. A chip below the current score is disabled.
  - With R&W filled in, an optional `R&W target` number field appears.
- **GainCard** (`--wash` tile):
  - `NOW 560`, a pill `+140`, and `TARGET 700` in orange.
  - A 200–800 track with the now marker (ink), the target marker (orange), the span between them painted orange, and the avg tick.
  - With R&W filled in, rows `R&W 500 → 650 (+150)` and `Total 1060 → 1350 (+290)` on a 400–1600 track.
  - A sentence in `aria-live=polite`: *From 560 to 700, 140 points.*
- **TargetNote** (mono 12.5, `--soft`), computed by the server from `scoring.py`:
  - Target above 580: *Above 580 needs the harder second module: 14 of 22 right in module 1 routes you up.*
  - Always: *700 is the middle of a test's band when you earn about 88% of the section's points (hard questions count 3, medium 2, easy 1).*
  - Target above 780: *A perfect section reads 710–800 here; the plan counts 780 as reaching your target.*
- **DateChips**:
  - One chip per published date after today (`plan.SAT_DATES`, on the server).
  - Two lines per chip: `Oct 3`, and in mono `10 d · 98/wk`. The selected chip is orange.
  - A last chip `Other date` opens a date input, from tomorrow to today + 730.
- Checkbox **`Not booked yet`**. When ticked, the date shows `not booked` everywhere and the Plan view shows a reminder banner.
- **PaceLine**: `45 days · 31 study days · about 22 points a week`, with a **PaceTag**:
  - `Steady` up to 15 a week, `Ambitious` for 15–30, `Very ambitious` above 30 (server constants, see open questions).
  - For `Very ambitious`, a line suggests a later date: *Nov 7 brings it to 22 a week.* The date is a button that selects that chip.
- **Invalid states**:
  - No date: `Pick a date`.
  - Today or earlier: `Pick a date after today`.

###### 2d. Step 3: Time you have
- H2 **Time you have**. Subline: *A plan you keep beats one you drop.*
- **MinutesChips** `A study day`: `15m 30m 45m 1h 1.5h 2h 2.5h 3h 4h`.
- **DaysSlider** `Days a week`, 1–7:
  - Readout `5 days · 3h 45m a week`, the true total including per-day minutes.
  - The slider adds days from Monday and removes them from Sunday back.
- **WeekdayTiles**: seven tiles, Mon–Sun, with 3-letter names. Each tile is 72px wide at desktop.
  - Top half: the name, plus `STUDY` (ink on `--wash`) or `REST` (`--soft` on `--tile`). Tapping it toggles the day, and the slider follows.
  - Bottom half, on study days only: a minutes select. It shows the default (e.g. `45m`) and offers the same values plus `Default`. A day that differs from the default gets an ink underline.
  - Under the tiles: `Study 5 · Rest 2`.
  - The last study day cannot be turned off. Its tile shakes (only when reduced motion is off) and `Keep at least one study day` shows.
- **DaysOff** section, always visible, headed `Days off`:
  - Rows such as `Oct 12 – Oct 16 · 5 days ×`.
  - Empty state: `None`.
  - `Add days off` opens `from` and `to` date inputs plus `Add`.
  - Validation: from ≤ to, both between today and the exam, at most 20 ranges.
- **TestRhythm** `Practice tests`: segmented `None · Weekly · Twice a week · Every study day`.
  - **TestSize**:
    - `Module · 22 q · 35 min`.
    - `Section · 44 q · 70 min`, disabled with `Needs a 70-minute day`.
    - Every option is disabled below 35 minutes, with `A module needs 35 minutes`.
  - **TestDay** (Weekly and Twice only): `Auto (last study day)`, or one of the study days.
  - Line: *Each test is a new adaptive section. None repeat.*
- **ClockMode** `Clock on practice sets`: `Off · Auto · Always`.
  - `Auto`, the default, times focus sets from Sharpen on, and earlier for any skill where you are slow (see 4, Clock).
  - Helper: `Test pace is 95 s a question`.
- **PreferredTime** `Usual time`, used for the calendar: chips `Morning 8:00 · Afternoon 15:00 · Evening 18:00 · Other`, where `Other` opens a time input.
- **TotalsLine**: `Until Nov 7: 31 study days · 23 h · 6 tests · about 870 new questions`.

###### 2e. Step 4: What to focus on
- H2 **What to focus on**. Subline: *Focus gets most of your week. Strong stays on light review.*
- **FocusCounters**:
  - `1/2 focus` (orange tag), `1 strong` (ink tag), `2/6 skills on focus`.
  - Quiet `Use suggestions` and `Reset`.
  - **At the cap**, a visible line under the counters: *2 focus areas at most. Move one back to Normal to pick another.* (Skills: *6 skills at most.*)
- **DomainRow** ×4, a grid of `name | stats | segmented | chevron`:
  - Row tint: Focus rows `--wash`, Strong rows get a 1.5px ink inset outline. The tint is never the only signal; the segmented control and the tags say it too.
  - Name, with a mono weight tag under it: `35% of the test` or `15% of the test`.
  - Stats: an `.mbar` of mastery, then mono `142 answered · 71% right · 3 mistakes` (orange dot on mistakes), or `Not started`.
  - A **Suggested** tag when the suggestion differs from the choice, e.g. `Suggested: Focus · weakest` or `Suggested: Strong · 86%`.
  - **Suggestion rule**:
    - Focus on the weakest worked domain when it is below 0.8.
    - Focus on any domain that holds a third or more of the open mistakes.
    - Strong on every domain at 0.8 or above.
  - **Segmented** `↑ Focus / — Normal / ✓ Strong`:
    - A radiogroup with arrow-key navigation.
    - Focus is orange when on.
    - At the cap, the third domain's Focus is disabled and the helper line above explains why.
  - **Chevron**: shows a count, e.g. `2 skills on focus` or `4 skills`. It expands **SkillRows**:
    - Each row: glyph, short name, mastery bar, `answered · right% · mistakes`, and a `Focus / — / Strong` segmented control.
    - A grid-in or pace gap shows as a tag: `grid-in 48% vs 71%` or `slow · 2:40 a question`.
- **SplitBar** `Your practice week`:
  - A stacked bar with the four domains labelled, e.g. `Algebra 24%`. Focus domains are orange; the others use ink and grey tints.
  - Under it in mono: `was 35 / 35 / 15 / 15 by the test's weights`.
  - These are the real shares the scheduler deals (section 4).
- **Extras** (the equivalent of their vocabulary toggle):
  - `Rechecks`, default on: *Mistakes you fixed come back 3, 10 and 30 days later with new numbers.*
  - `Question of the day`, default on.
  - `Daily challenge`, default off.
  - Extras never count against the day's minutes.
- **Your own tasks**:
  - Quick-add chips: `+ Reading & Writing · 30 min · every study day`, `+ Official Bluebook practice test · once`, `+ Other…`.
  - `Other…` opens title (≤60 characters), minutes (5–240) and repeat (`Once on…` date / `Every study day` / `Weekly on…` weekday).
  - Added tasks list below with ×.
  - They count toward the day's planned minutes and are done when you tick them.
- Create is never blocked by focus. With nothing chosen, the plan follows your results. Theirs disables Create.

###### 2f. Create and save
- `Create plan` sends `POST /api/plan`. It is synchronous and returns in under a second, so there is no fake progress screen; the button shows `aria-busy` until the call returns. Then:
  - the draft is cleared;
  - the URL becomes `/plan/`;
  - the page scrolls to the top on the Plan tab with today selected;
  - a toast (`role=status`) reads `Plan made · 31 study days to Nov 7`.
- `Save changes` sends `PATCH /api/plan/{id}`, which freezes past days first. Toast: `Plan updated`.
- `Save as new plan` sends `POST /api/plan {from: id}`. The old plan is archived.
- Errors:
  - 422: the message shows under the footer, and the step with the bad field gets the red dot.
  - 5xx: *Couldn't save the plan. Your draft is kept.* with `Try again`.

---

##### 3. Plan view

At 1280px the view is max 1120px wide. From the top: title row, stat tiles, banners, sticky tabs, then the tab body.

###### 3a. Title row
- Plan name: H1 28/800, default `Nov 7 · 700`.
- Mono sub-line: `5 days · 45 min · weekly module · Focus Advanced Math, Circles`.
- Right-aligned: quiet `Edit` (to `?edit=id&step=1`) and a `⋯` **PlanMenu**:
  - `Rename`
  - `Duplicate`
  - `Calendar…`
  - `Share read-only…`
  - `Print`
  - `Archive`
- The menu closes on Esc or an outside click and returns focus to its button.

###### 3b. StatTiles (4 in a row at desktop; one full-width tile plus a 3-up row at 390)
1. **Days to exam**:
   - `45` (DM Mono 72), with `days to Sat, Nov 7` and `31 study days · 6 tests left`.
   - On the eve: `1 · SAT tomorrow`. On the day: `SAT today`.
   - A `not booked` tag that links to step 2.
2. **Score**:
   - `560 → 700` with `+140 to go`.
   - A 200–800 track: the start marker, the target in orange, and the recent tests' mean band as a grey span.
   - A status chip: `Ahead · +25`, `On pace`, `Behind · 40` or `Target reached`, with the mono caption `from 2 tests since Sep 23`.
   - With no test since the plan began, the chip reads `No test yet` and the quiet button `Take this week's test now` starts the next test task.
3. **Plan done**:
   - `27%` with `12 of 44 study days`, a bar, and mono `31 tasks done · 2 skipped · 1 made up`.
   - Study days are the denominator because the future task count is a forecast, while study days are fixed.
4. **This week**:
   - `2h 10m of 3h 45m`, with a bar.
   - One dot per study day, each with its weekday letter under it: filled = done, half = partly done, ring with a dash = missed, orange ring = today.
   - `Streak 4 · longest 9`, where rest days and days off do not break the streak.

###### 3c. Banners
Each banner is dismissible. They appear in this order.
- **DriftBanner** (`suggest` present):
  - Up: `Your last 2 tests average 650 (Sep 14, Sep 21). The plan starts from 560.` Buttons: `Start from 650` (`PATCH {current}`), `Not now`.
  - Down: `Your last 2 tests average 520. The plan starts from 560.` Same actions.
  - Target reached: `Your last 2 tests average 710, past your 700 target.` Buttons: `Raise to 750`, `Keep 700`.
  - `Not now` is remembered per set of sittings, on the server.
- **BehindBanner** (`behind` present):
  - `2 of 5 study days done in the last 7. You average 22 min on a study day; the plan asks 45.`
  - Pill `Fit the plan to 25 min`. Under it, a preview line: `Same date and target · 870 → 480 questions to Nov 7 · pace unchanged`.
  - Quiet buttons: `Add days off`, which opens the day-off control, and `Dismiss`.
  - Toast: `Plan fitted to 25 min a day`.
- **MissedBanner** (the last planned study day was missed):
  - `Missed Tue, Sep 29 · Focus set on Circles, Percentages`.
  - Quiet `Do it now`, which starts that day's focus task and marks the day made up when it finishes.
  - `Move to Thu`, which moves it onto the next study day.
  - `Dismiss`.
- **BookedReminder** (the date is provisional): `Nov 7 isn't booked yet` with `Booked it`.

###### 3d. Tabs
- A sticky segmented control under the banners: `Plan · Progress · Plans 3`.
- It uses `role=tablist`, arrow keys move between tabs, and it sets `?tab=`.
- The stat tiles stay above the tabs on every tab.

###### 3e. Plan tab: layout
- At 1280: two columns (1.55fr / 1fr).
  - Left: DayPanel, then WeekStrip.
  - Right: ComingUp.
  - Below both, full width: PhaseStrip and MonthCalendar.
- At 390, in this order: DayPanel, WeekStrip, ComingUp, PhaseStrip, MonthCalendar.

###### 3f. DayPanel
Shows the selected day, today by default.

- **Head**:
  - Kicker: `TODAY · WED SEP 23`, or `THU · OCT 1` for another day.
  - Kind tag: `Practice`, `Test day`, `Rest`, `Day off`, `Rest before the SAT` or `SAT`.
  - Phase tag: `Build`, `Sharpen` or `Final`.
  - Right-aligned mono: `45 min planned`.
  - A `⋯ Day` menu:
    - `Change today's time…`: a minutes select for this day only.
    - `Take the day off`: its focus topics move to the next practice day.
    - `Add a task`.
    - `Reset this day`, shown when the day has overrides.
- **Progress line**: a bar filled by minutes done over minutes planned, with `2 of 4 tasks · 12 of 45 min · 33 min left` and `9 questions · 7 right`.
- **TaskRow list** (`UI.taskRow`), in order. Each row has these parts:
  - **Status circle**:
    - todo: empty
    - active: half filled
    - done: ink with a check
    - marked done: ink with a check and a small `m` in the title attribute; the text `Marked done` also shows
    - skipped: ring with a dash
    - moved: ring with an arrow
    - For your own tasks, the circle is a real checkbox (`Mark as done` / `Mark as not done`).
  - **Title**, a **type tag** and one **detail line**. Type tags: `Mistakes`, `Rechecks`, `Focus`, `Test`, `Your own`, `Extra`.
  - **Mono meta**, e.g. `18 questions · 28 min · Medium–Hard · Timed · Practice session`, with domain tags.
  - **Action**:
    - `Start`, or `Resume · 6 of 18` for an active set. The count comes from drill state `answered/total`, and total grows as repairs are added.
    - A done task shows `8/10 · 12 min` and `Review`, which opens the session summary or the test report.
    - The first undone task's action is the pill; the others are quiet.
  - **`Why this?`** is a disclosure listing the server's `why` lines, e.g.:
    - `Circles: 2 open mistakes, “used the diameter as the radius”`
    - `Circles: 41% right on 17, last worked 9 days ago`
    - `Geometry & Trig is on Focus: 32% of your practice`
    - `Clock on: you take 2:40 a question here; test pace is 1:35`
  - **`⋯` TaskMenu**:
    - `Move to…`: the next 7 study days as items (`Thu, Sep 24 · 45 min`), plus `Another date…`, a date input limited to the plan's range before the eve.
    - `Skip` / `Undo skip`.
    - `Mark done` / `Mark not done`.
    - `Swap topics` (focus only): cycles through the server's `alternatives`, two other topic sets with the same domain shares.
    - `Make it a section` / `Make it a module` (test only, when the day's minutes allow).
    - `Edit` and `Remove` (your own tasks only).
    - `Again · new questions` (done tasks): starts 10 more on the same topics, tagged `:extra`.
  - A **skipped** row drops to 55% opacity, with a `Skipped` tag and `Undo`.
  - A **moved** row shows as a ghost: `Moved to Thu, Sep 24 · Undo`.
- **Task kinds**:
  - **Fix mistakes**:
    - Detail: the top three open mistake labels with orange dots, plus `+5 more`.
    - It builds a drill with `{mistakes: true, count, task}`.
  - **Still fixed?** (rechecks):
    - Detail: `2 mistakes fixed Sep 12 and Sep 18 · new numbers`.
    - Body: `{recheck: true, count, task}`.
  - **Focus set**:
    - Detail: topic chips with their glyphs.
    - Body: `{topics, count, difficulty, timed, minutes, fmt, source: 'plan', task}`.
    - With a grid-in gap, the meta adds `Grid-in only` or `Half grid-in`.
  - **Module test / Section test**:
    - Detail: `New adaptive section · 22 questions · 35 min`.
    - Action `Start` calls `POST /api/mock/new {full, timed: true, task}` and opens `/test/?s=`.
  - **Your own task**:
    - Title, minutes and `repeats every study day`.
    - Tick to mark done.
    - The helper appears only on the first one: *Do this one on your own, then tick it.*
  - **Question of the day** (extra):
    - Detail: its skill.
    - `Answer` goes to Today's inline question. Once answered: `Done · right` or `Done · wrong`.
  - **Daily challenge** (extra):
    - `10 questions, the same for everyone`, then `rank 14 of 203` once done.
- **Footer states**:
  - All counted tasks done: `Day done ✓` with the quiet `Keep going · 10 more` (never runs out) and `Start tomorrow's focus set`.
  - Rest day: `Rest day · next study day Thu, Sep 24`, with `Practice anyway`, which starts 10 questions from the next allocation.
  - Day off: `Day off`, plus `Undo day off` when it was taken from the Day menu.
  - Nothing left because every task was moved or skipped: `Nothing left today · 1 moved to Thu` with `Work ahead`.
- **Future day**:
  - The same rows, in preview.
  - Fix and recheck rows read `Open mistakes that day come first · 8 open now`.
  - The action is a quiet `Start early`, which counts for that day.
  - Move, skip, swap and add all work on future days too.
- **Past day**:
  - `Planned` lists the frozen tasks.
  - `Done` lists that day's sessions: time, kind, `right/asked`, and a link to the review.
  - A status tag: `Done`, `Partly done`, `Missed`, `Skipped` or `Made up Oct 2`.
- **Eve**: `Rest before the SAT`, plus the **Checklist** (checkboxes stored in localStorage per viewer):
  - Bluebook installed and updated
  - Admission ticket
  - Photo ID
  - Device charged, and a charger
  - Pencils for scratch paper
  - Calculator (optional; Desmos is in Bluebook)
- **Exam day**: `SAT today · good luck`, plus the Checklist.
- **After the exam**, the **ResultPanel**:
  - `How did it go?`, a Math field (200–800), an optional R&W field, and `Save`, which calls `POST /api/plan/{id}/result`.
  - The panel stays until a score is saved: *Enter it when your scores are out.*
  - Then a summary: `Days done 38 of 44 · 29 h · 1,130 questions · 41 mistakes fixed · Target 700 · got 690`.
  - Pill `Plan the next one`: the wizard opens with current = the result (or the last test mean), date = the next published date, and the same time, focus and your own tasks.

###### 3g. WeekStrip
- **Header**:
  - `Week 3 of 7 · Sep 21–27`.
  - ‹ › buttons, disabled outside the plan's weeks.
  - `This week`, shown when you are on another week.
  - Right-aligned: `8 of 12 tasks · 67%`, with a bar.
- **Theme line** (server `weeks[].theme`): `Build · Circles, Percentages, Nonlinear functions · Module test Fri`. In Final it reads `Final · full sections and open mistakes`.
- **Seven columns**, each with:
  - weekday and date (mono);
  - a kind icon: circle = practice, rounded rectangle = test, none = rest, hatching = day off, orange `SAT`;
  - `45m`;
  - `2/3` tasks, or `rest`, or `—`;
  - a bar filled done/planned;
  - a check when the day is done.
- Selected column: an orange inset outline. Today: an ink outline with a 3px ink top bar.
- Clicking a column selects that day.

###### 3h. ComingUp (right column)
- Headed `Coming up`, listing the next 5 study days:
  - `Thu Sep 24 · Focus · Circles, Linear inequalities · 45m`
  - `Fri Sep 25 · Module test · 35m + 10m practice`
- Then `Next rest Sat Sep 26`, and `Sharpen starts Oct 15 · harder, timed`.
- Each row selects its day.

###### 3i. PhaseStrip and MonthCalendar
- **PhaseStrip**:
  - A three-part bar, each part as wide as its phase's days. The current phase is orange; the others `--tile`.
  - Each part shows its name, dates and one line:
    - **Build · Sep 23 – Oct 14**: *Weak skills and new ground, every difficulty.*
    - **Sharpen · Oct 15 – Oct 28**: *Harder, mixed, on the clock.*
    - **Final · Oct 29 – Nov 6**: *Full sections and your open mistakes.*
  - A plan under 35 days shows two parts; under 14 days, only Final.
- **MonthCalendar** (`UI.monthGrid`):
  - Header `October 2026` with ‹ ›, from the start month to the exam month, with no week cap.
  - Monday-first grid. Cells are 64px tall at desktop and 46px on phones. The date sits top-left in mono and the kind marker in the centre.
  - Status on the marker:
    - done: ink fill
    - partly done: half fill
    - missed: ring with a dash
    - skipped: ring with a slash
    - made up: ink fill with a dot
  - Planned minutes sit bottom-right: mono 10px at desktop, **9.5px on phones (still shown)**.
  - A day with your own tasks gets a small ink tick top-right.
  - A day off gets a diagonal hatch (`repeating-linear-gradient` with `--mat`).
  - Exam day: orange fill with `SAT`. The eve: `Rest` in mono.
  - Days outside the plan are blank and cannot be focused.
  - Today: ink inset outline. Selected: orange inset outline on `--wash`. The first day of each phase carries a mono label top-right.
  - Keyboard: `role=grid` with roving tabindex. Arrow keys move, Home/End go to the week's start or end, PageUp/PageDown change month, and T returns to today.
  - Each cell's `aria-label` reads like `Thu Oct 1, practice, 45 minutes, 2 of 3 tasks, partly done`.
  - **Legend**, always shown: Practice · Test · Rest · Day off · Done · Partly done · Missed · Skipped · Made up · SAT.

###### 3j. Progress tab
At 1280 this is a 2-column grid; at 390, one column.
- **ProgressCard** `Since Sep 23`, big mono numbers with labels:
  - `Days done 12/15 · 80%`
  - `Time 9h 20m of 11h 15m`
  - `Questions 412 · 74% right`
  - `Mistakes fixed 23 · opened 31 · open 8` (open links to `/mistakes/`)
  - `Rechecks passed 9 of 11`
  - `Tests 3`
  - `Streak 4 · longest 9`
  - Empty state (day 1): `Day 1. Today's tasks are on the Plan tab.`
- **StudyTimeChart** `Study time per day`:
  - Bars per day: studied minutes in ink, with tests stacked in a hatched ink. Planned minutes are an outlined `--mat` bar behind them.
  - A range segmented control: `2 weeks · Month · Whole plan`.
  - Header total: `9h 20m studied of 11h 15m planned · 12 days`.
  - Tooltip (hover or tap): `Thu Oct 1 · 38 of 45 min · 22 questions · 1 own task`.
  - Empty state: `Nothing logged yet`.
- **TrajectoryChart**:
  - An SVG, 100% wide and 220px tall.
  - The x-axis runs from the start to the exam with month ticks. The y-axis is Math, fitted to the data ±50, with gridlines every 50.
  - A graphite dashed **pace line** runs from (start, current) to (exam, target, capped at 780).
  - An orange target dot at the exam.
  - Each sitting from 30 days before the start is a vertical band (low–high) in `--mat` with an ink midpoint dot. Tooltip: `Module · Oct 2 · 610–750`.
  - A thin line marks `now`.
  - Caption: `A test reads as a band: ±70 for a module or section, ±100 for the diagnostic. The status uses your last 3 tests.`
  - Empty state: `No test yet` with `Start this week's test`.
  - With up to 60 sittings, bands thin to a 3px minimum and a tap selects the nearest.
- **DomainCard** `Accuracy by domain · weakest first`:
  - Four rows, sorted by accuracy since the plan began.
  - Each row: name, focus or strong tag, `68% right · 142 answered`, and a mastery bar with a tick at `start_mastery` and the change `+0.12` shown as bar length.
  - Mono `planned 40% · done 36%` of practice.
  - A row opens `/practice/?topics=…`.
  - **`All 19 skills`** expands in place into a table sorted weakest first. Columns: skill, answered, % right, open mistakes, last worked, and gap tags. A link to `/results/` follows.
- **SplitCard** `How the plan splits your time`:
  - A stacked bar of planned minutes by task type across the whole plan: Mistakes, Rechecks, Focus, Tests, Your own. Each segment is labelled `Focus 62% · 14h`.
  - Under it, a second bar: done so far, by the same types.
- **GapsCard** `What the plan is working on` (shown when there is a gap):
  - `Grid-in 48% right vs multiple choice 71% · 60 answers → focus sets are half grid-in`.
  - `Slowest: Circles 2:40 a question (test pace 1:35) → timed from now`.
- Every chart has a visually hidden `<table>` with the same numbers.

###### 3k. Plans tab (`PlansList`)
- Header `Your plans` with the pill `New plan`.
- Each row shows:
  - name, a status tag (`Active` in orange, `Archived`, or `Finished · 690`) and `You are here` on the one being viewed;
  - mono `Built Sep 23 · Sep 23 → Nov 7 · target 700 · 45 days left · 31 tasks done · 80% of days`.
- Actions:
  - `Open`: an archived plan opens read-only at `?id=`.
  - `Make active`, confirmed in place: `Switch to this plan? Your current one is kept.`
  - `Duplicate`: makes a draft from the plan.
  - `Remove`: archived plans only, confirmed in place, permanent.
- More than 5 plans collapse to 5, plus `Show all 12`.
- Footer line: *Changing your date or target? Edit keeps this plan's record. Save as new keeps this one here.*
- **Archived view banner**: `You are viewing an older plan · Sep 1 → Oct 3 · not your active plan`, with `Back to active plan` and `Make this my plan`. Every Start, Move and Skip is hidden.

###### 3l. Calendar, share and print
- **Calendar…** dialog:
  - `Download .ics`: fetches `GET /api/plan/{id}/ics` with the usual headers and saves it as `sat-plan.ics` through a Blob.
  - `Subscribe`: turns on a feed at `/cal/<token>.ics` and copies the link. The feed updates itself.
  - `Turn off link` revokes the token.
  - Note: *Some calendar apps ignore reminders in subscribed calendars; the download keeps them.*
  - The events:
    - One event per study day from today, at the preferred time, lasting its minutes: `SAT Math · 45 min · Circles, Percentages`, or `SAT Math · Module test`.
    - An all-day `SAT` on the exam day and `Rest before the SAT` on the eve.
    - A 10-minute `VALARM` on each study event.
    - `UID plan-<id>-<date>@satfreshman`, so a re-import updates instead of duplicating.
    - Floating local times, with no TZID.
- **Share read-only…** dialog:
  - Turns on `/plan/?view=<token>`, shows the link and a copy button, and offers `Turn off link`.
  - The shared page shows the title row, tiles, calendar, week and Progress tab. It shows no learner code and no start buttons, and a name only if one is set.
  - Note: *Anyone with the link sees this plan and its progress.*
- **Print**: `@media print` hides the nav, tabs and menus. It prints the title, tiles, phase strip, month grids and a week-by-week list (each day with its kind, minutes, topics and your own tasks).

###### 3m. Toasts (`UI.toast`, `role=status`, 5 s)
- With Undo: `Skipped`, `Moved to Thu, Sep 24`, `Marked done`, `Task removed`, `Day off`, `Plan archived`.
- Without: `Task added`, `Plan updated`, `Plan fitted to 25 min a day`, `Switched to this plan`, `Link copied`.
- A start that fails shows inline on its row: `Couldn't start. Try again`.

---

##### 4. How days and tasks are made (`server/plan.py`)

Every endpoint takes X-Learner and X-Tz. "Today" is the learner's local date, and the plan stores the tz it was created with.

**Day kind** for date d, checked in this order:
1. `before` if d < start; `after` if d > exam; `exam` if d == exam; `eve` if d == exam − 1.
2. `off` if d is in an off range or an override has `off`; `rest` if `days[dow] == '0'`.
3. `test`:
   - An override `test` wins.
   - `none`: no tests.
   - `weekly`: `test_day` when it is a study day, else the week's last study day that is not the eve or off. If that is off, the previous study day of the same Mon–Sun week.
   - `twice`: the weekly day plus the study day nearest Wednesday that is not it. A week with one study day gets one test.
   - `daily`: every study day.
   - A test needs ≥ 35 minutes that day, and a section needs ≥ 70; otherwise it drops to a module. Final upgrades a module to a section at ≥ 70.
4. Otherwise `practice`.

**Minutes**: override minutes, else `day_minutes[dow]`, else `minutes`. Days that are not study days get 0. Moved tasks add their minutes to the target day and take them off the source day.

**Questions for m minutes**: `clamp(round(m*60/95), 5, 120)`.

**Phases**, with T = exam − start in days:
- T ≥ 35: Build is the first 55%; Final is the last max(10, 15%) days before the eve; Sharpen sits between them.
- 14 ≤ T < 35: Sharpen, then a 10-day Final.
- T < 14: Final only.

**Difficulty** (the drill `difficulty` list):

| phase | target < 550 | 550–680 | ≥ 690 |
|---|---|---|---|
| Build | easy, medium | all | medium, hard |
| Sharpen | all | medium, hard | medium, hard |
| Final | all | all | medium, hard |

**Clock**:
- `off`: never timed.
- `always`: every focus set is timed.
- `auto`:
  - Focus sets are timed in Sharpen and Final.
  - A skill whose median ms over its last 20 answers exceeds 120 s is timed in any phase.
  - Timed means `timed: true, minutes: round(q*95/60)`.

**Format tilt**: over the last 60 answers, when grid-in accuracy trails multiple choice by 15 points or more (with at least 15 grid-ins), focus sets are `fmt: 'mix'` (half grid-in). Needs the drill `fmt` filter shared with the Practice section.

**Domain shares**:
- `w_d = BLUEPRINT[d] × {focus 2.0, normal 1.0, strong 0.4}[state_d] × (1.5 − m_d)`, where m_d is the mean mastery of the domain's worked topics, or 0.5 when none are worked. The weights are normalised.
- Topic weight inside a domain: the coach score (floored at 1) × {2, 1, 0.4} for the skill's own state.

**Allocation**:
- Deterministic, and cached per (plan, local date, overrides version).
- Slots per practice day: 3 when q ≥ 15, 2 when q ≥ 8, else 1.
- The walk runs over practice days from today. Each day takes domains by largest deficit (share × slots so far − slots used), at most 2 slots per domain per day.
- Inside a domain it takes the topic with the largest deficit not used on the previous 2 practice days.
- **Fallback** when none qualifies, which happens in 3-topic Advanced Math: relax to "not used on the previous practice day", then to "any topic".
- Swapped topics from overrides are fixed slots and count toward the deficits.
- A skipped focus task's topics keep their deficit, so they come back sooner.
- `alternatives` are the next two candidate sets under the same rules.

**Tasks for a practice budget of q questions**, where `task` is `"YYYY-MM-DD:kind"`:
1. `fix`, when open traps exist: `count = min(2 × open templates, max(4, round(0.3q)))`, rounded to even.
2. `recheck`, when Rechecks is on and closed traps are due: `count = min(due, 4)`.
3. `focus`: `count = q − fix − recheck`, at least 5. It is left out when q ≤ 8 and fix used all of q.
4. On a test day, `test` comes first. Leftover minutes of 15 or more get tasks 1–3.
5. `custom` tasks for that date or repeat rule. They count toward planned minutes but carry no questions.
6. Extras `qotd` and `challenge`, which are not counted.
7. Each task gets `why` lines built from the same numbers the allocator used.

**Task status**:
- `done` when any of these holds:
  - a session with its `task` finished;
  - that session's answered ≥ its planned count;
  - a `done` mark exists;
  - for `test`: any module or section finished that local day;
  - for `focus`: that day's attempts on its topics from any source ≥ its count.
- `made_up` when this happened on a later date.
- `active` while a tagged session is open.
- `skipped` or `moved` from marks.
- Otherwise `todo`.

**Day status**:
- `done` when every counted task is done or made up, or minutes_done ≥ 0.8 × planned.
- `skipped` when every counted task was skipped.
- `partial` when anything was done.
- `missed` when planned > 0 and nothing was done.
- `minutes_done` is the sum of:
  - the day's attempt ms, each capped at 10 min;
  - minutes marked done on your own tasks;
  - for each module or section finished that day **whose answers carry no ms**: min(finished − started, 35 × modules).

**Plan streak**:
- The run of planned study days back from today (today counts once it is done or partial) whose status is done, partial or made up.
- Rest days and days off are skipped, not broken.
- A rest day with any practice extends the streak.
- `longest` is the best run in the plan.

**Freezing**:
- On every `GET /api/plan` and before every edit, each day from the last frozen day to yesterday is written to `plan_days`: kind, minutes, test, phase, and the planned tasks with their topics.
- Past days are never recomputed.

**Recent tests mean**: over the last up to 3 finished module, mock or diagnostic sittings within 45 days, the mean of their band midpoints.

**Drift**:
- Built from sittings finished after max(plan.updated, drift_seen).
- `up` or `down` when |mean − current| ≥ 40.
- `target` when mean ≥ min(target, 780).
- `suggest = {kind, current: round10(mean), sessions}`.

**Pace status**: the mean against the pace line at the sittings' mean date. |Δ| ≤ 35 is `On pace`; otherwise `Ahead · +n` or `Behind · n`. A mean ≥ min(target, 780) is `Target reached`.

**Behind**:
- Looks at the last 7 local days.
- Applies when there were ≥ 3 planned study days and under 60% of them were done or partial.
- `behind = {planned, done, avg_minutes, suggest_minutes}`, where suggest_minutes is avg_minutes rounded up to a chip value, at least 15.
- The banner's preview line comes from `POST /api/plan/preview` with that minutes value. Applying it is a `PATCH {minutes}`.

**Week theme**: the phase, the three topics with the most slots that week, the test day, and your own repeating tasks.

---

##### 5. Other pages

- **Today (`/`)**, with an active plan, the Next card becomes today's plan:
  - `Today's plan · 2 of 4 done · 33 min left of 45`.
  - The first undone counted task is the main row with its pill; the other tasks are compact rows with status circles; your own tasks have checkboxes.
  - The link `Full plan`.
  - All done: `Day done ✓` with `Keep going · 10 more`.
  - Rest day: `Rest day · next study day Thu` and `Practice anyway`.
  - Without a plan, the coach set stays, with the quiet link `Make a plan`.
  - It reads `/api/today` → `plan`.
  - The shell's streak flame shows the plan streak when a plan is active.
- **Practice session summary**, when `drill_finish` returns `plan`:
  - `Next in today's plan: Focus set · 18 questions` with `Start`.
  - Or `Today's plan is done` with `Keep going · 10 more` and `Back to plan`.
- **Test report**:
  - When the sitting carries a `task`: `Back to plan`, plus the drift prompt if it applies.
  - When sessionStorage `satf.return` holds a `/plan/` path: `Back to your plan`.
- **Me**:
  - A plan tile: `Nov 7 · 700 · 45 min × 5 · 27% done`, with `Edit plan`.
  - Me's goals fields (target, exam date, minutes, days) write through to the active plan with `PATCH`. They are one value across Me, Today and Plan; theirs disagree.

---

##### 6. States

- **Loading**: skeleton tiles in `--tile`, pulsing only when motion is allowed. That means 4 stat tiles, a 180px day panel, a 90px week strip and 5×7 calendar cells. In the wizard the stepper works and the controls stay disabled until `/api/plan` returns.
- **Error**:
  - The page shows `The server is not answering.` with `Try again`.
  - The wizard keeps working from the local draft, with Create disabled and `Can't save right now`.
  - Failed task actions show inline and keep their state.
- **New student**:
  - The landing preview shows dashes, and the example day holds only a blueprint-weighted focus set.
  - Step 1 offers the diagnostic. Step 4 rows read `Not started`, with no suggestions.
  - Day 1 has no fix task, and focus starts on Algebra and Advanced Math.
  - Progress shows `Day 1`; the trajectory shows `No test yet`; the study-time chart shows `Nothing logged yet`.
- **Lots of history**:
  - The months navigate over any span.
  - Trajectory bands thin.
  - Plans collapse at 5.
  - The skills table sorts and scrolls inside its card.
  - Fix tasks are capped as in section 4, and the rest wait in `/mistakes/`.
- **Plan in the past** (exam < today): the ResultPanel, and no tasks.
- **Archived (`?id=`)** and **shared (`?view=`)**: read-only, with their banners.
- **Blocked storage**: the shell's existing message. The checklist then shows unticked every time.

##### 7. Phone at 390px
- 16px gutters, no horizontal page scroll, and every tap target at least 44px.
- **Wizard**:
  - The stepper shows numbers plus the step-name line.
  - WeekdayTiles wrap to a 4 + 3 grid, each with its STUDY/REST label and minutes select.
  - The date chips are the only horizontal scroller (scroll-snap).
  - The Glance is a bottom sheet.
  - The footer is sticky above the tabs, with `env(safe-area-inset-bottom)`.
- **Plan view**:
  - The tiles are one full-width Days tile plus a 3-up row of Score, Plan done and Week.
  - The tabs are sticky under the header.
  - A task's action button drops under its title when the row is narrower than 340px, and the ⋯ menu opens as a bottom sheet.
  - The week strip columns are 7 × ~48px, holding the date, icon and `2/3`.
  - Calendar minutes stay visible at 9.5px.

##### 8. Accessibility
- Every slider has a paired number field.
- Segmented controls and tabs are radiogroups or tablists with arrow keys.
- Stepper buttons carry `aria-current="step"`.
- The calendar is a grid with roving tabindex.
- A task status change is announced through `role=status`.
- Menus, dialogs and sheets close on Esc and return focus.
- Charts have hidden data tables.
- Colour is never the only signal.

### 3.6.4 Extras: what they missed

- **Focus that really changes time, with a live split bar**: Today, Focus only reorders topics and every topic still gets one turn per cycle. Domain shares feeding a slot allocation make 'most of your week goes here' true, and the SplitBar shows the real shares before you commit.
- **Skill-level focus (19 skills) under each domain**: They stop at domains. A student with one bad skill (circles) should not have to put all of Geometry & Trig on Focus.
- **'Why this?' built from facts, not AI prose**: Their aiReason is generated text. Ours lists the open mistakes by name, accuracy, days since the skill was last worked, the focus share and any timing gap: the same numbers the scheduler used, so the student can check them.
- **Move any task to any day, swap topics, take a day off, change one day's time**: Their only reschedule is 'a later day in the same week'. Real weeks need more, and the plan re-deals around every change.
- **Custom tasks that repeat (for example R&W 30 min every study day)**: We only teach Math. Letting the student put their R&W study, or an official Bluebook test, into the same plan and count it makes the plan cover the whole SAT.
- **Behind banner fitted to the minutes you actually study**: Theirs offers a vague 'rebalance'. Ours shows what you really average, proposes that as the plan, and previews the effect on questions and pace before you apply it.
- **Mistake-first daily task**: Every open trap names its misconception, and the drill serves the same template with new numbers. A fixed bank cannot re-ask the same trap without repeating the question.
- **Rechecks 3, 10 and 30 days after a mistake is fixed**: Spaced checking only works because a template regenerates with fresh numbers. It turns 'fixed once' into 'still fixed', and Progress shows the rechecks passed.
- **A fresh adaptive test on every test day**: Their plan draws on 10 papers and one free attempt, so a 12-week plan with weekly tests would run out. Ours never does, and 'Make it a section' upgrades a test on long days.
- **Keep going / Again · new questions / Start tomorrow early**: The bank never runs out, so a keen student is never stuck after 'Day done'.
- **Phases (Build, Sharpen, Final) with a difficulty ramp and the clock turning on**: Their 'week-by-week' is a theme sentence. Ours makes the weeks actually differ: harder and timed as the date nears, then full sections.
- **Grid-in gap and pace gap read from attempts**: Every attempt stores its format and time. When grid-ins trail multiple choice, or a skill runs slow, the plan tilts focus sets to grid-ins or turns the clock on early, and says so.
- **Pace on every exam-date chip, a pace tag and a later-date suggestion**: They print 'about 200 points per week' with no comment. We show the trade-off for each date and offer one tap to a more realistic one.
- **Honest target note from our own scoring**: Above 580 needs the upper module (14 of 22 in module 1), 700 is about 88% of the weighted points, and above 780 is capped. That is real context their plan never gives.
- **Frozen day history with done / partly done / skipped / missed / made up**: They keep no record of whether the plan was followed. Freezing past days keeps the record honest when settings change.
- **Score trajectory with a pace line, from the mean of recent tests**: It answers 'am I going to make it?' without letting one noisy sitting flip the verdict.
- **Drift in both directions, and 'Target reached, raise it?'**: Theirs only fires upward, as a snoozed localStorage banner. Ours also corrects an optimistic start and offers a next target.
- **Plan streak that rest days don't break, used app-wide**: Their profile and QOTD streaks disagree, and ours currently breaks every weekend for a 5-day plan. One rule everywhere.
- **Calendar download and a self-updating calendar feed**: They collect a preferred time and do nothing with it. Ours puts study blocks in the student's calendar through a revocable token, never the learner code.
- **Read-only share link for a tutor or parent**: Their Classes and teacher dashboard is hidden and needs a teacher account. A revocable link gives an adult the plan and its adherence with no account.
- **Example day on the landing, and a real named mistake in the stats**: The student sees what a day holds, built from their own data, before committing. Their stat cards are marketing numbers.
- **Print view**: A paper plan for the desk, built with print CSS.
- **Exam-eve rest and a test-day checklist**: The eve is already a rest day. Adding what to bring for Bluebook makes the last two days useful.
- **After the exam: log the real score (whenever it arrives), a plan summary, the next plan in one tap**: Today the page just drops into the wizard. Students often retake, and carrying the result and settings forward is what they need.
- **Unlimited plans with duplicate, switch and 'You are here'**: They cap plans per billing cycle and hide failed ones. Ours are free.
- **Server-side draft that survives failures and follows the learner code**: Theirs resets the draft after a failed build; ours is lost when the tab closes. The new one does neither and carries across devices through /api/me/carry.

### 3.6.5 Server changes

Tables and columns here are added by F4 as listed in §2.5; the drill fields map through §2.6; prefs through §2.7.

- **New module server/plan.py**: Owns: SAT_DATES (moved from the page); day kinds with overrides; test days; phases; difficulty, clock (auto, with the slow-skill rule) and format-tilt rules; domain shares; slot allocation with its fallback and alternatives; tasks and why-lines for a date; task and day status; the plan streak; freezing; stats; the recent-tests mean; pace status; drift; behind; week themes; the target note; the .ics builder. These are pure functions over (plan cfg, overrides, marks, custom tasks, learner history, tz), plus freeze(). It ends with a __main__ assert self-check covering: day kinds (eve, off, the weekly test on the last study day, the exam-week test moving to Thursday, a section dropping to a module on a short day), shares summing to 1, the Advanced Math fallback returning a set, and the streak skipping rest days.
- **New table plans**: plans(id TEXT PK, learner TEXT, name TEXT, cfg TEXT JSON, start TEXT, tz INTEGER, start_mastery TEXT JSON, created TEXT, updated TEXT, archived TEXT NULL, result TEXT JSON NULL, drift_seen TEXT NULL, cal_token TEXT NULL UNIQUE, view_token TEXT NULL UNIQUE). Index on (learner, archived). cfg fields: current, target, rw_current?, rw_target?, exam_date, booked, minutes, day_minutes[7]|null, days, off[[from,to]], tests none|weekly|twice|daily, test_size module|section, test_day 0-6|null, clock off|auto|always, time HH:MM|null, focus{domain}, skills{topic}, extras{recheck,qotd,challenge}.
- **New tables plan_days, plan_overrides, plan_tasks, plan_marks**: plan_days(plan, day, kind, minutes, test, phase, tasks JSON, PK(plan, day)) holds frozen history. plan_overrides(plan, day, minutes NULL, off INTEGER DEFAULT 0, test TEXT NULL, topics TEXT JSON NULL, PK(plan, day)). plan_tasks(id TEXT PK, plan, day TEXT NULL, repeat TEXT NULL (study_days | weekly:0-6), title TEXT <= 60, minutes INTEGER 5-240, created, removed NULL) holds custom tasks. plan_marks(plan, day, task, status done|skipped|moved, to_day NULL, at, PK(plan, day, task)); a mark on a custom task id records it done for that day.
- **learners: plan and plan_draft columns**: plan TEXT is the active plan id. plan_draft TEXT JSON holds {step, fields, updated}. The active plan mirrors current, target, exam_date, minutes, days, tests and focus into the existing learners columns, so the coach keeps working. progress.carry moves plans (UPDATE learner) and COALESCEs plan and plan_draft. When both codes have an active plan, the target's stays active and the other's is archived, never deleted.
- **GET /api/plan**: Freezes past days first. Returns {active, plans:[PlanSummary {id, name, status, built, start, exam, target, days_left, tasks_done, adherence, result}], draft, bank:{topics:19, templates:386, domains:4, example:{label, topic}}, score, sittings:[{session, kind, at, low, high}], days:[Day], weeks:[{n, from, to, theme, tasks_planned, tasks_done}], today:{day, tasks}, stats:{days_planned, days_done, study_days_total, tasks_done, tasks_skipped, made_up, minutes_planned, minutes_done, questions, right, mistakes_opened, mistakes_closed, mistakes_open, rechecks_passed, rechecks_due, tests, streak, longest, week:{minutes_planned, minutes_done, days:[{date, status}]}, split_planned:{kind: minutes}, split_done:{kind: minutes}}, domains:[{domain, state, mastery, start_mastery, right, answered, share_planned, share_done}], skills:[{topic, answered, right, traps, last, gap}], gaps:{fmt, pace}, phases, pace, suggest, behind, state: active|eve|exam|after}. Day = {date, kind, minutes, phase, test, status, minutes_done, questions, right, tasks_planned, tasks_done, custom:bool, overridden:bool}. Task = {id, kind fix|recheck|focus|test|custom|qotd|challenge|extra, title, detail, topics, labels, count, minutes, difficulty, timed, fmt, counted, status todo|active|done|marked|made_up|skipped|moved, moved_to, session, answered, total, result {right, asked, ms}, why:[str], alternatives, start {path, body}, open}.
- **GET /api/plan/day/{date}**: Day plus tasks for any date in the plan: frozen for past days (with that day's sessions), a forecast for future days. 404 outside the plan.
- **POST /api/plan**

  Body PlanIn (cfg fields plus name, custom tasks [{title, minutes, day|repeat}], and an optional from). Synchronous, under 1 s. Sets start = today (local, from X-Tz) and tz, computes start_mastery, archives the previous active plan, mirrors to learners, clears the draft, and returns the GET payload. Returns 422, with a message naming the field, when:
  - current or target is outside 200-800 or not a multiple of 10;
  - target < current;
  - exam_date is not a real date, is not after today, or is more than 730 days out;
  - days does not match ^[01]{7}$ or is all zeros;
  - day_minutes is not 7 values of null|0|5-240;
  - minutes is outside 5-240;
  - off ranges are reversed, fall outside today..exam, or number more than 20;
  - tests, test_size or clock is not in its set;
  - test_day is outside 0-6;
  - more than 2 domains or 6 skills are on focus;
  - a domain or topic is unknown;
  - time is not HH:MM;
  - name is over 40 characters;
  - a custom task has a bad title, minutes or repeat, or there are more than 10 custom tasks.

- **PATCH /api/plan/{id}**: A partial PlanIn on the active plan. Freezes past days, merges, bumps updated and re-mirrors to learners. 409 if archived.
- **Task endpoints**: POST /api/plan/{id}/tasks {title, minutes, day | repeat} creates a custom task. PATCH /api/plan/{id}/tasks/{task_id} {day, status: done|skipped|todo} sets or clears a mark (todo deletes it: Undo); {day, to: date} moves a generated task (to must be a study day in the plan before the eve; a test may not land on a day under 35 minutes); {title, minutes} edits a custom task. DELETE /api/plan/{id}/tasks/{custom_id} sets removed. All of them freeze first and return the refreshed Day and tasks for the affected dates.
- **Day override endpoints**: PUT /api/plan/{id}/day/{date} {minutes? 0|5-240, off? bool, topics? (one of the day's alternatives), test? module|section|none}. DELETE clears the override. Only dates from today to the eve. Returns the refreshed days from that date on.
- **Plan lifecycle endpoints**: POST /api/plan/{id}/activate archives the current plan and unarchives this one; start stays and frozen rows are kept. POST /api/plan/{id}/archive. POST /api/plan/{id}/duplicate writes plan_draft from its cfg and returns the draft. DELETE /api/plan/{id} works on archived plans only, removes the plan and its rows, and returns 409 on the active plan. POST /api/plan/{id}/result {math 200-800 step 10, rw?} is allowed from the exam date on. POST /api/plan/{id}/drift {dismiss: [sessions]} sets drift_seen.
- **Draft and preview**: PUT /api/plan/draft {step 1-4, fields} stores up to 8 KB; DELETE /api/plan/draft removes it. POST /api/plan/preview takes a PlanIn without saving, runs in under 150 ms, and returns {study_days, tests:{count, size, weekday}, hours, questions, pace_per_week, pace_tag, per_date:[{date, days, study_days, pace_per_week, tag}], later_date, split, base_split, phases, target_note:{route_up, route_right:14, route_of:22, points_pct, capped}, sample_day:[Task], warnings}.
- **Calendar and share**: GET /api/plan/{id}/ics (X-Learner) returns text/calendar. POST /api/plan/{id}/links {cal?: bool, view?: bool} mints a random token (secrets.token_urlsafe(16)) or revokes it. GET /cal/{token}.ics serves the same builder with no learner header. GET /api/plan/shared/{token} returns a read-only payload: no learner id, no start bodies, and name only if set. Unknown or revoked tokens return 404.
- **scoring.fraction_for(score)**: The inverse of the ANCHORS interpolation. points_pct = round(fraction x 100). Scores above 780 return 1.0 with capped=True. The route note uses ROUTE_UP_AT (ceil(0.6 x 22) = 14) and LOWER_ROUTE_CEILING 580.
- **POST /api/drill: task, recheck, fmt, count cap for mistakes**: task (str up to 40, matching ^\d{4}-\d{2}-\d{2}:(fix|recheck|focus|extra)$) is stored in cfg. With mistakes:true, count now caps the queue: the most-hit, most-recent templates first, each twice, up to count. recheck:true queues closed traps whose due <= now, on fresh seeds; 409 'nothing to recheck' when none are due. fmt mcq|spr|mix is shared with the Practice section's format filter.
- **POST /api/mock/new: task**: task (^...:test$) is stored in cfg. The results payload echoes task.
- **Finish responses carry plan**: drill_finish and the session finish return plan: {tasks: today's tasks with statuses, next: the first undone counted Task or null} when cfg.task is set, or when a plan is active and the session counts toward today.
- **GET /api/today: plan**: Adds plan: {id, day, tasks, tasks_done, tasks_counted, minutes_left} when a plan is active and today is inside it, else null. days.streak becomes the plan streak when a plan is active.
- **Trap rechecks (owned by the Mistakes section, consumed here)**: traps gains stage INTEGER DEFAULT 0 and due TEXT NULL. Closing a trap sets due = closed + 3 days. A correct answer on that template while due <= now advances the stage and sets due to +10 days, then +30 days, then NULL (passed). A wrong answer follows the existing record() rules (same reason reopens it, another reason opens a new trap) and sets the closed trap's due to NULL with stage -1 (failed). Adds progress.due_rechecks(learner) and rechecks_passed(learner, since).
- **Study time counts tests**: progress.days adds, for each module or section finished that local day whose attempts all have ms NULL, min(finished - started, 35 x modules) minutes. Once the test runner sends per-question ms (a Report-section need), that session's attempts count and the fallback is skipped.
- **PUT /api/me mirrors into the plan**: tests validation widens to none|weekly|twice|daily. When exam_date, target, minutes, days, current, tests or focus change through /api/me and a plan is active, the same fields are PATCHed into the plan (freezing first), so Me, Today and Plan never disagree.
- **test_flow.py and README**: Add the plan checks from the acceptance list to test_flow.py. Update the README serving-layer row for /plan/, add every new endpoint and /cal/{token}.ics, and add a line on the shared-view token.

### 3.6.6 Files this spec names, and who owns each

| file | owner |
|---|---|
| `web/plan/index.html` | S7 |
| `web/plan/plan.js` | S7 |
| `web/assets/ui.js` | F2 |
| `web/assets/ui.css` | F1 |
| `web/index.html` | S3 |
| `web/practice/session/index.html` | S4 |
| `web/results/report/index.html` | S6 |
| `web/diagnostic/index.html` | S5 |
| `web/me/index.html` | S1 |
| `server/plan.py` | S7 |
| `server/app.py` | F0 (routers register themselves, §2.10) |
| `server/db.py` | F4 |
| `server/drill.py` | F5 → S4 |
| `server/progress.py` | F4 |
| `server/scoring.py` | F4 |
| `server/test_flow.py` | shared: new checks go in server/checks/<task>.py |
| `README.md` | shared: each task edits its own subsection |

A file owned by another task is met through §2.9: the owner builds it, or this section's task adds its hook on its own page.

### 3.6.7 Shared needs

- UI.taskRow: one task row (status circle or checkbox, title, type tag, detail chips, meta, Start/Resume/Review, Why this?, a ⋯ menu). Used by Plan, Today's plan card, the landing's example day and the practice-session summary. → built in S7 plan-ui.js  
  ↳ UI.taskRow (S7 plan-ui.js)
- UI.seg and UI.tabs: segmented radiogroups and tablists with arrow keys and a visible disabled reason. Used by Practice (mode, volume, format), Results filters, Tests (module or section) and Report. → built in F1 kit.js
- UI.menu, UI.sheet and UI.dialog: an overflow menu that becomes a bottom sheet on phones, plus a dialog. All close on Esc and return focus. Report, Mistakes and Practice filters need them. → built in F1 kit.js
- UI.toast with an optional Undo (role=status). Saves in Me, Practice and Mistakes. → built in F1 kit.js
- UI.monthGrid: a Monday-first month calendar with roving tabindex and cell-state classes. Today's study-time calendar (they have one) uses it. It must mark days in the learner's local time: theirs marks them in UTC. → built in F1 charts.js
- UI.scoreSlider: a range input with a paired number field and a value bubble. Me (target) reuses it. → built in F1 kit.js
- A stat tile pattern (big mono number, label, sub-line, optional bar). Results, Me and Today.
- UI.barChart (studied vs planned per day) and UI.bandChart (score bands over time with a target or pace line), each with a hidden data table. Today's study time and Results' score over time use the same two. → built in F1 charts.js
- Tasks tagged task='YYYY-MM-DD:kind' on drill and mock sessions. Today, the session summary and the report all read plan status from it.
- Rechecks (traps.stage/due, drill recheck:true) are owned by the Mistakes section: it should show 'Still fixed?' and 'Fixed · rechecked 2/3'. The plan only consumes them.  
  ↳ R9: one check-in schedule, 3/10/30 days (F4); drill pool checks
- A drill fmt filter (mcq|spr|mix), shared with the Practice section's multiple-choice / grid-in / both choice.  
  ↳ R10: the drill body, §2.6 (F5)
- Per-question ms from the test runner (a Report-section need). Study time and the pace gap then include tests exactly.
- One streak rule app-wide: rest days and days off don't break it when a plan is active. The shell flame, Today, Me and the Plan all show the same number.  
  ↳ R13: progress.days (F4)
- Target, exam date, minutes and days are one value. Me's goals card and Today's countdown read the active plan and write through PATCH.
- A return-path convention (sessionStorage satf.return, same-origin /plan/ paths only) so the diagnostic and tests can send a student back to the page that sent them.

### 3.6.8 Acceptance checks

1. curl -s localhost:8000/api/plan -H 'X-Learner: a:v2revplanacc1' -H 'X-Tz: 0' returns active=null, bank.topics=19, bank.templates=386 and a non-empty bank.example.label.
2. time curl -s -X POST localhost:8000/api/plan -H 'X-Learner: a:v2revplanacc1' -H 'X-Tz: 0' -H 'content-type: application/json' -d '{"current":520,"target":700,"exam_date":"2026-11-07","minutes":45,"days":"1111100","tests":"weekly","test_size":"module","focus":{"Geometry and Trigonometry":"focus","Algebra":"strong"}}' returns 200 in under 1 s with active.id set. In days: 2026-11-07 is 'exam', 2026-11-06 is 'eve', every Saturday and Sunday is 'rest', each full Mon-Sun week before Nov 2 has exactly one 'test' on its Friday, and the week of Nov 2 has its test on Thursday 2026-11-05.
3. POST /api/plan/preview with that body gives split['Geometry and Trigonometry'] > 0.15 and split['Algebra'] < 0.35, the shares sum to 1 ± 0.01, target_note.points_pct is 88 and route_right is 14, and preview for target 800 has target_note.capped true.
4. Across GET /api/plan/day/{d} for the next 20 practice days, Geometry and Trigonometry topics fill more slots than Problem-Solving and Data Analysis topics, and no topic appears on 3 practice days in a row. With Advanced Math on focus and minutes 120, all 20 days return focus tasks (the fallback holds).
5. POST /api/plan returns 422 for each of: target 190; target 500 with current 520; exam_date yesterday; exam_date '2026-02-30'; days '0000000'; three domains on focus; tests 'hourly'; off [['2026-10-10','2026-10-01']]; a custom task titled with 61 characters.
6. PUT /api/plan/draft {step:3, fields:{minutes:90}}, then GET /api/plan, gives draft.step == 3, and the landing (shot.py at 1280) shows 'Continue' and 'step 3 of 4'. A POST /api/plan that returns 422 leaves the draft unchanged.
7. Take today.tasks' focus task and POST its start.path with start.body: GET /api/plan shows it 'active' with answered/total. Answer its full planned count without calling finish, and GET shows it 'done'. Call finish and the response carries plan.next.
8. After a learner finishes a whole module test with no ms sent, /api/me days.recent[-1].minutes >= 1.
9. In test_flow: backdate a plan's start by 3 days in sqlite and GET /api/plan: plan_days has rows for those 3 days. PATCH {minutes:90} leaves those rows' minutes unchanged, and today's Day.minutes becomes 90.
10. A past planned day with no study has status 'missed'. Starting its catch-up task (task=<that date>:focus) and finishing it turns that day 'made_up', and stats.made_up is 1.
11. POST /api/plan/{id}/tasks {day: today, title: 'Reading & Writing', minutes: 30} shows the task in today.tasks with kind 'custom'. PATCH it {day: today, status: 'done'} raises today's minutes_done by 30. PATCH {status: 'todo'} undoes it. DELETE removes it.
12. A repeating custom task {repeat: 'study_days', title: 'R&W', minutes: 30} appears on every study day in the next 14 days and on no rest day, and each such Day.minutes grows by 30.
13. PATCH today's focus task {day: today, status: 'skipped'} gives status 'skipped', and the page row has opacity 0.55 and the text 'Skipped'. PATCH {status: 'todo'} restores it.
14. PATCH today's focus task {day: today, to: <next study day>} marks today's row 'moved' with moved_to set, and that day's planned minutes grow by the task's minutes.
15. PUT /api/plan/{id}/day/{today} {off: true} makes today 'off', and the next practice day's focus topics include today's former topics. DELETE the override and today returns to 'practice'.
16. A plan whose start is backdated 8 days, with no study, returns behind.suggest_minutes >= 15. PATCH {minutes: behind.suggest_minutes} then changes Day.minutes for today onward only.
17. A learner on a '1111100' plan who studied on Friday and Monday, with nothing on Saturday and Sunday, has stats.streak == 2, and /api/today days.streak == 2.
18. curl GET /api/plan/{id}/ics with the learner header returns text/calendar containing 'BEGIN:VCALENDAR', one 'BEGIN:VEVENT' per study day from today plus the exam and eve, 'DTSTART;VALUE=DATE:20261107' with 'SUMMARY:SAT', and at least one 'BEGIN:VALARM'. After POST /links {cal:true}, /cal/<token>.ics returns the same events with no header; after {cal:false} it returns 404.
19. After POST /links {view:true}, GET /api/plan/shared/<token> with no X-Learner returns days and stats, and the body contains neither the learner code nor any start body. After {view:false} it returns 404.
20. After a module sitting whose band midpoint is 60 above the plan's current, GET /api/plan returns suggest.kind 'up'. POST /drift {dismiss} clears it. Two sittings averaging above the target give suggest.kind 'target'.
21. At 390px, document.documentElement.scrollWidth <= 390 on the landing, on each wizard step (?setup=1&step=1..4), and on each tab (?tab=plan|progress|plans), for learners a:v2revplanacc1 (new) and a:v2revshellhist (history).
22. At 390px the wizard shows 'Step 2 of 4 · Where you're going' as text. The WeekdayTiles read 'Mon'...'Sun', each with STUDY or REST, and every study tile contains a select. Calendar cells show their minutes text.
23. In step 4 with two domains on Focus, the page contains the visible text '2 focus areas at most' (not only a title attribute), and the third domain's Focus button is disabled.
24. Toggling Geometry & Trig to Focus in step 4 grows its SplitBar segment within 400ms, with no reload.
25. ?tab=progress renders an svg in the StudyTimeChart and a table inside it. The DomainCard rows are in ascending order of % right, and 'All 19 skills' expands to 19 rows.
26. With the exam date backdated to yesterday, GET /api/plan gives state 'after', the page shows the result form, and POST /api/plan/{id}/result {math:690} makes the Plans tab tag 'Finished · 690'.
27. With a plan active, Today (/) shows the first undone task's title from /api/today.plan, and its 'N of M done' equals the Plan tab's.
28. In the calendar, focus today's cell and press ArrowRight: the next day's cell gets aria-pressed=true and the DayPanel kicker changes to that date.
29. Create a second plan: the first shows under Plans as Archived. POST /api/plan/{first}/activate makes it active again, GET /api/me profile.exam_date equals its exam_date, and ?id=<second> shows the 'You are viewing an older plan' banner with both buttons.
30. Setting sessionStorage satf.return to '//evil.example' and opening a report shows no 'Back to your plan'. '/plan/?setup=1&step=1' shows it.
31. PYTHONPATH=. python3 server/test_flow.py passes, and python3 -m server.plan (the __main__ self-check) passes.

### 3.6.9 This section's open questions

Folded into Part 5 where they need a decision; kept here for context.

- PaceTag thresholds (Steady up to 15 points a week, Ambitious 15-30, Very ambitious above 30) are a heuristic with no source. One candidate anchor is the College Board / Khan Academy finding that about 20 hours of Official SAT Practice goes with about a 115-point average total gain. It is correlational and for the total score, not Math. Use that, keep the thresholds and call them a heuristic in the README, or show the numbers with no tag?
- MATH_MEAN for the average tick: 505 is the class-of-2024 annual report figure. Confirm the newest published figure before shipping.
- SAT dates: our SAT_DATES has 2027-03-13, but their exam-date select lists Mar 6, 2027. Check the College Board's published 2026-27 calendar and fix whichever is wrong.
- The test-day checklist wording should be checked against the College Board's current Bluebook test-day page (admission ticket, allowed calculators).
- server/mail.py already sends signup verification. Should verified students get an optional daily email of today's tasks, beyond the calendar feed, or is that out of scope?
- Is the read-only share link acceptable privacy-wise? It shows scores, mistake labels and adherence to anyone holding the link. Proposed: yes, off by default and revocable.
- Manual 'Mark done' on a generated task: proposed to count toward the day's status and minutes, but not toward question stats or mastery. Agree?
- Downward drift: offer to lower the starting score (proposed, since it makes the pace honest), or stay upward-only like theirs?

---

## 3.7 Compete: contests, rankings, leaderboards

> **Spec title:** Contests, rankings and leaderboards (Compete)  
> **Built by:** S8 (pages and server), S4 and S5 (contest mode inside the runners)  
> **Read with resolutions:** R1, R3, R4, R12, R16, R25, R27, R28 (§2.2). Where this spec disagrees with them, they win.

### 3.7.1 What they have

- **Three sidebar sections for competition**: Contests & Challenges (/contest-challenge), Contests Rankings (/contest-rankings) and Leaderboards (/leaderboard), all in the main sidebar nav.
- **Contests & Challenges: Global Leaderboard card**: Card titled GLOBAL LEADERBOARD with a 'Rankings >' link. Empty state: 'No rankings yet. Finish a contest to be the first on the board.'
- **Contests & Challenges: Your Contest Stats card**: Trophy icon. Empty state: 'Not ranked yet / Finish your first contest to get a global rank.' So the card holds your global rank.
- **Contests & Challenges: active contests list**: A full-width list of active contests. Empty state: trophy, 'No active contests right now / New challenges are posted regularly. Check back soon.' Contests are posted by hand, and the list was empty on both walks.
- **Contest types**: From the bundle: Daily, Weekly and Seasonal contests.
- **Contest tiers by plan**: The free tier gets no contests (the subscription table shows '—'). Pro gets free and standard paid contests. Elite also gets Elite-only prize contests.
- **Contest scoring rule**: From the bundle: 'Correct answers earn points by difficulty, plus a speed bonus based on the time you spend on each question.'
- **Contest integrity rules**: From the bundle: 'The contest runs in fullscreen. Switching tabs, leaving fullscreen, copying or pasting voids the answer to the question you're on.'
- **One attempt and a delayed reveal**: From the bundle: 'One attempt per contest. Answers are revealed after the contest ends.'
- **Resume limit**: Resumes are counted. Going over the limit scores the attempt 0: 'This attempt was scored 0 because the resume limit was exceeded'.
- **Per-contest stats**: Score / Correct / Incorrect / Skipped / Voided. So skipping exists, and so do voided answers.
- **Anonymous names**: Some boards show 'Anonymous student' instead of a username.
- **Contest Rankings: Performance Summary card**: Empty state with a 'Browse contests' button.
- **Contest Rankings: Contest Leaderboard card**: 'Pick a contest you've finished to see how you placed.' A picker of your finished contests opens that contest's board.
- **Contest Rankings: Your Rankings card**: Two rows: globe icon 'Global rank', medal icon 'Contests played'.
- **Contest Rankings: Time Analysis card**: 'Average seconds per answered question, by difficulty', drawn as a chart. The bundle also has 'under pressure' time analysis copy.
- **Contest Rankings: Badge Progress card**: Progress toward badges. It was empty when seen.
- **Contest Rankings: Your Contest History card**: A list of the contests you've sat. It was empty when seen.
- **Contest Rankings layout**: A two-column grid of the six cards above.
- **Leaderboard hero with podium**: A centred 'Leaderboard' title, 'See how you stack up… globally and in your country.', and a large space for a top-3 podium.
- **Leaderboard period control**: Segmented Weekly / Monthly (the default) / Yearly.
- **Leaderboard scope select**: Global, switchable to your country.
- **Leaderboard metric control**: Segmented Contest Points | Overall Score (the default).
- **Leaderboard table**: Columns RANK / USERNAME / ACCURACY / TIME. Footer 'No more rankings yet.' It pages or scrolls without end. Every period was empty.
- **Profile Performance Snapshot**: Global Rank (e.g. 128) and Country Rank (e.g. 43) on /profile. Both showed values with no contests played.
- **Profile Achievements**: Four hard-coded badge tiles: 7-Day Streak / 1000 Solved / Consistency / Top Rank. They show no progress and no earned state. 'View All' has no handler.
- **Ranked vs not ranked on the score report**: The report carries a pill 'Practice test — not ranked'. For ranked sittings (from the bundle) it shows a percentile: 'N% scored at or below you on their {first} attempt.' A sitting is ranked when it is a first attempt.
- **Username on boards**: The board shows a username. The account name comes from Google sign-in.
- **Question of the Day (two a day)**: One R&W and one Math on the dashboard, each opened by 'Answer' into a modal. The stem uses KaTeX and choices are full-width rows. 'Check answer' is disabled until you pick. After checking: an Incorrect/Correct banner and a 'Show explanation' link. The correct choice is NOT highlighted, and the primary button becomes 'Done'. There is a 'More practice' text button. One attempt a day, and a '1 day' streak pill.
- **Classes and homework (hidden)**: /my-classes ('Pick a class to see its homework'), assignments run as a full practice test or a question-bank session, with a time limit, due dates, 'Attach file' and [Finish Homework]. A /teacher dashboard creates classes, adds students and assigns work. None of it is in the sidebar.
- **Share**: 'Share' calls navigator.share (the OS share sheet), which froze the page in Dia. A shared QBank session gets its own landing page with 'Start Practice'.
- **Nothing is live without staff**: Contests are posted by hand ('posted regularly'), so the whole section can be empty, and it was on both walks.

### 3.7.2 What we have now

Status is have / partial / missing / worse, against theirs.

- **Daily challenge**: *have.* Ten questions a day, the same for everyone: 3 easy, 4 medium, 3 hard over 3/3/2/2 domains, grid-ins at 4 and 8, stored once in `challenges`. One sitting per learner per local day, resumable, run in the practice session with the key and rationale after each answer and no repairs.
- **Contest kinds (weekly, seasonal, private)**: *missing.* The daily challenge is the only competition. There is no weekly, seasonal, sprint or private contest, and no list of contests.
- **Challenge board**: *partial.* /challenge/ shows rank, name, right/asked and time for Today or Yesterday only: the top 100 plus your row, highlighted. There is no accuracy column, no paging, no other days and no scopes.
- **Board time**: *worse.* daily.board ranks on finished − started, so reading rationales and the pause before Finish count against you. The session summary shows the sum of the client-sent ms instead. Seen live: '7 min' on the summary and '0:00' on the board for the same sitting.
- **Clock charges reading time**: *worse.* The practice session's countdown is a wall clock from `started`, so reading the key and rationale after each answer eats the 16 minutes. The one thing we do better than them (the key after each answer) costs time in a challenge.
- **Ties**: *worse.* The sort is (-right, seconds, finished) and ranks are handed out 1..n, so equal scores get different ranks. Seen today: three players on 2/10 in 0:00 were ranked 1, 2 and 3.
- **Clock length**: *worse.* GET /api/challenge says 950 s (10 × 95). drill.seconds_of gives 954 s, because 10 × 2100 // 22 is computed as 21000 // 22.
- **Leaving a challenge**: *worse.* In the practice session, X calls finish() once one question is answered. Leaving hands the challenge in with the rest blank, and there is no warning.
- **Skip**: *missing.* You can't move on without answering. Theirs has Skipped in its contest stats.
- **Integrity**: *worse.* The questions are identical, the key is shown after each answer, and learner codes are free to mint (a private window is a new player). So anyone can harvest today's ten keys on a throwaway code. X-Tz is client-controlled (−840..720), so tomorrow's ten can be sat early. There is no too-fast check and no tab-leave or copy rule. Theirs voids the open question on a tab switch, copy or paste.
- **Points (difficulty and speed)**: *missing.* Ranking is right answers then seconds. There are no points by difficulty and no speed or pace bonus.
- **Global leaderboard (week/month/year)**: *missing.* No board spans more than one day.
- **Scope (global/country)**: *missing.* There is one global list. There is no country field and no groups.
- **Metric switch (points vs overall)**: *missing.* There are no points, no rating, no effort metric and no test-score metric.
- **Podium**: *missing.* None.
- **Your contest stats / performance summary**: *partial.* Only today's rank, shown in the /challenge/ header and on Today's Challenge card. There are no totals, bests, averages or global rank.
- **Per-contest breakdown (right / wrong / skipped / voided)**: *partial.* Only right/asked.
- **Contest picker (how you placed in a finished contest)**: *partial.* The Today/Yesterday toggle is the only way to see an older board.
- **Global rank, country rank, contests played**: *missing.* None.
- **Time analysis by difficulty**: *missing.* attempts.ms exists but is client-sent. It is shown only as a session's total minutes on the summary.
- **Badges / achievements**: *missing.* None, anywhere.
- **Contest history**: *partial.* Challenge sittings appear in the Results list as 'Challenge' rows with the score only. No rank, no field size and no link to that day's board.
- **Review of the challenge's questions**: *missing.* The session summary lists topics and mistakes, but you can't go back to the ten questions. There are no crowd stats per question.
- **Profile rank snapshot and achievements**: *missing.* /me/ holds only a name and the device code.
- **Ranked vs unranked label, test percentile**: *missing.* There is no idea of unranked, ghost, voided or flagged sittings. The score report has no percentile.
- **Board name**: *worse.* The name form appears only after finishing, or on /me/. NAME_OK (^[^\d<>@]{1,60}$) rejects digits, so 'mike2027' can't be used. Names aren't unique and can't be reported. There is no way to stay off public boards. The default name is 'Student 1A2B'. The after-finish name prompt is good and has to survive the rebuild.
- **Anonymous listing**: *missing.* Every row shows a name.
- **Classes / homework equivalent**: *missing.* No groups, no assigned sets, no due dates and no teacher view.
- **Navigation**: *worse.* The challenge isn't in NAV at all (SECTION maps challenge → today). It is reachable only from Today's card.
- **Question of the day**: *have.* One Math MCQ, answered inline on Today, one attempt. It shows the key, the misconception the chosen option names, the rationale and '% of N right', which is better feedback than theirs. Missing: the spread of picks per option, 'another like this', past days and a QOTD streak. A past day's answer is refused (409).
- **Duplicate sittings after a device carry**: *worse.* progress.carry leaves two sittings of one day under one code, and the board shows both (a known edge with a ponytail comment).
- **Twin generation**: *partial.* blueprint.draw_matching and per-learner seed starts (crc32(learner:template)) already make per-student variants possible. But Builder dedupes on the stem hash. 93 of 386 templates repeat their stem text within 40 seeds (lat.isosceles_cross, lat.three_lines_triangle and lat.vertical_isosceles have one stem each, with the numbers in the figure and choices). Such a template reads as spent for a learner after one sighting. Only similar.area repeats whole questions (23 distinct of 40).
- **Always something to do**: *have.* The daily challenge makes itself from the date, so it is never empty. Theirs was empty.

### 3.7.3 Design

#### Compete: contests, rankings and leaderboards

##### Review changes

What I changed in the proposed spec, and why.

1. **Seasonal contests were missing.** Theirs has Daily / Weekly / Seasonal (bundle). Added:
   - **Seasons** that run between official SAT dates ("Road to Oct 3");
   - a Season period on the leaderboard, a Season card on the Overview, and a Seasons table and season badges on Your rankings;
   - a **Season Final**: a full adaptive Math section in the test window on the weekend one week before each SAT date. It takes the place of that weekend's Weekly Module.
2. **Their per-contest stats had been reduced to a score.** Theirs: Score / Correct / Incorrect / Skipped / Voided. The result panel, review filters, history, Compare and the owner's results table now all carry Right / Wrong / Skipped / Voided. That needs two runner features the spec lacked, **Skip** and **voiding**, and both are added.
3. **Their integrity rules had no equivalent**: fullscreen, and a tab switch, copy or paste voiding the open question. Added:
   - an optional fullscreen button;
   - the open question is voided after 5 s away or on copy/cut/paste (theirs voids at once, with no grace);
   - a banner the first time a question is voided;
   - voided counts shown everywhere.

   Theirs zeroes a sitting that goes over its resume limit. Ours never zeroes one: leaving through X skips the open question and stops the clock.
4. **The clock charged reading time, which contradicted the spec's own §1.2.** Answer time excluded rationale reading, but the 16-minute wall clock kept running while you read. It is replaced with a server-side **answer clock** that runs only while a question is open. Reading the key and the rationale is free for both the clock and the rank.
5. **Speed bonus.** Theirs adds points for speed. Added a **pace bonus**: +5 for each right answer given within SAT pace (95 s), and nothing extra for going faster. It rewards the real test's pace, not rushing. The Daily's maximum goes from 210 to 260.
6. **The Daily could still be harvested** (identical ten, key after each answer, free codes, a client-set X-Tz). The Daily is now **twins by default**: everyone gets the same template, difficulty and format at each position, with their own numbers. Past identical days stay identical. The question of the day stays identical, since it is not ranked. This is left as an open question to confirm.
7. **Twins could not work as written.** I sampled all 386 templates at 40 seeds:
   - 93 repeat their stem text; three have a single stem, with the numbers living in the figure and the choices;
   - Builder's stem-hash rule marks such a template spent for a learner after one sighting, so twins would quietly fall back to other templates;
   - only similar.area repeats whole questions (23 distinct of 40).

   Twins now dedupe on the whole question, skip a (template, seed) another entrant already got, and take only templates that show ≥ 15 distinct questions in 18 surveyed seeds. The acceptance check compares whole questions, not seeds.
8. **Weekly storage was wrong.** `sessions.module1` holds module 1's mark, not its questions. A module sitting keeps its questions as `{"module1": [...]}` in `sessions.questions`. Also, the test window sends no per-question time, so weekly/final per-question times read "—" until the test-window section adds dwell time (a shared need).
9. **Hidden students changed everyone else's rank.** Removing `public=0` rows from other viewers' boards shifted the rank of everyone below them. Hidden students now keep their place and show as **Anonymous** (theirs: "Anonymous student"), with no row menu.
10. **The country scope had been dropped.** Theirs: Global ↔ Country, and a Country Rank on the profile. Added an optional country on Me (blank by default, suggested from the browser's language region), a Country scope, and a country rank in every snapshot. Groups and Near me stay.
11. **Their "Overall Score" had no equivalent.** Added:
    - a **Test score** metric: the best timed full-section Math estimate in the period;
    - on the score report, the Ranked / Not ranked pill and a **percentile** (theirs: "N% scored at or below you", ranked sittings only).
12. **Global rank was missing from the hub's stats card.** Theirs' Your Contest Stats *is* the global rank. Added all-time rank, country rank and the challenge streak.
13. **The name prompt after finishing had been dropped.** Today's /challenge/ asks for a name after your first finish, but the spec only had it on Me. It is back on the result panel.
14. **The contest summary could have lost the practice summary's study value.** It now says outright that it keeps the topic mastery bars and the mistakes opened and closed.
15. **Orange on the podium's first place clashed with orange = yours** (your row, your marks). The podium now uses tiles and heights, and only your own card gets orange.
16. **Classes and homework** (hidden in theirs, with a teacher dashboard) had no equivalent. A group owner can now give the group a private contest with a due time. Members see it with the due time on Compete and Today, and the owner gets a results table with per-question marks and Copy / Download CSV.
17. **Server gaps fixed:**
    - no server secret existed for the pid HMAC, so a `kv` table now holds one;
    - `learners` rows only exist after PUT /api/me, so compete upserts one;
    - contest and group codes now share one namespace;
    - a sprint start returns the open run instead of being idempotent forever;
    - name reports count only from codes with a finished ranked sitting, since otherwise anyone could mint three codes and reset a name;
    - default-looking and reserved names are refused;
    - the Final ranks on points and shows the estimate band, because `scoring.section_score` returns a band, not a point.
18. **The Weekly window** moved from UTC to the student's own local Saturday and Sunday, like the Daily. Twins make local windows fair, and this closes an open question.
19. **Extras added:**
    - time under pressure, and time on right vs wrong answers, in Pace;
    - a rating chart;
    - **Compare** with another student on a contest;
    - a domain filter on the leaderboard;
    - a daily reminder as a repeating calendar file;
    - a challenge streak and a 30-day strip of dailies;
    - a "sitting now" count;
    - the Daily Challenge and Weekly Module as Plan tasks (a shared need).
20. **Copy trimmed** where it narrated a control (for example, the Private empty state). Rules, legends, counts and units are kept.

---

TopTierPrep splits competition over three sidebar pages (Contests & Challenges, Contest Rankings, Leaderboard). All three were empty on both walks: staff post contests by hand, and plans gate them. Ours is one **Compete** section: the sixth nav item, four pages, and one contest model that schedules itself. Something is always live, everything is free, and every student is ranked by the same rules.

| theirs | ours |
|---|---|
| Contests & Challenges | **Overview** `/compete/` |
| a contest (never seen live) + the "Contest Leaderboard" picker | **Contest page** `/compete/contest/?id=…` (lobby, result, board, review, the field's traps, Compare) |
| Leaderboard | **Leaderboard** `/compete/leaderboard/` |
| Contest Rankings + Profile Performance Snapshot + Achievements | **Your rankings** `/compete/rankings/`, plus a Boards block on `/me/` |
| Daily / Weekly / Seasonal contests | Daily Challenge, Sprint, Weekly Module, Seasons + Season Final, Private |
| Classes & homework (hidden) | Groups, with group contests that have a due time and an owner results table |
| "Practice test — not ranked" + percentile on the report | Ranked / Not ranked pill + percentile on the report (§9) |

**Copy rule for this section:** headings, legends, counts, units and one-line rules are wanted. Nothing narrates a control. No illustrations and no marketing lines. Every number on a board says what it is.

---

##### 1. The contest model (everything below renders this)

###### 1.1 Kinds

| | Daily Challenge | Sprint | Weekly Module | Season Final | Private |
|---|---|---|---|---|---|
| id | `daily-2026-09-23` | `sprint-2026-W39` | `weekly-2026-W39` | `final-2026-10-03` | `p-` + 10 base32 chars |
| window | your own local calendar day (X-Tz); closes everywhere D+1 12:00 UTC | Mon 00:00 UTC → next Mon 00:00 UTC; always live | your local Sat 00:00 → Sun 23:59 of the ISO week; closes everywhere Mon 12:00 UTC | your local Sat–Sun, 7 days before the SAT date | from creation, for 1 h / 24 h / 3 days / 7 days; a group contest runs until its due time |
| questions | 10: 3E 4M 3H, domains 3/3/2/2, grid-ins at 4 and 8 | as many as you answer, from a 60-slot sequence in the week's theme domain | 22 on the module-1 blueprint: 7E 8M 7H, domains 8/7/4/3, grid-ins at 6, 7, 13, 14, 21, 22 | 44: module 1 as Weekly, then module 2 lower or upper, routed by module 1 | 5 / 10 / 15 / 22 over the creator's skills, difficulty and format |
| clock | answer clock 950 s (15:50) | answer clock 5:00 | wall clock 35:00 | wall clock 35:00 per module | answer clock: auto (95 s a question) or 5–70 min |
| runner | practice session | practice session, sprint mode | test window | test window | practice session |
| questions per student | twins | twins | twins | twins, per route | creator: same for everyone (default) or twins |
| key shown | after each question | after each question (short verdict) | at hand-in | at hand-in | creator: after each question (default) or at the end |
| skip | yes | yes | move freely, as in a test | move freely | yes |
| voiding | on | on | on | on | creator's "Strict" switch (off by default) |
| ranked sitting | your first sitting that day | every run; your best run counts | your first sitting in the window | your first sitting | each member's first sitting in the window |
| board order | points ↓, answer time ↑ | best-run points ↓, right ↓, answer time ↑ | points ↓, time used ↑ | points ↓, time used ↑ (the estimate band is shown) | points ↓, answer time ↑ |
| rated | yes | yes | yes | yes | no |
| season points | yes | best run of each week | yes | yes | no |

**Twin questions** are something only our bank can do. A twin contest stores a canonical slot list `[template, tier, fmt]`. It is drawn once from the contest id (`Builder(f"contest:{id}")` + `blueprint.fill`), and `fmt` is taken from the canonical card itself, not from what the slot asked for. Each student gets that slot's template, at that tier and format, on a seed of their own, which the per-learner seed start already gives. Three rules keep the numbers truly different:

- A twin is deduplicated on the **whole question** (stem, choices, figure, table), not the stem. 93 of the 386 templates keep the same stem text across seeds.
- A (template, seed) that another entrant of the same contest already got is skipped (`contest_items`).
- A slot only takes templates that showed **≥ 15 distinct questions in 18 surveyed seeds**. Today only similar.area fails this.

If a student's history has used a template up, the slot falls back to a template of the same topic, tier and format, same skill first. Field statistics for a slot are grouped by misconception, so a fallback still counts. Everyone faces the same skills, traps and difficulty with different numbers. So the key can be shown at once, answers can't be passed on, and retakes and ghost sittings are fair.

**Sprint theme** rotates on the ISO week number mod 4: 0 Algebra, 1 Advanced Math, 2 Problem-Solving & Data Analysis, 3 Geometry & Trigonometry. The 60 slots run easy for 1–4, medium for 5–12, then alternate medium and hard. Templates go round-robin through the domain's templates, ordered by `sha256(week + template)`.

**Seasons.**
- A season runs from the day after one official SAT date through the next one (UTC days), and is named for its end: "Road to Oct 3".
- The dates are one constant in `compete.py`, shared with Plan and with Today's exam-date picker: 2026-08-22, 2026-09-12, 2026-10-03, 2026-11-07, 2026-12-05, 2027-03-06, 2027-05-01, 2027-06-05.
- **Season points** = the points of every ranked contest finished in the window. A Sprint counts its best run of each week. Private contests don't count.
- When a season closes, its standings are stored and the season badges are awarded.
- The **Season Final** is the dress rehearsal: a timed, adaptive, full Math section on the weekend one week before the SAT date, against everyone else sitting it.

###### 1.2 How it's ranked (shown on every lobby as a list)

- **Points:**
  - 10 for each easy, 20 for each medium and 30 for each hard question answered right.
  - **Pace bonus:** +5 for each right answer given within 95 s (answer-clock kinds except Sprint).
  - **Finish bonus:** +10 for answering every question with none skipped or voided (not Sprint).
  - Maximums: Daily 260; Weekly 450; Final 440 + module 2 (lower 360, upper 520) + 10.
- **The answer clock** (Daily, Sprint, Private):
  - It runs only while a question is open, from the moment the server serves it to the moment it receives your answer.
  - Reading the key and the rationale is free.
  - When the clock hits 0, the open question scores 0 and the sitting ends.
  - A board's "answer time" is the clock you used.
  - Test-window kinds use a wall clock, like the real test, and rank on time used from start to hand-in.
- **Skip** scores 0. The key and rationale show at once, and no mistake is opened. It counts as Skipped.
- **Leaving** through X while a question is open skips that question. Leaving from a verdict just leaves. Either way the clock stops until you come back.
- **Voids** (ranked sittings):
  - A question is voided when the tab is hidden for 5 s or more, or text is copied, cut or pasted, while it is open.
  - You can still answer it, and it still shows its key and rationale and goes on your map.
  - It scores 0 and doesn't move your rating. It counts as Voided.
- **Ties:** equal points and equal answer time share a rank, shown `=4`, and the next distinct score takes rank 6 (competition ranking). Within a tie, the earlier finisher is listed first.
- **Top %** = `ceil(rank / ranked players × 100)`, shown only when there are ≥ 10 ranked players.
- **Ranked / Unranked:** every result, board row and history row says which. A sitting is Unranked when it is:
  - a **ghost** sitting of a closed contest or a past day ("Would have placed #6 of 37");
  - a **repeat**: a second sitting of one contest, which can arrive with a device-code carry;
  - **too fast**:
    - answer-clock kinds: a median answer time under 4 s with at least half right;
    - test window: under 20 s a question on average with at least half right;
    - shown as "Not ranked: answers came in faster than the questions can be read."
- **Rating and level:**
  - Each answer in a ranked, rated sitting (first attempt, not voided) moves your rating against that question's own rating: Elo against the item.
  - Each (template, tier) has a rating that calibrates from everyone's rated answers.
  - Students start at 1000 and show as **Placing** until they have 30 rated answers.
  - Levels 1–10 use the ladder in spec/rating.md (≤800, 801–950, 951–1100, …, 2001+).
  - The badge is the brand mark's ring, filled in ten steps, with the level digit in the counter. Placing is an empty ring with "–". Level 10 is a solid orange rounded square with "10".
  - Badge sizes: 20 px in tables, 32 px in cards, 48 px in stat cards.

---

##### 2. Shell changes
- `NAV` gains **Compete** `/compete/` (trophy icon), sixth, after Results.
  - Desktop bar: Today · Practice · Tests · Plan · Results · Compete.
  - Phone tabs: `repeat(6, 1fr)`, 65 px each at 390, labels still 10.5 px.
- `SECTION`:
  - `compete`, `contest`, `leaderboard` and `rankings` map to `compete`, and the old `challenge` entry goes;
  - `UI.shell(pageOverride)` lets the practice session and the test window highlight Compete once their state says it is a contest sitting.
- `/challenge/` becomes a server 307 to `/compete/contest/?id=daily`. `daily` resolves to today's local id through X-Tz, and `web/challenge/` is deleted.
- **Compete sub-nav** on Overview, Leaderboard and Your rankings: three underline links under the H1, "Overview · Leaderboard · Your rankings", in `.choices` style with `aria-current="page"`. The contest page has a back link, "‹ Compete", instead.

---

##### 3. Overview `/compete/` (theirs: Contests & Challenges)

**Desktop 1280.**
- H1 "Compete" on the left.
- On the right, two quiet buttons: "Join with a code" and "+ Create a contest".
- Then the sub-nav, then a grid: main column `minmax(0, 2fr)`, side column `minmax(0, 1fr)`, gap 20.

###### Main column

**A. Daily Challenge card** (wash ground, radius 14, padding 26)
- Top line: `k` "DAILY CHALLENGE · WED, SEP 23" on the left. On the right, `meta` "Next one in 07:14:22", a live countdown to local midnight (each second, `aria-live="off"`).
- **Ladder:** ten cells in a row (each `1fr`, 64 px tall, paper tiles).
  - Each cell holds the number (mono 11), the domain glyph (20 px) and difficulty pips (1–3 ink dots). Cells 4 and 8 carry a `grid-in` tag.
  - Legend: "● easy  ●● medium  ●●● hard · grid-in: you type the answer".
  - Hover or focus on a cell shows "Q4 · Algebra · Medium · grid-in". The questions themselves are never shown.
- Facts line: "10 questions · 15:50 answer clock · one sitting · ranked".
- Field line: "37 finished · 6 sitting now · median 170 pts · best 245", or "No one has finished yet."
- Your line: "Challenge streak 5 days" (best in `meta`: "best 12").
- Status block, by state:
  - *Not started*: pill "Start the challenge". Rule line: "The clock runs only while a question is open. Skipped and voided questions score 0."
  - *In progress*: pill "Resume" + `meta` "4 of 10 answered · 9:12 on the clock".
  - *Finished*:
    - Result line: "#4 of 37 · top 11% · 8/10 · 170 pts · 11:42".
    - Ten mini squares: orange = right, graphite = wrong, dotted outline = skipped, slashed = voided. Each links to `…/contest/?id=daily-…#q3`.
    - Rating chip "+14 → 1,084 · Level 3".
    - Buttons: pill "See the board"; quiet "Review answers", "Copy result".
  - *Finished, unranked*: the same, with an "Unranked" chip and the reason line.
- Footer: "Past days ›" (yesterday's contest page) · "Daily reminder" (sheet, below).

**B. Contests**
- Heading row: `h2` "Contests" + an underline filter: Live (n) · Upcoming (n) · Finished (n) · Private (n). The default is Live.
- Row (tile, radius 10, padding 16 18), grid `28px minmax(0,1fr) auto auto`:
  - **Kind icon:** sprint = bolt, weekly = module sheet, final = flag, daily = trophy, private = two people.
  - **Title:** "Sprint · Advanced Math week", "Weekly Module · Week 39", "Season Final · Road to Oct 3", "Period 3 quiz · Ms. Lee's group".
  - **Window line:** Live "Ends Mon 3:00 AM · in 4d 06h" · Upcoming "Opens Sat 12:00 AM · in 2d 11h" · Finished "Ended Mon 3:00 AM" · group "Due Fri 5:00 PM · in 2d". All times are local.
  - **Facts:** "22 questions · 35 min · your own twin questions · 128 in".
  - **Status chip** (tile-2 ground): "Not entered" · "In progress · 12:40 left" · "Finished · #12 of 128 · top 10%" · "Best 240 pts · 3 runs" (sprint) · "Final · #9 of 131".
  - **Action** (quiet): "Start" / "Resume" / "Results" / "Add to calendar" (upcoming only; downloads an `.ics` built in the page).
- Empty states:
  - Live and Upcoming are never empty: Daily and Sprint are always live, and the next Weekly (or Final) and the next Sprint are always upcoming.
  - Finished: "No finished contests yet."
  - Private: "No private contests yet." + quiet "+ Create a contest" + quiet "Join with a code".
- Finished shows 10 rows, then "Show 10 more".

**C. Question of the day strip** (tile, one row): `k` "QUESTION OF THE DAY".
- Unanswered: "Not answered yet" + quiet "Answer it on Today ›".
- Right: "Right · 61% of 212 got it · 5-day streak".
- Wrong: "Fell for: {misconception}".
- Quiet "This day ›" opens the day's contest page, which holds the QOTD panel.

###### Side column

**D. Your stats** (tile; theirs: Your Contest Stats)
- Level badge (48) + rating (`num` 32) "1,084" + "Level 3", or "Placing · 12 of 30 rated answers".
- 2×3 stat tiles: "Week rank #12 of 340" · "All-time rank #210 of 1,284" · "Country #14 of 96" (or "Set a country on Me") · "Points this week 620" · "Contests 14" · "Best finish #2 · Sep 19".
- Link "Your rankings ›".
- New student: an empty badge, "—" tiles, and "Finish a ranked contest to get a rank."

**H. Season** (tile)
- `k` "SEASON · ROAD TO OCT 3" + `meta` "10 days left", and a thin bar of the season's days elapsed.
- "#34 of 512 · top 7% · 1,240 pts".
- "Season Final · Sat Sep 26 – Sun Sep 27 · full Math section" + quiet "Add to calendar".
- Link "Season standings ›" goes to `/compete/leaderboard/?period=season`.
- New student: "Every ranked contest adds to your season points."

**E. Leaderboard preview** (tile)
- `k` "THIS WEEK · POINTS". Five rows: rank, name, 20 px level badge, points.
- If you're outside the top 5, a thin separator and then your row.
- Link "Full leaderboard ›". Empty: "No one has scored this week yet."

**F. Next badges** (tile)
- The three unearned badges you're closest to: icon, name, rule line, a progress bar and "5/7".
- Link "All badges ›" goes to `/compete/rankings/#badges`.

**G. Your groups** (tile)
- A row per group: name, member count, your week rank in it, and a "Due Fri" chip when the group has an open contest.
- Owners also get quiet "Set a contest".
- Quiet "Join with a code", quiet "Create a group".
- Empty: "Groups are private boards for a class or friends."

###### Phone 390
- One column in this order: A, D, H, B, E, C, F, G.
- The ladder becomes a 5×2 grid.
- The two header buttons collapse into one quiet "Join or create", which opens a sheet with both.
- The contest row stacks: icon + title/window on one line, then the facts, then the status chip and action on one line.
- No horizontal scroll anywhere.

###### Sheets (dialog.sheet)
- **Join with a code**: a 6-character field (uppercase, mono, `autocomplete=off`) and a pill "Join".
  - Errors: "No contest or group has that code." · "That contest has ended." + quiet "Sit it unranked".
  - A contest code goes to the contest page. A group code shows "You're in {group}." and the group appears in G.
- **Create a contest**: see §7.
- **Create a group**: a name field (3–40 chars) and "Create". The result shows the code large, with "Copy code" and "Copy link".
- **Daily reminder**: a time field (default 17:00) and a pill "Add to calendar". It downloads a repeating `.ics` (`RRULE:FREQ=DAILY`) titled "SAT Freshman · Daily Challenge" and linking to the contest page.

###### States
- Loading: skeleton tiles at their final sizes (grey ladder cells, 3 contest rows, 5 board lines), no spinners.
- Error: `.error` "The server is not answering." + quiet "Try again". Data from an earlier load stays on screen.

---

##### 4. Contest page `/compete/contest/?id=…` (theirs: a contest, plus "Contest Leaderboard")

###### Header (all states)
- Back link "‹ Compete".
- `k` kind: "DAILY CHALLENGE" / "SPRINT · ADVANCED MATH WEEK" / "WEEKLY MODULE" / "SEASON FINAL · ROAD TO OCT 3" / "PRIVATE CONTEST · by Ms. Lee".
- H1: the title (daily: "Wed, Sep 23").
- `meta` window: "Open until 11:59 PM your time" / "Sat 12:00 AM – Sun 11:59 PM" / "Due Fri 5:00 PM".
- Status chip: Upcoming / Live / Closed.
- **Daily only:**
  - Day navigation: "‹ Sep 22" · `<input type="date">` (min = the first stored day, max = today) · "Sep 24 ›" (disabled on today).
  - A **30-day strip**: one square per local day.
    - Orange = sat ranked, orange outline = sat as a ghost, grey = missed; today has an ink outline.
    - Each square links to its day. Legend: "sat · ghost · missed".

###### Body by state

**Upcoming**
- A big countdown: "Opens in 1d 04:12:09".
- The ladder or blueprint preview (as in §3A). Weekly shows 22 cells in two rows of 11. The Final shows module 1's 22 plus "Module 2 · 22 questions · easier or harder by your module 1".
- "How it's ranked" (the §1.2 list).
- Quiet "Add to calendar". Pill "Practice for it": a 10-question drill over the contest's domains.

**Live, not started**
- Rules, ladder, field line: "128 in · 6 sitting now · median 260 pts · best 410".
- Pill "Start".
- Private contests also show "Entrants (12)": a wrapped list of names with status dots (finished / in progress / not started).
- Weekly and Final: "Runs in the test window: move between questions, mark for review, hand in when ready. Answers and explanations appear at hand-in."

**In progress (you left)**
- Pill "Resume" + "4 of 10 answered · 9:12 on the clock".

**Finished (you): the result panel**
- Big rank `num` "#4" + "of 37" (with `=` when tied) · "Top 11%".
- Tiles:
  - Score "8/10"
  - Points "170", with the sub-line "120 + 40 pace + 10 finish"
  - Answer time "11:42"
  - Rating "+14 → 1,084" with a level badge (a level-up shows "Level 3 → 4")
- Breakdown line: "8 right · 1 wrong · 1 skipped · 0 voided".
- The practice summary's study value, kept:
  - one row per topic, with its mastery bar moving before → after and "right/asked";
  - the mistakes opened (orange dot + label) and closed (tick + label) in this sitting.
- New badges from this sitting, as small tiles.
- Answer strip: 10 (or 22, 44 or N) squares: orange = right, graphite = wrong, dotted outline = skipped, slashed = voided. Each jumps to its review item.
- **Name prompt** when you haven't chosen a name: "On the board as Student 1A2B" + the name field + "Save" (the §9 rules, inline errors).
- Actions: pill "See the board". Quiet: "Practice my misses" (the existing `from_session`), "Practice the field's traps", "Copy result", "Challenge a friend".
- Weekly adds "Module estimate 560–760" from `scoring.score`.
- The Final shows the section band from `scoring.section_score` as a big number pair, "610–750", with "Route: harder module 2", beside the rank.
- Sprint: "Best this week 240 pts (run 3 of 3)" and a pill "Run again". Every run draws fresh questions, and only your best run counts.

**Closed / past day, not sat**
- The board and the field's traps are visible.
- Pill "Sit it now (unranked)": "Twin questions, same skills. You'll see where you would have placed. It doesn't count for rank, rating or season points."
- After a ghost sitting the result panel reads "Would have placed #6 of 37".

###### Board section
- Heading `h2` "Board", `meta` "37 ranked · updated just now". While the contest is live and the tab is visible, it polls every 30 s.
- Scope underline: Everyone · Near me · Country · {each of your groups}.
- Table (`<table>`, `<th scope="col">`):
  - Daily and Private: Rank | Student | Score | Points | Answer time.
  - Sprint: Rank | Student | Best points | Right/answered | Runs.
  - Weekly: Rank | Student | Score | Points | Time used.
  - Final: Rank | Student | Band | Points | Time used.
  - The Student cell holds the name + a 20 px level badge. Hidden students show "Anonymous" in their real place. Ties show `=4`.
  - Your row: wash ground + amber inset edge + `aria-current="true"`, labelled "You".
  - Unranked sittings never appear. Your own unranked result shows as a line above the table: "Your sitting is unranked: {reason}."
- Paging: 50 rows, then "Show 50 more". At the end: "That's everyone: 37 students."
- **Sticky you-bar:** while your row is out of view (IntersectionObserver), a bar pinned above the phone tabs (bottom 0 on desktop) reads "You · #212 · 150 pts · Jump to me".
- **Row menu** (⋯, on named rows other than yours):
  - "Compare" (once you've finished too);
  - "Report name" (after 3 reports from different ranked players, the name resets to its default handle).
- **Compare sheet:**
  - "You vs {name}": two answer strips, one above the other, aligned by slot.
  - Per slot: "you 1:12 · them 0:58".
  - Totals: "Both right 6 · only you 2 · only them 1 · neither 1".
  - For twins, compared slot by slot.
- Empty: "No one has finished yet." Near me while you're unranked: "Finish this contest to see who's around you."

###### Review section (`#review`)
Gated: it opens once you've finished your sitting, or once the contest has closed everywhere (daily: D+1 12:00 UTC). Before that: "Answers open when you finish, or after the contest closes."
- Filter underline: All · Wrong (n) · Right (n) · Skipped (n) · Voided (n) · Hardest for the field (the 3 with the lowest field % right).
- Collapsed row per question: "Q3" · skill glyph + skill · pips · your mark (✓ orange / ✗ graphite / – skipped / ⊘ voided) · "field 62% right" · "you 1:12 · field median 1:34". Weekly and Final show "—" for times until the test window records per-question time.
- Expanded (`<details>`):
  - The question via `UI.question` in review mode (your pick, the key, struck wrong picks) + the rationale.
  - **How the field answered.**
    - Identical contests: one bar per option: "A 12%", "B 41%: Subtracted the constant terms instead of adding them", "C 38% · key", "D 9%: …".
    - Twin contests: one bar per misconception across all twins: "Fell for 'Swapped the columns…' 27%", "Right 58%", "Skipped / blank 10%", "Voided 5%".
  - Quiet "Another like this": a 5-question drill on that template with fresh seeds.

###### The field's traps
- `h2` "Where the field went wrong".
- The top 5 misconceptions in this contest: label, "% of the field fell for it", and your status ("you too" / "you avoided it" / "not in your questions").
- Pill "Practice these 5": a drill with those five templates queued twice each.

###### QOTD panel (daily only; side column on desktop, after Review on phone)
- That day's question of the day. If you answered it: your answer, the key, the rationale and the option spread.
- A past day you didn't answer can be answered: "Answer, unranked: it doesn't count for your streak".
- Below it, a 30-day strip of dots (right / wrong / not answered), each linking to its day.

###### Owner controls (private and group contests)
- The code, "Copy link", "Close now", "Extend 24 h", "Rename", "Delete". Every destructive control has a confirm sheet.
- The entrants list, with "Remove".
- **Results table** (the teacher view):
  - Columns: Student | Status | Score | Points | Time | Q1…Qn marks (✓ ✗ – ⊘).
  - A footer row with each question's % right.
  - Buttons: "Copy as CSV" and "Download CSV", both built in the page.

###### Layout
- Desktop: the header full width, then `2fr 1fr`.
  - Main: state panel → Board → Review → Traps.
  - Side: the rules card, the QOTD panel (daily), Entrants (private), owner controls (private).
  - The owner results table spans both columns under Board.
- Phone: one column: header, state panel, Board, Review, Traps, QOTD, rules.
  - The board keeps Rank | Student | Points, and the other columns become a `meta` line under the name: "8/10 · 11:42".
  - The owner results table scrolls inside its own box, with the Student column sticky.

###### Error and not-found
- Unknown id: "There's no contest with that link." + "Back to Compete".
- A private contest you're not in: its title + "Join with the code to take part."

---

##### 5. Leaderboard `/compete/leaderboard/` (theirs: Leaderboard)

- H1 "Leaderboard", the sub-nav, and a helper line that follows the controls: "Weekly boards reset Monday 00:00 UTC (Mon 3:00 AM your time · in 3d 4h)." For Season: "Road to Oct 3 · ends Oct 3 · 10 days left".
- **Controls** (one row on desktop, stacked on phone):
  - *Metric* underline: Points · Rating · Questions right · Test score. A one-line helper names the metric:
    - Points: "10 / 20 / 30 for each easy / medium / hard answer right in ranked contests, +5 at SAT pace, +10 for finishing. A sprint counts its best run each week."
    - Rating: "Skill rating from ranked contest answers, weighted by how hard each question is. Level 1–10."
    - Questions right: "Right answers in any mode: practice, tests, contests."
    - Test score: "Best timed full Math section in the period, by the middle of its estimate band."
  - *Period* underline: Week (default) · Month · Season · Year · All time. For Rating, the period decides who is listed (students active in it) and adds a "Change" column.
  - *Scope* `<select>`: Everyone · Near me · Country ({yours}, or "Country: set on Me", which links to Me) · each of your groups.
  - *Domain* `<select>` (Points and Questions right only; disabled with a tooltip otherwise): All domains · Algebra · Advanced Math · Problem-Solving & Data Analysis · Geometry & Trigonometry. With a domain picked, points count only that domain's answers, with no finish bonus.
  - The controls live in the URL (`?metric=points&period=week&scope=all&domain=`), so a board can be linked and a reload restores it.
- **Podium** (hidden for Near me): three cards in the order 2 · 1 · 3, heights 132 / 156 / 116.
  - Each card: rank numeral (`num`), name, 32 px level badge, metric value, "82% · 1:34 avg".
  - Grounds: tile-2 for first (with a trophy glyph), tile for second and third. Orange is kept for you: your card, if you're on it, gets wash + the amber inset edge.
  - With fewer than 3 players, the empty cards read "Open".
- **Table:** Rank | Student (name + level badge) | {Points | Rating | Right | Band} | Accuracy | Avg time | Contests (Rating: Change; Test score: Sections).
  - Accuracy and Avg time are computed over the same answers the metric counts.
  - Anonymous rows keep their rank.
  - Your row, the sticky you-bar, 50 rows then "Show 50 more", and the end line "That's everyone: 1,284 students." work as in §4.
- **Near me:** the 5 above you, you, and the 5 below you, with "Show 10 more above / below".
- **Phone 390:**
  - Metric and period are underlines with short labels: "Points · Rating · Right · Test" and "Week · Month · Season · Year · All".
  - Scope and Domain are full-width selects.
  - The podium keeps its three cards at 1fr each, with names ellipsised.
  - The table becomes Rank | Student (with the meta line "82% · 1:34 · 12 contests") | metric.
- **States:**
  - Loading: the podium and 8 skeleton rows.
  - Empty period: "No ranked contests yet this week." + a link to the nearest period that has players ("This month: 212 students ›") + pill "Start the challenge".
  - You unranked: the you-bar reads "You're not on this board yet: finish a ranked contest."
  - Hidden (public off): the you-bar reads "You · #212 · shown as Anonymous", with a link to Me.
  - Error line + "Try again".

---

##### 6. Your rankings `/compete/rankings/` (theirs: Contest Rankings + profile rank + achievements)

H1 "Your rankings" and the sub-nav. The sections come in this order; desktop puts them in a 2-column grid where noted.

1. **Performance summary** (full width)
   - Ten stat tiles, 5×2 on desktop and 2×5 on phone: Rating + level · Contests played · Average score (%) · Contest accuracy · Best finish ("#2 · Daily Sep 19") · Best top % · Podiums (top 3 with ≥ 10 players) · Points this week · Season rank · Challenge streak (sub-line "best 12").
   - Under them, a line chart, 100% wide and 120 px tall, with an underline toggle **Top % · Rating** and a range underline **Last 30 contests · 90 days · All**.
     - Top %: the y axis runs from top 1% (up) to 100%, with gridlines at 10% and 50%.
     - Rating: y in rating points, with the level bands drawn as faint horizontal stripes.
     - x is the contest date. Points are focusable and clickable, and open that contest.
   - New student: "—" tiles, "Finish a ranked contest to fill this in.", and pill "Start today's challenge" (theirs: "Browse contests").
2. **Your ranks** (left) | **Pace** (right)
   - **Your ranks** (theirs: Your Rankings):
     - A table with a row for Everyone, Country and each group, and columns Week / Month / Season / All time.
     - Cells read "#12 of 340 · top 4%" and link to the Leaderboard with those settings.
     - Hidden students see "#12 · as Anonymous".
     - Last row: "Contests played 14".
   - **Pace** (theirs: Time Analysis). Underline toggle: By difficulty · By domain · Right vs wrong · Under pressure.
     - By difficulty / By domain: one row each, with:
       - an orange bar of your median answer seconds;
       - a graphite tick at the field median;
       - a dashed vertical line at 95 s labelled "SAT pace";
       - text "you 1:12 · field 1:34 · accuracy 80% (field 64%)".
     - Right vs wrong: your median time on right answers vs wrong ones, per difficulty ("wrong answers came 0:31 faster": the rushing signal).
     - Under pressure: accuracy and median time with under 3 minutes left on the clock vs earlier ("Under 3 min left: 45% · 0:48 | Earlier: 78% · 1:21").
     - Rows with fewer than 3 answers show "—".
     - Helper: "Median seconds from question shown to answer, in ranked contests."
3. **How you placed in a contest** (theirs: Contest Leaderboard)
   - A `<select>` of every finished contest, newest first: "Daily · Sep 23 · #4 of 37".
   - Picking one shows a mini board inline (top 5 + you ± 2) and "Open contest ›".
4. **Badges** (`#badges`, full width)
   - A grid of tiles (auto-fill, min 170 px). Each tile: line icon, name, rule, a progress bar + "n/N", and "Earned Sep 19" once earned.
   - Earned tiles get an orange ring on the icon. Locked ones are soft grey and show their progress.
   - Filter underline: All · Earned (n) · In progress.
5. **Seasons** (full width)
   - Table: Season | Points | Rank | Top % | Final (band, rank) | Badge.
   - The live season is the first row, marked "live".
6. **Contest history** (full width)
   - Filters: Kind select (All / Daily / Sprint / Weekly / Final / Private) and Sort select (Newest / Best rank / Best top % / Most points).
   - Table: Date | Contest | Score | R · W · S · V | Points | Time | Rank | Top % | Rating Δ | Ranked/Unranked | "Review ›".
   - 20 rows, then "Show 20 more".
   - Phone rows are two lines: "Daily · Sep 23 · Ranked" and "8/10 · 8·1·1·0 · 170 pts · #4 of 37 · top 11% · +14".
   - Empty: "No contests yet."

Loading, error and empty states follow §3. A long history is handled by the paging, the filters and the chart's range.

###### Badge set (computed from data; the earned date is stored the first time a rule is met)

| id | name | rule | progress |
|---|---|---|---|
| first-contest | First contest | Finish a ranked contest | 0/1 |
| streak-7 | 7-day streak | Answer something 7 days in a row (best ever) | n/7 |
| daily-7 | Challenge week | Finish the Daily Challenge 7 days in a row | n/7 |
| daily-30 | Challenge month | Finish the Daily Challenge 30 days in a row | n/30 |
| perfect-ten | Perfect ten | 10/10 on a Daily Challenge | best/10 |
| pace-setter | Pace setter | 8+ right on a Daily, every right answer within 95 s | best/8 |
| solved-1000 | 1,000 solved | 1,000 questions right, any mode | n/1000 |
| consistency | Consistency | Practise on 20 of the last 30 days | n/20 |
| top-ten | Top ten | Top 10 in a Daily with ≥ 20 ranked players | 0/1 |
| podium | Podium | Top 3 in any ranked contest with ≥ 10 players | 0/1 |
| weekly-4 | Four weekends | Finish 4 Weekly Modules | n/4 |
| sprinter | Sprinter | 20 right in one sprint | best/20 |
| dress-rehearsal | Dress rehearsal | Sit a Season Final | 0/1 |
| season-top-10 | Top of the season | Finish a season in the top 10% (≥ 50 players) | 0/1 |
| level-5 | Level 5 | Reach a rating of 1,251 | rating/1251 |
| level-8 | Level 8 | Reach a rating of 1,701 | rating/1701 |
| trap-hunter | Trap hunter | Close 25 mistakes | n/25 |
| all-rounder | All-rounder | ≥ 70% in each domain across contests (≥ 10 answers each) | k/4 |

A new badge appears as a toast on the result panel: "Badge earned: Challenge week".

---

##### 7. Create a private contest (a sheet from Overview; also "Challenge a friend" and a group's "Set a contest")

Fields, top to bottom:
- **Title** (default "{name}'s challenge", 3–40 chars).
- **For**: "Anyone with the code" (default) · {each group you own}. A group contest lists every member as an entrant from the start.
- **Questions**: underline 5 · 10 (default) · 15 · 22.
- **Skills**: the shared topic picker from the practice builder (4 domains × 19 skills, select-all per domain). The default is all.
- **Difficulty**: underline "Easy → hard" (default) · Easy · Medium · Hard · Mixed.
- **Format**: Both (default) · Multiple choice · Grid-in.
- **Clock**: "Auto (95 s a question)" (default) or a minutes stepper, 5–70.
- **Open for**: 1 hour · 24 hours (default) · 3 days · 7 days. For a group, this becomes **Due**: a `datetime-local`, from 1 hour to 30 days ahead.
- **Questions for each student**, radio:
  - "Same questions for everyone: good for going over them together" (default);
  - "Everyone gets their own twin: same skills and difficulty, different numbers".
- **Show answers**, radio: "After each question" (default) / "At the end".
- **Strict**, switch, off by default: "Leaving the tab or copying voids the open question."

Footer: a summary line, "10 questions · 16 min · open until tomorrow 4:10 PM", and a pill "Create". The result shows the code large (mono), with "Copy code", "Copy link" and "Open contest".

"Challenge a friend" on a result panel opens this sheet prefilled from that contest: same count, skills and clock, with twins on.

---

##### 8. The runner in contest mode

**Practice session (`/practice/session/`)** — the same format as practice, which the user called the best.
- **Top bar:**
  - A chip, "Ranked" or "Unranked" (tile ground, 12 px), beside the progress bar.
  - The **answer clock** (mm:ss). It counts down while a question is open and dims while a verdict is showing. It is driven by the server's `clock.left` / `clock.running`, not by `started`.
  - Quiet "Skip".
  - "Full screen" (desktop, where the Fullscreen API exists). It's optional, and leaving fullscreen voids nothing.
  - Calculator and Reference, as always.
  - Save stays hidden until a question is answered.
- **X no longer hands the sitting in.** It opens a sheet:
  - Question open: "Leave the challenge? This question will be skipped. The clock stops until you come back. Finish before 11:59 PM." Buttons: quiet "Leave" (skips), pill "Hand in now", × "Stay".
  - On a verdict: "Leave the challenge? Come back before 11:59 PM to finish."
- **Voids** (ranked sittings, and Strict private contests):
  - Triggers: `visibilitychange` hidden for ≥ 5 s, `copy`/`cut`/`paste`, or a `pagehide` beacon while a question is open. Each posts `/api/drill/{sid}/void`.
  - The first void in a sitting shows a banner: "Question 4 is voided: the tab was hidden for 12 s. It still shows its answer, but scores 0."
  - After that, the verdict carries a "Voided" tag.
  - The progress segment of a voided question is slashed.
- **Skip:** the verdict reads "Skipped · The answer is C", then the rationale. The segment is a dotted outline.
- **The verdict adds the field:** "62% of 37 got this right" (for twins, the same slot), shown once ≥ 5 have answered.
- **"At the end" reveal:** after an answer, no verdict. The next question comes straight away, and answered segments are filled grey without right or wrong. The review opens at the end.
- **Sprint mode:**
  - Header: "Right 7 · 2:41 left", with no segments.
  - The verdict shows the key and the mistake line, with the rationale behind a collapsed "Why" toggle.
  - Enter goes to the next question. When time is up, the summary appears.
- **Summary in contest mode:** the §4 result panel, with the topic mastery bars, the mistakes opened and closed, the name prompt and badge toasts. It replaces today's "#1 of 3" line.
- **Copy result** copies plain text (no emoji, no OS share sheet):
  ```
  SAT Freshman · Daily Challenge · Sep 23
  8/10 · 170 pts · 11:42 · #4 of 37
  ■■□■■■■·■■
  https://…/compete/contest/?id=daily-2026-09-23
  ```
  - ■ right, □ wrong, · skipped or voided.
  - The button then reads "Copied" for 1.6 s. If the clipboard is refused, the text is selected in a field instead.

**Test window (`/test/`) for the Weekly Module and the Season Final**
- A chip in the header: "Weekly Module · Ranked" / "Season Final · Ranked".
- The navigator, mark for review, strike-out, Check Your Work and the wall clock work as for any test.
- Voids use the same rules as above, for the question on screen, via `/api/session/{sid}/void`.
- The Final routes module 2 from the contest's own twin slots for that route.
- Hand-in goes to the contest page's result panel, not the plain report. The report link stays on the panel.

---

##### 9. Today, Me, Results, Report

**Today's Challenge card** gets:
- the ten-square ladder (before) or the answer strip (after);
- "37 finished · 6 sitting now";
- "#4 of 37 · top 11%" + "Next one in 07:14:22" once done;
- "Challenge streak 5";
- the whole card links to the contest page.

Group contests with a due time show as a row under it: "Period 3 quiz · due Fri 5:00 PM · Start".

**Today's QOTD**, after answering, adds:
- the option spread: 4 thin bars with % and, for wrong options, the misconception;
- quiet "Another like this" (5 questions on that template);
- "5-day streak";
- quiet "Past days ›".

**Me gets a "Boards" block:**
- **Name on boards:** a field (3–24 chars: letters, digits, spaces, `-` `_` `.`). Helper: "Shown on public boards. Don't use your full name."
  - Taken name: "Someone already has that name."
  - Reserved or default-looking names ("Anonymous", "Student 1A2B", "You"): "That name is reserved."
- **Toggle "Show my name on public boards"**, on by default. Helper: "Off: you're listed as Anonymous. Groups you join still see your name."
- **Country:** a select, blank by default. If the browser language has a region, a one-tap suggestion appears: "Suggested: United States". Helper: "For the country board. Leave blank to skip it."
- **Rank snapshot:** "Week #12 of 340 · Country #14 of 96 · All time #210 · Level 3 (1,084)", linking to Your rankings. It shows "—" until the first ranked contest (theirs shows ranks with no contests played).
- **Badges:** the 4 most recently earned tiles + "All badges ›" (theirs: Achievements + a dead View All).
- **Groups:** a list with name, code + Copy, member count and "Leave". An owner instead gets "Delete group" and a member list with "Remove".

**Results list:** contest rows show the kind ("Daily Challenge · Sep 23"), "#4 of 37 · 170 pts", a Ranked/Unranked chip, and link to the contest page.

**Score report (theirs: "Practice test — not ranked" + percentile):**
- A pill: "Ranked: timed full section" / "Not ranked: untimed" / "Not ranked: one module".
- Ranked sittings add a percentile: "Higher than 71% of timed full sections in the last 90 days (212 sections)", shown once there are ≥ 20.

---

##### 10. Build order (each step is one commit and one push)

1. **Model and fixes:**
   - tables, columns, the `kv` secret, and the `challenges` → `contests` migration;
   - the answer clock, skip, void, points with the pace bonus, ties, 950 s, ranked/unranked, too fast, carry;
   - the X leave sheet.
2. Contest page (daily, twins) + `/challenge/` redirect + NAV/SECTION + Overview (A, B, D, E) + Today's card.
3. Leaderboard: points and right; week/month/year/all; everyone and near me; podium; paging; you-bar; anonymous rows; domain filter.
4. Your rankings: summary, chart, ranks, pace ×4, contest picker, history.
5. Review with the field's answers + the field's traps + Compare + QOTD spread, past days and streak + "Another like this" (`templates` on POST /api/drill).
6. Sprint.
7. Weekly Module in the test window.
8. Rating + level + badges + the Test score metric + the report pill and percentile.
9. Seasons + Season Final + the Season period + the H card + the Seasons table.
10. Groups + the Me Boards block (name rules, public, country) + country scope + report name.
11. Private and group contests + owner results + Challenge a friend + Copy result + Add to calendar + daily reminder + ghost sittings.
12. README serving-layer rows and spec/rebuild.md §9 updated.

### 3.7.4 Extras: what they missed

- **Twin questions for ranked contests, the Daily included**: Same template, difficulty and format at each slot, fresh numbers for each student. Keys can be shown right away (our teaching strength), answers can't be passed on, throwaway codes harvest nothing, and retakes and ghost sittings are fair. A finite bank would burn items or leak keys.
- **Answer clock that stops while you read**: The countdown and the board's time count only while a question is open. Reading the key and rationale after each answer costs nothing, so the practice-session format works in a contest. Theirs hides answers until the contest ends.
- **Pace bonus at SAT pace instead of a raw speed bonus**: +5 for a right answer within 95 s and nothing for going faster. It rewards the real test's rhythm, not rushing, while the too-fast rule catches bots.
- **Skip with the key shown, and voids with a grace period**: Matches their Skipped/Voided stats. A skip still teaches (the key and rationale show), a 5 s grace spares a notification blip, and leaving never zeroes a sitting the way their resume limit does.
- **Seasons aligned to official SAT dates, with a Season Final**: Their 'Seasonal' is a label. Ours ends on the real test day and closes with a timed, adaptive, full Math section one week before it, sat against everyone else preparing for the same date.
- **Sprint with ranked retakes**: A 5-minute run as often as you like, and your best run of the week counts. Each run draws new questions, so a retake can't be memorised. Theirs can't allow retakes of a ranked contest.
- **The field's answers, by misconception**: For each question, the share who fell for each named mistake ('41% subtracted the constants instead of adding'), not just a % right. It relies on Item.reasons, and it works across twins because it groups by misconception, not by letter.
- **The field's traps, then 'Practice these 5'**: A contest ends in a practice set on the misconceptions most students fell for. Competition feeds study instead of stopping at a number.
- **'Another like this' on every reviewed question and on the QOTD**: A fresh-seed drill on the exact template. That is our core power. Their 'More practice' is generic.
- **Compare with a student**: Two answer strips side by side, slot by slot, with times: 'only you 2 · only them 1'. Twins make a slot comparable even with different numbers.
- **Contests that schedule themselves**: Daily, Sprint, Weekly and the Final are made from the date, so something is always live. Theirs relies on staff and was empty on both walks.
- **Private contests, 'Challenge a friend', and group contests with a due time**: Anyone (a teacher, a study group) can set a contest over chosen skills, length and window. A group owner gets a results table with per-question marks and CSV. That is their hidden teacher dashboard, free and in the open.
- **Groups and Near me alongside the country board**: A class or a friends' board is who a student actually compares with. Country stays as an opt-in scope, and Near me shows you with five above and five below on a board of thousands.
- **Anonymous listing that keeps ranks honest**: A student can hide their name without changing anyone else's rank, unlike removing rows.
- **Rating and level against item difficulty, with a rating chart**: A skill measure that works asynchronously with few players (like a puzzle rating) and doesn't reward volume the way points do. It reuses the spec/rating.md ladder, and the chart shows the level bands.
- **Pace against SAT pace and the field, plus right-vs-wrong and under-pressure**: Their time analysis shows only your seconds. Ours sets them against the field median and the 95 s a real module allows. It shows whether wrong answers come from rushing, and how accuracy holds with under 3 minutes left.
- **Domain boards**: Points and right answers filtered to one domain ('best in Geometry this month'), possible because every answer carries its topic.
- **Ranked tests with a percentile on the report**: Their percentile needs a fixed paper and a first attempt. Ours compares any timed full section with every other timed section in the last 90 days, because each section is fresh.
- **Ghost sittings of past days and closed contests**: Any past day can be regenerated. You sit it unranked and see 'would have placed #6 of 37'.
- **Fair ties, top %, and a Ranked/Unranked label with a reason everywhere**: Equal scores share a rank (=4). Top % gives meaning on big boards. Unranked always states why (ghost, repeat, too fast).
- **Too-fast guard and name reports from real players**: There are no accounts, and minors use the site. A cheap rule keeps bots off the board, and only codes with a ranked sitting can report a name, so three throwaway codes can't reset one.
- **QOTD streak, challenge streak, 30-day strips and past days**: Past days can be regenerated from the date. Streaks and strips give a reason to come back every day, and a missed day can still be sat or answered unranked.
- **Copy result, Add to calendar and a daily reminder (.ics)**: Sharing that works everywhere, with no OS share sheet (theirs froze). Contests and a daily reminder go into the student's own calendar without a notification system.
- **Live field line and 'sitting now'**: '62% of 37 got this right' after each answer, and '6 sitting now' on the card. The board feels live even on a small site.

### 3.7.5 Server changes

Tables and columns here are added by F4 as listed in §2.5; the drill fields map through §2.6; prefs through §2.7.

- **db.py: new tables**

  - contests(id TEXT PK, kind TEXT daily|sprint|weekly|final|private, title TEXT, owner TEXT, code TEXT UNIQUE, grp TEXT, opens TEXT, closes TEXT, count INTEGER, seconds INTEGER, spec TEXT JSON, questions TEXT JSON (identical contests only), created TEXT).
  - spec holds {slots:[[template,tier,fmt]], slots_m2:{lower,upper} (final), topics, difficulty, formats, theme, twin:bool, reveal:'each'|'end', strict:bool, rated:bool}.
  - contest_items(contest, template, seed, PK(contest,template,seed)): a twin is never dealt twice in one contest.
  - contest_members(contest, learner, joined, PK).
  - groups(id TEXT PK, code TEXT UNIQUE, name TEXT, owner TEXT, created TEXT).
  - group_members(grp, learner, joined, PK).
  - badges(learner, id, earned, PK).
  - item_ratings(template, tier, rating REAL, n INTEGER, PK).
  - name_reports(target, reporter, at, PK).
  - seasons(id TEXT PK 'season-2026-10-03', opens, closes, standings TEXT JSON, closed TEXT).
  - kv(k TEXT PK, v TEXT): holds the HMAC secret, made once with secrets.token_hex(32).

- **db.py: new columns (LATER_COLUMNS) and indexes**

  - sessions: contest TEXT, ranked INTEGER DEFAULT 1, points INTEGER, secs INTEGER, unranked_why TEXT.
  - attempts: sms INTEGER (server ms from serve to answer) and void TEXT ('left'|'copy'|'paste'|'pagehide').
  - learners: public INTEGER NOT NULL DEFAULT 1, rating REAL DEFAULT 1000, rated INTEGER DEFAULT 0, country TEXT (ISO 3166 alpha-2).
  - Indexes: sessions(contest, ranked, points DESC, secs), sessions(learner, contest), attempts(session, qid), attempts(learner, at).
  - Right / wrong / skipped / voided counts and the points breakdown live in sessions.result JSON.

- **db.py: migration**

  - INSERT OR IGNORE INTO contests: each `challenges` day becomes 'daily-'||day, kind 'daily', spec.twin=false, with its questions.
  - UPDATE sessions SET contest='daily-'||day WHERE kind='challenge'.
  - Backfill points and secs on finished challenge sittings from their attempts: no pace bonus, and secs from finished − started capped at 950 because sms is missing. Mark result.backfilled.
  - New days are twin contests. Stop writing `challenges` once step 2 ships.

- **server/compete.py (new): schedule**

  ensure(now, tz) lazily INSERT OR IGNOREs these rows, with no cron:
  - today's local daily: canonical slots from the existing daily ladder via Builder(f'contest:{id}') + blueprint.fill, fmt taken from each canonical card;
  - the current and next sprint-YYYY-Www: the 60-slot theme ladder;
  - the current and next weekly-YYYY-Www: slots('module1',1). On the weekend 7 days before a SAT date it is replaced by final-<date>, with slots_m2 for the lower and upper routes.
  SAT_DATES is a constant, also served in GET /api/compete for Plan and Today. The same contest id always gives the same slots.

- **compete.py: twins**

  - twin_questions(learner, cid, slots): for each [template, tier, fmt], use blueprint.draw_matching with a Builder that dedupes on the whole question (a sha1 of stem + choices + figure + table) instead of the stem, and skips seeds already in contest_items for cid. INSERT OR IGNORE the pick into contest_items.
  - Fallback: another template of the same topic, tier and format, same skill first.
  - Slot templates are limited to those with variety ≥ 15/18: blueprint.survey also counts distinct whole questions per template.
  - Questions are stored on the sitting and remembered (db.remember).

- **compete.py: clock, points, secs, ranked**

  - clock(row): answer-clock kinds report used = Σ attempts.sms of the sitting + (now − served) of the open question; left = seconds − used; running = a question is open. drill.overtime uses it for contest sittings.
  - finish_contest(row), at finish: points = Σ right unvoided × {easy 10, medium 20, hard 30} + 5 × right unvoided with sms ≤ 95000 (answer-clock kinds except sprint) + 10 when all were answered with no skip or void (not sprint).
  - secs = min(used, seconds); test-window kinds use finished − started capped at the clock.
  - result gets {right, wrong, skipped, voided, points_parts}.
  - Ranked checks, in order: 'ghost' if started outside the window; 'repeat' if a ranked sitting already exists (sprint excepted); 'fast' if median sms < 4000, or test-window (finished − started)/asked < 20 s, with right ≥ asked/2.
  - Writes sessions.points/secs/ranked/unranked_why, and INSERT OR IGNORE INTO learners (id, created), since learners only get a row on PUT /api/me today.

- **compete.py: board()**

  board(cid, me, scope='all'|'near'|'country'|'group-{gid}', offset, limit=50) → {players, entries:[{pid, rank, tie, name, anon, level, points, right, asked, secs, runs?, you}], you, next_offset}.
  - One row per learner: sprint takes its best run, every other kind the ranked sitting.
  - public=0 rows keep their rank with name 'Anonymous' and anon:true, except in group scopes and your own row.
  - Competition ranking over (points DESC, secs ASC), listed by finished ASC within a tie.
  - pid = the first 10 chars of hmac-sha256(kv secret, learner), never the code.
  - name = learners.name or daily.handle().

- **compete.py: leaderboard()**

  leaderboard(metric='points'|'rating'|'right'|'test', period='week'|'month'|'season'|'year'|'all', scope, domain=None, offset, limit). Period starts are UTC: ISO Monday / 1st / season opens / Jan 1.
  - points: SUM(points) of ranked sittings finished in the period, sprint as MAX per ISO week. With a domain, it is recomputed from attempts JOIN sessions (tier points + pace, no finish bonus).
  - rating: learners.rating for learners with a rated answer in the period, with Δ from the sittings' rating_before/after.
  - right: COUNT(attempts.correct=1) in the period, optionally for one domain.
  - test: MAX of (low+high)/2 of timed full-section sittings (kind mock, cfg.timed not false).
  It also returns accuracy, median secs and contests over the same answers; podium (the first 3); you (with rank even when off the page, and anon); players; resets_at; nearest_nonempty for empty periods.

- **compete.py: review(), traps(), compare()**

  - review(cid, learner): 403 unless the learner's sitting is finished or the contest has closed everywhere. Per question/slot it returns:
    - the full question (key, rationale, reasons) from the learner's own sitting;
    - you {given, correct, skipped, voided, sms};
    - field {answered, right, skipped, voided, median_sms, options:[{index, share, mistake}] for identical, mistakes:[{label, share}] for twins}.
    Aggregated from ranked sittings, first attempt per (session, qid).
  - traps(cid): the top 5 (template, reason, label, share) by wrong ranked attempts.
  - compare(cid, me, pid): 403 unless both finished and the target is public. Returns both strips and per-slot sms.

- **compete.py: rating**

  On each rated answer (the first attempt of a ranked sitting of a rated contest, not voided, within the clock):
  - E = 1/(1+10^((Ri−Rs)/400));
  - Rs += Ks(S−E), with Ks = 32 while learners.rated < 30 and 12 after;
  - Ri −= 4(S−E), with Ri starting at 900 easy / 1100 medium / 1300 hard;
  - rated += 1.
  rating_before and rating_after are stored in the sitting's result JSON. level(r) uses the spec/rating.md ladder, provisional while rated < 30.

- **compete.py: badges and seasons**

  - evaluate(learner) computes the 18 badges from attempts, sessions, traps, learners and seasons, INSERT OR IGNOREs newly met ones with earned=now, and returns [{id, name, rule, have, need, earned}]. It is called at drill finish, test finish and GET /api/compete/me, and finish responses carry badges_new.
  - close_season(id): lazily, on the first request after `closes`, stores the standings JSON and awards season-top-10.

- **compete.py: percentile() for the report**: percentile(sid): for a timed full section (kind mock, timed), the share of timed full sections finished in the last 90 days whose band centre is ≤ this one, and n. Returned only when n ≥ 20. Otherwise ranked:false with why 'untimed' | 'module'.
- **drill.py: serving, clock, skip, void, slots, sprint, reveal**

  - _serve sets q['served'] = now(). answer() computes sms = min(now − served, clock left) and passes it to progress.record(…, sms=).
  - seconds_of fixes 954 → count × (MODULE_SECONDS // MODULE_SIZE) = 950. For contest sittings, state() returns clock {left, running} from compete.clock.
  - skip(row, qid) sets answers[qid] = '_skip' (never correct). It files no attempt and opens no trap, and returns the key and rationale.
  - void(row, qid, why, secs) stores the reason in cfg.voided[qid]; the later answer is filed with attempts.void.
  - marks become [{r:'right'|'wrong'|'skip'|'void'}].
  - The cfg 'slots' ([[template, tier, fmt]]) are served in order via compete.twin_questions (identical contests use items).
  - Sprint = seconds 300, count None, fixed, no repairs; it ends at the 60th slot.
  - reveal='end': _feedback returns only {answered, total} until finish.
  - _feedback adds field {answered, right} for contest sittings (same slot, ranked sittings) once answered ≥ 5, and voided:true.

- **progress.record and progress.carry**

  - record: new optional sms and void parameters, written to attempts. After filing, a ranked, unvoided sitting of a rated contest calls compete.rate().
  - carry also moves group_members, contest_members and badges (INSERT OR IGNORE), and keeps the rating of the side with more rated answers, all before the learners row moves. Afterwards, any second ranked sitting of one contest under the target code gets ranked=0, unranked_why='repeat'. This fixes the known edge.

- **daily.py**

  - challenge(day) stays as the daily slot builder and writes a twin contest row.
  - board() is replaced by compete.board.
  - question(day) is unchanged: the QOTD stays identical.
  - qotd_feedback adds options [{index, share, mistake}] and streak (consecutive local days with a qotd:{D} attempt made on day D).

- **app.py: contest endpoints**

  - GET /api/compete: the hub payload: daily status + field (+ sitting_now), live/upcoming counts, me {rating, level, provisional, week_rank, all_rank, country_rank, week_points, played, best, challenge_streak}, season {id, name, closes, rank, points, final}, board_preview, next_badges, groups, sat_dates.
  - GET /api/contests?status=live|upcoming|finished|private&offset&limit.
  - GET /api/contest/{cid}: 'daily' resolves via X-Tz. Returns meta, ladder, rules, field {players, sitting_now, median_points, best}, me {session, status, answered, clock, result, ranked, why}, recent_days (daily, 30), entrants (private), qotd (daily).
  - POST /api/contest/{cid}/start → {session, runner:'session'|'test'}. Per learner it returns the existing sitting (sprint: the open run, else a new run) using the INSERT … WHERE NOT EXISTS pattern keyed on contest. A ghost sitting when closed.
  - GET /api/contest/{cid}/board, /review, /traps, /compare/{pid}, and /results (owner only: entrants × per-question marks).
  - POST /api/contests (create private): validates count ∈ {5,10,15,22}, topics ⊂ catalogue, minutes 5–70, open_for ∈ {1,24,72,168} h or due within 1 h–30 d for an owned group, twin, reveal, strict. Returns {id, code}. Codes are ^[A-HJ-NP-Z2-9]{6}$, unique across contests and groups.
  - PATCH /api/contest/{cid} {close|extend|title} and DELETE /api/contest/{cid}: owner only, 403 otherwise.
  - POST /api/join {code} → {kind, id} + a member row.
  - POST /api/drill/{sid}/skip {question_id} and POST /api/drill/{sid}/void {question_id, why, secs}.

- **app.py: board, ranking and group endpoints**

  - GET /api/leaderboard?metric&period&scope&domain&offset&limit.
  - GET /api/compete/me: summary tiles, the chart series (top % and rating, range), the ranks table (everyone/country/groups × week/month/season/all), pace (difficulty, domain, right-vs-wrong, under-pressure) with field medians, badges, seasons.
  - GET /api/compete/history?kind&sort&offset&limit=20.
  - GET/POST /api/groups, GET /api/groups/{gid}, DELETE /api/groups/{gid}, DELETE /api/groups/{gid}/members/{pid|me}.
  - POST /api/report-name {pid}: counted only from reporters with a finished ranked sitting; 3 distinct reporters reset the name to NULL.
  - The /api/challenge* routes stay as thin aliases until Today moves, then go.
  - GET /challenge/ and /challenge → 307 /compete/contest/?id=daily, defined before the static mount.

- **app.py: /api/me**

  - name: HANDLE_OK = ^[A-Za-z0-9 _.\-]{3,24}$, unique case-insensitively (409 'Someone already has that name.'). Refused with 422: a small built-in blocklist, and reserved patterns (^student [0-9a-f]{4}$, anonymous, you).
  - public: bool.
  - country: an ISO alpha-2 from a built-in list, or null.
  - The response adds ranks {week, country, all, level, rating} and the latest 4 badges.
  - NAME_OK stays for the diagnostic sign-up.

- **app.py: /api/qotd and /api/drill**

  - GET /api/qotd?day=YYYY-MM-DD (≤ today; 422 for a future day).
  - POST /api/qotd accepts a past day (still once per day, stored as qotd:{day}). Only an answer made on its own day counts for the streak.
  - POST /api/drill gains templates: list[str], queued with fresh seeds like the mistakes queue, for 'Another like this' and 'Practice these 5'.

- **app.py: the test window for Weekly and Final**

  - POST /api/contest/weekly-…/start creates kind='module' with contest set, timed, and questions = json {module1: twin_questions(slots)}. It is the questions JSON, not the module1 column, which holds module 1's mark.
  - final-… creates kind='mock', mock_id 'new', with module1 twins. At routing, finish() builds module 2 from spec.slots_m2[route] via twin_questions instead of fresh_module.
  - /api/session/{sid}/finish then calls compete.finish_contest(row).
  - POST /api/session/{sid}/void {question_id, why, secs} records voids.
  - GET /api/session/{sid} includes contest {id, title, ranked} for the header chip.
  - GET /api/session/{sid}/results adds ranked {ok, why} and percentile {share, n}.

- **test_flow.py**

  New checks:
  - the same contest slots for everyone; twins match template/tier/fmt and differ in whole-question hash for at least 9 of 10 slots;
  - a (template, seed) is never dealt twice in one contest;
  - 954 → 950;
  - the answer clock doesn't move while a verdict is showing;
  - skip files no attempt and opens no trap;
  - a void scores 0 but files to the map;
  - the points breakdown (pace and finish bonus);
  - ties share a rank;
  - too fast is unranked;
  - ghost sittings are unranked with would_be;
  - review is 403 before finishing;
  - option shares sum to 1 ± 0.01;
  - the sprint counts its best run only;
  - near me has you in the middle;
  - public=0 shows as Anonymous at the same rank, and the player count is unchanged;
  - name uniqueness returns 409 and a reserved name 422;
  - the country scope;
  - private create, join and board; group due time and owner results;
  - carry leaves one ranked sitting;
  - rating moves, and provisional ends at 30;
  - the first-contest badge;
  - the season window and a Final with route-matched twins;
  - the percentile appears only with n ≥ 20;
  - /challenge/ redirects.


### 3.7.6 Files this spec names, and who owns each

| file | owner |
|---|---|
| `server/compete.py` | S8 |
| `server/db.py` | F4 |
| `server/blueprint.py` | F5 → S5 |
| `server/practice.py` | F5 → S4 |
| `server/drill.py` | F5 → S4 |
| `server/progress.py` | F4 |
| `server/daily.py` | S3 |
| `server/app.py` | F0 (routers register themselves, §2.10) |
| `server/test_flow.py` | shared: new checks go in server/checks/<task>.py |
| `web/compete/index.html` | S8 |
| `web/compete/contest/index.html` | S8 |
| `web/compete/leaderboard/index.html` | S8 |
| `web/compete/rankings/index.html` | S8 |
| `web/challenge/index.html` | S8 |
| `web/assets/ui.js` | F2 |
| `web/assets/ui.css` | F1 |
| `web/practice/session/index.html` | S4 |
| `web/test/index.html` | S5 |
| `web/test/test.js` | S5 |
| `web/index.html` | S3 |
| `web/me/index.html` | S1 |
| `web/results/index.html` | S6 |
| `web/results/report/index.html` | S6 |
| `README.md` | shared: each task edits its own subsection |
| `spec/rebuild.md` | F0 (superseded by this file) |

A file owned by another task is met through §2.9: the owner builds it, or this section's task adds its hook on its own page.

### 3.7.7 Shared needs

- NAV gets a sixth item (Compete) and the phone tab bar goes to 6 columns, which changes every page's shell. UI.shell(pageOverride) lets the session and the test window highlight Compete during a contest sitting. Any other section that wants a new nav item has to fit in this 6-column bar. → built in F2 ui.js  
  ↳ R1: the phone keeps 5 tabs; the item goes in the sidebar and the menu sheet
- UI.board(host, data, {columns, onMore, youBar, rowMenu}): a ranked table with =ties, level badges, Anonymous rows, your row, a sticky you-bar and paging. Used by the contest page, the leaderboard, the Overview preview, the rankings picker and group boards. → built in S8 compete-ui.js  
  ↳ R4: groups are classes (S2)
- UI.level(rating, provisional, size): the brand-mark ring level badge (10 steps, digit in the counter, solid square at level 10). Also used on Me and Results. → built in S8 compete-ui.js
- Stat tile component (label, big number, sub-line, '—' empty state), the same tiles Results, Report and Me need.
- UI.strip(marks): answer squares for right / wrong / skipped / voided / unanswered. Results, Report, the session header and Today use it too. → built in F1 kit.js
- Question review item with the field's answers: UI.question review mode plus an option/misconception spread bar. Report, Mistakes and the QOTD use it too. → built in F3 question.js / runner.js
- Underline segmented control and filter chips (the existing .choices), plus a compact <select> style for scope, domain, kind and sort filters. Shared with the Results/Report/Practice filter bars.
- Topic picker (4 domains × 19 skills with select-all) from the practice builder, reused in the Create a contest sheet.
- POST /api/drill `templates` ('another one like this' queue with fresh seeds). Practice, Report, Mistakes and the QOTD all need it.  
  ↳ R10: the drill body, §2.6 (F5)
- Server-measured answer time (attempts.sms) instead of client ms. Results' study time and pace charts should read it.  
  ↳ R7, R8: qstate ms and attempts.sms (F4, S5)
- The shared runner (session and test window) needs: the leave/hand-in sheet; Skip; void reporting (visibilitychange, copy/cut/paste, pagehide beacon); an answer clock driven by server clock.left/running; and a reveal-at-end mode. The exam runner and the practice session share one format, so both get them.
- The test window should record per-question dwell time. Without it, Weekly/Final per-question times, pace and field medians show '—'. The Report section needs the same for 'time per question' (their report lacks it).  
  ↳ R7, R8: qstate ms and attempts.sms (F4, S5)
- Builder dedupe on the whole question rather than the stem: 93 templates keep one stem across seeds and are otherwise spent for a learner after one sighting. That affects practice and tests too, not only twins.
- SAT_DATES (official test dates) lives in compete.py and is served in /api/compete. Plan and Today's exam-date picker should offer them (theirs: a select of official dates).  
  ↳ R15: server/satdates.py (F4), served in /api/shell (F2)
- Plan tasks can point at contests: the Daily Challenge as a daily task, and the Weekly Module or Season Final on the test day.
- Results list rows for contests (rank, points, Ranked/Unranked, a link to the contest page), and the Report's Ranked pill + percentile, both come from compete.
- Me's Boards block (name rules, public, country, ranks, badges strip, groups) sits inside the Me section's layout.
- Skeleton loading blocks (.skel) and the standard error line + 'Try again' used across pages.
- UI.countdown(el, iso) for contests, and also for the exam countdown on Today and Plan. → built in F1 kit.js
- UI.toast for badges earned and 'Copied'. → built in F1 kit.js
- UI.copyText (clipboard with a select-in-field fallback) and UI.ics (a calendar file, single or repeating) helpers. → built in F1 kit.js  
  ↳ R18(b): the plan's calendar file is built on the server (S7); single events use UI.ics(event) in F1 kit.js

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

### 3.7.9 This section's open questions

Folded into Part 5 where they need a decision; kept here for context.

- The Daily is now twins by default: the same template, difficulty and format at each position for everyone, with each student's own numbers. That closes key harvesting on throwaway codes and a shifted X-Tz. What it costs: 'what did you get for Q3' becomes 'how did you do Q3', and the option spread is by misconception rather than by letter. The QOTD stays identical. Keep twins, or go back to one identical ten with answers held until the day closes everywhere (theirs)?
- Voiding is on for every ranked kind, with a 5 s grace and no void for leaving fullscreen. Is that the strictness you want for a free site used by minors? The alternative is a warning on the first leave and voids only after that.
- Seasons run between official SAT dates, and the Season Final replaces the Weekly Module one weekend before each date. Keep that list of dates (Aug 22, Sep 12, Oct 3, Nov 7, Dec 5, Mar 6, May 1, Jun 5), or use calendar months?
- Nothing stops one person holding many learner codes. Is 'first sitting per code + too-fast + voids + reports only from ranked players' enough without accounts, or should ranked boards require the diagnostic's email sign-up?
- Is reusing spec/rating.md's duel ladder (seed 1000, levels 1–10, the ring badge) for a rating measured against questions acceptable? That spec was written for duels, and its badge art is marked 'proposed'.
- Country is opt-in and blank by default, with a suggestion from the browser language. Is a country field acceptable for minors, or should the country board go and groups stay?
- 'Questions right' counts practice answers, so it rewards volume on purpose, as an effort board. Keep it, or make every board contest-only?
- Is a sixth phone tab (65 px each at 390) acceptable, or should Compete sit under Today on phones?
- Real-time head-to-head duels (spec/rating.md) are still left out. Private contests, 'Challenge a friend' and Compare cover async play. Build live duels later?

---

## 3.8 Words (vocabulary)

> **Spec title:** Vocabulary  
> **Built by:** S9  
> **Read with resolutions:** R1, R10, R11, R13, R17, R24, R25, R29, R36 (§2.2). Where this spec disagrees with them, they win.

### 3.8.1 What they have

- **Nav item and route**: Sidebar 'Vocabulary' → /vocabulary, which redirects to /vocabulary/library. It uses the same shell as every other page.
- **Four big pill tabs**: Library / Flashcards / Quizzes / My Words, each on its own route: /vocabulary/library, /vocabulary/flashcards (?cardId= or ?collectionId=), /vocabulary/quizzes, and /vocabulary/my-words, which redirects to /my-words/saved.
- **Library size and default**: 1,002 words are claimed on the plan landing. Re-checked 2026-09-23: the Library opens already filtered to 'Must know 650 SAT words'.
- **Library: Difficulty filter**: Easy / Medium / Hard, colour coded throughout vocab: green easy, amber medium, red hard.
- **Library: Topic filter**: General / Academic / Science / Economics / Transitions.
- **Library: Collection filter**: 'Must know 650 SAT words' / 'The College Panda's 400' (a published book's list) / 'Custom Added Words'.
- **Library: Start Practice Session**: The primary button at the top right. It is a link to /vocabulary/flashcards?collectionId=…, so it starts flashcards over the whole collection and ignores the Difficulty and Topic filters.
- **Library: tile grid**: Word tiles in 6 columns, 16px radius, with a 1px border coloured by difficulty. There is no search, no status, no progress and no meaning on a tile. The tiles are not buttons or links (the accessibility tree shows plain text), so a keyboard user cannot open one.
- **Library data quality**: The default collection lists words twice: eloquent, elusive, inherent, meticulous, pervasive, unprecedented, lucid, mitigate and others appear twice in the same grid.
- **Tile → flashcard**: Clicking a tile opens that word's flashcard front-first (?cardId=uuid). The student can then move through the deck from there.
- **Flashcard: difficulty pill**: A coloured difficulty pill above the card.
- **Flashcard: stacked deck**: The card has two ghost cards behind it to suggest a deck.
- **Flashcard: front**: The word, large and centred.
- **Flashcard: flip**: Click the card to flip it.
- **Flashcard back: definition**: In bold.
- **Flashcard back: example**: One fixed example sentence, in italics and quotes.
- **Flashcard back: Synonyms**: A list with a share-style icon.
- **Flashcard back: Antonyms**: A list with an x icon.
- **Flashcard back: Common Confusions**: A lightbulb and a blue list of lookalike words (illusory → illusion, illustrate, elusive).
- **Save star**: A star at the top right of the panel. It appears only after the card is flipped.
- **I Know / Don't Know**: Two self-grade buttons. Don't Know just advances: nothing visible happens and the word is not added to Due. In the re-check, My Words still showed 'Due Today 0 words' after two words had been graded.
- **Previous / Next**: Free movement back and forward through the deck, with or without grading. Next is blue.
- **New-word allowance**: Opening a card uses up one new word for the day: Free 5, Pro 20, Elite 30. It is metered as 'New Words Today 0/5' on Subscription and Profile, so browsing is punished.
- **Quizzes: Collection select**: 'All Collections' or one collection.
- **Quizzes: timer**: No timer / 30 sec / 60 sec, per question.
- **Quiz item**: The definition is the prompt, centred and large, with 4 word tiles in a row as the answers. This is the only question type. The answer tiles are not buttons (plain text in the accessibility tree), so there is no keyboard answering.
- **Quiz distractors**: The wrong options are often near-synonyms of the answer, so more than one fits. Seen live: the prompt 'Cleverly inventive and resourceful, often in solving problems or creating new ideas.' offered ingenious / imaginative / innovative / original.
- **Quiz feedback, wrong**: The wrong tile tints red, the others fade, the correct one gets a faint outline, and a red label reads 'Correct answer: {word}'. A Next pill appears. It does not advance on its own and does not explain the mistake.
- **Quiz feedback, right**: The picked tile tints green, the others fade, and a Next pill appears. There is no 'Correct' text.
- **Quiz session**: No running score, no question count and no end of session: the quiz never finishes and never summarises.
- **Report chip**: On a quiz item. It opens the shared Report modal: a read-only 'Sent with your report' box, Title 0/200, Category (General feedback / Bug / Wrong answer key / Typo / Feature request / Other), Details 0/5000, up to 10 image attachments (JPEG/PNG/WebP/GIF, 50 MB each), and Send feedback.
- **My Words: two nav cards**: 'Saved Words N words >' and 'Due Today N words >', the spaced-repetition queue. Each opens its own filtered list.
- **My Words: filters**: The same Difficulty / Topic / Collection filters as the Library.
- **My Words: empty state**: A dashed box: 'No saved words match these filters' / 'Try broader filters or save more words from the library.'
- **Add-your-own-word FAB**: A draggable blue circle at the bottom right of every page ('Add your own word (drag to move)') that feeds 'Custom Added Words'. It covers the Next button in QBank sessions. In the re-check, a click from a background tab opened nothing, so the form's fields were not seen.
- **Plan wizard: Include vocabulary practice**: A toggle on step 4 ('What to focus on'), on by default. It is stored as vocabularyPreference in the plan (bundle).
- **Plan tasks (bundle)**: Vocabulary and Flashcards are task types. Each task has a duration, a domain and an aiReason behind 'Why this task?'. The destinations are Vocab quiz / Vocabulary / Flashcards, and the launch buttons are 'Study words' / 'Review cards'. Tasks can be Mark done, Skip, Practice again and Undo, and they count toward the plan's X of Y tasks.
- **Plan landing stat**: '1,002 Vocabulary words (flashcards, quizzes, spaced review)'.
- **Profile: vocab surfaces**: A 'Vocab N Word' stat tile, which counts words opened (it read 2 after two cards). A Saved Words count under Saved Content. An 'Include Vocab Review' toggle under Learning Preferences.
- **Subscription meter**: 'New Words Today 0/5' on Subscription and Profile. The cap is 20 a day on Pro and 30 on Elite.

### 3.8.2 What we have now

Status is have / partial / missing / worse, against theirs.

- **Words section / route**: *missing.* There is no page. /vocabulary/ and /words/ both return FastAPI's raw JSON {"detail":"Not Found"}. spec/rebuild.md deferred it: 'not now: the bank is Math. Later, with an R&W bank'.
- **Nav item**: *missing.* UI.NAV has five entries (Today, Practice, Tests, Plan, Results), and the phone tab grid is repeat(5,1fr) with 10.5px labels.
- **Word content**: *missing.* There is no glossary and no R&W word list. The bank already speaks in words, though. A 3-seed scan of the 386 templates (1,156 items, 1,576 distinct reasons) gives raw regex hits in the reasons for mean/median in 17 templates, sample/population in 18, radius/diameter in 12, supplement/complement in 10, hypotenuse in 8 and sine/cosine in 5. It finds none for percentage point, radian or 'no solution'. The hits are noisy ('less than|order|subtract' matched 102 templates), so links must be curated.
- **Tile grid and filters**: *partial.* The practice map has a reusable .tile (glyph, mastery bar, orange mistake dots) and .choices toggles. There is no search box and no dropdown filter anywhere on the site.
- **Flashcards (flip, know/don't know)**: *missing.* There is nothing to flip on any page.
- **Spaced repetition / Due today**: *missing.* Traps close after two clean answers on a template. That is a repair rule, not a review schedule, and nothing is dated.
- **Quiz runner**: *partial.* The practice session (web/practice/session/) already renders a 4-option MCQ that shows the key and names the mistake, with progress segments, a count beyond 24, a clock, .keys hints and a summary. Its .run-* CSS is inline in that page, not in ui.css.
- **Per-question timer**: *missing.* Practice has a whole-set clock (minutes) but no per-question timer.
- **Save**: *partial.* Questions can be saved (the saved table and the bookmark tool in the session). Words cannot.
- **My Words (saved + due)**: *missing.* Mistakes lists saved questions only.
- **Custom words / add from anywhere**: *missing.* There is no user-authored content anywhere. The shell bar holds only the brand, the nav, the streak and the avatar, and no page acts on selected text.
- **Report a problem**: *missing.* There is no report sheet or endpoint anywhere. It is planned for the session (enrichment item 6). python-multipart 0.0.22 is installed, so UploadFile works for attachments.
- **Plan: include vocabulary / words task**: *missing.* Plan step 4 has only the four domains as Focus / Normal / Strong (at most 2 on Focus). paintTask draws practice / test / rest per day from the profile, client-side. app.per_session() turns a day's minutes into questions at 95 s each, and nothing else takes minutes from the day.
- **Me: vocab stat and preference**: *missing.* Me shows the name, the device code and the carry form, nothing else.
- **Carry between devices**: *partial.* progress.carry moves attempts, sessions, practice_seen, saved, traps and learners. Me's 'use another code' check refuses a code unless days.total > 0, which counts question attempts only, or a profile field is set. So a words-only code would get 'Nothing is saved under that code.'
- **Sessions list**: *worse.* /api/history returns every finished session. Results links every row to /results/report/?id= and Tests filters by NAME[kind]. A new session kind such as a words run would land in Results with a link to a report that cannot render it.
- **Drill template filter**: *partial.* cfg.queue serves listed templates, but as repairs and only once each. There is no 'only these templates' filter. _pick falls back to the topic's whole pool (`or by_topic.get(topic, [])`) when the difficulty filter empties it.
- **Streak flame**: *partial.* paintMe hides the flame when days.total is 0, and days() counts attempts only, so a day of word review would not show a streak.
- **Daily word**: *partial.* There is no word of the day. daily.py already picks the question of the day from a sha256 date hash, and a word of the day can use the same pattern.
- **Term help inside questions**: *partial.* There is no lookup yet, but UI.question sets the stem as a single text node (.q-stem, textContent), so wrapping terms in text nodes is safe. Rationales are text too (.why).
- **Pronunciation**: *missing.* There is no audio anywhere. The browser's own speechSynthesis needs no content or key.

### 3.8.3 Design

#### Words: the Vocabulary section, rebuilt

##### Review changes

What this review changed from the proposed spec, and why.

1. **R&W vocabulary had no equivalent.** Theirs is 1,002 R&W words. The draft shipped about 220 math terms and left R&W to "type your own". This adds a **Reading & Writing** group:
   - **SAT words: core**, about 300 words.
   - **SAT words: advanced**, about 450 words.
   - **Transitions**, about 70 words and phrases, grouped by logic.

   Every entry has our own definition, a part of speech, 2–3 example sentences, synonyms, antonyms and lookalikes. With the math groups that makes about 1,090 distinct entries, more than theirs, and the build fails on a duplicate. Their default collection lists eloquent, elusive, inherent, meticulous, pervasive and others twice.
2. **Their "Common Confusions" (illusory / elusive) had no R&W equivalent.** Confusions now come in three kinds, each with its own tell:
   - **meaning mix-ups** (median / mean);
   - **lookalikes** (elusive / illusory, eminent / imminent);
   - **split senses** (degree; sanction; qualify).
3. **Their Topic filter was replaced, not matched.** Topic ▾ now groups three sets of values:
   - the 19 math topics by domain;
   - the SAT-word subjects: General, Academic, Science, History & social studies, Literature & arts, Economics;
   - the transition logics.
4. **A word with no bank link had no difficulty.** Every entry now carries an authored `level`. The bank-derived difficulty wins where it exists.
5. **There was no R&W quiz format.** Two SAT-style types are added:
   - **In context**: a short text with a blank, using the SAT's own kind of prompt.
   - **Pick the transition**: exactly one of the four options has the right logic, and every wrong one names its logic.
6. **Their free Previous / Next was cut** to "back one card, regrade the last one". The runner now has **← Previous** and **→ Next** (skip without grading) through the whole run. Any card can be regraded while that grade is still the word's latest review. Grading moves to `1` / `2`, plus swipe.
7. **A Library tile opened the sheet with the meaning already showing**, which lost the recall step (theirs opens a card front-first). The sheet now has **Flashcards from here**: a run over the list the student is in, starting at that word, front first.
8. **Add-from-anywhere was dropped along with the FAB.** It is back, without covering anything:
   - a **+ word** button in the shell bar on every page except the runners and the test;
   - **Add to my words** on any text selected in a question or a rationale, which prefills the word.
9. **My words lost the Collection filter.** The Library had put collections in tiles only. Collection ▾ is now in the shared filter bar on every Words list, kept in sync with the tiles. **Part of speech ▾** appears whenever the view holds R&W words.
10. **The Report sheet was weaker than theirs.** The draft allowed 2000-character details against their 5000, had no attachments, and had no General feedback or Feature request category. It now carries:
    - all of their categories, plus Wrong or unclear definition and Confusing question;
    - 5000-character details;
    - up to 10 images, picked or pasted, 10 MB each;
    - the auto-filled "Sent with your report" box.
11. **Plan parity was one calendar line.** Their plan has Vocabulary and Flashcards tasks with minutes, a reason and launch buttons. Ours now has a **Words task** on every study day ("12 due · 10 new · about 6 min"):
    - it has a reason line and three launch buttons: **Review cards**, **Learn 10** and **Quiz**;
    - it completes itself, and it can be marked done or skipped like any other task;
    - its minutes come out of the day's budget, so the coach's set shrinks. This settles the draft's open question the way their "no day runs longer than you said" step does.

    Step 4 also chooses which groups new words come from.
12. **Me had no parity for their profile.** Me now shows Words known, Words studied, Saved words and Reviews this week. It carries the same **Include words** switch as the plan (one field, so it cannot drift the way their target score does), plus new words a day and the underline switch.
13. **"Known" could be earned in three days**, because an early review promoted the word. Now only a due card (or a new one) moves up, while an early wrong answer still drops it. Known means right three times over at least ten days.
14. **A words-only device code could not be carried.** Me refuses a code unless `days.total` > 0, and `days.total` counts attempts only. `days.total`, carry's count and the streak flame now include word reviews and own words.
15. **Word runs would have broken Results.** `/api/history` lists every finished session, and Results links every row to `/results/report/`. Now:
    - words runs are listed only with `?kind=words`, and they open `/words/run/?id=`;
    - the sheet's one-question examples (`source:'word-example'`) are never listed;
    - the report page redirects a words id to the run.
16. **The sheet made a drill session on every open**, so paging through 40 words would have made 40 sessions. The example now comes instantly from the index. A session is made only on **Answer it** or **Another**.
17. **Drill filtering had a hole.** `_pick` falls back to the topic's whole pool when the difficulty filter empties it, which would escape the word's templates. The fallback now keeps `only`, and a repair inside a mix-up drill also looks for the mix-up.
18. **Bankless confusions would have failed the build.** A 3-seed scan finds no reason naming percentage points, radians or "no solution". Such confusions are now `bankless`. They stay on the sheet and in quizzes, and they have no Drill it.
19. **Saving during a quiz could reveal the target.** In a quiz, ★ and `S` work only after the verdict.
20. **Their live quiz uses near-synonyms as distractors**, so more than one answer fits. Seen live: "Cleverly inventive and resourceful…" with ingenious / imaginative / innovative / original. Ours rules them out:
    - a distractor is never a synonym of the target, or one hop through one;
    - a distractor matches the target's part of speech;
    - the build proves at least 3 valid distractors for every word and quiz type.
21. **Extras added**:
    - pronunciation through the device's own voices (`speechSynthesis`);
    - **Looked up**: a word tapped inside a question goes to the front of the New deck;
    - a **Missed lately** deck and status;
    - **two** words of the day (math and SAT), like their two questions of the day;
    - tap-to-define in rationales too, never on options;
    - Quizlet-format import;
    - a **Meanings** toggle on the grid;
    - a **Two meanings** filter for SAT words whose tested sense is not the common one;
    - word achievements handed to Me.
22. **One helper narrated.** "Tap or press Space to turn" became the practice session's `.keys` hint, shown on hover devices only like every other key hint.

##### 0. What it is

Words is the vocabulary section: one set of tools over three kinds of word.

1. **Math language**: the words SAT Math is written in. They are wired into the bank in both directions:
   - **Word to questions**: every word shows a real bank question that uses it, and "Another" never runs out. Every word can also start a practice set of only the questions that use it.
   - **Mistake to words**: a wrong answer whose named mistake is a word mix-up links to those words. Every mix-up can start a drill of questions in which exactly that mix-up is one of the options.
   - **Words inside questions**: math words are underlined in practice stems and rationales, and tapping one shows its meaning.
2. **Reading & Writing words**: SAT words (core and advanced) and transitions, with the same flashcards, spaced review and quizzes, including two SAT-style formats. There is no bank link until an R&W bank exists. The schema already has the fields for one (`tests`, `uses`, `cloze_templates`).
3. **My own**: the student's own words, in their own lists.

It is completely free:

- there is no allowance, and opening or browsing a card costs nothing;
- the daily new-word number is a goal the student sets, and "Learn 10 more" is always one click away.

The nav label and the H1 are "Words".

##### 1. Shell and navigation

- **Nav**: `UI.NAV` gains `['words','/words/','Words']` after Practice. The nav reads Today · Practice · Words · Tests · Plan · Results.
- **Icon**: `ICON.words` is two stacked rounded cards, the back one offset up and to the right and the front one carrying two text lines, drawn with the 1.6 stroke of the other icons. `ICON.wordplus` is the same with a small +.
- **Phone tabs** become `repeat(6,1fr)`: 65px a tab at 390px, and "Practice" at 10.5px is about 44px wide. If other sections also grow the nav past 6, the phone bar gets a **More** tab. That is decided once across sections (see shared needs).
- **`SECTION`** maps `words-study`, `words-run` and `words-mine` to `words`.
- **Words tabs** (`UI.wordsTabs(host, active)`): a 4-segment control under the H1, in the Plan steps style (tile fill; the selected segment in wash with a 1.5px amber inset). Each segment is its own route:
  - Library `/words/`;
  - Flashcards `/words/study/?mode=cards`;
  - Quiz `/words/study/?mode=quiz`;
  - My words `/words/mine/`, which carries an orange dot and the due count whenever anything is due.

  Below 420px the labels shorten to Library · Cards · Quiz · Mine.
- **Quick add from anywhere**: `.bar-end` gets a **+ word** icon button (`ICON.wordplus`, aria-label "Add a word"), before the streak. It appears on every page with the shell and is absent from `/practice/session/`, `/words/run/`, `/test/` and `/diagnostic/` while a sitting is live. It opens the Add sheet (§10). On Words pages, `N` opens the same sheet.
- **Add a selection**: in the practice session, the question of the day, the challenge (once answered) and the report review, selecting 1–6 words of stem or rationale text shows a small floating **Add to my words** button above the selection (`UI.pop` anchored to the selection rect). It opens the Add sheet with Word prefilled, and the entry records its source ("From a Circles question · Sep 23"). It never appears in the test window.
- **No floating button** anywhere: theirs covers Next.

##### 2. What a word is (content model)

The content is authored as JSON under `server/words/`: `math.json`, `sat.json`, `transitions.json`, `confusions.json` and `collections.json`. The definitions, examples and tells are our own wording. We use no third-party list: not their "650" and not The College Panda's 400.

###### Entry fields

- `slug`, `word`.
- `also`: inflections and alternate spellings.
- `sense`: the disambiguator for a split word.
- `pos`: n. / v. / adj. / adv. / phrase. Required on SAT words and transitions, optional on math words.
- `collection`.
- `topics`: bank topic slugs for math words; subject tags for SAT words; the logic group for transitions.
- `level`: easy / medium / hard, authored.
- `tier`: core / advanced, SAT words only.
- `meaning`: 1–2 sentences.
- `short`: at most 60 characters, used on tiles, in popovers and in quiz options and feedback.
- `examples`: 1–3 authored sentences, with the word marked `[[ ]]` so it can be highlighted.
- `symbols`: the notation line for math words, e.g. "In y = a(x − h)² + k, the vertex is (h, k)."
- `figure`: optional key of an inline SVG in ui.js.
- `same`, `opposite`, `related`: lists of slugs, or plain text when the word is not in the library.
- `cloze`: 1–3 fill-in items using `____`. For SAT words each is a 2–3 sentence "In context" text.
- `pairs`: transitions only. 2–4 sentence pairs whose correct link is this transition.
- `second_sense`: true when the SAT tests a meaning that is not the common one (qualify, sanction, appreciate, temper, champion, arrest, yield). These words have a split-sense entry.
- `match`: regexes that find the word in stems. They use a restricted syntax that reads the same in Python and JS: letters, spaces, hyphens, `(?:a|b)`, an optional `s?` or `es?`, and `\b`.
- `gloss`: underline inside questions. False for tiny words like "of" and "per".
- `cloze_templates`: bank templates approved for the "In a real question" blank.
- `bankless`: true when no template uses the word. Always true for R&W words today.

###### Collections, about 1,090 entries

**MATH LANGUAGE**

- **Question language**, about 26: which of the following, value of, in terms of, respectively, must be true, could be, is closest to, equivalent, satisfies, constant, positive constant, nonzero, integer, distinct, real number, intersect, in the xy-plane, best interpretation, approximately, and so on.
- **Word-problem phrases**, about 28: less than, more than, fewer than, subtracted from, decreased by, increased by, of, per, each, twice, twice as many, the sum of, the difference of, the product of, the quotient of, the ratio of … to …, percent of, percent more than, percent less than, what percent, at least, at most, no more than, no less than, exceeds, consecutive integers, markup, discount.
- **Algebra**, about 36: coefficient, constant term, like terms, solution, solution set, no solution, infinitely many solutions, slope, rate of change, y-intercept, x-intercept, slope-intercept form, point-slope form, standard form, parallel, perpendicular, ordered pair, system, substitution, elimination, inequality, compound inequality, boundary line, function, input, output, f(x) notation, linear model, absolute value, and so on.
- **Advanced Math**, about 38: quadratic, parabola, vertex, axis of symmetry, vertex form, factored form, zero, root, factor, polynomial, degree (polynomial), leading coefficient, exponent, base (power), exponential growth, exponential decay, growth factor, growth rate, decay factor, initial value, rational expression, radical, extraneous solution, discriminant, quadratic formula, completing the square, maximum, minimum, geometric sequence, common ratio, and so on.
- **Problem-Solving & Data**, about 45: ratio, unit rate, proportional, constant of proportionality, unit conversion, density, percent change, percentage point, mean, median, mode, range (data), standard deviation, outlier, frequency table, histogram, dot plot, box plot, quartile, interquartile range, scatterplot, line of best fit, association, probability, conditional probability, two-way table, sample, population, random sample, random assignment, margin of error, estimate, plausible, bias, causation, and so on.
- **Geometry & Trig**, about 45: area, perimeter, volume, surface area, similar, congruent, scale factor, transversal, vertical angles, supplementary, complementary, alternate interior, corresponding angles, isosceles, equilateral, exterior angle, triangle inequality, hypotenuse, leg, Pythagorean theorem, special right triangles, sine, cosine, tangent (ratio), cofunction, degree (angle), radian, arc, arc length, arc measure, sector, central angle, inscribed angle, chord, tangent line, radius, diameter, circumference, center, unit circle, equation of a circle, coterminal angles, and so on.

**READING & WRITING**

- **SAT words: core**, about 300: the academic words that recur in SAT-style passages and answer choices. For example: ambiguous, bolster, candid, corroborate, discrepancy, mitigate, plausible, undermine, underscore, viable.
- **SAT words: advanced**, about 450: rarer words that turn up in harder Words-in-Context choices.
- **Transitions**, about 70, by logic:
  - contrast: however, nevertheless, in contrast, conversely, on the other hand;
  - concession: still, admittedly, even so;
  - cause and effect: therefore, consequently, thus, as a result, hence;
  - addition: moreover, furthermore, in addition, additionally;
  - example: for example, for instance, specifically;
  - sequence: subsequently, meanwhile, finally, previously;
  - clarification and emphasis: in fact, indeed, that is, in other words;
  - similarity: likewise, similarly;
  - conclusion: ultimately, in sum.

**MINE**

- **My words**, plus any lists the student names (e.g. "English").

###### Confusions

About 40 meaning mix-ups, about 60 lookalikes and the split senses. Each has `id`, `kind` (meaning | lookalike | sense), `words` [2], `tell` (one sentence that separates them), `links` [{template, reason regex}] for math, and `bankless` when there are no links.

- **Meaning mix-ups**: median~mean, mean~mode, radius~diameter, circumference~area, area~perimeter, volume~surface area, hypotenuse~leg, sine~cosine, tangent ratio~tangent line, complementary~supplementary, similar~congruent, scale factor~area scale (k vs k²), degrees~radians, arc length~arc measure, central~inscribed angle, slope~y-intercept, x-intercept~y-intercept, zero~y-intercept, vertex~y-intercept, coefficient~constant term, factor~term, growth factor~growth rate, percent~percentage point, percent of~percent more than, at least~at most, exceeds~at least, sample~population, random sample~random assignment, correlation~causation, no solution~infinitely many solutions.
- **Lookalikes**: affect~effect, elusive~illusory, allusion~illusion, eminent~imminent, discreet~discrete, complement~compliment, principal~principle, prescribe~proscribe, ingenious~ingenuous, adverse~averse, credible~credulous, deprecate~depreciate, flaunt~flout, imply~infer, precede~proceed, censor~censure, perspective~prospective, and so on.
- **Split senses**: degree (angle / polynomial), base (power / triangle), range (data / of values), tangent (ratio / line), sanction (approve / penalize), qualify (limit / meet a requirement), novel (new / book), temper (moderate / mood), appreciate (value / rise in value).

**Linking is curated, not guessed.** Naive regex links go wrong too often:

- "complement" matched sample-complement reasons;
- "less than" matched "one power less than";
- "less than|order|subtract" hit 102 templates in a 3-seed scan;
- "degree", "base", "range" and "mean" each have two senses.

`tools/build_words.py` proposes links, and an author confirms them in the JSON.

###### Derived per word (`server/words_index.json`, generated)

- `tests`: templates whose skill label names the word.
- `uses`: templates whose stems contain the word, restricted to the word's topics.
- `bank`: |tests ∪ uses|.
- `difficulty`: the mean of the linked templates' tiers from `blueprint.abilities()` (easy 1, medium 2, hard 3), cut at 1.67 and 2.34. It falls back to `level`.
- `bank_examples`: 3 stem excerpts {template, seed, text, start, end}, so the sheet and card backs show a real question instantly.
- Per confusion: its live templates.

###### Build checks (exit 1 on any)

- Duplicate slug, or a duplicate (word, sense).
- A missing meaning, a `short` over 60, no example and no cloze, or a missing `pos` where one is required.
- A math word with no link and no `bankless`.
- A confusion link that matches on none of 20 seeds.
- A `cloze_template` whose stem no longer contains the word.
- A word with fewer than 3 valid distractors for any quiz type it can be asked in (the rules are in §7).
- A transitions pair whose four candidate options do not span four logics.
- A `match` regex outside the restricted syntax.

The tool prints proposed new links for an author and never writes them. It runs like `tools/build_mocks.py`.

##### 3. Library `/words/` (data-page `words`)

###### Desktop (1280), top to bottom

1. **Title row**
   - H1 "Words", with the meta line "1,090 words · 31 known · 12 due" beside it.
   - On the right, a search field and **Add a word** (quiet, + icon).
     - The placeholder is "Search words and meanings", and `/` focuses the field.
     - It matches word, `also`, `short`, `meaning` and `same`, case- and accent-insensitive.
     - Word-prefix matches rank first.
2. **Words tabs.**
3. **Today strip**: four stat tiles in a row.
   - **Due today**: a big number and a **Review** pill that starts the due flashcard deck directly. At 0 it reads "Nothing due · next: 6 on Thu".
   - **New today**: "4 / 10" with a thin bar and **Learn 10**, and the helper "Daily goal, set in Plan". Once the goal is met it reads "Goal met" with **Learn 10 more**. It is never a cap.
   - **Math word of the day**: the word (700 20px), its `short` and **Open**.
   - **Word of the day** (SAT): the same layout.

   Both words of the day are the same for everyone that day.
4. **Collections**: three labelled groups, MATH LANGUAGE · READING & WRITING · MINE, led by an **All** tile.
   - Each tile shows its name, "26 words", an ink known-bar with "4 known", and an orange dot with the count when anything is due.
   - Clicking a tile toggles that collection in the Collection filter (aria-pressed; wash with an amber inset when on).
   - MINE ends with a **New list** tile.
   - The groups wrap below 1100px.
5. **Filter bar** (`UI.filters`, dropdown chips `.fchip`, each showing its current value):
   - **Collection ▾**: multi-select, the same state as the tiles.
   - **Topic ▾**: multi-select in three groups:
     - the 19 math topics by domain, each with its glyph and a count;
     - SAT subjects: General / Academic / Science / History & social studies / Literature & arts / Economics;
     - transition logics.
   - **Difficulty**: Easy · Medium · Hard, a multi-toggle in the practice-map style, with counts.
   - **Status ▾**: All / New / Learning / Known / Due today / Saved / From my mistakes / Missed lately / Looked up / Two meanings / My own, each with a count.
   - **Part of speech ▾**: noun / verb / adjective / adverb / phrase. Shown when the view holds R&W words.
   - **Sort ▾**: A–Z / By topic / Most used in the bank / Due soonest / Weakest first / Level / Recently added.
   - **Meanings**: a toggle that adds each word's `short` under it on the tiles. It is off by default, so the grid doubles as a self-test.
   - **Select**: toggles tile checkboxes.
   - On the right, a live count ("42 words") and **Clear** whenever any filter is set.
   - The URL carries every filter (`?c=&t=&d=&s=&p=&sort=&m=&q=`), so a view can be linked and Back works.
6. **Legend** (mono 12px): `●●●○○ strength · DUE · ★ saved · ● from your mistakes · ▮▮▯ difficulty`.
7. **Grid**
   - Columns: 6 at 1100px and up, 4 at 760–1099, 3 at 560–759, 2 below. Gap 8px.
   - **Tile** `.wtile` is a `<button>`: min-height 92px, tile fill, 10px radius, no border.
     - The word, 600 16px, up to 2 lines.
     - A mono tag: the part of speech, the sense, or MINE.
     - A meta line with the topic's short name, or the `short` meaning when Meanings is on.
     - Bottom row: strength pips `.pips` on the left, difficulty bars `.dbars` on the right (aria-label "Medium").
     - Top-right corner: ★ (orange fill when saved), an orange dot for an open mistake, and "DUE" in amber-deep mono when due.
   - Difficulty is shown as bars plus a label, never as colour, because orange is the only accent.
   - Hover shows `tile-2`. A click opens the word sheet (`?w=slug`). In Select mode a click checks the tile and shift-click selects a range.
   - With Sort = By topic, the grid is grouped under headers: glyph, name, "8/21 known" and an mbar.
8. **Study bar**: sticky at the bottom. It is their Start Practice Session, but it acts on the filter or the selection, not the whole collection.
   - On the left: "42 words · 12 due · 30 new", or "5 selected".
   - On the right: **Quiz** (a tile button) and **Flashcards** (a pill), both skipping setup and using the last options.
   - Above 30 words, a helper reads "Takes 30: due first, then new".

###### States

- **Loading**: 18 static skeleton tiles, with no looping shimmer.
- **Error**: "Words did not load." with Retry.
- **No match**: "No words match these filters." with Clear filters.
- **New student**: every tile has empty pips. Due reads "Nothing due yet" and New reads "Learn your first 10".
- **Many tiles**: the first 400, then "Show 200 more".
- **`?w=unknown`**: the inline message "No word called “x”."

##### 4. Word sheet (`UI.word.open(slug, {list})`)

A dialog, 720px wide and at most 88vh tall, scrolling inside. Full-screen on a phone.

- **Head** (sticky):
  - the word (800 32px), with a **speak** button beside it (`speechSynthesis`, en-US voice; hidden when the device has no voice);
  - the part of speech, "also: vertices" and the sense tag;
  - tools: ★ Save (aria-pressed), ⚑ Report, ‹ › previous and next through the list it was opened from (←/→), and X (Esc).
- **Chip row**: the collection chip, topic chips (`UI.chip` with a glyph for math topics), the level with its bars, and, for math words, "Used in 14 kinds of bank question".
- **MEANING**: serif 19px.
- **EXAMPLES**, for R&W and own words: the authored sentences in serif, with the word in wash and an amber underline.
- **IN SYMBOLS**, and **FIGURE** when there is one (math).
- **IN A REAL QUESTION** (math words with bank > 0):
  - An instant excerpt from `bank_examples`, with the word highlighted, and a meta line such as "Nonlinear functions · the vertex of a parabola · Hard".
  - **Answer it** makes a 1-question drill of that exact (template, seed) (`source:'word-example'`). The question expands inline through `UI.question`, is answered through `/api/drill/{id}/answer`, and shows the key, the named mistake and the rationale.
  - **Another** makes a fresh item from a different template when there is one, through the same kind of 1-question drill.
  - Loading shows "Finding one…". A failure shows "Could not make one." with Try again.
- **SAME AS / OPPOSITE OF**: word chips that open that word's sheet, or plain text for words not in the library.
- **NOT THE SAME AS**: one row per confusion, by kind.
  - The row starts with "vs **y-intercept**" (a meaning mix-up), "looks like **illusory**" (a lookalike) or "other meaning: to penalize" (a split sense).
  - The tell follows in serif 15px.
  - For linked math mix-ups, a meta line reads "An option in 7 kinds of question is built on this mix-up".
  - When the student has picked such an option, an orange dot and "You fell for it 3× · last Sep 21".
  - **Drill it** (`POST /api/drill {confusion, count:10}`) opens the practice session. It is absent for bankless confusions.
  - Lookalike rows get **Quiz the pair**, a 6-item quiz of the two words.
- **YOUR RECORD**:
  - the pips and the status, e.g. "Learning · next review Thu, Sep 26";
  - "Reviews 6 · right 4", with a by-type line such as "Meaning → word 3/3 · In context 1/2";
  - for math words, "Questions that use it: 9 answered · 6 right" with a mini bar, read from `attempts` on the linked templates;
  - "First seen Sep 12" and "Looked up 2× in questions".
- **Footer** (sticky):
  - Math words: a **Practice 10 questions with it** pill (`POST /api/drill {word, count:10}`) and **Flashcards from here** (quiet).
  - R&W words: a **Flashcards from here** pill and **Quiz it with its lookalikes** (quiet).
  - Flashcards from here starts a cards run over the list the sheet was opened from, beginning at this word, front first. That is their tile → flashcard, kept.
  - An overflow menu holds **Reset progress**, behind a confirm.
- **Own word**: the same frame, with the student's meaning, example, same, opposite, notes and source. **Edit** and **Delete** are in the head, and there are no bank blocks.

##### 5. Study setup `/words/study/?mode=cards|quiz` (data-page `words-study`)

The H1 is "Flashcards" or "Quiz", above the tabs. The page opens preset to the best deck (Due when anything is due, otherwise New), so one click or Enter starts, like their tab. Desktop has two columns: options on the left, and an **At a glance** panel on the right in the Plan style.

1. **DECK**: radio tiles, each with a count.
   - Due today (12).
   - New ("Next 10 from the skills you're working on").
   - Missed lately.
   - Saved.
   - From my mistakes.
   - Looked up.
   - A collection ▸ (inline select).
   - A topic ▸.
   - My own ▸ (one of the lists).
   - From the Library, shown only when arriving with a filter or a selection ("42 from your filter").

   An empty deck is disabled with a helper, e.g. "Star words to build this deck".
2. **HOW MANY**: cards 10 · 20 · 30 · All (capped at 200); quiz 10 · 20 · 30 · ∞.
3. **Cards only**: SHOW FIRST Word · Meaning · Mixed; ORDER Due first · Shuffle · A–Z.
4. **Quiz only**:
   - **QUESTION TYPES**, a multi-toggle that needs at least one: Meaning → word · Word → meaning · Fill the blank · In context · Pick the transition · In a real question · Translate the phrase.
   - A type the deck cannot supply is disabled with its reason:
     - Pick the transition needs transitions.
     - In a real question and Translate need math words.
     - Own words allow the first two types only, and need 4 or more words.
   - **TIMER per question**: Off · 15 s · 30 s · 60 s.
5. **At a glance**: "20 cards · about 5 min" (10 s a card, 20 s a quiz item, or the timer value), "12 due · 8 new", the order, and a **Start** pill (Enter).

The last options for each mode are remembered in `localStorage` (`satf.words.study`, wrapped in try/catch).

##### 6. Runner `/words/run/?id=`, flashcards (data-page `words-run`)

- **Shell**: the practice session's own (the `.run-*` styles move to ui.css).
  - X ends the run and shows the summary, or returns to where the run started if nothing was graded.
  - Progress segments: up to 24, ink for don't know, amber for know, an outline on the current card. Beyond 24 it shows "7 / 30".
  - Tools: 🔊 Speak, ★ Save, ⚑ Report.
- **Card** `.fcard`:
  - centred, at most 620px wide and at least 340px tall (56vh on a phone);
  - two ghost cards behind it, offset 8px and 16px, in `tile-2` and `mat`;
  - "18 left" in mono under the stack.
- **Front**: a chip row (collection · level); the word (800 clamp(36px, 6vw, 56px)), or in Meaning-first mode the meaning (serif 24px); the part of speech or sense tag; and a `.keys` hint "Space" on hover devices.
- **Back**:
  - The flip is rotateY(180°) over .45s, or a .15s crossfade under reduced motion.
  - Content, top to bottom: the word, small; MEANING; EXAMPLES or IN SYMBOLS; IN A REAL QUESTION (math, instant from the index); SAME AS / OPPOSITE; up to two NOT THE SAME AS rows, then "+1 more", which opens the sheet; and **Open word**.
- **Controls**:
  - Before the flip, a **Show** pill (Space).
  - After the flip, two equal buttons: **Don't know** (tile, `1`) and **Know** (pill, `2`).
  - Always present: **‹ Previous** (←) and **Next ›** (→).
    - Next on an unflipped or ungraded card skips it. A skipped card goes once to the end of the run. It is not graded and not counted.
    - Previous walks back through any card, shown flipped with its grade. Where that grade is still the word's latest review, **Change to Know** or **Change to Don't know** is offered.
  - After a grade, a status line shows for 900ms, then the next card: "Back in 3 days", "Again in 3 cards", "Known · back in 16 days" or "Early review · stays Thu".
- **Touch**: after the flip, swipe right for Know and left for Don't know. The card tilts up to 8° with the finger and grades past 80px. No tilt under reduced motion.
- **Requeue**: Don't know puts the card back 3 cards later, at most twice a run. The bar grows by one animated segment, the way practice shows a repair.

##### 7. Runner, quizzes

The shell is the same. Every item renders through `UI.question(host, q, {head:{label, glyph}})`, so options, the key and the verdict look exactly like practice. A mono count line under the segments reads "5 right of 7" (theirs has no score at all).

###### Types

- **Meaning → word**: the meaning (serif 20px) and "Which word means this?", with 4 words.
- **Word → meaning**: the word (Archivo 700 28px) and "What does it mean?", with 4 `short` meanings.
- **Fill the blank**: an authored cloze ("The ____ of y = (x − 3)² + 5 is (3, 5)."), with 4 words.
- **In context** (SAT words): an authored 2–3 sentence text with a blank and "Which choice completes the text with the most logical and precise word?", with 4 words of the same part of speech.
- **Pick the transition**: an authored sentence pair with a blank opening the second sentence, and 4 transitions from 4 different logics.
- **In a real question**: an approved bank stem excerpt with the word blanked, 4 words, and the meta line "From a Nonlinear functions question". Every one is new.
- **Translate the phrase**: "Which expression represents 7 less than 3 times a number x?", with 4 expressions (serif) from `server/phrases.py`. Every wrong option carries its misreading, and the items are unlimited.

###### Distractors

- Order of preference:
  1. up to two of the word's confusions, including lookalikes, which are the real trap;
  2. then words in the same topic;
  3. then the same collection.
- Never a word in the target's `same` list, or one sharing a `same` entry with it (one hop).
- For SAT words and transitions, always the same part of speech.
- For Word → meaning, meanings of similar length (within ±40%).
- Own words take distractors from own words only.

###### Timer

A thin bar under the head drains over the time, with mm:ss in the top bar. Under 5 s the digits turn ink-deep and bold. At zero the item is revealed as wrong, with "Out of time".

###### Verdict (the practice one)

- The key is always shown in amber, and the student's pick is struck through.
- The `.mistake` line depends on the pick:
  - a confusion: "Mixed up median with mean", or "Mixed up elusive with illusory", followed by the tell;
  - another word: "“mode” means: the value that occurs most often";
  - a transition: "“However” signals a contrast, but the second sentence adds a point";
  - a phrase misreading: "Wrote it in the order it is read. “Less than” flips the order."
- A right answer gets a **Why** toggle that shows the meaning and one example.
- Links: **Open word**, and on a math confusion **Drill this mix-up in math**.
- ★ Save and `S` unlock with the verdict. Before it they are disabled, because the target is hidden.
- A **Next** pill, or Enter.

###### Keys

A–D or 1–4 choose, Enter goes on, S saves (after the verdict), O opens the word, P speaks it.

##### 8. Summary (both modes)

The practice summary layout:

- A big score ("14 / 20"; for cards "14 known / 20") and "6 min".
- One row per collection or topic: glyph, name, a known-bar that animates from before to after, and "right/asked".
- **Moved to Known**: word chips.
- **Still learning**: chips with their next dates.
- "Next reviews: 8 tomorrow · 7 in 3 days · 5 in a week".
- Quiz only: **By type** (Meaning → word 8/10 · In context 3/5 · Translate 4/5).
- **Mix-ups**: `.mistake` rows ("Mixed up median with mean ×2", "elusive / illusory ×1"). Each math row has **Drill it in math**, and each lookalike row has **Quiz the pair**.
- **Skipped**: "3 skipped", with **Study them**.
- **Up next**: chips for the next deck ("8 more due", "10 new", "Quiz these 20"), a **Keep going** pill and a **Library** quiet button.

Reloading a finished run shows the summary. That is where Results and `/results/report/?id=<words id>` land.

##### 9. My words `/words/mine/` (data-page `words-mine`)

1. **Stat tiles**: 8 in a 4×2 grid (2×4 on a phone). Each tile filters the list, and a selected tile is wash with an amber inset.
   - Due today (with Review).
   - Learning.
   - Known, with the helper "Right 3 times, over 10+ days".
   - Saved.
   - My own.
   - From my mistakes, with the helper "Words behind the mistakes you still have open".
   - Missed lately.
   - Looked up.
2. **Forecast**, "Due in the next 14 days":
   - 14 bars, today in amber and the others in ink at 30%;
   - mono day initials, with the date on hover;
   - the exam day marked when it falls in range;
   - on the right: "Reviewed today 24 · this week 130 · review streak 5 days".
3. **Filter bar and search**: the same `UI.filters` as the Library, Collection ▾ included.
4. **List** `.wlist`:
   - Desktop is a table: ☐ | Word | Collection · topic | Level | Strength | Next review ("Due" in amber-deep, or "Thu 26") | Quiz (right/total) | Last reviewed | ★.
   - Clicking a column head sorts by it, and clicking a row opens the sheet.
   - 120 rows show, then "Show 120 more".
5. **Bulk bar**: "5 selected · Flashcards · Quiz · Save · Unsave · Move to list · Reset progress · Delete (own only)", with Clear.
6. **Tools**: Add a word · New list · Import · Export CSV · Print this list. The print stylesheet sets word, part of speech and meaning in two columns.
7. **Lists** (own): rename and delete (a delete moves the words to "My words"). Each list is a collection tile in the Library's MINE group.

**Empty states**

- **New student**: "No words yet. Study a deck in the Library, star words to keep them, or add your own." with Library and Add a word.
- **Nothing due**: "Nothing due. Next: 6 on Thu, Sep 26."
- **From my mistakes, empty**: "None of your open mistakes points to a word."
- **Filtered to nothing**: "No words match these filters." with Clear filters.

##### 10. Add, edit and import own words

**Add sheet**: a 560px dialog, or a full-height bottom sheet on a phone.

- **Fields**:
  - Word*, up to 60 characters.
  - Meaning*, up to 400, in a 3-row textarea.
  - Part of speech (optional select).
  - Example, up to 300.
  - Same as and Opposite of: comma lists of up to 10 each.
  - Notes, up to 1000.
  - List: a combobox of the student's own lists, defaulting to "My words", with names up to 30 characters.
  - Source: read-only when the word came from a selection.
- **Buttons**: Save (pill), Save and add another, Cancel.
- **Inline errors**: "Add the word" / "Add what it means".
- **Duplicates**:
  - An own duplicate: "You already have “ubiquitous”." with an Edit link.
  - A library match: "“median” is in the library." with **Save that one**, which stars it.
- **Edit and Delete**: Edit opens the same sheet, prefilled. Delete confirms first: "Delete “x” and its review history?"
- Own-word text is always set with `textContent`, never HTML.

**Import sheet**

- A textarea for "One per line: word, then a tab, ' - ', ':' or ' — ', then the meaning". A Quizlet export (tab-separated) pastes in as is. A CSV with a `word,meaning` header also works.
- The target list.
- A live preview table with a status per row: new / duplicate / not understood.
- An **Add 18 words** pill, then the result "Added 18 · skipped 2", with the reasons.

**Export**: `GET /api/words/mine.csv`.

##### 11. Words across the site

- **Tap-to-define** (`UI.gloss(el)`):
  - **Where**: stems and rationales in the practice session, the question of the day, the challenge and the report review. Never on answer options, and never in the test window or the diagnostic during a sitting.
  - **What gets underlined**: up to 3 library terms per block with `gloss:true`, taking the longest match first, the first occurrence only, whole words, in text nodes only. The underline is a dotted `--faint` line.
  - **Popover**: a tap opens a `.pop`, 300px wide, with the word, its `short`, 🔊, ★ Save and **Open**. Esc or an outside click closes it (theirs ignores Esc), and focus returns to the term.
  - **Logging**: each tap posts `/api/words/lookup`, once per word per session. The word shows as Looked up and goes to the front of the New deck.
  - **Setting**: "Underline math words in questions" on Me, on by default.
- **Add a selection**: see §1.
- **Practice verdict**: when the named mistake is a linked confusion, a line under it reads "Words: median · mean". The chips open the sheet, and the words join From my mistakes.
- **Mistakes page**: each open trap row gets its word chips, and the header gains **Review these words (N)**.
- **Today**: a Words tile in the right column, under Challenge.
  - It shows the cards icon, "Words", a big "12" with "due", the meta "4/10 new today", and **Review**, which starts the due deck.
  - Below that, two lines: "Math word · discriminant: how many real solutions a quadratic has" and "Word · corroborate: to confirm with evidence". Each opens the sheet.
  - A new student sees **Learn 10**.
- **Plan**:
  - **Step 4, Words row** under the domains:
    - the switch "Words each study day", on by default;
    - NEW WORDS A DAY 5 · 10 · 20 (default 10);
    - NEW WORDS FROM Math language · SAT words · Transitions (multi-select, default Math language);
    - the helper "Due reviews come first".
  - **At a glance** gains "Words · 10 new a day · about 6 min".
  - **The day card gains a Words task**:
    - It reads "Words · 12 due · 10 new · about 6 min". Minutes = due × 10 s + new × 25 s, capped at a third of the day.
    - A reason line, e.g. "12 words come back today; the new ones are from Circles and Percentages, the skills you're working on."
    - Launch buttons: **Review cards** (the due deck), **Learn 10** (the New deck) and **Quiz** (today's words).
    - It is done automatically when nothing is left due and the new goal is met. It can also be marked done or skipped through the Plan's task model.
  - **Budget**: the words minutes come out of the day, so `per_session()` sizes the coach set from minutes minus words minutes, with a floor of 5 questions.
  - **Calendar**: future days show "Words · ~N due" from the forecast.
- **Me**:
  - stat tiles Words known, Words studied, Saved words and Reviews this week;
  - the **Include words** switch (the same field as the plan);
  - New words a day, and New words from;
  - the underline switch.
- **Results**:
  - a Words block with a stacked New / Learning / Known bar per group (Math language / SAT words / Transitions / Mine), quiz accuracy over the last 30 days, and reviews a day over 14 bars;
  - the sittings list gains a **Words** filter (`/api/history?kind=words`) whose rows open `/words/run/?id=`.
- **Streak and study time**: a day with 10 or more word reviews keeps the streak. Review time counts as study time, capped at 60 s a review.
- **Achievements**, handed to Me: 50 / 250 / 1,000 words known, every word in a collection known, and a 7-day review streak.

##### 12. Spaced review rules (`server/words.py`)

- **Boxes**: 0 is new. Boxes 1–5 are due again after 1, 3, 7, 16 and 35 days.
- **Know on a new word (box 0)**: box 2.
- **Know on a due word**: box + 1, up to 5.
- **Know on a word not yet due** (an early review, e.g. in a collection quiz): no promotion. Box and due stay as they are, and the review is logged.
- **Don't know, a wrong answer or a timeout**, due or not: box 1, due today, lapses + 1, and requeued in the run.
- **At most one box up per word per local day.**
- **Known** is box 4 or higher, so it is reachable no sooner than day 10: know on day 0, then on day 3 or later, then on day 10 or later.
- **Exam cap**: when an exam date is set and a due date would land on or after it, the due date becomes max(tomorrow, exam − 1). Every word is seen once more before the test.
- **A quiz grades only its target word**, never the distractors.
- **Statuses**:
  - New: box 0 or no row. Learning: boxes 1–3. Known: box 4 or higher.
  - Due: due ≤ today, in the learner's own time (X-Tz is JavaScript's getTimezoneOffset minutes, as elsewhere).
  - Missed lately: a wrong or don't-know in the last 14 days with no right answer since.
  - Looked up: a lookup in the last 30 days, and not Known.
  - "New today" counts words whose first grade came today.
- **New deck order**:
  1. Looked-up words and words linked to open traps.
  2. Words in the coach's current topics (`progress.coach`).
  3. Words in topics the student has worked on.
  4. SAT core before SAT advanced.
  5. By bank count.
  6. A–Z.

  All of this is filtered to the plan's New words from. Question-language and phrase words are interleaved one in three.

##### 13. Phone (390)

- **Library**:
  - The H1, with the meta line under it.
  - A full-width search field and a 40px "+" button.
  - Tabs as 4 segments.
  - The Today strip and the collection groups as horizontal scroll-snap rows, with tiles at 78% width and 160px.
  - Filter chips in one scroll row: Collection ▾ · Topic ▾ · Difficulty ▾ · Status ▾ · Part of speech ▾ · Sort ▾ · Meanings. Each opens a bottom sheet (`dialog.sheet.bottom`, at most 80vh) with 48px option rows, check marks, Clear and a Done pill.
  - A 2-column grid.
  - The study bar fixed above the tab bar, with 170px of bottom padding under the page.
  - No horizontal page scroll.
- **Sheet**: full-screen, with a sticky 56px head and a sticky footer pill.
- **Setup**: one column. At a glance becomes a sticky bottom bar, "20 cards · 5 min [Start]".
- **Runner**:
  - No tab bar. The card spans the width minus 32px.
  - The grade buttons sit 50/50 at the bottom, above the safe area, with ‹ › as 44px icon buttons at the card's lower corners.
  - Swipe grading works.
- **My words**: 2×4 stat tiles, the forecast at full width, and the table as stacked rows ("vertex ●●●○○ / Advanced Math · next Thu 26 · quiz 4/5"), with a fixed bulk bar.

##### 14. Accessibility and keys

- **Tiles** are buttons with a full aria-label: "vertex, noun, Advanced Math, medium, learning, due today, saved". (Theirs are not focusable at all.)
- **The flip** announces the back face through aria-live=polite, and a grade announces "Know, back in 3 days".
- **Dialogs** trap focus and close on Esc.
- **The quiz verdict** reuses the practice status region.
- **Speak** is a button with the label "Say vertex".
- **Keys**:
  - Library: `/` search, `N` add a word.
  - Sheet: ← → previous and next.
  - Cards: Space flip, 1 / 2 grade, ← → previous and next, S save, P speak.
  - Quiz: A–D or 1–4, then Enter; S (after the verdict), O, P.
- **Reduced motion**: no flip rotation, no tilt, no bar growth.

### 3.8.4 Extras: what they missed

- **A bigger, cleaner R&W library than theirs**: About 750 SAT words plus about 70 transitions, all in our own words, with part of speech, 2–3 examples, synonyms, antonyms and lookalikes. The build fails on duplicates, which their default collection has.
- **Math language wired into the bank**: About 220 terms that SAT Math is written in, each linked to the templates that use or test it. No finite-bank competitor can link words to questions that never run out.
- **Real questions as examples, never the same twice**: Their card has one fixed sentence. Ours shows a live bank question that uses the word, with Another for more and Answer it inline, and costs no session until the student asks.
- **Practice 10 questions that use this word**: It turns a definition into points: a drill restricted to the templates that use or test the word.
- **Mix-up drills (Drill it)**: Every curated confusion is linked to the templates whose options include that exact mix-up (radius vs diameter, sample vs population). The student practises the trap itself, with fresh numbers each time.
- **Mistake → words link**: When a practice verdict names a word confusion, it shows the words and feeds From my mistakes. Their vocabulary never touches their questions.
- **Tap-to-define inside questions and rationales, logged as Looked up**: A tap gives the meaning without leaving the question, and the word goes to the front of the New deck, because a lookup is proof the student did not know it. It is off in the live test.
- **SAT-style In context and Pick the transition quizzes**: They match the real R&W item forms (Words in Context and Transitions). Every wrong option says why it is wrong, which is our misconception format carried over to R&W before there is an R&W bank.
- **Translate-the-phrase quizzes with named misreadings**: '7 less than 3 times x' and similar items are generated without limit and self-checked, and every wrong option names its misreading.
- **Distractors that cannot both be right**: Their live quiz offered ingenious / imaginative / innovative / original for one definition. Ours excludes synonyms and one-hop synonyms, matches part of speech, and the build proves every word has at least 3 valid distractors.
- **Quiz feedback that explains the pick**: Theirs prints 'Correct answer: X' at most. Ours names the mix-up and its tell, says what the picked word means, or names the transition's logic.
- **Lookalike and two-meaning words as first-class confusions**: elusive/illusory and sanction (approve / penalize) get tells, Quiz the pair, and a Two meanings filter. Secondary meanings are exactly what Words in Context tests.
- **Honest spaced review with a 14-day forecast and an exam cap**: Known is earned over 10+ days, early reviews do not inflate it, every word comes back before the exam, and the forecast shows the coming load. Their Due Today stayed at 0 after grading.
- **Free Previous / Next with regrading, a visible outcome and requeue**: Every grade says what happens next ('Again in 3 cards', 'Back in 3 days'). A missed card comes back in the same run, and any grade that is still the latest can be changed.
- **Search, status filters, a Meanings toggle, per-collection progress**: Their library has none of these. A student can find 'slope', see how much of each collection they know, and scan meanings or hide them to self-test.
- **Pronunciation**: The device's own speech voices say any word, including own words, with no content or cost.
- **Two words of the day, the same for everyone**: A math term and an SAT word sit beside the question of the day on Today, using the daily date hash.
- **Add a word from any page without covering anything**: A + in the bar, plus Add to my words on text selected in a question. Their FAB sits on top of Next.
- **Own words with named lists, paste and Quizlet import, CSV export, print**: A student can bring decks they already have, study them with the same tools, and keep their data.
- **Words inside the plan's day budget**: A Words task sized in minutes, with a reason and three launch buttons. It completes itself, and the practice set shrinks to fit, so no day runs longer than the student said.
- **Missed lately and Skipped decks**: The words that just went wrong, or were skipped, are one tap from another pass.
- **Word achievements**: 50 / 250 / 1,000 known, a collection completed, a 7-day review streak. Theirs are four hard-coded tiles and a dead View All.

### 3.8.5 Server changes

Tables and columns here are added by F4 as listed in §2.5; the drill fields map through §2.6; prefs through §2.7.

- **server/words/*.json (new, authored content)**: math.json, sat.json, transitions.json, confusions.json and collections.json, with the entry fields in design §2: about 220 math, about 750 SAT and about 70 transition entries, and about 100 confusions of kind meaning, lookalike or sense. All wording is our own. Required on every entry: meaning, short (≤60), ≥1 example or cloze, match[] (math), and pos (SAT and transitions).
- **tools/build_words.py → server/words_index.json (generated)**: It generates 20 seeds per template. Per word it records tests (a skill label matches), uses (a stem matches within the word's topics), bank, difficulty (the mean of blueprint.abilities() tiers at 1/2/3, cut at 1.67/2.34, falling back to level) and bank_examples (3 × {template, seed, text, start, end}). Per confusion it records its live templates. It exits 1 on: a duplicate slug or (word, sense); a missing required field; a math word with no link and no bankless; a confusion link matching none of the 20 seeds; a cloze_template whose stem lost the word; fewer than 3 valid distractors for any quiz type a word can be asked in; a transition pair whose options cannot span 4 logics; or a match regex outside the restricted syntax. It prints proposed links and never writes them.
- **server/words.py (new)**

  It loads the content and the index once.
  - entry(slug).
  - library(learner, tz): every word with its state, for client-side filtering.
  - deck(learner, source, value, n, tz), where source is due|new|missed|saved|mistakes|lookedup|collection|topic|mine|list|words.
  - grade(learner, word, ok, mode, kind, ms, session, confusion, tz): the §12 rules, including no promotion on an early review, one box a day, and the exam cap.
  - quiz_item(word, kind, rng): the distractor rules in §7.
  - of_reason(template, reason) → words and a confusion.
  - mistake_words(learner): from open traps.
  - record(learner, slug): from attempts on the linked templates plus word_reviews.
  - minutes_today(learner, tz): the plan's Words task estimate.
  - gloss_index().
  Runs are stored in sessions (kind='words', cfg JSON {mode, direction, formats, timer, deck, order, i, requeue, skipped}, questions = the served items with their keys, answers).

- **server/phrases.py (new)**: About 15 phrase families: less than; more than; subtracted from; decreased/increased by n%; percent of; x is what percent of y; twice as many A as B; the ratio of a to b; per plus a fixed fee; at least / at most / no more than / exceeds (inequalities); the product of x and the sum; the square of the sum vs the sum of squares; consecutive integers. Each family(seed) returns {stem, choices[4], answer_index, reasons[4], word slug}, with parametric numbers and variable names. The __main__ self-check makes 200 per family and asserts no distractor is equivalent to the key: expressions by evaluating at 5 random x, inequalities by direction and boundary.
- **db.py schema**

  word_state(learner, word, box INT NOT NULL DEFAULT 0, due TEXT, reps INT, lapses INT, right INT, wrong INT, saved INT DEFAULT 0, first TEXT, last TEXT, lastday TEXT, lastwrong TEXT, PRIMARY KEY(learner, word)).
  word_reviews(id PK, learner, word, session, mode TEXT (cards|quiz|lookup), kind TEXT, correct INT NULL, given TEXT, confusion TEXT, box_before INT, due_before TEXT, ms INT, at TEXT). box_before and due_before let a regrade undo exactly.
  my_words(id TEXT PK 'u:'+random, learner, word, meaning, pos, example, same TEXT json, opposite TEXT json, notes, list, source, created, updated).
  reports(id PK, learner, kind, ref, category, title, details, context TEXT json, files INT, at).
  Indexes on word_state(learner, due), word_reviews(learner, at) and my_words(learner).
  LATER_COLUMNS adds learners.words_goal INT (NULL = 10, 0 = off), learners.words_from TEXT (JSON list, NULL = ['math']) and learners.gloss INT (NULL = on).

- **GET /api/words**: Needs X-Learner and X-Tz. Returns {today, groups:[{id,name,collections:[{id,name,count,known,due}]}], words:[{slug, word, sense, pos, collection, topics, difficulty, short, bank, own, list, second_sense, state:{box,due,saved,right,wrong,last}|null, is_due, from_mistakes, missed, looked_up}], counts:{total, due, new, learning, known, saved, mine, mistakes, missed, lookedup, new_today, goal}, forecast:[{day,n}]}. forecast is 14 days by default; ?days=N (at most 120) serves the plan calendar. The response is about 1,100 rows, so app gains Starlette's GZipMiddleware (minimum_size 1024).
- **GET /api/words/{slug}**: Returns the full entry: meaning, examples, symbols, figure, same, opposite and related (resolved to {slug,word} or text), confusions [{id, kind, other, tell, templates:n, fell:n, last}] (fell = the learner's attempts whose reason matches the link regex), bank_examples (text and offsets only, never the key), and record {questions:{answered,right}, reviews:{n,right,by_kind}, lookups, box, due, first, last}. It is 404 for an unknown slug, and for a 'u:' id that belongs to someone else.
- **POST /api/words/{slug}/example**: Body {index?: 0–2, fresh?: bool}. With index, it makes a 1-question drill of that bank_example's exact (template, seed) through drill.create(items=…). With fresh, it makes one from cfg.only = the word's templates, preferring a template other than the last. source='word-example', count 1. It first deletes this learner's unanswered 'word-example' session for the same slug. It returns {session, question (public), excerpt:{text,start,end}}. Answer it posts to /api/drill/{session}/answer, so the key only ever leaves through the normal drill feedback, and no (template, seed) is accepted from the client. The session is finished after its one answer.
- **POST /api/words/{slug}/save and POST /api/words/lookup**

  save: body {on}. It upserts word_state.saved and returns {saved}. It works for library slugs and own 'u:' ids. In a quiz, saving goes through POST /api/words/run/{id}/save {item_id}, which returns 409 until that item is answered.
  lookup: body {slug, where: session|qotd|challenge|report, ref}. It inserts one word_reviews row (mode 'lookup', correct NULL) per learner, slug and ref, and returns {ok}.

- **GET /api/words/today and GET /api/words/index**

  today: {day, math:{slug,word,short,collection,excerpt}, sat:{slug,word,short,pos,example}}, from daily.word(day, 'math') and daily.word(day, 'sat'), each a hash of 'word:{group}:'+the local date over that group. It adds each word's state when X-Learner is sent.
  index: public, no learner needed. It returns {v, terms:[{slug,word,match,short}]} for gloss:true words, with an ETag (and 304 on If-None-Match) and Cache-Control max-age=3600.

- **POST /api/words/run (+ GET /{id}, POST /{id}/next, /{id}/answer, /{id}/save, /{id}/finish)**

  create: {deck:{source, value?, words?≤200, start?:slug}, mode: cards|quiz, direction: word|meaning|mixed, order: due|shuffle|az, formats:[meaning2word, word2meaning, cloze, incontext, transition, bankcloze, phrase], count: 1–200 or null, timer: 0|15|30|60}. start begins a cards run at that word (Flashcards from here). It is 409 'nothing to study' for an empty deck, and 400 for a quiz of fewer than 4 own words or a format the deck cannot supply.
  A public quiz item never carries answer_index, reasons, tell, key or seed. meaning2word, cloze, incontext, transition and bankcloze items also omit the target slug.
  answer: {item_id, answer: 0–3 | 'know' | 'dontknow' | 'skip' | null (timeout), ms, regrade?:bool}. It claims each answer once (db.set_answer only_new). skip grades nothing and moves the card to the end once. regrade is allowed for any graded card whose review is still that word's latest; it restores box_before and due_before, then applies the new grade. The reply is {correct, answer_index, mistake, tell, word:{slug,word,short}, box:{before,after}, due, early, requeued, total}.
  finish: {asked, right, ms, groups:[{id,name,known_before,known_after,right,asked}], moved_known, learning:[{slug,due}], skipped:[slug], schedule:{tomorrow,in3,in7,later}, by_kind, mixups:[{confusion,kind,n}], next:{source,count,mode}}.
  A run owned by someone else is 403, and a finished run is 409.

- **Own words endpoints**

  POST /api/words/mine: 400 on a missing word or meaning or an over-long field; 409 {existing_id} on a case-insensitive own duplicate; 200 with a {library_slug} hint on a library match.
  PUT /api/words/mine/{id}.
  DELETE /api/words/mine/{id}, which also removes its word_state and word_reviews.
  POST /api/words/lists {name} and PUT/DELETE /api/words/lists/{name}; a delete moves the words to 'My words'.
  POST /api/words/mine/import {text ≤ 50 KB, ≤ 500 lines, list}: it accepts tab, ' - ', ':', ' — ' and a CSV with a word,meaning header, and returns {added, skipped:[{line, why}]}.
  GET /api/words/mine.csv.
  POST /api/words/reset {words:[…]} deletes word_state for those words.

- **drill.py and POST /api/drill: word and mix-up sets**

  The Drill body gains word: str|None and confusion: str|None (max_length 80). The endpoint resolves them to templates from the index (409 when there are none, or when the confusion is bankless), sets topics = those templates' topics, and sets cfg['only'] = the templates. For a confusion it also sets cfg['want'] = {template: regex}.
  In _pick, the pool and its difficulty fallback are both filtered by cfg['only'], so the fallback cannot escape the word's templates.
  In _fresh, a template with a want regex walks up to 12 seeds for an item where some reason matches, and otherwise takes the first. The repair after a miss goes through the same _fresh, so it keeps the mix-up.
  _feedback gains words:[{slug,word}] and confusion:{id,kind,words,tell} from words.of_reason(q['key'], reason).

- **progress.carry, progress.days and GET /api/me**

  carry moves word_reviews and my_words, and merges word_state per word: the higher box, summed reps/right/wrong/lapses, saved = max, due = the earlier, first = the earlier, last = the later. Its returned count adds word_reviews and my_words.
  days() also reads word_reviews (lookups excluded): a local day with 10 or more reviews counts toward the streak, minutes add min(ms, 60000) per review, recent[] gains 'words', and total counts reviews and own words. That way Me's 'Nothing is saved under that code' check and the streak flame both see a words-only learner.
  GET /api/me gains words:{known, studied, saved, reviews_week, due}.

- **PUT /api/me and per_session()**

  PUT /api/me accepts words_goal ∈ {0,5,10,20}, words_from ⊆ {math, sat, transitions} (non-empty) and gloss ∈ {true,false}, and returns them in profile. Plan step 4 and Me both write the same fields.
  per_session(p) subtracts words.minutes_today(learner, tz) when words_goal > 0 before converting minutes to questions (95 s each), with a floor of 5. /api/today returns words:{due, new_today, goal, minutes, done} for the Today tile and the Plan's Words task.

- **GET /api/history**: By default it excludes kind 'words' and drills whose cfg.source is 'word-example'. ?kind=words lists words runs only (right/asked from their result). Results' Words filter uses it, and its rows link to /words/run/?id=. /results/report/ redirects a words id to /words/run/?id=.
- **POST /api/report (shared)**: multipart/form-data (python-multipart is installed). Fields: kind (word|question|test|other), ref, category (general|bug|wrong_key|wrong_definition|typo|confusing|feature|other), title ≤200, details ≤5000, context (JSON: page, run or session id, item id, word slug; the server fills template and seed from the session, never from the client). files[]: up to 10 images, each ≤10 MB, JPEG/PNG/WebP/GIF checked by magic bytes, saved to server/reports/{id}/{n}.{ext}. Returns {id}. It is 422 on over-long fields, 400 on a bad file or an 11th file, and 429 past 20 reports per learner per day.
- **daily.py**: word(day, group): a sha256 of 'word:{group}:{day}' over that group's library words (math: bank-linked words; sat: core then advanced, weighted to core), the same for everyone.
- **server/test_flow.py**

  Checks:
  - the word-run payload never contains LEAKS, tell or the target slug for hidden-target types;
  - the SRS transitions, the exam cap, one box a day, and no promotion on an early review;
  - requeue, skip and regrade restoring box_before;
  - a word drill serves only linked templates, and the difficulty fallback stays within them;
  - a confusion drill's items carry a matching reason;
  - drill feedback lists radius and diameter after 'used the diameter as the radius';
  - quiz distractors never in the target's same list, with part of speech matched;
  - own-word validation, duplicates and import partial success;
  - carry moves all three word tables and counts them;
  - days() counts a review-only day, and me.days.total includes reviews;
  - history excludes words runs by default;
  - report file limits and the rate limit.


### 3.8.6 Files this spec names, and who owns each

| file | owner |
|---|---|
| `server/words/math.json` | S9 |
| `server/words/sat.json` | S9 |
| `server/words/transitions.json` | S9 |
| `server/words/confusions.json` | S9 |
| `server/words/collections.json` | S9 |
| `server/words_index.json` | S9 |
| `tools/build_words.py` | S9 |
| `server/words.py` | S9 |
| `server/phrases.py` | S9 |
| `server/db.py` | F4 |
| `server/app.py` | F0 (routers register themselves, §2.10) |
| `server/drill.py` | F5 → S4 |
| `server/progress.py` | F4 |
| `server/daily.py` | S3 |
| `server/reports/` | F6 |
| `server/test_flow.py` | shared: new checks go in server/checks/<task>.py |
| `web/assets/ui.js` | F2 |
| `web/assets/ui.css` | F1 |
| `web/words/index.html` | S9 |
| `web/words/study/index.html` | S9 |
| `web/words/run/index.html` | S9 |
| `web/words/mine/index.html` | S9 |
| `web/practice/session/index.html` | S4 |
| `web/index.html` | S3 |
| `web/challenge/index.html` | S8 |
| `web/plan/index.html` | S7 |
| `web/me/index.html` | S1 |
| `web/mistakes/index.html` | S10 |
| `web/results/index.html` | S6 |
| `web/results/report/index.html` | S6 |
| `README.md` | shared: each task edits its own subsection |
| `spec/rebuild.md` | F0 (superseded by this file) |
| `.gitignore` | F0 |

A file owned by another task is met through §2.9: the owner builds it, or this section's task adds its hook on its own page.

### 3.8.7 Shared needs

- The runner shell (.run-top, .run-in, .tools/.tool, .prog/.seg, .count, .next-row/.keys, .sum/.score/.rows/.row/.upnext) moves from web/practice/session inline CSS into ui.css. The practice session, the words runner and the test window (which is to take the practice look) all use it.  
  ↳ R21: F3 runner.js
- UI.question(host, q, {head}): a head override (label and glyph) for items with no topic, such as word, transition and phrase items. Their choices render through the same .opts. → built in F3 question.js / runner.js
- UI.filters: dropdown filter chips with counts, multi or single select, a phone bottom-sheet variant (dialog.sheet.bottom), and URL sync. Practice (source and format filters), Results (sittings by kind) and Mistakes need it too. → built in F1 kit.js
- UI.pop: an anchored popover that closes on Esc and outside click and returns focus. It can anchor to a selection rect. Used by the gloss, selection-to-add, the practice session's Details popover and the navigator. → built in F1 kit.js
- UI.report plus POST /api/report: one report sheet with every TopTierPrep category plus ours, title 200, details 5000, up to 10 images, and a read-only 'Sent with your report' box. Used for words, practice questions, the report review and the test. → built in F6 report.js  
  ↳ R17: UI.report (F6 report.js)
- The Plan's task model (done / skip / undo / reason / launch buttons, the day's minutes budget) must carry a Words task type whose done state comes from /api/today words.done. per_session() must subtract its minutes.
- A stat tile (.stat: label, big value, helper, optional action) for Me, Results, Challenge stats and My words.
- A 14-bar day chart (.forecast) for the Today week, Results study time and the words forecast.
- Nav count is one decision across sections: NAV grows to 6 here. If any other section adds a top-level item, the phone bar gets a More tab rather than going to 7 columns.  
  ↳ R1: the phone keeps 5 tabs; the item goes in the sidebar and the menu sheet
- The shell bar gains a '+ word' button. Runner pages and the test window must opt out.
- progress.days() learns about non-question study (word reviews) in the streak, minutes and total. progress.carry() has to move and count every new per-learner table. Me's carry check depends on days.total.  
  ↳ R13: progress.days (F4)
- /api/history gains a kind filter and stops returning session kinds the report page cannot render. The Results and Tests sections must render from it.
- Me's achievements (Me section) take the word achievements: 50/250/1,000 known, a collection completed, a 7-day review streak.
- A friendly 404 page for unknown routes. /vocabulary/ currently shows FastAPI's raw {"detail":"Not Found"}; /vocabulary/ should redirect to /words/.

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

### 3.8.9 This section's open questions

Folded into Part 5 where they need a decision; kept here for context.

- R&W words in v1: this spec ships about 750 SAT words and about 70 transitions now, because every tool works without a bank and their section is R&W. The earlier direction was 'Math only for now'. If that still holds, drop sat.json and transitions.json. Nothing else depends on them except the two SAT quiz types and the SAT word of the day.
- Content review: who reads about 1,090 definitions, about 100 tells and the math confusion links before they go live? The build tool checks links, duplicates and distractors, not wording.
- Nav placement: Words as a 6th top-level item (proposed, matching their sidebar), or under Practice? This has to be settled together with any other section that wants a top-level item.
- Tap-to-define in the daily challenge: it is on in this spec, since everyone gets the same help and a definition does not give the answer away. Or should the ranked challenge be bare, like the test?
- Pronunciation uses the device's own voices, whose quality varies by device. Is that acceptable, or should a word with no voice show a written respelling instead?

---

## 3.9 Review: redo, marked, saved, history, fixed

> **Spec title:** Review hub: the redo list (open mistakes), marked for review, saved questions, attempt history and the fixed log. It replaces /mistakes/ and plugs into the practice session, the exam runner, the report, the practice builder, Today and Me  
> **Built by:** S10 (page and endpoints), F3 (pane, history), F4 (traps, attempts, flags and notes), F6 (shares)  
> **Read with resolutions:** R2, R5, R6, R8, R9, R10, R18, R19, R22, R23, R24 (§2.2). Where this spec disagrees with them, they win.

### 3.9.1 What they have

- **Redo List filter in the QBank builder**: A select in the Advanced Filter: Redo List = All / Redo Only. It combines with the domain and skill checkboxes, the Easy/Medium/Hard pills, the Question Score 1–7 slider, Solved, Marked for Review, Volume (10/20/30/40/50/All) and Timed/Untimed. The live walk found how a question gets onto it: the API has toggleRedo, but no screen calls it (there is no Redo button in the session UI), so the list stays empty and Profile reads 'Redo Questions 0'. No page lists the redo questions.
- **Marked for Review filter in the builder (this is their saved list)**: The live walk shows its options are All / Saved Only. Marking a question for review in the QBank is how it gets saved (the API calls it toggleSaved), so 'marked' and 'saved' are one list. It sits next to Redo List.
- **Solved filter in the builder**: Solved = All / Solved Only / Unsolved Only. Their bank is finite, so 'Unsolved' runs out, and 'Solved Only' is how a student re-practises questions already done. Unchecking a domain does not update the 'N questions' count (a bug).
- **Question Score 1–7**: A dual-thumb range slider in the builder that gives a finer difficulty. The Details popover never shows the score.
- **Mark for Review in a QBank session**: A bookmark button on the question strip that fills blue when on. Marked questions show in the Question Overview as yellow with a bookmark corner flag.
- **Mark for Review in the exam runner**: The strip button turns into 'Unmark' (yellow). The footer navigator shows a red 'For Review' flag in its legend and grid. Check Your Work has a FOR REVIEW stat card and yellow cells with a bookmark.
- **Flagged in the score report**: The Question Review filters are All / R&W / Math / Flagged (n). The legend reads Correct / Incorrect / Unanswered / Flagged for review (n). Flagged cells get an orange corner dot in the per-module grids, and the review modal header shows a 'Flagged for review' chip.
- **Attempt History modal**: An 'Attempts' button on the QBank question strip, with a blue count badge, opens a modal with one row per try, for example '#1 ⊗ Incorrect · Option A · 00:22 · Sep 23, 11:35 AM', and a [Close] button. The empty state is 'No attempts yet.' It covers one question in one session.
- **Unlimited retries until right**: The key is never shown after a wrong answer: you retry, or open the explanation. Because of this, per-question accuracy means little.
- **Mixed status and the Question Overview**: A question answered wrong and then right counts as 'Mixed', drawn as a square split diagonally green and red. Status legend: Unanswered (outline) / Correct / Incorrect / Mixed / Marked (yellow) / Current (blue, which overrides the other states). Difficulty mode tints each cell Easy green / Medium blue / Hard red.
- **Per-question stopwatch**: It counts up on the question strip, and the Attempt History rows use it for time spent. A reload resets it to 00:00, and an earlier wrong pick comes back as a plain blue 'selected' instead of red.
- **Details popover**: QUESTION ID (for example 06469-DC), DOMAIN, SKILL and DIFFICULTY. It needs an outside click to close.
- **Saved Content card in Profile**: Counts only: Saved Words / Redo Questions / Saved Questions. Nothing seen lists the saved questions or offers a way to practise them.
- **Review modal in the report**: 'R&W - M1 · Q1' with a Correct/Unanswered chip and a 'Flagged for review' chip. Buttons: [Hide answers] / [Report] / '1 of 49' / Close. The body has the passage, stem, choices, a YOUR ANSWER box ('Unanswered' when blank), a CORRECT ANSWER box, and an explanation that is 'Justification:' followed by 'Distractor Analysis:' with one line per wrong option. ← and → move between questions. 'Hide answers' shows an 'Answers hidden' chip, removes the key and the explanation, turns the button into [Show answers], and stays on across Next, but you still cannot re-answer. The per-question payload has no domain, skill, difficulty or time spent.
- **Results list wrong-number chips**: Each sitting card lists wrong and unanswered question numbers together per module as red chips ('2 3 4 5 6 7 +19') above a full-width Review button. The chips cannot be clicked. The report's gauge counts unanswered as wrong, but its Performance Summary does not.
- **Shared session**: From the bundle: Share creates /question-bank/shared/:shareId with a 'Start Practice' landing. The toasts are 'Share link copied to clipboard' and 'Share created (id: …)'. On screen, Share called navigator.share and froze the page.
- **Clear Session**: A red button in the session top bar with the confirm text 'This removes answers, annotations, and attempts from this session only. Your question-bank progress from other sessions is kept.' It lets a student redo a session clean, but it deletes the history.
- **Eliminations and annotations saved to the server**: From the bundle: crossed-out choices and passage notes are kept per session.
- **Vocab My Words (their pattern for a saved + due list)**: Two nav cards, 'Saved Words N' and 'Due Today N' (spaced repetition), the same filters as the library, and a dashed empty state: 'No saved words match these filters / Try broader filters or save more words from the library.' A save star appears on a flashcard after it flips.
- **Weaknesses around this section**: There is no review-mistakes flow, no session summary and no list of sessions: a session survives only by its URL. The redo list has no way in. The key is hidden after a miss, the overview popover ignores Esc, Share freezes the page, and 'Share / Export Report' on Results has no handler.

### 3.9.2 What we have now

Status is have / partial / missing / worse, against theirs.

- **Redo list (open mistakes)**: *partial.* /mistakes/ lists every open trap by the misconception's name, grouped by topic, with a ×hits count and two pips for the clean answers still owed, plus 'Fix' per topic and 'Fix all · N'. A row cannot be clicked: you cannot see the question you missed, what you picked, the key, when it happened, its difficulty or where it came from. There is no selection, filter, sort or search. Still, it is already more than TopTierPrep's redo list, which nothing fills.
- **Trap identity**: *worse.* Traps are keyed by (template, raw reason text). Measured over 24–40 seeds per template, about 70 of the 349 MC templates put seed-specific numbers in their reasons ('applied the 10% change…' vs 'applied the 50% change…'), so one misconception opens a separate trap for each seed. That fragments the list and inflates the count (the seeded learner had 25 rows over 11 templates).
- **Grid-in and filler misses in the list**: *worse.* A grid-in miss is filed under the skill name ('Trigonometric ratios', 'Counting'). The bank's filler distractor 'near-miss arithmetic slip' (satbank/item.py _fillers, used in 27 templates) is filed as if it were a named misconception. Both are styled exactly like real misconceptions, so the list mixes three kinds of row with nothing to tell them apart.
- **Fix all count**: *worse.* The header reads '25 open mistakes' next to 'Fix all · 22'. 22 is templates × 2, and the drill really asks each template twice (queue = once + once) even when a trap is half fixed and needs only one more answer. Nothing explains the mismatch.
- **Marked for review in practice**: *missing.* The practice session has no flag.
- **Marked for review in tests**: *worse.* test.js keeps marks in a client-side Set. A reload loses them, the move to module 2 clears them (S.marked = new Set() in the gate handler), and they never reach the server, the report or any list.
- **Flagged filter in the report**: *missing.* /results/report/ has no flagged state or filter.
- **Saved questions**: *partial.* The session's bookmark saves (template, seed), which is exact and regenerable, better than a finite ID. But the hub shows only '14 saved · Again'. You cannot see the saved questions, unsave outside the session, add a note, filter, pick a subset, practise fresh versions, or save from a finished test's report (POST /api/saved returns 404 for any session that is not a drill or challenge).
- **Exact re-serve counts as evidence**: *worse.* When a saved question is served again exactly, a right answer counts toward mastery and closes traps, even though the student has already seen its key. The same happens on a retake of a fixed diagnostic form or shelf mock, whose (template, seed) pairs repeat.
- **Attempt history**: *missing.* The attempts table has every answer (template, seed, given, correct, reason, ms, session, at), but no endpoint or UI exposes it, per question, per kind of question or overall. Test answers are filed at finish with ms = NULL, so tests have no time per question.
- **Mixed status**: *missing.* Repair questions exist (drill.py serves the same template on a fresh seed after a miss, and the served question carries repair: true), but the status has no name, no visual and no column in attempts.
- **Solved / unsolved**: *partial.* 'Unsolved only' is implicit and better: practice never repeats a question (practice_seen), so every set is fresh and never runs out. There is no equivalent of 'Solved only' (practise what you have already done), except the saved set.
- **Builder source filters (redo / marked / saved)**: *missing.* The Practice builder cannot draw from the redo list, the marked questions or the saved ones. Redo starts only from /mistakes/, and it ignores difficulty and the clock.
- **Fixed mistakes**: *missing.* Closed traps stay in the table but are never shown. When a trap reopens, closed is set back to NULL, so the fact that it was once fixed is lost.
- **Question details and address**: *missing.* There is no way to see a question's skill, difficulty or (template, seed) address, or to copy a link to it.
- **List of sittings to go back to**: *partial.* GET /api/history lists finished sessions, and Results shows them. A practice set cannot be retaken exactly or with fresh numbers from there; only a test's misses can be fixed (from_session).
- **Share**: *missing.* There is no way to share a question or a set.
- **Saved-content counts on Me**: *missing.* /me/ shows only the name and the device code.
- **Empty state**: *worse.* A new student sees '0 open mistakes' and a bare 'Practice' link. Nothing says what this page will hold or how things get here.
- **Reachability**: *partial.* The page is reached only from an 'N mistakes' link on Practice and Today. It is not in the navigation (NAV in ui.js is Today / Practice / Tests / Plan / Results, and SECTION maps mistakes to practice).

### 3.9.3 Design

##### Review changes

What this review changed in the proposed spec, and why:

1. **TopTierPrep's inventory, corrected from the live walk.**
   - Their 'Marked for Review' builder select is *All / Saved Only*: in the QBank, marking a question is saving it.
   - Their redo list is filled only by a toggleRedo API call that no screen makes, so Profile reads 'Redo Questions 0'.
   - Added what the proposal did not list: the exact Attempt History row and empty-state copy; Hide answers staying on across Next; ←/→ keys; the report payload having no skill, difficulty or time; unanswered counted as wrong on one card only; the shared-session link with its landing page; the Clear Session copy; a reload losing the stopwatch and the wrong pick; the Overview's Mixed/Marked/Current and difficulty views; the Solved filter; eliminations kept on the server; the 1–7 score.
2. **The trap key: facts corrected and a flaw fixed.** I measured the bank (386 templates, 24–40 seeds each; one generate call with its audit takes 0.26 ms).
   - About 70 of the 349 MC templates put seed-specific numbers in a reason. The proposal said 109 of 348.
   - The filler 'near-miss arithmetic slip' appears in 27 templates. The proposal said 13.
   - The digit regex also folds two different options of **one** item into one mistake in 29 templates. For example, circles.degree_radian's 'divided by 360 instead of 180' and 'divided by 90 instead of 180' become one, and so do pct.series' 'the 2013 value as a percent of the 2014 value' and its reverse.
   - I kept the normalised key, because most of these folds are the same error: circles.coterminal's two 'quarter turn away' options are one misconception. But the label is now always the concrete text of the latest miss, every attempt stores its concrete reason and its norm, and a bank-side `Mis.tag` is listed as the exact fix (open question).
3. **Trap ids.** `template|norm` contains `#` and spaces, which breaks `?open=`. Traps get an INTEGER id.
4. **Repeat detection moved into `progress.record`.** It is one EXISTS query on attempts, so every caller gets it: drill, paper, QOTD and challenge. The proposal covered drills only. One consequence is now stated: a retake of a fixed diagnostic form or shelf mock files repeats.
5. **Marks: one `flags` table keyed (learner, session, qid).** The proposal had a JSON column plus a table keyed (learner, template, seed).
   - The 10 diagnostic forms and the shelf mocks are fixed papers, so the same (template, seed) comes back in another sitting, and a per-item key would move a report's flags between sittings.
   - The API says `flags` because `drill.state()` already uses `marks` for right/wrong.
6. **The access rule, made precise.** It now separates *reveal* (key, rationale, per-option reasons), *kept* (question only) and 404.
   - The flag endpoint checks ownership, which matters because `GET /api/session/{sid}` has no learner check.
   - Live-test items and unanswered challenge items can never reach a drill, a share or a worksheet.
7. **One strip, with integrity.** The exam runner uses the practice strip's slots, but Save and History are disabled during a live test ('After the test'). They are also disabled on an unanswered challenge question, because a family history is a study aid in the middle of a test. In practice, the History modal before answering shows results with no Open button: reading a solved sibling's rationale first would make the answer unclean.
8. **Minimalism cut back out.**
   - History gets selection and an action bar (Fresh versions / Again, exactly / Share). This is our 'Solved only'.
   - History gets a Group by **Day | Sitting** control. Sitting gives the list of sessions TopTierPrep lacks and a clean retake in place of Clear Session.
   - The pane shows skill, difficulty, format, source and date inline; Details keeps only the address.
   - The phone Options disclosure echoes its values in the summary line.
   - Marked rows show pick → key and time.
   - Result cells carry glyphs, and the legend is always visible.
   - Flag calibration is added.
9. **Tests get time per question.** The runner sends dwell ms with each answer save, so History's median, Slowest sort and the report's time tile cover tests. TopTierPrep's report has no time at all. This change is shared with Tests and Report.
10. **Blanks.** The proposal's 'Blank' result in History could not exist, because `record_paper` files no blanks. History holds answers; blanks live in the report, with Save and Mark.
11. **The drill body, consolidated.** Six new fields became `list`, `ids`, `exact`, `each` and `level`. `mistakes:true` and `saved:true` stay as aliases.
12. **The nav badge count** rides on `/api/me`, which the shell already fetches, instead of adding one request per page.
13. **Server-side search** needs stored text. attempts gains `stem`, written when an answer is filed and backfilled once.
14. **Share is made concrete.** It was an open question, and TopTierPrep has it (broken). There is a shares table and a `/s/` landing page. Only items revealed to the sharer can be shared, the link is copied to the clipboard, and navigator.share is never used.
15. **Extras added:**
    - the same mistake in other question types: 79 normalised misconceptions recur across 2 or more templates, 12 of them across topics (measured),
    - flag calibration,
    - a printable fresh worksheet,
    - Hide answers that persists,
    - shortcuts ignored while typing,
    - relapse rules (dismissed then missed = reopened, not relapsed; Fixed excludes dismissed),
    - spot and pane drills kept out of the sittings lists.

---

#### Review hub (`/review/`)

TopTierPrep spreads this across builder selects, a profile counter and a modal for one question at a time. Here it is one page with five tabs over a list: **Redo, Marked, Saved, History, Fixed**. A question pane sits beside the list.

- Every item opens the exact question again, rebuilt from its (template, seed) in the practice session's renderer.
- Every list, or any selection from it, becomes a practice set in one tap. The set is either **exactly** these questions or **fresh versions** on new numbers. Fresh versions are what a finite bank cannot offer.

##### 0. Vocabulary (one set of words on every page)

**Mistake kinds** (a chip on each redo row):

| kind | what it is | label | chip |
|---|---|---|---|
| Misconception | A wrong MC option. | The concrete text of the latest miss. | none (the default kind) |
| Grid-in | A wrong typed answer. | The skill. | `Grid-in` |
| Slip | The picked option is the bank's filler 'near-miss arithmetic slip'. | 'Arithmetic slip'. | `Slip` |
| Unsure | Answered right while flagged, or added by hand. | The skill. | `Unsure` |

An Unsure needs 1 clean answer.

**Mistake statuses:**
- **Open**: 2 clean answers owed. Pips ○○.
- **Half fixed**: 1 owed. Pips ●○ in orange.
- **Relapsed ×n**: fixed before, then missed again (by a new miss or a failed check-in). The chip is ink-filled.
- **Fixed**: closed by clean answers.
- **Dismissed**: closed by the student. A later miss reopens it as Open, not Relapsed.

**A clean answer** is a right answer that meets all three conditions:
1. it is on a (template, seed) this learner has **never answered before**,
2. it was **not flagged** when answered,
3. it is on the trap's template.

Only clean answers close mistakes or count toward check-ins. Exact repeats are filed with `repeat = 1` and shown in History. They are left out of mastery whether right or wrong. A **wrong** repeat still reopens or refreshes its mistake, because it is still evidence of the error.

**Answer results.** Each cell always has a glyph as well as its fill, and a legend is always shown where cells appear.

| result | cell | meaning |
|---|---|---|
| Right | amber fill, ✓ | |
| Wrong | ink fill, ✕ (white) | |
| Repaired | amber fill with an ink ↻ corner | right on the repair question that followed a miss. This is our 'Mixed', and the proof is on new numbers rather than a retry. |
| Repeat | outlined, `=` | an exact re-attempt |
| Blank | grey tile, – | the report grid and Check Your Work only. Blanks are not filed as answers. |
| Flagged | orange corner flag, overlaid on any result | |
| Current | 2px ink ring, overlaid | |

**Difficulty** is a 3-step bar glyph (▁▃▅, ink on grey) plus the word Easy / Medium / Hard. It is never shown by colour alone.

##### 1. Where it lives

**Navigation.**
- Top bar: `Today · Practice · Review · Tests · Plan · Results`.
- Review carries a badge: an orange dot and the number of open mistakes, hidden at 0. It reads `/api/me`'s new `review.open`, so there is no extra request.
- Phone: a 6th tab with a counter-clockwise-arrow-in-a-square icon, 65px wide at 390px. The longest label, 'Practice', fits at 10.5px.
- `SECTION` maps `mistakes → review`.

**Routes.** `/mistakes/` becomes a redirect to `/review/?tab=redo` that keeps the query.

**URL state:**

```
/review/?tab=redo|marked|saved|history|fixed
  &topics=a,b&difficulty=hard&fmt=mcq&kind=…&status=…&source=…&result=…
  &since=…&until=…&q=…&sort=…&group=…
  &open=trap:123 | q:<template>:<seed>
```

- A filter change uses `replaceState`. A tab change uses `pushState`, so Back returns to the previous tab.
- `open=` restores the pane. Template names are `[a-z0-9_.]`, so the value needs no escaping.

**Links in:**
- Today's Review card (§10).
- The Practice map's 'N mistakes' link, which goes to `?tab=redo&topics=<picked>`.
- The tooltip on a map tile, which gets a 'Review' link.
- The session summary's opened and fixed lines, each going to `open=trap:<id>`.
- The report's Mistakes block ('See all in Review').
- The Saved content card on Me.
- The share landing page (§15).

##### 2. Desktop layout (1280)

**Top bar.** The shell, with Review current.

**Header row** (`max-width: var(--max)`):
- Left: the H1 **Review** (Archivo 800, 36px), with a helper line under it (Archivo 500 14px, soft): *"Every wrong answer lands here, named by the mistake behind it. Two clean answers on fresh questions close it."*
- Right: the primary pill **Redo all · 22 questions**, with a meta line under it: `11 question types · about 35 min`.
  - The number is the sum, over the open templates, of the largest `owed` among that template's open traps. A half-fixed template adds 1.
  - The minutes come from `blueprint` pace.
  - The button is hidden only when nothing is open.

**Stat strip.** Five tiles in one row. Each is `--tile`, 10px radius, with a DM Mono 11px uppercase label, an Archivo 800 32px number and a sub line.

| label | number | sub line |
|---|---|---|
| OPEN MISTAKES | 25 | `7 half fixed · 1 relapsed · 2 unsure` |
| MARKED | 3 | `from 2 sittings · 67% of flags right` |
| SAVED | 14 | `4 with notes · 3 not answered` |
| FIXED | 40 | `6 this week · median 2 days` |
| CHECK-INS DUE | 2 | `fixed 7+ days ago` |

Each tile is a button that opens its tab with the matching filter. For example, CHECK-INS DUE opens Fixed with `status=due`.

**Tab bar.** Segmented tabs, each with its count: `Redo 25 · Marked 3 · Saved 14 · History 312 · Fixed 40`.
- The current tab has an ink label and a 2px amber underline, the shell nav's style.
- It is `role=tablist`, and the arrow keys move between tabs.
- While a filter is set, each count reads `9 of 25`.

**Filter bar** (`UI.filterBar`, shared). A row of dropdown chips. A chip with a value shows it, for example `Topic · 3`.

| chip | options | tabs |
|---|---|---|
| Topic | The 19 topics under 4 domain headers. Domain rows are tri-state checkboxes; each topic shows its count in this tab. 'Select all' and 'Clear'. | all |
| Difficulty | Easy / Medium / Hard, as multi-toggle pills. | all |
| Format | Multiple choice / Grid-in. | all |
| Kind | Misconception / Grid-in / Slip / Unsure. | Redo |
| Status | Redo: Open / Half fixed / Relapsed. Fixed: Check due / Checked / Fixed / Dismissed. | Redo, Fixed |
| Source | Practice / Section / Module / Diagnostic / Challenge / Question of the day / Review / Shared set. | History, Marked, Saved |
| Result | Right / Wrong / Repaired / Repeat. | History |
| Flagged | Flagged when answered / Not flagged. | History |
| Date | Today / 7 days / 30 days / All / Custom, where Custom is two native `<input type=date>` fields. | all |
| Sort | See the per-tab list below; the chip shows the current value. | all |

Sort options per tab:
- Redo: Most recent / Most missed / Closest to fixed / Oldest / Topic order.
- Marked: Newest / Sitting / Wrong first.
- Saved: Newest / Oldest / Topic / Not answered first.
- History: Newest / Oldest / Slowest.
- Fixed: Recently fixed / Longest to fix / Most relapses / Check due first.

After the chips come:
- **Search**, with the placeholder 'Search mistakes and questions'. It matches the label, skill, topic, the misconception and the stem text, runs on the server and is debounced 250ms.
- **Clear filters**, a text button shown only while a filter is set.

Menus close on Esc and on an outside click, and return focus to their chip.

**Body.** A two-column grid, `minmax(0,1fr) 460px`, gap 24px.
- Left: the tab's list.
- Right: the **Question pane** (§8), `position: sticky; top: 76px; max-height: calc(100vh - 96px); overflow: auto`.
  - With nothing open, it shows the first row.
  - For an empty tab, it shows what the tab is for.

**Action bar** (`UI.actionBar`, shared). Sticky at the bottom of the viewport, white, with a top hairline. It appears on **every** tab. Left: a live summary. Middle: the tab's options. Right: its primary action.

##### 3. Tab: Redo

**Most-missed strip** (shown when 5 or more are open): up to 5 chips, each the label cut to 40 characters plus `×hits`, then **Redo these 5 · n questions**.

**Grouping.** A 'Group by' select: Topic (default) / Domain / Mistake type / None. 'Mistake type' groups rows that share a norm across templates (§14). Each group header has:
- a tri-state checkbox,
- the topic glyph, the name and the domain (DM Mono 11px),
- `n open`,
- the text button `Redo · n questions`,
- a collapse chevron.

A group with more than 8 rows shows 8, then a `Show 7 more` button.

**Row** (`.redo-row`, 64px minimum, `--tile`, 10px radius; the open row gets an inset 1.5px amber border):
1. A checkbox with a 44px hit area.
2. The pips (●○), with `title` and `aria-label` '1 of 2 clean answers'.
3. Two lines:
   - Line 1: the label (Archivo 600 15px, 2 lines at most).
   - Line 2: DM Mono 12px soft, separated by dots: `skill · ▃ Medium · MC · missed 3× · last Sep 21 · Practice · picked C`.
4. The kind chip or status chip, if any.
5. `+2 elsewhere` when the same mistake is open on other templates.
6. A chevron.

Clicking the row opens the pane. The checkbox toggles selection and does not open the pane.

**Selection.**
- Every row is selected by default.
- The list head has a tri-state select-all with `25 of 25 selected`.
- The selection is kept per tab in sessionStorage, wrapped in try/catch.

**Action bar, Redo:**
- Summary: `12 selected · 6 question types · 10 questions · about 16 min`.
- Options:
  - **Level**: segmented `As missed | Any | Harder`, default As missed. As missed draws the fresh seed at the tier of the last miss. Harder goes one tier up where `_tiers_of(template)` has one, and otherwise falls back to As missed; the summary then says `3 can't go harder`.
  - **Timed**: the same clock toggle and minutes blank as the Practice builder.
- Primary: **Redo selected**, disabled at 0 selected with the reason 'Select a mistake'.
- Secondary: **Print worksheet** (§16) and **Share** (§15).

**Undo toast.** Dismissing from the pane removes the row and shows `Removed from Redo · Undo` for 6s.

##### 4. Tab: Marked

**Calibration line** at the top: `You flagged 12 questions · 7 were right (58%)`, with the tip *'Most flags right: trust your first answer more. Most wrong: flag and come back.'* It only counts flags set during a sitting, meaning the flag time is earlier than the finish.

**Groups.** Rows are grouped by sitting. Each header gives the kind, date and count, for example `Section · Sep 21 · 3 marked`, with a link to that sitting's report.

**Row:**
- a checkbox,
- an orange flag glyph,
- `Q17` (or `M2 Q5`),
- the stem's first line (Source Serif 4 15px, 1 line),
- the meta: `skill · ▅ Hard · MC · 1:40`,
- a result cell and `C → A`, or `Blank → A`, or 'Not answered yet',
- `flagged later` when the mark was added from the report or Review.

**Action bar, Marked:**
- Summary: `3 selected`.
- **Fresh versions** (primary), with a select `1 / 2 / 3 each`.
- **Again, exactly**. Items already answered file as repeats, and the summary says so: `2 will be repeats`.
- **Share**.
- **Unmark** (quiet), with an undo toast.

**Hidden until finished.** Flags on a live test, or on an unanswered challenge question, do not show until that sitting is finished or the question is answered (§ server access rule).

##### 5. Tab: Saved

**Row** (a taller card, 88px minimum):
- a checkbox and the bookmark glyph (orange fill),
- the stem clamped to 2 lines (Source Serif 4 15px),
- the meta: `topic chip · skill · difficulty · MC · saved Sep 20 · answered: Wrong (picked C) · 2 tries`,
- the note in italic Archivo 13px soft,
- row actions:
  - **Note**: an inline textarea, 280 characters at most, with a live counter. It saves on blur and on Cmd/Ctrl+Enter.
  - **Unsave**: removes the row with an undo toast; undo restores the note too.

**Action bar, Saved:**
- Summary: `5 selected · 5 questions`.
- **Again, exactly** (primary).
- **Fresh versions**, with `1 / 2 / 3 each`.
- **Share**.
- **Print worksheet**.
- **Unsave** (quiet).

**Pagination.** 50 at a time: `Load 50 more · 50 of 140`.

##### 6. Tab: History

This is every answer the student has filed, from any mode. Blanks are not answers, and the empty state of the Result filter says so, linking to the reports.

**Summary card**, for the current filters:
- Answers 312.
- Accuracy 71%.
- Median time 1:08. Tests count once dwell time exists; older test rows show `—` and the card says `time known for 280 of 312`.
- Accuracy by difficulty as three short bars, each with `r/n`.
- Repaired 18.
- Repeats 6.
- **Download CSV**.

**Group by: Day | Sitting.**
- **Day header**: `Tue, Sep 23 · 24 answered · 17 right · 38 min`, in local time via X-Tz.
- **Sitting header**: `Practice · Linear functions, Percentages · Sep 23 14:02 · 9/12 · 14 min`, with these buttons:
  - **Again, exactly**: a clean retake of that sitting that deletes nothing (it replaces TopTierPrep's Clear Session),
  - **Fresh versions**,
  - **Fix the misses** (the existing `from_session`),
  - **Report / summary** (a link).

**Compact row** (48px):
- a checkbox,
- the time (`14:02`, DM Mono),
- a result cell,
- the topic glyph and skill,
- the difficulty glyph,
- a source chip (Practice / Section M1 / Challenge / QOTD / Diagnostic / Review / Shared),
- `C → A` (a grid-in reads `12 → 9`),
- the time spent (`1:12` or `—`),
- a flag glyph if flagged,
- on wrong rows, the misconception: inline on desktop, on a second line on a phone.

Clicking a row opens that exact question in the pane.

**Action bar, History** (TopTierPrep's 'Solved only', done better):
- Summary: `24 selected · 19 question types`. Selection defaults to none on this tab; 'Select all 312 matching' selects by filter, capped at 120 with a note.
- **Fresh versions** (primary), with `1 / 2 / 3 each`.
- **Again, exactly**.
- **Share**.

**Pagination.** By attempt-id cursor: `Load 50 more · 50 of 312`.

##### 7. Tab: Fixed

**Stat line:** `40 fixed · 6 this week · median 2 days to fix · 3 relapsed · 2 dismissed`. Dismissed ones are not counted as fixed.

**Row:**
- a checkbox,
- the label and the topic chip,
- `fixed Sep 20 · took 3 days · missed 2× · relapsed 1×`,
- the check-in state: `Check due Sep 27` (amber outline), `Checked ✓ Oct 4 · next Oct 25`, `Checked twice ✓`, or `Dismissed`,
- **Reopen** on dismissed rows.

**Action bar, Fixed:** **Check these now** (primary). It builds a set with one fresh seed per selected template.
- A miss reopens the mistake as Relapsed.
- A clean answer counts as a check-in, even before its due date.

##### 8. Question pane (`UI.questionReview`, shared with the report and the challenge review)

**Header**, always visible:
- a status or result chip, plus a `Flagged` chip,
- for a trap: its pips and `1 of 2 clean answers`,
- a meta line: `Circles · Arc length · ▃ Medium · MC · Practice, Sep 21 14:02 · 1:12`, where the source is a link to the sitting's report or summary.

**Details** disclosure: the address `circles.arc · #48213` in DM Mono and **Copy link** (`/review/?open=q:circles.arc:48213`, which works only for the owner).

**Body.** `UI.question(host, item)`, then `reveal(fb, {open: true})`:
- The student's pick is `.no` and the key is `.ok`, as now.
- **Every wrong option carries a line under it naming its misconception**, in Archivo 500 12.5px soft with an orange dot.
  - The picked one starts with `Your pick ·`.
  - A filler option reads 'A near-miss number, not a named mistake'.
- The rationale is open.
- A grid-in shows `You entered 12 · Answer 9`.

**Hide answers** (TopTierPrep's, better).
- It hides the key, the per-option lines and the rationale, and shows an `Answers hidden` chip. The button becomes **Show answers**.
- It stays on across Prev/Next and is remembered per viewer (localStorage, in try/catch).
- Unlike theirs, the item can then be **re-answered**: **Check** files the answer through a 1-question drill as a Repeat.

**Family strip.** `This kind of question: seen 6 · right 3 · repaired 1`, then the last 10 results as small cells, oldest to newest, with a legend and a **History (6)** button that opens the modal (§9).

**Same mistake elsewhere** (when the norm is open or known on other templates): `Also a trap in 3 other question types: Slope from two points, Line from a table, …`, with **Practise across all 4**.

**Actions** (a wrapping row):
- primary **Fresh one like this**,
- **Again, exactly**,
- **Spot the trap** (MC only),
- **Save / Saved**,
- **Mark / Marked**,
- **Share**,
- **Report a problem** (the Session section's dialog),
- an overflow menu with **Add to Redo** (answered right only) and **Dismiss** (redo only), which asks: 'Remove this mistake without fixing it? It stays in your history.'

**Prev / Next** move through the current list, with J/K and ←/→. A `3 of 25` position shows between them.

**Inline mini-session.** 'Fresh one like this' and 'Again, exactly' run inside the pane.
- They create a 1-question drill: `POST /api/drill {list:'templates', ids:[t], count:1, source:'review'}` or `{list:'items', ids:[[t,s]]}`. It renders with the same `UI.question`, calculator and reference buttons, and answers through `/api/drill/{id}/answer`.
- A miss shows the named mistake, then **Try the repair**, which asks the repair the drill queued (the set grows to 2).
- A clean answer fills a pip with the map bar's animation.
- If the mistake closes, the pane shows `Fixed: <label>`, and the row leaves Redo with a 250ms collapse (instant under reduced motion) while the Fixed count goes up.
- **Back to the question you missed** returns to the original item.
- Pane drills are never finished, so they never appear as sittings in Results or History's Sitting view. Their answers show under Source = Review.

##### 9. Attempt History modal (`UI.history`, shared with the session and the report)

A `<dialog class="sheet">`, 560px wide on desktop and full-screen on a phone.

**Title.** `History · <skill>`, with the sub line: `This kind of question, on every set of numbers.`

**Summary row.** `seen 6 · right 3 · repaired 1 · repeats 1 · median 1:10`, then the open mistakes on this template, with their pips and labels.

**Table.**
- Columns: `#`, date and time, source, difficulty, a result cell with its label (`Wrong · picked C`), the misconception, time spent, flag.
- A row for this exact seed gets a `this question` tag.
- **Open** loads that exact question into the pane (in Review) or into a read-only review sheet (in the session and the report).

**Empty state.** 'No attempts yet. This is your first question of this kind.'

**Behaviour.**
- 'Load more' pages by cursor.
- Esc closes it (TopTierPrep's popover ignores Esc), and focus returns to the History button.

**Integrity.**
- In the practice session **before** answering, rows show but Open is disabled with the note 'Open after you answer'. Reading a solved sibling first would make this answer unclean.
- In a live test and on an unanswered challenge question, the History button is disabled ('After the test' / 'After you answer').

##### 10. Elsewhere (the same components)

**Question strip, one format in the practice session and the exam runner.** The slots, in order: number · **Mark** (flag, `aria-pressed`, orange fill when on) · **Save** · **History n** · **Details** · **Report** · (ABC in the runner, Eliminate in practice).
- In a live test, Save and History are disabled with a tooltip and `aria-disabled` reason 'After the test'.
- On a challenge question, they are disabled until it is answered.

**Practice session.**
- Mark is sent with the answer (`flagged: true`), which makes that answer unclean. If the answer is right, it opens an Unsure mistake.
- After a save, a 'Note' link shows for 5s and opens a small note popover.
- The Question Overview legend becomes Unanswered / Right / Wrong / Repaired / Flagged / Current, and gains the Status | Difficulty toggle (the Session section owns the layout).

**Exam runner** (`/test/`).
- Mark calls `POST /api/session/{sid}/flag`. `GET /api/session/{sid}` returns `flags`, so flags survive a reload and module 2. The module-2 navigator shows only its own questions; module 1's flags stay on the server.
- Check Your Work's FOR REVIEW card reads from the server.
- The runner also sends `ms` (dwell time since the question was shown) with each answer save.

**Report** (`/results/report/`).
- Question-grid filters: `All · Wrong · Blank · Flagged (n)`. Flagged cells get the corner flag, and the legend adds 'Flagged for review (n)'.
- The detail view becomes `UI.questionReview`, so it gets per-option misconceptions, Save, Mark, History, Share and 'Fresh one like this'.
- Saving from a finished test is allowed, blanks included.

**Practice builder** (the Practice section owns the layout).
- A **Source** segmented control: `New | Redo 25 | Marked 3 | Saved 14 | Fixed (check) 2`.
- For Saved, Marked and Fixed, a second toggle: `Exactly | Fresh versions`.
- The topic, difficulty, format and clock settings apply to every source.
- A live count reads `9 of your 25 mistakes are in these topics`, which TopTierPrep's count fails to update.

**Today.** A Review card:
- the open count with its pips, `7 half fixed`,
- `2 check-ins due`,
- `3 marked`,
- primary **Redo all · 22**, secondary **Open Review**.

**Me.** A Saved content card: `Open mistakes 25 · Marked 3 · Saved 14 · Fixed 40 · Answers 312`. Each number links to its tab.

**Session summary.** Each 'Opened' and 'Fixed' line links to `/review/?open=trap:<id>`.

##### 11. Phone (390)

- **Gutters.** 16px side gutters and no horizontal page scroll (`scrollWidth <= 390`).
- **Header.** The H1 at 28px, the helper line, and **Redo all · 22 questions** as a full-width pill.
- **Stat strip.** A 2-column grid: Open / Marked / Saved / Fixed. Check-ins due spans the full width when it is above 0.
- **Tabs.** Five equal segments, sticky under the top bar. Each segment has two lines: the label (Archivo 600 13px) and the count (DM Mono 12px).
- **Filters.**
  - One row: **Filters · 2**, a Sort select, and a search icon that expands the field.
  - Filters opens a bottom sheet (`<dialog>`) with every filter stacked, a sticky footer (`Clear` / `Show 12 results`) and a close X.
- **List.** Full width. Checkboxes are 24px in 44px hit areas, labels wrap to 3 lines at most, and the meta line wraps.
- **Pane.** Tapping a row opens it as a full-screen `<dialog>`.
  - X at the top left; the status chip and `3 of 25` at the top right.
  - The content scrolls, with a sticky footer: `‹` · **Fresh one like this** · `›`.
  - The other actions sit in a wrapping row above the footer.
  - It closes on Esc and on Back (`pushState`).
- **Action bar.** Fixed above the tab bar at `bottom: calc(62px + env(safe-area-inset-bottom))`.
  - The summary is one line and **includes the chosen options** (`12 selected · 10 questions · As missed · untimed`).
  - The primary button is full width. Level, Timed and the secondary actions sit behind an **Options** disclosure.
  - The page gets `padding-bottom: 200px`, so the last row is never covered.
- **History rows.** Two lines:
  - first: the checkbox, time, result and skill;
  - second: the source, `C → A`, time spent and the misconception.

##### 12. States

**Loading.**
- Stat tiles show grey number blocks, and the list shows 6 skeleton rows at the real row heights. They shimmer at 1.2s, and stay static under `prefers-reduced-motion`.
- Tab counts read `—`.
- The action bar is disabled.

**Error.**
- An error band reads `The server is not answering.` with **Try again**.
- The last good data stays on screen, and a failed action rolls back its optimistic change.
- A 409 from a set start shows its message inline in the action bar, for example 'no open mistakes in these topics'.

**New student** (no answers yet).
- The tiles show 0.
- A panel with three lines, each with an icon:
  - '**Redo**: every wrong answer, named by the mistake that caused it.'
  - '**Marked**: questions you flag in practice or a test.'
  - '**Saved**: questions you bookmark to keep.'
- Then **Start practice** (the coach's pick, as on Today) and a quiet **Take the diagnostic**.
- The pane is hidden.

**Nothing open, but history exists.** 'Nothing open. 40 fixed, 6 this week.' Then **Check 2 fixed mistakes** if check-ins are due, or **Keep going** (the coach set) if not.

**Empty tab.**
- Marked: 'Flag a question in practice or a test and it waits here.'
- Saved: 'Tap the bookmark on any question to keep it.'
- Fixed: 'Fixed mistakes move here. Each comes back once for a check a week later.'
- History: 'Every answer you give shows up here.'

**Filtered to nothing.** 'Nothing matches these filters.', **Clear filters**, and the tab count reads `0 of 25`.

**Lots of history.**
- Groups collapse past 8 rows.
- History, Saved, Marked and Fixed page 50 at a time by cursor.
- Counts and stats come from SQL, never from the rows loaded.
- Search runs on the server.
- The first page renders in under 300ms at 5,000 answers.

**Busy.** Buttons use `aria-busy`. Save, Mark, Unsave, Unmark and Note are optimistic and roll back on failure. One undo toast shows at a time.

**Share or worksheet refused.** An inline message: 'Today's challenge questions can be shared after today.'

**Storage blocked.** The shell's banner, as now.

##### 13. Keyboard and accessibility

- **List keys:** J/K or ↑/↓ move, Enter opens, X toggles the checkbox, `/` focuses search.
- **Pane keys:** ←/→ Prev/Next, F fresh one, E again exactly, S save, M mark, H history, A hide/show answers.
- **Shortcuts are ignored while focus is in an input, textarea or contenteditable**, so typing a grid-in or a note never triggers them. Esc closes a sheet or menu.
- **Semantics:** lists are `role=list` with rows as buttons; tabs are `role=tab` with `aria-controls`.
- **Announcements:** pips carry an `aria-label`, and result cells have text as well as fill and glyph.
- **Toasts** use `aria-live=polite`.
- **Touch targets** are at least 44px.

##### 14. Same mistake, other question types (extra)

At first use, the server builds a norm → templates index from 12 seeds per template (386 × 12 × 0.26 ms ≈ 1.2 s, cached in-process with `lru_cache`). There are 79 such misconceptions today, for example 'changed the sign of the slope' in 4 line templates and 'moved the decimal point one place' across percentages, rates and scatterplots.

- Redo rows show `+n elsewhere`.
- The pane lists the other templates.
- **Practise across all** builds a set of fresh seeds on those templates. Each one is drawn by walking seeds (at most 40) until the options include that misconception, so every question offers the same trap.
- The Redo 'Group by: Mistake type' uses the same index.

##### 15. Share (TopTierPrep's shared session, working)

**Share** in any action bar, and on the pane, creates `POST /api/shares {items, title?}` and copies `/s/?id=<id>` with `navigator.clipboard.writeText`. The toast reads 'Link copied'. If the clipboard is blocked, a read-only field with the link shows instead. There is no `navigator.share`, which froze their page.

**The landing page** (`/s/`):
- title (default 'A set from a friend'),
- `8 questions · Circles, Percentages · ▁▃▅ mix · about 12 min`,
- **Start**: a drill with those exact items for the visitor's own code, with the key shown only after each answer as always,
- and **Fresh versions instead**.

For the visitor, these are new questions, so they are clean evidence. On the sharer's side, a started share shows as 'Shared set' in the visitor's Source only; nothing about the visitor is shown to the sharer.

##### 16. Printable worksheet (extra)

**Print worksheet** on Redo and Saved opens `/review/print.html?…`: 1–3 fresh versions per selected template, numbered, with the stems, figures and choices, and space to work. The answers and each option's misconception are on the last page. It uses print CSS only.

The seeds are remembered as seen, so the worksheet never repeats in practice. The page says 'These answers are not filed. Practise online to count them.'

### 3.9.4 Extras: what they missed

- **Fresh versions of any list or selection**: Saved, marked, fixed, history or redo items can be practised again on new numbers ('Fresh one like this', 'Fresh versions · 1/2/3 each'). A finite bank can only repeat the same item, which tests memory more than skill.
- **Clean answers only: exact repeats never close a mistake or move mastery**: TopTierPrep's unlimited retries on the same question make accuracy meaningless. A Repeat is filed and shown; only an unseen (template, seed) answered without a flag counts as proof. Repaired is our better 'Mixed'.
- **Every wrong option explained, not just the one picked**: Every distractor names its misconception (Item.reasons), and a filler is labelled as a near-miss number, not a mistake. TopTierPrep's 'Distractor Analysis' is prose in one explanation and does not highlight the key after a miss.
- **Hide answers that can be re-answered**: Theirs only hides the key; you cannot re-attempt. Ours hides the key, the per-option lines and the rationale, remembers the setting, and lets the student re-answer. It files as a Repeat, so it never inflates mastery.
- **Spot the trap**: From a mistake, generate a fresh seed whose options include the same misconception and ask 'Which choice comes from: <misconception>?'. Only a bank with labelled distractors can build this. It trains recognising the trap, not only avoiding it, and it is not filed to mastery.
- **Same mistake in other question types**: 79 normalised misconceptions recur across 2 or more templates, 12 of them across topics (measured), such as 'changed the sign of the slope' in 4 line templates. The pane shows where else the trap lives, and 'Practise across all' draws fresh items whose options contain it.
- **Spaced check-ins on fixed mistakes**: A fixed mistake comes back once as a fresh question at 7 days, and again at 21 days if that is clean. A miss reopens it as Relapsed. This is TopTierPrep's vocab 'Due Today' applied to math, and it cannot run dry.
- **Unsure: right-but-flagged answers join the redo list**: A lucky guess is not mastery. Flag and get it right, and an Unsure item opens that needs one clean answer. TopTierPrep's marks mean nothing after the session.
- **Flag calibration**: 'You flagged 12 · 7 were right (58%)' tells a student whether to trust first instincts or to flag and return, which is a real test-day skill. TopTierPrep counts flags but never says what they were worth.
- **Redo at the difficulty of the miss, or one harder**: A repair should test the same thing at the same level, and 'Harder' lets a student prove it. TopTierPrep's redo filter has no link to the original question's difficulty.
- **Mistakes merged by misconception, not by numbers**: Normalising the numbers turns '10% change' and '50% change' on one template into one mistake with its hits added, so the counts are honest. The label stays concrete, and History keeps the exact text of each miss.
- **Attempt history for the whole kind of question**: Every seed of the template, across practice, tests, the challenge and QOTD, with source, difficulty, pick, misconception, flag and time. TopTierPrep's covers one item in one session.
- **Time per question in tests**: The exam runner sends dwell time with each answer, so History and the report know how long each test question took. TopTierPrep's report has no time per question at all.
- **Sittings you can retake without erasing them**: History grouped by sitting gives the list of sessions TopTierPrep lacks, with 'Again, exactly', 'Fresh versions' and 'Fix the misses'. That replaces their Clear Session, which deletes the history.
- **Fixed log with time-to-fix and relapse rate**: It shows progress on mistakes, not just a backlog. TopTierPrep never shows what was fixed.
- **Notes on saved questions**: Students write the trick down in their own words. TopTierPrep's notes live only on exam highlights.
- **Persistent flags in tests, per sitting**: Flags survive a reload and module 2, reach the report's Flagged filter and the Marked tab, and feed practice. Ours are lost today.
- **Working share links**: Share a question or a set with a friend or tutor. They start it on their own code and see keys only after answering. TopTierPrep's Share froze the page, and live-test and same-day challenge items can never be shared.
- **Printable fresh worksheet**: A tutor, parent or offline student gets a new worksheet every time, with answers and each option's misconception on the last page. A finite bank can only print the same pages.
- **History CSV export**: A tutor or parent can see every answer with its misconception, free. TopTierPrep's 'Share / Export Report' is a dead button.
- **Most-missed strip with one-tap 'Redo these 5'**: It points to the few mistakes that cost the most, without scrolling 25 rows.

### 3.9.5 Server changes

Tables and columns here are added by F4 as listed in §2.5; the drill fields map through §2.6; prefs through §2.7.

- **progress.norm() and the trap key**

  norm(reason) = lower(reason), with /[-−]?\d[\d.,/]*/ replaced by '#' and whitespace collapsed. A grid-in miss gets '', a flagged-right answer '~unsure', and the filler stays 'near-miss arithmetic slip' (kind 'slip').

  Known fold, documented in the docstring: in 29 templates two options of one item share a norm (circles.degree_radian 'divided by 360/90 instead of 180'; pct.series '2013 as a percent of 2014' and its reverse). They become one mistake whose label is the concrete text of the latest miss.

  An assert-based check in progress.py covers:
  - context.container_percent seeds 10% and 50% share one norm,
  - circles.coterminal's two quarter-turn options share one,
  - the filler maps to kind 'slip'.

- **Schema: traps rebuilt**

  db.py rebuilds traps the way _relax_form_id rebuilds sessions. Columns:
  - id INTEGER PRIMARY KEY (stable, used in ?open=trap:<id>), with UNIQUE(learner, template, norm),
  - reason (the latest concrete text), label, topic, hits, owed, opened, last, closed,
  - closed_how TEXT ('fixed'|'dismissed'),
  - relapses INTEGER DEFAULT 0,
  - seed INTEGER and session TEXT (the latest miss, or the hand-added item),
  - due TEXT (next check-in, ISO date) and checks INTEGER DEFAULT 0.

  The migration merges old rows with equal norm: hits are summed, opened takes MIN, last and owed take MAX, and closed is NULL if any merged row is open. seed and session are filled from the latest wrong attempts row.

  progress.carry merges on (template, norm).

- **Schema: attempts columns, computed in progress.record for every caller**

  New columns:
  - norm TEXT (NULL when right, '~unsure' for a flagged right),
  - repeat INTEGER NOT NULL DEFAULT 0,
  - repair INTEGER NOT NULL DEFAULT 0,
  - flagged INTEGER NOT NULL DEFAULT 0,
  - stem TEXT (plain text, first 200 characters, for search).

  New index attempts(learner, template, seed).

  progress.record itself sets repeat = EXISTS(an attempts row for the same learner, template, seed) before inserting, so the drill, record_paper, QOTD and the challenge all get it. repair comes from q.get('repair'), and flagged is a new parameter.

  The rules:
  - clean = right AND NOT repeat AND NOT flagged; only a clean answer lowers owed or counts as a check-in;
  - a right answer that is flagged opens or refreshes an '~unsure' trap with owed 1;
  - a wrong answer (repeat or not) opens, refreshes or reopens its trap. Reopening one with closed_how='fixed' adds 1 to relapses; a dismissed one just reopens.

  topic_mastery and board add AND repeat=0; days() still counts every row as study time. A one-off startup backfill fills stem and norm for old rows through generate (0.26 ms each).

  Consequence for test_flow: a retake of a fixed diagnostic form or shelf mock files repeats and does not move mastery. Scoring is untouched.

- **Schema: flags table (marks for review)**

  flags(learner, session, qid, template, seed, topic, at), PRIMARY KEY (learner, session, qid).

  It is keyed per sitting because diagnostic forms and shelf mocks are fixed papers whose (template, seed) recur, and one report's flags must not move to another. It is called flags, not marks, because drill.state() already returns 'marks' as the right/wrong list.

  'Flagged during the sitting' means flags.at <= sessions.finished (or earlier than the answer, for drills). record_paper(…, flagged=set of qids) and drill answers pass it to record.

  progress.carry adds flags (and shares) to its table loop. No sessions.marks JSON column is needed.

- **Schema: saved, sessions, shares**

  - saved gains note TEXT, session TEXT and qid TEXT.
  - sessions gains times TEXT (JSON qid → accumulated dwell ms, for tests).
  - A new table shares(id TEXT PRIMARY KEY, learner, title, items TEXT JSON, at).

- **Access rule: app.access(learner, template, seed) -> 'reveal' | 'kept' | None**

  - 'reveal' when this learner has an attempts row for the pair, or the pair is in a flags or saved row whose session is a finished mock, module or diagnostic. A finished report already shows those blanks.
  - 'kept' when the pair is in saved, or in flags whose session is a drill (kind 'drill') or is finished.
  - Otherwise None.

  Key, rationale and per-option reasons are returned only with 'reveal'. Drill exact items, shares and worksheets need 'reveal', or 'kept' from a practice drill, so a live-test item or an unanswered challenge item can never be re-served to read its key. Shares also refuse any pair in today's daily.challenge until the day is over (it is the same for everyone).

  POST /api/session/{sid}/flag checks mine(row, learner): GET /api/session/{sid} has no owner check, and a flag must not be settable by anyone holding the id.

- **GET /api/me gains review; GET /api/review/counts**

  /api/me adds review: {open} for the nav badge, which the shell already fetches.

  /api/review/counts returns {open, half, relapsed, unsure, marked, marked_right, marked_during, saved, noted, saved_unanswered, fixed, fixed_week, median_days, dismissed, due, answers, redo_questions, redo_templates}. redo_questions = Σ over open templates of max(owed).

  It is used by the stat strip, the tab counts, Today, Practice and Me. /api/today keeps 'mistakes' and adds 'review'.

- **GET /api/review/redo**

  Query: topics, difficulty, fmt, kind (misconception|gridin|slip|unsure), status (open|half|relapsed), q, sort (recent|hits|near|oldest|topic), group (topic|domain|norm).

  Returns:
  - items: [{id, template, norm, label, reason, kind, skill, topic, name, domain, hits, owed, clean, status, relapses, opened, last, difficulty, fmt, seed, session, source, given, given_label, elsewhere}]. The item fields come from the trap's latest wrong attempts row, joined on (learner, template, norm).
  - groups: [{key, name, domain, count, questions}]
  - total, questions

  Capped at 500 rows.

- **GET /api/review/marked, /saved, /fixed, /history (+ /history.csv)**

  All take the shared filters (topics, difficulty, fmt, source, since, until, q), cursor pagination (limit ≤ 100, default 50, next cursor or null), and return totals from SQL.

  - marked items: {session, qid, template, seed, topic, name, domain, skill, difficulty, fmt, at, during, session_kind, session_at, n (question number), answered, correct, given_label, answer, ms, stem}. calibration: {flagged, right}.
  - saved items: the same fields, plus note, tries and last_result.
  - fixed items: the trap fields, plus closed, closed_how, days_to_fix (closed − opened), due, checks. stats: {fixed, fixed_week, median_days, relapsed, dismissed}.
  - history items: {id, at, template, seed, topic, name, domain, skill, difficulty, fmt, correct, result (right|wrong|repaired|repeat), given, given_label, answer, mistake, ms, source, session, qid, flagged, repeat}. The cursor is the attempt id. It also returns days:[{day, questions, right, minutes}] in X-Tz local time, sittings:[{session, kind, source, topics, at, right, asked, minutes}] when group=sitting, and summary {answers, right, accuracy, median_ms, timed, repaired, repeats, by_difficulty}.

  source is derived with LEFT JOIN sessions:
  - kind drill → 'practice', or 'review' / 'shared' from cfg.source,
  - mock → 'section', module → 'module', diagnostic, challenge,
  - a session LIKE 'qotd:%' → 'qotd'.

  sessions with kind 'spot' are excluded everywhere, including /api/history. Stems for items without a stored stem come from an lru_cached generate(template, seed) and are cut to 160 characters. history.csv streams the same filtered rows with a header row.

- **GET /api/review/item and /api/review/family**

  item?template=&seed= goes through access() and returns 404 when None. It returns:
  - question (public fields), answer, rationale, reasons (only with 'reveal': a capitalised label per option, null for the key, 'A near-miss number, not a named mistake' for a filler),
  - attempts on this seed,
  - family {seen, right, repaired, repeats, median_ms, recent: [last 10 results]},
  - traps open on the template, elsewhere [{template, skill, topic}],
  - saved, note, flagged, address, access.

  family takes ?template= or ?session=&question_id=; the latter resolves the template on the server, so the session page never sees it. It returns {template, skill, topic, summary, attempts: […], next}. For a question from a live test, or an unanswered challenge question, it returns 409 'after the test'. Before a drill question is answered, the attempts carry no open link (openable: false).

- **Flag endpoints**

  - POST /api/session/{sid}/flag {question_id, on}: for mock, module and diagnostic sittings, while live and after finishing. It checks ownership and that the qid is on the paper, upserts or deletes the flags row, and returns {flags}.
  - payload() includes flags: [qid] for the whole session, so module 1's flags survive module 2. results() adds flagged: bool to each review item and flagged: n.
  - POST /api/flags {session, question_id, on} does the same for drills and challenges (challenge flags are hidden by access() until answered). It also accepts {template, seed, session, on:false} for clearing from the hub.
  - drill answers accept flagged: bool (DrillAnswer gains flagged = False). Flags set before the answer are also read from the flags table, so the two paths agree.

- **Per-question time in tests**

  POST /api/session/{sid}/answer accepts ms (0..MS_CAP). The server adds it into sessions.times with json_set, accumulating across revisits. record_paper passes times[qid] as ms, so History, the report and the median cover tests.

  This is shared with the Tests and Report sections: their plan already asks for a time tile. Old test rows keep ms NULL and show '—'.

- **Saved endpoints extended**

  POST /api/saved also accepts {template, seed, note?}, which must pass access(). Saving is allowed for a drill question, an answered challenge question, and any question of a finished test (blanks included); a live test is still refused.

  PATCH /api/saved {template, seed, note} sets a note of up to 280 characters, and returns 422 above that. Unsave stays {…, on:false}; the client re-posts the note on undo.

- **Mistake actions**

  - POST /api/mistakes/dismiss {id} sets closed = now and closed_how = 'dismissed'.
  - POST /api/mistakes/restore {id} undoes a dismiss and does not add to relapses.
  - POST /api/mistakes/add {template, seed} requires 'reveal' and opens or refreshes a '~unsure' trap with owed 1, labelled with the skill.
  - POST /api/mistakes/reopen {id} reopens a dismissed trap.

  GET /api/mistakes stays for compatibility with test_flow, with id, norm and status added.

- **POST /api/drill: one list source**

  The body gains:
  - list: 'redo'|'marked'|'saved'|'fixed'|'history'|'items'|'templates'|'related'|'share',
  - ids: a selection (trap ids, [session, qid] pairs, [template, seed] pairs, template names, attempt ids or a share id), or null for everything matching the filters,
  - exact: bool, meaning serve those (template, seed) pairs or fresh seeds on their templates,
  - each: 1–3 fresh per template,
  - level: 'as_missed'|'any'|'harder' (redo and fixed).

  topics, difficulty and fmt filter first. A 409 names what is empty ('no open mistakes in these topics'). Every exact pair passes access(), up to 120.

  The queue rules:
  - redo queues each template max(owed) times, all templates once before any second round;
  - fixed queues one per template and is flagged as a check-in;
  - related draws, for a norm, fresh seeds whose options contain it (at most 40 seeds walked per template).

  In drill._pick, a queued redo draws _fresh(b, template, {tier}): the tier of the trap's latest miss, the next tier up for 'harder' when _tiers_of has it, falling back to any.

  Aliases stay: mistakes:true = {list:'redo', ids:null}, and saved:true = {list:'saved', exact:true}. from_session stays.

- **Drill payloads**

  - public(q) adds seen (this learner's attempts on the template) for the History badge. It never includes template or seed.
  - _feedback adds reasons (per-option labels), family {seen, right}, flagged, repeat and trap ids.
  - state() keeps 'marks' (right/wrong) and adds 'flags'.
  - finish() adds repaired, repeats and opened/closed with trap id.
  - Pane drills (source 'review') are never finished.

- **Spaced check-ins (extra)**

  When a trap closes with how='fixed': due = closed + 7 days, checks = 0.

  A clean answer on its template while it is closed and due is set (early answers count too):
  - the first check sets checks = 1 and due = today + 21 days,
  - the second sets checks = 2 and due = NULL.

  A miss reopens it as a relapse. progress.coach adds the reason 'check', ranked below open mistakes and above weak topics. drill._pick asks one due template per topic before new material. counts.due reports the number due.

- **Spot the trap (extra)**

  POST /api/review/spot {trap_id} walks seeds from the builder cursor (at most 40, about 10 ms) for an unseen MC item whose reasons include the trap's norm. It remembers the item as seen and stores it as a session with kind 'spot' (never finished, excluded from every sittings list). It returns {id, question (public), prompt: label}.

  POST /api/review/spot/{id} {answer} returns {correct, trap_index, answer_index, reasons, rationale}. Nothing is filed to attempts. If no seed fits, it returns 409 'this mistake has no fresh version with that option'.

- **Related mistakes index (extra)**: progress.related(): a norm → templates index built on first use from 12 seeds per template, cached with lru_cache (about 1.2 s once). Fillers and '' are excluded. It feeds redo.items[].elsewhere, item.elsewhere, group=norm and list:'related'.
- **Shares (extra)**

  - POST /api/shares {items: [[t, s]] ≤ 40 | from: {list, ids}, title?} checks each pair with access() for the sharer (it must be 'reveal' or 'kept' from a practice drill), refuses today's challenge pairs, and returns {id} (token_urlsafe(9)).
  - GET /api/shares/{id} returns {title, count, topics, difficulties, minutes} and no stems.
  - POST /api/drill {list:'share', ids: id, exact: true|false} starts it for the visitor, with source 'shared'.

- **Worksheet (extra)**: GET /api/review/worksheet?list=&ids=&each=1..3 returns fresh items (public fields, answer, reasons, rationale), remembered as seen and not filed. It is capped at 40 items.
- **Tests in server/test_flow.py**

  New asserts:
  - norm merges two container_percent seeds into one trap with hits 2, and trap ids are integers;
  - an exact saved re-serve answered right leaves owed and mastery unchanged and files repeat=1; a wrong one refreshes the trap;
  - a flagged right answer opens an unsure trap with owed 1, and one clean fresh answer closes it;
  - test flags survive GET session and module 2, and reach results.review[].flagged and /api/review/marked after finish; flags from two sittings of the same diagnostic form stay separate;
  - /api/session/{sid}/flag from another learner returns 403;
  - /api/review/item returns 404 for an unanswered challenge item and for another learner's item; family returns 409 for a live-test question;
  - redo with a half-fixed trap starts a set of total 1;
  - dismiss then restore leaves relapses unchanged, and a miss after dismiss reopens without a relapse;
  - the history cursor pages strictly older;
  - carry moves flags;
  - a share of today's challenge item returns 409;
  - test answer ms accumulates into times and reaches attempts.ms.


### 3.9.6 Files this spec names, and who owns each

| file | owner |
|---|---|
| `web/review/index.html` | S10 |
| `web/review/print.html` | S10 |
| `web/s/index.html` | F6 |
| `web/mistakes/index.html` | S10 |
| `web/assets/ui.js` | F2 |
| `web/assets/ui.css` | F1 |
| `web/practice/session/index.html` | S4 |
| `web/test/test.js` | S5 |
| `web/test/index.html` | S5 |
| `web/results/report/index.html` | S6 |
| `web/practice/index.html` | S4 |
| `web/challenge/index.html` | S8 |
| `web/index.html` | S3 |
| `web/me/index.html` | S1 |
| `server/db.py` | F4 |
| `server/progress.py` | F4 |
| `server/drill.py` | F5 → S4 |
| `server/app.py` | F0 (routers register themselves, §2.10) |
| `server/test_flow.py` | shared: new checks go in server/checks/<task>.py |
| `README.md` | shared: each task edits its own subsection |

A file owned by another task is met through §2.9: the owner builds it, or this section's task adds its hook on its own page.

### 3.9.7 Shared needs

- UI.filterBar: dropdown chips (a Topic menu grouped by domain with tri-state checkboxes and counts; Difficulty pills; Format; Kind; Status; Source; Result; Date with native date inputs; Sort), a server-side search field and Clear, plus a 'Filters · n' bottom sheet on phone. Practice, Results, Tests history and the report's question filters need it too. → built in F1 kit.js
- UI.questionReview: one question pane (the practice renderer, reveal(open), per-option misconception lines, an inline meta line, Details with the address, the family strip, same-mistake-elsewhere, the actions Save / Mark / History / Share / Fresh one / Again exactly / Spot the trap / Report, re-answerable Hide answers, Prev/Next). The report detail, the Review pane and the challenge review all use it. → built in F3 question.js / runner.js
- UI.history: the attempt-history dialog for the whole template, opened from the session strip, the report and Review, with an integrity mode (no Open before answering; disabled in live tests and unanswered challenge questions). → built in F3 question.js / runner.js
- One result vocabulary with components (UI.resultCell: Right / Wrong / Repaired / Repeat / Blank / Flagged / Current, each with a glyph and an always-visible legend; UI.pips; UI.statusChip). The session's Question Overview, the report grid, Check Your Work and History all draw from it. → built in F1 kit.js
- One question strip for the practice session and the exam runner: number, Mark, Save, History n, Details, Report, and ABC/Eliminate. Mark state lives on the server (the flags table) in both, and Save and History are disabled while a test is live.  
  ↳ R5: the flags table (F4), endpoints in S10
- Per-question dwell time from the exam runner (ms on each answer save, accumulated in sessions.times). The Report section's time tile and the Tests section need the same.  
  ↳ R7, R8: qstate ms and attempts.sms (F4, S5)
- UI.actionBar: a sticky bottom bar with a live summary that echoes the chosen options, the options themselves and a primary button, sitting above the phone tab bar. The Practice builder's dock and every Review tab use it. → built in F1 kit.js
- UI.sheet: a generalised <dialog> that is full-screen under 640px, closes on Esc and on Back, and returns focus. The reference sheet, History, filters, the phone pane, the report dialog and the note popover use it. → built in F1 kit.js
- UI.toast with Undo (one at a time, 6s, aria-live polite) for unsave, unmark, dismiss and link copied. → built in F1 kit.js
- Shell: the Review nav item with an open-mistakes badge from /api/me review.open, and a 6th phone tab. The Today, Practice and Me owners need to agree on the order.  
  ↳ R1: the phone keeps 5 tabs; the item goes in the sidebar and the menu sheet
- The Report a problem dialog (from the Session section): the pane reuses it.  
  ↳ R17: UI.report (F6 report.js)
- One drill body with list / ids / exact / each / level, so the Practice builder's Source control, the Review action bars, shares and the report start sets the same way.  
  ↳ R10: the drill body, §2.6 (F5)
- The access() rule (reveal / kept / none) for every endpoint that returns a key or re-serves a (template, seed): Review, shares, worksheets, the challenge review and the report.

### 3.9.8 Acceptance checks

1. curl -s -H 'X-Learner: a:v2revacc1' localhost:8000/api/review/counts returns all zeros for a new code, /api/me has review.open == 0, and /review/ shows the new-student panel with 'Start practice'.
2. After a drill in which an MC question is answered wrong, /api/review/redo has one item with an integer id, kind 'misconception', owed 2, status 'open', a seed and a given_label; /api/review/history has a row with result 'wrong', mistake set and ms set.
3. Two misses on context.container_percent seeds whose reasons differ only in the percent give ONE redo item with hits 2 (its norm contains '#'), and its label is the concrete text of the second miss.
4. A miss whose option is 'near-miss arithmetic slip' gives kind 'slip' with the label 'Arithmetic slip'.
5. A half-fixed trap (owed 1) makes redo_questions count 1 for its template, and POST /api/drill {list:'redo', ids:[that id]} returns total 1.
6. Save a question, answer it right, start {list:'saved', exact:true} and answer it right again: that attempts row has repeat=1, the trap's owed is unchanged, /api/map mastery for the topic is unchanged, and History shows result 'repeat'.
7. Answer a practice question right with flagged:true: /api/review/redo gains an item with kind 'unsure' and owed 1, and one clean fresh answer on that template moves it to /api/review/fixed.
8. Live test: POST /api/session/{sid}/flag {question_id, on:true}; GET /api/session/{sid} includes it in flags; after module 1 → 2 the module-1 flag is still in flags; after finish, results.review[].flagged is true for it and /api/review/marked lists it with during:true.
9. The same flag call with another learner's X-Learner returns 403.
10. Two sittings of the same diagnostic form with different questions flagged: each report's flagged count matches only its own flags.
11. GET /api/review/item for the (template, seed) of an unanswered daily-challenge question returns 404; the same call under another learner's code for an item this learner answered returns 404; GET /api/review/family?session=<live test>&question_id=… returns 409.
12. POST /api/shares with today's challenge (template, seed) returns 409; a share of an answered practice item returns an id, and POST /api/drill {list:'share', ids:id, exact:true} under a second code serves that exact stem.
13. POST /api/mistakes/dismiss moves the item from redo to fixed with closed_how 'dismissed'; /restore brings it back with relapses unchanged; a later miss on a dismissed trap reopens it with relapses unchanged.
14. GET /api/review/history?limit=50, then ?cursor=<next>, returns only ids smaller than the first page's smallest id; summary.answers equals counts.answers when no filter is set.
15. A test answer saved twice with ms 3000 and 2000 files attempts.ms 5000 for that question after finish.
16. POST /api/me/carry moves flags rows to the new code (GET /api/review/marked lists them under the new code and returns an empty list under the old one).
17. Browser: http://localhost:8000/mistakes/ lands on /review/?tab=redo; clicking the Saved tab changes the URL to tab=saved, and Back returns to Redo.
18. Browser 1280: clicking a redo row opens the pane on the right with the exact missed question, the pick and the key marked, a misconception line under every wrong option, the skill and difficulty visible without opening Details, and pips; 'Fresh one like this' answers inline, and a clean answer fills one pip without a reload.
19. Browser 1280: Hide answers hides the key and rationale, stays on after Next and after a reload, and Check re-answers and files a Repeat.
20. Browser 1280: History with Group by = Sitting shows sitting headers with 'Again, exactly'; selecting 3 rows and pressing Fresh versions starts a 3-question set on those templates with unseen stems.
21. Browser 390: document.documentElement.scrollWidth <= 390 on every tab; a row tap opens a full-screen dialog that both Esc and the Back button close; the action bar sits above the tab bar, its summary shows the chosen Level, and the last row is not covered.
22. Browser 390: the Filters sheet with Topic = Circles shows only circle rows, and the tab count reads 'n of 25'; Clear filters restores all rows.
23. Browser: in the practice session, the History button shows a count before answering and opens the modal with earlier attempts on that kind of question across seeds, with Open disabled until answered; Esc closes it and returns focus to the button.
24. Browser: in /test/, the Save and History strip buttons are present but aria-disabled while the test is live.
25. Browser: the report page shows a 'Flagged (n)' filter after a test with a flagged question, and the flagged cell carries the corner flag and a legend entry.
26. Browser: pressing S while typing in a grid-in input or a note textarea types 's' and does not toggle Save.
27. PYTHONPATH=. python3 server/test_flow.py passes with the new asserts.

### 3.9.9 This section's open questions

Folded into Part 5 where they need a decision; kept here for context.

- Should Review be a 6th top-level nav item (recommended: it is where the study loop goes), or a tab inside Practice? A 6th phone tab is 65px wide at 390.
- Should exact repeats be left out of mastery and out of closing mistakes (proposed), or count as they do today? This changes the saved-set behaviour, and a retake of a fixed diagnostic form or shelf mock will no longer move the map.
- The digit-normalised key folds two different options of one item in 29 templates (for example circles.degree_radian's 'divided by 360' and 'divided by 90'). The exact fix is a stable Mis.tag per misconception in the bank. Should the bank owner add tags, with the server using the tag when present and the norm otherwise?
- Should Dismiss exist? The alternative is that mistakes close only on evidence. It is proposed with a confirmation, Restore and Reopen, for misclicks and bad items.
- In tests, should a question flagged and answered right also open an Unsure mistake? Proposed: yes, because a Bluebook flag usually means unsure.
- Spaced check-ins, Spot the trap, same-mistake-elsewhere, shares and the worksheet are fully specified. Ship them in the first pass with the core hub, or straight after it?
- Shares: should they expire (for example after 30 days), and should the sharer see how many people started one? Proposed: no expiry and no visitor data, since nothing about the visitor is needed.
- Grid-in misses name no misconception because SPR items carry no distractors. Where a template can also render the same parameters as MC, the typed value could be matched to a distractor's value. Worth asking the bank owner.
- The traps migration merges rows by normalised reason, which lowers existing students' counts. Is that acceptable without a notice?
- The worksheet consumes seeds (remembered as seen) without filing answers. Is that the right trade, or should worksheet seeds stay available to practice?

---

---

## 4. Build order

### 4.1 Waves

```
wave 0   F0 repo prep (serial, one task, small)
            |
wave 1a  F1 design system      F4 data layer      T-bank grid-in mistakes (runs on its own until done)
            |       \                |      \
wave 1b  F2 shell   F3 runner    F5 drill    F6 reports + sets
            \          |           |          /
wave 2   S1 Account & Me · S2 Classes · S3 Today · S4 Practice · S5 Tests · S6 Results & Report
         S7 Plan · S8 Compete · S9 Words · S10 Review           (all in parallel)
            |
wave 3   I1 integration and the full walk
```

* Wave 1b tasks start when their wave-1a dependencies are merged into `master`.
* Wave 2 starts when every foundation is merged. Its ten tasks run in parallel in separate
  worktrees; none edits another's files (4.3). Runtime needs between them are contracts
  (§2.9) that degrade quietly until the provider merges, so merge order inside wave 2 does
  not matter.
* T-bank touches only the bank (`satbank/`) and can merge any time after F0.
* I1 starts when wave 2 is merged.

### 4.2 Tasks

Each entry: what it builds (with the Part 3 sections it implements), what it owns
exclusively, what it needs, and its port. "→" marks a file that passes to a later owner
when the wave ends.

**F0 · Repo prep** (wave 0, port 8010). Builds §2.12 F0. Owns `server/app.py`,
`server/deps.py` →F4, `server/api_*.py` (each → its owner below), `server/api_legacy.py`,
`server/challenge.py` →S8, `server/checks/`, `web/manifest.webmanifest`, the icons,
`web/assets/head.js` →F2, stubs `web/assets/kit.js` and `charts.js` →F1, `.gitignore`, the
head block of every page (only the lines of the sweep), README's split, the first line of
`spec/rebuild.md`. Needs nothing.
State: built on `v2/f0`, not merged yet.

**F1 · Design system** (wave 1a, port 8011). Builds §2.1, §2.3, the F1 rows of §2.4,
Shell §2.13 tokens and §11 CSS. Owns `web/assets/ui.css`, `kit.js`, `charts.js`,
`web/404.html`, `web/dev/kit.html`. Needs F0.
State: not started.

**F4 · Data layer** (wave 1a, port 8014). Builds §2.5, §2.7 (validation), R8, R9, R12,
R13, R15, R16, R19 and the server items of Shell ("progress.days", "disputed attempts",
"learner_of retired", "PUT /api/me"), Today ("progress.days", "PUT /api/me", "carry"),
Report ("tests file their time", "progress.estimate"), Plan ("study time counts tests",
"trap rechecks", "PUT /api/me mirrors"), Review ("progress.norm", "traps rebuilt",
"attempts columns", "flags", "saved", "access rule", "spaced check-ins", "related"),
QBank ("progress: coach reasons, guess-aware mastery, record_trap, grid-in mistakes",
"notes", "prefs", "scoring.accepted_forms") and Compete ("progress.record and carry").
Owns `server/db.py`, `progress.py`, `prefs.py`, `estimate.py`, `satdates.py`,
`scoring.py`, `deps.py`, `api_me.py`, `api_notes.py`, `server/checks/f4.py`. Needs F0.
State: not started.

**T-bank · Named grid-in mistakes in the bank** (wave 1a, port 8017). Builds QBank's
"satbank Item.spr_mistakes": `Item.spr_mistakes`, computed before the SPR branch in every
template that already computes a mistakes list; `practice.to_question` stores
`spr_reasons` (F5 then S4 own that file: T-bank sends the two-line change to the owner);
the audit checks no spr_mistake value equals the key; a script prints "n of 133 grid-in
templates name their mistakes". Owns `satbank/item.py`, `satbank/topics/*/families/*.py`,
`tools/spr_coverage.py`. Needs F0. Ships with partial coverage and grows (open question 11).
State: not started.

**F2 · Shell** (wave 1b, port 8012). Builds §2.12 F2 = Shell §2 without §2.10, R1, R22,
R29. Owns `web/assets/ui.js`, `head.js`, `quick.js`, `palette.js`, `qr.js`,
`server/api_shell.py`, `server/checks/f2.py`. Needs F1, F4 (F5 for the palette's types
and Log a mistake at runtime).
State: not started.

**F3 · Question workspace and runner** (wave 1b, port 8013). Builds §2.12 F3 = R21, R23,
the F3 rows of §2.4, the runner key maps of §2.8. Owns `web/assets/question.js`,
`runner.js`, `runner.css`, `web/dev/workspace.html`. Needs F1.
State: not started.

**F5 · Drill engine and bank catalogue** (wave 1b, port 8015). Builds §2.6, R24, R33,
R34 and QBank's server items "blueprint.kinds()", "Measured levels", "POST /api/drill: new
body fields", "drill._pick / _fresh honour the filters and record why", Shell's "drill:
new sources and options", "blueprint.survey … GET /api/types", "POST /api/mistakes/log",
Words' "drill.py and POST /api/drill" (generic part), Review's "POST /api/drill: one list
source", Report's "POST /api/drill: only / each / scope / twin", Plan's "POST /api/drill:
task, recheck, fmt". Owns `server/drill.py` →S4, `practice.py` →S4, `api_practice.py` →S4,
`blueprint.py` →S5, `server/api_bank.py`, `server/checks/f5.py`. Needs F4.
State: not started.

**F6 · Reports and question sets** (wave 1b, port 8016). Builds R17, R18(c): Shell §2.10,
§10 and its "server/reports.py" items; the sets parts of QBank ("Shares"), Tests ("Share a
test") and Review ("Shares"). Owns `server/reports.py`, `server/sets.py`, `server/mail.py`
→S1, `web/assets/report.js`, `web/admin/reports/index.html`, `web/s/index.html`,
`tools/reports.py`, `server/checks/f6.py`. Needs F1, F4.
State: not started.

**S1 · Account, Me, Settings, Help** (wave 2, port 8021). Builds Part 3.1 §1, §3, §4, §5,
§6, §8, §9 and its server items (account, pairing, rotate, `/api/me/summary`, feed,
activity, achievements, export, delete, progress links and the shared view, diagnostic
sign-up joining the account, mail), R25, R31, Compete §9's Me Boards block, Words' Me
items, Review's Saved content card, Tests' test defaults. Owns `server/account.py`,
`api_account.py`, `api_profile.py`, `achievements.py`, `mail.py`, `web/me/**`,
`web/signin/**`, `web/pair/**`, `web/share/**`, `web/help/**`,
`web/diagnostic/signup.html`, `verified.html`, `server/checks/s1.py`.
State: not started.

**S2 · Classes** (wave 2, port 8022). Builds Part 3.1 §7 and its "server/classes.py" item,
R4 (class scope and class contests for Compete). Owns `server/classes.py`,
`web/class/**`, `web/join/**`, `server/checks/s2.py`.
State: not started.

**S3 · Today** (wave 2, port 8023). Builds Part 3.2 in full, R27 (QOTD), R30 (Review card,
Words tile), and the Today items of Review §10, Words §11 and Compete §9. Owns
`web/index.html`, `server/api_today.py` (`/api/today`, `/api/calendar`, `/api/scores`,
`/api/qotd`, the like-drill route), `server/daily.py`, `server/checks/s3.py`.
State: not started.

**S4 · Practice builder and session** (wave 2, port 8024). Builds Part 3.3 in full
(components come from F3, report and sets from F6, the body from F5), Compete §8 for the
practice session (R28), Review §10's session strip, Words' session hooks, Plan's session
summary. Owns `web/practice/**`, `server/drill.py`, `practice.py`, `api_practice.py`
(adds `/api/bank`, the session endpoints, `GET /api/drill`), `server/checks/s4.py`.
State: not started.

**S5 · Tests and the test window** (wave 2, port 8025). Builds Part 3.4 in full (runner
components from F3), Compete §8 for the test window, the Weekly Module and Season Final
starts, Review's flags in the runner, Shell's `UI.learner` and token rules for
`web/test/` (R32), QBank's "shelf sections and diagnostic forms remember what they serve".
Owns `web/tests/**`, `web/test/**`, `web/diagnostic/index.html`, `server/api_tests.py`,
`server/papers.py`, `blueprint.py`, `mocks.json`, `forms.json`, `tools/moderate.py`,
`server/checks/s5.py`.
State: not started.

**S6 · Results and the score report** (wave 2, port 8026). Builds Part 3.5 in full (the
player from F3, the report dialog from F6), R26, R35, the report's parts of Tests
(`?q=`, peers, notes, confidence, away, changes), Words (redirect), Compete (contest rows,
Ranked pill) and Review (Flagged filter). Owns `web/results/**`,
`server/api_results.py`, `web/assets/results-ui.js`, `server/checks/s6.py`.
State: not started.

**S7 · Plan** (wave 2, port 8027). Builds Part 3.6 in full, R14, the calendar feed of R18(b),
Words' Plan step 4 and Words task. Owns `web/plan/**`, `server/plan.py`,
`server/api_plan.py`, `web/assets/plan-ui.js`, `server/checks/s7.py`.
State: not started.

**S8 · Compete** (wave 2, port 8028). Builds Part 3.7 in full except the runner pages
(R28: S4 and S5 build those on its hooks), R3 (practice rank), R12's boards. Owns
`web/compete/**`, `web/challenge/**`, `server/compete.py`, `server/challenge.py`,
`server/api_compete.py`, `web/assets/compete-ui.js`, `server/checks/s8.py`.
State: not started.

**S9 · Words** (wave 2, port 8029). Builds Part 3.8 in full, R29's third tab
(`UI.addWord`). Owns `web/words/**`, `web/vocabulary/**`, `web/assets/words-ui.js`,
`server/words.py`, `server/words/**`, `server/words_index.json`, `server/phrases.py`,
`server/api_words.py`, `tools/build_words.py`, `server/checks/s9.py`.
State: not started.

**S10 · Review** (wave 2, port 8030). Builds Part 3.9 in full (components from F3, traps
logic from F4, sets from F6), R2, R5's endpoints. Owns `web/review/**`, `web/mistakes/**`,
`server/api_review.py`, `server/checks/s10.py`.
State: not started.

**I1 · Integration and the walk** (wave 3, port 8040). Runs every acceptance list in
Part 3 against the merged `master`; walks every page at 1280 and 390 with `a:v2revnew`
(new) and a seeded history learner; fixes seams in the owning files (by then every task is
merged, so I1 may touch any file in small commits); checks that every nav link lands on a
real page; finishes README and this file's State lines.
State: not started.

### 4.3 Ownership rules

* A file has one owner at a time (4.2). Passing a file on ("→") happens at the end of the
  wave; the next owner starts from the merged `master`.
* Shared-by-convention files: `README.md` (each task edits only its own subsection),
  `spec/rebuild-v2.md` (each task edits only its own State line), `server/test_flow.py`
  (existing asserts, smallest hunk, only when the task's change breaks them).
* No task edits `server/app.py` or `server/db.py` after its wave; routers register
  themselves and the schema is complete (§2.5, §2.10).
* Cross-section SQL reads are fine; writes to another section's tables go through that
  section's module functions.
* A need that the plan did not foresee is added as a contract line in §2.9 of this file in
  the same commit that starts using it.

### 4.4 Merging

1. Rebase the task branch on `master`.
2. Run `PYTHONPATH=. python3 server/test_flow.py` and the task's acceptance items on its
   own port.
3. Merge into `master` (`git merge --no-ff v2/<task>`), then remove the worktree.
4. Update the task's State line in 4.2 in that merge.

---

## 5. Open questions for the user

Each has a default the plan builds with until you say otherwise. The sections' own open
questions (end of each Part 3 section) are folded in here.

1. **Phone tabs.** Five (Today, Practice, Tests, Plan, Results), with Review, Words and Compete in the menu sheet (default), or does one of them get a tab?
2. **Words.** Ship about 750 SAT words and 70 transitions now, because their section is Reading & Writing (default), or Math language only? Who reads the ~1,090 definitions before launch?
3. **Daily Challenge.** Each student gets twin questions (same types, own numbers; default, stops key harvesting), or one identical ten with answers held until the day closes?
4. **Exact repeats.** A saved question served again, or a retake of a fixed diagnostic form, no longer moves mastery or closes a mistake (default). The mistakes migration also merges near-duplicate mistakes, so existing counts drop. OK?
5. **Sign-in.** Email codes need SMTP in production; without it codes only reach `server/outbox/` and pairing is the only way across devices. Add Google sign-in as well?
6. **Minors.** Parental consent before saving an email or joining a class? Teacher vetting before a teacher sees names and mistakes? Photo avatars stay off and country is opt-in (defaults). OK?
7. **People.** Who answers reports and key disputes, and moderates paper discussion? Which address is `SATF_REPORTS_TO`? Launch Discussion behind a flag until someone moderates?
8. **Diagnostic gate.** Keep the name-and-email step before its result (default for now), or show it directly like every other sitting?
9. **Pausing.** Save and exit stops a timed test's clock, and timed practice sets can pause; both are shown on the report (default). Or should the clock keep running, as on the real test?
10. **Dates.** We have Mar 13 2027; TopTierPrep lists Mar 6. All 2026–27 dates, the 8:00 AM doors time and the test-day checklist need checking against College Board before shipping.
11. **Grid-in mistakes.** Naming grid-in mistakes needs edits to up to 133 templates. Ship with partial coverage and grow (default)?
12. **Heuristics.** Confirm or change: pace tags (Steady up to 15, Ambitious up to 30 points a week), levels 1–7 (20 first tries to measure), crowd stats from 20 answers, drift at 40 points, practice rank by right answers over 7 days (rewards volume).
13. **Sharing.** A sharer's score shown to friends by default, links that never expire, and a progress link that shows mistake names (defaults). OK?
14. **Screenshots.** Store up to 10 images per report on disk (default), or text-only, since (template, seed) already reproduces the question?
15. **Desmos.** A production key is needed; the public trial key is in use today.
16. **R&W score.** A self-reported R&W score and target on Today and Plan, to show a 1600 total (default). OK?
17. **Official replicas.** A pool of templates pinned to College Board items, as the equivalent of their Question Bank toggle? College Board's reuse terms need checking first; left out.
18. **Mistake identity.** A stable tag per misconception in the bank would make mistakes exact (the number-stripped key folds two options together in 29 templates). Add it in T-bank?
19. **Live duels.** Real-time head-to-head (`spec/rating.md`) stays out; private contests and Compare cover play with friends. Later?
