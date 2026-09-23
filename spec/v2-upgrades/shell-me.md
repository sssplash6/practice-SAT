# v2 upgrades: app shell, navigation, profile and account

Written 2026-09-23 for `spec/rebuild-v2.md` §3.1 (lines 653–2294). It merges three designers'
proposals (outcomes, experience, unfair advantage) into one build-ready list.

* **Precedence.** `spec/v2-decisions.md` wins over this file. This file wins over §3.1 where
  they differ: §3 of this file lists every place that changes. Part 2 resolutions (R1–R38)
  still hold, except the lines named in §3.2 "Outside the section".
* **The bar.** A student who uses TopTierPrep today opens ours and wants to switch, because
  this area does more for their score and is nicer and faster to use. Parity is failure.
* **Names.** Upgrades are U1–U29 (U27 is removed: see below). Builders are Part 4's tasks
  (F1–F6, S1, S3–S10, T-bank; S2 is removed). New server modules are assigned to one owner
  each.
* **No classes** (v2-decisions item 5). This file has no teacher or student roles, classes,
  homework, assignments, class codes, `/class/` or `/join/` pages, class boards or rosters,
  and no data or endpoints for them. Where friends compete together, that is Compete's
  private contest: an invite code or link that Compete owns. The shell only shows what
  Compete exposes (U1 row 2, U18, U25).
* **Subject-aware.** Per v2-decisions item 3, every payload that is about a subject is keyed
  by `subject` (`math` now), so a second subject is additive:
  * `GET /api/me/summary?subject=math` returns
    `{stats, goals, subjects: {math: {score, domains, coverage, gains, pace, habits, levers, ranks}}}`.
    Only cross-subject facts sit at the top level: `stats` (study time, answers, streak,
    spares, series), `goals` (U4) and the account. Every `summary.X` path below that is about
    a subject means `summary.subjects.math.X`.
  * `/api/shell.me.domains`, `estimate.gains`, `progress.pace`, `habits` and the atlas take
    `subject`. Achievement tiers that count skills, domains or types (the 19 skill badges,
    the domain badges, Explorer's top tier of 386) are computed from
    `catalogue.by_topic(subject)`, never hard-coded.
  * Acceptance: `GET /api/me/summary` has `subjects.math`, and no top-level key holds
    `domains`, `coverage`, `gains`, `pace`, `habits` or a Math score.
* **Facts measured for this file** (on the current bank, 2026-09-23):
  * `material/keys` holds 1,039 official Math items: 54% of the 1,921 in College Board's Math
    question bank (teardown). It is uneven: circles 32 of 67, area and volume 59 of 110. So
    about 46% of real College Board Math IDs are not in our index yet (U2 handles them and
    closes the gap).
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
| 1 | Sidebar and icon rail | ~220px sidebar, a toggle to a ~60px rail, stacked wordmark | 248px sidebar and 68px rail, `[`, tooltips carrying the meta and the shortcut, an overlay at 760–1099px. Its pinned stack was taller than a school laptop's window, so the nav got no room | An **Up next** block with Start under Search (U1); a play button on the rail; rail peek. A height budget keeps every nav item on screen down to 480px tall. Below 1100px tall, Up next and the Today card move, in full, to a **Now strip** at the top of the page instead of shrinking (U26) | v2 BELOW theirs on a 1366×768 Chromebook (the nav scrolled out of sight). **U1 + U26 → WAY BETTER.** At every height the chrome says what to do next, why, how long it takes and how many points it is worth, in full text with nothing behind a hover, and starts it in one click (or `G N`) from every page. All nine items stay visible at 1366×657. |
| 2 | Primary nav | 10 routes, no counts, one of them sells | 9 items with live metas: 12/28, ● 14, Resume, Test day, New, #4, 2 due (the 9th was Class, now removed, decision 5) | Adds a **Profile** item with the week's goals ("1/3"), an inbox dot (U25), an urgent dot on the Today tab (U1). Each fact shows once: the Plan meta names the next test day instead of repeating Today's count (U26) | **WAY BETTER already in v2.** Nine items that each say what is waiting there, with nothing repeated. Theirs are ten silent labels, one of which sells. |
| 3 | Active nav state | Grey-blue pill, bold label | `--wash`, 600 weight, a 3px orange bar, section mapping for sub-pages. Me mapped to the user card, since there was no Profile item | Me, Settings and Sign in map to the new Profile item. Me, Settings, Results and Help get a sticky section bar with scroll-spy, built from one `UI.shell({sections})` list that covers every card, at every width (U26) | v2 PARITY, and Me had no nav item. **U26 → WAY BETTER.** On Me (16 cards), Settings, Results and Help, any card is one click away without lengthening the sidebar. |
| 4 | Upgrade card | "Upgrade to Pro · Unlimited tests & QBank" with a TRIAL badge | Today card: minutes and questions against the goal, streak, exam countdown (v2's due-assignment line is removed, decision 5) | Adds spare-day flames (U16), a registration deadline (U17) and a private contest closing within 24 h (from Compete). Drops the questions bar the Today item already shows. Below 1100px tall the whole card moves to the Now strip at the top of the page, every line in full (U26). Up next sits beside it (U1) | **WAY BETTER.** Their slot sells. Ours shows the student's own day in full at every screen height, and starts it. |
| 5 | User card | Avatar, name, role "User", chevron; badges Trialing / Teacher Seat | Avatar, name or handle, masked email or "Not saved yet" | The student's own name (any script, not the board handle, U29). A photo kept only on this device, or a living-mark avatar that fills with domain mastery, which only the student and their progress links see (U22). An unread count (U25). "Shared computer · Sign out" (U21) | v2 PARITY. **U21 + U22 + U25 + U29 → WAY BETTER.** Their name and photo, plus whether progress is safe, what is new, and how far each domain has come. |
| 6 | User popover | Name and email, My Profile, Send feedback, Sign out (red); ignores Esc | A `role=menu` with Profile, Settings, Sign in, Pair, Shortcuts, Help, Feedback, Sign out; Esc fixed (v2's Class item is removed, decision 5) | Adds the "Since you were last here" inbox: 3 rows and "See all" (U25). Adds Students on this device, on a family device (U21). A Display group of `menuitemcheckbox` rows (Dark theme, Large text) plus **Keyboard shortcuts (?)**. Home and End jump to the first item and to Sign out (U26) | v2 PARITY: a bug fix plus links. **→ WAY BETTER.** Missed events are kept, display toggles work without leaving the page, and Sign out is one End press away however long the menu grows. Siblings switch in one tap without mixing their answers. |
| 7 | Floating quick-add | A draggable "Add your own word" button that covers Next | Quick sheet (Q or the bolt): Quick question · Log a mistake · Add a word; never floats | Log a mistake takes a College Board question ID, pasted text or a whole Bluebook test, and names the mistake from the letter the student picked (U2). An ID we don't hold yet falls back to pasted text or a skill, never to an empty result. It is logged, and T-bank ingests the rest of the Question Bank so the map covers every Math ID. The sheet also offers a time-boxed start (U1) | **WAY BETTER.** Theirs captures a word. Ours turns a missed official question into its exact question type, its named misconception (92% of the official wrong options we hold resolve to one) and unlimited twins. It works by ID for the 1,039 IDs held today (54% of the Math bank; the ingest closes the rest), and by pasted text or skill for any other. |
| 8 | Sign-in | Google only, and a wall before anything works | No wall. Email code, pairing, device code. Slower than Google on a new device; email needs SMTP. Every sign-in silently merged whatever answers the browser held | **Continue with Google** when the deploy sets `SATF_GOOGLE_CLIENT_ID` (U19b). A passkey in 2 taps, offered in the field's autofill (U19). The phone approves a shared computer, with nothing typed on it (U20). Email codes, with SMTP a launch requirement and `/api/health` stating the mail mode, so the Email tab never dead-ends (U19). A remembered email in 1 tap. `/signin/` opens on the method this device used last. When the device holds answers, the student chooses whether to add them. A shared computer, or answers over a day old, never adds by default (U19–U21) | v2 BELOW theirs for a returning student, and a library sign-in could merge a stranger's answers. **U19 + U19b + U20 → WAY BETTER.** Their one method (Google) is there, and so are four more: a school Chromebook signs in with the student's Google account, a synced passkey signs in from autofill, a phone approves a library PC, and email works on any device. Still no wall, and no one else's answers are mixed into yours. |
| 9 | Password | Set / Change password (8+ characters, confirm) | None: email codes | Passkeys (U19), Google (U19b) | **WAY BETTER.** Nothing to remember and nothing to leak. |
| 10 | Sign out | Red Sign out in the popover and on the profile | Confirm dialogs. "Sign out everywhere else" rotates the one code | Every browser holds its own device key, including the one that saved. Other browsers that held the old code swap to their own key on their next visit instead of being cut off, and the student can end the old code at once. A one-time transfer code replaces Show / Copy. Sign out drops that student from the device and revokes its key, even if the tab closes during Undo. A shared computer signs out at once, and its key dies 60 s after the last tab closes or after 15 idle minutes (U21) | v2 PARITY. **U21 → WAY BETTER.** A library computer can be signed out from your phone, reopening a closed tab there doesn't bring you back, the list shows every device that can act as you, and no other device is affected. |
| 11 | Report modal | "Sent with your report" (UUID), Title 0/200, Category, Details 0/5000, 10 × 50 MB images; the student never hears back | (template, seed), a "named mistake doesn't fit" category, bounded disputes, replies, an admin page. Images capped at 10 MB each | "Answer key is wrong" is checked in about a second, two ways: a separate solver re-derives the numbers, and we compare how students who are Strong in the skill answer this question type. Only when both agree does the student get the named reason for their answer, worded as exactly what was checked. Wording, figure and option problems, and any disagreement, go to a person with the evidence. Matching reports merge ("me too"). One confirmed fix corrects every affected student. Bad questions are quarantined. No screenshot needed; a typo takes 2 taps. When a file helps: 10 files, GIFs and screen recordings up to 50 MB each, and a built-in **Record screen** (U3) | v2 PARITY in form, and BELOW theirs on file size. **U3 → WAY BETTER.** Most disputes become a lesson within seconds, without talking a student out of a real key error. Those reach a person with evidence, and the fix reaches everyone. Everything theirs attaches, ours attaches, plus video and a recorder. |
| 12 | Send feedback (+ /feedback) | The same modal, with no context | The same, plus page context and replies | A breadcrumb of the last 10 actions (kept in memory, shown before sending). A public "Fixed from your reports" list (U3) | v2 PARITY. **U3 → WAY BETTER.** Bugs arrive reproducible, and students can see their reports change things. |
| 13 | Toasts | Generic ("Task skipped / added …") | Generic, with actions; used for achievements and replies | An inbox keeps every missed toast. Undo on every reversible action. A welcome-back block. At most one sheet opens by itself a day, never over a link the student followed, and toasts wait until it closes (U25) | v2 PARITY. **U25 → WAY BETTER.** Nothing important vanishes after 4 seconds, a slip is one tap to undo, and coming back means one sheet, not a pile-up. |
| 14 | Profile layout | Left third / right two-thirds | The same split, 13 cards, a non-sticky left column, a phone order | A sticky section bar with scroll-spy at every width, and collapsible cards (U26). New cards: This week, Pace, Your habits, Test-day readiness. Learning preferences gains Words a day and Test timing (U15). Saved gains saved words and marked questions (§3.1 override 30) | v2 PARITY. **→ WAY BETTER.** It holds more and is faster to move through. |
| 15 | Identity card and tiles | Avatar with a camera badge, name, email, a "Not set yet" pill, 2×2 tiles (Streak / Tests / Solved / Vocab); two streaks disagree | 2×4 tiles with sub-lines and links, goal pills, one streak | An outcome strip: score since you started, points on the table, fixes that held. Each tile gets a 14-day sparkline and a delta. Accuracy is first-try. Every figure opens how it is worked out, your numbers, and what moves it (U10, U13) | v2 PARITY: more volume counts. **U10 + U13 → WAY BETTER.** It says whether the score is moving and what moves it next. |
| 16 | Streak | 0 on the profile and 1 on the question of the day; any missed day breaks it | One server value; planned rest days kept | Earned spare days: 1 per 7 study days in a row, up to 2, shown everywhere (U16) | **WAY BETTER.** One number, which a sick day cannot wipe out, and free. |
| 17 | Rank snapshot | Global 128 and Country 43, with no contests played and no stated basis | Practice rank (right answers in the last 7 days) among everyone and the same exam date; challenge lines (v2's per-class lines are removed, decision 5) | Adds movement since last week, the gap to the next place, and a Country line (their Country rank, which v2 dropped from Me), with the country chosen right there or in Settings › Account & devices. Adds a Climb rank among students who started near your band: the window widens until 20 are in it, and the card states it. Adds you against yourself from day 8 (U11) | v2 BELOW theirs: still ranks volume, and no Country rank. **U11 → WAY BETTER.** It rewards learning from launch week, gives every level a race it can win, keeps their Country rank (one tap to switch on), and states its terms. |
| 18 | Credits meters | Quota meters and Upgrade | "Question types met: 57 of 386" | Test-day readiness, weighted by how often each kind of question appears in College Board's own questions, with the type atlas (U8) | v2 PARITY: a raw count. **U8 → WAY BETTER.** Coverage tracks the questions the student will actually see, and the biggest gap is one click from practice. |
| 19 | Saved content | Counts: Saved Words, Redo Questions, Saved Questions | Counts with Practise saved, Fix all, In progress with Resume (v2's due assignments are removed, decision 5). It dropped their Saved Words | Saved words (Review them) and Marked for review (Practise marked) join the counts. Saved questions come back as fresh twins in Up next at 7 and 21 days (U1, §3.1 override 30) | v2 BELOW theirs (two of their three counts). **→ WAY BETTER.** All three of theirs, plus marked questions, and a bookmark list becomes spaced retrieval. |
| 20 | Account block | Name and email editable inline, password, "Google connected", Sign out | Saved and unsaved states, Manage, Sign out. One name served as both the student's name and the public board name, under the board rule (no José, no 李明, no second Emma) | The student's own name in any script, private and not unique, apart from the board name, each editable inline (U29). "Google connected" when used (U19b). Passkeys list, a devices list that includes every browser that can act as you, and a recovery line: "You can sign in 3 ways" (U19, U21) | v2 BELOW theirs on the name (a regression from our own site). **U29 + U19b + U21 → WAY BETTER.** Their name and email editing, a separate board name that keeps the real name off public boards, and the student sees every place they are signed in and that they can't be locked out. |
| 21 | Avatar | Photo upload, replace, remove | An initial or one of 19 glyphs, all free to pick | **Your photo, kept on this device only**: upload, replace and remove, downscaled to 256px and never uploaded. Or the living mark that fills with domain mastery, seen only by the student and their progress links. All 19 glyphs stay free from day one; reaching Strong adds a filled ring and a check to that glyph. Public boards show only the glyph or the initial (U22) | v2 BELOW theirs. **U22 → WAY BETTER.** Their photo, with no copy of a minor's face on any server, plus 21 more choices on day one, one of which says something true about the student, badges earned on top, and no photo or mastery on public boards. |
| 22 | Study goals card | Target (not synced), exam date "N days remaining", Daily 2h, Weekly 12h, Preferred time (no effect) | Target and exam date synced and editable; daily and weekly bars; week dots; focus; preferred time → calendar. Math target only, while Today and Plan show a 1600 total | The target on their 1600 scale: "Total 1400 = Math 700 + R&W 700", both parts editable, the same figure on Me, Today and Plan. The Math part stated in questions and module-1 routing, a projection to the exam, and week goals with history (U4, U9, U14) | v2 BELOW theirs (no 1600 total on the profile). **→ WAY BETTER.** The number colleges see, and whether it is realistic and what reaching it takes. |
| 23 | Target score modal | States the wrong "current score"; a number input; Save disabled until you type | Slider, chips, "+100 from your latest band"; synced | Total and both parts. "What 700 takes: about 37 of 44 right, with at least 14 of 22 in module 1 to reach the harder module 2; you're near 31." It names our model's ceiling (780) instead of promising 800. A live pace tag, one tap to a date that makes the target Steady, and "Raise to 750?" once it is reached (U4) | v2 PARITY. **U4 → WAY BETTER.** The target in right answers, with the routing it needs, on the 1600 scale. |
| 24 | Exam date | A select that includes past dates; the wizard uses a free calendar | Upcoming official dates, Another date, No date yet | Each chip shows the registration and late deadlines, and a projected score when the projection is within ±80 (U9). A deadline banner stays until "Registered"; the deadline goes to the calendar (U17, U4) | v2 PARITY. **U17 → WAY BETTER.** It covers missed registration, the plainest way to miss the SAT altogether. |
| 25 | Daily / weekly goal | "2 Hours" / "12 Hours", with bars | Bars and week dots (the plan's day rule) | Weekly goals chosen from evidence ("Fix the 4 open Circles mistakes", "Pass 6 check-ins") and a history of met weeks (U14) | v2 PARITY. **U14 → WAY BETTER.** |
| 26 | Preferred time | "Evening", with no effect anywhere | Calendar download or subscribe, with alarms. Google Calendar ignores alarms in URL feeds, Apple strips them by default, and feed titles went stale between refreshes | Notifications on this device ship in the core build: "3 check-ins due · about 4 min", worked out at send time, at the time the student chose, whatever that time is. Quiet hours (shown and editable) only hold back extra nudges (U18b). For calendars: step-by-step alert setup for Google and Apple, an **Add to Google Calendar** recurring event that uses the student's own notifications, and feed events that open what is due now (U18a) | v2 PARITY in practice (mostly silent blocks). **U18 → WAY BETTER.** The reminder actually rings, on time, and says what it is for. |
| 27 | Subject performance | A per-subject block, empty on a new account | 19 skills under 4 domains: bar, accuracy, mistake dots, Practise | Sorted by points on the table. Each skill states its evidence on one ladder: Not started, Not measured yet, rough, measured. It also shows its 14-day trend, its last 5 answers and a fading marker. A 12-question Sharpen probe (U4, U5) | v2 PARITY: a report card. **U4 + U5 → WAY BETTER.** A priced to-do list the student can trust. |
| 28 | Score trend | A line chart with "Latest: N" | Range bars, target line, exam tick, click-through | A projection to the exam date once 3 sittings span 3 weeks, labelled "If this pace held". It is shrunk toward no change, its gains taper after 4 weeks, and it is widened by the fit's own scatter. Also the plan's pace line, and what changed between two sittings (U9) | v2 PARITY: a nicer chart of the past. **U9 → WAY BETTER.** It ties effort to results and looks forward, without promising a score that a couple of sittings can't support. |
| 29 | Achievements | 4 hard-coded tiles; View All is dead | 43 tiered badges with progress, earned dates and rules | Go on every badge in progress starts the drill that advances it. New Trap-proof and week-goal ladders (U13, U6, U14) | **WAY BETTER already in v2.** |
| 30 | Learning preferences | Timed/Untimed, Adaptive/Fixed, 3 toggles | 5 inline rows, instant save, helpers, full Settings | Modes (Learn · Build · Test-like · Custom) that follow the exam date. They apply to sets the student builds and to Up next's skill rows; fixing drills always show the key after each answer. Each row says who set it. Words a day (their Include Vocab Review) and Test timing join the inline rows. Palette commands (U15, U24) | v2 BELOW theirs (no vocab row). **U15 → WAY BETTER.** Practice turns into test conditions on time, without the student remembering to switch, and fixing a mistake never waits for the end of a set. |
| 31 | Recent activity | A list of sittings | A filtered feed of 10 kinds under day headers, paged | Each row shows its effect (mastery words moved, mistakes fixed and opened, about how many points) and offers Again · new numbers, or Follow up (U12) | v2 PARITY in kind: log lines. **U12 → WAY BETTER.** |
| 32 | Subscription and billing | Header, plan status, usage meters, Pro $13.99 / Elite $23.99 cards, 7-day trial, payment history, /pricing | None: free | Nothing further | **WAY BETTER.** Everything is free, and each surface they sell from does study work: the Today card, Test-day readiness and Help. |
| 33 | FAQ accordion | Six billing questions | /help/ with live search, anchors, copy-link | A "?" beside every number opens its answer in place, with the student's own numbers. The palette searches Help. A Fixed list (U13, U24, U3) | v2 PARITY in form. **→ WAY BETTER.** |
| 34 | Classes, homework and the teacher dashboard (/my-classes) | Hidden in theirs; a teacher adds students, assigns a test or a QBank session with a time limit and Attach file, and sees results | /class/ with a join code, assignments, a roster | **Not built here** (v2-decisions item 5: a separate platform runs classes). No classes, roles, homework, assignments, class codes or `/class/` and `/join/` pages. Friends who want to compete together use Compete's private contests, an invite code or link that Compete owns. A parent or tutor who wants to follow one student uses the progress link (`/share/`, R18a) | **Out of scope by decision.** Not scored against theirs. |
| 35 | Single-question route | /question/:key | Permalink `?q=TEMPLATE:SEED` | "Send to a friend" defaults to a twin (same type, the friend's own numbers), with a head-to-head result (U28) | v2 PARITY. **U28 → WAY BETTER.** Answers can't be passed along. |
| 36 | Shared session links | /question-bank/shared/:id with a Start Practice landing | Sets, with owner results showing per-question right rates and the most common named mistake | A fresh-per-friend option (U28) | **WAY BETTER** (named mistakes in the owner's results). |
| 37 | Canvas and look | Light grey canvas, white 18px cards; no display settings | Paper with bordered tile cards; dark theme, large question text, reduced motion. Settings offered only Normal · Large, so the Small size had no control | Question text **Small · Normal · Large** with a live preview in Settings, and Dark theme and Large text in the account menu (U26). Instant pages: prerender on hover, and paint from cache. A prerendered page marks nothing as seen, opens no sheet or toast, and sends no write until it is actually opened (U23) | **WAY BETTER.** Display settings they lack, and pages that open with content instead of a skeleton, without breaking the "New" signals. |
| 38 | Phone chrome | Not seen in the walk | A 56px top bar with Search, the Review chip, Quick and the menu; 5 tabs; a menu sheet whose daily rows sat about 700px down, below the fold | Tapping the tab bar's grip opens the menu sheet. Up next comes first. Review, Words, Compete and Quick sit in a footer that is always on screen. The inbox shows 3 rows. A held tab offers shortcuts. The palette sits above the keyboard. The top bar fits 360px with a 3-digit count (U26, U1) | Theirs was not seen. v2 put the daily actions below the fold. **U26 → WAY BETTER.** Review is two taps from any page, on any phone, with no scrolling. |

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
| 2 | `contest` | a private contest the student joined (Compete's invite code or link) that closes within 24 h and they haven't finished (`deps.part('compete','closing_soon')`, which returns `[]` until S8 provides it) | "Sam's contest · 10 q" | "Closes tonight 23:59" | Compete's start href |
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
  (default 95).
* **`pts`**, one formula per kind, all from U4's `estimate.gains` (`gain(t)` = skill t's gain
  to 80%):
  * `skill`: `gain(t)`, rounded as U4 rounds it.
  * `redo`: `gain(t) × share`, where share = this trap's wrong attempts ÷ all wrong first-try
    attempts in skill t over the last 60 days. "Caught you 3 times" with 3 of 10 Probability
    misses and a gain of 20 gives ≈ 6.
  * `habit`: the sum over the habit's skills of `gain(s) × (the habit's misses in s ÷ all
    misses in s)`, over the same 60 days.
  * Every other kind (`resume`, `contest`, `plan`, `checks`, `probe`, `saved`, `warm`,
    `untried`, `qotd`): `pts = null`, and the meta and reason leave the figure out.
  * `redo` and `habit` round to whole points and hide below 1. With `gains == null` (under 30
    answers) every `pts` is null.
  * The lever popover (U13) prints the formula with the student's numbers: "Probability is
    worth about +20 if it reached 80%. This mistake is 3 of your 10 Probability misses in 60
    days, so about 6."
* **De-duplication.** Each item's `key` is `kind:pool:topic`. A plan task whose drill body has
  `pool: 'checks'` or `pool: 'redo'` is not listed as a `plan` row when row 4 or 5 already
  covers that pool. That row's reason gains "· also in today's plan", and finishing it ticks
  the plan task, because S7 matches done tasks on the drill body's `pool` and `topics`.
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
  * Below 1100px tall, and whenever the sidebar is the rail, the block leaves the sidebar
    and renders in full, every line, in the Now strip at the top of the page (U26). It never
    shrinks to a truncated line or a tooltip.
* **Rail**: a 44px orange play button under the search icon. Its tooltip reads
  "Next: Check-in · diameter vs radius · 3 q · 4 min · G N".
* **Phone**:
  * The first row of the menu sheet is Up next, with its Start and the time-box chips.
  * The Today tab gets a 7px dot when item 1 is `urgent` (resume, a contest closing, a
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
  * Brand-new student (0 answers). The first thing offered never ends in a sign-up form:
    1. "Take a module · 22 q · 35 min", reason "Your first score band. No sign-up."
       (href: S5's new-module start);
    2. "Sharpen · 12 q · ~19 min", reason "Or a shorter start: find your weak skills" (row 7);
    3. "Diagnostic · 20 q". While R38's sign-up gate exists, its reason reads "Asks for your
       name and email to show results". For a saved learner (`account.saved`, U19) there is
       no form, so the reason is "Your starting band in 20 questions".
    A quiet "or one quick question" follows.
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
7. A learner with `gains.skills.probability.gain == 20` and 10 wrong first-try Probability
   attempts in 60 days, 3 of them on one open trap: that trap's `redo` item has `pts == 6`.
   A `checks` item has `pts == null`, and its rendered meta contains no "pts".
8. A learner whose plan today holds a check-ins task, with 2 check-ins due: `GET /api/next`
   has exactly one item whose start body has `pool == 'checks'`, and its reason contains
   "also in today's plan".
9. A brand-new learner: `items[0].title` starts with "Take a module", and no item before the
   diagnostic ends in a sign-up form. With `deps.part('compete','closing_soon')` absent,
   `GET /api/next` still returns 200 and has no `contest` item.

#### U2. Bring your misses: an ID, pasted text or a whole Bluebook test becomes named mistakes

*From: outcomes #4, unfair-advantage #1, the experience "search first" gap. Effort M. Builders: F5 (`server/types.py`, the match and import endpoints), F2 (the quick sheet UI), F4 (traps `origin`, the `outside_scores.misses` column, `cb_unknown`), S3 (`add_outside_score`), T-bank (`cb-ingest`).*

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
  * **An ID we don't hold** (any 8-hex ID outside the map; about 46% of real College Board
    Math IDs today) returns one row `{via: 'none', cb_id}` and never an empty list. The sheet
    reads "We don't have 1a2b3c4d yet. Paste the question text, or pick its skill." The text
    box takes focus. Below it, a **Pick its skill** chip row (the 19 skills) is one tap
    away. Either path then continues exactly as a paste or the picker does: result cards,
    or the skill's types, then "Which answer did you pick?".
  * Unknown IDs are counted: `cb_unknown(cb_id PK, first, last, n)` (F4, not learner-keyed;
    no learner id is stored). The admin reports page lists the top 50. That list is the
    ingest queue.
* **Coverage is stated, not implied.** The field's helper reads "We know 1,039 of College
  Board's 1,921 Math question IDs. For any other, paste the question." The numbers come from
  `GET /api/types` → `cb: {known, bank: 1921}`, so they update as the ingest lands.
* **Closing the gap (T-bank, task `cb-ingest`).** Export the remaining College Board Question
  Bank Math questions as PDFs (the bank is public, and each export carries the Question ID,
  the skill and the key) into `material/`. Then run the existing `tools/extract_material.py`,
  which writes `material/keys/<topic>.json` and refuses a topic whose image and key counts
  disagree. Transcribe the new items into `material/transcripts/`, and re-run the `Source`
  rebuild survey. Target: every Math ID in the bank. Acceptance 3's floor is then raised to
  the new count.
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
  * A "Not in our set yet" row has a skill select in place of the type. Once a skill is
    picked, it joins the follow-up set as a skill-level miss, exactly as a Bluebook grid cell
    does (2 fresh questions of that skill's missed, then never-met, types).
  * The table's footer states the split: "23 matched · 7 we don't have yet: pick their skills
    to include them".
* Two buttons: **Add 23 to my mistakes** and **Practise all · 2 each**.

**Rules.** The official item itself is never shown: only its type and our generated twins.
Transcripts are used as an index only. Responses never carry official stem text.

**Data and endpoints (F5 `server/types.py`, `api_bank.py`).**
* `GET /api/types/match?id=` and `POST /api/types/match {text}` → `[{template, topic, skill, score, via: 'id'|'text'|'label', example}]`, top 3. An ID outside the map returns `[{via: 'none', cb_id}]` and increments `cb_unknown`. Rate limit 60 an hour per learner.
* `GET /api/types` adds `cb: {known, bank}`.
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
7. `GET /api/types/match?id=ffff0000` (not in the keys) → 200 with
   `[{via: 'none', cb_id: 'ffff0000'}]`, never `[]`, and `cb_unknown.n` for that ID is 1.
   The sheet shows "We don't have ffff0000 yet", the text box has focus, and the skill chips
   are visible.
8. `GET /api/types` → `cb.known` equals the number of distinct IDs in `material/keys`
   (1,039 today), and the helper text prints that number.
9. `POST /api/mistakes/import` with 2 known IDs and 1 unknown → 3 rows, one with
   `matched: false`. Picking a skill for it adds that skill's 2 questions to the follow-up
   set.

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
  No screenshot needed." Files sit behind "Add files".
* **Files** (changes R17's limits; at least what theirs takes, which is 10 × 50 MB):
  * Up to 10 files: PNG, JPEG and WebP stills (downscaled in the browser to 2000px, 10 MB
    cap after that), GIF sent as-is up to 50 MB, and screen recordings `video/webm` and
    `video/mp4` up to 50 MB each. 200 MB per report in all.
  * **Record screen** (where `navigator.mediaDevices.getDisplayMedia` and `MediaRecorder`
    exist, so desktop browsers): one tap records up to 60 s as WebM with a visible
    "Recording 0:12 · Stop", and the clip joins the list with its size. Nothing records
    without the browser's own share prompt.
  * Each file row shows its name, size and a remove ×. A file over its cap is refused in the
    row with the reason ("This GIF is 62 MB. The limit is 50 MB.") before anything is sent.
  * Server: the upload is streamed to `server/reports/{id}/` in chunks and stopped past the
    type's cap (413 `{file, limit}`). Any other type → 415. The admin page plays videos and
    GIFs inline.
* **Typo or display** and **Figure or table wrong** send without details: Report → chip →
  Send, 2 taps.
* **Me too**. When an open report exists on the same (template, seed), or on the same template
  and category in the last 30 days, the modal shows "Reported by 2 others · Being checked"
  and offers **Add me to it** in place of a duplicate.
* **Breadcrumb**. `UI.api` and `UI.shell` keep the last 10 actions in memory (page path,
  control label, API path and status). They are listed under "Include device details › Show",
  sent only with that box, and never stored on the device.

**What the check can and cannot see.** `satbank.registry.generate()` already audits every item
(`verify=True`) before practice, drill, daily and blueprint serve it. So on a served item the
separate solver agrees by construction: it re-derives the answer from `item.params`, not from
the stem, the figure or the option text. The key errors that can still reach a student are
those it cannot see: a stem that asks for the diameter while the params compute the radius, a
mislabelled figure, or ambiguous wording. The check is therefore worded as what it is, and it
needs a second, independent signal before it tells anyone they were wrong.

**The instant check** (only where the verdict has been shown; R19 and §2.10's live-sitting rule
still apply). `POST /api/report` with `key_wrong` regenerates the item from the stored
(template, seed) and gathers:
* `satbank.audit.audit(item)` and `check_item(item)`, over the numbers and the structure;
* `scoring.is_correct` on the stored answer under today's rules;
* **the Strong-student signal**, `reports.pick_rate(template, norm)`. The reported option is
  identified by its reason's norm, because option letters move between seeds. Over the last
  180 days of first-try answers on this template, it compares:
  * `strong`: the share of answers from learners who are currently Strong in the skill that
    picked an option with that norm (`n_strong` answers);
  * `base`: the same share over all learners.

The outcomes are tried **in this order**, and the first that applies wins:

| # | outcome | when | the modal says | what the server does |
|---|---|---|---|---|
| 1 | `broken` | `audit` or `check_item` fails on this seed | "You found a broken question. It no longer counts against you, and nobody will be served it again." | `disputed = 1` for good; `quarantine(template, seed)`; flagged at the top of admin |
| 2 | `remarked` | the stored answer is marked wrong, but is accepted today | "You were right. 0.6667 is accepted, so this now counts as right." | The attempt is re-marked right (`progress.remark`). The trap it opened closes if nothing else holds it open. Status `fixed`, `closed_how 'auto'` |
| 3 | `forms` | a grid-in refused by the entry rule | "Your 0.66 is too short. Grid-ins accept 2/3, .6666 or .6667 (the fourth-digit rule)." | Nothing yet |
| 4 | `unsure` (signal) | `n_strong ≥ 20` and `strong > 2 × base` | "Our solver gets B from the numbers, but students who are strong in Circles pick C here far more often than usual (31% against 9%). That points to the wording or the options. A person will check it, and it doesn't count against you meanwhile." | Status `new`, sorted first in admin, with `check.signal {strong, base, n_strong}`. `disputed = 1` while open. It uses none of the 5 dispute slots |
| 5 | `unsure` (thin) | `n_strong < 20` | "The numbers check out with our independent solver: it also gets B (12). C matches a known slip: using the diameter as the radius. Too few strong students have answered this kind of question for us to rule out a wording problem, so a person will check it." Then the rationale steps | Status `new`, with the reason attached. It is not disputed unless the student ticks the box |
| 6 | `explained` | an MC pick whose option has a named reason, `n_strong ≥ 20` and `strong ≤ 2 × base` | "The numbers check out with our independent solver: it also gets B (12). C is what you get if you used the diameter as the radius, and students who are strong in Circles rarely pick it. If the wording, the figure or the options are what's wrong, send it to a person." Then the rationale steps | Nothing yet |
| 7 | `unsure` | none of the above | "We couldn't confirm this automatically. A person will check it." | Status `new`, sorted first in admin |

* **Categories about the stem, the figure or the options always go to a person**, with no
  instant check and no lesson: Figure or table wrong, Typo or display, "No right answer, or two
  right answers", and The named mistake doesn't fit. Their check still runs and is attached
  for the reviewer, but the student sees only the Thanks screen.
* The `explained` text never says "Checked" or "correct" on its own. It names the two things
  that were checked: the numbers, and how strong students answer.
* After `forms`, `explained` or `unsure (thin)`, three buttons:
  * **That makes sense** (`POST /api/reports/{id}/accept`) → status `no_change`. It uses none
    of the 5 dispute slots.
  * **The wording or figure is wrong** → send to a person with the category moved to "Figure
    or table wrong" or "Explanation unclear" (a chip pair), the check attached.
  * **Still wrong: send to a person** → the spec's dispute, with the "don't count it" checkbox
    and the check result attached.
* In a live sitting nothing is checked. When the sitting ends, the check runs and posts an
  inbox item, "Report #123 checked" (U25).
* `ponytail:` the signal is template-wide, not per seed. A seed-specific wording bug in one
  seed of a sound template shows only as `unsure (thin)` or through me-too merges. Add a
  per-seed rate if admin finds such bugs slipping through.

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
1. A finished drill miss on an MC question whose option C has a reason, on a template seeded
   with 20 Strong learners' first-try answers (1 of them on C's norm) and 100 others (15 on
   it). `POST /api/report {category:'key_wrong', answer:'C'}` → `check.outcome ==
   'explained'`, `check.reason` equals that item's `reasons[2]`, and `check.text` contains
   "numbers check out" and not "Checked:". The attempt's `disputed` stays 0. After
   `/accept`, GET /api/reports shows status `no_change`, and a 6th key report is still
   allowed.
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
7. A fixture whose stem text contradicts its params (the stem asks for the diameter; the
   params compute the radius), with no answers on file → `check.outcome == 'unsure'` (thin),
   never `explained`, and the report is status `new` in admin.
8. The same fixture with 20 Strong learners of whom 12 picked C's norm, against a base rate
   of 15% → `unsure` with `check.signal.strong == 0.6`, and the attempt has `disputed = 1`.
9. `category: 'figure'` on any question → no lesson text in the response, and status `new`.
10. A report with a 40 MB GIF → 200, and the file is on disk at its full size. A 20 MB
    `video/webm` → 200. A 60 MB GIF → 413 naming the 50 MB limit. A `application/zip` → 415.

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
7. **Need** (`estimate.need(target)`), which must agree with how `scoring.py` scores a
   sitting:
   * **Ceiling.** `_interpolate` tops out at 780 for a perfect paper (`ANCHORS`). A target
     above 780 returns `{reachable: false, ceiling: 780, right_of_44: 44}`.
   * **Right answers.** Otherwise invert `_interpolate` to get F\*, and report
     `right_of_44 = ceil(44·F*)` against the learner's `round(44·F)`, with the 3 skills with
     the largest gains as "where the missing ones are".
   * **Routing.** `section_score` caps a lower-route band at `LOWER_ROUTE_CEILING` (580), and
     `route_after` routes up only at `ROUTE_UP_AT` (0.60) of module 1. So for a target above
     580, `m1_min = ceil(0.60 × 22) = 14` (read from the constants, never typed), else
     `m1_min = null`.
   * Returns `{target, reachable, ceiling, right_of_44, now_of_44, m1_min, where: [topic]}`.

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
* Each row's evidence follows the one ladder in U5: no gain is shown below 5 answers, and a
  rough row's gain carries the "rough" tag.

**The target is a 1600 total** (changes §3.3; R15 already stores `target`, `rw_now` and
`rw_target`, and Today and Plan already show the total):
* Me's Goals card Target row reads "Target **1400** = Math 700 + R&W 700 (your estimate)".
  With no `rw_target` it reads "Math target 700 · Add your R&W target for a total".
* The Snapshot's band line adds "SAT total 1130–1210 · R&W 610 (yours)" when `rw_now` is
  set (or an added outside score carries R&W), in Today's wording.
* `summary.goals = {total: {target, now_low, now_high} | null, subjects: {math: {target, band},
  rw: {target, now, source: 'yours'}}}`. Me, Today and Plan all read it, so one edit shows
  everywhere.

**Target popover** (changes §3.3):
* Two parts, each a slider 200–800 in tens with chips, and the total above them, live:
  "Total 1400". Save sends `PUT /api/me {target, rw_target}` (and `rw_now` when changed).
* **Math**: "What 700 takes: about 37 of 44 right, with at least 14 of 22 in module 1 to
  reach the harder module 2. You're near 31. The 6 you're most likely missing are in
  Circles, Probability and Nonlinear functions." For a target of 580 or less the module-1
  clause is left out. Above 780: "Our score model tops out at 780 for a perfect paper; a
  780 puts 800 inside your band." The helper links `/help/#routing`.
* **R&W**: "Your R&W now" (a number or "Not sure") and the R&W target. The line reads "R&W
  is your own estimate for now. Words is our first R&W piece; R&W practice comes later."
* The live pace line from S7's `plan.pace(target, exam, estimate)`: "45 days · 31 study days ·
  about 22 points a week · Ambitious".
* When the tag is Ambitious or harder, one chip moves the date: "Dec 5 makes it Steady".
* Once the target is reached: "Raise to 750?". "Reached" reads the latest band (R16's
  estimate), never the projection.

**Exam-date chips** add the projected midpoint from U9, "Dec 5 · ~690", only when a projection
exists and its half-width on that date is 80 or less. Otherwise the chip shows the deadlines
alone.

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
   * `need(700).m1_min == 14` and `need(560).m1_min is None`;
   * `need(800).reachable is False` and `need(800).ceiling == 780`;
   * for every target from 200 to 780 in tens, `scoring._interpolate(right_of_44 / 44) >=
     target`, and `(right_of_44 − 1) / 44` falls short of it;
   * `scoring.route_after(m1_min, 22) == 'upper'` and `route_after(m1_min − 1, 22) ==
     'lower'`.
3. A learner with 12 answers: `gains == null`, and the card shows "Answer 30 questions".
4. The target popover for 700 contains "of 44" with an integer from 0 to 44, and "14 of 22 in
   module 1". For 560 it has no "module 1" text. For 800 it names 780.
5. `PUT /api/me {target:700, rw_target:700}` → `summary.goals.total.target == 1400`, and
   `/`, `/plan/` and `/me/` all render "1400".

#### U5. Measured or rough: every skill says how far to trust it, and a 12-question Sharpen

*From: outcomes #10, the outcomes skills gap (trend, fading), the experience "last 5" gap. Effort S–M. Builders: F4 (evidence, trend and last 5 in `board()`), S1 (UI), F5 (source `probe`), S4 (the summary's "what changed").*

**Why.** Coaching is only as good as its measurement. With a wrong picture of weak and
strong, sessions go to known skills while real gaps go unmet. Probing the least-measured,
highest-weight skills gets the most information per question. Theirs shows "LOW CONFIDENCE"
in red with no way to fix it.

**Rows** (each Skills row, and the shared `UI.skillRow`):
* **Evidence**: one ladder, over first-try answers in the mastery window (R8 counting), used
  by Skills, U4's gains, Results and the share view:

  | answers | label | bar | U4 gain |
  |---|---|---|---|
  | 0 | "Not started" | empty | hidden |
  | 1–4 | "Not measured yet · try 5" (a link that starts 5 on the skill) | solid, no ± | hidden |
  | 5–9 | "rough · 6 answers" | a dashed ± extension | shown, tagged rough |
  | 10 or more | "measured · 26 answers" | solid | shown |

  `UI.skillRow` owns the ladder (`UI.evidence(n)`), so no page words it differently. U4's
  shrinkage constant (`EVIDENCE = 10`) and the 10-answer "measured" step are the same number
  on purpose. For Sharpen, the coach and Up next row 7, "still rough" means any skill below
  the measured rung (under 10 answers).
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
* A new student sees "Take a module · 22 q" and Sharpen side by side, in U1's new-student
  order (neither ends in a sign-up form).

**Summary** (S4). After a probe, the summary's first block reads "What changed: Probability
rough → Learning (the coach now includes it). Circles rough → Strong (the coach will skip
it)."

**Coach** (F4). A rough skill gets one probe item group before the coach assigns it a full
set (coach reason `probe`).

**Data.** `/api/me/summary.subjects.math.domains[].skills[]` adds
`{evidence, trend14, last5: [1,0,1,1,0], fading, last}`.

**Acceptance.**
1. A learner with 6 circles answers: the circles row contains "rough · 6 answers". With 4 it
   contains "Not measured yet · try 5" and no gain. With 0 it reads "Not started". With 26
   it contains "measured".
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
* Nothing marks the trap before the student answers. Each answer still gets its verdict at
  once, as every fixing drill does (U15).
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
* `/api/me/summary.subjects.math.habits: [{id, name, tell, misses, skills: [topic], trend}]`.
  `habits.py` families carry a `subject` (all `math` today), so an R&W family list is
  additive.
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
* `/api/me/summary.subjects.math.coverage` becomes `{readiness, met, total, types: {template: {met, right, last, open}}}`.
  `GET /api/types?subject=math` scopes the weights, so they sum to 1 within a subject.

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

* **Projection** (`estimate.projection(learner, to_day)`, F4, pure, with `assert`s in
  `estimate.py __main__`):
  * **Enough data.** It needs at least 3 scored standard sittings in the last 90 days, and
    the first and last of them at least 21 days apart. Otherwise it returns `null`.
  * **Slope.** A least-squares fit of band midpoints against weeks gives `b`. It is shrunk
    toward no change by the evidence: `b' = b × n / (n + 3)` (n = sittings). So 3 sittings
    count half.
  * **Anchor.** The shrunk line through the mean, read at the last sitting:
    `ȳ + b' × (x_last − x̄)`.
  * **Diminishing returns.** Over the w weeks to the exam, the gain is
    `b' × min(w, 4) + clip(b', −20, 20) × max(w − 4, 0)`. So after week 4 it moves at most 20 a
    week, either way. The midpoint is clipped to 200–800.
  * **Cone.** Its half-width is the latest band's own half-width plus the fit's prediction
    error at the exam date: `s × √(1 + 1/n + (x₀ − x̄)² / Sxx)`, where s is the residual
    standard deviation (n − 2 degrees of freedom). It is rounded to 10, at least 60 and at
    most 150. A constant is never used.
  * **Label.** "If this pace held: 550–670 on Nov 7". It never says "At this pace" or "You
    will".
  * **Where it shows.** The trend chart shows the cone at any width. The exam-date chips (U4)
    and the target popover's pace line show the midpoint only when the half-width is 80 or
    less.
  * With too few sittings there is no cone, and a line reads "Three modules over three weeks
    start a projection."
  * `ponytail:` a shrunk, tapered linear fit. Replace it with a fitted growth model once
    enough learners have sat both a module and the real SAT to calibrate against.
* **Pace line**: a dashed line from the plan's starting estimate (`plans.start`) to the target
  on the exam date, when a plan exists.
* **What changed**: hovering or focusing the gap between two adjacent sittings shows "Sep 12 →
  Sep 20: 212 questions · 3h 40m · 11 mistakes fixed · Circles → Strong · +40". It is computed
  by the server from `progress.days` and the traps closed between the two finish times
  (`summary.subjects.math.score.gaps[]`). The biggest-gain gap is labelled once on the chart.
* The chart's hidden table gains "Projected" and "Pace" rows.

**Acceptance.**
1. Sittings at midpoints 500 (Sep 1) and 560 (Sep 15), exam Nov 7 → `projection == null`,
   and the chart reads "Three modules over three weeks start a projection."
2. Add a third at 600 (Sep 22), which is a raw slope of about +33 a week. Then
   `projection.mid < 700` (the formula gives about 683), the SVG has a cone path, and the
   hidden table has a "Projected" row. An unshrunk line would have said about 790.
3. Sittings 500 (Sep 1), 530 (Sep 11), 560 (Sep 22), exam Nov 7 → `mid` about 611 and
   `half == 60`. The Nov 7 chip reads "~610".
4. Sittings 500 (Sep 1), 560 (Sep 15), 540 (Sep 29) → `half > 80`, and no exam-date chip
   carries a "~" figure.
5. `python3 server/estimate.py` asserts that a flat series projects its own mean, and that
   no projection moves more than 20 a week after week 4.

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
  `summary.stats.delta`, cross-subject. The outcome strip's first two figures read
  `subjects.math`.

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

A new line, **Country** (their Country Rank, kept): "United States **#14** of 96", shown when
`learners.country` is set. It reads Compete's practice board with the Country scope (S8,
R12), with the same movement and gap. When the country is blank the line reads "Add your
country to see your country rank", and **Add country** opens a small popover right there:
* a searchable select of ISO 3166 countries (names from `Intl.DisplayNames`), blank by
  default;
* above it, one suggestion chip from the browser's region
  (`new Intl.Locale(navigator.language).maximize().region`): "United States?". It is only a
  suggestion; nothing is set until the student picks;
* the helper "Shown on the Country board. Change or clear it in Settings › Account &
  devices.";
* Save sends `PUT /api/me {country}` (422 on a code outside ISO alpha-2), and the line
  renders the rank at once.

The same control sits in **Settings › Account & devices › Boards**, next to "Show me on
boards" (R12's `learners.board`) and the board name (U29), with **Clear**. Nothing detects a
location: the country is optional and set only by the student.

A new line, **Climb**: "Started 440–600 · +90 · ahead of 74% of 212".
* The cohort is learners whose first scored standard sitting's midpoint is near yours. The
  window widens step by step until the cohort holds at least 20 (R16's rule): ±40, then ±80,
  then ±160, then everyone with a first sitting.
* The line states the window it used: "Started 440–600" for ±80 around 520, or "Everyone who
  has sat a module" at the last step.
* The metric is R16's `mean3` midpoint minus that first midpoint.
* It is hidden only when fewer than 20 learners have a first sitting at all. Board visibility
  (R12) applies.
* `compete.climb(learner)` returns `{rank, of, window, lo, hi}` (`window` = 40 | 80 | 160 |
  null for everyone).

A new line, **You, N days ago**: "You, 30 days ago: +60 est. · 2 skills to Strong · 9 mistakes
fixed". It shows from day 8 of history. N is the history available, up to 30 ("You, 8 days
ago" on day 8). The estimate part appears only once both ends have a scored sitting.

**Acceptance.**
1. 20 seeded learners with first midpoints within ±40 and varied gains: `ranks.climb.of == 21`
   for a 21st, `window == 40`, and its rank is ordered by gain.
2. With 14 within ±40 and 8 more within ±80 → `window == 80`, `of == 23`, and the line reads
   "Started" followed by the ±80 range.
3. With 19 learners holding a first sitting in all, `ranks.climb == null`.
4. The gap line's number equals the next row's `right` minus yours, plus 1.
5. With `country = 'US'` set → `ranks.country` exists and its `of` equals the US practice
   board's size. With it blank → the "Add your country" line, and choosing a country in its
   popover sends `PUT /api/me {country}` and renders `#n of m` without a reload.
   `PUT /api/me {country:'XX'}` → 422. Settings › Account & devices has the same select.
6. A learner with 8 days of history → `ranks.self.days == 8`, and the line reads "You, 8
   days ago". With 7 days → `ranks.self == null`.

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
* **Data.** `/api/me/summary.subjects.math.levers: {key: {how, help, inputs: [...], next, start?}}`
  for subject figures (mastery, readiness, band, points, rank); `summary.stats.levers` for the
  cross-subject ones (streak, study time). Achievement tiers that count skills or types come
  from `catalogue.by_topic(subject)`, so Explorer's top tier is the served type count, not a
  typed 386.

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

**The sheet.** On the first clean shell page load of the student's week (`prefs.week_start`,
local day) a sheet opens, titled "Your week, Sep 14–20". It follows U25's one-sheet rule: it
never opens on a load that came through a link, and it absorbs the welcome-back block when
both are due. It can be dismissed, and reopened from Me › This week.
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
* The sidebar **Profile** item's meta (U26): "1/3" in DM Mono, with the pips and the goal
  names in its tooltip. The same shows on the menu sheet's account header. It stays out of
  the Today card, so the chrome states it once and the card stays short.
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
4. The sheet opens once per week per device, and never on `/practice/session/` or `/test/`,
   nor on a load with a query or a hash (U25 acceptance 4).

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

**Which drills the bundle governs** (F5's drill resolver, one table `prefs.MODE_SOURCES`):
* **Governed** by the resolved mode or stage: sets the student builds (the Practice builder
  and "Practise {skill}" links), Up next `skill` and `probe` rows, Sharpen, and the time box
  (`source: 'next'`, `box`).
* **Always instant**: `redo`, `checks`, `habit`, `gauntlet`, `quick`, `inline` (R24), the
  pacing and speed drills of U7 (they set their own clock), and the week-goal drills. They keep `feedback: 'instant'`, `repairs: 'next'` and
  `rationale: 'miss'`, whatever the stage. A student who fixes a named mistake three weeks
  before the exam sees the key after each answer.
* Tests and challenges are never governed; they have their own rules.
* The builder shows which applies: a governed set's summary line reads "Test-like · key at
  the end"; a fixing drill's reads "Fixing · key after each".

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
5. With `exam_date` = today + 10: `POST /api/drill {pool:'redo', ids:[x]}` → `cfg.feedback ==
   'instant'` and `cfg.repairs == 'next'`, and the first answer's response carries the key
   and the verdict. `POST /api/drill {topics:['circles']}` from the builder → `cfg.feedback
   == 'end'`. The same holds for `checks`, `habit`, `gauntlet` and `quick`.
6. On /me/, Learning preferences has a "Words a day" row that writes `words_goal`, and a
   "Test timing" row that writes `test_timing` (§3.1 override 22).

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

*From: outcomes #12, unfair-advantage #12. Effort S for (a), L for (b); both in the core waves. Builders: S7 (the feed, the render link, the recurring `.ics`), F2 (`?next=1`, `web/sw.js`), S1 (`server/push.py`, the Settings row, the Subscribe sheet).*

**Why.** Spacing only works if the due day is met. A specific, small, time-stated nudge ("about
4 min") beats a generic alarm. Their "Preferred time: Evening" does nothing.

**Why calendars alone are not enough.** Google Calendar ignores VALARM in feeds added by URL.
Apple Calendar's subscribe dialog removes alerts by default. Subscribed feeds refresh only
every several hours, so a title such as "3 check-ins + Circles · 25 min" goes stale. So push
ships in the core build, and each calendar path is set up so that it actually alerts.

**(a) Calendar.**
* **Feed events are titled generically**: "SAT Math · Up next · 25 min" on study days,
  "SAT Math · Module" on test days. What is due is worked out when the student opens it. The
  DESCRIPTION reads "Open to see what's due now: {BASE_URL}/?next=1" (U1), so a stale feed
  never states a wrong count. Registration and scores-release events (U17) keep their
  specific titles, because those are fixed dates.
* **The Subscribe flow** (Settings › Study and Plan step 3) is a small sheet with one tab per
  platform, each with the step that turns alerts on:
  * **Google**: "**Add to Google Calendar**" (recommended). It opens
    `https://calendar.google.com/calendar/render?action=TEMPLATE&text=SAT+Math+·+Up+next&dates=…&ctz={tz}&details=…/?next=1&recur=RRULE:FREQ=WEEKLY;BYDAY={study days}`.
    It creates a native recurring event, so the student's default notifications apply. Or
    subscribe to the feed, with the step "Settings › {this calendar} › Event notifications ›
    Add notification".
  * **Apple**: "Subscribe", with the step "In the dialog, untick **Remove Alerts**". Or
    **Download** a single recurring `.ics` with its VALARM; an imported event keeps its
    alert.
  * **Outlook and others**: Download (imported events keep alerts), or subscribe and add a
    reminder in the calendar's own settings.
  * The sheet ends with "Test it: we'll put an event 2 minutes from now" (a one-off `.ics`
    or render link), so the student hears the alert before relying on it.
* The plan's days change the recurrence: `BYDAY` follows the plan's study weekdays. The
  Settings row reads "Recurring Mon–Fri at 19:00 · update" once the plan's days change.

**(b) Push, in the core build** (after F2's shell, in S1's wave), on every browser that
supports Web Push: the installed app, and desktop Chrome, Edge, Firefox and Safari.
* **Keys.** With `SATF_VAPID_PUBLIC` and `SATF_VAPID_PRIVATE` unset, `server/push.py`
  generates a P-256 key pair on first start and keeps it next to the database in
  `server/vapid.pem` (mode 0600; `.gitignore` gains `server/*.pem`), so push works with no
  setup. The JWT `sub` is `SATF_BASE_URL`. `SATF_PUSH=off` hides
  everything.
* **Asking.** The browser's permission prompt only ever follows a tap: "Notify me on this
  device" in Settings › Study, and one offer, "Want a nudge at 19:00?", right after the
  student sets a preferred time (Plan step 3 or Settings). It is never shown on page load.
* **Settings**: Settings › Study gets "Notify me on this device" (on iOS it needs the
  home-screen app; the row says so and links to `/help/#install`). Kinds, each a switch:
  * study reminders (on), sent at the student's own `study_time − remind`, whatever time
    that is;
  * "one question keeps your streak" at 20:30 on an unfinished study day (off);
  * "a private contest you joined closes in 3 hours" (on; only when Compete exposes
    `closing_soon`).
* **Quiet hours** hold back only the nudges the student didn't time themselves (the streak
  nudge and the contest nudge; one that falls inside is sent at the window's end if still
  relevant, or dropped). They **never** hold back the study reminder the student chose: a
  22:00 study time rings at 22:00 less `remind`.
  * A row under the kinds shows the window and edits it: "Quiet hours 21:30 – 7:00 ·
    Change", two `<input type="time">` fields and Off. Stored in a new pref `quiet`
    (`{from, to}` local times, or null for off; default `{from:'21:30', to:'07:00'}`).
  * When the study time falls inside the window, the row says so: "Your 22:00 reminder still
    rings. Quiet hours only hold back extra nudges."
* **Service worker**: `web/sw.js` handles `push` and `notificationclick` only, with no fetch
  handler and no caching.
* **Payload-less pushes**. The worker calls `POST /api/push/next {endpoint}` for the text,
  worked out at send time from `next.queue` ("3 check-ins due · about 4 min"), so it is never
  stale. A tap opens `/?next=1&from=push`.
* **VAPID**: an ES256 JWT signed with `cryptography`, so no new dependency.
* **Scheduler**: an in-process asyncio loop every 5 minutes sends at `study_time − remind` on
  study days not yet done. At most one per kind a day, and every notification carries a Stop
  action.
* **Table**: `push_subs(id PK, learner, endpoint UNIQUE, p256dh, auth, kinds JSON, created,
  last_sent)`. `progress.carry`, export and delete cover it.

**Acceptance.**
1. (a) For a learner with 3 check-ins due tomorrow, tomorrow's VEVENT SUMMARY is "SAT Math ·
   Up next · 25 min" (no count), and its DESCRIPTION contains "/?next=1".
2. (a) The Google button's URL contains `action=TEMPLATE`, `ctz=` and
   `recur=RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR` for a Mon–Fri plan. The downloaded `.ics` has
   one VEVENT with an RRULE and a VALARM.
3. (b) With the VAPID env unset, the first start writes `server/vapid.pem`, and
   `GET /api/push/key` returns a public key. With `SATF_PUSH=off`, `/api/push/*` → 404 and
   Settings shows no row.
4. (b) A subscription row is created, and `POST /api/push/next` returns text naming the
   first Up next item. After that item is done, the next call names the new first item.
5. (b) No page calls `Notification.requestPermission()` outside a click handler (a check
   greps `web/**` for the call and asserts each one sits in a listener).
6. (b) With `study_time` 22:30, `remind` 10 and the default quiet hours, the scheduler (a
   test clock) sends the study reminder at 22:20. The streak nudge due at 20:30 with quiet
   hours `{from:'20:00', to:'07:00'}` is not sent inside the window.
   `PUT /api/me {prefs:{quiet:{from:'23:00', to:'06:30'}}}` → 200, and `{from:'25:00'}` → 422.

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
    * `user.name` = the student's name (U29), or the board name when the name is blank;
    * `residentKey: 'required'`, `userVerification: 'preferred'`, algorithms −7 and −257.
  * The client posts `response.getPublicKey()` (SPKI DER, so no CBOR parsing),
    `getPublicKeyAlgorithm()`, `getAuthenticatorData()`, `clientDataJSON` and the transports.
  * Toast: "Saved. This passkey signs you in wherever your passwords sync." This browser
    gets its own device token in the same response (U21).
  * The email code stays as the quiet alternative.
* **Signing in.**
  * `/signin/` opens on the method this device used last (`localStorage satf.lastMethod`:
    `passkey` | `phone` | `email` | `code`, written on each successful sign-in). A URL hash
    wins over it. With neither: **Passkey** when
    `isUserVerifyingPlatformAuthenticatorAvailable()` is true, otherwise **Use your phone**.
    An email-only student is taken straight to Email from their second visit on.
  * **Autofill (conditional mediation)**, fully specified:
    1. The email field has `autocomplete="username webauthn"`.
    2. On `/signin/` load, when `PublicKeyCredential.isConditionalMediationAvailable?.()`
       resolves true, the page sends `POST /api/passkey/login/options {conditional: true}`
       → `{challenge, rpId, timeout, expires}` and calls
       `navigator.credentials.get({mediation: 'conditional', publicKey: {challenge, rpId,
       allowCredentials: [], userVerification: 'preferred'}, signal})` with an
       `AbortController`.
    3. **Refresh.** 30 s before `expires` (the challenge's 5 minutes), and on
       `visibilitychange` back to visible after it, the page aborts that request, fetches new
       options and calls `get()` again. So a sign-in page left open for an hour still works
       from autofill.
    4. Picking a passkey from autofill posts the assertion to `POST /api/passkey/login`, as
       the button does.
    5. The **Sign in with a passkey** button first aborts the pending conditional request
       (the browser allows one `get()` at a time), then calls a modal `get()` with no
       `allowCredentials`.
    6. `SATF_WEBAUTHN_TTL` (seconds, default 300) sets the challenge lifetime, so a test can
       shorten it.
  * A school Chromebook with no synced passkey gets the browser's own "Use a phone" QR, and
    **Continue with Google** when the deploy has it (U19b), which is how most school
    Chromebooks are already signed in.
* **Email is a launch requirement, and says when it is off.**
  * SMTP (`SATF_SMTP_*`) is on the production checklist in the README's run section. Without
    it, codes land only in `server/outbox/`, which serves no student.
  * `GET /api/health` adds `mail: 'smtp' | 'outbox'`.
  * When `mail == 'outbox'`, the Email tab and "Save progress by email" don't offer a code
    that will never arrive. They read "Email codes aren't switched on for this site yet.
    Sign in with a passkey, your phone or Google, or use a transfer code from a signed-in
    device.", with those as buttons, and the save nudge offers only the passkey (and Google).
    Admin's header shows "Mail: outbox (codes are not sent)".
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
  * Login returns a device token (U21), then runs **the carry choice** below. The toast is
    "Signed in as Dana · 24 answers added" or "Signed in as Dana".
* **Managing.**
  * Settings lists each passkey: "iCloud Keychain · created Sep 23 · last used today"
    [Remove].
  * Removing the last way to sign in asks for a confirm.
  * The recovery line reads "You can sign in 3 ways: passkey, email, Google" (Google only
    when U19b is on). With one way only, it shows an orange dot and "Add a passkey or email".
* **The carry choice** (every sign-in path: passkey, Google, phone approval, email code or
  link, and the transfer code). It replaces v2's silent carry, because the browser may hold someone
  else's anonymous answers: a library computer, or a sibling's laptop.
  * When this device's own learner has 0 answers, nothing is asked.
  * Otherwise, after the account is known and before the reload, one step reads: "This
    device has 24 answers, answered here since Sep 21." It offers two choices:
    * **Add them to Dana's**: `progress.carry(this, Dana)`;
    * **Don't add them**: nothing moves.
  * The default choice (focused, and taken by Enter) is Add only when both hold: "This is a
    shared computer" is not ticked, and the newest local answer is under 24 hours old.
    Otherwise it is Don't add. A shared-computer sign-in never offers Add at all: its line
    reads "This computer's 24 answers stay separate."
  * **Don't add them** keeps those answers reachable. On a shared computer the session token
    lives only in sessionStorage (U21), so `satf.learner` is never touched and the anonymous
    code is still there when the session ends. On any other device the old code is parked in
    `satf.profiles` as "Student 4F2A · 24 answers · not saved", listed under Students on
    this device (U21), so nothing is lost.
  * The server never carries by default. Every sign-in endpoint takes `carry: true | false`
    and treats a missing value as false.
* **Counts as saved: one function.** `account.saved(learner)` (S1) is true when the learner
  has a passkey, a verified email (`users.learner` with a verified login) or a Google link
  (U19b). Every "saved" test in the site calls it, never `sessions.user_id` or `users`
  directly:
  * the user card, the save nudge, the unsaved callout and the Leave-this-device dialog;
  * a:-code retirement and the swap (U21);
  * **the diagnostic's results gate** (R38, `server/app.py`'s `403 {need: 'signup'}`):
    `results` returns 200 when `account.saved(learner)` holds. An email-saved learner's
    diagnostic session gets `sessions.user_id` bound to their `users` row when it starts; a
    passkey-only learner's stays null and is let through by `account.saved`. Either way no
    name-and-email form is shown to a saved learner. The form stays for unsaved learners
    while R38 keeps the gate (Part 5 question 8).
* **Tables** (F4):
  * `passkeys(cred_id PK, learner, user_handle, spki BLOB, alg INTEGER, sign_count INTEGER, label, created, last_used)`;
  * `webauthn_challenges(challenge PK, learner, purpose, expires)`.
  * `carry`, export (without keys) and delete cover passkeys.
* **Deploy.** `cryptography` must be on the production host. The README's run section lists
  it, since the repo has no requirements file.

**Acceptance.**
1. `server/checks/s1.py` registers a credential made with `cryptography`'s P-256 key, using a
   hand-built `authData` and `clientDataJSON`, then logs in with a valid signature →
   `{learner}`.
2. The same login with a wrong origin → 400, a reused challenge → 400, and a bad signature
   → 401.
3. After registering, `GET /api/account` shows `saved: true` without an email. That
   passkey-only learner finishes a diagnostic, and its results endpoint → 200 with no sign-up
   form rendered. An unsaved learner's → 403 `{need: 'signup'}`.
4. The `/signin/` field has `autocomplete` containing `webauthn`. In Chrome with a CDP
   virtual authenticator (`WebAuthn.addVirtualAuthenticator`, internal, resident key, user
   verification) holding a registered credential, loading `/signin/` sends one
   `/api/passkey/login/options` with `conditional: true`, and completing the conditional
   request signs in (`satf.learner` starts `d:`). With `SATF_WEBAUTHN_TTL=10`, a second
   options call is sent before 10 s have passed.
5. A sign-in with "This is a shared computer" ticked, on a device whose learner has 24
   answers, leaves the account's attempt count unchanged (`/api/me/summary` before and
   after), offers no Add, and leaves `localStorage satf.learner` unchanged.
6. A non-shared sign-in whose newest local answer is 30 h old focuses **Don't add them**.
   Choosing Add raises the account's attempt count by 24. `POST /api/passkey/login` with no
   `carry` field moves nothing.
7. After an email-code sign-in, a fresh visit to `/signin/` (no hash) opens on the Email
   tab.
8. `GET /api/health` has `mail`. With `SATF_SMTP_HOST` unset it is `'outbox'`, and the Email
   tab shows the "aren't switched on" text with a Passkey button and no code form.

#### U19b. Continue with Google, when the deploy has a client ID

*From: the skeptic's sign-in finding (their only method, and how school Chromebooks are signed in). Effort S–M. Builders: S1 (`server/google.py`, `/signin/`, Settings), F4 (the `users.google_sub` column).*

**Why.** A student on a school Chromebook is already signed in to Google, while their
passkey may sit on a phone that isn't with them. Theirs signs in with Google in 2 taps. Ours
offers the same, alongside passkeys, the phone and email, and never requires it.

* **Off unless configured.** Everything here is hidden, and `/api/google*` → 404, while
  `SATF_GOOGLE_CLIENT_ID` is unset. `GET /api/health` adds `google: true | false`.
* **Where it shows**:
  * `/signin/`: a full-width **Continue with Google** button above the tabs, on every tab;
  * the save nudge and Settings › Account & devices: **Save with Google**, beside Save with a
    passkey;
  * Settings lists it as a way in: "Google · d•••@gmail.com · connected Sep 23" [Disconnect]
    (the recovery-line rules of U19 apply: disconnecting the last way asks for a confirm).
* **Client.** Google Identity Services (`https://accounts.google.com/gsi/client`) is loaded
  only on `/signin/` and Settings, on demand. `google.accounts.id.initialize({client_id,
  nonce, callback, ux_mode: 'popup', use_fedcm_for_prompt: true})` and `renderButton`. The
  nonce comes from `POST /api/google/nonce` (single use, 5 minutes, stored in
  `webauthn_challenges` with `purpose 'google'`). The callback posts
  `POST /api/google {credential, nonce, carry, session_only}`.
* **Server** (`server/google.py`, stdlib `urllib` and `cryptography`, no new dependency):
  1. Fetch Google's JWKS (`https://www.googleapis.com/oauth2/v3/certs`), cached for the
     response's `Cache-Control: max-age`, refetched once on an unknown `kid`.
  2. Check the JWT header: `alg == 'RS256'` and a known `kid`. Verify the signature with
     `RSAPublicNumbers(e, n)` and PKCS1v15-SHA256 over `header.payload`.
  3. Check the claims: `iss` in `accounts.google.com` or `https://accounts.google.com`,
     `aud == SATF_GOOGLE_CLIENT_ID`, `exp` in the future (60 s skew), `nonce` equal to an
     unused one we issued, and `email_verified == true`.
  4. **Bind.** Find the `users` row by `google_sub`, else by the lowercased verified email.
     * Found: sign in to its learner (a `d:` token, U21), after the carry choice (U19).
     * Not found: this is a save. This device's learner gets a `users` row with that email
       (verified), `first` and `last` from `given_name` and `family_name` (or the email's
       local part), and `google_sub`; the device swaps to a `d:` token (U21).
  5. Store only `sub`, the email and the names. No Google token is kept.
* **Tables** (F4): `users.google_sub TEXT UNIQUE`. `carry`, export and delete cover it.

**Acceptance.**
1. With `SATF_GOOGLE_CLIENT_ID` unset: `/api/google` → 404, and `/signin/` has no Google
   button.
2. `server/checks/s1.py` signs an ID token with a test RSA key and points the JWKS fetch at
   it: a valid token → 200 with a credential starting `d:`. A wrong `aud` → 401, an expired
   token → 401, `email_verified: false` → 401, and a reused nonce → 400.
3. A token whose email matches an existing saved user signs in to that learner, with no
   answers moved when `carry` is missing. A token with a new email saves this device's
   learner: `account.saved` is then true, and a second sign-in with the same `sub` but a
   changed email reaches the same learner.

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
    screen in front of you." It adds "Shared computer: signs out when the browser closes" when
    the request was marked shared. [Sign in] [Not me] → `POST /api/link/{token}/approve | /deny`.
  * If the phone's browser has no learner (on iOS the camera opens Safari, whose storage is
    separate from the home-screen app): "Open SAT Freshman on your phone, then Menu › Sign in
    another device, and type 482 913."
* **Finish.**
  * On approval, the computer's poll gets a device token (U21). The carry choice (U19) runs
    on the computer; with "This is a shared computer" ticked it never adds. Then it toasts
    "Signed in as Dana".
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
2. A approves. B's `GET /api/link/{token}` → `{credential}` starting `d:`, and answers B
   records with it are stored under A's learner. A second approve → 410.
3. Deny → B reads `{state:'denied'}`.
4. 11 wrong codes from one IP within 10 minutes → 429.
5. A `session_only` request approved for a learner with 500 attempts, from a computer whose
   anonymous learner has 24: the owner still has 500 afterwards.

#### U21. Devices you can see and sign out; a shared-computer mode; switch student

*From: experience #9, the unfair-advantage devices and switch-student gaps, the outcomes switch-student gap, the experience sign-out gap. Effort M. Builders: F4 (the `devices` table, `learner_of` in `deps.py`), S1 (every sign-in flow mints tokens, the Settings UI), F2 (`UI.learner`, sessionStorage mode, the menu).*

**Why.** v2 can only rotate the one shared code, which signs out every device at once. It also
treats a copyable code as the credential, so any browser that ever held it can act as the
student without showing up anywhere. A session left on a library computer stays signed in.
Siblings on one laptop mix answers into one code, which corrupts mastery, mistakes and the
coach's picks.

**Device tokens.**
* Every sign-in (passkey, Google, phone approval, email code or link, transfer code) gives
  that browser its own token, `d:` + 32 base-36 characters, never the learner code.
* **Saving turns every browser that holds the code into a device: a swap, never a cut-off.**
  A save can finish somewhere else than the browser holding the answers: the diagnostic's
  confirmation link (§3.1.5) opens in the phone's mail app with no `X-Learner`, and an
  unsaved code may have been shared with a second browser by a transfer code. So:
  * The saving request, when it carries the `a:` code, gets its `d:` token in the same
    response (`method 'save'`), and the client swaps `satf.learner` to it.
  * **The swap window.** For 14 days after the save (`learners.swap_until`), a request that
    presents the saved learner's `a:` code is served normally, and its response carries
    `X-Learner-Swap: d:…`, a new device token for that browser (`method 'swap'`,
    labelled from its User-Agent). `UI.api` stores it and uses it from then on. That
    browser appears in the devices list as "Chrome on Mac · moved to its own key Sep 23".
  * **End the old code now** (Settings › Account & devices, and a line in the save toast's
    detail) sets `swap_until = now`. After the window, or after that, `learner_of` refuses
    the `a:` code for a saved learner: → 401 `{retired: true}`, whose banner offers Sign in.
    From then on the `a:` code is a non-secret learner id.
  * The diagnostic's confirmation link verifies the email and saves the account, and never
    retires the `a:` code by itself: the laptop that sat the diagnostic keeps working and
    swaps to its own key on its next request.
  * The save toast says so: "Saved. Your other browsers move to their own key on their next
    visit."
  * Before saving, the `a:` code is still the credential, because nothing else exists.
  * `ponytail:` during the 14 days anyone holding the code can still get a key, exactly as
    before saving, and each swap shows in the devices list. Shorten the window if the list
    shows swaps the student doesn't recognise.
* `deps.learner_of` resolves `a:` (unsaved learners, and saved ones inside the swap window),
  and `d:` through
  `devices(token PK, learner, label, method, created, last_seen, session_only, expires, revoked)`,
  indexed on learner.
  * It is one primary-key lookup. `last_seen` is written at most every 10 minutes.
  * A revoked or expired token → 401 `{retired: true}` (the existing banner).
* So once the old code has ended, the devices list is complete: every browser that can act
  as the student has a row, and every row can be signed out. Inside the swap window the list
  says so under its heading: "Your old code still works until Oct 7 for browsers that
  haven't visited since you saved · End it now".

**Transfer code** (replaces the Device code's Show / Copy, §4.4).
* **Move to another device** → `POST /api/transfer` → `{code, expires}`. The code is 8
  characters from the unambiguous alphabet `A-HJ-NP-Z2-9` (`db.new_code()`, "K7P4 M2QX"),
  single use, and expires in 10 minutes ("expires in 9:41").
* On the other device, `/signin/#code` (under More) takes it:
  `POST /api/transfer/redeem {code, carry, session_only}`.
  * For a saved learner it mints that device a `d:` token, which appears in the list.
  * For an unsaved learner it returns the `a:` code: there is no account yet, so both
    browsers share it, as in v2.
* Wrong codes share the per-IP limit (10 failed lookups per 10 minutes → 429).
* A saved learner's `a:` code is never shown or copyable again. Only the unsaved "Leave this
  device" dialog still shows it masked with Copy, because there it is the only way back.

**Settings › Account & devices › Devices.**
* One row per device:
  * "Chrome on Mac · this device · active now · saved here Sep 23";
  * "Safari on iPhone · 2h ago · signed in Sep 21 by passkey";
  * "Chrome on Windows · shared computer · expires in 11h".
  Each row has [Sign out].
* **Sign out all other devices** revokes every other `d:` token and ends the old code's swap
  window, and that is all it needs to do. Nothing is rotated, because `a:` then signs no one
  in. `POST /api/account/rotate` is not built.

**Shared computer.**
* A checkbox on every `/signin/` tab. The token lives only in sessionStorage.
  `satf.learner`, `satf.profiles`, `satf.lastEmail` and `satf.lastMethod` are never written.
* The user card's second line reads "Shared computer · Sign out".
* **It ends on the server, not only in the tab**, because browsers restore sessionStorage
  with session restore and Reopen closed tab (Ctrl/Cmd+Shift+T):
  * **Idle expiry.** A `session_only` token dies after 15 minutes with no request, and after
    12 h in all. For these tokens `last_seen` is written on every request (not every 10
    minutes).
  * **Heartbeat.** A visible shell page sends `POST /api/devices/this/ping` every 5 minutes
    (a hidden tab sends none, so a tab left in the background dies at 15 minutes).
  * **Closing.** On `pagehide`, the page sends a keepalive `POST /api/devices/this/leaving`,
    which sets that token's `expires` to now + 60 s. The next page in the same tab, or any
    other open tab of the session, pings at load and restores the 15-minute idle rule. So
    moving between pages never signs the student out, and closing the last tab or the
    browser kills the token within a minute.
  * **New tabs.** A new tab (a typed URL, or a `rel=noopener` link) has empty
    sessionStorage. It asks on a `BroadcastChannel('satf-session')` and waits up to 300 ms;
    an open tab of the session replies with the token, which the new tab keeps in its own
    sessionStorage. With no reply it starts signed out.
  * A restored tab whose token has died gets 401 `{retired: true}` on its first request and
    shows the banner "This shared-computer session has ended. Sign in again." It never
    shows the student's data first: `UI.cached` copies are in the same sessionStorage and
    are cleared on that 401 before painting.
  * The user card's tooltip says it: "Shared computer: ends 15 minutes after you stop, or
    about a minute after you close the browser."
  * `ponytail:` a tab reopened within the 60 s grace comes back signed in. Shorten the grace
    if a library reports it.
* Switch student and the remembered email are hidden.
* **Sign out is immediate**: no Undo. `DELETE /api/devices/this` is sent at once, and
  sessionStorage, including `UI.cached`'s copies, is cleared.

**Sign out, saved account (not shared).**
* There is no dialog. The page moves the credential to `sessionStorage satf.undo {cred,
  until}`, clears `satf.learner`, the caches and that student's `satf.profiles` entry, and
  goes to `/`. There an 8 s toast reads "Signed out · Undo".
* **The revoke is always sent.** `DELETE /api/devices/this` (with the held token) goes when
  the toast closes, or on `pagehide` with `fetch(…, {keepalive: true})`, whichever comes
  first, and `satf.undo` is cleared. A student who taps Sign out and closes the tab still
  leaves no live token and no ghost "active" device.
* **Undo** within 8 s puts the credential back (and its profile entry) and reloads. Nothing
  was sent, so nothing needs undoing on the server.
* `ponytail:` a browser crash inside the 8 s leaves the token live until it is signed out from
  the devices list. Revoke on the server after 8 s of silence if that shows up.
* Unsaved devices keep the warning dialog.

**Students on this device** (an account-menu section and a menu-sheet group).
* **Off by default.** It appears only once the owner turns on **This is a family device**
  (Settings › Account & devices). The first tap on **Add a student** asks for it: "Let other
  students use this browser? Each keeps their own progress, and anyone here can switch to
  them." [Turn on] [Cancel]. It is stored as `localStorage satf.family = 1`, and never offered
  on shared computers.
* With it on: up to 4 learners in `localStorage satf.profiles [{cred, name, avatar}]`, each
  with its avatar and name.
  * One tap → `UI.useLearner(cred)` and a reload, with the toast "Now Maya".
  * **Add a student** keeps the current one in the list and mints a fresh anonymous code.
  * **Remove from this device** revokes that entry's token. When that student is unsaved it
    warns: "Maya's progress isn't saved. Removing forgets it on this device."
* **The one exception**: a code parked by "Don't add them" (U19) is listed even with it off,
  as "Student 4F2A · 24 answers · not saved", with Switch and Remove, so no progress becomes
  unreachable.
* **Signing out** removes that student from `satf.profiles` and revokes their token, so a lab
  PC doesn't build up a list of signed-in students. Turning the family device off revokes
  every other entry's token (a keepalive DELETE each) and removes them, after warning about
  any unsaved ones.

**Acceptance.**
1. A passkey or email sign-in returns a `d:` token. `GET /api/devices` as the owner lists it.
   `DELETE /api/devices/{id}` → that token's next PUT gets 401 with `detail.retired == true`.
2. A `session_only` token idle for 16 minutes → 401 `{retired: true}` (a test sets
   `last_seen` back), and one used within 15 minutes but created 12 h ago → 401. After
   `/leaving` with no ping for 61 s → 401; a ping within 60 s keeps it working. Two page
   loads in a row in one tab (with the `pagehide` between them) keep the session. A tab
   restored after the token died shows the "session has ended" banner and paints no cached
   card.
3. No response to a `d:` device contains the learner's `a:` code (a check greps every
   endpoint body in `server/checks/s1.py`).
4. Browser A holds `a:X` and registers a passkey. Then A's `satf.learner` starts with `d:`,
   and `GET /api/devices` lists A. Browser B, which also holds `a:X`, calls `GET /api/shell`
   → 200 with an `X-Learner-Swap` header starting `d:`, B's next call uses it, and the
   devices list shows B. After **End the old code now**, `X-Learner: a:X` → 401
   `{retired: true}`.
5. `POST /api/transfer` → `{code}`. Redeeming it on B gives a `d:` token that
   `GET /api/devices` lists. A second redeem → 410, and a redeem after 10 minutes → 410.
6. Sign out on a saved device, then fire `pagehide` within 8 s: a keepalive DELETE is sent,
   and the token then gets 401. Undo within 8 s instead → the token still works, and no
   DELETE was sent.
7. After Sign out, `satf.profiles` has no entry with that token. A shared-computer Sign out
   sends the DELETE at once and shows no Undo.
8. With `satf.family` unset, Students on this device is not rendered, unless a parked
   unsaved code exists.
9. On a family device with two profiles, switching changes `X-Learner` on the next
   `/api/shell` call.
10. The diagnostic's confirmation link, opened with no `X-Learner`, verifies the email:
    `account.saved` becomes true, and the laptop's next request with `a:X` → 200 with a swap
    header, never 401.

#### U22. The living mark avatar, and glyphs with an earned ring

*From: unfair-advantage #11, the outcomes and experience avatar gaps, the skeptic's photo finding. Effort S. Builders: F1 (`UI.avatar`, `UI.localPhoto`), F2 (`/api/shell.me.domains`), S1 (the picker), S8 (boards never carry the mark).*

**Why.** Students like seeing their own face on their profile, and theirs allows it. But a
photo of a minor on a server, shown to others, is a privacy risk. Ours keeps the photo on
the student's own device, where only they see it, gives more choice than theirs on day one,
and lets progress show where only the student and the people they chose can see it.

* **Choices, all free from day one**: your photo (this device only), the living mark (the
  default), the initial, and all 19 topic glyphs.
* **Your photo, kept on this device** (`UI.localPhoto`, F1).
  * The picker's first tile, "Your photo · this device only", opens a file input
    (`accept="image/*"`, and on phones the camera through `capture="user"` as a second
    button, "Take one").
  * The browser centre-crops it square and downscales it to 256px through a canvas, then
    `toBlob('image/webp', 0.85)` (JPEG where WebP encoding isn't available). It is stored
    in IndexedDB (`satf` database, store `photo`, keyed by the learner id). **It is never
    uploaded**: no endpoint accepts it, and `PUT /api/me` has no photo field.
  * **Where it shows**: only this device's own chrome (the user card, the menu header, the
    phone avatar) and Me's identity card. Everywhere else, and on the student's other
    devices, the server's choice (living mark, glyph or initial) shows as usual. The picker
    says so: "Only on this device. Boards and your progress link show your {glyph|initial}."
  * **Replace**: pick another file. **Remove**: a confirm, "Remove your photo? Your
    {living mark|initial|glyph} will be shown instead." [Remove] [Cancel].
  * It is not offered on a shared computer. It is deleted on Sign out and on Remove from this
    device (U21), and each family-device profile keeps its own.
  * The photo is local, so the server's `avatar` stays the fallback: choosing the photo
    doesn't change `learners.avatar`.
* **The living mark.**
  * The mark's four rounded quadrants are the four domains: Algebra top-left, Advanced Math
    top-right, Problem-Solving and Data Analysis bottom-left, Geometry and Trigonometry
    bottom-right.
  * Each fills orange from the centre outward in proportion to that domain's mastery: 0 is a
    `--mat` outline, Strong is solid. A new student's mark is four outlines that start
    filling with the first answers.
  * Its aria-label and tooltip read "Algebra Strong · Advanced Math Learning · …".
* **Earned rings.** When a glyph's skill reaches Strong (its badge is earned), that glyph gains
  a filled 2px orange ring and a small ✓ badge, on its picker tile and wherever it shows as
  the avatar. A domain's four or five glyphs all ringed add a domain ring around the picker
  group. Nothing is locked: earning adds to a choice the student already has.
  * Picker tiles without a ring read "Strong in Circles adds the ring · 62%", with a thin bar.
* **Who sees what.**

  | where | shows |
  |---|---|
  | the student's own chrome, the menu, Me's identity card (72px, with a small legend) | the photo on the device that holds it; otherwise the chosen avatar, and the living mark with mastery |
  | their progress links (`/share/`) | the living mark with mastery (never the photo) |
  | **public boards** (Compete, private contests, the challenge, practice ranks), and anywhere another student sees them | the chosen glyph (with its earned ring) or the initial. A student whose choice is the living mark shows their initial. `anon` and `hidden` students show the plain mark. Never the photo |

  Mastery never leaves the student and their links. The boards' payloads carry
  `avatar: {kind: 'initial' | 'glyph' | 'plain', glyph?, ring?}` and never `domains`.
* **Subject-aware.** `me.domains` is keyed by subject. With a second subject, the mark reads
  the subject in focus.

**Acceptance.**
1. `/api/shell.me.domains` has 4 numbers from 0 to 1.
2. `PUT /api/me {avatar:'circles'}` for a brand-new learner → 200. After the circles badge is
   earned, `/api/shell.me.avatar.ring == true`.
3. The avatar SVG's aria-label names all four domains.
4. No board payload contains domain mastery: a check in `server/checks/s8.py` fetches every
   board endpoint (`/api/compete/*` boards, the challenge board, practice ranks) for a board
   holding a learner whose avatar is the living mark, and finds no `domains` key and no
   mastery figure. That learner's row shows the initial.
5. Choosing a 3 MB JPEG as the photo: the user card and Me show an `<img>` with a `blob:` URL
   no larger than 256×256, the network log shows no request carrying image data, and a board
   still shows the glyph or initial. Remove shows "Your … will be shown instead", and after
   it IndexedDB `photo` has no entry for the learner. On a shared-computer sign-in the photo
   tile is absent.

#### U29. Your name, and a separate board name

*From: the skeptic's profile-name finding. Effort S. Builders: F4 (the `learners.handle` column and validation), S1 (the identity card, Settings, `PUT /api/me`), S8 (boards read `handle`).*

**Why.** R12 made the one `learners.name` the public board name, under Compete's rule
(`HANDLE_OK`, 3–24 Latin characters, unique). So José, Zoë, 李明, Jo and Al couldn't enter
their own name on Me, and a second Emma was told "Someone already has that name". Theirs
shows the student's real name, and today's `NAME_OK` (`server/app.py`) accepts any script.
The real name and the public name are two different things.

* **Two fields** (changes R12):
  * `learners.name`, **your name**: private. It uses today's `NAME_OK` (any script, no
    digits, `@`, `<` or `>`), trimmed, 1–40 characters, not unique. It is shown only to the
    student: Me's H1, the user card, the menu header, the greeting, the passkey's
    `user.name`, emails, and the progress link's H1 ("Dana's SAT progress", which the
    student chose to share).
  * `learners.handle`, **your board name**: public. It uses Compete's `HANDLE_OK`
    (`^[A-Za-z0-9 _.\-]{3,24}$`), unique case-insensitively (409 "Someone already has that
    board name."), with the reserved and default-looking names refused (422). Null by
    default, so boards show "Student 4F2A" until it is set. It is the only name boards,
    private contests, the challenge and ranks ever show.
  * This settles §3.1's contradiction: "Names can't contain digits" is the rule for your
    name; board names may contain digits.
* **The identity card** (§3.1): the H1 is your name, with a pencil for inline edit. Under it
  a line reads "On boards: **Dana_R** · Change" (or "On boards: Student 4F2A · Choose a
  board name"), next to the board visibility (Name · Anonymous · Hidden). The same pair sits
  in Settings › Account & devices › Boards, with the country (U11).
* **First time.** When a student sets a name and has no handle, the card offers one tap:
  "Use Dana on boards too?" when the name passes `HANDLE_OK` and is free; otherwise it
  suggests a free variant ("Dana_R", "Dana2") without setting it.
* **`PUT /api/me`** validates each field on its own: `{name}` against `NAME_OK`, `{handle}`
  against `HANDLE_OK` and uniqueness. An error names its field.
* **Migration**: an existing `name` that passes `HANDLE_OK` is copied to `handle` (first
  come keeps it; a clash leaves `handle` null), and `name` is kept as it is.

**Acceptance.**
1. `PUT /api/me {name:'José'}` → 200, and `{name:'李明'}` → 200. `{name:'Dana2'}` → 422
   naming `name`.
2. Two learners both `PUT {name:'Emma'}` → 200 each. Both `PUT {handle:'Emma'}` → the second
   gets 409 naming `handle`.
3. No board payload (the `server/checks/s8.py` sweep of U22) contains a learner's `name`;
   rows show `handle` or "Student 4F2A".
4. `/me/`'s H1 shows the name, and its "On boards" line shows the handle.

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
* **Safe prerendering.** Speculation rules run a page's JS before the student sees it, so two
  guards are needed. Each lives in one place.
  1. While `document.prerendering` is true, `UI.api` sends GETs only. Any other method waits
     for `prerenderingchange`.
  2. **`UI.whenVisible(fn)`** runs `fn` at once when the page is not prerendering, and
     otherwise on `prerenderingchange`. Every "seen / shown / dismissed" effect goes through
     it, so a page that is prerendered and never opened changes nothing. That covers:
     * `localStorage satf.seen.*` (Results' "New" dot and any other seen marker);
     * the week sheet (U14) and the welcome-back sheet (U25), and their shown-once flags;
     * hints ("Hold a tab for shortcuts") and `satf.nudge`;
     * showing a toast (`UI.toast` queues until visible), so an achievement never plays
       unseen;
     * `POST /api/me/achievements/seen`, `/api/me/feed/seen`, `/api/reports/seen`;
     * `?next=1` auto-start (U1).
  * `UI.toast`, `UI.sheet`, `UI.hint` and the seen writers call `UI.whenVisible` themselves,
    so a page author cannot forget it. A lint check greps `web/**` for `satf.seen` writes,
    and for `/seen` calls, made outside those helpers.
  * Links carrying `?next=` are also excluded from prerendering.
* **Warming.** The first sidebar hover in a session fetches `/api/types`, for the palette.

**Acceptance.**
1. Chrome at 1280: after a 200 ms hover, clicking a nav item paints a real card (not a
   `.skel`) within 100 ms of `performance.getEntriesByType('navigation')[0].activationStart`.
2. Safari and Firefox, on a second visit: cached content is painted within 50 ms of
   DOMContentLoaded.
3. A prerendered `/me/` sends no POST before activation (checked through the network log).
4. Prerendering `/results/` without activating it (a hover, then moving away) leaves
   `localStorage satf.seen.report` unchanged, and the sidebar's Results "New" dot is still
   shown. Activating it then updates `satf.seen.report`.
5. A prerendered `/` on the first load of the week opens no sheet and writes no shown-once
   flag. On activation the week sheet opens.

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
and contest results matter enough to keep.

* **Inbox.** The top of the account menu (and of the menu sheet) holds "Since you were last
  here · 3".
  * It shows **at most 3 rows**, newest first, then **See all (n)** →
    `/me/?feed=unread#recent`: Recent activity (§3.10) with its new **Unread** filter, which
    lists them all under day headers. So the menu stays short, and Profile, Settings and Sign
    out stay a few keys away (U26).
  * Source: `GET /api/me/feed?unread=1&limit=3` (the count comes with it as `unread`).
  * Kinds: achievements, report replies and checks, corrections (U3), private-contest
    results and closings from Compete, spare days used (U16), week goals met (U14), stage
    changes (U15).
  * Unread dots, plus a count on the user card and the phone avatar.
  * Opening the menu or the list marks them read (`POST /api/me/feed/seen` →
    `learners.feed_seen = now`), through `UI.whenVisible` (U23).
* **Welcome back.** After 2 or more **study days** in a row with no activity, the next clean
  load offers what is waiting: check-ins due, a private contest closing, the streak and any
  spare, and
  the pill **Pick up: {Up next title}**.
  * A study day is R13's: planned rest days (the active plan's days off, the exam's eve) and
    spare days (U16) don't count. Without a plan every day is a study day. So a Mon–Fri
    planner coming back on Monday has missed 0 study days, and gets no welcome-back.
* **One interruption at a time** (F2, one function `UI.autoSheet()` that every auto-opening
  sheet goes through):
  * **At most one sheet opens by itself per local day per device**
    (`localStorage satf.sheet.day`).
  * **Precedence**: the week sheet (U14), then welcome-back. When both are due, the week
    sheet opens with the welcome-back block at its top ("Welcome back · 3 check-ins due ·
    streak 12 kept with a spare"), and welcome-back is marked shown.
  * **Only on a clean load**: the URL has no query and no hash, the page is a shell section
    root (`/`, `/practice/`, `/review/`, `/tests/`, `/plan/`, `/results/`, `/me/`, `/words/`,
    `/compete/`), and it is not prerendering. So `/?next=1` from a reminder or a push,
    `/s/?c=` share links, Compete's contest invite links, `?q=` question links, report links
    and every other deep link open straight to what was asked. A sheet held back that way
    opens on the day's next clean load.
  * While a sheet is open, toasts queue until it closes. At most 2 event toasts show on any
    load; the rest go straight to the inbox count.
  * Banners (§2.11) keep their one-at-a-time rule and never open a sheet.
* **Undo on every reversible toast**, for 6 s:
  * unsave, unmark, skip a plan task (S7), turn off a progress link, target or
    exam change, a palette command, sign out (8 s, U21; none on a shared computer).
  * Undo calls the inverse endpoint. `UI.toast(text, {undo})` already exists in kit.

**Acceptance.**
1. A new achievement shows in `GET /api/me/feed?unread=1`. After `POST /api/me/feed/seen` it
   does not.
2. A learner without a plan whose last attempt is 3 days old sees the welcome-back sheet
   once. A reload does not show it again.
3. Unsave → Undo → `GET /api/saved` contains the question again.
4. A Mon–Fri learner (an active plan, rest on Sat and Sun) whose last answer was on Friday:
   the first clean load on Monday opens exactly one sheet, the week sheet, with no
   welcome-back block. `/?next=1` on Monday before that opens the session with no sheet,
   and the week sheet then opens on the day's next clean load.
5. The same learner inactive since the previous Wednesday: Monday's first clean load opens
   one sheet, the week sheet, with the welcome-back block at its top.
6. With 20 unread items, the account menu renders 3 inbox rows and "See all (20)".

#### U26. Chrome that fits the screen, long pages and thumbs

*From: the unfair-advantage sub-links gap, the experience rail-peek gap, the experience profile-length gap, experience #10, the experience menu-toggles gap, and the skeptic's height, phone-sheet and menu findings. Effort M. Builders: F2 (shell, `UI.sections`, `UI.menu`), S1 (Me's section list and collapse), F1 (CSS).*

**Why.** v2's pinned sidebar stack (Up next, the Today card, Help and Feedback, the user card)
was about 650–720px tall. A 1366×768 school Chromebook shows about 620–650px, so the nine nav
items got no room. Theirs shows all ten items with no scrolling. The phone sheet put the daily
rows about 700px down. The account menu put controls in a non-focusable header.

* **The nav list: a Profile item, and each fact once** (changes §2.2 items 4, 5 and 7).
  * PROGRESS adds **Profile** (`/me/`, `G U`, a person icon) after Compete. Its meta is the
    week goals, "1/3" in DM Mono, when goals are set (U14), with the pips and goal names in
    its tooltip.
  * Section mapping: `me`, `settings` and `signin` → **Profile**. The user card no longer
    takes the active background.
  * **Plan**'s meta drops "28 q", because the Today item already says "12/28". On a study day
    it names the next test day within 7 days ("Test Sat"), or nothing. "Test day", "Rest",
    "Exam day" and "Set up" are unchanged.
  * The **Today card** drops its questions bar whenever the Today item shows a count (always,
    with or without a plan). It keeps the streak and spares, minutes against the goal, the
    registration line (U17), a private contest closing within 24 h (from Compete), and the
    exam footer.
* **Height budget** (replaces §2.2 item 6). The nav items are never scrolled and never cut,
  and nothing is shrunk into a tooltip. Below 1100px tall, Up next and the Today card leave
  the sidebar **whole** and move to the Now strip at the top of the page. Tiers are chosen
  by viewport height in CSS (`@media (max-height: …)`, no measuring script). Worst case
  assumed: all 9 items (with Profile), both group labels, and a Today card with every line.

  | tier | viewport height | brand | Search, Quick | Up next (U1) | nav rows | Today card | Help, Feedback | user card | total |
  |---|---|---|---|---|---|---|---|---|---|
  | Tall | ≥ 1100px | 64 | two 40 rows | the full block, ≤ 150 | 40, labels 28 → 416 | the full card, ≤ 170 | two 36 rows | 56 | ≤ 1,072 |
  | Medium | 760–1099 | 56 | one 40 row: Search, then a 40 square Quick | in the Now strip | 38, labels 24 → 390 | in the Now strip | 32px icons at the right of the user row | 56 | ≤ 566 |
  | Short | 480–759 | 44 | one 36 row | in the Now strip | 32, labels 18 → 324 | in the Now strip | icons in the user row | 44 | ≤ 460 |

  * The totals include the gaps: 8px in Tall and Medium, 4px in Short.
  * Order: in Tall it is brand, Search, Up next, Quick, the nav, the Today card, Help and
    Feedback, then the user card. In Medium and Short: brand, the Search and Quick row, the
    nav, the user card.
  * **Below 480px** (for example 150% zoom on a short laptop), the nav scrolls as one region,
    the active item scrolled into view. The brand, Search and the user card stay pinned.
  * **The rail** follows the same rule. The mark is the expand toggle, since Today is already
    `/`, which gives 17 targets. At 880px or taller they are 44px. At 620–879 they are 36px,
    and Help and Feedback leave the rail (they are in the account menu). Below 620 the icon
    column scrolls.
* **The Now strip** (`UI.nowStrip`, F2). It shows whenever the sidebar isn't showing both
  full blocks: below 1100px tall, on the rail at any height, and in the 760–1099px-wide
  overlay layout.
  * It is the first row of `main`, above the section bar: two cells side by side
    (`grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr)`), stacking when `main` is under
    720px wide. About 112px tall.
  * **UP NEXT cell**: U1's whole block (the title, the meta "3 q · 4 min · ≈ 6 pts", the
    reason, **Start** with `G N`, and the `›` popover with 5 more and the time-box chips).
  * **TODAY cell**: the whole Today card, every line as text with its links and lever
    popovers: the streak with spare flames, minutes against the goal with its bar, the
    registration line, the contest closing line, the exam footer.
  * It scrolls with the page, so reading space is never taken while scrolling. Once it has
    scrolled out of view, the sticky section bar (or a 36px sticky bar on a page without
    sections) shows at its right end "Up next: {title} · Start", so Start stays one click
    away.
  * On `/`, Today (S3) renders `UI.nowStrip` as its own first block, so it is never drawn
    twice. The session runner and the test window never show it.
* **The section bar** (replaces v2's sub-links in the nav and the phone-only chip row).
  * A page with sections registers them: `UI.shell({sections: [{id, label}]})`. `UI.sections`
    renders them as a sticky bar at the top of `main`: `top: 0` on desktop, under the 56px top
    bar on the phone. It is the same list at every width, so no card is left without a chip.
  * Desktop: chips 28px, 13px, wrapping to at most 2 rows. Phone: one row that scrolls
    sideways with scroll-snap, the active chip kept in view.
  * **Scroll-spy**: an IntersectionObserver (`rootMargin: '-64px 0px -66% 0px'`) sets
    `aria-current="true"` on the chip whose card crosses the top third. On Me's two desktop
    columns that can be one chip per column.
  * A click scrolls to the card (smooth unless reduced motion), moves focus to its H2
    (`tabindex=-1`), and writes the hash with `history.replaceState`, so a card can be linked.
  * **Lists.**
    * Me, all 16 cards: You · This week · Goals · Snapshot · Readiness · Skills · Trend ·
      Pace · Catching you · Habits · Badges · Activity · Recent · Preferences · Saved ·
      Account.
    * Settings: Practice · Tools & display · Study · Account & devices · Your reports · Privacy
      & data.
    * Help: its answer groups. Results: its sections (S6 registers them).
  * Why not in the sidebar: Me's 16 sub-links would take about 512px, which the height budget
    doesn't have. Help's item is not in the nav at all on shorter screens.
* **Rail peek.** Resting the pointer on the rail for 400 ms, or holding `[` for 300 ms, opens
  the full sidebar as an overlay without changing `satf.rail`. It closes when the pointer
  leaves or the key is released. Tapping `[` still collapses.
* **Collapsible cards.** Every Me card header has a collapse chevron that leaves a one-line
  summary ("Skills · weakest Probability 41%"). The state is kept in
  `localStorage satf.me.collapsed`. A section-bar chip opens a collapsed card as it scrolls
  there.
* **Thumb-first phone chrome.** The 5 tabs stay as specified (R1).
  * **Top bar at 360px.** Under 380px wide the gaps drop from 8px to 4px, and the Review chip
    is sized to its content (at least 48px, text capped at "999+"). Fixed parts
    16 + 40 + 40 + 48 + 40 + 40 + 16 = 240, plus 6 gaps of 4 = 264, leaves 96px for the chip
    and the spacer. "● 114" needs about 64.
  * **The grip.** The tab bar gets a 24px grip, a 44×24 button (`aria-label="Open menu"`)
    centred on its top edge. Tapping it opens the menu sheet. There is no swipe-up: on the
    iOS home indicator (standalone) and above Safari's bottom toolbar it collides with the
    system's own gestures.
  * **The menu sheet** (max-height 85vh) has two parts:
    * **A sticky footer, always on screen**: equal cells for Review (● 114), Words (12 due),
      Compete (New / #4) and Quick. Each is 64px tall, with a 22px icon, an 11px label and an
      11px DM Mono meta. At 360px each cell is at least 82px wide. Review, our core surface, is two taps from any page, never a scroll.
    * **The scrolling body above it**, opened at the top:
      1. Up next with Start and the time-box chips (U1).
      2. "Since you were last here": at most 3 rows and See all (U25).
      3. The Today card.
      4. The account header (→ Profile, with the week goals), then Students on this device
         (a family device only, U21).
      5. Settings, Save your progress (when unsaved), Sign in another device, Help & FAQ,
         Send feedback, Dark theme, Large text, Sign out (or Leave this device).
  * **Hold a tab** for 450 ms (cancelled by 8px of movement; `-webkit-touch-callout: none`)
    to open a shortcut menu anchored above it:
    * Today: Up next, Question of the day, Daily challenge · New;
    * Practice: Quick question, Log a mistake, Review · 14, Saved · 3, Words · 12 due;
    * Tests: Resume module · 12/22, New module, Full section, Diagnostic;
    * Plan: today's tasks;
    * Results: Latest report, Skills.
    Every item is also in the menu sheet, for keyboard and screen-reader users.
  * A first-visit hint above the tabs, "Hold a tab for shortcuts", goes after the first hold
    or a tap on ×. It is shown through `UI.whenVisible` (U23).
  * The palette's input is pinned just above the keyboard (`visualViewport`). Results stay in
    top-down order.
  * The quick sheet puts Check and Another in a 56px bottom action bar.
* **The account menu, in valid menu ARIA** (changes §2.6).
  * The header stays non-focusable and holds no controls: the avatar, name, email and role
    line.
  * The items, in keyboard order:
    1. the inbox, when unread: at most 3 rows, then **See all (n)** (U25);
    2. the unsaved callout, "Save your progress";
    3. Students on this device, on a family device only (U21);
    4. Profile (`G U`) · Settings (`G S`) · Sign in (unsaved only) · Sign in another device
       (U20) · Help & FAQ · Send feedback;
    5. a `role="group"` named "Display" holding **Dark theme** and **Large text**, each a
       `menuitemcheckbox` with `aria-checked`, and **Keyboard shortcuts** with its `kbd`
       "?" (a `menuitem` that closes the menu and opens the shortcuts sheet, the one clickable
       way to it from the chrome). Enter or Space toggles a checkbox without closing the
       menu, and writes `theme` (`dark` / `light`) or `text` (`large` / `normal`). Small text
       and System stay in Settings (Question text is Small · Normal · Large there, §3.1
       override 33);
    6. a `role="separator"`, then Sign out (or Leave this device).
  * Reach: `Home` and `End` jump to the first item and to Sign out, and typing a letter moves
    to the next item starting with it (the menu pattern's typeahead). So Sign out is one
    `End` press away however many inbox rows there are. For a saved learner with 20 unread
    items and no family device, ArrowDown takes 3 + 1 + 5 + 3 = 12 presses.

**Acceptance.**
1. **Height budget.** With all 9 nav items, at 1366×657, 1440×790, 1280×900 and 1280×500:
   every nav item's `getBoundingClientRect()` lies inside the viewport, and the sidebar's
   `scrollHeight == clientHeight`. At 1366×470 the nav region scrolls and the active item is
   in view. At 1920×1100 the full Up next block and the full Today card are in the sidebar,
   and no Now strip is drawn.
1a. **Nothing behind a hover.** At 1366×657 on `/me/`, with a Today card that has every line
   (spares, minutes, registration, a contest closing, the exam footer): the Now strip is in
   the viewport, and the Up next reason, its meta and every Today card line are visible
   text nodes (no `title` attribute or popover needed). After scrolling 1,000px, the section
   bar shows "Up next:" and a Start button, and `G N` still starts item 1.
2. With a plan, the Today card contains no "of 28 questions" text while the Today item reads
   "12/28", and the Plan item's meta never matches `^\d+ q$`.
3. At 1280 on /me/: the Profile item has `aria-current="page"`, and the section bar has 16
   chips. Scrolling to Skills sets `aria-current` on the Skills chip. At 390 the same 16 chips
   render.
4. On /help/ at 1366×657, the section bar lists Help's groups, and acceptance 1 still holds.
5. **Phone.** At 390×844 and at 360×740, with a Review count of 114: tapping the grip opens
   the menu sheet. The Review cell lies inside the viewport without scrolling the sheet.
   `document.documentElement.scrollWidth <= innerWidth`, and the top bar's
   `scrollWidth <= clientWidth`. Holding Practice for 500 ms lists "Log a mistake".
6. **Menu.** For a saved learner with 20 unread items, `End` from any item focuses Sign out,
   and ArrowDown from the first item reaches it in 12 presses. Dark theme has
   `role="menuitemcheckbox"` and toggles with Space while the menu stays open. Keyboard
   shortcuts is a `menuitem` in the Display group, and activating it opens the `?` sheet.
   The header has no focusable descendants.
7. Collapsing Skills on /me/ survives a reload.
8. At 390, `scrollWidth <= 390` on /me/ with every card collapsed and expanded.

### F. Sharing

#### U27. Removed: classes and homework

v2-decisions item 5 removes classes ("We have a separate platform for classes, drop it").
The earlier U27 (Reach-a-level homework, Tailored sets, teacher detail, the verified-email
rule for teachers, the free-mail cap, Report this class) is withdrawn with task S2, and so
are its drill fields `until` and `cfg.tailored`, the `FREEMAIL` constant, the `class` report
flag and `reports.class`. Nothing in this file depends on a class. Friends competing
together use Compete's private contests (an invite code or link that Compete owns); a parent
or tutor follows a student through the progress link (R18a, §6).

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
     resolving to the saved learner | passkey (U19), Google when configured (U19b), phone
     approval (U20), email code, or a one-time transfer code. When this device holds answers, the student chooses whether to
     add them (`progress.carry`); a shared computer, or answers over 24 h old, defaults to
     not adding (U19) |"
   * Add after the Saved row: "Saving also gives the saving browser its own `d:` token.
     Every other browser holding the `a:` code swaps to its own `d:` token on its next visit
     within 14 days; after that, or after End the old code now, the `a:` code is a
     non-secret id that no longer signs anyone in (U21). `account.saved(learner)` is the one
     test of saved (U19)."
   * Quote, in "Save to an email" step 5: "* It belongs to another code A:
     `progress.carry(this, A)`, the page adopts A (`UI.useLearner`) and reloads. Toast
     "Signed in as Dana · 24 answers moved here"."
     → "* It belongs to another code A: the carry choice (U19) runs, then the page adopts
     A's device token and reloads. Toast "Signed in as Dana", plus "· 24 answers added" when
     the student chose Add."

3. **§1 "Pairing (no email)."**
   * Quote: steps 1–4, from "1. Device A: "Show a pairing code"." through "* Deny → B reads
     "Your other device said no.""
   * Replace with: "**Phone approval (no email)**: U20. The new device shows a QR and 6 digits;
     the phone that holds the progress scans or types them and taps Sign in."

4. **§1 "Sign out of this device".**
   * Quote: "**Sign out of this device** clears `satf.learner` and the `satf.*` caches, keeping
     `satf.look` and `satf.rail`. It mints a fresh code, goes to `/` and shows the toast
     "Signed out"."
   * Append: "A saved account gets no dialog: the toast is "Signed out · Undo" (8 s). The `d:`
     token is revoked when the toast closes or on `pagehide` (a keepalive fetch), whichever
     comes first, and the student's `satf.profiles` entry is removed (U21). A
     shared-computer sign-out is immediate, with no Undo. A shared-computer token dies on the
     server 15 minutes after its last request, about a minute after its last tab closes, and
     12 h after sign-in at most (U21)."
   * Quote: "**Sign out everywhere else** (saved accounts only):" and its steps 1–3.
     → "**Sign out all other devices** revokes every other `d:` token (U21). Nothing is
     rotated: after saving, the `a:` code signs no one in."
   * Quote: "**Device code**: an advanced fallback, masked (`a:••••••••••••hist`) with Show and
     Copy. …"
     → "**Transfer code** (U21): a one-time, 10-minute, 8-character code from Move to another
     device. It gives the other device its own `d:` token (or, unsaved, the `a:` code). The
     masked `a:` code with Copy remains only in the unsaved Leave-this-device dialog."

5. **§1 "Privacy for minors".**
   * Quote: "* No photo upload: the avatar is an initial or one of our 19 topic glyphs."
   * Replace with: "* No photo upload: a photo the student picks stays on their own device
     (IndexedDB, 256px) and is never sent (U22). The server-side avatar is the living mark,
     the initial, or any of the 19 topic glyphs (all free; Strong adds a ring). The living
     mark, which shows mastery, is seen only by the student and their progress links. Public
     boards show the glyph or the initial, and only the board name (U29)."
   * Quote: "* No location is collected."
     → "* No location is detected. A country is optional, blank by default, and set only by
     the student, for the Country board (U11)."

6. **§2.2, sidebar.**
   * Quote: "3. **Quick** (40px, `--wash`, ink text): a bolt, "Quick", and the `kbd` "Q"."
   * Insert before it: "2a. **Up next** (U1): the UP NEXT block (title, meta, reason, Start
     with `G N`, and the › popover with 5 more and the time-box chips)."
   * Items 4–5: add **Profile** (`/me/`, `G U`, meta "1/3" week goals) to PROGRESS after
     Compete. Plan's meta drops "28 q" and names the next test day ("Test Sat") (U26).
   * Quote: "6. Flexible space. On short viewports, items 4–5 scroll inside the sidebar and
     items 7–9 stay pinned."
     → "6. **Height budget** (U26): the nav items never scroll and nothing moves into a
     tooltip. Three height tiers (≥ 1100, 760–1099, 480–759). Below 1100px tall, Up next and
     the Today card move whole to the **Now strip** at the top of `main`; the sidebar keeps
     the brand, Search and Quick, the nav and the user card. Below 480px the nav scrolls as
     one region."
   * Section mapping: "| me, settings, signin | the user card (it takes the active
     background) |" → "| me, settings, signin | Profile |".
   * Quote: "| **Class** | `/class/` | only when the student is in or teaches a class. …" →
     delete the row (decision 5). PROGRESS is Results, Words, Compete, Profile.

7. **§2.2 item 7, Today card.**
   * Quote: "* Header row: "TODAY" (k label), and on the right the flame icon and the streak
     ("6"). The flame is filled orange while the streak is above 0."
   * Append: "One small outlined flame per banked spare day (U16)."
   * Quote: "* Bar 2: "12 of 28 questions"." → delete it. The Today item's meta already shows
     "12/28" (U26). Likewise "18 min · 12 questions today" without a plan becomes "18 min
     today".
   * Add after Bar 1: "* "Register for Nov 7 · 5 days left", inside the deadline window
     (U17)."
   * Quote: "* "Due: Period 3 · Circles · Fri", when an assignment is due within 3 days
     (links to it)." → delete it (decision 5). Add in its place: "* "Sam's
     contest closes tonight 23:59 · Start", when a private contest the student joined
     closes within 24 h (from Compete's `closing_soon`)."
   * Add: "Below 1100px tall the whole card, every line, moves to the Now strip at the top of
     the page (U26). Week goals show on the Profile item, not here (U14)."

8. **§2.3, rail.**
   * Quote: "* **Search, Quick, Help and Feedback** become icons with tooltips."
   * Append:
     * "Under Search, a 44px orange play button starts Up next item 1; its tooltip carries the
       title, the reason and `G N` (U1)."
     * "Resting the pointer on the rail for 400 ms, or holding `[`, peeks the full sidebar as
       an overlay (U26)."
     * "The mark is the expand toggle. Targets are 44px from 880px tall, and 36px at
       620–879px, where Help and Feedback move to the account menu. Below 620px the column
       scrolls (U26)."

9. **§2.4, phone.**
   * Quote: "**Bottom tabs** (64px + safe area, 5 equal columns, 22px icon, 10.5px label):"
   * Append to that paragraph: "A 24px grip button; tapping it opens the menu sheet (no
     swipe gesture). A 450 ms hold on a tab opens its shortcuts. The Today tab's dot also means
     an urgent Up next item (U1, U26)."
   * Quote: "Everything fits 390px: 16 + 40 + 40 + flex + 64 + 48 + 40 + 40 + 16, with 8px
     gaps."
     → "Everything fits 360px: under 380px wide the gaps are 4px, and the Review chip is
     content-sized (at least 48px, capped at "999+"), leaving 96px for the chip and the
     spacer (U26)."
   * Quote: "**Menu sheet**: a bottom sheet with a drag handle, max-height 85vh, 52px rows,
     grouped:" and its list 1–4.
   * Quote: "**Class due**" in the dot list, and "or an assignment is due" on the avatar's
     dot → delete both (decision 5).
   * Replace with a sheet in two parts:
     * **A sticky footer, always visible**: Review (● 14), Words (12 due), Compete (New /
       #4), Quick, as equal 64px cells.
     * **The scrolling body**, opened at the top:
       1. Up next item 1 with Start, and the time-box chips (U1).
       2. "Since you were last here" (U25), when there is anything unread: at most 3 rows and
          See all.
       3. The Today card.
       4. The account header, then Students on this device (a family device only, U21).
       5. Settings, Save your progress (when unsaved), Sign in another device, Help & FAQ,
          Send feedback, Dark theme, Large text, Sign out (or Leave this device).

10. **§2.6, account menu.**
    * Quote: "1. **Header** (not focusable):" → unchanged. It holds no controls.
    * Insert after the header: "1a. **Since you were last here** (U25): at most 3 rows and
      **See all (n)** → `/me/?feed=unread#recent`. 1b. **Students on this device** (U21, a
      family device only)."
    * Quote: "3. Profile (`G U`) · Settings (`G S`) … · Sign in (only when unsaved; →
      `/signin/`) · Pair a device · …"
    * Replace "Pair a device" with "Sign in another device (U20)", and delete "Join or teach
      a class (→ `/class/`)" (decision 5). Move "Keyboard shortcuts (`?`)" into the Display
      group below; it stays a clickable `menuitem`.
    * Insert before item 4 (the divider): "3a. A `role="group"` "Display" holding **Dark
      theme** and **Large text** as `menuitemcheckbox` rows, and **Keyboard shortcuts (?)**
      as a `menuitem`. Enter or Space toggles a checkbox without closing the menu. `Home` and
      `End` jump to the first item and to Sign out (U26)."

11. **§2.7, quick sheet, Log a mistake.**
    * Quote: steps "1. **Which skill?**" through "5. **Add to my mistakes** (pill) sends POST
      `/api/mistakes/log`."
    * Replace with U2: one field (ID, paste or search), with the coverage helper ("We know
      1,039 of College Board's 1,921 Math question IDs…"); an unknown ID's fallback (paste the
      text, or pick its skill, never an empty result); "Which answer did you pick?"; Where;
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
    * Delete "`K` Class" (decision 5), here and in §2.8's global row (`K` stays free).
    * Append: "`G` then `N` starts Up next item 1."

14. **§2.10, report.**
    * Quote: "* **Answer key is wrong** reveals two fields:" and its two bullets.
    * Replace with U3: "Which answer do you get?" as A–D chips or the grid-in field; the
      instant check, tried in the order `broken` → `remarked` → `forms` → `unsure` (the
      Strong-student signal, or too few strong answers) → `explained` → `unsure`;
      `explained` requires the solver and the Strong-student signal to agree, and is worded
      "The numbers check out with our independent solver…"; That makes sense / The wording
      or figure is wrong / Still wrong: send to a person. Categories about the stem, the
      figure or the options (Figure or table wrong, Typo or display, No right answer or two
      right answers, The named mistake doesn't fit) always go to a person. The "don't count
      it" checkbox and the 5-dispute bound apply only to "send to a person".
    * Quote: "* **Images**: an "Add images" button, paste (⌘V) and drop."
    * Prefix with: "For a question report the box says "We have this exact question (…). No
      screenshot needed." and files sit behind "Add files"."
    * Replace its limits with U3's: up to 10 files; stills downscaled to 2000px and capped at
      10 MB; GIF as-is and `video/webm` / `video/mp4` up to 50 MB each; 200 MB per report;
      **Record screen** (60 s, desktop); each file row shows its size and a remove ×, and an
      over-limit file is refused in the row before sending (413 / 415 on the server).
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
      reports an event also lands in the inbox. Toasts wait while a sheet is open or the page
      is prerendering, and at most 2 event toasts show per load (U23, U25)."
    * Add after the banner list: "**Sheets that open by themselves** (the week sheet,
      welcome-back) go through `UI.autoSheet()`: at most one a day per device, the week sheet
      first with welcome-back merged into it, and only on a clean load (no query, no hash, a
      section root, not prerendering). A banner never opens a sheet (U25)."

16. **§2.12, shell data.**
    * Quote: "GET `/api/shell` once per page load."
    * Add these keys to the shell response (§3.1.5):
      * `next` (3), `goals`, `inbox` (unread count), `stage`, `pref_source`;
      * `me.name`, `me.handle` (U29), `me.domains` (keyed by subject), `me.avatar {kind,
        glyph?, ring?}`, `spares`;
      * `registration {exam_date, register_by, late_by, registered}`;
      * `device {method, session_only, expires}` (the current token's row, for the user
        card's "Shared computer" line and the last-method memory);
      * `today` (the whole Today card, every line, including `contest` from Compete's
        `closing_soon`), which the sidebar card and the Now strip both render (U26).

17. **§2.14, install.**
    * Quote: "* No service worker: the API is the app, and there is nothing useful to serve
      offline."
    * Replace with: "* A notification-only service worker, `/sw.js` (`push` and
      `notificationclick`; no fetch handler, no caching), registered when the student turns on
      "Notify me on this device" (U18b, in the core build). Nothing is served offline."

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
      preferences, Saved & in progress, Account", with collapsible cards (U26).
    * Add: "A sticky **section bar** at the top of the page lists all 16 cards at every width,
      with scroll-spy (U26). Me registers it through `UI.shell({sections})`; the phone uses
      the same list."
    * Quote: "**Data**: **GET `/api/me/summary`** (one call) builds the page."
    * Append: "It takes `?subject=` (default `math`) and returns `{stats, goals, subjects:
      {math: {score, domains, coverage, gains, pace, habits, levers, ranks}}}`: cross-subject
      facts (`stats` with `series`, `delta` and `levers`; `goals` with the 1600 total; `week`)
      at the top, everything about a subject under `subjects.<subject>` (U4–U13, the
      subject-aware rule at the top of this file)."

19. **§3.1, identity card.**
    * Quote: "* **Avatar** 72px: the initial on paper, a chosen topic glyph, or the mark when
      unnamed."
      → "* **Avatar** 72px: the living mark (U22) by default, or the initial, or any glyph
      (a glyph whose skill is Strong carries an orange ring and a ✓)."
    * Quote: "* It opens a popover: "Initial" plus the 19 glyph tiles (5 a row, 44px; the
      selected one has a 2px orange ring)."
      → "… "Living mark", "Initial", plus the 19 glyph tiles, all selectable. The selected
      tile has a 2px ink outline and "Selected" in its label, because the orange ring now
      means earned. Unringed tiles read "Strong in {skill} adds the ring · 62%". The first
      tile is "Your photo · this device only" (U22). A line under the picker: "Boards show
      your glyph or initial. Only you and your progress links see the living mark, and only
      this device sees your photo."
    * Quote: "* Editing swaps in an inline field (24 characters max). Enter saves, Esc
      cancels." → "… (40 characters max) edits your name (`learners.name`: any script, not
      unique; U29) …"
    * Quote: "* Errors inline: "Names can't contain digits, @, < or >." (the server's NAME_OK
      rule)." → unchanged: it is your name's rule.
    * Quote: "* Below it: "On boards: Dana" / "On boards: Student 4F2A" / "Not listed on
      boards", with a link to change it." → "… "On boards: **Dana_R** · Change" edits the
      board name (`learners.handle`, HANDLE_OK, unique; its own errors), beside the board
      visibility (U29)."
    * Quote: "* The role line, when in a class: "Student in Period 3" / "Teacher · 2
      classes"." → delete it (decision 5).
    * Quote: "* **Goal pills** (32px, paper): "Target 700" · …" → the pill reads "Target
      1400" when an R&W target is set, else "Math target 700" (U4).
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
    * Delete the per-class practice-rank lines (decision 5).
    * Add under the band: "SAT total 1130–1210 · R&W 610 (yours)" when `rw_now` is set (U4).
    * Append: "Each line adds its movement since last week and the gap to the next place.
      Add a **Country** line when `learners.country` is set (from Compete's Country board;
      otherwise "Add your country to see your country rank", whose **Add country** popover
      sets it in place, U11). Below them: the **Climb** line,
      whose cohort window widens (±40, ±80, ±160, everyone) until it holds 20 and is stated
      ("Started 440–600"), and **You, N days ago** from day 8 (U11)."

21. **§3.3, Study goals.**
    * Quote: "* **Target**:" and its first bullet (the 200–800 range bar).
      → Add above the bar: "Target **1400** = Math 700 + R&W 700 (your estimate)", from
      `summary.goals` (U4). The bar and its labels stay the Math part.
    * Quote: "* Save sends `PUT /api/me {target}` and toasts "Saved · your plan uses 700
      now"." → "… `PUT /api/me {target, rw_target}` (and `rw_now` when changed), toast
      "Saved · your plan uses 1400 now". The popover has both parts (U4)."
    * Quote: "* the live line "+100 from your latest band";"
    * Append:
      * "* "What 700 takes: about 37 of 44 right, with at least 14 of 22 in module 1 to reach
        the harder module 2; you're near 31", with the 3 skills; above 780 it names the
        model's 780 ceiling (U4);"
      * "* the pace line and tag from `plan.pace`, and the one-tap date that makes it Steady;"
      * "* "Raise to 750?" once reached."
    * Quote: "* **Edit** opens a popover with chips for the upcoming official dates, each with
      "in N days" …"
    * Append: "each chip also shows "register by …", "late …" and, when a projection exists
      with a half-width of 80 or less, "~690" (U17, U4, U9)."
    * Quote: "* The week starts on the student's preference."
    * Append: "* History: "Met 4 of the last 6 weeks", with 6 mini bars (U14)."

22. **§3.4, Learning preferences.**
    * Quote: "| Questions per set | seg 5 · 10 · 22 · ∞ | — |"
    * Insert above that row:
      * "| Mode | seg Learn · Build · Test-like · Custom | "Sets clock, feedback, repairs,
        explanations and difficulty together." |"
      * "| Follow my exam date | switch | "Build · 34 days to Nov 7 · Test-like starts Oct 17." |"
    * Add after the Calculator button row (their Include Vocab Review, and R31's "test
      defaults appear under Learning preferences"):
      * "| Words a day | seg Off · 5 · 10 · 20 (`words_goal`) | "New SAT Reading and Writing
        words in your plan each day. Off leaves words out." |"
      * "| New words from | multi-toggle SAT words · Transitions (`words_from`, default both)
        | — |". `words_from` ∈ {`sat`, `transitions`}, non-empty, default
        `[sat, transitions]`; `math` → 422 (v2-decisions item 2, no Math-language deck).
    * Delete `gloss` ("underline math words") from Me's rows. It no longer glosses anything a
      Math question uses; Words (S9) decides whether an EBRW gloss returns, and where.
      * "| Test timing | seg Official · 1.5× · 2× · Untimed (`test_timing`) | "Used when a
        module or section starts. Only Official timing is scored as a real sitting would be."
        |"
    * Add: "Rows the mode sets carry "Set by Build · Change" or "Yours · Back to Build" (U15).
      The Mode helper adds: "Applies to sets you build and Up next's skill rows. Fixing
      mistakes and check-ins always show the key after each answer."

23. **§3.5, Skills.**
    * Quote: "The header's right side reads "Strongest: Circles · Weakest: Probability" (once
      there are answers), with "All skills in Results"."
      → "The header holds "About 60 points on the table · your top 3 hold 34", the seg "By
      points · By domain", "Strongest / Weakest", the Sharpen line when skills are rough, and
      "All skills in Results" (U4, U5)."
    * Quote: "* a "Practise" link (a `prefs.set_length` set on that skill)."
    * Append:
      * "* the gain "≈ +20", "about 4 of 44", "at least 6 right · ~9 min" (U4);"
      * "* the evidence ladder (Not started · Not measured yet · try 5 · rough · n answers ·
        measured · n answers), the 14-day trend, the last 5, and Fading with Keep warm
        (U5)."
    * Add a footer: "Practise the top 3 · 15"."

24. **§3.6, Score trend.**
    * Quote: "* **Target and exam**: the target is a dashed line labelled "Target 700"."
    * Append: "The projection cone to the exam date ("If this pace held", from 3 sittings
      over 21 days, shrunk and tapered), the plan's pace line, and what changed in each gap
      between sittings (U9)."

25. **§3.7, What keeps catching you.**
    * Quote: "Footer: "All mistakes"."
    * Add before it: "Header pill: **Trap gauntlet · 10** (U6)."
    * Add a new card after §3.7: "**3.7a Your habits** (U6)."

26. **§3.8, Achievements.**
    * Quote: "* The earned date, "Sep 21"."
    * Append: "* In progress: **Go · {action}** (U13)."
    * Quote: "That is 43 in all."
    * Replace with: "That is 43, plus Trap-proof (U6) and Every goal met (U14). Tiers that count
      skills, domains or types (the skill badges, the domain badges, Explorer's top tier) are
      computed from `catalogue.by_topic(subject)` per subject, so an R&W bank adds its own
      badges without editing these."

27. **§3.9, Activity.**
    * Quote: "A planned rest day with nothing done shows a faint centre dash."
    * Append: "A spare day shows a hollow ring (U16)."

28. **§3.10, Recent activity.**
    * Quote: "Each row has an icon, a title, a detail, a time ("14:02 · 3h ago") and a
      chevron, and links wherever it can:"
    * Append: "Sitting rows add their effect line and **Again · new numbers** / **Follow up ·
      n** (U12)."
    * Add to its filter: "**Unread** (`?feed=unread`), the full inbox that the menu's See all
      opens (U25)."
    * Quote the row kind "| Assignment | "Period 3 · Circles · 8/10" | "on time" or "late" |
      the report |" → delete it (decision 5). A finished private contest is Compete's
      `contest` row.

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
    * Add after it (each hidden at 0, so theirs' three counts all appear):
      * "* "Saved words **8**", with **Review them** → `/words/?s=saved` (from
        `words.me_stats`, S9)."
      * "* "Marked for review **5**", with **Practise marked** (`/api/drill {pool:'marked'}`,
        R5), from Review's counts (R31)."
    * Quote: "* "Open mistakes **14**", with **Fix all** (`/api/drill {mistakes: true}`)."
      → unchanged; the part order is Saved questions, Saved words, Marked for review, Open
      mistakes, In progress.
    * Quote: "* "Assigned **2 due**" → `/class/`, for a student in a class." → delete it
      (decision 5).

31. **§3.13, Account.**
    * Quote: "* **Saved**: "Progress saved to dana@gmail.com · since Sep 23", with **Manage**
      → `/me/settings/#account`, and **Sign out** (quiet, door icon, confirm dialog)."
      → "* **Saved**: the recovery line ("You can sign in 2 ways: passkey, email"), "Signed in
      on 3 devices" → the Devices list (every browser that can act as the student, U21),
      **Manage**, and **Sign out** (quiet, Undo toast; U19, U21)."
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
    * **§4.2, Tools & display.** Quote: "* **Question text**: seg Normal · Large, with a live
      serif preview line, "If 3x + 5 = 20, what is x?"" → "* **Question text**: seg Small ·
      Normal · Large (`text`: small | normal | large, as §2.7 defines it), with the same live
      serif preview line." Small sets `--q-size` 18px and `--q-opt` 17px. The account menu's
      Large text checkbox toggles large ↔ normal (U26).

34. **§4.3, Study.**
    * Quote: "* **Reminder**: seg None · 10 min before · 30 min before (default 10)."
    * Append: "* **Notify me on this device** (U18b), with its kinds and the editable quiet
      hours (`quiet`), which never hold back the study reminder the student chose. It is in
      the core build, and hidden only when `SATF_PUSH=off`."
    * Quote: "* **Preferred study time**: seg Morning 7:00 · After school 16:00 · Evening 19:00 ·
      Night 21:00, plus a custom time input." → unchanged, plus: when the chosen time falls
      inside quiet hours, the line "Your 22:00 reminder still rings. Quiet hours only hold
      back extra nudges." (U18b).
    * Quote: "* **Subscribe**: copies a `webcal://…/api/cal/{token}.ics` link."
    * Replace with: "* **Add to calendar** opens U18a's sheet: **Add to Google Calendar** (a
      recurring event through the render URL, so the student's own notifications apply),
      Apple Subscribe with "untick Remove Alerts", Download (an imported recurring event
      keeps its alert), and "Test it". Feed events are titled "SAT Math · Up next · 25 min"
      and link to `/?next=1` (U18a)."

35. **§4.4, Account & devices.**
    * Quote: "* **Name** (a field and Save), with the board preview underneath."
      → a **Boards** block, in this order (U29, U11):
      * "* **Your name**: a field and Save (`name`, NAME_OK, any script, not unique). Shown
        only to you."
      * "* **Board name**: a field and Save (`handle`, HANDLE_OK, unique), with the board
        preview underneath."
      * "* **Show me on boards**" (unchanged, below).
      * "* **Country**: a searchable select, blank by default, with the browser-region
        suggestion chip and Clear. Helper: "Only for the Country board. We never detect
        where you are.""
    * Quote: "**Email**, by state:"
    * Insert before it:
      * "**Google** (U19b, only when configured): Save with Google or "Google ·
        d•••@gmail.com · connected Sep 23" [Disconnect]."
      * "**Passkeys** (U19): Save with a passkey, the list, Remove."
      * "**Devices** (U21): the list (including the browser that saved and every browser that
        swapped), Sign out, Sign out all other devices, **End the old code now** while the
        swap window is open, and the recovery line."
      * "**Email** in outbox mode (U19): "Email codes aren't switched on for this site yet.",
        with Save with a passkey (and Google) as the buttons."
      * "**This is a family device** (U21): a switch, off by default. On, it shows Students
        on this device in the menu. Off, it revokes and removes the other students' entries,
        after warning about unsaved ones."
    * Quote: the "**Pair a device**:" block, through "* **I have a code** → `/signin/#pair`."
    * Replace with: "**Sign in another device** (U20): type the 6 digits shown on the other
      device, or scan its QR."
    * Quote: the "**Device code**" `<details>` block, through "* Errors: "That is not a code."
      / "That is this device." / "Nothing is saved under that code.""
      → "**Move to another device** (U21): [Get a transfer code] shows an 8-character,
      one-time code ("K7P4 M2QX · expires in 9:41"). The other device enters it under
      Sign in › More. Errors: "That code has expired or was used." / "No code like that."
      The raw `a:` code is not shown for a saved account."
    * Quote: "* Saved → confirm: "Sign out? You can sign back in with dana@gmail.com." [Sign
      out] [Cancel]"
      → "* Saved → no dialog; the toast "Signed out · Undo" (U21), with the revoke sent on
      toast close or `pagehide`. On a shared computer, signed out at once with no Undo."
    * §4.6: quote, in **Delete everything**: "class memberships, " → delete it (decision 5); add
      "passkeys, devices, the Google link".
    * Quote: "**Sign out everywhere else** (saved only): confirm "Other devices will need to
      sign in again." → POST `/api/account/rotate`, then the toast "Other devices signed
      out"."
      → "**Sign out all other devices** (saved only): confirm "Other devices will need to
      sign in again." → revokes every other `d:` token (U21). `/api/account/rotate` is not
      built."

36. **§5, Sign in.**
    * Quote: "* Tabs: **Email code** · **Pairing code** · **Device code** (hash `#email` /
      `#pair` / `#code`)."
      → "* Tabs: **Passkey** · **Use your phone** · **Email code** · **More** (transfer code)
      (hash `#passkey` / `#phone` / `#email` / `#code`; `#pair` is an alias of `#phone`).
      It opens on the tab this device used last (`satf.lastMethod`); with no memory and no
      hash, on Passkey when a platform authenticator exists, otherwise Use your phone. Every
      tab has "This is a shared computer" (U21). Above the tabs, **Continue with Google**
      when `SATF_GOOGLE_CLIENT_ID` is set (U19b). The page starts a conditional-mediation
      passkey request on load and refreshes it before its challenge expires (U19). When
      `/api/health.mail == 'outbox'`, the Email code tab shows U19's "aren't switched on"
      text with the other ways as buttons, never a code form."
    * Quote: "* Line: "This device has 24 answers. They'll be added to the progress you sign in
      to." (Hidden at 0.)"
      → "* After the account is known, when this device has answers: "This device has 24
      answers, answered here since Sep 21." [Add them to Dana's] [Don't add them]. The
      default is Add only when the computer is not marked shared and the newest answer is
      under 24 h old. A shared computer never offers Add (U19)."
    * Quote: "**Success**: carry, adopt, then a reload to `/` with the toast "Signed in as
      Dana"."
      → "**Success**: the carry choice, adopt, then a reload to `/` with the toast "Signed in
      as Dana" (or "… · 24 answers added")."
    * Quote: the "**Pairing code**:" block, through "* 429 "Too many tries. Wait 10
      minutes.""
      → the U20 new-device screen, with the same 404 / 410 / 403 / 429 copy.
    * Quote: "`/pair/` is a two-line page that redirects to `/signin/?c=…#pair`, because a
      short URL is easier to type on a phone."
      → "… redirects to `/signin/?c=…#phone`, and `/link/?r=` is the phone's approval
      page (U20)."

37. **§6, Shared view.**
    * Quote: "* H1 "Dana's SAT Math progress", with "Shared by Dana · live · updated 14:02"."
      → "* H1 "Dana's SAT progress", …", since Words (R&W vocabulary) is on it too. Its
      subject cards render per `subjects` key (Math today), and a Words card (S9's
      `words.me_stats`) joins them. "Dana" is the student's name (U29), which they chose to
      share; the view never shows the photo (U22).
    * Quote: "* What keeps catching you (names and counts);"
    * Append: "* Your habits; This week; Test-day readiness (the atlas, read-only)."

38. **§7, Classes and homework: removed** (v2-decisions item 5). Delete §7 whole: its pages
    (`/class/`, `/join/`, the teacher views), tables (classes, members, assignments), endpoints
    (`/api/classes*`), `classes.resolve_drill` and the `assignment` drill field. Also delete,
    elsewhere in §3.1: the Class nav item and its `K` key (overrides 6, 13), the role line
    (19), the Assigned part (30), the Assignment activity row (28), "Join or teach a class"
    (9, 10), class push reminders (U18), class memberships in Delete everything (35), the
    class open questions in §3.1.9 (45), and the Class use of `qr.js` (it stays for U20's QR).

39. **§8, Help.** Add these answers:
    * `#points` (how points on the table is worked out, with the invented-anchors caveat);
    * `#readiness`, `#habits`, `#pace`, `#stages`, `#spare`, `#passkeys`, `#devices`,
      `#family`, `#reminders` (the per-platform alert steps of U18a), `#projection` (why it
      needs 3 sittings and says "If this pace held"), `#checks` (what the instant report check
      does and cannot see, U3);
    * `#fixed` (the list from `GET /api/reports/fixed`);
    * `#routing` (why a Math target above 580 needs at least 14 of 22 in module 1, and why
      our model tops out at 780, U4), `#google` (U19b), `#photo` (why the photo stays on your
      device, U22), `#names` (your name and your board name, U29), `#country` (U11),
      `#shared` (how a shared-computer session ends, U21).
    * Quote: "* What does it cover? (SAT Math: 4 domains, 19 skills. Reading & Writing not
      yet.)" → "* What does it cover? (SAT Math: 4 domains, 19 skills, and SAT Reading &
      Writing vocabulary in Words. R&W questions come later.)"
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
      under their parent. Reports that came in as `unsure` with a Strong-student signal show
      it ("strong 31% vs base 9%, n 24") and sort first (U3). Report files show inline,
      including GIFs and videos (U3). The unknown College Board IDs list, the top 50 by count,
      feeds `cb-ingest` (U2). The header shows the mail mode from `/api/health` (U19)."

42. **§11, component inventory.**
    * Quote: "* Features: `UI.report(ctx)`, `UI.quick()`, `UI.palette()`, `UI.keys.register(scope,
      map)`."
    * Append: "`UI.next` (the Up next block, popover and time box), `UI.inbox`, `UI.week` (the
      weekly sheet), `UI.lever(el, key)`, `UI.help(id)`, `UI.cached(path)`, `UI.share` (twin
      default), `UI.whenVisible(fn)` (U23), `UI.autoSheet()` (U25), `UI.sections` (the
      section bar, U26), `UI.evidence(n)` (the evidence ladder, U5)."
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
      * `devices` and `learner_of` for `d:`, the save-time `d:` token, the 14-day swap
        (`learners.swap_until`, `X-Learner-Swap`), `a:` refused after it, `/api/transfer` and
        `/redeem`, and for shared computers `/api/devices/this/ping` and `/leaving` with the
        15-minute idle rule (U21);
      * `account.saved(learner)`, and the diagnostic results gate reading it (U19);
      * `carry: bool` on every sign-in endpoint, default false (U19);
      * `server/google.py`, `/api/google/nonce`, `/api/google` and `users.google_sub`, behind
        `SATF_GOOGLE_CLIENT_ID` (U19b);
      * `GET /api/health` `mail` and `google` (U19, U19b);
      * `learners.handle` and the split name validation in `PUT /api/me` (U29);
      * `cb_unknown` and `GET /api/types` `cb` (U2);
      * `reports.pick_rate`, and the streamed report uploads with per-type caps (U3);
      * `push_subs` and `server/push.py` (U18);
      * `GET /api/prefs` (U24);
      * `feed?unread` and `/feed/seen` (U25);
      * `/api/me/summary` additions and its `subjects` shape (U4–U13);
      * the `quiet` pref and the scheduler rule that quiet hours never hold back the chosen
        study reminder (U18b).
    * Quote: "GET /api/shell" (Returns:)
    * Add the keys listed in override 16.

44. **§3.1.8, Acceptance checks.**
    * Quote: "18. Pairing: POST /api/pair as A → {code}. …"
    * Replace with U20's acceptance 1–4.
    * Quote: "19. Email: …"
    * Keep it, and add: "the passkey checks of U19."
    * Quote: "23. New learner a:v2revnew on /me/: …"
    * Add: "the U1 block's first item is "Take a module · 22 q" (no sign-up form on the way);
      Test-day readiness reads 0%; Pace and Your habits show their empty states."
    * Quote: "4. At 390x844, document.documentElement.scrollWidth <= 390 on /, /me/,
      /me/settings/, /help/, /signin/, /class/ and /share/?t=…." → drop `/class/`.
    * Delete every class, join and assignment check (decision 5).
    * Add the acceptance lists of U1–U29 (with U19b; U27 is removed) as items 38 onward.

45. **§3.1.9, open questions.**
    * Quote: "- Is SMTP configured for production (SATF_SMTP_*)? …"
      → "Answered: SMTP is a launch requirement (the README's production checklist), and
      `/api/health` reports `mail: 'smtp' | 'outbox'`. Until it is set, the Email tab says so
      and offers passkeys, the phone, Google and transfer codes instead (U19)."
    * Quote: "- Should we also offer Google sign-in? …"
      → "Answered: yes, optional. **Continue with Google** ships behind
      `SATF_GOOGLE_CLIENT_ID` (U19b): ID tokens verified with `cryptography` against Google's
      JWKS, bound by verified email, storing only `sub`, the email and the names. The privacy
      review covers exactly that list."
    * Quote: "- Photo avatars are left out for minors' privacy (an initial or a topic glyph
      only). Confirm."
      → "Answered: a photo is offered, kept only on the student's device and never uploaded,
      so there is nothing to review on the server; boards and share views never show it
      (U22)."
    * Quote: "- Age gate and consent: … before an under-13 student saves an email or joins a
      class (COPPA)? For classes, is the teacher's school consent enough?"
      → drop the class clauses (decision 5): "… before an under-13 student saves an email or
      links Google?"
    * Quote: "- Classes: should a teacher be vetted …" → delete (decision 5).
    * Quote: "- Should the share view and the teacher roster show the names of open mistakes, or
      only counts? …" → "- Should the share view show the names of open mistakes, or only
      counts? …" (no roster, decision 5).
    * Quote: "- The practice rank uses right answers over a rolling 7 days, which rewards
      volume. …"
    * Append: "Answered by U11: the volume rank stays, and Climb ranks gain for students who
      started near the same band."
    * Quote: "- Email reminders at the preferred time need SMTP and a scheduler. Are calendar
      alarms enough for now?"
      → "Answered: calendar alarms alone are not enough (Google ignores them in URL feeds,
      Apple strips them by default). Web Push ships in the core build and needs no SMTP
      (U18b); calendars get per-platform alert steps and a native Google recurring event
      (U18a)."

### 3.2 Outside the section (Part 2 lines these upgrades need; I1 applies them with the owners)

| where | change | upgrade |
|---|---|---|
| R1 | Unchanged (5 tabs). Add: the tab bar's grip button (no swipe) and hold shortcuts, Up next first in the menu sheet, and the daily rows (Review, Words, Compete, Quick) in its always-visible footer. Desktop PROGRESS adds **Profile** (`G U`) after Compete; the Class item is gone (decision 5) | U1, U26 |
| R4 | **Void** (v2-decisions item 5). No classes. Compete's private contests are an invite code or link that Compete owns; the shell reads only what Compete exposes (`deps.part('compete','closing_soon')` for U1 row 2, the Today card, U18 and U25), and nothing here creates, joins or lists them | U1, U18, U25 |
| R9 | Check-ins due feed Up next row 4 and the push text (worked out at send time). Calendar feed titles stay generic, so they never go stale. A plan check-ins task and Up next row 4 are one item (de-duplicated by pool) | U1, U18 |
| R11, §2.7 | New keys: `mode` (learn / build / test / custom, default learn), `stage_auto` (bool, true), `registered` (date or null). Under a mode or stage, a key the student sets is stored even when it equals the default; `{key: null}` deletes it. `GET /api/prefs` serves the registry. `prefs.MODE_SOURCES` names the drill sources the mode and stage govern (builder sets, Up next skill and probe rows, the time box); every other source keeps instant feedback and next repairs. `words_goal`, `words_from` and `test_timing` gain "Me" in their "also edited in" column. `words_from` becomes a non-empty subset of `sat, transitions`, default `[sat, transitions]`, and `math` → 422 (v2-decisions item 2). `gloss` loses "Me" (it stays wherever S9 keeps it). `text` is small / normal / large, all three offered in Settings. New key `quiet` (`{from, to}` local times or null; default 21:30–07:00) | U15, U17, U18, U24 |
| R12 | Board payloads carry `avatar {kind: initial \| glyph \| plain, glyph?, ring?}` and never `domains`, any mastery figure or a photo. A living-mark choice shows as the initial on boards. **Names split** (U29): `learners.name` is private (NAME_OK, any script, 1–40, not unique; Me, the menu, emails, the share view); `learners.handle` is the board name (HANDLE_OK, unique, 409; null shows "Student 4F2A"), and boards read only `handle`. The board name's rule allows digits; "Names can't contain digits" is only your name's rule. `learners.country` is set only by the student (U11) | U11, U22, U29 |
| R13 | Spare days: 1 per 7 study days in a row, up to 2; a spent spare neither breaks nor extends the streak. "No activity" for welcome-back counts study days only | U16, U25 |
| R15 | Me's Goals card and target popover show and edit the 1600 total (`target` + `rw_target`, with `rw_now`), from one `summary.goals`, so Me, Today and Plan agree | U4 |
| R16 | `estimate.py` adds `gains`, `need` (right answers of 44, `m1_min` from `ROUTE_UP_AT` above the 580 lower-route ceiling, and the 780 model ceiling), `projection`. The projection needs 3 sittings over 21 days, shrinks its slope by n/(n+3), tapers to at most 20 a week after week 4, and takes its cone from the residuals plus the band half-width | U4, U9 |
| R17 | The instant check, in the order broken → remarked → forms → unsure → explained → unsure, with `reports.pick_rate` (the Strong-student signal) required for `explained`; stem, figure and option categories always go to a person. Me-too (`reports.parent`), accept, fixed list, quarantine; F4 adds `progress.remark(learner, attempt_id)` (re-mark, close the trap it alone opened). Files: up to 10; stills downscaled to 2000px and capped at 10 MB; GIF, `video/webm` and `video/mp4` up to 50 MB each; 200 MB a report; streamed with 413 / 415; Record screen | U3 |
| R38 | The diagnostic's sign-up gate reads `account.saved(learner)`: a saved learner (passkey, verified email or Google) gets results with no form, and the confirmation link saves without retiring the `a:` code (U21's swap). Up next never makes the diagnostic a new student's first item while the gate exists | U1, U19, U21 |
| R18(b) | Feed events are titled generically ("SAT Math · Up next · 25 min") and link `/?next=1`; deadline events keep specific titles. Add a Google Calendar render link with `recur=RRULE`, and a downloadable single recurring `.ics` with VALARM | U17, U18 |
| R18(c) | `sets` `cfg.fresh` (a fresh seed per viewer) | U28 |
| R25 | New ladders: Trap-proof 5/20/50; Every goal met 1/4/12 weeks | U6, U14 |
| §2.5 | Tables: `passkeys`, `webauthn_challenges`, `devices`, `transfers(code PK, learner, expires, used)`, `quarantine`, `week_goals`, `push_subs`, `cb_unknown` (not learner-keyed). Columns: `pairs.dir / token / approver / session_only`, `reports.parent / check`, `outside_scores.misses`, `learners.feed_seen / handle / swap_until`, `users.google_sub`; `traps.origin` adds `cb_qbank`. No class tables (decision 5). `LEARNER_TABLES` and `carry` include the new learner-keyed tables | U2, U3, U14, U18–U21, U25, U29 |
| §2.6 | Fields: `segments` ([{pool, ids?, topics?, count}], filled in order), `box` (5–60 minutes). Sources: `next`, `probe`, `habit`, `gauntlet`, `bluebook`. `want` also matches `progress.norm(reason)`. The `assignment` field and `classes.resolve_drill` are gone (decision 5) | U1, U2, U5, U6 |
| §2.8 | Global: `G` then `N` starts Up next; `K` Class is deleted (decision 5) | U1 |
| §2.9 | Providers: F2 `next.queue` → S3, S4, S6, S7; F2 `UI.whenVisible`, `UI.autoSheet`, `UI.sections` → every page; F4 `estimate.gains / need / projection`, `progress.pace` → S1, S3, S6, S7, F2; F5 `habits`, `types.match` → S1, F2, F3, S4, S10; T-bank `check.check_item` → F6; T-bank `cb-ingest` → F5; F4 `quarantine` → F5, S3, S5, S8; S8 `compete.climb`, the Country practice board and `closing_soon` (private contests the learner joined, closing within 24 h) → S1, F2, S3; S7 `plan.pace` → S1, F2; S9 `words.me_stats.saved` → S1 | all |
| §2.12 F2 | F2 also owns `server/next.py`, `web/sw.js`, `UI.nowStrip`. F1 owns `UI.localPhoto`. F5 owns `server/habits.py`, `server/types.py`. S1 owns `server/push.py`, `server/google.py`, `account.saved` and `web/link/**`. S2 is removed | U1, U2, U6, U18–U22, U26 |

---

## 4. Rejected

* **Offline pack** (outcomes #13, unfair-advantage #13): it needs a caching service worker, a
  client grading path and back-dated answers. The need is rare, and `UI.saveQueue` already
  rides out brief drops.
* **Practice confidence tagging on every question** (outcomes #6, most of it): most students
  won't tap Sure/Unsure/Guess each time, so the card would be empty. The data that already
  exists (guess flags, test confidence, strikes) feeds U7's "When you guess" line instead.
* **Classroom features** (a live class check on a projector, printable per-student class
  packs, per-question working with teacher comments): classes are removed by v2-decisions
  item 5, so these have nothing to attach to.
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
* **Swipe-up on the tab bar** (experience #10): at the bottom edge it collides with the iOS
  home indicator in the installed app and with Safari's bottom toolbar. The grip button and
  the hold shortcuts do the job without a gesture fight (U26).
* **Page sub-links inside the sidebar** (unfair-advantage sub-links gap): Me's 16 would take
  about 512px that the height budget needs for the nav itself. The sticky section bar gives
  the same one-click reach on every width (U26).
* **Glyphs locked until Strong** (the first U22 draft): on day one it left a new student
  fewer choices than theirs. Every glyph is free, and Strong adds a ring instead (U22).
* **"700 needs +15 min a day"** (outcomes target gap): there is no model from minutes to
  points that we could defend. The popover states points a week and where the points are.
* **A Speed preset in Modes** (experience prefs gap): U7's Speed drill, per skill, does this
  better.
