# Premium audit: Plan (web/plan/**, web/assets/plan-ui.js)

Code-level only. States read: plan view (Plan, Progress, Plans tabs), landing, wizard steps 1 to 4, the new Shape sheet
(plan-ui.js:344-426 weekPlanner, plan.js:1370-1388 openShape), print and test-day sheet. Figures are estimates from the CSS.

## 1. First screen inventory

**Plan tab, 1440x900** (mid-plan weekday, 3 tasks, first one started, no banner). Visible: title row, settings line, the
whole Day card (plan.js:730-816), the calendar card's head, Tasks meter, theme line and about 2.5 rows of the month
(plan.js:1323-1361, 1467-1485); aside: the whole status card (plan.js:412-514) and Coming up (plan.js:1390-1411).
- Buttons ~27: tabs 3, plan menu, day menu, Start, "Today I have 45 min ▾", 3 round checkboxes, 2 row Starts, 3 row menus,
  Shape this week, week ‹ ›, month ‹ › (charts.js:1225-1226), 3 hidden tile taps, What changes it, 3 Coming up rows.
  Plus ~17 calendar day cells.
- Links 1-2 (Edit, "Register by ..."). Chips 2-3 (topic chips on the next task, plan-ui.js:165). Inputs 0.
- Boxes 4 cards, 4 hairline tiles in the status card, ~17 hairline-boxed day cells (ui.css:1767).
- Bars 5 (day meter, score track, Plan done meter, This week ticks, the week's Tasks ticks plan.js:1347), a 3px task bar
  in every past day cell (index.html:129-130), 5 day dots.
- Labels: h1, 4 h2, 4 stat-k, 3-4 tag badges, 1 pace badge. Helper or meta lines ~20 (8 of them in the status card).
- Rows of controls before the first task: (1) tabs + Edit + menu (plan.js:362), (2) banner actions + "N more" when a
  banner shows (plan.js:613), (3) the day menu (plan.js:755), (4) Start + Today I have (plan.js:763-774).
Start is high (~150px); the noise is around it: two navs, two tick meters, four menus in grey squares, eight status lines.

**Plan tab, 390x844.** Name row (Edit, menu), settings line, sticky tabs 3, day head on two lines + menu, Start, then
"Today I have" on its own row (label ~230px + ~160px > 358, plan.js:773), then 1.5 task rows of 3-4 lines each (detail
always on coarse pointers, plan-ui.js:83; actions drop to their own line, plan-ui.js:115). Buttons ~13, links 1, chips 2-3,
cards 1, helper lines ~7. Rows of controls before content: 5 (6 with a banner).

**Wizard step 2, 1440x900** (the busiest step). Title + Exit, stepper 4, target slider + number field, 7 quick-target
chips (wizard.js:404-406), gain box (2 figures, badge, track, wizard.js:417-422), Add an R&W target, 4 date cards with two
lines and a badge (wizard.js:436-437), Later dates, Other date input, booked checkbox, pace line + badge. Glance: "Live plan",
compact month (2 nav + ~30 cells), "Week 1" + 7-tile strip, "Day 1" + 5 numbered rows with badges, up to 13 dl rows
(wizard.js:211-266). Foot: Back, Draft saved, the shortcut hint, Next. Totals: buttons ~22 + 30 cells, chips 7, inputs 4,
boxes ~16, bars 2, labels ~10, helper lines ~18. The Glance alone runs ~750px and scrolls inside itself (index.html:230).
The screenshot's uppercase mono labels ("WEEK 1", "DAY 1 · ...", "NOW", "TARGET" and every `.meta`) are the committed
`.k` (10.5 mono, .14em, uppercase) and `.meta` (13 mono). The working tree already has them in sentence-case Geist 12.5
(ui.css:843, 845): fixed once this tree ships, no plan change needed. The busy column is still real (section 2).

**Shape sheet** (both widths). 7 rows, each a date, its focus topics, a ±15 select, Busy and Short toggles
(plan-ui.js:363-369): up to 21 controls, plus 2 swap selects and an arrow (plan-ui.js:382), plus Save. On a phone every row
wraps to two lines (plan-ui.js:136-139). Nothing says what Busy (a day off, its focus moves on) or Short (15 min) do, and
the week's total before and after is not shown.

## 2. Clutter fixes

- Day card, one action row: Start stands alone. "Today I have 45 min ▾" (plan.js:818-827) becomes the minutes word in the
  facts line ("Practice · Build · **45 min**", dotted underline, opens the same menu), so its menu stays one tap away.
  Start says "Start · 40 min left" (task count is in the rows; plan.js:769 restates both).
- Task rows: on fine pointers the non-next rows' Start and menu are `.reveal` (show on row hover or focus, always on touch,
  ui.css:341). The tag badge (plan-ui.js:238) folds into the meta line as its first word ("Focus · 10 questions · 15 min").
- Menu buttons: the five ⋯ are filled `.btn.sm.icon` squares on `--well`; make them ghost (`.ibtn` look) so they read as
  marks, not buttons.
- Calendar card, one nav: the week ‹ › already moves the month (charts.js:1368 select goes to the month), so the month's
  own ‹ › and Today jump hide inside `.pl .cal.plan` (title stays). Shape this week and This week stay in the head.
- Calendar cells unboxed: drop the hairline on plain future days (ui.css:1767); only today, the selected day, test days, the
  exam and the week on show keep a shape. Drop the per-cell task bar and "2/3" (index.html:129-130): the cell's mark
  already says done, partial, missed; the counts stay in the picked day's card and the cell's label.
- Legend (up to 10 swatches, charts.js:1311) goes behind a `?` (UI.why) beside the month title.
- One week meter: the calendar head's Tasks ticks (plan.js:1345-1349) show only when the week on show is not this week;
  this week's figure is the status card's This week.
- Status card: each tile is figure + one line. Score keeps the track and the pace badge; "At this pace", "Making +8 a week ·
  needs +12", the R&W line and What changes it (plan.js:463-479) move into a popover the tile opens. Days to exam keeps
  "to Nov 7 · 24 study days"; fits, short-by and register sit in the same popover unless short or unbooked (then one line).
- Aside: Map, Habits and Sweep (plan.js:666) become one "This phase" card with hairline groups (only the ones that apply).
- Wizard Glance: a figure line ("62 study days · 48 h · to Nov 7"), the month, then the 3-4 rows the current step changes;
  Week 1 and Day 1 behind a two-way seg under the month (one shows); the other dl rows fold under "All settings (9)".
- Wizard step 2: quick targets go from 7 chips to 3 (+50, +100, 700) set as tappable ticks under the slider; the gain box is
  the step's hero (section 3), so the Glance's Score row hides on steps 1-2.
- Wizard step 3: per-day minutes and the rhythm line under each day tile (wizard.js:494-502) defer behind "Different times
  on some days" (open when any day differs); a tile is then one tap target.
- Wizard step 4: a Math | Reading and Writing seg shows one section at a time; Where your points are shows top 3 + "3 more".
- Shape sheet: one seg per day replaces select + Busy + Short: [Busy · 15 min · 30 · 45 · 60] around the day's own minutes
  (same values the three controls give). A one-line key under the title: "Busy moves the day's focus to the next study day".
- Space: 24px between the Day card and the calendar on desktop (gap is 12, ui.css `--card-gap`), 16px between aside cards.

**Calm first screen, top to bottom (1440):** title row (name, tabs, Edit, ghost menu); settings line; one banner if any;
the Day card raised on paper (date, facts with the minutes trigger, Start alone, three quiet rows); 24px; the calendar
card (week head with one nav, the month with unboxed days). Aside: status card (four figures, one line each), Coming up.

## 3. Depth and hero

- Hero moment: the Day card. Paper surface (not `--tile`), 14px radius, a warm two-layer shadow
  (`0 1px 0 var(--line), 0 12px 32px -16px rgba(80,50,10,.22)`), no hairline. Every other card stays flat tile + hairline,
  so depth itself marks "now". Inside it, a thin amber top edge (2px, 40% width, left) on today only, not on other days.
- Start pill: the only raised control: `inset 0 1px 0 rgba(255,255,255,.3), 0 1px 2px rgba(120,60,0,.25)`, pressed
  flattens (shadow off, scale .97). The `kbd` Shift+Enter shows inside it on fine pointers (aria-keyshortcuts exists).
- Calendar: the selected day lifts (paper, `--shadow-float`, the amber ring) over unboxed days; the exam cell stays the
  one amber fill. Today keeps its ink ring.
- Status card: no elevation; figures at 28 carry it. Coming up: rows on paper, no card (spacing separates it).
- Wizard: the Glance is the one raised surface (paper + the warm shadow, sticky), the live preview. Step 2's gain box
  becomes the step hero: "560 → 650" at hero 44/600 with the target in `--amber-deep`, the badge "+90" beside.
- Shape sheet: a 7-bar week chart heads the sheet (bar height = minutes, Busy days a hatched stub), the sheet's one visual.
- Sticky bars (`.pl-thumb` index.html:189, `.wz-foot` index.html:348): translucent paper + `backdrop-filter: blur(12px)`
  and a soft upward shadow instead of the hairline: content slides under them.

## 4. Buttons, controls, highlights

| Control | Now | Should feel |
| --- | --- | --- |
| Start `.pill` (plan.js:770) | hover 8% darker, press .97, busy opacity .6 | raised edge, press flattens; busy: label crossfades to "Starting" with a 14px spinner, width held (UI.saving shape) |
| Task checkbox `.trow-box` (plan-ui.js:66) | 28px ring, no hover, instant fill | hover ring goes ink; tick: fill 160ms, check strokes in (dashoffset 200ms), 0.92 to 1 settle; untick reverses |
| Task row | no hover | fine pointer: 3% ink wash, 8px corners, -8px inline; next row keeps the amber left bar (plan-ui.js:88) |
| Row and day menus ⋯ | filled 34px squares | ghost until hover (well fill on hover, 120ms), pressed = well fill |
| Week ‹ › (plan.js:1331) | text glyphs in filled squares | ghost chevron icons; disabled at the plan's edges fades to `--faint` |
| Today I have ▾ (plan.js:824) | `.btn` with a text ▾ | the dotted minutes word in the facts line, chevron svg that turns on open |
| Status tile tap (index.html:84-86) | 4% hover, no press | press darkens 6%; focus ring stays inset ink |
| Wizard radio cards `.wz-choice` `.wz-date` (index.html:237-248) | wash + amber ring when on, no hover | hover 4% darker, press .98, on adds a check glyph top right (not colour alone) |
| Wizard day tiles `.wz-wd` (index.html:296-300) | wash when on, shake on last day | press .97; Study/Rest label crossfades; shake kept |
| Stepper (index.html:220-227) | 2px bars switch instantly | one amber bar slides to the current step (like `.tab-ind`); done steps get the check svg |
| Next / Create plan (wizard.js:157) | aria-busy only | Create: "Creating" with spinner, then the plan view lands (section 5) |
| Shape Save (plan.js:1379) | busy then sheet closes, toast | UI.saving in the sheet's button: Saving, Saved ✓ (600ms), then close; the week's cells pulse once |
| Banner actions (plan.js:577) | `.btn.sm.ink` | unchanged; banner gets a 3px amber left rule instead of a full wash when it is a nudge, wash only for "missed" |
| Focus | ink outlines everywhere | keep; Coming up rows (index.html:140) get the inset 2px ring `.pl-wkr` already has (index.html:170) |

## 5. Motion moments

- Load: skeleton to content crossfades 160ms (plan.js:78-98 swaps hard). No stagger on a normal load.
- Picking a day (calendar, week rows, arrows): the Day card's body crossfades and slides 8px in the time direction
  (later from the right), 200ms `--ease`; replaces the 1.1s amber blink `.pl-flash` (index.html:430-433, plan.js:723),
  which breaks DIRECTION's 300ms rule. Keyboard day stepping (ArrowLeft/Right) gets no slide, crossfade only.
- Selected cell: background and ring transition 160ms; the week-on-show ring (index.html:124) fades between weeks.
- Task tick: checkbox (section 4), day meter fills (ui.css:1272 has the transition), status figures roll with UI.roll
  (kit.js:1639): Plan done %, This week minutes, streak. Skipped or moved rows fade to .55 over 200ms (plan-ui.js:74 is instant).
- Banners: `.banner { animation: rise }` (ui.css:2286) replays on every redraw because drawBanners rebuilds them after each
  patch (plan.js:613). Animate only a banner key not shown before.
- Wizard: step change slides the body 12px in the step's direction with a crossfade, 200ms; the stepper bar slides. Glance
  rows that a change touched get a wash that fades over 600ms (wizard.js:229, 237 does this for week tiles only).
- Create plan: after the wizard's onDone (plan.js:125-136) run the same month fade-in stagger useProposal has
  (plan.js:269-270), by week rows at 30ms, and the Day card rises 8px. One shared function for both paths.
- Shape sheet: changing a day's seg morphs its bar height (transform scaleY, 200ms) and rolls the week total.
- Phases chevron already turns (index.html:156-158). Reduced motion: crossfades only, no slides, no rolls.

## 6. Icons and imagery

- Text glyphs to the shared ICON set (ui.js:438): ‹ › week and month nav (plan.js:1331-1332, charts.js:1225-1226) to `chev`;
  ▾ ▴ (plan.js:824, index.html:254-255, wizard.js:670) to `chev` rotated; × remove (wizard.js:570, 756) to `x`; stepper ✓
  (wizard.js:149) to `check`; "+ ..." chips (plan.js:1241-1242, wizard.js:780-783) to `plus`; "College Board ↗"
  (plan.js:586) needs an external-link glyph (new, same 1.6 stroke); "↑ Focus" (wizard.js:637) and the swap "→"
  (plan-ui.js:382) to `arrow`.
- Goal marks ✓ ○ – as 12.5px text (plan.js:1336), map squares' 9px ✓ (plan.js:1421), sweep ✓ ✕ (plan.js:1567) and
  checkpoint ✗→✓ (progress.js:211): drawn marks (filled dot, ring, dash, cross) on the `.pl-dots` pattern (index.html:95-102).
- Task kinds: a 16px kind glyph (Warm-up `review`, Test `tests`, Words `words`, Focus `bolt`, Mistakes a new mark) in
  `--soft` before the title, in place of the tag badge; aria-label carries the word.
- Plan menu (plan.js:366-388): icons on Add to calendar (kit.js:183 `calendar`), Share, Print, Archive; the rest plain.
- Spot illustrations (single-stroke, ink at 40%, 64px): Rest day and Day off foot (plan.js:875-879), "Day done"
  (plan.js:887-888), Coming up empty (plan.js:1409), Plans empty (plan.js:1705), no traps yet (plan.js:1684).
- Active states missing: Coming up rows and Phases week rows have no selected look for the day on show beyond the week mark.

## 7. Delight and feedback

- Day done: the last tick draws a ring around the Day card's date that closes in 400ms, "Day done" fades in, the day's
  calendar cell fills ink, the This week dot fills and the streak rolls up. No confetti, no exclamation.
- Plan made: the month draws in week by week, Day 1's card rises, toast "Plan made · 62 study days to Nov 7".
- Wizard target slider: "+90" rolls as you drag; picking a date slides the Glance month to it; the "Steady / Ambitious"
  badge crossfades.
- Shape sheet: the week total "3 h 45 min → 3 h 15 min" rolls live; after Save the changed days get the changed-dot
  (index.html:127) with a single pulse.
- Score tile: when a test moves the status (Behind to On track to Ahead), the badge rolls to its new word.
- Drag a task: the drop target cell takes a wash pulse on drop and the moved row slides out (plan.js:1113-1151 ends with a
  plain redraw).
- Exam eve and exam day: the Day card takes a warm wash surface with the checklist; ticking all six items checks a small
  ring beside "What to bring".

## 8. Ranked top 10

1. Day card as the raised hero, Start alone with a tactile edge, "Today I have" folded into the facts line: one focal point. M, slop low.
2. Calendar card with one nav, unboxed days, legend behind `?`, no per-cell bars: removes ~20 boxes and 2 controls. M, slop low.
3. Wizard Glance calmed (figure line, month, 3-4 step rows, Week 1 / Day 1 seg, rest folded) and raised: the busy column goes. M, slop low.
4. Shape sheet: one seg per day, a live 7-bar week chart and rolling total, a one-line key, Save via UI.saving. M, slop med.
5. Tick feedback chain: check draw, meter fill, UI.roll on status figures, Day done moment. S, slop low.
6. Status card to figure + one line per tile, details in a tile popover: 8 lines become 4. M, slop low.
7. Unicode stand-ins to ICON svgs and drawn goal, map, sweep and checkpoint marks: polish everyone notices. S, slop low.
8. Wizard step slide, sliding stepper bar, and one shared "plan made" entrance for both create paths. M, slop low.
9. Row actions revealed on hover or focus, ghost ⋯ menus, kind glyphs instead of tag badges: quieter rows. S, slop med.
10. Wizard deferrals: per-day minutes behind a toggle, Math | R&W seg on step 4, 3 quick targets, gain box as step 2's hero. M, slop low.
