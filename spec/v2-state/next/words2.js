export const meta = {
  name: 'words-frames',
  description: 'Finish the Words content: fills, ~1,500 frames and ~700 confusions, fold the parts, then an independent accuracy check with one fix round',
  phases: [
    { title: 'Setup', detail: 'fills.json and the frame loader' },
    { title: 'Author', detail: '4 frame authors by class group, 1 confusions author' },
    { title: 'Fold', detail: 'parts into the final files, collections refreshed, plan removed' },
    { title: 'Check', detail: 'independent accuracy checks of entries and frames, then a fix round' },
  ],
}

// Runs after words.js finished the library (1,242 senses, transitions, pairs, roots, foils).
// args: { from?: 'setup' | 'author' | 'fold' | 'check', only?: [author ids] } so a restart runs only what is missing.

const W = '/Users/workingmyassof/satbank/.claude/worktrees/words'
const SIGN = 'Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>'

const CONTEXT = `
You are working on the Words (vocabulary) CONTENT of "SAT Freshman", a free SAT prep site. Work ONLY in the git worktree ${W}
(branch v2/words-content): cd there first. Never touch the main working tree, master, or any other branch.
Read first: spec/v2-decisions.md (it wins; decision 2 = SAT Reading & Writing vocabulary only), spec/v2-upgrades/words.md (W1-W4,
W17, and in §3.1 overrides 12, 17 and 51) and the Words spec in spec/rebuild-v2.md lines 9134-10029. Match the formats of the
existing files in server/words/ and tools/build_words.py (the validator).
QUALITY: our own wording, American English, correct for the sense the SAT tests. Frames read like real SAT passages (1-3
sentences, a clue marked [[...]] that decides the blank). Any quotation from a real text must be cut from the real text: fetch the
plain text from gutenberg.org with curl and copy the passage exactly; never write a quotation or a historical fact from memory
without checking it.
GIT: commit only the files you own, with git commit -m "<real message>" -- <your paths>, the message ending with the line
"${SIGN}". Others share this worktree: on index.lock, wait a few seconds and retry. Never push or merge. Commit every ~50 items.
Before starting, check git log and your files: continue a predecessor's partial file, never restart it.
`

const setup = () => agent(`${CONTEXT}
YOUR JOB (you own server/words/fills.json and tools/build_words.py): write fills.json (W1's slot pools: researcher names from many
origins, fields, sites, organisms, artworks, periods, quantities; at least 40 values per pool) and make build_words.py load
server/words/parts/frames_*.json into the frame list and enforce W1's frame rules (one ____, a [[clue]], known slots, need tags
valid against classes.json, reviewed null or backed by adjudications) and the supply minimums as warnings until the frames land.
Also fix the "waste" family, which has only 2 member words: write a third real SAT word for it as a full entry in
server/words/parts/sat_fix.json (you own it; the loader already reads parts/sat_*.json). Return what you did.`, { label: 'setup: fills + loader', phase: 'Setup' })

const FRAMES = [0, 1, 2, 3].map(n => ({ id: `frames${n + 1}`,
  job: `Write the frames for class group ${n + 1} of 4 (sort classes.json by id and take the ${['first', 'second', 'third', 'fourth'][n]}
contiguous quarter) into server/words/parts/frames_${n + 1}.json, ids prefixed "f${n + 1}-". About 375 frames in W1's format, spread over
science, history & social studies, and literature & arts. For every SAT sense (sat.json and parts/sat_*.json) whose class is in your
group: it must be a legal key in at least 6 frames across at least 2 subjects, and each frame's need must admit exactly the senses
you intend (check the other members of the class and its opposite so exactly one option fits). At least 20% of your literature
frames are fixed frames cut from public-domain texts published before 1929 (fetched from gutenberg.org), with source {author,
title, year}. Second-sense entries' "nearly" texts become frames with stem "nearly". Leave reviewed: null on every frame.` }))

const CONF = { id: 'confusions', job: `Write server/words/confusions.json: about 700 pairs in W17's format (lookalikes such as illusory /
elusive / allusive, sense pairs such as qualify.limit / qualify.meet, near-miss pairs such as imply / infer), each with a one-line tell
that really separates them and a kind (meaning, lookalike or sense). Start from every entry's lookalikes (they are confusions the
build derives) and add the rest; every SAT sense needs at least one confusion with a non-empty tell.` }

const author = a => agent(`${CONTEXT}
YOUR JOB (you own only the file named here): ${a.job}
python3 tools/build_words.py must show no errors in your file. Return your counts and anything you were unsure of.`,
  { label: `author: ${a.id}`, phase: 'Author' })

const fold = () => agent(`${CONTEXT}
YOUR JOB (you own every file in server/words/ and tools/build_words.py now; the authors are finished): fold server/words/parts/
into the final files the spec names (sat.json holds every SAT entry; frames.json every frame; classes.json any added classes),
delete parts/ and _plan.json, refresh collections.json so its counts and members cover the whole library (Transitions and Second
meanings were empty when it was written), and make every validator check an error for phases 1-6 except the review gate and
freq.txt (their phases come later). python3 tools/build_words.py must exit 0. Commit. Return the final counts.`,
  { label: 'fold parts into final files', phase: 'Fold' })

const DEFECTS = { type: 'object', properties: {
  pass: { type: 'boolean' }, evidence: { type: 'string' },
  defects: { type: 'array', items: { type: 'object', properties: { where: { type: 'string' }, what: { type: 'string' }, fix: { type: 'string' } }, required: ['where', 'what', 'fix'] } },
}, required: ['pass', 'evidence', 'defects'] }

const check = (lens, n) => agent(`${CONTEXT}
You are an independent CHECKER, not an author: do not edit or commit anything. Try to REFUTE that the Words content is accurate
enough to put in front of students. ${lens}
Report every defect with the file and slug or frame id. Default to pass=false if a sample shows systematic problems.`,
  { label: `check ${n}`, phase: 'Check', schema: DEFECTS })

const LENSES = [
  `ENTRIES: take 150 random SAT senses (use a fixed seed and say which). For each: is the meaning right for the sense the SAT tests,
is the example natural and does it use that sense, are "same" true synonyms in that sense, is "opposite" a real antonym, does the
lookalike tell really separate the words, is class / polarity / intensity sensible against its family? Then fact-check every example
that names a real person, event, date or place (all of them, not a sample: grep for capitalized names and years).`,
  `FRAMES AND CONFUSIONS: take 120 random frames and 80 random confusions. For each frame, generate its items the way W1 describes
(the key and three distractors from the traps) and decide as a student would: does exactly one option fit, does the [[clue]] decide
it, is the text natural and at SAT difficulty? For every fixed literature frame in your sample, fetch the Gutenberg text and confirm
the passage is quoted exactly and the source is right. For each confusion, is the tell correct and useful?`,
]

const fix = defects => agent(`${CONTEXT}
YOUR JOB (you own every file in server/words/): independent checkers found these defects: ${JSON.stringify(defects)}
Fix every one; where a defect shows a pattern, search the whole library for the same problem and fix it everywhere. Keep
python3 tools/build_words.py at exit 0. Commit as you go. Return what you changed.`, { label: 'fix check defects', phase: 'Check' })

const a = args || {}
const order = ['setup', 'author', 'fold', 'check']
const from = order.indexOf(a.from || 'setup')
const out = {}
if (from <= 0) out.setup = await setup()
if (from <= 1) {
  const todo = [...FRAMES, CONF].filter(x => !a.only || a.only.includes(x.id))
  out.authors = await parallel(todo.map(x => () => author(x).then(r => ({ id: x.id, r }))))
}
if (from <= 2) out.fold = await fold()
const verdicts = (await parallel(LENSES.map((l, i) => () => check(l, i + 1)))).filter(Boolean)
out.checks = verdicts
const defects = verdicts.flatMap(v => v.defects || [])
if (defects.length) out.fix = await fix(defects)
log(`${defects.length} defects found by the checkers${defects.length ? ', one fix round applied' : ''}`)
return out
