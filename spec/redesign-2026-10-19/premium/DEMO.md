# Live demo: /dev/premium.html

`web/dev/premium.html` (styles, all proposals scoped under `.pro`) and `web/dev/premium.js` (specimens, motion).
Open http://127.0.0.1:8071/dev/premium.html. Every card has its ID, a Current | Proposed switch (Proposed by
default; Current is ui.css and the shipped kit exactly as they are) and a Replay button where motion is involved. The
header switches Dark (`html[data-theme]`) and Reduce motion (`html[data-motion="reduce"]`); `?theme=dark` also works.
No other file changed. Point at a specimen as "see A3".

## A. Buttons
- **A1** `.pill` rest, hover, press, focus, loading (spinner after 300ms), success (drawn check), disabled, plus a live one. REFERENCES R1, R11; MOTION C1, C3.
- **A2** Full and lite orange pill side by side, 42px and `.sm`, in a light and a dark panel. REFERENCES R1 (full), R1b (lite).
- **A3** `.pill.sm` states and in Up next rows. REFERENCES R1 at 34px; pages/today.md 3.
- **A4** `.btn` states (white face, BUILD 10), pressed, `.ink`, disabled, and on a card. REFERENCES R2 (Kitchen trigger, Vercel secondary, Kitchen dark stack for `.ink`).
- **A5** `.quiet` with the underline fading in amber, and the Stripe hover arrow on links that go somewhere. REFERENCES R3, R23.
- **A6** Icon buttons: hover fill, press .94, "on" as a raised key, bookmark outline to amber fill swap. MOTION C1, C2; DISCOVER I3; ICONS.md 5.
- **A7** Segmented control: lifted paper thumb with the amber ring on a recessed track, sliding on the soft spring. REFERENCES R12, R22; MOTION C6.
- **A8** Tabs: underline sliding on the soft spring. REFERENCES R13; MOTION C5.

## B. Depth
- **B1** The warm elevation scale e0 to e4, light and dark panels. REFERENCES R4, R6; DISCOVER K1.
- **B2** A card at rest (alpha ring, inner highlight, soft warm shadow) and a clickable card (e1 to e2, 1px lift max). REFERENCES R4, R5, R9; DISCOVER D2.
- **B3** Today: Up next as the one raised hero (featured lead, 42px Start with play glyph, corner wash, top sheen). pages/today.md 3; REFERENCES R7.
- **B4** Practice: the Your set card (preset trigger, 28px figure, topic glyph chips, Diagnostic foot line). pages/practice.md 3.
- **B5** Practice: a raised question sheet over a warm tile, raised option keys, pick with amber edge and wash halo. pages/runner.md 3.

## C. Highlights and states
- **C1** Selected chips: raised rest, press, 140 fill; count turns ink. MOTION C8; REFERENCES R2.
- **C2** Current nav item: one wash band (no side stripe) slides between items, 260 ease-move. MOTION N2.
- **C3** Row hover band, picked row, your row (leaderboard). pages/practice.md 2; DISCOVER H3.
- **C4** Focus: a thin amber-deep ring 2px out on controls; links get an amber-deep underline on a faint wash, no box; a white field whose edge turns amber-deep. REFERENCES R11, R22.
- **C5** Highlight (`mark`), search hit, text selection colour on a passage. DISCOVER H4.
- **C6** New dot that pings once, count badge with the pill's edge, outlined "New" badge. REFERENCES 1.1 (statusPulse), R19, R1b.

## D. Motion
- **D1** Page entry stagger: 8px rise, 200 ease, 30ms steps, capped at 6, primary never delayed. MOTION M1; REFERENCES R15.
- **D2** List row added and removed with FLIP. MOTION L1, L2; REFERENCES R16.
- **D3** Sheet open and close (desktop 260/180; phone spring 370 up, 200 down), surface e4. MOTION S1, S2; REFERENCES R17.
- **D4** Menu scaling in from its trigger corner (down-left and up-right), 100ms fade out, 80ms pick flash. MOTION S3, S4; DISCOVER H2, M3.
- **D5** Toast stack (Geist offsets), fan-out on hover or focus, enter and exit, Undo countdown line. REFERENCES R18; MOTION S6.
- **D6** Digit roll on a score and its band: only changed digits, direction-aware, spring 370. REFERENCES R14; MOTION D1; DISCOVER N1.
- **D7** Tick meter lighting left to right, and the R21 progress fill grown by clip-path. MOTION D3; REFERENCES R21.
- **D8** Task done: drawn check, drawn strike-through, one done pulse. MOTION C9; REFERENCES R19; pages/today.md 7.
- **D9** Practice right-answer stamp (pop on the letter disc, verdict rise, drawn check, segment fill) and the wrong-answer moment (dim and drawn strike). MOTION F1, F2, F11; pages/runner.md 7.
- **D10** Goal ring sweeping closed (registered property), then one beat, drawn check, "Goal met". MOTION D4, F6.
- **D11** Streak extended: number rolls, flame outline to filled amber with a pop. MOTION F5; DISCOVER F1.
- **D12** Skeleton only after 300ms, then the content fades in over it. DISCOVER E2; MOTION M2.

## E. Calm layout
- **E1** Practice first screen as it is (four control bands, boxed domains, empty bars) and calm (search alone, one tree-head line, plain groups, bars only with data, presets behind the Your set trigger). pages/practice.md 2; DISCOVER 2.0 C1 to C7.
- **E2** Today first screen as it is (fold rows, four aside cards) and calm (lifted Up next with featured lead, one footer line, the aside as the Today block plus five one-line rows). pages/today.md 2, 3.

## F. Icons
- **F1** The nine nav icons: current set vs Phosphor regular at a held 1.4px stroke, filled twin on the current item (150ms crossfade). ICONS.md 2, 4, 5.
- **F2** Inline marks ✓ ✕ ⋯ ▾ ⓘ ‹ › in the fallback font vs drawn Phosphor outlines, in context and side by side. ICONS.md 1a, 6.
- **F3** Status cells with drawn corner glyphs (correct, incorrect, skipped) as masks in `--st-mark`. ICONS.md 6 (no-font fallback).
- **F4** Spot drawings from the logo's four corners: start, clear, lost, done (Replay). ICONS.md 9.

## Notes for the reader
- Reduce motion: JS-driven moments (rolls, stagger, sheet, menus, toasts) become 120ms fades or jump to the end state,
  as MOTION 2 says. CSS transitions inside the page still collapse to the shipped ui.css `.01ms` rule, which the
  MOTION plan replaces with token-based durations; that difference is the plan's, not the demo's.
- Not shown: the spotlight border (R24, slop risk medium to high), texture (R8), shimmer skeletons (R20, ui.css rules 8
  and 10), view transitions between pages (N1, N3 to N5) and the sidebar rail morph (MOTION 3.8), which need real pages.

## Visual review

Two rounds of screenshots at 1440 (light and dark) and 390, with hover, Tab focus, presses, Current/Proposed flips and
motion sampled mid-flight (animations paused at 110 to 140ms). Shots: `premium/shots/demo-review/` (`r0-*` before,
`r1-*` round 1, `r2-*` round 2). Only `web/dev/premium.html`, `premium.js` and this file changed; Current still draws
from ui.css (its forced hover, press, focus and disabled copies now read the shipped tokens, so they track ui.css).

### Page chrome
- White canvas (near black in dark); each specimen is now a heading, one line of sources and one stage in the app's
  own `--page` colour. The old specimen card, its hairline and the boxes nested inside it are gone, so a card in a
  stage sits on what it sits on in the app.
- IDs are plain mono text in `--soft` (was a dark ink chip that shouted in both themes).
- Current | Proposed is a small neutral two-way switch (26px, white thumb, no amber ring); Replay is a 30px icon button
  beside it. The orange on screen is the specimen's own.
- More air: 80px between groups, 64px between specimens, 28px stage padding; shorter intro; titles no longer squeeze
  into three lines (D8 and D9 titles shortened).
- A2 and B1 show light and dark as two halves of one stage (no panel boxes inside a card).

### Per specimen
- **A1** Focus is the thin amber-deep ring; disabled is one flat tint (same as `.btn`).
- **A2** Light and dark halves of one stage.
- **A3** Focus ring as A1.
- **A4** Proposed `.btn` gets the white face (BUILD 10) explicitly, with a warm hover step; `.ink` and disabled kept
  their own fills (they were being overwritten); the duplicate Options dropped so Skip no longer wraps alone.
- **A5** Good as was.
- **A6** Focus ring as A1 (was an ink box shadow).
- **A7** Good as was.
- **A8** Good as was.
- **B1** Five levels in one row per theme (e4 was orphaned on a second row); panels in the page colour.
- **B2** The resting card is white like the clickable one (it showed tile grey next to a white card).
- **B3** Good as was.
- **B4** Two topic chips and "+3" (the "+2" chip wrapped alone).
- **B5** Good as was.
- **C1** Chips at rest wear the `.btn` face; picked keeps wash-2 and the amber ring; focus as A1.
- **C2** The 3px amber bar is gone: one wash band slides. Current also shows its wash again (a demo reset hid it).
- **C3** Picked is wash-2, yours the lighter wash in 600 with an amber-deep rank, no stripe, no check; rows take
  the focus ring inside; clicking a row focuses it, so arrow keys work.
- **C4** Thin amber-deep ring 2px out, following corners, never ink; the static link sample (a span) now also gets
  the no-box treatment; fields are white with a fine edge (the grey well read as disabled), focused edge amber-deep
  with a soft halo. The two fields stack instead of squeezing.
- **C5** Good as was.
- **C6** Good as was (the title no longer wraps).
- **D1** Good: primary at full opacity by 110ms, later blocks stepping in.
- **D2** The list sits in one card (rows floated as white strips with no top or bottom edge).
- **D3** Good as was.
- **D4** Fixed a bug: the preset menu rendered as raw grey native buttons (the CSS matched `menuitem`, not
  `menuitemradio`).
- **D5** No inner box around the toast area; a faint "Toasts stack here" until the first toast; the Undo countdown
  line is graphite, so Undo's underline is the only orange in the toast.
- **D6, D7, D8, D10, D11, D12** Good as were.
- **D9** Good; title shortened.
- **E1** Calm: open-mistake counts are neutral badges (orange counts competed with the checks and Start); the Your set
  card shows two chips and "+1" instead of three stacked chips; the search field is white.
- **E2** Good as was.
- **F1** The current item shows its wash band again (a demo reset hid it); text says the wash band, not a bar.
- **F2, F3** Good as were.
- **F4** Outlines drawn in `--faint` (in `--line` they nearly vanished on the page colour).

### Lessons for the build
Do:
- Focus: one thin amber-deep ring 2px out that follows the control's corners (outline, so the gap is transparent);
  inside rows and list items, inset it. Never ink, never thicker than 2px.
- Links: on focus the underline turns amber-deep at 2px on a faint wash; no ring, no box.
- Fields: white with a fine edge; focused, the edge turns amber-deep with a soft halo. A grey well reads as disabled.
- Rows: selected and "yours" are full-width bands (wash-2 for picked, wash for yours) with weight; no side stripes,
  no trailing check, no hairlines between banded rows.
- Nav: the current item is the wash band and 600, nothing else.
- Buttons and chips share one white face; set the fill explicitly on every variant (`.ink`, disabled, pressed) so a
  later rule cannot whiten them.
- Disabled is one flat tint for `.pill` and `.btn`.
- Badges: counts that are not alerts are neutral; keep orange for the one thing to do and for selection.
- Lists live in one card; never leave white rows floating on the page.
- Count the oranges per card or screen: the primary, the selection, nothing decorative (countdown lines, counts and
  dividers stay graphite).

Don't:
- Box a card inside a card, or a panel inside a stage; use the page colour as the ground and one surface on it.
- Put a dark or loud ID chip, label or tab next to content; chrome stays quieter than what it frames.
- Let a title, chip or button wrap one word or one item onto a line of its own; shorten or drop an item instead.
- Draw spot illustrations in `--line`; it disappears on the warm page.
- Reset `background` on a shared class in page CSS without `:where()`; it silently kills states like the nav wash.
