export const meta = {
  name: 'v2-continue-2',
  description: 'Finish the way-better pass: each section applies its saved verdict once (no second check); grid-in is complete',
  phases: [
    { title: 'Fix', detail: 'way-better fixers from the saved skeptic verdicts (also strip class material, decision 5)' },
    { title: 'Skeptic', detail: 'try to refute that each section is way better; merely equal fails' },
  ],
}

// Written 2026-09-23 when the user paused the run. Every step below starts from state saved on
// disk (spec/v2-state/next/*.json and the git branches), so nothing finished is re-run.

const SCR = '/private/tmp/claude-501/-Users-workingmyassof-satbank/9030c288-6222-49fa-a25a-6e6802e22cd3/scratchpad'
const REPO = '/Users/workingmyassof/satbank'
const NEXT = `${REPO}/spec/v2-state/next`
const SIGN = 'Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>'

const CONTEXT = `
PROJECT: ${REPO} -- "SAT Freshman", a free SAT prep website (FastAPI + sqlite in server/, static pages in web/, shared
web/assets/ui.css + ui.js). The competitor is TopTierPrep. Sources on them: spec/toptierprep-teardown.md, ${SCR}/ttp-notes.md and
${SCR}/ttp-live.md (if a scratchpad file is missing, rely on the teardown).
The v2 plan is spec/rebuild-v2.md (Part 2 shared foundations, Part 3 nine section specs, Part 4 build order). spec/v2-upgrades/
<section>.md holds the upgrades that push each section to WAY better than TopTierPrep. spec/v2-decisions.md holds the user's
decisions and wins over everything: twin daily challenges; Words = SAT Reading & Writing (EBRW) vocabulary only; Math-first,
the full SAT later, so build additively; no visual budget -- anything that helps study OR makes things clearer, more
straightforward or more convenient belongs; NO CLASSES (no teacher/student roles, classes, homework, assignments, class codes,
/class/ or /join/, class boards; Compete's private contests are an invite code or link that Compete owns).
OUR UNIQUE POWER: unlimited verified SAT Math questions from ~386 templates over 19 topics; every wrong option (and most grid-in
wrong values) names the misconception behind it; every item has a rationale and a skill; (template, seed) addressing means it
never runs out, never repeats, regenerates exactly, and "another like this" is always possible. Every answer is recorded.
CONSTRAINTS: completely free. Orange #F18508 is the only accent.
THE USER: "you are expected to build smth WAY BETTER"; "DONT CHASE MINIMALISM NOW, review everything they have and PRODUCE
SIMILAR STUFF IN WAY BETTER WAYS regarding ui/ux and functionality, think of extra functionalities, something they missed."
The bar: a student using TopTierPrep today opens ours and wants to switch. Parity is failure.
Do not commit anything; only write the file you are told you own.
`

const LINES = {
  'shell-me': '653-2294', today: '2295-3347', practice: '3348-4779', tests: '4780-6054', reports: '6055-7045',
  plan: '7046-8096', compete: '8097-9133', words: '9134-10029', review: '10030-10969',
  product: '1-648 and 10970-11183 (read Part 3 headings too)',
}
const TITLES = {
  'shell-me': 'App shell, navigation, profile and account', today: 'Today (the dashboard)',
  practice: 'Practice: the builder and the session', tests: 'Practice tests and the test window',
  reports: 'Score report and results', plan: 'Study plan', compete: 'Compete: contests, rankings, leaderboards',
  words: 'Words (vocabulary)', review: 'Review: redo, marked, saved, history, fixed',
  product: 'The product as a whole: signature features and how the sections work together',
}
// where each section stands: fix = the skeptic verdict to fix first (a file), round = the round that fix belongs to
const WB = [
  { id: 'shell-me', fix: `${NEXT}/shell-me-skeptic2-issues.json`, round: 2 },
  { id: 'today', fix: null, round: 2 },
  { id: 'practice', fix: `${NEXT}/practice-skeptic1-issues.json`, round: 1 },
  { id: 'tests', fix: `${NEXT}/tests-skeptic1-issues.json`, round: 1 },
  { id: 'reports', fix: `${NEXT}/reports-skeptic1-issues.json`, round: 1 },
  { id: 'plan', fix: `${NEXT}/plan-skeptic1-issues.json`, round: 1 },
  { id: 'compete', fix: `${NEXT}/compete-skeptic1-issues.json`, round: 1 },
  { id: 'words', fix: `${NEXT}/words-skeptic1-issues.json`, round: 1 },
  { id: 'review', fix: `${NEXT}/review-skeptic1-issues.json`, round: 1 },
  { id: 'product', fix: `${NEXT}/product-skeptic1-issues.json`, round: 1 },
]

const VERDICT = { type: 'object', properties: {
  pass: { type: 'boolean' },
  failures: { type: 'array', items: { type: 'object', properties: { feature: { type: 'string' }, why_not_way_better: { type: 'string' }, fix: { type: 'string' } }, required: ['feature', 'why_not_way_better', 'fix'] } },
}, required: ['pass', 'failures'] }

const skeptic = (id, round) => agent(`${CONTEXT}
YOUR SECTION: ${TITLES[id]}. Read spec/rebuild-v2.md lines ${LINES[id]}, spec/v2-upgrades/${id}.md, spec/v2-decisions.md and the
TopTierPrep sources for this area. Try to REFUTE the claim that this section, with the upgrades, is WAY better than TopTierPrep's.
Go feature by feature through what they have. A feature fails if ours is only equal, if the upgrade is vague or not buildable as
written, if it drops something of theirs, if it contradicts spec/v2-decisions.md (including any class, teacher or homework
material, which must be gone), or if it cuts or hides something useful to look lighter. Default to failing anything you are
unsure about. pass is true only if nothing fails.`, { label: `skeptic ${round}: ${id}`, phase: 'Skeptic', schema: VERDICT })

const fix = (id, failures, round) => agent(`${CONTEXT}
YOUR SECTION: ${TITLES[id]}. A skeptic found failures in spec/v2-upgrades/${id}.md -- ${typeof failures === 'string'
  ? `read them from ${failures}` : `listed here: ${JSON.stringify(failures)}`}.
An earlier fixer may have been interrupted part way through this same list: read the file as it stands now and finish the job,
do not undo what is already fixed. Edit that file (you own only it) so every failure is fixed: upgrade what was only parity, make
vague parts buildable, restore anything dropped, respect spec/v2-decisions.md. Also remove every class, teacher, homework,
assignment or class-code element from the file (decision 5), replacing Compete's class-based groups with invite-code private
contests where they are referenced. Update the scorecard verdicts to match. Write the file a section at a time, saving as you
go. Return a short list of what you changed.`, { label: `fix ${round}: ${id}`, phase: 'Fix' })

// The user dropped the second check: each section applies the fix its last saved verdict calls for,
// once, and stops. No further skeptic rounds. (today already had its fix, so it has nothing left.)
async function wayBetter(s) {
  if (!s.fix) return { id: s.id, result: 'already fixed; no further check' }
  const changed = await fix(s.id, s.fix, s.round)
  return { id: s.id, result: 'fixed from its saved verdict', changed }
}

// ------------------------------------------------------------------ grid-in (capped: no more fix rounds)
const COMMON = `
The repo is ${REPO}. satbank/ generates SAT Math items; a multiple-choice item's wrong options come from Mis(reason, value)
lists naming the misconception behind each wrong value. Branch v2/t-bank-all adds Item.spr_mistakes to grid-in items, built from
the same template mistake logic, filtered by satbank.item.gridin_mistakes and enforced by satbank/audit.py. A wrong grid-in a
student types is matched to these values to name their mistake, so a WRONG entry tells a student they made a mistake they did
not make. Rules: multiple-choice output must equal master's exactly; grid-in items may differ from master only in spr_mistakes;
PYTHONPATH=. python3 -m satbank check --topic <slug> must print PASS. Commits end with the line "${SIGN}". Never push; never merge
into master or into v2/t-bank-all. Do not touch satbank/item.py or satbank/audit.py.
`
const TVERDICT = { type: 'object', properties: {
  pass: { type: 'boolean' }, evidence: { type: 'string' },
  defects: { type: 'array', items: { type: 'object', properties: { where: { type: 'string' }, what: { type: 'string' }, fix: { type: 'string' } }, required: ['where', 'what', 'fix'] } },
}, required: ['pass', 'evidence', 'defects'] }

const recheck = t => agent(`${COMMON}
Try to REFUTE that topic ${t} is correct on branch v2/t-bank-fix-${t}. In this worktree: git switch --detach v2/t-bank-fix-${t};
do not commit.
1. MCQ identical to master for every template of satbank/topics/${t} (dump generate(template, seed) for seeds 0-80 with default
   and fmt="mcq" on master and on the branch; compare stem, choices, reasons, answer, rationale).
2. Grid-ins differ from master only in spr_mistakes (same dump with fmt="spr").
3. Every reason is real: for at least 25 random grid-in items across the topic's templates, recompute each spr_mistakes value by
   hand from the stem and the reason; each must be a plausible wrong route to this question's answer. Report every defect with
   the TEMPLATE NAME in "where".
4. The gate: PYTHONPATH=. python3 -m satbank check --topic ${t} -> PASS.
Default to pass=false if unsure.`, { label: `final recheck: ${t}`, phase: 'Grid-in', schema: TVERDICT, isolation: 'worktree' })

const drop = (t, defects) => agent(`${COMMON}
Topic ${t} has used its fix rounds. Make it safe instead of fixing it further: in this worktree run
git switch v2/t-bank-fix-${t}, and for every TEMPLATE named in the defects below, stop passing spr_mistakes in that template (so
its grid-ins fall back to naming the skill, as before this project). Leave every other template as it is. Then prove MCQ output is
identical to master for the topic (seeds 0-80), that the dropped templates' grid-ins have empty spr_mistakes and are otherwise
unchanged, and that PYTHONPATH=. python3 -m satbank check --topic ${t} prints PASS. Commit on v2/t-bank-fix-${t}.
DEFECTS: ${typeof defects === 'string' ? `read them from ${defects}` : JSON.stringify(defects)}
Return the templates dropped, the templates that keep named mistakes, and the evidence.`, { label: `drop: ${t}`, phase: 'Grid-in', isolation: 'worktree' })

const continueFix = t => agent(`${COMMON}
An earlier fixer for topic ${t} was interrupted; its partial work is committed on v2/t-bank-fix-${t} (commit "Checkpoint: ...").
In this worktree run git switch v2/t-bank-fix-${t}, read the defects from ${NEXT}/${t}-recheck0-issues.json, finish fixing them on
top of the checkpoint (edit only satbank/topics/${t}/), prove MCQ identical to master (seeds 0-80), grid-ins changed only in
spr_mistakes, and PYTHONPATH=. python3 -m satbank check --topic ${t} prints PASS. Commit on v2/t-bank-fix-${t}.
Return what you changed and the evidence.`, { label: `fix (continued): ${t}`, phase: 'Grid-in', isolation: 'worktree' })

// All grid-in topics were checked and integrated at f4bf864. Do not rerun them.

async function gridin(x) {
  const t = x.t
  if (x.do === 'done') return { topic: t, result: 'passed', branch: `v2/t-bank-fix-${t}` }
  if (x.do === 'drop') {
    const r = await drop(t, `${NEXT}/${t}-recheck2-issues.json`)
    return { topic: t, result: 'dropped failing templates', branch: `v2/t-bank-fix-${t}`, report: r }
  }
  if (x.do === 'fix-then-recheck') await continueFix(t)
  const v = await recheck(t)
  if (!v) return { topic: t, result: 'recheck died', branch: `v2/t-bank-fix-${t}` }
  if (v.pass) return { topic: t, result: 'passed', branch: `v2/t-bank-fix-${t}` }
  const r = await drop(t, v.defects)
  return { topic: t, result: 'dropped failing templates', branch: `v2/t-bank-fix-${t}`, report: r }
}

const wb = await pipeline(WB, s => wayBetter(s))
return { wayBetter: wb }
