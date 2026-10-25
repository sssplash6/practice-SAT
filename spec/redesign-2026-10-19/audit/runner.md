# Audit: the answering surfaces (runner, session, test window, challenge, diagnostic)

Code-level only. `runner.css`, `runner.js` (runner 1232-2770, between 2771-2854; the review player is audit/review.md),
UI parts of `question.js`, `web/practice/session/*`, `web/test/*`, `web/challenge/index.html`, `web/diagnostic/*.html`.

Scope correction: only `/practice/session/` and `/test/` are chrome-free. `/challenge/` and the three
`/diagnostic/` pages call `UI.shell()` and have `#bar` + `#tabs`: they are ordinary shell pages (lobby,
board, email gate) and should follow the page rules, not the runner's. The daily challenge itself runs in
`/practice/session/` (`rn-challenge`).

## What a student sees

1440x900, practice, math (no passage, nothing docked). Column `max-width: 740` centred, about 350px empty
each side. Vertical stack before the stem: top bar 64, `.rn-col` top pad `clamp(14px,3vh,32px)` = 27, rail
(16 segs + 6 + 16 railtext + 14 margin) = 52, `.rn-qstrip` 48, `.rn-why` 29, `.rn-q` margin 22. **Stem starts
at about 242px (27% of the height).** Fixed footer 68, so the stem plus four options (4 x 52 + 3 x 10 + 26)
get 590px. Bottom padding `calc(68px + 72px)` = 140.
1440x900, practice R&W: passage pane 440 on the left (`--passage-w`), the column centred in the remaining
~1000px track, so a ~130px dead gutter sits between passage and question (Bluebook butts them at a divider).
1440x900, exam: top 64, pad 27, strip 30 (railtext hidden), `.rn-qhead` 36, 22. Stem at ~179px. Close to
Bluebook, plus the progress strip Bluebook does not have.
390x844, practice: top 56, pad 12, rail ~51 (the set title moves into railtext), qstrip ~94 (row 1 number,
skill, stopwatch; row 2 seven icon-over-label tools at 10.5px), why ~29, 22. **Stem at ~264px (31%).**
Footer before the answer is two rows (Sure / Not sure / Guessing full width, then Back, Mark, "3 / 10")
= ~112px + safe area. About 430px are left for stem and options on first paint.
390x844, exam: top 56, pad 12, strip 30, qhead 44, 22: stem at ~164px. Footer one row.

## A. Purpose and primary action

- Session and test window: one job (answer this question), one primary (footer Check / Sure, then Next pill,
  `runner.js:1913-1927`). Clear. Primary sits in the fixed footer on every size; good.
- Summary (session.js:369+): purpose is clear (score, then next). Primary is the next-set pill; fine.
- Test lobby (test.js:205-277): primary "Enter fullscreen and begin"; kicker + h1 + 5-7 fact rows with icons
  before it. Primary lands ~430px down at 1440x900 inside a wash card. Acceptable, heavier than needed.
- Challenge page: primary Start/Resume is top right, fine; but the page shows a hardcoded "10 / questions ·
  16 min" before (and if) the API answers (challenge/index.html:41-43).
- Diagnostic index: one card, one Start. No `h1` on the page (same on challenge): a11y gap.

## B. Whitespace (concrete)

| Where | Now | Note |
|---|---|---|
| `.rn-col` padding | clamp(14,3vh,32) top, foot+72 bottom (phone foot+96) | 72 extra under content is slack |
| `.rn-rail` | 52px incl. 14 margin | can live in the top bar edge |
| `.rn-q` margin-top / `.opts` margin-top | 22 / 26 (ui.css:1931) | 16 / 20 enough |
| `.ws-cover`, `.spr` margin-top | 26 | 20 |
| `.verdict` margin-top, `.ws-bar` margin-top | 22 / 22 | 16 |
| `.rn-paused` | margin 12vh, padding 32/28 | fine (rare) |
| Summary `.psum` (session index.html:45) | pad 32/120, gap 40, max 860 | 16/48, gap 24; 290px dead each side at 1440 |
| Summary score `.sm-score .num` (:58) | 96px (72 phone) | off scale; 56 max |
| `.ps-state` / `.ps-skel` (:22, :25) | 72 / 88 top | skeleton does not mirror the runner frame: layout jump |
| Test `.tw-body` (test index.html:32) | clamp(20,5vh,48) top, 120 bottom, max 640 | 16 top, 48 bottom |
| `.tw-card` (:35) | pad 28, wash fill | no card needed; plain column |
| Challenge `.days` (:23) | margin-top 30 | 16 |
| Diagnostic `.door` | pad 28, radius 14 hardcoded, max 760 | page header instead |

## C. Always-on, not essential

What FOLD (ui.js ~2792) catches here: inside `.ws` only `.x-card` and `.spr-rule` fold (every other
FOLD_SEL class inside `.ws` is skipped by `foldOne`). Outside `.ws`: test.js `.tw-lead` lines over 70 chars
(the Time's up line, test.js:626, folds its second sentence) and the pressure-check `.help` (test.js:759).
`.cyw-lead` (Bluebook's own sentence), `.rn-why`, `.sm-note` are not caught; `.rn-nudge` is `role=status`
and skipped. `.rn-passage` and `.q-passage` carry `data-nofold`: correct.

- `.rn-why` "why this one" line (runner.js:1805-1813): always on, and the same text is the "Why this one" row
  of Details (runner.js:2332). Fold into Details or a hover tip on the skill name.
- Per-question stopwatch `.rn-watch` (`0:42 / 1:35` + bar) next to the top clock + `.t-delta` pace line:
  three time readouts at once in a timed practice set. Stopwatch could show only past 50% of budget (pref kept).
- Railtext "3 of 10 · 2 right · 2 in a row" (runner.js:1864-1874): "3 of 10" repeats the footer navigator
  label (runner.js:1905).
- Verdict tail (question.js:1335-1430): mastery, crowd ("Everyone: 62%..."), formula, then, saved note all
  stack under the verdict head before the explanation. On wide practice screens these are side-column material.
- Test lobby facts list (test.js:213-242): 5-7 rows each with a decorative icon. Keep the text, lose the icons.
- Summary: "Set complete · date" kicker over the score; four breakdown folds already folded (good).

## D. Side-panel use (Bluebook fidelity kept)

- The right slot `.rn-slot` (300px, `runner.js:1511-1551`) opens on demand from 1180px for Reference, Notes,
  "Entering your answer". At 1440 there is room for it without squeezing the column (1440-316-32 = 1092 > 740).
- Practice only (not the test window): a "Details" tab in the slot can carry what the Details popover
  (runner.js:2314-2338) and the verdict tail show: why this one, you and this type, everyone, formula, the
  exact-question link. Open by default from 1280 in practice, closable and remembered; popover below 1280.
- The test window keeps Bluebook's layout: slot only for Reference / Notes / grid-in directions (the
  automatic grid-in directions panel, runner.js:1742-1755, already mirrors Bluebook's left panel).
- R&W passage: column should sit next to the pane (`justify-self: start` when `.has-passage`), not centred.

## E. Redundancy

- Mark: qstrip `markB` (runner.js:1374) + phone footer `markFoot` (:1419, shown by runner.css:1115) in
  practice = two Mark buttons on a phone (exam hides the strip one, runner.css:1104). After the reveal the
  action row adds a third (`questionActions` mark, question.js:1863).
- After the reveal, Note, History and Report also appear twice: qstrip tools (runner.js:1376-1380) and the
  verdict's action row (question.js:1864-1879, wired by `actionsCtx` runner.js:1660-1669). Same action,
  two labels: "Attempts" (strip) vs "History" (row).
- "Explanation" three times on a right answer: `.x-toggle` button, the fold summary ui.js adds, the card's
  own `h3.x-title` (question.js:1568).
- Exam More menu repeats Directions, Notes, Scratch, Report, Save and exit (runner.js:2355-2371). Fine as
  phone fallbacks; on desktop they are duplicates.
- Lobby: top bar title `S.section` and the kicker "Math · #3" above the h1 (test.js:211).
- Print view (finished set): every question renders in review mode with its verdict and explanation inline,
  then the key section repeats answer, rationale, reasons and steps (session.js:600-626).
- Challenge page loads the board twice (paint `c.board`, then `showDay(0)` fetches it again, :105-106).

## F. Local overrides, hardcoded values, off-scale

- Overrides of shared buttons: `.rn-next` 44px + asymmetric padding (runner.css:620) vs `.pill` 42;
  `.split-check .sc-part` (runner.css:315) restyles `.pill`/`.btn` to `--ctl`, 14.5px; `.sm-next .btn`
  weight 500 (session :71); `.cover-acts .btn` paper fill (runner.css:172).
- Duplicate components: four exit buttons (`.rn-exit` runner.css:413, `.rv-close` :806, `.sm-exit` session
  :41, `.tw-exit` test :27) with radius 10/10/8/8; two navigator pills (`.rn-navb` :614, `.rv-navpill` :816);
  seven chip variants (`.rn-cond`, `.rn-fmt`, `.ws-fmt`, `.trap-chip`, `.rn-again`, `.rv-tag`, `.tw-chip`).
- Hardcoded colours: `rgba(30,30,30,.18)` (runner.css:309), `rgba(30,30,30,.35)` scratch-bar shadow (:767),
  `#999`, `#fff`, `#000` in session print CSS (fine for print), `'#3F3F3F'` fallback (runner.js:1010).
- 25 font sizes in scope CSS (9 to 96px). Phone labels at 10px (`.rn-tools .rn-tool`, `.rn-exit`,
  `.rn-markfoot`, runner.css:1081-1117) are under the micro step (11.5). Hero numbers 96 / 104 / 72px with
  `.num` weight 900 (session :58, challenge :21, diagnostic :18).
- 39 `var(--mono)` uses in runner.css; most are words: railtext, `.t-delta`, `.rn-saved`, `.v-bit`,
  `.ws-tries`, `.cyw-status`, `.cyw-pace`, `.rn-paused-t` ("12:34 left"), `.opt.picked.saved::after`.
- Radius: no 999px in CSS; `test.js:163` skeleton `r: 999` for a 10px-corner pill. `.strike` is a 40px round
  button (Bluebook's circled-letter strike: keep, fidelity exception; check-ui.py does not see it).
- Inline styles: `style="margin:0"` on the challenge Save (:51), skeleton `width: 60%` (signup :31). Width
  styles on bars from JS are fine.
- Gradients: skipped-segment hatch, mixed half fill, hold ring (runner.css:508-509, 129) encode state: keep.
  `.calc-grip` stripes (:368) are decoration on a grip; acceptable.

## G. AI-slop tells

- Uppercase letter-spaced mono: `.rn-cond` TRAINING / RANKED (runner.css:425), `.rn-fmt` GRID-IN (:542),
  `.opt-cap` YOUR ANSWER (:91), `.trap-chip` plus `toUpperCase()` in JS (question.js:1365), `.refd-g`
  (:776), `.rv-tlh` (:1191); `letter-spacing: .08em` on sentence-case `.ws-type` (:43).
- `.k` kickers above titles: "Set complete · date", "Diagnostic" over each h1 (signup x3), lobby kicker,
  "Paused", "Module 1 pace", "These cost the route"; `.k` used as form labels (signup :20, note editor
  runner.js:1612).
- Decorative icons: lobby facts, `.tw-moments` trophy/check (test.js:736).
- Orange-tinted callout boxes everywhere: `.sm-note` with a 3px amber left bar (session :63, the classic
  slop callout), `.rn-nudge`, `.spr-nudge`, `.ws-rule`, `.rn-paused`, `.rn-between-count`, `.tw-card`.
  Wash should mean state (picked, correct), not "notice".
- Stat-tile grids: between modules (4 tiles, runner.js:2813) and Check your work (`stat-v` 40px,
  runner.css:665).
- Zebra rows on the challenge board (`.line:nth-child(odd)`, :27) instead of hairline rows.

## H. Copy

- Same action, different names: Back is "Previous" in practice, "Back" in the test (runner.js:1417); Twin /
  rematch menu says "Start over with these exact questions (tests memory)" in the run and "Retake these exact
  questions (tests memory)" on the summary (session.js:319, 565); "Rematch: ..." vs "Rematch · ...".
- "Check asks how sure" (runner.js:2382): reads as a statement. "Ask how sure on Check".
- "Question overview" (practice navigator) vs "Questions" (test). One name.
- "Then → Now" (session.js:487): Title Case plus arrow. "Then and now".
- "Still open from before · see Mistakes" (session.js:429): "Older open mistakes".
- "You were sure, and it's wrong: this kind costs points on test day, because you wouldn't re-check it. It
  comes back first." (question.js:1370): explains. "Sure, but wrong. It comes back first."
- Stale fallback "Reports open here soon. Use Send feedback in the menu for now." (runner.js:2304, 3826,
  question.js:1876) while `UI.report` exists.
- Challenge summary pill "Board" goes to `/compete/` (session.js:545); every other link says `/challenge/`.
- Em dashes as empty values: the hidden-timer placeholder (runner.js:192), between tiles (:2814-2815), `pct`
  (session.js:21), print key (:623), Time's up line (test.js:626).

## I. CSS / layout bugs

1. **`.pv` collision on the session page.** The print view wrapper rule `.pv { max-width: 760px; margin: 0 auto;
   padding: 24px 16px 80px }` (session index.html:150) also hits the grid-in preview value `span.pv`
   (question.js:350) inside `.spr-preview` (a flex row). Every practice grid-in: typing an answer centres the
   preview and grows the row to ~125px.
2. **`.split` is taken.** DIRECTION section 4 plans a shared `.split` layout; runner.css:306-309 already styles `.split`
   (inline-flex split buttons), and question.js:1791 / 1891 and runner.js `.rn-check.split` use it on every
   page that loads runner.css (Today, Review, Results report, Words run). The new primitive needs another name.
3. **Explanation double toggle.** On a right answer the card starts `hidden` behind `.x-toggle`
   (question.js:1585-1590). After a tap the fold (which ignores hidden cards) wraps it in a closed
   `details.fold` within ~250ms: the card appears, then collapses behind a second "Explanation". The fold
   also closes cards opened by "Always open explanations" or by a miss until the student opens one fold.
4. **Fold rescans 4 times a second in every sitting.** The timer replaces the Hide button's children on
   every 250ms paint (runner.js:196) and the stopwatch rebuilds every second (:1823); both are childList
   mutations, so ui.js's observer re-runs `foldScan` continuously.
5. **Print view ignores "Include answer key".** Unchecked only hides `.pv-key` (session :163); the inline
   review-mode verdicts, marked options and explanations still print. FOLD_OFF tests the path only, so
   explanations are folded on the screen view of `?print=1` (opened again by beforeprint).
6. Challenge: `?day=` from Today's "Yesterday: #4" link (index.html:2636) is ignored; local `.line` rule
   (:25-27) also styles any `.skel.line` / `.badge.line` the shell draws on that page.
7. Right-slot tabs can overflow: "Reference" + "Notes 3" + "Entering your answer" at 12px plus the close
   button need ~305px in the 300px slot (runner.css:481-495, exam grid-ins). Verify.
8. Dead CSS: `.rn-qstrip .rn-qtools { padding-left: 34px }` (runner.css:546) and the 999px tool rule
   (:558-560) are always overridden (session :28-35, `.rn-qhead .tool` :567).
9. `.rn-col` max-width uses `--rn-pad` (20) while docked states pad 16 (:462-463): 8px wider than meant.

## Redesign proposals (ranked)

1. **Rename the planned layout primitive before the shared pass** (DIRECTION section 4): `.split` to e.g.
   `.cols` + `aside.cols-side`. Zero UI change here. Risk if skipped: high (breaks Check and Twin site-wide).
2. **Fix the `.pv` collision**: rename the print wrapper to `.pv-page` (session index.html:150-163,
   session.js:581). Risk low.
3. **One Explanation control.** Drop `.x-toggle` and the `h3.x-title` (question.js:1568, 1585-1590) and let
   the fold be the toggle; question.js adds `data-nofold` when the card must open (review, example, quiz,
   `open_explanations`, a miss, a sure miss). Plus runner.js:196 rebuilds the Hide button only when
   `hidden` changes, :1823 only when the text changes. Risk low; behaviour kept (pref still forces open).
4. **Print key toggle hides everything keyed**: `.pv.nokey .ws-verdict, .pv.nokey .opt-cap, .pv.nokey .mk
   { display: none }` and neutral `.opt.ok` under `.nokey`; FOLD_OFF also on `?print=1` (shared ask). Risk low.
5. **BIG: give the stem 60-80px back (practice).** Draw the progress segments as the top bar's bottom edge
   (16px hit area over the hairline, tooltips and keyboard group kept), move railtext's right / skipped /
   streak beside the title (desktop) and keep the phone's line; `.rn-col` top 16, `.rn-q` 16, `.opts` and
   `.spr` 20, bottom foot+32; `.rn-qstrip` box becomes a bottom hairline. Exam: same strip-in-bar move
   (Bluebook's line sits there). Files: runner.js:1346-1350, 1832-1876; runner.css:462, 499-531, 583.
   Risk medium (strip clicks, pace ticks, focus order). Stem at ~180px (1440) and ~210px (phone).
6. **De-duplicate practice controls.** Phone: hide `.rn-practice .rn-qstrip .rn-mark` (footer has Mark, as
   the exam does). After the reveal, `actionsCtx` passes a `compact` flag so the action row keeps Twin and
   Desmos way only; Mark, Note, History, Report stay in the strip (runner.js:1660-1669, question.js:1863-1879).
   One label "History" with its count. Keys M, O, Y, R unchanged. Risk low.
7. **BIG: practice context column from 1280.** A "Details" tab in `.rn-slot` (open by default in practice,
   remembered when closed) holds why this one, you and this type, everyone, formula, exact-question link,
   and after the reveal the verdict tail (mastery, crowd, formula, then, saved note). `.rn-why` leaves the
   column; below 1280 Details stays the popover and the tail stays in the verdict. Test window untouched.
   Files: runner.js:1511-1551, 2314-2338, 1805-1813; question.js verdict tail behind a `side` option.
   Risk medium (layout() widths, slot float rules, notes tab focus).
8. **R&W passage beside the question**: `.rn.has-passage .rn-col { justify-self: start }` with a 24px gap
   (runner.css:462-463). Closer to Bluebook. Risk low.
9. **BIG: Summary as a two-column page from 1100.** Left (sticky): score at 56px, what changed, next
   actions. Right: Review list, then the folds. `.psum` pad 16/48, gap 24; `.sm-note` loses the amber bar;
   kicker goes (date joins `.sm-meta`). Optional: render the summary inside `UI.shell` since the set is over
   (needs `#bar`/`#tabs` on the session page; flag to the user). Risk medium.
10. **Typography to the scale** in runner.css, session and test inline CSS: words out of mono (list in F),
    uppercase gone (5 rules + question.js:1365), 25 sizes onto DIRECTION's 8, phone tool labels 11px min,
    hero numbers 96/104 to 56 (summary) and 32 (challenge, diagnostic). Keep mono for clocks, `.rn-qn`,
    kbd, cell numbers. Risk low-medium (tool rows at 390 must still fit seven tools).
11. **One exit, one nav pill, one badge**: `.sm-exit`, `.tw-exit` reuse `.rn-exit`; `.rv-navpill` reuses
    `.rn-navb`; the seven chips become the shared micro badge (8px corners, 11.5px/500, sentence case).
    Grep each class first; keep old names as aliases if another file uses them. Risk low.
12. **Wash means state.** `.rn-nudge`, `.spr-nudge`, `.ws-rule`, `.sm-note`, `.rn-paused`,
    `.rn-between-count`, `.tw-card` go to `--tile` or plain text with a bold lead. Risk low.
13. **Test window screens**: lobby without the card, kicker and fact icons, facts as hairline rows, settings
    line and Begin on one row at 1440; between modules: four stat tiles become one meta line (`12 of 22
    answered · 2 marked · 31:40 used · 0:00 away`); Time's up line gets `data-nofold` (test.js:626);
    `.rn-cond` sentence case. Risk low.
14. **Challenge page**: add an h1, read `?day=`, no placeholder figures (skeleton instead), rename `.line` to
    `.ch-row`, hairline rows, drop the inline style, one board fetch. Risk low.
15. **Diagnostic pages**: h1 in place of `.k` + 104px number (index), `.label` for form labels and no
    kicker (signup), facts as a meta line. Risk low.
16. Copy fixes from H; em dash placeholders to `-` (or `--:--` for the hidden clock); test.js:163 skeleton
    radius 10; session skeleton mirrors the runner frame (64px bar, 740 column); delete dead CSS (I8).

## Shared asks (ui.css / ui.js / kit.js, lead only)

- Rename DIRECTION's `.split` layout (I2).
- Fold: honour `data-nofold` set on `.x-card` by question.js (already generic), and skip `.x-card` that has
  an `.x-toggle` sibling until proposal 3 lands; FOLD_OFF also for `?print=1`; consider ignoring mutations
  inside `.timer` and `.rn-watch` (or a longer debounce while `html.has-runner`).
- `.spr-rule` in FOLD_SEL folds a line whose only visible content is the "Entry rules" link; the summary
  shows the sr-only rule text. Drop it from FOLD_SEL, or make the rule a visible `.help` line.
- `.meta` is mono in ui.css:766 and is used for words all over this scope; DIRECTION's meta is Geist.
- `.k` to sentence case affects the note editor label, `.abox .k`, Check your work's "Show", `.t-k`.
- A shared micro badge (proposal 11) and `.stat-v` at the figure step (Check your work overrides to 40px).
