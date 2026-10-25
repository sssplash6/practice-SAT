# Premium renovation: browse pass on DISCOVER section 3

2026-10-19, Playwright Chromium at 1440x900 and 390x844. Follows DISCOVER.md section 3 in order. Does not repeat
REFERENCES.md (Linear, Vercel, Raycast, Stripe, Arc). Shots: `premium/shots/discover-*.png` (35).
Provenance per pass: **[live]** measured in the page (getComputedStyle, CSSOM rules, getAnimations, real pointer
drags); **[frames]** a video sampled with requestVideoFrameCallback onto a canvas; **[img]** the source's own figure
(CDN file or PDF crop); **[text]** read only. "ours:" = adaptation to our tokens: `.pill` 42/10 (ui.css:855), `--ease`
`(.23,1,.32,1)` (:141), `--shadow-float` / `--shadow-pop` (:107-108), `--amber` #F18508 with `--ink-deep` text,
`UI.toast`, `UI.sheet` / `UI.menuSheet`, `.meter.ticks`. Button rule holds everywhere: 42px, 10px corners, max 48.

## 1. Duolingo design posts [img, text]
Loaded: core-tabs-redesign (13 figures; its web fonts never finished loading so page screenshots timed out, figures
saved from the Ghost CDN) and streak-milestone-design-animation (the passes GIF read frame by frame).
Shots: `discover-duolingo-before-inconsistent`, `-flat-lack-of-clarity`, `-quest-before-after`, `-feed-before-after`,
`-milestone-frames` (16 of 175 frames), `-share-card`.
Seen:
- Before: three tabs, three header sizes, three title positions, header art that "tells nothing".
- Four directions pushed to extremes: Punchy (solid headers), Soft (gradients), Modular (cards), Flat (white space).
  Flat was captioned "It's simplified, but is it clear?". Shipped a blend: consistency balanced with purpose,
  simplicity with clarity.
- Profile before/after: four bordered stat cards (value over label, "123 / Day streak") become a borderless 2x2 of
  glyph + value ("123 days", "1200 XP", "Sapphire"): the label is merged into the value. Section titles (20px bold
  "Overview") become small grey caps eyebrows ("OVERVIEW"). Two buttons (Add friends + share) become one; share moves
  to a header icon.
- Quest before/after: the card inside the card is removed; avatar columns ("You 270 XP / Emily 50 XP") become two
  rows of dot + name + right-aligned value; the deadline shrinks to a "2D" chip top right.
- Stated rules: tiered header sizes by tab purpose with titles always in the same place; "a minimal number of
  styles"; "whitespace around the components instead of forcing containers". Outcome: "higher engagement across tabs
  while maintaining core learning metrics" (no figure given).
- Milestone GIF: 175 frames x 40ms = 7.0s of rough-to-final passes. The counter flips from grey 364 to orange 365 at
  the moment the character transforms; the "day streak!" label never moves.
- Share card, two tiers: an ordinary day = white card, orange number, flame glyph; a milestone = orange card, big
  white number, the character. Same layout, the colour carries the rarity.
Use in SAT Freshman:
- Me page and the Today sidebar: drop the stat tiles for borderless glyph + value rows ("14 days", "620 estimate",
  "312 answered"), C8. Section heads as small caps eyebrows in the muted ink.
- Practice, Plan, Results: no card in a card; one container, rows inside, space between groups (C5).
- Streak extension (F1 tier 2): the old number in muted ink flips to the new one in `--amber-deep` while the flame
  fills, in one beat. Share card (F5): ordinary days on paper with an orange number; milestones on `--amber` with an
  `--ink-deep` number (orange takes dark text).

## 2. Brilliant [frames, live]
Loaded: Rive case study (text; its two YouTube embeds refuse to play outside the page, Error 153, so the watch page
was used); "streak endscreen flow 1" (27.7s) sampled every 1.7s; brilliant.org and /courses at 1440 and 390 (course
pages themselves need log-in).
Shots: `discover-brilliant-streak-flow-frames`, `-streak-screens`, `-courses-1440`, `-course-expanded-1440`,
`-courses-390`, `-adapts-1440`.
Measured:
- End-of-lesson flow: "Lesson complete!" with the points counting 0 (0.3s) to 115 (by 2.0s) under small sparkles;
  next screen a flame character over a black "0"; the flame flares and the number becomes an orange "1"; one bold line
  ("You're on a 1-day streak, can you make it to 3 days in a row?"); one full-width black Continue with small corners.
  Day one adds a 3-page explainer with a dot pager ("A streak counts how many days you've practiced in a row", "Miss a
  day and your streak resets to 0" with the number gone grey, "Your streak restarts the next day you solve three
  problems!") and "You earned 1 Streak Charge!" (their freeze). Every screen: one glyph, one number, one line, one
  button. Rive post: the streak animation "is aligned with the increasing number count".
- Home: 76px/500 serif H1; two 60px fully round CTAs, `0 4px 7px rgba(0,0,0,.05)`, transition 0s, hover fill
  `rgb(41,204,87)` to `rgb(21,180,65)` at once. Progress card: "94.5%" big with "▲ 2.3% From last week" small beside.
- /courses: no cards, no rules. Row = 80px illustration, eyebrow "GRADES 7-9" 10px/700 caps `rgba(0,0,0,.4)` +.48px
  tracking, title 20/700, "NEW" badge, chevron, one grey 16px line. Rows 176-200px apart, whitespace only.
- Expanded course: a light grey well (about r24) holding path tiles joined by a 2px connector. Tile (measured):
  150x150, white, r16, `2px solid #E5E5E5`, `box-shadow: 0 4px 0 0 #E5E5E5`, `transform: translateY(-4px)` at rest.
  Hover: border and ledge to `rgba(0,0,0,.3)`, no lift. Transform and shadow .1s ease-out, border and fill .2s ease.
  The expand itself jumps 0 to 294px in one frame (only an opacity .15s ease-in): a motion gap, not a model.
- 390: the topic row becomes icon tiles (selected = tinted fill + coloured border + underline) and the path becomes a
  vertical stack of full-width ledge cards joined by a centred 2px line.
Use in SAT Freshman:
- Session summary and streak moment (F1 tiers 1-2): one screen = one number + one sentence + `.pill.wide` Continue.
  The count rolls (N1) and the flame fills inside the same 600-900ms. No confetti, no character.
- Day-one streak explainer (3 short pages) and a named freeze; the freeze needs server work (P4).
- Practice skill list and Plan: the /courses list is the C3/C5 target (eyebrow + title + one line, no boxes).
- ours: a ledge for selectable tiles only (Tests paper tiles, Plan day tiles): `0 3px 0 0 var(--line)` with
  `translateY(-3px)` at rest, pressed to 0 in 100ms. Never on `.pill`. Their 60px round CTAs are banned here.

## 3. Bluebook quick start PDF [img]
Loaded: sat-suite-practice-quick-start-guide.pdf (2026-27, 6 pages); crops rendered with pdftoppm at 200-300 dpi
(the PDF's own screenshots are low-resolution rasters, readable but soft).
Shots: `discover-bluebook-test-window`, `-finished`, `-score-card`, `-knowledge-skills`.
Seen:
- Header: timer centred-left, red when low ("3:15" shown red); right cluster Calculator, Reference, More, each an icon
  over an 11px label. Below the header the dashed multi-colour rule (grey, black, yellow, blue dashes).
- Question bar: grey band; number in a black square; red bookmark + "Mark for Review"; at the right a blue square
  "ABC" struck icon, the Option Eliminator toggle (College Board's name; DISCOVER #7 called it Answer Strikeout).
- Choices: boxes with about 8px corners and a circled letter. An eliminated choice gets one line struck across the
  whole box, greyed text, and an underlined "Undo" at its right; live choices show a struck-letter button there.
- End: "You're All Finished!", one centred card with one line, one yellow "View Your Score" pill.
- Score card: TOTAL SCORE, "1410" very large, "400-1600" under it with a dotted underline; two section rows (name +
  "200-800" small, score right); yellow Score Details, outlined Khan button, one text link.
- Knowledge and Skills: per domain "(26% of test section, 12-14 questions)", a 7-segment bar, "Difficulty level".
Use in SAT Freshman:
- Test window `/test/`: match these states, no premium styling. Eliminated choice = full-row strike line (ours: 1.5px
  `--ink` rule, not text-decoration) + muted text + "Undo"; bookmark filled red when marked; timer red near the end
  (check our threshold against Bluebook); Option Eliminator as a toggle in the question bar.
- Results skill list: the segmented bar is our `.meter.ticks` (P2); "(26% of section, 12-14 questions)" as the muted
  second line. Score report: one big number with its range under it, two section rows, then one primary.

## 4. Comeau demos [live]
Loaded: /animation/3d-button (hero button measured, its :hover and :active rules read from the CSSOM) and
/css/designing-shadows (elevation slider set to 0, .5, 1; playgrounds read inside their same-origin iframes).
Shots: `discover-comeau-3d-button-rest`, `-3d-button-hover`, `-elevation-slider-1440`, `-hue-matched-shadow`.
Measured, 3D button (180x54, r12):
- Layers: shadow `rgba(0,0,0,.2)` at `translateY(3px)` (no blur in the hero); edge `linear-gradient(270deg, #660022 0,
  #A30036 7%, #A30036 93%, #660022)`, darker at both ends so the side reads curved; front `#ED003B`, 20/700 white,
  padding 12 42, `translateY(-4px)`.
- Hover: front -6px, shadow +4px, both 250ms `cubic-bezier(.3,.7,.4,1.5)` (overshoots); `filter: brightness(110%)`.
- Active: front -2px, shadow +1px, transition **25ms** (live CSS; the article text says 34ms).
- Release: back to rest over 600ms `cubic-bezier(.3,.7,.4,1)`. `outline-offset: 4px`; focus-visible = hover pose.
- Feel: hover rises 2px with a small bounce, press snaps down 4px at once, release floats back slowly. The asymmetry
  is the effect, not the layers.
Measured, shadows:
- Elevation slider: e=0 `0 0 0 rgba(0,0,0,.5)`, scale 1; e=.5 `4px 8px 8px rgba(0,0,0,.38)`, scale 1.05; e=1 `8px
  16px 16px rgba(0,0,0,.25)`, scale 1.1. So x = 8e, y = 16e, blur = y, alpha = .5 - .25e: higher is larger, softer,
  lighter.
- Stacks: small 1 layer `.5px 1px 1px` at .7; medium 3 layers `1 2 2, 2 4 4, 3 6 6` at .333; large 5 layers doubling
  to `16px 32px 32px` at .2; his neutral smooth stack is 5 layers at .075 (Ahlin's .12 is another source).
- Hue match on `hsl(220 100% 80%)`: black .5 = "Too grey", `hsl(220 100% 55%)` = "Too bright", `hsl(220 60% 50%)` =
  "Just right": the page hue, less saturation, less lightness, full opacity, 8px blur.
Use in SAT Freshman:
- `.pill` and `.btn`: take the asymmetry only. Press down in 25-80ms, release 200-300ms `cubic-bezier(.3,.7,.4,1)`;
  keep `scale(.97)`. No overshoot hover, no lift (0 of 6 premium primaries move on hover, REFERENCES section 2).
- Shadows: `--shadow-float` becomes the 3-layer medium shape at .10-.12, `--shadow-pop` the 5-layer large shape,
  offsets 1:2, warm tint from R6 `rgb(60 52 44)` (Comeau's rule applied to our paper lands near it).
- `UI.why` popovers with a tip: `filter: drop-shadow` so the tip carries the shadow (D3).

## 5. Emil: Sonner, Vaul, 7 tips [live]
Loaded: sonner.emilkowal.ski (3 toasts, stack and hover-expand measured, rules read); vaul.emilkowal.ski at 390
(opened, then dragged with real mouse events); /ui/7-practical-animation-tips (demos are live components; CSSOM read).
Shots: `discover-sonner-stack-1440`, `-sonner-expanded-1440`, `-vaul-open-390`, `-emil-blur-crossfade-1440`.
Sonner:
- Toaster bottom right, offset 24, width 356, gap 14. Toast r8, white, 1px `#EDEDED`, padding 16, 13px,
  `0 4px 12px rgba(0,0,0,.1)`.
- Stack: toast n behind the front = `translateY(-14n px) scale(1 - .05n)` (measured 0; -14, .95; -28, .9), height
  clamped to the front toast, and its content `opacity: 0`: back toasts are blank paper edges, only the front reads.
- Hover expands: toast n moves to `-(h + 14)n` (h 74: -87.7, -175.4), scale 1, content fades in.
- Enter from `translateY(100%)`, opacity 0. Transform, opacity, height .4s, shadow .2s, all default `ease`. Front
  removal: `translateY(-100%)` + fade; back removal: `translateY(40%)`, transform .5s, opacity .2s. Swipe-out 200ms
  ease-out. Reduced motion: `transition: none !important`.
Vaul (390x844):
- Drawer r10 on top corners, `#F4F4F5`, top edge at 34px; handle 48x6 fully round `#D4D4D8`, 16px from the top;
  overlay `rgba(0,0,0,.4)`. Open: `slideFromBottom` 500ms `cubic-bezier(.32,.72,0,1)`, overlay fades on the same curve.
- Page behind: wrapper `scale((vw - 26) / vw)` = .9333, `translateY(14px + safe-area-top)`, r8, on a black body.
- Drag: the drawer follows 1:1 with `transition: none` (20 to 20, 200 to 200). Overlay opacity = 1 - dy / 810 (.975,
  .901, .753); wrapper scale, radius and offset ease back by the same fraction. Over-drag upward is damped as
  `8 * (ln(dy + 1) - 2)` (60px gives 16.9, 100px gives 20.9). A slow release at 80px snaps back on the 500ms curve.
7 tips (CSSOM):
- Tooltip 125ms ease-out on transform + opacity from `scale(.97)`, exit 100ms, `[data-instant]` for neighbours,
  origin from the trigger. Radix tooltip 100ms from .95.
- Dropdown 180ms `(.25,.46,.45,.94)` from `scale(.95)`, exit 160ms, origin from the trigger. Popover 150ms ease-out
  from .9, exit 100ms. Ease-in vs ease-out dropdowns both 300ms (the ease-out one is `(.19,1,.22,1)`, close 275ms).
  "Better" side nav 600ms `(.23,1,.32,1)`: exactly our `--ease`.
- Blur crossfade scrubbed to 0.5: both icons at `opacity .5, scale(.9)`, the better one with `blur(1px)` (the article
  says 2px peak); press `scale(.97)`.
Use in SAT Freshman:
- `UI.toast` (F4): copy the stack: 14px step, 5% scale step, back content hidden, expand on hover, 400ms, pause on
  hover. ours: r10, `--line` hairline, `--shadow-float`.
- Phone sheets (`UI.sheet`, `UI.menuSheet`, Practice Start, Review "Start ▾"): 500ms `(.32,.72,0,1)`, 1:1 drag, log
  damping upward, overlay fading with distance (Ph2). Skip the page-scale effect (wants a black body).
- `.dd` menus and `UI.why`: 180ms quad-out from .95 at the trigger origin; tooltips 125ms from .97, neighbours
  instant (M3, M4). Both sit inside DIRECTION 7's two speeds.
- Label swaps (Check to Next, Save to Saved): opacity + scale .8 to 1 + 1-2px blur, about 200ms (B5, I3); the blur
  is **[call: D6]**.

## 6. Craft: Paco, Rauno, Family [live, text, frames]
Loaded: paco.me/craft/filter (the demo did not hydrate; behaviour read from its CSS and rendered by setting
`data-state`, with grey tokens injected for the missing variables); /craft/tabs (live, WAAPI read); rauno.me/craft/
interaction-design (text only, its videos never mounted); benji.org/family-values (02.mp4 trays 11.5s and 21.mp4 text
morph 4.1s, sampled).
Shots: `discover-paco-filters-stacked`, `-paco-exclusion-tabs`, `-family-trays-frames`, `-family-text-morph-frames`.
Measured:
- Spotify Filters: 36px chips, r36, 1px border, padding 0 16, gap 8. Selected = filled + darker border. Two selected
  neighbours merge: the second gets `margin-left: -16px; padding-left: 28px`, left corners 0, transparent left border,
  a lighter fill and sits under the first, so a run of picks reads as one segmented pill. 100ms on margin, padding,
  radius and colours. A multi-select merge, not the C4 "siblings slide away + x chip" (that is Spotify iOS itself).
- Exclusion Tabs: the tab list is duplicated in active colours (`#FF9F0A` fill, black text: our orange-with-dark-text
  case) on top of the plain one and clipped by `clip-path: inset(0 R 0 L round 32px)`; moving the clip moves the
  indicator. WAAPI 300ms `ease`. Text flips colour exactly at the indicator edge, even mid-letter.
- Rauno, new over DISCOVER: scroll landmarks (double-tap the scrollbar to drop a return point while reading long
  text); show what the finger covers above it (loupe, key preview); launch from the visible source (Dynamic Island
  vs app icon).
- Family trays: floating cards inset about 8px from the screen edge, large radius, title + close x, one job each;
  consecutive trays differ in height (Wallet Details 2 rows, Select Icon 5 rows, emoji grid tall) and the tray
  resizes in place between steps; the page behind dims grey; the picked item gets a 2px ring.
- Family text morph: "Continue" on the Send screen becomes "Confirm" with a Face ID glyph on the next screen, same
  button position, done between two samples 250ms apart; the "$1.00" flies between the screens as a shared element and
  flies home on Back.
Use in SAT Freshman:
- Practice Options panel: Paco's merge for the difficulty multi-select (Easy, Medium, Hard): picked neighbours fuse
  into one segmented control, 100ms. ours: 34px, r10.
- `.seg` and tablists: the clip-path duplicate (orange fill, `--ink-deep` text) at 200-300ms instead of a sliding bar
  (R13); text inverts exactly under the thumb.
- Practice Start on the phone and Plan day edit: trays with one job, different heights, resize in place (Ph1). ours:
  8px inset, r16.
- Session footer: Check becomes Next in place (B5); the summary score flying from the top bar (M8) only if cheap.
- Long R&W passages: scroll landmarks parked (novel, low need).

## 7. NumberFlow [live]
Loaded: number-flow.barvian.me; Shuffle clicked and the shadow-root animations read with getAnimations.
Shots: `discover-numberflow-hero-1440`, `-numberflow-midroll` (element mid-roll, edge masks visible),
`-numberflow-timings-1440`.
Measured (hero, 72px):
- 27 animations per change: digit spin (`--_number-flow-d` 2 to 0) and layout transforms 900ms; leaving characters
  fade 450ms ease-out; a width change slides with the same spring. Documented defaults: transform and spin 750ms,
  opacity 350ms ease-out.
- Easing: a 90-point `linear()` spring with no overshoot (max 1.0): .24 at 10% of the time, .56 at 20%, .77 at 30%,
  .95 at 50%, .99 at 70%. It looks finished at about half time and settles quietly.
- Masks `.25em` high, `.5em` wide; the site uses `line-height: .85`; `tabular-nums` advised. Trend default
  `sign(new - old)`: every digit rolls up on a rise; trend 0 rolls each digit its own way; `continuous` passes
  through the numbers in between.
Use in SAT Freshman (N1, R14):
- A vanilla roller: one column per digit, `translateY(-n lh)` on a no-overshoot `linear()` spring, about 600ms;
  leaving digits fade 250ms ease-out; masks .25em / .5em; `tabular-nums`; value in `aria-label`, digits hidden.
- Where: estimate on Today and Results (with the trend direction), streak count (with the flame), Words due, Compete
  points. On change after a student action only, never on load; off under reduced motion and `data-motion="reduce"`.

## 8. Galleries [live, mostly walled]
Loaded: mobbin.com/explore (marketing page; /screens/streak is a 404 without log-in), dribbble.com/search/quiz-result,
dribbble.com/Quizlet and its "Next Action Banners" shot, recent.design App Screenshots. Not reached: refero, lapa,
land-book (time; their content is marketing sites).
Shots: `discover-gallery-dribbble-quiz-result-1440`, `-quizlet-dribbble-1440`, `-quizlet-next-action-1440`,
`-recent-app-screens-1440`.
Seen:
- Dribbble "quiz result": purple gradients, percentage rings, glow cards. The template look to avoid. The calm one
  is a plain question list with outlined right and wrong choices.
- Quizlet (2017-2020 work): next-action banner = tiny caps eyebrow ("SET A GOAL") + one-sentence headline + one text
  link with an arrow + dismiss x + a spot illustration (we drop that).
- recent.design's own chrome is a calm C1 example: grey left nav, one chip row ("All" selected in black), one sort
  menu at the right ("Recent ▾"), then content. Its App Screenshots are store marketing, little use.
Use in SAT Freshman:
- Today "Up next" and `#banners`: Quizlet's anatomy minus the art: eyebrow, one sentence, one arrow link (R23), x.
- Tests and Words deck lists: one chip row + one sort menu at the right, nothing else above the list (C1, C2).

## Corrections to DISCOVER.md found by measuring
- B2 / #12: Comeau's live `:active` transition is 25ms, not 34ms. Rest front -4, hover -6, active -2.
- #17 / D1: Comeau's own smooth stack uses 5 layers at .075; the .12 figure is Ahlin's.
- C4 / #18: Paco's Spotify Filters merges adjacent selected chips; it does not collapse siblings or add an x chip.
- #7 / H1: College Board calls the strikeout tool "Option Eliminator".
- #14 / N1: NumberFlow's home demo runs 900ms (docs 750); the spring never overshoots.
- #8 / F4: Sonner uses the default `ease`, and back toasts hide their content.

## Ranked takeaways (for the suggestion list)
1. Remove containers, merge labels into values: Me and Today stats become borderless glyph + value rows, small caps
   eyebrows for heads, no card in a card (Duolingo before/after). [slop low]
2. One screen, one number, one sentence, one Continue for set end and streak extension; number and flame move in one
   600-900ms beat, grey old number to orange new (Brilliant, Duolingo 364 to 365). [slop low]
3. `UI.toast` = Sonner stack: 14px and 5% steps, back content hidden, expand on hover, 400ms ease. [slop low]
4. Phone sheets = Vaul physics: 500ms `(.32,.72,0,1)`, 1:1 drag, overlay 1 - dy/h, log damping up; no page scale.
   [slop low]
5. Rolling digits on a no-overshoot `linear()` spring, about 600ms, masks .25em / .5em, on change only. [slop low]
6. Asymmetric press on `.pill` and `.btn`: down in 25-80ms, release 200-300ms `(.3,.7,.4,1)`; no hover lift or
   overshoot. [slop low]
7. `.seg` and tab indicator by clip-path duplicate: orange fill with dark text revealed exactly under the thumb,
   200-300ms (Paco). [slop low]
8. Hue-matched layered shadows: 3 layers medium, 5 large, offsets 1:2, alpha falling as elevation rises, warm R6
   tint. [slop low]
9. Menus 180ms quad-out from .95 at the trigger origin; tooltips 125ms from .97, neighbours instant (Emil's CSS).
   [slop low]
10. Test window parity with Bluebook: full-row strike + Undo, red bookmark, red timer near the end; Results domains
    on `.meter.ticks` with "% of section, n questions". [slop low]
11. The list is the page: Practice skill picker and Tests as eyebrow + title + one line rows in whitespace, no boxes
    (Brilliant /courses). [slop low]
12. Today banners in Quizlet's anatomy without art: eyebrow, one sentence, one arrow link, dismiss. [slop low]
13. Difficulty multi-select as merging chips inside the Options panel, r10 not r36 (Paco). [slop med]
14. Ledge tiles (border + `0 3px 0 0` ledge, -3px at rest, pressed to 0) for selectable tiles only, never `.pill`
    (Brilliant). [slop med]
15. Phone trays with one job and different heights for Practice Start and Plan day edit (Family). [slop med]
16. Two-tier share card: ordinary day on paper with an orange number, milestones on orange with a dark number
    (Duolingo). [slop med]
17. Label morph Check to Next, Save to Saved: opacity + scale + 1px blur, about 200ms; blur is [call: D6]. [slop med]
18. Day-one streak explainer (3 pages) and a named freeze (Brilliant "Streak Charge"); freeze needs server work.
    [slop med]
19. Avoid: 60px round CTAs (Brilliant), gradient result screens with rings (Dribbble), the 3-layer 3D button on
    `.pill`, overshooting hovers, height jumps with no motion (Brilliant's expand). [slop high if copied]
