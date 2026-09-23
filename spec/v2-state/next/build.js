export const meta = {
  name: 'v2-build',
  description: 'Build v2 foundation and section tasks: unit builders on the task branch, an independent verifier, up to 3 fix rounds',
  phases: [
    { title: 'Build', detail: 'one agent per unit, in order, committing on v2/<task>' },
    { title: 'Verify', detail: 'independent verifier tries to refute that the task is done' },
    { title: 'Fix', detail: 'fix the verifier defects on the task branch' },
  ],
}

// args: [{id, from?: 'build' | 'verify' | 'fix', unit?: n, round?: n, issues?: path}]
// Everything lives on the task branch and in saved verdicts, so a restart names where to begin
// (from: 'verify' after a finished build, 'fix' with the saved issues file) and nothing finished re-runs.

const REPO = '/Users/workingmyassof/satbank'
const SIGN = 'Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>'
const SHELL = '/Users/workingmyassof/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell'

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
    title: 'BANK · three question-bank flaws', port: 8019,
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
  Then git log --oneline master..HEAD and git status: continue from any predecessor's commits and uncommitted edits, never
  redo or discard them. If git says the branch is already checked out in another worktree, cd into that worktree and work
  there instead: it holds your predecessor's work. When you finish, commit and run git switch --detach so the branch is free.
- Commit on that branch after each finished piece of work (a file, a component group), with a real message ending with the line
  "${SIGN}". Never push. Never merge. Never touch master or the main working tree at ${REPO} (work only in your worktree).
- Do not edit spec/rebuild-v2.md (other agents cite its line numbers).
- A server, if you need one: SATF_DB=$PWD/server/v2.db PYTHONPATH=. python3 -m uvicorn server.app:app --port ${t.port}. Never
  use port 8000 or server/satfreshman.db. Stop your server when you are done.
- Headless browser checks: Python Playwright with p.chromium.launch(executable_path="${SHELL}") (the bundled chromium
  crashes on this machine).
- PYTHONPATH=. python3 server/test_flow.py must still print "all good".
`

const VERDICT = { type: 'object', properties: {
  pass: { type: 'boolean' }, evidence: { type: 'string' },
  defects: { type: 'array', items: { type: 'object', properties: { where: { type: 'string' }, what: { type: 'string' }, fix: { type: 'string' } }, required: ['where', 'what', 'fix'] } },
}, required: ['pass', 'evidence', 'defects'] }

const unit = (t, i) => agent(`${CONTEXT(t)}
YOUR UNIT (${i + 1} of ${t.units.length}): ${t.units[i]}
Earlier units are committed on the branch; later units are other agents' jobs, so do only this one, fully, to the spec and its
upgrades. Commit as you go. Return what you built, the commits, and anything left undone or needed from another owner.`,
  { label: `build ${t.id} ${i + 1}/${t.units.length}`, phase: 'Build', isolation: 'worktree' })

const verify = (t, round) => agent(`${CONTEXT(t)}
You are the VERIFIER, not the builder: do not fix anything and do not commit. Run git switch --detach v2/${t.id.toLowerCase()}.
Try to REFUTE that ${t.title} is done. Check, with evidence you ran yourself:
1. ${t.accept}
2. Every requirement of the spec sections above and every upgrade assigned to ${t.id} in spec/v2-upgrades/*.md is built as
   written (go item by item; missing, partial, vague or visibly broken fails).
3. Nothing outside the owned files changed: git diff --stat master...HEAD.
4. Nothing contradicts spec/v2-decisions.md.
Report every defect with the file and the item it violates. Default to pass=false if unsure.`,
  { label: `verify ${t.id} r${round}`, phase: 'Verify', schema: VERDICT, isolation: 'worktree' })

const fix = (t, defects, round) => agent(`${CONTEXT(t)}
A verifier found defects in ${t.title}. ${typeof defects === 'string' ? `Read them from ${defects}.` : `DEFECTS: ${JSON.stringify(defects)}`}
An earlier fixer may have been cut off part way: check the branch first and do not redo what is fixed. Fix every defect in the
files you own (list any that need another owner), commit as you go, and return what you changed.`,
  { label: `fix ${t.id} r${round}`, phase: 'Fix', isolation: 'worktree' })

async function run(a) {
  const t = { ...TASKS[a.id], id: a.id }
  const out = { id: a.id, branch: `v2/${a.id.toLowerCase()}`, units: [], rounds: [] }
  let round = a.round || 1
  let defects = a.issues || null
  if (!a.from || a.from === 'build') {
    for (let i = a.unit || 0; i < t.units.length; i++) out.units.push(await unit(t, i))
  }
  if (a.from === 'fix') await fix(t, defects, round++)
  for (;;) {
    const v = await verify(t, round)
    out.rounds.push(v)
    if (!v) { out.result = 'verifier died'; return out }
    if (v.pass) { out.result = 'passed'; return out }
    if (round >= 4) { out.result = 'still failing after 3 fix rounds'; out.defects = v.defects; return out }
    await fix(t, v.defects, round++)
  }
}

return await pipeline(args, a => run(a))
