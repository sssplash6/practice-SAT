export const meta = {
  name: 'words-library',
  description: 'Finish the Words library content: normalize the core and plan the rest, then advanced, second senses, transitions and roots in parallel',
  phases: [
    { title: 'Core', detail: 'normalize the 316 drafts into sat.json, fix the classes, reach 400 core, write the plan' },
    { title: 'Library', detail: 'parallel authors, one set of files each' },
  ],
}

// Picks up the Words content the user's other agent started (branch v2/words-content, cut off by a usage limit).
// args: { skipCore?: true, only?: [author ids] } so a restart runs only what is missing.
// Every author checks the branch first and continues from any partial file it owns.

const W = '/Users/workingmyassof/satbank/.claude/worktrees/words'
const SIGN = 'Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>'
const PLAN = 'server/words/_plan.json'

const CONTEXT = `
You are authoring CONTENT for the Words (vocabulary) section of "SAT Freshman", a free SAT prep site. Work ONLY in the git
worktree ${W} (branch v2/words-content): cd there first. Never touch the main working tree, master, or any other branch.
Read first: spec/v2-decisions.md (it wins: decision 2 = SAT Reading & Writing vocabulary only, no math words),
spec/v2-upgrades/words.md (W1-W4, W10, W17 and, in §3.1, overrides 12, 17 and 51) and spec/rebuild-v2.md lines 9134-10029.
Look at the existing files in server/words/ and tools/build_words.py (the validator) to match the entry format exactly.
QUALITY: every meaning must be correct for the sense the SAT tests, in plain student-friendly English, our own wording (no
third-party lists: not TopTierPrep's 650, not The College Panda's 400). American English. Every example is a natural sentence
of the kind an SAT passage would contain, with the headword marked [[like this]]. same = true synonyms in this sense; opposite
= a real antonym or no_opposite: true; every lookalike has a one-line tell that actually separates the two words.
Classes are SEMANTIC FAMILIES (weaken, confirm, cautious, praise, criticize...), never a class named after one word: the trap
generator needs several words per class at different intensities to build too_strong, too_weak and wrong-tone options.
GIT: commit only the files you own, with git commit -m "<real message>" -- <your paths> and a message ending with the line
"${SIGN}". Other authors share this worktree: if git reports index.lock, wait a few seconds and retry. Never push or merge.
Commit after every ~50 entries so an interruption loses little. Before starting, check git log and your files: if a
predecessor left a partial file of yours, continue it, never restart it.
`

const core = () => agent(`${CONTEXT}
YOUR JOB (you own server/words/sat.json, classes.json, core_a.json, core_b.json, ${PLAN}, tools/build_words.py):
1. Classes: consolidate server/words/classes.json into about 150-200 semantic families, each {id, dimension, opposite} with a
   reciprocal opposite. Every class that entries use must have at least 3 member words (core + planned advanced) spread over
   intensities 1-5 where the family allows it.
2. Normalize the 316 drafts in core_a.json and core_b.json into server/words/sat.json: sense = "main" for single-sense words
   (per-sense slugs like qualify.limit only for split words), short <= 60 characters and never a copy of meaning, class from
   the consolidated set, a realistic level spread (easy / medium / hard as the SAT uses the word), every field in W1 and W17.
   Re-read every meaning and fix any that is wrong or vague. Then delete core_a.json and core_b.json.
3. Add core entries until the core tier has at least 400 (common SAT R&W words a strong 10th grader should know).
4. Tag the answer-choice words (W17: the verbs and stance words R&W answer choices are written in) that are already in the
   core with lists: ["answer-choice"] and a real uses line.
5. Write ${PLAN}: {"advanced": [[~200 headwords], [~200], [~200]] (three disjoint batches, none in the core),
   "second_senses": [{slug: "word.sense", word, gloss}] (~100 SAT-tested second meanings: qualify.limit, qualify.meet...),
   "answer_choice_new": [~90 minus the tagged core ones, none in the core or advanced batches],
   "classes_by_batch": hints of which classes each advanced batch should fill}.
6. Make tools/build_words.py also load server/words/parts/sat_*.json and parts/classes_*.json into the sat and class lists (so
   parallel authors' files validate), and keep every override 17 check.
python3 tools/build_words.py must show sat_core >= 400 with no errors. Return the counts and anything you were unsure of.`,
  { label: 'core: normalize, 400, plan', phase: 'Core' })

const AUTHORS = [
  ...[0, 1, 2].map(n => ({ id: `adv${n + 1}`, files: `server/words/parts/sat_adv_${n + 1}.json, parts/classes_adv${n + 1}.json`,
    job: `Write the ~200 advanced SAT entries of batch ${n + 1} in ${PLAN} ("advanced"[${n}]), tier "advanced", every field in W1 and W17,
into server/words/parts/sat_adv_${n + 1}.json. Use the classes in classes.json; only if none fits, add a family to
parts/classes_adv${n + 1}.json (never edit classes.json). Tag answer-choice words there with lists and uses.` })),
  { id: 'second', files: 'server/words/parts/sat_second.json, parts/sat_answer.json, parts/classes_second.json',
    job: `Write the ~100 second senses in ${PLAN} ("second_senses") as their own per-sense entries (second_sense: true, each with at
least 3 "nearly" texts where the everyday meaning is the trap) into parts/sat_second.json. If the headword's main sense is in
sat.json with slug "word", give the new entry the "word.sense" slug and add an other_senses link on your entry only. Then write
the "answer_choice_new" entries (lists: ["answer-choice"], a real uses line: "In answer choices: ...") into parts/sat_answer.json.` },
  { id: 'transitions', files: 'server/words/transitions.json, server/words/pairs.json',
    job: `Write transitions.json (~80 transition words and phrases, each with pos, meaning, short, examples and W2's logic from the 9
groups) and pairs.json (at least 150 sentence-pair families, at least 15 per logic, over science, history & social studies and
literature & arts, in W2's format), so the generator can build transition questions whose options span 4 logics.` },
  { id: 'roots', files: 'server/words/roots.json, server/words/foils.json, server/words/collections.json',
    job: `Write roots.json (~80 roots, prefixes and suffixes with meaning and example words from the library, W4), foils.json (~60
pronounceable made-up words for placement, W10; none may be a real English word) and collections.json (the collections and
lists W17 and the Words spec name, over the library's slugs; read sat.json and ${PLAN} for them).` },
]

const author = a => agent(`${CONTEXT}
YOUR JOB (you own only: ${a.files}): ${a.job}
python3 tools/build_words.py must show no errors in your files (warnings for other phases are fine). Return your counts and
anything you were unsure of.`, { label: `author: ${a.id}`, phase: 'Library' })

const a = args || {}
const coreResult = a.skipCore ? 'skipped (already done)' : await core()
const todo = AUTHORS.filter(x => !a.only || a.only.includes(x.id))
const library = await parallel(todo.map(x => () => author(x).then(r => ({ id: x.id, r }))))
return { core: coreResult, library }
