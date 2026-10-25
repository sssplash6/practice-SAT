# Motion system: premium pass, 2026-10-19

The user: "fully renovate the web ui, use cool buttons, motions, animations ... it should feel premium". This file
**supersedes DIRECTION.md section 7** and the ui.css header rule 10 ("motion is entry only", "nothing animates on
load", one curve, no bounce). Everything else in DIRECTION stands. Lenses: Emil Kowalski primary (a study tool used
daily), Jakub Krehel secondary (enters and exits), Jhey Tompkins only for the rare reward moments. Opacity and
translate only: no filter, no blur (DIRECTION section 6), so the common `blur(4px)` enter recipe is not imported.
Plan only. The lead builds it in the shared files; page passes opt in and never write their own keyframes.

## 1. Principles

1. **Motion is state.** Each animation answers "what changed, and where did it go". Nothing idles, nothing loops (a spinner only while waiting, and only after 300ms).
2. **Content never waits.** The new state is in the DOM and painted inside the speed budgets (Check to verdict 100ms, Next to stem 50ms, CLS 0.02); motion decorates it and never holds focus, input or a promise.
3. **Frequency sets the budget.** 100+ a day (keys, option pick, Next): 0 to 120ms, colour or opacity. Tens a day (menus, tabs, sheets, pages): 140 to 260ms. Rare (set finished, goal met, score ready): up to 600ms and the one bounce.
4. **Keyboard is instant.** A change from a key, including Enter or Space on a button (`event.detail === 0`), skips movement. `slideMark` already works this way and is the pattern.
5. **Exits are quieter than entries.** About 70% of the time, half the distance, never a spring.
6. **Compositor only.** transform and opacity; clip-path and stroke-dashoffset for one-shot reveals. Never width, height, top, left, margin or padding; the three exceptions are named in 4.3.
7. **Motion starts where the hand was.** Popovers grow from their trigger side, phone sheets from the bottom edge, the nav mark slides from the old item to the new one. One axis per move, no ping-pong.
8. **Springs for what a hand moves** (press release, indicators, drag release); the pop spring for rewards only; `--ease` for the rest.
9. **The test window is Bluebook.** Nothing moves there that Bluebook does not move.
10. **Reduced means calm, not broken.** Movement goes; short fades and fills that explain a state stay.

## 2. Tokens (ui.css `:root`)

| Token | Value | Use |
|---|---|---|
| `--m-press` | 100ms | press down |
| `--m-fast` | 140ms | hover, colour, tooltips, small exits |
| `--m-base` | 200ms | popover, menu, toast, crossfades, page fade |
| `--m-slow` | 260ms | sheet, morphs, rail, fold |
| `--m-reveal` | 480ms | one-time draw-ins: meters, charts, heatmap |
| `--m-moment` | 600ms | rewards: count-up, gauge sweep (was 1200) |
| `--m-tip` | 400ms | tooltip delay; for 500ms after a tip closes the next one opens with no delay and no fade |

Exits run at 0.7x their entry (`calc(var(--m-base) * .7)`: 140 / 180ms). Keyboard and exam paths use 0ms.

Curves:
- `--ease: cubic-bezier(.23, 1, .32, 1)` (kept): every enter, exit, hover and fill.
- `--ease-move: cubic-bezier(.77, 0, .175, 1)`: something already on screen travelling A to B (nav mark, rail edge, FLIP, hero morph).
- `linear`: timed fills only (hold-to-strike, toast countdown, between-bar).
- Three springs, generated from spring physics (perceptual duration, bounce; the solver is `UI.motion.spring`, 4.1).
  **A spring is only correct at its own duration.** At any other duration the curve stretches and the overshoot
  lands late, so each has a paired duration token. Declare `var(--ease)` first as the fallback.

```css
/* --spring: bounce 0, no overshoot. Indicators, phone sheet, folds, roll. Duration --spring-d: 370ms */
--spring: linear(0, 0.004 1.3%, 0.02 2.8%, 0.048 4.5%, 0.085 6.3%, 0.16 9.3%, 0.45 19.8%, 0.54 23.5%, 0.615 27%, 0.681 30.5%, 0.737 34%, 0.787 37.8%, 0.829 41.5%, 0.871 46.3%, 0.905 51.2%, 0.932 56.8%, 0.954 63%, 0.981 76.8%, 1);
/* --spring-soft: bounce .2, 1.5% overshoot. Press release, seg thumb, tab underline. Duration --spring-soft-d: 420ms */
--spring-soft: linear(0, 0.006 1.5%, 0.026 3.3%, 0.057 5%, 0.103 7%, 0.201 10.5%, 0.525 21%, 0.62 24.5%, 0.704 28%, 0.771 31.3%, 0.827 34.5%, 0.877 38%, 0.917 41.5%, 0.951 45.5%, 0.979 50%, 0.998 55%, 1.009 60.5%, 1.015 73.8%, 1);
/* --spring-pop: bounce .35, 6.8% overshoot. Rewards only, never controls or the runner footer. Duration --spring-pop-d: 570ms */
--spring-pop: linear(0, 0.008 1.5%, 0.032 3%, 0.067 4.5%, 0.12 6.3%, 0.232 9.3%, 0.504 15.8%, 0.613 18.5%, 0.721 21.5%, 0.806 24.3%, 0.879 27%, 0.937 29.8%, 0.987 32.8%, 1.023 35.8%, 1.058 41%, 1.068 47.3%, 1.06 52.5%, 1.021 67.3%, 1.004 76.3%, 0.996 89%, 1);
```

Distances: `--m-rise: 8px` (block entry), `--m-nudge: 4px` (small entry, every exit), `--m-pop-from: .96`
(popover, menu), `--m-press-s: .97` (buttons, chips), `--m-press-l: .985` (rows: `.opt`, `.choice-row`, `button.stat`),
`--m-sheet-from: .98`. Never scale from 0; the lowest start is .6, rewards only, on elements of 48px or less.
Stagger: `--m-step: 30ms`, at most 6 items (the 7th on arrive with the 6th), the last starts by 150ms. Chart bars:
16ms, at most 14 steps.

| Kind | Enter | Exit |
|---|---|---|
| Page block | opacity 0, y +8px, 200 ease | none (leaves with the page) |
| Popover, menu | opacity 0, scale .96 from the trigger side, 160 ease | opacity, 100 |
| Sheet (desktop) | opacity 0, y +8px, scale .98, 260 ease | opacity, y +4px, 180 |
| Sheet (phone) | y 100%, 370 spring | y 100% from where the finger left it, 200 ease |
| Toast | opacity 0, y +8px, 200 ease | opacity, y +4px, 140 |
| List row | opacity 0, y +4px, 200 ease | opacity, scale .98, 140 |
| Tooltip | opacity, 120 | instant |

**Reduced** (`prefers-reduced-motion` or `html[data-motion="reduce"]`): distance tokens 0, scale tokens 1, springs
swap to `--ease`, durations capped at 120ms. Entries become short fades, fills still fill, page transitions stay off
(head.js), JS tweens (count-up, gauge, roll) jump to the end. In the catalogue, "fade" means that 120ms fade.

## 3. Catalogue

Hooks name file and function. "Once" means once per page view unless stated. Every row is skipped on keyboard
paths unless it says "keys too".

### 3.1 Navigation (cross-document view transitions; this is a multi-page app)

| Moment | Trigger | What moves, duration, curve | Reduced | Hook |
|---|---|---|---|---|
| N1 page change | link to another page | `main`: old fades out 100, new fades in 200 ease, no travel (M1 supplies it). `.bar .pbar #tabs .side` stay still (named, `animation: none`, as today) | off | ui.css VT block |
| N2 nav marker | same | one `.nav-mark` span inside the current `.side-item` (and `tab-mark` in the current `#tabs` link), named; it slides and resizes from the old item to the new, 260 ease-move. The current fill moves from the item onto the span | off | ui.js `navItem()`, the tabs builder (~1964); ui.css |
| N3 card into detail | click on `[data-vt-src]` | `pageswap` names the clicked element `hero`; `pagereveal` names `[data-vt-dst]` `hero` if it is painted; the group morphs 260 ease-move, old and new crossfade 160 inside it. Pairs: Results row to report header, Tests card to test start, Review list row to walk. No target: plain N1 | off | head.js listeners (they exist for quieting); pages add the attributes |
| N4 back, forward | `navigation.activation.navigationType === 'traverse'` | type `back`: main fades only, 140 | off | head.js `pagereveal` |
| N5 page title (trial) | static `<h1>` on both pages | first `main h1` named `page-title`: stays put, crossfades 160 while content rises. Cut it if it reads as text crossfading with travel; most pages build their h1 in JS and will not get it | off | head.js `pagereveal` |
| N6 theme switch | Theme pref | same-document VT, root crossfade 200 ease | instant | ui.js `look()` |
| N7 into the test window | any link to `/test/` | none: Bluebook starts on a cut | none | head.js: `navigation: none` on `/test/` |

### 3.2 Mount

| Moment | Trigger | What moves | Reduced | Hook |
|---|---|---|---|---|
| M1 entry stagger | first visible paint of a page view | direct children of `[data-m="stagger"]`, max 6: opacity 0, y +8px, 200 ease, step 30. The block holding the page's primary (`data-m-now`) is never delayed. Never blocks input | fade | `UI.motion.stagger()`, run from `UI.whenVisible` (a prerendered page must not play it while hidden) |
| M2 skeleton to content | data replaces a `.skel` | new content fades in 160 ease, no travel (the skeleton held the final size) | instant | `UI.motion.enter(host, 'fade')` where pages swap |
| M3 cache repaint | `UI.cached` repaint, JSON changed | no entry; changed figures roll (D1) | n/a | ui.js `cached()` passes a repaint flag |
| M4 bfcache restore | `pageshow` persisted | nothing replays | n/a | `UI.motion.once()` |

### 3.3 Lists

| Moment | Trigger | What moves | Reduced | Hook |
|---|---|---|---|---|
| L1 row added | word added, mistake logged, note saved | row opacity, y +4px, 200 ease; rows below move by FLIP 200 ease-move | fade | `UI.motion.flip(list, mutate)` |
| L2 row removed | fixed, deleted, task done | row opacity and scale .98, 140, then removed; the gap closes by FLIP 200 ease-move; Undo re-enters it as L1 | instant | same |
| L3 reorder | `UI.table` sortBy, sort chips | FLIP translate 220 ease-move, at most 40 rows (more: instant); the sort arrow rotates 140 | instant | kit.js `table()` sortBy, draw |
| L4 filter | filterBar, legend, chips | list body crossfades 120; no FLIP | instant | kit.js `filterBar()` commit, `legend()` |

### 3.4 Controls

| Moment | Trigger | What moves | Reduced | Hook |
|---|---|---|---|---|
| C1 press | pointer down | `.pill .btn .ibtn .chips>* .seg>* .tool`: scale .97 in 100 ease; release on spring-soft 420 (asymmetric: the transition sits on the base state, `:active` overrides it). Rows `.opt .choice-row button.stat`: .985 | colour only | ui.css |
| C2 hover | fine pointer only | fill colour 140 ease; no lift, no shadow growth, no scale | same | ui.css |
| C3 saving | `UI.saving` | label swaps with a 4px rise, 160 ease (exists); a 14px ring spinner only after 300ms (700ms linear turn, only while waiting); done: the check draws (stroke-dashoffset, 240 ease); back to rest by a 160 crossfade after 1200 | text swap; spinner `animation: none` (a static ring: the `.01ms` net would strobe it) | kit.js `saving()` |
| C4 busy | `aria-busy` on pills, sheet actions | opacity .6 (exists), plus the C3 spinner after 300ms | same | ui.css `[aria-busy]`, kit.js `sheet()` foot |
| C5 tabs | click | underline slides on spring-soft 420 (keys: at once, exists); panel: new fades in 120, old hidden at once | instant | kit.js `slideMark()`, `tabs()` select |
| C6 seg | click | thumb on spring-soft 420; label weight at once | instant | kit.js `slideMark()` |
| C7 switch | click | knob x on spring 370; track colour 140 | instant | ui.css `.switch` |
| C8 chips, choice-row | click | fill and ring 140; a count `.n` rolls (D1) | instant | ui.css; kit.js `choices()` count |
| C9 checkbox | click | the tick draws, 160 ease | instant | ui.css, kit.js `triCheck()` |
| C10 disclosure | `details.fold`, `.card-fold`, `.sm-fold`, `.refd-g` | chevron 160 ease (exists); on open the content fades in with y +4px, 160 (`details[open] > :not(summary)`); height snaps; close is instant | instant | ui.css |
| C11 tooltip | hover 400ms, focus at once | opacity 120; warm window (above); out instant; never moves | same | kit.js `tooltip()` show |
| C12 option pick | click, A to D | ring and fill 120 ease (was 160); press .985; keys: no transition | instant | ui.css `.opt`; `html[data-input="key"]` |
| C13 Check becomes Next | footer button changes | label crossfade with a 4px rise, 140 ease, width held; keys too (blocks nothing) | instant | question.js `splitCheck()` set, runner.js `syncFoot()` |

### 3.5 Surfaces

Every surface closes its state at once (layer stack spliced, focus restored, promise resolved) and only then
animates the orphaned node out, removing it at the end. A second close cancels the first.

| Moment | Trigger | What moves | Reduced | Hook |
|---|---|---|---|---|
| S1 sheet, desktop | `UI.sheet`, `UI.confirm` | enter 260 ease, backdrop 200; exit 180, backdrop 140 (section 2 table). CSS transitions with `@starting-style` and `display`/`overlay` allow-discrete, not keyframes; without `overlay` support (Firefox) the exit is instant | fade | ui.css `dialog.sheet`; kit.js `sheet()`: remove the node after the exit, not in the `close` handler |
| S2 sheet, phone | same, under 760px | enter y 100% on spring 370; drag follows the finger (exists); release under 90px and slow: springs back on spring 370 (today it snaps); over 90px or a flick (over .5px/ms): leaves from where it is, 200 ease; upward drag gets friction (1/4, max 12px) | fade | kit.js `sheet()` pointer handlers, `drop()` |
| S3 popover | `UI.pop`, `UI.why` | opacity, scale .96 from the trigger side, 160 ease; `place()` sets `data-side` and `transform-origin` (it already flips above the trigger; the entry still drops from +4px today); exit opacity 100, `hidePopover()` deferred to its end. Phone: S2 | fade | kit.js `place()`, `layer()` close |
| S4 menu | `UI.menu` by click | as S3 at 140; opened by a key: instant | instant | kit.js `menu()` |
| S5 palette | Mod+K | instant; opened by a click on Search: opacity 120 | instant | ui.css `dialog.palette` (was `pop .16s`) |
| S6 toast | `UI.toast` | enter and exit as the table; the rest of the stack closes up by FLIP 200 ease-move; undo toasts carry a 2px countdown line (scaleX 1 to 0, linear, 6s) that pauses with the timer | fade; the line runs regardless of `off()` (it is the timer) | kit.js `toast()` close, run, pause |
| S7 banner | `UI.banner` | enter as a page block; dismiss: opacity 140, then the height collapse (exception E2) | instant | kit.js `drawBanner()` |
| S8 sidebar overlay | 760 to 1099 toggle, rail peek | enter x -12px and opacity, 200 ease (was -24px); close: the scrim fades 140, the panel returns at once (the pointer has left) | instant | ui.js `openOverlay()`, `closeOverlay()` |
| S9 tour | step change | the ring moves by transform 260 ease-move; its size snaps (E3); the 9999px shadow never animates | instant | tour.js `.tour-ring` |

### 3.6 Data

| Moment | Trigger | What moves | Reduced | Hook |
|---|---|---|---|---|
| D1 changed figure | `UI.roll` | digits roll on spring 370 (was 220 ease) | text swap | kit.js `roll()` |
| D2 hero figure | first view of a new score or summary | count-up 600 ease (opt-in); scores count from their floor (400 total, 200 section), not 0 | end value | kit.js `countUp()` |
| D3 meters | first reveal in view; `set()` | the fill is `transform: scaleX(var(--p))` from the left (or `clip-path: inset()` where rounded ends must stay crisp); first reveal 480 ease, a change 240 ease; `.ticks` blocks light left to right, step 20, max 10 | fills in 120 | ui.css `.meter-bar > i`, `.mbar > i`; runner.css `.rn-between-bar > i`; report `.rp-mb i`; session `.bar2`, `.fill`; kit.js `meter()` first flag |
| D4 ring | Today ring changes | `@property --m-ring` (number); the arc sweeps old to new, 600 ease | end state | ui.css `.ring`; ui.js `todayCard()` |
| D5 line chart | first draw only | paths `pathLength=1`, stroke-dashoffset 1 to 0, 480 ease; markers and labels fade 120 from 300ms; bands fade 200 | fade | charts.js `sized()` passes `first` (it redraws on every resize); `UI.motion.draw(svg)` |
| D6 bar chart | first draw only | bars scaleY from the baseline (`transform-box: fill-box`), 360 ease, step 16, max 14; `set()`: crossfade 120 | fade | charts.js `barChart()` |
| D7 gauge | first view of a new band | sweep 600 ease (was 1200 cubic) | end state | charts.js `gauge()` show |
| D8 heatmap | first draw only | one clip-path wipe left to right over the grid, 480 ease: one animation, not 182; the readout line updates at once | fade | charts.js `heatmap()` |
| D9 scale band, dots | first draw | `.scale-band.grow` 480 ease (was 600); `.dots i.in`: scale .6 to 1 on spring-pop (was 0 to 1.35 keyframes); `out` fades | instant | ui.css |
| D10 status cells | state change (fixed, saved) | colour 140; dense grids (strip, atlas, heat cells) never get entry motion | same | ui.css `.cell` |

### 3.7 Feedback moments (practice, review, Today; the test window has none)

The DOM is painted inside the budget and the animation starts on that frame. Only a live reveal plays: question.js
sets `data-m-live` in `take()` and clears it on the next paint, so a revisit, Review replay or restored verdict is static.

| Moment | Trigger | What moves | Reduced | Hook |
|---|---|---|---|---|
| F1 right | Check, right | key option fills 120; its letter disc scales .85 to 1 on spring-pop (the only bounce in the flow); the verdict rises 4px, 200 ease (was 8px keyframes); the head glyph scales .8 to 1 on spring-pop | fade | question.js `reveal()`, `vHead()`; ui.css `.ws.right[data-m-live] .opt.ok .l` |
| F2 wrong | Check, wrong | the key fills as F1 with no pop; the pick dims to .42 and strikes, 160; the cross is static. No shake, no red | same | question.js `reveal()` |
| F3 wrong try | retry mode | the reason line under the option rises 4px, 160; the cross appears | instant | question.js `wrongTry()` |
| F4 mistake fixed | `fb.closed` | `.v-fixed` enters on spring-pop (was scale .96, 200); its check draws 280 ease after 120; one amber wash fades out over 900 ease; the sidebar Review count rolls when the shell refreshes | static | question.js `verdictSlot()`; runner.css `.v-fixed` |
| F5 streak extended | fresh streak above the cached one | the number rolls; the flame fills soft to amber 300 and scales .85 to 1 on spring-pop, once | static | ui.js `paintSide()`: it rebuilds the card with `replaceWith`, so diff old and new `shellData` and set a one-shot `.m-up` on the new node |
| F6 goal met | minutes cross the goal | the ring completes (D4), then one beat: scale 1, 1.06, 1, 400 ease; the meter turns done (colour 240); once a day (localStorage) | static | same diff; `todayCard()` |
| F7 set finished | session Summary | M1 over its 4 blocks (score, what changed, next, review), step 40; the right count counts up 600 (the "/ n" is static); the Next pill is in the first block, never delayed; once per sitting (sessionStorage `satf.m.sum.<sid>`) | static | practice/session/session.js `summary()` |
| F8 test scored | Report, first view per sitting | total counts up from 400, 600 ease; sections follow 80 later; gauge D7; no confetti | static | results/report/page.js |
| F9 achievement | event toasts | a toast (S6) whose glyph scales .8 to 1 on spring-pop | fade | ui.js event toasts |
| F10 next question | Next by pointer (practice) | the new question goes opacity .5 to 1, 120 ease, no travel; keys: none; a swipe keeps `rn-slide` 160 | none | runner.js `show()` |
| F11 progress segment | an answer files | `.rn-seg.add` scaleX 240 ease (was 320) | instant | runner.css |

### 3.8 Sidebar

| Moment | Trigger | What moves | Reduced | Hook |
|---|---|---|---|---|
| B1 Now card fold | fold button click | same-document VT with `html.vt-fold`; `.nextup`, `.side-day` and `.side-nav` named for this run only: the card morphs to one line, Today exits 140, the nav slides up, 260 ease-move; chevron 200 (exists) | instant | ui.js `paintSide()` fold handler through `UI.motion.vt()` |
| B2 rail expand, collapse | toggle click; `[` is instant | same-document VT with `html.vt-rail`, which re-enables the `side` and `main` groups (their `animation: none` would freeze them): the side group morphs 68 to 248px, 260 ease-move; labels fade 100 out, 160 in; main: old hidden, new drawn at its final size anchored left (`object-fit: none; object-position: left top`, group clipped) so content slides with the edge. Width and padding never animate | instant | ui.js `toggle()`, `layout()` |
| B3 rail peek | 400ms rest | S8 | instant | ui.js |
| B4 nav metas | shell repaint | a count bubble rolls (D1); a new dot scales .6 to 1, 200 ease; a cleared one fades 120 | instant | ui.js `paintSide()` slot |
| B5 Up next changes | a new top item | card content crossfades 160, no travel | instant | ui.js `nextBlock()` |

### 3.9 The test window (`exam`)

| Element | Motion |
|---|---|
| option select, strike, mark for review, Next, Back, question jump | none (a cut) |
| navigator popover ("Question N of M") | opacity 120 in, out instant |
| directions, reference, calculator panels | none; a drag follows the pointer with no inertia |
| timer | hide and show at once; `t-low` colour at once; the 60s `t-pulse` stays (Tests 4.3) |
| module break | the linear between-bar stays |
| page entry | no view transition (N7) |

Hook: runner.js sets `data-m="exam"` on its root when `exam`; ui.css zeroes every `--m-*` duration under it and
turns transitions off except the navigator popover, the between-bar and `t-pulse` (they keep literal values outside
the tokens). Existing exam motion stays exactly as it is.

## 4. Implementation plan

### 4.1 The module

`UI.motion` is a section of kit.js (about 150 lines), not a new file: kit.js loads on every page after ui.js and
before question.js, runner.js and charts.js, so no page gains a request or a script tag. head.js keeps the two
cross-document hooks (N3 to N5), since `pagereveal` fires before kit.js runs.

```js
UI.motion = {
  off(),                 // OS reduce or html[data-motion="reduce"]; kit still(), ui reduced(), runner and question still() alias it
  kb(),                  // the last input was a key: html[data-input="key" | "pointer"], set by two capture listeners
  ok(e),                 // !off() && !kb() && !(e && e.detail === 0): play movement
  enter(el, kind, o),    // 'rise' | 'nudge' | 'fade' | 'pop', WAAPI from the tokens -> Animation | null
  exit(el, kind, o),     // -> Promise, resolved at once when !ok(); the caller removes el after
  stagger(host, o),      // [data-m="stagger"] children, max 6, step 30; once per page view, after UI.whenVisible
  flip(host, mutate, o), // measure, mutate(), invert, play 200 ease-move; over 40 moved: just mutate()
  vt(update, o),         // same-document VT: o.cls on <html> for the run, o.names {selector: name}; else update()
  draw(svg),             // first chart draw: [data-m="line"] paths, [data-m="bar"] rects, [data-m="wipe"] grids
  once(key, store),      // true the first time (sessionStorage; 'local' for once a day)
  spring(d, bounce, v0), // -> {easing: 'linear(...)', duration}: the solver behind the tokens, for drag release
};
```

Pages opt in only through `data-m="stagger"`, `data-m-now`, `data-vt-src`, `data-vt-dst`, `UI.motion.flip()` and
`UI.motion.enter()`. Check: `UI.motion.spring(.3, 0)` must equal `--spring` (one assertion in web/dev/kit.html).

**No vendored library.** CSS (transitions, `@starting-style`, allow-discrete, `linear()` springs, `@property`), WAAPI
and view transitions cover every row above. motion.dev's mini `animate` (a few KB) wraps WAAPI, which we already
have; its full build (roughly 18KB gzipped) adds spring physics that carries velocity through a retarget. The one
place that needs velocity is the phone sheet release (S2), and `spring(d, bounce, v0)` (about 15 lines, the solver
that produced the tokens) builds those keyframes. Add motion.dev only if drag-reorder or follow-the-finger
question swipes land.

### 4.2 ui.css changes

1. Tokens (section 2), the reduced overrides, the `[data-m="exam"]` overrides.
2. The ~85 literal durations (`.12s`, `.16s`, `.2s`, `.24s` and the rest) become tokens.
3. Keyframes `rise pop fade sheet-in sheet-up side-in` become transitions with `@starting-style` on the shown state
   (they restart from zero when interrupted; transitions retarget); `pin` and `out` (scale 0, 1.35) go; new
   `m-pop`, `m-draw`, `m-wipe`.
4. The press and release pattern (C1); hover stays under `(hover: hover) and (pointer: fine)`.
5. Surfaces with allow-discrete exits and `data-side` origins.
6. Fills to scaleX (D3). Today `.meter-bar > i`, `.mbar > i`, `.rn-between-bar > i` and `.rp-mb i` transition width.
7. VT block: `::view-transition { pointer-events: none }` (missing today), N1 timings, `nav-mark`, `tab-mark`,
   `hero`, `page-title`, the `back` type, `html.vt-rail`, `html.vt-fold`.
8. Reduced block: the `.01ms` rule stays for `animation` (keyframes move things) as the safety net; transitions are
   governed by the tokens, so fades and fills survive. Add `::backdrop` and `::view-transition-*` explicitly.
9. `@property --m-ring`, `--m-hold`. Every motion property is prefixed `--m-`.
10. tools/check-ui.py flags: transitions on width, height, top, left, margin or padding outside E1 to E3;
    `scale(0)`; literal durations in page CSS; keyframes defined outside ui.css and runner.css.

### 4.3 Named exceptions to "compositor only"

- E1 `.seg-ind` and `.tab-ind` width: out of flow, one box; scaleX would bend their 8px corners and the inset underline.
- E2 banner dismiss: `grid-template-rows: 1fr` to `0fr`, 180ms, once, so the page closes up instead of jumping.
- E3 tour ring size: a fixed element; it snaps, only its position moves.

### 4.4 Build order

1. Plumbing, no visible change: tokens, `off/kb/ok`, the four `still()` copies aliased, `data-input`, the exam scope,
   the reduced rework, the `--p` rename (risks), the check-ui rules, `::view-transition` pointer-events.
2. Exits: sheet, popover, menu, toast (FLIP, countdown), banner. The biggest gap: today every surface vanishes.
3. Controls: press and release, spring indicators, saving spinner and check, tooltip warmth, palette instant.
4. Question feedback F1 to F4, F10, F11; re-measure Check to verdict and Next to stem.
5. Surface polish: popover origin, phone sheet release, overlay exit, tour ring.
6. Navigation: N1 timings, N2, N4, N7; then N3 pairs; N5 last, as a trial.
7. Data and rewards: meters, ring, roll, count-ups, gauge, F5 to F8.
8. Mount stagger and chart draw-ins (M1, D5, D6, D8): last, they depend most on the `whenVisible` and first-draw gates.
9. B1, B2 and list FLIP (L1 to L4), page by page as passes reach them.

### 4.5 Risks

- **View transitions freeze the page and snapshot it.** User-initiated only, 260ms at most, never for timers,
  toasts, refreshes or anything ambient; pointer-events pass through the overlay.
- **A duplicate `view-transition-name` skips the whole transition.** Names go on exactly one element, set by JS
  (`nav-mark` in the visible nav only; a `display: none` copy does not count); `hero` and `page-title` only when found once.
- **Same-document VT inherits `animation: none`** on `side`, `bar`, `pbar`, `tabs`; the `html.vt-*` class re-enables
  only what that run needs.
- **Support.** Cross-document VT: Chromium and Safari 18.2+ (Firefox navigates plainly). Same-document VT: Chromium,
  Safari 18, Firefox 144. Exit animations need `overlay` support (instant elsewhere). Everything degrades to today.
- **Replays.** `UI.cached` repaints, `sized()` resize redraws, bfcache restores and prerenders must not replay an
  entry: `first` flags, `once()`, `UI.whenVisible`.
- **Speed budgets** (ui.css rule 13): no animation delays DOM work or holds focus; measured after steps 4 and 8.
- **Low-end phones.** At most 6 staggered, 14 bars, 40 FLIP rows; one clip-path for the heatmap; no filter, blur or
  box-shadow animation (fade a pseudo-element's opacity instead); no global `will-change`; long `main` snapshots cost
  memory, so N1 stays a fade.
- **Motion sickness.** Travel 12px at most, except sheets (they follow the finger and anchor to an edge) and morphs
  (A to B the user chose); no parallax, no page zoom, no rotation beyond chevrons; overshoot only from spring-pop
  (6.8%, small elements); both the OS setting and the in-app switch apply (head.js mirrors `satf.look`).
- **`@property` is global.** runner.css registers `--p` as a non-inheriting `<percentage>` for the hold ring, and
  Today loads runner.css, so `.meter-bar > i` and `.ring::before` (which read `--p` as an inherited number) probably
  draw wrong there today. Rename it `--m-hold` in step 1 and check the Today meter and ring.
