export const meta = {
  name: 'i1-nothing-dropped',
  description: 'I1 audit: per section, list every spec and upgrade requirement as built / missing / weaker, then refute each gap claim',
  phases: [
    { title: 'Audit', detail: 'one auditor per section, full spec + full upgrade file + the code and pages' },
    { title: 'Refute', detail: 'an independent agent tries to disprove each missing / weaker claim' },
  ],
}

// Runs after the sections are merged into master (the user, 2026-09-27: "okay lets add that").
// args: optional list of section ids; default all. Read-only: no agent edits or commits anything.
// The confirmed gaps become build tasks (spec/v2-state/followups/audit-<id>.json, then build.js entries).

const REPO = '/Users/workingmyassof/freshbot/satbank'
const SHELL = '/Users/workingmyassof/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell'

const SECTIONS = {
  S1: { name: 'Account, Me, Settings, Help', lines: '653-2294 (§1, §3-§6, §8, §9)', up: 'shell-me', pages: '/me/, /me/settings/, /signin/, /pair/, /share/, /help/' },
  SHELL: { name: 'The shell (F2 + F2B)', lines: '653-2294 (§2 only)', up: 'shell-me', pages: 'the sidebar, rail, phone bar and tabs, menu sheet, palette and quick sheet on every page' },
  RUNNER: { name: 'The question workspace, test window and review player (F3)', lines: '3348-4779 (§2) and 4780-6054 (§1, §4.3-4.8)', up: 'practice', pages: 'the session and the test window: the question, strip, navigator, footer, tools, review player' },
  S3: { name: 'Today', lines: '2295-3347', up: 'today', pages: '/' },
  S4: { name: 'Practice builder and session', lines: '3348-4779', up: 'practice', pages: '/practice/, /practice/session/' },
  S5: { name: 'Tests and the test window', lines: '4780-6054', up: 'tests', pages: '/tests/, /test/, /diagnostic/' },
  S6: { name: 'Results and the score report', lines: '6055-7045', up: 'reports', pages: '/results/ and a sitting report' },
  S7: { name: 'Plan', lines: '7046-8096', up: 'plan', pages: '/plan/' },
  S8: { name: 'Compete', lines: '8097-9133', up: 'compete', pages: '/compete/, /challenge/' },
  S9: { name: 'Words', lines: '9134-10029', up: 'words', pages: '/words/, /words/run/' },
  S10: { name: 'Review', lines: '10030-10969', up: 'review', pages: '/review/' },
}

const ITEMS = { type: 'object', properties: {
  total: { type: 'integer' },
  built: { type: 'integer' },
  gaps: { type: 'array', items: { type: 'object', properties: {
    item: { type: 'string' }, source: { type: 'string' }, status: { type: 'string', enum: ['missing', 'weaker', 'contradicts'] },
    evidence: { type: 'string' }, build: { type: 'string' } }, required: ['item', 'source', 'status', 'evidence', 'build'] } },
}, required: ['total', 'built', 'gaps'] }

const VERDICTS = { type: 'object', properties: {
  confirmed: { type: 'array', items: { type: 'object', properties: {
    item: { type: 'string' }, status: { type: 'string' }, evidence: { type: 'string' }, build: { type: 'string' } },
    required: ['item', 'status', 'evidence', 'build'] } },
  refuted: { type: 'array', items: { type: 'object', properties: { item: { type: 'string' }, why: { type: 'string' } },
    required: ['item', 'why'] } },
}, required: ['confirmed', 'refuted'] }

const COMMON = s => `
Repo ${REPO} (master, with every section merged). READ-ONLY: do not edit, do not commit. Run the app yourself on port 8050+ with
SATF_DB=<a temp file> (never port 8000 or server/satfreshman.db); headless browser: Python Playwright with
p.chromium.launch(executable_path="${SHELL}"). Keep command output short (tail / grep).
Section: ${s.name}. Its pages: ${s.pages}. The requirements are the FULL texts, not the briefs: spec/rebuild-v2.md lines ${s.lines},
spec/v2-upgrades/${s.up}.md (accepted upgrades and spec overrides), the rows of spec/v2-upgrades/product.md that name this section,
and spec/v2-decisions.md (which wins over everything: no classes; Words is R&W only; twin daily challenges; no feature is cut to look
minimal). The product must be WAY better than TopTierPrep, so "weaker" means built but less than the spec or upgrade says.
`

const audit = id => agent(`${COMMON(SECTIONS[id])}
You are the AUDITOR. Enumerate EVERY requirement in those texts (each upgrade's screens, rules, data and acceptance items; each
design item of the section spec; each server item), then find its implementation in the code and see it on the page with a new
and a seeded learner at 1280 and 390. Classify each: built (as specified), missing, weaker (present but less than specified), or
contradicts (against the decisions). Report total, built, and every gap with its source (file and heading or upgrade id), the
evidence you saw, and exactly what to build. ALSO check every page of the section against decision 7 (a calm, quiet interface:
no zeros or defaults on screen, no fact repeated, details on demand, easy on the eyes) and report each violation as a gap with
status 'contradicts', source 'decision 7', the screen and the text, and the calmer version to build (keeping every feature).`, { label: `audit ${id}`, phase: 'Audit', schema: ITEMS })

const refute = (id, found) => agent(`${COMMON(SECTIONS[id])}
You are an independent REFUTER. An auditor claims these gaps: ${JSON.stringify(found.gaps)}
For each, try to prove it wrong: find the code and the page where the requirement IS built as specified, or show the requirement
does not say what the auditor thinks (or that spec/v2-decisions.md overrides it). Keep a gap only if you cannot refute it; then
restate what to build precisely. Return confirmed and refuted.`, { label: `refute ${id}`, phase: 'Refute', schema: VERDICTS })

const ids = Array.isArray(args) && args.length ? args : Object.keys(SECTIONS)
const out = await pipeline(ids,
  id => audit(id),
  (found, id) => Promise.resolve(found && found.gaps && found.gaps.length ? refute(id, found) : { confirmed: [], refuted: [] })
    .then(v => ({ id, total: found ? found.total : 0, built: found ? found.built : 0, confirmed: v ? v.confirmed : [], refuted: v ? v.refuted.length : 0 })))
const gaps = out.filter(Boolean).reduce((n, r) => n + r.confirmed.length, 0)
log(`${gaps} confirmed gaps across ${ids.length} sections`)
return out
