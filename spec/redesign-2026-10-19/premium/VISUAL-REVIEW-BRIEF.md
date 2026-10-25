Visual review of the real app (phase C). The user approved visual self-review: screenshots before they see it.

The bar, in the user's words: "it should feel premium", "premium means it is not clustered", "you can do a lot better", and
on two specimens that missed: "LOOKS BIT ASS" (a thick dark focus ring boxed around a link), "looks off" (a side stripe
and a wrapped check on a row). Calm first screens, one hero with depth, tactile buttons, purposeful motion, polished icons
and highlights, one orange focus.

Read first: spec/redesign-2026-10-19/premium/BUILD.md (rules and the APIs), premium/DEMO.md "## Visual review" (the
demo critic's do / don't list), premium/SUGGESTIONS.md "Not doing", /Users/workingmyassof/.claude/skills/impeccable/SKILL.md
("Absolute bans") and high-end-visual-design/SKILL.md, and the page's reports in spec/redesign-2026-10-19/passes/<name>.md.

Setup: the app runs at http://127.0.0.1:8071 against a COPY of the local database (safe to click anything). To see real
content, browse as a learner with history: read web/assets/ui.js to see how the learner id is stored (localStorage key)
and sent; pick from the copy at /private/tmp/claude-501/-Users-workingmyassof-freshbot-satbank/11932fea-c5c4-475d-bd5f-041033f1446a/scratchpad/localrun/satfreshman.db
the learner with the most rows in `attempts`, and one learner with an active plan (`plans.archived IS NULL`) for Plan.
Also look at a fresh learner (clear storage) for first-run and empty states. Nothing leaves this machine.

Browser: do NOT use the Playwright MCP browser tools (one other reviewer holds them). Use your OWN headless browser,
so reviewers run in parallel: /private/tmp/claude-501/-Users-workingmyassof-freshbot-satbank/11932fea-c5c4-475d-bd5f-041033f1446a/scratchpad/pw/shot.js
(`node shot.js <url> <out.png> [width] [height] [dark] [learnerId]`; it marks the guided tours as seen unless TOUR=1,
and under 600px it emulates a phone: touch and a coarse pointer; do the same in your own scripts).
For hover, focus, menus, sheets and feedback moments, copy shot.js to your own scratch file and script the page with
playwright-core (require it from .../scratchpad/pw/node_modules/playwright-core; launch with executablePath
~/Library/Caches/ms-playwright/chromium_headless_shell-1194/chrome-mac/headless_shell): p.hover, p.keyboard.press('Tab'),
p.click, p.waitForTimeout, p.screenshot({ clip }) to look closely. Close your browser at the end of every script. Screenshots to spec/redesign-2026-10-19/premium/shots/app-review/<page>-<state>-<width>[-dark].png;
Read them and look properly.

Per page: 1440 light, 1440 dark (html[data-theme="dark"] or the app's theme switch), 390 light; hover, Tab focus, press,
open a menu and a sheet, trigger the page's feedback moment if you can (answer a question, tick a task, fix a mistake).
Verdict per screen in plain words; then FIX what is off in the page's own files (you own the files listed in your task;
for shared files ui.css / ui.js / kit.js, write the fix as a precise ask in your report, do not edit them). Re-screenshot
and re-judge, at least two rounds, until each screen reads as premium at 1440, in dark and at 390.

Checks after your edits: check-ui.py, node --check, em dash grep, the smoke harness for your pages, the inventory diff.
Report: append "## Visual review" to spec/redesign-2026-10-19/passes/<name>.md: per screen what changed, the screenshot
folder, shared asks. Final message: 5 lines max.
