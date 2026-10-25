# Pass: Profile, Settings, Compete and the small pages (2026-10-19)

Audit: [../audit/me-compete-misc.md](../audit/me-compete-misc.md). Files: web/me/** (me.css, me.js, account.js,
settings/*), web/help, web/signin, web/welcome, web/pair, web/share, web/compete/** + assets/compete-ui.js,
web/parent, web/s, web/404.html, web/admin/** (new web/admin/admin.css). week.js untouched. help/answers.json gained
one sentence (the Practice intro moved there).

## First screen

**Profile /me/** (1440x900: section bar, then main 728 + aside 300)
- Leads with This week in the main column: up to three goals with meters and the one orange "Start the first"
  ("Plan your week" when there are none). Skills follows. The aside starts with a compact You card: 56px avatar,
  name as the h1, board line, outcome rows, four tiles (Answered, First-try accuracy, Study time, Mistakes fixed).
- Moved out of the way: Streak, Tests, Words and Rating tiles behind "More stats (N)"; Snapshot, Score trend, Pace,
  Mistakes and Activity start folded (once per device) and show their one-line answer; Learning preferences is
  one row in Account; the weekly study-days row moved from Goals into This week; Habits sits inside Mistakes,
  Recent inside Activity. Section chips 16 -> 12 (one row).
- 390x844: You card (~450px, was ~750) then This week; the rest follows in the old phone order.

**Settings** (1440: main 728, aside 300 from 1280px)
- Leads with the h1 and Practice: the 7 practice keys and 6 test keys Profile used to show; the other 18 and 5
  wait under "More practice options (18)" / "More test options (5)". The aside lists the six sections with their
  state (stage, "Saved · 2 ways to sign in", "1 new reply").
- Moved: the Practice intro sentence went to Help (the "?" on Practice opens it). Below 1280 the aside hides (the
  section bar is the index). 390: unchanged order, Practice is shorter.

**Help** (1440: answers in main, aside 300)
- Leads with the h1, search, then the answer groups. Still stuck (Send feedback) and Keyboard shortcuts moved from
  the page end into the aside; below 1280 they follow the answers as before. "Copy link to this answer" shows on
  hover or focus (always on touch).

**Sign in, Welcome, Pair**: the centred card is the first thing; no Now strip above it (`now: false`).
Sign in's fourth tab reads "Transfer code" (was "More").

**Shared view /share/**: same composition as Profile, read-only (no Pace, Badges, Saved, Account).

**Compete overview** (1440: main + 300 aside)
- A header row: the title, the Overview / Leaderboard / Your rankings tabs, then Join with a code and Create a
  contest. The Daily Challenge card leads: title with the date, a challenge-streak badge, "Next one in", one facts
  line, then **Start the challenge** (the only orange), then the 10-question ladder; its foot holds who has sat it
  and a one-row question of the day. Contests follow. The aside holds Your stats (rows), Rivals, Season, This
  week, Next badges and Private.
- Moved out of the way: the QOTD card, the Champions card, the Daily card's orange wash, the duplicate Join/Create.
- 390: title and "Join or create" on row 1, tabs under them; Start lands about 200px down (was about 560).

**Leaderboard**: tabs on the title row; main has a smaller podium (about 120px, was 156), the You strip (now also
the points to the top 10 and the podium) and the table, which starts about 250px higher. Metric, period, who and
Find are in the aside. 390: controls first (metrics scroll sideways, the Filters sheet unchanged), podium, You
strip, table; the separate path line is gone.

**Your rankings**: main = Summary, Your ranks, Pace, Contest history. Aside = Rating (its Practise button is the
one orange), Records and Rivals as rows, then Badges, Seasons, Champions and Level ladder, folded. 390: one column
in that order, the four reference cards last and folded.

**Contest**: the head is 3 rows (was 6): back link; title with a status badge; one meta row (kind, window, the
Daily's day buttons). The day strip moved to a "Your days" side card. Lobby: ladder, then **Start** right under
it, the facts, one Options row (Race, Rush domain, Your time), then the notes. Result: the rank is 44px (was 84),
the tiles are hairline columns, See the board is a small pill.

**Parent** (no shell): leads with the child's name, "Last active", then one This week card (questions this week
with the change, days practised N / 7, the 14-day bars). Accuracy, time, streak and tests are a quiet figure row
under it (was six equal tiles); the old Last 14 days card merged into This week. 1440 fits down to Doing well /
Needs attention; 390 fits the This week card.

**/s/** (a shared set): leads with the title, one meta line (kind · from · date · taken by N), the description,
the show-my-name box and Start (the only orange button). Stats, difficulty mix and topic chips moved below Start.
390: title to Start all in the first screen. Owner and word-list views: the kicker above the h1 is gone.

**404**: the h1, "404 · /typed/path" as meta under it, Today (the orange pill) and Practice.

**Admin** (low): same layout, shared card padding and hairline, sentence-case table heads.

## Big changes

- Profile: Learning preferences is now one row ("Practice and test defaults" + All settings) in the Account card.
  Every preference stays in Settings › Practice (it always held all of them).
- Profile: the columns flipped. The work and the charts (This week, Skills, Readiness, Score trend, Pace, Mistakes,
  Activity) take the wide column; You, Goals, Snapshot, Achievements, Saved and Account sit in the right column
  from 1280px. Below 1280 it is one column in the phone order.
- Profile: Snapshot, Score trend, Pace, Mistakes and Activity start folded once per device, each with its one-line
  summary; opening one keeps it open.
- Profile merges: Goals' weekly study-days row moved into This week; "What keeps catching you" and "Your habits"
  are one Mistakes card (two lists); Activity and Recent activity are one card (heatmap, then the feed). Old links
  (#habits, #recent, #preferences, #prefs) still land.
- Profile: the You card shows four tiles; Streak, Tests, Words and Rating are behind "More stats".
- Profile: one orange button: "Start the first" (or "Plan your week"); the unsaved account's save stays orange.
  Resume, Build my plan, Practise the top 3, Practise my biggest gaps, Timed set and Pacing drill are plain buttons.
- Settings: an index of its six sections in a right column from 1280px; Practice shows 13 rows open, the other 23
  behind two "More ... options" folds.
- Help: Still stuck and Keyboard shortcuts moved to a right column from 1280px.
- Sign in, Welcome and Pair no longer show the Up next strip.
- Compete overview: the question of the day is one row at the foot of the Daily card; Champions left the overview
  (Your rankings keeps them, now with the band winners line); Next badges moved to the side column and each says
  where it goes instead of "Go"; Join and Create only in the header ("Join or create" on a phone); an empty
  Private card hides itself; the Daily card lost its orange wash.
- All three Compete pages use the right column, with the tabs on the title row; Leaderboard's controls and Find
  moved there.
- Your rankings: Summary, ranks and history in main; Rating, Records, Rivals in the side; Badges, Seasons,
  Champions and Level ladder start folded and remember being opened (#champions and the overview's All badges
  open theirs).
- Contest lobby: Start sits right under the questions; Race, Domain and timing are one Options row.
- Compete lists are rows with hairlines instead of grey tiles (contests, stats, badges, review list, ladder).
- Parent: "This week" is the one focal card; the all-time totals became a quiet figure row.
- /s/: Start comes right after the title and description; the set's facts moved below it.

## Bugs fixed

- `/me/#boards` (leaderboard.js, contest.js "Set a country") pointed at nothing: both now go to
  `/me/settings/#account`; me.js also aliases `#boards` to the You card for anything else that sends it.
- `/me/#atlas` (results, tests), `/me/#route` and `/me/#points-<topic>` (server plan.py), `/me/?tab=week` and
  `/me/?tab=settings` (server) pointed at nothing; they now land on Readiness, Goals, Skills, This week and Settings.
- Entrant status dots got the class "edotdone" (overview.js, contest.js): now `edot done`, so finished and
  in-progress dots draw; the half dot no longer uses a gradient.
- compete.css: the two `.crow` rules merged (the later one undid the phone layout), dead `.crow .act` removed,
  `.crow:hover` behind a hover query; on a phone the status goes under the title.
- rankings: the no-op `#badges` id line removed; the history expand button rotates only its chevron.
- The leaderboard You strip no longer slides under the section bar when it sticks; its hardcoded colour and
  gradient are gone.
- Contest: the extended-time warning stays open (`data-nofold`).
- About 25 all-caps labels typed in compete JS are sentence case (including the `toUpperCase` on a student's name
  in Compare); the code inputs keep their caps. Kicker-only cards got real titles; kickers above h1s became meta.
- Glyphs out of button labels ("More ▾", "Share ▾", "+ Create a contest", the "… ›" links); "Updated", "No contests
  yet", "challenge streak" on Compete and Rankings.
- "Today's set" on an empty Skills card: verified the shared layer no longer folds a box holding a button, and
  moved it to the card foot anyway.
- Popover folding: no `data-nofold` workarounds existed in these files, so nothing to remove.
- me.css generic classes no longer leak: `.row .rows .tag .list .lrow .dom .big .ladder`, the `.me *` min-width,
  `.me p`, the card-head and fold rules are scoped to `.me-grid` (Profile and the shared view) or `.ach-list`
  (the badges sheet); the global `.card-foot` and `.field-err` overrides are gone (ui.css owns them). Only the
  helpers the seven account pages share (`.soft .gap .acts .odot .chk .sub-h .code-big .pop-form .country
  .help-q`) stay global, because their sheets and popovers sit outside main.
- me.js 1098 compared dates against the em dash; it uses `UI.NONE` now.
- Bottom padding: `.me` 96, `.set` 96, `.help-page` 96, `.si` 96, `.pair` 96 removed (the page's 48 holds).
- Pair: the "This browser has no progress yet" warning no longer folds (`data-nofold`).
- Parent / /s/ / 404 / admin: em dash placeholders are en dashes; kickers above h1s gone; iOS zoom on the /s/
  link field and the admin filters (font under 16px) fixed; admin row hover only on hover devices.

## Not done

- One "explain" control (audit 15: rebuild `helpBtn` on `C.info`): `C.info` lives in compete-ui.js, which Profile
  and Settings do not load. The "?" stays, restyled as a 24px square `.ibtn` with the shared hit area.
- Help's aside has no group index: the section bar already lists the groups (one source).
- Settings keeps both the section bar and the aside index from 1280px: the bar is the shell's (it also carries Up
  next when stuck); hiding it is a shell decision.
- Profile with an unsaved account and open goals shows two orange buttons (Start the first, and Save in Account at
  the end of the aside, out of the first screen). The audit allows either; both kept.
- `.id-card` link tiles (`a.stat`) keep their 16px inner padding while plain tiles sit flush (shared `.stat`
  rule): left edges differ by 16px inside the You card. Shared ask below.
- Parent and admin activity bars: a day's count is still only in a hover tooltip (as before); needs a tap readout.
- 404 keeps the Now strip: Up next is a useful way out of a dead link.
- Admin reports' raw context dump stays mono (raw keys and values count as code).
- Help's "Shortcuts" section chip targets `#keys-card`, which sits in the sticky aside from 1280px; the chip still
  scrolls to it, but the aside scrolls inside itself. Kept the chip because below 1280 the card is at the page end.
- Compete: the Daily's ‹ › day buttons and "‹ Compete" keep their arrows (direction controls).
- Compete: the level ladder's two always-empty columns and Seasons' "Final" are hidden until the server sends them.
- Compete: the -9px `.choices` alignment hacks stay (the fix is shared, below).
- Compete: "Your row" keeps its orange tint and edge (the app-wide marker for your own row).
- Compete: the folded rankings cards have no one-line summary (nothing worth a line).

## Shared asks

- ui.css `:where(.card, .panel) .stat:not(button):not(a)` drops fill and inline padding, but `a.stat` / `button.stat`
  in a card keep `padding: 12px 16px`: give them `padding-inline: 0` (or a hover inset) so a tile row shares one
  left edge (Profile You card, any card with mixed link and plain tiles).
- `.help-q` (account.js `UI.acct.helpBtn`) and compete's `.info-i` are two "explain" controls; if the lead wants one,
  a shared `UI.help(id, anchor)` (the hook helpBtn already calls when present) would let both pages drop theirs.
- ui.css: make the first `.choices` label sit flush, so `.board-ctl .choices`, `.lb-ctl .choices` and the phone
  `.subnav` can drop `margin-left: -9px`.
- ui.css: `.card[data-collapsed] .card-fold svg { transform: rotate(-90deg) }` assumes a down chevron, but
  `UI.ICON.chev` points right. me.css and compete.css both override it (rotate 90deg when open, none when folded);
  make that the shared rule.
- ui.css: `.stat-k` / `.stat-v` to Geist sentence case (planned); the compete tiles rely on it.
- A shared sticky-chrome height token: `--bar` (64px) has no desktop top bar behind it, yet compete-ui.js
  `.board-t tr { scroll-margin-top: calc(var(--bar) + 72px) }` uses it, and the You strip hardcodes 60px / 108px.
  Me, Settings and Help set `--twocol-top: 60px` for the same reason (the section bar's height).
- Optional: `.sx-help` into `FOLD_SEL` (it holds the sharer's own words, left open for now).
- Optional: `.reveal` currently needs the element's direct parent to be hovered; Help's copy link works, but a
  `.reveal-host` ancestor hook would let deeper rows use it.

## For the user

- The post-contest rank is 44px (the scale's largest step); it was 84px. Keep it there?
- Compete: the Daily card is a plain card now, its Start the page's only orange; Your rankings' four reference
  cards start folded. OK?

- Profile now opens on This week and Skills with your profile card on the right; Snapshot, Score trend, Pace,
  Mistakes and Activity start folded. OK?
- Learning preferences left the Profile page (one row and All settings remain). OK?
- Parent page: six tiles became one "This week" card plus a quiet row of four totals. OK?
- /s/: the set's stats now sit below the Start button. OK?

## Polish round

Files: web/me/account.js, me.js, me.css, week.js, settings/settings.js; web/assets/compete-ui.js; web/compete/compete.css,
index.html, overview.js, contest/contest.js; web/help/index.html; web/s/index.html; web/parent/index.html, parent.js;
web/admin/admin.css, admin/student/index.html. Leaderboard and rankings changed only through compete-ui.js.

### First screen

- **Profile**: the "?" beside card and part titles is the shared `UI.why` (named "About Goals", opens the Help answer,
  More in Help). Activity's heatmap readout is checked: under the grid it names the latest active day ("Fri, Oct 16 · 15
  questions · 20 min · 9 right"), the hovered, focused or tapped day replaces it; `.heat-stats` stays under it. Recent:
  each session is one row, the title (its link) and the result ("7 / 10") in a right-hand slot, what it changed under
  it, Again and Follow up beside that on hover or focus (always on touch); the kind icon and the duplicate chevron link
  are gone. The board-name pop's Save says Saving, then Saved, in place; the pop stays open to show it and the You card
  repaints when it closes (a shell refresh skips that card while a pop in it is open, so the pop never loses its
  anchor; this also fixes the round-one seg path); focus goes back to the new Change button. More stats' summary is on the 14px control step.
- **Your week sheet** (Profile › This week): the goal options are `.choice-row` rows (wash and amber edge when picked);
  with three picked the rest dim and stay disabled.
- **Settings**: Your name and Board name Save say Saving, Saved in place; the "Boards show ..." line updates without
  repainting the block. Copy (transfer code), Copy (tutor link) and Copy link (parent invite) say Copied in place.
- **Compete overview**: 8 cards became 3 surfaces: the Daily card (the focal card, its Start the one orange), the
  Contests list, and one side card holding Your stats, Rivals, Season, This week, Next badges and Private as parts split
  by hairlines (part titles 14.5/600). Every id stays. Copy link (private rows) and Copy recap say Copied in place.
- **Contest**: when the 30 s live poll moves your rank, the result's rank rolls to it (`UI.roll`) and "of N" and Top %
  update in place; never on load, never on a scope switch. The countdown (`.ct-count`) was already 28/600 tabular: kept.
  The owner card's Copy link and Copy code say Copied. The Create sheet's "Questions for each student", "Show answers"
  and Papers are `.choice-row` radios; its Copy code and Copy link say Copied.
- **All four Compete pages**: every ⓘ is the shared "?" (`UI.why`, anchored, "About the clock" and so on).
- **Leaderboard**: unchanged on purpose: `.table` with `tr.you` (ui.css wash plus the 3px amber edge), the podium's
  `.pod.you` and the You strip mark yours in orange. Only its two explainers changed (UI.why).
- **Parent**: the 14 bars name a day in the axis row, between the first and last dates, on hover or tap; at rest the
  14-day total ("35 in 14 days", in EN, UZ and RU). The bars' label now lists every day for screen readers.
- **Admin student**: the 30-day bars get the same readout ("Oct 12, 2026: 14 answered, 9 right"; at rest the total).
- **Help, /s/**: Copy link says Copied in place.

### New components added

- `UI.why`: `UI.acct.helpBtn` is now a thin wrapper over it (me.js 10 card and part "?", settings.js 5 section "?");
  `UI.compete.info` is a one-line wrapper over it (13 callers on 4 pages). Replaced `.help-q` and `.info-i`.
- `UI.saving`: Profile board-name Save; Settings Your name and Board name Save; Copy buttons in Settings (3), Help,
  /s/, Compete (owner card 2, create sheet 2, private rows, recap). Compete calls it through a new
  `UI.compete.copy(button, text)`. Replaced the Boards "Saved" span and the copy toasts.
- `UI.roll`: the contest result's rank on the live poll.
- Heatmap readout: probed on Profile (jsdom with fixtures: the line is there, `data-nofold`); the shared view runs the same call.
- `.choice-row`: the week sheet's goal checkboxes, the create sheet's radios (replaced `.cx-radio label` styling).
- The readout line (local, same pattern): parent and admin activity bars (replaced the bars' hover-only titles on
  parent; admin keeps its titles too).

### Removed local copies

- me.css `.help-q`, `.help-pop`; account.js's own popover and the dead `UI.help` branch.
- compete.css `.quiet.info-i`, `.quiet:not(.info-i) + .info-i`, `.pop-help` (one rule left: `.quiet + .why-q` keeps
  the "?" clear of a quiet button's hover box).
- settings.js Boards' local `.pref-state` "Saved" span (UI.saving says it, in place and in the live region).
- me.js `FEED_ICON` and the feed's aria-hidden chevron link (me.css `.feed-go`).
- compete-ui.js `.cx-radio label` styling.
- Grep of web/ for help-q, help-pop, info-i, pop-help, feed-go, FEED_ICON: nothing left.

### Not done

- Daily and Contests stay two surfaces: the Daily card is the focal point, and an unboxed Contests list would sit 16px
  left of the card's text (no shared left edge).
- Leaderboard names stay 600 (DIRECTION 9: titles stay 600).
- Profile's target pop keeps its toast: it carries Undo. The avatar picker, the "Show me on boards" seg and other
  instant saves keep their toast: there is no Save button to speak in.
- Menu items (Copy result, Copy a race link) keep the toast: the menu closes on the pick. "Copy the feed link" in the
  calendar sheet keeps its toast: it asks the server for the link first.
- The contest result's first-view rank reveal (once per sitting, C21, off under reduced motion) stays: a round-one
  function.
- `.ct-count` tracking stays -.02em (DIRECTION's figure step), not INSPO 6.6's -.03em.
- Sign in's "This is a shared computer" stays a checkbox: one yes/no, not a row choice.
- Smoke runs: the default fixtures still make /me/, Settings, Compete and Rankings throw the same pre-existing errors
  as before my edits (fixture shapes). Checked instead with my own fixtures: Profile (readout, feed rows, 10 "?"),
  Settings (Saving and Copying states), Compete overview (one side card, six parts), Contest (the rank went #2 to #3 on
  the poll), Parent (readout and label). No new errors.

### Shared asks

- ui.css: a `label.choice-row:has(input:disabled)` state; the week sheet sets `aria-disabled` on the label for the look.
- kit.js: `UI.copyText(text, {button})` that runs `UI.saving` on the button with Copying / Copied; settings.js,
  compete-ui.js (`UI.compete.copy`), help and /s/ each carry the same two lines today.
- charts.js: a small bars chart with the readout built in; parent and admin carry it locally.

### For the user

- Compete overview: the six side cards are one card now (Your stats, Rivals, Season, This week, Next badges, Private). OK?
- Profile › Recent: Again and Follow up show on hover (always on a phone), and the kind icon left each row. OK?
- Profile's board-name pop stays open after Save so you see Saved; it closes on Esc or a click outside. OK?

## Premium build (part 1)

Brief: premium/PAGE-BUILD-BRIEF.md, steps 1, 2, 6 and 7 (calm first screen, the hero, open bugs, the Per page and More
items that need no new shared JS). Files: web/me/me.css, me.js, week.js, settings/settings.js; web/signin/index.html,
signin.js; web/welcome/index.html, welcome.js; web/pair/index.html; web/help/index.html; web/share/index.html;
web/s/index.html; web/parent/index.html, parent.js; web/404.html; web/admin/admin.css, admin/reports/index.html;
web/compete/** and web/assets/compete-ui.js (listed under Compete). week.js changed (one option); account.js did not.

### The lead's two fixes first (user feedback)

- Yours rows: the same height as every row, a `--wash` tint, the rank in `--amber-deep`, the name 600; no side
  stripe, no check, no tag. Board (compete-ui.js, so Leaderboard, Contest, Challenge and every board): the ui.css
  `tr.you` stripe is overridden in `.board-t`, the "You" badge became "(you)" after the name (inside the ellipsis, so
  the row cannot grow), the confirmed-answers ✓ mark no longer shows on your own row, the rank cell is amber-deep 600.
  The You strip: wash, no stripe; stuck it floats on `--shadow-2`. Podium: your pedestal is wash with an amber-deep
  rank, no ring. Mini rows (Compete side card, Rankings history): wash bleeding 8px past the text, no stripe, no
  "You" badge, rank amber-deep (rankings split the rank into its own span for that). Rankings' level ladder and any
  other `.cx .table tr.you`: no stripe, first cell amber-deep 600, "Level 5 (you)" says it in words. /s/ tables: the
  same (the small-pages pass).
- Focus: no ink rings. Removed `.board-t tr:focus-visible` ink outline (now ui.css's amber-deep), `.crow:focus-visible`
  ink outline, me.css `.dots7 .today` 2px ink ring (today is a 2px amber-deep bar under the dot now). The avatar
  picker's picked tile takes the one selected look (`--sel-bg` + `--sel-edge`) instead of an ink ring.
- A1's notes: Settings' index hover is `--hover`, not `--tile`; the Profile pencil key sits on `--face` with
  `--shadow-btn`; admin `.adm-tiles` gap is a local 16 (was `--card-gap`, now 32); admin report wells read `--well`.

### Sign in, Welcome, Pair

- First screen before (1440): the app sidebar with Up next's orange Start (`now: false` removed only the strip), then
  a 440px card: 32px mark beside the title, four tabs (plus Google when on), the method's panel with a 34px pill, the
  shared-computer box. Two oranges, 6 controls in the card.
- After: `nowBlock: false` on all three (bug 10: the sidebar's Start leaves; one orange). The card is the page's
  `.card.hero`, centred lower (clamp 8px to 72px from the top), the mark at 40 above the title. Sign in shows one way:
  the one `first` already picked (last used, else Passkey with a platform authenticator, else Use your phone), as one
  line and one full-width `.pill.wide`; Google under it in a fixed 44px slot; then "Other ways to sign in" (quiet,
  `aria-expanded`) opens all four ways as `.choice-row`s with a one-line meta (Face ID, Touch ID or Windows Hello;
  Scan a code on a signed-in phone; A 6-digit code by email; From a signed-in device), the current one
  `aria-current`; a pick switches the panel, sets the hash, folds the list and focuses the panel's first control.
  "This is a shared computer" stays last at 13px. Card controls 6 to 3 (pill, Other ways, the box), oranges 2 to 1.
- Kept: every way and hash (#passkey #phone #email #code, #pair is #phone), `tabs.set()` (the passkey and outbox
  panels' "Use your phone", "Passkey", "Transfer code" buttons still switch), the conditional passkey request, the
  phone code's clock and poll, the email link path, the signed-in panel, the tooltip on the shared box.
- Welcome: the Create account / Sign in seg is gone; under the button, "No password: ..." at 12.5px, then one line
  "Have an account? Sign in" (or "New here? Create an account"), "Continue without an account" last, 24px above.
  Mark 40. Controls 4 to 3.
- Pair: the same card (`.card.hero`, the mark at 40 over the title, centred), `nowBlock: false`, its Sign in is a
  full `.pill` and Not me a `.btn` (were `.sm`). The pair page's own card rules moved to me.css (`.si, .pair`).
- Not yet: the focus chrome (`UI.shell({ chrome: 'focus' })`, part 2 once BUILD.md documents it).

### Profile /me/ and the shared view /share/

- First screen before (1440): section bar; main: This week (goals with meters, a Weekly goal row with a meter and 7
  day dots, six "met" bars, the Last week receipts line, Start the first, Change goals); aside: the You card (56px
  avatar, name 22, three lines, three outcome rows, four tiles each with a sub, a delta and a sparkline, More stats).
  About 25 bars and marks, ~20 controls.
- After: a full-width identity plate above both columns, the page's one hero (`.card.hero` on `.me-plate`, 32px
  above the columns): the avatar at 72 (`.avatar.xl`) with its pencil, the name at 28 in `--ink-strong` with Edit,
  one wrapping meta line (board name and Change, studying since, saved), the outcomes as one line of figures (+40
  since you started, About 80 points to gain, 3 / 4 fixes held), and at the right a shelf of the last three badges
  earned (before any: the three closest, unlit) in the badge art with "2 of 35 · All badges", which opens the
  Achievements sheet. Under a hairline, the four figures as one row (2 x 2 on a phone): label and value at rest;
  the week, the change and the sparkline are `.reveal` (hover or focus, always on touch). In the plate: 5 buttons,
  3 links, no visible bars at rest.
- This week: the goals and Start stay (Start the first is now a full `.pill`, Plan your week too when there are no
  goals). The Weekly goal row (meter and 7 dots), the six met bars and the Last week line became one row, "Your week ·
  20m of 2h 30m studied · met 2 of the last 3 weeks · last week 80 answered" with a chevron, which opens the Your week
  sheet. The sheet (week.js, new `extra` option) now carries the study days (Weekly goal, the meter, the dots) and the
  weeks-met bars under Last week; Change goals opens the same sheet. Card: 4 buttons, 2 meters (the goals'). The
  shared view has no sheet: it shows the same summary as a meta line.
- Skills: Practise on the first row only at rest; every other row's Practise is `.reveal` (the row is a
  `.reveal-host`); the line under a skill (trend, last five, Fading, Keep warm, Try 5 more) shows with its row on
  hover or focus (me.css, the same rule as `.reveal`). No grey mastery bar on a skill with no answers ("Not
  started" says it). Domain lines read "40 of 60 right", the card's summary "Weakest X 12 / 20" (counts over
  percentages).
- Achievements keep their card (the shelf is the way in on the first screen; its `--o: 10` no longer hides them).
- Phone (390): the plate first (56px avatar, the shelf under the name, figures 2 x 2), then This week.
- Bug: the shared view printed "null" after the score ("520–580null": `append()` of a null in the Snapshot row);
  only real nodes go in now.
- With the plate outside the grid, a turned-off share link would have kept the plate's skeleton above "This link
  was turned off": share/index.html removes `.me-plate` there too (checked with a failing `/shared/` fixture). On a
  phone the avatar cell is 56 and the avatar fills it.

### Settings

- Four preferences open per group, the rest under the existing "More ... options" fold: Practice 7 to 4 (mode, set
  length, clock, difficulty), Tests 6 to 4 (timing, calculator, pace, full screen), Tools & display 12 to 4 (theme,
  text, motion, show timer; "More display options"), Study 6 to 4 (study time, remind, quiet hours, registered;
  "More study options"), Words 8 to 4 (goal, from, gloss, method; "More Words options"). Every key keeps its row;
  every anchor other pages use (#practice #display #study #account #devices #reports #report- #privacy) is a
  section or sits outside the folds. Open rows at 1440: 39 to 20. No hero, on purpose.
- The index stays in the aside from 1280px; hiding the section bar there is a shell option (Shared asks).

### Help

- Before: the h1, a bare search, seven group cards, and in the aside Still stuck and a 9-row shortcuts card.
- After: the h1 and the search sit in one `.card.hero` (the page is about finding an answer); the seven groups are
  one surface with a heading per group (ids `g-*` kept for the section bar, hidden when a search empties them; the
  whole list hides when nothing matches and "No question matches" shows). Shortcuts: "Press ? on any page for its
  shortcuts", the nine rows under "The main ones (9)" (a fold), All shortcuts on this page stays. Surfaces 8 + 2 to
  2 + 2.

### Parent, /s/, 404, admin

(The small-pages pass; details in "Files" above.)
- Parent: This week is the `.card.hero`, its number (questions this week) a `.hero-num` with one line under it
  (the change, "5 of 7 days practised"); the two equal tiles became that one figure. A static This week skeleton
  shows while `/account`, the children and the child load (the page was blank). "No student linked" is a lead line
  and three steps (Open Settings; Privacy and data, then Parents; Invite a parent), EN, UZ and RU. 14 empty bars
  and their axis become "0 in 14 days" when nothing was answered. `.par-week` (unused) removed.
- /s/: the set card (visitor, word-list visitor, sharer) is `.card.hero`; the dead `.rise` class is off all five
  cards (no rule existed); Resume and See how you compare are `.btn`, so Start is the only orange; the compare
  table's Everyone column reads "2 of 3 · 67%"; yours rows lose the stripe (amber-deep "You", 600, wash). Bug: the
  sharer's word list drew a second card and a second h1 inside the sharer's card; it appends only the list now.
  Link previews: og:site_name, og:type, og:title, og:description and twitter:card (summary) on /s/ (and on
  /share/), so links stop unfurling bare in Telegram; the 1200x630 image card is a later step.
- 404: centred about a fifth down under a large "404" in `--mat`; the path line shows only the path (hidden on a
  direct /404.html); `now: false` so the phone has one orange (Today). `#lost-h`, `#lost-path` kept.
- Admin: tiles and cards on `--raised` with `--shadow-1`; tiles 16 apart inside a group; no yours rows or ink rings.
- Share: "Live · shared by the student, it updates as they study" with a static amber dot; the plate above it.

### Compete (overview, Leaderboard, Your rankings, Contest)

- Overview, the Daily card before you sit it (1440): 15 controls, 7 text items, 40 ladder marks before; 14, 6 and 30
  after; the action row 3 buttons to 2. The Daily card is the page's `.card.hero`. Start is a full `.pill`; Warm up · 6
  (with its line as a sub), Past days, Daily reminder and Copy result (once finished) are one ⋯ menu (`UI.menu`).
  The streak badge is a flame and the count by the title (the full "N-day challenge streak · best M" in its label and
  tooltip). "Next one in" shows in the foot only after you finish (the countdown still runs, so the midnight reload
  holds). Ladder cells are inset wells on the page tone; the slot number left the cell (it stays in the label and
  tooltip, "Q3"); your chance is a 3px fill along the cell's foot. After finishing the rank is 44 (was 28) and See
  the board a full pill. The side card's This week choice (Points, Over expected, Climb) is one small "Board"
  dropdown. The question of the day reads "Right · 48 of 120 got it" (was "40% of 120"). A badge with no progress
  shows its rule and "0/7" with no grey bar (Your rankings too). Phone: `now: false`, so the Now strip's second
  orange leaves.
- Leaderboard, 1440: the same controls, one per line in the side column: the 7 metrics as rows under "Ranked by"
  (they wrapped on ~3 lines), the period one `UI.seg` (Week, Month, Season, Year, All; full names in the tooltip),
  the stepper and its resets line, Scope and Domain, Find. Under 1280 (phones too): ~16 controls above the podium
  became 1: a summary button on the title row ("Points · This week · Everyone", `#lb-sum`) opens a "Board" sheet
  with the same controls and Find (they go back to the column when it closes); `/` opens it and focuses Find; M, P,
  comma and full stop work as before. Metrics with no period (Skill rating, Climb) say why in one line instead of
  six greyed options. Hero: the podium as stepped pedestals 136 / 112 / 96 on white at the card shadow, #1 a step
  higher with its number at 28, yours the wash with an amber-deep number. The empty board's Start is a full pill.
- Your rankings: the Rating card is the hero, the level ring 64 (was 48), the rating at the hero size. "No contests
  yet" shows a dimmed example row (Contests, Accuracy, This week, "Example") and one line saying what fills in;
  Start today's challenge stays.
- Contest: the header is the back link, the title with its status badge, one meta line; the day steps (previous,
  pick a day, next) moved into the Your days card beside the strip (always shown on a Daily, "Other days" before
  your first sitting; 4th on a phone). Lobby: the state panel is the hero; Start, Resume and "Sit it now
  (unranked)" full pills, Warm up a `.btn`; Rules keep Points, Pace bonus and Ties open, the rest under "More rules ·
  N" (Rush and Words keep their first two). Bug 10, phone lobby: 3 oranges to 1 (`now: false`, the panel's own Start
  and Resume hidden on a phone where the thumb bar carries them). Result: the rank is the page's one number at
  `--fs-hero` with "of N" and Top % beside it; tiles 5 to 3 (Score, Points, Over expected); rating one line ("Rating
  +60 → 1,260 · Level 4 → 5"); race, par and rivals today one line, each part only when it says something; a
  Details fold holds Time, the right / wrong / skipped / voided line, Skills and Mistakes from this sitting (its
  summary shows the open-mistake count); See the board a full pill; the rank still rolls on the 30s poll.
- Bug: ui.css now sets the first underline choice flush, so compete.css's `-9px` alignment hacks were removed.
- Removed and unreferenced in web/: `.lb-fbtn`, `.lb-sheet`, `.mist-d`, `.you-tag`, `.lad .n`; `side-first` dropped
  from the leaderboard page only.

### Inventory diff, accounted for

Runs at 1440 and 390 against the snapshot taken before any edit (scratchpad mcm/before, mcm/after).
- Sign in: the four tab buttons are now four rows with their meta ("Passkey" + "Face ID, Touch ID or Windows Hello",
  and so on), plus "Other ways to sign in"; new ids `si-panel`, `si-ways`; the tabs' internal `ktab*` ids are gone
  with the tabs.
- Welcome: "Create account" (the seg's current option) left; the mode switch is the "Sign in" / "Create an account"
  line under the button.
- Pair: new `#mark`. Help: new `#help-h` (the hero's h1).
- Compete: Points, Over expected and Climb are options of the new "Board" dropdown.
- Leaderboard: "All time" reads "All" (tooltip and summary still say All time); "Filters · Everyone" became the
  summary button (`#lb-sum`); Scope and Domain sit in the column or the sheet.
- Challenge: a new "Start" comes from the challenge page's own builder (not these files); its fixture crash is gone
  for the same reason.
- With own fixtures (the default ones crash overview, rankings, Profile and Settings as before): every overview and
  contest control is still there (Start, Warm up · 6 in the menu, Change, the "?"s, See the board, Share, the day
  steps, More rules); Profile has every card, button and link it had; Settings has every pref row (8 open, the rest
  in the folds).
- Parent, /s/, 404, admin, share: identical.

### Checks

- `python3 tools/check-ui.py`: ok. `node --check` on every touched JS file and every inline script (pair, help, share,
  /s/, 404, admin, the compete pages): ok. No em dash in any touched file.
- Smoke, page.js at 1440 and 390 for the 17 pages: the same error lines as before (fixture shapes: Profile's PAINT.*,
  Settings' `listing.forEach`, Compete's `S.hub.daily`, Rankings' `S.me.records`), only their line numbers moved;
  every other page NO ERRORS.
- Own jsdom fixtures (scratchpad mcm/fxme, mcm/fx, mcm-compete): Profile at 1440 and 390 (the plate, the shelf, the
  reveals, one pill, the Your week sheet carrying the study days), the shared view (me.js inlined), Settings (folds
  per group), Sign in (one way, Other ways, a pick to Email code moves the hash, the panel and focus), Welcome, Pair,
  signed-in / zero / no-child Parent, the /s/ visitor, word-list and sharer views, Compete overview before and
  after a sitting, Leaderboard (the sheet takes and returns the controls), Rankings full and empty, the Contest lobby
  and result: no errors, except the result's first-view rank animation (unchanged code; jsdom has no
  `Element.animate`).

### Not done

- Focus chrome for Sign in, Welcome, Pair: part 2, once `UI.shell({ chrome: 'focus' })` is in BUILD.md.
- Hiding the section bar at 1280+ on Profile, Settings and Help until it sticks: the bar and its sticky logic are
  the shell's; a page rule would leave an empty row or shift the page when it sticks (Shared asks).
- Profile: the level ring by the name and an amber progress ring on the avatar (compete-ui.js is not loaded on
  /me/; the ring's meaning is undecided), the four mini meters on the living mark, the shelf's shine: part 2 or
  later. The plate keeps its fold (Collapse You stays reachable).
- No amber glow under podium #1 ("no glow, no halos" wins). The overview ladder stays visible (not behind "See the
  10 questions"); the page audit keeps it. "Clean run" stays a small grey badge inside Details.
- Contest grid view: your row keeps the bold name and "(you)" but no wash: its pinned name cell needs an opaque
  wash token.
- Every ✓ ✕ ▲ ▼ ‹ › and drawn icon (sign-in way icons, Settings index icons, the shelf's medal, closed-mistake
  checks, the made-up day cell), the spot drawings (404, Rankings' empty ring, Parent's no-student), the ghost
  podium and all motion: part 2.
- Parent's bar hover marker (a 1.5px ink ring on the day being read) is a reading mark, not focus: kept.
- Link previews have no image (a 1200x630 card and an absolute URL are a later step).

### Shared asks

- ui.css `.table tr.you > :first-child { box-shadow: inset 3px 0 0 var(--amber) }`: if any stripe is left there
  after A1, drop it; compete-ui.js, compete.css and /s/ override it locally until then.
- Challenge (not mine): `.ch-row.you` in challenge/index.html still draws `inset 2px 0 0 var(--amber)`.
- The shell: a `sections({ defer: true })` (or a page flag) that, at 1280+ where a twocol already shows the cards,
  renders the bar only once `.stuck`, without reserving its row (the negative margin it already uses with no
  chips). Profile, Settings and Help would pass it.
- `UI.seg` writes one help line per disabled option; one shared reason line would let the Leaderboard drop its
  workaround.
- smoke/page.js: stub `Element.prototype.animate` so first-view reveals stop reading as errors.
- An opaque wash token (`--wash-solid`) for pinned cells in a yours row.

### For the user

- Sign in now shows one way (the one this device used last) with "Other ways to sign in" under it, on a centred
  raised card without the sidebar's Start. OK?
- Profile opens on a full-width plate (your mark at 72, name, gains, your last three badges, four figures) above This
  week; the week's dots and bars moved into the Your week sheet. OK?
- Settings opens four settings per group, the rest one tap away. OK?
- The contest result's rank is now hero size (56 to 64px; it was 44, and 84 before that). OK?
- Below 1280px the Leaderboard's controls sit behind one "Points · This week · Everyone" button, so the podium
  leads. OK?
- The Daily's Warm up moved into the ⋯ menu beside Start. OK?
- 404 drops the phone's Up next strip (Today is its way back), and on a shared set you started, Resume is a plain
  button so Start is the only orange. OK?

## Premium build (part 2)

Brief steps 3, 4 and 5 on the phase A layer (BUILD.md "## Integration", "## A2 motion", A3's call sites; DEMO.md's
do / don't list). The lead's calls: Sign in shows one way plus "Other ways" (kept), the Profile plate above This week
(kept), the contest rank stays 44px (part 1's hero size undone). Files: web/me/me.css, me.js, index.html,
settings/index.html, settings/settings.js; web/signin/index.html, signin.js; web/welcome/index.html, welcome.js;
web/pair/index.html; web/help/index.html; web/share/index.html; web/assets/compete-ui.js and web/compete/** (Compete
below); web/parent/**, web/s/index.html, web/404.html, web/admin/** (small pages below).

### Sign in, Welcome, Pair

- The focus chrome: all three call `UI.shell({ ..., chrome: 'focus' })`: no sidebar, rail, tabs or Now strip; the
  slim brand bar (mark and wordmark home, Help, the account button with Students and Sign out). From 760px the card
  sits in the middle of the screen, a little above centre (`body.has-focus main.page`, me.css); on a phone it stays
  at the top, where the keyboard leaves it in view.
- Page entry: the card rises once per visit (`data-m="stagger"` on `.si` / `.pair`, the card `data-m-now`).
- Sign in: picking another way crossfades the panel in (`UI.motion.enter(panel, 'fade')`; a key switches at once).
- Code boxes (email code on Sign in and Welcome, the six digits on Pair): disabled while the code is checked, all
  six take the amber edge on a wash when it is right (`.otp.ok`, me.css: UI.otp has no success state), a 4px nudge
  and the dashed edge when it is wrong, focus back in the boxes.
- Pair: approving draws a large check in a wash disc above "Chrome on Mac is signing in now" (`UI.fx.check`); "Not
  me" ends with its line alone.

### Profile, Settings, Help, Share

- One badge style: me.js's 40 badge drawings and `.bcirc` moved to compete-ui.js as `UI.compete.badgeIcon(a,
  earned, {size})` and `UI.compete.BADGE_PATHS` (its CSS with them); /me/ and /share/ now load compete-ui.js. The
  two clichés are redrawn: Clean set (a sparkle) is a list with a check, Perfect (a gem) a check in a circle. Earned
  discs carry the pill's faint top light and a small warm contact shadow. Compete's badge rows draw the same art.
- Icons: me.js's local pencil became `UI.ICON.pen`; `ic()` draws nothing for an unknown name (was an orange dot,
  bug 3); a met goal's ✓ is the drawn check. Settings' index rows got icons (practice, settings, calendar, devices,
  chat, eyeoff). ▲ ▼ → ↑ ↓ × stay as text: Geist has them (ICONS.md); ✓ ✕ in text are the Marks font's.
- Motion: page entry on Profile and Share (the plate and the two columns; the column holding Start the first is
  never delayed; me.js sets the hook once the cards exist), Settings (the h1 and its sections) and Help (the search
  hero and the answers). A badge earned since this device last looked pops once on the shelf (`UI.fx.pop`, 60ms
  apart); a goal met since then draws its check once (`UI.fx.check`); the first visit only remembers
  (`satf.me.badges`, `satf.me.met`). Card folds now animate by themselves (A2); me.css's own fold-chevron rules
  went (ui.css carries them).
- Share: og:image (`https://prac.fsat.io/assets/og.png`, 1200x630) and `summary_large_image`.

### Compete

- The lead's calls: the contest result rank is back to 44px (`.big-rank .num`, so the poll's roll still works); the
  Leaderboard's sheet below 1280 and Warm up in the ⋯ menu stay. Your rankings' rating stays the page's hero number
  (`.hero-num`, BUILD rule 9; the 44px call was the contest rank's).
- Controls: the Daily's ⋯ is an `.ibtn` with `UI.icon('more')`, so are the board and rivals row menus; Starts set
  `aria-busy` (ui.css's spinner); the Leaderboard stepper and the contest day steps are `.btn.sm.icon` with
  caret_left / caret_right 18, labelled and with tooltips naming the day or period; back links ("Compete", "Back to
  the result", 5 places) lead with caret_left 16 in `.quiet`; the leaderboard table sits in one card (its empty state
  is no longer a card inside it). Contest rows take the shared hover band bleeding 8px and their chevron nudges 2px.
- Motion (off under reduced motion, no-ops without WAAPI): page entry on all four pages (main and side columns;
  `data-m-now` on the Daily and the contest's state panel). Contest result, once per sitting, replacing the 320ms
  fade: the rank rolls from the field size to your place (`UI.roll`), Top % pops, the three tiles rise 40ms apart,
  the rating line leads with the level ring (on a level change the old ring swaps to the new one with a pop), New
  best pops. `UI.board.update()` glides moved rows (keyed by pid): on the contest's 30s poll your row shows "Up N"
  once when you rise (inline, the row height holds); on a Leaderboard control change the old board stays
  (`aria-busy`) until the new rows land, then they glide, no "Up N". The podium rises 3, 2, 1, 60ms apart, on a
  metric, period or sort change, never on first draw. Jump to me glows your row. The You strip nudges in as it
  sticks. The overview's Contests filter and Rankings' history (sort, Show more) glide. The Daily's streak flame
  fills once a day after you finish.
- Icons: compete-ui.js's `SVG` map points at `UI.ICON` (`UI.compete.SVG` keeps its names, dots maps to more;
  `UI.compete.svg` still exported); contest.js's local `ICON` map is gone (the grid / list toggle draws `UI.icon`);
  ▲ ▼ moves became words through a new `UI.compete.moved(n)` ("Up 3" in Move columns, "up 3" in lines); Rankings'
  badge rows and the overview's Next badges draw `UI.compete.badgeIcon` at sm (the 8px amber dot is gone);
  Rankings' "No contests yet" is `UI.spotArt('start')`, one line and Start.

### Parent, /s/, 404, admin

- 404: `UI.spotArt('lost')` is the one figure (96px, 72 on a phone; the big "404" numeral went, two figures
  competed), the path line reads "404 · /path" (or "404 · not found"), the blocks rise once (`data-m-now` on the
  block holding Today).
- Parent: page entry on the first dashboard paint only (never on the skeleton, the sign-in view, the language
  switch or a child switch); the 14 bars rise from the baseline once per tab (`data-m="bar"`, `UI.motion.draw`,
  `UI.motion.once`), not when empty, not on a language switch; "No student linked" draws `UI.spotArt('start')`;
  og tags (title, description, image 1200x630, summary_large_image).
- /s/: page entry on the first real paint (the card holding Start never delayed); og:image and
  summary_large_image. No local icon map and no toggles there; ✓ ✕ in text are Marks'.
- Admin: ui.js now loads before kit.js on all three pages, so kit's icons draw again; `data-nofold` on `<main>`
  keeps the operator help text unfolded; ui.js adds only its skip link (`main#main`), the ? sheet and the flash
  toast there (no shell, so no G keys or Mod+K). Student's "All students" back link leads with caret_left 16.

### Inventory diff (part 2), accounted for

- Sign in, Welcome, Pair: the app sidebar and its controls (nav links, Collapse sidebar, Search, Quick, Send
  feedback, the menu, `#side-progress`, `#side-study`) and the "Have progress on another device?" banner's Dismiss
  are gone with the focus chrome; the bar keeps home (the mark), Help and the account menu (Students, Sign out), and
  G keys, Mod+K and ? still work.
- 404: new `#lost-art`. Admin: new `#main` (ui.js's skip link target). Challenge: its own builder's Start.
- Everything else is part 1's (accounted above).

### Checks (part 2)

- `python3 tools/check-ui.py`: ok. `node --check` on every touched JS and inline script: ok. No em dash in any
  touched file.
- Smoke at 1440 and 390, all 18 pages vs the pre-edit snapshot: the same error lines (Profile's, Settings',
  Compete's and Rankings' fixture gaps), every other page NO ERRORS; Challenge went from an error to NO ERRORS
  through its own builder.
- Own fixtures: Profile on a return visit (the badge pop and the goal check each played once, the page entry
  hook set and run), the Your week sheet, the shared view (and a turned-off link), Settings, Sign in / Welcome /
  Pair in the focus chrome (no sidebar, Now strip or tabs; one hero; the entry ran), Parent (signed in, no child),
  /s/ visitor, 404, admin student and reports, Compete overview new and finished, Leaderboard with its sheet, a
  board update with "Up 3", the contest lobby and result, Rankings full and empty: no errors.

### Not done (part 2)

- Sign-in way icons, the shelf's medal and a Settings privacy shield: the map has no key, envelope, fingerprint,
  shield or medal (Shared asks); the rows keep their one-line metas.
- Daily Start plus ⋯ as a `.split-btn`: the menu holds side jobs (Past days, Reminder, Copy result), not ways to
  start, so a split chevron would promise start variants.
- The level ring swaps and pops instead of sweeping: it is a gapped dash path, not a `.ring`.
- The Compete subnav underline does not slide between pages (needs head.js page transitions); `C.under` choices keep
  a static underline; the history kind filter reloads and rebuilds (no glide); no ghost podium (the podium already
  shows Open and par places); Copy result's grid preview.
- Profile tiles do not count up on load (BUILD rule 6: only a new score counts); no shine on the shelf (no
  shimmer); the living mark's four mini meters on hover; the Welcome mark's corner fill.
- Parent's weekly-email box saves at once (no Save button for `UI.saving`); Parent has no orange primary to mark
  `data-m-now`.
- jsdom has no `getClientRects`, so the page entry's rise itself is unverified there (the hook is set and marked
  done); the visual critic will see it.

### Shared asks (part 2)

- Icons: key (passkey), envelope (email code), fingerprint, shield (privacy), medal (podium, badges).
- ui.css: `body.has-focus #bar` paints `--paper`; A1's rule is `--page` for sticky bars.
- A `.ring`-compatible level badge so `UI.fx.ring` can sweep it.
- smoke/page.js: `dialog.close()` never fires `close` (a sheet's `closed` promise never resolves), and no
  `Element.animate` / `getClientRects`.
- The lead's head pass: `/favicon.ico` links and the og set on Welcome, Pair and Contest (Share, /s/ and Parent
  have theirs).

### For the user

- Sign in, Welcome and Pair now have no app sidebar: a slim bar with the logo, Help and your account, the card in
  the middle of the screen. OK?
- Profile and Compete now draw badges the same way (the round amber disc); the sparkle and gem badges are redrawn
  as a checked list and a checked circle. OK?
- The 404 page shows the logo's lost-corner drawing instead of a big "404". OK?

## Visual review

Phase C, own headless browser (scratchpad mcm/vr.js, phone contexts with touch at 390) against the local DB copy.
Learners: a:v2revresults01 (most attempts, named Aziz in the copy) for Profile, Settings, Compete, /share/ and the
owner's /s/; a:v2revchalA (Ada, on the all-time board with a yours row and a contest result) for Leaderboard,
Rankings and Contest; a fresh browser for Sign in, Welcome, Help, 404; a parent account linked to Aziz for /parent/.
Shots: premium/shots/app-review/ (`<page>-r0-*` before, `-r1-*` after round 1, `-r2-*` after round 2; 1440, 1440-dark,
390, plus hover, Tab focus, press, menus, sheets and the feedback moments).

### Per screen

- **Sign in** (r0: QR in a box inside a box, "Other ways" 12px left of the text edge and weighted like a heading,
  "Waiting for your phone" left under a centred code). Now: the QR is one white tile with a fine edge; code, device
  line and status centred as one block; "Other ways to sign in" sits on the card's edge with a drawn caret that turns;
  the four ways are plain rows with icons (key, phone, envelope, devices) and the hover band, the current one in the
  selected look (on a phone each way's line sits under its name). A touch screen with no passkey starts on Email code,
  not a QR to scan with the phone in hand. The
  focus bar is on the page tone (the lead's change). Verdict: calm, one orange, premium at 1440, dark and 390.
- **Welcome** (r0: the lead text touched the First name field; "Have an account?Sign in" had no space; the skip line
  was centred under left-aligned content). Now: 20px between lead and form, the space is back, "Continue without an
  account" sits on the card's left edge under a hairline. Verdict: good; the autofocused field's ink edge is a shared ask.
- **Pair** (r0 at 390: the six boxes overflowed the card by ~11px and pushed the line past the edge). Now they size
  from the card. Approve draws the check in its wash disc (shot `pair-r1-approved`). Verdict: good.
- **Profile** (r0: three solid orange badge discs, a ~70px blank band under the four figures (hidden reveal lines),
  Study time 12px lower than its neighbours, sparklines drawn as stair-steps on a phone, a 44px pencil key covering the
  56px avatar, the board line wrapping one word per 44px line). Now: earned badges are a warm wash disc with an
  amber-deep drawing and a fine amber edge (Compete's badge rows too); each figure is label, value and one quiet line
  always shown (the week, the change and the sparkline left: Results carries the trends each tile links to); all four
  share one top edge; the phone pencil is 28px with its 44px hit area kept; the board line wraps between "On boards:
  no name yet" and its two actions, never inside. Verdict: the plate reads as one calm hero in light, dark and 390.
- **Your week sheet**: goals were four grey wells (read as disabled). Now outlined rows with the drawn checkbox showing,
  picked in the selected look. Verdict: good.
- **Settings** (r0 at 390: every stacked control 12px in from its label, from an empty "Saved" slot's flex gap; the
  More options folds used the device's ▶). Now flush; every "More ..." disclosure on these pages (Profile, Settings,
  Help) draws its chevron. Privacy's index icon is the shield. Verdict: good; the Test timing dropdown repeating its
  row label is a shared ask.
- **Compete overview** (r0: side-card links in 600 ink read as part titles, the Season line pushed right on a row of
  its own, the Rivals card's only sentence folded behind a chevron, ladder chance bars as dark stubs on each cell's
  edge). Now: links are quieter than the titles (500, soft, ink on hover); Season's name and days left sit under the
  title; Rivals' line never folds (`data-nofold`, Rankings too); the chance is a small inset meter. ⋯ menu checked.
  Verdict: good; the Rush row's "strikes" icon still reads as typed "xxx" (shared ask).
- **Leaderboard** (r0: "Champion · road-2026-10-03 · band #1" under every name, seven grey slabs for Ranked by, three
  dashed "par" pedestals when nobody has placed). Now: "Champion · Road to Oct 3 · Level band #1" (UI.compete.periodText);
  metric rows plain with the pick in the selected look; no podium until someone places (the card lists the pars), open
  places a hairline, the pedestal's duplicate "par" gone; the phone Board sheet focuses the metric in use instead of
  ringing the Everyone select. Yours row (wash, amber-deep rank, 600, no stripe), the You strip and the podium's
  wash pedestal checked in light, dark, 390, with the row menu and Jump to me. Verdict: premium.
- **Contest** (r0: **the result showed "#3 of 3" for the #1 sitting**: kit.js roll() throws, see asks, after the reveal
  set the field size; the question of the day's table rendered at zero width: compete.css `.cx * { min-width: 0 }`
  beat ui.css's `.q-table { min-width: 100% }`). Now: the rank lands on the true place (guarded in contest.js), the
  table shows (`:where(.cx *)`), the points bar is a 12px meter, and at #1 the headline says "Fixes add points here,
  not places: you hold #1." instead of "All of them right → #1 of 3". Verdict: good.
- **Your rankings** (r0: four identical folded cards stacked; podium records and champions printed raw ids). Now the
  folded reference cards join into one list (hairlines between, 14px rows); records read "Road to Oct 3", "Week 39";
  "Best Daily streak" fits its tile. Verdict: good.
- **Parent** (r0: the four totals were outlined tiles with text jammed in the corner; the signed-out form floated on
  the page). Now plain figures on the page and a raised sign-in card. Verdict: good.
- **/share/, /s/, Help, 404**: /share/ follows the plate fixes; /s/ owner, Help (search, the shortcuts fold) and 404
  (spot drawing, one orange) read calm as they were. Copy buttons use `UI.copyText(text, { button })` (settings.js,
  /s/, compete-ui.js; Help keeps its own "Link copied" wording).

### Checks

check-ui ok; `node --check` on every touched file and inline script ok; no em dash in touched files. Smoke at 1440 and
390 for all 18 pages vs the pre-review snapshot (mcm/vr-before, vr-after): identical except the empty Leaderboard no
longer printing three "Open" pedestals (intended) and the same pre-existing fixture errors on Rankings and Settings
(their line text or number moved). Inventory diff: identical on every page. No sideways scroll at 390 on the four compete pages
(the contest's grid view included) after the `:where(.cx *)` change.

Test data added to the local DB copy (the 8071 instance others also browse): a:v2revresults01 is named Aziz, has a
progress share link, a shared set (X16R4252) and a linked parent (a:vrparent0000000001, a verified user row).

### Shared asks

1. **kit.js:2026 `roll()`**: `const ... off = from.length - text.length` shadows the module's `off()` (line 229), so
   line 2042's `off()` throws whenever digits move. Every UI.roll caller that sets the old value first is left on it
   (Today index.html 758/787/1508/1766, plan.js 333/890, words). Rename the local to `shift` (2026 and 2030).
   contest.js wraps its two calls until then (ponytail comment).
2. **ui.css:1172 `.field:focus`, 1231 `.otp input:focus`**: the 1.5px ink edge + halo is the dark box on Welcome's
   autofocused First name, Pair's first box and Create a contest's Title; DEMO C4 says amber-deep edge + soft halo.
3. **ui.css:1507** `:where(.card, .panel) .stat:not(button):not(a)` keeps 12px block padding while link tiles net 0:
   use `padding: 0` (me.css patches `.id-card`).
4. **ui.css:491 `.choice-row`**: a grey `--well` at rest, a darker well on hover; reads disabled. Rest no fill (or a
   1px `--line` inset where rows are options), hover `--hover`. Local patches: `.si-ways`, `.lb-metrics`, `.wk-pick`,
   `.cx-radio` (remove them once shared).
5. **ui.css:1225 `.otp input`** width from `100vw - 90px`; use `calc((100% - 50px) / 6)` (me.css patches .si/.pair).
6. **ui.js pref rows**: an empty `.pref-state` before the control adds the 12px gap when stacked (phone); give it no
   gap while empty (me.css orders it last on Settings).
7. **ui.js icons**: `strikes` (Rush) reads as typed "xxx" at 18-22px.
8. **ui.js pref select**: the dropdown repeats the row's label ("Test timing  Official").
9. **Practice (not mine)**: /s/ as a visitor lands on practice/builder.js:382's banner, which prints "[object Object],
   [object Object]" for the topics and a stray "null" line under the show-my-name box.
10. **challenge/index.html `.ch-row.you`** stripe: not in my files; please pass it on.

### Round 3

- **Contest reveal**: kit.js's roll fix is in, so contest.js's local guard is gone (both calls are plain `UI.roll`
  again). As Ada on daily-2026-09-23, a fresh tab at 1440, 1440 dark and 390 ends on "#1 of 3" with no console errors.
  The number goes #1, then a rolling overlay (#1 over the old #3 field size), then #1, and at 0.1x playback the digits
  visibly roll (`contest-r3-reveal-800ms-1440.png`, `contest-r3-reveal-end-*.png`).
- **One orange**: `UI.shell({ ownPrimary: true })` on Compete, Contest, Your rankings, Profile, Help and 404, so the
  sidebar's Up next Start is a quiet `.btn` beside each page's own orange (Start the challenge, the lobby's Start or See
  the board, Rating's Practise, Plan your week, Send feedback, Today). Leaderboard and Settings have no orange
  primary, so the sidebar Start stays orange there.
- **Rush icon**: three rings (its three chances), drawn in compete-ui.js `OWN.chances` on the Phosphor grid, replacing
  `strikes`, which read as a typed "xxx". It shows wherever `C.icon('rush')` draws (contest rows, the details sheet).
- **This week's board pick**: the native select is now the shared `UI.dropdown` (`.btn.dd.sm`, `noAll`, the label
  hidden because the part title says it). It sits at the control height and opens the shared listbox. Inventory: the
  field "Board" became the button "Board: Points" with the same three options.
- **Found while re-shooting**: the contest lobby's Options row used `.opt-row`, which runner.css (loaded for the
  question of the day) also defines as a two-column grid. On a phone that squeezed Race's select to 0px and scattered
  its "?". The row is now `.ct-opts`, and Change keeps its "?" on the same line. The "Other days" card printed "null"
  under the day steps (replaceChildren of a null strip); that child is filtered now.
- Checks: check-ui ok, `node --check` ok, no em dash; no sideways scroll at 390 on the four compete pages; smoke
  unchanged since round 2; inventory differs only by the Board dropdown above. Shots: `compete-r3-*`,
  `compete-r3-board-dd-1440`, `contest-lobby-r3-*`, `contest-r3-reveal-*`, `rankings-r3-1440`, `me-r3-1440`,
  `help-r3-1440`, `404-r3-1440`.
