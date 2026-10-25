# Words: premium audit (2026-10-19)

Scope: /words/ (web/words/index.html), /words/mine/, /words/study/ (Flashcards and Quiz), /words/run/, /words/print/,
web/assets/words-ui.js (tabs, Today's words, By exam day, the word sheet, Add and Bring sheets). web/vocabulary/index.html
is a redirect (:12-14); nothing to propose. Code reading only: heights are estimates from the CSS, not measurements. The
shell sidebar (about 18 controls at 1440) is not counted below.

## 1. First screen inventory

| Page, viewport | Buttons | Links | Chips | Inputs | Boxes | Bars | Labels | Help lines | Content starts |
|---|---|---|---|---|---|---|---|---|---|
| Library 1440x900 | 26 + ~30 tiles | 4 | 3 | 2 | 4 cards, 1 fixed bar, ~30 tiles | 1 tick meter, 3 known hairlines, ~30 pip rows (150 dots), ~30 dbars | ~14 + 30 tile metas | ~5 | grid ~170-200px |
| Library 390x844 | ~10 | 4 | 3 | 1 | 2 | 1 meter | ~8 | ~4 | grid ~1,080px (below the fold) |
| Flashcards 1440 | ~27 (12-16 deck radios, 12 seg options) | 4 | 0 | 0-1 | 1 (glance) | 0 | ~18 (12 are counts) | 1 | decks ~70px |
| Quiz 1440 | ~35 (+10 type chips, Print, Grade) | 4 | 10 | 0-1 | 1 | 0 | ~20 | 1 | decks ~70px |
| Study 390 | ~12 deck rows + fixed Start bar | 4 | 0 | 0 | 1 bar | 0 | ~14 | 1 | options below the fold |
| My words 1440 | ~16 + ~1,180 wall cells | 4 | 0 | 1 | 5 aside cards | 14 forecast bars (+ weeks chart) | ~22 | 2 | wall ~150px |
| My words 390 | ~10 | 4 | 0 | 0 | 6 | 0 | ~12 | 1 | list ~850px |
| Run, a card 1440 | 7 (4 top icons, ‹ Show ›) | 0 | 0 | 0 | 1 card | 1 progress strip | 6 (3 are kbd) | 0 | card ~80px |
| Run summary 1440 | 4-5 Up next + 1 per trap row | 1 | 10-40 word chips | 0 | 0 | 0 | 6-8 heads | 1-3 | score ~70px |
| Worksheet 1440 | 5 + 1 switch | 1 | 0 | 0 | 1-2 sheets | 0 | 2 | 0 | sheet ~60px |

Rows of controls before the content:
- Library 1440: (1) tabs + Add words; (2) search + four or five filter dropdowns; (3) the last dropdowns, the count, `?`, the
  gear (index.html:358-405; `sheet: false` at :386 keeps all seven facets as chips). In the aside, Today's words stacks four
  control rows (Start; Review cards / Learn 10 / Quiz; Time box 5 / 10 / 15 + preview; Make a set) plus the offline line
  (words-ui.js:403-441, :349-364).
- Library 390: tabs, Add words, Today's words' four rows, two daily-question rows, By exam day, Collections, search, the
  filter scroller, count + gear: about 11 rows before the first word. The round 1 estimate (560px) left out Make a set and
  the offline line; Today's words alone is ~370px here.
- My words 1440: the header wraps to two rows (title + meta ~390px, tabs ~370px, Add a word + Bring words + `⋯` ~310px,
  over 1,040px), then the view bar (search, 3 dropdowns, Table / Wall) wraps inside its 728px column.
- Flashcards / Quiz: tabs, then the content is itself controls (decks, 3 option rows; Quiz up to 6).
- Run: one top bar. Already calm.

The Practice complaint (empty placeholder bars) is here in miniature: every new word tile draws five ink-outlined empty pips
and a difficulty glyph (index.html:481, words-ui.js:248-251), ~150 empty circles at 1440 before any data; every collection
row draws its known hairline at 0 known (index.html:297, .kb at :59).

## 2. Clutter fixes

Hide behind one control:
- Library facets: Topic, Family, Difficulty, Status, Part of speech (and Collection when narrow) behind one Filters button
  with a count badge (drop `sheet: false`, index.html:386, or give the sheet a desktop popover). Sort becomes a quiet
  "A to Z" menu by the count. Facets that are set show as removable chips on a second row, only while set.
- The gear (index.html:396-400) toggles an inline span and shifts the row. Make it a menu: Meanings (check), Select
  (check), What the marks mean, and for an un-narrowed view Share / Print / Grade a worksheet (now only in the study bar).
- Today's words: Start stays. Review cards, Learn 10, Quiz, Time box, Preview, Make a set and Take offline go into one
  "Other ways" menu, a chevron `.btn.icon` joined to Start. Make a set opens its field inline when chosen.
- My words: Add a word + Bring words become the library's one Add words menu (same items, index.html:187-194): one
  header row instead of two, and the two pages match.
- Flashcards: Order and Show first go under More options, as Quiz already does (study:273-276).
- Run back face: Open word (run:438) moves to the top tools as an icon (the O key exists, :973).

Defer until relevant:
- Tile pips only from box 1; the difficulty glyph in `.reveal` (hover / focus, always on touch) like the part of speech,
  and always in the sheet. Collection known hairline only when known > 0.
- Study bar (index.html:146-151, shown as soon as the grid is in view, :586-592): only while narrowed or selecting. The
  whole-library actions live in Flashcards / Quiz tabs and the gear menu.
- Daily questions (index.html:240-263, two clamped serif lines each): one row in Today's words ("2 daily questions",
  opens a sheet with both and Answer); an answered one reads as a check line.
- Offline line: in Other ways; a visible line only while cards are kept on the device.
- When the sidebar's Up next is Today's words, the library shows two Starts for one thing; let the sidebar skip it on
  /words/ (the DIRECTION 4 rule already applied to the Now strip).

Merge: By exam day (index.html:219) becomes a one-line footer of the Today's words card ("SAT Mar 14 · 18 at risk", opens
as now). On a phone, Collections is a filter, so it becomes one horizontal chip row above the grid.

Restore space: 32px between the hero card and the next group (now 12, `--card-gap`); 20px between the filter row and the
grid (12); grid gap 10 (8); My words aside cards keep 12 but the three folded ones read as a list, not boxes.

Calm first screen, Library 1440, top to bottom:
1. Words, "212 known", tabs, Add words: one row.
2. Main: one row (search fills, Filters, A to Z, "1,180 words", menu); the grid from ~110px: 4 columns of quiet tiles
   (word 16/600, one soft meta line, marks top right, a 2px amber strength line at the foot only once studied).
3. Aside: Today's words hero (title, "12 due" at figure size, "about 9 min", 10 ticks, Start + Other ways, footer lines
   for daily questions and By exam day), 32px, then Collections as plain rows (no fill until hover, count right).
Library 390: header, tabs, Add words; the hero (~230px); search + Filters; the Collections chip row; grid from ~580px, two
rows of words above the tab bar. Flashcards: Deck leads with three 48px rows (Today's words, Due today, New) and a
"More decks · 13" fold (remembered), How many, More options; the glance with Start is the aside (the fixed bar on a
phone). My words: one header row, one view row, the wall; aside: status rows and the forecast open, the other three
closed to title + fact even at 1440 (mine:200 opens all of them from 1280).

## 3. Depth and hero

- Library hero: Today's words. `--paper` card, hairline, soft two-step shadow (0 1px 2px rgba(30,30,30,.05), 0 12px 32px
  -16px rgba(30,30,30,.22); dark: black at .5 plus `inset 0 1px 0 rgba(255,255,255,.04)`), a faint `--wash` radial in
  the top-right corner behind the ticks. The due figure at 28/600. Everything else in the aside loses its box: 4 cards
  become 1.
- Word tiles: content, so flat at rest (hairline). On a fine pointer, hover lifts 1px with `--shadow-float` and the
  hairline goes to `--faint`. Selected keeps wash-2 + amber inset.
- Flashcards / Quiz: the glance card is the hero (same recipe), `.stat-v` already at figure size; deck rows flat.
- Run: the flashcard is the page. Card on `--paper` with a contact and an ambient shadow (0 1px 2px, 0 18px 40px -20px),
  12px corners. Under it the deck: up to two edges (translateY 6 / 12px, scale .97 / .94, `--tile`) only while 2+ cards
  remain. These follow `left` (run:452), so they are a real count, not the fake `.fstack` edges round 1 removed. Mid-flip
  the card lifts (scale 1.03) and the shadow widens.
- Summary hero: the score at 64px on a `--wash` plate (12px corners, no border), with this run's strip under it: the top
  bar's segments re-laid 10px tall, full width, each one a button that opens its word. A receipt of the run.
- My words: the wall is the hero. Above it one figure ("212 known", 28/600) and one stacked status bar (new / learning /
  claimed / known, 8px) in place of the legend's swatch chips (mine:400-402). No card around the wall.
- Worksheet: a desk. Body `--tile`, the sheet #fff with a paper shadow; print already resets it (print:62-65).
- Elevation is only for: the hero card, the flashcard, the floating study island and phone grade bar, menus, sheets.

## 4. Buttons, controls, highlights

| Control | Now | Should feel |
|---|---|---|
| Start, every startWords caller | amber, 8% darker on hover, .97 press; no busy state: startWords (words-ui.js:275-286) awaits a POST then navigates, 200-600ms of nothing | shared: 1px top highlight and an amber-tinted drop at rest, hover lifts 1px, press .97 and the drop collapses; busy: "Starting" in place with aria-busy, set once in startWords on the trigger |
| Know / Don't know / Show (run:468-470) | pill + btn, flex 1, kbd inside | the chosen one stays pressed through the beat, the other dims to .45 |
| ‹ › (run:461-462, :525) | text glyphs | the `left` / `right` svgs (words-ui.js:160-161) |
| Word tile (index.html:66-83) | hover tile-2, no press, no motion | hover lift; press .98, 120ms; selecting: the box draws its check (stroke, 160ms) |
| Collections, decks, status rows | `.choice-row`: `--well` fill always, pressed wash-2 + amber, no press | `.choice-row.plain` (no fill until hover) on long lists, asked in round 2; :active .99 |
| Words tabs (words-ui.js:32-39) | links; current on paper with amber ring | the ring slides to the new tab across the page change: a view-transition name on the current thumb (main already fades 120ms) |
| wchip (words-ui.js:98-103) | `--well`, hover only | :active .97; on the summary, Moved to Known chips in wash-2 with a check |
| Save star (words-ui.js:632, run:265) | fills amber when pressed | a 240ms pop (1, 1.2, 1) on save only |
| Speak (words-ui.js:524-530) | no playing state | the arcs pulse while the voice plays (onstart / onend), aria-pressed |
| Order rows (run:735, :108-113) | wash-2 + amber when picked; dragging is opacity .6 | the dragged row lifts (shadow-float, 1.02), the others glide |
| Gear (index.html:396) | inline toggle, row shifts | a menu |
| Focus | global 2px ink ring (ui.css:308) | keep; on the flashcard the ring wraps the card, not a face |

## 5. Motion moments

| Trigger | What moves | How |
|---|---|---|
| Flip (Space, tap) | the card, rotateY 180 | now .45s `--ease` (run:50); 360ms ease-in-out (.77, 0, .175, 1) with the mid lift; reduced motion keeps the opacity swap (run:73-77) |
| Swipe (touch, after flip) | the card | bug: `.fcard` keeps its .45s transform transition while pointermove writes inline transforms (run:492), so the card trails the finger; release springs it back to centre (:494), then the old card sits 900ms (:509). Fix: no transition while dragging, follow 1:1, rotate dx/20 (cap 10deg), a "Know" (amber) or "Again" (ink) stamp fades in with abs(dx)/80; past 80px or a flick over 0.11 px/ms it flies out (translateX 120%, rotate 12deg, 220ms ease-out); under it springs back (240ms). Mouse drag too (now touch only, :487) |
| Grade by key or button | card out, next in | used 20-60 times a run, so short: 24px toward its side + fade (140ms), the next rises from the deck (160ms). The status line ("Know · back in 3 days") rides under the new card for 1.2s instead of the 900ms hold |
| Each grade | the progress segment | colours swap instantly (run:29-36): fill left to right (inner scaleX, 200ms); the current ring slides |
| After the flip | the word's mark in the sentence | the amber underline draws once (background-size 0 to 100%, 240ms): the eye lands on the word. No text stagger (seen too often) |
| Sheet paging (arrows, words-ui.js:589-601) | the sheet body | slide 12px in the direction of travel + fade, 160ms; Know / Don't know in self-test pages the same way |
| Uncover (Space, :602) | covered blocks | wipe open top to bottom (clip-path inset 100% to 0, 200ms) |
| Filter or collection change | grid | crossfade 120ms, the count rolls (UI.roll); search keystrokes: none |
| Show more (index.html:503) | new tiles | 4px fade up, 20ms apart, first 12 only |
| Narrowed / selecting | study island | rises 8px + fade, 200ms (`rise`, ui.css:1193) |
| Ticks grew since last seen | the new ticks | fill 40ms apart; never on a cold load (sessionStorage) |
| Summary opens after a run | Moved to Known chips, total | chips land 40ms apart (cap 12), then the total rolls (exists, run:903) |
| Order the ladder (run:733-750) | rows | `draw()` rebuilds every row per move, so they jump: FLIP 160ms |
| Sort / placement swipe (run:601-609) | the word | only pointerup is read, the word never moves: follow with damping and fade in the answer it will give (right the first, left the third, up the second) |

## 6. Icons and imagery

- `⋯` as text: index.html:149, mine:277. words-ui.js has `ic('more')` (:162), used in the sheet foot (:837).
- `‹` `›` as text: run:461-462, "‹ Previous" :525.
- `✓` proven and `⌇` stubborn as text on tiles and in the legend (index.html:473-474, :568, :572); "• due today" and
  "⌇ stubborn" in the wall legend (mine:401). Use ICON.check (ui.js) and draw a stubborn mark (a looped arrow) in the
  same 1.6 stroke.
- `★` in the My words table head and cells (mine:365): the svg star (words-ui.js:158).
- `⠿` drag handle (run:735): a six-dot grip svg. `●○◐` in Bring from a text (words-ui.js:1196): drawn pip-style circles.
- `=` / `≠` (words-ui.js:709-710) are fine as type; give them a fixed 16px column so the chip rows align.
- The three lead decks could carry a glyph (Today's words `today`, Due `review`, New `plus`); not the long tail.
- Missing states: Speak playing, press on tiles / rows / chips, busy on every start.
- Spot illustrations, empty states only, line art in the icon stroke with one amber fill: My words empty (mine:344-346, a
  3x4 mini wall with three cells lit) and a run with no id (run:258, a small card stack). "No words match" needs none.

## 7. Delight and feedback

1. Daily goal met: the tenth tick fills, then all ten sweep amber once (30ms apart) and the label reads "Goal met" with a
   check (`.meter.done` exists); once per day.
2. The deck under the flashcard thins as you go; on the last card it is gone and "Last one" (run:454) shows.
3. Swipe stamps: Know / Again appear as you drag, so the gesture explains itself.
4. Moved to Known: wash-2 chips with a check land one by one, then the total rolls. Nothing celebrates when none moved.
5. Sprint "New best" (run:858) as a `.badge` that pops in once, not a fragment of the meta line.
6. Find your level (run:907-918): the band bars grow once (200ms, 60ms apart): it is new information.
7. Covered word sheet: blocks look like face-down cards (`--well` plates, 8px corners, a Space kbd) instead of the faint
   "Covered" text (words-ui.js:131-135), and wipe open.
8. Save star pop; Speak arcs pulse; worksheet New version (print:155-163) fades the sentences over and rolls the code.

## 8. Ranked top 10

1. Library one-row filter bar (search, Filters popover, A to Z, count, menu): grid at ~110px, two rows of controls gone; M, slop low.
2. Today's words as the one elevated hero (due figure, ticks, Start + Other ways, daily and exam footer); 4 aside boxes to 1, ticks fill when earned; M, low.
3. Flashcard physics: 1:1 drag with stamps, flick to fly out, next card rises from a real deck; fixes the trailing-card bug; M-L, med.
4. Quiet tiles: no empty pips or zero known bars, difficulty on hover, a strength line once studied, hover lift, press .98; S-M, low.
5. Busy state on every start in startWords ("Starting", aria-busy): no dead 200-600ms, no double runs; S, low.
6. Flip and card depth: 360ms flip with a mid lift, paper card with layered shadow, back face without the "Meaning" label; S, low.
7. Summary as a receipt: score plate, this run's strip, Known chips cascade, Up next cut to Next + one button + More; M, med.
8. Study setup: three lead decks + More decks fold, Order and Show first under More options, the glance elevated; S-M, low.
9. Word sheet: covered blocks as face-down plates with a wipe reveal, paging slides with the arrow; S-M, low.
10. Shared asks for the lead: tactile `.pill` (top highlight, amber drop, lift), :active on `.choice-row` / `.wtile` / `.wchip`, `.choice-row.plain`, the tab ring as a view transition; S, low.
