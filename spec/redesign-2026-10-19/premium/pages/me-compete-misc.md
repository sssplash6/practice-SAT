# Premium audit: Profile, Settings, Compete and the small pages (me-compete-misc)

Code-level only (no browser). Counts are estimates from the CSS and JS, prefixed `~`: main content only, the shell
excluded. The shell adds, at 1440: the sidebar (~17 controls, Up next's orange Start, the Today card); at 390: the
top bar (5-6), the tab bar (5) and, where a page does not pass `now: false`, the Now strip with a second orange.
Tags: [shared] needs ui.css / kit.js / ui.js (lead); [D6] / [D7] relaxes DIRECTION 6 (gradients, glow) or 7
(nothing animates on load), which this premium brief reopens.

## 1. First screen inventory

| Page | vp | btn | link | chip/tab | input | box | bar | label | help lines | control rows before content |
|---|---|---|---|---|---|---|---|---|---|---|
| Profile | 1440 | ~20 | ~5 | 12 + 1 badge | 0 | 4 cards, 4 tiles | ~12 (3 goal meters, week meter, 7 day dots, 6 week bars, 4 sparks, 2 gbars, 2 mastery) | ~12 | ~10 | 1: section bar, 12 chips (me.js:80, 1210) |
| Profile | 390 | 5 | 3 | 12 | 0 | You card, 4 tiles | 4 sparks | 4 | 5 | 3: top bar, Now strip (orange Start), section bar |
| Settings | 1440 | ~10 (7 pref controls, ~25 options) | 6 (aside index) | 6 | 2 switches | 1 card | 0 | 7 | 8 | 1: section bar, and the same 6 sections again in the aside (settings.js:40-43) |
| Help | 1440 | ~14 (12 disclosures, pill, btn) | 0 | 8 | 1 | 4 cards | 0 | 9 kbd rows | 1 | 2: section bar (8), search |
| Compete | 1440 | ~22 | 3 rows | 3 tabs, 4 filters, 2 badges | 0 | 3 cards, 10 ladder cells | ~14 (10 chance bars, season bar, 3 level rings) | ~6 | ~6 | 1: title, 3 tabs, Join, Create |
| Compete | 390 | ~8 | 0 | 3 + badge | 0 | Daily card | 0 | 1 | 2 | 4: top bar, Now strip (2nd orange), title + Join or create, tabs |
| Leaderboard | 1440 | ~19 (aside: 7 metrics, 5 periods, 2 steps, 2 ?, Jump to me) | 0 | 3 | 3 (2 selects, Find) | 3 pods, You strip, table | ~15 level rings | 8 col heads | 2 | 0 in main (controls in the aside) |
| Leaderboard | 390 | ~16 | 0 | 3 + 7 + 5 | 0 | podium | 3 | 0 | 1 | 5: top bar, Now strip, title + tabs, metrics row, period row + stepper + Filters |
| Rankings | 1440 | ~12 | 2 | 3 + 5 | 0 | 3 cards, 6 tiles | chart, 5 level rings | 6 | 3 | 1: title row |
| Contest lobby | 1440 | ~12 | 1 (back) | 1 badge | 1 select + 4 QOTD options | 4 cards, 10 cells | 10 | 2 | 3 facts, 9 rules, 2 notes | 2: back link; meta + 3 day buttons (contest.js:117-129) |
| Contest lobby | 390 | ~10 | 1 | 1 badge | 1 select | 10 cells (5 x 2) | 10 | 2 | 5 | 4: top bar, Now strip (orange), back, meta + day nav wrapping; up to 3 orange Starts (below) |
| Contest result | 1440 | ~8 | 1 | 4 badges | 0 (1 when the handle is default) | 4 cards, 5 tiles, 10 strip cells | ~8 | 5 | ~6 | 2: same header |
| Contest result | 390 | ~6 | 1 | 4 badges | 0 | 5 tiles (2 cols), strip | ~4 | 5 | ~6 | 4: top bar, Now strip, header on ~4 lines; the thumb bar carries See the board |
| Sign in | 1440 | 1 pill | 0 | 4 tabs | 1 checkbox | 1 card | 0 | 1 | 1 | 1: the 4 tabs (+ Google when on) between title and task |
| Sign in | 390 | 1 | 0 | 4 tabs on 2 rows (ui.css:1106) | 1 | 1 | 0 | 1 | 1 | 2 tab rows |
| Welcome | 1440 | 4 (seg 2, pill, quiet) | 0 | 0 | 2 | 1 | 0 | 0 | 3 | 1: Create / Sign in seg |
| Welcome | 390 | 4 | 0 | 0 | 2 | 1 (flush to the top bar, me.css:313) | 0 | 0 | 3 | 2: top bar, seg; fits in 844 |
| Pair | both | 0 | 0 | 0 | 6 OTP | 1 | 0 | 0 | 1 | 0 |
| Parent | 1440 | 3 (language seg) | 0 | 0 | 0 | 3 cards, 6 stats | 14 bars, ~4 meters | 6 | 1 | 1: language seg on the title row (fine) |
| /s/ | 1440 | 2 | 0 | N topic chips | 1 checkbox | 1 card, 4 tiles | 0 | 4 | 3 | 0: Start follows the description |
| Share | 1440 | 0 | 1 | 0 | 0 | 2-4 cards | ~8 | 4 | 4 | 0 |
| 404 | both | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |

Shell fact behind three of these: Sign in, Welcome and Pair call the full `UI.shell` (signin.js:18, welcome.js:14,
pair/index.html:48) with only `now: false`; the sidebar's Up next card and its orange Start stay, because only
`nowBlock: false` removes them (ui.js:2452). A new visitor's first screen is an app chrome plus two oranges.

## 2. Clutter fixes

Shell asks [shared], the two biggest wins:
- Focus chrome for signin, welcome, pair: no sidebar, no tab bar; a slim brand bar like share's `.sh-bar`
  (share/index.html:19-20) with Help and an account button at the right (the sidebar's user row is the only path to
  Students on this device and Sign out here); the card centred in `min-height: 100dvh`. Nav stays one tap away (the
  brand link). Until then: pass `nowBlock: false` on all three so the second orange leaves.
- Defer the section bar where two columns already show the cards (Profile, Settings, Help at 1280+): render it only
  once `.stuck`. Settings and Help use their aside as the one index (Settings has it; Help gains its 7 groups there).

Sign in (signin.js:52-65): show one method, the one `first` already picks (signin.js:37): one full-width `.pill`
(passkey, or the remembered email's one-tap send), Google under it, then one quiet "Other ways to sign in" that opens
the four as `.choice-row`s with icons. All four and their hashes stay. Shared computer stays, under the panel, 13px.
Calm: mark 40 -> title -> one line -> primary -> Google -> Other ways -> shared computer.
Note: Google is a GIS iframe (account.js:201, outline, large); it takes none of our styling. Give it a fixed 44px slot
at the pill's width and leave it.

Welcome (welcome.js:46-54): the seg goes; the mode switch becomes a text line under the button ("Have an account?
Sign in"). "No password" moves to a 12.5 line under the pill; "Continue without an account" stays last, 24px above.
Calm: mark -> headline -> one value line -> First name -> Email -> Create my account -> two quiet lines.

Profile:
- This week (me.js:406-412): keep the 3 goals and Start; Weekly goal dots, "Met 4 of the last 6" bars and the
  "Last week" receipts become one summary row that opens the Your week sheet (week.js:65 already shows receipts).
- You tiles (me.js:339-378): at rest label and value only; delta and sparkline on hover or focus. ~20 marks -> 8.
- Skills: `Practise · N` per row as `.reveal` (ui.css:341) except the top row; the `sk-x` line (me.js:789-797) too.
- Trophy room vs the pass's "work first": do not flip the columns again. Add a full-width identity plate above both
  columns (§3); This week stays the first card under it. Achievements stop living at `--o: 10` out of view (me.js:69).

Compete overview (overview.js:53-126): Daily head keeps title and date; the streak badge becomes flame + count by the
title; "Next one in" moves to the foot and shows only after finishing. Start becomes a full `.pill`; Warm up and
More fold into one `⋯` menu (Warm up · 6, Past days, Daily reminder). Ladder cells drop the visible number (the label
keeps "Q3") and the chance bar becomes the cell's bottom fill. The aside's "This week" 3-way filter folds into one
small dropdown in the part head (every metric also stays on Full board). Calm: title row -> Daily (title, date, facts, Start) -> ladder -> foot -> Contests.

Leaderboard: at 390 (`side-first`, leaderboard/index.html:50; leaderboard.js:85-132) one summary control in the
title row, "Points · This week · Everyone", opens a sheet with metric, period and stepper, scope, domain and Find;
the podium leads. At 1440 the metrics become a vertical list of `.choice-row`s (no 3-line wrap in 300px), period a
`UI.seg`, the stepper under it.

Contest: the day nav (contest.js:119-129) moves into the Your days card beside its strip; the header is back, title +
badge, one meta line. Result (contest.js:286-407): a hero (rank, Top %, score, points, See the board), then one
rating line; race, par and rivals lines merge into one context line; Skills and Mistakes from this sitting fold; 5
tiles -> 3. Lobby: Rules start folded with Points, Pace bonus and Ties visible (contest.js:919); the side QOTD uses
the overview's one-row form (overview.js:226-238) until answered. Phone lobby: the Now strip's Start, the state
card's `#start` (contest.js:226) and the thumb bar's Start (contest.js:992) all show, since `.has-thumb` hides only
`.youbar` and `.see-board` (compete.css:196-197): hide `#start` under `.has-thumb` and pass `now: false` here.

One line each: Settings: the duplicate index (above). Help: the search is the hero; 7 group cards -> one surface with
group headings. Parent: blank until `/account` resolves (parent.js:131-135): skeleton the This week card. /s/ and
share: `.rise` on cards is dead (s/index.html:125, 137, 193, 323, 399; ui.css:2555). 404: calm; add §6's spot.

## 3. Depth and hero

Two shared tokens [shared], defined once: `--shadow-1: 0 1px 2px rgba(30,30,30,.05), 0 8px 24px -12px rgba(30,30,30,.16)`
(dark: rgba(0,0,0,.5)), ink-tinted like `--shadow-float` (ui.css:108); `--hero-wash`: a top-left radial of `--wash`
fading into `--tile` [D6]. Only heroes and floating things get them; list cards stay flat (`.card` inset line,
ui.css:1203). One hero per page:
- Sign in, Welcome, Pair: the card. `--paper` on a `--tile` page with one soft `--wash` radial behind it [D6],
  `--shadow-1`, mark 40 (now 32, welcome.js:15). Fields go back to `--tile` inside (ui.css:985 paints them paper).
- Profile: the identity plate. `--hero-wash`; the living mark (kit.js livingMark) at `.avatar.xl` 72 (ui.css:425;
  now 56, me.css:72-73) with `data-ring`; name 28; one meta line (board name, since, saved); the level ring; a shelf
  of the last 3 earned badges as 44px `.bcirc` (me.css:212) with an inner top highlight and, earned, an amber-tinted
  shadow; "12 of 35 · All badges". The four tiles sit under it as one figure row.
- Compete overview: the Daily card. `--shadow-1`, `--hero-wash` behind its head; ladder cells become inset wells
  (`--paper`, inset 0 1px 2px rgba(30,30,30,.06)) so they read as slots to fill. The aside card stays flat.
- Leaderboard: the podium (compete-ui.js:106-117). Stepped pedestals 136 / 112 / 96 (now 120 / 108 / 100), a 1px
  top highlight, `--shadow-1`; #1 on `--paper` with an amber floor shadow (0 14px 24px -14px rgba(241,133,8,.45))
  [D6]; level badges 28. The You strip, once `.stuck` (compete-ui.js:98), floats: `--shadow-float`, radius 12.
- Contest result: the rank block on `--hero-wash`, the level ring 48 at its left. 44 stays (the scale's top,
  compete.css:135); anything bigger is a DIRECTION change for the lead, not a page one.
- Rankings: the Rating card (rankings.js:119-150), ring 48 -> 64. Parent: This week, its figure 28 -> 44, `--shadow-1`.
  Help: the search. /s/: the set card. Settings: none, on purpose.

## 4. Buttons, controls, highlights

| Control (where) | Now | Should feel |
|---|---|---|
| Hero primary: Start the challenge (overview.js:76, contest.js:222, 226), Sign in (signin.js:89), Start the first (me.js:45, 411) | `.pill.sm` 34px, flat amber, hover 8% darker, press .97, busy = opacity .6 (ui.css:855-875) | full `.pill` 42; [shared] tactile: inset 0 1px 0 rgba(255,255,255,.35), inset 0 -1px 0 rgba(0,0,0,.1), 0 1px 2px rgba(150,80,0,.25); hover (fine pointer) lift 1px, shadow 0 6px 14px -6px rgba(241,133,8,.5); press 120ms down + .98; focus `--ring`; busy "Starting" + 14px spinner, width held (the UI.saving pattern); success check, then go |
| `.btn` (Warm up, More, Change goals, day nav) | well fill, press .97 | a 1px inset bottom line for weight; More becomes `.ibtn` with the dots icon (compete-ui.js:169) |
| `C.under` choices (compete-ui.js:380-410): Contests filter, metrics, periods, chart ranges | static 2px underline per button | one sliding underline, the `.tab-ind` way (ui.css:2535) [shared] |
| Compete subnav (compete-ui.js:137-141) | static underline | the underline carries between the 3 pages via a named view transition (ui.css:2560 is on) |
| Contest rows `.crow` (compete.css:65-77) | hover underlines the title | row wash bleeding 8px, chevron nudges 2px right, press .99 |
| Ladder cells `.lad` (compete.css:43) | 1px line box, tooltip | inset well; hover or focus lifts 1px with an ink edge |
| Board rows (compete-ui.js:66-92) | hover tile-2; yours wash + 3px amber | yours on `--paper` + `--shadow-1`; `tr.hl` after Find or Jump fades out over 900ms |
| Sign-in methods | `UI.tabs` | `.choice-row`s with 18px icons; picked = wash-2 + amber inset (exists) |
| OTP (ui.css:1003-1013) | ink border, dashed when wrong | a filled digit pops 1.06 for 120ms; wrong: three 4px shakes, 240ms; right: all six take the amber edge |
| Fields (ui.css:965) | 1.5px ink inset on focus | plus a 3px `--wash-2` halo |
| Folds (me.js:91, rankings.js:27) | chevron rotates, body snaps | body height 200ms in, 150 out (grid rows 0fr -> 1fr) |
| Top % badge (contest.js:292, overview.js:100) | `.badge.soft` grey | top 10% or better: `.badge` (wash-2) with a 12px medal |

## 5. Motion moments

| Moment | Trigger | What moves, how |
|---|---|---|
| Welcome / Sign in entry [D7] | first visit on this device (Emil: rare, first-time) | card rises 12px and fades, 240ms `--ease`; then the mark's four corners fill one by one, 4 x 90ms |
| Method switch | Other ways, a pick | panel height and a crossfade, 200ms (a 2px blur on the outgoing panel only if the crossfade reads as two states [D6]) |
| Phone code expiry (signin.js:131-162) | QR shown | a 2px amber ring around the QR frame drains `linear` to the expiry (a timed fill, D7 allows) |
| Sign-in success | `finish()` before `location.href` (account.js:156-176) | the mark fills, then the view transition out, 300ms |
| Profile shelf [D6] | a badge earned since the last visit | one gradient shine across its circle, 700ms, then still |
| Profile tiles [D7] | first view this session | `countUp` (kit.js:1617, opt-in; me.js:351 never passes it) on Answered and Mistakes fixed only |
| Folds | toggle | height + opacity, 200 / 150 |
| Hero Start | press | press 120ms -> busy -> page transition |
| Podium | a metric or period change (never on load) | pedestals rise from 85% height in the order 3, 2, 1, 60ms apart, 240ms each |
| Jump to me | click (compete-ui.js:562 scrolls) | the row's wash fades out over 900ms |
| You strip | becomes `.stuck` | slides 8px down as its shadow appears, 160ms |
| Result reveal | first view of a sitting (contest.js:423-428; today a 320ms fade, :408) | rank rolls from "#players" to "#rank" (`UI.roll`), Top % pops from .9, tiles 40ms apart; on a level change the ring fills from the old level to the new; New best star turns 20 degrees once; ~600ms in all |
| Parent bars [D7] | first paint (weekly visits) | bars grow from the baseline, 15ms apart, 240ms |

The live-poll rank roll (contest.js:698-709) stays as is. Reduced motion keeps opacity only (ui.css motion block).

## 6. Icons and imagery

- Unicode stand-ins: ▲▼ deltas (me.js:343, 638, 791; overview.js:263, 358; leaderboard.js:311; rankings.js:143,
  209) -> a 10px caret svg; ✓ ✕ as text (me.js:214, 389, 793, 1000; settings.js:429; s/index.html:245; contest.js:23
  with » ⊘ –) -> the check and x icons and the `.cell` glyphs; × hits (me.js:1002); → (me.js:325, overview.js:109,
  contest.js:320); ↑ ↓ (me.js:1019). The ‹ › back and day controls (contest.js:117, 121-124; leaderboard.js:103-104)
  were kept on purpose as direction controls (pass, Not done); same reason, real glyph: the chev icon rotated.
- Missing from ICON (ui.js:438): medal, lock or shield, mail, key, qr, fingerprint. Wanted for the sign-in methods,
  6 Settings index icons (sliders, text, bell, devices, chat, shield) and podium places.
- Badge art is split: Profile draws 35 custom line badges in `.bcirc` (me.js:1031-1076); Compete's badge lists show a
  name and an 8px amber dot (rankings.js:299-310, overview.js:388-404, compete.css:223). Move BADGE_PATHS and
  `.bcirc` to the shared layer [shared]; one look on all three pages.
- Credit: BADGE_PATHS, the kind icons (compete-ui.js:161-176) and the level ring (compete-ui.js:342-362) are already
  custom line art in one 1.6 stroke; every new icon takes that stroke.
- Empty states are bare `p.soft` (me.js:1005, 1023, 1133; overview.js:288; leaderboard.js:297; rankings.js:58;
  parent `none`). First `UI.empty`'s dimmed sample row (ui.css:1352-1359): a ghost heatmap for Activity, a ghost
  podium on the Leaderboard, locked silhouettes on the shelf. Spot illustrations only three: 404 (the brand mark with
  one corner drifted off), Rankings' "No contests yet" (the level ring at "–", 64px), Parent's "No student linked"
  (three steps: Settings, Privacy, Invite a parent).

## 7. Delight and feedback

- Welcome: the living mark introduced once ("Your mark fills as you master each domain") as its corners fill: it
  explains the avatar the student will own.
- Sign in: the mark completes on success; "Signed in as Maya" already follows (account.js:174).
- Profile: the shelf and its shine; hovering the living mark (its title, kit.js:2242) opens four mini meters, one per
  domain; the streak flame by the name flares once on a new best.
- Compete: medals on the podium; "beat Maya" in Rivals today (contest.js:418) gets a check that pops; a level up
  fills the ring and says "Level 5"; Copied on Copy result previews the ■□ grid it copied.
- Pair: on approve, a large check and "Chrome on Mac is signing in now" in the card.
- Parent: "+12 more than last week" with an ink caret; the weekly-email box says Saved in place (UI.saving).

## 8. Ranked top 10

1. Focus chrome for Sign in, Welcome, Pair: no sidebar, a centred elevated card on a soft brand backdrop; the first impression stops being an app you have not joined. L [shared]; slop low.
2. Sign in shows the device's best method, the other three behind "Other ways" as icon rows: one decision, not four tabs. M; slop low.
3. Tactile hero primary: full 42px pill, inner highlight, amber-tinted shadow, lift and press, a Starting state; on Daily, contest, Welcome, Sign in, Profile. M [shared]; slop low.
4. Contest result reveal: the rank rolls from field size to place, Top % pops, the level ring fills, on a tinted hero, once per sitting. M; slop med.
5. Leaderboard podium as raised pedestals with medals and #1's amber floor shadow; on phones one summary control so the podium leads. M; slop med.
6. Profile identity plate: 72px living mark with its ring, name, level and a shelf of the last 3 badges in the shared badge art. M; slop med.
7. Compete Daily as the one focal point: full Start, Warm up and More in one menu, countdown to the foot, ladder cells as inset wells. S; slop low.
8. `--shadow-1` and `--hero-wash`, used only on heroes: depth without boxing everything again. S [shared]; slop med (D6).
9. Sliding indicators on `C.under` choices and the Compete subnav (a view transition across its 3 pages). S; slop low.
10. Empty states via `UI.empty` sample rows, three spot illustrations, and svg carets and checks for ▲▼✓✕. M; slop low.
