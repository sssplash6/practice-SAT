export const meta = {
  name: 'words-gate',
  description: 'Task 12: the Words review gate: build --review, two blind independent verdict passes, then mark agreed frames reviewed',
  phases: [
    { title: 'Tool', detail: 'build_words.py --review and the frame selection' },
    { title: 'Verdicts', detail: 'two independent, key-blind passes' },
    { title: 'Gate', detail: 'reviewed only where both passes name the key' },
  ],
}

// Runs on master after v2/helper-integ is merged (build_words.py and the Words server live there).
// args: { from?: 'tool' | 'verdicts' | 'gate' }. Each agent commits on v2/words-gate and continues a predecessor's work.

const REPO = '/Users/workingmyassof/freshbot/satbank'
const SIGN = 'Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>'
const CONTEXT = (br, base) => `
Repo ${REPO}. You are in your own git worktree. Work on branch ${br}: git switch ${br} 2>/dev/null || git switch -c
${br} ${base}; continue any predecessor's commits. Check git branch --show-current before every commit. Commit every ~100 frames with a real message ending "${SIGN}". Never
push or merge. READ spec/v2-upgrades/words.md W1 "The review gate" and the Words files in server/words/ and tools/build_words.py.
`

const tool = () => agent(`${CONTEXT('v2/words-gate', 'master')}
Build the review tooling W1 describes: python3 tools/build_words.py --review [--frame id] prints, for each frame x each legal key x
5 seeds, the full generated item (text, stem, 4 options) WITHOUT marking the key, and writes server/words/review-queue.json. Also write
server/words/gate_plan.json: a greedy selection of frames so that every SAT sense is a legal key in at least one selected frame, the
frames covering the most senses first (all 5,376 frames stay in frames.json; only the selection is judged now). Return the counts.`,
  { label: 'gate: review tool + plan', phase: 'Tool', isolation: 'worktree' })

const pass = (who, file, br) => agent(`${CONTEXT(br, 'v2/words-gate')}
You are an independent adjudicator "${who}". Do NOT open server/words/adjudications*.json of anyone else, and do not look at which
option is the key. For every item of every frame in server/words/gate_plan.json (use tools/build_words.py --review --frame <id>),
decide as a careful student which options fit the blank: verdict 'one' (exactly one fits; give that option), 'more' (two or more fit;
name them) or 'none'. Write {frame, key_slug, seed, by: "${who}", verdict, option, note} rows to ${file} (append; continue a
predecessor's file). Commit every ~100 frames. Return the counts of one / more / none.`,
  { label: `verdicts: ${who}`, phase: 'Verdicts', isolation: 'worktree' })

const gate = () => agent(`${CONTEXT('v2/words-gate', 'master')}
First git merge --no-ff v2/words-gate-a and v2/words-gate-b into v2/words-gate. Then merge server/words/adjudications_a.json and adjudications_b.json into server/words/adjudications.json (W1's format). A frame is
servable only when every one of its judged items has two 'one' verdicts from different "by" that both name the key: set its
reviewed {by: "model:helper-a+model:helper-b", date} in frames.json. Every 'more', 'none' or disagreement blocks the frame: list those
frames in server/words/review-queue.json with the verdicts, for a person. Run python3 tools/build_words.py (exit 0) and the Words server
checks (server/checks/s9.py). Commit. Return: frames servable, senses with at least one servable frame, and frames blocked.`,
  { label: 'gate: mark reviewed', phase: 'Gate', isolation: 'worktree' })

const a = args || {}
const order = ['tool', 'verdicts', 'gate']
const from = order.indexOf(a.from || 'tool')
const out = {}
if (from <= 0) out.tool = await tool()
if (from <= 1) out.verdicts = await parallel([
  () => pass('model:helper-a', 'server/words/adjudications_a.json', 'v2/words-gate-a'),
  () => pass('model:helper-b', 'server/words/adjudications_b.json', 'v2/words-gate-b'),
])
out.gate = await gate()
return out
