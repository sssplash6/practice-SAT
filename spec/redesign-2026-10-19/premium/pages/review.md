# Premium audit: Review and Mistakes (web/review/**, web/mistakes/index.html)

Code-level only. State audited unless said otherwise: Redo tab, 23 open mistakes in topic groups, 3 new misses from one
sitting, no worksheet waiting, selection defaulting to all (review.js:70), list column beside the pane from 1280px
(index.html:103). The shell sidebar (248px, 9 links, Today card) is shared and not counted.

## 1. First screen inventory

**1440x900, Redo.** Vertical stack (y, px): header 16-58 (index.html:25, min 42) / notes line 70-106 (index.html:34) /
tabs 118-154 / tab sub-line 160-179 (index.html:45) / Insights summary 191-213 (review.js:1158) / filter row 225-261 /
body from about 273: list head 44, group head 44 plus an italic tell, then rows. In the 380px column the container query
(index.html:181-186) puts tags on their own line and lets the title run 3 lines; the meta line wraps 2-3 times, so a row
is about 95-125px. The floating bar covers the last ~70px (and the pane's foot too). Result: about 4 mistakes visible.
The pane shows a 52px band holding only "Tools ▾" (runner.js:3123-3129), the head, the odds line (runner.js:3486), the
facts panel and the History timeline (runner.js:3523) before the stem, which starts near y 600: one or two options show.
- Buttons about 26: Start + caret 2, Walk 3 misses 1, tabs 6, Insights 1, Status and Sort dropdowns 2, Filters 1,
  list-head More 1, group Fix + fold 4, row buttons 4, pane Tools and cause chip 2, bar Options + Fix 2.
- Links 1 (pane sitting link). Inputs 8: search, 7 checkboxes (list head, 2 groups, 4 rows), all pre-checked.
- Chips and badges about 19: 3 Difficulty chips, 6 tab count pills, ~8 row tags (up to 5 a row, review.js:827-836),
  pane status chip and tags.
- Boxes 6: bordered list panel, 2 tinted group bands, pane card, pane facts panel, floating bar.
- Bars and marks: tab underline, current-row bar, 4 difficulty bars, 4 pip pairs, pane pips, timeline.
- Helper text about 22 lines of 12.5px soft: notes meta, sub-line, Insights meta, list-head meta, 2 group metas, 2
  tells, 4 row metas (up to 10 bits each, review.js:837-848) at 2-3 lines, pane odds and count line, bar summary + echo.
- Rows of controls before the first mistake: 8. Header (title, Start split) / notes (Walk) / tabs / sub-line /
  Insights / filters (Search, Easy, Medium, Hard, Status, Sort, Filters) / list head (select all, count, More) /
  group head (select, Fix N, fold).

**390x844, Redo.** Shell bar 56; header 72-116 (buttons 44 on touch); notes wrap to two lines 128-212; sticky tabs
224-272 (index.html:230-233); sub-line to ~290 (often two lines); Insights to ~322; Search + Filters · n 334-378
(ui.css:1182-1184 hides the rest); list head 390-434; group head and tell to ~498; first row 498-608. The bar is fixed at
72px + safe area (index.html:237) and wraps to ~110px, so its top sits near y 630: one mistake and a sliver. Buttons 17
(Start 2, Walk, 6 tabs, Insights, Filters, More, group 2, row, bar 2), 4 inputs, 6 count labels, plus 5 bottom tabs.

**Other states.** Due (default when anything is due, review.js:110) is calmer: Start, notes, tabs, sub-line, rows (no
filters, list head, bar or checkboxes). Walk (walk/index.html:41-47): one card with dots, Resume, Back: calm. Sheet: answer
rows, a sticky side card from 1280. Print: calm. mistakes/index.html is a 24-line redirect: nothing to audit.

## 2. Clutter fixes

- **Filter row** (index.html:87-90, review.js:412, 458): 7 equal-weight controls. Keep Search left and, right-aligned,
  Sort and Filters · n. Difficulty and Status go into the Filters popover (they are already there on a phone). This
  reverses the polish round's Difficulty chips: three usually-unset chips take a third of the row. A set filter shows as
  a removable token in the list head ("Medium ×", "Half fixed ×"), with Clear beside it (today the row hides Clear at
  every width, index.html:89; only the sheet has it).
- **Sub-line + Insights** (index.html:45, review.js:372, 1158-1167): two rows of small soft text. The tab's figures
  ("2 half fixed · 1 relapsed · ≈ 140 pts at stake") move into the list head, which describes the list; Insights becomes
  a .quiet at the right end of the filter row (chart icon, its meta as the tooltip, same remembered open state). 2 rows go.
- **Notes line** (review.js:281-313): costs a full row on every tab. New misses become a pinned first row in the Due and
  Redo lists (amber dot, "3 new misses from Section · Sep 21", Walk · about 5 min) and an unread dot on the Redo tab
  while counts.new > 0. Worksheets waiting: an item in the Start caret menu beside "See the list first". Same buttons,
  same hrefs.
- **Tab counts** (review.js:323-342): six pills; History's is lifetime answers (339), which nobody acts on. Pills only on
  Due (left today) and Redo (open); Marked, Saved, Fixed as plain soft numerals; History none (its figure leads its own
  summary line, review.js:1494). aria-labels keep every count.
- **Row diet** (review.js:821-856): keep the title (2 lines), one status badge (Blind spot, else Relapsed, Stuck, Half
  fixed), and three meta bits (tier bars, last date, pts right-aligned as a tabular figure). New becomes an unread dot
  before the title, Saved a bookmark icon after it. Skill, MC / Grid-in, missed n×, source, picked, avoided in, kind,
  cause and +n elsewhere already sit in the pane head (runner.js:3451-3519) and the phone dialog; they stay in the row's
  aria-label too. Rows drop from ~110 to ~68px in the column.
- **Checkboxes** (index.html:137-143): 20+ pre-checked boxes on load. Show a row's box on hover or focus, or for every
  row once the student changes the selection (the lead pips swap to the box on hover). Select all stays in the list head;
  touch keeps long-press (review.js:695-705) and gets a Select toggle in the list head.
- **Group heads** (review.js:786-815): Fix N and the fold reveal on hover (always on touch); meta trims to "4 open ·
  ≈ 24 pts"; domain and per-test go to the title tooltip. Heads stick to the top of the list column while their rows scroll.
- **Action bar** (review.js:1700-1754, index.html:211-216): two lines, full width, over the pane. One line: "23 selected
  · about 63 min", Options as an icon button, Fix 40. Types and question counts move into the Options popover head. The
  pass said one line truncates on a phone: there it shows "23 · Fix 40" only, the rest in the Options sheet head. From
  1280 the bar docks at the foot of the list column (sticky bottom inside .rh-panel), so it never covers the pane.
- **Phone row actions** (index.html:173-176; review.js:853, 917, 1016, 1132-1144): 1-2 buttons per row on touch.
  One row ⋯ (icon) opens UI.menu with the same items (Learn this type, Note, Unsave, n tries, Prove it, Reopen).
- **Pane** (shared ask, runner): move Tools into the head's top right as an icon, drop the 52px band (runner.css:868);
  fold the odds line and History timeline into the facts card as "Details". The stem then starts ~150px into the pane.

**Calm first screen, 1440.** (1) "Review" left, Start split right (chev icon caret); 24px. (2) Tabs: Due 3, Redo 23
with an unread dot, Marked 12, Saved 9, History, Fixed 41; 16px. (3) Tools row: Search left; Sort, Filters · n, Insights
right. (4) From ~y 190: the list column flat (list head: Select all · 23 open · ≈ 140 pts · tokens · More; the pinned
new-misses row; sticky group heads; ~68px rows) beside the raised pane, stem visible by ~y 350. (5) The bar docked under
the list. Rows before content: 4 (was 8); buttons about 16; no chips in a toolbar. Mistakes visible: 6-7 (was 4).
**Calm first screen, 390.** Header, sticky tabs, Search + Filters + Insights, list head, the pinned new-misses row, then
~3 rows above a one-line bar (was one).

## 3. Depth and hero

The hero is the question pane, where the task happens and where the fix lands. Today it is a flat 1px box level with
the list (runner.css:867), a --tile facts panel (runner.css:1201), and the bar sits over its foot.
- Layering: the list column goes flat (hairline rows, no outer border: index.html:94); the pane becomes the one raised
  surface: paper, 14px radius, 1px --line ring, a warm two-layer shadow (0 1px 2px rgba(63,52,40,.05), 0 12px 32px -12px
  rgba(63,52,40,.16)), one light source from above. Dark mode: --tile surface and the ring, no shadow.
- The facts panel is the fix meter: pips at the lg size (ui.css:1543), status word 16/600, the count line under it. When
  the mistake closes it turns --wash with an amber-deep check (orange marks progress: allowed).
- The pane head sticks while the question scrolls; a hairline shadow appears only once scrolled (the edge-fade pattern).
- Not the hero: a big "≈ 140 pts at stake" figure (a second focal point beside Start), the Insights card, the tab row.
  Flat: group bands, list head, Insights, Your rules, empty states, Walk and Sheet cards. Raised: pane, bar, popovers.

## 4. Buttons, controls, highlights

| Control | Now | Should feel |
|---|---|---|
| Start split | two .pill, caret is text "▾" (review.js:181-193); hover darkens 8%, press .97, busy opacity .6 (ui.css:871-875) | chev icon caret behind a 1px ink-deep/12% divider; tactile pill (inset top highlight, 1px darker bottom edge, small amber-tinted drop: shared ask); busy turns the caret into a 14px spinner, label stays |
| Tabs | UI.tabs, sliding amber underline (ui.css:2532-2541), count pills | counts roll on change (UI.roll exists, kit.js:1639); unread dot on Redo; hover tints the count pill |
| Filters | .dd orange while set; chips orange while pressed | set filters as list-head tokens; × shrinks a token out in 120ms |
| Rows | hover tint .16s; current: tile + 2px amber inset, instant (index.html:139); focus ring ink | current bar grows (scaleY 160ms); hover reveals the checkbox; checked rows in selection mode get a faint --wash |
| Checkboxes | native, amber accent | check stroke draws in 120ms (shared .check) |
| Group fold | chevron rotates .2s but rows vanish (display:none, index.html:126) | rows collapse 200ms (grid 0fr/1fr); chev icon |
| Bar + Fix | no entry (index.html:211; .selbar has rise, ui.css:1193) | rises 240ms on first show, exits 180ms; summary figures roll; Fix busy spinner |
| Two oranges | from 1280 the bar's Fix and the pane's Twin pill after a miss (question.js:1859) or Learn on stuck (runner.js:3758) | in pane mode with the bar showing, the pane's Twin is a .btn (the pass flagged rv-next for the same rule) |
| Insights | summary text with a 5px chevron (ui.css:2670-2675) | .quiet with a chart icon; body rises 160ms |
| Due × | .x reveal, toast with Undo | row dims to .5 over 160ms, "Not today" fades in |
| Note save | toast "Note saved" (review.js:934) | UI.saving in place (Save, Saving, Saved) |
| Walk dots | 10px circles, current amber outline (walk/index.html:31-33) | walked dots fill amber, current keeps the ring |
| Sheet bubbles | 44px round, ink fill on press, no transition (sheet/index.html:35-37) | 120ms fill, press .94 |

Success: Start and Fix navigate away (right). Loading: static skeleton rows (review.js:557-564), keep and crossfade.

## 5. Motion moments

**The moment a mistake is fixed, now.** (1) The twin is answered right in the pane: runner.js:3821-3823 lowers owed
and at 0 sets status fixed; paintHead replaces the pips line in one frame. (2) The verdict adds "Fixed · label" with
fixedin, .2s from scale .96 (question.js:1352-1355, runner.css:256-257): the only animated beat. (3) review.js:2032-2039:
a plain toast "Fixed: label" with no icon, the list row collapses by inline style (opacity and max-height .25s, a layout
animation), loadCounts makes the tab pills jump. The list is not reloaded, so the group head ("4 open"), list head and
bar ("Fix 40") stay stale until the next load. On a phone the row is behind the dialog: only the toast shows.

**Proposed** (desktop, about 900ms; rare, so delight is allowed):
- 0ms: verdict line pops (keep).
- 80ms: the last pip fills amber with the existing pin keyframe (ui.css:2547), 220ms; the facts row crossfades pips to a
  check (2px blur as a motion mask, not a surface blur), 160ms; the word becomes "Fixed"; the panel tints --wash, 240ms.
- 200ms: the list row's lead becomes a check; the row washes amber at 12%, 240ms. Hold.
- 700ms: the row slides 8px right and fades (150ms), then its height closes (grid rows 1fr to 0fr, 180ms) by a class,
  not inline style; the list refetches quietly so group, list head and bar figures are true.
- With the close: Redo's count rolls down, Fixed's rolls up with one --wash flash; the bar summary and Start label update.
- No toast on desktop; the pane's live region (runner.js say) announces it. The phone dialog keeps the toast with the
  check icon (o.icon) and "22 open". The last open mistake crossfades the list into Nothing open (section 6).
- Reduced motion: colour and opacity only; no movement, no blur.

**Other moments** (frequent ones stay short or still):
- Tab switch: underline slide exists; panel crossfades 120ms out, 160ms in with a 4px rise. Arrow keys: instant.
- First paint per tab: skeleton crossfades to rows, 160ms. A 20ms stagger on the first 6 rows reverses DIRECTION 7
  ("nothing animates on load"): only if the user wants it.
- Open a row by click: pane body crossfades 140ms (same 2px mask); current bar grows. j / k: instant.
- Select: box draws, bar figures roll, bar rises on first show and exits when the selection empties.
- Group fold and Insights: 200ms height; chevron rotation exists.
- Rows that leave (Unsave review.js:942-959, Unmark 1631-1647): a hard repaint today; reuse the fix exit, no wash.
  Insights stack bar and the Fixed chart: segments grow once on first open (grow, ui.css:2549).

## 6. Icons and imagery

- Unicode stand-ins: "▾" Start caret (review.js:184), group fold (811), sitting Fix menu (1053); "⋯" (1064,
  sheet.js:194); "✓" Due tab count (330, parsed again in the aria-label 369) and lead ticks (736, 1130, "–" when
  dismissed); "×" / "↺" preview drop (260, 265) and Due not today (743); " ✓" / " ○" proven levels (1127); "‹ Review"
  back links (walk/index.html:43, sheet/index.html:81, print.html:78); "Tools ▾ / ▴" in the pane (runner.js:3124-3129).
- ui.js ICON has chev, check, x, dot, search, review; kit has filter, fix, twin, again, learn. "more", "left" and a
  flag exist only in the runner, question and words maps (runner.js:85, words-ui.js:160-162; flag drawn three ways,
  strokes 1.6 and 1.8). Shared ask: one UI.ICON with more, left, undo, sliders, flag, bookmark at stroke 1.6.
- Missing active states: the unread dot (new misses), the open tab's count only shifts tint, topic glyphs on group
  heads have no current state.
- Empty states (review.js:634-661): only a new student's Redo gets a sample row; the rest are one text line. Add 40px
  line spots in --faint with one amber stroke from the icon set: tray with a check (Nothing open), flag (Marked),
  bookmark (Saved), clock (History), check in a ring (Fixed); Marked and Saved also get the dimmed Example row.
- Walk: one small icon per step (try, why, key, prove) beside "Step 1 of 4" (walk.js:179).

## 7. Delight and feedback

- The fix moment (section 5): the one reward on the page, landing in the pane and the row at once.
- Nothing open: the tray draws once, "Nothing open · 41 fixed" (a fact, not praise), Keep going stays.
- Due done for today: the Due count morphs from 3/8 into a check icon; a tick meter (.meter.ticks, ui.css:2479) in
  the Due sub-line fills one tick per finished item.
- Fixed: "Held all 3" shows three amber pips that settle into a small seal once; a won Prove it at Hard fills that
  row's bars with grow.
- Walk done (walk.js:170-175): one row per mistake with its pips (proven ones amber) and "named 4 of 5" as a 28px
  figure, instead of a line of text.
- Worksheet done (sheet.js:175-183): "7 / 10" counts up once (countUp is opt-in, kit.js:1617).
- Spot the trap (review.js:2047-2077): the trap choice's amber ring draws in (clip-path, 200ms); a right pick puts a
  check icon in the status line.
- Phone: toasts sit 80px up (ui.css:2275), under the fixed bar (72px + ~110): lift them above it while it shows.

## 8. Ranked top 10

1. Filter row to Search + Sort + Filters · n, Difficulty and Status behind Filters, set filters as list-head tokens: 7
   equal controls become 3 and the row reads as tools, not a form. S. Slop low.
2. Sub-line figures into the list head, Insights to the tools row, new misses as a pinned row plus an unread dot: three
   full-width rows gone, the list starts ~85px higher. M. Slop low.
3. Row diet (title, one badge, three meta bits, pts as a right-aligned figure, New as a dot, Saved as an icon): 6-7
   mistakes on the first screen instead of 4. M. Slop med (the pane and aria keep the dropped meta).
4. The fix moment: pip fills, facts card turns wash with a check, the row washes and leaves, counts roll, no desktop
   toast: the page's reward lands where the eye is. M. Slop low.
5. Raise the pane, flatten the list (one paper card, warm two-layer shadow): real depth and one focal point. S here
   plus a runner.css:867 ask. Slop low.
6. Dock the action bar under the list column from 1280, one line, rise in; phone shows count + Fix: the pane is never
   covered and the primary sits under what it acts on. M. Slop med.
7. Checkboxes on hover or in selection mode (pips swap in), Select all stays: removes a column of pre-checked boxes.
   M. Slop med (discoverability; the list-head toggle covers touch).
8. Tab counts only where actionable (Due, Redo), counts roll on change, Due done as a check icon: six pills become
   two. S. Slop low.
9. Icon pass (▾ ⋯ ✓ × ↺ ‹ to chev, more, check, x, undo, left; one icon map) and a tactile pill on Start and Fix:
   consistent strokes, buttons that feel pressable. S. Slop low.
10. Empty-state line spots, the Nothing open state, Walk and Sheet done figures: the quiet states look designed. M.
    Slop med (the drawings must match the 1.6 stroke icons or they read as clip art).
Not proposed: glass, grain, spotlight borders, gradient cards, fully rounded chips (DIRECTION 6 or high slop).
