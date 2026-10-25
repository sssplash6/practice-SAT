# UI redesign: where it stands

## Now (2026-10-19, second session)

- All 11 audits written (audit/*.md, INSPO.md). DIRECTION.md rewritten as v2 from them (section 0 is the
  visual bar; `.split` renamed `.twocol` because runner.css owns `.split`).
- Shared layer, done so far: tokens (--card-pad 16/12, --card-gap, --row-h, --radius-card 12, --ctl 36,
  --surface/--well), body 14.5, `.twocol` + `.reveal` primitives, surface resets; ui.js fold fixes (controls
  never fold, aria-live=off, popovers, dialog[data-fold], FOLD_OFF narrowed, timer ticks ignored), shell
  `now: false` also drops `.sections-next`, `nowBlock: false` (body.no-now; Today and Plan pass it), Up next
  pointing at this page is skipped; sidebar CSS (search+quick row, sr-only group labels, Now block from 700px
  tall, help/feedback icons by the user row, 8px section chips).
- Shared layer, also done: type scale on shared heads (.k/.meta/.h1-.h3/.label/.num), every mono-on-words and
  uppercase label in ui.css (mono kept: kbd, code, .otp, .countdown .num, chart svg text, .trend svg), `.pill`
  14/600 with a darker hover fill, `.btn` on `--well`, `.btn.sm`/`.pill.sm` 34, `.seg` -4, `.field.sm` 16, card
  hairline, card head/foot 12, kicker inline after the title, `.stat` unfilled in a card and figure 28, one
  `--track`, `.chips` 8, `.badge` 6, `.x` and `.skill-play` 8, sheets tighter with 16px titles, `.page` 16/48,
  `.gauge-v` 44/600, motion (`.rise` no-op, `.mbar` and meters .2s, kit countUp opt-in), kit.js `UI.NONE` en
  dash and eyebrow no uppercase, ui.js en dash, check-ui.py flags round buttons (`/* check-ui: round-ok */` opts
  an answer bubble out).
- Source audit in a real browser running (INSPO-VISUAL.md, screenshots in inspo/shots/), because the user
  asked for the six sources to be fully audited visually. Its findings drive a polish round after the passes.
- Nine page passes running in parallel (shared brief: PASS-BRIEF.md);
  each writes passes/<name>.md. Board: http://127.0.0.1:8072 (scratchpad board/serve.py).
- Then: shared asks from the pass reports, final checks, the big-changes list for the user.

## Premium renovation (2026-10-19, night): BUILDING

- Research done: premium/AUDIT.md, REFERENCES.md, MOTION.md, ICONS.md, DISCOVER.md, pages/*.md (9), merged into
  premium/SUGGESTIONS.md (16 recommended, ~50 more, 13 rules, bugs) + SUGGESTIONS-INDEX.md. Still running at launch:
  DISCOVER-BROWSE.md (browser pass) and the demo page web/dev/premium.html (+ premium/DEMO.md).
- User: "do all and follow your instinct regarding relaxes" (all 16 + all more). Decisions + plan: premium/BUILD.md.
- Phase A running: A1 ui.css (surfaces, controls, highlights), A2 kit.js + ui.js (motion, focus chrome; CSS to
  premium/build/motion.css), A3 icons (premium/build/icons.js, icons.css, glyphs.js, web/assets/fonts/Marks.woff2,
  favicon / app icon / og image). Lead then merges build/*.css into ui.css and build/icons.js + glyphs.js into ui.js.
- Phase B: nine page builders with premium/PAGE-BUILD-BRIEF.md (same page groups and file ownership as before).
- Phase C: checks, smoke, inventory diff, then the user reviews at http://127.0.0.1:8071.
- Lead fixes so far: runner.css --p (meters and rings drew empty), tour.js 999px buttons and #F28C18 fallback,
  check-ui.py now covers tour.js.

## After the polish round (2026-10-19, evening)

- User decisions: build the week sheet (done: plan-ui.js weekPlanner as day rows; save() uses PUT week for a week not
  begun, PUT day otherwise; the focus swap rides on per-day topics; plan.js "Shape this week" in the week head and
  ?shape=1; me/week.js links to it; check: smoke/weekplanner.js, 4 asserts). Twin, search box, greeting, 44px rank: ok.
- Local preview: uvicorn on 127.0.0.1:8071 with SATF_DB pointing at a copy in the scratchpad (localrun/).
- NEW DIRECTION from the user: "fully renovate the web ui, cool buttons, motions, animations, depth ... premium",
  "icons, highlights and bunch of stuff", "expand the sources of inspos", "premium means it is not clustered like this"
  (Practice screenshot). Running: premium/AUDIT.md (every layer + clutter), REFERENCES.md (browser: Linear, Vercel,
  Raycast, Stripe, Arc), MOTION.md, ICONS.md, DISCOVER.md (wider sources). Then: one ranked suggestion list for the
  user + a live demo page, BEFORE building (the user asked: audit first, then suggestions).

## Polish round (done, 2026-10-19)

- INSPO-VISUAL.md done (browser audit, 42 shots in inspo/shots/). DIRECTION section 9 holds the decisions (orange
  stays the selection colour, the user's call; titles stay 600).
- Lead done: --shadow-float on menus, popovers, tips, toasts, selbar; toasts on paper; palette 48px field, rows at
  --ctl, 12 corners; sidebar search a filled well; phone tab labels 11.5; `.choice-row`; edge fades (UI.edgeFade on
  the sidebar nav, the phone section bar, the palette list); the sidebar Now card folds (satf.nowfold); `.opt.picked`
  an orange edge on paper so a pick never looks correct. Kit agent done: UI.why, tooltip tap fallback, UI.saving,
  meter ticks, heatmap readout, sliding marks on UI.tabs / UI.seg, UI.roll (CSS merged into ui.css).
- Smoke harness: smoke/run.js (Today, 5 states) and smoke/page.js (any page); all pass as at HEAD.
- Nine page polish agents done (brief: PASS-BRIEF-2.md); each appended "## Polish round" to passes/<name>.md. After them:
  kit's heatmap readout removed (charts.js draw() owns it), `.tablist.sm`, meter `done: false`, the slide-cut fix
  (a resize that moves nothing keeps a slide running). Final checks: check-ui ok, 45 JS + 40 inline scripts parse,
  no em dashes in web/, Today smoke clean in 5 states x 2 widths, 19 pages x 2 widths match HEAD's smoke results.
- Functionality diff (smoke/inventory.js, 22 pages at 1440, HEAD vs now: links, button names, ids, fields): 78 items
  missing from the old layouts, every one renamed ("Help: X" -> "About X"), merged or moved as the pass reports say;
  none lost. Then: `.tablist.sm` on the runner's side tabs, print rules for `.twocol` / `.reveal` / fades, FOR-USER.md
  merged into one list.
- Next: the user reviews in a browser (FOR-USER.md on the board lists every call and change). No commits until asked.

## Polish-round backlog (from pass reports)

- One shared "explain" control: Profile `.help-q`, Compete `.info-i`, Results `.rx-info`, Tests `.ts-q`, Today `.why-i` do the same job
  (a `?` that opens its text); make `UI.why(text, label)` in kit.js and move the pages onto it.
- Shared key/value rows (`UI.rx.kv` / `.rx-kv` in results-ui.js) into kit; `UI.sheet({ foot })`; a synchronous
  `UI.fold(el, label)`; section-bar scroll-spy skipping `.twocol-side` when it is sticky; `.twocol.interleave`.
- One pressed-row button (wash-2 + amber inset when pressed, `--row-h`, 8px corners) for `.ctile`, `.deck`,
  `.wm-srow-b` (Words). `UI.tooltip` shows nothing on touch: a tap fallback for info triggers (goes with `UI.why`).
- `--twocol-bottom` exists now (Words library still sets its own max-height; can switch to the token).
- Heatmap readout for `UI.calendar` too (Today draws its own readout line under #cal until kit covers calendars).
- Optional: charts.js `barChart` `labels: 'ends'` (Words forecast); a no-fill `.choice-row` for long filter lists;
  `UI.tabs` shared-panel mode, short labels and a re-select callback; a one-value chip type for filterBar (Review).
- Done already from asks: `.quiet` 44px on touch, `.twocol-side` focus-ring room and size container (skill rows
  collapse inside it), `UI.nextMeta`, palette selected row without the stripe, stats in a card share one edge,
  first `.choices` flush, fold chevron, `.reveal-host`, chart text Geist 11.5 with charts.js textW at 11.5,
  `.card-head .chart-ctl`, `.gauge-s` 12.5, filterBar `keep` and `data-fkey`, Review tour step text.

## User notes (later, not now)

- Plan wizard, "Time you have": the per-day time dropdown (15 min to 4 h) should end with a "Custom amount"
  option as its last entry. (User, 2026-10-19: "just take a note, no need to do it rn".)
- Practice: replacing the animated search box needs the user's yes (the code records it as their choice).

## Earlier (first session)

Paused by the user mid-audit (switching accounts). Nothing is committed; the user mass-commits at the end.
Resume by reading BRIEF.md, DIRECTION.md, then this file.

## Done

- `BRIEF.md`: the user's words, the fixed rules, the shell findings. Includes the later instruction:
  bigger changes welcome, zero functionality loss, list every big change for the user.
- `DIRECTION.md`: draft spec (type scale, spacing tokens, surfaces, sidebar plan, `.split` right column,
  `.reveal` hover-reveal, slop list, ownership). Refine it with the audit results before any page pass.
- Fonts: `web/assets/fonts/Geist.woff2`, `GeistMono.woff2` (variable, from apdash's `geist` 1.7.2 package)
  and `OFL.txt` copied in. All 40 HTML pages now preload `/assets/fonts/Geist.woff2` instead of loading
  Archivo + DM Mono from Google; pages with questions still load Source Serif 4 from Google.
  `ui.css` now has the two `@font-face` rules and `--font: "Geist"`, `--mono: "Geist Mono"`; the print,
  sheet and walk pages' `var(--sans, 'Archivo')` / `var(--mono, 'DM Mono')` fallbacks point at the tokens.
  Not yet done: the type scale itself (sizes and weights are still Archivo's), `.k` still mono uppercase.

## Interrupted: the audit (re-run on resume)

Resumed 2026-10-19 in a new session: all eleven re-launched. Any file missing from audit/ (or INSPO.md)
was not finished; re-run just that one. Each writes one file. Prompt template (fill SCOPE and OUT):

> You are auditing one part of the SAT Freshman web app (vanilla HTML/CSS/JS, repo
> /Users/workingmyassof/freshbot/satbank) for a UI redesign. First read spec/redesign-2026-10-19/BRIEF.md and
> CLAUDE.md. Shared styles are web/assets/ui.css and runner.css; shared JS is ui.js and kit.js (read only what
> you need). YOUR SCOPE: {SCOPE}. CODE-LEVEL audit: no browser, no server, no screenshots, edit nothing but
> your output file, no git state changes. Work out what a student sees at 1440x900 (sidebar 248px) and
> 390x844. Audit: A purpose and primary action; B whitespace (concrete values); C non-essential always-on
> content (fold / hover-reveal / move to side column / delete duplicate; note what FOLD_SEL, ui.js ~2792,
> catches); D sidebar use (what belongs in a sticky right column or the left nav); E redundancy (also with
> the shell: streak, exam date, Up next, Today progress); F local overrides of shared components, hardcoded
> colours, off-scale sizes, radius 999px, inline styles; G AI-slop tells; H copy; I CSS/layout bugs. Then
> "Redesign proposals", ranked, concrete, with file:line and risk. Bigger structural changes welcome, zero
> functionality loss; flag each big one. Write {OUT} (120-250 lines, terse, no em dashes). Final message:
> 5 lines max.

| OUT (in spec/redesign-2026-10-19/) | SCOPE |
|---|---|
| audit/today.md | web/index.html (Today: hero, next, qotd, gain, mist, score, exam, pace, study, chal, words, cal, tests, due, soon; has .td-side at 1080px+) |
| audit/practice.md | web/practice/index.html, builder.js; plus web/assets/quick.js and palette.js |
| audit/runner.md | no-chrome answering surfaces: practice/session/*, test/*, challenge/index.html, diagnostic/*.html, assets/runner.css, runner.js, UI parts of question.js (keep Bluebook fidelity) |
| audit/review.md | web/review/** (index, review.js, item.js, sheet, walk, print.html), web/mistakes/index.html |
| audit/results.md | web/results/** and assets/results-ui.js, report.js, charts.js (styling and density) |
| audit/tests.md | web/tests/** (index.html, tests.js, start.js, talk.js, compare.js) |
| audit/plan.md | web/plan/** (index.html, plan.js, progress.js, wizard.js) and assets/plan-ui.js; with and without a plan |
| audit/words.md | web/words/** (index, mine, run, study, print), web/vocabulary/index.html, assets/words-ui.js |
| audit/me-compete-misc.md | web/me/** (me.css, me.js, account.js, week.js, settings/*), web/compete/** + assets/compete-ui.js, help, signin, welcome, parent, pair, share, s, 404, admin (low priority) |
| audit/shared.md | ui.css except the shell (tokens, type, controls, cards, data, marks, charts, sheets, kit pieces, motion, touch, print), kit.js, non-shell ui.js helpers. Output: type scale (max 8 steps), tighter 4px spacing scale, surface system, every uppercase kicker and its replacement, duplicate components, ranked ui.css/kit.js changes noting which pages override each rule. Never rename a class. |
| INSPO.md | apdash's taste sources (dqnamo.com/kitchen, smoothui.dev, bencho.dev, amicro.vercel.app, ui.aceternity.com, 21st.dev). Read apdash docs/premium-pass-2026-10-09/research/{kitchen,charts-amicro-bencho,type-colour-assets,motion-libraries}.md, its DIRECTION.md and freshweek-design-system.md first, then WebFetch the sites for what they miss: shell and sidebars, density, surfaces, progressive disclosure, controls, fonts (Latin + Cyrillic; Geist vs alternatives), what to avoid. Per source ADOPT / ADAPT / REJECT with numbers, then 15-20 rules for this app. |

## Plan after the audit

1. Refine DIRECTION.md from the audits.
2. Shared layer, lead only: `@font-face` + font tokens; type scale; spacing tokens; `.k` to sentence case;
   chips to 8px corners; `.split` and `.reveal` primitives; FOLD_SEL additions.
3. Shell (ui.css ~297-750, ui.js ~1408-2400): the full sidebar keeps Up next + Today as one Now block pinned
   above the user row at heights of 700px and up (today it needs 1100px, so laptops never see it); Search
   and Quick on one row; group labels sr-only; Help and Feedback as icons by the user row; hide the Now strip
   and `.sections-next` whenever the sidebar shows Up next; hide the sidebar Now block on Today (the page
   carries it). Keep every class name and every shortcut.
4. Page passes in parallel (the user lifted the agent cap), one agent per audit group, disjoint files,
   no edits to ui.css / ui.js / kit.js (they list "Shared asks"). Then `python3 tools/check-ui.py`,
   `node --check` on touched JS, and a grep that no removed selector is still referenced.
5. Report to the user: every big structural change, in a short list.

## Notes

- Do not take screenshots or open a browser to check changes (memory: the user reviews everything).
- Working tree has many unrelated uncommitted changes; never stash, checkout, restore or reset.
- A throwaway local server was used on port 8071 with a DB copy in the session scratchpad; not needed.

## Kit components (polish round)

All in `web/assets/kit.js` (documented in its top comment block, exported on `UI`); CSS in
`spec/redesign-2026-10-19/kit-polish.css` for the lead to merge (its header says where each block goes). Until
the CSS lands nothing changes on screen: the slider and the roll check for their own CSS and stay off without it,
and the other pieces only appear where a page calls them. Smoke-tested in jsdom (scratchpad, not kept).

API
- `UI.why(text, {about, label, anchored, className})` -> `button.why-q`. Click, tap, Enter or Space opens `text`
  in `UI.pop` (a second press closes it); a string or Node `text` is also the mouse hover tooltip. `text`: string, Node,
  a list of them (one paragraph each), or a function returning any of those or a Promise of them (shows Loading,
  then fills and repositions). `about` names it "About <about>" (else "More about this"); `label` shows a word
  instead of `?` (`.why-q.word`, named by its word). The click is stopped, so a label, link or row around it
  does not fire. 20px, 8px corners, `--soft` to ink, 44px hit area on touch. Pop content: `.why-pop`.
- Tooltip tap fallback (inside `UI.tooltip`, no API change): a touch or pen tap on a trigger with no action of
  its own (no link, button, field, label, ARIA control role, `[data-fact]` or pointer cursor on it, in it or
  around it; an `aria-disabled` button counts as no action) opens the tip text in `UI.pop`. Mouse and keyboard
  unchanged. It defers to practice/builder.js's own tap tip (`e._tip`).
- `UI.saving(btn, work, {busy, done, fail})` -> Promise. 'Saving' while `work` (promise or function) runs, then
  a check and 'Saved' for 1200ms, or 'Couldn’t save' for 2400ms and rethrows; then the button's own nodes come
  back (listeners intact). Width held from its first layout, `aria-busy` while running, done/fail announced
  in the toasts' polite region (a `.sr` span, no toast drawn), a second press shares the running promise.
  `[data-saving="busy|done|fail"]` on the button. Pass `work` as a function: `UI.saving(b, save())` has already
  started the request, so a double press would start a second one.
- `UI.meter({..., ticks: n})` -> `.meter.ticks`: n blocks (gap 3, radius 2), `floor(value / max * n)` lit
  amber (`.ink`: graphite), all lit at the goal. `.meter-n` text, `tick` marker and aria values unchanged.
- Heatmap readout: `UI.heatmap` lives in charts.js, not kit, so kit adds the line from outside: its existing
  MutationObserver puts `p.heat-readout` (aria-hidden, data-nofold) after every new `.heat-wrap`, and document
  listeners fill it with the hovered or focused cell's aria-label, else the most recent active day (by date).
  A mouse leaving the grid goes back to that; a tap keeps its day. The brief said "the most recent day"; this
  shows the latest day with activity, because today is often "nothing logged" (to flip it, drop the
  `dataset.h` filter in kit.js `heatRead`). Tooltip, aria-labels and `.heat-stats`
  unchanged. CSS makes the M / W / F labels screen-reader only (the readout names the weekday) and shrinks
  their column to 0. Better long-term home: charts.js `draw()` appends the line itself; then drop
  `heatReadouts(n)` from kit's observer.
- Sliding indicator, automatic in `UI.tabs` and single `UI.seg` (not multi, not chips): one `.tab-ind` (amber
  2px underline, inset 12) or `.seg-ind` (paper thumb, 1.5 amber ring) appended last in the control, placed
  from the selected item's offsetLeft/Top/Width/Height, recomputed by a ResizeObserver on the control and
  every item. It shows (`[data-ind]` on the control, which hides the static `::after` / thumb) only while every
  visible item sits on one line; a wrapped row (phone tabs), a hidden control, no ResizeObserver or no CSS
  keeps today's static mark. A click slides 200ms `--ease`; keys, `set()` and resizes move it at once; no
  slide on first placement or under reduced motion. Orange stays the selected mark.
- `UI.roll(el, to, {format})`: for a figure that changed on screen (the caller never rolls on load). The new
  text is set at once in a `.roll-t` span (the accessible text; aria-live as the caller has it, announced
  once), an aria-hidden copy over it rolls each changed digit (columns 1.15em, edge mask, 220ms `--ease`, no
  overshoot, right-aligned so new leading digits come in from 0). Plain text under reduced motion, with no
  change, off screen or before the CSS lands. Leaves `span.roll-w` (tabular figures) inside `el`. `el` must
  hold only the figure: its textContent is the old value and anything else in it (a unit `<small>`) is replaced.

Migration (pages delete their local copy; keep the exported name as a one-line wrapper until callers move)
- Today `web/index.html`: `info(text, label, {mark, hover})` -> `UI.why(text, {about})` (arrays and Nodes
  pass straight through; labels become nouns: 'How mistakes work' -> about 'mistakes'); delete `.why-i`,
  `.why-i.q`, `.info-pop` CSS once no `.why-i` is left. Keep the other `.why-i` at ~1266: it is an inline
  disclosure of the row's reasons, not a popover (restyle it with `.why-q` classes if wanted).
- Profile `web/me/account.js`: `helpBtn(id, label)` -> `UI.why(() => loadAnswers().then(as => { const a =
  as.find(x => x.id === id); return [h('p', {class: 'q', text: a ? a.q : label || 'Help'}), a && a.a,
  h('a', {class: 'link', href: '/help/#' + id, text: 'More in Help'})].filter(Boolean); }), {about: label ||
  id})`; keep `UI.acct.helpBtn` as that wrapper (me.js, settings.js call it); drop `.help-q` from me.css.
  Name changes from "Help: X" to "About X". The `UI.help` branch has no implementation anywhere today.
- Compete `web/assets/compete-ui.js`: `info(text, label)` -> `UI.why(text, {about: label.replace(/^About /, ''),
  anchored: true})`, keep `UI.compete.info` as the wrapper (13 callers); drop `.info-i` from compete.css.
- Results `web/assets/results-ui.js`: `UI.rx.info(text, label)` -> `UI.why(text, {about})`; touch now opens it
  (it was hover only). Drop `.rx-info` CSS. results/page.js and report/page.js call it through `info`.
- Tests `web/tests/start.js`: `TestStart.why(text, {label, text})` -> `UI.why(text, {about, label: o.text})`.
  Trap: there `label` is the aria name and `text` the visible word; in `UI.why` `label` is the word and
  `about` the name. Drop `.ts-q` from tests/index.html.
- Words `web/assets/words-ui.js`: `info(text, label)` -> `UI.why(text, {about: label})`, keep `word.info` as
  the wrapper (words/study calls `W.info`); drop `.winfo`, `.winfo-t`.
- `UI.saving`: Profile and settings Save, Copy link (share, pair), Words Add word (`{busy: 'Adding', done:
  'Added'}`); keep `.pref-state` text where it exists.
- `.meter.ticks`: Today minutes against the goal, Plan week view, Words daily target (pass `ticks`).
- `UI.roll`: Results section score after scoring, Words learnt after a run, Today minutes after a session.
- Plan `.wz-seg3 > [aria-checked="true"]:nth-child(2)` (the neutral middle option) still wins on the button,
  and its 1.5px line ring sits exactly over the thumb's amber ring; if amber shows at the corners, add
  `.wz-seg3:has(> [aria-checked="true"]:nth-child(2)) > .seg-ind { box-shadow: none; }` in plan/index.html.

Not done, and why
- Review `#rhtabs` is hand-built (`.rh-tabs`, review.js `paintTabs`), not `UI.tabs`, so it gets no slider. The
  Review pass can move it to `UI.tabs` (it needs per-tab sub-lines and aria-labels that `UI.tabs` lacks) or the
  lead can export `slideMark` and add `.rh-tabs` to the `.tab-ind` rules. Any other static `.tablist` / `.seg`
  markup keeps its static mark too.
- Disabled triggers (`button:disabled`, `select:disabled`, e.g. leaderboard's period stepper and board
  selects, the Results report's sample buttons) fire no click, so the tap fallback cannot reach their
  tooltip. Same as today; a page can wrap such a control in a span that carries the tip.
- `web/dev/kit.html` is not touched: the lead may add demos for `UI.why`, `UI.saving`, `ticks` and `UI.roll`.
- Month labels at 11.5 (INSPO-VISUAL row 14) are left to the lead's ui.css pass.
