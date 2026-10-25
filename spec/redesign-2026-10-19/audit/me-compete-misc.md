# Audit: Me, Settings, Compete and the small pages (2026-10-19)

Scope: web/me/** (me.css, me.js, account.js, week.js, settings/*), web/compete/** + assets/compete-ui.js, help, signin,
welcome, parent, pair, share, s, 404, admin (low). Code-level only. Shell findings are not repeated (BRIEF.md).

Viewports. 1440x900: main 1192 wide, `.page` is border-box 1120 so content = 1040 (gutter 40). Me grid = 320 + 20 + 700;
Compete grid = 680 + 20 + 340. 390x844: gutter 16, content 358, card inner ~326. Today's shell at 900 tall: the sidebar
is nav only, the Now strip (44 + 16) and the sticky section bar sit above every page here, including Sign in.

## A/B/C/D by page

**Me /me/** (me.js 63-80, 16 cards; me.css)
- A: the name is the h1 (me.js 182). No single next action: up to 9 amber pills on one page (me.js 383-384, 460, 676 x3,
  703-704, 814, 906, 956/971, 1174).
- B: chrome before the You card at 1440x900 = 27 top + 60 Now strip + ~80 section bar (16 chips wrap to 2 rows,
  me.js 81-82) = ~167px. Gaps: grid/col 20 (me.css 6-7), card-pad 22, `.outs` 18/14 (53), `.row` 12 (28), `.card-foot` 16
  (133, global), chip hosts 20 inline (me.js 1088, 1147). At 390 the You card alone (avatar, 3 id lines, up to 3 outs,
  up to 8 tiles at 2 per row, me.js 323-352) is ~750px: This week starts below the first screen.
- C (always on, not needed at a glance): Goals "What 700 takes ..." sentence (me.js 418-421, `.s`, never folds); Snapshot
  climb and "You, N days ago" lines (627-635); 11 round "?" buttons + 16 fold chevrons in card heads; "Studying since"
  (204); Daily challenge and QOTD rows (642-649). Recent activity starts folded once (86): good, reuse the mechanism.
- D: the 320 column is the wrong one for charts: Score trend (200px band chart) and Pace (quadrant) sit in it, while
  the 700 column carries the 16-row Learning preferences form third, above Skills (desktop DOM order, me.js 63-80).
  Desktop order and phone `--o` order disagree (prefs is o 14 on phone, 3rd on desktop; Saved/Account precede Trend).

**Settings /me/settings/** (settings.js; card shells in settings/index.html 25-30)
- A: clear; no primary needed. B: `.set` max 820 (me.css 183) leaves 220px dead at 1440; Practice card paints ~36
  pref rows (settings.js 51-55) = roughly 2000px; Account card is 8 blocks 26px apart (me.css 211), `.sub-h` 22/6 (185).
- C: intros fold (81, 652, 654: wanted). Stage line (87-93) repeats Me prefs (me.js 733). Sample question `.preview-q`
  always on under Text size (74). D: section index fits a sticky aside list at 1280+; Account status line could sit there.

**Compete overview /compete/** (index.html 29-53, overview.js)
- A: purpose = today's Daily + what is live. "Start the challenge" (pill.sm, overview.js 78) comes after the kicker row,
  10 ladder cells (72px each) and two fact lines; at 390 it lands ~560px down. Join/Create offered 3 times (index.html
  32-34, overview.js 211, 442, 465).
- B: grid gaps 20 (compete.css 8-9), card-head 14 (10), `.row-act` 18 (22), `.foot-links` 16 (14), `.crow` 16x18 pad +
  8 gap (63-64), subnav 10/22 (compete-ui.js 133), `#recap` 20 (index.html 23), `.daily-status` 20 (52).
- C: QOTD is a whole card for one line + link (overview.js 227-241); Champions table (376-392) repeats Rankings; the
  Monday week line (280); `.chip-s` streak tooltip. D: side is already 340; it holds 6 cards (too tall to stick).

**Leaderboard** (leaderboard.js; inline style in its index.html 18-33)
- A: "where do I stand"; the youbar answers it. B: before row 1 at 1440x900: 27 + 60 + h1 40 + subnav 70 + 2 control
  rows ~96 + 20 + podium 156 (compete-ui.js 107) + path line 50 + find 52 = ~570px, so ~6 rows show. At 390:
  h1, subnav, sideways metric row, Filters button, 156px podium, path, find, then youbar and table.
- C: podium repeats rows 1-3; path line (262-272) repeats the youbar's "to pass"; "updated N s ago" (347).
- D: metric/period/scope/domain and Find belong in a 300px aside at 1280+.

**Your rankings** (rankings/index.html 64-76: 11 cards, one column; Rating | Pace in `.rk-grid2`)
- Reference tables always open: Seasons (1 row, "Final" always a placeholder, rankings.js 297-301), Level ladder
  (10 rows, 2 columns always placeholder, 314-321), Champions list. Badges grid repeats Me Achievements.
- D: Rating, Records, Rivals are context: aside. Main: Summary chart, Your ranks, Contest history.

**Contest page** (contest.js; inline style in contest/index.html 18-35)
- A: Start/Resume/See the board. Head is 6 rows before the state card (contest.js 116-137: back, kicker, h1 + chip,
  window line, day nav, day strip + info). In the lobby Start (240-259) follows ladder, facts, race row, timing row and
  helper text. Result: rank figure 56-84px (compete.css 117), 5 tiles, breakdown, strip, skills, mistakes, then actions.
- D: side is sticky from 960 (compete.css 218-220): good, keep. Rules open before a sitting, folded after: good.

**Help** (help/index.html): `.help-page` max 820 left-aligned (18), 220px dead at 1440; Shortcuts and Still stuck sit
at the very end; "Copy link to this answer" under every answer (94-95). /help is in FOLD_OFF (ui.js 2795).

**Sign in, Welcome, Pair**: 440 centred cards. Shell default puts the Now strip ("Up next ... Start") above them
(signin.js 18, welcome.js 15, pair/index.html inline `UI.shell('pair')`). Welcome copies Sign in's 13-rule style block
(welcome/index.html 17-29 = signin/index.html 17-29). Sign in tab "More" hides "Transfer code" (signin.js 21).

**Parent** (no shell): `.par-card`/`.par-tile` clone `.card`/`.stat` (parent/index.html 24, 27); h1 800/22; uses "-"
placeholders (the model). **Share /share/**: me.js read-only in the same 320 + 700 grid; meta line in mono.
**/s/**: kicker above every h1 (s/index.html 192-193, 323-324, 392-393), `.sx-help` wash well inside a card.
**404**: kicker "404 · not found" above the h1 (404.html 31); loads Source Serif with no question on the page (16).
**Admin** (low): student/students repeat one 40-line style block (index.html 16-52); uppercase mono `th` (32, 46).

## C. What FOLD_SEL catches here (ui.js 2792-2833)
- Folds (`.help` >= 70 chars, outside FOLD_SKIP): Settings intros 81, 334, 363, 374, 545, 588, 652, 654 (good);
  Me 381 (last week receipts), 970 (strike note); compete overview 291; contest 160 (exactly 70), 162, 232, 261,
  267, 935 (owner branch only).
- Wrongly folded 1: `UI.pop` is `div.popover[role=dialog]` (kit.js 571), FOLD_SKIP lists only the `dialog` tag, so
  70+ char `.help` inside popovers folds: me.js 244, 246 (board name), 299 (avatar), 571 (target), 659 (country), and
  every compete `C.info` text (compete-ui.js 944, `.help.pop-help`): an i tap opens a pop that holds another toggle.
- Wrongly folded 2: action inside `.help`: me.js 784 ("Today's set", the new student's one way in on Skills, 75 chars).
  contest.js 160-162: the comment says the extended-time consequence "stays in the open", but it is `.help` and folds.
- Not caught and long: me.js 418-421 (`.s`), `.line` facts (overview 65), `.rules`, `.sx-help`, `.par-lead`, `.wl-lead`.

## E. Redundancy (inside the page and with the shell)
- Streak: shell; Me You tile (me.js 334) + card-sum (210); Daily "N-day streak" chip = challenge streak (overview 51);
  Rankings "Streak" tile (rankings.js 50). Two different streaks, both just "streak".
- Exam date: shell; Me Goals row + bar (me.js 428-443); Snapshot "Sitting <date>" (616); Me prefs stage line (733) and
  the same line in Settings (settings.js 87-93); Settings study line (209).
- Today minutes: shell meter and Me Goals "Daily goal" meter (me.js 449-451).
- Week: This week card (356-386) and Goals' `weekRow` (454, 469-494) are two week widgets in adjacent cards.
- Prefs: Me Learning preferences paints 16 `prefRow`s (728-729) that Settings paints again (settings.js 51-55).
- Board name/visibility: Me board line + pop (212-248), Settings Boards block (343-383), contest name prompt (426-438).
- Sign out / save state: Me Account card (684-709), Settings "This device" (613-622), the account menu.
- QOTD: Today, Me Snapshot row (646-649), Compete card, contest side card (contest.js 938-963).
- Badges: Me Achievements, Compete Next badges (overview 410-426), Rankings Badges. Rivals: overview + Rankings +
  race select. Champions: overview + Rankings. Season card + Seasons table. Ranks: Me Snapshot (practice, 7 days),
  Compete stats tiles, Rankings Your ranks.
- Up next: the Now strip tops every page in scope and `.sections-next` repeats it once stuck; badge "Go" links point
  at `/` for it (overview 406, rankings 270); on Sign in, Welcome, Pair it is noise (I8).
- Me tiles vs cards: "Mistakes fixed · N open" tile (347) vs Saved "Open mistakes" (672); "fixes held" out (319).

## F. Local overrides, tokens, sizes, inline styles
- New button sizes (CLAUDE.md: never a new button style): compete.css 250 (`.pill` forced to 40px, pill.sm grows),
  177 (thumbbar pill 44), 254 (`.quiet` restyled 32px box); welcome `.wl-form .pill` 44px (welcome/index.html 31).
- Round buttons (radius 50%, under the 24px letter of the rule, against its spirit): `.help-q` 22px (me.css 218),
  `.av-edit` 26px (40). Neither has the 44px hit area (ui.css 819-820 covers only `.btn.sm, .ibtn, .x`); same for
  `.rowmenu`, `.view-tg button`, `.stepper button`, `.xbtn` (32px) and focusable 10px `.edot` (overview 448).
- Figures over the 32px scale: `.big-rank .num` 56-84 (compete.css 117), `.daily-rank .num` 40-56 (57), `.ct-count`
  34-52/800 mono (contest/index.html 22), `.final-band .num` 40 (124), `.rate-block .num` 36 (rankings html 25),
  `.big` 34/900 (me.css 170), `.cx-code` 44 (compete-ui.js 147) and 28 inline (contest.js 934), `.code-big` 30.
  Under the scale: 9px (`.lad .gi` compete.css 44, me.css 78, 130), 10px (`.dots7`), 10.5px (`.you-tag`).
- Mono on words: `.id-lines` (me.css 48), `.ladder`, `.dots7`, `.rd-n`, `.target-pop .total`, `.cx .mono`, `.crow .w`,
  `.mini-rows .mm`, `.youbar`, `.pod-s`, `.who-t`, `.dr-m`, `.pacer-l`, `.cx-sum`, `.path-line`, `.day-legend`,
  `.stepper`, `.sx-mix`, `.sx-st`, `.par-axis`, admin `th`.
- Uppercase: CSS `.you-tag` and `tr.sep` (compete-ui.js 77, 92), `/s/ .sx-code .field`, admin `th`. Typed in caps (the
  `.k` change will NOT fix these): overview 53, 234, 319, 339, 482; rankings 107, 111, 120, 412, 414; contest 82,
  112-113, 205, 296, 363, 373, 456, 471, 475, 627 (`toUpperCase` on a student's name), 742, 827, 940.
- Cards titled only by a kicker (12px soft after the shared change): overview `kline` cards (Season, This week, QOTD,
  recap), contest QOTD (941); they need an `.h2`.
- Kicker above an h1: contest head (116), join card (82), test-day card (471), /s/ (3 places), 404.
- Wells inside cards (card in card): `.out` (me.css 54), `.id-card .stat` (63), `.btile` (156), `.preview-q` (192),
  `.crow` (compete.css 63), `.lad` (41), `.stat-grid .stat` (75), `.res-tiles .stat` (120), `.bdg` (206), `.crv`
  (159), `.sx-help`. Wash cards: `.id-card` (me.css 37), `.card.wash` Daily (compete.css 28).
- Local clones: `.chip-s` (compete.css 19) duplicates `.badge`; `.cx .soft` = me.css `.soft`; `.help-q` vs compete `ⓘ`
  `.info-i` (compete.css 242): two different "explain this" controls; `.rowmenu` defined twice (compete-ui.js 80,
  rankings html 52, the second unscoped).
- me.css leaks generic global classes to 6 pages (me, settings, signin, welcome, pair, share): `.row .rows .gap .acts
  .soft .tag .list .dom .big .ladder .chk .odot`, a global `.card-foot` margin (133) and `.me * { min-width: 0 }` (5).
- Hardcoded colour: compete-ui.js 98 `rgba(30,30,30,.35)`. Gradient hack: `.youbar` (97); inline gradient legend
  (contest.js 910). Inline styles: me.js 16, settings.js 19 (7x `margin-top: 10px` on `.acts`), week.js 4,
  contest.js 4 (`margin:0` labels 194, 235), compete-ui.js 4, rankings.js 2.
- Bottom padding vs DIRECTION 48: `.me` 96 (me.css 4, also drops the phone safe-area calc of ui.css 392), `.cx` 120,
  and stacked on `.page.me`: `.set` 96, `.help-page` 96, `.si` 96, `.pair` 96 = ~192px of empty page end.
- Widths: 440 (signin, welcome, pair), 760 (parent), 780 (/s/), 820 (settings, help): two values would do.

## G. AI-slop tells
- Caps mono kickers on every compete card (list above). Mono for words (list above). Round "?" chips on 11 Me cards.
- Glyph soup in labels: `▲ ▼ ▸ ▾ › ‹ ⓘ ✓ ✕ ≈ →` ("More ▾", "Share ▾", "See it ›", "Hall of champions ›",
  "+ Create a contest"). Pick words or one chevron icon.
- Equal tile grids everywhere: Me 8 tiles, Compete stats, Rankings summary 6, Records, contest result 5, parent 6.
- Count-stuffed button labels: "Pacing drill · 11 q · 17 min", "Sharpen · 12 questions · ~19 min", "Trap gauntlet · 10".
- Chatty titles: "What keeps catching you", "Points on the table", "Your first contest fills this page".

## H. Copy
- me.js 379 "They show on your Profile item as you go." (unclear) -> "They show here as you go."
- me.js 315-316 "≈ 120 points on the table · your top 3 hold 60" -> "About 120 points to gain, 60 in your top 3 skills".
- me.js 635 "You, 14 days ago: ..." -> "Last 14 days: ...". me.js 810 "N skills under five answers · five answers each
  show their points" -> "N skills with under 5 answers". me.js 571 roadmap talk ("R&W practice comes later"): cut.
- settings.js 81 explains the UI (Help/tooltip); 86 "Back to stage" -> "Use stage defaults"; 588 "On, Students on
  this device shows in the menu" -> "When on, the menu lists up to four students on this device".
- Streak names: "challenge streak" on Compete and Rankings, "study streak" on Me.
- Badge rows say only "Go" (overview 420, rankings 284); the real label is in a tooltip, invisible on touch.
- signin.js 21 tab "More" -> "Transfer code". leaderboard.js 347 "updated 12 s ago" -> "Updated 12 s ago".
- rankings.js 34 "Your first contest fills this page" -> "No contests yet".

## I. CSS / layout bugs
1. `edot` class built without a space: `edot${'done'}` = "edotdone" (overview.js 448, contest.js 908). Finished and
   in-progress entrant dots get no rule and collapse to nothing; only "not yet" shows. Fix: `edot ${...}`.
2. compete.css 256 redeclares `.crow` columns after the phone rule at 229 (same specificity, later wins): phones keep
   4 columns; a row without a status chip pushes its "›" to a second line under the title. `.crow .act` (69-70, 232)
   is dead: `crow()` emits `.st` and `.chev` only. `.crow:hover` (258) is not behind a hover media query.
3. FOLD in popovers and `.help` with an action (section C).
4. leaderboard.js 345 links `/me/#boards`; me.js has no `#boards` card and no alias (1199). Use `/me/settings/#account`.
5. Likely overlap, check in a browser: `.youbar.stuck` top 72px z 5 (compete-ui.js 98) vs the phone section bar
   sticky at 56px z 20 whenever it carries Up next.
6. rankings.js 291 no-op (`$('#badges').id = 'badges'`); rankings html 47 rotates the whole `.xbtn` (focus ring too).
7. The em dash placeholder (U+2014) is the empty value: compete-ui.js 49, 274, 458 (every board), rankings 19 hits,
   /s/ 11, overview 3, contest 2, admin 5; me.js 1098 compares against it (from `UI.date`).
8. Sign in, Welcome and Pair show the Now strip (Up next + Start) above the sign-in card.

## Redesign proposals (ranked; risk in brackets; BIG = tell the user)
1. Bugs I1-I4 + I6: edot space, `.crow` rule merge (compete.css 63 + 229, drop 256 and dead `.act`), `/me/#boards`,
   `data-nofold` on contest.js 159-162 and the five Me pop `.help`s, move the me.js 784 button to a `.card-foot`. [low]
2. Caps literals to sentence case and kicker-only cards to `.h2` titles (F list); `C.info` text stays. [low]
3. BIG. Me Learning preferences card -> one row "Practice and test defaults" + "All settings" (me.js 723-742). Every
   key survives on Settings (settings.js 51-55, which already holds a superset). Section chips 16 -> 15.
4. BIG. Me layout flip: `me.css 6` to `minmax(0,1fr) 300px`, colL becomes the aside (later `.split`). Aside: You
   (compact), Goals, Snapshot, Saved, Account, Badges. Main: This week, Skills, Readiness, Trend, Pace, Catching,
   Habits, Activity, Recent. Change `col` in me.js 63-80 so desktop order matches phone `--o`. Recheck the Skills
   column rules tuned for ~570px (me.css 240-248). [medium]
5. BIG. Me analytics start collapsed (Snapshot, Trend, Pace, Catching, Habits, Activity) through the existing
   `satf.me.collapsed` (me.js 84-86, as Recent does); `card-sum` keeps the one-line answer; a click restores. [low]
6. Me one pill: amber only for the unsaved account's save, else This week "Start the first"; the others -> `.btn.sm`
   (me.js list in A). [low]
7. Me merges: Goals `weekRow` into This week; Catching + Habits -> one "Mistakes" card (two lists); Activity +
   Recent -> one card (heatmap, then feed). 16 chips -> 12, one row at 1040. All content kept. BIG. [medium]
8. You card: 4 tiles open (Answered, Accuracy, Study time, Mistakes fixed), the rest behind "More stats"; Streak tile
   folds (shell shows it); at 390 the card drops to ~450px. [low]
9. BIG. Compete overview: QOTD card -> one row in the Daily card foot; Champions card leaves the overview (Rankings
   keeps the list; first add the band winners line from overview.js 388 to rankings.js 310-311); Next badges -> aside;
   Join/Create only in the header (phone "Join or create" sheet already covers it). [medium]
10. Compete header: subnav into the h1 row as tabs (compete index/leaderboard/rankings html; compete-ui.js 405-409),
    saves ~60px on 3 pages. [low]
11. Contest lobby: Start right under the ladder; Race and Timing become one "Options" row (contest.js 185-198,
    149-164, 240-259); head 6 rows -> 3 (kicker and window line into one meta line; day strip into the aside at 960+,
    its legend stays in the i). [medium]
12. Leaderboard: controls + Find into a 300px aside at 1280+; podium heights 156/132/116 -> ~96/84/76 and its number
    to 32px (compete-ui.js 106-111); path line folds into the youbar text. Table starts ~250px higher. [medium]
13. BIG. Rankings on `.split`: main Summary, Your ranks, History; aside Rating, Records, Rivals; Badges, Seasons,
    Champions, Level ladder as collapsed cards. Hide the ladder's 2 empty columns and Seasons' "Final" until data. [medium]
14. Figures to the scale: big rank 84 -> 40, Daily rank 56 -> 32, `.ct-count`, `.cx-code`, `.big` (F list). The hero
    rank after a contest is a judgement call: ask the user before shrinking it below 40. [low]
15. Remove local button overrides (compete.css 177, 250, 254; welcome 31); `.help-q` and `.av-edit` -> square `.ibtn`
    28px with the shared hit area; one "explain" control (keep `C.info`, rebuild `helpBtn` on it). [low]
16. Wells to hairline rows: `.crow` list, `.out`, `.stat-grid`/`.res-tiles`/`.id-card .stat`, `.btile`, `.bdg`. [medium,
    visual only]
17. Settings: Practice shows the 10 keys Me used (me.js 728) + test keys open; the other ~25 under "More practice
    options (N)" `details`. Aside at 1280+: section index + "Saved · 2 ways to sign in". BIG. [medium]
18. Help on `.split`: aside = group index (from `groups`), Still stuck, Shortcuts; "Copy link" via `.reveal`. [low]
19. Sign in / Welcome / Pair: `UI.shell({ page, now: false })`; move the shared `.si` block to me.css; tab label. [low]
20. Empty values: em dash placeholders -> blank cell or "-" (I7 list). Inline styles -> classes (`.acts.mt` etc). [low]
21. Bottom padding: drop `.set`, `.help-page`, `.si`, `.pair` bottoms; `.me`/`.cx` to the token. [low]
22. 404: no kicker, no Source Serif. /s/: kicker -> meta under the h1. Admin: one shared style block. [low]

## Shared asks (lead only)
- ui.js 2793 FOLD_SKIP: add `.popover, [role=dialog]` (fixes every pop in one place; then drop the page nofolds).
- `UI.date` returns the em dash placeholder (me.js 1098 depends): return "" and let callers decide.
- ui.css 819-820: extend the 44px hit area to `.ibtn`-like 22-32px controls, or give pages one class for it.
- `.split` + sticky aside with `max-height` and `overflow-y: auto` (model: compete.css 219) for Me, Rankings, Help.
- `.reveal`: board `.rowmenu` already does it locally (compete-ui.js 82-87): promote that pattern.
- `.choices` first label flush: removes the -9px hacks (compete.css 149, 193; compete-ui.js 133; leaderboard html 27).
- `.meta`, `.stat-k`, `.stat-v`, `.k` to Geist sentence case (shared audit); scope files only fix typed caps.
- Left nav sub-items for Compete (Overview, Leaderboard, Your rankings) and Settings sections, if the shell allows.
- me.css generic classes and the global `.card-foot` override leak into 6 pages: scope them under `.me` or move the
  genuinely shared ones (`.rows/.row`, `.acts`, `.gap`) into ui.css.
