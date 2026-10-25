# Premium audit: the answering screens (runner)

Scope: `web/practice/session/*` (runner + Summary), `web/test/*`, `web/challenge/index.html`, `web/diagnostic/*.html`,
`web/assets/runner.css`, `runner.js`, the UI parts of `question.js`. Read against passes/runner.md (rounds 1-2),
DIRECTION 0 and 9, ui.css tokens. Rule for this page: practice may gain depth, motion and reward; the test window
stays Bluebook-calm (section 3 and 5 say why per item). "(shared)" = a ui.css / kit.js ask for the lead.

## 1. First screen inventory

**Practice, math MC, Q3 of 10, untimed, confidence on, 1440x900** (Details opens by itself, runner.js:1610-1613):
- Buttons 28 + 10 rail segments: top bar 5 (Exit, Hide, Calculator, Reference, More; runner.js:1346-1371), strip
  6 icon tools (Mark, Eliminate, Highlight, Note, Details, Report; runner.js:1421), 4 options, 1-2 quiet under them
  (Hint · 1 of 3, Skip for now), footer 5 (Back, Question 3 of 10, Sure, Not sure, Guessing), Details column 4
  (3 tabs + close) + 2 Copy.
- Links 0. Chips/tags 3 kbd hints (Enter, ⇧Enter, I; question.js:1781-1785) + 0-2 badges (Grid-in, Again).
- Inputs 0. Boxes 8: top bar, ink number tile (runner.css:561), 4 option tiles, the Details card, the footer.
- Bars 2: the rail, the stopwatch's 56px bar (runner.css:578). Labels about 19: title, counts, clock digits,
  "elapsed", skill, type, difficulty, stopwatch, up to 10 Details `dt` (runner.js:2421-2431).
- Helper text 1-3 lines: "Why this one" sentence, "Not enough answers yet".
- Rows of controls before the stem (~140px): (1) top bar: Exit · title · counts | clock · Hide | 3 tools;
  (2) the rail on its edge; (3) strip: number · skill · type · difficulty · stopwatch · 6 icons.

**Practice, 390x844.** Buttons 20 + rail: top bar 3 (Exit, Hide, More), strip 5 icon-over-label tools, 4 options,
1-2 quiet, footer 6 on two rows (Sure / Not sure / Guessing; Back · Mark · 3 / 10). Boxes 6, bars 2, labels 7.
Before the stem (~200px): top bar, rail, the "Linear functions · 2 right" line, the info row, the 5-tool row. The
two-row footer (~128px) plus 256px above leaves ~460px for stem and options: option D often sits under the footer.

**Test window, math, 1440.** Buttons 18 + 22 segments: top bar 8 (Save and exit, Directions, Hide, Highlights &
Notes, Scratch, Calculator, Reference, More), Q head 3 (Mark for review, Eliminate, Report), 4 options, footer 3
(name or "Set your name", Question 1 of 22, Back + Next). 1 badge (Ranked). Rows before the stem: top bar, strip edge,
Q head; this matches Bluebook's header + Q bar and should stay. 390: 3 + 2 + 4 + 4, same rows.

**Summary, 1440** (7 / 10, a next set, words due): buttons ~22: Exit, pill, 2-3 `.btn`, More, Mark all incorrect,
~6 filter chips, 10 review rows; 5 folds below the fold. Boxes 0, cells 10, labels ~10, meta 2 lines. Rows of
controls before content: the next row under the score; Review head + the "Show" chip row before the list.
**Summary, 390:** score, 3 meta lines, 3 changed rows, then up to 5 full-width stacked buttons (pill, Fix, Same
settings, SAT words, More; session/index.html:146): ~260px of buttons before Review.

**Others.** Lobby: h1, 4-6 fact rows, settings line + Settings, Begin pill, 4 quiet links (test.js:203-271).
Between (Test-day): h1, meta line, countdown tile (22px clock, bar, 22-cell predict grid, Begin now), next-module
lines, Save and exit (runner.js:2899-2949). Challenge: h1, 28px count + meta, Start, 2-option seg, ~15 board rows.
Diagnostic: h1, meta, Start, 3 rows (calm already, but bare). Signup: h1, 3 fields, pill, 2 notes.

## 2. Clutter fixes

- **Defer:** Details column pre-answer shows only Why this one and You and this type; Skill, Question type,
  Difficulty, Format, Question ID, Link fold under one "Question info" disclosure (they repeat the strip);
  Everyone and Formula appear after the verdict (they are answer context). Keeps the column open (no column jump).
- **Defer:** the stopwatch bar until half the budget (text stays; runner.js:1906). The `.over` dot already exists.
- **Defer:** kbd chips on Sure / Not sure / Guessing / Next show on hover or keyboard focus and in a learner's
  first 3 sets (`satf.tap`-style counter); always in Keyboard shortcuts (?) and `title`. Removes 3-4 chips.
- **Hide behind one control:** Report and History leave the strip for the top More under a "This question" group
  (keys R and Y stay). Strip: Mark, Eliminate, Highlight, Note, Details.
- **Phone:** the strip's 5 labelled tools become Eliminate + Note icon-only (44px, `aria-label`); Highlight,
  Details, Report, History join More. Stem moves up ~50px. Footer: Back · Mark · 3 / 10 · Sure, with Not sure and
  Guessing as a quiet pair that slides up only after a pick (one row until the student has an answer).
- **Merge:** Summary phone buttons: pill full width, then one row of `Same settings` + `More` (Fix and SAT words
  into More, they are already listed there when the pill is the fix set; session.js:562-572).
- **Merge:** Summary meta line (`Set complete · 12:30 in all · 1:15 a question, pace 1:35 · ...`, session.js:401)
  into two rows of figure + label pairs inside the hero (time, pace), not one long sentence.
- **Space:** strip to stem 16 -> 24px; options gap 8 -> 10px; Summary lead groups 24 -> 32px; Details column
  rows 10 -> 14px between `dt` groups. Number tile ink 32px -> `--tile-2` with ink figure (the heaviest mark above
  the stem today, runner.css:561).

**Calm practice first screen, 1440, top to bottom:** 64px bar (Exit · title, counts | clock, Hide appearing on hover
or focus of the clock group, always on coarse pointers | Calculator, Reference, More), rail on its edge with one
sliding current marker; 24px air; strip (number · skill · type · difficulty left, stopwatch and 5 icons right);
the question sheet (section 3) with stem and 4 raised options; under it Skip / Hint as one quiet line. Right: Details
as a flat panel with two rows. Footer: Back | Question 3 of 10 | Sure (pill) + Not sure / Guessing (quiet pair).
**Phone:** bar, rail, one info line (title · counts merged with skill), stem at ~150px, options, one-row footer.

## 3. Depth and hero

- **Practice hero: the question sheet.** Page ground `--tile` (practice only); `.rn-col` becomes a paper sheet,
  14px radius, 1px `--line`, shadow `0 1px 2px rgba(60,45,20,.06), 0 12px 32px -18px rgba(60,45,20,.22)` (warm
  tinted, one light from above). R&W: passage pane and question share one sheet with the existing divider. Top bar
  and footer stay paper but flat at rest; each gains a 1px-to-soft shadow only while content scrolls under it
  (scroll-driven `animation-timeline: scroll()`, fallback: none). Details column: no box, sits on the ground
  (context recedes; drop `.rn-slot` box-shadow, runner.css:494). Phone: no sheet (full bleed), ground stays paper.
- **Options:** raised keys on the sheet: paper fill, `inset 0 0 0 1px var(--line)`, `0 1px 0 rgba(60,45,20,.06)`.
  Picked sinks in (shadow off, orange edge + 3px `--wash` halo). Right floods `--wash`. Nothing else elevated.
- **Summary hero: the score card.** One raised paper card at the lead (same shadow), figure 44 -> 64px, the set's
  own strip redrawn under it (10 status segments, the receipt), first-try line, then time and pace as two small
  figure/label pairs. What changed sits under the card flat; Review rows and folds stay flat hairline rows.
- **Between modules (test):** the countdown is the hero, as on Bluebook's break screen: clock 22 -> 44px figure
  (`.num`), bar under it; the tile box stays (runner.css:708-711). No shadow.
- **Test window question area: no depth.** Bluebook is flat white with hairlines; a sheet, raised options or
  halos would change the exam's look and its picked state (Bluebook: filled bubble only). Keep runner.css as is.
- **Challenge hero:** count or `#rank` 28 -> 44px with its meta, on a `--wash`-free paper panel; your board row
  keeps the wash + orange bar. **Diagnostic door:** a dimmed `UI.scale` sample band (200 wide) as the hero image.
- **No elevation:** strip, footer at rest, Review rows, folds, fact rows, navigator cells, Check your work tiles.

## 4. Buttons, controls, highlights

| Control | Now | Should feel |
|---|---|---|
| `.pill` Sure / Check / Next / Begin (shared) | flat amber, 8% darker hover, .97 press (ui.css:855-875) | inner top highlight `inset 0 1px 0 rgba(255,255,255,.28)`, 1px `--amber-deep` bottom edge, amber-tinted drop; hover lifts 1px; press .98 + shadow collapses; focus 2px ink ring, 2px gap; loading: label holds width, 16px arc spinner after 300ms; success: check swaps in 900ms (UI.saving) |
| `.btn` Not sure, Guessing, Same settings | `--well` fill, 7% hover | same edge recipe at half strength (1px `--line` bottom); pressed state stays wash-2 + amber inset |
| `.opt` (practice) | tile fill, tile-2 hover, .992 press (ui.css:2021-2044) | raised key (section 3); hover: line -> `--faint`, letter ring fills tile-2, 120ms; picked: sunk + halo; busy: letter ring turns into a spinner after 300ms; right: fill flood; wrong: ink edge + drawn cross |
| `.opt` (test) | same tokens | unchanged; only the press .992 (Bluebook has no hover lift) |
| `.strike` | 40px round, tile-2 hover | keep (Bluebook); line draws in 120ms when striking (practice only) |
| strip `.tool` icon | icon only; pressed: Mark wash + filled flag, others amber icon or 2px underline (runner.css:343-344, 440-441, 575-576) | one pressed look everywhere: `--wash-2` fill + amber icon; hover tile; tooltip 400ms |
| `.rn-seg` rail | rebuilt each paint, current taller + ink edge | answered segment fills from left 200ms; one persistent current marker slides |
| `.rn-navb` Question 3 of 10 | tile, chevron rotates | chevron rotate 160ms; badge dot when marked items exist |
| `.rn-exit` | text button, tile hover | keep; X rotates 90deg on hover (fine pointer only), practice only |
| `.t-hide` | always visible eye + Hide | practice: reveal on clock hover/focus; test: unchanged (Bluebook shows Hide) |
| Summary chips, `.sm-rl-row` | flat chips; row tile hover | rows: hover tile + chevron fades in at right; the clicked row's cell scales .97 on press |
| `.sm-fold` summary | CSS chevron, tile hover | chevron 180ms; body opens with `interpolate-size` height 200ms |
| `.choice-row` (test settings), `.rn-pcell` | shared pressed wash | unchanged (test) |

## 5. Motion moments

| Trigger | What moves | How |
|---|---|---|
| Check, right (practice) | picked option | wash flood from the letter outward (`clip-path: circle()` 240ms `--ease`), letter -> amber, check draws (`stroke-dashoffset` 200ms, +60ms) |
| Check, right | rail segment of this question | fills left to right 200ms, same frame as the verdict (cause -> effect) |
| Check, wrong | your pick, the key | cross draws 160ms on your pick; the key's wash pulses once (wash -> wash-2 -> wash, 420ms); no shake |
| Verdict | `.verdict` | keep `rise` 200ms (ui.css:2047); mastery bar 200 -> 600ms, 150ms delay, word rolls via UI.roll if it changes (question.js:1456-1464) |
| Fixed a mistake | `.v-fixed` line | keep pop; add a strike line drawn across the mistake label (clip-path, 360ms), once |
| Next / Back by pointer | stem + options | 140ms fade from .4 + 6px rise; Enter / arrows: instant (keyboard repeats, Emil); swipe slide exists (runner.js:2721) |
| Any move | rail current marker | one absolutely placed marker, transform 180ms; needs paintRail to stop `replaceChildren` (runner.js:1918) |
| Details / Reference open | side panel | 200ms fade + 12px from right; column does not reflow (panel already open) |
| Explanation fold | `details.x-fold` | height 200ms via `interpolate-size: allow-keywords`; content fades in 120ms |
| Mark toggle | flag icon | fill + scale .85 -> 1 160ms (not ui.css `pin`, it starts at scale 0) |
| Summary first view | score card | once per finished set (`satf.sumseen.{sid}`): figure counts up 600ms, strip segments fill with 30ms stagger; reload: static |
| Challenge day switch | board | crossfade 120ms, rows stagger 20ms (a change, not a load) |
| Test window | nothing new | Bluebook has no motion; answering is keyboard-repeated under time pressure. Keep only: option press, 60s clock pulse (runner.js:185), sheet entries. Fix: between bar animates `width` (runner.css:711) -> `transform: scaleX` |
| Reduced motion | all of the above | opacity only, no draw / slide / count (DIRECTION 7) |

## 6. Icons and imagery

- Unicode stand-ins: ✓ ✕ as option marks and verdict glyphs (question.js:1123, 1269, 1438, 1453; runner.js:3600,
  4309) -> the SVG `check` / `x` (all three sets have them), drawable. ▸ ▾ in `.ws-rule` (runner.css:52-53), "Tools
  ▾" (runner.js:3123), "▸ 3 tries" (runner.js:4364) -> `chev` rotating. ⌫ on the pad (question.js:1808) -> a delete
  glyph. "A− / A / A+" text-size radios (runner.js:2454) -> the shared `text` icon at three sizes.
- Three icon sets with drifting strokes: ui.js ICON 1.7-1.9 (ui.js:438), runner.js RI 1.6-2 (runner.js:82),
  question.js I 1.6-2 (question.js:104); `x`, `calc`, `ref`, `check`, `eye` are drawn twice. One set (ui.js),
  1.6 at 20px, 1.5 at 16px (shared).
- Verdict head glyph (runner.css:234): bare 18px character -> 24px disc: right = amber disc + dark check, wrong = ink
  ring + cross, blank = dashed ring. The Summary rows keep their status cells.
- Missing active states: top `.rn-tool` pressed is icon colour only (runner.css:440-441); `.t-hide` has none.
- Spot illustrations (line art in the icon stroke, `--soft` + one amber detail): Paused screen (pause glyph in a
  64px ring over "Paused", runner.js:2549); Notes tab empty (a note with an "Asked for" box, runner.js:1653);
  challenge "No one yet." (one dashed empty row with a rank slot, challenge/index.html:77); diagnostic door (the scale band).
- `fb.best` ("New best on this type") gets the shared `trophy` icon as a badge, not a ` · ` bit (question.js:1451).

## 7. Delight and feedback

- **Right answer stamp:** flood + drawn check + the rail segment filling, one 240ms beat. The point of the page.
- **Streak:** at 3, 5 and 10 in a row the count picks up the `flame` glyph (ui.js ICON, Today's streak language),
  amber, rolled with UI.roll; no confetti, no copy.
- **Crossed off:** a fixed mistake's label is struck through by a drawn line, then "Fixed" (once per mistake).
- **Level up in the verdict:** mastery word rolls (Developing -> Proficient) as the bar finishes.
- **Summary receipt:** the set's strip refills under a counting figure, once. A clean set says so in fact, not
  praise: "10 of 10, first try" as the figure's caption.
- **Wait states that talk:** Checking shows a spinner in the picked letter only past 300ms; the note editor uses
  UI.saving (Saving, Saved in place, runner.js:1687-1688) instead of a text swap.
- **Challenge:** your row sticks to the board's bottom edge while scrolled out of view (`position: sticky`), so
  "#4" is always on screen; rank rolls when the board refreshes after a name save.
- **Signup / Verified:** "Check your email" shows a quiet live dot beside "This page opens your results as soon as
  you confirm" (the poll is real, signup.html:115); Verified draws its check once.
- **Test window:** none on purpose. The only feedback is Bluebook's: the filled bubble, "Answer saved" to screen
  readers, the time toasts.

## 8. Ranked top 10

1. Right / wrong stamp on options + verdict disc (flood, drawn check / cross, key pulse) | the answer moment finally feels physical | M | low
2. Question sheet on a `--tile` ground, flat Details panel, scroll-only bar shadows (practice) | depth with one light, focus on the task | S | med (card-on-grey can look generic)
3. Raised option keys: hover lift, sunk pick with wash halo, press .99 (practice only) | tactile, the most touched object | S | low
4. Summary score card: 64px figure, the set's strip as receipt, first-view count-up + fill | the set ends on a reward, not a form | M | low
5. Details pre-answer cut to 2 rows, "Question info" fold, Everyone / Formula after the verdict | removes ~8 labels from the first screen | S | low
6. Strip down to 5 tools (Report, History into More); phone strip 2 icons + one-row footer until a pick | calm first screen, stem ~50px higher on phones | M | low
7. kbd hints on hover / focus and first 3 sets only; stopwatch bar past half budget | fewer equal-weight marks in the footer and strip | S | low
8. Tactile `.pill` / `.btn` recipe with loading spinner and in-place success (shared) | every primary feels pressed, not painted | S | med (keep the amber flat-ish, no glow)
9. Rail: answered segment fills, one sliding current marker (practice) | progress you can see happen | M | low
10. One icon set and SVG for every ✓ ✕ ▸ ▾ glyph; spot line art for Paused, empty Notes, empty board | consistency reads as finish | S | low

Test window (kept minimal on purpose): only the between-modules countdown at 44px (Bluebook's break screen has a
large timer), the bar on `scaleX`, and the shared pill. No sheet, halo, slide or stamp: Bluebook fidelity and
keyboard-repeated answering under a clock.
