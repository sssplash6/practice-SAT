# Audit: Tests (web/tests/**)

Scope: `web/tests/index.html` (380 lines of page CSS, 21-400), `tests.js` (981), `start.js` (start sheet), `talk.js`
(paper sheet), `compare.js` (compare sheet). Code-level only. Line refs are file lines.

## What the student sees

**1440x900, sidebar 248.** Main is 1192 wide; `.page` max 1120 plus 40px gutters leaves 1040 of content (76px unused
each side). Height 900 < 1100, so the sidebar is nav-only, and `UI.shell({now: false})` (tests.js:37) drops the Now strip.
Stack: page top 27 + section bar 44 + 16 margin + h1 38 + gap 28 = cards start at y 153.
- `.ts-top` 2fr/1fr (index.html:25): `#score` 680 wide, `.ts-side` 340.
- `#score` is about 980px tall: head row, band at 64px (`.sc-band` clamp 44-64), headline, meta, reason button,
  4 `.sc-line`s (total, projection, growth, calibration), then "What moves this band" (causes rows plus 3 skill rows).
  It ends near y 1135, below the fold.
- Right: `#next` (about 200 tall, Start pill at y 260-300) and `#scoreSide` (chart 120 plus Best / Target / Exam), ending
  near y 585. That leaves **about 550px of empty column** beside the score card.
- Above the fold: band, headline, score lines, Up next with Start. Below it: Test, Fix, Prove; **In progress** (from y 1160);
  Habits (folded); New test (8-9 cards, 3 by 3); Papers (9 cards plus filters); Your sittings.

**390x844.** Top bar 56 + page top 25 + section bar 44 + 16 + h1 28 + gap 22 = score card at y 191. The phone card runs
about 1170 tall (lines wrap at 326 wide, the causes rows go to two lines). `#next` comes **after** it (`.ts-top` goes to one
column), so the primary Start sits near **y 1480, two screens down** (usable height is about 728 between the bar and the
tabs). New test runs about 1350 (9 cards in one column) and Papers about 1000. The page is over 5000px.

## A. Purpose and primary action
- Question: "which test do I sit next, and where does my Math score stand?" Primary: `#nextGo` (tests.js:232).
- Desktop passes; phone fails (above). The estimate is context, the task is Start, but the DOM puts the estimate first.
- Orange count: the Up next pill + 8-9 kind Starts + 9 paper Starts + live pills = about 20 amber blocks on one page,
  all `.pill`. The primary does not stand out. `recommendedKind()` is computed (tests.js:426) but never used, so the
  "recommended card is marked elsewhere" comment (tests.js:456) is false: nothing marks it.

## B. Whitespace (current values)
- `.ts` gap 28 (22 phone) and `padding-bottom: 120px` (index.html:21) override `.page`'s 88: 120px dead at the bottom.
- `.ts-top` gap 20; `#score` gap 22; `.sc-top` gap 20/28; `.sc-lines` pad-top 14; `.sc-moves` pad-top 16, gap 14.
- `.ts-next` padding 22 (index.html:81); `.mv-block` padding 14/16 (66); `.lv-row` padding 16/18 + 10 between (94-96).
- Row heights: `.hb-row` min 56 (107), `.mv-row` min 48 (71), `.tk-head` min 44. DIRECTION wants 40-44.
- `.ts-grid` gap 16 (120); `.ts-card.kind` 14/16, `.paper` 12/16; the base `.ts-card` 20/20/18 is always overridden.
- `.ts-sec { scroll-margin-top: 110px }` (26): about 58px too much on desktop (the bar is 44+8).
- Negative-margin patches against `.card-head`'s 16px: `.ts-met` -8 (117), `.ts-sub` -10 (118), `.ts-chips` -6 (343),
  `.hb-bar` -6 (351), `.share-sheet .k + .seg` -6 (318). They break when DIRECTION sets `.card-head` to 10: remove them
  in the same change.

## C. Non-essential always-on content
FOLD_SEL on this page catches only `.ts-sub` (papers intro, tests.js:511, 108 chars, folds). Not caught:
- `.sc-empty` (tests.js:104, 105 chars, explains band widths): not in FOLD_SEL. Move it to a `?` tooltip.
- movesBand empty `.help` (tests.js:151, 51 chars): under FOLD_MIN, stays. Fine.
- `.sc-line` x4 (tests.js:133-142): total, projection, growth percentile, calibration, all always on. Fold behind
  "Details" or move to the side column.
- `.ts-met` "Question types met under the clock" (424): meta, stays. Fine as one line.
- **Sheets never fold**: `FOLD_SKIP` has `dialog` (ui.js:2793). The start sheet carries about 15 `.help` lines (start.js:
  323-331, 354, 383-384, 451, 461, 469, 496-503), the share sheet 3 (tests.js:805, 824, 827), talk 1, compare 1.
  This is the biggest block of unfolded text in scope.
- Opposite problem: kind and paper cards put tags, help and facts in a **native `title`** on the whole `<article>`
  (tests.js:437, 573). Touch has no tooltip, so the phone never sees "Asks for your name and email before the
  result" (diagnostic), "Tops out at 580", a paper's mistake types, new types, sat by, average or your band. This breaks
  "phone shows everything desktop shows". It needs a visible `.reveal` meta line.
- The conf chip's reason is a `title` on a non-focusable span (tests.js:99): no keyboard or touch path either.
- Habits folds with its own Show/Hide (tests.js:311-323): not remembered (memory only), not `.card-fold`, and it folds
  even the empty state, so a new student sees a bare title with "Show".

## D. Sidebar use
- Right column (`.split`, 1280+): estimate (band, confidence, headline, chart, Best / Target / Exam), the 4 score lines
  (folded), What moves this band, a Habits summary, "How scoring works". All of it is context, none of it is the task.
- Main keeps: next test + Start, In progress, Test / Fix / Prove, New test, Papers, Your sittings.
- Left nav: nothing to add. The Tests item lights as now.

## E. Redundancy
- **Two Up nexts, three after the shell pass.** `#next` reads `/api/tests` `up_next`; the sticky section bar's
  `.sections-next` (ui.js:2231-2238) reads `/api/shell` `next[]` (ui.js:1068) and shows on scroll on every page except
  Today. They can disagree (shell "Review 6 mistakes", page "Full section"). DIRECTION's sidebar Now block adds a third.
- Facts `Target` and `Exam` (tests.js:121-122) repeat the plan target and the sidebar Today block's exam countdown.
- Band chart: Tests (tests.js:114), Today (index.html:2079), Results (results/page.js:238).
- "Skills worth the most" (tests.js:172) repeats Today's gain card (its "All skills" link goes to `/#gain`).
- Levers causes `clock` and `changed` (tests.js:66) and the Habits measures Pacing and Answer changes (the preview at
  tests.js:342) report the same signals in two blocks.
- Streak and Today progress do not appear on Tests, so there is no duplicate there.
- A live sitting shows up to 3 times: Up next "Finish X" (197), `#live` row (281), and a sittings row with Resume (726).
  `#live` is the only place with Hand in and Discard, so it stays.
- New student: "Full section · 70 min" is offered 4 times plus the kind card (tests.js:100, 151, 346, 652) and Up next.
- Kinds are offered 3 ways: page cards (398-408), sheet radio cards (start.js:284), and presets (start.js:50-61:
  "Routing check" is the trainer, "700+ finisher" is module 2 harder).
- The 580 cap is explained 5 times (tests.js:402, 869; start.js:323, 340; Up next meta).
- Share sheet: `say()` (805) and the next help (824) both explain twins.

## F. Local overrides, scale, banned shapes
- **A third pill height.** `.ts-next .pill, .ts-card .tc-acts .pill` and `.st-go .pill, .st-go .btn` are forced to 38px
  (index.html:250-251). The user's rule allows 42 (`.pill`) and 34 (`.pill.sm`) only.
- **Round button.** `.tk-send` is `.pill` at 44x44 with `border-radius: 50%` (305). check-ui.py passes because it
  greps 999px and 24px+.
- `!important` on `.st-swh` (238) fights `.help`.
- `.tag` is defined here (29-32) and again in index.html, words, plan, review and me.css: one shared component, six
  copies. `.conf` (36-39) is a second chip style.
- Dead CSS: `.stat.sm` (33-35), `.sc-gate`, `.sc-spark` (60-61), `.tc-goal`, `.tc-stats`, `.tc-tags`, `.tc-hist`, the
  `.tc-rep` hover-reveal (146, 167-171; Report is in the ⋯ menu now), `.sr-cmp` (348-349; never rendered, see I-1).
- Card in a card: `.mv-block` is `--tile` inside `#score`'s `--tile` (66), so the "two separate panels" are invisible
  and only add 14/16 padding.
- Off-scale sizes: 11, 11.5, 12, 12.5, 13, 13.5, 14, 15, 15.5, 17, 18, 20, 22, 48 and the 44-64 clamp (`.sc-band`,
  49, with `.num` at weight 900). Weights 700 and 800 (`.sr-band`, 194) are off the 600 scale.
- Mono on words: `.lv-state mono` (tests.js:290), `.tc-facts mono` (444), `.hb-ev mono` (354), `.st-sum mono`
  (start.js:200), `.tk-when mono` (talk.js:304), every compare `td.mono` (compare.js:63), `.sr-d` date (index.html:188-189),
  `.hs-arrow mono` (tests.js:881). The `sections()` regex (tests.js:915) wraps any trailing number in `.n.mono`.
- No hardcoded colours. Inline `style` only for data bar widths (talk.js:159, compare.js:86): fine.
- Hardcoded sheet padding: `.st-foot` pulls out by `--card-pad` (22) but `.sheet-body` pads 24 (ui.css:1990), so the
  hairline stops 2px short each side; `.tk-compose` (301) hardcodes -24/-22. Both break on the spacing pass.

## G. AI-slop tells
- About 20 uppercase mono `.k` kickers: "Up next" above its own title (tests.js:231), "Estimated Math score" (94),
  "Test → Fix → Prove" above an h2 (251), "In one tap", "Training aids", "How", "What they sit", "Invite code",
  "Traps of this paper", "By domain", "Slot by slot", the compare row heads (`th.k`), and `M1`/`M2` in miss chips.
- `.hb-ck` (index.html:158): 11px mono, .1em tracking, uppercase. `.st-subj` "MATH" tag (start.js:345, index.html:229):
  mono caps, and redundant (the app is Math only).
- Generic equal card grids: 9 kind cards and 9 paper cards, 3 by 3.
- `.sc-dash` (45): an en dash squashed with `scaleX(.8)` at 55% opacity. Decoration on the hero figure.
- Five blank em-dash cells as the habits "preview" (tests.js:342-343): placeholder theatre.

## H. Copy
- Em dash characters (U+2014) as placeholders: tests.js:95, 343; compare.js:28-41 (9 uses) and the filter on 63.
  Use an en dash or "none".
- Sentences used as button labels: "One more section makes this Consistent · Start" (tests.js:101), "Sit this week's
  Paper #n instead" (226).
- Chatty: "The dress rehearsal: twins, ranked, this weekend" (210); "do you still take them?" (207), repeated at
  407 and start.js:451; "Your points leak to time: ..." (220).
- Jargon for a student: "an ordinal heuristic ... It is not IRT" (tests.js:867); "Gate +2" and "2nd pass +20" chips
  (706, 709) with no gloss.
- Stacked headers in the start sheet: title "Start a test" over h3 "What do you want to sit?" (start.js:195, 271).
- "No traps ready yet" is a status written as a disabled button label (tests.js:459). Use a meta line plus a disabled Start.
- Presets start a sitting at once ("Building…") but are drawn as chips under "In one tap" (start.js:276-280). They read
  as filters.

## I. Bugs (code-level)
1. **Compare tick class mismatch.** The checkbox sits in `span.sr-c` (tests.js:745), but three paths query
   `.sr-cmp input`: the X key (899, dead), the compare bar's Clear (647, leaves boxes ticked), and the third-pick
   eviction (758, the dropped box stays ticked while `picked` has dropped it). The UI and the state disagree.
2. **Active filters invisible on desktop.** index.html:133-134 hides every dropdown behind "Filters" at all widths.
   index.html:346 then hides the `.fchip.dup` chips at 760+ because "the dropdowns already show their values"
   (tests.js:384-385, a stale comment). On desktop the student sees only "Filters · 2" and never the current sort.
3. **O key dead.** It looks for a button with the text "Options" (tests.js:897), but Options moved into the ⋯ menu
   (438, 576). Restore it by calling `S.open` with the card's options directly.
4. **Section chips out of order.** `sections()` lists Habits, New test, Papers, In progress, Sittings (905-912). The DOM
   order is cycle, live, habits, kinds, papers, sittings. `#score` and `#cycle` have no chip.
5. **Phone loses data.** Under 760 `.sr-d` is hidden (index.html:384), so a sitting's date and minutes are gone. At
   760-999 `.sr-s` is hidden (364), so its score band is gone.
6. `.st-foot` and `.tk-compose` misalign with the sheet padding (F, last item).
7. Dead JS: `icon` (23), `ls` (24-27), `sourceLine` (67), `rec`/`est` (426-427), `n` in `liveRow` (282).

## Redesign proposals (ranked)

1. **[BIG] Split layout, task first.** index.html:406-422, 25, 44; tests.js:86-145, 186-237. Risk: medium.
   - Header row: h1 "Tests", then the next test (title and one meta line) and its Start as the one 42px `.pill`, plus
     the alt quiet button. Relabel `#next` to "Next test" so it reads differently from the shell's Up next.
   - `#live` straight under the header, as 40-44px rows in one card.
   - Main: Test / Fix / Prove, New test, Papers, Your sittings.
   - `aside.split-side` (sticky, 1280+): estimate card (band at the 32px figure, conf chip with a real tooltip,
     headline, chart, facts), the 4 score lines in a fold, What moves this band, Habits summary, "How scoring works"
     as a quiet link.
   - Under 1280: a one-line estimate under the header ("520 to 600 · Mixed · 60 below 650") that jumps to the estimate
     card, which stacks after `#live`.
   - Keep the ids `#score`, `#next`, `#scoreSide`, `#habits` (skeleton() 943, the error paths 956-958, hash links).
   - Removes the 550px hole and brings the phone Start from y 1480 to about y 260.
   - Unchanged: the deep links (tests.js:968-979: `?start=`, `?shared=`, `?compare=a,b`, the `#hash` scroll), the
     `satf:open` event from the section bar, the key map (893-901), and `showOnly` and liveCard's Show all (both
     target `#sittings`).
2. **Fix I-1 to I-5.** tests.js:647, 758, 899 (wrap the box in `label.sr-cmp`, which the existing `.sr-cmp` rule at index.html:348 already styles);
   897; 905-912; index.html:346 (show the chips at every width while the bar is popped) and 364/384 (move the date into
   `.sr-ks` on the phone; keep the band at 760-999 and drop the M1/M2 line instead). Risk: low.
3. **[BIG] New test and Papers as rows, one card each.** tests.js:418-466, 563-591; index.html:120-131. Risk: medium.
   - A kind row (44px): title, facts, your line, Start, ⋯. A paper row: name, new dot, rating chip, state, Start, ⋯.
   - The `title` content becomes a visible meta line using `.reveal` (hover/focus on desktop, always on phone). This
     fixes the phone loss in C.
   - Keep the `.ts-card`, `data-kind`, `data-paper` hooks (J/K/Enter/D keys) and 9 papers before Show all
     (acceptance 34).
4. **One pill size, no round button.** Delete index.html:250-251. Header Start is `.pill`, rows use `.pill.sm`, the
   sheet foot `.pill` at 42. `.tk-send` (305) becomes `.btn.icon` (radius 10). Risk: low.
5. **Mark the recommendation, quiet the rest.** Use the computed `rec` (tests.js:426): the recommended row keeps
   `.pill.sm`, the others take `.btn.sm`. This cuts about 18 orange blocks to 1 or 2. It reverses the "one orange Start
   on every card" decision (456), so ask the user first. Risk: preference.
6. **[BIG] Merge Habits into What moves.** A segmented "Where points went | Habits" in the aside's estimate block,
   replacing the custom fold (tests.js:311-323). Keep Last 5/10/All, scope, Why, Which sittings? and the `#habits`
   host id for `loadHabits()`. Risk: medium.
7. **Whitespace.** `.ts` gap 28 to 16 and bottom 120 to 48 (the phone keeps 88 for the tabs); `.ts-top` and `#score`
   gaps to 12; `.ts-next` 22 to 16; `.hb-row` 56 to 44, `.mv-row` 48 to 40; `.ts-grid` gap 12; scroll-margin to 64
   (108 on the phone). Remove the 5 negative margins (B) with the `.card-head` change. `.mv-block` becomes hairline
   groups (no tile on tile). Risk: low, but it depends on the shared spacing pass.
8. **Type and mono.** `.sc-band` to the 32px figure (drop `.num` 900 and `.sc-dash`); `.nx-title` to 16/600;
   `.tc-title`, `.lv-title`, `.tk-topic b` to 14.5/600; `.sr-band` 16/600 tabular. Drop `.mono` from the word strings
   in F and the `.n.mono` wrap (915). `.hb-ck` to sentence-case meta. Delete "MATH". Risk: low.
9. **Start sheet trims.** start.js. Risk: low.
   - Drop the h3 "What do you want to sit?" (271).
   - "In one tap" becomes the label "Start now" (280), so the presets read as actions.
   - The tool and aid helps (496-503) go into `?` tooltips. The conditions help (469-470) stays visible because it sets
     ranking.
   - The modules help (338-340) becomes the cards' meta line.
10. **Empty states: one line, one action.** For a new student, keep Start in the header. Moves, habits and sittings
    empty states become one line each, and the sittings empty state keeps a quiet "Start a full section"
    (tests.js:151, 346, 652). Move `.sc-empty` into the band's `?`. Risk: low.
11. **Copy pass (H).** Replace the U+2014 placeholders; shorten the two sentence buttons; "Pressure check" meta to
    "Open until you open its report"; gloss Gate and 2nd pass in their tooltips; drop "It is not IRT" (867). Risk: none.
12. **Share sheet.** Merge 805 and 824 into one line under the Twins/Exactly seg. Risk: none.
13. **Dead code out.** The CSS in F and the JS in I-7. Grep first; none of it is referenced. Risk: none.

## Shared asks (lead only)
- `paintBarNext` (ui.js:2236): also skip `.sections-next` on `data-page="tests"`, or add a shell option, since the header
  carries Start. Keep the sidebar Now block (different source, now labelled differently).
- One `.tag` in ui.css (8px corners, 22 and 26px heights); remove the six local copies.
- check-ui.py: flag `border-radius: 50%` on `.pill` and `.btn` (`.tk-send`).
- `.reveal` and `.split` primitives (DIRECTION 4, 5): needed by proposals 1 and 3.
- Folding in sheets: an opt-in (for example `[data-fold]` on `dialog.start-sheet`) so long `.help` in the start and
  share sheets can fold. Or confirm that sheets stay unfolded by design.
- `.meta` is mono in ui.css:767, so every meta line on this page is mono words. The shared audit owns it.
- `.sections` chips are 999px (ui.css:729, 750): the shell pass owns them.
