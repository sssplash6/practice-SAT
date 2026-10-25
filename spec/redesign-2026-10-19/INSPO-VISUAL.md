# UI redesign, 2026-10-19: visual audit of the inspiration sources

Measured in a real browser (Playwright, getComputedStyle) at 1440x900 and 390x844, 2026-10-19. Text-only research
is in [INSPO.md](INSPO.md); raw numbers from the first run are in [inspo/measured-so-far.md](inspo/measured-so-far.md);
screenshots in `inspo/shots/`. Numbers are px and ms unless marked. Colours given as hex (lab values rounded).

Contents: 1 per source (kitchen, smoothui, bencho, amicro, aceternity, 21st) / 2 what makes them look good /
3 shared-layer changes / 4 per-page changes / 5 new and replacement components / 6 contradictions with DIRECTION v2.

## 1. Per source

### 1.1 dqnamo.com/kitchen (first run; not revisited)

Loaded fully. Shots: `kitchen-home-1440`, `kitchen-home-390`, `kitchen-model-selector-1440`, `kitchen-menu-open-1440`,
`kitchen-menu-hover-detail-1440`, `kitchen-scroll-fade-list-1440`, `kitchen-dynamic-button-tabs-1440`.

| Element | Measured |
|---|---|
| Page | bg `#FCFCFC`, ink `#202020`, Inter; column 896 (32 padding), centred, no sidebar |
| Type, whole site | three sizes only: 16/400 brand, 14/400-500 titles and body, 12/400 descriptions (lh 20). Weights 400/500 |
| Greys | three ink steps carry hierarchy: `#202020` title, `#646464` secondary label, `#838383` description |
| Card grid | outer well r16, 1px `#F0F0F0`, bg `#F9F9F9`, padding 6, gap 6. Cards r13, 1px `#E8E8E8` + 2px bottom edge, white, padding 4 |
| Card body | preview well r8 bg `#F9F9F9` h160; text block padding 16/8/8; title row gap 12 with a 14px arrow at the far right |
| Card hover | bg to grayscale-2, border one step darker, 150 `(.4,0,.2,1)`; no lift, no shadow |
| Trigger button | 28 high, 14/500 `#646464`, white, r8, 1px `#E8E8E8`, padding 0 8, gap 6, shadow `inset 0 1px #fff9, 0 1px 2px -1px #0000001a` |
| Dark button (Send, Save) | 28 or 36 high, `#202020` fill, `#F9F9F9` text, r8, padding 0 12; four-layer shadow (rejected) |
| Composer | 448 wide, r12, 1px `#F0F0F0`, textarea 14/500 padding 12 |
| Popover menu | 240 wide, r8, 1px `#F0F0F0`, shadow `2px 2px 4px #00000005, 0 1px 2px #00000008` (barely there) |
| Menu search row | 33 high, hairline under it, input 14/400 32 high, icon at right |
| Menu option | 50 high two-line (14/400 title, 12 meta at 80%), r6, gap 8; active bg `#F9F9F9` ink `#202020`, rest `#646464` |
| Hover detail panel | opens beside the menu (240 wide), name 14/500, meta 12, 3-line description, 2x2 tick meters, then settings below a hairline |
| Segmented (Low/Medium/High) | 20 high, 12/400, padding 2 6, r6; on = `#F9F9F9` fill + ink, off = text only `#838383` |
| Tick meter | 10 columns, gap 4, each 5.6x12 r4; off `#F0F0F0`, on one colour |
| Demo tabs (Save/Copy/...) | 28 high, 12/500, padding 4 8, r6, gap 6; on = `#F0F0F0` fill + `#202020`, off = `#646464`, no fill, no border |
| Scroll-fade list | rows 40, padding 0 10, gap 10, r6; box 320 wide r13; fade 76 tall, surface to transparent, 75 linear, stops 10 short of the scrollbar |
| Dynamic button | width animates 80 to 161 over about 240 on `(.23,1,.32,1)`; label crossfades in a clipped slot |
| Hold to confirm | 36 high, red text on red-50, 1px red border, r8; fill layer wipes in by clip-path over 180 |
| Phone | same column, 16 side gutters, cards stack, description stays (no folding) |

What makes it look good: three type sizes and three greys do all the hierarchy; nothing is bold; borders are the
lightest grey that still reads (`#F0F0F0` on `#FCFCFC`); concentric radii (16 > 13 > 8) make nested boxes feel
machined; selected state is a fill, unselected is bare text, so a row of tabs has one shape in it, not five.

ADOPT
- Selected = soft fill, unselected = bare text, on tabs, chips, segmented and menu rows (one shape per row).
- Hierarchy by ink step before size: title `--ink`, label `--ink-2`, meta `--soft`; most text 14.5, metas 12.5.
- Popover: hairline + near-invisible shadow, search row with a hairline under it, two-line options with the meta muted.
- Scroll-fade list (76, 75 linear, stops short of the scrollbar).
- Dynamic label width animation for Save / Copy / Add word.
ADAPT
- Concentric radii: our 12 card, 8 inner well or row, 6 badge; dialogs 16.
- The detail panel beside a menu becomes the `.twocol` aside (select a row, its detail shows at the side).
REJECT
- Mono uppercase 10px kickers (INTELLIGENCE, DEMO, VARIANT), four-layer button shadows, the tactile/skeuomorph pieces,
  the floating dark dock (we have bottom tabs), 2px bottom border "edge" on cards (reads as a button, not a surface).

### 1.2 smoothui.dev

Loaded fully (docs shell plus `/preview/<name>?embed=1` demo pages). Shots: `smoothui-home-1440`,
`smoothui-docs-shell-pinned-list-1440`, `smoothui-dashboard-demo-1440`, `smoothui-tabs-page-1440`,
`smoothui-popover-open-1440`, `smoothui-badges-1440`, `smoothui-buttons-1440`, `smoothui-sidebar-1440`,
`smoothui-sidebar-collapsed-1440`, `smoothui-command-1440`, `smoothui-toast-1440`, `smoothui-digit-roll-1440`,
`smoothui-number-flow-1440`, `smoothui-contribution-graph-1440`, `smoothui-docs-390`, `smoothui-drawer-390`.

| Element | Measured |
|---|---|
| Shell | top bar 56, white, hairline under; left sidebar 240, white, 1px `#E2E2E2` right edge; page `#FAFAFA`; demo pane right half, dotted |
| Docs nav row | 34.6 high (13/400, padding 8, r10), ink `#737373`; active = brand text on 10% brand tint, no border |
| Docs nav groups | icon + 11px UPPERCASE label (rejected); on the phone drawer the same groups are sentence case 15/400 |
| Sidebar primitive | 240 wide; rows 36 (14/400, padding 0 10, gap 8, r8); active 14/500 on 10% ink fill; user row pinned at the bottom under a hairline; collapses to 56 with icon-only 36 rows and a 32 toggle |
| Dashboard demo nav | 176 wide, rows 32 (12/400, padding 8 12, r10, gap 4); active = ink fill, white text |
| Page title | H1 24/500 -0.6px; lead 15/24 `#3A3A3A`; H2 18/400 (weight 400, not bold) |
| Tabs | 40 high, 14/500, padding 10 16, gap 4; hairline under the list; 2px indicator slides `transform, width` 200 `(.23,1,.32,1)`; off tabs `#3A3A3A`, no fill |
| Buttons | 40 high, 14/500, padding 8 16, r8. Solid ink; outline = 1px 10% ring + `0 1px 2px -1px #0000001a`; ghost bare. Press 150 transform `(.23,1,.32,1)` |
| Input | 36 high, 14/400, padding 0 12, r8, 1px ink-25% border, `0 1px 2px #0000000d`; error = red border only; disabled = `#F0F0F0` fill |
| Field with label | label 14/500, 6 above the field; field 40 high r10, `#FAFAFA` fill, 1px hairline |
| Badge | 20 high, 12/500, padding 0 8 (fully round, rejected); status = 15% tint of the hue + dark text of that hue |
| Popover | 288 wide, r8, 1px hairline, padding 16, shadow `0 2px 4px -2px #00000014, 0 4px 6px -1px #0000001a`, 4 off the trigger; title 14/500, body 14/400 muted |
| Tooltip | inverted (ink fill, white text), 28 high, 12/400, padding 6 12, r8, 4 off, 150 opacity + transform |
| Command menu | 448 wide, r10, hairline, `0 1px 3px #0000000f`; input row 40 + hairline under; group label 12/500 sentence case, padding 6 8; options 32 high (14/400, padding 6 8, r6, gap 8); selected = 10% ink fill; kbd hints at the right edge |
| Toast | 352 wide, bottom right 16 inset, r10, hairline, padding 16, `0 8px 16px -6px #0000001f`; title 14/500 + one line 14/400 muted |
| Pinned list | rows 62 (padding 12, gap 12, r14, 1px 15% border, small shadow); title 14/500, meta 12/400; pinned group split from the rest by one 1px 10% hairline `<li>` with 4 margin; count `3 / 4 pinned` 12 tabular, top right |
| KPI tiles (demo) | r14, 1px 8% ring, padding 12, gap 12; label 12/400 muted over value 20/600 over a 12 delta |
| Contribution graph | 7 rows of 10 dots, 4 shades of one hue + empty, weekday labels 12 every other row, month labels 12, "Less / More" legend in one bottom row |
| Phone 390 | top bar 56 with three 34 icon buttons; demo first, docs after; nav is a right drawer 332 wide, `#F5F5F5`, rows 39 (15/400), scrolled to the active row, a section switcher on top, a small promo card pinned at the bottom |
| Scroll edge | sidebar list uses `mask-image: linear-gradient(transparent, #fff 12px, #fff calc(100% - 12px), transparent)` |

What makes it look good: the demo sits in its own pane, so the docs column is all text and stays narrow (560);
headings are weight 400-500, the size step does the work; every surface is white or `#FAFAFA` and separated by one
hairline; selected things are a tint, never a border plus a fill.

ADOPT
- Command menu anatomy for our `Mod+K` search: input row 40 with hairline under, sentence-case group labels 12/500,
  32 rows with r6, selected = soft fill, kbd hint right-aligned.
- Sidebar: user row pinned at the bottom under a hairline; collapse to an icon rail with the same row height.
- Scroll edges with `mask-image` 12 (works on any surface colour, no colour token needed): sidebar nav, chip rows.
- Tab underline indicator 2px sliding 200 on `--ease` for `.tablist`; off tabs bare text.
- Status badges as 15% tint + dark text of the same hue (fits `--st-*`).
- Toast: hairline, r10, one soft drop shadow, title + one muted line, bottom right on desktop.
- Pinned list grouping: one hairline between the pinned group and the rest, no header; count top right, 12 tabular.
ADAPT
- Active nav row: tint fill, but ours is `--well` grey with ink text, not an orange tint (orange is for the primary
  and progress only). Weight 500 on the active row, 400 on the rest.
- Tooltip inverted ink on our side: fine for kbd hints; definitions stay on `--paper` with a hairline (longer text).
- Buttons 40 / input 36: ours `.btn` 36 (`--ctl`), `.field` 48 and `.field.sm` 36, text 16 (iOS zoom floor).
REJECT
- Uppercase group labels with icons, fully round badges, the pink brand tint everywhere, the odometer digit boxes
  (number-flow), the hero halftone gradient, the floating sound/theme dock.

### 1.3 bencho.dev

Loaded in the browser (the text fetch had failed). The page runs inside its own scroll container; content fades
in after about 2 s. Shots: `bencho-home-1440`, `bencho-grid-1440`, `bencho-traffic-widget-1440`, `bencho-home-390`,
`bencho-toast-stack-page-1440`, `bencho-toast-stack-hover-1440`.

| Element | Measured |
|---|---|
| Page | white, Inter; top bar 72 with text nav (14/500, 36 high, padding 0 13), active ink `#17181A`, rest `#78797A` |
| Filter chips | 32 high, 14/500, padding 0 14, gap 8, 6% ink fill, fully round (rejected); one horizontal row that scrolls on the phone (no wrap, no fade) |
| Gallery tile | 459 wide (3 columns, gap 12, 20 gutters), 300 high, 6% ink fill, r28, no border, no shadow |
| Widget card | white on the grey tile, r20, padding 16, no border, no shadow (contrast of fills only) |
| Widget head | title 14/500 -0.01em, sub 12/400 `#868787` directly under it (no gap), segmented control top right |
| Segmented | track 6% ink, padding 2, r10, 32 high; options 28 high, 12/500, padding 0 10, r8; one white thumb slides `transform` 220 `(.22,1,.36,1)`, no shadow; off option grey text |
| Headline figure | 30/500, -0.9px (-0.03em), `tabular-nums`, digit roll on change; unit `visits` 13/400 grey on the same baseline |
| Bars | stacked, gap 2-3 per bar, rounded 3; only first and last x labels (12 grey) |
| Tick slider | 36 ticks, 3x20, r3, gap 4; on = ink, off = 70% grey; value 13 at the right; colour change 160 |
| Detail view | opens over the gallery (blurred, rejected); right panel 300: title 18/500, 13.5 description, settings rows: label left, control right |
| Slider row | 44 high, r10, 5% ink track, filled part darker, label 13.5 left inside the bar, value right inside the bar |
| Toast stack | toast 375 wide, 80 high, white, r20, padding 0 12 0 16; title 14/500, sub 13 grey; two older toasts peek 14 above; hover fans them into a list |
| Panel buttons | 40 high, 13/500, full width, fully round (rejected); primary ink fill, secondary 1px 16% ring |
| Phone 390 | search moves into the top bar centre, nav into a menu; gutter 14; one column of tiles |

What makes it look good: there are almost no borders on the page; grey tile, white card, ink text, three fills do
everything. Each widget states one number big, its unit small beside it, and a two-label axis. Controls sit inside
the thing they control (segmented in the card head, slider label inside the slider).

ADOPT
- Number first: figure 28 (our step) / 600, -0.03em, unit 12.5 `--soft` on the same baseline, title 14.5/600 above
  with a 12.5 sub directly under it, range control top right of the card head.
- Segmented: track `--well`, padding 2, r10; options `--ctl` - 4, r8; one sliding thumb (`--surface`), 200 `--ease`.
- Tick meter (3x20 ticks, gap 4, r3, on ink or orange, off `--track`) for minutes against goal and plan weeks.
- Axis with only first and last labels on small charts (Today minutes strip, Words forecast).
- Slider row with label and value inside the track for Plan settings (minutes per day, test date distance).
ADAPT
- Toast stack: the older toasts peek 8 above (not 14) and expand on hover or focus; ours keeps one toast in view on
  the phone. Toast corners 12, not 20.
- Fills instead of borders: works on bencho's white page because tiles are 6% ink; ours is `--paper` with `--tile`
  cards at 1.10:1, so keep the hairline (see §6).
REJECT
- r28 tiles and r20 cards (our 12), fully round chips and buttons, blurred backdrop behind the detail view,
  overshoot curve `(.28,1.3,.36,1)` on the search bar, content fading in after load.

### 1.4 amicro.vercel.app (now amicro.dev)

Loaded (redirects to amicro.dev; dark by default, measured in light after the theme toggle). Shots:
`amicro-home-1440`, `amicro-mono-charts-dark-1440`, `amicro-mono-charts-light-1440`, `amicro-heatmap-hover-1440`,
`amicro-charts-390`.

| Element | Measured |
|---|---|
| Page | white, Outfit; top nav is a segmented pill row (rejected), section tabs as a pill row under the hero |
| Chart card | white, r24, 1px `#E5E5E5`, padding 16; inset "stage" r14, `#F4F4F6`, padding 8 (card in a card, rejected) |
| Card head | figure 24/700 -0.6px, unit 12 mono beside it (mono rejected), small delta in the series colour, range control top right |
| Range control | track `#F7F7F7` + 1px hairline, padding 2, r8, 25 high; options 19 high 10/600 mono, padding 2 8, r6; on = ink fill, white text |
| Card caption (outside) | title 17/600 -0.015em, desc 13/500 `#737373`, one line, truncated with an ellipsis |
| Heatmap | 20 weeks x 7 days, cells 11.6 square, gap 3, r2.5; 5 levels of one hue, empty cells a faint tint of the same hue; month labels only (no weekday labels) |
| Heatmap hover | no floating tooltip: the hint line under the grid ("hover cells for daily metrics") is replaced in place by the readout ("8 commits on 2026-07-29"); the hovered cell gets a 1px ring |
| Line chart | horizontal dashed gridlines only, 5 y labels, 7 x labels, 9.5px grey; line 2.5 with white-stroked dots; comparison series dashed grey |
| Bars | ink bars r6, comparison bar beside each in light grey; weekday labels under |
| Copy action | a 32 icon button beside the card title, shown on hover at 1440, always shown on the phone |
| Phone 390 | cards full width with 32 gutters (too wide), the range control stays top right, charts keep all labels |

What makes it look good: one ink and one accent per chart; the number is the headline and the chart is its
evidence; nothing in the chart has a border or an axis line; hover adds detail in a fixed slot instead of a
floating box, so nothing covers the data.

ADOPT
- Heatmap: ours exists (`.heat`, 12 cells, gap 3, r3, 4 orange levels) and matches; take month labels only
  (weekday labels to screen readers) and the readout below.
- In-place readout: a fixed line under a chart that shows the hovered or focused cell ("3 sets, 42 min on 12 Oct"),
  empty state shows the total. Works with keyboard focus and on tap; nothing floats over the data.
- Chart chrome: dashed horizontal gridlines only, no axis line; comparison series dashed `--soft`.
- Hover-revealed secondary action beside a title, always visible on coarse pointers (= our `.reveal`).
ADAPT
- Figure in the card head: ours Geist 28/600 (not 700, not mono unit); delta 12.5 in a state colour plus a sign.
- Range control: ours is `.seg` at `--ctl` - 4 with Geist 12.5/500, not 10px mono.
- Axis labels 9.5px fail contrast at that size: ours 11.5 `--soft` (micro).
REJECT
- r24 card with an inset grey stage (card in a card), mono units and controls, pill nav, sponsor toast on the phone,
  32 phone gutters.

### 1.5 ui.aceternity.com

Loaded fully. Shots: `aceternity-docs-sidebar-page-1440`, `aceternity-sidebar-hover-open-1440`,
`aceternity-components-grid-1440`, `aceternity-docs-390`.

| Element | Measured |
|---|---|
| Shell | three columns at 1440: left nav 300 (`#FAFAFA`, no edge line), main 776 (x 332), right column 268 (x 1156) with one bordered card and a two-line note under it; top bar 64 with a hairline |
| Nav groups | 32-40 rows, icon + 14/500 `#6F6F6F` label, chevron at the right; groups collapse |
| Nav children | 28 high, 14/400 `#737373`, padding 4 8, r7.6; indented 44 with a 1px `#E5E5E5` guide line on the left; "New" tag 11 blue on blue-50 |
| Page head | breadcrumb 14 `#71717A` / ink; H1 36/700 -0.025em; lead 18/400 `#71717A`; tags 12 on `#F5F5F5` r4 |
| Preview / Code | segmented: track `#F7F7F7` padding 4 r9.6, 40 high; on = white, r7.6, `0 1px 3px #0000001a`, 32 high 14/500 |
| Stage | `#F7F7F7`, 1px `#EBEBEB`, r13.6, padding 16 around a white r10 canvas |
| Right card | white, 1px `#EBEBEB`, r13.6, padding 6, `0 1px 3px #0000000d`; image well, then 12 kicker, 16/600 title, 14 body, full-width CTA |
| Gallery card | 237 wide, `#F4F4F6` fill, r20, no border; image inset 4 with its own r16; title 20/700 `#3F3F3F`, two-line desc 15 `#737373`, ellipsis |
| Demo sidebar | 60 rail grows to 300 on hover (rejected); rows 36, 16/400, gap 8, icon 20 |
| Phone 390 | 16 gutters; top bar is logo + four 24 icons; Preview / Code shrink to icon-only tabs; "Copy prompt" shortens to "Prompt"; tags wrap |

What makes it look good: the right column is a real third column, not a floating panel: it holds one thing,
sticky, with a quiet note under it. The left nav uses a 1px guide line instead of indentation alone, so long lists
read as a tree without boxes.

ADOPT
- `.twocol-side` holds one card, sticky, with a quiet one-line note under it (no stack of cards in the aside).
- Collapsible nav groups with a 1px guide line on nested items (for Help's table of contents and Plan weeks).
- On the phone, controls shorten (icon-only tabs, shorter labels) instead of wrapping; ours keeps `aria-label`.
ADAPT
- A collapsed rail hides labels with `display: none` (no invisible tab stops); ours opens on the toggle or `[`,
  never on hover.
- Tags 12 on a grey fill, r4: ours `.badge` 11.5/500, r6.
REJECT
- Hover-to-expand sidebar (moves targets under the pointer), 36/700 titles and 20/700 card titles (too loud for
  a study tool), r20 gallery cards, blue CTA, the gallery-of-previews look.

### 1.6 21st.dev

Loaded (home is a dark marketing page; the app shell is on the listing pages; component previews render in an
iframe). Shots: `21st-home-1440`, `21st-sidebar-listing-1440`, `21st-component-page-1440`, `21st-listing-390`.

| Element | Measured |
|---|---|
| Shell | white page; sidebar 240 with no fill and no edge line (spacing separates it); listing 4 columns of 272, gap 32 rows / 24 columns |
| Sidebar head | back chevron + section name; search field fills the row: 32 high, `#EFEFEF` fill, no border, r6, 14/500, `/` key hint at the right |
| Nav row | 32 high, 14/500 `#737373`, padding 0 8 0 2, r6, icon 16; count right-aligned 12/500 at 60% of the label colour; hover fill + `scale` 150 |
| Nav group label | `Marketing Blocks` 12/500 `#737373`, sentence case, 16 above the group, no line |
| Tags in nav | "New", "Updated" 11/500 blue on 15% blue, 20 high, padding 0 6 (round, rejected) |
| Pinned sidebar card | at the bottom of the sidebar: white, 1px 70% hairline, r8, padding 12, gap 12, `0 1px 4px -2px #0000001f`; title 13/500, two short lines 14 grey, one full-width button, a dismiss button 24 (aria-label "Dismiss ... announcement") |
| Listing card | thumbnail 272x204, 1px `#E4E4E7`, r8, `#EFEFEF` behind; title 14/500 under it, "by" line 12/500 grey; no card box around the text |
| Component page | single column ~800 between two hairlines; title 24/600, three-line lead 15 grey, author row, action row (primary split button, secondary, then text buttons with icons), preview below |
| Dashboard demo (community) | stat row with coloured icon chips (slop) but a useful "Quick stats" aside: label left, value right, a thin meter under each, 3 rows |
| Phone 390 | top bar: menu, page name, one action; bottom tab bar 57 high, 4 tabs (icon 24 over 10/500 label), `#FFFFFFCC` with blur(8px) (blur rejected), 1px top hairline; gutters 12 |

What makes it look good: the listing has no card chrome at all; the thumbnail carries a hairline and the text
sits under it, so 16 items read as a calm grid. Counts in the nav are quiet (60% grey) and right-aligned, so the
labels stay the first thing read. The pinned card at the bottom of the sidebar is small, dismissible and never
covers navigation.

ADOPT
- Sidebar search: fills the row, filled `--well` (no border), r8 (our scale), key hint at the right edge.
- Quiet right-aligned counts in nav rows: 11.5 micro, `--soft`, tabular (Review due count, Words due, Practice).
- Sentence-case group label 12.5/500 `--soft`, 16 above its group, no line; or no label (DIRECTION's sr-only).
- Pinned card above the user row = our Now block: `--surface` card, hairline, r12 (ours), padding 12, a 24 icon
  button to fold it (folding remembered, never lost).
- Lists of things with a preview (mocks, tests): the preview carries the hairline, text sits under it, no box.
- Aside "Quick stats": label left, value right, thin meter under each row (Results, Today side).
ADAPT
- Phone bottom tabs: theirs 4 tabs, 10px labels, blur. Ours keeps five tabs, solid `--tile` with a hairline,
  labels 11.5 (micro), no blur.
- Hover `scale` on nav rows: ours no scale on nav (rows are wide); press only on buttons.
REJECT
- The dark marketing home (gradient, serif italic accent, blue CTA), coloured icon chips on stats, uppercase
  "ACCOUNT" labels, blue counters, round tags.

## 2. What makes them look good

1. Two or three type sizes do nearly all the work (kitchen 16/14/12, 21st 14/12, bencho 14/12 plus one 30 figure).
2. Hierarchy comes from ink steps before size or weight: kitchen `#202020` / `#646464` / `#838383`; 21st counts at 60%.
3. Titles are weight 500 (kitchen, smoothui, bencho, 21st); 600 appears only on a headline figure or a section head.
4. Selected is one signal: a soft fill, a sliding white thumb, or a 2px underline. Never fill plus ring plus bold.
5. Borders are 1px, the faintest grey that still reads, one per boundary; text under a preview sits in no box.
6. Radii nest: outer = inner + padding (kitchen 16 > 13 > 8, bencho 10 > 8, aceternity 9.6 > 7.6).
7. Floats cast small shadows: popover `0 4px 6px -1px #0000001a`, toast `0 8px 16px -6px #0000001f`; kitchen's is near zero.
8. A number leads, its unit sits small on the same baseline, the chart is evidence with two to five labels.
9. Controls live inside what they control: range switch in the card head, slider label inside the slider.
10. Secondary detail has a fixed slot: amicro's readout line, 21st's right-aligned counts, kitchen's 12px meta at 80%.
11. Hover reveals one extra action; the phone shows it always (amicro copy button).
12. One accent per screen; everything else is greyscale (smoothui pink only on the active row and the CTA).
13. Sidebars: 32-36 rows, search fills its row with a fill and no border, groups split by a gap, a small pinned card
    above the user row, edges masked 12 when the list scrolls.
14. Motion only on state change: indicators 200-220, popover and tooltip 150, press 150; nothing on load (kitchen).

## 3. Shared-layer changes (ui.css), ranked

Old -> new. Shot names are in `inspo/shots/`. "ui.js" marks a shared ask beyond CSS.

| # | Rule | Now | New | Source, shot |
|---|---|---|---|---|
| 1 | Selected state on `.chips >[aria-pressed]`, `.btn[aria-pressed]`, `.dd.on`, `button.stat[aria-pressed]` | `--wash-2` + inset 1.5 `--amber` + 600 | `--ink` fill, `--on-ink` text, 500; no ring; `.n` counts and `.dd-v` inherit the colour at 75% (as `.btn.ink .n`). Orange stays for the primary, progress, tab underline, "yours" rows and the correct answer. Conflicts with ui.css header rule 4; lead's call | amicro range, smoothui dashboard nav; `amicro-mono-charts-light-1440`, `smoothui-dashboard-demo-1440` |
| 2 | `.seg [aria-checked]` | paper + amber ring + 600 | `--surface` thumb on `--well`, `0 0 0 1px var(--line)`, 500 ink; off options `--soft` | bencho, aceternity; `bencho-traffic-widget-1440` |
| 3 | `.sections > a` | 28 high, `--tile` fill; current `--wash-2` + amber ring | off: no fill, `--soft` text; current: `--well` fill, ink; same on the phone `::before` | kitchen demo tabs; `kitchen-dynamic-button-tabs-1440` |
| 4 | `.side-item[aria-current]` | `--wash` + 600 + 3px amber bar | `--well` fill + 600 ink; bar goes (one signal) | `smoothui-sidebar-1440`, `21st-sidebar-listing-1440` |
| 5 | `.menu`, `.popover`, `.tip` shadow | `--shadow-pop` 0 30 80 -30 .45 | new `--shadow-float: 0 4px 6px -1px rgba(30,30,30,.10), 0 2px 4px -2px rgba(30,30,30,.08)` plus the 1px line; sheets and palette keep `--shadow-pop` | `smoothui-popover-open-1440`, `kitchen-menu-open-1440` |
| 6 | `dialog.palette` | r14; `.palette-q` 56 high, input 17; rows 44; selected `--wash` | r12; 44 high, 16; rows `--ctl` (36, 44 coarse); selected `--well`; group label stays 12.5 | `smoothui-command-1440` |
| 7 | `.side-search` | paper + inset 1px line | `--well` fill, no ring, r8; hover 6% darker | `21st-sidebar-listing-1440` |
| 8 | Scroll edges: `.side-nav`, `.sections` (phone), `.chips` that scroll, `.palette-list` | thin scrollbar, hard clip | `mask-image: linear-gradient(transparent, #000 12px, #000 calc(100% - 12px), transparent)` (the `.table-wrap.more-r` pattern) | `smoothui-drawer-390`, `kitchen-scroll-fade-list-1440` |
| 9 | `.tablist` | per-tab `::after`, selected 600 | one indicator sliding `transform, width` 200 `--ease` (ui.js); selected 500 ink | `smoothui-tabs-page-1440` |
| 10 | `.seg` thumb | jumps | slides `transform` 200 `--ease` (ui.js) | `bencho-traffic-widget-1440` |
| 11 | `.badge` default | `--wash-2` orange tint | `--well` + ink; status badges a 15% tint of `--st-*`; `.badge.n` keeps orange | `smoothui-badges-1440` |
| 12 | `.h3`, list row titles, `.side-name` | 600 | 500 (titles carry by ink, not weight); `.h1` `.h2` stay 600 | kitchen, `21st-sidebar-listing-1440` |
| 13 | `.toast` | ink fill, 48 min, r12, `--shadow-pop` | paper, 1px line, `--shadow-float`, title 14.5/500 + one 12.5 `--soft` line; Undo stays | `smoothui-toast-1440`, `bencho-toast-stack-page-1440` |
| 14 | `.heat-d` / `.heat-m` | weekday 10, month 10.5 | weekday labels sr-only; month 11.5 `--soft`; `.heat-stats` becomes the hover / focus readout | `amicro-heatmap-hover-1440` |
| 15 | `.tabs` (phone) labels | 10.5 | 11.5 (micro), active ink, others `--soft` | `21st-listing-390` |
| 16 | `.tip` padding | 7 10, r8 | 6 10, r8, 6 off the trigger, no motion | smoothui tooltip (measured: 28 high, 4 off, 150 fade; no shot) |

Unchanged and confirmed: `.pill` 42 / 10 and `.pill.sm`; `--card-pad` 16; `--row-h` 40; `--radius-card` 12; the
card hairline; `--ctl` 36; `.k` 12.5 sentence case; `.meter-bar` 4.

## 4. Per-page visual changes

- **Today** (`index.html`): 13 cards today (7 main, 6 aside). Aside becomes one surface "Today at a glance" with hairline
  rows (`#sum #exam #score #pace #chal #words` keep their ids): label left, value right, a 4px meter under pace and
  words (21st quick stats, aceternity one-card aside). Main leads with `#next` (the page's only orange pill);
  `#qotd #mist #gain` sit as rows of one surface; `#study` + `#cal` use the heatmap with the readout line.
- **Practice**: the aside holds only the Start bar (`#abar`) and the links as quiet rows with right-aligned counts
  (21st nav). Skill tree rows 40 with hairlines and counts 11.5 `--soft`; presets one chip row with the 12 mask.
- **Review**: `#rhtabs` with the sliding underline; `#list` rows 40, hairlines, row actions in `.reveal`; filters as
  chips with the ink selected state; selecting a row fills `.rh-pane` (kitchen's detail beside the list).
- **Results**: score as hero 44/600 with "/1600" at 14.5 `--soft` beside it; section cards number-first (28 + unit +
  delta), range `.seg` top right of the card head; charts: dashed horizontal gridlines only, no axis line, labels 11.5.
- **Tests**: `.ts-next` is the focal card; `.ts-sec` cards become rows of one surface; mock and test lists use the
  preview-with-hairline, text-under pattern (21st listing); 16 `.seg` pick up the thumb.
- **Plan**: week view as a tick meter per day (bencho); minutes per day as a slider row with label and value inside
  (bencho); nested week rows with a 1px guide line (aceternity nav).
- **Words**: counts quiet and right-aligned; Add word uses the dynamic label (Adding, Added); the learnt count rolls
  after a run; the 14-day forecast as bars with first and last date labels only.
- **Profile** (`me/`): heatmap readout, sessions as rows; Save uses the dynamic label.
- **Compete**: 8 cards to a list plus aside; leaderboard stays `.table` with `tr.you` (orange marks yours); contest
  countdown figure 28 tabular; all-caps strings in JS go sentence case (DIRECTION §1).
- **Answering screens**: `.opt.picked` and `.opt.ok` are identical today (`--wash` + amber ring), so a pick looks
  correct before Check. Picked becomes paper with a 1.5 `--ink` ring (Bluebook's dark outline); orange only on `.ok`.
  `.x-card` drops its tile box for a hairline above it when it sits in a card. Serif, `.opt .l` circles, `.t-digits`
  mono and the chrome-free window stay.

## 5. New and replacement components, ranked

Ranked by value to a student. Several exist already; the row says so.

| # | Component | Source, shot | Where it goes | Why for a student | Size | Function kept |
|---|---|---|---|---|---|---|
| 1 | Sidebar Now card with fold memory (extends `.nextup` + `.side-day`) | `21st-sidebar-listing-1440` | shell sidebar, above the user row; a 24 fold button turns it into one line "Up next · title · Start" | the next task is one click away on every page without eating nav | S | Start, the more list, reason tooltip all stay; fold state remembered; Now strip unchanged below 700 tall |
| 2 | Command palette restyle (exists, `dialog.palette`) | `smoothui-command-1440`, `kitchen-menu-open-1440` | Mod+K everywhere | faster scan: 36 rows, quiet groups, key hints at the right | S (CSS) | same rows, groups, Tab sub-actions, phone layout |
| 3 | Heatmap readout (extends `UI.heatmap`) | `amicro-heatmap-hover-1440`, `smoothui-contribution-graph-1440` | Profile activity, Today `#study` | consistency at a glance; the day's numbers show on tap with nothing covering the grid | S | tooltip and aria-label keep the numbers; readout repeats them |
| 4 | Sliding indicator for `.tablist` and `.seg` (replaces static marks) | `smoothui-tabs-page-1440`, `bencho-traffic-widget-1440` | every tab and segmented control | the eye follows the change; one shape per row | S (ui.js) | roles, arrows, Home/End unchanged |
| 5 | Neutral selected state (replaces wash + ring) | `amicro-mono-charts-light-1440`, `kitchen-dynamic-button-tabs-1440` | chips, filters, pressed buttons, sections, nav | orange means "do this" again, so the primary is found first | M (CSS) | aria-pressed / -checked / -current untouched |
| 6 | Tick meter `.meter.ticks` (new variant of `.meter`) | `bencho-grid-1440`, `kitchen-menu-hover-detail-1440` | Today minutes against goal, Plan week, Words daily target | minutes read as blocks done, not a thin bar | S | `.meter-n` text and aria values kept |
| 7 | Digit roll for figures that change on screen (beside opt-in `countUp`, a 600 tween) | `bencho-traffic-widget-1440`, `smoothui-digit-roll-1440` | Results after a section scores, Words learnt after a run, Today minutes after a session; never on load | the change itself is visible | S | text set at once, aria-live as now, off under reduced motion |
| 8 | Dynamic label button (Save, Saving, Saved) | `kitchen-dynamic-button-tabs-1440` | Profile and settings Save, Copy link (share, pair), Add word | confirms in place, no toast needed | S | `.pref-state` text kept for screen readers |
| 9 | Toast stack (restyles `.toasts`) | `bencho-toast-stack-page-1440`, `smoothui-toast-1440` | all pages, bottom left (bottom on phone) | several confirmations no longer cover the page | M | every toast stays in the live region; Undo and its key stay |
| 10 | Scroll-fade edges | `smoothui-drawer-390`, `kitchen-scroll-fade-list-1440` | `.side-nav`, phone `.sections`, chip rows, palette list | shows there is more without a scrollbar | S (CSS) | nothing removed |
| 11 | Quick-stats rows in the aside | `21st-component-page-1440` | Today and Results asides | six facts in one calm block instead of six cards | M (page) | same figures, same links |
| 12 | Number-first card head | `bencho-traffic-widget-1440`, `amicro-mono-charts-light-1440` | Results, Today score and pace | the answer before the chart | S | charts and tables unchanged |
| 13 | Saved-first grouping (pinned list) | `smoothui-docs-shell-pinned-list-1440` | Review lists where `data-saved` exists: saved rows on top, one hairline, "3 saved" count | the questions a student marked come first | M | sort and filters still apply; nothing hidden |
| 14 | Slider row with label inside | `bencho-toast-stack-page-1440` | Plan minutes per day | one row instead of label, slider, number | M | native range underneath keeps keys and value |

Rejected for this app: hover-expand sidebar, expandable gallery cards, odometer digit boxes, blurred detail
backdrop, floating docks, glass tab bar.

## 6. Where the sources contradict DIRECTION v2

1. §1 card and row titles at 600: all four light sources set titles at 500 (kitchen 14/500, smoothui H1 24/500 and H2
   18/400, 21st 14/500, bencho 14/500); 600 only on figures. Proposal: `.h3` and row titles 500, `.h1` `.h2` 600.
2. §1 control 14 beside body 14.5: every source uses one size (14) for both. Confirms INSPO §5.2.
3. §0.6 "orange marks the primary and progress" vs ui.css rule 4 "orange marks the selection": the sources side
   with §0.6 (neutral selected state). Shared change 1 to 5 above.
4. §3 "shadows only on floats": kitchen and smoothui put a 1px ring + `0 1px 2px` on secondary buttons and inputs.
   No change proposed: our `--well` buttons read without it.
5. §3 `--shadow-pop` on every float: sources use 4-16 blur on menus and popovers, 80 nowhere. Split the token (row 5).
6. §1 figure 28 / -0.02em: bencho 30/500 -0.03em, amicro 24/700 -0.025em. Keep 28/600, tracking -0.03em.
7. §4 the Now block shows from 700 tall: 21st's pinned card is dismissible and never pushes nav; add the fold (§5.1).
8. §3 card hairline: confirmed. Fill-only separation (bencho, aceternity gallery) works only on white with 6% grey tiles.
