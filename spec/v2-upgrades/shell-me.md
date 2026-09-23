# v2 upgrades: app shell, navigation, profile and account

Written 2026-09-23 for `spec/rebuild-v2.md` §3.1 (lines 653–2294). It merges three designers'
proposals (outcomes, experience, unfair advantage) into one build-ready list.

* **Precedence.** `spec/v2-decisions.md` wins over this file. This file wins over §3.1 where
  they differ: §3 of this file lists every place that changes. Part 2 resolutions (R1–R38)
  still hold, except the lines named in §3.2 "Outside the section".
* **The bar.** A student who uses TopTierPrep today opens ours and wants to switch, because
  this area does more for their score and is nicer and faster to use. Parity is failure.
* **Names.** Upgrades are U1–U28. Builders are Part 4's tasks (F1–F6, S1–S10, T-bank). New
  server modules are assigned to one owner each.
* **Subject-aware.** Per v2-decisions item 3, every new payload that is about a section
  (points, pace, readiness, habits, the avatar's domains) is keyed by `subject` (`math` now).
  A second subject is then additive.
* **Facts measured for this file** (on the current bank, 2026-09-23):
  * 1,030 official items have a `Source` that rebuilds them.
  * 911 of those rebuild onto one of the 386 served templates; the other 119 land on template
    names outside the served catalogue.
  * 2,186 of the 2,367 official wrong options (92%) match a reproduced choice that carries a
    named reason.
  * A sample of 8 seeds per template gives 2,550 distinct reasons. Families tag across topics:
    "answered a different quantity" 849 reasons over 19 topics, whole/part 219 over 18, sign
    149 over 16, inverted 109 over 16.
  * Topics hold 13 to 36 templates each.
  * `cryptography` 46.0.4 is installed locally. The repo has no requirements file.

---

## 1. Scorecard

The "v2 spec" column is §3.1 as written. The verdict says why ours is way better. Where v2 was
only at parity (or below), the verdict names the upgrade that fixes it.

| # | Their feature | Their version | v2 spec | After these upgrades | Verdict |
|---|---|---|---|---|---|
| 1 | Sidebar and icon rail | ~220px sidebar, a toggle to a ~60px rail, stacked wordmark | 248px sidebar and 68px rail, `[`, tooltips carrying the meta and the shortcut, an overlay at 760–1099px | An **Up next** block with Start under Search (U1); a play button on the rail; rail peek (U26); the page's sections as sub-links with scroll-spy (U26) | v2 PARITY: same shape, still a list of places. **U1 + U26 → WAY BETTER.** The chrome says what to do next, why, how long it takes and how many points it is worth, and starts it in one click (or `G N`) from every page. |
| 2 | Primary nav | 10 routes, no counts, one of them sells | 9 items with live metas: 12/28, ● 14, Resume, Test day, New, #4, 2 due | Adds an inbox dot (U25) and an urgent dot on the Today tab (U1) | **WAY BETTER already in v2.** Every item says what is waiting there; theirs are ten silent labels. |
| 3 | Active nav state | Grey-blue pill, bold label | `--wash`, 600 weight, a 3px orange bar, section mapping for sub-pages | The active item opens into that page's own sections, with scroll-spy (U26) | v2 PARITY. **U26 → WAY BETTER.** On Me (16 cards), Settings, Results and Help, any card is one click away. |
| 4 | Upgrade card | "Upgrade to Pro · Unlimited tests & QBank" with a TRIAL badge | Today card: minutes and questions against the goal, streak, the due assignment, exam countdown | Adds week-goal pips (U14), spare-day flames (U16), a registration deadline (U17); Up next sits above it (U1) | **WAY BETTER.** Their slot sells. Ours shows the student's own day and starts it. |
| 5 | User card | Avatar, name, role "User", chevron; badges Trialing / Teacher Seat | Avatar, name or handle, masked email or "Not saved yet" | A living-mark avatar that fills with domain mastery (U22); an unread count (U25); "Shared computer · Sign out" (U21) | v2 PARITY. **U21 + U22 + U25 → WAY BETTER.** It says whether progress is safe, what is new, and how far each domain has come. |
| 6 | User popover | Name and email, My Profile, Send feedback, Sign out (red); ignores Esc | A `role=menu` with Profile, Settings, Sign in, Pair, Class, Shortcuts, Help, Feedback, Sign out; Esc fixed | Adds the "Since you were last here" inbox (U25), Students on this device (U21), and Theme and text-size toggles (U26) | v2 PARITY: a bug fix plus links. **→ WAY BETTER.** Missed events are kept. Siblings switch in one tap without mixing their answers. |
| 7 | Floating quick-add | A draggable "Add your own word" button that covers Next | Quick sheet (Q or the bolt): Quick question · Log a mistake · Add a word; never floats | Log a mistake takes a College Board question ID, pasted text or a whole Bluebook test, and names the mistake from the letter the student picked (U2). The sheet also offers a time-boxed start (U1) | **WAY BETTER.** Theirs captures a word. Ours turns any missed official question into its exact question type, its named misconception (92% of official wrong options resolve to one) and unlimited twins. |
| 8 | Sign-in | Google only, and a wall before anything works | No wall. Email code, pairing, device code. Slower than Google on a new device; email needs SMTP | A passkey in 2 taps (U19). The phone approves a shared computer, with nothing typed on it (U20). A remembered email in 1 tap | v2 BELOW theirs for a returning student. **U19 + U20 → WAY BETTER.** Still no wall and no Google account needed. It is faster than Google, works without SMTP, and resists phishing. |
| 9 | Password | Set / Change password (8+ characters, confirm) | None: email codes | Passkeys (U19) | **WAY BETTER.** Nothing to remember and nothing to leak. |
| 10 | Sign out | Red Sign out in the popover and on the profile | Confirm dialogs. "Sign out everywhere else" rotates the one code | A list of devices, each with its own Sign out. Shared-computer sign-ins expire. Undo replaces the dialog (U21) | v2 PARITY. **U21 → WAY BETTER.** A library computer can be signed out from your phone, and no other device is affected. |
| 11 | Report modal | "Sent with your report" (UUID), Title 0/200, Category, Details 0/5000, 10 × 50 MB images; the student never hears back | (template, seed), a "named mistake doesn't fit" category, bounded disputes, replies, an admin page | "Answer key is wrong" is answered in about a second: a second, independent solver re-derives the key, and the student gets the named reason for the answer they gave. Matching reports merge ("me too"). One confirmed fix corrects every affected student. Bad questions are quarantined. No screenshot needed; a typo takes 2 taps (U3) | v2 PARITY in form. **U3 → WAY BETTER.** Most disputes become a lesson within seconds. Real key errors reach a person with evidence, and the fix reaches everyone. |
| 12 | Send feedback (+ /feedback) | The same modal, with no context | The same, plus page context and replies | A breadcrumb of the last 10 actions (kept in memory, shown before sending). A public "Fixed from your reports" list (U3) | v2 PARITY. **U3 → WAY BETTER.** Bugs arrive reproducible, and students can see their reports change things. |
| 13 | Toasts | Generic ("Task skipped / added …") | Generic, with actions; used for achievements, replies, assignments | An inbox keeps every missed toast. Undo on every reversible action. A welcome-back sheet (U25) | v2 PARITY. **U25 → WAY BETTER.** Nothing important vanishes after 4 seconds, and a slip is one tap to undo. |
| 14 | Profile layout | Left third / right two-thirds | The same split, 13 cards, a non-sticky left column, a phone order | Section sub-links with scroll-spy, a phone chip row, collapsible cards (U26). New cards: This week, Pace, Your habits, Test-day readiness | v2 PARITY. **→ WAY BETTER.** It holds more and is faster to move through. |
| 15 | Identity card and tiles | Avatar with a camera badge, name, email, a "Not set yet" pill, 2×2 tiles (Streak / Tests / Solved / Vocab); two streaks disagree | 2×4 tiles with sub-lines and links, goal pills, one streak | An outcome strip: score since you started, points on the table, fixes that held. Each tile gets a 14-day sparkline and a delta. Accuracy is first-try. Every figure opens how it is worked out, your numbers, and what moves it (U10, U13) | v2 PARITY: more volume counts. **U10 + U13 → WAY BETTER.** It says whether the score is moving and what moves it next. |
| 16 | Streak | 0 on the profile and 1 on the question of the day; any missed day breaks it | One server value; planned rest days kept | Earned spare days: 1 per 7 study days in a row, up to 2, shown everywhere (U16) | **WAY BETTER.** One number, which a sick day cannot wipe out, and free. |
| 17 | Rank snapshot | Global 128 and Country 43, with no contests played and no stated basis | Practice rank (right answers in the last 7 days) among everyone, the same exam date and each class; challenge lines | Adds movement since last week, the gap to the next place, a Climb rank among students who started near your band, and you against yourself 30 days ago (U11) | v2 PARITY: still ranks volume. **U11 → WAY BETTER.** It rewards learning, gives every level a race it can win, and states its terms. |
| 18 | Credits meters | Quota meters and Upgrade | "Question types met: 57 of 386" | Test-day readiness, weighted by how often each kind of question appears in College Board's own questions, with the type atlas (U8) | v2 PARITY: a raw count. **U8 → WAY BETTER.** Coverage tracks the questions the student will actually see, and the biggest gap is one click from practice. |
| 19 | Saved content | Counts: Saved Words, Redo Questions, Saved Questions | Counts with Practise saved, Fix all, due assignments, In progress with Resume | Saved questions come back as fresh twins in Up next at 7 and 21 days (U1) | **WAY BETTER.** A bookmark list becomes spaced retrieval. |
| 20 | Account block | Name and email editable inline, password, "Google connected", Sign out | Saved and unsaved states, Manage, Sign out | Passkeys list, devices list, and a recovery line: "You can sign in 2 ways" (U19, U21) | v2 PARITY. **→ WAY BETTER.** The student sees where they are signed in, and that they can't be locked out. |
| 21 | Avatar | Photo upload, replace, remove | An initial or one of 19 glyphs, all free to pick | Default: a living mark that fills with domain mastery. Glyphs are earned at Strong (U22) | v2 BELOW theirs. **U22 → WAY BETTER.** It says something true about the student, and stays photo-free for minors. |
| 22 | Study goals card | Target (not synced), exam date "N days remaining", Daily 2h, Weekly 12h, Preferred time (no effect) | Target and exam date synced and editable; daily and weekly bars; week dots; focus; preferred time → calendar | The target stated in questions, a projection to the exam, and week goals with history (U4, U9, U14) | v2 PARITY in facts. **→ WAY BETTER.** It says whether the target is realistic and what reaching it takes. |
| 23 | Target score modal | States the wrong "current score"; a number input; Save disabled until you type | Slider, chips, "+100 from your latest band"; synced | "What 700 takes: about 37 of 44 right; you're near 31." A live pace tag, one tap to a date that makes the target Steady, and "Raise to 750?" once it is reached (U4) | v2 PARITY. **U4 → WAY BETTER.** |
| 24 | Exam date | A select that includes past dates; the wizard uses a free calendar | Upcoming official dates, Another date, No date yet | Each chip shows the registration and late deadlines and a projected score. A deadline banner stays until "Registered"; the deadline goes to the calendar (U17, U4) | v2 PARITY. **U17 → WAY BETTER.** It covers missed registration, the plainest way to miss the SAT altogether. |
| 25 | Daily / weekly goal | "2 Hours" / "12 Hours", with bars | Bars and week dots (the plan's day rule) | Weekly goals chosen from evidence ("Fix the 4 open Circles mistakes", "Pass 6 check-ins") and a history of met weeks (U14) | v2 PARITY. **U14 → WAY BETTER.** |
| 26 | Preferred time | "Evening", with no effect anywhere | Calendar download or subscribe, with alarms | Calendar events titled with what is due. Opt-in push: "3 check-ins due · about 4 min" (U18) | **WAY BETTER already in v2** (it does something). U18 makes each reminder say what it is for. |
| 27 | Subject performance | A per-subject block, empty on a new account | 19 skills under 4 domains: bar, accuracy, mistake dots, Practise | Sorted by points on the table. Each skill shows whether it is measured or still rough, its 14-day trend, its last 5 answers and a fading marker. A 12-question Sharpen probe (U4, U5) | v2 PARITY: a report card. **U4 + U5 → WAY BETTER.** A priced to-do list the student can trust. |
| 28 | Score trend | A line chart with "Latest: N" | Range bars, target line, exam tick, click-through | A projection cone to the exam date, the plan's pace line, and what changed between two sittings (U9) | v2 PARITY: a nicer chart of the past. **U9 → WAY BETTER.** It ties effort to results and looks forward. |
| 29 | Achievements | 4 hard-coded tiles; View All is dead | 43 tiered badges with progress, earned dates and rules | Go on every badge in progress starts the drill that advances it. New Trap-proof and week-goal ladders (U13, U6, U14) | **WAY BETTER already in v2.** |
| 30 | Learning preferences | Timed/Untimed, Adaptive/Fixed, 3 toggles | 5 inline rows, instant save, helpers, full Settings | Modes (Learn · Build · Test-like · Custom) that follow the exam date, with each row saying who set it. Palette commands (U15, U24) | v2 PARITY: static defaults. **U15 → WAY BETTER.** Practice turns into test conditions on time, without the student remembering to switch. |
| 31 | Recent activity | A list of sittings | A filtered feed of 10 kinds under day headers, paged | Each row shows its effect (mastery words moved, mistakes fixed and opened, about how many points) and offers Again · new numbers, or Follow up (U12) | v2 PARITY in kind: log lines. **U12 → WAY BETTER.** |
| 32 | Subscription and billing | Header, plan status, usage meters, Pro $13.99 / Elite $23.99 cards, 7-day trial, payment history, /pricing | None: free | Nothing further | **WAY BETTER.** Everything is free, and each surface they sell from does study work: the Today card, Test-day readiness and Help. |
| 33 | FAQ accordion | Six billing questions | /help/ with live search, anchors, copy-link | A "?" beside every number opens its answer in place, with the student's own numbers. The palette searches Help. A Fixed list (U13, U24, U3) | v2 PARITY in form. **→ WAY BETTER.** |
| 34 | Classes (/my-classes) | Hidden; the teacher adds students | /class/ with a join code, class cards, assignments | Tailored questions and "Reach a level" homework (U27) | **WAY BETTER.** |
| 35 | Homework runner | A full test or a QBank session, time limit, Attach file, Finish | Set, module or section; fresh per student or the same for everyone; attach working; Start / Resume / Review | "Reach a level" serves fresh questions until each skill reaches the target (with a cap). Tailored puts each student's own mistakes first (U27) | v2 PARITY in shape. **U27 → WAY BETTER.** It assigns an outcome, not a count. |
| 36 | Teacher dashboard | Create a class, add students, assign, due dates | Roster, per-question results, the class's named mistakes with "Assign a repair" | Adds how many questions each student needed to reach the level, and who is stuck on which named mistake (U27) | **WAY BETTER.** |
| 37 | Single-question route | /question/:key | Permalink `?q=TEMPLATE:SEED` | "Send to a friend" defaults to a twin (same type, the friend's own numbers), with a head-to-head result (U28) | v2 PARITY. **U28 → WAY BETTER.** Answers can't be passed along. |
| 38 | Shared session links | /question-bank/shared/:id with a Start Practice landing | Sets, with owner results showing per-question right rates and the most common named mistake | A fresh-per-friend option (U28) | **WAY BETTER** (named mistakes in the owner's results). |
| 39 | Canvas and look | Light grey canvas, white 18px cards; no display settings | Paper with bordered tile cards; dark theme, large question text, reduced motion | Instant pages: prerender on hover, and paint from cache (U23) | **WAY BETTER.** Display settings they lack, and pages that open with content instead of a skeleton. |
| 40 | Phone chrome | Not seen in the walk | A 56px top bar with Search, the Review chip, Quick and the menu; 5 tabs; a menu sheet | A grip and swipe-up on the tab bar opens the menu. Up next comes first, the most-used rows sit at thumb height, a held tab offers shortcuts, and the palette sits above the keyboard (U26, U1) | Theirs was not seen. v2 put the daily actions in the hardest reach. **U26 → WAY BETTER.** |

---

## 2. Accepted upgrades

Grouped by how directly they move the score. Each one gives: why, screens and components,
controls and states, data and endpoints, how it uses the rest of the site, and acceptance
checks. Learner codes in the checks start `a:v2rev`; ports are each task's own.

### A. The study loop in the chrome

#### U1. Up next: one queue, one button, one key, on every page and after every session

*From: outcomes #1 and #7, experience #5, the unfair-advantage Today-card gap, and the saved-questions gap. Effort M. Builders: F2 (`server/next.py`, the chrome), F5 (the drill fields), S4 and S6 (chaining hooks), S3 (Today reads it).*

**Why.** Self-directed students over-practise the skills they like and skip rechecks. Theirs
has no single next action, and their plan generator failed 3 times out of 3. One ordered
queue puts spaced check-ins and the costliest mistakes first, and removes the minutes of
choosing that often end a session before it starts.

**Server: `server/next.py` (new, owner F2).**
`queue(learner, tz, limit=6) -> [item]`. Each item is
`{key, kind, title, detail, reason, minutes, pts, start: {path, body} | href, urgent}`.
The kinds, in order. The first rows that apply are taken, de-duplicated by `key`:

| # | kind | when | title (example) | reason (example) | start |
|---|---|---|---|---|---|
| 1 | `resume` | an unfinished timed module or section with time left | "Resume module · 12/22 · 18 min left" | "Your clock is still running" | href `/test/?s=` |
| 2 | `assignment` | a class assignment due within 24 h and not done (`deps.part('classes','due_soon')`) | "Period 3 · Circles · 10 q" | "Due tonight 23:59" | its start |
| 3 | `plan` | today's unfinished counted plan tasks, in plan order (`deps.part('plan','today_summary')`) | "Plan · Circles, Percentages · 10 q" | "Today's plan: 2 of 4 done" | the task's drill body |
| 4 | `checks` | fixed mistakes whose check-in is due today or earlier (R9 `traps.due`) | "Check-in: diameter vs radius (+2 more)" | "Fixed 10 days ago: checking it stuck" | `{pool:'checks', ids, count: min(3n, 9)}` |
| 5 | `redo` | open mistakes, ranked by the skill's points at stake (U4) × hits | "Fix: Used the diameter as the radius" | "Caught you 3 times · ≈ 6 pts" | `{pool:'redo', ids:[id], count:3}` |
| 6 | `habit` | one habit is ≥ 25% of the last 20 misses (U6) | "Habit: answered a different quantity · 8" | "7 of your last 20 misses" | `{source:'habit', habit, count:8}` |
| 7 | `probe` | ≥ 4 skills are rough and the learner has < 200 answers (U5) | "Sharpen · 12 q" | "7 skills still rough: measure them first" | `{source:'probe', count:12}` |
| 8 | `skill` | the coach's pick, reordered by points at stake (U4) | "Probability · 10 q" | "Most points on the table: ≈ 18" | `{topics:[t], count: prefs.set_length}` |
| 9 | `saved` | a question saved 7 or 21 days ago (±1 day) | "Saved Sep 2 · try a fresh one" | "Saved questions come back twice" | `{pool:'saved', ids, exact:false, each:1}` |
| 10 | `warm` | a Strong skill untouched for 10+ days (`prefs.keep_warm`) | "Keep warm: Circles · 3" | "Strong, last practised Sep 10" | `{pool:'review', topics:[t], count:3}` |
| 11 | `untried` | never-met types in the skill with the most points at stake | "5 new kinds of Circles question" | "3% of the test you haven't met" | `{pool:'untried', topics:[t], count:5}` |
| 12 | `qotd` | today's question of the day unanswered | "Question of the day" | "Day's-questions streak 4" | href `/#qotd` |

* `minutes` = count × the learner's median seconds per question over the last 60 days
  (default 95). `pts` comes from U4 where it applies, otherwise null.
* **Stage rules (U15).** In the final week, `probe` and `untried` are dropped. On the exam's
  eve, the queue is one item, "Rest. Nothing new today.", with an optional "Warm-up · 5"
  (check-ins, then keep-warm).
* `GET /api/next?limit=6` returns `{items}`. `/api/shell.next` carries the first 3.
  `ponytail:` recomputed on every shell load; memo it for 60 s with the shell if it shows up
  in profiles.

**Time box.** `POST /api/drill {source:'next', box: 5|15|30}`. F5 resolves it through
`next.resolve_drill` (the registry path of §2.6):
* It builds `segments`: check-ins due (≤ 3), open mistakes by points (≤ 4), one weak skill
  (≤ 3), one keep-warm skill (1).
* It sets `order:'mixed'`, so no two consecutive questions share a skill when two or more
  skills are in play, and `count: null`: after the segments it continues with the coach's
  pick until the box ends. `box` takes 5–60; the chips offer 5, 15 and 30.
* The session gets a box clock, "12:40 left of your 15". At zero the current question
  finishes and the summary opens, with Up next as its primary.

**Chrome.**
* **Sidebar**, new item between Search and Quick: the "UP NEXT" block.
  * A k-label.
  * The title (600 14.5, 2 lines max).
  * A DM Mono meta: "3 q · 4 min · ≈ 6 pts".
  * A 13px `--soft` reason line.
  * A full-width filled pill, **Start**, with the `kbd` "G N".
  * A `›` button (`aria-label="More up next"`) opening a `UI.pop` with:
    * the next 5 items, each with Start and **Not today**;
    * a chip row: "Got time? 5 · 15 · 30 min".
* **Rail**: a 44px orange play button under the search icon. Its tooltip reads
  "Next: Check-in · diameter vs radius · 3 q · 4 min · G N".
* **Phone**:
  * The first row of the menu sheet is Up next, with its Start and the time-box chips.
  * The Today tab gets a 7px dot when item 1 is `urgent` (resume, an assignment due, a
    check-in due).
* **Keys and links**:
  * `G N` starts item 1 on any shell page.
  * `/?next=1` (and `?next=1` on any shell page) starts item 1 once, then drops the parameter
    (used by U18 reminders).
* **Snooze**: "Not today" writes `localStorage satf.next.snooze {key: YYYY-MM-DD}`. The client
  drops snoozed keys for that local day. `ponytail:` per device; move to the server if
  students ask for it to sync.
* **States**:
  * Loading: two skeleton lines.
  * Error: the block hides, and the nav still works.
  * Brand-new student: "Take the diagnostic · 20 q", with a quiet "or one quick question".
  * Day done (the Plan day rule) with nothing urgent: "Day done · Another? Probability · 10 q".

**How it uses the rest of the site.**
* Today (S3): §3a's "Up next" reads `next.queue`, so there is one first-match rule.
* The palette's Suggested group (§2.8) lists the first 5 items.
* Chaining. Each of these makes "Next: {title}" its primary, read from `GET /api/next` with
  the just-finished kind and topic excluded:
  * the session summary (S4);
  * the report page (S6);
  * closing the quick sheet after at least one answer.
* So a student goes check-in → mistake → weak skill without returning to a menu.

**Acceptance.**
1. A learner with one trap due for a check-in today and one open trap: `GET /api/next`
   `items[0].kind == 'checks'` and `items[1].kind == 'redo'`. With an unfinished module that
   has time left, `items[0].kind == 'resume'`.
2. `curl -s -H 'X-Learner: a:v2revnextA' :PORT/api/shell` has `next`, an array of 3 or fewer
   items, each with `title`, `minutes` and `start` or `href`.
3. On `/me/` at 1280, `G` then `N` navigates to `/practice/session/?id=X`, and
   `GET /api/drill/X` has `cfg.pool == 'checks'`. On `/practice/session/` and `/test/`,
   `G N` does nothing.
4. `POST /api/drill {source:'next', box:15}` returns a session with `cfg.box == 15` and
   `count == null`. For a learner with traps in 2 topics, no two consecutive served questions
   share a topic.
5. "Not today" on item 1 hides it on reload for that local day. The next day it is back.
6. A learner whose exam is tomorrow gets one item whose title starts with "Rest".

#### U2. Bring your misses: an ID, pasted text or a whole Bluebook test becomes named mistakes

*From: outcomes #4, unfair-advantage #1, the experience "search first" gap. Effort M. Builders: F5 (`server/types.py`, the match and import endpoints), F2 (the quick sheet UI), F4 (traps `origin`, the `outside_scores.misses` column), S3 (`add_outside_score`).*

**Why.** Official tests and College Board's question bank are the most test-like practice
there is. Most students read the score and move on. Turning each miss into a named, spaced
repair keeps what the test taught. Theirs captures only vocabulary words.

**Log a mistake → one question** (replaces §2.7's four-step picker; the picker stays as the
link "Pick by skill instead"). One field: "Question ID, or paste or describe the question".
* **An 8-hex ID** (`^[0-9a-f]{8}$`, the College Board question ID) is an exact lookup.
  * At startup, `types.py` builds `cb_id → (topic, source id, template)` from
    `material/keys/*.json`, `material/transcripts/*.json` and `Source.build(Random(0))`.
  * 911 of 1,030 IDs land on a served template ("Exact"). The other 119 land on their skill
    only, and the text match picks the closest template in that skill ("Close").
* **A paste longer than 60 characters** is matched by TF-IDF cosine.
  * The index is the official transcripts' stems plus the survey's 18 generated stems per
    template.
  * Numbers are masked to `#` and single-letter variables to `v`. It uses stdlib `Counter`
    and `math` only.
  * It returns the top 3.
* **Anything shorter** searches the palette index (skill labels and misconception labels).
* **Result cards** each show:
  * a match word: Exact / Close (cosine ≥ 0.45) / Possible;
  * the skill chip and the type label;
  * one generated example from the reserved seeds (900000+), shown with no key.
  The student taps **This one**, or **None of these**, which opens the picker.
* **"Which answer did you pick?"**: A–D chips, or a grid-in field with its live preview.
  * With an Exact ID match, the server maps the official option at that letter onto the
    reproduced item's choice (`satbank.check._same`) and returns its named reason. This
    resolves 2,186 of 2,367 official wrong options.
  * Otherwise the sheet lists the type's surveyed reasons, plus "Something else" and
    "I don't know".
* **Where was it?** School · Bluebook · College Board question bank · Official practice ·
  Book · Other, plus the note (200).
* **Add to my mistakes** opens the trap (source `outside`). The sheet then shows the fix path
  in place:
  1. **The trap**: a reserved-seed example of that type, whose option carrying the chosen
     reason is marked "this is the trap", with the rationale.
  2. **Try one now**: a one-question inline drill (`want` = that reason, R24 `inline`).
  3. **Practise 3**: `{pool:'redo', ids:[trap]}`. The R9 check-ins at 3, 10 and 30 days
     follow on their own.

**Log a mistake → a whole test** (a segmented "One question | A whole test" at the top of the
tab).
1. The date, and the Math score. Both go through S3's `add_outside_score(source:'bluebook')`
   onto every trend.
2. Two 22-cell grids (Module 1, Module 2). Tapping a cell marks it missed and opens a compact
   picker: 19 skill chips, "Not sure", and optionally the letter picked. Helper: "Bluebook's
   review shows each question's skill."
3. **Build my follow-up**. It stores the misses on the outside score (`misses` JSON) and
   creates a "Bluebook follow-up" set. The set has 2 fresh questions per missed skill, drawn
   first from that skill's types the student has missed before, then from types they have
   never met (`segments`). Misses inside it open named traps as usual, and the set becomes
   Up next item 1.

**Bring many at once**: "Bring your misses" under Me › Saved & in progress, and a palette
action.
* A textarea takes up to 200 IDs, with any separators.
* The result is a table: ID · skill · question type · Matched / Not in our set.
* Two buttons: **Add 23 to my mistakes** and **Practise all · 2 each**.

**Rules.** The official item itself is never shown: only its type and our generated twins.
Transcripts are used as an index only. Responses never carry official stem text.

**Data and endpoints (F5 `server/types.py`, `api_bank.py`).**
* `GET /api/types/match?id=` and `POST /api/types/match {text}` → `[{template, topic, skill, score, via: 'id'|'text'|'label', example}]`, top 3. Rate limit 60 an hour per learner.
* `POST /api/types/match/pick {cb_id | template, letter | value}` → `{reason | null, reasons: [...]}`.
* `POST /api/mistakes/log` adds `cb_id?` and `letter?`. `origin` adds `cb_qbank`.
* `POST /api/mistakes/import {ids ≤ 200}` → `{rows: [{id, template, topic, matched}], added}`. Rate limit 5 a day.
* `POST /api/outside/misses {score_id, misses: [{module, n, topic, letter?}]}` → `{set: sid}`.

**Uses.** Review (S10) shows "Logged by you · College Board 23c5fcce" or "· Bluebook". Up next
(U1) picks up the follow-up set. Habits (U6) count logged reasons like any other.

**Acceptance.**
1. `GET /api/types/match?id=23c5fcce` → `rows[0].via == 'id'`, `topic == 'circles'`, and a
   template in `GET /api/types`.
2. `POST /api/types/match/pick {cb_id:'23c5fcce', letter:'C'}` returns a non-empty reason
   equal to one of that template's surveyed reasons.
3. A check in `server/checks/f5.py` walks every key: at least 900 IDs resolve with
   `via:'id'` onto a served template.
4. No `/api/types/match` response contains any 40-character substring of an official stem
   (a check in `server/checks/f5.py`).
5. Logging from an ID opens a trap with `source 'outside'` and `origin 'cb_qbank'`, and the
   attempts count is unchanged.
6. A whole-test log with misses in 3 skills creates a set of 6 questions over those 3
   topics, and `/api/scores` lists the outside score.

#### U3. Reports answered in a second, and one fix that corrects every student

*From: experience #2, unfair-advantage #4, the outcomes breadcrumb and Fixed-list gaps, the experience two-tap gap. Effort M. Builders: F6 (`reports.py`, `report.js`, admin), F4 (the `quarantine` table and `reports.parent`), F5, S3 and S5 (skip quarantined items), T-bank (a public `satbank.check.check_item(item) -> list[str]` over `_structure` and `_prose`).*

**Why.** With theirs, a report disappears into silence. Most "wrong key" reports come from a
misconception, not from a key error. Only a bank with a separate solver and named
distractors can answer one on the spot.

**The modal (changes §2.10).**
* **"Answer key is wrong"** now asks "Which answer do you get?" as A–D chips (MC) or as the
  grid-in field with its preview (F3). This replaces the 40-character box.
* The "Don't count this against me" checkbox moves to the "send to a person" step below.
* **Question reports** say "We have this exact question (circles/central_angle · seed 88213).
  No screenshot needed." Images sit behind "Add images".
* **Typo or display** and **Figure or table wrong** send without details: Report → chip →
  Send, 2 taps.
* **Me too**. When an open report exists on the same (template, seed), or on the same template
  and category in the last 30 days, the modal shows "Reported by 2 others · Being checked"
  and offers **Add me to it** in place of a duplicate.
* **Breadcrumb**. `UI.api` and `UI.shell` keep the last 10 actions in memory (page path,
  control label, API path and status). They are listed under "Include device details › Show",
  sent only with that box, and never stored on the device.

**The instant check** (only where the verdict has been shown; R19 and §2.10's live-sitting rule
still apply). `POST /api/report` with `key_wrong` regenerates the item from the stored
(template, seed) and runs three things:
* `satbank.audit.audit(item)`, the separate solver;
* `check_item(item)`;
* `scoring.is_correct` on the stored answer under today's rules.

The response is `{id, check: {outcome, text, reason?, key?, forms?}}`:

| outcome | when | the modal says | what the server does |
|---|---|---|---|
| `remarked` | the stored answer is marked wrong, but is accepted today | "You were right. 0.6667 is accepted, so this now counts as right." | The attempt is re-marked right (`progress.remark`). The trap it opened closes if nothing else holds it open. Status `fixed`, `closed_how 'auto'` |
| `forms` | a grid-in refused by the entry rule | "Your 0.66 is too short. Grid-ins accept 2/3, .6666 or .6667 (the fourth-digit rule)." | Nothing yet |
| `explained` | an MC pick whose option has a named reason | "Checked: a second solver, written separately from the question, also gets B (12). C is what you get if you used the diameter as the radius." Then the rationale steps | Nothing yet |
| `broken` | `audit` or `check_item` fails on this seed | "You found a broken question. It no longer counts against you, and nobody will be served it again." | `disputed = 1` for good; `quarantine(template, seed)`; flagged at the top of admin |
| `unsure` | none of the above | "We couldn't confirm this automatically. A person will check it." | Status `new`, sorted first in admin |

* After `forms` or `explained`, two buttons:
  * **That makes sense** (`POST /api/reports/{id}/accept`) → status `no_change`. It uses none
    of the 5 dispute slots.
  * **Still wrong: send to a person** → the spec's dispute, with the "don't count it" checkbox
    and the check result attached.
* In a live sitting nothing is checked. When the sitting ends, the check runs and posts an
  inbox item, "Report #123 checked" (U25).

**One fix for everyone (admin, changes §10).**
* **Key was wrong** offers "Just this question" or "Every seed of this template since {date}".
  It sets `disputed = 1` on every matching attempt of every learner, and closes the traps
  that only those attempts opened.
  * Each affected learner gets a feed item of kind `correction`: "A question you answered on
    Sep 21 had a wrong key. It no longer counts against you."
* **Stop serving** writes `quarantine(template, seed NULL = every seed, at, note, released)`.
  `practice.Builder`, `drill`, the blueprint fills and `daily` skip it until **Release**.
  The atlas (U8) shows the type hatched as "Being fixed".

**Fixed list.** `GET /api/reports/fixed` (public) → the last 30 reports marked Fixed:
date, skill or page, a one-line change and the number of reports. No names.
`/help/#fixed` renders it. The Thanks screen links to it.

**Schema (F4).**
* `reports.parent INTEGER` (me-too joins).
* `reports.check JSON`.
* `quarantine(template, seed, at, note, released)`, with PK (template, seed), where seed −1
  means the whole template.

**Acceptance.**
1. A finished drill miss on an MC question whose option C has a reason; `POST /api/report
   {category:'key_wrong', answer:'C'}` → `check.outcome == 'explained'` and `check.reason`
   equals that item's `reasons[2]`. The attempt's `disputed` stays 0. After `/accept`,
   GET /api/reports shows status `no_change`, and a 6th key report is still allowed.
2. A seed that `check_item` fails (a fixture that monkeypatches the check) → `broken`,
   `disputed = 1`, and `POST /api/drill {templates:[t], count:50}` never serves that seed.
3. Two learners report the same (template, seed). The second modal's `GET
   /api/reports/similar?session=&qid=` returns `{open: 1}`. Add me to it stores a row with
   `parent` set.
4. Admin "Key was wrong · every seed since" on a template with attempts from 2 learners sets
   `disputed = 1` on all of them, and each learner's feed has a `correction` item.
5. A report from a live mock returns no `check` and no key. After finishing, an inbox item
   "Report #n checked" exists.
6. `GET /api/reports/fixed` contains no learner id, name or email.

### B. Me: priced, measured, forward-looking

#### U4. Points on the table: every skill priced in scaled points, and the target in questions

*From: outcomes #3, experience #4, unfair-advantage #2, the skills/target/exam-chip gaps of all three, the experience target gap. Effort M. Builders: F4 (`estimate.gains`, `estimate.need`), S1 (Skills card, target popover), S7 (`plan.pace`), S6 (Results reuses the component).*

**Why.** A skill that makes up 1 question a test, answered at 30%, is worth less than one that
makes up 4 questions answered at 70%. Pricing both in points makes the trade-off visible, and
working by marginal points is the fastest route to a higher scaled score. Theirs shows
mislabelled percentages ("13% of test section, 1-8 questions").

**The model** (`estimate.gains(learner, subject='math')`, pure over the answer rows, with an
`assert` self-check in `estimate.py __main__`):
1. **Share of the section** per skill: `s_t` = domain share × the skill's weight within its
   domain.
   * Domain shares come from `blueprint.DOMAIN_SPLIT`: 15 / 15 / 7 / 7 of 44.
   * Weights within a domain come from one constant, `SKILL_WEIGHT`, taken from College
     Board's Question Bank counts in the teardown:
     * Algebra: linear equations in one variable 112, linear functions 170, linear equations
       in two variables 130, systems 126, inequalities 77.
     * Advanced Math: equivalent expressions 116, nonlinear equations 164, nonlinear
       functions 258.
     * Problem-Solving and Data Analysis: evaluating statistical claims 12, sample statistics
       28, one-variable data 84, percentages 83, probability 49, ratios 93, two-variable
       data 71.
     * Geometry and Trigonometry: area and volume 110, circles 67, lines and angles 102,
       right triangles 69.
2. **Accuracy** per skill: difficulty-weighted (`scoring.WEIGHT`) over the last 60 first-try
   answers counted by R8. It is pulled toward the learner's overall weighted accuracy with
   `EVIDENCE` = 10: `a' = (n·a + 10·ā)/(n + 10)`, where ā is 0.5 with no answers.
3. **Now**: `F = Σ s_t·a'_t` and `S = scoring._interpolate(F)`. This is the same curve the
   test score uses.
4. **Gain** for skill t: `_interpolate(F − s_t·a'_t + s_t·max(a'_t, 0.8)) − S`.
   * It is rounded to 5 and printed "about +20", or "under 5" when smaller.
   * The top 3 together are computed as one change, not a sum.
5. **Questions to Strong**: the smallest k right answers at the learner's current tier which,
   appended, lift `progress.mastery_of` past `STRONG`. It is stated as "at least k right".
6. **Time**: k × the learner's median seconds on that skill (default 95).
7. **Need** (`estimate.need(target)`): invert `_interpolate` to get F\*, then report
   `right_of_44 ≈ round(44·F*)` against the learner's `round(44·F)`, and the 3 skills with the
   largest gains as "where the missing ones are".

Returns `{subject, total, top3, skills: [{topic, gain, per_test (44·s_t, 1 decimal), accuracy,
evidence, to_strong, minutes}]}`. With fewer than 30 answers it returns `null`. `S` itself is
never shown as a score: only its differences are. The score estimate stays R16's.

**Me › Skills card** (changes §3.5).
* A `.seg` in the header: "By points · By domain". By points is the default once `gains`
  is not null.
* Each row adds, after the mastery bar:
  * "≈ +20" (DM Mono 600);
  * "about 4 of 44 · 52% right now" (`--soft`);
  * "at least 6 right · ~9 min".
  The top row carries a "Most points" chip.
* Header line: "About 60 points on the table · your top 3 hold 34".
* Footer pill: **Practise the top 3 · 15**: one mixed set over those three topics.
* Under 30 answers: "Answer 30 questions and this shows where your points are.", with the
  coach's set.
* A skill with fewer than 5 answers reads "Not measured yet · try 5".

**Target popover** (changes §3.3):
* "What 700 takes: about 37 of 44 right. You're near 31. The 6 you're most likely missing are
  in Circles, Probability and Nonlinear functions."
* The live pace line from S7's `plan.pace(target, exam, estimate)`: "45 days · 31 study days ·
  about 22 points a week · Ambitious".
* When the tag is Ambitious or harder, one chip moves the date: "Dec 5 makes it Steady".
* Once the target is reached: "Raise to 750?"

**Exam-date chips** add the projected score from U9 when a projection exists: "Dec 5 ·
~690".

**Copy and honesty.**
* Every figure says "about".
* The helper reads: "Estimated with our score model: how far your Math band would move if
  this skill reached 80%." It links to `/help/#points`.
* Help states that the scale anchors are our own stated choices (`scoring.py` says so), and
  that bands are ±100.

**Uses.** Up next orders mistakes and skills by it (U1). The coach breaks ties with it. The
palette's Skills group sorts by it. Results (S6) and the share view render the same rows.
Week goals word their suggestions with it (U14).

**Acceptance.**
1. A seeded learner: circles 10 answers at 30% right, linear_functions 20 at 90%, and 30 more
   spread over other skills. `gains.skills` has circles' gain > linear_functions' gain, and
   /me/ lists Circles above Linear functions under "By points".
2. `python3 server/estimate.py` passes asserts:
   * raising any single skill's accuracy never lowers S;
   * `gains` for a learner at 100% everywhere is all zeros;
   * `need(800).right_of_44 == 44`.
3. A learner with 12 answers: `gains == null`, and the card shows "Answer 30 questions".
4. The target popover for 700 contains the text "of 44" with an integer from 0 to 44.

#### U5. Measured or rough: every skill says how far to trust it, and a 12-question Sharpen

*From: outcomes #10, the outcomes skills gap (trend, fading), the experience "last 5" gap. Effort S–M. Builders: F4 (evidence, trend and last 5 in `board()`), S1 (UI), F5 (source `probe`), S4 (the summary's "what changed").*

**Why.** Coaching is only as good as its measurement. With a wrong picture of weak and
strong, sessions go to known skills while real gaps go unmet. Probing the least-measured,
highest-weight skills gets the most information per question. Theirs shows "LOW CONFIDENCE"
in red with no way to fix it.

**Rows** (each Skills row, and the shared `UI.skillRow`):
* **Evidence**:
  * Fewer than 10 answers in the mastery window: the bar gets a dashed extension (±) and
    reads "rough · 4 answers".
  * Otherwise: "measured · 26 answers".
* **Trend**: the arrow glyph and text for mastery now against 14 days ago: "▲ 14 days",
  "▼ 14 days", or nothing when the change is under 0.05.
* **Last 5**: a 5-cell strip of ✓ / ✕ (the R20 glyphs), so a recent slide shows instead of
  being averaged away.
* **Fading**: Strong and last answered 10+ days ago shows "Fading · last Sep 10" and
  **Keep warm · 3**.

**Header.**
* "7 skills are still rough. **Sharpen · 12 questions · ~19 min**."
* It starts `POST /api/drill {source:'probe', count:12}`. F5 picks the 4–6 rough skills with
  the highest `s_t × (1 − n/10)`, spreads the 12 across them with `adaptive: true` and
  `repairs: 'end'`, and orders them `mixed`.
* A new student sees Sharpen and "Take the diagnostic · 20 q" side by side.

**Summary** (S4). After a probe, the summary's first block reads "What changed: Probability
rough → Learning (the coach now includes it). Circles rough → Strong (the coach will skip
it)."

**Coach** (F4). A rough skill gets one probe item group before the coach assigns it a full
set (coach reason `probe`).

**Data.** `/api/me/summary.domains[].skills[]` adds
`{evidence, trend14, last5: [1,0,1,1,0], fading, last}`.

**Acceptance.**
1. A learner with 4 circles answers: the circles row contains "rough · 4 answers". With 26 it
   contains "measured".
2. `POST /api/drill {source:'probe', count:12}` for a learner with 6 rough skills → 12
   questions over 4 to 6 topics, all rough ones.
3. A skill at mastery ≥ 0.8 whose last answer is 11 days old shows "Fading" and a Keep warm
   link that posts `{pool:'review', topics:[t], count:3}`.

#### U6. Habits and the trap gauntlet: your misconceptions, grouped across skills

*From: outcomes #2, unfair-advantage #3. Effort M. Builders: F5 (`server/habits.py`, sources `habit` and `gauntlet`), S1 (the card and the Trap-proof ladder), F3 and S4 (the verdict chip), S10 (optional group-by in Review).*

**Why.** One habit, such as "answered a different quantity than asked", costs points in every
domain. Rehearsing the catch across skills, interleaved, transfers better than fixing
eleven separate mistakes one question type at a time. On test day the "tell" is one check the
student can run on any question. Their options carry no labels, so they cannot even count a
misconception.

**Families** (`server/habits.py`, owner F5). There are 11: `{id, name, tell, regex}`, applied
first match wins, in this order:

| order | id | name | tell |
|---|---|---|---|
| 1 | `formula` | Mixed up two formulas (radius/diameter, area/perimeter, 180/360) | "Write the formula before the numbers." |
| 2 | `percent` | Percent handling | "Percent of what? Name the base first." |
| 3 | `units` | Units and conversions | "Circle the unit the answer wants." |
| 4 | `roots` | Squares and roots | "Did you square, or take the root? Check both ways." |
| 5 | `inverted` | Inverted a ratio, rate or slope | "Say it as 'per': which quantity is on top?" |
| 6 | `sign` | Flipped a sign or direction | "Check the sign against a rough estimate." |
| 7 | `whole_part` | Gave the whole (or the rest) instead of the part | "Is it the part they asked for, or what's left?" |
| 8 | `early_late` | Stopped a step early or went a step too far | "Reread the last line: is this the final quantity?" |
| 9 | `read` | Read the wrong row, axis or point | "Point at the row or axis before you read it." |
| 10 | `different` | Answered a different quantity than asked | "Before you pick, reread what exactly is asked." |
| 11 | `slip` | Arithmetic slip | "Estimate first; does the answer fit?" |

* The families are tagged at startup over each template's surveyed reasons (`blueprint.kinds()`).
  An `OVERRIDES` dict fixes misfiles.
* The habit of a trap or a wrong attempt is computed from its reason, so no schema changes.
* `python3 server/habits.py` asserts that every family spans at least 3 topics, and prints
  the reasons and the share left untagged.

**Me › "Your habits"** (a new card after "What keeps catching you"). The top 3 habits by misses
in the last 60 days. Each row has:
* the name (600 15);
* "11 misses across 5 skills", with skill chips;
* the trend against the previous 30 days ("↓ 4 fewer");
* the tell in italics;
* **Drill this habit · 8**.

The drill is `POST /api/drill {source:'habit', habit, count:8}`. F5 resolves it:
* `templates`: those with a reason in the family, the student's missed ones first, at most 120;
* `want: {template: family regex}`;
* `order: 'mixed'`.

Every question then has an option built on that habit, across different skills, interleaved.
The summary shows the tell above the results.

**Trap gauntlet** (a header pill on "What keeps catching you": **Trap gauntlet · 10**).
* It takes 10 questions whose tempting wrong option is one of the student's own named
  misconceptions (trap norms, open or fixed in the last 60 days, ranked by hits × recency).
* Each is placed in a question type where the student has never met that misconception. With
  none left, it falls back to fresh numbers in the same types.
* Nothing is flagged during the set.
* The summary groups by misconception: "Used the diameter as the radius · caught you 3× in
  Circles · beaten in 3 of 4 new places", then each place with ✓ or ✕.
* A miss opens a trap on the new template, as any miss does.
* Empty: "Miss a few questions first: the gauntlet is built from your own mistakes."

**Elsewhere.**
* A wrong answer's verdict (F3 workspace, S4) carries a chip, "Habit: answered a different
  quantity", with the tell in its popover and a link to the card.
* Up next adds a habit drill (U1 row 6).
* The share view shows the habits.
* A new achievement ladder, Trap-proof (beaten in a new place 5 / 20 / 50), goes through R25.

**Data.**
* `/api/me/summary.habits: [{id, name, tell, misses, skills: [topic], trend}]`.
* F5's `want` matcher also tests `progress.norm(reason)`, so a norm string (escaped) works as
  a regex: a one-line change.
* The norm index (template → norms its distractors carry) is shared with Review's "same
  mistake elsewhere".

**Acceptance.**
1. `python3 server/habits.py` exits 0 and prints 11 families, each spanning ≥ 3 topics.
2. A learner with 3 traps whose reasons tag `whole_part` across 2 topics →
   `summary.habits[0].id == 'whole_part'` and `skills` has 2 entries.
3. `POST /api/drill {source:'habit', habit:'whole_part', count:8}` → 8 questions. A check in
   `server/checks/f5.py` regenerates each and finds an option reason matching the family.
4. `POST /api/drill {source:'gauntlet', count:10}` for a learner with traps on 2 templates →
   at least one served template is not a trap template, and has an option whose norm equals
   a trap norm.

#### U7. Pace: where the minutes go, and the drill that fixes each case

*From: outcomes #5, plus the "when you guess" line from outcomes #6. Effort M. Builders: F4 (`progress.pace`), F1 (`UI.quadrant` in charts.js), S1 (the card), S5 (the optional test-day hook).*

**Why.** In a timed module a 3-minute solve costs two other questions. Accuracy gains are
wasted if the student can't finish, and pacing can only be trained once the student sees,
skill by skill, where the minutes go. Theirs records time only inside a QBank attempt.

**Data** (`progress.pace(learner, days=60, subject='math')`, owner F4). Per skill with at
least 5 timed first-try answers:
* the median ms on right answers, the accuracy and n;
* time from `attempts.ms`, or `sms` when that is null (practice and, through R7, tests).

It also returns:
* `forecast`: the sum over a blueprint-mixed 22-question module of each slot's skill median,
  against 2,100 s, with the blanks it implies;
* the four quadrant lists;
* `guess: {n, right}`, from `attempts.guess` and `qstate.conf == 'guess'`;
* `struck2: {n, right}` (questions where two options were struck first).

**Me › "Pace"** (a new card after Score trend).
* **Header**: "At your pace a module takes 38:40 of 35:00: about 2 questions left blank." It
  carries a pill, **Pacing drill · half a module (11 q · 17 min)**, which starts
  `{mix:'blueprint', count:11, timed:true, minutes:17}`.
* **Chart**: `UI.quadrant(host, points, {x:'seconds', xRef:95, y:'accuracy', yRef: mean})`.
  * Each skill is a labelled glyph dot.
  * It has `role=img`, an aria summary and a hidden data table.
  * On the phone: a "Chart | List" seg (List gives skill, median, accuracy, quadrant chip and
    action).
* **Quadrants**, each with a label and one action:
  * Slow and right, "You know it, slowly": **Speed drill · 8 in 9 min**
    (`{topics:[t], count:8, timed:true, minutes:9}`).
  * Fast and wrong, "Rushing": **Careful set · 8** (untimed, instant feedback). The summary
    shows the student's top habit tell (U6).
  * Slow and wrong, "Time sink": **Learn it untimed · 8**. The skill also joins "Skip first
    on test day", which Tests' test-day checklist and the runner's pace guide read (S5,
    optional).
  * Fast and right, "Banked": **Keep warm · 3**.
* **"When you guess"** line, shown only when n ≥ 20:
  * "Your guesses are right 29% of the time (chance is 25%)."
  * With `struck2.n ≥ 20`: "When you strike two options first you're right 51%: strike, then
    guess."
* **Empty** (fewer than 3 skills with 5 timed answers): "Answer with the clock on to see your
  pace." with **Timed set · 10** (`clock: pace`).

**Acceptance.**
1. A learner with 6 timed right answers in circles at a median of 150 s and 90% accuracy:
   `pace.skills.circles.quadrant == 'slow_right'`, and the card offers "Speed drill".
2. `forecast.seconds` equals the sum of the per-slot medians (a unit assert in
   `server/checks/f4.py`).
3. A learner with 25 guess-tagged answers, 7 right → the line reads "28%".

#### U8. Test-day readiness: the type atlas, weighted by College Board's own questions

*From: unfair-advantage #6, the outcomes "types met" gap. Effort M. Builders: F5 (weights in `GET /api/types`), S1 (the card), F1 (`UI.cell` in a grid).*

**Why.** "57 of 386" weighs a rare type the same as one on every test. Weighting by how often
each form appears tells the student how ready they are for the questions they will actually
see. Theirs meters quotas.

**Weight** per template: `s_t × (official_t + 0.5) / Σ over the topic (official + 0.5)`.
* `official_t` is how many of the topic's official items rebuild onto that template (911
  land on served templates).
* `s_t` is U4's section share, so the weights sum to 1.

A type is **ready** once met and answered right on the first try at least twice (R8
counting). **Readiness** = Σ weight of the ready types.

**Me › "Test-day readiness"** (replaces §3.11).
* **Header**: "Test-day readiness **71%**", with the helper "Each kind of question counts by
  how often it comes up: its skill's share of the test, and how often College Board's own
  questions take that form." Second line: "57 of 386 question types met".
* **Atlas**: 19 skill rows under 4 domain headers.
  * Each row holds its types as 14px cells with 3px gaps, largest weight first.
  * On the phone, rows wrap at 20 cells.
  * Cell states, each with a glyph and counted in a legend: unmet (dashed), met (`--tile-2`),
    ready (ink with ✓), open mistake (orange dot), being fixed (hatched, U3).
* **Cell tooltip** (focus or hover; `role=grid`, arrow keys move): "Central angle from an arc ·
  met 6 · right 5 · last Sep 21 · 9 official questions take this form".
* **Cell click**: a mini sheet with a generated example (reserved seed, no key),
  **Practise 5 of this type** and **Log a mistake on it**.
* **Actions**:
  * **Practise my biggest gaps** runs `{templates: the prefs.set_length unmet or unready
    types with the most weight}`.
  * Each skill row has "Practise unmet".
  * When all are ready: "Every type ready." and the button hides.

**Data.**
* `GET /api/types` adds `weight` and `official` per template.
* `/api/me/summary.coverage` becomes `{readiness, met, total, types: {template: {met, right, last, open}}}`.

**Acceptance.**
1. `GET /api/types`: the weights sum to 1 (±1e-6). The circles weights sum to
   7/44 × 67/348 (±1e-6).
2. A learner with 2 first-try rights on the heaviest circles template has
   `readiness == that weight` (rounded to 3 places).
3. At 390px the atlas has no horizontal scroll (`scrollWidth <= 390`).

#### U9. A score trend that looks forward

*From: the score-trend gaps of all three designers. Effort S. Builders: F1 (`UI.bandChart` options), F4 (`estimate.projection`), S1 (`gaps` in the summary).*

**Why.** Theirs is a line chart of the past. Seeing the projected band on the exam date, next
to the pace the plan needs, shows whether today's effort is enough. The "what changed" gap
ties effort to results.

* **Projection** (`estimate.projection(learner, to_day)`, F4):
  * It needs ≥ 2 scored standard sittings in the last 60 days.
  * The slope is a least-squares fit of the band midpoints against days, clipped to
    ±40 a week.
  * The cone's half-width is 70 + 5 × weeks ahead, capped at 150.
  * Label: "At this pace: 640–700 on Nov 7".
  * With fewer sittings there is no cone, and a line reads "Two modules in 60 days start a
    projection."
  * `ponytail:` a linear fit; replace it with a model if it misleads.
* **Pace line**: a dashed line from the plan's starting estimate (`plans.start`) to the target
  on the exam date, when a plan exists.
* **What changed**: hovering or focusing the gap between two adjacent sittings shows "Sep 12 →
  Sep 20: 212 questions · 3h 40m · 11 mistakes fixed · Circles → Strong · +40". It is computed
  by the server from `progress.days` and the traps closed between the two finish times
  (`summary.score.gaps[]`). The biggest-gain gap is labelled once on the chart.
* The chart's hidden table gains "Projected" and "Pace" rows.

**Acceptance.** A learner with sittings at midpoints 500 (Sep 1) and 560 (Sep 15) and an exam
on Nov 7: `summary.score.projection.mid` is between 560 and 800, the SVG has a cone path, and
the hidden table has a "Projected" row. With one sitting, `projection == null`.

#### U10. Profile headline: an outcome strip, and tiles with direction

*From: the outcomes, experience and unfair-advantage tile gaps. Effort S. Builders: S1 (summary series), F1 (`UI.tile` sparkline).*

**Why.** Volume tiles say how much was done, not whether the score is moving.

* **Outcome strip**, above the tiles in the identity card. There are 3 figures, each a button
  opening its lever (U13):
  1. "**+80** since you started · 480–560 → 560–640": the first scored sitting against
     `estimate(learner).latest` (R16). Before 2 sittings: "Your first module sets your start."
  2. "**≈ 60** points on the table · top 3 hold 34" (U4).
  3. "**12 of 14** fixes held": check-ins passed out of those due so far (R9).
* **Tiles** (R31's 2×4). Each tile adds:
  * a 24px 14-day sparkline, with no axis, `role=img` and a text summary;
  * a delta against the previous 7 days, as an arrow glyph plus text: "▲ 84", "▼ 40m",
    "▲ 5 pts".
* ACCURACY is labelled **FIRST-TRY ACCURACY**. Its lever says repeats and retries are left
  out (R8), which is why it means something; theirs allows unlimited retries.
* **Data**: `summary.stats.series: {answered, minutes, accuracy, fixed}` (14 values each) and
  `summary.stats.delta`.

**Acceptance.** For a learner with 84 answers in the last 7 days and 0 in the 7 before, the
ANSWERED tile's delta reads "▲ 84", and its sparkline has 14 points.

#### U11. Ranks that reward learning: Climb, the gap to the next place, and you against you

*From: the rank gaps of all three designers. Effort S–M. Builders: S8 (`compete.climb`, weekly snapshots through `rank_snapshot`), S1 (display).*

**Why.** Ranking by right answers rewards grinding easy questions, and a weaker student who is
improving fast sits near the bottom (open question 12). Theirs is Global 128 with no stated
basis.

Each practice-rank line (§3.2) gains:
* **movement** since last week, "▲ 3", from S8's weekly snapshot;
* **the gap** to the next place, "7 right answers to pass #3", from the neighbouring row.

A new line, **Climb**: "Started near 520 · +90 · ahead of 74% of 212".
* The cohort is learners whose first scored standard sitting's midpoint is within ±40 of
  yours.
* The metric is R16's `mean3` midpoint minus that first midpoint.
* It is shown only when the cohort has n ≥ 20 (R16's rule). Board visibility (R12) applies.

A new line, **You, 30 days ago**: "+60 est. · 2 skills to Strong · 9 mistakes fixed". It is
shown once 30 days of history exist.

**Acceptance.**
1. 20 seeded learners with first midpoints within ±40 and varied gains: `ranks.climb.of == 21`
   for a 21st, and its rank is ordered by gain.
2. With 19 in the cohort, `ranks.climb == null`.
3. The gap line's number equals the next row's `right` minus yours, plus 1.

#### U12. Activity rows that show their effect and follow up

*From: the recent-activity gaps (outcomes, unfair-advantage). Effort S. Builders: S1 (feed `effect`), F5 (the `again` and `from_session` fields already exist).*

* Each finished sitting row in `/api/me/feed` adds
  `effect: {words: [{topic, from, to}], fixed, opened, pts}`.
  * Words are `UI.masteryWord` before the sitting started and after it finished, over the
    topics it touched.
  * `pts` is the change in U4's `S`, shown only when |pts| ≥ 5.
  * The row reads "Circles: Learning → Getting there · 2 mistakes fixed · 1 opened ·
    ≈ +4 pts".
* Two actions on each row:
  * **Again · new numbers**: `{again: sid}`.
  * **Follow up · 3**: `{from_session: sid, still_open: true, scope: 'misses'}`. It is hidden
    when nothing is still open.

**Acceptance.** A practice set that moved circles from 0.35 to 0.45 shows the row "Circles:
Learning → Getting there". Its Follow up posts a drill whose questions are the set's
still-open templates with fresh seeds.

#### U13. Every number says how it is worked out and what moves it

*From: outcomes #11, the experience "?" help popovers, the unfair-advantage achievements "Go". Effort S–M. Builder: S1 (`levers` in the summary, `web/help/answers.json`), F1 (`UI.pop` exists), F2 (Today card and nav tooltips).*

**Why.** A goal feels reachable when the gap is small and stated. A student who knows exactly
what moves a bar stops grinding random questions. Theirs: Global Rank 128 with no basis, and
"LOW CONFIDENCE" with no reason.

* **What opens one.** Every stat on Me, every Today card figure, the streak flame and each
  mastery bar is a button. Enter, a tap or a click opens a `UI.pop` with three parts:
  1. **How it's worked out**: one line, plus "More in Help".
  2. **Your numbers**: the inputs, e.g. "last 10 Circles answers: 7 right, 3 of them hard".
  3. **What moves it**: the next threshold, computed on the server, with **Start** when there
     is something to start.
* **What moves it**, per number:
  * **Mastery**: "2 more right on medium or hard reaches Strong". Found by appending right
    answers at the current tier to `mastery_of`'s window until `masteryWord` changes (pure,
    cheap).
  * **Streak**: "Answer 1 today to make it 7", or "Today is a rest day in your plan: your
    streak is safe", or "1 spare banked" (U16).
  * **Readiness**: "4 unmet Circles types are 3% of the test · Practise unmet".
  * **Rank**: "12 more right this week passes #127".
  * **Band**: "A module with 2 more right than your last moves the band about +30" (the last
    module re-scored with 2 more right at its own difficulty mix).
  * **Points on the table**: its top skill, with Start.
  * **Study time**: "25 min meets today's goal".
* **"?" buttons** (`UI.help(id)`) beside the band, the streak, the open-mistake dot, the rank
  and every preference row open that Help answer in a popover.
  * `web/help/answers.json` (S1) is built from the same content as `/help/`.
* **Achievements Go.** Every badge in progress, on the card and in View all, gets
  **Go · {action}**, which starts the drill that advances it:
  * a skill badge → Practise that skill;
  * Explorer → Practise unmet n;
  * Fixed → Fix all;
  * Clean set → a 10-question set at the current tier;
  * Hard right → a hard set;
  * a streak badge → a quick question.
  * `/api/me/achievements` adds `go: {label, body | href}`.
* **Data.** `/api/me/summary.levers: {key: {how, help, inputs: [...], next, start?}}`.

**Acceptance.**
1. A learner at circles mastery 0.7 with 12 answers: `levers['skill:circles'].next` matches
   `^\d+ more right`. Applying that many right answers (at medium) through
   `progress.mastery_of` reaches ≥ 0.8.
2. Every tile on /me/ is focusable and opens a popover on Enter. Esc closes it and returns
   focus.
3. `/api/me/achievements` rows with `have < next` all carry `go`.

#### U14. Your week: a Monday review and up to three goals

*From: outcomes #9, unfair-advantage #10, the experience goal-history gap. Effort M. Builders: S1 (the sheet, the endpoints, `api_profile.py`), F4 (the `week_goals` table), F2 (the Today card pips and the sheet trigger), S1 (the R25 ladder).*

**Why.** Specific short-term goals, tracked, reliably increase follow-through. The review
shows which effort actually moved skills. Theirs has only long-range numbers (2 hours a day,
12 hours a week), and no review.

**The sheet.** On the first shell page load of the student's week (`prefs.week_start`, local
day) a sheet opens, titled "Your week, Sep 14–20". It can be dismissed, and reopened from
Me › This week.
* **Last week**, as receipts:
  * questions answered, and first-try accuracy with its change;
  * minutes against the plan;
  * mistakes fixed, and new ones by name;
  * check-ins passed and relapsed;
  * skills that moved up a word ("Circles: Getting there → Strong");
  * the habit that fell most (U6);
  * the estimate change, if scored.
* **This week**: 5 suggestions built from the data. The student picks up to 3, each with a why
  and "about N min". Kinds:
  * `fix_traps {topic, n}`: "Fix the 4 open Circles mistakes (≈ 12 pts)";
  * `pass_checks {n}`: "Pass all 6 check-ins due this week";
  * `reach_word {topic, word}`: "Get Probability to Getting there (about 25 more answers)";
  * `take_module {day}`: "Take a module on Saturday";
  * `habit_cap {habit, max}`: "Keep answered-a-different-quantity to 2 misses or fewer";
  * `minutes {n}`.
  A custom goal uses the same kinds with a number.
* **Start the first** (pill) runs the first goal's drill.

**Where goals show.**
* The sidebar Today card: "Week goals 1 / 3", with pips.
* A "This week" card at the top of Me's right column, with a history: "Met 4 of the last 6
  weeks", six mini bars, and the best week named.
* The share view.
* An inbox item when a goal completes.
* The R25 ladder "Every goal met": 1 / 4 / 12 weeks.

**Data.**
* `week_goals(learner, week, id, kind, params JSON, target INTEGER, created, done_at)`,
  PK (learner, week, id).
* Progress is computed on the server from attempts, traps and sessions.
* Endpoints:
  * `GET /api/me/week?week=` → `{receipts, suggestions, goals}`;
  * `PUT /api/me/week/goals {week, goals: [...]}` (at most 3);
  * `/api/shell.goals: [{title, have, target, done}]`.

**Acceptance.**
1. `PUT /api/me/week/goals {week, goals:[{kind:'fix_traps', params:{topic:'circles'}, target:4}]}`
   → `/api/shell.goals[0] == {…, have:0, target:4, done:false}`.
2. Closing 4 circles traps → `done: true`, and the feed has a goal item.
3. A 4th goal → 422.
4. The sheet opens once per week per device, and never on `/practice/session/` or `/test/`.

### C. Practice habits

#### U15. Modes that follow the exam date: from learning to test conditions, on time

*From: outcomes #8, the experience "modes" gap, the unfair-advantage "presets" gap. Effort S. Builders: F4 (`prefs.py` keys, the stage and resolution), S7 (plan phase in `shell_part`), S1 (UI), F2 (the banner).*

**Why.** Instant feedback speeds early learning. Timed practice with delayed feedback in the
final weeks builds the pacing and unaided retrieval the test demands. Most self-studiers never
make the switch. Theirs are static selects.

**Modes** (a new pref `mode`: learn | build | test | custom; default learn) set a bundle:

| key | Learn | Build | Test-like |
|---|---|---|---|
| clock | off | pace | pace |
| feedback | instant | instant | end |
| repairs | next | next | end |
| rationale | miss | miss | tap |
| adaptive | true | true | false (all tiers) |

**Stage** (a new pref `stage_auto`, default true; it only acts with an exam date).
`prefs.stage(learner)` returns `{name, since, days_to_exam, next: {name, on}}`:
* It uses the active plan's phase for today (`plan_days.phase`, through S7's shell part) when
  there is one.
* Otherwise it goes by days to the exam: > 42 Learn; 42–22 Build; 21–8 Test-like; ≤ 7 Final
  week (= Test-like, plus U1's final-week rules).

**Resolution** for every key the bundle sets:
1. Yours: the key is stored because the student set it.
2. Otherwise the stage's bundle, when `stage_auto` is on.
3. Otherwise the chosen `mode`'s bundle.
4. Otherwise the default.

Under a mode or stage, a key the student changes is stored even when it equals the default.
`PUT /api/me {prefs: {key: null}}` deletes it ("Back to stage").

`GET /api/me` and `/api/shell` return `prefs`, plus `pref_source: {key: 'yours'|'stage'|'mode'|'default'}`
and `stage`.

**UI.**
* **Learning preferences (§3.4) and Settings › Practice (§4.1)** get a top row: "Mode: Learn ·
  Build · Test-like · Custom" (seg), and a switch, "Follow my exam date".
  * Helper: "Build · 34 days to Nov 7 · Test-like starts Oct 17."
  * Each row the mode sets carries a caption, "Set by Build", with **Change**. After a change
    it reads "Yours · Back to Build".
  * Picking a mode shows a one-line preview: "Your next set: 10 questions · SAT pace 16 min ·
    key after each".
* **Banner** (§2.11), on the first shell load of the day a stage changes: "Test-like starts
  today: sets run at SAT pace with the key at the end." [Why?] → `/help/#stages` · [Keep my
  settings] (turns `stage_auto` off).

**Acceptance.**
1. A learner with `exam_date` = today + 30 and no stored prefs: `GET /api/me` has
   `prefs.clock == 'pace'`, `pref_source.clock == 'stage'` and `stage.name == 'build'`.
2. `PUT {prefs:{clock:'off'}}` → `pref_source.clock == 'yours'`. `PUT {prefs:{clock:null}}`
   → back to `'stage'`.
3. With `exam_date` = today + 10 → `prefs.feedback == 'end'`.
4. `PUT {prefs:{mode:'x'}}` → 422 naming `mode`.

#### U16. Spare days: a streak one sick day can't break

*From: experience #8. Effort S. Builders: F4 (`progress.days`), F2 (tooltip and inbox item), S1 (heatmap and tile copy), F1 (heatmap ring).*

**Why.** Any missed day breaks theirs, and theirs disagrees with itself (0 against 1). Loss
of a long streak is a common reason to stop. Ours are earned by studying and cost nothing.

* **Rule** (in `progress.days`, R13's one function):
  * Every 7 study days in a row bank 1 spare, up to 2.
  * A missed day that is not a planned rest day spends a banked spare automatically.
  * The spent day neither breaks nor extends the streak (like a rest day) and is marked
    `spare_used`.
  * `best_streak` counts through spares.
* **Shown**:
  * the flame tooltip and the Today card header: "6 days · 1 spare", plus one small outlined
    flame per spare (an icon, not colour alone);
  * the streak tile's sub-line: "best 19 · 1 spare banked";
  * the heatmap: a hollow ring on a spare day, with the tooltip "Tue, Sep 22 · spare day used ·
    streak kept";
  * an inbox item the morning after: "Yesterday used a spare day. Streak 12 kept." [See];
  * Help: `#spare`.
* **Data.** `days()` returns `spares` and `per-day spare_used`. The achievements streak rule
  reads the same function.

**Acceptance.** A learner who answers on 7 consecutive study days, misses day 8 (a study day)
and answers on day 9: `/api/shell.streak == 8`, `spares == 0`, and day 8 has
`spare_used: true`. With the day-8 miss before any 7-day run, the streak breaks.

#### U17. Exam dates with registration deadlines

*From: the experience and unfair-advantage exam-date gaps. Effort S. Builders: F4 (`satdates.py` deadlines, pref `registered`), F1 (`UI.examDate`), F2 (the banner), S7 (deadline events in the calendar feed).*

**Why.** Missing registration is the plainest way to miss the test altogether, and no
competitor tracks it.

* **Data.**
  * `satdates.py` entries gain `register_by`, `late_by` and `scores_by`, each marked "verify
    against College Board" with a `checked` date.
  * A new pref, `registered` (YYYY-MM-DD or null).
* **Chips** in every exam-date picker (`UI.examDate`): "Nov 7 · in 45 days · register by Oct 23
  · late Oct 27".
* **Banner** (§2.11), shown from 7 days before `register_by` until `late_by`, while
  `registered != exam_date`:
  * "Register for Nov 7 by Oct 23 · 5 days left";
  * [I've registered], [Register at College Board ↗], [Add deadline to calendar] (`UI.ics(event)`).
  * The Today card shows the same line.
* **Calendar feed** (S7): deadline events and the scores-release day.

**Acceptance.**
1. With `exam_date` = a date whose `register_by` is 5 days away and `registered` null, the
   banner text contains "5 days left".
2. `PUT {prefs:{registered: exam_date}}` hides it.
3. The `.ics` feed contains a `SUMMARY` starting "Register for".

#### U18. Reminders that say what is due

*From: outcomes #12, unfair-advantage #12. Effort S for (a), L for (b). Builders: S7 (the feed), F2 (`?next=1`, `web/sw.js`), S1 (`server/push.py`, the Settings row).*

**Why.** Spacing only works if the due day is met. A specific, small, time-stated nudge ("about
4 min") beats a generic alarm. Their "Preferred time: Evening" does nothing.

**(a) Calendar, ships first.**
* Each study-day event in the subscribed feed (R18b, `plan.py`) is titled from the plan and
  the check-ins due that day: "SAT Math · 3 check-ins + Circles · 25 min".
* Its DESCRIPTION lists the items and the link `{BASE_URL}/?next=1` (U1).
* Future days use the plan's forecast and `traps.due`.

**(b) Push, on the installed app, after the core waves.** It is hidden unless
`SATF_VAPID_PUBLIC` and `SATF_VAPID_PRIVATE` are set.
* **Settings**: Settings › Study gets "Notify me on this device" (on iOS it needs the
  home-screen app). Kinds, each a switch:
  * study reminders (on);
  * "one question keeps your streak" at 20:30 on an unfinished study day (off);
  * class assignments (on).
  Quiet hours are 21:30–7:00.
* **Service worker**: `web/sw.js` handles `push` and `notificationclick` only, with no fetch
  handler and no caching.
* **Payload-less pushes**. The worker calls `POST /api/push/next {endpoint}` for the text
  ("3 check-ins due · about 4 min"). A tap opens `/?next=1`.
* **VAPID**: an ES256 JWT signed with `cryptography`, so no new dependency.
* **Scheduler**: an in-process asyncio loop every 5 minutes sends at `study_time − remind` on
  study days not yet done. At most one per kind a day, and every notification carries a Stop
  action.
* **Table**: `push_subs(id PK, learner, endpoint UNIQUE, p256dh, auth, kinds JSON, created,
  last_sent)`. `progress.carry`, export and delete cover it.

**Acceptance.**
1. (a) For a learner with 3 check-ins due tomorrow, tomorrow's VEVENT SUMMARY contains
   "3 check-ins", and its DESCRIPTION contains "/?next=1".
2. (b) With the VAPID env unset, `/api/push/*` → 404, and Settings shows no row.
3. (b) With it set, a subscription row is created, and `POST /api/push/next` returns text
   naming the first Up next item.

### D. Identity and account

#### U19. Passkeys: save and sign in with one tap, with no email, no password and no SMTP

*From: experience #1, unfair-advantage #5, the sign-in gaps of all three, the experience "remembered email" gap. Effort M. Builders: S1 (`account.py`, `/signin/`, Settings), F4 (tables), F2 (the menu callout and save nudge).*

**Why.** Coming back on a new device with v2's email code takes about 7 steps across two apps,
and does not work at all without SMTP. Google (theirs) takes 2–3 taps and needs a Google
account, which many school accounts block. A passkey takes 2 taps: the autofill row, then the
biometric.

* **Saving** (Settings › Account & devices, the 50-answer nudge, the menu callout).
  * **Save with a passkey** comes first when
    `PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()` is true. The nudge
    reads "Save with Face ID" (the OS sheet names the method).
  * It calls `navigator.credentials.create` with:
    * `rp.id` = the host of `SATF_BASE_URL`;
    * `user.id` = 16 random bytes stored per learner;
    * `user.name` = the board handle or name;
    * `residentKey: 'required'`, `userVerification: 'preferred'`, algorithms −7 and −257.
  * The client posts `response.getPublicKey()` (SPKI DER, so no CBOR parsing),
    `getPublicKeyAlgorithm()`, `getAuthenticatorData()`, `clientDataJSON` and the transports.
  * Toast: "Saved. This passkey signs you in wherever your passwords sync."
  * The email code stays as the quiet alternative.
* **Signing in.**
  * `/signin/` opens on a **Passkey** tab.
  * Its field has `autocomplete="username webauthn"`, so saved passkeys appear in the
    browser's autofill (conditional mediation). A **Sign in with a passkey** button calls
    `get()` with no `allowCredentials`.
  * A school Chromebook with no synced passkey gets the browser's own "Use a phone" QR, at no
    cost to us.
  * On a device not marked shared, the email tab remembers the last address (masked in
    `localStorage satf.lastEmail`): **Send a code to d•••@gmail.com**, in 1 tap.
* **Server** (S1 `account.py`):
  * `POST /api/passkey/register/options`, then `POST /api/passkey/register`.
  * `POST /api/passkey/login/options`, then `POST /api/passkey/login`.
  * Verification, in order:
    1. a single-use challenge (5 min, stored server-side);
    2. `clientDataJSON.type` and `origin == SATF_BASE_URL`'s origin;
    3. `authData[0:32] == sha256(rp_id)`, and the UP flag set;
    4. the signature over `authData ‖ sha256(clientDataJSON)`, with ECDSA-SHA256 (a DER
       signature) or RSA-PKCS1v15-SHA256, using `cryptography`;
    5. `sign_count` stored, and a non-increasing count only logged (synced passkeys send 0).
  * Login then runs the existing carry and adopt path, returning a device token (U21):
    "Signed in as Dana · 24 answers moved here".
* **Managing.**
  * Settings lists each passkey: "iCloud Keychain · created Sep 23 · last used today"
    [Remove].
  * Removing the last way to sign in asks for a confirm.
  * The recovery line reads "You can sign in 2 ways: passkey, email". With one way only, it
    shows an orange dot and "Add a passkey or email".
* **Counts as saved.** A passkey counts as "saved" everywhere a verified email does, including
  creating a class (R4 becomes "saved: a passkey or a verified email").
* **Tables** (F4):
  * `passkeys(cred_id PK, learner, user_handle, spki BLOB, alg INTEGER, sign_count INTEGER, label, created, last_used)`;
  * `webauthn_challenges(challenge PK, learner, purpose, expires)`.
  * `carry`, `rotate`, export (without keys) and delete cover passkeys.
* **Deploy.** `cryptography` must be on the production host. The README's run section lists
  it, since the repo has no requirements file.

**Acceptance.**
1. `server/checks/s1.py` registers a credential made with `cryptography`'s P-256 key, using a
   hand-built `authData` and `clientDataJSON`, then logs in with a valid signature →
   `{learner}`.
2. The same login with a wrong origin → 400, a reused challenge → 400, and a bad signature
   → 401.
3. After registering, `GET /api/account` shows `saved: true` without an email, and
   `POST /api/classes` succeeds.
4. The `/signin/` field has `autocomplete` containing `webauthn`.

#### U20. Sign in a shared computer without typing on it: it shows a code, your phone approves

*From: experience #6. Replaces v2's four-step pairing. Effort M. Builders: S1 (`account.py`, the `/link/` page), F4 (pairs columns), F2 (the menu item "Sign in another device").*

**Why.** On a library or school computer, theirs means typing a Google email, password and 2FA
code on a shared machine. v2's pairing takes 4 steps across two devices, plus typing on the new
one. Here it is 2 taps on the phone, and nothing typed on the shared computer.

* **New device.** `/signin/` tab **Use your phone**.
  * It sends `POST /api/link/request {device (≤ 40), session_only}` → `{token (32 chars), code (6 digits), expires}`.
  * It shows:
    * a 180px QR of `/link/?r=<token>`;
    * the same request as 6 digits ("482 913", DM Mono 32);
    * "Expires in 4:59";
    * its own label ("Chrome on Windows");
    * the checkbox "This is a shared computer" (U21).
  * It polls `GET /api/link/{token}` every 2 s.
* **Phone.** Either:
  * scan with the camera (opens `/link/?r=`); or
  * Menu › **Sign in another device** and type the 6 digits (`POST /api/link/code {code}`
    → the request).
  * It reads: "Sign in **Chrome on Windows** as Dana? It asked 20 s ago. Only do this for a
    screen in front of you." [Sign in] [Not me] → `POST /api/link/{token}/approve | /deny`.
  * If the phone's browser has no learner (on iOS the camera opens Safari, whose storage is
    separate from the home-screen app): "Open SAT Freshman on your phone, then Menu › Sign in
    another device, and type 482 913."
* **Finish.**
  * On approval, the computer's poll gets a device token (U21). It carries in its own answers
    (`progress.carry(new, owner)`), adopts, and toasts "Signed in as Dana".
  * On Not me: "Your phone said no."
* **Security.**
  * Tokens are single use, 10 minutes. The request carries no name until it is approved.
  * A guessed code does nothing without the owner's tap on their own screen.
  * Per-IP limits stay as specified (10 failed lookups per 10 minutes → 429).
  * The approved device appears in the devices list, and can be signed out there.
* **Schema** (F4): `pairs` gains `dir ('pull')`, `token UNIQUE`, `approver`, `session_only`.
  The old `/api/pair*` endpoints are not built. `/pair/?c=` redirects to
  `/signin/?c=…#phone`.

**Acceptance.**
1. As B: `POST /api/link/request` → `{token, code}`. As A: `POST /api/link/code {code}` → the
   request, with B's label and no name.
2. A approves. B's `GET /api/link/{token}` → `{credential}` starting `d:`, and B's attempts
   now carry A's learner. A second approve → 410.
3. Deny → B reads `{state:'denied'}`.
4. 11 wrong codes from one IP within 10 minutes → 429.

#### U21. Devices you can see and sign out; a shared-computer mode; switch student

*From: experience #9, the unfair-advantage devices and switch-student gaps, the outcomes switch-student gap, the experience sign-out gap. Effort M. Builders: F4 (the `devices` table, `learner_of` in `deps.py`), S1 (every sign-in flow mints tokens, the Settings UI), F2 (`UI.learner`, sessionStorage mode, the menu).*

**Why.** v2 can only rotate the one shared code, which signs out every device at once, and it
treats a copyable code as the credential. A session left on a library computer stays signed
in. Siblings on one laptop mix answers into one code, which corrupts mastery, mistakes and the
coach's picks.

**Device tokens.**
* Every sign-in (passkey, phone approval, email code, device code) gives that browser its own
  token, `d:` + 32 base-36 characters, never the learner code. The first anonymous device keeps
  its `a:` code.
* `deps.learner_of` resolves `a:` as today, and `d:` through
  `devices(token PK, learner, label, method, created, last_seen, session_only, expires, revoked)`,
  indexed on learner.
  * It is one primary-key lookup. `last_seen` is written at most every 10 minutes.
  * A revoked or expired token → 401 `{retired: true}` (the existing banner).
* A `d:` device never receives the `a:` code. Its Device code row reads "This device signs in
  with its own key."

**Settings › Account & devices › Devices.**
* One row per device:
  * "Chrome on Mac · this device · active now";
  * "Safari on iPhone · 2h ago · signed in Sep 21 by passkey";
  * "Chrome on Windows · shared computer · expires in 11h".
  Each row has [Sign out].
* **Sign out all other devices** revokes every other token. When the `a:` code is held
  elsewhere, it also rotates it (the existing rotate), so every other device is out.

**Shared computer.**
* A checkbox on every `/signin/` tab. The token lives only in sessionStorage and expires 12 h
  after last use.
* The user card's second line reads "Shared computer · Sign out".
* Closing the browser ends it.
* Switch student and the remembered email are hidden.

**Sign out, saved account.** There is no dialog. An 8 s toast reads "Signed out · Undo". The
credential is held in memory until the toast closes; only then is `DELETE /api/devices/this`
sent (for a `d:` token). Unsaved devices keep the warning dialog.

**Students on this device** (an account-menu section and a menu-sheet group; hidden on shared
computers).
* Up to 4 learners in `localStorage satf.profiles [{cred, name, avatar}]`, each with its
  avatar and name.
* One tap → `UI.useLearner(cred)` and a reload, with the toast "Now Maya".
* **Add a student** keeps the current one in the list and mints a fresh anonymous code.
* **Remove from this device**. When that student is unsaved it warns: "Maya's progress isn't
  saved. Removing forgets it on this device."

**Acceptance.**
1. A passkey or email sign-in returns a `d:` token. `GET /api/devices` as the owner lists it.
   `DELETE /api/devices/{id}` → that token's next PUT gets 401 with `detail.retired == true`.
2. A `session_only` token unused for 12 h → 401. A test sets `last_seen` back.
3. No response to a `d:` device contains the learner's `a:` code (a check greps every
   endpoint body in `server/checks/s1.py`).
4. Two profiles in `satf.profiles`: switching changes `X-Learner` on the next `/api/shell`
   call.

#### U22. The living mark avatar, and glyphs you earn

*From: unfair-advantage #11, the outcomes and experience avatar gaps. Effort S. Builders: F1 (`UI.avatar`), F2 (`/api/shell.me.domains`), S1 (the picker), S8 (boards respect visibility).*

**Why.** Their photo upload is a privacy risk for minors. Our 19-glyph picker says nothing
true about the student. Ours stays photo-free and shows progress at a glance.

* **The default avatar is the living mark.**
  * The mark's four rounded quadrants are the four domains: Algebra top-left, Advanced Math
    top-right, Problem-Solving and Data Analysis bottom-left, Geometry and Trigonometry
    bottom-right.
  * Each fills orange from the centre outward in proportion to that domain's mastery: 0 is a
    `--mat` outline, Strong is solid.
  * Its aria-label and tooltip read "Algebra Strong · Advanced Math Learning · …".
  * It shows on the user card, the menu, the identity card (72px, with a small legend), class
    rosters (a roster of marks reads as a heat map) and the share view.
  * Boards show the plain mark for `anon` and `hidden` students.
* **Earned glyphs.**
  * A skill's glyph unlocks as an avatar when that skill's badge is earned (mastery ≥ STRONG).
  * A domain ring unlocks when every skill in the domain is Strong.
  * Locked tiles read "Reach Strong in Circles · 62%", with a bar. The initial is always
    available.
  * `PUT /api/me {avatar}` refuses a locked glyph (422).
* **Subject-aware.** `me.domains` is keyed by subject. With a second subject, the mark reads
  the subject in focus.

**Acceptance.**
1. `/api/shell.me.domains` has 4 numbers from 0 to 1.
2. `PUT {avatar:'circles'}` for a learner without the circles badge → 422. After the badge is
   earned → 200.
3. The avatar SVG's aria-label names all four domains.

### E. Speed and reach

#### U23. Pages that are ready when you click: prerender and paint from cache

*From: experience #3. Effort S. Builder: F2 (`head.js`, `UI.api`, `UI.cached`).*

**Why.** Theirs is a React SPA whose routes mount first and fetch afterwards, so sections open
on skeletons. A study platform is used in many short visits, and every one should feel
instant.

* **Speculation rules.** `head.js` inserts one `<script type="speculationrules">`:
  * it prerenders same-origin links at `moderate` eagerness (hover or pointerdown);
  * it excludes `/practice/session/*`, `/test/*`, `/signin/*`, `/link/*`, `/admin/*`,
    `/api/*`, and any link marked `data-noprerender`.
* **Paint from cache.** `UI.cached(path)`:
  * paints the last `sessionStorage satf.c.<path>` copy of a page's main GET at once;
  * revalidates, and re-renders only if the JSON's hash changed;
  * caps each page's copy at 200 KB, and clears all copies on sign-out or a learner change.
* **Safe prerendering.** While `document.prerendering` is true, `UI.api` sends GETs only. Any
  other method waits for `prerenderingchange`. That one guard in `UI.api` covers every page.
* **Warming.** The first sidebar hover in a session fetches `/api/types`, for the palette.

**Acceptance.**
1. Chrome at 1280: after a 200 ms hover, clicking a nav item paints a real card (not a
   `.skel`) within 100 ms of `performance.getEntriesByType('navigation')[0].activationStart`.
2. Safari and Firefox, on a second visit: cached content is painted within 50 ms of
   DOMContentLoaded.
3. A prerendered `/me/` sends no POST before activation (checked through the network log).

#### U24. Change anything by typing it; Help in the palette; one prefs registry

*From: experience #7, the experience Help gap, outcomes #7's parsing. Effort S. Builders: F4 (`prefs.py` labels and synonyms, `GET /api/prefs`), F2 (the palette), S1 (`answers.json`), S7 (`plan.pace` for the preview).*

**Why.** Changing the target on theirs takes the Dashboard, a pencil, typing and Save, and the
new target never reaches the profile. Here it is ⌘K, type, Enter, from any page, with the pace
shown before committing and Undo after.

* **Commands.** A composed first row shows the current value and the new one:
  * "target 700" → "Target: 650 → 700 · about 22 points a week · Ambitious";
  * "exam dec 5" → "Exam: Nov 7 → Sat, Dec 5 · in 73 days · register by Nov 19";
  * also "timer off", "clock pace", "set 22", "hard", "adaptive", "grid", "explanations
    always", "mode test", "dark", "text large", "keys off", "week sunday".
* **Settings by name.** Every key in the registry is searchable by its label and synonyms
  ("calculator", "stopwatch", "font size") and shows its current value. Enter flips a switch
  or opens that setting's seg inside the row; the arrows pick.
* **Time box.** "15 min", "15m" and "half hour" compose "Up next for 15 minutes" (U1).
* **Actions**: sign out, save progress, sign in another device, copy progress link, download
  my data, report a bug.
* **Help group.** The palette searches `answers.json`. A row shows the question and the
  answer's first line; Enter opens `/help/#anchor`.
* **Applying.** `PUT /api/me`, the palette closes, and a toast confirms: "Target 700 · Undo".
  Undo sends the old value.
* **One list.** `GET /api/prefs` (public, cached per deploy) →
  `[{key, label, group, values: [{v, label}], helper, synonyms}]`. Settings, Me's inline
  preferences and the palette all render from it.

**Acceptance.**
1. ⌘K, type "target 700", Enter → `PUT /api/me {target:700}`. The toast has Undo; Undo sends
   the previous target.
2. "calculator" lists `calc_button` with its current value.
3. `GET /api/prefs` contains every key of §2.7, each with a label.
4. "why band" lists the Help answer on bands.

#### U25. An inbox, a welcome-back sheet, and Undo everywhere

*From: the experience toasts gap, the unfair-advantage Undo gap. Effort S. Builders: F2 (the menu inbox and the sheet), S1 (feed unread and seen), F4 (the `learners.feed_seen` column).*

**Why.** In both products a missed toast is gone for good. Achievements, replies, corrections
and new assignments matter enough to keep.

* **Inbox.** The top of the account menu (and of the menu sheet) holds "Since you were last
  here · 3": up to 20 items from `GET /api/me/feed?unread=1`.
  * Kinds: achievements, report replies and checks, corrections (U3), new assignments, spare
    days used (U16), week goals met (U14), stage changes (U15).
  * Unread dots, plus a count on the user card and the phone avatar.
  * Opening marks them read (`POST /api/me/feed/seen` → `learners.feed_seen = now`).
* **Welcome back.** After 2 or more days with no activity, the first shell page opens a sheet
  once:
  * what is waiting: check-ins due, assignments due, the streak and any spare;
  * the pill **Pick up: {Up next title}**.
* **Undo on every reversible toast**, for 6 s:
  * unsave, unmark, leave class, skip a plan task (S7), turn off a progress link, target or
    exam change, a palette command, sign out (8 s, U21).
  * Undo calls the inverse endpoint. `UI.toast(text, {undo})` already exists in kit.

**Acceptance.**
1. A new achievement shows in `GET /api/me/feed?unread=1`. After `POST /api/me/feed/seen` it
   does not.
2. A learner whose last attempt is 3 days old sees the welcome-back sheet once. A reload does
   not show it again.
3. Unsave → Undo → `GET /api/saved` contains the question again.

#### U26. Chrome that fits long pages and thumbs

*From: the unfair-advantage sub-links gap, the experience rail-peek gap, the experience profile-length gap, experience #10, the experience menu-toggles gap. Effort M. Builders: F2 (shell), S1 (Me chips and collapse), F1 (CSS).*

* **Page sections in the nav** (desktop).
  * A page with sections registers them: `UI.shell({sections: [{id, label}]})`. This covers
    Me, Settings, Help and Results.
  * The active nav item expands into indented sub-links (32px rows, 13.5px). An
    IntersectionObserver highlights the one in view.
  * On the rail, the sub-links appear in the item's tooltip menu.
* **Rail peek.** Resting the pointer on the rail for 400 ms, or holding `[` for 300 ms, opens
  the full sidebar as an overlay without changing `satf.rail`. It closes when the pointer
  leaves or the key is released. Tapping `[` still collapses.
* **Me on the phone.**
  * A sticky chip row under the identity card (Week · Goals · Skills · Pace · Trend · Habits ·
    Badges · Activity · Account) highlights the card in view.
  * Every card header has a collapse chevron that leaves a one-line summary ("Skills · weakest
    Probability 41%"). The state is kept in `localStorage satf.me.collapsed`.
* **Thumb-first phone chrome.** The top bar and the 5 tabs stay as specified (R1).
  * The tab bar gets a 24px grip. Swiping up on the tab bar, or tapping the grip, opens the
    menu sheet.
  * The menu sheet puts Up next first, and the four daily rows (Review, Words, Compete,
    Quick) in its bottom half, near the thumb.
  * Holding a tab for 450 ms (cancelled by 8px of movement; `-webkit-touch-callout: none`)
    opens a shortcut menu anchored above it:
    * Today: Up next, Question of the day, Daily challenge · New;
    * Practice: Quick question, Log a mistake, Review · 14, Saved · 3, Words · 12 due;
    * Tests: Resume module · 12/22, New module, Full section, Diagnostic;
    * Plan: today's tasks;
    * Results: Latest report, Skills.
    Every item is also in the menu sheet, for keyboard and screen-reader users.
  * A first-visit hint above the tabs, "Hold a tab for shortcuts", goes after the first hold
    or a tap on ×.
  * The palette's input is pinned just above the keyboard (`visualViewport`). Results stay in
    top-down order.
  * The quick sheet puts Check and Another in a 56px bottom action bar.
* **Menu toggles.** The account menu header carries Theme (Light · Dark) and text size (A · A+)
  toggles, writing the same prefs.

**Acceptance.**
1. At 1280 on /me/, the Profile item has sub-links. Scrolling to Skills sets `aria-current` on
   the Skills sub-link.
2. At 390, a swipe-up on the tab bar opens the menu sheet, and holding Practice for 500 ms
   lists "Log a mistake".
3. Collapsing Skills on /me/ survives a reload.
4. At 390, `scrollWidth <= 390` on /me/ with every card collapsed and expanded.

### F. Classes and sharing

#### U27. Classes: Tailored questions and "Reach a level" homework

*From: the outcomes classes gap (Tailored), unfair-advantage #7 (mastery homework). Effort M. Builders: S2 (`classes.py`, the class pages), F5 (drill fields `segments` and `until`).*

**Why.** Their homework is a fixed test or session: every student gets the same questions, and
"done" means submitted, however many were wrong. A finite bank cannot give a struggling
student 30 more fresh questions on one skill while a strong one stops after 8.

**New assignment sheet (§7.2).**
* **What** gains **Reach a level**, with:
  * skills or question types (found by search);
  * a target: Getting there | Strong;
  * a cap: 20–80 questions (default 40);
  * a due date.
  Each student gets fresh adaptive questions (R33) until every chosen skill reaches the target
  and no trap is open on those templates, or until the cap.
* **Questions** gains **Tailored** (sets only), with the helper "Each student's set starts with
  their own open mistakes on these skills, then their check-ins due, then types they haven't
  met. Same count and due date for everyone."

**Student row.** "Circles → Strong · 2 of 3 skills there · ~12 more questions", with Resume.

**Teacher detail.**
* Per student:
  * "Done in 14 q · 11 min";
  * or "Stuck: 40 q, still Learning, 2 open: Used the diameter as the radius", with
    [Assign a repair];
  * for Tailored: "had 3 of their own mistakes · fixed 2".
* A histogram of the questions each student needed.
* The roster adds "questions to Strong" per student.

**Data.**
* `assignments.kind` adds `mastery`, with `cfg {topics | templates, level, cap}`.
* `cfg.tailored = true` for sets.
* F5 adds `until: {mastery: 0.4 | 0.8, cap}` (the session ends when every topic in `topics`
  reaches it, or at `cap`).
* F5 also adds `segments` (U1's field): Tailored uses
  `[{pool:'redo', topics}, {pool:'checks', topics}, {pool:'untried', topics}, {pool:'new', topics}]`,
  filled in order up to `count`.

**Acceptance.**
1. A mastery assignment (circles, Strong, cap 30): a student at mastery 0.82 with no open
   circles traps sees Done after starting.
2. A student at 0.3 gets questions until 30, then sees "Stuck".
3. A Tailored 5-question set, for a student with 2 open circles traps, serves those 2
   templates first.
4. No teacher payload contains an email or an `a:` / `d:` code.

#### U28. Question links send a twin

*From: the unfair-advantage single-question gap. Effort S. Builders: F6 (`sets` `cfg.fresh`), S4 (the Share action in the session), F2 (`UI.share`).*

* **Send to a friend** (UI.share on any answered question) defaults to "Same kind of question,
  their own numbers":
  * `POST /api/sets {kind:'set', cfg:{templates:[t], count:1, fresh:true}, show_score:true}` →
    `/s/?c=CODE`;
  * the friend gets a fresh seed of the same template, so an answer can't be passed along;
  * the sender's results card (`GET /api/sets/{code}/results`) shows "You: right in 1:12 ·
    Sam: right in 0:58".
* **Exactly this question** (the `?q=` permalink) stays as the second option, for tutors.

**Acceptance.** Two learners open the same twin code and get the same template with different
seeds. The owner's results list both, with time and right.

---

## 3. Spec overrides

### 3.1 Inside §3.1 (spec/rebuild-v2.md lines 653–2294)

Each entry quotes the current text, then gives the replacement or addition.

1. **§3.1.3 Rules for this section.**
   * Quote: "* **One source per fact.** Streak, target, exam date, study time and the
     open-mistake count each come from one server function, and read the same on every
     screen."
   * Replace with: "* **One source per fact.** Streak (with spares), target, exam date, study
     time, the open-mistake count, **Up next (`next.queue`)**, **points on the table
     (`estimate.gains`)**, **pace (`progress.pace`)** and **readiness** each come from one
     server function, and read the same on every screen."
   * Add after it:
     * "* **Every number explains itself.** Every figure on Me and in the chrome opens how it
       is worked out, the student's numbers, and what moves it (U13)."
     * "* **Every end leads on.** Every screen that ends a session makes Up next its primary
       (U1)."

2. **§1, the identity table.** Replace these two rows:
   * Quote: "| **Saved** | the same code, plus a verified email bound to it (`users.learner`) |
     Save progress → the 6-digit code from the email, or the email's link |"
     → "| **Saved** | the same code, plus a passkey (`passkeys`) and/or a verified email
     (`users.learner`) | Save with a passkey (one tap), or the 6-digit code or link from the
     email |"
   * Quote: "| **Signed in elsewhere** | another device adopts the saved code | email code,
     pairing code (approved on the first device), or the device code. …"
     → "| **Signed in elsewhere** | another device holds its own device token (`d:`, U21),
     resolving to the saved learner | passkey (U19), phone approval (U20), email code, or the
     device code. This device's own answers are carried in first (`progress.carry`) |"

3. **§1 "Pairing (no email)."**
   * Quote: steps 1–4, from "1. Device A: "Show a pairing code"." through "* Deny → B reads
     "Your other device said no.""
   * Replace with: "**Phone approval (no email)**: U20. The new device shows a QR and 6 digits;
     the phone that holds the progress scans or types them and taps Sign in."

4. **§1 "Sign out of this device".**
   * Quote: "**Sign out of this device** clears `satf.learner` and the `satf.*` caches, keeping
     `satf.look` and `satf.rail`. It mints a fresh code, goes to `/` and shows the toast
     "Signed out"."
   * Append: "A saved account gets no dialog: the toast is "Signed out · Undo" (8 s), and a
     `d:` token is revoked when it closes (U21). Shared-computer sign-ins end when the browser
     closes, or 12 h after last use."

5. **§1 "Privacy for minors".**
   * Quote: "* No photo upload: the avatar is an initial or one of our 19 topic glyphs."
   * Replace with: "* No photo upload: the avatar is the living mark (U22), the initial, or a
     topic glyph earned at Strong."

6. **§2.2, sidebar.**
   * Quote: "3. **Quick** (40px, `--wash`, ink text): a bolt, "Quick", and the `kbd` "Q"."
   * Insert before it: "2a. **Up next** (U1): the UP NEXT block (title, meta, reason, Start
     with `G N`, and the › popover with 5 more and the time-box chips)."
   * On short viewports the block stays pinned with Search.

7. **§2.2 item 7, Today card.**
   * Quote: "* Header row: "TODAY" (k label), and on the right the flame icon and the streak
     ("6"). The flame is filled orange while the streak is above 0."
   * Append: "One small outlined flame per banked spare day (U16)."
   * After "* Bar 2: "12 of 28 questions"." add:
     * "* "Week goals 1 / 3" with pips, when goals are set (U14)."
     * "* "Register for Nov 7 · 5 days left", inside the deadline window (U17)."

8. **§2.3, rail.**
   * Quote: "* **Search, Quick, Help and Feedback** become icons with tooltips."
   * Append:
     * "Under Search, a 44px orange play button starts Up next item 1; its tooltip carries the
       title, the reason and `G N` (U1)."
     * "Resting the pointer on the rail for 400 ms, or holding `[`, peeks the full sidebar as
       an overlay (U26)."

9. **§2.4, phone.**
   * Quote: "**Bottom tabs** (64px + safe area, 5 equal columns, 22px icon, 10.5px label):"
   * Append to that paragraph: "A 24px grip; a swipe up on the bar opens the menu sheet; a
     450 ms hold on a tab opens its shortcuts; the Today tab's dot also means an urgent Up next
     item (U1, U26)."
   * Quote: "**Menu sheet**: a bottom sheet with a drag handle, max-height 85vh, 52px rows,
     grouped:" and its list 1–4.
   * Replace the list with:
     1. Up next item 1 with Start, and the time-box chips (U1).
     2. The Today card.
     3. "Since you were last here" (U25), when there is anything unread.
     4. The account header, Students on this device (U21), Settings, Save your progress (when
        unsaved), Sign in another device, Join or teach a class, Help & FAQ, Send feedback,
        Sign out (or Leave this device).
     5. At the bottom, at thumb height: Review (● 14), Words (12 due), Compete (New / #4),
        Class (2 due), Quick.

10. **§2.6, account menu.**
    * Quote: "1. **Header** (not focusable):"
    * Add to the header: "the Theme (Light · Dark) and A · A+ toggles (U26)."
    * Insert after the header: "1a. **Since you were last here · n** (U25), and **Students on
      this device** (U21, hidden on shared computers)."
    * Quote: "3. Profile (`G U`) · Settings (`G S`) … · Sign in (only when unsaved; →
      `/signin/`) · Pair a device · …"
    * Replace "Pair a device" with "Sign in another device (U20)".

11. **§2.7, quick sheet, Log a mistake.**
    * Quote: steps "1. **Which skill?**" through "5. **Add to my mistakes** (pill) sends POST
      `/api/mistakes/log`."
    * Replace with U2: one field (ID, paste or search); "Which answer did you pick?"; Where;
      Add, with the fix path in place; a "One question | A whole test" seg. The four-step
      picker stays behind "Pick by skill instead".
    * Quote: "**Quick question**"
    * Add under its header line: "A 'Got time? 5 · 15 · 30 min' chip row starts a time-boxed
      Up next set (U1)."

12. **§2.8, palette.**
    * Quote: "* **Suggested** (empty query only):" and its five bullets.
    * Replace with: "* **Suggested**: the first 5 Up next items (U1), each with its reason and
      minutes."
    * Add these groups after **Actions**:
      * "**Commands** (target, exam, every pref, mode, theme; U24)";
      * "**Settings** (every registry key by label and synonym)";
      * "**Help** (`answers.json`)".
    * Quote: "* Several skills combine: "circles percent 10"."
    * Add after it: "* "15 min", "15m" and "half hour" compose a time-boxed Up next."

13. **§2.9, keyboard.**
    * Quote: "* `G` then `T` Today, `P` Practice, `M` Mistakes, `E` Tests, `L` Plan, `R`
      Results, `C` Challenge, `K` Class, `U` Profile, `S` Settings, `H` Help."
    * Append: "`G` then `N` starts Up next item 1."

14. **§2.10, report.**
    * Quote: "* **Answer key is wrong** reveals two fields:" and its two bullets.
    * Replace with U3: "Which answer do you get?" as A–D chips or the grid-in field; the
      instant check with outcomes `remarked` / `forms` / `explained` / `broken` / `unsure`;
      That makes sense / Still wrong: send to a person. The "don't count it" checkbox and the
      5-dispute bound apply only to "send to a person".
    * Quote: "* **Images**: an "Add images" button, paste (⌘V) and drop."
    * Prefix with: "For a question report the box says "We have this exact question (…). No
      screenshot needed." and images sit behind "Add images"."
    * Quote: "Required for Bug and Other."
    * Append: "Typo or display and Figure or table wrong need no details."
    * Quote: "* A checkbox "Include device details" (on), with a **Show** disclosure listing
      exactly what is sent:"
    * Append to its list: "the last 10 actions on this page load (path, control, API path and
      status), from memory only."
    * Quote: "* **On success** the body becomes "Thanks. Report #123 is in. …""
    * Replace with: "On success the body shows the check's text (U3), or for other categories
      "Thanks. Report #123 is in. You'll see our answer under Settings › Your reports, and
      fixes are listed at Help › Fixed from your reports." Me too (U3) is added above the
      Summary."

15. **§2.11, banners.**
    * Quote: "4. **First visit**: 0 answers and not saved."
    * Insert before it:
      * "3a. **Registration deadline** (U17)."
      * "3b. **Stage change** (U15), on the day it happens."
    * Quote: "`UI.toast(text, {action, href, ms=4000})`:"
    * Add: "Every reversible action's toast carries Undo for 6 s (U25). Every toast that
      reports an event also lands in the inbox."

16. **§2.12, shell data.**
    * Quote: "GET `/api/shell` once per page load."
    * Add these keys to the shell response (§3.1.5):
      * `next` (3), `goals`, `inbox` (unread count), `stage`, `pref_source`;
      * `me.domains`, `spares`;
      * `registration {exam_date, register_by, late_by, registered}`.

17. **§2.14, install.**
    * Quote: "* No service worker: the API is the app, and there is nothing useful to serve
      offline."
    * Replace with: "* A notification-only service worker, `/sw.js` (`push` and
      `notificationclick`; no fetch handler, no caching), registered only when the server
      reports push is configured (U18). Nothing is served offline."

18. **§3, profile layout.**
    * Quote: "* **Left, 320px**: Identity, Snapshot, Saved & in progress, Account."
      → "* **Left, 320px**: Identity (with the outcome strip), Snapshot, Saved & in progress,
      Account."
    * Quote: "* **Right, fluid**: Goals, Learning preferences, Skills, Score trend, What keeps
      catching you, Achievements, Activity, Recent activity, Question types met."
      → "* **Right, fluid**: This week, Goals, Learning preferences, Skills, Test-day
      readiness, Score trend, Pace, What keeps catching you, Your habits, Achievements,
      Activity, Recent activity."
    * Quote: the phone order "Identity, Goals, Snapshot, Skills, Score trend, What keeps
      catching you, Achievements, Activity, Recent activity, Learning preferences, Question
      types met, Saved & in progress, Account."
      → "Identity, This week, Goals, Skills, Snapshot, Test-day readiness, Score trend, Pace,
      What keeps catching you, Your habits, Achievements, Activity, Recent activity, Learning
      preferences, Saved & in progress, Account", with the sticky chip row and collapsible
      cards (U26).
    * Quote: "**Data**: **GET `/api/me/summary`** (one call) builds the page."
    * Append: "It adds `gains`, `pace`, `habits`, `coverage.readiness`, `levers`, `week`,
      `score.projection`, `score.gaps` and `stats.series`."

19. **§3.1, identity card.**
    * Quote: "* **Avatar** 72px: the initial on paper, a chosen topic glyph, or the mark when
      unnamed."
      → "* **Avatar** 72px: the living mark (U22) by default, or the initial, or an earned
      glyph."
    * Quote: "* It opens a popover: "Initial" plus the 19 glyph tiles (5 a row, 44px; the
      selected one has a 2px orange ring)."
      → "… "Living mark", "Initial", plus the 19 glyph tiles, locked ones showing "Reach
      Strong in {skill} · 62%"."
    * Quote: "* **Stat tiles**: a 2×3 grid of paper tiles (radius 10, padding 12)." (R31 made
      it 2×4.)
    * Insert before it: "* **Outcome strip** (U10): since you started · points on the table ·
      fixes held."
    * Append to it: "Each tile adds a 14-day sparkline and a 7-day delta; ACCURACY reads
      FIRST-TRY ACCURACY; every tile opens its lever popover (U13)."
    * Quote the STREAK row's sub-line: ""best 9 · rest days kept"" → ""best 9 · 1 spare
      banked"" (U16).

20. **§3.2, Snapshot.**
    * Quote: "Each line has "Board" → `/challenge/#practice`."
    * Append: "Each line adds its movement since last week and the gap to the next place.
      Below them: the **Climb** line (n ≥ 20) and **You, 30 days ago** (U11)."

21. **§3.3, Study goals.**
    * Quote: "* the live line "+100 from your latest band";"
    * Append:
      * "* "What 700 takes: about 37 of 44 right; you're near 31", with the 3 skills (U4);"
      * "* the pace line and tag from `plan.pace`, and the one-tap date that makes it Steady;"
      * "* "Raise to 750?" once reached."
    * Quote: "* **Edit** opens a popover with chips for the upcoming official dates, each with
      "in N days" …"
    * Append: "each chip also shows "register by …", "late …" and, with a projection,
      "~690" (U17, U4)."
    * Quote: "* The week starts on the student's preference."
    * Append: "* History: "Met 4 of the last 6 weeks", with 6 mini bars (U14)."

22. **§3.4, Learning preferences.**
    * Quote: "| Questions per set | seg 5 · 10 · 22 · ∞ | — |"
    * Insert above that row:
      * "| Mode | seg Learn · Build · Test-like · Custom | "Sets clock, feedback, repairs,
        explanations and difficulty together." |"
      * "| Follow my exam date | switch | "Build · 34 days to Nov 7 · Test-like starts Oct 17." |"
    * Add: "Rows the mode sets carry "Set by Build · Change" or "Yours · Back to Build" (U15)."

23. **§3.5, Skills.**
    * Quote: "The header's right side reads "Strongest: Circles · Weakest: Probability" (once
      there are answers), with "All skills in Results"."
      → "The header holds "About 60 points on the table · your top 3 hold 34", the seg "By
      points · By domain", "Strongest / Weakest", the Sharpen line when skills are rough, and
      "All skills in Results" (U4, U5)."
    * Quote: "* a "Practise" link (a `prefs.set_length` set on that skill)."
    * Append:
      * "* the gain "≈ +20", "about 4 of 44", "at least 6 right · ~9 min" (U4);"
      * "* rough or measured, the 14-day trend, the last 5, and Fading with Keep warm (U5)."
    * Add a footer: "Practise the top 3 · 15"."

24. **§3.6, Score trend.**
    * Quote: "* **Target and exam**: the target is a dashed line labelled "Target 700"."
    * Append: "The projection cone to the exam date, the plan's pace line, and what changed
      in each gap between sittings (U9)."

25. **§3.7, What keeps catching you.**
    * Quote: "Footer: "All mistakes"."
    * Add before it: "Header pill: **Trap gauntlet · 10** (U6)."
    * Add a new card after §3.7: "**3.7a Your habits** (U6)."

26. **§3.8, Achievements.**
    * Quote: "* The earned date, "Sep 21"."
    * Append: "* In progress: **Go · {action}** (U13)."
    * Quote: "That is 43 in all."
    * Replace with: "That is 43, plus Trap-proof (U6) and Every goal met (U14)."

27. **§3.9, Activity.**
    * Quote: "A planned rest day with nothing done shows a faint centre dash."
    * Append: "A spare day shows a hollow ring (U16)."

28. **§3.10, Recent activity.**
    * Quote: "Each row has an icon, a title, a detail, a time ("14:02 · 3h ago") and a
      chevron, and links wherever it can:"
    * Append: "Sitting rows add their effect line and **Again · new numbers** / **Follow up ·
      n** (U12)."

29. **§3.11, Question types met.**
    * Quote: the heading "###### 3.11 Question types met (where they show usage meters)" and
      its body.
    * Replace with "###### 3.11 Test-day readiness (where they show usage meters)" = U8. The
      raw "57 of 386" becomes its second line.

30. **§3.12, Saved & in progress.**
    * Quote: "* "Saved questions **3**", with **Practise saved** (`/api/drill {saved: true}`)
      and "See all" → `/mistakes/#saved`."
    * Append: "Saved questions return as fresh twins in Up next at 7 and 21 days (U1). Add
      "Bring your misses" (U2)."

31. **§3.13, Account.**
    * Quote: "* **Saved**: "Progress saved to dana@gmail.com · since Sep 23", with **Manage**
      → `/me/settings/#account`, and **Sign out** (quiet, door icon, confirm dialog)."
      → "* **Saved**: the recovery line ("You can sign in 2 ways: passkey, email"), "Signed in
      on 3 devices" → the Devices list, **Manage**, and **Sign out** (quiet, Undo toast;
      U19, U21)."
    * Quote: "* **Save progress** (filled);"
      → "* **Save with a passkey** (filled when the platform supports it), or **Save
      progress** by email;"

32. **New §3.14 Pace** (U7) and **§3.15 This week** (U14): add them as cards, with the anatomy
    in U7 and U14.

33. **§4.1, Practice settings.**
    * Quote: "These are the defaults a new set opens with."
    * Prefix with the Mode and "Follow my exam date" rows (U15).
    * Quote: "A "Reset practice defaults" quiet button ends the section."
    * Append: "Beside it, "Back to stage" clears every key marked Yours."

34. **§4.3, Study.**
    * Quote: "* **Reminder**: seg None · 10 min before · 30 min before (default 10)."
    * Append: "* **Notify me on this device** (U18b), with its kinds and quiet hours, shown
      only when push is configured."
    * Quote: "* **Subscribe**: copies a `webcal://…/api/cal/{token}.ics` link."
    * Append: "Events are titled with what is due that day and link to `/?next=1` (U18a)."

35. **§4.4, Account & devices.**
    * Quote: "**Email**, by state:"
    * Insert before it:
      * "**Passkeys** (U19): Save with a passkey, the list, Remove."
      * "**Devices** (U21): the list, Sign out, Sign out all other devices, and the recovery
        line."
    * Quote: the "**Pair a device**:" block, through "* **I have a code** → `/signin/#pair`."
    * Replace with: "**Sign in another device** (U20): type the 6 digits shown on the other
      device, or scan its QR."
    * Quote: "* Saved → confirm: "Sign out? You can sign back in with dana@gmail.com." [Sign
      out] [Cancel]"
      → "* Saved → no dialog; the toast "Signed out · Undo" (U21)."

36. **§5, Sign in.**
    * Quote: "* Tabs: **Email code** · **Pairing code** · **Device code** (hash `#email` /
      `#pair` / `#code`)."
      → "* Tabs: **Passkey** · **Use your phone** · **Email code** · **More** (device code)
      (hash `#passkey` / `#phone` / `#email` / `#code`; `#pair` is an alias of `#phone`).
      Every tab has "This is a shared computer" (U21)."
    * Quote: the "**Pairing code**:" block, through "* 429 "Too many tries. Wait 10
      minutes.""
      → the U20 new-device screen, with the same 404 / 410 / 403 / 429 copy.
    * Quote: "`/pair/` is a two-line page that redirects to `/signin/?c=…#pair`, because a
      short URL is easier to type on a phone."
      → "… redirects to `/signin/?c=…#phone`, and `/link/?r=` is the phone's approval
      page (U20)."

37. **§6, Shared view.**
    * Quote: "* What keeps catching you (names and counts);"
    * Append: "* Your habits; This week; Test-day readiness (the atlas, read-only)."

38. **§7.2, the New assignment table.**
    * Quote: "| What | Practice set · Module (22 q · 35 min) · Full section (44 q · 70 min,
      adaptive) |"
      → "| What | Practice set · **Reach a level** (skills or types, Getting there or Strong,
      cap 20–80) · Module (22 q · 35 min) · Full section (44 q · 70 min, adaptive) |"
    * Quote: "| Questions | **Fresh for each student** (default; …) · **Same for everyone**
      ("Good for going over them together") |"
      → append "· **Tailored** ("Each student's own mistakes on these skills first")".
    * Quote: "* **Per student**: status, right/asked, time, finished at, late, and attached
      working."
    * Append: "For Reach a level: questions needed, or Stuck with the named mistake. For
      Tailored: own mistakes served and fixed. A histogram of questions needed (U27)."

39. **§8, Help.** Add these answers:
    * `#points` (how points on the table is worked out, with the invented-anchors caveat);
    * `#readiness`, `#habits`, `#pace`, `#stages`, `#spare`, `#passkeys`, `#devices`;
    * `#fixed` (the list from `GET /api/reports/fixed`).
    * Every answer also goes into `web/help/answers.json` (U13, U24).

40. **§9, the table.**
    * Quote: "| profile credits card | **Question types met** |"
      → "| profile credits card | **Test-day readiness** (the type atlas, U8) |"

41. **§10, admin.**
    * Quote: "* For a dispute: **Key was wrong** (the attempt stays disputed for good, and the
      template is flagged in the log) or **Key was right** (…)."
    * Append: "**Key was wrong** offers "just this question" or "every seed of this template
      since {date}", disputes every learner's matching attempts, and posts a correction to
      each. **Stop serving** / **Release** writes `quarantine`. Me-too children are listed
      under their parent (U3)."

42. **§11, component inventory.**
    * Quote: "* Features: `UI.report(ctx)`, `UI.quick()`, `UI.palette()`, `UI.keys.register(scope,
      map)`."
    * Append: "`UI.next` (the Up next block, popover and time box), `UI.inbox`, `UI.week` (the
      weekly sheet), `UI.lever(el, key)`, `UI.help(id)`, `UI.cached(path)`, `UI.share` (twin
      default)."
    * Quote: "* Data views and controls: `UI.trend`, `UI.heatmap`, …"
    * Append: "`UI.quadrant` (charts.js), `UI.atlas` (a grid of `UI.cell`), and the
      sparkline in `UI.tile`."

43. **§3.1.5, Server changes.**
    * Quote: the "**server/account.py: pairing with approval**" block.
    * Replace with the U20 endpoints (`/api/link/request`, `/api/link/{token}`,
      `/api/link/code`, `/approve`, `/deny`).
    * Add blocks:
      * `server/next.py` (U1);
      * `server/types.py` and the match / import endpoints (U2);
      * the report check, similar, accept, fixed and quarantine (U3);
      * `estimate.gains / need / projection` (U4, U9);
      * `progress.pace` (U7);
      * `server/habits.py` (U6);
      * `week_goals` and `/api/me/week` (U14);
      * `passkeys` and `webauthn_challenges` (U19);
      * `devices` and `learner_of` for `d:` (U21);
      * `push_subs` and `server/push.py` (U18);
      * `GET /api/prefs` (U24);
      * `feed?unread` and `/feed/seen` (U25);
      * `/api/me/summary` additions (U4–U13).
    * Quote: "GET /api/shell" (Returns:)
    * Add the keys listed in override 16.

44. **§3.1.8, Acceptance checks.**
    * Quote: "18. Pairing: POST /api/pair as A → {code}. …"
    * Replace with U20's acceptance 1–4.
    * Quote: "19. Email: …"
    * Keep it, and add: "the passkey checks of U19."
    * Quote: "23. New learner a:v2revnew on /me/: …"
    * Add: "the U1 block shows "Take the diagnostic"; Test-day readiness reads 0%; Pace and
      Your habits show their empty states."
    * Add the acceptance lists of U1–U28 as items 38 onward.

45. **§3.1.9, open questions.**
    * Quote: "- Is SMTP configured for production (SATF_SMTP_*)? …"
    * Append: "Passkeys (U19) and phone approval (U20) make accounts work without SMTP; email
      codes stay as one option."
    * Quote: "- The practice rank uses right answers over a rolling 7 days, which rewards
      volume. …"
    * Append: "Answered by U11: the volume rank stays, and Climb ranks gain for students who
      started near the same band."
    * Quote: "- Email reminders at the preferred time need SMTP and a scheduler. Are calendar
      alarms enough for now?"
      → "Calendar events now say what is due (U18a); Web Push needs no SMTP (U18b)."

### 3.2 Outside the section (Part 2 lines these upgrades need; I1 applies them with the owners)

| where | change | upgrade |
|---|---|---|
| R1 | Unchanged (5 tabs). Add: the tab bar's grip and hold shortcuts, and Up next first in the menu sheet | U1, U26 |
| R4 | "Creating a class needs a saved email" → "a saved account: a passkey or a verified email" | U19 |
| R9 | Check-ins due feed Up next row 4 and the calendar titles | U1, U18 |
| R11, §2.7 | New keys: `mode` (learn / build / test / custom, default learn), `stage_auto` (bool, true), `registered` (date or null). Under a mode or stage, a key the student sets is stored even when it equals the default; `{key: null}` deletes it. `GET /api/prefs` serves the registry | U15, U17, U24 |
| R13 | Spare days: 1 per 7 study days in a row, up to 2; a spent spare neither breaks nor extends the streak | U16 |
| R16 | `estimate.py` adds `gains`, `need`, `projection` | U4, U9 |
| R17 | The instant check, me-too (`reports.parent`), accept, fixed list, quarantine; F4 adds `progress.remark(learner, attempt_id)` (re-mark, close the trap it alone opened) | U3 |
| R18(b) | Feed titles and descriptions say what is due and link `/?next=1`; deadline events | U17, U18 |
| R18(c) | `sets` `cfg.fresh` (a fresh seed per viewer) | U28 |
| R25 | New ladders: Trap-proof 5/20/50; Every goal met 1/4/12 weeks | U6, U14 |
| §2.5 | Tables: `passkeys`, `webauthn_challenges`, `devices`, `quarantine`, `week_goals`, `push_subs`. Columns: `pairs.dir / token / approver / session_only`, `reports.parent / check`, `outside_scores.misses`, `learners.feed_seen`; `traps.origin` adds `cb_qbank`. `LEARNER_TABLES` and `carry` include the new learner-keyed tables | U2, U3, U14, U18–U21, U25 |
| §2.6 | Fields: `segments` ([{pool, ids?, topics?, count}], filled in order), `box` (5–60 minutes), `until` ({mastery, cap}). Sources: `next`, `probe`, `habit`, `gauntlet`, `bluebook`. `want` also matches `progress.norm(reason)` | U1, U2, U5, U6, U27 |
| §2.8 | Global: `G` then `N` starts Up next | U1 |
| §2.9 | Providers: F2 `next.queue` → S3, S4, S6, S7; F4 `estimate.gains / need / projection`, `progress.pace` → S1, S3, S6, S7, F2; F5 `habits`, `types.match` → S1, F2, F3, S4, S10; T-bank `check.check_item` → F6; F4 `quarantine` → F5, S3, S5, S8; S8 `compete.climb` → S1; S7 `plan.pace` → S1, F2 | all |
| §2.12 F2 | F2 also owns `server/next.py`, `web/sw.js`. F5 owns `server/habits.py`, `server/types.py`. S1 owns `server/push.py` and `web/link/**` | U1, U2, U6, U18, U20 |

---

## 4. Rejected

* **Offline pack** (outcomes #13, unfair-advantage #13): it needs a caching service worker, a
  client grading path and back-dated answers. The need is rare, and `UI.saveQueue` already
  rides out brief drops.
* **Practice confidence tagging on every question** (outcomes #6, most of it): most students
  won't tap Sure/Unsure/Guess each time, so the card would be empty. The data that already
  exists (guess flags, test confidence, strikes) feeds U7's "When you guess" line instead.
* **Live class check on a projector** (experience #11, unfair-advantage #9): classroom
  novelty for a secondary audience, with polling infrastructure. The assignment detail's
  class-misconception ranking and "Assign a repair" cover the teaching loop without it; revisit
  when a teacher asks.
* **Printable per-student class packs with QR answer entry** (unfair-advantage #8): Review's
  worksheet (S10) already prints. Per-student versions with QR marking wait for teacher demand.
* **Per-question working with teacher comments** (experience homework gap): turns attachments
  into a messaging feature; the existing attachment is enough.
* **A 4-digit PIN on shared-device profiles** (unfair-advantage): a PIN checked in the browser
  over localStorage is theatre. Shared-computer mode and per-device sign-out are the real
  protection.
* **A printed recovery card with the device code** (unfair-advantage #5): it puts the whole
  credential on paper in a school bag. Passkeys plus email cover recovery.
* **A profile-wide 7d / 30d / All range switch** (experience tiles gap): every card would need
  a range parameter. The deltas and sparklines (U10) carry direction for less.
* **Each student's best skill rank this week** (experience ranks gap): it is 19 more volume
  boards. Climb (U11) gives every level a race it can win on learning, not volume.
* **An "Had an effect" activity filter** (outcomes): each row already prints its effect (U12).
* **Help answers that read your own data on /help/** (unfair-advantage): the lever and "?"
  popovers (U13) show the student's numbers where the number is. Help stays static and
  cacheable.
* **Adaptive stepping per question type** (unfair-advantage prefs gap): 386 types would each
  need 2 answers before adapting. R33's per-skill rule adapts sooner.
* **Palette results bottom-up on the phone** (experience #10): a non-standard order that would
  confuse. The input pinned above the keyboard gives the reach.
* **A "Twin of this" tab in the quick sheet** (unfair-advantage quick-sheet gap): every
  surface that shows a question already has "Try one like this" (R23).
* **A weekly email to a parent** (unfair-advantage #10): it needs SMTP (open question 5). The
  progress link shows the week card live.
* **A bare `N` key for Up next** (outcomes #1): it collides with Words' N, the players' N and
  the runner's navigator. `G N` fits the G-letter map.
* **The habit tell above every stem in a careful set** (outcomes #5): it is a runner feature for
  one drill kind. The tell shows in the verdict chip and the summary instead.
* **"700 needs +15 min a day"** (outcomes target gap): there is no model from minutes to
  points that we could defend. The popover states points a week and where the points are.
* **A Speed preset in Modes** (experience prefs gap): U7's Speed drill, per skill, does this
  better.
