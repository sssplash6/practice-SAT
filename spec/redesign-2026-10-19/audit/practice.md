# Audit: Practice builder, quick sheet, palette

Scope: `web/practice/index.html` (inline `<style>` 17-313, markup 315-370), `web/practice/builder.js`,
`web/assets/quick.js`, `web/assets/palette.js`. Code-level only. Line refs are `file:line`; `ix` = index.html, `b` = builder.js.

## What a student sees

**1440x900** (sidebar 248, main 1192, `.page` content 1040 = `--max` 1120 minus 2x40 gutter). The 900px height tier
(ui.css:550) makes the sidebar nav-only, so the shell puts the Now strip at the top of main (ui.js:2412). Stack:

| Block | px | Source |
|---|---|---|
| `.page` top pad (3vh) | 27 | ui.css:364 |
| Now strip (Up next + Start) | 44 + 16 | ui.css:697 |
| `.pr-head`: subject seg 40, h1 36px/800, `#points` | ~107 | ix:318-326 |
| `#banners` (only with a set in progress or `?share=`) | 18 + ~62 | b:325 |
| `#ready`: fold button + 4 equal cards (2-line title clamp, 2-line meta, 34px pill) | 18 + 29 + ~138 | b:388-415 |
| `#searchSec`: 17px label, 56px animated field, `#sline`, empty `#results` | 18 + ~106 | ix:329-335 |
| `#presetSec` toggle (closed by default) | 18 + 29 | ix:336-341 |
| `.pr-thead` (Domains, Skills/Map/Habits, Select all, Clear, sort) | 18 + 50 | b:643 |
| `.dgrid`, 4 columns x 251px, tallest (PSDA, 7 skills) | ~316 | ix:121, 265 |
| fixed `.pr-abar` | 72 | ix:243-255 |

The task (tick skills) starts about 550px down; usable height ends at 828 (the bar), so 4-5 skill rows show. With a
set in progress, about 2. Three blocks above the tree are each a different way to start.

**390x844**: pbar 56 on top; tabs 64 + safe area and the action bar (~118: l1, l2, full-width 48px pill; ~140 with a
reason) at the bottom leave ~570px of scroll window. Pad 25, Now strip 60, head ~157 (links wrap to their own 44px
row), Ready 2x2 cards ~337. The first screen ends inside Ready. Search, Presets and the 2x2 domain tiles start
around 890px; each tile then opens a dialog (`openDomain`, b:719) to reach skills. The tree is two screens and a tap away.

## A. Purpose and primary action

- Purpose: build a set (skills + settings) and start it. Primary action: `#start` in the fixed bar, which opens the
  Start window (b:1560, 931), whose footer Start launches (b:966). Two clicks by design (tour.js:32).
- Competing starts in view at once: Now strip Start (shell), each Ready card's Start (b:401), search Enter (b:627;
  Enter on an empty field starts `ready[0]`, b:622), and when scrolled the sticky `.sections-next` "Up next: ... Start"
  (ui.js:2237). Ready cards are `/next?limit=3` (b:393), the same items the Now strip shows. Up to five orange/Start
  targets compete with the page's own.
- The subject seg sits above the h1 like a kicker (ix:320); the h1 is a 36px/800 word with no action beside it.

## B. Whitespace (concrete)

- `.pr-sec` margin-top 18 on six stacked sections (ix:34, 102); `.pr` bottom pad 120 desktop, 190 phone (ix:20, 284).
- Search block is 106px for one input: 17px label + 10 + 56px field + 8 + a 10px-margin empty `#results` (ix:81-97, 334).
- Ready cards ~138px tall for usually one-line content: clamp boxes reserve 2+2 lines (ix:42-47).
- Action bar min-height 72 for a 40px button (ix:246); phone ~118 (ix:305-308).
- Start window: radio rows 46px x 8 pools = 368 (ix:210); `.sgrp` 16px padding plus hairline (ix:202).
- h1 36px/800 (ui.css:768) vs DIRECTION page 22/600.

## C. Non-essential always-on content (FOLD_SEL, ui.js:2792)

- FOLD_SKIP (ui.js:2793) includes `dialog`, so nothing in the Start window, skill window, domain window, traps, share,
  quick sheet or palette ever folds. On the page only `.help` over 70 chars folds: R&W intro (b:291), R&W `b.note` (b:321),
  Map legend (b:880), long habit tells (b:897), three of four Your sets empty states (b:1414-1415, 86-87 chars). The
  empty states fold into a toggle labelled "Nothing in progress": an odd empty state.
- Not caught: `.pr-new` habits empty box (b:896, 120 chars, a filled tile), `.pr-card .meta` (2-line clamp),
  `.pr-banner p`, `.pr-note`. Shorten these rather than add them to FOLD_SEL; they are status, not help.
- Always-on that could reveal on hover/focus (`.reveal`): finished set rows show six actions each (Review, Rematch,
  Retake exact, Same settings, Share, Print, b:1433-1438); type rows show Try one, Learn, More (b:827); tree head
  Select all + Clear (b:658-659); presets row Save as preset, Copy link, Reset (b:472-474).
- Skill window leads with four stat tiles (`.sblock`, b:778) before the types the student came to tick; the
  "In {domain}" tile repeats the domain facts already in the domain header tooltip (b:713) and phone window (b:725).
- IA smell: "Your sets" (a 4-tab history table) lives inside the Presets fold (ix:338-339). The header link has to
  open the fold and scroll (`showSets`, b:1381).

## D. Sidebar use

- Right column (from 1280): the set summary and Start (today the fixed bottom bar), Ready rows, the resume row,
  the list links (Mistakes, Saved, Your sets), preset chips (a vertical list reads better than a wrapping row).
- Main column keeps: header, the search/filter row, the tree. Your sets is a 7-column table: main, not aside.
- Left nav: nothing new. Practice already gets a Resume badge there (ui.js:1489).

## E. Redundancy (page and shell)

- Up next, four times: Now strip, `.sections-next` on scroll, Ready card 1, Enter on empty search.
- Set in progress, four times: `#banners` (b:340), `pr-links` "Your sets · n in progress" (b:254), Your sets
  "In progress" tab, the shell's Practice "Resume" badge (ui.js:1489-1492). The palette's Suggested adds a fifth.
- Mistakes count: `pr-links` "Mistakes · n" (b:252) duplicates the Review nav badge "N due · M open" (ui.js:1494);
  the preset "My mistakes" (b:433) starts the same pool.
- Saved twice: `pr-links` Saved (b:253, sets pool and opens the window) and preset Saved (b:436, same pool plus all skills).
- Two set parsers: page `#q` and the palette both run `UI.parseSet` (b:569, palette.js:415) and both start a composed
  set on Enter. b:1563 registers `/` to focus `#q`, shadowing the shell's `/` = palette (ui.js:1061) on this page only.
  A shortcut collision, not a delete: both must stay reachable (Mod+K still opens the palette).
- Three resets: presets Reset (to prefs, b:474), linkNote "Use my defaults" (b:544), window "Reset to defaults" (to
  factory, b:1203). Same word, different targets.

## F. Local overrides, hardcodes, off-scale, inline

Dead code (grep counts in builder.js are zero): `.lvls` ix:219-225; `.inline` ix:217-218; `.pr-results`/`.pr-res`
ix:97-100 plus the never-filled `#results` ix:334; `.pr-chip .why/.x` ix:59-60; `.pr-map .atlas` ix:184 (the map
renders cells in a `.quick` div, b:883; the shared `.atlas` in ui.css:1416 stays); the 12-column
`.pr-grid` whose only child spans all columns ix:102-103, 279-280.

Re-implementations of shared pieces:
- `.pr-card .pill.sm` ix:48 is byte-identical to ui.css:789. `.pr-abar #start` ix:253 makes the pill 40px (rule: 42).
  `.pr-route .btn` ix:33 and `.skwin .btns .btn` ix:160 resize `.btn` to 34/36px; `.setrow .acts` ix:238 forces 34px.
- `.pr-thead select` ix:109 and `.pr-sets select` ix:234: two copies of `select.field` (ui.css:898).
- `.pr-chip` ix:55-58 re-creates `.chips > button` (ui.css:1065), with 10px corners vs DIRECTION's 8.
- `.pr-fold` ix:49-51 and the JS fold b:409-411, 1555-1559 re-create `details.fold` / `.card-fold`.
- `.pr-links a, button` ix:27-31: a new ghost-button style (CLAUDE.md: no new button styles); use `.quiet`.
- `.quiet` re-padded four times (ix:61, 108, 164, 176), which defeats its negative-margin hit area (ui.css:849-852).
- `.obadge` ix:132, 174, 275 re-creates `.badge.n` (ui.css:1196).
- `.tri` ix:113-118: a bare `role=checkbox` tri-state beside kit's `UI.triCheck` (used in the window, b:1168). Align the
  look, keep the element.
- `.pr-i` ix:73: an 18px circle `button` (radius 50%). check-ui.py only checks `.pill`/`.btn` selectors with `Npx`
  radii, so it passes the script and breaks the rule.
- `.dcard` ix:122 bordered paper card, radius 14 (DIRECTION: tile, no border, 12). `.pr-banner` ix:35 amber inset stripe.
- `.segfield` ix:63: radius 9, `var(--ctl, 44px)` fallback.
- Hardcoded colour: `#F18508`, `#FFC47A`, `rgba(241,133,8,…)` ix:86-88; `rgba(0,0,0,.25)` ix:243.
- Off-scale sizes (scale: 32, 22, 16, 14.5, 14, 12.5, 11.5): 17px ix:81, 84; 15px ix:127, 137, 198, 253; 13.5px ix:32,
  56, 77, 94, 98, 109, 128, 130, 146, 155, 163, 171, 176, 234, 235; 13px ix:29, 33, 78, 138, 153, 166, 183, 187, 199,
  214, 226, 238, 249; 12px ix:132, 173, 240; 11px ix:59, 73, 174, 275; weight 700 ix:43, 81, 127, 259.
- Words in mono: `#points` (shared `.meta`), "N types match" b:574, `.pr-links .n` ix:29, `.obadge`, `.setrow .mono`
  dates b:1441, quick tally quick.js:94, Start-window group `.k` (b:907), `.palette-group` and `.palette-foot`
  (ui.css:2222, 2231).
- Inline styles: builder 1 (b:689, a CSS var, fine). quick.js 59: every card, grid, margin and the whole Log-a-mistake
  flow (quick.js:67, 86, 93-99, 339-345, 397-410, 419-433, 471-474, 515-518, 547-564, 576-590). quick.js:563-564
  repaint the pressed state that `.btn[aria-pressed="true"]` (ui.css:828) already paints. palette.js 3 (183-184, 406).
- No `999px` in scope files; shared `.badge` is 999px (ui.css:1192) and shows in quick (quick.js:83, 150, 338).

## G. AI-slop tells

- Emoji `🏆` in set rows, b:1441.
- Em dash characters as null placeholders: b:16, 23, 295, 1445, 1493, 1494, 1498 (seven, all reach the UI).
- Uppercase mono kickers: Start-window group labels (b:907), R&W form label (b:306), quick domain labels
  (quick.js:368), palette group labels (shared).
- Four equal cards in a row (Ready, ix:40); amber side stripe (`.pr-banner` ix:36; palette selected row, shared).
- Dashed "Not sure" box, quick.js:405. Text glyphs as icons in buttons: `⋯` b:465, 816; `▾` b:810.
- The animated conic-gradient "glow" around the search (ix:82-93) breaks DIRECTION 6 and 7, but ix:79-80 records it as
  the user's call ("the glowing box is enough"). File under user calls, not slop.

## H. Copy

- "Build any set by typing it" (ix:330): a 17px marketing label over a form field; the placeholder already shows the syntax.
- Empty states are two sentences (b:1414-1415, 896); DIRECTION wants one line and one action.
- `sfootNote` "Saved as your defaults" is a permanent status line in the window (b:1202).
- Start window: "Questions from" and "Questions" are adjacent groups (b:1005, 1039); "Questions" means length.
- Mixed voice in presets: "My mistakes", "Check 3 skills I haven't tried" beside "Your top habit", "Plan focus" (b:428-444).
- "Again: your last set" (b:396); "Official questions you brought" (b:1396); "Reset" vs "Reset to defaults" (see E).

## I. CSS and layout bugs

1. `.tri::before { inset: -12px }` (ix:118) is a 44px box inside 38px rows at 1040+ (ix:269): neighbouring
   checkboxes' hit areas overlap by 3px, and reach 4px into the name button (gap 8, ix:269).
2. Phone bottom: `.pr` pads 190 (ix:284) with no safe area; tabs 64 + safe, bar ~118 (~140 with a reason, more with
   `#abarErr`). On a home-indicator phone the last rows (Your sets "Show more", the last tiles) sit under the bar.
3. R&W hides `#abar` (b:267) but keeps the 120/190px bottom pad (ix:20, 284).
4. `.setrow` 7-column grid (ix:235) holds from 760 to 1039px where content is ~650px; six actions alone need ~420.
   The phone rule starts at 759 (ix:301).
5. Breakpoints are viewport-based (ix:265, b:663) while the sidebar jumps 68 to 248 at 1100: at 1100-1279 the four
   tree columns are ~184px and "Lines, angles & triangles" wraps to three lines; Ready cards clamp to 185px wide.
6. Dimmed rows hide their reason at 1040+ (ix:272) and keep it only as `title` (b:872): no coarse-pointer path.
7. `.pr-card b/.meta` are `tabindex=0` and toggle on click only (b:403-404): focusable, not keyboard operable.
8. `.pr-sline .chipx` (ix:95) is a `span` (b:578) styled `cursor: pointer`: looks clickable, does nothing.
9. The search animation keeps running while focused and the page scrolls (ix:89); no `prefers-reduced-motion` gap,
   but it repaints a 1040px box forever.
10. `.quick` as a class name is used by the map's cell row (b:883) and by the quick sheet dialog (quick.js:673). No
    CSS clash today; a trap for the shared pass. `.srow` and `.trow` also exist with other meanings in runner/report/
    plan/review, so these page rules must never move to ui.css unprefixed.

## Redesign proposals (ranked)

1. **BIG: right column "Your set" from 1280.** Put `#abar` inside `aside.split-side` in the markup; below 1280 it stays
   `position: fixed` at the bottom (today's bar, phone unchanged); from 1280 it is static in the sticky aside. One
   element, no JS change, keeps `#abar/#l1/#l2/#start/#reason/#abarErr` (builder and tour.js:32). Show `B.sumText`
   (today only `#l1`'s tooltip, b:1561) as a visible line in the aside, keep the tooltip. Below it: compact Ready rows,
   the resume row, list links (Mistakes, Saved, Your sets), preset chips. Below 1280 this aside stacks **before**
   main (DIRECTION allows it per page), so Ready, resume and links stay at the top on 1100-1279 and phone as today;
   reset `.pr-abar-in`'s `max-width` and `margin: 0 auto` (ix:246) inside the aside. The tree gets main (~788px at 1440): two
   always-open domain columns. Switch `wide()` (b:663-665) and ix:265 from a viewport query to the tree's own width
   (container query plus a ResizeObserver). Result: whole tree on the first screen at 1440x900, no 72px bar, `.pr`
   bottom pad drops to the DIRECTION 48. Risk: medium (JS breakpoint, tour anchors). Zero loss checklist: Start opens
   the window, reason, error + Try again, worksheet gate (b:1246), `aria-live` on the window footer, `/` focus.
2. **Header to one row** (ix:318-326): h1 22px, subject seg beside it, `pr-links` at the right as `.quiet` links;
   `#points` stays one meta line (or moves to the aside from 1280); `#route` unchanged. Saves ~50px desktop, ~60 phone.
   Risk: low.
3. **Dedupe Up next on Ready's side.** Keep `UI.shell('practice')` as is: Ready is absent in R&W (b:413), when
   `/next` is empty (b:398) or `shell.has.next` is false (b:393), so the shell's Up next must stay. Mark Ready's first
   card `data-upnext` (when it is `nextItems()[0]`) and hide it wherever the shell already shows that item: the phone
   Now strip, and the lead's sidebar Now block from 700px tall (same media query; DIRECTION 4 already hides the strip
   and `.sections-next` there). Ready cards become 40px rows (title, one meta line, Start;
   `why` to the tooltip), drop the 2-line clamps and the tap-to-expand (fixes I7). Risk: low.
4. **BIG: Your sets out of the Presets fold.** Own section after the tree with its own remembered fold (or a sheet
   opened by the "Your sets" link; `showSets` b:1381 then opens it). Finished-row actions: Review visible, the other
   five in a `UI.menu` or `.reveal` (b:1433-1438). Below 1040 collapse `.setrow` to the phone layout (fixes I4).
   `🏆` to a `.badge.soft` "Challenge". Risk: low-medium.
5. **Search to a plain field in the tree head** (ix:329-335): `.field.sm` 40px (36 per DIRECTION) next to the view
   seg and sort, label `sr`, placeholder carries the syntax, parser hint in a `?` tooltip. Keep `#searchSec`, `#q`,
   `#sline`, Enter / Shift+Enter / ArrowUp / Esc, `?search=`, `/`. Delete `#results`. Saves ~90px.
   **Reverses a user call** (ix:79-80): needs a yes.
6. **Presets row:** `.pr-chip` to `.chips > button` (8px); Save as preset, Copy link, Reset into one `⋯` menu beside
   More presets (b:470-474); rename Reset to "My defaults" so it differs from the window's "Reset to defaults". Risk: low.
7. **Delete dead CSS and the vestigial grid** (list in F). Zero risk.
8. **Shared-component alignment** (page edits): drop ix:48; ix:253 back to plain `.pill`; ix:33, 160, 238 to
   `.btn.sm`/`.pill.sm` defaults; selects to `select.field.sm` (ix:109, 234, b:647, 1404-1406); `.pr-links` to `.quiet`;
   `.obadge` to `.badge.n`; the four `.quiet` re-paddings removed; `.pr-fold` to `details.fold`-style markup (keep
   `#presetTog`, `#presetBody`, `satf.pr.*` keys); `.pr-i` to the shared `.ibtn` or a `?` tooltip on the switch label;
   `.dcard` to tile without border; `.pr-banner` stripe off. Risk: low each.
9. **Type, mono, em dash, emoji** (page edits): sizes onto the scale (F list); em dash placeholders at b:16, 23, 295,
   1445, 1493, 1494, 1498 to blank or the shared null glyph; "N types match" off mono; Start-window group label
   "Questions" to "Length"; empty states to one line under 70 chars (b:1414-1415, 896). Risk: low.
10. **Phone fixes:** `.pr` pad = bar + tabs + `env(safe-area-inset-bottom)` (ix:284); bar to one row (l1 + Start
    `.pill`, l2 hidden on phone since the window footer repeats it, reason row only when set) (ix:305-308), saves ~55px;
    R&W drops the bottom pad when `#abar` is hidden (b:267). Risk: low.
11. **Skill window:** "Check my level" and the type list first; the four `.sblock` tiles become one two-column `dl.kv`
    behind a closed `details` "Your record" (b:777-778); drop the "In {domain}" tile (facts stay in the domain tooltip
    and phone window). Type row actions to `.reveal` (b:827). Risk: low.
12. **Quick sheet** (quick.js): name classes for the 59 inline styles (`.qk-card`, `.qk-head`, `.qk-row`, `.qk-grid`,
    `.qk-cell`, `.qk-example`), rules under Shared asks since quick.js loads on every page; delete quick.js:563-564;
    tally off mono (quick.js:94); dashed "Not sure" box to a hairline row (quick.js:405); fold "Where was it?" and the
    note behind "Add where (optional)" (quick.js:471-477). Risk: low.
13. **Palette** (palette.js:418): the empty query lists ~60 rows (Skills 19, Pages ~14, Actions ~18). Show Suggested,
    Recent, Pages, 5 Skills and 6 Actions, each group ending in an expander row ("All 19 skills", "More actions") on
    the existing `typeCap` / "Show more question types" pattern (palette.js:411, 422), so nothing needs a keystroke to
    exist. Inline styles at palette.js:183-184, 406 to classes. Risk: low.

## User calls to confirm (do not reverse silently)

- Glowing animated search box (ix:79-80). Ready fold and tap-to-expand titles (b:403, 407). No Edit on Ready cards (b:405).
- Bar Start opens the window, nothing auto-starts (b:1560, tour.js:32). Skill window keeps only "Check my level" (b:785).
- Type rows show difficulty only (b:821). Typed counts read "Other" (b:96). Pace lives in Feedback (b:1151).

## Shared asks (lead only: ui.css, ui.js, kit.js)

- None needed for Up next if DIRECTION 4 lands (sidebar Now block hides the strip and `.sections-next`); proposal 3
  only needs the media query the shell uses for that block, exposed as a body class or documented.
- `.k`, `.meta`, `.palette-group`, `.palette-foot` off mono and uppercase (ui.css:759, 767, 2222, 2231).
- `.split` / `.split-side` primitive with a container-friendly main; `.reveal` for row actions.
- FOLD_SKIP: nothing to add for this page; keep `dialog` exempt (the Start window must not fold its live lines).
- Quick sheet classes (proposal 12) in ui.css. `.badge` radius off 999px.
- check-ui.py (not lead-owned, but shared): also flag `border-radius: 50%` on any `button` rule (catches `.pr-i`).
