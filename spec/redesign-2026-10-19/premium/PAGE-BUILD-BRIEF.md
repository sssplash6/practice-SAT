Premium build, phase B: the brief every page builder reads first.

The user approved the whole premium list: "do all and follow your instinct regarding relaxes", both the 16 recommended and the ~50 "More" items. Their bar: "it should feel premium", "cool buttons, motions, animations ... depth", "icons, highlights and bunch of stuff", and "premium means it is not clustered" (calm first screens: few things visible, room between groups, density only inside lists).

Repo /Users/workingmyassof/freshbot/satbank (vanilla HTML/CSS/JS, no build step). Read, in this order:
1. spec/redesign-2026-10-19/premium/BUILD.md in full: the rules decided (shadows, gradients, motion, spacing, hero numbers, icons, marks font) and the reports "A1 surfaces and controls", "A2 motion", "A3 icons" with the shared API you must use (`.card.hero`, `--hero-wash`, `--fs-hero`, `--ink-strong`, `.split-btn`, `.pill.done`, the page entry hook, `UI.glide`, `UI.fx.*`, meter sweeps, fold animation, the focus chrome, the new icon names and filled twins, the spot illustrations).
2. spec/redesign-2026-10-19/premium/SUGGESTIONS.md: every Recommended and More item that touches your pages, the "Per page" line for your pages, the open bugs on your pages.
3. Your page's premium audit: spec/redesign-2026-10-19/premium/pages/<name>.md (its calm first screen, hero, controls, motion moments, icons, delight, top 10) and the matching sections of premium/SUGGESTIONS-INDEX.md.
4. Your page's earlier reports in spec/redesign-2026-10-19/passes/<name>.md, CLAUDE.md, and your pages' code in full.

THE JOB, in this order: (1) the calm first screen your page audit proposes (count what is visible before and after; hide behind one control or defer until relevant, never drop); (2) the page's one hero with depth (`.card.hero`, `--hero-wash`, the hero number at `--fs-hero` where the page has one number it is about); (3) the shared pieces adopted (tactile buttons and their busy / done states, split buttons, quiet menus, drawn checkboxes, highlights, hover bands); (4) motion moments (page entry hook on the top blocks, list glide, folds, feedback moments via `UI.fx.*` and `UI.roll`, meter sweeps), never on the test window beyond what MOTION.md allows; (5) icons: move every local icon copy and unicode stand-in (✓ ✕ ⋯ ▾ ‹ › ⓘ) in your files onto `UI.ICON` names (A3's list says which call sites change), filled twins for your toggles, spot illustrations in your empty states; (6) your page's open bugs; (7) every remaining "More" and "Per page" item for your pages. Judge each screen against "calm, deep, tactile, alive, one orange focus".

FIXED: logo and brand orange #F18508 (fills take dark text; orange is the selection colour); `.pill` 42px with 10px corners, `.pill.sm`, `.btn`, `.quiet`, no 24px+ radius, nothing taller than 48px; Source Serif 4 and Bluebook calm in the test window; no em dashes; sentence case, no exclamation marks; zero functionality loss (every action, link, figure, state, shortcut, tooltip, empty / error / loading state and phone path stays reachable); never rename or remove a class or id another file uses (grep web/ first); the "Not doing" list in SUGGESTIONS.md (no confetti, mascots, glass, grain, shimmer, lift on hover, shake on wrong answers).

FILES: edit only the files you own (listed in your task). Never edit web/assets/ui.css, ui.js or kit.js; list what you need under "Shared asks". No browser, no screenshots of the app (the user's rule), no git commands (the tree holds the user's uncommitted work).

CHECKS before reporting: `python3 tools/check-ui.py`; `node --check` on every JS file you touched and each inline script (extract to a temp file); grep web/ that every removed selector or id is unreferenced; grep your files for the em dash; smoke: `node spec/redesign-2026-10-19/smoke/page.js /Users/workingmyassof/freshbot/satbank/web <page path> 1440` and `390` for each page you touched (Today: `node spec/redesign-2026-10-19/smoke/run.js <fresh|plan|review|stretch|test> 1440|390`), compared against runs before your edits; and the inventory diff: `node spec/redesign-2026-10-19/smoke/inventory.js /Users/workingmyassof/freshbot/satbank/web <page path> 1440` before and after your edits, and account for every link, button, id or field that disappears (renamed, moved behind a control, merged).

REPORT: append "## Premium build" to spec/redesign-2026-10-19/passes/<name>.md: first screen before / after (counts), hero, what moved behind which control, new motion and feedback moments, icons changed, bugs fixed, inventory diff accounted for, "Not done" with reasons, "Shared asks", "For the user". Final message: 5 lines max.

TWO PARTS (to go faster). Phase A (the shared layer) is still being built while you start, so BUILD.md's "A1 / A2 / A3"
report sections may not exist yet.
- PART 1 (now): steps (1) the calm first screen, (2) the hero (use the names BUILD.md fixes: `.card.hero`,
  `--hero-wash`, `--fs-hero`, `--ink-strong`; they will exist in ui.css), (6) your page's open bugs, and (7) the
  "Per page" and "More" items that need no new shared JS (layout, grouping, copy, what folds, what moves behind one
  control, hiding empty bars, counts over percentages, sample rows for empties). Do not wait for or guess the motion,
  icon or feedback APIs. Run the checks, append "## Premium build (part 1)" to your passes/<name>.md, and stop.
- PART 2 (the lead will message you when phase A lands): steps (3) shared controls adopted, (4) motion and feedback
  moments, (5) icons and illustrations, plus anything part 1 left for the shared API. Append "## Premium build (part 2)".
The user's bar: "you did very well with demo ... can do even better". Aim above the demo page (web/dev/premium.html,
index premium/DEMO.md): it shows the direction; your page should look and feel at least that good.

Smoke data: `FIX=practice node spec/redesign-2026-10-19/smoke/page.js ...` (and inventory.js) adds /bank, /drill/preview,
/sets and /next, so Practice and anything that reads the bank renders with data; the default stays the Today set.
