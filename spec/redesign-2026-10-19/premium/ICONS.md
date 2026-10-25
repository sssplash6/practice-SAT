# Icons and illustration: audit and premium plan (2026-10-19)

Scope: every icon, glyph, mark and spot drawing in `web/`. Audit plus proposal; no app code changed. Shared files
(`ui.css`, `ui.js`, `kit.js`) are the lead's (DIRECTION 8), so the work lands as "Shared asks" at the end.

## The six decisions

1. **Weight:** one stroke, held in pixels, not scaled: 1.4px at 16 to 24px, 1.25px at 14px and below (1.3px dark).
2. **Grid:** Phosphor 256 grid, wrapped in the existing 24 viewBox, so `UI.svg(UI.ICON.x, 16)` keeps working.
3. **One map:** `UI.ICON` (ui.js:438) is the only icon map. Eight local maps and the inline drawings in 1d go.
4. **Active state:** outline to filled glyph, two layers in one svg, opacity swap on `aria-current` / `aria-pressed`.
5. **Topic glyphs:** keep 12 drawings, redraw 7, move them onto the icon weight rule. Custom, not Phosphor.
6. **Illustration:** only the mark's own geometry, at five moments. No art in list empties. Net icon count goes down.

## 1. What the code proves

**1a. Unicode stand-ins render in a fallback font.** fontTools on `web/assets/fonts/Geist.woff2` and
`GeistMono.woff2`: both lack `✓ ✕ ✗ ▾ ▴ ▸ ⓘ ★ ↻ ⋯ ✎ ⚑ ⊘ ⊖ ⌄ ■ □ ◐`. Each of those draws from the OS symbol font
(Apple Symbols, Segoe UI Symbol, Noto Symbols 2), so weight, width and baseline change per device. That is 128
uses in 37 files (comments excluded): ✓ 53, ✕ 21, ⋯ 15, ▾ 12, ✗ 4, ▴ 3, ▸ 3, ↻ 3, ⊘ 2, ★ 2, ⚑ 2, ✎ 2, ⌄ ◐ ⊖ ■ □ ⓘ 1
each. Hot spots: the cell corner glyph `--st-glyph` (ui.css:196-230, drawn at 700 9px by ui.css:1432), the verdict
head (question.js:1438, 1453), the switch knob (ui.css:1124), `.meter.done` (1276), `.counter.over` (994),
`[data-fact]::after` ⓘ (1368), and page overrides results/report/index.html:153-154, compete.css:128, 153,
results-ui.js:114. Geist does have `– » · ~ = ● ○ → ← ↗ ↑ ↓ ‹ › ▲ ▼ ↕ ×`, so those render on-brand.

**1b. Stroke overrides are dead.** Every map builds `${L} stroke-width="1.9"` with `L` already holding
`stroke-width="1.6"`. The HTML parser keeps the first duplicate attribute and drops the rest, so all of these render
at 1.6: ui.js results 443, x 445, clock 449, search 456, keyboard 469, plus 472, check 475; kit.js 181-189; runner.js
83-98 (pause "2", hl "3"); question.js 116, 121-123; words-ui.js 160-163. Topic glyphs too: SHAPES sets
`stroke-width` 3.2 / 1.8 / 2.4 (ui.js:671, 672, 681) and the `.stkl` class rule (ui.css:1987) beats a presentation
attribute, so the inequality ray's bold solution segment never shows.

**1c. Rendered stroke drifts with size.** 1.6 on a 24 box renders at 0.8px (12px: `.badge svg` ui.css:1284,
`.thumbs .x` 1342), 0.93 (14), 1.07 (16), 1.2 (18, sidebar 577), 1.33 (20, `.ibtn` 731), 1.47 (22, phone tabs 457,
menu rows 2132). Real widths that do apply: plan-ui.js:154 check 2.2, practice/index.html:100 search mask 2,
me.js:31 pencil 1.8, plan.js:547 and words/run:191 x 1.7, index.html:453 `svgI` 1.7, compete-ui.js:60 level ring 2.4.
Spread at screen: 0.8px to 2.4px. CSS icon sizes in use: 12 13 14 16 18 20 22 24 26 28.

**1d. Nine maps, one family drifting.** `const L =` appears in ui.js:428, kit.js:179, runner.js:81,
question.js:103, words-ui.js:155, compete-ui.js:161 (plus inline sets in contest.js:651, index.html:453, plan-ui.js:
154-156, plan.js:60/547, me.js:31, words/run:191, results-ui.js:178, practice/index.html:100). Same icon, many copies:

| Icon | Copies (file:line) | Drift |
|---|---|---|
| x | ui 445, kit 181, runner 83, question 123, plan.js 547, words/run 191, index 1121/2088 fallback | 1.6 / 1.7, joins differ |
| more (three dots) | runner 85, index 1245, words-ui 162, compete-ui 169, plan-ui 156, plan.js 60 + 9 text `⋯` | dot r 1.3 / 1.5 / 1.6 / 2 |
| chevron | ui 460 right, question 121 down, index 454 right, results-ui 178 down, words-ui 160-161 | same name, two directions |
| check | ui 475, kit 182, question 122, plan-ui 154 | 1.6 / 2.2 |
| search | ui 456, kit 187, runner 96 (longer handle), practice/index.html 100 (r7, stroke 2) | three shapes |
| play | ui 462 filled, runner 99 outline | fill vs stroke |
| book | ui `ref` 447 = question `book` 119 = kit `learn` 192 | one drawing, three meanings |
| undo arrow | ui `review` 453 = kit `again` 190 | nav item and verb share a glyph |
| pencil | me.js 31, index 1887 `PEN`, words-ui 164 `edit`, runner 87 `pen` | four drawings |
| flag / star / speak | question 114, compete-ui 163, words-ui 159; compete 167, words-ui 158; question 109, words-ui 157 | redrawn per file |
| calendar, clock | kit 183, index 1502, 1704; ui 449, index 1029 | redrawn inline |

`UI.ICON.more` does not exist (index.html:1246 falls back to a local copy). Four page helpers fall back to the
orange `dot` for any unknown name (test.js:31, me.js:25, builder.js:10, session.js:20), which hides typos.

**1e. Active states never change the glyph.** Sidebar: wash, 3px orange bar, 600, icon soft to ink
(ui.css:577-584). Phone tabs: orange 2px bar and 600 (457-462). `.sections` and chips: wash-2 ring (816, 1158).
The one outline-to-fill in the app is runner.css:576, 592, 1143 (CSS `fill` on the bookmark's closed path), which
cannot generalise: open paths (bars, path, arrows) cannot take a CSS fill.

**1f. Topic glyphs fail at their size.** viewBox `-13 -13 26 26` (ui.js:689), drawn at 18 (`.q-skill` 2008), 20
(chips 1996, `.skill-name` 2382), 22 (default 1984, toasts 2260). At 20px: `.stk` 1.3 and `.stkl` 1.4 render at
1.0-1.08px, `.stki` 0.9 at 55% opacity renders at 0.69px half-transparent, so axes, the slope riser, balance pans, cube
edges and the angle arc vanish. Content fills about 85% of the box against 75% for a UI icon, so a glyph beside an
icon at equal px reads larger. `.stk` paints `--gb` (default `--tile`, ui.css:1984); `.chip .glyph` (1996) never resets
it, so inside a selected chip (`--wash-2`, 1158) the die, cube, bars and percent rings show pale boxes (likely; verify).

**1g. Decoration and repeats.** Hold menus repeat one icon down a list: three `tests` (ui.js:2012-2013), two `plan`
(2014-2015), two `results` (2016-2017); feed rows repeat `bell` (2095, 2168); two different rows share `devices`
(2107-2108); "Save your progress" is `dot` (2100) in one menu and `save` (2181) in the other. `.side-quick svg` is amber
(ui.css:550), a second orange mark for a non-primary action. Test lobby fact icons are already gone (test.js:150).

## 2. Direction: Phosphor regular + fill, on our weight rule

**Pick:** Phosphor Icons, `raw/regular` and `raw/fill`, MIT, 1,512 icons, every one in both weights. Pin commit
`2b75f3ad12b4` of github.com/phosphor-icons/core (package 2.1.1). The last tag v2.0.8 has 1,248 icons and lacks
`calendar-dot`, `ranking`, `highlighter`, which this plan uses.

Why, against the field:

| Set | Licence | Stroke source | Filled pair | Verdict |
|---|---|---|---|---|
| Phosphor raw | MIT | yes: `stroke-width="16"` as an attribute, so we set our own width | all 1,512 | **take** |
| Phosphor Light (the high-end skill's pick) | MIT | 12/256 | yes | no: 0.84px at 18px, too thin beside Geist 14/500 |
| Lucide | ISC | yes, 2px default | none | no: no fills; the redesign skill names it the "AI default" |
| Heroicons | MIT | 1.5 | solid, plus 20 and 16px optical cuts | close second: about 300 icons, study tools (highlighter, eraser, formulas) would be custom |
| Tabler | MIT | 2px | about 1,000 of 5,000+ | no: fills missing exactly where needed |
| Iconoir | MIT | 1.5 | partial | no: fills partial |
| SF Symbols | Apple licence, Apple platforms only | | | not allowed on the web |
| Material Symbols | Apache 2.0, variable FILL axis | font | yes | no: Google look, banned by the high-end skill |
| Keep the custom set | ours | 1.6 | none drawn | no: 70 icons plus ~20 fills to hand-draw is where slop gets in |

Evidence (scratch render, regular non-scaling at 16/18/20/24, fill at 18/24): crisp at every size; container fills
(calendar, bookmark, flag, bell, fire, star, user) stay the same object, action fills (check, x, dots, caret) turn boxed.

**Licence:** copy the pinned commit's `LICENSE` verbatim to `web/assets/LICENSE-phosphor.txt`, and put a
one-line header above `ICON` naming the source, commit and that file.

## 3. Shipping in a no-build app

1. **Import once, by hand or a 30-line `tools/icons.py`** (not shipped, not run at build): read
   `raw/regular/<name>.svg` and `raw/fill/<name>-fill.svg`, drop the `<rect width="256" height="256" fill="none"/>`
   spacer and the `stroke-width="16"` attributes, keep `stroke="currentColor" stroke-linecap="round"
   stroke-linejoin="round"`, and write string entries into `ICON` (ui.js:438). Fills go into `ICON_FILL`.
2. **Wrap, do not rescale:** each entry is `<g transform="scale(.09375)">…</g>` (256 to 24). `svg()` (ui.js:426) and
   its viewBox `0 0 24 24` stay, so `UI.svg(UI.ICON.name, n)` and the 24-grid paths still passed to it keep working
   mid-move. Topic glyphs (`glyph()`) and badges (`badgeSvg`, me.js:1071) keep their own viewBox.
3. **One weight, in CSS** (ui.css, near `.ibtn` 725):
   `svg.i :is(path, line, polyline, polygon, rect, circle, ellipse)[stroke] { stroke-width: var(--i-sw, 1.4px);
   vector-effect: non-scaling-stroke; }`, `--i-sw: 1.25px` inside `.badge`, `.thumbs`, `.meter`, table heads, cells;
   `:root[data-theme="dark"] { --i-sw: 1.3px }` (light on dark reads heavier). `svg()` adds `class="i"`. Because the
   stroke is screen pixels, CSS size overrides (`.side-item svg { width: 18px }`) can no longer thin it out.
4. **Export a node helper:** `UI.icon(name, size)` (the private `icon`, ui.js:1437) joins the export list (2893). Then
   delete kit.js:179-196 (kit's `icon()` already falls back to `UI.ICON`, 201), runner.js:81-101, question.js:103-128
   (keep `UI.qicon` as an alias), words-ui.js:155-166, compete-ui.js:161-171, and the page constants in section 1d.
5. **Unknown name:** return nothing and `console.warn` on localhost; no orange dot fallback.
6. **Size steps:** 16 (beside 12.5-14px text, `.btn.sm`, `.quiet`), 18 (`.btn`, `.pill`, sidebar and menu rows,
   tools), 20 (`.ibtn`, rail), 24 (phone tabs, from 22); 12-14 only inside badges and cells. Inline icons
   `vertical-align: -.125em`; play nudged 1px right; busy glyphs (calculator, keyboard) at 18 and up only.

## 4. Replacement list (UI icons)

Nav (each gets a fill pair). Slop risk: low for all.

| Name | Old (ui.js line) | New (Phosphor) | Where |
|---|---|---|---|
| today | calendar with dot 439 | `calendar-dot` | nav, tabs, hold menu, palette |
| practice | four squares 440 | `squares-four` | nav, tabs, palette |
| review | undo arrow 453 (same as kit `again`) | `clock-counter-clockwise` | nav, hold menu; spaced review over time, not undo |
| words | "A=" 454 (reads as text style) | `cards` | nav, hold menu; flashcards; frees `text-aa` for Large text |
| tests | document 441 | `clipboard-text` | nav, tabs; not `exam` (its A+ smears at 18px, letter grades mean nothing on the SAT) |
| plan | S path 442 | `path` | nav, tabs (same idea, cleaner drawing) |
| results | three bare bars 443 | `chart-line-up` | nav, tabs; score over time |
| compete | `trophy` 451 | `ranking` (podium) | nav only; `trophy` stays for achievements and the daily challenge |
| profile | head and shoulders 455 | `user-circle` | nav, account menu |

Actions and tools (outline only unless marked F). Slop risk: low.

| Name | New | Where (file:line) |
|---|---|---|
| x, check, plus, arrow | `x`, `check`, `plus`, `arrow-right` | ui 445/475/472/450 and every copy in 1d |
| chev | `caret-right`; new `caret-down`, `caret-left`, `caret-up` | ui 460; question 121 becomes `caret-down`; index 454, 493, 1914, 2166; results-ui 178; words-ui 160-161 |
| more | `dots-three` (new key `more`) | index 1245, runner 85, words-ui 162, compete-ui 169, plan-ui 156, plan.js 60, 9 text buttons (section 6) |
| grip | `dots-six-vertical` | plan-ui 155, tabs grip |
| search | `magnifying-glass` | ui 456, kit 187, runner 96, practice/index.html:100 mask (same path as the mask) |
| bolt (Quick) | `lightning`, ink not amber | ui 457, 1743, 1927; ui.css:550 colour goes |
| help, chat | `question`, `chat-circle-text` | sidebar foot 1755-1756, menus |
| panel, dock, float | `sidebar-simple`, `sidebar-simple`, `picture-in-picture` | ui 461; question 125-126 |
| settings | `sliders-horizontal` | ui 463 (kept idea; gear would be the cliché) |
| signin, signout | `sign-in`, `sign-out` | ui 464-465, settings.js:648 |
| devices | `devices`; phone row `device-mobile` | ui 466, 2107-2108 |
| moon (F), text | `moon`, `text-aa` | ui 467-468, Display group |
| keyboard, save, users | `keyboard`, `cloud-arrow-up`, `users` | ui 469-471; "Save your progress" uses `save` in both menus (2100, 2181) |
| bell (F) | `bell-simple` | only on "See all" (2097, 2169); feed rows lose it (2095, 2168) |
| play, pause, stop | `play` (filled glyph by convention), `pause`, `stop` | ui 462, runner 84, 99, question 110 |
| clock, calendar | `timer`; `calendar-blank`, `calendar-check` for the done-day streak | ui 449, index 1029; kit 183, index 1704; index 1502 |
| calc, graph, ref | `calculator`, `function`, `math-operations` | question 111-113, ui 446-447 (ref sheet = formulas) |
| learn | `book-open-text` | kit 192, question `book` 119 |
| hint, speak | `lightbulb`, `speaker-high` | question 108-109, words-ui 157 |
| flag (F), bookmark (F), note (F), star (F) | `flag`, `bookmark-simple`, `note-pencil`, `star` | question 114, 115, 117; compete-ui 163, 167; words-ui 158-159 |
| report | `warning-circle` | question 116 (frees chat bubbles for feedback) |
| history | `clock-counter-clockwise` | question 118 (the runner has no nav, so no clash) |
| eye, cover | `eye`, `eye-slash` | question 106-107, runner 93-94 |
| skip, up, down, left, right | `caret-double-right`, `caret-up/down`, `arrow-left/right` | question 124, runner 89-92 |
| expand, shrink | `arrows-out-simple`, `arrows-in-simple` | question 127-128, index 1521 |
| marker, pen, erase, hl | `highlighter`, `pencil-simple`, `eraser`, `marker-circle` | runner 86-87, 97-98; me.js:31, index 1887, words-ui 164 use `pencil-simple` |
| list, grid, queue | `list-bullets`, `squares-four`, `queue` | runner 95, 100; contest.js:651-652 |
| filter, image, camera | `funnel-simple`, `image`, `camera` | kit 186, 184, 194 |
| twin, copy, again, fix | `copy`; `link-simple` for copy-link; `arrow-counter-clockwise`, `arrow-clockwise` | kit 188, 193, 190-191 |
| info | `info` | runner 88 |
| trap, clean, sheet | `crosshair-simple`, `check-circle`, `file-text` | compete-ui 165, 168, 164 |

Kept custom, redrawn on the 256 grid at the same weight: `eliminate` (question 105: Bluebook's struck "AB",
which `text-strikethrough` does not say), `twin_test` (copy plus a small timer, kit 189), `strikes` (compete-ui 166),
the streak flame becomes `fire` (F) with today's on/off logic (ui.css:412-413, index.html:422) moved to the fill layer.

## 5. Active-state treatment

- **Markup:** for names in `ICON_FILL`, `svg()` emits `<svg class="i"><g class="o">regular</g><g class="f">fill</g></svg>`.
  Others emit one layer. 15 pairs: nine nav, flag, bookmark, note, star, bell, moon, fire.
- **Rule** (ui.css): `svg.i .f { opacity: 0 }`; under `:is([aria-current="page"], [aria-current="true"],
  [aria-pressed="true"], [aria-selected="true"], [aria-checked="true"]) > svg.i` the `.o` goes to 0 and `.f` to 1.
  One element, no reflow, no class juggling in JS.
- **Timing:** DIRECTION 7, not a flat 150: fill in 160ms, outline out 160ms, reverse 120ms, `--ease`; reduced motion off.
  The mid-fade dip is invisible at 18-24px.
- **Colour:** nav fill in `--ink`, same as its label. The 3px sidebar bar and the 2px tab bar stay the one orange mark
  (DIRECTION 9). Rail (no label): the fill plus the wash is the whole signal, which is why it matters most there.
- **Status toggles** (Mark for review, Save, Star a word): fill in `--amber` with the outline kept in
  `--amber-deep` as its edge (orange on paper is 2.4:1; the deep edge is 3.2:1). Generalises runner.css:576, 592, 1143.
- **Hover:** soft to ink only; the fill means "you are here" or "on". Slop risk low; a bounce, glow or pop would not be.

## 6. Unicode stand-ins: replace by kind, not by file

| Kind | Glyphs | Fix | Sites |
|---|---|---|---|
| Inline marks inside text and CSS `content` | ✓ ✕ ✗ ↻ ⊘ ⊖ ⓘ ★ ⚑ ✎ ■ □ ◐ | **"Freshman Marks"**: a ~3KB woff2 holding only these codepoints, drawn from the same Phosphor outlines (`assets/` weight bold for 9px use), loaded with `unicode-range` and added after Geist in `--font`, `--mono` and `--serif`. Zero call-site changes. | 94 uses: kit.js:1874-1880, ui.css:196-230, 994, 1124, 1276, 1368, question.js:1123, 1269, 1438, 1453, 1610, review.js:330, 736, 1127, 1130, me.js:214, 389, 793, 1000, settings.js:429, plan.js:1336, 1421, 1567, wizard.js:149, tests.js:358, talk.js:156, compare.js:22, progress.js:211, s/index.html:245, index.html:225, 1457, charts.js:1634, runner.js:3600, 4309, results-ui.js:114, 235, 422, compete-ui.js:267, 441, 729, contest.js:23, words/index.html:473, 568, words-ui.js:1196, words/mine:365, report page.js:484, 903, 1231-1235, compete.css:128, 153, results/report/index.html:153-154 |
| More buttons | ⋯ | `UI.icon('more', 18)` in the same `.btn.icon` | words/index.html:149, words/mine:277, report page.js:387, 915, tests.js:421, 754, review/sheet/sheet.js:194, results/page.js:134, review.js:1064; tour.js:37, 47 and words/print:96 then say "the More button" |
| Disclosure | ▾ ▴ ▸ ⌄ | `caret-down` 16px; one rule rotates it 180deg on `[aria-expanded="true"]` (160ms) | runner.js:3123-3128, 4364-4365, review.js:184, 811, 1053, plan.js:824, wizard.js:670, plan/index.html:254-255, runner.css:52-53, report page.js:361 |
| Steppers | ‹ › as button text | `caret-left` / `caret-right` 18px in `.btn.sm.icon` | leaderboard.js:103-104, plan.js:1331-1332, charts.js:1225-1226, contest.js:121-124, words/run:461-462, 525 |
| Back links | "‹ Compete", "‹ Review", "‹ All students" | `caret-left` 16px + label in `.quiet` | contest.js:69, 70, 81, 117, 473; review/walk:43, review/sheet:81, review/print.html:78, admin/student:68 |
| Breadcrumb prose | "Settings › Your reports" | keep: `›` is in Geist and is typography here | settings, report, signin, pair copy |
| In-font arrows | ↗ → ▲ ▼ ↕ | keep (in Geist, on-weight) | ui.js:1608, 2530, plan.js:586, ui.css:1317-1319 |

Why a font for marks: SF Symbols and Material Symbols are fonts for the same reason; the ✓ inside "✓ Fixed" or a
9px cell corner must sit on the text baseline at the text's size, and `--st-glyph` stays a string, so the `--st-*`
contract (BRIEF) is untouched. Fallback if the lead rejects a font file: keep the token names, set `--st-glyph` values to
`url("data:image/svg+xml,…")` and draw `.cell::after` (ui.css:1432) and `.sw::after` (1475) as a mask in
`--st-mark`; the four override sites above must follow, and `kit.js:2347` stops stripping ⓘ by character.
Slop risk: low. Emoji: none left (practice trophy already replaced).

## 7. Topic glyphs: refine

Keep the idea: nineteen small math drawings no icon set has, apt and calm. Fix the drawing:

- Grid: viewBox `0 0 24 24`, live area 18 (match the icons), strokes via the same `svg.i` rule (1.4px).
- Two tiers only: primary strokes `currentColor`; secondary (axes, risers, pans) at full width in `--faint`, not
  0.9px at 55%. Dots stay ink: orange is primary and progress only (DIRECTION 0.6).
- No sticker fill: drop `--gb` (ui.css:1984, 2008, 2260, 2314); closed shapes `fill: none` (fixes 1f). Minimum 20px.

| Keep, re-weigh | Redraw | Why |
|---|---|---|
| percent, bars, die, right, cross, balance, cube, curveline, parabola, scatter, angle (arc at full width), dotcircle (+ radius) | | read at 20px once the hairlines are real |
| | numberline | taller ticks, the dot sits on a tick: it is a 6-unit sliver today |
| | ray | closed dot, bold solution segment, arrowhead (1b killed the bold part) |
| | errorbar | vertical interval over a short baseline, so it stops matching numberline and ray |
| | equiv | an equals sign whose lower bar is split in two (same value, other form); three bars read as a menu |
| | magnifier | a quote bubble holding two bars ("a claim about data"); today it is the search icon beside the search field |
| | graphline | line through two marked points on axes; today it is slope without the riser |
| | slope | rise and run at full weight |

Slop risk: medium (hand drawing). Draw at 48px, review at 20px on `--tile` and `--wash-2`, one reviewer for all 19.

**Achievement badges** (me.js:1031-1069, 40 drawings, own `badgeSvg` 1071): keep custom, move to `svg.i` weight.
Swap the two clichés: `clean_set` sparkles (the AI sparkle) to a closed ring with a tick; `perfect` gem to the full
mark. `sprinter` duplicates the Quick bolt; give it `timer`. The number literals ("3.500") are cosmetic.

## 8. The mark

In use: sidebar and phone bar 26 (ui.js:1727-1728, 1932), avatar fallback in `--soft` (1915), welcome and sign-in 32,
parent 28, share 26, favicon. The best things in this audit are already brand-derived: the living mark avatar (corners
fill by domain mastery, kit.js:2206-2218) and the compete level ring on the mark's squircle (compete-ui.js:343). Keep
both and build illustration from that geometry. No recolour, no dark variant: `#F18508` works on both papers. Open
question for the user, not a task: `.side-word` re-sets the wordmark in Geist 800 (ui.css:537); BRAND.md warns against
that, and `brand/SAT_LOGO.svg` holds the real paths.

## 9. Illustration: the mark's four corners, nothing else

One helper, `UI.spot(kind, size)`, built from `CORNER` (ui.js:432) like `livingMark`. Monochrome `--line` outline at
the icon weight, one piece in `--amber`, 56px phone / 72px desktop, left-aligned above the empty line
(`.empty` is a start-aligned grid, ui.css:1356). Never in sheets, popovers, filtered-empty states or print.

| Kind | Drawing | Where |
|---|---|---|
| start | four corners outlined, bottom-left filled amber | first-use empties: words/index.html:491, tests.js:661, me.js:1189, plan.js:1705, me.js:486, compete/overview.js:210 |
| clear | the whole mark in amber (it is the logo: "all done") | review.js:249, results/page.js:535, words-ui.js:461, Today's day-done state |
| lost | corners drifted 6 units apart, slightly turned | 404.html:27 |
| done | the living mark filling to the new mastery, corners staggered 40ms, 240ms each | set summary (runner) and test finished (test.js:732); only after the student's action, never on load |
| none | | every "No X match these filters" (tests.js:543, 674, review.js:640, results/page.js:474, words/index.html:493, talk.js:139): one line plus Clear filters |

Where a real sample exists, `UI.empty({sample})` (kit.js:2439, greyed example plus badge) beats any drawing; use it.
Slop risk: low for these (brand geometry, no new motif). High, so banned: characters, scenes, line-art people,
blobs, confetti, sparkles, rockets, trophies-with-stars, gradients, anything stock.

## 10. Favicon, app icon, social image

| Item | Now | Proposal | Slop risk |
|---|---|---|---|
| favicon | `/assets/mark.svg` linked on every page; no `/favicon.ico` | keep the SVG (wide gaps survive 16px); add `/favicon.ico` 16+32+48 at the web root for crawlers and old browsers | none |
| apple-touch-icon | 180 RGB, white tile, mark ~66% | keep | none |
| manifest icons | 192 and 512 RGB, `purpose` any only (manifest.webmanifest) | add `icon-maskable-512.png`, `"purpose": "maskable"`, mark at 56% of the canvas (inside the 80% safe circle); add `"id": "/"` and `"description"` | low |
| theme-color | white, switched by head.js:12 and ui.js:321 | fine | |
| social image | none: no `og:*` or `twitter:*` on any page or in server/ | static `/assets/og.png` 1200x630: paper ground, `brand/logo-stacked.png` lockup, one Geist 600 line from the meta description, orange only in the mark; `og:title`, `og:description`, `og:image`, `twitter:card` on index, welcome, s, share, compete/contest, parent, pair. Shared links land in Telegram and unfurl blank today. Per-share images need the server: later | low if plain; high with gradients or a phone mockup |

## 11. Order of work

1 one map, `UI.icon`, `svg.i` weight, dead overrides gone (no metaphor change yet); 2 Phosphor geometry and fill pairs;
3 Marks font, drawn ⋯ ‹ › ▾ controls; 4 topic glyphs; 5 `UI.spot`; 6 favicon.ico, maskable icon, og image.

## Shared asks (lead only)

- ui.js: replace `ICON` (438-476) with the Phosphor entries, add `ICON_FILL`, `svg()` adds `class="i"` and the two
  layers, export `icon`, drop the `dot` fallback, `UI.spot`, the redrawn `SHAPES` (666-686) on the 24 grid, menu fixes
  in 1g.
- ui.css: the `svg.i` weight and active rules, `--i-sw` tiers, `@font-face` Freshman Marks and the three font stacks,
  the caret rotation rule, `--gb` removal, `.side-quick svg` colour (550), tab icon 24 (457).
- kit.js: delete 179-196 local icons (keep `icon()` delegating), `STATES` glyphs stay as strings.
- New files: `web/assets/LICENSE-phosphor.txt`, `web/assets/fonts/FreshmanMarks.woff2`, `web/favicon.ico`,
  `web/assets/icon-maskable-512.png`, `web/assets/og.png`; optional `tools/icons.py` (import) and
  `tools/marks.py` (font build, fontTools + brotli).
- check-ui.py: fail on `const L =` outside ui.js, and on the Geist-missing characters outside the font file.

## Checks after each step

- `grep -rn "const L = " web --include=*.js` returns ui.js only; `grep -rnE "⋯|▾|▴|▸|⌄" web | grep -v dev/` returns
  nothing; `grep -rn 'stroke-width="[0-9.]*"[^>]*stroke-width' web` returns nothing (no duplicate attributes).
- `python3 tools/check-ui.py`, `node --check` on touched JS, no em dashes.
