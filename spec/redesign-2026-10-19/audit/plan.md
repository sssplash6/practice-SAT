# Audit: Plan (web/plan/**, web/assets/plan-ui.js)

Code-level only. States read: landing (no plan: with data, without data, with a draft), wizard (create, edit,
loading, offline), plan view (Plan, Progress, Plans tabs), older plan `?id=`, shared `?view=`, test-day sheet
`?print=sheet`, print. Files: index.html (542 lines, 500 of them page CSS), plan.js 1778, progress.js 325,
wizard.js 768, plan-ui.js 405 (also loaded by Today, web/index.html:859, so its CSS changes reach Today).
Content width today: 1440 wide = 1192 main, `.page` max 1120 minus 2x40 gutter = 1040. Phone: 390 - 2x16 = 358.

## A. Purpose and primary action

- Plan view answers "what do I do today, and am I on track". Primary: `Start today · 3 tasks · 40 min` (.pill,
  plan.js:758). Order above it (plan.js:302): Updating line, title row, 4 stat tiles, banners, sticky tab bar,
  then the Day card head. Start sits at about 411px from the top at 1440x900 with no banner, about 507 with
  one, about 603 with two (banner ~80px each). Phone 390x844: about 458px, 634 with one banner, below the
  fold (780 visible above the tabs) with two; `.pl-thumb` (index.html:160) then shows a second Start.
- Landing (no plan): primary `Use this plan` (with data) or `Create my plan`. With a draft the hero button
  becomes `Start over` (.btn, plan.js:157) and the real next step, `Continue` (.pill.sm), sits at the bottom of
  the hero in the draft tile (plan.js:161, 217). The draft's Continue should be the first, primary action.
- Wizard: `Next` / `Create plan` (.pill) in the sticky foot. Clear. Glance on the right is already a context column.
- Progress tab: no single action; it is a dashboard of 8 to 12 cards. Plans tab: `New plan` pill sm in card head.
- Test-day sheet: reading page, `Print` btn sm. Fine.

## B. Whitespace (concrete)

- `.pl { padding-bottom: 120px }` (index.html:21) on top of `.page` 88px: 208px of empty paper under every tab.
- Title to Start: tiles margin 14 + ~150 tall, banners margin 16, tab bar margin 20 + padding 8+8 (index.html:84),
  `.pl-cols` margin 16 + gap 16 (88), card pad 22, `.pl-dayhead` gap 10, `.pl-day-go` margin 12. Five stacked
  bands before the task: the main whitespace cost on this page.
- Task rows: `.trow` padding 14px 0 (plan-ui.js:62); next row ~94px with its detail line, others ~66px.
- `.pl-sec` margin 18 (24), `.pg` gap 16 (341), `.pg-nums` gap 14/18, `.pl-foot` 14+14 (103), `.pl-rest` 18 top (106).
- Landing hero padding 36, radius 18, gap 28 (167); `.pl-ready` padding 18, radius 14 (172); h1 up to 44px (168).
- Wizard: `.wz-steps` margin 18 and 44px rows on a fine pointer (209-211), `.wz-body` gap 28 margin 22 (219),
  `.wz-step` gap 22 (220), `.wz-glance` padding 18 gap 14 (309), `.wz-foot` margin-top 26 (322).
- `.wz-glance { top: 88px }` (309): there is no top bar on desktop, so it sticks 88px down and its max-height
  loses 184px (calc(100vh - 88px - 96px)).
- Progress `.pg` is 2 columns with align-items start: "Since" (~120px) sits beside "Score path" (~290px), a
  ~170px hole; same for Checks beside Weeks.

## C. Always-on non-essentials, and what the fold catches

- **The fold catches nothing on /plan/.** `<div id="plan" aria-live="off">` (index.html:530) matches `[aria-live]`
  in FOLD_SKIP (ui.js:2793), and every view, the wizard and the sheet render inside #plan. Today that saves:
  - landing `.lead` (83 chars, plan.js:152) would fold into "Mistakes first, then your focus skills, and a fresh test…";
  - wizard `.wz-note` boxes 75+ chars would fold, and the fold hides their button with them: rhythm "Use that"
    (wizard.js:451), "Weekly instead" (500). These need `data-nofold` or the button outside the folded text;
  - test-day sheet rationale `.help` (plan.js:1591) would fold on screen (FOLD_OFF tests the path, not `?print=`).
  - Short `.help` lines (under 70) never fold: plan-ui.js:798 note, plan.js:923, wizard.js:342, 615, 625.
- Plan banners use `.pl-banner > p`, not `.banner-t`, so they never fold; up to 6 stack (built, drift,
  registration, server, behind, missed: plan.js:544-591).
- Already hidden in a hover-only `title` (unreachable on touch, so phone loses them): tile sub-lines (plan.js:493-498:
  "to Mar 14", "12 study days · 3 tests left", "fits with 4 h to spare", "At this pace 600-650", R&W/Total,
  streak), the plan settings line (h1 title, 332), Coming up skills (1346), phase purpose (1382), a row's hidden
  detail (plan-ui.js:252), Map squares (1367). Brief rule: phone shows everything desktop shows.
- Candidates to fold or move: landing How it works (3 cards) and the bank-stats line (plan.js:174, 240-252);
  wizard step intros (wizard.js:301, 374, 443, 587) and "Your draft saves as you go." (84); "1 / 4" (159);
  Day head "45 min planned" (739) beside a Start label that says the minutes; Plans rows' 3-4 always-on btn.sm
  (1641-1657); Progress infoTips are fine (on demand).

## D. Sidebars

- Plan tab already has a side column: `.pl-cols` 7.5fr/4.5fr from 1080 (88-90) = 640 / 384px at 1440. It holds
  Coming up, Map, Habits, Sweep, Phases. The four tiles sit full width above everything. They are context, not
  task: they belong at the top of that side column, which should be the shared sticky `aside.split-side`.
- Wizard Glance (`.wz-glance`, 320px) is a right column already; move it onto `.split-side` (fix top 88).
- Progress: "Since" numbers, checkpoint summary and the planned-time split are side material; charts and the
  two tables stay in main.
- Test-day sheet already does this (`.pl-sheet` 1fr/340, What to bring sticky, 460-462).
- Left nav: nothing new. The shell's tab menu links `/plan/#today` and `/plan/#week` (ui.js:1998-1999) but no
  element has those ids (see I).

## E. Redundancy (page and shell)

- With the shell's planned Now block (sidebar from 700px tall): Up next + Start = the Day card's Start and
  `.pl-thumb`; Today minutes meter = the Day meter (plan.js:770) and the This week tile; exam countdown = tile 1;
  streak = tile 4 sub-line; registration = tile 1 link (417), the registration banner (565) and the side card's
  regLine (ui.js:1608). The page already opts out of the Now strip (`now: false`, index.html:536).
- Exam date said 4 times on one screen: auto title "Mar 14 · 650" (280), tile 1, the built banner's chip, calendar.
- Week said twice: tile 4 (minutes + dots) and the week head in the Calendar card (Tasks meter, plan.js:1319-1329).
- Phase said 3 times: Phases card, Day tag (735), Coming up note "Sharpen from ..." (1354), plus calendar marks.
- Day card: Start label "3 tasks · 40 min" + meter "1 of 4 tasks · 20 of 45 min · 25 min left" + "45 min planned".
- Progress tab repeats /results/ (domains, skills table, "Every result ›") and /me/#pace (pace card). Keep (zero
  loss) but it argues for folding the two long tables.
- Landing with data: "Your plan, ready" calendar + Day 1 rows, then "Your numbers", then How it works, then the
  bank line: the last two say what the first already shows.

## F. Local overrides, tokens, sizes, inline styles

- Shared buttons overridden: `.pl-day-go .pill { height: 40px }` (94; pill is 42); `.pl-day-go .btn.pl-have`
  40px (95); `.pl .quiet { margin: 0; padding: 6px 10px }` (385) breaks the shared tap-area trick, then patched
  with `margin-left: -10px` at 386, 394, 395, 254; `.trow-act .quiet` (plan-ui.js:94-95); leversPop `.btn`
  inline `height: auto; white-space: normal` (plan.js:526) wraps past 48px; `.pl-banner .chips > button` 34/13px (83).
- Duplicates of shared parts: `.pl .tag` (29-32, radius 999px) = `.badge`; `.pl-banner` (78-82) = `.banner`;
  `.pl .x` (35) = `.banner > .x`; `.pl-big` mono 28 (45) = `.stat-v`; `.pl-track` vs `.meter-bar`.
- `.pl .k, .pl .stat-k { 11.5px }` (384), `.pl .card-head { 12px }` (34), `.pl-wd .k`/`.wplan-day .k` letter-spacing.
- Hardcoded colour: `rgba(30,30,30,.08)` in `.wz-seg3` (255), `rgba(0,0,0,.18)` on `.pl-ghost` (437, floats: ok, tokenise).
- Font sizes in the page CSS: 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 16, 18, 22, 24, 26,
  28, 30, clamp(30-44): 22 sizes against a scale of 8. h1s are 28/800 (40, 208), hero 44/800.
- Uppercase: `.wz-grows dt` (320), `.pg-nums dt` (345), `.pg-grid .hd` (353), `.pl-thumb .soft` (163); in JS the
  literal 'STUDY'/'REST' (wizard.js:461) and `UI.date(..., 'eyebrow')` which upper-cases (plan.js:733, kit.js:215).
- Mono for words (30 `var(--mono)` in the page CSS): `.pl-up .d` dates (144), `.pl-moving` sentence (444),
  `.pl-drop` (442), `.pl-bank` marketing line (179), `.wz-split` labels (296), `.wz-wd span/select` (271, 273),
  `.pl-dow` (203), `.pl-have` chips (99), `.trow-meta` (plan-ui.js:88).
- Em dashes in UI strings: progress.js:20 (`pct` returns an em dash), wizard.js:230 (empty week cell shows one).
- Inline styles: plan.js 41, progress.js 11, wizard.js 9. Worst: calendarSheet option boxes with tile background
  and radius 12 (a card inside the sheet, plan.js:1707-1709), progress.js:98 `color: var(--ink)`, 206 grid override,
  284/296 label margins, plan.js:772, 1327, 1456 margin-tops.
- 999px: `.pl .tag` only (circles for dots, checkboxes and step numbers are marks, not buttons).

## G. AI-slop tells

- Landing: tinted wash hero with uppercase kicker "STUDY PLAN", 44px slogan h1, grey lead, "About a minute ·
  free · as many plans as you like"; three equal numbered-circle cards "Four questions / Every day planned / It
  keeps up" (180-183, 246-252); a mono bragging line "386 question types · 19 skills · a new section every
  sitting · every wrong answer named" (240-245).
- Four equal stat tiles with mono uppercase labels; numbered circles in the wizard stepper.
- Aphorisms: "A plan you keep beats one you drop." (wizard.js:443), "Tests measure; practice raises the score." (500).
- Glyph decoration: ✎ on every built chip (plan.js:596), "Day done ✓" (876), ▾/▴ appended to labels, › on 10+ links.

## H. Copy

- Slogans to facts: h1 "A plan to your score, one day at a time" -> "Study plan"; drop "free".
- Step intros explain the UI ("Start from your real number, so the plan is built for the gap you have."): delete
  or move to the field `?`. "Your draft saves as you go." -> fold into the foot status ("Saved" / "Can't save").
- Mixed names: "R&W", "Reading & Writing", "Reading and Writing" (wizard.js:336 vs 341 vs 404).
- Tile 3 label changes by state: "Plan done" / "Days studied" / "The plan" (461-470): pick one ("Plan done").
- Banner: "3 of 5 study days missed in the last 7 · you average 22 min on a study day; the plan asks 45." -> "Behind:
  3 of 5 study days missed this week" + actions; the averages to the fold.
- "Take this week's test ›" (445) and "What changes it ›" (451): drop the › glyph (quiet links read as links).
- 'STUDY'/'REST' -> "Study"/"Rest". "Day ⋯" (741) -> an icon button labelled "Day options".
- "Your plan, ready" kicker, "Live plan" kicker, "Draft · step 2 of 4" are fine as plain meta.

## I. CSS / layout bugs

1. Fold disabled page-wide by `aria-live="off"` on #plan (index.html:530). Drop the attribute (off is the default).
2. Shell links `/plan/#today`, `/plan/#week` (ui.js:1998-1999) have no targets; no `id` on R.day or the week head.
3. Phone `.pl-tabbar { top: var(--bar, 56px) }` (85): `--bar` is 64px (ui.css:137), the phone bar is 56px, so
   rows show through an 8px slit under the bar; `scroll-margin-top: 128px` (405) assumes the same.
4. `.wz-glance` sticky at 88px with no desktop bar (309-310); `.pl-thumb` bottom 68px over 64px tabs (160).
5. Tile sub-lines, plan settings, Coming up topics and phase purposes only in `title` (touch can't reach). See C.
6. Dead after the week strip was removed: drawWeek computes `changed` (plan.js:1313) and `theme` (1331) and draws
   neither, so the L15 "the plan changed this day" dot and the week theme no longer show anywhere on screen;
   `markTargets` still queries `.pl-wd[data-date]` (1083). Dead CSS: `.pl-week`, `.pl-wd*`, `.pl-wdn` (108-131, 445),
   `.pl-theme` (139), `.pl-print-months` (133), `.wz-range` (231-232), `.pl-have .chips` (98-99), second
   `.pl-dots [data-s=missed] i::after` (61 vs 424). `changeLog()` (661) is never called; `.pl-log` styles idle.
7. "Review week" (1322) needs `UI.weekReview`, which nothing defines: the button never renders.
8. leversPop buttons can exceed 48px (inline style, invisible to check-ui).
9. `.pg` 2-col holes (B). `new MutationObserver(tidy)` on the score chart is never disconnected (progress.js:87);
   each Progress redraw adds one.
10. `.wz-dates` declared twice (237, 244); `.pl-big small` twice (46, 49).

## Redesign proposals (ranked)

1. **BIG: plan view on `.split`.** Main: Day card, then the Calendar card (week head + month). `aside.split-side`
   (sticky, 300px, from 1280): a compact status block replacing the 4 tiles (Days to exam, Score with its track,
   pace tag and "What changes it", Plan done, This week dots and minutes), then Coming up, Phases, Map, Habits,
   Sweep. Below 1280 the aside stacks after the Day card (phone: Day card first, status after; the swipe strip can
   stay for the status). Start moves from ~411-603px to ~120px at 1440, ~240px on phone. Files: plan.js:282-312,
   389-503, 637-649; index.html:39-73, 88-90. Risk: medium (drag targets, `R.cal` scroll targets, print keeps tiles
   via `.print-keep`; keep every tile action: Set N min, Register by, Take this week's test, What changes it).
2. **Title row = h1 + tabs + actions.** `h1` 22/600, the Plan/Progress/Plans tablist on the same row from 760px,
   Edit + ⋯ at the end; one visible meta line with the plan settings (now the h1 `title`, 332). Drop the tab bar
   margin and padding (84). Phone: tabs under the title, sticky at 56px (fixes I3). Risk: low.
3. **Banners: one at a time.** Render on shared `.banner` / `.banner-t` / `.banner-act` (drop `.pl-banner`,
   `.pl .x`), show the most urgent (missed > behind > drift > registration > built > server) and a quiet "2 more"
   that expands the rest. Text one line, detail into `.banner-t` so it folds. plan.js:536-591. Risk: low; keep
   every action and dismiss key.
4. **Turn the fold on.** Remove `aria-live="off"` (index.html:530). Add `data-nofold` to `.wz-note` boxes that hold
   a button (wizard.js:307-314, 451, 485, 490, 500) or put the button outside the text. Delete the landing lead.
   Sheet: `data-nofold` on the rationale (plan.js:1591). Risk: low.
5. **Nothing only in `title`.** Tile sub-lines, Coming up topics, phase purposes, row detail: visible meta in the
   aside (there is room) or `.reveal` (always on coarse pointers). plan.js:493-498, 332, 1346, 1382; plan-ui.js:252.
   Restores phone parity. Risk: low.
6. **Day card tightened.** Head: "Today · Tue, Oct 14" as the h2 (no eyebrow caps), one meta line "Practice ·
   Build · 45 min", Day options as an icon button. Meter only once something is done (zero is not news). `.trow`
   padding 10 (rows ~52/76px). Restore the L15 changed-day dot on calendar cells (I6). Ids `today` on the Day card
   and `week` on the Calendar card (I2). plan.js:713-804, 1306-1334; plan-ui.js:61-62. Risk: low (plan-ui CSS also
   styles Today's rows; check web/index.html after).
7. **BIG: landing rebuilt as a page, not a hero.** Header h1 "Study plan" + primary action on one row (draft:
   Continue as the pill, Start over quiet; data: Use this plan, Adjust). Main: the ready plan (calendar + Day 1)
   or "A day in your plan". Aside: Your numbers, the mini tiles, Your plans. How it works becomes one `.help` line
   (folds); the bank line goes into it. Removes wash hero, kicker, 3 cards. plan.js:144-252; index.html:166-192.
   Risk: low; all text kept, one tap away.
8. **Wizard on `.split`.** Glance as `.split-side` with top 16 (fixes 88). Stepper 36px rows on fine pointers, no
   circles (number then name; ✓ when done). Drop "1 / 4" and "Your draft saves as you go." (status in the foot).
   Step intros deleted or a `?` by the step title. Gaps: body 28->16, step 22->14, foot margin 26->12. 'STUDY'/'REST'
   sentence case, not mono. wizard.js:83-86, 144-165, 301, 374, 443, 461, 587; index.html:207-338. Risk: low.
9. **Progress tab: main + aside.** Aside: Since numbers (as rows), checkpoint summary, planned-time split. Main one
   column: Score path, What your time bought, Ready on every skill, Domains, Study time, Checks, Weeks; "All 19
   skills" table folds (details, remembered). Fixes the 2-col holes. progress.js:37-173. Risk: low.
10. **Plans rows: `.reveal`.** Edit/Open visible; Make active, Duplicate, Remove reveal on hover/focus (always on
    phone). plan.js:1639-1659. Risk: low.
11. **Shared parts back.** `.tag` -> `.badge` / `.badge.line` / orange `.badge.n`-style (3 JS files); `.pl-big` ->
    `.stat-v`; delete `.pl .quiet` override and the four -10px patches; `.pl-day-go .pill` back to 42; leversPop
    as a `UI.menu` with sub lines instead of wrapped `.btn`s; calendarSheet options as hairline rows, no tinted box.
    Risk: low to medium (visual only; Today and Me have their own local `.tag`, change only plan's emitters).
12. **Type and mono pass.** Map every size to the 8-step scale; mono only for clocks and kbd (dates, counts,
    labels to Geist tabular); remove 4 uppercase rules and the 'eyebrow' call; em dashes in progress.js:20 and
    wizard.js:230 to an en dash or "none". Risk: low.
13. **Spacing.** `.pl` padding-bottom 120 -> 0 (phone keeps room for the thumb); `.pl-sec` 18->12; `.pl-cols`
    gap 16->12; card-head and tiles from tokens. Risk: none.
14. **Dead code.** Remove the dead CSS and `changeLog()`/`theme`/`markTargets` `.pl-wd` branch listed in I6, I10;
    disconnect the chart observer. Risk: none (grep confirms no other page uses `.pl-` classes).

## Shared asks (lead only)

- `.split` / `aside.split-side` and `.reveal` (DIRECTION 4, 5).
- Shell: extend `now: false` to hide the sidebar Now block on /plan/, as on Today; the page carries Start, exam,
  minutes and streak. Hides the side card's registration link here too (three today).
- `UI.date(..., 'eyebrow')` stops upper-casing (kit.js:215) or plan stops calling it.
- Fold: `FOLD_OFF` also skips `?print=` pages, or the sheet uses `data-nofold`.
- `.badge` corners to 8px (replaces `.pl .tag` 999px).

## Big changes to tell the user

- Plan view: tiles move into a right status column; the Day card and its Start come first (proposal 1).
- Plan tabs sit on the title row (2); banners show one at a time with "N more" (3).
- Landing loses the orange hero and the three How it works cards; same text, one tap away (7).
- Progress tab gets a side column and the skills table folds (9).
