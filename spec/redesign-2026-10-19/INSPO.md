# UI redesign, 2026-10-19: inspiration

Taste research behind [DIRECTION.md](DIRECTION.md). Sources: dqnamo.com/kitchen, smoothui.dev, bencho.dev,
amicro.vercel.app, ui.aceternity.com, 21st.dev. Built on apdash's premium-pass research (`kitchen.md`,
`charts-amicro-bencho.md`, `type-colour-assets.md`, `motion-libraries.md`), its `DIRECTION.md` and
`freshweek-design-system.md`. This file adds only what those miss for a student study tool: shell, density,
surfaces, disclosure, controls, fonts, and what to avoid. Numbers are px and ms unless marked.

## 0. What loaded (fetched 2026-10-19)

| Source | Status | Numbers below rest on |
|---|---|---|
| dqnamo.com/kitchen | index text only, no CSS | apdash `kitchen.md` (rebuilt from the RSC payload and the author's repo) |
| smoothui.dev | catalog (181 items) + registry JSON: expandable-navbar, expandable-cards, rich-popover, pinned-list, count-badge, content-skeleton | fetched source. There is no sidebar component on the site. |
| bencho.dev | JS app, only the page title came back | apdash `charts-amicro-bencho.md` |
| amicro.vercel.app | HTTP 429 twice | apdash `charts-amicro-bencho.md` (read from its MIT repo) |
| ui.aceternity.com | registry JSON: sidebar, expandable-card-demo-standard | fetched source |
| 21st.dev | sidebar listing only (68 items); source sits behind an API key | titles only; it re-hosts shadcn and aceternity originals (apdash says the same). No numbers taken. |

## 1. Per source

### dqnamo kitchen (via apdash)
ADOPT
- One curve, `cubic-bezier(.23,1,.32,1)` (= our `--ease`). Linear only for time-bound fills (undo countdown).
- Durations: 150 press and colour; content swap 180 in, 120-160 out; 200 indicators and borders; dialog 240 in,
  180 out. Exits run about 75% of their entry.
- Travel: 8 for a label in a clipped slot, 4 for panel content, `scale(.97)` dialogs, `scale(.95)` popovers from
  the trigger. Never more than 10.
- Nothing animates on mount. Changes made from the keyboard run at 0ms (`event.detail === 0`). Hover motion only
  under `(hover: hover) and (pointer: fine)`.
- Press `scale(.97)` (.98 wide controls); animate an inner layer so the hit area never moves. Focus ring 2, offset 2.
- Tooltip: 400 delay, 6 offset, no motion. Switch 16x28, thumb 150.
- Scroll-fade list: fade height = min(76, distance scrolled), painted in the surface colour, stopping short of
  the scrollbar gutter. Cap 32 on chip rows.
- Dynamic label button (Save, Saving, Saved): width 260, label slot ±8 over 180, check reverts after 1200.
  Fits settings saves, Copy link, Add word.

ADAPT
- Concentric radii (kitchen 6 controls, 8 buttons, 12-13 cards, 16 dialogs) become ours: 8 chips and inner
  fields, 10 buttons (fixed by the user), 12 cards, 16 dialogs and sheets.
- Kitchen's well holds a lighter surface. Ours is inverted: `--tile` card, `--tile-2` well for tracks, `--paper`
  for fields inside a card (ui.css:907 already does this).
- Tab and segmented indicator slides 200 (left and width transition, or CSS anchor positioning).
- UndoNotice: inverted wipe on the Undo button, linear 5000, paused on hover and focus.

REJECT
- 10px mono uppercase kickers (on our slop list), the button sheen gradient and four-layer button shadows (the
  `.pill` stays flat amber), every skeuomorph (receipt, cassette, ticket, foil, playing cards), scramble text,
  signature draw, logo-trace loader, the drop zone's pull, scale and glow.

### smoothui.dev (fetched source)
ADOPT
- expandable-navbar dismissal: Escape, pointerdown outside, focus leaving; 200 close delay. For kit.js menus,
  the user menu and the Quick sheet.
- pinned-list: groups split by one hairline `<li>` (`border-top: 1px`, 4 margin), no labelled header. Matches
  DIRECTION's sr-only "Study" / "Progress". Row padding 12, icon gap 12, title 14/500, meta 12.
- count-badge: 20 high, min-width 20, padding 0 4, values over 99 show `99+`, a changed value swaps with
  directional travel. Ours: the 17 rail count, `99+` cap, ±8 over 160, `--ink-deep` on orange (white on orange
  is 2.4:1).
- content-skeleton: `aria-busy` on the container, `aria-hidden` on the blocks, real children kept `invisible`
  underneath so nothing jumps when data lands. Add the reduced-motion stop it lacks.
- Accordion (via apdash): content stays mounted, height 0fr to 1fr over 200, chevron 180. For `details.fold`.

ADAPT
- expandable-navbar opens on hover. Ours: menus open on click; hover only shows metas (`.reveal`).
- rich-popover: 8 offset (keep 6-8); `rounded-2xl` 16 becomes 12; black surface becomes `--paper` with a
  hairline and the popover shadow; spring 500/30 becomes 150 `--ease` from `scale(.95)`.
- Springs with bounce .1 to .32 (pinned-list .3 over 400, count-badge .1 over 300): clamp to no bounce, i.e.
  `--ease` at the same duration.

REJECT
- expandable-cards (200 to 500 gallery, `blur(5px)` panel), every blur-in (rich-popover `blur(8px)`), the 17
  shader transitions, AI orbs, glass card, border beam, progressive blur, aurora, magnetic button, tilt card,
  scramble hover, typewriter, page preloader, dock, infinite slider.

### bencho.dev (via apdash; the site would not render)
ADOPT
- Digit roll for a figure that changes while on screen (score after a section, words learnt): one column per
  digit, 1.5em tall, edge mask, 220. Ours on `--ease`, no overshoot, no blur, never on load.
- Progress ticks: flex bars, gap 3, radius 2, off at 16% ink, on at full, height 320. Fits the Today minutes
  strip and the plan week.
- Its main curve `(.22,1,.36,1)` is ours within rounding: reuse `--ease`.

REJECT
- Overshoot curves `(.24,1.34,.38,1)`, the 2px blur on each digit change.

### amicro.vercel.app (via apdash; HTTP 429)
ADOPT
- Number first: figure 27-31 / 600 / -0.015em, unit beside it 12-13 muted, then a small delta. Title above at
  12.5-13 / 500. Range control top right.
- Chart chrome: horizontal gridlines only, 1px dashed `2 2`, three lines plus a baseline, 16% headroom; no axis
  line, no ticks; 4 y labels, 5 x labels.
- Marks: line 2.5 with round caps, comparison 1.5; dots r 3.5 with a 2px surface stroke; bars radius 4-6, 14-18 wide.
- Tooltip: 12 text, padding 8x12, radius 10, hairline, `0 6px 20px -6px rgb(0 0 0/.18)`, no blur. Crosshair 1px, 160.
- Range control: track radius 9, padding 3, gap 2; buttons 12 text, padding 5x12, radius 7; one sliding indicator.

ADAPT
- Axis labels 9.5-10 in `#A1A1AA` fail contrast: ours 11.5 (micro) in `--soft`, `tabular-nums`.

REJECT
- 24 card radius around an inset 14 "stage" (a card in a card), never-ending rAF dither canvases, glass
  tooltips, pulsing live dots, streak badges as decoration, card entrance from `scale(.98)` with blur on load.

### ui.aceternity.com (fetched source)
REJECT
- Sidebar: a 60 rail that grows to 300 on `mouseenter` and shrinks on `mouseleave`. It moves the target under
  the pointer and fires when the mouse passes by. Ours opens only on the toggle or `[`. Also reject its label
  `translate-x-1` hover nudge, its 300 easeInOut phone drawer, and the full-screen `p-10` drawer (we keep the
  phone bar plus five tabs).
- Expandable card: a row grows into a centred modal (`layoutId`), `bg-black/20` scrim, no focus trap, no
  `role=dialog`, close button hidden from `lg`, close icon unlabeled.
- Spotlight, beams, moving border, 3D cards, animated tooltip (stiffness 260, damping 10), animated modal
  (`rotateX 40` plus `blur(10px)`), text generate, multi-step loader.

ADOPT
- A collapsed rail hides labels with `display: none`, not opacity alone, so it has no invisible tab stops
  (`.side.rail` already does this for `.nextup` and `.side-meta`; keep it that way).

ADAPT
- "A row opens its detail" becomes: selecting a row fills `aside.split-side` on wide screens and a sheet on
  phones. Never a modal.

### 21st.dev (listing only)
- ADOPT (the slot, not the component): the 68 sidebars cluster around: a collapsible icon rail, search plus profile inside the sidebar, nav groups,
  settings sidebars, and "Sidebar News" (Dub.co): a small card pinned above the user row, the same slot
  DIRECTION gives the Now block. That confirms the slot; no numbers were taken.
- REJECT the gallery's house look: hero gradients, glow cards, 999px pills, uppercase badges.

## 2. Fonts (Latin plus Cyrillic)

Checked with fontTools on `geist@1.7.2`. The shipped `web/assets/fonts/Geist.woff2` is 69,652 bytes, the
package's unstripped variable file (Google's Geist build strips the stylistic sets).

| Face | Russian | Uz Cyrillic Ғ Қ Ҳ Ў | U+02BB ʻ | tnum | Sets as served | x-height | Verdict |
|---|---|---|---|---|---|---|---|
| Geist (self-hosted) | yes | yes | no | yes | ss01-ss11, case, frac | .530 | keep |
| Inter (Google) | yes | yes | yes | yes | stripped | .546 | reject: on apdash's reject list, the default AI look |
| Onest | yes | yes | yes | yes | none | .527 | runner-up if a warmer face is ever wanted |
| Golos Text | yes | yes | not checked | yes | none | .530 | no gain over Onest |
| Manrope | yes | no Ғ Қ Ҳ | not checked | yes | none | .540 | reject |
| Archivo (gone) | no | no | | | | | was the mid-line fallback bug |

- Geist also has `− – × π √ ≤ №`, so the bank typography (minus sign, en dash ranges, times sign) renders in one face.
- Gap: Geist has no U+02BB. The app writes Uzbek with ASCII `'` (412 `g'`, 173 `o'` in `web/assets/*.js`), which
  is fine. U+02BB appears in `web/results/page.js:120` ("Oʻzbekcha") and `server/progress_pdf.py`; that glyph
  falls back mid-word. Lead: use U+2019 or `'` in the web string; the PDF is server side, leave it.
- Geist Mono covers the same Cyrillic and has no ss05.
- Feature line: `html { font-feature-settings: "ss03", "ss05"; }` (tailed l, serifed I: "Ilhomjon", "Islom", Il
  in codes). ss08 (round dots) is taste, optional.
- Geist's x-height (.530) is lower than Inter's: body below 14 reads small, so keep body at 14.5.
- Russian labels often run 20-30% longer than English: nav, tabs, chips and buttons size to their content.

## 3. Shell, density, surfaces, disclosure, controls (synthesis)

- Sidebar width: sources 256-300; our 248 holds. Rows 32-36 across sources; DIRECTION's 34 holds.
- Rail: aceternity 60; ours 68 holds 44 items. 56 (44 plus 6 a side) would give main 12 back. Optional.
- Groups split by gap or hairline, no visible label (pinned-list). The Now block sits above the user row (Dub).
- Overflow in the sidebar nav gets the kitchen scroll fade, never a hidden scrollbar with a hard clip.
- Density: card padding 14-16 (amicro), list rows with hairlines, not cards (pinned-list's 8 gap between bordered
  rows is the airy version we are leaving).
- Surfaces: every source separates a card from the page by a hairline or a 2-6% micro-shadow (kitchen, amicro,
  freshweek). See flag 7 below.
- Disclosure ladder: hover or focus reveals metas (`.reveal`); a click opens a fold or fills the aside; a `?`
  tooltip after 400 for a definition; Help for how the UI works. Nothing a phone user must act on lives only in a
  tooltip.
- Controls: segmented track `--tile-2`, padding 3, gap 2, outer radius 10, inner 8; one sliding indicator over 200.

## 4. Rules for this app

1. Words are never uppercase; check: `text-transform: uppercase` in ui.css and runner.css only on `kbd` and print `thead` (from 45 to 3 or fewer).
2. `999px` / `50%` radius only on avatars, dots, radios and rail counts; check: grep `999px` lists no `.btn`, `.pill`, `.chip`, `.seg`, `.tab` selector (from 16).
3. No blur, glass or glow; check: grep `blur(` and `backdrop-filter` returns 0 outside print.
4. Gradients only for a chart area fill or a scroll-edge fade; check: every `gradient(` sits under `figure.chart` or a fade rule.
5. Font sizes come from the DIRECTION scale; check: distinct px sizes in ui.css 8 or fewer (from 35).
6. One curve: every `transition` uses `var(--ease)` (or `linear` for a timed fill) and a duration from {120, 150, 160, 180, 200, 240} (entries 160/200/240, exits 120/150/180, press 120); check: grep `transition` lines without `var(--ease)`.
7. Exits run at about 75% of their entry (dialog 240 in, 180 out; panel 200 in, 150 out); overlays opened from the keyboard open at 0ms.
8. Nothing animates on load; check: `animation:` only on `.skel`, spinners and toasts, and all of it stops under `prefers-reduced-motion`.
9. Every hover reveal has a `:focus-within` twin and is always on under `(pointer: coarse)`; it hides with opacity and visibility, never `display`, so nothing shifts.
10. Hover movement (translate, scale) only inside `@media (hover: hover) and (pointer: fine)`; press is `scale(.97)` on an inner layer or the button itself, never a moving hit area.
11. No card in a card; check: no `.card` inside `.card` in any page or template; inside a card, group with hairlines.
12. Shadows only on floating things (menu, popover, sheet, toast, dialog); check: every `box-shadow` with a blur radius belongs to one of them.
13. An orange fill carries `--ink-deep` text; check: each rule setting `background` to the orange token also sets `color: var(--ink-deep)`.
14. `details.fold` animates block-size over 200 (`::details-content`, `interpolate-size`), the chevron over 160; each new info-box class is in `FOLD_SEL`; errors and live status carry `data-nofold`.
15. Tooltips wait 400, sit 6 off the trigger, do not move, and open on focus and tap too.
16. Counts cap at `99+`; columns, clocks and counts use `tabular-nums`; a lone headline figure stays proportional.
17. An empty state is one line and one action; check: no empty-state block holds a second sentence.
18. Each fact shows once per viewport: streak, exam date, Up next and today's minutes live in the sidebar Now block or the Now strip, never both.
19. Text controls size to their content (Russian runs longer); check: no fixed `width` on `.pill`, `.btn`, tabs or nav labels.
20. Scroll edges fade instead of clipping: overflowing sidebar nav and chip rows get a surface-coloured fade of min(distance, 76 or 32).

## 5. Where the research contradicts or extends DIRECTION.md

1. §1: `.k` at 12px is off the scale it defines (meta 12.5, micro 11.5). Make it meta.
2. §1: control 14 next to body and item 14.5. A 0.5px step cannot be seen; kitchen uses one size for controls
   and titles. Merge to 14.5, or keep and say it is deliberate (the weight carries the difference).
3. §1: Geist Mono for clocks, codes, kbd and grid numbers. apdash's research skips mono: tabular Geist aligns
   clocks and grids, ss09 marks codes. Keep the 71 KB second face only for `kbd` and the test timer if Bluebook
   fidelity needs it; otherwise drop it.
4. §1: "figure 32 tabular". A lone figure reads better proportional (freshweek's `text-figure`); tabular is for
   columns and ticking values.
5. §1 has no feature line. Add `"ss03", "ss05"` on `html`.
6. §2: `.pill.sm` 34 beside `--ctl` 36. A row holding both misaligns by 2px. Set `.pill.sm` to 36 (the user's
   rule fixes only `.pill` at 42) or `--ctl` to 34.
7. §3: card = `--tile`, no border, no shadow. Measured: `--tile` on `--paper` is 1.10:1 (dark 1.11:1). Every
   source separates a card with a hairline or a 2-6% micro-shadow. Lead decides: keep borderless (calm, and it
   is what runs today) or give grids of cards the hairline (`.card.line` exists). Cannot be judged without a
   screen; the user reviews it.
8. §4: `.split` aside 300 from 1280 leaves main about 670-700 wide at 1280 with the 248 sidebar. Fine for
   lists; a page whose main holds a passage plus choices may want its own 1360 breakpoint.
9. §5: `.reveal` should also say "hide with opacity and visibility, never display" (rule 9).
10. §7 is missing: exits at about 75% of entry, dialog 240/180, popover 150 from `scale(.95)`, tooltip 400
    delay, keyboard-triggered changes at 0ms, hover motion only on fine pointers (it is in §5 but not §7).
11. Freshweek rules that do not carry over: orange is never a button (ours: orange is the primary `.pill`, per
    BRIEF), 999px buttons and chips (banned here), 30 page titles and 20x24 card padding (too airy for "cut
    whitespace"), navy as the action colour.
