# Audit: the shared layer (ui.css minus the shell, kit.js, ui.js helpers)

Code-level, 2026-10-19. ui.css lines cited are today's; shell (297-756) skipped except where a token touches it.
Override counts are CSS rules outside ui.css (`.css`, `<style>` blocks, the `const CSS` strings in assets/*.js)
whose selector contains the class. "Words are never mono" and "no uppercase" are DIRECTION rules.

## 0. DIRECTION.md token table vs ui.css today (what would break)

- **No hero step.** Big figures run 40-96px on 8 pages (index.html:82,343; tests:49; report:85; words/run:121;
  compete.css:57; session:58 at 96) plus `.gauge-v` 56 (ui.css:1589). The 32px "figure" cannot carry them. Add hero.
- **Figure 32 grows every stat tile**: `.stat-v` is 26 (1166); 32 adds ~6px per tile, against "less whitespace". Use 28.
- **`.k` at 12px is off DIRECTION's own scale** (meta is 12.5). **item and body are both 14.5**: a wasted step.
- **control 14/500** would drop `.pill` from 700/15 and `.btn` from 600/14 to 500: the primary goes limp. Keep 600.
- **control 14 must not reach inputs.** `.field` is 16px (890): the iOS Safari focus-zoom floor. `.field.sm` is
  already 15px (896) and zooms on iPhone today: set it to 16.
- **`--card-pad` 14 (phone) and `.card-head` 10** are off the 4px grid: use 12 and 12.
- **"card gap 20" is not a token**: 22 page-local `gap: 20px`. Add `--card-gap`, never `--gap`: `--gap`, `--row`,
  `--lab` are shell-local tokens on `.side` (443, 552, 568, 578, 622); a root `--gap` would be shadowed there.
- **`--ctl` 36** makes `.seg` options 30px (`calc(var(--ctl) - 6px)`, 980) and leaves a mixed row at .btn 36 /
  .pill.sm 34 / .btn.sm 32; kit `button()` (kit.js:187) emits `.sm` for every sheet, banner, empty and selbar action.
  Fix with it: `.btn.sm` 34 (= `.pill.sm`), `.seg` items `calc(var(--ctl) - 4px)`.
- **`--max` 1200 changes nothing at 1440**: 1440 - 248 sidebar - 2x40 gutter = 1112 < 1120 already. It engages from
  ~1530px. `.bar-in` also reads it; `dialog.sheet[data-size="full"]` hardcodes 1120 (1985). Harmless, low value.
- **"Wells (--tile-2) for inputs on a tile"** contradicts 825/907/1148: tile-2 on tile is ~1.05:1 and vanishes, which
  is why ui.css already goes to `--mat` (buttons, skeletons) and `--paper` (fields) inside a card. Keep that.
- **"A card has no border"**: `.card.line` (paper + hairline, 1121) is live (s/index.html:223,288; builder.js:277,290).
  Keep it as the card-on-a-tile variant.
- `.page` padding (362) lives in the shell block: the shell pass owns it.

## 1. Type scale (8 steps)

Inventory: 40 distinct px sizes, 1293 declarations across web/ (font and font-size; clamp counted at its minimum;
qr.js excluded). By size (uses): 7 (1), 8 (7), 8.5 (2), 9 (17), 9.5 (3), 10 (29), 10.5 (28), 11 (66), 11.5 (38),
12 (130), 12.5 (119), **13 (180)**, 13.5 (97), **14 (194)**, 14.5 (73), 15 (122), 15.5 (10), 16 (35), 16.5 (2),
17 (25), 17.5 (1), 18 (21), 19 (4), 20 (15), 21 (1), 22 (11), 24 (10), 26 (7), 28 (12), 30 (6), 32 (5), 34 (3),
36 (5), 38 (1), 40 (3), 44 (4), 48 (2), 56 (2), 72 (1), 96 (1). Heaviest files: runner.css, ui.css, plan, index, tests.
Weights in ui.css (non-shell): 400 x21, 500 x84, 600 x33, 700 x12, 800 x2, 900 x1.

| Step | Size / weight / tracking | Absorbs | Uses | ui.css examples (line) |
|---|---|---|---|---|
| hero | 44 / 700 / -0.03em, lh 1, tnum | 34-96 | 22 | `.gauge-v` 56 (1589, keep its cqw clamp, cap 44) |
| figure | 28 / 600 / -0.02em, lh 1.05, tnum | 24-32 | 40 | `.stat-v` 26, `.countdown .num` 28, `.fact-v` 24 |
| page | 22 / 600 / -0.02em, lh 1.2 | 20-22, `.h1` clamp 26-36 | 27 | `.h1` (768) |
| section | 16 / 600 / -0.01em, lh 1.3 | 16-19 | 88 | `.h2`, card and sheet titles 18, `.mistake` 16, `.skill-gain` 18 |
| body | 14.5 / 400 (titles 600), lh 1.5 | 14.5-15.5 | 205 | `body` 15 (245), `.h3` 15, `.more-row` 15, `.cal-title` 15 |
| control | 14 / 500 (`.pill` `.btn` 600) | 13.5-14 | 291 | `.btn`, `.seg`, `.chips`, `.tablist` 14.5, menu rows, `.label` 13.5 |
| meta | 12.5 / 400-500, `--soft` | 12-13 | 429 | `.meta` 13, `.help`, `.legend`, `.table th` 12, `.pts`, `.k` |
| micro | 11.5 / 500 | 7-11.5 | 191 | `.badge`, `.kbd` 11, `.stat-k` 11, `.cal-key` 11, `.ring` |

- **13px (180)**: prose and metas go to meta 12.5; a control label goes to control 14 (`.btn.sm` 813 13 -> 14);
  table number cells (`.table .n` 13 mono, 1222) take the row's 14 with tnum.
- **13.5px (97, 19 in practice/index.html)**: labels and menu text go to control 14; sentences go to body 14.5.
- Weights: 400 / 500 / 600 only. `.h1` 800 -> 600, `.num` 900 -> 600, `.pill` 700 -> 600, card titles 700 -> 600.
- Out of scale by design: serif question text (`--q-size` 17/20/23, `--q-opt`, `.q-table` 16, `.grid-in .field` 20,
  `.grid-key` 18, `.why` 16, `.ref figcaption` 15, `.ref-facts` 15); em-relative (`.frac` .9em, `.sp` .72em,
  `.rad .ri` .62em, kbd .92em); glyphs drawn in fixed boxes (`.cell::after` 9/8, `.sw` 9, `.cal-sat`/`.cal-meta` 9,
  `.avatar[data-ring]` 9, `.heat-d` 10).
- Chart svg text (1489-1497, 10.5/11/11.5 mono) is coupled to charts.js:131 `textW(s, px)` (0.62em per DM Mono
  glyph; callers pass 10.5, 11, 11.5). Keep it mono at those sizes (figures only) until the results pass moves
  charts.js to the micro px; changing CSS alone breaks label collision math.

## 2. Spacing (4px grid)

Scale: **4 8 12 16 20 24 32 48**. 2 and 6 only inside a control (icon to label, track inset) and in mark grids.
No raw `--sp-*` ladder: nothing would read it. Role tokens only:

| Token | Today | New |
|---|---|---|
| `--card-pad` | 22, 16 phone | 16, 12 phone |
| `--card-gap` (new, root) | page-local 20 | 12 |
| `.card-head` margin-bottom / `.card-foot` margin-top | 16 / 18 | 12 / 12 |
| `--ctl` | 40 (44 coarse) | 36 (44 coarse) |
| `--row-h` (new) | rows 40-60 | 40: list rows set min-height, padding is derived |
| `--radius-card` | 14 | 12; point sheets (1977) and palette (2213) at it |
| sheet padding | head 16/14/10/24, body 4/24/22, foot 14/24 | 12/12/8/20, 0/20/16, 12/20 |
| `.page` top / bottom | clamp(16,3vh,32) / 88 | 16 / 48, phone keeps tab room (shell owns) |

Snaps for off-grid values in ui.css (non-shell count): 3 (21) -> 4, but `.strip`/`.atlas`/`.heat` 3px gaps stay
(1428-1429 hardcode `3px` in max-width calcs; change together or not at all); 5 (14) -> 4; 6 (46) stays only as
label/icon gap, else 8; 7, 9 (19) -> 8; 10 (53) -> 8 in gaps, 12 in padding; 11, 13 -> 12; 14 (27) -> 12 gap,
16 box padding; 15, 18 (12) -> 16; 22 (6) -> 16; 26, 28 -> 24; 30 -> 32. Biggest single cuts: `.verdict` 22 -> 16
(1964), `.opts`/`.grid-in` margin 26 -> 16 (1931, 1956), `.empty` 28 -> 16 (1267), `.stat` 14/16/15 -> 12/16,
`.banner` margin 16 -> 12, `.table td` 11 block -> min-height 40.

## 3. Surfaces

Tokens: paper FFFFFF, tile F6F4F0, tile-2 EFECE6, mat E9E5DF, line E4E1DC, wash/wash-2 (orange). Dark set is complete.
System: page = paper; card = tile, no border, no shadow; inside a card nothing is filled except wells (tracks,
buttons, segmented tracks) at `--mat` and fields at paper; floats = paper + `--shadow-pop`.

**Proposal (no class change):** generalise the chart-only `--surface` (1484-1486) into two inherited tokens:
`:root { --surface: var(--paper); --well: var(--tile-2); }`,
`:where(.card, .panel, .stat, .side, .now-strip > *) { --surface: var(--tile); --well: var(--mat); }`,
`:where(dialog, .popover, .menu) { --surface: var(--paper); --well: var(--tile-2); }`. Then `.btn`, `.skel`,
`.seg` track, `.chips > *`, `.chip`, `.opt`, `.countdown > span`, `.thumbs > *`, `.cal-d`/`.heat` `--h0`,
`.table .stick` read `--well`/`--surface`; nine `:where(.card, .panel ...)` patches (825, 907 stays for fields,
1148, 1237, 1242, 1485, 1651, 1679, 1719, 1750) collapse into the one rule.

Broken today:
- **Tile on tile (no compensation inside a card):** `.stat` (me.css:63 patches it to paper by hand), `.chips > *`
  (1068), `.chip` (1904), `.opt` (1936), `.countdown > span` (2327), `.thumbs > figure` (1248), `.banner.sys` (2198),
  hover fills `.x:hover` (2015) and `.legend button:hover` (1449), `.seg` track tile-2 (973). Per DIRECTION a `.stat`
  in a card loses its fill: `:where(.card, .panel) .stat { background: none; padding-inline: 0; }`.
- **Opposite compensations for one job:** an empty day cell goes lighter in a card for `.cal-d` (paper, 1651) and
  darker for `.heat` (mat, 1750). `.field` goes paper (907) while `.btn` goes mat (825) (fields are right to differ).
- **Two track colours:** `--mat` (`.meter-bar` 1182, `.skill-track` 2311, `.scale-track` 1608, range 943, `.switch`
  1031) vs `--track` (`.mbar` via `--m-track` 1887, `.spread-bar` 1792, `.sb-seg.empty` 1843). Use `--track`
  everywhere (alpha, so it reads on paper, tile and dark).
- **Shadows on non-floating things:** `.pill:hover` orange glow (793, "glow" is on the slop list) -> a 6% darker
  fill; `.seg` checked `0 1px 2px` (986) -> drop. Knob (1037), range thumb (949, 953) and `.stick-last` scroll cue
  (1243) are affordances: keep. `.tip` (2146) has its own hardcoded rgba shadow, not themed: use `--shadow-pop`.
- **Radius:** 999px on `.chips` (1067) -> 8, `.badge` (1192, 20px tall) -> 6, `.quad-chip` (1813) -> 6,
  `.tablist .n` 10 on 20px -> 6. Circular buttons that pass `tools/check-ui.py` (its regex reads only `\d+px`):
  `.skill-play` (2301, a `.pill.sm`/`.btn.sm` at 50%) -> 10, `.x` (2012) -> 8, page `.clock-tog` (index.html:160).
  Scale: 4 marks, 6 badges/tags, 8 chips/.btn.sm/menu rows/cells, 10 .btn/.pill/fields, 12 cards and floats,
  50% only avatars, dots, rings, radio marks, knobs. Extend check-ui.py to flag `50%` and `.chips` selectors.

## 4. Uppercase kickers: every rule and its replacement

Replacement unless stated: the new `.k` look, `font: 500 12.5px/1.3 var(--font); letter-spacing: 0;
text-transform: none; color: var(--soft)`, text in sentence case.

Shared (lead):
- ui.css:759 `.k` -> the look above (one rule change reaches ~194 elements: 15 in HTML, 179 from JS).
- ui.css:1124 `.card-head > .k { flex: 1 0 100% }` is what stacks a kicker above a card title. Page passes delete
  those kickers; the rule becomes `flex: 0 1 auto; margin: 0` so any left over sits on the title row as meta.
- ui.css:1165 `.stat-k`; 1917 `.q-skill`; 2093 `.menu-label`; 2222 `.palette-group`; 2255 `.calc-bar` -> the look.
- ui.css:1701 `.cal-phase`, 2241 `.ref figcaption small` -> micro 11.5/500 Geist, no transform.
- ui.css:461 `.side-word` (shell): the wordmark beside the logo. Brand lockup, keep; ask the user.
- ui.css:492 `.side-label` (shell): sr-only per DIRECTION.
- kit.js:215 `UI.date(d, 'eyebrow')` calls `.toUpperCase()`: delete it. Fixes index.html:914 and plan.js:733 with no
  caller change; keep the `'eyebrow'` argument name.
- Literal ALL-CAPS strings the CSS cannot fix (compete pass): contest.js:82,205,296,363,471,475,742,940;
  rankings.js:107,111,412,414; overview.js:234.

Page-local (their passes): index.html:72,80,263,420; words/index.html:77; admin/student:32,46; admin/students:32,46;
results/index.html:61,75; results/report/index.html:111,187; tests/index.html:158; plan/index.html:163,320,345,353;
review/index.html:62,89,211; review/print.html:28,47; runner.css:91,425,542,776,1191; results-ui.js:133;
compete-ui.js:77,92. **Keep:** review/print.html:50 (printed table head), s/index.html:47 and compete-ui.js:731
(code inputs), report.js:129 (file-type stub on a thumbnail).
Local `.k` rules that re-add caps or tracking and go with the change: index.html:93 (600 11px .06em),
plan/index.html:111,130,384, plan-ui.js:131, review/index.html:211 (re-uppercases); index.html:225 becomes dead.

## 5. Duplicate components (two classes, one job; never rename, share values)

1. `.h2` (769), `.card-head > h2/h3/.h2` (1123), `dialog.sheet > .sheet-head > h2` (1989): identical 700 18px
   declared three times -> one selector list.
2. Group label: `.k`, `.stat-k`, `.menu-label`, `.palette-group`, `.calc-bar`, `.q-skill`, `.ref small`, shell
   `.side-label` repeat the mono caps recipe -> one selector list with the new `.k` values.
3. Meta: `.meta` (mono 13), `.note` (mono 12.5), `.pts`, `.menu-meta`, `.opt-meta`, `.pref-state`, `.counter`,
   `.more-meta`, `.tip .m` -> one rule: meta 12.5 Geist tnum, `--soft`.
4. Helper: `.help`, `.card-sum`, `.stat-sub`, `.menu-sub`, `.opt-sub`, `.chart-note`, `.empty-text`: already sans,
   five line-heights (1.35-1.5) -> one list at 12.5/1.45.
5. Error: `.error` (1910), `.field-err` (910), `.card-err` (1137) each draw the ink dot -> share the dot rule.
6. Tracks: `.mbar`, `.meter-bar`, `.skill-track`, `.spread-bar`, `.scale-track` (3, 4, 4, 6, 8px; two colours) ->
   one colour (`--track`), heights 4 (inline) and 8 (`.lg`, scale).
7. Pick one: `.seg`, `.chips`, `.tablist`, `.choices` (choices is compete-only, 2 files). Same kit `choices()`
   drives `.seg` and `.chips`. Keep all four, document roles: seg = mode, chips = filters, tablist = panels,
   choices = numeric value.
8. Chip: `.chip` (topic chip, radius 10, 600) vs `.chips > *` (radius 999, 500). `button.chip` is used as a toggle
   (results/page.js:413, question.js:2473) with no hover, pressed or focus look -> add `button.chip` to the
   `.chips > *` state selectors.
9. Tag clones of `.badge`: `.quad-chip` (ui.css:1813), `.pl .tag` (plan:29), `.rh-kind`, `.rh-row .tag` (review:74,
   170), `.rp-chip` (report:29), `.wtag` (words-ui.js:68), `.guess-chip` (words/run:118), `.trap-chip`, `.rn-fmt`,
   `.rn-cond` (runner.css:265,542,425) -> page passes adopt `.badge`/`.badge.soft`/`.badge.line`.
10. Legends: `.cal-key` (1712) and `.heat-key` (1774) restate `.legend` in mono 11 -> share `.legend`'s type.
11. Icon buttons: `.x` (38 round), `.btn.icon`, shell `.ibtn` -> `.x` takes `.btn.icon.sm` size and radius 8.
12. Card clones outside ui.css that ignore `--card-pad`: `.adm-card`, `.adm-tile` (admin x2), `.par-card`,
    `.par-tile` (parent), `.ts-card`, `.ts-next` (tests), `.tw-card` (test), `.aq`, `.ad-act` (admin/reports).

## 6. Ranked ui.css / kit.js changes (page overrides of each selector)

1. **`.k` + group-label list** to Geist meta sentence case (759, 1124, 1165, 1917, 2093, 2222, 2255; kit.js:215).
   Overrides: `.k` 55 rules / 20 files (mostly margins; 6 fight it, listed in 4); `.stat-k` 4 / 3. Risk low.
2. **Mono off words** in ui.css: `.meta`, `.note`, `.pts`, `.menu-meta`, `.opt-meta`, `.pref-state`, `.counter`,
   `.legend b`, every `.n` count (812, 921, 991, 1016, 1074, 1196), `.stat-v`, `.stat-delta`, `.meter-n`, `.ring`,
   `.cal-*`, `.heat-*`, `.scale-row`, `.sb-n`, `.spread-v`, `.atlas-row`, `.fact-v`, `.skill-gain`, `.palette-foot`,
   `.preview` -> `var(--font)` + tnum. Mono stays: kbd/code (262), `.mono` (298), `.otp input`, `.countdown .num`,
   chart svg text. Do not flip `--mono` globally: runner.css (39 uses) needs it for `.t-digits` timer (440),
   `.sci-in`/`.sci-out` (382-383), `.scratch-ta` (770). Widest blast radius: `.meta` 59 rules / 21 files; 257 page
   `var(--mono)` uses stay until their passes.
3. **Type scale on shared heads**: body 15 -> 14.5, `.h1` -> 22/600, the `.h2` list -> 16/600, `.h3` 14.5, `.num`
   900 -> 600, `.pill` 15/700 -> 14/600, `.gauge-v` cap 44. Overrides: `.h1` 7 / 6 (review/index.html:25,228 force
   36/28: delete), `.h2` 4 / 2, `.card-head` 31 / 8 (margins), `.num` 11 / 7, `.stat-v` 9 / 6 (me.css:64 22px,
   runner.css:665 40px).
4. **Surface tokens** `--surface`/`--well` (section 3), `.stat` unfilled in a card, one track colour.
   Overrides: `.chips` 15 / 7, `.btn` 54 / 14, `.stat` 17 / 7, `.skel` 4 / 3, `.mbar` 9 / 4, `.meter` 1 / 1.
5. **Spacing tokens** (section 2). Overrides: `.card` 18 / 8, `.card-head` 31 / 8, `.card-foot` 3 / 2, `.sheet-body`
   6 / 4, `.sheet-foot` 7 / 2; tests/index.html:247 bleeds with `calc(-1 * var(--card-pad))` and follows; the card
   clones in 5.12 do not.
6. **Radius and round buttons** (section 3). Overrides: `.chips` 15 / 7, `.badge` 2 / 2, `.x` 7 / 4; page 999px:
   plan:29, review:74,170, report:29, words-ui.js:68, words/run:116,118, report.js:147 (tour.js is check-exempt).
7. **`--ctl` 36 with `.btn.sm` 34 and `.seg` -4px.** Overrides of `--ctl` in pages: 12 rules (index.html:160,164,
   265,275,430,432; practice:27,108,109,234; plan:260; words-ui.js:33) all track the token.
8. **Touch**: `.pill.sm` has no 44px hit area on coarse pointers (819-820 cover `.btn.sm`, `.ibtn`, `.x` only): add
   it. Phone `.sheet-foot > :is(.btn, .pill)` (2008) gets `min-height`/`height: var(--touch)`. `.field.sm` 16px.
9. **Shadows**: `.pill:hover` glow (793), `.seg` checked (986), `.tip` (2146). `.pill` overrides 47 / 22 (none
   restyle hover).
10. **Load motion**: kit `countUp` (kit.js:1465) with `.counting` (1172) animates every tile on first view, for its
    own sake (DIRECTION 7); make it opt-in (`o.countUp === true`), zero loss since the figure stays in the text.
    `.rise`/`.rise-2`/`.rise-3` (2357-2359, 15 uses) likewise -> no-op. `.mbar` 1.1s fill (1891) -> .2s.
11. **Missing value glyph is an em dash**: kit.js:210,212,220,229,231,1507,1511,1647 and ui.js:708 return
    U+2014. Replace with an en dash (U+2013, already the `unanswered` glyph) through one `const NONE` in each file;
    fix the comments at ui.css:1157 and kit.js:64.
12. **ui.js helpers' inline type**: `runBetween` figure `font: 500 20px var(--mono)` (ui.js:1158) -> figure step via
    `.num`; `runRail` builds its own segment bar inline (ui.js:1227-1228) -> `.strip`-like class in ui.css;
    keys sheet `h3.k` (1034, 1036) fine after 1.
13. **FOLD_SEL** (ui.js:2792): `.fold-s:hover` (2475) sits outside a hover media query (sticky on touch); wrap it.
    `.chart-ctl > .help`, `.cal-metric > .help`, `.quad-ctl > .help` (1498, 1642, 1808) hide kit `seg()`'s
    disabled-reason line: a disabled option there says nothing. Let it fold instead of `display: none`.
14. **New primitives** `.split`, `.split-side`, `.reveal`: no collisions in web/ (grep clean). Add after 1-4.
