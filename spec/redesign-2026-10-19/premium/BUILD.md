# Premium build: decisions and plan (2026-10-19)

The user: "do all and follow your instinct regarding relaxes". So: every item in SUGGESTIONS.md (Recommended, More,
Per page, the open bugs), the "Not doing" list stands, and the rules below.

## Rules (the lead's calls)

1. Cards carry `--shadow-1`; clickable cards step to `--shadow-2` on hover; the page's one hero sits at `--shadow-3`.
   Menus, popovers, tooltips, toasts `--shadow-3`/`4`; sheets and the palette `--shadow-5`.
2. The solid 1px card border becomes a soft see-through edge (`0 0 0 1px rgb(from var(--ink) r g b / .06)` style,
   inside the shadow stack), so it works on any surface and in dark mode.
3. Gradients: three only. The orange button's faint top sheen; the amber fade under trend lines; `--hero-wash`, a faint
   warm corner tint behind one hero per page.
4. The orange `.pill` gets a small warm contact shadow (blur under 4px). No halos, no glow.
5. Blur only behind a sheet's backdrop and under the phone tab bar.
6. One short page entry per visit (blocks rise 8px, at most 6, 30ms apart, never on back or refresh, the primary never
   delayed). Hero numbers count or roll on a new score; the gauge sweeps on a fresh test. Nothing else on load.
7. Three `linear()` spring settles (MOTION.md); one small bounce reserved for rewards. Exits about 75% of entries.
8. Spacing: page top 32, 32-40 between groups, card padding 20 (16 phone); rows stay 40; density only inside lists.
9. A hero step of 56-64px for the one number a page is about (`--fs-hero`), `--ink-strong` for it and headings.
10. `.btn` gets a white face, a light top edge and a contact shadow.
11. New tokens: `--shadow-1`..`--shadow-5` (aliases `--shadow-float` and `--shadow-pop` keep working), `--hero-wash`,
    `--ink-strong`, `--ink-2`, warm page `#F7F5F1` (cards white on it), an amber ramp, motion speeds and springs.
12. Both: drawn icons for the button marks (‹ › ⋯ ▾ ⓘ ×), and a small subset "Marks" font (OFL source) behind Geist in
    `--font` for ✓ ✕ and the other marks inside text and 9px cells, so they look the same on every device.
13. Practice's search edge sweeps once on load, then rests lit.
Fixed as always: logo, #F18508 (also the selection colour), `.pill` 42px with 10px corners, `.pill.sm`, `.btn`,
`.quiet`, no 24px+ radius, nothing taller than 48px, Source Serif 4 and Bluebook calm in the test window, no em
dashes, zero functionality loss.

## Plan

Phase A, shared (three builders in parallel, disjoint files):
- A1 surfaces and controls: owns web/assets/ui.css. Tokens, warm page, elevation, card edge, `.card.hero`, spacing,
  type (hero step, ink-strong), the orange pill recipe and every button state (hover, press, busy spinner after
  300ms at fixed width, done check), `.btn`, `.quiet`, icon buttons, split buttons, quiet menus, drawn checkbox,
  fields, switch, slider, seg and tabs (raised thumb), highlights (selection, mark, caret, row hover band, focus,
  one selected look, disabled), tooltips as dark chips, thin warm scrollbars, scroll shadows (`.scrolled`), dark mode
  depth, phone tap feel, the shell's look (sidebar Now card as one raised card with a goal ring).
- A2 motion: owns web/assets/kit.js and web/assets/ui.js (except the ICON map block), writes its CSS to
  premium/build/motion.css for the lead to merge. Exits for sheets, menus, popovers, toasts; toasts stack and fan;
  menus grow from their button; folds animate height; page entry; list glide (enter, exit, reorder); nav marker
  slides between pages (view transitions); sidebar collapse and Now fold glide; charts and meters sweep on change;
  feedback components (check draw, ring close, flame fill, pop) as kit helpers; keycap flash; phone sheet drag;
  `::view-transition` pointer-events fix; reduced motion everywhere.
- A3 icons: writes premium/build/icons.js (the new UI.ICON map in Phosphor regular, same names plus missing ones,
  and a FILLED map), premium/build/icons.css, and web/assets/fonts/Marks.woff2 (OFL subset), for the lead to merge.
- Lead: merges A2's CSS and A3's map and CSS, fixes the small shared bugs, runs the checks.

Phase B, pages (nine builders in parallel, as before, after phase A): each page's lines in SUGGESTIONS.md ("Per page",
its Recommended items) and its premium/pages/<name>.md top 10, the calm first screen first; adopts the shared pieces;
moves its local icon copies onto UI.ICON; fixes its open bugs. The sign-in "focus chrome" (a slim brand bar instead of
the sidebar on Sign in, Welcome, Pair) is a shell option the lead adds after A2.

Phase C: check-ui, node --check (files and inline scripts), em dash grep, smoke (Today 5 states, every page vs HEAD),
the functionality inventory diff, then the user reviews at http://127.0.0.1:8071.

## A3 icons

Files (all checked: `node --check` on both .js, the woff2 read back with fontTools, no em dashes, no duplicate
`stroke-width` attributes; rendered offline with resvg for a look, never in a browser).

| File | Holds |
|---|---|
| `premium/build/icons.js` | The new `ICON` map: 94 names in Phosphor regular (pinned commit 2b75f3ad12b4, MIT), every name drawn today in ui.js, kit.js, runner.js, question.js, words-ui.js, compete-ui.js and contest.js, plus `more`, `compete` (ranking), `grip`, `phone`, `link`, `calendar_check`, `caret_left/right/down/up`. `ICON_FILL`: the 16 fills alone. Helpers `PHF`, `PH`, `ph`, `phf`, `twin` (no clashes in ui.js). Header: source, licence, the names that do not exist today. |
| `premium/build/icons.css` | The Marks `@font-face` + unicode-range and the three font stacks; the icon weight (`--i-sw` 1.4px, 1.25px at 14px and below, 1.3px dark, non-scaling); the twin swap; the amber status toggles; the caret turn; the topic glyph classes; the spot styles. |
| `premium/build/glyphs.js` | `SHAPES` (19 topic glyphs: 12 kept and re-weighed, 7 redrawn) in today's `g => s(...)` shape on a 24 grid; `SPOT` (`start`, `clear`, `lost`, `done(ms)`) and `spot(kind, ms)`, each with its one-line "where". |
| `premium/build/LICENSE-phosphor.txt` | Phosphor's MIT licence at the pinned commit, verbatim. |
| `premium/build/marks.py` | How Marks.woff2 was built (rerun only to change the set). |
| `web/assets/fonts/Marks.woff2` | 2.2 KB, 30 code points: ✓ ✕ ✗ ⋯ ▾ ▴ ▸ ⌄ ⓘ ↻ ↺ ⊘ ⊖ ○ ● ◐ ★ ✎ ⚑ ■ □ ⌫ ⌇ ⠿ ⁻ and ‹ › « » · (the last five and ○ ● are in Geist, which wins while it is first). From DejaVu Sans 2.37, scaled to Geist's cap height, Geist's vertical metrics, so a mark never changes the line box. ⓘ is not in DejaVu: drawn from DejaVu's own ring (①) and "i". |
| `web/assets/fonts/MARKS-LICENSE.txt` | Source and DejaVu's LICENSE verbatim. Note: DejaVu is the Bitstream Vera licence (permissive: use, modify, embed; rename if modified, which "Marks" does), not the OFL. Picked over Noto because one family matched Geist's weight and size; Noto needed three fonts with mismatched marks. |
| `web/favicon.ico` | 16, 32, 48, each rendered from `assets/mark.svg` at its size. |
| `web/assets/icon-maskable-512.png` | White tile, mark at 56% (inside the 80% safe circle). A new file: `icon-512.png` stays as the `any` icon, a 56% mark there would look small where no mask applies. |
| `web/assets/og.png` | 1200x630, warm paper, the stacked lockup from `brand/logo-stacked.png`, "Free SAT practice for Math and Reading & Writing." in Geist 600 (two lines); orange only in the mark. |

### How the lead merges

1. ui.js: delete `const L = ...` and the `const ICON = {...}` block (`L` is used nowhere else), paste icons.js in
   their place (keep its header). Export `ICON_FILL` beside `ICON`, and export the private `icon` as `UI.icon`.
   Optional (ICONS.md 3.5): `icon()` returns nothing and warns on localhost for an unknown name.
   Callers need no change: entries are still inner strings for a 24 viewBox, and the twin layers live inside the
   string, so `svg()` needs no `class="i"` and no second argument.
2. ui.js NAV: `compete` row `icon: 'trophy'` -> `icon: 'compete'`. Account menu "Save your progress" `icon: 'dot'`
   -> `icon: 'save'`. (1g's repeated hold-menu icons are optional polish.)
3. ui.js: replace `const SHAPES = {...}` with glyphs.js's `SHAPES`; in `glyph()` set the viewBox to
   `'-12 -12 24 24'`. Paste `corner`, `spotSvg`, `SPOT`, `spotN`, `spot` after `CORNER`/`mark` and export
   `spot` as `UI.spot`.
4. ui.css: paste icons.css. Put the `@font-face` beside Geist's; replace the three `--font`/`--mono`/`--serif`
   lines in `:root` with icons.css's (do not add a second `:root` for them). Delete the old `.glyph`, `.stk`,
   `.stki`, `.stkl`, `.stkd` rules and the `--gb` settings in `.q-skill .glyph`, `.toast > .glyph`,
   `.palette [role="option"] > .glyph`; set `.q-skill .glyph` to 20px. Delete `.side-quick svg`'s amber colour.
   Optional: `<link rel="preload" href="/assets/fonts/Marks.woff2" as="font" type="font/woff2" crossorigin>`.
5. Copy `premium/build/LICENSE-phosphor.txt` to `web/assets/LICENSE-phosphor.txt`.
6. kit.js (with A2): delete its local `L`/`ICON` (`icon()` already falls back to `UI.ICON`); the `STATES` table's
   `svgHTML(ICON.twin)` and friends become `svgHTML(UI.ICON.twin)` (twin, twin_test, again, fix, learn exist).
   `xBtn` uses `UI.ICON.x`.
7. manifest.webmanifest: add `{"src": "/assets/icon-maskable-512.png", "sizes": "512x512", "type": "image/png",
   "purpose": "maskable"}`, `"id": "/"` and `"description"`.
8. Head tags (no HTML touched by A3). Every page: `<link rel="icon" href="/favicon.ico" sizes="32x32">` before
   the SVG icon link. Index, welcome, s, share, compete/contest, parent, pair:
   `<meta property="og:title" content="SAT Freshman">`,
   `<meta property="og:description" content="Free SAT practice for Math and Reading &amp; Writing.">`,
   `<meta property="og:image" content="https://prac.fsat.io/assets/og.png">`, `<meta property="og:image:width"
   content="1200">`, `<meta property="og:image:height" content="630">`, `<meta name="twitter:card"
   content="summary_large_image">`. Every page's `<meta name="description">` still says "Free SAT Math practice that
   never runs out and never repeats." (Math only): worth matching to the og line.

### Call sites page builders change

- Names whose meaning changes: question.js `chev` (a down chevron) -> `caret_down`; words-ui.js `left`/`right`
  (stepper chevrons) -> `caret_left`/`caret_right` (in the new map `left`/`right` are arrows, as runner.js uses them);
  results-ui.js:178 inline chevron down -> `caret_down`. `play` is now the filled triangle everywhere (runner's was an outline).
- Local maps to delete, calling `UI.icon(name, size)` / `UI.svg(UI.ICON[name], size)` instead: runner.js `RI`
  (81-101), question.js `I` (103-128, keep `UI.qicon` as an alias of `UI.icon`), words-ui.js `PATHS` (155-166),
  compete-ui.js `SVG` (161-171), contest.js `ICON` (list, grid), index.html `svgI` (453) and `MORE` (1245-1246,
  `UI.ICON.more` now exists), plan-ui.js 154-156 (check, grip, more), plan.js 60 and 547 (more, x), me.js:31 and
  index.html `PEN` (pen), words/run x (191), practice/index.html:100 search mask (magnifying-glass).
- Dot fallbacks hide typos (bug 3): test.js:31, me.js:25, practice/builder.js:10, practice/session/session.js:20
  `UI.ICON[name] || UI.ICON.dot` -> `UI.ICON[name] || ''`.
- Unicode stand-ins (ICONS.md 6, line numbers from its audit): `⋯` buttons -> `UI.icon('more', 18)` in the same
  `.btn.icon` (words/index.html:149, words/mine:277, results/report/page.js:387, 915, tests.js:421, 754,
  review/sheet/sheet.js:194, results/page.js:134, review.js:1064); disclosure `▾ ▴ ▸ ⌄` -> `UI.icon('caret_down', 16)`
  as the control's direct child, turned by icons.css on `[aria-expanded="true"]` (runner.js:3123-3128, 4364-4365,
  review.js:184, 811, 1053, plan.js:824, wizard.js:670, plan/index.html:254-255, runner.css:52-53,
  results/report/page.js:361); steppers `‹ ›` -> `caret_left`/`caret_right` 18 in `.btn.sm.icon`
  (leaderboard.js:103-104, plan.js:1331-1332, charts.js:1225-1226, contest.js:121-124, words/run:461-462, 525);
  back links "‹ Compete" -> `caret_left` 16 plus the label in `.quiet` (contest.js:69, 70, 81, 117, 473;
  review/walk:43, review/sheet:81, review/print.html:78, admin/student:68). `✓ ✕` and the other marks inside text
  and CSS `content` need no change: Marks draws them.
- Twins only work when the svg is the control's direct child (or in a page helper's `span.ic`) and the control
  carries `aria-current`, `aria-pressed="true"`, `aria-checked="true"` or is a selected `role="tab"`. The runner's
  Mark for review and words' Star should be `aria-pressed` buttons with the `flag`/`bookmark`/`star` icon; then
  runner.css's `.rn-mark[aria-pressed="true"] svg { fill }` rules (3 places) can go.
- Empty states: `UI.spotArt('start')` on first-use empties, `UI.spotArt('clear')` on all-clear, `UI.spotArt('lost')` on 404,
  `UI.spotArt('done', ms)` on the set summary and test finished (where each goes is in glyphs.js). Filtered empties
  get no drawing.

### Not done

- Achievement badges (me.js `BADGE_PATHS`, 40 drawings, ICONS.md 7) are not redrawn; they keep their own
  stroke widths. The sparkle and gem swaps are still open.
- `vertical-align: -.125em` for inline icons and the size steps (16/18/20/24) are left to A1 and the pages.
- `flame` keeps one layer (its `.flame` path is filled by `.streak.on`, ui.css:413); `ICON_FILL.flame` exists
  if the streak moves to the twin swap later.
- ⌘ and ⌥ stay with the OS font (Mac key caps); the qr.js block characters are not in Marks.

## Lead merge checklist

- [x] web/assets/LICENSE-phosphor.txt copied; manifest: maskable icon, id, description (Math and R&W).
- [x] After A2 (ui.js, kit.js free): A3 steps 1-3 (icon map, NAV icon names, glyphs + spot) and step 6 (kit.js icons).
- [x] After A1 (ui.css free): A3 step 4 (icons.css, font stacks, old glyph rules out), merge build/motion.css (A2).
- [x] After A1: manifest background_color / theme_color to the warm page colour (#F7F5F1).
- [x] After A2 (ui.js): drop `.ts-sub` from FOLD_SEL (Tests no longer uses it); the sidebar's Up next Start turns quiet
      (`.btn`) when the page's hero carries the same item (Tests, Today); check A2 shipped deferred section chips
      (then Tests' -44px shim and Results' rx.deferSections can go in part 2).
- [x] After A2 (ui.js): the Now strip's Start is a second orange button on phones where the page has its own primary
      (Practice's bottom bar, Today, Tests): make it `.btn` there (a shell option, e.g. `UI.shell({ ownPrimary: true })`).
- [x] After integration (kit.js): a shared dropdown chevron and `UI.meter({ tickStates })` (round 3, below).
- [ ] `UI.calendar` options in charts.js: `nav: false`, `legend: 'why'`, `tasks: false` (not `marks: false`: `marks`
      is the exam / plan-range option); given to the Results reviewer (owns charts.js), then Plan drops its hiding CSS.
- [ ] Artifact v3: blocked by the permission classifier ("PII data handling", the sample student names). Waiting on the
      user: approve the publish, or swap to obviously fake names. Then `rebuild.py --css` plus fresh kit.js / ui.js.
- [x] After phase B: head tags: favicon.ico link on 34 pages, og tags on index, welcome, contest, pair (s, share, parent had them), index description now "Free SAT practice for Math and Reading & Writing."
- [ ] The favicon.ico line on the six answering-screen pages (challenge, diagnostic x3, practice/session, test) once their reviewer finishes.
- [ ] After the demo critic: python3 <scratchpad>/demo-artifact/rebuild.py, then republish the artifact (same URL).
- [ ] Phase B part 2 messages to the nine page builders, with A1/A2/A3's APIs and the critic's do / don't list.
- [ ] Phase C: checks, smoke, inventory diff, then the visual critic over every real page (light, dark, 390).

## A2 motion

Files: web/assets/kit.js (a `motion` section after the helpers, plus the surfaces, toasts, roll, meter, table, seg
and tabs), web/assets/ui.js (keys, nav, sidebar, folds, the focus chrome), and premium/build/motion.css (new).
Checks: `node --check` on both; every smoke page and Today's 5 states at 1440 and 390 run A/B against the same tree
with the old kit.js/ui.js and print identical output (Today's diffs vs the morning baseline come from concurrent
index.html edits, not from these files); weekplanner passes; check-ui passes; no em dash. A jsdom probe (toast
stack, sheet, pop, menu, glide, meter ticks, roll, clip tabs, spring, fx, once, vt fallback, saving, keys, nav
mark, rail toggle, Now fold, the focus chrome, section chips waiting, the goal ring sweeping on fresh data) passes.

### Merge motion.css

Paste premium/build/motion.css into web/assets/ui.css after A1's sections and before "touch targets" and "print".
Each of its sections names the old ui.css rules it replaces (the keyframe entries on .menu, .popover, .tip and
.toast, the sheet and backdrop keyframes, `.toasts` flex and gap, the meter's width transition, main's 120ms page
fade, the current item's wash, the `.sections` transition); delete those, and only those: `@keyframes fade` and
`rise` stay (the scrim, `.banner`, `.selbar`, `.verdict`, the test window's popover rule in section 3). Where A1
gave the same element a `transition` shorthand (`.toast`, `.sections`, `dialog.sheet`), merge the property lists
instead of stacking the rules. A1's press literals map onto the tokens one for one: `.05s` -> `var(--m-press-in)`,
`.25s cubic-bezier(.3, .7, .4, 1)` -> `var(--m-release) var(--ease-release)`. Keep ui.css's reduced block
(`transition-duration: .01ms !important`) until its literal durations are tokens, then narrow it to animations as motion.css section 12 shows: until then CSS transitions
(sheets, folds, the stack, meters) are instant under reduced motion while kit.js still plays 120ms fades. If A1
also declared the motion tokens or springs, keep one copy (the values are MOTION.md's).

### The APIs (what page builders call)

- Page entry: put `data-m="stagger"` on the container of the page's top blocks and `data-m-now` on the block
  holding the primary. kit.js plays it by itself once per visit (not on reload, back, forward or bfcache; a
  prerender waits until shown), as soon as the children exist, within 3s. `UI.motion.stagger(host)` plays it by hand.
- `UI.glide(list, mutate, {key, enter})` -> Promise: run any change to a list inside it; rows that moved slide
  (FLIP, 200 ease-move, at most 40), new rows rise 4px, removed rows fade to .98 where they stood while the gap
  closes. Rows match by `data-key`, then `id`, then identity, so a rebuilt list still glides. A row leaving:
  `UI.glide(list, () => row.remove())`. UI.table's sort glides already.
- `UI.fx.check(el)` a drawn check (el is an svg, holds one, or gets kit's check); `UI.fx.ring(ringEl, p)` a
  `.ring` sweeps to p in 600 (one beat when it closes; `{beat: false}`); `UI.fx.flame(el)` the streak flame fills
  and settles; `UI.fx.pop(el)` one pop from .85 (rewards only); `UI.fx.glow(row, {remove})` -> Promise, an amber
  wash then the row leaves by glide. All are no-ops under reduced motion (a fade) and in the test window.
- `UI.roll(el, to, {format})` (same API): only changed digits move, up from below on a rise, `--m-roll` (600) on
  `--spring`. `UI.tile({countUp: true, countFrom: 400})` counts a score from its floor.
- `UI.meter(...).set()` changes animate by themselves (the fill slides by clip-path in 240; new ticks light 20ms
  apart); the first paint never moves.
- Folds: `details.fold` (and question.js's Explanation fold) open and close in height and fade by CSS where
  interpolate-size exists, by ui.js elsewhere; a `.card[data-collapsed]` that opens grows and its content rises
  4px. Nothing to call.
- `UI.motion.enter(el, 'rise' | 'nudge' | 'fade' | 'pop' | 'up', {delay, duration})`, `UI.motion.exit(el,
  'nudge' | 'pop' | 'down' | 'fade') -> Promise` (remove after), `UI.motion.grow(el, fromHeight)`,
  `UI.motion.vt(update, {cls, names})`, `UI.motion.once(key, 'local')`, `UI.motion.spring(d, bounce, v0)`,
  `UI.motion.ok(e)` / `off()` / `kb()` / `calm()`.
- `UI.motion.draw(svg)`: a chart's first draw (`[data-m="line"]` strokes draw, `[data-m="bar"]` rise from the
  baseline 16ms apart, `[data-m="wipe"]` reveals left to right). Call it on the first draw only.
- `UI.scrolled(bar, {edge: 'bottom', root})` -> {stop}: `.scrolled` while content slides under a sticky bar (A1's
  shadows). Declarative: `data-scrolled` (or `data-scrolled="bottom"` on a footer) is wired by itself. Already on:
  the section bar, UI.actionBar/selbar, UI.sheet's head and foot, the focus bar, the phone top bar (as before).
- `UI.seg(...)` / `UI.tabs(...)` `{mark: 'clip'}`: Paco's clipped orange copy as the indicator (opt-in).
- Section chips (`UI.sections`, `UI.shell({ sections })`) now wait until the page's header has scrolled away and
  fade in as the bar sticks, on every page; waiting, the bar takes no room and is clear but keeps its landmark and
  its chips stay in the Tab order (one that gets focus brings the bar out where it is). Opt out with
  `UI.shell({ sections, sectionsAlways: true })` (from the top, as before). Results can drop `rx.deferSections`.
- The sidebar's Today card (A1's hand-off) shows the goal as a small `.ring.side-goal` beside "Today" (minutes
  inside, `--p` minutes / goal, a tooltip and the minutes fact) instead of the Study time meter; the menu sheet and
  the Now strip keep the meter. `UI.saving()` puts A1's `.spin` before its "Saving" label.
- `UI.shell({ page, chrome: 'focus' })`: Sign in, Welcome, Pair. No sidebar, rail, tabs or Now strip; a slim
  sticky bar (mark and wordmark to /, Help, the account button and its menu); `body.has-focus` for centring the
  card; G H, Mod+K, ? and the G keys still work; banners other than the system's and event toasts are off there.

### What moves by itself now

Sheets leave (195 desktop; the phone sheet drops from where it is, 375, Vaul's curve) with their backdrop;
popovers and menus grow from their trigger (place() writes `transform-origin` and `data-side`) and shrink back in
120; a menu pick shows on its row while it fades; tooltips fade in 120 after 400ms, neighbours within 500ms open at
once, they fade out in 90; toasts stack (Sonner: 14px and 5% steps, back content hidden, fan on hover or focus with
every timer held, enter from below 400, the front leaves downward 300, an Undo toast carries a running-out line);
phone sheets follow the finger 1:1, damp upward, thin the backdrop, close past 90px or on a flick (.5px/ms), and
spring back with the finger's speed (`UI.motion.spring`); the current nav item's wash (now a `.nav-mark` span; no
stripe, per A1) and the phone tab's top bar (`.tab-mark`) slide and resize to the new item on a page change; the
rail collapse and the Now card fold glide (same-document view transitions); `::view-transition` lets clicks through; main fades out 100, in 200; keycaps on screen flash when their shortcut fires; Saved draws its
check; the sidebar's goal ring and study meter sweep, and a longer streak rolls and fills its flame, when fresh
data changes them. Keys are instant everywhere (`html[data-input]`); reduced motion keeps 120ms fades; the test
window (`body[data-page="test"]`) gets nothing new (its popover keeps a 120ms fade in).

### Not done, and why

- Unverified in a browser (the harness is jsdom; check these in Chromium first): the rail glide's
  `animation: revert` on `::view-transition-group(side)` (if it does not re-arm the UA's morph, the side snaps and
  only its labels crossfade: then keep the group at `animation: none`); the sizing of the view-transition images
  (`object-fit: none` on main's and m-nextup's new picture); the nav wash's `mix-blend-mode: multiply` in flight;
  sheet exits and the backdrop's `--m-bd` (`overlay` transitions, `::backdrop` inheriting from its dialog, Chrome
  122+). All of them degrade to today's behaviour.
- Charts (D5 to D8) and the gauge: charts.js is not A2's. `UI.motion.draw(svg)` is the hook; charts.js should
  call it from `sized()` on the first draw and mark its paths and bars `data-m`.
- Answer feedback F1 to F4, F10, F11 (question.js, runner.js) and the Summary/Report count-ups (session.js,
  report page): not A2's files; they can call `UI.fx.*`, `UI.roll` and `UI.tile({countUp, countFrom})`.
- N3 (card into detail), N4 (back fades only) and N5 (page title): head.js's `pagereveal` hooks, not A2's.
- C1 press: done by A1 in ui.css; motion.css's tokens carry A1's values (`--m-press-in` 50ms, `--m-release`
  250ms, `--ease-release`) so the literals can become tokens with no visible change.
- The card collapse closes instantly: pages flip `data-collapsed` themselves, so the observer sees a close only
  after the content is gone. Today's own `.collapsed` cards (index.html) are not covered.
- Page entry runs from kit.js at the end of `<body>`; if the browser paints before the scripts, the first-screen
  blocks can show for a frame before they rise (a pre-paint class in head.js would close it).
- The toast stack does not clamp older toasts to the front one's height (Sonner does); a taller older toast shows
  a taller strip behind.
- A toast raised by a key appears with its entry (`force`), unlike other key-driven motion: it is not what the key
  moved, so it enters and leaves like any toast.
- UI.roll runs 600ms, not NumberFlow's 900: DISCOVER-BROWSE's own advice for this app is about 600, and the demo
  plays 370; one token (`--m-roll`) changes it.
- Sheet exits need `overlay` support (Chromium, Safari 26); elsewhere they close at once as before. The rail and
  fold glides need same-document view transitions; elsewhere they snap as before.
- Not touched: the palette (palette.js), the tour ring (tour.js), banner dismiss (S7), the theme crossfade (N6).

## A1 surfaces and controls

All in `web/assets/ui.css` (no other file touched). Checks: `tools/check-ui.py` ok, braces 1507/1507, no em dash,
lightningcss parses it with 0 warnings, css-tree finds no invalid value that was not there before (only its
known false positives on `env()` and `@font-face` weight ranges). Smoke: Today fresh/plan/review/stretch/test at
1440 and 390 "NO ERRORS"; page.js: review, results, tests, plan, words clean; practice 1, me 7, compete 1 error
lines, the same counts as before the edits (fixture gaps; the smoke strips `<link>`, so CSS cannot move them).
One Today run differed in its `pills:`/`drows:` lines while index.html was being edited by someone else at the
same minute; a rerun matched.

### What changed, by area

- **Tokens.** Warm page `--page` #F7F5F1 under white `--raised` cards and white `--float` floats; `--paper` stays
  white (the test window, fields, keycaps and the five pages that set `body { background: var(--paper) }` keep
  it). Dark: page #1A1917, raised #242220, float #2C2926, button face #312E2A: higher is lighter, every shadow
  level carries a 1px top highlight and a soft white edge. Warm shadows (`--sh: 60 52 44`, amber `140 70 0`
  under the pill), never grey. `--shadow-float` and `--shadow-pop` are aliases of `--shadow-3` and `--shadow-5`.
- **Surfaces.** body, `.bar`, `.pbar`, `.sections`, the phone tabs and grip, and the sidebar sit on `--page`;
  `.card`, `.stat`, `.panel`, `.nextup`, `.side-day`, `.now-strip > .nextup` are white at `--shadow-1`; floats
  (`dialog`, sheet, more, menu, popover, toast, selbar, palette, calc) on `--float`. The surfaces block now drives
  wells: page `--mat`, card and float `--tile-2` (dark: page `--tile-2`, card and float `--mat`). Overrides that
  painted paper inside a tile card are gone (`.field`/`.otp` in cards, `.cal-d`, `.cal.plan .cal-d`, `.cal-sw`,
  `.heat`, `.card-err`, chart `--surface`): they read `--surface`/`--well` now.
- **Spacing (rule 8).** `--card-pad` 20 (16 phone), `--card-gap` 32 (20 phone), `.page` top 32 (20 phone), bottom
  64, `.stats` gap 16. Rows stay 40. The 1280+ aside gets 8px of room so card shadows are not clipped.
- **Type.** `.h1 .h2 .h3`, card-head and sheet titles and `.stat-v` in `--ink-strong`; `.hero-num` at `--fs-hero`.
- **Pill.** Brand fill under a faint top sheen (gradient 1 of 3), 1px darker edge lit at the top, inner foot
  shade, warm contact shadow under 4px blur; hover brightens 9% (no lift, no shadow growth); press sinks 1px with
  an inner shadow, down in 50ms and back over 250ms `cubic-bezier(.3,.7,.4,1)` (Comeau); disabled solid grey;
  `[aria-busy]` hides the label after 300ms and turns a 16px spinner in its place (width held, CSS only);
  `.pill.done` draws a check in before the label. Demo A1-A3 construction, except hover is a fill step on
  `background-color` instead of the demo's `::after` layer (that pseudo is needed for busy and done).
- **Other controls.** `.btn` white face + fine edge + foot lip (light) or top highlight (dark) + contact shadow,
  hover face step, press sinks, open/pressed stays the orange selected look, `.btn.ink` Kitchen stack, disabled
  solid. `.quiet` amber underline on hover, no fill ever. `.ibtn` ghost until hover, `--well` when open, press .94.
  Chips are small white keys. Fields white with a fine edge and faint inner shadow; focus ink edge + soft orange
  halo (`--halo`); OTP the same. Switch: inset track, knob with a drawn check, stretches to 24px while pressed.
  Range: inset track, warm thumb that grows 12% while dragged. `.seg`: recessed track, raised white thumb
  (static and the sliding `.seg-ind`). Tab underline gets a hair of warm shadow.
- **Checkbox.** Every native checkbox (`:where(input[type=checkbox])`, zero specificity so a page rule still wins):
  18px, 5px corners, white with a 3.6:1 edge, amber when checked with a check grown in (an SVG background, so no
  pseudo-elements on inputs), a bar when indeterminate, solid when disabled. Menu checkbox and radio items use
  the same look. Radios stay native (accent-color).
- **Highlights and states.** Focus per the user's feedback: a 2px `--amber-deep` outline 2px out that follows the
  corners and leaves the shadows under it; links, `.link`, `.quiet`, `.fold-s` and word-`?` get no box, an
  amber-deep 2px underline on a `--wash`. Fields keep ink edge + halo. One selected look (`--sel-bg` +
  `--sel-edge`) on choice rows, chips, `.btn` pressed, sections, phone chip, `.dd.on`, link stats, legend and
  chart toggles, the picked plan day. Disabled solid (`--off-bg`/`--off-fg`, 3.1:1). Hover band `--hover` on
  tables (opaque, so pinned cells stay solid), menus, options, legends, stats in cards. Your table row: wash
  and 600, same height, no stripe (`.rank` in it turns amber-deep). The sidebar's current item lost its 3px
  stripe (the user's "no side stripes"): wash and 600 remain. The listbox check is a drawn mask at the row's end
  that cannot wrap, scoped to `[role=listbox]`. `::selection` amber 32%, `mark` a highlighter band on the lower
  half (runner's `mark.hl` resets it), amber caret on every input, palette matches underlined amber. Tooltips are
  dark chips (`--tip-*`, 6px corners, `--ink`/`--soft` redefined inside). Thin warm scrollbars. Scroll shadows
  (`--shadow-scroll`) on `.bar.scrolled`, `.pbar.scrolled`, `.sections.stuck` and any `.scrolled`. Backdrop blur
  only under sheets (4px) and the phone tab bar (16px, 86% page). No tap flash; no text selection or callout on
  controls. Print drops card shadows and the hero wash.
- **Data with weight (Recommended 15, the lead's ask).** Gauge: `.g-track` is a groove as wide as the band (16,
  round caps, `--tile-2`, a 1px light lip; `--mat` in dark and in floats), `.g-band` amber with a small warm
  contact shadow, `.g-mid` a 5px ink-strong knob needle with a small shadow, `.g-prev` an ink 18% ghost (it would
  vanish on the new track), `.gauge-v` in `--ink-strong`. `.ch-zone` gets a hairline edge. `.meter-bar` 6px (from
  4), `.ring` track 6px (`--ring-w`), inner shadows on meter and scale tracks. Chart text sizes untouched.
- **Test window.** `.rn-exam .pill` loses its sheen, edge and shadows; `.rn-exam .btn` keeps only its edge.
- **Header.** Rules 2, 3, 4, 6 and 10 rewritten to BUILD (depth not lines, three gradients, warm contact shadow,
  test window flat, the motion rule); the ui.css components list names the new classes. The summary block
  "premium A1 (2026-10-19)" closes the file.

### The API (tokens and classes page builders use)

| Name | What it is |
|---|---|
| `--page` | The warm canvas. Paint a sticky bar or a page-level strip with it, never with `--paper`. |
| `--raised` | A card's white (dark: a step up). |
| `--float` | A menu, popover, sheet or toast's surface. |
| `--face`, `--face-hover` | The white face of `.btn` and chips; use for any custom key. |
| `--ink-strong` | Headings and the one hero number. |
| `--ink-2` | A secondary value, between `--ink` and `--soft`. |
| `--fs-hero` | 56-64px clamp for the number a page is about. |
| `--amber-100` .. `--amber-700` | The amber ramp (100 = wash, 200 = wash-2, 500 = brand, 600 = deep). |
| `--shadow-1` .. `--shadow-5` | Elevation: card, clickable card hover, hero/menu/popover, toast/docked bar, sheet/palette. Each includes the edge; use one per element. |
| `--edge` | The soft see-through edge alone (a flat card, a divider ring). |
| `--shadow-scroll` | A sticky bar while content slides under it. |
| `--hero-wash` | The warm corner tint (gradient 3 of 3); `.card.hero` uses it. |
| `--edge-ctl`, `--shadow-btn`, `--shadow-btn-down` | A control's fine edge, its resting and pressed shadows. |
| `--shadow-field`, `--halo` | A field's recessed edge; the focused field's orange halo. |
| `--hover` | The warm hover band (translucent; layer it over `--surface` where the cell must stay opaque). |
| `--sel-bg`, `--sel-edge` | The one selected look (wash-2 + 1.5px amber inset). |
| `--off-bg`, `--off-fg` | Disabled: solid grey fill and text. |
| `--seg-thumb` | The raised thumb's shadow (amber ring included). |
| `--check-mask`, `--check-ink` | A drawn check: a mask for `background: currentColor`, or an ink-deep SVG for a background. |
| `--tip-bg`, `--tip-fg`, `--tip-soft` | The dark tooltip chip. |
| `.card.hero` | The page's one hero: `--shadow-3` on `--hero-wash`. One per page. |
| `.card.go`, `a.card`, `button.card` | A card that is one link or button: `--shadow-2` on hover, a hair of press. |
| `.card.line` | A flat card (edge only), for a card inside a surface. |
| `.ledge` | Opt-in for selectable tiles (Tests papers, Plan days): a 3px ledge that presses to 0; never on `.pill`. |
| `.hero-num` (+ `small`) | The hero number at `--fs-hero`, `--ink-strong`, the unit small on the baseline. |
| `.split-btn` | A wrapper for a main action plus its menu (`.pill`, `.pill.sm`, `.btn` or `.btn.sm` parts; the menu part carries `aria-haspopup`/`aria-expanded` and a chevron svg, which turns while open). |
| `.go` on `.pill`/`.btn`/`.quiet` | A way forward: its trailing svg arrow nudges 3px on hover. |
| `.pill.done` | The drawn-check success state (add for the moment, then remove). |
| `[aria-busy="true"]` on `.pill`/`.btn` | Spinner after 300ms at the same width; a `.spin` child is used instead if present. |
| `.spin` | A 14px ring spinner for anywhere (static under reduced motion). |
| `.scrolled` | Any sticky bar: the scroll shadow while set (a page's own `box-shadow` rule needs `.x.scrolled`). |
| `.rank` | In a `.table tr.you`, the rank cell turns amber-deep. |
| `.ch-area`, `.ch-fade` | The amber fade under a trend line (see Not done for the markup). |
| `--ring-w` | A `.ring`'s track width (6px). |

### Not done, and why

- **The Now card's goal ring.** The sidebar's Up next and Today card read as one white raised card (two grid
  items joined: shared corners, Up next's edge as the hairline, the shadow on the Today part), but the goal ring
  needs ui.js markup (the ring exists only in the rail form, beside a meter that says the same thing). For A2 or
  the lead: render `.ring` in the full card's head instead of the Study time meter, and I will style it.
- **Rule 13** (Practice's search edge): page builder, as instructed.
- **The amber fade under trend lines needs charts.js** (not mine; no area path exists today). CSS is ready:
  draw `<path class="ch-area" d="(the line, then down to the baseline and back)" fill="url(#fadeN)">` under
  the `.ch-line.you` / `.ch-trend` path, with `<defs><linearGradient class="ch-fade" id="fadeN" x1="0" y1="0" x2="0"
  y2="1"><stop offset="0"/><stop offset="1"/></linearGradient></defs>` (the stops' colour and opacity come from
  ui.css: amber .14 to 0). A `.ch-area` with no `fill` attribute shows a flat 10% tint. A knob dot at the needle's
  outer end would also need charts.js (a circle); the CSS needle is a thick round-capped bar.
- **Motion tokens and springs** (`--m-*`, `linear()`): A2's motion.css. A1 used literals: hover and colour
  140ms, press down 50ms, release 250ms `cubic-bezier(.3,.7,.4,1)` on `.pill .btn .ibtn .x .chips>* .seg>button`
  (MOTION C1 is done here; A2 need not duplicate it, only retime to tokens). The switch knob's stretch
  transitions `width` (one 20px pseudo-element; name it with E1-E3 if check-ui learns that rule).
- **Not mine, found while working.** Page files still paint page-level boxes `var(--tile)` (now the page tone:
  runner.css 29 (on its white paper, fine), plan 7, index 5, tests/review/session/words-run 3, results/admin 2,
  words, test, review/sheet, review/print, report, me.css 1); side stripes `inset 2-3px 0 0 var(--amber)` at
  index.html:338, plan/index.html:463, tests/index.html:162, review/sheet/index.html:30, review/index.html:139;
  ink focus outlines (`outline: 2px solid var(--ink)`) in runner.css, index.html, me.css, plan/index.html (2),
  results/report/index.html, review/index.html, words/mine. The calendar's picked day keeps its 2px ink outline
  (`.cal-d[aria-selected]`, "orange is the SAT's"), and `--ring` (current cell) stays ink: both are marks, not
  focus; say if they should go thinner.
- **kit.js `saving()`** sets `aria-busy` on its button, so a Save `.btn` now shows the spinner after 300ms in place
  of "Saving". To keep the label beside a spinner (demo A1), kit prepends `<span class="spin">` and the overlay
  steps aside.
- `--amber-deep` focus ring is 2.9:1 on the warm page (3.2:1 on white), as the lead decided.
- **On merging A2's motion.css:** A1's press rules use literals that match A2's tokens: `.05s` press-in ->
  `var(--m-press-in)`, `.25s cubic-bezier(.3, .7, .4, 1)` release -> `var(--m-release) var(--ease-release)`
  (grep `cubic-bezier(.3, .7, .4, 1)` in ui.css: pill, btn, ibtn, x, chips, seg, switch knob, cards). `.scrolled`
  is the class A2's `UI.scrolled` toggles.
- **For the Report builder:** `results/report/index.html:78-79` joins two pills by hand (`.rp-split`, `margin-left:
  1px`); with the pill's 1px borders that is now a 3px seam. Swap it for `.split-btn`. (runner.css's `.split`
  for the Twin verb is patched in ui.css: the caret pill keeps its depth and the borders merge.)
- **`--card-gap` is 32 now**, and some tile grids borrow it (practice `.dgrid`, `.tiles`; admin `.adm-tiles`): their
  tiles sit 32 apart until their builders give them their own gap (16 inside a group).

## Part 2 notes per page (for the lead's part 2 messages)

- runner: Review now frames the question pane itself (`.rh-pane`); do not raise or frame `.rv-pane` inside `.rh-pane`
  (two frames otherwise). Replace the pane's "Tools ▾" band with a head icon; Twin and `rv-next` are `.btn` while
  Review's bar shows. Answer feedback via UI.fx (right: fill, check draw, segment fill; wrong: dim and strike, the
  right one fills). The test window stays calm.
- results: chart draw-ins in charts.js (A2 left them), the `.ch-area` path for the amber fade (A1's CSS is ready),
  the gauge rules, drop `rx.deferSections` (the shell defers section chips now), `.rp-split` -> `.split-btn`.
- tests: drop the -44px section shim (deferred chips are shared now); `UI.shell({ ..., ownPrimary: true })`.
- practice, today: `ownPrimary: true`.
- plan: per-tick meter states and calendar options only if the lead has added them to kit (check BUILD.md).
- words: icons `left`/`right` -> `caret_left`/`caret_right`; flashcards follow the finger (A2's spring helper).
- me-compete-misc: switch Sign in, Welcome, Pair to `UI.shell({ chrome: 'focus' })`; user-level calls made by the
  lead: Sign in shows one way plus "Other ways" (yes), the Profile plate above This week (yes), the contest rank stays
  44px (the user already said 44 is ok).
- review: icons (`UI.icon`, more, caret_down, x), the phone row more-menu, motion; replace the temporary " ×" text marks.
- every page: read BUILD.md "## Integration" (UI.icon, UI.spotArt, ICON_FILL, ownPrimary, A2's UI.motion / glide / fx /
  scrolled, the `data-m="stagger"` page entry hook) and DEMO.md "## Visual review" (the critic's do / don't list).

## Integration

Phase A merged into web/assets/ui.css, ui.js and kit.js (no page file touched, nothing committed). **One rename: the
empty-state drawing is `UI.spotArt`, not `UI.spot`** (reason below); everything that says `UI.spot` above (A3 steps 3
and "Empty states", the part 2 note just above) means `UI.spotArt`.

### Steps

1. **ui.js icons (A3 1-3).** `L` and the old `ICON` block gave way to build/icons.js (header kept): 94 names, `ICON_FILL`
   exported beside `ICON`, the private `icon` exported as `UI.icon` (an unknown name returns '' and warns on
   localhost). NAV `compete` row `trophy` -> `compete`; the account menu's "Save your progress" `dot` -> `save`; also
   the phone menu sheet's Compete cell `trophy` -> `compete` (same destination, and it carries `aria-current`, so it
   needs the twin; Daily challenge keeps `trophy`). `SHAPES` is glyphs.js's (with its header), `glyph()` viewBox
   `-12 -12 24 24`; `corner`, `spotSvg`, `SPOT`, `spotN`, `spot` sit after `CORNER`/`mark`. Header docs list the new
   exports. Every icon name ui.js and kit.js use exists in the new map (checked by script).
2. **kit.js (A3 6).** Its local `L`/`ICON` are gone: `const ICON = UI.ICON || { x }`, so `xBtn`, the VERBS table
   (twin, twin_test, again, fix, learn) and `icon()` all draw from UI.ICON. The `{ x }` fallback is for the admin
   pages (admin/student, students, reports), which load kit.js **without ui.js**: there only the close mark draws and
   every other kit icon is empty (before, kit's own 14 drew). Lead: add ui.js to the admin pages, or accept it.
   `svgHTML` prints '' for a missing icon instead of "undefined".
3. **ui.css icons (A3 4).** Marks `@font-face` beside Geist's; the three stacks in `:root` now carry "Marks"; icons.css
   sections 2-6 (stroke weight, twins, amber toggles, caret turn, topic glyph classes, spots) replace the old
   `.glyph/.stk/.stki/.stkl/.stkd` rules; `--gb` gone from `.q-skill .glyph` (now 20px), `.toast > .glyph` and the
   palette's; `.side-quick svg`'s amber is gone. Marks preload skipped (no shared head place; the lead's head pass).
4. **motion (A2).** build/motion.css is the section "motion (premium A2)" right after the old motion block and before
   touch targets and print (A1's pieces sit after print, so "after A1's sections" could not hold; nothing after it
   touches the same properties). Deleted, as A2 listed: the `animation` on `.menu`, `.popover`, the phone
   `.popover:not(.anchored)`, `.tip`, `dialog.sheet[open]` (+ phone `animation-name`), `dialog.sheet[open]::backdrop`,
   `dialog.more[open]`, `.toast`; `.toasts`' flex, direction and gap; main's 120ms view-transition line; `.sections`'
   old transition (motion's box-shadow + opacity one is the only one now); the wash on `.side-item[aria-current]`
   (it lives on `.nav-mark`, rendered on every current item; 600 weight kept). Kept: `@keyframes fade/rise`, the scrim,
   banner, selbar, verdict, palette and tabs-hint animations, the view-transition pins (B2 needs them) and ui.css's
   reduced block (`transition-duration: .01ms`), as A2 advised. Not clean: `.meter-bar > i` lost only its width
   transition; its `width: calc(...)` stays for any bare `.meter-bar` (motion's `.meter:not(.ticks)` rule wins in a
   meter). A1's press literals were left as literals (optional, same values as the tokens).
5. **Lead checklist (ui.js).** `.ts-sub` out of FOLD_SEL. `UI.shell({ ownPrimary: true })`: the Now strip's and the
   sidebar's Up next Start become `.btn sm` (the phone menu sheet's and the section bar's stay `.pill sm`); ui.css's
   `.nextup-go .pill` sizing rules now read `.nextup-go :is(.pill, .btn)` so the card keeps its height. A2's deferred
   section chips are in (A2 notes), so Tests' -44px shim and `rx.deferSections` can go in part 2.

### Why `UI.spotArt`

`UI.spot` is taken by design: index.html:1531 shows "Spot it · 3" on each habit row when `UI.spot` exists ("Spot it is
Review's (S10): offered once its client helper has loaded"; review.js:2137 has that `spot(o)`). Exporting the drawing
as `UI.spot` would light a dead button on Today and squat on Review's name. `spotArt` is used nowhere else.

### Checks

- `node --check` ui.js and kit.js; `tools/check-ui.py` ok; no em dash in the three files; ui.css braces 1653/1653,
  lightningcss 0 warnings (as before). jsdom probes: `UI.icon` (twin layers, '' + warning on an unknown name),
  `ICON_FILL`, `UI.spotArt` (start, done), every topic glyph draws on the new viewBox, NAV compete, kit VERBS icons;
  `ownPrimary` gives `.btn sm` in the strip and sidebar and `.pill sm` without it.
- Smoke, A/B after every step against the same live page tree with my three files held at their pre-merge copies
  (pages were changing under me): Today fresh/plan/review/stretch/test at 1440 and 390, page.js practice
  (FIX=practice), review, results, tests, plan, words, me, compete, help, weekplanner, plus admin/students, student,
  reports. **No difference at any step**, except compete's stack line `:302` -> `:308`: ui.js's 6 new header lines
  (same source line, verified). Unchanged from before: me's 6 and compete's crash (fixture gaps, S.hub.daily).
- Visual (browser free: demo-review's newest shot 20:10, run at 21:29): Today and Practice at 1440 render the Phosphor
  icons at 1.4px with the current item's fill twin, the new topic glyphs in Practice's set chips, Geist loaded
  (Marks loads only when a page uses a mark Geist lacks). Shots: `.playwright-mcp/integ-today-1440.png`,
  `integ-practice-1440.png`.

### The API for part 2 (new from the merge)

| Call | What it does |
|---|---|
| `UI.icon(name, size)` | An svg node from `UI.ICON` (twins included); '' for an unknown name (a warning on localhost). `UI.svg(UI.ICON[name], size)` still gives a string. |
| `UI.ICON_FILL[name]` | The filled layer alone (16 names), for a page that draws its own "on" state. |
| `UI.spotArt(kind, ms)` | An svg string for an empty state: `'start'` first use, `'clear'` all clear, `'lost'` 404, `'done'` with the four masteries 0..1 (set summary, test finished). Never in sheets, popovers or filtered empties. |
| `UI.shell({ ..., ownPrimary: true })` | Practice, Today, Tests: Up next's Start in the Now strip and the sidebar is a `.btn`, so the page's hero keeps the one orange button. |
| A2's | `data-m="stagger"` + `data-m-now` page entry, `UI.glide`, `UI.fx.check/ring/flame/pop/glow`, `UI.roll`, `UI.tile({countUp})`, `UI.motion.*` (enter, exit, draw, vt, once, spring), `UI.scrolled` / `data-scrolled`, `{mark: 'clip'}` on seg and tabs, `UI.shell({ sectionsAlways, chrome: 'focus' })` (see "## A2 motion"). |

## Shared asks (round 3)

Files: web/assets/kit.js, ui.js, ui.css only (no page file, no charts.js). Each API is in kit.js's or ui.js's top
comment (the chevron and tick looks in ui.css beside their rules). Line numbers are the page files as of 22:05.

### Built

- **`UI.meter({ tickStates })`**: a state per block (`'done'` lit, `'partial'` half, `'today'` outlined amber-deep,
  `'missed'` a faint mark, `'off'` an empty outline (today's ring is 1px: on a 6px block a thicker one reads solid), anything else a plain block; `data-s` on each), n = its length
  unless `ticks` is given; `.meter-n` and the aria values still come from value/max; `set()` lights new done blocks
  20ms apart. Plan: This week's `.pl-dots` row beside the ticks (plan.js:537-549, index.html:102-109) can become
  one meter (the day letters are the only thing left to place, if kept).
- **`UI.icon('external', 14)`** (Phosphor arrow-up-right regular, commit 2b75f3ad as build/icons.js): the shell's
  two `↗` texts are drawn with it (sidebar registration link, the deadline banner's College Board action);
  `.link > svg` sits on the text like `p > svg`. Plan: plan.js:625 `ic('arrow', 14)` -> `ic('external', 14)` and
  drop index.html:64 (`.pl-ext svg { rotate: -45deg }`).
- **Icons `key`, `envelope`, `fingerprint`, `shield`, `medal`** (same source and commit), twins: the fill shows
  on a pressed, checked or current control, and `UI.ICON_FILL` has all five (21 names now).
- **`UI.motion.enter(el, {axis: 'x', dir: 1 | -1, dx})`** (also `enter(el, 'slide', {dir, dx})`) and
  **`UI.motion.exit(el, 'slide' | {axis: 'x', dir})`**: sideways, 10px by default (dx 8 to 12); dir 1 is forward
  (enters from the right, leaves to the left). Plan: plan.js:763-764 plus index.html:499-503 (`.pl-in` / `plin`) ->
  `[...R.day.children].forEach(k => UI.motion.enter(k, { axis: 'x', dir: later ? 1 : -1, dx: 8 }))`; wizard.js:180 ->
  `UI.motion.enter(body, { axis: 'x', dir, dx: 12 })` (both get keys and reduced motion for free).
- **Every enter / exit kind now moves `translate` / `scale`, never `transform`** (the lead's ask from Results):
  a box centred with `translateX(-50%)` keeps its place, and so do the toast stack's offsets. Same for UI.glide's
  slides and `UI.fx.pop` / `flame` / the ring's closing beat (the `.ring` keeps its own rotation). Report:
  report.js:372 can use `'nudge'` for `.rp-rec` again instead of `'fade'`. Floor: `translate` / `scale` as keyframe
  properties need Chrome 104, Safari 14.1, Firefox 72; below that an entry or exit is the fade alone.
- **`UI.glide(list, mutate, { rows: '.selector' })`**: rows found anywhere inside list (rows in group sections),
  matched by data-key as before; new ones nudge in, moved ones slide, removed ones fade where they stood. Review:
  `glideRows` (review.js:582-598) goes; its calls at 537, 1078, 1776 and 2215 become
  `UI.glide($('list'), paintList, { rows: '.rh-row[data-key]' })` (2215 with its own callback).
- **The drawn dropdown chevron** (ui.css, `--caret-mask` = caret_down at 1.4px): every `.dd` (the old CSS border
  chevron is replaced in place, so nothing doubles) and every text `.btn[aria-haspopup="menu"]` (UI.menu.bind sets
  that) get a 16px caret that turns over while open. None on a trigger that already holds an svg (td-size,
  session.js `sm-more`, words-ui `tw-more`, icon buttons), `.btn.icon`, `.split-btn` parts (their one-turn fix is
  untouched) or a busy button. New with no page change: contest.js:701 (its trailing space can go), Report's View
  (report/page.js:1059), and every page-made `.dd` (results/page.js:484, practice builder.js:717 and #presets,
  words, charts.js:462). Optional: index.html:1158 (td-size) and session.js:622 may drop their own `caret_down`.
- **`UI.copyText(text, { button, fail })`** -> Promise<bool>: the button says Copying, then Copied with a check (or
  Not copied) through UI.saving, no toast. Retires the same two lines in me/settings/settings.js:31-32,
  s/index.html:392-393, results/page.js:196-197, tests/tests.js:948-949, compete-ui.js:1032-1033.
- **Tabs and seg slides**: the picked option turning 600 widens it a frame after the click; that resize no longer
  cuts the 200ms slide with `transition: none` (kit `slideMark`, the runner builder's report). No page change.
- **ui.css**: `body.has-focus #bar` on `--page`; the test window swaps icon twins at once
  (`body[data-page="test"] :is(g.ph-f, g.ph-o) { transition: none }`: a body `--i-t` would lose to the 150ms the
  active svg sets itself); `.filters-pop` rules shared (tests/index.html:168-170, words/index.html:36-38 except its
  260px min-width if wanted, words/mine/index.html:61-63 can go).

### Not built: UI.calendar is charts.js (the Results builder's file)

`UI.calendar` lives in web/assets/charts.js (loaded after kit.js, and its `draw()` rewrites the figure's class
every paint), so kit cannot wrap it. For the charts.js owner, three options in `calendar()`:
- `nav: false`: in `draw()`, leave `prevB`, `nextB` and the `.cal-jump` Today button out of `.cal-head`.
- `legend: 'why'`: instead of `parts.push(calLegend(...))`, `title.after(UI.why(() => calLegend(summary, D, P),
  { about: 'the calendar’s marks' }))` (the summary stays in the data table).
- `tasks: false` (**not `marks: false`**: `marks` is already the `{exam, start, end, today}` option, and false
  there would drop the SAT and the plan's range): skip the `.cal-tk` append.
Then Plan drops index.html:148 (`#week .cal-nav, .cal-jump, .cal-key` hidden), index.html:162 (`.pl .cal-tk`) and
plan.js:1629-1632 (the hand-made `?` key; 1628's filter to the month's marks can move into the why content).

### Already in place (checked, nothing to do)

`::view-transition { pointer-events: none }` (ui.css "view transitions"); the meter's off-by-one; `UI.nextMeta`;
the fold's ticking selector (`.rn-between-clock`, `.rn-segs`) and `.x-card` out of FOLD_SEL; `.reveal-host`;
`label.choice-row:has(input:disabled)` and the choice-row hover fixes; the `.card-fold` chevron turn; `.card-head
.chart-ctl`; the palette's and `tr.you`'s stripes; `--twocol-bottom`; the `.skill-row` container query in asides;
kit's heatmap readout block (gone, charts.js owns it); `UI.why`; `UI.meter({done: false})` for a pace.

### Skipped, and why

- A body class for "the sidebar shows the Now block": the media query is the native tool, and Practice's copy is
  one line (practice/index.html:56); a JS class would only mirror it.
- `.choices` first label flush: it would double with the pages' current `margin-left: -9px` until they drop it.
- Design calls left to the lead or the visual reviewer: `a.stat` / `button.stat` inline padding in cards, `.pill`
  at `--touch` on coarse pointers, a 44px `.quiet` hit area, `.stat-k` / `.stat-v` / `.streak` / `.card-head` type,
  `.badge` corners, chart text at 11.5 (needs charts.js `textW` too), `.skill-row.gain` height, `.lead-t` folding,
  `--bar` / `scroll-padding-top` (anchors would land under the sticky section bar), `--wash-solid`.
- API changes with several callers (not clearly safe this round): filterBar `keep` / `pop: 'wide'` / single-value
  chips, UI.tabs shared panel and per-tab labels, `UI.sheet({ foot })`, a synchronous `UI.fold`, one reason line in
  UI.seg, section chips skipping a sticky aside, `UI.help` / `UI.info` (UI.why covers them).
- One page each (ask again if a second page needs it): `.ring` level badge, pressed-row button, `.choice-row.plain`,
  `.twocol.interleave`, `.twocol-side.one`, `.tablist.inline` / `.sm`, shared slider row, breadcrumb.
- Not mine: charts.js (calendar, heat readout under the calendar, `.cal-grid` fluid, bar labels), smoke run.js /
  page.js, tour.js copy, check-ui.py, runner.js / runner.css.

### Checks

`node --check` kit.js and ui.js; `tools/check-ui.py` ok; ui.css braces 1665/1665, lightningcss 0 warnings (as
before); no em dash in the three files. Smoke A/B against the same live tree with the three files at their
pre-round copies: Today fresh/plan/review/stretch/test at 1440 and 390, page.js practice (FIX=practice), review,
results, tests, plan, words, me, compete at both widths, weekplanner: identical output, and identical to the run
before the edits (22 NO ERRORS; me's 6 and compete's crash are the known fixture gaps). A jsdom probe passes: the
six icons and five fill twins, tickStates (states, lit, delays on set, aria and `.meter-n` unchanged, plain ticks
15 of 22 still 15), enter / exit keyframes (translate / scale only, slide both ways), glide over nested rows,
copyText with a button. Not seen in a browser (the visual reviewer holds it): the chevron mask's size against
the old 6px chevron, the tick state looks, the slide.

## Shared asks (round 4)

Files: web/assets/ui.css, ui.js, kit.js only. Shots in `premium/shots/app-review/shared-r4-*` (`-before-` where one
was taken, `-after-` light, `-dark`, `-390`; 390 shots are a phone: touch and a coarse pointer).

### Built

From Practice:
- **Menu radios** draw only the checked item's mark; the others keep its 18px slot, so labels line up (checkboxes keep
  their empty box). `menu-view-*`, `menu-presets-*`.
- **Seg thumb** is a raised white thumb with the `.btn` fine edge, no amber ring (`--seg-thumb`); dark lifts the thumb
  a step above whatever well it sits in (`--thumb`, declared on `.seg` and `.wtabs`), since `--face` was darker than a
  card's or sheet's well and read sunk. Every seg read as selected in both themes: `segs-sheet-light`,
  `segs-sheet-dark` (Practice, Results x2, Tests, Words, Settings x2, Leaderboard, Me), `seg-start-*`.
- **Section bar's Up next Start** is `.btn sm` under `UI.shell({ ownPrimary })` too. `bar-before-390` / `bar-after-390`.
- **Save banner**: one short line ("Your progress is only in this browser.", under the fold's 70 characters, so no
  toggle and no stray chevron), `Save to email` as `.btn sm`, Not now quiet; `.banner-t` basis 320 -> 220 so the icon
  and text share a line at 390: two lines in all. `banner-*`, `today-after-390`.
- **Sidebar Resume chips** (Practice, Tests) are `.badge.soft`. `menu-view-after-1440`.
- **Practice map**: the cells are page code (see asks); the shared changes below (correct as a wash, a number-less cell's
  glyph centred) already take the wall of orange away. `map-after-*`.

From Tests and the lead:
- **Empty-state "Example" tag** is the sample's first child on its own line (kit.js), never over its content.
  `empty-tests-*`, `empty-review-*`, `empty-results-*` (challenge had none showing).
- **Sidebar account row**: no chevron in the full sidebar (the row's hover band says it is a button; the svg stays in the
  DOM for the rail rule), `.side-sub` one line with an ellipsis only past ~100px. "Student DDDD" and "Not saved yet" fit
  at 1440x900, 1440x680, the 1024 overlay, light and dark. A masked email now ellipsizes instead of wrapping; a shared
  computer's line is "Shared computer" (was "Shared computer · Sign out", which would cut; the tooltip and the menu's
  Sign out carry it).
  `foot-before-*`, `foot-sheet-after`.

From Today and the lead:
- **Rail play** is the white `.btn` face under ownPrimary (`.side-play.own`). `rail-*-after-1024[-dark]`.
- **`.ibtn[aria-expanded]`**: the well stays only on a menu / dialog trigger held open (`[aria-haspopup]`); an open
  fold's arrow keeps ink, no well.
- **`button.streak`** reset (no native border or background).
- **Toast countdown line** graphite (ink 30%). `toast-after-1440[-dark]`.
- **Chrome dots and counts graphite**: tab bar dots, the account row and Results meta dots, the phone bar's avatar dot,
  rail dots (`--ink-2`); rail count bubble and phone avatar count ink; sidebar unread count `.badge.soft`; the phone bar's
  review chip on `--well`. What each dot says: Today tab, today's plan or an urgent Up next waiting; Tests tab, a test to
  resume or a test day; Results, a new report; the review chip's dot, reviews due today; the avatar's dot, today's
  challenge not started; the account row's, progress not saved to an email. None is an alert, so none stays orange.
  `today-after-390`, `bar-after-390`.

From Results:
- **Calendar**: today is its number (700, 1.5px underline), no box; the heat look's picked day one 1.5px ink ring 1px
  out (was 1.5px ink plus a 2px outline); the plan look's today the cell's own 1px hairline in ink. `cal-heat-after-*`,
  `cal-plan-after-*`.
- **Band chart hover**: no grey column (it already dims the other sittings). `chart-hover-after-*`.
- **Correct, repaired and mixed cells are an amber wash** (`--st-bg: --wash-2`, ink glyph, amber-deep flag; mixed a
  half wash with a soft amber edge), site-wide: cells, legend swatches, strips. `--st-fill` stays amber, so chart bars
  and the runner's glyphs and progress segments are unchanged. `cells-report-after-*`.
- **`.ch-zone` in dark**: 10% fill, 30% edge.
- **`UI.counter`** shows from `.near` (90%) and `.over`; before that it keeps its line (`visibility: hidden`, nothing
  moves when it shows) and stays the field's description. Callers checked: talk.js x2, tests.js, review.js x2,
  quick.js x2, question.js, report.js (its own hide rule is now redundant).

From Plan:
- **Default seg ring**: the shared thumb is now the grey ring, so Plan's own default-option rings match it (asks).
- **"Hold a tab for shortcuts"**: waits 1.5s, skips the visit when a fixed or sticky bar sits above the tabs (Practice's
  Start bar, Plan's builder foot), and leaves by itself after 8s (counted as seen). `hint-*-after-390`: shown on Today,
  Plan, Review; skipped on Practice.
- **One banner at a time**: a page's own `.banner` (no data-kind, e.g. Plan's) hides the shell's notices (sign-in, save,
  stage); system banners still show. `plan-plan-after-*` (Plan's banner only), `plan-fresh-after-*` (sign-in shows).
- **Keycaps** in Geist, not mono (`⇧Enter` on Plan's Start). `cal-plan-after-1440`.

From Words:
- **`UI.shell(page, opts)`** keeps opts (no other two-argument caller in web/).
- **`.twocol-side.card`** keeps its sticky and drops the -8px room from 1280px (Study's glance: sticky, margin 0).
- **Keycaps leave on touch** (`hover: none` and `pointer: coarse`), except a key that is content: the `?` sheet's
  table, Help's list, prose (checked at 390: Help keeps its keys, Today, Practice and Plan show none).

From Review:
- **No dead air in a gap layout**: the scroll sentinel is gone (the bar watches itself: stuck when its top sits at its
  CSS `top`, read from computed style, so the notch's safe area counts; 200px side slack in its root, so a bar
  overhanging by a pixel still reads whole), and while it waits it takes back main's row gap too. Checked on 20 shell
  pages at 390 and 1440: free at the top, stuck once scrolled wherever it shows and the page scrolls.
- **Filters sheet** 560px wide from 760px up (was 640). `filters-review-after-1440`.
- **A cell with no number** centres its glyph at 12px (Review's local rule, now shared).

From Profile / Compete / first run:
- **Field focus** amber-deep edge plus the soft halo (`.field`, `.otp input`), never the ink box. `field-*-after-*`.
- **`.choice-row`** rests with no fill and a 1px `--line` hairline; hover `--hover`; checked unchanged.
  `choice-compete-leaderboard-after-1440`.
- **Static stat in a card** `padding: 0` (link tiles already net 0). `me-after-*`.
- **`.otp input`** width from the row: `min(48px, calc((100% - 50px) / 6))`.
- **Pref rows**: an empty `.pref-state` is out of the flex (no 12px gap, still a live region); a dropdown in a pref row
  hides its own `.dd-k` (the row label says it) and shows its value in ink. `prefs-after-*`.

### Page-file asks

- practice/builder.js:986: the map passes answer statuses for type states; use the type map's own `'ready'` / `'met'` /
  `'unmet'` (or `UI.atlas`), and `size: 'sm'` (a number lands as a class "18", so cells are 40px); 982's help says
  "ringed when ready", which matches neither. Picked cells pass `current: true`, which is the test review's "on screen"
  ring (`--ring`, heavy and dark, one per picked cell in `map-after-1440`); `UI.atlas(..., { selectable })` has its own
  thin selection. builder.js:382: on /s/ as a visitor the banner prints
  "[object Object], [object Object]" for topics and a stray "null" line (from the Profile reviewer).
- practice/index.html:163: the local `.pr-kbd` touch rule can go if those are `.kbd` caps.
- tests/index.html:167-168: `.ts .empty-sample:has(> .badge) { padding-top: 28px }` and the badge's top / right go.
- review/index.html:28: `.rh > :is(div[aria-hidden="true"]:empty, nav.sections) { margin-top: -16px }` goes (it would
  now pull the header up 16px); :282's `padding-right: 84px` goes; :228 is shared now (keep :227's 22px size if wanted).
- results/index.html: `#overview .chart-hit:hover` goes.
- plan/index.html:319-321 and assets/plan-ui.js:156: the grey default-option rings now equal the shared thumb; drop
  them (keep `font-weight: 500` if the default should stay quieter).
- assets/words-ui.js:37 `.wt-mark`: `background: var(--thumb, var(--face))` (dark: its thumb is darker than its track).
  The touch keycap copies (words/study/index.html:67, words/run/index.html:97, words-ui.js:83) and Study's
  `.st .glance { margin: 0; position: sticky }` can go. Words' mains went block to dodge the sentinel's gaps
  (words/index.html:21, study:20, mine:20); a grid main with a gap is safe again if wanted.
- me/me.css: the `.id-card` stat padding, `.si` / `.pair` otp width and Settings' `.pref-state` order patches can go;
  so can the choice-row patches `.si-ways`, `.lb-metrics`, `.wk-pick`, `.cx-radio` (check each still wants its own look).
- assets/report.js:109 `.counter:not(.near, .over) { display: none }` is now redundant.
- challenge/index.html `.ch-row.you`: a side stripe (Profile reviewer's #10).
- compete pages: not `ownPrimary`, so the sidebar's orange Start sits beside "Start the challenge"
  (`choice-compete-leaderboard-after-1440`); `UI.shell({ ownPrimary: true })` would leave one.

### Skipped, and why

- The `strikes` icon (Rush) reading as "xxx": a redraw is a design call (three outlined circles with a cross, or
  Phosphor `heart` / `x-circle` repeated); say which.
- Two topic columns in the filters sheet: the checks are one flat grid (domain then sub rows), so columns would split a
  domain from its skills; capped at 560 instead.
- Plan's `.cal-sw.practice` / `.cal-sw.test` key look and the runner.js items in Review's list (not relayed, and
  runner.js is not mine).
- 390 before shots were taken before the lead's touch emulation; the after shots use it.

### Checks

`node --check` kit.js and ui.js; `tools/check-ui.py` ok; ui.css braces 1688/1688, lightningcss 0 warnings (as before);
no em dash in the three files or this section. Smoke A/B on one fresh copy of the live tree, the three files at their
pre-round copies vs now: Today fresh/plan/review/stretch/test and page.js practice (FIX=practice), review, results,
tests, plan, words, me, compete at 1440 and 390: 22 NO ERRORS both, errors identical (me's 6 and compete's crash are
the known fixture gaps); the only text change is "Example" now coming first in Review's and Results' samples.

## Round 4 page asks

Page files only (practice, tests, review, results, plan, plan-ui.js, words-ui.js, words/*, me.css, report.js). Shots in
`premium/shots/app-review/pageasks-<page>-<before|after>-<1440|1440-dark|390>[-clip].png` (390 is a phone: touch, coarse
pointer). Learners: a:v2revresults01, a:s790a6684c9aed61f5 (Shape the week), a fresh one (empty states, sign in, wizard).
Not mine and already done elsewhere: builder.js:382, challenge `.ch-row.you`, Compete `ownPrimary`.

- **review/index.html:28** done, narrowed rather than dropped. The rule matched two things: the shell's `nav.sections`
  (now takes back its own gap, so this pulled the header up 16px wherever the bar shows: 1024, 1440x680, phones) and
  kit.js's 1px `.scrolled` sentinel before `.rh-tabs` (still there; dropping that half put the tabs 16px lower, header
  to tabs 40px instead of 24). Kept the sentinel half only. The real cause of the old patch: the shell's banner (12px) and Up next strip
  (16px) carry their own bottom margin, which Review's flex gap doubled; new rules `.rh > .banner { margin-bottom: -4px }`
  and `.rh > .now-strip { margin-bottom: 0 }` (the lead may prefer lifting this into the shell for any gap main).
  Measured: the header now sits exactly where Practice's does at 1440 (94), 1024 (156), 390 (237), and with the banner
  dismissed (32 / 94 / 136). `review-*`.
- **review :282** done: the sample row's `padding-right: 84px` is gone (cursor kept); its title wraps 2 lines, not 3.
  `review-empty-*-390-clip`.
- **review :228** done: the no-number cell glyph rule is shared; :227's 22px size kept.
- **tests/index.html:167-168** done: no 28px dead strip above the Example tag. `tests-empty-*`.
- **results `#overview .chart-hit:hover`** done: same pixels; hovered hits read `rgba(0,0,0,0)` with the shared rule.
  `results-*`.
- **plan/index.html wz-seg3 rings** done: Normal is the shared thumb like Focus and Strong; kept `font-weight: 500` so
  the default stays a step quieter. `plan-wizard-*` (step 4, one row on Focus). wizard.js:676's comment ("only Focus and
  Strong wear the orange edge") is now stale; wizard.js is not mine.
- **plan-ui.js:156 wplan-c ring** done: the planned day is the shared thumb, `font-weight: 500` kept (a change is 600,
  and the bar's day label turns ink). `plan-week-*`.
- **practice/builder.js map** done: type statuses (`ready` filled with a tick, `met` a dot, `unmet` dashed; `open` is
  met plus the orange corner dot, as Me's atlas), `size: 'sm'` (28px at 1440; 44px touch on a phone, as before). No
  `current`: a picked cell is a toggle (`aria-pressed`) with a thin orange ring off the cell (1.5px page gap, 1.5px
  amber), matching the tree's picked rows; the help says what the map shows. A judgment call: a fully picked skill is a
  chain of orange rings; `--ink-2` in that one rule is the quieter alternative if wanted. `practice-map-*`,
  `practice-map-detail-after-1440[-dark]` (fold open, a focused picked cell).
- **practice/index.html:163 `.pr-kbd` touch rule** done: it is a `.kbd`, the shared rule hides it. `practice-search-*`
  (same pixels).
- **words-ui.js:37 `.wt-mark`** done: `var(--thumb, var(--face))`; dark now lifts the thumb above the track instead of
  sinking it, light unchanged. `words-*-clip`.
- **Touch keycap copies** done: words-ui.js:86 and Study's rule removed. words/run kept one line: `.wr .keys` is the
  page's "Space" span (`span.keys.meta`, not a `.kbd`), which the shared rule does not hide. `words-run-*` same pixels.
- **Study `.st .glance { margin: 0; position: sticky }`** done: computed sticky, margin 0 at 1280 and 1440 from ui.css.
- **Words mains as grid** not done (optional): a gap still doubles the banner's and Up next's own margins (see Review),
  so block stays; the three comments now say that instead of "sentinel".
- **me.css `.id-card` stat padding** done (same pixels, `me-*-clip`); **`.si` / `.pair` otp width** done (`pair-*` same);
  **`.wk-pick` rest look** done (`me-week-*-clip` same; its visible-checkbox rule stays).
- **me.css Settings `.pref-state` order** kept: the empty slot is ui.css's now, but on a phone a non-empty "Saved" sits
  before the control in the DOM, wraps onto its own line and drops the control 29px for 4s; `order: 1` puts it under
  the control. `settings-pref-removed-390` vs `settings-pref-kept-390`.
- **me.css `.si-ways`** kept its own look, changed: the shared rest hairline made the sign-in ways a stack of boxes, so
  the rule is now `box-shadow: none` (no fill was already shared). `signin-ways-after-*`.
- **report.js:109 counter** kept: ui.css holds the counter's line (`visibility: hidden`), which in the sheet's gap
  columns left ~28px of air under Summary and Details (sheet 49px taller). `feedback-kept-vs-removed-1440` (left kept,
  right removed); `feedback-after-*` is the kept rule. report.js's only diff is a comment on that line saying why.
- **Compete `.lb-metrics`, `.cx-radio`** not touched (compete/leaderboard/index.html, compete-ui.js are not mine):
  `.cx-radio`'s rest rule now equals the shared one and can go; `.lb-metrics` is "a list to pick from: plain rows",
  so like `.si-ways` it wants `box-shadow: none` instead of `background: none`.

Checks: `tools/check-ui.py` ok; `node --check` builder.js, plan-ui.js, words-ui.js, report.js and the 10 inline scripts
of the touched pages; no em dash in any touched file. A/B against a snapshot of web/ taken before these edits (only my
files differ): page.js at 1440 and 390 for practice (FIX=practice), review, results, tests, plan, words, words/study,
words/run, words/mine, me, me/settings, signin, pair: output identical (all NO ERRORS except me's fixture errors and
me/settings' crash, both identical before); inventory.js identical on all 26; run.js fresh/plan/review/stretch/test
NO ERRORS both; weekplanner.js 4 checks passed both.
