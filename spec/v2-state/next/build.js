export const meta = {
  name: 'v2-build',
  description: 'Build v2 tasks: unit builders on the task branch, one independent check, one fix, then ready to merge',
  phases: [
    { title: 'Build', detail: 'one agent per unit, in order, committing on v2/<task>' },
    { title: 'Verify', detail: 'independent verifier tries to refute that the task is done' },
    { title: 'Fix', detail: 'fix the verifier defects on the task branch' },
  ],
}

// args: [{id, from?: 'build' | 'verify' | 'fix', unit?: n, round?: n, issues?: path}]
// Everything lives on the task branch and in saved verdicts, so a restart names where to begin
// (from: 'verify' after a finished build, 'fix' with the saved issues file) and nothing finished re-runs.

const REPO = '/Users/workingmyassof/freshbot/satbank'
const SIGN = 'Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>'
const SHELL = '/Users/workingmyassof/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell'

// A wave-2 section: its spec pointers, upgrade file and owned files; five units from server to a walked page.
// Pages: two units. The independent check walks every page afterwards, so the builder's own walk is a quick one.
const PAGE_UNITS = [
  `The main page(s) of the section: layout, data wiring and every primary action, built from the kit and the shell, at 1280 and 390.`,
  `The rest of the section's screens (sheets, menus, empty, loading and error states, the phone layout, keyboard support, the upgrade
file's remaining page items), then a quick headless walk of every page at 1280 and 390 with a new and a seeded learner: no console
errors, test_flow still "all good".`,
]
// pagesOnly: the server half was built by the user's other agent and is merged; build only the pages.
// RULE (the user, 2026-09-27): every NEW task is pages-only. Backend parts are written into spec/v2-state/HELPER-TASKS.md
// for the user's other agent, and the user is asked to hand them over. The run wf_3f139f0b-f7c is the one exception.
function section(id, name, port, builds, upgrades, owns, pagesOnly) {
  section.pagesOnly = !!pagesOnly
  const t = {
    title: `${id} · ${name}`, port,
    spec: `spec/v2-state/briefs/${id}.md ONLY (it holds the decisions, your task entry, your upgrade file, product.md's overrides for
you, your section spec and Part 2; do not open spec/rebuild-v2.md or other upgrade files). You build ${builds}; the resolutions and contracts of Part 2
(§2.2 R1-R38, §2.9 contracts, §2.10 registries, §2.13 amended checks); and spec/v2-upgrades/${upgrades}.md (its accepted upgrades and
overrides win over the section spec). Use the merged foundations instead of writing your own: F1's ui.css, kit.js and charts.js (read
the kit.js header and /dev/kit.html), F2's shell (ui.js, UI.api, UI.prefs, UI.keys), F3's UI.workspace, UI.runner and UI.review,
F4's progress/estimate/prefs/deps.access, F5's drill body, F6's UI.report and sets. Another section's helper you need is called through
deps.part (server) or \`UI.x && UI.x(...)\` (client) so it degrades until that section lands.`,
    owns,
    units: section.pagesOnly ? PAGE_UNITS : [
      `Server and its checks: every endpoint and module function this section owns (its server items and the §2.9 contracts it
provides, validated at the boundary), and server/checks/${id.toLowerCase()}.py covering every server acceptance item (as amended by
§2.13 and the upgrade file), passing. Also fix the security findings in spec/v2-state/followups/security-audit.md that sit in your files.`,
      ...PAGE_UNITS,
    ],
    accept: section.pagesOnly
      ? `The PAGE items of the section's acceptance list in Part 3 (as amended by §2.13 and spec/v2-upgrades/${upgrades}.md), walked at 1280
and 390 with a new and a seeded learner, no console errors; the pages degrade cleanly where a server endpoint is not merged yet (the
server half is the user's other agent's; do not fail the pages for missing endpoints); test_flow prints "all good".`
      : `The section's acceptance list in Part 3 (as amended by §2.13 and spec/v2-upgrades/${upgrades}.md): its server items via
server/checks/${id.toLowerCase()}.py, and its page items walked at 1280 and 390 with a new and a seeded learner, no console errors;
test_flow prints "all good".`,
  }
  return { [id]: t }
}

const TASKS = {
  F1: {
    title: 'F1 · Design system', port: 8011,
    spec: `spec/rebuild-v2.md: §2.1 (line 90), §2.3 (176), the F1 rows of §2.4 (213), §2.12 F1 (543), Part 4.2 F1 (11009),
Shell §2.13 tokens and §11 CSS inside Part 3.1 (lines 653-2294, find them by heading), and every item assigned to F1 in
spec/v2-upgrades/*.md (grep -n "F1" spec/v2-upgrades/*.md; product.md's cross-file overrides too).`,
    owns: 'web/assets/ui.css, web/assets/kit.js, web/assets/charts.js, web/404.html, web/dev/kit.html',
    units: [
      'ui.css foundations: the §2.1 file header, every token of §2.3 (status, difficulty, mastery) and the light and dark tokens of Shell §2.13 (light stays default), base element styles and the print conventions. Existing pages keep working: add new classes, restyle existing ones, never rename.',
      'ui.css components: every shared class in the F1 row of §2.4 and Shell §11 CSS, including the status cells and legends of §2.3, at 1280 and 390 widths.',
      'kit.js: every component in the F1 kit.js row of §2.4 (overlays on native <dialog>, bottom sheet under 760px, confirm, menus, seg, tabs, listboxes, toasts and the rest listed there, plus the single-event UI.ics(event) of R18(b)), with keyboard behaviour: Esc closes and returns focus, arrow keys in seg, tabs, menus and listboxes. Added with Object.assign(UI, {...}).',
      'charts.js: every chart in the F1 charts.js row of §2.4, each with role=img, an aria summary and a visually hidden data table.',
      'web/404.html ("That page does not exist." with links to Today and Practice; confirm StaticFiles serves it for /nope/) and web/dev/kit.html showing every component and chart in light and dark. Then walk kit.html at 1280 and 390 in a headless browser and fix what is broken.',
    ],
    accept: `§2.12 F1's acceptance: web/dev/kit.html shows every component in light and dark at 1280 and 390, with keyboard behaviour
(Esc closes and returns focus; arrow keys in seg, tabs, menus and listboxes); every chart renders its hidden table; /nope/ shows the
404 page. Also: all 14 existing pages still load with no console errors and look intact; test_flow prints "all good".`,
  },
  BANK: {
    title: 'BANK · three question-bank flaws', port: 8019, rounds: 2,
    spec: `satbank/ (templates generate Items; wrong values come from Mis(reason, value) lists; Item.spr_mistakes names grid-in
mistakes, filtered by satbank.item.gridin_mistakes and enforced by satbank/audit.py). Find each template with
satbank.registry.templates() and generate(name, seed).`,
    owns: 'satbank/topics/*/families/*.py for the three templates below only (not satbank/item.py or satbank/audit.py)',
    units: [
      `Fix these, seen in generated items on master: (1) rr.repeated_factor: a reason reads "counted 1 years" (fix the grammar for
every count, e.g. "counted 1 year"). (2) pct.table_share: the grid-in stem says "The table summarizes..." -- check whether the item
carries its table in a field the site renders; if it does, this is not a flaw and you change nothing; if not, fix the item so its
table is present. (3) lat.triangle_sum: the named mistakes "subtracted from 100 instead of from 90" and "assumed the two acute angles
of a right triangle are each 45 degrees" (value 28 for angle D = 73) -- recompute each from the stem; keep a mistake only if it is a
real route a student takes to that exact value, otherwise remove it. Wrong-answer VALUES of multiple-choice items must not change
(reason text may). PYTHONPATH=. python3 -m satbank check must print PASS for every topic.`,
    ],
    accept: `The three flaws are fixed (or shown not to be flaws, with evidence); for seeds 0-80 of every template in the touched topics,
multiple-choice stems, choices, answers and option values are identical to master (only reason text may differ, and only in the three
templates); PYTHONPATH=. python3 -m satbank check prints PASS for all 19 topics; PYTHONPATH=. python3 server/test_flow.py prints
"all good".`,
  },
  F2: {
    title: 'F2 · Shell', port: 8012,
    spec: `spec/rebuild-v2.md: §2.12 F2 (line 553), Part 4.2 F2 (11035), the Shell spec §2 in Part 3.1 (lines 653-2294) except §2.10,
R1, R22, R29, §2.4's F2 rows (213), §2.8 keyboard (413), §2.10 registries (462), and every item assigned to F2 in
spec/v2-upgrades/*.md (grep -n "F2" spec/v2-upgrades/*.md; product.md too). Use F1's merged ui.css and kit.js components (read the
kit.js header and /dev/kit.html) instead of writing new ones. No Class nav item, no class toasts (decision 5). Also finish F1's
view-transition follow-up in head.js (spec/v2-state/followups/F1.json).`,
    owns: 'web/assets/ui.js, head.js, quick.js, palette.js, qr.js, server/api_shell.py, server/checks/f2.py',
    units: [
      'head.js (theme, text size and motion before first paint, and F1\'s view-transition follow-up) and the ui.js core: UI.learner, UI.useLearner, UI.api (X-Learner, X-Tz, offline and retired handling), UI.prefs / UI.prefRow, theme apply, the UI.keys registry and shortcuts sheet, the skip link; server/api_shell.py with /api/shell and the §2.10 parts registry.',
      'The shell chrome: sidebar, rail, phone top bar and 5 tabs, menu sheet, account menu, section mapping (R1), the Today card and nav metas from /api/shell, on every page.',
      'Banners (retired, offline with backoff, storage blocked, first visit, save nudge), achievement and reply toasts, the quick sheet with its three tabs (R29), the palette with parsing and aliases ("circles hard 5 timed"), and qr.js (vendored MIT encoder).',
      'server/checks/f2.py covering §2.12 F2\'s acceptance, then walk every page at 1280 and 390 in light and dark with a new and a seeded learner, and fix what is broken.',
    ],
    accept: `§2.12 F2's acceptance: Shell acceptance items on the sidebar, rail, phone tabs and menu, /api/shell keys, account-menu keyboard,
palette, quick sheet, offline banner and theme (as amended by §2.13); every page loads with no console errors at 1280 and 390;
test_flow prints "all good".`,
  },
  F3: {
    title: 'F3 · Question workspace and runner', port: 8013,
    spec: `spec/rebuild-v2.md: §2.12 F3 (line 564), Part 4.2 F3 (11041), R21, R23, §2.4's F3 rows (213), §2.8's runner key maps (413);
QBank §2 in Part 3.3 (lines 3348-4779), Tests §1 and §4.3-4.8 in Part 3.4 (4780-6054), Report §1.13 in Part 3.5 (6055-7045) and
Review §8-9 in Part 3.9 (10030-10969); every item assigned to F3 in spec/v2-upgrades/*.md (grep -n "F3"; product.md too). The user
wants one test format everywhere, based on the practice session ("the practice one is the best"). Use F1's merged ui.css and kit.js.`,
    owns: 'web/assets/question.js, web/assets/runner.js, web/assets/runner.css, web/dev/workspace.html',
    units: [
      'question.js: UI.workspace (R21) in every mode (practice instant / retry / end, exam, review, quiz, inline), select-then-Check, strike and Undo, the SPR field, the check flow in the three feedback modes, tools and the calculator.',
      'runner.js and runner.css: UI.runner (the shell shared by the practice session and the test window): sticky top bar, progress rail, question strip, navigator with its views, footer, Check your work, timer, highlights and notes, calculator dock and phone sheet, the key map of §2.8.',
      'The review player, pane and history (Report §1.13, Review §8-9), with Hide answers persisting across Next.',
      'web/dev/workspace.html driving every mode with fixture questions (MC, grid-in, figure, table); walk it at 1280 and 390 in light and dark and fix what is broken.',
    ],
    accept: `§2.12 F3's acceptance: the dev page drives every mode with fixture questions (MC, grid-in, figure, table) at 1280 and 390:
select then Check, strike and Undo, highlight and reload-restore through a fake store, navigator views and Esc, Check your work tiles
adding up, calculator dock and phone sheet, the review player's Hide answers persisting across Next, and the key map of §2.8.
test_flow prints "all good".`,
  },
  F6: {
    title: 'F6 · Reports and question sets', port: 8016,
    spec: `spec/rebuild-v2.md: §2.12 F6 (line 605), Part 4.2 F6 (11056), R17, R18(c), Shell §2.10 and §10 in Part 3.1 (lines 653-2294)
and its "server/reports.py" items, the sets parts of QBank ("Shares"), Tests ("Share a test") and Review ("Shares"); every item
assigned to F6 in spec/v2-upgrades/*.md (grep -n "F6"; product.md too). The tables are F4's (merged): use them, do not change db.py.
Use F1's merged ui.css and kit.js for the modal and pages.`,
    owns: 'server/reports.py, server/sets.py, server/mail.py, web/assets/report.js, web/admin/reports/index.html, web/s/index.html, tools/reports.py, server/checks/f6.py',
    units: [
      'Server: reports.py (POST /api/report with up to 10 files on disk under server/reports/{id}/, the 10 MB cap, 10 an hour and 20 a day per learner, bounded disputes, GET /api/reports with replies, the admin endpoints behind SATF_ADMIN_TOKEN), mail.py and tools/reports.py.',
      'sets.py: POST /api/sets, GET /api/sets/{code} (public summary, no stems), /results (owner only, per-question right rates and the most common named mistake), DELETE (410 after), all through deps.access; and the /s/ landing page.',
      'report.js (UI.report(ctx) with every context and the category union of R17; mid-test reports hide marking and key disputes) and web/admin/reports/index.html.',
      'server/checks/f6.py covering §2.12 F6\'s acceptance.',
    ],
    accept: `§2.12 F6's acceptance: Shell's report and admin acceptance items; QBank's and Tests' share items read through sets (a second
learner gets identical stems; the public summary has no stems; results 403 for others; revoked -> 410). test_flow prints "all good".`,
  },
  // F5 was built outside this script by the user's other agent (branch v2/f5, rebased on master); run it with from: 'verify'.
  F5: {
    title: 'F5 · Drill engine and bank catalogue', port: 8015,
    spec: `spec/rebuild-v2.md: §2.6 the drill body (line 316), §2.12 F5 (592), Part 4.2 F5 (11046) with every Part 3 item it lists,
R10, R24, R33, R34 (Part 2, lines 130-175), R45 (repairs and fix drills serve items that offer the trap), and every item assigned to
F5 in spec/v2-upgrades/*.md (grep -n "F5"; product.md too). No class or assignment pools (decision 5).`,
    owns: 'server/drill.py, practice.py, blueprint.py, api_practice.py, api_bank.py, server/checks/f5.py (and the check_learner asserts in test_flow)',
    units: [],
    accept: `§2.12 F5's acceptance in server/checks/f5.py (every pool and alias in §2.6, preview counts and 409 reasons, templates-only and
want-regex sets, exact items refused by access(), inline drills absent from /api/history, QBank's "templates", "tiers" and "levels"
items), each exercised against a server on port 8015; repairs and {mistakes: true} drills offer the trap; test_flow prints "all good"
on 3 runs in a row.`,
  },
  F2B: {
    title: 'F2B · Shell follow-ups (frontend): run and share helpers, welcome back, offline', port: 8018,
    spec: `spec/v2-state/briefs/F2B.md ONLY for requirements, plus spec/v2-state/followups/F2.json (F2's check: the items assigned to F2 that no
task owned). The backend half (server/next.py, GET /api/next, /api/shell.next and .has, checks/f2.py) is being built by the user's other
agent: code against the endpoints the brief specifies and degrade quietly until they land. F2 is merged: extend it.`,
    owns: 'web/sw.js, web/assets/ui.js, web/assets/palette.js, web/assets/quick.js',
    units: [
      `ui.js: UI.run (start, between, rail; G1) reading /api/next and /api/shell.next, UI.autoSheet with the welcome-back sheet (U25),
UI.share (U28); gate the Today card's fact popovers on UI.has('levers') and link the flame to /me/#activity until then; replace the
retired phrases in palette.js and quick.js (G2); the quick sheet full screen under 760px; palette Recent rows keep the skill name.`,
      `web/sw.js (U18 offline) registered from ui.js; then a quick headless walk of the shell at 1280 and 390, no console errors,
test_flow still "all good".`,
    ],
    accept: `The frontend follow-ups in spec/v2-state/followups/F2.json are fixed; the Up next block, rail play button and G N render from
/api/next when it is present and degrade when it is not; the welcome-back sheet shows once a day; offline pages load from the service
worker; test_flow prints "all good".`,
  },
  // Server halves built by the user's other agent (spec/v2-state/HELPER-TASKS.md); run each with from: 'verify'.
  S9S: {
    title: 'S9S · Words server', port: 8029,
    spec: `spec/v2-state/HELPER-TASKS.md Task 1; the Words spec in spec/rebuild-v2.md Part 3.8 (lines 9134-10029) server items and
spec/v2-upgrades/words.md W1-W22 server parts; S8's two Words contracts (words.sprint_items, words.record_contest_miss).`,
    owns: 'server/words.py, server/api_words.py, server/checks/s9.py, server/words_index.json, tools/build_words.py',
    units: [],
    accept: `server/checks/s9.py covers and passes every Words server acceptance item (W7: no run of self-graded Know lifts a word
above box 3; per-sense slugs keep separate state; only reviewed frames are served unless SATF_WORDS_UNREVIEWED=1); the helpers
today_summary, minutes_today, me_stats, of_reason, sprint_items and record_contest_miss exist; test_flow prints "all good".`,
  },
  S7S: {
    title: 'S7S · Plan server', port: 8027,
    spec: `spec/v2-state/HELPER-TASKS.md Task 2; the Plan spec in spec/rebuild-v2.md Part 3.6 (lines 7046-8096) server items, R13, R14,
R15, R18(b), the S7 contract row of §2.9, and spec/v2-upgrades/plan.md server parts.`,
    owns: 'server/plan.py, server/api_plan.py, server/checks/s7.py',
    units: [],
    accept: `server/checks/s7.py covers and passes every Plan server acceptance item (as amended by §2.13 and plan.md): plan generation,
PATCH tasks with done / skipped / todo / move / swap, plan.mirror both ways, plan.today_summary, the .ics download and token feed,
the shared view; test_flow prints "all good".`,
  },
  S8S: {
    title: 'S8S · Compete server', port: 8028,
    spec: `spec/v2-state/HELPER-TASKS.md Task 3; the Compete spec in spec/rebuild-v2.md Part 3.7 (lines 8097-9133) server items, R3, R12,
R25, R28, the S8 contract row of §2.9, §2.10's write-path hooks, and spec/v2-upgrades/compete.md server parts (C1-C27). Contracts owned
by S4, S5 and S1 are PENDING by design until those sections merge; that is not a defect.`,
    owns: 'server/compete.py, server/challenge.py, server/api_compete.py, server/checks/s8.py',
    units: [],
    accept: `server/checks/s8.py passes with only other sections' contracts PENDING (s8.py --supply and --traps included, now that the
bank supply and habits.py are merged): twin daily challenges with no whole-question collisions, invite-code private contests, boards
with R12's names, ratings, rank snapshots; test_flow prints "all good".`,
  },
  // ---- wave 2: the sections (built on the merged foundations F0-F6). Server halves the user's other agent builds
  // (S7, S8, S9 servers) are not here; their pages-only tasks are added when those servers merge.
  ...section('S1', 'Account, Me, Settings, Help', 8021, `Part 3.1 §1, §3, §4, §5, §6, §8 and §9 (lines 653-2294; §2, §7 and
§10 are not yours: the shell is F2's, classes are dropped, §10 is F6's), R25, R31, Compete §9's Me Boards block, Words' Me items,
Review's Saved content card, Tests' test defaults`, 'shell-me',
    'web/me/**, web/signin/**, web/pair/**, web/share/**, web/help/**, web/diagnostic/signup.html, web/diagnostic/verified.html', true),
  ...section('S3', 'Today', 8023, `Part 3.2 in full (lines 2295-3347), R27 (the questions of the day), R30 (the Review card and
Words tile), and the Today items of Review §10, Words §11 and Compete §9`, 'today',
    'web/index.html, server/api_today.py, server/daily.py, server/checks/s3.py'),
  ...section('S4', 'Practice builder and session', 8024, `Part 3.3 in full (lines 3348-4779; components from F3, report and sets
from F6, the body from F5), Compete §8 for the practice session (R28), Review §10's session strip, Words' session hooks, Plan's session
summary; also F6's drill.py follow-up (pool 'set' through sets.serve, in spec/v2-state/followups/F6.json)`, 'practice',
    'web/practice/**, server/drill.py, server/practice.py, server/api_practice.py, server/checks/s4.py'),
  ...section('S5', 'Tests and the test window', 8025, `Part 3.4 in full (lines 4780-6054; runner components from F3), Compete §8
for the test window, the Weekly Module and Season Final starts, Review's flags in the runner, Shell's UI.learner and token rules for
web/test/ (R32), QBank's "shelf sections and diagnostic forms remember what they serve". One test format everywhere, based on the
practice session (the user: "the practice one is the best")`, 'tests',
    'web/tests/**, web/test/**, web/diagnostic/index.html, server/api_tests.py, server/papers.py, server/blueprint.py, server/mocks.json, server/forms.json, tools/moderate.py, server/checks/s5.py'),
  ...section('S6', 'Results and the score report', 8026, `Part 3.5 in full (lines 6055-7045; the player from F3, the report dialog
from F6), R26, R35, the report's parts of Tests (?q=, peers, notes, confidence, away, changes), Words (redirect), Compete (contest rows,
Ranked pill) and Review (Flagged filter); also the follow-ups in spec/v2-state/followups/F1.json (UI.sittingCard) and F5.json (move
the R24 history filter into api_results.history so S4 can delete F5's shadow GET /api/history). A skill on Results opens its stats and
starts Practice on only that skill (the user's request)`, 'reports',
    'web/results/**, web/assets/results-ui.js', true),
  ...section('S10', 'Review', 8030, `Part 3.9 in full (lines 10030-10969; components from F3, traps logic from F4, sets from F6), R2,
R5's endpoints`, 'review',
    'web/review/**, web/mistakes/**', true),
  ...section('S7', 'Plan pages', 8027, `Part 3.6 in full (lines 7046-8096): the PAGES only. The server (server/plan.py, api_plan.py) is
merged from the user's other agent: use its endpoints; list any server change you need instead of making it`, 'plan',
    'web/plan/**, web/assets/plan-ui.js', true),
  ...section('S8', 'Compete pages', 8028, `Part 3.7 in full (lines 8097-9133): the PAGES only (the runner hooks' UI is S4's and S5's). The
server (server/compete.py, challenge.py, api_compete.py) is merged from the user's other agent: use its endpoints`, 'compete',
    'web/compete/**, web/challenge/**, web/assets/compete-ui.js', true),
  ...section('S9', 'Words pages', 8029, `Part 3.8 in full (lines 9134-10029): the PAGES only. The server (server/words.py, api_words.py) is
merged from the user's other agent: use its endpoints`, 'words',
    'web/words/**, web/vocabulary/**, web/assets/words-ui.js', true),
  // F4 was built outside this script by another agent (branch v2/f4, from v2/f0); run it with from: 'verify'.
  F4: {
    title: 'F4 · Data layer', port: 8014,
    spec: `spec/rebuild-v2.md: §2.5 schema (line 243), §2.7 preferences (371), §2.12 F4 (584), Part 4.2 F4 (11013) with every Part 3
item it lists, the resolutions it builds in Part 2 (R5-R9, R11-R13, R15, R16, R19; lines 130-175), and every item assigned to F4 in
spec/v2-upgrades/*.md (grep -n "F4" spec/v2-upgrades/*.md; product.md's cross-file overrides too). No class tables or fields
(decision 5).`,
    owns: 'server/db.py, progress.py, prefs.py, estimate.py, satdates.py, scoring.py, deps.py, api_me.py, api_notes.py, server/checks/f4.py',
    units: [],
    accept: `§2.12 F4's acceptance, run as server/checks/f4.py and checked by reading it (norm merging, repeat not moving mastery, unsure
opening with owed 1, a relapse, check-ins at 3/10/30, days() with a rest-day plan (streak 6), a module's minutes counted once, prefs
422 and merge, access() on a live test item and today's challenge item, carry of every table), plus every server item Part 4.2
lists for F4, each exercised against a server on port 8014. Migrations run on a copy of an old database (make one from master's
schema with some attempts, traps and saved rows) without losing a row. test_flow prints "all good".`,
  },
}
const CONTEXT = t => `
PROJECT: ${REPO} -- "SAT Freshman", a free SAT prep website (FastAPI + sqlite in server/, static pages in web/). We are building
v2 from spec/rebuild-v2.md (Part 2 foundations, Part 3 section specs, Part 4 tasks). spec/v2-upgrades/<section>.md upgrades each
section to WAY better than the competitor TopTierPrep and overrides rebuild-v2.md where it says so. spec/v2-decisions.md wins
over both: twin daily challenges; Words = SAT Reading & Writing vocabulary only; Math-first, full SAT later, so build additively;
no visual budget (anything that helps study or makes things clearer or more convenient belongs; do not strip features to look
minimal); NO CLASSES (no teacher/student roles, classes, homework, assignments, class codes, /class/, /join/). Completely free.
Orange #F18508 is the only accent.
YOUR TASK: ${t.title} (port ${t.port}). You own only: ${t.owns}. Read: ${t.spec}
If you need a change in a file you do not own, do not make it; list it in your return.
RULES:
- You are in your own git worktree. First: git switch v2/${t.id.toLowerCase()} 2>/dev/null || git switch -c v2/${t.id.toLowerCase()} master.
  If the branch already existed and master has moved on (git merge-base --is-ancestor master HEAD fails), run git rebase
  master first and resolve any conflict keeping both sides' intent; master now holds the merged servers and fixes.
  Then git log --oneline master..HEAD and git status: continue from any predecessor's commits and uncommitted edits, never
  redo or discard them. Never create another branch for this task, and never move the branch with update-ref or branch -f.
  If git says the branch is already checked out in another worktree: if git -C <that worktree> status --short is empty, run
  git -C <that worktree> switch --detach and switch here; otherwise cd into that worktree and continue its work there. When you
  finish, commit everything (leave no uncommitted file) and run git switch --detach so the branch is free. Before every
  commit, check that git branch --show-current prints v2/<task>: never commit on a detached HEAD.
- Commit on that branch after each finished piece of work (a file, a component group), with a real message ending with the line
  "${SIGN}". Never push. Never merge. Never touch master or the main working tree at ${REPO} (work only in your worktree).
- Do not edit spec/rebuild-v2.md (other agents cite its line numbers).
- A server, if you need one: SATF_DB=$PWD/server/v2.db PYTHONPATH=. python3 -m uvicorn server.app:app --port ${t.port}. Never
  use port 8000 or server/satfreshman.db. Stop your server when you are done.
- Headless browser checks: Python Playwright with p.chromium.launch(executable_path="${SHELL}") (the bundled chromium
  crashes on this machine).
- PYTHONPATH=. python3 server/test_flow.py must still print "all good".
EFFICIENCY (tokens are scarce; every tool result stays in your context for the rest of the task):
- Cut every command's output: pipe through tail -n 40, grep, or head. Never cat a big file, print a whole JSON, or dump a
  full test log; for a failing test show only the traceback's last lines.
- Read your brief once. Read other code only where you call it, by line range (sed -n or grep -n first), not whole files.
- Plan the file, then write it in one go; edit with small targeted replacements, never rewrite a file you already wrote.
- Run the checks once per finished group of files, not after every edit.
`

const VERDICT = { type: 'object', properties: {
  pass: { type: 'boolean' }, evidence: { type: 'string' },
  defects: { type: 'array', items: { type: 'object', properties: {
    where: { type: 'string' }, what: { type: 'string' }, fix: { type: 'string' },
    severity: { type: 'string', enum: ['blocker', 'followup'] } }, required: ['where', 'what', 'fix', 'severity'] } },
}, required: ['pass', 'evidence', 'defects'] }

const unit = (t, i) => agent(`${CONTEXT(t)}
YOUR UNIT (${i + 1} of ${t.units.length}): ${t.units[i]}
Earlier units are committed on the branch; later units are other agents' jobs, so do only this one, fully, to the spec and its
upgrades. Commit as you go. Return what you built, the commits, and anything left undone or needed from another owner.`,
  { label: `build ${t.id} ${i + 1}/${t.units.length}`, phase: 'Build', isolation: 'worktree' })

// Check policy (the user, 2026-09-24): one check, one fix, merge; small or data-only tasks set inline: true and get the
// main session's inline check instead of a check agent. Leftovers go on a follow-up list for the section that uses
// them or for I1. A task sets rounds: 2 only when it puts content in front of students (questions, definitions).
const verify = (t, round) => agent(`${CONTEXT(t)}
You are the VERIFIER, not the builder: do not fix anything and do not commit. Run git switch --detach v2/${t.id.toLowerCase()}.
Your requirements: spec/v2-state/briefs/${t.id}-check.md if it exists (open the full brief only to look up one item).
Check, with evidence you ran yourself:
1. The task's own check file (server/checks/${t.id.toLowerCase()}.py) if it exists, and PYTHONPATH=. python3 server/test_flow.py.
2. ${t.accept}
3. A SAMPLE of 15 requirements from the spec sections above and the upgrades assigned to ${t.id} (pick across the whole list and
   say which), built as written.
4. Nothing outside the owned files changed (git diff --stat master...HEAD), and nothing contradicts spec/v2-decisions.md.
Mark each defect severity "blocker" (a failing check, broken or unsafe behaviour, data loss, a security hole, a contradiction of
the decisions, or something another task needs now) or "followup" (anything else). pass = no blockers.`,
  { label: `verify ${t.id} r${round}`, phase: 'Verify', schema: VERDICT, isolation: 'worktree' })

const fix = (t, defects, round) => agent(`${CONTEXT(t)}
A verifier found defects in ${t.title}. ${typeof defects === 'string' ? `Read them from ${defects}.` : `DEFECTS: ${JSON.stringify(defects)}`}
An earlier fixer may have been cut off part way: check the branch first and do not redo what is fixed. Fix every blocker, and
every followup that is small, in the files you own (list any that need another owner). Fix only the listed defects: do
not widen the scope, and if a fix creates new work (content to add, a pattern elsewhere), list it in your return instead of doing it. Then run the task's check file and
test_flow; both must pass. Commit as you go, and return what you changed and which defects are left.`,
  { label: `fix ${t.id} r${round}`, phase: 'Fix', isolation: 'worktree' })

async function run(a) {
  const t = { ...TASKS[a.id], id: a.id }
  const out = { id: a.id, branch: `v2/${a.id.toLowerCase()}`, units: [], rounds: [] }
  const max = t.rounds || 1
  let round = a.round || 1
  if (!a.from || a.from === 'build') {
    for (let i = a.unit || 0; i < t.units.length; i++) out.units.push(await unit(t, i))
  }
  // small or data-only tasks (inline: true) skip the check agent: the main session checks them inline (the user, 2026-09-24)
  if (t.inline) { out.result = 'built; inline check by the main session, then merge'; return out }
  if (a.from === 'fix') { out.fixes = [await fix(t, a.issues, round)]; out.result = 'fixed; ready to merge (leftovers in the fix report)'; return out }
  for (;;) {
    const v = await verify(t, round)
    out.rounds.push(v)
    if (!v) { out.result = 'verifier died'; return out }
    const blockers = (v.defects || []).filter(d => d.severity === 'blocker')
    out.followups = (v.defects || []).filter(d => d.severity !== 'blocker')
    if (!blockers.length) { out.result = 'passed; ready to merge'; return out }
    const r = await fix(t, v.defects, round)
    out.fixes = [...(out.fixes || []), r]
    if (round >= max) { out.result = 'fixed once; ready to merge (leftovers in the fix report)'; return out }
    round++
  }
}

// At most WORKERS tasks at a time (the user, 2026-09-27: finish a few before usage limits instead of many at once).
const WORKERS = 3
const queue = [...args]
const results = []
await parallel(Array.from({ length: WORKERS }, () => async () => {
  while (queue.length) { const a = queue.shift(); results.push(await run(a)) }
}))
return results
