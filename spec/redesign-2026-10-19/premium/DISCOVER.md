# Premium renovation: discovery (wider sources)

2026-10-19. Text-only research (web search and page fetches, no browser). Excludes what is covered elsewhere:
INSPO-VISUAL.md (kitchen, smoothui, bencho, amicro, aceternity, 21st) and the parallel agent (linear, vercel/geist,
raycast, stripe, arc). Status per source: **[F]** page fetched and read, **[S]** search summary only (secondary,
numbers unverified), **[U]** URL only, not read. Numbers below are the page's own unless marked *house* (our proposal).

**Read with DIRECTION.md.** Several premium techniques collide with DIRECTION 3 (shadows only on floats) and
DIRECTION 6 (no glow, glass, blur, grain, gradients, decorative icons, animation on load). Each such pattern is tagged
**[call: D3]** or **[call: D6]**: the user decides; nothing tagged is a default. Button rules (`.pill` 42px, 10px
corners, max 48px, no new style, orange takes dark text) are not negotiable: button ideas below are value changes only.

## 1. Ranked shortlist (relevance to a 16-18 study app)

1. **Duolingo streak write-ups** [F] https://blog.duolingo.com/how-duolingo-streak-builds-habit/ and
   https://blog.duolingo.com/streak-milestone-design-animation : a streak-extension animation plus milestone animations
   raised day-7 retention of new learners by +1.7%; two equippable freezes +0.38% DAU; early days matter most (2 to 3 is
   +50%, 200 to 201 is 0.5%); bigger moments only on milestone days (week, month, 100, year); a shareable card.
2. **Brilliant, via Rive's case study** [F] https://rive.app/blog/how-brilliant-org-motivates-learners-with-rive-animations :
   the streak animation is timed to the number counting up; learning paths are colour-coded per topic; one file ships
   to iOS, Android and web. Progress and celebration are part of the 2023 "game mechanics" redesign.
3. **Duolingo core tabs refresh** [F] https://blog.duolingo.com/core-tabs-redesign/ : the calm-layout case study.
   Problems were mixed header sizes, no type hierarchy, header art that "tells nothing", bordered segmented cards.
   Shipped: fewer text styles, tiered left-aligned headers, containers replaced with whitespace, flatter cards.
4. **NN/g progressive disclosure** [F] https://www.nngroup.com/articles/progressive-disclosure/ : show the few frequent
   options, defer the rest; two levels max ("beyond two typically have low usability"); label the trigger with clear
   scent; never split tightly coupled controls; staged (wizard) only for linear tasks.
5. **Pencil & Paper, filtering** [F] https://www.pencilandpaper.io/articles/ux-pattern-analysis-enterprise-filtering :
   a good default state first; applied filters as removable chips "in their original context"; counts on filter labels
   and per option; clear-all per filter and global; instant apply for small low-stakes lists.
6. **Khan Academy mastery** [S] https://support.khanacademy.org/hc/en-us/articles/47216131257997 : levels Attempted,
   Familiar, Proficient, Mastered; the reimagined app dropped mastery percentages for counts ("0 of 4 skills to
   Proficient"). Rationale: https://blog.khanacademy.org/?p=13201 (proficiency correlates with outside exams).
7. **College Board Bluebook** [S] https://blog.collegeboard.org/whats-bluebook and the quick start PDF
   https://satsuite.collegeboard.org/media/pdf/sat-suite-practice-quick-start-guide.pdf : fidelity reference only.
   Mark for Review (bookmark) and Answer Strikeout sit on the question; Annotate under More (top right) with
   calculator and reference; question menu shows skipped and flagged; strikeouts are undoable; line reader.
8. **Emil Kowalski** [F] https://emilkowal.ski/ui/7-practical-animation-tips , /ui/you-dont-need-animations ,
   /ui/building-a-toast-component , /ui/building-a-drawer-component : press `scale(.97)`; never enter from `scale(0)`
   (start at .9 or higher, example .93); tooltips 125ms ease-out, first one delayed, neighbours instant; under 300ms
   (180ms select beats 400ms); 2px blur hides a crossfade; origin-aware popovers; never animate keyboard-initiated
   actions; animate in inverse proportion to frequency.
9. **Rauno Freiberg, Invisible details** [F] https://rauno.me/craft/interaction-design : frequency vs novelty (a command
   menu lost its fade after "a couple of days"); macOS menus flash the accent on the picked row, then fade; interruptible
   motion; spatial consistency (things leave and return to where they came from); never hide what the thumb is on.
10. **Family, "Family values"** [F] https://benji.org/family-values : simplicity (fundamentals first, reveal as relevant),
    fluidity ("fly instead of teleport"), delight scaled to rarity. Trays with one job each and different heights;
    "Continue" morphs into "Confirm" via shared letters; only the changed part of a sentence animates; confetti once,
    on backup complete.
11. **Josh Comeau, Designing shadows** [F] https://www.joshwcomeau.com/css/designing-shadows/ : one light source, x:y
    offset 1:2, 3 to 5 layers, shadow colour hue-matched to the surface ("too grey" vs "just right"), small / medium /
    large tokens, `filter: drop-shadow` for shapes with tips.
12. **Josh Comeau, 3D button** [F] https://www.joshwcomeau.com/animation/3d-button/ : shadow / edge / front layers;
    front rests -4px, hover -6px (250ms `cubic-bezier(.3,.7,.4,1.5)`), active -2px in 34ms, release 600ms
    `cubic-bezier(.3,.7,.4,1)`; hover `brightness(110%)`; `outline-offset: 4px`; tap highlight off on phones.
13. **Jakub Krehel, Details** [F] https://jakub.kr/writing/details-that-make-interfaces-feel-better : concentric radii
    (outer = inner + padding), `tabular-nums`, `text-wrap: balance / pretty`, shadow-as-border tokens, 10% image
    outline, softer exits, 80 to 100ms stagger, icon swaps via opacity + scale + blur, interruptible transitions.
14. **NumberFlow** [F] https://number-flow.barvian.me/ : digits roll in the trend's direction, edge mask fade .25em
    tall / .5em wide, `respectMotionPreference` on by default, tabular nums. React only: port the idea, not the lib.
15. **NN/g empty states** [F] https://www.nngroup.com/articles/empty-state-interface-design/ and **skeletons** [F]
    https://www.nngroup.com/articles/skeleton-screens/ : status + learning cue + direct pathway; never "no items" while
    loading; nothing under 1s, skeleton for full pages under 10s, spinner for one module, progress bar over 10s.
16. **Things 3** [F] https://www.macstories.net/reviews/things-3-beauty-and-delight-in-a-task-manager/ : "dominated by
    white space"; an opened task comes forward while the list fades back; details hidden until opened; project progress
    shown in the sidebar; past events turn grey. Calm by subtraction.
17. **Tobias Ahlin, layered shadows** [F] https://tobiasahlin.com/blog/layered-smooth-box-shadows/ : smooth = five
    layers 1/2/4/8/16px at .12; sharp = same offsets at .25/.20/.15/.10/.05.
18. **Paco Coursey, craft** [F titles only] https://paco.me/craft : Spotify-style filters, exclusion tabs (clip-path
    tab transitions), iOS-style nested dropdown. Interview: https://ui.land/interviews/paco-coursey [U].
19. **Refactoring UI** [S] https://www.refactoringui.com/previews/labels-are-a-last-resort : "12 left in stock" beats
    "In stock: 12"; de-emphasise the rest to emphasise one thing.
20. **Apple HIG, tab bars** [S] https://developer.apple.com/design/human-interface-guidelines/tab-bars : filled symbols in
    a tab bar, outlined in a sidebar; the selected item gets the tint.
21. **Phosphor icons** [F] https://github.com/phosphor-icons/homepage : Thin, Light, Regular, Bold, Fill, Duotone;
    16px design grid; MIT; `@phosphor-icons/web@2.1.1` loads one stylesheet per weight (Regular + Fill pair).
22. **Dark elevation** [S] https://atlassian.design/foundations/elevation : higher surfaces are lighter; raised and
    overlay surfaces still carry a (weaker) shadow; desaturate accents; avoid pure white text.
23. **Lazyweb research** [F] https://www.lazyweb.com/research/how-common-are-streak-screens-outside-duolingo-2 : 51% of
    education apps (19 of 37) have a streak screen; about 12% of 809 apps have a celebration screen, clustered in
    habit, fitness and education. Advice: a streak only where a real daily habit exists (true for SAT prep).
24. **Confetti critiques** [S] https://uxplanet.org/why-confetti-celebrations-backfire-and-how-to-make-them-work-be838a6e7b8b
    and https://uxdesign.cc/when-and-how-to-add-confetti-to-your-product-ui-3c87ea541e8a : celebrate the user's goal, not
    the company's (no confetti for sign-up); small completions get a toast; never block the next action.
25. **Mochi** [S] https://borretti.me/article/first-impressions-mochi : UI praised over Anki; critique: the progress bar
    during review should be more prominent, and the total card count is missing. Directly applies to Words.
26. **Photomath** [S] https://www.designrush.com/best-designs/apps/photomath : steps collapsed by default, each step
    expands; the answer comes at the end of the steps. Applies to Explanation cards.
27. **UWorld SAT** [S] https://testprepinsight.com/reviews/uworld-sat-prep-review/ : praised for explanations that cover
    every answer choice and analytics that flag weak areas; criticised for text-only explanations.
28. **CSS-Tricks, grainy gradients** [F] https://css-tricks.com/grainy-gradients/ : feTurbulence `fractalNoise`,
    `baseFrequency .65`, `numOctaves 3`, then `contrast(170%) brightness(1000%)`, `isolation: isolate`. **[call: D6]**
29. **Superhuman** [S, unverified] https://blakecrosley.com/guides/design/superhuman : 100ms public target; optimistic
    UI; the command palette shows each action's shortcut every time, so shortcuts are learned by use.
30. **ui.land resources** [F] https://ui.land/resources : the directory behind several of the above (Brian Lovin,
    Ahmad Shadeed, Build UI, Maxime Heckel, Wojtek Witkowski). Use to find more craft writers.

Not reached or thin: Quizlet (no official write-up; the team's Dribbble page is in Browse next), Elevate (only "App of
the Year 2014" for "polished design" and "fascinating stats"), Speak, Synthesis (K-5, nothing on design), Magoosh,
Notion Calendar, Mercury, Ramp, Granola (no primary design write-ups found this round).

## 2. Patterns by category

Pages: Today `/`, Practice `/practice/` (+ session), Test window `/test/`, Tests `/tests/`, Review `/review/`,
Mistakes, Words `/words/`, Plan `/plan/`, Results `/results/`, Compete `/compete/`, Me `/me/`.

### 2.0 Calm, uncluttered layouts (the user's "premium means it is not clustered like this")

- **C1 One control row or none above the content.** Title, then at most one row of controls, then the thing itself.
  Frequent controls up front, rare ones one level down, never three levels (NN/g #4). Duolingo #3 got its calm by
  removing containers and text styles, not by adding polish. *Practice:* today the head is title + subject + points,
  then the search box + status line, then a preset chip row, then the tree head: four bands. Target: title row holding
  the subject switch and the search field; the skill list starts right under it.
- **C2 Filters behind one button.** A single "Options" (or "Filters 2") button with a count of what is set; the
  panel holds difficulty, status, count, minutes. Applied values show as removable chips in context with clear-all
  (Pencil & Paper #5); a good default so most students never open it. *Practice* (difficulty, status, length),
  *Review* list, *Mistakes*, *Words* deck filters, *Compete* leaderboard scope.
- **C3 The list is the picker.** No separate presets row and no boxed sections: skills are dense rows (32-36px) with
  a checkbox at left and mastery ticks + a count at right; presets become the first rows of the same list
  ("Recommended", "Weakest 3", "Mixed review") or a menu on the Options button. The pick feeds one summary in the Start
  column ("3 skills, 10 questions, 15 min" + Start). *Practice skill picker first*; same shape for Words decks.
- **C4 Chip row that collapses on pick** (Paco's Spotify filters #18): tap "Math", the sibling chips slide away, an x
  chip clears it, and the next level's chips take their place. One row, never two. *Practice* subject > domain,
  *Words* deck types, *Review* tabs if they outgrow a seg.
- **C5 Space between groups, density inside.** Groups separated by 24-32px of space (*house*), rows inside them tight,
  no card around every group (Duolingo #3 "flat" direction; Things #16). A hairline or a gap, never both.
- **C6 Hide empty, never draw a placeholder.** A region with nothing to say is absent, not an empty bar. Only the
  page's main content gets an empty state (2.8). *Practice:* `#sline`, `#linkNote`, `#banners`, `#ready`, the R&W block
  and an empty "Your sets" stay hidden until they have content; *Today* cards with no data collapse.
- **C7 One focal point, one orange.** Equal-weight chips and links are the clutter: rank them. One primary, at most
  one quiet link row; the rest goes under a clearly labelled "More" (NN/g: label the trigger). *Practice* `.pr-links`.
- **C8 Labels are a last resort** (#19): "14 due today", "620 estimate", "3 of 8 skills proficient" instead of
  label: value pairs. Fewer words per row is most of the calm. *Today, Results, Plan, Words.*
- **C9 Staged disclosure only for linear tasks** (NN/g): Plan wizard, Diagnostic onboarding. Practice's controls are
  coupled (skills, length, minutes), so they stay on one screen, folded, not split into steps.

### 2.1 Depth

- **D1 Hue-matched layered shadows.** Never pure black; tint to the surface hue (Comeau #11: `hsl(220 60% 50%)` "just
  right" vs black "too grey"); 3 layers for medium, 5 for large, offsets doubling (Ahlin #17). For our warm palette,
  *house*: graphite-brown `hsl(30 10% 20% / a)`. Apply to `--shadow-float` and `--shadow-pop` first (DIRECTION allows).
- **D2 Shadow as border on cards.** Krehel #13: `0 0 0 1px rgb(0 0 0/.06), 0 1px 2px -1px rgb(0 0 0/.06), 0 2px 4px
  rgb(0 0 0/.04)`; hover .08/.08/.06; dark `0 0 0 1px rgb(255 255 255/.08)`, hover .12. Gives `.card` a lift without a
  heavier line. **[call: D3]** (cards are tile + hairline today). Trial on *Tests* paper tiles and *Today* Up next.
- **D3 Drop-shadow for shapes with tips** (`filter: drop-shadow`, 3 stacked, Comeau #11): `UI.why` popovers and
  tooltips with arrows, so the arrow carries the shadow.
- **D4 Figure outline.** `outline: 1px solid rgb(0 0 0/.1); outline-offset: -1px`, white 10% in dark (Krehel #13).
  Question figures and graphs, *Tests* preview tiles, share cards.
- **D5 Grain / noise** (#28). Only plausible on a share card or certificate image. **[call: D6]**; default: skip.

### 2.2 Buttons (value changes to `.pill`, `.btn`, `.quiet` only)

- **B1 Lit edge on `.pill`.** `inset 0 1px 0 rgb(255 255 255/.35)` (top highlight) + `inset 0 -1px 0 rgb(0 0 0/.10)`
  (bottom shade) + a 1px ring one step darker than the orange (*house* values; the recipe is the standard layered
  shading, see the CSS examples in search results and Comeau's edge layer #12). Not a gradient, not a glow.
- **B2 Asymmetric press.** Down fast, back slower: Comeau presses in 34ms and releases in 600ms; Krehel "you don't
  open a door the way you close it". Keep DIRECTION 7's 120ms `scale(.97)` press, add a ~200ms release and let the
  inset shadow deepen while pressed. Every `.pill` and `.btn`.
- **B3 Raised edge button** (Comeau #12; *house* values): front 3px above a darker edge, hover -4, active -1, in 42px.
  The Duolingo look. **[call: D6]** and taste risk (may read childish); if tried, only on the session Check / Next.
- **B4 Hover.** Comeau brightens 110%; ours is a 6% darker fill. Keep ours: brightening orange under dark text lowers
  contrast.
- **B5 Label morphs.** Check > Next, Save > Saved: crossfade with a 2px blur (Emil #8) or animate only the changed
  letters (Family #10). `UI.saving` already swaps text; give it the crossfade. Blur here is **[call: D6]**.
- **B6 Phone hygiene** (Comeau): `-webkit-tap-highlight-color: transparent`, `user-select: none` on buttons;
  `outline-offset` 2-4px on `:focus-visible`.

### 2.3 Motion (map onto DIRECTION 7, do not add a second scale)

- **M1 Frequency rule** (Emil, Rauno, Family): the more often seen, the less it moves. Answer picks, question
  navigation, list hovers: no motion beyond the 120ms press. Set end, streak extended, new best: motion.
- **M2 Never animate keyboard-initiated actions** (Emil). Test window and session shortcuts, Review j/k, Words keys.
- **M3 Origin-aware popovers** from `scale(.95)` (DIRECTION has the scale; add `transform-origin` at the trigger):
  Review "Start ▾", `.dd` menus, sidebar menus.
- **M4 Tooltip chain:** first waits (ours 400ms), neighbours open instantly, 125ms ease-out from `scale(.97)` (Emil).
  Rail tooltips, heatmap cells, chart dots.
- **M5 Soft exits:** exits smaller and quicker than entries; Krehel slides out to -70% with opacity and 4px blur.
  DIRECTION 7 already has exits at 75%; blur part **[call: D6]**.
- **M6 Stagger 80-100ms** (Krehel) only when a state change reveals a list: the session Summary rows, the Results
  report after a test. Never on page load (DIRECTION 6).
- **M7 Interruptible:** transitions, not keyframes, for anything reversible (folds, sidebar collapse, sheets, toasts).
- **M8 Spatial consistency** (Rauno, Family): the Review question opens from its row and returns to it; tabs slide
  toward the tapped side; a phone sheet rises from the button that opened it.
- **M9 Change only what changed** (Family): "7 of 20" rolls the 7 only; "14 due" rolls the digits only.

### 2.4 Icons

- **I1 Outline at rest, filled when current** (Apple HIG #20): phone bottom tabs show the filled twin on the current
  tab; the sidebar keeps outlines plus the orange current row. Draw filled twins for the 5 tab icons in `ICON`
  (ui.js ~427, 24 grid, 1.6 stroke).
- **I2 Phosphor as the reference set** (#21) if new glyphs are needed: the Regular / Fill pairing is exactly I1.
  Keep the hand-drawn set; copy geometry rather than adding a font. Icons stay functional (nav, status, action),
  never decorative (DIRECTION 6).
- **I3 Icon swaps animate opacity + scale + blur** (Krehel; values not stated, *house* 150ms from `scale(.8)`):
  bookmark > bookmarked, copy > check, play > pause, flame outline > filled on streak extension.
- **I4 Status pairs a glyph with colour** (already a rule): check, x, dash, bookmark on question chips and rows.

### 2.5 Highlights and selection

- **H1 Bluebook fidelity in the test window** (#7): strikeout on choices (undoable), bookmark on the question,
  question menu with skipped and flagged, Annotate highlight + note, line reader. No premium styling here beyond crisp
  states; match Bluebook first.
- **H2 Pick flash:** macOS menus flash the accent on the chosen row, then fade (Rauno). For `.dd` and menus: one 80ms
  `--wash` flash before close (*house* timing).
- **H3 Focus the open item:** Things 3 brings the opened task forward while the list recedes (#16). Review and
  Mistakes from 1280px: the selected row sits on `--paper` with `--shadow-float`, siblings stay quiet.
- **H4 Text selection and search hits:** `::selection` on `--wash-2`, search matches in Practice and Words marked
  with `--wash` and 2px corners (*house*).

### 2.6 Feedback and celebration

- **F1 Four tiers by rarity** (Family, Emil, confetti critiques):
  0 every answer: instant state, 120ms press, nothing else. 1 set or Words session done: Summary with rolling figures
  and one plain line. 2 first activity of the day: the streak number rolls up and the flame fills, timed together
  (Duolingo +1.7% D7; Brilliant syncs the animation to the count). 3 rare (streak 7 / 30 / 100 / 365, first full
  test, new best estimate, contest podium): one short confetti burst or a share card. Tier 3 confetti **[call: D6]**.
- **F2 Right and wrong without theatre.** Checked option settles (`scale(.98)` to 1, 160ms *house*) with a check
  glyph; a wrong pick gets the x glyph and the correct choice turns orange (settled rule). No shake, no red flash, no
  sound by default. Explanation opens in place.
- **F3 Explanation like Photomath** (#26): the key step first, the rest folded per step; with UWorld (#27), say why
  each wrong choice fails when the item data has it (UI only if the data exists).
- **F4 Small wins are toasts** (critiques #24; Sonner #8: stack offset 14px per toast, scale 1 - .05 x index, 400ms
  in, 4s, pauses on hover and hidden tab): "Saved", "Added to Words", "Plan updated".
- **F5 Share card for milestones** (Duolingo): streak milestones, new best estimate and contest rank render to the
  existing `/share` card, savable without leaving the page.
- **F6 Celebrate the student's goal, never ours:** nothing for sign-up, plan created or settings saved.

### 2.7 Progress, mastery and streaks

- **P1 Counts over percentages** (Khan #6): "3 of 8 skills proficient", "12 of 20 done". Plan, Practice tree head,
  Results skill list.
- **P2 Four mastery steps on a tick meter** (Khan levels; `.meter.ticks` exists): Practice skill rows, Results.
- **P3 Make days 1-7 feel big** (Duolingo: early increments carry the most weight); milestone moments only on 7, 30,
  100, 365. Today sidebar streak, Me.
- **P4 Streak freeze** (+0.38% DAU with two equipped): needs server work, outside UI-only. Park; tell the user.
- **P5 Progress where you navigate** (Things shows project progress in the sidebar): a small goal ring on the sidebar
  Today card and on the Plan week strip.
- **P6 Session progress louder, with the total** (Mochi critique #25): "7 / 20" plus a bar in Words study and the
  practice session top bar.
- **P7 Topic colour per path** (Brilliant) **[call: D6 / calm colour]**: orange stays the only accent; prefer
  difficulty tints and glyphs that exist.

### 2.8 Empty, loading and error states

- **E1 Main-content empty state = status + cue + action** (NN/g #15, e.g. "Star your favorites to list them here"):
  Mistakes ("Questions you miss land here" + Start practice), Words mine, Review saved, Compete history.
- **E2 Never "no items" while loading; skeleton only if the wait passes ~300ms** (*house* delay; NN/g: nothing under
  1s): Practice `.skel-tree`, Results, Review list. Placeholders mirror the final layout; no shimmer sweep.
- **E3 First-use pointer:** Family shows an animated arrow once in an empty in-app browser; ours: a one-time hint
  dot on the action, gone after first use.
- **E4 No spot illustrations.** At most one functional glyph in a 40px tile.

### 2.9 Data viz and numbers

- **N1 Rolling digits on change, never on load** (NumberFlow #14): estimate score, streak, Words due, points. Port as a
  small vanilla roller: per-digit columns, direction from the trend, mask fade .25em / .5em, tabular nums, off under
  reduced motion.
- **N2 Tabular figures** wherever numbers stack or tick (Krehel): Archivo with `tnum`, DM Mono already.
- **N3 Scrub readout** (Family flips the change arrow while scrubbing a price chart): Results score trend, Me
  activity heatmap readout line shows the delta with an up / down glyph.
- **N4 A number leads, the chart is evidence** (INSPO-VISUAL rule 8 holds): Results estimate out of 800, then the trend.

### 2.10 Dark mode

- **K1 Higher is lighter** (#22). We have paper `#1A1917` < tile `#242220`; add one lighter step for dialogs, menus
  and sheets, keep a weaker shadow under it.
- **K2 Rings instead of shadows on dark cards** (Krehel: 8% white ring, 12% on hover).
- **K3 Desaturate accents, no pure white text.** Ink `#ECE8E1` is right; check orange fills and `--wash` for glare on
  large areas.
- **K4 Figure outlines flip to white 10%** (D4).

### 2.11 Phone feel

- **Ph1 Trays with one job** (Family): title + dismiss, one action, consecutive trays differ in height. Practice Start
  sheet, Review Start ▾, Words options, Plan day edit.
- **Ph2 Sheet physics** (Vaul #8): 500ms `cubic-bezier(.32,.72,0,1)` (iOS sheet), momentum dismiss, damped drag past
  the top, no drag until content is scrolled to top. Phone sheets only; dialogs keep DIRECTION 7's 240ms.
- **Ph3 Keep the thumb's target visible** (Rauno): slider value shows above the thumb, drag survives leaving the
  track. Plan "A study day" slider, minutes picker.
- **Ph4 Tabs:** filled current icon (I1), content slides toward the tapped tab (Family).
- **Ph5 Toast swipe** (Sonner): dismiss on distance or velocity over .11, friction when dragged the wrong way.

## 3. Browse next (for a browser agent, in this order)

1. **Duolingo design posts** https://blog.duolingo.com/core-tabs-redesign/ (the four explored directions, before and
   after headers, flat quest cards) and https://blog.duolingo.com/streak-milestone-design-animation (Fire Duo motion,
   share card): look at hierarchy with no containers, and how the milestone moment is framed and timed.
2. **Brilliant** https://rive.app/blog/how-brilliant-org-motivates-learners-with-rive-animations (embedded videos:
   streak count + animation sync, path nodes) and https://brilliant.org (home and a course page): the one-card "today"
   lesson, the path, how much is on the first screen.
3. **Bluebook** https://satsuite.collegeboard.org/media/pdf/sat-suite-practice-quick-start-guide.pdf : screenshot pages
   of the toolbar, question menu, strikeout and bookmark, for test-window fidelity.
4. **Comeau demos** https://www.joshwcomeau.com/animation/3d-button/ and https://www.joshwcomeau.com/css/designing-shadows/
   : press the button, move the elevation slider; judge B1-B3 and D1 by feel.
5. **Emil live demos** https://sonner.emilkowal.ski , https://vaul.emilkowal.ski , https://emilkowal.ski/ui/7-practical-animation-tips
   (side-by-side videos): toast stack, sheet physics, ease-in vs ease-out, blur crossfade.
6. **Craft videos** https://paco.me/craft (Spotify Filters and Exclusion Tabs: the C4 model for Practice),
   https://rauno.me/craft/interaction-design , https://benji.org/family-values (trays, text morph, confetti once).
7. **NumberFlow** https://number-flow.barvian.me : the trend and continuous demos; decide N1 timing for the estimate.
8. **Galleries** (log-in walls likely; take what is public): https://mobbin.com/explore (search "streak", "quiz",
   "progress", "empty state", "filter"), https://refero.design (search "success", "filter", "empty"),
   https://dribbble.com/Quizlet (Checkpoint and level-up shots), https://dribbble.com/search/quiz-result ,
   https://dribbble.com/search/study-app-dashboard , https://recent.design (App Screenshots and Web Interface sections; godly.website
   now redirects here), https://www.lapa.ninja , https://land-book.com . saaspo.com returned 403 to a fetch.

## 4. Avoid (reads as AI slop, or childish for 16-18)

- Take Duolingo's mechanics (streak, extension moment, milestone days, share card, rolling numbers), not its tone:
  no mascot, no cartoon characters or spot illustrations, no "Amazing!" copy, no bouncing on every correct answer.
- No currencies or lives: XP, gems, coins, hearts. Practice is never rationed or punished.
- No guilt mechanics: no streak-loss nags, no "you will lose" banners, no red counters. A freeze, not a threat.
- No confetti on routine completions, sign-up, plan creation or settings. Rare and short, or none.
- No shake or red flash on a wrong answer; no sound on by default.
- No glass, aurora gradients, glowing borders, spotlight cursors, 3D tilt cards, particle backgrounds, animated
  gradient text, neumorphism (low contrast fails our readers).
- No motion on page load, on keyboard-driven actions, or on things seen hundreds of times a session.
- No shimmer skeletons on fast loads; no placeholder bars for empty regions.
- No decorative icons beside headings, no emoji, no Title Case, no exclamation marks, no em dashes.
- Nothing premium in the test window: Bluebook fidelity wins, no celebration mid-test, no chrome.
- No three rows of controls before content; no row of ten equal chips; no box around every group.
