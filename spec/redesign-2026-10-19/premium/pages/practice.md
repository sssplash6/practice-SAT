# Premium audit: Practice (`web/practice/index.html`, `web/practice/builder.js`)

Case audited (the user's screenshot): a new student, Math, Mentor's pick on (3 skills), no set in progress, no answers yet
(so the Diagnostic link shows, builder.js:509), one or two Ready rows. Shell is not this page's, but its orange counts.
Figures below are derived from the code paths, not measured in a browser.

## 1. First screen inventory

**1440x900** (sidebar 248, main 728 + aside 300, ui.css:329). Rows of controls before the first skill row (about y 280):
1. Header: `Practice`, subject seg (2), points link if `bank.gains` (builder.js:232-238). `#route` adds a `.btn.sm` row when present (239-245).
2. Search box, 48px, animated orange edge (index.html:96-112).
3. Presets: 4 chips (Mentor's pick, Full section mix, Solve first · 10, Check 3 skills; +Plan focus, +Desmos drills when they
   qualify, builder.js:450-468, `later()` 476), then All presets, Options, Diagnostic (490-509).
4. Tree head: Domains, count, Skills/Map/Habits seg (3), Select all, Clear, Test order select (682-701).

| Visible before scroll | 1440 main | 1440 aside | 390 (visible band) |
|---|---|---|---|
| Orange primaries (`.pill`) | 0 | 1 (+ sidebar Up next `.pill.sm`, ui.js:1642) | 2 (Now strip Start, fixed bar Start) |
| Other buttons | 23 (19 skill-name buttons, All presets, Options, Select all, Clear, Your sets summary) | 4-5 (Ready fold, 1-2 Start, Saved, Your sets) | 10 (Now More, Ready fold + 2 Start, Saved, Your sets, All presets, Options, Select all, Clear) |
| Checkboxes (`.tri`) | 23 (4 domain, 19 skill) | 0 | 0 |
| Seg options | 5 | 0 | 5 |
| Chips | 4 (+2) | 0 | about 2.5 (row scrolls) |
| Links | 1-2 (Diagnostic, points) | 1 (Mistakes) | 2-3 |
| Inputs | 2 (search, sort) | 0 | 1 (sort cut off) |
| Boxes / cards | 5 (search, 4 domain cards) | 1 (Start card) | 3 (Now strip, search, fixed bar) |
| Bars | 23, all empty grey (builder.js:732, 753, 782) | 0 | 0 |
| Labels | about 27 (h1, h2, count, 4 domains, 19 skills) | 3-4 | about 8 |
| Helper lines | 1 (placeholder) | 3-4 (l2 wraps to 2, row meta) | 2-3 |
| Hairlines | 23 inside the cards | 2-3 | 2 |

Totals at 1440: about 65 targets, 23 checkboxes, 23 empty bars, 6 boxes and about 12 orange marks (search edge, search icon,
pressed chip, 2 seg thumbs, 3 checked tris, 2-3 mixed domain tris, Start, sidebar Start). With that much orange, nothing leads.

**390x844**: 844 minus pbar 56, tabs 64 and fixed bar about 60 leaves about 664px (about 630 with the home-indicator inset).
Stack: Now strip 44+16, header 44 (+20 points), Ready fold 44 + two rows about 112, links about 60, search 48, chip row 44,
All presets / Options / Diagnostic line 44, tree head wrapping to about 126. Tiles start about y 760 (about 600 with no Ready
rows), so **no skill is on the first phone screen**. The space is all controls, and there are two orange Starts.

## 2. Clutter fixes

**Hide behind one control**
- Presets row (chips + All presets + Options) becomes one trigger in the Your set card, reading the preset's name ("Mentor's
  pick", "Custom"). It opens `UI.menu` (builder.js:501 already uses it) with groups Suggested / From your history / Yours.
  Disabled presets show their reason as the item's `sub` line (no tooltip to hunt for), and Save as preset, Copy link, My defaults
  and rename/delete sit at its foot. Keep the id `#presetSec` on the trigger's wrapper (tour.js:30).
- Select all + Clear become a master `.tri` before the tree heading: three-state, `aria-checked` from the global count, its
  click calls `setSkill` on all then `markCustom(); paintSel(); preview()` exactly as 698-699 do. That is a zero-loss merge, which
  answers the pass's "Not done" reason (passes/practice.md:76). "Clear" shows as a quiet word beside the count only while 1+ is picked.
- Skills/Map/Habits seg + sort select become one `View` trigger (UI.dropdown with groups, kit.js:1230): Show (Skills, Map,
  Habits) and Sort (the 8 orders). It reads "Test order" in Skills view and "Map" or "Habits" otherwise. Keep `tip(view.btns[2])` (695) as the Habits item's sub line.

**Defer until relevant**
- Mastery bars: render `bar()` only when `answered > 0` (skill 782, domain 753). A new student sees names, not 23 grey tracks.
- Habits option: listed but disabled with "After about 30 answers" until `bank.habits` has rows (942).
- Diagnostic: drop the presets-row link (509). Show "New here? Diagnostic, 20 questions" as a quiet foot line in the Your set card
  when `totals.answered === 0` and no Ready row's href is `/diagnostic/`. Do not lean on `renderReady` for it: that hides the whole
  section when `ready` is empty (412) and for R&W (426), and those are exactly the cases a new student lands in.
- Search parsed-chip line: already empty until typing (113-114). Keep.

**Merge**: `l2` "3 skills · 24 types · ..." (1312) drops "3 skills": the card's glyph chips name them. The points line
(237) becomes the card's "works on ≈ +n" when skills carry gain, and stays a header meta link otherwise.

**Space to restore**: header to body 16 to 24 (index.html:26); search to tree 16 to 32 (27); domain groups 12 + borders to 28
with no border (155-156); aside sections 12 + hairline to 24 with no rule above the lists (58-61). Rows stay 40 (`--row-h`).

**Calm first screen, 1440, top to bottom**
1. y16: `Practice` left, subject seg right. Points as one meta line under the title (only with gains).
2. y76: the search, full main width, `/` kbd cap at its right end when empty. Nothing else on the row.
3. y156: tree head, one row: master tri, `Skills` h2, "3 of 19 selected · Clear" meta, `View: Test order` trigger at right.
4. y200: the tree, two columns, **no boxes**. Each domain is a heading row (tri, name 600, "+9 pts" and the orange open badge
   right) with one hairline under it, then its skill rows: tri, name, right-aligned badge, and a bar only if answered. No row
   dividers. Hover is a `--tile-2` band with 8px corners, and a picked row is a `--wash` band. Test order reading down each column, 28px between groups.
5. Your sets fold under the tree, unchanged.
6. Aside: the Your set card (the hero, section 3); 24px; Ready to start rows; 24px; the three lists as icon rows.
Result: about 30 targets (19 of them rows), 0 empty bars, 2 surfaces (search, hero), and orange only where it means "yours" or "go".

**Calm first screen, 390**: below 1280 the aside becomes `display: contents`, with `#banners { order: -1 }`, `.pr-main { order: 0 }`
and `#ready, #links { order: 1 }` (`#abar` stays fixed and its ResizeObserver still measures it, builder.js:1611). Stack: Now strip,
header, search (y200), tree head on one line (y272), 2x2 tiles by y 324 to 528, then Ready and lists. The fixed bar's left
half is the preset trigger over "10 questions · ~14 min", and Start practice sits on the right. Tiles are `--tile` fills with no border.

## 3. Depth and hero

Hero: **the Your set card** (`#abar` from 1280, index.html:75-79). It is the only elevated, tinted surface on the page.
- Surface: `--paper` card with a 1px `--line` ring, a warm corner tint `radial-gradient(120% 90% at 100% 0, var(--wash), transparent 60%)`,
  an inset top highlight `inset 0 1px 0 rgba(255,255,255,.7)`, and a shadow that fits the aside's 4px clip (ui.css:331-335):
  `0 1px 2px rgba(40,30,20,.06), 0 2px 4px -1px rgba(40,30,20,.07)`. Shared ask: raise `.twocol-side` padding/margin to 12px so an ambient
  `0 10px 24px -12px rgba(40,30,20,.18)` fits. Dark: card on `--tile`, `inset 0 1px 0 rgba(255,255,255,.05)` edge, no black shadow.
- Content: the preset trigger (head); the figure "10" at 28/600/-0.02em, tabular, with "questions · ~14 min" at 14.5 `--soft` on its
  baseline (today `l1` is 16px, 70); up to 3 `UI.chip` glyph chips (ui.js:697) + "+2"; Start practice full width; the meta line.
- No elevation for: domain groups, Ready rows, list rows, phone tiles (fill only), the search (its edge is its emphasis).
- Floating layers keep tokens: menus `--shadow-float`, sheets `--shadow-pop`. The phone's fixed bar adds `0 -8px 24px -16px
  rgba(30,30,30,.18)` over its top hairline (82), because it floats over the list as it scrolls.

## 4. Buttons, controls, highlights

| Control | Now | Should feel |
|---|---|---|
| Start practice `.pill` | hover 8% darker, press .97, disabled opacity .32, busy text "Building…" at .6 (ui.css:871-875, builder.js:1338) | Rest: inset top highlight + `inset 0 -1px 0 rgba(0,0,0,.12)` + 2px amber-tinted shadow. Hover: 1px lift, shadow to 4px. Press: .97 and the shadow collapses, 120ms. Disabled: `--tile-2` fill with `--soft` label (not a washed orange), reason under it in ink. Loading: width locked, label blurs to "Building" with a 14px ring. Error row (1348-1350) slides in 160ms. |
| Preset trigger (new) | chips with `aria-pressed` wash + amber inset | `.btn.dd`-style quiet trigger; open = `.btn[aria-expanded]` wash + amber (ui.css:904); current item has a check icon |
| `.tri` | 1.5px ink box, check appears instantly (index.html:147-151) | Rest 1.5px `--faint`, `--ink` on row hover; checked: fill scales .85 to 1 in 120ms, check draws by clip-path 140ms; mixed bar grows from centre; focus `--ring` |
| Skill row `.srow` | hover `--tile-2`, no transition (177); no picked state but the tri | 160ms background; picked = `--wash` band; the chevron (`.go`, hidden wide, 186) reveals on hover as the details cue |
| Subject seg / View | sliding paper thumb with amber ring (ui.css:2521-2530) | Thumb gets `0 1px 2px rgba(30,30,30,.08)`, a lifted iOS-style key |
| Search field | conic edge always turning, focus ring 3px amber 40% (103-112) | See section 5; `/` cap at rest; Escape clears (exists, 656) |
| List links (Mistakes, Saved, Your sets) | quiet text, underline hover (ui.css:931), count `.n` | Icon rows: 16px icon `--soft` to ink, hover band, count as `.badge.soft`, press .98 |
| Ready row Start | `.quiet` "Start" | Same, arrow icon nudges 2px on hover (fine pointer only) |
| Open-mistake `.badge.n` | orange count | Keep: it is a true "yours" mark |

## 5. Motion moments

All under 300ms, `--ease`, transform and opacity only, hover motion behind `(hover: hover) and (pointer: fine)`, reduced motion = opacity only.
- Bank loads (skeleton 1555-1560 to tree): 160ms opacity crossfade, no stagger (nothing animates on load for its own sake).
- Preset chosen: rows that become picked fill in tree order 20ms apart (cap 240ms), then the domain tris settle. Shows where the picks went.
- Domain tri clicked: its child tris fill top-down, 30ms apart.
- Set changes: the hero figure and "~14 min" swap with a 4px rise + 2px blur crossfade, 160ms; glyph chips enter .96 to 1 + fade 160ms, exit 120ms.
- Preset label changes to "Custom" (`markCustom`, 556): same blur crossfade on the trigger text.
- Start enables: fill eases 200ms, reason line fades out 120ms.
- Menus (preset, View): scale .96 to 1 from the trigger, 150ms in, 110ms out.
- Subject switch: tree area 120ms out / 200ms in; the seg thumb already slides.
- Ready fold: chevron rotates (34-36); content height via `::details-content` + `interpolate-size: allow-keywords` where supported, else instant.
- Typing in search: no motion (keyboard, high frequency). Rows hide instantly; parsed chips may fade in 120ms, 30ms apart.

## 6. Icons and imagery

- Search icon is a hand-made data-URI mask (index.html:99-101) while `UI.ICON.search` exists (ui.js:456, kit.js:187): reuse it.
- The 19 topic glyphs (`UI.glyph`, ui.js:687) never appear on Practice. Use them in the hero chips and in the skill window title (`openSkill`, builder.js:793).
  Keep tree rows text-only.
- Lists have no icons (252-255): `fix` (kit.js) for Mistakes, `bookmark` for Saved, `practice` for Your sets.
- View trigger: kit `filter` icon (kit.js:186). Preset trigger: chevron only.
- Unicode stand-ins: `∞` as a seg label (1116) should be a 1.6-stroke SVG with `aria-label="Endless"`. "Loading…" in `l1` and on Start
  (index.html:350, 355; builder.js:1324) should be a skeleton line and a disabled "Start practice". `≈` stays (it is math).
- Missing active states: no picked-row state, no current-preset mark once chips go, and wide rows hide the details chevron.
- Empty states that want a small `--faint` spot drawing above their one line: Habits (942), Your sets tabs (1460-1462), R&W bank
  coming (291-292), Map's intro for a new student (926).

## 7. Delight and feedback

1. The preset cascade: picking "Weakest 3" visibly lights three rows across the tree, so the student sees the choice, not just a label.
2. Glyph chips in the hero give the set an identity ("Circles, Percentages, Systems" drawn, not listed).
3. First pick from an empty selection: Start enables with one soft amber halo (ring 0 to 6px, fades in 600ms), once per visit.
4. The search sentence: parsed chips arrive one by one as the parser recognises "circles", "hard", "10", "15 min"; "Enter to start" stays (618).
5. Edits turn the trigger into "Custom" and the menu's first item into "Save as preset": a quiet nudge to keep what you built.
6. `/` cap in the search and the kbd hints already registered (1616-1618) make the page feel keyboard-native.

## 8. Ranked top 10

1. Tree without boxes: domain groups with one hairline, 28px apart, hover and picked bands. Why: removes 4 boxes and 23 lines, so the list reads as one calm column. M, slop low.
2. Bars only after answers (753, 782). Why: 23 empty placeholders vanish, and a bar now always means data. S, low.
3. Presets into one trigger on the Your set card (`UI.menu`, reasons as `sub`, Options at its foot, `#presetSec` kept). Why: one row of 7 equal-weight controls leaves. M, low.
4. Tree head on one line: master tri, count with contextual Clear, one View trigger. Why: 6 controls become 2. M, med (Map/Habits less visible).
5. Hero Your set card: corner tint, fitted shadow, 28px figure, glyph chips, tactile pill. Why: one place with depth and one focal point. M, med (shadow can go heavy).
6. Lighter `.tri` + picked-row `--wash` band + drawn check. Why: 19 ink boxes stop shouting, and the picks highlight themselves. S, low.
7. Phone order: aside `display: contents`, tiles before Ready and lists, preset trigger in the fixed bar. Why: skills on the first phone screen. M, low.
8. Diagnostic merged into the hero foot (answered === 0, not already in Ready). Why: up to three Diagnostic entries become one. S, low.
9. Motion set: preset cascade, figure blur-swap, menu scale-in, tri draw. Why: changes explain themselves. M, med.
10. Icons: `UI.ICON.search` reuse, list icons, SVG infinity, spot drawings for 4 empty states. Why: finished, consistent detail. S, low.
Rejected as high slop: spotlight or glow borders on domain groups, grain, glass on the aside, a second conic edge.

## For the user

- The search's orange edge turns forever (index.html:107). ui.css rule 10 says nothing loops, and it competes with Start. Calmer options:
  turn once on arrival and on hover/focus only, or keep it looping at 8s with its bright arc at 35% (now 4.5s, 100%). Your call, kept as is until then.
- Presets move from a visible chip row (round 2's choice) to one trigger in the Your set card. OK?

## Shared asks

- `.twocol-side` padding/margin 4px to 12px, so the hero's ambient shadow is not clipped (ui.css:334).
- tour.js:30 text: "Ready-made sets. Open this to pick one, or save your own."
- Now strip Start is a `.pill` (ui.css:786): a second orange primary on the phone. `.btn.sm` on pages that carry their own Start.
