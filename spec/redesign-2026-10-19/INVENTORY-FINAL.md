# Inventory final: every GONE item, classified (2026-10-20)

Input: `smoke/inventory-diff-2026-10-20.md` (jsdom first paint at 1440, Today's fixtures, FIX=practice on /practice/), the last commit's `web/` against the working tree. Each GONE item was traced by its handler in the head copy to the current code, and checked in a headless Chromium on 8071 where code reading was not conclusive (real learners `a:v2revresults01`, `a:v2revchalA`). /compete/ and /compete/rankings/ crash the jsdom smoke at head and now alike, so those pages were also re-inventoried live against 8071 (`smoke/inventory-live.js`); items only that run found are marked "live". Paths below without a folder are relative to the page's own folder; `smoke/` is spec/redesign-2026-10-19/smoke.

Classes: (a) renamed, (b) moved behind a control, (c) shows in another state, (d) intentional removal with nothing lost, (e) LOST.

Count by table row (a row can group several labels, for example the five Session size buttons or a run of kit ids): **(a) 50, (b) 44, (c) 11, (d) 37, (e) 1 (restored)**, 143 rows. Rows marked (a)+(b) or (d)/(b) count under their first class.

Gone ids still referenced: one, `#grid` in web/assets/tour.js:31 (Practice tour, a harmless fallback after `#tree`); removed. Every other gone id (`dayNote due-h tdAm tdAs tdBm tdBs big day champs qotd path prefs-h grid presetBody presetTog results sort optsbox tabsub scoreSide legacts legend bar tabs side-progress side-study` and the kit's `kclip*`/`kmk*`/`ktab*`) has no reference in web/ (web/dev/ included) or server/ (`smoke/inventory-ids.py`, plus a word grep of web/dev/); the `qotd`, `grid`, `results`, `bar`, `tabs` hits that remain belong to other pages' own elements of that name (contest's QOTD card, Profile's and contest's grid, the nav item, the shell's bar and tabs, null-guarded on pages without them). Every `#id` in web/assets/tour.js's page steps was checked against that page's first-paint ids: all resolve.

## / (Today)

Live check (headless, learner a:v2revresults01, 1440): the Session size menu lists `5 min | 15 min | 30 min | 45 min | 60 min | 5 questions | 10 questions | 22 questions | Endless`; the aside rows read `Today 1 || SAT No date yet || Score 430–570 || Pace 22:24 of 35:00 || Daily challenge || Words 34 due · 10 new · ~11 min` while closed.

| GONE item | Class | Where now / evidence |
|---|---|---|
| button `5`, `15`, `30`, `45`, `60` | (b) | The Session size button beside Study (`button.td-size`, web/index.html:1206-1243); its menu (UI.menu.bind, :1224-1231) lists the same `box` options (`nx.box.options` or [5, 15, 30, 45, 60], :1201) as `N min` radios and calls the same `choose({kind:'box', v})`. 2 taps. The numbers of questions and Timed (head's Questions toggle and clock) are in the same menu. When a step leads the day, the builder sits behind "Or a practice session" (:1267), as it did at head. |
| button `Blind spots` | (a) | It was only the (i) help button of the "Blind spots · N" sub-heading (head `info(..., 'Blind spots')`); now `UI.why(..., { about: 'blind spots' })` = "About blind spots", web/index.html:1635. The blind-spot rows and their actions are unchanged (:1636). |
| button `Collapse Daily challenge`, `Collapse Pace`, `Collapse SAT`, `Collapse Score`, `Collapse Words` | (b) | Same fold toggles, now "Expand X": the aside rows rest folded to label, value, chevron until opened (web/index.html:599-602, `shut = aside && id !== 'sum'`); 1 tap on the chevron or anywhere on the head (:620); the choice is remembered (`satf.card.<id>`). The closed row still shows the figure (Score range, Pace, SAT date, Words due). See Needs the user. |
| button `Collapse Due today` | (d) | The Due today card merged into Up next: its rows are `#due` inside Up next (web/index.html:1381, labelled group "Due today"; tour step `#due` still finds it); Up next has its own fold ("Collapse Up next") and the "N more due" / "N done" toggles on its footer (:1390). Nothing lost. |
| button `Goal 30 min ✎` | (a) | "Daily goal 30 min, change it" (aria-label; visible "Goal 30 min" + pen icon), web/index.html:2534. |
| button `How the challenge works` | (a) | "About the challenge", web/index.html:2738. |
| button `How the points are worked out` | (a) | "About the points", web/index.html:1987 (same text and the /help/#points link). |
| button `Now its twin` | (a) | "Try its twin", web/index.html:1849 (copy change, today.md P16). |
| button `Practice again` | (a) | "Practise again" (verb spelling), web/index.html:1509. |
| button `Sun, Nov 29, 2026 ▾` | (a) | "Sun, Nov 29, 2026" with a caret icon instead of the glyph, web/index.html:2396. |
| button `Target 650 needs about 34 of 44 right;you’re near 29` | (a) | Same button, now with a space after the semicolon ("...right; you’re near 29"), web/index.html:1992. |
| button `Target 650 ✎` | (a) | "Target 650, change it" (aria-label; visible "Target 650" + pen icon), web/index.html:2120. |
| href `/challenge/` | (a) | Yesterday's result link now goes to `/compete/contest/?id=daily-<day>` (web/index.html:2775). Better than head: the server redirects every GET `/challenge/` to `/compete/contest/?id=daily` (server/api_compete.py:847-850, checked: 307), so head's `/challenge/?day=X` opened today's challenge, not yesterday's. Other `/challenge/` links (results/report, practice, session, ui.js) still work through that redirect. |
| id `dayNote` | (a) | The midnight "It’s a new day" note is now a toast, `UI.toast(...)`, web/index.html:2961 (same text, same trigger). No reference to `dayNote` left. |
| id `due-h` | (d) | Heading id of the old Due today card (card() sets `<id>-h`); the card merged into Up next (`next-h`), see `Collapse Due today`. No reference left. |
| id `tdAm`, `tdAs`, `tdBm`, `tdBs` | (d) | Layout-only column wrappers of head's `place()` (no content of their own); replaced by the nine-line `place(stretch)` that moves cards into main, the rows surface and the aside (web/index.html:848-857; today.md "Dead code deleted"). No reference left. |
| id `kclip32` to `kclip36` | (d) | Kit auto ids (`uid('clip')`, web/assets/kit.js:157), renumbered (`kclip40`-`kclip44` now). Not referenced anywhere. |

## /challenge/

Note: the real app never shows this page: GET `/challenge/` is a 307 to `/compete/contest/?id=daily` (server/api_compete.py:847-850; the browser lands on `/compete/contest/?id=daily-2026-10-20`). Only a HEAD request falls through to the static file.

| GONE item | Class | Where now / evidence |
|---|---|---|
| id `big` | (a) | The big figure (your rank, or the question count) is `span.num.hero-num.ch-big` inside `#sub`, web/challenge/index.html:131 and :136. |
| id `day` | (a) | The day label is the last part of `#sub`'s meta line (`c.day ? day(c.day) : null`), web/challenge/index.html:132 and :137. |

No reference to `#big` or `#day` left in web/ or server/.

## /practice/

Classified by handler (head `practice/builder.js` (last commit) against the current `web/practice/builder.js`),
then checked in Chromium on 8071 as `a:v2revresults01` at 1440 and 390: the
preset menu lists every preset, the View menu every view and order, and the wide tree every skill row. Why the skill rows
look gone: jsdom has no layout, so `$('#tree').clientWidth` is 0 and the tree paints its narrow tiles (builder.js:748-749);
the head build switched on a viewport query (1040px) instead, so jsdom drew the wide rows there.

"Preset menu" = the trigger at the head of Your set, `#presets` (index.html:435), named "Preset: <the preset that is on>"
(builder.js:494-496), bound at builder.js:518; items built by `presetItems` (builder.js:499-517) in groups Suggested,
From your history, Yours, then Save as preset, Copy link, My defaults. 2 taps: open, pick. "View menu" = `#view`,
"View and order: <order>" (builder.js:723-733), items by `viewItems` (builder.js:735-745). 2 taps.

| GONE item | Class | Where now / evidence |
|---|---|---|
| button `Biggest gains · 3 skills` | (b) | Preset menu, Suggested; builder.js:468 |
| button `Check 1 skills I haven't tried` | (b) | Preset menu, Suggested; label now "Check 1 skill I haven't tried" (plural fixed), builder.js:475 |
| button `Circles, details and question types` | (c) | Skill row name, builder.js:829. Shows in the wide tree (tree at least 560px wide, builder.js:748, 807; at 1440 in Chromium it is on screen); a narrower tree shows domain tiles and the row is in the tile's window (`openDomain`, builder.js:812-823), 1 tap |
| button `Copy link` | (b) | Preset menu foot, same handler (`UI.copyText(deepLink())`), builder.js:513 |
| button `Due for review · 3` | (b) | Preset menu, From your history; builder.js:473 |
| button `Full section mix` | (b) | Preset menu, Suggested; builder.js:467 |
| button `Habits` | (b) | View menu, Show > Habits (listed even before it has rows, with "After about 30 answers"), builder.js:738-741 |
| button `Linear equations, details and question types` | (c) | As Circles: skill row, builder.js:829 |
| button `Map` | (b) | View menu, Show > Map, builder.js:740 |
| button `Marked` | (b) | Preset menu, From your history; builder.js:471 |
| button `Mentor's pick` | (b) | Preset menu, first item (its reason as the item's second line), builder.js:464; the trigger also reads "Preset: Mentor's pick" while it is on |
| button `Missed · 6` | (b) | Preset menu, From your history; builder.js:470 |
| button `More presets` | (d) | It only revealed the presets that can't run yet; the menu now lists them all, dimmed with the reason under each (builder.js:500-503). Nothing hidden |
| button `My mistakes` | (b) | Preset menu, From your history; builder.js:469 |
| button `Official questions you brought0` | (a) | Your sets tab "Official questions" (count 0), builder.js:1537 |
| button `Percent, details and question types` | (c) | As Circles: skill row, builder.js:829 |
| button `Presets` | (a) | The fold toggle `#presetTog` became the preset menu trigger `#presets` (index.html:435), named "Preset: Mentor's pick" |
| button `Quadratics, details and question types` | (c) | As Circles: skill row, builder.js:829 |
| button `Ready to start` | (a) | The fold is a `details.fold` now; its toggle is the `<summary>Ready to start</summary>` (builder.js:435, still remembered in `satf.pr.ready`); the inventory counts buttons, not summaries |
| button `Reset` | (a) | "My defaults" ("Back to your saved settings") in the preset menu, same handler (`fromPrefs`, `applyPreset('coach')`), builder.js:514 |
| button `Save as preset` | (b) | Preset menu foot, builder.js:512 (`savePreset`, builder.js:568-) |
| button `Saved` (preset chip) | (b) | Preset menu, From your history; builder.js:472 |
| button `Saved· 12` | (a) | List row "Saved" with the count as its own badge ("Saved12" in the inventory), same handler, builder.js:261 |
| button `Select Circles` | (c) | Skill row box `tri('Select <name>')`, builder.js:827; wide tree or the domain tile's window, as Circles above |
| button `Select Linear equations` | (c) | As Select Circles, builder.js:827 |
| button `Select Percent` | (c) | As Select Circles, builder.js:827 |
| button `Select Quadratics` | (c) | As Select Circles, builder.js:827 |
| button `Select Systems` | (c) | As Select Circles, builder.js:827 |
| button `Select all` | (a) | The master box `#treeAll` "Select every skill" (all / some / none), builder.js:721-722; Clear stays (`#treeClear`, shown while something is picked) |
| button `Skills` | (b) | View menu, Show > Skills, builder.js:740 (picking an order also returns to Skills, builder.js:744) |
| button `Solve first · 10` | (b) | Preset menu, Suggested; builder.js:474 (Math only; the head build hid every preset on R&W) |
| button `Start` | (a) | Ready rows' Start, now quiet with an arrow and named "Start <title>" (builder.js:420-422): "Start Plan · Linear", "Start Review due", "Start Your last set again" |
| button `Systems, details and question types` | (c) | As Circles: skill row, builder.js:829 |
| button `Weakest 3` | (b) | Preset menu, Suggested; builder.js:465 |
| button `Your sets· 1 in progress` | (a) | List row "Your sets" (builder.js:262, `showSets` opens `#setsFold` and scrolls, builder.js:1520); the in-progress count is the Set in progress card's ("+n more" opens Your sets on In progress, builder.js:349-353) |
| field `Sort` | (b) | View menu, Order skills: all 8 orders (Most points only when a skill has gains, as before), builder.js:702, 742-744; still saved to `satf.tree.sort` |
| id `grid` | (d) | The wrapper is `.twocol.pr-body` (index.html:412). The one leftover reference, tour.js:31 `['#tree', '#grid']` (a fallback list, harmless since `#tree` exists, index.html:423), is now removed: `sel: '#tree'` (web/assets/tour.js:31) |
| id `presetBody` | (d) | The Presets fold's body: presets are the menu, Your sets has its own fold `#setsFold` (index.html:428). `B.presetBody` in builder.js is a state field, not this id |
| id `presetTog` | (a) | `#presets` (index.html:435), see `Presets` |
| id `results` | (d) | An empty `.pr-results` div in the head markup that no script wrote to (no reference in head builder.js); nothing in web/ or server/ uses it |
| id `sort` | (b) | The select became the View menu's Order skills group (see field `Sort`); no `#sort` reference left |


## /results/

| GONE item | Class | Where now / evidence |
|---|---|---|
| button `Last 10` | (b) | The chart's Range seg became one menu button, "Showing All sittings. Range and kinds" (aria-label; visible text "All sittings"). Tap it, then Range > Last 10. web/assets/charts.js:460 (RANGES), :473-484 (UI.menu.bind). Same filter code as before (charts.js:445-452). Shown under the same condition as head (`filters: pts.length > 1`, web/results/page.js:324). 2 taps. |
| button `30 days` | (b) | Same menu, Range > 30 days. web/assets/charts.js:460, :475. 2 taps. |
| button `All` | (b) | Same menu, Range > All (the menu item keeps the word "All"; the button reads "All sittings"). web/assets/charts.js:475. The sittings seg's "All" is still on the card (inventory `All2`, page.js:486). 2 taps. |
| button `Full section · 70 min` | (a) | "Full section" (pill), same `startTest(true)`; the minutes moved into the line under it ("A full section (70 min) is the most accurate..."). web/results/page.js:218-219. |
| button `One module · 35 min` | (a) | "One module" (.btn), same `startTest(false)`; "(35 min)" in the line under. web/results/page.js:218-219. |
| button `Share` | (a) | "Share progress", same handler `shareChoose()` (language tiles, PDF, "Or share a read-only link"). web/results/page.js:143, :156-172. The ⋯ menu (CSV, Print, Share a read-only link) is unchanged, page.js:139-141. |
| field `Sort sittings` (select) | (b) | The select became the "Sort" menu button `#sitfilt` ("Sort and filter" when a kind filter or open mistakes exist). Same five sorts: Newest, Oldest, Highest, Lowest, Most points still open (when any sitting has recovery), same `SITQ.sort` and URL param. web/results/page.js:491-505. 2 taps. |
| id `kclip28` | (d) | Auto-numbered kit id (`uid('clip')`, web/assets/kit.js:157) of the old Range seg's clip; ids renumber (kclip29-36 now). Not referenced anywhere. |

## /tests/

| GONE item | Class | Where now / evidence |
|---|---|---|
| button `Show` | (b) | Head: the "How you take tests" card's fold toggle (head tests.js:319). The card is now the Habits half of "What moves this band": tap the "Habits" seg (web/tests/tests.js:192, `#levers`, index.html:406); `habitsCard()` tests.js:439-482 paints the same rows, Sittings (Last 5 / 10 / All) and Which tests segs, Why and Which sittings? actions. The choice is remembered (`satf.tests.levers`, tests.js:38). 1 tap, as before. |
| button `No traps ready yet` | (d) | Was a disabled Start (head tests.js:459-460) that did nothing. Same words now as text at the row's end: web/tests/tests.js:568-588. |
| button `Start a full section · 70 min` | (d) | Was the Habits empty state's pill (head tests.js:346), a duplicate start. The empty state is now one line (tests.js:452-458). A full section still starts from: the Up next card (tests.js:257, "Full section · 44 questions · 70 min"), the kinds list "Start Full section" (tests.js:582), the score card's "Full section · 70 min" at low confidence (tests.js:116) and the empty sittings list "Start a full section" (tests.js:819, :821). |
| id `scoreSide` | (a) | Head held the score chart and the Best / Target / Exam facts under Up next (head index.html:413, tests.js:126). Merged into `#score` itself: chart tests.js:128-132, facts tests.js:133-137, `#score` index.html:405. No reference to `scoreSide` left (grep web/ server/: 0). |
| ids `kclip26`-`kclip31` | (d) | Auto-numbered kit clip ids (kit.js:157); now kclip32-39. Not referenced. |

## /review/

| GONE item | Class | Where now / evidence |
|---|---|---|
| id `optsbox` | (b) | Head: the set options box (Questions, Clock, Feedback, Each, Level) under the action bar (head index.html:279, review.js:1652-1707). Now behind "Options" (.quiet) in the same action bar, a popover (sheet on a phone) with the same five options and the set's summary at its head; it shows "Options · N" when options are off their defaults. web/review/review.js:1855-1871 (options), :1879-1880 (button), :1892 (count). Shows when rows are selected, as before. 1 tap. No reference to `optsbox` left. |
| id `tabsub` | (a) | Head: the open tab's sub-line, shown only on a phone (head index.html:245, review.js:371). Now the open tab's figure leads the list head (`#listhead .rh-lh-m`, web/review/review.js:604-629: "≈ N pts at stake", "about N min left today", "N with notes"...); every tab keeps its full sub-line as its tooltip and in its aria-label (review.js:385, :388); half fixed / relapsed counts also sit on the Status filter (review.js:443). No reference to `tabsub` left. |

## /words/

| GONE item | Class | Where now / evidence |
|---|---|---|
| button `Add words ▾` | (a) | `Add words` (same `#bring`, the caret is now the `.dd` style): web/words/index.html:162; its menu (A word, From a text, A word list, A question I missed, Import) is unchanged at :221-228 |
| button `View options` (gear) | (a) | `View options, study, share or print` (the ⋯ `ibtn`): web/words/index.html:435-442; it now also carries the study and share items |
| button `Meanings` | (b) | ⋯ > `Meanings` (checkbox item): web/words/index.html:437, `setMeanings` :460, still kept in the URL (`m=1`). 2 taps, the same as head (gear, then Meanings) |
| button `Select` | (b) | ⋯ > `Select` (checkbox item): web/words/index.html:438, `setSelecting` :461; `Done selecting` (`#barDone`, :181, shown at :651) ends it; the tile keyboard select still starts it (:708). 2 taps, the same as head |
| button `Difficulty: Estimated until your first answer, then measured` | (b) | ⋯ > `What the marks mean` popover, last row, same wording: web/words/index.html:440 and :635; each tile also keeps its `Difficulty: <tier> · estimated until your first answer` title (:526). 2 taps |
| id `legend` | (b) | The always-on legend line became the `What the marks mean` popover (`legendNode`, web/words/index.html:625-636): the same marks (strength, proven, due, saved, trap, stubborn, difficulty) with the per-mark counts as "· N here". The word count it used to sit beside is `#count` (:443, filled by `legend()` :621). Not referenced anywhere (grep) |
| id `legacts` | (d) | Its holder became the `.wl-legacts` div with no id (web/words/index.html:443). Not referenced anywhere (grep) |
| id `kclip34` | (d) | auto-numbered kit id (`uid('clip')`, web/assets/kit.js:157) |

## /words/mine/

| GONE item | Class | Where now / evidence |
|---|---|---|
| button `Add a word` | (b) | `Add words` > `A word` (kbd N): web/words/mine/index.html:310-311. 2 taps; the N shortcut still adds one directly (:508) |
| button `Bring words ▾` | (a) | Merged into `Add words` (:310-311): From a text, A word list, A question I missed, Import a file or a paste (`bringItems`, :322-326), same as the library's menu. Import is also under ⋯ (:315) |

## /words/print/

| GONE item | Class | Where now / evidence |
|---|---|---|
| hrefs `/`, `/compete/`, `/help/`, `/me/`, `/plan/`, `/practice/`, `/results/`, `/review/`, `/signin/`, `/tests/`, `/words/`; buttons `Collapse sidebar`, `Dismiss`, `Menu, today’s challenge is new`, `Open menu`, `Quick question or log a mistake`, `Quick question, log a mistake or add a word`, `Search`, `Send feedback`, `You, not saved yet, account menu`; ids `bar`, `tabs`, `side-progress`, `side-study` | (d) | The shell left on purpose: print pages have no chrome (DIRECTION.md:126; passes/words.md:36, :59, :154). Back: the toolbar's `Back` goes to the page that opened the sheet (`satf.words.from`, set by web/assets/words-ui.js:273), web/words/print/index.html:94 and :149. Print: `Print` pill :155 and the P key :168. The no-code state links `Quiz setup` (:100). Every nav item is one tap away through Back. `#bar` / `#tabs` are not referenced by this page; the shell's own lookups are null-guarded (web/assets/ui.js:2749-2750, :2755-2756) |
| (state) error: "No worksheet with that code on this account." / "The worksheet did not load." | (e) restored | Before, the shell gave a way out; after the redesign this state had only Retry (or nothing on a 404), so browser Back was the only exit. Fixed: the error message now carries the same `Back` (web/words/print/index.html:105-106) |
| ids `kclip26` to `kclip33` | (d) | auto-numbered kit ids from the shell's sidebar (web/assets/kit.js:157) |

## /words/study/

| GONE item | Class | Where now / evidence |
|---|---|---|
| button `A topicScienceHistory & social studiesLiterature & artsTrans…` | (a) | `A topic` (the deck radio no longer wraps its select): web/words/study/index.html:204-210 |
| button `ClaimedProve them in context` | (a) | `Claimed`; "Prove them in context" moved to the deck's tooltip (:213) and its note when chosen (:217) |
| button `NewNext 20 by test value` | (a) | `New`; the help moved the same way (:213, :217) |
| button `Show first: Commit first shows three meanings before the fli…` | (a) | `About show first` (`UI.why`, :193), same text (:246); Show first sits under `More options` in Cards (:247, fold remembered) |
| field `A topic` (select) | (c) | Shows beside the chosen deck: choose `A topic` (under `More decks · n`, :225, remembered open) and its select appears (:216-217) with the same options as head: every subject plus every Transitions logic pair (:164, identical to head :162). 2 taps (More decks, A topic) then the select |
| ids `kclip27`, `kclip28` | (d) | auto-numbered kit ids (web/assets/kit.js:157) |


## /compete/

Method: the jsdom inventory crashes on /compete/ (and /compete/rankings/) at head and now with the default fixtures, so these four pages were re-inventoried head vs now against the live API on 8071 (`smoke/inventory-live.js`; a:v2revresults01 for Compete, Profile, Settings; a:v2revchalA for Leaderboard, Rankings), then checked in a headless Chromium: Daily card, its More menu, the Board dropdown, the QOTD link target, the Private tab, Champions on Your rankings, the leaderboard period seg and Board sheet at 390, Profile's preferences row and folds, Settings' About buttons. Items only the live run found are marked "live".

| GONE item | Class | Where now / evidence |
|---|---|---|
| button `+ Create a contest` | (a) | "Create a contest", web/compete/index.html:36 (glyph dropped); "Join or create" on a phone |
| button `About champions` | (b) | Your rankings tab, Champions card (2 taps: tab, then Open Champions; `#champions` links open it). Its empty line says the same "A week closes Mondays at 12:00 UTC": web/compete/rankings/rankings.js:335 |
| button `About private contests` | (b) | Contests card, Private filter (1 tap): "No private contests yet. Make one for friends from Create a contest, or join with a code." web/compete/overview.js:216-217. The empty Private card hides (overview.js:432-433); Create and Join stay in the header |
| button `Points` / `Over expected` / `Climb` | (b) | "Board: Points" dropdown on the This week part, all three options: web/compete/overview.js:346 (browser: Points, Over expected, Climb) |
| id `champs` | (b) | the Champions card moved to /compete/rankings/ `#champions` (rankings/index.html:78, rankings.js:329-342, with the band winners line); overview.js:383 comment. No reference left in web/ or server/ |
| id `qotd` | (a) | one `.qotd-row` in the Daily card's foot (overview.js:233-244, placed at :129). "Answer" still opens /compete/contest/?id=daily#qotd, whose `#qotd` exists (contest/index.html:64, contest.js:989; browser: visible with the question). compete.css:278 `#qotd` styles that contest card. No reference to an overview `#qotd` left |
| ids `kclip38`-`kclip40` | (d) | kit.js auto ids (`uid('clip')`, kit.js:157) |
| live: button `More ▾` | (a) | "More" dots button, overview.js:73-77 (same menu: Past days, Daily reminder) |
| live: button `Warm up · 6` | (b) | Daily card, More menu (2 taps), with its explanation as the item's sub line: overview.js:85-89 (browser: listed first) |
| live: button `Start` (section bar's Up next) | (d) | duplicate: Compete sets `now: false` (index.html:62) so the Daily's Start is the one orange; the sidebar's Up next Start (G N) is unchanged |
| live: ids `kmk31`/`kmk35`/`kmk37` | (d) | kit.js auto ids |

## /compete/rankings/ (live only; not in the fixture diff)

| GONE item | Class | Where now / evidence |
|---|---|---|
| button `About the median` | (d) | it explained the Level ladder's "Timed-section median" column, whose cells were a hardcoded dash at head; the two always-empty columns left with it (rankings.js:346-347 notes they return when the server sends them) |
| ids `kclip59`-`kclip66`, `kmk28`-`kmk36` | (d) | kit.js auto ids |

## /compete/leaderboard/

| GONE item | Class | Where now / evidence |
|---|---|---|
| button `All time` | (a) | "All" in the period seg, its title and tooltip "All time" (leaderboard.js:24, :103); the board summary still reads "All time" (leaderboard.js:62). period=all unchanged |
| button `Filters · Everyone` | (a) | `#lb-sum` "Board: Points · This week · Everyone. Change" (index.html:42, leaderboard.js:134-146): opens the Board sheet with metric, period, Scope (all six), Domain and Find; from 1280px the same controls sit in the side column `#ctl` (browser-checked at 1440 and 390) |
| id `path` | (a) | the "N to top 10 · N to the podium" line is part of the You strip text now (leaderboard.js:236-242). No reference left |
| ids `kclip28`-`kclip30` | (d) | kit.js auto ids |

## /me/

| GONE item | Class | Where now / evidence |
|---|---|---|
| `Collapse Snapshot` / `Collapse Score trend` / `Collapse Pace` / `Collapse Activity` | (b) | same cards, now folded on a device's first visit (me.js:81-84): "Expand X", 1 tap, remembered open after |
| `Collapse What keeps catching you` | (a)+(b) | the card is "Mistakes" ("Expand Mistakes", folded first visit), me.js:77 |
| `Collapse Your habits` | (b) | Habits is a part inside Mistakes (me.js:77): Expand Mistakes, 1 tap; `#habits` still lands |
| `Expand Recent activity` | (b) | Recent is a part inside Activity (me.js:78): Expand Activity, the same 1 tap as before; `#recent` and `#feed` still land (me.js:1231) |
| `Collapse Learning preferences` | (b) | card left Profile: Account card row "Practice and test defaults" + "All settings" (me.js:803-809, href /me/settings/#practice), 1 tap; Settings holds every key the card had plus the stage line (settings.js:62-70, :110-115) |
| live: the Learning preferences controls (Questions per set field, 5/10/20/Custom, Learn/Build/Test-like/Auto/Follow my exam date, Easy/Medium/Hard, Adaptive difficulty, When I miss/Always/Off/On tap, Calculator button, SAT words/Transitions, Test timing, Calculator in tests, Pace guide, Confidence chips, Show my module 2 route, Fullscreen tests) | (b) | /me/settings/ Practice, Tests, Display and Words sections (settings.js:62-70; 36 rows in Practice, browser-checked), via All settings (1 tap) |
| `Help: Account` / `Activity` / `Goals` / `Pace` / `Score trend` / `Skills` / `Snapshot` / `Test-day readiness` | (a) | "About X": the same `A.helpBtn(c.help, c.title)` (me.js:92) now names itself through `UI.why` `about` (account.js:183-186, kit.js:1155) |
| `Help: What keeps catching you` | (a) | "About Mistakes" (help id `mistakes`, me.js:77) |
| `Help: Your habits` | (a) | "About Habits" (help id `habits`, me.js:77) |
| `Help: Learning preferences` | (b) | the same Help answer `stages` is Settings' "About Practice" (settings.js:47-49): All settings, then About Practice (2 taps) |
| id `prefs-h` | (b) | heading left with the card; no reference left. `#prefs` / `#preferences` links land on Account (me.js:1231-1232) and the row itself is `id="prefs"` (me.js:808) |
| live: button `Sharpen · 12 questions · ~19 min` | (a) | "Sharpen · 12", the "12 questions, about 19 min" moved into its help line (me.js:866-868) |
| ids `kclip203`, `kclip632`-`kclip635` | (d) | kit.js auto ids |

## /me/settings/

| GONE item | Class | Where now / evidence |
|---|---|---|
| `Help: Account & devices` / `Practice` / `Privacy & data` / `Study` / `Your reports` | (a) | "About X", same answers (settings.js:47-49 via account.js:183-186) |
| live: button `Back to stage` | (a) | "Use stage defaults", same `resetPractice(true)` (settings.js:110) |
| id `kclip26` | (d) | kit.js auto id |

## Focus chrome: /signin/, /welcome/, /pair/ (shared rows)

Sign in, Welcome and Pair now run in the focus chrome (`UI.shell({ chrome: 'focus' })`, web/assets/ui.js:2721-2734 `buildFocus`, 2744-2756): a slim bar with the mark and wordmark linking home (ui.js:2732), Help & FAQ, and the account menu. The sidebar, rail, tabs and Now strip are not built (ui.js:2752, 2756) and the shell's notices are skipped (ui.js:2773 `if (!focus) onShell(notices)`). The keyboard shortcuts stay (ui.js:1259 Mod+K search, G H). The account menu (ui.js:2359-2386) still carries Profile, Settings, Sign in (when not saved), Sign in another device, Help & FAQ, Send feedback, Dark theme, Large text, Keyboard shortcuts and Sign out.

Shared shell rows (same on all three pages; listed once, they count once):

| GONE item | Class | Where now / evidence |
|---|---|---|
| hrefs /compete/ /me/ /plan/ /practice/ /results/ /review/ /tests/ /words/ | (d) | Focus chrome: the logo goes to Today (ui.js:2732), where the full nav is; /me/ is also in the account menu (ui.js:2372) |
| href /signin/ (Welcome, Pair) | (d) | It was the sidebar account row and the 'first' banner. Account menu, Sign in (ui.js:2375), 2 taps; Welcome also has its own Sign in switch (welcome.js:47) |
| Collapse sidebar, Open menu, Menu, today's challenge is new | (d) | Sidebar and phone menu are not built in the focus chrome (ui.js:2752) |
| Search | (d) | Mod+K still opens it (ui.js:1259); the logo leads to every page with the sidebar search |
| Quick question or log a mistake / ... or add a word | (d) | The quick capture belongs to the app chrome: sidebar button on every normal page (ui.js:1964) and the Q shortcut (ui.js:1258) |
| Send feedback | (b) | Account menu, Send feedback (ui.js:2380), 2 taps |
| Dismiss (Welcome, Pair) | (d) | The 'Have progress on another device? Sign in / Dismiss' banner (ui.js:2861-2866); notices are skipped on focus pages (ui.js:2773) and still show on every normal page |
| ids side-progress, side-study | (d) | Sidebar groups, not built on focus pages; no references left in web/ or server/ |
| ids kclip*, ktab* | (d) | Auto-numbered by kit (kit.js:157 `uid`); never referenced |

## /signin/

| GONE item | Class | Where now / evidence |
|---|---|---|
| Shell rows above | (d)/(b) | See the shared table |
| Email code, Passkey, Use your phone | (a) | Same ways, now rows with a line of meta: 'Email codeA 6-digit code by email' etc. (web/signin/signin.js:23-24, rows at 65-67) behind 'Other ways to sign in' (signin.js:68), 1 tap; the device's last or best way shows open at once (signin.js:40-42) |
| More | (a)+(b) | Renamed 'Transfer code' (signin.js:24, panel at 264-268), a row under 'Other ways to sign in', 1 tap; also linked from the passkey panel (signin.js:215) |
| ids ktab27-30 | (d) | The tab strip became the row list (si-ways, signin.js:64) |

## /welcome/

| GONE item | Class | Where now / evidence |
|---|---|---|
| Shell rows above | (d)/(b) | See the shared table |
| Create account | (a)+(c) | The 'Create account / Sign in' segmented control became one quiet line under the form (web/welcome/welcome.js:46-54). The page opens in create mode (welcome.js:20), so the create form is already showing; from sign-in mode, 'New here? Create an account' (welcome.js:47, 54) switches back, 1 tap |

## /pair/

| GONE item | Class | Where now / evidence |
|---|---|---|
| Shell rows above | (d)/(b) | See the shared table; 'Back to Today' after approving is kept (web/pair/index.html done()) |
## Restored

1. /words/print/: the error states ("No worksheet with that code on this account." and "The worksheet did not load.") had no way out once the print page lost the shell; they now carry the toolbar's Back through one `back()` helper (web/words/print/index.html:93-94, used at :106 and in the toolbar). Checked in the real app at 1440 and 390 with `?id=zzz123`.
2. web/assets/tour.js:31: the Practice tour step no longer lists the gone `#grid` (`sel: '#tree'`).

No other item was lost.

Also tidied (not a loss): web/assets/tour.js:74, the Compete tour's Next badges step said "Go takes you straight to the next one", but the badge rows now name where they go (web/compete/overview.js:411-412); it now reads "Earn badges by playing. Each one links straight to where you earn it." The two Compete help texts that became empty-state lines carry the same facts: head "Private contests are for friends: make one and share the link." vs now "No private contests yet. Make one for friends from Create a contest, or join with a code."; head "Last week's podiums show here once a week closes, Mondays at 12:00 UTC." vs the Champions card's "A week closes Mondays at 12:00 UTC".

## Needs the user

Nothing below is lost; each is a first-paint or tap-count change the user should own.

- Today: the aside cards SAT, Score, Pace, Daily challenge and Words first paint folded to one row (label, figure, chevron; web/index.html:599-602), so Score's target line, Pace's lines, the challenge's Start and board and Words' Start are one tap further. Each card remembers being opened.
- Profile: Snapshot, Score trend, Pace, Mistakes and Activity start folded on a device's first visit (web/me/me.js:81-84). Learning preferences left Profile: one row, "Practice and test defaults", plus All settings (me.js:803-809); every control is in /me/settings/.
- Practice: the 11 presets went from chips (1 tap) to the "Preset: ..." menu (2 taps); Skills / Map / Habits and the sort order share the "View and order" menu (2 taps, was 1).
- Results: the chart range (Last 10 / 30 days / All) and Sort sittings each went from visible controls to a menu (2 taps, was 1). Same options.
- Words: the marks legend with its counts (proven, due, saved, trap, stubborn) showed on first paint; it is now behind the ⋯ menu, What the marks mean (2 taps).
- Compete: Champions left the overview for Your rankings, Champions (2 taps); Warm up moved into the Daily card's More menu (2 taps).

## Checks after the fixes

Whole-app run (the final run script: check-ui, node --check, em dashes, smoke head vs now, inventory head vs now): check-ui ok; node --check clean on every file and all 41 inline scripts; no em dash in web/ (the two hits are tools/check_rw.py and tools/rw_options.py, R&W bank tooling outside this redesign); the smoke harness at 1440 and 390 is the same as the last commit on every page (the only DIFF is /challenge/, which crashed at head and is clean now); Today's five states at 1440 and 390 clean; weekPlanner 4 checks passed. The inventory re-run, compared as JSON sets per page, gives exactly the GONE sets of the input diff on every page: the three fixes live in an error state and the guided tour, which the first-paint inventory does not see.
